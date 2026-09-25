const STATUS = {works_now: 'works now', needs_tooling: 'tooling', needs_fw_change: 'firmware', research_only: 'research', impossible_on_silicon: 'not on silicon'};
const CHECK = {confirmed: 'confirmed by two reviewing agents', disputed: 'reviewing agents corrected details; the row reflects them', unverified: 'not reviewed', changed: 'rewritten after review', refuted: 'refuted'};
const CHECK_SYM = {confirmed: '✓', disputed: '±', unverified: '·', changed: '†', refuted: '✗'};
const REPO = 'https://github.com/yaroslavvb/et-soc1-prototyping/';
const PAGES = 'https://spacesheep.dev/@yaroslavvb/';
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
const chip = s => `<span class="chip ${s}">${STATUS[s]}</span>`;
const verif = c => `<span class="ck ${c}" title="${CHECK[c]}" aria-label="${CHECK[c]}">${CHECK_SYM[c] || '·'}</span>`;
const P = D.power, CARDS = ['aifoundry2', 'aifoundry3'];
const f = (v, n) => Number(v).toFixed(n == null ? 2 : n);
const num = CK.fmt.num, rng = (a, b, dp, unit) => CK.fmt.range(Math.min(a, b), Math.max(a, b), dp, unit);
const mm = a => [Math.min(...a), Math.max(...a)];
const sgn = (v, dp) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(dp == null ? 2 : dp);
const pct = (v, dp) => num(100 * v, dp == null ? 0 : dp) + '%';
const med = a => { const s = [...a].sort((p, q) => p - q), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
const setHTML = (id, h) => { const e = document.getElementById(id); if (e) e.innerHTML = h; };
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

/* ---------- numbers the hand-kept rows quote, filled from the data: {{name}} in data.json ---------- */
const TOK = (function () {
  const F = P.fit, RF = P.rail_filter, Dp = P.droop, IU = P.idle_unsensed, A2 = F.aifoundry2, A3 = F.aifoundry3, CH = P.checks;
  /* standard errors robust to the DRAM configurations' larger scatter (HC3; power.checks) */
  const rel = k => CARDS.map(c => CH.fit[c].se_hc3[k] / F[c].coef[k]);
  const pr = (a, dp) => rng(...mm(a), dp);
  const pc = a => rng(...mm(a.map(v => Math.round(100 * v))), 0) + '%';
  return {
    rf_tau: pr(CARDS.map(c => RF[c].tau_s), 2), rf_1s: pc(CARDS.map(c => RF[c].frac_1s)), rf_2s: pc(CARDS.map(c => RF[c].frac_2s)),
    droop_slope: f(Dp.mv_per_dram_offrail_w, 2), droop_n: num(Dp.n, 0), droop_rms: f(Dp.rms_mv, 2), droop_mvw: f(1 / Dp.mv_per_dram_offrail_w, 1),
    droop_slope_a3: f(CH.droop.aifoundry3.slope, 2), droop_rms_a3: f(CH.droop.aifoundry3.rms_mv, 2),
    fit_rms_a2: f(A2.rms_w, 2), fit_n_a2: num(A2.n, 0), fit_rmsd_a2: f(A2.rms_dram_w, 1), fit_nd_a2: num(A2.n_dram, 0),
    fit_rms_a3: f(A3.rms_w, 2), fit_n_a3: num(A3.n, 0), fit_rmsd: pr(CARDS.map(c => F[c].rms_dram_w), 1),
    se_minion: num(100 * Math.max(...rel('minion')), 1) + '%', se_dram: num(100 * Math.max(...rel('dram_pj_per_byte')), 0) + '%',
    se_noc_sram: rng(Math.round(100 * Math.min(...rel('noc'))), Math.round(100 * Math.max(...rel('sram'))), 0) + '%',
    minion_pct: pc(CARDS.map(c => F[c].coef.minion)), dram_pj: pr(CARDS.map(c => F[c].coef.dram_pj_per_byte), 0),
    idle_unsensed: rng(Math.round(Math.min(...CARDS.map(c => IU[c].w[0]))), Math.round(Math.max(...CARDS.map(c => IU[c].w[1]))), 0, 'W'),
    idle15: f(P.idle_73c.unsensed_w, 0),
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
      return g + `<tr><td class="lvl"><a href="${r.url}">${esc(r.title)}</a></td><td class="small">${esc(r.date)}</td><td>${r.what}</td><td class="small">${esc(r.instruments)}</td></tr>`; }).join('') + '</tbody>';
  CK.stackTable(t);
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
  document.getElementById('gran-leg').innerHTML = Object.keys(STATUS).map(chip).join(' ') +
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
      rows.map(r => `<tr id="${ladId(r.level)}"><td class="lvl">${esc(r.level)}</td><td>${esc(fill(r.what))}` +
        (r.note ? `<details class="lnote"${open ? ' open' : ''}><summary>note</summary><div class="small">${esc(fill(r.note))}</div></details>` : '') +
        `</td><td>${esc(fill(r.gran))}</td><td>${esc(r.instrument)}</td><td class="inl">${esc(r.access)}</td><td class="inl">${chip(r.status)}</td><td class="inl">${verif(r.check)}</td></tr>`).join('') + '</tbody>';
    CK.stackTable(t);
    GRAN.filter(filter);
  }
  const onWide = () => t.querySelectorAll('details.lnote').forEach(d => { d.open = wide.matches || all; });
  if (wide.addEventListener) wide.addEventListener('change', onWide);
  render();
  return {set(k) { if (filter !== k) { filter = k; render(); } }};
})();

