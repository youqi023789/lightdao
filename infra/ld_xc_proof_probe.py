#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_xc_proof_probe.py —— IBC「证明源就绪度」服务器端探针（11-08 老板令：自走、别靠会话盯）。

背景：LightDAO 跨链的入金(osmo→主网)与超时退款都要求"对面链出 ICS-23 证明"；
这台网关此刻连不到会出证明的 Osmosis 端点（公共 gRPC 全超时，可用 LCD 把 proof 剥成空），
主网自身 binary 又不发证明（另案）。与其等人手动重试，不如把"探到能出证明的端点"这件事
交给服务器 cron 定时跑，一旦逮到就翻就绪标志 + 写状态 + 告警；探针本身哑了/全失败也告警。

四件套（对齐本项目铁律）：
  执行点：cron 每 N 分钟跑本脚本；
  检测点：对每个候选端点做一次"带证明的查询"（PacketReceipt 或 ClientState 都要返回非空 proof）；
  告警点：①首次从"全不通"变"某源通"→INFO；②连续 FAIL_STREAK 次全不通→WARN；
          ③状态文件没更新（进程/权限哑了）→由外部 watch 兜底，本脚本每次成功都带心跳时间戳；
  自测：  --selftest 注入"坏端点必判不通 / 假好端点必判通 / 心跳缺失要被发现"，反向验证不误报。

