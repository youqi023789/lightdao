#!/bin/bash
# ld_observer_watch.sh v2 — 观察者节点同步监控:每10分钟,高度2小时无进展则Discord告警
# v2: 原实现要 ssh 跳到观察者机再 curl(迁移到 HK 后家目录无私钥 → 一直 QUERY-FAIL);
#     改为直接 curl 观察者 RPC(26657 本就对外可读),无密钥依赖。
test -r /etc/lightdao/hosts.env && . /etc/lightdao/hosts.env
OBS=${LD_OBS_RPC:-}
[ -z "$OBS" ] && { echo "$(date -u +%FT%TZ) CFG-FAIL 缺少 LD_OBS_RPC（侧车未读到，拒绝静默跳过）"; exit 1; }
H=$(curl -s --max-time 12 "$OBS/status" 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)[\"result\"][\"sync_info\"][\"latest_block_height\"])" 2>/dev/null)
[ -z "$H" ] && { echo "$(date -u +%FT%TZ) QUERY-FAIL"; exit 0; }
LAST=$(cat /tmp/ld_obs_last_h 2>/dev/null || echo 0)
STAMP=$(cat /tmp/ld_obs_last_t 2>/dev/null || echo 0)
NOW=$(date +%s)
if [ "$H" == "$LAST" ]; then
  STUCK=$(( NOW - STAMP ))
  if [ $STUCK -gt 7200 ] && [ "$H" != "283000" ]; then
    python3 /usr/local/bin/discord_bot.py send "⚠️ UCloud观察者同步卡住: height=$H 已 $((STUCK/60)) 分钟无进展" >/dev/null 2>&1
  fi
else
  echo "$H" > /tmp/ld_obs_last_h; echo "$NOW" > /tmp/ld_obs_last_t
fi
echo "$(date -u +%FT%TZ) height=$H"
