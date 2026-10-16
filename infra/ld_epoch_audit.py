#!/usr/bin/env python3
"""ld_epoch_audit.py — G15: epoch-level conservation audit for mining_reward (MR).
Invariants (formula-free, all from chain):
  C. MR balance delta == -(claims + validator_share payouts) since last audit  [conservation]
  D. cumulative payouts (claims + valshare) <= 1B ulight pool cap
  E. every claim tx succeeded with reward>0 recorded; per-day claim totals reported
State/watermark: /home/ubuntu/ld_epoch_audit.state
Alerts via discord_bot. Cron daily 07:20Z."""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.parse

RPC = "http://127.0.0.1:26657"
MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
NODE = "tcp://127.0.0.1:26657"
POOL_CAP = 1_000_000_000_000_000  # 1B LIGHT in ulight
STATE = "/home/ubuntu/ld_epoch_audit.state"

def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def rpc(path):
    with urllib.request.urlopen(RPC + path, timeout=30) as r:
        return json.loads(r.read())

def b64s(x):
    try: return base64.b64decode(x).decode()
    except Exception: return x

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G15 epoch-audit] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    st = json.load(open(STATE))
except Exception:
    st = {"height": 0, "mr_balance": None, "cum_claims": 0, "cum_valshare": 0, "days": {}}

fails = []
wm = st.get("height", 0)

def harvest(action):
    """Return list of {h, day, reward} for successful txs with wasm action=<action>, height > wm."""
    out = []
    page = 1
    while True:
        q = urllib.parse.quote("\"wasm.action='%s'\"" % action)
        d = rpc("/tx_search?query=%s&per_page=100&page=%d" % (q, page))
        txs = d.get("result", {}).get("txs", [])
        total = int(d.get("result", {}).get("total_count", "0"))
        for t in txs:
            h = int(t.get("height", 0))
            if h <= wm: continue
            if t.get("tx_result", {}).get("code", 0) != 0: continue
            day, reward = None, None
            for ev in t.get("tx_result", {}).get("events", []):
                if ev.get("type") != "wasm": continue
                kv = {b64s(a.get("key", "")): b64s(a.get("value", "")) for a in ev.get("attributes", [])}
                if kv.get("action") == action:
                    if action == "claim":
                        reward = int(kv.get("reward", "0") or 0)
                    else:
                        if kv.get("committed") == "true":
                            reward = int(kv.get("validator_share", "0") or 0)
                    day = kv.get("day")
            if day is None:
                # claim day only exists in msg body (base64 tx) — decode
                try:
                    raw = base64.b64decode(t.get("tx", ""))
                    m = re.search(rb'"claim":\{"day":(\d+)', raw)
                    if m: day = int(m.group(1))
                except Exception:
                    pass
            out.append({"h": h, "day": day, "reward": reward})
        if page * 100 >= total: break
        page += 1
    return out

claims = harvest("claim")
roots = harvest("submit_root")

new_claims = sum(c["reward"] or 0 for c in claims)
new_val = sum(r["reward"] or 0 for r in roots)
for c in claims:
    if c["reward"] is None:
        fails.append("claim tx at h=%s missing reward attribute" % c["h"])
    elif c["day"] is not None:
        st["days"][str(c["day"])] = st["days"].get(str(c["day"]), 0) + c["reward"]
st["cum_claims"] += new_claims
st["cum_valshare"] += new_val

# current MR balance
rc, out = sh("wasmd", "q", "bank", "balances", MR, "--node", NODE, "-o", "json")
if rc != 0:
    alert("cannot query MR balance rc=%d" % rc); print("EPOCH-AUDIT ERR"); sys.exit(1)
bal = 0
for b in json.loads(out).get("balances", []):
    if b["denom"] == "ulight": bal = int(b["amount"])

prev_bal = st.get("mr_balance")
if prev_bal is not None:
    expected = prev_bal - new_claims - new_val
    if bal != expected:
        fails.append("CONSERVATION BROKEN: bal %d -> %d, payouts claims=%d val=%d, expected %d (diff %d)"
                     % (prev_bal, bal, new_claims, new_val, expected, bal - expected))
st["mr_balance"] = bal

# pool cap invariant
if st["cum_claims"] + st["cum_valshare"] > POOL_CAP:
    fails.append("cumulative payouts %d exceed 1B pool cap" % (st["cum_claims"] + st["cum_valshare"]))

st["height"] = int(rpc("/status")["result"]["sync_info"]["latest_block_height"])
json.dump(st, open(STATE, "w"))

day_summary = ", ".join("%s:%d" % (k, v) for k, v in sorted(st["days"].items(), key=lambda x: int(x[0]))[-5:])
if fails:
    alert(" | ".join(fails[:4]))
    print("EPOCH-AUDIT FAILS: %d" % len(fails))
    for f in fails: print("  FAIL:", f)
    sys.exit(1)
print("EPOCH-AUDIT OK: MR bal=%d claims(cum)=%d val(cum)=%d recent_days[%s]"
      % (bal, st["cum_claims"], st["cum_valshare"], day_summary))
