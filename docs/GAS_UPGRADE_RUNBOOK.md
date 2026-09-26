# LightDAO 主网 §4.5 Gas 经济升级 Runbook(协调升级)

**适用**: 将 `x/lightfee` 模块部署到 `lightdao-mainnet-1`(7 验证者)
**前提**: 测试网彩排已通过(见 `TEST_REPORT.md`)
**性质**: ⚠️ **共识破坏性升级** — BeginBlocker/EndBlocker 写状态,**必须 7 节点在同一块高协调切换**,不可单机灰度

---

## 0. 关键背景(必读)

### 0.1 为什么不能"1 节点灰度"
lightfee 在每块 BeginBlock 更新价格、EndBlock 转移 fee_collector 资金 → 改变 app_hash。若只升 1 台、其余 6 台跑旧二进制,升级节点算出的状态根与其他人不同 → 提议被拒 → 100 块内被 jail。**唯一安全路径 = x/upgrade 治理提案设定升级块高 H,7 节点在 H 同时换二进制。**

### 0.2 ⚠️ 主网 denom 脑裂(升级前必须决策)
当前主网 genesis 存在配置矛盾(2026-09-22 链上核实):
- `staking.bond_denom = ulight`(质押/治理用 ulight)
- `mint.mint_denom = stake`(原生通胀却 mint stake — **错误**)
- 总供应:**ulight = 2,500,000,000,000,000(25 亿 LIGHT,真币)** + **stake = 929,434,918,668(92.9 万,垃圾 denom,持续被通胀)**
- mint 参数:inflation 0.13 / blocks_per_year 6311520

**关键认知(纠正早期判断)**:白皮书的挖矿发行走 **mining_reward 合约**(pool_balance=10 亿 LIGHT,daily_release≈68.5 万/天,epoch 机制),**不是原生 mint 模块**。因此:
- 原生 mint 通胀 stake 是**纯垃圾发行**:验证者质押 ulight,却从 distribution 拿到无用的 stake 奖励
- ❌ **不要**把 mint_denom 改成 ulight —— 那会让原生 mint 和 mining_reward 合约**双重发行 LIGHT**,破坏白皮书总量模型
- ✅ **正确修法**:把原生 mint 通胀**归零**(inflation_min=inflation_max=0,或 mint_denom 设为一个不发行的占位),发行完全交给 mining_reward 合约

**对 ① lightfee 升级的影响**:
- lightfee 主网必须配 `LIGHTDAO_DENOM=ulight`(gas 以真 LIGHT 计价)
- lightfee.EndBlock 只抽 fee_collector 的 **ulight** 余额(用户付的 ulight gas fee),不碰 stake → 与 distribution 无冲突
- lightfee 升级**不依赖** mint 修复,两者解耦

**决策点(升级前回答)**:
- [ ] A. 本次只上 lightfee(denom=ulight);mint 垃圾发行留到独立提案处理(推荐,解耦)
- [ ] B. lightfee 升级 + 同窗口提交「mint 通胀归零」gov 参数提案(两个独立提案,可同批投票)

> mint 归零是 **gov 参数提案(MsgUpdateParams),无需换二进制、无共识 halt**,比 lightfee 升级简单得多,可独立或同批进行。命令见 §7。

### 0.3 节点清单(7 验证者)
从主网 `persistent_peers` 提取的 7 个 IP(升级前用 `status` 确认每台 moniker):

| moniker | 推测密钥文件 | P2P IP | node_id |
|---|---|---|---|
| val01-jp | `ariben.pem` | 待确认 | 78f5b4b9… / 47.245.63.27 等 |
| val02-kr | `ahanguo.pem` | 待确认 | |
| val03-sg | `txinjiapo.pem` | **43.160.218.196** | bc506d556b01cb50c4284b92b2e69b32a6b65568 |
| val04-us | `ameiguo.pem` | 待确认 | |
| val05-hk | `axianggang.pem`/`txianggang.pem` | 待确认 | |
| val06-fr | `tfaguo.pem` | 待确认 | |
| val07-uk | `ayingguo.pem` | 待确认 | |

