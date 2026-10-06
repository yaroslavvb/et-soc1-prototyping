const STATUS = {works_now: 'works now', needs_tooling: 'tooling', needs_fw_change: 'firmware', research_only: 'research', impossible_on_silicon: 'not on silicon', ask_team: 'ask the team'};
/* 'ask the team' is used only by §5's rungs (documents and interfaces to ask AI Foundry for); §2's instruments never carry it */
const LADDER_STATUS = Object.keys(STATUS).filter(s => s !== 'ask_team');
const CHECK = {confirmed: 'confirmed by two reviewing agents', disputed: 'reviewing agents corrected details; the row reflects them', unverified: 'not reviewed', changed: 'rewritten after review', refuted: 'refuted'};
const CHECK_SYM = {confirmed: '✓', disputed: '±', unverified: '·', changed: '†', refuted: '✗'};
const REPO = 'https://github.com/yaroslavvb/et-soc1-prototyping/';
const PAGES = 'https://spacesheep.dev/@yaroslavvb/';
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
/* [text](url) in ladder notes and rung texts becomes a link, applied after esc(); only in-page anchors, this set's spacesheep pages and the two repositories */
const lk = h => h.replace(/\[([^\]]+)\]\(((?:#|https:\/\/spacesheep\.dev\/@yaroslavvb\/|https:\/\/github\.com\/(?:yaroslavvb\/et-soc1-prototyping|aifoundry-org\/et-platform)\/)[^)\s"<]*)\)/g, '<a href="$2">$1</a>');
/* "rung N" in the same texts links to that rung's row in §5 (#rung-N), outside any link already there */
const rk = h => h.split(/(<a\b[^>]*>[\s\S]*?<\/a>)/).map((s, i) => (i % 2 ? s : s.replace(/\brung (\d+)\b/g, '<a href="#rung-$1">rung $1</a>'))).join('');
const chip = s => `<span class="chip ${s}">${STATUS[s]}</span>`;
const verif = c => `<span class="ck ${c}" title="${CHECK[c]}" aria-label="${CHECK[c]}">${CHECK_SYM[c] || '·'}</span>`;
/* §4's cards: every card the power blocks carry (the version-3 campaign's three since 26 September), in registry order;
   CARDS[0] (aifoundry2) is the reference the droop chart and the cross-card ratios use. */
const P = D.power, CARDS = CK.cardsIn(Object.keys(P.rail_filter).filter(k => k !== 'rule'));
const f = (v, n) => Number(v).toFixed(n == null ? 2 : n);
const num = CK.fmt.num, rng = (a, b, dp, unit) => CK.fmt.range(Math.min(a, b), Math.max(a, b), dp, unit);
const mm = a => [Math.min(...a), Math.max(...a)];
const sgn = (v, dp) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(dp == null ? 2 : dp);
const pct = (v, dp) => num(100 * v, dp == null ? 0 : dp) + '%';
const med = a => { const s = [...a].sort((p, q) => p - q), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
const setHTML = (id, h) => { const e = document.getElementById(id); if (e) e.innerHTML = h; };
const andList = a => (a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]);
/* per-card values as prose: "0.86 on aifoundry2, 0.87 on aifoundry3 and 1.00 on aifoundry1-c1" (unit after the first),
   or, when every card gives the same text, "767 mV on all three cards" */
const perCard = (vals, unit, cards) => { cards = cards || CARDS; const u = unit ? ' ' + unit : '';
  if (vals.every(v => v === vals[0])) return `${vals[0]}${u} on ${cards.length === 2 ? 'both' : `all ${WORD[cards.length] || cards.length}`} cards`;
  return andList(vals.map((v, i) => `${v}${i ? '' : u} on ${cards[i]}`)); };
/* the nearest plain fraction, for "about a quarter" */
const FRAC = [[1, 'all'], [3 / 4, 'three quarters'], [7 / 10, 'seven tenths'], [2 / 3, 'two thirds'], [3 / 5, 'three fifths'], [1 / 2, 'half'], [2 / 5, 'two fifths'], [1 / 3, 'a third'],
  [1 / 4, 'a quarter'], [1 / 5, 'a fifth'], [1 / 6, 'a sixth'], [1 / 7, 'a seventh'], [1 / 8, 'an eighth'], [1 / 10, 'a tenth']];
const fracWord = x => FRAC.reduce((b, e) => (Math.abs(Math.log(e[0] / x)) < Math.abs(Math.log(b[0] / x)) ? e : b))[1];
const WORD = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
const word = n => WORD[n] || num(n, 0);
/* The same classification as tools/ettelem/fit_unmetered.py moves_dram(): 'dram' in the name, except the stride-8K
   row walk, which the L3 serves (its reads cross the mesh; it is named like a DRAM row). */
const movesDram = c => c.includes('dram') && !c.includes('stride8K');
function inkOn(css) {  /* --ink or --page, whichever contrasts more with a fill (theme-aware; CK redraws on theme change) */
  const lum = c => { const s = document.createElement('span'); s.style.color = c; s.style.display = 'none'; document.body.appendChild(s);
    const cs = getComputedStyle(s).color, u = /^color\(/.test(cs) ? 1 : 255, v = (cs.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number); s.remove();
    const l = x => { x /= u; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
    return 0.2126 * l(v[0]) + 0.7152 * l(v[1]) + 0.0722 * l(v[2]); };
  const b = lum(css), k = (x, y) => (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  return k(b, lum('var(--ink)')) >= k(b, lum('var(--page)')) ? 'var(--ink)' : 'var(--page)';
}
const pretty = c => c.startsWith('dramrow/stride8K') ? `L3 reads through the mesh (<code>${esc(c)}</code>)` : `<code>${esc(c)}</code>`;
/* A session's "when" ("22 Sep, 13:16–13:22", "20–21 Sep") as days after 18 September 00:00: [start, end]. */
const parseWhen = w => {
  const m = String(w).match(/^(\d+)(?:–(\d+))? Sep(?:, (\d\d):(\d\d)(?:–(\d\d):(\d\d))?)?/);
  if (!m) return [NaN, NaN];  /* not a September date: the map leaves it out, the table sorts it last */
  const d0 = +m[1], d1 = m[2] ? +m[2] : d0;
  const T = (d, h, mi) => d - 18 + (h + mi / 60) / 24;
  /* a range of days with times ("28–29 Sep, 23:47–00:27") starts on the first day and ends on the second */
  if (m[3]) { const a = T(d0, +m[3], +m[4]); return [a, m[5] ? T(d1, +m[5], +m[6]) : a]; }
  return [T(d0, 12, 0), T(d1, 12, 0)];
};
/* CK.sortTable on a table whose tr.grp rows head groups: while a column is sorted the group rows step aside, and
   while the text filter (o.filter) or a status filter (class st-off) hides rows, a group row shows only above a
   visible one. The filter's count counts entries (o.noun), not group rows. Call it after CK.stackTable. */
function sortGrouped(t, o) {
  o = o || {};
  const api = CK.sortTable(t, o), tb = t.tBodies[0], wrap = t.closest('.ck-table-wrap');
  const fw = o.filter && wrap && wrap.previousElementSibling && wrap.previousElementSibling.classList.contains('ck-filter') ? wrap.previousElementSibling : null;
  const inp = fw && fw.querySelector('input'), cnt = fw && fw.querySelector('.ck-filter-n');
  const isGrp = r => r.classList.contains('grp'), vis = r => !r.classList.contains('ck-hidden') && !r.classList.contains('st-off');
  function fix() {
    const sorted = !!t.querySelector('th[aria-sort="ascending"], th[aria-sort="descending"]');
    let head = null, any = false;
    const close = () => { if (head) { head.classList.remove('ck-hidden'); head.classList.toggle('grp-off', sorted || !any); } };  /* the text filter does not judge group rows */
    for (const r of tb.rows) { if (isGrp(r)) { close(); head = r; any = false; } else if (vis(r)) any = true; }
    close();
    if (cnt) {
      const q = inp.value.trim(), pool = [...tb.rows].filter(r => !isGrp(r) && !r.classList.contains('st-off'));
      cnt.textContent = q ? `${pool.filter(vis).length} of ${pool.length} ${o.noun || 'rows'}` : '';
    }
  }
  if (t.tHead) t.tHead.addEventListener('click', fix);  /* runs after the header button's own sort */
  if (inp) inp.addEventListener('input', fix);
  fix();
  return Object.assign({fix}, api);
}

/* ---------- numbers the hand-kept rows quote, filled from the data: {{name}} in data.json ---------- */
const TOK = (function () {
  const F = P.fit, RF = P.rail_filter, Dp = P.droop, IU = P.idle_unsensed, A2 = F.aifoundry2, A3 = F.aifoundry3, CH = P.checks;
  /* standard errors robust to the DRAM configurations' larger scatter (HC3; power.checks) */
  const rel = k => CARDS.map(c => CH.fit[c].se_hc3[k] / F[c].coef[k]);
  const pr = (a, dp) => rng(...mm(a), dp);
  const pc = a => rng(...mm(a.map(v => Math.round(100 * v))), 0) + '%';
  const ns = CARDS.map(c => num(F[c].n, 0));
  return {
    cards: andList(CARDS),
    rf_tau: pr(CARDS.map(c => RF[c].tau_s), 2), rf_1s: pc(CARDS.map(c => RF[c].frac_1s)), rf_2s: pc(CARDS.map(c => RF[c].frac_2s)),
    droop_slope: f(Dp.mv_per_dram_offrail_w, 2), droop_n: num(Dp.n, 0), droop_rms: f(Dp.rms_mv, 2), droop_mvw: f(1 / Dp.mv_per_dram_offrail_w, 1),
    droop_slope_a3: f(CH.droop.aifoundry3.slope, 2), droop_rms_a3: f(CH.droop.aifoundry3.rms_mv, 2),
    /* per card, in CARDS order ("0.86, 0.87 and 1.00"), and the range of 1 mV in watts over the cards */
    droop_slopes: andList(CARDS.map(c => f(CH.droop[c].slope, 2))), droop_rmss: andList(CARDS.map(c => f(CH.droop[c].rms_mv, 2))),
    droop_ns: ns.every(n => n === ns[0]) ? ns[0] : andList(ns), droop_mvw_cards: pr(CARDS.map(c => 1 / CH.droop[c].slope), 1),
    fit_rms_a2: f(A2.rms_w, 2), fit_n_a2: num(A2.n, 0), fit_rmsd_a2: f(A2.rms_dram_w, 1), fit_nd_a2: num(A2.n_dram, 0),
    fit_rms_a3: f(A3.rms_w, 2), fit_n_a3: num(A3.n, 0), fit_rmsd: pr(CARDS.map(c => F[c].rms_dram_w), 1),
    fit_rmss: andList(CARDS.map(c => f(F[c].rms_w, 2))), fit_ns: ns.every(n => n === ns[0]) ? ns[0] : andList(ns),
    se_minion: pc(rel('minion')), se_dram: num(100 * Math.max(...rel('dram_pj_per_byte')), 0) + '%',
    se_noc_sram: pc(rel('noc').concat(rel('sram'))),
    minion_pct: pc(CARDS.map(c => F[c].coef.minion)), dram_pj: pr(CARDS.map(c => F[c].coef.dram_pj_per_byte), 0),
    idle_unsensed: rng(Math.round(Math.min(...CARDS.map(c => IU[c].w[0]))), Math.round(Math.max(...CARDS.map(c => IU[c].w[1]))), 0, 'W'),
    idle15: f(P.idle_73c.unsensed_w, 0),
    /* the host link on each card (E50, D.pcie), for the index row of "Over the PCIe link": ranges over the cards */
    ...(function () {
      const X = D.pcie || {per_card: {}}, rows = CK.cardsIn(X.per_card).map(c => X.per_card[c]), v = k => rows.map(r => r[k]);
      if (!rows.length) return {};
      const r1 = (k, dp) => pr(v(k), dp);
      return {pcie_h2d: r1('h2d_dma_gbs', 1), pcie_d2h: r1('d2h_dma_gbs', 1), pcie_staged: r1('h2d_staged_gbs', 1), pcie_link: f(X.link_gbs, 2),
        pcie_eff: pc(v('h2d_dma_gbs').map(g => g / X.link_gbs)), pcie_wait: r1('launch_wait_us', 0), pcie_queued: num(Math.round(v('launch_queued_us').reduce((a, b) => a + b, 0) / rows.length), 0),
        pcie_two: pr(v('two_h2d_over_one'), 2)};
    })(),
  };
})();
const fill = s => String(s == null ? '' : s).replace(/\{\{(\w+)\}\}/g, (m, k) => (k in TOK ? TOK[k] : m));

/* ---------- the glossary opens itself when the address asks for it ---------- */
(function () {
  const T = document.getElementById('terms');
  const open = () => { if (location.hash === '#terms') T.open = true; };
  open(); addEventListener('hashchange', open);
  document.querySelectorAll('a[href="#terms"]').forEach(a => a.addEventListener('click', () => { T.open = true; }));
})();

/* ---------- the reading paths: open on a wide screen, one tap each on a phone ---------- */
if (window.matchMedia('(max-width: 599px)').matches) {
  document.querySelectorAll('details.path').forEach(d => { d.open = false; });
  setHTML('paths-hint', 'tap a question to open its path');
} else setHTML('paths-hint', 'each a row of pages in reading order');

/* ---------- table of contents ---------- */
document.getElementById('toclist').innerHTML = [...document.querySelectorAll('h2[id]')]
  .map(h => `<li><a href="#${h.id}">${esc(h.textContent.replace(/^\d+\.\s*/, ''))}</a></li>`).join('');

/* ---------- the reports index: grouped by subject; 'what' may hold links, so it is inserted as HTML ---------- */
(function () {
  let group = null;
  const t = document.getElementById('reportstab');
  t.innerHTML = '<thead><tr><th style="width:18%">Report</th><th style="width:9%">When</th><th style="width:50%">What it established</th><th style="width:23%">Instruments</th></tr></thead><tbody>' +
    D.reports.map(r => { const g = r.group && r.group !== group ? `<tr class="grp"><td colspan="4"><b>${esc(r.group)}</b></td></tr>` : ''; if (r.group) group = r.group;
      return g + `<tr><td class="lvl"><a href="${r.url}">${esc(r.title)}</a></td><td class="small" data-sort="${esc(r.pub)}">${esc(r.date)}</td><td>${fill(r.what)}</td><td class="small">${esc(r.instruments)}</td></tr>`; }).join('') + '</tbody>';
  CK.stackTable(t);
  sortGrouped(t);  /* "When" sorts by the day a report was first published */
})();

/* ---------- the ladder: the time-resolution chart and the table share one filter ---------- */
const ladId = s => 'lad-' + s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
let LAD = null;
function goRow(level) {
  if (LAD) LAD.set('all');
  const tr = document.getElementById(ladId(level));
  if (!tr) return;
  const d = tr.querySelector('details'); if (d) d.open = true;
  tr.scrollIntoView({block: 'center', behavior: CK.reduced ? 'auto' : 'smooth'});
  tr.classList.add('flash'); setTimeout(() => tr.classList.remove('flash'), 1800);
}
const GRAN = (function () {
  const rows = D.ladder.filter(r => r.sec);
  const COL = {works_now: 'var(--ok)', needs_tooling: 'var(--warn)', needs_fw_change: 'var(--c1)', research_only: 'var(--muted)', impossible_on_silicon: 'var(--bad)'};
  const TK = [[1e-9, '1 ns'], [1e-8, '10 ns'], [1e-7, '100 ns'], [1e-6, '1 µs'], [1e-5, '10 µs'], [1e-4, '100 µs'], [1e-3, '1 ms'], [1e-2, '10 ms'], [1e-1, '100 ms'], [1, '1 s'], [10, '10 s']];
  const rowH = W => (W < 600 ? 40 : 22), T = 30, B = 48;
  let filter = 'all', groups = [], fr = null;
  function draw(f) {
    const W = f.W, nar = f.narrow, L = nar ? 10 : 250, R = 18, h = rowH(W), yEnd = T + rows.length * h;
    const x = CK.log(1e-9, 10, L, W - R), g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    TK.forEach(([v, s], i) => {
      CK.el('line', {x1: x(v), x2: x(v), y1: T - 4, y2: yEnd, class: 'grid-line'}, g0);
      if (!nar || i % 2 === 0) CK.txt(g0, x(v), yEnd + 16, s, 'tick', 'middle');
    });
    CK.txt(g0, (L + W - R) / 2, yEnd + 38, 'finest time step (log scale)', 'lab', 'middle');
    const xc = x(1 / 600e6);
    CK.el('line', {x1: xc, x2: xc, y1: T - 10, y2: yEnd, stroke: 'var(--axis)', 'stroke-dasharray': '3 3'}, g0);
    CK.txt(g0, xc + 4, T - 14, '1 cycle at 600 MHz', 'lab');
    groups = rows.map((r, i) => {
      const y0 = T + i * h, cy = nar ? y0 + 28 : y0 + h / 2;
      const g = CK.el('g', {class: 'gran-row', 'data-status': r.status}, f.svg);
      CK.el('rect', {x: 0, y: y0, width: W, height: h, class: 'ck-hit'}, g);
      if (nar) CK.txt(g, L, y0 + 14, r.level, 'lab'); else CK.txt(g, L - 8, cy + 4, r.level, 'lab', 'end');
      CK.el('line', {x1: L, x2: W - R, y1: cy, y2: cy, class: 'grid-line', opacity: 0.6}, g);
      const c = CK.el('circle', {cx: x(r.sec), cy, r: 6, stroke: 'var(--surface)', 'stroke-width': 2}, g);
      c.style.fill = COL[r.status];
      CK.tip(f, g, `<b>${esc(r.level)}</b><br>${esc(fill(r.gran))}<br>${chip(r.status)}<br><span class="small">Enter: its row in the table</span>`, {role: 'button'});
      return g;
    });
    CK.keynav(f, groups, {onEnter: (n, k) => { CK.hide(f); goRow(rows[k].level); }});
    dim();
  }
  function dim() { groups.forEach((g, i) => { g.style.opacity = filter === 'all' || rows[i].status === filter ? 1 : 0.15; }); }
  fr = CK.frame('gran', {height: W => T + rows.length * rowH(W) + B, minW: 300, maxW: 1288, label: 'Time resolution of each instrument', draw});
  document.getElementById('gran-leg').innerHTML = LADDER_STATUS.map(chip).join(' ') +
    ' <span class="small">· rows without a single time step (per-launch counts, whole-program traces, one-shot dumps, RTL simulation, per-shire attribution) are in the table only</span>';
  return {filter(k) { filter = k; dim(); }};
})();
LAD = (function () {
  let filter = 'all', all = false;
  const fbox = document.getElementById('filters'), t = document.getElementById('laddertab');
  const wide = window.matchMedia('(min-width: 600px)');
  const opts = [['all', 'all rows'], ['works_now', 'works now'], ['needs_tooling', 'needs tooling'], ['needs_fw_change', 'needs firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon']];
  function render() {
    fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('') +
      `<button type="button" id="notesall">${all ? 'collapse all notes' : 'expand all notes'}</button>`;
    fbox.querySelectorAll('button[data-k]').forEach(b => { b.onclick = () => { filter = b.dataset.k; render(); }; });
    document.getElementById('notesall').onclick = () => { all = !all; t.querySelectorAll('details.lnote').forEach(d => { d.open = all; }); document.getElementById('notesall').textContent = all ? 'collapse all notes' : 'expand all notes'; };
    const rows = D.ladder.filter(r => filter === 'all' || r.status === filter), open = wide.matches || all;
    t.innerHTML = '<thead><tr><th style="width:12%">Instrument</th><th style="width:32%">What it shows</th><th style="width:16%">Finest granularity</th><th style="width:15%">How</th><th style="width:9%">Who</th><th style="width:10%">Status</th><th style="width:6%">Check</th></tr></thead><tbody>' +
      rows.map(r => `<tr id="${ladId(r.level)}"><td class="lvl">${esc(r.level)}</td><td>${rk(esc(fill(r.what)))}` +
        (r.note ? `<details class="lnote"${open ? ' open' : ''}><summary>note</summary><div class="small">${rk(lk(esc(fill(r.note))))}</div></details>` : '') +
        `</td><td>${rk(esc(fill(r.gran)))}</td><td>${esc(r.instrument)}</td><td class="inl">${esc(r.access)}</td><td class="inl">${chip(r.status)}</td><td class="inl">${verif(r.check)}</td></tr>`).join('') + '</tbody>';
    CK.stackTable(t);
    GRAN.filter(filter);
  }
  const onWide = () => t.querySelectorAll('details.lnote').forEach(d => { d.open = wide.matches || all; });
  if (wide.addEventListener) wide.addEventListener('change', onWide);
  render();
  return {set(k) { if (filter !== k) { filter = k; render(); } }};
})();

/* ---------- how many identical events before the meter sees one? Two views of one chart: one row per event, on one
   scale of joules; and the energy-rate plane (energy across, rate up, so every diagonal is one power), which adds
   E48's configurations and E59's sparse parity from the energy_plane block. The rows stay the default on a phone. ---------- */
(function () {
  const E = D.energy_events, M = E.meter, FAM = E.families, EV = E.events, PL = D.energy_plane, W59 = PL.workloads;
  const famOf = Object.fromEntries(FAM.map(([k, l, c]) => [k, {l, c}]));
  const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹', sup = n => (n < 0 ? '⁻' : '') + String(Math.abs(n)).split('').map(d => SUP[+d]).join('');
  const sci = (v, sig) => { let e = Math.floor(Math.log10(v)), m = +(v / Math.pow(10, e)).toPrecision(sig); if (m >= 10) { m /= 10; e += 1; } return `${num(m, sig - 1)}×10${sup(e)}`; };
  const UNITS = [[1e-3, 'mJ'], [1e-6, 'µJ'], [1e-9, 'nJ'], [1e-12, 'pJ'], [1e-15, 'fJ'], [1e-18, 'aJ']];
  const J = (v, sig) => { const u = UNITS.find(([s]) => v >= s * 0.9995) || UNITS[UNITS.length - 1]; const x = v / u[0]; return (sig ? num(+x.toPrecision(sig)) : num(x)) + ' ' + u[1]; };
  const JR = (lo, hi) => { const u = UNITS.find(([s]) => lo >= s * 0.9995) || UNITS[UNITS.length - 1]; return rng(+(lo / u[0]).toPrecision(3), +(hi / u[0]).toPrecision(3), undefined, u[1]); };
  /* the plane also needs whole joules (a solve), rates from one a second up, and watts from milliwatts */
  const JJ = (v, sig) => (v >= 0.9995 ? (sig ? num(+v.toPrecision(sig)) : num(v)) + ' J' : J(v, sig));
  const RATE = v => (v < 1e4 ? num(v) : sci(v, 2));
  const WATT = v => (v < 0.9995 ? num(1e3 * v) + ' mW' : num(v) + ' W');
  const PREC = [0.5, 0.3, 0.2, 0.1, 0.06, 0.05, 0.03, 0.02];
  const ctl = document.getElementById('ev-ctl');
  const st = {view: (ctl.clientWidth || window.innerWidth) >= 700 ? 'plane' : 'rows', data: 'random', sigma: 0.2, prec: 0.06, sel: 'wire-free', psel: 'ev:wire-free', gs: false};
  const V = e => e.v[st.data] || e.v.any;
  const need = e => st.sigma / (st.prec * V(e).e[0]);
  const emin = e => st.sigma / (st.prec * V(e).rate);
  const seen = e => V(e).rate >= need(e);
  const thr = () => st.sigma / st.prec;  /* the lift, in W, that the meter prices to the precision asked */
  const read = CK.readout('ev-read');
  const box = n => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  /* the view's own title, caption, legend and note carry data-ev-view; the controls and the readout are shared */
  function showView() {
    document.querySelectorAll('[data-ev-view]').forEach(el => { const on = el.getAttribute('data-ev-view') === st.view; el.hidden = !on; el.style.display = on ? '' : 'none'; });
    /* the readout: under the plane, as under the other charts, so that a selection that changes its length does not
       move the plot under the pointer; above the long rows, beside the sliders whose count it gives */
    const rd = document.getElementById('ev-read'), ch = document.getElementById('ev');
    if (rd && ch) { if (st.view === 'plane') ch.after(rd); else ch.before(rd); }
  }
  CK.seg(box(), {label: 'View', options: [['rows', 'one row per event'], ['plane', 'energy × rate']], value: st.view, onChange: v => { st.view = v; showView(); upd(); }});
  CK.seg(box(), {label: 'Operands', options: [['random', 'random data'], ['zeros', 'zeros']], value: st.data, onChange: v => { st.data = v; upd(); }});
  CK.range(box(), {label: 'Baseline uncertainty σ', min: 0.01, max: 0.2, step: 0.01, value: st.sigma, fmt: v => num(v, 2) + ' W', onInput: v => { st.sigma = v; upd(); }});
  CK.range(box(), {label: 'Precision', stops: PREC, value: st.prec, fmt: v => '±' + num(100 * v, 0) + '%', onInput: v => { st.prec = v; upd(); }});
  const sb = box(); sb.className = 'sel';
  const lab = document.createElement('label'); lab.htmlFor = 'ev-select'; lab.textContent = 'Event';
  const sel = document.createElement('select'); sel.id = 'ev-select';
  sel.innerHTML = FAM.map(([k, l]) => `<optgroup label="${esc(l)}">` + EV.filter(e => e.family === k).map(e => `<option value="${e.id}">${esc(e.label)}</option>`).join('') + '</optgroup>').join('');
  sel.value = st.sel; sel.onchange = () => select(sel.value);
  sb.append(lab, sel);
  /* E48's configurations behind a box of their own, off at first (the plane is busy enough without them) */
  const gb = box(); gb.setAttribute('data-ev-view', 'plane');
  const gl = document.createElement('label'); gl.className = 'chk';
  const gi = document.createElement('input'); gi.type = 'checkbox'; gi.id = 'ev-gs'; gi.checked = st.gs;
  gi.addEventListener('change', () => { st.gs = gi.checked; legend(); upd(); });
  gl.append(gi, document.createTextNode(`E48's ${PL.gs.rows.length} gather, scatter and atomic configurations`));
  gb.appendChild(gl);
  /* an instruction's label starts with its mnemonic, which keeps its case */
  const title = e => { if (e.family === 'instr') { const m = e.label.match(/^(\S+)(.*)$/); return `<code>${esc(m[1])}</code>${esc(m[2])}`; } return esc(e.label[0].toUpperCase() + e.label.slice(1)); };
  const FLIPW = EV.filter(e => e.id.startsWith('flip-')).reduce((t, e) => t + V(e).e[0] * V(e).rate, 0);  /* the four flip rows share one burst */
  function describe(e) {
    const v = V(e), ok = seen(e), ratio = ok ? v.rate / need(e) : need(e) / v.rate, lift = v.rate * v.e[0], got = st.sigma / lift;
    const cards = Object.keys(v.cards || {}).length ? ` (${CK.cardsIn(v.cards).map(c => `${c} ${J(v.cards[c])}`).join(', ')})` : '';
    const range = v.e[1] < v.e[2] ? ` [${JR(v.e[1], v.e[2])}]` : '';
    const opnd = e.v.any ? '' : (st.data === 'random' ? ', random data' : ', zeros');
    return `<b>${title(e)}</b>${opnd}: ${J(v.e[0])}${range} per ${e.unit}${cards}. At ±${num(100 * st.prec, 0)}% against a ${num(st.sigma, 2)} W baseline it needs about ${sci(need(e), 1)} a second; ` +
      `the measurement ran it at ${sci(v.rate, 2)} a second (${num(lift, lift < 10 ? 1 : 0)} W), which that baseline prices to about ±${num(100 * got, got < 0.1 ? 1 : 0)}%, ` +
      `so at these settings the meter ${ok ? `sees it (${num(ratio, ratio < 10 ? 1 : 0)}× to spare)` : `does not see it (${num(ratio, ratio < 10 ? 1 : 0)}× short)`}. ` +
      (e.id.startsWith('flip-') ? `That rate is one fp32 matmul burst's, of about ${num(FLIPW, 0)} W with the four kinds of flip together, which the meter saw whole: a fit gives this flip its share, and the line judges the share. `
        : e.id.startsWith('wire-') ? `Its energy is the data part a fit gives the links' power over many bursts, and the line judges that part. ` : '') +
      `Source: <a href="${e.src.url}">${esc(e.src.label)}</a>${e.note ? `; ${esc(e.note)}` : ''}.`;
  }
  function select(id) { st.sel = id; st.psel = 'ev:' + id; sel.value = id; upd(true); }
  function pselect(id) { if (id.startsWith('ev:')) { select(id.slice(3)); return; } st.psel = id; upd(true); }

  /* ---- the plane's points: every event, E48's configurations when asked, E59's solve, candidate and multiply-add per
     size, and one minion's gathers. x is the energy per event (J), y the rate (per second), x·y the lift (W). ---- */
  const KINDS = [['mac', 'one executed int8 multiply-add', 'a multiply-add'], ['candidate', 'one candidate scored', 'a candidate'], ['solve', 'one whole solve', 'a solve']];
  const gsParts = r => { const [op, table, pat, data, h, m] = r[0].split('/'); return {op, table, pat, data, harts: +h.slice(1), mask: m.slice(1)}; };
  function points() {
    const out = EV.map(e => { const v = V(e); return {id: 'ev:' + e.id, kind: 'ev', e, x: v.e[0], lo: v.e[1], hi: v.e[2], y: v.rate, c: famOf[e.family].c}; });
    if (st.gs) PL.gs.rows.forEach((r, i) => out.push({id: 'gs:' + i, kind: 'gs', r, x: r[1], lo: r[2], hi: r[3], y: r[4]}));
    W59.sizes.forEach(s => KINDS.forEach(([k]) => out.push({id: `w:${s.id}:${k}`, kind: 'w', s, k, x: s.per[k][0], y: s.per[k][1]})));
    out.push({id: 'minion', kind: 'minion', x: PL.minion.e_j, y: PL.minion.per_s});
    return out;
  }
  const verdict = P => { const t = thr(), ok = P >= t, r = ok ? P / t : t / P; return ok ? `seen at these settings (${num(r, r < 10 ? 1 : 0)}× to spare)` : `not seen at these settings (${num(r, r < 10 ? 1 : 0)}× short)`; };
  function gsHtml(r) {
    const c = gsParts(r), P = r[1] * r[4], what = c.op === 'upd' ? esc(PL.gs.upd) : `<code>${esc(c.op)}</code>`;
    const bits = [esc(PL.gs.tables[c.table] || c.table), esc(PL.gs.patterns[c.pat] || c.pat), c.data === 'zeros' ? 'zeros' : 'random data'];
    if (c.harts !== 2) bits.push('one hart of each minion');
    if (c.mask !== 'ff') bits.push(`lanes 0x${esc(c.mask)}`);
    const only = (PL.gs.fewer_cards || {})[r[0]];
    return `<b>E48 · ${what}</b> (${bits.join('; ')}): ${J(r[1])} [${JR(r[2], r[3])}] per ${PL.gs.update_ops.includes(c.op) ? 'update' : 'element'} at ${RATE(r[4])} a second${only ? ` (on ${andList(only.map(esc))} only)` : ''}, a lift of ${WATT(P)}: ${verdict(P)}.`;
  }
  const sizeName = s => { const t = `(${s.size[0]}, ${s.size[1]}, η ${s.size[2]}, m ${num(s.size[3], 0)})`; return s.label.startsWith('(') ? t : `${esc(s.label)} ${t}`; };
  function wHtml(s, k) {
    const [e, r] = s.per[k], P = e * r, K = KINDS.find(x => x[0] === k);
    const what = k === 'solve' ? `${JJ(e, 3)} over idle at ${RATE(r)} solves a second`
      : `${JJ(e, 3)} at ${RATE(r)} a second (a solve's ${JJ(s.j_per_solve, 3)} over idle ÷ ${k === 'mac' ? `its ${num(s.ops, 0)} TensorIMA8A32 ops × ${num(W59.macs_per_op, 0)}` : `its ${num(s.candidates, 0)} candidates`})`;
    return `<b>Sparse parity ${sizeName(s)}, ${K[1]}</b> (E59 on ${esc(W59.card)}): ${what}, a lift of ${WATT(P)}: ${verdict(P)}. ` +
      `The same ${WATT(s.w)} is ${RATE(s.per.solve[1])} solves, ${RATE(s.per.candidate[1])} candidates or ${RATE(s.per.mac[1])} multiply-adds a second; the meter cannot tell which.` +
      (k === 'solve' ? '' : ` An average over the whole solve (row generation, the scan and its epilogue together), not ${K[2]} repeated alone.`);
  }
  function mHtml() {
    const m = PL.minion, P = m.e_j * m.per_s;
    return `<b>One minion's word gathers from its L1</b> (E48, <code>fgw.ps</code>, both harts): ${RATE(m.per_s)} elements a second measured on one minion, at the ${J(m.e_j, 3)} an element ` +
      `of the whole chip's run (${RATE(m.chip_per_s)} a second): ${WATT(P)}, under one reading's ${WATT(M.board_lsb_w)} step on the board, so ${verdict(P)}. ` +
      `One minion's own energy per element was not measured; this borrows the chip's.`;
  }
  const pHtml = p => (p.kind === 'ev' ? describe(p.e) : p.kind === 'gs' ? gsHtml(p.r) : p.kind === 'w' ? wHtml(p.s, p.k) : mHtml());
  const pShort = p => (p.kind === 'ev' ? p.e.label : p.kind === 'gs' ? `E48: ${gsParts(p.r).op}, ${PL.gs.tables[gsParts(p.r).table].split(':')[0]}`
    : p.kind === 'w' ? `${p.s.label}: ${KINDS.find(x => x[0] === p.k)[2]}` : "one minion's L1 gathers");
  function planeSum() {
    const lifts = EV.map(e => V(e).e[0] * V(e).rate), k = EV.filter(seen).length;
    let s = `At these settings (the line: σ ÷ precision = ${WATT(thr())}) the meter sees <b>${k} of ${EV.length}</b> events`;
    if (st.gs) s += ` and <b>${PL.gs.rows.filter(r => r[1] * r[4] >= thr()).length} of E48's ${PL.gs.rows.length}</b> configurations`;
    return s + `; the events come to ${rng(+Math.min(...lifts).toPrecision(3), +Math.max(...lifts).toPrecision(3), undefined, 'W')} over idle at the rates measured, the flips and the wires as a fit's shares of a larger burst. `;
  }
  function upd(keepFocus) {
    const k = EV.filter(seen).length, e = EV.find(x => x.id === st.sel);
    if (st.view === 'plane') { const ps = points(), p = ps.find(q => q.id === st.psel) || ps.find(q => q.id === 'ev:' + st.sel); read.set(planeSum() + pHtml(p)); }
    else read.set(`At these settings the meter sees <b>${k} of ${EV.length}</b> events. ` + describe(e));
    fr.redraw();
  }

  /* ---- the plane's legend (HTML, above the chart): the families' dots, then E59's diamond, the minion's square and
     E48's dot when shown; the lines are labelled on the chart ---- */
  const legHost = document.getElementById('ev-leg');
  function legend() {
    if (!legHost) return;
    const items = FAM.map(([k, l, c]) => ({key: k, label: l, color: c, mark: 'dot'}))
      .concat([{key: 'w', label: 'sparse parity (E59): a multiply-add, a candidate, a solve', color: 'var(--ink)', mark: 'diamond'},
        {key: 'minion', label: "one minion's L1 gathers (E48)", color: 'var(--ink)', mark: 'box'}]);
    if (st.gs) items.push({key: 'gs', label: "E48's configurations", color: 'color-mix(in srgb, var(--ref) 60%, var(--surface))', mark: 'dot'});
    CK.legend(legHost, items);
    const sw = legHost.querySelectorAll('.ck-li svg');
    const ms = sw[FAM.length + 1] && sw[FAM.length + 1].querySelector('rect');  /* the minion's square is hollow, as on the chart */
    if (ms) { ms.setAttribute('x', 5); ms.setAttribute('y', 1); ms.setAttribute('width', 8); ms.setAttribute('height', 8); ms.style.fill = 'var(--surface)'; ms.style.stroke = 'var(--ink)'; ms.style.strokeWidth = '1.5'; }
    const key = document.createElement('span'); key.className = 'ck-li'; key.textContent = 'filled: seen at these settings; hollow: not';
    legHost.appendChild(key);
  }

  /* ---- the plane's domain: whole decades around everything it can draw ---- */
  const PV = (function () {
    const xs = [PL.minion.e_j], ys = [PL.minion.per_s];
    EV.forEach(e => Object.values(e.v).forEach(v => { xs.push(v.e[0], v.e[1], v.e[2]); ys.push(v.rate); }));
    PL.gs.rows.forEach(r => { xs.push(r[2], r[3]); ys.push(r[4]); });
    W59.sizes.forEach(s => Object.values(s.per).forEach(([e, r]) => { xs.push(e); ys.push(r); }));
    const lo = a => Math.floor(Math.log10(Math.min(...a)) + 1e-9), hi = a => Math.ceil(Math.log10(Math.max(...a)) - 1e-9);
    return {x0: lo(xs), x1: hi(xs), y0: lo(ys), y1: hi(ys)};
  })();
  /* equal decades on both axes while the plot is no taller than 620 px, so a diagonal of one power runs at 45° on a phone */
  const pLay = W => { const nar = W < 600, L = nar ? 40 : 50, R = nar ? 10 : 16, T = 24, B = 42, pw = W - L - R;
    const ph = Math.round(Math.min(pw * (PV.y1 - PV.y0) / (PV.x1 - PV.x0), 620)); return {nar, L, R, T, B, pw, ph, H: T + ph + B}; };
  function drawPlane(f) {
    const W = f.W, G = pLay(W), {L, T, pw, ph, nar} = G, svg = f.svg, t = thr();
    const X0 = Math.pow(10, PV.x0), X1 = Math.pow(10, PV.x1), Y0 = Math.pow(10, PV.y0), Y1 = Math.pow(10, PV.y1);
    const x = CK.log(X0, X1, L, L + pw), y = CK.log(Y0, Y1, T + ph, T);
    /* a diagonal of power P inside the plot: it enters at the left or the top and leaves at the bottom or the right */
    const diag = P => { const xa = Math.max(X0, P / Y1), xb = Math.min(X1, P / Y0); return xa < xb ? {xa, xb, left: P / Y1 <= X0, bottom: P / Y0 <= X1} : null; };
    const g0 = CK.el('g', {'aria-hidden': 'true'}, svg);
    /* not seen: everything under σ ÷ precision */
    const d0 = diag(t);
    if (d0) {
      const pts = [[X0, Y0], d0.left ? [X0, t / X0] : [X0, Y1], ...(d0.left ? [] : [[d0.xa, Y1]]), [d0.xb, t / d0.xb], ...(d0.bottom ? [] : [[X1, Y0]])];
      const sh = CK.el('polygon', {points: pts.map(([a, b]) => `${x(a).toFixed(1)},${y(b).toFixed(1)}`).join(' ')}, g0);
      sh.style.fill = 'color-mix(in srgb, var(--ref) 13%, var(--surface))';
    }
    /* the grid every third decade, labelled; the frame's two axes */
    const xt = [], yt = [];
    for (let k = Math.ceil(PV.x0 / 3) * 3; k <= PV.x1; k += 3) xt.push(k);
    for (let k = Math.ceil(PV.y0 / 3) * 3; k <= PV.y1; k += 3) yt.push(k);
    const labs = [];
    xt.forEach(k => { const v = Math.pow(10, k); CK.el('line', {x1: x(v), x2: x(v), y1: T, y2: T + ph, class: 'grid-line'}, g0); labs.push(CK.txt(g0, x(v), T + ph + 16, JJ(v), 'tick', 'middle')); });
    yt.forEach(k => { const v = Math.pow(10, k); CK.el('line', {x1: L, x2: L + pw, y1: y(v), y2: y(v), class: 'grid-line'}, g0); labs.push(CK.txt(g0, L - 6, y(v) + 4, k === 0 ? '1' : '10' + sup(k), 'tick', 'end')); });
    CK.el('line', {x1: L, x2: L + pw, y1: T + ph, y2: T + ph, class: 'ck-axis'}, g0);
    CK.el('line', {x1: L, x2: L, y1: T, y2: T + ph, class: 'ck-axis'}, g0);
    labs.push(CK.txt(g0, L + pw / 2, G.H - 6, 'energy per event (log scale)', 'lab', 'middle'));
    labs.push(CK.txt(g0, 2, 12, 'events per second (log scale)', 'lab'));
    CK.inside(f, labs);
    /* the diagonals: faint every decade of watts; the meter's step (one reading, rail and board), σ, and σ ÷ precision */
    const LINES = [];
    for (let k = -1; k <= 2; k++) LINES.push({P: Math.pow(10, k), kind: 'faint', text: WATT(Math.pow(10, k))});
    LINES.push({P: M.rail_lsb_w, kind: 'step', text: nar ? `rail step ${WATT(M.rail_lsb_w)}` : `one reading's step, a rail: ${WATT(M.rail_lsb_w)}`});
    LINES.push({P: M.board_lsb_w, kind: 'step', pref: nar ? -7.5 : null, text: nar ? `board step ${WATT(M.board_lsb_w)}` : `one reading's step, the board: ${WATT(M.board_lsb_w)}`});
    LINES.push({P: st.sigma, kind: 'sigma', text: nar ? `σ ${num(st.sigma, 2)} W` : `σ, the baseline's uncertainty: ${num(st.sigma, 2)} W`});
    LINES.push({P: t, kind: 'thr', text: nar ? `seen above ${WATT(t)}` : `σ ÷ precision = ${WATT(t)}: seen above this line`});
    const STY = {faint: ['var(--ref)', 1, null, 0.55], step: ['var(--ink-2)', 1.3, '6 4', 1], sigma: ['var(--ink-2)', 1.5, '2 3', 1], thr: ['var(--ink)', 2.2, null, 1]};
    LINES.forEach(l => {
      const d = diag(l.P); l.d = d; if (!d) return;
      const s = STY[l.kind], ln = CK.el('line', {x1: x(d.xa), y1: y(l.P / d.xa), x2: x(d.xb), y2: y(l.P / d.xb), 'stroke-width': s[1]}, g0);
      ln.style.stroke = s[0]; ln.style.opacity = s[3]; if (s[2]) ln.setAttribute('stroke-dasharray', s[2]);
    });
    const pts = points().sort((a, b) => a.x - b.x || a.y - b.y);
    pts.forEach(p => { p.px = x(p.x); p.py = y(p.y); p.P = p.x * p.y; });
    /* the lines' labels run along them, just above, where they hit no point and no other label: every diagonal is
       parallel, so in coordinates along (u) and across (v) the line each label is a box at the line's own v */
    const dx = pw / (PV.x1 - PV.x0), dy = ph / (PV.y1 - PV.y0), ang = Math.atan2(dy, dx), ca = Math.cos(ang), sa = Math.sin(ang);
    const toUV = (px, py) => [px * ca + py * sa, -px * sa + py * ca];  /* u along the descending diagonal, v down across it */
    const taken = pts.map(p => { const [u, v] = toUV(p.px, p.py); return [u - 7, u + 7, v - 7, v + 7]; });
    const hit = (b) => taken.some(q => b[0] < q[1] && b[1] > q[0] && b[2] < q[3] && b[3] > q[2]);
    const inPlot = (px, py) => px >= L + 2 && px <= L + pw - 2 && py >= T + 2 && py <= T + ph - 2;
    const order = ['thr', 'sigma', 'step', 'faint'];
    /* the meter's lines are strips no other line's label may cross (a faint line may run under a label's halo) */
    const vOf = l => toUV(x(l.d.xa), y(l.P / l.d.xa))[1];
    const strips = LINES.filter(l => l.d && l.kind !== 'faint').map(l => { const v = vOf(l); return {l, b: [-1e5, 1e5, v - 2, v + 2]}; });
    const crosses = (b, l) => strips.some(s => s.l !== l && b[0] < s.b[1] && b[1] > s.b[0] && b[2] < s.b[3] && b[3] > s.b[2]);
    const halo = n => { n.style.paintOrder = 'stroke'; n.style.stroke = 'var(--surface)'; n.style.strokeWidth = '3px'; n.style.strokeLinejoin = 'round'; };
    /* a faint diagonal within 0.6 of a decade of a line of the meter's keeps no label (the two would touch). On a phone,
       where a decade is about 12 px across the lines, only σ ÷ precision is labelled on its line; σ and the two steps
       are named in a key in the empty corner below every line, and the faint lines keep no label */
    const covered = l => l.kind === 'faint' && LINES.some(m => m.kind !== 'faint' && Math.abs(Math.log10(m.P / l.P)) < 0.6);
    const onLine = l => l.d && !covered(l) && (!nar || l.kind === 'thr');
    LINES.filter(onLine).sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind)).forEach(l => {
      const tx = CK.txt(g0, -999, -999, l.text, l.kind === 'thr' ? 'lab-strong' : l.kind === 'faint' ? 'tick' : 'lab', 'middle');
      const w = tx.getComputedTextLength() || 6.5 * l.text.length, bh = (tx.getBBox && tx.getBBox().height) || 15;
      /* try centres along the line from the empty column of energies (no event between ~10⁻⁷ J and a solve), outward;
         a line of the meter's that finds no room clear of the other lines takes the first spot clear of marks and labels */
      const lx0 = Math.log10(l.d.xa), lx1 = Math.log10(l.d.xb), pref = Math.max(lx0, Math.min(lx1, l.pref == null ? -4.5 : l.pref));
      const cand = [];
      for (let s = 0; s <= (lx1 - lx0) * 4; s++) { cand.push(pref + s / 4, pref - s / 4); }
      for (const strict of l.kind === 'faint' ? [true] : [true, false]) {
        for (const lx of cand) {
          if (lx < lx0 || lx > lx1) continue;
          const cx = x(Math.pow(10, lx)), cy = y(l.P / Math.pow(10, lx)), [u, v] = toUV(cx, cy);
          const b = [u - w / 2 - 4, u + w / 2 + 4, v - 3 - bh - 1.5, v + 2];  /* the text sits 3 px above its line; its box from the line to its top, halo included */
          /* the box's four corners, back in the plot's coordinates */
          const corners = [[b[0], b[2]], [b[1], b[2]], [b[0], b[3]], [b[1], b[3]]].map(([uu, vv]) => [uu * ca - vv * sa, uu * sa + vv * ca]);
          if (!corners.every(([px, py]) => inPlot(px, py)) || hit(b) || (strict && crosses(b, l))) continue;
          taken.push(b);
          const ox = cx + 3 * sa, oy = cy - 3 * ca;
          tx.setAttribute('x', ox.toFixed(1)); tx.setAttribute('y', oy.toFixed(1));
          tx.setAttribute('transform', `rotate(${(ang * 180 / Math.PI).toFixed(2)} ${ox.toFixed(1)} ${oy.toFixed(1)})`);
          halo(tx);
          return;
        }
      }
      tx.remove();  /* a faint line keeps no label when there is no room for one */
    });
    if (nar) {
      /* the key: a short sample of each line's dash beside its name, bottom left, above the region's own name */
      const keyL = LINES.filter(l => l.d && (l.kind === 'sigma' || l.kind === 'step')).sort((a, b) => b.P - a.P);
      keyL.forEach((l, i) => {
        const yy = T + ph - 10 - 17 * (keyL.length - i), s = STY[l.kind];
        const ln = CK.el('line', {x1: L + 8, x2: L + 28, y1: yy - 4, y2: yy - 4, 'stroke-width': s[1]}, g0);
        ln.style.stroke = s[0]; if (s[2]) ln.setAttribute('stroke-dasharray', s[2]);
        halo(CK.txt(g0, L + 34, yy, l.text, 'lab', 'start'));
      });
    }
    /* the two regions, named where nothing is drawn */
    const ns = CK.txt(g0, L + 8, T + ph - 10, 'not seen at these settings', 'lab', 'start');
    const sn = CK.txt(g0, L + pw - 8, T + Math.round(0.4 * ph), 'seen', 'lab', 'end');
    [ns, sn].forEach(n => { n.style.paintOrder = 'stroke'; n.style.stroke = 'var(--surface)'; n.style.strokeWidth = '3px'; });
    /* the marks: E48 under everything, then E59's connectors, the events with their ranges, E59 and the minion */
    const sp = st.psel, nodes = [], list = [];
    const gC = CK.el('g', {}, svg), gW = CK.el('g', {}, svg), gE = CK.el('g', {}, svg), gT = CK.el('g', {}, svg);
    W59.sizes.forEach(s => {
      const q = KINDS.map(([k]) => pts.find(p => p.id === `w:${s.id}:${k}`)), on = sp.startsWith(`w:${s.id}:`);
      const ln = CK.el('polyline', {points: q.map(p => `${p.px.toFixed(1)},${p.py.toFixed(1)}`).join(' '), fill: 'none', 'stroke-width': on ? 1.6 : 1, 'aria-hidden': 'true'}, gW);
      ln.style.stroke = 'var(--ink-2)'; ln.style.opacity = on ? 0.9 : 0.5;
    });
    pts.forEach(p => {
      const ok = p.P >= t, host = p.kind === 'gs' ? gC : p.kind === 'ev' ? gE : gT, g = CK.el('g', {}, host);
      if (p.kind === 'gs') {
        const c = CK.el('circle', {cx: p.px, cy: p.py, r: nar ? 2.6 : 3}, g);
        c.style.fill = ok ? 'color-mix(in srgb, var(--ref) 60%, var(--surface))' : 'var(--surface)'; c.style.stroke = 'var(--ref)'; c.style.strokeWidth = ok ? '0.5' : '1';
      } else if (p.kind === 'ev') {
        if (p.lo < p.hi) { const w = CK.el('line', {x1: x(p.lo), x2: x(p.hi), y1: p.py, y2: p.py, 'stroke-width': 1.5}, g); w.style.stroke = p.c; }
        const c = CK.el('circle', {cx: p.px, cy: p.py, r: 4.5, 'stroke-width': 1.8}, g);
        c.style.stroke = p.c; c.style.fill = ok ? p.c : 'var(--surface)';
      } else if (p.kind === 'w') {
        const R = 6, d = CK.el('polygon', {points: `${p.px},${p.py - R} ${p.px + R},${p.py} ${p.px},${p.py + R} ${p.px - R},${p.py}`, 'stroke-width': 1.5}, g);
        d.style.stroke = 'var(--ink)'; d.style.fill = ok ? 'var(--ink)' : 'var(--surface)';
      } else {
        const r = CK.el('rect', {x: p.px - 4, y: p.py - 4, width: 8, height: 8, 'stroke-width': 1.5}, g);
        r.style.stroke = 'var(--ink)'; r.style.fill = ok ? 'var(--ink)' : 'var(--surface)';
      }
      CK.tip(f, g, () => pHtml(p).replace(/ Source: .*$/, ''), {role: 'button'});
      p.node = g; nodes.push(g); list.push(p);
    });
    /* the selected point: a ring, and its name beside it, wrapped to the room there: the first of right and up (where
       the power is higher and little is drawn), right and down, left and up, left and down whose text covers no other
       mark and stays in the plot; else the first that stays in the plot */
    const cur = pts.find(p => p.id === sp) || pts.find(p => p.id === 'ev:' + st.sel);
    if (cur) {
      const gs = CK.el('g', {'aria-hidden': 'true'}, svg), ring = CK.el('circle', {cx: cur.px, cy: cur.py, r: 9, fill: 'none', 'stroke-width': 2}, gs);
      ring.style.stroke = 'var(--ink)';
      const probe = CK.txt(gs, -999, -999, '', 'lab-strong'), wOf = str => { probe.textContent = str; return probe.getComputedTextLength() || 7 * str.length; };
      const wrap = room => { const lines = [];
        pShort(cur).split(' ').forEach(wd => { const t = lines.length ? lines[lines.length - 1] + ' ' + wd : wd; if (lines.length && wOf(t) > room) lines.push(wd); else if (lines.length) lines[lines.length - 1] = t; else lines.push(wd); });
        return lines; };
      const place = (right, up) => {
        const room = right ? L + pw - cur.px - 12 : cur.px - L - 12, lines = wrap(Math.max(room, 60)), wd = Math.max(...lines.map(wOf));
        const ys = lines.map((_, i) => (up ? cur.py - 12 - 14 * (lines.length - 1 - i) : cur.py + 24 + 14 * i));
        const bx = right ? [cur.px + 8, cur.px + 12 + wd] : [cur.px - 12 - wd, cur.px - 8], by = [ys[0] - 12, ys[ys.length - 1] + 4];
        const fits = room >= Math.min(wOf(pShort(cur)), 160) && bx[0] >= L && bx[1] <= L + pw && by[0] >= T - 4 && by[1] <= T + ph;
        const clear = !pts.some(p => p !== cur && p.px + 5 > bx[0] && p.px - 5 < bx[1] && p.py + 5 > by[0] && p.py - 5 < by[1]);
        return {right, lines, ys, fits, ok: fits && clear};
      };
      const tries = [[true, true], [true, false], [false, true], [false, false]].map(([r, u]) => place(r, u));
      const pick = tries.find(o => o.ok) || tries.find(o => o.fits) || tries[0];
      probe.remove();
      const lt = CK.txt(gs, 0, 0, '', 'lab-strong', pick.right ? 'start' : 'end');
      pick.lines.forEach((ln, i) => { const ts = CK.el('tspan', {x: pick.right ? cur.px + 10 : cur.px - 10, y: pick.ys[i]}, lt); ts.textContent = ln; });
      lt.style.paintOrder = 'stroke'; lt.style.stroke = 'var(--surface)'; lt.style.strokeWidth = '4px'; lt.style.strokeLinejoin = 'round';
    }
    /* hover and tap find the nearest point within 24 px, so a dot never has to be hit dead centre */
    const ov = CK.el('rect', {x: L - 8, y: T - 8, width: pw + 16, height: ph + 16, class: 'ck-hit', 'aria-hidden': 'true'}, svg);
    let at = null;
    const near = ev => { const b = svg.getBoundingClientRect(), mx = ev.clientX - b.left, my = ev.clientY - b.top; let best = null, bd = 24 * 24;
      pts.forEach(p => { const d2 = (p.px - mx) * (p.px - mx) + (p.py - my) * (p.py - my); if (d2 < bd) { bd = d2; best = p; } }); return best; };
    const fire = (node, type, ev) => node.dispatchEvent(new PointerEvent(type, {pointerType: ev.pointerType, clientX: ev.clientX, clientY: ev.clientY}));
    ov.addEventListener('pointermove', ev => { if (ev.pointerType === 'touch') return; const p = near(ev), n = p ? p.node : null;
      if (at && at !== n) fire(at, 'pointerleave', ev); at = n; ov.style.cursor = n ? 'pointer' : ''; if (n) fire(n, 'pointermove', ev); });
    ov.addEventListener('pointerleave', ev => { if (at) fire(at, 'pointerleave', ev); at = null; });
    ov.addEventListener('pointerdown', ev => { if (ev.pointerType !== 'touch') return; const p = near(ev); if (p) fire(p.node, 'pointerdown', ev); });
    ov.addEventListener('click', ev => { const p = near(ev); if (p && p.id !== st.psel) pselect(p.id); });
    CK.keynav(f, nodes, {onEnter: (n, k) => { if (list[k].id !== st.psel) pselect(list[k].id); }});
  }

  /* ---- the rows ---- */
  const T = 44, B = 40, hH = 24, NAR = W => W < 800, rH = W => (NAR(W) ? 30 : 19);  /* below 800 px each label gets its own line */
  const layout = W => { let y = T; const out = []; FAM.forEach(([k]) => { out.push({head: k, y}); y += hH; EV.filter(e => e.family === k).forEach(e => { out.push({e, y}); y += rH(W); }); }); return {rows: out, H: y + B}; };
  const TICKS = [[1e-17, '10 aJ'], [1e-16, '100 aJ'], [1e-15, '1 fJ'], [1e-14, '10 fJ'], [1e-13, '100 fJ'], [1e-12, '1 pJ'], [1e-11, '10 pJ'], [1e-10, '100 pJ'], [1e-9, '1 nJ'], [1e-8, '10 nJ'], [1e-7, '100 nJ'], [1e-6, '1 µJ'], [1e-5, '10 µJ'], [1e-4, '100 µJ'], [1e-3, '1 mJ'], [1e-2, '10 mJ']];
  function drawRows(f) {
    /* the label column is as wide as the longest label */
    const tw = str => { const t = CK.txt(f.svg, -999, -999, str, 'lab'), w = t.getComputedTextLength(); t.remove(); return w || str.length * 6.5; };
    const W = f.W, nar = NAR(W), L = nar ? 8 : Math.min(Math.round(0.45 * W), Math.ceil(Math.max(...EV.map(e => tw(e.label)))) + 16), R = 20, {rows, H} = layout(W), h = rH(W), yEnd = H - B;
    const x = CK.log(1e-17, 1e-2, L, W - R), lo = x.domain[0], hi = x.domain[1], cl = v => Math.max(lo, Math.min(hi, v));
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    const b0 = x(M.rail_lsb_w * M.pass_s), b1 = x(M.board_lsb_w * M.pass_s);
    const band = CK.el('rect', {x: b0, y: T - 6, width: b1 - b0, height: yEnd - T + 6}, g0);
    band.style.fill = 'color-mix(in srgb, var(--c4) 18%, var(--surface))';
    CK.txt(g0, b1, T - 30, `one reading on aifoundry2: ${J(M.rail_lsb_w * M.pass_s)} (rail)`, 'lab', 'end');
    CK.txt(g0, b1, T - 16, `to ${J(M.board_lsb_w * M.pass_s)} (board)`, 'lab', 'end');
    TICKS.forEach(([v, s], i) => {
      CK.el('line', {x1: x(v), x2: x(v), y1: T - 6, y2: yEnd, class: 'grid-line'}, g0);
      if (nar ? i % 3 === 2 : true) CK.txt(g0, x(v), yEnd + 16, s, 'tick', 'middle');
    });
    CK.txt(g0, (L + W - R) / 2, yEnd + 34, 'energy per event (log scale)', 'lab', 'middle');
    const nodes = [], list = [];
    rows.forEach(r => {
      if (r.head) { const x0 = nar ? L : 8; CK.el('circle', {cx: x0 + 5, cy: r.y + 12, r: 5, fill: famOf[r.head].c}, g0); CK.txt(g0, x0 + 15, r.y + 16, famOf[r.head].l, 'lab-strong'); return; }
      const e = r.e, v = V(e), c = famOf[e.family].c, cy = nar ? r.y + 21 : r.y + h / 2, ok = seen(e), active = e.id === st.sel;
      const g = CK.el('g', {class: 'ev-row'}, f.svg);
      const hit = CK.el('rect', {x: 0, y: r.y, width: W, height: h, class: 'ck-hit'}, g);
      if (active) { hit.setAttribute('class', ''); hit.style.fill = 'color-mix(in srgb, var(--c1) 9%, transparent)'; }
      if (nar) CK.txt(g, L, r.y + 11, e.label, 'lab'); else CK.txt(g, L - 8, cy + 4, e.label, 'lab', 'end');
      const xe = x(cl(v.e[0])), xm = x(cl(emin(e)));
      const conn = CK.el('line', {x1: xm, x2: xe, y1: cy, y2: cy, 'stroke-width': 1.2, 'stroke-dasharray': '2 3'}, g); conn.style.stroke = 'var(--ref)';
      const tk = CK.el('line', {x1: xm, x2: xm, y1: cy - 6, y2: cy + 6, 'stroke-width': 2}, g); tk.style.stroke = 'var(--ink-2)';
      if (v.e[1] < v.e[2]) { const w = CK.el('line', {x1: x(cl(v.e[1])), x2: x(cl(v.e[2])), y1: cy, y2: cy, 'stroke-width': 2}, g); w.style.stroke = c; }
      const d = CK.el('circle', {cx: xe, cy, r: 5, 'stroke-width': 2}, g);
      d.style.stroke = c; d.style.fill = ok ? c : 'var(--surface)';
      CK.tip(f, g, () => describe(e).replace(/Source: .*$/, ''), {role: 'button'});
      g.addEventListener('click', () => { if (st.sel !== e.id) select(e.id); });
      nodes.push(g); list.push(e);
    });
    CK.keynav(f, nodes, {onEnter: (n, k) => { if (st.sel !== list[k].id) select(list[k].id); }});
  }
  const fr = CK.frame('ev', {height: W => (st.view === 'plane' ? pLay(W).H : layout(W).H), minW: 300, maxW: 1288,
    label: 'Energy per event for a selection of the events the reports priced, against what the meter resolves: one row per event, or energy against rate', draw: f => (st.view === 'plane' ? drawPlane(f) : drawRows(f))});
  /* the defaults, stated once in the caption */
  const at = (id, data) => { const e = EV.find(x => x.id === id), v = e.v[data] || e.v.any; return [v.e[0], 0.2 / (0.06 * v.e[0])]; };
  const w1 = at('wire-free', 'random'), w2 = at('i-fmadd.ps', 'random');
  setHTML('ev-golden', `At the defaults (σ = 0.2 W, ±6%), one random bit carried 1 mm (${J(w1[0], 2)}) needs about ${sci(w1[1], 1)} a second and an fmadd.ps on random data (${J(w2[0], 2)}) about ${sci(w2[1], 1)}.`);
  const hot = EV.find(x => x.id === 's-contended').v.any;
  const ring = EV.find(x => x.id === 'm-xshire1');
  setHTML('ev-note', `σ defaults to 0.2 W, about the idle law's rms per idle sample (${num(M.idle_law_rms_w, 3)} W): the uncertainty of a baseline predicted from temperature. The hot line's contended atomic, about ${num(hot.e[0] * hot.rate, 1)} W over idle, carries a bar of ${sgn(100 * (hot.e[1] / hot.e[0] - 1), 0)}% to ${sgn(100 * (hot.e[2] / hot.e[0] - 1), 0)}%, about that size. ` +
    `The bars are the range over every pass on every card measured, so they include the difference between the cards ` +
    `(${esc(ring.label)}: ${sgn(100 * (ring.v.any.e[1] / ring.v.any.e[0] - 1), 0)}% to ${sgn(100 * (ring.v.any.e[2] / ring.v.any.e[0] - 1), 0)}%${Object.keys(ring.v.any.cards || {}).length > 1 ? `, with ${andList(CK.cardsIn(ring.v.any.cards).map(c => `${J(ring.v.any.cards[c])} on ${c}`))}` : ''}); the flips and the wires were priced by fits over many bursts. ` +
    `The band is one reading's step on aifoundry2, 1 mW on a rail and 10 mW on the board for one pass (§4.1); the rail's own average spreads a single event over about a second.`);
  /* the plane's caption and note: its numbers at the defaults (σ 0.2 W, ±6%, random operands where both ran) */
  {
    const vd = e => e.v.random || e.v.any, es = EV.map(e => vd(e).e[0]), lifts = EV.map(e => vd(e).e[0] * vd(e).rate), t0 = 0.2 / 0.06;
    const un = EV.filter(e => vd(e).e[0] * vd(e).rate < t0).map(e => vd(e).e[0] * vd(e).rate);
    const gl = PL.gs.rows.map(r => r[1] * r[4]), ge = PL.gs.rows.map(r => r[1]), gun = PL.gs.rows.filter(r => r[1] * r[4] < t0);
    const wid = PL.gs.rows.reduce((b, r) => (r[3] / r[2] > b[3] / b[2] ? r : b)), fewer = Object.entries(PL.gs.fewer_cards || {});
    const l1 = W59.sizes[0], mw = PL.minion.e_j * PL.minion.per_s, r3w = v => +v.toPrecision(3);
    const flips = EV.filter(e => e.id.startsWith('flip-')), flipW = flips.reduce((s, e) => s + vd(e).e[0] * vd(e).rate, 0);
    setHTML('ev-plane-cap', `The ${EV.length} events span ${num(Math.log10(Math.max(...es) / Math.min(...es)), 1)} decades of energy, ${J(Math.min(...es))} to ${J(Math.max(...es))}, ` +
      `yet each, at the rate its measurement ran it, comes to ${rng(r3w(Math.min(...lifts)), r3w(Math.max(...lifts)), undefined, 'W')} over idle (for the ${flips.length} flip rows, the shares a fit gives one fp32 matmul burst of about ${num(flipW, 0)} W, which the meter saw whole; for the wires, the fitted data part of a link's power); ` +
      `at the defaults ${EV.length - un.length} are seen, the ${un.length} hollow ones at ${rng(r3w(Math.min(...un)), r3w(Math.max(...un)), undefined, 'W')}. ` +
      `The meter's own step, ${WATT(M.rail_lsb_w)} on a rail and ${WATT(M.board_lsb_w)} on the board (dashed), lies ${num(Math.log10(t0 / M.board_lsb_w), 1)}–${num(Math.log10(t0 / M.rail_lsb_w), 1)} decades under the line that limits pricing at the defaults. ` +
      `Sparse parity's diamonds share one diagonal per size: on size ${sizeName(l1)} the same ${WATT(l1.w)} is ${RATE(l1.per.solve[1])} solves or ${RATE(l1.per.mac[1])} multiply-adds a second, and the meter cannot tell which.`);
    setHTML('ev-plane-note', `Each event sits at its energy and at its rate, ${esc(E.rate_rule)}; energy × rate is then the power a burst of them adds to the board, and ` +
      `the bars are each energy's range, as in the rows. The diagonals are powers: faint every decade of watts, dashed one reading's step (${WATT(M.rail_lsb_w)} on a rail, ${WATT(M.board_lsb_w)} on the board) and the baseline's σ, bold σ ÷ precision, which follows the sliders. ` +
      `E48's ${PL.gs.rows.length} configurations (the box above the chart shows them) are every chip-wide gather, scatter and atomic run with an energy, pooled over three passes on each of three cards` +
      (fewer.length ? ` (${andList(fewer.map(([k, c]) => { const g = gsParts([k]); return `<code>${esc(g.op)}</code> from ${esc((PL.gs.tables[g.table] || g.table).split(': ').pop().replace(/ \(.*\)$/, ''))} on ${andList(c.map(esc))} alone`; }))}, the other cards' bursts of it dropped by E48's clock rule)` : '') + ': ' +
      `they span ${num(Math.max(...ge) / Math.min(...ge), 0)}× in energy at ${rng(r3w(Math.min(...gl)), r3w(Math.max(...gl)), undefined, 'W')}` +
      (gun.length === 1 ? `, and the only one under the line at the defaults, <code>${esc(gsParts(gun[0]).op)}</code> on ${esc(PL.gs.tables[gsParts(gun[0]).table])} at ${WATT(gun[0][1] * gun[0][4])}, ` +
        (gun[0] === wid ? `also has the widest range of them all (${JR(gun[0][2], gun[0][3])} over passes and cards). ` : `has a range of ${JR(gun[0][2], gun[0][3])}. `)
        : `, ${gun.length} of them under the line at the defaults. `) +
      `Sparse parity (E59, ${esc(W59.card)}, one run per size) is a solve's board joules over idle and its solve rate, divided by the candidates it scores or by its TensorIMA8A32 ops × ${num(W59.macs_per_op, 0)} multiply-adds (16 × 16 × 64 each, padding included), so its points are averages over the whole solve. ` +
      `One minion's word gathers from its L1 take E48's single-minion rate (${RATE(PL.minion.per_s)} a second, both harts, measured) and the chip's ${J(PL.minion.e_j, 3)} an element (borrowed): ${WATT(mw)}, timed to the cycle yet under even the board's step. Data: <code>energy_events</code> and <code>energy_plane</code> in the page's data, written by <code>tools/ettelem/sync_hub_data.py</code> from <code>manual.json</code> and each E59 run's <code>energy.json</code>.`);
  }
  showView(); legend(); upd();
})();

/* ---------- contrast ---------- */
(function () {
  const t = document.getElementById('contrast');
  t.innerHTML = '<thead><tr><th>Topic</th><th>ET-SoC-1</th><th>A100/H100</th><th>Sources</th></tr></thead><tbody>' +
    D.contrast.map(c => `<tr><td class="lvl">${esc(c.topic)}</td><td>${esc(c.et)}</td><td>${esc(c.gpu)}</td><td class="small">${esc(c.src)}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
})();

/* ---------- power: the chain, the remainder, the sensors ---------- */
const CLS = [['instr', 'instructions', 'var(--c1)'], ['wire', 'mesh wires', 'var(--c2)'], ['onchip', 'other on-chip moves', 'var(--c3)'],
  ['dram', 'DRAM loads, stores, rows', 'var(--c4)'], ['st', 'stores through the L1', 'var(--c5)']];
const CLC = Object.fromEntries(CLS.map(c => [c[0], c[2]]));
const klass = cfg => (cfg.startsWith('st_stream/') ? 'st' : movesDram(cfg) ? 'dram' : /\/h\d$/.test(cfg) ? 'instr' : cfg.startsWith('wire/') ? 'wire' : 'onchip');
function solve4(A, b) {  /* Gaussian elimination with partial pivoting on a copy */
  const n = b.length, M = A.map((r, i) => [...r, b[i]]);
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = c + 1; r < n; r++) { const k = M[r][c] / M[c][c]; for (let j = c; j <= n; j++) M[r][j] -= k * M[c][j]; }
  }
  const x = new Array(n).fill(0);
  for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let j = r + 1; j < n; j++) s -= M[r][j] * x[j]; x[r] = s / M[r][r]; }
  return x;
}
/* Each card's configurations as the fit sees them; the refit counts st_stream's bytes twice (the line read). The
   V1 chart offers every card in power.per_config (the text above it stays on CARDS); a card with no published fit
   gets the same least-squares fit here, from its own rows. */
const V1CARDS = CK.cardsIn(Object.keys(P.per_config).filter(k => k !== 'fields' && Array.isArray(P.per_config[k]) && Array.isArray(P.per_config[k][0])));  /* its keys: 'fields', then one list of rows per card */
const PC = Object.fromEntries(V1CARDS.map(c => [c, P.per_config[c].map(r => ({cfg: r[0], over: r[1], mi: r[2], sr: r[3], no: r[4], g: r[5],
  un: r[1] - r[2] - r[3] - r[4], k: klass(r[0]), rnd: r[0].includes('/random')}))]));
function fitOf(card, line) {
  const R = PC[card], dram = r => r.g * 1e-3 * (line && r.k === 'st' ? 2 : 1);
  let coef;
  if (!line && P.fit[card]) { const c = P.fit[card].coef; coef = [c.minion, c.sram, c.noc, c.dram_pj_per_byte]; } else {
    const X = R.map(r => [r.mi, r.sr, r.no, dram(r)]), A = [0, 1, 2, 3].map(i => [0, 1, 2, 3].map(j => X.reduce((s, x) => s + x[i] * x[j], 0)));
    coef = solve4(A, [0, 1, 2, 3].map(i => X.reduce((s, x, n) => s + x[i] * R[n].un, 0)));
  }
  const pts = R.map(r => { const loss = coef[0] * r.mi + coef[1] * r.sr + coef[2] * r.no, dr = coef[3] * dram(r); return {...r, loss, dr, fit: loss + dr, res: r.un - loss - dr}; });
  const rms = a => Math.sqrt(a.reduce((s, p) => s + p.res * p.res, 0) / a.length), D_ = pts.filter(p => p.g > 0);
  return {coef, pts, rms: rms(pts), rmsd: rms(D_), n: pts.length, nd: D_.length};
}
(function () {
  const I = P.idle_73c, F = P.fit, Dp = P.droop, RF = P.rail_filter, SA = P.sampler, IU = P.idle_unsensed, CH = P.checks;
  setHTML('norails', esc(P.rails_no_telemetry.join(', ')));
  setHTML('rf-fall', andList(CARDS.map((c, i) => (i ? `${pct(RF[c].frac_1s)} and ${pct(RF[c].frac_2s)}` : `${pct(RF[c].frac_1s)} of the way after one second and ${pct(RF[c].frac_2s)} after two`) +
    ` on ${c} (τ ≈ ${f(RF[c].tau_s, 2)} s)`)) + ` (the median over ${andList(CARDS.map(c => num(RF[c].n, 0)))} bursts of the energy manual's catalogue, in that order)`);
  /* the s <-> s+16 ring: the medians of the passes it starved, per campaign and card (power.sampler.ring.per_card) */
  const RG = SA.ring, RV3 = (RG.per_card || {}).v3 || {}, R23 = (RG.per_card || {})['23sep'] || {}, rv3 = CK.cardsIn(RV3), r23 = CK.cardsIn(R23);
  setHTML('ring-ms', `${rng(...mm(RG.median_ms), 0, 'ms')} (the median in each pass it starved: ` +
    andList([...rv3.map(c => `${rng(...mm(RV3[c]), 0)} ms on ${c}`)].concat(r23.map(c => `${rng(...mm(R23[c]), 0)} ms on ${c} on 23 September`))) + ')');
  const fb = RG.fallback_23sep, nv3 = RG.v3_passes_per_card || {};
  setHTML('ring-v3', rv3.length ? `In the version-3 campaign's reruns the ring starved the sampler on ${rv3.length === CARDS.length ? `all ${WORD[rv3.length]} cards` : andList(rv3)}, ` +
    `in ${rv3.every(c => RV3[c].length === nv3[c]) ? `every pass (${andList([...new Set(rv3.map(c => word(nv3[c])))])} on each card)` : andList(rv3.map(c => `${word(RV3[c].length)} of ${word(nv3[c])} passes on ${c}`))}` +
    (fb ? `, so the energy manual keeps ${andList(fb.cards)}'s passes of 23 September for it.` : '.') : '');
  /* DRAM reads: per card, the sampler's median latency over the DRAM-read bursts against every other burst */
  setHTML('sampler-dram', `DRAM reads slow it too: over a burst of tensor loads or row walks from DRAM the median sample takes up to ` +
    andList(CARDS.map((c, i) => `${num(SA[c].read_median_ms[1], 0)}${i ? '' : ' ms'} on ${c}`)) +
    `, against ${rng(...mm(CARDS.flatMap(c => SA[c].other_median_ms)), 0, 'ms')} in every other burst; the catalogue keeps those bursts.`);
  setHTML('idle-unsensed', `${f(I.unsensed_w, 1)} W of the ${f(I.board_w, 1)} W the board draws at ${num(I.die_c, 0)} °C on aifoundry2 (one 60 s window), about half`);
  /* the other cards' idle over the catalogue's idle gaps, with the share as a plain fraction */
  setHTML('idle-unsensed-a3', 'Over the catalogue\'s idle gaps it is about ' + andList(CARDS.slice(1).map(c => { const u = IU[c], sh = (u.w[0] / u.board_w[0] + u.w[1] / u.board_w[1]) / 2;
    return `${fracWord(sh)} on ${c} (${rng(...u.w, 1, 'W')} of ${rng(...u.board_w, 1, 'W')} at ${rng(...u.die_c, 0, '°C')})`; })) + '.');
  const nsF = CARDS.map(c => F[c].n);
  setHTML('fit-n', nsF.every(n => n === nsF[0]) ? `${num(nsF[0], 0)} configurations` : andList(CARDS.map((c, i) => `${num(nsF[i], 0)} configurations on ${c}`)));

  /* the fit table and the text under it */
  const hosts = CARDS;
  document.getElementById('fittab').innerHTML = '<thead><tr><th>unmetered W of a configuration =</th>' + hosts.map(h => `<th class="num">${h}</th>`).join('') + '</tr></thead><tbody>' +
    [['× minion-rail W', 'minion', 3, ''], ['× SRAM-rail W', 'sram', 3, ''], ['× NoC-rail W', 'noc', 3, ''], ['pJ per DRAM byte', 'dram_pj_per_byte', 1, ' pJ/B']].map(r =>
      `<tr><td>${r[0]}</td>` + hosts.map(h => `<td class="num">${f(F[h].coef[r[1]], r[2])} ± ${f(CH.fit[h].se_hc3[r[1]], r[2])}${r[3]}</td>`).join('') + '</tr>').join('') +
    '<tr><td class="small">residual rms, configuration means</td>' + hosts.map(h => `<td class="num small">${f(F[h].rms_w)} W, n = ${F[h].n}</td>`).join('') + '</tr></tbody>';
  CK.stackTable(document.getElementById('fittab'));  /* one card per term on a phone, each card's value labelled */
  const fit = Object.fromEntries(V1CARDS.map(c => [c, fitOf(c, false)])), refit = Object.fromEntries(V1CARDS.map(c => [c, fitOf(c, true)]));
  const all = CARDS.flatMap(c => fit[c].pts), full = p => /^(tload|tstore)\/dram\/|^dramrow\/stride1K\//.test(p.cfg);
  const cm = k => CARDS.map(c => F[c].coef[k]), dif = a => 100 * (Math.max(...a) / Math.min(...a) - 1);
  const quarter = CARDS.map(c => { const d = fit[c].pts.filter(p => p.g > 0); return fit[c].rmsd / (d.reduce((s, p) => s + p.un, 0) / d.length); });
  const stR = all.filter(p => p.k === 'st').map(p => p.res), rR = all.filter(p => full(p) && p.rnd).map(p => p.res), zR = all.filter(p => full(p) && !p.rnd).map(p => -p.res);
  /* the minion coefficient: the cards within 10% of the reference card's form its group; any other card is set apart,
     with its SRAM coefficient beside the group's (on aifoundry1-c1 the fit moves the loss from the minion rail to the SRAM one) */
  const mc = c => F[c].coef.minion, grp = CARDS.filter(c => Math.abs(mc(c) / mc(CARDS[0]) - 1) <= 0.1), apart = CARDS.filter(c => !grp.includes(c));
  const gm = grp.reduce((a, c) => a + mc(c), 0) / grp.length, gs = grp.map(c => F[c].coef.sram);
  const dramAgree = (() => { const se = CARDS.map(c => CH.fit[c].se_hc3.dram_pj_per_byte), v = cm('dram_pj_per_byte');
    return CARDS.every((c, i) => CARDS.every((d, j) => Math.abs(v[i] - v[j]) <= 2.58 * Math.hypot(se[i], se[j]))); })();
  const cmp = (a, b) => (a >= 0 ? `${sgn(a, 1).slice(1)} W above` : `${f(-a, 1)} W below`);
  const posR = rR.filter(v => v > 0), posZ = zR.filter(v => v > 0);
  setHTML('fittext', `Four coefficients, no intercept, fitted per card to the mean of each configuration's three passes (${nsF.every(n => n === nsF[0]) ? `${num(nsF[0], 0)} configurations on each of ${andList(CARDS)}` : andList(CARDS.map((c, i) => `${num(nsF[i], 0)} configurations on ${c}`))}), ` +
    `on bursts of ${rng(...mm(all.map(p => p.over)), 1)} W over idle. DRAM bytes are the bytes the DRAM load, store and row configurations move; stores through the L1 (<code>st_stream</code>) count only the bytes written, not the line read before each write. ` +
    `Each ± is one standard error, robust to the larger scatter of the DRAM configurations. ` +
    `The minion coefficient is pinned to ${TOK.se_minion} (one standard error) on each card. ${grp.length > 1 ? `On ${andList(grp)} it differs by ${num(dif(grp.map(mc)), 0)}%, about the cards' spread elsewhere in the manual` : ''}` +
    (apart.length ? `${grp.length > 1 ? '; ' : ''}${andList(apart)}'s is ${andList(apart.map(c => f(mc(c), 2)))}, about ${fracWord(apart.reduce((a, c) => a + mc(c), 0) / apart.length / gm)} of that, and there the fit puts ${andList(apart.map(c => f(F[c].coef.sram, 2)))} on the SRAM rail against ${rng(...mm(gs), 2)}: ` +
      `its unmetered power follows the SRAM rail more than the minion rail, for a reason not measured (that card runs the older firmware and a higher SRAM rail voltage: <a href="${PAGES}et-soc1-energy-manual#two-cards">the energy manual, §8</a>). ` : '. ') +
    `The DRAM terms ${dramAgree ? 'agree within their errors' : 'differ'} (${andList(cm('dram_pj_per_byte').map(v => f(v, 1)))} pJ/B, ${(() => { const s = CARDS.map(c => num(CH.fit[c].se_hc3.dram_pj_per_byte, 0)); return s.every(x => x === s[0]) ? `each ±${s[0]}` : andList(s.map(x => '±' + x)); })()}). ` +
    `The SRAM and NoC coefficients are collinear with each other (not with the minion one) and uncertain to ${TOK.se_noc_sram}` +
    (() => { const z = CARDS.filter(c => CH.fit[c].pass_ci99.sram[0] <= 0), np = [...new Set(z.map(c => word(CH.fit[c].pass_coef.sram.length)))];
      return z.length ? `; the SRAM one is not distinguishable from zero on ${andList(z)}, whose ${np.length === 1 ? np[0] + ' ' : ''}passes fit it at ${andList(z.map(c => rng(...mm(CH.fit[c].pass_coef.sram), 2)))}` : ''; })() +
    `. The residual is small overall but not on DRAM traffic: ${rng(...mm(CARDS.map(c => fit[c].rmsd)), 1)} W rms on the DRAM configurations, ` +
    `about ${fracWord(quarter.reduce((a, b) => a + b, 0) / quarter.length)} of their unmetered power (${andList(quarter.map(q => pct(q)))}). It has a pattern: the three stores through the L1 sit ${rng(...mm(stR), 1)} W above the fit on every card, because their line reads are not counted ` +
    `(counting them brings the DRAM rms to ${rng(...mm(CARDS.map(c => refit[c].rmsd)), 2)} W: the checkbox in the chart below); on the full-rate tensor loads, tensor stores and row walks, random data sits ` +
    (posR.length === rR.length ? `${rng(...mm(rR), 1)} W above it` : `above it in ${word(posR.length)} of the ${word(rR.length)} configurations on the ${WORD[CARDS.length]} cards (up to ${f(Math.max(...rR), 1)} W; the other ${cmp(Math.min(...rR))})`) +
    ` and zeros or constants ` + (posZ.length === zR.length ? `${rng(...mm(zR), 1)} W below.` : `below it in ${posZ.length} of ${zR.length}.`));

  /* 'three things follow', from the per-configuration rows (the full-rate DRAM configurations; st_stream apart) */
  const off = all.filter(p => p.g > 0 && full(p)).map(p => ({...p, pj: (p.un - p.loss) / (p.g * 1e-3), tot: p.over / (p.g * 1e-3)}));
  const offSt = all.filter(p => p.k === 'st').map(p => (p.un - p.loss) / (p.g * 1e-3));
  const zc = off.filter(p => !p.rnd), rd = off.filter(p => p.rnd), tl = off.filter(p => p.cfg.startsWith('tload/dram/') && !p.cfg.endsWith('const'));
  const gmm = grp.map(mc), perPct = 100 * (1 + mc(CARDS[0])) * (1 / 0.99 - 1), scale = 100 * (1 - (1 + Math.min(...gmm)) / (1 + Math.max(...gmm)));
  const r0 = v => Math.round(v);
  setHTML('three-things', `<b>Three things follow.</b> <b>An instruction's unmetered energy is consistent with a regulator's delivery loss</b>: ` +
    `${perCard(CARDS.map(c => pct(mc(c))), '')} of what the minion rail delivers goes missing between the 12 V input and the core, ` +
    `as far as the rails' own meters can be trusted: the figure rests on their gain and on the correction for their one-second average, and each 1% in either moves it by about ${num(perPct, 1)} points ` +
    `(${grp.length > 1 ? `a ${num(scale, 1)}% difference in rail scale would explain the ${num(dif(gmm), 0)}% between ${andList(grp)}` : ''}${apart.length ? `${grp.length > 1 ? '; ' : ''}${andList(apart)}'s smaller figure goes with the SRAM coefficient above` : ''}; ` +
    `the mesh rail's gain is not checked either, <a href="${PAGES}et-soc1-heat-per-mm#limits">Heat per millimetre, §10</a>). Nothing else moves. ` +
    `<b>A DRAM byte's unmetered energy is the memory's</b>: the fitted ${TOK.dram_pj} pJ per byte, off the rails, in the DDR PHY, the I/O rail and the DRAM chips (${rng(...mm(zc.map(p => r0(p.pj))), 0)} on zeros and constants, ` +
    `${rng(...mm(rd.map(p => r0(p.pj))), 0)} on random data, per configuration), on top of the ${rng(...mm(off.map(p => r0(p.tot - p.pj))), 0)} pJ the mesh, the SRAM, the cores (a few pJ either way) and the delivery losses take on the way: ` +
    `together ${rng(...mm(tl.map(p => r0(p.tot))), 0)} pJ per byte for tensor loads from DRAM, zeros to random data. A byte written through the L1 costs about twice that off-rail (${rng(...mm(offSt.map(r0)), 0)} pJ), ` +
    `because the line is read from DRAM before it is written. <b>And the NoC coefficient is not all regulator</b>: ${rng(...mm(cm('noc').map(v => r0(100 * v))), 0)}% is more than a delivery loss would take; ` +
    `the likely rest, not measured, is the memory shires' own logic, on an unmetered rail, which works whenever the mesh moves bytes to them.`);

  /* §5's paragraph */
  const dUn = all.filter(p => full(p) || p.k === 'st').map(p => p.un), c2 = F.aifoundry2.coef;
  const w0 = a => rng(Math.round(a[0]), Math.round(a[1]), 0, 'W');
  setHTML('unmet-today', `${f(I.unsensed_w, 0)} W of a ${f(I.board_w, 0)} W idle on aifoundry2 (${andList(CARDS.slice(1).map(c => `${w0(IU[c].w)} of ${w0(IU[c].board_w)} on ${c}`))}) and ${rng(...mm(dUn), 1)} W of a full-rate DRAM workload are on no meter`);
  setHTML('idle15b', rng(Math.round(Math.min(...CARDS.map(c => IU[c].w[0]))), Math.round(Math.max(...CARDS.map(c => IU[c].w[1]))), 0));
  setHTML('idle-nometer', `about ${f(I.unsensed_w - (c2.minion * I.minion_w + c2.sram * I.sram_w + c2.noc * I.noc_w), 0)} W of aifoundry2's idle at ${num(I.die_c, 0)} °C, ` +
    `if the loss fractions fitted above idle also hold for the rails' idle power (an assumption)`);

  /* ---------- V1: where a workload's watts go ---------- */
  const shareV = (c, k) => med(fit[c].pts.filter(p => k(p)).map(p => p.un / p.over)), share = (c, k) => pct(shareV(c, k));
  setHTML('v1-cap', `Of what each configuration adds above idle, how much is on no meter, and does the four-term fit account for it? The scatter: every catalogue configuration's unmetered watts ` +
    `(board over idle less the three rails) against what the fit gives it; filled dots ran on random data, open ones on zeros or constants. The first bar: the idle card at ${num(I.die_c, 0)} °C on aifoundry2, ${f(I.unsensed_w, 1)} W of it on no meter, ` +
    `which cannot be split further. The second bar: the chosen configuration's watts over idle, the three rails and then the fit's delivery loss and DRAM term, with the measured total as a tick. ` +
    `Above idle, ${(() => { const ins = CARDS.map(c => shareV(c, p => p.k === 'instr')), w = [...new Set(ins.slice().sort((a, b) => b - a).map(fracWord))];
      return `${w.length === 1 ? `about ${w[0]}` : `between ${w[w.length - 1]} and ${w[0]}`} of an instruction's watts are on no meter (median ${perCard(ins.map(v => pct(v)), '')})`; })()} ` +
    `and about ${fracWord(med(CARDS.map(c => shareV(c, p => p.g > 0))))} of DRAM traffic's (${andList(CARDS.map(c => share(c, p => p.g > 0)))}). Hover, tap or tab to a point to break it down; arrows step through the points in residual order.`);
  const st = {card: V1CARDS[0], line: false, on: new Set(CLS.map(c => c[0])), sel: 'tload/dram/random'};
  const ctl = document.getElementById('v1-ctl'), box = () => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.cardSeg(box(), {cards: V1CARDS, value: st.card, onChange: v => { st.card = v; fr.redraw(); out(); }});
  const cb = box(); cb.innerHTML = '<label class="chk"><input type="checkbox" id="v1-line"> Count the line read before each L1 store</label>';
  document.getElementById('v1-line').addEventListener('change', ev => { st.line = ev.target.checked; fr.redraw(); out(); });
  const legHost = document.getElementById('v1-leg'), l1 = document.createElement('div');
  legHost.append(l1);
  CK.legend(l1, CLS.map(([k, l, c]) => ({key: k, label: l, mark: 'dot', color: c})), {toggle: true, onChange: keys => { st.on = new Set(keys); fr.redraw(); }});
  /* the bars' colours as in #sj below: the rails light at idle, full colour for what a configuration adds over idle */
  const tintV = c => `color-mix(in srgb, ${c} 38%, var(--surface))`;
  const SEG = [['mi', 'minion', 'var(--c1)'], ['sr', 'SRAM', 'var(--c3)'], ['no', 'NoC', 'var(--c2)'], ['loss', 'delivery loss (fit)', 'var(--c7)'],
    ['dr', 'DRAM term (fit)', 'var(--c4)'], ['imi', 'minion', tintV('var(--c1)')], ['isr', 'SRAM', tintV('var(--c3)')], ['ino', 'NoC', tintV('var(--c2)')],
    ['none', 'no meter', 'color-mix(in srgb, var(--ref) 45%, var(--surface))']];
  const segItem = k => { const [key, label, color] = SEG.find(sg => sg[0] === k); return {key, label, mark: 'box', color}; };
  [['Idle:', ['imi', 'isr', 'ino', 'none'].map(segItem)],
    ['Over idle:', ['mi', 'sr', 'no', 'loss', 'dr'].map(segItem).concat([{key: 'm', label: 'measured total', mark: 'line', color: 'var(--ink)'}])]].forEach(([label, items]) => {
    const d = document.createElement('div'); legHost.appendChild(d);
    d.style.cssText = 'display: grid; grid-template-columns: max-content 1fr; column-gap: 8px; align-items: baseline; margin: 2px 0';
    const t = document.createElement('span'); t.style.cssText = 'color: var(--ink); font-weight: 600; font-size: 0.82rem'; t.textContent = label;
    const c = document.createElement('div'); d.append(t, c); CK.legend(c, items); c.style.margin = '0';
  });
  const read = CK.readout('v1-read');
  const cur = () => (st.line ? refit : fit)[st.card];
  function out() {
    const F0 = fit[st.card], F1 = refit[st.card], c = cur().coef;
    let s = `${st.card}: unmetered = ${f(c[0], 3)} × minion + ${f(c[1], 3)} × SRAM + ${f(c[2], 3)} × NoC + ${f(c[3], 1)} pJ per DRAM byte; rms ${f(cur().rms, 2)} W over ${cur().n}; ${f(cur().rmsd, 2)} W over ${cur().nd} DRAM configurations.`;
    if (st.line) {
      const d = F1.pts.filter(p => full(p)), up = d.filter(p => p.rnd && p.res > 0).length, dn = d.filter(p => !p.rnd && p.res < 0).length, nr = d.filter(p => p.rnd).length;
      s += ` Counting the line read before each L1 store: DRAM rms ${f(F0.rmsd, 2)} → ${f(F1.rmsd, 2)} W, ${f(F0.coef[3], 1)} → ${f(F1.coef[3], 1)} pJ/B; the pattern remains (random data above the fit in ${up} of ${nr} full-rate DRAM configurations, zeros and constants below in ${dn} of ${d.length - nr}).`;
    }
    setHTML('v1-coef', s);
    const p = cur().pts.find(q => q.cfg === st.sel) || cur().pts[0], rail = p.mi + p.sr + p.no;
    read.set(`${pretty(p.cfg)} on ${st.card}: ${f(p.over, 2)} W over idle; the rails ${f(rail, 2)} W (minion ${f(p.mi, 2)}, SRAM ${f(p.sr, 2)}, NoC ${f(p.no, 2)}); on no meter ${f(p.un, 2)} W (${pct(p.un / p.over)}): ` +
      `the fit gives ${f(p.loss, 2)} W of delivery loss${p.g > 0 ? ` and ${f(p.dr, 2)} W of DRAM (${num(p.g, 1)} GB/s)` : ''}, residual ${sgn(p.res)} W.`);
  }
  let gB = null, geo = null, circ = {};
  function drawB() {
    if (!gB) return;
    while (gB.firstChild) gB.removeChild(gB.firstChild);
    const {bx, by, bw} = geo, p = cur().pts.find(q => q.cfg === st.sel) || cur().pts[0];
    const x = CK.lin(0, Math.max(I.board_w, p.over) * 1.04, bx + 4, bx + bw - 8), bh = 26;
    const bar = (y, segs, title) => {
      CK.txt(gB, bx + 4, y - 8, title, 'lab-strong');
      let x0 = 0; const outs = [];
      segs.forEach(([k, v, lab]) => {
        if (v <= 0) return;
        const c = SEG.find(s => s[0] === k)[2], r = CK.el('rect', {x: x(x0), y, width: Math.max(0.5, x(x0 + v) - x(x0)), height: bh}, gB);
        r.style.fill = c; r.style.stroke = 'var(--surface)'; r.style.strokeWidth = '1';
        const w = x(x0 + v) - x(x0), cx = (x(x0) + x(x0 + v)) / 2;
        if (w >= 40) { const t = CK.txt(gB, cx, y + 17, f(v, 2), 'lab-strong', 'middle'); t.style.fill = inkOn(c); } else outs.push([cx, lab + ' ' + f(v, 2)]);
        x0 += v;
      });
      if (outs.length) {  /* segments too narrow for their number: listed under the bar, wrapped to the panel */
        const lines = [''], max = Math.max(20, Math.floor((bw - 8) / 6.4));
        outs.forEach(([cx, s]) => { const l = lines.length - 1; if (lines[l] && (lines[l] + ' · ' + s).length > max) lines.push(s); else lines[l] = lines[l] ? lines[l] + ' · ' + s : s; });
        lines.forEach((s, i) => CK.txt(gB, bx + 4, y + bh + 15 + 14 * i, s, 'tick'));
      }
      return x0;
    };
    bar(by + 22, [['imi', I.minion_w, 'minion'], ['isr', I.sram_w, 'SRAM'], ['ino', I.noc_w, 'NoC'], ['none', I.unsensed_w, 'no meter']], `Idle at ${num(I.die_c, 0)} °C (aifoundry2): ${f(I.board_w, 1)} W`);
    const y2 = by + 112, fitted = [['mi', p.mi, 'minion'], ['sr', p.sr, 'SRAM'], ['no', p.no, 'NoC'], ['loss', p.loss, 'loss'], ['dr', p.dr, 'DRAM']];
    CK.txt(gB, bx + 4, y2 - 24, p.cfg.startsWith('dramrow/stride8K') ? 'L3 reads through the mesh' : p.cfg, 'lab-strong');
    bar(y2, fitted, `${st.card}, over idle: measured ${f(p.over, 2)} W, residual ${sgn(p.res)} W`);
    const xm = x(p.over), m = CK.el('line', {x1: xm, x2: xm, y1: y2 - 5, y2: y2 + bh + 5, 'stroke-width': 2.5}, gB); m.style.stroke = 'var(--ink)';
    const ya = by + 196;
    CK.el('line', {x1: x(0), x2: x(Math.max(I.board_w, p.over) * 1.04), y1: ya, y2: ya, class: 'ck-axis'}, gB);
    x.ticks(5).forEach(t => { CK.el('line', {x1: x(t), x2: x(t), y1: ya, y2: ya + 4, class: 'ck-axis'}, gB); CK.txt(gB, x(t), ya + 16, num(t), 'tick', 'middle'); });
    CK.txt(gB, bx + bw / 2, ya + 32, 'watts', 'lab', 'middle');
  }
  const layout = W => { const side = W >= 760, aW = side ? Math.min(440, Math.floor(W * 0.46)) : W, aH = side ? aW : Math.min(W, 420);
    return {side, aW, aH, bx: side ? aW + 28 : 0, by: side ? 10 : aH + 18, bw: side ? W - aW - 28 : W, H: side ? Math.max(aH, 250) : aH + 18 + 240}; };
  function draw(fm) {
    const W = fm.W, G = layout(W), L = 46, R = 10, T = 26, B = 42, a = CK.el('g', {}, fm.svg);
    geo = G;
    const x = CK.lin(0, 8, L, G.aW - R), y = CK.lin(0, 8, G.aH - B, T), g0 = CK.el('g', {'aria-hidden': 'true'}, a);
    x.ticks(4).forEach(t => { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: G.aH - B, class: 'grid-line'}, g0); CK.txt(g0, x(t), G.aH - B + 16, num(t), 'tick', 'middle'); });
    y.ticks(4).forEach(t => { CK.el('line', {x1: L, x2: G.aW - R, y1: y(t), y2: y(t), class: 'grid-line'}, g0); CK.txt(g0, L - 6, y(t) + 4, num(t), 'tick', 'end'); });
    CK.txt(g0, (L + G.aW - R) / 2, G.aH - 8, 'unmetered W the fit gives', 'lab', 'middle');
    CK.txt(g0, 2, 13, 'unmetered W measured (board − rails, over idle)', 'lab');
    const dg = CK.el('line', {x1: x(0), y1: y(0), x2: x(8), y2: y(8), 'stroke-dasharray': '5 4', 'stroke-width': 1.3}, g0); dg.style.stroke = 'var(--ref)';
    CK.txt(g0, x(7.9), y(7.9) + 14, 'fit = measured', 'tick', 'end');
    /* the card shown, with its registry mark, in the empty corner under the diagonal */
    const kc = CK.card(st.card), kt = CK.txt(g0, G.aW - R - 4, G.aH - B - 10, kc.label, 'lab-strong', 'end');
    let kw = 0; try { kw = kt.getComputedTextLength(); } catch (_) { /* no layout */ }
    CK.cardMark(g0, st.card, G.aW - R - 4 - (kw || 7 * kc.label.length) - 10, G.aH - B - 14, 5);
    const pts = cur().pts.filter(p => st.on.has(p.k)).sort((p, q) => p.res - q.res), nodes = [];
    circ = {};
    pts.forEach(p => {
      const cx = x(Math.min(8, Math.max(0, p.fit))), cy = y(Math.min(8, Math.max(0, p.un))), c = CLC[p.k];
      const n = CK.el('circle', {cx, cy, r: p.cfg === st.sel ? 6 : 3.8, 'stroke-width': 1.6, stroke: c, fill: p.rnd ? c : 'var(--surface)', class: p.cfg === st.sel ? 'pt-sel' : null}, a);
      circ[p.cfg] = n;
      CK.tip(fm, n, `<b>${pretty(p.cfg)}</b> · ${st.card}<br>unmetered ${f(p.un, 2)} W, the fit ${f(p.fit, 2)} W, residual ${sgn(p.res)} W<br>${f(p.over, 2)} W over idle, ${pct(p.un / p.over)} of it on no meter`);
      n.addEventListener('pointerenter', () => pick(p.cfg));
      n.addEventListener('pointerdown', () => pick(p.cfg));
      nodes.push(n);
    });
    CK.keynav(fm, nodes, {onFocus: (n, k) => pick(pts[k].cfg)});
    gB = CK.el('g', {'aria-hidden': 'true'}, fm.svg);
    drawB();
  }
  const mark = (m, cfg, on) => { const n = m[cfg]; if (n) { n.classList.toggle('pt-sel', on); n.setAttribute('r', on ? 6 : 3.8); } };
  function pick(cfg) { if (st.sel === cfg) return; mark(circ, st.sel, false); st.sel = cfg; mark(circ, cfg, true); drawB(); out(); }
  const fr = CK.frame('v1', {height: W => layout(W).H, minW: 300, maxW: 1100, label: "Where a workload's watts go: measured against fitted unmetered power, and a configuration's watts by meter", draw});
  out();

  /* ---------- the sensors table ---------- */
  const V = P.pvt, pts0 = V.vm_points;
  const pv = document.getElementById('pvttab');
  pv.innerHTML = '<thead><tr><th>Moortec PVT on the die</th><th>Count</th><th>Resolution</th><th>What the host gets</th></tr></thead><tbody>' +
    `<tr><td>Temperature sensors</td><td>${V.ts_active} live of ${V.controllers * V.ts_per_controller} (${V.controllers} controllers × ${V.ts_per_controller}; one per minion shire and one in the IO shire, the PCIe shire's dropped from the RTL)</td><td>${V.ts_resolution_c} °C (12-bit)</td><td>${esc(V.host_sees.temperature)}</td></tr>` +
    `<tr><td>Voltage monitor points</td><td>${Object.values(pts0).reduce((s, v) => s + v, 0)}: ${Object.keys(pts0).map(k => k + ' ' + pts0[k]).join('; ')}</td><td>${Math.round(V.vm_lsb_uv)} µV (${V.vm_bits}-bit); 1 mV as forwarded</td><td>${esc(V.host_sees.voltage)}<div class="small">In the SP’s DEBUG trace: ${esc(V.host_sees.debug_trace)}</div></td></tr>` +
    `<tr><td>Process detectors</td><td>${V.pd_active} live of ${V.controllers * V.pd_per_controller}</td><td>ring-oscillator counts</td><td>nothing: configured with measurement disabled, never read</td></tr>` +
    `<tr><td>External analog inputs</td><td>2</td><td>as the monitors</td><td>nothing: the reader is a stub with no caller; what the board wires to them is unknown</td></tr></tbody>`;
  CK.stackTable(pv);

  /* ---------- V1b: is the DDR monitor a DRAM meter? ---------- */
  const a = Dp.mv_per_dram_offrail_w, b = Dp.mv_per_board_w_common, rms = Dp.rms_mv, ir = Dp.minion_ir_drop_mv_per_w;
  const DR = Dp.per_config.map(r => ({cfg: r[0], dd: r[1], off: r[2], over: r[3], dm: r[4], mi: r[5], k: klass(r[0]), rnd: r[0].includes('/random'), dram: movesDram(r[0])}))
    .map(p => ({...p, pred: a * p.off + b * (p.over - p.off)})).map(p => ({...p, ex: p.dd - p.pred}));
  const nd = DR.filter(p => !p.dram), dRows = DR.filter(p => p.dram), minD = dRows.reduce((s, p) => (p.dd < s.dd ? p : s)), big = DR.filter(p => p.ex > 1);
  const l3 = nd.filter(p => p.cfg.startsWith('dramrow/stride8K')).reduce((s, p) => (p.dd > s.dd ? p : s));
  /* The chart's own per-card calibrations (power.checks.droop[card].per_config), so it can draw any card; the
     prose below and DR/a/b/rms/ir/minD/l3 stay aifoundry2's (the reference calibration), unaffected. */
  const DROOP_BY_CARD = {aifoundry2: {a, b, rms, ir, rows: DR, minD, l3}};
  CARDS.filter(c => c !== 'aifoundry2').forEach(c => {
    const w = CH.droop[c];
    if (!w || !w.per_config) return;
    const a2 = w.slope, b2 = w.common;
    const rows = w.per_config.map(r => ({cfg: r[0], dd: r[1], off: r[2], over: r[3], dm: r[4], mi: r[5], k: klass(r[0]), rnd: r[0].includes('/random'), dram: movesDram(r[0])}))
      .map(p => ({...p, pred: a2 * p.off + b2 * (p.over - p.off)})).map(p => ({...p, ex: p.dd - p.pred}));
    const ndc = rows.filter(p => !p.dram), drc = rows.filter(p => p.dram);
    const minDc = drc.length ? drc.reduce((s, p) => (p.dd < s.dd ? p : s)) : null;
    const l3c = ndc.filter(p => p.cfg.startsWith('dramrow/stride8K'));
    DROOP_BY_CARD[c] = {a: a2, b: b2, rms: w.rms_mv, ir: w.ir, rows,
      minD: minDc, l3: l3c.length ? l3c.reduce((s, p) => (p.dd > s.dd ? p : s)) : null};
  });
  const DRCARDS = CK.cardsIn(Object.keys(DROOP_BY_CARD));
  const DC = CH.droop, d2 = DC.aifoundry2, OTH = CARDS.slice(1);
  setHTML('droopidle', perCard(CARDS.map(c => f(DC[c].idle_ddr_mv, 0)), 'mV'));
  const irz = OTH.filter(c => DC[c].pass_ci99.ir[0] <= 0), irp = irz.every(c => DC[c].passes.ir.every(v => v > 0));
  setHTML('irdrop', `about ${perCard(CARDS.map(c => f(DC[c].ir, 2)), 'mV per watt the cores draw')}` +
    (irz.length ? ` (on ${andList(irz)} ${irp ? 'the sag is there in every pass, but ' : ''}the 99% interval over ${irz.length > 1 ? 'their' : 'its'} ${word(DC[irz[0]].passes.ir.length)} passes includes zero)` : ''));
  setHTML('droop-mvw', `1 mV ≈ ${perCard(CARDS.map(c => f(1 / DC[c].slope, 1)), 'W')}`);
  /* how the idle reading moves with the die temperature (power.checks.droop[card].idle_vs_temp) */
  const IT = c => DC[c].idle_vs_temp, it2 = IT(CARDS[0]);
  setHTML('droop-temp', it2 ? `Its idle reading falls as the die warms, by about ${f(-it2.slope_mv_per_c, 2)} mV per °C on ${CARDS[0]} (${f(-it2.slope_mv_per_c * (it2.die_c_p10_p90[1] - it2.die_c_p10_p90[0]), 1)} mV ` +
    `between ${num(it2.die_c_p10_p90[0], 0)} and ${num(it2.die_c_p10_p90[1], 0)} °C, the middle 80% of its catalogue's idle gaps), ${andList(OTH.map(c => `${f(-IT(c).slope_mv_per_c, 2)} on ${c}`))}; ` +
    OTH.map((c, i) => (i ? `${c} ${rng(...IU[c].die_c, 0, '°C')} and ${f(DC[c].idle_ddr_mv, 0)} mV` : `${c} idles at ${rng(...IU[c].die_c, 0, '°C')} in the catalogue and reads ${f(DC[c].idle_ddr_mv, 0)} mV there`)).join(', ') : '');
  const onMesh = big.filter(p => /^(wire|tload\/scp|tstore\/scp|scpline|neigh|dramrow\/stride8K)/.test(p.cfg)).length;
  setHTML('drooptext', `Over aifoundry2's ${Dp.n} catalogue configurations (${F.aifoundry2.n > Dp.n ? `its ${F.aifoundry2.n} less the ${word(F.aifoundry2.n - Dp.n)} not in this telemetry` : 'all of them, from the telemetry of its version-3 catalogue'}), the DDR rail droops ` +
    `<b>${f(a, 2)} mV per watt of off-rail DRAM power</b> (the unmetered watts less the fitted rail losses), with an rms of ${f(rms, 2)} mV: ` +
    `about ${fracWord(rms / minD.dd)} of the smallest DRAM burst's droop (${f(minD.dd, 2)} mV, <code>${esc(minD.cfg)}</code>). The same fit gives ` +
    andList(OTH.map(c => `${f(DC[c].slope, 2)} mV per watt on ${c}'s ${num(DC[c].n, 0)} configurations (rms ${f(DC[c].rms_mv, 2)} mV)`)) + '. ' +
    `The fit also carries a small term for the rest of the board's power: ` +
    andList(CARDS.map(c => { const z = DC[c].pass_ci99.common[0] <= 0; return `${num(DC[c].common, 3)} mV per watt on ${c}${z ? `, which its ${word(DC[c].passes.common.length)} passes do not distinguish from zero` : ''}`; })) + '. ' +
    `The DRAM slope rests on ${word(dRows.length)} configurations, and the ${word(big.length)} residuals above 1 mV ` +
    `(${rng(...mm(big.map(p => p.ex)), 1, 'mV')}) are all bursts with no DRAM traffic, ${word(onMesh)} of them on the mesh, the scratchpads or the L3.`);
  const NM = DC.named, nmv = (c, k) => DC[c].named[k].mean, top = Math.max(...CARDS.flatMap(c => [...NM.mesh, NM.l3].map(k => nmv(c, k))));
  const l3med = med(d2.named[NM.l3].passes);
  setHTML('droopmesh', `heavy mesh, scratchpad and L3 traffic with no DRAM access droops it by up to about ${f(top, 0)} mV on ${CARDS.length === 2 ? 'both' : `all ${WORD[CARDS.length]}`} cards (on aifoundry2 ` +
    NM.mesh.map(k => `<code>${esc(k)}</code> ${f(nmv('aifoundry2', k), 2)} mV`).join(' and ') +
    NM.mesh.map(k => { const o = OTH.filter(c => Math.abs(nmv('aifoundry2', k) - nmv(c, k)) > 0.3);
      return o.length ? `; <code>${esc(k)}</code> reads ${andList(o.map(c => `${f(nmv(c, k), 2)} mV on ${c}`))}` : ''; }).join('') +
    `; ${f(l3med, 1)} mV for L3 reads through the mesh, <code>${esc(NM.l3)}</code>, the median of ${word(d2.named[NM.l3].passes.length)} passes), ` +
    `up to ${perCard(CARDS.map(c => f(DC[c].max_nondram_excess_mv[0], 1)), 'mV')} more than the calibration allows, ` +
    `which it would read as up to about ${f(Math.max(...CARDS.map(c => DC[c].max_nondram_excess_mv[0] / DC[c].slope)), 0)} W of DRAM.`);
  const mv1 = v => (Math.round(v * 10) / 10).toFixed(1);
  const dt = document.getElementById('drooptab');
  dt.innerHTML = '<thead><tr><th>Configuration (aifoundry2)</th><th class="num">W over idle</th><th class="num">unmetered W less fitted rail losses</th><th class="num">DDR-rail droop, mV</th><th class="num">minion-rail droop, mV</th></tr></thead><tbody>' +
    Dp.examples.map(e => `<tr><td><code>${esc(e.cfg)}</code></td><td class="num">${f(e.over_idle_w)}</td><td class="num">${e.dram_offrail_w ? f(e.dram_offrail_w) : '—'}</td><td class="num">${mv1(e.droop_ddr_mv)}</td><td class="num">${mv1(e.droop_minion_mv)}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(dt);
  const ds = {view: 'board', on: new Set(CLS.map(c => c[0])), sel: l3.cfg, card: 'aifoundry2'};
  const VIEWS = {board: {x: p => p.over, y: p => p.dd, xd: [0, 27], yd: [-0.5, 6.5], xl: 'board watts over idle', yl: 'DDR-rail droop, mV'},
    pred: {x: p => p.pred, y: p => p.dd, xd: [-0.5, 7], yd: [-0.5, 7], xl: 'droop the calibration predicts, mV', yl: 'DDR-rail droop measured, mV'},
    minion: {x: p => p.mi, y: p => p.dm, xd: [0, 22], yd: [-0.5, 2.5], xl: 'minion-rail watts over idle', yl: 'minion-rail droop, mV'}};
  const drCtl = document.getElementById('dr-ctl'), drBox = () => { const d = document.createElement('div'); drCtl.appendChild(d); return d; };
  if (DRCARDS.length > 1) CK.cardSeg(drBox(), {cards: DRCARDS, bus: 'chain-card', value: ds.card, onChange: v => {
    ds.card = v;
    if (!DROOP_BY_CARD[v].rows.some(p => p.cfg === ds.sel)) ds.sel = (DROOP_BY_CARD[v].l3 || DROOP_BY_CARD[v].rows[0]).cfg;
    dfr.redraw(); dout();
  }});
  CK.seg(drBox(), {label: 'View', options: [['board', 'against board watts'], ['pred', 'predicted against measured'], ['minion', 'minion rail (IR drop)']], value: ds.view, onChange: v => { ds.view = v; dfr.redraw(); dout(); }});
  CK.legend('dr-leg', CLS.map(([k, l, c]) => ({key: k, label: l, mark: 'dot', color: c})), {toggle: true, onChange: keys => { ds.on = new Set(keys); dfr.redraw(); }});
  const dread = CK.readout('dr-read');
  function dout() {
    const cd = DROOP_BY_CARD[ds.card], a = cd.a, b = cd.b, ir = cd.ir, DR = cd.rows;
    const p = DR.find(q => q.cfg === ds.sel);
    if (ds.view === 'minion') { dread.set(`${pretty(p.cfg)} on ${ds.card}: the minion rail draws ${f(p.mi, 2)} W over idle and its monitors read ${f(p.dm, 2)} mV lower; ${f(ir, 3)} mV per watt predicts ${f(ir * p.mi, 2)} mV.`); return; }
    dread.set(`${pretty(p.cfg)} on ${ds.card}: droop ${f(p.dd, 2)} mV measured, ${f(p.pred, 2)} mV predicted (${f(a, 2)} × ${f(p.off, 2)} W off-rail DRAM + ${f(b, 3)} × ${f(p.over - p.off, 2)} W of the rest); ` +
      `excess ${sgn(p.ex)} mV, which reads as ${sgn(p.ex / a)} W of ${p.dram ? 'extra' : 'phantom'} DRAM.`);
  }
  function ddraw(fm) {
    const cd = DROOP_BY_CARD[ds.card], a = cd.a, b = cd.b, rms = cd.rms, ir = cd.ir, DR = cd.rows, minD = cd.minD, l3 = cd.l3;
    const W = fm.W, H = fm.H, v = VIEWS[ds.view], L = 46, R = 12, T = 26, B = 42;
    const x = CK.lin(v.xd[0], v.xd[1], L, W - R), y = CK.lin(v.yd[0], v.yd[1], H - B, T);
    CK.axes(fm, {x, y, L, R, T, B, xl: v.xl, yl: v.yl});
    const g0 = CK.el('g', {'aria-hidden': 'true'}, fm.svg), line = (m, c0, lab) => {
      const x0 = v.xd[0], x1 = v.xd[1], yy = xx => c0 + m * xx;
      if (ds.view !== 'minion') { const band = CK.el('path', {d: `M${x(x0)},${y(yy(x0) + rms)} L${x(x1)},${y(Math.min(v.yd[1], yy(x1) + rms))} L${x(x1)},${y(Math.min(v.yd[1], yy(x1) - rms))} L${x(x0)},${y(yy(x0) - rms)} Z`}, g0); band.style.fill = 'color-mix(in srgb, var(--ref) 18%, transparent)'; }
      const l = CK.el('line', {x1: x(x0), y1: y(yy(x0)), x2: x(x1), y2: y(Math.min(v.yd[1], yy(x1))), 'stroke-dasharray': '5 4', 'stroke-width': 1.4}, g0); l.style.stroke = 'var(--ref)';
      if (lab) CK.txt(g0, x(x1) - 4, y(Math.min(v.yd[1], yy(x1))) - 8, lab, 'tick', 'end');
    };
    /* the reference line's label: on the line when there is room, else as a key at top right, clear of the points */
    const noDram = [`no DRAM: ${f(b, 3)} mV per W${CH.droop[ds.card].pass_ci99.common[0] <= 0 ? ', within noise' : ''}`, `band ± ${f(rms, 2)} mV rms`];
    if (ds.view === 'board') line(b, 0, fm.narrow ? '' : noDram.join('; '));
    if (ds.view === 'pred') line(1, 0, `measured = predicted ± ${f(rms, 2)} mV`);
    if (ds.view === 'minion') line(ir, 0, `${f(ir, 3)} mV per W`);
    const pts = DR.filter(p => ds.on.has(p.k)).sort((p, q) => v.x(p) - v.x(q)), nodes = [];
    dcirc = {};
    pts.forEach(p => {
      const cx = x(Math.max(v.xd[0], Math.min(v.xd[1], v.x(p)))), cy = y(Math.max(v.yd[0], Math.min(v.yd[1], v.y(p)))), c = CLC[p.k], on = p.cfg === ds.sel;
      if (ds.view === 'board' && p.dram) { const py = y(p.pred), l = CK.el('line', {x1: cx, x2: cx, y1: py, y2: cy, 'stroke-width': 1.2}, g0); l.style.stroke = c;
        const dm = CK.el('path', {d: `M${cx - 4},${py} L${cx},${py - 4} L${cx + 4},${py} L${cx},${py + 4} Z`, 'stroke-width': 1.3}, g0); dm.style.stroke = c; dm.style.fill = 'var(--surface)'; }
      const n = CK.el('circle', {cx, cy, r: on ? 6 : 3.8, 'stroke-width': 1.6, stroke: c, fill: p.rnd ? c : 'var(--surface)', class: on ? 'pt-sel' : null}, fm.svg);
      dcirc[p.cfg] = n;
      CK.tip(fm, n, ds.view === 'minion' ? `<b>${pretty(p.cfg)}</b><br>minion rail ${f(p.mi, 2)} W over idle, droop ${f(p.dm, 2)} mV` :
        `<b>${pretty(p.cfg)}</b><br>droop ${f(p.dd, 2)} mV, predicted ${f(p.pred, 2)} mV<br>excess ${sgn(p.ex)} mV = ${sgn(p.ex / a)} W of ${p.dram ? 'extra' : 'phantom'} DRAM`);
      n.addEventListener('pointerenter', () => dpick(p.cfg)); n.addEventListener('pointerdown', () => dpick(p.cfg));
      nodes.push(n);
    });
    if (ds.view === 'board') {
      const note = (p, s, dy) => { if (!p || !ds.on.has(p.k)) return; const px = x(p.over), right = px > (L + W - R) / 2; CK.txt(g0, px + (right ? -9 : 8), y(p.dd) + dy, s, 'tick', right ? 'end' : 'start'); };
      note(l3, 'L3 reads through the mesh', 4); note(minD, 'smallest DRAM droop', 14);
      CK.txt(g0, W - R - 4, T + 12, '◇ predicted for a DRAM point', 'tick', 'end');
      if (fm.narrow) { const kx = W - R - 4, ky = T + 60, k = CK.el('line', {x1: kx - 22, x2: kx, y1: ky - 4, y2: ky - 4, 'stroke-dasharray': '5 4', 'stroke-width': 1.4}, g0);
        k.style.stroke = 'var(--ref)'; noDram.forEach((s, i) => CK.txt(g0, kx - 28, ky + 14 * i, s, 'tick', 'end')); }
    }
    CK.keynav(fm, nodes, {onFocus: (n, k) => dpick(pts[k].cfg)});
  }
  let dcirc = {};
  function dpick(cfg) { if (ds.sel === cfg) return; mark(dcirc, ds.sel, false); ds.sel = cfg; mark(dcirc, cfg, true); dout(); }
  const dfr = CK.frame('dr', {height: W => (W < 600 ? 340 : 380), minW: 300, maxW: 900, label: 'DDR-rail droop of every catalogue configuration, on the chosen card, against board watts, its prediction, or the minion rail', draw: ddraw});
  dout();
})();

/* ---------- the meter chain as a diagram (S4.1) ---------- */
(function () {
  const M = D.energy_events.meter, RF = P.rail_filter, SA = P.sampler, I = P.idle_73c, NR = P.rails_no_telemetry;
  const nMods = P.pmbus_modules.length, nVals = P.pmbus_values.length, nRead = P.pmbus_readings.length, nNum = nMods * nVals * nRead;
  const st = {card: CARDS[0]};
  CK.cardSeg('chain-ctl', {cards: CARDS, bus: 'chain-card', value: st.card, onChange: v => { st.card = v; fr.redraw(); }});
  const read = CK.readout('chain-read');
  /* per card, from the version-3 campaign's three passes: how often a new board value arrives while ettelem samples at
     10 Hz (energy_events.meter.board_refresh_ms, phase-folding the board-power stream; the mean over the passes), and
     the SP's own pass in its trace, under the sampler and with no sampler running (sp_pass_ms; the medians) */
  const SPM = M.sp_pass_ms || {}, BR = M.board_refresh_ms || {}, medOf = a => (a && a.length ? med(a) : null);
  const meanOf = a => (a && a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);
  const refMs = c => meanOf((BR[c] || {}).sampler_10hz_ms) || 1000 * ({aifoundry2: M.pass_s, aifoundry3: M.pass_s_a3, 'aifoundry1-c1': M.pass_s_a1c1}[c] || M.pass_s);
  const passMs = c => medOf((SPM[c] || {}).sampled_ms);
  const quietMs = c => medOf((SPM[c] || {}).quiet_ms);
  const ROWS = [
    {key: 'in', lines: ['12 V input', 'from the power supply'],
      desc: () => `The board's 12 V input, metered too: ${num(1000 * M.board_lsb_w, 0)} mW steps, one new value a pass.`},
    {key: 'reg', lines: ['3 PMBus regulators', 'minion · SRAM · NoC'],
      desc: c => `Each regulator's running average has fallen ${pct(RF[c].frac_1s)} of the way one second after ${c} steps down (τ ≈ ${f(RF[c].tau_s, 2)} s); ${num(1000 * M.rail_lsb_w, 0)} mW steps.`},
    {key: 'pmic', lines: ['PMIC', `${nMods} × ${nVals} × ${nRead} = ${nNum} numbers`, 'V, I, W ×2 sides, °C'],
      desc: () => `${nMods} regulator modules × ${nVals} values (voltage, current and power on both sides of the regulator, and its temperature) × ${nRead} readings (current, min, max, running average) = ${nNum} numbers; only 4 leave it each pass.`},
    {key: 'sp', lines: ['SP loop', 'rereads all 84 each pass', 'forwards the averages'],
      desc: c => `On ${c} a new board value arrives about every ${num(refMs(c), 0)} ms while ettelem samples, one per pass` +
        (passMs(c) ? `; the SP's own trace, a second method (§4.1), times that pass at ${num(passMs(c), 0)} ms under the sampler${quietMs(c) ? ` and ${num(quietMs(c), 0)} ms with no sampler running` : ''}` : '') +
        `. Each pass forwards each rail's average power, its min and max, and the 12 V input power.`},
    {key: 'ettelem', lines: ['ettelem', 'samples at 10 Hz'],
      desc: c => `${SA[c].bursts} catalogue bursts on ${c}; in ${SA[c].over_60ms ? word(SA[c].over_60ms) : 'none'} of them did the median sample take over 60 ms, and the longest single sample of a DRAM-read burst took ${num(SA[c].read_max_ms, 0)} ms (the strips of “The meter starved by the workload”, above).`},
  ];
  const REST = {lines: [`${NR.length} more rails`, 'no current or power meter', `≈${f(I.unsensed_w, 1)} W of idle unmetered`],
    desc: () => `${NR.join(', ')}: no current or power telemetry; set points in the PMIC for all but the IO shire; on-die voltage readings for four (DDR core, PCIe/PShire, IO shire, Maxion; §4.3), none for VDDQ, VDDQLP or PCIe logic. About ${f(I.unsensed_w, 1)} W of aifoundry2's ${f(I.board_w, 1)} W idle draw (§4.2) is on none of the meters above.`};
  const boxH = n => 20 + 16 * n;
  function layout() {
    let y = 14; const pos = {};
    ROWS.forEach(r => { const h = boxH(r.lines.length); pos[r.key] = {y, h}; y += h + 22; });
    const chainEnd = y - 22, restY = chainEnd + 34, restH = boxH(REST.lines.length);
    return {pos, restY, restH, H: restY + restH + 14};
  }
  function draw(f) {
    const W = f.W, LY = layout(), bw = Math.min(380, W - 70), bx = (W - bw) / 2, branchX = Math.max(10, bx - 22);
    const defs = CK.el('defs', {}, f.svg), mk = CK.el('marker', {id: 'chain-arr', viewBox: '0 0 10 10', refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: 'auto-start-reverse'}, defs);
    const ap = CK.el('path', {d: 'M0,0 L10,5 L0,10 Z'}, mk); ap.style.fill = 'var(--ink-2)';
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    for (let i = 0; i < ROWS.length - 1; i++) {
      const a = LY.pos[ROWS[i].key], b = LY.pos[ROWS[i + 1].key];
      const l = CK.el('line', {x1: bx + bw / 2, y1: a.y + a.h, x2: bx + bw / 2, y2: b.y, 'stroke-width': 1.6, 'marker-end': 'url(#chain-arr)'}, g0);
      l.style.stroke = 'var(--ink-2)';
    }
    const bp = LY.pos.reg, midY1 = bp.y + bp.h / 2, midY2 = LY.restY + LY.restH / 2;
    const dpath = CK.el('path', {d: `M${bx},${midY1} L${branchX},${midY1} L${branchX},${midY2} L${bx},${midY2}`, fill: 'none', 'stroke-width': 1.4, 'stroke-dasharray': '5 4'}, g0);
    dpath.style.stroke = 'var(--ref)';
    function box(x0, y0, w, h, lines, fill, stroke, dash, subCls) {
      const g = CK.el('g', {}, f.svg);
      const r = CK.el('rect', {x: x0, y: y0, width: w, height: h, rx: 8, 'stroke-width': 1.4, 'stroke-dasharray': dash || null}, g);
      r.style.fill = fill; r.style.stroke = stroke;
      CK.txt(g, x0 + 10, y0 + 17, lines[0], 'lab-strong');
      lines.slice(1).forEach((s, i) => CK.txt(g, x0 + 10, y0 + 17 + 15 * (i + 1), s, subCls || 'tick'));
      CK.el('rect', {x: x0, y: y0, width: w, height: h, class: 'ck-hit'}, g);
      return g;
    }
    const nodes = [];
    ROWS.forEach(r => {
      const p = LY.pos[r.key];
      const g = box(bx, p.y, bw, p.h, r.lines, 'color-mix(in srgb, var(--c1) 9%, var(--surface))', 'var(--c1)');
      const html = () => `<b>${esc(r.lines[0])}</b><br>${esc(r.desc(st.card))}`;
      CK.tip(f, g, html, {role: 'button'});
      g._desc = html; nodes.push(g);
    });
    const rg = box(bx, LY.restY, bw, LY.restH, REST.lines, 'color-mix(in srgb, var(--ref) 16%, var(--surface))', 'var(--ref)', '5 4', 'lab');
    const rhtml = () => `<b>${esc(REST.lines[0])}</b><br>${esc(REST.desc())}`;
    CK.tip(f, rg, rhtml, {role: 'button'});
    rg._desc = rhtml; nodes.push(rg);
    CK.keynav(f, nodes, {onFocus: n => read.set(n._desc())});
  }
  const fr = CK.frame('chain', {height: () => layout().H, minW: 280, maxW: 620, label: 'The meter chain, from the 12 V input to a number on this page', draw});
  read.set(`<b>${esc(ROWS[0].lines[0])}</b>: ${esc(ROWS[0].desc(st.card))}`);
})();

/* ---------- the fit's coefficients per card, beside #fittab (S4.2) ---------- */
(function () {
  const F = P.fit, CH2 = P.checks.fit;
  const COEFS = [['minion', '× minion-rail W'], ['sram', '× SRAM-rail W'], ['noc', '× NoC-rail W'], ['dram_pj_per_byte', 'pJ per DRAM byte']];
  const rowH = 38 + 16 * CARDS.length, L = 8, R = 10, T = 4, B = 10;  /* one whisker per card in each row */
  function draw(f) {
    const W = f.W, g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), nodes = [];
    COEFS.forEach(([k, lab], i) => {
      const y0 = T + i * rowH, dp = k === 'dram_pj_per_byte' ? 1 : 3;
      CK.txt(f.svg, L, y0 + 11, lab, 'lab-strong');
      const vals = CARDS.map(c => ({card: c, v: F[c].coef[k], se: CH2[c].se_hc3[k]}));
      const lo0 = Math.min(0, ...vals.map(v => v.v - 1.3 * v.se)), hi0 = Math.max(...vals.map(v => v.v + 1.3 * v.se));
      const pad = (hi0 - lo0) * 0.1 || 1;
      const x = CK.lin(lo0 - pad, hi0 + pad, L, W - R);
      const gy0 = y0 + 26, gy1 = y0 + rowH - 12;
      x.ticks(3).forEach(t => {
        CK.el('line', {x1: x(t), x2: x(t), y1: gy0, y2: gy1, class: 'grid-line'}, g0);
        CK.txt(g0, x(t), y0 + rowH - 2, num(t), 'tick', 'middle');
      });
      if (lo0 - pad < 0 && hi0 + pad > 0) {
        const zl = CK.el('line', {x1: x(0), x2: x(0), y1: gy0, y2: gy1, 'stroke-dasharray': '3 3'}, g0); zl.style.stroke = 'var(--ref)';
      }
      vals.forEach((v, j) => {
        const cy = gy0 + 8 + j * 16, cc = CK.card(v.card), xlo = x(v.v - v.se), xhi = x(v.v + v.se), xc = x(v.v);
        const g = CK.el('g', {}, f.svg);
        const w0 = CK.el('line', {x1: xlo, x2: xhi, y1: cy, y2: cy, 'stroke-width': 2}, g); w0.style.stroke = cc.color;
        [xlo, xhi].forEach(xx => { const cap = CK.el('line', {x1: xx, x2: xx, y1: cy - 4, y2: cy + 4, 'stroke-width': 1.4}, g); cap.style.stroke = cc.color; });
        CK.cardMark(g, v.card, xc, cy, 4);
        CK.el('rect', {x: L, y: cy - 8, width: W - L - R, height: 16, class: 'ck-hit'}, g);
        CK.tip(f, g, `<b>${esc(cc.label)}</b> ${esc(lab)}<br>${num(v.v, dp)} ± ${num(v.se, dp)} (one robust SE)`, {role: 'img'});
        nodes.push(g);
      });
    });
    CK.keynav(f, nodes);
  }
  CK.frame('coef', {height: () => T + COEFS.length * rowH + B, minW: 220, maxW: 340, label: "The fit's coefficients per card, each ± one robust standard error", draw});
})();

/* ---------- the meter starved by the workload: one strip per card (S4.1) ---------- */
(function () {
  const SA = P.sampler;
  const SCARDS = CK.cardsIn(Object.keys(SA).filter(c => SA[c] && Array.isArray(SA[c].dist)));
  const read = CK.readout('starve-read');
  const allMs = SCARDS.flatMap(c => SA[c].dist.map(d => d.ms).concat((SA[c].dropped || []).map(d => d.ms)));
  const lo = 18, hi = Math.max(...allMs) * 1.12;
  const maxN = Math.max(...SCARDS.flatMap(c => SA[c].dist.map(d => d.n)));
  const rad = n => Math.max(3, Math.min(13, 3 + 9 * Math.sqrt(n / maxN)));
  const TICKS = [20, 25, 30, 50, 75, 100, 150, 200, 300];
  const rowH = 46, T = 24, B = 34;
  function draw(f) {
    const W = f.W, L = 14, R = 14, plotBottom = T + SCARDS.length * rowH;
    const x = CK.log(lo, hi, L, W - R);
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    TICKS.filter(t => t >= lo && t <= hi).forEach(t => {
      CK.el('line', {x1: x(t), x2: x(t), y1: T - 8, y2: plotBottom - 6, class: 'grid-line'}, g0);
      CK.txt(g0, x(t), plotBottom + 12, num(t, 0), 'tick', 'middle');
    });
    CK.txt(g0, (L + W - R) / 2, plotBottom + 30, 'one telemetry sample, ms (log scale)', 'lab', 'middle');
    const nodes = [];
    SCARDS.forEach((c, i) => {
      const cy = T + i * rowH + rowH / 2 - 4, cc = CK.card(c), total = SA[c].bursts;
      CK.txt(g0, L, T + i * rowH - 2, `${cc.label} (${total} bursts)`, 'lab-strong');
      CK.el('line', {x1: L, x2: W - R, y1: cy, y2: cy, class: 'grid-line', opacity: 0.5}, g0);
      (SA[c].dist || []).forEach(d => {
        const cx = x(Math.max(lo, Math.min(hi, d.ms))), r = rad(d.n);
        const n0 = CK.el('circle', {cx, cy, r, 'stroke-width': 1.4}, f.svg);
        n0.style.fill = cc.color; n0.style.stroke = 'var(--surface)';
        const detail = d.cfgs ? '<br>' + d.cfgs.map(x2 => `<code>${esc(x2.cfg)}</code> pass ${x2.pass}`).join('<br>') : '';
        const html = `<b>${num(d.ms, 1)} ms</b> · ${esc(cc.label)}: ${d.n} of ${total} burst${d.n === 1 ? '' : 's'}${detail}`;
        CK.tip(f, n0, html, {role: 'img'});
        n0._desc = html; nodes.push(n0);
      });
      (SA[c].dropped || []).forEach(d => {
        const cx = x(Math.max(lo, Math.min(hi, d.ms))), s = 6;
        const dm = CK.el('polygon', {points: `${cx},${cy - s} ${cx + s},${cy} ${cx},${cy + s} ${cx - s},${cy}`, 'stroke-width': 1.6}, f.svg);
        dm.style.fill = 'var(--surface)'; dm.style.stroke = 'var(--warn)';
        const html = `<b>${num(d.ms, 1)} ms</b> · ${esc(cc.label)}: dropped, not counted — <code>${esc(d.burst)}</code> (${esc(d.run)})`;
        CK.tip(f, dm, html, {role: 'img'});
        dm._desc = html; nodes.push(dm);
      });
    });
    CK.keynav(f, nodes, {onFocus: n => read.set(n._desc)});
  }
  CK.frame('starve', {height: () => T + SCARDS.length * rowH + B, minW: 300, maxW: 1000, label: "Every catalogue burst's own sampler latency, one strip per card", draw});
  read.set(`Most bursts take the usual sample time on ${SCARDS.length === 2 ? 'both cards' : `all ${word(SCARDS.length)} cards`}; the tail past it is what the workload starves. Hover, tap or tab to a mark.`);
})();

/* E59's three sizes, named as on the sparse parity page, for the captions of #bt and #sj (L1 and L2 there are sizes, not
   cache levels) */
const spSizes = () => { const Z = (D.solve_energy || {}).sizes || [];
  return `three sizes, named as on the sparse parity page: ` + andList(Z.map((s, i) => `${esc(s.label)} = (${i ? '' : 'n '}${s.size[0]}, ${i ? '' : 'k '}${s.size[1]}, ${i ? '' : 'η '}${s.size[2]}, ${i ? '' : 'm '}${num(s.size[3], 0)})`)); };

/* ---------- one solve's joules, as the card's meters report them: §4.2's fit on a workload it was not made on (E59) ---------- */
(function () {
  const S = D.solve_energy;
  if (!S || !document.getElementById('sj')) return;
  const SZ = S.sizes, A = S.acc, FT = P.fit[S.card], C = FT.coef;
  /* the segments, left to right: [key, meter, idle | leak | over, fill, its field in energy.json]; the rails keep
     #v1's colours, light for the idle the card draws anyway, full for what the solve adds; no meter is #v1's grey */
  const tint = c => `color-mix(in srgb, ${c} 38%, var(--surface))`;
  const SEGS = [
    ['idle_minion', 'minion rail', 'idle', tint('var(--c1)'), 'rails.minion_w.idle_w ÷ solves_per_s'],
    ['idle_sram', 'SRAM rail', 'idle', tint('var(--c3)'), 'rails.sram_w.idle_w ÷ solves_per_s'],
    ['idle_noc', 'NoC rail', 'idle', tint('var(--c2)'), 'rails.noc_w.idle_w ÷ solves_per_s'],
    ['idle_off', 'no meter', 'idle', 'color-mix(in srgb, var(--ref) 45%, var(--surface))', '(board.sp_avg_idle_w − the rails’ idle_w) ÷ solves_per_s'],
    ['leak', "the leakage's rise", 'leak', 'url(#sj-hatch)', 'board.leak_rise_j_per_solve'],
    ['minion', 'minion rail', 'over', 'var(--c1)', 'rails.minion_w.j_per_solve'],
    ['sram', 'SRAM rail', 'over', 'var(--c3)', 'rails.sram_w.j_per_solve'],
    ['noc', 'NoC rail', 'over', 'var(--c2)', 'rails.noc_w.j_per_solve'],
    ['off', 'no meter', 'over', 'var(--ref)', 'rails.unmetered.j_per_solve: the board over idle less the rails'],
  ];
  /* per size: the rails' joules over idle, the idle, the fit's gap, and the range the rails' stated bias allows the
     part on no meter (a rail reading r(1 + e) for a true r, e in acc.rails, leaves off + R e / (1 + e) on no meter) */
  const X = SZ.map(s => {
    const j = s.j, R = j.minion + j.sram + j.noc, idle = j.idle_minion + j.idle_sram + j.idle_noc + j.idle_off;
    return Object.assign({}, s, {R, idle, noMeter: j.idle_off + j.off, gap: s.fit_off - j.off,
      bias: A.rails.map(e => j.off + R * e / (1 + e)), boardErr: A.board * s.over});
  });
  const ext = a => [Math.min(...a), Math.max(...a)];
  const sz = s => `(${s.size[0]}, ${s.size[1]}, η ${s.size[2]}, m ${num(s.size[3], 0)})`, szShort = s => `(${s.size[0]}, ${s.size[1]}, η ${s.size[2]})`;
  const where = sg => (sg[1] === 'no meter' ? 'on no meter' : `on the ${sg[1]}`);
  const runsDie = s => { const b = ext(s.runs.map(r => r.die_c[0])), u = ext(s.runs.map(r => r.die_c[1]));
    return `the die at ${rng(b[0], b[1], 0, '°C')} before the burst and ${rng(u[0], u[1], 1, '°C')} in it (the mean)`; };
  function segHtml(s, sg) {
    const v = s.j[sg[0]], g = sg[2];
    const head = g === 'idle' ? `idle, ${where(sg)}` : g === 'leak' ? "the leakage's rise" : `added by the solve, ${where(sg)}`;
    let h = `<b>${esc(s.label)} · ${head}</b><br>${num(v, 3)} J per solve: ${pct(v / s.total, 1)} of the solve`;
    if (g === 'over') h += `, ${pct(v / s.over, 1)} of what it adds over idle`;
    if (g === 'idle') h += ` (${num(v / s.s_per_solve, 2)} W over the ${num(s.s_per_solve, 3)} s a solve takes)`;
    if (g === 'leak') h += `: the extra leakage as the die warms (${runsDie(s)}), by the energy catalogue's law`;
    if (sg[0] === 'off') h += `<br>§4.2's fit gives ${num(s.fit_off, 3)} J; the rails' stated bias allows ${rng(s.bias[0], s.bias[1], 3, 'J')}`;
    return h + `<br><span class="small">energy.json: ${esc(sg[4])}${s.runs.length > 1 ? `, the ${word(s.runs.length)} halves summed` : ''}</span>`;
  }
  /* a run's name as #bt gives it ('first half', 'second half'), from the burst_trace block's label for the same run */
  const half = r => { const b = ((D.burst_trace || {}).runs || []).find(q => q.id === r.run); return b ? b.label.split(', ').pop() : r.run; };
  const fitHtml = s => `<b>${esc(s.label)} · §4.2's fit (${esc(S.card)})</b><br>${f(C.minion, 3)} × ${num(s.j.minion, 3)} + ${f(C.sram, 3)} × ${num(s.j.sram, 3)} + ${f(C.noc, 3)} × ${num(s.j.noc, 3)} J = ` +
    `<b>${num(s.fit_off, 3)} J</b> on no meter over idle, against ${num(s.j.off, 3)} J measured: ${num(s.gap, 3)} J apart, ${pct(s.gap / s.R, 1)} of the rails' ${num(s.R, 2)} J. ` +
    `The rails' bias (${sgn(100 * A.rails[0], 0)}% to ${sgn(100 * A.rails[1], 0)}%) allows ${rng(s.bias[0], s.bias[1], 3, 'J')}; the board's ±${num(100 * A.board, 0)}%, another ±${num(s.boardErr, 2)} J` +
    `<br>In watts, the catalogue's method: ${andList(s.runs.map(r => `${num(r.w.off, 2)}\u00a0W measured against ${num(r.w.fit_off, 2)}\u00a0W${s.runs.length > 1 ? ` (${esc(half(r))})` : ''}`))}`;

  /* the controls, the legend (two rows: the idle, then what the solve adds; then the fit's marks) and the readout */
  const VIEWS = [['all', 'The whole solve'], ['over', 'Over idle'], ['j', 'Joules']];
  const ctl = document.getElementById('sj-ctl');
  /* on a narrow screen the chart opens on 'Over idle', where the fit's tick and bracket span tens of pixels, not a few */
  const st = {view: (ctl.clientWidth || window.innerWidth) < 600 ? 'over' : 'all'};
  CK.seg(ctl, {label: 'Show', options: VIEWS, value: st.view, onChange: v => { st.view = v; legView(); fr.redraw(); read.set(dflt()); }});
  const leg = document.getElementById('sj-leg');
  /* each row: its name in a column of its own and the items wrapping beside it, so a second line starts under the first item */
  const legRow = (label, items) => {
    const d = document.createElement('div'); leg.appendChild(d);
    d.style.cssText = 'display: grid; grid-template-columns: max-content 1fr; column-gap: 8px; align-items: baseline; margin: 2px 0';
    const t = document.createElement('span'); t.style.cssText = 'color: var(--ink); font-weight: 600; font-size: 0.82rem'; t.textContent = label;
    const c = document.createElement('div'); d.append(t, c); CK.legend(c, items); c.style.margin = '0';
    return d;
  };
  const item = sg => ({key: sg[0], label: sg[1].replace(/ rail$/, '').replace(/^the /, ''), mark: 'box', color: sg[3]});
  const idleRow = legRow('Idle:', SEGS.filter(sg => sg[2] === 'idle').map(item));
  const addRow = legRow('Added:', SEGS.filter(sg => sg[2] !== 'idle').map(item));
  /* 'Over idle' draws neither the idle nor the leakage's rise: their legend items go with them */
  const leakLi = addRow.querySelectorAll('.ck-li')[SEGS.filter(sg => sg[2] !== 'idle').findIndex(sg => sg[2] === 'leak')];
  const legView = () => { const o = st.view === 'over'; idleRow.style.display = o ? 'none' : 'grid'; if (leakLi) leakLi.style.display = o ? 'none' : ''; };
  legView();
  const fl = legRow("§4.2's fit:", [{key: 'fit', label: 'where the last segment would end', mark: 'line', color: 'var(--ink)'},
    {key: 'bias', label: "the rails' stated bias", mark: 'line', color: 'var(--ink-2)'}]);
  /* the fit's swatch is a tick and the bias's a bracket, as drawn on the bars */
  const sw = fl.querySelectorAll('.ck-li svg');
  if (sw[0]) { sw[0].innerHTML = ''; const l = CK.el('line', {x1: 9, x2: 9, y1: 0, y2: 10, 'stroke-width': 2.5}, sw[0]); l.style.stroke = 'var(--ink)'; }
  if (sw[1]) { sw[1].innerHTML = ''; const p = CK.el('path', {d: 'M2,2 V8 M2,5 H16 M16,2 V8', fill: 'none', 'stroke-width': 1.5}, sw[1]); p.style.stroke = 'var(--ink-2)'; }
  const read = CK.readout('sj-read');
  const dflt = () => (st.view === 'over'
    ? `The rails carry ${rng(...ext(X.map(s => 100 * s.R / s.over)), 0)}% of what each solve adds over idle; the fit puts ${andList(X.map(s => num(s.fit_off, 3)))} J on no meter where the meters show ${andList(X.map(s => num(s.j.off, 3)))} J (${andList(X.map(s => esc(s.label)))}).`
    : st.view === 'j'
      ? `A solve takes ${andList(X.map(s => `${num(s.total, 1)} J`))} of board energy (${andList(X.map(s => esc(s.label)))}), ${andList(X.map(s => `${num(s.noMeter, 2)}`))} J of it on no meter.`
      : `Of the card's ${rng(...ext(SZ.flatMap(s => s.runs.map(r => r.board_idle_w))), 1, 'W')} idle, ${rng(...ext(SZ.flatMap(s => s.runs.map(r => r.board_idle_w - r.rails_idle_w))), 1, 'W')} is on no meter; ` +
        `idle is ${rng(...ext(X.map(s => 100 * s.idle / s.total)), 0)}% of every solve and ${rng(...ext(X.map(s => 100 * s.noMeter / s.total)), 0)}% of each solve is on no meter.`) +
    ' Hover, tap or tab to a segment or a tick.';

  const keys = () => (st.view === 'over' ? SEGS.filter(sg => sg[2] === 'over') : SEGS);
  const den = s => (st.view === 'over' ? s.over : st.view === 'all' ? s.total : 1);
  const offStart = s => (st.view === 'over' ? s.R : s.total - s.j.off);
  const layout = W => { const narrow = W < 600, bh = narrow ? 22 : 26, rowH = 22 + bh + 32, T = 2, B = 46; return {narrow, bh, rowH, T, B, H: T + SZ.length * rowH + B}; };
  function draw(fm) {
    const W = fm.W, G = layout(W), L = 4, R = 26, svg = fm.svg, share = st.view !== 'j';
    /* the hatch for the leakage's rise (the legend's swatch points at it too) */
    const pat = CK.el('pattern', {id: 'sj-hatch', patternUnits: 'userSpaceOnUse', width: 5, height: 5, patternTransform: 'rotate(45)'}, CK.el('defs', {}, svg));
    CK.el('rect', {width: 5, height: 5}, pat).style.fill = 'var(--surface)';
    CK.el('line', {x1: 1, x2: 1, y1: 0, y2: 5, 'stroke-width': 2}, pat).style.stroke = 'var(--ref)';
    const hi = Math.max(1, ...X.map(s => Math.max(offStart(s) + s.fit_off, offStart(s) + s.bias[1]) / den(s)));
    const x = CK.lin(0, share ? hi : hi * 1.01, L, W - R), bottom = G.T + SZ.length * G.rowH;
    const g0 = CK.el('g', {'aria-hidden': 'true'}, svg);
    const ticks = share ? [0, 0.25, 0.5, 0.75, 1] : x.ticks(Math.max(3, Math.round((W - L - R) / 110)));
    /* the grid only beside the bars (the lines of text between them stay clear); 100% of a share is the board's total */
    ticks.forEach(t => {
      X.forEach((s, i) => { const by = G.T + i * G.rowH + 22;
        CK.el('line', {x1: x(t), x2: x(t), y1: by - 4, y2: by + G.bh + 4, class: share && t === 1 ? 'ck-axis' : 'grid-line'}, g0); });
      CK.el('line', {x1: x(t), x2: x(t), y1: bottom + 2, y2: bottom + 6, class: 'ck-axis'}, g0);
    });
    CK.el('line', {x1: L, x2: W - R, y1: bottom + 2, y2: bottom + 2, class: 'ck-axis'}, g0);
    CK.inside(fm, ticks.map(t => CK.txt(g0, x(t), bottom + 19, share ? pct(t) : num(t), 'tick', 'middle')));
    CK.inside(fm, [CK.txt(g0, (L + W - R) / 2, G.H - 6, st.view === 'over' ? "share of the board's joules over idle"
      : share ? "share of one solve's board energy, idle included" : 'joules per solve', 'lab', 'middle')]);
    const nodes = [], per = keys().length + 1;
    X.forEach((s, i) => {
      const y0 = G.T + i * G.rowH, by = y0 + 22, bh = G.bh, d = den(s);
      const nm = CK.txt(g0, L, y0 + 14, `${s.label} · ${num(st.view === 'over' ? s.over : s.total, st.view === 'over' ? 2 : 1)} J ${st.view === 'over' ? 'over idle' : 'per solve'}`, 'lab-strong');
      if (!G.narrow) CK.txt(g0, W - R, y0 + 14, `${sz(s)} · ${num(s.s_per_solve, 3)} s a solve${s.runs.length > 1 ? ', two halves' : ''}`, 'tick', 'end');
      else { const ts = CK.el('tspan', {class: 'tick', dx: 6}, nm); ts.style.fontWeight = '400'; ts.textContent = szShort(s); }
      let x0 = 0;
      keys().forEach(sg => {
        const v = s.j[sg[0]] / d, xa = x(x0), xb = x(x0 + v), w = xb - xa, g = CK.el('g', {}, svg);
        const r = CK.el('rect', {x: xa, y: by, width: Math.max(0.75, w), height: bh}, g);
        r.style.fill = sg[3]; r.style.stroke = 'var(--surface)'; r.style.strokeWidth = '1';
        if (w >= 38 && sg[2] !== 'leak') { const t = CK.txt(g, (xa + xb) / 2, by + bh / 2 + 4, share ? pct(v) : num(s.j[sg[0]], 2), 'lab-strong', 'middle'); t.style.fill = inkOn(sg[3]); t.setAttribute('aria-hidden', 'true'); }
        CK.el('rect', {x: (xa + xb) / 2 - Math.max(w, 8) / 2, y: by - 3, width: Math.max(w, 8), height: bh + 6, class: 'ck-hit'}, g);
        const html = segHtml(s, sg);
        CK.tip(fm, g, html); g._desc = html; nodes.push(g);
        x0 += v;
      });
      /* the fit's tick and the rails' bracket, both measured from where the last segment starts */
      const o = offStart(s), xt = x((o + s.fit_off) / d), b0 = x((o + s.bias[0]) / d), b1 = x((o + s.bias[1]) / d), yb = by + bh + 6;
      const gf = CK.el('g', {}, svg);
      const br = CK.el('path', {d: `M${b0},${yb - 3} V${yb + 3} M${b0},${yb} H${b1} M${b1},${yb - 3} V${yb + 3}`, fill: 'none', 'stroke-width': 1.5}, gf);
      br.style.stroke = 'var(--ink-2)';
      const tk = CK.el('line', {x1: xt, x2: xt, y1: by - 5, y2: by + bh + 9, 'stroke-width': 2.5}, gf); tk.style.stroke = 'var(--ink)';
      if (i === 0) CK.txt(gf, xt + 4, by + bh / 2 + 4, 'fit', 'lab-strong');
      CK.el('rect', {x: Math.min(xt, b0) - 6, y: by - 6, width: Math.max(xt, b1) - Math.min(xt, b0) + 12, height: bh + 16, class: 'ck-hit'}, gf);
      const fh = fitHtml(s);
      CK.tip(fm, gf, fh); gf._desc = fh; nodes.push(gf);
      /* one line under each bar: what the view is for */
      const line = st.view === 'over' ? `on no meter ${num(s.j.off, 3)} J (${pct(s.j.off / s.over, 1)}); the fit ${num(s.fit_off, 3)} J`
        : st.view === 'j' ? `idle ${num(s.idle, 2)} J · on no meter ${num(s.noMeter, 2)} J`
          : `idle ${pct(s.idle / s.total)} · on no meter ${pct(s.noMeter / s.total)}`;
      CK.txt(g0, L, by + bh + 22, line, 'tick');
    });
    nodes.forEach(n => n.addEventListener('pointerenter', () => read.set(n._desc)));
    CK.keynav(fm, nodes, {onFocus: n => read.set(n._desc),
      step: (k, K) => (K === 'ArrowDown' ? (k + per < nodes.length ? k + per : k) : K === 'ArrowUp' ? (k - per >= 0 ? k - per : k) : null)});
  }
  const fr = CK.frame('sj', {height: W => layout(W).H, minW: 300, maxW: 1100, label: "One solve's board energy by meter, for three sizes of sparse parity on " + S.card + ", with §4.2's fit", draw});
  read.set(dflt());

  /* the caption's numbers and the note under the chart */
  const shareOf = (a, b) => rng(...ext(X.map(s => 100 * a(s) / b(s))), 0) + '%';
  setHTML('sj-card', `${esc(S.card)} at ${andList(S.mhz.map(v => num(v, 0)))} MHz`);
  setHTML('sj-sizes', spSizes());
  setHTML('sj-bias', `${sgn(100 * A.rails[0], 0)}% to ${sgn(100 * A.rails[1], 0)}%`);
  setHTML('sj-cap-c', `The reducer's ±${num(100 * A.unmetered, 0)}% on that segment was checked where it was about ${fracWord((A.stub_unmetered_share[0] + A.stub_unmetered_share[1]) / 2)} of what a solve adds, ` +
    `not ${rng(...ext(X.map(s => 100 * s.j.off / s.over)), 0)}% here (<a href="#sj-note">how far to trust it</a>).` +
    (st.view === 'over' ? ' On a narrow screen the chart opens on “Over idle”, where the tick and the bracket are wider.' : ''));
  setHTML('sj-cap-a', `Idle is ${shareOf(s => s.idle, s => s.total)} of every solve and about half of it is on no meter, ` +
    `so ${shareOf(s => s.noMeter, s => s.total)} of each solve is on no meter; the rails carry ${shareOf(s => s.R, s => s.over)} of what the solve adds.`);
  setHTML('sj-cap-b', `the fit puts more on no meter than the meters show, by ${rng(...ext(X.map(s => 100 * s.gap / s.R)), 1)}% of the rails' joules, ` +
    `about the top of that bias, so this workload cannot tell the fit's error from the meters'.`);
  setHTML('sj-note', `What a solve adds on no meter is the board's joules over idle less the rails', a small difference of two larger numbers. ` +
    `The board's is claimed to ±${num(100 * A.board, 0)}% (${andList(X.map(s => num(s.boardErr, 2)))} J here) and the rails' to ${sgn(100 * A.rails[0], 0)}% to ${sgn(100 * A.rails[1], 0)}%; ` +
    `the reducer's ±${num(100 * A.unmetered, 0)}% on the difference was checked on test doubles where it was ${rng(100 * A.stub_unmetered_share[0], 100 * A.stub_unmetered_share[1], 0)}% of what a solve adds, ` +
    `against ${rng(...ext(X.map(s => 100 * s.j.off / s.over)), 1)}% here, so it does not carry over: the bracket uses the rails' bias instead. ` +
    `The fit is applied without its DRAM term, since every run staged its operands in the shires' scratchpads. The rails here are integrated over the burst and its tail; ` +
    `by the catalogue's own method in watts (the board's plateau over idle less the rails' plateaus) the comparison is the same: ` +
    andList(X.map(s => s.runs.length > 1 ? s.runs.map((r, k) => `${k ? 'its' : esc(s.label) + "'s"} ${esc(half(r))} ${num(r.w.off, 2)} W against the fit's ${num(r.w.fit_off, 2)}`).join(' and ')
      : `${esc(s.label)} ${num(s.runs[0].w.off, 2)} W against the fit's ${num(s.runs[0].w.fit_off, 2)}`)) +
    `; the fit's residual rms over the catalogue is ${f(FT.rms_w, 2)} W. Data: each run's <code>energy.json</code> (<code>workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy</code>), ` +
    `through <code>tools/ettelem/sync_hub_data.py</code> (the <code>solve_energy</code> block).`);
})();

/* ---------- the improvement ladder: every rung drawn once; the status buttons and the text filter hide rows ---------- */
(function () {
  let filter = 'all';
  const fbox = document.getElementById('impfilters'), t = document.getElementById('imptab');
  const opts = [['all', 'all rungs'], ['done', 'done'], ['works_now', 'works now'], ['needs_tooling', 'tooling or lab hardware'], ['needs_fw_change', 'firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon'], ['ask_team', 'ask the team']];
  let group = null;
  /* every rung is a link target as #rung-N (its number); a rung with an id is one too (the chip diagram links its
     dashed parts to #ask-… and #exp-… rows, and the memory-levels page its unknown parts); r.diagram names the part
     of the chip diagram the rung would settle, and r.levels the views of the memory-levels page it would settle, as [hash, label] pairs (#l3/cell: a level and a scale,
     or a level and an access) */
  t.innerHTML = '<thead><tr><th style="width:23%">Rung</th><th style="width:28%">What it adds</th><th style="width:15%">Cost</th><th style="width:24%">What changes in the numbers</th><th style="width:10%">Status</th></tr></thead><tbody>' +
    D.improvements.map((r, i) => { const g = r.group !== group ? `<tr class="grp"><td colspan="5"><b>${esc(r.group)}</b></td></tr>` : ''; group = r.group;
      const cap = !r.adds || /\.$/.test(r.adds), see = r.row ? `${r.adds ? ' ' : ''}<a href="#${ladId(r.row)}" class="seerow" data-row="${esc(r.row)}">${cap ? 'See' : 'see'} §2: ${esc(r.row)}</a>` : '';
      const dg = r.diagram ? ` <a href="${PAGES}et-soc1-chip-diagram#honest">Chip diagram: ${esc(r.diagram)}</a>.` : '';
      const lv = r.levels ? ` Memory levels: ${r.levels.map(([h, t]) => `<a href="${PAGES}et-soc1-memory-levels#${esc(h)}">${esc(t)}</a>`).join(', ')}.` : '';
      return g + `<tr data-i="${i}"${r.id ? ` id="${esc(r.id)}"` : ''}><td class="lvl"><span id="rung-${r.rung}">${r.rung}.</span> ${esc(r.what)}${r.done ? ' <span class="verif confirmed">done</span>' : ''}</td><td>${rk(lk(esc(fill(r.adds))))}${see}${dg}${lv}</td><td class="small">${rk(esc(r.cost))}</td><td>${rk(lk(esc(fill(r.effect))))}</td><td class="inl">${chip(r.status)}</td></tr>`; }).join('') + '</tbody>';
  t.querySelectorAll('a.seerow').forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); goRow(a.dataset.row); }));
  CK.stackTable(t);
  const sorter = sortGrouped(t, {filter: true, filterLabel: 'Filter rungs', noun: 'rungs'});
  fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('');
  fbox.querySelectorAll('button').forEach(b => { b.onclick = () => {
    filter = b.dataset.k;
    fbox.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    t.querySelectorAll('tr[data-i]').forEach(tr => { const r = D.improvements[+tr.dataset.i]; tr.classList.toggle('st-off', !(filter === 'all' || (filter === 'done' ? r.done : r.status === filter))); });
    sorter.fix();
  }; });
  /* a link to a rung (#ask-noc-docs from the chip diagram, or #rung-N for any rung) shows every rung, then centres and flashes that row */
  const goRung = () => {
    const id = decodeURIComponent(location.hash.slice(1)), el = id && document.getElementById(id), tr = el && t.contains(el) ? el.closest('tr[data-i]') : null;
    if (!tr) return;
    if (tr.classList.contains('st-off')) fbox.querySelector('button[data-k="all"]').click();
    tr.scrollIntoView({block: 'center', behavior: CK.reduced ? 'auto' : 'smooth'});
    tr.classList.add('flash'); setTimeout(() => tr.classList.remove('flash'), 1800);
  };
  addEventListener('hashchange', goRung);
  if (document.readyState === 'complete') goRung(); else addEventListener('load', goRung);
})();

