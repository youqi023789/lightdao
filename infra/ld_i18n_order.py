#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n 脚本块的**唯一**顺序定义：页面挂载顺序与发布门禁判据必须来自同一处。

为什么要单独抽出来（今天刚踩的）：
  · normalize_i18n_blocks.py 把顺序改成"i18n_lat.js（展开器本体）必须排在所有表式批次之前"之后，
    g13 门禁里还留着另一份按字母序的算法 → 两边对"正确顺序"各有说法，门禁把正确的页面判成错
    （"应有 28 片，实际 28 片"——数量对、顺序判不同）。这正是本项目反复出现的
    "同一事实两份表达"，只不过这次发生在质检员身上。

规则（与浏览器里的行为一致）：
  i18n.js → i18n_core.js → 全部 pages_en*（中→英，创建键）
  → i18n_lat.js（定义 __ldExpandLangs）→ 其余人工表（b*、gov_labels、lat4/5/6、more…按名）
  → 全部 i18n_mt_*（机器表最后：先建键再展开，人工译文永远优先）
"""
import os
import re

EN_PREFIX = "i18n_pages_en"
EXPANDER_HOST = "i18n_lat.js"
FIRST = ["i18n.js", "i18n_core.js"]


def is_i18n(name):
    return bool(re.match(r"^i18n(_[a-z0-9]+)*\.js$", name))


def order_for(js_dir):
    allf = sorted(f for f in os.listdir(js_dir) if is_i18n(f))
    en = [f for f in allf if f.startswith(EN_PREFIX)]
    mt = sorted([f for f in allf if f.startswith("i18n_mt")],
                key=lambda s: int(s.split("_")[-1].split(".")[0]))
    head = [f for f in FIRST if f in allf]
    host = [EXPANDER_HOST] if EXPANDER_HOST in allf else []
    used = set(head) | set(en) | set(mt) | set(host)
    rest = [f for f in allf if f not in used]
    return head + en + host + rest + mt


if __name__ == "__main__":
    import sys
    print(" ".join(order_for(sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo/client/js")))
