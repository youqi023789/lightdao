/* LD-I18N-B5-20261104  同批标签的中→英（人工） */
(function () {
  "use strict";
  window.LDI18N = window.LDI18N || {};
  function E(zh, m) { var k = window.LDI18N[zh] || (window.LDI18N[zh] = {});
    for (var p in m) { if (Object.prototype.hasOwnProperty.call(m, p)) { k[p] = m[p]; } } }
  function en(zh, v) { E(zh, { en: v }); }
  en("解除", "Undelegate");
  en("验证", "Verified");
  en("定稿", "Settled");
  en("带宽kbps", "Bandwidth kbps");
  en("在线s", "Uptime s");
  en("稳定%", "Stability %");
  en("应得LIGHT", "LIGHT earned");
  en("保存委托", "Save delegation");
  en("查询中…", "Querying…");
  en("加载可领历史", "Load claimable history");
  en("等待全网数据…", "Waiting for network data…");
  en("社交恢复(分片)", "Social recovery (shards)");
  en("未委托(自己在线)", "Not delegated (online yourself)");
  en("请勿重复点击,以免误操作", "Please don't click again to avoid mistakes");
  en("一键领取验证者/质押收益", "Claim validator / staking rewards in one tap");
  en("钱包安全 / Wallet security", "Wallet security");
  en("治理 · Governance(投票/提案/金库)", "Governance (voting / proposals / treasury)");
  en("空投中心 / Airdrops(白皮书 §5.7)", "Airdrops (whitepaper §5.7)");
  en("反女巫提示 / Anti-sybil notice", "Anti-Sybil notice");
  en("子代币兑换 / Sub-token exchange", "Sub-token exchange");
  en("委托在线 / Delegate uptime (70/30)", "Delegate uptime (70/30)");
  en("我的贡献历史 / My contribution history", "My contribution history");
  en("我的头衔与成就 / Titles & Achievements", "Titles & achievements");
  en("移除本机登录信息 / Remove this device's login", "Remove this device's login");
  en("我的安全与邀请 / My security & referrals", "My security & referrals");
  en("正在恢复登录状态,请稍候… / Restoring session…", "Restoring session…");
  en("机器翻译 · 未人工校对（点此看中文）", "Machine translation · not human-reviewed (click for Chinese)");
  en("资金池", "Treasury pool");
})();
