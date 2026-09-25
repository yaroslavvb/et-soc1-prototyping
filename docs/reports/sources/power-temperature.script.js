/* Power and temperature (sessions E5 and E6). D is summary.json from tools/ettelem/summarize_power_session.py; every
   number this script prints is computed from it. Charts use the shared toolkit CK (docs/reports/sources/chartkit.js).
   One time bus links the two time charts, the time slider, the power-against-temperature chart and the edge panels. */
const S = D.thermal.series, PH = D.thermal.phases, GAPS = D.thermal.gaps, FAST = D.thermal.fast, CX = D.context;
const $ = id => document.getElementById(id);
const put = (id, v) => { const e = $(id); if (e) e.textContent = v; };
const num = CK.fmt.num;
const LAW = CX.idle_law.value;
const law = T => LAW.P_fix + LAW.A_at_80 * Math.exp((T - 80) / LAW.T_L);
const lawSlope = T => LAW.A_at_80 / LAW.T_L * Math.exp((T - 80) / LAW.T_L);
const markT = name => PH.find(p => p.phase === name).t;
const T_MM = markT('matmul'), T_C1 = markT('cool1'), T_DR = markT('dram'), T_C2 = markT('cool2');
const T_END = S[S.length - 1].t + 1;
const rest = p => p.board - p.minion - p.sram - p.noc;
const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
const median = a => { const b = [...a].sort((x, y) => x - y), n = b.length; return n % 2 ? b[(n - 1) / 2] : (b[n / 2 - 1] + b[n / 2]) / 2; };
const WORD = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'];
const word = n => WORD[n] || num(n);
const wholeRange = (a, b) => (Math.round(a) === Math.round(b) ? num(Math.round(a), 0) : num(Math.round(a), 0) + '–' + num(Math.round(b), 0));
const PHASE_NAME = {idle0: 'idle', matmul: 'matmul', cool1: 'idle, cooling', dram: 'DRAM loads', cool2: 'idle, cooling', end: 'idle'};
const GROUP = {idle0: 'idle', matmul: 'matmul', cool1: 'idle', dram: 'dram', cool2: 'idle', end: 'idle'};
const phaseAt = t => { let n = PH[0].phase; for (const p of PH) if (p.t <= t) n = p.phase; return n; };
const bin = k => S[Math.max(0, Math.min(S.length - 1, k))];
/* A 1 s bin k covers [k, k+1). A gap bin holds one of the launch gaps the reducer found in the 10 Hz stream; a settling
   bin starts less than 3 s after a change of phase (the recording's start is not one). */
const gapBin = k => GAPS.some(g => g >= k && g < k + 1);
const nearGap = (k, w) => GAPS.some(g => Math.abs(Math.floor(g) - k) <= w);
const settling = k => PH.some(p => p.phase !== 'idle0' && p.phase !== 'end' && k + 0.5 - p.t >= 0 && k + 0.5 - p.t < 3);
function lsq(xs, ys) {
  const mx = mean(xs), my = mean(ys);
  let sxy = 0, sxx = 0;
  xs.forEach((x, i) => { sxy += (x - mx) * (ys[i] - my); sxx += (x - mx) ** 2; });
  const b = sxy / sxx;
  return {b, a: my - b * mx};
}
function tipAt(f, html, cx, cy) {  // place the frame's tooltip next to a point (host coordinates)
  const t = f.tip; t.innerHTML = html; t.style.display = 'block';
  const hw = f.host.clientWidth, tw = t.offsetWidth, th = t.offsetHeight;
  let top = cy + 14;
  if (top + th > f.host.clientHeight && cy - th - 10 >= 0) top = cy - th - 10;
  t.style.left = Math.max(0, Math.min(cx + 12, hw - tw)) + 'px'; t.style.top = top + 'px';
}
const hideTip = f => { f.tip.style.display = 'none'; };

/* ---------- numbers in the prose ---------- */
put('law-fix', num(LAW.P_fix, 1)); put('law-a', num(LAW.A_at_80, 1)); put('law-tl', num(LAW.T_L, 0));
put('law-slope80', num(lawSlope(80), 2)); put('law-80', num(law(80), 0));
{ // the whole-degree readings the idle fit used, as runs of consecutive degrees ("64–67 and 81–88")
  const T = [...LAW.fit_T].sort((a, b) => a - b), runs = [];
  for (const t of T) { const r = runs[runs.length - 1]; if (r && t === r[1] + 1) r[1] = t; else runs.push([t, t]); }
  const txt = runs.map(([a, b]) => (a === b ? num(a, 0) : num(a, 0) + '–' + num(b, 0)));
  put('law-trange', txt.length < 2 ? txt.join('') : txt.slice(0, -1).join(', ') + ' and ' + txt[txt.length - 1]);
}
const IDLE0 = S.filter(p => p.t + 1 <= T_MM), COOL = S.filter(p => p.t >= T_DR - 5 && p.t + 1 <= T_DR);
put('box-idle-rest', num(mean(IDLE0.map(rest)), 0));
const RF = CX.rail_filter.value;
// the rails' filter on each card (catalogue.json rail_filter: median fall after the board's step-down, per card)
const pct = v => num(100 * v, 0) + '%';
const tauCards = `${num(RF.aifoundry2.tau_s, 2)} s on aifoundry2, ${num(RF.aifoundry3.tau_s, 2)} s on aifoundry3`;
put('kpi-tau', tauCards); put('rf-tau', tauCards);
put('rf-n', `${num(RF.aifoundry2.n, 0)} load bursts on aifoundry2 and ${num(RF.aifoundry3.n, 0)} on aifoundry3`);
put('rf-12s', `${pct(RF.aifoundry2.frac_1s)} after 1 s and ${pct(RF.aifoundry2.frac_2s)} after 2 s on aifoundry2, ` +
  `${pct(RF.aifoundry3.frac_1s)} and ${pct(RF.aifoundry3.frac_2s)} on aifoundry3`);
