# LightDAO 合约安全审计报告（自审）

> 状态：**自审 + 修复 + 链上验证通过**。本报告由 AI 完成，**不能替代专业第三方审计**（如 Oak Security / Nethermind / Cantina）。上主网前请务必再做一次独立审计。
> 链：`lightdao-testnet-1`（wasmd v0.60 / wasmvm v2.2.1 / cosmos-sdk v0.53）。合约：CosmWasm，rustc 1.85 编译，`wasm-opt --mvp-features -O3` 归一化后上链。

## 0. 编译/上链关键坑（务必保留）
- rustc 1.85 / LLVM 19 默认给 wasm32 输出 `reference-types` 特性，而 wasmvm v2.2.1 的 wasmer4 **禁用了该特性**，store 会在 **DeliverTx** 阶段报 `reference-types not enabled`。
- `-C target-feature=-reference-types` / `-C target-cpu=mvp` **无效**（rustc 把 reftype 焊进 target spec）。**唯一可靠修复**：编译后用 `wasm-opt --mvp-features -O3 in.wasm -o out.wasm` 归一化（也是 CosmWasm 官方 optimizer 的标准步骤）。
- `tx wasm store/instantiate2 -b sync` 返回的是 **CheckTx** 结果，可能 code:0 但 DeliverTx 失败。**必须** `wasmd q tx <hash>` 查真实结果。
- 连续发交易必须**显式递增 `--sequence` 且每笔间隔 > 出块时间（本链约 5s）**，否则 `account sequence mismatch (code:32)`。
- `instantiate2` 必须带 `--admin` 或 `--no-admin`（wasmd #719），否则广播前即失败。
- 循环依赖（light_token↔mining_reward↔anti_fraud、governance↔subtoken_factory）用 `wasmd q wasm build-address <code-hash> <creator> <salt-hex>`（离线）**提前算出地址**，再填入各自 InstantiateMsg，即可一次性正确互连。

## 1. 审计发现（按严重度）

| 级别 | 合约 | 问题 | 影响 |
|---|---|---|---|
| 致命 | mining_reward | `SubmitDailyRoot` 无鉴权 + 空证明单叶 Merkle + `ACTIVE_MINERS` 恒为 1 + score 无上限 | 任何人可自造每日根并领取整日矿池，跨天重复 → **抽干 2.5B 硬顶** |
| 高 | governance | `Stake` 非托管且累加；`vote` 无投票期校验 | 重复 `Stake` 可把投票权刷到远超持仓；投票期外可投票 |
| 高 | validator_registry | `SlashDoubleSign/SlashOffline` 无鉴权；`Register` 质押不存在的原生 `ulight`（LIGHT 实为 CW20） | 任何人可罚没/封禁任意验证者；注册功能不可用 |
| 高 | vesting | `AddSchedule` 无鉴权；`Claim` 只改计数、不真正转账 | 任何人可给自己建归属；归属永不发放 |
| 高 | insurance_fund | `Accrue`/`VoteClaim` 无鉴权、投票权重调用者任填；`ResolveClaim` 无真实转账；POOL 为假计数 | 可自批赔付、随意增发池；无真实资金流 |
| 中 | oracle_twap | `Twap30d` 为全程简单平均、非 30 天时间加权；无单区块去重 | 价格可被单区块刷屏操纵，TWAP 不符白皮书 |
| 低 | subtoken_factory | 15% 单地址上限用铸前供应量比较 | 上限判定偏差 |
| — | light_token / anti_fraud / treasury_multisig | 逻辑健全 | treasury 的 3/5 门限 + 72h 时间锁 + 不可紧急豁免均正确 |

## 2. 修复内容（改动 8 个合约）

- **light_token**：新增 `TransferFrom{from,to,amount}`（allowance 授权转账），作为托管式质押/归属/注册的底层能力。Mint 仍受 minter 鉴权 + 2.5B 硬顶约束（未改）。
- **mining_reward**（致命项）：
  - `SubmitDailyRoot` 改为**仅授权验证者**可提交（`validators` 白名单，实例化时设定）；根**不可重复提交**；**仅允许已完结的天**（`day < current_day`）。
  - 提交时同时写入 `active_miners` 与 `total_score`（当日全体加权分之和）。
  - 奖励公式改为 **`当日矿池 × 我的加权分 / 当日总分`**：全体矿工之和恰等于当日矿池，**杜绝超发**。
  - `Claim` 强制每个 score 分量 **≤ 1e6**；仅完结天可领；防重复领取。
