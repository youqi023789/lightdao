#!/bin/bash
# ld_vesting_watch.sh — S17 检测点: deployer 75M cliff-0 claimed 监控
# 每小时查 vesting.schedule(deployer).claimed; >0 即 Discord 告警。
V=wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x
DEPLOYER=wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj
NODE="--node tcp://127.0.0.1:26657 -o json"
CLAIMED=$(wasmd q wasm contract-state smart $V "{\"schedule\":{\"address\":\"$DEPLOYER\"}}" $NODE 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get(\"data\",{}).get(\"claimed\",\"0\"))" 2>/dev/null)
if [ -z "$CLAIMED" ]; then
  echo "$(date -u +%FT%TZ) QUERY-FAIL vesting.schedule(deployer)" >> /home/ubuntu/ld_vesting_watch.log
  exit 0
fi
if [ "$CLAIMED" != "0" ]; then
  MSG="🚨 S17 VESTING ALERT: deployer claimed=$CLAIMED (was 0). 75M LIGHT may be draining. Check immediately."
  echo "$(date -u +%FT%TZ) ALERT claimed=$CLAIMED" >> /home/ubuntu/ld_vesting_watch.log
  python3 /usr/local/bin/discord_bot.py send "$MSG" >/dev/null 2>&1
else
  echo "$(date -u +%FT%TZ) OK claimed=0" >> /home/ubuntu/ld_vesting_watch.log
fi
