#!/bin/bash
# ld_daily_x_marketing.sh — X 营销日更:与 TG/Discord 共用统一内容源 daily_unified.json 与同一海报(am/pm 两班)。
# 用法: ld_daily_x_marketing.sh [am|pm]  默认 am。仅按 280 加权字数限制裁去页眉(📢…Daily N/10)与页脚(——————— 之后)。
# DRY_RUN=1 只打印不发帖;发帖前经加权长度门禁,超限自动回退为不带链接版。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/marketing/daily_unified.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
SLOT="${1:-am}"
BASE=$(( $(date -u +%j) % 10 ))
if [ "$SLOT" = "pm" ]; then IDX=$(( (BASE+5) % 10 )); else IDX=$BASE; fi
N=$((IDX+1))
T=$(SRC="$SRC" IDX="$IDX" python3 - <<'PY'
import json,os,re
data=json.load(open(os.environ["SRC"])); s=data[int(os.environ["IDX"])]
s=re.sub(r'^\s*📢.*?Daily \d+/\d+\s*\n+','',s)   # 去掉页眉行
s=re.split(r'\n+\s*—{3,}',s)[0]                    # 去掉"———————"页脚及其后
print(s.strip())
PY
)
python3 -c "import sys;t=sys.argv[1];w=sum(2 if ord(c)>0x2E7F else 1 for c in t);print('weighted',w);sys.exit(0 if w<=280 else 2)" "$T" || { echo "tweet $IDX too long, abort"; exit 2; }
echo "[$(date -u +%FT%TZ)] slot=$SLOT day-index=$IDX posting X $N/10"
POSTER="/home/ubuntu/marketing/posters/poster_$N.jpg"
[ -f "$POSTER" ] || POSTER=""
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T"; echo "DRY media: ${POSTER:-none}"; exit 0; fi
T2="$T

📡 Telegram: t.me/lightdao_news · Discord: discord.gg/9YY9X2Cdv"
python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER" || { echo "json write failed"; exit 2; }
set -a; source /etc/lightdao/x_api.env; set +a
python3 -c "import sys;t=sys.argv[1];w=sum(2 if ord(c)>0x2E7F else 1 for c in t);sys.exit(0 if w<=280 else 2)" "$T2" || { echo "tweet with links too long, posting bare"; T2="$T"; python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER"; }
python3 /home/ubuntu/post_tweet_media.py /home/ubuntu/x_mkt_thread.json
