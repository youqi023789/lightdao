# 链上合约字节码台账（code ↔ 源码 ↔ 可复现性）

最后核对：2026-10-16（网关本机 `wasmd q` + 节点 wasm 存储实测，非记忆）

## 为什么要这张表

CosmWasm 的 `store code` 只要把字节码丢上链就会拿到一个 `code_id`，**不要求提交源码，
也不校验来源**。这意味着"治理投票通过 → 合约迁移到新代码"这条路上，如果那份字节码
没有对应源码，等于把资金规则交给一份没人能审的二进制。本链已经真实发生过：
提案 #14/#15 投票通过、目标 code 18 的校验和在本机与仓库产物清单里都找不到，
最后是靠执行失败才没出事。

## 现状：链上 20 个 code 全部回捞并核对

对每个 code 做了三件事：① 从节点的 wasm 存储里按校验和找回文件；② 反算 `sha256(文件)`
与链上校验和双向核对（20/20 一致）；③ 用"源码里 ≥18 字符的英文字面量有多少原样出现在
字节码里"给每个 code 找最匹配的源码 crate（命中数/该 crate 长句总数）。

| code | 在用它的是 | 实例 | 上传者 | 能改吗（admin） | 源码命中 | 产物文件 |
|---|---|---|---|---|---|---|
| 1 | light_token | 1 | 运维 deployer 地址 | 无 admin＝永久不可改 | 0/0（该 crate 无长句可比） | `code1_light_token.wasm` |
| 2 | 无（孤儿） | 0 | deployer | — | 11/16 mining_reward | `code2_mining_reward.wasm` |
| 3 | 无（孤儿） | 0 | deployer | — | 3/12 governance | `code3_governance.wasm` |
| 4 | treasury_multisig（金库多签） | 1 | deployer | governance | 2/2 | `code4_treasury_multisig.wasm` |
| 5 | subtoken_factory | 1 | deployer | governance | 2/2 | `code5_subtoken_factory.wasm` |
| 6 | oracle_twap（价格喂价） | 1 | deployer | governance | 3/3 | `code6_oracle_twap.wasm` |
| 7 | anti_fraud | 1 | deployer | governance | 1/1 | `code7_anti_fraud.wasm` |
| 8 | validator_registry | 1 | deployer | governance | 3/3 | `code8_validator_registry.wasm` |
| 9 | vesting | 1 | deployer | governance | 2/3 | `code9_vesting.wasm` |
| 10 | insurance_fund | 1 | deployer | governance | 2/2 | `code10_insurance_fund.wasm` |
| 11 | 无（孤儿） | 0 | deployer | — | 3/12 governance | `code11_governance.wasm` |
| 12 | mining_reward（挖矿发币） | 1 | deployer | governance | 11/16 | `code12_mining_reward.wasm` |
| 13 | governance（治理本体） | 1 | 治理模块账户 | 自身 | 5/12 | `code13_governance.wasm` |
| 14 | 无（孤儿） | 0 | 治理模块账户 | — | 3/12 governance | `code14_governance.wasm` |
| 15 | 无（孤儿） | 0 | 治理模块账户 | — | 11/16 mining_reward | `code15_mining_reward.wasm` |
| 16 | vesting-v2-wp54 | 1 | 治理模块账户 | 无 admin＝永久不可改 | 1/3 vesting | `code16_vesting-v2.wasm` |
| 17 | ecosystem-fund-wp53（生态基金） | 1 | 治理模块账户 | 无 admin＝永久不可改 | 1/3 vesting | `code17_ecosystem_fund.wasm` |
| 18 | 无（孤儿，#14/#15 的目标） | 0 | 治理模块账户 | — | 3/12 governance | `code18_governance.wasm` |
| 19 | 提案 #17 准备把 governance 迁来 | 0 | deployer | —（还没有实例） | 5/12 | `code19_governance.wasm` |
| 20 | 提案 #17 准备把 mining_reward 迁来 | 0 | deployer | —（还没有实例） | 12/16 | `code20_mining_reward.wasm` |

"上传者"两类的区别很重要：

- **治理模块账户**＝这份字节码是经治理提案 `MsgStoreCode` 上链的，提案号、投票记录、
  执行结果都在链上，任何第三方都能复核。
- **deployer 运维地址**＝有人直接在节点上跑了一次 `tx wasm store`。合法存在
  （链参数 `code_upload_access=Everybody`），但它绕过了治理留痕，事后只能靠这份台账对账。
  code 1–12、19、20 都属于这类。

## 门禁（执行点 + 检测点 + 告警 + 测试）

- 预检：`python3 /usr/local/bin/ld_migrate_gate.py check <code_id> [目标合约]`
  —— 提 migrate 之前跑，非 0 就不许提。
- 监控：root cron 每小时第 37 分跑 `watch`，只看"还能改变结果"的提案
  （投票中，或已通过但链上合约的 `code_id` 还没变成目标值）。
- 判定三档：`OK` 产物在清单里且 BUILDLOG 写明可复现；
  `WARN/跟踪例外` 产物已登记但缺构建记录（带解除日期，默认 2026-11-30，到期未补就升级为硬失败）；
  `FAIL` 校验和不在 `contracts/wasm/SHA256SUMS` 里 → 退出码 1 并写 `/home/ubuntu/ld_alerts.log`。
