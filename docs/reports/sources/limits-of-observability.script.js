const STATUS = {works_now: 'works now', needs_tooling: 'tooling', needs_fw_change: 'firmware', research_only: 'research', impossible_on_silicon: 'not on silicon'};
const CHECK = {confirmed: 'confirmed by two reviewing agents', disputed: 'reviewing agents corrected details; the row reflects them', unverified: 'not reviewed', changed: 'rewritten after review', refuted: 'refuted'};
const CHECK_SYM = {confirmed: '✓', disputed: '±', unverified: '·', changed: '†', refuted: '✗'};
const REPO = 'https://github.com/yaroslavvb/et-soc1-prototyping/';
const NS = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function txt(parent, x, y, s, cls, anchor) { const t = el('text', {x, y, class: cls || 'tick', 'text-anchor': anchor || 'start'}, parent); t.textContent = s; return t; }
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
const chip = s => `<span class="chip ${s}">${STATUS[s]}</span>`;
const verif = c => `<span class="ck ${c}" title="${CHECK[c]}" aria-label="${CHECK[c]}">${CHECK_SYM[c] || '·'}</span>`;

/* ---------- granularity figure ---------- */
(function () {
  const rows = D.ladder.filter(r => r.sec);
  const W = 900, H = 60 + rows.length * 19, L = 250, R = 20, T = 28;
  const host = document.getElementById('gran'); host.innerHTML = '';
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img'}, host);
  const tip = document.createElement('div'); tip.className = 'tip'; host.appendChild(tip);
  const lx = v => Math.log10(v);
  const x = v => L + (lx(v) - lx(1e-9)) / (lx(10) - lx(1e-9)) * (W - L - R);
  const ticks = [[1e-9, '1 ns'], [1e-8, '10 ns'], [1e-7, '100 ns'], [1e-6, '1 µs'], [1e-5, '10 µs'], [1e-4, '100 µs'], [1e-3, '1 ms'], [1e-2, '10 ms'], [1e-1, '100 ms'], [1, '1 s'], [10, '10 s']];
  for (const [v, s] of ticks) { el('line', {x1: x(v), x2: x(v), y1: T - 6, y2: H - 22, class: 'grid-line'}, svg); txt(svg, x(v), H - 6, s, 'tick', 'middle'); }
  txt(svg, x(1.67e-9) + 4, T - 12, '1 cycle at 600 MHz', 'lab');
  el('line', {x1: x(1.67e-9), x2: x(1.67e-9), y1: T - 8, y2: H - 22, stroke: 'var(--axis)', 'stroke-width': 1, 'stroke-dasharray': '3 3'}, svg);
  rows.forEach((r, i) => {
    const y = T + 8 + i * 19;
    const g = el('g', {}, svg);
    txt(g, L - 8, y + 4, r.level, 'lab', 'end');
    el('line', {x1: L, x2: W - R, y1: y, y2: y, class: 'grid-line', opacity: 0.5}, g);
    const col = {works_now: 'var(--ok)', needs_tooling: 'var(--warn)', needs_fw_change: 'var(--c1)', research_only: 'var(--muted)', impossible_on_silicon: 'var(--bad)'}[r.status];
    el('circle', {cx: x(r.sec), cy: y, r: 6, fill: col, stroke: 'var(--surface)', 'stroke-width': 2}, g);
    el('rect', {x: 0, y: y - 9, width: W, height: 18, fill: 'transparent'}, g);
    const show = ev => { tip.innerHTML = `<b>${esc(r.level)}</b><br>${esc(r.gran)}<br>${chip(r.status)}`; tip.style.display = 'block';
      const b = host.getBoundingClientRect(); const p = ev.touches ? ev.touches[0] : ev;
      tip.style.left = Math.min(p.clientX - b.left + 12, b.width - 300) + 'px'; tip.style.top = (p.clientY - b.top + 12) + 'px'; };
    g.addEventListener('mousemove', show); g.addEventListener('touchstart', show, {passive: true});
    g.addEventListener('mouseleave', () => tip.style.display = 'none');
  });
  const leg = document.createElement('div'); leg.className = 'legend';
  leg.innerHTML = Object.keys(STATUS).map(k => chip(k)).join(' ') + ' <span class="small">· rows without a single time step (per-launch counts, whole-program traces, one-shot dumps, RTL simulation) are in the table only</span>';
  host.appendChild(leg);
})();