- **governance**：
  - `Stake/Unstake` 改为**托管式**：`Stake` 通过 `light_token.TransferFrom` 把 LIGHT 真正锁进治理合约；`Unstake` 用 `Transfer` 退回。**重复质押无法凭空增票**（每次都要真实转币）。
  - `vote` 增加**投票期窗口校验**（`start ≤ now < end`）且**无质押不能投票**。
  - 保留：投资类提案通过后 `exec()` 向 subtoken_factory 发 `CreateSubToken`；`voting_period_secs` 可实例化覆盖（测试网用短周期，主网 `None` 走白皮书按类型天数）。
- **validator_registry**：`Slash*` 改为**仅 owner**（治理/金库）可调用，罚没额**真实销毁 LIGHT**（通缩）；`Register{amount}` 改为质押**真实 CW20 LIGHT**（TransferFrom 托管），`Unregister` 退还、封禁期不可退。
- **vesting**：`AddSchedule` **仅 owner**；`Claim` **真实转账** LIGHT 给受益人（金库需先注资）。
- **insurance_fund**：`Accrue` 仅 `accrue_source`/治理且**真实归集 LIGHT**；`VoteClaim` **仅治理**可中继 DAO 权重（防自批）；`ResolveClaim` 通过后**真实赔付**，受 20% 池上限约束。
- **oracle_twap**：改为**真正的 30 天按日分桶时间加权均价**（每日样本均值，窗口内按天等权）+ **单区块去重**。
- **subtoken_factory**：15% 上限改为对**铸后总供应**比较；`Exchange` 要求 TWAP 非零。

## 3. 链上验证结果（真实交易，非模拟）

### 三条主链路（happy path 全 DeliverTx code:0）
- **A 挖矿**：授权验证者提交 day0 根 → miner1 `Claim` → **mint 650,684,931,506 microLIGHT**（=650,684.93 LIGHT），余额/总量/上限同步。
- **B 治理**：`IncreaseAllowance` → `Stake 2000 LIGHT`（治理托管余额=2,000,000,000；miner1 质押权重=2,000,000,000）→ `CreateProposal(vc, CAFE, 1M USD)` → `Vote yes`（yes_weight=2e9, yes_addrs=1）。
- **C 子代币**：投票期满 → `ExecuteProposal` → 治理跨合约调用 factory → `AllSubTokens=["CAFE"]`，`CAFE{total_supply=1,000,000, investment_usd=1,000,000, locked_until=+30d}`。

### 7 项安全回归（全部按预期 revert，code:5）
| 攻击/边界 | 期望 | 实测 |
|---|---|---|
| 非验证者提交每日根 | 拒绝 | ✓ `unauthorized` |
| 提交未来天的根 | 拒绝 | ✓ `day not completed` |
| score 分量 >1e6 | 拒绝 | ✓ `score out of range` |
| 重复领取同一天 | 拒绝 | ✓ `already claimed` |
| 无授权重复质押刷票 | 拒绝 | ✓ `Insufficient allowance`（无法凭空增票）|
| 非 owner 罚没验证者 | 拒绝 | ✓ `unauthorized` |
| 非 owner 建归属 / 非治理投保险票 | 拒绝 | ✓ `unauthorized` |

## 4. 仍存在的信任假设 / 后续加固建议（非漏洞）
1. `SubmitDailyRoot` 的 `total_score`/`active_miners` 目前**信任授权验证者诚实提交**；主网建议加验证者多签或链下可验证计算（如 zk / 乐观挑战）。
2. vesting / insurance_fund 金库的**初始 LIGHT 注资**目前靠 owner 手动转入，建议加治理审批流。
3. Merkle 证明格式为自定义 `'L'/'R' + hex` 前缀；建议统一到业界标准（如 OpenZeppelin merkle proof）并补 fuzz 测试。
4. 缺少 CosmWasm 单元测试 / 集成测试；建议补 `cargo test` + `cw-multi-test` 覆盖，再做独立审计。
5. 经济参数（epoch 减半、95/5 分配、TWAP 窗口、各类门限）应与最新白皮书 V2.3 再核对一次。

## 5. 复现方式
见 `README.md` 与 `scripts/`：`build_normalize.sh` → `deploy.sh`（可选 `RESET=yes`）→ `verify_flows.sh`。

---

# 第二轮加固（本次实现，均已链上验证）

针对第 4 节列出的信任假设，已在代码层实现并重新部署验证：

