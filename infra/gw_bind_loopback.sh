#!/usr/bin/env bash
# 把评分网关从 0.0.0.0:8080 收紧到 127.0.0.1:8080（明文公网口 → 只留 nginx /gw）。
# 状态：2026-10-16 写好但**未执行**——生产变更要等用户在线批准（见 docs/GW_BIND_LOOPBACK_PROPOSAL.md）。
# 用法：sudo bash gw_bind_loopback.sh            # 执行
#      sudo bash gw_bind_loopback.sh --rollback # 还原到执行前
set -u
GW=/usr/local/bin/gateway_v3.py
SVC=lightdao-gateway
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BAK=/root/gateway_v3.py.bak-bind-$STAMP
UNITBAK=/root/$SVC.unit.bak-bind-$STAMP

rollback() {
  if [ -f /root/gateway_v3.py.bind-backup ]; then
    cp -a /root/gateway_v3.py.bind-backup $GW && echo "已还原脚本"
    systemctl daemon-reload; systemctl restart $SVC; echo "已重启（回滚）"
    curl -s -m 5 -o /dev/null -w "本机 health HTTP %{http_code}\n" http://127.0.0.1:8080/v1/health
  else
    echo "没有 /root/gateway_v3.py.bind-backup，无从回滚"; exit 2
  fi
}
[ "${1:-}" = "--rollback" ] && { rollback; exit $?; }

echo "== 0) 前置确认：矿工确实走 /gw，没人直连 8080 =="
est=$(ss -tn state established "( sport = :8080 )" 2>/dev/null | grep -c ":8080" || true)
echo "   当前 8080 上的已建立连接数 = $est（>0 就先别动，先查是谁）"
if [ "$est" != "0" ]; then echo "   中止：有活跃直连"; exit 3; fi

echo "== 1) 备份 =="
cp -a $GW /root/gateway_v3.py.bind-backup; cp -a $GW $BAK
systemctl cat $SVC > $UNITBAK 2>/dev/null || true
echo "   备份：$BAK"

echo "== 2) 打补丁（绑定地址改成可用环境变量控制，默认 127.0.0.1） =="
python3 - <<'PY'
import re
p = "/usr/local/bin/gateway_v3.py"
s = open(p, encoding="utf-8").read()
if 'GW_BIND' in s:
    print("   已打过补丁，跳过")
    raise SystemExit(0)
new = s.replace('ThreadingHTTPServer(("0.0.0.0", PORT), H)',
                'ThreadingHTTPServer((os.environ.get("GW_BIND", "127.0.0.1"), PORT), H)')
if new == s:
    print("   FAIL 没找到要替换的绑定行，不动文件")
    raise SystemExit(1)
open(p, "w", encoding="utf-8").write(new)
print("   已替换绑定行")
PY
rc=$?
if [ $rc -ne 0 ]; then echo "   补丁失败，还原"; cp -a /root/gateway_v3.py.bind-backup $GW; exit 4; fi

echo "== 3) 语法自检（不过就自动还原，绝不带着坏文件重启） =="
if ! python3 -m py_compile $GW; then
  echo "   py_compile 失败，还原并退出"; cp -a /root/gateway_v3.py.bind-backup $GW; exit 5
fi
echo "   语法 OK"

echo "== 4) 重启（必须 sudo 下执行，本脚本要求 sudo） =="
systemctl daemon-reload && systemctl restart $SVC && sleep 3
systemctl is-active $SVC

echo "== 5) 三项验收 =="
curl -s -m 6 -o /dev/null -w "   本机 127.0.0.1:8080/v1/health  HTTP %{http_code}\n" http://127.0.0.1:8080/v1/health
curl -sk -m 10 -o /dev/null -w "   公网 /gw/v1/health            HTTP %{http_code}\n" https://lightdao.net/gw/v1/health
echo -n "   监听地址："; ss -ltnp 2>/dev/null | grep ":8080" | head -1

bind_now=$(ss -ltn 2>/dev/null | grep -c "0.0.0.0:8080" || true)
if [ "$bind_now" != "0" ]; then
  echo "   FAIL 仍在 0.0.0.0 上监听 → 自动回滚"; rollback; exit 6
fi
echo "   PASS 已只绑 127.0.0.1"
echo "== 6) 10 分钟后请看心跳是否继续 =="
echo "   sudo tail -f /var/log/nginx/access.log | grep 'POST /gw/v1/heartbeat'"
echo "   或跑：bash /home/ubuntu/ld_gw_heartbeat_count.sh"
