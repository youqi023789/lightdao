#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-MIGRATE-CHECK-GATE-20261016-B
两层防护，防的是同一件事：治理把合约迁移到一份"没有源码、无法复现"的代码。
（实测发生过：提案 #14/#15 投票通过、目标 code 18 的校验和在本机/仓库产物里都找不到，
  最后靠执行失败才没出事。）

用法：
  预检   python3 ld_migrate_gate.py check <code_id> [目标合约]   -> 非 0 = 不许提
  监控   python3 ld_migrate_gate.py watch                        -> 扫链上"还能改结果"的迁移提案
产物清单：contracts/wasm/SHA256SUMS（sha256 + 相对路径）
构建记录：contracts/wasm/BUILDLOG.tsv（这份字节码是哪个提交、哪套工具链编的、能否复现）

与 A 版的三处区别（都是这轮复盘发现的量具错）：
  1) SDK 0.50 的 gov v1 提案字段叫 id 不是 proposal_id —— A 版打印"提案 None"，
     等于告警里丢掉了最关键的一个信息（提案号），修成 id or proposal_id。
  2) A 版把链上 17 条提案全扫一遍，包含早已 FAILED/REJECTED 的历史提案——
     一旦有真问题会被历史噪声淹没。现在只看还能改变结果的状态。
  3) "字节码在仓库里"≠"字节码能从源码复现"。A 版只查前者，会把
     18/19/20 这种"文件捞回来了但没有构建记录"判成绿灯。现在按 BUILDLOG
     的 reproducible 字段判：缺记录=跟踪例外（带解除日期），到期未补则非零退出。
