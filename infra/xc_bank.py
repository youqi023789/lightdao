#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xc_bank.py —— 读「一个地址在链上的全部面额」并如实标注来源（只给查询，不签名不广播）。
为什么要有它：主网 IBC 转账参数实测 send_enabled=true、receive_enabled=true、
allowed_clients=["*"]，也就是**任意外来 ibc/… 面额都能入账**（公链应有的姿态）；
但客户端所有余额代码写死了 `ulight`，一旦真有钱进来，用户看不到 = 静默丢钱。
这个模块就是把"所有面额"读出来、分清楚哪些是本链发的、哪些是跨来的、跨来的从哪条通道来。

为什么不用 LCD/REST：浏览器侧只有同源 /rpc/（ABCI 查询），加一条 LCD 反代等于多开一个公网口；
服务端直接对本地 RPC 发 abci_query，protobuf 自己解 —— 依赖为零，可自测。

自检（--selftest）：自己造 protobuf 字节 → 自己解回来，逐项比对；解不出来就等于量具坏了。
"""

import base64
import json
import re
import urllib.request

ADDR_RE = re.compile(r"^wasm1[a-z0-9]{38,59}$")
IBC_RE = re.compile(r"^ibc/[0-9A-F]{64}$")
NATIVE = "ulight"          # 本链原生面额（白皮书第四章：质押/治理/Gas 均为 ulight）


# ---------- 最小 protobuf 线格式（够 IBC/bank 的这几个查询用） ----------
def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def enc_str_field(no, s):
    tag = (no << 3) | 2
    raw = s.encode() if isinstance(s, str) else s
    return _varint(tag) + _varint(len(raw)) + raw


def decode(msg):
    """返回 [(字段号, 线型, 值)]；线型 0=varint(int)，2=长度分隔(bytes)"""
    out, i = [], 0
    while i < len(msg):
        key, shift = 0, 0
        while True:
            if i >= len(msg):
                raise ValueError("截断的 varint")
            b = msg[i]; i += 1
            key |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        wt = key & 7
        if wt == 0:
            v, shift = 0, 0
            while True:
                b = msg[i]; i += 1
                v |= (b & 0x7F) << shift
                if not b & 0x80:
                    break
                shift += 7
            out.append((key >> 3, 0, v))
        elif wt == 2:
            ln, shift = 0, 0
            while True:
                b = msg[i]; i += 1
                ln |= (b & 0x7F) << shift
                if not b & 0x80:
                    break
                shift += 7
            out.append((key >> 3, 2, msg[i:i + ln])); i += ln
        elif wt == 5:
            out.append((key >> 3, 5, msg[i:i + 4])); i += 4
        elif wt == 1:
            out.append((key >> 3, 1, msg[i:i + 8])); i += 8
        else:
            raise ValueError("不支持的线型 %d" % wt)
    return out


def fields(msg, no):
    return [v for (n, wt, v) in decode(msg) if n == no]


def s(msg, no, idx=0, default=""):
    f = fields(msg, no)
    if len(f) <= idx:
        return default
    v = f[idx]
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)


# ---------- 链上查询 ----------
def abci(node, path, payload, timeout=8):
    """CometBFT 的 /abci_query JSON-RPC：data 与 response.value 都是**十六进制**，不是 base64；
    而且 params.height 要么是字符串要么是省略 —— 传整数 0 会直接 "Invalid params"（实测踩到）。
    这两处写错的表象都是"读不到"，会被误当成"没钱"，所以正例反例都要有（见 --selftest + 对照 CLI）。"""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "abci_query",
                       "params": {"path": path, "data": payload.hex(),
                                  "prove": False}}).encode()
    req = urllib.request.Request(node, data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "LightDAO-XChain-Probe/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as f:
        d = json.load(f)
    r = (d.get("result") or d)
    resp = r.get("response") or {}
    code = int(resp.get("code") or 0)
    val = resp.get("value") or ""
    if code != 0:
        raise RuntimeError("%s code=%s log=%s" % (path, code, str(resp.get("log"))[:80]))
    if not val:
        raise RuntimeError("%s 返回空 value（查询没命中，不是余额为 0）" % path)
    # 请求侧 data 要十六进制，响应侧 value 却是 base64（CometBFT 0.38 就是这么不对称）；
    # 两种都试，别按"应该一致"的想当然写死 —— 写错的表象同样是"读不到"。
    if re.match(r"^[0-9a-fA-F]+$", val) and len(val) % 2 == 0:
        try:
            return bytes.fromhex(val)
        except Exception:
            pass
    return base64.b64decode(val)


def all_balances(node, addr):
    """→ [(denom, amount_str)]，包含 ulight 与全部 ibc/… 外来面额"""
    raw = abci(node, "/cosmos.bank.v1beta1.Query/AllBalances", enc_str_field(1, addr))
    out = []
    for coin in fields(raw, 1):
        if not isinstance(coin, bytes):
            continue
        d, a = s(coin, 1), s(coin, 2)
        if d:
            out.append((d, a))
    return out


def denom_trace(node, hash_):
    """ibc/… → 它的来源路径（transfer/channel-N/基币）。查不到就返回 None（外来但未登记，照样如实显示）。"""
    try:
        raw = abci(node, "/ibc.applications.transfer.v1.Query/DenomTrace", enc_str_field(1, hash_))
    except Exception:
        return None
    t = fields(raw, 1)
    if not t or not isinstance(t[0], bytes):
        return None
    inner = t[0]
    return {"path": s(inner, 1), "base_denom": s(inner, 2)}


def denom_meta(node, denom):
    """面额元数据（符号/显示名/小数位）。链上没登记元数据时返回 None —— 不能瞎编符号。"""
    try:
        raw = abci(node, "/cosmos.bank.v1beta1.Query/Metadata", enc_str_field(1, denom))
    except Exception:
        return None
    m = fields(raw, 1)
    if not m or not isinstance(m[0], bytes):
        return None
    inner = m[0]
    units = []
    for u in fields(inner, 2):
        if isinstance(u, bytes):
            exp = [v for (n, wt, v) in decode(u) if n == 2 and wt == 0]
            units.append({"denom": s(u, 1), "exponent": exp[0] if exp else 0})
    return {"description": s(inner, 1), "base": s(inner, 3), "display": s(inner, 4),
            "name": s(inner, 5), "symbol": s(inner, 6), "denom_units": units}


def transfer_params(node):
    """收/发策略实测。两种线形都要吃下：
       · 本链 fork：Params{ bool send_enabled=1; bool receive_enabled=2 }（CLI 打出 true/true）
       · 上游 SDK ：Params{ repeated DenomEnabled send_enabled=1; repeated bool receive_enabled=2 }
    读不到就标 unknown —— 把"读不到"写成"允许/不允许"都是撒谎。"""
    try:
        raw = abci(node, "/ibc.applications.transfer.v1.Query/Params", b"")
    except Exception as e:
        return {"ok": False, "error": str(e)[:90], "send_enabled": None, "receive_enabled": None}
    pm = [x for x in fields(raw, 1) if isinstance(x, bytes)]
    params = decode(pm[0]) if pm else []
    send_bool = [v for (n, wt, v) in params if n == 1 and wt == 0]
    recv_bool = [v for (n, wt, v) in params if n == 2 and wt == 0]
    send_list = [v for (n, wt, v) in params if n == 1 and wt == 2]
    per_denom = []
    for d in send_list:
        f = decode(d)
        en = [v for (n, wt, v) in f if n == 1 and wt == 0]
        dn = [v.decode("utf-8", "replace") for (n, wt, v) in f if n == 2 and wt == 2]
        per_denom.append({"denom": dn[0] if dn else "?", "enabled": bool(en[0]) if en else None})
    return {"ok": True,
            "wire_form": "fork-bool" if send_bool else "sdk-list",
            "send_enabled": (bool(send_bool[0]) if send_bool else (True if not per_denom else "见 per_denom")),
            "receive_enabled": (bool(recv_bool[0]) if recv_bool else True),
            "per_denom": per_denom}


def humanize(denom, amount, meta):
    """把最小单位换算成显示单位（有元数据用元数据，没有就按 6 位小数并标 out of assumption）"""
    try:
        a = int(amount)
    except Exception:
        return {"display": amount, "assumed": True}
    exp, disp = 6, NATIVE if denom == NATIVE else denom
    if meta:
        for u in meta.get("denom_units") or []:
            if u["denom"] == meta.get("display"):
                exp = int(u.get("exponent") or 0)
        disp = meta.get("display") or disp
    val = a / float(10 ** exp) if exp else float(a)
    return {"display_amount": ("%.{}f".format(exp) % val).rstrip("0").rstrip(".") if exp else str(int(val)),
            "display_denom": disp, "exponent": exp,
            # 原生 ulight 的 6 位小数是链上 denom 元数据（ulight/mlight/light）写死的，不算"猜"；
            # 外来面额没登记元数据时按 6 位显示 = 假设，必须标出来，UI 得如实带"小数位未登记"
            "assumed": (meta is None and denom != NATIVE)}


def summarize(node, addr, ours_note="LIGHT 原生面额（本链发行）"):
    """给面板用的一份余额清单：本链 / 外来跨链 / 其它，逐条带来源与是否可验证。"""
    if not ADDR_RE.match(addr or ""):
        return {"ok": False, "error": "地址格式不对（要 wasm1…）"}
    out = {"ok": True, "address": addr, "native": NATIVE, "balances": [], "warnings": []}
    try:
        bals = all_balances(node, addr)
    except Exception as e:
        return {"ok": False, "error": "链上读不到：%s" % str(e)[:90]}
    for d, a in bals:
        meta = denom_meta(node, d) if not IBC_RE.match(d) else None
        item = {"denom": d, "amount": a, "ours": d == NATIVE,
                "kind": "native" if d == NATIVE else ("ibc" if IBC_RE.match(d) else "other"),
                "unvetted": False, "source": None}
        item.update(humanize(d, a, meta))
        if meta:
            item["symbol"] = meta.get("symbol") or None
            item["name"] = meta.get("name") or None
        if IBC_RE.match(d):
            tr = denom_trace(node, d)
            if tr:
                item["source"] = tr
                base = tr.get("base_denom") or ""
                item["origin_denom"] = base
                md = denom_meta(node, base)
                if md:
                    item["symbol"] = md.get("symbol") or item.get("symbol")
                    item["name"] = md.get("name") or item.get("name")
            else:
                item["unvetted"] = True
                out["warnings"].append("%s 没有链上来源登记，只能按原始哈希显示" % d[:18])
        if item["kind"] != "native" and item.get("assumed"):
            item["unvetted"] = True
        out["balances"].append(item)
    out["counts"] = {k: len([b for b in out["balances"] if b["kind"] == k])
                     for k in ("native", "ibc", "other")}
    out["policy"] = transfer_params(node)
    if out["policy"].get("ok"):
        out["policy_note"] = ("参数实测：receive_enabled=%s、send_enabled=%s，无面额名单限制 → "
                              "任意外来 ibc/… 面额可入账；外来面额一律标「非 LIGHT 发行」，不计入 LIGHT 总量"
                              % (out["policy"].get("receive_enabled"), out["policy"].get("send_enabled")))
    else:
        out["policy_note"] = ("链上收/发参数这次读不到（%s）—— 不下结论，UI 要显示「读不到」"
                              % out["policy"].get("error"))
    return out


def _selftest():
    """自己造 protobuf 字节，再解回来 —— 解不对就说明量具坏了，不能拿去汇报余额。"""
    coin = enc_str_field(1, "ibc/ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789") \
        + enc_str_field(2, "1234567")
    coin2 = enc_str_field(1, "ulight") + enc_str_field(2, "1000000")
    resp = enc_str_field(1, coin) + enc_str_field(1, coin2)
    got = [tuple(x) for x in [(s(c, 1), s(c, 2)) for c in fields(resp, 1)]]
    ok1 = got == [("ibc/ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789", "1234567"),
                  ("ulight", "1000000")]
    tr = enc_str_field(1, enc_str_field(1, "transfer/channel-0/uosmo") + enc_str_field(2, "uosmo"))
    ok2 = s(fields(tr, 1)[0], 1) == "transfer/channel-0/uosmo" and s(fields(tr, 1)[0], 2) == "uosmo"
    md = enc_str_field(1, enc_str_field(3, "uosmo") + enc_str_field(4, "osmo")
                       + enc_str_field(5, "Osmosis") + enc_str_field(6, "OSMO")
                       + enc_str_field(2, enc_str_field(1, "uosmo") + _varint((2 << 3) | 0) + _varint(0))
                       + enc_str_field(2, enc_str_field(1, "osmo") + _varint((2 << 3) | 0) + _varint(6)))
    mm = fields(md, 1)[0]
    ok3 = s(mm, 6) == "OSMO" and len(fields(mm, 2)) == 2
    h = humanize("ibc/x", "1234567", {"display": "osmo", "denom_units": [{"denom": "osmo", "exponent": 6}]})
    ok4 = h.get("display_amount") == "1.234567"
    hr = humanize("ulight", "1500000", None)
    ok5 = hr.get("display_amount") == "1.5" and hr.get("assumed") is False
    bad = summarize("http://127.0.0.1:1", "not-an-address")
    ok6 = bad.get("ok") is False
    # 本链 fork 的 Params 是两个 bool（CLI 打 true/true）；线形认错了会把"允许"读成"禁止"，必须测
    inner = _varint((1 << 3) | 0) + _varint(1) + _varint((2 << 3) | 0) + _varint(1)
    resp2 = enc_str_field(1, inner)
    p2 = decode(fields(resp2, 1)[0])
    ok7 = ([v for (n, wt, v) in p2 if n == 1 and wt == 0] == [1]
           and [v for (n, wt, v) in p2 if n == 2 and wt == 0] == [1])
    # 上游 SDK 的名单形：field1 是 DenomEnabled 消息，不能被当成 bool
    de = _varint((1 << 3) | 0) + _varint(0) + enc_str_field(2, "uatom")
    p3 = decode(enc_str_field(1, de))
    ok8 = ([wt for (n, wt, v) in p3 if n == 1] == [2])
    res = [("AllBalances 解码", ok1), ("DenomTrace 解码", ok2), ("Metadata 解码", ok3),
           ("外来面额按元数据换算", ok4), ("原生 6 位小数换算", ok5), ("坏地址被拒（不瞎返回）", ok6),
           ("本链 fork 的 bool 参数线形", ok7), ("上游名单线形不误判", ok8)]
    for n, v in res:
        print("  [%s] %s" % ("OK " if v else "坏", n))
    good = sum(1 for _, v in res if v)
    print("自检 %d/%d" % (good, len(res)))
    return 0 if good == len(res) else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    node = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:26657"
    addr = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(summarize(node, addr), ensure_ascii=False, indent=1))
