#!/usr/bin/env bash
# 迁移门禁"可复现声明"三档反向验证：编造的提交号必须被拒，真实提交号才放行。
set -u
BL=/home/ubuntu/repo/contracts/wasm/BUILDLOG.tsv
GATE=/usr/local/bin/ld_migrate_gate.py
GOV=wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt
REAL=$(cd /home/ubuntu/repo && git rev-parse HEAD)
cp -a $BL /tmp/bl.orig

setrow() {   # $2 = 要写进 source_commit 的值
  cp -a /tmp/bl.orig $BL
  python3 - "$1" <<'PY'
import sys
p="/home/ubuntu/repo/contracts/wasm/BUILDLOG.tsv"
val=sys.argv[1]
out=[]
for ln in open(p,encoding="utf-8"):
    if ln.startswith("19\t"):
        f=ln.rstrip("\n").split("\t")
        f[3]=val; f[5]="yes"; f[6]=""
        ln="\t".join(f)+"\n"
    out.append(ln)
open(p,"w",encoding="utf-8").write("".join(out))
PY
}

echo "=== A) 声明 yes 但 source_commit=unknown → 必须 FAIL ==="
setrow unknown
out=$(sudo python3 $GATE check 19 $GOV); rc=$?; echo "$out" | cut -c1-118; echo "  rc=$rc"

echo "=== B) 声明 yes 但 source_commit=deadbeef（编造）→ 必须 FAIL ==="
setrow deadbeef
out=$(sudo python3 $GATE check 19 $GOV); rc=$?; echo "$out" | cut -c1-118; echo "  rc=$rc"

echo "=== C) 声明 yes 且 source_commit 是真实提交 → 必须 OK ==="
setrow "$REAL"
out=$(sudo python3 $GATE check 19 $GOV); rc=$?; echo "$out" | cut -c1-118; echo "  rc=$rc"

cp -a /tmp/bl.orig $BL
echo "=== D) 复位后（19 回到跟踪例外，watch 应 rc=0） ==="
sudo python3 $GATE watch | tail -1; echo "rc=${PIPESTATUS[0]}"
