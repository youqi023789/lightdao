#!/usr/bin/env bash
# LD-GW-HARDEN-20261016  合并变更：
#   1) 评分网关 8080 从 0.0.0.0 收紧到 127.0.0.1（外部只留 nginx /gw 这一条路）
#   2) 轮换管理员口令，并从 systemd 单元里搬进 root:ubuntu 0640 的 EnvironmentFile
#      —— 之前口令写在单元文件的 Environment= 行里，`systemctl cat` 就能看到明文，
#      本轮排查就是用它带出过一次口令，必须从根上改掉这个暴露面
#   3) X-Admin 比对改成 hmac.compare_digest（防时序侧信道）
# 任何一步失败：自动还原全部备份并重启回旧状态。
set -u
TS=$(date -u +%Y%m%dT%H%M%SZ)
BK=/root/gw_hardening_$TS
UNIT=/etc/systemd/system/lightdao-gateway.service
DROP=/etc/systemd/system/lightdao-gateway.service.d
GWPY=/usr/local/bin/gateway_v3.py
FIN=/usr/local/bin/ld_finalize.sh
ENVF=/etc/lightdao/gw_admin.env
OLDSEC=/home/ubuntu/lightdao_gateway/admin_secret
[ "$(id -u)" = "0" ] || { echo "要用 sudo 跑"; exit 2; }
mkdir -p $BK && chmod 700 $BK
cp -a $UNIT $BK/unit.main
cp -a $DROP $BK/dropins
cp -a $GWPY $BK/gateway_v3.py
cp -a $FIN $BK/ld_finalize.sh
[ -f $OLDSEC ] && cp -a $OLDSEC $BK/admin_secret.old && OLDBAK=1 || OLDBAK=0
echo "备份完成 -> $BK"

restore() {
  echo "!! 回滚：还原单元/脚本/口令"
  cp -a $BK/unit.main $UNIT
  rm -rf $DROP; cp -a $BK/dropins $DROP
  cp -a $BK/gateway_v3.py $GWPY
  cp -a $BK/ld_finalize.sh $FIN
  [ "$OLDBAK" = "1" ] && cp -a $BK/admin_secret.old $OLDSEC
  rm -f $ENVF
  systemctl daemon-reload && systemctl restart lightdao-gateway
  sleep 3
  curl -s -m 6 -o /dev/null -w "回滚后本机 health HTTP %{http_code}\n" http://127.0.0.1:8080/v1/health
  exit 1
}

echo "== 1) 生成新口令并落进单一来源文件（不打印值） =="
umask 077
install -d -m 750 /etc/lightdao
printf 'GW_ADMIN_SECRET=%s\n' "$(openssl rand -hex 32)" > $ENVF
chown root:ubuntu $ENVF; chmod 640 $ENVF
if ! grep -q "^GW_ADMIN_SECRET=[0-9a-f]\{32,\}$" $ENVF; then echo "新口令写入失败"; restore; fi
cp -f $ENVF $BK/gw_admin.env.copies && chmod 600 $BK/gw_admin.env.copies
# 兼容旧读取方：老路径同步成新值（下一步会把 ld_finalize.sh 改成读 $ENVF）
if [ "$OLDBAK" = "1" ]; then
  cut -d= -f2- $ENVF > $OLDSEC
  chmod 640 $OLDSEC
fi
echo "   新口令已写入 $ENVF（root:ubuntu 640）"

echo "== 2) 单元里去掉明文 Environment= 行，改用 EnvironmentFile =="
if grep -qE "^Environment=GW_ADMIN_SECRET=" $UNIT; then
  sed -i -E "s|^Environment=GW_ADMIN_SECRET=.*|EnvironmentFile=$ENVF|" $UNIT
else
  sed -i "/^\[Service\]/a EnvironmentFile=$ENVF" $UNIT
fi
grep -q "EnvironmentFile=$ENVF" $UNIT || { echo "单元改失败"; restore; }
grep -qE "^Environment=GW_ADMIN_SECRET=" $UNIT && { echo "明文行还在"; restore; }
echo "   单元已改为 EnvironmentFile（systemctl cat 不再显示口令）"

echo "== 3) 网关脚本：绑定地址可配（默认只绑本机）+ 口令比对改常量时间 =="
python3 - <<'PY' || restore
import re
p = "/usr/local/bin/gateway_v3.py"
s = open(p, encoding="utf-8").read()
if "LD-GW-HARDEN" not in s:
    # 注意：必须整行替换。上一版只替换了 ThreadingHTTPServer(...) 那一小截，
    # 把行尾注释插在 .serve_forever() 之前，等于把"开始服务"注释掉了——
    # 进程建好对象就正常退出（退出码 0、无 traceback），实盘启动后 1 秒就没了。
    old = 'ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()'
    new = ('ThreadingHTTPServer((os.environ.get("GW_BIND", "127.0.0.1"), PORT), H)'
           '.serve_forever()  # LD-GW-HARDEN 外部只走 nginx /gw')
    if old not in s:
        print("FAIL 没找到完整绑定行，不动文件"); raise SystemExit(1)
    s = s.replace(old, new, 1)
if "compare_digest" not in s:
    s = s.replace("from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer",
                  "from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\n"
                  "import hmac  # LD-GW-HARDEN 管理员口令用常量时间比对")
    old2 = 'if self.headers.get("X-Admin") != ADMIN: return self._send(403, {"error": "forbidden"})'
    new2 = ('if not hmac.compare_digest(str(self.headers.get("X-Admin") or ""), str(ADMIN)):'
            ' return self._send(403, {"error": "forbidden"})  # LD-GW-HARDEN')
    if old2 not in s:
        print("FAIL 没找到 X-Admin 比对行，不动文件"); raise SystemExit(1)
    s = s.replace(old2, new2, 1)
