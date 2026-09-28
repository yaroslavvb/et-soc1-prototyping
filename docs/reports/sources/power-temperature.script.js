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
const RFC = CK.cardsIn(RF);                    // every card the catalogue measured, in the registry's order
const andList = a => (a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]);
const tauCards = andList(RFC.map(c => `${num(RF[c].tau_s, 2)} s on ${c}`));
put('kpi-tau', tauCards); put('rf-tau', tauCards);
put('rf-n', andList(RFC.map((c, i) => `${num(RF[c].n, 0)}${i ? '' : ' load bursts'} on ${c}`)));
put('rf-12s', andList(RFC.map((c, i) => (i ? `${pct(RF[c].frac_1s)} and ${pct(RF[c].frac_2s)} on ${c}`
  : `${pct(RF[c].frac_1s)} after 1 s and ${pct(RF[c].frac_2s)} after 2 s on ${c}`))));
{ // the busy drift of the strict Horace runs on each card, with how well its runs pin it down
  const BD = CX.busy_drift_cards, a2 = BD.aifoundry2, a3 = BD.aifoundry3;
  const rng = c => wholeRange(c.temp_c[0], c.temp_c[1]);
  put('busy-drift', `${num(a2.w_per_c, 2)} W/°C at ${rng(a2)} °C (the ${word(a2.runs)} runs that heated the die by at least 3 °C, standard error ${num(a2.se, 2)} W/°C)`);
  // a card's runs one by one: when the largest is more than twice the next, name it apart from the rest
  const each = c => { const e = [...(c.each || [])].sort((x, y) => x - y), n = e.length;
    if (n < 3) return '';
    return e[n - 1] > 2 * e[n - 2] ? `: ${word(n - 1)} gave ${CK.fmt.range(e[0], e[n - 2], 2, 'W/°C')} (median ${num(median(e.slice(0, -1)), 2)}) and one ${num(e[n - 1], 2)}`
      : `: from ${num(e[0], 2)} to ${num(e[n - 1], 2)} W/°C`; };
  put('busy-drift-a3', `On aifoundry3 the same runs at ${rng(a3)} °C, where the idle law's own slope is about ` +
    `${num(lawSlope((a3.temp_c[0] + a3.temp_c[1]) / 2), 2)} W/°C, gave ${num(a3.w_per_c, 2)} W/°C on average` +
    (a3.se > 0.1 * a3.w_per_c ? `, but its ${word(a3.runs)} runs scatter widely (standard error ${num(a3.se, 2)} W/°C)${each(a3)}.`
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
  put('ddr-idle', `In this session the DDR domain reads ${num(dI, 0)} mV on die at ${num(tI, 0)} °C idle and ${num(dC, 0)} mV at ${num(tC, 0)} °C, ` +
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
const railTxt = 'τ ≈ ' + andList(RFC.map((c, i) => `${num(RF[c].tau_s, 2)} s and ${pct(RF[c].frac_2s)}${i ? '' : ' of a step after 2 s'} on ${c}`));
const M = [
 ['Board power, now', 'whole card · a new value each SP pass: about every 156 ms on aifoundry2, 158 ms on aifoundry1-c1 and 263 ms on aifoundry3 while ettelem samples at 10 Hz (126–135, 134–139 and 223–224 ms with a one-command poller at 10 Hz; three passes per card) · 10 mW', 'DM_CMD_GET_MODULE_POWER (ettelem: up to 45 samples/s; the SP refreshes it once per pass)', 'works_now', 'works now'],
 ['Board power, PMIC average / min / max', 'whole card · the PMIC\'s running average, like the rails; min and max since the last stats reset', 'DM_CMD_GET_SP_STATS via ettelem (the stock CLI calls it unsupported), or the SPST trace', 'works_now', 'works now'],
 ['Rail power: minion cores, SRAM, mesh', `3 rails · 1 mW · the PMIC's running average (${railTxt}), one record per SP pass, plus min/max`, 'same snapshot; the SPST trace keeps the last 6,500–6,700 records, one per pass, with µs stamps: about 17 min on aifoundry2, 16 min on aifoundry1-c1 and 29 min on aifoundry3 (the longest extracts of the three-card check)', 'works_now', 'works now'],
 ['Rail voltage and clock', '3 rails · 1 mV · avg/min/max; minion and mesh MHz', 'same snapshot', 'works_now', 'works now'],
 ['On-die voltage per domain', '7 domains (DDR, SRAM, Maxion, minion, PCIe shire, mesh, IO shire) · 1 mV', 'DM_CMD_GET_ASIC_VOLTAGE; compare with the regulator set-points from DM_CMD_GET_MODULE_VOLTAGE for the drop to the die', 'works_now', 'works now'],
 ['On-die voltage per shire', '34 minion shires × 3 rails · 1 mV · current, and hardware low/high between polls; the 8 memory shires × 2 are printed only right after a telemetry query, so idle dumps hold the 34 minion shires', 'SP log at DEBUG level: ettelem loglevel debug + sptrace (4 KB buffer, wraps about once per pass: 22 of 27 dumps on three cards held a whole pass)', 'works_now', 'works now'],
 ['Temperature', 'IO shire, and mean, low and high of the 34 minion-shire sensors · 1 °C · per SP pass; "low/high" are extremes since reset, not the current spread', 'DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (its field labelled PMIC holds the minion mean again)', 'works_now', 'works now'],
 ['Power state, throttle residency, thresholds', 'card-wide · µs residency counters', 'DM_CMD_GET_MODULE_POWER_STATE, _RESIDENCY_*, _TEMPERATURE_THRESHOLDS, _STATIC_TDP_LEVEL', 'works_now', 'works now'],
 ['Device-wide bandwidth and utilisation', 'DDR, L2/L3, PCIe · 1 ms samples', 'MMST trace; a proxy for where memory energy goes', 'works_now', 'works now'],
 ['Energy per event', 'pJ per load, per multiply-add, per mesh hop · needs ≥10⁹ identical events/s for seconds', 'rail power above a same-temperature baseline ÷ event rate (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#where-the-energy-goes">memory anatomy</a>, <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment">the Horace experiment</a>; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual">the energy manual</a> does it for every instruction and byte)', 'works_now', 'works now'],
 ['Static against dynamic power', 'per rail', 'frequency sweep at fixed voltage: DM_CMD_SET_FREQUENCY with power management off. Changes the card for everyone, which the lab leaves to its admin; not run here', 'research_only', 'lab admin only'],
 ['Instantaneous rail power', '3 rails · 1 mW · per pass', 'the SP already reads it each pass and discards it; a few assignments in thermal_pwr_mgmt.c', 'needs_fw_change', 'firmware'],
 ['Faster sampling', 'tens to hundreds of Hz', 'in the firmware source each pass makes ~96 I2C transactions, each followed by a hard-coded 1 ms wait, a floor of about 100 ms; the measured pass is longer. In the SP\'s own trace (three passes per card) it is 133 ms on aifoundry2 and 135 ms on aifoundry1-c1 with no telemetry client, 160 and 162 ms while ettelem samples at 10 Hz; on aifoundry3 224 and 266 ms, 1.7× as long, for reasons not established. Under the sampler the board-power stream shows a new value 3–5 ms sooner than the trace\'s pass (156, 158 and 263 ms, the lede): the two methods differ by that much. Skip the 84-read snapshot and fix the wait', 'needs_fw_change', 'firmware'],
 ['Per-shire temperature; process detectors', '34 shires · 0.06 °C in hardware; ring-oscillator counts in µs windows', 'sampled continuously by the PVT controllers, never exported', 'needs_fw_change', 'firmware'],
 ['DDR, PCIe, Maxion, IO rails', '—', 'regulators with set-points but no current sense: only "board minus three rails"', 'impossible_on_silicon', 'no sensor'],
 ['Board power at kHz', 'whole card · ~1 ms', 'scope on the hot-swap controller\'s current-monitor pin, or a PCIe riser with a shunt', 'needs_tooling', 'hardware'],
];
$('methods').innerHTML = '<thead><tr><th>What</th><th>Granularity</th><th>How</th><th>Status</th></tr></thead><tbody>' +
  M.map(r => `<tr><td class="lvl" style="white-space:normal">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${chip(r[3], r[4])}</td></tr>`).join('') + '</tbody>';
CK.stackTable($('methods'));
CK.sortTable('methods');  // after stackTable. (No filter box: chartkit's inserts it via t.parentNode before the .wide wrapper, which is that parent.)

/* ---------- §1: what asking costs, the SP's pass under each way of polling (V3-TEL, D.tel_v3.sp_pass) ---------- */
// sp_pass.cards.<card>[] holds each pass's median SP-record interval (ms) in each arm; arms are in the check's order,
// lightest first. A fresh board value arrives once per pass, so 1000 / ms is the fresh readings per second.
const SPP = D.tel_v3 && D.tel_v3.sp_pass;
if (SPP && Object.keys(SPP.cards).length) {
  const ARMS = SPP.arms, AC = CK.cardsIn(SPP.cards);
  const vals = (c, a) => SPP.cards[c].map(p => p.ms[a]).filter(v => v != null && isFinite(v));
  const mid = (c, a) => { const v = vals(c, a); return v.length ? median(v) : null; };
  const rngMs = (c, a) => { const v = vals(c, a); return CK.fmt.range(Math.min(...v), Math.max(...v), 1, 'ms'); };
  const perS = ms => 1000 / ms;
  const R = (f, a, b) => CK.fmt.range(Math.min(a, b), Math.max(a, b), f);
  const across = fn => { const v = AC.map(fn).filter(x => x != null && isFinite(x)); return [Math.min(...v), Math.max(...v)]; };
  const cardList = fn => andList(AC.map(c => `${fn(c)} on ${CK.card(c).label}`));
  const haloA = t => { Object.assign(t.style, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '4px', strokeLinejoin: 'round'}); return t; };
  CK.legend('askcost-leg', CK.cardLegend(AC).concat([{key: 'ask', label: 'the interval the host asked at', mark: 'line', color: 'var(--ink-2)'}]));
  const hasE = ['E10', 'E20', 'E40'].every(a => ARMS.some(x => x.key === a));
  CK.frame('askcost', {label: 'The service processor’s pass length under each way of polling the card, per card',
    height: W => { const rowH = W < 600 ? 50 : 34; return 30 + rowH * ARMS.length + 42; }, minW: 280, draw: f => {
      const nar = f.narrow, rowH = nar ? 50 : 34, L = nar ? 10 : 220, Rm = 56, T = 30, B = 42, yb = f.H - B;
      const all = AC.flatMap(c => ARMS.flatMap(a => vals(c, a.key)));
      const hi = Math.ceil(Math.max(...all) * 1.04 / 100) * 100;
      const x = CK.lin(0, hi, L, f.W - Rm), xt = x.ticks(nar ? 4 : 6);
      const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      for (const t of xt) CK.el('line', {x1: x(t), x2: x(t), y1: T - 8, y2: yb, class: 'grid-line'}, g0);
      CK.axes(f, {x, y: CK.lin(0, 1, yb, T), L, R: Rm, T, B, xt, yt: [], grid: false, xfmt: v => num(v, 0),
        xl: 'service-processor pass, ms (one fresh board value per pass)'});
      const rowY = i => T + rowH * i + (nar ? 34 : rowH / 2), rowLabs = [];
      ARMS.forEach((a, i) => {
        if (i) CK.el('line', {x1: nar ? L : 8, x2: f.W - Rm, y1: T + rowH * i, y2: T + rowH * i, class: 'grid-line'}, g0);
        const y = rowY(i);
        rowLabs.push(haloA(nar ? CK.txt(g0, L, y - 16, a.what, 'lab') : CK.txt(g0, L - 12, y + 4, a.what, 'lab', 'end')));
      });
      if (hasE) for (const c of AC) {   // ettelem at 10, 20 and 40 Hz: one thin line per card through its three medians
        const pts = ['E10', 'E20', 'E40'].map(k => [mid(c, k), rowY(ARMS.findIndex(q => q.key === k))]).filter(p => p[0] != null);
        const ln = CK.el('path', {d: pts.map((p, j) => (j ? 'L' : 'M') + x(p[0]).toFixed(1) + ',' + p[1].toFixed(1)).join(' '),
          fill: 'none', 'stroke-width': 1.5, 'aria-hidden': 'true'}, f.svg);
        ln.style.stroke = CK.card(c).color; ln.style.opacity = '0.55';
      }
      /* the row labels over those lines: on a phone the lines cross the labels' rows, and pass under their halo */
      const gT = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      rowLabs.forEach(t => gT.appendChild(t));
      const nodes = [], ends = [];
      ARMS.forEach((a, i) => {   // the interval the host asked at, where it asked at a fixed one
        if (a.ask_ms == null) return;
        const y = rowY(i), t = CK.el('line', {x1: x(a.ask_ms), x2: x(a.ask_ms), y1: y - 8, y2: y + 8, 'stroke-width': 2, 'aria-hidden': 'true'}, g0);
        t.style.stroke = 'var(--ink-2)';
      });
      ARMS.forEach((a, i) => {
        const y = rowY(i), q = ARMS[0].key;
        AC.forEach((c, k) => {
          const v = vals(c, a.key);
          if (!v.length) return;
          const m = mid(c, a.key), cd = CK.card(c), dy = (k - (AC.length - 1) / 2) * 3, gr = CK.el('g', {}, f.svg);
          CK.cardMark(gr, c, x(m), y + dy, 5);
          CK.el('rect', {x: x(m) - 9, y: y + dy - 9, width: 18, height: 18, class: 'ck-hit'}, gr);
          const q0 = mid(c, q), ratio = q0 ? m / q0 : null;
          CK.tip(f, gr, `<b>${cd.label}</b>, ${a.what}` +
            `<br>pass ${num(m, 1)} ms (median of ${num(v.length, 0)} passes: ${rngMs(c, a.key)})` +
            (a.key !== q && ratio ? `<br>${num(m - q0, 1)} ms longer than with nothing polling (×${num(ratio, 2)})` : '') +
            `<br>a fresh board value ${num(perS(m), 1)} times a second` + (a.ask_ms ? `, asked for ${num(1000 / a.ask_ms, 0)} times a second` : ''));
          nodes.push(gr);
        });
        const top = Math.max(...AC.flatMap(c => vals(c, a.key)));
        if (a.key === 'E40' || a.key === q) {   // direct labels on the first and the heaviest arm only
          const lab = AC.map(c => mid(c, a.key)).filter(v => v != null);
          ends.push(haloA(CK.txt(g0, x(top) + 10, y + 4, R(0, Math.min(...lab), Math.max(...lab)) + ' ms', 'lab-strong')));
        }
      });
      CK.inside(f, ends);
      CK.keynav(f, nodes);
    }});
  // the caption, from the same numbers
  const Q = c => mid(c, 'Q'), d = (c, a) => mid(c, a) - Q(c), rt = (c, a) => mid(c, a) / Q(c);
  const one = across(c => Math.max(d(c, 'PWR'), d(c, 'L10')));
  const e10 = across(c => d(c, 'E10')), vo = across(c => d(c, 'VOLT')), r40 = across(c => rt(c, 'E40'));
  const f10 = across(c => perS(mid(c, 'E10'))), f40 = across(c => perS(mid(c, 'E40'))), e40 = ARMS.find(a => a.key === 'E40');
  $('askcost-cap').innerHTML = `With nothing polling, the pass takes ${cardList(c => num(Q(c), 0) + ' ms')}. ` +
    `A single power command, even every ~${num(ARMS.find(a => a.key === 'PWR').ask_ms, 0)} ms, lengthens it by at most ${num(Math.max(0, one[1]), 1)} ms; the voltage command loop by ` +
    `${R(0, vo[0], vo[1])} ms; <code>ettelem</code>'s snapshot at 10 Hz by ${R(0, e10[0], e10[1])} ms, and by more the faster it samples. ` +
    `At 40 Hz the pass is ${R(1, r40[0], r40[1])} times its quiet length: <code>ettelem</code> asks for ${num(1000 / e40.ask_ms, 0)} readings a second and ` +
    `gets a fresh board value ${R(1, f40[0], f40[1])} times a second, fewer than at 10 Hz (${R(1, f10[0], f10[1])}). ` +
    `The short grey ticks mark the interval the host asked at. Each mark is a card's median over its three passes, which agree within ${num(Math.max(...AC.flatMap(c => ARMS.map(a => { const v = vals(c, a.key); return v.length ? Math.max(...v) - Math.min(...v) : 0; }))), 1)} ms. ` +
    `Source: V3-TEL, <code>tel.json</code> <code>passes.&lt;card&gt;[].sp</code>; the arms ran in a shuffled order, 30 s apart.`;
}

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
let fDrift = null;  // the busy-drift chart below, which shows the matmul fit's slope
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
  let h = `This session, fit from ${PV.from} s after launch: board <b>${num(F.board.b, 2)} W/°C</b> (minion ${num(F.minion, 2)}) over ${F.P.length} bins at ` +
    `${CK.fmt.range(F.t0, F.t1, 1, '°C')}; the idle law's own slope there: ${num(F.law, 2)} W/°C.`;
  h += PV.dropGaps ? ` With the ${word(fitOf(PV.from, false).P.length - F.P.length)} launch-gap bins: ${num(G.board.b, 2)} W/°C.`
    : ` Without the ${word(nGap)} launch-gap bins: ${num(G.board.b, 2)} W/°C.`;
  if (PV.view === 'above') h += ` Median above the law in this session, leaving out each phase's first 3 s and the gap bins: ` +
    ['idle', 'dram', 'matmul'].filter(g => MED[g]).map(g => `${GNAME[g]} ${sign(MED[g].m)} W`).join(', ') + '.';
  pvtRead.set(h);
  if (fDrift) { fDrift.redraw(); driftOut(); }
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

/* ---------- §2 bullet 1: the busy drift on each card, with its uncertainty ---------- */
// context.busy_drift_cards: per card, the mean slope over its strict Horace runs (w_per_c), the runs' sd, the standard
// error of the mean, the run count and the die temperatures. Cards come from the data's keys, in the registry's order,
// with the registry's colour and mark, so a card added to the data appears with no change here.
const BD = CX.busy_drift_cards || {}, BV3 = CX.busy_drift_loadstep_v3 || {};
// Two groups of rows: the strict Horace runs (busy_drift_cards) and the version-3 check's repeats of this page's load step
// (busy_drift_loadstep_v3, MMB-T/P1: four 58 s matmuls per card, with each repeat's slope in `each`).
const GROUPS = [
  {key: 'strict', title: 'Strict 7 s Horace runs, 21–22 September', short: 'Strict Horace runs, 21–22 Sep', unit: 'runs', data: BD},
  {key: 'v3', title: 'This load step, repeated four times per card, 26 September', short: 'This load step, 4 repeats, 26 Sep', unit: 'load steps', data: BV3}]
  .map(g => Object.assign(g, {cards: CK.cardsIn(g.data).filter(c => g.data[c] && isFinite(g.data[c].w_per_c))}))
  .filter(g => g.cards.length);
const DROWS = GROUPS.flatMap(g => g.cards.map(c => ({g, c, v: g.data[c]})));
const DCARDS = CK.cardsIn([...new Set(DROWS.map(r => r.c))]);
const two = r => 2 * (r.v.se || 0);
const halo = t => { Object.assign(t.style, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '4px', strokeLinejoin: 'round'}); return t; };
const driftRefs = () => {
  const fit = fitOf(PV.from, PV.dropGaps).board.b, lw = lawSlope(80);
  return [{key: 'law', v: lw, text: `idle law at 80 °C: ${num(lw, 2)}`, color: 'var(--ink)', dash: '5 4', row: 0},
    {key: 'fit', v: fit, text: `this session's matmul fit: ${num(fit, 2)}`, color: 'var(--ink-2)', dash: null, row: 1}];
};
CK.legend('drift-leg', CK.cardLegend(DCARDS).concat([
  {key: 'rep', label: 'one load step (lower rows)', mark: 'ring', color: 'var(--ink-2)'},
  {key: 'fit', label: 'matmul fit, this session (aifoundry2)', mark: 'line', color: 'var(--ink-2)'},
  {key: 'law', label: 'idle law’s slope at 80 °C (aifoundry2)', mark: 'dash', color: 'var(--ink)'}]));
const driftRead = CK.readout('drift-out');
function driftOut() {
  const r = driftRefs();
  driftRead.set(GROUPS.map(g => `<b>${g.title}:</b> ` + g.cards.map(c => { const v = g.data[c];
    return `${CK.card(c).label} <b>${num(v.w_per_c, 2)} W/°C</b> (±${num(2 * (v.se || 0), 2)} at 2 se; ${num(v.runs, 0)} ${g.unit} at ${wholeRange(v.temp_c[0], v.temp_c[1])} °C)`; }).join(' · ')).join('<br>') +
    `<br>For reference: the matmul fit ${num(r[1].v, 2)}, the idle law at 80 °C ${num(r[0].v, 2)} W/°C.`);
}
const GH = 24;  // a group's title line
const driftH = W => { const rowH = W < 600 ? 56 : 38; return 44 + GROUPS.length * GH + rowH * Math.max(1, DROWS.length) + 38; };
fDrift = CK.frame('drift', {label: 'Busy drift per card, in the strict runs and in the load step’s repeats: the mean slope with ±2 standard errors, against the matmul fit and the idle law',
  height: driftH, minW: 280, draw: f => {
    const nar = f.narrow, rowH = nar ? 56 : 38, L = nar ? 12 : 250, R = 52, T = 44, B = 38, yb = f.H - B;
    const refs = driftRefs();
    const vals = DROWS.flatMap(r => [r.v.w_per_c - two(r), r.v.w_per_c + two(r)].concat(r.v.each && r.g.key === 'v3' ? r.v.each : [])).concat(refs.map(q => q.v));
    const lo = Math.min(0, Math.floor(Math.min(...vals) / 0.2) * 0.2), hi = Math.ceil(Math.max(...vals) * 1.05 / 0.2) * 0.2;
    const x = CK.lin(lo, hi, L, f.W - R), xt = x.ticks(nar ? 4 : 6);
    const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    for (const t of xt) CK.el('line', {x1: x(t), x2: x(t), y1: T - 6, y2: yb, class: 'grid-line'}, g0);
    CK.axes(f, {x, y: CK.lin(0, 1, yb, T), L, R, T, B, xt, yt: [], grid: false, xfmt: v => num(v, 1), xl: 'W per °C of die temperature (board power, the same work)'});
    const labs = [];
    for (const q of refs) {
      const e = CK.el('line', {x1: x(q.v), x2: x(q.v), y1: T - 6, y2: yb, 'stroke-width': 1.5}, g0);
      e.style.stroke = q.color; if (q.dash) e.style.strokeDasharray = q.dash;
      labs.push(CK.txt(g0, x(q.v), 13 + 16 * q.row, q.text, 'lab', 'middle'));
    }
    CK.inside(f, labs);
    const nodes = [];
    let y0 = T;
    GROUPS.forEach((g, gi) => {
      if (gi) CK.el('line', {x1: nar ? L : 8, x2: f.W - R, y1: y0 + 2, y2: y0 + 2, class: 'grid-line'}, g0);
      halo(CK.txt(g0, nar ? L : 8, y0 + 17, nar ? g.short : g.title, 'lab-strong'));
      y0 += GH;
      g.cards.forEach(c => {
        const v = g.data[c], cd = CK.card(c), y = y0 + (nar ? 34 : rowH / 2), w = v.w_per_c, e2 = 2 * (v.se || 0);
        const name = `${cd.label} · ${wholeRange(v.temp_c[0], v.temp_c[1])} °C · ${num(v.runs, 0)} ${g.unit}`;
        // on a phone the name sits above its row, where the reference lines cross it: a page-coloured outline stops them short
        halo(nar ? CK.txt(g0, L, y - 16, name, 'lab') : CK.txt(g0, L - 12, y + 4, name, 'lab', 'end'));
        const gr = CK.el('g', {}, f.svg);
        if (e2 > 0) {
          const wl = CK.el('line', {x1: x(w - e2), x2: x(w + e2), y1: y, y2: y, 'stroke-width': 2}, gr); wl.style.stroke = cd.color;
          for (const u of [w - e2, w + e2]) { const cap = CK.el('line', {x1: x(u), x2: x(u), y1: y - 5, y2: y + 5, 'stroke-width': 2}, gr); cap.style.stroke = cd.color; }
        }
        if (g.key === 'v3') for (const e of v.each || []) {   // each load step, as a small ring on the row
          const ring = CK.el('circle', {cx: x(e), cy: y, r: 3.5, fill: 'none', 'stroke-width': 1.3}, gr); ring.style.stroke = 'var(--ink-2)';
        }
        CK.cardMark(gr, c, x(w), y, 5.5);
        halo(CK.txt(gr, Math.max(...[w + e2].concat(g.key === 'v3' ? v.each || [] : []).map(x)) + 8, y + 4, num(w, 2), 'lab-strong'));
        CK.el('rect', {x: L, y: y - (nar ? 26 : rowH / 2), width: f.W - L - R, height: nar ? 40 : rowH, class: 'ck-hit'}, gr);
        const tip = g.key === 'v3'
          ? `<b>${cd.label}</b>: ${num(w, 2)} W/°C, the mean over this page's load step repeated ${num(v.runs, 0)} times (26 September)` +
            `<br>each: ${v.each.map((e, k) => `${num(e, 2)} at ${wholeRange(v.each_temp_c[k][0], v.each_temp_c[k][1])} °C`).join('; ')}` +
            `<br>standard error ${num(v.se, 2)}; 99% interval ${num(v.ci99[0], 2)} to ${num(v.ci99[1], 2)} W/°C${v.tested ? '' : ' (reported, not tested against a band)'}`
          : `<b>${cd.label}</b>: ${num(w, 2)} W/°C, the mean over ${num(v.runs, 0)} strict runs at ${wholeRange(v.temp_c[0], v.temp_c[1])} °C` +
            `<br>run-to-run sd ${num(v.sd, 2)}, standard error ${num(v.se, 2)}; ±2 standard errors: ${num(w - e2, 2)} to ${num(w + e2, 2)} W/°C`;
        CK.tip(f, gr, tip);
        nodes.push(gr);
        y0 += rowH;
      });
    });
    CK.keynav(f, nodes);
  }});
driftOut();

/* ---------- §2 bullet 4: the remainder at the load edges, board power filtered like the rails ---------- */
const EDGE = {tau: 0, avg: false};
const FT = FAST.t, FIDX = FAST.windows.map(([a, z]) => FT.map((t, i) => i).filter(i => FT[i] >= a && FT[i] < z));
// a "fresh" 10 Hz sample: FAST.board actually changed from the sample before it (the service processor's own pass rate)
const FRESH = FIDX.map(idx => idx.filter((i, j) => j > 0 && FAST.board[i] !== FAST.board[idx[j - 1]]));
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
    const fresh = FRESH[w];
    fresh.forEach(i => CK.el('line', {x1: x(FT[i]), x2: x(FT[i]), y1: H - B, y2: H - B - 4, stroke: 'var(--c1)', 'stroke-width': 1, opacity: 0.6}, f.svg));
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
    const fDur = FT[idx[idx.length - 1]] - FT[idx[0]], fMs = fDur * 1000 / fresh.length;
    edgeOut[w].set(`remainder from ${num(Math.min(...rem), 1)} to ${num(Math.max(...rem), 1)} W · ` +
      `${num(fresh.length, 0)} new board readings (ticks) in ${num(fDur, 1)} s, one per ~${num(fMs, 0)} ms`);
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
  {key: 's', label: 'steady levels', mark: 'dash', color: 'var(--ref)'},
  {key: 'f', label: 'tick: a fresh board reading (10 Hz log, slower true rate)', mark: 'line', color: 'var(--c1)'}]);
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
      : `stays within ${CK.fmt.range(Math.min(...filt), Math.max(...filt), 1, 'W')}.`) + ` The PMIC's own board average stays within ${CK.fmt.range(Math.min(...avg), Math.max(...avg), 1, 'W')}.` +
    ` The ticks under each panel mark the samples where the board reading actually changed; between them our 10 Hz log just repeats the last value (each panel's readout gives the count and rate).`;
}

