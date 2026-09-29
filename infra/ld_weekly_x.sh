#!/bin/bash
# ld_weekly_x.sh — 周更X线程(4-5帖): 取数+生成+发帖。DRY_RUN=1 只生成不发帖。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
H=$(curl -s http://127.0.0.1:26657/status | python3 -c "import sys,json;print(json.load(sys.stdin)['result']['sync_info']['latest_block_height'])")
DAY=$(curl -s http://127.0.0.1:8080/v1/health | python3 -c "import sys,json;print(json.load(sys.stdin)['current_day'])")
MIN=$(curl -s "http://127.0.0.1:8080/v1/scores?day=$DAY" | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('scores',{})))")
BURN=$(wasmd q bank balances wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;b=json.load(sys.stdin).get('balances');print(round(int(b[0]['amount'])/1e6,1) if b else 0)")
TRE=$(wasmd q bank balances wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;b=json.load(sys.stdin).get('balances');print(round(int(b[0]['amount'])/1e6,1) if b else 0)")
VAL=$(wasmd q staking validators --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c "import sys,json;v=json.load(sys.stdin)['validators'];print(sum(1 for x in v if x['status']=='BOND_STATUS_BONDED'), sum(1 for x in v if x['jailed']))")
W=$(python3 -c "import datetime;print(int(datetime.date.today().isocalendar()[1]))")
cat > /home/ubuntu/weekly.json <<JSON
[
 "LightDAO Weekly W$W — chain height $H, $VAL bonded/jailed validators, season day $DAY. Everything below is read straight from mainnet.",
 "Burn: $BURN LIGHT destroyed forever (50% of every fee). Treasury: $TRE LIGHT. Supply only shrinks — hard cap 2.5B, on-chain verifiable.",
 "Mining today: $MIN active light-nodes, all in plain browser tabs. No rig, no install: bandwidth + compute + uptime, triple-proven daily.",
 "Settle is daily & on-chain: 5-of-7 validator Merkle roots, public proofs, claim = verify. Contribution verifiable, rewards unfakeable.",
 "Own a seat at the table: mine at https://lightdao.net (founder ref wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v) · read the code https://github.com/youqi023789/lightdao · Discord https://discord.gg/9YY9X2Cdv"
]
JSON
python3 - <<'PY' || exit 2
import json
ts=json.load(open("/home/ubuntu/weekly.json"))
for i,t in enumerate(ts):
    w=sum(2 if ord(c)>0x2E7F else 1 for c in t)
    print(i, w, "OK" if w<=280 else "TOO-LONG")
    if w>280: raise SystemExit(2)
PY
if [ "$DRY_RUN" = "1" ]; then echo "DRY weekly built"; exit 0; fi
set -a; source /etc/lightdao/x_api.env; set +a
python3 /home/ubuntu/post_tweet.py /home/ubuntu/weekly.json
