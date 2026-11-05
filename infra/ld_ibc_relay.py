#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_ibc_relay.py —— 跨链中继看门狗：进程 / 心跳 / 未确认包 / 客户端寿命 / 中继油钱。

每一条判定都来自实测到的故障方式（不是想象中的清单）：
  · 11-04：人工手动中继与守护进程共用同一个签名账户 → `account sequence mismatch` 刷了
    一整天，进程"active"但一个包都不动 —— 所以必须同时看进程和"有没有未确认包"；
  · 11-05：A→B 200,000 与 B→A 100,000 都是靠常驻中继自己到账（commitments 归零、
    escrow 600,000=500,000+200,000−100,000 对平）—— 这才叫"自动"；
  · osmo 那 4 个客户端早已过期，报错淹没日志：本脚本只监控在用的两条链，
    但会把"跳过了几条"打出来，不做静默吞掉；
  · 客户端一旦过期通道就冻死，补一次 UpdateClient 的成本远小于重开通道。

退出码：0 全过 / 1 有告警 / 2 量具自己读不到数（读不到绝不当成正常）。
--probe 只把读到的事实打出来；--selftest 植入故障证明它真的会响。
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

BIN = os.environ.get("LD_IBC_BIN", "/home/ubuntu/lightd.testnet.bin")
RPC_A = os.environ.get("LD_IBC_RPC_A", "http://127.0.0.1:26757")
RPC_B = os.environ.get("LD_IBC_RPC_B", "http://127.0.0.1:26957")
CH_A = os.environ.get("LD_IBC_CH_A", "channel-2")     # A 侧对 B 的通道
CH_B = os.environ.get("LD_IBC_CH_B", "channel-0")     # B 侧对 A 的通道
RELAYER_A = "wasm179u6h2xus9zetqe4ejwamxz6sv7ks8djf5kpjc"
RELAYER_B = "wasm1rct6n8snzdufxapu9qhxt3xwgg04k6cvxct60s"
ESCROW_A = "wasm12k2pyuylm9t7ugdvz67h9pg4gmmvhn5v4658cl"
MONITORED = set(os.environ.get("LD_IBC_CHAINS", "lightdao-testnet-gas,lightdao-testnet-b").split(","))
STATE = os.environ.get("LD_IBC_STATE", "/home/ubuntu/ld_ibc_relay_state.json")
ALERTS = os.environ.get("LD_IBC_ALERTS", "/home/ubuntu/ld_alerts.log")
SERVICE = os.environ.get("LD_IBC_SVC", "hermes-relay.service")
STALE_MIN = float(os.environ.get("LD_IBC_STALE_MIN", "25"))
GAS_MIN = int(os.environ.get("LD_IBC_GAS_MIN", "400000"))
TRUST_FRAC = float(os.environ.get("LD_IBC_TRUST_FRAC", "0.6"))
HB_LIM = {"A": int(os.environ.get("LD_IBC_HB_A", "300")), "B": int(os.environ.get("LD_IBC_HB_B", "3600"))}


def write_alert(line):
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def q_json(args, node):
    p = subprocess.run([BIN, "q"] + args + ["-o", "json", "--node", node],
                       capture_output=True, text=True, timeout=40)
    if p.returncode != 0:
        raise RuntimeError("q %s 失败：%s" % (" ".join(args), (p.stderr or p.stdout)[:90].replace("\n", " ")))
    try:
        return json.loads(p.stdout)
    except Exception as e:
        raise RuntimeError("q %s 的 JSON 解析不了：%s / 前 60 字=%s" % (" ".join(args), str(e)[:40], p.stdout[:60]))


def height(node):
    with urllib.request.urlopen(node + "/status", timeout=12) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    return int(j["result"]["sync_info"]["latest_block_height"])


def commitments(node, ch):
    """返回该通道上"已发出还没被确认"的包序号列表 —— 非空就是要盯的东西。
       用 commitments 而不是 send/recv 序号相减：实测这个 SDK 版本的
       `next-sequence-receive` 读数与链上真实收包历史不一致（B 已入账 200,000 却仍报 1），
       拿它当指标会天天误报，所以只信 commitments（它是 IBC 记账本体）。"""
    j = q_json(["ibc", "channel", "packet-commitments", "transfer", ch], node)
    out = []
    for c in j.get("commitments") or []:
        seq = c.get("sequence")
        if seq is None:   # 老/别的版本把它塞在 packet_connection 里
            m = re.search(r"sequences/(\d+)", str(c.get("packet_connection") or c))
            seq = m.group(1) if m else None
        if seq is None:
            raise RuntimeError("commitments 条目读不出序号，实际字段=%s" % list(c)[:6])
        out.append(int(seq))
    return out


def stake_balance(node, addr):
    j = q_json(["bank", "balances", addr], node)
    for b in j.get("balances", []):
        if b.get("denom") == "stake":
            return int(b["amount"])
    return 0


