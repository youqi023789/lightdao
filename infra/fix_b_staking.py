#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清掉我在生成 B 链创世时塞进去的**不存在字段**：
   SDK 0.50 的 staking 创世里没有 `last_power`（那是 comet 侧概念），报
   "unknown field \"last_power\" in types.GenesisState"。
   顺带把 bank.supply 之类保留原样，只做"删字段"，不猜新字段名。"""
import json, os

B = "/home/ubuntu/.lightd-testnet-b/config/genesis.json"
g = json.load(open(B, encoding="utf-8"))
st = g["app_state"]
removed = []
for section, key in (("staking", "last_power"), ("staking", "last_total_power")):
    if key in st.get(section, {}):
        st[section].pop(key)
        removed.append("%s.%s" % (section, key))
tmp = B + ".tmp"
json.dump(g, open(tmp, "w", encoding="utf-8"), indent=1)
os.replace(tmp, B)
print("删除字段：%s" % (removed or "无（本来就没有）"))
print("staking 现有键：%s" % sorted(st.get("staking", {}).keys()))
