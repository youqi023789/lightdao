# LightDAO 发布章程(RELEASE)

原则:**任何问题不应由用户先发现。** 靠三层闭环:上线前门 → 灰度发布 → 生产探针/金丝雀。
且**验证机制本身也要被验证**:门必须跑在退化态,探针要有自测,否则等于没有。

## 1. 语义化版本(MAJOR.MINOR.PATCH)
- 载体(四处必须一致,由真相对探针校验):`js/app_*.js` 的 `LDBUILD` 与 `APPV`、`js/ver.json {"v"}`、各 html 的 `?v=`。
- PATCH=bugfix/文案/UI;MINOR=新增向后兼容功能;**MAJOR=共识/链升级或破坏性变更(跨整数)**。
  例:网站修复=1.0.x;v3-lightfee 链升级=2.0.0;v4 合约迁移=2.1.0。
- 客户端自愈合:`ver.json.v != APPV` 时按"按版本哨兵"自动重载一次/版本(同会话可多次升版)。

## 2. Web 发布:唯一入口 `infra/promote.py`(禁止手改 /var/www 的 js 或 ?v)
1. 备候选:仓库 `client/` → `/home/ubuntu/candidate/`。
2. 灰度(不碰主站):`sudo promote.py /home/ubuntu/candidate <NEXT>`
   → 建 staging(`:8093`,独立 root),对 staging 跑 **qa_site + qa_extra + site_audit**(经 `LD_WEB_ROOT`/`LD_PORT`)+ **qa_truth**(浏览器+静态)。任一 fail 即停。
3. 通过后才:`sudo promote.py /home/ubuntu/candidate <NEXT> --apply`
   → 先快照旧 js 到 `/var/www/lightdao_js_prev`(含 VERSION),再推候选到主站并改 `?v`/`ver.json`。
4. 观察窗:发布后 30 分钟看 监控 truth_probe、client_errors、Discord 金丝雀;无告警视为稳定。
5. 回滚:`sudo promote.py --rollback`(恢复旧 js+版本,客户端按版本哨兵自动重载)。

## 3. 门清单(各自抓什么)
- qa_site:JS 语法、处理器↔元素 id 接线、资源存在。
- qa_extra:ES 兼容(禁 ?. ?? 等)、孤儿交互元素、DEFINED-GLOBALS。
- site_audit:27 端点、死链/锚点/占位符。
- mobile_e2e:6 剖面全流程(微信/QQ/旧 WebView/iOS 隐私模式/存储抛错…)。
- qa_truth:**真相不变量**(徽章==LDBUILD==ver.json;状态徽章==status.json;倒计时抗设备时钟漂移)+ **退化态**(断网优雅、status 取数缓存击穿、回前台重取、按版本自愈哨兵、gasPrice=0.2)。

## 4. 退化态矩阵(为什么必须有)
真实用户活在退化态:陈旧 HTTP 缓存、后台被节流、同会话二次升版、无代付授权、弱网/断网、设备时钟漂移、隐私模式存储抛错。pristine 快乐路径测试永远复现不了这些;故每个退化态都要有剖面断言"有清晰反馈、且不撒谎"。

## 5. 生产探针(上线后)
- 错误信标 `/v1/clienterr`(阈值 ≥5/小时、每小时去重)。
- 客户端真相自检:徽章/状态一旦"显示≠真相"自动上报信标。
- 监控真相对探针:线上 app_1/2/3+ver.json+status.json 互一致、gasPrice 正确、缓存击穿在位、status 新鲜;不一致每小时告警。
- 金丝雀:每日 05:40Z 真实"定稿→签根→领取→断言到账";05:45Z 降级金丝雀(无授权钱包:断言 code38 干净识别 + 0.2 手续费无 min-gas 回归)。
- status.json 徽章(链/网关/定稿/签根/HTTP)。

## 6. 链发布(共识级,禁止单台金丝雀——会被 jailed)
x/upgrade gov 提案 + 7 台协调高度换二进制:看门狗监听 `UPGRADE <name> NEEDED` → cp lightd.new→wasmd + restart,DONE_FLAG 门控,`Restart=always` 保证 halt 期反复日志可被捕获。升级后验收 cron 校验(7 台二进制 sha、高度、lightfee 事件、无 crash-loop),通过才提参数提案;回滚=恢复旧二进制+restart。

## 7. 时区
- 系统 cron 一律 `CRON_TZ=UTC`(历史上曾误跑 CST,导致定稿滞后 ~16h,已修)。
- 日界:2026-09-30 00:00 UTC 起为 00:00 UTC 对齐(之前 04:48 UTC);切换日为一个短天,历史天数索引与已上链根不变。
- UI 一律按**用户本地时区**显示结算倒计时与刷新时刻。