- 查不到链上数据必须非零退出（rc=3/4），不允许"没查成"被当成"没问题"。
- 反向验证（植入假故障，2026-10-16 做过）：把 code 19 从清单里删掉 → 报
  `FAIL code 19 不在仓库产物清单里（无源可查，禁止迁移到 governance）` 且 rc=1、告警 +1 行；
  删掉 BUILDLOG → code 20 报 `有产物但无构建记录` 且 rc=1。健康态 rc=0 且不多写告警。
- 门禁自身被 `ld_gate_watch.py` 盯：哈希记在 `infra/gate_manifest.txt`，
  与线上部署不一致就告警。

## 还没解决的部分（诚实记录）

1. **不可复现——已用 CI 实测坐实（不再是推断）**：2026-10-16 起仓库带一条
   `.github/workflows/wasm-repro.yml`，用当年同一套配方（rustc 1.85.0 +
   `wasm32-unknown-unknown` + `wasm-opt --mvp-features -O3`）在 GitHub 托管 runner 上
   重新构建全部合约，再由 `infra/ci_wasm_compare.py` 与"链上归档字节码"逐字节比对。
   第一次实测结果：**比对 20 项，一致 0、不一致 18、未产出 2**（未产出的两项就是下面第 2 条
   说的 code 16/17 没有源码 crate）。也就是说包括正在投票的 #17 目标 code 19/20 在内，
   **链上跑的每一份合约代码目前都无法从仓库源码重跑出同样的 sha256**。
   结论可公开复核：`curl -s https://api.github.com/repos/youqi023789/lightdao/actions/runs?per_page=1`
   取最新 run，再读它的 `/jobs` 与 `/check-runs/{job_id}/annotations`（公开仓库无需凭据）。
   差异到底来自哪里（10-16 CI 实测，已排除一个常见猜测）：本次 CI 解析出的依赖版本是
   `cosmwasm-std=2.3.6`，**与链上二进制里嵌的版本完全一致**，所以字节差异不是【依赖没锁定】造成的
   （没有 `Cargo.lock` 仍然是要补的隐患，但它不是本次不一致的原因）。剩下的可能只有两类：
   ① 工具链差异（当年构建机的 rustc patch 版与 binaryen/wasm-opt 版本已随机器退订无法追回）；
   ② **仓库源码与当年编出这些字节的那份源码不是同一状态**——这条嫌疑最大，因为 code 19/20 是
   10-13/10-14 在另一台机器上编的，而引入 `migrate_v5_updatable_config`、`validators must not be
   empty` 等字面量的提交 `b01987c` 时间是 10-14 05:47Z，晚于 code 20 的上链时刻 10-14 03:12Z：
   先编、后提交，源码快照与产物之间没有可核对的绑定关系。
   因此本台账的口径改为：**历史 code 1-20 一律按【无法从仓库源码复现】处理**（不再归因于依赖），
   可复现性只对【以后】负责——以后必须先跑 workflow 拿到 sha256、把 source_commit 与 toolchain
   一起写进 BUILDLOG 并核对链上校验和一致，才允许提 migrate。CI 每次把生成的 `Cargo.lock`
   作为构件保留 30 天，锁定依赖这件事照做，只是不再把它当成本次差异的解释。
   **下一步口径**：以后任何新 store 之前先跑这条 workflow，把它产出的 sha256 写进
   `SHA256SUMS` 与 `BUILDLOG.tsv`（`reproducible=yes` + `source_commit` + `toolchain`），
   再核对链上校验和一致才提 migrate；比对脚本对"声称 yes 却复现不出"直接判红。

2. **code 16 / 17 的源码归属**：仓库里没有 `vesting-v2` 与 `ecosystem_fund` 两个 crate，
   它们与 `vesting` crate 只命中 1/3 长句。这两个合约 admin 为空＝永久不可改，
   其中 17 号是生态基金（管钱）。需要补出对应的源码目录，或把"它由 vesting 源码加什么
   改动而来"写清楚。
3. **light_token（code 1）无法用长句比对**：该 crate 源码里没有 ≥18 字符的英文字面量，
   命中 0/0 不等于对得上，也不等于对不上——需要正式复现构建才能判。
4. **孤儿 code 6 个**（2、3、11、14、15、18）：链上没人用但永久占着状态。清理需要治理
   决定（本链无 `forget_code` 类操作），暂不处理，只登记。

## 以后新增/迁移合约的硬流程

1. 在**有工具链的机器**上按 `contracts/scripts/build_normalize.sh` 构建；
2. 产物提交进 `contracts/wasm/`，同时向 `SHA256SUMS` 与 `BUILDLOG.tsv` 各追加一行
   （`source_commit`、`toolchain`、`reproducible=yes` 三样必须齐，脚本已会自动写）；
3. 走**治理提案** `MsgStoreCode` 上链（别再用运维地址直接 store）；
4. 链上确认校验和与登记值逐字节一致后，再提 `MsgMigrateContract`；
5. 提之前跑一次 `ld_migrate_gate.py check`，非 0 不许提。
