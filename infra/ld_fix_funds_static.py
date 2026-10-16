#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""删掉 funds.html 第 2 节的"手工快照余额表"，只保留不会过期的白皮书额度列。
为什么删而不是改数字：同一事实有两份表达（静态表 + 实时表），静态那份必然再次腐烂。
本次实测它已经错了两笔：金库停在 1,242,000,092.38（实际 842,000,094.14，4 亿 10-15 已转出）、
生态基金合约写着 0（实际 400,000,000.00）。"""
import io
import re
import sys

P = "/home/ubuntu/repo/client/funds.html"
s = io.open(P, encoding="utf-8").read()
if "不再放手工快照余额" in s:
    print("已改过，跳过")
    raise SystemExit(0)

start = s.find('<h2>2. 四大资金池的链上余额')
if start < 0:
    print("FAIL 找不到第 2 节标题，不动文件")
    raise SystemExit(1)
tbl_end = s.find("</table>", start)
if tbl_end < 0:
    print("FAIL 找不到该节表格结束，不动文件")
    raise SystemExit(1)
tbl_end += len("</table>")

NEW = (
 '<h2>2. 四大资金池 <span class="st live">余额实时</span> '
 '<span class="en">Where the tokens actually sit</span></h2>\n'
 '<p class="note">本节<b>不再放手工快照余额</b>。以前这里有一张 2026-10-14 的静态表，'
 '与下方实时表构成<b>同一事实的两份表达</b>，结果静态那份一直停在错误数字：'
 '金库多签写着 <code>1,242,000,092.38</code>（4 亿已于 10-15 转出，实测 '
 '<code>842,000,094.14</code>），生态基金合约写着 <code>0</code>'
 '（实测 <code>400,000,000.00</code>）。现在余额只在下方的实时表出现一次，'
 '取不到数会明确显示取数失败，不会拿旧数字冒充现状。'
 ' <span class="en">Stale hand-made snapshot removed; balances are rendered live from the chain only once.</span></p>\n'
 '<table>\n'
 '<tr><th>资金池</th><th>白皮书额度</th><th>说明</th></tr>\n'
 '<tr><td>挖矿奖励池 <a href="/contracts.html">mining_reward</a></td>'
 '<td>1,000,000,000（40%）</td><td>每日按贡献分账，验证者份额 5% 已启用</td></tr>\n'
 '<tr><td>投资金库 <a href="/contracts.html">treasury_multisig</a></td>'
 '<td>850,000,000（34%）</td><td>3/5 多签 + 72 小时时间锁；余额见下方实时表</td></tr>\n'
 '<tr><td>生态基金 <a href="/contracts.html">ecosystem_fund</a></td>'
 '<td>400,000,000（16%）</td><td>10-15 起为独立合约持有，TGE 释放 30% 立即可用</td></tr>\n'
 '<tr><td>战略运营基金 <a href="/contracts.html">vesting</a> + '
 '<a href="/contracts.html">vesting-v2</a></td><td>250,000,000（10%）</td>'
 '<td>服务换代币 1.25 亿 / 战略融资 7500 万 / 核心贡献者 5000 万，均 12 个月 cliff</td></tr>\n'
 '<tr><td>保险基金 <a href="/contracts.html">insurance_fund</a></td>'
 '<td>利润 10% 计提</td><td>尚无利润可计提</td></tr>\n'
 '</table>')

s = s[:start] + NEW + s[tbl_end:]
io.open(P, "w", encoding="utf-8").write(s)
# 自检：本节内不该再有带两位小数的余额数字
seg = s[start:start + len(NEW)]
bad = re.findall(r"\d,\d{3},\d{3}(?:,\d{3})*\.\d\d", seg)
print("已替换第 2 节；新片段里带小数的余额数字:", bad or "无")
if bad:
    print("FAIL 新内容仍含余额型数字，回滚")
    raise SystemExit(2)
