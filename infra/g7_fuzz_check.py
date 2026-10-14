#!/usr/bin/env python3
"""g7_fuzz_check.py — G7 gate: gateway negative/abuse fuzz.
Spawns an ISOLATED gateway instance (port 8095, temp data dir) from
/home/ubuntu/gateway.py, throws malformed/abusive traffic at it, asserts:
  - every request gets a valid HTTP response (no hang/reset)
  - zero 5xx
  - 429 rate limiting engages under hammering
  - /v1/finalize requires admin secret (403 without)
  - service healthy at start and end
Exit 1 on any fail."""
import json, os, shutil, signal, subprocess, sys, tempfile, time
import urllib.request, urllib.error

GW_SRC = "/home/ubuntu/gateway.py"
PORT = 8095
BASE = "http://127.0.0.1:%d" % PORT

tmp = tempfile.mkdtemp(prefix="g7fuzz_")
env = dict(os.environ, GW_PORT=str(PORT), GW_DATA=tmp, GW_ADMIN_SECRET="g7-test-secret",
           GW_GENESIS="1789084800")
proc = subprocess.Popen(["python3", GW_SRC], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
fails = []

def req(method, path, body=None, headers=None, timeout=8):
    url = BASE + path
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method,
                               headers=headers or {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return None, str(e).encode()

def case(name, method, path, body=None, headers=None, expect_lt=500, note=""):
    st, _ = req(method, path, body, headers)
    ok = st is not None and st < expect_lt
    if not ok:
        fails.append("%s: status=%s %s" % (name, st, note))
    return st

def wait_up():
    for _ in range(40):
        st, b = req("GET", "/v1/health")
        if st == 200: return True
        time.sleep(0.25)
    return False

try:
    if not wait_up():
        fails.append("gateway instance did not start")
    else:
        # ---- valid baseline ----
        case("health", "GET", "/v1/health")
        case("day-valid", "GET", "/v1/day?day=0")
        # POSITIVE proof path (regression guard: 2026-10-10 proof 502 outage was
        # missed because fuzz only exercised malformed inputs)
        MINER = "wasm1fuzzaaa111111111111111111111111111111111"
        st, body = req("POST", "/v1/heartbeat",
                       {"miner": MINER, "day": 1, "bandwidth_kbps": 100, "session_secs": 60,
                        "verification_tasks": 1, "stability_pct": 100, "fp": "fuzzfp1"})
        # finalize day 1 with admin secret so /v1/proof has a finalized day with proofs
        st, _ = req("POST", "/v1/finalize", {"day": 1}, headers={"X-Admin": "g7-test-secret"})
        st, body = req("GET", "/v1/proof?day=1&miner=" + MINER)
        if st != 200:
            fails.append("proof-VALID path broken: status=%s body=%.100s" % (st, body))
        else:
            try:
                pj = json.loads(body)
                # single-miner tree yields a VALID empty proof array; score must be a non-empty dict
                if not isinstance(pj.get("proof"), list) or not pj.get("score"):
                    fails.append("proof-VALID missing proof/score fields")
            except Exception as e:
                fails.append("proof-VALID bad json: %s" % e)
        case("hb-valid", "POST", "/v1/heartbeat",
             {"miner": MINER, "day": 1,
              "bandwidth_kbps": 100, "session_secs": 60, "verification_tasks": 1, "stability_pct": 100,
              "fp": "fuzzfp1"})
        # ---- malformed bodies ----
        case("hb-bad-json", "POST", "/v1/heartbeat", b"{not json", expect_lt=500)
        case("hb-array-body", "POST", "/v1/heartbeat", [1, 2, 3], expect_lt=500)
        case("hb-empty", "POST", "/v1/heartbeat", {}, expect_lt=500)
        case("hb-null", "POST", "/v1/heartbeat", None, expect_lt=500)
        case("hb-huge", "POST", "/v1/heartbeat", {"miner": "wasm1" + "x" * 100000}, expect_lt=500)
        # ---- bad params ----
        case("hb-bad-miner", "POST", "/v1/heartbeat", {"miner": "evil"}, expect_lt=500)
        case("hb-day-str", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": "abc"}, expect_lt=500)
        case("hb-day-neg", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": -5}, expect_lt=500)
        case("hb-day-1e18", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": 10**18}, expect_lt=500)
        case("hb-metrics-str", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": 1, "bandwidth_kbps": "abc"}, expect_lt=500)
        case("hb-metrics-1e30", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": 1, "bandwidth_kbps": 10**30}, expect_lt=500)
        case("hb-metrics-neg", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": 1, "session_secs": -99999}, expect_lt=500)
        case("hb-metrics-obj", "POST", "/v1/heartbeat", {"miner": "wasm1fuzzaaa111111111111111111111111111111111", "day": 1, "stability_pct": {"a": 1}}, expect_lt=500)
        # ---- loops: delegation A<->B, referral A<->B ----
        A = "wasm1fuzzAAA111111111111111111111111111111111"
        B = "wasm1fuzzBBB222222222222222222222222222222222"
        for i in range(3):
            case("deleg-loop-%d" % i, "POST", "/v1/heartbeat",
                 {"miner": A, "day": 2, "delegate_to": B, "referrer": B})
            case("referr-loop-%d" % i, "POST", "/v1/heartbeat",
                 {"miner": B, "day": 2, "delegate_to": A, "referrer": A})
            case("self-deleg-%d" % i, "POST", "/v1/heartbeat",
                 {"miner": A, "day": 2, "delegate_to": A, "referrer": A})
        # ---- deleg-then-finalize: regression guard for the 2026-10-14 float bug.
        # Heartbeats alone returned 200; only finalising surfaced the crash
        # (delegation boost produced a float, leaf_hash to_bytes blew up).
        st, body = req("POST", "/v1/finalize", {"day": 2},
                       headers={"X-Admin": "g7-test-secret"})
        if st != 200:
            fails.append("deleg-then-finalize: expected 200, got %s (%s)" % (st, str(body)[:120]))
        else:
            try:
                _root = json.loads(body).get("root") if isinstance(body, (str, bytes)) else None
                if isinstance(body, bytes):
                    _root = json.loads(body.decode()).get("root")
            except Exception:
                _root = None
            if not _root or len(str(_root)) != 64:
                fails.append("deleg-then-finalize: root missing/short after delegation heartbeats (%r)" % (_root,))
        # ---- GET param abuse ----
        case("day-neg", "GET", "/v1/day?day=-1", expect_lt=500)
        case("day-str", "GET", "/v1/day?day=zzz", expect_lt=500)
        case("day-1e18", "GET", "/v1/day?day=999999999999999999", expect_lt=500)
        case("proof-missing", "GET", "/v1/proof", expect_lt=500)
        case("proof-bad", "GET", "/v1/proof?day=abc&miner=x", expect_lt=500)
        case("scores-bad-day", "GET", "/v1/scores?day=1e30", expect_lt=500)
        case("me-huge-addr", "GET", "/v1/me?addr=" + "w" * 5000, expect_lt=500)
        case("unknown-path", "GET", "/v1/nope", expect_lt=500)
        # ---- finalize auth ----
        st = case("finalize-noauth", "POST", "/v1/finalize", {"day": 1}, expect_lt=500)
        if st != 403:
            fails.append("finalize-noauth: expected 403, got %s" % st)
        # ---- files created must be sane (no day_-5.json etc) ----
        bad_files = [f for f in os.listdir(tmp) if not (f.startswith("day_") and f[4:-5].isdigit() and 0 <= int(f[4:-5]) <= 100000)]
        if bad_files:
            fails.append("polluted data files: %s" % bad_files)
        # ---- hammer -> 429 (post limit 120/min) ----
        got429 = False
        for i in range(200):
            st, _ = req("POST", "/v1/clienterr", {"i": i})
            if st == 429: got429 = True; break
            if st is None or st >= 500:
                fails.append("hammer-%d: status=%s" % (i, st)); break
        if not got429:
            fails.append("rate limiting never engaged (no 429 in 200 rapid posts)")
        # ---- still healthy ----
        st, _ = req("GET", "/v1/health")
        if st != 200:
            fails.append("post-fuzz health=%s (service degraded)" % st)
finally:
    proc.send_signal(signal.SIGTERM)
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
    shutil.rmtree(tmp, ignore_errors=True)

print("G7 fuzz cases done")
if fails:
    print("G7 FUZZ FAILS: %d" % len(fails))
    for x in fails[:20]: print("  FAIL:", x)
    sys.exit(1)
print("G7 FUZZ FAILS: 0")
