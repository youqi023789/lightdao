#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g16_i18n_boot —— 每页必须"语言引擎真的跑过"的门禁（真机渲染 + 判据自测）。

为什么要有它：词典齐全、分片按序引用（g12/g13 全绿）不等于页面被翻译。
实测 2026-11-06：app.html?lang=de、funds.html?lang=de 渲染完成后 <html> 上没有 data-ld-i18n，
而同一时刻手动调 window.__ldApplyLang("de") 立刻写出 w72 s221 —— 引擎是好的，
是启动那一次没生效（boot 的 try/catch 把它咽了）；用户端表现为德语页残留几十处中文，
而所有既有门禁全绿。这就是"静默不生效"，必须有独立检测点。

判据（每个页面 × 每个受检语种，真机渲染后的 DOM 上取）：
 1) data-ld-i18n 必须存在（中文页也要有：i18n.js 现在在 zh 分支也盖章）
 2) 值不能是 boot-miss:*（boot 自证重放后仍失败）
 3) data-ld-i18n-err 必须不存在（切换器/重放抛过错 = 响）
 4) 非中文页"看得见的"中文片段数 ≤ VMAX（抓"盖了章却没翻到"这一类）

--selftest 不复制站点目录（复制一份去渲染会被 SRI/SW/绝对路径等环境差异污染，
反而测不准），改为两层：
  A 判据层：5 段构造好的 HTML 送进判定函数，逐一确认"该响的响、该静的静"；
  B 量具层：真机渲染一个已知正常的页（canary），必须盖章 —— 浏览器/环境坏了要说"量具不可信"，
    而不是把"读不到"混成"通过"。
