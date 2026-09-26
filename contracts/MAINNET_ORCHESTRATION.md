# LightDAO 主网编排总方案（ORCHESTRATION）

本文件是**总规划**：把「租机器 → 起 7 验证者 → 创世 → 部署合约 → 监控 → 灰度上线」串成一条可执行流水线，并说明每步由谁、在哪台机器、跑哪个脚本。配合 `MAINNET_RUNBOOK.md`（规格/闸口/密钥模型）与 `AUDIT_REPORT.md`（合约安全）一起看。

---

## 0. 关于「7 台同一家云商行不行」
**结论：能用，但不推荐把 7 台全放同一家、同一地区。** 这是风险梯度，不是硬性禁止：

- BFT 规则：7 验证者容错 f=2，**≥3 台同时离线就停链**。
- 同一家云商的**相关性故障**（全局控制面故障、某地区机房断电/断网、你账户被封/欠费/被风控）会一次性带走多台 → 停链。
- 同一云商**不同地区**比同一地区好很多，但仍是单一厂商控制面风险。
- 建议拓扑（性价比与安全的平衡）：
  - **至少 2 家云商**、**至少 3 个地区**分散 7 台验证者；
  - 验证者**不直接暴露公网**，前面挂 1–2 台 **sentry 哨兵**（可与验证者同商不同机）；
  - 理想：4 台在 A 商（跨 2 地区）+ 3 台在 B 商（跨 1–2 地区）。
- 预算极紧的折中：一家云商但**跨 3 个地区**（如 HK/SG/JP 或 US-East/US-West/EU），并保留 1 台**备用验证者**（不同商，平时不同步出块，故障时顶上）。

## 1. 支付友好 + 性价比云商（你可用支付宝/微信的）
> 价格随行情变动，下单前以官网为准。验证者需 **NVMe + 稳定网络 + 海外地区**。

| 云商 | 支付方式 | 适合度 | 说明 |
|---|---|---|---|
| **Vultr** (vultr.com) | **支付宝**、信用卡、PayPal | ★★★★★ | NVMe/高性能云主机，全球 ~30 机房（东京/新加坡/悉尼/美东西/欧洲），按小时计费，最适合分散多地区。4vCPU/16GB 约 $48–96/月 |
| **腾讯云**（国内站 buy.qcloud.com，选**香港/新加坡**地域） | **支付宝/微信** | ★★★★ | 中文控制台、发票方便；轻量应用服务器或 CVM；HK/SG 节点。需实名 |
| **阿里云**（国内站，选**香港/新加坡/日本**地域） | **支付宝** | ★★★★ | 同上，ECS + ESSD 云盘；海外地域免备案 |
| **华为云**（香港/新加坡） | 支付宝/微信 | ★★★ | 备选，凑多厂商分散 |
| Hetzner (hetzner.com) | **不接受中国卡**（需欧卡/PayPal 视情况） | ★★（若能付） | 最便宜、NVMe 好，4vCPU/16GB 约 €15–30/月；但**对 CN 支付不友好**，且机房集中欧洲 |

**建议组合（支付友好 + 分散）**：Vultr（支付宝）开 4 台跨 东京/新加坡/美西/法兰克福 + 腾讯云 HK/SG 开 3 台 = 7 台、2 家、多地区。哨兵/监控可各加 1 台便宜机型。

**详细购买步骤（以 Vultr 为例）**：
1. 注册 vultr.com → Billing → 充值选 **Alipay**（支付宝）。
2. Deploy → **Cloud Compute（Regular/High Performance，选 NVMe）**。
3. Server Location：分别选 Tokyo / Singapore / Los Angeles / Frankfurt（**分散**）。
4. Image：Ubuntu 22.04/24.04 LTS x64。
5. Plan：**4 vCPU / 16 GB / 500GB NVMe**（或 High Frequency 同配）。
6. 开启 IPv4，添加 SSH Key（**用你自己的公钥**，别用密码登录）。
7. 部署后记下每台的公网 IP；腾讯云/阿里云同理（选 HK/SG 地域、Ubuntu、4C16G、ESSD/NVMe、绑 SSH 密钥或设强密码）。
8. 每台登录后先跑 `scripts/node_bootstrap.sh`。

---

