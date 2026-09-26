/**
 * Bundled by jsDelivr using Rollup v4.62.2 and esbuild v0.28.1.
 * Original file: /npm/@protobufjs/eventemitter@1.1.0/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
var i,o;function f(){if(o)return i;o=1,i=s;function s(){this._listeners={}}return s.prototype.on=function(r,e,n){return(this._listeners[r]||(this._listeners[r]=[])).push({fn:e,ctx:n||this}),this},s.prototype.off=function(r,e){if(r===void 0)this._listeners={};else if(e===void 0)this._listeners[r]=[];else for(var n=this._listeners[r],t=0;t<n.length;)n[t].fn===e?n.splice(t,1):++t;return this},s.prototype.emit=function(r){var e=this._listeners[r];if(e){for(var n=[],t=1;t<arguments.length;)n.push(arguments[t++]);for(t=0;t<e.length;)e[t].fn.apply(e[t++].ctx,n)}return this},i}var u=f();export{u as default};
//# sourceMappingURL=/sm/6b1f6c789bc31dece2fa566857bab8eac1917df3afd73f439fe25a321aca846d.map