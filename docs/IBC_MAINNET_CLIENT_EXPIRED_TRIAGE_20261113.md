# 主网 IBC 客户端已 Expired —— 2026-11-13 每小时巡检定位（只读，未改动任何生产状态）

结论先说：**lightdao-mainnet-1 ↔ osmosis-1 的 A 侧轻客户端 07-tendermint-0 状态已经是 `Expired`**，
且通道上压着 **3 笔未确认报文（commitments seq 8/9/10）**。主网跨链哨兵 `ld_xc_mainnet_watch.py`
仍然每 10 分钟报"正常"，因为它**既不查客户端状态，积压判据又取错了 JSON 字段**。
本条不是测试网问题，是主网用户可见问题（"转出去没到账"）+ 监控失明。

## 取证数据（全部在网关本机只读查询得到，UTC）

| 项 | 实测值 |
|---|---|
| 通道 | transfer/channel-0 (A) ↔ transfer/channel-111104 (B)，`STATE_OPEN`，`ORDER_UNORDERED` |
| A 侧客户端 | `07-tendermint-0` |
| 客户端状态 | `wasmd q ibc client status 07-tendermint-0` → **"Expired"** |
| 信任期 / 解押期 | 259200s（3 天）/ 1209600s（14 天） |
| 最后一条共识状态 | B 高 74390830，时间 **2026-11-07T11:54:06Z**（共 17 条，全部停在 11-07） |
| B 侧当前高度 | ≈74994379 → 客户端落后约 60.3 万块 / **6.1 天**，远超 3 天信任期 |
| 过期时刻推算 | ≈**2026-11-10T11:54Z**，即已过期约 **3.1 天** |
| 未确认报文 | `packet-commitments transfer channel-0` → 3 条，seq **8、9、10** |

## 中继侧根因

`lightdao-ibc-mainnet.service`（hermes，config-mainnet.toml）systemd 仍是 `active (running)`，
自 2026-11-07T16:28:54Z 起没重启过，但 **journalctl --since 2026-11-10 输出 0 行**，
最后一条是 2026-11-09T20:57Z `failed to reconnect to ws://127.0.0.1:26657/`，
此前密集出现 `event_source.websocket{chain=lightdao-mainnet-1}: ... reading from WebSocket connection timed out after 30 seconds`。

链路是：hermes 的 A 侧事件源写死走网关本机 `ws://127.0.0.1:26657`，而本机 lightd 早在
2026-11-07 共识 panic（height 742040，AppHash 分歧）后已不能供块；现在 26657 是由转发器代理到
健康验证者的。转发器能答 HTTP `/status`（所以巡检第 1 项、status.json 都是绿的），
但 hermes 依赖的 WebSocket 事件订阅这条腿没通 → 它拿不到新事件 → 从不 `update_client` →
信任期一路衰减到过期。**这与客户端最后更新时间停在 11-07 11:54Z 是同一条时间线。**

## 哨兵的两个判据漏洞（不是环境坏了，是判据写漏/写错）

1. **完全没覆盖客户端状态。** `ld_xc_mainnet_watch.py` 只检查 4 件事：服务 active、通道 OPEN、
   两侧出块、积压=0。全文 `client status` / `Expired` / `trusting` 出现 0 次。
   客户端过期不会让通道离开 `STATE_OPEN`，也不会让任何一侧停止出块，所以四项全绿照样过期。
   `--selftest` 也只植入这 4 类故障，天然测不出来。

2. **积压恒等于 0。** `backlog()` 取 `d.get("packet_commitments")`，而本链 CLI 该查询返回的键是
   `commitments`（实测输出 `{"commitments":[{"sequence":"10"...},{"sequence":"8"...},{"sequence":"9"...}]}`）。
   取不到键 → `or []` → `total=0` → 日志稳定输出"无积压"。当前真实积压是 3。
   （`infra/ld_xc_mainnet_watch.py` 仓库副本与在用文件逐字节相同，两处同病。）

## 影响面

- 通道状态仍是 OPEN，锁仓账面未被破坏；A→B 已发的 seq 8/9/10 三条报文拿不到回执，
  用户侧表现为跨链转账长时间不到账。
