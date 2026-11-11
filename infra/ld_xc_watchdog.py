#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_xc_watchdog.py —— 监控监控本身（"任务哑了必须自己会叫"，11-08 教训落地）。

只干一件事：检查证明源就绪探针 ld_xc_proof_probe.py 写出的状态文件心跳。
  · 心跳超时（默认 >95 分钟，cron 每 30 分一跑，2 次没动就算哑）→ 写告警；
  · 状态文件缺失/损坏 → 也告警（探针从没跑过或挂了）；
  · 正常 → 不刷噪音。
本脚本本身由 cron 每小时跑；它哑了由人/上层心跳兜（这里只覆盖探针这一层）。
"""
import json
import os
import time

STATE = os.environ.get("XCP_STATE", "/home/ubuntu/ld_xc_proof_state.json")
LOG = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")   # 汇入站内统一告警口（Discord 分发脚本读这里）
MAX_AGE_MIN = int(os.environ.get("XCW_MAX_AGE_MIN", "95"))


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def age_minutes(utc_str):
    try:
        t = time.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return (time.time() - time.mktime(t)) / 60.0
    except Exception:
        return None


def check(path=STATE, max_age=MAX_AGE_MIN):
    """返回 (status, detail)。status ∈ ok / stale / missing / corrupt。"""
    if not os.path.exists(path):
        return "missing", "状态文件不存在——探针从未成功跑过"
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
    except Exception as e:
        return "corrupt", "状态文件读不出：%s" % str(e)[:60]
    a = age_minutes(st.get("utc") or "")
    if a is None:
        return "corrupt", "心跳时间戳不可解析"
    if a > max_age:
        return "stale", "证明探针已 %.0f 分钟没更新（>%d）——cron 可能哑了/额度耗尽" % (a, max_age)
    return "ok", "心跳 %.1f 分钟前，ready_src=%s" % (a, st.get("ready_src"))


def alert(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s [xc-watchdog] %s\n" % (_now(), msg))
    except Exception:
        pass


def run():
    status, detail = check()
    print("watchdog: %s | %s" % (status, detail))
    if status != "ok":
        alert("证明源监控异常：%s / %s" % (status, detail))
    # 非 ok 一律退出码 1，方便外部（systemd/邮件）也捕获
    return 0 if status == "ok" else 1


def _selftest():
    import tempfile
    good = 0
    def chk(c, l):
        nonlocal good; good += 1 if c else 0
        print(("  [%s] " % ("OK " if c else "坏")) + l)
    # 新鲜心跳 → ok
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"ready_src": "x", "utc": _now()}, f); p_ok = f.name
    st, _ = check(p_ok); chk(st == "ok", "新鲜心跳判 ok（正常态不误报）")
    # 植入"旧心跳" → stale（反向验证：哑了必须被检出）
    old = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 200 * 60))
    with open(p_ok, "w", encoding="utf-8") as f:
        json.dump({"ready_src": None, "utc": old}, f)
    st, _ = check(p_ok, max_age=95); chk(st == "stale", "200 分钟旧心跳 → 判 stale（哑了必被逮）")
    # 缺失文件 → missing
    st, _ = check("/no/such/file.json"); chk(st == "missing", "文件缺失 → 判 missing")
    # 损坏 → corrupt
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write("{not json"); p_bad = f.name
    st, _ = check(p_bad); chk(st == "corrupt", "损坏内容 → 判 corrupt")
    for p in (p_ok, p_bad):
        try: os.remove(p)
        except Exception: pass
    print("ld_xc_watchdog 自测：%d/4 通过" % good)
    return 0 if good == 4 else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    sys.exit(run())
