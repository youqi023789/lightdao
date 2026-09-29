#!/usr/bin/env python3
import json, subprocess, glob
NL = ["--node", "tcp://127.0.0.1:26657"]
NS = "--node tcp://127.0.0.1:26657"
DEP = "wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"
CANARY = "wasm1ar9mg3ls3xw3ac44j29dvptnls0zgdhy8aghc3"
EXPLICIT = ["wasm1vhpf9c3h8eu8hd7ca520dvspzdsxz4nkka3h7s"]  # compromised seed, abandoned by owner

def sh(c):
    r = subprocess.run(c, shell=isinstance(c, str), capture_output=True, text=True, timeout=90)
    return r.stdout.strip()

grants = json.loads(sh(["wasmd", "q", "feegrant", "grants-by-granter", DEP] + NL + ["-o", "json"]))["allowances"]
grantees = [g["grantee"] for g in grants]
active = {CANARY}
for p in glob.glob("/home/ubuntu/lightdao_gateway/data/day_*.json"):
    try:
        active |= set((json.load(open(p)).get("miners") or {}).keys())
    except Exception:
        pass
revoke = sorted(set([g for g in grantees if g not in active] + [e for e in EXPLICIT if e in grantees]))
print("grantees=%d active=%d revoke=%d" % (len(grantees), len(active), len(revoke)))
for g in revoke:
    out = sh("wasmd tx feegrant revoke %s %s --from deployer --home /home/ubuntu/.wasmd --keyring-backend test --chain-id lightdao-mainnet-1 %s --gas 200000 --fees 60000ulight -y -o json" % (DEP, g, NS))
    try:
        code = json.loads(out[out.find("{"):]).get("code")
    except Exception:
        code = "parse-fail:" + out[:80]
    print("revoked", g, "code=", code)
rem = json.loads(sh(["wasmd", "q", "feegrant", "grants-by-granter", DEP] + NL + ["-o", "json"]))["allowances"]
print("remaining grants:", len(rem))
