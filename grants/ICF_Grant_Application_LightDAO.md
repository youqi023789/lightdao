# Interchain Foundation Grant Application — LightDAO

**申请平台：** grants.interchain.io
**填写说明：** 以下按ICF Grant申请表标准字段逐项填写，直接复制粘贴到对应表单字段即可。

---

## Field 1: Project Name

```
LightDAO — Browser-Based Light Node Network with DAO-Governed Real-World Investment
```

## Field 2: One-Line Description (≤140 characters)

```
A Cosmos SDK app-chain enabling zero-hardware browser mining via Proof-of-Contribution, with DAO governance directing real-world enterprise investment through compliant SPVs.
```

## Field 3: Project Category

```
Infrastructure / DePIN / DAO Tooling
```

## Field 4: Project Description (≤2000 characters)

```
LightDAO is a Layer 1 application chain built on Cosmos SDK that enables any internet user to participate in network security and earn rewards through their browser alone — no specialized hardware, no technical expertise, no capital requirement.

The protocol introduces three innovations to the Cosmos ecosystem:

1. BROWSER-BASED PROOF-OF-CONTRIBUTION (PoC): Light nodes run entirely in-browser via PWA technology, contributing bandwidth relay (WebRTC), block header verification (Web Worker), and session uptime (WebSocket). A three-layer verification architecture ensures contribution authenticity without trusting client-reported data: (a) random challenge-response from validators (5% of nodes every 10 minutes), (b) peer attestation (8-16 P2P peers independently record and sign data exchange volumes), (c) Merkle aggregation on-chain (per-block Root hash, O(1) storage).

2. DAO-GOVERNED REAL-WORLD INVESTMENT: Unlike pure-infrastructure DePIN projects, LightDAO connects network participation to real economic output. Token holders vote on enterprise investments (consumer chains, tech startups) executed through Cayman Islands SPVs. Profits flow back on-chain: 40% to sub-token holders, 30% to treasury for reinvestment, 20% to LIGHT buyback-and-burn, 10% to insurance fund. This creates a verifiable revenue-backed token flywheel.

3. PROGRESSIVE DECENTRALIZATION WITH BFT SAFETY: The chain launches with 10-21 Tendermint validators (f≥3 fault tolerance), expanding to 100 via community election from month 7. Governance transitions through four phases (Guardian → Co-signature → Committee → Full DAO) over 25 months, with mathematical safety guarantees at each stage.

Technical stack: Cosmos SDK v0.50+, Tendermint PoS (1.75s blocks), CosmWasm (10 core contracts in Rust), PWA frontend (React/Next.js), WebRTC P2P mesh, WebSocket gateways (50K connections/validator), IPFS frontend hosting, on-chain TWAP oracle with manipulation resistance.

Token: LIGHT, 2.5B total supply (never inflated). 40% mining (halving every 2yr), 34% investment treasury, 16% ecosystem, 10% strategic operations. Full whitepaper (36 pages) published with triple numerical audit and verified external citations.
```

## Field 5: Problem Statement (≤1000 characters)

```
The Cosmos ecosystem lacks a DePIN chain accessible to non-technical users. Existing DePIN projects (Helium, Filecoin) require $200-$1000+ hardware, limiting participation to technically capable users in developed markets. Meanwhile, 4 billion people (bottom 50% globally) own just 2% of wealth (World Inequality Report 2026), and quality investment assets remain gated behind $200K income / $1M net worth thresholds (SEC Reg D, EU MiFID II).

LightDAO addresses both gaps simultaneously: (1) a zero-hardware, browser-only DePIN chain expanding Cosmos's addressable user base beyond crypto-natives, and (2) a DAO governance model connecting token participation to real-world economic output, creating sustainable demand for LIGHT beyond speculation.

No existing Cosmos chain combines browser-based resource contribution with real-world asset investment governance. This creates a new category within the ecosystem.
```

## Field 6: Proposed Solution & Technical Approach (≤2000 characters)

