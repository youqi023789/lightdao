#!/usr/bin/env python3
"""
LightDAO Scoring Gateway (MVP) — 资深后端工程师实现, 仅用 Python 标准库, 零依赖.
职责: 收集轻节点贡献心跳 -> 按确定性规则打分(0..1e6/维) -> 构建与 mining_reward 合约
字节级一致的每日 Merkle 树 -> 对外提供 root + 每矿工 proof, 供验证者提交根、矿工领取.

合约叶子格式(必须严格一致):
  leaf = sha256( miner_bech32_bytes || day_le_u64 || bw_le_u128 || se_le_u128 || ve_le_u128 || st_le_u128 )
  内部节点 = sha256(left32 || right32); proof 元素 = 'L'+sib_hex(兄在左) 或 'R'+sib_hex(兄在右)
  reward = daily_pool(day) * weighted_score(miner) / total_score(day)
  weighted_score = (bw*40 + se*30 + ve*20 + st*10) / 100
"""
import json, os, sys, hashlib, struct, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA       = os.environ.get("GW_DATA", os.path.expanduser("~/lightdao_gateway/data"))
PORT       = int(os.environ.get("GW_PORT", "8080"))
ADMIN      = os.environ.get("GW_ADMIN_SECRET", "change-me-in-prod")
GENESIS    = int(os.environ.get("GW_GENESIS", "0"))   # 链上 mining_reward 的 genesis_time(秒), 用于对齐 day
DAY_SECS   = 86400
SCALE      = 1_000_000
WEIGHTS    = {"bandwidth": 40, "session": 30, "verification": 20, "stability": 10}
REFERRAL_BONUS = 0.10   # S1: 邀请人得被邀人首周加权分10%
REFERRAL_WINDOW = 7     # 首周天数
# MVP 评分目标(达到即满分 1e6); 真实贡献度量, 可配置
TARGETS    = {"bandwidth_kbps": 10_000, "session_secs": 3_600, "verification_tasks": 100, "stability_pct": 100}

os.makedirs(DATA, exist_ok=True)
LOCK = threading.Lock()

# ---- per-IP rate limiting ----
import time as _time
_RATE = {}
_RATE_LIM = {"heartbeat": int(os.environ.get("GW_RATE_HB", 60)), "get": int(os.environ.get("GW_RATE_GET", 300)), "post": int(os.environ.get("GW_RATE_POST", 120))}   # per minute per IP
def _rate_ok(ip, kind):
    now = _time.time()
    lim = _RATE_LIM.get(kind, 600)
    e = _RATE.setdefault(ip, {})
    w = e.get(kind)
    if not w or (now - w[1]) > 60:
        e[kind] = [1, now]
        return True
    w[0] += 1
    return w[0] <= lim

# ---------- Merkle (与合约严格一致) ----------
def leaf_hash(miner: str, day: int, bw: int, se: int, ve: int, st: int) -> bytes:
    pre = miner.encode() + day.to_bytes(8, "little") \
        + bw.to_bytes(16, "little") + se.to_bytes(16, "little") \
        + ve.to_bytes(16, "little") + st.to_bytes(16, "little")
    return hashlib.sha256(pre).digest()

def build_tree(leaves):
    """返回 (root_bytes, levels); 奇数复制末节点."""
    if not leaves:
        return None, []
    level = list(leaves); levels = [level]
    while len(level) > 1:
        if len(level) % 2: level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i+1]).digest() for i in range(0, len(level), 2)]
        levels.append(level)
    return levels[-1][0], levels

def proof_for(levels, index):
    proof = []; idx = index
    for level in levels[:-1]:
        if idx % 2 == 0:
            sib = idx + 1
            if sib >= len(level): sib = idx          # 复制的末节点
            proof.append("R" + level[sib].hex())     # 兄在右
        else:
            proof.append("L" + level[idx - 1].hex()) # 兄在左
        idx //= 2
    return proof

def contract_verify(miner, day, score, proof, root_hex) -> bool:
    """精确复刻合约 merkle_verify, 用于自检."""
    cur = leaf_hash(miner, day, score["bandwidth"], score["session"], score["verification"], score["stability"]).hex()
    for elem in proof:
        d, sib = elem[0], elem[1:]
        combined = (sib + cur) if d == "L" else (cur + sib)
        cur = hashlib.sha256(bytes.fromhex(combined)).hexdigest()
    return cur.lower() == root_hex.lower()

