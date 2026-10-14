#!/usr/bin/env python3
"""ld_secret_scan.py — G18: secret leak scan (public repo, web root, gateway logs, ops scripts).
Patterns: private keys, GitHub/AWS/Slack/Discord tokens, VPS IPs, password assignments.
Alerts on NEW findings (state dedup). Cron weekly Mon 05:00Z + on-demand.
State: /home/ubuntu/ld_secret_scan.state"""
import hashlib, json, os, re, subprocess, sys

PATHS = ["/home/ubuntu/repo-push", "/var/www/lightdao",
         "/home/ubuntu/lightdao_gateway/clienterr.log"]
EXTRA_GLOBS = ["/home/ubuntu/*.py", "/home/ubuntu/*.sh", "/home/ubuntu/*.json",
               "/usr/local/bin/*.py", "/usr/local/bin/*.sh"]
SKIP_DIRS = {".git", "node_modules", "vendor", "lightdao_js_archive", "lightdao_js_prev", "lightdao_staging"}
SKIP_FILES = {"ld_secret_scan.py"}
STATE = "/home/ubuntu/ld_secret_scan.state"

PATTERNS = [
    ("privkey", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----")),
    ("gh-token", re.compile(r"gh[posu]_[A-Za-z0-9]{20,}")),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("discord-bot-token", re.compile(r"[MNO][A-Za-z0-9_-]{22,26}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{25,}")),
    ("password-assign", re.compile(r"(?i)(password|passwd|secret)\s*[=:]\s*['\"][^'\"{}<>\s]{8,}['\"]")),
]
# 地址来自侧车 /etc/lightdao/hosts.env（脚本因此可以公开入库）。
# 读不到就抛错停摆：一个"静默什么都不扫"的扫描器比报错更危险。
def _load_hosts(p="/etc/lightdao/hosts.env"):
    kv = {}
    try:
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln: continue
            k, v = ln.split("=", 1); kv[k] = v.strip('"')
    except IOError:
        raise SystemExit("缺少 %s：拒绝以空清单继续扫描" % p)
    return kv
VPS_IPS = _load_hosts()["LD_SCAN_VPS_IPS"].split()

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[G18 secret-scan] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    st = json.load(open(STATE))
except Exception:
    st = {}

files = []
for p in PATHS:
    if os.path.isfile(p):
        files.append(p)
    elif os.path.isdir(p):
        for base, dirs, fns in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in fns:
                if fn in SKIP_FILES or fn.endswith((".jpg", ".png", ".webp", ".wasm", ".zip", ".pem")):
                    continue
                files.append(os.path.join(base, fn))
import glob
for g in EXTRA_GLOBS:
    for f in glob.glob(g):
        if os.path.isfile(f) and os.path.basename(f) not in SKIP_FILES:
            files.append(f)

hits = []
scanned = 0
for f in files:
    try:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            for i, ln in enumerate(fh, 1):
                scanned += 1
                for name, rx in PATTERNS:
                    if rx.search(ln):
                        hits.append("%s|%s|%s:%d" % (name, hashlib.sha1(ln.strip().encode()).hexdigest()[:10], f, i))
                        break
                for ip in VPS_IPS:
                    if ip in ln and "127.0.0.1" not in ln and "localhost" not in ln:
                        hits.append("vps-ip|%s:%d" % (f, i))
                        break
    except Exception:
        pass

new = []
for h in hits:
    if h not in st:
        st[h] = 1
        new.append(h)
json.dump(st, open(STATE, "w"))

if new:
    alert("%d NEW secret-pattern hits (first 5): %s" % (len(new), "; ".join(new[:5])))
    print("SECRET-SCAN NEW HITS: %d" % len(new))
    for h in new[:20]: print("  HIT:", h)
    sys.exit(1)
print("SECRET-SCAN OK: %d files, %d lines, %d known-hits, 0 new" % (len(files), scanned, len(hits)))
