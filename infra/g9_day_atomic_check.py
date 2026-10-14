#!/usr/bin/env python3
"""g9_day_atomic_check.py — G9 gate: day-file atomicity + corruption recovery.
Imports the real gateway module with an isolated temp GW_DATA and verifies:
  1. save_day produces valid JSON, no tmp litter left behind
  2. 10 threads x 50 concurrent save_day -> final file valid JSON (never partial)
  3. corrupted day_N.json -> load_day returns clean dict AND quarantines .corrupt backup
  4. source uses os.replace (atomic) not truncate-write
Exit 1 on any fail."""
import importlib.util, json, os, shutil, sys, tempfile, threading, time

GW_SRC = "/home/ubuntu/gateway.py"
tmp = tempfile.mkdtemp(prefix="g9day_")
os.environ["GW_DATA"] = tmp
spec = importlib.util.spec_from_file_location("gw_g9", GW_SRC)
gw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw)

fails = []
try:
    # 1. basic save/load roundtrip
    d = {"day": 5, "miners": {"wasm1t": {"bandwidth_kbps": 1}}, "finalized": False}
    gw.save_day(d)
    p = gw.day_path(5)
    if not os.path.exists(p): fails.append("save_day wrote nothing")
    back = gw.load_day(5)
    if back.get("miners", {}).get("wasm1t", {}).get("bandwidth_kbps") != 1:
        fails.append("roundtrip mismatch: %s" % back)
    litter = [f for f in os.listdir(tmp) if ".tmp." in f]
    if litter: fails.append("tmp litter: %s" % litter)

    # 2. concurrent hammer
    def hammer():
        for i in range(50):
            gw.save_day({"day": 6, "miners": {"m%d" % threading.get_ident(): {"bandwidth_kbps": i}}, "finalized": False})
    ts = [threading.Thread(target=hammer) for _ in range(10)]
    [t.start() for t in ts]; [t.join() for t in ts]
    try:
        final = json.load(open(gw.day_path(6)))
        if "miners" not in final: fails.append("hammered file missing miners key")
    except Exception as e:
        fails.append("hammered file unreadable: %s" % e)

    # 3. corruption quarantine
    with open(gw.day_path(7), "w") as f:
        f.write('{"day": 7, "miners": {"a": 1}, "finali')  # truncated mid-write simulation
    rec = gw.load_day(7)
    if rec.get("day") != 7 or rec.get("finalized") is not False:
        fails.append("corrupt day did not return clean default: %s" % rec)
    quarantined = [f for f in os.listdir(tmp) if f.startswith("day_7.json.corrupt.")]
    if not quarantined: fails.append("corrupt file not quarantined (.corrupt backup missing)")
    if os.path.exists(gw.day_path(7)): fails.append("corrupt file still in place after load")

    # 4. source-level atomicity assertion
    src = open(GW_SRC).read()
    if "os.replace(t, p)" not in src: fails.append("save_day not using atomic os.replace")

    # 5. tmp files must not be picked up by /v1/me day listing logic (name check)
    gw.save_day({"day": 8, "miners": {}, "finalized": False})
    with open(gw.day_path(9), "w") as f: f.write("garbage")
    gw.load_day(9)
    dayjsons = [f for f in os.listdir(tmp) if f.startswith("day_") and f.endswith(".json")]
    if len(dayjsons) != 3: fails.append("unexpected day json count: %s" % dayjsons)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("G9 atomic-IO cases done")
if fails:
    print("G9 DAY-ATOMIC FAILS: %d" % len(fails))
    for x in fails: print("  FAIL:", x)
    sys.exit(1)
print("G9 DAY-ATOMIC FAILS: 0")
