# Contributing to LightDAO

LightDAO is a browser-native DePIN Cosmos L1 (wasmd + CosmWasm). Contributions welcome: code, docs, translations, security, tooling.

## Ways to contribute
- **Code / contracts**: see `contracts/` (10 CosmWasm modules) and `chain/` (x/lightfee fork of wasmd). Build with Rust (wasm32-unknown-unknown, `-C target-feature=-reference-types`) and Go 1.23+.
- **Bounties**: issues labeled `bounty` are paid in LIGHT (token-for-service). Comment to claim; submit PR referencing the issue.
- **Docs & translations**: `whitepaper/`, `docs/`, and client i18n (14 languages). PRs fixing clarity or adding locales are fast-merged.
- **Security**: do NOT open public issues for vulnerabilities. Email security@lightdao.net or use GitHub private advisory. 90-day coordinated disclosure; bounty up to $50k tiered.

## PR flow
1. Fork + branch `feat/…` / `fix/…`.
2. Keep client JS ES2017-safe (no `?.`, `??`, optional catch) — enforced by `infra/qa_extra.py`.
3. Run gates before pushing: `infra/qa_site.py`, `infra/qa_extra.py`, `site_audit.py`, `infra/mobile_e2e.py` (headless Chrome, 6 UA profiles).
4. One concern per PR; describe the user-visible effect.
5. A maintainer runs the same gates in CI-less fashion (server-side) before merge.

## Ground rules
- Be kind; assume good faith. No shilling, no price talk in technical threads.
- Client changes must preserve: no inline scripts (CSP), no modern syntax in non-vendor JS, visible feedback on every failure path.
- Chain/contract changes require a governance proposal (see whitepaper §4.12 upgrade levels) — PRs prepare the artifact, governance enacts it.

## Dev setup (quick)
```
git clone https://github.com/youqi023789/lightdao
cd lightdao/contracts && cargo test          # contract unit tests
python3 infra/qa_site.py && python3 infra/qa_extra.py   # static gates
```
Questions: GitHub Discussions, or Discord https://discord.gg/9YY9X2Cdv
