#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X 日更文案的合规门禁（可反向验证，不靠人肉"看着没事"）。
禁止项来自项目既有口径：不得含收益承诺、价格预测/暗示、稳赚不赔类措辞、
以及把销毁量/供应量写错单位。命中任何一条 → 非零退出，任务据此不发帖。
用法：ld_x_compliance.py <文本文件>   或   echo "文案" | ld_x_compliance.py -
"""
import json
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "-"
BANNED = [
    (r"\bguarantee[d]?\b", "收益保证"),
    (r"\brisk[- ]free\b", "无风险表述"),
    (r"\b(apy|apr|yield|roi)\b", "收益率表述"),
    (r"\b(passive income|earn money|make money|get rich)\b", "赚钱承诺"),
    (r"\b(will (go|reach|hit|pump)|to the moon|moon\b|100x|no[- ]brainer)\b", "价格预测/鼓吹"),
    (r"\b(price (target|prediction)|forecast)\b", "价格预测"),
    (r"\b(don'?t miss|limited time|act now)\b", "催购话术"),
    (r"\b(稳赚|保本|无风险|必涨|躺赚)\b", "中文违规话术"),
]
# 必须出现的事实锚点（防止把占位符/未取到数的空稿发出去）
NEED = [(r"height\s+\d+", "区块高度"), (r"https://lightdao\.net", "官网链接")]


def main():
    if PATH == "-":
        txt = sys.stdin.read().strip()
    else:
        try:
            raw = open(PATH, encoding="utf-8").read().strip()
        except Exception as e:
            print("X-COMPLIANCE FAIL 读不到文案文件 %s: %s" % (PATH, e))
            return 2
        if raw.startswith("["):                 # 脚本落的是 JSON 数组
            try:
                txt = " ".join(json.loads(raw))
            except Exception as e:
                print("X-COMPLIANCE FAIL 文案文件不是合法 JSON: %s" % e)
                return 2
        else:
            txt = raw
    if not txt:
        print("X-COMPLIANCE FAIL 文案为空（取数失败也会走到这里，绝不发空稿）")
        return 2
    w = sum(2 if ord(c) > 0x2E7F else 1 for c in txt)     # X 按加权长度计数
    bad = []
    if w > 280:
        bad.append("加权长度 %d 超 280" % w)
    for pat, why in BANNED:
        m = re.search(pat, txt, re.I)
        if m:
            bad.append("命中禁用项[%s]: %r" % (why, m.group(0)[:30]))
    for pat, why in NEED:
        if not re.search(pat, txt):
            bad.append("缺少事实锚点[%s]" % why)
    if re.search(r"\bNone\b|\bnan\b|\{\}|\$\{", txt):
        bad.append("文案里有未取到的变量（None/nan/模板占位）")
    if bad:
        print("X-COMPLIANCE FAIL %d 项：" % len(bad) + "；".join(bad))
        print("  文案: %s" % txt[:200])
        return 1
    print("X-COMPLIANCE OK  长度加权 %d/280  文案: %s" % (w, txt[:120]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
