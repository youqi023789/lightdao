#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-MIGRATE-CHECK-GATE-20261016
两层防护，防的是同一件事：治理把合约迁移到一份"没有源码、无法复现"的代码。
（实测发生过：提案 #14/#15 投票通过、目标 code 18 的校验和在本机/仓库产物里都找不到，
  最后靠执行失败才没出事。）

用法：
  预检   python3 ld_migrate_gate.py check <code_id> [目标合约]   -> 非 0 = 不许提
  监控   python3 ld_migrate_gate.py watch                        -> 扫链上待执行/已通过的迁移提案
产物清单：contracts/wasm/SHA256SUMS（sha256 + 相对路径）
"""
import json
import os
import subprocess
import sys

RPC = "http://127.0.0.1:26657"
REPO = "/home/ubuntu/repo"
SUMS = os.path.join(REPO, "contracts/wasm/SHA256SUMS")
ALERTS = "/home/ubuntu/ld_alerts.log"
# 这些合约被迁移等于改变资金/治理规则，必须可溯源
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


def load_sums():
    if not os.path.exists(SUMS):
        return None
    out = {}
    for ln in open(SUMS, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        if len(parts) >= 2:
            out[parts[0].lower()] = parts[-1]
    return out


def code_info(cid):
    p = subprocess.run(["wasmd", "q", "wasm", "code-info", str(cid),
                        "--node", RPC, "-o", "json"], capture_output=True, timeout=60)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        return None
    try:
        d = json.loads(s[i:])
        # 注意：`q wasm code-info` 返回的是顶层对象（不是嵌在 code_info 下），
        # 之前按嵌套取导致永远拿空值、把有源的 code 误判成"链上不存在"。
        return d.get("code_info") or d
    except Exception:
        return None


def check(cid, target=None, quiet=False):
    sums = load_sums()
    if sums is None:
        print("FAIL 产物清单不存在（%s）——无法核验来源" % SUMS)
        return 4
    ci = code_info(cid)
    if not ci:
        print("FAIL code_id %s 在链上不存在" % cid)
        return 2
    chk = (ci.get("checksum") or "").lower()
    name = SENSITIVE.get(target or "", "?")
    if not chk:
        print("FAIL 取不到 code %s 的校验和" % cid)
        return 3
    src = sums.get(chk)
    if src:
        print("OK   code %-4s 校验和 %s… 对应仓库产物 %s" % (cid, chk[:16], src))
        return 0
    print("FAIL code %-4s 校验和 %s… 不在仓库产物清单里（无源可查，禁止迁移%s）"
          % (cid, chk[:16], (" 到 " + name) if name != "?" else ""))
    if not quiet:
        print("     正确做法：从源码重新构建 -> 把 sha256 追加进 %s -> "
              "先提 store code 提案 -> 核对链上校验和一致 -> 再提 migrate" % SUMS)
    return 1


def watch():
    """扫链上治理提案里所有 MsgMigrateContract，目标合约属敏感清单就核验校验和。"""
    p = subprocess.run(["wasmd", "q", "gov", "proposals", "--node", RPC,
                        "-o", "json"], capture_output=True, timeout=90)
    s = p.stdout.decode("utf-8", "replace")
    i = s.find("{")
    if i < 0:
        # 查不到就必须非零退出：否则"没查成"会被当成"没有风险"，
        # 这正是本会话反复出现的静默绿灯模式。
        print("FAIL watch 无法读取链上提案:",
              (p.stderr.decode("utf-8", "replace") or s)[:140])
        return 3
    try:
        props = json.loads(s[i:]).get("proposals") or []
    except Exception as e:
        print("FAIL watch 解析提案列表失败:", e)
        return 4
    bad = []
    n_mig = 0
    for pr in props:
        for m in (pr.get("messages") or []):
            t = m.get("@type") or m.get("type") or ""
            v = m.get("value") or m.get("msg") or {}
            if "MsgMigrateContract" not in str(t):
                continue
            tgt = v.get("contract")
            if tgt not in SENSITIVE:
                continue
            n_mig += 1
            pid = pr.get("proposal_id")
            st = pr.get("status")
            rc = check(v.get("code_id"), tgt, quiet=True)
            if rc != 0:
                bad.append((pid, st, SENSITIVE[tgt], v.get("code_id")))
    print("watch: 敏感合约迁移类消息 %d 条，其中无源可查 %d 条" % (n_mig, len(bad)))
    for pid, st, name, cid in bad:
        print("   !!! 提案 %s (%s) 要把 %s 迁到无源可查的 code %s" % (pid, st, name, cid))
    if bad:
        import datetime
        with open(ALERTS, "a") as f:
            f.write("%s ALERT [migrate-gate] %d 个迁移提案目标代码无源可查: %s\n"
                    % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                       len(bad), bad[:4]))
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "watch":
        sys.exit(watch())
    if sys.argv[1] == "check":
        sys.exit(check(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
    print("未知子命令"); sys.exit(2)
