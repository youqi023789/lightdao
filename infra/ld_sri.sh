#!/bin/bash
# ld_sri.sh — SRI verify + Discord alert on failure (N1, 2026-10 monthly audit).
# Replaces the bare `sri_verify.py >> ld_sri.log` cron line, which failed silently: the daily
# verify could go RED and nobody was notified (detection without alert). Now a failure appends to
# ld_alerts.log AND pushes Discord. Exit code is preserved so promote/CI can gate on it.
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
LOG=/home/ubuntu/ld_sri.log
if /usr/bin/python3 /home/ubuntu/sri_verify.py >> "$LOG" 2>&1; then
  echo "$(date -u +%FT%TZ) SRI OK" >> "$LOG"
  exit 0
else
  echo "$(date -u +%FT%TZ) SRI-FAIL" >> "$LOG"
  echo "$(date -u +%FT%TZ) SRI-FAIL" >> /home/ubuntu/ld_alerts.log
  DETAIL=$(grep -m1 "SRI VERIFY FAIL" "$LOG" | tail -c 280)
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "🚨 SRI VERIFY FAILED on $(hostname): ${DETAIL}" >/dev/null 2>&1
  exit 1
fi
