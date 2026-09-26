/**
 * Bundled by jsDelivr using Rollup v4.62.2 and esbuild v0.28.1.
 * Original file: /npm/minimalistic-crypto-utils@1.0.1/lib/utils.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
var u={},h;function y(){return h||(h=1,(function(x){var o=x;function p(r,n){if(Array.isArray(r))return r.slice();if(!r)return[];var t=[];if(typeof r!="string"){for(var e=0;e<r.length;e++)t[e]=r[e]|0;return t}if(n==="hex"){r=r.replace(/[^a-z0-9]+/ig,""),r.length%2!==0&&(r="0"+r);for(var e=0;e<r.length;e+=2)t.push(parseInt(r[e]+r[e+1],16))}else for(var e=0;e<r.length;e++){var l=r.charCodeAt(e),v=l>>8,c=l&255;v?t.push(v,c):t.push(c)}return t}o.toArray=p;function f(r){return r.length===1?"0"+r:r}o.zero2=f;function i(r){for(var n="",t=0;t<r.length;t++)n+=f(r[t].toString(16));return n}o.toHex=i,o.encode=function(n,t){return t==="hex"?i(n):n}})(u)),u}var a=y(),A=a.encode,d=a.toArray,s=a.toHex,z=a.zero2;export{a as default,A as encode,d as toArray,s as toHex,z as zero2};
//# sourceMappingURL=/sm/7a8a48a0bacff6667f27555ce4a8b17d90d53e09315f54046962821d5fb5a9dc.map