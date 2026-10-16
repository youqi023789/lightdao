#!/bin/bash
# LightDAO daily root signer v5 — N-of-M multi-voter (per-voter keyring dirs), commit-confirmed, 7-day catch-up.
#
# Why v5 (2026-10-13): mining_reward commits a daily root only after >= root_threshold(5) DISTINCT
# authorized validator accounts submit the same commitment. After the validator migration the other
# 6 legacy voter keyrings were still on the retired Tencent hosts, so day 31 stalled at 1/5 votes and
# miners could not claim. The 6 keyrings were recovered to /home/ubuntu/voters/<host>/keyring-test.
# NOTE: cosmos "test" keyring resolves by ADDRESS via <name>.address index files — a key must be
# copied with its whole keyring-test dir and keep its original name, renaming the .info alone breaks
# signing ("pubKey does not match signer address" / "key with address ... not found").
#
# VOTERS format: "<keyring-dir-or-empty>|<keyname>" separated by spaces. Empty dir = this host's
# default --home keyring.
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
H=${LD_WASMD_HOME:-$HOME/.wasmd}; RPC=${LD_RPC:-tcp://localhost:26657}
KB="--keyring-backend test"; CID=lightdao-mainnet-1
MR=wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx
GW=${LD_GW:-http://127.0.0.1:8080}
LOOKBACK=${LD_SIGN_LOOKBACK:-7}
VOTERS=${LD_VOTERS:-"|operator /home/ubuntu/voters/jp|operator /home/ubuntu/voters/kr|operator /home/ubuntu/voters/us|operator /home/ubuntu/voters/hk|operator /home/ubuntu/voters/uk|operator /home/ubuntu/voters/fr|operator"}
CUR=$(/usr/local/bin/ld_day.sh cur)


# 合约日界与网关日界不一致（纪元对齐提案执行前）：提前判断，避免白跑交易与误报
contract_current_day() {
  # mining_reward 没有 config 查询变体，直接读原始状态键 "config"(hex 636f6e666967) 取 genesis_time
  local RAW GT
  RAW=$(wasmd q wasm contract-state raw "$MR" 636f6e666967 --node "$RPC" -o json 2>/dev/null \
        | grep -oE '"(value|data)": *"[A-Za-z0-9+/=]+"' | head -1 | sed -E 's/.*"([A-Za-z0-9+\/]+=*)"$/\1/')
  [ -z "$RAW" ] && { echo ""; return; }
  GT=$(printf '%s' "$RAW" | base64 -d 2>/dev/null | grep -oE '"genesis_time": *[0-9]+' | grep -oE '[0-9]+' | head -1)
  [ -z "$GT" ] && { echo ""; return; }
  echo $(( ( $(date +%s) - GT ) / 86400 ))
}

onchain() {
  wasmd q wasm contract-state smart "$MR" "{\"root_submitted\":{\"day\":$1}}" --node "$RPC" -o json 2>/dev/null \
    | grep -aoE '"data": *(true|false)' | grep -aoE 'true|false' | head -1
}

keyargs() { # $1 = "dir|name" -> prints flags for wasmd
  local dir=${1%%|*} name=${1##*|}
  if [ -n "$dir" ]; then echo "--keyring-dir $dir --keyring-backend test --from $name"
  else echo "--home $H --keyring-backend test --from $name"; fi
}

vote_once() { # $1=day $2=voter-spec $3=root $4=AM $5=TS
  local DAY=$1 V=$2 ROOT=$3 AM=$4 TS=$5
  local KA=$(keyargs "$V")
  local OUT=$(wasmd tx wasm execute "$MR" "{\"submit_daily_root\":{\"day\":$DAY,\"root\":\"$ROOT\",\"active_miners\":\"$AM\",\"total_score\":\"$TS\"}}" \
    $KA --node "$RPC" --chain-id "$CID" --gas 400000 --fees 120000ulight -y -b sync -o json 2>&1)
  local TXH=$(printf '%s' "$OUT" | python3 -c "import sys,json;s=sys.stdin.read()
try: print(json.loads(s[s.find('{'):]).get('txhash',''))
except Exception: print('')" 2>/dev/null)
  local CTX=$(printf '%s' "$OUT" | python3 -c "import sys,json;s=sys.stdin.read()
try:
    d=json.loads(s[s.find('{'):]); print(d.get('code'), str(d.get('raw_log',''))[:110])
except Exception: print('parse-fail', s[:110])" 2>/dev/null)
  [ -z "$TXH" ] && { echo "  [$V] no-txhash ($CTX)"; return 1; }
  case "$CTX" in
    0\ *) : ;;
    *"already voted"*) echo "  [$V] already voted"; return 0 ;;
    *) echo "  [$V] checktx-fail ($CTX)"; return 1 ;;
  esac
  local i dc=""
  for i in $(seq 1 25); do
    sleep 3
    local R=$(wasmd q tx "$TXH" --node "$RPC" -o json 2>/dev/null)
    if [ -n "$R" ]; then
      dc=$(printf '%s' "$R" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('code'), str(d.get('raw_log',''))[:120])" 2>/dev/null)
      break
    fi
  done
  [ -z "$dc" ] && { echo "  [$V] LOST tx $TXH (not committed in 75s)"; return 1; }
  case "$dc" in
    0\ *) echo "  [$V] voted tx=$TXH"; return 0 ;;
    *"already voted"*) echo "  [$V] already voted"; return 0 ;;
    *) echo "  [$V] deliver-fail ($dc) tx=$TXH"; return 1 ;;
  esac
}

sign_day() {
  local DAY=$1
  [ "$(onchain $DAY)" = "true" ] && { echo "day $DAY committed (threshold reached)"; return 0; }
  local CCD=$(contract_current_day)
  if [ -n "$CCD" ] && [ "$DAY" -ge "$CCD" ]; then echo "day $DAY not complete on-chain yet (contract day=$CCD, boundary 04:48Z) - skip, no wasted tx"; return 0; fi
  local INFO=$(curl -s --max-time 20 "$GW/v1/day?day=$DAY")
  local FIN=$(echo "$INFO" | grep -aoE '"finalized": *(true|false)' | grep -aoE 'true|false' | head -1)
  [ "$FIN" = "true" ] || { echo "day $DAY not finalized yet"; return 0; }
  local ROOT=$(echo "$INFO" | grep -aoE '"root": *"[a-f0-9]+"' | grep -aoE '[a-f0-9]{64}' | head -1)
  local AM=$(echo "$INFO"  | grep -aoE '"active_miners": *[0-9]+' | grep -aoE '[0-9]+' | head -1)
  local TS=$(echo "$INFO"  | grep -aoE '"total_score": *[0-9]+'  | grep -aoE '[0-9]+'  | head -1)
  [ -n "$ROOT" ] || { echo "day $DAY no root"; return 0; }
  echo "day $DAY needs votes (root=${ROOT:0:12}.. miners=$AM score=$TS)"
  local v
  for v in $VOTERS; do
    [ "$(onchain $DAY)" = "true" ] && { echo "day $DAY COMMITTED ✓"; return 0; }
    vote_once "$DAY" "$v" "$ROOT" "$AM" "$TS"
  done
  if [ "$(onchain $DAY)" = "true" ]; then echo "day $DAY COMMITTED ✓"; return 0
  else echo "day $DAY STILL NOT COMMITTED (voters exhausted)"; return 1; fi
}

rc=0
for ((d=CUR-1; d>=CUR-LOOKBACK; d--)); do
  [ "$d" -lt 1 ] && break
  sign_day "$d" || rc=1
done
exit $rc
