#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_share.py —— 盯住"测试探针在真实矿工奖励里占多大比重"。

为什么需要它：探针每天在链上领走近 9 万 LIGHT（占矿工池 13.9%，
公式与链上实收两边吻合）。为了让它继续证明"领取链路通"，我把它的足迹降到最小
（平日只留极小分，每周一次满强度覆盖 ≥4h 空投路径）。
但"降了"不等于"以后一直低"：任何人调心跳参数、或网关改了权重，占比会悄悄爬回去，
而它爬回去的代价是真实矿工少拿钱——这种事必须机器先发现。

判据照抄被审计方的公式（gateway_v3.py 的 norm + WEIGHTS），不自己另写一套：
上一轮我就是因为自造归一公式，把占比估低了、还顺手误报了一个不存在的"权重虚增"bug。
"""
import glob, json, os, subprocess, sys, time
from datetime import datetime, timezone

DATA = os.environ.get("LD_GW_DATA", "/home/ubuntu/lightdao_gateway/data")
GW = "/usr/local/bin/gateway_v3.py"
STATE = os.environ.get("LD_PROBE_STATE", "/home/ubuntu/ld_probe_share_state.json")
ALERTS = "/home/ubuntu/ld_alerts.log"
LIMIT_PCT = float(os.environ.get("LD_PROBE_LIMIT", "6"))
EXCLUDE_SELF = os.environ.get("LD_PROBE_EXCLUDE", "1") == "1"


def read_formula():
    """从网关源码里读 TARGETS/WEIGHTS，避免两边各写一份常量。"""
    try:
        s = open(GW, encoding="utf-8", errors="replace").read()
    except Exception:
        return None, None
    import ast as _ast
    t = _ast.parse(s)
    out = {}
    for node in t.body:
        if isinstance(node, _ast.Assign):
            for tg in node.targets:
                if isinstance(tg, _ast.Name) and tg.id in ("TARGETS", "WEIGHTS"):
                    try:
                        out[tg.id] = _ast.literal_eval(node.value)
                    except Exception:
                        pass
    return out.get("TARGETS"), out.get("WEIGHTS")


def latest_day_file():
    best = None
    for f in glob.glob(os.path.join(DATA, "day_*.json")):
        try:
            d = int(os.path.basename(f)[4:-5])
        except Exception:
            continue
        if best is None or d > best[0]:
            best = (d, f)
    return best


def main():
    TARGETS, WEIGHTS = read_formula()
    if not TARGETS or not WEIGHTS:
        print("PROBE-SHARE-UNKNOWN 读不到网关公式（不算通过）")
        return 2
    got = latest_day_file()
    if not got:
        print("PROBE-SHARE-UNKNOWN 没有 day 文件（不算通过）")
        return 2
    day, f = got
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("PROBE-SHARE-UNKNOWN 读 day 文件失败 %s" % str(e)[:60])
        return 2
    miners = d.get("miners") or {}
    # 探针身份从 cron/配置里读，不在这里硬编码地址（硬编码一旦换钥就静默失真）
    probes = set()
    if EXCLUDE_SELF:
        try:
            r = subprocess.run(["wasmd", "keys", "show", "canary", "-a",
                               "--keyring-backend", "test", "--home", "/home/ubuntu/.wasmd"],
                              capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                probes.add(r.stdout.strip())
        except Exception:
            pass
    DIM = {"bandwidth": "bandwidth_kbps", "session": "session_secs",
           "verification": "verification_tasks", "stability": "stability_pct"}

    def wscore(m):
        tot = 0
        for k, metric in DIM.items():
            tgt = TARGETS.get(metric) or 1
            v = min(int(m.get(metric) or 0), tgt)
            tot += (v * 100 // tgt) * WEIGHTS.get(k, 0)
        return tot
    sc = {a: wscore(v or {}) for a, v in miners.items()}
    total = sum(sc.values())
    if total <= 0:
        print("day %s 无有效分数（跳过判定）" % day)
        return 0
    psum = sum(v for a, v in sc.items() if a in probes)
    pct = 100.0 * psum / total
    print("day %s：矿工 %d 个，探针 %s，占比 %.1f%%（阈值 %.1f%%）"
          % (day, len(miners), ("+".join(x[:12] for x in probes) or "未识别"), pct, LIMIT_PCT))
    prev = {}
    try:
        prev = json.load(open(STATE))
    except Exception:
        pass
    now = int(time.time())
    if pct > LIMIT_PCT:
        bucket = int(pct // 3)
        if prev.get("bucket") != bucket or now - int(prev.get("ts", 0)) > 86400:
            line = "%s PROBE-SHARE 探针占矿工奖励 %.1f%%（阈值 %.1f%%），day=%s" % (
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), pct, LIMIT_PCT, day)
            try:
                open(ALERTS, "a").write(line + "\n")
                subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", line],
                               capture_output=True, timeout=30)
            except Exception as e:
                print("WARN 告警落盘失败：" + str(e)[:80])
            json.dump({"bucket": bucket, "ts": now, "pct": pct}, open(STATE, "w"))
        print("PROBE-SHARE FAIL")
        return 1
    if prev.get("pct") and prev.get("pct") > LIMIT_PCT:
        print("已回落到阈值内（上次 %.1f%%）" % prev["pct"])
    json.dump({"bucket": None, "ts": now, "pct": pct}, open(STATE, "w"))
    print("PROBE-SHARE OK")
    return 0


sys.exit(main())