- 客户端过期期间，任何依赖该客户端验证的新报文/回执都会被链上拒证。
- 测试网方向是同一条衰减曲线的早期阶段：`ld_ibc_relay.py` 报 07-tendermint-4（对面 testnet-b）
  已用掉 84%、07-tendermint-0（对面 testnet-gas）已用掉 80% 的 10 天信任期，
  预计 **2026-11-15 前后**先后过期。测试网中继的 hermes 配置只覆盖 testnet↔osmo 测试网那一对，
  这几条 testnet 之间的客户端本来就没有中继在搬，空闲即衰减。

## 建议处置（都需要人工批准，本轮一律未动手）

按"最小破坏"排序：

1. **止血（不改共识、不改合约）**：对 A 侧 07-tendermint-0 做一次 `update_client` / hermes
   `push client` 之类的客户端刷新，把共识状态推到 B 侧可信高度内，再让积压的 seq 8/9/10 走 ack。
   前提是先确认 B 侧对应客户端是否也已过期——本轮只查了 A 侧（B 侧需要向对面发查询，未做）。
   这属于主网写操作，**必须逐次授权**。
2. **恢复中继的事件源**：把 hermes 的 A 侧 WebSocket 端点从"网关本机 26657（现由转发器代答）"
   改成能正常提供事件订阅的节点，或直接等本机 lightd 重建。改配置会牵涉中继重启，按硬规则不在本轮范围。
3. **补判据（低风险，纯只读监控改动）**：给 `ld_xc_mainnet_watch.py` 增加第 5 项检查——
   `q ibc client status <client_id>` 非 `Active` 即 ALERT，并按信任期已用比例提前预警；
   同时把 `backlog()` 的取值改成 `d.get("commitments") or d.get("packet_commitments") or []` 两种键都认，
   并在 `--selftest` 里加"客户端 Expired 必须响""积压非 0 必须响"两植。
   建议先出 patch 走评审，评审过了再落到在用脚本 + 仓库 `infra/`，避免又造一次 drift。
4. **不要顺手做的事**：不要为了让告警闭嘴而把信任期调大或改用 `--max_block_time` 兜底；
   那是改共识参数，不解决报文积压，还会掩盖下一次衰减。

## 本轮同时复核到的两件已缓解项（记录以免重复排查）

- **每日 keys 备份空归档**：11-10/11/12 三份 keys 归档各 217B（0 条 .info，脚本自报 FATAL-W）。
  在用 `/home/ubuntu/ld_backup.sh` 于 2026-11-13T00:48Z 被替换（8337B，keyring 候选改为按 .info 计数选择），
  今天 06:00Z 产出 12687B、**12 条 .info**，`file` 验为 AES-256 对称加密包，已缓解。
  仍存两点：(a) 在用版本保留 `find ... -mtime +7 -delete` 的删除式留存，仓库 68232d8 那版
  "移入 .pruned 不真删"的修复**依旧未部署**，且现在漂移方向反过来（在用与仓库互不相同，各 8337B/11368B）；
  (b) 11-07 那份 11838B 的可恢复归档会在 11-14/15 被删除式留存清掉，虽然今天已有好备份，
  仍建议人工把它 `mv` 进 manual-keep 再放行留存。
- **重放节点 26659 卡在 0**：自 2026-11-11T23:52Z 起 `latest_block_height=0`、
  `earliest_block_height=0`、blockstore 空（data 目录仅 132K），10 个 peer 全部在线、整份日志 0 条 ERR。
  直接原因是配置 `[statesync] enable = false`，StateSync service 起了但从不请求快照，blocksync 也没取过第 1 块。
  这条告警的判据是对的（确实 39 小时没动），修法需要改配置并重启该节点，按硬规则未动。
  站点侧无影响：26657 仍由转发器供健康高度。
- 巡检第 5 项权限面全绿：`/etc/lightdao` 是 755，`gw_admin.env` 是 640 root:ubuntu，
  8080 仅绑 127.0.0.1，ubuntu 身份可读 leak_ips.txt/hosts.env，泄露门禁没有降级。
  顺带记一笔：网关节点当前仍在和一个老腾讯云 observer 保持 P2P（连接时长 ~11 天），
  该地址在 leak_ips.txt 的老腾讯云分组里、注释本身就写着"保留到 DNS/peer 完全迁走"，属已知遗留，不是新泄露。
