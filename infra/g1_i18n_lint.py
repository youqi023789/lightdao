#!/usr/bin/env python3
"""g1_i18n_lint.py v4 — G1 gate: i18n key coverage check.
Matches key:" or "key":" or key:' or "key":" in JS dicts.
Exit 1 on missing keys or missing locale blocks."""
import re, sys, glob, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/var/www/lightdao"
LOCALES = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id"]

# Extract data-i keys from HTML
html_keys = {}
for f in glob.glob(os.path.join(ROOT, "*.html")):
    content = open(f, encoding="utf-8").read()
    for k in re.findall(r'data-i="([^"]+)"', content):
        html_keys.setdefault(k, []).append(os.path.basename(f))

# Load all JS i18n content
js_blob = ""
for f in glob.glob(os.path.join(ROOT, "js", "*_2.js")):
    js_blob += open(f, encoding="utf-8").read()

# A key is covered if it appears as key:" or "key":" or key:' etc.
missing = {}
for k, files in html_keys.items():
    # Match: key:" or "key":" or key:' or "key":'
    if not re.search(r'(?<![a-zA-Z0-9_])["\']?' + re.escape(k) + r'["\']?\s*:\s*["\']', js_blob):
        missing[k] = files

# Locale block presence
locales_missing = [loc for loc in LOCALES if not re.search(loc + r':\{', js_blob)]

print("HTML data-i keys: %d" % len(html_keys))
print("Missing in JS dicts: %d" % len(missing))
for k in sorted(missing)[:10]:
    print("  MISSING: %s (used in %s)" % (k, ",".join(missing[k][:3])))
print("Locales missing: %s" % (locales_missing or "none"))

fails = len(missing) + len(locales_missing)
if fails:
    print("I18N-LINT FAILS: %d" % fails)
    sys.exit(1)
print("I18N-LINT FAILS: 0")
