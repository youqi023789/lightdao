# B5 Gas 代付（Paymaster）规格差距分析

> 生成：2026-11-06T20:10Z（自走巡检第 8 步推进项，只读分析、未动主网）
> 数据源：whitepaper/LightDAO_Whitepaper_V2.4.md:453（V2.0:424 同文）、
> infra/gas_grant.py（网关执行版 /home/ubuntu/lightdao_gateway/gas_grant.py）、
> ubuntu crontab `*\/10 * * * * gas_grant.py $(ld_day.sh cur)`、
> 链上 `wasmd q feegrant grants-by-granter`（2026-11-06T20:08Z，26 条存活 BasicAllowance）。

## 白皮书承诺（§4.9）
> 新用户前 100 笔交易 Gas 由生态基金代付（Paymaster 模式）。

## 现状实现
- 机制：cosmos x/feegrant BasicAllowance，granter=deployer（wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj），
  spend_limit=5,000,000ulight／条，到期=30 天滚动；对"当日已 finalized 的活跃矿工"（day_<N>.json）逐一发放。
- 幂等：网关本机 granted.json（当前 27 条）；防刷：每 IP 每日最多 3 条 grant；
  零余额地址先 bank send 200,000ulight dust（此笔走普通转账，不属 feegrant 记账）。

## 差距清单
| # | 差距 | 性质 |
|---|---|---|
| G1 | "前 100 笔"是按笔数计的承诺，现状是"5M ulight/30 天额度"的金额制近似，未对任何用户做笔数计数 | 规格不等价 |
| G2 | 出资方是 deployer 地址，不是"生态基金"——B1 生态基金独立合约未建，补贴成本目前混在部署账户账上 | 归属不符 §5.3 |
| G3 | 覆盖面只有"当日活跃矿工"的 claim 交易；白皮书说的"新用户"（如普通转账接收者）拿不到 grant | 范围收窄 |
| G4 | 每 IP 3 条/日的防刷可被多账号绕过，链上无每地址终身配额计数 | 防护不足 |
| G5 | granted.json 幂等状态仅存网关本机；若未纳入每日备份清单，丢失后可对同批地址重发 grant（重复补贴） | 运维风险 |
| G6 | 预算口径未定：100 笔×实测单笔 gas 尚未做链上抽样，5M/30 天是否覆盖"高频领取 100 笔"无数据结论 | 待补数 |

## 收敛建议（TGE 前排期，均不触碰本次巡检禁区）
1. 二选一并在 GAP_LEDGER 标注：a) 实现"每地址终身 N 笔"链上计数配额；b) 白皮书措辞修订为金额制
   （"每 30 天滚动窗口 ≤5M ulight Gas 补贴"），走治理修正流程——与 A 类"叙述与实现一致"原则对齐。
2. B1 落地后把 granter 切换为生态基金地址，补贴支出计入基金账本。
3. 核查 granted.json（连同 gateway data/ 目录）是否已在 gw-*.tgz 每日备份内；未含则加入清单。
4. 做一次只读链上抽样：统计典型 claim tx 实际 gas_used×fee，回填 G6 预算表。
