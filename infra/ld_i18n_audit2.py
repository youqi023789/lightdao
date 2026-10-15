#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-I18N-AUDIT v2 —— 量"真翻译"，不被英语回退骗过。

为什么换指标：v1 只看"残留中文比例"，而 ?lang=ru 若只是回退成英文，
残留中文同样是 0，会被误判成"已覆盖"。真实判据是：
  与英语渲染比 —— 文本几乎一致 = 没翻（英文回退）；不同且含目标文字 = 真翻。
输出每语种：与英文重合度、目标文字出现率、判定（真翻/英文回退/部分）。
"""
import json
import os
import re
import subprocess
import sys

BASE = os.environ.get("LD_AUDIT_BASE", "https://lightdao.net")
PAGE = (sys.argv[1] if len(sys.argv) > 1 else "/index.html")
CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                           "/usr/bin/chromium-browser"] if os.path.exists(c)), None)

# 各语种的"目标文字"判据（有脚本的用语种自带文字；拉丁语系只能靠与英文差异）
SCRIPT = {
    "ru": re.compile(r"[Ѐ-ӿ]"), "uk": re.compile(r"[Ѐ-ӿ]"),
    "ar": re.compile(r"[؀-ۿ]"), "hi": re.compile(r"[ऀ-ॿ]"),
    "ja": re.compile(r"[぀-ヿ]"), "ko": re.compile(r"[가-힯]"),
    "zh": re.compile(r"[一-鿿]"),
}
LATIN = {"es", "pt", "id", "vi", "fr", "de", "fil", "tr", "en"}


def render(lang):
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=60000", "--dump-dom",
                        BASE + PAGE + "?lang=" + lang],
                       capture_output=True, timeout=180)
    h = p.stdout.decode("utf-8", "replace")
    if not h:
        return None, None
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    m = re.search(r'<html[^>]*\blang="([a-z-]+)"', h)
    return t, (m.group(1) if m else "?")


def words(s):
    return re.findall(r"[0-9A-Za-zÀ-ɏ؀-ۿऀ-ॿ぀-ヿ가-힯]+", s.lower())


def jacards(a, b):
    A, B = set(a), set(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def main():
    if not CHROME:
        print("无 chrome"); return 3
    en, _ = render("en")
    if not en:
        print("英文基准渲染失败"); return 3
    E = set(words(en))
    print("基准 /index.html?lang=en：%d 词，样本 %s" % (len(E), PAGE))
    print("%-4s %-8s %-9s %-9s %s" % ("语", "声明", "与英文重合", "目标文字", "判定"))
    rows = []
    for L in ["es", "pt", "id", "vi", "fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"]:
        t, declared = render(L)
        if not t:
            rows.append((L, "-", "-", "渲染失败"))
            print("%-4s %-8s %-9s %-9s %s" % (L, "?", "-", "-", "渲染失败"))
            continue
        W = words(t)
        ov = jacards(W, list(E))
        if L in SCRIPT:
            hit = len(SCRIPT[L].findall(t)) / max(1, len(t)) * 100
            hs = "%.1f%%" % hit
            if hit < 1.0:
                verdict = "英文回退（未翻译）" if ov > 0.75 else "疑似未翻译"
            else:
                verdict = "真翻译" if ov < 0.80 else "部分（混英）"
        else:
            hs = "n/a(拉丁)"
            # 拉丁语系没有独有文字，只能看与英文差异是否明显 + 常见功能词
            FUNC = {
                "es": ["de", "los", "una", "para"], "pt": ["de", "uma", "para", "você"],
                "id": ["dan", "untuk", "dengan", "yang"], "vi": ["và", "cho", "của", "không"],
                "fr": ["les", "pour", "avec", "est"], "de": ["und", "für", "mit", "nicht"],
                "tr": ["ve", "için", "ile", "değil"], "fil": ["ang", "mga", "para", "ng"],
            }
            f = [w for w in FUNC.get(L, []) if re.search(r"\b%s\b" % w, t.lower())]
            hs = "功能词 %d/4" % len(f)
            if ov > 0.90 and len(f) == 0:
                verdict = "英文回退（未翻译）"
            elif len(f) >= 2 and ov < 0.85:
                verdict = "真翻译"
            elif len(f) >= 1:
                verdict = "部分（混英）"
            else:
                verdict = "疑似未翻译"
        rows.append((L, declared, "%.2f" % ov, hs, verdict))
        print("%-4s %-8s %-9s %-9s %s" % (L, declared, "%.2f" % ov, hs, verdict))
    n_true = sum(1 for r in rows if r[-1].startswith("真"))
    n_back = sum(1 for r in rows if "回退" in r[-1] or "未翻译" in r[-1])
    print("\n汇总：真翻译 %d / 英文回退或未译 %d / 共 %d" % (n_true, n_back, len(rows)))
    return 0


sys.exit(main())