/* ---------- ladder table with filter ---------- */
(function () {
  let filter = 'all';
  const fbox = document.getElementById('filters');
  const opts = [['all', 'all rows'], ['works_now', 'works now'], ['needs_tooling', 'needs tooling'], ['needs_fw_change', 'needs firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon']];
  const t = document.getElementById('laddertab');
  function render() {
    fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('');
    fbox.querySelectorAll('button').forEach(b => b.onclick = () => { filter = b.dataset.k; render(); });
    const rows = D.ladder.filter(r => filter === 'all' || r.status === filter);
    t.innerHTML = '<thead><tr><th style="width:12%">Instrument</th><th style="width:32%">What it shows</th><th style="width:16%">Finest granularity</th><th style="width:15%">How</th><th style="width:9%">Who</th><th style="width:10%">Status</th><th style="width:6%">Check</th></tr></thead><tbody>' +
      rows.map(r => `<tr><td class="lvl">${esc(r.level)}</td><td>${esc(r.what)}${r.note ? `<div class="small">${esc(r.note)}</div>` : ''}</td><td>${esc(r.gran)}</td><td>${esc(r.instrument)}</td><td>${esc(r.access)}</td><td>${chip(r.status)}</td><td>${verif(r.check)}</td></tr>`).join('') +
      '</tbody>';
  }
  render();
})();

/* ---------- contrast ---------- */
document.getElementById('contrast').innerHTML = '<thead><tr><th>Topic</th><th>ET-SoC-1</th><th>A100/H100</th><th>Sources</th></tr></thead><tbody>' +
  D.contrast.map(c => `<tr><td class="lvl">${esc(c.topic)}</td><td>${esc(c.et)}</td><td>${esc(c.gpu)}</td><td class="small">${esc(c.src)}</td></tr>`).join('') + '</tbody>';

/* ---------- table of contents ---------- */
(function () {
  const ol = document.getElementById('toclist');
  ol.innerHTML = [...document.querySelectorAll('h2[id]')].map(h => `<li><a href="#${h.id}">${esc(h.textContent.replace(/^\d+\.\s*/, ''))}</a></li>`).join('');
})();

/* ---------- the reports hub: grouped by subject; 'what' may hold links, so it is inserted as HTML ---------- */
(function () {
  let group = null;
  document.getElementById('reportstab').innerHTML = '<thead><tr><th style="width:18%">Report</th><th style="width:9%">When</th><th style="width:50%">What it established</th><th style="width:23%">Instruments</th></tr></thead><tbody>' +
    D.reports.map(r => { const g = r.group && r.group !== group ? `<tr class="grp"><td colspan="4"><b>${esc(r.group)}</b></td></tr>` : ''; if (r.group) group = r.group;
      return g + `<tr><td class="lvl"><a href="${r.url}">${esc(r.title)}</a></td><td class="small">${esc(r.date)}</td><td>${r.what}</td><td class="small">${esc(r.instruments)}</td></tr>`; }).join('') + '</tbody>';
})();

