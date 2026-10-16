#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核实：code 18 是否真的不存在；governance 合约迁移历史；提案 14/15 的失败线索。"""
import json
import subprocess

RPC = "http://127.0.0.1:26657"
GOV = "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt"


def run(args):
    p = subprocess.run(args, capture_output=True, timeout=90)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        return None, (p.stderr.decode("utf-8", "replace") or s)[:200]
    try:
        return json.loads(s[i:]), ""
    except Exception as e:
        return None, "parse:%s %s" % (e, s[i:i + 120])


print("=== 1) 链上全部 code_id ===")
d, err = run(["wasmd", "q", "wasm", "list-code", "--node", RPC, "-o", "json",
              "--page-limit", "0"])
if not d:
    print("  查询失败:", err)
else:
    codes = d.get("code_infos") or []
    ids = sorted(int(c["code_id"]) for c in codes)
    print("  共 %d 个；id 列表: %s" % (len(ids), ",".join(map(str, ids))))
    print("  code 18 是否存在: %s" % (18 in ids))
    for c in codes:
        if int(c["code_id"]) >= 12:
            print("   code %-3s creator=%s" % (c["code_id"],
                                               (c.get("creator") or "")[:22]))

print("\n=== 2) governance 合约迁移历史 ===")
d, err = run(["wasmd", "q", "wasm", "contract-history", GOV, "--node", RPC,
              "-o", "json"])
if not d:
    print("  查询失败:", err)
else:
    for e in (d.get("entries") or []):
        print("   %-12s code_id=%-4s %s" % (e.get("operation"), e.get("code_id"),
                                            str(e.get("msg"))[:70]))

print("\n=== 3) 待作废的 5 个 governance 内部提案现状 ===")
for pid in (2, 5, 6, 7, 9):
    d, err = run(["wasmd", "q", "wasm", "contract-state", "smart", GOV,
                  json.dumps({"proposal": {"id": pid}}), "--node", RPC, "-o", "json"])
    if not d or not d.get("data"):
        print("   提案 %-2s 查询失败/不存在" % pid)
        continue
    p = d["data"]
    import datetime
    end = p.get("end")
    try:
        ts = datetime.datetime.utcfromtimestamp(int(end)).strftime("%Y-%m-%d")
    except Exception:
        ts = "?"
    print("   提案 %-2s %-28s executed=%-5s 到期=%s(%s) 已过=%s"
          % (pid, str(p.get("title"))[:28], p.get("executed"), ts, end,
             (end or 0) < __import__("time").time()))

print("\n=== 4) 活跃提案列表里还有几个 ===")
d, err = run(["wasmd", "q", "wasm", "contract-state", "smart", GOV,
              json.dumps({"active_proposals": {}}), "--node", RPC, "-o", "json"])
if d and isinstance(d.get("data"), list):
    import time
    now = time.time()
    expired = [x for x in d["data"] if (x.get("end") or 0) < now]
    print("   active_proposals 共 %d 个，其中已过期仍挂着 %d 个: %s"
          % (len(d["data"]), len(expired), [x.get("id") for x in expired]))
else:
    print("   查询失败:", err)
