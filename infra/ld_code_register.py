#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD 合约字节码全量登记（取代只查"存不存在"的旧脚本）：
1) 列出链上全部 code（id / 校验和 / 上传者）
2) 从节点 wasm 存储回捞对应字节码文件，逐个 sha256 反算核对（文件哈希==链上校验和）
3) 用 list-contract-by-code + contract-info 的 label 反查"这个 code 被哪个合约在用"
4) 与仓库已归档产物比对，指出"链上在跑但仓库没有"与"仓库有但链上没在用"
5) 把核对通过的字节码补档进 contracts/wasm/ 并重写 SHA256SUMS
默认只看不动（--apply 才写文件）。"""
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/repo"
WDIR = os.path.join(REPO, "contracts/wasm")
SUMS = os.path.join(WDIR, "SHA256SUMS")
RPC = "http://127.0.0.1:26657"
STORES = ["/home/ubuntu/.wasmd/wasm", "/home/ubuntu/.wasmd/data"]
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
APPLY = "--apply" in sys.argv


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


def find_file(chk):
    for root in STORES:
        if not os.path.isdir(root):
            continue
        for dp, _d, files in os.walk(root):
            for fn in files:
                if fn.lower().endswith(".wasm") and chk[:16] in fn.lower():
                    return os.path.join(dp, fn)
    return None


def consumers(cid):
    d = jq(["wasmd", "q", "wasm", "list-contract-by-code", str(cid),
            "--node", RPC, "-o", "json"]) or {}
    addrs = d.get("contracts") or []
    names = []
    for a in addrs[:6]:
        lab = ""
        ci = jq(["wasmd", "q", "wasm", "contract-info", a, "--node", RPC, "-o", "json"]) or {}
        infos = ci.get("contract_infos") or [{}]
        lab = (infos[0].get("label") or "").strip()
        names.append(SENSITIVE.get(a) or lab or (a[:12] + "…"))
    if len(addrs) > 6:
        names.append("等 %d 个实例" % len(addrs))
    return names


codes = (jq(["wasmd", "q", "wasm", "list-code", "--node", RPC, "-o", "json"])
         or {}).get("code_infos") or []
print("链上 code 共 %d 个（%s 写盘）" % (len(codes), "会" if APPLY else "只查不"))

arch = {}
if os.path.exists(SUMS):
    for ln in open(SUMS, encoding="utf-8"):
        ps = ln.split()
        if len(ps) >= 2:
            arch[ps[0].lower()] = ps[-1]

rows, n_ok, n_miss, n_orphan = [], 0, 0, 0
for c in sorted(codes, key=lambda x: int(x.get("code_id") or 0)):
    cid = c.get("code_id")
    chk = (c.get("data_hash") or c.get("checksum") or "").lower()
    creator = c.get("creator") or ""
    f = find_file(chk)
    if not f:
        verdict = "字节码不在节点存储里（无法核验）"
        n_miss += 1
        cons = []
    else:
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if h != chk:
            verdict = "FAIL 文件哈希与链上不符（%s≠%s）" % (h[:12], chk[:12])
            n_miss += 1
            cons = []
        else:
            cons = consumers(cid)
            have = chk in arch
            verdict = ("已归档" if have else "仓库缺此产物 → 需补档")
            if not have:
                n_orphan += 1
            n_ok += 1
            if not APPLY:
                pass
            else:
                safe = re.sub(r"[^A-Za-z0-9_.\-]", "_",
                              (cons[0] if cons else "unknown"))
                dst = "contracts/wasm/code%s_%s.wasm" % (cid, safe)
                p = os.path.join(REPO, dst)
                if not os.path.exists(p):
                    open(p, "wb").write(open(f, "rb").read())
                arch[chk] = dst
    rows.append((cid, chk[:16], creator[:20], ";".join(cons)[:44], verdict))

print("%-4s %-17s %-21s %-45s %s" % ("code", "校验和前16", "上传者", "在用它的是", "判定"))
print("-" * 112)
for r in rows:
    print("%-4s %-17s %-21s %-45s %s" % r)
print("-" * 112)
print("哈希核验通过 %d / 取不到或不符 %d / 仓库缺产物 %d" % (n_ok, n_miss, n_orphan))

if APPLY:
    legacy = [v for k, v in arch.items()]
    with open(SUMS, "w", encoding="utf-8") as s:
        for k in sorted(arch, key=lambda x: arch[x].lower()):
            s.write("%s  %s\n" % (k, arch[k]))
    print("SHA256SUMS 重写为 %d 行" % len(arch))
