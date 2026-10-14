#!/bin/bash
# ld_daily_discord.sh — 每日Discord日更(营销轮换+带图)。DRY_RUN=1 只打印不发帖。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/marketing/discord_daily.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
IDX=$(( $(date -u +%j) % 10 ))
N=$((IDX+1))
MSG=$(python3 -c "import json;print(json.load(open('$SRC'))[$IDX])")
POSTER="/home/ubuntu/marketing/posters/poster_$N.jpg"
[ -f "$POSTER" ] || POSTER=""
python3 -c "import sys;t=sys.argv[1];sys.exit(0 if 0<len(t)<=2000 else 2)" "$MSG" || { echo 'message length invalid'; exit 2; }
echo "[$(date -u +%FT%TZ)] day-index=$IDX posting Discord $N/10 media=${POSTER:-none}"
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $MSG"; exit 0; fi
if [ -n "$POSTER" ]; then
  python3 /home/ubuntu/post_discord_media.py "$MSG" "$POSTER"
else
  printf '%s' "$MSG" | python3 /usr/local/bin/discord_bot.py send
fi
