#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 chain B 的创世参数：验证失败信息是
     "expedited minimum deposit must be greater than minimum deposit: 100stake"
   —— A 链的 genesis 里 min_deposit 与 expedited_min_deposit 都是 100stake，
   而这一版 SDK 在 gentx 阶段才校验这条约束，所以直接把 B 的加急押金调高即可。
   只改 B 的文件，不碰 A。"""
import json, os, sys

B = "/home/ubuntu/.lightd-testnet-b/config/genesis.json"
g = json.load(open(B, encoding="utf-8"))
gov = g["app_state"].setdefault("gov", {})
params = gov.setdefault("params", {})


def bump(key):
    md = params.get("min_deposit") or []
    ed = params.get(key)
    if not ed:
        return
    base = int(ed[0]["amount"]) if ed and str(ed[0]["amount"]).isdigit() else 100
    want = max(base, 1000)
    # 必须严格大于 min_deposit
    if md:
        mn = int(md[0]["amount"])
        want = max(want, mn + 900)
        ed[0]["amount"] = str(want)
        ed[0]["denom"] = md[0]["denom"]
    print("%s → %s" % (key, ed[0]["amount"]))


bump("expedited_min_deposit")
# 顺带确认关键字段（便于后面查问题一眼看到）
print("min_deposit=%s" % params.get("min_deposit"))
print("voting_period=%s expedited_voting_period=%s" % (params.get("voting_period"), params.get("expedited_voting_period")))
tmp = B + ".tmp"
json.dump(g, open(tmp, "w", encoding="utf-8"), indent=1)
os.replace(tmp, B)
print("已写回 %s" % B)
