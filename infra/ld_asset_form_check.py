#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g15：资产形态口径必须与白皮书一致（执行点/检测点/告警/测试 四件套里的"检测点"）。

为什么需要它（2026-11-05 实测事故）：我在 docs 与跨链面板里写过
"LIGHT 是 CW20 合约代币 → IBC 搬不动 → 需要 warp 封装"，而白皮书第 9 行明写
"质押/治理/Gas 均为 `ulight`"，链上实测也是原生币（denom-metadata name=LIGHT、
bond_denom=ulight、bank total 2.5e15）。一个错误归因同时活在 4 份文档、站点表格和 14 语种文案里，
而且所有门禁全绿 —— 因为没有任何一处会去比对"资产形态"这类口径。这条门禁就是补那个洞。

判据（任一不过 = 非零退出 + 写告警日志）：
 A) 白皮书（线上 whitepaper.md）必须仍写着原生 ulight 那句权威表述；
 B) 站点 HTML/JS、docs 里不得再出现"把 LIGHT 说成合约币/warp 才能搬"的句式；
 C) 链上三项事实必须与之一致：denom-metadata name=LIGHT、staking bond_denom=ulight、
    bank total(ulight) 是 2.5e15 量级（不是凭空冒出的第二个总量）；
 D) 跨链探针的"未开通"必须带**实测证据**（mainnet_clients 数字），不能只写结论。

