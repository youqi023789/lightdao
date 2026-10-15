#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-I18N-AUDIT-20261015
逐语种【真渲染】审计多语言，量的是"实际生效"，不是字典行数。
（历史教训：i18n_lat.js 的 hasOwnProperty 写错时，静态检查显示 376/376 全对，
 实际一条都没应用 —— 所以必须看运行时。）

指标：
  applied  页面自己上报的 writes（真被替换掉的文本节点数）
  cjk      渲染后可见文本里的中日韩字符占比（非中文语种越低越说明翻到了）
  guard    MutationObserver 自激熔断计数（必须为 0，否则有性能/循环风险）
棘轮：每个语种记录历史最好 cjk 占比；若明显倒退（比历史差 5 个百分点以上）→ 失败。
退出码非 0 = 有问题（可直接当门禁 g12）。
"""
import json
import os
import re
import subprocess
import sys

LOCALES = (sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "--quick"
           else ["en", "es", "pt", "id", "vi", "fr", "de", "ru", "ja", "ko", "ar", "hi"])
# 页面词典是全页共用的，首页字符串最密，用它做门禁样本即可（15 次渲染太慢）
PAGES = (sys.argv[2].split(",") if len(sys.argv) > 2 else ["/index.html"])
RATCHET = "/etc/lightdao/i18n_ratchet.json"
BASE = os.environ.get("LD_AUDIT_BASE", "https://lightdao.net")
CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                           "/usr/bin/chromium-browser"] if os.path.exists(c)), None)
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")


def render(url):
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=45000", "--dump-dom", url],
                       capture_output=True, timeout=170)
    return p.stdout.decode("utf-8", "replace")


def visible_text(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", h)


def stats_of(h):
    m = re.search(r'data-ld-i18n="([^"]*)"', h)
    d = {"writes": -1, "skips": -1, "same": -1, "guard": -1}
    if m:
        for kv in m.group(1).split():
            mm = re.match(r"(w|s|same|guard)(\d+)$", kv)
            if mm:
                d[{"w": "writes", "s": "skips", "same": "same",
                   "guard": "guard"}[mm.group(1)]] = int(mm.group(2))
    return d


def main():
    if not CHROME:
        print("无 chrome，无法做运行时审计")
        return 3
    try:
        old = json.load(open(RATCHET)) if os.path.exists(RATCHET) else {}
    except Exception:
        old = {}
    new = dict(old)
    bad = []
    print("%-5s %-14s %8s %8s %8s %8s" % ("语", "页面", "applied", "cjk%", "guard", "判定"))
    for L in LOCALES:
        for pg in PAGES:
            url = BASE + pg + "?lang=" + L
            h = render(url)
            if not h:
                bad.append("%s %s 渲染失败" % (L, pg))
                continue
            st = stats_of(h)
            txt = visible_text(h)
            n = len(txt.strip())
            cjk = (len(CJK.findall(txt)) / n * 100) if n else 0.0
            verdict = "ok"
            if L != "zh" and st["writes"] == 0 and st["same"] == 0 and n > 500:
                # 有内容却一条都没替换：要么没词典要么应用失效
                verdict = "无生效翻译"
            if st["guard"] not in (-1, 0):
                verdict = "熔断触发"
                bad.append("%s %s MutationObserver 熔断 guard=%s" % (L, pg, st["guard"]))
            key = L + ":" + pg
            best = old.get(key)
            if L not in ("zh", "ja", "ko") and best is not None and cjk > best + 5.0:
                verdict = "倒退"
                bad.append("%s %s cjk 从 %.1f%% 升到 %.1f%%（翻译覆盖倒退）" % (L, pg, best, cjk))
            if best is None or cjk < best:
                new[key] = round(cjk, 2)
            print("%-5s %-14s %8s %8.1f %8s %8s" %
                  (L, pg, st["writes"], cjk, st["guard"], verdict))
    try:
        tmp = RATCHET + ".tmp"
        json.dump(new, open(tmp, "w"), indent=1, sort_keys=True)
        os.replace(tmp, RATCHET)
    except Exception as e:
        print("(棘轮写入失败: %s —— 不影响审计结论)" % type(e).__name__)
    if bad:
        print("\nI18N-AUDIT FAILS: %d" % len(bad))
        for b in bad:
            print("   -", b)
        return 1
    print("\nI18N-AUDIT OK")
    return 0


sys.exit(main())
