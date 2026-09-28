#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_lock.py - SEC-LOCK gate (wallet unlock password + WebAuthn PRF biometric + step-up).

Single-reader headless-CDP pattern, same as qa_truth.py: one browser websocket,
targets created/attached/closed serially, never concurrently.

Usage:  qa_lock.py [PORT]        # PORT=443 (default, main) or 8093 (staging)

Assertions
  static   : lock.js served + loaded before app_2.js, governance.html loads it,
             schema/KDF params present, no plaintext-seed writer left, claim stays ungated
  profile A: onboarding mandates password (ack + setup before enter), no-biometric
             profile shows password only, post-onboarding storage has no ld_seed /
             no ld_persist_v1, same-tab reload = no prompt, wrong password fails,
             correct password unlocks, logout keeps lock and re-entry requires unlock,
             step-up blocks a send/delegate until verified then lets it through
  profile B: WeChat UA can set password + unlock + step-up
  profile C: governance vote() is blocked by step-up until verified
  profile D: migration from ld_persist_v1 + plaintext ld_seed -> forced set password
             -> ld_lock_v1 written, ld_seed and ld_persist_v1 DELETED
  profile E: 5 wrong passwords -> 30s cooldown
  profile F: WebAuthn PRF virtual authenticator -> biometric button shown, enrol,
             biometric unlock, biometric step-up
