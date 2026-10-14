#!/usr/bin/env python3
"""post_tweet_media.py — 带图发帖(OAuth1.0a)。
输入 JSON: [{"text":"...", "media":"/abs/path.png"}, ...] (media 可省略=纯文本)
也兼容旧格式 ["tweet1","tweet2"](纯文本线程)。
env: /etc/lightdao/x_api.env (X_API_KEY/SECRET/ACCESS_TOKEN/ACCESS_SECRET)
MEDIA_TEST_ONLY=1 时只上传媒体返回 media_id,不发帖(免费,不进时间线)。
"""
import base64, hashlib, hmac, json, mimetypes, os, sys, time, urllib.parse, urllib.request, uuid

def ov(k): return os.environ[k]

def sign(method, url, params):
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
    base_str = f"{method}&{urllib.parse.quote(url, safe='')}^{urllib.parse.quote(base, safe='')}"\
        .replace("^", "&")
    key = f"{urllib.parse.quote(ov('X_API_SECRET'), safe='')}^{urllib.parse.quote(ov('X_ACCESS_SECRET'), safe='')}".replace("^", "&")
    sig = base64.b64encode(hmac.new(key.encode(), base_str.encode(), hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth.items()))

def upload_media(path):
    """X v1.1 media/upload, multipart. OAuth signature covers only oauth params."""
    url = "https://upload.twitter.com/1.1/media/upload.json"
    data = open(path, "rb").read()
    if len(data) > 5 * 1024 * 1024:
        raise SystemExit("media >5MB: %s (%d bytes)" % (path, len(data)))
    mime = mimetypes.guess_type(path)[0] or "image/png"
    boundary = "ld" + uuid.uuid4().hex
    parts = []
    parts.append(("--%s\r\nContent-Disposition: form-data; name=\"media\"; filename=\"%s\"\r\n"
                  "Content-Type: %s\r\n\r\n" % (boundary, os.path.basename(path), mime)).encode())
    parts.append(data)
    parts.append(("\r\n--%s--\r\n" % boundary).encode())
    body = b"".join(parts)
    auth = sign("POST", url, {})  # multipart: 只签 oauth 参数
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": auth,
        "Content-Type": "multipart/form-data; boundary=" + boundary,
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read())
    mid = res.get("media_id_string")
    if not mid:
        raise SystemExit("media upload FAIL: %s" % json.dumps(res)[:300])
    return mid

def safe_upload(path):
    """MEDIA-FALLBACK: 媒体上传失败不阻断当日发布。"""
    if not path:
        return None
    try:
        return upload_media(path)
    except SystemExit as e:
        sys.stderr.write('MEDIA-SKIP(systemexit): %s\n' % e); return None
    except Exception as e:
        sys.stderr.write('MEDIA-SKIP(%s): %s\n' % (type(e).__name__, e)); return None


def post_tweet(text, media_ids=None, reply_to=None):
    url = "https://api.x.com/2/tweets"
    payload = {"text": text}
    if media_ids: payload["media"] = {"media_ids": media_ids}
    if reply_to: payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    body = json.dumps(payload).encode()
    auth = sign("POST", url, {})
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    entries = json.load(open(sys.argv[1]))
    norm = []
    for e in entries:
        if isinstance(e, str): norm.append({"text": e})
        else: norm.append(e)
    if os.environ.get("MEDIA_TEST_ONLY") == "1":
        for i, e in enumerate(norm, 1):
            p = e.get("media")
            if p:
                mid = upload_media(p)
                print("media%d OK id=%s file=%s" % (i, mid, p))
            else:
                print("media%d (none)" % i)
        print("MEDIA_TEST_DONE")
        return
    parent = None; ids = []
    for i, e in enumerate(norm, 1):
        mids = []
        if e.get("media"):
            mids = [x for x in [safe_upload(e["media"])] if x]
        # MEDIA-FALLBACK: 带图被拒(403)或上传失败时自动降级为纯文本，保证每日必发
        _mid = mids
        if isinstance(_mid, list) and not _mid:
            _mid = None
        try:
            res = post_tweet(e["text"], _mid, parent)
        except Exception as _e:
            _c = getattr(_e, 'code', None)
            if _mid and _c in (403, 400):
                sys.stderr.write('MEDIA-REJECTED(%s) -> posting text-only\n' % _c)
                res = post_tweet(e["text"], None, parent)
            else:
                raise

        tid = res.get("data", {}).get("id")
        if not tid:
            print(f"tweet{i} FAIL:", json.dumps(res)[:300]); sys.exit(1)
        ids.append(tid); parent = tid
        tag = "+media" if mids else ""
        print(f"tweet{i} OK id={tid} {tag} https://x.com/i/web/status/{tid}")
        time.sleep(2)
    print("THREAD_DONE", len(ids))

if __name__ == "__main__":
    main()
