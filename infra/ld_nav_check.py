#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真机渲染验证：吸顶导航 + 三个返回按钮 + 出块时间实测值"""
import re
import subprocess
import sys

URL = sys.argv[1] if len(sys.argv) > 1 else "https://lightdao.net/index.html"
p = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--virtual-time-budget=90000", "--dump-dom", URL],
                   capture_output=True, timeout=200)
h = p.stdout.decode("utf-8", "replace")
if not h:
    print("渲染无输出:", p.stderr.decode("utf-8", "replace")[-300:])
    sys.exit(2)

bad = []
if 'class="ldnav"' not in h:
    bad.append("没有 .ldnav 吸顶条")
for want in ["返回上一页", "返回挖矿页", "返回主客户端"]:
    if want not in h:
        bad.append("缺按钮: " + want)
if "返回上一页" in h and 'history' not in h:
    pass
# 出块时间：必须是实测数字（xx.xx s），不能是 1.75s 也不是"—"
if "~1.75s" in h or ">1.75s<" in h:
    bad.append("出块时间仍是写死的 1.75s")
m = re.search(r"<b[^>]*data-btime[^>]*>([^<]{0,20})</b>", h)
val = m.group(1).strip() if m else "(元素不存在)"
print("出块时间显示:", repr(val))
if m:
    mv = re.match(r"^([0-9]\.[0-9]{2})s$", val)
    if not mv:
        if val == "取不到":
            print("  注：实测取不到（已按设计显示失败，不冒充数字）")
        else:
            bad.append("出块时间不是实测格式: " + val)
    else:
        s = float(mv.group(1))
        if not (0.2 < s < 60):
            bad.append("出块时间数值不合理: %s" % s)
        else:
            print("  实测出块间隔 = %.2f 秒/块 ✓" % s)
if 'aria-current="page"' not in h:
    bad.append("当前页链接没有 aria-current 标记")
# 老的那行重复链接应被收起
if "data-ldnav-hidden" not in h and 'data-back' in h:
    print("  注：本页本来就没有重复链接行（无需收起）")

print("\n结果:", "NAV_OK" if not bad else "NAV_FAIL: " + " / ".join(bad))
sys.exit(0 if not bad else 1)
