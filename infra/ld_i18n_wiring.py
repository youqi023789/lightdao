#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g13：机器表分片 + i18n 词典块的"接线一致性"门禁。

两条规则都来自真实事故，不是假想：
 A) 分片存在 ≠ 被引用。实测：磁盘上有 i18n_mt_1..7 七片、共 303 行译文，
    线上页面却只挂 1..5 五片 —— 6、7 两片里的长句运行时永远读不到，
    而当时 g1..g12 全绿（没人比对"片数 vs 页面引用"）。
 B) 每页的 i18n 清单必须一模一样。实测：18 个页面各挂一串 i18n_*.js，
    audit_logic/blog/… 少了 pages_en3，于是同一句「治理制度」在首页有译文、
    在这些页面上没有 → nav.js 退回它自带的中英小表 → 德语页面出现"德语正文 + 英语导航"，
    __ldTgaps 涨到 8 条，而且只在部分页面出现（最容易骗过抽查）。

规范顺序：i18n.js → i18n_core.js → 全部 pages_en*（英文回指表必须早于只填空槽的表，
v1.10.19 实测过）→ 其余人工表 → 全部 i18n_mt_*（机器表最后：先建键再展开）。

退出码：0 通过 / 1 不一致（promote 会因此拒绝发布）。
"""
import os
import re
import sys

JS_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo/client/js"
HTML_DIR = sys.argv[2] if len(sys.argv) > 2 else "/home/ubuntu/repo/client"


def num(f):
    return int(f.split("_")[-1].split(".")[0])


shards = sorted([f for f in os.listdir(JS_DIR) if re.match(r"^i18n_mt_\d+\.js$", f)], key=num)
# 顺序定义只有一处（ld_i18n_order.py）：门禁与页面重写各自算一份"正确顺序"时，
# 一边改了另一边没改 = 把正确的页面判成错（11-05 08:3x 实测就是这样）。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, "/usr/local/bin")
from ld_i18n_order import order_for
CANON = order_for(JS_DIR)
# 注意：promote 会给脚本标签注入 integrity/crossorigin，所以这里必须容忍属性，
# 否则"预发布目录里明明挂了、门禁却说不认识"——那是量具看错，不是页面出错（实测踩过）。
PAT = re.compile(r'<script\s+src="/js/(i18n(?:_[a-z0-9]+)*\.js)"[^>]*></script>')
ANCHOR = '<script src="/js/nav.js'
fails = []
pages = sorted(f for f in os.listdir(HTML_DIR) if f.endswith(".html")
               and not f.startswith("404-") and not f.startswith("_"))
for pg in pages:
    t = open(os.path.join(HTML_DIR, pg), encoding="utf-8").read()
    if ANCHOR not in t:
        fails.append("%s：找不到 nav.js 锚点（词典块该插在哪都说不清）" % pg)
    refs = PAT.findall(t)
    if not refs:
        if "i18n.js" in t or 'src="/js/i18n.js"' in t:
            fails.append("%s：引用写法不被识别（页面里看得到 i18n.js 却没匹配到脚本块）" % pg)
        continue
    if refs != CANON:
        miss = [x for x in CANON if x not in refs]
        extra = [x for x in refs if x not in set(CANON)]
        why = []
        if miss:
            why.append("少引用 %d 片：%s" % (len(miss), ",".join(miss[:6])))
        if extra:
            why.append("引用了不存在的 %s（会 404 并静默少一批译文）" % ",".join(extra[:4]))
        if not miss and not extra:
            why.append("顺序与规范不一致（同一句可能被后到的表覆盖成另一份译文）")
        fails.append("%s：%s ｜ 应有 %d 片，实际 %d 片" % (pg, "；".join(why), len(CANON), len(refs)))
if fails:
    print("G13 MT/I18N-WIRING FAILS: %d 处" % len(fails))
    for f in fails[:26]:
        print("  ✗ " + f)
    sys.exit(1)
print("G13 OK：%d 个页面都按规范顺序引用全部 %d 片词典（含机器表 %d 片）"
      % (len(pages), len(CANON), len(shards)))
sys.exit(0)