/* ---------- §3: the per-shire voltage map ---------- */
// The map shows the 20 September capture (D.shires, aifoundry2 at idle) or, from the three-card check, a card's idle or
// loaded dump (D.tel_v3.vmaps: for each card the passes of TEL-Q's Q4 test; the map uses the first pass whose two dumps
// each held one whole pass, else the first).
const VM = {rail: 'mnn', field: 'now', cap: 'sep20', card: 'aifoundry2'};
const RAIL = {mnn: 'Minion rail', sram: 'SRAM rail', noc: 'Mesh rail'};
const FIELD = {now: 'current reading', low: 'lowest captured', high: 'highest captured', swing: 'swing (high − low)'};
const VMV3 = (D.tel_v3 && D.tel_v3.vmaps && D.tel_v3.vmaps.cards) || {};
const VCARDS = CK.cardsIn(VMV3);
const vPass = c => { const ps = VMV3[c].passes; return ps.find(p => p.idle.whole_pass && p.load.whole_pass) || ps[0]; };
const curMap = () => (VM.cap === 'sep20' || !VMV3[VM.card] ? D.shires : vPass(VM.card)[VM.cap].map);
const capName = () => (VM.cap === 'sep20' || !VMV3[VM.card] ? 'aifoundry2, 20 September, idle'
  : `${CK.card(VM.card).label}, 26 September, ${VM.cap === 'load' ? 'under a 7 s load' : 'idle'} (pass ${vPass(VM.card).pass})`);