/* ---------- power: the chain, the remainder, the sensors ---------- */
(function () {
  const P = D.power, f = (v, n) => Number(v).toFixed(n == null ? 2 : n);
  document.getElementById('k-unmet').textContent = f(P.idle_73c.unsensed_w, 1) + ' W of ' + f(P.idle_73c.board_w, 1);
  document.getElementById('norails').textContent = P.rails_no_telemetry.join(', ');
  const I = P.idle_73c, rows = [['Minion cores (regulator output)', I.minion_w], ['SRAM: L2, L3, scratchpads', I.sram_w], ['Mesh', I.noc_w], ['On no sensor: the other rails and every regulator\u2019s loss', I.unsensed_w]];
  document.getElementById('idletab').innerHTML = `<thead><tr><th>Idle at ${I.die_c} °C after about ${I.hours} h, mean of 300 samples over 60 s (± sd)</th><th class="num">W</th><th class="num">share</th></tr></thead><tbody>` +
    rows.map(r => `<tr><td>${r[0]}</td><td class="num">${f(r[1])}</td><td class="num">${Math.round(100 * r[1] / I.board_w)}%</td></tr>`).join('') +
    `<tr><td><b>Board (12 V input)</b></td><td class="num"><b>${f(I.board_w)}</b> ± ${f(I.board_sd)}</td><td></td></tr></tbody>`;
  const F = P.fit, hosts = Object.keys(F);
  document.getElementById('fittab').innerHTML = '<thead><tr><th>unmetered W of a configuration =</th>' + hosts.map(h => `<th class="num">${h}</th>`).join('') + '</tr></thead><tbody>' +
    [['× minion-rail W', 'minion', 3, ''], ['× SRAM-rail W', 'sram', 3, ''], ['× NoC-rail W', 'noc', 3, ''], ['pJ per DRAM byte', 'dram_pj_per_byte', 1, ' pJ/B']].map(r =>
      `<tr><td>${r[0]}</td>` + hosts.map(h => `<td class="num">${f(F[h].coef[r[1]], r[2])} ± ${f(F[h].se[r[1]], r[2])}${r[3]}</td>`).join('') + '</tr>').join('') +
    '<tr><td class="small">residual rms, configuration means</td>' + hosts.map(h => `<td class="num small">${f(F[h].rms_w)} W, n = ${F[h].n}</td>`).join('') + '</tr></tbody>';
  document.getElementById('fittext').innerHTML = `Four coefficients, no intercept, fitted per card to the mean of each configuration's three passes (${F.aifoundry2.n} configurations on aifoundry2, which also ran six DRAM-row configurations, ${F.aifoundry3 ? F.aifoundry3.n : 0} on aifoundry3), on bursts of 0.8 to 26 W over idle. DRAM bytes are the bytes of the DRAM load, store and row configurations, streaming stores counted once. The minion coefficient is pinned to 1.4% on each card but differs by 10% between them, about the cards' spread elsewhere in the manual; the DRAM one differs by 7%. The SRAM and NoC coefficients are collinear with the minion one and uncertain to 7–33%. The residual is small overall but not on DRAM traffic: 1.1–1.3 W rms on the DRAM configurations, about a fifth of their unmetered power.`;
  const V = P.pvt, pts = V.vm_points;
  document.getElementById('pvttab').innerHTML = '<thead><tr><th>Moortec PVT on the die</th><th>Count</th><th>Resolution</th><th>What the host gets</th></tr></thead><tbody>' +
    `<tr><td>Temperature sensors</td><td>${V.ts_active} live of ${V.controllers * V.ts_per_controller} (${V.controllers} controllers × ${V.ts_per_controller})</td><td>${V.ts_resolution_c} °C (12-bit)</td><td>${esc(V.host_sees.temperature)}</td></tr>` +
    `<tr><td>Voltage monitor points</td><td>${Object.values(pts).reduce((a, b) => a + b, 0)}: ${Object.keys(pts).map(k => k + ' ' + pts[k]).join('; ')}</td><td>${Math.round(V.vm_lsb_uv)} µV (${V.vm_bits}-bit); 1 mV as forwarded</td><td>${esc(V.host_sees.voltage)}<div class="small">In the SP\u2019s DEBUG trace: ${esc(V.host_sees.debug_trace)}</div></td></tr>` +
    `<tr><td>Process detectors</td><td>${V.pd_active} live of ${V.controllers * V.pd_per_controller}</td><td>ring-oscillator counts</td><td>nothing: configured with measurement disabled, never read</td></tr>` +
    `<tr><td>External analog inputs</td><td>2</td><td>as the monitors</td><td>nothing: the reader is a stub with no caller; what the board wires to them is unknown</td></tr></tbody>`;
  const Dp = P.droop;
  document.getElementById('droopidle').textContent = f(Dp.idle_die_mv.ddr, 0);
  document.getElementById('drooptab').innerHTML = '<thead><tr><th>Configuration (aifoundry2)</th><th class="num">W over idle</th><th class="num">unmetered W less fitted rail losses</th><th class="num">DDR-rail droop, mV</th><th class="num">minion-rail droop, mV</th></tr></thead><tbody>' +
    Dp.examples.map(e => `<tr><td><code>${esc(e.cfg)}</code></td><td class="num">${f(e.over_idle_w)}</td><td class="num">${e.dram_offrail_w ? f(e.dram_offrail_w) : '—'}</td><td class="num">${f(e.droop_ddr_mv)}</td><td class="num">${f(e.droop_minion_mv)}</td></tr>`).join('') + '</tbody>';
  document.getElementById('drooptext').innerHTML = `Over aifoundry2's ${Dp.n} catalogue configurations (its ${F.aifoundry2.n} less the six DRAM-row ones, run separately and not in this telemetry), the DDR rail droops <b>${f(Dp.mv_per_dram_offrail_w)} mV per watt of off-rail DRAM power</b>, plus ${f(Dp.mv_per_board_w_common, 3)} mV per watt of anything else, with an rms of ${f(Dp.rms_mv)} mV: an eighth of the smallest DRAM burst's droop (about 2.9 mV). The DRAM slope rests on 11 configurations, and the largest residuals, about +1 to +1.7 mV, are mostly mesh and scratchpad bursts with no DRAM traffic.`;
  document.getElementById('irdrop').textContent = f(Dp.minion_ir_drop_mv_per_w, 3);
})();

