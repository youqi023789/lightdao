/**
 * Bundled by jsDelivr using Rollup v4.62.2 and esbuild v0.28.1.
 * Original file: /npm/define-properties@1.1.3/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
import*as d from"object-keys-1.0.12.js";function m(o){return o&&Object.prototype.hasOwnProperty.call(o,"default")?o.default:o}var g=m(d),p,f;function D(){if(f)return p;f=1;var o=g,l=typeof Symbol=="function"&&typeof Symbol("foo")=="symbol",v=Object.prototype.toString,y=Array.prototype.concat,n=Object.defineProperty,_=function(r){return typeof r=="function"&&v.call(r)==="[object Function]"},b=function(){var r={};try{n(r,"x",{enumerable:!1,value:r});for(var t in r)return!1;return r.x===r}catch{return!1}},i=n&&b(),P=function(r,t,a,e){t in r&&(!_(e)||!e())||(i?n(r,t,{configurable:!0,enumerable:!1,value:a,writable:!0}):r[t]=a)},u=function(r,t){var a=arguments.length>2?arguments[2]:{},e=o(t);l&&(e=y.call(e,Object.getOwnPropertySymbols(t)));for(var s=0;s<e.length;s+=1)P(r,e[s],t[e[s]],a[e[s]])};return u.supportsDescriptors=!!i,p=u,p}var c=D(),S=c.supportsDescriptors;export{c as default,S as supportsDescriptors};
//# sourceMappingURL=/sm/c8c29eab1d69c5f986044d68f327b9274f0da67af46ad2f2dc1fb3b96e6f3677.map