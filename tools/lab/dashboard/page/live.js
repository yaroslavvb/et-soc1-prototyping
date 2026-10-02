/* live.js: the dashboard's live section, drawn from the spacesheep streams aifoundry/<host> (one JSON line a second
   from tools/lab/live/live-collector.py on each machine). window.ss exists only when the page is open on spacesheep.dev.
   Each card is built once and updated in place, so an open "Top processes" fold stays open; its rows slide to their
   new places, ordered by a smoothed CPU share so they do not swap places every second.
   Temperatures: the host's sensors stream live, and so do the cards' die temperatures: the collector reads them once a
   second with `ettelem temp` while nobody holds a card on that machine. While a card is held (or its link is down)
   the page falls back to the last reading, and to the dashboard's 30-minute sample in D; the 48-hour line is D's. */
(function () {
  var HOSTS = ["aifoundry1", "aifoundry2", "aifoundry3"];
  var grid = document.getElementById("live-grid"), note = document.getElementById("live-state");
  if (!grid) return;
  var ROW_H = 22, TOP_N = 8, EMA = 0.35, KEEP = 300;
  var TS = [["cpu", "CPU", "var(--c1,#3b82c4)"], ["nvme", "NVMe", "var(--c3,#7c5cc4)"], ["nic", "NIC", "var(--c2,#2f9e8f)"]];
  var CARD_COL = ["#c53030", "#7c3aed"];
  var HIST = (typeof D !== "undefined" && D.history) || {}, CARDS = (typeof D !== "undefined" && D.cards) || {};
  var last = {}, hist = {}, ui = {};
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function gb(mb) { return (mb / 1024).toFixed(mb >= 10240 ? 0 : 1); }
  function age(h) { var v = last[h]; return v ? (Date.now() - v.t) / 1000 : Infinity; }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

  function build(h) {
    var c = el("div", "lv-card off");
    c.innerHTML = '<div class="lv-head"><b>' + h + '</b><span class="lv-dot"></span><span class="lv-age">not streaming</span></div>' +
      '<div class="lv-body"><div class="lv-row"><span class="lv-big">–</span><span class="small lv-sub"></span></div>' +
      '<div class="lv-cores" aria-label="CPU per thread"></div><svg class="lv-spark" viewBox="0 0 160 28" preserveAspectRatio="none" aria-hidden="true"><path/></svg>' +
      '<div class="lv-row small lv-mem"></div><div class="lv-row small lv-disk"></div>' +
      '<div class="lv-temps"><div class="lv-row small lv-tleg"></div><svg class="lv-tspark" viewBox="0 0 160 34" preserveAspectRatio="none" aria-hidden="true"></svg>' +
      '<div class="lv-die small"></div></div>' +
      '<div class="lv-row lv-cards"></div>' +
      '<details class="lv-topd"><summary>Top processes</summary><div class="lv-top"></div></details></div>';
    grid.appendChild(c);
    ui[h] = { card: c, rows: {}, ema: {},
      dot: c.querySelector(".lv-dot"), age: c.querySelector(".lv-age"), big: c.querySelector(".lv-big"), sub: c.querySelector(".lv-sub"),
      cores: c.querySelector(".lv-cores"), spark: c.querySelector(".lv-spark path"), mem: c.querySelector(".lv-mem"),
      cards: c.querySelector(".lv-cards"), top: c.querySelector(".lv-top"), disk: c.querySelector(".lv-disk"),
      tleg: c.querySelector(".lv-tleg"), tsvg: c.querySelector(".lv-tspark"), die: c.querySelector(".lv-die") };
    drawDie(h, null);
  }

  function path(vals, w, hgt, lo, hi, bridge) {  // SVG path; a run of more than `bridge` nulls breaks the line
    var n = vals.length, d = "", pen = false, gap = 0;
    vals.forEach(function (v, i) {
      if (v == null) { if (++gap > (bridge || 0)) pen = false; return; }
      gap = 0;
      var x = n < 2 ? 0 : i * w / (n - 1), y = hgt - (Math.max(lo, Math.min(hi, v)) - lo) * hgt / (hi - lo);
      d += (pen ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1); pen = true;
    });
    return d;
  }

  function fresh(c) { return c && c.temp && c.temp.at && Date.now() - c.temp.at < 5000 ? c.temp : null; }
  function cardOf(v, n) { return ((v && v.cards) || []).filter(function (c) { return String(c.n) === String(n); })[0]; }
  function ago(ms) { var s = Math.round((Date.now() - ms) / 1000); return s < 120 ? s + " s" : s < 7200 ? Math.round(s / 60) + " min" : Math.round(s / 3600) + " h"; }

  /* the ET card(s) of host h: the live die temperature when there is one, else the last reading; the 48-hour line
     from D.history.cards (10-minute steps) */
  function drawDie(h, v) {
    var u = ui[h], keys = Object.keys(CARDS).filter(function (k) { return k === h || k.indexOf(h + "-") === 0; });
    var html = "";
    keys.forEach(function (k) {
      var t = (CARDS[k] || {}).telemetry || {}, n = k === h ? 0 : k.slice(h.length + 2);
      var ser = ((HIST.cards || {})[k] || {}).die_c || [], c = cardOf(v, n), lt = fresh(c), note;
      if (lt) note = "live · hottest " + lt.die_max_c + " °C · " + lt.board_w.toFixed(0) + " W";
      else if (c && c.temp && c.temp.at) {
        t = { die_c: c.temp.die_c, at_ms: c.temp.at };
        note = "read " + ago(c.temp.at) + " ago" + (c.ok === false ? " (link down)" : c.held ? " (card in use)" : "");
      }
      if (!lt && !note && t.die_c == null && !ser.some(function (x) { return x != null; })) {
        html += '<div class="lv-dierow"><span>card ' + esc(n) + ' die: no reading</span></div>'; return;
      }
      var lo = 30, hi = 130, mx = Math.max.apply(null, ser.filter(function (x) { return x != null; }).concat([t.die_c || 0]));
      var cur = lt ? lt.die_c : t.die_c, hot = cur >= 95 ? " hot" : "";
      var when = t.at_ms ? new Date(t.at_ms).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "?";
      var mins = t.at_ms ? Math.round((Date.now() - t.at_ms) / 60000) : null;
      html += '<div class="lv-dierow"><span class="lv-dieval' + hot + '">card ' + esc(n) + " die " + (cur == null ? "?" : cur + " °C") + "</span>" +
        '<svg class="lv-diespark" style="--k:' + CARD_COL[keys.indexOf(k) % CARD_COL.length] + '" viewBox="0 0 120 16" preserveAspectRatio="none" role="img" aria-label="die temperature, last 48 hours, peak ' + mx + ' °C"><title>die temperature, last 48 h (peak ' + mx + ' °C); dashed: 95 °C</title>' +
        '<path class="lv-die95" d="M0,' + (16 - (95 - lo) * 16 / (hi - lo)).toFixed(1) + 'H120"/><path d="' + path(ser, 120, 16, lo, hi, 6) + '"/></svg>' +
        '<span class="muted">' + (note || "sampled " + when + (mins != null && mins > 40 ? " (" + ago(t.at_ms) + " ago)" : "")) + "</span></div>";
    });
    u.die.innerHTML = html;
  }

  function updateTop(h, v) {
    var u = ui[h], seen = {};
    (v.top || []).forEach(function (r) {  // [user, comm, pid, cpu, rss_mb]
      var k = r[0] + "|" + r[1] + "|" + r[2];
      seen[k] = r;
      u.ema[k] = u.ema[k] == null ? r[3] : u.ema[k] + EMA * (r[3] - u.ema[k]);
    });
    Object.keys(u.ema).forEach(function (k) { if (!seen[k]) { u.ema[k] *= 1 - EMA; if (u.ema[k] < 0.05) delete u.ema[k]; } });
    var order = Object.keys(u.ema).sort(function (a, b) { return u.ema[b] - u.ema[a]; }).slice(0, TOP_N);
    var keep = {};
    order.forEach(function (k, i) {
      keep[k] = 1;
      var row = u.rows[k];
      if (!row) {
        var p = k.split("|");
        row = el("div", "lv-tr entering", '<span class="lv-cpu"></span><span class="lv-user">' + esc(p[0]) + '</span><code class="lv-proc">' + esc(p[1]) + "</code>");
        row.style.transform = "translateY(" + (i * ROW_H) + "px)";
        u.top.appendChild(row); u.rows[k] = row;
        requestAnimationFrame(function () { row.classList.remove("entering"); });
      }
      row.style.transform = "translateY(" + (i * ROW_H) + "px)";
      var pct = seen[k] ? seen[k][3] : 0;
      row.firstChild.textContent = pct.toFixed(pct < 10 ? 1 : 0) + "%";
      row.firstChild.style.setProperty("--w", Math.min(100, pct) + "%");
    });
    Object.keys(u.rows).forEach(function (k) {
      if (keep[k]) return;
      var row = u.rows[k]; delete u.rows[k];
      row.classList.add("leaving");
      setTimeout(function () { row.remove(); }, 400);
    });
    u.top.style.height = (Math.max(order.length, 1) * ROW_H) + "px";
  }

  function update(h) {
    var u = ui[h], v = last[h], a = age(h), live = a < 5;
    u.card.className = "lv-card" + (v ? "" : " off");
    u.dot.className = "lv-dot" + (live ? " on" : a < 60 ? " stale" : "");
    u.age.textContent = v ? (live ? "live" : "last reading " + Math.round(a) + " s ago") : "not streaming";
    if (!v) return;
    u.big.textContent = v.cpu_all.toFixed(0) + "%";
    u.sub.textContent = "CPU, " + (v.cpu || []).length + " threads · load " + (v.load || []).join(" ");
    var cpu = v.cpu || [];
    while (u.cores.children.length < cpu.length) u.cores.appendChild(el("i"));
    while (u.cores.children.length > cpu.length) u.cores.lastChild.remove();
    cpu.forEach(function (x, i) { u.cores.children[i].style.height = Math.max(2, x) + "%"; u.cores.children[i].title = x + "%"; });
    var pts = (hist[h] || []).map(function (x) { return x.cpu_all; }), n = pts.length, d = "";
    pts.forEach(function (p, i) { d += (i ? "L" : "M") + (n < 2 ? 0 : i * 160 / (n - 1)).toFixed(1) + "," + (28 - p * 28 / 100).toFixed(1); });
    u.spark.setAttribute("d", d);
    var m = v.mem || {}, used = m.total_mb ? 100 * m.used_mb / m.total_mb : 0;
    u.mem.innerHTML = "memory " + gb(m.used_mb) + " of " + gb(m.total_mb) + ' GB<span class="lv-bar"><i style="width:' + used.toFixed(0) + '%"></i></span>';
    u.disk.innerHTML = (v.disk || []).map(function (d) {
      var tot = d.used_gb + d.free_gb, pct = tot ? 100 * d.used_gb / tot : 0;
      return '<span>disk <code>' + esc(d.mount) + "</code> " + d.used_gb.toFixed(0) + " GB used, " + d.free_gb.toFixed(0) + ' GB free<span class="lv-bar' + (pct > 90 ? " full" : "") + '"><i style="width:' + pct.toFixed(0) + '%"></i></span></span>';
    }).join(" ");
    var tp = {}, hs = hist[h] || [], all = [], lo, hi;
    // series: [label, colour, value of reading x]; the card lines take a reading only if it was read within 3 s of x
    var ser = TS.map(function (s) { return [s[1], s[2], function (x) { return (x.temps || {})[s[0]]; }]; });
    (v.cards || []).forEach(function (c, i) {
      ser.push(["card " + c.n, CARD_COL[i % CARD_COL.length], function (x) {
        var q = cardOf(x, c.n); return q && q.temp && Math.abs(x.t - q.temp.at) < 3000 ? q.temp.die_c : null; }]);
    });
    ser.forEach(function (s) { tp[s[0]] = s[2](v); hs.forEach(function (x) { var q = s[2](x); if (q != null) all.push(q); }); });
    if (all.length) {
      lo = Math.floor(Math.min.apply(null, all) / 5) * 5 - 5; hi = Math.ceil(Math.max.apply(null, all) / 5) * 5 + 5;
      u.tsvg.innerHTML = ser.map(function (s) {
        return '<path style="stroke:' + s[1] + '" d="' + path(hs.map(s[2]), 160, 34, lo, hi, 3) + '"/>';
      }).join("");
    }
    u.tleg.innerHTML = ser.filter(function (s) { return tp[s[0]] != null; }).map(function (s) {
      return '<span class="lv-tk' + (/^card/.test(s[0]) && tp[s[0]] >= 95 ? " hot" : "") + '" style="--k:' + s[1] + '">' + s[0] + " " + tp[s[0]].toFixed(0) + " °C</span>";
    }).join("") + (hs.length > 1 && all.length ? '<span class="muted">last ' + Math.max(1, Math.round((hs[hs.length - 1].t - hs[0].t) / 60000)) +
      " min, scale " + lo + "–" + hi + " °C</span>" : "");
    drawDie(h, v);
    u.cards.innerHTML = (v.cards || []).map(function (c) {
      var cls = c.ok === false ? "bad" : c.held ? "busy" : "ok";
      return '<span class="lv-chip ' + cls + '">card ' + c.n + ": " + esc(c.link) + (c.ok === false ? "" : c.held ? " · in use" : " · free") + "</span>";
    }).join(" ");
  }

  HOSTS.forEach(build);
  function tick() {
    HOSTS.forEach(update);
    if (note) note.textContent = HOSTS.filter(function (h) { return age(h) < 5; }).length + " of " + HOSTS.length + " machines streaming";
  }
  if (!(window.ss && window.ss.stream)) {
    if (note) note.textContent = "Live data appears when this page is open on spacesheep.dev.";
    tick();
    return;
  }
  HOSTS.forEach(function (h) {
    window.ss.stream("aifoundry/" + h).keep(KEEP).draw(function (v, history) {
      if (v && (!last[h] || v.t !== last[h].t)) { last[h] = v; updateTop(h, v); }
      hist[h] = (history || []).map(function (x) { return x && x.v ? x.v : x; }).filter(function (x) { return x && typeof x.cpu_all === "number"; });
      update(h);
    });
  });
  tick();
  setInterval(tick, 1000);
})();
