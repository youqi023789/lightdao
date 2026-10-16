#!/usr/bin/env python3
"""ld_validator_watch.py — G13: validator health alert.
  - jailed / unbonding status (x/staking query)
  - missed blocks: real commit-signature scan of last 50 blocks (version-independent,
    works around CLI signing-info missing missed_blocks_counter on SDK 0.50.12)
  - jailed_until in future (from signing-infos list)
Alerts via discord_bot; dedup per issue 6h. State: /home/ubuntu/ld_valwatch.state"""
import json, os, subprocess, sys, time, urllib.request

NODE = "tcp://127.0.0.1:26657"
RPC = "http://127.0.0.1:26657"
STATE = "/home/ubuntu/ld_valwatch.state"
WINDOW = 50
MISS_WARN_PCT = 10.0
MISS_CRIT_PCT = 30.0

def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def rpc(path):
    with urllib.request.urlopen(RPC + path, timeout=15) as r:
        return json.loads(r.read())["result"]

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G13 val-watch] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    state = json.load(open(STATE))
except Exception:
    state = {}

issues = []   # (kind, key, desc)
try:
    # ---- validator set (address -> moniker/power) ----
    vs = rpc("/validators?per_page=100")
    vmap = {}
    for v in vs.get("validators", []):
        vmap[v["address"]] = (v.get("pub_key", {}).get("value", "")[:16], int(v.get("voting_power", "0")))
    # ---- jailed / status via staking ----
    rc, out = sh("wasmd", "q", "staking", "validators", "--node", NODE, "-o", "json")
    if rc != 0 or '"validators"' not in out:
        alert("cannot query staking validators: rc=%d out=%.200s" % (rc, out))
        print("VALWATCH ERR query"); sys.exit(1)
    n_val = 0
    for v in json.loads(out)["validators"]:
        n_val += 1
        mon = v.get("description", {}).get("moniker", "?")
        op = v.get("operator_address", "?")
        if v.get("jailed"):
            issues.append(("jailed", op, "%s JAILED" % mon))
        elif v.get("status") != "BOND_STATUS_BONDED":
            issues.append(("status", op, "%s status=%s" % (mon, v.get("status"))))
    # ---- jailed_until via signing-infos list ----
    rc, si = sh("wasmd", "q", "slashing", "signing-infos", "--node", NODE, "-o", "json")
    if rc == 0:
        try:
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            for it in json.loads(si).get("info", []):
                ju = it.get("jailed_until", "1970-01-01T00:00:00Z")
                if ju > "1970-01-01" and ju > now_iso:
                    issues.append(("jailed_until", it.get("address", "?"), "%s jailed_until=%s" % (it.get("address", "?"), ju)))
        except Exception:
            pass
    # ---- missed blocks: scan last WINDOW block commits ----
    tip = int(rpc("/status")["sync_info"]["latest_block_height"])
    miss = {a: 0 for a in vmap}
    counted = 0
    for h in range(tip - WINDOW + 1, tip + 1):
        if h < 1: continue
        try:
            sigs = rpc("/commit?height=%d" % h)["signed_header"]["commit"]["signatures"]
        except Exception:
            continue
        counted += 1
        signed = set()
        for s in sigs:
            if s.get("block_id_flag") == 2 and s.get("validator_address"):
                signed.add(s["validator_address"])
        for a in miss:
            if a not in signed:
                miss[a] += 1
    if counted >= 30:
        for a, m in miss.items():
            if m == 0: continue
            pct = 100.0 * m / counted
            tag = vmap.get(a, (a[:12], 0))[0]
            if pct >= MISS_CRIT_PCT:
                issues.append(("missed_crit", a, "val %s missed %d/%d blocks (%.0f%%)" % (tag, m, counted, pct)))
            elif pct >= MISS_WARN_PCT:
                issues.append(("missed_warn", a, "val %s missed %d/%d blocks (%.0f%%)" % (tag, m, counted, pct)))
    else:
        issues.append(("noscan", "noscan", "only %d commits scanned (node syncing?)" % counted))
except Exception as e:
    issues.append(("exception", "exc", "probe exception: %s" % e))

now = time.time()
fired = []
for kind, key, desc in issues:
    sig = "%s|%s" % (kind, key)
    if state.get(sig, 0) < now - 6 * 3600:
        fired.append(desc)
        state[sig] = now
# clear dedup for resolved issues (>1h old) so re-occurrence re-alerts
live = set("%s|%s" % (k, key) for k, key, _d in issues)
for sig in list(state):
    if sig not in live and now - state.get(sig, 0) > 3600:
        state.pop(sig, None)
json.dump(state, open(STATE, "w"))

if fired:
    alert(" | ".join(fired[:6]))
    print("VALWATCH ALERTS: %d" % len(fired))
    for f in fired: print("  -", f)
    sys.exit(1)
print("VALWATCH OK: %d validators, %d commits scanned, 0 issues" % (n_val if n_val else len(vmap), counted if 'counted' in dir() else 0))
