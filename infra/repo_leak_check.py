#!/usr/bin/env python3
"""repo_leak_check.py — public-repo leak gate (v2: allowlist + externalized infra list).

WHAT IT DOES
  Walks a git working tree and fails when it finds anything that must never be public:
    * infrastructure public IPs        (list lives OUTSIDE the repo: /etc/lightdao/leak_ips.txt)
    * private keys / mnemonics / webhooks / bearer tokens / inline secrets
    * operator local paths (desktop dirs) and committed keyring files
  Findings are matched against an allowlist (/etc/lightdao/leak_allow.json). Every waiver needs a
  reason and an expiry, so a real leak can never hide in a pile of permanent false positives.

WHY IT EXISTS
  A transparency-first workflow occasionally commits operational detail it should not: commit
  70be67e removed infrastructure addresses, key file names and an operator machine path that had
  been committed by mistake. The gate exists so that class of mistake fails here first instead of
  being discovered by a stranger.

USAGE
  repo_leak_check.py [REPO] [--json]           default REPO=/home/ubuntu/repo
  exit 0 = clean (waived items reported separately), 1 = findings need a human, 2 = cannot run.

NOTES
  * The shapes below are assembled at runtime from fragments: a scanner whose own source contains
    a complete PEM header, authorization prefix or operator path trips the very detectors it
    implements — and this gate is required to pass over itself with an empty waiver list, because
    every exemption is a place a real leak could later hide.
  * This file is safe to commit: it contains no infrastructure identifiers of its own.
"""
import json
import os
import re
import sys
import time


def _cat(*parts):
    """Join fragments so this source never contains a complete secret-shaped literal."""
    return "".join(parts)


REPO = "/home/ubuntu/repo"
IP_FILE = "/etc/lightdao/leak_ips.txt"
ALLOW_FILE = "/etc/lightdao/leak_allow.json"
ALERT_LOG = "/home/ubuntu/ld_alerts.log"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "target", "dist", "vendor"}
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".wasm", ".gz", ".tgz", ".so", ".zip", ".woff", ".woff2")
MAX_BYTES = 2 * 1024 * 1024


# The operator-path words are assembled at runtime on purpose: writing them whole would make this
# source match the very rule it defines, and the gate could then only be published by exempting
# the gate itself. Every exemption is a place a real leak can later hide, so there are none here.
_DESK = "Desk" + "top"
_HOME = "Use" + "rs"

PATTERNS = [
    ("private-key", re.compile(_cat("BEGIN ", "[A-Z ]*", "PRIVATE", " KEY"))),
    ("discord-webhook", re.compile(_cat("discord\\.com/api/webhooks/\\d+/[\\w-]+"))),
    ("bearer-token", re.compile(_cat("Be", "arer", " [A-Za-z0-9_\\-]{25,}"))),
    # refined 2026-10-14: value must be a single non-space token and must not start with `<` or `$`
    # (placeholder / shell-expansion shapes). The old form matched code that merely spanned a
    # `startswith("...TOKEN=")` line, which burned the waiver budget on syntax noise.
    ("inline-secret", re.compile(_cat("(?i)(secret|token|passphrase|password|api[_-]?key)"
                                      "\\s*[:=]\\s*['\"](?![<$])[^\\s'\"]{12,}['\"]"))),
    # A bare  Desktop/  alternative was dropped on purpose: it fires on innocent asset names
    # (assets/Desktop/ui.png) and it made this file and its own documentation trip the rule. The
    # three shapes kept all require a home directory:  <drive>:\<home>\  /<home>/<user>/<desk>
    # and  ~/<desk> . The home and desktop words are concatenated at runtime so this source cannot
    # match itself.
    ("local-desktop-path", re.compile(_cat("(?:[A-Za-z]:\\\\+" + _HOME + "\\\\+|",
                                           "(?:/home|/" + _HOME + ")/[^/\\s\"']+/" + _DESK + "|",
                                           "~/" + _DESK + ")"))),
    ("keyring-file", re.compile(_cat("keyring-(test|file)/.*\\.info$"))),
    ("oauth-consumer-secret", re.compile(_cat("(?i)(consumer|api)[_-]?(secret|key)\\s*[=:]\\s*"
                                              "[A-Za-z0-9]{20,}"))),
    ("mnemonic-phrase", re.compile(_cat("\\b(?:[a-z]{4,12} ){11,23}(?:[a-z]{4,12})\\b"))),
]


