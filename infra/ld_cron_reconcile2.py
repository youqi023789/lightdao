#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G24 修订版：cron 实际任务 vs 仓库清单 双向对账。
为什么要重写（2026-10-16 实测）：
  · 旧版把清单路径写死成 /home/ubuntu/repo-push/docs/... —— 那个目录早已不存在
    （仓库现在在 /home/ubuntu/repo），于是它每天（如果有人跑的话）只会报
    "ERR manifest" 然后退出，等于这道门禁形同虚设；
  · 更糟的是它**根本没被排进任何 crontab**（grep 计数 0、告警日志 0 条），
    10-14 写了工具和清单就以为有防护了 —— 典型的"写了≠在跑"；
  · 旧 --gen 会把 `>> x.log 2>&1` 规整成命令尾部一个 "2"，生成的清单和线上对不上；
  · 旧告警只发 Discord，不落 /home/ubuntu/ld_alerts.log，Discord 挂了就没痕迹。
两个方向都必须查：线上有、清单没有 = 未登记的自动化（漂移）；
清单有、线上没有 = 文档承诺的自动化静默死亡。
用法：ld_cron_reconcile2.py            # 对账（cron 用）
      ld_cron_reconcile2.py --gen      # 从线上生成清单草稿（人工补 purpose 后提交）
      LD_MANIFEST=... 可覆盖清单路径；LD_CRON_USERS=root,ubuntu 可覆盖要查的用户。"""
import json
import os
import re
import subprocess
import sys
import time

MANIFEST = os.environ.get("LD_MANIFEST", "/home/ubuntu/repo/docs/CRON_MANIFEST.json")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
USERS = os.environ.get("LD_CRON_USERS", "root,ubuntu").split(",")


def note(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print("%s %s" % (ts, msg))
    try:
        with open(ALERTS, "a") as f:
            f.write("%s %s\n" % (ts, msg))
    except Exception as e:
        print("  WARN 告警没落盘 %s: %s —— 请用 root 跑或设 LD_ALERTS" % (ALERTS, e))


def try_discord(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send",
                        "[G24 cron-reconcile] " + msg], timeout=30, capture_output=True)
    except Exception:
        pass


def _strip_redir(s):
    """重定向必须整段去掉。旧版把 `>> x.log 2>&1` 截剩一个 `2` 留在命令尾部，
    导致生成的清单和线上永远对不上账。"""
    s = re.sub(r"\s#.*$", "", s.strip())
    s = re.sub(r">>?\s*\S+(\s+2>&1)?", "", s)
    s = re.sub(r"2>&1", "", s)
    s = re.sub(r"\s2$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_cmd(cmd):
    """清单里的 cmd 字段：只有命令，没有调度字段，绝不能砍前 5 个词。"""
    parts = _strip_redir(cmd).split()
    while parts and re.match(r"^[A-Z_][A-Z0-9_]*=", parts[0]):
        parts = parts[1:]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def norm(line):
    """一行 crontab：去掉调度字段（5 段或 @daily），再去掉重定向。"""
    s = re.sub(r"\s#.*$", "", line.strip())
    parts = s.split()
    while parts and re.match(r"^[A-Z_][A-Z0-9_]*=", parts[0]):
        parts = parts[1:]
    if parts and parts[0].startswith("@"):
        parts = parts[1:]
    else:
        parts = parts[5:]
    return _strip_redir(" ".join(parts))


def schedule(line):
    s = re.sub(r"\s#.*$", "", line.strip())
    parts = s.split()
    while parts and re.match(r"^[A-Z_][A-Z0-9_]*=", parts[0]):
        parts = parts[1:]
    if parts and parts[0].startswith("@"):
        return parts[0]
    return " ".join(parts[:5])


def live_jobs():
    out = []
    for u in USERS:
        args = ["crontab", "-l"] if u == "root" else ["crontab", "-l", "-u", u]
        if u == "root" and os.geteuid() != 0:
            args = ["sudo"] + args
        r = subprocess.run(args, capture_output=True, text=True, timeout=60)
        for ln in (r.stdout or "").splitlines():
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            c = norm(ln)
            if not c:
                continue
            out.append({"user": u, "cmd": c, "schedule": schedule(ln)})
    return out


def key(j):
    # 键必须含 schedule：同一命令跑多个调度时（线上 ld_finalize.sh 有 4 个时刻），
    # 只按命令去重会把 4 条并成 1 条，之后删掉其中 3 个时刻对账也发现不了。
    return (j["user"], j["cmd"], j.get("schedule", ""))


def main():
    live = live_jobs()
    if "--gen" in sys.argv:
        for j in sorted(live, key=lambda x: (x["user"], x["cmd"])):
            print(json.dumps({"user": j["user"], "schedule": j["schedule"],
                              "cmd": j["cmd"], "purpose": "TODO 补一句为什么需要它",
                              "added": time.strftime("%Y-%m-%d")}, ensure_ascii=False))
        print("# 共 %d 条；把输出并入 %s 的 jobs 数组，补 purpose 后提交"
              % (len(live), MANIFEST), file=sys.stderr)
        return 0

    if not os.path.exists(MANIFEST):
        note("ALERT [cron-reconcile] 清单不存在 %s —— 门禁无法执行（先修路径/权限，别当没事）"
             % MANIFEST)
        try_discord("manifest missing: %s" % MANIFEST)
        return 3
    try:
        man = json.load(open(MANIFEST, encoding="utf-8"))
    except Exception as e:
        note("ALERT [cron-reconcile] 清单不是合法 JSON: %s" % e)
        return 3
    jobs = man.get("jobs") or []
    if not jobs:
        note("ALERT [cron-reconcile] 清单 jobs 数组为空，等于没有登记任何任务")
        return 3
    want = {}
    for j in jobs:
        want.setdefault((j.get("user"), norm_cmd(j.get("cmd") or ""),
                         (j.get("schedule") or "").strip()), []).append(j)
    livek = {}
    for j in live:
        livek[key(j)] = j

    undocumented = [j for k, j in sorted(livek.items()) if k not in want]
    missing = [k for k in sorted(want) if k not in livek]
    # 清单里尾部带 "2" 这类历史脏数据：单独点名，别让它靠"永远匹配不上"混过去
    dirty = [j.get("cmd") for j in jobs if re.search(r"\s2$", j.get("cmd") or "")]
    print("线上 cron 条目 %d（用户 %s）；清单登记 %d 条"
          % (len(livek), "/".join(USERS), len(jobs)))
    for j in undocumented:
        print("  未登记: [%s] %s  %s" % (j["user"], j["schedule"], j["cmd"][:96]))
    for u, c, sch in missing:
        print("  清单有但线上没跑: [%s] %s  %s" % (u, sch, c[:88]))
    if dirty:
        print("  清单脏数据（命令尾部残留 `2`，是旧 --gen 的截断产物）%d 条，例：%s"
              % (len(dirty), dirty[0][:70]))
    if undocumented or missing:
        msg = ("ALERT [cron-reconcile] 未登记自动化 %d 条 / 清单承诺但静默死亡 %d 条"
               % (len(undocumented), len(missing)))
        note(msg)
        try_discord(msg.replace("ALERT [cron-reconcile] ", ""))
        return 1
    if dirty:
        print("  （脏数据不阻断，但必须清掉：它们让对账长期失真）")
    print("CRON-RECONCILE OK：%d 条线上任务全部有登记，清单里也没有失联项" % len(livek))
    return 0


if __name__ == "__main__":
    sys.exit(main())
