#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 block_results 里挖 gov 提案 15 的执行错误。
提案 15 投票截止 2026-10-15T20:57:12Z，该时刻节点日志显示高度约 379641。
CometBFT 0.38 的事件属性是 base64，需解码后再匹配。"""
import base64
import json
import subprocess
import urllib.request

RPC = "http://127.0.0.1:26657"
TARGET_TIME = "2026-10-15T20:57"


def gj(path):
    try:
        return json.loads(urllib.request.urlopen(RPC + path, timeout=15).read().decode())
    except Exception as e:
        return {"_e": type(e).__name__}


def dec(v):
    try:
        return base64.b64decode(v).decode("utf-8", "replace")
    except Exception:
        return str(v)


# 1) 先定位投票截止对应的区块高度（按时间二分/线性逼近）
lo, hi = 379500, 379800
hit = None
for h in range(lo, hi):
    b = gj("/block?height=%d" % h)
    try:
        t = b["result"]["block"]["header"]["time"]
    except Exception:
        continue
    if t.startswith(TARGET_TIME) or t >= TARGET_TIME:
        hit = h
        print("投票截止 %s 对应首个区块高度 = %d (time=%s)" % (TARGET_TIME, h, t))
        break
if hit is None:
    print("在 %d-%d 未找到目标时间，改为直接扫描该区间的事件" % (lo, hi))
    hit = lo

# 2) 扫该高度起 12 个区块的 begin/end block 事件，找 gov/wasm 相关与错误
found = 0
for h in range(hit, hit + 12):
    r = gj("/block_results?height=%d" % h)
    res = r.get("result") or {}
    evs = []
    for k in ("begin_block_events", "end_block_events", "validator_set_updates"):
        for e in (res.get(k) or []):
            attrs = {dec(a.get("key", "")): dec(a.get("value", ""))
                     for a in (e.get("attributes") or []) if isinstance(a, dict)}
            evs.append((k, e.get("type"), attrs))
    for k, typ, a in evs:
        blob = " ".join(list(a.values())).lower()
        if typ in ("message", "wasm", "proposal", "error") or "proposal" in blob or "error" in blob:
            if any(x in blob for x in ("proposal", "migrate", "error", "wasm")):
                found += 1
                print("\n[高度 %d / %s / %s]" % (h, k, typ))
                for kk in ("action", "module", "proposal_id", "error", "sender",
                           "contract_address", "code_id", "key", "value"):
                    if kk in a:
                        print("   %-16s %s" % (kk, str(a[kk])[:180]))
                if found > 24:
                    break
if not found:
    print("\n该区间未匹配到相关事件；说明执行错误没有作为事件暴露，"
          "需要改用 ABCI 查询 gov 模块的 failed proposal logs 存储键。")
