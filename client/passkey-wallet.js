/* LightDAO §4.9 Passkey Wallet v1 — seedless UX + Shamir social recovery.
 *
 * Design:
 *  - Daily login: WebAuthn Passkey (biometric). The Passkey's PRF extension derives
 *    a deterministic 32-byte secret -> HKDF -> AES-GCM key that decrypts the BIP39
 *    mnemonic stored (ciphertext-only) in localStorage. The plaintext seed is never
 *    persisted and never shown in normal use.
 *  - Chain signing stays secp256k1 (cosmjs) — the decrypted mnemonic feeds the
 *    existing DirectSecp256k1HdWallet. (Full P-256 on-chain smart-account is a
 *    future increment; this v1 delivers the seedless UX + recovery without it.)
 *  - Fallback: browsers without WebAuthn PRF use a user PIN (PBKDF2-SHA256, 210k
 *    iters) as the key-encryption-key. Passkey still gates access as 2nd factor.
 *  - Social recovery: Shamir Secret Sharing over GF(256), 3-of-5, splits the
 *    mnemonic bytes. Guardians hold shares; any 3 reconstruct the seed.
 *
 * No external deps: Web Crypto (AES-GCM/HKDF/PBKDF2/SHA-256) + WebAuthn + inline Shamir.
 */
