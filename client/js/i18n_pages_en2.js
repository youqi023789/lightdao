/* LightDAO 内页英文词条 · 第 2 批（补 ld_i18n_coverage.py 报出的最后 21 条长句） */
(function () {
  "use strict";
  window.LDI18N = window.LDI18N || {};
  function E(zh, m) {
    var k = window.LDI18N[zh] || (window.LDI18N[zh] = {});
    for (var p in m) { if (Object.prototype.hasOwnProperty.call(m, p)) { k[p] = m[p]; } }
  }
  function en(zh, v) { E(zh, { en: v }); }

  en("质押 LIGHT → 投票/发起提案 → 执行。链上治理:质押→提案→投票→执行(governance 合约,自迁移治理)。", "Stake LIGHT → vote / submit proposals → execution. On-chain governance: stake → proposal → vote → execute (governance contract, self-migrating).");
  en("投票需先质押 LIGHT(治理权重=质押额)。质押通道维护中,迁移完成后即可质押并投票。", "Voting requires staking LIGHT first (governance weight = staked amount). The staking channel is under maintenance; staking and voting resume after the migration.");
  en("质押通道维护中:链上治理合约(旧CW20质押)与代币合约版本不兼容,需一次合约迁移(改为原生质押,已排期治理提案)。迁移完成前质押不可用,不影响挖矿/领取/委托。", "Staking channel under maintenance: the legacy CW20-based governance contract is incompatible with the current token contract and needs one migration (to native staking; a governance proposal is scheduled). Until then staking is unavailable — mining, claiming and delegation are unaffected.");
  en("质押(原生 LIGHT 随消息附带)…", "Stake (native LIGHT attached to the message)…");
  en("✓ 已质押", "✓ Staked");
  en("质押失败:", "Stake failed:");
  en("赎回质押 / Unstake", "Unstake");
  en("✓ 已赎回", "✓ Unstaked");
  en("赎回失败:", "Unstake failed:");
  en("发起提案 / Create proposal", "Create proposal");
  en("提交提案…", "Submitting proposal…");
  en("✓ 提案已提交", "✓ Proposal submitted");
  en("提交失败(需质押≥门槛):", "Submission failed (stake must meet the threshold):");
  en("金库余额:", "Treasury balance:");
  en("· 签名人:", "· signers:");
  en("无 Passkey 钱包,先用主客户端创建", "No Passkey wallet — create one in the main app first");
  en("已连接(沿用主客户端登录):", "Connected (reusing the main app session):");
  en(",Passkey 认领钱包,点开始挖矿即成为节点。你的贡献由三层 Proof-of-Contribution 验证(验证者挑战 + 对等 attest + 逐块 Merkle 根),无需任何审批。", ", claim a Passkey wallet, and press Start mining to become a node. Your contribution is verified by three layers of Proof-of-Contribution (validator challenges + peer attestations + per-block Merkle roots) with no approval required.");
  en("子代币 = SPV 收益分配请求权凭证(白皮书 §5.9):由", "A sub-token is a claim on SPV profit distributions (whitepaper §5.9), issued by");
  en("尚无子代币=尚无投资发行。第一笔子代币将在首笔治理投资提案通过后铸造。", "No sub-tokens yet means no investments yet. The first sub-token will be minted once the first governance investment proposal passes.");
  en("输入你的 wasm1… 地址(或带 ?addr= 打开)", "Enter your wasm1… address (or open with ?addr=)");
})();
