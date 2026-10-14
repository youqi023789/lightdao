#!/usr/bin/env python3
"""g4_sw_check.py — G4 gate: service worker version == ver.json.
Asserts:
  1. sw.js exists and defines const CACHE = "lightdao-v<N>"
  2. <N> == ver.json v with dots stripped (e.g. 1.3.2 -> lightdao-v132)
     => SW cache is guaranteed to bust on every promote (relabel rewrites it).
  3. every entry in sw.js SHELL array exists on disk.
Exit 1 on any fail."""
import json, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/var/www/lightdao"
swp = os.path.join(ROOT, "sw.js")
vjp = os.path.join(ROOT, "js", "ver.json")
fails = []

if not os.path.exists(swp): print("G4 SW FAILS: 1\n  FAIL: sw.js missing"); sys.exit(1)
sw = open(swp, encoding="utf-8").read()
v = json.load(open(vjp))["v"]
expect = "lightdao-v" + v.replace(".", "")

m = re.search(r'const\s+CACHE\s*=\s*"([^"]+)"', sw)
if not m:
    fails.append('sw.js missing const CACHE = "..."')
else:
    if m.group(1) != expect:
        fails.append("SW CACHE %s != expected %s (ver.json v%s)" % (m.group(1), expect, v))

# SHELL entries exist
for entry in re.findall(r'["\'](/[^"\']*)["\']', sw.split("SHELL")[1].split("]")[0] if "SHELL" in sw else ""):
    if entry.startswith("/js/vendor"):
        ok_prefix = os.path.join(ROOT, "js", "vendor")
    p = os.path.join(ROOT, entry.lstrip("/").split("?")[0])
    if not os.path.exists(p):
        fails.append("SW SHELL entry missing on disk: %s" % entry)

if not re.match(r"^\d+\.\d+\.\d+$", v):
    fails.append("ver.json v=%s not semver" % v)

print("G4 sw CACHE=%s ver.json=%s" % (m.group(1) if m else "?", v))
if fails:
    print("G4 SW FAILS: %d" % len(fails))
    for x in fails: print("  FAIL:", x)
    sys.exit(1)
print("G4 SW FAILS: 0")
