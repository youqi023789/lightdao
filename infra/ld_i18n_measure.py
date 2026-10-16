#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方案 B 工作量测量：全站每页在 ?lang=en 下还剩多少中文可见片段、多少字符，
并区分两种成因：
   A 类 = 词典里根本没有这条（需要新增词条）
   B 类 = 词典里有这条但 en 字段为空/缺失（需要补字段）
不区分就会白干：B 类补一条就全语种受益，A 类要逐条写译文。
输出 JSON 供后续脚本按页取用，不靠人抄。"""
import io
import json
import os
import re
import subprocess
import sys

BASE = "https://lightdao.net"
ROOT = "/var/www/lightdao"
OUT = "/home/ubuntu/ld_i18n_gap.json"
CHROME = "/usr/bin/google-chrome"


def render(path, budget=40000):
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--ignore-certificate-errors",
                        "--virtual-time-budget=%d" % budget,
                        "--dump-dom", BASE + path],
                       capture_output=True, timeout=140)
    return p.stdout.decode("utf-8", "replace")


def visible_text(html):
    b = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", "\n", b)
    return t


def zh_fragments(html):
    out = []
    for raw in visible_text(html).split("\n"):
        s = re.sub(r"\s+", " ", raw).strip()
        if not s:
            continue
        if re.search(r"[一-鿿]", s):
            out.append(s)
    # 合并同一元素被标签切断的碎片：只做长度>1 的去重
    seen, res = set(), []
    for s in out:
        if s in seen:
            continue
        seen.add(s)
        res.append(s)
    return res


def load_dict_keys():
    """把线上词典里已有的"中文原文 -> 有哪些语种"读出来（在浏览器里取 window.LDI18N）。"""
    js = ("JSON.stringify(Object.keys(window.LDI18N||{}).map(function(k){"
          "return [k, Object.keys(window.LDI18N[k]).join(',')]}))")
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--ignore-certificate-errors", "--virtual-time-budget=40000",
                        "--run-all-compositor-stages-before-draw",
                        "--virtual-time-bypass-css-fonts",
                        "--dump-dom", BASE + "/index.html?lang=en"],
                       capture_output=True, timeout=140)
    return None   # 词典结构改在下一步用文件解析，浏览器注入取不到稳定结果


def dict_from_files():
    """直接解析 i18n_*.js 里的 E("中文", { en:"...", ... }) 形式条目。"""
    d = {}
    for fn in sorted(os.listdir(os.path.join(ROOT, "js"))):
        if not fn.startswith("i18n"):
            continue
        s = io.open(os.path.join(ROOT, "js", fn), encoding="utf-8",
                    errors="replace").read()
        for m in re.finditer(r'E\(\s*"((?:[^"\\]|\\.)+)"\s*,\s*\{(.{0,900}?)\}\s*\)', s, re.S):
            src = m.group(1).encode().decode("unicode_escape")
            langs = set(re.findall(r"\b([a-z]{2,3})\s*:", m.group(2)))
            d[src] = {"langs": sorted(langs), "file": fn}
    return d


def main():
    dic = dict_from_files()
    print("词典已有条目 %d 条（来自 %d 个 i18n 文件）"
          % (len(dic), len([f for f in os.listdir(os.path.join(ROOT, "js"))
                            if f.startswith("i18n")])))
    pages = sorted("/" + f for f in os.listdir(ROOT) if f.endswith(".html"))
    only = sys.argv[1:] or pages
    report = {}
    for p in only:
        html = render(p + "?lang=en")
        frags = zh_fragments(html)
        a_cls, b_cls = [], []
        for s in frags:
            ent = dic.get(s)
            if ent is None:
                # 词典里没有整条：允许命中"包含关系"的已有词条（长句被切开的情况）
                hit = [k for k in dic if s and (s in k or k in s)]
                if hit:
                    b_cls.append(s)
                else:
                    a_cls.append(s)
            elif "en" not in ent["langs"]:
                b_cls.append(s)
            else:
                continue
        chars = sum(len(s) for s in a_cls + b_cls)
        report[p] = {"frags": frags, "nFrags": len(frags),
                     "A_无词条": len(a_cls), "B_缺en字段": len(b_cls),
                     "中文字符": chars,
                     "samples": (a_cls[:6] + b_cls[:3])}
        print("%-22s 中文片段 %3d  A 无词条 %3d  B 缺 en %3d  字符 %6d"
              % (p, len(frags), len(a_cls), len(b_cls), chars))
    tot_a = sum(r["A_无词条"] for r in report.values())
    tot_b = sum(r["B_缺en字段"] for r in report.values())
    print("\n全站合计：A 需新增词条 %d 条，B 只需补 en 字段 %d 条" % (tot_a, tot_b))
    json.dump(report, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("明细已写 %s" % OUT)


if __name__ == "__main__":
    main()