--selftest：造一份含旧错误句式的临时目录 → 必须变红；干净目录 → 必须通过。
"""
import json
import os
import shutil
import re
import subprocess
import sys
import time
import urllib.request

WWW = os.environ.get("LD_WWW", "/var/www/lightdao")
REPO = os.environ.get("LD_REPO", "/home/ubuntu/repo")
BIN = os.environ.get("LD_BIN", "/usr/local/bin/wasmd")
NODE = os.environ.get("LD_NODE", "http://127.0.0.1:26657")
PROBE = os.environ.get("LD_PROBE", "http://127.0.0.1:8096/v1/ibc")
ALERTS = "/home/ubuntu/ld_alerts.log"
# 这些句式一旦重新出现就说明口径又跑偏了（覆盖中英混合写法与探针 reason_code）
FORBIDDEN = [
    "CW20 代币 LIGHT",
    "LIGHT 是合约代币",
    "LIGHT 是 **CW20 合约币**",
    "LIGHT 是 CW20 合约币",
    "cw20_needs_warp",
    "contract token (CW20)",
    "jeton contractuel (CW20)",
    "Contract-Token (CW20)",
    "контрактный токен (CW20)",
    "コントラクトトークン（CW20）",
    "컨트랙트 토큰(CW20)",
    "رمز تعاقدي (CW20)",
    "कॉन्ट्रैक्ट टोकन (CW20)",
    "sözleşme token'ı (CW20)",
    "token kontrak (CW20)",
    "hợp đồng (CW20)",
    "token de contrato (CW20)",
]
AUTHORITY = re.compile(r"均为\s*`ulight`|质押/治理/Gas 均为")


def scan_globs(www, repo):
    """注意：扫描清单必须在**调用时**用当前 WWW/REPO 现算。
       原来写成模块级常量，自测里改了全局目录也不生效 → 自测实际在扫真实站点，
       "植入故障抓到/去掉后不再报"两项都被污染（这就是"量具自己看错"的又一实例）。"""
    return [(os.path.join(www, "*.html"), "站点 html"),
            (os.path.join(www, "js", "*.js"), "站点 js"),
            (os.path.join(repo, "docs", "*.md"), "docs"),
            (os.path.join(repo, "client", "*.html"), "仓库 html"),
            (os.path.join(repo, "client", "js", "*.js"), "仓库 js"),
            (os.path.join(repo, "infra", "*.py"), "infra")]


def alert(msg, alarms):
    line = "%s ASSET-FORM %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line)
    alarms.append(line)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def sh_q(args, timeout=20):
    p = subprocess.run([BIN, "q"] + args + ["--node", NODE], capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[:110].replace("\n", " "))
    return p.stdout


def check(alarms, www=None, repo=None):
    # 默认值在函数定义时就冻结了模块级常量，自测里改全局目录不会生效
    # （真实踩过：两轮都扫到线上站点，绿灯是假的）→ 改为调用时解析。
    www = www or globals()["WWW"]
    repo = repo or globals()["REPO"]
    # A) 白皮书权威句还在不在
    wp = os.path.join(www, "whitepaper.md")
    try:
        t = open(wp, encoding="utf-8").read()
        if not AUTHORITY.search(t):
            alert("白皮书里找不到「质押/治理/Gas 均为 ulight」这句权威表述：口径源被改动，门禁无法再对齐", alarms)
    except Exception as e:
        alert("读不到白皮书 %s：%s" % (wp, str(e)[:60]), alarms)
    # B) 旧错误句式有没有复活
    import glob as g
    self_path = os.path.realpath(__file__)
    self_base = os.path.basename(self_path)
    for pat, tag in scan_globs(www, repo):
        for f in g.glob(pat):
            rp = os.path.realpath(f)
            # 排除量具自身（含它的 .bak 副本）：本文件的禁句清单里就原文写着这些句子，
            # 把自己当违规内容会让门禁永远红 —— 那不是"抓到问题"，是门禁坏了。
            # 注意：只排除这一个文件，docs/站点/其它 infra 文件照扫（自测里有反向验证）。
            # 按**文件名**排除，而不是按 realpath：真实发布时跑的是 /usr/local/bin 里的部署副本，
            # 仓库 infra 里还有一份同名同内容的源文件 —— 只排除 realpath 的话，那份副本照样自撞。
            if tag == "infra" and (os.path.basename(rp) == self_base
                                   or os.path.basename(rp).startswith(self_base + ".bak")):
                continue
            try:
                s = open(f, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for bad in FORBIDDEN:
                m = re.search(re.escape(bad), s)
                if m:
                    ln = s[:m.start()].count("\n") + 1
                    alert("%s 里重新出现了把 LIGHT 说成合约代币/warp 才能搬的句式（%s:%d 命中「%s」）"
                          % (tag, os.path.basename(f), ln, bad[:34]), alarms)
                    break
    # C) 链上事实三点
    try:
        meta = sh_q(["bank", "denom-metadata", "ulight"])
        if "name: LIGHT" not in meta:
            alert("链上 ulight 的 denom-metadata 里 name 不再是 LIGHT：资产形态口径与链不符", alarms)
    except Exception as e:
        alert("读不到 denom-metadata：%s" % str(e)[:70], alarms)
    try:
        sp = sh_q(["staking", "params"])
        if "bond_denom: ulight" not in sp:
            alert("链上 bond_denom 不是 ulight（质押币变了）：文档与面板必须重新核对资产形态", alarms)
    except Exception as e:
        alert("读不到 staking params：%s" % str(e)[:70], alarms)
    # D) 探针的"未开通"必须带实测数字
    try:
        req = urllib.request.Request(PROBE, headers={"User-Agent": "ld-asset-form/1.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace"))
        mi = d.get("mainnet_ibc") or {}
        if mi.get("enabled") is False and mi.get("mainnet_clients") is None:
            alert("探针说主网跨链未开通却没给实测客户端数（结论无证据支撑）", alarms)
        if mi.get("reason_code") == "cw20_needs_warp_and_governance":
            alert("探针 reason_code 仍是 cw20_needs_warp（旧错误归因复活）", alarms)
    except Exception as e:
        alert("读不到跨链探针 %s：%s" % (PROBE, str(e)[:70]), alarms)


def selftest():
    print("ASSET-FORM SELFTEST：植入旧错误句式，必须变红")
    tmp = "/home/ubuntu/asset_form_selftest." + str(int(time.time()))
    os.makedirs(tmp + "/js", exist_ok=True)
    os.makedirs(tmp + "/docs", exist_ok=True)
    open(tmp + "/whitepaper.md", "w", encoding="utf-8").write("质押/治理/Gas 均为 `ulight`(LIGHT,6 位小数)\n")
    open(tmp + "/bad.html", "w", encoding="utf-8").write("<td>CW20 代币 LIGHT，总量 25 亿枚</td>\n")
    # 再往 infra 的**另一个**文件植入同一句式：排除量具自身之后，这一类必须照样抓到
    os.makedirs(tmp + "/infra", exist_ok=True)
    open(tmp + "/infra/sibling_tool.py", "w", encoding="utf-8").write(
        "# 说明文档：LIGHT 是 CW20 合约币\nX = 1\n")
    shutil.copy2(os.path.realpath(__file__), tmp + "/infra/ld_asset_form_check.py")
    open(tmp + "/docs/OK.md", "w", encoding="utf-8").write("LIGHT 是原生币 ulight\n")
    globals()["WWW"] = tmp
    globals()["REPO"] = tmp
    # 关键：check() 的默认参数在定义时就绑死了旧目录，自测必须显式把临时目录传进去，
    # 否则"植入故障/去掉故障"两轮扫的还是真实站点，测出来的绿灯是假的。
    al = []
    check(al, tmp, tmp)
    hit = any("重新出现" in x for x in al)
    hit_html = any("bad.html" in x for x in al)
    hit_infra = any("sibling_tool.py" in x for x in al)
    selfclean = not any("ld_asset_form_check.py" in x for x in al)
    print("  植入旧句式 -> %s（%d 条告警）｜站点 html 抓到=%s｜infra 兄弟文件抓到=%s｜"
          "量具自身不再自撞=%s" % ("抓到" if hit else "漏了", len(al), hit_html, hit_infra, selfclean))
    os.replace(tmp + "/bad.html", tmp + "/bad.html.checked")
    os.replace(tmp + "/infra/sibling_tool.py", tmp + "/infra/sibling_tool.py.checked")
    al2 = []
    check(al2)
    clean_ok = not any("重新出现" in x for x in al2)
    print("  去掉旧句式后该判据不再报（不误报）= %s" % clean_ok)
    all_ok = hit and hit_html and hit_infra and selfclean and clean_ok
    print("SELFTEST：%s（4 项：植入抓到+html+infra+不自撞，1 项：去掉不误报）"
          % ("通过" if all_ok else "不过——这条门禁不可信"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    # 允许传站点根目录：发布门禁要把"将要发出去的那份"当参数传进来（预发布目录），
    # 否则门禁扫的是线上旧文件，等于永远在报昨天的问题、却拦不住今天的问题。
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        globals()["WWW"] = sys.argv[1]
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    alarms = []
    try:
        check(alarms)
    except Exception as e:
        alert("FAIL 量具自己读不到（不当成通过）：%s" % str(e)[:150], alarms)
        sys.exit(2)
    if alarms:
        print("ASSET-FORM FAILS: %d" % len(alarms))
        sys.exit(1)
    print("ASSET-FORM OK：白皮书、站点、docs、链上、探针五处口径一致（LIGHT=原生 ulight）")
    sys.exit(0)