const vOf = (s, rail, field) => { const v = curMap()[s][rail]; return field === 'now' ? v[0] : field === 'low' ? v[1] : field === 'high' ? v[2] : v[2] - v[1]; };
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
  put('vmap-repeat', rep.length ? `${word(rep.length)} more trace dumps, taken about 0.3 s later, hold later passes, and their readings differ from this map's in ` +
    `${rep.map(r => num(r.differing, 0)).join(' and ')} of its ${num(rep[0].cells, 0)} cells, by at most ${num(Math.max(...rep.map(r => r.max_abs_mv)), 0)} mV, ` +
    `${rep.every(r => r.low_high_identical) ? 'always in the current reading; every low and high is the same.' : 'including some lows and highs.'}` : '');
}
if (VCARDS.length) {   // which capture: the 20 September one is aifoundry2's, so choosing it selects that card
  const capSeg = CK.seg('vmap-cap', {label: 'Capture', options: [['sep20', '20 Sep, idle'], ['idle', '26 Sep, idle'], ['load', '26 Sep, under load']],
    value: VM.cap, onChange: v => { VM.cap = v; if (v === 'sep20' && VM.card !== 'aifoundry2') { VM.card = 'aifoundry2'; cardSeg.quiet('aifoundry2'); } fMap.redraw(); }});
  const cardSeg = CK.seg('vmap-card', {label: 'Card', options: VCARDS.map(c => [c, CK.card(c).label]), value: VM.card,
    onChange: v => { VM.card = v; if (VM.cap === 'sep20' && v !== 'aifoundry2') { VM.cap = 'idle'; capSeg.quiet('idle'); } fMap.redraw(); }});
}
CK.seg('vmap-rail', {label: 'Rail', options: [['mnn', 'Minion'], ['sram', 'SRAM'], ['noc', 'Mesh']], value: VM.rail, onChange: v => { VM.rail = v; fMap.redraw(); }});
CK.seg('vmap-field', {label: 'Value', options: [['now', 'Now'], ['low', 'Lowest captured'], ['high', 'Highest captured'], ['swing', 'Swing']], value: VM.field,
  onChange: v => { VM.field = v; fMap.redraw(); }});
