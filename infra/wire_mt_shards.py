#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按"实际存在的分片"精确挂 <script>，不靠手数。
   上一版我把分片数写死成 1..3，实际只生成两片，qa_site 立刻报"引用了不存在的资源"——
   门禁这次是帮我挡住了"页面 404 一个脚本、翻译表少一片"的事故。
   所以：先扫目录拿到真实分片名，再重写所有页面的挂载块（幂等，可重复跑）。"""
import glob, os, re

REPO = "/home/ubuntu/repo/client"
pat = re.compile(r"^i18n_mt_\d+\.js$")
shards = sorted((os.path.basename(p) for p in glob.glob(os.path.join(REPO, "js", "i18n_mt_*.js"))),
                key=lambda s: int(s.split("_")[-1].split(".")[0]))
shards = [s for s in shards if pat.match(s)]
if not shards:
    raise SystemExit("没有任何机器表分片，拒绝改页面")
INS = "".join('<script src="/js/%s"></script>' % s for s in shards)
ANCHOR = '<script src="/js/nav.js'

changed, bad = 0, []
for p in sorted(glob.glob(os.path.join(REPO, "*.html"))):
    t = open(p, encoding="utf-8").read()
    t = re.sub(r'<script src="/js/i18n_mt(?:_\d+)?\.js"></script>', '', t)
    if ANCHOR not in t:
        bad.append(os.path.basename(p))
        continue
    open(p, "w", encoding="utf-8").write(t.replace(ANCHOR, INS + ANCHOR, 1))
    changed += 1
print("分片=%s ｜ 重挂 %d 页 ｜ 无锚点=%s" % (",".join(shards), changed, bad or "无"))
