#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线上运维脚本 vs 仓库 的对账（同名≠同内容，必须逐字节比）。
背景：2026-10-16 已两次踩到"线上比仓库新"——promote.py 与 qa_truth.py 的仓库副本
缺了 g11 挂载和 status 缓存失效不变量，一旦按仓库重建机器，这两处防护会静默消失。
本脚本只读对账 + 可选把线上真相回填进 infra/（回填后还要跑泄露扫描与门禁哈希同步）。"""
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys

REPO = "/home/ubuntu/repo"
DIRS = ["/usr/local/bin", "/home/ubuntu"]
APPLY = "--apply" in sys.argv


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


# 仓库里每个文件名对应哪些副本
idx = {}
for dirpath, _d, files in os.walk(REPO):
    if "/.git" in dirpath:
        continue
    for fn in files:
        idx.setdefault(fn, []).append(os.path.join(dirpath, fn))

# cron 里引用到的脚本名
cron_txt = ""
for u in ("root", "ubuntu"):
    p = subprocess.run(["crontab", "-l", "-u", u] if u != "root" else ["crontab", "-l"],
                       capture_output=True)
    cron_txt += p.stdout.decode("utf-8", "replace")
cron_names = set(re.findall(r"/(?:usr/local/bin|home/ubuntu)/([A-Za-z0-9_.-]+\.(?:py|sh))",
                            cron_txt))

drift, missing, same = [], [], 0
for d in DIRS:
    for pat in ("*.py", "*.sh"):
        for f in sorted(glob.glob(os.path.join(d, pat))):
            b = os.path.basename(f)
            if b.startswith("._") or b == "run_chrome.sh":
                continue
            cands = idx.get(b) or []
            hs = sha(f)
            if not cands:
                missing.append((b, os.path.getsize(f), b in cron_names))
                continue
            if any(sha(c) == hs for c in cands):
                same += 1
            else:
                drift.append((b, f, cands[0], os.path.getsize(f), b in cron_names))

print("逐字节一致 %d 个" % same)
print("\n== 线上与仓库内容不同（%d 个）==" % len(drift))
for b, f, r, sz, in_cron in drift:
    print("   %-30s %8dB  cron在用=%s   仓库副本 %s" % (b, sz, "是" if in_cron else "否",
                                                  r.replace(REPO + "/", "")))
print("\n== 仓库里完全没有（%d 个，标 * 的是 cron 正在用的，必须先入库）==" % len(missing))
for b, sz, in_cron in sorted(missing, key=lambda x: (not x[2], -x[1])):
    print("   %s%-32s %8dB" % ("*" if in_cron else " ", b, sz))

if APPLY:
    n = 0
    for b, f, r, sz, in_cron in drift:
        shutil.copy2(f, r)
        n += 1
    for b, sz, in_cron in missing:
        if not in_cron:
            continue
        src = None
        for d in DIRS:
            if os.path.isfile(os.path.join(d, b)):
                src = os.path.join(d, b)
                break
        if src:
            shutil.copy2(src, os.path.join(REPO, "infra", b))
            n += 1
    print("\n已回填 %d 个文件（线上为准）" % n)
