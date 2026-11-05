# IBC（跨链）开通现状与落地路径（实测记录，2026-11-04）

本文件只做一件事：把"跨链到底能不能用、卡在哪、要什么才能做完"写成**可复核的事实**，
不写成愿望。所有结论都带命令，任何人都能在网关自跑。

## 一、主网（lightdao-mainnet-1）能力实测：链的"闸门"是开的，但没有通道

| 检查项 | 命令 | 实测结果 | 含义 |
|---|---|---|---|
| 轻客户端是否受限 | `wasmd q ibc client params --node http://127.0.0.1:26657` | `allowed_clients: ['*']` | **任何人都能建客户端**，不需要治理放行 |
| ICS-20 转账开关 | `wasmd q ibc-transfer params --node http://127.0.0.1:26657` | `send_enabled: true` / `receive_enabled: true` | 模块层允许收发 |
| 现有客户端 | `wasmd q ibc client states --node http://127.0.0.1:26657` | `total: 0` | **一个都没有** |
| 现有通道 | `wasmd q ibc channel channels --node http://127.0.0.1:26657` | 空 | **没有 transfer 通道** |

结论：**主网跨链未上线**，不是因为链禁止，而是因为从来没人建过客户端/连接/通道，
也没有跑在两个主网之间的中继。站内此前写"IBC 双向 transfer 已实测"是虚报，
已在 v1.10.11 全语种改为"主网未开通 + 测试网实测过"，并由渲染层用例锁住（`ld_render_truth.py`）。

## 二、测试网（lightdao-testnet-gas ↔ osmo-test-5）确实建过，但已经烂在那里

实测（本机 RPC `http://127.0.0.1:26757`）：

- 曾建成：客户端 `07-tendermint-0/1/2`（指向 `osmo-test-5`），通道
  `channel-0 ↔ osmo channel-11849`、`channel-1 ↔ channel-11850`，端口 `transfer`。
- 现在**不能用**：真发一笔转账被链上直接拒：
  `cannot send packet using client (07-tendermint-2) with status Expired: client state is not active`
  （ibc-go v10 `modules/core/04-channel/keeper/packet.go:60`）。
  原因很直白：这台机上的测试网节点此前停着（`lightd-testnet.service` inactive），
  对端头不再更新，信任期一过客户端就 **Expired——这是终态，救不回来，只能重建客户端+连接+通道**。
- 我 11-04 已把测试网节点拉起来（`systemctl start lightd-testnet`，随后 height 931073 正常出块、
  `catching_up=false`），`hermes health-check` 也 SUCCESS；但重建通道卡在下述两处，见第三节。

## 三、要"做完跨链"，实测挡路的是这三件事（不是代码能力）

1. **对端 RPC 从本机不可达（中继侧）**：`hermes create client --host-chain osmo-test-5 …` 报
   `RPC error to endpoint https://rpc.testnet.osmosis.zone/: error sending request / error trying to connect`，
   而同一时刻 `curl https://rpc.testnet.osmosis.zone:443/status` 从本机是 HTTP 200。
   → 中继的 HTTP 客户端（含 HTTP/2、IPv6 或代理差异）与 curl 结果不一致，需要单独定位
   （候选：强制 IPv4、换 `rpc_addr` 为 `wss://…/websocket`+mode=pull、或换公共端点）。**不猜着改配置**，
   因为这台机上跑的是主网资金相关服务，中继配置错了会把"看起来在跑、其实不动"变成常态。
2. **对端手续费**：重建通道要在 osmo-test-5 上提交 `connectionOpenTry/channelOpenTry`，
   中继账户 `osmo13w2kk5nl43hthzyw8w30qhzfsjnfa08cqqqqqp` 是否有测试 OSMO 我没查到——
   本机的 LCD 请求被 TLS 断流（`UNEXPECTED_EOF_WHILE_READING`），**查不到就记为未确认**，
   绝不当成"有钱"。缺币就要过一次 faucet（人工点一次即可，不做自动化保活）。
3. **资产形态这一条已被链上实测纠正（2026-11-05 14:18Z，主网高度 696,476）**：
   LIGHT **就是原生币 `ulight`**（`q bank denom-metadata ulight` → name LIGHT / 6 位小数；
   `q bank total` → 2,500,000,000,000,000 ulight＝25 亿；`q staking params` → bond_denom=ulight、
   解绑 504h）。链上 code 1 的 `light_token` 只是**一层 CW20 门面**：它的 `token_info` 返回
   `denom: ulight`，而且只接受 `token_info`/`burned`/`config` 三个查询（按地址查余额被拒），
   所以它不是第二本账、也不存在"重复发行 25 亿"。
   ⇒ **结论修正**：ICS-20 能直接搬原生 `ulight`，主网跨链**不需要 warp 封装，也不需要改资产形态**。
   真实缺的是三件事（都还没做，也不该我单方面做）：
   - ① 选定对端链（对方是否接受我们的轻客户端参数：解绑 504h 意味着信任期必须显著小于它）；
   - ② 建客户端/连接/通道并让中继长期在线（通道建立本身不碰金库，但一旦有真实价值进出就是资金风险）；
   - ③ 治理授权：接收哪些对端 `ibc/...` 面额、是否限制转账开关、中继账户权限与额度。
   这三条都需要你先定方向；在你定之前，主网跨链保持"未开通"并在面板如实标注。

## 四、还有一条链上参数约束（与跨链安全性直接相关）

- `wasmd q staking params` 实测 `unbonding_time = 504h`（21 天）。
  轻客户端的 `trusting_period` 必须 **< 2/3 × unbonding_time**（否则验证者集合换防窗口内无法证明恶意签名），
  即 ≤ 14 天；而我们现在这个测试网客户端就是因为节点停摆、头不更新而过期的。
- 这意味着**主网要长期开跨链，中继必须 7×24 活着并有告警**；今天这类"节点停了没人知道"
  在主网上会让通道变成"看起来开着、其实早就过期"的死通道。上线前必须先有这条告警。

## 五、如果要我现在继续推进，我建议的顺序（等你点头）

1. 先修中继对端可达性（IPv4/端点/mode=pull 三种试法各一次，每步都留日志与回滚点）；
2. 用 faucet 给中继补一次测试 OSMO（人工点，不做自动保活），重建测试网客户端+连接+通道；
3. 跑一笔**真实的测试网转账**并贴出两边交易哈希与 packet 确认（这是唯一能证明"功能可用"的东西）；
4. 定资产形态（第三节三选一），再谈主网通道与对手链选择（Osmosis 主网还是 Neutron/Umee 等）；
5. 主网开之前先补两条告警：中继心跳（通道存在但 30 分钟没有 update-client 就响）、
   客户端剩余寿命（< 20% trusting_period 就响，避免再次"过期了才发现"）。

我不会在没有你定方向的情况下擅自选一条跨链资产路线或动主网资金相关的合约——
这三条路在资金归属上不等价，猜错比不做更贵。
