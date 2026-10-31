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
# LD-X-GATE-20261031 原来这一行在合规检查之前就 return，门禁永远不会被演练到
T2="$T

📡 Telegram: t.me/lightdao_news · Discord: discord.gg/9YY9X2Cdv"
python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER" || { echo "json write failed"; exit 2; }
set -a; source /etc/lightdao/x_api.env; set +a
python3 -c "import sys;t=sys.argv[1];w=sum(2 if ord(c)>0x2E7F else 1 for c in t);sys.exit(0 if w<=280 else 2)" "$T2" || { echo "tweet with links too long, posting bare"; T2="$T"; python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER"; }
# LD-X-ANCHOR-20261031 补齐事实锚点（链上高度 + 官网），而不是放宽门禁：
# 取不到高度就不补——写 "height 0" 是编造事实，宁可被门禁拦住报警。
H=$(wasmd status --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);si=(d.get('sync_info') or d.get('SyncInfo') or d.get('Result',{}).get('SyncInfo') or {});print(si.get('latest_block_height',''))" 2>/dev/null)
case "$T2" in *"https://lightdao.net"*) A_LINK="" ;; *) A_LINK="
https://lightdao.net" ;; esac
if [ -n "$H" ]; then
  case "$T2" in *"height "*) A_H="" ;; *) A_H="
LightDAO height $H" ;; esac
else
  A_H=""
  echo "WARN 取不到区块高度，锚点未补齐（预计会被门禁拦下）"
fi
T2="$T2$A_H$A_LINK"
python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER" || { echo "json rewrite failed"; exit 2; }
python3 /usr/local/bin/ld_x_compliance.py /home/ubuntu/x_mkt_thread.json
if [ $? -ne 0 ]; then
  echo "$(date -u +%FT%TZ) X-COMPLIANCE-BLOCK 文案未过内容门禁，已阻止发帖：$(python3 /usr/local/bin/ld_x_compliance.py /home/ubuntu/x_mkt_thread.json 2>&1 | tail -2 | tr '\n' ' ' | cut -c1-200)" >> /home/ubuntu/ld_alerts.log
  echo "X-COMPLIANCE 拦截：不发帖"; exit 3
fi
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T2"; echo "DRY media: ${POSTER:-none}"; echo "DRY：内容门禁已通过，未发帖"; exit 0; fi
python3 /home/ubuntu/post_tweet_media.py /home/ubuntu/x_mkt_thread.json