const vmLive = $('vmap-live');
const VM_TILES = {};
let VM_HI = null;   // a shire lit from the offset chart below, when the map shows that shire's card and a check capture
function vmHi(sh) {   // sh: a list of shire numbers to outline on the map, or null
  VM_HI = sh;
  const on = new Set((sh || []).map(String));
  for (const [k, r] of Object.entries(VM_TILES)) { r.style.stroke = on.has(k) ? 'var(--ink)' : ''; r.style.strokeWidth = on.has(k) ? '3px' : ''; }
}
const fMap = CK.frame('vmap', {height: W => { const cw = (W - 16) / 6; return Math.round(8 + 6 * cw + 24 + cw + 8); }, minW: 300, maxW: 520,
  label: 'The per-shire voltage map', draw: f => {
    const W = f.W, pad = 8, cw = (W - 2 * pad) / 6, gy = pad + 6 * cw, small = cw < 64;
    const vals = Object.keys(curMap()).map(s => vOf(s, VM.rail, VM.field));
    const lo = Math.min(...vals), hi = Math.max(...vals), spanMv = Math.max(hi - lo, 5);
    const P = v => (v - lo) / spanMv;
    for (const [cx, cy] of EMPTY) {
      const X = pad + cx * cw, Y = pad + cy * cw;
      const r = CK.el('rect', {x: X + 2, y: Y + 2, width: cw - 4, height: cw - 4, rx: 8, fill: 'none', 'stroke-width': 1.5, 'stroke-dasharray': '5 4'}, f.svg);
      r.style.stroke = 'var(--axis)';
      const lines = (INFERRED[cx + ',' + cy] || ['no compute', 'shire']).concat(['inferred']);
      const lh = 15;   /* 12 px text on 15 px lines: the three lines stay apart, even in a phone's small cell */
      lines.forEach((t, i) => CK.txt(f.svg, X + cw / 2, Y + cw / 2 + (i - (lines.length - 1) / 2) * lh + 4, t, 'vm-note', 'middle'));
    }
    CK.txt(f.svg, pad + 2, gy + 17, small ? 'Not on the grid: master (32), spare (33)' : 'Not placed on the grid: the master shire (32) and the spare (33)', 'lab');
    const nodes = [];
    for (const k in VM_TILES) delete VM_TILES[k];
    const tile = (s, X, Y) => {
      const v = vOf(s, VM.rail, VM.field), p = P(v), row = curMap()[s], g = CK.el('g', {}, f.svg);
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
      CK.tip(f, g, () => `<b>Shire ${s}</b> ${where} · ${capName()}<br>minion ${row.mnn[0]} mV [${row.mnn[1]}–${row.mnn[2]}]<br>SRAM ${row.sram[0]} [${row.sram[1]}–${row.sram[2]}]<br>mesh ${row.noc[0]} [${row.noc[1]}–${row.noc[2]}]`);
      nodes.push([s in LAYOUT ? LAYOUT[s][1] * 6 + LAYOUT[s][0] : 100 + +s, g]);
      VM_TILES[s] = r;
    };
    for (const s of Object.keys(LAYOUT)) tile(s, pad + LAYOUT[s][0] * cw, pad + LAYOUT[s][1] * cw);
    OFFGRID.forEach((s, i) => tile(s, pad + i * cw, gy + 24));
    CK.keynav(f, nodes.sort((a, b) => a[0] - b[0]).map(n => n[1]));
    // legend: one swatch per whole-mV value present, on the same scale
    const sw = []; for (let v = lo; v <= hi; v++) sw.push(`<span class="vm-sw" style="background:${CK.ramp(P(v))};color:${CK.rampInk(P(v))}">${v}</span>`);
    $('vmap-leg').innerHTML = `<span class="vm-leg-lab">${RAIL[VM.rail]}, ${FIELD[VM.field]} (mV):</span> ${sw.join('')} <span class="vm-leg-lab">1 mV steps; the colour scale spans ${spanMv} mV</span>`;
    const pl = plane(VM.rail, VM.field);
    vmLive.innerHTML = `<b>${capName()}.</b> ${RAIL[VM.rail]}, ${FIELD[VM.field]}: ${CK.fmt.range(lo, hi, 0, 'mV')} over the ${vals.length} shires. A plane across the ${pl.n} grid ` +
      `shires explains R² = ${num(pl.r2, 2)} of the spread, ${chance(pl.p)}.` +
      (VM.field === 'low' || VM.field === 'swing' || VM.field === 'high' ? ' These are extremes since the last stats reset' +
        (VM.cap === 'sep20' ? ' (when that was is not recorded for this capture), not idle values.' : ', not current readings.') : '');
    vmHi(VM_HI);
  }});

