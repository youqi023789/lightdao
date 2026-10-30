#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gas_renew.py — 矿工代付授权（x/feegrant）到期续期与体检。

为什么需要它（实测，不是推测）：
  现有 gas_grant.py 用 granted.json 里 "ok" 标记做幂等：授予过一次就再也不授予。
  而它给的授权带 30 天过期（--expiration now+30d）与 5 LIGHT 消费上限。
  → 第 30 天之后，那些"自己没余额"的矿工（代付账户还给过他们 1000ulight 尘埃，
    但一笔领取要 75000ulight，根本不够）会安静地领不了，报
    "<granter> does not allow to pay fee"（sdk code 38=unauthorized）。
  2026-10-30 实测：25 个已授予矿工里 14 个授权已过期（最早 3 天前），
  其中 7 个自身余额不足以自付一笔 gas；金丝雀账号正卡在这里。

三种模式：
  默认        只打印将要续期的清单（不碰链）
  --apply     真的广播续期交易（每次 sleep 3s 避开同一签名者的 sequence 竞争）
  --check     给 cron 用的体检：有活跃矿工失去有效授权就非零退出 + 落告警
"""
import argparse, json, os, subprocess, sys, time
from datetime import datetime, timedelta, timezone

DATA = "/home/ubuntu/lightdao_gateway/data"
GRANTED = "/home/ubuntu/lightdao_gateway/granted.json"
DEP = "wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"
NODE = "tcp://127.0.0.1:26657"
HOME = "/home/ubuntu/.wasmd"
CHAIN = "lightdao-mainnet-1"
LIMIT = "5000000ulight"
DAYS = 30
ALERTS = "/home/ubuntu/ld_alerts.log"
STATE = os.environ.get("LD_GASRENEW_STATE", "/home/ubuntu/ld_gas_renew_state.json")
CLAIM_FEE_ULIGHT = 75000


def alert_line(msg):
    """告警统一出口：落盘失败必须喊出来（静默的告警=没有告警）。"""
    line = "%s %s" % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg)
    print(line)
    try:
        with open(ALERTS, "a") as f:
            f.write(line + "\n")
    except Exception as e:
        print("WARN 告警没落盘（%s）：%s" % (ALERTS, str(e)[:80]))


def sh(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def allowance(miner):
    """查链上真实授权。返回 (状态, 数据)：
         ("grant", {"expires":int|None,"remaining":int|None})  有授权
         ("none",  None)                                       链上明确说没有（含已过期被清理）
         ("error", 说明)                                       查不动/解析不了——绝不能当成"没有"
       上一版把查询子命令写成 allowance（正确的是 grant）且把"报错"和"没有"混成同一个 None，
       于是把 11 个仍有效的授权全报成"无授权"，差点据此去广播 27 笔续期。"""
    r = sh(["wasmd", "q", "feegrant", "grant", DEP, miner, "--node", NODE, "-o", "json"])
    out = (r.stdout or "") + (r.stderr or "")
    if "fee-grant not found" in out:
        return "none", None
    if r.returncode != 0 or not r.stdout.strip():
        return "error", (out.strip()[:120] or "空响应")
    try:
        d = json.loads(r.stdout)
    except Exception as e:
        return "error", "解析失败 " + str(e)[:60]
    gr = d.get("grant") or d.get("allowance") or {}
    raw = gr.get("allowance") or gr
    exp = raw.get("expiration")
    ts = None
    if exp:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                ts = int(datetime.strptime(exp, fmt).replace(tzinfo=timezone.utc).timestamp())
                break
            except Exception:
                pass
    lim = raw.get("spend_limit")
    rem = None
    if isinstance(lim, list) and lim:
        try:
            rem = int(lim[0].get("amount"))
        except Exception:
            rem = None
    return "grant", {"expires": ts, "remaining": rem}


def balance_ulight(addr):
    r = sh(["wasmd", "q", "bank", "balances", addr, "--node", NODE, "-o", "json"], 40)
    try:
        for b in json.loads(r.stdout).get("balances", []):
            if b["denom"] == "ulight":
                return int(b["amount"])
    except Exception:
        pass
    return 0


def active_miners(days_back):
    """最近 N 个赛季日文件里出现过的矿工（活跃集）。"""
    out = set()
    if not os.path.isdir(DATA):
        return out
    files = []
    for f in os.listdir(DATA):
        if f.startswith("day_") and f.endswith(".json"):
            try:
                files.append((int(f[4:-5]), f))
            except Exception:
                pass
    files.sort(reverse=True)
    for _, f in files[:days_back]:
        try:
            d = json.load(open(os.path.join(DATA, f)))
        except Exception:
            continue
        for m in (d.get("miners") or {}).keys():
            if m.startswith("wasm1") and len(m) > 20:
                out.add(m)
    return out


def grant_tx(miner):
    exp = (datetime.now(timezone.utc) + timedelta(days=DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = ["wasmd", "tx", "feegrant", "grant", DEP, miner,
           "--spend-limit", LIMIT, "--expiration", exp,
           "--from", "deployer", "--home", HOME, "--keyring-backend", "test",
           "--chain-id", CHAIN, "--node", NODE, "--gas", "200000",
           "--fees", "60000ulight", "-y", "-o", "json"]
    r = sh(cmd, 90)
    try:
        o = json.loads(r.stdout)
        return o.get("code") == 0, str(o.get("raw_log", ""))[:140], exp
    except Exception:
        return False, (r.stdout + r.stderr)[:140], exp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的广播续期（默认只打印）")
    ap.add_argument("--check", action="store_true", help="体检模式：有活跃矿工没有效授权就非零退出")
    ap.add_argument("--back", type=int, default=7, help="活跃集回看天数")
    ap.add_argument("--warn-days", type=int, default=7, help="距过期不足这么多天就续")
    a = ap.parse_args()
    now = int(time.time())
    g = {}
    try:
        g = json.load(open(GRANTED))
    except Exception:
        pass
    act = active_miners(a.back)
    # 只处理"被代付机制覆盖过"的矿工（在 granted.json 里），外加活跃且自身付不起 gas 的
    cands = sorted(set(g.keys()) | (act & {m for m in act if m.startswith("wasm1")}))
    plan, broken, unknown = [], [], []
    for m in cands:
        if m not in g and m not in act:
            continue
        st, al = allowance(m)
        if st == "error":
            unknown.append((m, al))
            continue
        exp = (al or {}).get("expires")
        missing = (st == "none")
        soon = bool(exp and exp - now < a.warn_days * 86400)
        expired = bool(exp and exp < now)
        if missing or soon:
            can_self = balance_ulight(m) >= CLAIM_FEE_ULIGHT
            row = (m, "无授权" if missing else ("已过期 %d 天" % ((now - exp) // 86400) if expired
                                              else "剩 %d 天" % ((exp - now) // 86400)),
                   "能自付" if can_self else "不能自付")
            (broken if (missing or expired) and not can_self else plan).append(row)
    print("活跃矿工集（近 %d 天）：%d 个；已授予记录：%d 条" % (a.back, len(act), len(g)))
    if unknown:
        print("注意：有 %d 个地址查不动授权，不当成『没有授权』处理（宁可漏续也不误发交易）：" % len(unknown))
        for m, why in unknown[:5]:
            print("   ", m[:24], why[:70])
    print("需要续期：%d；其中已失效且自己付不起 gas（=正在被卡住）：%d" % (len(plan) + len(broken), len(broken)))
    for m, why, selfpay in (broken + plan)[:40]:
        print("   %s %-16s %s" % (m[:24], why, selfpay))
    if a.check:
        # 体检模式只报警、不广播。同一批人反复报没意义（会被忽略或逼人关掉告警），
        # 所以按"被卡住的地址集合"去重：集合变了立刻报，集合没变每 24 小时补一条。
        key = ",".join(sorted(m for m, _w, _s in broken))
        st = {"ts": 0, "key": ""}
        try:
            st = json.load(open(STATE))
        except Exception:
            pass
        now2 = int(time.time())
        if not broken:
            if st.get("key"):
                alert_line("GAS-OK 矿工代付授权已恢复（上一批 %d 个）" % len(st["key"].split(",")))
                json.dump({"ts": now2, "key": ""}, open(STATE, "w"))
            print("CHECK OK 活跃矿工都有有效代付授权")
            sys.exit(0)
        if st.get("key") == key and now2 - int(st.get("ts", 0)) < 86400:
            print("CHECK 仍有 %d 个矿工被卡（同签名，%d 小时前已报）" % (len(broken), (now2 - int(st.get("ts", 0))) // 3600))
            sys.exit(1)
        msg = ("矿工代付授权失效且无法自付 gas：%d 个矿工领取会被拒（code 38："
               "\"<granter> does not allow to pay fee\"）。跑 gas_renew.py --apply 续期。"
               "地址：%s" % (len(broken), key[:200]))
        alert_line("GAS-RENEW " + msg)
        json.dump({"ts": now2, "key": key}, open(STATE, "w"))
        print("CHECK FAIL " + msg)
        sys.exit(1)
    if not a.apply:
        print("（未 --apply，一条链上交易都没发）")
        sys.exit(0)
    todo = plan + broken
    if not todo:
        print("没有要续期的"); sys.exit(0)
    done = 0
    for m, _why, _s in todo:
        ok, log, exp = grant_tx(m)
        print("  %s %s %s" % ("续期" if ok else "失败", m[:24], log[:70]))
        if ok:
            rec = g.get(m) or {}
            rec.update({"renew_ts": now, "renew_exp": exp, "day": rec.get("day"), "ok": True})
            g[m] = rec
            done += 1
            time.sleep(3)
        else:
            print("   FAIL 中断：不继续刷后续（避免半套状态）"); break
    json.dump(g, open(GRANTED, "w"), indent=1)
    print("完成 %d 个" % done)
    sys.exit(0 if done == len(todo) else 1)


main()