## #1 每日根 N-of-M 验证者多签（mining_reward）
- `SubmitDailyRoot` 由“单验证者即可写根”改为 **N-of-M 多签**：每个授权验证者对 `(root, active_miners, total_score)` 的 **sha256 承诺**投票，达到 `root_threshold` 个**不同**验证者的相同承诺后，根才被 `committed`。
- 单验证者无法再单独伪造每日根。主网建议 `validators=7, root_threshold=5`（2/3+1）；测试网用 `3, 2`。
- 防重复投票、防未完结天、根不可覆盖。
- **链上验证**：`A root vote 1/2` 后矿工领取被拒（`root not committed`）；`2/2` 后 `RootSubmitted=true`，领取成功。

## #3 Merkle 证明硬化（mining_reward）
- `merkle_verify` 现在强制：root 必须 64 位 hex；每个证明元素必须恰为 `'L'|'R' + 64hex`（长度 65）；证明深度 ≤ 32（DoS 防护）；hex 解码失败即拒绝（不再 `unwrap_or_default` 静默吞错）；大小写不敏感比较。
- 单元测试覆盖单叶匹配、错误 root、非法方向字符、非法长度。

## #2 治理成为真正的 DAO 执行器（governance）
- 提案新增通用字段 `target` / `call_msg`(Binary) / `migrate_code_id`。提案通过后 `exec()` 可：
  - 投资类：向 subtoken_factory 发 `CreateSubToken`（原有）；
  - 通用：向任意 `target` 合约发 `WasmMsg::Execute{call_msg}`（如给 vesting 建归属、给 insurance 归集、改 light_token minter）；
  - 升级：发 `WasmMsg::Migrate{target, new_code_id, call_msg}`。
- **所有合约 admin = governance**；`light_token.owner`、`vesting.owner`、`validator_registry.owner` 均 = governance。→ 金库注资、归属创建、罚没、minter 变更、合约升级**全部只能经 DAO 提案+投票**，无单点。
- **链上验证（Flow D）**：提案#2（target=vesting, call_msg=AddSchedule 的 base64）投票通过 → `exec` → vesting 中**由治理创建**了 miner1 的归属表 `{total:1e9, cliff:0, linear:100}` ✓。

## #4 单元测试（cargo test，13 项全绿）
- mining_reward（8）：矿池 epoch1/减半、加权分（满分=1e6、单维=40%）、奖励按比例且不超池、Merkle 单叶匹配、Merkle 拒绝坏 root/坏证明、hex64 校验。
- governance（5）：双维度通过判定——无票失败、单质押者全票通过、多数反对失败、低投票率抬高门限、紧急类需 75%。
- 运行：`cargo +1.85 test -p mining_reward -p governance`。

## #5 经济参数复核（分析）
- epoch=730 天减半、epoch1=5 亿、矿工 95%/验证者 5%、硬顶 2.5B、TWAP 30 天、各类提案门限——与代码常量一致；**需与白皮书 V2.3 最终数值再逐项对表**（尤其 5% 验证者份额的发放路径当前未在 mining_reward 内实现，建议补验证者奖励分配或明确由金库链下结算）。

## 第二轮验证结果汇总（真实交易）
| 用例 | 期望 | 实测 |
|---|---|---|
| A 非验证者提交根 | 拒绝 | ✓ code5 |
| A 提交未来天根 | 拒绝 | ✓ code5 |
| A 单验证者(1/2)后领取 | 拒绝(未达门限) | ✓ code5 |
| A 达门限(2/2)后提交 | 根 committed | ✓ RootSubmitted=true |
| A score>1e6 | 拒绝 | ✓ code5 |
| A 正常领取 day0 | 成功 mint | ✓ code0，miner1 +650,684,931,506 |
| A 重复领取 | 拒绝 | ✓ code5 |
| B 无授权重复质押刷票 | 拒绝 | ✓ code5 Insufficient allowance |
| B 托管质押 2000 | 成功(治理真实持币) | ✓ 治理余额=2e9 |
| C 提案通过→铸子代币 | CAFE 生成 | ✓ AllSubTokens=[CAFE] |
| D 提案通过→治理建归属 | vesting 表生成 | ✓ Schedule(miner1) 存在 |
| 非 owner 罚没 / 非 owner 建归属 / 非治理投保险票 | 拒绝 | ✓ 全 code5 |

> 结论：第 4 节的信任假设 #1/#2/#3/#4 已在代码层消除或大幅收敛；剩余为流程类（第三方审计/bug bounty、密钥仪式、合规、监控）——见 `MAINNET_RUNBOOK.md` 的 go/no-go 闸口。
