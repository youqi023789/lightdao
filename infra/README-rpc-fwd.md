# infra/ld_rpc_fwd.py — 网关本机 RPC 应急转发

## 它是什么

网关本机 `127.0.0.1:26657` 不一定是本机 `lightdao-mainnet` 节点。当本机节点缺位或落后时
（2026-11-10 至 11-14 就是这种情况，见 `docs/GW_LOCAL_NODE_DOWN_TRIAGE_20261114.md`），
`ld_rpc_fwd.service` 把回环 26657 纯 TCP 转发到一台**远端健康验证者**，让结算签名、跨链探针、
巡检等内部工具继续拿到实时链数据。HTTP 与 WebSocket 都透传，协议无关。

**它不是健康标志。** 巡检看到 `127.0.0.1:26657` 出块正常，只说明"远端那台健康"，
不代表网关自己有节点。网关自己那一台是否恢复，要看
`systemctl is-active lightdao-mainnet` 和它的 block 数据是否在长。

## 为什么源码里没有地址（2026-11-16 改造）

现场版把远端验证者公网 IP 硬编码在 `UP = (...)` 里。仓库的 pre-push 泄露门禁
（`.git/hooks/pre-push` → `/usr/local/bin/repo_leak_check.py` + `repo_leak_history.py`）
以 `/etc/lightdao/leak_ips.txt` 为黑名单，原样入库必被拦，
这也是 `docs/GW_LOCAL_NODE_DOWN_TRIAGE_20261114.md` 第 52 行当时否决"直接补进 infra/"的原因。

入库版改成从配置读取，源码零地址：

| 来源（按优先级） | 键 | 说明 |
|---|---|---|
| 环境变量 | `LD_RPC_FWD_UP` | `host:port`，空格/逗号分隔可配多台轮询 |
| 环境变量 | `LD_RPC_FWD_HOST` / `LD_RPC_FWD_PORT` | 与上一行等价，二选一 |
| `/etc/lightdao/hosts.env` | 同上 | systemd 经 `EnvironmentFile` 注入；脚本也会自己兜底读 |
| 环境变量 | `LD_RPC_FWD_LISTEN_HOST` / `LD_RPC_FWD_LISTEN_PORT` | 默认 `127.0.0.1:26657` |

两者都拿不到 → **拒绝启动**（fail closed），不猜默认值，避免静默转到错误节点。
`LD_RPC_FWD_LISTEN_HOST` 只允许回环地址，填公网/`0.0.0.0` 直接退出——把 RPC 暴露到公网属变更，需另行授权。

## 上线步骤（需要人工执行，本次巡检未动生产）

1. 往 `/etc/lightdao/hosts.env`（保持 `root:ubuntu 640`）追加一行：
   `LD_RPC_FWD_UP=<健康验证者IP>:26657`，建议配两台空格分隔以消掉单点依赖。
2. 把 `infra/ld_rpc_fwd.py` 复制到 `/usr/local/bin/ld_rpc_fwd.py`。
   **先备份现场版**：`cp -a /usr/local/bin/ld_rpc_fwd.py{,.bak-upstream-env-<日期>Z}`。
3. `systemctl daemon-reload && systemctl restart lightdao-rpc-fwd`
   （重启的是这个转发器，不是验证者节点，也不碰 `lightd`）。
4. 验证：`curl -s 127.0.0.1:26657/status | jq .result.sync_info.latest_block_height` 在推进；
   日志出现 `ld_rpc_fwd: 127.0.0.1:26657 -> 2 upstream(s)`，且不含任何地址明文。

## 撤回

本机主网节点追平后：`systemctl stop lightdao-rpc-fwd && systemctl restart lightdao-mainnet`，
再确认 `127.0.0.1:26657` 由本机节点应答。

## 已知遗留

- 现场版仍是单点上游（一台验证者）。配两台即可消掉，无需改代码。
- 转发器自身没有独立健康探针；它的可见性靠巡检读 `/home/ubuntu/ld_alerts.log` 的
  「勿当健康」WARN 行。
