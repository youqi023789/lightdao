# LightDAO 增长运营工具包(零预算 · 社区优先 · 可直接复制)

> 原则:$0 现金预算 → 全部用「代币激励 + 社区自组织 + 免费渠道」。LIGHT 本身就是获客货币(贡献即挖矿)。
> 目标人群:无硬件/无技术背景的全球普通网民(东南亚/拉美/非洲/南亚优先,白皮书 CAC $55/人 区间低端)。

## 0. 定位一句话(所有文案的母版)

- EN: "Mine crypto with just your browser. No hardware, no seed phrase, no money down — contribute bandwidth & uptime, earn LIGHT."
- 中: "只用浏览器就能挖矿。无硬件、无助记词、零投入——贡献带宽与在线时长,赚 LIGHT。"

---

## 1. X/Twitter(首发线程,直接复制)

```
🧵 1/8 Most "mining" needs $2k of hardware. LightDAO needs nothing but your browser.

Mainnet is LIVE. 7 validators. 10 audited contracts. Browser light-nodes already earning LIGHT by relaying bandwidth & verifying block headers.

No seed phrase either — you log in with your fingerprint. 🧵👇

2/8 What you actually do:
• Open lightdao.net (no install, PWA)
• Create a Passkey wallet (biometric, seedless, Shamir social-recovery)
• Hit "Start Mining"
• Your browser contributes: bandwidth relay (WebRTC), block-header verification, uptime, stability

3/8 How we know you're not faking it (Proof-of-Contribution):
• Validators randomly challenge 5% of nodes every 10 min
• 8–16 P2P peers independently attest your data exchange (median wins)
• All scores → one Merkle Root per block, on-chain, self-verifiable

4/8 The tokenomics that make it deflationary:
Every gas fee: 50% BURNED 🔥 / 30% validators / 20% treasury.
USD-anchored gas: a reference transfer costs ~$0.001 regardless of LIGHT price.
2.5B hard cap. Emission only via the mining contract. Native inflation governance-zeroed.

5/8 Wallet UX most chains can't match:
Passkey/WebAuthn login (no seed to lose), Shamir 3-of-5 social recovery via guardians you trust. Mnemonic kept only as an optional fallback.

6/8 Infra is real, not a whitepaper:
8-region TURN/TURNS relay fleet + WSS signaling + REST TURN creds. Your relayed bytes are metered on-device and score 40% of your mining reward.

7/8 Governance isn't cosmetic:
Every chain upgrade so far passed on-chain votes (7/7 validators) with testnet rehearsal first — including the fee-split module and the inflation fix.

8/8 Try it (testnet-phase, no real value yet):
https://lightdao.net
Repo, mainnet status & whitepaper V2.4: https://github.com/youqi023789/lightdao
Mine with your idle laptop. That's the whole pitch. ⛏️
```

**置顶帖(短)**:
```
LightDAO = browser-only DePIN mining. Live mainnet, seedless Passkey wallet, 50% fee burn.
Start: https://lightdao.net · Docs: https://github.com/youqi023789/lightdao · Community: [TG/Discord]
```

**每周更新模板**:
```
LightDAO Weekly — W[nn]
✅ Shipped: [1-3 条,带链接/高度]
📈 Network: [validators] vals · [height] height · [miners] miners · [relayed] GB relayed
🔥 Burned: [X] LIGHT (50% of fees)
👷 Next: [1-2 条]
Proof: [tx/区块链接]
```

---

## 2. Telegram / Discord(建群首条公告,直接复制)

```
👋 Welcome to LightDAO — mine with your browser, no hardware.

What this is: a live Cosmos chain where idle devices earn LIGHT by relaying bandwidth (WebRTC) + verifying block headers. Seedless Passkey wallet. 50% of every gas fee is burned.

Start in 60 seconds:
1) https://lightdao.net
2) Create Passkey wallet (fingerprint/face)
3) Start Mining → contribute → claim daily

House rules: no shilling other tokens, no seed/privkey EVER asked (anyone asking = scam, report), English/中文/ES welcome.

Links: Whitepaper V2.4 [repo] · Mainnet status [repo] · GitHub [repo]
Current phase: testnet-value (no real assets yet) — perfect time to farm contribution score.
```

**欢迎机器人/固定消息**:同上精简版 + 「邀请 3 人并进群 → Season-1 贡献加成」(见 §5 活动)。

---

## 3. Reddit(两帖,直接复制)