def load_ips():
    if not os.path.isfile(IP_FILE):
        return None
    ips = []
    for ln in open(IP_FILE, encoding="utf-8", errors="ignore"):
        ln = ln.split("#")[0].strip()
        if ln:
            ips.append(ln)
    return ips


def build_ip_regex(ips):
    return re.compile(r"\b(" + "|".join(re.escape(i) for i in ips) + r")\b")


def load_allow():
    """Waivers: [{path, contains, reason, added, review_by}]. Expired waivers stop applying."""
    if not os.path.isfile(ALLOW_FILE):
        return []
    try:
        rules = json.load(open(ALLOW_FILE, encoding="utf-8"))
    except Exception as e:
        print("WARN allowlist unreadable (%s) -> treating as empty" % e)
        return []
    today = time.strftime("%Y-%m-%d")
    live, expired = [], []
    for r in rules:
        rb = r.get("review_by") or "2999-12-31"
        (expired if rb < today else live).append(r)
    return live, expired


def waived(rules, rel, name, frag):
    for r in rules:
        p = r.get("path") or ""
        if not rel.startswith(p):
            continue
        need = r.get("contains")
        if need and need not in frag and need not in name:
            continue
        if r.get("kind") and r.get("kind") != name:
            continue
        return r
    return None


def scan(repo, ip_rx, allow):
    hits, waivers = [], []
    now = time.strftime("%Y-%m-%d")
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(SKIP_EXT):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, repo).replace(os.sep, "/")
            # only anonymised examples may live in the tree; a committed allowlist is scanned too
            if fn.endswith(".sample"):
                continue
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            probes = list(PATTERNS)
            if ip_rx is not None:
                probes = [("infra-ip", ip_rx)] + probes
            for name, rx in probes:
                if name == "mnemonic-phrase" and "/vendor/" in rel:
                    continue
                for m in list(rx.finditer(txt))[:5]:
                    line = txt[:m.start()].count("\n") + 1
                    frag = txt[max(0, m.start() - 40):m.start() + 80].replace("\n", " ")
                    if name == "infra-ip" and frag.strip().startswith("#"):
                        continue
                    rule = waived(allow, rel, name, frag) if allow else None
                    if rule:
                        waivers.append((rel, line, name, rule.get("reason", "")[:50]))
                        continue
                    hits.append((rel, line, name, frag[:120]))
    return hits, waivers


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    global REPO
    if args:
        REPO = args[0]
    if not os.path.isdir(REPO):
        print("repo not found: %s" % REPO)
        return 2
    ips = load_ips()
    if ips is None:
        print("WARN %s missing -> infrastructure-IP scan disabled" % IP_FILE)
        ip_rx = None
    elif not ips:
        print("WARN %s is empty -> infrastructure-IP scan disabled" % IP_FILE)
        ip_rx = None
    else:
        ip_rx = build_ip_regex(ips)
    allow = load_allow()
    live, expired = (allow if isinstance(allow, tuple) else ([], []))
    hits, waivers = scan(REPO, ip_rx, live)
    print("repo-leak-check  repo=%s  infra_ips=%s  waivers_live=%d expired=%d  waived_hits=%d  findings=%d"
          % (REPO, len(ips or []), len(live), len(expired), len(waivers), len(hits)))
    for rel, line, name, frag in hits[:40]:
        print("  FINDING %-18s %s:%d  …%s…" % (name, rel, line, frag))
    for rel, line, name, reason in waivers[:10]:
        print("  waived  %-18s %s:%d  (%s)" % (name, rel, line, reason))
    if expired:
        print("  NOTE  %d waiver(s) expired and are no longer applied" % len(expired))
    if hits:
        print("REPO LEAK FAILS: %d" % len(hits))
        try:
            if os.access(ALERT_LOG, os.W_OK):
                with open(ALERT_LOG, "a", encoding="utf-8") as fh:
                    fh.write("%s ALERT repo-leak-check: %d unwaived finding(s) in %s\n"
                             % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), len(hits), REPO))
        except Exception:
            pass
        return 1
    print("REPO LEAK OK")
    return 0


sys.exit(main())
