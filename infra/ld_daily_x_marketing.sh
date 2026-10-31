#!/bin/bash
# ld_daily_x_marketing.sh — X 营销日更:与 TG/Discord 共用统一内容源 daily_unified.json 与同一海报(am/pm 两班)。
# 用法: ld_daily_x_marketing.sh [am|pm]  默认 am。仅按 280 加权字数限制裁去页眉(📢…Daily N/10)与页脚(——————— 之后)。
# DRY_RUN=1 只打印不发帖;发帖前经加权长度门禁,超限自动回退为不带链接版。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
SRC=/home/ubuntu/repo/infra/marketing/daily_unified.json
[ -f "$SRC" ] || { echo "missing $SRC"; exit 2; }
SLOT="${1:-am}"
BASE=$((${X_SLOT_IDX:-$(date -u +%j) % 10}))   # LD-X-FIT 可用 X_SLOT_IDX 逐条演练；生产不设即按日期轮换
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
# LD-X-FIT-20261031 组装顺序：正文 → 必带锚点 → 放得下才加社交页脚。
# （旧顺序先塞页脚、超长再回退，等于让装饰挤掉了"可核验"这件事。）
# LD-X-COMPOSE-20261031 组装规则集中在 x_compose.py（可单测）：
# 正文 → 必带锚点（域名就地升级不重复追加 + 真实区块高度）→ 放得下才加社交页脚；
# 取不到高度或"正文+锚点"仍超 280 → 不发帖（宁可不发，也不写假数字、也不自动截句）。
H=$(wasmd status --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);si=(d.get('sync_info') or d.get('SyncInfo') or {});print(si.get('latest_block_height',''))" 2>/dev/null)
T2=$(printf '%s' "$T" | python3 /usr/local/bin/x_compose.py "$H")
if [ $? -ne 0 ]; then
  echo "$(date -u +%FT%TZ) X-FIT-BLOCK 文案无法在 280 加权字符内安放事实锚点，已阻止发帖（需人改文案）" >> /home/ubuntu/ld_alerts.log
  echo "X-FIT 拦截：不发帖"; exit 3
fi
W=$(printf '%s' "$T2" | python3 -c "import sys;t=sys.stdin.read();print(sum(2 if ord(c)>0x2E7F else 1 for c in t))")
if [ "$W" -gt 280 ]; then
  echo "$(date -u +%FT%TZ) X-FIT-BLOCK 装配后加权长度 $W 超 280，已阻止发帖（不自动截句）" >> /home/ubuntu/ld_alerts.log
  echo "X-FIT 拦截：加权 $W > 280，不发帖"; exit 3
fi
python3 -c "import json,sys;json.dump([{'text':sys.argv[1],'media':sys.argv[2]}],open('/home/ubuntu/x_mkt_thread.json','w'))" "$T2" "$POSTER" || { echo "json write failed"; exit 2; }
set -a; source /etc/lightdao/x_api.env; set +a
python3 /usr/local/bin/ld_x_compliance.py /home/ubuntu/x_mkt_thread.json
if [ $? -ne 0 ]; then
  echo "$(date -u +%FT%TZ) X-COMPLIANCE-BLOCK 文案未过内容门禁，已阻止发帖：$(python3 /usr/local/bin/ld_x_compliance.py /home/ubuntu/x_mkt_thread.json 2>&1 | tail -2 | tr '\n' ' ' | cut -c1-200)" >> /home/ubuntu/ld_alerts.log
  echo "X-COMPLIANCE 拦截：不发帖"; exit 3
fi
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T2"; echo "DRY media: ${POSTER:-none}"; echo "DRY：内容门禁已通过，未发帖"; exit 0; fi
POSTER_BIN="${LD_X_POSTER:-/home/ubuntu/post_tweet_media.py}"   # 可注入：默认是真发帖器
"$POSTER_BIN" /home/ubuntu/x_mkt_thread.json
rc=$?
if [ $rc -ne 0 ]; then
  echo "$(date -u +%FT%TZ) X-POST-FAIL rc=$rc slot=$SLOT n=$N 文案已过门禁但发帖失败（凭据失效/额度/网络），待发帖内容在 /home/ubuntu/x_mkt_thread.json（可直接重试）。详见 /home/ubuntu/ld_x_mkt.log" >> /home/ubuntu/ld_alerts.log
  echo "X-POST-FAIL rc=$rc（已写告警）"; exit 4
fi
