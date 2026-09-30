# 草案:治理合约迁移提案(x/gov MsgMigrateContract)— 目标窗口 2026-10-05

状态:DRAFT,待 10-04 v4 执行后提交。**不要用链内治理提案做此事**(见"为什么")。

## 问题(已实测)
- 链上 governance 实例 `wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt` = code 11(旧构建):stake 走 light_token 的 allowance + 内部 transfer_from。
- 链上 light_token `wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z` = code 1(新构建,消息形状已变)。
- 两者不兼容 → 质押必报 `Error parsing into type light_token::ExecuteMsg`;投票因权重=质押额而报 `no stake`。治理实质不可用。
- 仓库当前 governance 源码已改为**原生 LIGHT 随消息质押**(不再调 light_token),即迁移目标构建。
- 证据:直接向 light_token 发 increase_allowance / transfer_from{from,to,amount} 均 code 0(代币侧形状正常)→ 失败点在治理合约内部子消息。

## 为什么走 x/gov 而非链内提案
链内 create_proposal 需要质押权重,而质押已坏 → 鸡生蛋。故用链级 `x/gov`(MsgStoreCode + MsgMigrateContract,authority=gov 模块),由 7 个验证者投票通过(与共识级变更同路径)。

## 步骤
1. SG 构建目标 governance wasm:`cargo rustc --release --target wasm32-unknown-unknown --crate-type cdylib -- -C target-feature=-reference-types`,再 `wasm-opt --mvp-features -O3`;记录 sha256。
2. **测试网先行**:在 lightdao-testnet-1 对测试网 governance 实例做同构迁移,验证 STAKED/提案状态保留、原生 stake/vote 可用,再上主网。
3. x/gov 提案(消息序):① MsgStoreCode(新 governance wasm)→ 得 code_id N;② MsgMigrateContract{contract: wasm14axmz…, code_id: N, msg:{}}。deposit 10 LIGHT;7 验证者 yes。
4. **顺序约束:必须在 10-04 05:35Z v4(proposal 10 执行)之后**(proposal 10 的存在与 executed 标记在 governance 状态里,迁移虽保留同键状态,仍避开同窗口叠加风险)。建议 10-05。
5. 网页 1.2.0:stake 改为随消息附原生 LIGHT(删除 increase_allowance 步骤),unstake 返回原生;文案同步。
6. 验收:已知地址 staked_balance 迁移前后一致;active_proposals 含 #10 且 executed 标记不变;新 stake/vote 成功;qa_site/qa_extra/site_audit/qa_truth/qa_click 全过;monitor truth-probe 绿。
7. 回滚:仅当存储键向前兼容时迁回 code 11;否则前向修复。迁移前快照 governance 全状态(`contract-state all` 导出)留存。

## 提案正文(中文摘要,供提交)
标题:迁移治理合约至原生质押构建(修复质押/投票不可用)
摘要:治理合约 code 11 与 light_token code 1 消息形状不兼容,导致质押与投票不可用。本提案经 x/gov 存储新治理代码并迁移治理实例;迁移保留全部质押与提案状态;网页客户端同步改为原生质押。不影响挖矿、领取、v4 排放。

## 14. 两段式提案(取代单提案;09-29 演练发现的攻击面)
- 链参数 code_upload_access=Everybody → 任何人可 store code;CosmWasm 不对同 checksum 去重(drill FAIL 项)→ 单提案内预测 code_id 可被"序号顶移"攻击迁移到恶意代码。
- 故拆为:A=MsgStoreCode(独立提案,执行后观测真实 code_id);B=MsgMigrateContract(独立提案,提交前用 make_proposal_b.sh 校验 sha256(code[id])==9e0dc33866396d34e4a151d67d6e6504e1de91f27a53aad6805fd961ffcced6a 并填入真实 id;不匹配即 ABORT)。
- 文件:/home/ubuntu/gov_migration_A_storecode.json、gov_migration_B_migrate_TEMPLATE.json、make_proposal_b.sh。
- 窗口顺序:10-05 提 A → 48h 投票 → 执行 → 跑 make_proposal_b.sh → 提 B → 48h → 执行 → 验收(MIGRATION 12 条)。

## 16. 加速时间线(09-30 起执行, 取代原 10-05 单窗口)
- A(store gov v2 code): 09-30 已提交 x/gov #6, 7/7 yes(3.5e12), 自动执行 2026-10-02 03:23Z。
- B(migrate governance→v2, void 2/5/6/7/9): cron 0455dcc4 @ 10-02 04:00Z(sha 校验 9e0dc338… 后提交+7票); 自动执行 ~10-04 04:xxZ。
- v4(mining_reward→code12): cron d417f628 @ 10-04 05:35Z(execute_proposal 10, deployer=proposer, v2 权限模型下仍可行)。
- C(mining_reward→epoch 对齐 code, genesis_time=1789084800): cron 428470ec @ 10-04 12:00Z(构建+store+治理提案, 投票7d)→ 执行 ~10-11 → **领取开放统一为北京 08:00**。
- 过渡期(至 ~10-11): 结算 08:00 / 领取 12:48(合约日界), UI 1.2.0 单处展示双时间+倒计时+统一日期, 不再弹报错吐司。