# ---------- 评分 ----------
def weighted_score(s):
    return (s["bandwidth"]*WEIGHTS["bandwidth"] + s["session"]*WEIGHTS["session"]
          + s["verification"]*WEIGHTS["verification"] + s["stability"]*WEIGHTS["stability"]) // 100

def norm(metric, value):
    return min(int(value), TARGETS[metric]) * SCALE // TARGETS[metric]

def score_miner(m):
    return {
        "bandwidth":    norm("bandwidth_kbps",    m.get("bandwidth_kbps", 0)),
        "session":      norm("session_secs",      m.get("session_secs", 0)),
        "verification": norm("verification_tasks",m.get("verification_tasks", 0)),
        "stability":    norm("stability_pct",     m.get("stability_pct", 0)),
    }

# ---------- 存储 ----------
def day_path(day): return os.path.join(DATA, f"day_{day}.json")
def load_day(day):
    p = day_path(day)
    if os.path.exists(p):
        with open(p) as f: return json.load(f)
    return {"day": day, "miners": {}, "finalized": False}
def save_day(d):
    with open(day_path(d["day"]), "w") as f: json.dump(d, f)
CUTOVER = int(os.environ.get("GW_DAY_CUTOVER", "1790726400"))  # 2026-09-30 00:00:00 UTC; 之后日界=00:00UTC
D_CUT = (CUTOVER - GENESIS - 1) // DAY_SECS + 1   # 截断的旧天保留其索引;首个00:00对齐天=+1,防索引碰撞
def current_day():
    now = int(time.time())
    if now < CUTOVER: return (now - GENESIS) // DAY_SECS
    return D_CUT + (now - CUTOVER) // DAY_SECS
