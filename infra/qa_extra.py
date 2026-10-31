#!/usr/bin/env python3
"""QA extra: ES-compat scan (old mobile WebViews) + orphan interactive element detection (dead buttons)."""
import glob, os, re, sys

WWW = __import__("os").environ.get("LD_WEB_ROOT", "/var/www/lightdao")
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
    # LD-ES-GATE-ROOT-20261030 原来只扫 /js/*.js，站点根级脚本（passkey-wallet.js、
    # webrtc-relay.js）完全不在范围内——今天用户报的 SyntaxError 就在根级文件里，
    # 门禁全绿。把根级 *.js 一并纳入（vendor 的排除在循环体里已有，不重复写）。
    for f in sorted(glob.glob(WWW + "/js/*.js")) + sorted(glob.glob(WWW + "/*.js")):
        if "/vendor/" in f: continue
        s = open(f, encoding="utf-8").read()
        # LD-ES-COMMENT-20261030 只扫代码行：注释里出现同名标记（例如解释
        # "为什么不能用某个语法"的说明）不是兼容性问题。原实现拿整份文本硬扫，
        # 结果我自己写的注释被判成违规——那种判据只会逼人删掉注释。
        s = "\n".join(l for l in s.splitlines()
                       if not re.match(r"^\s*(//|/\*|\*|<!--)", l))
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
    FAILS_EO = bool(e or o)


def defined_globals():
    """Each page's concatenated js must DEFINE every global it uses from a known critical set."""
    fails = []
    CRIT = ["PAYMASTER", "CFG", "ensureLD", "autoLogin", "startMining", "loadDayCounters", "saveDayCounters", "w1e6", "esc"]
    for pre, pg in PAGE_OF_PREFIX.items():
        js = ""
        for f in glob.glob(WWW + "/js/" + pre + "*.js"):
            js += open(f, encoding="utf-8").read()
        if not js: continue
        for name in CRIT:
            used = re.search(r"\b" + name + r"\b", js)
            defined = re.search(r"(const|let|var|function|async function)\s+" + name + r"\b", js) or (name + "=") in js.replace(" ", "")
            if used and not defined:
                fails.append((pg, name))
    return fails

if __name__ == "__main__":
    dg = defined_globals()
    print("DEFINED-GLOBALS FAILS:", len(dg))
    for x in dg: print("  ", x)
    sys.exit(1 if (dg or globals().get('FAILS_EO')) else 0)
