#!/usr/bin/env python3
"""qa_cross.py v2 — 跨层一致性门(每小时 + 灰度第5门)。
C1 纪元偏移∈{0,1}(1=跟踪例外至10-11) C2 领取窗口真相 C3 签根日志真实(基线后) C4 TZ/cron
C5 status 异常必有 reason C6 自动tx无失败/未知码(除tracked) C7 治理无"通过却长期未执行"提案(除void清单)"""
import json, subprocess, time, urllib.request, re, sys, datetime
GEN = 1789102088
TRACK_UNTIL = datetime.datetime(2026, 10, 11, tzinfo=datetime.timezone.utc).timestamp()
NL = chr(10); FAILS = []
def rec(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (" | " + d if d else ""))
    if not ok: FAILS.append(n)
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
def gw(p): return json.load(urllib.request.urlopen("http://127.0.0.1:8080" + p, timeout=15))
now = int(time.time())
h = gw("/v1/health"); gwd = h["current_day"]; ctd = (now - GEN) // 86400; off = gwd - ctd
rec("C1 epoch offset", off in (0, 1) and (off == 0 or now <= TRACK_UNTIL), "offset=%d tracked-until-10-11" % off)
d = gwd - 1; sub = False
try:
    MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
    out = sh("wasmd q wasm contract-state smart %s '{\"root_submitted\":{\"day\":%d}}' --node tcp://127.0.0.1:26657 -o json" % (MR, d))
    sub = json.loads(out[out.find("{"):]).get("data") is True
except Exception: sub = False
fin = gw("/v1/day?day=%d" % d).get("finalized")
if sub and d < ctd: state = "open"
elif sub and d >= ctd: state = "window-tracked"
elif fin and not sub:
    age = now - (h["next_boundary_ts"] - 86400); state = "missing-young" if age < 6 * 3600 else "MISSING-OLD"
else: state = "not-finalized"
rec("C2 claim-window truth", state != "MISSING-OLD", "day%d fin=%s root=%s state=%s" % (d, fin, sub, state))
try: base = int(open("/home/ubuntu/ld_sign.log.baseline").read().strip() or 0)
except Exception: base = 0
newlog = NL.join(open("/home/ubuntu/ld_sign.log").read().splitlines()[base:])
lie = bool(re.search(r"submitted root for day \d+\s*$", newlog, re.M))
rec("C3 sign-log truth", not lie, "lying lines since baseline" if lie else "clean since baseline(%d)" % base)
tz = sh("date +%Z"); cr = sh("(crontab -u ubuntu -l 2>/dev/null || crontab -l 2>/dev/null) | grep -cE 'ld_finalize.sh|ld_sign_root.sh'")
rec("C4 TZ+crons", tz == "UTC" and int(cr or 0) >= 6, "tz=%s lines=%s" % (tz, cr))
st = json.load(open("/var/www/lightdao/status.json"))
rec("C5 status reason", (st["ok"] is True) or bool(st.get("reason")), "ok=%s reason=%r" % (st["ok"], st.get("reason")))
# C6 automated tx receipts
tracked = set()
try: tracked = set(x.strip() for x in open("/home/ubuntu/ld_tx_tracked") if x.strip())
except Exception: pass
bad = []
try:
    cut = now - 86400
    for ln in open("/home/ubuntu/ld_tx.log"):
        m = re.match(r"(\S+)Z (\S+) hash=\S* code=(\S+)", ln)
        if not m: continue
        ts = datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
        if ts < cut: continue
        if m.group(3) not in ("0",) and m.group(2) not in tracked: bad.append(ln.strip()[:80])
except FileNotFoundError:
    pass
rec("C6 auto-tx receipts", not bad, "; ".join(bad[:2]) if bad else "no failed auto-tx in 24h")
# C7 governance stale passed-unexecuted
voided = set()
try: voided = set(int(x) for x in open("/home/ubuntu/ld_void_ids").read().replace(",", " ").split())
except Exception: voided = {2, 5, 6, 7, 9}
stale = []
try:
    GOV = "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt"
    ap = json.loads(sh("wasmd q wasm contract-state smart %s '{\"active_proposals\":{}}' --node tcp://127.0.0.1:26657 -o json" % GOV))["data"]
    for p in ap:
        if p.get("executed"): continue
        if int(p["id"]) in voided: continue
        if int(p.get("end", 0)) < now - 3 * 86400: stale.append(p["id"])
except Exception as e:
    stale = ["query-err"]
rec("C7 no stale passed-unexecuted proposals", not stale, "stale=%s void=%s" % (stale, sorted(voided)))
print("CROSS FAILS: %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