/* ---------- §3: the offset test drawn (TEL-Q, item Q4): each shire's idle deviation against its loaded one ---------- */
// One panel per card (D.tel_v3.vmaps, the pass the map above uses): x = the shire's minion-rail reading at idle less the
// 34-shire idle mean, y = the same under the 7 s load. A fixed per-monitor offset puts every shire on y = x. Readings are
// whole millivolts, so shires share points; a bubble's area grows with how many do.
if (VCARDS.length) {
  const S34 = Object.keys(VMV3[VCARDS[0]].passes[0].idle.map);
  const sdv = a => { const m = mean(a); return Math.sqrt(a.reduce((t, v) => t + (v - m) ** 2, 0) / (a.length - 1)); };
  const corr = (a, b) => { const ma = mean(a), mb = mean(b); let sab = 0, saa = 0, sbb = 0;
    a.forEach((v, k) => { sab += (v - ma) * (b[k] - mb); saa += (v - ma) ** 2; sbb += (b[k] - mb) ** 2; }); return sab / Math.sqrt(saa * sbb); };
  const PAN = VCARDS.map(c => {
    const p = vPass(c), iv = S34.map(s => p.idle.map[s].mnn[0]), lv = S34.map(s => p.load.map[s].mnn[0]);
    const mi = mean(iv), ml = mean(lv), pts = S34.map((s, k) => ({s, i: iv[k], l: lv[k], x: iv[k] - mi, y: lv[k] - ml}));
    const cells = {};
    pts.forEach(q => { const k = q.i + ',' + q.l; (cells[k] = cells[k] || []).push(q); });
    const r = corr(iv, lv), sdI = sdv(iv), sdL = sdv(lv);
    return {c, p, pts, cells: Object.values(cells).sort((a, b) => a[0].x - b[0].x || a[0].y - b[0].y), r, sdI, sdL, slope: r * sdL / sdI};
  });
  const lim = Math.ceil(Math.max(...PAN.flatMap(P => P.pts.flatMap(q => [Math.abs(q.x), Math.abs(q.y)]))) + 0.5);
  const haloV = t => { Object.assign(t.style, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '4px', strokeLinejoin: 'round'}); return t; };
  const sgn = (v, dp) => (v > 0 ? '+' : '') + num(v, dp);
  CK.legend('vmoff-leg', CK.cardLegend(VCARDS).concat([
    {key: 'diag', label: 'a fixed offset: the diagonal', mark: 'dash', color: 'var(--ink-2)'},
    {key: 'fit', label: 'least-squares line through the shires', mark: 'line', color: 'var(--ink-2)'}]));
  const layout = W => { const cols = W >= 720 ? PAN.length : 1, gap = 22, pw = Math.min(cols === 1 ? 380 : 400, (W - gap * (cols - 1)) / cols);
    const side = pw - 46 - 8; return {cols, gap, pw, side, ph: 44 + side + 46}; };
  CK.frame('vmoff', {label: 'Each shire’s minion-rail deviation at idle against under load, one panel per card', minW: 280, maxW: 1240,
    height: W => { const g = layout(W); return Math.ceil(PAN.length / g.cols) * g.ph; }, draw: f => {
      const g = layout(f.W), nodes = [];
      PAN.forEach((P, k) => {
        const col = k % g.cols, row = Math.floor(k / g.cols), ox = col * (g.pw + g.gap), oy = row * g.ph, cd = CK.card(P.c);
        const L = ox + 46, T = oy + 44, side = g.side, x = CK.lin(-lim, lim, L, L + side), y = CK.lin(-lim, lim, T + side, T);
        const g0 = CK.el('g', {'aria-hidden': 'true'}, f.svg), tk = x.ticks(side < 260 ? 4 : 6);
        for (const t of tk) {
          CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: T + side, class: 'grid-line'}, g0);
          CK.el('line', {x1: L, x2: L + side, y1: y(t), y2: y(t), class: 'grid-line'}, g0);
          CK.txt(g0, x(t), T + side + 16, sgn(t, 0), 'tick', 'middle');
          CK.txt(g0, L - 6, y(t) + 4, sgn(t, 0), 'tick', 'end');
        }
        CK.el('rect', {x: L, y: T, width: side, height: side, fill: 'none', class: 'ck-axis'}, g0).style.stroke = 'var(--axis)';
        CK.txt(g0, L + side / 2, T + side + 36, 'idle, mV from the 34-shire mean', 'lab', 'middle');
        haloV(CK.txt(g0, ox + 2, oy + 14, `${cd.label} · pass ${P.p.pass}`, 'lab-strong'));
        CK.txt(g0, ox + 2, oy + 31, `under load, mV from the mean · r = ${num(P.r, 2)}`, 'lab');
        const dg = CK.el('line', {x1: x(-lim), y1: y(-lim), x2: x(lim), y2: y(lim), 'stroke-width': 1.5}, g0);
        dg.style.stroke = 'var(--ink-2)'; dg.style.strokeDasharray = '5 4';
        // least-squares line of y on x, clipped to the square
        const b = P.slope, xe = Math.min(lim, lim / Math.abs(b)), fl = CK.el('line', {x1: x(-xe), y1: y(-b * xe), x2: x(xe), y2: y(b * xe), 'stroke-width': 2}, g0);
        fl.style.stroke = cd.color; fl.style.opacity = '0.7';
        for (const cell of P.cells) {
          const q = cell[0], n = cell.length, gr = CK.el('g', {}, f.svg), R = 3 + 2 * Math.sqrt(n);
          const m = CK.cardMark(gr, P.c, x(q.x), y(q.y), R);
          if (cd.mark !== 'ring') { m.style.stroke = 'var(--surface)'; m.style.strokeWidth = '1.5'; }
          CK.el('circle', {cx: x(q.x), cy: y(q.y), r: Math.max(9, R + 2), class: 'ck-hit'}, gr);
          const names = cell.map(z => `${z.s}${z.s in LAYOUT ? ' (' + LAYOUT[z.s].join(', ') + ')' : ' (' + (OFFNOTE[z.s] || 'off grid') + ')'}`);
          CK.tip(f, gr, `<b>${cd.label}</b>, pass ${P.p.pass}: shire${n > 1 ? 's' : ''} ${names.join(', ')}` +
            `<br>idle ${num(q.i, 0)} mV (${sgn(q.x, 1)} from the mean), under load ${num(q.l, 0)} mV (${sgn(q.y, 1)})` +
            `<br>deviation changed by ${sgn(q.y - q.x, 1)} mV; a fixed offset would leave it unchanged`);
          const lit = () => { if (VM.card === P.c && VM.cap !== 'sep20') vmHi(cell.map(z => z.s)); };
          gr.addEventListener('pointerenter', lit); gr.addEventListener('focus', lit);
          gr.addEventListener('pointerleave', () => vmHi(null)); gr.addEventListener('blur', () => vmHi(null));
          nodes.push(gr);
        }
      });
      CK.keynav(f, nodes);
    }});
  // the lead's conclusion and the caption, from the same maps
  const rs = PAN.map(P => P.r), sl = PAN.map(P => P.slope), sr = PAN.map(P => P.sdL / P.sdI);
  const Q4 = VCARDS.flatMap(c => VMV3[c].passes.map(p => p.q4)), rng = (a, dp) => CK.fmt.range(Math.min(...a), Math.max(...a), dp);
  const kept = Math.min(...rs) >= 0.5, steeper = Math.min(...sl) > 1.2;
  put('vmoff-lead-end', kept && steeper
    ? `on every card the shires keep their idle pattern under load (r = ${rng(rs, 2)}) but spread ${rng(sr, 1)} times as wide, so they fall on a line steeper than the diagonal, not on it.`
    : 'the shires do not sit on it.');
  $('vmoff-cap').innerHTML = `Each bubble is one or more shires with the same pair of whole-millivolt readings; its area grows with their number. ` +
    `Idle and loaded deviations correlate at ${andList(PAN.map(P => `r = ${num(P.r, 2)} on ${CK.card(P.c).label}`))}, and the loaded map's spread is ` +
    `${andList(PAN.map(P => `${num(P.sdL / P.sdI, 1)} times the idle one on ${CK.card(P.c).label} (sd ${num(P.sdL, 1)} against ${num(P.sdI, 1)} mV)`))}; ` +
    `a least-squares line through the shires is ${rng(sl, 1)} times as steep as the diagonal (whole-millivolt readings blur the idle deviations, which tends to flatten it). ` +
    `Under the load each shire's deviation changed with a standard deviation of ${rng(Q4.map(q => q.sd_dev_change_mv), 2)} mV over every pass of the check's test ` +
    `(the largest single change ${rng(Q4.map(q => q.max_abs_dev_change_mv), 1)} mV), where a fixed offset would allow about ${num(D.tel_v3.vmaps.tolerance_mv, 1)} mV; ` +
    `the whole map also sagged by ${rng(Q4.map(q => -q.common_shift_mv), 1)} mV, which measuring from each map's mean removes. ` +
    `Pointing at a bubble outlines its shires on the map above when the map shows that card's check capture. Source: V3-TEL, the DEBUG block's dumps <code>dbg/x2-idle.bin</code> and <code>x2-load.bin</code>; item TEL-Q, Q4.`;
}

TB.emit(60.5, 'init');  // start every linked view at one minute in, mid-matmul
