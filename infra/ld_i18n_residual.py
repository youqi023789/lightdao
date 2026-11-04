#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-I18N-RESIDUAL-20261104  直接量"非中文界面里还剩多少中文"——渲染后的可见文本，
   不看词典行数、不看静态判据（静态量具今天先把我把 573 条正常文字也打成了漏翻，
   因为导航/英文表等机制我只扫了一半；**结论必须来自浏览器实际看到的东西**）。

白名单（这些"中文"是对的，不算漏翻）：
  · 语言切换器里的母语名（中文/日本語/한국어/العربية…）——按国际惯例用本族语写；
  · <title>/og 描述与合约地址、人名等专有名词按现状先不判（要改是产品决策，不是 bug）。
输出：每语种的残留片段清单（同一串去重），并给 rc（有残留=1，供 cron 报警/棘轮）。
"""
import os, re, subprocess, sys

CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                          "/usr/bin/chromium", "/usr/bin/chromium-browser"] if os.path.exists(c)), None)
BASE = os.environ.get("LD_BASE", "https://lightdao.net")
LOCALES = ["en", "es", "pt", "id", "vi", "fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"]
PAGES = (os.environ.get("LD_PAGES", "/") or "/").split(",")
CJK = re.compile(r"[\u4e00-\u9fff]{2,}")
NATIVE = ("中文", "日本語", "한국어", "العربية", "हिन्दी", "Deutsch", "Français", "Русский",
          "Português", "Español", "Bahasa", "Tiếng", "Türkçe", "Filipino", "Italiano")
# 这些串是"母语名列表/语言按钮"的组成部分，出现在任何界面都正常
STRIP = [re.compile(r"<(script|style|noscript|template)[^>]*>.*?</\1>", re.S),
         re.compile(r"<[^>]+>")]
budget = os.environ.get("LD_BUDGET", "45000")

if not CHROME:
    print("FAIL 没有 chrome，量具不可用（不当成通过）")
    sys.exit(1)

total = 0
for loc in LOCALES:
    leftovers = []
    for pg in PAGES:
        url = "%s%s%s?lang=%s" % (BASE, pg, "" if "?" in pg else "", loc)
        try:
            p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--ignore-certificate-errors", "--virtual-time-budget=" + budget,
                                "--dump-dom", url], capture_output=True, timeout=140)
            html = p.stdout.decode("utf-8", "replace")
            if not html.strip():
                # 空 DOM 不一定是页面问题：本项目的页里有 setInterval/动画，
                # --virtual-time-budget 会让 chrome 在这类页上吐空壳（10-16 就栽过同类坑）。
                # 所以空结果要**去掉 virtual-time 再量一次**，两次都空才算 FAIL。
                p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                                    "--ignore-certificate-errors", "--dump-dom", url],
                                   capture_output=True, timeout=140)
                html = p.stdout.decode("utf-8", "replace")
        except Exception as e:
            print("FAIL %s %s 渲染异常 %s" % (loc, pg, e)); total += 1; continue
        if not html.strip():
            print("FAIL %s %s 空 DOM（rc=%s）→ 不算通过" % (loc, pg, p.returncode)); total += 1; continue
        vis = html
        for rx in STRIP:
            vis = rx.sub(" ", vis)
        vis = re.sub(r"\s+", " ", vis)
        for m in CJK.finditer(vis):
            s = m.group(0)
            if any(n in vis[max(0, m.start() - 12):m.end() + 12] for n in NATIVE):
                continue
            leftovers.append(s)
    uniq = sorted(set(leftovers))
    if uniq:
        total += len(uniq)
        print("%-4s 残留 %d 种：%s" % (loc, len(uniq), " | ".join(uniq[:12])[:280]))
    else:
        print("%-4s 残留 0" % loc)
print("合计残留片段=%d" % total)
sys.exit(1 if total else 0)
