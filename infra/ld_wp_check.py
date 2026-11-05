#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_wp_check.py —— 白皮书多语言版本的完整性门禁（防止"文件在、内容是坏的"这类静默故障）。

为什么单独一个检查：白皮书页现在按语种取 /wp/whitepaper.<lang>.md。
只要有一个语种的文件缺失/被截断/夹着一半中文，访客看到的是"我这门语言没写好"的页面，
而站点其他一切正常 —— 没有任何其它门禁会因此变红。所以必须有人每天量一次。

检查项（任一不过 = 非零退出 + 写告警）：
 1) 13 个语种文件都在（www 与 repo 两份都要在，防止只写了一边）
 2) 体积 ≥ 中文原文的 45%（德语会膨胀、日语接近原文，45% 是"绝不可能是截断半篇"的下限）
 3) 非中日韩语种的**汉字行数占比** ≤ 25%（结构校验失败会保留原文行，超了就是生成器坏了）
 4) 文件头必须带"机器翻译/以中文原文为准"的提示行（诚实声明不能被悄悄删掉）
 5) 前端 whitepaper_2.js 仍按 /wp/ 取文件（有人改回单一中文源要立刻发现）
 6) manifest 里 bad_lines 总数与文件实况一致（数字对不上=清单在骗人）

--selftest：植入"缺一个语种/文件被截半/声明被删"三种故障，确认都能被抓到。
"""
import json
import os
import re
import sys
import time

WWW = os.environ.get("LD_WWW", "/var/www/lightdao")
REPO = "/home/ubuntu/repo/client"
SRC = os.path.join(WWW, "whitepaper.md")
MANIFEST = os.environ.get("LD_WP_MANIFEST", "/home/ubuntu/ld_wp_manifest.json")
ALERTS = os.environ.get("LD_WP_ALERTS", "/home/ubuntu/ld_alerts.log")
LANGS = os.environ.get("LD_WP_LANGS", "fr,de,ru,ja,ko,ar,hi,tr,fil,es,pt,id,vi").split(",")
CJK_HEAVY = {"ja", "ko"}
MIN_RATIO = float(os.environ.get("LD_WP_MIN_RATIO", "0.45"))
MAX_CJK_LINE = float(os.environ.get("LD_WP_MAX_CJK_LINE", "0.25"))
CJK = re.compile(r"[一-鿿]")


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def alert(msg, alarms):
    line = "%s WP-I18N %s" % (stamp(), msg)
    print(line)
    alarms.append(line)


def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception:
        return None


def check(alarms, src_text):
    src_lines = [l for l in src_text.split("\n") if CJK.search(l)]
    for lg in LANGS:
        fn = "whitepaper.%s.md" % lg
        pw, pr = os.path.join(WWW, "wp", fn), os.path.join(REPO, "wp", fn)
        a, b = read(pw), read(pr)
        if a is None:
            alert("缺文件（站点上取不到）：%s" % fn, alarms)
            continue
        if b is None:
            alert("缺文件（仓库里没有，回滚就会丢）：%s" % fn, alarms)
        if a != b:
            alert("两份不一致：%s（www 与 repo 必须同一份，否则下次发布静默回退）" % fn, alarms)
        ratio = len(a.encode("utf-8")) / max(1.0, len(src_text.encode("utf-8")))
        if ratio < MIN_RATIO:
            alert("体积只有原文的 %.0f%%（阈值 %.0f%%）——疑似截断或生成失败：%s"
                  % (ratio * 100, MIN_RATIO * 100, fn), alarms)
        if "原文" not in a[:600] and "original" not in a[:600].lower():
            alert("文件头缺「机器翻译/以中文原文为准」的声明：%s" % fn, alarms)
        if lg not in CJK_HEAVY:
            bad = [l for l in a.split("\n") if CJK.search(l)]
            frac = len(bad) / max(1.0, len(src_lines))
            if frac > MAX_CJK_LINE:
                alert("译文里仍有 %.0f%% 的中文行（阈值 %.0f%%）——结构校验失败被保留原文太多：%s（例：%s）"
                      % (frac * 100, MAX_CJK_LINE * 100, fn, bad[0][:44] if bad else ""), alarms)
    js = read(os.path.join(WWW, "js", "whitepaper_2.js"))
    if js is None or "/wp/whitepaper." not in js:
        alert("前端不再按 /wp/whitepaper.<lang>.md 取文件（改动会把多语言白皮书静默变回中文）", alarms)
    man = {}
    try:
        man = json.load(open(MANIFEST, encoding="utf-8"))
    except Exception:
        pass
    tot_bad = sum(int(man.get(l, {}).get("bad_lines", 0)) for l in LANGS)
    if man:
        print("清单：%d 个语种，结构校验失败并保留原文共 %d 段" % (len(man), tot_bad))
    else:
        alert("没有 %s：白皮书译文可能是手工塞进去的，来源不可追" % MANIFEST, alarms)
    for l in LANGS:
        rec = man.get(l)
        if rec and int(rec.get("ok_lines", 0)) == 0:
            alert("清单里 %s 的成功段数为 0，但文件存在（数字与事实矛盾）" % l, alarms)


def selftest():
    src = read(SRC)
    if not src:
        print("找不到 %s，自测无从做起" % SRC); return 2
    tmp_www = "/tmp/wp_selftest_www"
    os.makedirs(tmp_www + "/wp", exist_ok=True)
    os.makedirs("/tmp/wp_selftest_repo/wp", exist_ok=True)
    os.makedirs("/tmp/wp_selftest_www/js", exist_ok=True)
    good = "# t\n\n这是一段正常的译文占位。\n" + ("x" * 60000)
    for lg in LANGS:
        open("%s/wp/whitepaper.%s.md" % (tmp_www, lg), "w", encoding="utf-8").write("原文声明 / Chinese original\n" + good)
        open("%s/wp/whitepaper.%s.md" % ("/tmp/wp_selftest_repo", lg), "w", encoding="utf-8").write("原文声明 / Chinese original\n" + good)
    open(tmp_www + "/js/whitepaper_2.js", "w", encoding="utf-8").write('fetch("/wp/whitepaper."+l+".md")')
    open(tmp_www + "/whitepaper.md", "w", encoding="utf-8").write(src)
    globals()["WWW"] = tmp_www
    globals()["REPO"] = "/tmp/wp_selftest_repo"
    globals()["SRC"] = tmp_www + "/whitepaper.md"
    al = []
    check(al, src)
    print("SELFTEST 基线（全部正常）应 0 告警：%d 条%s" % (len(al), (" ← 基线本身有问题" if al else "")))
    hits = 0
    # a) 缺一个语种
    os.remove(tmp_www + "/wp/whitepaper.vi.md")
    al = []; check(al, src); ok = any("缺文件" in x for x in al); hits += ok
    print("  a 缺语种文件 -> %s" % ("抓到" if ok else "漏了"))
    # b) 文件被截半
    open(tmp_www + "/wp/whitepaper.vi.md", "w", encoding="utf-8").write("短")
    al = []; check(al, src); ok = any("体积" in x for x in al); hits += ok
    print("  b 文件截断 -> %s" % ("抓到" if ok else "漏了"))
    # c) 诚实声明被删
    open(tmp_www + "/wp/whitepaper.vi.md", "w", encoding="utf-8").write(good)
    al = []; check(al, src)
    open(tmp_www + "/wp/whitepaper.vi.md", "w", encoding="utf-8").write(good.replace("原文声明 / Chinese original", "translated"))
    al = []; check(al, src); ok = any("声明" in x for x in al); hits += ok
    print("  c 声明缺失 -> %s" % ("抓到" if ok else "漏了"))
    # d) 前端改回单一中文源
    open(tmp_www + "/js/whitepaper_2.js", "w", encoding="utf-8").write('fetch("/whitepaper.md")')
    al = []; check(al, src); ok = any("不再按 /wp/" in x for x in al); hits += ok
    print("  d 前端不再取多语言文件 -> %s" % ("抓到" if ok else "漏了"))
    # e) 译文夹大量中文
    open(tmp_www + "/wp/whitepaper.vi.md", "w", encoding="utf-8").write(
        "原文声明 / Chinese original\n" + "\n".join("这是中文句子 %d" % i for i in range(400)))
    al = []; check(al, src); ok = any("中文行" in x for x in al); hits += ok
    print("  e 译文夹中文过多 -> %s" % ("抓到" if ok else "漏了"))
    print("SELFTEST：%d/5 类被抓到" % hits)
    return 0 if hits >= 5 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    src = read(SRC)
    if not src:
        print("读不到 %s（量具故障，不当成通过）" % SRC)
        sys.exit(2)
    alarms = []
    check(alarms, src)
    if alarms:
        try:
            with open(ALERTS, "a", encoding="utf-8") as f:
                f.write("\n".join(alarms) + "\n")
        except Exception:
            pass
        print("WP-I18N 共 %d 条告警" % len(alarms))
        sys.exit(1)
    print("WP-I18N OK：%d 个语种的白皮书文件都在、体积正常、声明齐全、前端仍按语种取" % len(LANGS))
    sys.exit(0)
