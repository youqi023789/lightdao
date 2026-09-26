#!/bin/bash
# LightDAO §4.7 coturn (TURN/STUN 中继) 部署。用法: sudo bash coturn_deploy.sh <公网IP> <turn密钥>
# 带 systemd 资源限制(CPUWeight/IOWeight/MemoryMax)保护同机 wasmd 共识进程。
set -e
PUBIP="$1"; SECRET="$2"
export DEBIAN_FRONTEND=noninteractive

echo "[1] 安装 coturn"
apt-get update -qq
apt-get install -y -qq coturn >/dev/null

echo "[2] 写 /etc/turnserver.conf"
cat > /etc/turnserver.conf <<TEOF
# LightDAO TURN/STUN — §4.7 中继层
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=$PUBIP
realm=lightdao.net
server-name=lightdao.net
# REST API 临时凭证(WebRTC 标准用法)
use-auth-secret
static-auth-secret=$SECRET
# 中继端口范围
min-port=49152
max-port=65535
fingerprint
no-tlsv1
no-tlsv1_1
no-cli
# SSRF 防护:禁止中继到内网/环回/元数据
denied-peers=127.0.0.0/8,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,169.254.0.0/16,0.0.0.0/8
no-multicast-peers
proc-user=turnserver
proc-group=turnserver
# 日志
log-file=/var/log/turnserver.log
simple-log
TEOF

echo "[3] 启用 coturn"
if [ -f /etc/default/coturn ]; then
  sed -i 's/#TURNSERVER_ENABLED=1/TURNSERVER_ENABLED=1/' /etc/default/coturn
  grep -q TURNSERVER_ENABLED /etc/default/coturn || echo "TURNSERVER_ENABLED=1" >> /etc/default/coturn
fi

echo "[4] systemd 资源限制(保护 wasmd 共识优先级)"
mkdir -p /etc/systemd/system/coturn.service.d
cat > /etc/systemd/system/coturn.service.d/limits.conf <<LEOF
[Service]
CPUWeight=40
IOWeight=40
MemoryMax=1G
Nice=10
LEOF

echo "[5] OS 防火墙(ufw)"
ufw allow 3478/tcp  >/dev/null 2>&1 || true
ufw allow 3478/udp  >/dev/null 2>&1 || true
ufw allow 5349/tcp  >/dev/null 2>&1 || true
ufw allow 49152:65535/udp >/dev/null 2>&1 || true

echo "[6] 启动"
systemctl daemon-reload
systemctl enable --now coturn >/dev/null 2>&1
sleep 2
ACT=$(systemctl is-active coturn)
LIS=$(ss -tulnp 2>/dev/null | grep -c ':3478')
echo "RESULT coturn=$ACT listening_3478=$LIS pubkey_ext=$PUBIP"
echo "⚠ 还需在腾讯云控制台防火墙放行: 3478/tcp,3478/udp,5349/tcp,49152-65535/udp (否则外网连不进)"
