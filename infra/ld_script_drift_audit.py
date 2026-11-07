#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_script_drift_audit.py — read-only audit: is the code the gateway actually runs in the repo?

Why (found by the 2026-11-07 hourly patrol): ld_i18n_validate.js had been edited in place under
/usr/local/bin on 2026-11-04 (MT-table dead-row exemption) and the infra/ copy never caught up,
while that same file is a release gate invoked by the promote checks. A gate that verifies a
version nobody runs is a gate that verifies nothing.

Contract: NEVER writes to /usr/local/bin or the repo, never touches git state, never deletes,
never restarts anything. Pure read + hash + report.

Exit 0 = every scheduled script is versioned and byte-identical to its repo copy.
Exit 1 = findings (DRIFT / UNVERSIONED-RUNNING / UNREADABLE).
Exit 2 = cannot run (repo missing) -- loud, never silently "clean".

Relationship to ld_gate_watch.py (deliberate overlap, different surface): gate-watch checks the
~20 published release gates against the deployed manifest and is green (checked=20 drift=0) even
while ld_i18n_validate.js -- which promote.py actually invokes -- sits outside that manifest and
had drifted. This audit covers every non-backup script in BIN whose name appears in a crontab or
in the repo, so the "gate nobody runs" class of bug has a second, independent net.

Scheduling note: if this ever goes into a crontab, add the line with
/usr/local/bin/ld_cron_add_safe.py (append-only, refuses when the line count drops).
Do not edit crontabs with `A && B || C` chains. Run under sudo only to widen hashing coverage:
0600 root-only files degrade to UNREADABLE / EACCES, never to a false DRIFT.
"""
import hashlib
import os
import re
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo"
BIN = sys.argv[2] if len(sys.argv) > 2 else "/usr/local/bin"
CRON_DIR = "/var/spool/cron/crontabs"
EXTS = (".sh", ".py", ".js")
SKIP = re.compile(r"(\.bak|\.pre-|\.orig|~$|\.example$)")
NAME_RE = re.compile(r"/(?:usr/local/bin|home/ubuntu)/([\w.\-]+\.(?:sh|py|js))")
SUDO = ["/usr/bin/sudo", "-n"] if os.path.exists("/usr/bin/sudo") else []


def sha(path):
    """Hash a file. 0600 root-only ops scripts (keyrings backups, voter tooling) are normal here,
    so a PermissionError is never reported as drift: retry through `sudo -n sha256sum`, and if
    that is unavailable, report UNREADABLE instead of inventing a finding."""
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except PermissionError:
        pass
    except OSError:
        return "MISSING"
    if SUDO:
        try:
            r = subprocess.run(SUDO + ["sha256sum", path], capture_output=True,
                               text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.split()[0]
        except Exception:
            pass
    return "EACCES"


def scheduled_names(tracked):
    """Names that are demonstrably in service: referenced by a crontab, or named inside a repo
    file. Anything here that is missing from the repo is a real hole, not a stray one-shot tool."""
    names = set()
    try:
        users = os.listdir(CRON_DIR)
    except OSError:
        users = []
    for user in users:
        try:
            with open(os.path.join(CRON_DIR, user), "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith("#"):
                        continue
                    names.update(NAME_RE.findall(line))
        except OSError:
            continue
    for rel in tracked:
        if not rel.endswith((".sh", ".py", ".js", ".md", ".json", ".yml", ".yaml", ".txt")):
            continue
        try:
            with open(os.path.join(REPO, rel), "r", encoding="utf-8", errors="replace") as fh:
                names.update(NAME_RE.findall(fh.read()))
        except OSError:
            continue
    return names


if not os.path.isdir(os.path.join(REPO, ".git")):
    print("SCRIPT-DRIFT AUDIT NOT IN EFFECT: repo not found at %s" % REPO)
    sys.exit(2)

tracked = {}
res = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, timeout=180)
if res.returncode != 0:
    print("SCRIPT-DRIFT AUDIT NOT IN EFFECT: git ls-files failed: %s" % res.stderr.strip()[:160])
    sys.exit(2)
for rel in res.stdout.splitlines():
    tracked.setdefault(os.path.basename(rel), []).append(rel)

scheduled = scheduled_names(tracked)
findings = []
checked = 0
for name in sorted(os.listdir(BIN)):
    src = os.path.join(BIN, name)
    if not name.endswith(EXTS) or SKIP.search(name) or not os.path.isfile(src):
        continue
    checked += 1
    hits = tracked.get(name, [])
    if not hits:
        if name in scheduled:
            findings.append(("UNVERSIONED-RUNNING", name,
                             "in service but no repo copy exists"))
        else:
            findings.append(("UNVERSIONED-idle", name,
                             "not referenced anywhere; probably a one-shot tool"))
        continue
    rel = hits[0]
    a, b = sha(src), sha(os.path.join(REPO, rel))
    if a == "EACCES" or b == "EACCES":
        findings.append(("UNREADABLE", name,
                         "cannot hash live or %s without root; re-run under sudo" % rel))
    elif a != b:
        findings.append(("DRIFT", name, "live %s != repo %s" % (a[:12], b[:12])))

live = [f for f in findings if f[0] in ("UNVERSIONED-RUNNING", "DRIFT", "UNREADABLE")]
print("script-drift-audit repo=%s bin=%s scanned=%d in_service_names=%d tracked=%d"
      % (REPO, BIN, checked, len(scheduled), len(tracked)))
for kind, name, note in findings:
    print("  %-20s %-34s %s" % (kind, name, note))
if live:
    print("SCRIPT DRIFT FAILS: %d finding(s) needing a human" % len(live))
    sys.exit(1)
print("SCRIPT DRIFT OK: every scheduled /usr/local/bin script is byte-identical to its repo copy")
sys.exit(0)
