#!/usr/bin/env python3
"""promote.py — 灰度发布唯一入口(语义化版本)。
用法:
  promote.py <SOURCE_DIR> <NEXT>            # 建 staging(候选=NEXT) + 跑全部门, 不碰主站
  promote.py <SOURCE_DIR> <NEXT> --apply    # 门全过才把候选推到主站(先快照旧版供回滚)
  promote.py --rollback                     # 回滚到上一次 promote 前的主站 js/版本
SOURCE_DIR = 候选站点根(含 app.html 与 js/), 例如 /home/ubuntu/candidate 或 /var/www/lightdao(自测)。
门 = qa_site + qa_extra + site_audit(对 staging) + qa_truth(浏览器+静态, 对 staging :8093)。
任一失败 => 不 promote, 退出非0。"""
import io, os, re, glob, json, shutil, subprocess, sys

MAIN = "/var/www/lightdao"; STG = "/var/www/lightdao_staging"; PREV = "/var/www/lightdao_js_prev"
SEM = r"[\d]+\.[\d]+\.[\d]+"

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
        print("ROLLED BACK main to", pv); return
    if len(args) < 2: print(__doc__); sys.exit(2)
    src, nxt = args[0], args[1]; apply = "--apply" in args
    cur = readv(MAIN)
    # build staging from CANDIDATE source
    if os.path.exists(STG): shutil.rmtree(STG)
    shutil.copytree(src, STG)
    relabel(STG, nxt)
    print("staging built: candidate=%s as v%s (main cur=%s)" % (src, nxt, cur))
    env = {"LD_WEB_ROOT": STG, "LD_PORT": "8093"}
    gates = [("qa_site", ["python3", "/home/ubuntu/qa_site.py"]),
             ("qa_extra", ["python3", "/home/ubuntu/qa_extra.py"]),
             ("site_audit", ["python3", "/home/ubuntu/site_audit.py"]),
             ("qa_truth", ["python3", "/home/ubuntu/qa_truth.py", "8093"])]
    for name, cmd in gates:
        rc, out = run(cmd, env)
        last = [l for l in out.strip().splitlines() if l.strip()][-3:]
        print("[%s] rc=%d | %s" % (name, rc, " / ".join(last)))
        if rc != 0:
            print("STAGING GATE FAIL (%s) -> NOT promoting" % name); sys.exit(1)
    print("STAGING GATE PASS (v%s)" % nxt)
    if not apply:
        print("(dry-run; pass --apply to promote)"); return
    # snapshot prev for rollback
    if os.path.exists(PREV): shutil.rmtree(PREV)
    os.makedirs(PREV)
    for f in glob.glob(os.path.join(MAIN, "js", "*.js")): shutil.copy(f, PREV)
    io.open(os.path.join(PREV, "VERSION"), "w").write(cur)
    # promote candidate -> main
    for f in glob.glob(os.path.join(STG, "js", "*.js")): shutil.copy(f, os.path.join(MAIN, "js", os.path.basename(f)))
    relabel(MAIN, nxt)
    print("PROMOTED main %s -> %s (prev snapshot=%s)" % (cur, nxt, PREV))

if __name__ == "__main__":
    main()
