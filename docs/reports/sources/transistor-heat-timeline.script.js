/* The transistor-heat timeline. A copy of session-timeline.script.js reworked for seven weeks of many sessions:
   the HUMAN track is the questions, AGENTS is the sessions, CARDS is the experiments and ARTIFACTS is the documents.
   D is timeline.json (tools/timeline/build_transistor_timeline.py); every number on the page is computed from it.
   Times are seconds since Sun 6 Sep 2026 00:00 PDT (UTC-7; US DST ends 1 Nov, so the offset holds across the whole
   span), so a day is 86 400 s and clock time is t mod 86 400. The month of a day comes from meta.day_iso, never from
   the day number.
   The timeline is one CK frame holding the four tracks on one x scale; the per-machine session detail is a second
   frame on the same scale. The view (S.v) is shared: buttons, swipes, drags, pinches, the wheel and the axis's keys change it, and
   both frames redraw on the next animation frame, drawing only what is in view. While a gesture, its momentum or a
   zoom animation runs, a frame is drawn fast: each series as one path, with no tooltips or keyboard stops; the full
   drawing, a node per mark, follows when it ends (see gestures()). Charts use the shared toolkit CK
   (docs/reports/sources/chartkit.js): tooltips by pointer, touch and keyboard, one tab stop per group of marks,
   template colour tokens only. */
const DAY = 86400, DN = D.meta.days, FULL = D.meta.full;
const HU = D.human, MA = D.main, AG = D.agents, CA = D.cards, AR = D.artifacts, HL = D.highlights;
const NB = D.neighbors && D.neighbors.sessions && D.neighbors.sessions.length ? D.neighbors : null;   // the ten lanes
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
/* CK.fmt.num's output, with one Intl.NumberFormat per format kept (toLocaleString builds one per call, which made
   number formatting the largest cost of a redraw) */
const NF = new Map();
const num = (v, dp) => {
  if (v == null || !isFinite(v)) return '—';
  const auto = dp == null;
  if (auto) dp = v === 0 ? 0 : Math.min(6, Math.max(0, 2 - Math.floor(Math.log10(Math.abs(v)))));
  const k = (auto ? 'a' : 'f') + dp;
  let nf = NF.get(k);
  if (!nf) NF.set(k, nf = new Intl.NumberFormat('en-GB', {minimumFractionDigits: auto ? 0 : dp, maximumFractionDigits: dp}));
  const s = nf.format(Number(v));
  return /[1-9]/.test(s) ? s.replace('-', '−') : s.replace('-', '');
};
const pad2 = n => String(n).padStart(2, '0');
const hm = t => { const s = ((Math.floor(t) % DAY) + DAY) % DAY; return pad2(Math.floor(s / 3600)) + ':' + pad2(Math.floor(s % 3600 / 60)); };
const dayOf = t => Math.floor(t / DAY);
// the month of day index d, read from meta.day_iso: the span crosses two months and a heuristic would mislabel it
const MOL = d => MONTHS[+(D.meta.day_iso[d] || '2026-09-01').slice(5, 7) - 1] || '';
const MO = d => MOL(d).slice(0, 3);
const WEEK = d => D.meta.day_week[d];
const when = t => `${DN[dayOf(t)] || ''} ${MO(dayOf(t))} ${hm(t)}`;
const span = (a, b) => (dayOf(a) === dayOf(b) || (b % DAY === 0 && dayOf(b) === dayOf(a) + 1) ? `${when(a)}–${b % DAY === 0 && dayOf(b) > dayOf(a) ? '24:00' : hm(b)}` : `${when(a)} – ${when(b)}`);
const dur = s => (s < 90 ? `${Math.round(s)} s` : s < 5400 ? `${Math.round(s / 60)} min` : s < 2 * 86400 ? `${num(s / 3600, 1)} h` : `${num(s / 86400, 1)} days`);
const hrs = (h, dp) => `${num(h, dp == null ? 1 : dp)} h`;
const tokAx = v => (v >= 1e9 ? `${num(v / 1e9)} B` : v >= 1e6 ? `${num(v / 1e6)} M` : v >= 1e3 ? `${num(v / 1e3)} k` : num(v));
const tok = v => (v >= 1e9 ? `${num(v / 1e9, 2)} B` : v >= 1e6 ? `${num(v / 1e6, 1)} M` : v >= 1e3 ? `${num(v / 1e3, 0)} k` : num(v, 0));
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
const setH = (id, h) => { const e = document.getElementById(id); if (e) e.innerHTML = h; };
const sty = (n, o) => { for (const k in o) n.style[k] = o[k]; return n; };
const mixT = (c, p) => `color-mix(in srgb, ${c} ${p}%, transparent)`;
const unrle = r => { const a = []; for (const [v, n] of r) for (let i = 0; i < n; i++) a.push(v); return a; };
const overlap = (iv, a, b) => iv.reduce((s, q) => s + Math.max(0, Math.min(q[1], b) - Math.max(q[0], a)), 0);
function union(iv, bridge) { const u = []; for (const [a, b] of iv.slice().sort((p, q) => p[0] - q[0])) { if (u.length && a - u[u.length - 1][1] < (bridge || 0)) u[u.length - 1][1] = Math.max(u[u.length - 1][1], b); else u.push([a, b]); } return u; }
function rect(g, x, y, w, h, fill, extra) { return sty(CK.el('rect', Object.assign({x: +x.toFixed(2), y, width: Math.max(0, +w.toFixed(2)), height: Math.max(0, h)}, extra || {}), g), {fill}); }
const lineEl = (g, x1, y1, x2, y2, st) => sty(CK.el('line', {x1, y1, x2, y2}, g), st);
function spreadX(items, gap, lo, hi) {  // keep at least gap px between flags, inside [lo, hi], moving each as little as needed
  items.sort((a, b) => a.x0 - b.x0); items.forEach(o => { o.x = Math.max(lo, Math.min(hi, o.x0)); });
  for (let i = 1; i < items.length; i++) items[i].x = Math.max(items[i].x, items[i - 1].x + gap);
  if (items.length) items[items.length - 1].x = Math.min(items[items.length - 1].x, hi);
  for (let i = items.length - 2; i >= 0; i--) items[i].x = Math.min(items[i].x, items[i + 1].x - gap);
  if (items.length && items[0].x < lo) { items[0].x = lo; for (let i = 1; i < items.length; i++) items[i].x = Math.max(items[i].x, items[i - 1].x + gap); }
  return items;
}

/* ---------- the data, unpacked ---------- */
const COL = {main: 'var(--c7)', wf: 'var(--c4)', tool: 'var(--c5)', fail: 'var(--ref)'};
/* Experiment families get no hue of their own: the agents use --c4, --c5 and --c7 and the cards --c1, --c2, --c3, so
   the families are a neutral ramp in time order (ink mixed into the surface), and the development runs, which come
   from the transcripts rather than a data file, are drawn outlined. */
const DEVF = CA.dev;   // -1 here: every interval on this page comes from a committed data file
const NFAM = CA.families.length - (DEVF >= 0 ? 1 : 0);   // the families, 22% to 94% ink in time order
const FAMCOL = CA.families.map((f, i) => (i === DEVF ? 'transparent' : `color-mix(in srgb, var(--ink) ${Math.round(22 + 72 * (DEVF >= 0 && i > DEVF ? i - 1 : i) / Math.max(1, NFAM - 1))}%, var(--surface))`));
const INUSE_FILL = [0, 28, 42, 60, 85].map(p => mixT('var(--ink)', p));   // cards in use, 0 to 4 (the height carries the count)
const famFill = (f, cardColor) => (f === DEVF ? mixT(cardColor || 'var(--ink-2)', 30) : FAMCOL[f]);
const KINDLAB = {prompt: 'typed at the prompt', midturn: 'sent while the agent was working', voice: 'dictated as a voice note',
  discord: 'posted in the lab’s channel', 'slash-command': 'a slash command', interrupt: 'an interrupt (Esc)'};
const CATMARK = ['dot', 'diamond', 'box', 'ring', 'line'];
const MSG = HU.msgs.map((m, i) => ({i, t: m[0], act: m[1], actp: m[2], cat: m[3], kind: HU.kinds[m[4]], sum: m[5], rid: m[6], chars: m[7], read: m[8], type: m[9], paste: m[10],
  text: m[11], rm: m[12] || [], img: m[13] || 0, to: m[14] || null}));
const LANE_NAME = {};   // a lane's id to the name used in prose
// every owner message, the main session's and the other sessions', in time order: what the prompt reader steps through
const PROMPTS = MSG.map(m => ({t: m.t, sum: m.sum, text: m.text, rm: m.rm, img: m.img, kind: m.kind, cat: m.cat, rid: m.rid, chars: m.chars,
  where: 'the main session', lost: false}))
  .concat(NB ? NB.sessions.flatMap(nb => nb.msgs.map(m => ({t: m[0], sum: m[3], text: m[4], rm: m[5] || [], img: 0, kind: HU.kinds[m[2]], cat: m[1],
    rid: null, chars: m[8] || 0, where: nb.name, lost: !!m[6], sid: m[7]}))) : [])
  .sort((a, b) => a.t - b.t);
PROMPTS.forEach((p, k) => { p.k = k; });
const PIDX = new Map(PROMPTS.map(p => [p.where + '@' + p.t + '@' + p.sum, p.k]));
const pidx = (where, t, sum) => PIDX.get(where + '@' + t + '@' + sum);
const SES = HU.sessions.map((s, i) => ({i, s: s[0], e: s[1], n: s[2], act: s[3], actp: s[4]}));
const BUSY = MA.busy.map(b => ({s: b[0], e: b[1], trig: MA.triggers[b[2]], tok: b[3], tools: b[4], msgs: b[5], act: b[6], tw: b[7], ow: b[8], twl: b[9]}));
const STRICT = MA.strict, WATCH = MA.watch;
const BUSY_H = BUSY.reduce((a, b) => a + b.e - b.s, 0) / 3600;   // the main agent's busy hours, as every total on the page counts them
// sessions busy per minute: Claude Code sessions (CW), the other harnesses (CT), and sessions abandoned (CF)
const CW = unrle(D.conc.wf), CT = unrle(D.conc.tool), OW = unrle(D.conc.okwf), OT = unrle(D.conc.oktool), CF = unrle(D.conc.fail), C0 = D.conc.start;
const PK = AG.peak.subagents.value, PKOK = AG.peak.subagents_excluding_errored.value, PKM = AG.peak_minute;
const niceMax = v => [4, 8, 12, 16, 20, 24, 30, 40, 50, 60].find(k => v <= k) || Math.ceil(v / 20) * 20;
const WFS = AG.workflows, GRP = AG.groups;
const AGR = AG.rows.map(r => ({s: r[0], e: r[1], g: r[2], lane: r[3], wf: r[4], label: r[5], phase: r[6], st: AG.status[r[7]], kind: AG.kinds[r[8]], busy: r[9], tok: r[10], otok: r[11], tools: r[12],
  iv: r[13].reduce((a, v, i) => { if (i % 2) a[a.length - 1].push(v); else a.push([v]); return a; }, [])}));
const CIV = CA.intervals.map(r => ({c: r[0], s: r[1], e: r[2], f: r[3], E: r[4], label: r[5], name: r[6], st: r[7], die: r[8]}));
const CU = CA.ids.map((id, k) => union(CIV.filter(q => q.c === k).map(q => [q.s, q.e]), 120));
const INU = CA.inuse, INV = unrle(INU.rle);
const PAGES = AR.pages;
const DEP = AR.deploys.map(d => ({t: d[0], p: d[1], nw: d[2], ok: d[3]})).sort((a, b) => a.t - b.t);
const COM = AR.commits.map(c => ({t: c[0], sha: c[1], sub: c[2], ses: c[3], br: c[4], files: c[5]})).sort((a, b) => a.t - b.t);
// the hosts down (a hang, or the power cycle), drawn over their cards' lanes: [[card indices], s, e, kind, title, text]
const HOSTEV = NB && NB.hosts ? NB.hosts.map(h => ({cards: h[0], s: h[1], e: h[2], kind: h[3], title: h[4], text: h[5]})) : [];
function byMinute(arr) { const m = new Map(); for (const o of arr) { const k = Math.floor(o.t / 60); if (!m.has(k)) m.set(k, []); m.get(k).push(o); } return [...m.values()].map(v => ({t: v[0].t, items: v})); }
const DEPM = byMinute(DEP), COMM = byMinute(COM);
const SUBIV = {workflow: [], tool: []};
AGR.forEach(a => a.iv.forEach(q => SUBIV[a.kind === 'claude-code' ? 'workflow' : 'tool'].push(q)));
const subHours = k => SUBIV[k].reduce((s, q) => s + q[1] - q[0], 0) / 3600;
const TOT_SESSION = D.meta.snapshot_end - D.meta.session_start;

/* ---------- lede, the lanes list and the KPIs ---------- */
(function () {
  const W = D.who, at = AG.totals, ct = CA.totals, art = AR.totals;
  const dayLab = d => `${+D.meta.day_iso[d].slice(8)} ${MOL(d)}`;
  setH('l-range', `${dayLab(dayOf(FULL[0]))} \u2013 ${dayLab(dayOf(D.meta.snapshot_end))} 2026`);
  setH('l-n', HU.totals.n);
  setH('l-ses', at.agents);
  setH('l-mach', AG.groups.length);
  setH('l-lanes', NB ? NB.sessions.length : 0);
  setH('l-exp', num(ct.intervals, 0));
  setH('l-cardh', `${num(ct.held_h, 0)} card-hours`);
  setH('l-doc', art.pages);
  setH('l-pub', art.public);
  setH('l-wall', `${num(W.wall_h / 24, 0)} days`);
  if (NB) LANE_NAME && NB.sessions.forEach(nb => { LANE_NAME[nb.id] = nb.name; });
  const lk = document.getElementById('lane-key');
  if (lk && NB) lk.innerHTML = NB.sessions.map(nb => `<li><b>${esc(nb.lane)}</b> \u2014 ${esc(nb.name)}: ` +
    `${nb.n > 1 ? `${nb.n} sessions` : 'one session'}, ${hrs(nb.busy_h, 1)} of work, ${nb.asks} ask${nb.asks === 1 ? '' : 's'}</li>`).join('');
  const bc = HU.totals.by_category;
  setH('k-human', `${HU.totals.n} asks`);
  setH('k-human-sub', `${bc.request} requests, ${bc.question} questions, ${bc.correction} corrections, ${bc.status} status checks, ` +
    `${bc['approval/answer']} approvals (<a href="#asked">the list</a>)<span class="kpi-est">about ${hrs(W.human_active_h, 1)} of writing, an estimate</span>`);
  setH('k-agents', `${num(W.sub_agent_h, 0)} session-hours`);
  setH('k-agents-sub', `${at.agents} sessions on ${AG.groups.length} machines, ${hrs(W.main_busy_h, 0)} of wall clock in which some session was working; ` +
    `up to ${AG.peak.subagents.value} at once`);
  setH('k-cards', `${num(W.card_held_h, 0)} card-hours`);
  setH('k-cards-sub', CA.per_card.map(p => `${CK.card(p.id).label} ${num(p.held_h, 1)}`).join(' \u00b7 ') +
    ` h held, over ${num(ct.intervals, 0)} measurements`);
  setH('k-doc', `${art.pages} write-ups`);
  setH('k-doc-sub', `${art.public} public, ${art.pages - art.public} kept private; ${art.deploys} versions in all, and ` +
    `${num(art.commits, 0)} commits to the lab repository`);
})();

