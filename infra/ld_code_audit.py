#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""链上 code_id ↔ 本地产物 全量对账。
输出：每个 code 的 checksum、是否能在本机/仓库 wasm 产物里找到同名 sha256。
目的：量化"链上跑着但无法复现/审计的代码"有多少。"""
import json
import os
import subprocess

RPC = "http://127.0.0.1:26657"
ROOTS = ["/home/ubuntu/repo", "/home/ubuntu"]

# 1) 链上全部 code
p = subprocess.run(["wasmd", "q", "wasm", "list-code", "--node", RPC, "-o", "json"],
                   capture_output=True, timeout=90)
s = p.stdout.decode("utf-8", "replace")
i = s.find("{")
codes = (json.loads(s[i:]).get("code_infos") or []) if i >= 0 else []
print("链上 code 数量:", len(codes))

# 2) 本地产物 sha256 索引（只扫 .wasm，跳过节点内部存储目录以免自证）
local = {}
seen_dirs = set()
for root in ["/home/ubuntu/repo", "/home/ubuntu/lightdao-chain", "/home/ubuntu/builds",
             "/home/ubuntu/artifacts", "/home/ubuntu/wasmd-src"]:
    if not os.path.isdir(root):
        continue
    for dirpath, _dirs, files in os.walk(root):
        if "/.git/" in dirpath:
            continue
        for fn in files:
            if fn.lower().endswith(".wasm"):
                fp = os.path.join(dirpath, fn)
                try:
                    h = subprocess.run(["sha256sum", fp], capture_output=True,
                                       timeout=30).stdout.decode().split()[0]
                except Exception:
                    continue
                local.setdefault(h.lower(), []).append(fp)
print("本地仓库侧 wasm 产物:", sum(len(v) for v in local.values()), "个，唯一哈希",
      len(local), "个")

# 3) 对账
rows = []
for c in sorted(codes, key=lambda x: int(x["code_id"])):
    cid = c["code_id"]
    chk = (c.get("data_hash") or c.get("checksum") or "").lower()
    hits = local.get(chk, [])
    rows.append((int(cid), chk[:16], "✓" if hits else "✗",
                 os.path.relpath(hits[0], "/home/ubuntu") if hits else ""))

print("\n%-6s %-18s %-8s %s" % ("code", "checksum前16", "有产物", "产物路径"))
n_ok = 0
for cid, chk, mark, path in rows:
    print("%-6s %-18s %-8s %s" % (cid, chk, mark, path[:60]))
    n_ok += 1 if mark == "✓" else 0
print("\n可审计（本机能复现产物）: %d / %d" % (n_ok, len(rows)))
print("不可审计（链上有、本地产物里找不到）: %d 个 -> code_ids: %s"
      % (len(rows) - n_ok, [r[0] for r in rows if r[2] == "✗"]))

# 4) 生成产物清单（供门禁使用），只写仓库内产物
sums_path = "/home/ubuntu/repo/contracts/wasm/SHA256SUMS"
lines = []
for h, ps in sorted(local.items()):
    for fp in ps:
        if fp.startswith("/home/ubuntu/repo/"):
            lines.append("%s  %s" % (h, os.path.relpath(fp, "/home/ubuntu/repo")))
if lines:
    with open(sums_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sorted(set(lines))) + "\n")
    print("\n已生成 %s（%d 行）" % (sums_path, len(set(lines))))
