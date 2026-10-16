#!/bin/bash
# 金库 5 把签名钥：加密冷备份 + 【还原验证】+ 权限收紧。
# 绝不把明文钥发到本机以外的地方；密文可以。绝不打印口令。
set -u
SRC=/home/ubuntu/.wasmd/keyring-test
TS=$(date +%Y%m%dT%H%M%SZ)
WORK=/home/ubuntu/backup/treasury-keys-$TS
PASSFILE=$WORK/passphrase.once
BLOB=$WORK/treasury_signers_keyring.tar.gz.enc

mkdir -p "$WORK"
echo "== 1) 只打包 5 把金库钥所在的整个 keyring（cosmos test 后端靠索引文件解析，必须整目录）=="
TMPK=$WORK/keyring-test
mkdir -p "$TMPK"
for n in signer1 signer2 signer3 signer4 signer5; do
  if [ -f "$SRC/$n.info" ]; then
    cp -a "$SRC/$n.info" "$TMPK/"
    [ -f "$SRC/$n.address" ] && cp -a "$SRC/$n.address" "$TMPK/"
    echo "   收 $n.info ✓"
  else
    echo "   缺 $n.info  <<< 中止"; exit 2
  fi
done
echo "   实际打包文件数: $(ls -1 $TMPK | wc -l)"

echo "== 2) 生成随机口令（只写入 0600 文件，不打印）=="
head -c 24 /dev/urandom | base64 | tr -d '\n=' > "$PASSFILE"
chmod 600 "$PASSFILE"
echo "   口令长度 $(wc -c < $PASSFILE) 字符（值不显示）"

echo "== 3) 加密打包 =="
tar -cz -C "$WORK" keyring-test | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt \
  -pass file:"$PASSFILE" -out "$BLOB"
chmod 600 "$BLOB"
echo "   密文 $(ls -l $BLOB | awk '{print $5}') 字节  sha256=$(sha256sum $BLOB | cut -c1-16)…"

echo "== 4) 还原验证（解密到隔离目录，证明备份真的可用）=="
VER=$WORK/verify
mkdir -p "$VER"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$PASSFILE" -in "$BLOB" \
  | tar -xz -C "$VER"
echo "   还原出 $(ls -1 $VER/keyring-test | wc -l) 个文件"
echo "   用还原副本解析 5 把钥的地址（应为 wasmvaloper/wasm 主网地址，逐条比对）:"
for n in signer1 signer2 signer3 signer4 signer5; do
  a=$(wasmd keys show $n --keyring-backend test --home "$VER" -a 2>/dev/null | grep -oE 'wasm[a-z0-9]{39,}' | head -1)
  echo "     $n -> ${a:-解析失败}"
done

echo "== 5) 权限收紧（明文 keyring 目录与 .info）=="
chmod 700 /home/ubuntu/.wasmd/keyring-test 2>/dev/null || sudo chmod 700 /home/ubuntu/.wasmd/keyring-test
for n in signer1 signer2 signer3 signer4 signer5; do
  sudo chmod 600 "$SRC/$n.info" 2>/dev/null && echo "   $n.info -> 600"
done
echo "   当前: $(ls -ld /home/ubuntu/.wasmd/keyring-test | awk '{print $1, $3}')"

echo
echo "BLOB=$BLOB"
echo "PASSFILE=$PASSFILE"
echo "NEXT: 用链上 signers 逐条核对上面 5 个地址，全部一致才允许考虑从网关摘除明文"

# ===== LD-BACKUP-CLEANUP-20261016 =====
# 缺陷修复：本脚本原先把明文 keyring 与 verify 解包目录留在备份目录里，
# 等于在"加密备份"旁边摆着明文私钥（2026-10-16 发现，机器上 15 个残留已清除）。
# 收尾强制粉碎一切明文，并调用不变量检测自检。
echo "[收尾] 清除备份目录内的明文私钥残留"
find "$WORK" -name '*.info' -type f -exec shred -u {} + 2>/dev/null || true
find /tmp -maxdepth 1 -name 'verify-restore-*' -type d 2>/dev/null | while read -r d; do
  find "$d" -type f -exec shred -u {} + 2>/dev/null || true
done
left=$(find "$WORK" -name '*.info' 2>/dev/null | wc -l)
if [ "$left" != "0" ]; then echo "FAIL 备份目录仍有 $left 个明文私钥"; exit 5; fi
if [ -f "$WORK/passphrase.once" ]; then
  echo "提醒：口令与密文同机存放。交付给用户后必须 shred 该口令文件，否则加密无意义。"
fi
if command -v /usr/local/bin/ld_treasury_keywatch.sh >/dev/null 2>&1; then
  sudo /usr/local/bin/ld_treasury_keywatch.sh || { echo "FAIL 金库密钥不变量检测未通过"; exit 6; }
fi
echo "BACKUP_CLEANUP_OK 备份目录只剩密文"
