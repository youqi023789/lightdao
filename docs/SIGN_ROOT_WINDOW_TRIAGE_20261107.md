## sign_root 日间空窗与 monitor reason 判据分诊（2026-11-07）

每小时巡检中，`/var/www/lightdao/status.json` 出现 `checks.sign_root.ok=false` 但顶层
`ok=true`、`reason=""` 的组合。本文记录根因定位过程与结论，供后续判据修订评审。

### 一、结论

1. 日根提交（root_submitted）的空窗是**设计内延迟**，不是事故，不需要人工补签。
2. `reason` 字段确实存在判据缺陷（读死字段），但**不影响告警是否触发**，只影响触发时能否说明原因。
3. 本次未改动任何生产代码与链上状态。

### 二、观测证据（2026-11-07 02:00–02:10Z 实测，非引用旧记忆）

| 项 | 值 |
| --- | --- |
| 链高度 | 本地 719952 → 720034（8 秒 +2，推进正常），`catching_up=false` |
| 观察者 RPC（公网 IP 不入仓，见运维手册） | 720034，与本地高度差 0 |
| `ld_day.sh` | cur=57 prev=56 |
| 合约 `epoch_info` | `day_in_epoch=56`（合约仍停在 56） |
| 网关 `/v1/day` | day 54/55/56 `finalized=true`；day 57 `finalized=false` |
| 合约 `root_submitted` | day 54=true 55=true **56=false** 57=false |
| `ld_sign.log` 末行 | `day 56 not complete on-chain yet (contract day=56, boundary 04:48Z) - skip, no wasted tx` |
| ubuntu crontab | `ld_sign_root.sh` 于 00:20/00:40 与 05:10/05:30；`ld_finalize.sh` 于 00:10/00:20/00:30 与 05:00/05:10/05:20/05:30 |

### 三、为什么 56 号未签却属正常

结算与链上对「日」的口径相差一天：网关按 `ld_day.sh` 的 cutover 口径已进到 57 日并把 56 日
finalize 完成，而 mining_reward 合约的 `day_in_epoch` 仍是 56（合约日界在 04:48Z）。

`ld_sign_root.sh` v5 在 `sign_day()` 里对此显式设了闸：

```
local CCD=$(contract_current_day)
if [ -n "$CCD" ] && [ "$DAY" -ge "$CCD" ]; then
  echo "day $DAY not complete on-chain yet (contract day=$CCD, boundary 04:48Z) - skip, no wasted tx"
  return 0
fi
```

即 `DAY >= 合约当前日` 时直接跳过，避免对着尚未过界的日发投票交易（白烧 gas 且必然失败）。
脚本头注亦说明此为「合约日界与网关日界不一致（纪元对齐提案执行前）」的临时处理。

因此 00:20/00:40 两轮只完成回溯确认（day 50–55 全部 `committed (threshold reached)`），
56 号留待 04:48Z 过界后的 05:10/05:30 两轮提交。cron 之所以在 05:xx 再排一轮，正是为此。

本次按巡检规程执行了 `ld_sign_root.sh`（幂等、7 日回溯），输出与上述一致、`EXIT=0`、
未产生任何交易，属预期的 no-op。上一完整日（55）多签齐、矿工可正常领取。

### 四、判据缺陷（建议修，本次未动）

`ld_monitor.py` 中 sign_root 分支本身是正确的：未签时只在 UTC 6 点后判事故，给足 04:48Z
过界加 05:10/05:30 补签的余量。

```
if not sok:
    if datetime.datetime.utcnow().hour >= 6:
        st["ok"] = False; alert("root not signed for day %s" % (day - 1))
```

问题在汇总 `reason` 的部分。`checks["finalize"]` 与 `checks["sign_root"]` 存的是**字典**
（`{"ok": ...}`），而判断写成了与布尔常量 `False` 比较：

```
if c.get("finalize") is False: _why.append("finalize")
if c.get("sign_root") is False: _why.append("sign_root")
```

`{"ok": false} is False` 恒为假，故这两项**永远不会进 `_why`**。后果是 6 点后真出事、
顶层 `ok` 已被置 false 时，`reason` 仍可能是空串，值班只看到 `ok=false` 而看不到原因。

同型问题在 WP-I18N 分诊（cf389fb 之前一轮，commit 337da95）已出现过一次，都是判据读了
不存在的字段形态。

建议改法（评审后再落地，勿在无人值守巡检中直接改生产判据）：

```
if not c.get("finalize", {}).get("ok", True): _why.append("finalize")
if not c.get("sign_root", {}).get("ok", True): _why.append("sign_root")
```

注意 `st["ok"]` 由 sign_root 分支直接置位，`reason` 只是说明串，因此本缺陷不会漏告警、
只会漏归因，优先级中等。同时 `checks` 里 `expiry_*` 为数值、`miners_today` 为计数，
不应被当作布尔纳入 `_why`。

### 五、巡检快速复核命令

```
C=wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx
/usr/local/bin/ld_day.sh; /usr/local/bin/ld_day.sh prev
wasmd q wasm contract-state smart $C '{"epoch_info":{}}' --node http://127.0.0.1:26657 -o json
D=$(/usr/local/bin/ld_day.sh prev)
wasmd q wasm contract-state smart $C "{\"root_submitted\":{\"day\":$D}}" --node http://127.0.0.1:26657 -o json
curl -s "http://localhost:8080/v1/day?day=$D"
tail -3 /home/ubuntu/ld_sign.log
```

判据：`root_submitted(day prev)=false` 时，先看 `ld_sign.log` 是否给出
`not complete on-chain yet` 与当前 UTC 是否 < 05:10；两者同时成立即属正常空窗，
越过 06:00Z 仍为 false 才算真事故（此时 monitor 会自动 ALERT）。
