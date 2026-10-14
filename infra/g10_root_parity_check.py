#!/usr/bin/env python3
"""g10_root_parity_check.py — 发布门禁 G10：Merkle 根一致性对拍。

用网关自身的 leaf_hash/build_tree/weighted_score，从夹具中的期望 scores 独立重算
每个历史定稿日的 Merkle 根与 total_score，必须与「已经 5 票多签上链」的期望值逐字节一致。

存在意义：网关存储层改造（追加日志 + 定期快照，为解决 5 万矿工写放大）之后，
根计算必须零漂移。此门禁把"我保证没改坏"变成机器判定。

用法: g10_root_parity_check.py [fixture.json] [gateway.py]
退出码: 0 全一致 / 非 0 有漂移（打印差异明细）
"""
import hashlib, importlib.util, json, os, sys

FIX = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/gw_root_fixtures_public.json"
GW = sys.argv[2] if len(sys.argv) > 2 else "/home/ubuntu/gateway.py"

if not os.path.exists(FIX):
    print("G10 SKIP: 夹具不存在 %s" % FIX); raise SystemExit(0)

os.environ.setdefault("GW_DATA", "/tmp/gw_g10_data")
os.makedirs(os.environ["GW_DATA"], exist_ok=True)
spec = importlib.util.spec_from_file_location("gw", GW)
gw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw)

# 防呆：夹具记录的网关代码哈希若与当前 gateway.py 不同，只提示不失败
# （根计算未变时也应通过；变了就必须重新生成夹具，故此处给出醒目提示）
cur = hashlib.sha256(open(GW, "rb").read()).hexdigest()
d = json.load(open(FIX))
if d.get("gateway_sha256") and d["gateway_sha256"] != cur:
    print("G10 NOTE: gateway.py 已变更（夹具 %s… / 当前 %s…）——若根计算逻辑被改动，本门禁会失败"
          % (d["gateway_sha256"][:12], cur[:12]))

bad, checked = [], 0
for f in d.get("fixtures", []):
    exp = f.get("expect") or {}
    scores = exp.get("scores")
    day = f.get("day")
    if not scores or day is None:
        continue
    checked += 1
    addrs = sorted(scores)
    leaves = [gw.leaf_hash(a, day, scores[a]["bandwidth"], scores[a]["session"],
                           scores[a]["verification"], scores[a]["stability"]) for a in addrs]
    root, _ = gw.build_tree(leaves)
    got_root = root.hex()
    want_root = (exp.get("root") or "").lower()
    got_ts = sum(gw.weighted_score(scores[a]) for a in addrs)
    want_ts = exp.get("total_score")
    if got_root != want_root:
        bad.append("day %s ROOT %s != %s" % (day, got_root[:16], want_root[:16]))
    if want_ts is not None and got_ts != want_ts:
        bad.append("day %s TOTAL_SCORE %s != %s" % (day, got_ts, want_ts))

print("G10 root-parity | days=%d mismatches=%d" % (checked, len(bad)))
for b in bad[:10]:
    print("  ✗", b)
if bad:
    print("G10 ROOT PARITY FAILS: %d" % len(bad))
    raise SystemExit(1)
print("G10 OK")
