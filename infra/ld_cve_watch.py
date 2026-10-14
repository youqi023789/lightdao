#!/usr/bin/env python3
"""ld_cve_watch.py — G21: dependency CVE subscription (GitHub Advisories, free API).
Pinned versions -> alert when a published advisory's vulnerable range covers us.
State: /home/ubuntu/ld_cve_watch.state. Cron daily 06:00Z."""
import json, os, re, subprocess, sys, time, urllib.request

PINNED = [
    ("github.com/CosmWasm/wasmvm", "2.2.1"),
    ("github.com/CosmWasm/wasmd", "0.55.0"),
    ("github.com/cosmos/cosmos-sdk", "0.50.12"),
    ("github.com/cometbft/cometbft", "0.38.15"),
    ("npm:@cosmjs/stargate", "0.32.4"),
    ("npm:@cosmjs/cosmwasm-stargate", "0.32.4"),
]
STATE = "/home/ubuntu/ld_cve_watch.state"

def ver_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])

def in_range(ver, rng):
    """rng like '>= 2.1.0, < 2.1.6' or '< 1.5.8'."""
    ver = ver_tuple(ver)
    for part in rng.split(","):
        part = part.strip()
        m = re.match(r"(>=|<=|>|<|==|=)\s*([\d.]+)", part)
        if not m: continue
        op, rv = m.group(1), ver_tuple(m.group(2))
        if op == ">=" and not ver >= rv: return False
        if op == ">" and not ver > rv: return False
        if op == "<=" and not ver <= rv: return False
        if op == "<" and not ver < rv: return False
        if op in ("==", "=") and ver != rv: return False
    return True

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G21 cve-watch] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    st = json.load(open(STATE))
except Exception:
    st = {"acked": []}

def advisories(pkg):
    url = "https://api.github.com/advisories?affects=%s&per_page=100" % urllib.parse.quote(pkg)
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "LightDAO-CVE-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

import urllib.parse
applicable = []
for pkg, ver in PINNED:
    try:
        for a in advisories(pkg):
            for v in a.get("vulnerabilities", []):
                if v.get("package", {}).get("name", "").lower() not in (pkg.split(":")[-1].lower(),):
                    continue
                rng = v.get("vulnerable_version_range") or ""
                if rng and in_range(ver, rng):
                    applicable.append((a["ghsa_id"], pkg, ver, rng, a.get("severity"), a["summary"][:80]))
                    break
    except Exception as e:
        print("WARN: %s query failed: %s" % (pkg, e))

acked = set(st.get("acked", []))
new = [x for x in applicable if x[0] not in acked]
st["acked"] = sorted(set(st.get("acked", [])) | {x[0] for x in applicable})
st["last_run"] = int(time.time())
json.dump(st, open(STATE, "w"))

if new:
    alert("%d NEW applicable advisories: " % len(new) +
          " | ".join("%s %s@%s in %s [%s] %s" % x for x in new[:4]))
    print("CVE-WATCH NEW: %d" % len(new))
    for x in new: print("  -", x)
    sys.exit(1)
print("CVE-WATCH OK: %d packages checked, %d advisories applicable (all acked), 0 new" %
      (len(PINNED), len(applicable)))
