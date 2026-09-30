#!/bin/bash
# ld_tx.sh — 所有自动化链上 tx 的标准包装: 广播→等→查 DeliverTx 码→TXOK/TXFAIL 入日志, 失败即告警。
# 用法: ld_tx.sh <label> <wasmd tx ... 原参数(不含 -o json)>
LABEL="$1"; shift
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
OUT=$("$@" -o json -y 2>&1)
HASH=$(printf '%s' "$OUT" | grep -oE '"txhash":"[A-F0-9]{64}"' | head -1 | cut -d'"' -f4)
sleep 7
CODE="unknown"
if [ -n "$HASH" ]; then
  CODE=$(wasmd q tx "$HASH" --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;s=sys.stdin.read()
try: print(json.loads(s[s.find('{'):]).get('code'))
except Exception: print('unknown')" 2>/dev/null)
fi
echo "$(date -u +%FT%TZ) $LABEL hash=$HASH code=$CODE" >> /home/ubuntu/ld_tx.log
if [ "$CODE" != "0" ]; then
  echo "$(date -u +%FT%TZ) TXFAIL $LABEL code=$CODE" >> /home/ubuntu/ld_alerts.log
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "⚠️ TXFAIL $LABEL code=$CODE (ld_tx.log)" >/dev/null 2>&1
  exit 3
fi
exit 0
