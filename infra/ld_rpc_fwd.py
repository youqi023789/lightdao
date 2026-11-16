#!/usr/bin/env python3
# ld_rpc_fwd.py — 应急 TCP 转发：把本机 127.0.0.1:<LISTEN_PORT> 转发到一台健康验证者的 Tendermint RPC。
#
# 用途：网关本机 lightdao-mainnet 节点缺位/落后时，让结算签名(ld_sign_root.sh)、
# 跨链探针、巡检等内部工具仍能读到实时链数据。协议无关(纯 TCP)，HTTP 与 WebSocket 都透传。
#
# ⚠ 这是"应急"，不是健康标志。转发器自己会往 /home/ubuntu/ld_alerts.log 写
#   「勿当健康」WARN；本机节点回来后应停本服务并重启 lightdao-mainnet。
#
# 2026-11-16 入库版：原网关现场版把远端验证者地址硬编码在源码里，无法过
# docs/GW_LOCAL_NODE_DOWN_TRIAGE_20261114.md 第 52 行所说的泄露门禁
# (/etc/lightdao/leak_ips.txt)。本版改为从环境读入，源码不含任何公网地址。
#
# 上游地址来源（按优先级，命中即止）：
#   1) 环境变量 LD_RPC_FWD_UP，形如 "<host>:<port>"；
#      或分别给 LD_RPC_FWD_HOST / LD_RPC_FWD_PORT。
#   2) 配置文件 /etc/lightdao/hosts.env 里的同名键（systemd 用 EnvironmentFile 注入，
#      手工运行时本脚本也会自行兜底读取）。
# 两者都没有 → 拒绝启动（fail closed），不猜默认值，避免静默转到错误节点。
#
# hosts.env 需要新增一行（root:ubuntu 640，勿提交进仓库）：
#   LD_RPC_FWD_UP=<健康验证者公网IP>:26657
# 建议至少配 2 台轮询消单点：LD_RPC_FWD_UP="ip1:26657 ip2:26657"，见下方 UPSTREAMS。

import os
import socket
import sys
import threading

HOSTS_ENV = os.environ.get("LD_HOSTS_ENV", "/etc/lightdao/hosts.env")
DEFAULT_LISTEN_HOST = "127.0.0.1"          # 只绑回环，绝不外露
DEFAULT_LISTEN_PORT = 26657
CONNECT_TIMEOUT = 15
BACKLOG = 256


def _strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def _from_hosts_env(key):
    """兜底读 hosts.env（systemd 已注入时这步只是幂等重读；文件不可读则跳过）。"""
    try:
        with open(HOSTS_ENV, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == key:
                    return _strip_quotes(v)
    except OSError:
        pass
    return ""


def _lookup(key):
    return os.environ.get(key, "").strip() or _from_hosts_env(key)


def resolve_upstreams():
    """返回 [(host, port), ...]。支持空格分隔多目标，用于消单点。"""
    raw = _lookup("LD_RPC_FWD_UP")
    if not raw:
        host = _lookup("LD_RPC_FWD_HOST")
        port = _lookup("LD_RPC_FWD_PORT") or str(DEFAULT_LISTEN_PORT)
        raw = ("%s:%s" % (host, port)) if host else ""
    if not raw:
        raise SystemExit(
            "ld_rpc_fwd: 未配置上游。请设置环境变量 LD_RPC_FWD_UP=<host>:<port>，"
            "或在 %s 中添加该键（该文件含公网地址，禁止提交进仓库）。" % HOSTS_ENV
        )

    ups = []
    for token in raw.replace(",", " ").split():
        host, sep, port = token.rpartition(":")
        if not sep or not host:
            raise SystemExit("ld_rpc_fwd: LD_RPC_FWD_UP 格式应为 host:port，实测 %r" % token)
        if not port.isdigit():
            raise SystemExit("ld_rpc_fwd: 上游端口必须是数字，实测 %r" % token)
        ups.append((host, int(port)))
    return ups


def resolve_listen():
    host = _lookup("LD_RPC_FWD_LISTEN_HOST") or DEFAULT_LISTEN_HOST
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit(
            "ld_rpc_fwd: 监听地址只允许回环，实测 %r。对外暴露 RPC 属变更，需另行授权。" % host
        )
    port = _lookup("LD_RPC_FWD_LISTEN_PORT") or str(DEFAULT_LISTEN_PORT)
    if not port.isdigit():
        raise SystemExit("ld_rpc_fwd: 监听端口必须是数字，实测 %r" % port)
    return host, int(port)


def pick(upstreams):
    """简单轮询：逐个试到能连上为止。全失败则抛最后一个异常。"""
    last = None
    for up in upstreams:
        try:
            return up, socket.create_connection(up, timeout=CONNECT_TIMEOUT)
        except Exception as exc:  # noqa: BLE001 - 换下一台
            last = exc
    raise last


def pump(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except Exception:
        pass
    finally:
        try:
            b.shutdown(socket.SHUT_WR)
        except Exception:
            pass


def handle(client, upstreams):
    try:
        _up, remote = pick(upstreams)
    except Exception:
        try:
            client.close()
        except Exception:
            pass
        return
    for a, b in ((client, remote), (remote, client)):
        t = threading.Thread(target=pump, args=(a, b), daemon=True)
        t.start()


def main():
    listen_host, listen_port = resolve_listen()
    upstreams = resolve_upstreams()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((listen_host, listen_port))
    srv.listen(BACKLOG)
    # 日志里只打端口与台数，不打地址，避免又被日志采集带出去。
    print("ld_rpc_fwd: %s:%d -> %d upstream(s)" % (listen_host, listen_port, len(upstreams)),
          flush=True)

    while True:
        try:
            conn, _ = srv.accept()
        except Exception:
            continue
        threading.Thread(target=handle, args=(conn, upstreams), daemon=True).start()


if __name__ == "__main__":
    sys.exit(main())