7 个 P2P 端点(完整):
```
78f5b4b96849a9073ac52764a9de0091cc8e461f@47.245.63.27:26656
4ceadc027548f04ff8dd845afdc7b4726e1a2850@43.108.80.121:26656
bc506d556b01cb50c4284b92b2e69b32a6b65568@43.160.218.196:26656   ← SG val03
58b604661cad23798244bb5f8064b32b60457e45@47.85.97.63:26656
83b486553b87537838fb5d74b580f44c5079050b@47.82.73.162:26656
e8a8eba0b1ac40752145b70273428ee58cc84d55@43.165.3.88:26656
a346e94e16149dcbf02cc73f12d684d252fe80d6@8.208.114.196:26656
```
密钥目录:`C:\Users\33635\Desktop\哈哈\*.pem`

### 0.4 治理参数(已查)
- `min_deposit`: 10000000 ulight
- `voting_period`: 48h
- `quorum`: 0.334,`threshold`: 0.5
- 当前无待执行 upgrade plan

---

## 1. 升级前准备(T-1 天)

### 1.1 分发二进制到 7 节点
新二进制在 SG:`/home/ubuntu/lightd`(sha256 `34d8f5317c3a177dcd0805c084bad5230dd4ff5eaf445b218b865da1e6cbd24f`,含 lightfee + v2-lightfee 升级处理器)

对每个节点(IP 替换 `<IP>`,密钥替换 `<KEY>.pem`):
```bash
# 从 SG 跳到其他节点,或先 scp 到本地再分发。校验 sha256 一致!
scp -i <KEY>.pem /home/ubuntu/lightd ubuntu@<IP>:/home/ubuntu/lightd.new
ssh -i <KEY>.pem ubuntu@<IP> 'sha256sum /home/ubuntu/lightd.new'
# 必须 == 34d8f5317c3a177dcd0805c084bad5230dd4ff5eaf445b218b865da1e6cbd24f
```
> 注:SG 本身已有 `/home/ubuntu/lightd`。当前 SSH 可达 = SG(txinjiapo.pem)+ FR(43.165.3.88, tfaguo.pem);HK(47.82.73.162)仅 RPC 可达;其余 4 台需先把本机出口 IP 加入其腾讯云安全组,或由你本人在这 4 台执行。

### 1.2 每台设置 lightfee 环境变量(systemd unit 或启动脚本)
```bash
LIGHTDAO_DENOM=ulight                    # ← 主网用 ulight,不是 stake!
LIGHTDAO_STATIC_PRICE_USD=0.05           # oracle 未喂价前的静态回退
LIGHTDAO_TREASURY_ADDR=<金库 bech32>     # 20% 去向;建议用 treasury_multisig 合约地址
LIGHTDAO_TRANSFER_USD=0.001              # 白皮书 §4.5 参考转账 USD 目标
# 可选:LIGHTDAO_ORACLE_CONTRACT=<oracle_twap 合约 bech32>(喂价后启用)
```
主网 treasury_multisig 合约(来自 MEMORY):`wasm1ndygz3lmlpmgeskucpd8vrrw33e7aj53956l435vquyjcp54r4ns762vxn`

> ⚠️ 7 台的 env **必须完全一致**,否则各节点算出不同 min_gas_price/分配 → 状态分叉。

### 1.3 升级名与处理器(已注册 + 已彩排验证)
升级名:`v2-lightfee`。已在 `app/upgrades.go` 注册处理器:
```go
var Upgrades = []upgrades.Upgrade{v050.Upgrade, noop.NewUpgrade("v2-lightfee")}
```
lightfee 无独立 KV store,故用 noop 处理器(只跑 RunMigrations,无状态迁移)。**测试网已端到端验证**:旧二进制在 H halt → 换 lightd → 日志 `applying upgrade "v2-lightfee" at height: H` → 链恢复出块 → lightfee 生效(见 §8 彩排证据)。

---

## 2. 提交治理升级提案(T 时刻)

**实测可用的命令形式**(wasmd v0.55 用 MsgSoftwareUpgrade JSON,非 legacy 子命令)。gov authority 地址(wasm 前缀)= `wasm10d07y265gmmuvt4z0w9aw880jnsr700js7zslc`。

