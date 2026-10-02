/* The lab dashboard (tools/lab/dashboard/DESIGN.md §4). D is the collector's data.json (§1), CK the report chart toolkit.
   Every string from the data goes into the page as text (textContent), never as HTML; tooltip HTML escapes it.
   Missing values are null and show as "—". The page never fetches anything: a new version arrives as a redeploy, and the
   spacesheep viewer reloads the tab (§4.4 covers what the viewer misses). */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const ELL = '—';
  const H = D.hosts || {}, C = D.cards || {}, P = Array.isArray(D.people) ? D.people : [];
  const HI = D.history || {}, COL = D.collector || {};
  const U = (D.usage && typeof D.usage === 'object') ? D.usage : null, UH = (U && U.hosts) || {}, UC = (U && U.cards) || {};
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
  /* Every time on the page is in the lab's own zone (lab.json "tz", America/Los_Angeles), named once in the header, whatever
     the viewer's zone: the collector's alert titles are in it too, so a clock time means the same everywhere on the page. */
  const LTZ = (D.usage && typeof D.usage === 'object' && D.usage.tz) || COL.lab_tz || null;
  function labFmt(o) {
    try { return new Intl.DateTimeFormat('en-GB', Object.assign({}, o, LTZ ? {timeZone: LTZ} : {})); } catch (_) { return new Intl.DateTimeFormat('en-GB', o); }
  }
  const F_HM = labFmt({hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
  const F_WD = labFmt({weekday: 'short'});
  const F_DM = labFmt({day: 'numeric', month: 'short'});
  const F_DAY = labFmt({year: 'numeric', month: '2-digit', day: '2-digit'});
  const dayKey = ms => F_DAY.format(ms);
  let ZONE = '';
  try {
    const z = new Intl.DateTimeFormat('en-US', Object.assign({timeZoneName: 'short'}, LTZ ? {timeZone: LTZ} : {})).formatToParts(GEN || Date.now()).find(x => x.type === 'timeZoneName');
    ZONE = z ? z.value : '';
  } catch (_) { /* no zone name */ }
  /* "13:12" today, "Tue 11:40" this week, "25 Sep 16:38" before (the lab's days). */
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
  /* Durations in seconds: "3 s", "4 min 10 s", then dur()'s "2 h 5 min". */
  function durS(s) {
    if (!isNum(s)) return ELL;
    s = Math.max(0, s);
    if (s < 1) return 'under 1 s';
    if (s < 59.5) return Math.round(s) + ' s';
    if (s < 600) { const r = Math.round(s), m = Math.floor(r / 60), x = r % 60; return m + ' min' + (x ? ' ' + x + ' s' : ''); }
    return dur(s / 60);
  }
  /* The lab-zone formatters of card use (the same zone as clock()). */
  const L_HM = F_HM, L_HMS = labFmt({hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'});
  const L_H = labFmt({hour: 'numeric', hourCycle: 'h23'}), L_WD = F_WD, L_D = labFmt({day: 'numeric'});
  const L_DAY = F_DAY, L_DM = labFmt({weekday: 'short', day: 'numeric', month: 'short'});
  const LZONE = ZONE;
  const labHour = ms => parseInt(L_H.format(ms), 10) % 24;
  /* A time in the lab's zone: "13:12" on the data's own day, "Tue 13:12" before it; with seconds when asked. */
  function lclock(ms, secs) {
    if (!isNum(ms)) return ELL;
    const t = (secs ? L_HMS : L_HM).format(ms);
    return L_DAY.format(ms) === L_DAY.format(isNum(GEN) ? GEN : Date.now()) ? t : L_WD.format(ms) + ' ' + t;
  }
  /* "2026-10-28" -> "28 Oct"; any other string as it is */
  const dateText = s => (/^\d{4}-\d\d-\d\d$/.test(String(s)) ? F_DM.format(new Date(s + 'T20:00:00Z')) : String(s));  // midday in the lab
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
    held: 'lv-held', free: 'lv-ok', missing: 'lv-bad'};
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
  const devOf = id => (isNum((C[id] || {}).devnum) ? C[id].devnum : 99);
  const cardsOf = h => CK.cardsIn(C).filter(id => hostOfCard(id) === h).sort((a, b) => devOf(a) - devOf(b));
  /* The page's one order of cards: by machine, as the strip and the machine panels, then by device number. */
  const CARDS = HOSTS.flatMap(cardsOf).concat(CK.cardsIn(C).filter(id => !HOSTS.includes(hostOfCard(id))));
  const inOrder = ids => CARDS.filter(id => ids.includes(id)).concat(ids.filter(id => !CARDS.includes(id)));
  function cardName(id, short) {
    const c = C[id] || {}, h = hostOfCard(id), many = cardsOf(h).length > 1;
    if (short) return many ? 'card ' + (isNum(c.devnum) ? c.devnum : id.replace(/^.*-c/, '')) : 'card';
    return many ? h + ' card ' + (isNum(c.devnum) ? c.devnum : id.replace(/^.*-c/, '')) : h;
  }
  /* Card marks are drawn in ink on this page (their shape and name identify the card), so that colour means a login
     wherever card use is shown; only the two readings charts colour cards, with the chart kit's registry colours. */
  const MARK_INK = 'var(--ink-2)';
  function markSvg(id, s) {
    s = s || 14;
    const svg = CK.el('svg', {width: s, height: s, viewBox: `0 0 ${s} ${s}`, 'aria-hidden': 'true', class: 'mk'});
    CK.cardMark(svg, id, s / 2, s / 2, s * 0.3, MARK_INK);
    return svg;
  }
  /* ---- one colour per login, the same everywhere on the page (card use, the 48-hour rows, the tables). Three hues: of
     the palette's categorical hues without the status ones (the warning amber, ok green and bad red), violet, aqua and
     orange are the only three that stay apart for any pair, in light and dark (the dataviz validator, all pairs), and
     any two logins can meet in a lane. The collector keeps each login's slot from run to run (usage.colors), so a colour
     follows its login; everyone else is "others", in --ref. Names always travel with the colour: legends, tooltips,
     labels and tables. ---- */
  const LOGIN_COLORS = ['var(--c7)', 'var(--c3)', 'var(--c2)'];
  const OTHER_COLOR = 'var(--ref)';
  const USER_COLOR = (function () {
    const m = {}, reg = U && U.colors && typeof U.colors === 'object' ? U.colors : null;
    if (reg) {
      for (const [u, k] of Object.entries(reg)) if (isNum(k) && k >= 0 && k < LOGIN_COLORS.length) m[u] = LOGIN_COLORS[k];
      return m;
    }
    // a data file without the collector's slots: the (at most three) logins with the most card time, alphabetically
    const score = {}, bump = (u, s) => { if (u && u !== '?') score[u] = (score[u] || 0) + s; };
    for (const id in UC) {
      const cu = UC[id] || {};
      for (const [u, e] of Object.entries(cu.users || {})) bump(u, 1e6 + ((e && e.held_s) || 0) * 10);
      for (const x of cu.now || []) bump(x.user, 1e6);
      for (const d of cu.daily || []) for (const [u, e] of Object.entries(d.users || {})) bump(u, (e && e.held_s) || 0);
    }
    for (const id in C) for (const w of ((C[id] || {}).holder || {}).who || []) if (!w.system) bump(w.login, 1e6);
    for (const id in (HI.cards || {})) for (const h of ((HI.cards[id] || {}).hold || [])) if (h && h !== 'system') bump(h, 1);
    Object.keys(score).sort((a, b) => score[b] - score[a] || natural(a, b)).slice(0, LOGIN_COLORS.length).sort(natural)
      .forEach((u, k) => { m[u] = LOGIN_COLORS[k]; });
    return m;
  })();
  const userColor = u => USER_COLOR[u] || OTHER_COLOR;
  const hasOthers = logins => logins.some(u => !USER_COLOR[u]);
  function swatch(u, size) {
    const s = size || 10, svg = CK.el('svg', {width: s, height: s, viewBox: `0 0 ${s} ${s}`, 'aria-hidden': 'true', class: 'mk'});
    CK.el('rect', {x: 0, y: 0, width: s, height: s, rx: 2}, svg).style.fill = userColor(u);
    return svg;
  }
  const DOING = {card: 'on a card', agent: 'AI agent', build: 'building', sim: 'simulator', python: 'Python', editor: 'editor', shell: 'shell only',
    other: 'other processes'};
  const doingText = list => (Array.isArray(list) && list.length ? list.map(k => DOING[k] || k).join(', ') : null);

  /* ---- a card's state: FREE, IN USE, EXCLUDED, NO DATA, MISSING ---- */
  function holderOf(c) {
    const who = (c.holder && Array.isArray(c.holder.who)) ? c.holder.who : [];
    const w = who.find(x => /^\/dev\//.test(String(x.node || ''))) || who[0];  // the node holder names the program
    return w ? Object.assign({}, w, w.system ? {login: null} : {}) : null;  // root or CI: "system or CI"
  }
  function holdSince(w) {
    const t = isNum(w.since_ms) ? w.since_ms : isNum(w.etime_s) && isNum(GEN) ? GEN - w.etime_s * 1000 : null;
    return t;
  }
  function cardState(id) {
    const c = C[id] || {}, host = H[hostOfCard(id)] || {};
    const w = holderOf(c);
    if (c.excluded && !w && host.reachable !== false) return {key: 'excluded', word: 'EXCLUDED', title: c.note || 'excluded from all work'};
    if (c.present === false) return {key: 'missing', word: 'MISSING', title: 'the driver has no bound device for this card'};
    if (host.reachable === false && !PAGE_STALE) {
      const seen = T(c, 'as_of') || T(host, 'last_ok_at'), st = stateOf(host);
      const was = w ? 'held by ' + (w.login || 'system or CI') : c.excluded ? 'excluded' : 'free';
      return {key: 'unknown', word: 'UNKNOWN:', extra: st === 'down' ? 'machine down' : st === 'approval needed' ? 'approval needed' : 'no answer', stale: true,
        title: seen ? `last known at ${clock(seen)}: ${was}` : 'no data from this machine yet'};
    }
    if (host.reachable === false || c.stale || PAGE_STALE) {
      const seen = (host.reachable === false || c.stale) ? (T(c, 'as_of') || T(host, 'last_ok_at')) : GEN;
      const was = w ? 'held by ' + (w.login || 'system or CI') : 'free';
      return {key: 'unknown', word: 'NO DATA', extra: seen ? 'was ' + was + ' at ' + clock(seen) : null, stale: true,
        title: PAGE_STALE ? 'this page\'s data is ' + dur(ageMin()) + ' old' : 'the machine did not answer the latest check'};
    }
    if (w) {
      const t = holdSince(w);
      return {key: c.excluded ? 'warn' : 'held', word: 'IN USE:', login: w.login || null,
        extra: [w.login || 'system or CI', w.comm || null, t ? 'since ' + lclock(t) : null].filter(Boolean).join(' · '),
        title: (c.excluded ? 'an excluded card in use; ' : '') + 'from et-who' + (w.from === 'et-usage' || isNum(w.since_ms) ? ' and et-usage' : '')};
    }
    if (c.holder && c.holder.held) return {key: 'held', word: 'IN USE'};
    if (c.excluded) return {key: 'excluded', word: 'EXCLUDED', title: c.note || 'excluded from all work'};
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
  const STATUS_RANK = {active: 0, idle: 1, 'processes only': 2, away: 3, unknown: 4};
  const pdClass = s => ({active: 'active', idle: 'idle', away: 'away', 'processes only': 'procs', unknown: 'unk'}[s] || 'unk');
  const presence = s => attrs(E('span', 'pd ' + pdClass(s)), {'aria-hidden': 'true'});
  function sortedPeople(list) {
    return list.slice().sort((a, b) => (STATUS_RANK[a.status] ?? 9) - (STATUS_RANK[b.status] ?? 9) || natural(String(a.login), String(b.login)));
  }
  /* Logged in on a machine: a session that is not closing, or an open terminal (a tmux pane outlives its login). */
  const loggedOn = (p, h) => { const x = p && p.hosts && p.hosts[h]; return !!(x && ((isNum(x.sessions) && x.sessions > 0) || (isNum(x.ttys) && x.ttys > 0))); };
  const loggedIn = p => Object.keys((p && p.hosts) || {}).some(h => loggedOn(p, h));
  const peopleOn = h => sortedPeople(P.filter(p => p && p.hosts && p.hosts[h]));
  function idleOf(p, h) {
    const hs = h ? [p.hosts[h]] : Object.values(p.hosts || {});
    const v = hs.map(x => x && x.idle_min).filter(isNum);
    return v.length ? Math.min(...v) : null;
  }
  /* A person's status on one machine (the collector's per-machine status), else their overall status. */
  const statusOn = (p, h) => (h && p.hosts && p.hosts[h] && p.hosts[h].status) || (h && p.hosts && p.hosts[h] ? 'processes only' : p.status);
  function personChip(p, h) {
    const idle = idleOf(p, h), st = statusOn(p, h) || 'unknown', dg = doingText(((p.hosts || {})[h] || {}).doing || p.doing);
    const t = st + (isNum(idle) ? ', idle ' + dur(idle) : '') + (dg ? '; ' + dg : '');
    const s = E('span', 'who', presence(st), p.login, E('span', 'vh', ', ' + t));
    s.title = t;
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
  function timeTicks(a, b, every) {  // whole hours of the lab's day (its offset is whole hours)
    const out = [];
    for (let t = Math.ceil(a / 36e5) * 36e5; t <= b; t += 36e5) if (labHour(t) % every === 0) out.push(t);
    return out;
  }
  const tickLabel = t => (labHour(t) === 0 ? F_WD.format(t) + ' ' + L_D.format(t) : F_HM.format(t));

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
    // the "Data as of ..." line was removed (2 Oct 2026): the stale banner below is the only age notice
    $('stale').hidden = !stale;
    if (stale) { fill('stale-age', dur(age)); fill('stale-hb', dur(HB_MIN)); fill('stale-host', COL.host || 'aifoundry2'); fill('stale-maint', COL.maintainer || 'its maintainer'); }
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
    fill('ab-maint', COL.maintainer || 'the maintainer'); fill('ab-maint2', COL.maintainer || 'the maintainer');
    // the space's visibility mode (DESIGN.md §3.3): public by the owner's decision of 30 September 2026, or private
    if (COL.visibility === 'public') {
      fill('ab-vis', 'The page is public (the owner\u2019s decision, 30 September 2026) and names the lab\u2019s users.');
      const hh = $('ab-halt-help'); if (hh) hh.hidden = true;
    } else if (COL.visibility === 'private') {
      fill('ab-vis', 'The page is private because it names the lab\u2019s users.');
    }
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

  /* ================= theme: follows the system (no selector since 2 Oct 2026; ?theme=light|dark|auto still works) ================= */
  function renderTheme() {
    const root = document.documentElement;
    try {
      const q = new URLSearchParams(location.search).get('theme');
      if (q === 'light' || q === 'dark') root.dataset.theme = q;
    } catch (_) { /* no query */ }
  }

  /* ================= overview strip ================= */
  /* The machine's own state (DESIGN.md §1.2): up, down (Tailscale: offline), unreachable, approval needed. */
  const stateOf = x => (x && x.state) || (x && x.reachable === true ? 'up' : x && x.reachable === false ? 'unreachable' : 'no data');
  const isUp = h => stateOf(H[h]) === 'up';
  const tsNow = x => !!(x && x.tailscale && isNum(x.tailscale.at_ms) && isNum(GEN) && Math.abs(x.tailscale.at_ms - GEN) < 6e4);
  function statePill(x) {
    const st = stateOf(x);
    if (st === 'down') return pill('bad', 'DOWN', null, 'Tailscale says the machine is offline');
    if (st === 'unreachable') {
      const local = x.via === 'local', lv = (x.fails_in_row || 0) >= 2 ? 'bad' : 'warn';
      if (local) return pill(lv, 'PROBE FAILED', null, 'the probe on the collector\'s own machine did not finish; the machine is up');
      return pill(lv, 'UNREACHABLE', null, tsNow(x) && x.tailscale.online ? 'online on Tailscale, but ssh did not answer' : 'ssh did not answer, and Tailscale\'s view was not available');
    }
    if (st === 'approval needed') return pill('warn', 'APPROVAL NEEDED', null, 'Tailscale SSH waits for a person to approve a check');
    return null;
  }
  function hostPill(h) {
    const al = alertsOfHost(h), b = count(al, 'bad'), w = count(al, 'warn'), x = H[h] || {};
    const sp = statePill(x);
    if (sp) return sp;
    if (b) return pill('bad', plural(b, 'PROBLEM', 'PROBLEMS'));
    if (w) return pill('warn', plural(w, 'WARNING', 'WARNINGS'));
    if (x.reachable === false) return pill('unknown', 'NO ANSWER');
    if (x.reachable !== true) return pill('unknown', 'NO DATA');
    if (x.level === 'bad' || x.level === 'warn') return pill(x.level, x.level === 'bad' ? 'PROBLEM' : 'WARNING');
    return pill('ok', 'OK');
  }
  /* "down since 14:33 (last answer 14:32; Tailscale last seen 14:33)" */
  function reachText(x) {
    const st = stateOf(x), since = isNum(x.down_since_ms) ? x.down_since_ms : T(x, 'state_since');
    const last = isNum(x.last_answer_ms) ? x.last_answer_ms : T(x, 'last_ok_at') || T(x, 'as_of'), tsl = x.tailscale_last_seen_ms;
    const word = st === 'down' ? 'down' : st === 'approval needed' ? 'approval needed' : x.via === 'local' ? 'the probe failed' : 'unreachable';
    const why = st === 'unreachable' && x.error ? ': ' + x.error : '';
    const paren = [last ? 'last answer ' + clock(last) : 'no answer yet', st === 'down' && isNum(tsl) ? 'Tailscale last seen ' + clock(tsl) : null].filter(Boolean).join('; ');
    return [word, since ? ' since ' + clock(since) : '', why, ' (', paren, ')'];
  }
  const lastKnown = x => { const t = isNum(x.last_answer_ms) ? x.last_answer_ms : T(x, 'last_ok_at'); return t ? clock(t) : null; };
  function upText(x) { return isNum(x.uptime_h) ? 'up ' + dur(x.uptime_h * 60) : null; }
  function renderStrip() {
    const root = $('strip');
    for (const h of HOSTS) {
      const x = H[h] || {}, st = stateOf(x);
      const box = E('div', 'mbox card' + (st === 'down' ? ' is-down lv-bad' : x.reachable === false ? ' is-away lv-warn' : ''));
      const a = focusLink(attrs(E('a', null, h), {href: '#m-' + h}), '#focus=' + h);
      box.append(E('div', 'mbox-head', a, hostPill(h)));
      const lp = x.load || {};
      box.append(E('div', 'mbox-sub', x.reachable === false ? reachText(x)
        : [upText(x), isNum(lp.per_thread) ? ' · load ' + n2(lp.per_thread) + ' per thread' : '', x.via === 'local' ? ' · the collector runs here' : '']));
      for (const id of cardsOf(h)) {
        const st = cardState(id), r = reading(C[id]);
        const hp = cardHealth(id), old = !!(r && isNum(r.at) && Date.now() - r.at > 3 * 36e5);
        const chip = focusLink(attrs(E('a', 'cchip' + (st.extra ? ' long' : '')), {href: '#card-' + id, 'aria-label': cardName(id) + ': ' + st.word +
          (st.extra ? ', ' + st.extra : '') + (hp ? ', ' + hp.textContent.toLowerCase() : '')}), '#card=' + id);
        chip.append(markSvg(id), E('span', 'cc-name', cardName(id, true)),
          pill(st.key, st.word, st.extra, st.title));
        chip.append(E('span', 'cc-temp' + (old ? ' old' : ''), hp, hp ? ' ' : '', C[id].excluded ? 'never touched; driver counters only'
          : r && isNum(r.die) ? [old ? 'last reading: ' : '', `die ${n0(r.die)} °C`, isNum(r.w) ? ` · ${n1(r.w)} W` : '', ' · ', agoSpan(r.at)] : 'no temperature reading'));
        box.append(chip);
      }
      const ppl = peopleOn(h);
      if (!isUp(h) && H[h]) {
        const lk = lastKnown(x);
        box.append(E('div', 'logins is-old', E('span', 'small', 'People: unknown now' + (lk ? `; at ${lk}: ` : '')), lk ? (ppl.length ? ppl.map(p => personChip(p, h)) : E('span', 'small muted', 'nobody')) : null));
      } else box.append(E('div', 'logins', ppl.length ? ppl.map(p => personChip(p, h)) : E('span', 'small muted', 'nobody seen')));
      root.append(box);
    }
    // what the marks on the people's chips mean (a title alone reaches neither touch nor the keyboard)
    const lg = $('pd-legend');
    if (lg) while (lg.firstChild) lg.removeChild(lg.firstChild);
    if (lg) lg.append(E('span', 'pdl', 'People:'), ...[['active', 'active: a terminal used in the last 30 min'], ['idle', 'idle'], ['away', 'away: a day or more'],
      ['processes only', 'processes only: no login, no terminal']].map(([k, t]) => E('span', 'pdl', presence(k), t)),
      E('span', 'pdl', 'greyed: last known (machine not answering)'));
  }

  /* ================= KPIs ================= */
  function renderKpis() {
    const k = (lab, val, sub) => E('div', 'kpi card', E('div', 'lab', lab), E('div', 'val', val), E('div', 'sub', sub || ELL));
    const ans = HOSTS.filter(h => (H[h] || {}).reachable === true);
    const miss = HOSTS.filter(h => (H[h] || {}).reachable !== true).map(h => { const x = H[h] || {}; return x.reachable === false ? `${h} ${stateOf(x).toUpperCase()}` + (isNum(x.down_since_ms) ? ` since ${clock(x.down_since_ms)}` : '') : h + ': no data'; });
    const usable = CARDS.filter(id => !(C[id] || {}).excluded);
    const states = CARDS.map(id => [id, cardState(id)]);
    const inUse = states.filter(([id, s]) => s.word.startsWith('IN USE') && !(C[id] || {}).excluded);
    const exclUsed = states.filter(([id, s]) => s.word.startsWith('IN USE') && (C[id] || {}).excluded);
    const parts = inUse.map(([id, s]) => `${s.login || 'someone'} on ${cardName(id)}`);
    exclUsed.forEach(([id, s]) => parts.push(`${s.login || 'someone'} on the excluded ${cardName(id)}`));
    const unk = states.filter(([id, s]) => s.key === 'unknown' && !(C[id] || {}).excluded).length; if (unk) parts.push(unk + ' no data');
    const excl = CARDS.length - usable.length; if (excl && !exclUsed.length) parts.push(excl + ' excluded');
    // the light counts current alerts only: the last known data of a machine that is not answering is counted apart
    const cur = LIVE.filter(a => !a.stale), b = count(cur, 'bad'), w = count(cur, 'warn'), inf = count(cur, 'info'), kn = ALERTS.length - LIVE.length;
    const old = LIVE.length - cur.length;
    const upHosts = HOSTS.filter(h => (H[h] || {}).reachable === true);
    const onLab = P.filter(p => upHosts.some(h => p.hosts && p.hosts[h]));
    const logged = onLab.filter(p => upHosts.some(h => loggedOn(p, h))), act = onLab.filter(p => upHosts.some(h => statusOn(p, h) === 'active' && p.hosts[h]));
    const perHost = HOSTS.map(h => {
      if ((H[h] || {}).reachable !== true) return `${h} unknown (${stateOf(H[h])})`;
      return `${h} ${P.filter(p => loggedOn(p, h)).length}`;
    });
    const procsOnly = onLab.length - logged.length;
    // what the people on the machines that answered are doing (a person with several kinds counts in each)
    const dc = {};
    for (const p of onLab) for (const d of (Array.isArray(p.doing) ? p.doing : [])) if (!['card', 'shell', 'other'].includes(d)) dc[d] = (dc[d] || 0) + 1;
    const doing = Object.keys(dc).sort((a, b) => dc[b] - dc[a] || Object.keys(DOING).indexOf(a) - Object.keys(DOING).indexOf(b)).slice(0, 3)
      .map(d => `${DOING[d]} ${dc[d]}`);
    const knownCards = usable.length - unk;
    $('kpis').append(
      k('Machines answering', `${ans.length} of ${HOSTS.length}`, miss.length ? miss.join('; ') : 'all answered the last check'),
      k('People logged in', String(logged.length), perHost.join(' · ') + (procsOnly > 0 ? `; ${procsOnly} more with processes only` : '')),
      k('Active now', String(act.length), 'a terminal used in the last 30 min' + (doing.length ? '; running: ' + doing.join(' · ') : '')),
      k('Cards in use now', knownCards > 0 ? `${inUse.length} of ${knownCards}` + (unk ? ' known' : '') : 'unknown', parts.join(' · ') || 'all free'),
      usageKpi(k),
      k('Alerts', b ? plural(b, 'problem') : w ? plural(w, 'warning') : 'none',
        `${plural(b, 'problem')} · ${plural(w, 'warning')} · ${plural(inf, 'note')} · ${kn} known` + (old ? ` · ${old} from last known data` : '')));
  }
  function usageKpi(k) {
    if (!U) return k('Card use, last 24 h', ELL, 'no card-use data');
    const ids = CARDS.filter(id => (UC[id] || {}).logged);
    const people = new Set(), notLogged = HOSTS.filter(h => !['running', 'stale'].includes((UH[h] || {}).logger));
    let held = 0, cards = 0;
    for (const id of ids) {
      const cu = UC[id];
      Object.keys(cu.users || {}).forEach(u => { if (u !== '?') people.add(u); });
      if (isNum(cu.held_s) && cu.held_s > 0) { held += cu.held_s; cards++; }
    }
    const val = ids.length ? (people.size ? plural(people.size, 'person', 'people') : held > 0 ? 'unseen users only' : 'nobody') : 'not logged';
    const sub = (ids.length ? `${durS(held)} held on ${plural(cards, 'card')}` : 'no machine logs card use yet') +
      (notLogged.length && ids.length ? `; not logged on ${notLogged.join(', ')}` : '');
    return k('Card use, last 24 h', val, sub);
  }

  /* ================= alerts ================= */
  const AWORD = {bad: 'PROBLEM', warn: 'WARNING', info: 'NOTE'};
  function scopeOf(a) {
    if (a.card) return E('span', 'scope', markSvg(a.card, 12), cardName(a.card));
    if (a.host) return E('span', 'scope', a.host);
    return E('span', 'scope', {people: 'people', collector: 'the collector', lab: 'the lab'}[a.scope] || a.scope || ELL);
  }
  function alertRow(a, minor) {
    const since = T(a, 'since');
    const d = E('details', 'al ' + (LV[a.level] || 'lv-info') + (minor ? ' minor' : ''));
    d.append(E('summary', null, pill(a.level, AWORD[a.level] || String(a.level || '').toUpperCase()), scopeOf(a), E('span', 'al-title', a.title || a.id),
      E('span', 'al-since', since ? ['raised ', clock(since)] : '', a.stale ? ' (last known data)' : '')));
    const body = E('div', 'al-body');
    if (a.detail) body.append(E('p', null, a.detail));
    if (a.known) body.append(E('p', null, E('b', null, 'Known condition: '), typeof a.known === 'string' ? a.known : 'listed in lab.json'));
    if (a.ack) {
      const k = typeof a.ack === 'object' ? a.ack : {note: String(a.ack)}, until = T(k, 'until');
      body.append(E('p', null, E('b', null, 'Acknowledged'), k.note ? ': ' + k.note : '', until ? ` (until ${clock(until)})` : ''));
    }
    body.append(E('p', 'small', 'Source: ', a.source || ELL, since ? ['; raised ', clock(since), ' (', agoSpan(since), ')'] : '',
      '. ID ', E('code', null, a.id), '.'));
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
    const allS = hs('sessions_all');
    out.append(vital('Sessions', isNum(lg.sessions) ? n0(lg.sessions) : ELL,
      isNum(lg.people) ? plural(lg.people, 'person', 'people') : null, sp3));
    later.push(() => spark(sp3, {label: h + ' login sessions', name: 'Login sessions', lo: 0, fmt: n0,
      series: [{v: allS, color: 'var(--ink-2)', label: 'all, including the login screen'}]}));
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
    if (c.excluded) tile.append(E('p', 'ct-note', 'Excluded (out of service): never touched; driver counters only.'));
    else if (stale) tile.append(E('p', 'ct-note', host.reachable === false || c.stale ? (lastKnown(host) ? `Last known at ${lastKnown(host)}: the machine is ${stateOf(host) === 'down' ? 'down' : 'not answering'}; nothing below is current.`
      : `No data from this machine yet: it is ${stateOf(host) === 'down' ? 'down' : 'not answering'}.`)
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
    const cu = UC[id] || {}, strip = E('div', 'strip48');
    if (cu.logged) {
      // the card's own lane of "Card use, last 24 hours", smaller
      const a = focusLink(attrs(E('a', null, 'Card use'), {href: '#card-use'}), '#card-use');
      tile.append(E('div', 'small muted', usageSentence(id, true), ' (', a, ')'), strip);
      later.push(() => usageStrip(strip, id));
    } else {
      // when no machine logs card use, Card use says so once; here only the machine that lacks it while others have it
      tile.append(E('div', 'small muted', 'Held at the 10-minute checks, last 48 hours', ANY_LOGGED ? [' (', notLoggedText(hostOfCard(id)), ')'] : ''), strip);
      later.push(() => activityStrip(strip, id));
    }
    tile.append(cardDetails(id, c, r, sx, host));
    return tile;
  }
  function cardDetails(id, c, r, sx, host) {
    const d = E('details', 'ct-more', E('summary', null, 'Every number and its source'));
    const er = c.errors || {}, fmtObj = o => (o && Object.keys(o).length ? Object.entries(o).map(([k, v]) => `${n0(v)} ${k}`).join(', ') : 'none');
    const kl = c.kernel_log || {}, act = c.activity || {}, aer = c.aer || {}, sm = c.sample || {}, gd = c.guard, l = c.link || {};
    const who = ((c.holder || {}).who || []).map(w => `${(!w.system && w.login) || 'system or CI'}${w.comm ? ' (' + w.comm + ')' : ''} on ${w.node || '?'}${isNum(w.etime_s) ? ', ' + dur(w.etime_s / 60) : ''}`).join('; ');
    const cu = UC[id] || {}, lastIv = (cu.intervals || []).reduce((b, iv) => (!b || iv.end_ms > b.end_ms ? iv : b), null);
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
      cu.logged ? ['Last used', lastIv ? [lastIv.open ? 'now' : lclock(lastIv.end_ms), ' by ', lastIv.user, ` (${LZONE || 'lab time'})`] : `not in the last ${U.hours || 24} h`, 'et-usage']
        : ['Last used', T(act, 'last_used_at') ? [clock(T(act, 'last_used_at')), act.last_used_by ? ' by ' + act.last_used_by : ''] : '', 'collector'],
      ['Card-use log', cu.logged ? `${usageSentence(id, true)}` : notLoggedText(hostOfCard(id)), 'et-usage'],
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
    const x = H[h] || {}, f = E('div', 'mp-foot'), nw = x.nodewatch || {};
    const here = P.filter(p => loggedOn(p, h)), act = here.filter(p => statusOn(p, h) === 'active');
    const dp = x.device_procs, cij = x.ci_jobs;
    if (x.reachable === false) f.append(E('div', null, E('span', 'fl', 'Now'), `unknown (${stateOf(x)})`, lastKnown(x) ? E('span', 'old-note', ` · at ${lastKnown(x)}: ${plural(here.length, 'person', 'people')} logged in`) : ''));
    else f.append(E('div', null, E('span', 'fl', 'Now'), `${plural(here.length, 'person', 'people')} logged in`, here.length ? ` (${act.length} active)` : '',
      isNum(dp) ? ` · ${dp ? plural(dp, 'device process', 'device processes') + (isNum(x.device_people) ? ` of ${plural(x.device_people, 'person', 'people')}` : '') : 'no device process'}` : '',
      isNum(cij) ? ` · ${cij ? plural(cij, 'CI job') + ' running' : 'no CI job'}` : ''));
    const uh = UH[h];
    if (uh && (ANY_LOGGED || uh.logger !== 'not installed')) f.append(E('div', null, E('span', 'fl', 'Card-use log'), loggerText(h)));
    if (nw && nw.present !== false && (nw.beat_at || isNum(nw.beat_age_min))) {
      const beat = T(nw, 'beat_at');
      f.append(E('div', null, E('span', 'fl', 'nodewatch'), 'heartbeat ', beat ? agoSpan(beat) : dur(nw.beat_age_min) + ' ago',
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
      if (x.reachable === false) {
        // a machine that is not answering: its last known uptime and kernel, never read as current
        const lk = lastKnown(x);
        sec.append(E('div', 'mp-sub', E('span', null, lk ? `last known, at ${lk}: ` + ([upText(x), k.running ? 'kernel ' + k.running : '',
          k.reboot_pending ? 'reboot pending' : ''].filter(Boolean).join(' · ') || ELL) : 'no data from this machine yet')));
      } else {
        sec.append(E('div', 'mp-sub', E('span', null, [upText(x), k.running ? ' · kernel ' + k.running : ''].filter(Boolean).join('') || ELL),
          k.reboot_pending ? pill('info', 'REBOOT PENDING', null, 'since ' + pendingSince(k)) : null));
      }
      if (x.reachable === false) {
        const nt = T(x, 'next_try_at'), st = stateOf(x), lk = lastKnown(x);
        sec.append(E('div', 'mp-note ' + (st === 'down' || (x.fails_in_row || 0) >= 2 ? 'lv-bad' : 'lv-warn'), E('b', null, st === 'down' ? 'DOWN: ' : st === 'approval needed' ? 'Approval needed: ' : 'Unreachable: '), reachText(x),
          '. ', lk ? `Everything below is the last known, at ${lk}, not the present.` : 'No data from this machine yet.', nt && st === 'approval needed' ? ` Next try about ${clock(nt)}.` : ''));
      }
      if (isNum(x.rebooted_at_ms)) {
        const af = x.reboot_after;
        if (af && typeof af === 'object') {
          const t0 = isNum(af.since_ms) ? af.since_ms : af.last_ok_ms;
          sec.append(E('div', 'mp-note lv-warn', E('b', null, 'Rebooted '), clock(x.rebooted_at_ms), `, after being ${af.state === 'down' ? 'down' : 'unreachable'}`,
            isNum(t0) ? ` since ${clock(t0)}` : '', isNum(x.reboot_seen_ms) ? `; back at ${clock(x.reboot_seen_ms)}` : '', ': an outage, not a planned reboot.'));
        } else if (x.reboot_planned == null) {
          sec.append(E('div', 'mp-note lv-info', E('b', null, 'Rebooted '), clock(x.rebooted_at_ms), ', before the dashboard first saw this boot: whether it was planned is not known.'));
        } else {
          sec.append(E('div', 'mp-note ' + (x.reboot_planned ? 'lv-info' : 'lv-warn'), E('b', null, 'Rebooted '), clock(x.rebooted_at_ms), x.reboot_planned ? ' (a reboot was pending).' : ', unplanned: no reboot was pending before it.'));
        }
      }
      sec.append(E('div', 'sect', x.reachable === false && lastKnown(x) ? `Vitals (last known at ${lastKnown(x)})` : 'Vitals'), vitals(h));
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
      if (h) return {key: 'held', who: h};
      if (u) return {key: 'used'};
      return {key: 'free'};
    });
  }
  function hostRuns(h) {
    const up = series('hosts', h, 'up') || [];
    const load = series('hosts', h, 'beats') || series('hosts', h, 'load');  // heartbeats per slot, else any nodewatch value
    const beat = i => !!(load && isNum(load[i]) && load[i] > 0);
    const hasNW = !!(load && load.some(v => isNum(v) && v > 0));
    return runsOf(i => {
      const u = up[i];
      if (u === 1 || u === true) {
        if (hasNW && !beat(i) && i < HN - 1) return {key: 'gap'};
        return {key: 'up'};
      }
      if (u === 'approval' || u === 2 || u === -1) return {key: 'approval'};
      if (u === 3) return {key: 'down'};
      if (u === 0 || u === false) return {key: 'noans'};
      if (beat(i)) return {key: 'nw'};  // no check by the collector in this slot, but nodewatch's heartbeat ran
      return {key: 'nodata'};
    });
  }
  const RUNTEXT = {
    held: r => `held by ${r.who === 'system' ? 'system or CI' : r.who} at the check`, used: () => 'in use, with no holder at the check',
    free: () => 'free', nodata: () => 'no data (no check, or the machine did not answer)',
    up: () => 'answered', approval: () => 'no answer: Tailscale check approval needed', gap: () => 'answered; nodewatch heartbeat missing',
    down: () => 'machine down (Tailscale: offline)', noans: () => 'no answer: ssh timed out or failed (the machine may be up)', nw: () => 'alive (nodewatch heartbeat; the collector did not check)',
  };
  const THIN = {free: 1, up: 1, nw: 1};
  function runMark(f, r, xa, xb, y, hgt, label) {
    const g = CK.el('g', null, f.svg), w = Math.max(1, xb - xa);
    if (r.key !== 'nodata') {
      const thin = THIN[r.key], hh = thin ? 3 : hgt;
      const bar = CK.el('rect', {class: 'tl-' + r.key, x: xa + (thin ? 0 : 0.5), y: y + (hgt - hh) / 2, width: Math.max(1, w - (thin ? 0 : 1)), height: hh, rx: thin ? 1 : 2}, g);
      if (r.key === 'held') bar.style.fill = r.who === 'system' ? OTHER_COLOR : userColor(r.who);
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
    if (!list.length) { tb.append(E('tr', null, attrs(E('td', null, 'Nobody was seen on any lab machine.'), {colspan: 8}))); return; }
    for (const p of list) {
      const hs = p.hosts || {}, idle = idleOf(p);
      const procs = Object.values(hs).reduce((s, x) => s + (x && isNum(x.procs) ? x.procs : 0), 0);
      const holds = Array.isArray(p.card_holds) ? p.card_holds : [];
      const c24 = Array.isArray(p.cards_24h) ? p.cards_24h : [];
      const dg = Array.isArray(p.doing) ? p.doing : null, many = Object.keys(hs).length > 1;
      const held24 = c24.reduce((s, x) => s + (isNum(x.held_s) ? x.held_s : 0), 0);
      const tr = E('tr', null,
        E('td', null, E('span', 'pl-login', p.login)),
        E('td', null, E('span', 'st', presence(p.status), p.status || ELL), p.status === 'unknown' ? E('span', 'old-note', ' (its machine is not answering)') : ''),
        E('td', null, dg && dg.length ? E('span', 'dgs', dg.map(k => E('span', 'dg' + (k === 'card' ? ' dg-card' : ''), DOING[k] || k))) : ELL),
        E('td', null, Object.keys(hs).sort(natural).map(h => {
          const x = hs[h] || {};
          const old = x.stale || (Array.isArray(p.stale_hosts) && p.stale_hosts.includes(h));
          const dh = many ? doingText(x.doing) : null;
          return E('span', 'mh', E('b', null, h), ': ', plural(x.sessions || 0, 'session'), x.closing ? ` (${x.closing} closing)` : '',
            isNum(x.ttys) ? `, ${plural(x.ttys, 'terminal')}` : '', dh ? ` · ${dh}` : '', old ? E('span', 'old-note', ' (old data)') : '');
        })),
        attrs(E('td', 'num', isNum(idle) ? dur(idle) : ELL), {'data-sort': isNum(idle) ? idle : 1e9}),
        E('td', null, holds.length ? holds.map(hd => {
          const since = isNum(hd.since_ms) ? hd.since_ms : isNum(hd.etime_s) && isNum(GEN) ? GEN - hd.etime_s * 1000 : null;
          return E('span', 'mh', markSvg(hd.card, 11), ' ', cardName(hd.card), hd.comm ? ' · ' + hd.comm : '', since ? ' · since ' + lclock(since) : '',
            !isUp(hostOfCard(hd.card)) ? E('span', 'old-note', ' (last known)') : '');
        }) : ELL),
        attrs(E('td', null, c24.length ? c24.map(x => E('span', 'mh', swatch(p.login), ' ', cardName(x.card), ': ', durS(x.held_s),
          isNum(x.runs) ? `, ${plural(x.runs, 'run')}` : '')) : ELL), {'data-sort': held24}),
        attrs(E('td', 'num', n0(procs), p.device_procs ? E('span', 'cellsub', `${plural(p.device_procs, 'device process', 'device processes')}`) : null), {'data-sort': procs}));
      for (const c of tr.cells) if (c.textContent.trim() === ELL) c.classList.add('none');  // left out of the phone layout
      tb.append(tr);
    }
    CK.stackTable(t);
    CK.sortTable(t, {filter: list.length > 3, filterLabel: 'Filter people'});
  }

  /* ================= card use, last 24 hours (et-usage) ================= */
  const ANY_LOGGED = CARDS.some(id => (UC[id] || {}).logged);  // at least one machine logs card use
  const US0 = U && isNum(U.start_ms) ? U.start_ms : null, US1 = U && isNum(U.end_ms) ? U.end_ms : null;
  const UHOURS = (U && isNum(U.hours)) ? U.hours : 24;
  function loggerText(h) {
    const uh = UH[h] || {}, lg = uh.logger, sk = (isNum(uh.skipped) && uh.skipped > 0 ? `; ${plural(uh.skipped, 'unreadable log line')} skipped` : '') +
      (uh.log_error ? `; could not read part of its log (${uh.log_error})` : '') +
      (isNum(uh.truncated_before_ms) ? `; read only from ${lclock(uh.truncated_before_ms)} (the log is larger than et-usage reads at once)` : '');
    const asof = (uh.stale && isNum(uh.as_of_ms) ? ` (as of ${clock(uh.as_of_ms)})` : '') + sk;
    if (lg === 'running' && uh.paused) return `paused: ${uh.paused}; it runs, but writes no records until there is room` + asof;
    if (lg === 'running') return 'running' + (isNum(uh.logging_since_ms) ? `, its log begins ${lclock(uh.logging_since_ms)}` : '') + asof;
    if (lg === 'stale') return (isNum(uh.stopped_ms) ? `stopped at ${lclock(uh.stopped_ms)} (a clean stop)` : `stopped: last alive ${isNum(uh.alive_ms) ? lclock(uh.alive_ms) : '?'}`) +
      (uh.paused ? `, while paused: ${uh.paused}` : '') + asof;
    if (lg === 'not installed') return 'not installed (et-usage)' + asof;
    if (lg === 'not running') return 'installed, but its daemon has not run' + asof;
    if (lg === 'error') return 'et-usage failed: ' + (uh.error || '?') + asof;
    return 'no data' + (uh.stale ? ' (the machine has not answered)' : '');
  }
  function notLoggedText(h) {
    const lg = (UH[h] || {}).logger;
    if (lg === 'not installed') return `usage logging not installed on ${h}`;
    if (lg === 'not running') return `the usage logger on ${h} has not run`;
    if (lg === 'error') return `et-usage failed on ${h}`;
    if (!U) return 'no card-use data';
    return `no card-use data from ${h}`;
  }
  const pctOf = s => { const p = 100 * s / (UHOURS * 3600); return p <= 0 ? '0%' : p < 1 ? 'under 1%' : Math.round(p) + '%'; };
  /* "sgemm_host ×12, pcie_host"; et-usage's "(others)" (a long list cut to its largest entries) always comes last */
  function progText(pr, k) {
    const all = Object.entries(pr || {}), oth = all.filter(([p]) => p === '(others)');
    const e = all.filter(([p]) => p !== '(others)').sort((a, b) => b[1] - a[1] || natural(a[0], b[0]));
    if (!e.length && !oth.length) return null;
    const more = e.length > (k || 3);
    return e.slice(0, k || 3).map(([p, n]) => p + (n > 1 ? ' ×' + n : '')).join(', ') +
      (oth.length && !more ? (e.length ? ', ' : '') + 'others ×' + oth[0][1] : more ? ', …' : '');
  }
  /* et-usage's "?": a node opened and closed between two of its scans (a few ms), so it could not see whose process
     it was (the collector also writes "?" for a login that fails the login rule). Never counted as a person. */
  const whoName = u => (u === '?' ? 'unseen (?)' : u);
  const WHO_UNSEEN = 'a node opened and closed between two of the logger\'s scans (a few ms): whose process it was is unknown';
  const usersOf = id => Object.entries((UC[id] || {}).users || {}).sort((a, b) => b[1].held_s - a[1].held_s || natural(a[0], b[0]));
  /* "Last 24 h: held 2 h 10 min (9%) by user-a, user-b" */
  function usageSentence(id, short) {
    const cu = UC[id] || {}, us = usersOf(id);
    if (!us.length) return `Last ${UHOURS} h: not used` + (cu.stale ? ' (old data)' : '');
    const names = us.map(u => whoName(u[0]));
    return `Last ${UHOURS} h: held ${durS(cu.held_s)} (${pctOf(cu.held_s)}) by ` + (short && names.length > 3 ? names.slice(0, 3).join(', ') + ` and ${names.length - 3} more` : names.join(', '));
  }
  /* Spans of the window not covered by the host's log, each with its reason. */
  function gapsOf(h) {
    const uh = UH[h] || {}, cov = (Array.isArray(uh.coverage_ms) ? uh.coverage_ms : []).filter(c => Array.isArray(c) && isNum(c[0]) && isNum(c[1]))
      .map(c => [Math.max(US0, c[0]), Math.min(US1, c[1])]).filter(c => c[1] > c[0]).sort((a, b) => a[0] - b[0]);
    const out = [];
    let t = US0;
    const why = (a, b) => {
      if (isNum(uh.truncated_before_ms) && b <= uh.truncated_before_ms + 60e3) return 'not read: the log is larger than et-usage reads at once';
      if (a <= US0 + 1000 && (!isNum(uh.logging_since_ms) || uh.logging_since_ms >= b - 60e3)) return 'before its log begins';
      if (b >= US1 - 1000 && uh.stale) {
        const x = H[h] || {}, st = stateOf(x);
        return st === 'down' ? `machine down since ${clock(isNum(x.down_since_ms) ? x.down_since_ms : uh.as_of_ms)}`
          : `not known: the machine has not answered since ${clock(uh.as_of_ms)} (${st})`;
      }
      if (b >= US1 - 1000 && uh.logger === 'stale') return 'the logger stopped' + (uh.paused ? ` while paused: ${uh.paused}` : '');
      if (b >= US1 - 1000 && uh.paused) return `the logger is paused: ${uh.paused}`;
      return 'the logger was not running';
    };
    for (const [a, b] of cov) { if (a - t > 60e3) out.push({a: t, b: a, why: why(t, a)}); t = Math.max(t, b); }
    if (US1 - t > 60e3) out.push({a: t, b: US1, why: why(t, US1)});
    return out;
  }
  /* A span "14:02–14:09" (or with seconds), the end's weekday only when it is another day. */
  function spanText(a, b, secs, open) {
    const f = secs ? L_HMS : L_HM;
    const end = open ? 'now' : L_DAY.format(a) === L_DAY.format(b) ? f.format(b) : L_WD.format(b) + ' ' + f.format(b);
    return lclock(a, secs) + '–' + end;
  }
  /* The intervals of one lane merged at the drawing's resolution: one login's bars closer than 3 px become one. */
  function pixelGroups(ivs, x) {
    const out = [], last = {};
    for (const iv of (Array.isArray(ivs) ? ivs : []).slice().sort((a, b) => a.start_ms - b.start_ms)) {
      if (!isNum(iv.start_ms) || !isNum(iv.end_ms)) continue;
      const g = last[iv.user];
      if (g && x(iv.start_ms) - x(g.b) < 3) {
        g.b = Math.max(g.b, iv.end_ms); g.held_s += iv.held_s || 0; g.node_s += iv.node_s || 0; g.runs += iv.runs || 0;
        g.n += iv.n || 1; g.open = g.open || !!iv.open; g.lost = g.lost || !!iv.lost_end; g.ivs.push(iv);
        if (g.lock !== iv.lock_user) g.lock = null;
        for (const [p, n] of Object.entries(iv.programs || {})) g.programs[p] = (g.programs[p] || 0) + n;
      } else {
        const ng = {user: iv.user, a: iv.start_ms, b: iv.end_ms, held_s: iv.held_s || 0, node_s: iv.node_s || 0, runs: iv.runs || 0,
          n: iv.n || 1, open: !!iv.open, lost: !!iv.lost_end, lock: iv.lock_user || null, programs: Object.assign({}, iv.programs || {}), ivs: [iv]};
        out.push(ng); last[iv.user] = ng;
      }
    }
    return out;
  }
  /* The share of a bar's span that the card was held (a bar that joins several runs spans the gaps between them). */
  const heldShare = gr => { const span = Math.max(1, gr.b - gr.a) / 1000; return Math.max(0, Math.min(1, (gr.held_s || 0) / span)); };
  function groupTip(gr, label) {
    const secs = gr.b - gr.a < 600e3, pr = progText(gr.programs, 4), sh = heldShare(gr);
    const lines = [`<b>${esc(whoName(gr.user))}</b> on ${esc(label)}`, esc(spanText(gr.a, gr.b, secs, gr.open)) + (gr.open ? ' (still held)' : '')];
    if (gr.user === '?') lines.push(esc(WHO_UNSEEN));
    if (gr.user === '?' && gr.lock) lines.push(esc(`the card's lock was held by ${gr.lock} at the time (a hint, not proof)`));
    if (gr.lost) lines.push(esc('its end is approximate: the logger died while it was held, so it ends where the logger last saw it'));
    if (gr.n > 1) lines.push(esc(`${plural(gr.n, 'hold')}, ${durS(gr.held_s)} held in all` + (sh < 0.9 ? ` (${Math.max(1, Math.round(100 * sh))}% of the span; drawn light, each run solid)` : '')));
    else lines.push(esc(`held ${durS(gr.held_s)}`));
    lines.push(esc(`device nodes open ${durS(gr.node_s)}; ${gr.runs ? plural(gr.runs, gr.user === '?' ? 'open' : 'run') : 'the lock only'}`));
    if (pr && gr.user !== '?') lines.push('programs: ' + esc(pr));
    return lines.join('<br>');
  }
  /* Text colour on a bar: --ink or --page, whichever contrasts more with the bar's colour in the current theme. */
  function luminance(css) {
    const s = document.createElement('span'); s.style.color = css; s.style.display = 'none'; document.body.appendChild(s);
    const c = getComputedStyle(s).color; s.remove();
    const v = (c.match(/[\d.]+/g) || [0, 0, 0]).map(Number), unit = /^color\(/.test(c) ? 1 : 255;
    const f = x => { x /= unit; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(v[0]) + 0.7152 * f(v[1]) + 0.0722 * f(v[2]);
  }
  function inkFor(color) {
    const cr = (p, q) => (Math.max(p, q) + 0.05) / (Math.min(p, q) + 0.05), bg = luminance(color);
    return cr(bg, luminance('var(--ink)')) >= cr(bg, luminance('var(--page)')) ? 'var(--ink)' : 'var(--page)';
  }
  /* One card's lane between x(US0) and x(US1) at y: the track, hatched spans not logged, activity ticks, one bar per
     login's hold (at least 2 px wide, so a 3-second run stays visible). Returns the marks with tooltips, in time order. */
  function drawLane(f, id, x, by, bh, label, mini) {
    const h = hostOfCard(id), cu = UC[id] || {}, uh = UH[h] || {}, nodes = [];
    const X0 = x(US0), X1 = x(US1);
    CK.el('rect', {class: 'tl-track', x: X0, y: by, width: X1 - X0, height: bh, rx: 2}, f.svg);
    if (!cu.logged) {
      const g = CK.el('g', null, f.svg);
      CK.el('rect', {class: 'cu-hatch', x: X0, y: by, width: X1 - X0, height: bh, rx: 2}, g);
      const t = notLoggedText(h) + (uh.stale && isNum(uh.as_of_ms) ? ` (as of ${clock(uh.as_of_ms)})` : '');
      if (!mini) {
        const bg = CK.el('rect', {class: 'cu-textbg', x: X0 + 4, y: by + 1, width: 10, height: bh - 2, rx: 3}, g);
        const tx = CK.txt(g, X0 + 10, by + bh / 2 + 4, t, 'lab');
        let w = 0; try { w = tx.getComputedTextLength(); } catch (_) { w = 0; }
        bg.setAttribute('width', Math.min(X1 - X0 - 8, (w > 0 ? w : 6.6 * t.length) + 12));
      }
      CK.el('rect', {class: 'ck-hit', x: X0, y: by - 3, width: X1 - X0, height: bh + 6}, g);
      CK.tip(f, g, `<b>${esc(label)}</b><br>${esc(t)}`);
      nodes.push([X0, g]);
      return nodes.map(n => n[1]);
    }
    for (const gp of gapsOf(h)) {
      const g = CK.el('g', null, f.svg), xa = x(gp.a), w = Math.max(2, x(gp.b) - xa);
      CK.el('rect', {class: 'cu-hatch', x: xa, y: by, width: w, height: bh}, g);
      CK.el('rect', {class: 'ck-hit', x: xa, y: by - 3, width: Math.max(6, w), height: bh + 6}, g);
      CK.tip(f, g, `<b>${esc(label)}: not logged</b><br>${esc(spanText(gp.a, gp.b, false, false))} (${esc(durS((gp.b - gp.a) / 1000))})<br>${esc(gp.why)}`);
      nodes.push([xa, g]);
    }
    const act = Array.isArray(cu.activity_min) ? cu.activity_min : [];
    if (act.length) {
      const ga = CK.el('g', {'aria-hidden': 'true', class: 'cu-act'}, f.svg);
      for (const a of act) {
        if (!Array.isArray(a) || !isNum(a[0])) continue;
        const te = US0 + a[0] * 6e4, ta = te - (isNum(a[1]) ? a[1] : 60) * 1000, xa = x(Math.max(US0, ta));
        CK.el('rect', {x: xa, y: by + bh + 2, width: Math.max(1, x(te) - xa), height: mini ? 2 : 3}, ga);
      }
    }
    // Logins whose bars overlap at this width (interleaved runs, or a busy log merged into long bars) share the lane
    // in rows, the most held on top and the rest in the last row, so that no login's bar hides another's.
    const groups = pixelGroups(cu.intervals, x), ends = {};
    let overlap = false;
    for (const gr of groups) {
      const xa = x(gr.a);
      if (Object.keys(ends).some(u => u !== gr.user && xa < ends[u] - 0.5)) { overlap = true; break; }
      ends[gr.user] = Math.max(ends[gr.user] || -Infinity, xa + Math.max(2, x(gr.b) - xa));
    }
    const rank = {};
    usersOf(id).forEach(([u], k) => { rank[u] = k; });
    const nrows = overlap ? Math.min(Object.keys(rank).length || 1, mini ? 3 : 4) : 1, rh = bh / nrows;
    for (const gr of groups) {
      const r = nrows > 1 ? Math.min(isNum(rank[gr.user]) ? rank[gr.user] : nrows - 1, nrows - 1) : 0, ry = by + r * rh;
      const g = CK.el('g', null, f.svg), xa = x(gr.a), w = Math.max(2, x(gr.b) - xa), color = userColor(gr.user), hh = nrows > 1 ? rh - 0.5 : bh;
      // a bar held for most of its span is solid; one that joins runs with gaps between them (at this width, or merged by
      // the collector in a busy log) is a light span with each run solid inside it, so it never reads as busy all along
      const env = w >= 4 && heldShare(gr) < 0.9;
      const bar = CK.el('rect', {x: xa, y: ry, width: w, height: hh, rx: w > 6 && nrows === 1 ? 2 : 0}, g);
      bar.style.fill = color;
      if (env) {
        bar.style.fillOpacity = '0.28';
        for (const iv of gr.ivs || []) {
          const ia = x(iv.start_ms), iw = Math.max(1, x(iv.end_ms) - ia), ish = heldShare({a: iv.start_ms, b: iv.end_ms, held_s: iv.held_s});
          // a span merged from many runs (by et-usage or the collector, in a busy log) is not a run: it stays light
          if (ish < 0.9 && ((iv.n || 1) > 1 || (iv.runs || 0) > 1)) continue;
          const m = CK.el('rect', {x: ia, y: ry, width: iw, height: hh}, g);
          m.style.fill = color; if (ish < 0.9) m.style.fillOpacity = String(Math.max(0.45, ish).toFixed(2));
        }
      }
      if (!mini && nrows === 1 && w >= 0.62 * 12 * gr.user.length + 12) {
        const tx = CK.txt(g, xa + 5, by + bh / 2 + 4, gr.user, 'cu-blab');
        tx.style.fill = env ? 'var(--ink)' : inkFor(color);
        tx.setAttribute('aria-hidden', 'true');
      }
      const hw = Math.max(8, w), hy = nrows > 1 ? ry - (r === 0 ? 3 : 0) : by - 3;
      CK.el('rect', {class: 'ck-hit', x: xa + w / 2 - hw / 2, y: hy, width: hw, height: nrows > 1 ? rh + (r === 0 || r === nrows - 1 ? 3 : 0) : bh + 6}, g);
      CK.tip(f, g, groupTip(gr, label));
      nodes.push([xa, g]);
    }
    nodes.sort((a, b) => a[0] - b[0]);
    return nodes.map(n => n[1]);
  }
  function renderUsage() {
    const chart = $('cu-chart');
    fill('cu-zone', LZONE ? LZONE + ', the lab\'s time' : 'the lab\'s time');
    if (!U || US0 == null || US1 == null || !(US1 > US0)) {
      chart.append(E('p', 'small muted', 'No card-use data in this data file: the collector may be older than this page.'));
      $('cu-extra').hidden = true;
      return;
    }
    const ids = CARDS.slice();
    if (!ANY_LOGGED) {
      // no machine logs card use yet: one line instead of an empty chart, notes and tables
      const hs = HOSTS.filter(h => (UH[h] || {}).logger === 'not installed');
      chart.append(E('p', 'cu-none', E('b', null, 'No machine logs card use yet'), hs.length ? ` (et-usage is not installed on ${hs.join(', ')})` : '',
        ': who held each card at each 10-minute check is in Last 48 hours, below.'));
      $('cu-extra').hidden = true; $('cu-note').hidden = true;
      return;
    }
    const logins = (Array.isArray(U.logins) ? U.logins : []).filter(u => u && u !== '?');
    const items = logins.filter(u => USER_COLOR[u]).map(u => ({key: u, label: u, color: userColor(u), mark: 'box'}));
    if (hasOthers(logins) || ids.some(id => Object.keys((UC[id] || {}).users || {}).includes('?'))) items.push({key: '_others', label: 'others', color: OTHER_COLOR, mark: 'box'});
    items.push({key: '_nolog', label: 'not logged', color: 'url(#cu-hatch)', mark: 'box'},
      {key: '_act', label: 'card queues active (ticks)', color: 'var(--ink-2)', mark: 'line'},
      {key: '_now', label: `now (${lclock(US1)})`, color: 'var(--ink)', mark: 'dash'});
    CK.legend('cu-legend', items);
    CK.frame(chart, {minW: 300, maxW: 1248, label: `Card use by login, last ${UHOURS} hours`,
      height: W => 16 + ids.length * (W < 600 ? 46 : 36) + 30,
      draw(f) {
        const nar = f.narrow, L = nar ? 4 : 176, R = 10, Tp = 16, B = 30, rowH = nar ? 46 : 36, bh = 16;
        const x = CK.lin(US0, US1, L, f.W - R);
        const ga = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
        const every = nar ? 6 : 3;
        for (let t = Math.ceil(US0 / 36e5) * 36e5; t <= US1; t += 36e5) {
          const hr = labHour(t), major = hr % every === 0;
          CK.el('line', {class: major ? 'tl-vgrid' : 'cu-minor', x1: x(t), x2: x(t), y1: major ? Tp - 4 : f.H - B, y2: f.H - B + (major ? 4 : 3)}, ga);
          if (major) labs.push(CK.txt(ga, x(t), f.H - B + 18, hr === 0 ? `${L_WD.format(t)} ${L_D.format(t)}` : L_HM.format(t), hr === 0 ? 'lab-strong' : 'tick', 'middle'));
        }
        CK.inside(f, labs);
        ids.forEach((id, k) => {
          const y0 = Tp + k * rowH, by = nar ? y0 + 18 : y0 + 6, cu = UC[id] || {}, c = C[id] || {};
          const lg = CK.el('g', {'aria-hidden': 'true'}, f.svg), name = cardName(id);
          CK.cardMark(lg, id, nar ? 8 : 10, nar ? y0 + 9 : by + 6, 4, MARK_INK);
          CK.txt(lg, nar ? 18 : 22, nar ? y0 + 13 : by + 10, name + (nar && c.excluded ? ' (excluded)' : ''), c.excluded ? 'lab' : 'lab-strong');
          if (!nar) CK.txt(lg, 22, by + 25, (c.excluded ? 'excluded · ' : '') + (cu.logged ? (usersOf(id).length ? `${durS(cu.held_s)} held` : 'not used') : 'not logged'), 'tick');
          else if (cu.logged) CK.txt(lg, f.W - R - 8, y0 + 13, usersOf(id).length ? `${durS(cu.held_s)} held` : 'not used', 'tick', 'end');
          CK.keynav(f, drawLane(f, id, x, by, bh, cardName(id), false));
        });
        const xn = x(US1);
        CK.el('line', {class: 'cu-now', x1: xn, x2: xn, y1: nar ? Tp - 6 : Tp - 2, y2: f.H - B}, ga);  // starts under its label
        labs.length = 0;
        labs.push(CK.txt(ga, xn, nar ? f.H - B + 18 : Tp - 8, 'now', nar ? 'lab-strong' : 'tick', 'end'));
        CK.inside(f, labs);
      }});
    renderUsageCards(ids);
    renderUsageTable(ids);
    renderUsageDays(ids);
  }
  function usageStrip(host, id) {
    if (US0 == null) { host.append(E('span', 'small muted', 'no card-use data')); return; }
    CK.frame(host, {minW: 120, maxW: 900, height: 24, label: cardName(id) + ': card use, last ' + UHOURS + ' hours', draw(f) {
      const x = CK.lin(US0, US1, 1, f.W - 1);
      CK.keynav(f, drawLane(f, id, x, 3, 13, cardName(id), true));
    }});
  }
  function renderUsageCards(ids) {
    const root = $('cu-cards');
    for (const id of ids) {
      const cu = UC[id] || {}, h = hostOfCard(id), uh = UH[h] || {}, c = C[id] || {};
      const head = E('b', null, markSvg(id, 13), ' ', cardName(id), c.excluded ? ' (excluded)' : '');
      const div = E('div', 'cu-card');
      if (!cu.logged) {
        div.append(head, ': ', notLoggedText(h), '.', E('span', 'cu-sub', uh.stale && isNum(uh.as_of_ms) ? `As of ${clock(uh.as_of_ms)}, when ${h} last answered. ` : '',
          'Last 48 hours below shows who held it at each 10-minute check.'));
        root.append(div); continue;
      }
      const us = usersOf(id), ppl = us.filter(u => u[0] !== '?'), unseen = us.length > ppl.length;
      const main = !us.length ? [`not used in the last ${UHOURS} h`]
        : !ppl.length ? [`held ${durS(cu.held_s)} of the ${UHOURS} h (${pctOf(cu.held_s)}), by unseen (?) runs only`]
        : [`held ${durS(cu.held_s)} of the ${UHOURS} h (${pctOf(cu.held_s)}) by ${plural(ppl.length, 'person', 'people')}${unseen ? ' and unseen (?) runs' : ''}`,
          `; busiest: ${ppl[0][0]} (${durS(ppl[0][1].held_s)}, ${plural(ppl[0][1].runs || 0, 'run')})`];
      const now = (cu.now || []).filter(x => x && x.user), was = cu.stale ? (cu.was_now || []).filter(x => x && x.user) : [];
      const sub = [];
      const holdText = x => `${whoName(x.user)} · ${x.comm || '?'} · since ${lclock(x.start_ms)}`;
      const more = !cu.stale && isNum(cu.now_more) && cu.now_more > 0 ? `; and ${plural(cu.now_more, 'more hold')} not listed` : '';
      if (now.length) sub.push('In use now: ' + now.map(holdText).join('; ') + more + '.');
      if (was.length) sub.push(`Held when ${h} last answered (${clock(uh.as_of_ms)}): ` + was.map(holdText).join('; ') + '; whether it still is, is unknown.');
      const gaps = gapsOf(h);   // concise (2 Oct 2026): only what is missing; queue ticks and bar merging are in the chart
      if (gaps.length) sub.push(`Not logged: ${gaps.slice(0, 3).map(g => spanText(g.a, g.b, false, false) + ' (' + g.why + ')').join(', ')}${gaps.length > 3 ? ', …' : ''}.`);
      if (cu.stale) sub.push(`As of ${clock(uh.as_of_ms)}, when ${h} last answered.`);
      div.append(head, ': ', ...main, '.', E('span', 'cu-sub', sub.join(' ')));
      root.append(div);
    }
  }
  function renderUsageTable(ids) {
    const t = $('cu-table'), tb = t.tBodies[0], rows = [];
    for (const id of ids) for (const [u, e] of usersOf(id)) rows.push([u, id, e]);
    rows.sort((a, b) => b[2].held_s - a[2].held_s || natural(a[0], b[0]));
    if (!rows.length) { tb.append(E('tr', null, attrs(E('td', null, `Nobody used a logged card in the last ${UHOURS} hours.`), {colspan: 7}))); CK.stackTable(t); return; }
    for (const [u, id, e] of rows) {
      tb.append(E('tr', null,
        attrs(E('td', null, swatch(u), ' ', E('span', 'pl-login', whoName(u))), u === '?' ? {title: WHO_UNSEEN} : {}),
        E('td', null, markSvg(id, 11), ' ', cardName(id)),
        attrs(E('td', 'num', durS(e.held_s)), {'data-sort': e.held_s}),
        attrs(E('td', 'num', pctOf(e.held_s)), {'data-sort': e.held_s}),
        E('td', 'num', n0(e.runs || 0)),
        E('td', null, (u !== '?' ? progText(e.programs, 3) : (UC[id] || {}).unseen_lock && UC[id].unseen_lock.length ? `lock held by ${UC[id].unseen_lock.join(', ')} (a hint)` : null) || ELL),
        attrs(E('td', null, e.open ? `now (since ${lclock(isNum(e.open_ms) ? e.open_ms : e.first_ms)})` : lclock(e.last_ms)), {'data-sort': e.open ? 9e15 : e.last_ms})));
    }
    CK.stackTable(t);
    CK.sortTable(t, {filter: rows.length > 6, filterLabel: 'Filter'});
  }
  function renderUsageDays(ids) {
    const t = $('cu-days');
    const logged = ids.filter(id => (UC[id] || {}).logged), notLogged = ids.filter(id => !(UC[id] || {}).logged);
    const days = [];
    for (let k = 0; k <= 6; k++) { const d = US1 - k * 864e5; days.push({key: L_DAY.format(d), label: L_WD.format(d) + ' ' + L_D.format(d), ms: d}); }  // newest first
    const thead = E('thead', null, E('tr', null, E('th', null, 'Day'), logged.map(id => E('th', null, markSvg(id, 11), ' ', cardName(id)))));
    const tb = E('tbody');
    let max = 1;
    const cell = {};
    for (const id of logged) for (const d of ((UC[id] || {}).daily || [])) {
      if (!isNum(d.day_ms)) continue;
      const tot = Object.values(d.users || {}).reduce((s, e) => s + ((e && e.held_s) || 0), 0);
      cell[id + '|' + L_DAY.format(d.day_ms)] = d; max = Math.max(max, tot);
    }
    for (const d of days) {
      const tr = E('tr', null, E('th', 'cu-dl', d.label));
      for (const id of logged) {
        const uh = UH[hostOfCard(id)] || {}, since = isNum(uh.logging_since_ms) ? uh.logging_since_ms : null;
        const e = cell[id + '|' + d.key];
        // et-usage lists every one of the 7 dates ({} for no use) with the seconds its logger ran that date
        // (logged_s): a date it never ran is "not logged", never "none"; a partly logged date says how much
        const lg = e && isNum(e.logged_s) ? e.logged_s : null;
        const part = lg != null && lg > 0 && lg < 86400 - 120 && d.key !== L_DAY.format(US1) ? `logged ${durS(lg)} of the day` : null;
        const us = Object.entries((e && e.users) || {}).sort((a, b) => b[1].held_s - a[1].held_s);
        if (!us.length) {
          const nl = lg != null ? lg <= 0 : !!(since && d.key !== L_DAY.format(since) && d.ms < since);
          tr.append(attrs(E('td', 'cu-dc muted', nl ? 'not logged' : 'none', part ? E('span', 'cu-who', part) : null), {'data-sort': 0}));
          continue;
        }
        const tot = us.reduce((s, x) => s + (x[1].held_s || 0), 0);
        const bar = E('span', 'cu-mini');
        for (const [u, x] of us) { const sp = E('span'); sp.style.width = Math.max(2, 100 * (x.held_s || 0) / max) + '%'; sp.style.background = userColor(u); bar.append(sp); }
        const txt = us.map(([u, x]) => `${whoName(u)} ${durS(x.held_s)}${isNum(x.runs) ? ' (' + plural(x.runs, u === '?' ? 'open' : 'run') + ')' : ''}`).join(', ') + (part ? '; ' + part : '');
        const who = whoName(us[0][0]) + (us.length > 1 ? ` +${us.length - 1}` : '');
        tr.append(attrs(E('td', 'cu-dc', E('span', 'cu-dt', durS(tot)), bar, E('span', 'cu-who', who, E('span', 'vh', ': ' + txt))), {title: txt, 'data-sort': tot}));
      }
      tb.append(tr);
    }
    t.append(thead, tb);
    if (notLogged.length) t.parentNode.after(E('p', 'small muted', 'Not logged: ' + notLogged.map(id => `${cardName(id)} (${notLoggedText(hostOfCard(id))})`).join('; ') + '.'));
  }

  /* ================= last 48 hours ================= */
  function renderTimeline() {
    if (!HN || HT0 == null) { $('tl').append(E('p', 'small muted', 'No history yet.')); return; }
    const rows = [], logged = [];
    for (const id of inOrder(CK.cardsIn(HI.cards || {}))) {
      if ((UC[id] || {}).logged) { logged.push(id); continue; }  // drawn from the usage log in Card use, above
      // "aifoundry2 card": a one-card machine's card row is never taken for the machine's own row below it
      rows.push({kind: 'card', id, label: cardName(id) + (cardsOf(hostOfCard(id)).length > 1 ? '' : ' card'), runs: cardRuns(id)});
    }
    for (const h of HOSTS) if (series('hosts', h, 'up')) rows.push({kind: 'host', id: h, label: h, runs: hostRuns(h)});
    const kept = rows.filter(r => r.kind === 'card');
    fill('tl-cards', logged.length ? (kept.length ? `Cards with a card-use log (${logged.map(id => cardName(id)).join(', ')}) are in Card use, above.` : '')
      : 'Card rows show who held each card at each check.');
    const holders = [...new Set(kept.flatMap(r => r.runs.filter(x => x.key === 'held').map(x => x.who)))].sort(natural);
    CK.legend('tl-legend', [
      ...holders.map(u => ({key: 'h:' + u, label: `held by ${u === 'system' ? 'system or CI' : u}`, color: u === 'system' ? OTHER_COLOR : userColor(u), mark: 'box'})),
      ...(kept.length ? [{key: 'used', label: 'in use, no holder at the check', color: 'color-mix(in srgb,var(--ink-2) 50%,var(--surface))', mark: 'box'},
        {key: 'free', label: 'free', color: 'var(--axis)', mark: 'line'}] : []),
      {key: 'up', label: 'machine answered', color: 'color-mix(in srgb,var(--ok) 60%,var(--surface))', mark: 'line'},
      {key: 'nw', label: 'alive (nodewatch only)', color: 'color-mix(in srgb,var(--ok) 30%,var(--surface))', mark: 'line'},
      {key: 'approval', label: 'approval needed', color: 'color-mix(in srgb,var(--warn) 75%,var(--surface))', mark: 'box'},
      {key: 'down', label: 'machine down (Tailscale offline)', color: 'var(--bad)', mark: 'box'},
      {key: 'noans', label: 'no answer (ssh)', color: 'color-mix(in srgb,var(--bad) 40%,var(--surface))', mark: 'box'},
      {key: 'gap', label: 'nodewatch gap', color: 'var(--muted)', mark: 'box'},
    ]);
    const nCards = kept.length;
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
          labs.push(CK.txt(ga, x(t), f.H - B + 18, tickLabel(t), labHour(t) === 0 ? 'lab-strong' : 'tick', 'middle'));
        }
        CK.inside(f, labs);
        if (nCards && nCards < rows.length) {
          const ys = yOf(nCards) - 6;
          CK.el('line', {class: 'tl-sep', x1: 0, x2: f.W, y1: ys, y2: ys}, ga);
        }
        rows.forEach((r, k) => {
          const y0 = yOf(k), by = nar ? y0 + 16 : y0 + (rowH - bar) / 2;
          const lg = CK.el('g', {'aria-hidden': 'true'}, f.svg);
          if (r.kind === 'card') CK.cardMark(lg, r.id, nar ? 8 : 10, nar ? y0 + 7 : by + bar / 2, 4, MARK_INK);
          CK.txt(lg, nar ? 18 : 22, nar ? y0 + 11 : by + bar / 2 + 4, r.label, r.kind === 'card' ? 'lab-strong' : 'lab');
          CK.el('rect', {class: 'tl-track', x: L, y: by, width: f.W - R - L, height: bar, rx: 2}, f.svg);
          const nodes = r.runs.map(run => runMark(f, run, x(slotT(run.a)), x(slotT(run.b)), by, bar, r.label));
          CK.keynav(f, nodes);
        });
      }});
  }
  function readingsChart(key, hostId, legId, o) {
    const ids = inOrder(CK.cardsIn(HI.cards || {})).filter(id => { const s = series('cards', id, key); return s && s.some(isNum); });
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
    CK.legend('leg-sess', [{key: 'all', label: 'login sessions, all users, including the login screen', color: 'var(--ink-2)', mark: 'line'}]);
    const mx = Math.max(2, ...hs.flatMap(h => series('hosts', h, 'sessions_all').filter(isNum)));
    for (const h of hs) {
      const box = E('div', null, E('div', 'mt', h)), host = E('div');
      box.append(host);
      $('ch-sess').append(box);
      const all = series('hosts', h, 'sessions_all');
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
        crossHover(f, {n: HN, x: xi, top: Tp, bottom: f.H - B, label: h + ' login sessions',
          valid: i => isNum(all[i]),
          dots: i => [isNum(all[i]) ? [xi(i), y(all[i]), 'var(--ink-2)'] : null],
          html: i => `<b>${esc(h)}</b><br>${esc(slotLabel(i))}<br>login sessions, all users, including the login screen: ${esc(n0(all[i]))}`});
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
  renderUsage();
  renderHosts();
  renderPeople();
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
