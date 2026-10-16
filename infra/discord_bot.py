#!/usr/bin/env python3
"""Discord helpers: post message / build+post weekly network recap. Token from /etc/lightdao/discord_bot.env."""
import json, os, sys, urllib.request

ENV = "/etc/lightdao/discord_bot.env"
CHAN = "/etc/lightdao/discord_channel"
API = "https://discord.com/api/v10"

def token():
    for ln in open(ENV):
        if ln.startswith("DISCORD_BOT_TOKEN="):
            return ln.split("=", 1)[1].strip()
    raise SystemExit("no token")

def req(method, path, body=None):
    r = urllib.request.Request(API + path, method=method,
        headers={"Authorization": "Bot " + token(), "Content-Type": "application/json", "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net; press@lightdao.net)"})
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(r, data, timeout=30) as resp:
        return resp.status, json.loads(resp.read() or b"{}")

def post(channel_id, text):
    st, body = req("POST", "/channels/%s/messages" % channel_id, {"content": text})
    return st, body.get("id")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    if cmd == "me":
        st, me = req("GET", "/users/@me")
        print("auth", st, me.get("username"), me.get("discriminator"))
    elif cmd == "guilds":
        st, gs = req("GET", "/users/@me/guilds")
        for g in gs: print(g["id"], g["name"])
    elif cmd == "channels":
        gid = sys.argv[2]
        st, cs = req("GET", "/guilds/%s/channels" % gid)
        for c in cs: print(c["id"], c.get("type"), c.get("name"))
    elif cmd == "detect":
        st, gs = req("GET", "/users/@me/guilds")
        gid = None
        for g in gs:
            if "lightdao" in g["name"].lower(): gid = g["id"]
        if not gid and gs: gid = gs[0]["id"]
        st, cs = req("GET", "/guilds/%s/channels" % gid)
        cid = None
        for c in cs:
            if c.get("name") == "announcements" and c.get("type") == 0: cid = c["id"]
        if not cid:
            for c in cs:
                if c.get("type") == 0: cid = c["id"]; break
        open(CHAN, "w").write(cid + "\n")
        print("guild", gid, "channel", cid)
    elif cmd == "send":
        OPS="/etc/lightdao/discord_ops"
        cid = open(OPS).read().strip() if os.path.exists(OPS) else open(CHAN).read().strip()
        if len(sys.argv) > 3 and sys.argv[2] == "--chan":
            cid = sys.argv[3]; text = sys.argv[4] if len(sys.argv) > 4 else sys.stdin.read()
        else:
            text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        st, mid = post(cid, text)
        print("sent", st, mid)
    elif cmd == "weekly":
        import subprocess
        def sh(c):
            try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=30).stdout.strip()
            except Exception: return ""
        h = sh("wasmd status --node tcp://127.0.0.1:26657 2>/dev/null | python3 -c \"import sys,json;print(json.load(sys.stdin)['sync_info']['latest_block_height'])\"")
        burn = sh("wasmd q bank balances wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c \"import sys,json;d=json.load(sys.stdin)['balances'];print(round(sum(int(x['amount']) for x in d if x['denom']=='ulight')/1e6,1))\"")
        tre = sh("wasmd q bank balances wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c \"import sys,json;d=json.load(sys.stdin)['balances'];print(round(sum(int(x['amount']) for x in d if x['denom']=='ulight')/1e6,1))\"")
        vals = sh("wasmd q staking validators --node tcp://127.0.0.1:26657 -o json 2>/dev/null | python3 -c \"import sys,json;v=json.load(sys.stdin)['validators'];print(sum(1 for x in v if x['status']=='BOND_STATUS_BONDED'),len(v))\"")
        day = sh("curl -s http://127.0.0.1:8080/v1/health | python3 -c \"import sys,json;print(json.load(sys.stdin)['current_day'])\"")
        miners = sh("curl -s http://127.0.0.1:8080/v1/scores?day=%s | python3 -c \"import sys,json;print(len(json.load(sys.stdin)['scores']))\" 2>/dev/null" % day)
        msg = ("**LightDAO Weekly Recap**\n"
               "Height: %s · Validators: %s bonded\n"
               "Burned (cumulative): %s LIGHT · Treasury: %s LIGHT\n"
               "Season day: %s · Miners today: %s\n"
               "Mine (no hardware, no seed): https://lightdao.net\n"
               "Explorer / governance / whitepaper on-site · Discord: <#%s>"
               ) % (h or "?", vals or "?", burn or "?", tre or "?", day or "?", miners or "?", open(CHAN).read().strip())
        st, mid = post(open(CHAN).read().strip(), msg)
        print("weekly sent", st, mid)

if __name__ == "__main__":
    main()
