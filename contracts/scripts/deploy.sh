#!/usr/bin/env bash
# LightDAO one-click deploy (HARDENED): store 10 + instantiate2 a fully-wired, DAO-controlled set.
# - predictable addresses via `q wasm build-address` (breaks all circular deps)
# - contract admin = governance (DAO-controlled upgrades via proposal+migrate)
# - mining_reward daily root = N-of-M validator multi-sig
# Env: RESET=yes|no  WASM_DIR  VOTING  GENESIS_OFFSET_DAYS  ROOT_THRESHOLD
set -euo pipefail
NODE_BIN=${NODE_BIN:-/home/ubuntu/wasmd60/wasmd}
HOME_DIR=${HOME_DIR:-/home/ubuntu/.wasmd}
RPC=${RPC:-tcp://localhost:26657}
CID=${CID:-lightdao-testnet-1}
KEY=${KEY:-validator}
WASM_DIR=${WASM_DIR:-/home/ubuntu/wasm_v2}
RESET=${RESET:-no}
VOTING=${VOTING:-30}
GENESIS_OFFSET_DAYS=${GENESIS_OFFSET_DAYS:-10}
ROOT_THRESHOLD=${ROOT_THRESHOLD:-2}
BLOCK_WAIT=${BLOCK_WAIT:-7}
NODE="$NODE_BIN --home $HOME_DIR --node $RPC"
OFF="$NODE_BIN --home $HOME_DIR"
KB="--keyring-backend test"
CONTRACTS="light_token mining_reward governance treasury_multisig subtoken_factory oracle_twap anti_fraud validator_registry vesting insurance_fund"

V=$($OFF keys show "$KEY" -a $KB)
for i in 1 2 3 4 5; do $OFF keys add signer$i $KB >/dev/null 2>&1 || true; done
S1=$($OFF keys show signer1 -a $KB); S2=$($OFF keys show signer2 -a $KB); S3=$($OFF keys show signer3 -a $KB)
S4=$($OFF keys show signer4 -a $KB); S5=$($OFF keys show signer5 -a $KB)
echo "deployer=$V  root validators=[$V,$S1,$S2] threshold=$ROOT_THRESHOLD"

if [ "$RESET" = "yes" ]; then
  echo "== reset chain =="
  pkill -x wasmd || true; sleep 3
  $NODE_BIN comet unsafe-reset-all --home "$HOME_DIR" >/dev/null 2>&1
  ( cd /home/ubuntu && nohup $NODE_BIN start --rpc.laddr tcp://0.0.0.0:26657 --home "$HOME_DIR" > /home/ubuntu/wasmd60.log 2>&1 & )
  sleep 9
fi

seq_of(){ $NODE q auth account "$1" --output json 2>/dev/null | grep -aoE '"sequence": "[0-9]+"' | grep -aoE '[0-9]+'; }
SEQ=$(seq_of "$V"); SEQ=${SEQ:-0}

echo "== store 10 (seq from $SEQ) =="
for c in $CONTRACTS; do
  TX=$($NODE tx wasm store "$WASM_DIR/$c.wasm" --from "$KEY" $KB --chain-id "$CID" --sequence $SEQ --gas 6000000 --fees 30000stake -y -b sync --output json 2>&1 | grep -aoE '[A-F0-9]{64}' | head -1)
  SEQ=$((SEQ+1)); sleep $BLOCK_WAIT
  code=$($NODE q tx "$TX" --output json 2>&1 | grep -aoE '"code": ?[0-9]+' | head -1 | grep -aoE '[0-9]+$')
  echo "  store $c -> DeliverTx=$code"; [ "$code" = "0" ] || { echo "STORE FAILED $c"; exit 1; }
done

$NODE q wasm list-code --output json 2>&1 | grep -aoE '"code_id":"[0-9]+","creator":"[^"]*","data_hash":"[A-F0-9]{64}"' > /tmp/codes.txt
i=1; for c in $CONTRACTS; do eval "CID_$c=$i"; i=$((i+1)); done
hash_of(){ grep -aoE "\"code_id\":\"$1\",.*\"data_hash\":\"[A-F0-9]{64}\"" /tmp/codes.txt | grep -aoE '[A-F0-9]{64}'; }
predict(){ local h; h=$(hash_of "$1"); local s; s=$(echo -n "$2" | xxd -ps); $OFF q wasm build-address "$h" "$V" "$s" 2>/dev/null | head -1; }

LT=$(predict $CID_light_token ld_lt);   MR=$(predict $CID_mining_reward ld_mr)
GOV=$(predict $CID_governance ld_gov);  SUB=$(predict $CID_subtoken_factory ld_sub)
ORA=$(predict $CID_oracle_twap ld_ora); AF=$(predict $CID_anti_fraud ld_af)
VR=$(predict $CID_validator_registry ld_vr); VEST=$(predict $CID_vesting ld_vest)
INS=$(predict $CID_insurance_fund ld_ins);   TRE=$(predict $CID_treasury_multisig ld_tre)
GEN=$(( $(date +%s) - GENESIS_OFFSET_DAYS*86400 ))
VP_JSON=$( [ -n "$VOTING" ] && echo "$VOTING" || echo "null" )
cat > /tmp/lightdao_addrs.env <<EOT
LT=$LT
MR=$MR
GOV=$GOV
SUB=$SUB
ORA=$ORA
AF=$AF
VR=$VR
VEST=$VEST
INS=$INS
TRE=$TRE
V=$V
S1=$S1
S2=$S2
GEN=$GEN
CID=$CID
EOT
echo "== predicted addresses =="; cat /tmp/lightdao_addrs.env

echo "== instantiate2 (admin=governance => DAO-controlled upgrades) =="
inst(){ local label=$1 cid=$2 salt=$3 msg=$4
  local sh; sh=$(echo -n "$salt" | xxd -ps)
  local tx; tx=$($NODE tx wasm instantiate2 "$cid" "$msg" "$sh" --label "$label" --admin "$GOV" --from "$KEY" $KB --chain-id "$CID" --sequence $SEQ --gas 3000000 --fees 20000stake -y -b sync --output json 2>&1 | grep -aoE '[A-F0-9]{64}' | head -1)
  SEQ=$((SEQ+1)); sleep $BLOCK_WAIT
  local code; code=$($NODE q tx "$tx" --output json 2>&1 | grep -aoE '"code": ?[0-9]+' | head -1 | grep -aoE '[0-9]+$')
  echo "  instantiate $label (code $cid) -> DeliverTx=$code"; [ "$code" = "0" ] || { echo "INSTANTIATE FAILED $label"; exit 1; }
}
inst validator_registry $CID_validator_registry ld_vr   "{\"light_token\":\"$LT\",\"owner\":\"$GOV\"}"
inst vesting            $CID_vesting            ld_vest "{\"light_token\":\"$LT\",\"owner\":\"$GOV\"}"
inst oracle_twap        $CID_oracle_twap        ld_ora  "{\"validators\":[\"$V\"],\"feeders\":[\"$V\"]}"
inst treasury_multisig  $CID_treasury_multisig  ld_tre  "{\"signers\":[\"$S1\",\"$S2\",\"$S3\",\"$S4\",\"$S5\"]}"
inst anti_fraud         $CID_anti_fraud         ld_af   "{\"mining_reward\":\"$MR\",\"validators\":[\"$V\"]}"
inst light_token        $CID_light_token        ld_lt   "{\"minter\":\"$MR\",\"owner\":\"$GOV\",\"decimals\":6}"
inst mining_reward      $CID_mining_reward      ld_mr   "{\"light_token\":\"$LT\",\"anti_fraud\":\"$AF\",\"genesis_time\":$GEN,\"validators\":[\"$V\",\"$S1\",\"$S2\"],\"root_threshold\":$ROOT_THRESHOLD}"
inst governance         $CID_governance         ld_gov  "{\"light_token\":\"$LT\",\"subtoken_factory\":\"$SUB\",\"proposal_min_stake\":\"1000000000\",\"voting_period_secs\":$VP_JSON}"
inst subtoken_factory   $CID_subtoken_factory   ld_sub  "{\"light_token\":\"$LT\",\"oracle\":\"$ORA\",\"governance\":\"$GOV\"}"
inst insurance_fund     $CID_insurance_fund     ld_ins  "{\"light_token\":\"$LT\",\"governance\":\"$GOV\",\"accrue_source\":\"$SUB\"}"

echo "== final list-code =="
$NODE q wasm list-code --output json 2>&1 | grep -aoE '"code_id":"[0-9]+"' | tr '\n' ' '; echo
echo "DEPLOY OK (addresses in /tmp/lightdao_addrs.env)"
