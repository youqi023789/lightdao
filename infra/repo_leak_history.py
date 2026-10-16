#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""泄露门禁的历史维度：扫"将要推出去的提交"，而不是只扫工作树。
为什么要补这一刀（2026-10-16 实测）：pre-push 钩子只跑 `repo_leak_check.py <仓库>`，
它看的是当前工作树。于是"这一版写进去、下一版删掉再推"会全绿通过，
而 GitHub 的历史 blob 是公开可翻的 —— 老网关 IP 正是这种情况：
最初的 9c9c239 把它写进多个文档，后来 5ef6e38/6f89189 做了脱敏，工作树干净，
但历史里仍然查得到。门禁不能只保证"现在干净"。

做法：不复制一份规则（两份规则迟早各说各话），而是把每个待推提交的"新增行"
落成临时文件，再交给**同一个** repo_leak_check.py 去判。
用法：repo_leak_history.py [仓库目录] [rev 范围，默认 origin/main..HEAD]"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo"
RANGE = sys.argv[2] if len(sys.argv) > 2 else "origin/main..HEAD"
GATE = "/usr/local/bin/repo_leak_check.py"


def git(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True,
                       text=True, timeout=180)
    return r.returncode, r.stdout, r.stderr


rc, out, err = git("rev-list", "--max-count=200", RANGE)
if rc != 0:
    # 范围算不出来时必须喊，不能"当没事发生"放过一次推送
    print("HISTORY-GATE NOT IN EFFECT: 无法解析 rev 范围 %s: %s" % (RANGE, err.strip()[:160]))
    sys.exit(3)
commits = [c for c in out.split() if c]
if not commits:
    print("HISTORY OK：待推范围 %s 内没有提交（无需扫历史）" % RANGE)
    sys.exit(0)

work = tempfile.mkdtemp(prefix="ld_leakhist_")
bad = []
try:
    for sha in commits:
        rc2, patch, _ = git("show", "--no-color", "--format=", sha)
        if rc2 != 0:
            print("WARN 读不到提交 %s，按失败处理（不静默放过）" % sha[:8])
            bad.append((sha[:8], "commit-unreadable"))
            continue
        added = []
        fname = ""
        for ln in patch.splitlines():
            if ln.startswith("diff --git"):
                fname = ln.split(" b/")[-1][:80] if " b/" in ln else "?"
            if ln.startswith("+") and not ln.startswith("+++"):
                added.append(ln[1:])
        if not added:
            continue
        d = os.path.join(work, sha[:10])
        os.makedirs(d, exist_ok=True)
        # 每条新增行都落进同一个文件，行号丢了但命中定位靠提交号+文件名回查
        with open(os.path.join(d, "added_lines.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(added) + "\n")
        r = subprocess.run(["python3", GATE, d], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            hits = [l.strip() for l in (r.stdout or "").splitlines()
                    if re.search(r"FINDING|FAILS", l)]
            bad.append((sha[:8], "; ".join(hits)[:300] or "见门禁输出"))
    if bad:
        print("HISTORY LEAK: %d 个待推提交的新增内容含禁止项" % len(bad))
        for sha, why in bad[:8]:
            print("   提交 %s  %s" % (sha, why[:220]))
        print("   修复方式：把内容改掉后重新提交（不要用豁免；豁免只给确证的误报，"
              "且必须带理由与复核到期日）")
        sys.exit(1)
    print("HISTORY OK：扫了 %d 个待推提交的新增行，无禁止项" % len(commits))
finally:
    shutil.rmtree(work, ignore_errors=True)
