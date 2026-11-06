# 多语言投递链：本轮实测根因与跟踪例外（2026-11-06）

## 一句话结论

词典齐全、分片按序引用、页面权重达标**都不等于页面真的被翻译**。今天找到并修掉的是
"语言层在 app / funds / institutions 页启动那一次静默抛错"，并新增 g16 门禁专门盯这件事。

## 实测证据（可复现）

```
# 1) 修复前：这两页渲染完成后 <html> 上根本没有 data-ld-i18n（语言引擎没盖章）
google-chrome --headless=new --virtual-time-budget=20000 --dump-dom \
  "https://lightdao.net/app.html?lang=de" | grep -o 'data-ld-i18n="[^"]*"'      # 无输出

# 2) 同一时刻在浏览器里手动调一次引擎，立刻出数 —— 说明引擎是好的，是"启动那次没跑成"
Runtime.evaluate: window.__ldApplyLang("de")   →  data-ld-i18n = "w72 s221 same0 guard0"

# 3) 根因：i18n.js 引用了 pairValue()，但全站 js 目录里没有任何一处定义它
grep -rn "pairValue" /home/ubuntu/repo/client/js | head      # 只有 i18n.js:161 一处引用，零定义
grep -rc "function pairValue" /home/ubuntu/repo/client/js/*.js | grep -v ':0'   # 修复后才有

# 4) 修复后（v1.10.38 线上实测）：app/funds/institutions 都盖章且可见中文达标
python3 /usr/local/bin/ld_i18n_boot_check.py --base https://lightdao.net --langs de,ar
```

为什么以前所有门禁都是绿的：词典结构（g12）、分片挂载（g13）、页面体积（g3）检查的都是**静态文件**，
而"抛异常被 `try/catch` 咽掉"只发生在运行时。g16 是唯一一个"真机渲染后必须拿到运行痕迹"的门。

## g16_i18n_boot 的口径（避免用数字掩盖问题）

| 现象 | 处理 |
| --- | --- |
| `<html>` 无 `data-ld-i18n` | 红：引擎在这一页根本没跑成 |
| 值为 `boot-miss:N` | 红：boot 自证重放（0/300/1200/3000ms）后仍没盖章 |
| 有 `data-ld-i18n-err` | 红：语言层抛过错（原文留在属性里，不再静默） |
| 外语页可见中文 > 6 | 先复测一次（异步表格在短预算下会呈现"还没轮到翻"的中间态）；两轮都超标才红 |
| 「中文 / English」刻意对照 | 不计漏翻，**单列数量**写进日志（不许拿它当"零残留"邀功） |
| 日/韩正常译文里的汉字 | 邻近出现假名/谚文即认定是本语种译文，不误报；无假名混排的纯中文照样红 |
| 白皮书长文档 | 允许未译完，但页面必须自报 `data-ld-wp-pending="N"`，且 N 与实测一致才放行 |

自测：`python3 /usr/local/bin/ld_i18n_boot_check.py --selftest` → 13/13（含"接错地址必须报量具问题"
这条反例，防止把"读不到"当成"没翻译"或"没问题"）。

## 跟踪例外（带解除日期，逾期即视为故障）

1. **白皮书整篇译文未完**：德语版仍有 **209 段**保持中文原文，页面顶部已按 14 语种如实声明数量。
   解除条件：`ld_wp_build.py` 把该语种 pending 清零；值守 `ld_wp_check.py` 每小时推进、
   免费接口限流时自动退避（不是无限期）。责任：agent。复查日：2026-11-20。
2. **主网跨链通道未开**：链上实测 0 个 IBC 轻客户端 / 0 条通道；中继身份已建、两侧密钥已进 hermes、
   开通器护栏 7/7、值守自检 6/6，等所有者转入油钱后由 cron 自动开通并双向自证。
   解除条件：`/home/ubuntu/ld_xc_mainnet.json` 的 status 变为 `opened` 且 docs 里有双向转账回执。
   责任：所有者转入 + agent 值守。复查日：2026-11-14。
3. **外来面额的"发出去"仍缺客户端签名路径**：链上收币参数实测 `receive_enabled=true`（任意外来
   `ibc/…` 都能入账），客户端已能如实显示全部面额；但把外来面额**跨回对面**需要
   `MsgTransfer`（IBC 转账消息）的本地签名，本站 PWA 目前只内置了本链 `ulight` 的发送。
   解除条件：客户端注册 `/cosmos.ibc.applications.transfer.v1.MsgTransfer` 的编码器并在测试网跑通一笔。
   责任：agent。复查日：2026-11-16。
