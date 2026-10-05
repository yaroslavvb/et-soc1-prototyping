/* The session timeline. D is timeline.json (tools/timeline/build_timeline_data.py); every number on the page is
   computed from it. Times are seconds since Sat 19 Sep 2026 00:00 PDT (UTC-7; no DST change that week), so a day is
   86 400 s and clock time is t mod 86 400.
   The timeline is one CK frame holding the four tracks on one x scale; the subagent detail is a second frame on the
   same scale. The view (S.v) is shared: buttons, swipes, drags, pinches, the wheel and the axis's keys change it, and
   both frames redraw on the next animation frame, drawing only what is in view. While a gesture, its momentum or a
   zoom animation runs, a frame is drawn fast: each series as one path, with no tooltips or keyboard stops; the full
   drawing, a node per mark, follows when it ends (see gestures()). Charts use the shared toolkit CK
   (docs/reports/sources/chartkit.js): tooltips by pointer, touch and keyboard, one tab stop per group of marks,
   template colour tokens only. */
const DAY = 86400, DN = D.meta.days, FULL = D.meta.full;
const HU = D.human, MA = D.main, AG = D.agents, CA = D.cards, AR = D.artifacts, TO = D.tokens, HL = D.highlights;
const NB = D.neighbors && D.neighbors.sessions && D.neighbors.sessions.length ? D.neighbors : null;   // other sessions' lanes
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
// the month of day index d (19 September is day 0; the snapshot of 1 October adds day 12)
const MO = d => (+String(DN[d] || '').split(' ')[1] < 19 ? 'Oct' : 'Sep'), MOL = d => (MO(d) === 'Oct' ? 'October' : 'September');
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
const DEVF = CA.dev;
const NFAM = CA.families.length - 1;   // the families drawn in grey (all but the development runs), 22% to 94% ink in time order
const FAMCOL = CA.families.map((f, i) => (i === DEVF ? 'transparent' : `color-mix(in srgb, var(--ink) ${Math.round(22 + 72 * (i < DEVF ? i : i - 1) / Math.max(1, NFAM - 1))}%, var(--surface))`));
const INUSE_FILL = [0, 28, 42, 60, 85].map(p => mixT('var(--ink)', p));   // cards in use, 0 to 4 (the height carries the count)
const famFill = (f, cardColor) => (f === DEVF ? mixT(cardColor || 'var(--ink-2)', 30) : FAMCOL[f]);
const KINDLAB = {prompt: 'sent at the prompt', midturn: 'sent while the agent was working', 'slash-command': 'a slash command',
  'question-answer': 'an answer to the agent’s question', interrupt: 'an interrupt (Esc)', talk: 'written on a published page (its Talk tab)'};
const TRIGLAB = {human: 'a message from the owner', 'task-notification': 'a background agent or workflow finishing',
  'agent-message': 'a message from another agent', 'compact-continuation': 'a continuation after compaction',
  interrupt: 'an interrupt', continuation: 'a continuation', 'watch-loop': 'the end of a loop that watched its own workflows'};
const CATMARK = ['dot', 'diamond', 'box', 'ring', 'line'];
const MSG = HU.msgs.map((m, i) => ({i, t: m[0], act: m[1], actp: m[2], cat: m[3], kind: HU.kinds[m[4]], sum: m[5], rid: m[6], chars: m[7], read: m[8], type: m[9], paste: m[10],
  text: m[11], rm: m[12] || [], img: m[13] || 0}));
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
// subagents busy per minute: all (CW + CT), and split into workflow and Agent-tool agents that did not fail (OW, OT)
// and those that failed or ended on an error (CF); OW + OT + CF = CW + CT
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
AGR.forEach(a => a.iv.forEach(q => SUBIV[a.kind === 'workflow' ? 'workflow' : 'tool'].push(q)));
const subHours = k => SUBIV[k].reduce((s, q) => s + q[1] - q[0], 0) / 3600;
const wfName = a => (a.wf >= 0 ? WFS[a.wf].name : a.kind === 'fork' ? 'a fork of an Agent-tool agent' : 'started with the Agent tool');
const TOT_SESSION = D.meta.snapshot_end - D.meta.session_start;

/* ---------- lede and KPIs ---------- */
(function () {
  const W = D.who, at = AG.totals, ct = CA.totals;
  const WD = {Sat: 'Saturday', Sun: 'Sunday', Mon: 'Monday', Tue: 'Tuesday', Wed: 'Wednesday', Thu: 'Thursday', Fri: 'Friday'};
  const ed = DN[dayOf(D.meta.snapshot_end)].split(' '), oct = +ed[1] < 19;
  setH('l-end', `${hm(D.meta.snapshot_end)} on ${WD[ed[0]]} ${ed[1]} ${oct ? 'October' : 'September'}`);
  setH('l-range', oct ? `19 September – ${ed[1]} October 2026` : `19–${ed[1]} September 2026`);
  setH('l-n', HU.totals.n); setH('l-agents', num(at.agents, 0)); setH('l-wf', at.workflow_runs);
  setH('l-dep', AR.totals.deploys); setH('l-com', AR.commits.filter(c => c[0] >= D.meta.session_start).length);
  setH('l-wall', `${num(TOT_SESSION / 3600, 0)} hours (${num(TOT_SESSION / DAY, 1)} days)`);
  // the main session's own span: its first message to its last work (it stopped on 2 October; the snapshot is later)
  const mainEnd = Math.max(MSG[MSG.length - 1].t, ...BUSY.map(b => b.e));
  const nd = Math.round((mainEnd - D.meta.session_start) / DAY), words = ['', 'one day', 'two days', 'three days', 'four days', 'five days', 'six days', 'a week',
    'eight days', 'nine days', 'ten days', 'eleven days', 'twelve days', 'thirteen days', 'two weeks'];
  setH('l-days', words[nd] || `${nd} days`);
  if (NB) document.querySelector('p.lede').insertAdjacentHTML('beforeend', ` The owner also ran <b>other sessions</b> on the lab’s machine, on two Claude accounts: ` +
    `a maintenance session, which ran the link test that hung aifoundry1 on 30 September and made the dashboard live on 2 October; an audit session and an ` +
    `Antigravity session on 4 October; and the session that checkpointed the machine’s setup and refreshed this page on 5 October. Each has a lane of its own, ` +
    `and a red band marks each host or card that was down.`);
  const bc = HU.totals.by_category;
  setH('k-human', `${HU.totals.n} messages`);
  setH('k-human-sub', `${bc.request} requests, ${bc.correction} corrections, ${bc['approval/answer']} approvals or answers, ${bc.question} questions, ${bc.status} status checks ` +
    `(<a href="#asked">the list</a>)<span class="kpi-est">about ${hrs(W.human_active_h)} of reading and typing, an estimate</span>`);
  setH('k-agents', `${num(BUSY_H + W.sub_agent_h, 0)} agent-hours`);
  setH('k-agents-sub', `the main agent ${hrs(BUSY_H)} busy (${hrs(W.main_strict_h)} of it active, events under 3 min apart), ${num(at.agents, 0)} subagents ${num(W.sub_agent_h, 1)} agent-h; ` +
    `up to ${PKOK} at once (${PK} in the minute the usage limit hit, most of them failing)`);
  const m3 = (ct.minutes_by_count['3'] || 0) / 60;
  setH('k-cards', `${num(W.card_held_h, 1)} card-hours`);
  setH('k-cards-sub', CA.per_card.map(p => `${CK.card(p.id).label} ${num(p.held_h, 1)}`).join(' · ') + ` h held; up to 4 cards at once, 3 for ${hrs(m3)}`);
  const T = TO.totals.all;
  setH('k-tok', `${num(T.total / 1e9, 2)} billion`);
  setH('k-tok-sub', `${CK.fmt.pct(T.cache_read / T.total, 1)} cache reads · ${tok(T.output)} output · subagents ${CK.fmt.pct(TO.totals.subagents.total / T.total)}`);
})();

