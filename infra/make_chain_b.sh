#!/usr/bin/env bash
# LD-IBC-CHAIN-B-20261105  在本机起第二条 LightDAO 测试链（chain B），
# 目的：跨链（IBC）要拿"真交易"当证据，就必须有一对能互相建轻客户端的链。
# 对外链（osmo-test-5）需要对方手续费与外部水龙头、还要别人配合建通道，本机说不上话；
# 自己起第二条链做对手端，IBC 全流程（客户端/连接/通道/转账/回执）都在我们掌控内跑通，
# 这才是"具备跨链交易功能"的可复核证据。
#
# 安全边界：只新建目录与新端口，绝不碰主网节点、也不动现有测试网 A 的数据目录。
set -euo pipefail
BIN=/home/ubuntu/lightd.testnet.bin
A=/home/ubuntu/.lightd-testnet
B=/home/ubuntu/.lightd-testnet-b
CHAIN_B=lightdao-testnet-b
KEY=Bval
STAKE_HOME=/home/ubuntu/.lightd-testnet-b

# 上一次跑到一半会留下半个目录；先挪开再重建（只移动、不删除，随时可回退）
if [ -d "$STAKE_HOME" ]; then sudo mv "$STAKE_HOME" "$STAKE_HOME.bak-$(date -u +%H%M%S)"; echo "已挪开上次残留"; fi

# 端口：A 用 26757(RPC)/26758(P2P)/26658(ABCI)/9190(gRPC)/1317(API)
RPC_PORT=26957; P2P_PORT=26958; ABCI_PORT=26959; GRPC_PORT=9191; API_PORT=1319

sudo -u ubuntu "$BIN" init ibc-chain-b --home "$B" --chain-id "$CHAIN_B" >/dev/null
sudo -u ubuntu "$BIN" keys add "$KEY" --home "$B" --keyring-backend test >/dev/null 2>&1 || true
ADDR=$(sudo -u ubuntu "$BIN" keys show "$KEY" -a --home "$B" --keyring-backend test)
echo "B 验证者账户：$ADDR"

# 复用 A 的链参数（同一份二进制、同样的模块与 denom），但换 chain_id、加 funded 账户
python3 - "$A" "$B" "$CHAIN_B" "$ADDR" <<'PYEOF'
import json, sys
A, B, cid, addr = sys.argv[1:5]
g = json.load(open(A + "/config/genesis.json"))
g["chain_id"] = cid
cp = g.get("consensus_params") or g.get("consensus") or {}
cp.setdefault("block", {})["max_gas"] = "50000000"
g["consensus_params"] = cp
st = g["app_state"]
# 清空 A 的验证者/质押/治理状态，改成 B 自己的一枚验证者
st["staking"]["validators"] = []
st["staking"]["delegations"] = []
st["staking"]["last_power"] = 0
st["genutil"]["gen_txs"] = []
st["bank"]["balances"] = [{"address": addr, "coins": [{"denom": "stake", "amount": "500000000000"}]}]
st["bank"]["supply"] = [{"denom": "stake", "amount": "500000000000"}]
if "auth" in st:
    st["auth"]["accounts"] = [a for a in st.get("auth", {}).get("accounts", []) if a.get("@type", "").endswith("BaseAccount")]
    st["auth"]["accounts"].append({"@type": "/cosmos.auth.v1beta1.BaseAccount", "address": addr, "pub_key": None, "account_number": "0", "sequence": "0"})
for key in ("crisis", "evidence", "slashing"):
    st.get(key, {}).pop("signed_blocks_window", None)
st.setdefault("ibc", {})
st["ibc"].setdefault("client_genesis", {})["clients"] = []
st["ibc"]["client_genesis"]["next_client_sequence"] = "0"
st["ibc"]["connection_genesis"] = {"connections": [], "client_connection_paths": [], "next_connection_sequence": "0", "params": {"max_expected_time_per_block": "30000000000"}}
st["ibc"]["channel_genesis"] = {"channels": [], "acknowledgements": [], "commitments": [], "receipts": [], "send_sequences": [], "recv_sequences": [], "ack_sequences": [], "next_channel_sequence": "0"}
json.dump(g, open(B + "/config/genesis.json", "w"), indent=1)
print("B genesis 已生成：chain_id=%s funded=%s" % (cid, addr))
PYEOF