/* ---------- the view ---------- */
const S = {v: FULL.slice(), sub: false, perPage: true, cardMode: 'family', focus: null, fast: false, drawFast: false};
const MINSPAN = 15 * 60;
function clampV(a, b) {
  let s = Math.max(MINSPAN, Math.min(FULL[1] - FULL[0], b - a));
  if (a < FULL[0]) a = FULL[0];
  if (a + s > FULL[1]) a = FULL[1] - s;
  return [a, a + s];
}
let raf = 0, anim = 0, animating = false, gestureTimer = 0, lastDetail = 0, inertia = 0;
/* While a swipe, drag, pinch or wheel gesture, its momentum or a zoom animation runs, the timeline is drawn fast (each
   series one path, no tooltips or keyboard stops: TIP, NAV and PB below); a full redraw follows 160 ms after the
   gesture's last move, and at an animation's last frame. */
let gestureGen = 0;
function gesture() {   // the full redraw waits for 160 ms without a move, then for the browser to be idle (input first)
  S.fast = true; clearTimeout(gestureTimer);
  const gen = ++gestureGen, full = () => { if (gen === gestureGen && !inertia) { S.fast = false; redrawAll(true); } };
  gestureTimer = setTimeout(() => (window.requestIdleCallback ? requestIdleCallback(full, {timeout: 250}) : full()), 160);
}
function setView(a, b, fromGesture) { S.v = clampV(a, b); if (fromGesture) gesture(); if (!raf) raf = requestAnimationFrame(() => { raf = 0; redrawAll(); }); }
// a tooltip: html is a string, or () => string for one built only when the frame is drawn in full
const TIP = (f, n, h, o) => (S.drawFast ? n : CK.tip(f, n, typeof h === 'function' && !(o && o.live) ? h() : h, o));
const NAV = (f, nodes, o) => (S.drawFast ? null : CK.keynav(f, nodes, o));
const stopMotion = () => { cancelAnimationFrame(anim); cancelAnimationFrame(inertia); anim = inertia = 0; animating = false; };
function animateTo(a, b) {
  const [a0, b0] = S.v, [a1, b1] = clampV(a, b);
  stopMotion();
  if (CK.reduced) { setView(a1, b1); return; }
  // zoom in the log of the span and pan linearly, so a zoom from the whole week into an hour moves evenly
  const t0 = performance.now(), s0 = b0 - a0, s1 = b1 - a1, c0 = (a0 + b0) / 2, c1 = (a1 + b1) / 2;
  const T = Math.min(700, 380 + 60 * Math.abs(Math.log2(s1 / s0)));
  animating = true;
  const step = now => { const k = Math.min(1, (now - t0) / T), e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    if (k >= 1) animating = false;
    const sp = s0 * Math.pow(s1 / s0, e), c = c0 + (c1 - c0) * e;
    setView(c - sp / 2, c + sp / 2); if (k < 1) anim = requestAnimationFrame(step); };
  anim = requestAnimationFrame(step);
}
/* A fast frame's path: every rect, mark or line of one series in one <path>. With merge, a rect that touches or overlaps
   the one before it on the same row (a run of sub-pixel intervals) extends it instead of adding its own. */
function PB(merge) {
  let d = '', q = null;
  const f1 = v => Math.round(v * 10) / 10;
  const put = r => { d += `M${f1(r[0])} ${f1(r[1])}h${f1(r[2])}v${f1(r[3])}h${f1(-r[2])}z`; };
  return {
    rect(x, y, w, h) {
      if (!(w > 0 && h > 0)) return;
      if (merge && q && q[1] === y && q[3] === h && x <= q[0] + q[2] + 0.5 && x >= q[0]) { q[2] = Math.max(q[2], x + w - q[0]); return; }
      if (q) put(q);
      q = [x, y, w, h];
      if (!merge) { put(q); q = null; }
    },
    line(x1, y1, x2, y2) { d += `M${f1(x1)} ${f1(y1)}L${f1(x2)} ${f1(y2)}`; },
    circle(cx, cy, r) { d += `M${f1(cx - r)} ${f1(cy)}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0z`; },
    diamond(cx, cy, r) { d += `M${f1(cx)} ${f1(cy - r)}l${r} ${r}l${-r} ${r}l${-r} ${-r}z`; },
    flush(g, style) { if (q) { put(q); q = null; } if (d) sty(CK.el('path', {d, 'aria-hidden': 'true'}, g), style); d = ''; },
  };
}
const zoomBy = k => { const c = (S.v[0] + S.v[1]) / 2, h = (S.v[1] - S.v[0]) * k / 2; animateTo(c - h, c + h); };
const panBy = k => { const d = (S.v[1] - S.v[0]) * k; animateTo(S.v[0] + d, S.v[1] + d); };
const dayView = d => [Math.max(d * DAY, FULL[0]), Math.min((d + 1) * DAY, FULL[1])];   // the part of the day the data window holds
const hlView = h => { const pad = Math.max(900, (h.b - h.a) * 0.08); return [h.a - pad, h.b + pad]; };
let main = null, detail = null;
function redrawAll(full) {
  S.drawFast = !full && (S.fast || animating);
  if (main) main.redraw();
  if (!animating) S.focus = null;
  if (detail && S.sub) { const now = performance.now(); if (!S.drawFast || now - lastDetail > 45) { lastDetail = now; detail.redraw(); } }
  S.drawFast = false;
  readout(); pressed();
}

/* ---------- time ticks ---------- */
const STEPS = [60, 120, 300, 600, 900, 1800, 3600, 7200, 10800, 21600, 43200, DAY];
function ticks(a, b, pw, minPx) {
  const s = b - a; let st = STEPS.find(k => pw * k / s >= minPx);
  if (!st) st = DAY * Math.ceil(minPx * s / pw / DAY);
  const out = []; for (let t = Math.ceil(a / st) * st; t <= b + 1e-6; t += st) out.push(t);
  out.step = st; return out;
}

/* ---------- the layout of the timeline ---------- */
const ASK_ROW = 17;   // one row of what-was-asked labels under the owner's marks (zoomed in)
function layout(W) {
  const nar = W < 600, L = nar ? 66 : 164, R = nar ? 8 : 16, rows = {}; let y = 0;
  const add = (k, h) => { rows[k] = {y, h}; y += h; };
  add('axis', 40); add('hl', 30); y += 2;
  add('hH', 18); add('human', S.v[1] - S.v[0] <= 2 * DAY ? 30 + 3 * ASK_ROW : 30);
  y += 8;
  add('hA', 18); add('main', 18);
  if (NB) { y += 2; NB.sessions.forEach((n, k) => add('nb' + k, 20)); }
  y += 4; add('conc', nar ? 52 : 66); y += 8;
  add('hC', 18); CA.ids.forEach((id, k) => add('card' + k, 17)); y += 4; add('inuse', nar ? 30 : 36); y += 8;
  add('hR', 18);
  if (S.perPage) PAGES.forEach((p, k) => add('page' + k, 13)); else add('deploys', 30);
  y += 4; add('commits', 16); y += 2; add('xaxis', 26);
  return {nar, L, R, rows, H: y};
}

/* ---------- gestures ----------
   Touch: a vertical swipe scrolls the page natively (the frames' touch-action is pan-y); a swipe that starts sideways
   pans the timeline and keeps going when the finger lifts (momentum); two fingers pinch-zoom about their midpoint and
   pan with it. The direction is decided once, after 8 px of movement, so a diagonal or vertical swipe never also pans.
   A tap shows the mark's details, pinned until the next tap (a second tap on a highlight's flag zooms there), and never
   pans; a touch that turns into a scroll shows nothing. Lifting one finger of a pinch carries on as a one-finger drag,
   and a release anywhere (the listeners for it are on window) ends the gesture. Several of these follow the lessons of
   the reusable session-timeline component this project built earlier.
   Mouse: drag to pan; hover for details; click a flag to zoom.
   Wheel: Ctrl/⌘ + wheel (also how Chrome delivers a trackpad pinch) zooms about the pointer; a trackpad's sideways
   swipe (deltaX) or Shift + wheel pans; a vertical wheel scrolls the page. A wheel gesture keeps the axis of its first
   event, as the browser latches a scroll, so a page scroll that drifts sideways never starts a pan. The frames stop
   horizontal overscroll (overscroll-behavior-x: contain, in the body's CSS), so a sideways swipe never goes back a page.
   Every change goes through setView, which redraws once per animation frame. */
const SLOP = {touch: 8, pen: 6, mouse: 4};   // px before a press is a drag (the component uses 6; a finger's tap can wander 6)
const plotW = f => f.W - f.L - f.R;
function panPx(f, dx) { const sp = (S.v[1] - S.v[0]) / plotW(f); setView(S.v[0] + dx * sp, S.v[1] + dx * sp, true); }
function zoomAt(f, p, k) {   // zoom by k about the pixel p: the time under p stays under p
  const q = Math.max(f.L, Math.min(f.W - f.R, p)), s0 = S.v[1] - S.v[0], tc = S.v[0] + (q - f.L) / plotW(f) * s0;
  const s1 = Math.max(MINSPAN, Math.min(FULL[1] - FULL[0], s0 * k)), a = tc - (q - f.L) / plotW(f) * s1;
  setView(a, a + s1, true);
}
function fling(f, samples, tEnd) {   // momentum after a touch pan: the release speed, decaying with a 325 ms time constant
  const q = samples.filter(v => tEnd - v[0] < 100);
  if (q.length < 2) return;
  let v = (q[q.length - 1][1] - q[0][1]) / Math.max(8, q[q.length - 1][0] - q[0][0]);   // px per ms
  if (Math.abs(v) < 0.25) return;
  v = Math.max(-6, Math.min(6, v));
  let last = performance.now();
  const step = now => {
    const dt = Math.min(48, now - last); last = now;
    const before = S.v[0];
    panPx(f, -v * dt); v *= Math.exp(-dt / 325);
    inertia = Math.abs(v) < 0.02 || S.v[0] === before ? 0 : requestAnimationFrame(step);
  };
  inertia = requestAnimationFrame(step);
}
function gestures(f) {
  const svg = f.svg, pts = new Map();   // pointerId -> {x, y, x0, y0, cx, cy, t0, type, target}
  let mode = null, pinch = null, samples = [], eatClick = false, lastTouch = 0, wg = {axis: null, t: -1e9};
  const px = ev => ev.clientX - svg.getBoundingClientRect().left;
  // two fingers: their distance, floored at 24 px so a two-finger tap cannot divide by nothing, and their midpoint
  const two = () => { const [a, b] = [...pts.values()]; return {d: Math.max(24, Math.hypot(a.x - b.x, a.y - b.y)), c: (a.x + b.x) / 2, v: S.v.slice()}; };
  const tipNode = t => { for (let n = t; n && n !== svg; n = n.parentNode) if (n._ckTip) return n; return null; };
  // capture: the timeline decides first, before a mark's own tooltip handler (CK.tip pins a touch at pointerdown)
  svg.addEventListener('pointerdown', ev => {
    if (!ev.isTrusted) return;   // a tap sent on by tap() below, for the mark's tooltip
    if (ev.pointerType === 'mouse' && ev.button !== 0) return;
    eatClick = false;
    if (inertia || animating) stopMotion();
    if (ev.pointerType === 'touch') { ev.stopPropagation(); lastTouch = Date.now(); }
    const x = px(ev);
    pts.set(ev.pointerId, {x, y: ev.clientY, x0: x, y0: ev.clientY, cx: ev.clientX, cy: ev.clientY, t0: performance.now(), type: ev.pointerType, target: ev.target});
    if (pts.size === 1) { mode = 'pending'; samples = []; }
    else if (pts.size === 2) { pinch = two(); mode = 'pinch'; svg.classList.add('dragging'); }
  }, true);
  svg.addEventListener('pointermove', ev => {
    const p = pts.get(ev.pointerId);
    if (!p) return;
    p.x = px(ev); p.y = ev.clientY;
    if (mode === 'pinch') {
      if (pts.size < 2) return;
      const {d, c} = two(), s0 = pinch.v[1] - pinch.v[0];
      const s1 = Math.max(MINSPAN, Math.min(FULL[1] - FULL[0], s0 * pinch.d / d)), tc = pinch.v[0] + (pinch.c - f.L) / plotW(f) * s0;
      const a0 = tc - (c - f.L) / plotW(f) * s1;
      setView(a0, a0 + s1, true);
      return;
    }
    if (mode === 'pending') {
      const dx = p.x - p.x0, dy = p.y - p.y0;
      if (Math.hypot(dx, dy) < (SLOP[p.type] || 6)) return;
      // decided once: a sideways start pans; any other start is the page's (the browser scrolls it and cancels this pointer)
      if (p.type !== 'mouse' && Math.abs(dx) < 1.2 * Math.abs(dy)) { mode = 'page'; return; }
      mode = 'pan'; p.lx = p.x0; svg.classList.add('dragging');
      try { svg.setPointerCapture(ev.pointerId); } catch (_) { /* no capture */ }
    }
    if (mode === 'pan') {
      const dx = p.x - p.lx; p.lx = p.x;
      if (dx) panPx(f, -dx);
      samples.push([ev.timeStamp, p.x]); if (samples.length > 12) samples.shift();
    }
  });
  const tap = p => {   // a touch that did not move: the mark's details, or a second tap on a flag zooms there
    const n = tipNode(p.target);
    if (n && (n.hasAttribute('data-hl') || n.hasAttribute('data-go')) && f.pinned === n && n._go) { CK.hide(f); n._go(); return; }
    p.target.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true, composed: true, pointerType: 'touch',
      isPrimary: true, pointerId: 1e6, clientX: p.cx, clientY: p.cy}));
  };
  const end = ev => {
    const p = pts.get(ev.pointerId);
    if (!p) return;
    pts.delete(ev.pointerId);
    if (mode === 'pinch') {
      eatClick = true;
      if (pts.size === 1) { const q = [...pts.values()][0]; q.lx = q.x; mode = 'pan'; samples = []; pinch = null; }   // the pinch-to-drag handoff
      else if (!pts.size) { mode = null; pinch = null; svg.classList.remove('dragging'); }
      return;
    }
    if (mode === 'pan') {
      svg.classList.remove('dragging'); eatClick = true;
      if (ev.type === 'pointerup' && p.type !== 'mouse') fling(f, samples, ev.timeStamp);
    } else if (mode === 'pending' && ev.type === 'pointerup' && p.type === 'touch' && performance.now() - p.t0 < 700) tap(p);
    if (!pts.size) mode = null;
  };
  window.addEventListener('pointerup', end); window.addEventListener('pointercancel', end);   // a release outside ends it too
  // a click after a drag, a pinch or any touch is not a click on a mark (a touch tap was handled above)
  svg.addEventListener('click', ev => { if (eatClick || Date.now() - lastTouch < 900) { ev.stopPropagation(); ev.preventDefault(); eatClick = false; } }, true);
  svg.addEventListener('wheel', ev => {
    const unit = ev.deltaMode === 1 ? 16 : ev.deltaMode === 2 ? 400 : 1, dx = ev.deltaX * unit, dy = ev.deltaY * unit;
    if (ev.ctrlKey || ev.metaKey) {
      ev.preventDefault(); if (inertia || animating) stopMotion();
      zoomAt(f, px(ev), Math.exp(Math.max(-0.6, Math.min(0.6, dy * 0.0025))));
      wg = {axis: 'zoom', t: ev.timeStamp};
      return;
    }
    if (ev.timeStamp - wg.t > 240 || wg.axis === 'zoom') wg.axis = Math.abs(dx) > Math.abs(dy) || (ev.shiftKey && dy) ? 'x' : 'y';
    wg.t = ev.timeStamp;
    if (wg.axis !== 'x') return;   // the page's scroll
    ev.preventDefault(); if (inertia || animating) stopMotion();
    panPx(f, Math.abs(dx) >= Math.abs(dy) ? dx : dy);
  }, {passive: false});
}

