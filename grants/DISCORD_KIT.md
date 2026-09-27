# LightDAO Discord 建服包(复制即用)

> 服务器:https://discord.gg/9YY9X2Cdv 。以下全部为"设置→复制粘贴"操作,无需机器人。
> 若你之后愿意给我创建一个 Bot token(Discord 开发者门户 → New Application → Bot),我可在服务器自动播报网络数据(高度/销毁/矿工/赛季),现在先手动模板。

## 1. 频道结构(Settings → Channels → Create)
分类 **INFO**
- #announcements(只读:仅 Mod 可发)
- #rules(只读)
- #roadmap(只读,贴白皮书路线图截图)
分类 **MINING**
- #mining-help(求助/答疑)
- #show-your-rig(晒贡献/截图)
- #season-1(赛季讨论)
分类 **GOVERNANCE**
- #gov-proposals(提案讨论)
- #treasury-transparency(贴 explorer 多签/金库截图)
分类 **BUILDERS**
- #bounties(贴 GitHub bounty issue 链接)
- #dev-chat
分类 **LOCAL**
- #中文
- #espanol / #bahasa / #tieng-viet(按增长市场加)
分类 **VOICE**(可选):Mining Together(挂机语音房)

## 2. 角色(Roles → Create)
- Founder(你)
- Mod(可信者)
- Ambassador(≥10 邀请,白皮书 §368)
- Partner(≥50 邀请)
- Builder(提交过 PR/bounty)
- Miner(默认加入者)
权限:announcements/rules/roadmap 仅 Mod+ 可发;其余全员可发。

## 3. #rules 置顶文案(复制)
```
1) No shilling other tokens, no price promises, no "guaranteed profit". LightDAO tokens are contribution credits & SPV profit-distribution claims, not securities; nothing here is investment advice.
2) NEVER share your seed phrase, Shamir shares, PIN, or Passkey. No staff will ever ask. Anyone asking = scam, report immediately.
3) Only official domain: lightdao.net. Any other domain/airdrop/"support" DM is fake.
4) Be kind. Critique ideas, not people. Technical disagreement is welcome.
5) No NSFW, no hate, no doxxing.
6) English + 中文 + ES welcome; use #中文 etc.
```

## 4. #announcements 首条(复制)
```
LightDAO mainnet is live. Your browser is the node.
- Mine (no hardware, no seed phrase): https://lightdao.net
- Explorer (burn/treasury/validators/vesting): https://lightdao.net/explorer.html
- Governance (stake, propose, vote): https://lightdao.net/governance.html
- Whitepaper V2.4: https://lightdao.net/whitepaper.html
- Repo + mainnet status: https://github.com/youqi023789/lightdao
Season 1 runs 2026-10-01 → 10-29: contribute, climb the leaderboard, share the 5M LIGHT pool. Invite friends: +10% of their first-week contribution.
Weekly network recap posts here every Monday.
```

## 5. 每周一数据播报模板(手动填,或给我 Bot token 后自动)
```
LightDAO Weekly — W<n>
Height: <h> · Validators: 7/7 bonded · Miners today: <m>
Burned (cumulative): <b> LIGHT · Treasury: <t> LIGHT
Season day: <d>/29
Shipped this week: <1-3 bullets with links>
Next: <1-2 bullets>
Proof: <explorer/tx links>
```

## 6. 欢迎消息(System → New member welcome,复制)
```
Welcome to LightDAO, <user>! Start here:
1) #rules (2 min)
2) Mine in 60s: https://lightdao.net (Passkey login, no seed)
3) Stuck? #mining-help — someone answers fast.
4) Want rewards beyond mining? #bounties and the Ambassador path (10 invites).
Your browser is the node. ⚡
```
