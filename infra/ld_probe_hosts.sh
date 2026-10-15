#!/bin/bash
# 只读探测：网关到其它主机的可达性（不打印 IP 本身，只打印序号与结果）
HENV=/etc/lightdao/hosts.env
echo "--- 变量名 ---"
sudo grep -oE '^[A-Z_0-9]+=' $HENV 2>/dev/null | sed 's/=$//'
IPS=$(sudo awk -F'"' '/^LD_SCAN_VPS_IPS=/{print $2}' $HENV 2>/dev/null)
if [ -z "$IPS" ]; then
  IPS=$(sudo sed -n 's/^LD_SCAN_VPS_IPS=//p' $HENV 2>/dev/null | tr -d '"'"'" | head -1)
fi
N=$(echo "$IPS" | tr ' ' '\n' | grep -c .)
echo "--- 候选主机数量: $N ---"
echo "--- known_hosts 行数: $(sudo wc -l < ~/.ssh/known_hosts 2>/dev/null || echo 0) ---"
echo "--- 私钥文件（只列名）: $(ls ~/.ssh/ 2>/dev/null | grep -vE 'pub$|known_hosts|authorized_keys' | tr '\n' ' ') ---"
i=0
for ip in $IPS; do
  i=$((i+1))
  if timeout 8 ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 "ubuntu@$ip" true 2>/dev/null; then
    echo "  host#$i -> ssh ubuntu 可达 OK"
  elif timeout 8 ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 "root@$ip" true 2>/dev/null; then
    echo "  host#$i -> ssh root 可达 OK"
  else
    echo "  host#$i -> 不可达/无密钥"
  fi
done
echo "--- 本机内存现状（测试网已停后）---"
free -m | head -2
