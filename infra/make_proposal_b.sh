#!/bin/bash
# make_proposal_b.sh — 在 A 执行后运行: 观测真实 code_id + 校验 sha + 生成 B
set -e
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
WANT=9e0dc33866396d34e4a151d67d6e6504e1de91f27a53aad6805fd961ffcced6a
TEMPLATE=/home/ubuntu/gov_migration_B_migrate_TEMPLATE.json
OUTPUT=/home/ubuntu/gov_migration_B_migrate.json

ID=$(wasmd q wasm list-code --node tcp://127.0.0.1:26657 -o json | python3 -c "import sys,json;cs=json.load(sys.stdin)['code_infos'];print(max(int(c['code_id']) for c in cs))")
# [fix 2026-10-02] this wasmd's `q wasm code-info` returns a TOP-LEVEL "checksum" (uppercase hex),
# not {"code_info":{"data_hash":...}}. The old parse raised KeyError and (set -e) aborted before the
# sha-gate ever ran, so Part B was never generated. Accept both shapes; normalize to lowercase.
GOT=$(wasmd q wasm code-info $ID --node tcp://127.0.0.1:26657 -o json | python3 -c "import sys,json;d=json.load(sys.stdin);ci=d.get('code_info',d);h=(ci.get('data_hash') or ci.get('checksum') or d.get('checksum') or d.get('data_hash') or '');print(str(h).lower())")
echo "latest code_id=$ID data_hash=$GOT"
[ -n "$GOT" ] || { echo "ABORT: could not read code checksum (empty) — refusing to build Part B blind"; exit 2; }
[ "$GOT" = "$WANT" ] || { echo "ABORT: sha mismatch (possible code-id shift attack or wrong upload)"; exit 2; }

# [guard 2026-10-02] metadata must be <=255 chars (gov module limit on this chain)
META_LEN=$(python3 -c "import json;print(len(json.load(open('$TEMPLATE')).get('metadata','')))")
if [ "$META_LEN" -gt 255 ]; then
  echo "ABORT: template metadata=${META_LEN} chars > gov limit 255. Shorten it before submitting."
  exit 2
fi
echo "metadata length OK ($META_LEN <= 255)"

python3 - "$ID" <<'PY'
import json, sys
cid = sys.argv[1]
B = json.load(open("/home/ubuntu/gov_migration_B_migrate_TEMPLATE.json"))
B["messages"][0]["code_id"] = cid
json.dump(B, open("/home/ubuntu/gov_migration_B_migrate.json", "w"), indent=2, ensure_ascii=False)
print("wrote gov_migration_B_migrate.json with code_id", cid)
PY