"""
import argparse
import os
import re
import subprocess
import sys
import time

CH = os.environ.get("I18N_BOOT_CHROME", "/usr/bin/google-chrome")
ALERTS = os.environ.get("I18N_BOOT_ALERTS", "/home/ubuntu/ld_alerts.log")
LOCALES = os.environ.get("I18N_BOOT_LANGS", "de,zh").split(",")
VMAX = int(os.environ.get("I18N_BOOT_VMAX", "6"))
CJK = re.compile(r"[\u4e00-\u9fff]{2,}")
NATIVE_NAMES = {"中文", "日本語", "한국어", "العربية", "हिन्दी", "繁體", "Русский", "Deutsch",
                "Français", "Português", "Español", "Tiếng", "Bahasa", "Türkçe", "Filipino"}
BUDGET = int(os.environ.get("I18N_BOOT_BUDGET", "12000"))


def line(msg, alarms=None):
    t = "%s I18N-BOOT %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(t)
    if alarms is not None:
        alarms.append(t)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(t + "\n")
    except Exception:
        pass


def render(url, budget=None, tries=2):
    """浏览器连续快速起停会偶发拿到空壳（实测 index/search 各挂过一次）。
       空壳不能算"页面没翻译"，必须先重试；重试仍空 = 量具不可信，报量具问题。"""
    last = ""
    for k in range(tries):
        p = subprocess.run([CH, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--ignore-certificate-errors",
                            "--virtual-time-budget=%d" % (budget or BUDGET),
                            "--dump-dom", url], capture_output=True, timeout=220)
        last = p.stdout.decode("utf-8", "replace")
        if len(last) > 2000:
            return last
        time.sleep(2 + 2 * k)
    return last


def judge(page, lang, html, alarms):
    """纯判定：没有渲染、没有 IO，可以被自测逐条钉死。返回 (是否通过, 失败类别)。"""
    m = re.search(r'data-ld-i18n="([^"]*)"', html)
    err = re.search(r'data-ld-i18n-err="([^"]*)"', html)
    if not m:
        line("%s[%s] 语言引擎没盖章（无 data-ld-i18n）—— 整片可能留中文" % (page, lang), alarms)
        return False, "nostamp"
    if m.group(1).startswith("boot-miss"):
        line("%s[%s] boot 自证失败：%s" % (page, lang, m.group(1)), alarms)
        return False, "bootmiss"
    if err:
        line("%s[%s] 语言层抛过错：%s" % (page, lang, err.group(1)[:90]), alarms)
        return False, "err"
    if lang != "zh":
        n, hid, bi, frags, nsk = visible_cjk(html, lang)
        if n > VMAX:
            # 长文档页（白皮书整篇 markdown）允许"没译完"，但必须**自己声明**还剩多少段：
            # 页面渲染后写 data-ld-wp-pending="N"。没声明、或声明数明显低于实测数（=粉饰），照样红。
            dec = re.search(r'data-ld-wp-pending="(\d+)"', html)
            doc_page = page in os.environ.get("I18N_BOOT_DOCPAGES", "whitepaper.html").split(",")
            if doc_page and dec and int(dec.group(1)) > 0 and int(dec.group(1)) >= n - 2:
                # 只写日志、不计入告警清单：这是"已声明的跟踪例外"，不是通过不了的故障
                line("%s[%s] 本语种仍有 %s 段未译（页面已如实声明，实测 %d；另有刻意双语对照 %d）——按跟踪例外放行"
                     % (page, lang, dec.group(1), n, bi))
                return True, None
            if doc_page and dec and int(dec.group(1)) > 0:
                line("%s[%s] 页面声明剩 %s 段，实测可见中文 %d —— 声明与实差不符"
                     % (page, lang, dec.group(1), n), alarms)
                return False, "cjk"
            line("%s[%s] 可见中文 %d > %d 且页面未自报剩余量（刻意双语对照 %d 处已另计，"
                 "日/韩正常汉字译文 %d 处已另计，隐藏区 %d 处）｜%s"
                 % (page, lang, n, VMAX, bi, nsk, hid, "、".join(frags[:8])), alarms)
            return False, "cjk"
    return True, None


BILING = re.compile(r"([\u4e00-\u9fff]{2,})\s*/\s*[A-Za-zÀ-ſ][\wÀ-ſ\s&.,'\-]*"
                    r"|[A-Za-zÀ-ſ][\wÀ-ſ\s&.,'\-]*\s*/\s*[\u4e00-\u9fff]{2,}")


def visible_cjk(html, lang=""):
    """只数"看得见的"：去脚本样式、去 hidden 块。
       站内有一批刻意写成「中文 / English」的对照标签（页脚、返回行、卡片小标题）：
       中文半边是本意，英文半边才由 i18n 换成本语种 —— 这类不计入漏翻，但**单列数量**，
       免得既拿它邀功"零残留"、又用它掩盖真没译的句子（11-05 的口径教训）。"""
    h = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", html)
    native_skipped = 0
    hid = len(CJK.findall(" ".join(re.findall(r"(?is)<[^>]*hidden[^>]*>.*?</[^>]+>", h))))
    h = re.sub(r"(?is)<[^>]*hidden[^>]*>.*?</[^>]+>", " ", h)
    v = re.sub(r"(?s)<[^>]+>", " ", h)
    v = re.sub(r"\s+", " ", v)
    bi = len({m.group(1) for m in BILING.finditer(v) if m.group(1)})
    v2 = BILING.sub(" ", v)
    resid = set()
    for m in CJK.finditer(v2):
        f = m.group(0)
        if f in NATIVE_NAMES:
            continue
        # 日语/韩语的**正常译文本身就用汉字/混排**：「資金とリリース」里切出的「資金」正好等于
        # 某个中文源串，就会被当成漏翻（11-05 实测 governance?lang=ja 报的 40 个"残留"全是正常日语）。
        # 判据：片段附近（±24 字）出现假名/谚文，说明这段已是日/韩文，不计漏翻，但单列数量看得见。
        if lang in ("ja", "ko"):
            w = v2[max(0, m.start() - 24): m.end() + 24]
            kana = bool(re.search(r"[぀-ヿ]", w))
            hangul = bool(re.search(r"[가-힯]", w))
            if (lang == "ja" and kana) or (lang == "ko" and hangul):
                native_skipped += 1
                continue
        resid.add(f)
    return len(resid), hid, bi, sorted(resid), native_skipped


def check_url(base, page, lang, alarms, tag=""):
    url = "%s/%s?lang=%s" % (base.rstrip("/"), page, lang)
    try:
        html = render(url)
    except Exception as e:
        line("%s 渲染失败 %s：%s（渲染失败 ≠ 通过）" % (tag, url, str(e)[:70]), alarms)
        return False
    # 环境不通要单独报：nginx 的 400/404 错误页里也有 <html>，若不加这一条，
    # "语言引擎没盖章"会把"量具接错了地址"伪装成"页面有 bug"（今天 promote 就这么挡过一次）。
    head = html[:1200]
    if re.search(r"400 Bad Request|404 Not Found|nginx</", head, re.I):
        line("%s 取到的不是页面而是错误页（%s）—— 量具/地址问题，不判通过"
             % (tag, re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", head))[:70]), alarms)
        return False
    if len(html) < 2000:
        line("%s %s 渲染内容为空/不是本站页面 —— 量具问题，不判通过" % (tag, url), alarms)
        return False
    ok, kind = judge(page, lang, html, alarms)
    if ok or kind != "cjk":
        return ok
    # 「超标」要再判一次：有些表格是异步取数后重排的，短预算下看到的是"还没轮到翻译"的中间态。
    # 复测给到 2 倍时间：仍然超标 = 真没投递到，红；复测达标 = 记一条"延迟收敛"留痕，放行。
    del alarms[-1]
    html2 = render(url, budget=BUDGET * 2, tries=1)
    al2 = []
    ok2, kind2 = judge(page, lang, html2, al2)
    if ok2:
        line("%s %s[%s] 首轮超标、复测（%dms）收敛 —— 判合格但记下延迟，不当成没问题"
             % (tag, page, lang, BUDGET * 2))
        return True
    for x in al2:
        alarms.append(x)
    return False


def pages_of(base):
    """页面清单来自站点目录（真实存在才算），不用缓存清单。"""
    root = os.environ.get("I18N_BOOT_ROOT", "/var/www/lightdao")
    out = []
    try:
        for f in sorted(os.listdir(root)):
            if f.endswith(".html") and not f.startswith("_"):
                out.append(f)
    except Exception:
        pass
    return out


def selftest():
    print("I18N-BOOT SELFTEST：判据层 5 例 + 量具层 canary 1 例")
    cases = [
        ("正常盖章 + 外语可见中文达标",
         '<html lang="de" data-ld-i18n="w21 s1041 same0 guard0"><body><p>Mein Konto</p></body></html>',
         "de", True),
        ("完全没盖章（本次修的这个 bug）",
         '<html lang="de"><body><p>我的账户</p></body></html>', "de", False),
        ("盖章但值为 boot-miss",
         '<html data-ld-i18n="boot-miss:0"><body></body></html>', "de", False),
        ("盖章但语言层抛过错",
         '<html data-ld-i18n="w1 s1" data-ld-i18n-err="switcher:x"><body></body></html>', "de", False),
        ("盖章了却没翻（可见中文超标）",
         '<html data-ld-i18n="w1 s9"><body>'
         + "".join("<p>漏翻%s</p>" % c for c in "甲乙丙丁戊己庚辛壬癸") + "</body></html>", "de", False),
    ]
    good = 0
    body = "".join("<p>漏翻%s</p>" % c for c in "甲乙丙丁戊己庚辛壬癸")
    for name, html, lang, want in cases:
        al = []
        got, _k0 = judge("t.html", lang, html, al)
        ok = (got == want) and (bool(al) == (not want))
        good += 1 if ok else 0
        print("  [%s] %s → 判=%s 期望=%s 告警=%d" % ("OK " if ok else "坏", name, got, want, len(al)))
    # 长文档页的"跟踪例外"必须是**自己声明**的：声明数与实差一致才放行，声明粉饰则拦
    al = []
    ok_dec, _k1 = judge("whitepaper.html", "de",
                   '<html data-ld-wp-pending="10" data-ld-i18n="w9 s9"><body>'
                   + body + "</body></html>", al)
    good += 1 if (ok_dec and not al) else 0
    print("  [%s] 长文档页自报 10 段、实测 10 片段 → 放行（并写日志留痕）"
          % ("OK " if (ok_dec and not al) else "坏"))
    al = []
    bad_dec, _k2 = judge("whitepaper.html", "de",
                    '<html data-ld-wp-pending="1" data-ld-i18n="w9 s9"><body>'
                    + body + "</body></html>", al)
    good += 1 if ((not bad_dec) and al) else 0
    print("  [%s] 声明只剩 1 段却实测 10 片段 → 必须拦（声明与实差不符）"
          % ("OK " if ((not bad_dec) and al) else "坏"))
    al = []
    no_dec, _k3 = judge("app.html", "de",
                   '<html data-ld-i18n="w9 s9"><body>' + body + "</body></html>", al)
    good += 1 if ((not no_dec) and al) else 0
    print("  [%s] 普通页超标且非长文档白名单 → 必须拦（不许拿白皮书口径当挡箭牌）"
          % ("OK " if ((not no_dec) and al) else "坏"))
    # 中文页不需要翻译，但必须有章（"引擎跑过"的证据），否则门禁看不见"没跑"
    al = []
    ok_zh, _k4 = judge("t.html", "zh", '<html lang="zh" data-ld-i18n="w0 s0 same0 guard0"><body><p>中文</p></body></html>', al)
    good += 1 if (ok_zh and not al) else 0
    print("  [%s] 中文页盖章即通过（不要求翻译）" % ("OK " if (ok_zh and not al) else "坏"))
    # 日语正常译文用汉字：假名在旁即认定已是日语，不能当漏翻（11-05 实测 ja 误报 40 处的老毛病）
    al = []
    ok_ja, _k5 = judge("t.html", "ja", '<html data-ld-i18n="w40 s80"><body>'
                       + "".join("<p>資金とリリース%d、ブロック検証</p>" % i for i in range(10))
                       + "</body></html>", al)
    good += 1 if (ok_ja and not al) else 0
    print("  [%s] 日语汉字译文不误报 %s" % ("OK " if (ok_ja and not al) else "坏",
          "" if ok_ja else "→ " + "; ".join(al)[-80:]))
    # 但日语下"整页真没翻"（周围没有假名）也必须报，不能借上面那条规则蒙过去
    al = []
    bad_ja, _k6 = judge("t.html", "ja", '<html data-ld-i18n="w1 s2"><body>'
                        + "".join("<p>未译段落%s说明</p>" % c for c in "甲乙丙丁戊己庚辛壬癸")
                        + "</body></html>", al)
    good += 1 if ((not bad_ja) and al) else 0
    print("  [%s] 日语真漏翻（无假名混排）必须报 %s" % ("OK " if ((not bad_ja) and al) else "坏",
          "" if not bad_ja else "→ 判成了通过"))
    # 量具层 A：环境不通必须报"量具问题"，不能报"引擎没盖章"（地址写成 http://:8093 就会这样）
    bad_base = os.environ.get("I18N_BOOT_BADBASE", "http://127.0.0.1:8093")
    al0 = []
    ck0 = check_url(bad_base, "index.html", "de", al0, tag="量具反例")
    ok0 = (not ck0) and al0 and ("量具" in al0[-1] or "渲染" in al0[-1])
    good += 1 if ok0 else 0
    print("  [%s] 量具层 反例：接错地址必须报「量具问题」而不是「引擎没盖章」%s"
          % ("OK " if ok0 else "坏", "" if ok0 else "→ " + (al0[-1][-90:] if al0 else "没告警")))
    # 量具层 B：真机渲染 canary 必须盖章
    base = os.environ.get("I18N_BOOT_CANARY_BASE", "https://127.0.0.1:8093")
    canary = os.environ.get("I18N_BOOT_CANARY", "index.html")
    al2 = []
    ck = check_url(base, canary, "de", al2, tag="canary")
    good += 1 if ck else 0
    print("  [%s] 量具层 canary（%s/%s[de]）真机渲染必须盖章 %s"
          % ("OK " if ck else "坏", base, canary, "" if ck else "→ " + "; ".join(al2)[-90:]))
    total = len(cases) + 8     # 判据 5 + 长文档例外 3 + 中文盖章 1 + 日语两条 2 + 量具反例 1 + canary 1
    print("SELFTEST %d/%d" % (good, total))
    return 0 if good == total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("I18N_BOOT_BASE", "https://lightdao.net"))
    ap.add_argument("--langs", default=",".join(LOCALES))
    ap.add_argument("--only", default="", help="逗号分隔的页面白名单（本地快测用）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    langs = [x for x in a.langs.split(",") if x]
    pl = [x for x in a.only.split(",") if x] or pages_of(a.base)
    if not pl:
        print("I18N-BOOT FAILS: 1（页面清单为空 —— 量具问题，不判通过）")
        return 1
    alarms = []
    bad = 0
    for pg in pl:
        for lang in langs:
            if not check_url(a.base, pg, lang, alarms, tag="线上"):
                bad += 1
    if alarms:
        print("I18N-BOOT FAILS: %d（%d 页 × %d 语种）" % (len(alarms), len(pl), len(langs)))
        return 1
    print("I18N-BOOT OK：%d 页 × %d 语种都盖章、无 boot-miss、无抛错、可见中文不超标"
          % (len(pl), len(langs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
