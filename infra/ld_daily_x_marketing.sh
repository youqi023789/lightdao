#!/bin/bash
# ld_daily_x_marketing.sh — 每日X营销轮换:10条文案按天轮发(1条/天,10天一循环)。
# 内容源 /home/ubuntu/marketing/x_thread.json;DRY_RUN=1 只打印不发帖。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/marketing/x_thread.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
IDX=$(( $(date -u +%j) % 10 ))
N=$((IDX+1))
T=$(python3 -c "import json;print(json.load(open('$SRC'))[$IDX])")
python3 -c "import sys;t=sys.argv[1];w=sum(2 if ord(c)>0x2E7F else 1 for c in t);print('weighted',w);sys.exit(0 if w<=280 else 2)" "$T" || { echo "tweet $IDX too long, abort"; exit 2; }
echo "[$(date -u +%FT%TZ)] day-index=$IDX posting X $((IDX+1))/10"
POSTER="/home/ubuntu/marketing/posters/poster_$N.jpg"
[ -f "$POSTER" ] || POSTER=""
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T"; echo "DRY media: ${POSTER:-none}"; exit 0; fi
T2="$T

📡 Telegram: t.me/lightdao_news · Discord: discord.gg/9YY9X2Cdv"
python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER" || { echo "json write failed"; exit 2; }
set -a; source /etc/lightdao/x_api.env; set +a
python3 -c "import sys;t=sys.argv[1];w=sum(2 if ord(c)>0x2E7F else 1 for c in t);sys.exit(0 if w<=280 else 2)" "$T2" || { echo "tweet with links too long, posting bare"; T2="$T"; python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER"; }
python3 /home/ubuntu/post_tweet_media.py /home/ubuntu/x_mkt_thread.json