def next_boundary_ts():
    now = int(time.time())
    if now < CUTOVER:
        nb = ((now - GENESIS) // DAY_SECS + 1) * DAY_SECS + GENESIS
        return min(nb, CUTOVER)
    return CUTOVER + ((now - CUTOVER) // DAY_SECS + 1) * DAY_SECS

def finalize_day(day):
    with LOCK:
        d = load_day(day)
        if not d["miners"]:
            return {"error": "no miners for day"}
        addrs = sorted(d["miners"].keys())           # 确定性排序
        # 每日根=纯PoC分(不折邀请奖励);邀请+10%在赛季末从S1池结算(见 referrals 记录)
        scores = {a: score_miner(d["miners"][a]) for a in addrs}
        # 反女巫(§4.8):同设备指纹当日只计最高分一个钱包,其余清零;同IP>3不同指纹=标记信号
        ZERO = {"bandwidth":0,"session":0,"verification":0,"stability":0}
        fps = d.get("fps", {}); ips = d.get("ips", {})
        byfp = {}
        for m in addrs:
            fp = fps.get(m)
            if fp: byfp.setdefault(fp, []).append(m)
        flagged = []
        for fp, ms in byfp.items():
            if len(ms) > 1:
                ms.sort(key=lambda m: weighted_score(scores[m]), reverse=True)
                for m in ms[1:]:
                    scores[m] = dict(ZERO); flagged.append(m)
        byip = {}
        for m in addrs:
            ip = ips.get(m)
            if ip: byip.setdefault(ip, set()).add(fps.get(m) or m)
        for ip, fset in byip.items():
            if len(fset) > 3:
                flagged += [m for m in addrs if ips.get(m)==ip]
        d["flagged"] = sorted(set(flagged))
        # BEHAVIOR BOOST (WP 985): 4 behaviors x 5%, cap 20%, applied to bw/se/ve dims
        bhs = d.get("behaviors") or {}
        for aa in list(scores.keys()):
            fl = bhs.get(aa) or {}
            cnt = sum(1 for k in ("pwa", "delegated", "social", "quiz") if fl.get(k))
            if cnt:
                f = 1.0 + 0.05 * min(cnt, 4)
                sc = scores[aa]
                sc["bandwidth"] = int(sc.get("bandwidth", 0) * f)
                sc["session"] = int(sc.get("session", 0) * f)
                sc["verification"] = int(sc.get("verification", 0) * f)
                # WP 338: PWA install => +10% session dim
                if fl.get("pwa"):
                    sc["session"] = int(sc.get("session", 0) * 1.1)  # pwa_session_bonus

        # DELEG SPLIT (whitepaper mobile-adaptation): delegator keeps 70% session, relay node gets 30%
        delegs = d.get("delegations") or {}
        for m, D in list(delegs.items()):
            if m not in scores or not D or D == m: continue
            mv = scores[m].get("session", 0) * 0.3
            scores[m]["session"] = scores[m].get("session", 0) - mv
            if D not in scores:
                scores[D] = {"bandwidth": 0, "session": 0, "verification": 0, "stability": 100}
                addrs = sorted(set(addrs) | {D})
            scores[D]["session"] = scores[D].get("session", 0) + mv
        leaves = [leaf_hash(a, day, scores[a]["bandwidth"], scores[a]["session"], scores[a]["verification"], scores[a]["stability"]) for a in addrs]
        root, levels = build_tree(leaves)
        proofs = {a: proof_for(levels, i) for i, a in enumerate(addrs)}
        total_score = sum(weighted_score(scores[a]) for a in addrs)
        # ---- airdrop ledger (WP 5.7): first day with >=4h valid session => 50 LIGHT ----
        try:
            LP = os.path.join(os.path.dirname(day_path(day)), "..", "airdrops.json")
            LP = os.path.normpath(LP)
            led = json.load(open(LP)) if os.path.exists(LP) else {}
            for aa in addrs:
                ss = (d["miners"].get(aa) or {}).get("session_secs", 0) or 0
                if ss >= 14400 and aa not in led:
                    led[aa] = {"type": "first_mine_4h", "amount_light": 50, "day": day}
            # referral tiers (WP 985): 3/10/50 -> 100/500/2500 LIGHT
            ref_tot = {}
            for fn2 in os.listdir(os.path.dirname(day_path(day))):
                if not fn2.startswith("day_") or not fn2.endswith(".json"): continue
                try: d2 = json.load(open(os.path.join(os.path.dirname(day_path(day)), fn2)))
                except Exception: continue
                for mm, rr in (d2.get("referrals") or {}).items():
                    rf = (rr or {}).get("referrer")
                    if rf: ref_tot[rf] = ref_tot.get(rf, 0) + 1
            for rf, cnt in ref_tot.items():
                for thr, amt in ((3, 100), (10, 500), (50, 2500)):
                    key = rf + "#tier%d" % thr
                    if cnt >= thr and key not in led:
                        led[key] = {"type": "referral_tier", "tier": thr, "amount_light": amt, "day": day, "addr": rf}
            # learn-to-earn 30L + first-vote 20L (first day flag true)
            for aa in addrs:
                fl = (d.get("behaviors") or {}).get(aa) or {}
                if fl.get("quiz") and (aa + "#quiz") not in led:
                    led[aa + "#quiz"] = {"type": "learn_to_earn", "amount_light": 30, "day": day, "addr": aa}
                if fl.get("voted") and (aa + "#vote") not in led:
                    ld2 = led
                    ld2[aa + "#vote"] = {"type": "first_vote", "amount_light": 20, "day": day, "addr": aa}
            json.dump(led, open(LP, "w"))
        except Exception as _e:
            pass
        d.update({"finalized": True, "root": root.hex(), "active_miners": len(addrs),
                  "total_score": total_score, "scores": scores, "proofs": proofs})
        save_day(d)
        return {"day": day, "root": d["root"], "active_miners": d["active_miners"], "total_score": total_score}

# ---------- HTTP ----------
class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*"); self.send_header("Access-Control-Allow-Methods", "*"); self.end_headers()
    def do_GET(self):
        if not _rate_ok(self.client_address[0], "get"): return self._send(429, {"error": "rate limited"})
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/v1/health": return self._send(200, {"ok": True, "current_day": current_day(), "next_boundary_ts": next_boundary_ts()})
        if u.path == "/v1/probe":
            blob = b"\0" * (256 * 1024)   # 256KB 下载探测, 供客户端实测带宽
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(blob))); self.end_headers()
            try: self.wfile.write(blob)
            except Exception: pass
            return
        if u.path == "/v1/day":
            day = int(q.get("day", [current_day()-1])[0]); d = load_day(day)
            return self._send(200, {"day": day, "finalized": d.get("finalized"), "root": d.get("root"),
                                    "active_miners": d.get("active_miners"), "total_score": d.get("total_score")})
        if u.path == "/v1/proof":
            day = int(q["day"][0]); miner = q["miner"][0]; d = load_day(day)
            if not d.get("finalized") or miner not in d.get("proofs", {}):
                return self._send(404, {"error": "no proof"})
            return self._send(200, {"day": day, "miner": miner, "proof": d["proofs"][miner],
                                    "score": d["scores"][miner], "root": d["root"]})
        if u.path == "/v1/scores":
            day = int((q.get("day") or [current_day()])[0])
            d = load_day(day)
            ms = d.get("miners") or {}
            out = {}; tot = 0
            fin = bool(d.get("finalized")) and bool(d.get("scores"))
            for a, m in ms.items():
                dims = d["scores"].get(a) if fin else score_miner(m)
                w = weighted_score(dims or {})
                out[a] = {"w": w}
                tot += w
            if fin:
                tot = d.get("total_score") or tot
            return self._send(200, {"day": day, "total": tot, "scores": out, "finalized": bool(d.get("finalized"))})
        if u.path == "/v1/me":
            addr = (q.get("addr") or [""])[0]
            out = {"addr": addr, "days": {}}
            for fn in sorted(os.listdir(DATA)):
                if not fn.startswith("day_") or not fn.endswith(".json"): continue
                try: d = json.load(open(os.path.join(DATA, fn)))
                except Exception: continue
                dd = d.get("day"); m = (d.get("miners") or {}).get(addr)
                rec = {"day": dd, "active": bool(m), "finalized": bool(d.get("finalized"))}
                if m: rec["score"] = m
                fps = d.get("fps") or {}
                if addr in fps: rec["fp"] = fps[addr][:12]
                if addr in fps:
                    rec["fp_peers"] = [x for x in fps if fps[x] == fps[addr] and x != addr]
                # flagged if my score zeroed while sharing fp with another miner (dedupe)
                if m and fps.get(addr):
                    same = [a for a, f2 in fps.items() if f2 == fps[addr] and a != addr]
                    rec["fp_shared_with"] = len(same)
                    rec["flagged"] = bool(same) and all((m.get(k, 0) or 0) == 0 for k in ("bandwidth", "session", "verification"))
                refs = d.get("referrals") or {}
                rec["referred"] = sum(1 for k, v in refs.items() if (v or {}).get("referrer") == addr)
                if addr in refs: rec["referrer"] = refs[addr].get("referrer")
                out["days"][dd] = rec
            days = out.get("days") or {}
            act = [dd for dd, r in days.items() if r.get("active")]
            actn = sorted(int(x) for x in act)
            streak = 0
            for k in range(len(actn)):
                if k == 0 or actn[k] == actn[k-1] + 1: streak += 1
                else: streak = 1
            out["first_day"] = actn[0] if actn else None
            out["active_days"] = len(actn)
            out["streak"] = streak
            out["referred_total"] = sum((r.get("referred") or 0) for r in days.values())
            try:
                LP = os.path.normpath(os.path.join(DATA, "..", "airdrops.json"))
                led = json.load(open(LP)) if os.path.exists(LP) else {}
                out["airdrop_first_mine"] = led.get(addr)
            except Exception:
                out["airdrop_first_mine"] = None
            maxs = max([((r.get("score") or {}).get("session_secs") or 0) for r in days.values()] or [0])
            out["best_day_session_secs"] = maxs
            out["behaviors"] = (days.get(str(day)) or {}).get("behaviors") if False else None
            bl = None
            for dd in sorted(days.keys(), key=lambda x: int(x)):
                pass
            out["airdrop_list"] = []
            try:
                LP2 = os.path.normpath(os.path.join(DATA, "..", "airdrops.json"))
                led2 = json.load(open(LP2)) if os.path.exists(LP2) else {}
                for k, v in led2.items():
                    if v.get("addr") == addr or k == addr:
                        out["airdrop_list"].append(v)
            except Exception:
                pass
            bb = None
            for dd in sorted(days.keys(), key=lambda x: int(x), reverse=True):
                rec = days[dd]
                if rec.get("active"):
                    try:
                        d3 = json.load(open(os.path.join(DATA, "day_%s.json" % dd)))
                        bb = (d3.get("behaviors") or {}).get(addr)
                    except Exception:
                        bb = None
                    if bb: break
            out["behaviors"] = bb or {}
            return self._send(200, out)
        return self._send(404, {"error": "not found"})
    def do_POST(self):
        _u = urlparse(self.path)
        if not _rate_ok(self.client_address[0], "heartbeat" if _u.path == "/v1/heartbeat" else "post"): return self._send(429, {"error": "rate limited"})
        u = urlparse(self.path); n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if u.path == "/v1/heartbeat":
            miner = body.get("miner"); 
            if not miner or not miner.startswith("wasm1"): return self._send(400, {"error": "bad miner"})
            day = int(body.get("day", current_day()))
            with LOCK:
                d = load_day(day)
                if d.get("finalized"): return self._send(409, {"error": "day finalized"})
                d["miners"][miner] = {k: body.get(k, 0) for k in TARGETS}  # 客户端报当日累计
                fp = (body.get("fp") or "")[:64]
                ip = (self.headers.get("X-Forwarded-For") or self.client_address[0] or "").split(",")[0].strip()
                d.setdefault("fps", {})[miner] = fp
                d.setdefault("ips", {})[miner] = ip
                ref = body.get("referrer")
                bh = body.get("behaviors") or {}
                if isinstance(bh, dict):
                    d.setdefault("behaviors", {})[miner] = {k: bool(bh.get(k)) for k in ("pwa", "delegated", "social", "quiz", "voted") if k in bh}
                dlg = body.get("delegate_to")
                if dlg and dlg.startswith("wasm1") and dlg != miner:
                    d.setdefault("delegations", {})[miner] = dlg
                if ref and ref.startswith("wasm1") and ref != miner:
                    d.setdefault("referrals", {})
                    if miner not in d["referrals"]:
                        d["referrals"][miner] = {"referrer": ref, "first_day": day}
                save_day(d)
            return self._send(200, {"ok": True, "day": day})
        if u.path == "/v1/clienterr":
            try:
                ip = (self.headers.get("X-Forwarded-For") or self.client_address[0] or "").split(",")[0].strip()
                ua = (self.headers.get("User-Agent") or "")[:300]
                with open("/home/ubuntu/lightdao_gateway/clienterr.log", "a") as lf:
                    lf.write(json.dumps({"ts": int(time.time()), "ip": ip, "ua": ua, "body": body}) + "\n")
            except Exception:
                pass
            return self._send(200, {"ok": True})
        if u.path == "/v1/finalize":
            if self.headers.get("X-Admin") != ADMIN: return self._send(403, {"error": "forbidden"})
            day = int(body.get("day", current_day()-1))
            _dd = load_day(day)
            if _dd.get("finalized"): return self._send(200, {"already": True, "day": day, "root": _dd.get("root")})
            return self._send(200, finalize_day(day))
        return self._send(404, {"error": "not found"})

