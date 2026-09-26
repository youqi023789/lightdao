# LightDAO — DePIN 轻节点挖矿网络

**把闲置设备变成收益**:浏览器即轻节点,贡献带宽/在线/验证/稳定性,赚取原生 LIGHT 代币。基于 Cosmos SDK + CosmWasm 的应用链 `lightdao-mainnet-1`。

> 🟢 **主网已上线并运行**。Gas 经济(§4.5)、WebRTC 中继(§4.7)、Passkey 智能钱包(§4.9)、TGE vesting(§4.4)均已部署主网并验证。见 [docs/MAINNET_STATUS.md](docs/MAINNET_STATUS.md)。

## 是什么

LightDAO 是一个 **DePIN(去中心化物理基础设施网络)**:用户用浏览器运行轻节点,贡献真实网络资源(带宽中继、区块头验证、在线时长、稳定性),按 **PoC 贡献证明** 获得 LIGHT 奖励。无需矿机、无需高能耗算力。

- **网页即客户端**:PWA,打开 [lightdao.net](https://lightdao.net) 即可挖矿,无需安装
- **Passkey 智能钱包**:无助记词,生物识别登录 + Shamir 3-5 社交恢复(§4.9)
- **WebRTC P2P 中继**:节点间数据通道互中继,TURN 兜底,中继量计入贡献(§4.7)
- **USD 锚定 Gas + 通缩**:每笔手续费 50% 销毁 / 30% 验证者 / 20% 金库(§4.5)
- **公平发行**:2.5B LIGHT,挖矿合约按 epoch 释放,无预挖滥发

## 仓库结构

| 目录 | 内容 |
|---|---|
| `chain/` | wasmd v0.55 fork 的 `x/lightfee` 模块(§4.5 Gas 经济)+ app/ante 补丁 + 升级补丁脚本 |
| `contracts/` | 10 个核心 CosmWasm 合约(经审计):light_token、mining_reward、governance、treasury_multisig、oracle_twap、vesting 等 |
| `client/` | 网页客户端(PWA):挖矿 + Passkey 钱包 + WebRTC 中继;含 staging 测试页 |
| `infra/` | 打分网关、WebRTC 信令服务器、TURN 凭证端点、coturn 部署、oracle 喂价器、节点升级脚本 |
| `docs/` | 测试报告、主网升级 runbook、Passkey 钱包说明、WebRTC TURN 成本估算、主网实况 |
| `whitepaper/` | 白皮书(§4 技术经济模型) |
| `grants/` | ICF(Interchain Foundation)grant 申请 |

## 快速开始(用户)

1. 打开 https://lightdao.net
2. 「Passkey 钱包」→ 创建(生物识别)→ 自动进入挖矿
3. 点「开始挖矿」→ 贡献带宽/在线/验证 → 累计贡献分
4. 每日定稿后「领取奖励」→ LIGHT 到账(Merkle proof 链上验证)

## 快速开始(验证者/开发者)

- 链:`lightdao-mainnet-1`,7 验证者(JP/KR/SG/US/HK/FR/UK),denom `ulight`(LIGHT,6 位小数)
- RPC:`https://lightdao.net/rpc/` · 网关:`https://lightdao.net/gw/` · 信令:`wss://lightdao.net/signal` · TURN 凭证:`https://lightdao.net/turn/`
- 构建 lightd:见 `chain/patches/`(wasmd v0.55.0 + 三个补丁脚本),go 1.23.6
- 合约交互:CosmWasm,地址见 `docs/MAINNET_STATUS.md`

## 安全与审计

- 核心合约经独立审计(见 `contracts/` 内审计报告);挖矿根提交为 5/7 验证者多签
- Passkey 钱包:种子仅以 WebAuthn-PRF 派生密钥 AES-GCM 密文存储,明文不落地;Shamir 3-of-5 社交恢复
- 主网升级为 x/upgrade 治理提案 + 全节点协调切换,测试网端到端彩排后执行

## 状态与路线

- ✅ 主网 LIVE:挖矿闭环、Gas 经济、Passkey 钱包、WebRTC 中继、vesting
- 🔄 动态 oracle 价(v3 升级后激活)、参数链上治理
- ⬜ 真实用户增长、社区中继节点规模化、LIGHT/USDC 流动性池(启用链上 TWAP)

## 许可与联系

代码 Apache-2.0(合约)/ MIT(客户端)。社区与治理见链上 governance 合约。
