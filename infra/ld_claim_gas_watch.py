#!/usr/bin/env python3
"""ld_claim_gas_watch.py — G16: claim gas drift monitor.
From tx_search (all wasm.action='claim'):
  - recent claim gas_used stats (last N claims)
  - alert if: any gas_used > 280000 (approaching 300k canary limit)
             avg drifted >20% vs stored baseline
             a failed claim tx (code!=0, esp. out-of-gas) appears
State: /home/ubuntu/ld_claim_gas.state. Cron daily 07:25Z."""
import base64, json, re, subprocess, sys, time, urllib.request, urllib.parse

RPC = "http://127.0.0.1:26657"
STATE = "/home/ubuntu/ld_claim_gas.state"
LIMIT_WARN = 280000
DRIFT_PCT = 20.0

def rpc(path):
    with urllib.request.urlopen(RPC + path, timeout=30) as r:
        return json.loads(r.read())

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G16 gas-watch] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    st = json.load(open(STATE))
except Exception:
    st = {}

fails = []
page = 1
txs = []
while True:
    q = urllib.parse.quote("\"wasm.action='claim'\"")
    d = rpc("/tx_search?query=%s&per_page=100&page=%d&order_by=\"asc\"" % (q, page))
    res = d.get("result", {})
    txs += res.get("txs", [])
    total = int(res.get("total_count", "0"))
    if page * 100 >= total: break
    page += 1

recent = txs[-30:]
gases = [int(t.get("tx_result", {}).get("gas_used", "0")) for t in recent]
failed = [t for t in recent if t.get("tx_result", {}).get("code", 0) != 0]

if gases:
    avg = sum(gases) // len(gases)
    mx = max(gases)
    prev = st.get("avg")
    if mx > LIMIT_WARN:
        fails.append("claim gas_used max=%d exceeds warn %d" % (mx, LIMIT_WARN))
    if prev and abs(avg - prev) * 100.0 / prev > DRIFT_PCT:
        fails.append("claim gas drift: avg %d vs baseline %d (+%.0f%%)" % (avg, prev, (avg - prev) * 100.0 / prev))
    else:
        st["avg"] = avg
    st["last_max"] = mx
if failed:
    fails.append("%d failed claim txs in last 30 (codes=%s)" %
                 (len(failed), ",".join(str(t["tx_result"]["code"]) for t in failed[:5])))

json.dump(st, open(STATE, "w"))
if fails:
    alert(" | ".join(fails[:4]))
    print("GAS-WATCH FAILS: %d" % len(fails))
    for f in fails: print("  FAIL:", f)
    sys.exit(1)
print("GAS-WATCH OK: %d claims sampled, avg gas=%d max=%d" % (len(gases), sum(gases)//max(len(gases),1), max(gases) if gases else 0))
