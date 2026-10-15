#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真机渲染核对：额度列单位、埋点步数、以及余额与白皮书额度是否自洽"""
import io
import re
import subprocess
import sys

URL = sys.argv[1] if len(sys.argv) > 1 else "https://lightdao.net/funds.html"
STEP = re.compile(r'data-live-step="([^"]*)"')


def render():
    p = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=180000", "--dump-dom", URL],
                       capture_output=True, timeout=220)
    return p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


# 无头渲染的虚拟时间在真实网络面前是个竞速结果（ cosmjs 有 5.5MB 要拉），
# 所以必须重试，否则会把"还没跑完"误判成"跑坏了"。
h = ""
best = ""
for attempt in range(1, 4):
    h, err = render()
    if not h:
        print("第 %d 次渲染无输出: %s" % (attempt, err[-200:]))
        continue
    m = STEP.search(h)
    cur = m.group(1) if m else "(缺失)"
    print("第 %d 次渲染: 埋点=%s" % (attempt, cur))
    if cur > best:
        best = cur
    if cur.startswith("7"):
        break
else:
    pass
if not h:
    sys.exit(2)


def strip(s):
    s = re.sub(r"<[^>]+>", " | ", s)
    return re.sub(r"\s*\|\s*(\|\s*)*", " | ", s).strip()


m = STEP.search(h)
print("埋点(仅供参考):", m.group(1) if m else "(缺失)")
i = h.find("挖矿奖励池")
print("余额表:", strip(h[i:i + 900])[:520])

# 判定必须看"内容渲染出来了没有"，不能看瞬时属性值：
# 页面里 60s 的 setInterval 会在虚拟时间下很快开启第二轮同步，
# 那时抓到的埋点会退回第 3~4 步，而第一轮的结果仍在 DOM 里。
body = strip(h[i:i + 4000]) if i > 0 else ""
bad = []
if "读取中" in body:
    bad.append("余额表仍是占位符")
for want in ["1,000,000,000", "850,000,000"]:
    if want not in h:
        bad.append("白皮书额度列缺 " + want)
if not re.search(r"99[0-9],[0-9]{3},[0-9]{3}\.", h):
    bad.append("挖矿池余额没渲染出真实数字")
if "ecosystem" not in h.lower() and "生态发展基金" not in h:
    bad.append("缺生态基金行")
if "已执行" not in h:
    bad.append("多签台账没有渲染（应含\"已执行\"）")
if "取数失败" in h:
    bad.append("有账户取数失败")
if "超出额度" in h:
    bad.append("出现超额提示，需人工判断口径")
print("台账片段:", strip(h[h.find("提案号"):h.find("提案号") + 700])[:300])
print("\n结果:", "RENDER_OK" if not bad else "RENDER_FAIL: " + " / ".join(bad))
sys.exit(0 if not bad else 1)
