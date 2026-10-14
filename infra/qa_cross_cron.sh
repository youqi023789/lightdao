#!/bin/bash
/usr/bin/python3 /usr/local/bin/qa_cross.py >> /home/ubuntu/ld_cross.log 2>&1
if [ $? -ne 0 ]; then
  echo "$(date -u +%FT%TZ) CROSS-FAIL" >> /home/ubuntu/ld_alerts.log
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "⚠️ CROSS-LAYER GATE FAIL (see ld_cross.log)" >/dev/null 2>&1
fi
