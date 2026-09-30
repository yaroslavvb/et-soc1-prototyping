/* The lab dashboard (tools/lab/dashboard/DESIGN.md §4). D is the collector's data.json (§1), CK the report chart toolkit.
   Every string from the data goes into the page as text (textContent), never as HTML; tooltip HTML escapes it.
   Missing values are null and show as "—". The page never fetches anything: a new version arrives as a redeploy, and the
   spacesheep viewer reloads the tab (§4.4 covers what the viewer misses). */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const ELL = '—';
  const H = D.hosts || {}, C = D.cards || {}, P = Array.isArray(D.people) ? D.people : [], O = D.owner || {};
  const HI = D.history || {}, COL = D.collector || {};
  const OWNER = O.login || (P.find(p => p && p.owner) || {}).login || null;
  const STALE_MIN = +COL.stale_after_min || 80, IV_MIN = +COL.interval_min || 10, HB_MIN = +COL.heartbeat_min || 60;
  const natural = (a, b) => a.localeCompare(b, 'en', {numeric: true});
  const later = [];  // chart draws, run once the DOM they measure is in the page

  /* ---- DOM ---- */
  function add(e, kids) {
    for (const k of kids.flat(Infinity)) if (k != null && k !== false && k !== '') e.append(k instanceof Node ? k : String(k));
    return e;
  }
  const E = (tag, cls, ...kids) => { const e = document.createElement(tag); if (cls) e.className = cls; return add(e, kids); };
  const attrs = (e, a) => { for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]); return e; };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const plain = html => String(html).replace(/<br\s*\/?>/gi, '; ').replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
  const fill = (id, v) => { const e = $(id); if (e) e.textContent = v == null || v === '' ? ELL : v; };

  /* ---- numbers and times ---- */
  const isNum = v => typeof v === 'number' && isFinite(v);
  const n0 = v => (isNum(v) ? CK.fmt.num(v, 0) : ELL);
  const n1 = v => (isNum(v) ? CK.fmt.num(v, Math.abs(v) >= 100 ? 0 : 1) : ELL);
  const n2 = v => (isNum(v) ? CK.fmt.num(v, 2) : ELL);
  const plural = (n, one, many) => n + ' ' + (n === 1 ? one : (many || one + 's'));
  /* Epoch ms of the time o[k]: its *_ms twin (generated_at -> generated_ms, or k + '_ms') when present, else the ISO string. */
  function T(o, k) {
    if (!o || typeof o !== 'object') return null;
    const base = k.replace(/_at$/, '');
    for (const kk of [base + '_ms', k + '_ms']) if (isNum(o[kk])) return o[kk];
    const v = o[k];
    if (isNum(v)) return v > 1e11 ? v : v * 1000;
    if (typeof v === 'string') { const t = Date.parse(v); return isNaN(t) ? null : t; }
    return null;
  }
  const GEN = T(D, 'generated_at');
  const F_HM = new Intl.DateTimeFormat('en-GB', {hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
  const F_WD = new Intl.DateTimeFormat('en-GB', {weekday: 'short'});
  const F_DM = new Intl.DateTimeFormat('en-GB', {day: 'numeric', month: 'short'});
  const dayKey = ms => { const d = new Date(ms); return d.getFullYear() * 500 + d.getMonth() * 40 + d.getDate(); };
  let ZONE = '';
  try {
    const z = new Intl.DateTimeFormat('en-US', {timeZoneName: 'short'}).formatToParts(GEN || Date.now()).find(x => x.type === 'timeZoneName');
    ZONE = z ? z.value : '';
  } catch (_) { /* no zone name */ }
  /* "13:12" today, "Tue 11:40" this week, "25 Sep 16:38" before. */
  function clock(ms) {
    if (!isNum(ms)) return ELL;
    const now = Date.now();
    if (dayKey(now) === dayKey(ms)) return F_HM.format(ms);
    return (Math.abs(now - ms) < 6 * 864e5 ? F_WD.format(ms) : F_DM.format(ms)) + ' ' + F_HM.format(ms);
  }
  function dur(min) {
    if (!isNum(min)) return ELL;
    min = Math.max(0, min);
    if (min < 1) return 'under 1 min';
    if (min < 59.5) return Math.round(min) + ' min';
    if (min < 47.5 * 60) { const r = Math.round(min), h = Math.floor(r / 60), m = r % 60; return h + ' h' + (m ? ' ' + m + ' min' : ''); }
    const hrs = Math.round(min / 60), d = Math.floor(hrs / 24), h = hrs % 24;
    return d + ' d' + (h ? ' ' + h + ' h' : '');
  }
  /* "2026-10-28" -> "28 Oct"; any other string as it is */
  const dateText = s => (/^\d{4}-\d\d-\d\d$/.test(String(s)) ? F_DM.format(new Date(s + 'T12:00:00')) : String(s));
  const agoText = ms => (!isNum(ms) ? ELL : Date.now() - ms < 45e3 ? 'just now' : dur((Date.now() - ms) / 6e4) + ' ago');
  function agoSpan(ms) { const s = E('span', 'ago'); if (isNum(ms)) s.dataset.ago = ms; s.textContent = agoText(ms); return s; }
  const ageMin = () => (isNum(GEN) ? (Date.now() - GEN) / 6e4 : Infinity);
  /* The whole page is stale when its data is older than the collector's stale_after_min: then no card reads FREE and
     the light says what the data said. It is re-evaluated on every tick (tick() re-renders on a change). */
  let PAGE_STALE = ageMin() > STALE_MIN;
  /* The next run of the cron line "<m>-59/<iv> * * * *" after now (minutes counted in UTC, which equals local time for
     whole-hour zones). */
  function nextCheck(now) {
    const cm = (isNum(COL.cron_minute) ? COL.cron_minute : 2) % IV_MIN, d = new Date(now);
    d.setUTCSeconds(0, 0);
    let add1 = (cm - (d.getUTCMinutes() % IV_MIN) + IV_MIN) % IV_MIN;
    if (add1 === 0 && d.getTime() <= now - 30e3) add1 = IV_MIN;
    return d.getTime() + add1 * 6e4;
  }

  /* ---- levels ---- */
  const LV = {ok: 'lv-ok', warn: 'lv-warn', bad: 'lv-bad', stale: 'lv-stale', unknown: 'lv-unk', excluded: 'lv-excl', info: 'lv-info',
    ours: 'lv-ours', held: 'lv-held', free: 'lv-ok', missing: 'lv-bad'};
  const RANK = {bad: 3, warn: 2, info: 1, ok: 0};
  function pill(level, word, extra, title) {
    const p = E('span', 'pill ' + (LV[level] || 'lv-unk'), attrs(E('i'), {'aria-hidden': 'true'}), word, extra ? E('span', 'pl', extra) : null);
    if (title) p.title = title;
    return p;
  }
  const ALERTS = (Array.isArray(D.alerts) ? D.alerts : []).filter(a => a && a.id);
  const folded = a => !!(a.known || a.ack);
  const LIVE = ALERTS.filter(a => !folded(a));
  const hostOfCard = id => (C[id] && C[id].host) || String(id).replace(/-c\d+$/, '');
  const alertsOfHost = h => LIVE.filter(a => a.host === h || (a.card && hostOfCard(a.card) === h));
  const count = (list, lv) => list.filter(a => a.level === lv).length;

  const HOSTS = Object.keys(H).sort(natural);
  const CARDS = CK.cardsIn(C);
  const cardsOf = h => CARDS.filter(id => hostOfCard(id) === h);
  function cardName(id, short) {
    const c = C[id] || {}, h = hostOfCard(id), many = cardsOf(h).length > 1;
    if (short) return many ? 'card ' + (isNum(c.devnum) ? c.devnum : id.replace(/^.*-c/, '')) : 'card';
    return many ? h + ' card ' + (isNum(c.devnum) ? c.devnum : id.replace(/^.*-c/, '')) : h;
  }
  function markSvg(id, s) {
    s = s || 14;
    const svg = CK.el('svg', {width: s, height: s, viewBox: `0 0 ${s} ${s}`, 'aria-hidden': 'true', class: 'mk'});
    CK.cardMark(svg, id, s / 2, s / 2, s * 0.3);
    return svg;
  }
  const isOwner = login => !!login && login === OWNER;

  /* ---- a card's state: FREE, OURS, IN USE, EXCLUDED, NO DATA, MISSING ---- */
  function cardState(id) {
    const c = C[id] || {}, host = H[hostOfCard(id)] || {};
    if (c.excluded) return {key: 'excluded', word: 'EXCLUDED', title: c.note || 'excluded from all work'};
    if (c.present === false) return {key: 'missing', word: 'MISSING', title: 'the driver has no bound device for this card'};
    const who = (c.holder && Array.isArray(c.holder.who)) ? c.holder.who : [];
    const w = who[0] ? Object.assign({}, who[0], who[0].system ? {login: null} : {}) : null;  // root or CI: "system or CI"
    if (host.reachable === false || c.stale || PAGE_STALE) {
      const seen = (host.reachable === false || c.stale) ? (T(c, 'as_of') || T(host, 'last_ok_at')) : GEN;
      const was = w ? 'held by ' + (w.login || 'system or CI') : 'free';
      return {key: 'unknown', word: 'NO DATA', extra: seen ? 'was ' + was + ' at ' + clock(seen) : null, stale: true,
        title: PAGE_STALE ? 'this page\'s data is ' + dur(ageMin()) + ' old' : 'the machine did not answer the latest check'};
    }
    if (w) {
      const ours = w.ours || isOwner(w.login), t = isNum(w.etime_s) ? dur(w.etime_s / 60) : null;
      if (ours) return {key: 'ours', word: 'OURS', extra: t, login: w.login};
      return {key: 'held', word: 'IN USE', extra: (w.login || 'system or CI') + (t ? ' · ' + t : ''), login: w.login || null};
    }
    if (c.holder && c.holder.held) return {key: 'held', word: 'IN USE'};
    if (!c.holder || host.reachable !== true) return {key: 'unknown', word: 'NO DATA'};
    return {key: 'free', word: 'FREE'};
  }
  /* A card's health beside its occupancy word: its live warnings and problems, else its level. */
  function cardHealth(id) {
    const al = LIVE.filter(a => a.card === id), b = count(al, 'bad'), w = count(al, 'warn'), lv = (C[id] || {}).level;
    if (b) return pill('bad', plural(b, 'PROBLEM', 'PROBLEMS'));
    if (w) return pill('warn', plural(w, 'WARNING', 'WARNINGS'));
    if (lv === 'bad' || lv === 'warn') return pill(lv, lv === 'bad' ? 'PROBLEM' : 'WARNING');
    return null;
  }
  function reading(c) {
    const t = (c && c.telemetry) || null;
    if (!t || t.source === 'none' || (t.die_c == null && t.board_w == null)) return null;
    let at = T(t, 'at');
    if (at == null && isNum(t.age_min) && isNum(GEN)) at = GEN - t.age_min * 6e4;
    return {die: t.die_c, dieMax: t.die_max_c, pmic: t.pmic_c, w: t.board_w, mhz: t.minion_mhz, noc: t.noc_mhz, ddr: t.ddr_mhz,
      at, source: t.source, from: t.from};
  }
  const SRC = {live: 'live sample', experiment: 'experiment file'};

  /* ---- people ---- */
  const STATUS_RANK = {active: 0, idle: 1, 'processes only': 2, away: 3};
  const pdClass = s => ({active: 'active', idle: 'idle', away: 'away', 'processes only': 'procs'}[s] || 'away');
  const presence = s => attrs(E('span', 'pd ' + pdClass(s)), {'aria-hidden': 'true'});
  function sortedPeople(list) {
    return list.slice().sort((a, b) => (b.owner ? 1 : 0) - (a.owner ? 1 : 0) || (STATUS_RANK[a.status] ?? 9) - (STATUS_RANK[b.status] ?? 9)
      || natural(String(a.login), String(b.login)));
  }
  const peopleOn = h => sortedPeople(P.filter(p => p && p.hosts && p.hosts[h]));
  function idleOf(p, h) {
    const hs = h ? [p.hosts[h]] : Object.values(p.hosts || {});
    const v = hs.map(x => x && x.idle_min).filter(isNum);
    return v.length ? Math.min(...v) : null;
  }
  /* A person's status on one machine (the collector's per-machine status), else their overall status. */
  const statusOn = (p, h) => (h && p.hosts && p.hosts[h] && p.hosts[h].status) || (h && p.hosts && p.hosts[h] ? 'processes only' : p.status);
  function personChip(p, h) {
    const idle = idleOf(p, h), me = p.owner || isOwner(p.login), st = statusOn(p, h) || 'unknown';
    const s = E('span', 'who' + (me ? ' me' : ''), presence(st), p.login, me ? ' (you)' : null,
      E('span', 'vh', ', ' + st + (isNum(idle) ? ', idle ' + dur(idle) : '')));
    s.title = st + (isNum(idle) ? ', idle ' + dur(idle) : '');
    return s;
  }

  /* ---- focus: #focus=<host> opens a machine's panel, #card=<card> (or #focus=<card>) a card's tile. The template mirrors the
     hash to the viewer (ss-hash), which restores it after every reload, so a selection survives the automatic refresh. ---- */
  function focusTarget(hash) {
    const m = /^#(focus|card)=([A-Za-z0-9_.-]+)$/.exec(hash || '');
    if (!m) return null;
    if (m[1] === 'focus' && H[m[2]]) return document.querySelector(`[data-host="${m[2]}"]`);
    if (C[m[2]]) return document.querySelector(`[data-card="${m[2]}"]`);
    return null;
  }
  function focusOn(hash, smooth) {
    const el = focusTarget(hash);
    if (!el) return false;
    document.querySelectorAll('.focused').forEach(e => e.classList.remove('focused'));
    el.classList.add('focused');
    const d = el.querySelector(':scope > details.ct-more');
    if (d) d.open = true;
    el.scrollIntoView({block: 'start', behavior: smooth && !CK.reduced ? 'smooth' : 'auto'});
    return true;
  }
  function go(hash) {
    try { history.replaceState(null, '', location.pathname + location.search + hash); } catch (_) { /* sandboxed */ }
    if (window.parent !== window) { try { window.parent.postMessage({type: 'ss-hash', hash}, '*'); } catch (_) { /* no viewer */ } }
    focusOn(hash, true);
  }
  function focusLink(a, hash) { a.addEventListener('click', ev => { ev.preventDefault(); go(hash); }); return a; }

  /* ---- a crosshair tooltip for time series drawn in a CK.frame: pointer, touch and keyboard (arrows, Home, End, Escape) ---- */
  const openTips = new Set();
  document.addEventListener('pointerdown', ev => { for (const t of openTips) if (!t.host.contains(ev.target)) t.hide(); }, true);
  function place(f, cx, cy) {
    const t = f.tip;
    t.style.display = 'block'; t.style.left = '0px'; t.style.top = '0px';
    const hb = f.host.getBoundingClientRect(), tw = t.offsetWidth, th = t.offsetHeight, vw = document.documentElement.clientWidth;
    let left = cx + 12;
    if (hb.left + left + tw > vw - 6) left = vw - 6 - tw - hb.left;
    if (hb.left + left < 6) left = 6 - hb.left;
    let top = cy + 14;
    if (hb.top + top + th > window.innerHeight - 4 && hb.top + cy - th - 10 > 0) top = cy - th - 10;
    t.style.left = Math.round(left) + 'px'; t.style.top = Math.round(top) + 'px';
  }
  function crossHover(f, o) {
    const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    const ln = CK.el('line', {class: 'xh', y1: o.top, y2: o.bottom}, g);
    const dots = CK.el('g', null, g);
    g.style.display = 'none';
    const n = o.n, x0 = o.x(0), x1 = o.x(n - 1), valid = o.valid || (() => true);
    const hit = CK.el('rect', {class: 'ck-hit', x: Math.min(x0, x1) - 4, y: 0, width: Math.abs(x1 - x0) + 8, height: f.H,
      tabindex: 0, role: 'img', 'aria-label': o.label || ''}, f.svg);
    let cur = null;
    const last = () => { for (let j = n - 1; j >= 0; j--) if (valid(j)) return j; return null; };
    const first = () => { for (let j = 0; j < n; j++) if (valid(j)) return j; return null; };
    function nearest(px) {
      let i = Math.round((px - x0) / ((x1 - x0) / Math.max(1, n - 1)));
      i = Math.max(0, Math.min(n - 1, i));
      for (let d = 0; d < n; d++) { if (i - d >= 0 && valid(i - d)) return i - d; if (i + d < n && valid(i + d)) return i + d; }
      return null;
    }
    const api = {host: f.host, hide};
    function hide() { g.style.display = 'none'; f.tip.style.display = 'none'; cur = null; openTips.delete(api); }
    function show(i, cx, cy) {
      if (i == null) { hide(); return; }
      cur = i;
      const px = o.x(i);
      g.style.display = '';
      ln.setAttribute('x1', px); ln.setAttribute('x2', px);
      while (dots.firstChild) dots.removeChild(dots.firstChild);
      for (const d of (o.dots ? o.dots(i) : [])) if (d) CK.el('circle', {cx: d[0], cy: d[1], r: 3.2, class: 'xh-dot'}, dots).style.fill = d[2];
      f.tip.innerHTML = o.html(i);
      const sb = f.svg.getBoundingClientRect(), hb = f.host.getBoundingClientRect();
      place(f, cx == null ? sb.left - hb.left + px : cx, cy == null ? sb.top - hb.top + o.top : cy);
      openTips.add(api);
    }
    const at = ev => { const sb = f.svg.getBoundingClientRect(), hb = f.host.getBoundingClientRect(); show(nearest(ev.clientX - sb.left), ev.clientX - hb.left, ev.clientY - hb.top); };
    hit.addEventListener('pointermove', at);
    hit.addEventListener('pointerdown', at);
    hit.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') hide(); });
    hit.addEventListener('focus', () => { if (cur == null) show(last()); });
    hit.addEventListener('blur', hide);
    hit.addEventListener('keydown', ev => {
      const k = ev.key;
      if (k === 'Escape') { hide(); return; }
      let i = cur == null ? last() : cur;
      if (i == null) return;
      const stepTo = d => { for (let j = i + d; j >= 0 && j < n; j += d) if (valid(j)) return j; return i; };
      if (k === 'ArrowLeft' || k === 'ArrowDown') i = stepTo(ev.shiftKey ? -6 : -1);
      else if (k === 'ArrowRight' || k === 'ArrowUp') i = stepTo(ev.shiftKey ? 6 : 1);
      else if (k === 'Home') i = first();
      else if (k === 'End') i = last();
      else return;
      ev.preventDefault();
      show(i);
    });
  }

  /* ---- history grid ---- */
  const HN = isNum(HI.n) ? HI.n : 0, HT0 = isNum(HI.t0_ms) ? HI.t0_ms : null, HSTEP = (isNum(HI.step_min) ? HI.step_min : 10) * 6e4;
  const HEND = HT0 == null ? null : HT0 + HN * HSTEP;
  const slotT = i => HT0 + i * HSTEP;
  const slotLabel = i => clock(slotT(i)) + '–' + F_HM.format(slotT(i + 1));
  const series = (group, id, key) => { const s = ((HI[group] || {})[id] || {})[key]; return Array.isArray(s) && s.length === HN ? s : null; };
  /* Time ticks at local whole hours, every `every` hours; midnight is labelled with the weekday. */
  function timeTicks(a, b, every) {
    const out = [], d = new Date(a);
    d.setMinutes(0, 0, 0);
    while (d.getTime() < a || d.getHours() % every) d.setHours(d.getHours() + 1);
    for (; d.getTime() <= b; d.setHours(d.getHours() + every)) out.push(d.getTime());
    return out;
  }
  const tickLabel = t => { const d = new Date(t); return d.getHours() === 0 ? F_WD.format(t) + ' ' + d.getDate() : F_HM.format(t); };

  /* A sparkline: series [{v, color, label}] over the 48-hour grid, with a crosshair tooltip. */
  function spark(host, o) {
    const ss = o.series.filter(s => s.v);
    if (!ss.length || !HN) { host.append(E('span', 'small muted', 'no history')); return; }
    const all = ss.flatMap(s => s.v.filter(isNum));
    if (!all.length) { host.append(E('span', 'small muted', 'no history yet')); return; }
    host.classList.add('spark');
    CK.frame(host, {minW: 60, maxW: 640, height: o.height || 28, label: o.label, draw(f) {
      const L = 2, R = 4, Tp = 4, B = 3;
      let lo = o.lo != null ? Math.min(o.lo, ...all) : Math.min(...all), hi = o.hi != null ? Math.max(o.hi, ...all) : Math.max(...all);
      if (!(hi > lo)) { hi = lo + 1; }
      const x = CK.lin(0, HN - 1, L, f.W - R), y = CK.lin(lo, hi, f.H - B, Tp);
      CK.el('line', {class: 'sp-base', x1: L, x2: f.W - R, y1: f.H - B + 0.5, y2: f.H - B + 0.5}, f.svg);
      for (const s of ss.slice().reverse()) {
        let d = '', pen = false;
        s.v.forEach((v, i) => { if (isNum(v)) { d += (pen ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(v).toFixed(1); pen = true; } else pen = false; });
        CK.el('path', {d, class: 'sp-line'}, f.svg).style.stroke = s.color;
        s.v.forEach((v, i) => {  // an isolated reading has no neighbour to draw a line to
          if (isNum(v) && !isNum(s.v[i - 1]) && !isNum(s.v[i + 1])) CK.el('circle', {cx: x(i), cy: y(v), r: 1.6}, f.svg).style.fill = s.color;
        });
      }
      const s0 = ss[0];
      for (let i = HN - 1; i >= 0; i--) if (isNum(s0.v[i])) { CK.el('circle', {cx: x(i), cy: y(s0.v[i]), r: 2.4}, f.svg).style.fill = s0.color; break; }
      crossHover(f, {n: HN, x, top: Tp - 2, bottom: f.H - B, label: o.label + ', last 48 hours',
        valid: i => ss.some(s => isNum(s.v[i])),
        dots: i => ss.map(s => (isNum(s.v[i]) ? [x(i), y(s.v[i]), s.color] : null)),
        html: i => `<b>${esc(o.name || o.label)}</b><br>${esc(slotLabel(i))}<br>` +
          ss.map(s => esc(s.label) + ': ' + esc(isNum(s.v[i]) ? (o.fmt || n1)(s.v[i]) : 'no data')).join('<br>')});
    }});
  }
  function meter(pct, warnAt, badAt) {
    const m = E('div', 'meter' + (pct >= badAt ? ' bad' : pct >= warnAt ? ' warn' : ''));
    const s = E('span'); s.style.width = Math.max(0, Math.min(100, pct)) + '%'; m.append(s);
    return attrs(m, {role: 'img', 'aria-label': n0(pct) + '% used'});
  }

  /* ================= header ================= */
  let lightWas = null;
  function renderHeader() {
    const age = ageMin(), stale = age > STALE_MIN;
    const data = (D.status || {}).level || 'unknown', lvl = stale ? 'stale' : data;
    const WORD = {ok: 'HEALTHY', warn: 'WARNINGS', bad: 'NEEDS ATTENTION', stale: 'STALE', unknown: 'NO DATA'};
    const word = stale ? 'STALE · was ' + (WORD[data] || 'NO DATA') : (WORD[lvl] || 'NO DATA');
    if (word !== lightWas) {  // the light is a live region: rewrite it only when it changes
      lightWas = word;
      $('light').className = 'light ' + (LV[lvl] || 'lv-unk');
      fill('light-word', word);
    }
    const t = $('asof');
    t.textContent = clock(GEN) + (ZONE ? ' ' + ZONE : '');
    if (isNum(GEN)) t.setAttribute('datetime', new Date(GEN).toISOString());
    fill('age', agoText(GEN));
    $('next-lead').textContent = stale ? 'next check: ' : 'next check about ';
    fill('next', stale ? 'unknown, the collector may be stopped' : clock(nextCheck(Date.now())));
    $('stale').hidden = !stale;
    if (stale) { fill('stale-age', dur(age)); fill('stale-hb', dur(HB_MIN)); fill('stale-host', COL.host || 'aifoundry2'); }
  }
  function renderStatic() {
    const st = D.status || {};
    let head = st.headline;
    if (!head && !st.level) head = 'This data file has no overall status: the collector may be older or newer than this page.';
    if (!head) {
      const b = count(LIVE, 'bad'), w = count(LIVE, 'warn');
      head = b ? plural(b, 'problem') + (w ? ' and ' + plural(w, 'warning') : '') : w ? plural(w, 'warning') : 'Every machine and card looks healthy.';
    }
    fill('headline', head);
    fill('cadence', `checked every ${IV_MIN} min, republished on any change and at least every ${HB_MIN} min`);
    $('fixture-pill').hidden = !(COL.fixture || (D._build || {}).fixture);
    fill('ab-host', COL.host || 'aifoundry2'); fill('ab-iv', IV_MIN); fill('ab-hb', HB_MIN);
    const b = D._build || {};
    fill('ab-version', `Data from ${clock(GEN)}${ZONE ? ' ' + ZONE : ''}, collected in ${isNum(COL.took_s) ? n1(COL.took_s) + ' s' : ELL}` +
      ` by collector code ${COL.code || ELL}; page built ${isNum(b.at_ms) ? clock(b.at_ms) : ELL} from page sources ${b.page || ELL}` +
      `${b.fixture || COL.fixture ? ', from the made-up fixture' : ''}; card sampling ${COL.card_sample || 'off'}; data fingerprint ${D.fingerprint || ELL}.`);
    const errs = (Array.isArray(COL.errors) ? COL.errors : []).slice();
    if (COL.halted) errs.unshift('deploys are halted (' + (typeof COL.halted === 'string' ? COL.halted : 'HALT set') + '); update.sh resume clears it');
    const ld = T(COL, 'last_deploy');
    if (ld) fill('ab-version', $('ab-version').textContent.replace(/\.$/, `; the previous deploy was at ${clock(ld)}.`));
    fill('ab-errors', errs.length ? 'Collector errors in this run: ' + errs.join('; ') + '.' : 'The collector reported no errors in this run.');
  }

  /* ================= theme: auto, light, dark ================= */
  function renderTheme() {
    const KEY = 'labdash.theme', root = document.documentElement;
    let pick = null;
    try { const q = new URLSearchParams(location.search).get('theme'); if (/^(light|dark|auto)$/.test(q || '')) pick = q; } catch (_) { /* no query */ }
    if (!pick) { try { pick = localStorage.getItem(KEY); } catch (_) { pick = null; } }
    if (pick === 'light' || pick === 'dark') root.dataset.theme = pick;
    else if (pick === 'auto') delete root.dataset.theme;
    CK.seg('theme', {label: 'Theme', value: root.dataset.theme || 'auto', options: [['auto', 'Auto'], ['light', 'Light'], ['dark', 'Dark']],
      onChange: v => {
        if (v === 'auto') delete root.dataset.theme; else root.dataset.theme = v;
        try { localStorage.setItem(KEY, v); } catch (_) { /* not remembered */ }
      }});
  }

  /* ================= overview strip ================= */
  function hostPill(h) {
    const al = alertsOfHost(h), b = count(al, 'bad'), w = count(al, 'warn'), x = H[h] || {};
    if (b) return pill('bad', plural(b, 'PROBLEM', 'PROBLEMS'));
    if (w) return pill('warn', plural(w, 'WARNING', 'WARNINGS'));
    if (x.reachable === false) return pill('unknown', 'NO ANSWER');
    if (x.reachable !== true) return pill('unknown', 'NO DATA');
    if (x.level === 'bad' || x.level === 'warn') return pill(x.level, x.level === 'bad' ? 'PROBLEM' : 'WARNING');
    return pill('ok', 'OK');
  }
  function reachText(x) {
    const why = x.error || 'no answer', last = T(x, 'last_ok_at') || T(x, 'as_of');
    return [why, last ? ' · last data ' + clock(last) + ' (' : '', last ? agoSpan(last) : null, last ? ')' : ''];
  }
  function upText(x) { return isNum(x.uptime_h) ? 'up ' + dur(x.uptime_h * 60) : null; }
  function renderStrip() {
    const root = $('strip');
    for (const h of HOSTS) {
      const x = H[h] || {}, box = E('div', 'mbox card');
      const a = focusLink(attrs(E('a', null, h), {href: '#m-' + h}), '#focus=' + h);
      box.append(E('div', 'mbox-head', a, hostPill(h)));
      const lp = x.load || {};
      box.append(E('div', 'mbox-sub', x.reachable === false ? reachText(x)
        : [upText(x), isNum(lp.per_thread) ? ' · load ' + n2(lp.per_thread) + ' per thread' : '', x.via === 'local' ? ' · the collector runs here' : '']));
      for (const id of cardsOf(h)) {
        const st = cardState(id), r = reading(C[id]);
        const hp = cardHealth(id), old = !!(r && isNum(r.at) && Date.now() - r.at > 3 * 36e5);
        const chip = focusLink(attrs(E('a', 'cchip'), {href: '#card-' + id, 'aria-label': cardName(id) + ': ' + st.word +
          (st.extra ? ', ' + st.extra : '') + (hp ? ', ' + hp.textContent.toLowerCase() : '')}), '#card=' + id);
        chip.append(markSvg(id), E('span', 'cc-name', cardName(id, true)),
          pill(st.key, st.word, st.extra, st.title));
        chip.append(E('span', 'cc-temp' + (old ? ' old' : ''), hp, hp ? ' ' : '', C[id].excluded ? 'never touched; driver counters only'
          : r && isNum(r.die) ? [old ? 'last reading: ' : '', `die ${n0(r.die)} °C`, isNum(r.w) ? ` · ${n1(r.w)} W` : '', ' · ', agoSpan(r.at)] : 'no temperature reading'));
        box.append(chip);
      }
      const ppl = peopleOn(h);
      box.append(E('div', 'logins', ppl.length ? ppl.map(p => personChip(p, h)) : E('span', 'small muted', 'nobody seen')));
      root.append(box);
    }
  }

  /* ================= KPIs ================= */
  function renderKpis() {
    const k = (lab, val, sub) => E('div', 'kpi card', E('div', 'lab', lab), E('div', 'val', val), E('div', 'sub', sub || ELL));
    const ans = HOSTS.filter(h => (H[h] || {}).reachable === true);
    const miss = HOSTS.filter(h => (H[h] || {}).reachable !== true).map(h => h + ': ' + ((H[h] || {}).reachable === false ? (H[h] || {}).error || 'no answer' : 'no data'));
    const usable = CARDS.filter(id => !(C[id] || {}).excluded);
    const states = usable.map(cardState), free = states.filter(s => s.key === 'free').length;
    const parts = [];
    const ours = states.filter(s => s.key === 'ours').length, held = states.filter(s => s.key === 'held');
    if (ours) parts.push(ours + ' ours');
    if (held.length) parts.push(held.length + ' in use' + (held.length === 1 && held[0].login ? ' by ' + held[0].login : ''));
    const unk = states.filter(s => s.key === 'unknown').length; if (unk) parts.push(unk + ' no data');
    const excl = CARDS.length - usable.length; if (excl) parts.push(excl + ' excluded');
    const b = count(LIVE, 'bad'), w = count(LIVE, 'warn'), inf = count(LIVE, 'info'), kn = ALERTS.length - LIVE.length;
    const act = P.filter(p => p.status === 'active').length;
    const others = ['idle', 'away', 'processes only'].map(s => [s, P.filter(p => p.status === s).length]).filter(x => x[1]).map(x => x[1] + ' ' + x[0]);
    const runs = HOSTS.flatMap(h => (((H[h] || {}).experiments || {}).running || []).map(r => [h, r]));
    const bm = (O.sessions || {}).by_machine || {};
    const working = Object.values(bm).reduce((s, m) => s + (isNum(m.working) ? m.working : 0), 0);
    const accts = ((O.claudes || {}).accounts) || [];
    $('kpis').append(
      k('Machines answering', `${ans.length} of ${HOSTS.length}`, miss.length ? miss.join('; ') : 'all answered the last check'),
      k('Cards free', `${free} of ${usable.length}`, parts.join(' · ') || 'all free'),
      k('Alerts', b ? plural(b, 'problem') : w ? plural(w, 'warning') : 'none',
        `${plural(b, 'problem')} · ${plural(w, 'warning')} · ${plural(inf, 'note')} · ${kn} known`),
      k('People active now', String(act), P.length ? `of ${P.length} seen` + (others.length ? ': ' + others.join(', ') : '') : 'nobody seen'),
      k('Our experiments', runs.length ? runs.length + ' running' : 'none running',
        runs.length ? runs.map(([h, r]) => `${r.kind || 'run'} on ${h}`).join('; ') : lastEnded()),
      k('Your Claude sessions', working + ' working',
        (isNum((O.sessions || {}).needs_you) && O.sessions.needs_you ? `${O.sessions.needs_you} need${O.sessions.needs_you === 1 ? 's' : ''} you · ` : '') +
        (accts.length ? `claudes: ${accts.filter(a => a.logged_in).length} of ${accts.length} logged in` : 'claudes: no data')));
  }
  function lastEnded() {
    let best = null;
    for (const h of HOSTS) { const l = (((H[h] || {}).experiments) || {}).last_log; const t = T(l, 'at'); if (l && t && (!best || t > best.t)) best = {t, h}; }
    return best ? `last log line ${clock(best.t)} on ${best.h}` : 'no recent log';
  }

  /* ================= alerts ================= */
  const AWORD = {bad: 'PROBLEM', warn: 'WARNING', info: 'NOTE'};
  function scopeOf(a) {
    if (a.card) return E('span', 'scope', markSvg(a.card, 12), cardName(a.card));
    if (a.host) return E('span', 'scope', a.host);
    return E('span', 'scope', {owner: 'you', people: 'people', collector: 'the collector'}[a.scope] || a.scope || ELL);
  }
  function alertRow(a, minor) {
    const since = T(a, 'since');
    const d = E('details', 'al ' + (LV[a.level] || 'lv-info') + (minor ? ' minor' : ''));
    d.append(E('summary', null, pill(a.level, AWORD[a.level] || String(a.level || '').toUpperCase()), scopeOf(a), E('span', 'al-title', a.title || a.id),
      E('span', 'al-since', since ? ['since ', clock(since)] : '', a.stale ? ' (old data)' : '')));
    const body = E('div', 'al-body');
    if (a.detail) body.append(E('p', null, a.detail));
    if (a.known) body.append(E('p', null, E('b', null, 'Known condition: '), typeof a.known === 'string' ? a.known : 'listed in lab.json'));
    if (a.ack) {
      const k = typeof a.ack === 'object' ? a.ack : {note: String(a.ack)}, until = T(k, 'until');
      body.append(E('p', null, E('b', null, 'Acknowledged'), k.note ? ': ' + k.note : '', until ? ` (until ${clock(until)})` : ''));
    }
    body.append(E('p', 'small', 'Source: ', a.source || ELL, since ? ['; first seen ', clock(since), ' (', agoSpan(since), ')'] : '',
      '. ID ', E('code', null, a.id), a.level !== 'info' && !folded(a) ? ['; to silence it: ', E('code', null, 'update.sh ack ' + a.id)] : ''));
    d.append(body);
    return d;
  }
  function renderAlerts() {
    const root = $('alert-list'), main = LIVE.filter(a => a.level === 'bad' || a.level === 'warn');
    const notes = LIVE.filter(a => a.level !== 'bad' && a.level !== 'warn'), known = ALERTS.filter(folded);
    if (!main.length) root.append(E('p', 'noalerts', pill('ok', 'OK'), 'No warnings.'));
    else root.append(E('div', 'alist', main.map(a => alertRow(a))));
    if (notes.length) root.append(E('div', 'alabel', 'Notes'), E('div', 'alist', notes.map(a => alertRow(a, true))));
    if (known.length) {
      const m = E('details', 'more', E('summary', null, plural(known.length, 'known condition'), ' ',
        E('span', 'more-hint', '(known or acknowledged; not counted in the light)')));
      m.append(E('div', 'alist', known.map(a => alertRow(a, true))));
      root.append(m);
    }
  }

  /* ================= machines and cards ================= */
  function vital(label, value, sub, viz, wide) {
    const v = E('div', 'vital' + (wide ? ' wide' : ''), E('div', 'vl', label), E('div', 'vv', value, sub ? E('span', 'vsub', sub) : null));
    if (!wide) v.append(viz || E('div', 'vs'));
    return v;
  }
  function vitals(h) {
    const x = H[h] || {}, out = E('div', 'vitals');
    const hs = k => series('hosts', h, k);
    const lp = x.load || {}, th = isNum(lp.threads) ? lp.threads : null;
    const loadS = hs('load'), perT = loadS && th ? loadS.map(v => (isNum(v) ? v / th : null)) : null;
    const sp1 = E('div', 'vs');
    out.append(vital('Load', isNum(lp.per_thread) ? n2(lp.per_thread) + ' per thread' : ELL,
      isNum(lp['1']) ? `${n2(lp['1'])} over ${th || '?'} threads` : null, sp1));
    later.push(() => spark(sp1, {label: h + ' load per thread', name: 'Load per thread', lo: 0, hi: 0.25, fmt: n2,
      series: [{v: perT, color: 'var(--c1)', label: 'highest in the slot'}]}));
    const m = x.mem || {}, sp2 = E('div', 'vs');
    out.append(vital('Memory free', isNum(m.avail_gib) ? `${n1(m.avail_gib)} GiB` : ELL,
      isNum(m.total_gib) ? `of ${n0(m.total_gib)} GiB (${n0(m.avail_pct)}%)` : null, sp2));
    later.push(() => spark(sp2, {label: h + ' memory available', name: 'Memory available, GiB', lo: 0, hi: isNum(m.total_gib) ? m.total_gib : null,
      series: [{v: hs('mem_avail_gib'), color: 'var(--c1)', label: 'lowest in the slot'}]}));
    const lg = x.logins || {}, sp3 = E('div', 'vs');
    const ownS = hs('sessions_owner'), allS = hs('sessions_all');
    out.append(vital('Sessions', isNum(lg.sessions) ? n0(lg.sessions) : ELL,
      isNum(lg.people) ? plural(lg.people, 'person', 'people') : null, sp3));
    later.push(() => spark(sp3, {label: h + ' login sessions', name: 'Login sessions', lo: 0, fmt: n0,
      series: [{v: allS, color: 'var(--ink-2)', label: 'all, including the login screen'}, {v: ownS, color: 'var(--c7)', label: 'yours'}]}));
    for (const dk of (Array.isArray(x.disks) ? x.disks : [])) {
      out.append(vital('Disk ' + dk.mount, isNum(dk.used_pct) ? n0(dk.used_pct) + '% used' : ELL,
        isNum(dk.free_gib) ? n0(dk.free_gib) + ' GiB free' : null, E('div', 'vs', isNum(dk.used_pct) ? meter(dk.used_pct, 85, 97) : null)));
    }
    const pools = x.zfs ? (Array.isArray(x.zfs.pools) && x.zfs.pools.length ? x.zfs.pools : [x.zfs]) : [];
    for (const z of pools) {
      out.append(vital('Pool ' + (z.pool || ''), isNum(z.used_pct) ? n0(z.used_pct) + '% used' : ELL,
        [z.state || null, z.note ? ' · ' + z.note : ''], E('div', 'vs', isNum(z.used_pct) ? meter(z.used_pct, 85, 97) : null)));
    }
    const tp = x.temps || {};
    if (tp.cpu_c != null || tp.nvme_c != null) {
      out.append(vital('Temperature', [isNum(tp.cpu_c) ? `CPU ${n0(tp.cpu_c)} °C` : null, isNum(tp.cpu_c) && isNum(tp.nvme_c) ? ' · ' : '',
        isNum(tp.nvme_c) ? `NVMe ${n0(tp.nvme_c)} °C` : null], null, null, true));
    }
    const sd = x.systemd || {};
    if (sd.state) {
      const failed = Array.isArray(sd.failed) ? sd.failed : [];
      out.append(vital('systemd', [sd.state === 'running' ? E('span', 'ok-mark', '✓ ') : null, sd.state,
        failed.length ? ': ' + plural(failed.length, 'failed unit') : ''], failed.length ? failed.join(', ') : null, null, true));
    }
    return out;
  }
  function linkText(l) {
    if (l && l.down) return E('span', 'warn-text', 'down');
    if (!l || !l.speed) return ELL;
    const w = isNum(l.width) ? ' ×' + l.width : '', sp = String(l.speed).replace(/\.0 GT\/s/, ' GT/s');
    const full = l.ok !== false && (l.max_width == null || l.width === l.max_width) && (l.max_speed == null || l.speed === l.max_speed);
    return full ? [sp + w + ' ', E('span', 'ok-mark', '✓')]
      : E('span', 'warn-text', `${sp}${w} of ${String(l.max_speed || '?').replace(/\.0 GT\/s/, ' GT/s')} ×${l.max_width ?? '?'}`);
  }
  const sumObj = o => (o && typeof o === 'object' ? Object.values(o).reduce((s, v) => s + (isNum(v) ? v : 0), 0) : null);
  function gauge(c, r, stale) {
    const lo = 20, hi = 120, pct = v => ((Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo) * 100).toFixed(2) + '%';
    const st = c.static || {}, band = Array.isArray(st.idle_c) ? st.idle_c : null;
    const old = !!(r && isNum(r.at) && Date.now() - r.at > 3 * 36e5);  // over 3 hours: shown, but muted
    const g = E('div', 'gauge' + (stale || old ? ' stale-data' : ''));
    const read = E('div', 'g-read');
    if (r && isNum(r.die)) {
      read.append(E('span', null, E('b', null, `${n0(r.die)} °C`), ' die', isNum(r.dieMax) ? ` (hottest sensor ${n0(r.dieMax)})` : ''),
        E('span', null, SRC[r.source] || r.source || 'reading', ', ', agoSpan(r.at), old ? ' (old)' : ''));
    } else read.append(E('span', null, E('b', null, ELL), ' die'), E('span', null, c.excluded ? 'never read: the card is not touched' : 'no reading in the last 7 days'));
    const tr = E('div', 'g-track');
    const zone = (a, b, cls) => { const z = E('span', 'g-zone ' + cls); z.style.left = pct(a); z.style.width = ((b - a) / (hi - lo) * 100) + '%'; return z; };
    tr.append(zone(90, 100, 'w'), zone(100, 120, 'b'));
    if (band) { const bd = E('span', 'g-band'); bd.style.left = pct(band[0]); bd.style.width = ((band[1] - band[0]) / (hi - lo) * 100) + '%'; bd.title = `usual idle ${band[0]}–${band[1]} °C`; tr.append(bd); }
    const tk = E('span', 'g-tick'); tk.style.left = pct(65); tr.append(tk);
    if (r && isNum(r.die)) { const mk = E('span', 'g-mark'); mk.style.left = pct(r.die); tr.append(mk); }
    const sc = E('div', 'g-scale');
    [[20, '20', 'first'], [65, '65'], [90, '90'], [100, '100'], [120, '120 °C', 'last']].forEach(([v, t, cls]) => {
      const s = E('span', cls || null, t); s.style.left = pct(v); sc.append(s);
    });
    attrs(g, {role: 'img', 'aria-label': `die temperature ${r && isNum(r.die) ? n0(r.die) + ' °C' : 'unknown'}` +
      (band ? `; usual idle ${band[0]}–${band[1]} °C` : '') + '; 65 °C is where the governor holds 600 MHz; 90 and 100 °C are the warning and alarm marks'});
    g.append(read, tr, sc);
    return g;
  }
  function policyChip(st) {
    const p = st.policy, word = p === 'dvfs' ? 'DVFS' : p === 'pinned' ? 'PINNED 600' : p === 'fixed' ? 'FIXED 600' : p ? String(p).toUpperCase() : null;
    return word ? E('span', 'chip pol', word) : null;
  }
  function detailTable(rows) {
    const t = E('table', 'dtab');
    const tb = E('tbody');
    for (const [k, v, src] of rows) {
      const empty = v == null || v === '' || (Array.isArray(v) && !v.flat(Infinity).some(x => x != null && x !== false && x !== ''));
      tb.append(E('tr', null, E('td', null, k), E('td', null, empty ? ELL : v, src ? E('span', 'cellsub src', src) : null)));
    }
    t.append(tb);
    return E('div', 'table-wrap', t);
  }
  function cardTile(id) {
    const c = C[id] || {}, st = cardState(id), r = reading(c), sx = c.static || {}, host = H[hostOfCard(id)] || {};
    const stale = st.key === 'unknown';
    const tile = attrs(E('div', 'ct card' + (c.excluded ? ' excl' : '')), {'data-card': id, id: 'card-' + id});
    tile.append(E('div', 'ct-head', markSvg(id, 16), E('b', null, cardName(id, true)), E('span', 'ct-id', id), cardHealth(id), pill(st.key, st.word, st.extra, st.title)));
    if (c.excluded) tile.append(E('p', 'ct-note', 'Excluded (overheats): never touched; driver counters only.'));
    else if (stale) tile.append(E('p', 'ct-note', host.reachable === false || c.stale ? 'Last known state: the machine did not answer the latest check.'
      : `Last known state: this page's data is ${dur(ageMin())} old.`));
    tile.append(gauge(c, r, stale));
    const kv = E('dl', 'kv');
    const row = (k, ...v) => kv.append(E('dt', null, k), E('dd', null, ...v));
    const w = r && isNum(r.w) ? r.w : null, iw = Array.isArray(sx.idle_w) ? sx.idle_w : null;
    row('Board power', w != null ? `${n1(w)} W` : ELL, iw ? E('span', 'muted', ` · idle ${iw[0]}–${iw[1]} W`) : '',
      isNum(sx.tdp_w) ? E('span', 'muted', ` · TDP ${sx.tdp_w} W`) : '');
    row('Clock', r && isNum(r.mhz) ? `${n0(r.mhz)} MHz ` : '', policyChip(sx) || (r && isNum(r.mhz) ? '' : ELL));
    row('Firmware', sx.firmware || ELL);
    row('PCIe link', linkText(c.link));
    const ce = sumObj((c.errors || {}).ce), uce = sumObj((c.errors || {}).uce), cn = sumObj((c.errors || {}).ce_new), un = sumObj((c.errors || {}).uce_new);
    row('Card events', ce == null ? ELL : `${n0(ce)} corrected, ${n0(uce || 0)} uncorrected`,
      cn ? E('span', c.excluded ? 'muted' : 'warn-text', ` · +${n0(cn)} corrected since the last check`) : '',
      un ? E('span', 'warn-text', ` · +${n0(un)} uncorrected since the last check`) : '');
    const aer = c.aer || {};
    row('Root port', isNum(aer.port_per_h) ? `${n0(aer.port_per_h)} corrected errors/h` : ELL);
    tile.append(kv);
    const strip = E('div', 'strip48');
    tile.append(E('div', 'small muted', 'Held and used, last 48 hours'), strip);
    later.push(() => activityStrip(strip, id));
    tile.append(cardDetails(id, c, r, sx, host));
    return tile;
  }
  function cardDetails(id, c, r, sx, host) {
    const d = E('details', 'ct-more', E('summary', null, 'Every number and its source'));
    const er = c.errors || {}, fmtObj = o => (o && Object.keys(o).length ? Object.entries(o).map(([k, v]) => `${n0(v)} ${k}`).join(', ') : 'none');
    const kl = c.kernel_log || {}, act = c.activity || {}, aer = c.aer || {}, sm = c.sample || {}, gd = c.guard, l = c.link || {};
    const who = ((c.holder || {}).who || []).map(w => `${(!w.system && w.login) || 'system or CI'} on ${w.node || '?'}${isNum(w.etime_s) ? ', ' + dur(w.etime_s / 60) : ''}`).join('; ');
    const rows = [
      ['Firmware', [sx.firmware, sx.bl ? ` · BL ${sx.bl}` : '', sx.pmic ? ` · PMIC ${sx.pmic}` : '', sx.minion ? ` · minion ${sx.minion}` : ''], 'lab.json'],
      ['Clock policy', sx.clock, 'lab.json'],
      ['Usual idle', [Array.isArray(sx.idle_c) ? `${sx.idle_c[0]}–${sx.idle_c[1]} °C` : '', Array.isArray(sx.idle_w) ? `, ${sx.idle_w[0]}–${sx.idle_w[1]} W` : ''], 'lab.json'],
      ['Device', [isNum(c.devnum) ? `/dev/et${c.devnum}_*` : '', c.pci ? ` at ${c.pci}` : '', c.lock ? `, lock ${c.lock}` : '',
        c.lock_owner ? ` (owned by ${c.lock_owner})` : ''], 'sysfs devnum'],
      ['Power state', [c.power_state || '', c.enabled == null ? '' : c.enabled ? ', enabled' : ', disabled'], 'sysfs'],
      ['Link', l.speed ? `${l.speed} ×${l.width} (max ${l.max_speed} ×${l.max_width})` : '', 'sysfs current_link_*'],
      ['Holder', (c.holder && c.holder.held) || who ? who || 'held' : 'nobody', 'et-who'],
      ['Corrected events', fmtObj(er.ce), 'sysfs err_stats'],
      ['Uncorrected events', fmtObj(er.uce), 'sysfs err_stats'],
      ['New since last check', [fmtObj(er.ce_new), er.uce_new && Object.keys(er.uce_new).length ? '; uncorrected ' + fmtObj(er.uce_new) : ''], 'collector'],
      ['PCIe AER', [isNum(aer.card_total) ? `card ${n0(aer.card_total)}` : 'card —', isNum(aer.port_total) ? `, root port ${n0(aer.port_total)}` : '',
        isNum(aer.port_per_h) ? ` (${n0(aer.port_per_h)}/h)` : ''], 'sysfs aer_dev_correctable'],
      ['Kernel log', isNum(kl.error_events) ? `${n0(kl.error_events)} error events, ${n0(kl.refused_opens)} refused second opens, enabled ${n0(kl.enables)} times in the last ${n1(kl.window_h)} h` : '', 'et-lab-health'],
      ['Message counters', isNum(act.mgmt) ? `mgmt ${n0(act.mgmt)}, ops ${n0(act.ops)}${act.used ? '; moved since the last check' : ''}` : '', 'sysfs *_vq_stats'],
      ['Last used', T(act, 'last_used_at') ? [clock(T(act, 'last_used_at')), act.last_used_by ? ' by ' + act.last_used_by : ''] : '', 'collector'],
      ['Telemetry', r ? [isNum(r.die) ? `die ${n0(r.die)} °C` : '', isNum(r.dieMax) ? ` (max ${n0(r.dieMax)})` : '', isNum(r.pmic) ? `, PMIC ${n0(r.pmic)} °C` : '',
        isNum(r.w) ? `, ${n1(r.w)} W` : '', isNum(r.mhz) ? `, minion ${n0(r.mhz)} MHz` : '', isNum(r.noc) ? `, NoC ${n0(r.noc)}` : '', isNum(r.ddr) ? `, DDR ${n0(r.ddr)}` : '',
        ' at ', clock(r.at)] : 'none', r ? (SRC[r.source] || r.source) : ''],
      ['From', r && r.from ? E('code', null, r.from) : '', ''],
      ['Live sample', [sm.enabled ? 'on' : 'off', sm.result ? ` · ${sm.result}` : '', T(sm, 'last_try') ? ` · last try ${clock(T(sm, 'last_try'))}` : ''], 'collector'],
    ];
    if (gd) rows.push(['Clock guard', gd.present ? `marker ${gd.this_boot ? 'for this boot' : 'from an earlier boot'}: minion ${gd.minion_mhz} MHz, NoC ${gd.noc_mhz} MHz, TDP ${gd.tdp_w} W` : 'no marker', '/run marker']);
    if (Array.isArray(c.reasons) && c.reasons.length) rows.push(['Level', `${c.level || ELL}: ${c.reasons.join('; ')}`, 'collector']);
    if (c.stale || host.reachable === false) rows.push(['As of', clock(T(c, 'as_of') || T(host, 'last_ok_at')), 'last good check']);
    d.append(detailTable(rows));
    return d;
  }
  const pendingSince = k => { const t = T(k, 'pending_since'); return t ? clock(t) : (k.pending_since || '?'); };
  function hostFooter(h) {
    const x = H[h] || {}, f = E('div', 'mp-foot'), ex = x.experiments || {}, nw = x.nodewatch || {};
    const runs = Array.isArray(ex.running) ? ex.running : [], ll = ex.last_log;
    f.append(E('div', null, E('span', 'fl', 'Experiments'), runs.length ? ['running: ', runs.map(r => `${r.kind || 'run'} ${r.what || ''}`.trim() + (isNum(r.count) && r.count > 1 ? ` (×${r.count})` : '')).join(', ')] : 'none running',
      ll && ll.line ? E('div', 'small', 'last log line: ', E('span', 'mono', ll.line), ll.file ? ` (${ll.file}, ` : ' (', agoSpan(T(ll, 'at')), ')') : null,
      isNum(ex.others_device_procs) && ex.others_device_procs ? E('div', 'small', `${plural(ex.others_device_procs, 'device process', 'device processes')} of other users`) : null,
      isNum(ex.ci_jobs) && ex.ci_jobs ? E('div', 'small', plural(ex.ci_jobs, 'CI job') + ' running') : null));
    if (nw && nw.present !== false && (nw.beat_at || isNum(nw.beat_age_min))) {
      const beat = T(nw, 'beat_at');
      f.append(E('div', null, E('span', 'fl', 'nodewatch'), 'heartbeat ', beat ? agoSpan(beat) : dur(nw.beat_age_min) + ' ago',
        nw.tmux != null ? ` · tmux ${nw.tmux ? 'up' : 'none'}` : '', isNum(nw.claude) ? ` · ${plural(nw.claude, 'Claude process', 'Claude processes')}` : '',
        nw.linger != null ? ` · linger ${nw.linger ? 'on' : 'off'}` : '',
        Array.isArray(nw.gaps_48h) && nw.gaps_48h.length ? ` · ${plural(nw.gaps_48h.length, 'gap')} in 48 h` : '',
        nw.logins_48h && isNum(nw.logins_48h.in) ? ` · ${plural(nw.logins_48h.in, 'login')} in 48 h` : ''));
    }
    const hl = x.health || {};
    if (Array.isArray(hl.lines) && hl.lines.length) {
      const d = E('details', 'hf-more', E('summary', null, `et-lab-health${hl.rev ? ' rev ' + hl.rev : ''}: ${plural(hl.warn || 0, 'WARN', 'WARN')}, ${hl.info || 0} INFO, ${hl.lines.length} lines`));
      d.append(E('ul', 'hlines', hl.lines.map(l => E('li', l.level || '', E('span', 'hl-l ' + (l.level || ''), l.level || ''), E('span', 'hl-c', l.check || ''), E('span', 'hl-t', l.text || '')))));
      f.append(d);
    }
    const k = x.kernel || {}, mf = x.manifest || {}, ci = x.ci_runner, ch = x.chrony || {};
    const facts = [
      ['Kernel', [k.running || '', k.reboot_pending ? ` · reboot pending since ${pendingSince(k)}` : ''], 'uname'],
      ['Pending', Array.isArray(k.pending) && k.pending.length ? k.pending.join(', ') : '', 'reboot-required.pkgs'],
      ['Driver', mf.et_soc1 ? `et_soc1 ${mf.et_soc1}${mf.srcversion ? ', srcversion ' + mf.srcversion : ''}` : '', 'et-lab-manifest'],
      ['Runtime', mf.libetrt ? `libetrt ${mf.libetrt}` : '', 'et-lab-manifest'],
      ['CPU', [mf.cpu || '', x.power_profile ? ` · power profile ${x.power_profile}` : ''], 'et-lab-manifest'],
      ['Time', ch.synced == null ? '' : ch.synced ? `chrony synced${isNum(ch.offset_ms) ? ', offset ' + n1(ch.offset_ms) + ' ms' : ''}` : 'chrony not synced', 'et-lab-health'],
      ['CI runner', ci ? `${plural(ci.units || 0, 'unit')}, ${ci.active || 0} active, ${plural((isNum(ci.jobs_now) ? ci.jobs_now : ci.jobs) || 0, 'job')} running` : 'none', 'et-lab-health'],
      ['Probe', [x.via || '', isNum(x.took_ms) ? `, ${n1(x.took_ms / 1000)} s` : '', x.boot_id8 ? `, boot ${x.boot_id8}` : ''], 'collector'],
    ];
    f.append(E('details', 'hf-more', E('summary', null, 'Machine facts'), detailTable(facts)));
    return f;
  }
  function renderHosts() {
    const root = $('hostgrid');
    for (const h of HOSTS) {
      const x = H[h] || {}, stale = x.reachable === false || x.stale;
      const sec = attrs(E('section', 'mp card' + (stale ? ' is-stale' : '')), {'data-host': h, id: 'm-' + h});
      sec.append(E('div', 'mp-head', attrs(E('h3', null, h), {id: h}), hostPill(h)));
      const k = x.kernel || {};
      sec.append(E('div', 'mp-sub', E('span', null, [upText(x), k.running ? ' · kernel ' + k.running : ''].filter(Boolean).join('') || ELL),
        k.reboot_pending ? pill('info', 'REBOOT PENDING', null, 'since ' + pendingSince(k)) : null));
      if (x.reachable === false) {
        const nt = T(x, 'next_try_at');
        sec.append(E('div', 'mp-note ' + (x.error === 'approval needed' ? 'lv-warn' : 'lv-bad'), E('b', null, 'No answer: '), reachText(x),
          '. The numbers below are from then.', nt ? ` Next try about ${clock(nt)}.` : ''));
      }
      sec.append(E('div', 'sect', 'Vitals'), vitals(h));
      const cs = cardsOf(h);
      if (cs.length) sec.append(E('div', 'sect', cs.length > 1 ? 'Cards' : 'Card'), E('div', 'tiles', cs.map(cardTile)));
      sec.append(hostFooter(h));
      root.append(sec);
    }
  }
  function activityStrip(host, id) {
    const hold = series('cards', id, 'hold'), used = series('cards', id, 'used');
    if (!hold && !used) { host.append(E('span', 'small muted', 'no history')); return; }
    const runs = cardRuns(id);
    CK.frame(host, {minW: 120, maxW: 900, height: 18, label: cardName(id) + ': held and used, last 48 hours', draw(f) {
      const x = CK.lin(HT0, HEND, 1, f.W - 1), nodes = [];
      CK.el('rect', {class: 'tl-track', x: 1, y: 3, width: f.W - 2, height: 12, rx: 2}, f.svg);
      for (const r of runs) nodes.push(runMark(f, r, x(slotT(r.a)), x(slotT(r.b)), 3, 12, cardName(id)));
      CK.keynav(f, nodes);
    }});
  }

  /* ---- runs of one state along the 48-hour grid ---- */
  function runsOf(stateAt) {
    const out = [];
    for (let i = 0; i < HN; i++) {
      const s = stateAt(i), prev = out[out.length - 1];
      if (prev && prev.key === s.key && prev.who === s.who) prev.b = i + 1;
      else out.push(Object.assign({a: i, b: i + 1}, s));
    }
    return out;
  }
  function cardRuns(id) {
    const hold = series('cards', id, 'hold') || [], used = series('cards', id, 'used') || [];
    return runsOf(i => {
      const h = hold[i], u = used[i];
      if (h == null && u == null) return {key: 'nodata'};
      if (h) return {key: isOwner(h) ? 'ours' : 'other', who: h};
      if (u) return {key: 'used'};
      return {key: 'free'};
    });
  }
  const HOME = O.host || COL.host || 'aifoundry2';  // the owner's home machine: where tmux and Claude must live (§5)
  function hostRuns(h) {
    const up = series('hosts', h, 'up') || [], tmux = series('hosts', h, 'tmux'), cl = series('hosts', h, 'claude');
    const load = series('hosts', h, 'beats') || series('hosts', h, 'load');  // heartbeats per slot, else any nodewatch value
    const beat = i => !!(load && isNum(load[i]) && load[i] > 0);
    const home = h === HOME, hasNW = !!(load && load.some(v => isNum(v) && v > 0));
    const hasTmux = home && !!(tmux && tmux.some(v => v === 1)), hasCl = home && !!(cl && cl.some(v => isNum(v) && v > 0));
    return runsOf(i => {
      const u = up[i];
      if (u === 1 || u === true) {
        if ((hasTmux && tmux[i] === 0) || (hasCl && cl[i] === 0)) return {key: 'gone'};
        if (hasNW && !beat(i) && i < HN - 1) return {key: 'gap'};
        return {key: 'up'};
      }
      if (u === 'approval' || u === 2 || u === -1) return {key: 'approval'};
      if (u === 0 || u === false) return {key: 'down'};
      if (beat(i)) return {key: 'nw'};  // no check by the collector in this slot, but nodewatch's heartbeat ran
      return {key: 'nodata'};
    });
  }
  const RUNTEXT = {
    ours: r => `held by ${r.who} (you)`, other: r => `held by ${r.who}`, used: () => 'in use, with no holder at the check',
    free: () => 'free', nodata: () => 'no data (no check, or the machine did not answer)',
    up: () => 'answered', approval: () => 'no answer: Tailscale check approval needed', gap: () => 'answered; nodewatch heartbeat missing',
    down: () => 'no answer', gone: () => 'answered, but your tmux or Claude was gone (nodewatch)',
    nw: () => 'alive (nodewatch heartbeat; the collector did not check)',
  };
  const THIN = {free: 1, up: 1, nw: 1};
  function runMark(f, r, xa, xb, y, hgt, label) {
    const g = CK.el('g', null, f.svg), w = Math.max(1, xb - xa);
    if (r.key !== 'nodata') {
      const thin = THIN[r.key], hh = thin ? 3 : hgt;
      CK.el('rect', {class: 'tl-' + r.key, x: xa + (thin ? 0 : 0.5), y: y + (hgt - hh) / 2, width: Math.max(1, w - (thin ? 0 : 1)), height: hh, rx: thin ? 1 : 2}, g);
    }
    CK.el('rect', {class: 'ck-hit', x: xa, y: y - 3, width: w, height: hgt + 6}, g);
    const end = r.b >= HN ? 'now' : clock(slotT(r.b));
    CK.tip(f, g, `<b>${esc(label)}</b><br>${esc(RUNTEXT[r.key](r))}<br>${esc(clock(slotT(r.a)))} – ${esc(end)} (${esc(dur((r.b - r.a) * HSTEP / 6e4))})`);
    return g;
  }

  /* ================= people ================= */
  function renderPeople() {
    const t = $('ptable'), tb = t.tBodies[0];
    const list = sortedPeople(P);
    if (!list.length) { tb.append(E('tr', null, attrs(E('td', null, 'Nobody was seen on any lab machine.'), {colspan: 6}))); return; }
    for (const p of list) {
      const me = p.owner || isOwner(p.login), hs = p.hosts || {};
      const idle = idleOf(p);
      const procs = Object.values(hs).reduce((s, x) => s + (x && isNum(x.procs) ? x.procs : 0), 0);
      const holds = Array.isArray(p.card_holds) ? p.card_holds : [];
      const tr = E('tr', null,
        E('td', null, E('span', 'pl-login', p.login), me ? E('span', 'you', 'YOU') : null),
        E('td', null, E('span', 'st', presence(p.status), p.status || ELL)),
        E('td', null, Object.keys(hs).sort(natural).map(h => {
          const x = hs[h] || {};
          const old = x.stale || (Array.isArray(p.stale_hosts) && p.stale_hosts.includes(h));
          return E('span', 'mh', E('b', null, h), ': ', plural(x.sessions || 0, 'session'), x.closing ? ` (${x.closing} closing)` : '',
            isNum(x.ttys) ? `, ${plural(x.ttys, 'terminal')}` : '', old ? E('span', 'old-note', ' (old data)') : '');
        })),
        attrs(E('td', 'num', isNum(idle) ? dur(idle) : ELL), {'data-sort': isNum(idle) ? idle : 1e9}),
        E('td', null, holds.length ? holds.map(hd => E('span', 'mh', markSvg(hd.card, 11), ' ', cardName(hd.card), isNum(hd.etime_s) ? ', ' + dur(hd.etime_s / 60) : '')) : ELL),
        attrs(E('td', 'num', n0(procs), p.device_procs ? E('span', 'cellsub', `${plural(p.device_procs, 'device process', 'device processes')}`) : null), {'data-sort': procs}));
      tb.append(tr);
    }
    CK.stackTable(t);
    CK.sortTable(t, {filter: list.length > 3, filterLabel: 'Filter people'});
  }
  function renderOwner() {
    const root = $('owner'), cl = O.claudes || {}, ss = O.sessions || {};
    const c1 = E('div', 'card', E('h4', null, 'Claude logins ', E('span', 'small muted', '(claudes status)')));
    for (const a of (Array.isArray(cl.accounts) ? cl.accounts : [])) {
      const lapse = isNum(a.lapse_days) ? a.lapse_days : null;
      const lv = !a.logged_in || a.wrong_account ? 'bad' : lapse != null && lapse <= 7 ? 'warn' : 'ok';
      c1.append(E('div', 'acct', pill(lv, a.wrong_account ? 'WRONG ACCOUNT' : a.logged_in ? 'LOGGED IN' : 'LOGGED OUT'), E('span', null, E('b', null, 'Account ' + a.n),
        a.lapses ? ` · login lapses ${dateText(a.lapses)}${lapse != null ? ' (in ' + plural(lapse, 'day') + ')' : ''}` : ''),
        E('span', 'sub', [a.tmux ? `tmux ${a.tmux}` : '', a.server != null ? ` · server ${a.server ? 'up' : 'down'}` : '',
          isNum(a.phones) ? ` · ${plural(a.phones, 'phone')}` : '', isNum(a.sessions) ? ` · ${plural(a.sessions, 'session')}` : '',
          a.credentials_note ? ` · ${a.credentials_note}` : ''].join('').replace(/^ · /, ''))));
    }
    if (!(cl.accounts || []).length) c1.append(E('p', 'small muted', 'No claudes data.'));
    const pins = Array.isArray(cl.pins) ? cl.pins : [];
    if (pins.length) {
      c1.append(E('div', 'acct', pill(pins.every(p => p.running) ? 'ok' : 'warn', plural(pins.filter(p => p.running).length, 'PIN') + ' UP'),
        E('span', null, pins.map(p => `${p.window || p.id8} (account ${p.account}) ${p.running ? 'running' : 'down'}`).join(', '))));
    }
    const wd = cl.watchdog;
    if (wd) {
      const lr = T(wd, 'last_run'), age = lr ? (Date.now() - lr) / 6e4 : wd.age_min;
      c1.append(E('div', 'acct', pill(!wd.on ? 'bad' : age != null && age > 5 + ageMin() ? 'warn' : 'ok', wd.on ? 'WATCHDOG ON' : 'WATCHDOG OFF'),
        E('span', null, 'last run ', lr ? agoSpan(lr) : dur(wd.age_min) + ' ago')));
    }
    const tm = Array.isArray(cl.tmux) ? cl.tmux : [];
    if (tm.length) {
      c1.append(E('div', 'acct', pill('ok', plural(tm.length, 'TMUX SESSION', 'TMUX SESSIONS')),
        E('span', null, tm.map(t => `${t.name}${isNum(t.windows) ? ' (' + plural(t.windows, 'window') + (t.attached ? ', attached' : '') + ')' : ''}`).join(', '))));
    }
    const home = O.host || COL.host || 'aifoundry2', nws = O.nodewatch || {};
    for (const h of Object.keys(nws).sort((a, b) => (a === home ? -1 : b === home ? 1 : natural(a, b)))) {
      const nw = nws[h] || {}, main = h === home;
      const ok = !main || (nw.tmux && isNum(nw.claude) && nw.claude > 0), age = isNum(nw.beat_age_min) ? nw.beat_age_min : null;
      const lv = nw.stale ? 'unknown' : !ok || (age != null && age > 30) ? 'bad' : age != null && age > 5 ? 'warn' : 'ok';  // §5's owner rules
      c1.append(E('div', 'acct', pill(lv, main ? (ok ? 'TMUX UP' : 'TMUX OR CLAUDE GONE') : 'NODEWATCH'),
        E('span', null, `${h}: tmux ${nw.tmux ? 'up' : 'none'}, ${plural(nw.claude || 0, 'Claude process', 'Claude processes')}, linger ${nw.linger ? 'on' : 'off'}` +
          (isNum(nw.beat_age_min) ? `, heartbeat ${dur(nw.beat_age_min)} old` : '') + (nw.stale ? ' (old data)' : ''))));
    }
    if (T(cl, 'as_of')) c1.append(E('p', 'small muted', 'As of ', clock(T(cl, 'as_of')), '.'));

    const c2 = E('div', 'card', E('h4', null, 'Claude sessions ', E('span', 'small muted', '(spacesheep)')));
    const bm = ss.by_machine || {}, ms = Object.keys(bm).sort(natural);
    if (ms.length) {
      const cols = [['working', 'Working'], ['needs_you', 'Needs you'], ['idle', 'Idle'], ['done', 'Done']]
        .filter(([k], j) => j === 0 || j === 2 || ms.some(m => isNum((bm[m] || {})[k])));
      const t = E('table', 'mtab', E('thead', null, E('tr', null, E('th', null, 'Machine'), cols.map(([, l]) => E('th', 'num', l)), E('th', null, 'Last activity'))));
      const tb = E('tbody');
      for (const m of ms) {
        const r = bm[m] || {};
        tb.append(E('tr', null, E('td', null, m), cols.map(([k]) => E('td', 'num', n0(r[k] || 0))),
          E('td', null, T(r, 'last_at') ? agoSpan(T(r, 'last_at')) : ELL)));
      }
      t.append(tb);
      c2.append(E('div', 'table-wrap', t));
    } else c2.append(E('p', 'small muted', 'No session data.'));
    if (T(ss, 'as_of')) c2.append(E('p', 'small muted', 'As of ', clock(T(ss, 'as_of')), '.'));

    const c3 = E('div', 'card', E('h4', null, 'Sessions on the lab machines'));
    const lab = Array.isArray(ss.lab) ? ss.lab : [];
    const SLV = {working: 'ours', idle: 'unknown', done: 'excluded'};
    if (lab.length) {
      c3.append(E('ul', 'slist', lab.map(s => E('li', null, E('span', null, s.title || ELL), pill(SLV[s.state] || 'unknown', String(s.state || '?').toUpperCase()),
        E('span', 'sm', [s.machine, s.model, isNum(s.turns) ? plural(s.turns, 'turn') : null, T(s, 'started_at') ? `started ${clock(T(s, 'started_at'))}` : null,
          T(s, 'last_at') ? 'last ' : null].filter(Boolean).join(' · '), T(s, 'last_at') ? agoSpan(T(s, 'last_at')) : null)))));
    } else c3.append(E('p', 'small muted', 'No sessions on the lab machines.'));
    root.append(c1, c2, c3);
  }

  /* ================= last 48 hours ================= */
  function renderTimeline() {
    if (!HN || HT0 == null) { $('tl').append(E('p', 'small muted', 'No history yet.')); return; }
    const rows = [];
    for (const id of CK.cardsIn(HI.cards || {})) rows.push({kind: 'card', id, label: cardName(id), runs: cardRuns(id)});
    for (const h of HOSTS) if (series('hosts', h, 'up')) rows.push({kind: 'host', id: h, label: h, runs: hostRuns(h)});
    const col = k => `var(--c${k})`;
    CK.legend('tl-legend', [
      {key: 'ours', label: 'held by you', color: col(7), mark: 'box'},
      {key: 'other', label: 'held by someone else', color: col(5), mark: 'box'},
      {key: 'used', label: 'in use, no holder at the check', color: 'color-mix(in srgb,var(--ink-2) 50%,var(--surface))', mark: 'box'},
      {key: 'free', label: 'free', color: 'var(--axis)', mark: 'line'},
      {key: 'up', label: 'machine answered', color: 'color-mix(in srgb,var(--ok) 60%,var(--surface))', mark: 'line'},
      {key: 'nw', label: 'alive (nodewatch only)', color: 'color-mix(in srgb,var(--ok) 30%,var(--surface))', mark: 'line'},
      {key: 'approval', label: 'approval needed', color: 'color-mix(in srgb,var(--warn) 75%,var(--surface))', mark: 'box'},
      {key: 'down', label: 'no answer', color: 'var(--bad)', mark: 'box'},
      {key: 'gone', label: `your tmux or Claude gone (${HOME})`, color: 'var(--c2)', mark: 'box'},
      {key: 'gap', label: 'nodewatch gap', color: 'var(--muted)', mark: 'box'},
    ]);
    const nCards = rows.filter(r => r.kind === 'card').length;
    CK.frame('tl', {minW: 300, maxW: 1248, label: 'Cards and machines over the last 48 hours',
      height: W => 8 + rows.length * (W < 600 ? 34 : 24) + (nCards && nCards < rows.length ? 10 : 0) + 30,
      draw(f) {
        const nar = f.narrow, L = nar ? 4 : 168, R = 10, Tp = 8, B = 30, rowH = nar ? 34 : 24, bar = 12;
        const x = CK.lin(HT0, HEND, L, f.W - R);
        const yOf = k => Tp + k * rowH + (k >= nCards && nCards && nCards < rows.length ? 10 : 0);
        const ticks = timeTicks(HT0, HEND, nar ? 12 : 6), labs = [];
        const ga = CK.el('g', {'aria-hidden': 'true'}, f.svg);
        for (const t of ticks) {
          CK.el('line', {class: 'tl-vgrid', x1: x(t), x2: x(t), y1: Tp - 4, y2: f.H - B + 4}, ga);
          labs.push(CK.txt(ga, x(t), f.H - B + 18, tickLabel(t), new Date(t).getHours() === 0 ? 'lab-strong' : 'tick', 'middle'));
        }
        CK.inside(f, labs);
        if (nCards && nCards < rows.length) {
          const ys = yOf(nCards) - 6;
          CK.el('line', {class: 'tl-sep', x1: 0, x2: f.W, y1: ys, y2: ys}, ga);
        }
        rows.forEach((r, k) => {
          const y0 = yOf(k), by = nar ? y0 + 16 : y0 + (rowH - bar) / 2;
          const lg = CK.el('g', {'aria-hidden': 'true'}, f.svg);
          if (r.kind === 'card') CK.cardMark(lg, r.id, nar ? 8 : 10, nar ? y0 + 7 : by + bar / 2, 4);
          CK.txt(lg, nar ? 18 : 22, nar ? y0 + 11 : by + bar / 2 + 4, r.label, r.kind === 'card' ? 'lab-strong' : 'lab');
          CK.el('rect', {class: 'tl-track', x: L, y: by, width: f.W - R - L, height: bar, rx: 2}, f.svg);
          const nodes = r.runs.map(run => runMark(f, run, x(slotT(run.a)), x(slotT(run.b)), by, bar, r.label));
          CK.keynav(f, nodes);
        });
      }});
  }
  function readingsChart(key, hostId, legId, o) {
    const ids = CK.cardsIn(HI.cards || {}).filter(id => { const s = series('cards', id, key); return s && s.some(isNum); });
    if (!HN || !ids.length) { $(hostId).append(E('p', 'small muted', 'No readings in the last 48 hours.')); return; }
    let f = null;
    if (ids.length > 1) CK.legend(legId, CK.cardLegend(ids).map(it => Object.assign(it, {label: cardName(it.key)})), {toggle: true, onChange: keys => f && CK.showSeries(f, keys)});
    else CK.legend(legId, CK.cardLegend(ids).map(it => Object.assign(it, {label: cardName(it.key)})));
    const vals = ids.flatMap(id => series('cards', id, key).filter(isNum));
    const lo = Math.min(o.lo, Math.floor(Math.min(...vals) / 10) * 10), hi = Math.max(o.hi, Math.ceil(Math.max(...vals) / 10) * 10);
    f = CK.frame(hostId, {height: W => (W < 600 ? 190 : 220), label: o.label, draw(fr) {
      const L = 40, R = 12, Tp = 24, B = 30;
      const x = CK.lin(HT0, HEND, L, fr.W - R), y = CK.lin(lo, hi, fr.H - B, Tp);
      CK.axes(fr, {x, y, L, R, T: Tp, B, xt: timeTicks(HT0, HEND, fr.narrow ? 12 : 6), xfmt: tickLabel, yl: o.unit});
      for (const ref of o.refs || []) {
        if (ref.v < lo || ref.v > hi) continue;
        CK.el('line', {class: 'ref-line', x1: L, x2: fr.W - R, y1: y(ref.v), y2: y(ref.v)}, fr.svg);
        CK.inside(fr, [CK.txt(fr.svg, fr.W - R, y(ref.v) - 4, ref.label, 'tick', 'end')]);
      }
      const on = () => fr.seriesOn || ids;
      for (const id of ids) {
        const s = series('cards', id, key), g = CK.el('g', {'data-series': id}, fr.svg);
        let d = '', pen = false;
        s.forEach((v, i) => { if (isNum(v)) { d += (pen ? 'L' : 'M') + x(slotT(i) + HSTEP / 2).toFixed(1) + ',' + y(v).toFixed(1); pen = true; } else pen = false; });
        CK.el('path', {d, class: 'ser-line'}, g).style.stroke = CK.card(id).color;
        s.forEach((v, i) => { if (isNum(v)) CK.cardMark(g, id, x(slotT(i) + HSTEP / 2), y(v), 2.6); });
      }
      crossHover(fr, {n: HN, x: i => x(slotT(i) + HSTEP / 2), top: Tp, bottom: fr.H - B, label: o.label,
        valid: i => ids.some(id => on().includes(id) && isNum(series('cards', id, key)[i])),
        dots: i => ids.filter(id => on().includes(id)).map(id => { const v = series('cards', id, key)[i]; return isNum(v) ? [x(slotT(i) + HSTEP / 2), y(v), CK.card(id).color] : null; }),
        html: i => `<b>${esc(slotLabel(i))}</b><br>` + ids.filter(id => on().includes(id)).map(id => {
          const v = series('cards', id, key)[i]; return esc(cardName(id)) + ': ' + (isNum(v) ? esc(o.fmt(v)) : 'no reading');
        }).join('<br>')});
    }});
  }
  function renderSessions() {
    const hs = HOSTS.filter(h => series('hosts', h, 'sessions_all'));
    if (!HN || !hs.length) { $('ch-sess').append(E('p', 'small muted', 'No session history.')); return; }
    CK.legend('leg-sess', [{key: 'all', label: 'all, including the login screen', color: 'var(--ink-2)', mark: 'line'}, {key: 'own', label: 'yours', color: 'var(--c7)', mark: 'line'}]);
    const mx = Math.max(2, ...hs.flatMap(h => series('hosts', h, 'sessions_all').filter(isNum)));
    for (const h of hs) {
      const box = E('div', null, E('div', 'mt', h)), host = E('div');
      box.append(host);
      $('ch-sess').append(box);
      const all = series('hosts', h, 'sessions_all'), own = series('hosts', h, 'sessions_owner');
      CK.frame(host, {height: 118, minW: 260, label: h + ': login sessions, last 48 hours', draw(f) {
        const L = 26, R = 10, Tp = 8, B = 26;
        const x = CK.lin(HT0, HEND, L, f.W - R), y = CK.lin(0, mx, f.H - B, Tp);
        CK.axes(f, {x, y, L, R, T: Tp, B, xt: timeTicks(HT0, HEND, f.W < 420 ? 24 : 12), xfmt: tickLabel, yt: [0, Math.round(mx / 2), mx].filter((v, k, a) => a.indexOf(v) === k)});
        const xi = i => x(slotT(i) + HSTEP / 2);
        const line = (s, cls, color) => {
          if (!s) return;
          let d = '', pen = false;
          s.forEach((v, i) => { if (isNum(v)) { d += (pen ? 'L' : 'M') + xi(i).toFixed(1) + ',' + y(v).toFixed(1); pen = true; } else pen = false; });
          CK.el('path', {d, class: 'sp-line'}, f.svg).style.stroke = color;
        };
        line(all, 'all', 'var(--ink-2)');
        line(own, 'own', 'var(--c7)');
        crossHover(f, {n: HN, x: xi, top: Tp, bottom: f.H - B, label: h + ' login sessions',
          valid: i => isNum(all[i]) || (own && isNum(own[i])),
          dots: i => [isNum(all[i]) ? [xi(i), y(all[i]), 'var(--ink-2)'] : null, own && isNum(own[i]) ? [xi(i), y(own[i]), 'var(--c7)'] : null],
          html: i => `<b>${esc(h)}</b><br>${esc(slotLabel(i))}<br>all, including the login screen: ${esc(n0(all[i]))}<br>yours: ${esc(own ? n0(own[i]) : ELL)}`});
      }});
    }
  }

  /* ================= refresh (§4.4) ================= */
  function renderLive() {  // the parts that read PAGE_STALE: the strip, the KPIs and the machines' card tiles
    for (const id of ['strip', 'kpis', 'hostgrid']) { const e = $(id); while (e.firstChild) e.removeChild(e.firstChild); }
    renderStrip(); renderKpis(); renderHosts();
    later.splice(0).forEach(fn => fn());
    if (/^#(focus|card)=/.test(location.hash)) focusOn(location.hash, false);
  }
  function tick() {
    const st = ageMin() > STALE_MIN;
    if (st !== PAGE_STALE) { PAGE_STALE = st; renderLive(); }
    document.querySelectorAll('[data-ago]').forEach(s => { s.textContent = agoText(+s.dataset.ago); });
    renderHeader();
  }
  /* The viewer reloads the frame on every deploy; this covers a tab that missed one. Only inside the viewer (never under
     file://, so check_page sees a still page), never more than once in 5 minutes, and once in 30 when a reload brought back
     the same data (the collector is stopped). It loads the newest version: the origin's root, never the framed /v/<sha>/. */
  const IN_VIEWER = location.protocol === 'https:' && /\.spacesheep\.app$/.test(location.hostname);
  const KEY_R = 'labdash.reload';
  let canStore = false;
  try { sessionStorage.setItem('labdash.t', '1'); sessionStorage.removeItem('labdash.t'); canStore = true; } catch (_) { canStore = false; }
  function reloadNewest(why) {
    if (!IN_VIEWER) return;
    if (!canStore && why === 'stale') return;  // without a memory of the last reload, never reload on a timer
    const now = Date.now();
    let last = null;
    try { last = JSON.parse(sessionStorage.getItem(KEY_R) || 'null'); } catch (_) { last = null; }
    const gap = last && last.gen === GEN ? 30 * 6e4 : 5 * 6e4;
    if (last && now - last.t < gap) return;
    try { sessionStorage.setItem(KEY_R, JSON.stringify({t: now, gen: GEN, why})); } catch (_) { /* not remembered */ }
    location.replace(location.origin + '/' + location.hash);
  }
  function startTimers() {
    let hiddenAt = null, lastBeat = Date.now();
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') hiddenAt = Date.now();
      else if (hiddenAt != null) { const away = Date.now() - hiddenAt; hiddenAt = null; tick(); if (away > 2 * 6e4) reloadNewest('visible'); }
    });
    setInterval(tick, 30e3);  // first fires at 30 s: nothing moves in the first 6 s after load
    setInterval(() => {
      const now = Date.now(), jumped = now - lastBeat > 3 * 6e4;
      lastBeat = now;
      if (jumped) reloadNewest('sleep');
      else if (ageMin() > STALE_MIN) reloadNewest('stale');
    }, 60e3);
  }

  /* ================= build ================= */
  renderTheme();
  renderStatic();
  renderHeader();
  renderStrip();
  renderKpis();
  renderAlerts();
  renderHosts();
  renderPeople();
  renderOwner();
  renderTimeline();
  readingsChart('die_c', 'ch-die', 'leg-die', {lo: 40, hi: 100, unit: '°C', label: 'Die temperature by card, last 48 hours', fmt: v => n0(v) + ' °C',
    refs: [{v: 65, label: '65 °C: the governor holds 600 MHz'}, {v: 90, label: '90 °C'}]});
  readingsChart('board_w', 'ch-w', 'leg-w', {lo: 20, hi: 50, unit: 'W', label: 'Board power by card, last 48 hours', fmt: v => n1(v) + ' W', refs: []});
  renderSessions();
  later.forEach(fn => fn());
  if (/^#(focus|card)=/.test(location.hash)) requestAnimationFrame(() => focusOn(location.hash, false));
  window.addEventListener('hashchange', () => { if (/^#(focus|card)=/.test(location.hash)) focusOn(location.hash, true); });
  startTimers();
})();
