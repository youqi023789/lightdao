# 每日密钥备份连续 3 天归档为空：根因与处置窗口（2026-11-11 自走巡检）

本文全部数字为 2026-11-11 00:00–00:30 UTC 在网关实测，命令随条目给出；不含推断。

## 1. 现象

- `/home/ubuntu/backups/keys-10-7-42-113-2026-11-08/09/10.tar.gz.gpg` 均为 **217 字节**（空包），
  而 11-06 与 11-07 两份是 **11838 字节**：
  `sudo ls -l --time-style=full-iso /home/ubuntu/backups/keys-*.gpg`
- 在用备份脚本自己的判定就是坏的，`/home/ubuntu/ld_backup.log` 在 11-08、11-09、11-10 各打了一条：
  `FATAL-W: 0 .info entries archived - key backup NOT restorable, fix the keyring layout before relying on it`
  并写明 `inputs keyring=/root/.wasmd/keyring-test priv_validator_state=none`（实测该目录为空，`total 0`）。
- 真实密钥在 `/home/ubuntu/.wasmd/keyring-test`：**12 个 `.info`**（`ls | sed -E "s/.*\.//" | sort | uniq -c`）。
- `voters-2026-11-10.tar.gz.gpg` 为 65051 字节，六套投票 keyring 正常，不在本告警范围。

## 2. 根因：仓库已修，但修复没部署到在用路径

`diff /home/ubuntu/ld_backup.sh /home/ubuntu/repo/infra/ld_backup.sh` 只有单向新增（仓库新、在用旧）：

| 文件 | 字节 | mtime | 关键差异 |
|---|---|---|---|
| `/home/ubuntu/ld_backup.sh`（cron 在用） | 8318 | 2026-11-06 13:18Z | 无 `home_keyn()`/`HOMEKEYN`，WASMD_HOME 选择仍会命中空的 `/root/.wasmd/keyring-test`；无 `page()`；无 `prune_keys()` |
| `/home/ubuntu/repo/infra/ld_backup.sh` | 11368 | 2026-11-10 04:20Z | 候选按真实 `.info` 数选择、FATAL-W 上告警面、留存不再误删最后一份可用备份（即 68232d8） |

也就是说：11-07 之后 `/root/.wasmd` 冒出一个空的 `keyring-test`，在用的旧版脚本按目录 glob 选中了它，
于是每天 06:00Z 把"空 keyring"备份成 217 字节的"成功"归档。修复在 68232d8 已进仓库，但没有部署。

`ops-reconcile` 连续 4 天（11-07 起）报的 `ld_backup.sh 与仓库不一致或未入库` 就是这件事，
但它只说"不一致"，不区分漂移方向，也不区分"缺能力"和"缺修复"，所以这条 ALERT 一直没被当成备份失效来读。

## 3. 影响与硬期限

- 密钥恢复面：最后一份**可能可恢复**的自动归档是 `keys-10-7-42-113-2026-11-07.tar.gz.gpg`（11838B，2026-11-07 06:00:02Z）。
- 在用脚本第 165 行 `find "$DEST" -name "keys-*.tar.gz.gpg" -mtime +7 -delete`：该份会在 **2026-11-14/15 06:00Z 前后被自动删除**，
  此后归档目录里只剩 217B 空包。这是处置窗口，不是推测。
- 已超出自动备份覆盖的密钥：`t1x.info` mtime 2026-11-07 10:05:58Z 晚于 11-07 06:00Z 那份归档，
  即 `t1x` 从未进入任何自动 keys 归档。`relayer-main.info`（2026-11-06 00:11Z）在 11-06/11-07 两份里是覆盖到的。
- 唯一现存缓解：`/home/ubuntu/backups/manual-keep/keyring-ubuntu-10-7-42-113-2026-11-10T233146Z.tar.gz.gpg`
  （12554B，2026-11-10 23:31:46Z）。文件名字段像 ubuntu keyring 全量且大小与 11838B 归档同量级，
  但它由谁生成、口令是什么、是否真含 12 个 `.info`，本轮无法证明（无口令，未解密）。
  `manual-keep/` 不在 `keys-*` 删除 glob 下，所以不会被留存逻辑清掉。

## 4. 建议处置（需人工逐次批准，本轮未动手）

1. 部署已在仓库的修复（在用文件为 `ubuntu:ubuntu 775`，写入即可，不改 cron 行、不改 crontab）：
   `install -m 775 -o ubuntu -g ubuntu /home/ubuntu/repo/infra/ld_backup.sh /home/ubuntu/ld_backup.sh`
   部署前建议 `bash -n` 与人工读一遍 `page()` 的上报文案。
2. 部署后立即手动跑一次 `sudo /home/ubuntu/ld_backup.sh`，确认新归档回到万字节量级且不再打 FATAL-W；
   跑之前先把 11-07 那份 11838B 归档复制到 `manual-keep/`，避免留存逻辑在它被证明可用前就删掉它。
3. 人工验证 `manual-keep` 那份能否解密并含 12 个 `.info`（口令与来源不在本轮掌握范围）。
4. 判据侧补两条（都不涉及主网写）：
   - `ops-reconcile` 对 cron 在用脚本要输出漂移方向与"仓库有修复未部署"这一类，否则每天一条同文案没人接；
   - 备份脚本的 FATAL-W 必须同时进 `ld_alerts.log`（仓库版已加 `page()`，正是这条）。
   实测 `grep -a FATAL /home/ubuntu/ld_alerts.log` 为空 —— 连续 3 天密钥备份报废，告警面零感知。