open(p, "w", encoding="utf-8").write(s)
# 自检：serve_forever 必须还在、且没被行尾注释吞掉（上一版就栽在这里）
chk = open(p, encoding="utf-8").read()
bad = [l for l in chk.splitlines()
       if ".serve_forever()" in l and "#" in l.split(".serve_forever()")[0]]
if not any(l.strip().startswith("ThreadingHTTPServer(") and ".serve_forever()" in l
           for l in chk.splitlines()) or bad:
    print("FAIL serve_forever 被注释吞掉或丢了，不动文件"); raise SystemExit(1)
import ast
ast.parse(chk)
print("   gateway_v3.py 已打两处补丁（serve_forever 仍在注释之前）")
PY
python3 -m py_compile $GWPY || { echo "网关脚本语法不过"; restore; }
grep -n "serve_forever" $GWPY | tail -2 | cut -c1-130

echo "== 4) 每日结算脚本改成读同一个来源 =="
python3 - <<'PY'
p = "/usr/local/bin/ld_finalize.sh"
s = open(p, encoding="utf-8").read()
if "gw_admin.env" not in s:
    old = 'S=$(cat /home/ubuntu/lightdao_gateway/admin_secret)'
    new = ('# LD-GW-HARDEN 管理员口令只有一个来源，避免"单元里一份、文件里一份"迟早对不上\n'
           'S=$(grep -m1 "^GW_ADMIN_SECRET=" /etc/lightdao/gw_admin.env | cut -d= -f2-)')
    if old not in s:
        print("FAIL 没找到取口令那行，人工确认后再改"); raise SystemExit(1)
    open(p, "w", encoding="utf-8").write(s.replace(old, new))
print("   ld_finalize.sh 已改读 /etc/lightdao/gw_admin.env")
PY
bash -n $FIN || { echo "finalize 脚本语法不过"; restore; }

echo "== 4.5) 退役重复的口令文件（原来是 ubuntu:ubuntu 664，同机任何进程都能读）=="
if [ "$OLDBAK" = "1" ] && [ -f $OLDSEC ]; then
  mv $OLDSEC $BK/admin_secret.retired && chmod 600 $BK/admin_secret.retired
  echo "   已移走 $OLDSEC（唯一来源现在是 $ENVF；两份口令迟早对不上）"
fi

echo "== 5) 重启 =="
systemctl daemon-reload && systemctl restart lightdao-gateway
# 上一版在这里 sleep 4 后只看 is-active，撞上 systemd 的 RestartSec=5 空档，
# 把"还没回到 active"误判成失败而触发回滚（那次其实真失败在别处）。
# 现在改成轮询：状态 active 且本机 health 真应答，才算起来。
up=0
for i in $(seq 1 12); do
  sleep 3
  st=$(systemctl is-active lightdao-gateway || true)
  hc=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/v1/health || echo 000)
  echo "   第 $i 次探测：state=$st health=$hc"
  [ "$st" = "active" ] && [ "$hc" = "200" ] && { up=1; break; }
done
[ "$up" = "1" ] || { echo "   起不来（state/health 不达标）"; restore; }

echo "== 6) 验收 =="
ok=1
curl -s -m 6 -o /dev/null -w "   本机 127.0.0.1:8080/v1/health  HTTP %{http_code}\n" http://127.0.0.1:8080/v1/health
[ "$(curl -s -m 6 -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/v1/health)" = "200" ] || { echo "   FAIL 本机 health 不通"; ok=0; }
curl -sk -m 10 -o /dev/null -w "   公网 /gw/v1/health             HTTP %{http_code}\n" https://lightdao.net/gw/v1/health
[ "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' https://lightdao.net/gw/v1/health)" = "200" ] || { echo "   FAIL /gw 不通"; ok=0; }
if ss -ltn | grep -q "0.0.0.0:8080"; then echo "   FAIL 仍在 0.0.0.0 上监听"; ok=0; else echo "   PASS 只绑 127.0.0.1"; fi
S=$(grep -m1 "^GW_ADMIN_SECRET=" $ENVF | cut -d= -f2-)
r_new=$(curl -s -m 10 -X POST http://127.0.0.1:8080/v1/finalize -H "X-Admin: $S" -d '{"day":34}')
echo "   新口令调 finalize：$r_new"
echo "$r_new" | grep -qE '"already"|"root"' || { echo "   FAIL 新口令没被接受"; ok=0; }
# 口令必须是 ASCII：上一版这里写中文，curl 直接拒发请求，http_code 变成 000，
# 被误判成"网关没拒绝错口令"。
code_bad=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8080/v1/finalize -H "X-Admin: wrong-secret-000" -d '{"day":34}')
[ "$code_bad" = "403" ] && echo "   PASS 错口令 403" || { echo "   FAIL 错口令返回 $code_bad（应 403）"; ok=0; }
# 取日志里最后一条 JSON 响应，不是 "finalizing day N" 那行 echo
bash $FIN
r_fin=$(tail -6 /home/ubuntu/ld_finalize.log | grep -E '^\{' | tail -1)
echo "   每日结算脚本实跑：${r_fin:-无 JSON 响应}"
echo "$r_fin" | grep -qE '"already"|"root"' || { echo "   FAIL 结算脚本没跑通"; ok=0; }
[ "$ok" = "1" ] || restore
echo "== 全部验收通过 =="
echo "旧口令文件与单元备份留在 $BK（700），确认稳定后可删"
