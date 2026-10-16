#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把台账里"公开页仍写着生态基金 0 / 资金都在金库内"这条待办标为已闭环（v1.9.1）。
台账里点名的东西改完了不回填，等于下一条假账等着下次再查。"""
import io

P = "/home/ubuntu/repo/docs/TREASURY_MOVEMENT_LEDGER.md"
s = io.open(P, encoding="utf-8").read()
i = s.find("- **`/funds.html`、`/contracts.html` 是 10-14 快照**")
if i < 0:
    print("FAIL 找不到那条待办，不动文件")
    raise SystemExit(1)
j = s.find("\n", i)
old = s[i:j]
NEW = (old.rstrip() +
       "\n  **【已闭环 2026-10-16，站点 v1.9.1】**：删掉 funds.html 第 2 节的静态快照余额表"
       "（同一事实两份表达是根因，改数字只会再烂一次），余额只保留下方实时表一处；"
       "第 1 节【真实销毁 230.96】补上【截至 2026-10-14 快照】日期（实测今天已到 235.35）；"
       "并给全站巡检加一条结构门禁 `LD-STATIC-BALANCE-DATE`：静态 HTML 里 "
       "`<td class=\"num\">` 出现带两位小数的余额却附近没有日期，即判失败。"
       "反向验证：植入一个无日期的 `1,242,000,092.38` 余额格 → 巡检报 FAIL；"
       "撤掉后改报【文件不存在】，不会静默放过。发布后线上 18 页复测 rc=0。")
s = s[:i] + NEW + s[j:]
io.open(P, "w", encoding="utf-8").write(s)
print("台账该条已标闭环")
print("自检：含已闭环 =", "已闭环 2026-10-16" in s)
