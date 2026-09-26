# LightDAO 合约包（审计修复版）

本包为 LightDAO 10 个 CosmWasm 合约的**审计修复后**源码、可直接上链的 wasm 二进制、以及一键构建/部署/自检脚本。

## 目录结构
```
LightDAO_contracts_audited/
├── README.md               本文件
├── AUDIT_REPORT.md         安全审计报告（发现 + 修复 + 链上验证结果）
├── contracts/              10 个合约的 Rust 源码（已修复）
│   ├── light_token/        CW20 代币 + Mint(硬顶2.5B) + TransferFrom
│   ├── mining_reward/      挖矿释放（验证者提交每日根，按分比例铸造）
│   ├── governance/         治理（托管质押 + 提案 + 双维度表决 + 触发子代币）
│   ├── treasury_multisig/  金库 3/5 多签 + 72h 时间锁
│   ├── subtoken_factory/   子代币铸造 + LIGHT 兑换销毁
│   ├── oracle_twap/        30 天时间加权均价 + 外部中位数 + 异常检测
│   ├── anti_fraud/         挑战-应答反作弊 + 罚没联动
│   ├── validator_registry/ 验证者注册（CW20 质押）+ owner 门限罚没
│   ├── vesting/            归属（owner 建表 + 真实发放）
│   └── insurance_fund/     保险基金（授权归集 + 治理表决 + 真实赔付）
├── wasm/                   10 个 wasm-opt 归一化后的二进制（可直接 store）
└── scripts/
    ├── build_normalize.sh  rustc1.85 编译 + wasm-opt 归一化
    ├── deploy.sh           重置(可选) + store 10 + instantiate2 全互连 + 校验
    └── verify_flows.sh     三条主链路 + 7 项安全回归（真实链上交易）
```

## 环境要求（VPS / Linux）
- wasmd v0.60（wasmvm v2.2.1），单节点测试网 `lightdao-testnet-1` 已运行，RPC `tcp://localhost:26657`。
- rustup 工具链 `1.85.0` + `wasm32-unknown-unknown` target。
- `wasm-opt`（binaryen，VPS 上为 v105）。
- keyring-test 中有 `validator` 账户（部署者/owner）。

## 一键复现
```bash
# 1) 编译 + 归一化（产出 /home/ubuntu/wasm_v2/*.wasm）
bash scripts/build_normalize.sh

# 2) 部署（RESET=yes 会先重置链到创世；默认 no 则在现有链上追加）
RESET=yes bash scripts/deploy.sh
#   - 依次 store 10 个合约（code_id 1..10）
#   - 用 instantiate2 + build-address 预测地址，破解循环依赖，全互连实例化
#   - 地址写入 /tmp/lightdao_addrs.env

# 3) 自检（真实交易，跑三条链路 + 7 项安全回归）
bash scripts/verify_flows.sh
```

## 关键参数（测试网）
- `genesis_time = now - 10 天`（让 day 0..9 成为“已完结天”，可领取挖矿奖励）。主网应设为真实 TGE 时间。
- `voting_period_secs = 30`（测试网快速演示）。主网设 `null` → 走白皮书按提案类型的天数（紧急 1 天 / 其余 7 天）。
- 代币精度 6；硬顶 2.5B；epoch 730 天减半；epoch1 释放 5 亿；矿工份额 95%。
- 提案最低质押 `proposal_min_stake = 1000 LIGHT`（1e9 micro）。

## 安全须知
- 这是**自审**，不能替代专业第三方审计。上主网前请再做独立审计并补测试。
- 合约 admin = 部署者（validator），可 migrate 升级；主网应把 admin 交给治理/多签。
- 详见 `AUDIT_REPORT.md`。
