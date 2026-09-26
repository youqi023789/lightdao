#!/usr/bin/env python3
"""QA extra: ES-compat scan (old mobile WebViews) + orphan interactive element detection (dead buttons)."""
import glob, os, re, sys

WWW = "/var/www/lightdao"
PAGE_OF_PREFIX = {"app_": "app.html", "explorer_": "explorer.html", "index_": "index.html",
                  "landing_": "landing.html", "nodes_": "nodes.html", "invest_": "invest.html",
                  "governance_": "governance.html", "search_": "search.html", "season_": "season.html",
                  "blog_": "blog.html", "privacy_": "privacy.html", "terms_": "terms.html",
                  "whitepaper_": "whitepaper.html", "audit_": "audit_logic.html"}
MODERN = [("?.", "optional-chaining"), ("??", "nullish"), ("catch{", "optional-catch"),
          (".at(", "Array.at"), ("replaceAll", "replaceAll"), ("structuredClone", "structuredClone"),
          ("globalThis", "globalThis")]

def es_compat():
    fails = []
    for f in sorted(glob.glob(WWW + "/js/*.js")):
        if "/vendor/" in f: continue
        s = open(f, encoding="utf-8").read()
        for pat, name in MODERN:
            if pat in s:
                fails.append((os.path.basename(f), name))
    return fails

def orphans():
    fails = []
    for pre, pg in PAGE_OF_PREFIX.items():
        p = os.path.join(WWW, pg)
        if not os.path.exists(p): continue
        h = open(p, encoding="utf-8").read()
        js = ""
        for f in glob.glob(WWW + "/js/" + pre + "*.js"):
            js += open(f, encoding="utf-8").read()
        # buttons with id
        for m in re.finditer(r'<button[^>]*id="([A-Za-z0-9_]+)"[^>]*>', h):
            bid = m.group(1)
            tag = m.group(0)
            handled = (bid in js)
            if not handled:
                fails.append((pg, "button#" + bid, "no handler"))
        # anchors with id but no href/data-go/data-back
        for m in re.finditer(r'<a[^>]*id="([A-Za-z0-9_]+)"[^>]*>', h):
            aid = m.group(1)
            tag = m.group(0)
            if 'href=' not in tag and 'data-go' not in tag and 'data-back' not in tag:
                handled = ('$("#%s")' % aid) in js or ('getElementById("%s")' % aid) in js
                if not handled:
                    fails.append((pg, "a#" + aid, "no href & no handler"))
    return fails

if __name__ == "__main__":
    e = es_compat(); o = orphans()
    print("ES-COMPAT FAILS:", len(e))
    for x in e: print("  ", x)
    print("ORPHAN INTERACTIVE FAILS:", len(o))
    for x in o: print("  ", x)
    sys.exit(1 if (e or o) else 0)