def client_facts(node):
    j = q_json(["ibc", "client", "states"], node)
    out = []
    for c in j.get("client_states", []):
        s = c.get("client_state") or {}
        cid = c.get("client_id", "?")
        m = re.match(r"^(\d+)(ns|s|m|h)?$", str(s.get("trusting_period", "")).strip())
        if not m:
            raise RuntimeError("客户端 %s 的 trusting_period 读不懂：%r" % (cid, s.get("trusting_period")))
        n = int(m.group(1))
        mult = {"ns": 1e-9, "s": 1, "m": 60, "h": 3600}.get(m.group(2) or "s", 1)
        trust = int(n * mult)
        frozen = str(((s.get("frozen_height") or {}).get("revision_height")) or "0") != "0"
        ts = None
        try:
            cs = q_json(["ibc", "client", "consensus-states", cid], node)
            lst = cs.get("consensus_states") or []
            if lst:
                t = (lst[-1].get("consensus_state") or {}).get("timestamp", "")
                ts = time.mktime(time.strptime(t[:19], "%Y-%m-%dT%H:%M:%S"))
        except Exception as e:
            print("  （读 %s 的共识状态失败：%s）" % (cid, str(e)[:60]))
        out.append({"id": cid, "chain": s.get("chain_id", "?"), "trust": trust,
                    "frozen": frozen, "ts": ts})
    return out


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {}


def save_state(d):
    try:
        json.dump(d, open(STATE, "w", encoding="utf-8"))
    except Exception:
        pass


def run(alarms, now, probe=False):
    st = load_state()
    ha, hb = height(RPC_A), height(RPC_B)
    print("链高 A=%d B=%d（A 出块约 5s，B 是新建的测试链）" % (ha, hb))
    for k, tag, v in (("hA", "A", ha), ("hB", "B", hb)):
        old = st.get(k)
        if old is not None and v <= old and (now - st.get(k + "_ts", now)) > HB_LIM[tag]:
            alarms.append("心跳停摆：%s 链 %.0f 秒高度没长（仍=%d）——节点不出了块，中继再勤也过不去包"
                          % (tag, (now - st.get(k + "_ts", now)) / 1.0, v))
        st[k], st[k + "_ts"] = v, now
    for name, node, ch in (("A→B", RPC_A, CH_A), ("B→A", RPC_B, CH_B)):
        fake = os.environ.get("LD_IBC_FAKE_PEND", "")
        if fake.startswith(name + ":"):        # 只给自测用，且会在输出里明说
            print("  （注入的假积压 %s=%s —— 不是链上读数）" % (name, fake.split(":", 1)[1]))
            seqs = [int(x) for x in fake.split(":", 1)[1].split(",") if x]
        else:
            seqs = commitments(node, ch)
        key = "pend_" + name
        print("%s 未确认包=%s" % (name, seqs if seqs else "无"))
        if seqs:
            first = st.get(key)
            if first is None:
                st[key] = now
            elif now - first > STALE_MIN * 60:
                alarms.append("%s 有 %d 个包（序号 %s）挂了 %.0f 分钟仍未确认：用户视角就是转账没到，"
                              "先查 %s 与中继账户序列号是否被人工抢用" % (name, len(seqs), ",".join(map(str, seqs[:5])),
                                                                      (now - first) / 60.0, SERVICE))
        else:
            st.pop(key, None)
    skip = 0
    for node, tag in ((RPC_A, "A"), (RPC_B, "B")):
        for c in client_facts(node):
            if c["chain"] not in MONITORED:
                skip += 1
                continue
            if c["frozen"]:
                alarms.append("客户端 %s（%s 侧，对面 %s）已冻结：这条通道现在过不去任何包"
                              % (c["id"], tag, c["chain"]))
                continue
            if c["ts"] is None:
                alarms.append("量具告警：客户端 %s（%s 侧）读不到共识状态时间戳，判断不了寿命" % (c["id"], tag))
                continue
            age = now - c["ts"]
            if age > c["trust"] * TRUST_FRAC:
                alarms.append("客户端 %s（%s 侧，对面 %s）共识状态 %.1f 天没更新，信任期 %.1f 天已用掉 %.0f%%"
                              "——过期即冻死，只能重开通道" % (c["id"], tag, c["chain"], age / 86400.0,
                                                        c["trust"] / 86400.0, 100.0 * age / c["trust"]))
    if skip:
        print("（跳过 %d 个属于未监控链的客户端，例如早先对接 osmo 测试网的旧通道；只跳过不隐藏）" % skip)
    for node, addr, tag in ((RPC_A, RELAYER_A, "A"), (RPC_B, RELAYER_B, "B")):
        bal = stake_balance(node, addr)
        print("%s 侧中继账户 stake=%d" % (tag, bal))
        if bal < GAS_MIN:
            alarms.append("%s 侧中继账户只剩 %d stake（阈值 %d）：付不出 gas 的中继等于没有中继"
                          % (tag, bal, GAS_MIN))
    esc = stake_balance(RPC_A, ESCROW_A)
    print("A 侧 channel-2 escrow 锁仓 stake=%d（跨链总额的最终账面）" % esc)
    p = subprocess.run(["systemctl", "is-active", SERVICE], capture_output=True, text=True, timeout=20)
    svc = (p.stdout or "").strip()
    print("%s=%s" % (SERVICE, svc or "?"))
    if svc != "active":
        alarms.append("中继进程 %s 不是 active（实测 %s）：跨链转账会停在这里" % (SERVICE, svc or "读不到"))
    save_state(st)
    return st