/* ---------- the sessions table (§7) ---------- */
/* Raw-data paths are stored in full and shown without the common docs/reports/data/ prefix; directories link to
   GitHub's tree view, files to the blob view. */
const rawLink = p => { const PRE = 'docs/reports/data/'; return `<a href="${REPO}${p.path.endsWith('/') ? 'tree' : 'blob'}/main/${p.path}"><code>${esc(p.path.startsWith(PRE) ? p.path.slice(PRE.length) : p.path)}</code></a>${p.note ? ' (' + esc(p.note) + ')' : ''}`; };
(function () {
  const t = document.getElementById('sessionstab');
  t.innerHTML = '<thead><tr><th style="width:7%">Session</th><th style="width:9%">When</th><th style="width:8%">Card</th><th style="width:28%">What it measured</th><th style="width:14%">Instruments</th><th style="width:21%">Raw data</th><th style="width:13%">Reports</th></tr></thead><tbody>' +
    D.sessions.map(r => `<tr><td class="lvl" data-sort="${+((r.id.match(/\d+/) || [0])[0])}">${esc(r.id)}</td><td class="small" data-sort="${parseWhen(r.when)[0].toFixed(4)}">${esc(r.when)}</td><td class="small">${esc(r.card)}</td><td>${esc(r.what)}</td><td class="small">${esc(r.instruments)}</td><td class="small">${r.data.map(rawLink).join('<br>')}</td><td class="small">${r.reports.map(x => `<a href="${x.url}">${esc(x.title)}</a>`).join('<br>')}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
  sortGrouped(t, {filter: true, filterLabel: 'Filter sessions', noun: 'sessions'});  /* Session sorts by E-number, When by start time */
  setHTML('nsess', String(D.sessions.length));
})();

/* ---------- V2: the reports and sessions map (§1) ---------- */
/* The cards a session ran on, read from its free-text card field (D.sessions[].card): card ids and labels
   (aifoundry2, aifoundry1-c1, "aifoundry1 card 1"; a bare "aifoundry1" is that machine), the registry's short names
   (a2, a1c1), "both" (the two cards measured before version 3), "all three cards" (the version-3 campaign's cards,
   amendment A4) and "all three" alone (E21's "all three machines"). No card ("—") is an analysis. The cards come back
   in registry order, any other name after them. */
const V3CARDS = CK.cards.filter(c => c.id !== 'aifoundry1-c0').map(c => c.id);
function cardsOfText(str) {
  const t = String(str || '').toLowerCase(), out = [], add = id => { if (!out.includes(id)) out.push(id); };
  const known = id => CK.cards.some(c => c.id === id);
  for (const m of t.matchAll(/aifoundry(\d)(?:-c(\d)|\s+card\s+(\d))?/g)) add(CK.card(m[2] || m[3] ? `aifoundry${m[1]}-c${m[2] || m[3]}` : `aifoundry${m[1]}`).id);
  for (const m of t.matchAll(/\b(a\d)-?(c\d)?\b/g)) { const id = CK.card(m[1] + (m[2] || '')).id; if (known(id)) add(id); }
  if (/\bboth\b/.test(t)) ['aifoundry2', 'aifoundry3'].forEach(add);
  if (/\b(?:all three|all 3|three|all) cards\b/.test(t)) V3CARDS.forEach(add);
  else if (/\ball three\b/.test(t)) ['aifoundry2', 'aifoundry3', 'aifoundry1'].forEach(add);
  return CK.cardsIn(out);
}
(function () {
  const GROUPS = [['This hub', 'Hub', 'var(--ref)'], ["Synthesis: the set's measurements in one picture", 'Synthesis', 'var(--c2)'], ['Energy and power', 'Energy and power', 'var(--c1)'], ['Contention and moving data', 'Contention', 'var(--c3)'],
    ['Memory and compute baselines, 18–19 September', 'Baselines', 'var(--c4)'], ['Research and exploratory', 'Research', 'var(--c5)'],
    ['Briefs: analysis, no new measurements', 'Briefs', 'var(--c7)']];
  const gOf = Object.fromEntries(GROUPS.map(([k, s, c], i) => [k, {s, c, i}]));
  const base = u => u.split('#')[0];
  const REP = D.reports.map((r, i) => ({...r, key: 'r' + i, kind: 'report', grp: r.group || 'This hub', day: +r.pub.slice(8, 10)}));
  const repOf = u => (u.startsWith('#') ? REP[0] : REP.find(r => base(r.url) === base(u)));
  const byShort = s => REP.find(r => r.short === s);
  const SES = D.sessions.map((s, i) => { const [t0, t1] = parseWhen(s.when); return {...s, key: 's' + i, kind: 'session', t0, t1, cards: cardsOfText(s.card), name: s.id === '—' ? 'before E1' : s.id,
    reps: [...new Set(s.reports.map(x => repOf(x.url)).filter(Boolean))]}; }).filter(s => isFinite(s.t0));
  /* one lane (a column on a phone) per card any session names, in registry order, coloured from the registry */
  const LANES = CK.cardsIn(SES.flatMap(s => s.cards));
  const NDAYS = Math.max(7, ...REP.map(r => r.day - 17), ...SES.map(s => Math.ceil(s.t1)));  // from 18 September to the newest report or session
  const colShort = id => { const c = CK.card(id); return c.short !== c.id ? c.short : id.replace(/^aifoundry/, 'a'); };
  const SUP = D.superseded.map((s, i) => ({...s, key: 'e' + i, fromR: byShort(s.from), to: s.to.map(t => ({...t, r: byShort(t.report)}))}));
  const st = {sel: null, card: 'pooled', sup: true};
  const byKey = k => REP.find(r => r.key === k) || SES.find(s => s.key === k);
  setHTML('map-head', `${REP.length} reports · ${SES.length} sessions · ${SUP.length} superseded numbers`);
  const ctl = document.getElementById('map-ctl'), box = () => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.cardSeg(box(), {cards: LANES, pooled: true, bus: 'map-card', value: st.card, onChange: v => { st.card = v; fr.redraw(); }});  /* its own bus: a filter, not §4.2's card */
  const cb = box(); cb.innerHTML = '<label class="chk"><input type="checkbox" id="map-sup" checked> Show superseded numbers</label>';
  document.getElementById('map-sup').addEventListener('change', ev => { st.sup = ev.target.checked; fr.redraw(); });
  const panel = document.getElementById('map-panel');
  const showCard = s => st.card === 'pooled' || !s.cards.length || s.cards.includes(st.card);
  const laneCards = () => LANES.filter(c => st.card === 'pooled' || c === st.card);
  function related(k) {
    const out = new Set([k]);
    if (!k) return out;
    const n = byKey(k);
    if (n.kind === 'session') n.reps.forEach(r => out.add(r.key));
    else {
      SES.filter(s => s.reps.includes(n)).forEach(s => out.add(s.key));
      SUP.forEach(e => { if (e.fromR === n || e.to.some(t => t.r === n)) { out.add(e.key); out.add(e.fromR.key); e.to.forEach(t => out.add(t.r.key)); } });
    }
    return out;
  }
  const btn = n => `<button type="button" class="linkbtn" data-k="${n.key}">${esc(n.kind === 'session' ? n.name : n.short)}</button>`;
  function fillPanel() {
    const n = st.sel && byKey(st.sel);
    if (!n) {
      panel.innerHTML = `<h4>Select a report or a session</h4><p class="small">Click or tap a mark, or tab to the map and use the arrow keys and Enter. A report shows what it established, the sessions behind it and the numbers that moved to or from it; a session shows what it measured and its raw data.</p>`;
      return;
    }
    if (n.kind === 'report') {
      const ses = SES.filter(s => s.reps.includes(n)), out = SUP.filter(e => e.fromR === n), inn = SUP.filter(e => e.to.some(t => t.r === n));
      panel.innerHTML = `<h4><a href="${n.url}">${esc(n.title)}</a></h4><p class="small">${esc(gOf[n.grp].s)} · first published ${n.day} September · ${esc(n.date)}</p><dl>` +
        `<dt>What it established</dt><dd>${fill(n.what)}</dd><dt>Instruments</dt><dd>${esc(n.instruments)}</dd>` +
        (ses.length ? `<dt>Sessions behind it</dt><dd>${ses.map(btn).join(' ')}</dd>` : '') +
        (out.length ? `<dt>Superseded here: now held by a later page</dt><dd>${out.map(e => `${esc(e.what)} → ${e.to.map(t => `<a href="${t.r.url}#${t.anchor}">${esc(t.label)}</a>`).join(', ')}`).join('<br>')}</dd>` : '') +
        (inn.length ? `<dt>Current source for</dt><dd>${inn.map(e => `${esc(e.what)} (first given in ${btn(e.fromR)})`).join('<br>')}</dd>` : '') + '</dl>';
    } else {
      panel.innerHTML = `<h4>${esc(n.name)}</h4><p class="small">${esc(n.when)} · ${esc(n.card)}</p><dl><dt>What it measured</dt><dd>${esc(n.what)}</dd>` +
        `<dt>Instruments</dt><dd>${esc(n.instruments)}</dd><dt>Raw data</dt><dd>${n.data.map(rawLink).join('<br>')}</dd>` +
        `<dt>Reports it fed</dt><dd>${n.reports.map(x => `<a href="${x.url}">${esc(x.title)}</a>`).join('<br>')}</dd></dl>`;
    }
    panel.querySelectorAll('button.linkbtn').forEach(b => b.addEventListener('click', () => select(b.dataset.k)));
  }
  function select(k) { st.sel = st.sel === k ? null : k; fr.redraw(); fillPanel(); }
  let els = {};
  function applySel() {
    const R = related(st.sel);
    Object.entries(els).forEach(([k, e]) => {
      const on = !st.sel || R.has(k) || (e.edge && R.has(e.a) && R.has(e.b));
      e.el.classList.toggle('dim', !on);
      if (e.edge && e.kind === 'feed') { e.el.style.stroke = st.sel && on ? 'var(--ink-2)' : 'var(--axis)'; e.el.style.strokeWidth = st.sel && on ? '1.8' : '1.1'; }
      if (!e.edge) e.el.classList.toggle('map-sel', k === st.sel);
    });
  }
  function measure(svg, s, cls) { const t = CK.txt(svg, -999, -999, s, cls); const w = t.getComputedTextLength(); t.remove(); return w || s.length * 6.5; }
  function draw(f) {
    const vert = f.W < 600, W = vert ? f.W - 16 : f.W, svg = f.svg; els = {};
    const defs = CK.el('defs', {}, svg), mk = CK.el('marker', {id: 'map-arr', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse'}, defs);
    const ap = CK.el('path', {d: 'M0,0 L10,5 L0,10 Z'}, mk); ap.style.fill = 'var(--ink-2)';  /* not a card's colour */
    const gE = CK.el('g', {}, svg), gN = CK.el('g', {}, svg), nodes = [];
    const pos = {};  // key -> {x, y, w, h}
    const ses = SES.filter(showCard);
    if (!vert) {
      const L = 112, R = 10, T = 30, x = t => L + t / NDAYS * (W - L - R), rowS = 19, rowR = 26;
      for (let d = 0; d <= NDAYS; d++) { CK.el('line', {x1: x(d), x2: x(d), y1: T - 6, y2: f.H - 8, class: 'grid-line'}, gE); if (d < NDAYS) CK.txt(gE, x(d + 0.5), T - 12, `${18 + d} Sep`, 'tick', 'middle'); }
      let y = T + 4;
      /* a lane per card, then the analyses; a session on several cards has a box in each of their lanes */
      laneCards().concat(['none']).forEach(ln => {
        const items = ses.filter(s => (ln === 'none' ? !s.cards.length : s.cards.includes(ln))).sort((p, q) => p.t0 - q.t0), rows = [];
        if (!items.length) return;
        items.forEach(s => { const x0 = x(s.t0), w = Math.max(x(s.t1) - x0, measure(svg, s.name, 'tick') + 10); let k = rows.findIndex(e => e + 3 <= x0); if (k < 0) { rows.push(0); k = rows.length - 1; } rows[k] = x0 + w;
          (pos[s.key] = pos[s.key] || {boxes: []}).boxes.push({x: x0, y: y + k * rowS, w, h: 15, cards: ln === 'none' ? [] : [ln]}); });
        const band = CK.el('rect', {x: 0, y: y - 2, width: L - 8, height: rows.length * rowS, rx: 4}, gE);
        band.style.fill = `color-mix(in srgb, ${ln === 'none' ? 'var(--ref)' : CK.card(ln).color} ${ln === 'none' ? 10 : 12}%, transparent)`;
        const lab = ln === 'none' ? 'analysis' : CK.card(ln).label;
        CK.txt(gE, 6, y + 11, measure(svg, lab, 'lab') <= L - 16 ? lab : CK.card(ln).id, 'lab');
        y += rows.length * rowS + 4;
      });
      ses.forEach(s => { const p = pos[s.key]; if (p) Object.assign(p, p.boxes.reduce((a, b) => (b.y > a.y ? b : a))); });  /* curves leave from the lowest box */
      y += 22;
      CK.el('line', {x1: 0, x2: W, y1: y - 12, y2: y - 12, class: 'ck-axis'}, gE);
      GROUPS.forEach(([gk, gs, gc]) => {
        const items = REP.filter(r => r.grp === gk).sort((p, q) => p.day - q.day), rows = [];
        if (!items.length) return;
        items.forEach(r => { const w = measure(svg, r.short, 'tick') + 16, x0 = Math.min(W - R - w, Math.max(L, x(r.day - 18 + 0.5) - w / 2)); let k = rows.findIndex(e => e + 4 <= x0); if (k < 0) { rows.push(0); k = rows.length - 1; } rows[k] = x0 + w; pos[r.key] = {x: x0, y: y + k * rowR, w, h: 20}; });
        CK.el('rect', {x: 2, y: y + 2, width: 4, height: rows.length * rowR - 8, rx: 2, fill: gc}, gE); CK.txt(gE, 11, y + 14, gs, 'lab-strong');
        y += rows.length * rowR + 6;
      });
    } else {
      /* a column per card; a session spans its cards' columns (one box per run of adjacent columns), an analysis all */
      const cols = laneCards(), n = Math.max(1, cols.length), lw = n <= 2 ? 58 : Math.max(30, Math.floor((0.56 * W - 44) / n) - 4), bow = n <= 2 ? 34 : 22;
      const T = 16, dayH = 158, xT = 40, xA = xT + 4, colX = i => xA + i * (lw + 4), xR = colX(n) + 8, y = t => T + t * dayH;
      for (let d = 0; d <= NDAYS; d++) { CK.el('line', {x1: 0, x2: W, y1: y(d), y2: y(d), class: 'grid-line'}, gE); if (d < NDAYS) { CK.txt(gE, 2, y(d) + 14, `${18 + d}`, 'lab-strong'); CK.txt(gE, 2, y(d) + 28, 'Sep', 'tick'); } }
      cols.forEach((c, i) => CK.txt(gE, colX(i) + lw / 2, T - 4, colShort(c), 'tick', 'middle'));
      const bottom = cols.map(() => 0);
      ses.slice().sort((p, q) => p.t0 - q.t0).forEach(s => {
        const idx = s.cards.length ? cols.map((c, i) => (s.cards.includes(c) ? i : -1)).filter(i => i >= 0) : cols.map((c, i) => i);
        if (!idx.length) return;
        const h = Math.min(40, Math.max(16, y(s.t1) - y(s.t0))), y0 = Math.max(y(s.t0), ...idx.map(i => bottom[i] + 2)), runs = [];
        idx.forEach(i => { bottom[i] = y0 + h; const r = runs[runs.length - 1]; if (r && r[1] === i - 1) r[1] = i; else runs.push([i, i]); });
        const boxes = runs.map(([i0, i1]) => ({x: colX(i0), y: y0, w: (i1 - i0 + 1) * lw + (i1 - i0) * 4, h, cards: s.cards.length ? cols.slice(i0, i1 + 1) : []}));
        pos[s.key] = Object.assign({boxes}, boxes[boxes.length - 1]);  /* curves leave from the rightmost box */
      });
      const byDay = {};
      REP.slice().sort((p, q) => p.day - q.day || gOf[p.grp].i - gOf[q.grp].i).forEach(r => { const k = (byDay[r.day] = (byDay[r.day] || 0) + 1) - 1; pos[r.key] = {x: xR, y: y(r.day - 18) + 6 + k * 26, w: Math.min(W - xR - bow, measure(svg, r.short, 'tick') + 16), h: 20}; });
    }
    /* session -> report curves */
    ses.forEach(s => s.reps.forEach(r => {
      const a = pos[s.key], b = pos[r.key]; if (!a || !b) return;
      const d = vert ? `M${a.x + a.w},${a.y + a.h / 2} C${a.x + a.w + 30},${a.y + a.h / 2} ${b.x - 30},${b.y + b.h / 2} ${b.x},${b.y + b.h / 2}`
        : `M${a.x + a.w / 2},${a.y + a.h} C${a.x + a.w / 2},${a.y + a.h + 40} ${b.x + b.w / 2},${b.y - 40} ${b.x + b.w / 2},${b.y}`;
      const p = CK.el('path', {d, fill: 'none', class: 'mapedge'}, gE); p.style.stroke = 'var(--axis)'; p.style.strokeWidth = '1.1';
      els[s.key + '>' + r.key] = {el: p, edge: true, kind: 'feed', a: s.key, b: r.key};
    }));
    /* supersession arrows */
    const drawn = new Set();
    if (st.sup) SUP.forEach(e => e.to.forEach((t, j) => {
      const a = pos[e.fromR.key], b = pos[t.r.key], pair = e.fromR.key + '>' + t.r.key; if (!a || !b || a === b || drawn.has(pair)) return;
      drawn.add(pair);
      let d;
      if (vert) { const x0 = a.x + a.w, x1 = b.x + b.w, bow = Math.min(W - 4, Math.max(x0, x1) + 18 + 6 * j); d = `M${x0},${a.y + a.h / 2} C${bow},${a.y + a.h / 2} ${bow},${b.y + b.h / 2} ${x1 + 2},${b.y + b.h / 2}`; }
      else { const ax = a.x + a.w / 2, bx = b.x + b.w / 2, ay = a.y + (b.y > a.y ? a.h : 0), by = b.y + (b.y > a.y ? 0 : b.h), my = (ay + by) / 2 + (Math.abs(by - ay) < 8 ? 34 : 0); d = `M${ax},${ay} C${ax},${my} ${bx},${my} ${bx},${by}`; }
      const p = CK.el('path', {d, fill: 'none', class: 'mapedge', 'stroke-dasharray': '5 3', 'stroke-width': 1.5, 'marker-end': 'url(#map-arr)'}, gE); p.style.stroke = 'var(--ink-2)';
      els[e.key + '/' + j] = {el: p, edge: true, kind: 'sup', a: e.fromR.key, b: t.r.key};
    }));
    /* nodes: sessions, then reports */
    const addNode = (n, tipHtml, paint) => {
      const p = pos[n.key], g = CK.el('g', {class: 'mapnode'}, gN);
      paint(g, p);
      CK.tip(f, g, tipHtml, {role: 'button'});
      g.addEventListener('click', () => select(n.key));
      g.addEventListener('keydown', ev => { if (ev.key === 'Escape' && st.sel) select(st.sel); });
      els[n.key] = {el: g}; nodes.push(g);
    };
    const mix = c => `color-mix(in srgb, ${c} 30%, var(--surface))`, paint = (e, fill, stroke) => { e.style.fill = fill; if (stroke) e.style.stroke = stroke; return e; };
    /* the tooltip shows a session's first sentence; a click shows the rest in the panel */
    const brief = s => { const m = s.match(/^[\s\S]{30,}?[.?](?=\s+[A-Z0-9])/); return m ? m[0] + ' …' : s; };
    ses.slice().sort((p, q) => p.t0 - q.t0).forEach(s => addNode(s, `<b>${esc(s.name)}</b> · ${esc(s.when)} · ${s.cards.length ? esc(s.card) : 'analysis, no card'}<br>${esc(brief(s.what))}`, (g, p) => {
      p.boxes.forEach(b => {
        if (!b.cards.length) paint(CK.el('rect', {x: b.x, y: b.y, width: b.w, height: b.h, rx: 3, 'stroke-width': 1.2, 'stroke-dasharray': '3 2'}, g), 'var(--surface)', 'var(--ref)');
        else if (b.cards.length === 1) paint(CK.el('rect', {x: b.x, y: b.y, width: b.w, height: b.h, rx: 3, 'stroke-width': 1.2}, g), mix(CK.card(b.cards[0]).color), CK.card(b.cards[0]).color);
        else {  /* a box across several cards' columns: each card's part in its tint, one outline */
          const k = b.cards.length;
          b.cards.forEach((c, i) => paint(CK.el('rect', {x: b.x + i * b.w / k, y: b.y, width: b.w / k, height: b.h}, g), mix(CK.card(c).color)));
          paint(CK.el('rect', {x: b.x, y: b.y, width: b.w, height: b.h, rx: 3, 'stroke-width': 1}, g), 'none', 'var(--ink-2)');
        }
        CK.el('rect', {x: b.x, y: b.y, width: b.w, height: b.h, class: 'ck-hit'}, g);
        const t = CK.txt(g, b.x + 5, b.y + Math.min(b.h, 15) / 2 + 4, s.name, 'tick'); t.style.fill = 'var(--ink)'; t.style.fontWeight = '600';
        if (vert && /[,–]/.test(s.name) && 1.1 * measure(svg, s.name, 'tick') + 8 > b.w) t.textContent = s.name.split(/[,–]/)[0] + '…';  /* a narrow column: the first ID; the tooltip has all */
      });
    }));
    REP.slice().sort((p, q) => p.day - q.day || gOf[p.grp].i - gOf[q.grp].i).forEach(r => addNode(r, `<b>${esc(r.title)}</b><br>first published ${r.day} September · ${esc(gOf[r.grp].s)}`, (g, p) => {
      const c = gOf[r.grp].c;
      CK.el('rect', {x: p.x, y: p.y, width: p.w, height: p.h, rx: 10, 'stroke-width': 1.6, fill: `color-mix(in srgb, ${c} 16%, var(--surface))`, stroke: c}, g);
      const t = CK.txt(g, p.x + 8, p.y + 14, r.short, 'tick'); t.style.fill = 'var(--ink)';
    }));
    CK.keynav(f, nodes, {onEnter: (n, k) => { const key = Object.keys(els).find(q => els[q].el === n); if (key) select(key); }});
    applySel();
  }
  const height = W => {
    if (W < 600) return 16 + NDAYS * 158 + 12;
    const lanesRows = 6, repRows = 12;  // an upper bound; the frame is resized after the first draw
    return 30 + lanesRows * 19 + 40 + repRows * 26 + 40;
  };
  const fr = CK.frame('map-frame', {height, minW: 300, maxW: 1100, label: 'Every session on a timeline by card, the reports each fed, and where superseded numbers moved', draw: f => {
    draw(f);
    if (f.W >= 600) {  // shrink the frame to what the layout used
      const bb = f.svg.getBBox(), H = Math.ceil(bb.y + bb.height + 10);
      if (Math.abs(H - f.H) > 4) { f.H = H; f.svg.setAttribute('viewBox', `0 0 ${f.W} ${H}`); f.svg.setAttribute('height', H); }
    } else {  // days run down inside a scrolling frame: leave its scrollbar room
      const W = f.W - 16; f.svg.setAttribute('viewBox', `0 0 ${W} ${f.H}`); f.svg.setAttribute('width', W); f.svg.style.width = W + 'px';
    }
  }});
  fillPanel();
})();

/* ---------- the claims scoreboard (§1): each page's claims by verdict, or by the cards whose data they rest on ----------
   D.claims_status comes from tools/ettelem/sync_hub_data.py: verdicts [[key, label, meaning]] and series[], each
   {label, short, note, pages: {<slug>: {claims, verdict: {<key>: n}, cards: {<card ids joined by +, or none>: n}}}}.
   Every series is drawn, one bar per page and series, in the data's order: the claims after the version-3 campaign
   (complete, 25-26 September) first, then the plan's verdicts before it. */
(function () {
  const C = D.claims_status, SER = C.series, S = SER.length, VD = C.verdicts;
  const GREY = 'color-mix(in srgb, var(--ref) 55%, var(--surface))';
  /* verdict colours, strongest evidence first (checked for colour-blind separation of neighbours, light and dark:
     the dataviz validator on c3, c2, c1, c4, c7, c5 passes every adjacent pair against both surfaces, 26 Sep);
     "not a measurement" is neutral grey. "a test behind it failed" (any pre-registered test covering the claim failed in some part) exists only after the campaign.
     A verdict not listed here draws in --ref. */
  const VCOL = {'PROVEN': 'var(--c3)', 'CORRECTED': 'var(--c2)', 'CARD-DIFFERENT': 'var(--c1)', 'ONE-CARD': 'var(--c4)', 'UNDER-REPLICATED': 'var(--c7)', 'WITHIN-NOISE': 'var(--c5)', 'NOT-EMPIRICAL': GREY};
  const VLAB = Object.fromEntries(VD.map(v => [v[0], v[1]]));
  const slugOf = u => u.split('#')[0].replace(/\/$/, '').split('/').pop();
  const REP = D.reports.map(r => ({...r, slug: slugOf(r.url)}));
  const inAny = slug => SER.some(s => s.pages[slug]);
  const extra = [...new Set(SER.flatMap(s => Object.keys(s.pages)))].filter(k => !REP.some(r => r.slug === k)).sort();
  const PAGES = REP.filter(r => inAny(r.slug)).concat(extra.map(k => ({slug: k, short: k, title: k, url: 'https://spacesheep.dev/@yaroslavvb/' + k})));
  const HUB = REP[0].slug;
  const st = {view: 'verdict', scale: 'n'};
  /* the categories of the current view, in order, each {key, label, fills: [colours]} (a card set: one stripe a card) */
  const setCards = k => (k === 'none' ? [] : k.split('+'));
  const cardsLab = ids => (ids.length ? ids.map(c => CK.card(c).label).reduce((a, b, i, l) => a + (i === l.length - 1 ? ' and ' : ', ') + b) : '');
  function cats() {
    if (st.view === 'verdict') {
      const seen = new Set(SER.flatMap(s => Object.values(s.pages).flatMap(p => Object.keys(p.verdict))));
      return VD.filter(v => seen.has(v[0])).map(v => ({key: v[0], label: v[1], fills: [VCOL[v[0]] || 'var(--ref)']}));
    }
    const keys = [...new Set(SER.flatMap(s => Object.values(s.pages).flatMap(p => Object.keys(p.cards))))];
    const rank = k => { const c = setCards(k); return [k === 'none' ? 1 : 0, -c.length, ...CK.cardsIn(c).map(x => CK.cards.findIndex(y => y.id === x))]; };
    keys.sort((a, b) => { const ra = rank(a), rb = rank(b); for (let i = 0; i < Math.max(ra.length, rb.length); i++) { const d = (ra[i] == null ? -1 : ra[i]) - (rb[i] == null ? -1 : rb[i]); if (d) return d; } return 0; });
    return keys.map(k => { const c = CK.cardsIn(setCards(k)); return {key: k, label: c.length ? (c.length === 1 ? cardsLab(c) + ' only' : cardsLab(c)) : 'no card’s data', fills: c.length ? c.map(x => CK.card(x).color) : [GREY]}; });
  }
  const counts = p => (st.view === 'verdict' ? p.verdict : p.cards);
  const phrase = (k, n, tot) => `${esc(st.view === 'verdict' ? VLAB[k] || k : cats().find(c => c.key === k).label)}: ${num(n, 0)} (${pct(n / tot)})`;

  /* status line, scope, definitions */
  setHTML('claims-status', SER.map(s => `<b>${esc(s.label)}</b> (“${esc(s.short)}”): ${esc(s.note)}${s.tested ? ` (${num(s.tested, 0)} claims tested, over all the pages)` : ''}.`).join('<br>'));
  if (S > 1) setHTML('claims-bars', 'one bar per page for each status');
  const out = REP.filter(r => !inAny(r.slug));
  setHTML('claims-scope', out.length ? `Not in the check: ${andList(out.map(r => `<a href="${r.url}">${esc(r.short)}</a>`))}.` : '');
  setHTML('claims-defs', VD.map(v => `<dt>${esc(v[1])}</dt><dd>${esc(v[2] || v[0])}</dd>`).join('') +
    '<dt>the cards behind a claim</dt><dd>the cards whose data the claim rests on, as the check recorded them (most claims with no card’s data are source readings, specifications or arithmetic); after the campaign, a claim it tested adds the cards the campaign tested or reported it on (a corrected claim rests on those alone)</dd>');

  /* controls and legend */
  const ctl = document.getElementById('claims-ctl'), box = () => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.seg(box(), {label: 'Split by', options: [['verdict', 'verdict'], ['cards', 'cards behind it']], value: st.view, onChange: v => { st.view = v; legend(); fr.redraw(); summary(); }});
  CK.seg(box(), {label: 'Scale', options: [['n', 'claims'], ['share', 'share of the page']], value: st.scale, onChange: v => { st.scale = v; fr.redraw(); }});
  function swatch(fills) {
    const s = CK.el('svg', {viewBox: '0 0 18 12', width: 18, height: 12, 'aria-hidden': 'true'}), h = 12 / fills.length;
    fills.forEach((c, i) => { const r = CK.el('rect', {x: 2, y: i * h, width: 14, height: h}, s); r.style.fill = c; });
    return s;
  }
  function legend() {
    const h = document.getElementById('claims-leg'); h.textContent = '';
    cats().forEach(c => { const sp = document.createElement('span'); sp.className = 'ck-li'; sp.append(swatch(c.fills), document.createTextNode(c.label)); h.appendChild(sp); });
  }
  const read = CK.readout('claims-read');
  function summary() {
    read.set(SER.map(s => {
      const tot = {}, pages = Object.values(s.pages), N = pages.reduce((a, p) => a + p.claims, 0);
      pages.forEach(p => { for (const k in counts(p)) tot[k] = (tot[k] || 0) + counts(p)[k]; });
      return `${esc(s.label)}: ${num(N, 0)} claims on ${pages.length} pages. ${st.view === 'verdict' ? 'By verdict' : 'By the cards behind them'}: ` +
        cats().filter(c => tot[c.key]).map(c => phrase(c.key, tot[c.key], N)).join('; ') + '.';
    }).join('<br>'));
  }

  /* the chart */
  const open = r => { if (r.slug === HUB) window.scrollTo({top: 0, behavior: CK.reduced ? 'auto' : 'smooth'}); else location.href = r.url; };
  const bh = 14, bg = 4, pad = 10, T = 6, B = 40;
  const barsH = S * bh + (S - 1) * bg;
  const layout = W => { const nar = W < 600, rowH = (nar ? 17 : 0) + Math.max(barsH, 16) + pad; let y = T, prev; const rows = PAGES.map(r => { if (prev !== undefined && r.group !== prev) y += 6; prev = r.group; const o = {r, y}; y += rowH; return o; }); return {nar, rows, H: y + B}; };
  function draw(f) {
    const W = f.W, {nar, rows, H} = layout(W), svg = f.svg, cs = cats(), yEnd = H - B;
    const tw = (s, cls) => { const t = CK.txt(svg, -999, -999, s, cls); let w = 0; try { w = t.getComputedTextLength(); } catch (_) { /* no layout */ } t.remove(); return w || s.length * 7; };
    const endTxt = (p, s) => num(p.claims, 0) + (S > 1 ? ' · ' + s.short : '');
    const endW = Math.ceil(Math.max(...rows.flatMap(({r}) => SER.map(s => (s.pages[r.slug] ? tw(endTxt(s.pages[r.slug], s), 'tick') : 0))))) + 10;
    const L = nar ? 2 : Math.min(Math.round(0.32 * W), Math.ceil(Math.max(...rows.map(({r}) => tw(r.short, 'lab')))) + 14);
    const maxN = Math.max(...SER.flatMap(s => Object.values(s.pages).map(p => p.claims)));
    const x = st.scale === 'share' ? CK.lin(0, 1, L, W - endW) : CK.lin(0, maxN, L, W - endW);
    const g0 = CK.el('g', {'aria-hidden': 'true'}, svg);
    const ticks = st.scale === 'share' ? [0, 0.25, 0.5, 0.75, 1] : x.ticks(Math.max(2, Math.round((W - L - endW) / 80)));
    ticks.forEach(t => { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: yEnd, class: 'grid-line'}, g0); CK.txt(g0, x(t), yEnd + 16, st.scale === 'share' ? pct(t) : num(t, 0), 'tick', 'middle'); });
    CK.txt(g0, (L + W - endW) / 2, H - 6, st.scale === 'share' ? 'share of the page’s claims' : 'claims on the page', 'lab', 'middle');
    const nodes = [], list = [];
    rows.forEach(({r, y}) => {
      const by = nar ? y + 17 : y + (Math.max(barsH, 16) - barsH) / 2;
      if (nar) CK.txt(g0, 2, y + 12, r.short, 'lab'); else CK.txt(g0, L - 8, by + barsH / 2 + 4, r.short, 'lab', 'end');
      SER.forEach((s, si) => {
        const p = s.pages[r.slug], yb = by + si * (bh + bg);
        if (!p) { if (S > 1) CK.txt(g0, L + 2, yb + bh - 3, `not in the check (${s.short})`, 'tick'); return; }
        const g = CK.el('g', {class: 'cbar'}, svg), n = counts(p), tot = p.claims, scale = st.scale === 'share' ? 1 / tot : 1;
        CK.el('rect', {x: 0, y: yb - bg / 2, width: W, height: bh + bg, class: 'ck-hit'}, g);
        let x0 = 0;
        cs.forEach(c => {
          const v = n[c.key] || 0; if (!v) return;
          const xa = x(x0 * scale), xb = x((x0 + v) * scale), w = Math.max(0.5, xb - xa), sh = bh / c.fills.length;
          c.fills.forEach((col, i) => { const e = CK.el('rect', {x: xa, y: yb + i * sh, width: w, height: sh}, g); e.style.fill = col; });
          CK.el('rect', {x: xa, y: yb, width: w, height: bh, class: 'seg', fill: 'none'}, g);
          x0 += v;
        });
        CK.txt(g0, x(x0 * scale) + 5, yb + bh - 2, endTxt(p, s), 'tick');
        /* the claims the campaign tested on this page, by this chart's rule (p.tested) beside the page's own note (r.v3_note) */
        const tt = p.tested, tn = tt ? Object.values(tt).reduce((a, b) => a + b, 0) : 0;
        const vs = tt ? `<br><span class="small">The ${num(tn, 0)} the campaign tested, by this chart's rule: ${Object.keys(tt).map(k => `${num(tt[k], 0)} ${esc(VLAB[k] || k)}`).join(', ')}` +
          (r.v3_note ? `; by the page's own note: ${r.v3_note.map(([k, w]) => `${num(k, 0)} ${esc(w)}`).join(', ')}` : '') + '</span>' : '';
        const tip = `<b>${esc(r.title)}</b>${S > 1 ? ' · ' + esc(s.short) : ''}: ${num(tot, 0)} claims<br>` + cs.filter(c => n[c.key]).map(c => phrase(c.key, n[c.key], tot)).join('<br>') + vs +
          `<br><span class="small">${r.slug === HUB ? 'this page' : 'click or Enter: open the page'}</span>`;
        CK.tip(f, g, tip, {role: 'link'});
        g.addEventListener('pointerdown', ev => { g._touch = ev.pointerType === 'touch'; g._go = f.pinned !== g; });  /* after the tip's own handler: a second tap opens */
        g.addEventListener('click', () => { if (g._touch && !g._go) return; open(r); });
        nodes.push(g); list.push(r);
      });
    });
    CK.keynav(f, nodes, {onEnter: (node, k) => open(list[k])});
  }
  legend(); summary();
  const fr = CK.frame('claims', {height: W => layout(W).H, minW: 300, maxW: 1100, label: 'Claims on each page before and after the version-3 campaign, by verdict or by the cards whose data they rest on; a bar opens its page', draw});
})();

