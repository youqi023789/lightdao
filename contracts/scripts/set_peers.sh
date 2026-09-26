#!/usr/bin/env bash
# set_peers.sh — configure p2p in config.toml. Run on every node before start.
#  - SENTRY/RPC nodes: PERSISTENT_PEERS = all validators + other sentries; expose RPC.
#  - VALIDATOR nodes: PERSISTENT_PEERS = ONLY its own sentries; PRIVATE_PEER_IDS = other validators;
#    external_address set; addr_book_strict; do NOT expose RPC.
set -euo pipefail
HOME_DIR=${HOME_DIR:-/home/lightdao/.wasmd}
ROLE=${ROLE:?set ROLE=validator|sentry}
PERSISTENT_PEERS=${PERSISTENT_PEERS:-}      # comma list nodeid@ip:26656
SEEDS=${SEEDS:-}
EXTERNAL_ADDR=${EXTERNAL_ADDR:-}            # validator/sentry public ip:26656
PRIVATE_PEER_IDS=${PRIVATE_PEER_IDS:-}      # validators hide each other behind sentries
CFG="$HOME_DIR/config/config.toml"

set_kv(){ sed -i "s|^$1 = .*$1 = $2|" "$CFG" 2>/dev/null || true; }
# use a robust in-place edit
py() { python3 - "$CFG" "$1" "$2" <<'PY'
import re,sys
f,k,v=sys.argv[1],sys.argv[2],sys.argv[3]
s=open(f).read()
s=re.sub(r'(?m)^(\s*'+re.escape(k)+r'\s*=\s*).*$','\\1'+v,s)
open(f,'w').write(s)
PY
}

case "$ROLE" in
  sentry)
    py persistent_peers "\"$PERSISTENT_PEERS\""
    [ -n "$SEEDS" ] && py seeds "\"$SEEDS\""
    [ -n "$EXTERNAL_ADDR" ] && py external_address "\"$EXTERNAL_ADDR\""
    py addr_book_strict "false"
    ;;
  validator)
    py persistent_peers "\"$PERSISTENT_PEERS\""     # only its sentries
    [ -n "$PRIVATE_PEER_IDS" ] && py private_peer_ids "\"$PRIVATE_PEER_IDS\""
    [ -n "$EXTERNAL_ADDR" ] && py external_address "\"$EXTERNAL_ADDR\""
    py addr_book_strict "true"
    # keep RPC local on validators
    py laddr "\"tcp://127.0.0.1:26657\""
    ;;
  *) echo "ROLE must be validator|sentry"; exit 1;;
esac
echo "peers configured for role=$ROLE in $CFG"
echo "start with: sudo systemctl start lightd   (after genesis_time)"
