#!/bin/bash
# 网关 v2 -> v3 切换（/v1/validators），带前置校验、验收与自动回滚。
# 任何一步不达标：立刻回滚并退出非 0。全程不打印任何密钥值。
set -u
D=/etc/systemd/system/lightdao-gateway.service.d
TS=$(date +%Y%m%dT%H%M%SZ)

echo "== 0) 前置：确认 admin secret 不是代码默认值（不打印值）=="
PID=$(systemctl show lightdao-gateway -p MainPID --value)
ISDEFAULT=$(sudo tr '\0' '\n' < /proc/$PID/environ | awk -F= '/^GW_ADMIN_SECRET=/{print ($2=="change-me-in-prod")?"YES":"no"}')
HASVAR=$(sudo tr '\0' '\n' < /proc/$PID/environ | grep -c '^GW_ADMIN_SECRET=')
if [ "$HASVAR" = "0" ]; then echo "  GW_ADMIN_SECRET 未设置 -> 会退到默认值，中止切换"; exit 5; fi
if [ "$ISDEFAULT" = "YES" ]; then echo "  GW_ADMIN_SECRET 仍是默认值，中止切换（先改密钥）"; exit 5; fi
echo "  已自定义 ✓（值未显示）"

echo "== 1) 落地 v3（唯一差异 = 新增 /v1/validators；绑回 0.0.0.0）=="
cp -a /home/ubuntu/gateway_v2.py /home/ubuntu/gateway_v2.py.bak-$TS
sudo install -m 644 /home/ubuntu/gateway_v3_soak.py /usr/local/bin/gateway_v3.py
sudo sed -i 's/ThreadingHTTPServer(("127.0.0.1", PORT)/ThreadingHTTPServer(("0.0.0.0", PORT)/' /usr/local/bin/gateway_v3.py
sudo python3 -m py_compile /usr/local/bin/gateway_v3.py || { echo "  语法不通，中止"; exit 6; }
echo "  v3 语法 OK；绑定已改回 0.0.0.0；备份 $(basename /home/ubuntu/gateway_v2.py.bak-$TS)"

echo "== 2) 切 ExecStart =="
printf '%s\n' '[Service]' 'ExecStart=' 'ExecStart=/usr/bin/python3 /usr/local/bin/gateway_v3.py' | sudo tee $D/v3.conf >/dev/null
sudo systemctl daemon-reload && sudo systemctl restart lightdao-gateway
sleep 4
RUNNING=$(systemctl is-active lightdao-gateway)
NEWPID=$(systemctl show lightdao-gateway -p MainPID --value)
echo "  服务状态=$RUNNING 新 PID=$NEWPID"
if [ "$RUNNING" != "active" ]; then echo "  服务没起来 -> 回滚"; fi

echo "== 3) 验收三条 =="
PASS=1
H=$(curl -s -m 10 https://lightdao.net/gw/v1/health | head -c 120)
echo "  [1] /gw/v1/health -> $H"
echo "$H" | grep -q '"ok": *true' || { echo "      health 不 OK"; PASS=0; }
V=$(curl -s -m 40 https://lightdao.net/gw/v1/validators)
echo "  [2] /gw/v1/validators -> $(echo "$V" | head -c 150)"
echo "$V" | grep -q 'lightdao-mainnet-1' || { echo "      validators 没拿到主网链ID"; PASS=0; }
echo "$V" | grep -q 'wasmvaloper1' || { echo "      validators 没有 operator 地址"; PASS=0; }
S=$(curl -s -m 10 https://lightdao.net/gw/v1/scores | head -c 60)
echo "  [3] 既有端点 /gw/v1/scores -> $S"
echo "$S" | grep -q '"day"' || { echo "      既有端点回归"; PASS=0; }

echo "== 4) 决定 =="
if [ "$PASS" = "1" ]; then
  echo "CUTOVER_OK  （v2 备份：gateway_v2.py.bak-$TS；回滚：删除 $D/v3.conf 后 daemon-reload+restart）"
  exit 0
fi
echo "验收未过 -> 立即回滚"
sudo rm -f $D/v3.conf
sudo systemctl daemon-reload && sudo systemctl restart lightdao-gateway
sleep 4
echo "  回滚后状态=$(systemctl is-active lightdao-gateway) health=$(curl -s -m 10 https://lightdao.net/gw/v1/health | head -c 60)"
exit 1
