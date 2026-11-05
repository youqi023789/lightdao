# 跨链（IBC）实测与面板 · 2026-11-05 增补

本文只记**能被复现的证据**：每条结论后面跟着能直接跑的命令或链上哈希。
历史上这里出现过"命令跑完了就算成了"的写法，已经改掉了。

## 1. 常驻中继确实自己在搬包（不是人工 clear 出来的）

测试方式：故意把中继进程停掉，再打一笔转账，看告警是否响、恢复后包是否自己到账。

| 步骤 | 事实 | 复现命令 |
|---|---|---|
| 停中继 | `systemctl stop hermes-relay.service` | — |
| 发一笔 | A→B 50,000 stake，`txhash=30D6061A85A37214F5CD33407000ECE8E6466AFB41C89723D868989A80B479FB` | `lightd tx ibc-transfer transfer transfer channel-2 …` |
| 看告警 | 看门狗退出码 1，报"中继进程不是 active"；注入假序号两轮后报"仍未确认" | `LD_IBC_STALE_MIN=0 python3 /home/ubuntu/ld_ibc_relay.py` |
| 恢复 | 启动中继后 **不手动 clear packets**，B 侧收款人 ibc 余额 100,000 → 150,000（+50,000） | `systemctl start hermes-relay.service` 后轮询 |
| 再验一次 | A→B 30,000（seq 4）与 A→B 20,000（seq 5，`txhash=F7C8C968C0D0484D5A852394396CE424C11AAA669075FB18AEB12CE7018C819C`）都在无人为干预下到账 | 同上 |

对平账（截至本文提交）：A 侧 `channel-2` escrow = **720,000 stake**
= 500,000（11-04 双向测试后余额）+ 200,000（11-05 上午）+ 20,000 + 30,000 + 20,000（面板演示两笔），
B 侧收款人 `ibc/C053D637…` = **220,000**。两侧数字能对上，说明没有双花或凭空铸造。

复算命令：

```bash
B=/home/ubuntu/lightd.testnet.bin
$B q bank balances wasm12k2pyuylm9t7ugdvz67h9pg4gmmvhn5v4658cl --node http://127.0.0.1:26757   # A 侧 escrow
$B q bank balances wasm1vgjc0y4ut6j9xjrhxvqqlguzgaqkxer2anjkmg --node http://127.0.0.1:26957   # B 侧收款人
$B q ibc channel packet-commitments transfer channel-2 --node http://127.0.0.1:26757           # 应为空
```

## 2. 之前"中继装了但不干活"的真原因（已修）

日志里反复出现：

```
send_tx_with_account_sequence_retry{chain=lightdao-testnet-b account.sequence=10}:
estimate_gas: failed to simulate tx … account sequence mismatch, expected 11, got 10
```

原因不是配置漏了链 B（链 B 一直在 `config.toml` 里），而是**守护进程和我手动敲的命令共用同一个签名账户**：
每手动跑一次 `hermes tx` / `hermes clear packets`，链上序列号就往前走，进程内存里的序列号落后一截，
于是它构造的每笔交易都被 `sigverify` 拒掉——表现为"进程活着、通道 OPEN、钱却不过去"。

处理：手动操作改用另一个账户（面板演示用 `demo`），并且**不再用中继账户签名**；
新增看门狗 `ld_ibc_relay.py` 每 15 分钟检查五件事：进程、两条链心跳、未确认包积压、
客户端寿命/冻结、中继账户油钱。`--selftest` 植入五类假故障，实测 **5/5 都能报警**，
空积压时不误报。

> 为什么未确认包用 `packet-commitments` 而不是"发送序号减接收序号"：实测这个 SDK 版本两侧
> `next_sequence_receive` 恒为 1，而链上明明已经双向入账（escrow 与 ibc 余额都对得上）。
> 拿它当指标会天天误报，所以只信 commitments（它是 IBC 记账本体：被收下且 ack 送回才清空）。

## 3. 被排除的噪声：osmo 旧通道

