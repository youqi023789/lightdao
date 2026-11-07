# 泄露门禁 ALERT 分诊 / Leak-Gate ALERT Triage — 2026-11-07（UTC）

本轮（自走执行器 2026-11-07 20:00Z 档）对 ld_alerts.log 里 11-07 的 7 条 ALERT 逐条定位根因。
本文件只覆盖两条 `repo-leak-check`，其余给出结论与去处，避免下一轮重复挖。

## 1. 结论速览

| ALERT（UTC） | 判据 | 根因 | 生产影响 | 状态 |
|---|---|---|---|---|
| 02:11:57Z `repo-leak-check: 1 unwaived finding(s) in <repo>` | 第一层（工作树） | 一次人工/会话期临时写入被门禁抓到，随后该文件被删或加豁免 | 无（07:15 定时扫描当日每一次 `findings=0`） | 已消解 |
| 18:11:09Z `repo-leak-check: 10 unwaived finding(s) in /tmp/ld_infra_wt_20261108` | 第一层（临时 worktree） | 本地分支 `ops/infra-audit-scripts-20261108` 的临时 worktree 内**未跟踪的网关脚本副本**含明文口令/密钥形态串 | 无（worktree 已不在；该分支从未推出，`origin/main..` 该分支仍差 1 个提交） | 门禁按设计拦下，infra/ 补录事项**处于被阻断状态** |
| 07:45:01Z `[miner-watch] 第 56 天矿工掉了 2 人（阈值 2）` | 矿工留存 | 真实掉线：55 天 8 人 → 56 天 6 人（两个地址退出） | 结算不受影响：56 天已 finalize 且 root 已签 | 非系统故障，属运营侧（需人工触达，执行器不动手） |
| 08:30:11Z `XCHAIN 探针自报读数缺口：主网出现了 1 个 IBC 轻客户端` | 面板文案 vs 链上事实 | 面板仍写"主网跨链未开通"，链上已有轻客户端 → 判据过期，不是生产异常 | 无 | 已由 11-07 提交把面板改为现查链上（见 `docs/IBC_MAINNET_EVIDENCE.md`） |
| 15:00 / 15:30 / 16:00Z `XCHAIN ... 通道已 OPEN 但 lightdao-ibc-mainnet.service=inactive` | 中继活性 | 通道先开、中继进程后起；服务 16:28:54Z 起 active，之后每条 XC-MN-WATCH 均"服务 active、通道 OPEN、两侧出块、backlog=0" | 窗口内无在途积压（backlog=0） | 已消解；16:00 之后无复发 |
| 11-06 04:09:13Z（及更早）`deploy gates drifted ... 1 drift` | 部署门禁与仓库漂移 | 已由 11-07 提交补上"门禁跑的是哪一版"这张网 | 无 | 11-07 全天无复发 |

## 2. 对两条泄露 ALERT 做的验证（不是转述）

1. 第一层当日定时结果：`/var/log/ld_repo_leak.log` 今天每次运行都是 `infra_ips=19 waivers_live=3 expired=0 waived_hits=3 findings=0 → REPO LEAK OK`，即"02:11 那条"在当前工作树里已不存在。
2. 已发布历史侧写：取 `origin/main` 最近 30 个提交里每个改动文件在该提交下的 blob，落盘到 `/tmp/ld_hist_probe_20261107T2012Z`（150 个文件，5.8 MB，保留可回溯，未删除），用 `LD_LEAK_NO_ALERT=1` 扫描 → `findings=0`。结论：02:11 的内容没有进入已发布历史（近 30 个提交范围内）。
3. 分支侧写：`ops/infra-audit-scripts-20261108` 已提交的三个 `infra/` 脚本单独抽出扫描 → `findings=0`；故 10 条命中来自 worktree 里**未跟踪**的网关脚本副本，不是那三个已提交文件。worktree 目录已不存在，本地分支仍未推出。

## 3. 遗留缺口（本轮只记录，不动手）

- 第二层（待推提交扫描）只挂在 `.git/hooks/pre-push`，fail-closed 逻辑本身正确；但 `.git/hooks` 不在版本控制里，换机器/新克隆不会带上这道钩子。建议后续把钩子内容纳入仓库并配一条可读的安装说明，属于工程项而非紧急项。
- worktree / 临时目录不在任何定时扫描范围内，这类"补录 ops 脚本"的工作只有在 push 时才会被兜住。约定：人工或会话期对临时目录跑门禁时统一带 `LD_LEAK_NO_ALERT=1`（脚本注释里已有的开关，只抑制写日志，退出码不变），避免把告警面刷脏。
- 矿工留存阈值 2 在 6–8 人规模下比较敏感（11-01 以来 52、53、56 天各触发过）。是否调整属运营判断，执行器不改判据。
- infra/ 补录事项在泄露分诊完成前保持阻断：每条命中要么删掉明文，要么进 `/etc/lightdao/leak_allow.json` 写理由和 `review_by`（豁免会过期是设计）。

## 4. 复现命令（只读）

```
sudo python3 /usr/local/bin/repo_leak_check.py <repo>          # 第一层：工作树
LD_LEAK_NO_ALERT=1 sudo python3 /usr/local/bin/repo_leak_check.py <dir> --json   # 对临时目录扫描且不写告警
git -C <repo> log --oneline origin/main..ops/infra-audit-scripts-20261108        # 确认未推出的范围
```
