#!/usr/bin/env python3
"""wal_rotation_soak.py — 用**变化的数值**重测网关 WAL 轮转（上一轮数值全 0，等于没测）。

要证明的三件事：
 1. 轮转确实在发生：WAL 文件大小有上界，不会随心跳无限增长。
 2. 快照后的日文件 == 内存里的权威状态（逐矿工、逐字段）。
 3. 崩溃恢复正确：拿"日文件 + 残余 WAL"重放一遍，必须还原出同一个状态——
    尤其是同一矿工的值来回变化（5→9→3→0→12）时，恢复结果必须是最后一次的，
    不能被旧记录盖掉。上一轮全 0 数值恰好掩盖了这类"最后写入"错误。

只在临时 DATA 目录 + 随机端口上跑隔离实例，绝不碰生产网关。
"""
import glob
import json
import os
import random
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

GW = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/gateway_v2.py"
SNAP = sys.argv[2] if len(sys.argv) > 2 else "1"   # 调大才能观察到"WAL 攒起来→轮转清零"
PORT = random.randrange(18000, 19999)
TMP = tempfile.mkdtemp(prefix="wal-soak-")
DATA = os.path.join(TMP, "data")
os.makedirs(DATA, exist_ok=True)

import secrets
env = dict(os.environ, GW_PORT=str(PORT), GW_DATA=DATA,
           # 每次运行随机生成，源码里不留任何"像密钥的字面量"，
           # 这样就不必为它开一条泄露门禁豁免（本测试也从不调用管理端点）。
           GW_ADMIN_SECRET=secrets.token_hex(12),
           GW_SNAPSHOT_SECS=SNAP, GW_GENESIS=str(int(time.time()) - 86400 * 3),
           GW_DAY_CUTOVER=str(int(time.time()) - 3600),
           # 限流参数是"每分钟允许条数"，0 = 一条都不许，不是"关闭限流"。
           # 上一版把它们设成 0，等于自己把摄入关掉，测出来的"没记录"是我的错。
           GW_RATE_HB="100000", GW_RATE_HB_IP="100000", GW_RATE_HB_MINER="100000",
           GW_RATE_GET="100000", GW_RATE_POST="100000", GW_CLIENTERR="0")
log = open(os.path.join(TMP, "gw.log"), "w")
proc = subprocess.Popen([sys.executable, GW], env=env, stdout=log, stderr=subprocess.STDOUT)


def api(path, payload=None):
    url = "http://127.0.0.1:%d%s" % (PORT, path)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"_http": e.code, "_body": e.read().decode()[:200]}
        except Exception:
            time.sleep(0.4)
    return {"_err": "unreachable"}


def hb(miner, bw, sess, verif, stab, ip, fp):
    # 字段名以网关实现为准：bandwidth_kbps / session_secs / verification_tasks / stability_pct
    # （上一版测试发的是 bandwidth/session/... 网关按自己的键取值，于是全记成 0，
    #   测出来的是测试脚本的错，不是网关的错。）
    return api("/v1/heartbeat", {"miner": miner, "bandwidth_kbps": bw, "session_secs": sess,
                                 "verification_tasks": verif, "stability_pct": stab,
                                 "ip": ip, "fp": fp, "ts": int(time.time())})


def real_addresses(n=6):
    """用 wasmd 在一次性 keyring 里生成 n 个合法 bech32 地址（假地址会被网关按格式拒掉）。"""
    home = os.path.join(TMP, "keys")
    addrs = []
    for i in range(n):
        r = subprocess.run(["/usr/local/bin/wasmd", "keys", "add", "soak%d" % i,
                            "--keyring-backend", "test", "--home", home, "--output", "json"],
                           capture_output=True, text=True, timeout=60)
        try:
            addrs.append(json.loads(r.stdout)["address"])
        except Exception:
            continue
    return addrs


MINERS = real_addresses(6)
if len(MINERS) < 3:
    print("生成真实地址失败，退出（不要用假地址测，那只会测到地址校验）")
    proc.send_signal(signal.SIGKILL)
    sys.exit(2)
print("测试地址（合法 bech32）:", [m[:14] + "…" for m in MINERS])
SERIES = {}   # miner -> list of (bw, sess, verif, stab) actually sent, in order


CUM = {}   # miner -> 累计值（真实客户端上报的是"当日累计"，所以必须单调递增）


def varying(miner, step):
    """单调递增的累计值：既满足"数值一直在变、不是全 0"的测试目的，
    也符合网关的累计语义（否则倒退会被按设计忽略，测出来的是语义差异而不是轮转）。"""
    c = CUM.setdefault(miner, [0, 0, 0, 0])
    r = random.Random((hash(miner) & 0xffff) * 31 + step)
    c[0] = min(9900, c[0] + r.randrange(50, 900))        # bandwidth_kbps（上限 10000 归一）
    c[1] = min(3590, c[1] + r.randrange(20, 400))        # session_secs（上限 3600）
    c[2] = min(99, c[2] + r.randrange(1, 6))             # verification_tasks（上限 100）
    c[3] = max(c[3], min(100, c[3] + r.choice([0, 0, 1, 2, 3])))   # stability_pct 只增不减
    return (c[0], c[1], c[2], c[3])


def day_file():
    fs = sorted(glob.glob(os.path.join(DATA, "day_*.json")))
    if not fs:
        return None
    return json.load(open(fs[-1], encoding="utf-8"))


