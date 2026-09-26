#!/usr/bin/env bash
# Build all 10 contracts with rustc 1.85 and normalize to MVP (strip reference-types).
# Output: $OUT/*.wasm  (ready for `wasmd tx wasm store`)
set -euo pipefail
export PATH="$PATH:$HOME/.cargo/bin"
SRC=${SRC:-/home/ubuntu/lightdao-chain}
OUT=${OUT:-/home/ubuntu/wasm_v2}
TARGET_DIR=${TARGET_DIR:-/home/ubuntu/wasmbuild_v2}
CONTRACTS="light_token mining_reward governance treasury_multisig subtoken_factory oracle_twap anti_fraud validator_registry vesting insurance_fund"

echo "== [1/2] cargo build (rustc 1.85, wasm32-unknown-unknown) =="
cd "$SRC"
CARGO_TARGET_DIR="$TARGET_DIR" cargo +1.85.0 build --release --target wasm32-unknown-unknown

echo "== [2/2] wasm-opt --mvp-features -O3 (CRITICAL: strips reference-types for wasmer4) =="
mkdir -p "$OUT"
for c in $CONTRACTS; do
  wasm-opt --mvp-features -O3 "$TARGET_DIR/wasm32-unknown-unknown/release/$c.wasm" -o "$OUT/$c.wasm"
  printf "  %-20s %8s bytes  %s\n" "$c" "$(stat -c%s "$OUT/$c.wasm")" "$(sha256sum "$OUT/$c.wasm" | cut -c1-16)"
done
echo "done -> $OUT"
