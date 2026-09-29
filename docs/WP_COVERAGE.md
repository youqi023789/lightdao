# 白皮书覆盖矩阵 v2(WP_COVERAGE)— 六元组版(承诺/出处/状态/执行点/检测点/告警/测试/缺口)

> 规则:状态 ❌ 必须带排期否则阻断 release;🟡 必须 UI 公示;每行"检测点+告警"缺一即视为**未审计**(进 OPS_ROADMAP OPEN)。
> 状态:✅已上线 🟡部分 ⏳待条件 ❌未做 ⚠️有缺口(注明)。

| # | 承诺 | 出处 | 状态 | 执行点 | 检测点 | 告警 | 测试 | 缺口/排期 |
|---|---|---|---|---|---|---|---|---|
| 1 | 浏览器轻节点挖矿(PoC 三层) | §4.3/4.8 | ✅ | app+网关+mining_reward | 金丝雀每日领取 | Discord ⚠️ | qa_click/e2e | — |
| 2 | USD-gas + 50/30/20 | §4.5 | ✅ | x/lightfee | 链上事件 lightfee_price_update | 验收 cron | v3 已验 | Oracle 主源⏳(#18) |
| 3 | Passkey+Shamir 3-of-5 | §4.9 | ✅ | passkey-wallet.js | qa_lock | — | e2e | PIN 强度(F6)排期 |
| 4 | WebRTC 中继+TURN | §4.7 | ✅ | webrtc-relay+coturn×8 | TURN 凭据 HMAC | — | e2e | — |
| 5 | vesting vault 三分批 75/100/75 | §5.3/1135 | ✅ | vesting 合约(deployer/strat2/strat3=运维键,非个人钱包) | 链上 schedule 查询==WP 参数 | 月度审计 | 已核 09-29 | 子分配(服务125/战略75/贡献者50,§525-527)⏳治理恢复后按里程碑;贡献者释放受益默认创始地址;strat2/3 明文key→S1 |
| 6 | 链上治理 5 档/双维度 | §5.14 | ⚠️ | governance code11 | — | — | — | execute 无权限/无过期(F4)→10-05 迁移;质押坏→同迁移;迁移后第一提案=贡献者释放流程(§527) |
| 7 | 邀请返佣 10% 首周 | §985 | ✅ | 网关 referrals | 对账 cron | RECON-FAIL | 赛季脚本 | — |
| 8 | 头衔/徽章/投票权重 | §368/985 | 🟡 | app 徽章卡(链下) | qa_click | — | e2e | 链上徽章⏳第7月 |
| 9 | 空投九类 | §5.7/985 | 🟡 | 前五项账本+空投中心 | 对账 cron | RECON-FAIL | qa | 后四项(ZK-KYC/DEX/审核/合作) |
| 10 | 赛季/子代币30%/TGE种子空投 | §5.7/517 | ⏳ | S1 结算脚本 | — | — | — | 触发条件公示于空投中心 |
| 11 | 委托在线 70/30 | §338 | ✅ | finalize 拆分+app 开关 | 金丝雀 fp 行为 | — | e2e | 输入框占位/校验 1.1.5 |
| 12 | 验证者 30% 手续费 | §408 | ✅ | x/distribution | 周领 cron 日志 | — | 手动核 | 委托人分润无→DESIGN_DELEGATOR_YIELD |
| 13 | 验证者 5% 排放 | §539/5.5 | 🟡 | v4 code12+提案10 | 10-04 cron 验 validator_share | Discord ⚠️ | 单测9/9 | 10-04 05:35Z 执行 |
| 14 | 验证者选举扩 100 | §4.6/81 | ⏳ | /nodes 公示 | — | — | — | 第7月 |
| 15 | 子代币发行/兑换/分红 | §5.9 | 🟡 | 合约就绪+只读 UI | qa_click | — | e2e | 首笔投资提案触发 |
| 16 | 保险基金 10% | §68/681 | 🟡 | 合约+explorer 公示 | 月度审计 | — | — | 计提随利润流 |
| 17 | 金库多签 | §507 | ✅ | treasury_multisig | signer1-5 在 keyring | — | — | 纳入 S1 runbook |
| 18 | 预言机 TWAP 主源 | §4.10 | 🟡 | 外部中位现役 | truth-probe | 每小时 | — | 多源+速率限制(S4)10-05 |
| 19 | 四级升级流程 | §459 | ✅ | x/gov+看门狗 | 验收 cron | Discord ⚠️ | v2/v3 实演 | 回滚归档已修 09-29 |
| 20 | 反女巫 | §4.8 | ⚠️ | finalize 去重+IP 标记 | /v1/me+UI 当天flag | — | qa_truth | fp 自报无 PoW(F5)→S2 提案 10-10;XFF 已修 |
| 21 | 移动端会话/宽限/PWA 加成 | §338 | ✅ | 网关+app | 金丝雀行为加成 | — | e2e | 加成钳制≤1e6 已修 |
| 22 | KYC/合格投资者 | §271/288 | ⏳ | — | — | — | — | TGE 合规;UI 已公示待启 |
| 23 | 法律声明非证券 | §32/92 | ⚠️ | 页脚+terms | 文案扫描(月审) | — | — | 免责声明仅中文(F9)→多语排期 |
| 24 | CAC $55/空投预算 | §569/581 | ⏳ | 账本 | — | — | — | TGE |
| 25 | 钱包锁+敏感操作 step-up | (安全设计) | ✅ | lock.js 1.1.0+ | qa_lock 134 项 | — | e2e | 老会话 adoptSeed 已修 1.1.2 |
| 26 | 日界整点+本地时区显示 | (UX) | ✅ | 网关 cutover 09-30 | qa_truth S6 | — | e2e | — |
| 27 | 可领取=链上真相 | (UX/真相) | ✅ | tx_search 排除已领 1.1.6 | qa_truth | 信标 | e2e | — |
| 28 | 显示==真相(徽章/状态) | (UX/真相) | ✅ | JS 驱动+truth-probe | qa_truth+monitor | 每小时 | e2e | — |
| 29 | 结算 SLA(定稿≤边界+2h) | (运维) | ⚠️ | cron UTC+ld_day | monitor SLA | Discord/ld_alerts | — | cron 已重启生效;SLA 公式已修 |
| 30 | 密钥托管安全 | (安全) | ❌ | keyring test 明文 | 文件完整性(待加) | 待加 | runbook 演练过 | S1:10-06 窗口;含 strat2/3/signer1-5 |
| 31 | 传输/响应安全头 | (安全) | ✅ | nginx snippet CSP/HSTS/XFO | 头复验+月审 | — | — | 09-29 恢复 |
| 32 | 供应链(SRI/固定版本) | (安全) | ✅ | vendor+SRI 152 | sri_verify 每日 | Discord ⚠️ | — | jsdelivr 回退无签名(F7)→移除/自托管排期 |
| 33 | 隐私(指纹/IP 留存) | (合规) | ⚠️ | 网关存储 | — | — | — | 留存期+删除路径(S6)10月 |
| 34 | 经济守恒(供应=硬顶−销毁) | (经济) | ✅ | 合约 mint/burn | 每日对账 cron | RECON-FAIL | 审计 F2 重算 3/3 | mint_denom=stake 惰性(F3)→提案 |
| 35 | 发布可回滚 | (运维) | ✅ | promote 版本化归档 | 归档目录非空检查 | — | 1.1.x 实演 | — |
| 36 | 监控自身存活 | (运维) | ⚠️ | monitor+信标 | 哨兵故障注入(周红队) | — | — | 红队首跑后闭环 |

## 门禁与审计挂钩
- 每行六元组缺"检测点/告警"→ 自动进 OPS_ROADMAP OPEN(月审 diff 本表)。
- release 前:qa_site/qa_extra/site_audit/qa_truth(+qa_lock/qa_click 视改动)+ staging 四门 + 本表 ❌ 清零或带排期。
