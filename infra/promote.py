#!/usr/bin/env python3
"""promote.py — 灰度发布: 新构建先只进 staging(:8093), 跑 qa_truth 门, 通过才 promote 到主站。
用法: promote.py [NEXT] [--apply]
  无 --apply: 建 staging(候选=NEXT) + 跑门, 不改动主站。
  有 --apply: 门通过后把候选 js/版本 推到主站。"""
import io, os, re, glob, json, shutil, subprocess, sys

MAIN = "/var/www/lightdao"; STG = "/var/www/lightdao_staging"
args = [a for a in sys.argv[1:]]
apply = "--apply" in args
nums = [a for a in args if a.isdigit()]
cur = json.load(open(os.path.join(MAIN, "js/ver.json")))["v"]
NEXT = int(nums[0]) if nums else cur + 1

# build staging = copy of main, candidate labels = NEXT
if os.path.exists(STG): shutil.rmtree(STG)
shutil.copytree(MAIN, STG)
for f in ("app_1.js", "app_2.js", "app_3.js"):
    p = os.path.join(STG, "js", f)
    t = io.open(p, encoding="utf-8").read()
    t = re.sub(r'window\.LDBUILD="v\d+";', 'window.LDBUILD="v%d";' % NEXT, t)
    io.open(p, "w", encoding="utf-8").write(t)
p1 = os.path.join(STG, "js/app_1.js")
t = io.open(p1, encoding="utf-8").read()
t = re.sub(r'var APPV=\d+;', 'var APPV=%d;' % NEXT, t)
io.open(p1, "w", encoding="utf-8").write(t)
io.open(os.path.join(STG, "js/ver.json"), "w", encoding="utf-8").write('{"v": %d}\n' % NEXT)
for hp in glob.glob(os.path.join(STG, "**/*.html"), recursive=True):
    hs = io.open(hp, encoding="utf-8").read()
    hs2 = re.sub(r'\?v=\d+', '?v=%d' % NEXT, hs)
    if hs2 != hs: io.open(hp, "w", encoding="utf-8").write(hs2)
print("staging built for v%d" % NEXT)

# gate against staging
r = subprocess.run(["python3", "/home/ubuntu/qa_truth.py", "8093"], capture_output=True, text=True, timeout=300)
tail = r.stdout.strip().splitlines()[-6:]
print("\n".join(tail))
if r.returncode != 0:
    print("STAGING GATE FAIL -> NOT promoting"); sys.exit(1)
print("STAGING GATE PASS (v%d)" % NEXT)
if not apply:
    print("(dry-run; pass --apply to promote)"); sys.exit(0)

# promote: candidate js -> main js; bump main html refs + ver.json
for f in glob.glob(os.path.join(STG, "js", "*.js")):
    shutil.copy(f, os.path.join(MAIN, "js", os.path.basename(f)))
for hp in glob.glob(os.path.join(MAIN, "**/*.html"), recursive=True):
    hs = io.open(hp, encoding="utf-8").read()
    hs2 = re.sub(r'\?v=\d+', '?v=%d' % NEXT, hs)
    if hs2 != hs: io.open(hp, "w", encoding="utf-8").write(hs2)
io.open(os.path.join(MAIN, "js/ver.json"), "w", encoding="utf-8").write('{"v": %d}\n' % NEXT)
print("PROMOTED main to v%d" % NEXT)
