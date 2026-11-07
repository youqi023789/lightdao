# WASM 自描述段扫描：给 B6 两条阻断项补客观证据（2026-11-07）

范围：只读扫描 `contracts/wasm/*.wasm` 的顶层 custom section，回答一个此前只能靠
`BUILDLOG.tsv` 自述的问题——**归档的链上字节码里，到底还留着多少"我是谁、我用什么编的"的证据**。
工具：`infra/wasm_meta_scan.py`（只读，不写主网、不改文件，除显式 `--out`）。
现场：网关仓库 `main @ e16939b`，UTC 2026-11-07 01:1x。

## 一、实测事实

| 项 | 结果 |
|---|---|
| 扫描产物数 | 30 份 `.wasm` |
| 去重后的 sha256 | 29 个（唯一重复：`governance.wasm` 与 `code13_governance.wasm` 逐字节相同） |
| 与 `SHA256SUMS` 对账 | 30/30 一致，0 处不一致、0 个不在册 |
| 含 `cosmwasm` 自描述段（contract_name / contract_version） | **0/30，一个都没有** |
| 含 `producers` 段 | 30/30 |
| `producers` 组合种类 | **1 种：`Rust; rustc=1.85.0 (4d91de4e4 2025-02-17)`**，全部产物一致 |
| `wasm-opt` / cw-build 痕迹 | 无（producers 里没有 wasm-opt，也没有 cosmwasm 段，说明这批码不是走 cw-build 标准链路出的） |
| 按文件名归到 `contracts/contracts/` 的 crate | 28 份 NAME-HINT，2 份 NO-METADATA：`code16_vesting-v2.wasm`、`code17_ecosystem_fund.wasm` |

## 二、解读（含边界，不把话说满）

1. **阻断②（`toolchain=unknown`）有了可核对的观测值。** producers 段是编译器自己写进字节码的署名，
   全部 30 份都指向 `rustc 1.85.0 (4d91de4e4 2025-02-17)`。因此 BUILDLOG 的 toolchain 列不再是"无人知道"，
   而应写成"由产物 producers 段观测得到 rustc 1.85.0"。**但 producers 只是编译器署名，不等于确定性构建**，
   所以 `reproducible` 一列必须继续保持 `no`，直到 `infra/ci_wasm_compare.py` 的逐字节比对通过——
   本轮没有动 `BUILDLOG.tsv`（该文件被迁移门禁 `infra/ld_migrate_gate.py` 读取，改它属于动门禁口径，需人审）。

2. **阻断①（code 16/17 缺源 crate）得到独立佐证，但措辞要收窄。** 因为全体产物都不带 `cosmwasm`
   自描述段，"哪个 code id 对应哪个 crate"这件事**无法由字节码自证**，目前只能靠文件名归类。
   `code16_vesting-v2` / `code17_ecosystem_fund` 之所以判 NO-METADATA，是"没有自描述证据 + 仓库里没有
   同名 crate"两条叠加，**不等于已经证明源码不存在**。给审计方的正确表述是：这两份只能靠"源码 + 逐字节
   重建比对"闭环，靠字节码里的元数据闭不了环。

3. **`governance.wasm == code13_governance.wasm` 是全场唯一一份"本地构建产物与链上 code id 完全相同"的样本。**
   它可以直接当 CI 比对流程的回归锚点：先用 rustc 1.85.0 + wasm32 重建 governance crate，若能复现出
   这一份字节，说明构建口径（优化级别、profile、feature、target）找对了，再往下推其余 9 个有源 crate；
   若复现不出来，就说明口径还没对齐，此时任何 `reproducible=yes` 的声称都不可信。

## 三、下一步（均属非破坏，按可自动做 / 需人审分开）

可自动推进（只读链、只读仓库）：

- 在 CI 里按上述锚点顺序做确定性重建，逐份跑 `python3 infra/ci_wasm_compare.py`，把"一致 / 不一致 /
  未产出"的三态结论积累成表，作为豁免期（2026-11-30）内的进度口径。
- 把本扫描脚本挂到每次合约升级后跑一遍，比对 producers 组合是否从 1 种变成多种（多工具链混用是
  复现失败最常见的原因）。

需人审后再动（本轮没做）：

- `BUILDLOG.tsv` 的 toolchain 列按观测值填写，并新增 evidence 列（`wasm.producers`）。该文件是迁移
  门禁的输入，改判定口径要用户确认。
- code 16/17 的路线选择：找回原源码，还是按白皮书 §5.3 / §5.10 重写并以**新 code id** 迁移。
  后者涉及改合约与链上迁移，按硬规则不在自走执行范围内，需要提案与逐次授权。

## 四、复算命令

```
cd /home/ubuntu/repo
python3 infra/wasm_meta_scan.py            # 表格 + 汇总，只读
python3 infra/wasm_meta_scan.py --out /tmp/wasm_meta.json   # 需要机读结果时
```