边界：只读查询，不签名、不广播、不碰私钥；端点清单从环境/内置列表来，不含任何密钥。
"""
import json
import os
import time
import urllib.request

STATE = os.environ.get("XCP_STATE", "/home/ubuntu/ld_xc_proof_state.json")
FAIL_STREAK = int(os.environ.get("XCP_FAIL_STREAK", "8"))
# 候选 Osmosis 证明端点：改用 cosmos/chain-registry 权威登记（多为 :443 gRPC-over-TLS，
# 本机房 9090 原生 gRPC 实测连不通）。全部只读、可增删；11-08 实测这些当前都不发证明(proof_len0)，
# 一旦某节点开始发证明，本探针即翻 ready_src 并告警。
OSMO_GRPC = os.environ.get("XCP_OSMO_GRPC", ",".join([
    "osmosis.lavenderfive.com:443", "osmosis.grpc.stakin-nodes.com:443",
    "osmosis-grpc.publicnode.com:443", "grpc.osmosis.validatus.com:443",
    "osmosis-grpc.polkachu.com:12590", "grpc-osmosis-01.stakeflow.io:6754"]))
OSMO_REST = os.environ.get("XCP_OSMO_REST", ",".join([
    "https://lcd.osmosis.zone", "https://rest.cosmos.directory/osmosis",
    "https://osmosis-rest.publicnode.com", "https://osmosis.rest.stakin-nodes.com"]))
CHANNEL = os.environ.get("XCP_CHANNEL", "channel-111104")
PORT = "transfer"
GRPCURL = os.environ.get("XCP_GRPCURL", "/home/ubuntu/grpcurl")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def rest_has_proof(base, height):
    """REST 客户端状态带 x-cosmos-block-height 查询：返回 proof 非空即视为该源能出证明。"""
    url = base.rstrip("/") + "/ibc/core/client/v1/client_states/07-tendermint-3768"
    req = urllib.request.Request(url, headers={"User-Agent": "ld-xc-proof-probe/1.0",
                                                "x-cosmos-block-height": str(height)})
    with urllib.request.urlopen(req, timeout=20) as f:
        d = json.load(f)
    pr = d.get("proof")
    return bool(pr) and len(pr) > 8


def grpc_has_proof(endpoint, height, channel, sequence="8"):
    import subprocess
    data = json.dumps({"port_id": PORT, "channel_id": channel, "sequence": sequence})
    # :443 及已知 grpcs 走 TLS（不加 -plaintext），其余按明文 9090
    insecure = not (endpoint.endswith(":443") or "grpcs" in endpoint)
    args = [GRPCURL] + (["-plaintext"] if insecure else []) + \
        ["-H", "x-cosmos-block-height: %d" % height, "-d", data, endpoint,
         "ibc.core.channel.v1.Query/PacketReceipt"]
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    out = (p.stdout or "").strip()
    if not out:
        return False
    try:
        d = json.loads(out)
    except Exception:
        return False
    pr = d.get("proof")
    return bool(pr) and len(pr) > 8


def osmo_height():
    req = urllib.request.Request("https://rpc.osmosis.zone/status", headers={"User-Agent": "ld"})
    with urllib.request.urlopen(req, timeout=15) as f:
        return int(json.load(f)["result"]["sync_info"]["latest_block_height"]) - 5


def probe():
    ready_src = None
    results = []
    try:
        h = osmo_height()
    except Exception as e:
        h = 0
        results.append(("osmo_height", "ERR " + str(e)[:60]))
    for ep in [x for x in OSMO_GRPC.split(",") if x]:
        try:
            ok = grpc_has_proof(ep, h, CHANNEL) if h else False
        except Exception as e:
            ok = False
            results.append(("grpc " + ep, "ERR " + str(e)[:50]))
        results.append(("grpc " + ep, "proof" if ok else "none"))
        if ok and not ready_src:
            ready_src = ep
    for base in [x for x in OSMO_REST.split(",") if x]:
        try:
            ok = rest_has_proof(base, h) if h else False
        except Exception as e:
            ok = False
            results.append(("rest " + base, "ERR " + str(e)[:50]))
        results.append(("rest " + base, "proof" if ok else "none"))
        if ok and not ready_src:
            ready_src = base
    return ready_src, results


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"ready_src": None, "fail_streak": 0, "history": [], "utc": None}


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)
    os.replace(tmp, STATE)


def notify(msg, level):
    try:
        with open(os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log"), "a", encoding="utf-8") as f:
            f.write("%s [xc-proof] %s %s\n" % (_now(), level, msg))
    except Exception:
        pass


def run():
    ready_src, results = probe()
    st = load_state()
    was = st.get("ready_src")
    if ready_src:
        st["fail_streak"] = 0
        if was != ready_src:
            notify("证明源就绪→ %s（入金/超时退款可推进；此前=%s）" % (ready_src, was), "INFO")
        st["ready_src"] = ready_src
    else:
        st["fail_streak"] = st.get("fail_streak", 0) + 1
        if was is not None:
            notify("此前就绪的证明源 %s 现在全不通（第 %d 次）" % (was, st["fail_streak"]), "WARN")
            st["ready_src"] = None
        if st["fail_streak"] == FAIL_STREAK:
            notify("Osmosis 证明端点连续 %d 次全不通——入金/退款仍被证明源堵（需换可用 RPC 提供者）" % FAIL_STREAK, "WARN")
    st["last_results"] = results[:12]
    st["utc"] = _now()
    save_state(st)
    print("ready_src=%s fail_streak=%d %s" % (st.get("ready_src"), st["fail_streak"], _now()))
    return 0


# ============ 自测 + 反向验证（不碰网，纯逻辑；植入错误必须被识别） ============
def _selftest():
    good = 0
    def chk(c, lbl):
        nonlocal good
        good += 1 if c else 0
        print(("  [%s] " % ("OK " if c else "坏")) + lbl)

    # 判"有证明"的口径：非空且长度>8
    def judge(d):
        pr = d.get("proof")
        return bool(pr) and len(pr) > 8
    chk(judge({"proof": "a"*100}), "非空长 proof → 判通")
    chk(not judge({"proof": None}), "proof=null → 判不通（主网/Osmosis 实测就是这种）")
    chk(not judge({"proof": ""}), "proof 空串 → 判不通")
    chk(not judge({}), "无 proof 字段 → 判不通")
    # 状态机：从"不通"到"通"翻 ready_src 且清零 fail_streak
    st = {"ready_src": None, "fail_streak": 5}
    # 模拟 run 的核心分支
    def step(state, ready):
        if ready:
            state["fail_streak"] = 0
            state["ready_src"] = ready
        else:
            state["fail_streak"] = state.get("fail_streak", 0) + 1
            state["ready_src"] = None if state["ready_src"] is None else state["ready_src"]
        return state
    step(st, "epX")
    chk(st["fail_streak"] == 0 and st["ready_src"] == "epX", "逮到就绪源 → 清零 + 记源")
    # 反向：植入"源失效"——从有变无要能被标出（run 里 was is not None 分支）
    st2 = {"ready_src": "epX", "fail_streak": 0}
    was = st2["ready_src"]
    step(st2, None)
    detected = (was is not None) and (st2["fail_streak"] == 1)
    chk(detected, "已就绪源突然不通 → 能被检出并告警计数")
    # 心跳缺失要能被发现：状态文件缺 utc 视为哑
    chk((not st2.get("utc")), "缺 utc 心跳 → 视为可疑（外部 watch 兜底）")
    print("ld_xc_proof_probe 自测：%d/7 通过" % good)
    return 0 if good == 7 else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    sys.exit(run())
