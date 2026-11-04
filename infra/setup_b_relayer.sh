#!/usr/bin/env bash
# 给 chain B 建中继账户并导入 hermes。
# hermes 1.13 的 `keys add` 不再自动生成助记词，必须给 --key-file 或 --mnemonic-file；
# 所以先用 wasmd 生成一把测试钥匙（B 链、test 钥匙串），把它的助记词交给 hermes 导入。
# 只在 B 的 home 与 hermes 自己的 keys 目录里操作，不碰主网、不碰 A 链。
set -euo pipefail
BIN=/home/ubuntu/lightd.testnet.bin
B=/home/ubuntu/.lightd-testnet-b
C=/home/ubuntu/.hermes/config/config.toml
MN=/home/ubuntu/.hermes/b_relayer.mnemonic

if [ ! -f "$MN" ]; then
  OUT=$(sudo -u ubuntu "$BIN" keys add relayerb --home "$B" --keyring-backend test --output json 2>&1 || true)
  MNEM=$(printf '%s' "$OUT" | python3 -c "
import json,sys,re
s=sys.stdin.read()
m=re.search(r'\"mnemonic\"\s*:\s*\"([^\"]+)\"', s)
print(m.group(1) if m else '')
" 2>/dev/null || true)
  if [ -z "${MNEM:-}" ]; then
    # 有些构建把助记词打在 stderr 的明文行里
    MNEM=$(printf '%s' "$OUT" | grep -oE "(-[a-z]+ ){11,23}[a-z]+" | head -1 | sed 's/^-//' || true)
  fi
  if [ -z "${MNEM:-}" ]; then
    echo "拿不到助记词，原始输出："; printf '%s\n' "$OUT" | head -12; exit 1
  fi
  printf '%s\n' "$MNEM" | sudo tee "$MN" >/dev/null
  sudo chown ubuntu:ubuntu "$MN"; sudo chmod 600 "$MN"
  echo "已写入助记词文件（B 链 relayer）"
fi

sudo -u ubuntu /usr/local/bin/hermes --config "$C" keys add --chain lightdao-testnet-b \
  --key-name relayer --mnemonic-file "$MN" --overwrite 2>&1 | tail -2 | cut -c1-150
sudo -u ubuntu /usr/local/bin/hermes --config "$C" keys list --chain lightdao-testnet-b 2>&1 | tail -3 | cut -c1-150
