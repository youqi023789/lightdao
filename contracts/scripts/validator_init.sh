#!/usr/bin/env bash
# validator_init.sh — run on EACH of the 7 validators (after node_bootstrap.sh).
# Creates the node identity (consensus key + p2p key), an operator key, and prints the
# three things the coordinator needs: NODE_ID@IP:26656, CONSENSUS_PUBKEY(json), OPERATOR_ADDR.
#
# SECURITY: for real mainnet, generate the OPERATOR key on an OFFLINE/air-gapped machine and
# import via `wasmd keys add operator --recover` (seed phrase) or use a ledger/HSM. This script
# uses keyring-backend=file with a passphrase prompt as a reasonable default; test backend only for dev.
set -euo pipefail
MONIKER=${MONIKER:?set MONIKER=val01..val07}
CHAIN_ID=${CHAIN_ID:-lightdao-mainnet-1}
HOME_DIR=${HOME_DIR:-/home/lightdao/.wasmd}
KB=${KB:-file}                 # keyring-backend: file (mainnet) | test (dev only)
PUB_IP=${PUB_IP:?set PUB_IP=<this node public ip>}
P2P_PORT=${P2P_PORT:-26656}

sudo -u lightdao wasmd init "$MONIKER" --chain-id "$CHAIN_ID" --home "$HOME_DIR" >/dev/null 2>&1 || \
  wasmd init "$MONIKER" --chain-id "$CHAIN_ID" --home "$HOME_DIR"

# operator key (self-delegation / rewards). Use --recover on an offline-generated seed for mainnet.
if ! wasmd keys show operator --home "$HOME_DIR" --keyring-backend "$KB" >/dev/null 2>&1; then
  echo ">> create/import operator key (keyring-backend=$KB). For mainnet prefer: wasmd keys add operator --recover"
  wasmd keys add operator --home "$HOME_DIR" --keyring-backend "$KB"
fi

NODE_ID=$(wasmd comet show-node-id --home "$HOME_DIR")
PUBKEY=$(wasmd comet show-validator --home "$HOME_DIR")
OPERATOR=$(wasmd keys show operator -a --home "$HOME_DIR" --keyring-backend "$KB")

echo "=============================================================="
echo "SEND THESE 3 TO THE COORDINATOR (securely, e.g. encrypted msg):"
echo "  moniker         = $MONIKER"
echo "  peer            = ${NODE_ID}@${PUB_IP}:${P2P_PORT}"
echo "  consensus_pubkey= $PUBKEY"
echo "  operator_addr   = $OPERATOR"
echo "=============================================================="
# also dump to a file for easy copy
cat > "$HOME_DIR/validator_submission_${MONIKER}.txt" <<EOT
moniker=$MONIKER
peer=${NODE_ID}@${PUB_IP}:${P2P_PORT}
consensus_pubkey=$PUBKEY
operator_addr=$OPERATOR
EOT
echo "saved -> $HOME_DIR/validator_submission_${MONIKER}.txt"
echo "BACK UP NOW: $HOME_DIR/config/priv_validator_key.json (consensus) and operator seed. Offline copies."
