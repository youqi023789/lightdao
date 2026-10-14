#!/usr/bin/env python3
"""ab3_parity_recovery.py — v1/v2 根对拍 + 崩溃恢复（修正版：真实状态码、合法测试日）。"""
import json, os, shutil, subprocess, sys, time, urllib.error, urllib.request

SG, SV2 = "/tmp/gateway_fixed.py", "/home/ubuntu/gateway_v2.py"
BASE = "/tmp/ab3"
N = int(os.environ.get("AB_N", "400")); BEATS = int(os.environ.get("AB_BEATS", "3"))
COMMON = dict(GW_GENESIS="1789102088", GW_RATE_HB="1000000", GW_RATE_POST="1000000",
              GW_RATE_GET="1000000", GW_ADMIN_SECRET="absec", GW_SNAPSHOT_SECS="5",
              GW_DAY_CUTOVER="1790726400")


def start(script, port, data):
    os.makedirs(data, exist_ok=True)
    env = dict(os.environ, **COMMON, GW_PORT=str(port), GW_DATA=data)
    p = subprocess.Popen([sys.executable, script], env=env,
                         stdout=open(os.path.join(data, "gw.out"), "w"), stderr=subprocess.STDOUT)
    for _ in range(80):
        time.sleep(0.4)
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/v1/health" % port, timeout=3).read(); return p
        except Exception:
            if p.poll() is not None:
                print("启动失败:", open(os.path.join(data, "gw.out")).read()[-400:]); sys.exit(1)
    print("健康超时"); sys.exit(1)


def call(port, path, obj=None, method="POST"):
    data = json.dumps(obj).encode() if obj is not None else None
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path), data=data, method=method,
                                 headers={"Content-Type": "application/json", "X-Admin": "absec"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")      # 关键：不再吞掉真实错误码
    except Exception as e:
        return -1, "%s: %s" % (type(e).__name__, e)


def hb(port, day, i, b):
    m = "wasm1%058x" % i
    return call(port, "/v1/heartbeat", {
        "miner": m, "day": day, "fp": "fp%060x" % i,
        "bandwidth_kbps": 1000 + (i % 9000), "session_secs": 900 * (b + 1),
        "verification_tasks": 5 + (i % 95), "stability_pct": 80 + (i % 20),
        "behaviors": {"pwa": i % 3 == 0, "delegated": i % 7 == 0, "social": False,
                       "quiz": i % 11 == 0, "voted": i % 13 == 0},
        "delegate_to": ("wasm1%058x" % ((i + 1) % N)) if i % 7 == 0 else None,
        "referrer": ("wasm1%058x" % ((i * 7) % N)) if i % 5 == 0 and (i * 7) % N != i else None})


def wait_file(p, secs=60):
    for _ in range(int(secs / 0.5)):
        if os.path.exists(p): return True
        time.sleep(0.5)
    return False


shutil.rmtree(BASE, ignore_errors=True); os.makedirs(BASE)
pr1 = start(SG, 18201, os.path.join(BASE, "v1"))
pr2 = start(SV2, 18202, os.path.join(BASE, "v2"))
try:
    st, b = call(18201, "/v1/health", None, "GET")
    cur = json.loads(b)["current_day"]; DAY = cur - 1
    print("=== N=%d × %d 心跳, 测试日=%d（当前日=%d）===" % (N, BEATS, DAY, cur))

    t0 = time.time()
    r1 = [hb(18201, DAY, i, b2) for b2 in range(BEATS) for i in range(N)]
    t1 = time.time() - t0
    t0 = time.time()
    r2 = [hb(18202, DAY, i, b2) for b2 in range(BEATS) for i in range(N)]
    t2 = time.time() - t0
    print("  心跳耗时 v1=%.1fs v2=%.1fs | 成功数 v1=%d v2=%d"
          % (t1, t2, sum(1 for x in r1 if x[0] == 200), sum(1 for x in r2 if x[0] == 200)))

    s1, b1 = call(18201, "/v1/finalize", {"day": DAY})
    s2, b2 = call(18202, "/v1/finalize", {"day": DAY})
    print("  finalize HTTP v1=%s v2=%s" % (s1, s2))
    if s1 != 200 or s2 != 200:
        print("  v1 body:", b1[:200]); print("  v2 body:", b2[:200]); sys.exit(1)

    f1p = os.path.join(BASE, "v1", "day_%d.json" % DAY)
    f2p = os.path.join(BASE, "v2", "day_%d.json" % DAY)
    print("  快照落盘 v1=%s v2=%s" % (wait_file(f1p, 10), wait_file(f2p, 60)))
    f1 = json.load(open(f1p)); f2 = json.load(open(f2p))
    assert f1.get("root"), "v1 root 为空，测试无效"
    same = (f1["root"] == f2["root"] and f1["total_score"] == f2["total_score"]
            and f1["active_miners"] == f2["active_miners"]
            and json.dumps(f1["scores"], sort_keys=True) == json.dumps(f2["scores"], sort_keys=True))
    print("  root v1=%s" % f1["root"][:40])
    print("  root v2=%s" % f2["root"][:40])
    print("  >>> 根/总分/矿工数/scores 全一致: %s" % ("是 ✓" if same else "否 ✗"))

    print("=== 崩溃恢复（SIGKILL 后重启，读快照+重放日记）===")
    hb(18202, DAY, 0, 9); hb(18202, DAY, 1, 9)      # 制造"已快照后又来心跳、尚未快照"的状态
    time.sleep(0.5)
    os.kill(pr2.pid, 9); time.sleep(1.5)
    pr3 = start(SV2, 18203, os.path.join(BASE, "v2"))
    st, body = call(18203, "/v1/day?day=%d" % DAY, None, "GET")
    d = json.loads(body) if st == 200 else {}
    print("  重启后 HTTP=%s finalized=%s root=%s" % (st, d.get("finalized"), str(d.get("root"))[:40]))
    print("  >>> 恢复后根与原值一致: %s" % ("是 ✓" if d.get("root") == f2["root"] else "否 ✗"))
    pr3.terminate()
    print("  v2 WAL 大小: %s 字节" % (os.path.getsize(os.path.join(BASE, "v2", "day_%d.wal" % DAY))
                                    if os.path.exists(os.path.join(BASE, "v2", "day_%d.wal" % DAY)) else "已随快照轮转"))
finally:
    pr1.terminate(); pr2.terminate()
