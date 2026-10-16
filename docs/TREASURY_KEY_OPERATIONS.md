# 金库签名钥运行手册（TREASURY KEY OPERATIONS）

生效时间：2026-10-16 01:37 UTC（北京 09:37）。本文件记录一次**主动降低集中风险**的变更，
以及今后动用金库时的正确流程。

## 变更内容

网关服务器上**不再持有**金库 5 个签名人的私钥。

- 摘除前：`~/.wasmd/keyring-test/signer1..signer5.info`（明文，Cosmos `test` 钥匙串 = 私钥直接落盘）
  → 任何人拿到这台机器，就凑齐 3/5 票，可绕过审批发起并执行金库转账。
- 摘除后：5 把私钥只存在于**加密冷备份**中；解密口令**只由所有者离线保管**，服务器上没有。
- 与密文同机存放的口令文件已一并清除（否则"加密"形同虚设：拿到机器就能自己解）。

链上安全机制**未改动**：仍是 3/5 多签审批 + 72 小时时间锁。变的只是"攻击者需要拿下的东西"
从「一台服务器」变成「一台服务器 + 一份离线口令」。

## 摘除前的强制闸门（已执行，通过）

1. 从加密备份解密到临时目录，逐把 `wasmd keys show` 解析地址；
2. 与链上 `treasury_multisig {"signers":{}}` 返回的 5 个地址**逐一精确比对**；
3. 全部一致才允许删除；删除后立即 `shred` 掉中间副本。

> 这一步第一次跑是**失败**的，原因是我的校验脚本把 bech32 地址长度写死成 39 位
> （实际 `wasm1` 后是 38 位），导致正则永不匹配、误判"备份不可用"。
> 教训：**闸门报错时先怀疑闸门本身**，不能因为"闸门拦住了"就以为备份真的坏了——
> 反过来更危险：如果我把长度放宽成"能过就行"，就可能带着一个不可还原的备份删掉私钥。

## 今后要动用金库时的正确流程

前提：需要所有者提供解密口令（这是设计出来的摩擦，不是 bug）。

```bash
# 1) 用口令解密到内存盘（tmpfs，不落磁盘）
mkdir -p /dev/shm/ldkeys && chmod 700 /dev/shm/ldkeys
read -s -p "口令: " P && openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -pass pass:"$P" -in /home/ubuntu/backup/treasury-keys-*/treasury_signers_keyring.tar.gz.enc \
  | tar xz -C /dev/shm/ldkeys && unset P

# 2) 用临时钥匙串发起/审批/执行（--home 指向 /dev/shm/ldkeys 的父级）
wasmd keys list --keyring-backend test --home /dev/shm/ldkeys
#   …… 正常执行 propose_transfer / approve / execute_transfer ……

# 3) 用完立刻销毁内存副本
find /dev/shm/ldkeys -type f -exec shred -u {} + ; rmdir -p /dev/shm/ldkeys/keyring-test 2>/dev/null

# 4) 事后必须做的三件事（硬规则）
#    a. 写 docs/TREASURY_MOVEMENT_LEDGER.md：提案号/签名人/时间锁到期/执行哈希/执行后余额
#    b. 执行前后各向所有者报告一次
#    c. 复跑 ld_monitor.py 与渲染巡检确认无副作用
```

## 备份位置与保管要求

| 件 | 位置 | 说明 |
|---|---|---|
| 密文 | 网关 `/home/ubuntu/backup/treasury-keys-20261015T072658Z/*.enc` + 所有者电脑各一份 | 无口令即无用 |
| 口令 | **仅所有者离线持有**（本机文件 `KEYRING口令-请离线保存.txt`） | 建议再抄一份到密码管理器或纸质，分两处存放 |

⚠️ **口令丢失 = 5 把私钥永久不可恢复**，而链上签名人名单无法自行更换（更换需 3/5 现有签名人
先执行 `set_signers` 类提案）。所以口令的可用性比保密性更致命——请先做一次"能否解密"演练。

## 建议的下一步（尚未做）

1. 把 5 把钥**分散到 5 台不同主机/硬件**，每人一把，彻底消除单点（需要那几台的登录通道）。
2. 口令改用更强 KDF 或分片（如 Shamir 3/5），避免"一句口令丢了全完"。
3. 给"金库相关操作"加检测点：任何 `treasury_multisig` 的 `propose_transfer`/`execute_transfer`
   事件出现时自动告警并写台账——目前只有事后人工记录。
