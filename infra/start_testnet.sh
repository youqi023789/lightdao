#!/usr/bin/env bash
# LightDAO §4.5 lightfee testnet rehearsal — single validator on SG VPS.
# Independent home + ports so the running mainnet wasmd (26657) is untouched.
set -euo pipefail

LIGHTD=/home/ubuntu/lightd
HOME_DIR=/home/ubuntu/.lightd-testnet
CHAIN_ID=lightdao-testnet-gas
MONIKER=val-test-gas
DENOM=stake
# Fixed treasury addr for observation (bech32 derived from a fresh key below).
KEYRING=test

# Ports (mainnet uses 26657/26656/9090/9091/1317)
RPC_PORT=26757
P2P_PORT=26758
GRPC_PORT=9190
GRPC_WEB_PORT=9191
API_PORT=1417
PROM_PORT=26760

echo "== 清理旧测试目录 =="
rm -rf "$HOME_DIR"

echo "== init =="
"$LIGHTD" init "$MONIKER" --chain-id "$CHAIN_ID" --home "$HOME_DIR" --default-denom "$DENOM" >/dev/null

echo "== 配置端口 + gas =="
sed -i "s|^laddr = \"tcp://127.0.0.1:26657\"|laddr = \"tcp://0.0.0.0:${RPC_PORT}\"|" "$HOME_DIR/config/config.toml"
sed -i "s|^laddr = \"tcp://0.0.0.0:26656\"|laddr = \"tcp://0.0.0.0:${P2P_PORT}\"|" "$HOME_DIR/config/config.toml"
sed -i "s|^prometheus_listen_addr = \":26660\"|prometheus_listen_addr = \":${PROM_PORT}\"|" "$HOME_DIR/config/config.toml"
sed -i 's|^timeout_commit = ".*"|timeout_commit = "2s"|' "$HOME_DIR/config/config.toml"
sed -i 's|^minimum-gas-prices = ".*"|minimum-gas-prices = "0.0001stake"|' "$HOME_DIR/config/app.toml"
sed -i "s|^address = \"tcp://0.0.0.0:1317\"|address = \"tcp://0.0.0.0:${API_PORT}\"|" "$HOME_DIR/config/app.toml"
sed -i "s|^address = \"0.0.0.0:9090\"|address = \"0.0.0.0:${GRPC_PORT}\"|" "$HOME_DIR/config/app.toml"
sed -i "s|^address = \"0.0.0.0:9091\"|address = \"0.0.0.0:${GRPC_WEB_PORT}\"|" "$HOME_DIR/config/app.toml"
sed -i 's|^enable = false$|enable = true|' "$HOME_DIR/config/app.toml" || true

echo "== 生成测试账户 =="
"$LIGHTD" keys add validator --home "$HOME_DIR" --keyring-backend "$KEYRING" --output json > /tmp/val.json 2>&1
"$LIGHTD" keys add alice     --home "$HOME_DIR" --keyring-backend "$KEYRING" --output json > /tmp/alice.json 2>&1
"$LIGHTD" keys add treasury  --home "$HOME_DIR" --keyring-backend "$KEYRING" --output json > /tmp/treasury.json 2>&1

VAL_ADDR=$(python3 -c "import json; print(json.load(open('/tmp/val.json'))['address'])")
ALICE_ADDR=$(python3 -c "import json; print(json.load(open('/tmp/alice.json'))['address'])")
TREAS_ADDR=$(python3 -c "import json; print(json.load(open('/tmp/treasury.json'))['address'])")
echo "validator: $VAL_ADDR"
echo "alice:     $ALICE_ADDR"
echo "treasury:  $TREAS_ADDR"

echo "== genesis: 给 alice 充足余额 =="
"$LIGHTD" genesis add-genesis-account "$ALICE_ADDR" 1000000000000stake --home "$HOME_DIR" 2>&1 | tail -3 || \
"$LIGHTD" add-genesis-account "$ALICE_ADDR" 1000000000000stake --home "$HOME_DIR"

echo "== gentx =="
"$LIGHTD" genesis gentx validator 1000000000stake --chain-id "$CHAIN_ID" --home "$HOME_DIR" --keyring-backend "$KEYRING" 2>&1 | tail -3 || \
"$LIGHTD" gentx validator 1000000000stake --chain-id "$CHAIN_ID" --home "$HOME_DIR" --keyring-backend "$KEYRING"

"$LIGHTD" genesis collect-gentxs --home "$HOME_DIR" 2>&1 | tail -3 || \
"$LIGHTD" collect-gentxs --home "$HOME_DIR"

echo "== 启动测试节点(后台, 5 秒块间隔) =="
export LIGHTDAO_DENOM="$DENOM"
export LIGHTDAO_STATIC_PRICE_USD="0.05"
export LIGHTDAO_TREASURY_ADDR="$TREAS_ADDR"
export LIGHTDAO_TRANSFER_USD="0.001"

mkdir -p /home/ubuntu/lightd-testnet-logs
nohup "$LIGHTD" start --home "$HOME_DIR" \
  --rpc.laddr "tcp://0.0.0.0:${RPC_PORT}" \
  --p2p.laddr "tcp://0.0.0.0:${P2P_PORT}" \
  --grpc.address "0.0.0.0:${GRPC_PORT}" \
  --grpc-web.address "0.0.0.0:${GRPC_WEB_PORT}" \
  > /home/ubuntu/lightd-testnet-logs/node.log 2>&1 &
NODE_PID=$!
echo "node pid=$NODE_PID"
echo "$NODE_PID" > /tmp/lightd-testnet.pid
echo "$TREAS_ADDR" > /tmp/lightd-treasury.addr
echo "$ALICE_ADDR" > /tmp/lightd-alice.addr

echo "== 等待 5 个块 =="
for i in $(seq 1 30); do
  sleep 2
  H=$("$LIGHTD" status --node "tcp://127.0.0.1:${RPC_PORT}" 2>&1 | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('\n',1)[1] if 'WARN' in sys.stdin.read()[:200] else sys.stdin.read()); print(d.get('sync_info',{}).get('latest_block_height','0'))" 2>/dev/null || echo 0)
  echo "  height=$H"
  if [ "${H:-0}" -ge 5 ]; then
    break
  fi
done

echo "== 测试网就绪 =="
echo "RPC:  tcp://127.0.0.1:${RPC_PORT}"
echo "PID:  $NODE_PID"
