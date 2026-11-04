#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 chain B 加进 hermes 配置（追加一个 [[chains]] 段）。
   为什么插在最前面而不是文件尾：这个文件尾部可能已有 [filters]/[key_store] 之类的表头，
   TOML 里 [[chains]] 出现在别的表之后会被解析成那个表的子表 → hermes 直接读不到链。
   所以插到"第一个 [[chains]] 之前"，保证它仍是顶层表。"""
import os, re, shutil, time

C = "/home/ubuntu/.hermes/config/config.toml"
BLOCK = '''[[chains]]
id = "lightdao-testnet-b"
rpc_addr = "http://127.0.0.1:26957"
grpc_addr = "http://127.0.0.1:9191"
event_source = { mode = "push", url = "ws://127.0.0.1:26957/websocket" }
rpc_timeout = "20s"
account_prefix = "wasm"
key_name = "relayer"
store_prefix = "ibc"
default_gas = 200000
max_gas = 5000000
gas_price = { price = 0.25, denom = "stake" }
gas_multiplier = 1.6
max_msg_num = 20
max_tx_size = 180000
clock_drift = "10s"
max_block_time = "60s"
trusting_period = "10 days"
memo_prefix = "lightdao-relay"

'''
t = open(C, encoding="utf-8").read()
if "lightdao-testnet-b" in t:
    print("已存在 chain B 配置，跳过")
    raise SystemExit(0)
shutil.copy2(C, C + ".bak-" + time.strftime("%Y%m%dT%H%M%SZ"))
m = re.search(r'(?m)^\[\[chains\]\]', t)
pos = m.start() if m else len(t)
out = t[:pos] + BLOCK + t[pos:]
tmp = C + ".tmp"
open(tmp, "w", encoding="utf-8").write(out)
os.replace(tmp, C)
print("chain B 已插入到第一个 [[chains]] 之前（偏移 %d）" % pos)
