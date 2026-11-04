document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};

/* LD-SEASON-DAY-20261104  赛季页那个天数必须是实时数：所有者 2026-11-04 明确决定
   "承认延长、页面跟着链上走"，写死日历日就等于让页面重新变旧。
   取不到（网关不响应/返回不是 JSON/没有 current_day）就保持"—"，绝不显示猜测值。
   取法与首页 index_2.js 的 #sDay 完全一致（同一个端点、同一个字段），不另造口径。*/
(function () {
  try {
    fetch(location.origin + "/gw/v1/health?ts=" + Date.now(), { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (h) {
        if (!h || !h.current_day) return;
        var e = document.getElementById("epDay");
        if (e) e.textContent = h.current_day;
      })
      .catch(function () { });
  } catch (err) { }
})();
