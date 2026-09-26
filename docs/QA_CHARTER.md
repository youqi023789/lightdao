# LightDAO QA / 验收 / 提示词章程(QA_CHARTER)

> 目的:把"问题不该由用户发现"制度化。任何功能/文案/部署,先过本章程的门禁再上线。
> 状态:本章程自身也是活文档,每次事故复盘后更新。

## 0. 事故复盘驱动的教训(为什么有这份章程)
- 文案脱离白皮书(自创 slogan)→ 文案必须逐条锚定源文档,附出处。
- 静态审计(链接/锚点)漏掉功能级 bug(奖励公式错 1000×、ensureLD 作用域、CSP 拦 wasm/CSSOM)→ 必须有**真实浏览器 E2E**。
- 缓存/SW 导致修复不达用户 → 部署必须带缓存破坏(?v=)与 SW 版本 bump,并验证"老 SW 用户也能拿到新代码"。
- 移动端与桌面差异(微信 X5 无 WebAuthn、iOS 隐私模式存储抛错)→ 矩阵必须含**能力降级剖面**,不只是 UA 伪装。
- 内联脚本/样式与 CSP 冲突 → 安全收紧必须配 E2E 回归,否则"安全"变成"不可用"。

## 1. 审计维度(每次 release 全跑)
1. **功能 E2E(无头 Chrome 矩阵)**:modern-android / wechat / qq / ios-safari / ios-private(存储抛错)/ old-webview-UA;每剖面跑:加载→控制台 0 错误→创建/导入钱包→主界面→刷新自动登录→清 sessionStorage 仍自动登录(持久化)→创始人 ref 默认归因→首页 CTA 带 ref→语言数→主题切换→实时数据。
2. **链上/数据一致性**:奖励数学(池×占比,对照合约 daily_miner_pool 与网关 total_score)、手续费 50/30/20、释放 95/5、vesting 三段、Merkle 根与合约 verify(selftest)、referral 记录、finalize/sign 流水线日志。
3. **安全**:CSP 生效且不禁用必要能力(wasm/CSSOM)、无内联 script、XSS 转义、密钥非托管、TURN 临时凭证、finalize 管理密钥、限流 429、SRI 清单校验、security.txt/SECURITY.md、HSTS/nosniff/referrer。
4. **兼容**:ES 兼容静态扫描(禁 ?. ?? 无参catch .at replaceAll 等进非 vendor 代码)、能力降级(WebAuthn 缺失→默认助记词+置灰+内联说明;存储抛错→安全包装;旧引擎→能力横幅)、UA 矩阵。
5. **i18n**:每个 data-i 键在 zh/en 齐全;语言数达标;切换后无残键;per-locale OG/hreflang。
6. **a11y**:对比度 ≥4.5(逐 token 计算)、焦点环、skip-link、aria-label、减弱动效、语义地标。
7. **性能**:首屏无阻塞外链、动态 import 仅按需、SW 缓存策略正确(壳网络优先/静态缓存优先/immutable 带破缓存)、vendor 体积监控。
8. **链接/结构**:全站爬虫 0 死链 0 缺锚 0 占位;sitemap/robots 同步新页。
9. **运维/生产**:监控(status.json 五查:链推进/网关/定稿/签根/矿工数/HTTP)、告警日志、每日备份保留 7 份、升级看门狗、回滚预案、日志轮转。
10. **法务/文案**:免责声明在页脚与条款页;文案逐条对白皮书;不承诺收益。

## 2. 验证门禁(deploy 前必跑,全绿才推)
`infra/qa_site.py`(语法+接线+资源)→ `infra/qa_extra.py`(ES 兼容+孤儿交互)→ `site_audit.py`(链接/锚点/占位)→ `infra/mobile_e2e.py`(六剖面 E2E)→ `sri_verify.py` → `ld_monitor.py` 一次手动跑。任一红 = 不部署。

## 3. 提示词/需求章程(给未来自己与协作者)
每个需求写成:**目标(可验收结果)+ 源文档出处 + 边界(不做什么)+ 验收命令 + 回滚方案**。
- 不接受无验收标准的需求;文案类需求必须指明源文档章节。
- 安全/体验冲突时:可用性优先,但必须记录权衡(如 style-src unsafe-inline)。
- 任何"用户可见字符串"改动 → 跑 i18n 键检查 + 矩阵。
- 任何部署 → 缓存破坏 + SW bump + 老 SW 用户可达性验证。

## 4. 生产监控与响应
- `ld_monitor.py` 每 5 分钟:链高推进(>6min 不涨=停摆)、网关健康、昨日定稿、昨日签根、今日矿工数、HTTP 200;失败写 `ld_alerts.log` 并反映到 `/status.json`(首页徽标)。
- 每日 06:00 UTC 备份网关数据(granted/day 文件)保留 7 份。
- 升级:测试网彩排 → 治理提案 → 7 节点看门狗同块切换 → 验收任务自动跑 → 失败回滚二进制+快照。