/* ---------- the improvement ladder ---------- */
(function () {
  let filter = 'all';
  const fbox = document.getElementById('impfilters'), t = document.getElementById('imptab');
  const opts = [['all', 'all rungs'], ['done', 'done'], ['works_now', 'works now'], ['needs_tooling', 'tooling or lab hardware'], ['needs_fw_change', 'firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon']];
  function render() {
    fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('');
    fbox.querySelectorAll('button').forEach(b => b.onclick = () => { filter = b.dataset.k; render(); });
    const rows = D.improvements.filter(r => filter === 'all' || (filter === 'done' ? r.done : r.status === filter));
    let group = null;
    t.innerHTML = '<thead><tr><th style="width:23%">Rung</th><th style="width:28%">What it adds</th><th style="width:15%">Cost</th><th style="width:24%">What changes in the numbers</th><th style="width:10%">Status</th></tr></thead><tbody>' +
      rows.map(r => { const g = r.group !== group ? `<tr><td colspan="5"><b>${esc(r.group)}</b></td></tr>` : ''; group = r.group;
        return g + `<tr><td class="lvl">${r.rung}. ${esc(r.what)}${r.done ? ' <span class="verif confirmed">done</span>' : ''}</td><td>${esc(r.adds)}</td><td class="small">${esc(r.cost)}</td><td>${esc(r.effect)}</td><td>${chip(r.status)}</td></tr>`; }).join('') + '</tbody>';
  }
  render();
})();

/* ---------- the power and temperature sessions ---------- */
/* Raw-data paths are stored in full and shown without the common docs/reports/data/ prefix; directories link to
   GitHub's tree view, files to the blob view. */
(function () {
  const PRE = 'docs/reports/data/';
  const link = p => `<a href="${REPO}${p.path.endsWith('/') ? 'tree' : 'blob'}/main/${p.path}"><code>${esc(p.path.startsWith(PRE) ? p.path.slice(PRE.length) : p.path)}</code></a>${p.note ? ' (' + esc(p.note) + ')' : ''}`;
  document.getElementById('sessionstab').innerHTML = '<thead><tr><th style="width:7%">Session</th><th style="width:9%">When</th><th style="width:8%">Card</th><th style="width:28%">What it measured</th><th style="width:14%">Instruments</th><th style="width:21%">Raw data</th><th style="width:13%">Reports</th></tr></thead><tbody>' +
    D.sessions.map(r => `<tr><td class="lvl">${esc(r.id)}</td><td class="small">${esc(r.when)}</td><td class="small">${esc(r.card)}</td><td>${esc(r.what)}</td><td class="small">${esc(r.instruments)}</td><td class="small">${r.data.map(link).join('<br>')}</td><td class="small">${r.reports.map(x => `<a href="${x.url}">${esc(x.title)}</a>`).join('<br>')}</td></tr>`).join('') + '</tbody>';
})();
document.getElementById('relatedlist').innerHTML = D.related.map(r => `<li><a href="${r.url}">${esc(r.title)}</a> — ${esc(r.what)}</li>`).join('');
