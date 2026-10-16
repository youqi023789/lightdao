#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全地往 crontab 加一行：只增不删，任何"行数变少/内容丢失"都拒绝安装。
起因：2026-10-16 我用 shell 链式命令 `A && B && C || { echo >> /tmp/x && crontab /tmp/x; }`
加一条 cron，A 失败后直接跳到 || 分支，而 /tmp/x 根本没被前面的步骤创建，
结果把 root 的整张 crontab（18 条）覆盖成 1 条，root 侧所有定时任务停摆约 1 分钟。
根因不是手滑，是"用一次性 shell 链改关键状态、且没有任何防缩水校验"。
用法：ld_cron_add_safe.py <root|ubuntu> "<整行 crontab 内容>" """
import subprocess
import sys

WHO = sys.argv[1] if len(sys.argv) > 1 else "root"
LINE = sys.argv[2] if len(sys.argv) > 2 else ""
if WHO not in ("root", "ubuntu") or not LINE.strip():
    print(__doc__)
    sys.exit(2)
if len(LINE.split()) < 6:
    print("FAIL 这行不像合法 crontab 条目（字段太少）：%r" % LINE)
    sys.exit(2)


def read():
    args = ["crontab", "-l"] if WHO == "root" else ["crontab", "-l", "-u", WHO]
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if r.returncode != 0 and "no crontab" not in (r.stderr or "").lower():
        print("FAIL 读取现有 crontab 失败，拒绝写入:", (r.stderr or "").strip()[:120])
        sys.exit(3)
    return r.stdout or ""


base = read()
bl = [l for l in base.splitlines() if l.strip()]
if len(bl) < 5 and WHO == "root":
    print("FAIL 现有 crontab 只有 %d 条，与预期（root 十几条）不符，"
          "先查是不是已经被破坏，不在坏状态上继续写" % len(bl))
    sys.exit(4)
if LINE in base:
    print("已存在，跳过（不重复加）")
    sys.exit(0)

new = base.rstrip("\n") + "\n" + LINE.strip() + "\n"
nl = [l for l in new.splitlines() if l.strip()]
if len(nl) != len(bl) + 1:
    print("FAIL 新内容行数 %d != 原 %d + 1，拒绝安装" % (len(nl), len(bl)))
    sys.exit(5)
# 原有每一行都必须还在（只增不删的硬检查）
gone = [l for l in bl if l not in nl]
if gone:
    print("FAIL 有 %d 条原任务会丢失，拒绝安装。第一条：%s" % (len(gone), gone[0][:80]))
    sys.exit(6)

tmp = "/tmp/ld_cron_add_%s.tmp" % WHO
open(tmp, "w").write(new)
args = ["crontab", tmp] if WHO == "root" else ["crontab", "-u", WHO, tmp]
r = subprocess.run(args, capture_output=True, text=True, timeout=60)
if r.returncode != 0:
    print("FAIL 安装失败:", (r.stderr or r.stdout)[:200])
    sys.exit(7)
after = [l for l in read().splitlines() if l.strip()]
if len(after) != len(bl) + 1 or LINE.strip() not in "\n".join(after):
    print("FAIL 安装后校验不符：原 %d 条，现 %d 条" % (len(bl), len(after)))
    sys.exit(8)
print("OK 已加入一条（%s 的 crontab：%d → %d 条）" % (WHO, len(bl), len(after)))