## 2. 角色与机器规划（最小可用）
| 角色 | 台数 | 位置 | 暴露端口 | 备注 |
|---|---|---|---|---|
| Validator val01–07 | 7 | 2 家云商 × ≥3 地区 | 仅 26656(p2p，且只连自己哨兵) | RPC 只监听 127.0.0.1 |
| Sentry 哨兵 | 2–3 | 分散 | 26656 + 26657(可选) | 隐藏验证者真实 IP，抗 DDoS |
| RPC/浏览器 | 1 | 任一 | 26657/1317/9090 | 对外查询、钱包、区块浏览器 |
| Monitor 监控 | 1 | 独立 | 9090/3000（限内网/VPN） | Prometheus+Grafana |

> 预算紧可先 7 验证者 + 1 监控；哨兵/RPC 随后补。但验证者**务必不直接公网暴露 RPC**。

---

## 3. 关键设计决策（上线前必须拍板）
1. **原生代币 vs LIGHT**：本链**原生 denom**（脚本默认 `uldg`）用于**质押 + Gas**；**LIGHT 是 CW20 合约代币**（light_token），用于挖矿奖励/治理/子代币。两者是不同的东西——你必须决定：
   - 原生代币叫什么、总量、如何分发给 7 个验证者做自质押、是否公开售卖；
   - Gas 定价（`min-gas-price`，建议用 oracle 锚定 USD 的动态 Gas，见白皮书）；
   - LIGHT 的 TGE 分配（挖矿/生态/团队/战略）与创世金库注资路径。
2. **合约 admin = 治理**（已在部署脚本设定）；治理自身的 admin 建议交给 **treasury_multisig(3/5+72h)**。
3. **验证者集合**：起步 7（f=2）。主网稳定后可通过治理逐步加到 ≥15 提升去中心化。
4. **root_threshold**：7 验证者设 **5**（2/3+1）。
5. **投票周期**：主网 `voting_period_secs=null` → 按类型（紧急 1 天 / 其余 7 天）。

---

## 4. 端到端执行顺序（谁 / 哪台 / 跑什么）
> 前置：合约已审计或已跑公开 bug bounty（RUNBOOK 的 G2）。以下把链先起在**无真实价值**的公开 testnet，压测 2–4 周后再走软启动主网。

**阶段 A — 每台机器基础环境（7 验证者 + 哨兵 + 监控都跑）**
```bash
# 先把编译好的 wasmd v0.60 linux/amd64 二进制 scp 到每台（wasmd 无官方发行二进制）
scp /home/ubuntu/wasmd60/wasmd user@<each-ip>:/tmp/wasmd
# 在每台上：
WASMD_SRC=/tmp/wasmd bash scripts/node_bootstrap.sh
```

**阶段 B — 生成验证者身份（7 台验证者各跑）**
```bash
MONIKER=val01 CHAIN_ID=lightdao-mainnet-1 PUB_IP=<本机公网IP> KB=file \
  bash scripts/validator_init.sh
# 把输出的 peer / consensus_pubkey / operator_addr 安全发给协调者
# 立即离线备份 priv_validator_key.json 与 operator 助记词
```

**阶段 C — 协调者组装创世（1 台协调机）**
```bash
# 1) 填 validators.txt（moniker|peer|pubkey|operator|selfdel）与 allocations.txt（addr|amount）
# 2) 生成公共创世（含 denom/参数/预置账户）
CHAIN_ID=lightdao-mainnet-1 DENOM=uldg GENESIS_TIME=2026-10-01T13:00:00Z \
  bash scripts/coordinator_genesis.sh
# 3) 把 genesis_out/genesis_common.json 发回 7 台验证者
```

**阶段 D — 各验证者签 gentx（7 台各跑）**
```bash
# 先把 genesis_common.json 覆盖到 ~/.wasmd/config/genesis.json
MONIKER=val01 CHAIN_ID=lightdao-mainnet-1 DENOM=uldg SELF_DELIG=1000000000 \
  PUB_IP=<本机IP> KB=file bash scripts/make_gentx.sh
# 把 genesis_out/gentx-val01.json 发回协调者
```

**阶段 E — 协调者汇总最终创世**
```bash
mkdir -p ~/.wasmd/config/gentx && cp genesis_out/gentx-*.json ~/.wasmd/config/gentx/
wasmd genesis collect-gentxs --home ~/.wasmd
wasmd genesis validate   --home ~/.wasmd
cp ~/.wasmd/config/genesis.json genesis_out/genesis_final.json   # 分发给所有节点
```

