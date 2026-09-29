#!/bin/bash
# ld_watchdog.sh — 独立于 monitor 的"监控防致盲"看门狗(每15分钟):
# 1) status.json 必须新鲜(<15min),否则说明 monitor 死了/被致盲;
# 2) ld_alerts.log 必须可写(触一下),否则告警通道坏了;
# 3) 网关 /v1/health 必须 200。
# 任一失败 → 写 ld_watchdog.log + Discord 报警(走 discord_bot,不依赖 monitor)。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
NOW=$(date +%s)
FAIL=""
TS=$(python3 -c "import json;print(json.load(open('/var/www/lightdao/status.json'))['ts'])" 2>/dev/null || echo 0)
AGE=$((NOW-TS))
[ "$AGE" -gt 900 ] && FAIL="status.json stale ${AGE}s"
touch /home/ubuntu/ld_alerts.log 2>/dev/null || FAIL="$FAIL alerts-log-unwritable"
HC=$(curl -s -o /dev/null -w "%{http_code}" -m 8 http://127.0.0.1:8080/v1/health)
[ "$HC" != "200" ] && FAIL="$FAIL gateway-http-$HC"
echo "$(date -u +%FT%TZ) watchdog ok=${FAIL:-1} age=${AGE}" >> /home/ubuntu/ld_watchdog.log
if [ -n "$FAIL" ]; then
  python3 /usr/local/bin/discord_bot.py send "⚠️ WATCHDOG: $FAIL (monitor may be blinded)" >/dev/null 2>&1
fi
