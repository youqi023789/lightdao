#!/bin/bash
# mig_autopilot.sh — server-side migration autopilot. Runs every 15 min via cron.
# Checks: snapshot availability -> state-sync readiness -> alerts on stalls.
# NEVER makes chain-state changes; only monitors and alerts (execution stays with agent).
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
LOG=/home/ubuntu/mig_autopilot.log
NOW=$(date -u +%FT%TZ)

TIP=$(curl -s -m 8 http://127.0.0.1:26657/status | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["sync_info"]["latest_block_height"])' 2>/dev/null)
SNAPS=$(ls /home/ubuntu/.wasmd/data/snapshots/ 2>/dev/null | grep -v metadata | wc -l)
SNAPSTATE=$(journalctl -u lightd --since '30 min ago' --no-pager 2>/dev/null | grep -ciE 'snapshot (created|sync)' )

# LD-AUTOPILOT-HTTPPROBE-20261015 原 ssh 探测因缺 id_ucloud 恒失败（静默失灵），改 HTTP RPC；覆盖 7 台新机
NEWMACH=""
LAGBAD=""
# 节点清单在 root-only 文件里（公开仓库不含地址）；空清单必须大声失败，
# 绝不允许"清单读不到"再次伪装成正常运行（今天已经栽过一次）。
NODE_IPS=$(cat /etc/lightdao/node_ips.txt 2>/dev/null | tr -d "\r" | grep -Eo "[0-9]{1,3}(\.[0-9]{1,3}){3}" | tr "\n" " ")
if [ -z "$(echo $NODE_IPS)" ]; then
  echo "$NOW CFG-FAIL 节点清单为空/不可读(/etc/lightdao/node_ips.txt) —— 探测未执行" >> $LOG
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "[autopilot] 节点探测配置失效：清单为空" >/dev/null 2>&1 || true
  exit 1
fi
for ip in $NODE_IPS; do
  read -r h catch <<<"$(curl -s -m 8 "http://$ip:26657/status" | python3 -c 'import json,sys; d=json.load(sys.stdin)["result"]["sync_info"]; print(d["latest_block_height"], "catching" if d.get("catching_up") else "")' 2>/dev/null)"
  if [ -z "$h" ]; then
    NEWMACH="$NEWMACH $ip:DOWN"; LAGBAD="$LAGBAD $ip(无响应)"; continue
  fi
  if [ -n "$catch" ]; then
    NEWMACH="$NEWMACH $ip:catching"; LAGBAD="$LAGBAD $ip(仍在追块)"; continue
  fi
  NEWMACH="$NEWMACH $ip:$h"
  if [ -n "$TIP" ]; then
    d=$(( TIP - h ))
    if [ "$d" -gt 60 ]; then LAGBAD="$LAGBAD $ip(落后${d}块)"; fi
    if [ "$d" -lt -5 ]; then LAGBAD="$LAGBAD $ip(超前${d}块)"; fi
  fi
done

echo "$NOW tip=$TIP snapshots=$SNAPS snaplog=$SNAPSTATE new:$NEWMACH bad:${LAGBAD:-none}" >> $LOG

# alert if mainnet tip is stale (no new block in 5 min = chain halt!)
TIPAGE=$(curl -s -m 8 http://127.0.0.1:26657/status | python3 -c 'import json,sys; import time; d=json.load(sys.stdin)["result"]["sync_info"]; print(int(time.time()) - int(d["latest_block_time"][:10]))' 2>/dev/null)
if [ -n "$TIPAGE" ] && [ "$TIPAGE" -gt 300 ]; then
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "[autopilot] MAINNET TIP STALE ${TIPAGE}s - investigate!" >/dev/null 2>&1
  echo "$NOW ALERT mainnet-stale-${TIPAGE}s" >> $LOG
fi

if [ -n "$LAGBAD" ]; then
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "[autopilot] 节点同步异常:$LAGBAD" >/dev/null 2>&1
  echo "$NOW ALERT node-sync-bad$LAGBAD" >> $LOG
fi

# alert if snapshots not appearing after 1h of service
if [ "$SNAPS" -eq 0 ] && [ "$SNAPSTATE" -eq 0 ]; then
  echo "$NOW note: no snapshots yet" >> $LOG
fi
