#!/usr/bin/env bash
# cosmovisor_setup.sh — run on every full node/validator. Sets up cosmovisor dir layout +
# a systemd service so on-chain `software-upgrade` proposals auto-swap the binary and restart.
#
# Layout:  $COSMOVISOR_HOME/genesis/bin/wasmd      (current binary)
#          $COSMOVISOR_HOME/upgrades/<name>/bin/wasmd  (future upgrades, fetched by cosmovisor)
set -euo pipefail
SERVICE_USER=${SERVICE_USER:-lightdao}
HOME_DIR=${HOME_DIR:-/home/$SERVICE_USER/.wasmd}
COSMOVISOR_HOME=${COSMOVISOR_HOME:-/home/$SERVICE_USER/.wasmd/cosmovisor}
WASMD_SRC=${WASMD_SRC:-/usr/local/bin/wasmd}
CHAIN_ID=${CHAIN_ID:-lightdao-mainnet-1}
DAEMON_NAME=wasmd

echo "== create cosmovisor layout =="
sudo -u "$SERVICE_USER" mkdir -p "$COSMOVISOR_HOME/genesis/bin" "$COSMOVISOR_HOME/upgrades"
sudo -u "$SERVICE_USER" cp "$WASMD_SRC" "$COSMOVISOR_HOME/genesis/bin/$DAEMON_NAME"
sudo -u "$SERVICE_USER" ln -sfn "$COSMOVISOR_HOME/genesis/bin/$DAEMON_NAME" "$COSMOVISOR_HOME/$DAEMON_NAME"

echo "== systemd unit =="
sudo tee /etc/systemd/system/lightd.service >/dev/null <<UNIT
[Unit]
Description=LightDAO node (cosmovisor)
After=network-online.target
Wants=network-online.target

[Service]
User=$SERVICE_USER
Group=$SERVICE_USER
Type=simple
Environment=DAEMON_NAME=$DAEMON_NAME
Environment=DAEMON_HOME=$COSMOVISOR_HOME
Environment=DAEMON_ARGS=start --home $HOME_DIR --rpc.laddr tcp://0.0.0.0:26657
Environment=UNSAFE_SKIP_BACKUP=true
ExecStart=/usr/local/bin/cosmovisor run \$DAEMON_ARGS
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable lightd.service
echo "enabled lightd.service (start AFTER genesis_time: sudo systemctl start lightd)"
echo
echo "UPGRADE FLOW (governance WasmMsg::Migrate for contracts; software-upgrade for the CHAIN binary):"
echo "  1) pass an on-chain software-upgrade proposal at height H"
echo "  2) before H: place new binary at $COSMOVISOR_HOME/upgrades/<name>/bin/wasmd on every node"
echo "  3) at H the chain halts; cosmovisor swaps binary and restarts automatically"
