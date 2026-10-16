# 金库资金变动记录（Treasury Ledger）

本文件存在的唯一原因：**任何动用金库、多签或改变资金归属的操作，执行前后都必须留下可核对的记录，并即时告知资产所有者。**

规则（2026-10-15 起生效，由本次事件催生）：

1. 执行**前**：在本文件登记提案号、提案人、审批人、金额、收款方、时间锁到期时刻。
2. 执行**后**：补记交易哈希、区块高度、UTC/北京时间、执行后各方余额。
3. 同时在告警日志留一条，并在与所有者的对话里显式报告——**"完成"不等于"已告知"**。
4. 记录中的每个字段必须来自链上查询，不接受记忆或推断；文末附可复现命令。

---

## 2026-10-15 金库多签 → 生态基金：4 亿 LIGHT

| 字段 | 值 | 来源 |
|---|---|---|
| 提案号 | `id = 1` | `treasury_multisig` 合约 `{"tx":{"id":1}}` |
| 动作 | `propose_transfer` → `approve` ×2 → `execute_transfer` | 链上事件 `wasm.action` |
| 签名人总数 | 5 | 合约 `{"signers":{}}` |
| 审批门槛 | 3 / 5 | 合约配置 |
| 已审批（3 票，链上原样） | `wasm1wh0vkmvln8xdpk5wa8atuh7ujlf6dau65wm522`（提案人）<br>`wasm1ual8frq2yrl5hxdmftaxq2jrplmvalylvdsq0w`<br>`wasm1s60nhc7c602efdwhwqdd420yqqycpxud5sd53d` | 同上 |
| 付款方 | `wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u`（treasury_multisig） | 银行事件 `transfer.sender` |
| 收款方 | `wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835`（生态基金） | 银行事件 `transfer.recipient` |
| 金额 | `400000000000000 ulight` = **400,000,000 LIGHT**（总供应量 25 亿的 16%） | 提案 `amount` + 银行事件一致 |
| 提案入队时刻 `queued_at` | `1791763032` = 2026-10-11T23:57:12Z（北京 10-12 07:57:12） | 提案字段换算 |
| 时间锁 | `TIMELOCK_SECS = 259200`（72 小时，不可由紧急提案豁免资金动作） | 合约常量 |
| 最早可执行时刻 | 2026-10-14T23:57:12Z（北京 10-15 07:57:12） | 入队 + 72h |
| 实际执行交易哈希 | `9470524A749B58872D1CD1CF0A893F543C5D1A5A9F8AAD9D2A98B1BBD909AE30` | `tx_search` |
| 高度 / 时间 | 366304 / 2026-10-15T00:05:19.779Z（北京 08:05:19） | `/block?height=366304` |
| 到期后延迟 | 8 分 07 秒（定时任务节奏所致，非人为） | 计算 |
| 提交执行的账户 | `wasm1wh0vkmvln8xdpk5wa8atuh7ujlf6dau65wm522`（即 1 号签名人） | `message.sender` |
| 手续费 | 50,391 ulight，进入链上费用池 | `coin_spent` |
| 码值 | `0`（成功） | `tx_result.code` |
| 执行后余额 | 金库多签 **842,000,092.73 LIGHT**；生态基金 **正好 400,000,000.00 LIGHT** | `q bank balances` |
| 资金是否离开系统 | **否**。仅从金库多签合约转入生态基金合约，无对外转账、无继续外流 | 链上全量核对 |

用途符合白皮书 §4.6 / §7 生态基金的既定安排（提案本身即按此目的提交并获 3/5 通过）。

### 这次真正失败的是什么

机制没有失败：**3/5 审批 + 72 小时时间锁都按设计生效并如期执行**。失败的是流程——**执行完成后没有任何人通知资产所有者**，也没写进任何"已执行"台账，导致创始人清晨看到余额变动时按"被盗"处置。本文件第 1~4 条规则即为此而设。

### 我此前两处误判，在此正式收回

1. ~~"多签形同虚设、没有任何机制阻止这笔转账"~~ —— **错误**。审批与时间锁都真实拦到了规定时点才放行。仍然成立的只有一点：**5 把签名钥目前全在同一台服务器上**，这是结构性集中风险，处置方案见下。
2. ~~"这笔交易在链上查不到"~~ —— **错误，且错在我自己**。原因是我把 CometBFT RPC 的 `order_by=asc` 按未加引号的值传了进去，节点返回 HTTP 500，被我误读成"查无此笔"。链上索引一直正常。用文末命令可查到唯一一笔。

### 遗留风险与处置状态

- **5 把签名钥集中在单台主机**：待迁移到独立主机/硬件（属主密钥操作，需所有者在线批准）。迁移期间金库不产生新的动账。
- **`/funds.html`、`/contracts.html` 是 10-14 快照**：现在公开页面仍写着"生态基金 0、资金都在金库内"，**与本页事实矛盾**，必须改为实时取数或标注快照时间（进行中）。
- 网关机上仍有一个**测试网节点**在跑（`lightd.testnet.bin`，其 LCD 在 127.0.0.1:1317 返回测试网验证者数据）：任何验证者/资金展示**禁止**接入该端口，否则会拿测试网数据冒充主网。

### 复现命令（任何人可在能连主网的节点上执行）

```bash
# 1) 提案本身
wasmd q wasm contract-state smart \
  wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u \
  '{"tx":{"id":1}}' -o json
wasmd q wasm contract-state smart \
  wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u \
  '{"signers":{}}' -o json

# 2) 那笔转账（注意：不要把 order_by 写成不带引号的 asc，否则节点返回 500）
curl -sG http://127.0.0.1:26657/tx_search \
  --data-urlencode 'query="transfer.recipient='"'"'wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835'"'"'"' \
  --data-urlencode 'per_page=10'

# 3) 区块时间
curl -s http://127.0.0.1:26657/block?height=366304 | head -c 400

# 4) 当前余额
wasmd q bank balances wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u -o json
wasmd q bank balances wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835 -o json
```

## 2026-10-16 密钥管理变更（已执行）

网关上的 5 把金库明文私钥已摘除，改为加密冷备份 + 所有者离线口令；
链上 3/5 审批与 72h 时间锁不变。操作流程见 。
摘除前闸门：解密还原 5 地址与链上 signers 逐一比对通过；摘除后复核：金库 842,000,093.15 LIGHT、
生态基金 400,000,000.00 LIGHT、7 个 voter 账户完好、无待执行提案。
