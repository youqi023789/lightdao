# 泄露自查门禁 / Repository Leak Gate

> 中文摘要在文末。

## Why this exists

This repository is public from day one, and a transparency-first workflow occasionally commits
operational detail it should not: commit `70be67e` removed infrastructure addresses, key file names
and an operator machine path that had been committed by mistake. Nothing was abused as a result, but
"nothing happened" is luck, and luck is not a control.

`repo_leak_check.py` is the control. It walks a working tree and fails when it finds anything that
must never be public.

## What it looks for

| class | shape |
|---|---|
| `infra-ip` | any address listed in the private sidecar (see below) |
| `private-key` | PEM headers |
| `mnemonic-phrase` | 12–24 consecutive BIP39-shaped words |
| `discord-webhook` | `discord.com/api/webhooks/<id>/<token>` |
| `bearer-token` | `Bearer <25+ chars>` |
| `inline-secret` | `secret|token|passphrase|password|api_key = "<12+ non-space chars>"` (placeholders and shell expansions are excluded so the rule keeps its teeth without drowning in noise) |
| `local-desktop-path` | operator machine home / desktop paths — drive-letter and POSIX spellings. Not written out literally here: this document would then trip the rule it documents, and a gate that needs an exemption for itself is not a gate. |
| `keyring-file` | committed Cosmos keyring entries |

## Two-file design (important)

The infrastructure address list is **never** stored in the repository — a scanner that lists the
addresses it protects would itself be the leak.

* `/etc/lightdao/leak_ips.txt` — `root:ubuntu 640`, one address per line, `#` comments allowed.
* `/etc/lightdao/leak_allow.json` — `root:ubuntu 640`, waivers (see below).
* `/usr/local/bin/repo_leak_check.py` — the scanner, safe to publish.

If the IP sidecar is missing the scanner says so and continues with the other classes; it does not
silently pretend the address check ran.

## Waivers expire, by design

Every known false positive needs an entry in the allowlist with a `reason` **and** a `review_by`
date. An expired waiver stops applying. That is deliberate: a permanent allowlist is how a real leak
ends up hidden under a pile of "we always knew that one was fine".

Current waivers (test vectors and a throwaway sandbox credential) are in
`leak_allow.sample.json`; the live file lives outside the repo.

## Where it runs

1. **Daily, 07:15 UTC** — root crontab refreshes the working copy, then scans it. A finding appends
   one line to `/home/ubuntu/ld_alerts.log` and non-zero exit, so it pages like every other alarm.
2. **`pre-push` hook** in the operator's working copy — blocks a push that would publish a finding.

## Proving the gate still bites

A gate with an allowlist must be tested in *both* directions, otherwise a broken regex and a
fully-waived tree look identical. `leak_proof.py` copies the tree to a scratch directory, plants one
synthetic finding per class, and asserts all of them are reported:

```
$ python3 /home/ubuntu/leak_proof.py /home/ubuntu/repo
findings=7 … classes expected: 7  missing: none
PROOF OK: planted leaks in all 7 classes were caught
```

---

## 中文摘要

这个仓库从第一天起就是公开的，而"透明优先"的工作方式偶尔会把不该公开的运行细节提交上来：
`70be67e` 移除了一批被误提交的节点地址、密钥文件名与操作机本地路径。事后没有造成损失，但
"没出事"是运气，运气不是控制手段。
`repo_leak_check.py` 就是防止同类事故再发生的门禁：扫描工作树，命中「基础设施 IP / 私钥 / 助记词 /
webhook / Bearer / 内联明文口令 / 本机路径 / keyring 文件」任一形态即失败。

基础设施地址表**不进仓库**（否则门禁自身就成了泄露源），放在机器上的
`/etc/lightdao/leak_ips.txt`（属主 root，组 ubuntu，权限 640）。

白名单必须写理由并带复核到期日（`review_by`），过期即失效——避免"反正一直是误报"把真泄露埋掉。
门禁每天 07:15 UTC 跑一次（root crontab，失败写 `ld_alerts.log` 告警），并在推送前用 `pre-push`
钩子拦一道。双向验证脚本 `leak_proof.py` 会把每一类形态各造一条假样本种进临时副本，确认 7 类全部
被抓到才算门禁有效。

## 两层扫描（2026-10-16 补第二层）

第一层 `repo_leak_check.py` 扫**工作树**。这不够：只要"这一版写进去、下一版删掉再推"，
工作树就是干净的，而 GitHub 的历史 blob 公开可翻。实测本仓库就是这样漏的——
老网关的公网 IP 在最初的大提交 `9c9c239`（2026-09-26）里被写进多个文档，
后来 `5ef6e38`、`6f89189` 做了脱敏，工作树现在扫不出任何一条，但历史里仍然查得到。

第二层 `repo_leak_history.py` 扫**将要推出去的提交**：把每个待推提交的新增行落成临时文件，
交给同一个第一层门禁判定（不复制一份规则，避免两套规则各说各话）。pre-push 钩子
（版本化副本见 `infra/git-hooks-pre-push`）现在两道都跑，任一非零即拒绝推送；
连 `origin/main` 基线都取不到时也拒绝（fail closed，宁可拦错也不放过）。

### 反向验证（2026-10-16，全程在临时分支上做，没有推出去过任何东西）

- 提交里放一条假私钥头、文件仍留在工作树 → 被第一层拦下，报 `FINDING private-key`。
- 再把该文件覆盖成干净内容后推送 → 第一层输出 `REPO LEAK OK`，**第二层拦下**并点名那次
  提交（`aaf7b309`）；用 `git ls-remote` 确认远端没有收到该分支（返回 0 行）。
- 测完删除临时分支，并用 `git reflog expire --expire=now --all` 加 `git gc --prune=now`
  清掉本地游离对象。

### 历史里已经存在的那条老 IP

属于"已经公开"的既成事实。要彻底抹掉需要改写全部历史并强推（`git filter-repo` 之后
`git push --force`），代价是所有已克隆过的地方都要重新克隆，且历史提交号全部变化，
是否执行由所有者决定。若不处理，实际缓解手段是这台机器自身的暴露面已经收窄：
评分网关 8080 只绑 127.0.0.1（对外只留 nginx 的 `/gw`），SSH 仅密钥登录，
管理员口令已从 systemd 单元搬进 `EnvironmentFile`。

### 写文档/脚本时的一个自伤坑（本轮踩到）

带反引号或 `$` 的内容**不能**塞进未加引号的 heredoc（`<<PY`）：shell 会把反引号当命令替换执行，
结果文档里的代码片段被吃掉、还把一条命令的输出插进了正文。必须用 `<<'PY'`（定界符加引号），
或者像本节一样：本地写成文件、scp 上去、再由脚本按标记替换。
