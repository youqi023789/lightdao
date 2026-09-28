#!/bin/bash
# LightDAO validator daily root signer — cutover-aware day + on-chain dedupe gating.
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
H=$HOME/.wasmd; RPC=tcp://localhost:26657; KB="--keyring-backend test"; CID=lightdao-mainnet-1
MR=wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx
GW=http://43.160.218.196/gw
DAY=$(/usr/local/bin/ld_day.sh prev)
# on-chain gating: skip if this day's root already committed (makes repeat runs safe)
ON=$(wasmd q wasm contract-state smart "$MR" "{\"root_submitted\":{\"day\":$DAY}}" --node "$RPC" -o json 2>/dev/null | grep -aoE '"data": *(true|false)' | grep -aoE 'true|false' | head -1)
[ "$ON" = "true" ] && { echo "day $DAY already on-chain"; exit 0; }
INFO=$(curl -s --max-time 20 "$GW/v1/day?day=$DAY")
FIN=$(echo "$INFO" | grep -aoE '"finalized": *(true|false)' | grep -aoE 'true|false' | head -1)
[ "$FIN" = "true" ] || { echo "day $DAY not finalized yet"; exit 0; }
ROOT=$(echo "$INFO" | grep -aoE '"root": *"[a-f0-9]+"' | grep -aoE '[a-f0-9]{64}' | head -1)
AM=$(echo "$INFO"  | grep -aoE '"active_miners": *[0-9]+' | grep -aoE '[0-9]+' | head -1)
TS=$(echo "$INFO"  | grep -aoE '"total_score": *[0-9]+'  | grep -aoE '[0-9]+' | head -1)
[ -n "$ROOT" ] || { echo "no root"; exit 0; }
wasmd tx wasm execute "$MR" "{\"submit_daily_root\":{\"day\":$DAY,\"root\":\"$ROOT\",\"active_miners\":\"$AM\",\"total_score\":\"$TS\"}}" \
  --from operator --home "$H" --node "$RPC" $KB --chain-id "$CID" --gas 500000 --fees 150000ulight -y -b sync >/dev/null 2>&1
echo "submitted root for day $DAY"
