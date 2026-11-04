#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-GOV-A3-FOLLOWUP-20261104  按所有者 2026-11-04 的明确指令：
"#12 通过后立即执行，并继续提交挖矿合约 code20 补 7 席"
把这条链条交给机器跑，不靠"我记得到时候去点一下"。

背景（都是链上实测）：
  · 提案 #12（治理合约自迁移 code 19 + 门槛 5,000 LIGHT）投票期
    2026-11-04 14:00:06Z → 2026-11-11 14:00:06Z（7 天，major 需 66% 且权重/地址数双维过）。
  · **这个治理合约不会自动执行**：exec() 里要有人调 ExecuteProposal；
    历史上 #11/#17 就是"过了/执行失败"之后一直挂着。
  · 挖矿合约→code 20 必须由治理合约（它是 mining_reward 的 admin）来迁，
    所以顺序只能是 ①先执行 #12 ②再 create+vote #13 ③到期执行 #13。

每小时跑一次，状态机幂等推进；每一步都：先核对链上前置状态，再动手，再回读验证，
成功/失败都写 ld_alerts.log（含提案号、交易哈希、实测 code_id/门槛）。
任何"前置不满足"一律不动手只报警——宁可不推进，也不能把主网状态推成猜的样子。
补第 6/7 席需要两把新钥匙的交付方式由所有者定，脚本到那一步只会报警求助，不自作主张生成保管物。
"""
import json, os, subprocess, sys, time

G = "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt"
MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
NODE = "tcp://127.0.0.1:26657"
STATE = os.environ.get("LD_A3_STATE") or "/home/ubuntu/ld_gov_a3_state.json"
ALERTS = os.environ.get("LD_A3_ALERTS") or "/home/ubuntu/ld_alerts.log"
DRY = "--dry" in sys.argv

P12 = 12
P12_END = 1794405606          # 2026-11-11T14:00:06Z（实测读出来的，不靠记忆）


def alert(msg):
    line = "%s GOV-A3 %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print("WARN 告警写不下去：%s" % e)


def run(args, timeout=120):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def q_json(args):
    r = run(args)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout)[:200]
    try:
        return json.loads(r.stdout), ""
    except Exception as e:
        return None, "json %s / %s" % (e, r.stdout[:120])


def smart(addr, msg):
    return q_json(["wasmd", "q", "wasm", "contract-state", "smart", addr, msg,
                   "--node", NODE, "-o", "json"])


def code_id(addr):
    d, err = q_json(["wasmd", "q", "wasm", "contract", addr, "--node", NODE, "-o", "json"])
    if d is None:
        return None, err
    ci = d.get("data") or d.get("contract_info") or {}
    return ci.get("code_id"), ""


def load():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"step": "wait12"}


def save(s):
    if DRY:
        print("(dry) 状态将是：%s" % json.dumps(s, ensure_ascii=False))
        return
    tmp = STATE + ".tmp"
    json.dump(s, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def execute_proposal(pid):
    msg = json.dumps({"execute_proposal": {"proposal_id": int(pid)}})
    if DRY:
        print("(dry) 将执行 ExecuteProposal(%s)" % pid)
        return None
    r = run(["wasmd", "tx", "wasm", "execute", G, msg, "--from", "deployer",
             "--keyring-backend", "test", "--home", "/home/ubuntu/.wasmd",
             "--chain-id", "lightdao-mainnet-1", "--node", NODE,
             "--gas", "1200000", "--fees", "400000ulight", "-y", "-b", "sync", "-o", "json"])
    try:
        d = json.loads(r.stdout)
    except Exception:
        return {"error": (r.stderr or r.stdout)[:200]}
    return d


def now():
    # 反向验证用的时间桩：正常不设；设了也只是"假装到了某个时刻"，不会绕过链上真实状态
    return int(os.environ.get("LD_A3_NOW") or time.time())


st = load()
print("当前状态=%s" % json.dumps(st, ensure_ascii=False)[:200])
if st.get("step") not in ("wait12", "done12", "proposed13", "done13"):
    alert("FAIL 状态文件里的 step=%r 不认识（可能被人为改坏或写坏），拒绝动作" % st.get("step"))
    raise SystemExit(1)

if st.get("step") == "wait12":
    d, err = smart(G, json.dumps({"proposal": {"id": P12}}))
    if d is None:
        alert("FAIL 读不到提案 #%s：%s（量具问题也算失败）" % (P12, err))
        raise SystemExit(1)
    p = d.get("data") or {}
    if p.get("executed"):
        cid, _ = code_id(G)
        st = {"step": "done12", "governance_code_id": cid}
        save(st)
        alert("OK 提案 #%s 已被执行（governance code_id=%s）" % (P12, cid))
    elif now() < int(p.get("end") or P12_END):
        print("未到投票结束时刻（还剩 %d 小时）" % ((int(p.get("end")) - now()) // 3600))
    else:
        t = p.get("yes_weight"), p.get("no_weight")
        cid_before, _ = code_id(G)
        res = execute_proposal(P12)
        if res is None:
            alert("DRY 演练：将执行 #%s（当前 yes=%s no=%s code_id=%s）" % (P12, t[0], t[1], cid_before))
            raise SystemExit(0)
        if res.get("code"):
            alert("FAIL 执行 #%s 被拒 code=%s log=%s" % (P12, res.get("code"), str(res.get("raw_log"))[:160]))
            raise SystemExit(1)
        h = res.get("txhash")
        time.sleep(8)
        cid, _ = code_id(G)
        cfg, _ = smart(G, '{"config":{}}')
        stake = ((cfg or {}).get("data") or {}).get("proposal_min_stake")
        if str(cid) == "19":
            st = {"step": "done12", "tx": h, "governance_code_id": cid, "proposal_min_stake": stake}
            save(st)
            alert("OK 提案 #%s 执行完成 tx=%s governance code_id=%s→19 门槛=%s ulight（=%s LIGHT）"
                  % (P12, h, cid_before, stake, int(stake or 0) // 10**6))
        else:
            alert("FAIL 执行交易已入块但 code_id=%s 不是 19，需人工看 tx=%s" % (cid, h))
            raise SystemExit(1)

if st.get("step") == "done12":
    d, err = smart(MR, '{"epoch_info":{}}')
    cid, _ = code_id(MR)
    print("mining_reward 当前 code_id=%s" % cid)
    if str(cid) == "20":
        st = dict(st); st["step"] = "done13"
        save(st)
        alert("OK 挖矿合约已在 code 20（可能已由别处执行）")
    else:
        # 建 #13：只带一个 target + 一个 migrate_code_id（合约结构决定无法打包两件事）
        inner = {"create_proposal": {
            "ptype": "major",
            "title": "A3b: migrate mining_reward to code 20 (updatable signer list)",
            "description": ("Migrate mining_reward to code_id 20 so the DAO can update the daily-root signer "
                            "list/threshold (WP designs 7 seats; chain currently has 5 active signers, "
                            "threshold 5 = zero redundancy)."),
            "symbol": None, "investment_usd": None,
            "target": MR, "migrate_code_id": 20, "call_msg": "e30=",   # base64("{}")：exec() 里 migrate 载荷取自 call_msg
        }}
        msg = json.dumps(inner)
        if DRY:
            alert("DRY 将创建提案 #13（mining_reward→code20）；payload=%s" % msg[:120])
        else:
            r = run(["wasmd", "tx", "wasm", "execute", G, msg, "--from", "deployer",
                     "--keyring-backend", "test", "--home", "/home/ubuntu/.wasmd",
                     "--chain-id", "lightdao-mainnet-1", "--node", NODE,
                     "--gas", "1200000", "--fees", "400000ulight", "-y", "-b", "sync", "-o", "json"])
            try:
                dd = json.loads(r.stdout)
            except Exception:
                alert("FAIL 创建 #13 无法解析返回：%s" % (r.stderr or r.stdout)[:180])
                raise SystemExit(1)
            if dd.get("code"):
                alert("FAIL 创建 #13 被拒 code=%s log=%s" % (dd.get("code"), str(dd.get("raw_log"))[:160]))
                raise SystemExit(1)
            time.sleep(8)
            cfg, _ = smart(G, '{"config":{}}')
            nid = ((cfg or {}).get("data") or {}).get("next_id")
            pid = int(nid) - 1 if nid else None
            v = run(["wasmd", "tx", "wasm", "execute", G,
                     json.dumps({"vote": {"proposal_id": pid, "option": "yes", "bet": "0"}}),
                     "--from", "deployer", "--keyring-backend", "test", "--home", "/home/ubuntu/.wasmd",
                     "--chain-id", "lightdao-mainnet-1", "--node", NODE,
                     "--gas", "400000", "--fees", "120000ulight", "-y", "-b", "sync", "-o", "json"])
            st = dict(st); st["step"] = "proposed13"; st["p13"] = pid
            save(st)
            alert("OK 已创建提案 #%s（mining→code20）tx=%s，并已用 deployer 投 yes（rc=%s）；"
                  "7 天后到期需再执行一次" % (pid, dd.get("txhash"), v.returncode))

if st.get("step") == "proposed13":
    pid = st.get("p13")
    d, err = smart(G, json.dumps({"proposal": {"id": pid}}))
    p = (d or {}).get("data") or {}
    if p.get("executed"):
        st = dict(st); st["step"] = "done13"
        save(st)
    elif now() >= int(p.get("end") or 0):
        res = execute_proposal(pid)
        cid, _ = code_id(MR)
        if str(cid) == "20":
            st = dict(st); st["step"] = "done13"
            save(st)
            alert("OK 提案 #%s 执行完成，mining_reward code_id=%s；"
                  "补第 6/7 席需要两把新钥匙与交付方式由所有者确定，脚本不擅自生成保管物" % (pid, cid))
        else:
            alert("FAIL 执行 #%s 后 mining code_id=%s 非 20，tx=%s" % (pid, cid, (res or {}).get("txhash")))
            raise SystemExit(1)
    else:
        print("#%s 未到投票结束（还剩 %d 小时）" % (pid, (int(p.get("end")) - now()) // 3600))

if st.get("step") == "done13":
    print("A3 链条已完成：门槛 5,000 + 挖矿合约可更新签名名单；下一步是补 7 席（需所有者定钥匙交付）")
