#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反向验证 ld_render_watch 的检测器：坏 DOM 必须报错、好 DOM 不得误报。"""
import sys

src = open("/home/ubuntu/ld_render_watch.py", encoding="utf-8").read()
src = src.replace("\nmain()\n", "\npass  # 末尾调用已剥离，只测检测函数\n")
if "pass  # 末尾调用" not in src:
    print("找不到要剥离的 main() 调用行，拒绝继续（否则一 exec 就会真的去跑 chrome）")
    sys.exit(3)
g = {}
exec(compile(src, "rw", "exec"), g)

fails = []

# 坏首页：没有导航/按钮/出块元素
bad_index = "<html><body>" + "x" * 50 + "</body></html>"
r = g["check_index"](bad_index)
print("坏首页 -> 检出 %d 项" % len(r))
for x in r:
    print("     ", x)
if len(r) < 5:  # R1 + R2x3 + R3
    fails.append("坏首页漏报")

# 坏资金页：停在首次同步 + 有旧降级词 + 有静态快照 990,394,202.64（考验会不会被旧数字骗过）
bad_funds = ('<html><body class="ldnav">返回上一页 返回挖矿页 返回主客户端 '
             '首次同步中… 990,394,202.64 加载验证者失败</body></html>')
r = g["check_funds"](bad_funds)
print("坏资金页 -> 检出 %d 项" % len(r))
for x in r:
    print("     ", x)
if not any("R4" in x for x in r):
    fails.append("坏资金页未检出实时取数没跑通")
if not any("R5" in x for x in r):
    fails.append("未检出旧的静默降级词")

# 好资金页：最后同步 + 已执行 + 无降级词
good_funds = ('<html><body class="ldnav">返回上一页 返回挖矿页 返回主客户端 '
              '最后同步 2026-10-15 06:16 UTC 已执行 990,166,600.07</body></html>')
r = g["check_funds"](good_funds)
print("好资金页 -> 误报 %d 项 %s" % (len(r), r))
if r:
    fails.append("好资金页被误报")

# 好首页：实测出块 5.42s
good_index = ('<html><body class="ldnav">返回上一页 返回挖矿页 返回主客户端 '
              '<b id="sBt" data-btime>5.42s</b></body></html>')
r = g["check_index"](good_index)
print("好首页 -> 误报 %d 项 %s" % (len(r), r))
if r:
    fails.append("好首页被误报")

if fails:
    print("\n反向验证 FAIL:", " | ".join(fails))
    sys.exit(1)
print("\n反向验证 PASS：坏页面必报、好页面不误报")
