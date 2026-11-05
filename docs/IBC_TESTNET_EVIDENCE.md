
---

## 2026-11-04（同日续 4）跨链：自己起第二条链当对手端，第一笔真实 IBC 转账已在链上落地

### 为什么这么绕
对外链（osmo-test-5）要对方配合建通道、还要外部水龙头，本机说不上话；
"要交易当证据"就得有一对**我们能完全掌控**的链。于是在同一台机器上新起一条
`lightdao-testnet-b`（RPC 26957 / gRPC 127.0.0.1:9099 / p2p 26958，独立数据目录与新服务单元
`lightd-testnet-b.service`），与既有测试网 A（`lightdao-testnet-gas`）做对手端。
只新建目录和端口，不碰主网节点、不碰 A 的数据。

### 已经做到的（都是链上可查，不是"配好了"）
| 步骤 | 结果 |
|---|---|
| 建轻客户端 | A 侧 `07-tendermint-4` → `chain_id: lightdao-testnet-b`；B 侧 `07-tendermint-0` → `chain_id: lightdao-testnet-gas`（`q ibc client states` 实测） |
| 建连接 | A `connection-2`（绑 client-4）、B `connection-0`（绑 client-0），`connection_delay = 0ns` |
| 建 transfer 通道 | A `channel-2` ↔ B `channel-0`（`q ibc channel channels` 两侧互见） |
| **第一笔跨链转账** | A→B 发出 1,000,00 stake（packet `sequence: 1`）；B 侧账户余额出现 **`ibc/C053D637CCA2A2BA030E2C5EE1B28A16F71CCB0E45E8BE52766DC1B241B77878 = 1,000,00`**；A 侧该通道托管地址 `wasm12k2pyuylm9t7ugdvz67h9pg4gmmvhn5v4658cl` 恰好锁住 **1,000,00 stake** |

也就是说：IBC  fungible token transfer（跨链代币转账）**在测试网链对上已经真的跑通过一次**，
发送方锁仓、接收方按 `ibc/<哈希>` 记账，与规范一致，两边都能用命令复现核对。

### 还没做到（不当成已完成）
反向 B→A 已发出（B 侧 ibc 余额从 1,000,00 减到 600,000，即 400,000 已烧掉待到账），
但 A 侧到现在还没入账：中继没把回执/收包搬过去。这台机上的 hermes 1.13 不认我用的
`--all-channels` 之类的参数（是配置项 `global.running_mode`，我已改成 `"all"` 并重启服务），
下一步要看的是它是否真按新配置把两条链的通道纳入轮询；没到账就是没到账，不粉饰。

### 过程中被实测打回来的三个"看起来对其实错"
1. **端口撞车没人报错**：B 的 gRPC 配 `localhost:9090`，而 9090 早被**主网 wasmd 进程**占着
   （`ss -ltnp` 才看得见属主），B 的 gRPC 其实从没监听；hermes 打到 9090 是打到主网节点上，
   于是报"account not found"。只看配置会以为没问题。改到 127.0.0.1:9099 后一次就通。
2. **`keys list -o json` 不存在**：这个构建的 `wasmd keys list` 没有 `-o` 标志（返回帮助文本），
   我一度把"没有输出"当成"这台机没有可用钥匙"。改用文本输出抓 `address:` 才对。
3. **命令失败被当成零结果**：`q ibc client states --node <错端口>` 返回的是 Usage 文本，
   我据此说过"测试网也是 0 客户端"——错，实际有 3 个（后来又加了 2 个）。
   查不到 ≠ 没问题，报错 ≠ 空值，这条又应验了一次。

### 主网还差什么（一句话）
主网侧的闸门本来就是开的（`allowed_clients: ['*']`、transfer 模块 send/receive 都 true），
但**这条当时就写错了**（2026-11-05 主网实测更正）：LIGHT 是原生 `ulight`，ICS-20 能直接搬；
   链上 `light_token`（code 1）只是 CW20 门面（`token_info.denom=ulight`，无按地址余额查询）——
要对外说"LIGHT 能跨链"，得先定资产形态：warp 式封装 / 改原生 denom / 先只搬子代币。
这一步在资金语义上不等价，等所有者选路；选完我按测试网这套同样的流程在主网做通道 + 回执告警。

---

## 2026-11-04（同日续 5）跨链已双向跑通，账目能对上（测试网链对 A↔B）

四笔链上事实（命令与数额都可复核）：

| 方向 | 动作 | 结果（链上实测） |
|---|---|---|
| A→B | 发 1,000,00 stake（transfer/channel-2 → B channel-0） | B 侧账户出现 `ibc/C053D637CCA2A2BA030E2C5EE1B28A16F71CCB0E45E8BE52766DC1B241B77878 = 1,000,00`；A 侧通道托管地址 `wasm12k2py…` 锁住 1,000,00 ✓ |
| B→A（第 1 笔） | 退回 400,000（未指定收款人，落到 A 侧中继账户） | A 中继账户 `wasm179u6h…` 余额 3,060,167（含这 400,000）；B 的 ibc 余额 1,000,00 → 600,000 ✓ |
| B→A（第 2 笔） | 退回 100,000，`--receiver` 指定为 `wasm1rct6n8…` | A 上该账户出现 `100,000 stake`；B 的 ibc 余额 600,000 → 500,000 ✓ |
| 守恒核对 | — | A 托管 = 1,000,00 − 400,000 − 100,000 = **500,000**（与查询一致）；B ibc 余额 500,000；两边相加 = 1,000,00 ✓ 没有凭空多或少 |

即：**跨链代币转账（ICS-20）双向都真的走通了**——发送侧锁仓/接收侧按 `ibc/<哈希>` 记账、
回流时按原 denom 解锁，数额逐笔对得上；回执与收包由 hermes 的 `clear packets` 搬运。

踩到并修掉的三个真问题（都是"看着配好了其实没通"）：
1. B 的 gRPC 配 `localhost:9090`，而 9090 **已被主网 wasmd 进程占用**，B 的 gRPC 实际从没监听；
   hermes 打到 9090 是打到主网节点上，于是报 `account not found`。靠 `ss -ltnp` 看到属主才查清，
   换到 127.0.0.1:9099 后一次就通。
2. `wasmd keys list` 在这个构建里**没有 `-o` 标志**（返回的是帮助文本），我一度据此判定"本机没钥匙"。
3. `hermes create channel` 的参数组合：`--new-connection` 与 `--a-connection` 互斥、
   也没有 `--all-channels` 这种启动参数（是配置项），照文档想当然会静默什么也不做
   ——它的 `rc=0` 不代表建成，必须回链上查通道才算数（这条本项目铁律又应验一次）。

主网还差什么（一句话、不含糊）：主网 IBC 闸门本身是开的
（`allowed_clients: ['*']`、transfer 模块 send/receive 均为 true），
资产形态这一条已核实：**LIGHT 就是原生 `ulight`**，ICS-20 可直接搬运，不需要 warp 也不需要改形态。
剩下的方向题是"对端链选谁、接收哪些 ibc 面额、中继权限额度"——这些要你定；定完我就照这套已验证流程在主网建通道，
并同时补上"中继心跳"和"轻客户端剩余寿命"两条告警（这次反向包差点因为中继没搬回执而卡住，
正是缺这两条告警的现场版）。
