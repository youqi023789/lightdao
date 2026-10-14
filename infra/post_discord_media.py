#!/usr/bin/env python3
"""post_discord_media.py — Discord 带图发帖(multipart)。
用法: python3 post_discord_media.py "<text>" </abs/path.jpg>
token=/etc/lightdao/discord_bot.env, channel=/etc/lightdao/discord_channel
无图参数时退化为纯文本。
"""
import json, os, sys, urllib.request, uuid

ENV = "/etc/lightdao/discord_bot.env"
CHAN_F = "/etc/lightdao/discord_channel"
API = "https://discord.com/api/v10"

def token():
    for ln in open(ENV):
        if ln.startswith("DISCORD_BOT_TOKEN="):
            return ln.split("=", 1)[1].strip()
    raise SystemExit("no token")

def channel():
    return open(CHAN_F).read().strip()

def post(text, image_path=None):
    ch = channel()
    UA = "LightDAOBot/1.0 (+https://lightdao.net; press@lightdao.net)"
    if not image_path:
        body = json.dumps({"content": text}).encode()
        req = urllib.request.Request(API + "/channels/%s/messages" % ch, data=body, method="POST",
            headers={"Authorization": "Bot " + token(), "Content-Type": "application/json", "User-Agent": UA})
    else:
        boundary = "ld" + uuid.uuid4().hex
        payload = json.dumps({"content": text}).encode()
        img = open(image_path, "rb").read()
        mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        parts = []
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"payload_json\"\r\n"
                      "Content-Type: application/json\r\n\r\n" % boundary).encode())
        parts.append(payload)
        parts.append(("\r\n--%s\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"%s\"\r\n"
                      "Content-Type: %s\r\n\r\n" % (boundary, os.path.basename(image_path), mime)).encode())
        parts.append(img)
        parts.append(("\r\n--%s--\r\n" % boundary).encode())
        body = b"".join(parts)
        req = urllib.request.Request(API + "/channels/%s/messages" % ch, data=body, method="POST",
            headers={"Authorization": "Bot " + token(),
                     "Content-Type": "multipart/form-data; boundary=" + boundary,
                     "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.loads(r.read())
    print("sent %s %s%s" % (r.status, res.get("id"), "+file" if image_path else ""))

def delete(msg_id):
    ch = channel()
    req = urllib.request.Request(API + "/channels/%s/messages/%s" % (ch, msg_id), method="DELETE",
        headers={"Authorization": "Bot " + token(),
                 "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net; press@lightdao.net)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("delete %s -> %s" % (msg_id, r.status))
    except Exception as e:
        print("delete %s FAIL: %s" % (msg_id, e))

if __name__ == "__main__":
    if sys.argv[1] == "delete":
        delete(sys.argv[2])
    else:
        post(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
