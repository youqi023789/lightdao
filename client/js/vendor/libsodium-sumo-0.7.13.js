/* LightDAO libsodium shim (pure JS, no WebAssembly).
 * cosmjs imports libsodium-wrappers-sumo but LightDAO flows only need:
 *   ready, randombytes_buf, to_base64, from_base64, to_hex.
 * Signing (secp256k1) and hashing (sha256/ripemd/pbkdf2) come from @noble (pure JS);
 * AES-GCM for passkey vault uses WebCrypto. Anything else throws loudly (unused paths).
 * Removes the WebAssembly/CSP(wasm-unsafe-eval) dependency so old WebViews (WeChat X5, old Safari) work.
 */
var b64c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
function toB64(u8) { var s = ""; for (var i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]); return btoa(s); }
function fromB64(st) { var bin = atob(st); var u = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u; }
function toHex(u8) { var s = ""; for (var i = 0; i < u8.length; i++) s += ("0" + u8[i].toString(16)).slice(-2); return s; }
var base = {
  ready: Promise.resolve(),
  randombytes_buf: function (n) { var u = new Uint8Array(n); crypto.getRandomValues(u); return u; },
  to_base64: toB64,
  from_base64: fromB64,
  to_hex: toHex,
  to_string: function (u8) { return new TextDecoder().decode(u8); },
  useBackupModule: function () { return Promise.resolve(); },
  addOnReady: function (fn) { if (fn) fn(); },
  from_string: function (st) { return new TextEncoder().encode(st); }
};
var shim = new Proxy(base, {
  get: function (t, k) {
    if (k in t) return t[k];
    if (k === "then") return undefined;
    if (typeof k === "string" && k.charAt(0) === "_") return function () { return 0; };
    if (k === "HEAPU8" || k === "HEAP8" || k === "HEAP32") return new Uint8Array(0);
    if (typeof k === "string" && k.indexOf("crypto_") === 0) return function () { throw new Error("libsodium-shim: " + String(k) + " not implemented (unused by LightDAO)"); };
    return function () { var n = String(k); if (n.indexOf("ToString") >= 0) return ""; return 0; };
  },
  set: function () { return true; }
});
export default shim;
export var ready = base.ready;
export var randombytes_buf = base.randombytes_buf;
export var to_base64 = base.to_base64;
export var from_base64 = base.from_base64;
export var to_hex = base.to_hex;