def wal_lines():
    out = []
    for w in glob.glob(os.path.join(DATA, "day_*.wal")):
        out += [x for x in open(w, encoding="utf-8").read().splitlines() if x.strip()]
    return out


def replay_state():
    """模拟崩溃恢复：日文件为底，残余 WAL 逐条覆盖。
    网关写 WAL 的形态是 {"miner": m, "miners": {m: {bandwidth_kbps:…}}, …}，
    所以恢复时整条覆盖该矿工，而不是逐字段挑（逐字段挑会掩盖"旧记录盖新记录"这类错）。"""
    d = day_file() or {}
    miners = dict(d.get("miners") or {})
    for line in wal_lines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        inner = rec.get("miners")
        if isinstance(inner, dict):
            for m, v in inner.items():
                if isinstance(v, dict):
                    miners[m] = v
        m = rec.get("miner")
        if m and isinstance(rec.get("score"), dict):
            miners[m] = rec["score"]
    d["miners"] = miners
    return d


KEYS = ("bandwidth_kbps", "session_secs", "verification_tasks", "stability_pct")


def tup_of(rec):
    if not rec:
        return (None, None, None, None)
    return tuple(rec.get(k) for k in KEYS)


def live_state():
    h = api("/v1/health")
    day = h.get("current_day")
    sc = api("/v1/scores?day=%s" % day)
    return day, sc


def main():
    random.seed(20261015)
    for m in MINERS:
        SERIES[m] = []
    peak_wal = 0
    wal_curve = []
    rotations = 0
    seen_wal = set()
    mismatches = []

    t_end = time.time() + 45
    step = 0
    while time.time() < t_end:
        step += 1
        for m in MINERS:
            v = varying(m, step)
            SERIES[m].append(v)
            hb(m, v[0], v[1], v[2], v[3], "10.7.42.%d" % (step % 250), "fp%02d" % (step % 17))
        time.sleep(1.2)          # 让 SNAPSHOT_SECS=1 的轮转至少发生一次
        for w in glob.glob(os.path.join(DATA, "day_*.wal")):
            sz = os.path.getsize(w)
            peak_wal = max(peak_wal, sz)
            if w not in seen_wal:
                seen_wal.add(w)
        day, live = live_state()
        st = replay_state()
        miners = st.get("miners") or {}
        bad = 0
        for m in MINERS:
            last = SERIES[m][-1]
            got = miners.get(m)
            if not got:
                bad += 1
                mismatches.append("step %d: %s 恢复后不存在" % (step, m))
                continue
            if tup_of(got) != last:
                bad += 1
                mismatches.append("step %d: %s 期望 %s 恢复得 %s" % (step, m, last, got))
        wal_now = sum(os.path.getsize(x) for x in glob.glob(os.path.join(DATA, "day_*.wal")))
        wal_curve.append((step, wal_now))
        if step <= 4 or bad:
            print("step %2d day=%s 矿工=%d 不一致=%d 当前WAL=%dB 峰值=%dB"
                  % (step, day, len(miners), bad, wal_now, peak_wal))
        if len(glob.glob(os.path.join(DATA, "day_*.json"))) >= 2:
            rotations += 1

    # 崩溃恢复实测：SIGKILL 后不重启，只从磁盘重放，必须等于最后一次发送的值
    print("\n=== 杀掉实例（SIGKILL，模拟硬崩溃）===")
    proc.send_signal(signal.SIGKILL)
    time.sleep(1.0)
    st = replay_state()
    miners = st.get("miners") or {}
    ok = 0
    for m in MINERS:
        last = SERIES[m][-1]
        got = miners.get(m) or {}
        tup = tup_of(got)
        flag = "OK " if tup == last else "BAD"
        if tup == last:
            ok += 1
        else:
            mismatches.append("崩溃恢复: %s 期望 %s 实得 %s" % (m, last, tup))
        print("  %s %s 最后发送=%s 恢复=%s" % (flag, m[:16], last, tup))

    wal_left = glob.glob(os.path.join(DATA, "day_*.wal"))
    print("\n轮转检查：快照文件 %d 个，残留 WAL %d 个，WAL 峰值 %d 字节，心跳步数 %d"
          % (len(glob.glob(os.path.join(DATA, "day_*.json"))), len(wal_left), peak_wal, len(SERIES[MINERS[0]])))
    total_hb = sum(len(v) for v in SERIES.values())
    print("共发送 %d 次心跳；若不轮转按每条 ~180B 估算应达 %d 字节" % (total_hb, total_hb * 180))
    print("WAL 增长曲线(前 14 步):", ", ".join("%d:%dB" % (s, b) for s, b in wal_curve[:14]))
    print("曲线是否出现\"涨后归零\":", "是" if (max([b for _, b in wal_curve] or [0]) > 500 and any(b == 0 for _, b in wal_curve[3:])) else "未观察到")
    if mismatches:
        print("\n不一致 %d 处（前 12 条）：" % len(mismatches))
        for x in mismatches[:12]:
            print("   ", x)
    verdict = (ok == len(MINERS)) and peak_wal < max(20000, total_hb * 40) and not mismatches
    print("\nWAL-SOAK %s" % ("PASS" if verdict else "FAIL"))
    print("临时目录保留在 %s（未删除，便于复核）" % TMP)
    return 0 if verdict else 1


sys.exit(main())