/* ---------- the view ---------- */
const S = {v: FULL.slice(), sub: false, perPage: false, cardMode: 'card', focus: null, fast: false, drawFast: false};
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
  if (NB) add('humanNb', 18);   // the owner's messages to the neighbor session(s)
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
   the reusable session-timeline component (spacesheep.dev/@yaroslavvb/scrollable-session-timeline, LESSONS.md §5).
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
const msgTip = m => `<b style="font-size:1.06em">${esc(m.sum)}</b><br>${when(m.t)} · ${HU.cats[m.cat]}${m.rid ? ` · request ${m.rid} in the knowledge base` : ''}` +
  promptTip(m.text, false, m.img) +
  `<span style="display:block;font-size:.8em;color:var(--muted)">estimated ${dur(m.act)} of reading and typing (reading ${dur(m.read)}, typing ${dur(m.type)}` +
  `${m.paste ? `; likely pasted, so ${dur(m.actp)} with typing capped at 3 min` : ''}) · ${num(m.chars, 0)} characters, ${KINDLAB[m.kind] || m.kind}</span>`;
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
const busyTip = b => `<b>Main agent busy</b> ${span(b.s, b.e)} (${dur(b.e - b.s)})<br>active (events under 3 min apart) ${dur(b.act)}` +
  `${b.tw > 30 ? `; waiting on a tool ${dur(b.tw)}${b.twl > 30 ? ` (${b.twl >= b.tw - 30 ? 'all' : dur(b.twl)} on card runs or the lab machines)` : ''}` : ''}` +
  `${b.ow > 30 ? `; other waits ${dur(b.ow)}` : ''}<br>started by ${TRIGLAB[b.trig] || b.trig}` +
  `<br>${num(b.msgs, 0)} messages, ${num(b.tools, 0)} tool calls, ${tok(b.tok)} tokens`;
const watchTip = (a, b) => `<b>Watching its workflows</b> ${span(a, b)} (${dur(b - a)})<br>the main agent’s only calls in flight were loops ` +
  `that watched its own workflows or subagents; this time counts as idle, because the subagents’ hours cover it`;
function cardTip(q) {
  const c = CK.card(CA.ids[q.c]);
  return `<b>${c.label}</b> · ${esc(q.label)}${q.name && q.name !== q.label ? ` — ${esc(q.name)}` : ''}<br>${span(q.s, q.e)} (${dur(q.e - q.s)})` +
    `<br>${esc(CA.families[q.f].label)}<br>${q.f === DEVF ? esc(q.st) + ' (an upper bound: a call’s time includes any build in the same command)' : 'status: ' + esc(q.st)}` +
    `${q.die != null ? ` · die ${q.die} °C at the start` : ''}`;
}
const pageTitle = p => (p.private ? esc(p.title) : `${esc(p.title)} <span class="small">(${esc(p.short)})</span>`);
const depTip = d => `<b>${pageTitle(PAGES[d.p])}</b><br>${when(d.t)} · ${d.nw ? 'first publish (a new space)' : 'an update'}${d.ok ? '' : ' · not confirmed by the tool’s output'}`;
function listTip(head, items, fmt, max) {
  const shown = items.slice(0, max).map(fmt).join('<br>');
  return `${head}<br>${shown}${items.length > max ? `<br>and ${items.length - max} more` : ''}`;
}
const comTip = g => listTip(`<b>${g.items.length > 1 ? g.items.length + ' commits' : 'Commit'}</b> ${when(g.t)} · ${AR.sessions[g.items[0].ses]}`,
  g.items, c => `<code>${c.sha}</code> ${esc(c.sub)}`, 6);