Any FAIL => exit non-zero.
"""
import asyncio, json, re, ssl, sys, urllib.request

import websockets

CDP = "http://127.0.0.1:9222"
PORT = sys.argv[1] if len(sys.argv) > 1 else "443"
ORIGIN = ("https://lightdao.net:" + PORT) if PORT != "443" else "https://lightdao.net"
APP = ORIGIN + "/app.html"
GOV = ORIGIN + "/governance.html"
MNEM = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
PW = "E2E-lock-2026"
BADPW = "wrong-password-9999"
UA_ANDROID = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
UA_WECHAT = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.44(0x28002c33) WeChat/arm64")

R = []


def rec(name, ok, detail=""):
    R.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ((" | " + str(detail)) if detail else ""))


# --------------------------------------------------------------------- static
def https_get(path):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    pre = "https://127.0.0.1:" + PORT
    req = urllib.request.Request(pre + path, headers={"Host": "lightdao.net"})
    return urllib.request.urlopen(req, context=ctx, timeout=20).read().decode("utf-8", "replace")


def static_checks():
    ah = https_get("/app.html")
    gh = https_get("/governance.html")
    lj = https_get("/js/lock.js")
    a2 = https_get("/js/app_2.js")
    a3 = https_get("/js/app_3.js")
    g2 = https_get("/js/governance_2.js")

    ia, i2 = ah.find("/js/lock.js"), ah.find("/js/app_2.js")
    rec("static lock.js referenced in app.html", ia > 0, "idx=%d" % ia)
    rec("static lock.js loaded BEFORE app_2.js", 0 < ia < i2, "lock=%d app2=%d" % (ia, i2))
    rec("static lock.js referenced in governance.html", "/js/lock.js" in gh)
    rec("static lock.js served non-empty", len(lj) > 8000, "%d bytes" % len(lj))
    rec("static ld_lock_v1 schema key", "ld_lock_v1" in lj and "v: 1" in lj)
    rec("static PBKDF2-SHA256 310k", "PBKDF2" in lj and "SHA-256" in lj and "310000" in lj)
    rec("static AES-GCM wrap", lj.count("AES-GCM") >= 3)
    rec("static WebAuthn PRF", "prf" in lj and "isUserVerifyingPlatformAuthenticatorAvailable" in lj)
    rec("static PRF enrol = create()+get() (Chrome releases the secret on assertion)",
        "bioAssert(out.credId" in lj and "res.prf.enabled" in lj)
    rec("static rate limit 5/30s", "MAX_FAILS = 5" in lj and "COOLDOWN_MS = 30000" in lj)
    rec("static LDStepUp exported", "global.LDStepUp" in lj)
    for tok in ("?.", "??", "catch{", ".at(", "replaceAll", "structuredClone", "globalThis"):
        rec("static lock.js ES5-clean no %s" % tok, tok not in lj)

    # plaintext-seed writers must be gone
    rec("static app_2 no lsSet(ld_seed)", 'lsSet("ld_seed"' not in a2)
    rec("static app_2 enter() no persistSet", "persistSet(s)" not in a2)
    rec("static app_2 keeps persistGet for migration", "async function persistGet" in a2)
    rec("static app_2 autoLogin checks ld_lock_v1", "hasLock()" in a2 and "showUnlock()" in a2)
    rec("static app_2 migration forces showSetup", "showSetup(legacy,{migrate:true})" in a2)
    logout_lines = [l for l in a2.splitlines() if "btnLogout" in l and "onclick" in l]
    rec("static app_2 logout clears session only (lock kept)",
        bool(logout_lines) and 'ssDel("ld_session")' in logout_lines[0] and "removeDevice" not in logout_lines[0],
        logout_lines[0][:110] if logout_lines else "btnLogout handler missing")
    rec("static app_2 remove-device control", "btnRemoveDevice" in a2 and 'id="btnRemoveDevice"' in ah)
    rec("static app_2 export gated", "LDStepUp" in a2.split("btnExportSeed")[1][:600])

    # claim must stay frictionless; delegate/send must be gated
    rec("static claim broadcast ungated (frictionless)", 'ldBroadcast(msgs,"auto",null)' in a3)
    claim_seg = a3.split("async claim(day)")[1].split("/* ---- SEC-LOCK")[0]
    stake_seg = a3.split("async claimStaking()")[1].split("async claim(day)")[0]
    rec("static claim() has no step-up", "LDStepUp" not in claim_seg and "ldStepUpOk" not in claim_seg)
    rec("static claimStaking() has no step-up (frictionless)",
        "LDStepUp" not in stake_seg and "ldStepUpOk" not in stake_seg)
    rec("static delegate gated", "MsgDelegate" in a3 and "ldStepUpOk" in a3)
    rec("static bank send gated", "MsgSend" in a3 and "window.LD.sendTokens" in a3)
    rec("static sub-token exchange gated", "window.LD.exchangeSubToken" in a3)
    rec("static gov vote gated", "ldGate(" in g2.split("async function vote")[1][:260])
    rec("static gov propose gated", "ldGate(" in g2.split("btnPropose")[1][:300])
    rec("static gov SSO uses lock", "LDLock" in g2 and "showUnlock" in g2)


# ------------------------------------------------------------------ CDP plumbing
class Page:
    def __init__(self, ws, sid):
        self.ws = ws; self.sid = sid; self.mid = 0; self.errors = []

    async def send(self, method, params=None):
        self.mid += 1
        msg = {"id": self.mid, "method": method, "params": params or {}}
        if self.sid:
            msg["sessionId"] = self.sid
        await self.ws.send(json.dumps(msg))
        while True:
            r = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=60))
            if r.get("method") == "Runtime.exceptionThrown":
                d = r["params"]["exceptionDetails"]
                exc = (d.get("exception") or {}).get("description") or d.get("text", "")
                self.errors.append("exc: " + str(exc).replace("\n", " ")[:140])
            if r.get("id") == self.mid and (self.sid is None or r.get("sessionId") == self.sid):
                if "error" in r:
                    raise RuntimeError(method + " -> " + json.dumps(r["error"])[:200])
                return r.get("result", {})

    async def ev(self, expr, awaitp=False):
        r = await self.send("Runtime.evaluate",
                            {"expression": expr, "returnByValue": True, "awaitPromise": awaitp})
        res = r.get("result", {})
        if res.get("subtype") == "error":
            return "EVAL_ERROR:" + str(res.get("description"))[:160]
        return res.get("value")


async def new_page(ws, ua=None, mobile=True):
    t = await Page(ws, None).send("Target.createTarget", {"url": "about:blank"})
    a = await Page(ws, None).send("Target.attachToTarget", {"targetId": t["targetId"], "flatten": True})
    pg = Page(ws, a["sessionId"])
    await pg.send("Page.enable"); await pg.send("Runtime.enable")
    if ua:
        await pg.send("Emulation.setUserAgentOverride",
                      {"userAgent": ua, "platform": "Android" if "Android" in ua else "iPhone"})
    if mobile:
        await pg.send("Emulation.setDeviceMetricsOverride",
                      {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True})
    return pg, t["targetId"]


async def close_page(ws, pg, tid):
    try:
        await pg.send("WebAuthn.disable")
    except Exception:
        pass
    await Page(ws, None).send("Target.closeTarget", {"targetId": tid})


async def goto(pg, url, wait=4.0):
    await pg.send("Page.navigate", {"url": url})
    await asyncio.sleep(wait)


async def reset_storage(pg, url):
    """Fresh per-profile slate: same browser profile shares origin storage."""
    await goto(pg, url, 2.0)
    await pg.ev("try{localStorage.clear();sessionStorage.clear();}catch(e){} 'cleared'")
    await goto(pg, url, 4.5)


async def wait_for(pg, expr, timeout=30.0, poll=0.3):
    """Poll until expr is truthy. Returns (ok, last_value)."""
    left = timeout
    last = None
    while left > 0:
        last = await pg.ev(expr)
        if last:
            return True, last
        await asyncio.sleep(poll)
        left -= poll
    return False, last


JS = lambda s: json.dumps(s)

MAIN_VISIBLE = '!document.getElementById("sec-main").classList.contains("hide")'
HAS_SETUP = '!!document.getElementById("ldLockSetup")'
HAS_UNLOCK = '!!document.getElementById("ldLockUnlock")'
HAS_STEP = '!!document.getElementById("ldLockStep")'

# Blocks every consensus broadcast *and* the gas-estimation simulation that
# cosmjs performs first, so no test can ever mutate chain state, while still
# recording that signing was reached (i.e. the step-up gate opened).
TX_BLOCK = r"""
(function(){
  if(window.__ldTxInstalled) return 'already';
  window.__ldTxInstalled=true; window.__ldTx=[];
  var F=window.fetch;
  window.fetch=function(u,o){
    try{
      var body=(o&&o.body)?String(o.body):'';
      if(String(u).indexOf('/rpc/')>=0 && (body.indexOf('broadcast_tx')>=0 || body.indexOf('Simulate')>=0)){
        window.__ldTx.push(body.indexOf('broadcast_tx')>=0?'broadcast':'simulate');
        return Promise.resolve(new Response(JSON.stringify({jsonrpc:'2.0',id:null,error:{code:-32000,message:'blocked-by-qa_lock'}}),
          {status:200,headers:{'Content-Type':'application/json'}}));
      }
    }catch(e){}
    return F.apply(this,arguments);
  };
  return 'installed';
})();
"""


async def onboard(pg, label, expect_bio_row=False):
    """Import the test mnemonic and clear the mandatory set-password gate."""
    await pg.ev('document.getElementById("mnem").value=%s; document.getElementById("btnImport").click(); "clicked"' % JS(MNEM))
    ok, _ = await wait_for(pg, HAS_SETUP, 25)
    rec(label + " onboarding shows mandatory set-password overlay", ok)
    if not ok:
        return False
    bio_row = await pg.ev('(function(){var e=document.getElementById("ldLockSetupBioRow");return e?e.style.display:"missing";})()')
    if expect_bio_row:
        rec(label + " biometric option offered when platform authenticator present", bio_row != "none", "display=" + str(bio_row))
    else:
        rec(label + " no-biometric profile shows password only", bio_row == "none", "display=" + str(bio_row))
    seed_shown = await pg.ev('(document.getElementById("ldLockSetupSeed")||{}).textContent||""')
    rec(label + " anti-lockout: seed re-displayed during setup", MNEM.split()[0] in seed_shown and len(seed_shown.strip()) > 40)
    # ack is mandatory
    await pg.ev('(function(){var a=document.getElementById("ldLockSetupPw"),b=document.getElementById("ldLockSetupPw2");a.value=%s;b.value=%s;document.getElementById("ldLockSetupGo").click();return "sent";})()' % (JS(PW), JS(PW)))
    await asyncio.sleep(2.0)
    still = await pg.ev(HAS_SETUP)
    err1 = await pg.ev('(document.getElementById("ldLockSetupErr")||{}).textContent||""')
    rec(label + " setup blocked until seed-backup acknowledged", bool(still) and bool(err1), err1[:60])
    await pg.ev('(function(){document.getElementById("ldLockSetupAck").checked=true;document.getElementById("ldLockSetupGo").click();return "sent";})()')
    ok2, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockSetup') && " + MAIN_VISIBLE + ";})()", 30)
    rec(label + " password set -> wallet entered", ok2)
    return ok2


async def check_storage_clean(pg, label):
    st = await pg.ev("JSON.stringify({lock:localStorage.getItem('ld_lock_v1'),seed:localStorage.getItem('ld_seed'),persist:localStorage.getItem('ld_persist_v1')})")
    d = json.loads(st or "{}")
    rec(label + " ld_lock_v1 written", bool(d.get("lock")))
    rec(label + " NO plaintext ld_seed", d.get("seed") in (None, ""), repr(d.get("seed"))[:40])
    rec(label + " NO legacy ld_persist_v1", d.get("persist") in (None, ""), repr(d.get("persist"))[:40])
    return d.get("lock")


# --------------------------------------------------------------------- profiles
async def profile_a(ws):
    """modern android, no biometric: full behaviour matrix + step-up on send/delegate"""
    pg, tid = await new_page(ws, UA_ANDROID)
    L = "A/android"
    try:
        await reset_storage(pg, APP)
        rec(L + " LDLock + LDStepUp present", await pg.ev("!!(window.LDLock&&window.LDStepUp)"))
        rec(L + " bio capability detection says unavailable",
            (await pg.ev("window.LDLock.bioAvailable()", True)) is False)
        await onboard(pg, L)
        lock = await check_storage_clean(pg, L)
        try:
            r = json.loads(lock or "{}")
            rec(L + " schema {v,salt,iter=310000,wrap_pw,seed_enc}",
                r.get("v") == 1 and bool(r.get("salt")) and r.get("iter") == 310000
                and bool((r.get("wrap_pw") or {}).get("ct")) and bool((r.get("seed_enc") or {}).get("ct")))
            rec(L + " no wrap_bio when biometrics unavailable", not r.get("wrap_bio") and not r.get("bio"))
        except Exception as e:
            rec(L + " schema parse", False, str(e)[:80])

        # same-tab reload -> no prompt
        await goto(pg, APP, 5)
        rec(L + " same-tab reload: no unlock prompt", (await pg.ev(HAS_UNLOCK)) is False)
        rec(L + " same-tab reload: stays logged in", await pg.ev(MAIN_VISIBLE))

        # logout keeps the lock; re-entry requires verification
        await pg.ev('document.getElementById("btnLogout").click(); "x"')
        await asyncio.sleep(5)
        rec(L + " logout keeps ld_lock_v1", await pg.ev("!!localStorage.getItem('ld_lock_v1')"))
        rec(L + " after logout re-entry requires unlock", await pg.ev(HAS_UNLOCK))
        rec(L + " after logout wallet view hidden", not await pg.ev(MAIN_VISIBLE))

        # wrong password fails
        await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(BADPW))
        await asyncio.sleep(3.5)
        e1 = await pg.ev('(document.getElementById("ldLockUnlockErr")||{}).textContent||""')
        rec(L + " wrong password fails unlock", (await pg.ev(HAS_UNLOCK)) and not await pg.ev(MAIN_VISIBLE), e1[:50])
        rec(L + " wrong password shows error", ("密码错误" in e1) or ("Incorrect" in e1), e1[:60])
        # correct password unlocks
        await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(PW))
        ok, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockUnlock') && " + MAIN_VISIBLE + ";})()", 30)
        rec(L + " correct password unlocks", ok)

        # step-up gate on the bank-send / delegate sign path
        okld, _ = await wait_for(pg, "!!(window.LD&&window.LD.sendTokens&&window.LD.delegate)", 25)
        rec(L + " gated sign API exposed", okld)
        await pg.ev(TX_BLOCK)
        await pg.ev("window.__ldP=window.LD.sendTokens('wasm1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq','1')"
                    ".then(function(){return 'broadcast';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        oks, _ = await wait_for(pg, HAS_STEP, 20)
        rec(L + " step-up modal appears before signing", oks)
        bio_btn = await pg.ev('(function(){var e=document.getElementById("ldLockStepBio");return e?e.style.display:"missing";})()')
        rec(L + " step-up hides biometric button when unavailable", bio_btn == "none", "display=" + str(bio_btn))
        await pg.ev('document.getElementById("ldLockStepCancel").click(); "x"')
        await asyncio.sleep(2)
        res1 = await pg.ev("window.__ldP", True)
        n1 = await pg.ev("window.__ldTx.length")
        rec(L + " step-up cancelled => tx aborted, nothing broadcast",
            str(res1).find("step-up-cancelled") >= 0 and (n1 or 0) == 0, "res=%s tx=%s" % (res1, n1))
        # now pass step-up
        await pg.ev("window.__ldTx=[]; window.__ldP2=window.LD.delegate('wasm1valoperqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq','1')"
                    ".then(function(){return 'broadcast';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        oks2, _ = await wait_for(pg, HAS_STEP, 20)
        rec(L + " step-up modal appears for delegate", oks2)
        await pg.ev('(function(){var p=document.getElementById("ldLockStepPw");p.value=%s;document.getElementById("ldLockStepGo").click();return "x";})()' % JS(PW))
        ok2, _ = await wait_for(pg, "(function(){return window.__ldTx && window.__ldTx.length>0;})()", 30)
        res2 = await pg.ev("window.__ldP2", True)
        rec(L + " step-up passed => delegate broadcast attempted", ok2, "res=%s" % res2)
    finally:
        await close_page(ws, pg, tid)


async def profile_wrongpw_stepup(ws):
    """step-up must reject a wrong password and keep the gate closed"""
    pg, tid = await new_page(ws, UA_ANDROID)
    L = "A2/stepup-wrongpw"
    try:
        await reset_storage(pg, APP)
        await onboard(pg, L)
        await pg.ev(TX_BLOCK)
        await pg.ev("window.__ldP=window.LD.sendTokens('wasm1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq','1')"
                    ".then(function(){return 'broadcast';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        await wait_for(pg, HAS_STEP, 20)
        await pg.ev('(function(){var p=document.getElementById("ldLockStepPw");p.value=%s;document.getElementById("ldLockStepGo").click();return "x";})()' % JS(BADPW))
        await asyncio.sleep(3.5)
        rec(L + " wrong password keeps step-up open", await pg.ev(HAS_STEP))
        rec(L + " wrong password => nothing broadcast", (await pg.ev("window.__ldTx.length") or 0) == 0)
        await pg.ev('(function(){var p=document.getElementById("ldLockStepPw");p.value=%s;document.getElementById("ldLockStepGo").click();return "x";})()' % JS(PW))
        ok, _ = await wait_for(pg, "(function(){return window.__ldTx && window.__ldTx.length>0;})()", 30)
        rec(L + " correct password opens the gate", ok)
    finally:
        await close_page(ws, pg, tid)


async def profile_wechat(ws):
    pg, tid = await new_page(ws, UA_WECHAT)
    L = "B/wechat"
    try:
        await reset_storage(pg, APP)
        await onboard(pg, L)
        await check_storage_clean(pg, L)
        await pg.ev('try{sessionStorage.removeItem("ld_session");}catch(e){} "x"')
        await goto(pg, APP, 5)
        rec(L + " new login requires unlock", await pg.ev(HAS_UNLOCK))
        rec(L + " wechat: password-only (no biometric button)",
            (await pg.ev('(function(){var e=document.getElementById("ldLockUnlockBio");return e?e.style.display:"missing";})()')) == "none")
        await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(PW))
        ok, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockUnlock') && " + MAIN_VISIBLE + ";})()", 30)
        rec(L + " wechat: password unlock works", ok)
        await pg.ev(TX_BLOCK)
        await pg.ev("window.__ldP=window.LD.sendTokens('wasm1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq','1')"
                    ".then(function(){return 'broadcast';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        await wait_for(pg, HAS_STEP, 20)
        await pg.ev('(function(){var p=document.getElementById("ldLockStepPw");p.value=%s;document.getElementById("ldLockStepGo").click();return "x";})()' % JS(PW))
        ok2, _ = await wait_for(pg, "(function(){return window.__ldTx && window.__ldTx.length>0;})()", 30)
        rec(L + " wechat: step-up works", ok2)
    finally:
        await close_page(ws, pg, tid)


async def profile_gov(ws):
    """governance vote()/propose() must be step-up gated"""
    pg, tid = await new_page(ws, UA_ANDROID)
    L = "C/governance"
    try:
        await reset_storage(pg, APP)
        await onboard(pg, L)
        await goto(pg, GOV, 8)
        conn = await pg.ev('(document.getElementById("addrLine")||{}).textContent||""')
        rec(L + " SSO reused same-tab session without prompt", "已连接" in conn, conn[:40])
        rec(L + " no unlock prompt when session is live", (await pg.ev(HAS_UNLOCK)) is False)
        await pg.ev(TX_BLOCK)
        await pg.ev("window.__ldV=vote(1,'yes').then(function(){return 'done';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        oks, _ = await wait_for(pg, HAS_STEP, 20)
        rec(L + " vote() raises step-up before client.execute", oks)
        await pg.ev('document.getElementById("ldLockStepCancel").click(); "x"')
        await asyncio.sleep(2.5)
        n1 = await pg.ev("window.__ldTx.length")
        lg = await pg.ev('(document.getElementById("log")||{}).textContent||""')
        rec(L + " vote cancelled => no broadcast", (n1 or 0) == 0, "tx=%s" % n1)
        rec(L + " vote cancelled => user-visible abort message", ("未通过安全验证" in lg) or ("Cancelled" in lg), lg[:60])
        await pg.ev("window.__ldTx=[]; window.__ldV2=vote(1,'yes').then(function(){return 'done';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        await wait_for(pg, HAS_STEP, 20)
        await pg.ev('(function(){var p=document.getElementById("ldLockStepPw");p.value=%s;document.getElementById("ldLockStepGo").click();return "x";})()' % JS(PW))
        ok2, _ = await wait_for(pg, "(function(){return window.__ldTx && window.__ldTx.length>0;})()", 30)
        rec(L + " vote verified => execute proceeds", ok2)
        # propose handler
        await pg.ev("window.__ldTx=[]; document.getElementById('ptitle').value='qa_lock probe'; document.getElementById('pdesc').value='qa_lock probe'; document.getElementById('btnPropose').click(); 'fired'")
        okp, _ = await wait_for(pg, HAS_STEP, 20)
        rec(L + " propose() raises step-up", okp)
        await pg.ev('document.getElementById("ldLockStepCancel").click(); "x"')
        await asyncio.sleep(2.5)
        rec(L + " propose cancelled => no broadcast", (await pg.ev("window.__ldTx.length") or 0) == 0)
    finally:
        await close_page(ws, pg, tid)


async def migrate_case(ws, L, kind):
    """kind='persist': only the legacy device-key blob ld_persist_v1.
       kind='seed'   : only the legacy plaintext ld_seed.
       Both must be intercepted, force a password, and end with ld_lock_v1 only."""
    pg, tid = await new_page(ws, UA_ANDROID)
    try:
        await reset_storage(pg, APP)
        if kind == "persist":
            plant = ("(async function(){try{localStorage.removeItem('ld_seed');"
                     "var r=await persistSet(%s);sessionStorage.removeItem('ld_session');"
                     "return (r&&localStorage.getItem('ld_persist_v1'))?'planted-persist':'plant-failed';"
                     "}catch(e){return 'err:'+e.message;}})()") % JS(MNEM)
        else:
            plant = ("(function(){try{localStorage.removeItem('ld_persist_v1');"
                     "localStorage.setItem('ld_seed',%s);sessionStorage.removeItem('ld_session');"
                     "return localStorage.getItem('ld_seed')?'planted-seed':'plant-failed';"
                     "}catch(e){return 'err:'+String(e);}})()") % JS(MNEM)
        p = await pg.ev(plant, True)
        rec(L + " legacy state planted", str(p).startswith("planted"), p)
        if not str(p).startswith("planted"):
            return None
        await goto(pg, APP, 5)
        ok, _ = await wait_for(pg, HAS_SETUP, 25)
        rec(L + " legacy login intercepted by forced set-password", ok)
        title = await pg.ev('(document.querySelector("#ldLockSetup .ldlock-t")||{}).textContent||""')
        rec(L + " migration overlay is the set-password one",
            ("解锁密码" in title) or ("unlock password" in title.lower()), title[:50])
        rec(L + " wallet NOT entered before a password is set", (await pg.ev(MAIN_VISIBLE)) is False)
        await pg.ev('(function(){document.getElementById("ldLockSetupAck").checked=true;'
                    'var a=document.getElementById("ldLockSetupPw"),b=document.getElementById("ldLockSetupPw2");'
                    'a.value=%s;b.value=%s;document.getElementById("ldLockSetupGo").click();return "x";})()' % (JS(PW), JS(PW)))
        ok2, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockSetup') && " + MAIN_VISIBLE + ";})()", 40)
        rec(L + " migration completes into the wallet", ok2)
        await check_storage_clean(pg, L)
        return await pg.ev("(window.LD&&window.LD.addr)||''")
    finally:
        await close_page(ws, pg, tid)


async def profile_migration(ws):
    a1 = await migrate_case(ws, "D1/migrate-persist", "persist")
    a2 = await migrate_case(ws, "D2/migrate-plaintext-seed", "seed")
    rec("D/migration both legacy paths restore the same wallet",
        bool(a1) and a1 == a2, "%s vs %s" % (str(a1)[:22], str(a2)[:22]))


async def profile_ratelimit(ws):
    pg, tid = await new_page(ws, UA_ANDROID)
    L = "E/ratelimit"
    try:
        await reset_storage(pg, APP)
        await onboard(pg, L)
        await pg.ev('try{sessionStorage.removeItem("ld_session");}catch(e){} "x"')
        await goto(pg, APP, 5)
        rec(L + " unlock overlay shown", await pg.ev(HAS_UNLOCK))
        for i in range(5):
            await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(BADPW))
            await asyncio.sleep(2.6)
        e = await pg.ev('(document.getElementById("ldLockUnlockErr")||{}).textContent||""')
        dis = await pg.ev('(function(){var b=document.getElementById("ldLockUnlockGo");return b?!!b.disabled:null;})()')
        left = await pg.ev("window.LDLock.cooldownLeft()")
        rec(L + " 5 wrong passwords trigger cooldown", ("秒后再试" in e) or ("retry in" in e), e[:70])
        rec(L + " submit disabled during cooldown", dis is True, "disabled=%s" % dis)
        rec(L + " cooldown window ~30s", isinstance(left, int) and 0 < left <= 30, "left=%s" % left)
        rec(L + " still locked during cooldown", not await pg.ev(MAIN_VISIBLE))
        # even the right password is refused while cooling down
        await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(PW))
        await asyncio.sleep(2.5)
        rec(L + " correct password refused during cooldown", await pg.ev(HAS_UNLOCK))
        await pg.ev("try{localStorage.removeItem('ld_lock_rl');}catch(e){} 'cleared'")
    finally:
        await close_page(ws, pg, tid)


async def profile_bio(ws):
    """WebAuthn PRF via a CDP virtual platform authenticator.

    Real devices return a PRF secret and the full biometric round-trip is asserted.
    Chromium's virtual authenticator may only report prf:{enabled:true} without
    releasing a secret; in that case the spec's degradation contract is asserted
    instead (password-only lock, biometric UI hidden, user never locked out)."""
    pg, tid = await new_page(ws, UA_ANDROID)
    L = "F/biometric"
    aid = None
    try:
        await reset_storage(pg, APP)
        await pg.send("WebAuthn.enable")
        r = await pg.send("WebAuthn.addVirtualAuthenticator", {"options": {
            "protocol": "ctap2", "transport": "internal", "hasResidentKey": True,
            "hasUserVerification": True, "isUserVerified": True, "supportsPrf": True,
            "automaticPresenceSimulation": True}})
        aid = r.get("authenticatorId")
        rec(L + " virtual platform authenticator added (PRF)", bool(aid), str(aid)[:20])
        avail = await pg.ev("window.LDLock.bioAvailable()", True)
        rec(L + " capability detection reports biometrics available", avail is True, repr(avail))

        # direct API probe: gives the exact enrol outcome for diagnostics
        api = await pg.ev("(async function(){var r=await window.LDLock.set(%s,%s,true);window.LDLock.removeDevice();return JSON.stringify(r);})()"
                          % (JS(MNEM), JS(PW)), True)
        try:
            apij = json.loads(api or "{}")
        except Exception:
            apij = {}
        prf_released = bool(apij.get("bio"))
        rec(L + " PRF enrol returns a usable secret or a safe note",
            prf_released or apij.get("ok") is True, str(apij)[:90])

        await pg.ev('document.getElementById("mnem").value=%s; document.getElementById("btnImport").click(); "clicked"' % JS(MNEM))
        ok, _ = await wait_for(pg, HAS_SETUP, 25)
        rec(L + " setup overlay shown", ok)
        row = await pg.ev('(function(){var e=document.getElementById("ldLockSetupBioRow");return e?e.style.display:"missing";})()')
        rec(L + " biometric option visible when a platform authenticator exists",
            row != "none" and row != "missing", "display=" + str(row))
        await pg.ev('(function(){document.getElementById("ldLockSetupAck").checked=true;'
                    'document.getElementById("ldLockSetupBio").checked=true;'
                    'var a=document.getElementById("ldLockSetupPw"),b=document.getElementById("ldLockSetupPw2");'
                    'a.value=%s;b.value=%s;document.getElementById("ldLockSetupGo").click();return "x";})()' % (JS(PW), JS(PW)))
        ok2, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockSetup') && " + MAIN_VISIBLE + ";})()", 45)
        rec(L + " enrol flow completes into the wallet", ok2)
        lock = await pg.ev("localStorage.getItem('ld_lock_v1')")
        try:
            j = json.loads(lock or "{}")
        except Exception:
            j = {}
        has_bio = bool(j.get("wrap_bio")) and bool((j.get("bio") or {}).get("credId"))
        await check_storage_clean(pg, L)

        if not has_bio:
            # degradation contract: password-only, no half-written bio record, no lockout
            rec(L + " degraded to password-only lock (no broken wrap_bio)", bool(j.get("wrap_pw")) and not j.get("wrap_bio"))
            await pg.ev('try{sessionStorage.removeItem("ld_session");window.LDLock.forgetSession();}catch(e){} "x"')
            await goto(pg, APP, 5)
            await wait_for(pg, HAS_UNLOCK, 20)
            bb = await pg.ev('(function(){var e=document.getElementById("ldLockUnlockBio");return e?e.style.display:"missing";})()')
            rec(L + " biometric button hidden when no PRF was enrolled", bb == "none", "display=" + str(bb))
            await pg.ev('(function(){var p=document.getElementById("ldLockUnlockPw");p.value=%s;document.getElementById("ldLockUnlockGo").click();return "x";})()' % JS(PW))
            okp, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockUnlock') && " + MAIN_VISIBLE + ";})()", 30)
            rec(L + " password unlock still works after degradation", okp)
            print("NOTE " + L + " authenticator released no PRF secret (%s); asserted the"
                  " password-only degradation contract instead of the bio round-trip" % str(apij)[:70])
            return

        rec(L + " wrap_bio + bio.credId persisted", True)
        # biometric unlock
        await pg.ev('try{sessionStorage.removeItem("ld_session");window.LDLock.forgetSession();}catch(e){} "x"')
        await goto(pg, APP, 5)
        oku, _ = await wait_for(pg, HAS_UNLOCK, 20)
        rec(L + " unlock overlay shown", oku)
        bb = await pg.ev('(function(){var e=document.getElementById("ldLockUnlockBio");return e?e.style.display:"missing";})()')
        rec(L + " biometric unlock button visible", bb != "none" and bb != "missing", "display=" + str(bb))
        await pg.ev('document.getElementById("ldLockUnlockBio").click(); "x"')
        ok3, _ = await wait_for(pg, "(function(){return !document.getElementById('ldLockUnlock') && " + MAIN_VISIBLE + ";})()", 45)
        rec(L + " biometric unwrap unlocks the wallet", ok3)
        # biometric step-up
        await pg.ev(TX_BLOCK)
        await pg.ev("window.__ldP=window.LD.sendTokens('wasm1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq','1')"
                    ".then(function(){return 'broadcast';}).catch(function(e){return 'err:'+String(e.message||e);}); 'fired'")
        await wait_for(pg, HAS_STEP, 20)
        sb = await pg.ev('(function(){var e=document.getElementById("ldLockStepBio");return e?e.style.display:"missing";})()')
        rec(L + " step-up offers biometrics when enrolled", sb != "none" and sb != "missing", "display=" + str(sb))
        await pg.ev('document.getElementById("ldLockStepBio").click(); "x"')
        ok4, _ = await wait_for(pg, "(function(){return window.__ldTx && window.__ldTx.length>0;})()", 45)
        rec(L + " biometric proof opens the step-up gate", ok4)
        await pg.ev('try{window.LDLock.removeDevice();}catch(e){} "x"')
    finally:
        try:
            if aid:
                await pg.send("WebAuthn.removeVirtualAuthenticator", {"authenticatorId": aid})
        except Exception:
            pass
        await close_page(ws, pg, tid)


async def browser_checks():
    ver = json.load(urllib.request.urlopen(CDP + "/json/version"))
    async with websockets.connect(ver["webSocketDebuggerUrl"], max_size=20 * 1024 * 1024) as ws:
        await profile_a(ws)
        await profile_wrongpw_stepup(ws)
        await profile_wechat(ws)
        await profile_gov(ws)
        await profile_migration(ws)
        await profile_ratelimit(ws)
        await profile_bio(ws)
        # leave the shared browser profile clean for the other gates
        pg, tid = await new_page(ws, UA_ANDROID)
        try:
            await goto(pg, APP, 2)
            await pg.ev("try{localStorage.clear();sessionStorage.clear();}catch(e){} 'cleaned'")
        finally:
            await close_page(ws, pg, tid)


static_checks()
asyncio.run(browser_checks())
fails = [r for r in R if not r[1]]
print("LOCK-MATRIX checks: %d  FAILS: %d" % (len(R), len(fails)))
for f in fails:
    print("  FAILED: " + f[0])
sys.exit(1 if fails else 0)