```
SOLUTION: A Cosmos SDK app-chain where browser-based light nodes contribute verifiable network resources (bandwidth relay, block header verification, session uptime) and earn LIGHT tokens, while token holders govern real enterprise investments through on-chain voting.

TECHNICAL APPROACH:

Consensus Layer: Standard Tendermint PoS with 21 initial validators (expandable to 100). Block time 1.5-2s (median 1.75s). BFT tolerance f=6 at 21 validators.

Light Node Layer (Novel): PWA-based browser nodes connecting via WebSocket to validator gateways (50K connections/validator). P2P data relay via WebRTC ICE (STUN/TURN). Block header verification via Web Worker. Heartbeat via hourly signed attestations. Mobile adaptation: cumulative session scoring (4h/day = 100%), 5-min reconnection grace, PWA Background Sync bonus (+10%), delegation mechanism (70/30 split).

Contribution Verification (Novel): Three-layer architecture preventing client-side fabrication:
- Layer 1: Validator random challenges (5% of nodes/10min, 30s response window, 3 failures = daily score zeroed)
- Layer 2: Peer attestation (8-16 P2P peers independently sign data exchange records, median reported)
- Layer 3: Merkle aggregation (all node scores → single Root hash per block, O(1) on-chain, user-verifiable via Merkle Proof)

Smart Contracts: 10 CosmWasm modules (Rust): light_token, mining_reward, governance, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, insurance_fund.

Oracle: Hybrid on-chain TWAP (30-day, per-block accumulation) + external multi-source aggregation (3+ validators submit independently, median taken). Manipulation resistance: single-block deviation >5% excluded; cross-source deviation >15% triggers anomaly pause.

Wallet: Three-tier (Passkey/WebAuthn embedded → Social recovery via Shamir Secret Sharing → BIP-39 self-custody). Gas abstraction (Paymaster) for first 100 transactions per new user.

Frontend: PWA (React/Next.js + TypeScript), IPFS-hosted with CDN fallback, responsive desktop/mobile, i18n (5 languages at launch).
```

## Field 7: Milestones & Deliverables

```
Milestone 1: Smart Contract Prototype (Month 1-2)
Deliverables:
- light_token.cosmwasm (core token: transfer, burn, mint with supply cap enforcement)
- mining_reward.cosmwasm (daily settlement, Merkle Root verification, contribution scoring)
- Unit tests (≥90% coverage) + integration tests
- Technical documentation (interface specs, state machine diagrams)
Budget: $10,000
Success Criteria: Contracts compile, pass all tests, enforce 2.5B hard cap, mint only callable by mining_reward

Milestone 2: Browser Light Node Client (Month 2-3)
Deliverables:
- PWA frontend (React/Next.js) with mining dashboard
- WebSocket heartbeat + WebRTC P2P relay implementation
- Web Worker block header verification
- Cumulative session scoring (4h = 100%)
- Passkey wallet integration (WebAuthn)
- Mobile-responsive design (iOS Safari + Android Chrome tested)
Budget: $8,000
Success Criteria: 100 concurrent browser nodes maintain stable connections for 4+ hours; contribution scores calculated correctly; Passkey wallet creates/imports/signs successfully

Milestone 3: Testnet Deployment (Month 3-4)
Deliverables:
- 7-validator testnet (Docker + Ansible deployment scripts)
- Block explorer (fork of Mintscan or custom)
- Faucet for test LIGHT
- 100 external beta testers recruited and onboarded
- Stress test report (target: 5,000 concurrent light nodes)
- Anti-fraud system calibration report (target: FP rate <2%)
Budget: $7,000
Success Criteria: Testnet runs 30 days without halt; 5,000 concurrent nodes sustained; block time within 1.5-2.5s; Merkle aggregation <500ms at 5,000 nodes

Milestone 4: Security Review Preparation (Month 4)
Deliverables:
- Internal code review report (all 10 contracts)
- Audit scope document (finalized for external auditor)
- Known limitations document
- Formal verification of critical invariants (supply cap, multisig threshold, burn irreversibility) using cw-verify or equivalent
Budget: $5,000
Success Criteria: Zero critical/high vulnerabilities in internal review; formal verification proves supply cap cannot be exceeded; audit scope accepted by ≥1 external auditor
```

## Field 8: Total Budget Requested

```
$30,000 USD (or equivalent in ATOM/USDC)

Breakdown:
- Milestone 1 (Contracts): $10,000
- Milestone 2 (Light Node Client): $8,000
- Milestone 3 (Testnet): $7,000
- Milestone 4 (Security Review): $5,000

Payment preference: 30% upfront (M1 start), 70% milestone-based (upon deliverable acceptance).
```

## Field 9: Team

