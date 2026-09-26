# LightDAO §4.9 Passkey 钱包 v1(staging)

## 是什么
无种子体验(WebAuthn Passkey 生物识别登录)+ Shamir 3-of-5 社交恢复。链上签名仍用 secp256k1。

## 架构决策
WebAuthn Passkey 用 P-256,而 cosmos 原生只验 secp256k1。完整方案需 P-256 链上智能合约账户(大工程,列为后续增量)。v1 务实方案:
- Passkey 的 PRF 扩展派生确定性密钥 → HKDF → AES-GCM 加密 BIP39 助记词 → localStorage 仅存密文(明文种子不落地、不显示)
- 浏览器不支持 PRF 时回退用户 PIN(PBKDF2-SHA256 210k 轮)
- Shamir 3-of-5 社交恢复:助记词切 5 份给监护人,任 3 份重建;本地不存分片
- 解锁后的助记词喂给现有 cosmjs DirectSecp256k1HdWallet 签名

## 文件
- `passkey-wallet.js` — 零依赖模块(GF(256) Shamir + WebAuthn PRF + AES-GCM + HKDF + PBKDF2,纯 Web Crypto)
- `wallet-v2.html` — staging 测试页(环境检测 + 密码学自检 + 创建/解锁/社交恢复/分片恢复/链上余额)

## 部署状态
- 线上:https://lightdao.net/wallet-v2.html(staging,主客户端 index.html 未动)
- 需用户在浏览器实测 WebAuthn(CLI 无法测生物识别)
- 确认无误后再并入主客户端

## 关键 bug 记录(已修)
GF(256) 表生成最初用生成元 0x02(倍增),但 0x02 对 AES 多项式 0x11b 的阶只有 51(非本原元),导致 EXP 表仅 51 个不同值、Shamir 全错(连 (1,1) 往返都失败)。改用生成元 0x03(阶 255)后,经 Python 交叉验证:255 distinct + EXP/LOG 互逆 + 逆元 + 所有 (t,n) 往返 + t-1 安全性 + 含 0x00 随机字节,全部 PASS。
**教训:任何 GF(256)/Shamir 实现,生成元必须验证为本原元;密码学上线前必用独立语言交叉验证。**

## 测试步骤(用户)
1. 浏览器开 https://lightdao.net/wallet-v2.html(Chrome/Edge/Safari,HTTPS)
2. 点「运行密码学自检」→ 应全 PASS
3. 点「创建 Passkey 钱包」→ 完成生物识别 → 看密钥来源(PRF 或 PIN 回退)
4. 点「生成分片」→ 抄下 5 份
5. 刷新页面 → 「Passkey 解锁」→ 生物识别 → 应解出地址
6. 「从分片恢复」粘贴任 3 份 → 应重建出同一助记词
