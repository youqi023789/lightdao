/* 合约与地址页交互：复制 + 实时链高。刻意不依赖任何框架，也不改其它页面的全局。 */
(function () {
  "use strict";

  function toast(msg) {
    var el = document.getElementById("ldcpTip");
    if (!el) {
      el = document.createElement("div");
      el.id = "ldcpTip";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      el.style.cssText = "position:fixed;left:50%;bottom:26px;transform:translateX(-50%);" +
        "background:rgba(10,14,28,.94);color:#eaf0ff;border:1px solid rgba(255,255,255,.16);" +
        "padding:10px 16px;border-radius:999px;font-size:13.5px;z-index:99;pointer-events:none";
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.opacity = "1";
    clearTimeout(el._t);
    el._t = setTimeout(function () { el.style.opacity = "0"; }, 1800);
  }

  function copyText(s, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(s).then(function () { done(true); }, function () { legacy(s, done); });
      return;
    }
    legacy(s, done);
  }

  function legacy(s, done) {
    try {
      var ta = document.createElement("textarea");
      ta.value = s;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:-1000px;left:-1000px";
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand("copy");
      document.body.removeChild(ta);
      done(!!ok);
    } catch (e) {
      done(false);
    }
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest("button.cp") : null;
    if (!b) return;
    var a = b.getAttribute("data-a") || "";
    if (!a) return;
    copyText(a, function (ok) {
      toast(ok ? "已复制完整地址 / copied" : "复制失败，请手动选中");
      if (ok) {
        b.classList.add("done");
        setTimeout(function () { b.classList.remove("done"); }, 1200);
      }
    });
  });

  /* 实时链高：证明这页说的地址确实活在同一条链上。取不到就显示占位，绝不写死一个数字冒充实时。 */
  function refresh() {
    var el = document.getElementById("ldHeight");
    var elT = document.getElementById("ldTime");
    if (!el) return;
    try {
      fetch("/rpc/status", { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          var h = j && j.result && j.result.sync_info && j.result.sync_info.latest_block_height;
          var t = j && j.result && j.result.sync_info && j.result.sync_info.latest_block_time;
          if (h) { el.textContent = Number(h).toLocaleString(); el.style.color = "var(--ok,#39d98a)"; }
          else { el.textContent = "取不到（离线）"; el.style.color = "var(--warn,#ffb454)"; }
          if (elT && t) { elT.textContent = String(t).replace("T", " ").slice(0, 19) + " UTC"; }
        })
        .catch(function () { el.textContent = "取不到（离线）"; el.style.color = "var(--warn,#ffb454)"; });
    } catch (e) {
      el.textContent = "取不到（离线）";
    }
  }
  refresh();
  setInterval(refresh, 60000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) refresh(); });
})();
