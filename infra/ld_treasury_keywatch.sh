#!/bin/bash
# LD-TREASURY-KEYWATCH-20261016
# 不变量：
#   A) 网关上不得存在任何 signer*.info（明文私钥）
#   B) 金库钥匙串条目数必须为 0
#   C) 必须存在至少一份 v2 加密备份密文（防止"密钥既不在机器上、备份也没了"）
#   D) 密文与口令不得同机存放
# 违反 A/B 视为高危（私钥回流），违反 C/D 视为中危。
export PATH=/usr/local/bin:/usr/bin:/bin
ALERTS=/home/ubuntu/ld_alerts.log
STATE=/home/ubuntu/.treasury_keywatch_state
ts=$(date -u +%FT%TZ)
bad=""

n=$(sudo find / -name 'signer*.info' -not -path '/proc/*' 2>/dev/null | wc -l)
[ "$n" -gt 0 ] && bad="$bad 明文私钥文件=$n"

k=$(wasmd keys list --keyring-backend test --home /home/ubuntu/.wasmd 2>/dev/null | grep -c 'name: signer')
[ "$k" -gt 0 ] && bad="$bad 钥匙串signer条目=$k"

e=$(ls -1 /home/ubuntu/backup/treasury-keys-v2-*/*.enc 2>/dev/null | wc -l)
[ "$e" -eq 0 ] && bad="$bad 缺少加密备份密文"

# 密文目录里不得再有明文 keyring，也不得放口令
leak=$(sudo find /home/ubuntu/backup -name '*.info' 2>/dev/null | wc -l)
[ "$leak" -gt 0 ] && bad="$bad 备份目录内含明文=$leak"
pp=$(sudo find /home/ubuntu/backup -iname '*passphrase*' 2>/dev/null | wc -l)
[ "$pp" -gt 0 ] && bad="$bad 口令与密文同机=$pp"

prev=""
[ -f "$STATE" ] && prev=$(cat "$STATE")
if [ -n "$bad" ]; then
  echo "$ts VIOLATION$bad" >> "$ALERTS"
  /usr/bin/python3 /usr/local/bin/discord_bot.py send "[keywatch] 金库密钥不变量被破坏:$bad" >/dev/null 2>&1 || true
  echo "viol" > "$STATE"
  echo "KEYWATCH VIOLATION$bad"; exit 1
fi
if [ "$prev" = "viol" ]; then echo "$ts RECOVERED 金库密钥不变量恢复" >> "$ALERTS"; fi
echo "ok" > "$STATE"
echo "KEYWATCH OK (明文=0 钥匙串=0 密文=$e)"
