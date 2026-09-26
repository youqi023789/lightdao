#!/usr/bin/env bash
# make_gentx.sh — run on EACH validator AFTER placing the coordinator's genesis_common.json
# into $HOME_DIR/config/genesis.json. Produces gentx-<moniker>.json to send back to coordinator.
set -euo pipefail
MONIKER=${MONIKER:?set MONIKER=val01..val07}
CHAIN_ID=${CHAIN_ID:-lightdao-mainnet-1}
DENOM=${DENOM:-uldg}
HOME_DIR=${HOME_DIR:-/home/lightdao/.wasmd}
KB=${KB:-file}
WASMD=${WASMD:-wasmd}
SELF_DELIG=${SELF_DELIG:?set SELF_DELIG=<self-delegation amount in $DENOM, e.g. 1000000000>}
PUB_IP=${PUB_IP:?set PUB_IP=<this node public ip>}
OUT=${OUT:-./genesis_out}; mkdir -p "$OUT"

NODE_ID=$($WASMD comet show-node-id --home "$HOME_DIR")
PUBKEY=$($WASMD comet show-validator --home "$HOME_DIR")

$WASMD genesis gentx operator "${SELF_DELIG}${DENOM}" \
  --chain-id "$CHAIN_ID" \
  --node-id "$NODE_ID" \
  --pubkey "$PUBKEY" \
  --moniker "$MONIKER" \
  --details "LightDAO validator $MONIKER" \
  --commission-rate 0.05 --commission-max-rate 0.20 --commission-max-change-rate 0.01 \
  --min-self-delegation "$SELF_DELIG" \
  --ip "$PUB_IP" --home "$HOME_DIR" --keyring-backend "$KB" -y

GENTX=$(ls -t "$HOME_DIR"/config/gentx/gentx-*.json | head -1)
cp "$GENTX" "$OUT/gentx-${MONIKER}.json"
echo ">> send $OUT/gentx-${MONIKER}.json back to the coordinator"
