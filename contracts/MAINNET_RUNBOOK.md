# LightDAO 主网启动运行手册（MAINNET RUNBOOK）

> 目标：把当前单验证者测试网，升级为 **7 验证者 BFT 主网**，合约 admin 归治理（DAO 控制升级），分级上线、可回滚、带 go/no-go 闸口。
> 原则：**先加固、再灰度、后承载真实价值**。未过闸口不承载真实资金。

---

## 0. 7 台验证者 VPS 规格（你要租的机器）

CosmWasm 链（wasmd v0.60 / wasmvm v2.2.1 / SDK v0.53）验证者对 **内存、磁盘 IO、CPU** 都敏感（store/instantiate/migrate 时尤甚）。

| 角色 | 数量 | CPU | 内存 | 磁盘 | 网络 | 系统 |
|---|---|---|---|---|---|---|
| 验证者（出块） | 7 | 4 vCPU（独享更好） | 16 GB | 500 GB NVMe SSD | 1 Gbps，公网 IP | Ubuntu 22.04/24.04 LTS |
| Sentry 哨兵（可选，抗 DDoS） | 2–3 | 4 vCPU | 8 GB | 300 GB NVMe | 1 Gbps | Ubuntu 22.04/24.04 |
| RPC/浏览器节点（可选） | 1 | 4 vCPU | 16 GB | 1 TB NVMe | 1 Gbps | Ubuntu 22.04/24.04 |

**最低可跑**（预算紧）：验证者 2 vCPU / 8 GB / 200 GB NVMe —— 但 store 大合约、状态增长后易吃紧，主网**强烈建议 16 GB + NVMe**。
**关键点**：
- 必须 **NVMe SSD**（IavlDB/状态读写密集，HDD 会拖垮出块）。
- 7 台**分布在不同机房/地区/云商**（BFT 要求 <1/3 同时离线；同城同云商=单点）。
- 用 **Hetzner / OVH / 腾讯云国际 / AWS** 等；国内备案机器不适合（延迟+合规）。
- 每台独立 **ed25519 验证者密钥** + 独立 **sentry 架构**（验证者不直接暴露公网，经哨兵转发，隐藏 validator IP）。
- 预算参考：4vCPU/16GB/500GB NVMe 海外 VPS 约 **$20–60/月/台**，7 台约 **$140–420/月**。

---

## 1. 上线前 go/no-go 闸口（缺一不可）

| # | 闸口 | 状态 | 说明 |
|---|---|---|---|
| G1 | 合约自审 + 修复 + 链上回归通过 | ✅ 已完成（本次） | 见 AUDIT_REPORT.md；13 单测 + 三链路 + 多签/DAO/鉴权回归全绿 |
| G2 | **独立第三方审计** 或 **公开 bug bounty + 时间** | ⬜ 待办 | 你选择跳过第三方审计；**替代方案**：公开源码 + Immunefi 式 bounty + 至少 4–8 周公开审查期。BTC 无正式审计但经过 16 年数千人攻击 + 仍有 CVE 紧急分叉——新合约没有这个时间沉淀，务必用 bounty+时间+灰度补偿 |
| G3 | 合约 admin = 治理（非单一 EOA） | ✅ 已完成 | 所有合约 admin=governance，升级须走提案+投票+migrate |
| G4 | 7 验证者密钥仪式 + sentry 架构 | ⬜ 待办 | 见 §3 |
| G5 | 创世分配 / TGE / 金库注资方案 + 法律合规 | ⬜ 待办 | 代币发行涉合规，需法律顾问；本手册不含法律意见 |
| G6 | 监控告警 + 快照备份 + 升级演练 | ⬜ 待办 | 见 §5 |
| G7 | **灰度上线**：先 0 价值 devnet→testnet→软启动（限额）→主网 | ⬜ 待办 | 见 §6 |

> 未过 G2/G4/G5/G6/G7 **不得**承载真实价值。

---

## 2. 分级上线路径（devnet → testnet → 软启动 → 主网）

1. **devnet（本地/单机）**：`RESET=yes deploy.sh` + `verify_flows.sh` 全绿（当前已做到）。
2. **公开 testnet（7 验证者，无真实价值）**：按 §3 起 7 台，genesis 分测试币，公开 faucet，跑 2–4 周，收 bug bounty，压测（大量 store/instantiate/claim/transfer）。
3. **软启动主网（限额）**：真实创世但**先限额**——挖矿硬顶临时调低、子代币/兑换暂不开放、金库小额；admin 仍在治理多签。观察 1–2 周。
4. **正式主网**：解除限额，开放全部功能，TGE。