先写提案 JSON(`<H>` 替换为目标块高):
```json
{
  "messages": [{
    "@type": "/cosmos.upgrade.v1beta1.MsgSoftwareUpgrade",
    "authority": "wasm10d07y265gmmuvt4z0w9aw880jnsr700js7zslc",
    "plan": {"name": "v2-lightfee", "height": "<H>", "info": "lightfee gas economics"}
  }],
  "metadata": "lightfee-v2",
  "deposit": "10000000ulight",
  "title": "LightDAO v2-lightfee upgrade",
  "summary": "Deploy x/lightfee: USD-anchored min-gas-price + 50/30/20 fee split."
}
```
提交(在 SG 节点):
```bash
wasmd tx gov submit-proposal /tmp/proposal.json \
  --from <有≥10000000 ulight 的账户> \
  --chain-id lightdao-mainnet-1 --node tcp://127.0.0.1:26657 \
  --gas 400000 --gas-prices 0.025ulight -y
```
**选 H**:当前高度 + 足够投票时间(48h voting + 缓冲)。块间隔 ~5s → 48h ≈ 34560 块 → H ≈ 当前 + 40000(留余量)。投票通过后 H 固定不可改。

### 2.1 投票(7 验证者,需 >50% 投票权赞成,quorum 33.4%)
```bash
wasmd tx gov vote <proposal-id> yes --from valXX --chain-id lightdao-mainnet-1 \
  --node tcp://127.0.0.1:26657 --gas 200000 --gas-prices 0.025ulight -y
```
**注意**(来自 MEMORY):链重置会清 gov 质押 → 提案前确认验证者已质押 ulight 有投票权。每个验证者用各自 operator key 投。

---

## 3. 协调切换(块高 H,T+48h 后)

### 3.1 切换前(所有 7 台)
- 确认 `/home/ubuntu/lightd.new` sha256 正确
- 确认 env 变量已写入启动配置
- 备份当前二进制:`cp /usr/local/bin/wasmd /usr/local/bin/wasmd.v1.bak`
- **所有人在线待命**(无 cosmovisor,需手动换)

### 3.2 H 到达时
每台节点会在 H 高度 panic 退出,日志:
```
ERR UPGRADE "v2-lightfee" NEEDED at height: <H>
```
**立即在 7 台同时执行**:
```bash
# 停旧进程
sudo systemctl stop wasmd   # 或 pkill -x wasmd
# 换二进制
sudo cp /home/ubuntu/lightd.new /usr/local/bin/wasmd
sudo chmod +x /usr/local/bin/wasmd
# 带 lightfee env 重启
sudo systemctl start wasmd  # env 已在 unit 文件;或手动 export 后启动
```

### 3.3 切换窗口
- 7 台必须在 **H 后尽量短的时间内**(建议 < 5 分钟)全部换完重启
- 若 >1/3 投票权未及时恢复 → 链暂停出块(但不会丢状态,补齐后自动继续)
- 无真实用户(已确认),容错空间大;极端情况可 `comet unsafe-reset-all` 重来

---

## 4. 升级后验证(T+48h+10min)

```bash
NODE=tcp://127.0.0.1:26657
# 1) 链恢复出块
wasmd status --node $NODE | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print('height',d['sync_info']['latest_block_height'],'catching',d['sync_info']['catching_up'])"

# 2) lightfee 价格事件(每块应有)
curl -s http://127.0.0.1:26657/block_results?height=<最新> | python3 -c "
import sys,json,base64
r=json.loads(sys.stdin.read()).get('result',{})
for e in r.get('finalize_block_events',[]):
    if 'lightfee' in e.get('type',''):
        print(e['type'],{base64.b64decode(a['key']).decode():base64.b64decode(a['value']).decode() for a in e['attributes']})
"

# 3) 发一笔 ulight fee 交易,验证 min-gas-price(0.2 ulight/gas)
#    足额:--gas 200000 --fees 50000ulight  → code 0
#    不足:--gas 200000 --fees 1000ulight   → code 13 + USD-anchored 错误

# 4) 验证 50/30/20:查 burn/treasury 地址余额增量
#    burn = authtypes.NewModuleAddress("lightdao_burn_v1")(用 addrtool 算,见下)
```
burn 地址计算工具(在 SG wasmd-src 下跑):
```bash
cd /home/ubuntu/wasmd-src && go run /tmp/addrtool/main.go   # 已存在,打印 wasm1... burn/treasury
```

---

## 5. 回滚预案

若升级后链异常(状态分叉/panic 循环):
1. 7 台同时停节点
2. 恢复旧二进制:`sudo cp /usr/local/bin/wasmd.v1.bak /usr/local/bin/wasmd`
3. **但**:若已在 H 高度用新二进制提交过块,旧二进制无法重放新状态 → 需从 H-1 的快照恢复,或 `unsafe-reset-all` + 从 H 前重新同步
4. 因无真实用户,最坏情况 = 全体 reset 到升级前快照重启(状态不丢用户资产,因无用户)

