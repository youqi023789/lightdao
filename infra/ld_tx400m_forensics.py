#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
取证：1) 4 亿 LIGHT 转账的权威凭证（哈希/高度/时间/付款方/收款方/金额）
     2) 领取交易 A1D75008... 的链上真相 + 客户端"可领取"是怎么算出来的
只读操作，不发送任何交易。
"""
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

RPCS = ["http://127.0.0.1:26657", "http://127.0.0.1:26658",
        "http://localhost:26657", "http://127.0.0.1:36657"]

CLAIM_HASH = ("A1D75008E71D0F962BE67019A4C811687F0C35C8B51561AA54578EBF406691C7")
AMT = "400000000000000ulight"


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "ld-forensics"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pick_rpc():
    for x in RPCS:
        try:
            d = http_json(x + "/status", timeout=8)
            h = d["result"]["sync_info"]["latest_block_height"]
            print("[ok] RPC %s  最新高度=%s" % (x, h))
            return x
        except Exception as e:
            print("[no] RPC %s  %s: %s" % (x, type(e).__name__, str(e)[:90]))
    return None


def tx_search(rpc, query, per=100):
    url = (rpc + "/tx_search?query=%s&page=1&per_page=%d&order_by=asc"
           % (urllib.parse.quote(query, safe=""), per))
    d = http_json(url, timeout=40)
    res = d.get("result") or {}
    return res.get("txs") or [], res.get("total_count") or res.get("total")


def events_of(item):
    r = (item.get("tx_result") or item.get("result")
         or item.get("deliver_tx") or {})
    ev = r.get("events") or []
    out = []
    for e in ev:
        attrs = e.get("attributes") or e.get("attributes_json") or []
        d = {}
        for a in attrs:
            if isinstance(a, dict):
                k = a.get("key")
                v = a.get("value")
                d[k] = v
        out.append((e.get("type"), d))
    return out, r


def find_wasmd():
    w = shutil.which("wasmd")
    if w:
        return w
    for p in ["/usr/local/bin/wasmd", "/usr/bin/wasmd",
              "/home/ubuntu/go/bin/wasmd", "/opt/wasmd/wasmd"]:
        if os.path.exists(p):
            return p
    return None


def wasmd_tx(wasmd, rpc, h):
    for hh in ("0x" + h, h):
        try:
            p = subprocess.run([wasmd, "q", "tx", hh, "--node", rpc,
                                "-o", "json"],
                               capture_output=True, timeout=40)
            out = (p.stdout.decode("utf-8", "replace")
                   + p.stderr.decode("utf-8", "replace"))
            i = out.find("{")
            if i >= 0:
                return json.loads(out[i:])
        except Exception:
            continue
    return None


def main():
    rpc = pick_rpc()
    if not rpc:
        print("FATAL: 本机无可用的 CometBFT RPC 端口")
        return
    wasmd = find_wasmd()
    print("wasmd =", wasmd or "(未找到，只能看事件)")

    # ---------- A. 4 亿转账 ----------
    print("\n=== A. 4 亿 LIGHT 转账取证 ===")
    hits = []
    for q in ["transfer.amount='%s'" % AMT,
              "tx.height>=366100 AND tx.height<=366500"]:
        try:
            txs, total = tx_search(rpc, q)
        except urllib.error.HTTPError as e:
            print("[查询失败] %s -> HTTP %s" % (q, e.code))
            continue
        except Exception as e:
            print("[查询失败] %s -> %s: %s" % (q, type(e).__name__, str(e)[:90]))
            continue
        print("[查询] %-52s 命中 %s 笔 (total=%s)" % (q[:52], len(txs), total))
        for t in txs:
            ev, r = events_of(t)
            for typ, d in ev:
                if d.get("amount") == AMT:
                    hits.append((t, typ, d, r))
        if hits:
            break

    if not hits:
        print("!! 没有找到该金额的 transfer 事件，请把下面的高度扫描结果贴回来")
    seen = set()
    for t, typ, d, r in hits:
        h = t.get("height")
        hh = t.get("hash")
        key = (hh, d.get("sender"), d.get("recipient"))
        if key in seen:
            continue
        seen.add(key)
        bt = "?"
        try:
            b = http_json(rpc + "/block?height=%s" % h, timeout=20)
            bt = b["result"]["block"]["header"]["time"]
        except Exception as e:
            bt = "取块失败:%s" % type(e).__name__
        code = r.get("code", 0)
        print("\n- 哈希        %s" % hh)
        print("  高度        %s   区块时间(UTC) %s" % (h, bt))
        print("  事件        %s  sender=%s" % (typ, d.get("sender")))
        print("  recipient   %s" % d.get("recipient"))
        print("  amount      %s" % d.get("amount"))
        print("  码值        %s  log=%s" % (code, str(r.get("log"))[:160]))
        # 其它相关属性
        for typ2, d2 in events_of(t)[0]:
            if typ2 in ("execute", "wasm", "message", "transfer"):
                keep = {k: v for k, v in d2.items()
                        if k in ("_contract_address", "contract_address",
                                 "action", "method", "owner", "sender",
                                 "recipient", "amount", "mode", "proposal_id",
                                 "id", "new_owner")}
                if keep:
                    print("    %s %s" % (typ2, json.dumps(keep, ensure_ascii=False)))
        if wasmd:
            tj = wasmd_tx(wasmd, rpc, hh)
            if tj:
                print("  --- 解码后的消息 ---")
                print("  tx 签名者 %s" % (tj.get("auth_info", {})
                                          .get("signer_infos", [{}])[0]
                                          .get("pub_key", {}).get("key", "")[:24]))
                for m in (tj.get("tx", {}).get("body", {})
                          .get("messages") or []):
                    s = json.dumps(m, ensure_ascii=False)
                    print("   msg:", s[:600])
                print("  raw_log:", str(tj.get("raw_log"))[:300])

    # 双边余额
    addrs = []
    for _, _, d, _ in hits:
        for k in ("sender", "recipient"):
            if d.get(k) and d[k] not in addrs:
                addrs.append(d[k])
    if addrs and wasmd:
        print("\n=== 相关账户当前余额 (ulight) ===")
        for a in addrs:
            try:
                p = subprocess.run([wasmd, "q", "bank", "balances", a,
                                    "--denom", "ulight", "--node", rpc,
                                    "-o", "json"],
                                   capture_output=True, timeout=30)
                out = p.stdout.decode("utf-8", "replace")
                i = out.find("{")
                j = json.loads(out[i:]) if i >= 0 else {}
                print("  %-64s %s" % (a, j.get("balance", {}).get("amount")))
            except Exception as e:
                print("  %s 查询失败 %s" % (a, type(e).__name__))

    # ---------- B. 那笔"已领取"的失败交易 ----------
    print("\n=== B. 领取交易 %s... ===" % CLAIM_HASH[:16])
    if wasmd:
        tj = wasmd_tx(wasmd, rpc, CLAIM_HASH)
        if not tj:
            print("  wasmd q tx 失败，改用 RPC")
        else:
            print("  高度=%s  码值=%s  %s" % (tj.get("height"),
                                              tj.get("code"),
                                              str(tj.get("raw_log"))[:300]))
            for m in (tj.get("tx", {}).get("body", {})
                      .get("messages") or []):
                print("   msg:", json.dumps(m, ensure_ascii=False)[:700])
    try:
        txs, total = tx_search(rpc, "tx.hash='%s'" % CLAIM_HASH)
        print("  RPC tx.hash 查询命中 %s (total=%s)" % (len(txs), total))
    except Exception as e:
        print("  RPC tx.hash 查询失败 %s" % type(e).__name__)

    # 该地址历史上成功领取过几次
    if rpc:
        for q in ["message.sender='wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v'"]:
            try:
                txs, total = tx_search(rpc, q, per=100)
                print("\n  该地址发起的交易: 命中 %s (total=%s)" % (len(txs), total))
                n = 0
                for t in txs:
                    ev, r = events_of(t)
                    acts = [d.get("action") for _, d in ev if d.get("action")]
                    if any(a and "claim" in str(a).lower() for a in acts):
                        n += 1
                        if n <= 12:
                            print("   高度 %s 哈希 %s action=%s code=%s"
                                  % (t.get("height"), str(t.get("hash"))[:16],
                                     ",".join(map(str, acts))[:40],
                                     r.get("code", 0)))
                print("   含 claim 动作的交易共 %d 笔" % n)
            except Exception as e:
                print("  查询失败 %s: %s" % (type(e).__name__, str(e)[:120]))

    # ---------- C. 客户端"可领取"是怎么算的 ----------
    print("\n=== C. 客户端 claimable 相关代码 ===")
    jsdir = "/var/www/lightdao/js"
    if os.path.isdir(jsdir):
        for f in sorted(os.listdir(jsdir)):
            if not f.endswith(".js"):
                continue
            path = os.path.join(jsdir, f)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except Exception:
                continue
            for i, ln in enumerate(lines, 1):
                low = ln.lower()
                if ("claim" in low and
                        any(k in low for k in ("claimable", "already",
                                               "claimed", "pending",
                                               "available"))):
                    print("  %s:%d: %s" % (f, i, ln.strip()[:190]))
    else:
        print("  (本机没有 %s)" % jsdir)

    print("\nDONE")


main()
