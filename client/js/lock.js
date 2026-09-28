/* =====================================================================
 * lock.js - LightDAO wallet unlock + sensitive-action step-up (SEC-LOCK v1)
 *
 * Storage record  localStorage["ld_lock_v1"] =
 *   { v:1, salt:b64, iter:310000, wrap_pw:{iv,ct}, wrap_bio:{iv,ct}?,
 *     bio:{credId,salt}?, seed_enc:{iv,ct} }
 *
 *   DEK        = 256-bit random data key (never persisted)
 *   seed_enc   = AES-GCM(DEK, mnemonic)
 *   wrap_pw    = AES-GCM(PBKDF2-SHA256(password, salt, 310000), DEK)
 *   wrap_bio   = AES-GCM(HKDF-SHA256(WebAuthn PRF secret, bioSalt), DEK)
 *
 * Unlock = unwrap DEK by either path, then decrypt the mnemonic.
 * Proof-of-knowledge for step-up is exactly "successfully unwrapped DEK".
 * Nothing (password, hash, key) ever leaves the browser.
 *
 * Classic script, strict ES5 syntax only (no arrow functions, no let/const,
 * no template literals, no async/await, none of the modern built-ins that
 * qa_extra rejects). Loaded BEFORE app_2.js. No external dependencies.
 * ===================================================================== */