**强烈建议**:升级前对 7 台各做数据快照:
```bash
sudo systemctl stop wasmd
sudo tar czf /home/ubuntu/wasmd-backup-H-$(date +%s).tgz -C /home/ubuntu .wasmd/data .wasmd/config/genesis.json
sudo systemctl start wasmd
```

---

## 6. 升级后待办(下一段)

1. **修 mint 垃圾发行**:把原生 mint 通胀**归零**(不是改成 ulight——会和 mining_reward 合约双重发行)。见 §7 独立 gov 参数提案。
2. **oracle 喂价**:给 oracle_twap 合约接真实 LIGHT/USD 价格源,设 `LIGHTDAO_ORACLE_CONTRACT`,min-gas-price 转为动态
3. **参数链上治理化**:把 lightfee 的 BurnPct/TreasuryPct/TransferUsdTarget 做成 governance 可调,免再次协调升级
4. **原生 denom 重构收尾**:确认存量 stake(92.9 万)的处置(兑换/销毁),统一为单一 ulight

---

## 7. mint 垃圾发行归零(独立 gov 参数提案,无需换二进制)

原生 mint 当前通胀 stake(垃圾 denom)。白皮书发行由 mining_reward 合约负责,故应把原生通胀归零。这是 **MsgUpdateParams 参数提案,无共识 halt**,可独立或和 lightfee 升级同批投票。

提案 JSON(把 inflation_min/max/rate_change 全设 0,保留其他字段):
```json
{
  "messages": [{
    "@type": "/cosmos.mint.v1beta1.MsgUpdateParams",
    "authority": "wasm10d07y265gmmuvt4z0w9aw880jnsr700js7zslc",
    "params": {
      "mint_denom": "stake",
      "inflation_rate_change": "0.000000000000000000",
      "inflation_max": "0.000000000000000000",
      "inflation_min": "0.000000000000000000",
      "goal_bonded": "0.670000000000000000",
      "blocks_per_year": "6311520"
    }
  }],
  "metadata": "stop-junk-stake-inflation",
  "deposit": "10000000ulight",
  "title": "Zero native mint inflation (emission via mining_reward contract)",
  "summary": "Native mint currently inflates junk 'stake' denom. Whitepaper emission is contract-driven (mining_reward). Set inflation to 0."
}
```
提交 + 投票同 §2/§2.1(`wasmd tx gov submit-proposal /tmp/mint.json ...`)。生效后 mint 每块发行 0,验证者奖励改由 mining_reward 合约的 LIGHT 发行承担。

> ⚠️ 归零前确认:mining_reward 合约的 daily_release 发放路径确实把 LIGHT 发到验证者/矿工,否则归零后验证者将暂无奖励。建议归零提案与「确认合约发放正常」同批评估。

---

## 8. 测试网升级彩排证据(2026-09-22,已完整跑通)

在 `lightdao-testnet-gas`(单验证者)用**主网旧 wasmd 二进制**(0 lightfee)→ **新 lightd**(53 lightfee + v2-lightfee 处理器)完整演练:

| 步骤 | 实测结果 |
|---|---|
| gov MsgSoftwareUpgrade 提案 | code 0,id=1,进入 VOTING_PERIOD |
| 投票(验证者 100% 权) | code 0,提案 PASSED |
| 旧二进制到 H=123 | `ERR UPGRADE "v2-lightfee" NEEDED at height: 123` → CONSENSUS FAILURE → halt ✅ |
| 换 lightd 重启 | `INF applying upgrade "v2-lightfee" at height: 123` ✅ |
| 链恢复 | height 130→187 持续出块,无 panic ✅ |
| 升级后 lightfee | 不足额 fee code 13 拒绝;足额 code 0;burn+50000/treasury+20000(精确 50/20);price_update 事件恢复 ✅ |
| 升级计划 | `q upgrade plan` = {}(已清空,不再 halt)✅ |

**结论:主网升级流程已证明机械可复现,风险接近零。** 主网与彩排唯一差异 = 7 节点需在 H 后短窗口内全部换二进制(>1/3 投票权未及时恢复会暂停出块,补齐后自动继续;无真实用户,容错大)。

---

## 附:本次升级不改动的内容
- 10 个 CosmWasm 合约(code 1-10)不变
- 验证者集合/质押不变
- 客户端/nginx/gateway 不变(lightfee 是链层,对前端透明)
- 测试网 `lightdao-testnet-gas`(SG 26757,systemd `lightd-testnet`)保留作持续验证环境
