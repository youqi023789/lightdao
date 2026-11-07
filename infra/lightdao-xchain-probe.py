#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lightdao-xchain-probe —— 跨链状态的只读服务（给客户端"跨链"面板喂数）。

为什么要有这个服务，而不是让浏览器直接查：
  · 浏览器要自己拼 ABCI 证明查询才能读到通道/锁仓/未确认包，等于把链上查询逻辑抄第二份；
    本项目反复栽过"同一事实两份表达"，所以只允许服务端一处读、一处算；
  · 免费行情接口（CoinGecko）有速率限制：让每个访客各打一次，很快就把 IP 打进 429；
    服务端 60 秒缓存一次，全站共享，访客侧永远是快的。

边界（写死在代码里，不靠自觉）：
  · 只读：只做 query，不签名、不广播、不持有任何私钥；
  · 只绑 127.0.0.1:8095，公网经 nginx /xchain/ 反代并限速；
  · 主网跨链状态照实返回 enabled=false 与原因，绝不假装"已支持"。
"""
import json
import os
import re
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xc_bank   # 全量面额读取 + 外来 ibc/… 面额的来源与如实标注（只读）

BIN = os.environ.get("XC_BIN", "/home/ubuntu/lightd.testnet.bin")
RPC_A = os.environ.get("XC_RPC_A", "http://127.0.0.1:26757")
RPC_B = os.environ.get("XC_RPC_B", "http://127.0.0.1:26957")
RPC_MAIN = os.environ.get("XC_RPC_MAIN", "http://127.0.0.1:26657")
CH_A = "channel-2"
CH_B = "channel-0"
ESCROW_A = "wasm12k2pyuylm9t7ugdvz67h9pg4gmmvhn5v4658cl"
RELAYER_A = "wasm179u6h2xus9zetqe4ejwamxz6sv7ks8djf5kpjc"
RELAYER_B = "wasm1rct6n8snzdufxapu9qhxt3xwgg04k6cvxct60s"
MAIN_RELAY_SVC = os.environ.get("XC_MAIN_RELAY_SVC", "lightdao-ibc-mainnet.service")
CG = ("https://api.coingecko.com/api/v3/simple/price?ids=lightdao,bitcoin,ethereum,"
      "binancecoin,solana,uniswap,ripple,dogecoin&vs_currencies=usd&include_24hr_change=true")
UA = {"User-Agent": "LightDAO-XChain-Probe/1.0 (read-only status surface)"}
TTL_STATE = float(os.environ.get("XC_TTL_STATE", "20"))
TTL_PRICE = float(os.environ.get("XC_TTL_PRICE", "60"))
LOCK = threading.Lock()
CACHE = {"state": (0.0, None), "price": (0.0, None)}
BAL_CACHE = {}
TTL_BAL = float(os.environ.get("XC_TTL_BAL", "30"))


def balances_cached(addr):
    key = addr
    now = time.time()
    with LOCK:
        hit = BAL_CACHE.get(key)
        if hit and now - hit[0] < TTL_BAL:
            return hit[1], True
    v = xc_bank.summarize(RPC_MAIN, addr)
    with LOCK:
        if len(BAL_CACHE) > 512:      # 只读服务不能被陌生人拿地址表撑爆内存
            BAL_CACHE.clear()
        BAL_CACHE[key] = (now, v)
    return v, False


def http_json(url, timeout=8):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def cq(args, node, timeout=8):
    p = subprocess.run([BIN, "q"] + args + ["-o", "json", "--node", node],
                       capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[:120].replace("\n", " "))
    return json.loads(p.stdout)


def stake_of(node, addr):
    for b in (cq(["bank", "balances", addr], node).get("balances") or []):
        if b.get("denom") == "stake":
            return int(b["amount"])
    return 0


def ibc_amt_of(node, addr, needle):
    for b in (cq(["bank", "balances", addr], node).get("balances") or []):
        if b.get("denom", "").startswith(needle):
            return int(b["amount"])
    return 0


def pend(node, ch):
    j = cq(["ibc", "channel", "packet-commitments", "transfer", ch], node)
    return [int(c["sequence"]) for c in (j.get("commitments") or []) if c.get("sequence")]


def channel_end(node, ch):
    j = cq(["ibc", "channel", "end", "transfer", ch], node)
    c = j.get("channel") or {}
    return {"state": c.get("state"), "counterparty": (c.get("counterparty") or {}).get("channel_id"),
            "connection": (c.get("connection_hops") or [None])[0]}


def quote(frm, to, amount, sym_from, sym_to):
    """第三方聚合器（Li.Fi）的跨链报价：服务端代理 = 免 CORS、可缓存、可限流。
       fromAddress 只为满足接口的必填校验而传零地址，绝不带任何访客信息。
       报价里的数字全部来自接口原值（toAmount/toAmountMin/gasCosts/executionDuration），
       本站不重算、不四舍五入成"看起来更好"的数（ decimals 只用于人类可读展示）。"""
    u = ("https://li.quest/v1/quote?" + urllib.parse.urlencode({
        "fromChain": frm, "fromToken": sym_from, "toChain": to, "toToken": sym_to,
        "fromAmount": str(amount),
        # 接口拒绝零地址（实测 400），这里用一个语法合法的占位地址：
        # 报价不需要真实发件人，但绝不能把访客地址带出去。
        "fromAddress": os.environ.get("XC_QUOTE_PLACEHOLDER", "0x1111111111111111111111111111111111111111")}))
    d = http_json(u, timeout=15)
    est = d.get("estimate") or {}
    act = d.get("action") or {}
    t = d.get("toolDetails") or {}
    if "message" in d and not est:
        raise RuntimeError("接口返回错误：%s" % str(d.get("message"))[:90])

    def human(raw, dec):
        try:
            return round(int(raw) / (10 ** int(dec or 0)), 8)
        except Exception:
            return None
    fdec = ((act.get("fromToken") or {}).get("decimals")) or 0
    tdec = ((act.get("toToken") or {}).get("decimals")) or 0
    gas_usd = None
    try:
        gas_usd = round(sum(float(g.get("amountUSD") or 0) for g in (est.get("gasCosts") or [])), 4) or None
    except Exception:
        gas_usd = None
    out = {"ok": True, "tool": t.get("name") or est.get("tool") or d.get("tool"),
           "from": {"chain": (act.get("fromChainId") or frm),
                    "symbol": (act.get("fromToken") or {}).get("symbol"),
                    "amount": human(est.get("fromAmount") or amount, fdec)},
           "to": {"chain": (act.get("toChainId") or to),
                  "symbol": (act.get("toToken") or {}).get("symbol"),
                  "amount": human(est.get("toAmount"), tdec),
                  "amount_min": human(est.get("toAmountMin"), tdec),
                  "usd": est.get("toAmountUSD")},
           "gasUsd": gas_usd, "etaSec": est.get("executionDuration"),
           "feeCosts": len(est.get("feeCosts") or []),
           "deeplink": "https://li.fi/swap?fromChain=%s&fromToken=%s&toChain=%s&toToken=%s&fromAmount=%s"
                       % (frm, sym_from, to, sym_to, amount),
           "notice": "报价来自第三方聚合器 Li.Fi；签名与广播在你自己的钱包里完成，"
                     "LightDAO 不托管资产、不参与撮合，也不保证成交结果。",
           "utc": stamp()}
    if not out["to"]["amount"]:
        raise RuntimeError("接口没给出到账数量（该线路由暂不可用）")
    return out


QUOTE_TTL = float(os.environ.get("XC_TTL_QUOTE", "25"))
HOME_A = os.environ.get("XC_HOME_A", "/home/ubuntu/.lightd-testnet")
HOME_B = os.environ.get("XC_HOME_B", "/home/ubuntu/.lightd-testnet-b")
IBC_DENOM = os.environ.get("XC_IBC_DENOM",
                           "ibc/C053D637CCA2A2BA030E2C5EE1B28A16F71CCB0E45E8BE52766DC1B241B77878")
# 演示转账用的账户（测试网专用，钥匙环在 A 的 home 里；不在 unit 里写死地址，靠 EnvironmentFile）
DEMO_KEY = os.environ.get("XC_DEMO_KEY", "demo")
DEMO_ACCT = os.environ.get("XC_DEMO_ACCT", "")
HISTF = os.environ.get("XC_HIST", "/home/ubuntu/ld_xchain_txhist.json")
TXHIST = {"h": [], "ip": []}          # 转账额度台账（落盘，见 load_hist/save_hist）；只存时间戳与 IP


def sh(cmd, timeout=60):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout or "", p.stderr or ""


def load_hist():
    """限额状态必须落盘：只在内存里记账，重启服务就等于把额度清零（等于没有限额）。"""
    try:
        with open(HISTF, encoding="utf-8") as f:
            d = json.load(f)
        TXHIST["h"] = [[float(x[0]), x[1]] for x in (d.get("h") or [])]
        TXHIST["ip"] = [[float(x[0]), str(x[1])] for x in (d.get("ip") or [])]
    except Exception:
        pass


def save_hist():
    try:
        tmp = HISTF + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(TXHIST, f)
        os.replace(tmp, HISTF)
    except Exception as e:
        tx_log("hist-save 失败：%s" % str(e)[:60])


def tx_log(msg):
    try:
        with open("/home/ubuntu/ld_xchain_tx.log", "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (stamp(), msg))
    except Exception:
        pass


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def transfer(direction, amount, receiver, ip):
    """客户端面板发起的**测试网**跨链转账（真实上链，不是演示动画）。

    写死的安全边界（一条不满足就直接拒绝，不看调用方是谁）：
      · 方向只认 ab / ba，通道固定 A:channel-2 ↔ B:channel-0；
      · 签名账户是测试网专用 demo 账户（不在主网钥匙环里，主网一分钱都不经过这里）；
      · 单笔 ≤ XC_MAX（默认 50,000 stake）、每小时 ≤ XC_QUOTA（默认 12 笔）、同一 IP 5 分钟 1 笔；
      · 广播前用链上 account 序列与 chain-id 双重核对，链对不上立刻中止；
      · 每一笔都往 ld_xchain_tx.log 记一行（时间、方向、金额、txhash、来源 IP），事后可核对。
    """
    lim = int(os.environ.get("XC_MAX", "50000"))
    quota = int(os.environ.get("XC_QUOTA", "12"))
    if direction not in ("ab", "ba"):
        raise ValueError("方向只能是 ab/ba")
    if direction == "ba" and os.environ.get("XC_ALLOW_BA") != "1":
        raise ValueError("回顶方向（B→A）未开放（需运维显式开 XC_ALLOW_BA）")
    # 两个方向各自的"身份四件套"全部来自 EnvironmentFile：代码里不写死账户与通道，
    # 免得将来换对端/换演示账户时改一处漏一处。
    D = {
        "ab": {"node": RPC_A, "home": HOME_A, "chain": "lightdao-testnet-gas", "ch": CH_A,
               "key": DEMO_KEY, "recv": os.environ.get("XC_DEMO_RECV", ""),
               "denom": "stake", "pend": lambda: pend(RPC_A, CH_A),
               "gas": lambda: stake_of(RPC_B, RELAYER_B), "signer": DEMO_ACCT,
               "avail": lambda: stake_of(RPC_A, DEMO_ACCT),
               "sendable": lambda: stake_of(RPC_A, DEMO_ACCT),
               "label": "测试网 A→B"},
        "ba": {"node": RPC_B, "home": HOME_B, "chain": "lightdao-testnet-b", "ch": CH_B,
               "key": os.environ.get("XC_BA_KEY", "demob"),
               "recv": os.environ.get("XC_BA_RECV", ""),
               "denom": IBC_DENOM, "pend": lambda: pend(RPC_B, CH_B),
               "gas": lambda: stake_of(RPC_A, RELAYER_A), "signer": os.environ.get("XC_BA_ACCT", ""),
               "sendable": lambda: ibc_amt_of(RPC_B, os.environ.get("XC_BA_ACCT", ""), "ibc/"),
               "label": "测试网 B→A"},
    }[direction]
    try:
        amt = int(amount) if str(amount or "").strip() else int(os.environ.get("XC_DEMO_AMOUNT", "20000"))
    except Exception:
        raise ValueError("金额必须是整数（6 位小数的 stake 最小单位）")
    if not (0 < amt <= lim):
        raise ValueError("单笔金额必须在 1 ~ %d 之间" % lim)
    recv = (receiver or D["recv"]).strip()
    if not re.match(r"^wasm1[02-9ac-hj-np-z]{38,58}$", recv):
        raise ValueError("收款地址格式不对")
    # 收款人白名单：不然这个按钮就成了任意地址的提款口（虽然是测试币，
    # 但也别让访客能把我们的演示账户搬到陌生地址上去计数）。
    if os.environ.get("XC_ALLOW_ANY_RECV") != "1" and recv != D["recv"].strip():
        raise ValueError("演示转账只发往该方向固定的演示地址（防止被当成提款口）")
    # 配额与限流
    now = time.time()
    with LOCK:
        hist = TXHIST.setdefault("h", [])
        TXHIST["h"] = [x for x in hist if now - x[0] < 3600]
        ips = TXHIST.setdefault("ip", [])
        TXHIST["ip"] = [x for x in ips if now - x[0] < 300]
        if len(TXHIST["h"]) >= quota:
            raise RuntimeError("本小时测试网跨链额度已用完（%d 笔）" % quota)
        # 按"来源 + 方向"限流：同一访客演示完去程还能演示回程，
        # 但同一方向仍然 5 分钟一笔（不放开成想发就发）。
        if any(x[1] == ip + "|" + direction for x in TXHIST["ip"]):
            raise RuntimeError("同一来源同一方向 5 分钟内只能发一笔")
    got = http_json(D["node"] + "/status", timeout=10)
    cid = got["result"]["node_info"].get("network")
    if cid != D["chain"]:
        raise RuntimeError("源链 chain-id 对不上（读到 %s，要求 %s）——拒绝广播" % (cid, D["chain"]))
    # 发之前先看"路上有没有人"和"账户还够不够"：宁可按钮报错，
    # 也不要发一笔注定卡在半路的包，让访客以为跨链坏了。
    try:
        stuck = D["pend"]()
        chst = channel_end(D["node"], D["ch"])
    except Exception as e:
        raise RuntimeError("读不到通道/在途包，拒绝广播：%s" % str(e)[:60])
    if str(chst.get("state")) not in ("STATE_OPEN", "OPEN"):
        raise RuntimeError("通道不是 OPEN（实测 %s）" % chst.get("state"))
    if stuck:
        raise RuntimeError("%s 已有 %d 个包在途，等中继消化完再发" % (D["label"], len(stuck)))
    if D["gas"]() < 200000:
        raise RuntimeError("对面中继账户油钱不足 200,000 stake：发出去也没人搬包")
    if not D["signer"]:
        raise RuntimeError("该方向没配签名账户地址（EnvironmentFile 缺项），拒绝广播")
    # 签名账户既要有 gas，也要有"要发出去的那种币"：
    #   ab 发的是原生 stake；ba 发的是 ibc 面额 —— 只查 stake 会让 ba 在"有钱但发不出"时假通过。
    if stake_of(D["node"], D["signer"]) < int(os.environ.get("XC_DEMO_FLOOR", "200000")):
        raise RuntimeError("签名账户 gas 不足，已停止对外演示（需管理员补测试币）")
    if D["sendable"]() < amt + int(os.environ.get("XC_SEND_FLOOR", "10000")):
        raise RuntimeError("%s 侧签名账户可发的 %s 不够这一笔（还差 %d）"
                           % (D["label"], D["denom"][:12], amt + 10000 - D["sendable"]()))
    if direction == "ab":
        # 发之前先看"路上有没有人"和"演示账户还够不够"：宁可按钮报错，
        # 也不要发一笔注定卡在半路的包让访客以为跨链坏了。
        try:
            stuck = pend(RPC_A, CH_A)
            chst = channel_end(RPC_A, CH_A)
        except Exception as e:
            raise RuntimeError("读不到通道/未确认包，拒绝广播：%s" % str(e)[:60])
        if str(chst.get("state")) not in ("STATE_OPEN", "OPEN"):
            raise RuntimeError("通道不是 OPEN（实测 %s）" % chst.get("state"))
        if stuck:
            raise RuntimeError("A→B 已有 %d 个包在途，等中继消化完再发" % len(stuck))
        if stake_of(RPC_A, RELAYER_A) < 200000:
            raise RuntimeError("中继账户油钱不足 200,000 stake：现在发出去也没人搬包")
        if not DEMO_ACCT:
            raise RuntimeError("没配 XC_DEMO_ACCT（演示账户地址），拒绝广播")
        if stake_of(RPC_A, DEMO_ACCT) < int(os.environ.get("XC_DEMO_FLOOR", "200000")):
            raise RuntimeError("演示账户余额过低，已停止对外演示（需管理员补测试币）")
    cmd = [BIN, "tx", "ibc-transfer", "transfer", "transfer", D["ch"], recv, "%d%s" % (amt, D["denom"]),
           "--from", D["key"], "--home", D["home"], "--keyring-backend", "test",
           "--chain-id", D["chain"], "--node", D["node"], "--broadcast-mode", "sync",
           "-y", "--gas", "auto", "--gas-adjustment", "1.6", "--fees", "60000stake", "-o", "json"]
    txh = None
    try:
        rc, out, err = sh(cmd)
        if rc != 0:
            raise RuntimeError((err or out)[:180])
        d = json.loads(out)
        txh = d.get("txhash")
        if int(d.get("code") or 0) != 0:
            raise RuntimeError("链上拒绝：code=%s %s" % (d.get("code"), str(d.get("raw_log"))[:150]))
    finally:
        with LOCK:
            TXHIST["h"].append((time.time(), txh))
            TXHIST["ip"].append((time.time(), ip + "|" + direction))
            save_hist()
        tx_log("dir=%s amount=%d recv=%s tx=%s ip=%s" % (direction, amt, recv, txh, ip))
    return {"ok": True, "txhash": txh, "direction": direction, "amount": amt,
            "denom": D["denom"], "channel": D["ch"], "chain_id": D["chain"],
            "note": "已广播；到账要靠中继搬包，面板每 20 秒刷新一次未确认包与对面余额。",
            "utc": stamp()}


def chain_brief(node, expect=None):
    j = http_json(node + "/status")["result"]
    si, ni = j["sync_info"], j.get("node_info", {})
    cid = ni.get("network") or si.get("network")
    d = {"chain_id": cid, "height": int(si["latest_block_height"]),
         "block_time": si["latest_block_time"], "catching_up": bool(si.get("catching_up"))}
    if expect and cid != expect:
        d["chain_id_mismatch"] = expect
    return d


def ibc_client_count(node):
    return len((cq(["ibc", "client", "states"], node) or {}).get("client_states") or [])


def state():
    s = {"ts": time.time(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    err = []
    for k, node, exp in (("a", RPC_A, "lightdao-testnet-gas"), ("b", RPC_B, "lightdao-testnet-b"),
                         ("main", RPC_MAIN, "lightdao-mainnet-1")):
        try:
            s[k] = chain_brief(node, exp)
        except Exception as e:
            s[k] = None
            err.append("%s 链状态读不到：%s" % (k, str(e)[:60]))
    try:
        s["channel_a"] = channel_end(RPC_A, CH_A)
        s["channel_b"] = channel_end(RPC_B, CH_B)
    except Exception as e:
        s["channel_a"] = s["channel_b"] = None
        err.append("通道读不到：%s" % str(e)[:60])
    for key, fn in (("escrow_a", lambda: stake_of(RPC_A, ESCROW_A)),
                    ("pending_a2b", lambda: pend(RPC_A, CH_A)),
                    ("pending_b2a", lambda: pend(RPC_B, CH_B)),
                    ("relayer_gas_a", lambda: stake_of(RPC_A, RELAYER_A)),
                    ("relayer_gas_b", lambda: stake_of(RPC_B, RELAYER_B))):
        try:
            s[key] = fn()
        except Exception as e:
            s[key] = None
            err.append("%s 读不到：%s" % (key, str(e)[:60]))
    try:
        s["ibc_in_b"] = ibc_amt_of(RPC_B, RELAYER_B, "ibc/")
    except Exception as e:
        s["ibc_in_b"] = None
        err.append("ibc 余额读不到：%s" % str(e)[:60])
    # 演示账户与剩余额度：面板据此置灰按钮，而不是让人点了才知道不行
    try:
        with LOCK:
            used = len([x for x in TXHIST["h"] if time.time() - x[0] < 3600])
        s["demo"] = {"account": DEMO_ACCT or None,
                     "ba_allowed": os.environ.get("XC_ALLOW_BA") == "1",
                     "ba_signer": os.environ.get("XC_BA_ACCT") or None,
                     "ba_stake": stake_of(RPC_B, os.environ["XC_BA_ACCT"]) if os.environ.get("XC_BA_ACCT") else None,
                     "stake": stake_of(RPC_A, DEMO_ACCT) if DEMO_ACCT else None,
                     "quota_left": max(0, int(os.environ.get("XC_QUOTA", "12")) - used),
                     "max": int(os.environ.get("XC_MAX", "50000")),
                     "receiver": os.environ.get("XC_DEMO_RECV", "wasm1vgjc0y4ut6j9xjrhxvqqlguzgaqkxer2anjkmg")}
    except Exception as e:
        s["demo"] = None
        err.append("演示账户信息读不到：%s" % str(e)[:60])
    # 主网跨链：照实说明，不假装；并且把"未开通"这件事用主网自己的读数兜住
    mn, mn_errs = mainnet_state()
    s["mainnet_ibc"] = mn
    err.extend(mn_errs)
    s["errors"] = err
    return s


def chan_state(c):
    """本链 CLI 的 channel state 是字符串 "STATE_OPEN"，上游部分版本是 {"status": ...}。
       只认一种形状就会把"已开通"读成"没有通道"（11-07 实撞过一次）。"""
    st = c.get("state")
    if isinstance(st, str):
        return st
    return (st or {}).get("status") if isinstance(st, dict) else None


def mainnet_state():
    """主网跨链的真实状态：现查链上，不写死。返回 (给面板的 dict, 错误列表)"""
    errs = []
    out = {"enabled": False, "reason_code": "unknown", "reason_zh": "",
           "mainnet_clients": None, "mainnet_channels": None, "relayer": None,
           "testnet_zh": "测试网 A(lightdao-testnet-gas) ↔ B(lightdao-testnet-b) 已双向实测自动中继"}
    try:
        out["mainnet_clients"] = ibc_client_count(RPC_MAIN)
    except Exception as e:
        errs.append("主网 IBC 客户端数量读不到：%s" % str(e)[:60])
    chs = []
    try:
        for c in (cq(["ibc", "channel", "channels"], RPC_MAIN).get("channels") or []):
            chs.append({"id": c.get("channel_id"), "port": c.get("port_id"),
                        "state": chan_state(c),
                        "peer": (c.get("counterparty") or {}).get("channel_id"),
                        "conn": (c.get("connection_hops") or [None])[0],
                        "version": c.get("version")})
    except Exception as e:
        errs.append("主网 IBC 通道读不到：%s" % str(e)[:60])
    out["mainnet_channels"] = len(chs)
    open_ch = [c for c in chs if c["port"] == "transfer" and c["state"] == "STATE_OPEN"]
    try:
        p = subprocess.run(["systemctl", "is-active", MAIN_RELAY_SVC],
                           capture_output=True, text=True, timeout=8)
        out["relayer"] = (p.stdout or "").strip() or "unknown"
    except Exception as e:
        out["relayer"] = "读不到"
        errs.append("主网中继进程状态读不到：%s" % str(e)[:50])
    if open_ch:
        c0 = open_ch[0]
        out["enabled"] = True
        out["reason_code"] = "open"
        out["channel"] = c0["id"]
        out["peer_channel"] = c0["peer"]
        out["connection"] = c0["conn"]
        out["version"] = c0["version"]
        out["peer_chain_hint"] = "osmosis-1"
        # 超时高度必须按**对端客户端同步到的高度**算（ibc-go 的校验口径）。
        # 浏览器自己拿主网高度填 timeout，会得到"出生即过期"的报文（11-07 实测拒发）。
        try:
            cs = cq(["ibc", "client", "state", "07-tendermint-0"], RPC_MAIN)
            lh = (((cs.get("client_state") or {}).get("latest_height")) or {})
            out["peer_revision"] = int(lh.get("revision_number") or 0)
            out["peer_height"] = int(lh.get("revision_height") or 0)
        except Exception as e:
            out["peer_height"] = None
            errs.append("对端客户端高度读不到（浏览器会拒绝发送而不是填错）：%s" % str(e)[:50])
        if out["relayer"] not in ("active",):
            errs.append("主网通道已 OPEN，但中继进程 %s=%s —— 转账会卡在途，用户端表现为不到账"
                        % (MAIN_RELAY_SVC, out["relayer"]))
    elif out["mainnet_clients"]:
        out["reason_code"] = "partial_state"
        out["reason_zh"] = "主网已有 IBC 轻客户端但没有 OPEN 的 transfer 通道（半截状态），需人工核对"
        errs.append("主网有 %d 个轻客户端却没有 OPEN 通道 = 半截状态" % out["mainnet_clients"])
    else:
        out["reason_code"] = "no_channel_yet"
        out["reason_zh"] = ("主网还没有建立任何跨链通道：链上实测 IBC 轻客户端 0 个、通道 0 条。"
                            "LIGHT 本身就是原生币 ulight，ICS-20 可直接搬运；缺的是对端链选定、"
                            "通道与中继的部署，以及治理授权（接收哪些对面额、中继权限与额度）。")
    return out, errs


def price():
    j = http_json(CG, timeout=10)
    out = {"ts": time.time(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "usd": {}}
    for k, v in (j or {}).items():
        out["usd"][k] = {"usd": v.get("usd"), "chg24h": v.get("usd_24h_change")}
    return out


def cached(which, fn, ttl):
    with LOCK:
        t, val = CACHE[which]
        if val is not None and time.time() - t < ttl:
            return val, True
    v = fn()
    with LOCK:
        CACHE[which] = (time.time(), v)
    return v, False


class H(BaseHTTPRequestHandler):
    server_version = "LD-XChain/1.0"

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "https://lightdao.net")
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p not in ("/v1/transfer", "/v1/transfer/"):
            self._send(404, {"ok": False, "error": "只有 /v1/transfer 接受 POST"})
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(min(n, 2048)).decode("utf-8", "replace")
            body = json.loads(raw or "{}")
            ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
            out = transfer(str(body.get("direction", "")), body.get("amount"),
                           str(body.get("receiver", "")), ip)
            self._send(200, out)
        except Exception as e:
            self._send(400, {"ok": False, "error": str(e)[:180]})

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p in ("/v1/health", "/v1/health/"):
            self._send(200, {"ok": True, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            return
        if p in ("/v1/ibc", "/v1/ibc/"):
            try:
                v, hit = cached("state", state, TTL_STATE)
                v = dict(v)
                v["cached"] = hit
                self._send(200, v)
            except Exception as e:
                self._send(500, {"ok": False, "error": str(e)[:200]})
            return
        if p in ("/v1/prices", "/v1/prices/"):
            try:
                v, hit = cached("price", price, TTL_PRICE)
                v = dict(v)
                v["cached"] = hit
                self._send(200, v)
            except Exception as e:
                self._send(502, {"ok": False, "error": str(e)[:200]})
            return
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if p in ("/v1/quote", "/v1/quote/"):
            try:
                out = quote((q.get("fromChain") or ["1"])[0], (q.get("toChain") or ["10"])[0],
                            (q.get("fromAmount") or ["1000000000000000000"])[0],
                            (q.get("fromToken") or ["ETH"])[0], (q.get("toToken") or ["USDC"])[0])
                self._send(200, out)
            except Exception as e:
                self._send(502, {"ok": False, "error": str(e)[:200]})
            return
        m = re.match(r"^/v1/balances/(wasm1[a-z0-9]{38,59})/?$", p)
        if m:
            # 全量面额：本链 ulight + 任意外来 ibc/… 都列出来，外来的一律标非本链发行
            try:
                v, hit = balances_cached(m.group(1))
                v = dict(v)
                v["cached"] = hit
                self._send(200 if v.get("ok") else 502, v)
            except Exception as e:
                self._send(502, {"ok": False, "error": str(e)[:200]})
            return
        self._send(404, {"ok": False, "error": "unknown path", "paths": ["/v1/ibc", "/v1/prices", "/v1/health", "/v1/balances/<wasm1…>"]})

    def log_message(self, fmt, *a):
        pass


def main():
    # 默认端口与 systemd unit、nginx 反代保持一致（8095 是 g7_fuzz 的影子网关在用）
    port = int(os.environ.get("XC_PORT", "8096"))
    load_hist()
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print("xchain probe on 127.0.0.1:%d" % port, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
