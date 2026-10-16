#!/usr/bin/env python3
"""ld_gov_fail_watch.py — 每15分钟扫描 x/gov 提案，发现新的 FAILED 立即告警。
背景：提案 #14 执行失败后静默约 26 小时才被人工发现（2026-10-13）。"""
import json, os, subprocess, sys, time, urllib.request

SEEN = "/home/ubuntu/ld_gov_failed_seen"
ALERTS = "/home/ubuntu/ld_alerts.log"
NODE = "tcp://127.0.0.1:26657"

def failed_ids():
    # 本版 CLI 无 --status 旗标；列全部后本地过滤，避免参数名漂移
    r = subprocess.run(["wasmd", "q", "gov", "proposals",
                        "--node", NODE, "-o", "json"],
                       capture_output=True, text=True, timeout=40)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None
    return [p["id"] for p in d.get("proposals", [])
            if p.get("status") == "PROPOSAL_STATUS_FAILED"]

def main():
    ids = failed_ids()
    if ids is None:
        # 查询失败本身也报，但只在连续失败时（避免节点抖动刷屏）
        n = int(open("/home/ubuntu/ld_gov_watch_errcount").read()) if os.path.exists("/home/ubuntu/ld_gov_watch_errcount") else 0
        n += 1
        open("/home/ubuntu/ld_gov_watch_errcount", "w").write(str(n))
        if n == 6:
            with open(ALERTS, "a") as f:
                f.write("%s ALERT gov-fail-watch cannot query proposals 6x\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            subprocess.run(["/usr/local/bin/discord_bot.py", "send", "⚠️ 治理失败监控连续 6 次无法查询提案"], capture_output=True)
        return
    if os.path.exists("/home/ubuntu/ld_gov_watch_errcount"):
        open("/home/ubuntu/ld_gov_watch_errcount", "w").write("0")
    seen = set()
    if os.path.exists(SEEN):
        seen = set(open(SEEN).read().split())
    new = [i for i in ids if i not in seen]
    if new:
        with open(ALERTS, "a") as f:
            for i in new:
                f.write("%s ALERT gov proposal FAILED id=%s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), i))
        subprocess.run(["/usr/local/bin/discord_bot.py", "send",
                        "⚠️ 治理提案执行失败：%s（用 wasmd q gov proposal <id> 看 failed_reason）" % ",".join(new)],
                       capture_output=True)
    with open(SEEN, "w") as f:
        f.write(" ".join(sorted(set(ids) | seen)))
    print("gov-fail-watch ok; failed_total=%d new=%d" % (len(ids), len(new)))

main()