---

## 3. 7 验证者起网步骤（概要）

> 用**自定义链二进制**（`chain/go/lightd`，内嵌 x/wasm）或直接用 wasmd。下面以 wasmd 为例。

**每台验证者：**
1. 装 Go 1.23、wasmd v0.60 二进制、开 NVMe 挂载。
2. `wasmd init <moniker> --chain-id lightdao-mainnet-1`
3. 生成并**离线保管**验证者密钥：`wasmd tendermint create-validator-key`（priv_validator_key.json 拷到安全位置/HSM）。
4. 生成节点 P2P 密钥，交换 7 台的 `node_id@ip:26656` 配 persistent_peers；验证者**只连哨兵**，不公开。
5. 创世账户：把 10 个合约部署者、金库、团队/生态地址写入 genesis（分配见 G5）。
6. 收集 7 份 `gentx`（各自 create-validator，自质押 ≥ 门限）→ `collect-gentxs` → `validate-genesis` → 分发统一 genesis.json。
7. 约定 `genesis_time`（真实 TGE 时间）后同时 `wasmd start`。
8. 出块后由部署者（或治理）`store` 10 合约 + `instantiate2` 全互连（用本包 `deploy.sh`，把 `RESET=no`、`KEY`/`RPC`/`CID` 换成主网参数、`VOTING=""` 走白皮书天数、`ROOT_THRESHOLD=5`、`validators` = 7 个网关地址）。

**主网参数建议**：`root_threshold=5`（7 的 2/3+1）；`voting_period_secs=null`（按类型 1/7 天）；`genesis_time=` 真实 TGE；`proposal_min_stake=` 按白皮书（如 5000 LIGHT）。

---

## 4. 密钥与权限模型（务必执行）

- **合约 admin = governance**（已设）。任何升级/minter 变更/金库动作 = 提案+投票+执行，无单点。
- **governance 自身 admin**：建议交给 **treasury_multisig（3/5 + 72h 时间锁）** 或治理自身；避免部署者 EOA 长期持有。
- **验证者签名密钥**：离线/HSM，哨兵架构隐藏。
- **部署者 EOA**：上线后把残留权限全部移交治理/多签，部署者密钥冷存。
- 所有私钥**永不**进 git/聊天/日志；本次会话若在聊天里出现过密钥，视为已泄露、**立即轮换**。

---

## 5. 运维：监控 / 备份 / 升级

- **监控**：Prometheus + Grafana（wasmd 暴露 26660 metrics）；告警项：出块停滞、`missing blocks`、验证者 jailed、磁盘 >80%、内存、peer 数 <阈值、合约 store/instantiate 失败率。
- **备份**：每日快照 `data/`（或 state-sync 快照）；`priv_validator_key.json`、`genesis.json` 离线多副本。
- **升级演练**：主网前在 testnet 走一遍**链软件升级**（cosmovisor）+ **合约 migrate**（治理提案 → WasmMsg::Migrate，本包 governance 已支持）。
- **state-sync / seeds**：配 seed 节点与 state-sync 快照，便于新验证者快速同步。

---

## 6. 应急与回滚

- **暂停开关**：oracle `Anomaly`（跨源偏差 >15%）应联动暂停子代币兑换等敏感操作（当前 `Anomaly{}` 已实现，建议在 subtoken_factory.exchange 里加「anomaly 时拒绝」——见 AUDIT_REPORT 后续项）。
- **合约漏洞**：admin=治理 → 紧急提案 migrate 到修复版（Emergency 类型 1 天投票；主网可评估更短的紧急多签通道，但需权衡去中心化）。
- **链halt**：>1/3 验证者离线会停链 → 7 台跨地区 + 哨兵 + 备用验证者。
- **回滚**：保留升级前快照；cosmovisor 可回退二进制版本。

---

## 7. 一键复现（testnet/devnet）
```bash
bash scripts/build_normalize.sh          # 编译+wasm-opt归一化 -> wasm_v2/
RESET=yes bash scripts/deploy.sh         # 重置+store10+instantiate2(admin=治理,2/3多签根)
bash scripts/verify_flows.sh             # 三链路+DAO通用执行+多签+鉴权回归(真实交易)
CARGO_TARGET_DIR=/tmp/t cargo +1.85 test -p mining_reward -p governance   # 13 单元测试
```
