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
cron_names = set(re.findall(r"/(?:usr/local/bin|home/ubuntu)/([A-Za-z0-9_.-]+\.(?:py|sh|js))",
                            cron_txt))

drift, missing, same, unreadable = [], [], 0, []
for d in DIRS:
    # LD-RECON-JS-20261017 这里原本只有 py/sh：.js 的运维脚本（语种覆盖率、i18n 校验器）
    # 因此完全不在对账范围内，实测线上与仓库副本差 43 行跑了三周无人发现。
    # .js 只对 /usr/local/bin 生效——/home/ubuntu 下全是手搓工作副本，纳入只会噪声。
    pats = ("*.py", "*.sh", "*.js") if d == "/usr/local/bin" else ("*.py", "*.sh")
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(d, pat))):
            b = os.path.basename(f)
            if b.startswith("._") or b == "run_chrome.sh":
                continue
            cands = idx.get(b) or []
            hs = sha(f)
            if not cands:
                missing.append((b, os.path.getsize(f), b in cron_names))
                continue
            # LD-RECON-UNREADABLE-20261017 读不到≠不一致，也≠一致。
            # 之前 None 会参与比较：被扫文件读不到→假"内容不同"；
            # 仓库副本读不到→两边都是 None→假"一致"（真漂移被吞，更危险）。
            if hs is None:
                unreadable.append((b, f, "被测文件读不到（多半是权限，请用真实运行身份跑）"))
                continue
            rh = [(c, sha(c)) for c in cands]
            if any(h is None for _c, h in rh):
                unreadable.append((b, f, "有仓库副本读不到，无法判定，不算一致"))
                continue
            if any(h == hs for _c, h in rh):
                same += 1
            else:
                drift.append((b, f, cands[0], os.path.getsize(f), b in cron_names))

print("逐字节一致 %d 个" % same)
if unreadable:
    print("\n== 读不到、无法判定（%d 个）==" % len(unreadable))
    for b, f, why in unreadable:
        print("   %-30s %s  （%s）" % (b, f, why))
print("\n== 线上与仓库内容不同（%d 个）==" % len(drift))
for b, f, r, sz, in_cron in drift:
    # 必须印出"漂移的是哪一份"：同名脚本在 /usr/local/bin 与 /home/ubuntu 各有一份时，
    # 只印仓库路径会让人对着好的那份查半天（本轮真实发生过）。
    print("   %-30s %8dB  cron在用=%s\n      扫描到 %s\n      仓库副本 %s"
          % (b, sz, "是" if in_cron else "否", f, r.replace(REPO + "/", "")))
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

# ---- 门禁模式：漂移或未入库的 cron 脚本 = 非零退出 + 告警 ----
# 为什么值得当门禁：机器一旦重建，仓库里有的那套才是"真相"。线上有、仓库没有的
# 监控脚本会直接消失；线上比仓库新的脚本会被旧版覆盖掉（2026-10-16 实测：
# 73 个一致，10 个漂移，103 个仓库没有、其中 10 个正被 cron 调用）。
if "--gate" in sys.argv:
    _seen = set()
    hard = []
    for x in [d for d in drift if d[4]] + [m for m in missing if m[2]]:
        b = x[0]
        if b in _seen:
            continue          # 同一个脚本在 /usr/local/bin 和 /home/ubuntu 各有一份时，
        _seen.add(b)          # 只算一条，否则"2 个问题"其实是 1 件事，会把人带偏
        hard.append(x)
    line = ("ops-reconcile: 逐字节一致=%d 漂移=%d(cron在用=%d) 未入库=%d(cron在用=%d)"
            % (same, len(drift), sum(1 for x in drift if x[4]),
               len(missing), sum(1 for x in missing if x[2])))
    print(line)
    if hard:
        names = ", ".join(x[0] for x in hard[:8])
        msg = "ALERT [ops-reconcile] %d 个 cron 在用脚本与仓库不一致或未入库: %s" % (len(hard), names)
        print(msg)
        try:
            with open("/home/ubuntu/ld_alerts.log", "a") as f:
                import time as _t
                f.write("%s %s\n" % (_t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()), msg))
        except Exception as e:
            print("WARN 告警没落盘: %s（内容见上）" % e)
        sys.exit(1)
    # 非 cron 的漂移只提示不阻断：一次性脚本改过没回填属正常噪声，
    # 但列出来，别让它悄悄积累成"下次重建机器才发现"。
    if drift:
        print("提示（不阻断）：%d 个非 cron 脚本与仓库不同: %s"
              % (len(drift), ", ".join(x[0] for x in drift[:8])))
    print("OPS RECONCILE OK：cron 在用的脚本全部在库且逐字节一致")
    sys.exit(0)
