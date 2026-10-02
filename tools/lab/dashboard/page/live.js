/* live.js: the dashboard's live section, drawn from the spacesheep streams aifoundry/<host> (one JSON line a second
   from tools/lab/live/live-collector.py on each machine). window.ss exists only when the page is open on spacesheep.dev. */
(function () {
  var HOSTS = ["aifoundry1", "aifoundry2", "aifoundry3"];
  var grid = document.getElementById("live-grid"), sel = document.getElementById("live-sel");
  var topT = document.getElementById("live-top"), note = document.getElementById("live-state");
  if (!grid) return;
  var last = {}, hist = {}, stat = {};
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function gb(mb) { return (mb / 1024).toFixed(mb >= 10240 ? 0 : 1); }
  function age(h) { var v = last[h]; return v ? (Date.now() - v.t) / 1000 : Infinity; }
  function spark(points) {
    if (!points.length) return "";
    var w = 160, hgt = 28, n = points.length, d = "";
    points.forEach(function (p, i) { d += (i ? "L" : "M") + (n < 2 ? 0 : (i * w / (n - 1))).toFixed(1) + "," + (hgt - p * hgt / 100).toFixed(1); });
    return '<svg class="lv-spark" viewBox="0 0 ' + w + ' ' + hgt + '" preserveAspectRatio="none" aria-hidden="true"><path d="' + d + '"/></svg>';
  }
  function card(h) {
    var v = last[h], a = age(h), live = a < 5;
    var head = '<div class="lv-head"><b>' + h + '</b><span class="lv-dot' + (live ? " on" : a < 60 ? " stale" : "") + '"></span><span class="lv-age">' +
      (v ? (live ? "live" : "last reading " + Math.round(a) + " s ago") : "not streaming") + "</span></div>";
    if (!v) return '<div class="lv-card off">' + head + '<p class="small">No live data from this machine yet.</p></div>';
    var cores = (v.cpu || []).map(function (c) { return '<i style="height:' + Math.max(2, c) + '%" title="' + c + '%"></i>'; }).join("");
    var m = v.mem || {}, used = m.total_mb ? 100 * m.used_mb / m.total_mb : 0;
    var cards = (v.cards || []).map(function (c) {
      var cls = c.ok === false ? "bad" : c.held ? "busy" : "ok";
      return '<span class="lv-chip ' + cls + '">card ' + c.n + ": " + esc(c.link) + (c.ok === false ? "" : c.held ? " · in use" : " · free") + "</span>";
    }).join(" ");
    return '<div class="lv-card">' + head +
      '<div class="lv-row"><span class="lv-big">' + v.cpu_all.toFixed(0) + '%</span><span class="small">CPU, ' + (v.cpu || []).length +
      " threads · load " + (v.load || []).join(" ") + "</span></div>" +
      '<div class="lv-cores" aria-label="per-thread CPU">' + cores + "</div>" + spark((hist[h] || []).map(function (x) { return x.cpu_all; })) +
      '<div class="lv-row small">memory ' + gb(m.used_mb) + " of " + gb(m.total_mb) + ' GB<span class="lv-bar"><i style="width:' + used.toFixed(0) + '%"></i></span></div>' +
      '<div class="lv-row">' + cards + "</div></div>";
  }
  function topRows() {
    var which = sel ? sel.value : "all", rows = [];
    HOSTS.forEach(function (h) {
      if ((which === "all" || which === h) && last[h] && age(h) < 60) (last[h].top || []).forEach(function (r) { rows.push([h].concat(r)); });
    });
    rows.sort(function (a, b) { return b[4] - a[4] || b[5] - a[5]; });
    rows = rows.slice(0, which === "all" ? 25 : 15);
    var head = "<thead><tr>" + (which === "all" ? "<th>Machine</th>" : "") + "<th>User</th><th>Process</th><th>PID</th><th>CPU %</th><th>Memory MB</th></tr></thead>";
    var body = rows.map(function (r) {
      return "<tr>" + (which === "all" ? "<td>" + r[0] + "</td>" : "") + "<td>" + esc(r[1]) + "</td><td><code>" + esc(r[2]) + "</code></td><td>" + r[3] +
        '</td><td class="num">' + r[4].toFixed(1) + '</td><td class="num">' + r[5] + "</td></tr>";
    }).join("");
    return head + "<tbody>" + (body || '<tr><td colspan="6" class="small">No live data yet.</td></tr>') + "</tbody>";
  }
  function render() {
    grid.innerHTML = HOSTS.map(card).join("");
    if (topT) topT.innerHTML = topRows();
    var n = HOSTS.filter(function (h) { return age(h) < 5; }).length;
    if (note) note.textContent = n + " of " + HOSTS.length + " machines streaming";
  }
  if (!(window.ss && window.ss.stream)) {
    if (note) note.textContent = "Live data appears when this page is open on spacesheep.dev.";
    render();
    return;
  }
  HOSTS.forEach(function (h) {
    window.ss.stream("aifoundry/" + h).keep(120).draw(function (v, history, st) {
      if (v) last[h] = v;
      hist[h] = (history || []).map(function (x) { return x && x.v ? x.v : x; }).filter(function (x) { return x && typeof x.cpu_all === "number"; });
      stat[h] = st;
    });
  });
  if (sel) sel.addEventListener("change", render);
  render();
  setInterval(render, 1000);
})();
