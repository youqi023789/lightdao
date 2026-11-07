# Code-ID 溯源核对（审计前置 / B6 blocker 收窄）— 2026-11-06

生成方式：`python3 infra/ld_codeid_provenance.py --instances`（只读，仅 `wasmd q`，不发任何 tx、不写链）。
数据源：主网关 RPC `http://127.0.0.1:26657`，网络 `lightdao-mainnet-1`。
对照物：`contracts/wasm/*.wasm` 与 `contracts/wasm/BUILDLOG.tsv`。

## 1. 结论

**链上 20 个 code-id（1–20）全部与仓库内一份 wasm 产物逐字节相等（sha256 20/20 MATCH，0 problem）。**

这把 `docs/AUDIT_RFQ_FORMAL_VERIFICATION.md` 里 blocker ① 的表述需要拆开看：

- blocker ① 原表述"code 16/17 在仓库里没有源 crate"——**产物层面已不成立**：
  `code16_vesting-v2.wasm`、`code17_ecosystem_fund.wasm` 就在 `contracts/wasm/`，且与链上 checksum 完全一致。
  仍然成立的部分只有"源码 crate 缺失"：`contracts/contracts/` 目前 10 个 crate
  （anti_fraud / governance / insurance_fund / light_token / mining_reward / oracle_twap /
  subtoken_factory / treasury_multisig / validator_registry / vesting），没有 vesting-v2 与 ecosystem_fund 的目录。
- 真正的硬 blocker 是 blocker ②：**20 条产物全都 `reproducible=no`、`source_commit=unknown`、`toolchain=unknown`**（BUILDLOG.tsv 全量），
  例外窗口 `until=2026-11-30`。也就是说"我们拿得到 bytecode、拿不到可复现的构建"，审计方进场后无法独立重编译验证。
  这条没解决之前，向审计方交付的应当是"bytecode + 链上一致性证明"，而不是"源码构建证明"。

## 2. code-id ↔ 产物 ↔ 实例

| code | 状态 | 仓库产物 | 实例数 | 代表地址 / label |
|---|---|---|---|---|
| 1 | MATCH | code1_light_token.wasm | 1 | wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z |
| 2 | MATCH | code2_mining_reward.wasm | 0 | 已被 12/15/20 取代，无实例 |
| 3 | MATCH | code3_governance.wasm | 0 | 已被 11/13/14/18/19 取代，无实例 |
| 4 | MATCH | code4_treasury_multisig.wasm | 1 | wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u |
| 5 | MATCH | code5_subtoken_factory.wasm | 1 | wasm1uykr2f24sdj9f4la0wv78gvjuyqqnqk9r8jggcqd9ha9vxjrrkksum5x0g |
| 6 | MATCH | code6_oracle_twap.wasm | 1 | wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace |
| 7 | MATCH | code7_anti_fraud.wasm | 1 | wasm1klrq28c5ef4mrn8h7f5kmph48amjplvw39ajmvkgy8lfak3x093src46wr |
| 8 | MATCH | code8_validator_registry.wasm | 1 | wasm1egt8ut5swmck6xt5lqeuhkmhp44rwsv73ka8jfp7rn2kg629cdeqdlh6qf |
| 9 | MATCH | code9_vesting.wasm | 1 | wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x |
| 10 | MATCH | code10_insurance_fund.wasm | 1 | wasm1wj3369pug9sdn5wcqu74yr00vtcntqvwgqrmcs0k0twwnvgm8m2qu77ewf |
| 11 | MATCH | code11_governance.wasm | 0 | 无实例 |
| 12 | MATCH | code12_mining_reward.wasm | 1 | wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx（每日 root 结算合约） |
| 13 | MATCH | code13_governance.wasm | 1 | wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt |
| 14 | MATCH | code14_governance.wasm | 0 | 无实例 |
| 15 | MATCH | code15_mining_reward.wasm | 0 | 无实例 |
| 16 | MATCH | code16_vesting-v2.wasm | 1 | wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6（label `vesting-v2-wp54`，**admin 为空**） |
| 17 | MATCH | code17_ecosystem_fund.wasm | 1 | wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835（label `ecosystem-fund-wp53`，**admin 为空**） |
| 18 | MATCH | code18_governance.wasm | 0 | 无实例 |
| 19 | MATCH | code19_governance.wasm | 0 | 无实例 |
| 20 | MATCH | code20_mining_reward.wasm | 0 | 无实例 |

上传 creator 只有两类：`wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj`（14 条）与 `wasm10d07y265gmmuvt4z0w9aw880jnsr700js7zslc`（6 条）。

## 3. 未编号产物（10 个 note）

`contracts/wasm/` 里另有 10 份文件名不带 codeN 的 wasm：

- `governance.wasm` 与 **code 13 逐字节相同**——同一份 bytecode 的两个文件名，建议收敛成一个，否则 BUILDLOG 里 code 13 会出现两条不同来源的记录（见 §4）。
- 其余 9 份（anti_fraud / insurance_fund / light_token / mining_reward / oracle_twap / subtoken_factory / treasury_multisig / validator_registry / vesting）与链上任一 code-id 都不相等。这 9 份恰好对齐 9 个 crate 名，最可能的身份是**从源码构建出来的候选产物**——即 blocker ② 的复现产物。若是，则"构建能跑通"和"构建结果与链上一致"是两件事，需要逐条比对确认，不能默认等价。
  注意：`mining_reward.wasm`（sha 73C60FB788020634）≠ 链上任一 mining_reward（2/12/15/20），差异要么是版本、要么是构建环境（OptLevel/lto/工具链版本），这是复现性排查的第一优先样本。