(function (global) {
  "use strict";

  var LS_LOCK = "ld_lock_v1";
  var LS_RL = "ld_lock_rl";
  var LS_LEGACY_SEED = "ld_seed";
  var LS_LEGACY_PERSIST = "ld_persist_v1";
  var SS_SESSION = "ld_session";
  var ITER = 310000;
  var MIN_PW = 8;
  var MAX_FAILS = 5;
  var COOLDOWN_MS = 30000;
  var HKDF_INFO = "ld-lock-bio-v1";

  var memSeed = null;      /* unlocked mnemonic, memory only, never persisted */
  var memOnly = false;     /* true when storage refused the record (private mode) */
  var openMask = null;     /* one overlay at a time */

  /* ---------------------------------------------------------- storage --- */
  function lsGet(k) { try { return global.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { global.localStorage.setItem(k, v); return true; } catch (e) { return false; } }
  function lsDel(k) { try { global.localStorage.removeItem(k); } catch (e) { return false; } }
  function ssDel(k) { try { global.sessionStorage.removeItem(k); } catch (e) { return false; } }

  function readRec() {
    var raw = lsGet(LS_LOCK);
    if (!raw) { return null; }
    try { var o = JSON.parse(raw); if (o && o.wrap_pw && o.seed_enc) { return o; } } catch (e) { return null; }
    return null;
  }
  function writeRec(o) { return lsSet(LS_LOCK, JSON.stringify(o)); }

  /* ------------------------------------------------------------- bytes --- */
  function rand(n) { var u = new Uint8Array(n); global.crypto.getRandomValues(u); return u; }
  function b64enc(u8) {
    var s = "";
    for (var i = 0; i < u8.length; i++) { s += String.fromCharCode(u8[i]); }
    return global.btoa(s);
  }
  function b64dec(str) {
    var bin = global.atob(str);
    var u8 = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) { u8[i] = bin.charCodeAt(i); }
    return u8;
  }
  function b64uEnc(u8) {
    return b64enc(u8).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function b64uDec(str) {
    var pad = str.replace(/-/g, "+").replace(/_/g, "/");
    while (pad.length % 4 !== 0) { pad += "="; }
    return b64dec(pad);
  }
  function utf8(s) { return new TextEncoder().encode(s); }
  function unutf8(u8) { return new TextDecoder().decode(u8); }
  function ab(u8) { return u8.buffer.slice(u8.byteOffset, u8.byteOffset + u8.byteLength); }

  /* ------------------------------------------------------------ crypto --- */
  function cryptoOk() { return !!(global.crypto && global.crypto.subtle); }

  function importAes(rawBytes) {
    return global.crypto.subtle.importKey("raw", rawBytes, "AES-GCM", false, ["encrypt", "decrypt"]);
  }
  function aesEnc(key, bytes) {
    var iv = rand(12);
    return global.crypto.subtle.encrypt({ name: "AES-GCM", iv: iv }, key, bytes).then(function (ct) {
      return { iv: b64enc(iv), ct: b64enc(new Uint8Array(ct)) };
    });
  }
  function aesDec(key, box) {
    return global.crypto.subtle.decrypt({ name: "AES-GCM", iv: b64dec(box.iv) }, key, b64dec(box.ct))
      .then(function (pt) { return new Uint8Array(pt); });
  }
  function pwKey(password, saltBytes, iter) {
    return global.crypto.subtle.importKey("raw", utf8(password), "PBKDF2", false, ["deriveKey"])
      .then(function (base) {
        return global.crypto.subtle.deriveKey(
          { name: "PBKDF2", salt: saltBytes, iterations: iter, hash: "SHA-256" },
          base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
      });
  }
  function bioKey(prfSecret, saltBytes) {
    return global.crypto.subtle.importKey("raw", prfSecret, "HKDF", false, ["deriveKey"])
      .then(function (base) {
        return global.crypto.subtle.deriveKey(
          { name: "HKDF", hash: "SHA-256", salt: saltBytes, info: utf8(HKDF_INFO) },
          base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
      });
  }

  /* --------------------------------------------------------- WebAuthn --- */
  function rpId() { try { return global.location.hostname; } catch (e) { return "localhost"; } }

  function bioSupported() {
    if (!global.navigator || !global.navigator.credentials) { return false; }
    if (typeof global.PublicKeyCredential === "undefined") { return false; }
    if (typeof global.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable !== "function") { return false; }
    return true;
  }
  /* capability detection: WeChat/QQ/old kernels resolve false -> button hidden */
  function bioAvailable() {
    if (!bioSupported()) { return Promise.resolve(false); }
    if (!cryptoOk()) { return Promise.resolve(false); }
    return global.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
      .then(function (v) { return !!v; })
      .catch(function () { return false; });
  }
  function prfExt(saltBytes) { return { prf: { eval: { first: ab(saltBytes) } } }; }

  function bioEnroll(saltBytes) {
    var opts = { publicKey: {
      challenge: rand(32),
      rp: { name: "LightDAO", id: rpId() },
      user: { id: rand(16), name: "lightdao-lock", displayName: "LightDAO Unlock" },
      pubKeyCredParams: [{ type: "public-key", alg: -7 }, { type: "public-key", alg: -257 }],
      authenticatorSelection: { authenticatorAttachment: "platform", userVerification: "required", residentKey: "preferred" },
      timeout: 60000,
      attestation: "none",
      extensions: prfExt(saltBytes)
    } };
    return global.navigator.credentials.create(opts).then(function (cred) {
      var out = { credId: b64uEnc(new Uint8Array(cred.rawId)), prf: null };
      var enabled = false;
      try {
        var res = cred.getClientExtensionResults ? cred.getClientExtensionResults() : null;
        if (res && res.prf) {
          if (res.prf.first) { out.prf = new Uint8Array(res.prf.first); }
          enabled = (res.prf.enabled === true) || !!res.prf.first;
        }
      } catch (e) { enabled = false; }
      /* Chrome reports prf:{enabled:true} at registration but only releases the
       * PRF secret on an assertion, so enrol = create() then one get() using the
       * same salt. Browsers that do return prf.first at create are handled too.
       * No PRF at all -> caller degrades to a password-only lock (never locks the
       * user out). */
      if (out.prf || !enabled) { return out; }
      return bioAssert(out.credId, saltBytes).then(function (prf) { out.prf = prf; return out; });
    });
  }
  function bioAssert(credIdB64u, saltBytes) {
    var opts = { publicKey: {
      challenge: rand(32),
      rpId: rpId(),
      allowCredentials: [{ type: "public-key", id: b64uDec(credIdB64u), transports: ["internal", "platform"] }],
      userVerification: "required",
      timeout: 60000,
      extensions: prfExt(saltBytes)
    } };
    return global.navigator.credentials.get(opts).then(function (asr) {
      var prf = null;
      try {
        var res = asr.getClientExtensionResults ? asr.getClientExtensionResults() : null;
        if (res && res.prf && res.prf.first) { prf = new Uint8Array(res.prf.first); }
      } catch (e) { prf = null; }
      return prf;
    });
  }

  /* ------------------------------------------------------- rate limiting - */
  function rlRead() {
    try { var o = JSON.parse(lsGet(LS_RL) || "null"); if (o) { return o; } } catch (e) { return { f: 0, u: 0 }; }
    return { f: 0, u: 0 };
  }
  function rlWrite(o) { lsSet(LS_RL, JSON.stringify(o)); }
  function cooldownLeft() {
    var o = rlRead();
    var now = Date.now();
    if (o.u && o.u > now) { return Math.ceil((o.u - now) / 1000); }
    return 0;
  }
  function bumpFail() {
    var o = rlRead();
    o.f = (o.f || 0) + 1;
    if (o.f >= MAX_FAILS) { o.f = 0; o.u = Date.now() + COOLDOWN_MS; }
    rlWrite(o);
  }
  function resetFail() { rlWrite({ f: 0, u: 0 }); }

  /* -------------------------------------------------------- legacy kill -- */
  /* Spec: plaintext ld_seed and the device-key blob ld_persist_v1 must never
   * survive once ld_lock_v1 exists (and ld_seed is deleted on every path). */
  function killLegacy() {
    lsDel(LS_LEGACY_SEED);
    lsDel(LS_LEGACY_PERSIST);
  }

  /* --------------------------------------------------------- set / unlock */
  function setLock(mnemonic, password, useBio) {
    if (!cryptoOk()) { return Promise.resolve({ ok: false, err: "webcrypto-unavailable" }); }
    if (!password || password.length < MIN_PW) { return Promise.resolve({ ok: false, err: "pw-too-short" }); }
    if (!mnemonic) { return Promise.resolve({ ok: false, err: "no-seed" }); }

    var dek = rand(32);
    var salt = rand(16);
    var rec = { v: 1, salt: b64enc(salt), iter: ITER, wrap_pw: null, seed_enc: null };
    var finish;

    var p = importAes(dek)
      .then(function (k) { return aesEnc(k, utf8(mnemonic)); })
      .then(function (box) { rec.seed_enc = box; return pwKey(password, salt, ITER); })
      .then(function (kpw) { return aesEnc(kpw, dek); })
      .then(function (box) { rec.wrap_pw = box; return rec; });

    finish = p.then(function () {
      if (!useBio) { return commit(rec, false); }
      var bioSalt = rand(32);
      return bioEnroll(bioSalt).then(function (r) {
        if (!r || !r.prf) { return commit(rec, false, "prf-unavailable"); }
        return bioKey(r.prf, bioSalt).then(function (kb) { return aesEnc(kb, dek); }).then(function (wb) {
          rec.wrap_bio = wb;
          rec.bio = { credId: r.credId, salt: b64enc(bioSalt) };
          return commit(rec, true);
        });
      }).catch(function () { return commit(rec, false, "bio-failed"); });
    });
    return finish.catch(function (e) {
      return { ok: false, err: String((e && e.message) || e || "error") };
    });
  }

  function commit(rec, bioUsed, note) {
    memOnly = !writeRec(rec);
    killLegacy();
    resetFail();
    return { ok: true, bio: !!bioUsed, memOnly: memOnly, note: note || "" };
  }

  function unwrapWith(keyPromise, rec) {
    return keyPromise
      .then(function (k) { return aesDec(k, rec.wrap_pw); })
      .then(function (dek) { return importAes(dek); })
      .then(function (k2) { return aesDec(k2, rec.seed_enc); })
      .then(function (seedBytes) { return unutf8(seedBytes); });
  }

  function unlockPassword(password) {
    var rec = readRec();
    if (!rec) { return Promise.resolve(null); }
    if (cooldownLeft() > 0) { return Promise.resolve(null); }
    return unwrapWith(pwKey(password, b64dec(rec.salt), rec.iter || ITER), rec)
      .then(function (m) { resetFail(); memSeed = m; return m; })
      .catch(function () { bumpFail(); return null; });
  }

  function unlockBio() {
    var rec = readRec();
    if (!rec || !rec.wrap_bio || !rec.bio) { return Promise.resolve(null); }
    if (cooldownLeft() > 0) { return Promise.resolve(null); }
    return bioAssert(rec.bio.credId, b64dec(rec.bio.salt))
      .then(function (prf) {
        if (!prf) { throw new Error("no-prf"); }
        return unwrapWith(bioKey(prf, b64dec(rec.bio.salt)), rec);
      })
      .then(function (m) { resetFail(); memSeed = m; return m; })
      .catch(function () { bumpFail(); return null; });
  }

  function removeDevice() {
    memSeed = null;
    memOnly = false;
    lsDel(LS_LOCK);
    killLegacy();
    ssDel(SS_SESSION);
    resetFail();
  }

  /* --------------------------------------------------------------- UI --- */
  var CSS = ""
    + ".ldlock-mask{position:fixed;left:0;top:0;right:0;bottom:0;z-index:9999;"
    + "background:rgba(5,6,10,.86);display:flex;align-items:center;justify-content:center;padding:18px;"
    + "overflow-y:auto;-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}"
    + ".ldlock-box{width:100%;max-width:430px;box-sizing:border-box;background:#0e1424;border:1px solid #26304a;"
    + "border-radius:14px;padding:18px;color:#eef1f6;font:14px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;"
    + "margin:auto}"
    + ".ldlock-t{font-size:16.5px;font-weight:600;margin:0 0 6px;color:#f4f7fc}"
    + ".ldlock-s{font-size:12.5px;color:#9aa3b2;margin:0 0 12px;line-height:1.7}"
    + ".ldlock-in{width:100%;box-sizing:border-box;padding:11px 12px;border-radius:10px;border:1px solid #2b3752;"
    + "background:#0a0f1c;color:#eef1f6;font-size:15px;margin:0 0 10px}"
    + ".ldlock-in:focus{outline:2px solid #7c8cff;outline-offset:1px}"
    + ".ldlock-btn{display:block;width:100%;box-sizing:border-box;padding:11px 12px;border-radius:10px;border:0;"
    + "background:#7c8cff;color:#08101f;font-size:14.5px;font-weight:600;cursor:pointer;margin:0 0 8px;text-align:center}"
    + ".ldlock-btn2{background:#182238;color:#cdd6e6;border:1px solid #2b3752;font-weight:500}"
    + ".ldlock-btn3{background:transparent;color:#8d97ab;border:0;font-size:12.5px;font-weight:400;text-decoration:underline}"
    + ".ldlock-btn[disabled]{opacity:.5;cursor:default}"
    + ".ldlock-err{color:#ff9a9a;font-size:12.5px;min-height:17px;margin:0 0 8px}"
    + ".ldlock-seed{background:#0a0f1c;border:1px dashed #3d4a6b;border-radius:10px;padding:10px 12px;"
    + "font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13.5px;line-height:1.9;color:#dfe6f2;"
    + "word-break:break-word;margin:0 0 10px}"
    + ".ldlock-lbl{display:flex;gap:8px;align-items:flex-start;font-size:12.5px;color:#c3cbda;margin:0 0 10px;"
    + "cursor:pointer;line-height:1.6}"
    + ".ldlock-lbl input{width:auto;margin:3px 0 0;flex:0 0 auto}"
    + ".ldlock-hint{font-size:11.5px;color:#7f8a9e;margin:8px 0 0;line-height:1.7}"
    + ".ldlock-busy{opacity:.6;pointer-events:none}";

  function ensureCss() {
    if (global.document.getElementById("ldlockCss")) { return; }
    var st = global.document.createElement("style");
    st.id = "ldlockCss";
    st.appendChild(global.document.createTextNode(CSS));
    (global.document.head || global.document.documentElement).appendChild(st);
  }

  function hideAppOverlay() {
    try {
      var ov = global.document.getElementById("loginOverlay");
      if (ov) { ov.style.display = "none"; }
      global.document.documentElement.classList.remove("ld-restoring");
    } catch (e) { /* no overlay on this page */ }
  }

  function mount() {
    ensureCss();
    closeMask();
    hideAppOverlay();
    var m = global.document.createElement("div");
    m.className = "ldlock-mask";
    m.id = "ldLockMask";
    m.setAttribute("role", "dialog");
    m.setAttribute("aria-modal", "true");
    (global.document.body || global.document.documentElement).appendChild(m);
    openMask = m;
    return m;
  }
  function closeMask() {
    try {
      if (openMask && openMask.parentNode) { openMask.parentNode.removeChild(openMask); }
    } catch (e) { /* already gone */ }
    openMask = null;
  }
  function gid(id) { return global.document.getElementById(id); }
  function box(m, html) {
    var b = global.document.createElement("div");
    b.className = "ldlock-box";
    b.innerHTML = html;
    m.appendChild(b);
    return b;
  }
  function notify(msg) {
    try { if (typeof global.toast === "function") { global.toast(msg); } } catch (e) { /* page has no toast */ }
  }
  function setErr(id, msg) { var e = gid(id); if (e) { e.textContent = msg || ""; } }
  function busy(on) {
    if (!openMask) { return; }
    var b = openMask.firstChild;
    if (b) { b.className = on ? "ldlock-box ldlock-busy" : "ldlock-box"; }
  }
  function cooldownText(sec) {
    return "尝试次数过多,请 " + sec + " 秒后再试 / Too many attempts, retry in " + sec + "s";
  }
  function tickCooldown(errId, goId, done) {
    var left = cooldownLeft();
    if (left <= 0) { if (done) { done(); } return; }
    setErr(errId, cooldownText(left));
    var g = gid(goId);
    if (g) { g.disabled = true; }
    global.setTimeout(function () {
      var l2 = cooldownLeft();
      if (l2 > 0) { tickCooldown(errId, goId, done); return; }
      setErr(errId, "");
      var g2 = gid(goId);
      if (g2) { g2.disabled = false; }
      if (done) { done(); }
    }, 1000);
  }

  /* ---- set-password overlay (onboarding + migration + password reset) ---- */
  function showSetup(mnemonic, opts) {
    var o = opts || {};
    return new Promise(function (resolve) {
      if (!cryptoOk()) {
        notify("此浏览器不支持 WebCrypto,无法设置解锁密码 / WebCrypto unavailable");
        resolve(false);
        return;
      }
      bioAvailable().then(function (canBio) {
        var title = o.migrate
          ? "升级为本机解锁密码 / Set your wallet unlock password"
          : "设置钱包解锁密码 / Set wallet unlock password";
        var sub = "密码只留在你的浏览器,用于在本机加密助记词;服务器不保存任何密码或密钥。"
          + " / The password encrypts your seed on this device only; no server ever sees it.";
        var html = ""
          + '<div class="ldlock-t">' + title + "</div>"
          + '<p class="ldlock-s">' + sub + "</p>"
          + '<p class="ldlock-s" style="margin-bottom:6px">请先抄写助记词(唯一离线备份) / Write down your seed phrase first - it is the only offline backup:</p>'
          + '<div class="ldlock-seed" id="ldLockSetupSeed"></div>'
          + '<label class="ldlock-lbl" for="ldLockSetupAck"><input type="checkbox" id="ldLockSetupAck">'
          + "<span>我已把上面 12/24 个单词抄在纸上并妥善保存(忘记密码时只能靠它恢复)"
          + " / I wrote these words down on paper and stored them safely (the only way back if I forget my password)</span></label>"
          + '<input class="ldlock-in" type="password" id="ldLockSetupPw" autocomplete="new-password" '
          + 'placeholder="解锁密码(至少 8 位) / Unlock password (min 8 chars)">'
          + '<input class="ldlock-in" type="password" id="ldLockSetupPw2" autocomplete="new-password" '
          + 'placeholder="再次输入密码 / Repeat password">'
          + '<label class="ldlock-lbl" for="ldLockSetupBio" id="ldLockSetupBioRow" style="display:none">'
          + '<input type="checkbox" id="ldLockSetupBio">'
          + "<span>同时启用本机生物识别解锁(指纹/面容,可选) / Also enable biometric unlock (fingerprint / face, optional)</span></label>"
          + '<div class="ldlock-err" id="ldLockSetupErr"></div>'
          + '<button class="ldlock-btn" type="button" id="ldLockSetupGo">保存并进入钱包 / Save &amp; enter wallet</button>'
          + '<button class="ldlock-btn ldlock-btn2" type="button" id="ldLockSetupCancel">取消 / Cancel</button>'
          + '<p class="ldlock-hint">忘记密码?在登录页用助记词重新导入即可重设密码。'
          + " / Forgot it later? Re-import your seed phrase to set a new password.</p>";
        var m = mount();
        var b = box(m, html);
        b.id = "ldLockSetup";
        var seedEl = gid("ldLockSetupSeed");
        if (seedEl) { seedEl.textContent = String(mnemonic || ""); }
        if (canBio) { var row = gid("ldLockSetupBioRow"); if (row) { row.style.display = ""; } }

        gid("ldLockSetupCancel").onclick = function () { closeMask(); resolve(false); };
        gid("ldLockSetupGo").onclick = function () {
          var ack = gid("ldLockSetupAck");
          var p1 = gid("ldLockSetupPw").value;
          var p2 = gid("ldLockSetupPw2").value;
          if (ack && !ack.checked) { setErr("ldLockSetupErr", "请先确认已抄写助记词 / Confirm you wrote down your seed phrase first"); return; }
          if (!p1 || p1.length < MIN_PW) { setErr("ldLockSetupErr", "密码至少 " + MIN_PW + " 位 / Password must be at least " + MIN_PW + " characters"); return; }
          if (p1 !== p2) { setErr("ldLockSetupErr", "两次输入的密码不一致 / Passwords do not match"); return; }
          setErr("ldLockSetupErr", "");
          busy(true);
          var bio = false;
          var cb = gid("ldLockSetupBio");
          if (cb && cb.checked) { bio = true; }
          setLock(mnemonic, p1, bio).then(function (r) {
            busy(false);
            if (!r || !r.ok) {
              setErr("ldLockSetupErr", "设置失败 / Setup failed: " + String((r && r.err) || "error"));
              return;
            }
            if (bio && !r.bio) { notify("生物识别不可用,已仅用密码保护 / Biometrics unavailable; password-only lock saved"); }
            if (r.memOnly) { notify("本机存储被禁用,解锁信息仅本次会话有效 / Storage blocked; unlock info is session-only"); }
            closeMask();
            resolve(true);
          });
        };
      });
    });
  }

  /* ---------------------------- unlock overlay (new login on this device) - */
  function showUnlock(opts) {
    var o = opts || {};
    return new Promise(function (resolve) {
      var rec = readRec();
      if (!rec) { resolve(false); return; }
      var hasBio = !!(rec.wrap_bio && rec.bio);
      bioAvailable().then(function (canBio) {
        var showBio = hasBio && canBio;
        var html = ""
          + '<div class="ldlock-t">解锁钱包 / Unlock wallet</div>'
          + '<p class="ldlock-s">检测到本机已保存的钱包。请输入解锁密码'
          + (showBio ? "或使用生物识别" : "")
          + "。 / A wallet is saved on this device. Enter your unlock password"
          + (showBio ? " or use biometrics" : "") + ".</p>"
          + '<input class="ldlock-in" type="password" id="ldLockUnlockPw" autocomplete="current-password" '
          + 'placeholder="解锁密码 / Unlock password">'
          + '<div class="ldlock-err" id="ldLockUnlockErr"></div>'
          + '<button class="ldlock-btn" type="button" id="ldLockUnlockGo">解锁 / Unlock</button>'
          + '<button class="ldlock-btn ldlock-btn2" type="button" id="ldLockUnlockBio" style="display:none">'
          + "使用生物识别解锁 / Unlock with biometrics</button>"
          + '<button class="ldlock-btn ldlock-btn3" type="button" id="ldLockUnlockReimport">'
          + "忘记密码?用助记词重新导入 / Forgot it? Re-import seed phrase</button>"
          + '<button class="ldlock-btn ldlock-btn3" type="button" id="ldLockUnlockWipe">'
          + "移除本机登录信息 / Remove this device's login</button>"
          + '<p class="ldlock-hint">同一标签页内刷新不会再次询问。 / Refreshing this same tab will not ask again.</p>';
        var m = mount();
        var b = box(m, html);
        b.id = "ldLockUnlock";
        var pw = gid("ldLockUnlockPw");
        if (showBio) { var bb = gid("ldLockUnlockBio"); if (bb) { bb.style.display = ""; } }

        function fail(msg) {
          busy(false);
          setErr("ldLockUnlockErr", msg);
          tickCooldown("ldLockUnlockErr", "ldLockUnlockGo", null);
        }
        function tryPw() {
          var v = pw.value;
          if (!v) { setErr("ldLockUnlockErr", "请输入密码 / Enter your password"); return; }
          var left = cooldownLeft();
          if (left > 0) { fail(cooldownText(left)); return; }
          busy(true);
          setErr("ldLockUnlockErr", "");
          unlockPassword(v).then(function (seed) {
            if (seed) { closeMask(); resolve(true); return; }
            var l2 = cooldownLeft();
            fail(l2 > 0 ? cooldownText(l2) : "密码错误 / Incorrect password");
          });
        }
        gid("ldLockUnlockGo").onclick = tryPw;
        pw.onkeydown = function (ev) {
          var k = ev && (ev.key || ev.keyCode);
          if (k === "Enter" || k === 13) { tryPw(); }
        };
        gid("ldLockUnlockBio").onclick = function () {
          var left = cooldownLeft();
          if (left > 0) { fail(cooldownText(left)); return; }
          busy(true);
          setErr("ldLockUnlockErr", "");
          unlockBio().then(function (seed) {
            if (seed) { closeMask(); resolve(true); return; }
            var l2 = cooldownLeft();
            fail(l2 > 0 ? cooldownText(l2) : "生物识别失败,请改用密码 / Biometrics failed, use your password");
          });
        };
        gid("ldLockUnlockReimport").onclick = function () {
          closeMask();
          try {
            if (typeof global.showTab === "function") { global.showTab("Imp"); }
            var mi = gid("mnem");
            if (mi) { mi.value = ""; mi.focus(); }
          } catch (e) { /* page without import tab */ }
          notify("请粘贴助记词以重设解锁密码 / Paste your seed phrase to reset the password");
          resolve(false);
        };
        gid("ldLockUnlockWipe").onclick = function () {
          var ok = global.confirm("将删除本机保存的钱包登录信息,之后必须用助记词重新导入。确认?"
            + " / Delete this device's saved login? You will need your seed phrase to log in again.");
          if (!ok) { return; }
          removeDevice();
          closeMask();
          resolve(false);
          try { global.location.reload(); } catch (e) { /* ignore */ }
        };
        tickCooldown("ldLockUnlockErr", "ldLockUnlockGo", null);
        global.setTimeout(function () { try { pw.focus(); } catch (e) { /* ignore */ } }, 60);
      });
    });
  }

  /* --------------------------------------------- step-up for sensitive tx */
  function stepUp(label) {
    return new Promise(function (resolve) {
      var rec = readRec();
      if (!rec) {
        /* No lock on this device (e.g. passkey-only or storage-blocked session):
         * nothing to unwrap, so nothing to prove. Do not break existing flows. */
        resolve(!!memSeed);
        return;
      }
      var hasBio = !!(rec.wrap_bio && rec.bio);
      bioAvailable().then(function (canBio) {
        var showBio = hasBio && canBio;
        var html = ""
          + '<div class="ldlock-t">安全验证 / Security check</div>'
          + '<p class="ldlock-s" id="ldLockStepLabel"></p>'
          + '<input class="ldlock-in" type="password" id="ldLockStepPw" autocomplete="current-password" '
          + 'placeholder="解锁密码 / Unlock password">'
          + '<div class="ldlock-err" id="ldLockStepErr"></div>'
          + '<button class="ldlock-btn" type="button" id="ldLockStepGo">验证并继续 / Verify &amp; continue</button>'
          + '<button class="ldlock-btn ldlock-btn2" type="button" id="ldLockStepBio" style="display:none">'
          + "使用生物识别验证 / Verify with biometrics</button>"
          + '<button class="ldlock-btn ldlock-btn2" type="button" id="ldLockStepCancel">取消 / Cancel</button>';
        var m = mount();
        var b = box(m, html);
        b.id = "ldLockStep";
        var lbl = gid("ldLockStepLabel");
        if (lbl) {
          lbl.textContent = (label || "敏感操作 / Sensitive action")
            + " - 请再次验证身份后才会签名。 / Verify again before this is signed.";
        }
        var pw = gid("ldLockStepPw");
        if (showBio) { var bb = gid("ldLockStepBio"); if (bb) { bb.style.display = ""; } }

        function fail(msg) {
          busy(false);
          setErr("ldLockStepErr", msg);
          tickCooldown("ldLockStepErr", "ldLockStepGo", null);
        }
        function tryPw() {
          var v = pw.value;
          if (!v) { setErr("ldLockStepErr", "请输入密码 / Enter your password"); return; }
          var left = cooldownLeft();
          if (left > 0) { fail(cooldownText(left)); return; }
          busy(true);
          setErr("ldLockStepErr", "");
          unlockPassword(v).then(function (seed) {
            if (seed) { closeMask(); resolve(true); return; }
            var l2 = cooldownLeft();
            fail(l2 > 0 ? cooldownText(l2) : "密码错误 / Incorrect password");
          });
        }
        gid("ldLockStepGo").onclick = tryPw;
        pw.onkeydown = function (ev) {
          var k = ev && (ev.key || ev.keyCode);
          if (k === "Enter" || k === 13) { tryPw(); }
        };
        gid("ldLockStepBio").onclick = function () {
          busy(true);
          setErr("ldLockStepErr", "");
          unlockBio().then(function (seed) {
            if (seed) { closeMask(); resolve(true); return; }
            fail("生物识别失败,请改用密码 / Biometrics failed, use your password");
          });
        };
        gid("ldLockStepCancel").onclick = function () { closeMask(); resolve(false); };
        tickCooldown("ldLockStepErr", "ldLockStepGo", null);
        global.setTimeout(function () { try { pw.focus(); } catch (e) { /* ignore */ } }, 60);
      });
    });
  }

  /* -------------------------------------------------------- public API --- */
  var LDLock = {
    KEY: LS_LOCK,
    ITER: ITER,
    MIN_PW: MIN_PW,
    MAX_FAILS: MAX_FAILS,
    COOLDOWN_MS: COOLDOWN_MS,
    hasLock: function () { return !!readRec(); },
    isUnlocked: function () { return !!memSeed; },
    isLocked: function () { return !!readRec() && !memSeed; },
    currentSeed: function () { return memSeed; },
    memOnly: function () { return memOnly; },
    bioSupported: bioSupported,
    bioAvailable: bioAvailable,
    cooldownLeft: cooldownLeft,
    set: setLock,
    unlockPassword: unlockPassword,
    unlockBio: unlockBio,
    removeDevice: removeDevice,
    killLegacy: killLegacy,
    forgetSession: function () { memSeed = null; },
    showSetup: showSetup,
    showUnlock: showUnlock,
    closeMask: closeMask
  };

  global.LDLock = LDLock;
  global.LDStepUp = function (label) { return stepUp(label); };
})(window);
