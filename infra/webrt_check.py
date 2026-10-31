#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""webrt_check.py —— 盯住 WebRTC 信令的那类签名错误有没有真的停下来。
   为什么单独要一个：我只改了代码并上线，这不等于问题解决。
   判据用被改对象自己的证据：客户端错误日志里
   "setRemoteDescription ... Called in wrong state" 的近 24 小时条数。
   超过阈值（默认 6 条/24h，修前实测 4 条/24h、3 个 IP）→ 报警；
   同一批不重复刷屏：按条数分档去重。"""
import json, os, sys, time
from datetime import datetime, timezone

LOG = "/home/ubuntu/lightdao_gateway/clienterr.log"
STATE = os.environ.get("LD_WEBRTC_STATE", "/home/ubuntu/ld_webrtc_state.json")
ALERTS = "/home/ubuntu/ld_alerts.log"
LIMIT = int(os.environ.get("LD_WEBRTC_LIMIT", "6"))
HOURS = 24
SIG = ("setRemoteDescription", "wrong state")


def count_24h():
    cut = time.time() - HOURS * 3600
    n, ips = 0, set()
    try:
        f = open(LOG, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        print("没有客户端错误日志，判据无法成立（不算通过）")
        return None, None
    for ln in f:
        try:
            j = json.loads(ln)
        except Exception:
            continue
        if j.get("ts", 0) < cut:
            continue
        m = str((j.get("body") or {}).get("msg") or "")
        if all(x in m for x in SIG):
            n += 1
            ips.add(str(j.get("ip", "")))
    return n, ips


n, ips = count_24h()
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
if n is None:
    print("WEBRTC-CHECK-UNKNOWN 读不到数据源")
    sys.exit(2)
print("近 %d 小时 setRemoteDescription 状态错：%d 条 / %d 个来源" % (HOURS, n, len(ips)))
prev = {}
try:
    prev = json.load(open(STATE))
except Exception:
    pass
if n > LIMIT:
    bucket = n // 10                      # 每上一档才再报一次，避免持续刷
    if prev.get("bucket") != bucket or time.time() - float(prev.get("ts", 0)) > 6 * 3600:
        line = "%s WEBRTC-ERRORS %d 条/%d IP（阈值 %d）仍在出现，修掉的重复 answer 防护可能没覆盖到该路径" % (stamp, n, len(ips), LIMIT)
        try:
            with open(ALERTS, "a") as fo:
                fo.write(line + "\n")
            print("已落告警")
        except Exception as e:
            print("WARN 告警没落盘：%s" % str(e)[:80])
        json.dump({"bucket": bucket, "ts": time.time(), "n": n}, open(STATE, "w"))
        sys.exit(1)
    print("同档已报过，不再刷")
    sys.exit(1)
if prev.get("bucket") is not None:
    print("已回落到阈值内（上一次 %s 条）" % prev.get("n"))
json.dump({"bucket": None, "ts": time.time(), "n": n}, open(STATE, "w"))
print("WEBRTC-CHECK OK")
