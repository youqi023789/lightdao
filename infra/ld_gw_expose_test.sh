#!/usr/bin/env bash
# 反向验证 ld_gw_expose_watch.py：造一个真监听在 0.0.0.0 的影子端口，
# 让哨兵必须报 E1；再把影子撤掉，确认它转绿。
set -u
PORT=${1:-8099}
export PYTHONDONTWRITEBYTECODE=1
echo "=== A) 正常态（真网关端口 8080） ==="
python3 /usr/local/bin/ld_gw_expose_watch.py; echo "rc=$?"
echo "=== B) 造一个 0.0.0.0:$PORT 的影子监听 ==="
python3 - "$PORT" <<'PY' &
import socket, sys, time
p = int(sys.argv[1])
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", p))
s.listen(1)
time.sleep(25)
PY
SHADOW=$!
sleep 2
ss -ltn | grep -c "0.0.0.0:$PORT" | sed 's/^/   影子监听确认: /'
LD_GW_PORT=$PORT python3 /usr/local/bin/ld_gw_expose_watch.py; rc=$?
echo "   rc=$rc（应为 1）"
kill $SHADOW 2>/dev/null
wait $SHADOW 2>/dev/null
echo "=== C) 撤掉影子后（哨兵应转绿或至少不再报 E1） ==="
sleep 1
LD_GW_PORT=$PORT python3 /usr/local/bin/ld_gw_expose_watch.py; echo "   rc=$?（端口没人听，应报 E1 缺失，不是通过）"
echo "=== D) 回到真端口确认全绿 ==="
python3 /usr/local/bin/ld_gw_expose_watch.py; echo "rc=$?"
