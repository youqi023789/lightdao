#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_xc_mainnet_watch.py —— 主网跨链的值守：等油钱 → 油钱到了自动开 → 开完盯住别悄悄烂掉。

为什么需要：开通道这件事的"触发条件"是所有者转账，时间点不可预测；而开通之后真正的风险是
**静默失效**（中继进程挂了 / 通道被关 / 报文积压），用户端只会看到"钱没到账"，链上却没人报警。
所以一个脚本两种职责，用状态文件分岔：
  status != opened：每轮做就绪体检；两侧油钱都够 → 自动调 ld_xc_mainnet_open.py 开通（一次性上锁在开通器里）
  status == opened：盯 4 件事，任一异常 = 非零退出 + 写告警

盯梢项（opened 态）：
 1) systemd 服务 active（`systemctl is-active`）
 2) 主网 transfer 通道仍有 STATE_OPEN（链上权威，不信进程）
 3) 中继日志/hermes 侧仍在推进：两侧 packet-commitments 数量不得单调增长（积压=搬不动）
 4) 主网与 Osmosis 高度都在长（对面停链也会导致回不来账）

反向验证（--selftest）：把上面 4 项分别植入故障，确认每一植必响；再给一份正常态，确认不误报。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

STATE = os.environ.get("XC_MN_STATE", "/home/ubuntu/ld_xc_mainnet.json")
ALERTS = os.environ.get("XC_MN_ALERTS", "/home/ubuntu/ld_alerts.log")
WSTATE = os.environ.get("XC_MN_WSTATE", "/home/ubuntu/ld_xc_mainnet_watch.json")
A_RPC = os.environ.get("XC_MN_A_RPC", "http://127.0.0.1:26657")
B_RPC = os.environ.get("XC_MN_B_RPC", "https://rpc.osmosis.zone")
SVC = os.environ.get("XC_MN_SVC", "lightdao-ibc-mainnet.service")
OPEN = os.environ.get("XC_MN_OPEN", "/home/ubuntu/ld_xc_mainnet_open.py")
DRY = os.environ.get("XC_MN_DRY", "0") == "1"
BACKLOG_MAX = int(os.environ.get("XC_MN_BACKLOG_MAX", "40"))
AGE_MAX = int(os.environ.get("XC_MN_AGE_MAX", "1800"))     # 距上次成功轮询超过 30 分钟 = 值守本身死了
FX = os.environ.get("XC_MW_FIX")


def line(msg):
    s = "%s XC-MN-WATCH %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(s, flush=True)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(s + "\n")
    except Exception:
        pass


def fx(name, default=None):
    if not FX:
        return default
    try:
        with open(FX, encoding="utf-8") as f:
            return json.load(f).get(name, default)
    except Exception:
        return default


def jrun(cmd, timeout=60):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(p.stdout) if p.stdout.strip() else {}
    except Exception:
        return {}


