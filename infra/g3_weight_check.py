#!/usr/bin/env python3
"""g3_weight_check.py — G3 gate: payload weight budget + web-root hygiene.
Usage: g3_weight_check.py [ROOT]
Budgets (derived from 2026-10-10 baseline x ~3-4x headroom):
  html page        <= 64 KB   (cur max 14.4 KB)
  non-vendor js    <= 128 KB per file (cur max 44 KB)
  js/vendor total  <= 8 MB    (cur 5.8 MB)
  single image     <= 1.5 MB  (og.png cur 1.37 MB)
  body <img>       <= 300 KB each (LCP guard)
  total non-vendor payload <= 4 MB
  hygiene: no *.pre-* / *.bak / *.orig / *~ served from root, js/, css/
Exit 1 on any fail."""
import glob, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/var/www/lightdao"
KB = 1024
fails = []

def sz(p): return os.path.getsize(p)

# 1. html budget
htmls = glob.glob(os.path.join(ROOT, "*.html"))
for f in htmls:
    if sz(f) > 64 * KB:
        fails.append("html %s %.0fKB > 64KB" % (os.path.basename(f), sz(f) / KB))

# 2. non-vendor js budget
for f in glob.glob(os.path.join(ROOT, "js", "*.js")):
    if sz(f) > 128 * KB:
        fails.append("js %s %.0fKB > 128KB" % (os.path.basename(f), sz(f) / KB))

# 3. vendor total
vt = sum(sz(f) for f in glob.glob(os.path.join(ROOT, "js", "vendor", "**", "*"), recursive=True) if os.path.isfile(f))
if vt > 8 * 1024 * KB:
    fails.append("vendor total %.1fMB > 8MB" % (vt / 1024 / KB))

# 4. images
imgs = []
for pat in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"):
    imgs += glob.glob(os.path.join(ROOT, pat))
for f in imgs:
    if sz(f) > 1536 * KB:
        fails.append("image %s %.0fKB > 1.5MB" % (os.path.basename(f), sz(f) / KB))

# 5. body <img> LCP guard (exclude meta og:image which is crawler-only)
for f in htmls:
    s = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<img[^>]*src="([^"]+)"', s):
        src = m.group(1)
        if src.startswith("http") or src.startswith("data:"):
            continue
        p = os.path.join(ROOT, src.lstrip("/").split("?")[0])
        if os.path.exists(p) and sz(p) > 300 * KB:
            fails.append("%s body img %s %.0fKB > 300KB" % (os.path.basename(f), src, sz(p) / KB))

# 6. total non-vendor payload
total = 0
for base, dirs, files in os.walk(ROOT):
    if "vendor" in base:
        continue
    for fn in files:
        total += sz(os.path.join(base, fn))
if total > 4 * 1024 * KB:
    fails.append("non-vendor total %.1fMB > 4MB" % (total / 1024 / KB))

# 7. hygiene: backup/temp files must not be served
for sub in ("", "js", "css"):
    for pat in ("*.pre-*", "*.bak", "*.orig", "*~", "*.tmp"):
        for f in glob.glob(os.path.join(ROOT, sub, pat)):
            fails.append("served backup/temp file: %s" % os.path.relpath(f, ROOT))

print("G3 html=%d js(non-vendor)=%d vendor=%.1fMB imgs=%d total(non-vendor)=%.1fMB"
      % (len(htmls), len(glob.glob(os.path.join(ROOT, "js", "*.js"))), vt / 1024 / KB, len(imgs), total / 1024 / KB))
if fails:
    print("G3 WEIGHT FAILS: %d" % len(fails))
    for x in fails[:20]: print("  FAIL:", x)
    sys.exit(1)
print("G3 WEIGHT FAILS: 0")
