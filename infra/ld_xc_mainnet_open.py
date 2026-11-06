#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_xc_mainnet_open.py —— 主网跨链通道的一次性开通器（油钱到位才动手，动手就自证）。

为什么需要：主网 IBC 客户端数=0、通道数=0（链上实测），所以面板上"主网跨链未开通"是事实。
打开它要三件事按顺序成立：① 中继身份（已建：hermes 双侧同一条助记词）② 两侧油钱
③ 握手 + 中继进程。①完成、②等所有者转入，③就是这个脚本。

四件套（本项目的不变量口径）：
  执行点：本脚本（--dry-run 只体检不动链）
  检测点：结束后自己回查链上通道状态 + 真跑一笔双向转账（不看返回值就宣称成功 = 严禁）
  告警  ：全程写 /home/ubuntu/ld_alerts.log（XC-MAINNET 前缀）
  测试  ：--selftest 用假数据逐项确认该停手时真的停手、该动手时判得准

护栏（任一不过 = 绝不上链）：
 1) hermes 配置 validate 通过，两侧 key 都在
 2) 主网中继账户 ulight ≥ MIN_ULIGHT 且 Osmosis 侧 uosmo ≥ MIN_UOSMO（对面也要 gas，否则握手必卡）
 3) 主网已有客户端但没有 OPEN 通道 = 半截状态 → 停手报警（自动重开会造重复客户端，链上不可逆）
 4) 已有 OPEN 的 transfer 通道 → 不重复开
 5) 状态文件 opened → 幂等退出
