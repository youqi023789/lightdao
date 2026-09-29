#!/bin/bash
# ld_daily_x.sh — 每日X日更: 取数+发帖一条命令。DRY_RUN=1 只生成不发帖。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
H=$(curl -s http://127.0.0.1:26657/status | python3 -c "import sys,json;print(json.load(sys.stdin)['result']['sync_info']['latest_block_height'])")
DAY=$(curl -s http://127.0.0.1:8080/v1/health | python3 -c "import sys,json;print(json.load(sys.stdin)['current_day'])")
MIN=$(curl -s "http://127.0.0.1:8080/v1/scores?day=$DAY" | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('scores',{})))")
BURN=$(wasmd q bank balances wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;b=json.load(sys.stdin).get('balances');print(round(int(b[0]['amount'])/1e6,1) if b else 0)")
T="LightDAO Daily $(date -u +%Y-%m-%d) - height $H | $MIN miners today | season day $DAY | $BURN LIGHT burned. Browser as node: contribute bandwidth & compute, settle daily, verifiable on-chain. https://lightdao.net"
python3 -c "import json,sys;t=sys.argv[1];json.dump([t],open('/home/ubuntu/daily.json','w'));w=sum(2 if ord(c)>0x2E7F else 1 for c in t);print('weighted',w);sys.exit(0 if w<=280 else 2)" "$T" || { echo "tweet too long"; exit 2; }
if [ "$DRY_RUN" = "1" ]; then echo "DRY: $T"; exit 0; fi
set -a; source /etc/lightdao/x_api.env; set +a
python3 /home/ubuntu/post_tweet.py /home/ubuntu/daily.json