function limitNear(t) { const l = MA.limits.find(([u]) => Math.abs(u - t) <= 120); return l ? `<br><b>⚠ usage limit reached</b> (${l[1]}) at ${hm(l[0])}` : ''; }
function runningAt(t) { return WFS.filter(w => w.s <= t && t <= w.e).map(w => w.name); }
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
  head('hH', 'HUMAN', `${HU.totals.n} messages · a mark per message; what was asked shows under it when zoomed in to two days or less, and in its details · faint bar: estimated reading and typing time · shaded: engagement sessions`);
  head('hA', 'AGENTS', 'the main agent: solid, active (events under 3 min apart); tint, waiting inside a turn; dotted, watching its workflows (idle) · below: subagents busy at once');
  head('hC', 'CARDS', 'one lane per card, each interval a measurement; outlined: development runs, from the transcripts · red: the host down · below: cards in use, 0 to 4');
  head('hR', 'ARTIFACTS', (S.perPage ? 'deploys: ● first publish, ○ update' : 'deploys: a bar per minute, its height the number of pages; a dot marks a first publish') +
    ' · commits: tall tick, this session; short tick, another session');
  // the session's start and the snapshot's end
  [[D.meta.session_start, 'first message'], [D.meta.snapshot_end, 'end of the data']].forEach(([t]) => {
    if (!vis(t, t)) return;
    lineEl(plot, x(t), rows.human.y, x(t), y1, {stroke: 'var(--ink-2)', strokeWidth: '1.2px', strokeDasharray: '5 3'});
  });
  if (vis(D.meta.snapshot_end, FULL[1])) rect(plot, X(D.meta.snapshot_end), rows.human.y, X(FULL[1]) - X(D.meta.snapshot_end), y1 - rows.human.y, mixT('var(--ink)', 5));

  // HUMAN
  const hu = rows.human, hy = hu.y + 15;
  CK.txt(gut, 2, hy + 4, nar ? 'owner' : 'the owner', 'lab');
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
  // the owner's messages to the neighbor session(s), on a row of their own (smaller marks)
  if (NB) {
    const r = rows.humanNb, cy = r.y + 9, gN = CK.el('g', {}, plot), nNodes = [];
    CK.txt(gut, 2, cy + 4, nar ? '→ others' : 'to the others', 'lab');
    if (fast) { const pm = [PB(), PB(), PB(), PB(), PB()]; NB.sessions.forEach(nb => nb.msgs.forEach(m => { if (vis(m[0], m[0])) markPath(pm, m[1], x(m[0]), cy, 0.8); })); flushMarks(pm, gN); }
    else NB.sessions.forEach(nb => nb.msgs.forEach(m => {
      if (!vis(m[0], m[0])) return;
      const g = CK.el('g', {}, gN), cx = x(m[0]);
      CK.el('circle', {cx, cy, r: 7, class: 'ck-hit'}, g);
      sty(humanMark(g, m[1], cx, cy), {transform: `translate(${cx}px, ${cy}px) scale(0.8) translate(${-cx}px, ${-cy}px)`});
      TIP(f, g, () => `<b style="font-size:1.06em">${esc(m[3])}</b><br>${when(m[0])} · ${HU.cats[m[1]]} · to ${esc(nb.name)}` + promptTip(m[4], m[6]) +
        `<span style="display:block;font-size:.8em;color:var(--muted)">${KINDLAB[HU.kinds[m[2]]] || ''}; not counted in this page’s totals</span>`);
      nNodes.push(g);
      readable(f, g, pidx(nb.name, m[0], m[3]));
    }));
    NAV(f, nNodes, {onEnter: n => n._go && n._go()});
  }

  // AGENTS: the main agent (tint: busy; solid: active; dotted: watching its own workflows, counted idle)
  const mr = rows.main;
  CK.txt(gut, 2, mr.y + 13, nar ? 'main' : 'main agent', 'lab');
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

  // AGENTS: the neighbor session(s), another Claude session on the lab's own machine, from its transcripts: its busy
  // time (grey), its subagents (the thin bar under it) and its key events (a marker each; red for the host down)
  if (NB) NB.sessions.forEach((nb, k) => {
    const r = rows['nb' + k], gN = CK.el('g', {}, plot), nNodes = [], eNodes = [];
    CK.txt(gut, 2, r.y + 14, nb.lane || 'session', 'lab');
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
        TIP(f, n, () => `<b>${esc(nb.name)}: busy</b> ${span(a, b)} (${dur(b - a)})<br>${esc(nb.title)}` +
          `<br>its subagents busy in this span: ${dur(overlap(nb.sub, a, b))} of agent time`); nNodes.push(n);
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
  CK.txt(gut, 2, cr.y + 14, 'subagents', 'lab');
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
const GNAME = GRP.map((g, i) => {
  const base = g.wf < 0 ? 'Agent tool and forks' : g.name;
  return GRP.filter(h => h.name === g.name).length > 1 ? `${base}, ${hm(g.s)}` : base;
});
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
  CK.txt(gut, 2, 14, nar ? 'SUBAGENTS' : 'EVERY SUBAGENT', 'lab-strong');
  if (!DL.gs.length) { CK.txt(svg, L + 8, 64, 'No subagent ran in this window.', 'lab'); return; }
  const gNodes = [], aNodes = [], maxc = Math.floor((L - 6) / 6.1);
  DL.gs.forEach((g, k) => {
    if (k % 2) rect(bg, 0, g.y - 1, W, g.h + 2, mixT('var(--ink)', 3));
    const w = g.wf >= 0 ? WFS[g.wf] : null, name = GNAME[g.i];
    const lab = nar ? halo(CK.txt(gut, L + 2, g.y + 11, name, 'lab')) : CK.txt(gut, 2, g.y + 11, name.length > maxc ? name.slice(0, maxc - 1) + '…' : name, 'lab');
    sty(lab, {fontSize: '11px'}).setAttribute('aria-hidden', 'true');
    const hit = CK.el('rect', nar ? {x: 0, y: g.y, width: L + 2 + 6.2 * name.length, height: 13, class: 'ck-hit'} : {x: 0, y: g.y, width: L - 4, height: Math.max(14, g.h), class: 'ck-hit'}, gut);
    const st = w ? Object.entries(w.states).map(([s2, n]) => `${n} ${s2}`).join(', ') : '';
    TIP(f, hit, () => w ? `<b>${esc(name)}</b>${w.status === 'running' ? ' (still running at the snapshot)' : w.status === 'killed' ? ' (stopped)' : ''}` +
      `${w.summary ? `<br>${esc(w.summary)}` : ''}<br>${span(w.s, w.e)}<br>${w.agents} agents: ${st}` +
      `<br>${num(w.busy_min / 60, 1)} agent-hours busy · ${tok(w.tokens.total)} tokens${w.phases.length ? `<br>phases: ${w.phases.map(esc).join(' → ')}` : ''}`
      : `<b>${esc(name)}</b><br>${g.n} agents started with the Agent tool, and their forks`);
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
    TIP(f, n, () => `<b>${esc(a.label)}</b>${a.phase ? ` · ${esc(a.phase)}` : ''}<br>${esc(wfName(a))}<br>${span(a.s, a.e)} · busy ${dur(a.busy * 60)}` +
      `<br>${a.st} · ${tok(a.tok)} tokens (${tok(a.otok)} output) · ${num(a.tools, 0)} tool calls`);
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
  const d = document.getElementById('tl-days');
  const lab = document.createElement('span'); lab.className = 'tl-lab'; lab.textContent = 'Day:'; d.appendChild(lab);
  DN.forEach((n, i) => presetBtns.push(button(d, n, () => animateTo(...dayView(i)), {view: clampV(...dayView(i)), aria: `Show ${n} ${MOL(i)}`})));
  const sp = document.getElementById('tl-spans');
  const lab2 = document.createElement('span'); lab2.className = 'tl-lab'; lab2.textContent = 'Spans:'; sp.appendChild(lab2);
  const H = t => HL.find(h => h.title.indexOf(t) >= 0);
  const spans = [
    ['179 agents and a usage limit', hlView(H('usage limit'))],
    ['Review and overnight validation', [H('report review').a - 1800, H('Validation overnight').b + 1800]],
    ['Claims check v3, four cards to three', [H('Claims check v3 begins').a, H('v3 campaign').b]],
    ['The last queue and the pause', [H('Gathers and scatters').a - 3600, H('The weekly limit').b]],
    ['Chip diagram, heat and DV2', [H('Chip diagram and this timeline').a, H('A major pass').a]],
    ['The major pass', [H('A major pass').a, 10 * DAY + 3 * 3600]],
    ['Sparse parity, DV2’s verdicts, a third card', [10 * DAY + 3.5 * 3600, 10 * DAY + 18.5 * 3600]],
    ['Dashboard, new users and the hang', [11 * DAY + 12.5 * 3600, 12 * DAY + 3 * 3600]],
    ['The chip diagram’s loop, a card off the bus', [12 * DAY + 5 * 3600, 13 * DAY + 3 * 3600]],
    ['The lab day', [13 * DAY + 6 * 3600, 13 * DAY + 17 * 3600]],
    ['Audit, Antigravity, the checkpoint', [15 * DAY + 10.5 * 3600, FULL[1]]],
  ].filter(([, v]) => v[0] < FULL[1] && v[1] > FULL[0] && v[1] > v[0]);
  spans.forEach(([t, v]) => presetBtns.push(button(sp, t, () => animateTo(...v), {view: clampV(...v)})));
  const tgs = document.getElementById('tg-sub'), tgp = document.getElementById('tg-pages'), det = document.getElementById('tl-detail'), detLeg = document.getElementById('tl-detail-leg');
  tgs.addEventListener('click', () => {
    S.sub = !S.sub; tgs.setAttribute('aria-pressed', String(S.sub)); det.hidden = !S.sub; detLeg.hidden = !S.sub;
    if (S.sub) { if (!detail) { detail = CK.frame('tl-detail', {label: 'Every subagent, one thin lane each, grouped by workflow', minW: 300, maxW: 1440, height: W => detailLayout(W).H, draw: drawDetail}); gestures(detail); } else detail.redraw(); }
  });
  tgp.addEventListener('click', () => { S.perPage = !S.perPage; tgp.setAttribute('aria-pressed', String(S.perPage)); legendArt(); main.redraw(); });
})();
function pressed() { presetBtns.forEach(b => b.setAttribute('aria-pressed', String(Math.abs(b._view[0] - S.v[0]) < 90 && Math.abs(b._view[1] - S.v[1]) < 90))); }
function readout() {
  const [a, b] = S.v;
  const nm = MSG.filter(m => m.t >= a && m.t <= b).length;
  const mb = overlap(BUSY.map(q => [q.s, q.e]), a, b) / 3600;
  const sb = (overlap(SUBIV.workflow, a, b) + overlap(SUBIV.tool, a, b)) / 3600;
  const ch = CU.reduce((s, u) => s + overlap(u, a, b), 0) / 3600;
  let pk = 0, po = 0;
  for (let j = Math.max(0, Math.floor((a - C0) / 60)); j < Math.min(CW.length, Math.ceil((b - C0) / 60)); j++) { pk = Math.max(pk, CW[j] + CT[j]); po = Math.max(po, OW[j] + OT[j]); }
  const nd = DEP.filter(d => d.t >= a && d.t <= b).length, nc = COM.filter(c => c.t >= a && c.t <= b).length;
  setH('tl-readout', `Showing <b>${span(a, b)}</b> (${dur(b - a)}). In view: <b>${nm}</b> message${nm === 1 ? '' : 's'} · main agent busy <b>${hrs(mb)}</b> · ` +
    `subagents <b>${num(sb, 1)} agent-h</b>${pk ? ` (up to ${po} at once${pk > po ? `; ${pk} counting failed starts` : ''})` : ''} · cards <b>${num(ch, 1)} card-h</b> · ` +
    `<b>${nd}</b> deploy${nd === 1 ? '' : 's'} · <b>${nc}</b> commit${nc === 1 ? '' : 's'}`);
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
const famLegend = () => CA.families.map((fm, i) => (i === DEVF ? {key: fm.key, label: 'development run, from the transcripts (outlined)', sw: SW.dev('var(--ink-2)')}
  : {key: fm.key, label: fm.short || fm.label, mark: 'box', color: FAMCOL[i]}));
function legendCards() {
  const items = S.cardMode === 'card' ? CK.cardLegend(CA.ids).concat([{key: 'dev', label: 'development run, from the transcripts (outlined)', sw: SW.dev('var(--c1)')}]) : famLegend();
  legend('leg-cards', items.concat(HOSTEV.length ? [{key: 'down', label: 'the host down: hung, or power-cycled', sw: SW.down}] : [])
    .concat([1, 2, 3, 4].map(n => ({key: 'u' + n, label: n === 1 ? 'cards in use: 1' : String(n), sw: SW.step(n)}))));
}
function legendArt() {
  legend('leg-art', (S.perPage ? [{key: 'n', label: 'first publish', mark: 'dot', color: 'var(--ink)'}, {key: 'u', label: 'update', mark: 'ring', color: 'var(--ink)'}]
    : [{key: 'd', label: 'deploys in one minute (the bar’s height: how many)', sw: SW.bar}, {key: 'n', label: 'a first publish among them', sw: SW.barDot}])
    .concat([{key: 'c', label: 'commit, this session', sw: SW.tall}, {key: 'o', label: 'commit, another session', sw: SW.short}]));
}
legend('leg-human', [
  {key: 'r', label: 'request', mark: 'dot', color: 'var(--ink)'}, {key: 'c', label: 'correction', mark: 'diamond', color: 'var(--ink)'},
  {key: 'a', label: 'approval or answer', mark: 'box', color: 'var(--ink)'}, {key: 'q', label: 'question', mark: 'ring', color: 'var(--ink)'},
  {key: 's', label: 'status', mark: 'line', color: 'var(--ink)'},
  {key: 'act', label: 'estimated reading + typing', mark: 'box', color: mixT('var(--ink-2)', 55)},
  {key: 'ses', label: 'engagement session', mark: 'box', color: mixT('var(--ink)', 14)}]
  .concat(NB ? [{key: 'nbm', label: 'the row below: messages to the other sessions (smaller marks)', mark: 'dot', color: 'var(--ink-2)'}] : []));
legend('leg-agents', [
  {key: 'ma', label: 'main agent active', color: COL.main}, {key: 'mb', label: 'main agent waiting inside a turn', color: mixT('var(--c7)', 32)},
  {key: 'mw', label: 'main agent watching its workflows (idle)', sw: SW.dotted},
  {key: 'wf', label: 'workflow agents busy', color: COL.wf}, {key: 'tl', label: 'Agent-tool agents and forks busy', color: COL.tool},
  {key: 'fl', label: 'agents that failed or ended on an error', color: COL.fail},
  {key: 'lim', label: 'usage limit reached', mark: 'dash', color: 'var(--bad)'}]
  .concat(NB ? [{key: 'nb', label: 'another session busy', color: 'var(--ref)'}, {key: 'nbs', label: 'its subagents busy', color: mixT('var(--c4)', 75)},
    {key: 'nbe', label: 'its key events (red: the host down)', mark: 'diamond', color: 'var(--ink)'}] : []));
legend('tl-detail-leg', [{key: 'w', label: 'workflow agent busy', color: COL.wf}, {key: 't', label: 'Agent-tool agent or fork busy', color: COL.tool},
  {key: 'f', label: 'failed, ended on an error or stopped', color: COL.fail}, {key: 'i', label: 'thin line: running, not busy', mark: 'line', color: 'var(--ink-2)'}]);
legendCards(); legendArt();
CK.seg('cards-mode', {label: 'Colour the card intervals by', options: [['card', 'card'], ['family', 'experiment family']], value: S.cardMode,
  onChange: v => { S.cardMode = v; legendCards(); main.redraw(); }});

(function () {
  document.getElementById('tg-pages').setAttribute('aria-pressed', String(S.perPage));
  main = CK.frame('tl', {label: 'The week on one time axis: the owner, the agents, the cards and the artifacts', minW: 300, maxW: 1440,
    height: W => layout(W).H, draw: drawMain});
  gestures(main);
  readout(); pressed();
  const running = AG.totals.running_workflows.length;
  setH('tl-cap', `All times PDT. The data ends at the snapshot, ${when(D.meta.snapshot_end)} (shaded after it); ${running === 0 ? 'no workflow was' : running === 1 ? 'one workflow was' : `${running} workflows were`} ` +
    `still running then. Card work before the session (on 18 September) is left out. The owner’s bars and sessions are estimates (rule in <a href="#method">§5</a>). ` +
    `Subagent counts are per minute: an agent counts in a minute if any of its busy time falls in it. The lane’s scale follows the agents that did not fail; ` +
    `agents that failed or ended on an error (${PKM.started_in_it} of the ${PK} in the minute the usage limit hit on 20 September started in that minute) are drawn on top, and cut at the top of the lane.` +
    (NB ? ` The other sessions’ lanes come from their own transcripts (<a href="#method">§5</a>); their time is not in this page’s totals.` : ''));
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
  const days = [];
  MSG.forEach(m => { const d = dayOf(m.t); if (!days.length || days[days.length - 1][0] !== d) days.push([d, []]); days[days.length - 1][1].push(m); });
  host.innerHTML = days.map(([d, ms]) => `<section class="ask-day" data-day="${d}"><h3>${DN[d]} ${MOL(d)} <span class="ask-n">${ms.length} message${ms.length > 1 ? 's' : ''}</span></h3><ol class="ask-list">` +
    ms.map(m => `<li data-cat="${m.cat}"><button type="button" data-t="${m.t}"><svg class="ask-mark" width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" fill="var(--ink)">${MARK[m.cat] || MARK[0]}</svg>` +
      `<span class="ask-sum">${esc(m.sum)}</span><span class="ask-meta">${hm(m.t)} · ${esc(HU.cats[m.cat])}${m.rid ? ` · ${esc(m.rid)}` : ''}${m.kind === 'talk' ? ' · from a page’s Talk tab' : ''}` +
      `<span class="ask-est"> · about ${dur(m.act)} to read and write</span></span></button>${words(m.text, false, pidx('the main session', m.t, m.sum))}</li>`).join('') + '</ol></section>').join('');
  host.addEventListener('click', e => {
    const b = e.target.closest('button[data-t]'); if (!b) return;
    const t = +b.dataset.t; animateTo(t - 3 * 3600, t + 3 * 3600);
    document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'});
  });
  // the owner's messages to the neighbor session(s): after the list, apart from its totals and its filter
  const hnb = document.getElementById('asked-nb');
  if (hnb && NB) hnb.innerHTML = NB.sessions.filter(nb => nb.msgs.length).map(nb => {
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
  const counts = HU.totals.by_category, opts = [['all', `all ${HU.totals.n}`]].concat(HU.cats.map((c, i) => [String(i), `${PL[c] || c} (${counts[c] || 0})`]));
  CK.seg('asked-filter', {label: 'Show', options: opts, value: 'all', onChange: v => {
    host.querySelectorAll('li[data-cat]').forEach(li => { li.hidden = v !== 'all' && li.dataset.cat !== v; });
    host.querySelectorAll('section.ask-day').forEach(sec => { sec.hidden = !sec.querySelector('li[data-cat]:not([hidden])'); });
  }});
})();

/* ---------- who did the time ---------- */
(function () {
  const W0 = D.who, wfh = subHours('workflow'), tlh = subHours('tool');
  const rows = [
    {label: 'Owner, active', est: true, unit: 'h', segs: [{v: W0.human_active_h, c: 'var(--ink-2)', t: `estimated reading + typing: ${hrs(W0.human_active_h, 2)}; ${hrs(W0.human_active_paste_h, 2)} with pasted text not counted as typing`}], mark: W0.human_active_paste_h},
    {label: 'Owner, engagement', est: true, unit: 'h', segs: [{v: W0.human_engagement_h, c: mixT('var(--ink)', 30), t: `${HU.totals.sessions} sessions (messages under 30 min apart), from the estimated start of the first message to the last: ${hrs(W0.human_engagement_h, 2)}`}]},
    {label: 'Main agent, busy', unit: 'h', segs: [{v: W0.main_strict_h, c: COL.main, t: `active (events under 3 min apart): ${hrs(W0.main_strict_h, 2)}`},
      {v: BUSY_H - W0.main_strict_h, c: mixT('var(--c7)', 32), t: `waiting inside a turn: ${hrs(BUSY_H - W0.main_strict_h, 2)}, of it ${hrs(W0.main_tool_wait_lab_h, 2)} on card runs and the lab machines`}]},
    {label: 'Subagents, busy', unit: 'agent-h', segs: [{v: wfh, c: COL.wf, t: `${AG.totals.by_kind.workflow} workflow agents: ${num(wfh, 1)} agent-hours`},
      {v: tlh, c: COL.tool, t: `${AG.totals.by_kind.agent} Agent-tool agents and ${AG.totals.by_kind.fork} forks: ${num(tlh, 1)} agent-hours`}]},
    {label: 'Cards, held', unit: 'card-h', segs: CA.per_card.map(p => ({v: p.held_h, c: CK.card(p.id).color, t: `${CK.card(p.id).label}: ${num(p.held_h, 2)} card-hours held (${num(p.busy_h, 2)} busy)`}))},
  ];
  CK.legend('who-leg', [{key: 'h', label: 'the owner', mark: 'box', color: 'var(--ink-2)'}, {key: 'm', label: 'main agent, active', mark: 'box', color: COL.main},
    {key: 'mw', label: 'main agent, waiting inside a turn', mark: 'box', color: mixT('var(--c7)', 32)}, {key: 'w', label: 'workflow agents', mark: 'box', color: COL.wf},
    {key: 't', label: 'Agent-tool agents and forks', mark: 'box', color: COL.tool}].concat(CK.cardLegend(CA.ids)));
  const max = Math.max(...rows.map(r => r.segs.reduce((s, q) => s + q.v, 0)));
  CK.frame('who', {label: 'Who did the time: the owner, the agents and the cards, in hours', minW: 300, maxW: 1100,
    height: W => (W < 600 ? rows.length * 50 + 56 : rows.length * 38 + 44), draw(f) {
      const nar = f.narrow, L = nar ? 8 : 214, R = nar ? 80 : 100, T = 10, rh = nar ? 50 : 38, bh = nar ? 16 : 20;
      const x = CK.lin(0, Math.ceil(max / 20) * 20, L, f.W - R), nodes = [], labs = [];
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      for (const t of x.ticks(nar ? 4 : 6)) { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: T + rows.length * rh, class: 'grid-line'}, g); labs.push(CK.txt(g, x(t), T + rows.length * rh + 16, num(t, 0), 'tick', 'middle')); }
      labs.push(CK.txt(g, nar ? L : (L + f.W - R) / 2, f.H - 4, 'hours (agent-hours, card-hours)', 'lab', nar ? 'start' : 'middle'));
      rows.forEach((r, i) => {
        const y = T + i * rh + (nar ? 20 : (rh - bh) / 2);
        CK.txt(f.svg, nar ? L : L - 10, nar ? y - 6 : y + bh / 2 + 4, r.label + (r.est ? ' (estimate)' : ''), 'lab', nar ? 'start' : 'end');
        let acc = 0;
        r.segs.forEach(s => {
          if (s.v <= 0) return;
          const n = rect(f.svg, x(acc), y, Math.max(1, x(acc + s.v) - x(acc)), bh, s.c, {rx: 2});
          sty(n, {stroke: 'var(--page)', strokeWidth: '1.5px'});
          CK.tip(f, n, `<b>${esc(r.label)}</b><br>${esc(s.t)}`); nodes.push(n); acc += s.v;
        });
        if (r.mark != null) lineEl(f.svg, x(r.mark), y - 3, x(r.mark), y + bh + 3, {stroke: 'var(--ink)', strokeWidth: '2px'});
        labs.push(CK.txt(f.svg, x(acc) + 6, y + bh / 2 + 4, `${num(acc, 1)} ${r.unit}`, 'lab-strong'));
      });
      CK.inside(f, labs); CK.keynav(f, nodes);
    }});
  setH('who-cap', `The owner’s rows are estimates. The tick on the first bar marks ${hrs(W0.human_active_paste_h, 2)}, the total when the few long pasted messages count 3 minutes of typing at most. ` +
    `The main agent’s solid part (${hrs(W0.main_strict_h)}) is time in which its events were under 3 minutes apart; the tinted part (${hrs(BUSY_H - W0.main_strict_h)}) is time inside a turn spent waiting, ` +
    `${hrs(W0.main_tool_wait_lab_h)} of it on card runs and the lab machines. It also spent ${hrs(W0.main_watch_h)} in loops that only watched its own workflows; that time counts as idle and is not in its bar, ` +
    `because the subagents’ hours already cover it. Card-hours are counted from the first message on and include ${hrs(CA.totals.held_h - CA.totals.held_h_without_dev, 1)} of development runs seen only in the transcripts ` +
    `(${num(CA.totals.held_h_incl_18sep, 2)} card-hours from the data files alone with the work of 18 September). Hover, tap or tab to a bar for its exact value.`);
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
  setH('cardh-cap', `${num(tot.held_h, 1)} card-hours held in all, ${num(tot.busy_h, 1)} busy. Held counts a card’s gaps shorter than 2 minutes as held, because a queue keeps the card between passes. Busy is the exact union of the intervals. ` +
    `The families are shades of one grey, a step per family in time order; the outlined part is the development runs (${CA.totals.dev_calls} commands of the main agent, ${hrs(CA.totals.dev_busy_h, 2)} of their own time), which left no data file. ` +
    `aifoundry1 card 0 ran only smoke tests: amendment A4 excluded it from the campaign because it overheats under load.`);
})();

/* ---------- the owner's time ---------- */
(function () {
  const t = HU.totals, bc = t.by_category;
  setH('human-text', `The owner sent <b>${t.n}</b> messages (${num(t.chars, 0)} characters): ${bc.request} requests, ${bc.correction} corrections, ` +
    `${bc['approval/answer']} approvals or answers, ${bc.question} questions and ${bc.status} status messages. The time spent on them is not recorded anywhere, ` +
    `so it is <b>estimated</b> from what was read and typed: <b>${hrs(t.active_h, 2)}</b> in all (reading ${hrs(t.read_h, 2)}, typing ${hrs(t.type_h, 2)}), ` +
    `or <b>${hrs(t.active_paste_h, 2)}</b> if the few long pasted messages count at most 3 minutes of typing each. The messages fall into <b>${t.sessions}</b> ` +
    `engagement sessions that span <b>${hrs(t.engagement_h, 2)}</b>. That is an upper bound on attention, from the estimated start of each session’s first message to its last message.`);
  document.getElementById('human-rules').innerHTML = [
    ['Typing', 'the message’s length at 200 characters a minute, at least 10 s (the one interrupt counts 2 s; images are not counted).'],
    ['Reading', 'the words of the agent’s latest reply before the message, at 250 words a minute and at most 10 minutes; each reply counts for one message only.'],
    ['Active time', 'reading plus typing.'],
    ['Pasted text', 'the second total counts at most 3 minutes of typing for the messages over 2,000 characters and two shorter ones that were mostly pasted.'],
    ['Engagement session', 'a run of messages less than 30 minutes apart, from its first message’s estimated start (the time it was sent less its active time) to its last message.']]
    .map(([k, v]) => `<li><b>${k}:</b> ${v}</li>`).join('');
})();

/* ---------- tokens ---------- */
(function () {
  const T = TO.totals, all = T.all.total;
  const rows = [['Main agent', T.main], ['Workflow agents', T.workflow], ['Agent-tool agents', T.agent], ['Forks', T.fork], ['All subagents', T.subagents]];
  const cell = v => `<td class="num" data-sort="${v}">${num(v, 0)}</td>`;
  const tb = document.getElementById('tok-table');
  tb.innerHTML = '<thead><tr><th>Who</th><th class="num">Input (not cached)</th><th class="num">Cache writes</th><th class="num">Cache reads</th><th class="num">Output</th><th class="num">Total</th><th class="num">Share</th></tr></thead><tbody>' +
    rows.map(([k, v]) => `<tr><td>${k}</td>${cell(v.input)}${cell(v.cache_creation)}${cell(v.cache_read)}${cell(v.output)}${cell(v.total)}<td class="num">${CK.fmt.pct(v.total / all, 1)}</td></tr>`).join('') +
    `<tr class="total"><td>Everything</td>${cell(T.all.input)}${cell(T.all.cache_creation)}${cell(T.all.cache_read)}${cell(T.all.output)}${cell(T.all.total)}<td class="num">100%</td></tr></tbody>`;
  CK.stackTable(tb);
  setH('tok-text', `Tokens are counted from the <b>usage fields</b> that the API returned with every assistant message, as the session’s transcripts record them. ` +
    `A message streamed over several transcript lines is counted once, and a message that a fork copied from its parent counts only for the parent. ` +
    `<b>${num(all / 1e9, 2)} billion</b> tokens in all, and <b>${CK.fmt.pct(T.all.cache_read / all, 1)}</b> of them are <i>cache reads</i>: at every step an agent’s ` +
    `conversation so far is read again from the prompt cache. Cache writes are ${CK.fmt.pct(T.all.cache_creation / all, 1)}, and output, what the models wrote including their thinking, is ` +
    `${CK.fmt.pct(T.all.output / all, 2)} (${tok(T.all.output)}). The subagents used ${CK.fmt.pct(T.subagents.total / all, 0)} of all tokens and wrote ${CK.fmt.pct(T.subagents.output / T.all.output, 0)} of the output.`);
  const days = D.perday.map(d => d.date), PD = TO.per_day;
  const SER = [['main', 'main agent', COL.main, d => PD[d] && PD[d].main], ['workflow', 'workflow agents', COL.wf, d => PD[d] && PD[d].workflow],
    ['tool', 'Agent-tool agents and forks', COL.tool, d => { const a = PD[d] && PD[d].agent, b = PD[d] && PD[d].fork; if (!a && !b) return null; const o = {}; ['input', 'cache_creation', 'cache_read', 'output', 'total'].forEach(k => { o[k] = ((a || {})[k] || 0) + ((b || {})[k] || 0); }); return o; }]];
  CK.legend('tok-leg', SER.map(s => ({key: s[0], label: s[1], mark: 'box', color: s[2]})));
  const MEAS = [['total', 'all tokens'], ['output', 'output'], ['cache_creation', 'cache writes'], ['input', 'input (not cached)']];
  let meas = 'total';
  const f = CK.frame('tokday', {label: 'Tokens per day, main agent and subagents', minW: 300, maxW: 1100, height: W => (W < 600 ? 260 : 300), draw(f) {
    const nar = f.narrow, L = nar ? 50 : 62, R = 10, T = 26, B = 40;
    const tot = days.map(d => SER.reduce((s, q) => s + ((q[3](d) || {})[meas] || 0), 0)), mx = Math.max(...tot) * 1.12 || 1;
    const x = CK.lin(-0.5, days.length - 0.5, L, f.W - R), y = CK.lin(0, mx, f.H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xt: days.map((d, i) => i), xfmt: i => (nar ? DN[i].slice(4) : DN[i]), yfmt: v => tokAx(v),
      xl: nar ? (MO(DN.length - 1) === 'Oct' ? 'September–October (PDT)' : 'September (PDT)') : null, yl: `${MEAS.find(m => m[0] === meas)[1]} per day (PDT)`});
    const bw = Math.min(56, (x(1) - x(0)) * 0.62), nodes = [], labs = [];
    days.forEach((d, i) => {
      let acc = 0;
      SER.forEach(q => {
        const v = ((q[3](d) || {})[meas] || 0); if (!v) return;
        const n = rect(f.svg, x(i) - bw / 2, y(acc + v), bw, Math.max(0.5, y(acc) - y(acc + v)), q[2]);
        sty(n, {stroke: 'var(--page)', strokeWidth: '1px'});
        CK.tip(f, n, `<b>${DN[i]} ${MO(i)}</b> · ${q[1]}<br>${MEAS.find(m => m[0] === meas)[1]}: ${num(v, 0)} (${tok(v)})`); nodes.push(n); acc += v;
      });
      if (acc && (!nar || acc >= 0.25 * mx)) labs.push(CK.txt(f.svg, x(i), y(acc) - 5, nar ? tokAx(acc) : tok(acc), 'tick', 'middle'));
    });
    CK.inside(f, labs); CK.keynav(f, nodes);
  }});
  CK.seg('tok-seg', {label: 'Measure', options: MEAS, value: meas, onChange: v => { meas = v; f.redraw(); }});
  const ck = TO.per_day_check;
  setH('tok-cap', `Days are PDT and a message counts in the day of its first line. The per-day subagent figures add up to ${num(ck.subagents_sum_per_day, 0)}, which is ${num(ck.subagents_total - ck.subagents_sum_per_day, 0)} ` +
    `(${CK.fmt.pct((ck.subagents_total - ck.subagents_sum_per_day) / ck.subagents_total, 3)}) short of the total above: messages still being written in the second the agents were extracted fall after the cut-off. ` +
    `No subagent ran on 21–23 September, and on 26 September none ran after the weekly limit at 08:41.`);
})();

/* ---------- day by day: small multiples, one row per day ---------- */
(function () {
  CK.legend('days-leg', [{key: 'h', label: 'the owner’s messages', mark: 'dot', color: 'var(--ink)'}, {key: 'm', label: 'main agent busy', mark: 'box', color: COL.main},
    {key: 'w', label: 'workflow agents', mark: 'box', color: COL.wf}, {key: 't', label: 'Agent-tool agents and forks', mark: 'box', color: COL.tool},
    {key: 'f', label: 'failed or ended on an error (cut at the top)', mark: 'box', color: COL.fail},
    {key: 'c', label: 'cards in use (height: how many)', mark: 'box', color: INUSE_FILL[3]}]);
  const PDY = D.perday, PEAK = niceMax(PKOK);   // scaled to the peak of agents that did not fail; failed starts are cut
  setH('d-scale', PEAK); setH('d-okpk', PKOK); setH('d-pk', PK);
  CK.frame('days', {label: 'The week by day: one row per day, midnight to midnight', minW: 300, maxW: 1100, height: W => PDY.length * 70 + 30, draw(f) {
    const nar = f.narrow, L = nar ? 50 : 70, R = nar ? 8 : 200, T = 24, rh = 70;
    const x = CK.lin(0, DAY, L, f.W - R), g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), nodes = [], labs = [];
    for (let hh = 0; hh <= 24; hh += nar ? 6 : 3) { CK.el('line', {x1: x(hh * 3600), x2: x(hh * 3600), y1: T - 4, y2: T + PDY.length * rh, class: 'grid-line'}, g0); labs.push(CK.txt(g0, x(hh * 3600), T - 9, pad2(hh % 24 === 0 && hh ? 24 : hh) + ':00', 'tick', 'middle')); }
    PDY.forEach((d, i) => {
      const y = T + i * rh, a = d.day * DAY, b = a + DAY, X = t => x(Math.max(a, Math.min(b, t)) - a), g = CK.el('g', {}, f.svg);
      rect(g, 0, y, f.W, rh - 4, i % 2 ? mixT('var(--ink)', 3) : 'transparent');
      CK.txt(g, 4, y + 18, d.label, 'lab-strong');
      // owner
      MSG.filter(m => m.t >= a && m.t < b).forEach(m => sty(CK.el('circle', {cx: X(m.t), cy: y + 7, r: 2.6}, g), {fill: 'var(--ink)'}));
      // main agent
      BUSY.filter(q => vis2(q.s, q.e, a, b)).forEach(q => rect(g, X(q.s), y + 13, Math.max(1, X(q.e) - X(q.s)), 5, COL.main));
      // subagents, 5-minute maxima, scaled to the week's peak of agents that did not fail (failed ones on top, cut)
      const sy = y + 48, sh = 26, j0 = Math.max(0, Math.floor((a - C0) / 60)), j1 = Math.min(CW.length, Math.floor((b - C0) / 60));
      const hh = v => Math.min(v, PEAK) / PEAK * sh;
      lineEl(g0, X(a), sy - sh, X(b), sy - sh, {stroke: 'var(--grid)', strokeWidth: '1px', strokeDasharray: '1 3'});
      for (let j = j0; j < j1; j += 5) {
        let best = -1, bw = 0, bt = 0, bf = 0; for (let k = j; k < Math.min(j + 5, j1); k++) if (CW[k] + CT[k] > best) { best = CW[k] + CT[k]; bw = OW[k]; bt = OT[k]; bf = CF[k]; }
        if (best <= 0) continue;
        const xx = X(C0 + j * 60), ww = Math.max(0.8, X(C0 + (j + 5) * 60) - xx);
        if (bw) rect(g, xx, sy - hh(bw), ww, hh(bw), COL.wf);
        if (bt) rect(g, xx, sy - hh(bw + bt), ww, hh(bw + bt) - hh(bw), COL.tool);
        if (bf && hh(bw + bt + bf) > hh(bw + bt)) rect(g, xx, sy - hh(bw + bt + bf), ww, hh(bw + bt + bf) - hh(bw + bt), COL.fail);
      }
      // cards in use
      let t = INU.start;
      for (const [n, cnt] of INU.rle) { const s = t, e = t + cnt * 60; t = e; if (!n || !vis2(s, e, a, b)) continue; rect(g, X(s), y + 64 - n / 4 * 12, Math.max(0.8, X(e) - X(s)), n / 4 * 12, INUSE_FILL[n]); }
      if (!nar) CK.txt(g, f.W - R + 12, y + 18, `${d.human_n} msg · ${num(d.main_busy_h + d.sub_agent_h, 1)} agent-h`, 'tick');
      if (!nar) CK.txt(g, f.W - R + 12, y + 34, `${num(d.card_h, 1)} card-h · ${d.deploys} deploys`, 'tick');
      const hit = CK.el('rect', {x: 0, y, width: f.W, height: rh - 4, class: 'ck-hit'}, g);
      hit.style.cursor = 'pointer';
      CK.tip(f, hit, `<b>${d.label} ${MOL(d.day)}</b><br>${d.human_n} messages, estimated active ${num(d.human_active_min, 0)} min<br>main agent busy ${hrs(d.main_busy_h)}; subagents ${num(d.sub_agent_h, 1)} agent-h, up to ${d.peak_sub_ok} at once${d.peak_sub > d.peak_sub_ok ? ` (${d.peak_sub} counting failed starts)` : ''}` +
        `<br>cards ${num(d.card_h, 1)} card-h · ${d.deploys} deploys · ${d.commits} commits<br>${tok(d.tokens_main + d.tokens_sub)} tokens<br><i>Click or press Enter to open this day in the timeline.</i>`, {role: 'button'});
      const go = () => { animateTo(...dayView(d.day)); document.getElementById('timeline').scrollIntoView({block: 'start', behavior: CK.reduced ? 'auto' : 'smooth'}); };
      hit.addEventListener('click', go); hit._go = go;
      nodes.push(hit);
    });
    CK.inside(f, labs); CK.keynav(f, nodes, {onEnter: n => n._go()});
  }});
  function vis2(s, e, a, b) { return e >= a && s <= b; }
  // the table
  const tb = document.getElementById('day-table'), c = v => `<td class="num">${v}</td>`;
  const sum = k => PDY.reduce((s, d) => s + d[k], 0);
  tb.innerHTML = '<thead><tr><th>Day</th><th class="num">Messages</th><th class="num">Owner active, min (est.)</th><th class="num">Engagement, h (est.)</th>' +
    '<th class="num">Main agent busy, h</th><th class="num">Main agent active, h</th><th class="num">Subagents, agent-h</th><th class="num">Peak subagents (not counting failed starts)</th>' +
    '<th class="num">Card-h held</th><th class="num">Deploys</th><th class="num">Commits</th><th class="num">Tokens</th><th class="num">Output tokens</th></tr></thead><tbody>' +
    PDY.map(d => `<tr><td>${d.label}</td>${c(d.human_n)}${c(num(d.human_active_min, 1))}${c(num(d.engagement_h, 2))}${c(num(d.main_busy_h, 2))}${c(num(d.main_strict_h, 2))}` +
      `${c(num(d.sub_agent_h, 1))}<td class="num" data-sort="${d.peak_sub_ok}">${d.peak_sub_ok}${d.peak_sub > d.peak_sub_ok + 5 ? ` <span class="note">(${d.peak_sub} with ${PKM.started_in_it} failed starts)</span>` : ''}</td>${c(num(d.card_h, 2))}${c(d.deploys)}${c(d.commits)}<td class="num" data-sort="${d.tokens_main + d.tokens_sub}">${tok(d.tokens_main + d.tokens_sub)}</td>` +
      `<td class="num" data-sort="${d.out_main + d.out_sub}">${tok(d.out_main + d.out_sub)}</td></tr>`).join('') +
    `</tbody><tfoot><tr class="total"><td>The week</td>${c(sum('human_n'))}${c(num(sum('human_active_min'), 1))}${c(num(sum('engagement_h'), 2))}${c(num(sum('main_busy_h'), 2))}` +
    `${c(num(sum('main_strict_h'), 2))}${c(num(sum('sub_agent_h'), 1))}${c(Math.max(...PDY.map(d => d.peak_sub_ok)))}${c(num(sum('card_h'), 2))}${c(sum('deploys'))}${c(sum('commits'))}` +
    `${c(tok(sum('tokens_main') + sum('tokens_sub')))}${c(tok(sum('out_main') + sum('out_sub')))}</tr></tfoot>`;
  CK.sortTable(tb);   // 13 columns: on a phone the table scrolls sideways rather than stacking into 117 lines
})();

/* ---------- how it was counted ---------- */
(function () {
  const at = AG.totals, st = at.status, ht = HU.totals, bk = ht.by_kind, mt = MA.totals;
  const inSession = AR.commits.filter(c => c[0] >= D.meta.session_start).length;
  const items = [
    `<b>The owner.</b> ${ht.n} inputs: ${bk.prompt} messages typed at the prompt or sent from the Remote Control queue, ${bk.midturn} sent while the agent was working, ` +
    `${bk['slash-command']} slash commands, ${bk['question-answer']} answer${bk['question-answer'] === 1 ? '' : 's'} to the agent’s questions, ${bk.interrupt} interrupt and ${bk.talk || 0} messages written on a published page’s Talk tab, which reach the session as notifications. Tool results, other notifications, messages between agents and system text are not counted. ` +
    `A message’s time is when it was sent. Each has a summary of at most 12 words, written for this page, and <b>its own words</b>: their start in the mark’s details and in <a href="#asked">§3</a>, all of them in the reader that a click, a second tap or Enter opens. ` +
    `In the words, what this public page withholds is replaced by a marked note: a sentence about how the lab’s machines are reached (root, ssh, the network, keys or passwords), an address or a path, another person’s name or a place, ` +
    `a link to a page or a session that is not public, and the agents’ permission mode. A slash command is shown as typed, an answer to the agent’s question with the question. <b>Estimated active time</b> is reading plus typing. ` +
    `Reading is the agent’s latest reply before the message, at 250 words a minute and at most 10 minutes, each reply counted once (none for a Talk message, written on a page). Typing is the message’s length at 200 characters a minute, at least 10 s. ` +
    `The “pasted” variant counts at most 3 minutes of typing for the few messages that were mostly pasted. An <b>engagement session</b> is a run of messages less than 30 minutes apart, from the estimated start of its first message to its last message.`,
    `<b>The main agent.</b> Its events (replies, tool calls, tool results and incoming messages) are merged into one busy interval when they are less than 3 minutes apart. ` +
    `A longer gap still counts as busy when the agent was provably waiting inside a turn: on a tool call, such as a loop that watched a card run to its end, on the model, or on a compaction of its context. ` +
    `Any other gap of 3 minutes or more is idle, for example while it waited for background agents or for the owner. A gap in which its only calls in flight were loops that watched its own workflows or subagents ` +
    `(their journals, transcripts or output files) is idle too, because the subagents’ hours already count that time: ${hrs(mt.watch_h)} of such loops, drawn dotted in its lane. ` +
    `That gives ${hrs(BUSY_H)} busy: ${hrs(mt.strict_h)} active under the 3-minute rule (drawn solid) and ${hrs(BUSY_H - mt.strict_h)} of waiting inside a turn (tinted), ${hrs(mt.tool_wait_lab_h)} of it on card runs and the lab machines. ` +
    `About half an hour on 20 September was six short commands that waited together, apparently on a permission prompt; they count as waits. ${num(mt.messages, 0)} replies, ${num(mt.tool_calls, 0)} tool calls, ${mt.compactions} compactions.`,
    `<b>The subagents.</b> ${num(at.agents, 0)} transcripts: ${at.by_kind.workflow} workflow agents in ${at.workflow_runs} workflow runs (from ${at.workflow_launch_calls} Workflow calls: one refused, two resumes), ` +
    `${at.by_kind.agent} agents started with the Agent tool and ${at.by_kind.fork} forks. An agent is busy while its events are less than 3 minutes apart. The count of agents busy at once is per minute: ` +
    `an agent counts in a minute if any of its busy time falls in it. By state at the snapshot: ${st.done} done, ${st.failed + st.error} failed or ended on an error ` +
    `(99 of them starts of the limits-of-observability workflow after the usage limit), ${st.killed} stopped and ${st.running} running. ` +
    `The highest count, ${PK}, is the minute the usage limit hit on 20 September: ${PKM.started_in_it} of those agents started in that minute and ${PKM.failed} failed. ` +
    `Without the agents that failed or ended on an error the peak is ${PKOK}, and ${AG.peak.subagents_sustained_10min.value} were busy for 10 minutes on end; the lanes are scaled to that, and the failed agents are drawn in grey on top. ` +
    `${at.running_workflows.length === 1 ? 'One workflow was' : `${at.running_workflows.length} workflows were`} still running at the snapshot (${at.running_workflows.map(esc).join(', ')}), so ${at.running_workflows.length === 1 ? 'its numbers are' : 'their numbers are'} partial.`,
    `<b>The cards.</b> A card is in use while a measurement holds it. For the version-3 claims check the intervals come from the queue logs on the lab machines, which record when each pass begins and ends. ` +
    `The passes’ own records agree with the logs to within about a second. For the earlier experiments the intervals are the first and last timestamps of each data file. ` +
    `The times stated in <code>docs/findings/03-experiments.md</code> agree with both to within about a minute. A few holds carry no timestamps (${CA.undated.map(u => esc(u.E)).join(', ')}): these are drawn at their stated times or left out. ` +
    `<b>Development and debug runs</b> left no data file: they come from the transcript, as the main agent’s own commands that ran a program on a card (a host program, a launcher, it_test, telemetry sampling or a run_ script, on aifoundry2 or sent to another lab machine), ` +
    `from each call’s start to its result, less what a data file or queue log already covers. That is an upper bound, since a call’s time includes any build in the same command: ` +
    `${CA.totals.dev_calls} commands in ${CA.totals.dev_runs} runs, drawn outlined, ${hrs(CA.totals.held_h - CA.totals.held_h_without_dev, 1)} of held card time. Subagents are left out: their card work went through the logged queues. ` +
    `<b>Held</b> card-hours count a gap of less than 2 minutes as held, because a queue keeps its card between passes; <b>busy</b> card-hours are the exact union. Card work on 18 September, before the session, is left out.`,
    `<b>The artifacts.</b> A deploy is one publish of one page to spacesheep. It is counted from what the tool printed (${AR.totals.confirmed} of the ${AR.totals.deploys}) or, where a command hid its output, from the command itself. ` +
    `${AR.totals.new_spaces} deploys created a new space. ` +
      (AR.failed_attempts.length ? `${AR.failed_attempts.length} more ${AR.failed_attempts.length === 1 ? 'attempt' : 'attempts'} failed and ${AR.failed_attempts.length === 1 ? 'is' : 'are'} not counted (` +
        AR.failed_attempts.map(f => `${when(f[0])}, ${esc(AR.pages[f[1]].short)}`).join('; ') +
        `): the tool returned no result or could not reach the host, and the page was then created afresh. ` : '') +
    `Commits are the repository’s history on every branch: ${AR.totals.commits} in all, ${inSession} of them after the session began. ` +
    `Two other Claude sessions also committed to the repository, one on 24 September and one on the evening of 26 September (PDT), which also deployed pages. Their deploys are not in these transcripts, so they appear here only through their commits.`,
    ...(NB ? [`<b>The other sessions.</b> In these two weeks the owner ran ${NB.sessions.reduce((a, nb) => a + (nb.n || 1), 0)} more Claude Code sessions on the lab’s machine, on two Claude accounts, ` +
      `each in a lane of its own (the short ones share one): ` +
      NB.sessions.map(nb => `<b>${esc(nb.name)}</b>, ${esc(nb.title)} (${hrs(nb.busy_h, 2)} busy, ${nb.agents} subagents and ${num(nb.agent_h, 1)} agent-hours, ${num(nb.tokens / 1e6, 0)} million tokens)`).join('; ') + '. ' +
      `Each lane is drawn from that session’s own transcripts with the rules above: its main agent is busy while its events are under 3 minutes apart or a tool call is in flight, and the thin bar under it is when any of its subagents was busy. ` +
      `The owner’s messages to them are on the row “to the others”, each with a summary and its words, as for the main session; they, the sessions’ time, deploys and tokens are not in this page’s totals. ` +
      `Their key events (diamonds; red for a host or card down) come from their transcripts, the hosts’ own boot records and <code>docs/findings/14-card-behaviour.md</code>; a deploy of a public page and a commit are events too, and their commits are the short ticks marked as theirs. ` +
      `The maintenance session’s transcript was rewritten when it resumed on 2 October, so its part of 30 September (the link test at 14:41, the hang, the power cycle at about 15:07 and the investigation after it) ` +
      `comes from the previous snapshot’s extract: its messages of that day keep their summaries, but their words are no longer on the machine.`] : []),
    `<b>Tokens.</b> Every assistant reply in a transcript carries the usage fields the API returned with it: uncached input, cache writes, cache reads and output, which includes thinking. ` +
    `A reply streamed over several lines is counted once, and a reply that a fork copied from its parent counts only for the parent. Days are PDT, by the reply’s first line.`,
    `<b>Privacy.</b> This page is public. It shows the owner’s messages as summaries in its own words and as the owner wrote them, with the parts listed under “The owner” removed and each removal marked. It names no other person, except two published authors whose work the public reports cite: ` +
    `in the title of The Horace experiment, named after the author of the blog post it reproduces, and in the labels and commit subjects of the heat-per-mm check of a wire-energy figure (Q63). ` +
    `It shows no credentials or access paths, and does not say which account can do what on the lab machines. ` +
    `One report written for the lab lead appears only as “a report for the lab lead”, without its content or link. The pages outside the report set share one lane.` +
    (NB ? ' The other sessions’ workflows and agents are not named (the maintenance session’s served that report and fixes to the machines).' : ''),
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
