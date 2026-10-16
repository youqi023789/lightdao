# 收紧评分网关监听地址（8080 明文口）——待批准，未执行

日期：2026-10-16　提出：自动巡检　状态：**只测量完，没动生产**

## 现状与证据（全部实测，非推断）

| 事实 | 证据命令 | 结果 |
|---|---|---|
| 评分网关监听 `0.0.0.0:8080` | `sudo ss -ltnp \| grep 8080` | 公网可达，明文 HTTP |
| 绑定地址是写死的 | `grep -n ThreadingHTTPServer /usr/local/bin/gateway_v3.py` | 第 645 行 `("0.0.0.0", PORT)`，而同一行注释写着"浸泡只绑本机"＝注释与代码不一致 |
| 站点/节点都走 nginx 的 `/gw` 前缀 | `grep -o "CFG.gw" /var/www/lightdao/js/*.js`、仓库全文搜 `8080` | 站点 JS 用 `CFG.gw`（默认 `/gw`），仓库文档里没有任何一处提到 8080 |
| 矿工确实在用 `/gw`，不是直连 8080 | `tail -200000 /var/log/nginx/access.log` 计数 | 近 1 天：`/gw/v1/health` 10915 次、`/gw/v1/scores` 8712 次、`POST /gw/v1/heartbeat` 6250 次 |
| 当前没有外部连接到 8080 | `sudo ss -tn state established "( sport = :8080 )"` | 0 条 |
| 8080 上有一条要管理员口令的路由 | `sed -n '594,606p' gateway_v3.py` | `POST /v1/finalize` 校验 `X-Admin` 头 |

## 为什么值得收紧

`/v1/finalize` 需要管理员口令（`X-Admin` 头）。8080 是**明文 HTTP**，任何走 8080 的管理调用都会把口令以可读形式在网络上传输；同时它绕开了 nginx 的安全响应头与 `client_max_body_size` 限制。功能面没有增加（`/gw` 已经代理同样的路由），纯粹多开一个不受保护的入口。

## 建议改法（一行 + 一次重启）

```python
# gateway_v3.py 第 645 行
ThreadingHTTPServer((os.environ.get("GW_BIND", "127.0.0.1"), PORT), H).serve_forever()
```

配套：`systemctl edit lightdao-gateway` 里保留 `GW_PORT=8080` 不动，nginx 的 `proxy_pass http://127.0.0.1:8080` 已经指向本机，**不需要改 nginx**。

## 执行与回滚步骤（已写成 `infra/gw_bind_loopback.sh`，等用户在线时跑）

1. 备份 `/usr/local/bin/gateway_v3.py` 与 systemd 单元；
2. 打补丁 → `python3 -m py_compile` 自检，失败立即还原（这条是本项目老规矩：改发布/网关脚本必须带自检与自动还原）；
3. `systemctl daemon-reload && systemctl restart lightdao-gateway`（必须用 sudo，之前踩过 polkit 拒绝的坑）；
4. 验收三件事：`curl 127.0.0.1:8080/v1/health` 有 JSON；`https://lightdao.net/gw/v1/health` 有 JSON；`sudo ss -ltnp | grep 8080` 显示 `127.0.0.1:8080` 而不是 `0.0.0.0:8080`；
5. 观察 10 分钟：`/gw/v1/heartbeat` 的 POST 计数要继续涨（说明矿工没断）；
6. 任一步失败：还原备份 + 重启，并写告警。

## 风险与不做的代价

- 做的风险：网关重启的几秒内心跳请求会失败，客户端会重试（历史上重启过多次，未见丢分）；如果哪天有第三方工具直连 `:8080`，收紧后它会断——实测当前没有任何直连痕迹，且文档从未公布 8080。
- 不做的代价：管理员口令存在明文传输路径；多一个绕过 nginx 防护的入口。

## 另一件必须记在案上的事（同一次排查中发生）

本次为了确认服务配置执行了 `systemctl cat lightdao-gateway`，其输出包含
`Environment=GW_ADMIN_SECRET=…`，**该口令随会话记录被带出**（口令本身没被主动读取或存储，但出现在了输出里）。
处置建议：按轮换处理——生成新口令、写入 systemd 覆盖片段、同步改调用方（每日 finalize 的脚本/定时任务），
并复核 `X-Admin` 的比对方式（当前是明文相等比较，建议改成 `hmac.compare_digest` 防时序侧信道）。
轮换同样需要重启网关，因此与上面的收紧动作合并成一次变更更省。
