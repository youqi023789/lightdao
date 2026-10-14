#!/usr/bin/env python3
"""g2_a11y_check.py — G2 gate: static accessibility assertions.
Usage: g2_a11y_check.py [ROOT]   (default /var/www/lightdao)
Checks (per page scope):
  ALL pages   : html lang=, <title>, meta description, <img> alt=, meta viewport
  PAGED pages : skip-link, :focus-visible CSS, select#lang aria-label
Exit 1 on any fail."""
import re, sys, glob, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/var/www/lightdao"
# all pages must carry the a11y baseline (skip-link, focus-visible, lang-aria)

fails = []
pages = sorted(f for f in glob.glob(os.path.join(ROOT, "*.html")) if not os.path.basename(f).startswith("404-"))
if not pages:
    print("G2: no html pages found under %s" % ROOT); sys.exit(1)

for f in pages:
    name = os.path.basename(f)
    s = open(f, encoding="utf-8").read()
    def chk(cond, msg):
        if not cond: fails.append("%s: %s" % (name, msg))
    chk(re.search(r'<html[^>]*\slang="', s), "missing html lang=")
    chk(re.search(r"<title>[^<]{3,}</title>", s), "missing/empty <title>")
    chk('name="description"' in s, "missing meta description")
    chk('name="viewport"' in s, "missing meta viewport")
    # img alt (skip tracking pixels with width 1)
    for m in re.finditer(r'<img([^>]*)>', s):
        attrs = m.group(1)
        if 'alt=' not in attrs:
            fails.append("%s: <img> without alt: %s" % (name, m.group(0)[:80]))
    chk(re.search(r'class="skip"[^>]*href="#', s) or re.search(r'href="#[^"]*"[^>]*class="skip"', s), "missing skip-link")
    chk(":focus-visible" in s, "missing :focus-visible CSS")
    if 'id="lang"' in s:
        chk(re.search(r'<select[^>]*id="lang"[^>]*aria-label=', s) or re.search(r'aria-label=[^>]*id="lang"', s), "select#lang missing aria-label")

print("G2 pages checked: %d" % len(pages))
if fails:
    print("G2 A11Y FAILS: %d" % len(fails))
    for x in fails[:20]: print("  FAIL:", x)
    sys.exit(1)
print("G2 A11Y FAILS: 0")
