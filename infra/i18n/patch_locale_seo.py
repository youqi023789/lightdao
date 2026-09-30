#!/usr/bin/env python3
"""patch_locale_seo.py — refresh the 14 SEO redirect stubs' <title>/og:title/description
to the NEW localized brand line (captured live into /home/ubuntu/locale_seo.json).
Run with sudo (stubs are root-owned). Asserts each stub exists; skips desc if empty."""
import io, json, os, re, sys

SEO = json.load(io.open("/home/ubuntu/locale_seo.json", encoding="utf-8"))
ROOT = "/var/www/lightdao"
LOCS = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id"]


def esc_text(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_attr(s):
    return esc_text(s).replace('"', "&quot;")


patched = 0
for loc in LOCS:
    p = os.path.join(ROOT, loc, "index.html")
    if not os.path.isfile(p):
        print("MISSING stub: %s -- ABORT" % p); sys.exit(2)
    info = SEO.get(loc) or {}
    title = (info.get("title") or "").strip()
    desc = (info.get("desc") or "").strip()
    if not title:
        print("no title for %s -- ABORT" % loc); sys.exit(2)
    t = io.open(p, encoding="utf-8").read()
    orig = t
    t = re.sub(r"<title>.*?</title>", "<title>%s</title>" % esc_text(title), t, count=1, flags=re.S)
    t = re.sub(r'(<meta property="og:title" content=").*?(")', lambda m: m.group(1) + esc_attr(title) + m.group(2), t, count=1)
    if desc:
        t = re.sub(r'(<meta property="og:description" content=").*?(")', lambda m: m.group(1) + esc_attr(desc) + m.group(2), t, count=1)
        t = re.sub(r'(<meta name="description" content=").*?(")', lambda m: m.group(1) + esc_attr(desc) + m.group(2), t, count=1)
    if t != orig:
        io.open(p, "w", encoding="utf-8").write(t)
        patched += 1
        print("  [%s] title updated" % loc)
    else:
        print("  [%s] no change" % loc)
print("PATCHED %d/%d stubs" % (patched, len(LOCS)))