(function (global) {
  "use strict";

  // ---------- base64url helpers ----------
  const b64u = {
    enc(buf) {
      const b = new Uint8Array(buf);
      let s = "";
      for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
      return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    },
    dec(str) {
      str = String(str).replace(/-/g, "+").replace(/_/g, "/");
      while (str.length % 4) str += "=";
      const bin = atob(str);
      const out = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
      return out;
    },
  };
  const te = new TextEncoder();
  const td = new TextDecoder();
  const rand = (n) => crypto.getRandomValues(new Uint8Array(n));

  // ================= Shamir Secret Sharing over GF(256) =================
  // Field polynomial 0x11B (AES). Generator 0x03 (primitive: order 255).
  // NOTE: 0x02 is NOT primitive for 0x11b (order 51) — must use 0x03.
  const EXP = new Uint8Array(512);
  const LOG = new Uint8Array(256);
  (function initTables() {
    let x = 1;
    for (let i = 0; i < 255; i++) {
      EXP[i] = x;
      LOG[x] = i;
      const x2 = ((x << 1) ^ (x & 0x80 ? 0x1b : 0)) & 0xff; // x * 2 (xtime)
      x = (x2 ^ x) & 0xff;                                    // x * 3
    }
    for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
  })();
  function gmul(a, b) {
    if (a === 0 || b === 0) return 0;
    return EXP[LOG[a] + LOG[b]];
  }
  function gdiv(a, b) {
    if (b === 0) throw new Error("div0");
    if (a === 0) return 0;
    return EXP[(LOG[a] + 255 - LOG[b]) % 255];
  }
  // Evaluate polynomial (coeffs[0]=secret) at x using Horner.
  function evalPoly(coeffs, x) {
    let y = 0;
    for (let i = coeffs.length - 1; i >= 0; i--) y = gmul(y, x) ^ coeffs[i];
    return y;
  }
  // Lagrange interpolation at x=0 over GF(256). points = [[x,y],...]
  function interp0(points) {
    let secret = 0;
    for (let i = 0; i < points.length; i++) {
      const [xi, yi] = points[i];
      let num = 1, den = 1;
      for (let j = 0; j < points.length; j++) {
        if (i === j) continue;
        const xj = points[j][0];
        num = gmul(num, xj);          // product of xj  (since target x=0: (0 ^ xj)=xj)
        den = gmul(den, xi ^ xj);     // product of (xi ^ xj)
      }
      const lagrange = gdiv(num, den);
      secret ^= gmul(yi, lagrange);
    }
    return secret;
  }
  // Split a byte array into n shares with threshold t. Returns [{x, y:Uint8Array}].
  function shamirSplit(bytes, t, n) {
    if (t > n) throw new Error("t>n");
    const xs = [];
    for (let i = 1; i <= n; i++) xs.push(i); // x = 1..n (nonzero, distinct)
    const shares = xs.map((x) => ({ x, y: new Uint8Array(bytes.length) }));
    for (let b = 0; b < bytes.length; b++) {
      // random polynomial of degree t-1 with constant term = secret byte
      const coeffs = new Uint8Array(t);
      coeffs[0] = bytes[b];
      const r = rand(t - 1);
      for (let k = 1; k < t; k++) coeffs[k] = r[k - 1];
      for (let s = 0; s < n; s++) shares[s].y[b] = evalPoly(coeffs, xs[s]);
    }
    return shares;
  }
  // Reconstruct from >=t shares.
  function shamirCombine(shares) {
    if (!shares.length) throw new Error("no shares");
    const len = shares[0].y.length;
    const out = new Uint8Array(len);
    for (let b = 0; b < len; b++) {
      const pts = shares.map((s) => [s.x, s.y[b]]);
      out[b] = interp0(pts);
    }
    return out;
  }
  // Share <-> compact string: "x.b64u(y)"
  const shareToStr = (s) => s.x + "." + b64u.enc(s.y);
  const shareFromStr = (str) => {
    const [xs, ys] = String(str).trim().split(".");
    return { x: parseInt(xs, 10), y: b64u.dec(ys) };
  };

  // ================= Key derivation =================
  // HKDF-SHA256(ikm, salt, info) -> 32-byte AES-GCM key (CryptoKey)
  async function hkdfKey(ikm, salt, info) {
    const km = await crypto.subtle.importKey("raw", ikm, "HKDF", false, ["deriveKey"]);
    return crypto.subtle.deriveKey(
      { name: "HKDF", hash: "SHA-256", salt: salt, info: te.encode(info) },
      km,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }
  async function pbkdf2Key(pin, salt) {
    const km = await crypto.subtle.importKey("raw", te.encode(pin), "PBKDF2", false, ["deriveKey"]);
    return crypto.subtle.deriveKey(
      { name: "PBKDF2", hash: "SHA-256", salt: salt, iterations: 210000 },
      km,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }
  async function aesEncrypt(key, plaintextBytes) {
    const iv = rand(12);
    const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plaintextBytes);
    return { iv: b64u.enc(iv), ct: b64u.enc(ct) };
  }
  async function aesDecrypt(key, ivB64, ctB64) {
    const pt = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: b64u.dec(ivB64) }, key, b64u.dec(ctB64)
    );
    return new Uint8Array(pt);
  }

  // ================= WebAuthn (PRF) =================
  const RP = { name: "LightDAO", id: location.hostname };
  const PRF_SALT = te.encode("lightdao-passkey-wallet-v1"); // fixed first-input for deterministic PRF

  function prfSupported() {
    // Feature-detect PRF extension support (best effort).
    return typeof PublicKeyCredential !== "undefined" &&
      typeof PublicKeyCredential.isConditionalMediationAvailable === "function";
  }
  async function hasPrf() {
    try {
      return await PublicKeyCredential.isUserVerifiablePlatformAuthenticatorAvailable();
    } catch (e) { return false; }
  }

  // Register a passkey; try to obtain PRF-derived secret. Returns {credId, prf:Uint8Array|null}
  async function registerPasskey(userLabel) {
    const challenge = rand(32);
    const userId = rand(16);
    const pubKeyCredParams = [
      { type: "public-key", alg: -7 },   // ES256 (P-256)
      { type: "public-key", alg: -257 }, // RS256
    ];
    const createOpts = {
      challenge,
      rp: RP,
      user: { id: userId, name: userLabel || "lightdao-user", displayName: userLabel || "LightDAO User" },
      pubKeyCredParams,
      authenticatorSelection: { authenticatorAttachment: "platform", userVerification: "required", residentKey: "preferred" },
      timeout: 60000,
      attestation: "none",
      extensions: { prf: { eval: { first: PRF_SALT.buffer.slice(PRF_SALT.byteOffset, PRF_SALT.byteOffset + PRF_SALT.byteLength) } } },
    };
    const cred = await navigator.credentials.create({ publicKey: createOpts });
    const credId = b64u.enc(cred.rawId);
    let prf = null;
    try {
      const ext = cred.getClientExtensionResults && cred.getClientExtensionResults().prf;
      if (ext && ext.first) prf = new Uint8Array(ext.first);
    } catch (e) {}
    return { credId, prf };
  }

  // Assert with an existing passkey; try to obtain the same PRF-derived secret.
  async function assertPasskey(credId) {
    const challenge = rand(32);
    const getOpts = {
      challenge,
      rpId: RP.id,
      allowCredentials: credId ? [{ type: "public-key", id: b64u.dec(credId), transports: ["internal", "platform", "authenticator"] }] : undefined,
      userVerification: "required",
      timeout: 60000,
      extensions: { prf: { eval: { first: PRF_SALT.buffer.slice(PRF_SALT.byteOffset, PRF_SALT.byteOffset + PRF_SALT.byteLength) } } },
    };
    const asr = await navigator.credentials.get({ publicKey: getOpts });
    let prf = null;
    try {
      const ext = asr.getClientExtensionResults && asr.getClientExtensionResults().prf;
      if (ext && ext.first) prf = new Uint8Array(ext.first);
    } catch (e) {}
    return { credId: b64u.enc(asr.rawId), prf };
  }

  // ================= High-level wallet API =================
  const LS = "ld_passkey_v1"; // {credId, kdf:"prf"|"pin", iv, ct, salt?, pinHint?, shares?}
  const load = () => { try { return JSON.parse(localStorage.getItem(LS) || "null"); } catch (e) { return null; } };
  const save = (o) => localStorage.setItem(LS, JSON.stringify(o));

  // Derive the AES key from PRF secret (or PIN fallback) + stored salt.
  async function deriveKey(rec, prfSecret, pin) {
    const salt = b64u.dec(rec.salt);
    if (rec.kdf === "prf" && prfSecret) return hkdfKey(prfSecret, salt, "ld-passkey-prf");
    if (rec.kdf === "pin" && pin) return pbkdf2Key(pin, salt);
    throw new Error("missing credential (prf or pin)");
  }

  const LDPasskey = {
    b64u, shamirSplit, shamirCombine, shareToStr, shareFromStr, // exposed for tests
    gmul, gdiv, evalPoly, interp0,

    isAvailable() {
      return typeof navigator !== "undefined" && !!navigator.credentials &&
        typeof global.PublicKeyCredential !== "undefined" && !!crypto?.subtle;
    },
    hasWallet() { return !!load(); },

    // Create a passkey-protected wallet wrapping `mnemonic`.
    // Returns {usedPrf:boolean, needPin:boolean}
    async create(mnemonic, opts = {}) {
      const rec0 = { salt: b64u.enc(rand(16)) };
      const { credId, prf } = await registerPasskey(opts.userLabel);
      let kdf, key;
      if (prf) {
        kdf = "prf";
        key = await hkdfKey(prf, b64u.dec(rec0.salt), "ld-passkey-prf");
      } else {
        // PRF unavailable -> require a PIN as KEK
        if (!opts.pin) return { needPin: true, credId, partial: { salt: rec0.salt } };
        kdf = "pin";
        key = await pbkdf2Key(opts.pin, b64u.dec(rec0.salt));
      }
      const { iv, ct } = await aesEncrypt(key, te.encode(mnemonic));
      const rec = { credId, kdf, iv, ct, salt: rec0.salt };
      save(rec);
      return { usedPrf: kdf === "prf", needPin: false, rec };
    },

    // Finish PIN-based creation when PRF was unavailable.
    async createWithPin(mnemonic, credId, saltB64, pin) {
      const salt = b64u.dec(saltB64);
      const key = await pbkdf2Key(pin, salt);
      const { iv, ct } = await aesEncrypt(key, te.encode(mnemonic));
      save({ credId, kdf: "pin", iv, ct, salt: saltB64 });
      return { usedPrf: false, needPin: false };
    },

    // Unlock with passkey (+PIN if pin-kdf). Returns mnemonic or throws.
    async unlock(pin) {
      const rec = load();
      if (!rec) throw new Error("no wallet");
      let prf = null;
      try {
        const r = await assertPasskey(rec.credId); prf = r.prf;
      } catch (e) {
        if (e && e.name === "NotAllowedError") {
          // Exact credential likely removed from the OS password manager (irreversible).
          // Fall back to a discoverable get so the platform offers ANY lightdao.net passkey.
          let disc = null;
          try { disc = await assertPasskey(null); } catch (e2) { disc = null; }
          if (disc && disc.credId === rec.credId) { prf = disc.prf; }
          else if (disc) {
            throw new Error("PASSKEY_MISMATCH: the passkey you picked does not match this device's wallet data (the matching one was likely removed). Import via seed phrase / social recovery, or create a new wallet. / 选中的通行密钥与本机钱包数据不匹配(对应的那枚可能已被删除)。请用助记词或社交恢复导入,或新建钱包。");
          } else {
            throw new Error("PASSKEY_GONE: no lightdao.net passkey remains on this device (it was likely removed from the OS password manager, which is irreversible). This wallet can no longer be unlocked here - import via seed phrase / social recovery shares, or create a new wallet. / 本机已不存在该钱包的通行密钥(可能已在系统密码管理器中删除,删除不可逆)。请用助记词或社交恢复(分片)导入,或新建钱包。");
          }
        } else { throw e; }
      }
      const key = await deriveKey(rec, prf, pin);
      const pt = await aesDecrypt(key, rec.iv, rec.ct);
      return td.decode(pt);
    },

    // ---- Social recovery (Shamir 3-of-5 over the mnemonic) ----
    async setupSocialRecovery(pin, threshold = 3, total = 5) {
      const rec = load();
      if (!rec) throw new Error("no wallet");
      const { prf } = await assertPasskey(rec.credId);
      const key = await deriveKey(rec, prf, pin);
      const mnemonic = td.decode(await aesDecrypt(key, rec.iv, rec.ct));
      const shares = shamirSplit(te.encode(mnemonic), threshold, total);
      const strs = shares.map(LDPasskey.shareToStr);
      rec.meta = { threshold, total };
      save(rec);
      return strs; // caller distributes to guardians; NOT stored locally
    },

    // Reconstruct mnemonic from >=threshold share strings.
    recoverFromShares(shareStrs) {
      const shares = shareStrs.map(LDPasskey.shareFromStr).filter((s) => s.x > 0);
      const bytes = shamirCombine(shares);
      return td.decode(bytes);
    },

    // Wipe local passkey wallet (seed recoverable only via shares).
    clear() { localStorage.removeItem(LS); },
  };

  global.LDPasskey = LDPasskey;
})(typeof window !== "undefined" ? window : globalThis);
