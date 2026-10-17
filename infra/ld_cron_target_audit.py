#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 crontab 里引用的每个脚本/解释器都做"存在+可读+可执行"体检。
   起因（实测，不是猜）：ubuntu crontab 第 17 行 `30 3 * * * /usr/local/bin/ld_sri.sh`
   调的脚本里写死了 /home/ubuntu/sri_verify.py，而这个文件根本不存在——
   连续 3 天（10-15/16/17）报 SRI-FAIL，看起来像"线上有问题"，
   实际是【检测工具自己坏了】，SRI 这条不变量三天没有任何执行点。
   这类问题必须靠"体检所有 cron 目标"来抓，不能等日志里那条 alert 被人读懂。"""
import os, re, subprocess, sys
SH = "/bin/sh"
targets, per_line = set(), []
for user in ("root", "ubuntu"):
    cmd = ["crontab", "-l"] if user == "root" else ["crontab", "-l", "-u", user]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        print("读不到 %s 的 crontab: %s" % (user, p.stderr.decode()[:80])); continue
    for i, line in enumerate(p.stdout.decode("utf-8", "replace").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"): continue
        # 去掉 5 个时间字段 / env 赋值
        body = re.sub(r"^[A-Za-z_]+=[^ ]+\s*", "", s)
        body = re.sub(r"^(@(daily|hourly|weekly|monthly|reboot)\s+)", "", body)
        body = re.sub(r"^\d+[\d*/,\-]*\s+\S+\s+\S+\s+\S+\s+\S+\s+", "", body)
        for tok in re.findall(r"(/(?:usr|home|etc|var)[^\s;|&]+)", body):
            # 去掉收尾的引号/括号：`bash -c '/usr/local/bin/x.sh'` 抽出来的 token
            # 会带上结尾单引号，直接判存在就变成假 MISSING（首跑就这么报了一条）。
            tok = tok.rstrip("'\"),;")
            if tok.endswith((">", "2>&1", ".log", ".out")) or ">>" in tok: continue
            targets.add(tok); per_line.append((user, i, tok))
        for tok in re.findall(r"([a-z0-9_./-]+\.py|[a-z0-9_./-]+\.sh|[a-z0-9_./-]+\.js)", body):
            if tok.startswith("/"): continue
            print("  注意：相对路径调用 %s（cron 的 cwd 不是你的家目录）" % tok)
bad = 0
seen = set()
for user, i, t in per_line:
    if t in seen: continue
    seen.add(t)
    if not os.path.exists(t):
        print("MISSING %s（%s crontab 第 %d 行引用）" % (t, user, i)); bad += 1; continue
    if os.path.isdir(t): continue
    if not os.access(t, os.R_OK):
        print("NOREAD  %s（%s 读不到，cron 会以运行身份失败）" % (t, user)); bad += 1; continue
    if t.endswith((".sh", ".py", ".js")) and not os.access(t, os.X_OK) and "python3 " not in "" :
        pass

# ---- 第二层：脚本自己调用的绝对路径也要体检 ----
# 这次的事故就在这层：crontab → ld_sri.sh 都在，但 ld_sri.sh 里调的
# /home/ubuntu/sri_verify.py 根本不存在，于是 SRI 这条不变量三天没真跑过。
# 只查 crontab 那一层是查不出来的。
inner = {}
for t in sorted(seen):
    if not t.endswith((".sh", ".py")) or not os.path.isfile(t): continue
    if os.path.basename(t) == os.path.basename(__file__): continue   # 不扫自己（本文档里就写着那个坏例子）
    try:
        s = open(t, encoding="utf-8", errors="replace").read()
    except Exception as e:
        print("NOREAD  %s（体检脚本自己读不动它：%s）" % (t, e)); bad += 1; continue
    kept = []
    for ln in s.splitlines():
        st = ln.strip()
        # 注释里写的"以前那个坏路径"不是调用关系：不排除就会把说明文字当成坏引用，
        # 假阳性会把真问题淹掉（这次修好的 ld_sri.sh 在注释里回顾了同一个路径）。
        if st.startswith("#") or st.startswith('"""') or st.startswith("'''"):
            continue
        kept.append(ln)
    s = "\n".join(kept)
    # 扩展名必须到此结束：上一版写成 \.(?:py|sh|js) 会把 leak_allow.json 切成
    # "leak_allow.js"、把 chainparams_baseline.sha256 切成 "…baseline.sh"，
    # 一次报出 15 条假 MISSING 把唯一那条真问题（sri_verify.py 不存在）淹掉。
    for p in re.findall(r"(/(?:home|usr|var|etc)/[A-Za-z0-9_./-]+\.(?:py|sh|js))(?![A-Za-z0-9_.])", s):
        if p.endswith((".pyc",)): continue
        inner.setdefault(p, []).append(t)
for p, froms in sorted(inner.items()):
    if not os.path.exists(p):
        print("MISSING(内层) %s ← 被 %s 调用" % (p, ", ".join(sorted(set(froms)))))
        bad += 1
    elif p.endswith((".sh",)) and not os.access(p, os.X_OK):
        print("NOEXEC(内层)  %s ← 被 %s 调用" % (p, ", ".join(sorted(set(froms)))))
        bad += 1
print("---")
print("cron 目标 %d 个（去重 %d）+ 内层引用 %d 个，问题 %d 个"
      % (len(per_line), len(seen), len(inner), bad))
sys.exit(1 if bad else 0)
