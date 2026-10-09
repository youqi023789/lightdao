# light_token 构建说明

## 已做(2026-10-04)
- **修 repo drift**:仓库此前携带的 CW20-style 版本(contract.rs/msg.rs/state.rs/
  error.rs 四文件、v0.2.0)**从未部署**到主网。真实部署版(code_id=1)是
  `src/lib.rs` 单文件、cw2 版本 **1.0.0**、原生 `ulight` denom 的元数据壳
  + 永久销毁池:任何发到本合约地址的 ulight 被锁死即视为 burned。
  旧漂移版备份在 `_cw20_drift_backup_*.tgz`(仅供审计)。
- 现 lib.rs = 真实部署源码基线 v1.0.0。

## 已回退(2026-10-04,用户决定"以后正式交易前再做")
- Lumda 品牌改名(v1.1.0:加 MigrateMsg + lt_meta Item + symbol=LUMDA/name=Lumda)
  **已挖通端到端但未上链**,理由:
  - 主网提案 8 (Lumda rebrand E: store light_token v1.1.0) 在投票期被 x/gov 自动
    REJECTED(0 票参与触发 quorum 判负机制),未执行、code_id 未创建。
  - 部署侧仍停在 v1.0.0 symbol=LIGHT。
  - 用户明确"等人多、正式交易前再改"。

## 复活路径(未来重启用)
- 已保存 artifacts(SG:/home/ubuntu/):
  - `lumda_light_token_v1.1.0.wasm` sha256=69e484c72ad6979ad9a3d54a58c45333883acb57c3b3f46d3907223191cb3bd1
  - `lumda_light_token_v1.1.0.wasm.b64.gz`(提案载荷源)
  - `lumda_proposals/E_store_light_token_v110.json` / `F_migrate_light_token_TEMPLATE.json` / `G_bank_denom_metadata.json`
  - `patch_light_token_lumda.py`(可重复打同一组补丁,断言式安全)
- Drill 冒烟测已通过(testnet 26857,instantiate 1.0.0 → query LIGHT → migrate 1.1.0 →
  query LUMDA → 幂等 empty re-migrate 保留 LUMDA),复用时不需重跑。
- 复活时:①跑 patch 脚本 ②build ③sha256 一致即可,直接跳过诊断阶段。

## 已知约束(避免重踩坑)
- x/gov metadata JSON ≤ 255 字符,且 title/summary 必须与顶层匹配(SDK 0.50.12)。
- wasmd fork CLI 未注册 `/cosmos.bank.v1beta1.MsgSetDenomMetadata`,wallet 显示层
  改名要走链升级或 raw protobuf 手搓 tx。
- Vote tx 需要 `--gas 200000` 左右(`--gas auto --gas-adjustment 1.5` 会低估到
  57727 而实际 58037 就 out-of-gas)。