put('ir-drop', num(CX.minion_ir_drop_mv_per_w.value, 2));
{ // the busy drift of the strict Horace runs on each card, with how well its runs pin it down
  const BD = CX.busy_drift_cards, a2 = BD.aifoundry2, a3 = BD.aifoundry3;
  const rng = c => wholeRange(c.temp_c[0], c.temp_c[1]);
  put('busy-drift', `${num(a2.w_per_c, 2)} W/°C at ${rng(a2)} °C (${word(a2.runs)} runs, standard error ${num(a2.se, 2)} W/°C)`);
  put('busy-drift-a3', `On the second card, aifoundry3, the same runs at ${rng(a3)} °C gave ${num(a3.w_per_c, 2)} W/°C` +
    (a3.se > 0.1 * a3.w_per_c ? `, but its ${word(a3.runs)} runs scatter so widely (standard error ${num(a3.se, 2)} W/°C) that the drift there is not pinned down.`
      : ` (${word(a3.runs)} runs, standard error ${num(a3.se, 2)} W/°C).`));
}
put('rest-idle0', num(mean(IDLE0.map(rest)), 1)); put('rest-idle0-t', num(mean(IDLE0.map(p => p.temp)), 0));
put('rest-cool', num(mean(COOL.map(rest)), 1)); put('rest-cool-t', num(mean(COOL.map(p => p.temp)), 0));
{ // steady remainder under load: 5 s (matmul) or 1 s (DRAM) after the mark, two or more bins from a launch gap
  const rm = S.filter(p => p.t >= T_MM + 5 && p.t + 1 <= T_C1 && !nearGap(p.t, 1)).map(rest);
  const rd = S.filter(p => p.t >= T_DR + 1 && p.t + 1 <= T_C2 && !nearGap(p.t, 1)).map(rest);
  put('rest-mm', wholeRange(Math.min(...rm), Math.max(...rm))); put('rest-dram', wholeRange(Math.min(...rd), Math.max(...rd)));
  // what the DRAM load moves, against the last 5 s of the cool-down before it; the matmul's minion rail against idle0
  const DR = S.filter(p => p.t >= T_DR + 1 && p.t + 1 <= T_C2 && !nearGap(p.t, 1)), MMB = S.filter(p => p.t >= T_MM + 5 && p.t + 1 <= T_C1 && !nearGap(p.t, 1));
  const mOf = (P, f) => mean(P.map(f));
  put('dram-rest', num(mOf(DR, rest) - mOf(COOL, rest), 0)); put('dram-mnn', num(mOf(DR, p => p.minion) - mOf(COOL, p => p.minion), 1));
  put('dram-dt', num(mOf(DR, p => p.temp) - mOf(COOL, p => p.temp), 0));
  const i0 = mOf(IDLE0, p => p.minion), mm = MMB.map(p => p.minion - i0);
  put('mm-mnn', wholeRange(Math.min(...mm), Math.max(...mm)));
}
{ // the DDR domain's on-die reading: its fall with temperature at idle, then what each load adds to it
  const ddr = P => mean(P.map(p => p.die_ddr)), tmp = P => mean(P.map(p => p.temp));
  const dI = ddr(IDLE0), tI = tmp(IDLE0), dC = ddr(COOL), tC = tmp(COOL), k = (dC - dI) / (tC - tI), trend = T => dC + k * (T - tC);
  const DR = S.filter(p => p.t >= T_DR + 3 && p.t + 1 <= T_C2), MM = S.filter(p => p.t >= T_C1 - 18 && p.t + 1 <= T_C1);
  const below = P => trend(tmp(P)) - ddr(P), mmT = MM.map(p => p.temp);
  put('ddr-idle', `The DDR domain reads ${num(dI, 0)} mV on die at ${num(tI, 0)} °C idle and ${num(dC, 0)} mV at ${num(tC, 0)} °C, ` +
    `against an 800 mV set-point: at idle it falls about ${num(-k, 1)} mV per °C.`);
  put('ddr-load', `Under the DRAM-bound load, at ${num(tmp(DR), 0)} °C, it reads ${num(ddr(DR), 0)} mV, ${num(below(DR), 0)} mV below that trend. ` +
    `Under the matmul, with little DRAM traffic, it reads ${num(ddr(MM), 0)} mV at ${wholeRange(Math.min(...mmT), Math.max(...mmT))} °C, ` +
    (Math.abs(below(MM)) < 0.5 ? 'which the trend alone predicts.' : `${num(below(MM), 1)} mV below the trend.`));
}
{ // the matmul's runs: what each did (the load log) and how long each took between dips (the 10 Hz gaps)
  const L = D.thermal.loads && D.thermal.loads.matmul;
  if (L) {
    put('mm-runs', word(L.processes));
    put('mm-work', `${word(L.launches_per_process)} launches of ${num(L.iters_per_launch)} iterations on all ${num(L.minions)} minions`);
  }
  const g = GAPS.filter(t => t > T_MM && t < T_C1), d = g.slice(1).map((t, i) => t - g[i]);
  put('mm-spans', CK.fmt.range(Math.min(...d), Math.max(...d), 1, 's'));
  const a = bin(Math.floor(T_MM) + 2), b = bin(Math.floor(T_C1) - 1);
  put('extra-w', num(b.board - a.board, 1)); put('law-part', num(law(b.temp) - law(a.temp), 1));
}

/* ---------- §1: the instruments ---------- */
const chip = (s, t) => `<span class="chip ${s}">${t}</span>`;
const railTxt = `τ ≈ ${num(RF.aifoundry2.tau_s, 2)} s and ${pct(RF.aifoundry2.frac_2s)} of a step after 2 s on aifoundry2, ` +
  `${num(RF.aifoundry3.tau_s, 2)} s and ${pct(RF.aifoundry3.frac_2s)} on aifoundry3`;
