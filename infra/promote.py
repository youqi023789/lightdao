#!/usr/bin/env python3
"""promote.py — 灰度发布唯一入口(语义化版本)。
用法:
  promote.py <SOURCE_DIR> <NEXT>            # 建 staging(候选=NEXT) + 跑全部门, 不碰主站
  promote.py <SOURCE_DIR> <NEXT> --apply    # 门全过才把候选推到主站(先快照旧版供回滚)
  promote.py --rollback                     # 回滚到上一次 promote 前的主站 js/版本
SOURCE_DIR = 候选站点根(含 app.html 与 js/), 例如 /home/ubuntu/candidate 或 /var/www/lightdao(自测)。
门 = qa_site + qa_extra + site_audit(对 staging) + qa_truth(浏览器+静态, 对 staging :8093) + g10_root_parity(Merkle 根对拍)。
任一失败 => 不 promote, 退出非0。"""
import io, os, re, glob, json, shutil, subprocess, sys

MAIN = "/var/www/lightdao"; STG = "/var/www/lightdao_staging"; PREV = "/var/www/lightdao_js_prev"
SEM = r"[\d]+\.[\d]+\.[\d]+"

# N1 (2026-10 monthly audit): SRI/integrity is now enforced in the served HTML, so every release
# MUST regenerate the manifest and re-inject integrity (relabel rewrites ?v= and JS bytes, which
# changes hashes). Without this the next promote would white-screen the site. sri_integrity.py is
# the shared, root-parameterized helper (gen/inject/verify) installed under /usr/local/bin.
sys.path.insert(0, "/usr/local/bin")
try:
    import sri_integrity as _sri
except Exception:
    _sri = None

def maintain_sri(root, label=""):
    """Regenerate SRI.json for `root`, (re)inject integrity= into its HTML, then verify every
    tagged local resource hashes to its integrity value. Hard-fail the release on any mismatch."""
    if _sri is None:
        print("SRI GATE FAIL (sri_integrity module unavailable) -> NOT promoting"); sys.exit(1)
    man = _sri.gen_sri(root)
    changed = _sri.inject_integrity(root)
    checked, fails = _sri.verify_integrity(root)
    print("[sri%s] manifest=%d html_changed=%d injected_tags=%d verified=%d fails=%d"
          % (label, len(man), len(changed), sum(n for _, n in changed), checked, len(fails)))
    if fails:
        for f in fails[:20]: print("   SRI FAIL", f)
        print("SRI GATE FAIL -> NOT promoting"); sys.exit(1)

def readv(root): return json.load(open(os.path.join(root, "js/ver.json")))["v"]
def setv(root, v):
    io.open(os.path.join(root, "js/ver.json"), "w", encoding="utf-8").write('{"v": "%s"}\n' % v)
def relabel(root, v):
    for f in ("app_1.js", "app_2.js", "app_3.js"):
        p = os.path.join(root, "js", f)
        t = io.open(p, encoding="utf-8").read()
        t = re.sub(r'window\.LDBUILD="%s";' % SEM, 'window.LDBUILD="%s";' % v, t)
        t = re.sub(r'var APPV="%s";' % SEM, 'var APPV="%s";' % v, t)
        io.open(p, "w", encoding="utf-8").write(t)
    for hp in glob.glob(os.path.join(root, "**/*.html"), recursive=True):
        hs = io.open(hp, encoding="utf-8").read()
        hs2 = re.sub(r'\?v=%s' % SEM, '?v=%s' % v, hs)
        if hs2 != hs: io.open(hp, "w", encoding="utf-8").write(hs2)
    sp = os.path.join(root, "sw.js")
    if os.path.exists(sp):
        st = io.open(sp, encoding="utf-8").read()
        st2 = re.sub(r'(const CACHE\s*=\s*")lightdao-v[\d.]*(")',
                     lambda mm: mm.group(1) + "lightdao-v" + v.replace(".", "") + mm.group(2), st)
        if st2 != st: io.open(sp, "w", encoding="utf-8").write(st2)
    setv(root, v)