"""
import datetime
import json
import os
import subprocess
import sys

RPC = "http://127.0.0.1:26657"
REPO = os.environ.get("LD_REPO", "/home/ubuntu/repo")
SUMS = os.path.join(REPO, "contracts/wasm/SHA256SUMS")
BUILDLOG = os.path.join(REPO, "contracts/wasm/BUILDLOG.tsv")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
# 还能改变结果的提案状态；其余（已否决/已失败/已执行）不再重复告警
OPEN_STATUS = ("PROPOSAL_STATUS_VOTING_PERIOD", "PROPOSAL_STATUS_PASSED",
               "PROPOSAL_STATUS_SUBMITTED")
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


def note(line):
    """写告警。写不进去必须喊出来：历史上"日志写失败被吞"= 告警从未到达。
    （root cron 建的 root 属主日志会把非 root 运行者的写入打死，这坑踩过。）"""
    import datetime
    txt = "%s %s\n" % (datetime.datetime.now(datetime.timezone.utc)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"), line)
    try:
        with open(ALERTS, "a") as f:
            f.write(txt)
        return True
    except Exception as e:
        sys.stderr.write("WARN 告警写入失败 %s: %s（内容: %s）\n" % (ALERTS, e, line[:80]))
        return False


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


def load_buildlog():
    """sha256前16 -> {字段: 值}。文件不存在时返回 {}，由调用方按缺记录处理。"""
    out = {}
    if not os.path.exists(BUILDLOG):
        return out
    head = None
    for ln in open(BUILDLOG, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        ps = ln.split("\t")
        if head is None:
            head = ps
            continue
        d = dict(zip(head, ps))
        sha = (d.get("sha256_16") or "").lower()
        if sha:
            out[sha] = d
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


def verify(cid, target=None, quiet=False, sums=None, blog=None):
    """返回 (rc, 是否只是跟踪例外). rc=0 干净 / rc=1 有例外 / rc>=2 硬失败。"""
    if sums is None:
        sums = load_sums()
    if sums is None:
        print("FAIL 产物清单不存在（%s）——无法核验来源" % SUMS)
        return 4, False
    if blog is None:
        blog = load_buildlog()
    ci = code_info(cid)
    if not ci:
        print("FAIL code_id %s 在链上不存在" % cid)
        return 2, False
    chk = (ci.get("checksum") or "").lower()
    name = SENSITIVE.get(target or "", "?")
    if not chk:
        print("FAIL 取不到 code %s 的校验和" % cid)
        return 3, False
    src = sums.get(chk)
    if not src:
        print("FAIL code %-4s 校验和 %s… 不在仓库产物清单里（无源可查，禁止迁移%s）"
              % (cid, chk[:16], (" 到 " + name) if name != "?" else ""))
        if not quiet:
            print("     正确做法：从源码构建 -> 产物与 sha256 一起提交（含 BUILDLOG 一行）-> "
                  "先提 store code 提案 -> 核对链上校验和一致 -> 再提 migrate")
        return 1, False
    rec = blog.get(chk[:16])
    repro = (rec or {}).get("reproducible", "").strip().lower()
    until = (rec or {}).get("until", "").strip()
    if repro == "yes":
        print("OK   code %-4s 校验和 %s… 产物 %s，构建记录：源码 %s / 工具链 %s"
              % (cid, chk[:16], src, (rec or {}).get("source_commit", "?"),
                 (rec or {}).get("toolchain", "?")))
        return 0, False
    # 有字节码但没构建记录 = 只能核对"是不是这一份"，不能证明"能从源码编出来"
    if until and datetime.date.today() <= datetime.date.fromisoformat(until):
        print("WARN code %-4s 校验和 %s… 已登记产物 %s，但【无构建记录、不可复现】"
              "（跟踪例外，解除日 %s；%s）" % (cid, chk[:16], src, until,
                                       (rec or {}).get("note", ""))[:240])
        return 1, True
    print("FAIL code %-4s 校验和 %s… 有产物但无构建记录%s，例外已到期或未登记"
          % (cid, chk[:16], ("（解除日 %s 已过）" % until) if until else ""))
    return 1, False


def contract_code(addr):
    """链上某合约当前真正在跑的 code_id（用来判断"迁移是否已执行"）。
    本 wasmd 构建里命令是 `q wasm contract`（不是 contract-info，后者会报
    unknown command 并静默返回 None，害我把已执行的旧提案当成未决）。"""
    d = jq(["wasmd", "q", "wasm", "contract", addr, "--node", RPC, "-o", "json"]) or {}
    ci = d.get("contract_info") or (d.get("contract_infos") or [{}])[0]
    return str(ci.get("code_id") or "") or None


def watch():
    """扫链上未决治理提案里的 MsgMigrateContract，目标在敏感清单里就核验来源与可复现性。"""
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
    sums = load_sums()
    blog = load_buildlog()
    bad, soft = [], []
    n_mig = 0
    for pr in props:
        st = pr.get("status")
        if st not in OPEN_STATUS:
            continue
        pid = pr.get("id") or pr.get("proposal_id")
        for m in (pr.get("messages") or []):
            t = m.get("@type") or m.get("type") or ""
            v = m.get("value") or m.get("msg") or {}
            if "MsgMigrateContract" not in str(t):
                continue
            tgt = v.get("contract")
            if tgt not in SENSITIVE:
                continue
            # 已经执行完的迁移不再重复告警：PASSED 的历史提案（如 #7）若不过这一道，
            # 会永远挂在告警里，把真问题淹在噪声里。判据是链上合约当前的 code_id。
            if st == "PROPOSAL_STATUS_PASSED" and \
                    contract_code(tgt) == str(v.get("code_id")):
                continue
            n_mig += 1
            rc, is_soft = verify(v.get("code_id"), tgt, quiet=True,
                                 sums=sums, blog=blog)
            if rc != 0:
                (soft if is_soft else bad).append(
                    (pid, st, SENSITIVE[tgt], v.get("code_id")))
    print("watch: 未决敏感合约迁移 %d 条；硬失败 %d 条；跟踪例外 %d 条"
          % (n_mig, len(bad), len(soft)))
    for pid, st, name, cid in bad:
        print("   !!! 提案 #%s (%s) 要把 %s 迁到无源/不可复现且例外已到期的 code %s"
              % (pid, st, name, cid))
    for pid, st, name, cid in soft:
        print("   ·  跟踪例外：提案 #%s (%s) 迁 %s → code %s（缺构建记录，见 BUILDLOG）"
              % (pid, st, name, cid))
    if bad:
        note("ALERT [migrate-gate] %d 个未决迁移提案目标代码无源或例外到期: %s"
             % (len(bad), bad[:4]))
        return 1
    if soft:
        # 例外只提示、不阻断；但同一个例外每天只记一次，避免刷屏
        today = datetime.date.today().isoformat()
        mark = "/tmp/ld_migrate_gate_exception_%s" % today
        if not os.path.exists(mark):
            note("NOTE [migrate-gate] 跟踪例外（缺构建记录）%d 条: %s"
                 % (len(soft), soft[:4]))
            try:
                open(mark, "w").write(today)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "watch":
        sys.exit(watch())
    if sys.argv[1] == "check":
        rc, soft = verify(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        sys.exit(rc if not soft else 0)
    print("未知子命令")
    sys.exit(2)
