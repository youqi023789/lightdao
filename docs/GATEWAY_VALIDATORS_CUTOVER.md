# 网关 /v1/validators 切换手册（LD-VALIDATORS-20261015）

## 背景：为什么必须走网关
| 数据源 | 结论 |
|---|---|
| `127.0.0.1:1317`（LCD） | **是测试网进程 `lightd.testnet.bin` 的接口**，返回 `val-test-gas`、1000 LIGHT 之类测试网数据。主网节点 `app.toml` 里 `api.enable=false`，没有主网 LCD。接它 = 拿测试网数据冒充主网，禁止。 |
| `/rpc/validators`（CometBFT） | 只有共识层验证者（hex 地址 + voting power），**没有 `wasmvaloper1…` operator 地址、没有 moniker**，无法用于委托。 |
| 合约 `validator_registry.active_validators` | 实测返回 **`[]`**（登记册为空；主网 10 个验证者走原生质押）。 |
| `wasmd q staking validators --node 127.0.0.1:26657` | ✅ 唯一正确来源：operator 地址、moniker、tokens、jailed、commission 齐全。 |

## 已完成的浸泡验证（2026-10-15）
副本 `/home/ubuntu/gateway_v3_soak.py` 在 **127.0.0.1:8099**、使用**独立 data 副本**（`/tmp/gw3data`，不与生产共用 WAL）：

- 正向：`chain_id=lightdao-mainnet-1 count=10 bonded=10`，列出 `val01-jp / val02-kr / val04-us / val08-th / val10-br …`，`tokens=500000000000`（=50 万 LIGHT/个）。
- 反向（关键）：把 `GW_MAIN_RPC` 指向测试网 `127.0.0.1:26757` → **HTTP 503**，正文
  `RPC 链ID=lightdao-testnet-gas 与预期 lightdao-mainnet-1 不符，拒绝提供数据（可能误连测试网节点）`。
- 生产 `gateway_v2.py` md5 `adf83ea538c9559e482383b98be6620d` **全程未改动**。
- 前端 `app_2.js` 已在 v1.7.7 起优先请求 `/gw/v1/validators` 并**校验返回的 chain_id**，
  拿不到时如实显示原因 + 允许手动粘贴 `wasmvaloper1…`，不再出现"加载验证者失败"这种吞掉异常的说法。

## 为什么必须每次调用都校验 chain_id
本节点未开放 `/node_info`（实测 404），链 ID 只能从 `/status` 的 `result.node_info.network` 取。
第一版我按 `/node_info` 写守卫，结果**守卫从未真正执行过**（拿 404 当成"读不到"），
是实跑正反用例才暴露的。所以：**没被真实请求验证过的安全判断，视为不存在。**

## 切换步骤（须业主在线批准）
```bash
# 1) 备份 + 落地 v3（内容 = v2 + /v1/validators + 模块级 validators_snapshot()）
sudo cp -a /home/ubuntu/gateway_v2.py /home/ubuntu/gateway_v2.py.bak-$(date +%Y%m%dT%H%M%SZ)
sudo cp -a /home/ubuntu/gateway_v3_soak.py /usr/local/bin/gateway_v3.py
#    注意：生产要公网可达，必须把绑定地址从 127.0.0.1 改回 0.0.0.0（仅这一处差异）
sudo sed -i 's/ThreadingHTTPServer(("127.0.0.1", PORT)/ThreadingHTTPServer(("0.0.0.0", PORT)/' /usr/local/bin/gateway_v3.py

# 2) 切 systemd ExecStart（沿用 drop-in 机制，可一键回滚）
printf '%s\n' '[Service]' 'ExecStart=' 'ExecStart=/usr/bin/python3 /usr/local/bin/gateway_v3.py' \
  | sudo tee /etc/systemd/system/lightdao-gateway.service.d/v3.conf >/dev/null
#    确认 EnvironmentFile 仍被继承（GW_ADMIN_SECRET / GW_DATA / GW_GENESIS 不得丢失）
sudo systemctl daemon-reload && sudo systemctl restart lightdao-gateway

# 3) 验收（三条都要过，任一不过立刻回滚）
curl -s https://lightdao.net/gw/v1/validators | head -c 160   # 期望 chain_id=lightdao-mainnet-1, bonded=10
curl -s https://lightdao.net/gw/v1/health | head -c 80        # 期望 ok:true
python3 /home/ubuntu/ld_render_watch.py                        # 期望全部通过
```

## 回滚
```bash
sudo rm -f /etc/systemd/system/lightdao-gateway.service.d/v3.conf
sudo systemctl daemon-reload && sudo systemctl restart lightdao-gateway
curl -s https://lightdao.net/gw/v1/health | head -c 80
```

## 切换后收尾
- 停掉浸泡实例（按端口处置，勿用 `pkill -f gateway_v3_soak`——它会连执行命令的会话一起匹配杀掉，已踩过）：
  `kill $(ss -lntpH "sport = :8099" | grep -oE "pid=[0-9]+" | head -1 | cut -d= -f2)`
- 把 `g11`/渲染巡检纳入的告警通道保持观察 24h。

## 仓库推送通道现状（2026-10-15 实测）
HK 无 GitHub 凭据，且 HK→sg-old 无互信密钥（scp 直接被拒），所以推送只能在【本机】编排：
[1/4] HK 打 bundle（仅快进、绝不 force）。
sg-old 于 10-18 退役，届时必须先在 HK 配好 gh auth 或 GitHub Deploy Key，否则提交推不出去。
先前入库的  假设可在 HK 跑，是错的，已改为废弃指针脚本并在此收回。