/* ---------- shared pieces of the two timeline frames ---------- */
function drawTimeAxis(f, x, y, h, W, L, R, bottom) {
  const g = CK.el('g', {'aria-hidden': 'true'}, f.svg), pw = W - L - R, nar = W < 600;
  const tk = ticks(S.v[0], S.v[1], pw, nar ? 58 : 64), labs = [];
  if (!bottom) {  // day names, centred on the visible part of each day
    for (let d = Math.max(0, dayOf(S.v[0])); d <= Math.min(DN.length - 1, dayOf(S.v[1] - 1)); d++) {
      const a = Math.max(d * DAY, S.v[0]), b = Math.min((d + 1) * DAY, S.v[1]);
      if (x(b) - x(a) < (nar ? 40 : 56)) continue;
      labs.push(CK.txt(g, (x(a) + x(b)) / 2, y + 14, nar || x(b) - x(a) < 80 ? DN[d] : `${DN[d]} ${MO(d)}`, 'lab-strong', 'middle'));
    }
  }
  if (tk.step < DAY) for (const t of tk) labs.push(CK.txt(g, x(t), bottom ? y + 16 : y + 31, hm(t), 'tick', 'middle'));
  else if (bottom) for (const t of tk) labs.push(CK.txt(g, x(t) + 4, y + 16, DN[dayOf(t)] || '', 'tick', 'start'));
  lineEl(g, L, bottom ? y + 2 : y + h - 2, W - R, bottom ? y + 2 : y + h - 2, {stroke: 'var(--axis)', strokeWidth: '1px'});
  keepIn(f, labs);
  return tk;
}
// CK.inside, but with estimated widths (0.6 em a character) in a fast frame, which must not force a layout
function keepIn(f, labs) {
  if (!S.drawFast) return CK.inside(f, labs);
  for (const t of labs) {
    const w = 7.2 * t.textContent.length, a = t.getAttribute('text-anchor') || 'start', x = +t.getAttribute('x');
    const x0 = a === 'end' ? x - w : a === 'middle' ? x - w / 2 : x;
    if (x0 < 2) { t.setAttribute('text-anchor', 'start'); t.setAttribute('x', 2); }
    else if (x0 + w > f.W - 2) { t.setAttribute('text-anchor', 'end'); t.setAttribute('x', f.W - 2); }
  }
  return labs;
}
function gridAndDays(f, g, x, y0, y1, tk) {
  for (let d = Math.max(0, dayOf(S.v[0])); d <= dayOf(S.v[1]); d++) {
    if (d % 2) rect(g, x(Math.max(d * DAY, S.v[0])), y0, x(Math.min((d + 1) * DAY, S.v[1])) - x(Math.max(d * DAY, S.v[0])), y1 - y0, mixT('var(--ink)', 3.5));
  }
  for (const t of tk) {
    const mid = t % DAY === 0;
    lineEl(g, x(t), y0, x(t), y1, {stroke: mid ? 'var(--axis)' : 'var(--grid)', strokeWidth: '1px', shapeRendering: 'crispEdges'});
  }
}
function clip(f, id, L, R) {
  const defs = CK.el('defs', {}, f.svg), cp = CK.el('clipPath', {id}, defs);
  CK.el('rect', {x: L, y: 0, width: Math.max(0, f.W - L - R), height: f.H}, cp);
  return `url(#${id})`;
}
const vis = (a, b) => b >= S.v[0] && a <= S.v[1];

/* ---------- tooltips ---------- */
// the owner's own words, as the page may show them: a removed part is marked (rmFmt); the tooltip shows the start
const rmFmt = s0 => esc(s0).replace(/\[(removed: [^\]]*|the report for the lab lead)\]/g, '<span class="rm">[$1]</span>');
const EXC = 360;
const promptTip = (text, lost, img) => text == null || text === ''
  ? (lost ? '<div class="tip-prompt lost">Its words are no longer on the machine: the session’s transcript was rewritten on 2 October, and only the summary was kept.</div>' : '')
  : `<div class="tip-prompt">${rmFmt(text.length > EXC ? text.slice(0, EXC).trimEnd() + ' …' : text)}</div>` +
    `<span class="tip-more">${img ? `with ${img} image${img > 1 ? 's' : ''} (not shown) · ` : ''}${text.length > EXC ? `${num(text.length - EXC, 0)} more characters · ` : ''}click, tap again or press Enter to read it whole</span>`;
const msgTip = m => `<b style="font-size:1.06em">${esc(m.sum)}</b><br>${when(m.t)} · ${HU.cats[m.cat]}${m.rid ? ` · ${m.rid} in the request log` : ''}` +
  `${m.to && LANE_NAME[m.to] ? ` · to ${esc(LANE_NAME[m.to])}` : ''}` +
  promptTip(m.text, false, m.img) +
  `<span style="display:block;font-size:.8em;color:var(--muted)">${num(m.chars, 0)} characters, ${KINDLAB[m.kind] || m.kind}` +
  `${m.act ? ` · about ${dur(m.act)} to write, an estimate` : ''}</span>`;
// a mark whose message the prompt reader opens: a click, a second tap (as on a highlight's flag) or Enter
function readable(f, g, k) {
  if (k == null) return;
  g.setAttribute('data-go', '');
  g._go = () => { CK.hide(f); openPrompt(k); };
  g.addEventListener('click', ev => { ev.stopPropagation(); g._go(); });
  g.style.cursor = 'pointer';
}
/* ---------- the prompt reader: one message's own words, whole; ← and → step to the previous and next message ---------- */
const PV = {k: 0};
function openPrompt(k) {
  const d = document.getElementById('pv'); if (!d || k == null || !PROMPTS[k]) return;
  const p = PROMPTS[k]; PV.k = k;
  document.getElementById('pv-when').innerHTML = `${when(p.t)} · ${esc(HU.cats[p.cat] || '')} · ${esc(KINDLAB[p.kind] || p.kind || '')}` +
    `${p.rid ? ` · request ${esc(p.rid)}` : ''} · to ${esc(p.where)}`;
  document.getElementById('pv-sum').textContent = p.sum;
  const tx = document.getElementById('pv-text');
  if (p.text) { tx.innerHTML = rmFmt(p.text); tx.classList.remove('lost'); }
  else {
    tx.textContent = p.lost ? 'Its words are no longer on the machine: the session’s transcript was rewritten on 2 October, and only the summary was kept.'
      : 'No words were recorded for this message.';
    tx.classList.add('lost');
  }
  const note = [p.img ? `${p.img} image${p.img > 1 ? 's' : ''} came with it (not shown).` : '',
    p.rm.length ? `Removed for this public page: ${p.rm.join(', ')}.` : ''].filter(Boolean).join(' ');
  const nt = document.getElementById('pv-note'); nt.textContent = note; nt.hidden = !note;
  document.getElementById('pv-pos').textContent = `${k + 1} of ${PROMPTS.length}`;
  document.getElementById('pv-prev').disabled = k === 0;
  document.getElementById('pv-next').disabled = k === PROMPTS.length - 1;
  if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); }
  tx.scrollTop = 0;
}
// a label cut to fit a width in pixels (the chart's 12 px text: about 6.6 px a character)
const trunc = (s0, px) => { const n = Math.floor(px / 6.6); return s0.length <= n ? s0 : s0.slice(0, Math.max(1, n - 1)).trimEnd() + '…'; };
const busyTip = b => `<b>Some session was working on the thread</b><br>${span(b.s, b.e)} (${dur(b.e - b.s)})` +
  `<br>the union of every session's busy time: two sessions at once count once here, and the lanes below say which`;
const watchTip = (a, b) => `<b>Watching its workflows</b> ${span(a, b)} (${dur(b - a)})<br>the main agent’s only calls in flight were loops ` +
  `that watched its own workflows or subagents; this time counts as idle, because the subagents’ hours cover it`;
function cardTip(q) {
  const c = CK.card(CA.ids[q.c]);
  return `<b>${q.E ? esc(q.E) + ' · ' : ''}${esc(q.label)}</b>${q.name && q.name !== q.label ? `<br>${esc(q.name)}` : ''}` +
    `<br>${c.label} · ${span(q.s, q.e)} (${dur(q.e - q.s)})<br>${esc(CA.families[q.f].label)}<br>status: ${esc(q.st)}` +
    `${q.die != null ? ` · die ${q.die} °C at the start` : ''}`;
}
const pageTitle = p => esc(p.title);
const depTip = d => { const p = PAGES[d.p];
  return `<b>${pageTitle(p)}</b><br>${when(d.t)} · ${d.nw ? 'first version' : 'a later version'} · ${esc(p.group)}` +
    `${p.summary ? `<br>${esc(p.summary)}` : ''}` +
    `<br>${p.private ? '<i>kept private: it names people, or carries material under an agreement</i>' : `<a href="${esc(p.url)}">read it</a>`}`;
};
function listTip(head, items, fmt, max) {
  const shown = items.slice(0, max).map(fmt).join('<br>');
  return `${head}<br>${shown}${items.length > max ? `<br>and ${items.length - max} more` : ''}`;
}
const comTip = g => listTip(`<b>${g.items.length > 1 ? g.items.length + ' commits' : 'Commit'}</b> ${when(g.t)} · ${esc(AR.sessions[g.items[0].ses])}`,
  g.items, c => `<code>${c.sha}</code> ${esc(c.sub)}`, 6);
function limitNear(t) { const l = MA.limits.find(([u]) => Math.abs(u - t) <= 120); return l ? `<br><b>⚠ usage limit reached</b> (${l[1]}) at ${hm(l[0])}` : ''; }
function runningAt(t) { return NB ? NB.sessions.filter(w => w.s <= t && t <= w.e && w.busy.some(q => q[0] <= t && t <= q[1])).map(w => w.name) : []; }
function cardsAt(t) { return CIV.filter(q => q.s <= t && t < q.e).map(q => `${CK.card(CA.ids[q.c]).label}: ${esc(q.label)}`); }
function mainBusyAt(t) { return BUSY.some(b => b.s <= t && t <= b.e); }

