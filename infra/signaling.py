#!/usr/bin/env python3
"""
LightDAO §4.7 WebRTC 信令服务器 (v1)
职责:
  - 客户端(miner)经 WSS 连接,注册自己的地址
  - 维护在线 peer 池,供 P2P 数据通道发现
  - 中转 SDP offer/answer + ICE candidate( WebRTC 信令)
  - 累计每个 miner 的中继流量字节(喂给 gateway 的 40% 带宽分)
协议(JSON 文本帧):
  C->S {"type":"hello","addr":"wasm1...","region":"sg"}
  S->C {"type":"welcome","id":"<peerId>","peers":<count>}
  C->S {"type":"peers"}                -> S->C {"type":"peer-list","peers":[{"id","addr","region"}...]}
  C->S {"type":"offer","to":"<id>","sdp":{...}}   -> 转发给 to
  C->S {"type":"answer","to":"<id>","sdp":{...}}  -> 转发给 to
  C->S {"type":"ice","to":"<id>","candidate":{...}} -> 转发给 to
  C->S {"type":"relay","bytes":N,"for":"<id>"}     -> 累计中继计量
  S->C {"type":"relay-total","bytes":N}
零外部依赖(仅 websockets)。监听 127.0.0.1:8090,由 nginx WSS 反代。
"""
import asyncio, json, logging, os, secrets, time
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

HOST = os.environ.get("SIGNAL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SIGNAL_PORT", "8090"))
MAX_PEERS_LIST = int(os.environ.get("SIGNAL_MAX_PEERS", "50"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("signal")

# peerId -> {ws, addr, region, relay_bytes, joined}
PEERS = {}
# addr -> relay_bytes(跨重连累计,周期性可持久化)
RELAY_TOTALS = {}


async def send(ws, obj):
    try:
        await ws.send(json.dumps(obj))
    except Exception:
        pass


async def broadcast_count():
    msg = json.dumps({"type": "peer-count", "peers": len(PEERS)})
    async def _safe(p):
        try:
            await p["ws"].send(msg)
        except Exception:
            pass
    await asyncio.gather(*[_safe(p) for p in PEERS.values()], return_exceptions=True)


async def handler(ws):
    peer_id = secrets.token_hex(8)
    addr = None
    try:
        async for raw in ws:
            try:
                m = json.loads(raw)
            except Exception:
                continue
            t = m.get("type")

            if t == "hello":
                addr = (m.get("addr") or "")[:128]
                region = (m.get("region") or "")[:16]
                PEERS[peer_id] = {"ws": ws, "addr": addr, "region": region,
                                  "joined": time.time(), "relay_bytes": RELAY_TOTALS.get(addr, 0)}
                await send(ws, {"type": "welcome", "id": peer_id, "peers": len(PEERS)})
                await broadcast_count()
                log.info("peer joined id=%s addr=%s region=%s total=%d", peer_id, addr[:16], region, len(PEERS))

            elif t == "peers":
                # 返回其他在线 peer(最多 MAX_PEERS_LIST,优先同 region 之外做跨域中继)
                others = [{"id": pid, "addr": p["addr"], "region": p["region"]}
                          for pid, p in PEERS.items() if pid != peer_id]
                # 简单打散,避免所有人只连前几个
                others = others[-MAX_PEERS_LIST:]
                await send(ws, {"type": "peer-list", "peers": others})

            elif t in ("offer", "answer", "ice"):
                to = m.get("to")
                target = PEERS.get(to)
                if target:
                    fwd = {"type": t, "from": peer_id}
                    if t == "ice":
                        fwd["candidate"] = m.get("candidate")
                    else:
                        fwd["sdp"] = m.get("sdp")
                    await send(target["ws"], fwd)

            elif t == "relay":
                # 中继流量计量:bytes 为本 peer 为别人中继的字节数
                try:
                    b = int(m.get("bytes", 0))
                except Exception:
                    b = 0
                if b > 0 and addr:
                    PEERS[peer_id]["relay_bytes"] = PEERS[peer_id].get("relay_bytes", 0) + b
                    RELAY_TOTALS[addr] = RELAY_TOTALS.get(addr, 0) + b
                    await send(ws, {"type": "relay-total", "bytes": RELAY_TOTALS[addr]})

            elif t == "ping":
                await send(ws, {"type": "pong", "t": time.time()})

    except ConnectionClosed:
        pass
    finally:
        p = PEERS.pop(peer_id, None)
        if p and addr:
            RELAY_TOTALS[addr] = p.get("relay_bytes", RELAY_TOTALS.get(addr, 0))
        await broadcast_count()
        log.info("peer left id=%s total=%d", peer_id, len(PEERS))


async def stats_logger():
    while True:
        await asyncio.sleep(60)
        log.info("online=%d relay_addrs=%d", len(PEERS), len(RELAY_TOTALS))


async def main():
    log.info("LightDAO signaling starting on %s:%d", HOST, PORT)
    async with serve(handler, HOST, PORT, max_size=2**20, ping_interval=20, ping_timeout=20) as server:
        await asyncio.gather(stats_logger(), server.serve_forever())


if __name__ == "__main__":
    asyncio.run(main())
