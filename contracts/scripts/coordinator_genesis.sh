#!/usr/bin/env bash
# coordinator_genesis.sh — run on ONE coordinator machine.
# Builds the mainnet genesis: params + denom + allocations, distributes a common genesis to the
# 7 validators (they each run make_gentx.sh), then collect-gentxs -> final genesis.json.
#
# Inputs (edit before running):
#   validators.txt : moniker|peer(nodeid@ip:port)|consensus_pubkey_json|operator_addr|self_delegation
#   allocations.txt: address|amount   (treasury/team/ecosystem/faucet pre-funded accounts)
# Env: CHAIN_ID DENOM SELF_DELIG default params, WASMD, HOME_DIR, KB, GENESIS_TIME
set -euo pipefail
CHAIN_ID=${CHAIN_ID:-lightdao-mainnet-1}
DENOM=${DENOM:-uldg}                 # NATIVE staking+gas denom (micro). NOTE: LIGHT is a CW20, separate. See ORCHESTRATION doc.
HOME_DIR=${HOME_DIR:-/home/lightdao/.wasmd}
KB=${KB:-file}
WASMD=${WASMD:-wasmd}
GENESIS_TIME=${GENESIS_TIME:-}         # e.g. 2026-10-01T13:00:00Z ; empty = now+ (set explicitly for mainnet)
MAX_VALIDATORS=${MAX_VALIDATORS:-100}
UNBONDING=${UNBONDING:-1800s}          # 21d? keep short for testnet; mainnet typically 1209600s (14d)
VALIDATORS_FILE=${VALIDATORS_FILE:-validators.txt}
ALLOC_FILE=${ALLOC_FILE:-allocations.txt}
OUT=${OUT:-./genesis_out}
mkdir -p "$OUT"

[ -f "$VALIDATORS_FILE" ] || { echo "need $VALIDATORS_FILE (moniker|peer|pubkey|operator|selfdel)"; exit 1; }

echo "== [1/6] base genesis =="
rm -rf "$HOME_DIR"/config/genesis.json 2>/dev/null || true
$WASMD init coordinator --chain-id "$CHAIN_ID" --home "$HOME_DIR" >/dev/null 2>&1 || true
G="$HOME_DIR/config/genesis.json"

echo "== [2/6] chain params (denom=$DENOM, max_val=$MAX_VALIDATORS, unbonding=$UNBONDING) =="
TMP=$(mktemp)
jq --arg d "$DENOM" --arg mv "$MAX_VALIDATORS" --arg ub "$UNBONDING" '
  .chain_id = env.CID
  | .app_state.staking.params.bond_denom = $d
  | .app_state.staking.params.max_validators = ($mv|tonumber)
  | .app_state.staking.params.unbonding_time = $ub
  | .app_state.gov.params.min_deposit = [{"denom":$d,"amount":"10000000"}]
  | .app_state.wasm.params.code_upload_access = {"permission":"Everybody"}
  | .app_state.wasm.params.instantiate_default_permission = "Everybody"
' "$G" > "$TMP" 2>/dev/null || cp "$G" "$TMP"
# CID env for jq
CID="$CHAIN_ID" jq --arg d "$DENOM" --arg mv "$MAX_VALIDATORS" --arg ub "$UNBONDING" '
  .chain_id = env.CID
  | .app_state.staking.params.bond_denom = $d
  | .app_state.staking.params.max_validators = ($mv|tonumber)
  | .app_state.staking.params.unbonding_time = $ub
  | .app_state.wasm.params.code_upload_access = {"permission":"Everybody"}
  | .app_state.wasm.params.instantiate_default_permission = "Everybody"
' "$G" > "$TMP" && mv "$TMP" "$G"

if [ -n "$GENESIS_TIME" ]; then
  TMP=$(mktemp); jq --arg t "$GENESIS_TIME" '.genesis_time=$t' "$G" > "$TMP" && mv "$TMP" "$G"
fi

echo "== [3/6] fund allocations (treasury/team/ecosystem/faucet) =="
if [ -f "$ALLOC_FILE" ]; then
  while IFS='|' read -r addr amt; do
    [ -z "$addr" ] && continue
    $WASMD genesis add-genesis-account "$addr" "${amt}${DENOM}" --home "$HOME_DIR"
    echo "  funded $addr ${amt}${DENOM}"
  done < "$ALLOC_FILE"
fi

echo "== [4/6] fund validator operator accounts (self-delegation source) =="
while IFS='|' read -r moniker peer pubkey operator selfdel; do
  [ -z "$moniker" ] && continue
  $WASMD genesis add-genesis-account "$operator" "${selfdel}${DENOM}" --home "$HOME_DIR"
  echo "  funded operator $operator ($moniker) ${selfdel}${DENOM}"
done < "$VALIDATORS_FILE"

echo "== [5/6] publish common genesis for validators =="
cp "$G" "$OUT/genesis_common.json"
echo "  -> $OUT/genesis_common.json  (send this to all 7 validators; they run make_gentx.sh)"
echo "  validators place $G, then run: CHAIN_ID=$CHAIN_ID DENOM=$DENOM SELF_DELIG=<their selfdel> bash make_gentx.sh"

echo "== [6/6] after you collect all 7 gentx-*.json into $OUT/gentx/ , run:"
echo "  mkdir -p $HOME_DIR/config/gentx && cp $OUT/gentx/*.json $HOME_DIR/config/gentx/"
echo "  $WASMD genesis collect-gentxs --home $HOME_DIR"
echo "  $WASMD genesis validate --home $HOME_DIR"
echo "  cp $HOME_DIR/config/genesis.json $OUT/genesis_final.json   # distribute THIS to all nodes"
echo "DONE (stage 1). Final genesis is produced after collect-gentxs."
