#!/usr/bin/env bash
# qa_cross_cron.sh — 每小时跑跨层自检，失败才告警；但【同一批问题不逐小时刷屏】。
#
# 为什么改（实测）：CROSS-FAIL 从 10-29 起每小时一条，三天 62 条，内容却始终是
# 同样的 C1/C7。没有签名去重的告警只有两种下场：要么被忽略，要么逼人把整条告警关掉——
# 后者会把真问题一起静音。所以：
#   1) 告警里带上"哪几项失败"，不用去翻日志就知道要处理什么；
#   2) 失败集合没变时不重复告警，但每 24 小时补一条"仍未解决"，避免长期问题被静音；
#   3) 失败集合变化（新增/消失项）立即告警；
#   4) 状态文件读不到/写不进都要喊出来——"检测到了但没人知道"是本项目反复挨打的模式。
set -u
STATE=${LD_CROSS_STATE:-/home/ubuntu/ld_cross_state.json}
LOG=${LD_CROSS_LOG:-/home/ubuntu/ld_cross.log}
ALERTS=/home/ubuntu/ld_alerts.log
# 可把被测命令换掉（默认就是线上那条）：判据要能被"植入成功/失败"两种情况验证，
# 不能只能拿真实自检当靶子——上一版恢复路径就是因为没法替换而根本没测到。
CHECKER=${LD_CROSS_CHECKER:-/usr/bin/python3 /usr/local/bin/qa_cross.py}
OUT=$(eval "$CHECKER" 2>&1); RC=$?
printf '%s\n' "$OUT" >> "$LOG"
FAILED=$(printf '%s\n' "$OUT" | grep -oE '^FAIL [A-Z][0-9]+' | awk '{print $2}' | sort -u | tr '\n' ',' | sed 's/,$//')
[ -z "$FAILED" ] && FAILED="(rc=$RC，未识别到 FAIL 行)"
NOW=$(date -u +%s)
STAMP=$(date -u +%FT%TZ)

if [ "$RC" = 0 ]; then
  # 恢复了就把状态挪走（不用 rm：这台机器上我自己定的规矩是"任何删除都走可恢复路径"，
  # 状态文件虽小也不该例外），并留一条 NOTE
  if [ -f "$STATE" ]; then
    echo "$STAMP CROSS-OK 前一次失败项：$(sed -n 's/.*"failed": "\([^"]*\)".*/\1/p' "$STATE" | head -1)" >> "$ALERTS"
    printf '%s\n' "$STAMP NOTE [cross] 跨层自检恢复正常" >> "$LOG"
    mv "$STATE" "$STATE.prev" 2>/dev/null || true
  fi
  exit 0
fi

PREV=""
if [ -f "$STATE" ]; then
  PREV=$(sed -n 's/.*"failed": "\([^"]*\)".*/\1/p' "$STATE" | head -1)
  LAST=$(sed -n 's/.*"ts": \([0-9]*\).*/\1/p' "$STATE" | head -1)
  LAST=${LAST:-0}
else
  LAST=0
fi

SINCE=$(( NOW - LAST ))
if [ "$PREV" = "$FAILED" ] && [ "$SINCE" -lt 86400 ]; then
  # 同一批问题且不到 24 小时：只更新日志，不重复告警
  printf '%s\n' "$STAMP CROSS-SKIP-DUP 同签名（$FAILED）已在 $((SINCE/3600)) 小时前告警过" >> "$LOG"
  exit "$RC"
fi

echo "$STAMP CROSS-FAIL [$FAILED]" >> "$ALERTS"
/usr/bin/python3 /usr/local/bin/discord_bot.py send \
  "⚠️ CROSS-LAYER GATE FAIL：$FAILED（详见 ld_cross.log；$(printf '%s\n' "$OUT" | grep '^FAIL' | head -2 | cut -c1-120 | tr '\n' ' ')）" >/dev/null 2>&1
if ! printf '{"failed": "%s", "ts": %d}\n' "$FAILED" "$NOW" > "$STATE" 2>/dev/null; then
  echo "$STAMP CROSS-STATE-WRITE-FAIL 写 $STATE 失败，去重将失效（会变成逐条告警）" >> "$ALERTS"
fi
exit "$RC"