/* ---------- the late carry, cycle by cycle (§3): the RTL's mechanism simulated, and the cards' measurements ----------
   D.carry (tools/ettelem/sync_hub_data.py): rtl = the constants of rtl-sim/pmu_carry (E2); per_card = the version-3
   campaign's raw read pairs (MEM-R1) and fixcyc()'s leftover per corrected launch (MEM-R3). */
(function () {
  const C = D.carry;
  if (!C || !document.getElementById('carry-anim')) return;
  const K = C.rtl, N = K.counters, WR = Math.pow(2, K.pre_bits);
  /* The RTL's rule for one counting counter (the testbench's): each cycle the adder serves the counter under its index if
     that counter's carry is pending, and the index moves on while any carry is pending; it starts just past counter 0,
     where it stopped after the last fold. A read returns post × 2^bits + pre and ignores a pending carry. */
  const sim = [];
  (function () {
    let pre = 0, post = 0, ov = 0, idx = 1;
    for (let t = 0; t < 2 * WR; t++) {
      sim.push({t, pre, post, ov, idx, read: post * WR + pre});
      const any = ov;
      if (ov && idx === 0) { post += 1; ov = 0; }
      if (any) idx = (idx + 1) % N;
      pre += 1; if (pre === WR) { pre = 0; ov = 1; }
    }
  })();
  const shortN = sim.filter(s => s.t >= WR && s.read !== s.t).length;  /* reads short per wrap in the simulation */
  if (shortN !== K.sim_short_reads) console.warn('carry: the simulation gives ' + shortN + ' short reads, the RTL run ' + K.sim_short_reads);
  const T0 = WR - 8, T1 = WR + shortN + 12;
  const st = {t: WR - 3, timer: null};
  const ctl = document.getElementById('carry-ctl'), read = CK.readout('carry-read');
  const bbox = document.createElement('div'); bbox.className = 'controls'; bbox.style.margin = '0';
  const mk = (txt, fn) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = txt; b.addEventListener('click', fn); bbox.appendChild(b); return b; };
  const play = mk('Play', () => (st.timer ? stop() : start()));
  mk('Step', () => { stop(); go(st.t >= T1 ? T0 : st.t + 1); });
  mk('To the wrap', () => { stop(); go(WR - 1); });
  ctl.appendChild(bbox);
  const sb = document.createElement('div'); ctl.appendChild(sb);
  const slider = CK.range(sb, {label: 'Cycle', min: T0, max: T1, step: 1, value: st.t, fmt: v => num(v, 0), onInput: v => { stop(); go(v); }});
  function start() { if (st.t >= T1) go(T0); play.textContent = 'Pause'; play.setAttribute('aria-pressed', 'true');
    st.timer = setInterval(() => { if (st.t >= T1) stop(); else go(st.t + 1); }, CK.reduced ? 900 : 420); }
  function stop() { if (st.timer) clearInterval(st.timer); st.timer = null; play.textContent = 'Play'; play.setAttribute('aria-pressed', 'false'); }
  function go(t) {  /* show cycle t; the slider follows without firing its own handler */
    st.t = Math.max(T0, Math.min(T1, Math.round(t)));
    slider.input.value = st.t; slider.input.setAttribute('aria-valuetext', num(st.t, 0)); slider.el.querySelector('output').textContent = num(st.t, 0);
    fr.redraw(); say();
  }
  function say() {
    const s = sim[st.t], wrapT = Math.floor(st.t / WR) * WR, k = st.t - wrapT;
    if (s.ov) {
      const m = (N - s.idx) % N;
      read.set(`<b>Cycle ${num(st.t, 0)}</b>: the pre-counter wrapped ${k ? `${word(k)} cycle${k === 1 ? '' : 's'} ago` : 'this cycle'} and set its carry, which waits for the shared adder. ` +
        `The adder is at counter ${s.idx} and reaches counter 0 ${m ? `in ${word(m)} cycle${m === 1 ? '' : 's'}` : 'this cycle, and folds the carry in'}. Until then a read returns ${num(s.post, 0)} × ${WR} + ${s.pre} = <b>${num(s.read, 0)}</b>: 128 short of ${num(st.t, 0)}.`);
    } else if (st.t >= WR) {
      read.set(`<b>Cycle ${num(st.t, 0)}</b>: the adder folded the carry into the post-counter ${word(st.t - WR - shortN + 1)} cycle${st.t - WR - shortN + 1 === 1 ? '' : 's'} ago, and stopped just past counter 0. A read returns ${num(s.read, 0)}, right again until the next wrap, ${num(WR - (st.t - WR), 0)} cycles on.`);
    } else {
      read.set(`<b>Cycle ${num(st.t, 0)}</b>: the pre-counter reads ${s.pre} of its ${WR} values and no carry is pending, so a read returns the true count, ${num(s.read, 0)}. ${WR - s.pre === 1 ? 'It wraps on the next cycle.' : `It wraps in ${word(WR - s.pre)} cycles.`}`);
    }
  }
  const layout = W => { const wide = W >= 640; return wide ? {wide, R: 78, ringH: 232, valH: 0, H: 232 + 150} : {wide, R: 64, ringH: 196, valH: 186, H: 196 + 186 + 150}; };
  function draw(f) {
    const W = f.W, Lo = layout(W), s = sim[st.t], svg = f.svg;
    const g0 = CK.el('g', {'aria-hidden': 'true'}, svg);
    /* the ring of counters and the adder's index */
    const cx = Lo.wide ? 150 : W / 2, cy = 26 + Lo.R + 14, R = Lo.R;
    CK.txt(g0, Lo.wide ? 8 : cx, 16, Lo.wide ? `${N} counters share one adder; counter 0 counts cycles` : `${N} counters, one shared adder`, 'lab-strong', Lo.wide ? 'start' : 'middle');
    const ring = CK.el('circle', {cx, cy, r: R, fill: 'none', 'stroke-dasharray': '2 4'}, g0); ring.style.stroke = 'var(--axis)';
    const pos = i => { const a = -Math.PI / 2 + 2 * Math.PI * i / N; return [cx + R * Math.cos(a), cy + R * Math.sin(a)]; };
    const [hx, hy] = pos(s.idx), hl = 1 - 22 / R;
    const hand = CK.el('line', {x1: cx, y1: cy, x2: cx + (hx - cx) * hl, y2: cy + (hy - cy) * hl, 'stroke-width': 3, 'stroke-linecap': 'round'}, g0);
    hand.style.stroke = s.ov ? 'var(--warn)' : 'var(--ink-2)';
    const hub = CK.el('circle', {cx, cy, r: 24}, g0); hub.style.fill = 'var(--surface)'; hub.style.stroke = 'var(--ink-2)'; hub.style.strokeWidth = '1.5';
    CK.txt(g0, cx, cy + 4, 'adder', 'lab', 'middle');
    for (let i = 0; i < N; i++) {
      const [x, y] = pos(i), c0 = i === 0, pend = c0 && s.ov, here = i === s.idx;
      const b = CK.el('circle', {cx: x, cy: y, r: 13}, g0);
      b.style.fill = pend ? 'color-mix(in srgb, var(--warn) 55%, var(--surface))' : here ? 'color-mix(in srgb, var(--ink-2) 18%, var(--surface))' : 'var(--surface)';
      b.style.stroke = c0 ? 'var(--c1)' : 'var(--axis)'; b.style.strokeWidth = c0 ? '2.5' : '1.2';
      CK.txt(g0, x, y + 4, String(i), c0 || here || pend ? 'lab-strong' : 'tick', 'middle');
    }
    /* counter 0's value */
    const vx = Lo.wide ? 320 : 8, vy = Lo.wide ? 30 : Lo.ringH + 8, bw = Lo.wide ? 30 : Math.min(30, Math.floor((W - 16) / (K.pre_bits + 4)));
    CK.txt(g0, vx, vy, `Counter 0 (the cycle count): its pre-counter, ${K.pre_bits} bits`, 'lab-strong');
    for (let b = 0; b < K.pre_bits; b++) {
      const bit = (s.pre >> (K.pre_bits - 1 - b)) & 1, x = vx + b * (bw + 3), r = CK.el('rect', {x, y: vy + 10, width: bw, height: 26, rx: 4}, g0);
      r.style.fill = bit ? 'var(--c1)' : 'var(--surface)'; r.style.stroke = bit ? 'var(--c1)' : 'var(--axis)';
      const t = CK.txt(g0, x + bw / 2, vy + 28, String(bit), 'lab-strong', 'middle'); t.style.fill = bit ? inkOn('var(--c1)') : 'var(--ink-2)';
    }
    CK.txt(g0, vx + K.pre_bits * (bw + 3) + 6, vy + 28, `= ${s.pre}`, 'lab-strong');
    const rows = [
      ['carry into the post-counter', s.ov ? (Lo.wide ? 'pending: ignored by a read' : 'pending') : st.t >= WR ? (Lo.wide ? 'folded in by the adder' : 'folded in') : 'none pending'],
      ['post-counter', `${num(s.post, 0)} (× ${WR} = ${num(s.post * WR, 0)})`],
      ['a read returns post × ' + WR + ' + pre', num(s.read, 0)],
      ['the true count', num(st.t, 0)],
    ];
    rows.forEach(([a, b], i) => { const y = vy + 60 + i * 22; CK.txt(g0, vx, y, a, 'lab'); CK.txt(g0, Lo.wide ? vx + 230 : W - 8, y, b, 'lab-strong', Lo.wide ? 'start' : 'end'); });
    const short = s.read !== st.t, yv = vy + 60 + rows.length * 22 + 4;
    const badge = CK.el('rect', {x: vx, y: yv - 2, width: short ? 128 : 96, height: 22, rx: 11}, g0);
    badge.style.fill = short ? 'color-mix(in srgb, var(--warn) 40%, var(--surface))' : 'color-mix(in srgb, var(--ok) 22%, var(--surface))';
    badge.style.stroke = short ? 'var(--warn)' : 'var(--ok)';
    CK.txt(g0, vx + 10, yv + 13, short ? `read is ${WR} short` : 'read is right', 'lab-strong');
    /* the trace: read minus the true count over the cycles around the wrap */
    const tT = Lo.ringH + Lo.valH + 22, tB = tT + 78, L = 58, Rr = 12;
    const x = CK.lin(T0 - 0.5, T1 + 0.5, L, W - Rr), y = v => (v === 0 ? tT + 10 : tB - 6);
    CK.txt(g0, 2, tT - 10, 'read − true count, cycles', 'lab');
    [0, -WR].forEach(v => { CK.el('line', {x1: L, x2: W - Rr, y1: y(v), y2: y(v), class: 'grid-line'}, g0); CK.txt(g0, L - 8, y(v) + 4, v ? `−${WR}` : '0', 'tick', 'end'); });
    const sh = sim.filter(q => q.t >= T0 && q.t <= T1 && q.read !== q.t);
    if (sh.length) { const r = CK.el('rect', {x: x(sh[0].t - 0.5), y: tT, width: x(sh[sh.length - 1].t + 0.5) - x(sh[0].t - 0.5), height: tB - tT}, g0); r.style.fill = 'color-mix(in srgb, var(--warn) 16%, transparent)'; }
    let d = '';
    for (let t = T0; t <= T1; t++) { const v = sim[t].read - t; d += (t === T0 ? `M${x(t - 0.5)},${y(v)}` : `L${x(t - 0.5)},${y(v)}`) + `L${x(t + 0.5)},${y(v)}`; }
    const pth = CK.el('path', {d, fill: 'none', 'stroke-width': 2}, g0); pth.style.stroke = 'var(--c1)';
    const step = W < 480 ? 8 : 4;
    for (let t = T0; t <= T1; t += step) CK.txt(g0, x(t), tB + 16, num(t, 0), 'tick', 'middle');
    CK.txt(g0, (L + W - Rr) / 2, tB + 34, `cycle (the pre-counter wraps at ${WR})`, 'lab', 'middle');
    const xc = x(st.t), cur = CK.el('line', {x1: xc, x2: xc, y1: tT - 2, y2: tB + 2, 'stroke-width': 1.5}, g0); cur.style.stroke = 'var(--ink)';
    const dot = CK.el('circle', {cx: xc, cy: y(sim[st.t].read - st.t), r: 5.5}, g0); dot.style.fill = 'var(--c1)'; dot.style.stroke = 'var(--surface)'; dot.style.strokeWidth = '2';
    /* keyboard: one stop on the trace; arrows step the cycle, Home and End jump */
    /* its top sits below the axis title, so the focus ring (2 px, 2 px out) clears the title's descenders */
    const hit = CK.el('rect', {x: L, y: tT + 2, width: W - Rr - L, height: tB - tT + 2, class: 'ck-hit'}, svg);
    hit.setAttribute('tabindex', '0'); hit.setAttribute('role', 'slider'); hit.setAttribute('aria-label', 'The cycle shown: use the arrow keys to step');
    hit.setAttribute('aria-valuemin', T0); hit.setAttribute('aria-valuemax', T1); hit.setAttribute('aria-valuenow', st.t);
    hit.addEventListener('keydown', ev => {
      const k = ev.key, j = k === 'ArrowRight' || k === 'ArrowUp' ? st.t + 1 : k === 'ArrowLeft' || k === 'ArrowDown' ? st.t - 1 : k === 'Home' ? T0 : k === 'End' ? T1 : null;
      if (j == null) return; ev.preventDefault(); stop(); go(j); fr.svg.querySelector('[role="slider"]').focus();
    });
    hit.addEventListener('pointerdown', ev => { const b = svg.getBoundingClientRect(), px = (ev.clientX - b.left) * (W / b.width); stop(); go(T0 + (px - L) / (W - Rr - L) * (T1 - T0 + 1) - 0.5); });
  }
  const fr = CK.frame('carry-anim', {height: W => layout(W).H, minW: 300, maxW: 900, label: `The late carry in the RTL: ${N} counters share one adder; after the pre-counter wraps, a read is ${WR} short until the adder reaches counter 0`, draw});
  say();

  /* ---- the cards: raw pairs and corrected intervals per launch ---- */
  const CS = CK.cardsIn(C.per_card), gap = (C.per_card[CS[0]].raw[0] || {}).gap || 10;
  /* phases (of WR) at which a pair gap cycles apart straddles a window of w short reads: 2w below the spacing,
     2 × gap for any window of gap or more */
  const w19 = K.card_short_reads_19sep, phases = w => { let n = 0; for (let a = 0; a < WR; a++) if ((a < w) !== ((a + gap) % WR < w)) n++; return n; };
  const expRaw = phases(gap), p0 = expRaw / WR;
  const rawF = r => (r.plus + r.minus) / r.pairs;
  /* each card's raw launches against the prediction: a card whose launches bracket it matches; one whose every launch
     reads lower fits a window shorter than the spacing (or one that varies) */
  const rawMM = c => mm(C.per_card[c].raw.map(rawF));
  const cMatch = CS.filter(c => rawMM(c)[0] <= p0 && rawMM(c)[1] >= p0), cLow = CS.filter(c => rawMM(c)[1] < p0), cHigh = CS.filter(c => rawMM(c)[0] > p0);
  const spanOf = cs => rng(100 * Math.min(...cs.map(c => rawMM(c)[0])), 100 * Math.max(...cs.map(c => rawMM(c)[1])), 1) + '%';
  /* the launch ids as words: p1/t_raw is pass 1's raw read pairs, p1/t_rawodd the same pairs each after a timestamp */
  const PROG = {t_raw: 'raw read pairs', t_rawodd: 'raw read pairs, each after a timestamp', t_glitch: 'timed no-ops'};
  const lname = (id, prog) => { const m = /^p(\d+)(?:\/(t_\w+))?$/.exec(id), k = m && (m[2] || prog);
    return m ? `pass ${m[1]}, ${PROG[k] || esc(k)} (<code>${esc(k)}</code>)` : esc(id); };
  const allRaw = CS.flatMap(c => C.per_card[c].raw.map(rawF)), allFix = CS.flatMap(c => C.per_card[c].fixed.map(q => q.frac));
  const pc1 = v => num(100 * v, 1) + '%';
  document.getElementById('carry-cards-title').textContent = `On the cards: read pairs ${gap} cycles apart that come out ${WR} off, raw and after the fix`;
  CK.legend('carry-leg', CS.map(c => ({key: c, label: CK.card(c).label, color: CK.card(c).color, mark: CK.card(c).mark})));
  const RW = 22, T = 30, B = 40, rowHf = W => 2 * RW + 26 + (W < 600 ? 16 : 0);
  const fixText = c => { const v = C.per_card[c].fixed.map(q => q.frac), z = v.filter(x => x === 0).length, nz = v.filter(x => x > 0);
    return z === v.length ? `0% in all ${word(v.length)} launches on ${c}` : z ? `0% in ${word(z)} of ${word(v.length)} launches on ${c} and ${rng(100 * Math.min(...nz), 100 * Math.max(...nz), 1)}% in the other${nz.length > 1 ? ` ${word(nz.length)}` : ''}`
      : `${rng(100 * Math.min(...nz), 100 * Math.max(...nz), 1)}% in all ${word(v.length)} on ${c}`; };
  const wLow = cLow.length ? (() => { const lo = Math.min(...cLow.map(c => rawMM(c)[0])), hi = Math.max(...cLow.map(c => rawMM(c)[1]));
    const ws = []; for (let w = Math.max(1, Math.round(lo * WR / 2)); w <= Math.min(gap - 1, Math.round(hi * WR / 2)); w++) ws.push(w); return ws; })() : [];
  const rawParts = [];
  if (cMatch.length) rawParts.push(`${andList(cMatch)} read ${spanOf(cMatch)} of pairs, either side of the ${pc1(p0)} (${expRaw} of ${WR} phases) that any window of ${gap} or more short reads gives (at least the pairs' spacing)`);
  if (cLow.length) rawParts.push(`${cLow.length > 1 ? andList(cLow) + ' read' : cLow[0] + '’s ' + word(C.per_card[cLow[0]].raw.length) + ' launches all read'} lower, ${spanOf(cLow)}, as a window shorter than the spacing or one that varies would` +
    (wLow.length ? ` (a window of w < ${gap} cycles gives 2w of ${WR} phases: ${wLow.map((w, i) => `${w}${i ? '' : ' cycles'} gives ${pc1(phases(w) / WR)}`).join(', ')})` : '') +
    `, which fits ${cLow.length > 1 ? 'their' : 'its'} fixcyc() leftover: fixcyc() adds ${WR} below ${K.fixcyc_below}, so it over-corrects a shorter window`);
  if (cHigh.length) rawParts.push(`${andList(cHigh)} read${cHigh.length > 1 ? '' : 's'} higher, ${spanOf(cHigh)}`);
  const cread = CK.readout('carry-cards-read'), csum = `Raw: ${rawParts.join('; ')}. After fixcyc(): ${andList(CS.map(fixText))}.`;
  cread.set(csum);
  setHTML('carry-lead', `<b>The late carry, cycle by cycle.</b> In the RTL a read ignores a carry that waits for the shared adder, so it comes back ${WR} short for ${word(shortN)} cycles after every wrap; ` +
    `on the ${word(CS.length)} cards two raw reads ${gap} cycles apart come out ${WR} off ${rng(100 * Math.min(...allRaw), 100 * Math.max(...allRaw), 0)}% of the time, and the fixed correction leaves up to ${pc1(Math.max(...allFix))}.`);
  setHTML('carry-cap', `Above: the RTL's rule simulated for counter 0 alone, as <a href="${REPO}tree/main/rtl-sim/pmu_carry"><code>rtl-sim/pmu_carry</code></a> runs <code>neigh_pmu.v</code>: ${N} counters, each a ${K.pre_bits}-bit pre-counter and a ${K.post_bits}-bit post-counter, share one adder whose index moves one counter a cycle while a carry is pending; ` +
    `${word(shortN)} short reads per wrap in the simulation; on aifoundry2's card on 19 September at least low bits 0–${w19[0] - 1} in one launch and 0–${w19[1] - 1} in the other, and <code>fixcyc()</code> assumes 0–${K.fixcyc_below - 1} (it adds ${WR} below ${K.fixcyc_below}). ` +
    `Below: the version-3 campaign on each card (E35), every launch: the upper line of a card is its raw read pairs (MEM-R1: ${word(C.per_card[CS[0]].raw.length)} launches of ${num(C.per_card[CS[0]].raw[0].pairs, 0)} pairs on each card; in ${num(CS.reduce((a, c) => a + C.per_card[c].raw_launches_no_window, 0), 0)} of ${num(CS.reduce((a, c) => a + C.per_card[c].raw.length, 0), 0)} no single window fits), the lower the share of ${gap}-cycle intervals still ${WR} off after <code>fixcyc()</code> (MEM-R3, ${word(C.per_card[CS[0]].fixed.length)} launches). ` +
    `The dashed line is the raw share that any window of ${gap} or more short reads gives (at least the pairs' spacing): ${expRaw} of ${WR} phases, ${pc1(p0)}; a window of w < ${gap} cycles gives 2w of ${WR}, less. Hover, tap or tab to a mark for its launch.`);
  function cdraw(f) {
    const W = f.W, nar = W < 600, L = nar ? 8 : 190, R = 16, H = f.H, yEnd = H - B, rowH = rowHf(W);
    const xmax = Math.max(0.18, ...allRaw), x = CK.lin(0, xmax, L, W - R);
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
    const ticks = [0, 0.05, 0.1, 0.15].filter(t => t <= xmax);
    ticks.forEach(t => { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: yEnd, class: 'grid-line'}, g0); labs.push(CK.txt(g0, x(t), yEnd + 16, num(100 * t, 0) + '%', 'tick', 'middle')); });
    labs.push(CK.txt(g0, (L + W - R) / 2, H - 6, `share of pairs ${gap} cycles apart that read ${WR} off`, 'lab', 'middle'));
    const xe = x(expRaw / WR), ref = CK.el('line', {x1: xe, x2: xe, y1: T - 6, y2: yEnd, 'stroke-dasharray': '5 4', 'stroke-width': 1.4}, g0); ref.style.stroke = 'var(--ref)';
    const nodes = [];
    CS.forEach((c, i) => {
      const y0 = T + i * rowH, cc = CK.card(c), yr = y0 + (nar ? 38 : 14), yf = yr + (nar ? 30 : RW);
      if (nar) { CK.cardMark(g0, c, 12, y0 + 10, 5); CK.txt(g0, 24, y0 + 14, cc.label, 'lab-strong'); }
      else { CK.cardMark(g0, c, 12, y0 + 22, 5); CK.txt(g0, 24, y0 + 26, cc.label, 'lab-strong'); }
      /* a subline's name: left of the plot on a wide screen; on a phone above the line's left end, clear of its marks */
      const sub = (yy, s, vals) => { CK.el('line', {x1: L, x2: W - R, y1: yy, y2: yy, class: 'grid-line', opacity: 0.7}, g0);
        labs.push(nar ? CK.txt(g0, L, yy - 10, s, 'tick', 'start') : CK.txt(g0, L - 8, yy + 4, s, 'tick', 'end')); };
      sub(yr, 'raw', C.per_card[c].raw.map(rawF)); sub(yf, 'after fixcyc()', C.per_card[c].fixed.map(q => q.frac));
      const mark = (xx, yy, html) => { const gg = CK.el('g', {}, f.svg); CK.el('rect', {x: xx - 7, y: yy - 9, width: 14, height: 18, class: 'ck-hit'}, gg); CK.cardMark(gg, c, xx, yy, 4.5);
        CK.tip(f, gg, html); gg.addEventListener('focus', () => cread.set(html)); gg.addEventListener('blur', () => cread.set(csum)); nodes.push(gg); };
      C.per_card[c].raw.forEach(r => mark(x(rawF(r)), yr, `<b>${esc(cc.label)}</b>, ${lname(r.launch)}: ${num(r.plus + r.minus, 0)} of ${num(r.pairs, 0)} pairs ${gap} cycles apart read ${WR} off (${pc1(rawF(r))}: ${num(r.plus, 0)} by +${WR}, ${num(r.minus, 0)} by −${WR})`));
      C.per_card[c].fixed.forEach(q => mark(x(q.frac), yf, `<b>${esc(cc.label)}</b>, ${lname(q.launch, 't_glitch')}, corrected by fixcyc(): ${pc1(q.frac)} of ${gap}-cycle intervals still ${WR} off; ` +
        (q.e != null ? `one window fits the launch, low bits 0–${q.e}` : 'no single window fits the launch')));
    });
    labs.push(CK.txt(g0, xe, T - 12, `${pc1(expRaw / WR)}: expected raw`, 'tick', 'middle'));
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('carry-cards', {height: W => T + CS.length * rowHf(W) + B, minW: 300, maxW: 900, label: `Per launch and card, the share of read pairs ${gap} cycles apart that come out ${WR} off: raw, and after fixcyc()`, draw: cdraw});
})();

