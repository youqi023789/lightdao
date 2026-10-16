#!/usr/bin/env python3
"""wp_reconcile.py — G22: daily whitepaper-vs-chain parameter reconciliation."""
import json, subprocess, sys, datetime

MAIN = "tcp://127.0.0.1:26657"
LT = "wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z"
MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
VS = "wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x"
GV = "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt"

def q(contract, msg):
    r = subprocess.run(["wasmd","q","wasm","contract-state","smart",contract,
        json.dumps(msg),"--node",MAIN,"-o","json"],
        capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)["data"]

checks = []
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

ti = q(LT, {"token_info":{}})
checks.append(("total_supply==2.5B", int(ti["total_supply"]) == 2_500_000_000_000_000))

pool = q(MR, {"pool_balance":{}})
checks.append(("mining_pool<=1B", int(pool) <= 1_000_000_000_000_000))

vv = int(q(VS, {"vault_balance":{}}))
checks.append(("vesting_vault<=250M", vv <= 250_000_000_000_000))

ei = q(MR, {"epoch_info":{}})
checks.append(("daily_release==684932", int(ei["daily_release"]) == 684_931_506_848))
checks.append(("epoch==1", ei["epoch"] == 1))

try:
    gc = q(GV, {"config":{}})
    checks.append(("proposal_min_stake==5000L", int(gc["proposal_min_stake"]) == 5_000_000_000))
except Exception:
    checks.append(("proposal_min_stake", False))

try:
    md = json.loads(subprocess.run(["wasmd","q","bank","denom-metadata","ulight","--node",MAIN,"-o","json"],
        capture_output=True, text=True, timeout=30).stdout)
    checks.append(("bank_symbol==LIGHT", md["metadata"]["symbol"] == "LIGHT"))
except Exception:
    checks.append(("bank_symbol", False))

fails = [name for name, ok in checks if not ok]
all_ok = len(fails) == 0
print("%s wp-reconcile: %d/%d PASS %s" % (now, len(checks)-len(fails), len(checks),
      "| ALL OK" if all_ok else "| FAIL: " + ",".join(fails)))

if not all_ok:
    subprocess.run(["python3","/usr/local/bin/discord_bot.py","send",
        "WP-RECONCILE FAIL: %s" % ",".join(fails)],
        capture_output=True, timeout=30)
sys.exit(0 if all_ok else 1)
