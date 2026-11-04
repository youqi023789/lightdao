#!/usr/bin/env python3
"""tg_post.py — Telegram channel post (text + optional photo).
Usage: tg_post.py <text> [photo_path]
Env: /etc/lightdao/telegram_bot.env (TG_BOT_TOKEN=..., TG_CHANNEL=@...)
Uses sendPhoto when photo given, sendMessage otherwise. Exits non-zero on failure."""
import json, os, sys, urllib.request

ENV = "/etc/lightdao/telegram_bot.env"

def cfg():
    tok, chan = None, None
    for ln in open(ENV):
        if ln.startswith("TG_BOT_TOKEN="): tok = ln.split("=", 1)[1].strip()
        if ln.startswith("TG_CHANNEL="): chan = ln.split("=", 1)[1].strip()
    return tok, chan

def main():
    text = sys.argv[1]
    photo = sys.argv[2] if len(sys.argv) > 2 else None
    tok, chan = cfg()
    if not tok or not chan:
        print("ERR: telegram_bot.env missing TG_BOT_TOKEN/TG_CHANNEL"); sys.exit(2)
    if len(text) > 1024:
        text = text[:1020] + "..."
    url = "https://api.telegram.org/bot%s/sendMessage" % tok
    data = {"chat_id": chan, "text": text, "disable_web_page_preview": False}
    if photo and os.path.exists(photo):
        url = "https://api.telegram.org/bot%s/sendPhoto" % tok
        # multipart upload (CRLF-terminated parts — Telegram API rejects bare-LF)
        boundary = "----ldboundary"
        head = ""
        head += '--%s\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n%s\r\n' % (boundary, chan)
        head += '--%s\r\nContent-Disposition: form-data; name="caption"\r\n\r\n%s\r\n' % (boundary, text[:1024])
        head += '--%s\r\nContent-Disposition: form-data; name="photo"; filename="%s"\r\nContent-Type: image/jpeg\r\n\r\n' % (boundary, os.path.basename(photo))
        payload = head.encode() + open(photo, "rb").read() + ('\r\n--%s--\r\n' % boundary).encode()
        req = urllib.request.Request(url, data=payload, method="POST",
            headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary,
                     "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net)"})
    else:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST",
            headers={"Content-Type": "application/json",
                     "User-Agent": "LightDAOBot/1.0 (+https://lightdao.net)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
        if resp.get("ok"):
            print("TG OK message_id=%s" % resp["result"]["message_id"])
        else:
            print("TG FAIL %s" % resp); sys.exit(1)
    except Exception as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        print("TG ERR %s %s" % (e, body)); sys.exit(1)

if __name__ == "__main__":
    main()
