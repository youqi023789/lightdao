#!/usr/bin/env python3
"""sri_integrity.py — Subresource-Integrity helper for the LightDAO release pipeline (N1 fix).

Root-parameterized so it works identically on /var/www/lightdao (main),
/var/www/lightdao_staging (staging) and any candidate dir.

Functions:
  gen_sri(root)          -> regenerate <root>/js/vendor/SRI.json with real per-file sha384
                            over <root>/js/*.js, <root>/js/vendor/*.js, <root>/css/*.css.
  inject_integrity(root) -> idempotently add/refresh integrity= (+crossorigin) on every
                            <script src="/js/.."> and <link .. href="/css/.."> whose path
                            (ignoring ?v= query) is present in the manifest. Tags whose
                            resource is NOT in the manifest are left untouched (never guess).
  verify_integrity(root) -> re-hash every integrity-tagged local resource from disk and
                            assert it equals the tag's integrity value. Returns list of fails.
                            This is authoritative for SRI: the browser compares the hash of the
                            bytes it receives; nginx serves these static files verbatim, so the
                            on-disk hash == served-bytes hash. Any mismatch => would white-screen.

Design rules:
  * Only same-origin /js/ and /css/ references are touched. Inline scripts, external URLs,
    and anything not in the manifest are never given an integrity attribute.
  * crossorigin="anonymous" is added alongside integrity (standard for SRI).
  * Idempotent: re-running replaces the existing integrity/crossorigin rather than duplicating.
"""
import base64, glob, hashlib, json, os, re, sys

def _hash384(path):
    h = hashlib.sha384(open(path, "rb").read()).digest()
    return "sha384-" + base64.b64encode(h).decode()

def gen_sri(root):
    man = {}
    for pat in [root + "/js/*.js", root + "/js/vendor/*.js", root + "/css/*.css"]:
        for f in sorted(glob.glob(pat)):
            if f.endswith("SRI.json"):
                continue
            man["/" + os.path.relpath(f, root)] = _hash384(f)
    out = root + "/js/vendor/SRI.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(json.dumps(man, indent=1))
    return man

# match a script src="/js/....js(?v=..)" or link href="/css/....css(?v=..)" tag
_TAG_RE = re.compile(r'<(script|link)\b[^>]*?>', re.IGNORECASE)
_SRC_RE = re.compile(r'\b(src|href)\s*=\s*"(/(?:js|css)/[^"?]+)(\?[^"]*)?"', re.IGNORECASE)

def _rewrite_tag(tag, man):
    m = _SRC_RE.search(tag)
    if not m:
        return tag, None
    path = m.group(2)              # e.g. /js/app_2.js  (query stripped)
    if path not in man:
        return tag, None           # never guess a hash for an unmanifested resource
    integrity = man[path]
    # drop any pre-existing integrity=/crossorigin= to stay idempotent
    t = re.sub(r'\s+integrity\s*=\s*"[^"]*"', '', tag, flags=re.IGNORECASE)
    t = re.sub(r'\s+crossorigin\s*=\s*"[^"]*"', '', t, flags=re.IGNORECASE)
    # insert before the closing '>' (handles both '<...>' and '<.../>')
    if t.rstrip().endswith("/>"):
        idx = t.rstrip().rfind("/>")
        t = t.rstrip()[:idx].rstrip() + ' integrity="%s" crossorigin="anonymous" />' % integrity
    else:
        idx = t.rstrip().rfind(">")
        t = t.rstrip()[:idx].rstrip() + ' integrity="%s" crossorigin="anonymous">' % integrity
    return t, path

def inject_integrity(root):
    man = json.load(open(root + "/js/vendor/SRI.json"))
    changed = []
    for hp in glob.glob(root + "/**/*.html", recursive=True):
        s = open(hp, encoding="utf-8").read()
        injected = []
        def repl(mo):
            newtag, path = _rewrite_tag(mo.group(0), man)
            if path:
                injected.append(path)
            return newtag
        s2 = _TAG_RE.sub(repl, s)
        if s2 != s:
            open(hp, "w", encoding="utf-8").write(s2)
            changed.append((os.path.relpath(hp, root), len(injected)))
    return changed

_INTEG_RE = re.compile(r'\b(?:src|href)\s*=\s*"(/(?:js|css)/[^"?]+)(?:\?[^"]*)?"[^>]*?\bintegrity\s*=\s*"(sha384-[^"]+)"', re.IGNORECASE)
_INTEG_RE2 = re.compile(r'\bintegrity\s*=\s*"(sha384-[^"]+)"[^>]*?\b(?:src|href)\s*=\s*"(/(?:js|css)/[^"?]+)(?:\?[^"]*)?"', re.IGNORECASE)

def verify_integrity(root):
    fails = []
    checked = 0
    for hp in glob.glob(root + "/**/*.html", recursive=True):
        s = open(hp, encoding="utf-8").read()
        pairs = []
        for m in _INTEG_RE.finditer(s):
            pairs.append((m.group(1), m.group(2)))
        for m in _INTEG_RE2.finditer(s):
            pairs.append((m.group(2), m.group(1)))
        for path, integrity in pairs:
            f = root + path
            if not os.path.exists(f):
                fails.append((hp, path, "missing-file")); continue
            checked += 1
            if _hash384(f) != integrity:
                fails.append((hp, path, "hash-mismatch"))
    return checked, fails

if __name__ == "__main__":
    root = sys.argv[2] if len(sys.argv) > 2 else "/var/www/lightdao"
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "gen":
        m = gen_sri(root); print("gen_sri %s -> %d entries" % (root, len(m)))
    elif cmd == "inject":
        ch = inject_integrity(root)
        print("inject_integrity %s -> %d html changed, %d tags" % (root, len(ch), sum(n for _, n in ch)))
        for f, n in ch: print("   %s: %d" % (f, n))
    elif cmd == "verify":
        c, fails = verify_integrity(root)
        print("verify_integrity %s -> checked=%d fails=%d" % (root, c, len(fails)))
        for x in fails[:40]: print("   FAIL", x)
        sys.exit(1 if fails else 0)
    else:
        print("usage: sri_integrity.py [gen|inject|verify] [root]"); sys.exit(2)
