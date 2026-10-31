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
    # 中文没有词边界，不能用 \b；这几个词是社媒上最常见的收益承诺/风险淡化说法
    # 「归零风险」是风险披露不是风险淡化：不能只用子串匹配（今天实测误伤第 9 条）
    (r"(稳赚|保本|保底|包赚|旱涝保收|无风险|(?<!归)零风险)", "中文风险淡化"),
    (r"(保证[^，。\s]{0,6}(收益|回报|盈利|赚)|承诺[^，。\s]{0,6}(收益|回报)|固定收益|收益保证)", "中文收益承诺"),
    (r"(年化|apy|apr|收益率?可达|躺赚|睡后收入|财富自由)", "中文收益率暗示"),
    (r"(必涨|必爆|翻倍|冲[0-9０-９.]+\s*(元|刀|u|usd)?|目标价|看到[0-9０-９.]+\s*(元|刀))", "中文价格暗示"),
    (r"(无脑(买|冲)|全仓|梭哈|闭眼买|错过不再|限时[^，。\s]{0,4}(抢|买))", "中文催购/鼓吹"),
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
        if raw.startswith("["):                 # 发帖脚本落的是 [{"text":..,"media":..}]
            try:
                data = json.loads(raw)
            except Exception as e:
                print("X-COMPLIANCE FAIL 文案文件不是合法 JSON: %s" % e)
                return 2
            items = []
            for it in (data if isinstance(data, list) else [data]):
                if isinstance(it, dict):
                    items.append(str(it.get("text") or it.get("body") or ""))
                else:
                    items.append(str(it or ""))
            if not any(s.strip() for s in items):
                print("X-COMPLIANCE FAIL 文案为空（取数失败也会走到这里，绝不发空稿）")
                return 2
            multi = items
            txt = " \n ".join(multi)
        else:
            txt = raw
            multi = [raw]
    if not txt:
        print("X-COMPLIANCE FAIL 文案为空（取数失败也会走到这里，绝不发空稿）")
        return 2
    def wl(s):                                            # X 按加权长度计数（CJK=2）
        return sum(2 if ord(c) > 0x2E7F else 1 for c in s)
    bad = []
    ws = [wl(s) for s in multi] if multi else [wl(txt)]
    # 逐条判定：X 的限制是"每条"280，拼接长度既会误杀多楼长文也会漏判
    for i, x in enumerate(ws, 1):
        if x > 280:
            bad.append("第 %d 条加权长度 %d 超 280" % (i, x))
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
    print("X-COMPLIANCE OK  各条加权长度 %s  文案: %s" % ("/".join(str(x) for x in ws), txt[:120]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
