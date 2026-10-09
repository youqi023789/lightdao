# LightDAO 主网实况(Mainnet Status)

**链**: `lightdao-mainnet-1` · Cosmos SDK v0.50.12 / wasmd v0.55.0 / CometBFT v0.38.15
**原生代币**: `ulight`(LIGHT,6 位小数)· 总供应 2,500,000,000 LIGHT(2.5e15 ulight)· 质押/治理/ Gas 均用 ulight
**验证者**: 7(满足 BFT 下限 f=2)· 全部 BONDED、无 jailed

| moniker | 区域 | P2P IP |
|---|---|---|
| val01-jp | 日本 | JP_ENDPOINT |
| val02-kr | 韩国 | KR_ENDPOINT |
| val03-sg | 新加坡 | SG_ENDPOINT |
| val04-us | 美国 | US_ENDPOINT |
| val05-hk | 香港 | HK_ENDPOINT |
| val06-fr | 法国 | FR_ENDPOINT |
| val07-uk | 英国 | UK_ENDPOINT |

(+1 备用中继节点 XG_ENDPOINT)

## 公共端点

| 服务 | 地址 |
|---|---|
| 网页客户端(PWA) | https://lightdao.net |
| CometBFT RPC | https://lightdao.net/rpc/ |
| 打分网关 | https://lightdao.net/gw/ |
| WebRTC 信令(WSS) | wss://lightdao.net/signal |
| TURN 临时凭证 | https://lightdao.net/turn/ |
| TURN/TURNS 中继 | turn-{jp,kr,sg,us,hk,fr,uk,8}.lightdao.net :3478(UDP/TCP)/ :5349(TLS) |

## 核心合约(code_id → 地址)

| 合约 | 地址 |
|---|---|
| light_token (CW20, LIGHT) | wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z |
| mining_reward(挖矿池 10亿 LIGHT) | wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx |
| governance(DAO) | wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt |
| treasury_multisig(金库 5/7) | wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u |
| oracle_twap(价格预言机) | wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace |
| vesting(TGE 锁仓) | wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x |

(其余:subtoken_factory、anti_fraud、validator_registry、insurance_fund,code 5/7/8/10)

## §4.5 Gas 经济(已上线,2026-09-24 v2-lightfee @ height 58627)

- **USD 锚定动态 min-gas-price**:`min_gas = (转账USD目标 $0.001 / LIGHT-USD价) × 10⁶ / 参考gas 100000`。当前价 $0.05 → **0.2 ulight/gas**
- **手续费分配**:50% 销毁 → `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(死地址)/ 30% 验证者 / 20% 金库(treasury_multisig)。主网实测精确匹配
- **mint 通胀已归零**(gov 提案 2):原生 mint 不再增发垃圾 `stake`;LIGHT 发行完全由 mining_reward 合约承担,避免双重发行
- 价格源:oracle_twap `external_median`(7 验证者 cron 轮值喂价,当前 50000=$0.05);v3 升级后 lightfee 直接读 oracle 转动态价

## 升级历史

| 升级 | 高度 | 状态 |
|---|---|---|
| v2-lightfee(Gas 经济) | 58627 | ✅ 已应用(2026-09-24),7 节点看门狗自动切换 |
| v3-lightfee(oracle 动态价 + 参数链上治理) | 118055 | 🔄 gov 提案 3 全票通过,~2026-09-28 自动切换 |

升级机制:x/upgrade 治理提案 + 全节点同块高协调;每台部署 auto-swap 看门狗(检测 `UPGRADE … NEEDED` 自动换二进制重启),测试网端到端彩排后执行。

## §4.4 vesting(TGE 三段,已上线)

3 个独立 schedule:vault 250,000,000 LIGHT → 75M(cliff 0)/ 100M(cliff 1 年)/ 75M(cliff 2 年)。

## 治理(DAO,已上线)

10 类提案(micro 55% / acquisition 60% / vc 60% / major 66% / emergency 75% 通过线,低投票率动态抬升门槛);双维度计票(代币权重 yes% + 地址数 yes%)。质押为原生 ulight 托管(Stake 附带原生币,Unstake 原路退回)。governance 合约自身为 admin,可通过提案自我迁移或调用/迁移任意目标合约。

**投票期修复(2026-09-26)**:初始实例化遗留 `voting_period_secs=30`(测试值)。已通过提案 #8 自我迁移到 code_id 11,置 `voting_period_secs=null`,恢复按类型的默认投票期——普通提案 7 天、紧急提案 1 天。链上验证:contract-history 显示 INIT(code 3,period=30)→ MIGRATE(code 11,period=null)@ 区块 81955。

## §4.7 WebRTC 中继(已上线)

8 节点 coturn(TURN/STUN,TLS 证书 turn-*.lightdao.net)+ WSS 信令 + REST 临时凭证(HMAC-SHA1)。客户端 P2P 数据通道互中继,中继字节计入 40% 带宽贡献分;对称 NAT 走 TURN 兜底,失败降级纯验证模式。

## 挖矿闭环(已上线)

浏览器贡献(带宽/在线/验证/稳定)→ 打分网关每日定稿 → Merkle 根 5/7 验证者多签提交 mining_reward → 矿工凭 proof 链上领取。每日根已持续上链。

## 社区与增长

- X: [@lightdaoproto](https://x.com/lightdaoproto);首发线程 2026-09-26(8 帖):https://x.com/lightdaoproto/status/2103791251367825588
- Season 1 治理提案 #4(2026-10-01→10-29,5M LIGHT 池,邀请+10% 首周):7/7 通过
- 邀请裂变:网关记录 referrals,赛季末从 S1 池结算(每日根保持纯 PoC)