def selftest():
    print("SELFTEST：四类故障逐项验证（抓不到的看门狗等于没写）")
    st = load_state()
    now = time.time()
    hits = 0

    def base_state(**kw):
        d = dict(st)
        # 清掉上一轮真故障留下的 pend_*，否则第一轮就会报警，测不出"两轮判定"的逻辑
        for k in list(d):
            if k.startswith("pend_"):
                del d[k]
        d.update({"hA": height(RPC_A), "hA_ts": now, "hB": height(RPC_B), "hB_ts": now})
        d.update(kw)
        save_state(d)

    save_state(dict(st, hA=height(RPC_A) + 10 ** 7, hA_ts=now - 99999, hB=height(RPC_B), hB_ts=now))
    al = []; run(al, now)
    ok = any("心跳" in x for x in al); hits += ok
    print("  a 心跳停摆 -> %s" % ("抓到" if ok else "漏了"))

    globals()["TRUST_FRAC"] = 0.0
    base_state()
    al = []; run(al, now)
    ok = any("共识状态" in x or "已冻结" in x for x in al)
    hits += ok
    print("  b 客户端寿命/冻结 -> %s（%d 条）" % ("抓到" if ok else "漏了", sum(1 for x in al if "客户端" in x)))
    globals()["TRUST_FRAC"] = 0.6

    globals()["GAS_MIN"] = 10 ** 15
    base_state()
    al = []; run(al, now)
    ok = any("中继账户" in x for x in al); hits += ok
    print("  c 油钱不足 -> %s" % ("抓到" if ok else "漏了"))
    globals()["GAS_MIN"] = int(os.environ.get("LD_IBC_GAS_MIN", "400000"))

    globals()["SERVICE"] = "ld-definitely-not-running.service"
    base_state()
    al = []; run(al, now)
    ok = any("不是 active" in x for x in al); hits += ok
    print("  d 中继进程挂掉 -> %s" % ("抓到" if ok else "漏了"))
    globals()["SERVICE"] = os.environ.get("LD_IBC_SVC", "hermes-relay.service")
    # e 积压检测：注入假序号跑两轮 —— 第一轮只记时间不报警（刚发出去在途是正常的），
    #   第二轮超过阈值必须报警。真故障（11-05 07:29 故意停中继后链上真的出现序号 4 的未确认包）
    #   已经实测过一轮，这里测的是报警逻辑本身。
    globals()["STALE_MIN"] = 0.0
    os.environ["LD_IBC_FAKE_PEND"] = "A→B:7,8"
    base_state()
    al = []; run(al, now)
    quiet = not any("仍未确认" in x for x in al)
    al = []; run(al, now + 4000)
    fired = any("仍未确认" in x for x in al)
    ok = quiet and fired
    hits += ok
    print("  e 包积压两轮判定（第一轮不报=%s，第二轮报警=%s）-> %s" % (quiet, fired, "抓到" if ok else "漏了"))
    del os.environ["LD_IBC_FAKE_PEND"]
    globals()["STALE_MIN"] = float(os.environ.get("LD_IBC_STALE_MIN", "25"))
    # f 误报防护：当前通道若无未确认包，绝不能凭空报"包积压"
    base_state()
    al = []; run(al, now)
    bad = [x for x in al if "未确认" in x or "仍未确认" in x]
    print("  f 空积压时不误报 -> %s" % ("通过" if not bad else "误报：%s" % bad[0][:60]))
    save_state(st)
    print("SELFTEST：%d/5 类被抓到" % hits)
    return 0 if hits >= 5 and not bad else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    alarms = []
    probe = "--probe" in sys.argv
    try:
        run(alarms, time.time(), probe)
    except Exception as e:
        line = "%s IBC-RELAY FAIL 量具自己没读到数（绝不当成正常）：%s" % (stamp(), str(e)[:200])
        print(line)
        write_alert(line)
        sys.exit(2)
    if probe:
        print("PROBE：以上为读到的原始事实"); sys.exit(0)
    for a in alarms:
        line = "%s IBC-RELAY ALERT %s" % (stamp(), a)
        print(line)
        write_alert(line)
    if alarms:
        sys.exit(1)
    print("IBC-RELAY OK：进程/心跳/未确认包/客户端寿命/油钱 五项全过")
    sys.exit(0)
