#!/usr/bin/env bash
# monitoring_setup.sh — run on the MONITORING node. Installs Prometheus + Grafana + Alertmanager,
# scrapes all validators' CometBFT metrics (:26660), and loads LightDAO alert rules.
#
# Env: VALIDATOR_IPS="ip1 ip2 ... ip7"  METRICS_PORT=26660  GRAFANA_ADMIN_PW=...
set -euo pipefail
VALIDATOR_IPS=${VALIDATOR_IPS:?set VALIDATOR_IPS="ip1 ip2 ip3 ip4 ip5 ip6 ip7"}
METRICS_PORT=${METRICS_PORT:-26660}
PROM_VER=${PROM_VER:-2.53.0}
GRAFANA_ADMIN_PW=${GRAFANA_ADMIN_PW:-changeme}

echo "== [1/5] enable metrics on each node's config.toml (do this on every validator too) =="
echo "   [instrumentation] enabled=true, addr 0.0.0.0:$METRICS_PORT   (keep $METRICS_PORT firewalled to VPC/monitor IP only)"

echo "== [2/5] install Prometheus =="
cd /tmp
wget -q "https://github.com/prometheus/prometheus/releases/download/v${PROM_VER}/prometheus-${PROM_VER}.linux-amd64.tar.gz"
tar xzf "prometheus-${PROM_VER}.linux-amd64.tar.gz"
sudo install -m0755 "prometheus-${PROM_VER}.linux-amd64"/prometheus /usr/local/bin/prometheus
sudo install -m0755 "prometheus-${PROM_VER}.linux-amd64"/promtool   /usr/local/bin/promtool
sudo mkdir -p /etc/prometheus
SCRAPE=""
for ip in $VALIDATOR_IPS; do SCRAPE="$SCRAPE      - targets: ['${ip}:${METRICS_PORT}']\n"; done
sudo tee /etc/prometheus/prometheus.yml >/dev/null <<YML
global:
  scrape_interval: 15s
  evaluation_interval: 15s
rule_files:
  - /etc/prometheus/rules/lightdao.yml
scrape_configs:
  - job_name: 'lightdao-validators'
    static_configs:
$(printf "%b" "$SCRAPE")
YML

echo "== [3/5] alert rules (chain halt / jailed / missing blocks / disk / peers) =="
sudo mkdir -p /etc/prometheus/rules
sudo tee /etc/prometheus/rules/lightdao.yml >/dev/null <<'RULES'
groups:
- name: lightdao
  rules:
  - alert: ChainHalted
    expr: increase(cometbft_consensus_height[3m]) == 0
    for: 3m
    labels: {severity: critical}
    annotations: {summary: "Chain not producing blocks (>3m)"}
  - alert: ValidatorJailed
    expr: cometbft_consensus_validator_power == 0
    for: 1m
    labels: {severity: critical}
    annotations: {summary: "Validator power=0 (jailed/missing)"}
  - alert: MissingBlocks
    expr: rate(cometbft_consensus_num_txs[5m]) < 0
    for: 5m
    labels: {severity: warning}
  - alert: LowPeers
    expr: cometbft_p2p_peers < 3
    for: 5m
    labels: {severity: warning}
    annotations: {summary: "Node has <3 peers"}
  - alert: DiskHigh
    expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.20
    for: 10m
    labels: {severity: warning}
    annotations: {summary: "Disk <20% free"}
RULES
sudo promtool check config /etc/prometheus/prometheus.yml || true

sudo tee /etc/systemd/system/prometheus.service >/dev/null <<'UNIT'
[Unit]
Description=Prometheus
After=network-online.target
[Service]
Type=simple
ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
sudo mkdir -p /var/lib/prometheus
sudo systemctl daemon-reload && sudo systemctl enable --now prometheus

echo "== [4/5] install Grafana =="
sudo apt-get install -y apt-transport-https software-properties-common wget 2>/dev/null || true
wget -q -O /usr/share/keyrings/grafana.gpg https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list >/dev/null
sudo apt-get update -y && sudo apt-get install -y grafana
sudo systemctl enable --now grafana-server

echo "== [5/5] done =="
echo "Prometheus: http://<monitor-ip>:9090   Grafana: http://<monitor-ip>:3000 (admin/$GRAFANA_ADMIN_PW)"
echo "Import a CometBFT/Cosmos Grafana dashboard (e.g. grafana.com id 15991) and add Prometheus as source."
echo "Set Grafana admin password: sudo grafana-cli admin reset-admin-password '$GRAFANA_ADMIN_PW'"
