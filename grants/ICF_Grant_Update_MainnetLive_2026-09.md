# ICF Grant — 更新与提交包(主网已上线版,2026-09-26)

> 用途:替换 9 月「团队组建期」旧申请。LightDAO 已从"提案阶段"推进到**主网运行**,本包提供需更新的字段文本 + 提交附言 + 检查清单,直接复制粘贴到 grants.interchain.io 表单。

## 0. 现状一句话(供附言/各处引用)

LightDAO 主网 `lightdao-mainnet-1` 已于 2026-09 上线:7 验证者(跨国)出块、10 个核心 CosmWasm 合约部署、浏览器轻节点挖矿闭环运行、§4.5 Gas 经济(50% 销毁/30% 验证者/20% 金库)与 §4.9 Passkey 智能钱包、§4.7 WebRTC 中继均经治理升级上线并链上验证。

---

## Field 4 更新版(项目描述,≤2000 字符)

```
LightDAO is a LIVE Cosmos SDK Layer-1 where any internet user mines via browser alone — no hardware, no CLI, no capital. Mainnet lightdao-mainnet-1 has been running since Sep 2026 with 7 geographically distributed validators and 10 audited CosmWasm contracts.

DELIVERED (on mainnet, governance-upgraded):
1. Browser Proof-of-Contribution: PWA light nodes contribute WebRTC bandwidth relay, Web-Worker block-header verification, and session uptime. Three-layer verification (validator random challenges, 8-16 peer attestation, per-block Merkle Root) prevents fabricated contributions. Daily Merkle roots are submitted by 5-of-7 validator multisig; miners claim on-chain with Merkle proofs.
2. USD-anchored gas economics (§4.5): dynamic min-gas-price = (USD target / LIGHT-USD oracle price) × 10^6 / ref-gas; every fee splits 50% burn / 30% validators / 20% treasury — verified on-chain (exact 50/30/20 on real transactions).
3. Passkey smart wallet (§4.9): seedless WebAuthn login (PRF-derived AES-GCM encrypted seed) + Shamir 3-of-5 social recovery; mnemonic retained as fallback.
4. WebRTC relay fleet (§4.7): 8 coturn TURN/TURNS nodes across 7 regions + WSS signaling + REST temporary credentials; client P2P data-channel relay with real byte metering feeding the 40% bandwidth score.
5. DAO-governed upgrades: all chain upgrades executed via x/upgrade governance proposals with coordinated 7-node swaps (auto-swap watchers), rehearsed end-to-end on testnet first.

Token LIGHT: 2.5B fixed supply, emission solely via mining_reward contract (native mint inflation governance-zeroed to prevent double emission).
```

## Field 6 更新版(技术方案,≤2000 字符)

```
LIVE ARCHITECTURE (Cosmos SDK v0.50 / wasmd v0.55 / CometBFT v0.38):
- Consensus: Tendermint BFT, 7 validators (f=2), ≥7 enforced as TGE hard floor; expandable via governance.
- Light node layer: PWA client (vanilla JS + cosmjs, i18n zh/en/es) over WebSocket gateways; WebRTC ICE (STUN-first, TURN/TURNS fallback on 8 regional coturn nodes); Web Worker header verification; heartbeat Merkle aggregation O(1) on-chain.
- Contribution verification: validator random challenges (5%/10min), peer attestation median (8-16 peers), per-block Merkle Root; 3 failed challenges zero the day's score.
- Contracts (Rust/CosmWasm, audited): light_token, mining_reward, governance, treasury_multisig(5/7), subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, insurance_fund.
- Oracle (§4.10): validator-rotated external price submission (external_median, live) + on-chain 30d TWAP (activates with LIGHT/USDC pool); >±15% deviation flags anomaly, >5% single-block excluded.
- Wallet: Passkey/WebAuthn (PRF→AES-GCM encrypted seed) + Shamir 3-of-5 social recovery + BIP-39 fallback.
- Gas: custom x/lightfee module (ante USD-anchored min-gas + EndBlock 50/30/20 split); params moving on-chain (governance-adjustable) in v3 upgrade.
- Upgrades: x/upgrade governance + coordinated multi-node swap with auto-swap watchers; testnet-rehearsed before every mainnet upgrade.
```

