/* LD-I18N-B6-20261104  同批的中→英 */
(function () {
  "use strict";
  window.LDI18N = window.LDI18N || {};
  function E(zh, m) { var k = window.LDI18N[zh] || (window.LDI18N[zh] = {});
    for (var p in m) { if (Object.prototype.hasOwnProperty.call(m, p)) { k[p] = m[p]; } } }
  function en(zh, v) { E(zh, { en: v }); }
  en("在此设备保存加密的登录信息(下次打开需解锁密码或生物识别验证;同一标签页内刷新不再询问)", "Save encrypted login on this device (next time you need a password or biometric to unlock; refreshes inside the same tab won't ask again)");
  en("导出助记词备份", "Export mnemonic backup");
  en("📲 PWA 已安装 · 可离线/心跳更稳", "📲 PWA installed · works offline / steadier heartbeat");
  en("赛季空投:S1 池 5M LIGHT 按赛季贡献分结算(见 Season 页)。", "Season airdrop: the S1 pool of 5M LIGHT is settled by season contribution score (see the Season page).");
  en("子代币空投:每次投资发行的 30% 空投给社区(待首笔发行)。", "Sub-token airdrop: 30% of every investment issuance is airdropped to the community (awaiting the first issuance).");
  en("TGE 种子空投:4,800 万枚于 TGE 发放(白皮书 §5.3/5.7)。", "TGE seed airdrop: 48M LIGHT distributed at TGE (whitepaper §5.3/5.7).");
  en("空投当前记账于网关账本,TGE 时链上发放;不构成收益承诺。 Airdrops are ledger-recorded now and distributed on-chain at TGE; no yield is promised.", "Airdrops are currently recorded in the gateway ledger and distributed on-chain at TGE; this is not a promise of yield.");
  en("依据白皮书 §985:3人=布道者(10%+100L)·10人=大使(15%+500L+徽章+投票权重+5%)·50人=合伙人(20%+2500L+徽章+10%);链上徽章与投票权重加成于治理第 7 个月激活。", "Per whitepaper §985: 3 referrals = Preacher (10% + 100L) · 10 = Ambassador (15% + 500L + badge + 5% voting weight) · 50 = Partner (20% + 2500L + badge + 10%); on-chain badges and the voting-weight bonus activate in governance month 7.");
  en("移动端可把\"在线\"委托给中继节点:你拿 70% 在线分,中继拿 30%(白皮书移动端适配)。留空=不委托。", "On mobile you can delegate your uptime to a relay node: you keep 70% of the uptime score, the relay gets 30% (whitepaper mobile adaptation). Leave empty to not delegate.");
  en("合约 Exchange 已就绪(LIGHT 兑换子代币并销毁);当前尚无子代币发行,首笔治理投资提案通过后此处开放兑换。", "The Exchange contract is ready (swap LIGHT for sub-tokens, with burning); no sub-token has been issued yet, so swapping opens here after the first governance investment proposal passes.");
  en("连接钱包后自动读取你在两个锁仓合约里的排期。", "After you connect a wallet, your schedules in both vesting contracts load automatically.");
  en("转账 / Send", "Send");
  en("委托验证者 / Delegate", "Delegate");
  en("锁仓解锁 / Vesting", "Vesting");
  en("领取已归属 / Claim vested", "Claim vested");
  en("每日结算刷新:你当地 {t} · 倒计时 {cd}", "Daily settlement refresh: your local {t} · countdown {cd}");
})();
