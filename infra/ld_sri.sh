#!/bin/bash
# ld_sri.sh — 每天校验线上 HTML 的 SRI 完整性，坏了一条就落告警 + 推 Discord。
#
# LD-SRI-DEADCHECK-20261017 之前三天（10-15/16/17）这条 cron 都在报 "SRI-FAIL"，
# 看起来像"线上有问题"，真相是它调用的 /home/ubuntu/sri_verify.py 根本不存在——
# 也就是【检测工具自己坏了】，SRI 这条不变量三天没有任何执行点，而红灯还长得
# 像"被测系统出问题"。教训与修法：
#   1) 改调仓库里那份通用工具 sri_integrity.py（root 参数化，verify 实测 241 项 0 失败）；
#   2) 三种结果分开报，绝不混为一谈：
#        SRI-TOOL-BAD   工具/路径坏了（检测点自己失效，优先级最高）
#        SRI-MISMATCH   线上真的不一致（会导致浏览器拒绝加载脚本=白屏）
#        SRI OK         通过
#   3) 告警文本带上原因与实数，不再只写一个 SRI-FAIL 让人去猜。
#   4) 退出码保留：promote/CI 可以拿它当门。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
LOG=/home/ubuntu/ld_sri.log
TOOL=/usr/local/bin/sri_integrity.py
ROOT=${1:-/var/www/lightdao}
PY=/usr/bin/python3

alert() {
  echo "$(date -u +%FT%TZ) $1" >> /home/ubuntu/ld_alerts.log
  $PY /usr/local/bin/discord_bot.py send "$2" >/dev/null 2>&1
}

# ---- 检测点自检：工具不在/不可编译，就是 SRI-TOOL-BAD，绝不能算"通过" ----
if [ ! -f "$TOOL" ]; then
  echo "$(date -u +%FT%TZ) SRI-TOOL-BAD 找不到 $TOOL" >> "$LOG"
  alert "SRI-TOOL-BAD" "🚨 SRI 校验没法跑：$TOOL 不存在（这条不变量当前无执行点）"
  exit 2
fi
# 自检只做"纯读语法解析"：原来用 py_compile 写 /tmp/ld_sri_check.pyc 固定名，
# root 与 ubuntu 两种身份跑就会因为粘滞位 /tmp 不让覆盖对方的文件而失败——
# 失败被判成"检测工具坏了"，于是每天误报 SRI-TOOL-BAD，而真校验是过的。
if ! $PY -c "import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read())" "$TOOL" 2>>"$LOG"; then
  echo "$(date -u +%FT%TZ) SRI-TOOL-BAD $TOOL 语法不过" >> "$LOG"
  alert "SRI-TOOL-BAD" "🚨 SRI 校验工具本身语法不过：$TOOL"
  exit 2
fi

OUT=$($PY "$TOOL" verify "$ROOT" 2>&1); RC=$?
echo "$OUT" >> "$LOG"
if [ "$RC" = 0 ]; then
  # 通过也要能证明"真的数过东西"：checked=0 说明量具空转
  if echo "$OUT" | grep -q "checked=0"; then
    echo "$(date -u +%FT%TZ) SRI-TOOL-BAD checked=0（没校验到任何标签）" >> "$LOG"
    alert "SRI-TOOL-BAD" "🚨 SRI 校验返回 0 项——要么页面没 integrity 要么工具坏了，不接受当成通过"
    exit 2
  fi
  echo "$(date -u +%FT%TZ) $(echo "$OUT" | tail -1)" >> "$LOG"
  exit 0
fi
echo "$(date -u +%FT%TZ) SRI-MISMATCH" >> "$LOG"
DETAIL=$(echo "$OUT" | grep -m3 -E "FAIL|hash-mismatch|missing-file" | head -c 280)
alert "SRI-MISMATCH" "🚨 SRI 不一致 on $(hostname) at $ROOT：${DETAIL}（浏览器会拒绝加载这些脚本=白屏）"
exit 1
