#!/bin/bash
UPGRADE_NAME="v3-lightfee"
NEW_BIN="/home/ubuntu/lightd.new"
TARGET="/usr/local/bin/wasmd"
DONE_FLAG="/etc/lightdao/.upgrade-${UPGRADE_NAME}-done"
UNIT="lightd.service"
while true; do
  sleep 8
  [ -f "$DONE_FLAG" ] && continue
  if journalctl -u "$UNIT" --since "60 seconds ago" --no-pager 2>/dev/null | grep -qE "UPGRADE.*${UPGRADE_NAME}.*NEEDED"; then
    if [ -f "$NEW_BIN" ]; then
      cp -f "$TARGET" "${TARGET}.v1.bak.$(date +%s)" 2>/dev/null || true
      cp -f "$NEW_BIN" "$TARGET"
      chmod +x "$TARGET"
      touch "$DONE_FLAG"
      systemctl restart "$UNIT"
      logger -t lightd-upgrader "SWAPPED to lightd for $UPGRADE_NAME at $(date -u)"
    fi
  fi
done
