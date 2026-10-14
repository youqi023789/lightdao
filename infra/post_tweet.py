#!/usr/bin/env python3
"""LightDAO X 发帖脚本(OAuth1.0a)。用法: python3 post_tweet.py thread.json
thread.json = ["tweet1","tweet2",...] 自动串成线程(reply 链)。
env: /etc/lightdao/x_api.env 需含 X_API_KEY X_API_SECRET X_ACCESS_TOKEN X_ACCESS_SECRET
"""
import base64, hashlib, hmac, json, os, sys, time, urllib.parse, urllib.request

def ov(k): return os.environ[k]

def sign(method, url, params, body=None):
    oauth = {
        "oauth_consumer_key": ov("X_API_KEY"),
        "oauth_nonce": base64.b32encode(os.urandom(10)).decode().rstrip("="),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ov("X_ACCESS_TOKEN"),
        "oauth_version": "1.0",
    }
    sigparams = dict(oauth); sigparams.update(params)
    base = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
                    for k, v in sorted(sigparams.items()))
    base_str = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(base, safe='')}"
    key = f"{urllib.parse.quote(ov('X_API_SECRET'), safe='')}&{urllib.parse.quote(ov('X_ACCESS_SECRET'), safe='')}"
    sig = base64.b64encode(hmac.new(key.encode(), base_str.encode(), hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth.items()))

def post_tweet(text, reply_to=None):
    url = "https://api.x.com/2/tweets"
    payload = {"text": text}
    if reply_to: payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    body = json.dumps(payload).encode()
    auth = sign("POST", url, {})
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    tweets = json.load(open(sys.argv[1]))
    parent = None; ids = []
    for i, t in enumerate(tweets):
        res = post_tweet(t, parent)
        tid = res.get("data", {}).get("id")
        if not tid:
            print(f"tweet{i+1} FAIL:", json.dumps(res)[:300]); sys.exit(1)
        ids.append(tid); parent = tid
        print(f"tweet{i+1} OK id={tid} https://x.com/i/web/status/{tid}")
        time.sleep(2)
    print("THREAD_DONE", len(ids))

if __name__ == "__main__":
    main()
