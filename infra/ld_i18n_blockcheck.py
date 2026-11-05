#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g13 的第二条规则：所有页面的 i18n 脚本块必须**完全一致**（同一份清单、同一个顺序）。

发现过程：导航在 audit_logic 等页面上退回英文小表（__ldTgaps=8），一查到底是因为
18 个页面各挂一串 i18n_*.js，清单不一样 —— 同一句在 A 页有译文、在 B 页没有。
这类"每页一份事实"迟早再犯，所以直接把"必须一致"变成发布门禁。

规则：
  · 每页的 i18n 块（从 i18n.js 到最后一个 i18n_*.js）必须等于按规范顺序生成的清单；
  · 规范顺序 = i18n.js → i18n_core.js → 全部 pages_en*（英文回指表必须早于只填空槽的表）
    → 其余人工表 → 全部 i18n_mt_*（机器表最后，先建键再展开）；
  · 顺序不对也算失败（同一句会被后到的表覆盖成另一份译文）。
"""
import os
import re
import sys

JS_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo/client/js"
HTML_DIR = sys.argv[2] if len(sys.argv) > 2 else "/home/ubuntu/repo/client"
shards = sorted([f for f in os.listdir(JS_DIR) if re.match(r"^i18n_mt_\d+\.js$", f)],
                key=lambda s: int(s.split("_")[-1].split(".")[0]))
ALL = sorted([f for f in os.listdir(JS_DIR) if re.match(r"^i18n(_[a-z0-9]+)*\.js$", f)])
EN = [f for f in ALL if f.startswith("i18n_pages_en")]
REST = [f for f in ALL if f not in EN and not f.startswith("i18n_mt") and f not in ("i18n.js", "i18n_core.js")]
CANON = (["i18n.js"] + (["i18n_core.js"] if "i18n_core.js" in ALL else []) ) + EN + REST + shards
PAT = re.compile(r'<script src="/js/(i18n(?:_[a-z0-9]+)*\.js)"></script>')
bad = []
pages = sorted(f for f in os.listdir(HTML_DIR) if f.endswith(".html")
               and not f.startswith("404-") and not f.startswith("_"))
for pg in pages:
    t = open(os.path.join(HTML_DIR, pg), encoding="utf-8").read()
    refs = PAT.findall(t)
    if not refs:
        continue
    if refs != CANON:
        miss = [x for x in CANON if x not in refs]
        extra = [x for x in refs if x not in set(CANON)]
        why = []
        if miss:
            why.append("少 %d 片：%s" % (len(miss), ",".join(miss[:5])))
        if extra:
            why.append("多出不存在的 %s" % ",".join(extra[:3]))
        if not miss and not extra:
            why.append("顺序与规范不一致（同一句可能被后到的表覆盖成另一份译文）")
        bad.append("%s：%s（应 %d 片，实际 %d 片）" % (pg, "；".join(why), len(CANON), len(refs)))
if bad:
    print("I18N-BLOCK FAILS: %d 页" % len(bad))
    for b in bad[:20]:
        print("  ✗ " + b)
    sys.exit(1)
print("I18N-BLOCK OK：%d 个页面都按同一顺序引用全部 %d 片词典" % (len(pages), len(CANON)))
sys.exit(0)
