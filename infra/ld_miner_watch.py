#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-MINER-WATCH-20261016  矿工留存看门狗（每天跑一次，比"人肉发现矿工在掉"早）。
为什么需要：2026-10-16 手工核对发现按天计分的矿工数 12→9→8，且这三天
**一个新矿工都没进来**。这种趋势以前只能靠我偶然去查 /gw/v1/scores 才看得见。

口径（刻意保守，避免误报）：
  · 只比"已完成的整天"（current_day-1 及更早），当天在跑不算掉人；
  · 掉人 >= DROP_ALERT(默认2) 或 连续 NO_NEW_DAYS(默认3) 天零新增 -> 告警；
  · 网关查不到 / 返回不是 JSON / 分数表为空 -> 报 QUERY-FAIL 并非零退出，
    绝不允许"没查到"被当成"没问题"（这条是本项目的硬规矩）。
历史落在 /var/lib/ld_miner_watch/history.jsonl（自己攒，不依赖网关保留期）。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("LD_GW_BASE", "https://lightdao.net/gw")
STATE_DIR = os.environ.get("LD_MW_STATE", "/var/lib/ld_miner_watch")
HIST = os.path.join(STATE_DIR, "history.jsonl")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
DROP_ALERT = int(os.environ.get("LD_MW_DROP", "2"))
NO_NEW_DAYS = int(os.environ.get("LD_MW_NONEW", "3"))
UA = {"User-Agent": "ld-miner-watch/1.0"}


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def note(line):
    txt = "%s %s\n" % (utc(), line)
    sys.stdout.write(txt)
    try:
        with open(ALERTS, "a") as f:
            f.write(txt)
    except Exception as e:
        sys.stderr.write("WARN 告警写不进 %s: %s（内容见本行输出）\n" % (ALERTS, e))


def day_scores(day):
    d = get("/v1/scores?day=%d" % day)
    s = d.get("scores") or {}
    if not isinstance(s, dict):
        raise ValueError("scores 不是对象")
    return d.get("day"), s


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        h = get("/v1/health")
        cur = int(h["current_day"])
    except Exception as e:
        note("ALERT [miner-watch] QUERY-FAIL 网关 /v1/health 不可用: %s" % e)
        return 5
    if not h.get("ok"):
        note("ALERT [miner-watch] 网关自报不健康: %s" % json.dumps(h)[:160])
        return 5

    done = cur - 1                      # 最近一个"已完成整天"
    rows = []
    for back in range(0, 8):            # 往前 8 天，够判"连续零新增"
        d = done - back
        if d < 1:
            break
        try:
            got, s = day_scores(d)
        except Exception as e:
            note("ALERT [miner-watch] QUERY-FAIL 第 %d 天分数取不到: %s" % (d, e))
            return 5
        if got != d:
            # 网关忽略 day 参数时会把"今天"当成历史天返回，必须当场识破
            note("ALERT [miner-watch] 请求第 %d 天却回 %s —— 参数没生效，判定作废"
                 % (d, got))
            return 6
        rows.append((d, sorted(s), sum(int(v.get("w", 0)) for v in s.values())))

    rows.reverse()                     # 旧 -> 新
    with open(HIST, "a", encoding="utf-8") as f:
        for d, addrs, tot in rows:
            f.write(json.dumps({"ts": utc(), "day": d, "n": len(addrs),
                                "total": tot, "addrs": addrs}) + "\n")

    print("已完成整天序列（日 人数 总分）: " +
          "  ".join("%d:%d/%d" % (d, len(a), t) for d, a, t in rows))
    problems = []
    for i in range(1, len(rows)):
        (d0, a0, _), (d1, a1, _) = rows[i - 1], rows[i]
        gone = sorted(set(a0) - set(a1))
        new = sorted(set(a1) - set(a0))
        if gone:
            print("  第 %d 天：掉 %d 人 %s" % (d1, len(gone), [x[:14] + "…" for x in gone[:4]]))
        if len(gone) >= DROP_ALERT:
            problems.append("第 %d 天矿工掉了 %d 人（阈值 %d）" % (d1, len(gone), DROP_ALERT))
        if not new:
            print("  第 %d 天：无新增矿工" % d1)
    tail_new = [bool(set(rows[i][1]) - set(rows[i - 1][1])) for i in range(1, len(rows))]
    streak = 0
    for v in reversed(tail_new):
        if v:
            break
        streak += 1
    if streak >= NO_NEW_DAYS:
        problems.append("连续 %d 天零新增矿工" % streak)

    if problems:
        for p in problems:
            note("ALERT [miner-watch] " + p)
        return 1
    print("矿工留存正常：没有整天掉人达到阈值 %d；已完成的 %d 天里有新增的天数=%d"
          % (DROP_ALERT, len(tail_new), sum(1 for v in tail_new if v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