/* ---------- how often a new reading arrives, card by card (§4.1) ----------
   energy_events.meter: the SP stats trace's own pass, quiet and under ettelem at 10 Hz (sp_pass_ms, three passes per
   card), and the board value's refresh under ettelem (board_refresh_ms, phase-folded): every pass, with the medians
   (the trace) and means (the stream) the text quotes. */
(function () {
  const M = D.energy_events.meter, SP = M.sp_pass_ms || {}, BR = M.board_refresh_ms || {};
  if (!document.getElementById('timing')) return;
  const CS = CK.cardsIn(SP).filter(c => SP[c].quiet_ms && SP[c].sampled_ms && BR[c]);
  if (!CS.length) return;
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  const V = Object.fromEntries(CS.map(c => [c, {q: med(SP[c].quiet_ms), s: med(SP[c].sampled_ms), b: mean(BR[c].sampler_10hz_ms)}]));
  const add = CS.map(c => V[c].s - V[c].q), over = CS.map(c => V[c].s - V[c].b);
  const slow = CS.reduce((a, c) => (V[c].q > V[a].q ? c : a)), rest = CS.filter(c => c !== slow), ratio = V[slow].q / mean(rest.map(c => V[c].q));
  /* the rows name their card in words and colour, without the registry's glyphs: here a ring means nothing polling
     and a dot the sampler running, on every card */
  const SER = [['q', 'the SP’s pass, nothing polling', 'ring'], ['s', 'the SP’s pass while ettelem samples', 'dot'], ['b', 'a new board value while ettelem samples (mean of three passes)', 'line']];
  CK.legend('timing-leg', SER.map(([k, l, m]) => ({key: k, label: l, color: 'var(--ink-2)', mark: m})));
  { const sw = document.querySelectorAll('#timing-leg .ck-li svg')[2];  /* the board value's glyph: the chart's vertical bar */
    if (sw) { sw.textContent = ''; const r = CK.el('rect', {x: 7, y: 0, width: 4, height: 10, rx: 1.5}, sw); r.style.fill = 'var(--ink-2)'; } }
  const read = CK.readout('timing-read');
  const sum = `The sampler lengthens the pass by ${rng(Math.min(...add), Math.max(...add), 0, 'ms')} on ${CS.length === 2 ? 'both cards' : `all ${word(CS.length)} cards`}; ${slow}'s pass is about ${num(ratio, 1)} times the other ${word(rest.length)} cards' with nothing polling; ` +
    `under the sampler the trace's pass runs ${rng(Math.min(...over), Math.max(...over), 0, 'ms')} longer than the refresh the board stream shows (two methods).`;
  read.set(sum);
  setHTML('timing-lead', `A reading can be no fresher than the service processor's pass, and reading it slows that pass: ${slow} gets a new value about every ${num(V[slow].b, 0)} ms while ettelem samples, the other ${word(rest.length)} every ${rng(...mm(rest.map(c => V[c].b)), 0, 'ms')}.`);
  setHTML('timing-cap', `Per card, every pass of the version-3 campaign (three each): the SP stats trace's own pass interval with no sampler running and while <code>ettelem</code> samples at 10 Hz (TEL-P1, P3 and P5; the larger marks are the medians), and the interval between new board values in the board-power stream under the same sampler (TEL-S, phase-folded; the bar under each line is the mean of the three passes, the fainter lines the passes). Hover, tap or tab to a mark.`);
  const rowH = 50, T = 12, B = 40;
  function draw(f) {
    const W = f.W, nar = W < 600, L = nar ? 8 : 150, R = 16, yEnd = T + CS.length * (rowH + (nar ? 16 : 0));
    const lo = 10 * Math.floor(Math.min(...CS.flatMap(c => SP[c].quiet_ms.concat(BR[c].sampler_10hz_ms))) / 10) - 10, hi = 10 * Math.ceil(Math.max(...CS.flatMap(c => SP[c].sampled_ms)) / 10) + 10;
    const x = CK.lin(lo, hi, L, W - R), g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
    x.ticks(nar ? 4 : 8).forEach(t => { CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: yEnd, class: 'grid-line'}, g0); labs.push(CK.txt(g0, x(t), yEnd + 16, num(t, 0), 'tick', 'middle')); });
    labs.push(CK.txt(g0, (L + W - R) / 2, yEnd + 34, 'milliseconds between new values', 'lab', 'middle'));
    const nodes = [];
    CS.forEach((c, i) => {
      const cc = CK.card(c), y0 = T + i * (rowH + (nar ? 16 : 0)), cy = y0 + (nar ? 16 : 0) + rowH / 2 - (nar ? 0 : 6);
      if (nar) CK.txt(g0, 8, y0 + 13, cc.label, 'lab-strong'); else CK.txt(g0, 8, cy + 4, cc.label, 'lab-strong');
      CK.el('line', {x1: L, x2: W - R, y1: cy, y2: cy, class: 'grid-line', opacity: 0.6}, g0);
      const v = V[c], ar = CK.el('line', {x1: x(v.q) + 7, x2: x(v.s) - 8, y1: cy, y2: cy, 'stroke-width': 2}, g0); ar.style.stroke = cc.color;
      const ah = CK.el('path', {d: `M${x(v.s) - 8},${cy} l-6,-4 l0,8 z`}, g0); ah.style.fill = cc.color;
      labs.push(CK.txt(g0, (x(v.q) + x(v.s)) / 2, cy - 9, `+${num(v.s - v.q, 0)} ms`, 'tick', 'middle'));
      const item = (xx, html, paint) => { const gg = CK.el('g', {}, f.svg); CK.el('rect', {x: xx - 7, y: cy - 10, width: 14, height: 34, class: 'ck-hit'}, gg); paint(gg); CK.tip(f, gg, html);
        gg.addEventListener('focus', () => read.set(html)); gg.addEventListener('blur', () => read.set(sum)); nodes.push(gg); };
      const ring = (gg, xx, r, fill) => { const e = CK.el('circle', {cx: xx, cy, r}, gg); e.style.fill = fill ? cc.color : 'var(--surface)'; e.style.stroke = cc.color; e.style.strokeWidth = fill ? '1' : '2'; };
      /* the board value's refresh: a bar under the line at the mean, each pass a fainter line */
      const tick = (gg, xx, mean) => { const e = mean ? CK.el('rect', {x: xx - 2, y: cy + 6, width: 4, height: 16, rx: 1.5}, gg) : CK.el('line', {x1: xx, x2: xx, y1: cy + 8, y2: cy + 20, 'stroke-width': 2}, gg);
        if (mean) e.style.fill = cc.color; else { e.style.stroke = cc.color; e.style.opacity = '0.45'; } };
      BR[c].sampler_10hz_ms.forEach((ms, k) => item(x(ms), `<b>${esc(cc.label)}</b>, pass ${k + 1}: a new board value every ${num(ms, 1)} ms while ettelem samples at 10 Hz (TEL-S)`, gg => tick(gg, x(ms), false)));
      item(x(v.b), `<b>${esc(cc.label)}</b>: a new board value every ${num(v.b, 0)} ms on average over the three passes while ettelem samples`, gg => tick(gg, x(v.b), true));
      SP[c].quiet_ms.forEach((ms, k) => item(x(ms), `<b>${esc(cc.label)}</b>, pass ${k + 1}: the SP's pass took ${num(ms, 1)} ms with nothing polling (TEL-P)`, gg => ring(gg, x(ms), 3, false)));
      item(x(v.q), `<b>${esc(cc.label)}</b>: the SP's pass, ${num(v.q, 0)} ms with nothing polling (the median of three passes)`, gg => ring(gg, x(v.q), 6, false));
      SP[c].sampled_ms.forEach((ms, k) => item(x(ms), `<b>${esc(cc.label)}</b>, pass ${k + 1}: the SP's pass took ${num(ms, 1)} ms while ettelem samples (TEL-P)`, gg => ring(gg, x(ms), 3, true)));
      item(x(v.s), `<b>${esc(cc.label)}</b>: the SP's pass, ${num(v.s, 0)} ms while ettelem samples (the median of three passes), ${num(v.s - v.q, 0)} ms longer than with nothing polling`, gg => ring(gg, x(v.s), 6, true));
    });
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('timing', {height: W => T + CS.length * (rowH + (W < 600 ? 16 : 0)) + B, minW: 300, maxW: 900, label: 'How often a new reading arrives on each card: the service processor’s pass with nothing polling and under the sampler, and the board value’s refresh', draw});
})();