const M = [
 ['Board power, now', 'whole card · a new value each SP pass: about every 156 ms on aifoundry2, 263 ms on aifoundry3, while ettelem samples at 10 Hz · 10 mW', 'DM_CMD_GET_MODULE_POWER (ettelem: up to 45 samples/s; the SP refreshes it once per pass)', 'works_now', 'works now'],
 ['Board power, PMIC average / min / max', 'whole card · the PMIC\'s running average, like the rails; min and max since the last stats reset', 'DM_CMD_GET_SP_STATS via ettelem (the stock CLI calls it unsupported), or the SPST trace', 'works_now', 'works now'],
 ['Rail power: minion cores, SRAM, mesh', `3 rails · 1 mW · the PMIC's running average (${railTxt}), one record per SP pass, plus min/max`, 'same snapshot; the SPST trace keeps ~15 min of records with µs stamps', 'works_now', 'works now'],
 ['Rail voltage and clock', '3 rails · 1 mV · avg/min/max; minion and mesh MHz', 'same snapshot', 'works_now', 'works now'],
 ['On-die voltage per domain', '7 domains (DDR, SRAM, Maxion, minion, PCIe shire, mesh, IO shire) · 1 mV', 'DM_CMD_GET_ASIC_VOLTAGE; compare with the regulator set-points from DM_CMD_GET_MODULE_VOLTAGE for the drop to the die', 'works_now', 'works now'],
 ['On-die voltage per shire', '34 minion shires × 3 rails + 8 memory shires × 2 · 1 mV · current, and hardware low/high between polls', 'SP log at DEBUG level: ettelem loglevel debug + sptrace (4 KB buffer, wraps about once per pass)', 'works_now', 'works now'],
 ['Temperature', 'IO shire, and mean, low and high of the 34 minion-shire sensors · 1 °C · per SP pass; "low/high" are extremes since reset, not the current spread', 'DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (its field labelled PMIC holds the minion mean again)', 'works_now', 'works now'],
 ['Power state, throttle residency, thresholds', 'card-wide · µs residency counters', 'DM_CMD_GET_MODULE_POWER_STATE, _RESIDENCY_*, _TEMPERATURE_THRESHOLDS, _STATIC_TDP_LEVEL', 'works_now', 'works now'],
 ['Device-wide bandwidth and utilisation', 'DDR, L2/L3, PCIe · 1 ms samples', 'MMST trace; a proxy for where memory energy goes', 'works_now', 'works now'],
 ['Energy per event', 'pJ per load, per multiply-add, per mesh hop · needs ≥10⁹ identical events/s for seconds', 'rail power above a same-temperature baseline ÷ event rate (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#where-the-energy-goes">memory anatomy</a>, <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment">the Horace experiment</a>; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual">the energy manual</a> does it for every instruction and byte)', 'works_now', 'works now'],
 ['Static against dynamic power', 'per rail', 'frequency sweep at fixed voltage: DM_CMD_SET_FREQUENCY with power management off. Changes the card for everyone; not run here', 'works_now', 'works now, with care'],
 ['Instantaneous rail power', '3 rails · 1 mW · per pass', 'the SP already reads it each pass and discards it; a few assignments in thermal_pwr_mgmt.c', 'needs_fw_change', 'firmware'],
 ['Faster sampling', 'tens to hundreds of Hz', 'in the firmware source each pass makes ~96 I2C transactions, each followed by a hard-coded 1 ms wait, a floor of about 100 ms; the measured pass is longer (about 135 ms on aifoundry2 with a light poller in one session, 156 ms while ettelem samples at 10 Hz, and about 1.7× as long on aifoundry3, for reasons not established). Skip the 84-read snapshot and fix the wait', 'needs_fw_change', 'firmware'],
 ['Per-shire temperature; process detectors', '34 shires · 0.06 °C in hardware; ring-oscillator counts in µs windows', 'sampled continuously by the PVT controllers, never exported', 'needs_fw_change', 'firmware'],
 ['DDR, PCIe, Maxion, IO rails', '—', 'regulators with set-points but no current sense: only "board minus three rails"', 'impossible_on_silicon', 'no sensor'],
 ['Board power at kHz', 'whole card · ~1 ms', 'scope on the hot-swap controller\'s current-monitor pin, or a PCIe riser with a shunt', 'needs_tooling', 'hardware'],
];
$('methods').innerHTML = '<thead><tr><th>What</th><th>Granularity</th><th>How</th><th>Status</th></tr></thead><tbody>' +
  M.map(r => `<tr><td class="lvl" style="white-space:normal">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${chip(r[3], r[4])}</td></tr>`).join('') + '</tbody>';
CK.stackTable($('methods'));

/* ---------- the time bus: one moment, shown on every chart ---------- */
const TB = CK.bus('pt-time');
const frames = [];
TB.on(t => frames.forEach(f => f.cross && f.cross(t)));
const readRow = k => {
  const p = bin(k);
  return `${PHASE_NAME[phaseAt(k + 0.5)]} · die ${num(p.temp, 1)} °C · board ${num(p.board, 1)} W · minion ${num(p.minion, 1)} · SRAM ${num(p.sram, 1)} · mesh ${num(p.noc, 1)} · unmetered ${num(rest(p), 1)} W · above the idle law ${p.board - law(p.temp) >= 0 ? '+' : ''}${num(p.board - law(p.temp), 1)} W`;
};
const scrubOut = CK.readout('scrubout');
const scrub = CK.range('scrub', {label: 'Step through time', min: 0, max: T_END - 1, step: 1, value: 60, fmt: v => v + ' s',
  onInput: v => TB.emit(v + 0.5, 'scrub')});
TB.on((t, src) => {
  const k = Math.max(0, Math.min(T_END - 1, Math.floor(t)));
  if (src !== 'scrub') { scrub.input.value = k; scrub.el.querySelector('output').textContent = k + ' s'; scrub.input.setAttribute('aria-valuetext', k + ' s'); }
  scrubOut.set(`<b>t ${k} s</b> · ${readRow(k)}`);
});

