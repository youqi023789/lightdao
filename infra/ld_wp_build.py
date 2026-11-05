#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_wp_build.py v2 —— 白皮书整篇按语种生成译文，可断点续跑、限流退避、不假装完成。

v1 的实测缺陷（2026-11-05）：
  · 三个进程并行 + 页面补齐流水线一起打，google gtx 直接 429；
  · v1 把"取不到译文"和"结构校验不过"混成一类 bad_lines，文件只在最后一步落盘 ——
    中途被打断就全丢，第二天从零再打一遍配额；法语一轮 156/343 段"失败"其实是 429。
v2 的规矩：
  · 每个语种一份单元缓存 ld_wp_cache.<lang>.json，跑多少存多少，随时可中断续跑；
  · 429 走指数退避（5/15/45/120 秒 + 抖动），连续多次仍失败就**停手**并把剩余段记为 pending，
    而不是硬刷配额；pending>0 会在清单里明写，配套门禁 ld_wp_check.py 会把"还在生成"报出来；
  · 结构校验（行数/竖线/链接/反引号/标题/列表项计数）不过 → 该段保留中文原文并记 bad，
    宁可留一段原文，也绝不把表格、代码、链接翻坏。

用法：ld_wp_build.py [--langs de,fr] [--force] [--max-units N]
"""
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ld_i18n_mt_build2 import gtx, translate_batch, alert, load

SRC = os.environ.get("LD_WP_SRC", "/var/www/lightdao/whitepaper.md")
OUT_DIRS = ["/home/ubuntu/repo/client/wp", "/var/www/lightdao/wp"]
MANIFEST = "/home/ubuntu/ld_wp_manifest.json"
CACHE_DIR = "/home/ubuntu/ld_wp_cache"
ORD = ["fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil", "es", "pt", "id", "vi"]
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
LATINISH = re.compile(r"[A-Za-zÀ-ÿƠƠ]")
NOTICE = {
    "fr": "> Traduction automatique, non relue. En cas de divergence, la version chinoise fait foi.",
    "de": "> Maschinell übersetzt, nicht menschlich geprueft. Bei Abweichungen gilt die chinesische Originalversion.",
    "ru": "> машинный перевод, без вычитки человеком; при расхождениях действительна китайская оригинальная версия.",
    "ja": "> 機械翻訳・人間未校閲。食い違いがある場合は中国語原文が優先されます。",
    "ko": "> 기계 번역이며 사람 검수를 거치지 않았습니다. 차이가 있으면 중국어 원문이 우선합니다.",
    "ar": "> ترجمة آلية غير مُراجَعة بشريًا؛ وعند أي تعارض تعتمد النسخة الصينية الأصلية.",
    "hi": "> यह मशीन अनुवाद है, मानव समीक्षा नहीं हुई; असंगति होने पर चीनी मूल पाठ मान्य होगा।",
    "tr": "> Otomatik çeviri, insan tarafından gözden geçirilmedi. Anlaşmazlık durumunda Çinçe orijinal metin esas alınır.",
    "fil": "> Awtomatikang pagsasalin, hindi sinusuri ng tao. Kung may hindi pagkakatugma, ang orihinal na Tsino ang may kapangyarihan.",
    "es": "> Traducción automática sin revisión humana. En caso de discrepancia, prevalece la versión original en chino.",
    "pt": "> Tradução automática sem revisão humana. Em caso de divergência, prevalece a versão original em chinês.",
    "id": "> Terjemahan mesin tanpa pemeriksaan manusia. Jika ada perbedaan, versi asli bahasa Mandarin yang berlaku.",
    "vi": "> Bản dịch máy chưa qua hiệu đính con người; nếu có sai khác, bản gốc tiếng Trung được ưu tiên.",
}
LINK_ZH = "[中文原文 / Chinese original](/whitepaper.md)"
SIG_NAMES = ("行数", "竖线", "链接", "反引号", "标题井号", "列表项")


def fence_split(lines):
    blocks, cur, incode, cur2 = [], [], False, []
    for ln in lines:
        if ln.strip().startswith("```"):
            if not incode:
                if cur:
                    blocks.append((False, cur)); cur = []
                incode, cur2 = True, [ln]
            else:
                cur2.append(ln); blocks.append((True, cur2)); cur2, incode = [], False
            continue
        (cur2 if incode else cur).append(ln)
    if cur:
        blocks.append((False, cur))
    return blocks


def units_of(lines):
    out, buf = [], []
    for ln in lines:
        if not ln.strip():
            if buf:
                out.append(("u", buf)); buf = []
            out.append(("b", [ln]))
        else:
            buf.append(ln)
    if buf:
        out.append(("u", buf))
    return out


def sig(text):
    ls = text.split("\n")
    return (len(ls),
            sum(l.count("|") for l in ls),
            sum(l.count("](") for l in ls),
            sum(l.count("`") for l in ls),
            sum(len(m.group(0)) for m in re.finditer(r"^\s*#+", text, re.M)),
            sum(1 for m in re.finditer(r"^\s*[-*]\s", text, re.M)))


def sig_diff(a, b):
    return "; ".join("%s %d→%d" % (n, x, y) for n, x, y in zip(SIG_NAMES, a, b) if x != y)


def plan_of(src_text):
    plan = []
    for is_code, ls in fence_split(src_text.split("\n")):
        if is_code:
            for x in ls:
                plan.append((x, False))
            continue
        for kind, grp in units_of(ls):
            plan.append(("\n".join(grp), kind == "u"))
    return plan


def get_one(unit, lang, tries=4):
    """一段一译，带 429 退避；返回 (译文|None, 是否疑似配额耗尽)"""
    src = "zh-CN" if CJK.search(unit) else "en"
    rate_limited = False
    for k in range(tries):
        try:
            v = gtx(unit, src, lang, limit=4600)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                rate_limited = True
                time.sleep(min(120, 5 * (3 ** k)) + random.random() * 2)
                continue
            time.sleep(2 + k)
            continue
        except Exception:
            time.sleep(2 + k)
            continue
        if not v:
            continue
        if sig(v) != sig(unit):
            # 整段结构对不上（表格/加粗/反引号被并句）：能按行拆就按行拆着译，每行单独校验后再拼回去。
            # 不做这种回退时，实测德语版有 8 段（33 行、189 个中文片段）被整段留成中文——
            # 一段表格两行就够让校验失败，但那不代表这两句不能翻。
            if "\n" in unit:
                lines_out, ok_all = [], True
                for one in unit.split("\n"):
                    if not one.strip():
                        lines_out.append(one)
                        continue
                    v1, rl1 = get_one(one, lang, tries=2)
                    rate_limited = rate_limited or rl1
                    if v1 is None:
                        ok_all = False
                        break
                    lines_out.append(v1)
                if ok_all and sig("\n".join(lines_out)) == sig(unit):
                    return "\n".join(lines_out), rate_limited
            return None, rate_limited
        if lang not in ("ja", "ko") and not LATINISH.search(v):
            return None, rate_limited
        return v, rate_limited
    return None, rate_limited


def build(lang, plan, man, force, max_units):
    key = hashlib.sha256("\n".join(u for u, _ in plan).encode("utf-8")).hexdigest()[:16]
    cf = os.path.join(CACHE_DIR, "%s.json" % lang)
    cache = load(cf, {})
    rec = man.get(lang, {})
    todo = [u for u, need in plan if need and (force or u not in cache)]
    # 只有"确实一段都没落下"才允许跳过。老记录里没有 pending/kept_zh 字段（v1 写的），
    # 一律当成需要复检：否则那 8 段结构校验失败的原文永远没人再试（改一处不改一处=白修）。
    if not force and rec.get("src_sha") == key and int(rec.get("pending", -1) or 0) == 0 \
            and int(rec.get("kept_zh", -1) or 0) == 0:
        print("  %s：源文件未变且无待补段，跳过" % lang)
        return rec
    print("  %s：待译段 %d（已缓存 %d）" % (lang, len(todo), len(cache)), flush=True)
    stopped = False
    done = 0
    # 先试打包（同一语种一次几十段），失败或条数对不上再退回逐段
    if todo:
        for chunk_start in range(0, len(todo), 60):
            grp = todo[chunk_start:chunk_start + 60]
            src = "zh-CN" if CJK.search(grp[0]) else "en"
            try:
                got = translate_batch(grp, lang, src)
            except Exception as e:
                alert("WARN 批量失败 %s：%s" % (lang, str(e)[:60]))
                got = {}
            for u in grp:
                if u in got and sig(got[u]) == sig(u):
                    cache[u] = got[u]
                    done += 1
            if chunk_start and chunk_start % 120 == 0:
                save_json(cf, cache)
    # 补齐批量没拿到的
    miss = [u for u in todo if u not in cache]
    for u in miss:
        if done + 1 > max_units and max_units:
            stopped = True
            break
        v, rl = get_one(u, lang)
        if v is None:
            if rl and sum(1 for x in miss if x not in cache) > 3:
                stopped = True
                break
            continue
        cache[u] = v
        done += 1
        if done % 25 == 0:
            save_json(cf, cache)
            print("    %s 进度 %d 段" % (lang, done), flush=True)
    save_json(cf, cache)
    out, bad = [], 0
    for u, need in plan:
        if not need:
            out.append(u)
            continue
        v = cache.get(u)
        if v is None:
            bad += 1
            out.append(u)
        else:
            out.append(v)
    pending = len([u for u, need in plan if need and u not in cache])
    text = NOTICE.get(lang, "") + "\n" + LINK_ZH + "\n\n" + "\n".join(out)
    n_units = sum(1 for _, need in plan if need)
    res = {"src_sha": key, "units": n_units, "cached": len(cache), "pending": pending,
           "kept_zh": bad, "bytes": len(text.encode("utf-8")),
           "stopped_early": stopped,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for d in OUT_DIRS:
        try:
            os.makedirs(d, exist_ok=True)
            tmp = os.path.join(d, "whitepaper.%s.md.tmp" % lang)
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, os.path.join(d, "whitepaper.%s.md" % lang))
        except Exception as e:
            alert("WARN 写 %s 失败：%s" % (d, str(e)[:50]))
    print("  %s：%d/%d 段有译文，仍留原文 %d 段%s" % (
        lang, n_units - bad, n_units, bad, "（本轮提前停：限流）" if stopped else ""), flush=True)
    return res


def save_json(path, obj):
    """原子落盘：两个进程同时在写同一个缓存文件时，json.dump 直接覆盖会写出半截 JSON
       （下次读回来直接炸）。先写 .tmp 再 os.replace。"""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def main():
    args = sys.argv[1:]
    langs = ORD
    if "--langs" in args:
        langs = args[args.index("--langs") + 1].split(",")
    force = "--force" in args
    max_units = int(args[args.index("--max-units") + 1]) if "--max-units" in args else 0
    os.makedirs(CACHE_DIR, exist_ok=True)
    src = open(SRC, encoding="utf-8").read()
    plan = plan_of(src)
    print("源文件 %d 字节；待译单元 %d" % (len(src.encode("utf-8")), sum(1 for _, n in plan if n)))
    man = load(MANIFEST, {})
    for lg in langs:
        man[lg] = build(lg, plan, man, force, max_units)
        save_json(MANIFEST, man)
    pend = sum(int(v.get("pending", 0)) for v in man.values())
    kept = sum(int(v.get("kept_zh", 0)) for v in man.values())
    if pend:
        alert("PROGRESS 白皮书还有 %d 段没译文（限流或后端故障），%d 段暂留原文；重跑本脚本会续上" % (pend, kept))
    return 1 if pend else 0


if __name__ == "__main__":
    sys.exit(main())
