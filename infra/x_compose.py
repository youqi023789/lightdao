#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""x_compose.py —— 把一条 X 文案组装成"最终要发的那串字"，规则集中在这里，可单测。

为什么单独成文件：这段逻辑先前散在 shell 的 case/heredoc 里，我改一次顺序就出一次新问题
（先是页脚挤掉锚点，然后锚点重复：正文里本来写着 lightdao.net，我又追加了一次 https://lightdao.net，
读起来像机器人发的）。放进一个函数里就能被真实断言测试，而不是"看一眼觉得没问题"。

规则（顺序即优先级）：
  1) 可核验锚点必须在场：区块高度 + 官网链接；
     正文已写 lightdao.net（不带协议）→ 就地升级成 https:// 形式，绝不重复追加第二个域名；
  2) 高度取不到 → 宁可不发（返回 over=False 且标记 blocked），也不写 "height 0" 这种假数字；
  3) 社交页脚是装饰：放得下才加；
  4) 连"正文+锚点"都超 280 加权字符 → 交给人改文案，脚本绝不自动截句。
"""
import re
import sys

LIMIT = 280
DOMAIN = "lightdao.net"
FULL_URL = "https://lightdao.net"
SOCIAL = "📡 Telegram: t.me/lightdao_news · Discord: discord.gg/9YY9X2Cdv"
# 只匹配"裸域名"：前面已经有 :// 的（即已经是 https://lightdao.net）不再动
BARE = re.compile(r"(?<!://)\b" + re.escape(DOMAIN) + r"\b")


def wlen(s):
    """X 按加权长度计（CJK 与多数全角符号算 2，ASCII 算 1）。"""
    return sum(2 if ord(c) > 0x2E7F else 1 for c in s)


def ensure_https(t):
    """把正文里所有裸域名升级成带协议的形式。
       上一版只换第一处，于是"访问 lightdao.net …（结尾又一行 lightdao.net）"的第 4 条
       留下一个裸域名，读起来像贴了两遍网址 —— 域名要么统一要么不出现。"""
    n = len(BARE.findall(t))
    if n:
        return BARE.sub(FULL_URL, t), ("裸域名升级为 https 形式 ×%d" % n)
    return t, ""


def compose(text, height):
    """返回 (最终文案, 说明)。说明里带 blocked 表示不该发帖。"""
    t = (text or "").strip()
    if not t:
        return "", "blocked：正文为空"
    notes = []
    # 1) 锚点：域名统一成 https 形式，绝不重复追加第二个域名
    t, msg = ensure_https(t)
    if msg:
        notes.append(msg)
    if FULL_URL not in t:
        t = t + "\n" + FULL_URL
        notes.append("补官网锚点")
    h = str(height or "").strip()
    if not h.isdigit():
        return t, "blocked：取不到真实区块高度，宁可不发也不写假数字"
    if "height " not in t.lower():
        t = t + "\nLightDAO height " + h
        notes.append("补区块高度锚点")
    with_social = t + "\n\n" + SOCIAL
    if wlen(with_social) <= LIMIT:
        return with_social, "带社交页脚；" + "；".join(notes)
    return t, "页脚放不下已省略；" + "；".join(notes)


def selftest():
    cases = [
        # (正文, 期望：不重复域名、必须含 https、必须含 height)
        ("传统私募,两种命运。\n\nlightdao.net", "bare-domain"),
        ("访问 lightdao.net 即可", "in-sentence"),
        ("1. 访问 lightdao.net 登录 ⏎ 2. 挖矿 ⏎ ⏎ lightdao.net", "double-domain"),
        ("已经写了 https://lightdao.net 的一段", "already-https"),
        ("什么链接都没有", "no-domain"),
        ("X" * 300, "over-long"),
    ]
    ok = True
    for t, tag in cases:
        out, why = compose(t, "617270")
        bare_left = len(BARE.findall(out)) > 0        # 装配后不该再有任何裸域名
        has_url = FULL_URL in out
        has_h = "height 617270" in out
        long_ok = wlen(out) <= LIMIT or tag == "over-long"
        bad = bare_left or (tag != "over-long" and (not has_url or not has_h or not long_ok))
        ok = ok and not bad
        print("  %s %-14s wlen=%3d %s" % ("OK  " if not bad else "FAIL", tag, wlen(out), why[:60]))
        if bad:
            print("       输出尾部：…" + out[-90:].replace("\n", " ⏎ "))
    # 取不到高度必须 blocked，且不能出现假数字
    out2, why2 = compose("正文 lightdao.net", "")
    b = ("blocked" in why2) and ("height 0" not in out2)
    ok = ok and b
    print("  %s %-14s %s" % ("OK  " if b else "FAIL", "no-height", why2[:50]))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    # 作为管道使用：stdin=正文，argv[1]=高度 → stdout=最终文案，退出码 3 表示 blocked
    body = sys.stdin.read()
    final, why = compose(body, sys.argv[1] if len(sys.argv) > 1 else "")
    sys.stderr.write(why + "\n")
    sys.stdout.write(final)
    sys.exit(3 if why.startswith("blocked") else 0)