/* ---------- §2: power and temperature against time ---------- */
const TS = {L: 40, R: 12, T: 16, B: 30};
function timeChart(id, o) {
  const f = CK.frame(id, {height: W => (W < 600 ? o.h[0] : o.h[1]), label: o.label, draw: f => {
    const {L, R, T, B} = TS, W = f.W, H = f.H;
    const x = CK.lin(0, T_END, L, W - R), y = CK.lin(o.y0, o.y1, H - B, T);
    for (let i = 0; i < PH.length - 1; i++) {
      const n = PH[i].phase;
      if (n !== 'matmul' && n !== 'dram') continue;
      CK.el('rect', {x: x(PH[i].t), y: T, width: x(PH[i + 1].t) - x(PH[i].t), height: H - B - T, fill: 'var(--grid)', opacity: 0.45}, f.svg);
      CK.txt(f.svg, x(PH[i].t) + 4, T + 12, n === 'matmul' ? 'matmul' : (f.narrow ? 'DRAM' : 'DRAM loads'), 'lab');
    }
    const step = f.narrow ? 40 : 20, xt = [];
    for (let t = 0; t < T_END; t += step) xt.push(t);
    CK.axes(f, {x, y, L, R, T, B, xt, yt: o.yt, xfmt: v => v + ' s'});
    if (o.gapTicks) for (const g of GAPS) CK.el('line', {x1: x(g), x2: x(g), y1: H - B, y2: H - B - 7, stroke: 'var(--ink-2)', 'stroke-width': 1.5}, f.svg);
    for (const s of o.series) {
      const pts = S.map(p => [p.t + 0.5, s.get(p)]);
      const e = CK.el('path', {d: CK.path(pts, x, y), fill: 'none', 'stroke-width': s.w || 2, 'stroke-linejoin': 'round', 'data-series': s.key}, f.svg);
      e.style.stroke = s.color; if (s.dash) e.style.strokeDasharray = s.dash;
    }
    const cross = CK.el('line', {y1: T, y2: H - B, stroke: 'var(--ink-2)', 'stroke-width': 1, 'pointer-events': 'none'}, f.svg);
    const hit = CK.el('rect', {x: L, y: T, width: W - L - R, height: H - B - T, class: 'ck-hit', tabindex: 0, role: 'img',
      'aria-label': o.label + '. Left and right arrow keys step one second; the readout below the charts gives the values.'}, f.svg);
    let k = 60;
    f.cross = t => { k = Math.max(0, Math.min(T_END - 1, Math.floor(t))); cross.setAttribute('x1', x(k + 0.5)); cross.setAttribute('x2', x(k + 0.5)); };
    const tipHtml = () => `<b>${k} s</b> · ${PHASE_NAME[phaseAt(k + 0.5)]}<br>` + o.tip(bin(k));
    const at = ev => { const b = f.svg.getBoundingClientRect(), hb = f.host.getBoundingClientRect();
      TB.emit(Math.floor(x.inv(ev.clientX - b.left)) + 0.5, id); tipAt(f, tipHtml(), ev.clientX - hb.left, ev.clientY - hb.top); };
    hit.addEventListener('pointermove', at); hit.addEventListener('pointerdown', at);
    hit.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') hideTip(f); });
    const keyTip = () => { const hb = f.host.getBoundingClientRect(), b = f.svg.getBoundingClientRect(); tipAt(f, tipHtml(), b.left - hb.left + x(k + 0.5), T); };
    hit.addEventListener('focus', keyTip); hit.addEventListener('blur', () => hideTip(f));
    hit.addEventListener('keydown', ev => {
      const d = {ArrowRight: 1, ArrowLeft: -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10}[ev.key];
      if (ev.key === 'Escape') { hideTip(f); return; }
      let nk = d ? k + d : ev.key === 'Home' ? 0 : ev.key === 'End' ? T_END - 1 : null;
      if (nk == null) return;
      ev.preventDefault(); nk = Math.max(0, Math.min(T_END - 1, nk));
      TB.emit(nk + 0.5, id); keyTip();
    });
    if (TB.value != null) f.cross(TB.value);
  }});
  frames.push(f);
  return f;
}
const POWER_SERIES = [
  {key: 'board', label: 'board', color: 'var(--c1)', get: p => p.board},
  {key: 'minion', label: 'minion cores', color: 'var(--c2)', get: p => p.minion},
  {key: 'sram', label: 'SRAM', color: 'var(--c3)', get: p => p.sram},
  {key: 'noc', label: 'mesh', color: 'var(--c4)', get: p => p.noc},
  {key: 'rest', label: 'unmetered (board − rails)', color: 'var(--c5)', dash: '5 3', get: rest},
];
const pMax = Math.ceil(Math.max(...S.map(p => p.board)) / 10) * 10, pMin = Math.min(0, Math.floor(Math.min(...S.map(rest)) / 10) * 10);
const fPower = timeChart('power', {h: [230, 300], y0: pMin, y1: pMax, gapTicks: true, series: POWER_SERIES,
  label: 'Board power, the three rails and the unmetered remainder against time',
  tip: p => `board ${num(p.board, 1)} W<br>minion ${num(p.minion, 1)} · SRAM ${num(p.sram, 1)} · mesh ${num(p.noc, 1)}<br>unmetered ${num(rest(p), 1)} W`});
const leg1 = CK.legend('leg1', POWER_SERIES.map(s => ({key: s.key, label: s.label, color: s.color, mark: s.dash ? 'dash' : 'line'})),
  {toggle: true, onChange: keys => CK.showSeries(fPower, keys)});
const tLo = Math.floor(Math.min(...S.map(p => p.temp)) / 5) * 5, tHi = Math.ceil(Math.max(...S.map(p => p.temp)) / 5) * 5;
timeChart('temp', {h: [140, 170], y0: tLo, y1: tHi, series: [{key: 'temp', color: 'var(--c7)', get: p => p.temp}],
  label: 'Die temperature against time', tip: p => `die ${num(p.temp, 1)} °C · board ${num(p.board, 1)} W`});

/* ---------- §2: board power against die temperature ---------- */
const PV = {view: 'board', from: 5, rings: true, dropGaps: false};
const GCOL = {idle: 'var(--ref)', matmul: 'var(--c7)', dram: 'var(--c5)'};
const GNAME = {idle: 'idle', matmul: 'matmul', dram: 'DRAM loads'};
const groupOf = p => GROUP[phaseAt(p.t + 0.5)];
const fitBins = (from, drop) => S.filter(p => p.t >= T_MM + from && p.t + 1 <= T_C1 && !(drop && gapBin(p.t)));
function fitOf(from, drop) {
  const P = fitBins(from, drop), T = P.map(p => p.temp);
  return {P, board: lsq(T, P.map(p => p.board)), minion: lsq(T, P.map(p => p.minion)).b, law: lsq(T, T.map(law)).b,
    t0: Math.min(...T), t1: Math.max(...T)};
}
const above = p => p.board - law(p.temp);
const medians = () => {  // per group, leaving out each phase's first 3 s and the gap bins
  const g = {};
  for (const p of S) if (!settling(p.t) && !gapBin(p.t)) (g[groupOf(p)] = g[groupOf(p)] || []).push(p);
  return Object.fromEntries(Object.entries(g).map(([k, P]) => [k, {m: median(P.map(above)), t0: Math.min(...P.map(p => p.temp)), t1: Math.max(...P.map(p => p.temp))}]));
};
const MED = medians();
const sign = v => (v >= 0.05 ? '+' : '') + num(v, 1);
CK.seg('pvt-view', {label: 'Plot', options: [['board', 'Board power'], ['above', 'Above the idle law']], value: 'board',
  onChange: v => { PV.view = v; fPvt.redraw(); pvtOut(); }});
CK.range('pvt-from', {label: 'Fit starts', min: 1, max: 20, step: 1, value: PV.from, fmt: v => v + ' s after launch',
  onInput: v => { PV.from = v; fPvt.redraw(); pvtOut(); }});
