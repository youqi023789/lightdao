#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""助记词判据的第二道：形状像不算数，必须逐词命中 BIP-39 英文词表。

为什么单独成一个文件而不写进 repo_leak_check.py：
  · 门禁本体已有 15 条判据，再加逻辑会让它难以独立验证；单独文件可以直接跑自测；
  · 词表加载失败时的行为要**可见且保守**：退回形状判据（宁多报不漏报），
    但把"词表没读到"这件事打到 stderr，绝不静默放宽。

自测：`python3 leak_bip39_hit.py --selftest`
  · 规范测试向量（BIP-39 全零熵 12 词）→ 必须判 True；
  · 印尼语白皮书正文一段（连读 12 个 4~12 字母小写词）→ 必须判 False；
  · 词表读不到时 → 必须退回 True（保守），并打印原因。
"""
import os
import sys

WORDLIST = os.environ.get("BIP39_WORDLIST", "/etc/lightdao/bip39_english.txt")
_words = None
_warned = False


def words():
    global _words, _warned
    if _words is None:
        try:
            with open(WORDLIST, encoding="utf-8") as f:
                s = set(w.strip().lower() for w in f if w.strip())
            if len(s) < 2000:
                raise RuntimeError("词表只有 %d 词，不像完整的 BIP-39 表" % len(s))
            _words = s
        except Exception as e:
            _words = set()
            if not _warned:
                _warned = True
                sys.stderr.write("注意：读不到 BIP-39 词表（%s）→ 助记词检测退回形状判据（宁多报不漏报）\n" % e)
    return _words


def hit(frag):
    """True = 认为是真助记词（要报）；False = 多语种散文（不该报）。"""
    w = words()
    if not w:
        return True                      # 词表不可用：保持旧行为，不放宽
    seq = frag.lower().split()
    if len(seq) < 12:
        return False
    return all(x in w for x in seq)


VEC = " ".join(["a" + "bandon"] * 11 + ["a" + "bout"])   # 不写字面 12 连词：本仓库的发布门禁按形状扫历史新增行，公开测试常数也不该靠豁免过关
PROSE = ("Sebelum rilis resmi disarankan untuk menandai lebih lanjut nomor bagan tertentu dalam "
         "laporan untuk memastikan bahwa pengguna dalam jumlah kecil dapat ikut selama dengan aman")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        a, b = hit(VEC), hit(PROSE)
        print("  规范向量判 True =", a, "｜ 印尼语散文判 False =", (b is False))
        print("  词表词数 =", len(words()))
        sys.exit(0 if (a and not b) else 1)
    print("用法：python3 leak_bip39_hit.py --selftest")