```
Project Lead & Protocol Design: [Your Name]
- Designed complete protocol architecture, tokenomics model (25B supply, 40/34/16/10 allocation), governance framework (dual-dimension voting, 4-phase power transfer), and legal structure (Cayman SPV + ZK-KYC)
- Authored 36-page whitepaper (V2.3) with full mathematical derivation, triple numerical audit (76 verification points, 0 inconsistencies), and verified external citations (Bessembinder 2018 JFE, Cong et al. 2021 RFS, CoinGecko 2025, World Inequality Report 2026)
- Responsible for: protocol design, community building, fundraising, legal coordination, business development
- Full-time commitment since [date]

Technical Lead: [To Be Confirmed — Recruitment Active]
- Requirements: Cosmos SDK / CosmWasm production experience, Rust proficiency, PWA/WebRTC familiarity
- Recruitment channels: Cosmos Discord, CryptoJobsList, GitHub cosmos-sdk contributors, DePIN community
- Compensation: 2-5% token allocation (12-mo cliff + 36-mo linear) from Strategic Operations Fund
- Grant funds (M1-M4) will compensate the confirmed technical lead or development studio

Note: We are transparent about not yet having a confirmed technical lead. The completeness of our technical specification (10 contract modules with full interface definitions, three-layer contribution proof design, BFT validator architecture) significantly de-risks the development phase. The grant would fund either: (a) a confirmed co-founder's compensation, or (b) a Cosmos ecosystem development studio engagement for prototype delivery.
```

## Field 10: Why Should ICF Fund This? (≤1000 characters)

```
1. ECOSYSTEM EXPANSION: LightDAO targets non-crypto-native users (browser-only, no CLI, no hardware). This directly serves ICF's mission of expanding Cosmos adoption beyond developer circles to mainstream internet users in emerging markets (Southeast Asia, Africa, Latin America).

2. NOVEL DEPIN MODEL: No existing Cosmos chain combines browser-based resource contribution with real-world asset investment governance. This creates a new category ("productive DePIN") within the ecosystem, complementary to existing infrastructure projects.

3. IBC-NATIVE: As a standard Cosmos SDK chain, LightDAO is IBC-compatible from day one, enabling cross-chain asset flows, governance interoperability, and shared security considerations with the broader Cosmos ecosystem.

4. REVENUE-GENERATING: Unlike most chains relying purely on speculation, LightDAO generates real USD revenue from enterprise investments, creating sustainable demand for LIGHT (gas fees, governance staking, sub-token exchange) and a verifiable buyback-burn flywheel.

5. OPEN SOURCE: All contracts, frontend code, infrastructure tooling, and documentation will be Apache 2.0 licensed and publicly available on GitHub.

6. REALISTIC TIMELINE: 14-month whitepaper-to-TGE with proper security audits BEFORE token launch, progressive validator decentralization, and mathematical safety guarantees at each governance phase.
```

## Field 11: Links & References

```
Whitepaper (Chinese, 36 pages): [GitHub link]
Whitepaper (English): [GitHub link]
Live Demo (PWA prototype): https://qu578he6.qwenwork.host/
GitHub Organization: [to be created]
Twitter/X: [your handle]
Discord: [your invite link]
```

## Field 12: Additional Notes

```
- This application is submitted at the "team formation" stage. We prioritize transparency over appearing more ready than we are.
- The $30K requested covers prototype development only (4 months). Full production development, security audit, and TGE preparation require additional $100-250K, which will be sourced from: (a) strategic investors (Pre-TGE sale, 75M LIGHT at $0.03-0.05), (b) additional grants, (c) community fundraising.
- We are simultaneously applying to: Filecoin DePIN Grants, DoraHacks, Encode Club Accelerator.
- All protocol design decisions are documented with mathematical derivation and academic citations. We welcome technical scrutiny.
- The live demo (https://qu578he6.qwenwork.host/) demonstrates the complete UI/UX with simulated data strictly matching whitepaper parameters (cross-audited: 0 inconsistencies across 14 parameter categories).
```

---

## 提交前检查清单

- [ ] 替换所有 [Your Name] / [date] / [link] 占位符
- [ ] 确认GitHub组织已创建并上传白皮书PDF
- [ ] 确认Twitter和Discord已注册（链接填入Field 11）
- [ ] 阅读ICF Grant最新申请指南（可能有字段变化）
- [ ] 检查字符数限制（部分字段有上限）
- [ ] 准备5分钟视频介绍（可选，但强烈推荐）

## 申请提交地址

https://grants.interchain.io

**备注：** ICF Grant为滚动申请（无固定截止日期），但评审周期通常为4-8周。建议尽早提交。
