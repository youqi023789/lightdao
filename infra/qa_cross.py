#!/usr/bin/env python3
"""qa_cross.py — 跨层一致性门。C1 纪元偏移∈{0,1}(1 为跟踪例外至 10-11);C2 领取窗口真相;
C3 签根日志真实性(以部署基线行号为界, 只查新行); C4 主机TZ==UTC 且 cron 在位; C5 status 异常必有 reason。
退出 0=过(含跟踪例外), 1=FAIL。"""
import json, subprocess, time, urllib.request, re, sys, datetime

GEN = 1789102088
TRACK_UNTIL = datetime.datetime(2026, 10, 11, tzinfo=datetime.timezone.utc).timestamp()
NL = chr(10)
FAILS = []

def rec(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (" | " + d if d else ""))
    if not ok: FAILS.append(n)

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()

def gw(p):
    return json.load(urllib.request.urlopen("http://127.0.0.1:8080" + p, timeout=15))

now = int(time.time())
h = gw("/v1/health"); gwd = h["current_day"]
ctd = (now - GEN) // 86400
off = gwd - ctd
rec("C1 epoch offset gw-contract", off in (0, 1) and (off == 0 or now <= TRACK_UNTIL), "offset=%d tracked-until-10-11" % off)

d = gwd - 1
sub = None
try:
    MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
    out = sh("wasmd q wasm contract-state smart %s '{\"root_submitted\":{\"day\":%d}}' --node tcp://127.0.0.1:26657 -o json" % (MR, d))
    sub = json.loads(out[out.find("{"):]).get("data") is True
except Exception:
    sub = False
fin = gw("/v1/day?day=%d" % d).get("finalized")
if sub and d < ctd: state = "open"
elif sub and d >= ctd: state = "window-tracked"
elif fin and not sub:
    age = now - (h["next_boundary_ts"] - 86400)
    state = "missing-young" if age < 6 * 3600 else "MISSING-OLD"
else:
    state = "not-finalized"
rec("C2 claim-window truth", state != "MISSING-OLD", "day%d fin=%s root=%s state=%s" % (d, fin, sub, state))

try:
    base = int(open("/home/ubuntu/ld_sign.log.baseline").read().strip() or 0)
except Exception:
    base = 0
lines = open("/home/ubuntu/ld_sign.log").read().splitlines()
newlog = NL.join(lines[base:])
old_lie = bool(re.search(r"submitted root for day \d+\s*$", newlog, re.M))
rec("C3 sign-log truthfulness", not old_lie, "lying lines since baseline" if old_lie else "clean since baseline(%d)" % base)
for m in re.finditer(r"SIGN-FAIL day (\d+) code=(\S+)", newlog):
    print("NOTE C3 sign-fail day %s code %s (tracked window)" % (m.group(1), m.group(2)))

tz = sh("date +%Z")
cr = sh("crontab -l | grep -cE 'ld_finalize.sh|ld_sign_root.sh'")
rec("C4 host TZ + crons", tz == "UTC" and int(cr or 0) >= 6, "tz=%s cron_lines=%s" % (tz, cr))

st = json.load(open("/var/www/lightdao/status.json"))
rec("C5 status reason on failure", (st["ok"] is True) or bool(st.get("reason")), "ok=%s reason=%r" % (st["ok"], st.get("reason")))

print("CROSS FAILS: %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
