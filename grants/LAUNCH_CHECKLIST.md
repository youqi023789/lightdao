# LightDAO — 剩余手动操作清单(每项 30 秒,文案已备好,直接复制)

> 说明:下面这些都需要**你本人的登录态**(X/TG/Discord/Reddit/HN/PH/目录/ICF 表单),我没有浏览器接管工具,也无法用 API 改 X 资料(该档位无 bio/banner/pin 接口),所以只能你点。所有文案已写好,复制粘贴即可。
> 已自动完成的部分:X 首发 8 帖线程、推广帖、治理里程碑 3 帖线程(含你的邀请链接)、每周自动更新 cron、GitHub 公开仓库、横幅图(见附件)。
> 你的创始人邀请链接(所有渠道都用它):
> `https://lightdao.net/?ref=wasm1vhpf9c3h8eu8hd7ca520dvspzdsxz4nkka3h7s`

---

## A. X/Twitter 资料(3 步)

**A1. 上传横幅**
1. 打开 https://x.com/lightdaoproto → 点「Edit profile / 编辑资料」
2. 横幅区点相机图标 → 上传附件 `lightdao_x_banner.png`
3. X 会按 3:1 裁剪 → 拖动让 "LightDAO" 居中 → Apply → Save
   (图是 2560×1080,裁成 1500×500 即可,已留左右安全边距)

**A2. 简介 Bio(≤160 字符,直接粘贴)**
```
Browser-only DePIN mining on a live Cosmos L1. No hardware, seedless Passkey wallet, 50% of gas burned. Mine LIGHT from any browser → lightdao.net
```
- Location 填:`lightdao.net`
- Website 填:`https://lightdao.net`

**A3. 置顶帖**
1. 打开首发线程第 1 帖:https://x.com/lightdaoproto/status/2103791251367825588
2. 点右下「⋯」→「Pin to your profile / 置顶到主页」→ 确认
   (置顶帖接口在本档位返回 404,只能手动点这一下)

---

## B. Telegram(建群 + 首条公告)

1. TG → 新建群组,名称:`LightDAO — Browser Mining`,用户名设为 `@LightDAO_mining`(若可用)
2. 群简介填定位一句话(见 GROWTH_KIT §0)
3. 置顶下面这条公告(复制 GROWTH_KIT.md §2 的「建群首条公告」整段),结尾加邀请链接:
```
Start now: https://lightdao.net/?ref=wasm1vhpf9c3h8eu8hd7ca520dvspzdsxz4nkka3h7s
```
4. 把 TG 群链接回填到 X bio/website 和 lightdao.net 页脚(告诉我链接,我加到客户端)

---

## C. Discord(建服 + 公告)

1. Discord → 新建服务器:`LightDAO`,分类频道 `#announcements` `#general` `#mining-help`
2. `#announcements` 首条 = GROWTH_KIT.md §2 公告整段 + 你的邀请链接
3. 服务器邀请设为「永不过期」,把链接发我 → 我加到客户端页脚和 X bio

---

## D. Reddit(2 帖,标题+正文都在 GROWTH_KIT §3,直接复制)

1. r/Cosmos(或 r/cosmosnetwork)→ 发「We built a Cosmos L1 where mining = leaving a browser tab open…」正文见 §3
2. r/DePIN → 发「No-hardware DePIN: your browser IS the node…」正文见 §3
- 两帖正文里的 `https://lightdao.net` 换成你的邀请链接(带 ref)
- 注意:新号先发 1-2 条正常评论养号,避免被 automod 删

---

## E. Show HN + Product Hunt

**Show HN**(https://news.ycombinator.com/submit):
- 标题:`Show HN: LightDAO – mine a Cosmos L1 with just a browser tab (Passkey wallet, WebRTC relay, live mainnet)`
- URL:`https://lightdao.net`
- 正文第一条评论放 GROWTH_KIT §3 的 Cosmos 帖正文(技术细节 + honest status)

**Product Hunt**(https://www.producthunt.com/ → Launch):
- Name:`LightDAO` · Tagline:`Mine crypto with just your browser — no hardware`
- Description:GROWTH_KIT §4 的通用 blurb
- 备好 3-5 张截图(客户端挖矿页/治理页/浏览器页)——需要我生成截图包就说一声

---

## F. 免费目录收录(逐个提交,通用 blurb 见 GROWTH_KIT §4)

- DePIN 目录:depin.com、depinpedia、depinbay
- Cosmos 生态:https://cosmos.network/ecosystem(提交项目)
- CoinGecko / CoinMarketCap:先建「项目/链」页(代币待上交易所再单独提交)
- GitHub Topics:给仓库加 `depin` `cosmos` `cosmwasm` `webrtc` `webauthn` `pwa`(这个我能用 gh 直接加,见下)

---

## G. ICF Grant 提交

1. 打开 https://grants.interchain.io → 用邮箱注册/登录 → 新建申请
2. 逐字段复制 `ICF_Grant_Application_LightDAO.md`(在旧工作区 outputs,或我重新生成一份放进 repo `grants/`)
3. 提交后把 **Submission ID / 确认邮件** 发我,我登记跟进 + 到期催进度

---

## 我能立刻替你做的(说一声即可)

- [x] X 发帖(API)——已完成
- [ ] 给 GitHub 仓库加 Topics(depin/cosmos/…)——`gh repo edit` 一条命令,我可代做
- [ ] 把 TG/Discord 链接加进 lightdao.net 客户端页脚 + X bio 文案更新——你给链接我就改
- [ ] 生成 Product Hunt / 目录用的截图包 + 多语言 blurb
- [ ] 把 ICF 完整申请书重新生成进 repo grants/
- [ ] 每周 X 数据播报(cron 已建,周一 09:00 CST,自动带邀请链接)