# ---------- 自检: 证明与合约字节级兼容 ----------
def selftest():
    print("== selftest: Merkle 与合约兼容性 ==")
    # 1) 已知: flowA 中 miner1/day0/全1e6 的根曾在主网成功领取
    m = "wasm1vsvuc5nyyav33zhs2sfgw44dxhc32x9y0axxjt"
    known_root = "f937d14237881d2905becb2351e4403b8855b1f861bf33908a4784012c109ada"
    s = {"bandwidth": SCALE, "session": SCALE, "verification": SCALE, "stability": SCALE}
    single = leaf_hash(m, 0, s["bandwidth"], s["session"], s["verification"], s["stability"]).hex()
    ok1 = single == known_root
    print(f"  单叶根匹配主网已验证根: {ok1} ({single[:16]}...)")
    # 2) 多矿工树 + 证明, 用合约算法逐一验证
    miners = [f"wasm1test{i:02d}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" for i in range(5)]
    scores = {mm: {"bandwidth": SCALE, "session": (i+1)*SCALE//5, "verification": SCALE//2, "stability": SCALE} for i, mm in enumerate(miners)}
    leaves = [leaf_hash(mm, 7, scores[mm]["bandwidth"], scores[mm]["session"], scores[mm]["verification"], scores[mm]["stability"]) for mm in miners]
    root, levels = build_tree(leaves)
    ok2 = True
    for i, mm in enumerate(miners):
        pf = proof_for(levels, i)
        if not contract_verify(mm, 7, scores[mm], pf, root.hex()): ok2 = False; print(f"  proof FAIL {mm}")
    print(f"  5矿工树+证明经合约算法验证: {ok2} (root={root.hex()[:16]}...)")
    # 3) 加权分与奖励比例
    w = weighted_score(s); print(f"  满分加权分={w} (应=1e6): {w==SCALE}")
    print(f"  total_score(5矿工)={sum(weighted_score(scores[mm]) for mm in miners)}")
    print("SELFTEST_PASS" if (ok1 and ok2 and w == SCALE) else "SELFTEST_FAIL")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest(); sys.exit(0)
    print(f"LightDAO gateway listening :{PORT} data={DATA} genesis={GENESIS}")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
