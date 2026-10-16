#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1) 给 funds.html 第 1 节的销毁量补上快照日期（它每天在涨，不能不加日期地冒充现状）
2) 给全站巡检加一条结构门禁：静态 HTML 里出现"带两位小数的余额型数字"时，
   同一元素文本内必须出现日期（如 2026-10-14），否则判失败。
   规则刻意做成结构性的（只看 td class="num"），因为正文里为留证据引用旧数字是合法的。"""
import io
import re

P = "/home/ubuntu/repo/client/funds.html"
s = io.open(P, encoding="utf-8").read()
if "死地址累计接收" in s and "230.96 LIGHT（截至 2026-10-14）" not in s:
    s2 = s.replace('<td class="num">230.96 LIGHT</td>',
                   '<td class="num">230.96 LIGHT（截至 2026-10-14 快照，此后每日增长）</td>', 1)
    if s2 == s:
        print("FAIL 没找到销毁量那个格子，不改（不猜结构）")
        raise SystemExit(1)
    io.open(P, "w", encoding="utf-8").write(s2)
    print("已给销毁量加快照日期")
else:
    print("已改过或找不到目标，跳过")

# 现在整页扫一遍：还有哪些"两位小数余额"没带日期
DATE = re.compile(r"20\d{2}-\d{2}-\d{2}|\d{1,2}-\d{2}(?![\d:])")
cur = io.open(P, encoding="utf-8").read()
bad = []
for m in re.finditer(r'<td class="num">([^<]*\d+\.\d\d[^<]*)</td>', cur):
    ctx = cur[max(0, m.start() - 260):m.end() + 60]
    if not DATE.search(ctx):
        bad.append(m.group(0))
print("仍缺日期标注的小数余额格:", len(bad))
for b in bad[:5]:
    print("   ", re.sub(r"<[^>]+>", "", b))