/* ---------- one sparse parity burst through every meter on the card (§4.1, E59) ----------
   burst_trace: each run's 10 Hz samples from window_s[0] to window_s[1] s after the host's first launch, kept where a
   reading changed. The board's point sample is drawn held until the sampler saw the next value; the PMIC's average and
   the rails, which are running averages, as lines through the samples where each changed. The solves are rebuilt from
   the host's launch_s with the gaps between launches (the burst's wall time less their sum) spread evenly, and a pass
   tick marks every sample where the board or a rail changed. The share view divides each meter's rise over its idle by
   its step (levels): the NoC rail's step, about 0.1 W, is left out of it. */
(function () {
  const BT = D.burst_trace;
  if (!BT || !document.getElementById('bt')) return;
  const ix = Object.fromEntries(BT.cols.map((k, i) => [k, i]));
  const avg = a => a.reduce((p, q) => p + q, 0) / a.length;
  const MET = [
    {k: 'board_w', label: 'board power, the SP’s point sample', short: 'board', color: 'var(--ink)', step: true, w: 2},
    {k: 'board_avg_w', label: 'board power, the PMIC’s running average', short: 'average', color: 'var(--ink-2)', dash: '5 3', w: 1.75},
    {k: 'minion_w', label: 'minion rail', short: 'minion', color: 'var(--c1)', w: 2},
    {k: 'sram_w', label: 'SRAM rail', short: 'SRAM', color: 'var(--c3)', w: 2},
    {k: 'noc_w', label: 'NoC rail', short: 'NoC', color: 'var(--c2)', w: 2},
  ];
  const RAILS = ['minion_w', 'sram_w', 'noc_w'], BOARD = ix.board_w;
  const X = BT.runs.map(r => {
    const S = r.samples, n = r.launch_s.length, sum = r.launch_s.reduce((p, q) => p + q, 0);
    const gap = n > 1 ? Math.max(0, (r.wall_s - sum) / (n - 1)) : 0;
    let t0 = 0;
    const solves = r.launch_s.map(d => { const s = [t0, t0 + d]; t0 += d + gap; return s; });
    const changed = (i, keys) => i > 0 && keys.some(k => S[i][ix[k]] !== S[i - 1][ix[k]]);
    const passes = S.filter((row, i) => changed(i, ['board_w'].concat(RAILS))).map(row => row[0]);
    const inB = passes.filter(t => t >= r.edges_s[0] - 1e-9 && t <= r.wall_s + 1e-9);
    /* the board value each sample shows: when the sampler first saw it, and when it saw the next one */
    const since = [], until = [];
    S.forEach((row, i) => since.push(i && row[BOARD] !== S[i - 1][BOARD] ? row[0] : (i ? since[i - 1] : row[0])));
    for (let i = S.length - 1, nx = null; i >= 0; i--) { until[i] = nx; if (i && S[i][BOARD] !== S[i - 1][BOARD]) nx = S[i][0]; }
    /* the reducer's busy readings at idle: a new board value in its busy window below the midpoint of idle and busy */
    const mid = (r.cat_idle_w + r.cat_busy_w) / 2;
    const dips = S.map((row, i) => i).filter(i => S[i][0] >= r.busy_from_s && S[i][0] <= r.wall_s && S[i][BOARD] < mid &&
      (i === 0 || S[i][BOARD] !== S[i - 1][BOARD] || S[i - 1][0] < r.busy_from_s));
    /* each average's drawn points, [t, value]: straight from one 10 Hz sample to the next. A sample left out of the data
       repeated the one before it, so each change is drawn from the sample one period earlier at the old value */
    const dt = 1 / BT.sampler_hz;
    const pts = Object.fromEntries(MET.map(m => { const c = ix[m.k], out = [[S[0][0], S[0][c]]];
      for (let i = 1; i < S.length; i++) if (S[i][c] !== S[i - 1][c]) {
        const tb = Math.max(S[i - 1][0], S[i][0] - dt);
        if (tb > out[out.length - 1][0]) out.push([tb, S[i - 1][c]]);
        out.push([S[i][0], S[i][c]]);
      }
      if (S[S.length - 1][0] > out[out.length - 1][0]) out.push([S[S.length - 1][0], S[S.length - 1][c]]);
      return [m.k, out]; }));
    return Object.assign({}, r, {S, gap, solves, passes, since, until, dips, pts, mean_s: sum / n,
      pass_s: inB.length > 1 ? (inB[inB.length - 1] - inB[0]) / (inB.length - 1) : null});
  });
  const st = {run: X[0].id, view: 'w'};
  const cur = () => X.find(r => r.id === st.run) || X[0];
  const share = () => st.view === 'share';
  const mets = () => (share() ? MET.filter(m => m.k !== 'noc_w') : MET);
  const frac = (r, m, v) => (v - r.levels[m.k][0]) / (r.levels[m.k][1] - r.levels[m.k][0]);
  const val = (r, m, v) => (share() ? frac(r, m, v) : v);
  /* one scale for every run, so that switching runs moves the lines and not the axis */
  const inWin = r => r.S.filter(row => row[0] >= BT.window_s[0] && row[0] <= BT.window_s[1]);
  const wMax = 5 * Math.ceil(Math.max(...X.flatMap(r => inWin(r).map(row => row[BOARD]))) / 5);
  const fr0 = X.flatMap(r => inWin(r).flatMap(row => MET.filter(m => m.k !== 'noc_w').map(m => frac(r, m, row[ix[m.k]]))));
  const sLo = Math.min(-0.1, Math.floor(10 * Math.min(...fr0)) / 10), sHi = Math.max(1.2, Math.ceil(10 * Math.max(...fr0)) / 10);
  const sgnT = t => (t > 0.0005 ? '+' : t < -0.0005 ? '−' : '') + num(Math.abs(t), 2);
  const Mtr = D.energy_events && D.energy_events.meter, BR = Mtr && Mtr.board_refresh_ms && Mtr.board_refresh_ms[BT.card];
  const passMs = BR ? avg(BR.sampler_10hz_ms) : null, RF = P.rail_filter && P.rail_filter[BT.card];
  const shareTxt = (r, m, v) => (share() && m.k !== 'noc_w' ? ` (${pct(frac(r, m, v))} of its step)` : '');

  const ctl = document.getElementById('bt-ctl'), c1 = document.createElement('div'), c2 = document.createElement('div');
  ctl.append(c1, c2);
  CK.seg(c1, {label: 'Run', options: X.map(r => [r.id, r.label]), value: st.run, onChange: v => { st.run = v; fr.redraw(); read.set(dflt()); }});
  CK.seg(c2, {label: 'Show', options: [['w', 'Watts'], ['share', 'Share of each meter’s step']], value: st.view,
    onChange: v => { st.view = v; legend(); fr.redraw(); read.set(dflt()); }});
  function legend() {
    CK.legend('bt-leg', mets().map(m => ({key: m.k, label: m.label, color: m.color, mark: 'line', dash: m.dash})));
    const sw = document.querySelector('#bt-leg .ck-li svg');  /* the point sample's glyph: a step */
    if (sw) { sw.textContent = ''; const p = CK.el('path', {d: 'M1,8 H7 V2 H12 V6 H17', fill: 'none', 'stroke-width': 2}, sw); p.style.stroke = 'var(--ink)'; }
  }
  legend();
  const read = CK.readout('bt-read');
  function dflt() {
    const r = cur(), per = r.pass_s ? r.pass_s / r.mean_s : null, R1 = r.rise, ts = BT.rise_s.map(t => num(t, 0));
    const two = k => `${pct(R1[k][0])}, ${pct(R1[k][1])}`;
    let s = `<b>${esc(r.label)}</b> · ${r.solves.length} solves of ${num(r.mean_s, 3)} s in ${num(r.wall_s, 2)} s: a new board or rail value every ${num(r.pass_s, 2)} s in the burst, ` +
      (per > 1 ? `about ${num(per, 1)} solves to each board value.` : `about ${num(1 / per, 1)} passes to each solve.`);
    s += `<br>Share of each meter's step ${ts[0]} s and ${ts[1]} s after the board's first busy reading: point sample ${two('board_w')}; PMIC average ${two('board_avg_w')}; minion rail ${two('minion_w')}; SRAM rail ${two('sram_w')}` +
      (RF ? ` (on this card's catalogue bursts the rails fall ${pct(RF.frac_1s)} and ${pct(RF.frac_2s)} of the way in the same times).` : '.');
    const d = r.dips.length === r.at_idle ? r.dips : [];
    s += `<br>Busy board values at idle: ${num(r.at_idle, 0)} of ${r.busy_readings} (${num(r.at_idle_expected, 2)} expected)` +
      (d.length ? `: ${andList(d.map(i => `${num(r.S[i][BOARD], 2)} W at ${sgnT(r.S[i][0])} s, while the PMIC's average read ${num(r.S[i][ix.board_avg_w], 2)} W`))}; by the reducer's rule, a pass that sampled a gap between two launches.` : '.');
    return s + ' Hover, tap or tab to a moment or a solve.';
  }
  function rowHtml(r, i) {
    const row = r.S[i], t = row[0], k = r.solves.findIndex(([a, b]) => t >= a && t < b);
    const where = t < 0 ? 'before the first launch' : t > r.wall_s ? `${num(t - r.wall_s, 2)}\u00a0s after the last solve ended`
      : k >= 0 ? `during solve ${k + 1} of ${r.solves.length}` : 'between two launches';
    const v = key => row[ix[key]];
    let h = `<b>${esc(r.label)} · ${sgnT(t)}\u00a0s</b>, ${where}<br>board ${num(v('board_w'), 2)}\u00a0W${shareTxt(r, MET[0], v('board_w'))}: ${r.since[i] === r.S[0][0] ? 'already showing when the window opens' : `the sampler first saw it at ${sgnT(r.since[i])}\u00a0s`}` +
      (r.until[i] != null ? ` and the next value ${num(r.until[i] - r.since[i], 2)}\u00a0s later` : ', still held at the window’s end');
    if (r.dips.includes(i)) h += `<br>below the midpoint of idle and busy inside the burst: the reducer counts it as a busy reading at idle`;
    h += `<br>the PMIC’s average ${num(v('board_avg_w'), 2)}\u00a0W${shareTxt(r, MET[1], v('board_avg_w'))}<br>` +
      `minion rail ${num(v('minion_w'), 2)}\u00a0W${shareTxt(r, MET[2], v('minion_w'))}, SRAM rail ${num(v('sram_w'), 2)}\u00a0W${shareTxt(r, MET[3], v('sram_w'))}, NoC rail ${num(v('noc_w'), 2)}\u00a0W` +
      `<br>die ${num(v('die_c'), 0)}\u00a0°C (the minion shires’ mean, whole degrees)`;
    return h;
  }
  function solveHtml(r, k) {
    const [a, b] = r.solves[k], seen = r.S.filter((row, i) => row[0] >= a && row[0] < b && (i === 0 || row[BOARD] !== r.S[i - 1][BOARD])).map(row => num(row[BOARD], 2));
    return `<b>${esc(r.label)} · solve ${k + 1} of ${r.solves.length}</b>: ${num(r.launch_s[k], 4)}\u00a0s, from ${sgnT(a)} to ${sgnT(b)}\u00a0s (rebuilt from the host's launch times)<br>` +
      (seen.length ? `new board values the sampler saw in it: ${andList(seen.map(x => x + '\u00a0W'))}` : 'the sampler saw no new board value in it');
  }

  const lay = W => { const nar = W < 600, T = 28, ph = nar ? 220 : 270; return {nar, T, ph, H: T + ph + 78}; };
  const narFrom = Math.max(BT.window_s[0], -2);  /* a narrow chart starts here, so that the burst keeps its width */
  function draw(f) {
    const r = cur(), W = f.W, G = lay(W), nar = G.nar, T = G.T, pb = T + G.ph, L = nar ? 48 : 56, R = nar ? 8 : 14;
    const yS = pb + 9, yP = pb + 24, sh = 9, yX = pb + 52;
    const x0 = nar ? narFrom : BT.window_s[0], x1 = BT.window_s[1], x = CK.lin(x0, x1, L, W - R);
    const y = share() ? CK.lin(sLo, sHi, pb, T) : CK.lin(0, Math.max(45, wMax), pb, T), ms = mets();
    CK.axes(f, {x, y, L, R, T, B: f.H - pb, xt: [], yt: share() ? [0, 0.25, 0.5, 0.75, 1] : y.ticks(nar ? 4 : 5),
      yfmt: share() ? (v => pct(v)) : (v => num(v, 0)), yl: share() ? 'share of its step' : 'watts'});
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
    /* the burst, shaded, and named above the plot */
    const bx0 = Math.max(x(0), L), bx1 = Math.min(x(r.wall_s), W - R);
    CK.el('rect', {x: bx0, y: T, width: bx1 - bx0, height: G.ph}, g0).style.fill = 'color-mix(in srgb, var(--ink) 5%, transparent)';
    labs.push(CK.txt(g0, (bx0 + bx1) / 2, T - 7, nar ? `the burst: ${r.solves.length} solves` : `the burst: ${r.solves.length} solves of ${num(r.mean_s, 3)} s`, 'tick', 'middle'));
    if (share()) [0, 1].forEach(v => { CK.el('line', {x1: L, x2: W - R, y1: y(v), y2: y(v), class: 'ck-axis'}, g0); });
    /* the lines, clipped to the plot */
    const cp = CK.el('clipPath', {id: 'bt-clip'}, CK.el('defs', {}, f.svg));
    CK.el('rect', {x: L, y: T - 3, width: W - R - L, height: G.ph + 6}, cp);
    const gl = CK.el('g', {'clip-path': 'url(#bt-clip)', 'aria-hidden': 'true'}, f.svg);
    const pos = {};
    /* the SRAM rail, the minion rail, then the NoC rail, flat and drawn over the SRAM rail where both read about 2.2 W
       after the burst; the board's lines last, on top */
    const RANK = {sram_w: 0, minion_w: 1, noc_w: 2, board_avg_w: 3, board_w: 4};
    ms.slice().sort((a, b) => RANK[a.k] - RANK[b.k]).forEach(m => {
      const P0 = r.pts[m.k].map(([t, v]) => [x(t), y(val(r, m, v))]);
      let d;
      if (m.step) d = r.S.map((row, i) => { const X0 = x(row[0]).toFixed(1), Y0 = y(val(r, m, row[ix[m.k]])).toFixed(1); return i ? `H${X0}V${Y0}` : `M${X0},${Y0}`; }).join('');
      else d = P0.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('');
      const p = CK.el('path', {d, fill: 'none', 'stroke-width': m.w, 'stroke-linejoin': 'round'}, gl);
      p.style.stroke = m.color; if (m.dash) p.style.strokeDasharray = m.dash;
      /* where the line is drawn at a given x: the held value for the step, the polyline elsewhere */
      pos[m.k] = xx => {
        if (m.step) { let i = 0; while (i + 1 < r.S.length && x(r.S[i + 1][0]) <= xx + 1e-6) i++; return y(val(r, m, r.S[i][ix[m.k]])); }
        let j = 0; while (j + 1 < P0.length && P0[j + 1][0] <= xx) j++;
        const a = P0[j], b = P0[Math.min(j + 1, P0.length - 1)];
        return b[0] > a[0] ? a[1] + (b[1] - a[1]) * (xx - a[0]) / (b[0] - a[0]) : a[1];
      };
    });
    /* the reducer's busy readings at idle: a ring on the point sample */
    r.dips.forEach(i => { const c = CK.el('circle', {cx: x(r.S[i][0]), cy: y(val(r, MET[0], r.S[i][BOARD])), r: 5.5, fill: 'none', 'stroke-width': 1.5}, gl); c.style.stroke = 'var(--ink)'; });
    /* the rails named where the burst ends, in the watts view (the share view's rails overlap: the legend names them) */
    if (!share()) {
      const xe = Math.min(x(r.wall_s), W - R) - 4, want = RAILS.map(k => ({k, y: pos[k](xe) - 6})).sort((a, b) => a.y - b.y);
      for (let k = 1; k < want.length; k++) want[k].y = Math.max(want[k].y, want[k - 1].y + 13);
      want.forEach(w => { const m = MET.find(q => q.k === w.k), t = CK.txt(gl, xe, w.y, m.short, 'lab', 'end');
        t.style.stroke = 'var(--surface)'; t.style.strokeWidth = '3px'; t.style.paintOrder = 'stroke'; t.style.strokeLinejoin = 'round'; });
    }
    /* under the axis: the solves (alternate shades) and the passes (a tick per new board or rail value) */
    labs.push(CK.txt(g0, L - 6, yS + sh - 1, 'solves', 'tick', 'end'), CK.txt(g0, L - 6, yP + sh - 1, 'passes', 'tick', 'end'));
    const gRows = CK.el('g', {}, f.svg), gs = CK.el('g', {}, f.svg), snodes = [];  /* the moments first in the tab order */
    r.solves.forEach(([a, b], k) => {
      const xa = Math.max(x(a), L), xb = Math.min(x(b), W - R);
      if (xb <= xa) return;
      const g = CK.el('g', {}, gs);
      const e = CK.el('rect', {x: xa, y: yS, width: Math.max(0.6, xb - xa - (xb - xa > 4 ? 0.6 : 0)), height: sh}, g);
      e.style.fill = k % 2 ? 'color-mix(in srgb, var(--ink) 28%, var(--surface))' : 'color-mix(in srgb, var(--ink) 62%, var(--surface))';
      CK.el('rect', {x: xa, y: yS - 3, width: Math.max(xb - xa, 2), height: sh + 6, class: 'ck-hit'}, g);
      const html = solveHtml(r, k);
      CK.tip(f, g, html); g.addEventListener('focus', () => read.set(html)); g.addEventListener('blur', () => read.set(dflt()));
      snodes.push(g);
    });
    r.passes.forEach(t => { if (t < x0 || t > x1) return; CK.el('line', {x1: x(t), x2: x(t), y1: yP, y2: yP + sh, 'stroke-width': 1.5}, g0).style.stroke = 'var(--ink-2)'; });
    /* the time axis under the strips */
    x.ticks(nar ? 6 : 8).forEach(t => {
      CK.el('line', {x1: x(t), x2: x(t), y1: pb, y2: pb + 4, class: 'ck-axis'}, g0);
      labs.push(CK.txt(g0, x(t), yX, t > 0 ? '+' + num(t, 0) : num(t, 0), 'tick', 'middle'));
    });
    labs.push(CK.txt(g0, (L + W - R) / 2, yX + 19, 'seconds from the first launch', 'lab', 'middle'));
    CK.inside(f, labs);
    /* a moment: one hit column per kept sample, and a crosshair with a dot on each line */
    const gx = CK.el('g', {'aria-hidden': 'true', 'pointer-events': 'none'}, f.svg);
    gx.style.display = 'none';
    const vl = CK.el('line', {y1: T, y2: yP + sh, 'stroke-width': 1}, gx); vl.style.stroke = 'var(--ink-2)';
    const dots = ms.map(m => { const c = CK.el('circle', {r: 3.5}, gx); c.style.fill = m.color; c.style.stroke = 'var(--surface)'; c.style.strokeWidth = '1.5'; return c; });
    const cross = i => {
      if (i == null) { gx.style.display = 'none'; return; }
      const xx = x(r.S[i][0]); gx.style.display = '';
      vl.setAttribute('x1', xx); vl.setAttribute('x2', xx);
      ms.forEach((m, k) => { dots[k].setAttribute('cx', xx); dots[k].setAttribute('cy', pos[m.k](xx)); });
    };
    const nodes = [];
    r.S.forEach((row, i) => {
      if (row[0] < x0 || row[0] > x1) return;
      const xa = x(row[0]), xb = i + 1 < r.S.length ? Math.min(x(r.S[i + 1][0]), W - R) : W - R;
      const g = CK.el('g', {}, gRows);
      CK.el('rect', {x: xa, y: T, width: Math.max(1, xb - xa), height: G.ph, class: 'ck-hit'}, g);
      g._bt = i;
      const html = rowHtml(r, i);
      CK.tip(f, g, html); g.addEventListener('focus', () => read.set(html)); g.addEventListener('blur', () => read.set(dflt()));
      nodes.push(g);
    });
    f._sync = () => setTimeout(() => { const a = f.active; cross(a && a._bt != null ? a._bt : null); }, 0);
    ['pointerover', 'pointerout', 'pointerdown', 'focusin', 'focusout', 'keydown'].forEach(ev => f.svg.addEventListener(ev, f._sync));
    CK.keynav(f, nodes);
    CK.keynav(f, snodes);
  }
  const fr = CK.frame('bt', {height: W => lay(W).H, minW: 300, maxW: 1100, label: 'One sparse parity burst through every meter on ' + BT.card +
    ': the board’s point sample, the PMIC’s average of it and the three rails, with the solves and the passes under the time axis', draw});
  document.addEventListener('pointerdown', () => fr._sync && fr._sync());
  read.set(dflt());

  /* the caption's numbers */
  const all = (fn, dp, unit) => rng(Math.min(...X.map(fn)), Math.max(...X.map(fn)), dp, unit);
  setHTML('bt-card', `${esc(BT.card)} at ${andList(BT.mhz.map(v => num(v, 0)))} MHz`);
  setHTML('bt-sizes', spSizes());
  setHTML('bt-hz', `${num(BT.sampler_hz, 0)} Hz`);
  const short = X.reduce((a, b) => (a.mean_s < b.mean_s ? a : b));
  setHTML('bt-cap-a', `An ${esc(short.label)} solve (${num(short.mean_s, 3)} s) is shorter than the time between two board values` +
    (passMs ? ` (${num(passMs, 0)} ms on this card under the sampler, TEL-S, the chart above)` : '') +
    `, so no reading prices one solve: the joules per solve in <a href="#sj-title">§4.2</a> are averages over a whole burst.`);
  const ms1 = 1000 / BT.sampler_hz;
  setHTML('bt-note', `Each run's samples from ${num(-BT.window_s[0], 0)} s before the host's first launch to ${num(BT.window_s[1], 0)} s after it, kept where one of the six readings changed` +
    (narFrom > BT.window_s[0] ? ` (on a narrow screen the chart starts ${num(-narFrom, 0)} s before it)` : '') + '. ' +
    `The sampler polls every ${num(ms1, 0)} ms, so it sees each new value up to ${num(ms1, 0)} ms after the service processor publishes it: the board's step and the ticks are drawn when the sampler saw them. ` +
    `The PMIC's average and the rails are drawn straight from one sample to the next, so their own holds show as short flat runs: they too change once a pass. ` +
    `The solves' edges are rebuilt from the host's own time for each launch (§4.2's time per solve divides the burst by its solves, so it also counts a gap), with the gaps between launches (${all(r => 1000 * r.gap, 1, 'ms')} on average, the burst's wall time less the launches' sum) spread evenly. ` +
    `The share view divides each meter's rise over its idle by its step: the point sample's from its idle before the burst to its busy mean (the catalogue's method), the PMIC average's by the same step from its own idle (the average has unit gain), ` +
    `each rail's from its idle to its plateau as the reducer estimates it; the NoC rail is left out of that view, its whole step being ${all(r => r.levels.noc_w[1] - r.levels.noc_w[0], 2, 'W')}. ` +
    `A busy reading at idle is the reducer's: a new board value in its busy window (from ${num(X[0].busy_from_s, 1)} s after the first launch to the last solve's end) below the midpoint of idle and busy. ` +
    `The board's ramps and dips inside a burst are not interpreted here. Data: each run's <code>telemetry.jsonl.gz</code>, <code>host.json</code> and <code>energy.json</code> ` +
    `(<code>workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy</code>), through <code>tools/ettelem/sync_hub_data.py</code> (the <code>burst_trace</code> block).`);
})();
