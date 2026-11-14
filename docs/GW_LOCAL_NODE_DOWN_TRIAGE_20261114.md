# 网关本机主网节点缺位与 26659 重放停滞分诊（2026-11-14 自走巡检）

> 全程只读实测（curl / ps / ss / systemctl / 日志与配置读取）。未重启任何节点、未改中继、未发交易、未动 crontab、未改监控判据。
> 证据时间基准：2026-11-14T06:01Z–06:11Z。

## 1. 结论先说

1. 网关本机已经没有在跑的主网全节点。`lightdao-mainnet.service`（状态 enabled）自 2026-11-10T02:56:17Z 起 inactive，到本次已 4 天。
2. 所有内部工具（结算签名、跨链探针、巡检、以及本任务第 1 项）读的 `127.0.0.1:26657`，实际是应急 TCP 转发器 `ld_rpc_fwd.py`，它把流量转给一台远端健康验证者。链面因此"看起来全绿"，但网关对那一台远端节点是单点依赖。转发器自己的告警行也是这么写的：「勿当健康」。
3. 用来顶替本机节点的 26659 重放节点（起于 11-11 23:52Z，`--home ~/.wasmd --rpc.laddr tcp://0.0.0.0:26659`）56 小时来高度恒为 0。这不是"按设计不追块"，是取块链路真的坏了（见 §3）。

## 2. 26659 是怎么来的

`/home/ubuntu/resync_node.sh` 的动作序列：备份 config.toml → 写 persistent_peers → `systemctl stop lightdao-mainnet` → `wasmd comet unsafe-reset-all` → 以 26659 起 wasmd。
执行痕迹一致：`config.toml` 与 `priv_validator_key.json` 的 mtime 都是 11-11 23:52Z，`config.toml.bak-resync` 停在 10-13。
即本机主网区块库在 11-11 23:52 被清空重建；现在 `.wasmd/data` 只有 132K（`.wasmd` 全目录 17M）。

## 3. 卡 0 的实测根因（修正 32b6750 的判断）

上一轮 32b6750 记为「26659 重放卡 0 系 statesync enable=false 判据正确」。本轮实测显示这句话只对了一半，并且把结论说轻了：

| 实测项 | 结果 |
|---|---|
| `[statesync] enable` | false（确实没开状态同步） |
| P2P 连接 | `net_info` n_peers=10、listening=true，对端含观察者与 10 台验证者 moniker |
| 日志模块分布 | 自 11-11 23:52 起只有 pex 的 `Ensure peers` 心跳；无一条取块记录 |
| 启动握手 | ABCI Handshake 完成，appHeight=0，appHash 为空树根；Blocksync Reactor 与 BlockPool 均已启动 |
| 对端状态 | 10 个 peer 的 `node_state` 全为空 → 本机从未拿到任何对端的 height |
| 区块库 | data 目录 132K，height 恒 0，`earliest_block_height=0` |
| 节点侧报错 | 仅公网 seed 的拨号超时/拒绝；persistent_peers 与验证者连接正常 |

判读：TCP 与 NodeInfo 握手是通的，但**对端 Status 从未应答**，BlockPool 因此没有任何"高度比自己大"的候选 peer 可发块请求，于是只剩 pex 心跳、永远停在 0。所以这是同步链路真的坏了，不是"关了 statesync 就会慢慢追"。要么补可用的状态快照来源，要么换一条已知能起来的引导路径；两者都要动节点，本轮不动手。

对照参照：同一分钟内观察者报 829715、网关 26657 报 829640 → 随后 829744/829745（约 5s 出块、catching_up=false）。全网出块正常，问题只在这台重建的节点上。

## 4. 影响面

- 结算链路本次是健康的：day 62 与 day 63 的 `root_submitted` 均为 true，day 64 为 false（未到当日完成态，属正常）；ld_sign.log 末三行为 day 57/58/59 committed，ld_finalize.log 显示 day 63 `already: true`。
- 但签名与 finalize 全部经 26657 → 即全部依赖那一台远端验证者。该远端一旦失联，网关所有内部工具同时失明，第 1 项检查会立刻转红。这就是告警里「#2 未闭环」的实际含义。
- 不是资源问题：磁盘 53%、可用内存 2724M。

## 5. 顺带核实/更新的三件事

1. 测试网 IBC 客户端沿 20261113 记账的曲线推进：A 侧 07-tendermint-4 由 84% → 90%，B 侧 07-tendermint-0 由 80% → 86%，ETA 仍在 11-15 前后。两条链本身都在出块（26757 高 1338434、26957 高 162491，块时间距实测不足 10s），hermes `[mode.clients] enabled=true refresh=true`、三链配置均在。停滞起点（约 11-05/06）与 osmo-test-5 加入配置（11-06 00:14）、config 目录最后改动（11-07 13:05）时间吻合 → 判据是真阳性而非写错，代价只是退役中的 testnet↔testnet 通道冻结，不触及主网结算。解冻需发链上交易或重开通道，属禁区。
2. 76dcb44 记的"最后一份可恢复 keys 归档将被 -mtime +7 删掉"已自然解除风险：11-13 与 11-14 两份均为 12687B 的在用版本产物（对比 11-08 至 11-12 连续 5 天的 217B 空档），旧的 11838B 归档即使被留存策略移除也不再是唯一恢复点。当日 voters 归档 65051B 亦在。
3. 权限面三项全绿：`/etc/lightdao` 为 755、`gw_admin.env` 为 root:ubuntu 640、网关 8080 仅监听回环。

## 6. 待办（均需人工批准，自走执行器不会自行处理）

- 定本机主网节点怎么回来：恢复 `lightdao-mainnet.service`，还是把 26659 改造成能真同步的节点。无论哪种都要动节点。
- 节点回来之前，建议给 `ld_rpc_fwd.py` 的远端目标配至少 2 台轮询，先消掉单点。
- 第 8 项原计划把 `resync_node.sh` / `ld_rpc_fwd.py` / `ld_resync_watch.py` 补进 `infra/`，本轮实测否决：`git grep` 显示所抽检的 4 个基础设施公网地址在仓库内 0 命中，而它们正是 `/etc/lightdao/leak_ips.txt` 明令禁止入库的清单；`resync_node.sh` 内嵌 persistent_peers（公网 seed 与节点 ID），`ld_rpc_fwd.py` 内嵌远端验证者地址，原样入库必然踩泄露门禁。要做的话必须先把地址抽到 hosts.env / xchain.env 间接引用，再入库。
- 测试网那两条退役客户端：要么接受到期冻结并把探针判据收敛到"hermes 当前实际服务的通道"，顺带消掉每小时 2 条噪声；要么补一次 update_client。前者属改监控，交人工决定。
