#!/usr/bin/env bash
# node_bootstrap.sh — run ONCE on every machine (7 validators + sentries + monitor).
# Installs deps, wasmd v0.60 binary, cosmovisor, firewall, tuning. Idempotent-ish.
#
# Usage (as a sudo user on each VPS):
#   WASMD_SRC=/path/to/wasmd bash node_bootstrap.sh
# Provide the wasmd v0.60 linux/amd64 binary via WASMD_SRC (scp it from the build box;
# wasmd ships NO official release binaries, so you reuse the one you compiled).
set -euo pipefail
SERVICE_USER=${SERVICE_USER:-lightdao}
WASMD_SRC=${WASMD_SRC:?set WASMD_SRC=/path/to/wasmd (linux/amd64 v0.60 binary)}
HOME_DIR=${HOME_DIR:-/home/$SERVICE_USER/.wasmd}
SSH_PORT=${SSH_PORT:-22}

echo "== [1/7] system packages =="
sudo apt-get update -y
sudo apt-get install -y build-essential curl wget jq git ufw fail2nvim 2>/dev/null || sudo apt-get install -y build-essential curl wget jq git ufw

echo "== [2/7] service user + dirs =="
id -u "$SERVICE_USER" >/dev/null 2>&1 || sudo useradd -m -s /bin/bash "$SERVICE_USER"
sudo mkdir -p /usr/local/bin "$HOME_DIR"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$HOME_DIR"

echo "== [3/7] install wasmd binary =="
sudo install -m 0755 "$WASMD_SRC" /usr/local/bin/wasmd
wasmd version --long 2>/dev/null | grep -aE 'cosmos_sdk_version' || true

echo "== [4/7] install cosmovisor (for on-chain software upgrades) =="
if ! command -v cosmovisor >/dev/null; then
  # prefer a prebuilt cosmovisor binary if provided, else go install
  if [ -n "${COSMOVISOR_SRC:-}" ]; then sudo install -m 0755 "$COSMOVISOR_SRC" /usr/local/bin/cosmovisor
  elif command -v go >/dev/null; then GOBIN=/usr/local/bin sudo -E go install cosmossdk.io/tools/cosmovisor@v1.5.0
  else echo "WARN: no cosmovisor; provide COSMOVISOR_SRC or install Go 1.23"; fi
fi

echo "== [5/7] kernel/network tuning (NVMe + high peer count) =="
sudo tee /etc/sysctl.d/99-lightdao.conf >/dev/null <<'SYS'
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5
net.core.somaxconn=4096
net.ipv4.tcp_max_syn_backlog=4096
fs.file-max=2097152
SYS
sudo sysctl --system >/dev/null
echo "$SERVICE_USER soft nofile 65535" | sudo tee /etc/security/limits.d/99-lightdao.conf >/dev/null
echo "$SERVICE_USER hard nofile 65535" | sudo tee -a /etc/security/limits.d/99-lightdao.conf >/dev/null

echo "== [6/7] firewall (default-deny inbound; expose only what's needed) =="
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow "$SSH_PORT"/tcp comment 'ssh'
sudo ufw allow 26656/tcp comment 'cometbft p2p'
# RPC/API: expose ONLY on sentries/RPC node. On validators keep them local (do NOT allow):
if [ "${EXPOSE_RPC:-no}" = "yes" ]; then
  sudo ufw allow 26657/tcp comment 'rpc (sentry/rpc only)'
  sudo ufw allow 1317/tcp  comment 'lcd api (sentry/rpc only)'
fi
# metrics (26660) stays local; Prometheus scrapes via SSH tunnel or from within VPC only.
sudo ufw --force enable
sudo ufw status verbose || true

echo "== [7/7] done. Next: run validator_init.sh (validators) or node_run.sh (sentry/rpc) =="
echo "wasmd: $(command -v wasmd)  home: $HOME_DIR  user: $SERVICE_USER"
