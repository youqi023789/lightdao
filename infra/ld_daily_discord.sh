#!/bin/bash
# ld_daily_discord.sh — Discord 日更(统一内容源+带图,支持 am/pm 两班)。DRY_RUN=1 只打印不发帖。
# 用法: ld_daily_discord.sh [am|pm]   默认 am。三平台共用 /home/ubuntu/marketing/daily_unified.json 与同一海报。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/repo/infra/marketing/daily_unified.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
SLOT="${1:-am}"
BASE=$(( $(date -u +%j) % 10 ))
if [ "$SLOT" = "pm" ]; then IDX=$(( (BASE+5) % 10 )); else IDX=$BASE; fi
N=$((IDX+1))
MSG=$(python3 -c "import json;print(json.load(open('$SRC'))[$IDX])")
POSTER="/home/ubuntu/marketing/posters/poster_$N.jpg"
[ -f "$POSTER" ] || POSTER=""
python3 -c "import sys;t=sys.argv[1];sys.exit(0 if 0<len(t)<=2000 else 2)" "$MSG" || { echo 'message length invalid'; exit 2; }
echo "[$(date -u +%FT%TZ)] slot=$SLOT day-index=$IDX posting Discord $N/10 media=${POSTER:-none}"
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $MSG"; exit 0; fi
if [ -n "$POSTER" ]; then
  python3 /home/ubuntu/post_discord_media.py "$MSG" "$POSTER"
else
  printf '%s' "$MSG" | python3 /usr/local/bin/discord_bot.py send
fi
