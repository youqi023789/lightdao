#!/usr/bin/env bash
# LightDAO on-chain self-check (HARDENED). Real transactions.
# Covers: Flow A mining (N-of-M multi-sig root), Flow B governance (custodial stake),
# Flow C subtoken (governance->factory), Flow D generic DAO action (governance->vesting),
# and security regressions. Reads /tmp/lightdao_addrs.env (written by deploy.sh).
set -uo pipefail
NODE_BIN=${NODE_BIN:-/home/ubuntu/wasmd60/wasmd}
HOME_DIR=${HOME_DIR:-/home/ubuntu/.wasmd}
RPC=${RPC:-tcp://localhost:26657}
NODE="$NODE_BIN --home $HOME_DIR --node $RPC"
OFF="$NODE_BIN --home $HOME_DIR"
KB="--keyring-backend test"
source /tmp/lightdao_addrs.env
CID=${CID:-lightdao-testnet-1}
VOTING_WAIT=${VOTING_WAIT:-34}
BLOCK_WAIT=${BLOCK_WAIT:-7}

$OFF keys add miner1 $KB >/dev/null 2>&1 || true
$OFF keys add attacker $KB >/dev/null 2>&1 || true
MINER=$($OFF keys show miner1 -a $KB); ATT=$($OFF keys show attacker -a $KB)
echo "miner1=$MINER"; echo "attacker=$ATT"; echo "signer1=$S1"

# fund gas (native denom = stake)
for pair in "miner1:$MINER:1000000" "attacker:$ATT:500000" "signer1:$S1:300000"; do
  nm=${pair%%:*}; rest=${pair#*:}; addr=${rest%%:*}; amt=${rest##*:}
  $NODE tx bank send validator "$addr" ${amt}stake --from validator $KB --chain-id "$CID" --gas 200000 --fees 5000stake -y -b sync >/dev/null 2>&1; sleep $BLOCK_WAIT
done

send(){ # label from contract msg
  local tx; tx=$($NODE tx wasm execute "$3" "$4" --from "$2" $KB --chain-id "$CID" --gas 1000000 --fees 5000stake -y -b sync --output json 2>&1 | grep -aoE '[A-F0-9]{64}' | head -1)
  sleep $BLOCK_WAIT
  local res; res=$($NODE q tx "$tx" --output json 2>&1)
  local code; code=$(echo "$res" | grep -aoE '"code": ?[0-9]+' | head -1 | grep -aoE '[0-9]+$')
  local rl; rl=$(echo "$res" | grep -aoE '"raw_log": ?"[^"]{0,58}' | head -1)
  printf "[%-28s] code=%s %s\n" "$1" "$code" "$rl"
}
qs(){ $NODE q wasm contract-state smart "$1" "$2" --output json 2>&1 | head -c "${3:-200}"; echo; }

echo "================ FLOW A: mining (2-of-3 multi-sig root) ================"
ROOT=$(python3 - "$MINER" <<'PY'
import hashlib,sys
a=sys.argv[1]; day=0; s=1000000
pre=a.encode()+day.to_bytes(8,"little")+s.to_bytes(16,"little")*4
print(hashlib.sha256(pre).hexdigest())
PY
)
SUBMSG="{\"submit_daily_root\":{\"day\":0,\"root\":\"$ROOT\",\"active_miners\":\"1\",\"total_score\":\"1000000\"}}"
echo "root=$ROOT"
send "A-NEG unauth root"      attacker "$MR" "$SUBMSG"
send "A-NEG future day"       validator "$MR" "{\"submit_daily_root\":{\"day\":99,\"root\":\"$ROOT\",\"active_miners\":\"1\",\"total_score\":\"1000000\"}}"
send "A root vote 1/2 (V)"    validator "$MR" "$SUBMSG"
send "A-NEG claim pre-commit" miner1 "$MR" '{"claim":{"day":0,"proof":[],"score":{"bandwidth":"1000000","session":"1000000","verification":"1000000","stability":"1000000"}}}'
send "A root vote 2/2 (S1)"   signer1 "$MR" "$SUBMSG"
echo -n "RootSubmitted(0)="; qs "$MR" '{"root_submitted":{"day":0}}' 30
send "A-NEG score>1e6"        miner1 "$MR" '{"claim":{"day":0,"proof":[],"score":{"bandwidth":"2000000","session":"0","verification":"0","stability":"0"}}}'
send "A claim(day0)"          miner1 "$MR" '{"claim":{"day":0,"proof":[],"score":{"bandwidth":"1000000","session":"1000000","verification":"1000000","stability":"1000000"}}}'
send "A-NEG double claim"     miner1 "$MR" '{"claim":{"day":0,"proof":[],"score":{"bandwidth":"1000000","session":"1000000","verification":"1000000","stability":"1000000"}}}'
echo -n "miner1 LIGHT: "; qs "$LT" "{\"balance\":{\"address\":\"$MINER\"}}" 70
echo -n "token_info:   "; qs "$LT" '{"token_info":{}}' 140

echo "================ FLOW B: governance (custodial stake) ================"
send "B allowance->gov"         miner1 "$LT"  "{\"increase_allowance\":{\"spender\":\"$GOV\",\"amount\":\"2000000000\"}}"
send "B stake 2000 LIGHT"       miner1 "$GOV" '{"stake":{"amount":"2000000000"}}'
send "B-NEG re-stake(no allow)" miner1 "$GOV" '{"stake":{"amount":"2000000000"}}'
echo -n "StakedBalance(miner1)="; qs "$GOV" "{\"staked_balance\":{\"address\":\"$MINER\"}}" 40
echo -n "gov LIGHT custody=  "; qs "$LT" "{\"balance\":{\"address\":\"$GOV\"}}" 60
send "B create proposal#1" miner1 "$GOV" '{"create_proposal":{"ptype":"vc","title":"Invest CAFE 1M","description":"pilot","symbol":"CAFE","investment_usd":"1000000","target":null,"call_msg":null,"migrate_code_id":null}}'
send "B vote yes #1"     miner1 "$GOV" '{"vote":{"proposal_id":1,"option":"yes","bet":"0"}}'
echo -n "Proposal#1: "; qs "$GOV" '{"proposal":{"id":1}}' 200

echo "================ FLOW D: generic DAO action -> vesting (owner=gov) ================"
CALL=$(printf '%s' "{\"add_schedule\":{\"beneficiary\":\"$MINER\",\"total\":\"1000000000\",\"cliff_secs\":0,\"linear_secs\":100}}" | base64 -w0)
send "D create proposal#2" miner1 "$GOV" "{\"create_proposal\":{\"ptype\":\"micro\",\"title\":\"Fund vesting miner1\",\"description\":\"DAO-approved\",\"symbol\":null,\"investment_usd\":null,\"target\":\"$VEST\",\"call_msg\":\"$CALL\",\"migrate_code_id\":null}}"
send "D vote yes #2"     miner1 "$GOV" '{"vote":{"proposal_id":2,"option":"yes","bet":"0"}}'

echo "================ FLOW C + D execution (wait voting period) ================"
echo -n "AllSubTokens BEFORE="; qs "$SUB" '{"all_sub_tokens":{}}' 40
echo "waiting ${VOTING_WAIT}s..."; sleep $VOTING_WAIT
send "C execute #1 ->subtoken" miner1 "$GOV" '{"execute_proposal":{"proposal_id":1}}'
send "D execute #2 ->vesting"  miner1 "$GOV" '{"execute_proposal":{"proposal_id":2}}'
echo -n "AllSubTokens AFTER="; qs "$SUB" '{"all_sub_tokens":{}}' 40
echo -n "SubToken CAFE: "; qs "$SUB" '{"sub_token":{"symbol":"CAFE"}}' 200
echo -n "vesting Schedule(miner1): "; qs "$VEST" "{\"schedule\":{\"address\":\"$MINER\"}}" 220

echo "================ AUTH-FIX REGRESSIONS ================"
send "NEG slash(non-owner)"       attacker "$VR"   "{\"slash_double_sign\":{\"validator\":\"$V\"}}"
send "NEG addSchedule(non-owner)" attacker "$VEST" "{\"add_schedule\":{\"beneficiary\":\"$ATT\",\"total\":\"1000000\",\"cliff_secs\":0,\"linear_secs\":100}}"
send "NEG voteClaim(non-gov)"     attacker "$INS"  '{"vote_claim":{"claim_id":1,"approve":true,"weight":"999999999"}}'

echo "================ EXPECTED ================"
echo "happy paths => code=0 ; all *-NEG/NEG* => code=5 (reverted)"
echo "miner1 LIGHT>0 ; CAFE subtoken exists ; vesting schedule for miner1 exists"