/* ---------- how many identical events before the meter sees one? ---------- */
(function () {
  const E = D.energy_events, M = E.meter, FAM = E.families, EV = E.events;
  const famOf = Object.fromEntries(FAM.map(([k, l, c]) => [k, {l, c}]));
  const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹', sup = n => (n < 0 ? '⁻' : '') + String(Math.abs(n)).split('').map(d => SUP[+d]).join('');
  const sci = (v, sig) => { let e = Math.floor(Math.log10(v)), m = +(v / Math.pow(10, e)).toPrecision(sig); if (m >= 10) { m /= 10; e += 1; } return `${num(m, sig - 1)}×10${sup(e)}`; };
  const UNITS = [[1e-3, 'mJ'], [1e-6, 'µJ'], [1e-9, 'nJ'], [1e-12, 'pJ'], [1e-15, 'fJ'], [1e-18, 'aJ']];
  const J = (v, sig) => { const u = UNITS.find(([s]) => v >= s * 0.9995) || UNITS[UNITS.length - 1]; const x = v / u[0]; return (sig ? num(+x.toPrecision(sig)) : num(x)) + ' ' + u[1]; };
  const JR = (lo, hi) => { const u = UNITS.find(([s]) => lo >= s * 0.9995) || UNITS[UNITS.length - 1]; return rng(+(lo / u[0]).toPrecision(3), +(hi / u[0]).toPrecision(3), undefined, u[1]); };
  const PREC = [0.5, 0.3, 0.2, 0.1, 0.06, 0.05, 0.03, 0.02];
  const st = {data: 'random', sigma: 0.2, prec: 0.06, sel: 'wire-free'};
  const V = e => e.v[st.data] || e.v.any;
  const need = e => st.sigma / (st.prec * V(e).e[0]);
  const emin = e => st.sigma / (st.prec * V(e).rate);
  const seen = e => V(e).rate >= need(e);
  const read = CK.readout('ev-read');
  const ctl = document.getElementById('ev-ctl');
  const box = n => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.seg(box(), {label: 'Operands', options: [['random', 'random data'], ['zeros', 'zeros']], value: st.data, onChange: v => { st.data = v; upd(); }});
  CK.range(box(), {label: 'Baseline uncertainty σ', min: 0.01, max: 0.2, step: 0.01, value: st.sigma, fmt: v => num(v, 2) + ' W', onInput: v => { st.sigma = v; upd(); }});
  CK.range(box(), {label: 'Precision', stops: PREC, value: st.prec, fmt: v => '±' + num(100 * v, 0) + '%', onInput: v => { st.prec = v; upd(); }});
  const sb = box(); sb.className = 'sel';
  const lab = document.createElement('label'); lab.htmlFor = 'ev-select'; lab.textContent = 'Event';
  const sel = document.createElement('select'); sel.id = 'ev-select';
  sel.innerHTML = FAM.map(([k, l]) => `<optgroup label="${esc(l)}">` + EV.filter(e => e.family === k).map(e => `<option value="${e.id}">${esc(e.label)}</option>`).join('') + '</optgroup>').join('');
  sel.value = st.sel; sel.onchange = () => select(sel.value);
  sb.append(lab, sel);
  /* an instruction's label starts with its mnemonic, which keeps its case */
  const title = e => { if (e.family === 'instr') { const m = e.label.match(/^(\S+)(.*)$/); return `<code>${esc(m[1])}</code>${esc(m[2])}`; } return esc(e.label[0].toUpperCase() + e.label.slice(1)); };
  function describe(e) {
    const v = V(e), ok = seen(e), ratio = ok ? v.rate / need(e) : need(e) / v.rate, lift = v.rate * v.e[0], got = st.sigma / lift;
    const cards = Object.keys(v.cards || {}).length ? ` (aifoundry2 ${J(v.cards.aifoundry2)}, aifoundry3 ${J(v.cards.aifoundry3)})` : '';
    const range = v.e[1] < v.e[2] ? ` [${JR(v.e[1], v.e[2])}]` : '';
    const opnd = e.v.any ? '' : (st.data === 'random' ? ', random data' : ', zeros');
    return `<b>${title(e)}</b>${opnd}: ${J(v.e[0])}${range} per ${e.unit}${cards}. At ±${num(100 * st.prec, 0)}% against a ${num(st.sigma, 2)} W baseline it needs about ${sci(need(e), 1)} a second; ` +
      `the measurement ran it at ${sci(v.rate, 2)} a second (${num(lift, lift < 10 ? 1 : 0)} W), which that baseline prices to about ±${num(100 * got, got < 0.1 ? 1 : 0)}%, ` +
      `so at these settings the meter ${ok ? `sees it (${num(ratio, ratio < 10 ? 1 : 0)}× to spare)` : `does not see it (${num(ratio, ratio < 10 ? 1 : 0)}× short)`}. ` +
      `Source: <a href="${e.src.url}">${esc(e.src.label)}</a>${e.note ? `; ${esc(e.note)}` : ''}.`;
  }
  function select(id) { st.sel = id; sel.value = id; upd(true); }
  function upd(keepFocus) {
    const k = EV.filter(seen).length, e = EV.find(x => x.id === st.sel);
    read.set(`At these settings the meter sees <b>${k} of ${EV.length}</b> events. ` + describe(e));
    fr.redraw();
  }
  const T = 44, B = 40, hH = 24, NAR = W => W < 800, rH = W => (NAR(W) ? 30 : 19);  /* below 800 px each label gets its own line */
  const layout = W => { let y = T; const out = []; FAM.forEach(([k]) => { out.push({head: k, y}); y += hH; EV.filter(e => e.family === k).forEach(e => { out.push({e, y}); y += rH(W); }); }); return {rows: out, H: y + B}; };
  const TICKS = [[1e-17, '10 aJ'], [1e-16, '100 aJ'], [1e-15, '1 fJ'], [1e-14, '10 fJ'], [1e-13, '100 fJ'], [1e-12, '1 pJ'], [1e-11, '10 pJ'], [1e-10, '100 pJ'], [1e-9, '1 nJ'], [1e-8, '10 nJ'], [1e-7, '100 nJ'], [1e-6, '1 µJ'], [1e-5, '10 µJ'], [1e-4, '100 µJ'], [1e-3, '1 mJ'], [1e-2, '10 mJ']];
  function draw(f) {
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
  const fr = CK.frame('ev', {height: W => layout(W).H, minW: 300, maxW: 1288, label: 'Energy per event for every event the reports priced, against what the meter resolves', draw});
  /* the defaults, stated once in the caption */
  const at = (id, data) => { const e = EV.find(x => x.id === id), v = e.v[data] || e.v.any; return [v.e[0], 0.2 / (0.06 * v.e[0])]; };
  const w1 = at('wire-free', 'random'), w2 = at('i-fmadd.ps', 'random');
  setHTML('ev-golden', `At the defaults (σ = 0.2 W, ±6%), one random bit carried 1 mm (${J(w1[0], 2)}) needs about ${sci(w1[1], 1)} a second and an fmadd.ps on random data (${J(w2[0], 2)}) about ${sci(w2[1], 1)}.`);
  const hot = EV.find(x => x.id === 's-contended').v.any;
  const ring = EV.find(x => x.id === 'm-xshire1');
  setHTML('ev-note', `σ defaults to 0.2 W, about the idle law's rms (${num(M.idle_law_rms_w, 3)} W): the uncertainty of a baseline predicted from temperature. The hot line's contended atomic, about ${num(hot.e[0] * hot.rate, 1)} W over idle, carries a bar of ${sgn(100 * (hot.e[1] / hot.e[0] - 1), 0)}% to ${sgn(100 * (hot.e[2] / hot.e[0] - 1), 0)}%, about that size. ` +
    `A burst bracketed by idle measured just before and after does better than σ = 0.2 W, which is why some hollow events still carry bars of a few per cent (${esc(ring.label)}: ${sgn(100 * (ring.v.any.e[1] / ring.v.any.e[0] - 1), 0)}% to ${sgn(100 * (ring.v.any.e[2] / ring.v.any.e[0] - 1), 0)}%); the flips and the wires were priced by fits over many bursts. ` +
    `Each event's rate is ${esc(E.rate_rule)}. The band is one reading's step on aifoundry2 while ettelem samples, 1 mW × about ${num(1000 * M.pass_s, 0)} ms on a rail and 10 mW × ${num(1000 * M.pass_s, 0)} ms on the board ` +
    `(a reading lasts about ${num(1000 * M.pass_s_a3, 0)} ms on aifoundry3, and the SP's own pass on aifoundry2 is ${num(1000 * M.sp_pass_s_quiet_a2, 0)} ms without the sampler); the rail's own average spreads a single event over about a second.`);
  upd();
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
/* Each card's configurations as the fit sees them; the refit counts st_stream's bytes twice (the line read). */
const PC = Object.fromEntries(CARDS.map(c => [c, P.per_config[c].map(r => ({cfg: r[0], over: r[1], mi: r[2], sr: r[3], no: r[4], g: r[5],
  un: r[1] - r[2] - r[3] - r[4], k: klass(r[0]), rnd: r[0].includes('/random')}))]));
function fitOf(card, line) {
  const R = PC[card], dram = r => r.g * 1e-3 * (line && r.k === 'st' ? 2 : 1);
  let coef;
  if (!line) { const c = P.fit[card].coef; coef = [c.minion, c.sram, c.noc, c.dram_pj_per_byte]; } else {
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
  const R2 = RF.aifoundry2, R3 = RF.aifoundry3;
  setHTML('rf-fall', `${pct(R2.frac_1s)} of the way after one second and ${pct(R2.frac_2s)} after two on aifoundry2 (τ ≈ ${f(R2.tau_s, 2)} s), ` +
    `${pct(R3.frac_1s)} and ${pct(R3.frac_2s)} on aifoundry3 (τ ≈ ${f(R3.tau_s, 2)} s; the median over ${num(R2.n, 0)} bursts of the energy manual's catalogue on aifoundry2 and ${num(R3.n, 0)} on aifoundry3)`);
  const s2 = SA.aifoundry2, s3 = SA.aifoundry3, low = s2.slow.map(b => b.noc_other_passes_w - b.noc_w);
  setHTML('ring-ms', `${rng(...mm(SA.ring.median_ms), 0, 'ms')} (the median in each of ${word(SA.ring.passes)} passes)`);
  setHTML('sampler-dram', `DRAM reads slow it too on aifoundry2: over a burst of tensor loads or row walks from DRAM, the median sample takes ${rng(...s2.read_median_ms, 0, 'ms')}, ` +
    `the longest single one ${num(s2.read_max_ms, 0)} ms, while every aifoundry3 burst stays at ${rng(...s3.read_median_ms, 0, 'ms')}. The catalogue keeps those bursts: their board watts stand to aifoundry3's ` +
    `as every other configuration's do (aifoundry3 ÷ aifoundry2 ${rng(...SA.reads_a3_over_a2, 2)}, against ${num(SA.cross_card.p10, 2)}–${num(SA.cross_card.p90, 2)} for the middle 80% of the catalogue), ` +
    `though in the ${word(s2.over_60ms)} slowest of aifoundry2's ${num(s2.bursts, 0)} bursts (a median over 60 ms) the rails' readings are stale and the NoC rail reads ${rng(...mm(low), 1)} W below the same configuration's other passes ` +
    `(aifoundry2's alone: ${s3.over_60ms ? `${word(s3.over_60ms)} of aifoundry3's bursts slowed too` : `none of aifoundry3's ${num(s3.bursts, 0)} slowed`}).`);
  setHTML('idle-unsensed', `${f(I.unsensed_w, 1)} W of the ${f(I.board_w, 1)} W the board draws at ${num(I.die_c, 0)} °C on aifoundry2 (one 60 s window), about half`);
  setHTML('idle-unsensed-a3', `On aifoundry3, which idles cooler, it is about half too: ${rng(...IU.aifoundry3.w, 1, 'W')} of ${rng(...IU.aifoundry3.board_w, 1, 'W')} over the catalogue's idle gaps, at ${rng(...IU.aifoundry3.die_c, 0, '°C')}.`);
  setHTML('fit-n', `${num(F.aifoundry3.n, 0)} configurations (${num(F.aifoundry2.n, 0)} on aifoundry2)`);

  /* the fit table and the text under it */
  const hosts = CARDS;
  document.getElementById('fittab').innerHTML = '<thead><tr><th>unmetered W of a configuration =</th>' + hosts.map(h => `<th class="num">${h}</th>`).join('') + '</tr></thead><tbody>' +
    [['× minion-rail W', 'minion', 3, ''], ['× SRAM-rail W', 'sram', 3, ''], ['× NoC-rail W', 'noc', 3, ''], ['pJ per DRAM byte', 'dram_pj_per_byte', 1, ' pJ/B']].map(r =>
      `<tr><td>${r[0]}</td>` + hosts.map(h => `<td class="num">${f(F[h].coef[r[1]], r[2])} ± ${f(CH.fit[h].se_hc3[r[1]], r[2])}${r[3]}</td>`).join('') + '</tr>').join('') +
    '<tr><td class="small">residual rms, configuration means</td>' + hosts.map(h => `<td class="num small">${f(F[h].rms_w)} W, n = ${F[h].n}</td>`).join('') + '</tr></tbody>';
  const fit = Object.fromEntries(CARDS.map(c => [c, fitOf(c, false)])), refit = Object.fromEntries(CARDS.map(c => [c, fitOf(c, true)]));
  const all = CARDS.flatMap(c => fit[c].pts), full = p => /^(tload|tstore)\/dram\/|^dramrow\/stride1K\//.test(p.cfg);
  const cm = k => CARDS.map(c => F[c].coef[k]), dif = a => 100 * (Math.max(...a) / Math.min(...a) - 1);
  const quarter = CARDS.map(c => { const d = fit[c].pts.filter(p => p.g > 0); return fit[c].rmsd / (d.reduce((s, p) => s + p.un, 0) / d.length); });
  const stR = all.filter(p => p.k === 'st').map(p => p.res), rR = all.filter(p => full(p) && p.rnd).map(p => p.res), zR = all.filter(p => full(p) && !p.rnd).map(p => -p.res);
  setHTML('fittext', `Four coefficients, no intercept, fitted per card to the mean of each configuration's three passes (${F.aifoundry2.n} configurations on aifoundry2, which also ran six DRAM-row configurations, ${F.aifoundry3.n} on aifoundry3), ` +
    `on bursts of ${rng(...mm(all.map(p => p.over)), 1)} W over idle. DRAM bytes are the bytes the DRAM load, store and row configurations move; stores through the L1 (<code>st_stream</code>) count only the bytes written, not the line read before each write. ` +
    `Each ± is one standard error, robust to the larger scatter of the DRAM configurations. ` +
    `The minion coefficient is pinned to about ${TOK.se_minion} (one standard error) on each card but differs by ${num(dif(cm('minion')), 0)}% between them, about the cards' spread elsewhere in the manual; ` +
    (() => { const se = CARDS.map(c => CH.fit[c].se_hc3.dram_pj_per_byte), v = cm('dram_pj_per_byte'), s = se.map(x => num(x, 0));
      return Math.abs(v[0] - v[1]) <= 2.58 * Math.hypot(...se)
        ? `the DRAM terms agree within their errors (${f(v[0], 1)} and ${f(v[1], 1)} pJ/B, ${s[0] === s[1] ? `each ±${s[0]}` : `±${s[0]} and ±${s[1]}`}). `
        : `the DRAM terms differ by ${num(dif(v), 0)}%. `; })() +
    `The SRAM and NoC coefficients are collinear with each other (not with the minion one) and uncertain to ${TOK.se_noc_sram}` +
    CARDS.filter(c => CH.fit[c].pass_ci99.sram[0] <= 0).map(c => `; the SRAM one is not distinguishable from zero on ${c}, whose ${word(CH.fit[c].pass_coef.sram.length)} passes fit it at ${rng(...mm(CH.fit[c].pass_coef.sram), 2)}`).join('') +
    `. The residual is small overall but not on DRAM traffic: ${rng(...CARDS.map(c => fit[c].rmsd), 1)} W rms on the DRAM configurations, ` +
    `about a quarter of their unmetered power (${CARDS.map(c => c.slice(-1) === '2' ? pct(quarter[0]) : pct(quarter[1])).join(' and ')}). It has a pattern: the three stores through the L1 sit ${rng(...mm(stR), 1)} W above the fit, because their line reads are not counted ` +
    `(counting them brings the DRAM rms to ${rng(...CARDS.map(c => refit[c].rmsd), 2)} W: the checkbox in the chart below); on the full-rate tensor loads, tensor stores and row walks, random data sits ${rng(...mm(rR), 1)} W above it and zeros or constants ${rng(...mm(zR), 1)} W below.`);

  /* 'three things follow', from the per-configuration rows (the full-rate DRAM configurations; st_stream apart) */
  const off = all.filter(p => p.g > 0 && full(p)).map(p => ({...p, pj: (p.un - p.loss) / (p.g * 1e-3), tot: p.over / (p.g * 1e-3)}));
  const offSt = all.filter(p => p.k === 'st').map(p => (p.un - p.loss) / (p.g * 1e-3));
  const zc = off.filter(p => !p.rnd), rd = off.filter(p => p.rnd), tl = off.filter(p => p.cfg.startsWith('tload/dram/') && !p.cfg.endsWith('const'));
  const a2 = F.aifoundry2.coef.minion, a3 = F.aifoundry3.coef.minion, perPct = 100 * (1 + a2) * (1 / 0.99 - 1), scale = 100 * (1 - (1 + Math.min(a2, a3)) / (1 + Math.max(a2, a3)));
  const r0 = v => Math.round(v);
  setHTML('three-things', `<b>Three things follow.</b> <b>An instruction's unmetered energy is consistent with a regulator's delivery loss</b>: ` +
    `${pct(F.aifoundry2.coef.minion)} of what the minion rail delivers on aifoundry2 and ${pct(F.aifoundry3.coef.minion)} on aifoundry3 goes missing between the 12 V input and the core, ` +
    `as far as the rails' own meters can be trusted: the figure rests on their gain and on the correction for their one-second average, and each 1% in either moves it by about ${num(perPct, 1)} points ` +
    `(a ${num(scale, 1)}% difference in rail scale would explain the two cards' ${num(dif(cm('minion')), 0)}%; the mesh rail's gain is not checked either, <a href="${PAGES}et-soc1-heat-per-mm#limits">Heat per millimetre, §10</a>). Nothing else moves. ` +
    `<b>A DRAM byte's unmetered energy is the memory's</b>: the fitted ${TOK.dram_pj} pJ per byte, off the rails, in the DDR PHY, the I/O rail and the DRAM chips (${rng(...mm(zc.map(p => r0(p.pj))), 0)} on zeros and constants, ` +
    `${rng(...mm(rd.map(p => r0(p.pj))), 0)} on random data, per configuration), on top of the ${rng(...mm(off.map(p => r0(p.tot - p.pj))), 0)} pJ the mesh, the SRAM and the delivery losses take on the way: ` +
    `together ${rng(...mm(tl.map(p => r0(p.tot))), 0)} pJ per byte for tensor loads from DRAM, zeros to random data. A byte written through the L1 costs about twice that off-rail (${rng(...mm(offSt.map(r0)), 0)} pJ), ` +
    `because the line is read from DRAM before it is written. <b>And the NoC coefficient is not all regulator</b>: ${rng(...mm(cm('noc').map(v => r0(100 * v))), 0)}% is more than a delivery loss would take; ` +
    `the likely rest, not measured, is the memory shires' own logic, on an unmetered rail, which works whenever the mesh moves bytes to them. What the fit cannot say is how the idle ${TOK.idle_unsensed} (${rng(r0(IU.aifoundry3.w[0]), r0(IU.aifoundry3.w[1]), 0, 'W')} on aifoundry3 at ` +
    `${rng(r0(IU.aifoundry3.die_c[0]), r0(IU.aifoundry3.die_c[1]), 0, '°C')}, ${rng(r0(IU.aifoundry2.w[0]), r0(IU.aifoundry2.w[1]), 0, 'W')} on aifoundry2 at ${rng(r0(IU.aifoundry2.die_c[0]), r0(IU.aifoundry2.die_c[1]), 0, '°C')}) ` +
    `splits between DDR refresh and PHY, PCIe, the IO shire, Maxion and the regulators' own draw, nor how the DRAM term splits below the regulator.`);

  /* §5's paragraph */
  const dUn = all.filter(p => full(p) || p.k === 'st').map(p => p.un), c2 = F.aifoundry2.coef, U3 = IU.aifoundry3;
  const w0 = a => rng(Math.round(a[0]), Math.round(a[1]), 0, 'W');
  setHTML('unmet-today', `${f(I.unsensed_w, 0)} W of a ${f(I.board_w, 0)} W idle on aifoundry2 (${w0(U3.w)} of ${w0(U3.board_w)} on aifoundry3) and ${rng(...mm(dUn), 1)} W of a full-rate DRAM workload are on no sensor`);
  setHTML('idle15b', rng(Math.round(Math.min(...CARDS.map(c => IU[c].w[0]))), Math.round(Math.max(...CARDS.map(c => IU[c].w[1]))), 0));
  setHTML('idle-nometer', `about ${f(I.unsensed_w - (c2.minion * I.minion_w + c2.sram * I.sram_w + c2.noc * I.noc_w), 0)} W of aifoundry2's idle at ${num(I.die_c, 0)} °C, ` +
    `if the loss fractions fitted above idle also hold for the rails' idle power (an assumption)`);

  /* ---------- V1: where a workload's watts go ---------- */
  const share = (c, k) => pct(med(fit[c].pts.filter(p => k(p)).map(p => p.un / p.over)));
  setHTML('v1-cap', `Of what each configuration adds above idle, how much is on no sensor, and does the four-term fit account for it? The scatter: every catalogue configuration's unmetered watts ` +
    `(board over idle less the three rails) against what the fit gives it; filled dots ran on random data, open ones on zeros or constants. The first bar: the idle card at ${num(I.die_c, 0)} °C on aifoundry2 ` +
    `(${f(I.board_w, 2)} W, the mean of one 60 s window of ${num(I.samples, 0)} samples whose standard deviation is ${f(I.board_sd, 2)} W, after ${num(I.hours, 1)} h idle apart from a 4.9 s probe five minutes before the window): ${f(I.unsensed_w, 1)} W of it is on no sensor ` +
    `and cannot be split further. The second bar: the chosen configuration's watts over idle, the three rails and then the fit's delivery loss and DRAM term, with the measured total as a tick. ` +
    `Above idle, about a sixth of an instruction's watts are on no sensor (median ${share('aifoundry2', p => p.k === 'instr')} on aifoundry2, ${share('aifoundry3', p => p.k === 'instr')} on aifoundry3) ` +
    `and about two thirds of DRAM traffic's (${share('aifoundry2', p => p.g > 0)} and ${share('aifoundry3', p => p.g > 0)}). Hover, tap or tab to a point to break it down; arrows step through the points in residual order.`);
  const st = {card: 'aifoundry2', line: false, on: new Set(CLS.map(c => c[0])), sel: 'tload/dram/random'};
  const ctl = document.getElementById('v1-ctl'), box = () => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.seg(box(), {label: 'Card', options: CARDS.map(c => [c, c]), value: st.card, onChange: v => { st.card = v; fr.redraw(); out(); }});
  const cb = box(); cb.innerHTML = '<label class="chk"><input type="checkbox" id="v1-line"> Count the line read before each L1 store</label>';
  document.getElementById('v1-line').addEventListener('change', ev => { st.line = ev.target.checked; fr.redraw(); out(); });
  const legHost = document.getElementById('v1-leg'), l1 = document.createElement('div'), l2 = document.createElement('div');
  legHost.append(l1, l2);
  CK.legend(l1, CLS.map(([k, l, c]) => ({key: k, label: l, mark: 'dot', color: c})), {toggle: true, onChange: keys => { st.on = new Set(keys); fr.redraw(); }});
  const SEG = [['mi', 'minion rail', 'var(--c1)'], ['sr', 'SRAM rail', 'var(--c3)'], ['no', 'NoC rail', 'var(--c2)'], ['loss', 'delivery loss (fit)', 'var(--c7)'],
    ['dr', 'DRAM term (fit)', 'var(--c4)'], ['none', 'on no sensor, idle', 'color-mix(in srgb, var(--ref) 45%, var(--surface))']];
  CK.legend(l2, SEG.map(([k, l, c]) => ({key: k, label: l, mark: 'box', color: c})).concat([{key: 'm', label: 'measured total', mark: 'line', color: 'var(--ink)'}]));
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
    read.set(`${pretty(p.cfg)} on ${st.card}: ${f(p.over, 2)} W over idle; the rails ${f(rail, 2)} W (minion ${f(p.mi, 2)}, SRAM ${f(p.sr, 2)}, NoC ${f(p.no, 2)}); on no sensor ${f(p.un, 2)} W (${pct(p.un / p.over)}): ` +
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
    bar(by + 22, [['mi', I.minion_w, 'minion'], ['sr', I.sram_w, 'SRAM'], ['no', I.noc_w, 'NoC'], ['none', I.unsensed_w, 'no sensor']], `Idle at ${num(I.die_c, 0)} °C (aifoundry2): ${f(I.board_w, 1)} W`);
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
    const pts = cur().pts.filter(p => st.on.has(p.k)).sort((p, q) => p.res - q.res), nodes = [];
    circ = {};
    pts.forEach(p => {
      const cx = x(Math.min(8, Math.max(0, p.fit))), cy = y(Math.min(8, Math.max(0, p.un))), c = CLC[p.k];
      const n = CK.el('circle', {cx, cy, r: p.cfg === st.sel ? 6 : 3.8, 'stroke-width': 1.6, stroke: c, fill: p.rnd ? c : 'var(--surface)', class: p.cfg === st.sel ? 'pt-sel' : null}, a);
      circ[p.cfg] = n;
      CK.tip(fm, n, `<b>${pretty(p.cfg)}</b> · ${st.card}<br>unmetered ${f(p.un, 2)} W, the fit ${f(p.fit, 2)} W, residual ${sgn(p.res)} W<br>${f(p.over, 2)} W over idle, ${pct(p.un / p.over)} of it on no sensor`);
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
  const DC = CH.droop, d2 = DC.aifoundry2, d3 = DC.aifoundry3;
  const both = (v2, v3, u) => (v2 === v3 ? `${v2} ${u} on both cards` : `${v2} ${u} on aifoundry2 and ${v3} on aifoundry3`);
  setHTML('droopidle', both(f(Dp.idle_die_mv.ddr, 0), f(d3.idle_ddr_mv, 0), 'mV'));
  setHTML('irdrop', `about ${f(d2.ir, 2)} mV per watt the cores draw on aifoundry2 and ${f(d3.ir, 2)} on aifoundry3`);
  setHTML('droop-mvw', `1 mV ≈ ${both(f(1 / d2.slope, 1), f(1 / d3.slope, 1), 'W').replace(' on both cards', '')}`);
  setHTML('droop-temp', `aifoundry3 idles at ${rng(...IU.aifoundry3.die_c, 0, '°C')} in the catalogue and reads ${f(d3.idle_ddr_mv, 0)} mV there`);
  const onMesh = big.filter(p => /^(wire|tload\/scp|tstore\/scp|scpline|neigh|dramrow\/stride8K)/.test(p.cfg)).length;
  setHTML('drooptext', `Over aifoundry2's ${Dp.n} catalogue configurations (its ${F.aifoundry2.n} less the ${word(F.aifoundry2.n - Dp.n)} DRAM-row ones, run separately and not in this telemetry), the DDR rail droops ` +
    `<b>${f(a, 2)} mV per watt of off-rail DRAM power</b> (the unmetered watts less the fitted rail losses), with an rms of ${f(rms, 2)} mV: ` +
    `about an eighth of the smallest DRAM burst's droop (${f(minD.dd, 2)} mV, <code>${esc(minD.cfg)}</code>). The same fit on aifoundry3's ${d3.n} configurations gives ${f(d3.slope, 2)} mV per watt (rms ${f(d3.rms_mv, 2)} mV). ` +
    `The fit also carries a small term for the rest of the board's power: ` +
    CARDS.map(c => { const z = DC[c].pass_ci99.common[0] <= 0; return `${num(DC[c].common, 3)} mV per watt on ${c}${z ? `, which its ${word(DC[c].passes.common.length)} passes do not distinguish from zero` : ''}`; }).join(', and ') + '. ' +
    `The DRAM slope rests on ${word(dRows.length)} configurations, and the ${word(big.length)} residuals above 1 mV ` +
    `(${rng(...mm(big.map(p => p.ex)), 1, 'mV')}) are all bursts with no DRAM traffic, ${word(onMesh)} of them on the mesh, the scratchpads or the L3.`);
  const NM = DC.named, nmv = (c, k) => DC[c].named[k].mean, top = Math.max(...CARDS.flatMap(c => [...NM.mesh, NM.l3].map(k => nmv(c, k))));
  const l3med = med(d2.named[NM.l3].passes);
  setHTML('droopmesh', `heavy mesh, scratchpad and L3 traffic with no DRAM access droops it by up to about ${f(top, 0)} mV on both cards (on aifoundry2 ` +
    NM.mesh.map(k => `<code>${esc(k)}</code> ${f(nmv('aifoundry2', k), 2)} mV` + (Math.abs(nmv('aifoundry2', k) - nmv('aifoundry3', k)) > 0.3 ? `, which reads ${f(nmv('aifoundry3', k), 2)} mV on aifoundry3` : '')).join(' and ') +
    `; ${f(l3med, 1)} mV for L3 reads through the mesh, <code>${esc(NM.l3)}</code>, the median of ${word(d2.named[NM.l3].passes.length)} passes), ` +
    `up to ${f(d2.max_nondram_excess_mv[0], 1)} mV more than the calibration allows on aifoundry2 and ${f(d3.max_nondram_excess_mv[0], 1)} on aifoundry3, ` +
    `which it would read as up to about ${f(Math.max(...CARDS.map(c => DC[c].max_nondram_excess_mv[0] / DC[c].slope)), 0)} W of DRAM.`);
  const mv1 = v => (Math.round(v * 10) / 10).toFixed(1);
  const dt = document.getElementById('drooptab');
  dt.innerHTML = '<thead><tr><th>Configuration (aifoundry2)</th><th class="num">W over idle</th><th class="num">unmetered W less fitted rail losses</th><th class="num">DDR-rail droop, mV</th><th class="num">minion-rail droop, mV</th></tr></thead><tbody>' +
    Dp.examples.map(e => `<tr><td><code>${esc(e.cfg)}</code></td><td class="num">${f(e.over_idle_w)}</td><td class="num">${e.dram_offrail_w ? f(e.dram_offrail_w) : '—'}</td><td class="num">${mv1(e.droop_ddr_mv)}</td><td class="num">${mv1(e.droop_minion_mv)}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(dt);
  const ds = {view: 'board', on: new Set(CLS.map(c => c[0])), sel: l3.cfg};
  const VIEWS = {board: {x: p => p.over, y: p => p.dd, xd: [0, 27], yd: [-0.5, 6.5], xl: 'board watts over idle', yl: 'DDR-rail droop, mV'},
    pred: {x: p => p.pred, y: p => p.dd, xd: [-0.5, 7], yd: [-0.5, 7], xl: 'droop the calibration predicts, mV', yl: 'DDR-rail droop measured, mV'},
    minion: {x: p => p.mi, y: p => p.dm, xd: [0, 22], yd: [-0.5, 2.5], xl: 'minion-rail watts over idle', yl: 'minion-rail droop, mV'}};
  CK.seg('dr-ctl', {label: 'View', options: [['board', 'against board watts'], ['pred', 'predicted against measured'], ['minion', 'minion rail (IR drop)']], value: ds.view, onChange: v => { ds.view = v; dfr.redraw(); dout(); }});
  CK.legend('dr-leg', CLS.map(([k, l, c]) => ({key: k, label: l, mark: 'dot', color: c})), {toggle: true, onChange: keys => { ds.on = new Set(keys); dfr.redraw(); }});
  const dread = CK.readout('dr-read');
  function dout() {
    const p = DR.find(q => q.cfg === ds.sel);
    if (ds.view === 'minion') { dread.set(`${pretty(p.cfg)}: the minion rail draws ${f(p.mi, 2)} W over idle and its monitors read ${f(p.dm, 2)} mV lower; ${f(ir, 3)} mV per watt predicts ${f(ir * p.mi, 2)} mV.`); return; }
    dread.set(`${pretty(p.cfg)}: droop ${f(p.dd, 2)} mV measured, ${f(p.pred, 2)} mV predicted (${f(a, 2)} × ${f(p.off, 2)} W off-rail DRAM + ${f(b, 3)} × ${f(p.over - p.off, 2)} W of the rest); ` +
      `excess ${sgn(p.ex)} mV, which reads as ${sgn(p.ex / a)} W of ${p.dram ? 'extra' : 'phantom'} DRAM.`);
  }
  function ddraw(fm) {
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
    const noDram = [`no DRAM: ${f(b, 3)} mV per W${P.checks.droop.aifoundry2.pass_ci99.common[0] <= 0 ? ', within noise' : ''}`, `band ± ${f(rms, 2)} mV rms`];
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
      const note = (p, s, dy) => { if (!ds.on.has(p.k)) return; const px = x(p.over), right = px > (L + W - R) / 2; CK.txt(g0, px + (right ? -9 : 8), y(p.dd) + dy, s, 'tick', right ? 'end' : 'start'); };
      note(l3, 'L3 reads through the mesh', 4); note(minD, 'smallest DRAM droop', 14);
      CK.txt(g0, W - R - 4, T + 12, '◇ predicted for a DRAM point', 'tick', 'end');
      if (fm.narrow) { const kx = W - R - 4, ky = T + 60, k = CK.el('line', {x1: kx - 22, x2: kx, y1: ky - 4, y2: ky - 4, 'stroke-dasharray': '5 4', 'stroke-width': 1.4}, g0);
        k.style.stroke = 'var(--ref)'; noDram.forEach((s, i) => CK.txt(g0, kx - 28, ky + 14 * i, s, 'tick', 'end')); }
    }
    CK.keynav(fm, nodes, {onFocus: (n, k) => dpick(pts[k].cfg)});
  }
  let dcirc = {};
  function dpick(cfg) { if (ds.sel === cfg) return; mark(dcirc, ds.sel, false); ds.sel = cfg; mark(dcirc, cfg, true); dout(); }
  const dfr = CK.frame('dr', {height: W => (W < 600 ? 340 : 380), minW: 300, maxW: 900, label: 'DDR-rail droop of every aifoundry2 catalogue configuration against board watts, its prediction, or the minion rail', draw: ddraw});
  dout();
})();

/* ---------- the improvement ladder ---------- */
(function () {
  let filter = 'all';
  const fbox = document.getElementById('impfilters'), t = document.getElementById('imptab');
  const opts = [['all', 'all rungs'], ['done', 'done'], ['works_now', 'works now'], ['needs_tooling', 'tooling or lab hardware'], ['needs_fw_change', 'firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon']];
  function render() {
    fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('');
    fbox.querySelectorAll('button').forEach(b => { b.onclick = () => { filter = b.dataset.k; render(); }; });
    const rows = D.improvements.filter(r => filter === 'all' || (filter === 'done' ? r.done : r.status === filter));
    let group = null;
    t.innerHTML = '<thead><tr><th style="width:23%">Rung</th><th style="width:28%">What it adds</th><th style="width:15%">Cost</th><th style="width:24%">What changes in the numbers</th><th style="width:10%">Status</th></tr></thead><tbody>' +
      rows.map(r => { const g = r.group !== group ? `<tr class="grp"><td colspan="5"><b>${esc(r.group)}</b></td></tr>` : ''; group = r.group;
        const cap = !r.adds || /\.$/.test(r.adds), see = r.row ? `${r.adds ? ' ' : ''}<a href="#${ladId(r.row)}" class="seerow" data-row="${esc(r.row)}">${cap ? 'See' : 'see'} §2: ${esc(r.row)}</a>` : '';
        return g + `<tr><td class="lvl">${r.rung}. ${esc(r.what)}${r.done ? ' <span class="verif confirmed">done</span>' : ''}</td><td>${esc(fill(r.adds))}${see}</td><td class="small">${esc(r.cost)}</td><td>${esc(fill(r.effect))}</td><td class="inl">${chip(r.status)}</td></tr>`; }).join('') + '</tbody>';
    t.querySelectorAll('a.seerow').forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); goRow(a.dataset.row); }));
    CK.stackTable(t);
  }
  render();
})();

/* ---------- the sessions table (§7) ---------- */
/* Raw-data paths are stored in full and shown without the common docs/reports/data/ prefix; directories link to
   GitHub's tree view, files to the blob view. */
const rawLink = p => { const PRE = 'docs/reports/data/'; return `<a href="${REPO}${p.path.endsWith('/') ? 'tree' : 'blob'}/main/${p.path}"><code>${esc(p.path.startsWith(PRE) ? p.path.slice(PRE.length) : p.path)}</code></a>${p.note ? ' (' + esc(p.note) + ')' : ''}`; };
(function () {
  const t = document.getElementById('sessionstab');
  t.innerHTML = '<thead><tr><th style="width:7%">Session</th><th style="width:9%">When</th><th style="width:8%">Card</th><th style="width:28%">What it measured</th><th style="width:14%">Instruments</th><th style="width:21%">Raw data</th><th style="width:13%">Reports</th></tr></thead><tbody>' +
    D.sessions.map(r => `<tr><td class="lvl">${esc(r.id)}</td><td class="small">${esc(r.when)}</td><td class="small">${esc(r.card)}</td><td>${esc(r.what)}</td><td class="small">${esc(r.instruments)}</td><td class="small">${r.data.map(rawLink).join('<br>')}</td><td class="small">${r.reports.map(x => `<a href="${x.url}">${esc(x.title)}</a>`).join('<br>')}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
  setHTML('nsess', String(D.sessions.length));
})();

/* ---------- V2: the reports and sessions map (§1) ---------- */
(function () {
  const GROUPS = [['This hub', 'Hub', 'var(--ref)'], ['Energy and power', 'Energy and power', 'var(--c1)'], ['Contention and moving data', 'Contention', 'var(--c3)'],
    ['Memory and compute baselines, 18–19 September', 'Baselines', 'var(--c4)'], ['Research and exploratory', 'Research', 'var(--c5)'],
    ['Briefs: analysis, no new measurements', 'Briefs', 'var(--c7)']];
  const gOf = Object.fromEntries(GROUPS.map(([k, s, c], i) => [k, {s, c, i}]));
  const base = u => u.split('#')[0];
  const REP = D.reports.map((r, i) => ({...r, key: 'r' + i, kind: 'report', grp: r.group || 'This hub', day: +r.pub.slice(8, 10)}));
  const NDAYS = Math.max(7, ...REP.map(r => r.day - 17));  // the timeline runs from 18 September to the newest report
  const repOf = u => (u.startsWith('#') ? REP[0] : REP.find(r => base(r.url) === base(u)));
  const byShort = s => REP.find(r => r.short === s);
  const parseWhen = w => {
    const m = w.match(/^(\d+)(?:–(\d+))? Sep(?:, (\d\d):(\d\d)(?:–(\d\d):(\d\d))?)?/), d0 = +m[1], d1 = m[2] ? +m[2] : d0;
    const T = (d, h, mi) => d - 18 + (h + mi / 60) / 24;
    if (m[3]) { const a = T(d0, +m[3], +m[4]); return [a, m[5] ? T(d0, +m[5], +m[6]) : a]; }
    return [T(d0, 12, 0), T(d1, 12, 0)];
  };
  const cardOf = s => (/both|all three/.test(s) || (s.includes('aifoundry2') && s.includes('aifoundry3')) ? 'both' : s.includes('aifoundry2') ? 'a2' : s.includes('aifoundry3') ? 'a3' : 'none');
  const CARD = {a2: 'aifoundry2', a3: 'aifoundry3', both: 'both cards', none: 'analysis, no card'};
  const SES = D.sessions.map((s, i) => { const [t0, t1] = parseWhen(s.when); return {...s, key: 's' + i, kind: 'session', t0, t1, lane: cardOf(s.card), name: s.id === '—' ? 'before E1' : s.id,
    reps: [...new Set(s.reports.map(x => repOf(x.url)).filter(Boolean))]}; });
  const SUP = D.superseded.map((s, i) => ({...s, key: 'e' + i, fromR: byShort(s.from), to: s.to.map(t => ({...t, r: byShort(t.report)}))}));
  const st = {sel: null, card: 'all', sup: true};
  const byKey = k => REP.find(r => r.key === k) || SES.find(s => s.key === k);
  setHTML('map-head', `${REP.length} reports · ${SES.length} sessions · ${SUP.length} superseded numbers`);
  const ctl = document.getElementById('map-ctl'), box = () => { const d = document.createElement('div'); ctl.appendChild(d); return d; };
  CK.seg(box(), {label: 'Card', options: [['all', 'both cards'], ['a2', 'aifoundry2'], ['a3', 'aifoundry3']], value: st.card, onChange: v => { st.card = v; fr.redraw(); }});
  const cb = box(); cb.innerHTML = '<label class="chk"><input type="checkbox" id="map-sup" checked> Show superseded numbers</label>';
  document.getElementById('map-sup').addEventListener('change', ev => { st.sup = ev.target.checked; fr.redraw(); });
  const panel = document.getElementById('map-panel');
  const showCard = s => st.card === 'all' || s.lane === 'both' || s.lane === 'none' || s.lane === st.card;
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
        `<dt>What it established</dt><dd>${n.what}</dd><dt>Instruments</dt><dd>${esc(n.instruments)}</dd>` +
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
    const ap = CK.el('path', {d: 'M0,0 L10,5 L0,10 Z'}, mk); ap.style.fill = 'var(--c2)';
    const gE = CK.el('g', {}, svg), gN = CK.el('g', {}, svg), nodes = [];
    const pos = {};  // key -> {x, y, w, h}
    const ses = SES.filter(showCard);
    if (!vert) {
      const L = 112, R = 10, T = 30, x = t => L + t / NDAYS * (W - L - R), rowS = 19, rowR = 26;
      for (let d = 0; d <= NDAYS; d++) { CK.el('line', {x1: x(d), x2: x(d), y1: T - 6, y2: f.H - 8, class: 'grid-line'}, gE); if (d < NDAYS) CK.txt(gE, x(d + 0.5), T - 12, `${18 + d} Sep`, 'tick', 'middle'); }
      let y = T + 4;
      const lanes = [['a2', 'aifoundry2'], ['both', 'both cards'], ['a3', 'aifoundry3'], ['none', 'analysis']];
      lanes.forEach(([ln, lab]) => {
        const items = ses.filter(s => s.lane === ln).sort((p, q) => p.t0 - q.t0), rows = [];
        if (!items.length) return;
        items.forEach(s => { const x0 = x(s.t0), w = Math.max(x(s.t1) - x0, measure(svg, s.name, 'tick') + 10); let k = rows.findIndex(e => e + 3 <= x0); if (k < 0) { rows.push(0); k = rows.length - 1; } rows[k] = x0 + w; pos[s.key] = {x: x0, y: y + k * rowS, w, h: 15}; });
        const band = CK.el('rect', {x: 0, y: y - 2, width: L - 8, height: rows.length * rowS, rx: 4}, gE);
        band.style.fill = ln === 'a2' ? 'color-mix(in srgb, var(--c1) 12%, transparent)' : ln === 'a3' ? 'color-mix(in srgb, var(--c5) 14%, transparent)' : 'color-mix(in srgb, var(--ref) 10%, transparent)';
        CK.txt(gE, 6, y + 11, lab, 'lab');
        y += rows.length * rowS + 4;
      });
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
      const T = 16, dayH = 158, xT = 40, lw = 58, xA = xT + 4, xB = xA + lw + 4, xR = xB + lw + 12, y = t => T + t * dayH;
      for (let d = 0; d <= NDAYS; d++) { CK.el('line', {x1: 0, x2: W, y1: y(d), y2: y(d), class: 'grid-line'}, gE); if (d < NDAYS) { CK.txt(gE, 2, y(d) + 14, `${18 + d}`, 'lab-strong'); CK.txt(gE, 2, y(d) + 28, 'Sep', 'tick'); } }
      CK.txt(gE, xA + lw / 2, T - 4, 'a2', 'tick', 'middle'); CK.txt(gE, xB + lw / 2, T - 4, 'a3', 'tick', 'middle');
      const bottom = {a2: 0, a3: 0};
      ses.slice().sort((p, q) => p.t0 - q.t0).forEach(s => {
        const cols = s.lane === 'a2' ? ['a2'] : s.lane === 'a3' ? ['a3'] : ['a2', 'a3'], h = Math.min(40, Math.max(16, y(s.t1) - y(s.t0))), y0 = Math.max(y(s.t0), ...cols.map(c => bottom[c] + 2));
        cols.forEach(c => { bottom[c] = y0 + h; });
        pos[s.key] = {x: cols[0] === 'a2' ? xA : xB, y: y0, w: cols.length * lw + (cols.length - 1) * 4, h};
      });
      const byDay = {};
      REP.slice().sort((p, q) => p.day - q.day || gOf[p.grp].i - gOf[q.grp].i).forEach(r => { const k = (byDay[r.day] = (byDay[r.day] || 0) + 1) - 1; pos[r.key] = {x: xR, y: y(r.day - 18) + 6 + k * 26, w: Math.min(W - xR - 34, measure(svg, r.short, 'tick') + 16), h: 20}; });
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
      const p = CK.el('path', {d, fill: 'none', class: 'mapedge', 'stroke-dasharray': '5 3', 'stroke-width': 1.5, 'marker-end': 'url(#map-arr)'}, gE); p.style.stroke = 'var(--c2)';
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
    ses.slice().sort((p, q) => p.t0 - q.t0).forEach(s => addNode(s, `<b>${esc(s.name)}</b> · ${esc(s.when)} · ${CARD[s.lane]}<br>${esc(s.what)}`, (g, p) => {
      const mix = c => `color-mix(in srgb, ${c} 30%, var(--surface))`;
      if (s.lane === 'both') {
        CK.el('rect', {x: p.x, y: p.y, width: p.w, height: p.h / 2, fill: mix('var(--c1)')}, g);
        CK.el('rect', {x: p.x, y: p.y + p.h / 2, width: p.w, height: p.h / 2, fill: mix('var(--c5)')}, g);
        CK.el('rect', {x: p.x, y: p.y, width: p.w, height: p.h, rx: 3, fill: 'none', stroke: 'var(--ink-2)', 'stroke-width': 1}, g);
      } else {
        const c = s.lane === 'a2' ? 'var(--c1)' : s.lane === 'a3' ? 'var(--c5)' : 'var(--ref)';
        CK.el('rect', {x: p.x, y: p.y, width: p.w, height: p.h, rx: 3, fill: s.lane === 'none' ? 'var(--surface)' : mix(c), stroke: c, 'stroke-width': 1.2, 'stroke-dasharray': s.lane === 'none' ? '3 2' : null}, g);
      }
      CK.el('rect', {x: p.x, y: p.y, width: p.w, height: p.h, class: 'ck-hit'}, g);
      const t = CK.txt(g, p.x + 5, p.y + Math.min(p.h, 15) / 2 + 4, s.name, 'tick'); t.style.fill = 'var(--ink)'; t.style.fontWeight = '600';
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
