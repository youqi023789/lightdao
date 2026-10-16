#!/bin/bash
# ld_daily_telegram.sh — 每日 Telegram 频道日更(营销轮换+带图),与 X/Discord 同步同内容。
# 内容源 /home/ubuntu/marketing/discord_daily.json(与 Discord 共用10条轮换);
# DRY_RUN=1 只打印不发帖。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/marketing/discord_daily.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
IDX=$(( $(date -u +%j) % 10 ))
N=$((IDX+1))
T=$(python3 -c "import json;print(json.load(open('$SRC'))[$IDX])")
echo "[$(date -u +%FT%TZ)] day-index=$IDX posting Telegram $N/10"
POSTER="/home/ubuntu/marketing/posters/poster_$N.jpg"
[ -f "$POSTER" ] || POSTER=""
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T"; echo "DRY media: ${POSTER:-none}"; exit 0; fi
STATS=$(curl -s -m 10 http://127.0.0.1:26657/status | grep -oE '"latest_block_height":"[0-9]+"' | grep -oE '[0-9]+' | head -1)
MINERS=$(curl -s -m 10 "http://127.0.0.1:8080/v1/scores?day=$(curl -s -m 10 http://127.0.0.1:8080/v1/health | grep -oE '"current_day": [0-9]+' | grep -oE '[0-9]+')" | python3 -c 'import json,sys;print(len(json.load(sys.stdin).get("scores",{})))' 2>/dev/null || echo '?')
BURN=$(wasmd q bank balances wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c 'import json,sys;b=json.load(sys.stdin).get("balances");print(f"{int(b[0]["amount"])/1e6:,.0f}" if b else "?")' 2>/dev/null || echo '?')
LINE="📊 今日链上: 区块 $STATS"
[ "${MINERS:-0}" -ge 50 ] 2>/dev/null && LINE="$LINE · 活跃矿工 $MINERS"
[ "${BURN:-0}" -ge 100000 ] 2>/dev/null && LINE="$LINE · 已销毁 ${BURN} LIGHT"
TEXT="$LINE

$T

🌐 https://lightdao.net | Chat: https://discord.gg/9YY9X2Cdv"
if [ -n "$POSTER" ]; then
  python3 /usr/local/bin/tg_post.py "$TEXT" "$POSTER"
else
  python3 /usr/local/bin/tg_post.py "$TEXT"
fi
