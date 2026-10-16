#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD 合约字节码登记 v2：回捞 + 校验 + 用"源码长句命中率"给每个 code 定名。
命名优先级：敏感合约地址表 > 实例 label > 最匹配的源码 crate（至少命中 1 条长句）
> 无实例=orphan > unmatched。
写盘前把旧的 code*.wasm 移到 contracts/wasm/_pre_regen_<日期>/（不删除）。"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

REPO = "/home/ubuntu/repo"
W = os.path.join(REPO, "contracts/wasm")
SUMS = os.path.join(W, "SHA256SUMS")
RPC = "http://127.0.0.1:26657"
STORES = ["/home/ubuntu/.wasmd/wasm", "/home/ubuntu/.wasmd/data"]
APPLY = "--apply" in sys.argv
SENSITIVE = {
    "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt": "governance",
    "wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u": "treasury_multisig",
    "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx": "mining_reward",
    "wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z": "light_token",
    "wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x": "vesting",
    "wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6": "vesting-v2",
    "wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835": "ecosystem_fund",
    "wasm1wj3369pug9sdn5wcqu74yr00vtcntqvwgqrmcs0k0twwnvgm8m2qu77ewf": "insurance_fund",
}
CRATES = sorted(os.listdir(os.path.join(REPO, "contracts/contracts"))) \
    if os.path.isdir(os.path.join(REPO, "contracts/contracts")) else []


def jq(args):
    p = subprocess.run(args, capture_output=True, timeout=90)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        return None
    try:
        return json.loads(s[i:])
    except Exception:
        return None


def src_lits(crate):
    base = os.path.join(REPO, "contracts/contracts", crate, "src")
    lits = set()
    for dirpath, _d, files in os.walk(base):
        for fn in files:
            if fn.endswith(".rs"):
                t = open(os.path.join(dirpath, fn), encoding="utf-8",
                         errors="replace").read()
                for m in re.finditer(r'"([^"\\\n]{18,90})"', t):
                    s = m.group(1)
                    if re.search(r"[a-z]{4,} [a-z]{4,}", s) and "{}" not in s:
                        lits.add(s)
    return lits


CRIT = {c: src_lits(c) for c in CRATES if os.path.isdir(
    os.path.join(REPO, "contracts/contracts", c, "src"))}


def best_crate(blob_text):
    crate, hits, tot = "", 0, 0
    for name, lits in CRIT.items():
        if not lits:
            continue
        h = sum(1 for l in lits if l in blob_text)
        if h > hits:
            crate, hits, tot = name, h, len(lits)
    return crate, hits, tot


def find_file(chk):
    for root in STORES:
        if not os.path.isdir(root):
            continue
        for dp, _d, files in os.walk(root):
            for fn in files:
                if fn.lower().endswith(".wasm") and chk[:16] in fn.lower():
                    return os.path.join(dp, fn)
    return None


codes = (jq(["wasmd", "q", "wasm", "list-code", "--node", RPC, "-o", "json"])
         or {}).get("code_infos") or []
print("链上 code %d 个；%s" % (len(codes), "会写盘" if APPLY else "只查不写"))

if APPLY:
    bak = os.path.join(W, "_pre_regen_%s" % datetime.date.today().isoformat())
    os.makedirs(bak, exist_ok=True)
    for fn in sorted(os.listdir(W)):
        if fn.startswith("code") and fn.endswith(".wasm"):
            shutil.move(os.path.join(W, fn), os.path.join(bak, fn))
    print("旧 code*.wasm 已移到 %s" % os.path.relpath(bak, REPO))

table = []
for c in sorted(codes, key=lambda x: int(x["code_id"])):
    cid, chk = c["code_id"], (c.get("data_hash") or "").lower()
    f = find_file(chk)
    if not f:
        table.append((cid, chk[:16], 0, "-", "-", "字节码不在节点存储"))
        continue
    raw = open(f, "rb").read()
    if hashlib.sha256(raw).hexdigest() != chk:
        table.append((cid, chk[:16], 0, "-", "-", "FAIL 哈希与链上不符"))
        continue
    d = jq(["wasmd", "q", "wasm", "list-contract-by-code", cid, "--node", RPC,
            "-o", "json"]) or {}
    addrs = d.get("contracts") or []
    name = SENSITIVE.get(addrs[0] if addrs else "", "")
    crate, hits, tot = best_crate(raw.decode("latin1"))
    if not name:
        name = crate if (crate and hits) else ("orphan" if not addrs else "unmatched")
    if APPLY:
        out = os.path.join(W, "code%s_%s.wasm" % (cid, re.sub(r"[^A-Za-z0-9_.\-]", "_", name)))
        open(out, "wb").write(raw)
    table.append((cid, chk[:16], len(addrs), name, "%d/%d" % (hits, tot),
                  ("源码命中 %d/%d" % (hits, tot)) if tot else "无长句可比对"))

print("%-5s %-17s %-7s %-22s %-8s %s" % ("code", "校验和前16", "实例", "定名", "长句命中", "备注"))
print("-" * 96)
for r in table:
    print("%-5s %-17s %-7s %-22s %-8s %s" % tuple(str(x)[:24] for x in r))

if APPLY:
    lines = []
    for fn in sorted(os.listdir(W)):
        if fn.endswith(".wasm"):
            p = os.path.join(W, fn)
            lines.append((hashlib.sha256(open(p, "rb").read()).hexdigest(),
                          "contracts/wasm/" + fn))
    with open(SUMS, "w", encoding="utf-8") as s:
        for sha, rel in sorted(lines, key=lambda x: x[1]):
            s.write("%s  %s\n" % (sha, rel))
    print("-" * 96)
    print("SHA256SUMS 重写 %d 行（全部按文件实际 sha256 反算）" % len(lines))
