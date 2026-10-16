#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真机渲染验证治理页：只读首屏是否加载成功 + 提案分类是否生效。"""
import io
import re
import subprocess
import sys

OUT = "/tmp/g2.html"
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                "--virtual-time-budget=120000", "--dump-dom",
                "https://lightdao.net/governance.html"],
               stdout=open(OUT, "w"), stderr=subprocess.DEVNULL, timeout=220)
h = io.open(OUT, encoding="utf-8", errors="replace").read()
if not h:
    print("渲染无输出"); sys.exit(2)

t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
t = re.sub(r"(?s)<[^>]+>", " ", t)
t = re.sub(r"\s+", " ", t)
i = t.find("进行中的提案")
print("=== 提案区文本 ===")
print(t[i:i + 620] if i >= 0 else "(未找到标题)")
print()
seg = t[i:i + 120] if i >= 0 else ""
cards = len(re.findall(r'class="prop"', h))
dis = len(re.findall(r"<button[^>]*disabled", h))
res = {
    "仍停在加载中": ("加载中…" in seg),
    "出现分组提示": ("不计入进行中" in t),
    "出现作废标注": ("已作废/已过期" in t),
    "提案卡片数": cards,
    "禁用按钮数": dis,
}
for k, v in res.items():
    print("  %-14s %s" % (k, v))

bad = []
if res["仍停在加载中"]:
    bad.append("未连钱包仍读不到提案（只读首屏没生效）")
if cards < 1:
    bad.append("一个提案卡片都没渲染")
if not res["出现分组提示"]:
    bad.append("分类未生效（没有『不计入进行中』提示）")
if dis < 5:
    bad.append("已作废/过期提案的按钮未被禁用（禁用数=%d）" % dis)
print()
print("结果:", "GOV_RENDER_OK" if not bad else "GOV_RENDER_FAIL: " + " / ".join(bad))
sys.exit(0 if not bad else 1)
