# light_token 构建说明(2026-10-04 Lumda rebrand)

- 部署版本(主网 code_id 1)对应本文件 lib.rs 的 v1.0.0 状态(commit 前置基线)。
- v1.1.0 变更:
  1. CONTRACT_VERSION 1.0.0 → 1.1.0
  2. 新增 `Item<TokenMeta>` at key `"lt_meta"`(持久化 symbol/name)
  3. 新增 `MigrateMsg { new_symbol, new_name }` + `migrate()` entry_point
  4. `query(TokenInfo)` 从 META 读 symbol/name;首次 migrate 前默认 LUMDA/Lumda
- cw20/state.rs/error.rs/contract.rs/msg.rs 是**仓库漂移历史**(v0.2.0 CW20-style 从未部署),
  保留在 `_cw20_drift_backup_*.tgz` 里供审计,后续清理窗口移除。
- 构建命令:`cargo build --release --target wasm32-unknown-unknown --locked -p light_token` 后
  `wasm-opt --mvp-features -O3 --strip-debug`。
- **产物 sha256 = 69e484c72ad6979ad9a3d54a58c45333883acb57c3b3f46d3907223191cb3bd1**(v1.1.0)—— 提案 E(store code)的校验锚,提案 F(migrate)引用同 code 的 code_id。
