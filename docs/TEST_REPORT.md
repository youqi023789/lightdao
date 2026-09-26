# LightDAO §4.5 Gas 经济模块 — 测试网彩排报告

**日期**: 2026-09-22
**模块**: `x/lightfee`(wasmd v0.55.0 fork)
**测试环境**: SG VPS 单验证者独立测试网 `lightdao-testnet-gas`(端口 26757,与主网 26657 完全隔离)
**结论**: ✅ **功能与可观测性全部验证通过,主网未受任何影响**

---

## 1. 被测二进制

| 项 | 值 |
|---|---|
| 路径 | `/home/ubuntu/lightd`(SG VPS) |
| sha256 | `f5d159b506627726323ad9397fc994af241cc1e48197680381228edd178bd76c` |
| 大小 | 159,985,144 字节 |
| 基线 | wasmd v0.55.0 / cosmos-sdk v0.50.12 / wasmvm v2.2.1 / cometbft v0.38.15 |
| 编译器 | go1.23.6 linux/amd64 |

与线上主网链 `lightdao-mainnet-1` 同基线,确保升级后状态机兼容。

## 2. 实现的两个机制

### (a) USD 锚定动态 min-gas-price
公式:
```
min_gas_price(Denom/gas) = (TransferUsdTarget / UsdPerToken) × 10^Decimals / RefTransferGas
```
测试参数:`TransferUsdTarget=$0.001`,`UsdPerToken=$0.05`(静态回退),`Decimals=6`,`RefTransferGas=100000`
→ `min_gas_price = (0.001/0.05)×10^6/100000 = 0.2 stake/gas`

价格源:优先查询 `oracle_twap` 合约(`QueryOraclePrice`),失败/未配置时回退静态价。当前测试用静态价(oracle 尚未喂价)。

### (b) 手续费分配 50% 销毁 / 30% 验证者 / 20% 金库
在 `EndBlock` 抽干 `fee_collector`:
- 50% → 销毁地址 `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(确定性死地址,无密钥可花)
- 20% → 金库地址(env `LIGHTDAO_TREASURY_ADDR` 配置)
- 30% → 留在 fee_collector,由 x/distribution 下一块 BeginBlock 扫给验证者

## 3. 验证结果

### 测试 1:足额 fee 交易通过
- 发 `--gas 200000 --fees 50000stake`(要求 ≥ 0.2×200000 = 40000)
- 结果:**code 0 成功**,gas_used 84236,已上块

### 测试 2:不足额 fee 交易被拒
- 发 `--gas 200000 --fees 1000stake`(< 40000 要求)
- 结果:**code 13 拒绝**,错误信息精确:
  ```
  USD-anchored min-gas-price not met: required >=40000stake, got 1000stake
  (gas=200000, min_gas_price=0.200000000000000000/stake-gas): insufficient fee
  ```

### 测试 3:50/30/20 分配精确匹配
发 3 笔交易,总 fee = 300000 stake:

| 去向 | 实测增量 | 期望 | 结果 |
|---|---|---|---|
| 销毁 | 150000 | 50% = 150000 | ✅ |
| 金库 | 60000 | 20% = 60000 | ✅ |
| 验证者 | 90000 | 30% = 90000 | ✅ |

### 测试 4:事件可观测性(v2 修复后)
单笔 100000 fee 交易所在块的事件流:
```
[BeginBlock] lightfee_price_update {price_usd:0.05, source:static, min_gas_price:0.2, denom:stake}
[EndBlock]   lightfee_burn         {amount:50000, to:wasm1aeaty...(burn)}
[EndBlock]   lightfee_treasury     {amount:20000, to:wasm1cgtfz...(treasury)}
[EndBlock]   lightfee_summary      {total_fee:100000, burn:50000, treasury:20000, validators:30000}
```
每块均发出 `lightfee_price_update`,分配块发出 `burn/treasury/summary`。

### 测试 5:不抽通胀(关键正确性)
`finalize_block_events` 证实:mint 每块通胀(如 20638 stake)→ fee_collector → **distribution 在同块 BeginBlock 立即扫给验证者**(rewards/commission 事件可见)。lightfee.EndBlock 在 distribution 之后运行,fee_collector 此时仅含本块真实 tx fee,**通胀未被误抽/误烧**。

## 4. 修复的工程问题(记录)

| # | 问题 | 修复 |
|---|---|---|
| 1 | 原 `lightfee.go` 是伪代码:`sdk.AnteDecoratorFunc` 不存在、`sdk.AccAddress([]byte(name))` 错误、`ctx.WithMinGasPrice` 无效 | 全部重写:真 struct 实现 `AnteHandle`、`authtypes.NewModuleAddress`、Keeper 内存态价格 |
| 2 | `Coins.IsAnyGTE` 需 `Coins` 不是 `DecCoins` | 用 `TruncateInt()` 转 `Coins` |
| 3 | lightfee 装饰器拦截 genesis gentx(空 fee) | `ctx.BlockHeight()==0` 时放行(cosmos-sdk 标准做法) |
| 4 | wasmd v0.55 `gentx`/`create-validator` 不自动填 `delegator_address` | 用 `tx create-validator <json> --generate-only` → 手动补 delegator → `tx sign --offline` → 注入 genesis |
| 5 | 事件不可见:`ModuleManager.BeginBlock/EndBlock` 内部 `WithEventManager(NewEventManager())` 丢弃外层事件 | v2:lightfee 用独立 EM 运行,事件 append 进 resp(状态写同一 store,不影响 app_hash) |

## 5. 已知限制(主网前需知)

1. **denom 仍是 `stake` 不是 `ulight`**:白皮书 §4.5 经济模型建立在原生 LIGHT 计价上。当前链原生 denom 是 `stake`,需先做 denom 重构(独立工作段)才能让 gas 真正以 LIGHT 计价。lightfee 的 `Denom` 可配,重构后改 env 即可。
2. **oracle 未喂价**:`QueryOraclePrice` 已实现但 `oracle_twap` 合约无真实价格源,当前用静态 $0.05。接入真实喂价(Chainlink/Pyth/自建 CEX TWAP)后,设 `LIGHTDAO_ORACLE_CONTRACT` 即自动切换。
3. **参数无链上治理**:v1 参数来自 env/编译期,改参数需再次协调升级。后续可做成 governance 可调。
4. **30% 验证者份额依赖 distribution 时序**:留在 fee_collector 由下块 distribution 扫走。若有其他模块在两者之间动 fee_collector 需重新评估(当前链无此情况)。

## 6. 主网影响声明

测试全程在独立 home `/home/ubuntu/.lightd-testnet` + 独立端口(26757/26758/9190)进行。主网 `lightdao-mainnet-1`(端口 26657,旧 wasmd 二进制)在整个测试期间持续正常出块(测试开始时 height 17234),**零接触、零影响**。
