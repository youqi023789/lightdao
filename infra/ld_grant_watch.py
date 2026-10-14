#!/usr/bin/env python3
"""ld_grant_watch.py — 看门狗：谁来看"给用户代付 Gas 的那套东西"。

背景：gas_grant.py 每 10 分钟为矿工签发 fee grant（领取免 Gas 的来源），但主监控里
对 feegrant / granter / gas_grant 的引用是 0 —— 也就是说它哪天静默失败（换钥匙、RPC 报错、
cron 行被改坏），用户领取会开始失败而没有任何告警。这和"第 31 天奖励根没提交、躺了 26 小时
没人发现"是同一类故障：坏的是链路最后一环，且失败形态是"用户点了没反应"。

三条判据（任一不满足就告警，去重 1 小时一次）：
  1) 签发日志必须新鲜（默认 40 分钟内有心跳）；
  2) granter 当前签出的授权数必须 > 0；
  3) granter 账户余额必须高于地板值（默认 10,000 LIGHT）。

只读链上查询 + 读日志，不写任何状态；退出码 0=正常，1=已告警。
"""
import json
import os
import re
import subprocess
import time

GRANTER = "wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"   # feegrant 出资账户（账户，不是合约）
LOG = "/home/ubuntu/ld_gasgrant.log"
STATE = "/home/ubuntu/ld_grant_watch_state"
ALERTS = "/home/ubuntu/ld_alerts.log"
RPC = "http://127.0.0.1:26657"
WASMD = "/usr/local/bin/wasmd"
STALE_SECS = 40 * 60
BAL_FLOOR_LIGHT = 10000


def alert(msg):
    line = "%s ALERT %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line)
    try:
        with open(ALERTS, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception as e:
        print("(cannot write alert log: %s)" % e)


def deduped(key):
    """同一类问题一小时最多响一次。"""
    now = time.time()
    last = {}
    try:
        for ln in open(STATE, encoding="utf-8"):
            k, _, v = ln.strip().partition("=")
            if k:
                last[k] = float(v or 0)
    except Exception:
        pass
    if now - last.get(key, 0) < 3600:
        return False
    last[key] = now
    try:
        with open(STATE, "w", encoding="utf-8") as fh:
            for k, v in last.items():
                fh.write("%s=%s\n" % (k, v))
    except Exception:
        pass
    return True


def grant_count():
    try:
        out = subprocess.run([WASMD, "query", "feegrant", "grants-by-granter", GRANTER,
                              "--node", RPC, "--output", "json"],
                             capture_output=True, text=True, timeout=45).stdout
        return len(re.findall(r'"grantee"', out))
    except Exception as e:
        print("(grant query failed: %s)" % e)
        return -1


def granter_balance():
    """返回 ulight 整数；查不到返回 -1。"""
    try:
        out = subprocess.run([WASMD, "query", "bank", "balances", GRANTER,
                              "--node", RPC, "--output", "json"],
                             capture_output=True, text=True, timeout=45).stdout
        j = json.loads(out)
        for c in j.get("balances", []):
            if c.get("denom") == "ulight":
                return int(c["amount"])
    except Exception as e:
        print("(balance query failed: %s)" % e)
    return -1


def main():
    bad = 0
    # 1) 签发心跳
    if os.path.exists(LOG):
        age = time.time() - os.path.getmtime(LOG)
        if age > STALE_SECS:
            bad += 1
            if deduped("stale"):
                alert("gas-grant 心跳过期 %.0f 分钟（>%d 分钟），用户领取可能已开始失败"
                      % (age / 60, STALE_SECS // 60))
        else:
            print("OK heartbeat %.0f 分钟前" % (age / 60))
    else:
        bad += 1
        if deduped("nostale"):
            alert("gas-grant 日志不存在：%s，无法判断代付是否在跑" % LOG)

    # 2) 授权数
    n = grant_count()
    if n == 0:
        bad += 1
        if deduped("zerogrants"):
            alert("granter 当前有效 fee grant = 0，领取免 Gas 已失效")
    elif n < 0:
        bad += 1
        if deduped("queryfail"):
            alert("fee grant 查询失败（节点 RPC 或 wasmd 异常），无法确认代付状态")
    else:
        print("OK grants=%d" % n)

    # 3) 出资账户余额
    bal = granter_balance()
    if bal < 0:
        bad += 1
        if deduped("balquery"):
            alert("granter 余额查询失败，无法确认代付资金是否充足")
    else:
        light = bal / 1e6
        if light < BAL_FLOOR_LIGHT:
            bad += 1
            if deduped("lowbal"):
                alert("granter 余额仅 %.0f LIGHT（地板 %d），领取代付即将断粮"
                      % (light, BAL_FLOOR_LIGHT))
        else:
            print("OK granter 余额 %.0f LIGHT" % light)

    print("GRANT-WATCH %s" % ("PROBLEMS=%d" % bad if bad else "OK"))
    return 1 if bad else 0


raise SystemExit(main())
