#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把机器翻译缓存重写成与其它词典表同构的静态表（var L + var T + __ldExpandLangs），
   这样 g12 的结构校验对它一视同仁（列数、语种码、跨文字混入都会被点名）。
   加载位置在所有人工表之后，而展开器只填空槽 → 人工译文永远优先，本表只补空缺。
   用到本表时右下角挂一枚"机器翻译·未人工校对"徽标，点一下回到中文原文。"""
import json, os, re, subprocess

REPO_JS = "/home/ubuntu/repo/client/js"
LIVE_JS = "/var/www/lightdao/js"
CACHE = "/home/ubuntu/ld_i18n_mt_cache.json"
ORD = ["en", "fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil", "es", "pt", "id", "vi"]

TPL_HEAD = """/* LD-I18N-MT-20261104  机器翻译补齐表（未人工校对）。
   与人工表同构（var L + var T + __ldExpandLangs），所以 g12 一视同仁地查它；
   加载排在全部人工表之后，且展开器只填空槽 → 人工译文永远优先。 */
(function () {
  "use strict";
  var L = ["@@LANGS@@"];
  var T = {
"""

TPL_BODY = """  };
  window.__ldMtKeys = Object.keys(T).length;
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldMtStats = { error: "expander-missing" };
    return;
  }
  /* 关键一步：展开器只往"已有的键"里填空槽，新句子必须先把键建出来，
     否则整行成为死行（缓存有译文、分片里有这行、页面仍是中文）。
     已存在的键绝不覆盖 —— 人工译文优先；空语种交给下面的 __ldExpandLangs 补。 */
  var M = window.LDI18N = window.LDI18N || {};
  var created = 0;
  for (var ck in T) {
    if (!Object.prototype.hasOwnProperty.call(T, ck)) continue;
    if (M[ck]) continue;
    var cp = String(T[ck]).split("|"), co = {};
    for (var ci = 0; ci < L.length && ci < cp.length; ci++) { if (cp[ci]) co[L[ci]] = cp[ci]; }
    if (co.en || co.de || co.fr) { M[ck] = co; created++; }
  }
  window.__ldMtCreated = created;
  window.__ldMtStats = window.__ldExpandLangs(L, T);
  function badge() {
    try {
      var lang = (document.documentElement.getAttribute('lang') || 'zh').toLowerCase();
      if (lang === 'zh' || !window.__ldMtKeys) return;
      if (document.getElementById('ldMtBadge')) return;
      var d = document.createElement('div');
      d.id = 'ldMtBadge';
      d.setAttribute('role', 'note');
      d.style.cssText = 'position:fixed;right:10px;bottom:10px;z-index:9999;background:#1c2230;color:#cfd6e4;border:1px solid #3a465c;border-radius:8px;padding:6px 9px;font:12px/1.5 system-ui;cursor:pointer;opacity:.92';
      var KEY = "机器翻译 · 未人工校对（点此看中文）";
      var lab = KEY;
      try { if (window.__ldT) { var t = window.__ldT(KEY); if (t && t !== KEY) lab = t; } } catch (e) { }
      d.textContent = '\\u{1F916} ' + lab;
      d.title = 'Machine-translated text, not human-reviewed. Click for the Chinese source.';
      d.onclick = function () {
        try { localStorage.setItem('ld_lang', 'zh'); } catch (e) { }
        location.href = location.pathname + '?lang=zh';
      };
      document.body.appendChild(d);
    } catch (e) { }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', badge);
  } else { badge(); }
})();
"""


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def human_keys():
    ks = set()
    for fn in sorted(os.listdir(REPO_JS)):
        # 机器表自己不能算"人工键"：否则第二轮会把上一轮的机器行当成"已覆盖"而自我清空
        # （实测踩过：分片改名 i18n_mt_*.js 后 47 条只剩 1 条）
        if not fn.startswith("i18n") or fn.startswith("i18n_mt"):
            continue
        try:
            t = open(os.path.join(REPO_JS, fn), encoding="utf-8").read()
        except Exception:
            continue
        for m in re.finditer(r'(?m)^\s{2,4}"((?:[^"\\]|\\.)+)"\s*:', t):
            ks.add(m.group(1))
        for m in re.finditer(r'en\(\s*"((?:[^"\\]|\\.)+)"\s*,', t):
            ks.add(m.group(1))
    return ks


cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
HK = human_keys()
rows = []
kept = 0
dropped = 0
MAX_KEY_CHARS = int(os.environ.get("LD_MT_MAX_KEY_CHARS", "900"))
skipped_big = 0
for k, v in sorted(cache.items()):
    if k in HK:
        continue
    # 整篇文档那种 blob：一行的体积就能顶穿分片上限，运行时也永远命中不了
    if len(k) > MAX_KEY_CHARS or sum(len(str(x)) for x in v) > 24000:
        skipped_big += 1
        continue
    if not isinstance(v, list) or len(v) != len(ORD) or not all(str(x).strip() for x in v):
        continue
    # 质量闸：后端"没真翻到"的行一律不写进表。留着会让界面显示英文却以为有译文，
    # 比继续显示中文原文更糟（中文至少是可核对的原文）。
    #   ① 非拉丁语种（ja/ko/ru/ar/hi）的值若是纯 ASCII → 就是把英文原样吐回来了；
    #   ② 任何一列与英文列一字不差 → 同样算没翻到。
    def _ascii_only(s):
        return all(ord(c) < 128 for c in s)
    en_val = str(v[0]).strip()
    drop = False
    for i, lang in enumerate(ORD):
        val = str(v[i]).strip()
        if lang in ("ja", "ko", "ru", "ar", "hi") and _ascii_only(val):
            drop = True
            break
        if i > 0 and val == en_val:
            drop = True
            break
        # 11-05 实测补的一条：ja/ko 列原样抄中文（「验证者」「不得执行」）既不是纯 ASCII
        # 也不等于英文列，于是顺利通过旧闸进了表 —— 运行时"翻译"成同样的汉字，
        # 页面没变化、普查却一直报漏翻，而流水线自认"补完了"。等于键本身一律判没翻。
        if val == k.strip():
            drop = True
            break
    if drop:
        dropped += 1
        continue
    rows.append('    "%s": "%s",' % (esc(k), "|".join(esc(str(x)) for x in v)))
    kept += 1

MT_LABEL = "'机器翻译 · 未人工校对（点此看中文）'"
# 发布门禁 g3_weight 对单个 JS 有 128KB 上限（实测 156KB 被挡），所以按体积分片；
# 每片各自登记，展开器只填空槽 → 片与片之间没有先后依赖。
SHARD_LIMIT = int(os.environ.get('LD_MT_SHARD_KB', '60')) * 1024
shards, cur, cursz = [], [], 0
for r in rows:
    b = len(r.encode("utf-8")) + 1
    if cursz + b > SHARD_LIMIT and cur:
        shards.append(cur)
        cur, cursz = [], 0
    cur.append(r)
    cursz += b
if cur:
    shards.append(cur)

names = []
for idx, sh in enumerate(shards, 1):
    name = "i18n_mt_%d.js" % idx
    body = (TPL_HEAD.replace("@@LANGS@@", '","'.join(ORD)) + "\n".join(sh) + "\n" + TPL_BODY)
    body = body.replace("MT_LABEL", MT_LABEL)
    for d in (REPO_JS, LIVE_JS):
        try:
            open(os.path.join(d, name), "w", encoding="utf-8").write(body)
        except Exception as e:
            print("  WARN 写失败 %s：%s" % (name, str(e)[:50]))
    names.append((name, len(body.encode("utf-8"))))

# 老的单文件形态作废：挪进 staging 而不是留着——同一份译文留两处，必有一处会过期
for d in (REPO_JS, LIVE_JS):
    old = os.path.join(d, "i18n_mt.js")
    if os.path.exists(old):
        try:
            os.replace(old, "/home/ubuntu/ld_i18n_mt_staging/" + os.path.basename(os.path.dirname(d)) + "__i18n_mt.js.hold")
        except Exception as e:
            print("  WARN 旧文件挪不动：%s" % str(e)[:50])

HARD = 122880
over = [n for n, s in names if s > HARD]
print("机器表分片 %s ｜ %d 条 ×14 语种（剔除没真翻到的 %d 条、超长整篇 blob %d 条）"
      % (", ".join("%s=%dKB" % (n, s // 1024) for n, s in names), kept, dropped, skipped_big))
if over:
    print("MT-SHARD FAIL 单片超过 128KB 上限：%s —— 调小 LD_MT_SHARD_KB 或提高 LD_MT_MAX_KEY_CHARS 的过滤"
          % " ".join(over))
    raise SystemExit(1)
print("MT-SHARD OK：全部 %d 片都在 128KB 以内（按 UTF-8 真实字节算）" % len(names))
if names:
    r = subprocess.run(["node", "--check", os.path.join(REPO_JS, names[0][0])], capture_output=True, text=True)
    print("node --check:", "OK" if r.returncode == 0 else r.stderr[:220])
