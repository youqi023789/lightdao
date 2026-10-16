#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反向验证 R6/R7：坏 DOM 必须被检出，好 DOM 不得误报。"""
import io
import sys

src = io.open("/home/ubuntu/ld_render_watch.py", encoding="utf-8").read()
for call in ("\nsys.exit(main())\n", "\nmain()\n"):
    if call in src:
        src = src.replace(call, "\npass  # 不真跑渲染\n")
if "不真跑渲染" not in src:
    print("找不到要剥离的 main() 调用，拒绝继续（否则会真的去跑 chrome）")
    sys.exit(3)
g = {}
exec(compile(src, "rw", "exec"), g)
check_gov = g["check_gov"]

cases = [
    ("好页面：有进行中+分组+禁用按钮",
     '<div class="prop">x</div><button disabled>a</button>'
     '<body>进行中的提案 #11 活着 以下 5 个提案已作废或已过期，不计入进行中 '
     '已作废/已过期</body>', 0),
    ("坏：永远停在加载中（未连钱包读不到）",
     '<body>进行中的提案 加载中… </body>', 1),
    ("坏：标了已作废但按钮没禁用",
     '<div class="prop">a</div><body>进行中的提案 #2 已作废/已过期 '
     '不计入进行中</body>', 1),
    ("坏：标了已作废但没分组说明",
     '<div class="prop">a</div><button disabled>x</button>'
     '<body>进行中的提案 #2 已作废/已过期</body>', 1),
    ("坏：既无卡片也无空状态",
     '<body>进行中的提案 </body>', 1),
    ("好：空状态明确",
     '<body>进行中的提案 暂无可投票的进行中提案</body>', 0),
]
bad = 0
for name, html, want_any in cases:
    f = check_gov(html)
    caught = bool(f)
    ok = (caught == bool(want_any))
    if not ok:
        bad += 1
    print("  %-38s 检出=%-5s 期望=%-5s %s"
          % (name, caught, bool(want_any), "OK" if ok else "FAIL"))
    if f:
        print("       ->", f[0][:88])
print()
print("反向验证:", "PASS" if bad == 0 else "FAIL(%d)" % bad)
sys.exit(0 if bad == 0 else 1)
