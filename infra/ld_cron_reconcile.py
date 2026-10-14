#!/usr/bin/env python3
"""ld_cron_reconcile.py — G24: cron jobs vs documented manifest reconciler.
Manifest: /home/ubuntu/repo-push/docs/CRON_MANIFEST.json (public repo, reviewed via PR).
Checks ubuntu + root crontabs on SG against manifest:
  - cron entry present but not in manifest  (undocumented automation = drift)
  - manifest entry not found in crontab     (documented automation missing = silent death)
Alerts via discord_bot. State not needed (pure set-diff). Cron daily 07:30Z."""
import json, re, subprocess, sys

MANIFEST = "/home/ubuntu/repo-push/docs/CRON_MANIFEST.json"

def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G24 cron-reconcile] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

def norm_cmd(cmd):
    """Strip schedule fields (keep command part), normalize spaces, strip env prefixes."""
    parts = cmd.split()
    # skip CRON_TZ / env assignments
    while parts and (re.match(r"^[A-Z_]+=", parts[0]) or parts[0] == "CRON_TZ"):
        parts = parts[1:]
    # cron schedule = 5 fields (or @daily etc = 1 field)
    if parts and parts[0].startswith("@"):
        parts = parts[1:]
    else:
        parts = parts[5:]
    cmd_s = " ".join(parts)
    # normalize redirects/logging
    cmd_s = re.sub(r"\s*>>?\s*\S+", "", cmd_s)
    cmd_s = re.sub(r"\s*2>&1", "", cmd_s)
    cmd_s = re.sub(r"\s+", " ", cmd_s).strip()
    return cmd_s

def user_crons(user):
    rc, out = sh("crontab", "-l", "-u", user)
    if rc != 0: return []
    cmds = []
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        c = norm_cmd(ln)
        if c: cmds.append(c)
    return cmds

live = []
live += ["/root " + c for c in user_crons("root")]
live += ["/ubuntu " + c for c in user_crons("ubuntu")]

if "--gen" in sys.argv:
    seen = []
    for x in sorted(live):
        u, c = x.split(" ", 1)
        if x not in seen:
            seen.append(x)
            print(json.dumps({"user": u[1:], "cmd": c}))
    print("# manifest entries above; wrap into CRON_MANIFEST.json {\"jobs\":[...]}", file=sys.stderr)
    sys.exit(0)


try:
    man = json.load(open(MANIFEST))
    expected = ["/%s %s" % (e["user"], e["cmd"]) for e in man.get("jobs", [])]
except Exception as e:
    alert("manifest unreadable: %s" % e); print("CRON-RECONCILE ERR manifest"); sys.exit(1)

def base(s): return re.sub(r"\s+", " ", s.strip())

live_b = {base(x) for x in live}
exp_b = {base(x) for x in expected}
undoc = [x for x in sorted(live_b) if x not in exp_b]
missing = [x for x in sorted(exp_b) if x not in live_b]

if undoc or missing:
    msg = []
    if undoc: msg.append("UNDOCUMENTED (%d): %s" % (len(undoc), "; ".join(undoc[:5])))
    if missing: msg.append("MISSING FROM CRONTAB (%d): %s" % (len(missing), "; ".join(missing[:5])))
    alert(" | ".join(msg))
    print("CRON-RECONCILE DRIFT: undoc=%d missing=%d" % (len(undoc), len(missing)))
    for x in undoc: print("  UNDOC:", x)
    for x in missing: print("  MISSING:", x)
    sys.exit(1)
print("CRON-RECONCILE OK: %d jobs match manifest" % len(live_b))