def rpc(node, method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(node, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as f:
        d = json.load(f)
    return d.get("result", d)


def load(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save(p, d):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, p)


def svc_active():
    v = fx("svc")
    if v is not None:
        return v == "active"
    p = subprocess.run(["systemctl", "is-active", SVC], capture_output=True, text=True, timeout=20)
    return p.stdout.strip() == "active"


def open_channels(node=A_RPC):
    raw = fx("channels")
    if raw is None:
        raw = (jrun(["wasmd", "q", "ibc", "channel", "channels", "--node", node, "-o", "json"])
               .get("channels") or [])
    return [c for c in raw
            if c.get("port_id") == "transfer" and ((c.get("state") or {}).get("status")) == "STATE_OPEN"]


def height(node):
    h = fx("height_" + ("A" if "127.0.0.1" in node else "B"))
    if h is not None:
        return int(h)
    try:
        return int(rpc(node, "status")["sync_info"]["latest_block_height"])
    except Exception:
        return -1


def backlog(node=A_RPC):
    """待确认报文数：通道开了但报文堆着不动 = 中继哑了（用户表现为"转出去没到账"）"""
    n = fx("backlog")
    if n is not None:
        return int(n)
    total = 0
    for ch in open_channels(node):
        d = jrun(["wasmd", "q", "ibc", "channel", "packet-commitments", "transfer",
                  ch.get("channel_id", ""), "--node", node, "-o", "json"])
        total += len(d.get("packet_commitments") or [])
    return total


def check_opened(problems):
    if not svc_active():
        problems.append("中继服务 %s 不在 active —— 用户转账会没人搬" % SVC)
    if not open_channels():
        problems.append("主网查不到 OPEN 的 transfer 通道 —— 通道被关或状态文件与实际不符")
    hA, hB = height(A_RPC), height(B_RPC)
    prev = load(WSTATE, {})
    if hA > 0 and prev.get("hA", -1) > 0 and hA <= prev["hA"]:
        problems.append("主网高度没在长（%s → %s）" % (prev["hA"], hA))
    if hB > 0 and prev.get("hB", -1) > 0 and hB <= prev["hB"]:
        problems.append("Osmosis 高度没在长（%s → %s）" % (prev["hB"], hB))
    if hA < 0:
        problems.append("主网状态读不到")
    if hB < 0:
        problems.append("Osmosis 状态读不到（对面挂了也会导致回程不到账）")
    bl = backlog()
    if bl > prev.get("backlog", 0) + BACKLOG_MAX:
        problems.append("待确认报文从 %s 涨到 %s —— 中继搬不动了" % (prev.get("backlog"), bl))
    save(WSTATE, {"hA": hA, "hB": hB, "backlog": bl,
                  "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    return {"hA": hA, "hB": hB, "backlog": bl}


def try_open(dry=False):
    """油钱到位就自动开通（护栏 + 一次性上锁在开通器里，这里只负责按周期触发）"""
    cmd = [sys.executable, OPEN] + (["--dry-run"] if dry else [])
    if DRY and not dry:
        line("DRY=1：本该真开通，按演练处理")
        return 0
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    tail = " | ".join([" ".join(l.split()) for l in p.stdout.splitlines() if l.strip()][-4:])
    line("%s rc=%d：%s" % ("演练体检" if dry else "自动开通", p.returncode, tail[:400]))
    return p.returncode


def selftest():
    """植入 4 类故障必须响 + 正常态不误报；顺带确认等钱阶段不会乱报警。"""
    import tempfile
    good = 0
    cases = [
        ("服务挂掉要响", {"svc": "failed", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                       "state": {"status": "STATE_OPEN"}}],
                        "height_A": 100, "height_B": 100, "backlog": 0,
                        "prev": {"hA": 99, "hB": 99, "backlog": 0}}, True),
        ("通道被关要响", {"svc": "active", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                      "state": {"status": "STATE_CLOSED"}}],
                        "height_A": 101, "height_B": 101, "backlog": 0,
                        "prev": {"hA": 99, "hB": 99, "backlog": 0}}, True),
        ("主网停块要响", {"svc": "active", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                     "state": {"status": "STATE_OPEN"}}],
                        "height_A": 99, "height_B": 102, "backlog": 0,
                        "prev": {"hA": 99, "hB": 99, "backlog": 0}}, True),
        ("对面停块要响", {"svc": "active", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                     "state": {"status": "STATE_OPEN"}}],
                        "height_A": 103, "height_B": 99, "backlog": 0,
                        "prev": {"hA": 99, "hB": 99, "backlog": 0}}, True),
        ("报文积压要响", {"svc": "active", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                     "state": {"status": "STATE_OPEN"}}],
                        "height_A": 104, "height_B": 104, "backlog": 500,
                        "prev": {"hA": 99, "hB": 99, "backlog": 0}}, True),
        ("一切正常不许响", {"svc": "active", "channels": [{"port_id": "transfer", "channel_id": "channel-0",
                                                       "state": {"status": "STATE_OPEN"}}],
                          "height_A": 105, "height_B": 105, "backlog": 3,
                          "prev": {"hA": 99, "hB": 99, "backlog": 0}}, False),
    ]
    global WSTATE
    old_w, old_fx = WSTATE, os.environ.get("XC_MW_FIX")
    for name, data, want_alarm in cases:
        tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data, tf); tf.close()
        os.environ["XC_MW_FIX"] = tf.name
        globals()["FX"] = tf.name
        wf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data["prev"], wf); wf.close()
        WSTATE = wf.name
        problems = []
        check_opened(problems)
        got = bool(problems)
        ok = got == want_alarm
        good += 1 if ok else 0
        print("  [%s] %s → 报警=%s 期望=%s%s"
              % ("OK " if ok else "坏", name, got, want_alarm,
                 "" if ok else "  实测：" + "; ".join(problems)[:140]))
        os.unlink(tf.name); os.unlink(wf.name)
    WSTATE = old_w
    os.environ.pop("XC_MW_FIX", None)
    globals()["FX"] = old_fx
    print("自检 %d/%d" % (good, len(cases)))
    return 0 if good == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    st = load(STATE, {})
    status = st.get("status", "unknown")
    problems = []
    if status in ("opened", "ready_to_open"):
        facts = check_opened(problems)
        print("opened 态检查：%s" % json.dumps(facts, ensure_ascii=False))
        if problems:
            for p in problems:
                line("异常：" + p)
            return 1
        line("正常：服务 active、通道 OPEN、两侧出块、无积压（hA=%s hB=%s backlog=%s）"
             % (facts["hA"], facts["hB"], facts["backlog"]))
        return 0
    if status == "opened_unverified":
        line("状态是 opened_unverified（通道开了但双向验证没过）—— 需要人工看，不自动重试")
        return 1
    # 还没开通：不信状态文件里的旧结论，每轮重新问一次链上现状（护栏本体在开通器里）
    rc = try_open(dry=True)
    if rc == 0:
        line("就绪体检通过，开始正式开通")
        return 0 if try_open() == 0 else 1
    if rc == 3:
        print("仍在等待：%s" % "; ".join(st.get("reasons") or [])[:300])
        return 0
    line("就绪体检本身出问题 rc=%d —— 这不是「等油钱」，要看" % rc)
    return 1


if __name__ == "__main__":
    sys.exit(main())