function toggle(host, label, on, fn) {
  const b = document.createElement('button'); b.type = 'button'; b.textContent = label; b.setAttribute('aria-pressed', String(on));
  b.addEventListener('click', () => { const v = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', String(v)); fn(v); });
  $(host).appendChild(b); return b;
}
toggle('pvt-toggles', 'Mark launch gaps', PV.rings, v => { PV.rings = v; fPvt.redraw(); });
toggle('pvt-toggles', 'Leave launch-gap bins out of the fit', PV.dropGaps, v => { PV.dropGaps = v; fPvt.redraw(); pvtOut(); });
CK.legend('pvt-leg', [
  {key: 'i', label: 'idle', mark: 'dot', color: GCOL.idle}, {key: 'm', label: 'matmul', mark: 'dot', color: GCOL.matmul},
  {key: 'd', label: 'DRAM loads', mark: 'dot', color: GCOL.dram}, {key: 's', label: 'hollow: a phase\'s first 3 s', mark: 'ring', color: 'var(--ink-2)'},
  {key: 'g', label: 'ringed: a launch gap', mark: 'ring', color: 'var(--ink)'}, {key: 'l', label: 'idle law', mark: 'dash', color: 'var(--ink)'},
  {key: 'f', label: 'fit through the matmul', mark: 'line', color: 'var(--c1)'},
  {key: 'md', label: 'dotted: each phase\'s median (above-the-law view)', mark: 'dash', color: 'var(--ink-2)'}]);
const pvtRead = CK.readout('pvt-out');
function pvtOut() {
  const F = fitOf(PV.from, PV.dropGaps), G = fitOf(PV.from, !PV.dropGaps), nGap = F.P.length - fitOf(PV.from, true).P.length;
  put('slope-board', num(F.board.b, 2)); put('slope-minion', num(F.minion, 2)); put('slope-law', num(F.law, 2)); put('fit-from', `${PV.from} s after launch` + (PV.dropGaps ? ', leaving out the launch-gap seconds,' : ''));
  let h = `Fit from ${PV.from} s after launch: board <b>${num(F.board.b, 2)} W/°C</b> (minion ${num(F.minion, 2)}) over ${F.P.length} bins at ` +
    `${CK.fmt.range(F.t0, F.t1, 1, '°C')}; the idle law's own slope there: ${num(F.law, 2)} W/°C.`;
  h += PV.dropGaps ? ` With the ${word(fitOf(PV.from, false).P.length - F.P.length)} launch-gap bins: ${num(G.board.b, 2)} W/°C.`
    : ` Without the ${word(nGap)} launch-gap bins: ${num(G.board.b, 2)} W/°C.`;
  if (PV.view === 'above') h += ` Median above the law, leaving out each phase's first 3 s and the gap bins: ` +
    ['idle', 'dram', 'matmul'].filter(g => MED[g]).map(g => `${GNAME[g]} ${sign(MED[g].m)} W`).join(', ') + '.';
  pvtRead.set(h);
}
const fPvt = CK.frame('pvt', {height: W => (W < 600 ? 300 : 360), label: 'Board power against die temperature, one dot per second', draw: f => {
  const W = f.W, H = f.H, L = 42, R = 14, T = 16, B = 36;
  const temps = S.map(p => p.temp), ab = PV.view === 'above';
  const x = CK.lin(Math.floor((Math.min(...temps) - 1) / 5) * 5, Math.ceil((Math.max(...temps) + 1) / 5) * 5, L, W - R);
  const ys = S.map(ab ? above : p => p.board);
  const y = CK.lin(Math.floor((Math.min(...ys) - 2) / 5) * 5, Math.ceil((Math.max(...ys) + 2) / 5) * 5, H - B, T);
  CK.axes(f, {x, y, L, R, T, B, xl: 'die temperature (°C, 34-shire mean)', xfmt: v => num(v, 0), yfmt: v => (ab && v > 0 ? '+' : '') + num(v, 0) + ' W'});
  const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
  // the idle law, and the least-squares line through the matmul bins
  const Ts = []; for (let t = x.domain[0]; t <= x.domain[1] + 1e-9; t += 0.25) Ts.push(t);
  const lawPath = CK.el('path', {d: CK.path(Ts.map(t => [t, ab ? 0 : law(t)]), x, y), fill: 'none', 'stroke-width': 1.5}, g0);
  lawPath.style.stroke = 'var(--ink)'; lawPath.style.strokeDasharray = '5 4';
  CK.txt(g0, W - R - 2, y(ab ? 0 : law(x.domain[1])) + (ab ? 14 : -6), ab ? 'idle law = 0' : 'idle law', 'lab', 'end');
  const F = fitOf(PV.from, PV.dropGaps);
  const fl = [F.t0, F.t1].map(t => [t, F.board.a + F.board.b * t - (ab ? law(t) : 0)]);
  const fitE = CK.el('path', {d: CK.path(ab ? Ts.filter(t => t >= F.t0 && t <= F.t1).concat([F.t1]).map(t => [t, F.board.a + F.board.b * t - law(t)]) : fl, x, y),
    fill: 'none', 'stroke-width': 2}, g0);
  fitE.style.stroke = 'var(--c1)';
  if (ab) for (const g of ['idle', 'dram', 'matmul']) {
    const m = MED[g]; if (!m) continue;
    const e = CK.el('line', {x1: x(m.t0), x2: x(m.t1), y1: y(m.m), y2: y(m.m), 'stroke-width': 1.5}, g0);
    e.style.stroke = GCOL[g]; e.style.strokeDasharray = '2 3';
  }
  // one dot per second, in time order (the keyboard steps through them in that order)
  const nodes = [], hl = CK.el('circle', {r: 9, fill: 'none', 'stroke-width': 2, 'pointer-events': 'none'}, f.svg);
  hl.style.stroke = 'var(--ink)';
  const r = f.narrow ? 3.5 : 4;
  for (const p of S) {
    const g = groupOf(p), c = GCOL[g], hollow = settling(p.t), cx = x(p.temp), cy = y(ab ? above(p) : p.board);
    const node = CK.el('g', {}, f.svg);
    if (PV.rings && gapBin(p.t)) { const ring = CK.el('circle', {cx, cy, r: r + 3.5, fill: 'none', 'stroke-width': 1.2}, node); ring.style.stroke = 'var(--ink)'; }
    const dot = CK.el('circle', {cx, cy, r}, node);
    if (hollow) { dot.style.fill = 'var(--surface)'; dot.style.stroke = c; dot.style.strokeWidth = '1.5'; }
    else { dot.style.fill = c; dot.style.stroke = 'var(--surface)'; dot.style.strokeWidth = '1'; }
    const html = () => `<b>${p.t} s</b> · ${PHASE_NAME[phaseAt(p.t + 0.5)]}${gapBin(p.t) ? ' · a gap between two ~7 s runs' : ''}${hollow ? ' · first 3 s of a phase' : ''}` +
      `<br>die ${num(p.temp, 1)} °C · board ${num(p.board, 1)} W · minion ${num(p.minion, 1)} W<br>above the idle law ${sign(above(p))} W`;
    CK.tip(f, node, html);
    node.addEventListener('pointerenter', () => TB.emit(p.t + 0.5, 'pvt'));
    node._p = p; nodes.push(node);
  }
  CK.keynav(f, nodes, {onFocus: n => TB.emit(n._p.t + 0.5, 'pvt')});
  f.cross = t => { const p = bin(Math.floor(t)); hl.setAttribute('cx', x(p.temp)); hl.setAttribute('cy', y(ab ? above(p) : p.board)); };
  if (TB.value != null) f.cross(TB.value);
}});
frames.push(fPvt);
pvtOut();

/* ---------- §2 bullet 4: the remainder at the load edges, board power filtered like the rails ---------- */
const EDGE = {tau: 0, avg: false};
const FT = FAST.t, FIDX = FAST.windows.map(([a, z]) => FT.map((t, i) => i).filter(i => FT[i] >= a && FT[i] < z));
function boardPrime(idx, tau, avg) {
  let y = null, tp = null;
  return idx.map(i => {
    if (avg) return FAST.board_avg[i];
    const v = FAST.board[i];
    y = (y == null || tau <= 0) ? v : y + (1 - Math.exp(-(FT[i] - tp) / tau)) * (v - y);
    tp = FT[i]; return y;
  });
}
const remOf = (w, tau, avg) => { const b = boardPrime(FIDX[w], tau, avg); return FIDX[w].map((i, j) => b[j] - FAST.rails[i]); };
const steady = w => {  // the steady remainder before and after each edge, from that panel's instant readings
  const idx = FIDX[w], [a, z] = FAST.windows[w], r = remOf(w, 0, false);
  const pick = (lo, hi) => median(idx.map((i, j) => [FT[i], r[j]]).filter(([t]) => t >= lo && t < hi).map(v => v[1]));
  return [pick(a, a + 4), pick(z - 5, z)];
};
const STEADY = [0, 1].map(steady);
const eMin = Math.floor(Math.min(...[0, 1].flatMap(w => remOf(w, 0, false))) / 5) * 5;
const eMax = Math.ceil(Math.max(...FIDX.flat().map(i => FAST.board[i])) / 10) * 10;
const edgeOut = [CK.readout('edge-a-out'), CK.readout('edge-b-out')];
function edgeFrame(id, w) {
  const f = CK.frame(id, {height: W => (W < 600 ? 220 : 250), minW: 260, label: 'The unmetered remainder, board power and the rails, 10 samples a second', draw: f => {
    const [a, z] = FAST.windows[w], W = f.W, H = f.H, L = 38, R = 10, T = 12, B = 30, idx = FIDX[w];
    const x = CK.lin(a, z, L, W - R), y = CK.lin(eMin, eMax, H - B, T), xt = [];
    for (let t = Math.ceil(a / 5) * 5; t <= z; t += 5) xt.push(t);
    CK.axes(f, {x, y, L, R, T, B, xt, xfmt: v => v + ' s', yfmt: v => num(v, 0)});
    const z0 = CK.el('line', {x1: L, x2: W - R, y1: y(0), y2: y(0), 'stroke-width': 1}, f.svg); z0.style.stroke = 'var(--ink)';
    for (const g of GAPS) if (g >= a && g < z) CK.el('line', {x1: x(g), x2: x(g), y1: H - B, y2: H - B - 7, stroke: 'var(--ink-2)', 'stroke-width': 1.5}, f.svg);
    STEADY[w].forEach((v, j) => {
      const e = CK.el('line', {x1: L, x2: W - R, y1: y(v), y2: y(v), 'stroke-width': 1}, f.svg); e.style.stroke = 'var(--ref)'; e.style.strokeDasharray = '3 3';
      const lab = (j === 0) === (w === 0) ? 'idle' : 'matmul';
      CK.txt(f.svg, j === 0 ? L + 4 : W - R - 4, y(v) + (v > STEADY[w][1 - j] ? -5 : 13), `${num(v, 1)} W ${lab}`, 'lab', j === 0 ? 'start' : 'end');
    });
    const bp = boardPrime(idx, EDGE.tau, EDGE.avg), rem = idx.map((i, j) => bp[j] - FAST.rails[i]);
    const line = (vals, color, width, op, key) => {
      const e = CK.el('path', {d: CK.path(idx.map((i, j) => [FT[i], vals[j]]), x, y), fill: 'none', 'stroke-width': width, 'stroke-linejoin': 'round', opacity: op, 'data-series': key}, f.svg);
      e.style.stroke = color;
    };
    line(bp, 'var(--c1)', 1.5, 0.45, 'b'); line(idx.map(i => FAST.rails[i]), 'var(--c2)', 1.5, 0.45, 'r'); line(rem, 'var(--c5)', 2, 1, 'x');
    edgeOut[w].set(`remainder from ${num(Math.min(...rem), 1)} to ${num(Math.max(...rem), 1)} W`);
    const cross = CK.el('line', {y1: T, y2: H - B, stroke: 'var(--ink-2)', 'stroke-width': 1, 'pointer-events': 'none', opacity: 0}, f.svg);
    const dot = CK.el('circle', {r: 4, 'pointer-events': 'none', opacity: 0}, f.svg); dot.style.fill = 'var(--c5)';
    let j = 0;
    const show = jj => { j = Math.max(0, Math.min(idx.length - 1, jj)); const i = idx[j];
      cross.setAttribute('x1', x(FT[i])); cross.setAttribute('x2', x(FT[i])); cross.setAttribute('opacity', 1);
      dot.setAttribute('cx', x(FT[i])); dot.setAttribute('cy', y(rem[j])); dot.setAttribute('opacity', 1); };
    const tipHtml = () => { const i = idx[j]; return `<b>${num(FT[i], 1)} s</b><br>board${EDGE.avg ? ' (the PMIC\'s average)' : EDGE.tau > 0 ? `, filtered (τ = ${num(EDGE.tau, 1)} s)` : ''} ${num(bp[j], 1)} W<br>rails ${num(FAST.rails[i], 1)} W<br>remainder <b>${num(rem[j], 1)} W</b>`; };
    const nearest = t => { let b = 0; idx.forEach((i, q) => { if (Math.abs(FT[i] - t) < Math.abs(FT[idx[b]] - t)) b = q; }); return b; };
    const hit = CK.el('rect', {x: L, y: T, width: W - L - R, height: H - B - T, class: 'ck-hit', tabindex: 0, role: 'img',
      'aria-label': `The remainder from ${a} to ${z} s. Left and right arrow keys step one sample.`}, f.svg);
    const at = ev => { const b = f.svg.getBoundingClientRect(), hb = f.host.getBoundingClientRect(); show(nearest(x.inv(ev.clientX - b.left)));
      TB.emit(FT[idx[j]], id); tipAt(f, tipHtml(), ev.clientX - hb.left, ev.clientY - hb.top); };
    hit.addEventListener('pointermove', at); hit.addEventListener('pointerdown', at);
    hit.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') hideTip(f); });
    const keyTip = () => { const hb = f.host.getBoundingClientRect(), b = f.svg.getBoundingClientRect(); tipAt(f, tipHtml(), b.left - hb.left + x(FT[idx[j]]), b.top - hb.top + y(rem[j])); };
    hit.addEventListener('focus', () => { show(j); keyTip(); }); hit.addEventListener('blur', () => hideTip(f));
    hit.addEventListener('keydown', ev => {
      const d = {ArrowRight: 1, ArrowLeft: -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10}[ev.key];
      if (ev.key === 'Escape') { hideTip(f); return; }
      const n = d ? j + d : ev.key === 'Home' ? 0 : ev.key === 'End' ? idx.length - 1 : null;
      if (n == null) return;
      ev.preventDefault(); show(n); TB.emit(FT[idx[j]], id); keyTip();
    });
    f.cross = t => { if (t >= a && t < z) show(nearest(t)); else { cross.setAttribute('opacity', 0); dot.setAttribute('opacity', 0); } };
    if (TB.value != null) f.cross(TB.value);
  }});
  frames.push(f);
  return f;
}
const tauRail = Math.round(RF.aifoundry2.tau_s * 10) / 10;  // the rails' own filter on this card, to the slider's step
const tauR = CK.range('edge-tau', {label: 'Filter board power with τ =', min: 0, max: 2, step: 0.1, value: 0, fmt: v => num(v, 1) + ' s',
  onInput: v => { EDGE.tau = v; redrawEdges(); }});
const preset = (label, fn) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = label; b.addEventListener('click', fn); $('edge-btns').appendChild(b); return b; };
preset('Instant reading (τ = 0)', () => { setAvg(false); tauR.set(0); });
preset(`Filter like the rails (τ = ${num(tauRail, 1)} s)`, () => { setAvg(false); tauR.set(tauRail); });
const avgBtn = toggle('edge-btns', 'The PMIC\'s own board average', false, v => setAvg(v, true));
function setAvg(v, fromBtn) {
  EDGE.avg = v; avgBtn.setAttribute('aria-pressed', String(v)); tauR.input.disabled = v;
  if (fromBtn) redrawEdges();
}
CK.legend('edge-leg', [{key: 'x', label: 'remainder (board − rails)', mark: 'line', color: 'var(--c5)'},
  {key: 'b', label: 'board power, as filtered', mark: 'line', color: 'var(--c1)'}, {key: 'r', label: 'the three rails', mark: 'line', color: 'var(--c2)'},
  {key: 's', label: 'steady levels', mark: 'dash', color: 'var(--ref)'}]);
const fEdges = [edgeFrame('edge-a', 0), edgeFrame('edge-b', 1)];
function redrawEdges() { fEdges.forEach(f => f.redraw()); }
{ // the caption, from the same data
  const r0 = [remOf(0, 0, false), remOf(1, 0, false)], near = (w, g) => FIDX[w].map((i, j) => [FT[i], r0[w][j]]).filter(([t]) => Math.abs(t - g) < 0.3).map(v => v[1]);
  const gapMins = GAPS.flatMap(g => [0, 1].filter(w => g >= FAST.windows[w][0] && g < FAST.windows[w][1]).map(w => Math.min(...near(w, g))));
  const stopMin = Math.min(...r0[1].filter((v, j) => FT[FIDX[1][j]] >= T_C1 - 0.5));
  const taus = [1.0, 1.1, 1.2, 1.3, 1.4], filt = taus.flatMap(t => [0, 1].flatMap(w => remOf(w, t, false)));
  const avg = [0, 1].flatMap(w => remOf(w, 0, true)), lv = STEADY.flat(), lo = Math.min(...lv), hi = Math.max(...lv);
  // "cleanly": every filtered sample stays within half a watt of the steady levels on either side of the edges
  const clean = Math.min(...filt) >= lo - 0.5 && Math.max(...filt) <= hi + 0.5;
  $('edge-cap').innerHTML = `At τ = 0 the remainder spikes to ${num(Math.max(...r0[0]), 1)} W when the matmul starts, and drops below zero when ` +
    `it stops (${num(stopMin, 1)} W) and at each gap between launches (to ${num(Math.min(...gapMins), 1)} W). Filter board power the way the ` +
    `PMIC filters the rails, with any τ from ${num(taus[0], 1)} to ${num(taus[taus.length - 1], 1)} s, and it ` +
    (clean ? `steps cleanly between about ${num(lo, 0)} and ${num(hi, 0)} W, the steady levels on either side of the edges.`
      : `stays within ${CK.fmt.range(Math.min(...filt), Math.max(...filt), 1, 'W')}.`) + ` The PMIC's own board average stays within ${CK.fmt.range(Math.min(...avg), Math.max(...avg), 1, 'W')}.`;
}

/* ---------- §3: the per-shire voltage map ---------- */
const VM = {rail: 'mnn', field: 'now'};
const RAIL = {mnn: 'Minion rail', sram: 'SRAM rail', noc: 'Mesh rail'};
const FIELD = {now: 'current reading', low: 'lowest captured', high: 'highest captured', swing: 'swing (high − low)'};
const vOf = (s, rail, field) => { const v = D.shires[s][rail]; return field === 'now' ? v[0] : field === 'low' ? v[1] : field === 'high' ? v[2] : v[2] - v[1]; };
const LAYOUT = D.mesh.layout, EMPTY = D.mesh.empty_cells;
// the four cells without a compute shire, labelled as the spatial temperature brief infers them (heat-per-mm die study)
const INFERRED = {'0,3': ['master', 'or spare'], '5,3': ['master', 'or spare'], '0,4': ['I/O or', 'PCIe'], '0,5': ['I/O or', 'PCIe']};
const OFFGRID = Object.keys(D.shires).filter(s => !(s in LAYOUT)).sort((a, b) => a - b);
const OFFNOTE = {32: 'master', 33: 'spare'};
function plane(rail, field) {  // least-squares plane over the grid shires; R² and the chance of doing as well by luck
  const P = Object.entries(LAYOUT).map(([s, [cx, cy]]) => [cx, cy, vOf(s, rail, field)]), n = P.length;
  // normal equations for v = a + b x + c y
  const sx = P.reduce((s, p) => s + p[0], 0), sy = P.reduce((s, p) => s + p[1], 0), sv = P.reduce((s, p) => s + p[2], 0);
  const sxx = P.reduce((s, p) => s + p[0] * p[0], 0), syy = P.reduce((s, p) => s + p[1] * p[1], 0), sxy = P.reduce((s, p) => s + p[0] * p[1], 0);
  const sxv = P.reduce((s, p) => s + p[0] * p[2], 0), syv = P.reduce((s, p) => s + p[1] * p[2], 0);
  const A = [[n, sx, sy], [sx, sxx, sxy], [sy, sxy, syy]], bvec = [sv, sxv, syv];
  const det = m => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
  const D0 = det(A), c = [0, 1, 2].map(k => det(A.map((row, i) => row.map((v, j) => (j === k ? bvec[i] : v)))) / D0);
  const mv = sv / n, ssTot = P.reduce((s, p) => s + (p[2] - mv) ** 2, 0), ssRes = P.reduce((s, p) => s + (p[2] - c[0] - c[1] * p[0] - c[2] * p[1]) ** 2, 0);
  const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;
  return {r2, p: Math.pow(1 - r2, (n - 3) / 2), n};  // F-test with 2 and n−3 degrees of freedom: P(F > f) = (1 − R²)^((n−3)/2)
}
// Twelve views (3 rails × 4 values) can be chosen, so a lean counts only if p is under 0.05 / 12.
const chance = p => (p >= 0.05 ? `no more than random scatter would give (p = ${num(p, 2)})`
  : p >= 0.05 / 12 ? `a hint only (p = ${num(p, 3)}): with twelve views to choose from, one this strong can turn up by chance`
  : `unlikely to be chance (p = ${num(p, 3)}, under ${num(0.05 / 12, 3)}, the bar for twelve views)`);
{
  const pl = plane('mnn', 'now');
  put('vmap-r2', num(100 * pl.r2, 0) + '%');
  put('vmap-shire-w', num(mean(IDLE0.map(p => p.minion)) / Object.keys(D.shires).length, 1));
  const rep = D.voltage_repeat || [];
  put('vmap-repeat', rep.length ? `${word(rep.length)} more trace dumps, taken moments later, hold later passes, and their readings differ from this map's in ` +
    `${rep.map(r => num(r.differing, 0)).join(' and ')} of its ${num(rep[0].cells, 0)} cells, by at most ${num(Math.max(...rep.map(r => r.max_abs_mv)), 0)} mV, ` +
    `${rep.every(r => r.low_high_identical) ? 'always in the current reading; every low and high is the same.' : 'including some lows and highs.'}` : '');
}
CK.seg('vmap-rail', {label: 'Rail', options: [['mnn', 'Minion'], ['sram', 'SRAM'], ['noc', 'Mesh']], value: VM.rail, onChange: v => { VM.rail = v; fMap.redraw(); }});
CK.seg('vmap-field', {label: 'Value', options: [['now', 'Now'], ['low', 'Lowest captured'], ['high', 'Highest captured'], ['swing', 'Swing']], value: VM.field,
  onChange: v => { VM.field = v; fMap.redraw(); }});
const vmLive = $('vmap-live');
const fMap = CK.frame('vmap', {height: W => { const cw = (W - 16) / 6; return Math.round(8 + 6 * cw + 24 + cw + 8); }, minW: 300, maxW: 520,
  label: 'The per-shire voltage map', draw: f => {
    const W = f.W, pad = 8, cw = (W - 2 * pad) / 6, gy = pad + 6 * cw, small = cw < 64;
    const vals = Object.keys(D.shires).map(s => vOf(s, VM.rail, VM.field));
    const lo = Math.min(...vals), hi = Math.max(...vals), spanMv = Math.max(hi - lo, 5);
    const P = v => (v - lo) / spanMv;
    for (const [cx, cy] of EMPTY) {
      const X = pad + cx * cw, Y = pad + cy * cw;
      const r = CK.el('rect', {x: X + 2, y: Y + 2, width: cw - 4, height: cw - 4, rx: 8, fill: 'none', 'stroke-width': 1.5, 'stroke-dasharray': '5 4'}, f.svg);
      r.style.stroke = 'var(--axis)';
      const lines = (INFERRED[cx + ',' + cy] || ['no compute', 'shire']).concat(['inferred']);
      lines.forEach((t, i) => CK.txt(f.svg, X + cw / 2, Y + cw / 2 + (i - (lines.length - 1) / 2) * 13 + 4, t, 'vm-note', 'middle'));
    }
    CK.txt(f.svg, pad + 2, gy + 17, small ? 'Not on the grid: master (32), spare (33)' : 'Not placed on the grid: the master shire (32) and the spare (33)', 'lab');
    const nodes = [];
    const tile = (s, X, Y) => {
      const v = vOf(s, VM.rail, VM.field), p = P(v), row = D.shires[s], g = CK.el('g', {}, f.svg);
      const r = CK.el('rect', {x: X + 2, y: Y + 2, width: cw - 4, height: cw - 4, rx: 8}, g); r.style.fill = CK.ramp(p);
      const ink = CK.rampInk(p), where = s in LAYOUT ? `(${LAYOUT[s].join(', ')})` : OFFNOTE[s];
      const t = (yy, str, cls) => { const e = CK.txt(g, X + cw / 2, yy, str, cls, 'middle'); e.style.fill = ink; return e; };
      const shown = VM.field === 'swing' ? v + ' mV' : String(v);
      if (small) t(Y + cw / 2 + 5, shown, 'vm-val');
      else {
        t(Y + cw / 2 - 12, 'shire ' + s, 'vm-sub');
        t(Y + cw / 2 + 6, shown + (VM.field === 'swing' ? '' : ' mV'), 'vm-val');
        t(Y + cw / 2 + 22, VM.field === 'now' ? 'low ' + row[VM.rail][1] : 'now ' + row[VM.rail][0], 'vm-sub');
      }
      CK.tip(f, g, () => `<b>Shire ${s}</b> ${where}<br>minion ${row.mnn[0]} mV [${row.mnn[1]}–${row.mnn[2]}]<br>SRAM ${row.sram[0]} [${row.sram[1]}–${row.sram[2]}]<br>mesh ${row.noc[0]} [${row.noc[1]}–${row.noc[2]}]`);
      nodes.push([s in LAYOUT ? LAYOUT[s][1] * 6 + LAYOUT[s][0] : 100 + +s, g]);
    };
    for (const s of Object.keys(LAYOUT)) tile(s, pad + LAYOUT[s][0] * cw, pad + LAYOUT[s][1] * cw);
    OFFGRID.forEach((s, i) => tile(s, pad + i * cw, gy + 24));
    CK.keynav(f, nodes.sort((a, b) => a[0] - b[0]).map(n => n[1]));
    // legend: one swatch per whole-mV value present, on the same scale
    const sw = []; for (let v = lo; v <= hi; v++) sw.push(`<span class="vm-sw" style="background:${CK.ramp(P(v))};color:${CK.rampInk(P(v))}">${v}</span>`);
    $('vmap-leg').innerHTML = `<span class="vm-leg-lab">${RAIL[VM.rail]}, ${FIELD[VM.field]} (mV):</span> ${sw.join('')} <span class="vm-leg-lab">1 mV steps; the colour scale spans ${spanMv} mV</span>`;
    const pl = plane(VM.rail, VM.field);
    vmLive.innerHTML = `${RAIL[VM.rail]}, ${FIELD[VM.field]}: ${CK.fmt.range(lo, hi, 0, 'mV')} over the ${vals.length} shires. A plane across the ${pl.n} grid ` +
      `shires explains R² = ${num(pl.r2, 2)} of the spread, ${chance(pl.p)}.` +
      (VM.field === 'low' || VM.field === 'swing' || VM.field === 'high' ? ' These are extremes since the last stats reset, a window that included loads that evening, not idle values.' : '');
  }});

TB.emit(60.5, 'init');  // start every linked view at one minute in, mid-matmul
