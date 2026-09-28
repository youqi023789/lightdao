#!/usr/bin/env python3
"""engage.py — 互动巡检收集器(只收集+去重, 不自行回复; 回复由定时任务agent判断后执行)。
用法: engage.py [x|discord|gh|all]
输出 JSON: 各渠道"自上次巡检以来"的新条目。状态存 /home/ubuntu/engage_seen.json。"""
import json, os, sys, urllib.request, subprocess

SEEN = "/home/ubuntu/engage_seen.json"
XENV = "/etc/lightdao/x_api.env"
DENV = "/etc/lightdao/discord_bot.env"
CHANS = {"general": "1553595031670095952", "mining-help": "1553595102004252712"}

def load():
    try: return json.load(open(SEEN))
    except Exception: return {}
def save(d): json.dump(d, open(SEEN, "w"))
def envfile(p):
    e = {}
    for ln in open(p):
        if "=" in ln: k, v = ln.strip().split("=", 1); e[k] = v.strip('"')
    return e
def get(url, hdr):
    req = urllib.request.Request(url, headers=hdr)
    return json.load(urllib.request.urlopen(req, timeout=20))

def collect_x(seen):
    e = envfile(XENV)
    bearer = e.get("X_BEARER_TOKEN") or e.get("X_BEARER") or ""
    if not bearer: return {"error": "no bearer"}
    H = {"Authorization": "Bearer " + bearer, "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net)"}
    uid = get("https://api.twitter.com/2/users/by/username/lightdaoproto", H)["data"]["id"]
    data = get("https://api.twitter.com/2/users/%s/mentions?max_results=50&tweet.fields=created_at,author_id,username" % uid, H).get("data", []) or []
    last = seen.get("x_last", "")
    new = [t for t in data if (not last) or t["id"] > last]
    if not last: new = data[:10]
    if new: seen["x_last"] = max(t["id"] for t in new)
    return [{"id": t["id"], "user": t.get("username"), "text": t["text"][:220], "at": t.get("created_at")} for t in new]

def collect_discord(seen):
    e = envfile(DENV)
    tok = e.get("DISCORD_BOT_TOKEN") or e.get("TOKEN") or ""
    if not tok: return {"error": "no token"}
    H = {"Authorization": "Bot " + tok, "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net)"}
    out = []
    for name, cid in CHANS.items():
        msgs = get("https://discord.com/api/v10/channels/%s/messages?limit=25" % cid, H)
        last = seen.get("dc_" + name, "")
        new = [m for m in msgs if (not last) or m["id"] > last]
        if not last: new = msgs[:8]
        if new: seen["dc_" + name] = max(m["id"] for m in new)
        for m in new:
            if m.get("author", {}).get("bot"): continue
            out.append({"chan": name, "id": m["id"], "user": m["author"].get("username"), "text": (m.get("content") or "")[:220]})
    return out

def collect_gh():
    r = subprocess.run(["/home/ubuntu/gh", "api", "notifications", "--jq",
                        ".[0:15][] | {id:.id, repo:.repository.full_name, title:.subject.title, type:.subject.type, unread:.unread}"],
                       capture_output=True, text=True, timeout=40)
    try: return [json.loads(l) for l in r.stdout.strip().splitlines() if l.strip()]
    except Exception: return {"raw": r.stdout[:500] or r.stderr[:300]}

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    seen = load(); changed = False; out = {}
    if mode in ("all", "x"):
        out["x_mentions"] = collect_x(seen); changed = True
    if mode in ("all", "discord"):
        out["discord_new"] = collect_discord(seen); changed = True
    if mode in ("all", "gh"):
        out["github_unread"] = collect_gh()
    if changed: save(seen)
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
