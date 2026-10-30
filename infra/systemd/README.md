# infra/systemd —— 网关服务定义的异地副本

网关（HK 主网关）上三个 lightdao systemd unit 之前**只存在于 `/etc/systemd/system/`**，
仓库里没有。网关重装、迁移或磁盘故障时，仅靠 `infra/gateway.py`、`infra/signaling.py`、
`infra/turn-cred.py` 无法复原服务的端口、运行用户、环境变量注入方式和自动重启策略，
所以把它们纳进仓库。

| 文件 | 与现役一致性 | 说明 |
| --- | --- | --- |
| `lightdao-gateway.service` | 逐字节一致（sha256 5fb05b17712b） | GW_PORT=8080，密钥走 `EnvironmentFile=/etc/lightdao/gw_admin.env`，unit 内无明文密钥 |
| `lightdao-signaling.service` | 逐字节一致（sha256 a46619b514dd） | 只绑 127.0.0.1:8090 |
| `lightdao-turncred.service` | **TURN_SECRET 已脱敏为占位符** | 现役 unit 里是 644 明文，禁止把真实值提交进仓库 |

## 安装 / 复原

```bash
sudo cp infra/systemd/lightdao-*.service /etc/systemd/system/
# turncred 需先把 TURN_SECRET 改成 EnvironmentFile 注入，再替换占位符
sudo systemctl daemon-reload
sudo systemctl enable --now lightdao-gateway.service
```

## 待授权处置（本次巡检发现，未动手）

1. `/etc/systemd/system/lightdao-turncred.service` 以 **644 明文内嵌 TURN_SECRET**，
   本机任意用户可读。建议迁到 `/etc/lightdao/turn.env`（root:ubuntu 640）并改用
   `EnvironmentFile=`；生效需 `daemon-reload` + 重启该服务。
2. `/usr/local/bin/lightdao-{gateway,signaling,turncred}.service` 是 Sep 22–25 的三份陈旧副本，
   其中 gateway 那份内嵌一个 `GW_ADMIN_SECRET`。实测与现役 `/etc/lightdao/gw_admin.env`
   的值**不同**，判定为已废弃旧密钥；但它仍是"看起来像可用凭据"的诱饵，建议移入可恢复
   回收目录（不要直接删），并确认无脚本引用。
3. `qa_cross_cron.sh` 的 24h 补报去重已生效（`ld_cross_state.json` 06:17 生成），
   CROSS-FAIL 从每天 24 条降到 1 条。
