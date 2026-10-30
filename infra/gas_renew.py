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
# 探针地址：它有自己的余额（2,627,134 LIGHT），不该占用矿工代付额度
CANARY_PROBE = "wasm1ar9mg3ls3xw3ac44j29dvptnls0zgdhy8aghc3"


def save_state(ts, key):
    """状态写失败绝不能把已经做完的工作弄成"崩溃退出"：
       上一版这里直接 open(STATE,"w")，被 root 先建过同名文件的残留卡住
       （PermissionError），续期已经广播了 1 笔、工具却崩在最后一步。"""
    try:
        json.dump({"ts": ts, "key": key}, open(STATE, "w"))
    except Exception as e:
        print("WARN 状态写不了（%s）：%s —— 去重会失效，但已完成的工作不丢"
              % (STATE, str(e)[:80]))


def grant_alive(grantee):
    """链上是否还有有效授权（供外部核对用）。"""
    st, _ = allowance(grantee)
    return st == "grant"


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
    # 链上真实形状是 {"allowance":{"granter":...,"allowance":{"type":"cosmos-sdk/BasicAllowance",
    #   "value":{"spend_limit":[...],"expiration":"..."}}}} —— 到期时间藏在 value 里。
    # 之前只找 raw["expiration"]，于是永远解析成 None，把"30 天后到期"当成"永不过期"，
    # 到期前不会续，等于这个工具会在 30 天后重演今天这出。
    val = raw.get("value") or {}
    exp = None
    for cand in (val.get("expiration"), raw.get("expiration"), gr.get("expiration")):
        if cand:
            exp = cand
            break
    lim = val.get("spend_limit") or raw.get("spend_limit")
    ts = None
    if exp:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                ts = int(datetime.strptime(exp, fmt).replace(tzinfo=timezone.utc).timestamp())
                break
            except Exception:
                pass
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
        code = o.get("code")
        log = str(o.get("raw_log", ""))
        # 代付账户是共享签名者：网关 finalize、别的自动化也在用它，实测 sequence 两分钟内
        # 从 159 跳到 167。这类冲突是可重试的——重新签名会取到新 sequence。
        # 但重试间隔必须大于一个出块周期，否则又拿到同一个旧 sequence（第一版就是
        # 用 8s/12s + 一失败就中断整批，结果每跑一次只能修好一个）。
        for k in range(3):
            if code == 0 or "sequence mismatch" not in log:
                break
            time.sleep(12 + 10 * k)
            r = sh(cmd, 90)
            o = json.loads(r.stdout or "{}")
            code = o.get("code")
            log = str(o.get("raw_log", ""))
        return code == 0, log[:140], exp
    except Exception:
        return False, (r.stdout + r.stderr)[:140], exp


