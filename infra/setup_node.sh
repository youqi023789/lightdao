#!/bin/bash
# LightDAO v2-lightfee 节点升级预备:注入 lightfee env + 部署自动切换看门狗。
# 用法: sudo bash setup_node.sh <NEW_BIN路径> <TREASURY地址>
# 幂等;不重启 lightd.service(旧二进制继续跑,直到 H 高度看门狗自动切换)。
set -e
NEW_BIN="$1"; TREAS="$2"
mkdir -p /etc/lightdao

# 1) lightfee env(新二进制启动时读取;旧二进制忽略)
cat > /etc/lightdao/lightfee.env <<ENVEOF
LIGHTDAO_DENOM=ulight
LIGHTDAO_STATIC_PRICE_USD=0.05
LIGHTDAO_TREASURY_ADDR=$TREAS
LIGHTDAO_TRANSFER_USD=0.001
ENVEOF

# 2) 给 lightd.service 注入 EnvironmentFile(幂等)
if ! grep -q "EnvironmentFile=-/etc/lightdao/lightfee.env" /etc/systemd/system/lightd.service; then
  sed -i '/^\[Service\]/a EnvironmentFile=-/etc/lightdao/lightfee.env' /etc/systemd/system/lightd.service
fi

# 3) 看门狗脚本(检测 UPGRADE NEEDED → 备份+换二进制+重启,done-flag 防重复)
#    grep 用 ERE 通配,避免引号转义脆弱性
cat > /usr/local/bin/lightd-upgrade-watch.sh <<'WEOF'
#!/bin/bash
UPGRADE_NAME="v2-lightfee"
NEW_BIN="__NEWBIN__"
TARGET="/usr/local/bin/wasmd"
DONE_FLAG="/etc/lightdao/.upgrade-${UPGRADE_NAME}-done"
UNIT="lightd.service"
while true; do
  sleep 8
  [ -f "$DONE_FLAG" ] && continue
  if journalctl -u "$UNIT" --since "60 seconds ago" --no-pager 2>/dev/null | grep -qE "UPGRADE.*${UPGRADE_NAME}.*NEEDED"; then
    if [ -f "$NEW_BIN" ]; then
      cp -f "$TARGET" "${TARGET}.v1.bak.$(date +%s)" 2>/dev/null || true
      cp -f "$NEW_BIN" "$TARGET"
      chmod +x "$TARGET"
      touch "$DONE_FLAG"
      systemctl restart "$UNIT"
      logger -t lightd-upgrader "SWAPPED to lightd for $UPGRADE_NAME at $(date -u)"
    fi
  fi
done
WEOF
sed -i "s|__NEWBIN__|$NEW_BIN|g" /usr/local/bin/lightd-upgrade-watch.sh
chmod +x /usr/local/bin/lightd-upgrade-watch.sh

# 4) 看门狗 systemd 服务
cat > /etc/systemd/system/lightd-upgrader.service <<'UEOF'
[Unit]
Description=LightDAO v2-lightfee auto-swap watcher
After=lightd.service
[Service]
Type=simple
ExecStart=/usr/local/bin/lightd-upgrade-watch.sh
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
UEOF

systemctl daemon-reload
systemctl enable --now lightd-upgrader.service >/dev/null 2>&1
echo "OK env+watcher | lightd=$(systemctl is-active lightd) watcher=$(systemctl is-active lightd-upgrader) | newbin=$(sha256sum "$NEW_BIN" 2>/dev/null | cut -c1-12)"
