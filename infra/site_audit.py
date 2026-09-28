#!/usr/bin/env python3
"""Full-site link & section audit for lightdao.net (via localhost, Host header)."""
import re, ssl, urllib.request, urllib.parse, sys

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
HOST = "lightdao.net"
PAGES = ["/", "/app.html", "/explorer.html", "/governance.html", "/whitepaper.html",
         "/season.html", "/blog.html", "/privacy.html", "/terms.html", "/landing.html",
         "/zh/", "/en/", "/ja/", "/ar/", "/nodes.html", "/invest.html", "/rss.xml", "/sitemap.xml", "/robots.txt",
         "/humans.txt", "/.well-known/security.txt", "/AUDIT.md", "/og.png", "/manifest.json",
         "/sw.js", "/passkey-wallet.js", "/webrtc-relay.js"]

def get(path):
    _port = __import__("os").environ.get("LD_PORT", "")
    _pre = "https://127.0.0.1:" + _port if _port else "https://127.0.0.1"
    req = urllib.request.Request(_pre + path, headers={"Host": HOST})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

def main():
    dead = []; missing_anchor = []; okc = 0
    page_html = {}
    for p in PAGES:
        st, body = get(p)
        page_html[p] = body
        if st == 200: okc += 1
        else: dead.append((p, st))
    print("pages checked:", len(PAGES), "OK:", okc)
    if dead: print("DEAD PAGES:", dead)
    # internal link check from html pages
    htmlpages = [p for p in PAGES if page_html.get(p, "").startswith("<!DOCTYPE") or page_html.get(p, "").startswith("<html")]
    for p in htmlpages:
        body = page_html[p]
        ids = set(re.findall(r'id="([^"]+)"', body))
        for href in re.findall(r'href="([^"]+)"', body):
            if href.startswith("#"):
                if href[1:] and href[1:] not in ids: missing_anchor.append((p, href))
                continue
            if href.startswith("http") and HOST not in href and "127.0.0.1" not in href:
                continue  # external, skip
            path = href.split("#")[0].split("?")[0]
            if not path or path.startswith("mailto:"): continue
            if not path.startswith("/"): path = "/" + path
            st, _ = get(path)
            if st != 200: dead.append((p + " -> " + href, st))
            # anchor target on linked page
            if "#" in href:
                anc = href.split("#")[1]
                st2, b2 = get(path)
                if st2 == 200 and ('id="%s"' % anc) not in b2: missing_anchor.append((p + " -> " + href, anc))
    print("\nDEAD LINKS:", len(dead))
    for d in dead: print("  ", d)
    print("\nMISSING ANCHORS:", len(missing_anchor))
    for m in missing_anchor: print("  ", m)
    # new sections present on /
    body = page_html.get("/", "")
    need = ["whatis","use","paths","stake","scam","grants","events","gloss","compare","story","sP","sS","sBt"]
    print("\nSECTION/ID CHECK on /:")
    for n in need:
        print("  %-8s %s" % (n, "OK" if ('id="%s"' % n) in body else "MISSING"))
    # nav anchors resolve
    print("\nNAV ANCHORS on /:")
    for a in re.findall(r'href="#([a-z]+)"', body):
        print("  #%-8s %s" % (a, "OK" if ('id="%s"' % a) in body else "MISSING"))
    # placeholder '#' links (known pending: discord/tg/etc)
    ph = re.findall(r'href="#"[^>]*>([^<]*)<', body)
    print("\nPLACEHOLDER '#' LINKS (pending real URLs):", ph)

if __name__ == "__main__":
    main()
