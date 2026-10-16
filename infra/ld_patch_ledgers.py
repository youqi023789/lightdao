#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1) 把补记的 75M 条目插进资金台账（按时间就近的位置，不是简单追加到末尾）
2) 更新 WP_COVERAGE 第 30 行"密钥托管安全"：从 ❌ 改成 🟡，并写清
   已经有什么检测点、还缺什么、排期在哪。规则要求 ❌ 必须带排期，
   而这行原本连检测点都写着"待加"——实际我今天已经加了一个只覆盖金库签名钥的。"""
import re
import sys

LED = "/home/ubuntu/repo/docs/TREASURY_MOVEMENT_LEDGER.md"
NEW = open("/home/ubuntu/ledger_75m.md", encoding="utf-8").read()
WPC = "/home/ubuntu/repo/docs/WP_COVERAGE.md"

s = open(LED, encoding="utf-8").read()
if "vesting v2 资金重锁：75M" in s:
    print("台账已有该条目，跳过")
else:
    anchor = "## 2026-10-16 治理升级异常"
    if anchor not in s:
        print("FAIL 找不到插入锚点，不动台账")
        sys.exit(1)
    s = s.replace(anchor, NEW + anchor, 1)
    open(LED, "w", encoding="utf-8").write(s)
    print("台账已插入 75M 补记（在 10-16 治理异常条目之前）")

w = open(WPC, encoding="utf-8").read()
old = re.search(r"^\|\s*30\s*\|[^\n]*$", w, re.M)
if not old:
    print("FAIL WP_COVERAGE 找不到第 30 行，不改（不猜格式）")
else:
    row = old.group(0)
    print("原行:", row[:120])
    new_row = ("| 30 | 密钥托管安全 | (安全) | 🟡 | 金库 5 把签名钥 10-16 已从网关摘除（全盘明文=0），"
               "唯一备份=所有者持有密文+分离口令；deployer/operator 等运维钥匙仍在网关 test 钥匙环（明文等价） "
               "| `ld_treasury_keywatch.sh`（每小时 4 条不变量，植入明文文件反向验证会报） "
               "| ld_alerts.log | 已加（仅覆盖金库签名钥） "
               "| 缺口：运维钥匙未覆盖；5 把备份只有单份+单口令，需分发到独立主机/硬件（排期见 "
               "docs/TREASURY_KEY_OPERATIONS.md 的下一步） |")
    w = w.replace(row, new_row, 1)
    open(WPC, "w", encoding="utf-8").write(w)
    print("WP_COVERAGE 第 30 行已更新为 🟡 并写明剩余缺口与排期指向")
