#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""让 chain B 的 gRPC 真正可用。
   实测根因：B 的 app.toml 里 grpc 地址是 localhost:9090，而 9090 已被**主网 wasmd 进程**占用
   （ss -ltnp 显示 127.0.0.1:9090 属于 pid 190163 的 wasmd），B 的 gRPC 因此根本没监听，
   hermes 打到 9090 其实是打到主网节点上 → 报"account not found"（那台链上确实没有这个账户）。
   这种"端口撞了但进程不报错"的情况，靠看配置是看不出来的，必须 ss -ltnp 看到属主才算查清。

   改法：B 的 gRPC 换到 127.0.0.1:9099，并同步 hermes 配置；两处都改完再重启 B。
   不碰主网、不碰 A 链的端口配置。"""
import os, re, subprocess

APP = "/home/ubuntu/.lightd-testnet-b/config/app.toml"
HER = "/home/ubuntu/.hermes/config/config.toml"
PORT = "9099"


def grpc_block(t):
    i = t.find("[grpc]")
    if i < 0:
        raise SystemExit("app.toml 里找不到 [grpc] 段")
    j = t.find("[grpc-web]", i)
    return i, (j if j > 0 else len(t))


t = open(APP, encoding="utf-8").read()
i, j = grpc_block(t)
seg = t[i:j]
seg2, n1 = re.subn(r'(?m)^\s*address\s*=\s*"[^"]*"', 'address = "127.0.0.1:%s"' % PORT, seg, count=1)
seg2, n2 = re.subn(r'(?m)^\s*enable\s*=\s*(false|true)', "enable = true", seg2, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("app.toml 的 grpc 段没改到（address=%d enable=%d）" % (n1, n2))
out = t[:i] + seg2 + t[j:]
tmp = APP + ".tmp"
open(tmp, "w", encoding="utf-8").write(out)
os.replace(tmp, APP)
print("B gRPC → 127.0.0.1:%s（enable=true）" % PORT)

h = open(HER, encoding="utf-8").read()
i2 = h.find('id = "lightdao-testnet-b"')
if i2 < 0:
    raise SystemExit("hermes 配置里找不到 chain B")
j2 = h.find("[[chains]]", i2 + 10)
j2 = j2 if j2 > 0 else len(h)
seg = h[i2:j2]
seg2 = re.sub(r'grpc_addr = "[^"]*"', 'grpc_addr = "http://127.0.0.1:%s"' % PORT, seg, count=1)
if seg2 == seg:
    raise SystemExit("hermes 的 B 段里没找到 grpc_addr")
out2 = h[:i2] + seg2 + h[j2:]
tmp2 = HER + ".tmp"
open(tmp2, "w", encoding="utf-8").write(out2)
os.replace(tmp2, HER)
print("hermes B grpc_addr →", [l.strip() for l in seg2.split("\n") if "grpc_addr" in l])

subprocess.run(["systemctl", "restart", "lightd-testnet-b"], check=False)
subprocess.run(["systemctl", "restart", "hermes-relay"], check=False)