"""
import argparse
import base64
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

CFG = os.environ.get("XC_MN_CFG", "/home/ubuntu/.hermes/config/config-mainnet.toml")
STATE = os.environ.get("XC_MN_STATE", "/home/ubuntu/ld_xc_mainnet.json")
LOCKF = os.environ.get("XC_MN_LOCK", "/home/ubuntu/ld_xc_mainnet.lock")
ALERTS = os.environ.get("XC_MN_ALERTS", "/home/ubuntu/ld_alerts.log")
EVID = os.environ.get("XC_MN_EVID", "/home/ubuntu/repo/docs/IBC_MAINNET_EVIDENCE.md")
A = os.environ.get("XC_MN_A", "lightdao-mainnet-1")
B = os.environ.get("XC_MN_B", "osmosis-1")
A_RPC = os.environ.get("XC_MN_A_RPC", "http://127.0.0.1:26657")
B_LCD = [x.strip() for x in os.environ.get(
    "XC_MN_B_LCD",
    "https://lcd.osmosis.zone,https://api.osmosis.validatus.com,https://osmosis-api.highstakes.ch,"
    "https://osmosis.api.pocket.network,https://osmosis-api.noders.services,"
    "https://osmosis.rest.stakin-nodes.com").split(",") if x.strip()]
LCD_CACHE = os.environ.get("XC_MN_LCD_CACHE", "/tmp/oz_lcd.txt")
MIN_ULIGHT = int(os.environ.get("XC_MN_MIN_ULIGHT", "5000000"))     # 5 LIGHT
MIN_UOSMO = int(os.environ.get("XC_MN_MIN_UOSMO", "300000"))        # 0.3 OSMO
MAIN_ADDR = os.environ.get("XC_MN_ADDR", "wasm1tplhv9hclk9y3d8ahshf37auwenmn8jx9rw3yp")
SVC = os.environ.get("XC_MN_SVC", "lightdao-ibc-mainnet.service")
UNIT = os.environ.get("XC_MN_UNIT", "/tmp/ld_xc_mainnet_unit.txt")
B_ADDR_FILE = os.environ.get("XC_MN_BADDR", "/tmp/xc_osmo_addr.txt")
# 假数据开关（只给 --selftest 用；正常跑不设这几个变量）
FX = os.environ.get("XC_MN_FIX")


def log(msg):
    s = "%s XC-MAINNET %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(s, flush=True)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(s + "\n")
    except Exception:
        pass


def sh(cmd, timeout=240, user="ubuntu"):
    full = (["sudo", "-u", user] if user else []) + cmd
    try:
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return 1, "EXC %s" % str(e)[:200]


def hq(args, timeout=180):
    return sh(["hermes", "--config", CFG] + args, timeout=timeout)


def fx(name, default=None):
    """fixture 模式：从 --selftest 写好的假现场文件里取数，量具和被测分离，便于反向验证。"""
    if not FX:
        return default
    try:
        with open(FX, encoding="utf-8") as f:
            return json.load(f).get(name, default)
    except Exception:
        return default


def wq(args, node=A_RPC, timeout=40):
    p = subprocess.run(["wasmd", "q"] + args + ["--node", node, "-o", "json"],
                       capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(p.stdout) if p.stdout.strip() else {}
    except Exception:
        return {}


def get_json(url, timeout=15):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as f:
            return json.load(f)
    except Exception:
        return None


def lcd_alive(base):
    """验活要用「必定存在」的接口：node_info 并核对 chain_id。
    用总供应那条路会因 SDK 版本换了 REST 路径而 404，把活节点误判成死的（实测踩过）。"""
    d = get_json(base.rstrip("/") + "/cosmos/base/tendermint/v1beta1/node_info", timeout=12)
    if not d:
        return None
    cid = (d.get("default_node_info") or {}).get("network")
    return cid if cid == B else None


def pick_lcd():
    """LCD（公共 REST 节点）会死，所以先用 node_info 验活再拿去查余额。
    不做这一步的话，读不到 = 0，就会把"量具坏了"当成"账户没钱"——这是本项目严禁的假阴性。"""
    try:
        c = open(LCD_CACHE).read().strip()
        if c and lcd_alive(c):
            return c
    except Exception:
        pass
    for base in B_LCD:
        if lcd_alive(base):
            try:
                open(LCD_CACHE, "w").write(base + "\n")
            except Exception:
                pass
            return base
    return None


def rest_balances(addr):
    base = pick_lcd()
    if not base:
        return None
    d = get_json(base.rstrip("/") + "/cosmos/bank/v1beta1/balances/" + addr)
    return (d.get("balances") or []) if d else None


def balance(addr, which):
    """which='A' 主网（本机节点直接查）；'B' Osmosis（先验活 LCD，再退回 CLI）。
    返回 None 表示"读不到"（量具坏了），和"读到 0"是两回事 —— 前者不许当成后者报警。"""
    fb = fx("balance_" + which)
    if fb is not None:
        return int(fb)
    if not addr:
        return None
    want = "ulight" if which == "A" else "uosmo"
    if which == "A":
        d = wq(["bank", "balances", addr], node=A_RPC)
        if not d:
            return None
        lst = d.get("balances") or []
    else:
        lst = rest_balances(addr)
        if lst is None:
            d = wq(["bank", "balances", addr], node=fx("rpc_B", "https://rpc.osmosis.zone"))
            if not d:
                return None
            lst = d.get("balances") or []
    return next((int(b["amount"]) for b in lst if b.get("denom") == want), 0)


def b_addr():
    fb = fx("addr_B")
    if fb:
        return fb
    try:
        return open(B_ADDR_FILE).read().strip()
    except Exception:
        return ""


def clients(node=A_RPC):
    n = fx("clients_A")
    if n is not None:
        return int(n)
    return len((wq(["ibc", "client", "states"], node=node).get("client_states") or []))


def channels(node=A_RPC):
    fc = fx("channels_A")
    raw = fc if fc is not None else (wq(["ibc", "channel", "channels"], node=node).get("channels") or [])
    out = []
    for c in raw:
        out.append({"id": c.get("channel_id"), "port": c.get("port_id"),
                    "state": (c.get("state") or {}).get("status"),
                    "counter": (c.get("counterparty") or {}).get("channel_id")})
    return out


def open_transfer(node=A_RPC):
    return [c for c in channels(node) if c["port"] == "transfer" and c["state"] == "STATE_OPEN"]


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(d):
    d["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def hermes_ready():
    if fx("hermes_ok") is not None:
        return bool(fx("hermes_ok")), "fixture"
    rc, out = hq(["config", "validate"])
    if rc != 0:
        return False, "配置不合法：%s" % " ".join(out.split())[:120]
    for chain, key in ((A, "relayer-main"), (B, "relayer-osmo")):
        rc, out = hq(["keys", "list", "--chain", chain])
        if key not in out:
            return False, "%s 侧缺 key %s" % (chain, key)
    return True, "配置合法 + 两侧 key 齐"


def precheck():
    reasons, facts = [], {}
    ok, why = hermes_ready()
    facts["hermes"] = why
    if not ok:
        reasons.append("hermes 未就绪：" + why)
    baddr = b_addr()
    bA = balance(MAIN_ADDR, "A")
    bB = balance(baddr, "B")
    facts.update(main_ulight=bA, osmo_uosmo=bB, main_addr=MAIN_ADDR, osmo_addr=baddr,
                 a_clients=clients())
    openA = open_transfer()
    facts["open_channels_A"] = [c["id"] for c in openA]
    if openA:
        return False, ["已存在 OPEN 的 transfer 通道 %s —— 不重复开" % ",".join(facts["open_channels_A"])], facts
    if bA is None:
        reasons.append("主网中继余额读不到（是量具坏了不是没钱）：检查 %s" % A_RPC)
    elif bA < MIN_ULIGHT:
        reasons.append("主网油钱不够：ulight %d < %d（请转 %g LIGHT 到 %s）"
                       % (bA, MIN_ULIGHT, MIN_ULIGHT / 1e6, MAIN_ADDR))
    if bB is None:
        reasons.append("Osmosis 侧余额读不到（公共节点全失联，是量具坏了不是没钱）—— 换 LCD 名单")
    elif bB < MIN_UOSMO:
        reasons.append("对面链 gas 不够：uosmo %d < %d（请转 %g OSMO 到 %s）"
                       % (bB, MIN_UOSMO, MIN_UOSMO / 1e6, baddr or "?"))
    if facts["a_clients"] > 0:
        reasons.append("主网已有 %d 个 IBC 客户端却没有 OPEN 通道 = 半截状态，"
                       "自动重开会留下重复客户端（不可逆），停手交人工核对" % facts["a_clients"])
    return (not reasons), reasons, facts


def install_unit():
    txt = ("[Unit]\n"
           "Description=LightDAO IBC relayer (lightdao-mainnet-1 <-> osmosis-1)\n"
           "After=network-online.target\n\n"
           "[Service]\n"
           "User=ubuntu\n"
           "ExecStart=/usr/local/bin/hermes --config %s start\n"
           "Restart=on-failure\nRestartSec=10\n\n"
           "[Install]\n"
           "WantedBy=multi-user.target\n" % CFG)
    with open(UNIT, "w", encoding="utf-8") as f:
        f.write(base64.b64encode(txt.encode()).decode())
    if fx("skip_install"):
        return True, "fixture 跳过装单元"
    rc, out = sh(["sudo", "bash", "-c",
                  "base64 -d %s > %s && rm -f %s && systemctl daemon-reload && systemctl enable %s"
                  % (UNIT, "/etc/systemd/system/" + SVC, UNIT, SVC)], timeout=90, user=None)
    return rc == 0, " ".join(out.split())[:200]


def do_open():
    log("握手开始：一条 hermes create channel 内含 客户端 + 连接 + transfer 通道")
    if fx("fake_open_ok") is not None:
        okv = bool(fx("fake_open_ok"))
        return okv, {"fixture": True}
    rc, out = hq(["create", "channel", "--a-chain", A, "--b-chain", B,
                  "--a-port", "transfer", "--b-port", "transfer",
                  "--new-client-connection", "--yes"], timeout=900)
    tail = " | ".join([" ".join(l.split()) for l in out.splitlines() if l.strip()][-6:])
    if rc != 0:
        log("握手失败 rc=%d：%s" % (rc, tail[:400]))
        return False, tail
    time.sleep(8)
    openA = open_transfer()
    if not openA:
        log("命令返回 0 但主网查不到 OPEN 通道 —— 判失败（绝不信返回值）")
        return False, "命令 0 但链上无 OPEN 通道：" + tail[:200]
    log("通道已 OPEN：主网 %s ↔ Osmosis %s" % (openA[0]["id"], openA[0]["counter"]))
    oki, mi = install_unit()
    if not oki:
        return False, "单元装不上：" + mi
    sh(["sudo", "systemctl", "restart", SVC], timeout=90, user=None)
    time.sleep(25)
    rc4, out4 = sh(["systemctl", "is-active", SVC], timeout=20, user=None)
    log("中继进程 %s = %s" % (SVC, (out4.strip() or "unknown")))
    return out4.strip() == "active", {"channel_A": openA[0]["id"], "channel_B": openA[0]["counter"]}


def verify_transfer(facts):
    """真跑一笔 A→B 再 B→A，用链上余额对平；不通就不给 opened。"""
    if fx("skip_verify"):
        return True, {"fixture": True}
    chid = facts.get("channel_A")
    baddr = b_addr()
    amt = 1000
    rc, out = hq(["tx", "ft-transfer", "--dst-chain", B, "--src-chain", A,
                  "--src-connection", "connection-0", "--src-port", "transfer",
                  "--src-channel", chid, "--amount", str(amt), "--denom", "ulight",
                  "--timeout-height-offset", "4000", "--number-of-packets", "1"], timeout=300)
    if rc != 0:
        return False, "A→B 发送失败：" + " ".join(out.split())[:200]
    ibc_denom, got = "", 0
    for _ in range(18):
        time.sleep(10)
        lst = rest_balances(baddr) or []
        for b in lst:
            if b["denom"].startswith("ibc/") and int(b["amount"]) >= amt:
                ibc_denom, got = b["denom"], int(b["amount"])
                break
        if ibc_denom:
            break
    if not ibc_denom:
        return False, "A→B 超时未到账（中继没搬 or 报文卡住）：Osmosis 侧查不到 ibc/… 余额"
    log("A→B 实测到账：%s %s… = %d" % (baddr, ibc_denom[:14], got))
    rc, out = hq(["tx", "ft-transfer", "--dst-chain", A, "--src-chain", B,
                  "--src-connection", "connection-0", "--src-port", "transfer",
                  "--src-channel", facts.get("channel_B"), "--amount", str(amt // 2),
                  "--denom", ibc_denom, "--timeout-height-offset", "4000",
                  "--number-of-packets", "1"], timeout=300)
    back = 0
    for _ in range(18):
        time.sleep(10)
        d = wq(["bank", "balances", MAIN_ADDR], node=A_RPC)
        back = next((int(b["amount"]) for b in (d.get("balances") or []) if b.get("denom") == ibc_denom), 0)
        if back >= amt // 2:
            break
    ok = back >= amt // 2
    log("B→A 回程实测：主网 %s… = %d（预期 ≥ %d）%s"
        % (ibc_denom[:14], back, amt // 2, "通过" if ok else "不通过"))
    return ok, {"channel_A": chid, "channel_B": facts.get("channel_B"), "ibc_denom": ibc_denom,
                "ab_sent": amt, "ba_back": back}


def evidence(facts):
    txt = ("\n## %s 主网 ↔ Osmosis 通道实测证据\n\n"
           "- 中继身份：主网 `%s`；Osmosis 侧同一条助记词派生 `%s`（只放油钱的热钱包，和金库/结算密钥无关）\n"
           "- 通道：主网 `%s` ↔ Osmosis `%s`，端口 `transfer`，版本 `ics20-1`\n"
           "- 双向 ICS-20 实测：去程 %s ulight，回程到账 %s（外来面额 `%s…`）\n"
           "- 中继进程：`%s`（systemd，Restart=on-failure；配 watchdog 双向盯梢）\n"
           "- 结论：主网跨链从「链上 0 客户端 / 0 通道」变为「1 条通道 OPEN 且双向有回执」；"
           "LIGHT 以原生 `ulight` 经 ICS-20 直接搬运，无需 wLIGHT 封装。\n"
           % (time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), MAIN_ADDR, facts.get("osmo_addr", "?"),
              facts.get("channel_A", "?"), facts.get("channel_B", "?"), facts.get("ab_sent", "?"),
              facts.get("ba_back", "?"), (facts.get("ibc_denom") or "?")[:20], SVC))
    try:
        d = os.path.dirname(EVID)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(EVID, "a", encoding="utf-8") as f:
            f.write(txt)
        return True
    except Exception as e:
        log("证据写盘失败：%s" % str(e)[:80])
        return False


def selftest():
    """反向验证：五种该停手/该放行/该判失败的组合，逐一确认量具本身说得准。"""
    import tempfile
    cases = [
        ("没钱必须挡下", {"balance_A": 0, "balance_B": 0, "clients_A": 0, "channels_A": [],
                        "hermes_ok": True, "addr_B": "osmo1x"}, False),
        ("只够一侧也算没备齐", {"balance_A": MIN_ULIGHT + 1, "balance_B": 1, "clients_A": 0,
                             "channels_A": [], "hermes_ok": True, "addr_B": "osmo1x"}, False),
        ("半截状态（有客户端无通道）必须停手", {"balance_A": MIN_ULIGHT, "balance_B": MIN_UOSMO,
                                          "clients_A": 2, "channels_A": [], "hermes_ok": True,
                                          "addr_B": "osmo1x"}, False),
        ("已开通道不许重复开", {"balance_A": MIN_ULIGHT, "balance_B": MIN_UOSMO, "clients_A": 1,
                           "channels_A": [{"channel_id": "channel-0", "port_id": "transfer",
                                           "state": {"status": "STATE_OPEN"},
                                           "counterparty": {"channel_id": "channel-9"}}],
                           "hermes_ok": True, "addr_B": "osmo1x"}, False),
        ("万事俱备必须放行", {"balance_A": MIN_ULIGHT, "balance_B": MIN_UOSMO, "clients_A": 0,
                         "channels_A": [], "hermes_ok": True, "addr_B": "osmo1x"}, True),
        ("hermes 没就绪不许上链", {"balance_A": MIN_ULIGHT, "balance_B": MIN_UOSMO, "clients_A": 0,
                              "channels_A": [], "hermes_ok": False, "addr_B": "osmo1x"}, False),
        ("余额读不到要说「量具坏了」，不许混成「没钱」",
         {"balance_A": None, "balance_B": None, "clients_A": 0, "channels_A": [],
          "hermes_ok": True, "addr_B": "osmo1x"}, False),
    ]
    good = 0
    old_fx = os.environ.get("XC_MN_FIX")
    for name, data, want in cases:
        tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data, tf)
        tf.close()
        os.environ["XC_MN_FIX"] = tf.name
        globals()["FX"] = tf.name
        go, reasons, facts = precheck()
        ok = (go == want)
        good += 1 if ok else 0
        print("  [%s] %s → go=%s 期望=%s%s" % ("OK " if ok else "坏", name, go, want,
              ("" if ok else "  实际理由：" + "; ".join(reasons)[:120])))
        os.unlink(tf.name)
    os.environ.pop("XC_MN_FIX", None)
    globals()["FX"] = old_fx
    print("自检 %d/%d" % (good, len(cases)))
    return 0 if good == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只体检不动链")
    ap.add_argument("--force", action="store_true", help="忽略 opened 再体检一次（仍不会重复开通道）")
    ap.add_argument("--selftest", action="store_true", help="用假数据验证护栏本身灵不灵")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    st = load_state()
    print("状态文件：%s" % json.dumps(st, ensure_ascii=False)[:300])
    if st.get("status") == "opened" and not a.force:
        print("已 opened，一次上锁生效 —— 不重复操作（复核用 --dry-run --force）")
        return 0
    go, reasons, facts = precheck()
    print("护栏体检：%s" % json.dumps(facts, ensure_ascii=False))
    for r in reasons:
        print("  挡下：%s" % r)
    st.update(facts)
    st["reasons"] = reasons
    if not go:
        st["status"] = "waiting"
        save_state(st)
        log("未动手：%d 条护栏未过" % len(reasons))
        return 3
    if a.dry_run:
        st["status"] = "ready_to_open"
        save_state(st)
        log("护栏全过（--dry-run，未上链）：可以开")
        return 0
    lf = open(LOCKF, "w")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("已有另一个开通流程在跑，退出（防并发造重复客户端）")
        return 4
    st["status"] = "opening"
    save_state(st)
    ok, info = do_open()
    if not ok:
        st.update(status="failed", detail=str(info)[:400])
        save_state(st)
        log("开通失败：%s" % str(info)[:300])
        return 5
    okv, vf = verify_transfer(info if isinstance(info, dict) else {})
    vf = vf if isinstance(vf, dict) else {"detail": str(vf)[:300]}
    vf.setdefault("osmo_addr", facts.get("osmo_addr"))
    st.update(status="opened" if okv else "opened_unverified", verify=vf)
    save_state(st)
    if okv:
        evidence(vf)
        log("全绿：通道 OPEN + 双向转账对平，证据已写 %s" % EVID)
        return 0
    log("通道已开但双向验证没过：%s —— 记 opened_unverified，需人工看" % str(vf)[:200])
    return 6


if __name__ == "__main__":
    sys.exit(main())