/* ---------- the timeline ---------- */
const halo = n => sty(n, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '3px', strokeLinejoin: 'round'});
const DEPD = DEP.slice().sort((a, b) => a.nw - b.nw || a.t - b.t);   // updates first, so a first publish is never hidden
function drawMain(f) {
  const Y = layout(f.W), {L, R, rows, nar} = Y, W = f.W, svg = f.svg, fast = S.drawFast;
  const want = S.focus; if (want) f.refocus = null;
  f.L = L; f.R = R;
  const x = CK.lin(S.v[0], S.v[1], L, W - R), X = t => Math.max(L - 6, Math.min(W - R + 6, x(t)));
  f.x = x;
  const cp = clip(f, 'tl-clip', L, R), bg = CK.el('g', {'aria-hidden': 'true'}, svg), gut = CK.el('g', {}, svg);
  const ui = CK.el('g', {}, svg), plot = CK.el('g', {'clip-path': cp}, svg), y0 = rows.hl.y, y1 = rows.xaxis.y;
  const tk = drawTimeAxis(f, x, 0, rows.axis.h, W, L, R, false);
  drawTimeAxis(f, x, rows.xaxis.y, rows.xaxis.h, W, L, R, true);
  gridAndDays(f, bg, x, y0, y1, tk);
  const pw = W - L - R;

  // highlights first, so a flag keeps keyboard focus after the zoom it asks for. A flag sits as near its time as the
  // others allow; where that would shrink the flags or move one more than 90 px from its time (a narrow screen at week
  // zoom), flags closer than 24 px merge into one badge ("9–18") that zooms to all of them. A highlight's time is a tick on the flags' row; the
  // dashed line through the tracks shows only while its flag is hovered or focused.
  const hr = rows.hl, hlNodes = [];
  HL.forEach(h => { if (vis(h.a, h.b)) rect(plot, X(h.a), hr.y + hr.h - 5, X(h.b) - X(h.a), 3, mixT('var(--ink)', 22)); });
  const vis0 = HL.map((h, i) => ({h, i, x0: x(h.t), ids: [i]})).filter(o => o.h.t >= S.v[0] && o.h.t <= S.v[1]);
  let items = vis0, gap = Math.min(22, vis0.length > 1 ? (pw - 16) / (vis0.length - 1) : 22);
  const trial = spreadX(vis0.map(o => Object.assign({}, o)), gap, L + 8, W - R - 8);
  if (gap < 18 || trial.some(o => Math.abs(o.x - o.x0) > 90)) {
    const cl = [];
    for (const o of vis0) { const c = cl[cl.length - 1]; if (c && o.x0 - c.last < 24) { c.ids.push(o.i); c.xs.push(o.x0); c.last = o.x0; } else cl.push({ids: [o.i], xs: [o.x0], last: o.x0}); }
    items = cl.map(c => ({i: c.ids[0], ids: c.ids, x0: (c.xs[0] + c.xs[c.xs.length - 1]) / 2, xs: c.xs}));
    items.forEach(o => { o.lab = o.ids.length > 1 ? `${o.ids[0] + 1}–${o.ids[o.ids.length - 1] + 1}` : String(o.i + 1); });
    gap = Math.max(...items.map(o => (o.ids.length > 1 ? 12 + 6.8 * o.lab.length : 19))) + 4;
  }
  spreadX(items, gap, L + 8, W - R - 8);
  const fr = Math.min(9.5, gap / 2 - 0.3);
  items.forEach(o => {
    const cx = o.x, g = CK.el('g', {'data-hl': o.i}, ui), many = o.ids.length > 1;
    const xs = o.xs || [o.x0], lines = [];
    xs.forEach(xt => {
      lineEl(bg, xt, hr.y + hr.h - 7, xt, hr.y + hr.h, {stroke: 'var(--ink-2)', strokeWidth: '1px'});
      if (!fast) lines.push(sty(lineEl(plot, xt, hr.y + hr.h, xt, y1, {stroke: 'var(--ink-2)', strokeWidth: '1px', strokeDasharray: '2 3'}), {display: 'none'}));
    });
    const xm = many ? (xs[0] + xs[xs.length - 1]) / 2 : o.x0;
    if (Math.abs(cx - xm) > 1) lineEl(g, cx, hr.y + 20, xm, hr.y + hr.h - 7, {stroke: 'var(--ink-2)', strokeWidth: '1px'});
    if (many) {
      const w = 10 + 6.8 * o.lab.length;
      sty(CK.el('rect', {x: cx - w / 2, y: hr.y + 1.5, width: w, height: 19, rx: 9.5}, g), {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'});
      sty(CK.txt(g, cx, hr.y + 15, o.lab, 'lab', 'middle'), {fill: 'var(--page)', fontSize: '11px', fontWeight: '700', pointerEvents: 'none'});
    } else {
      sty(CK.el('circle', {cx, cy: hr.y + 11, r: fr}, g), {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'});
      sty(CK.txt(g, cx, hr.y + 15, String(o.i + 1), 'lab', 'middle'), {fill: 'var(--page)', fontSize: '11px', fontWeight: '700', pointerEvents: 'none', letterSpacing: fr < 8 ? '-0.04em' : null});
    }
    g.style.cursor = 'pointer';
    const view = many ? [Math.min(...o.ids.map(k => HL[k].a)), Math.max(...o.ids.map(k => HL[k].b))] : null;
    const go = () => { S.focus = `[data-hl="${o.i}"]`; animateTo(...(many ? [view[0] - 1800, view[1] + 1800] : hlView(HL[o.i]))); };
    g._go = go;
    if (fast) { g.setAttribute('tabindex', '-1'); hlNodes.push(g); return; }   // focusable, for the zoom it asked for
    CK.tip(f, g, many ? `<b>Highlights ${o.lab}</b><br>` + o.ids.map(k => `${k + 1}. ${esc(HL[k].title)} (${when(HL[k].t)})`).join('<br>') + '<br><i>Click, press Enter or tap again to zoom to them.</i>'
      : `<b>${o.i + 1}. ${esc(HL[o.i].title)}</b><br>${span(HL[o.i].a, HL[o.i].b)}<br>${esc(HL[o.i].caption)}<br><i>Click, press Enter or tap again to zoom here.</i>`, {role: 'button'});
    const show = on => lines.forEach(l => { l.style.display = on ? '' : 'none'; });
    g.addEventListener('pointerenter', () => show(true)); g.addEventListener('pointerleave', () => show(false));
    g.addEventListener('focus', () => show(true)); g.addEventListener('blur', () => show(false));
    g.addEventListener('click', go);
    hlNodes.push(g);
  });
  NAV(f, hlNodes, {onEnter: n => n._go()});

  // the axis as a keyboard control: arrows pan, + and − zoom, 0 or Home shows the whole span
  const ax = rect(ui, L, 0, W - L - R, rows.axis.h, 'transparent', {class: 'ck-hit', 'data-axis': '', tabindex: '0'});
  if (!fast) CK.tip(f, ax, () => `<b>Time axis</b>: ${span(S.v[0], S.v[1])}<br>← → pan · + − zoom · 0 the whole span`);
  ax.addEventListener('keydown', ev => {
    const k = ev.key; let did = true;
    S.focus = '[data-axis]';
    if (k === 'ArrowLeft') panBy(-0.25); else if (k === 'ArrowRight') panBy(0.25);
    else if (k === '+' || k === '=') zoomBy(0.5); else if (k === '-' || k === '_') zoomBy(2);
    else if (k === '0' || k === 'Home') animateTo(...FULL); else { did = false; S.focus = null; }
    if (did) { ev.preventDefault(); }
  });

  // track headers: the title in the gutter, a one-line caption over the plot (with a halo, as lines cross it)
  const fit = (s2, px) => { const n = Math.floor(px / 6.4); if (s2.length <= n) return s2; const parts = s2.split(' · '); let o = parts[0];
    if (o.length > n) return ''; for (let i = 1; i < parts.length && (o + ' · ' + parts[i]).length <= n; i++) o += ' · ' + parts[i]; return o; };
  const head = (row, title, cap) => {
    CK.txt(gut, 2, rows[row].y + 13, title, 'lab-strong');
    const c2 = !nar && cap ? fit(cap, pw) : ''; if (c2) halo(CK.txt(gut, L, rows[row].y + 13, c2, 'tick'));
  };
  head('hH', 'QUESTIONS', `${HU.totals.n} asks · a mark each; what was asked shows under it when two days or less are in view, and in its details · faint bar: estimated writing time · shaded: a sitting`);
  head('hA', 'SESSIONS', 'the spine: any session working on the thread · under it one lane per strand, with its key events · below: sessions busy at once');
  head('hC', 'EXPERIMENTS', 'one lane per ET-SoC-1 card, each interval a measurement holding it, shaded by experiment family · below: cards in use, 0 to 4');
  head('hR', 'DOCUMENTS', (S.perPage ? 'one lane per write-up: ● first version, ○ a later one' : 'a bar per minute, its height the number of write-ups published; a dot marks a first version') +
    ' · commits to the lab repository');
  // the session's start and the snapshot's end
  [[D.meta.session_start, 'first ask'], [D.meta.snapshot_end, 'end of the data']].forEach(([t]) => {
    if (!vis(t, t)) return;
    lineEl(plot, x(t), rows.human.y, x(t), y1, {stroke: 'var(--ink-2)', strokeWidth: '1.2px', strokeDasharray: '5 3'});
  });
  if (vis(D.meta.snapshot_end, FULL[1])) rect(plot, X(D.meta.snapshot_end), rows.human.y, X(FULL[1]) - X(D.meta.snapshot_end), y1 - rows.human.y, mixT('var(--ink)', 5));

  // HUMAN
  const hu = rows.human, hy = hu.y + 15;
  CK.txt(gut, 2, hy + 4, nar ? 'asks' : 'my asks', 'lab');
  const gS = CK.el('g', {}, plot), sesNodes = [];
  const gB = CK.el('g', {'aria-hidden': 'true'}, plot), gM = CK.el('g', {}, plot), mNodes = [];
  if (fast) {
    const ps = PB(true), pa = PB(true), pm = [PB(), PB(), PB(), PB(), PB()];
    for (const s of SES) if (vis(s.s, s.e)) ps.rect(X(s.s), hu.y + 1, Math.max(3, X(s.e) - X(s.s)), hu.h - 2);
    ps.flush(gS, {fill: mixT('var(--ink)', 9)});
    for (const m of MSG) if (vis(m.t - m.act, m.t)) pa.rect(X(m.t - m.act), hy - 2, Math.max(1.5, X(m.t) - X(m.t - m.act)), 4);
    pa.flush(gB, {fill: 'var(--ink-2)', opacity: 0.22});
    for (const m of MSG) if (vis(m.t, m.t)) markPath(pm, m.cat, x(m.t), hy, 1);
    flushMarks(pm, gM);
  } else {
    for (const s of SES) {
      if (!vis(s.s, s.e)) continue;
      const n = rect(gS, X(s.s), hu.y + 1, Math.max(3, X(s.e) - X(s.s)), hu.h - 2, mixT('var(--ink)', 9), {rx: 3});
      TIP(f, n, () => `<b>Engagement session ${s.i + 1}</b>: ${span(s.s, s.e)}<br>${s.n} message${s.n > 1 ? 's' : ''}; estimated active ${dur(s.act)}` +
        `${s.actp < s.act - 1 ? ` (${dur(s.actp)} with pasted text not counted as typing)` : ''}<br>the session starts when its first message was being read and written (estimate)`);
      sesNodes.push(n);
    }
    for (const m of MSG) { if (vis(m.t - m.act, m.t)) sty(rect(gB, X(m.t - m.act), hy - 2, Math.max(1.5, X(m.t) - X(m.t - m.act)), 4, 'var(--ink-2)', {rx: 1}), {opacity: 0.22}); }
    for (const m of MSG) {
      if (!vis(m.t, m.t)) continue;
      const g = CK.el('g', {}, gM), cx = x(m.t);
      CK.el('circle', {cx, cy: hy, r: 8, class: 'ck-hit'}, g);
      humanMark(g, m.cat, cx, hy);
      TIP(f, g, () => msgTip(m)); mNodes.push(g);
      readable(f, g, pidx('the main session', m.t, m.sum));
    }
  }
  // what was asked: when two days or less are in view, each message's summary under the marks, starting at its mark
  // (a hairline joins them), the rows taken in turn and each summary cut to end before the next one in its row; a
  // summary with too little room stays in the mark's details and in §3's list
  if (S.v[1] - S.v[0] <= 2 * DAY) {
    const gL = CK.el('g', {'aria-hidden': 'true'}, plot), right = W - R - 4, vm = MSG.filter(m => vis(m.t, m.t)), hair = PB();
    vm.forEach((m, k) => {
      const r = k % 3, x0 = x(m.t) - 3, stop = k + 3 < vm.length ? x(vm[k + 3].t) - 13 : right;
      const w = Math.min(360, stop - x0, m.sum.length * 6.9 + 4);
      if (w < 44) return;
      const ly = hu.y + 30 + 12 + r * ASK_ROW;
      hair.line(x(m.t), hy + 6, x(m.t), ly - 10);
      const lab = sty(CK.txt(gL, x0, ly, trunc(m.sum, w), 'tick'), {fill: 'var(--ink)', fontSize: '12.5px', fontWeight: 500});
      if (!fast) halo(lab);
    });
    hair.flush(gL, {stroke: 'var(--axis)', strokeWidth: '1px', fill: 'none'});
  }
  NAV(f, mNodes, {onEnter: n => n._go && n._go()}); NAV(f, sesNodes);
  // AGENTS: the main agent (tint: busy; solid: active; dotted: watching its own workflows, counted idle)
  const mr = rows.main;
  CK.txt(gut, 2, mr.y + 13, nar ? 'any' : 'any session', 'lab');
  const gm = CK.el('g', {}, plot), bNodes = [], wNodes = [];
  if (fast) {
    const pt = PB(true), pa = PB(true), pwt = PB();
    for (const b of BUSY) if (vis(b.s, b.e)) pt.rect(X(b.s), mr.y + 2, Math.max(2, X(b.e) - X(b.s)), mr.h - 4);
    for (const [s0, e0] of STRICT) if (vis(s0, e0)) pa.rect(X(s0), mr.y + 2, Math.max(1, X(e0) - X(s0)), mr.h - 4);
    for (const [a, b] of WATCH) if (vis(a, b)) pwt.line(X(a), mr.y + mr.h / 2, X(b), mr.y + mr.h / 2);
    pt.flush(gm, {fill: mixT('var(--c7)', 32)}); pa.flush(gm, {fill: 'var(--c7)'});
    pwt.flush(gm, {stroke: COL.main, strokeWidth: '2px', strokeDasharray: '1.5 3', strokeLinecap: 'round', fill: 'none'});
  } else {
    let si = 0;
    for (const b of BUSY) {
      if (!vis(b.s, b.e)) continue;
      const g = CK.el('g', {}, gm), a = X(b.s), w = Math.max(2, X(b.e) - a);
      rect(g, a, mr.y + 2, w, mr.h - 4, mixT('var(--c7)', 32), {rx: 2});
      while (si < STRICT.length && STRICT[si][1] < b.s) si++;
      for (let j = si; j < STRICT.length && STRICT[j][0] <= b.e; j++) {
        const s = Math.max(STRICT[j][0], b.s), e = Math.min(STRICT[j][1], b.e);
        if (e > s && vis(s, e)) rect(g, X(s), mr.y + 2, Math.max(1, X(e) - X(s)), mr.h - 4, 'var(--c7)', {'aria-hidden': 'true'});
      }
      TIP(f, g, () => busyTip(b)); bNodes.push(g);
    }
    for (const [a, b] of WATCH) {
      if (!vis(a, b)) continue;
      const g = CK.el('g', {}, gm);
      CK.el('rect', {x: X(a), y: mr.y + 2, width: Math.max(4, X(b) - X(a)), height: mr.h - 4, class: 'ck-hit'}, g);
      lineEl(g, X(a), mr.y + mr.h / 2, X(b), mr.y + mr.h / 2, {stroke: COL.main, strokeWidth: '2px', strokeDasharray: '1.5 3', strokeLinecap: 'round'});
      TIP(f, g, () => watchTip(a, b)); wNodes.push(g);
    }
  }
  NAV(f, bNodes); NAV(f, wNodes);
  // usage limits: a marker over the main agent's row (the subagent lane below says so in its tooltip)
  const limNodes = [];
  MA.limits.forEach(([t, kind]) => {
    if (!vis(t, t)) return;
    const g = CK.el('g', {}, plot);
    lineEl(g, x(t), mr.y, x(t), mr.y + mr.h + 3, {stroke: 'var(--bad)', strokeWidth: '1.6px', strokeDasharray: '3 2'});
    sty(CK.el('polygon', {points: `${x(t) - 5},${mr.y - 1} ${x(t) + 5},${mr.y - 1} ${x(t)},${mr.y + 7}`}, g), {fill: 'var(--bad)'});
    if (fast) return;
    CK.el('rect', {x: x(t) - 6, y: mr.y - 2, width: 12, height: mr.h + 6, class: 'ck-hit'}, g);
    CK.tip(f, g, `<b>⚠ Usage limit reached</b> (${kind}), ${when(t)}<br>the agents stopped until it reset`); limNodes.push(g);
  });
  NAV(f, limNodes);

  // SESSIONS: one lane per strand of the thread - its busy time and its key events (a marker each)
  if (NB) NB.sessions.forEach((nb, k) => {
    const r = rows['nb' + k], gN = CK.el('g', {}, plot), nNodes = [], eNodes = [];
    CK.txt(gut, 2, r.y + 14, trunc(nb.lane || 'session', L - 5), 'lab');
    if (fast) {
      const ps = PB(true), pb = PB(true);
      for (const [a, b] of nb.sub) if (vis(a, b)) ps.rect(X(a), r.y + r.h - 6, Math.max(1, X(b) - X(a)), 3);
      for (const [a, b] of nb.busy) if (vis(a, b)) pb.rect(X(a), r.y + 3, Math.max(2, X(b) - X(a)), r.h - 11);
      ps.flush(gN, {fill: mixT('var(--c4)', 75)}); pb.flush(gN, {fill: 'var(--ref)'});
    } else {
      for (const [a, b] of nb.sub) if (vis(a, b)) rect(gN, X(a), r.y + r.h - 6, Math.max(1, X(b) - X(a)), 3, mixT('var(--c4)', 75), {'aria-hidden': 'true'});
      for (const [a, b] of nb.busy) {
        if (!vis(a, b)) continue;
        const n = rect(gN, X(a), r.y + 3, Math.max(2, X(b) - X(a)), r.h - 11, 'var(--ref)', {rx: 2});
        TIP(f, n, () => `<b>${esc(nb.name)}</b> · ${span(a, b)} (${dur(b - a)})<br>${esc(nb.title)}` +
          `<br>${nb.n > 1 ? `${nb.n} sessions` : 'one session'} on ${esc(nb.machine)} · ${nb.asks} ask${nb.asks === 1 ? '' : 's'} of mine · ${hrs(nb.busy_h, 1)} working in all`); nNodes.push(n);
      }
    }
    NAV(f, nNodes);
    nb.events.forEach(([t, e, kind, title, text]) => {
      if (!vis(t, e > t ? e : t)) return;
      const g = CK.el('g', {}, plot), cx = x(t), red = kind === 'hang' || kind === 'power' || kind === 'reboot' || kind === 'down';
      if (e > t) rect(g, X(t), r.y + r.h - 2, Math.max(1, X(e) - X(t)), 2, red ? 'var(--bad)' : 'var(--ink-2)', {'aria-hidden': 'true'});
      if (red) sty(CK.el('polygon', {points: `${cx - 5},${r.y} ${cx + 5},${r.y} ${cx},${r.y + 8}`}, g), {fill: 'var(--bad)', stroke: 'var(--page)', strokeWidth: '1px'});
      else sty(CK.el('polygon', {points: `${cx},${r.y} ${cx + 4.5},${r.y + 4.5} ${cx},${r.y + 9} ${cx - 4.5},${r.y + 4.5}`}, g), {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'});
      if (fast) return;
      CK.el('rect', {x: cx - 7, y: r.y - 1, width: 14, height: r.h, class: 'ck-hit'}, g);
      CK.tip(f, g, `<b>${esc(title)}</b>, ${e > t ? span(t, e) : when(t)}<br>${esc(text)}`); eNodes.push(g);
    });
    NAV(f, eNodes);
  });

  // AGENTS: subagents busy at once, stacked: workflow agents, Agent-tool agents and forks, then the agents that failed or
  // ended on an error. The scale follows the agents that did not fail; failed starts above it are clipped and the
  // highest count in view is labelled at its minute.
  const cr = rows.conc, base = cr.y + cr.h;
  const i0 = Math.max(0, Math.floor((S.v[0] - C0) / 60)), i1 = Math.min(CW.length, Math.ceil((S.v[1] - C0) / 60));
  const per = Math.max(1, Math.ceil((i1 - i0) / pw)), B = [];
  let topOk = 0, topAll = 0, topAt = null;
  for (let i = i0; i < i1; i += per) {
    let best = -1, bj = i;
    for (let j = i; j < Math.min(i + per, i1); j++) {
      const t2 = CW[j] + CT[j]; if (t2 > best) { best = t2; bj = j; }
      topOk = Math.max(topOk, OW[j] + OT[j]);
      if (t2 > topAll) { topAll = t2; topAt = C0 + (j + 0.5) * 60; }
    }
    B.push([C0 + i * 60, C0 + Math.min(i + per, i1) * 60, OW[bj], OT[bj], CF[bj]]);
  }
  const ymax = niceMax(Math.max(4, topOk));
  const yc = v => CK.lin(0, ymax, base, cr.y + 6)(Math.min(v, ymax));
  lineEl(bg, L, yc(ymax), W - R, yc(ymax), {stroke: 'var(--grid)', strokeWidth: '1px', strokeDasharray: '3 3'});
  lineEl(bg, L, base, W - R, base, {stroke: 'var(--axis)', strokeWidth: '1px'});
  if (nar) halo(CK.txt(svg, L + 3, yc(ymax) + 11, String(ymax), 'tick'));
  else { CK.txt(gut, L - 6, yc(ymax) + 4, String(ymax), 'tick', 'end'); CK.txt(gut, L - 6, base, '0', 'tick', 'end'); }
  CK.txt(gut, 2, cr.y + 14, 'sessions', 'lab');
  if (!nar) CK.txt(gut, 2, cr.y + 30, 'busy at once', 'tick');
  if (B.length) {
    const area = (lo, hi) => {
      const r1 = v => Math.round(v * 10) / 10;
      let d = `M${r1(X(B[0][0]))},${r1(yc(lo(B[0])))}`;
      for (const b of B) d += `L${r1(X(b[0]))},${r1(yc(hi(b)))}L${r1(X(b[1]))},${r1(yc(hi(b)))}`;
      for (let k = B.length - 1; k >= 0; k--) d += `L${r1(X(B[k][1]))},${r1(yc(lo(B[k])))}L${r1(X(B[k][0]))},${r1(yc(lo(B[k])))}`;
      return d + 'Z';
    };
    sty(CK.el('path', {d: area(() => 0, b => b[2])}, plot), {fill: COL.wf, shapeRendering: 'crispEdges'});
    sty(CK.el('path', {d: area(b => b[2], b => b[2] + b[3])}, plot), {fill: COL.tool, shapeRendering: 'crispEdges'});
    sty(CK.el('path', {d: area(b => b[2] + b[3], b => b[2] + b[3] + b[4])}, plot), {fill: COL.fail, shapeRendering: 'crispEdges'});
    if (topAll > ymax && topAt != null) {
      const tx = X(topAt);
      sty(CK.el('polygon', {points: `${tx - 4},${cr.y + 5} ${tx + 4},${cr.y + 5} ${tx},${cr.y}`}, plot), {fill: 'var(--ink)'});
      halo(CK.txt(plot, tx + 6, cr.y + 10, `${topAll} (failed starts clipped)`, 'tick', 'start'));
    }
  }
  const track = (hit, ln) => {
    hit.addEventListener('pointermove', ev => { const p = ev.clientX - svg.getBoundingClientRect().left; f.cx = p; ln.setAttribute('x1', p); ln.setAttribute('x2', p); ln.style.display = ''; });
    hit.addEventListener('pointerleave', () => { f.cx = null; ln.style.display = 'none'; });
    hit.addEventListener('focus', () => { f.cx = null; });
  };
  if (!fast) {
    const cross = sty(CK.el('line', {x1: 0, x2: 0, y1: cr.y, y2: base}, plot), {stroke: 'var(--ink)', strokeWidth: '1px', display: 'none', pointerEvents: 'none'});
    const hitC = rect(svg, L, cr.y, pw, cr.h, 'transparent', {class: 'ck-hit'});
    track(hitC, cross);
    CK.tip(f, hitC, () => {
      if (f.cx == null) {  // keyboard: the peaks of the window in view
        let pk = -1, pi = i0, po = -1, poi = i0;
        for (let j = i0; j < i1; j++) { if (CW[j] + CT[j] > pk) { pk = CW[j] + CT[j]; pi = j; } if (OW[j] + OT[j] > po) { po = OW[j] + OT[j]; poi = j; } }
        return `<b>Subagents busy at once</b>, ${span(S.v[0], S.v[1])}<br>peak ${Math.max(0, po)}${po > 0 ? ` at ${when(C0 + poi * 60)}` : ''}, not counting agents that failed` +
          `${pk > po ? `; ${pk} with them, at ${when(C0 + pi * 60)}` : ''}<br>move the pointer over the chart for any minute`;
      }
      const t = x.inv(f.cx), j = Math.floor((t - C0) / 60), ow = OW[j] || 0, ot = OT[j] || 0, cf = CF[j] || 0, n = ow + ot + cf, run = runningAt(t);
      return `<b>${when(t)}</b><br>${n} subagent${n === 1 ? '' : 's'} busy: ${ow} workflow agent${ow === 1 ? '' : 's'}, ${ot} Agent-tool agent${ot === 1 ? '' : 's'} or forks` +
        `${cf ? `, and ${cf} that failed or ended on an error` : ''}<br>main agent ${mainBusyAt(t) ? 'busy' : 'idle'}${run.length ? `<br>workflow running: ${run.map(esc).join(', ')}` : ''}${limitNear(t)}`;
    });
  }

  // CARDS: one lane each, coloured by card (or by experiment family); development runs outlined, under the rest
  const cNodes = [];
  CA.ids.forEach((id, k) => {
    const r = rows['card' + k], c = CK.card(id), cy = r.y + r.h / 2, nodes = [];
    rect(bg, L, r.y + 1, pw, r.h - 2, mixT(c.color, 7));
    CK.cardMark(gut, id, nar ? 7 : 9, cy, 4);
    CK.txt(gut, nar ? 16 : 20, cy + 4, nar ? c.short : c.label, 'lab');
    if (fast) {   // one path per fill: the development runs, then the wide intervals (a page-coloured edge) and the narrow ones
      const P = new Map(), get = (key, style) => { if (!P.has(key)) P.set(key, {p: PB(key[0] === 'n'), style}); return P.get(key).p; };
      for (const pass of [0, 1]) for (const q of CIV) {
        if (q.c !== k || (q.f === DEVF) !== (pass === 0) || !vis(q.s, q.e)) continue;
        const w = Math.max(1.5, X(q.e) - X(q.s)), dev = q.f === DEVF, fill = S.cardMode === 'card' ? c.color : FAMCOL[q.f];
        if (dev) get('dev', {fill: famFill(q.f, S.cardMode === 'card' ? c.color : null), stroke: S.cardMode === 'card' ? c.color : 'var(--ink-2)', strokeWidth: '1px'}).rect(X(q.s), r.y + 2, w, r.h - 4);
        else get((w > 5 ? 'w' : 'n') + fill, w > 5 ? {fill, stroke: 'var(--page)', strokeWidth: '1px'} : {fill}).rect(X(q.s), r.y + 2, w, r.h - 4);
      }
      for (const {p, style} of P.values()) p.flush(plot, style);
    } else {
      for (const pass of [0, 1]) for (const q of CIV) {
        if (q.c !== k || (q.f === DEVF) !== (pass === 0) || !vis(q.s, q.e)) continue;
        const w = Math.max(1.5, X(q.e) - X(q.s)), dev = q.f === DEVF;
        const n = rect(plot, X(q.s), r.y + 2, w, r.h - 4, dev ? famFill(q.f, S.cardMode === 'card' ? c.color : null) : S.cardMode === 'card' ? c.color : FAMCOL[q.f]);
        if (dev) sty(n, {stroke: S.cardMode === 'card' ? c.color : 'var(--ink-2)', strokeWidth: '1px'});
        else if (w > 5) sty(n, {stroke: 'var(--page)', strokeWidth: '1px'});
        TIP(f, n, () => cardTip(q)); nodes.push(n);
      }
      nodes.sort((a, b) => +a.getAttribute('x') - +b.getAttribute('x'));
    }
    cNodes.push(nodes);
  });
  cNodes.forEach(n => NAV(f, n));
  // the hosts down: hung (aifoundry1 after its link retrain) or switched off (the power cycle), over their cards' lanes
  const hNodes = [];
  HOSTEV.forEach(h => {
    if (!vis(h.s, h.e)) return;
    h.cards.forEach(k => {
      const r = rows['card' + k], a = X(h.s), w = Math.max(3, X(h.e) - a), g = CK.el('g', {}, plot);
      sty(rect(g, a, r.y + 1, w, r.h - 2, mixT('var(--bad)', h.kind === 'hang' ? 22 : 45)), {stroke: 'var(--bad)', strokeWidth: '1px'});
      if (fast) return;
      CK.el('rect', {x: a - 3, y: r.y, width: w + 6, height: r.h, class: 'ck-hit'}, g);
      CK.tip(f, g, `<b>${esc(h.title)}</b>: ${span(h.s, h.e)} (${dur(h.e - h.s)})<br>${esc(h.text)}`); hNodes.push(g);
    });
  });
  NAV(f, hNodes);
  // cards in use, 0 to 4: the bar's height is the count (faint lines at 1, 2 and 3)
  const ur = rows.inuse, ub = ur.y + ur.h - 1, uh = ur.h - 6;
  for (const n of [1, 2, 3]) lineEl(bg, L, ub - n / 4 * uh, W - R, ub - n / 4 * uh, {stroke: 'var(--grid)', strokeWidth: '1px', strokeDasharray: '1 3'});
  {
    const pu = [null, PB(true), PB(true), PB(true), PB(true)];
    let t = INU.start;
    for (const [n, cnt] of INU.rle) {
      const s = t, e = t + cnt * INU.step; t = e;
      if (!n || !vis(s, e)) continue;
      pu[n].rect(X(s), ub - n / 4 * uh, Math.max(1, X(e) - X(s)), n / 4 * uh);
    }
    for (const n of [1, 2, 3, 4]) pu[n].flush(plot, {fill: INUSE_FILL[n]});
  }
  lineEl(bg, L, ub - uh, W - R, ub - uh, {stroke: 'var(--grid)', strokeWidth: '1px', strokeDasharray: '3 3'});
  lineEl(bg, L, ub, W - R, ub, {stroke: 'var(--axis)', strokeWidth: '1px'});
  if (nar) halo(CK.txt(svg, L + 3, ub - uh + 11, '4', 'tick'));
  else { CK.txt(gut, L - 6, ub - uh + 4, '4', 'tick', 'end'); CK.txt(gut, L - 6, ub - uh / 2 + 4, '2', 'tick', 'end'); CK.txt(gut, L - 6, ub, '0', 'tick', 'end'); }
  CK.txt(gut, 2, ur.y + 14, nar ? 'in use' : 'cards in use', 'lab');
  if (!fast) {
    const crossU = sty(CK.el('line', {x1: 0, x2: 0, y1: ur.y, y2: ub}, plot), {stroke: 'var(--ink)', strokeWidth: '1px', display: 'none', pointerEvents: 'none'});
    const hitU = rect(svg, L, ur.y, pw, ur.h, 'transparent', {class: 'ck-hit'});
    track(hitU, crossU);
    CK.tip(f, hitU, () => {
      if (f.cx == null) {
        const mins = [0, 0, 0, 0, 0]; let tt = INU.start;
        for (const [n, cnt] of INU.rle) { const s = tt, e = tt + cnt * 60; tt = e; mins[n] += Math.max(0, Math.min(e, S.v[1]) - Math.max(s, S.v[0])) / 60; }
        return `<b>Cards in use</b>, ${span(S.v[0], S.v[1])}<br>` + [4, 3, 2, 1].filter(n => mins[n] > 0).map(n => `${n} card${n > 1 ? 's' : ''}: ${dur(mins[n] * 60)}`).join('<br>');
      }
      const tt = x.inv(f.cx), j = Math.floor((tt - INU.start) / 60), n = INV[j] || 0, at = cardsAt(tt);
      return `<b>${when(tt)}</b><br>${n} card${n === 1 ? '' : 's'} in use${at.length ? '<br>' + at.join('<br>') : ''}`;
    });
  }

  // ARTIFACTS: deploys, one row of counts per minute or one lane per page
  const dNodes = [];
  if (S.perPage) {
    const maxc = Math.floor((L - 6) / 6.1);
    PAGES.forEach((p, k) => {
      const r = rows['page' + k], cy = r.y + r.h / 2;
      if (k % 2) rect(bg, L, r.y, pw, r.h, mixT('var(--ink)', 3));
      const lab = p.short.length > maxc ? p.short.slice(0, maxc - 1) + '…' : p.short;
      sty(CK.txt(gut, L - 8, cy + 4, lab, 'lab', 'end'), {fontSize: '11px'});
    });
    if (fast) {
      const pn = PB(), pu = PB();
      for (const d of DEPD) { if (!vis(d.t, d.t)) continue; const cy = rows['page' + d.p].y + rows['page' + d.p].h / 2; (d.nw ? pn : pu).circle(x(d.t), cy, d.nw ? 3.8 : 3.2); }
      pu.flush(plot, {fill: 'var(--page)', stroke: 'var(--ink)', strokeWidth: '1.5px'}); pn.flush(plot, {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'});
    } else {
      for (const d of DEPD) {
        if (!vis(d.t, d.t)) continue;
        const r = rows['page' + d.p], cy = r.y + r.h / 2, g = CK.el('g', {}, plot);
        CK.el('circle', {cx: x(d.t), cy, r: 6, class: 'ck-hit'}, g);
        const c = CK.el('circle', {cx: x(d.t), cy, r: d.nw ? 3.8 : 3.2}, g);
        sty(c, d.nw ? {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'} : {fill: 'var(--page)', stroke: 'var(--ink)', strokeWidth: '1.5px'});
        TIP(f, g, () => depTip(d)); dNodes.push(g);
      }
      dNodes.sort((a, b) => +a.firstChild.getAttribute('cx') - +b.firstChild.getAttribute('cx'));
    }
  } else {
    const r = rows.deploys, maxN = Math.max(...DEPM.map(g => g.items.length)), bh = r.h - 8;
    CK.txt(gut, 2, r.y + 16, 'deploys', 'lab');
    const pbar = PB(), pdot = PB();
    for (const g0 of DEPM) {
      if (!vis(g0.t, g0.t)) continue;
      const n = g0.items.length, h = Math.max(4, n / maxN * bh);
      if (fast) { pbar.rect(x(g0.t) - 1.5, r.y + r.h - 2 - h, 3, h); if (g0.items.some(d => d.nw)) pdot.circle(x(g0.t), r.y + r.h - 2 - h - 3.5, 2.8); continue; }
      const g = CK.el('g', {}, plot);
      CK.el('rect', {x: x(g0.t) - 4, y: r.y, width: 8, height: r.h, class: 'ck-hit'}, g);
      rect(g, x(g0.t) - 1.5, r.y + r.h - 2 - h, 3, h, 'var(--ink)', {rx: 1});
      if (g0.items.some(d => d.nw)) sty(CK.el('circle', {cx: x(g0.t), cy: r.y + r.h - 2 - h - 3.5, r: 2.8}, g), {fill: 'var(--ink)'});
      TIP(f, g, () => listTip(`<b>${n} deploy${n > 1 ? 's' : ''}</b> ${when(g0.t)}`, g0.items,
        d => `${d.nw ? '● ' : '○ '}${PAGES[d.p].private ? esc(PAGES[d.p].title) : esc(PAGES[d.p].short)}`, 8));
      dNodes.push(g);
    }
    pbar.flush(plot, {fill: 'var(--ink)'}); pdot.flush(plot, {fill: 'var(--ink)'});
  }
  NAV(f, dNodes);
  // commits: a tall tick for this session, a short one for another session
  const co = rows.commits, kNodes = [];
  CK.txt(gut, S.perPage ? L - 8 : 2, co.y + 12, 'commits', 'lab', S.perPage ? 'end' : 'start');
  const pc = [PB(), PB()];
  for (const g0 of COMM) {
    if (!vis(g0.t, g0.t)) continue;
    const other = g0.items[0].ses !== 0;
    if (fast) { pc[other ? 1 : 0].rect(x(g0.t) - 1.5, other ? co.y + co.h / 2 : co.y + 1, 3, other ? co.h / 2 - 1 : co.h - 2); continue; }
    const g = CK.el('g', {}, plot);
    CK.el('rect', {x: x(g0.t) - 4, y: co.y, width: 8, height: co.h, class: 'ck-hit'}, g);
    rect(g, x(g0.t) - 1.5, other ? co.y + co.h / 2 : co.y + 1, 3, other ? co.h / 2 - 1 : co.h - 2, other ? 'var(--muted)' : 'var(--ink-2)');
    TIP(f, g, () => comTip(g0)); kNodes.push(g);
  }
  pc[0].flush(plot, {fill: 'var(--ink-2)'}); pc[1].flush(plot, {fill: 'var(--muted)'});
  NAV(f, kNodes);

  if (want) { const n = svg.querySelector(want); if (n) n.focus({preventScroll: true}); }
}
// the owner's marks in a fast frame: one path per category (dot, diamond, box, ring, bar), scaled by k
function markPath(pm, cat, cx, cy, k) {
  const p = pm[cat] || pm[0];
  if (cat === 1) p.diamond(cx, cy, 5 * k);
  else if (cat === 2) p.rect(cx - 3.8 * k, cy - 3.8 * k, 7.6 * k, 7.6 * k);
  else if (cat === 3) p.circle(cx, cy, 3.8 * k);
  else if (cat === 4) p.rect(cx - 1.3 * k, cy - 6 * k, 2.6 * k, 12 * k);
  else p.circle(cx, cy, 4.2 * k);
}
function flushMarks(pm, g) {
  pm.forEach((p, c) => p.flush(g, c === 3 ? {fill: 'var(--page)', stroke: 'var(--ink)', strokeWidth: '2px'} : {fill: 'var(--ink)', stroke: 'var(--page)', strokeWidth: '1px'}));
}
function humanMark(g, cat, cx, cy) {
  const ink = 'var(--ink)';
  let e;
  if (cat === 1) e = CK.el('polygon', {points: `${cx},${cy - 5} ${cx + 5},${cy} ${cx},${cy + 5} ${cx - 5},${cy}`}, g);
  else if (cat === 2) e = CK.el('rect', {x: cx - 3.8, y: cy - 3.8, width: 7.6, height: 7.6}, g);
  else if (cat === 3) return sty(CK.el('circle', {cx, cy, r: 3.8}, g), {fill: 'var(--page)', stroke: ink, strokeWidth: '2px'});
  else if (cat === 4) e = CK.el('rect', {x: cx - 1.3, y: cy - 6, width: 2.6, height: 12}, g);
  else e = CK.el('circle', {cx, cy, r: 4.2}, g);
  return sty(e, {fill: ink, stroke: 'var(--page)', strokeWidth: '1px'});
}

/* ---------- the subagent detail: one thin lane per concurrently running agent, grouped by workflow ---------- */
const GAG = GRP.map((g, i) => AGR.filter(a => a.g === i));
// a group's name, with its start where two workflow runs share a name
const GNAME = GRP.map(g => g.name);
function detailGroups() { return GRP.map((g, i) => Object.assign({i}, g)).filter(g => GAG[g.i].some(a => vis(a.s, a.e))); }
const laneH = () => (S.v[1] - S.v[0] > 2 * DAY ? 1.2 : 3);   // lanes thin out when more than two days are in view
function detailLayout(W) {  // on a phone a group's name sits over its lanes, on a line of its own, instead of in the gutter
  const gs = detailGroups(), nar = W < 600, lh = laneH(); let y = 46;
  gs.forEach(g => { g.y = y; g.top = nar ? 14 : 0; g.h = Math.max(16, g.top + g.lanes * lh + 6); y += g.h + 2; });
  return {gs, H: gs.length ? y + 4 : 80};
}
function drawDetail(f) {
  const Y = layout(f.W), {L, R, nar} = Y, W = f.W, svg = f.svg, DL = detailLayout(W), lh = laneH();
  f.L = L; f.R = R;
  const x = CK.lin(S.v[0], S.v[1], L, W - R), X = t => Math.max(L - 6, Math.min(W - R + 6, x(t)));
  f.x = x;
  const cp = clip(f, 'tld-clip', L, R), bg = CK.el('g', {'aria-hidden': 'true'}, svg), gut = CK.el('g', {}, svg), plot = CK.el('g', {'clip-path': cp}, svg);
  const tk = drawTimeAxis(f, x, 0, 40, W, L, R, false);
  gridAndDays(f, bg, x, 40, f.H, tk);
  CK.txt(gut, 2, 14, nar ? 'SESSIONS' : 'EVERY SESSION', 'lab-strong');
  if (!DL.gs.length) { CK.txt(svg, L + 8, 64, 'No session ran in this window.', 'lab'); return; }
  const gNodes = [], aNodes = [], maxc = Math.floor((L - 6) / 6.1);
  DL.gs.forEach((g, k) => {
    if (k % 2) rect(bg, 0, g.y - 1, W, g.h + 2, mixT('var(--ink)', 3));
    const w = g.wf >= 0 ? WFS[g.wf] : null, name = GNAME[g.i];
    const lab = nar ? halo(CK.txt(gut, L + 2, g.y + 11, name, 'lab')) : CK.txt(gut, 2, g.y + 11, name.length > maxc ? name.slice(0, maxc - 1) + '…' : name, 'lab');
    sty(lab, {fontSize: '11px'}).setAttribute('aria-hidden', 'true');
    const hit = CK.el('rect', nar ? {x: 0, y: g.y, width: L + 2 + 6.2 * name.length, height: 13, class: 'ck-hit'} : {x: 0, y: g.y, width: L - 4, height: Math.max(14, g.h), class: 'ck-hit'}, gut);
    TIP(f, hit, () => `<b>${esc(name)}</b><br>${g.n} session${g.n === 1 ? '' : 's'} on the thread · ${span(g.s, g.e)}` +
      `<br>${num(GAG[g.i].reduce((a, x) => a + x.busy, 0) / 60, 1)} session-hours of work`);
    gNodes.push(hit);
  });
  const gi = {}; DL.gs.forEach(g => { gi[g.i] = g; });
  const PF = {}, pf = c => PF[c] || (PF[c] = {thin: PB(), busy: PB()});   // a fast frame: two paths per colour
  for (const a of AGR) {
    const g = gi[a.g]; if (!g || !vis(a.s, a.e)) continue;
    const cy = g.y + g.top + 3 + a.lane * lh + lh / 2, c = a.st === 'failed' || a.st === 'error' || a.st === 'killed' ? COL.fail : a.kind === 'workflow' ? COL.wf : COL.tool;
    if (S.drawFast) {
      const q2 = pf(c);
      if (lh >= 2) q2.thin.rect(X(a.s), cy - 0.6, Math.max(1, X(a.e) - X(a.s)), 1.2);
      for (const q of a.iv) if (vis(q[0], q[1])) q2.busy.rect(X(q[0]), cy - Math.min(1.3, lh / 2), Math.max(1.2, X(q[1]) - X(q[0])), Math.min(2.6, lh));
      continue;
    }
    const n = CK.el('g', {}, plot);
    CK.el('rect', {x: X(a.s) - 2, y: cy - Math.max(1.5, lh), width: Math.max(6, X(a.e) - X(a.s) + 4), height: Math.max(3, 2 * lh), class: 'ck-hit'}, n);
    if (lh >= 2) sty(rect(n, X(a.s), cy - 0.6, Math.max(1, X(a.e) - X(a.s)), 1.2, c), {opacity: 0.45});
    for (const q of a.iv) if (vis(q[0], q[1])) rect(n, X(q[0]), cy - Math.min(1.3, lh / 2), Math.max(1.2, X(q[1]) - X(q[0])), Math.min(2.6, lh), c);
    TIP(f, n, () => `<b>${esc(a.label)}</b><br>${esc(GNAME[a.g])} · ${esc(a.kind)}${a.phase ? ` · ${esc(a.phase)}` : ''}` +
      `<br>${span(a.s, a.e)} · working ${dur(a.busy * 60)}`);
    aNodes.push(n);
  }
  for (const c in PF) { PF[c].thin.flush(plot, {fill: c, opacity: 0.45}); PF[c].busy.flush(plot, {fill: c}); }
  NAV(f, gNodes); NAV(f, aNodes);
}

/* ---------- controls, legends, readout ---------- */
function button(host, label, onClick, o) {
  const b = document.createElement('button'); b.type = 'button'; b.textContent = label;
  if (o && o.aria) b.setAttribute('aria-label', o.aria);
  if (o && o.cls) b.className = o.cls;
  if (o && o.view) { b.setAttribute('aria-pressed', 'false'); b._view = o.view; }
  b.addEventListener('click', onClick); host.appendChild(b); return b;
}
const presetBtns = [];
(function () {
  const z = document.getElementById('tl-zoom');
  button(z, '−', () => zoomBy(2), {aria: 'Zoom out', cls: 'icon'});
  button(z, '+', () => zoomBy(0.5), {aria: 'Zoom in', cls: 'icon'});
  button(z, '◀', () => panBy(-0.4), {aria: 'Earlier', cls: 'icon'});
  button(z, '▶', () => panBy(0.4), {aria: 'Later', cls: 'icon'});
  presetBtns.push(button(z, 'Whole span', () => animateTo(...FULL), {view: FULL}));
  const d = document.getElementById('tl-weeks');
  const lab = document.createElement('span'); lab.className = 'tl-lab'; lab.textContent = 'Week:'; d.appendChild(lab);
  (D.meta.weeks || []).forEach(w => presetBtns.push(button(d, w.label, () => animateTo(w.s, w.e),
    {view: clampV(w.s, w.e), aria: `Show ${w.title}`})));
  const sp = document.getElementById('tl-spans');
  const lab2 = document.createElement('span'); lab2.className = 'tl-lab'; lab2.textContent = 'Go to:'; sp.appendChild(lab2);
  // the chapters of the thread, each the span of one or more of §2's turning points
  const H = t => HL.find(h => h.title.indexOf(t) >= 0);
  const chapter = (label, from, to) => { const a = H(from), b = to ? H(to) : a; return a && b ? [label, [a.a, b.b]] : null; };
  [chapter('Before the card', 'Before the card', 'First runs'),
   chapter('The Horace result', 'The question that starts it', 'Flips counted in RTL'),
   chapter('The price list', 'The energy manual', 'Dally’s 100 fJ'),
   chapter('Three cards at once', 'Everything re-run', 'Where the heat sits'),
   chapter('Building the camera', 'A thermal camera'),
   chapter('The flip series', 'The bit-flip ladder', 'Power first'),
   chapter('This week', 'One flipped bit, through', 'What is still missing')]
    .filter(Boolean).filter(([, v]) => v[0] < FULL[1] && v[1] > FULL[0] && v[1] > v[0])
    .forEach(([t, v]) => presetBtns.push(button(sp, t, () => animateTo(v[0] - 1800, v[1] + 1800), {view: clampV(v[0] - 1800, v[1] + 1800)})));
  const tgs = document.getElementById('tg-sub'), tgp = document.getElementById('tg-pages'), det = document.getElementById('tl-detail'), detLeg = document.getElementById('tl-detail-leg');
  tgs.addEventListener('click', () => {
    S.sub = !S.sub; tgs.setAttribute('aria-pressed', String(S.sub)); det.hidden = !S.sub; detLeg.hidden = !S.sub;
    if (S.sub) { if (!detail) { detail = CK.frame('tl-detail', {label: 'Every session, one thin lane each, grouped by machine', minW: 300, maxW: 1440, height: W => detailLayout(W).H, draw: drawDetail}); gestures(detail); } else detail.redraw(); }
  });
  tgp.addEventListener('click', () => { S.perPage = !S.perPage; tgp.setAttribute('aria-pressed', String(S.perPage)); legendArt(); main.redraw(); });
})();
function pressed() { presetBtns.forEach(b => b.setAttribute('aria-pressed', String(Math.abs(b._view[0] - S.v[0]) < 90 && Math.abs(b._view[1] - S.v[1]) < 90))); }
function readout() {
  const [a, b] = S.v;
  const nm = MSG.filter(m => m.t >= a && m.t <= b).length;
  const mb = overlap(BUSY.map(q => [q.s, q.e]), a, b) / 3600;
  const sb = (overlap(SUBIV.workflow, a, b) + overlap(SUBIV.tool, a, b)) / 3600;
  const ch = CU.reduce((s2, u) => s2 + overlap(u, a, b), 0) / 3600;
  let po = 0;
  for (let j = Math.max(0, Math.floor((a - C0) / 60)); j < Math.min(CW.length, Math.ceil((b - C0) / 60)); j++) po = Math.max(po, CW[j] + CT[j]);
  const ne = CIV.filter(q => q.e >= a && q.s <= b).length;
  const nd = DEP.filter(d => d.t >= a && d.t <= b).length, nc = COM.filter(c => c.t >= a && c.t <= b).length;
  setH('tl-readout', `Showing <b>${span(a, b)}</b> (${dur(b - a)}). In view: <b>${nm}</b> ask${nm === 1 ? '' : 's'} \u00b7 ` +
    `some session working <b>${hrs(mb)}</b> of it (<b>${num(sb, 1)} session-h</b>${po ? `, up to ${po} at once` : ''}) \u00b7 ` +
    `<b>${ne}</b> measurement${ne === 1 ? '' : 's'}, <b>${num(ch, 1)} card-h</b> \u00b7 ` +
    `<b>${nd}</b> publish${nd === 1 ? '' : 'es'} \u00b7 <b>${nc}</b> commit${nc === 1 ? '' : 's'}`);
}
/* legends: CK.legend's swatches, and drawn ones where a mark has no swatch of its kind (ticks, the dotted line, steps) */
const SW = {
  tall: '<rect x="7.5" y="0" width="3" height="10" style="fill:var(--ink-2)"/>',
  short: '<rect x="7.5" y="5" width="3" height="5" style="fill:var(--muted)"/>',
  dotted: '<line x1="1" x2="17" y1="5" y2="5" style="stroke:var(--c7);stroke-width:2;stroke-dasharray:1.5 3;stroke-linecap:round"/>',
  dev: c => `<rect x="3.5" y="0.5" width="11" height="9" rx="1" style="fill:${mixT(c, 30)};stroke:${c};stroke-width:1"/>`,
  step: n => `<rect x="3" y="${10 - 2.5 * n}" width="12" height="${2.5 * n}" style="fill:${INUSE_FILL[n]}"/>`,
  bar: '<rect x="7.5" y="3" width="3" height="7" rx="1" style="fill:var(--ink)"/>',
  barDot: '<rect x="7.5" y="5" width="3" height="5" rx="1" style="fill:var(--ink)"/><circle cx="9" cy="2" r="2" style="fill:var(--ink)"/>',
  down: `<rect x="3.5" y="0.5" width="11" height="9" style="fill:${mixT('var(--bad)', 30)};stroke:var(--bad);stroke-width:1"/>`,
};
function legend(host, items) {
  CK.legend(host, items.map(it => Object.assign({mark: 'box'}, it)));
  const h = document.getElementById(host);
  items.forEach((it, i) => { if (it.sw) h.children[i].firstChild.innerHTML = it.sw; });
}
const famLegend = () => CA.families.map((fm, i) => ({key: fm.key, label: fm.short || fm.label, mark: 'box', color: FAMCOL[i]}));
function legendCards() {
  const items = S.cardMode === 'card' ? CK.cardLegend(CA.ids) : famLegend();
  legend('leg-cards', items.concat(HOSTEV.length ? [{key: 'down', label: 'the host down: hung, or power-cycled', sw: SW.down}] : [])
    .concat([1, 2, 3, 4].map(n => ({key: 'u' + n, label: n === 1 ? 'cards in use: 1' : String(n), sw: SW.step(n)}))));
}
function legendArt() {
  legend('leg-art', (S.perPage ? [{key: 'n', label: 'first version of a write-up', mark: 'dot', color: 'var(--ink)'}, {key: 'u', label: 'a later version', mark: 'ring', color: 'var(--ink)'}]
    : [{key: 'd', label: 'versions published in one minute (the bar’s height: how many)', sw: SW.bar}, {key: 'n', label: 'a first version among them', sw: SW.barDot}])
    .concat([{key: 'c', label: 'commit to the lab repository', sw: SW.tall}]));
}
legend('leg-human', [
  {key: 'r', label: 'request', mark: 'dot', color: 'var(--ink)'}, {key: 'c', label: 'correction', mark: 'diamond', color: 'var(--ink)'},
  {key: 'a', label: 'approval or answer', mark: 'box', color: 'var(--ink)'}, {key: 'q', label: 'question', mark: 'ring', color: 'var(--ink)'},
  {key: 's', label: 'status check', mark: 'line', color: 'var(--ink)'},
  {key: 'act', label: 'estimated writing time', mark: 'box', color: mixT('var(--ink-2)', 55)},
  {key: 'ses', label: 'a sitting (asks under an hour apart)', mark: 'box', color: mixT('var(--ink)', 14)}]);
legend('leg-agents', [
  {key: 'ma', label: 'some session working on the thread', color: COL.main},
  {key: 'wf', label: 'Claude Code sessions busy at once', color: COL.wf}, {key: 'tl', label: 'other harnesses busy at once', color: COL.tool}]
  .concat(NB ? [{key: 'nb', label: 'one lane busy', color: 'var(--ref)'},
    {key: 'nbe', label: 'a write-up published from that lane', mark: 'diamond', color: 'var(--ink)'}] : []));
legend('tl-detail-leg', [{key: 'w', label: 'a Claude Code session working', color: COL.wf}, {key: 't', label: 'another harness working', color: COL.tool},
  {key: 'i', label: 'thin line: the session open, not working', mark: 'line', color: 'var(--ink-2)'}]);
legendCards(); legendArt();
CK.seg('cards-mode', {label: 'Colour the measurements by', options: [['family', 'experiment family'], ['card', 'card']], value: S.cardMode,
  onChange: v => { S.cardMode = v; legendCards(); main.redraw(); }});

(function () {
  document.getElementById('tg-pages').setAttribute('aria-pressed', String(S.perPage));
  main = CK.frame('tl', {label: 'Seven weeks on one time axis: the questions, the sessions, the experiments and the documents', minW: 300, maxW: 1440,
    height: W => layout(W).H, draw: drawMain});
  gestures(main);
  readout(); pressed();
  setH('tl-cap', `All times Pacific. The data ends at the snapshot, ${when(D.meta.snapshot_end)} (shaded after it). ` +
    `A session's busy time is an estimate, not a record: it runs from four minutes before each recorded act of work \u2014 an ask of mine, a commit, ` +
    `a publish, a card run \u2014 to twenty-six minutes after it, with gaps under 45 minutes bridged. The spine is the union of all of them, so two ` +
    `sessions working at once count once there; the count below the lanes is per minute. A measurement's interval is read from the data file the ` +
    `experiment committed, so it is exact; ${CA.undated.length} experiments in the register left no timestamps and are not drawn (listed in <a href="#method">\u00a75</a>). ` +
    `My own bars are an estimate of writing time only.`);
})();

/* ---------- highlights list ---------- */
(function () {
  const ol = document.getElementById('hl-list');
  HL.forEach((h, i) => {
    const li = document.createElement('li'), b = document.createElement('button');
    b.type = 'button';
    b.innerHTML = `<span class="hl-head"><span class="hl-n">${i + 1}</span><b>${esc(h.title)}</b><span class="hl-track">${esc(h.track)}</span></span>` +
      `<span class="hl-when">${span(h.a, h.b)}</span><span class="hl-cap">${esc(h.caption)}</span>`;
    b.addEventListener('click', () => { animateTo(...hlView(h)); document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'}); });
    li.appendChild(b);
    // the published pages this highlight produced or changed: links beside the card's button, not inside it
    if (h.links && h.links.length) {
      const d = document.createElement('div');
      d.className = 'hl-links';
      d.innerHTML = `<span class="hl-links-lab">${h.links.length > 1 ? 'Pages' : 'Page'}:</span> ` +
        h.links.map(([ti, u]) => `<a href="${esc(u)}">${esc(ti)}</a>`).join('<span class="hl-sep"> · </span>');
      li.appendChild(d);
    }
    ol.appendChild(li);
  });
})();

// under a message in §3: the start of its words and a button that opens the reader
function words(text, lost, k) {
  if (k == null) return '';
  if (!text) return lost ? `<div class="ask-words lost">its words are no longer on the machine; only the summary was kept</div>` : '';
  return `<div class="ask-words"><span class="ask-words-text">${rmFmt(text.length > 400 ? text.slice(0, 400) + ' …' : text)}</span>` +
    `<button type="button" class="ask-read" data-pk="${k}">read it whole</button></div>`;
}
/* ---------- what the owner asked: every message, the request first, the estimates small ---------- */
(function () {
  const host = document.getElementById('asked-list'); if (!host) return;
  const MARK = ['<circle cx="7" cy="7" r="4.2"/>', '<polygon points="7,2 12,7 7,12 2,7"/>', '<rect x="3.2" y="3.2" width="7.6" height="7.6"/>',
    '<circle cx="7" cy="7" r="3.8" fill="var(--page)" stroke="var(--ink)" stroke-width="2"/>', '<rect x="5.7" y="1" width="2.6" height="12"/>'];
  // grouped by ISO week, and by day inside it: 51 day headings would be unreadable
  const wks = [];
  MSG.forEach(m => {
    const d = dayOf(m.t), w = WEEK(d);
    if (!wks.length || wks[wks.length - 1][0] !== w) wks.push([w, []]);
    const days = wks[wks.length - 1][1];
    if (!days.length || days[days.length - 1][0] !== d) days.push([d, []]);
    days[days.length - 1][1].push(m);
  });
  host.innerHTML = wks.map(([w, days]) => {
    const nw = days.reduce((a, q) => a + q[1].length, 0);
    const d0 = days[0][0], d1 = days[days.length - 1][0];
    return `<section class="ask-week"><h3>Week ${w} <span class="ask-n">${+D.meta.day_iso[d0].slice(8)} ${MOL(d0)}` +
      `${d1 !== d0 ? ` \u2013 ${+D.meta.day_iso[d1].slice(8)} ${MOL(d1)}` : ''} \u00b7 ${nw} ask${nw > 1 ? 's' : ''}</span></h3></section>` +
      days.map(([d, ms]) => `<section class="ask-day" data-day="${d}"><h3>${DN[d]} ${MOL(d)} <span class="ask-n">${ms.length} ask${ms.length > 1 ? 's' : ''}</span></h3><ol class="ask-list">` +
      ms.map(m => `<li data-cat="${m.cat}"><button type="button" data-t="${m.t}"><svg class="ask-mark" width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" fill="var(--ink)">${MARK[m.cat] || MARK[0]}</svg>` +
        `<span class="ask-sum">${esc(m.sum)}</span><span class="ask-meta">${hm(m.t)} · ${esc(HU.cats[m.cat])}${m.rid ? ` · ${esc(m.rid)}` : ''}` +
        `${m.to && LANE_NAME[m.to] ? ` · to ${esc(LANE_NAME[m.to])}` : ''}${m.kind !== 'prompt' ? ` · ${esc(KINDLAB[m.kind] || m.kind)}` : ''}` +
        `</span></button>${words(m.text, false, pidx('the main session', m.t, m.sum))}</li>`).join('') + '</ol></section>').join('');
  }).join('');
  host.addEventListener('click', e => {
    const b = e.target.closest('button[data-t]'); if (!b) return;
    const t = +b.dataset.t; animateTo(t - 3 * 3600, t + 3 * 3600);
    document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'});
  });
  // the owner's messages to the neighbor session(s): after the list, apart from its totals and its filter
  const hnb = document.getElementById('asked-nb');
  if (hnb && NB) hnb.innerHTML = NB.sessions.filter(nb => nb.msgs && nb.msgs.length).map(nb => {
    const ds = [...new Set(nb.msgs.map(m => dayOf(m[0])))].map(d => `${+String(DN[d]).split(' ')[1]} ${MOL(d)}`);
    return `<section class="ask-day ask-nb"><h3>To ${esc(nb.name)} <span class="ask-n">${nb.msgs.length} message${nb.msgs.length === 1 ? '' : 's'}, ` +
    `${ds.length > 2 ? ds[0] + ' to ' + ds[ds.length - 1] : ds.join(' and ')}</span></h3><p class="ask-nb-what">${esc(nb.title)}</p><ol class="ask-list">` +
    nb.msgs.map(m => `<li><button type="button" data-t="${m[0]}"><svg class="ask-mark" width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" fill="var(--ink-2)">${MARK[m[1]] || MARK[0]}</svg>` +
      `<span class="ask-sum">${esc(m[3])}</span><span class="ask-meta">${DN[dayOf(m[0])]} ${MO(dayOf(m[0]))} ${hm(m[0])} · ${esc(HU.cats[m[1]])}</span></button>` +
      `${words(m[4], m[6], pidx(nb.name, m[0], m[3]))}</li>`).join('') + '</ol></section>';
  }).join('');
  if (hnb) hnb.addEventListener('click', e => {
    const b = e.target.closest('button[data-t]'); if (!b) return;
    const t = +b.dataset.t; animateTo(t - 3 * 3600, t + 3 * 3600);
    document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'});
  });
  const PL = {request: 'requests', correction: 'corrections', 'approval/answer': 'approvals or answers', question: 'questions', status: 'status checks'};
  const counts = HU.totals.by_category;
  const opts = [['all', `all ${HU.totals.n}`]].concat(HU.cats.map((c, i) => [String(i), `${PL[c] || c} (${counts[c] || 0})`]).filter((o, i) => counts[HU.cats[i]]));
  CK.seg('asked-filter', {label: 'Show', options: opts, value: 'all', onChange: v => {
    host.querySelectorAll('li[data-cat]').forEach(li => { li.hidden = v !== 'all' && li.dataset.cat !== v; });
    host.querySelectorAll('section.ask-day').forEach(sec => { sec.hidden = !sec.querySelector('li[data-cat]:not([hidden])'); });
  }});
})();

/* ---------- where the time went ---------- */
(function () {
  const W0 = D.who, cch = subHours('workflow'), oth = subHours('tool');
  const rows = [
    {label: 'Me, writing', est: true, unit: 'h', segs: [{v: W0.human_active_h, c: 'var(--ink-2)', t: `estimated writing time of ${HU.totals.n} asks: ${hrs(W0.human_active_h, 2)}`}]},
    {label: 'Me, in a sitting', est: true, unit: 'h', segs: [{v: W0.human_engagement_h, c: mixT('var(--ink)', 30), t: `${HU.totals.sessions} sittings (asks under an hour apart), first to last: ${hrs(W0.human_engagement_h, 2)}`}]},
    {label: 'Some session working', unit: 'h', segs: [{v: W0.main_busy_h, c: COL.main, t: `the union of every session's busy time: ${hrs(W0.main_busy_h, 2)} of wall clock`}]},
    {label: 'Sessions, added up', unit: 'session-h', segs: [{v: cch, c: COL.wf, t: `Claude Code: ${num(cch, 1)} session-hours`},
      {v: oth, c: COL.tool, t: `the other harnesses: ${num(oth, 1)} session-hours`}]},
    {label: 'Cards, held', unit: 'card-h', segs: CA.per_card.map(p => ({v: p.held_h, c: CK.card(p.id).color, t: `${CK.card(p.id).label}: ${num(p.held_h, 2)} card-hours held (${num(p.busy_h, 2)} busy)`}))},
  ];
  CK.legend('who-leg', [{key: 'h', label: 'me', mark: 'box', color: 'var(--ink-2)'}, {key: 'm', label: 'some session working', mark: 'box', color: COL.main},
    {key: 'w', label: 'Claude Code', mark: 'box', color: COL.wf}, {key: 't', label: 'other harnesses', mark: 'box', color: COL.tool}]
    .concat(CK.cardLegend(CA.ids)));
  const max = Math.max(...rows.map(r => r.segs.reduce((a, q) => a + q.v, 0)));
  CK.frame('who', {label: 'Where the time went: me, the sessions and the cards, in hours', minW: 300, maxW: 1100,
    height: W => (W < 600 ? rows.length * 50 + 56 : rows.length * 38 + 44), draw(f) {
      const nar = f.narrow, L = nar ? 8 : 214, R = nar ? 80 : 100, T = 10, rh = nar ? 50 : 38, bh = nar ? 16 : 20;
      const x = CK.lin(0, Math.ceil(max / 20) * 20, L, f.W - R), nodes = [], labs = [];
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      for (const t of x.ticks(nar ? 4 : 6)) { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: T + rows.length * rh, class: 'grid-line'}, g); labs.push(CK.txt(g, x(t), T + rows.length * rh + 16, num(t, 0), 'tick', 'middle')); }
      labs.push(CK.txt(g, nar ? L : (L + f.W - R) / 2, f.H - 4, 'hours (session-hours, card-hours)', 'lab', nar ? 'start' : 'middle'));
      rows.forEach((r, i) => {
        const y = T + i * rh + (nar ? 20 : (rh - bh) / 2);
        CK.txt(f.svg, nar ? L : L - 10, nar ? y - 6 : y + bh / 2 + 4, r.label + (r.est ? ' (estimate)' : ''), 'lab', nar ? 'start' : 'end');
        let acc = 0;
        r.segs.forEach(q => {
          if (q.v <= 0) return;
          const nd = rect(f.svg, x(acc), y, Math.max(1, x(acc + q.v) - x(acc)), bh, q.c, {rx: 2});
          sty(nd, {stroke: 'var(--page)', strokeWidth: '1.5px'});
          CK.tip(f, nd, `<b>${esc(r.label)}</b><br>${esc(q.t)}`); nodes.push(nd); acc += q.v;
        });
        labs.push(CK.txt(f.svg, x(acc) + 6, y + bh / 2 + 4, `${num(acc, 1)} ${r.unit}`, 'lab-strong'));
      });
      CK.inside(f, labs); CK.keynav(f, nodes);
    }});
  setH('who-cap', `My own two rows are estimates: there is no record of how long an ask took to think of or to write. ` +
    `“Some session working” is the union of every session's busy time, so a night with four sessions running counts once; ` +
    `“sessions, added up” counts each separately, which is why it is larger. Card-hours count a gap under two minutes as held, ` +
    `because a queue keeps the card between passes. Hover, tap or tab to a bar for its exact value.`);
})();

/* ---------- card-hours per card, by experiment family ---------- */
(function () {
  legend('cardh-leg', famLegend());
  const P = CA.per_card, max = Math.max(...P.map(p => p.family_h.reduce((a, b) => a + b, 0)));
  CK.frame('cardh', {label: 'Card-hours per card, by experiment family', minW: 300, maxW: 640, height: W => P.length * 40 + 56, draw(f) {
    const nar = f.narrow, L = nar ? 50 : 140, R = nar ? 104 : 116, T = 8, rh = 40, bh = 20;
    const x = CK.lin(0, Math.ceil(max / 5) * 5, L, f.W - R), g = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [], nodes = [];
    for (const t of x.ticks(nar ? 4 : 6)) { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: T + P.length * rh, class: 'grid-line'}, g); labs.push(CK.txt(g, x(t), T + P.length * rh + 16, num(t, 0), 'tick', 'middle')); }
    labs.push(CK.txt(g, (L + f.W - R) / 2, f.H - 4, 'card-hours busy; the label gives the hours held', 'lab', 'middle'));
    P.forEach((p, i) => {
      const y = T + i * rh + (rh - bh) / 2, c = CK.card(p.id);
      CK.cardMark(f.svg, p.id, 8, y + bh / 2, 4);
      CK.txt(f.svg, 18, y + bh / 2 + 4, nar ? c.short : c.label, 'lab');
      let acc = 0;
      p.family_h.forEach((v, k) => {
        if (v <= 0) return;
        const n = rect(f.svg, x(acc), y, Math.max(1, x(acc + v) - x(acc)), bh, k === DEVF ? famFill(k, c.color) : FAMCOL[k]);
        sty(n, k === DEVF ? {stroke: c.color, strokeWidth: '1px'} : {stroke: 'var(--page)', strokeWidth: '1.5px'});
        CK.tip(f, n, `<b>${c.label}</b><br>${esc(CA.families[k].label)}: ${num(v, 2)} card-hours busy`); nodes.push(n); acc += v;
      });
      labs.push(CK.txt(f.svg, x(acc) + 6, y + bh / 2 + 4, `held ${num(p.held_h, 1)} card-h`, 'lab-strong'));
    });
    CK.inside(f, labs); CK.keynav(f, nodes);
  }});
  const tot = CA.totals;
  setH('cardh-cap', `${num(tot.held_h, 1)} card-hours held in all, ${num(tot.busy_h, 1)} busy, over ${num(tot.intervals, 0)} measurements. Held counts a card’s gaps shorter than 2 minutes as held, because a queue keeps the card between passes; busy is the exact union of the intervals. ` +
    `The families are shades of one grey, a step per family in time order. Card 0 of the first host ran only smoke tests: an amendment kept it out of the September campaign because it overheats under load.`);
})();

/* ---------- how the asks were counted ---------- */
(function () {
  const t = HU.totals, bc = t.by_category, bk = t.by_kind;
  setH('human-text', `${t.n} asks (${num(t.chars, 0)} characters): ${bc.request} requests, ${bc.question} questions, ` +
    `${bc.correction} corrections, ${bc.status} status checks and ${bc['approval/answer']} approvals. ` +
    `${bk.prompt} were typed at a prompt, ${bk.midturn} arrived while an agent was already working, ${bk.voice} were dictated as voice notes ` +
    `and ${bk.discord} was posted in the lab's channel. The time each took is recorded nowhere, so it is <b>estimated</b> from its length alone: ` +
    `<b>${hrs(t.active_h, 2)}</b> in all. They fall into <b>${t.sessions}</b> sittings spanning <b>${hrs(t.engagement_h, 2)}</b>.`);
  document.getElementById('human-rules').innerHTML = [
    ['Writing', 'the length at 200 characters a minute, at least 10 s. Reading time is not estimated on this page: the replies these asks answered are not in the data.'],
    ['A sitting', 'a run of asks less than an hour apart, from the estimated start of the first to the last.'],
    ['The summary', 'written for this page, at most twelve words, in the third person, and never a quotation.'],
    ['The words', 'as the session log recorded them, dictation and all. What this public page withholds is replaced by a marked note.'],
    ['What is not here', 'asks of those weeks that were about something else, and anything inside the private archive.']]
    .map(([k, v]) => `<li><b>${k}:</b> ${v}</li>`).join('');
})();

/* ---------- day by day: one thin row per day, and the week table ---------- */
(function () {
  CK.legend('days-leg', [{key: 'h', label: 'my asks', mark: 'dot', color: 'var(--ink)'},
    {key: 'm', label: 'some session working', mark: 'box', color: COL.main},
    {key: 'w', label: 'Claude Code sessions at once', mark: 'box', color: COL.wf},
    {key: 't', label: 'other harnesses at once', mark: 'box', color: COL.tool},
    {key: 'c', label: 'cards in use (height: how many)', mark: 'box', color: INUSE_FILL[3]}]);
  const PDY = D.perday, PEAK = niceMax(Math.max(2, PKOK));
  setH('d-scale', PEAK);
  const rh = 28;
  CK.frame('days', {label: 'Seven weeks by day: one row per day, midnight to midnight', minW: 300, maxW: 1100,
    height: W => PDY.length * rh + 34, draw(f) {
    const nar = f.narrow, L = nar ? 52 : 74, R = nar ? 8 : 120, T = 24;
    const x = CK.lin(0, DAY, L, f.W - R), g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), nodes = [], labs = [];
    for (let hh = 0; hh <= 24; hh += nar ? 6 : 3) { CK.el('line', {x1: x(hh * 3600), x2: x(hh * 3600), y1: T - 4, y2: T + PDY.length * rh, class: 'grid-line'}, g0); labs.push(CK.txt(g0, x(hh * 3600), T - 9, pad2(hh % 24 === 0 && hh ? 24 : hh) + ':00', 'tick', 'middle')); }
    PDY.forEach((d, i2) => {
      const y = T + i2 * rh, a = d.day * DAY, b = a + DAY, X = t => x(Math.max(a, Math.min(b, t)) - a), g = CK.el('g', {}, f.svg);
      rect(g, 0, y, f.W, rh - 2, (WEEK(d.day) % 2) ? mixT('var(--ink)', 3) : 'transparent');
      CK.txt(g, 4, y + 13, d.label, 'tick');
      MSG.filter(m => m.t >= a && m.t < b).forEach(m => sty(CK.el('circle', {cx: X(m.t), cy: y + 5, r: 2.2}, g), {fill: 'var(--ink)'}));
      BUSY.filter(q => q.e >= a && q.s <= b).forEach(q => rect(g, X(q.s), y + 9, Math.max(1, X(q.e) - X(q.s)), 4, COL.main));
      // sessions at once, 10-minute maxima, on their own baseline
      const sy = y + 20, sh = 6, j0 = Math.max(0, Math.floor((a - C0) / 60)), j1 = Math.min(CW.length, Math.floor((b - C0) / 60));
      const hh2 = v => Math.min(v, PEAK) / PEAK * sh;
      for (let k = j0; k < j1; k += 10) {
        let bw = 0, bt = 0;
        for (let q = k; q < Math.min(k + 10, j1); q++) { if (OW[q] + OT[q] > bw + bt) { bw = OW[q]; bt = OT[q]; } }
        if (!(bw + bt)) continue;
        const xx = X(C0 + k * 60), ww = Math.max(0.8, X(C0 + (k + 10) * 60) - xx);
        if (bw) rect(g, xx, sy - hh2(bw), ww, hh2(bw), COL.wf);
        if (bt) rect(g, xx, sy - hh2(bw + bt), ww, hh2(bw + bt) - hh2(bw), COL.tool);
      }
      let t = INU.start;
      for (const [cnt0, cnt] of INU.rle) { const s2 = t, e2 = t + cnt * 60; t = e2; if (!cnt0 || e2 < a || s2 > b) continue; rect(g, X(s2), y + 26 - cnt0 / 4 * 6, Math.max(0.8, X(e2) - X(s2)), cnt0 / 4 * 6, INUSE_FILL[cnt0]); }
      if (!nar) CK.txt(g, f.W - R + 10, y + 14, `${d.human_n} ask${d.human_n === 1 ? '' : 's'} · ${num(d.card_h, 1)} card-h`, 'tick');
      const hit = CK.el('rect', {x: 0, y, width: f.W, height: rh - 2, class: 'ck-hit'}, g);
      hit.style.cursor = 'pointer';
      CK.tip(f, hit, `<b>${d.label} ${MOL(d.day)}</b> · week ${d.week}<br>${d.human_n} ask${d.human_n === 1 ? '' : 's'}` +
        `<br>some session working ${hrs(d.main_busy_h)}; ${num(d.sub_agent_h, 1)} session-hours, up to ${d.peak_sub_ok} at once` +
        `<br>cards ${num(d.card_h, 1)} card-h · ${d.deploys} published · ${d.commits} commits<br><i>Click or press Enter to open this day in the timeline.</i>`, {role: 'button'});
      const go = () => { animateTo(...dayView(d.day)); document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'}); };
      hit.addEventListener('click', go); hit._go = go;
      nodes.push(hit);
    });
    CK.inside(f, labs); CK.keynav(f, nodes, {onEnter: n2 => n2._go()});
  }});
  // the week table
  const PW = D.perweek, tb = document.getElementById('week-table'), c = v => `<td class="num">${v}</td>`;
  const sum = k => PW.reduce((a, d) => a + d[k], 0);
  tb.innerHTML = '<thead><tr><th>Week</th><th>Days</th><th class="num">Asks</th><th class="num">Writing, min (est.)</th>' +
    '<th class="num">Some session working, h</th><th class="num">Sessions, session-h</th><th class="num">Peak at once</th>' +
    '<th class="num">Card-h held</th><th class="num">Versions published</th><th class="num">Commits</th></tr></thead><tbody>' +
    PW.map(d => `<tr><td>${d.label}</td><td>${esc(d.title.replace(/^week \d+, /, ''))}</td>${c(d.human_n)}${c(num(d.human_active_min, 0))}` +
      `${c(num(d.main_busy_h, 1))}${c(num(d.sub_agent_h, 1))}${c(d.peak_sub_ok)}${c(num(d.card_h, 1))}${c(d.deploys)}${c(d.commits)}</tr>`).join('') +
    `</tbody><tfoot><tr class="total"><td>All</td><td>${PW.length} weeks</td>${c(sum('human_n'))}${c(num(sum('human_active_min'), 0))}` +
    `${c(num(sum('main_busy_h'), 1))}${c(num(sum('sub_agent_h'), 1))}${c(Math.max(...PW.map(d => d.peak_sub_ok)))}${c(num(sum('card_h'), 1))}` +
    `${c(sum('deploys'))}${c(sum('commits'))}</tr></tfoot>`;
  CK.sortTable(tb);
})();

/* ---------- how it was put together ---------- */
(function () {
  const at = AG.totals, ht = HU.totals, bk = ht.by_kind, ct = CA.totals, art = AR.totals;
  const items = [
    `<b>What this page is.</b> One thread of work, from a blog post about matrix multiplies to femtojoules per flipped bit, ` +
    `laid on one time axis so you can see what was asked, who was working, which cards were held and what came out. ` +
    `It is assembled, not mined: every row comes from a ledger that is committed in the lab repository or from the project's own hub, ` +
    `and the six inputs are committed beside the page. Nothing here was read out of a session's private transcript except my own asks.`,

    `<b>The questions.</b> ${ht.n} asks of mine on this thread between ${+D.meta.day_iso[dayOf(FULL[0])].slice(8)} ${MOL(dayOf(FULL[0]))} and the snapshot: ` +
    `${bk.prompt} typed at a prompt, ${bk.midturn} sent while an agent was already working, ${bk.voice} dictated as voice notes, ${bk.discord} posted in the lab's channel. ` +
    `Each has a summary of at most twelve words written for this page and, where the log kept them, <b>its own words</b>: their start in the mark's details and in <a href="#asked">§3</a>, ` +
    `all of them in the reader that a click, a second tap or Enter opens. Asks of those same weeks about something else are left out, and so is everything sent to the private archive. ` +
    `<b>Estimated writing time</b> is the message's length at 200 characters a minute, at least 10 s; reading time is not estimated here, because the replies are not in the data.`,

    `<b>The sessions.</b> ${at.agents} agent sessions across ${AG.groups.length} machines and ${at.by_kind['claude-code']} + ${at.by_kind.antigravity + at.by_kind.codex} harnesses ` +
    `(Claude Code, and Antigravity). No harness records when a session was thinking, so busy time is <b>estimated</b>: four minutes before each recorded act of work — ` +
    `an ask of mine, a commit, a publish, a card run — to twenty-six minutes after it, with gaps under 45 minutes bridged, clipped to the session's own span. ` +
    `The spine under SESSIONS is the union of all of them; the ten named lanes group the sessions into strands, and the count below is per minute. ` +
    `Sessions inside the private archive appear only as a lane with dates and spans: no title, no content, nothing of what they read.`,

    `<b>The experiments.</b> ${num(ct.intervals, 0)} intervals in which an ET-SoC-1 card was held, ${num(ct.held_h, 1)} card-hours in all. ` +
    `Each interval is read from the data file the experiment itself committed — its start, its end, the die temperature at the start and whether it returned data — ` +
    `so these are exact, not estimates. Where an experiment pre-dates that convention, the time comes from the range stated in the experiment register. ` +
    `${ct.intervals ? '' : ''}${CA.undated.length} registered experiments left no times at all and are not drawn: ` +
    CA.undated.map(u => `<b>${esc(u.E)}</b> (${esc(u.what)})`).join('; ') + `. ` +
    `<b>Held</b> card-hours count a gap under two minutes as held, because a queue keeps the card between passes; <b>busy</b> is the exact union. ` +
    `The families are a hand-written grouping of the register's experiments, in time order.`,

    `<b>The documents.</b> ${art.pages} write-ups, ${art.public} of them public and linked from their lane; the ${art.pages - art.public} that are not public ` +
    `appear by title only, because they name people or carry material under an agreement. A dot is a first version and a ring a later one, ${art.deploys} in all. ` +
    `The tick row is every commit the lab repository took over these seven weeks, ${num(art.commits, 0)} of them.`,

    `<b>What is not here.</b> No machine of mine is named by its address and no link points at one; no session link; no credentials or access paths. ` +
    `The private design archive appears only as dates and spans. The only people named are the published authors whose work these reports cite — ` +
    `Horace He, whose blog post started this; Bill Dally, whose rule of thumb everything is measured against; and, inside my own words, ` +
    `Mark Horowitz and Jeff Dean, whose reference numbers I asked for by name. Everyone else appears by role. ` +
    `The build refuses to write the page's data if any of that survives its scan.`,
  ];
  document.getElementById('method-list').innerHTML = items.map(x => `<li>${x}</li>`).join('');
})();

/* ---------- the prompt reader's buttons and keys ---------- */
(function () {
  const d = document.getElementById('pv'); if (!d) return;
  const on = (id, fn) => { const b = document.getElementById(id); if (b) b.addEventListener('click', fn); };
  const close = () => { if (d.close) d.close(); else d.removeAttribute('open'); };
  on('pv-close', close);
  on('pv-prev', () => openPrompt(Math.max(0, PV.k - 1)));
  on('pv-next', () => openPrompt(Math.min(PROMPTS.length - 1, PV.k + 1)));
  on('pv-show', () => {
    const t = PROMPTS[PV.k].t; close(); animateTo(t - 3 * 3600, t + 3 * 3600);
    document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'});
  });
  // a click on the backdrop closes it, if it also began there: the click that a phone sends after the tap that opened the
  // reader lands on the backdrop too, and must not close it
  let downOnBackdrop = false;
  d.addEventListener('pointerdown', ev => { downOnBackdrop = ev.target === d; });
  d.addEventListener('click', ev => { if (ev.target === d && downOnBackdrop) close(); downOnBackdrop = false; });
  d.addEventListener('keydown', ev => {
    if (ev.key === 'ArrowLeft' && PV.k > 0) { ev.preventDefault(); openPrompt(PV.k - 1); }
    else if (ev.key === 'ArrowRight' && PV.k < PROMPTS.length - 1) { ev.preventDefault(); openPrompt(PV.k + 1); }
  });
  // §3's lists: a message's "words" button opens it here too
  document.addEventListener('click', ev => {
    const b = ev.target.closest('button[data-pk]'); if (!b) return;
    ev.stopPropagation(); openPrompt(+b.dataset.pk);
  });
})();
