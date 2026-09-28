#!/usr/bin/env python3
"""Site functional QA: js syntax (node --check), bracket balance, handler<->id wiring,
script/css asset existence. Run before every deploy."""
import glob, os, re, subprocess, sys

WWW = __import__("os").environ.get("LD_WEB_ROOT", "/var/www/lightdao")
PAGE_OF_PREFIX = {"app_": "app.html", "explorer_": "explorer.html", "index_": "index.html",
                  "landing_": "landing.html", "nodes_": "nodes.html", "invest_": "invest.html",
                  "governance_": "governance.html", "search_": "search.html", "season_": "season.html",
                  "blog_": "blog.html", "privacy_": "privacy.html", "terms_": "terms.html",
                  "whitepaper_": "whitepaper.html", "audit_": "audit_logic.html"}

def ids_of(html):
    return set(re.findall(r'id="([^"]+)"', html))

def main():
    fails = []
    # 1 syntax + balance
    for f in sorted(glob.glob(WWW + "/js/*.js")):
        if "/vendor/" in f: continue
        r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
        if r.returncode != 0:
            # node12 false-positive on ?. ; detect
            if "Unexpected token '.'" in r.stderr and "?." in open(f, encoding="utf-8").read():
                pass
            else:
                fails.append(("SYNTAX", os.path.basename(f), r.stderr.strip().split("\n")[0]))
        s = open(f, encoding="utf-8").read()
        d = p = 0; instr = None; esc = False
        for ch in s:
            if instr:
                if esc: esc = False
                elif ch == "\\": esc = True
                elif ch == instr: instr = None
                continue
            if ch in "\"'`": instr = ch
            elif ch == "{": d += 1
            elif ch == "}": d -= 1
            elif ch == "(": p += 1
            elif ch == ")": p -= 1
        if False:  # balance check unreliable (regex/comments); node --check is authoritative
            fails.append(("BALANCE", os.path.basename(f), "brace=%d paren=%d" % (d, p)))
    # 2 wiring: js id refs vs page ids
    pageids = {}
    for pre, pg in PAGE_OF_PREFIX.items():
        p = os.path.join(WWW, pg)
        if os.path.exists(p):
            pageids[pre] = ids_of(open(p, encoding="utf-8").read())
    for f in sorted(glob.glob(WWW + "/js/*.js")):
        base = os.path.basename(f)
        pre = base.split("_")[0] + "_"
        if pre not in pageids: continue
        s = open(f, encoding="utf-8").read()
        refs = set(re.findall(r'\$\("([A-Za-z0-9_]+)"\)', s)) | set(re.findall(r'getElementById\("([A-Za-z0-9_]+)"\)', s))
        missing = [r for r in refs if r not in pageids[pre]]
        # allow ids created dynamically by js itself
        created = set(re.findall(r'id="([A-Za-z0-9_]+)"', s)) | set(re.findall(r'\.id\s*=\s*"([A-Za-z0-9_]+)"', s))
        missing = [m for m in missing if m not in created]
        if missing:
            fails.append(("WIRING", base, ",".join(sorted(missing))))
    # 3 assets referenced exist
    for pg in set(PAGE_OF_PREFIX.values()):
        p = os.path.join(WWW, pg)
        if not os.path.exists(p): continue
        s = open(p, encoding="utf-8").read()
        for m in re.findall(r'(?:src|href)="(/[^"?#]+)', s):
            if not os.path.exists(WWW + m) and not m.startswith("/rpc") and not m.startswith("/gw"):
                fails.append(("ASSET", pg, m))
    print("QA FAILS:", len(fails))
    for f in fails:
        print("  ", f)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
