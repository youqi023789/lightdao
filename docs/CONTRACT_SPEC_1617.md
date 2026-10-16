# 无源码合约行为规格：code 16（vesting-v2）与 code 17（ecosystem_fund）

生成：2026-10-17　方式：全部为链上实测（`wasmd q`），非记忆、非推断
**性质声明：这是"行为规格"，不是"恢复出来的源码"。** 我们没能恢复原始 Rust 源码
（构建机已退订、仓库全历史从未提交过这两个 crate）。把猜测写的代码标成"这就是它的源码"
会让后人误以为已经可审，那比承认缺口更危险。所以本文只记录**可复核的观测事实**，
并把"不知道什么"写清楚。

## 一、两个合约的共同事实

| 项 | code 16 | code 17 |
|---|---|---|
| 合约地址 | `wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6` | `wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835` |
| label | `vesting-v2-wp54` | `ecosystem-fund-wp53` |
| code_id | 16 | 17 |
| **admin** | **空 = 永久不可迁移**（不能换代码） | **空 = 永久不可迁移** |
| owner（合约内部权限） | 治理合约 `wasm14axmz…fukapt` | 治理合约 `wasm14axmz…fukapt` |
| 创建者（谁部署的） | `wasm13c2…ykhj`（网关 deployer 钥匙，明文等价存于网关） | 同左 |
| 当前余额 | **75,000,000.00 LIGHT** | **400,000,000.00 LIGHT** |
| 上链时间 | 2026-10-11 17:00 UTC（提案 11 生成 code 16 后实例化） | 2026-10-11 23:55 UTC（提案 12 生成 code 17 后实例化） |

合计 **475,000,000 LIGHT** 存放在两份无源码的字节码里。两者 admin 均为空，
意味着**代码本身永远无法升级或替换**；要改行为只能新建合约并迁移资金（资金迁移是治理动作）。

## 二、code 16（vesting-v2）实测接口与数据

可答查询（其余 22 个候选查询名均返回错误）：

- `{"config":{}}` → `{"owner":"wasm14axmz…"}`
- `{"all_schedules":{}}` → 三条计划：

| 类别 | 受益人 | 总额 | cliff | 线性期 | 起始 | 已领取 |
|---|---|---|---|---|---|---|
| services | `wasm13c2…`（deployer） | 125,000,000 | 31,536,000s（12 个月） | 94,608,000s（36 个月） | 1791738037（2026-10-11 17:00:37 UTC） | 0 |
| strategic | `wasm13c2…`（deployer） | 75,000,000 | 12 个月 | 63,072,000s（24 个月） | 同上 | 0 |
| contributor | `wasm19g2…`（创始人钱包） | 50,000,000 | 12 个月 | 94,608,000s（36 个月） | 同上 | 0 |

**与白皮书 §5.4 的交叉核对（这条是好消息）**：战略运营基金 2.5 亿的子分配为
服务换代币 1.25 亿（50%，12 月 cliff + 36 月线性）、战略融资 7500 万（30%，12 月 cliff + 24 月线性）、
核心贡献者 5000 万（20%，12 月 cliff + 36 月线性）。链上三条计划的**金额、cliff、线性期逐项吻合**，
所以"部署时参数写错"这一类风险可以排除；剩下的问题只是**代码逻辑本身无人能审**。

二进制里能看到的候选入口名（**未经执行验证，仅作线索**）：`claim`、`vested`、`claimable`、
`update_beneficiary`、`new_beneficiary`、`vault_balance`、`instantiate_v2`、
错误串 `immutable`、`unauthorized`。

## 三、code 17（ecosystem_fund）实测接口与数据

可答查询：

- `{"unlocked":{}}` → `120,000,000` LIGHT（= 4 亿的 30%，对应白皮书"TGE 释放 30%"）
- `{"released":{}}` → `0`
- `{"remaining":{}}` → `120,000,000`
- `{"balance":{}}` → `400,000,000`

二进制里的候选入口名（**未验证**）：`eco_config`、`instantiate_ecosystem_fund`、`owner`、
`release`、`recipient`、`unlocked`、`released`、`remaining`、错误串 `unauthorized`。

## 四、我们不知道什么（必须写出来，不能装作知道）

1. **Execute 面的完整参数与权限判定**：谁能让生态基金释放资金、按什么节奏、有没有上限，
   只能从字符串猜（`release`/`owner`/`unauthorized`），无法在管着 4 亿的线上合约上试。
2. **存储键布局**：无法从优化过的二进制可靠还原，因此也无法验证"迁移到新代码时状态是否兼容"。
3. **数值边界与溢出/取整行为**：线性释放的每秒计算方式未知。
4. 因此：**不能声称这两个合约"已审计"或"源码已归档"**。

## 五、处置路径（按可执行性排序）

1. **已做**：把上面的观测事实固化成本文件；新增源码覆盖率监控（见
   `infra/ld_src_coverage.py`），让"无源码的敏感合约"数量**只能降不能悄悄升**。
2. **建议下一步（需要治理动作，等所有者决定）**：用 CI 先产 sha256 的新流程，
   写一份**有源码、有单元测试、行为按本规格实现**的新合约，在测试网按本规格逐条比对行为一致后，
   再走提案把资金迁过去，把这两份无源码合约退役。
3. **不建议**：把猜测写的代码提交进 `contracts/contracts/` 并当作它们的源码——
   那会制造一个"看起来可审"的假象，比现在的诚实缺口更糟。

## 六、复现命令（任何人可自查）

```bash
A=wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6
B=wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835
wasmd q wasm contract $A --node tcp://127.0.0.1:26657 -o json     # code_id / admin / label
wasmd q wasm contract-state smart $A '{"all_schedules":{}}' --node tcp://127.0.0.1:26657 -o json
wasmd q wasm contract-state smart $B '{"unlocked":{}}' --node tcp://127.0.0.1:26657 -o json
wasmd q bank balances $A --node tcp://127.0.0.1:26657 -o json
wasmd q bank balances $B --node tcp://127.0.0.1:26657 -o json
```