## 4. BUILDLOG.tsv 自身的两处账目问题

核对时顺带发现（本次不改动，留给 owner 决策）：

1. code 13 有**重复行**（第二行指向 `contracts/wasm/governance.wasm`，commit bd07923，缺 toolchain 与依赖锁）。
2. 末尾有 **6 行 code_id 为空**（anti_fraud / insurance_fund / light_token / mining_reward / oracle_twap / subtoken_factory，commit 9c9c239，理由同样是缺 Cargo.lock 与工具链固定）。这 6 行正是 §3 里"未编号产物"的一部分来源。

## 5. 需要 owner 拍板的一项账目冲突（本报告不代为修改）

`docs/GAP_LEDGER_WP.md:20` 把 **B1「生态基金独立合约」标为 🔴 未建**（§5.3，支持 TGE 1.2 亿+分阶段释放）。
但链上 **code 17 已经有一份 label 为 `ecosystem-fund-wp53` 的实例在跑，且 admin 为空（不可再升级）**。
两种可能，需要人来确认哪一种：

- 部署的这份不是 §5.3 需要的那版（功能/释放曲线不符），那 B1 保持未建，但必须额外记录"链上已存在一个同名 no-admin 合约"这个既成事实与它的资金敞口；
- 部署的这份就是 §5.3，那 B1 状态应改，且"no-admin + 无源 crate + 无复现构建"三者叠加意味着**这份合约一旦有 bug 无法热修、审计方也无法从源码验证**，属于 TGE 前最高优先级项。

无论哪种，都不该由自走执行器改账目，故只报告。

## 6. 复跑方式

    cd /home/ubuntu/repo
    python3 infra/ld_codeid_provenance.py                 # 表 + summary，有问题才 rc=1
    python3 infra/ld_codeid_provenance.py --instances --out /tmp/codeid.json

脚本刻意不写链、不动文件（除显式 `--out`），可挂到审计交付前的检查里；本次**未加 cron、未部署到 /usr/local/bin**。


---

## 7. 2026-11-07 独立复核（第二实现交叉验证）

自走巡检于 2026-11-07T00:16Z 用**另一个实现**重跑了一次同源核对，脚本随本报告一起入库：
`infra/audit_codeid_verify.py`（刻意不复用 `ld_codeid_provenance.py` 的解析路径，这样任一份的解析 bug 不会在另一份里被同样漏掉）。

结果：

- 链上 `list-code` 共 **20 个 code id（1–20）**，逐个与 `contracts/wasm/code<N>_*.wasm` 做 sha256 比对：**20/20 MATCH，0 DIFFER，0 缺产物**。仓库里 `code<N>_*.wasm` 命名产物正好 20 个，**没有孤儿**（不存在"有编号但链上无此 id"）；其余 **10 个未编号产物**（`anti_fraud.wasm`、`governance.wasm`、`insurance_fund.wasm`、`light_token.wasm`、`mining_reward.wasm`、`oracle_twap.wasm`、`subtoken_factory.wasm`、`treasury_multisig.wasm`、`validator_registry.wasm`、`vesting.wasm`）仍按 §4 的账目问题处理。
- 逐个 `list-contract-by-code` 数实例：链上共 **12 个合约实例**，`code 1,4,5,6,7,8,9,10,12,13,16,17` 各 1 个，其余为 0。
  即 **8 个 code id 是"已上传但没在跑"的旧版本**——同一逻辑合约有多个 id：mining_reward = code 2/12/15/20（只有 12 在跑）、governance = code 3/11/13/14/18/19（只有 13 在跑）。审计方问"哪些代码在生产上跑"时看这一行，不要按 code id 上限 20 理解。
- 在跑的 mining_reward 实例地址 = `wasm173y0pgdh6…r9wx`（code 12），与运维脚本里硬编码的那个一致；governance 在跑的是 code 13（`wasm14axmz…kapt`）。

复核同时确认本报告两条阻断项**没有变化**：

1. 阻断 ①：code 16（vesting-v2）与 code 17（ecosystem_fund）有字节匹配的产物，但 `contracts/contracts/` 仍只有 10 个 crate，缺这两个源 crate；
2. 阻断 ②：`contracts/wasm/BUILDLOG.tsv` 里全部产物仍是 `reproducible=no / source_commit=unknown / toolchain=unknown`（豁免期到 2026-11-30）。

给审计方的复现提示（本轮踩过的坑，写下来省时间）：这套 wasmd 的 `list-code` 返回字段是 **`code_id` + 十六进制 `data_hash`**，不是常见的 `checksum`/base32 校验和；本版本**没有** `list-contracts`、`all-contracts` 这两个命令，数实例必须用 **`list-contract-by-code <id>`**。两份脚本对两种字段形态都做了兼容。

两份脚本都只读链、只读仓库，不写主网、不改文件（除显式 `--out`）。本次**未加 cron**，可作为 TGE 前交付及每次合约升级后的人工检查项：

    cd /home/ubuntu/repo
    python3 infra/audit_codeid_verify.py
