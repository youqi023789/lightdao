#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读：枚举各 keyring 的账户名 -> 地址，并标注它是不是金库签名人/根投票账户。
金库签名人地址来自多签合约的 signers 查询；根投票账户来自 validator_registry 的
config.authorized —— 都不靠我手抄，避免用错地址做安全判断。
本脚本只调用 keys show -a（地址是公开信息），绝不导出/打印私钥。"""
import glob
import json
import os
import subprocess

REG = "wasm1egt8ut5swmck6xt5lqeuhkmhp44rwsv73ka8jfp7rn2kg629cdeqdlh6qf"
TRE = "wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u"
RPC = "http://127.0.0.1:26657"


def smart(contract, msg):
    p = subprocess.run(["wasmd", "q", "wasm", "contract-state", "smart", contract,
                        json.dumps(msg), "--node", RPC, "-o", "json"],
                       capture_output=True, timeout=60)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        return None
    try:
        return json.loads(s[i:]).get("data")
    except Exception:
        return None


SIGNERS = smart(TRE, {"signers": {}}) or []
cfg = smart(REG, {"config": {}}) or {}
VOTERS = cfg.get("authorized") or []
print("金库签名人 %d 个 / 根投票账户 %d 个（均取自链上）" % (len(SIGNERS), len(VOTERS)))
print("两组交集:", set(SIGNERS) & set(VOTERS) or "空 ✓（搬金库钥不影响每日结算）")

DIRS = ["/home/ubuntu/.wasmd/keyring-test"] + \
       sorted(glob.glob("/home/ubuntu/voters/*/keyring-test")) + \
       sorted(glob.glob("/home/ubuntu/lightdao_keys/keyring-test")) + \
       sorted(glob.glob("/home/ubuntu/*keyring*"))


def names_in(d):
    try:
        return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".info"))
    except Exception:
        return []


def addr_of(d, name):
    for bech in ("account", "validator"):
        p = subprocess.run(["wasmd", "keys", "show", name, "--keyring-dir", d,
                            "--keyring-backend", "test", "--bech", bech, "-a"],
                           capture_output=True, timeout=40)
        a = p.stdout.decode("utf-8", "replace").strip()
        if a.startswith("wasm1") or a.startswith("wasmvaloper"):
            return a
    return "(取不到)"


loc = {}
print("\n=== 各 keyring 位置 ===")
for d in DIRS:
    ns = names_in(d)
    if not ns:
        continue
    print("\n%s  （%d 个账户）" % (d, len(ns)))
    for n in ns:
        a = addr_of(d, n)
        tag = ""
        if a in SIGNERS:
            tag = "   <<< 金库签名人"
            loc.setdefault(a, []).append((d, n))
        elif a in VOTERS:
            tag = "   [根投票]"
        print("   %-38s %-48s%s" % (n[:38], a, tag))

print("\n=== 金库 5 把钥的实际落点 ===")
for i, a in enumerate(SIGNERS, 1):
    v = loc.get(a, [])
    print("  signer%d %-46s %s" % (i, a,
          "; ".join("%s::%s" % (d, n) for d, n in v) if v else "*** 未在这些目录里找到 ***"))
print("\n命中 %d/%d" % (len(loc), len(SIGNERS)))