def classify(cands, now, warn_days, granted):
    """链上真值分类：(要续期的, 已失效且自己付不起=正在被卡住的, 查不动的)。
       三个列表共用一份逻辑，避免"体检说没事、续期时才发现有问题"两套判据不一致。"""
    plan, broken, unknown = [], [], []
    for m in cands:
        st, al = allowance(m)
        if st == "error":
            unknown.append((m, al))
            continue
        exp = (al or {}).get("expires")
        missing = (st == "none")
        soon = bool(exp and exp - now < warn_days * 86400)
        expired = bool(exp and exp < now)
        if missing or soon:
            can_self = balance_ulight(m) >= CLAIM_FEE_ULIGHT
            why = ("无授权" if missing else
                   ("已过期 %d 天" % ((now - exp) // 86400) if expired else "剩 %d 天" % ((exp - now) // 86400)))
            row = (m, why, "能自付" if can_self else "不能自付")
            (broken if (missing or expired) and not can_self else plan).append(row)
    return plan, broken, unknown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的广播续期（默认只打印）")
    ap.add_argument("--check", action="store_true", help="体检模式：有活跃矿工没有效授权就非零退出")
    ap.add_argument("--active-only", action="store_true",
                    help="只处理最近 --back 天内真的还在名单里的矿工（每日自动续期用这个，"
                         "不给已不活跃的地址无限续，避免被人当成长期补贴刷）")
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
    if a.active_only:
        # 每日自动续期只认"最近真的还在挖"的地址。
        cands = sorted(act & set(g.keys()))
        skipped = len(set(g.keys()) - act)
        print("活跃-only：近期活跃且在代付名单里的 %d 个；因不活跃跳过 %d 个"
              % (len(cands), skipped))
    else:
        cands = sorted(set(g.keys()) | (act & {m for m in act if m.startswith("wasm1")}))
    plan, broken, unknown = classify(cands, now, a.warn_days, g)
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
                save_state(now2, "")
            print("CHECK OK 活跃矿工都有有效代付授权")
            sys.exit(0)
        if st.get("key") == key and now2 - int(st.get("ts", 0)) < 86400:
            print("CHECK 仍有 %d 个矿工被卡（同签名，%d 小时前已报）" % (len(broken), (now2 - int(st.get("ts", 0))) // 3600))
            sys.exit(1)
        msg = ("矿工代付授权失效且无法自付 gas：%d 个矿工领取会被拒（code 38："
               "\"<granter> does not allow to pay fee\"）。跑 gas_renew.py --apply 续期。"
               "地址：%s" % (len(broken), key[:200]))
        alert_line("GAS-RENEW " + msg)
        save_state(now2, key)
        print("CHECK FAIL " + msg)
        sys.exit(1)
    if not a.apply:
        print("（未 --apply，一条链上交易都没发）")
        sys.exit(0)
    todo = [(m, w, s) for (m, w, s) in (plan + broken) if m != CANARY_PROBE]
    skipped_probe = len(plan + broken) - len(todo)
    if skipped_probe:
        # 金丝雀（探针）自己有钱付 gas，不该占代付额度；它现在走 selfpay 模式证明链路。
        print("跳过探针地址 %d 个（它自己付 gas，占代付额度没有意义）" % skipped_probe)
    if not todo:
        print("没有要续期的"); sys.exit(0)
    done = 0
    failed_soft = 0
    for m, _why, _s in todo:
        ok, log, exp = grant_tx(m)
        print("  %s %s %s" % ("续期" if ok else "失败", m[:24], log[:70]))
        if ok:
            rec = g.get(m) or {}
            rec.update({"renew_ts": now, "renew_exp": exp, "day": rec.get("day"), "ok": True})
            g[m] = rec
            done += 1
            time.sleep(8)      # 必须大于出块周期：上一版睡 3 秒，紧接着那笔就 sequence 撞车
            continue
        if "sequence mismatch" in log:
            # 共享签名者冲突：跳过这一个继续后面的，别把整批停掉
            # （每跑一次只修一个 = 白跑；实测 14 个跑两轮才修掉 9 个就是这么浪费的）。
            print("   跳过（sequence 冲突，下一轮再修）")
            failed_soft += 1
            time.sleep(6)
            continue
        print("   FAIL 非冲突类失败，中断不再刷后续（避免半套状态）")
        break
    json.dump(g, open(GRANTED, "w"), indent=1)
    print("完成 %d 个，因签名冲突跳过 %d 个" % (done, failed_soft))
    # 续完之后再用链上真值复查一遍：只报"仍然没解决"的，且按地址集合去重，
    # 免得变成每天重复刷屏（广播失败/授权被别处删掉都要能看见）。
    _pl2, br2, un2 = classify(cands, now, a.warn_days, g)
    # 只有"确实没有效授权"才报警；"查询异常"不是链上事实，把它算进告警集合会让
    # 每日任务永远红着（granted.json 里就有个当年测试留下的非法地址 wasm1endpointtest…）。
    leftover = [m for m, _w, _s in br2]
    if un2:
        print("提示：%d 个地址查不动授权（不报警，仅提示清理数据）：%s"
              % (len(un2), ", ".join(m[:24] for m, _r in un2[:3])))
    if leftover:
        key2 = ",".join(sorted(leftover))
        prev2 = {}
        try:
            prev2 = json.load(open(STATE))
        except Exception:
            pass
        if prev2.get("key") != key2 or now - int(prev2.get("ts", 0)) >= 86400:
            alert_line("GAS-RENEW-INCOMPLETE 续期后仍有 %d 个矿工没有有效代付授权（广播失败或查不动）：%s"
                       % (len(leftover), key2[:180]))
            save_state(now, key2)
        print("仍有 %d 个未解决" % len(leftover))
        sys.exit(1)
    try:
        if json.load(open(STATE)).get("key"):
            alert_line("GAS-OK 矿工代付授权已全部有效（续期完成 %d 个）" % done)
            save_state(now, "")
    except Exception:
        pass
    sys.exit(0 if done == len(todo) else 1)


if __name__ == "__main__":
    main()
