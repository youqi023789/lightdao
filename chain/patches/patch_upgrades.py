#!/usr/bin/env python3
"""
Patch wasmd app/upgrades.go to register the v2-lightfee upgrade handler.

lightfee has no dedicated KV store, so a noop handler (RunMigrations only) is
sufficient — it lets the chain pass the upgrade height after the binary swap.
Idempotent.
"""
import sys
from pathlib import Path

P = Path("/home/ubuntu/wasmd-src/app/upgrades.go")
s = P.read_text()

old = 'var Upgrades = []upgrades.Upgrade{v050.Upgrade}'
new = 'var Upgrades = []upgrades.Upgrade{v050.Upgrade, noop.NewUpgrade("v2-lightfee")}'

if new in s:
    print("[skip] v2-lightfee already registered")
elif old in s and s.count(old) == 1:
    P.write_text(s.replace(old, new, 1))
    print("[ok] registered v2-lightfee upgrade handler")
else:
    print(f"[FAIL] anchor count={s.count(old)}")
    sys.exit(2)