# 端口与跨域
sudo -u ubuntu python3 - "$B" "$ABCI_PORT" "$RPC_PORT" "$P2P_PORT" "$API_PORT" "$GRPC_PORT" <<'PYEOF'
import re, sys
B, abci, rpc, p2p, api, grpc = sys.argv[1:7]
p = B + "/config/config.toml"
t = open(p).read()
t = re.sub(r'proxy_app = "tcp://127\.0\.0\.1:\d+"', 'proxy_app = "tcp://127.0.0.1:%s"' % abci, t)
t = re.sub(r'laddr = "tcp://0\.0\.0\.0:\d+"', lambda m: m.group(0), t)
# 依次替换：第一个 laddr 是 RPC，第二个是 P2P
parts = t.split('laddr = "tcp://0.0.0.0:26657"')
if len(parts) == 1:
    parts = t.split('laddr = "tcp://127.0.0.1:26657"')
t = ('laddr = "tcp://0.0.0.0:%s"' % rpc).join(parts)
parts = t.split('laddr = "tcp://0.0.0.0:26656"')
if len(parts) > 1:
    t = ('laddr = "tcp://0.0.0.0:%s"' % p2p).join(parts)
t = t.replace('cors_allowed_origins = []', 'cors_allowed_origins = ["*"]')
open(p, "w").write(t)

p2 = B + "/config/app.toml"
t2 = open(p2).read()
t2 = re.sub(r'address = "tcp://0\.0\.0\.0:\d+"', 'address = "tcp://0.0.0.0:0"', t2, count=1)
t2 = t2.replace('enable = true\n\n[grpc-web]', 'enable = false\n\n[grpc-web]')
t2 = re.sub(r'(\[grpc\][\s\S]*?enable = )true', r'\1true', t2)
t2 = re.sub(r'address = "0\.0\.0\.0:\d+"', 'address = "0.0.0.0:%s"' % grpc, t2, count=1)
t2 = re.sub(r'address = "tcp://0\.0\.0\.0:\d+"', 'address = "tcp://0.0.0.0:%s"' % api, t2, count=1)
open(p2, "w").write(t2)
print("B 端口已改：rpc=%s p2p=%s abci=%s grpc=%s api=%s" % (rpc, p2p, abci, grpc, api))
PYEOF

# 建验证者并写进 genesis
sudo -u ubuntu "$BIN" keys show "$KEY" -a --home "$B" --keyring-backend test >/dev/null
VALOPER=$(sudo -u ubuntu "$BIN" tendermint show-validator --home "$B")
sudo -u ubuntu "$BIN" genesis add-genesis-account "$ADDR" 300000000000stake --home "$B" --keyring-backend test 2>/dev/null \
  || sudo -u ubuntu "$BIN" add-genesis-account "$ADDR" 300000000000stake --home "$B" --keyring-backend test
sudo -u ubuntu "$BIN" genesis gentx "$KEY" 200000000000stake --chain-id "$CHAIN_B" --home "$B" --keyring-backend test \
  --moniker ibc-chain-b --commission-rate 0.05 --commission-max-rate 0.20 --commission-max-change-rate 0.01 \
  --min-self-delegation 1 2>/dev/null \
  || sudo -u ubuntu "$BIN" gentx "$KEY" 200000000000stake --chain-id "$CHAIN_B" --home "$B" --keyring-backend test \
       --moniker ibc-chain-b --commission-rate 0.05 --commission-max-rate 0.20 --commission-max-change-rate 0.01 --min-self-delegation 1
(sudo -u ubuntu "$BIN" genesis collect-gentxs --home "$B" 2>/dev/null || sudo -u ubuntu "$BIN" collect-gentxs --home "$B") >/dev/null
echo "B 验证者：$VALOPER"

cat > /etc/systemd/system/lightd-testnet-b.service <<EOF
[Unit]
Description=LightDAO IBC counterpart testnet (chain B)
After=network-online.target
[Service]
User=ubuntu
ExecStart=$BIN start --home $STAKE_HOME --rpc.laddr tcp://0.0.0.0:$RPC_PORT --p2p.laddr tcp://0.0.0.0:$P2P_PORT
Environment=LIGHTDAO_DENOM=stake
Environment=LIGHTDAO_STATIC_PRICE_USD=0.05
Environment=LIGHTDAO_TRANSFER_USD=0.001
Restart=on-failure
RestartSec=5
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now lightd-testnet-b
sleep 14
timeout 15 curl -s http://127.0.0.1:$RPC_PORT/status | head -c 240
echo
echo "B 已启动（RPC :$RPC_PORT）"