**阶段 F — 配置 P2P 拓扑（每台）**
```bash
# 哨兵：连所有验证者+其他哨兵
ROLE=sentry    PERSISTENT_PEERS="<val/sentry peers>" EXTERNAL_ADDR=<ip:26656> bash scripts/set_peers.sh
# 验证者：只连自己的哨兵，隐藏其他验证者
ROLE=validator PERSISTENT_PEERS="<我的哨兵>" PRIVATE_PEER_IDS="<其他验证者nodeid>" \
  EXTERNAL_ADDR=<ip:26656> bash scripts/set_peers.sh
```

**阶段 G — cosmovisor + 启动（每台）**
```bash
WASMD_SRC=/usr/local/bin/wasmd bash scripts/cosmovisor_setup.sh
# 到达 genesis_time 后： sudo systemctl start lightd
wasmd status   # 确认出块、catching_up=false
```

**阶段 H — 部署合约（协调者/部署者，链出块后）**
```bash
# 用本包已归一化的 wasm/ 与 deploy.sh，但换成主网参数、且 RESET=no（不重置主网！）
RESET=no KEY=deployer CID=lightdao-mainnet-1 VOTING="" ROOT_THRESHOLD=5 \
  WASM_DIR=./wasm bash scripts/deploy.sh
# deploy.sh 会 store 10 + instantiate2 全互连（admin=治理），并把地址写 /tmp/lightdao_addrs.env
bash scripts/verify_flows.sh   # 三链路 + 安全回归（主网建议在独立账户上小额度跑）
```

**阶段 I — 监控（监控节点）**
```bash
VALIDATOR_IPS="ip1 ip2 ip3 ip4 ip5 ip6 ip7" GRAFANA_ADMIN_PW=<强密码> \
  bash scripts/monitoring_setup.sh
# 各验证者的 config.toml 打开 [instrumentation] enabled=true, addr 0.0.0.0:26660（仅对监控IP/VPC开放）
```

**阶段 J — 灰度上线**
1. 公开 testnet 跑 2–4 周 + bug bounty + 压测（大量 store/instantiate/claim/transfer/升级演练）。
2. 软启动主网：真实创世但**限额**（挖矿硬顶临时调低、子代币兑换暂关、金库小额），观察 1–2 周。
3. 解除限额 + TGE，正式主网。

---

## 5. 脚本清单（scripts/）
| 脚本 | 在哪跑 | 作用 |
|---|---|---|
| `node_bootstrap.sh` | 每台 | 装依赖/wasmd/cosmovisor/防火墙/调优 |
| `validator_init.sh` | 7 验证者 | 建共识密钥+operator，产出 peer/pubkey/addr |
| `coordinator_genesis.sh` | 协调机 | 组装公共创世（denom/参数/账户） |
| `make_gentx.sh` | 7 验证者 | 各自签 self-delegation gentx |
| `set_peers.sh` | 每台 | 配 p2p（验证者藏哨兵后、哨兵连全网） |
| `cosmovisor_setup.sh` | 每台 | cosmovisor 目录 + systemd 自动升级 |
| `monitoring_setup.sh` | 监控机 | Prometheus+Grafana+告警规则 |
| `build_normalize.sh` | 构建机 | 编译 + wasm-opt 归一化 |
| `deploy.sh` | 部署者 | store 10 + instantiate2 全互连 + 校验 |
| `verify_flows.sh` | 部署者 | 三链路 + DAO 执行 + 安全回归 |

---

## 6. 我（AI）不能替你做、必须你/专业方完成的
- **私钥/助记词离线生成与保管**（HSM/硬件钱包/多签），密钥仪式的物理安全。
- **第三方审计或公开 bug bounty + 时间**（你选择跳过审计，请用 bounty+审查期+限额软启动补偿）。
- **法律合规 / TGE / 代币发行**（涉证券/税务/地区监管，需法律顾问）。
- **真实资金与账户安全**（云商账户 2FA、提币白名单、冷热钱包分离）。

> 这些不是技术能替代的。技术侧（合约、链、脚本、监控、灰度）我已尽量做到可一键复现；把机器和密钥准备好，我可以远程带你逐台执行阶段 A–J。
