# LightDAO — 浏览器即矿机，贡献即挖矿

**一条真实运行的 Cosmos 应用链。不用买矿机、不用装软件、不用质押：打开浏览器就在挖矿，每一笔奖励都能自己在链上验算。**

主网 `lightdao-mainnet-1` 自 2025 年起持续出块，原生代币 **LIGHT**（总供应 2,500,000,000，固定通胀上限）。

> 🌐 官网：https://lightdao.net
> ⛏ 创世矿工：https://lightdao.net/miners.html
> ✅ 奖励自证：https://lightdao.net/verify.html

---

## 三分钟看懂

### 1. 它是干什么的

LightDAO 是一个 **DePIN（去中心化物理基础设施网络）**。用户用浏览器运行轻节点，贡献四类真实资源，按 **PoC 贡献证明** 获得 LIGHT：

| 维度 | 权重 | 说明 |
|---|---|---|
| 带宽中继 | 40% | WebRTC P2P 中继，帮其他节点传数据 |
| 会话在线 | 30% | 保持连接的时长 |
| 区块验证 | 20% | 校验区块头 |
| 稳定性 | 10% | 不掉线的连续运行 |

每天，挖矿池按 `个人加权分 ÷ 全网总分` 结算一次。加权分公式、叶节点哈希、Merkle 树全部公开，任何人可用 [/verify.html](https://lightdao.net/verify.html) 输入「地址 + 日期」自行复算。

### 2. 怎么开始（30 秒）

1. 打开 <https://lightdao.net>
2. 创建 Passkey 钱包（生物识别，无助记词）或连接已有钱包
3. 点「开始挖矿」— 浏览器标签页开着就在贡献，关掉即停止

不需要：矿机、显卡、质押、KYC、下载安装包。

### 3. 怎么证明你没被骗

这是本项目最重要的一条：**不要相信任何页面上的数字，自己验。**

```
奖励 = 每日挖矿池 × (你的加权分 ÷ 当日全网总分)
your_leaf = sha256(地址 || 日序号 || 带宽分 || 会话分 || 验证分 || 稳定分)
```

- 打开 <https://lightdao.net/verify.html>，输入地址 + 日期
- 页面会返回：四个维度的原始分 → 加权分 → 当日总分 → 每日池 → 应得 LIGHT → **完整 Merkle 证明路径**
- 把证明路径逐级哈希，应该能得到当日的 Merkle 根；这个根就是结算时写进链上的那个

链上直接查（无需信任本站）：

```bash
curl -s https://lightdao.net/gw/v1/proof?day=65&miner=<你的地址>
```

---

## 为什么不是又一个「云挖矿」

| 常见项目 | LightDAO |
|---|---|
| 买矿机 / 买算力 | 浏览器标签页就是节点 |
| 团队发币、不公开账本 | 每个 epoch 的奖励根上链，可复算 |
| 提现靠平台审核 | 链上合约结算，无需许可 |
| 「保证收益」 | 没有保本承诺，奖励随全网总分浮动 |

---

## 网络与合约

| 项 | 值 |
|---|---|
| 链 ID | `lightdao-mainnet-1` |
| 共识 | CometBFT（Cosmos SDK v0.50 / wasmd v0.55） |
| 原生代币 | `ulight`（1 LIGHT = 10⁶ ulight） |
| 总供应 | 2,500,000,000 LIGHT（固定上限） |
| 公开 RPC | `https://lightdao.net/rpc/` |
| 区块浏览器 | <https://lightdao.net/explorer.html> |

---

## 治理与金库

协议参数不靠团队口头承诺，靠链上多签与治理：

- **金库**：3/5 多签 + 72 小时时间锁。任何转账需 3 个签名人批准，并在 72 小时后才可执行。
- **资金流向**：每笔可查 <https://lightdao.net/funds.html>
- **治理**：提案 → 投票 → 执行全部在链上，投票权重按质押与贡献计算

白皮书（V2.4）是项目宪法：<https://lightdao.net/whitepaper.html>

---

## 仓库结构

```
client/       前端（PWA，21 个页面）
docs/         设计与运维文档
infra/        部署与监控脚本
contracts/    CosmWasm 合约（Rust）
```

---

## 参与

| 渠道 | 链接 |
|---|---|
| 官网 | <https://lightdao.net> |
| X / Twitter | <https://x.com/lightdaoproto> |
| Discord | <https://discord.gg/aBWEatEkUX> |
| Telegram 链上日报 | <https://t.me/lightdao_news> |

有问题直接在 Discord 的 `#founding-miners` 提问；发现 bug 请开 issue。

---

## 免责声明

LIGHT 是网络的功能性代币，不是投资合约，不承诺任何收益。挖矿奖励取决于你贡献的真实资源量与全网总分，可能为零。参与前请自行评估风险。

---

## English summary

LightDAO is a live Cosmos L1 (`lightdao-mainnet-1`) for browser-based DePIN mining. Open <https://lightdao.net>, and your browser becomes a light node contributing bandwidth relay, session uptime, block-header verification and stability. Rewards settle daily from an on-chain mining pool: `reward = daily_pool × your_weighted_score ÷ total_score`. Every reward is independently verifiable — the full Merkle proof is returned by <https://lightdao.net/verify.html>, and the daily root is anchored on-chain. No hardware, no staking, no KYC. Treasury is a 3-of-5 multisig with a 72-hour timelock.