def run(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=e)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def main():
    args = sys.argv[1:]
    if "--rollback" in args:
        if not os.path.isdir(PREV): print("no prev snapshot"); sys.exit(1)
        pv = open(os.path.join(PREV, "VERSION")).read().strip()
        for f in glob.glob(os.path.join(PREV, "*.js")): shutil.copy(f, os.path.join(MAIN, "js", os.path.basename(f)))
        relabel(MAIN, pv)
        maintain_sri(MAIN, " rollback")
        print("ROLLED BACK main to", pv); return
    if len(args) < 2: print(__doc__); sys.exit(2)
    src, nxt = args[0], args[1]; apply = "--apply" in args
    cur = readv(MAIN)
    # build staging from CANDIDATE source
    if os.path.exists(STG): shutil.rmtree(STG)
    shutil.copytree(src, STG)
    relabel(STG, nxt)
    maintain_sri(STG, " staging")
    print("staging built: candidate=%s as v%s (main cur=%s)" % (src, nxt, cur))
    env = {"LD_WEB_ROOT": STG, "LD_PORT": "8093"}
    gates = [("qa_site", ["python3", "/home/ubuntu/qa_site.py"]),
             ("qa_extra", ["python3", "/home/ubuntu/qa_extra.py"]),
             ("site_audit", ["python3", "/home/ubuntu/site_audit.py"]),
             ("qa_truth", ["python3", "/home/ubuntu/qa_truth.py", "8093"]),
             ("g10_root_parity", ["python3", "/usr/local/bin/g10_root_parity_check.py"]),
             ("g1_i18n", ["python3", "/usr/local/bin/g1_i18n_lint.py", STG]),
             ("g2_a11y", ["python3", "/usr/local/bin/g2_a11y_check.py", STG]),
             ("g3_weight", ["python3", "/usr/local/bin/g3_weight_check.py", STG]),
             ("g4_sw", ["python3", "/usr/local/bin/g4_sw_check.py", STG]),
             ("g7_fuzz", ["python3", "/usr/local/bin/g7_fuzz_check.py"]),
             ("g9_day_atomic", ["python3", "/usr/local/bin/g9_day_atomic_check.py"])]
    for name, cmd in gates:
        rc, out = run(cmd, env)
        last = [l for l in out.strip().splitlines() if l.strip()][-3:]
        print("[%s] rc=%d | %s" % (name, rc, " / ".join(last)))
        if rc != 0:
            print("STAGING GATE FAIL (%s) -> NOT promoting" % name); sys.exit(1)
    print("STAGING GATE PASS (v%s)" % nxt)
    if not apply:
        print("(dry-run; pass --apply to promote)"); return
    # snapshot prev for rollback + permanent versioned archive (G-fix 10-10:
    # N1 rewrite had lost html sync + archive -> 1.3.0-class regression restored)
    if os.path.exists(PREV): shutil.rmtree(PREV)
    os.makedirs(PREV)
    for f in glob.glob(os.path.join(MAIN, "js", "*.js")): shutil.copy(f, PREV)
    for f in glob.glob(os.path.join(MAIN, "*.html")): shutil.copy(f, PREV)
    io.open(os.path.join(PREV, "VERSION"), "w").write(cur)
    ARCH = "/var/www/lightdao_js_archive"
    os.makedirs(ARCH, exist_ok=True)
    av = os.path.join(ARCH, cur)
    if not os.path.isdir(av):
        os.makedirs(av)
        for f in glob.glob(os.path.join(MAIN, "js", "*.js")): shutil.copy(f, av)
        for f in glob.glob(os.path.join(MAIN, "*.html")): shutil.copy(f, av)
        io.open(os.path.join(av, "VERSION"), "w").write(cur)
    # promote candidate -> main: js + top-level html + locale SEO shells (one level deep)
    for f in glob.glob(os.path.join(STG, "js", "*.js")): shutil.copy(f, os.path.join(MAIN, "js", os.path.basename(f)))
    for f in glob.glob(os.path.join(STG, "*.html")): shutil.copy(f, os.path.join(MAIN, os.path.basename(f)))
    for f in glob.glob(os.path.join(STG, "*", "index.html")): shutil.copy(f, os.path.join(MAIN, os.path.relpath(f, STG)))
    if os.path.exists(os.path.join(STG, "sw.js")): shutil.copy(os.path.join(STG, "sw.js"), os.path.join(MAIN, "sw.js"))

    # LD-APPLY-ASSET-SYNC-20261015: HTML 引用的本地资源必须跟着 HTML 一起上线。promote 过去只同步 js/*.js、*.html、sw.js，
    # css/ 以及任何新引入的本地资源都会被漏掉，而 staging 是全树 copytree，所以门禁在 staging
    # 全绿、到主站才 404。这里按"页面实际引用什么"来同步，不再靠记住目录清单。
    import re as _re_sync
    refs = set()
    for hp in glob.glob(os.path.join(MAIN, "**", "*.html"), recursive=True):
        for r in _re_sync.findall(r'(?:src|href)="(/[^"?#]+)', io.open(hp, encoding="utf-8", errors="ignore").read()):
            refs.add(r)
    copied_assets, still_missing = [], []
    for r in sorted(refs):
        dst = os.path.join(MAIN, r.lstrip("/"))
        # LD-APPLY-ASSET-SYNC-V2: 内容变了也要同步。只判断"存不存在"会让第二次及以后的 css/资源改动永远不上线。
        if os.path.exists(dst):
            try:
                if io.open(dst, "rb").read() == io.open(os.path.join(STG, r.lstrip("/")), "rb").read():
                    continue
            except Exception:
                continue
        ssrc = os.path.join(STG, r.lstrip("/"))
        if os.path.isfile(ssrc):  # 覆盖式同步（含内容变更）
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(ssrc, dst)
            copied_assets.append(r)
        else:
            still_missing.append(r)
    if copied_assets:
        print("[asset-sync] 补同步 " + str(len(copied_assets)) + " 个引用资源: " + ", ".join(copied_assets[:8]))
    if still_missing:
        # 只警告不阻断：历史遗留引用（例如未提供的图标）不该让一次发布卡死；
        # 真正要紧的本地资源随后会被 SRI 门禁拦下（它会为本地资源注入并校验 integrity）。
        print("[asset-sync] WARN 以下引用在主站与 staging 都不存在: " + ", ".join(still_missing[:8]))
    relabel(MAIN, nxt)
    maintain_sri(MAIN, " main")
    print("PROMOTED main %s -> %s (prev snapshot=%s)" % (cur, nxt, PREV))

if __name__ == "__main__":
    main()
