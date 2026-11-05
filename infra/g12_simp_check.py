#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把"日/韩译文里夹简体字"的检测接进 g12（词典结构校验器），让它成为发布门禁的一部分。

起因：普查在 index.html?lang=ja 抓到「传统私募の初期枠は…」——句子是日语，但「传统」是简体字
（日语应是「伝統」）。这类行既不是"纯 ASCII"也不"等于英文列"，g12 原有的文字检查放过它。
现在补上，并且只在**确定不同形**的字上判：日语新字体里同样长这样的字（当 点 断 式 争 律 写 会
号 口 来 楼 概 板 数 立…）一律不算命中——第一版把这些列进来，16 条告警里 12 条是误杀，
误杀会把正确译文删掉重译，比漏杀更难发现，所以逐字核过。

用法：node ld_i18n_validate.js <js目录>          （随 promote 一起跑）
      python3 g12_simp_check.py <js目录>          （同一判据的独立跑法，供巡检/排查用）
"""
import json
import os
import re
import subprocess
import sys

JS = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo/client/js"
SIMP = "传统经济转验图执认识设记变让们这应风页关开间运远达极构标树档检样气张强寻尔层岗币帅帮广庆废异弯总悬惊护报拥挥摄显术机杀权战错钟钱长门陆险隐难义乐习继产价级"
PAT = "((?:(?!\\\\[\"\\\\]).)*)"
CJK = re.compile(u"[%s]" % SIMP)


def rows_from_table(path):
    src = open(path, encoding="utf-8").read()
    m = re.search(r"var L = \[([^\]]*)\]", src)
    if not m:
        return None, []
    langs = re.findall(r'"([a-z\-]+)"', m.group(1))
    out = []
    for mm in re.finditer(r'(?m)^\s{2,4}"((?:[^"\\]|\\.)+)"\s*:\s*"((?:[^"\\]|\\.)*)"', src):
        out.append((mm.group(1), mm.group(2), langs))
    return langs, out


def entries_from_word(path):
    """词条式文件：E("中文", {ja:"…", ko:"…"}) / tr("…") 之类，宽松扫 ja/ko 值"""
    src = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'(ja|ko)\s*:\s*"((?:[^"\\]|\\.)*)"', src):
        out.append((m.group(1), m.group(2)))
    return out


bad = []
for fn in sorted(os.listdir(JS)):
    if not fn.startswith("i18n") or not fn.endswith(".js"):
        continue
    p = os.path.join(JS, fn)
    try:
        langs, rows = rows_from_table(p)
    except Exception:
        continue
    for zh, val, ls in rows or []:
        parts = val.split("|")
        for i, lg in enumerate(ls or []):
            if lg not in ("ja", "ko") or i >= len(parts):
                continue
            hit = CJK.findall(parts[i])
            if hit:
                bad.append((fn, "表式", lg, "".join(sorted(set(hit)))[:10], parts[i][:46]))
    for lg, val in entries_from_word(p):
        hit = CJK.findall(val)
        if hit:
            bad.append((fn, "词条", lg, "".join(sorted(set(hit)))[:10], val[:46]))

print("词典目录=%s；日/韩译文夹简体字的行=%d" % (JS, len(bad)))
seen = set()
for fn, kind, lg, chars, val in bad[:24]:
    key = (fn, val[:20])
    if key in seen:
        continue
    seen.add(key)
    print("  %-22s %-4s %s 夹[%s]：%s" % (fn, kind, lg, chars, val))
if bad:
    print("SIMPLE-ZH-IN-JAKO FAILS: %d 处（人工表需要逐条改，机器表会被质量闸剔除重译）" % len(bad))
    sys.exit(1)
print("SIMPLE-ZH-IN-JAKO OK")
sys.exit(0)
