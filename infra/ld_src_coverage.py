#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-SRC-COVERAGE-20261017  敏感合约"有没有源码"的覆盖率监控（棘轮式）。
为什么需要：链上管钱的合约里有两份（code 16 vesting-v2、code 17 ecosystem_fund）
仓库里根本没有对应源码，合计 4.75 亿 LIGHT。这类缺口一旦存在过，最危险的不是它本身，
而是"又多了一个却没人发现"。所以这里做成棘轮：无源码的敏感合约数量**只准降不准升**，
升了就告警；数量不变时每天只记一行状态，不刷屏。

判据（三路都要过才算"有源码"）：
  1 合约当前 code_id 的校验和在 contracts/wasm/SHA256SUMS 里（字节码已归档）；
  2 BUILDLOG.tsv 里有对应行（登记过来源）；
  3 由归档文件名 codeN_<crate>.wasm 推出的 crate 目录真实存在于 contracts/contracts/<crate>/。
第 3 条是关键——只归档字节码不等于有源码。
查不到链上数据一律 QUERY-FAIL 非零退出，绝不把"没查到"当成"没问题"。"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

REPO = os.environ.get("LD_REPO", "/home/ubuntu/repo")
RPC = os.environ.get("LD_RPC", "http://127.0.0.1:26657")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
STATE = os.environ.get("LD_SRCCOVER_STATE", "/var/lib/ld_src_coverage/state.json")
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
# 归档名与 crate 目录名不同时的显式映射（避免用"猜的字符串相似度"糊过去）
CRATE_ALIAS = {"vesting": "vesting", "light_token": "light_token",
               "insurance_fund": "insurance_fund", "mining_reward": "mining_reward",
               "governance": "governance", "treasury_multisig": "treasury_multisig"}


def note(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print("%s %s" % (ts, msg))
    try:
        with open(ALERTS, "a") as f:
            f.write("%s %s\n" % (ts, msg))
    except Exception as e:
        print("  WARN 告警没落盘 %s: %s" % (ALERTS, e))


def jq(args):
    p = subprocess.run(args, capture_output=True, timeout=60)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        return None
    try:
        return json.loads(s[i:])
    except Exception:
        return None


def load_sums():
    p = os.path.join(REPO, "contracts/wasm/SHA256SUMS")
    if not os.path.exists(p):
        return None
    out = {}
    for ln in open(p, encoding="utf-8"):
        ps = ln.split()
        if len(ps) >= 2:
            out[ps[0].lower()] = ps[-1]
    return out


def load_blog():
    p = os.path.join(REPO, "contracts/wasm/BUILDLOG.tsv")
    rows = {}
    if not os.path.exists(p):
        return rows
    head = None
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        ps = ln.split("\t")
        if head is None:
            head = ps
            continue
        d = dict(zip(head, ps))
        if d.get("sha256_16"):
            rows[d["sha256_16"].lower()] = d
    return rows


def main():
    sums = load_sums()
    if sums is None:
        note("ALERT [src-coverage] QUERY-FAIL 产物清单读不到（%s），无法判定" % sums)
        return 5
    blog = load_blog()
    missing = []
    detail = []
    for addr, name in sorted(SENSITIVE.items(), key=lambda kv: kv[1]):
        ci = jq(["wasmd", "q", "wasm", "contract", addr, "--node", RPC, "-o json"])
        if not ci:
            note("ALERT [src-coverage] QUERY-FAIL 读不到合约 %s（%s），本次判定作废"
                 % (name, addr[:16]))
            return 5
        info = ci.get("contract_info") or {}
        cid = str(info.get("code_id") or "")
        chk = jq(["wasmd", "q", "wasm", "code-info", cid, "--node", RPC, "-o json"])
        if not chk:
            note("ALERT [src-coverage] QUERY-FAIL 读不到 code %s 校验和" % cid)
            return 5
        checksum = ((chk.get("code_info") or chk).get("checksum") or "").lower()
        art = sums.get(checksum)
        reasons = []
        if not art:
            reasons.append("字节码未归档")
        else:
            # crate 名按"合约名"映射，不从归档文件名猜：同一校验和可能在清单里
            # 对应两条路径（原始的 governance.wasm 与回捞的 code13_governance.wasm），
            # 字典后写覆盖前写，用文件名推 crate 会把有源码的 governance 误判成缺源码。
            crate = CRATE_ALIAS.get(name, name)
            if not os.path.isdir(os.path.join(REPO, "contracts/contracts", crate)):
                reasons.append("仓库无 contracts/contracts/%s 源码目录" % crate)
            elif not blog.get(checksum[:16]):
                reasons.append("BUILDLOG 未登记")
        if reasons:
            missing.append(name)
        detail.append("   %-17s code %-3s %s" % (name, cid, "；".join(reasons) or "有源码"))
    print("敏感合约源码覆盖率：%d/%d 有源码" % (len(SENSITIVE) - len(missing), len(SENSITIVE)))
    for d in detail:
        print(d)

    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    prev = {"missing": []}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            prev = {"missing": []}
    pm = set(prev.get("missing") or [])
    now = set(missing)
    worse = sorted(now - pm)
    better = sorted(pm - now)
    json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "missing": sorted(now)}, open(STATE, "w"))
    if better:
        print("   改善：%s" % ", ".join(better))
    if worse:
        note("ALERT [src-coverage] 新增无源码的敏感合约 %s（当前共 %d 个：%s）"
             % (",".join(worse), len(now), ",".join(sorted(now))))
        return 1
    print("   无源码清单与上次一致（棘轮未恶化）: %s" % (", ".join(sorted(now)) or "无"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