四个 `osmo-test-5` 客户端从 10-14 起就 `outside of trusting period`，日志一直被它们刷屏，
真故障被埋在里面。看门狗现在**只监控在用的两条链**，但会打印"跳过了几条"，不做静默吞掉。
通道本身没有删除（要删得走治理与重开通道流程），只是不参与告警判定。

## 4. 客户端跨链面板（v1.10.29 起）

数据面：`lightdao-xchain.service`（只绑 127.0.0.1:8096，公网经 nginx `/xchain/`）。

| 端点 | 方法 | 内容 |
|---|---|---|
| `/xchain/v1/ibc` | GET | 三条链高度、通道状态、两侧未确认包、A 侧 escrow、中继账户油钱、演示账户与剩余额度 |
| `/xchain/v1/prices` | GET | CoinGecko 行情（服务端 60 秒缓存，访客不重复吃配额） |
| `/xchain/v1/quote` | GET | 第三方聚合器 Li.Fi 的跨链报价（占位地址，不带访客信息） |
| `/xchain/v1/transfer` | POST | **测试网** A→B 真实转账；`/xchain/` 其余路径只允许 GET（实测 POST 返回 403） |

探针不做的事：不签名主网、不持有任何主网私钥、不广播除这一条测试通道以外的任何交易。

面板上的诚实性约束：
- 主网跨链明写"未开通"，并给原因（LIGHT 是 CW20 合约代币，IBC 20 号标准只搬原生币；
  封装路由与治理授权未完成）。这条由 `ld_render_truth.py` 的文案门禁把住，不许被改口。
- 探针自己读不到的项写进 `errors[]`，面板如实显示"读数有缺口"，不拿旧数装实时。
- 外部链（ETH/BNB/UNI/SOL）交易入口是第三方聚合器深链，文案明写"我们不托管资产、不参与撮合"。

## 5. 面板转账的护栏（写在服务端，不靠前端自觉）

`transfer()` 在广播前逐项检查，任一不过直接拒绝并把原因回给前端显示：

1. 方向只认 `ab`（`ba` 需环境变量显式打开），通道固定 `channel-2`；
2. 金额 ≤ `XC_MAX`（默认 50,000 stake，6 位小数），且必须是整数；
3. 收款人必须等于白名单里的演示地址（实测传别的地址被拒："演示转账只发往固定的演示地址"）；
4. 每小时 ≤ `XC_QUOTA`（默认 12 笔）、同一来源 5 分钟 1 笔，台账落盘 `ld_xchain_txhist.json`（重启不清零）；
5. 链上 `chain-id` 必须是 `lightdao-testnet-gas`；通道不是 OPEN 就拒；A→B 已有在途包就拒；
6. 中继账户油钱 < 200,000 或演示账户余额 < 200,000 就拒（宁可按钮报错，也不发一笔注定卡住的包）；
7. 每笔记 `ld_xchain_tx.log`（时间、金额、txhash、来源 IP）。

实测（11-05 09:1x）：越界三种都被拒；正常一笔上链 `txhash=143047E1064524C8CFD89D7B7A859B59D1F54F36BAA22045F4A008FCC71FDCED`，
20,000 stake 锁进 escrow（700,000 → 720,000），未确认包归零（自动中继），5 分钟内第二笔被限流拒绝。

面板健康由 `ld_xchain_watch.py` 每 30 分钟检查：进程、数据新鲜度（<180 秒）、高度不回退、
探针自报 errors、**公网反代路径**（防止"服务活着但反代断了，访客全瞎"）、行情币种数。
`--selftest` 植入四类故障，实测 4/4 报警。

## 6. 还没做的事（不写成已完成）

- 主网 LIGHT（CW20）跨链：需要封装路由（warp 一类）或把 LIGHT 改成原生资产，且要走治理；
  目前只有测试网 A↔B 的原生 `stake` 通道被证明能自动双向搬。
- ETH/BNB/SOL 的"在客户端内直接成交"：当前是报价 + 深链，签名与广播发生在用户钱包/聚合器；
  要做成站内直成交需要接钱包 SDK 与对方路由合约，属于新的资金路径，需要所有者批准后再动。
