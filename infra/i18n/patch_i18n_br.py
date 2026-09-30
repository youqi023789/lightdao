#!/usr/bin/env python3
"""patch_i18n_br.py — fix literal <br> bug in homepage/landing i18n.
Root cause: apply() and the zh baseline capture use el.textContent, which strips
markup on capture and escapes <br> on write. Switch both to innerHTML.
Dict values are trusted build-time strings (no user input) -> innerHTML is safe.
Asserts exactly one replacement per pattern per file; aborts otherwise."""
import io, sys

FILES = [
    "/home/ubuntu/home_candidate/js/index_2.js",
    "/home/ubuntu/home_candidate/js/landing_2.js",
]

# (old, new) — must match exactly once each
CAP_OLD = 'T.zh[el.getAttribute("data-i")]=el.textContent;'
CAP_NEW = 'T.zh[el.getAttribute("data-i")]=el.innerHTML;'
APPLY_OLD = 'var v=d[k]||e2[k];if(v)el.textContent=v;'
APPLY_NEW = 'var v=d[k]||e2[k];if(v)el.innerHTML=v;'

changed_any = False
for p in FILES:
    try:
        t = io.open(p, encoding="utf-8").read()
    except FileNotFoundError:
        print("MISSING (skip):", p); continue
    orig = t
    for old, new, label in [(CAP_OLD, CAP_NEW, "capture"), (APPLY_OLD, APPLY_NEW, "apply")]:
        n = t.count(old)
        if n == 0:
            # already patched?
            if t.count(new) >= 1:
                print("  [%s] %s already patched" % (p, label)); continue
            print("  [%s] %s PATTERN NOT FOUND (count=0) -- ABORT" % (p, label)); sys.exit(2)
        if n != 1:
            print("  [%s] %s pattern count=%d (expected 1) -- ABORT" % (p, label, n)); sys.exit(2)
        t = t.replace(old, new)
        print("  [%s] %s patched (1)" % (p, label))
    if t != orig:
        io.open(p, "w", encoding="utf-8").write(t)
        changed_any = True

print("CHANGED" if changed_any else "NOCHANGE")