## Field 7 更新版(里程碑:1-3 已交付,资助转向下一阶段)

```
ALREADY DELIVERED (no funding requested — de-risks the grant):
- M1 Contracts: 10 CosmWasm contracts built, audited, deployed to mainnet; supply cap + multisig enforced on-chain.
- M2 Client: PWA live at lightdao.net with mining dashboard, Passkey wallet, WebRTC relay; multi-language.
- M3 Network: 7-validator mainnet + testnet; governance upgrades executed; daily Merkle roots submitting.

REQUESTED FUNDING — NEXT PHASE ($30,000):
Milestone A: Independent mainnet security audit (lightfee module + relay metering + wallet crypto), $14,000
  Success: 0 critical/high unresolved; report published.
Milestone B: Light-node scaling to 5,000 concurrent (gateway + relay load test, anti-fraud FP<2% report), $9,000
  Success: sustained 5k nodes, Merkle aggregation <500ms.
Milestone C: Ecosystem tooling — block explorer + public metrics dashboard + i18n to 5 languages, $7,000
  Success: explorer live indexing mainnet; dashboard public.
Payment: 30% upfront, 70% milestone-based.
```

## Field 11 更新版(链接)

```
Live client (mainnet): https://lightdao.net
Whitepaper V2.4 (EN/CN, mainnet-live edition): https://github.com/youqi023789/lightdao/whitepaper/
Mainnet status & endpoints: https://github.com/youqi023789/lightdao/docs/MAINNET_STATUS.md
GitHub: https://github.com/youqi023789/lightdao
Testnet rehearsal & upgrade runbooks: https://github.com/youqi023789/lightdao/docs/
Twitter/X: [your handle]   Discord/Telegram: [invite]
```

## Field 12 更新版(附加说明)

```
- Status changed since draft: mainnet is LIVE (Sep 2026), not pre-prototype. Milestones 1-3 of the original plan are delivered and on-chain verifiable; this request funds the NEXT phase (audit, scaling, tooling).
- All chain upgrades to date were executed via on-chain governance with coordinated validator swaps and prior testnet rehearsal — demonstrating the governance maturity ICF looks for.
- Known honest limitations: no real-user traffic yet (growth is the current focus); LIGHT not yet on a DEX (on-chain TWAP activates with liquidity; oracle currently validator-fed reference price); native mint inflation governance-zeroed to keep emission single-source.
- Open source: chain module, contracts, client, and infra tooling published under Apache-2.0/MIT at https://github.com/youqi023789/lightdao.
```

## 提交附言(cover note,粘贴到附加字段或邮件)

```
Subject: LightDAO — Grant Application Update: Mainnet Now Live

Dear ICF Grants Team,

Since drafting our application, LightDAO has progressed from team-formation to a live mainnet
(lightdao-mainnet-1, 7 validators, 10 audited CosmWasm contracts). Browser-based Proof-of-Contribution
mining, USD-anchored gas economics with 50/30/20 fee split, Passkey smart wallets, and an 8-node WebRTC
relay fleet are all deployed and on-chain verifiable; every chain upgrade has run through governance
with testnet rehearsal first.

We have updated Fields 4/6/7/11/12 to reflect delivered work and now request funding for the next
phase only: an independent mainnet security audit, 5,000-node scaling validation, and public ecosystem
tooling (explorer + metrics). Delivered milestones are offered as evidence of execution, not as
funding requests.

Repository, live client, and mainnet status document are linked in Field 11. We welcome technical
scrutiny of any on-chain claim.

Thank you for considering LightDAO.
[Your Name], Project Lead
```

## 提交前检查清单

- [ ] 建仓并 push 后,把 https://github.com/youqi023789/lightdao 占位符全部替换为真实 URL
- [ ] Field 9 Team:填你的名字 + 技术负责人现状(可写"协议工程已由主网交付证明,审计阶段聘外部审计")
- [ ] Field 11 补 Twitter/Discord(增长运营产出后填)
- [ ] 核对 grants.interchain.io 当前字段与字符上限
- [ ] 附 5 分钟主网演示视频(录 lightdao.net 挖矿+Passkey+领取,强烈建议)
- [ ] 提交后记录 submission ID,4-8 周评审期内按附言邮箱跟进
