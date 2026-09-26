#!/usr/bin/env python3
"""
LightDAO §4.7 TURN 临时凭证端点 (coturn REST API / use-auth-secret)
客户端 GET /turn/ -> 返回 iceServers(8 个域名节点)+ 限时 HMAC 凭证。
凭证算法(coturn 标准):username="<expiry>:<rand>", credential=base64(HMAC(secret, username))
域名版:证书按 turn-*.lightdao.net 签发,故 ICE 用域名(含 turns TLS)。
零外部依赖。监听 127.0.0.1:8091,nginx 反代 /turn/。
"""
import base64, hashlib, hmac, json, os, time, random, string
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SECRET = os.environ.get("TURN_SECRET", "").strip()
PORT = int(os.environ.get("TURN_CRED_PORT", "8091"))
TTL = int(os.environ.get("TURN_TTL", "86400"))
# 8 个 TURN/STUN 节点域名(§4.7 验证者分布式中继)
TURN_HOSTS = [
    "turn-jp.lightdao.net",
    "turn-kr.lightdao.net",
    "turn-sg.lightdao.net",
    "turn-us.lightdao.net",
    "turn-hk.lightdao.net",
    "turn-fr.lightdao.net",
    "turn-uk.lightdao.net",
    "turn-8.lightdao.net",
]


def make_cred():
    expiry = int(time.time()) + TTL
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f"{expiry}:{rand}"
    mac = hmac.new(SECRET.encode(), username.encode(), hashlib.sha1).digest()
    credential = base64.b64encode(mac).decode()
    return username, credential


def ice_servers():
    u, c = make_cred()
    servers = []
    for h in TURN_HOSTS:
        servers.append({
            "urls": [
                f"stun:{h}:3478",
                f"turn:{h}:3478?transport=udp",
                f"turn:{h}:3478?transport=tcp",
                f"turns:{h}:5349?transport=tcp",
            ],
            "username": u,
            "credential": c,
        })
    return {"iceServers": servers, "ttl": TTL}


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        if not SECRET:
            self.send_response(500); self._cors(); self.end_headers()
            self.wfile.write(b'{"error":"TURN_SECRET not set"}'); return
        body = json.dumps(ice_servers()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"TURN cred endpoint on 127.0.0.1:{PORT} (secret_set={bool(SECRET)}, hosts={len(TURN_HOSTS)})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