**r/Cosmos / r/cosmosnetwork:**
标题: `We built a Cosmos L1 where mining = leaving a browser tab open (mainnet live, 7 validators, PoC not PoW)`
正文:
```
TL;DR: LightDAO is a live Cosmos SDK chain (lightdao-mainnet-1). Browser PWA light-nodes contribute WebRTC bandwidth relay + Web-Worker block-header verification + uptime. Rewards = PoC (proof-of-contribution), verified by validator challenges + peer attestation + per-block Merkle root. Wallet is Passkey/WebAuthn (seedless) with Shamir 3-of-5 social recovery. Gas is USD-anchored; fees split 50% burn / 30% validators / 20% treasury (on-chain verified).

Why Cosmos: IBC-native, gov-upgradable (all our upgrades were on-chain votes + coordinated swaps, testnet-rehearsed), CosmWasm for the 10-contract suite.

Honest status: mainnet live but pre-traffic (you'd be early); LIGHT not on a DEX yet (oracle is validator-fed reference price until a pool exists); native mint inflation governance-zeroed so emission stays single-source.

Links: client https://lightdao.net · repo/status/whitepaper https://github.com/youqi023789/lightdao
AMA in comments — happy to walk through the contribution-verification math or the fee-split txs.
```

**r/DePIN:**
标题: `No-hardware DePIN: your browser IS the node (live mainnet, TURN fleet + on-device relay metering)`
正文: 同上但强调 DePIN 角度(带宽中继计量、8 区域 TURN/TURNS、贡献=收益、对比 Helium/Filecoin 需硬件)。

---


### 3.1 合规版(反 shilling 规则,2026-09-27 直发被拦后改写)

**为什么被拦**:r/cosmosnetwork Rule 1 = No Spamming/Shilling/Scamming;推广语气+正文带链接=典型 shilling 特征。改法:**技术深潜+自我披露+正文零链接+邀请批评**,先发 3-5 条有价值评论养号再发。

**r/cosmosnetwork 标题**: How we verify browser-contributed bandwidth on a Cosmos L1 without trusting client reports (PoC design critique welcome)
**正文**:

**r/DePIN 标题**: DePIN without hardware: what breaks when the node is a browser tab? (design critique welcome)
**正文**: 同上,但把开头换成 DePIN 视角(对比 Helium/Filecoin 需 00-000 硬件;我们零硬件的代价是验证更难),其余相同。
**发帖前置**:账号 karma≥50、账龄≥7 天、先评论 3-5 条; flair 选 Build/Dev 类;避开 mod 活跃时段外连发。

## 4. 免费目录/生态收录(逐个提交,文案通用)

提交目标(全免费):DePIN 目录(depin.com / depinscanner 等)、Cosmos 生态页(ecosystem.cosmos.network 提交)、CoinGecko/CoinMarketCap(先列链/项目页,代币待交易所)、ProductHunt(.launch)、HackerNews(Show HN)、GitHub Topics(depin, cosmos, webrtc, webauthn)。

**通用 blurb(复制)**:
```
LightDAO — browser-based DePIN light-node network on a live Cosmos L1. Zero-hardware mining via Proof-of-Contribution (WebRTC bandwidth relay + block-header verification + uptime), seedless Passkey wallet with Shamir social recovery, USD-anchored gas with 50% fee burn. Mainnet live with 7 validators; all upgrades governance-executed. https://lightdao.net
Tags: DePIN, Cosmos, WebRTC, WebAuthn/Passkey, PWA, Proof-of-Contribution
```

**Show HN 标题**: `Show HN: LightDAO – mine a Cosmos L1 with just a browser tab (Passkey wallet, WebRTC relay, live mainnet)`

---

## 5. 零成本增长活动(代币激励,不花现金)

**S1 贡献赛季(4 周)**:测试网贡献分排行 → 主网 LIGHT 空投池(从生态基金 16% 拨一小档,治理提案通过)。规则:贡献分=带宽40/在线30/验证20/稳定10(已在链上计分),赛季末按分空投。→ 把"挖矿"变成"竞赛",自带传播。
**邀请裂变**:邀请链接绑定;被邀人首周贡献的 10% 额外奖邀请人(白皮书已有邀请裂变引擎,直接启用)。
**监护人招募**:Passkey 社交恢复需要 3-5 监护人 → "成为别人的监护人赚声誉/NFT 徽章" → 天然拉新(每个钱包拉 3-5 人当监护人)。
**Builder 赏金**:GitHub issues 标 `bounty`(文档翻译/探索器/仪表盘),以 LIGHT 结算(token-for-service,零现金)。

**节奏**:X 每日 1 帖(更新/数据/教育)、每周 1 线程;TG/Discord 每日播报网络数据(burn/height/miners);Reddit 每周 1 深度帖;目录提交第 1 周完成。

**KPI(首月)**:TG/Discord ≥500 人 · X ≥1k 关注 · 测试网矿工 ≥300 · 目录收录 ≥6 · S1 赛季参与 ≥200。

---

## 6. 执行顺序(第 1 周)

1. 建 GitHub 公开仓库(代码+白皮书 V2.4+主网状态)→ 所有文案的 https://github.com/youqi023789/lightdao 占位替换
2. 注册 X + TG + Discord(用定位一句话做 bio)
3. 发 X 首发线程 + 置顶;TG/Discord 建群公告
4. Reddit 两帖;ProductHunt/Show HN 排队
5. 目录提交(6+);Cosmos 生态页提交
6. 上线 S1 赛季提案(治理)+ 邀请裂变开关
7. 每周更新模板跑起来(数据从链上/网关自动取)
