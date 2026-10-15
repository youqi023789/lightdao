#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""脚本标签结构体检：
 A) <script ...> 元素内部又出现 <script（嵌套=后者永不加载）
 B) 同一文件里同一个 src 重复出现（重复下载/重复执行）
 C) <script 与 </script> 数量不等、或出现裸的 </script>
用法: ld_script_lint.py <web根> [--json]
退出码: 有问题=1（可直接当门禁）"""
import glob
import io
import os
import re
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "/var/www/lightdao"
as_json = "--json" in sys.argv

TAG = re.compile(r"<script\b[^>]*>", re.I)


def lint(path):
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    low = txt.lower()
    problems = []
    opens = len(re.findall(r"<script\b", low))
    closes = low.count("</script>")
    if opens != closes:
        problems.append("数量不等: <script>=%d </script>=%d" % (opens, closes))
    # 逐个 script 开标签：它到匹配 </script> 之间不应再出现 <script
    pos = 0
    seq = []
    while True:
        m = TAG.search(txt, pos)
        if not m:
            break
        start = m.end()
        end = low.find("</script>", start)
        if end < 0:
            problems.append("有未闭合的 <script> 于偏移 %d" % m.start())
            break
        inner = txt[start:end].strip()
        tag = m.group(0)
        src = re.search(r"src=[\"']([^\"']+)", tag)
        name = src.group(1) if src else "(inline %d 字节)" % len(inner)
        seq.append(name)
        if "<script" in inner.lower():
            problems.append("嵌套: %s 的元素体内又出现 <script（该脚本永不执行）" % name)
        pos = end + 9
    seen = {}
    for s in seq:
        seen[s] = seen.get(s, 0) + 1
    for s, n in seen.items():
        if n > 1:
            problems.append("重复加载 %d 次: %s" % (n, s))
    # 多余的 </script>：出现在任何 <script 开标签之后的裸闭合
    stray = 0
    for m in re.finditer(r"</script>", low):
        before = low[:m.start()]
        if before.count("<script") <= before.count("</script>"):
            stray += 1
    if stray:
        problems.append("发现 %d 个多余/裸的 </script>" % stray)
    return problems


out = []
for p in sorted(glob.glob(os.path.join(root, "*.html")) +
                glob.glob(os.path.join(root, "*", "index.html"))):
    pr = lint(p)
    if pr:
        out.append((p, pr))

if as_json:
    import json
    print(json.dumps({os.path.relpath(p, root): v for p, v in out},
                     ensure_ascii=False, indent=1))
else:
    if not out:
        print("SCRIPT-LINT OK  (%d 个 html 全部结构正常)"
              % len(glob.glob(os.path.join(root, "*.html"))))
        sys.exit(0)
    for p, pr in out:
        print("FAIL %s" % os.path.relpath(p, root))
        for x in pr:
            print("      -", x)
    print("\nSCRIPT-LINT FAILS: %d 个文件" % len(out))
sys.exit(1)
