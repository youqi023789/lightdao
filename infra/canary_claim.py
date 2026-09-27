#!/usr/bin/env python3
"""Canary miner: server-controlled wallet heartbeats daily; after finalize+sign it claims via CLI
and asserts balance increase. Failure => ld_alerts.log + Discord broadcast. Proves the whole
settle->sign->proof->claim->payout pipeline daily, before any real user can hit a break."""
import json, os, subprocess, sys, time, urllib.request

# cron PATH is minimal (/usr/bin:/bin); use absolute binaries.
os.environ["PATH"] = "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")
WASMD = "/usr/local/bin/wasmd"

NODE = "tcp://127.0.0.1:26657"
HOME = "/home/ubuntu/.wasmd"
KB = ["--home", HOME, "--keyring-backend", "test", "--chain-id", "lightdao-mainnet-1", "--node", NODE]
MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"   # mining_reward (verified label on-chain)
DEP = "wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"                        # deployer / fee granter
GW = "http://127.0.0.1:8080"
FP = "canary-fp-0001"
# Stable canary wallet (key lives in server keyring-test). Beat mode needs only this address.
CANARY_ADDR = "wasm1ar9mg3ls3xw3ac44j29dvptnls0zgdhy8aghc3"

def sh(c, timeout=90):
    try:
        r = subprocess.run(c, shell=isinstance(c, str), capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return "ERR:%s" % e, 99

def alert(msg):
    try:
        with open("/home/ubuntu/ld_alerts.log", "a") as f:
            f.write("%s CANARY %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))
    except Exception:
        pass
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "⚠️ CANARY: " + msg], timeout=30)
    except Exception:
        pass

def canary_addr():
    # Prefer the keyring (authoritative); fall back to the known constant.
    out, rc = sh([WASMD, "keys", "show", "canary", "-a", "--home", HOME, "--keyring-backend", "test"])
    if rc == 0 and out.startswith("wasm1"):
        return out.strip()
    return CANARY_ADDR

def heartbeat(addr, day_sess):
    body = json.dumps({"miner": addr, "bandwidth_kbps": 3000, "session_secs": day_sess,
                       "verification_tasks": 20, "stability_pct": 100, "fp": FP,
                       "behaviors": {"pwa": True}}).encode()
    req = urllib.request.Request(GW + "/v1/heartbeat", data=body, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=20).read()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "claim"
    addr = canary_addr()
    if not addr:
        alert("canary key missing"); sys.exit(1)
    if mode == "beat":
        h = json.load(urllib.request.urlopen(GW + "/v1/health", timeout=20))
        day = h["current_day"]
        # cumulative session within day: 1800s per half-hour call, cap 14400
        st = {}
        try: st = json.load(open("/home/ubuntu/canary_state.json"))
        except Exception: pass
        sess = min(14400, st.get(str(day), 0) + 1800)
        st[str(day)] = sess
        json.dump(st, open("/home/ubuntu/canary_state.json", "w"))
        heartbeat(addr, sess)
        print("canary beat day", day, "sess", sess, "addr", addr)
        return
    # claim mode: claim yesterday if finalized+signed and canary has score
    h = json.load(urllib.request.urlopen(GW + "/v1/health", timeout=20))
    d = h["current_day"] - 1
    day = json.load(urllib.request.urlopen(GW + "/v1/day?day=%d" % d, timeout=20))
    if not day.get("finalized"):
        print("day", d, "not finalized"); return
    sc = json.load(urllib.request.urlopen(GW + "/v1/scores?day=%d" % d, timeout=20))
    mine = (sc.get("scores") or {}).get(addr)
    if not mine or not (mine.get("w", 0) > 0):
        print("canary no score day", d); return
    on = json.loads(sh([WASMD, "q", "wasm", "contract-state", "smart", MR, json.dumps({"root_submitted": {"day": d}}), "--node", NODE, "-o", "json"])[0]).get("data")
    if not on:
        alert("root not on-chain for day %d" % d); sys.exit(1)
    bal0 = json.loads(sh([WASMD, "q", "bank", "balances", addr, "--node", NODE, "-o", "json"])[0])
    b0 = sum(int(x["amount"]) for x in bal0.get("balances", []) if x["denom"] == "ulight")
    proof = json.load(urllib.request.urlopen(GW + "/v1/proof?day=%d&miner=%s" % (d, addr), timeout=20))
    msg = {"claim": {"day": d, "proof": proof["proof"],
                     "score": {k: str(proof["score"][k]) for k in ("bandwidth", "session", "verification", "stability")}}}
    out, rc = sh([WASMD, "tx", "wasm", "execute", MR, json.dumps(msg), "--from", "canary",
                  "--fee-granter", DEP, "--gas", "300000", "--fees", "75000ulight", "-y", "-o", "json"] + KB)
    code = None
    try: code = json.loads(out).get("code")
    except Exception: pass
    if code not in (0, None):
        alert("canary claim tx code %s day %s log %s" % (code, d, out[:200])); sys.exit(1)
    time.sleep(8)
    bal1 = json.loads(sh([WASMD, "q", "bank", "balances", addr, "--node", NODE, "-o", "json"])[0])
    b1 = sum(int(x["amount"]) for x in bal1.get("balances", []) if x["denom"] == "ulight")
    if b1 <= b0:
        alert("canary claim did not increase balance day %d (%d->%d)" % (d, b0, b1)); sys.exit(1)
    print("CANARY OK day %d +%s ulight" % (d, b1 - b0))
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send",
                        "✅ Canary claim OK: day %d +%s LIGHT (settle→sign→proof→claim→payout verified)" % (d, round((b1 - b0) / 1e6, 2))], timeout=30)
    except Exception:
        pass

if __name__ == "__main__":
    main()
