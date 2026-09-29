#!/usr/bin/env python3
"""Paymaster: grant x/feegrant fee-allowance from deployer to each new miner of a finalized day,
so their first claim txs are gasless. Idempotent via granted.json. Usage: gas_grant.py <day>"""
import json, os, subprocess, sys, time
from datetime import datetime, timedelta, timezone

DATA = "/home/ubuntu/lightdao_gateway/data"
GRANTED = "/home/ubuntu/lightdao_gateway/granted.json"
DEP = "wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"
NODE = "tcp://127.0.0.1:26657"
CHAIN = "lightdao-mainnet-1"
HOME = "/home/ubuntu/.wasmd"
LIMIT = "5000000ulight"      # ~ enough for many claim txs at 0.2 ulight/gas

def exp_rfc3339():
    return (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

def load():
    try: return json.load(open(GRANTED))
    except Exception: return {}

def save(d): json.dump(d, open(GRANTED, "w"), indent=1)

def grant(miner):
    cmd = ["wasmd", "tx", "feegrant", "grant", DEP, miner,
           "--spend-limit", LIMIT, "--expiration", exp_rfc3339(),
           "--from", "deployer", "--home", HOME, "--keyring-backend", "test",
           "--chain-id", CHAIN, "--node", NODE, "--gas", "200000", "--fees", "60000ulight", "-y", "-o", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    try: out = json.loads(r.stdout)
    except Exception: return False, r.stdout[:200] + r.stderr[:200]
    return out.get("code") == 0, out.get("raw_log", "")[:150]

def main():
    day = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if day is None:
        print("usage: gas_grant.py <day>"); sys.exit(1)
    p = os.path.join(DATA, "day_%d.json" % day)
    if not os.path.exists(p): print("no day file", p); return
    _dj = json.load(open(p))
    miners = (_dj.get("miners") or {}).keys()
    ips = _dj.get("ips") or {}
    g = load(); changed = False
    import time as _t
    _today = _t.gmtime().tm_mday
    def _ip_count(ip):
        return sum(1 for v in g.values() if v.get("ip") == ip and v.get("d") == _today)

    for m in sorted(miners):
        if not m.startswith("wasm1") or len(m) < 20: continue
        if g.get(m, {}).get("ok"): continue
        _ip = ips.get(m) or "unknown"
        if _ip_count(_ip) >= 3:
            print("skip grant %s: ip %s reached daily cap 3" % (m, _ip)); continue
        ok, log = grant(m)
        try:
            bal=subprocess.run(["wasmd","q","bank","balances",m,"--node",NODE,"-o","json"],capture_output=True,text=True,timeout=30)
            if not json.loads(bal.stdout).get("balances"):
                subprocess.run(["wasmd","tx","bank","send",DEP,m,"1000ulight","--from","deployer","--home",HOME,"--keyring-backend","test","--chain-id",CHAIN,"--node",NODE,"--gas","150000","--fees","45000ulight","-y"],capture_output=True,text=True,timeout=60)
                time.sleep(4)
        except Exception:
            pass

        g[m] = {"day": day, "ok": ok, "log": log, "ts": int(time.time()), "dust": True, "ip": (ips.get(m) or "unknown"), "d": __import__("time").gmtime().tm_mday}
        changed = True
        print("grant", m, "ok" if ok else "FAIL " + log)
        time.sleep(3)  # avoid sequence race on same signer
    if changed: save(g)
    print("granted total:", sum(1 for v in g.values() if v.get("ok")))

if __name__ == "__main__":
    main()
