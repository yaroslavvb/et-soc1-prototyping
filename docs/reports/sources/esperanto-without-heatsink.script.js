/* Feasibility of running the ET-SoC-1 without its heatsink. Every model number comes from D (page.json, written by
   docs/reports/data/2026-09-30-without-heatsink/make_page_data.py from nohs_calc.py's record, plus the trajectories it runs);
   the repository facts are in the prose with their references. Charts use the shared toolkit CK (tokens only); the cards
   come from the data (CK.cardsIn), never a fixed list. */
const $ = id => document.getElementById(id);
const num = CK.fmt.num, V = {};
const f0 = v => num(v, 0), f1 = v => num(v, 1), f2 = v => num(v, 2);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const rng = (a, b, f) => { const s = f(a), t = f(b); return s === t ? s : `${s}–${t}`; };
const kind = k => `<span class="kind">${k}</span>`;
const ref = k => `<span class="cite">[<a href="#src-${k.toLowerCase()}">${k}</a>]</span>`;
const CARDS = CK.cardsIn(D.cards);
const C600 = CARDS.filter(c => c !== 'aifoundry1-c0');          // the cards at 600 MHz
const lab = c => CK.card(c).label + (c === 'aifoundry1-c0' ? ' (300 MHz)' : '');
const minOf = (cs, f) => Math.min(...cs.map(f)), maxOf = (cs, f) => Math.max(...cs.map(f));
const LOADLAB = {idle: 'idle', '+9': '+9 W (all-ones operands)', '+23': '+23 W (random data)'};
const AIRLAB = {still: 'still air', fan: 'fan'};
const COND = {  // the three ways of cooling aifoundry2, in every chart: colour and label
  sink: {label: 'with its heatsink', color: 'var(--c7)'},
  fan: {label: 'bare, fan', color: 'var(--c4)', dash: '6 3'},
  still: {label: 'bare, still air', color: 'var(--c5)'},
};
const med = (p, f, unit) => p[1] == null ? 'never' : `${f(p[1])}${unit || ''}`;
const p595 = (p, f) => p[0] == null ? 'never' : p[2] == null ? `${f(p[0])} to never` : rng(p[0], p[2], f);

/* ---------- the numbers the prose needs ---------- */
(function () {
  const C = D.cards, B = D.bare, T = D.transients, S = D.sensor, TC = D.thermocouple;
  const find = (arr, o) => arr.find(r => Object.keys(o).every(k => r[k] === o[k]));
  const sinkLo = minOf(C600, c => C[c].theta_sink[0]), sinkHi = maxOf(C600, c => C[c].theta_sink[1]);
  const maxLo = minOf(C600, c => C[c].theta_max[0]), maxHi = maxOf(C600, c => C[c].theta_max[1]);
  V.ansSink = `${rng(sinkLo, sinkHi, f1)} °C per watt (1.47 °C/W on aifoundry2's fitted model)`;
  V.ansMax = rng(maxLo, maxHi, f1);
  const n = air => C600.reduce((a, c) => a + C[c].equilibrium[air].n, 0);
  const ok = air => C600.reduce((a, c) => a + C[c].equilibrium[air].n_ok, 0);
  const okCards = air => C600.filter(c => C[c].equilibrium[air].n_ok > 0);
  const okTxt = air => okCards(air).map(c => `${lab(c)}, at ${f0(C[c].equilibrium[air].T_eq[1])} °C`).join('; ');
  const cnt = (k, m) => `${k === 0 ? 'none' : f0(k)} of ${f0(m)}`;
  const settle = (air, what) => { const k = ok(air), m = n(air);
    return k === 0 ? `none of the ${f0(m)} ${what} settles` : `${f0(k)} of the ${f0(m)} ${what} ${k === 1 ? 'settles' : 'settle'} (${okTxt(air)})`; };
  V.ansMC = `in the model's Monte Carlo ${settle('still', 'still-air draws at 600 MHz')}, and ${settle('fan', 'fan draws')}.`;
  const a2i = find(T.cold, {card: 'aifoundry2', air: 'still', load: 'idle'});
  V.ansT90 = `${f0(a2i.t90[1])} s (${rng(a2i.t90[0], a2i.t90[2], f0)} s)`;
  // the heatsink-off card: time to 90 C at idle from a cold power-on, in still air and with a fan (model)
  const a2f = find(T.cold, {card: 'aifoundry2', air: 'fan', load: 'idle'}), c1i = find(T.cold, {card: 'aifoundry1-c1', air: 'still', load: 'idle'});
  V.offStill = `${rng(a2i.t90[0] / 60, a2i.t90[2] / 60, f0)} minutes`;
  V.offC1 = `${rng(c1i.t90[0], c1i.t90[2], f0)} s`;
  V.offFan = `${f1(a2f.t90[0] / 60)}–${f0(a2f.t90[2] / 60)} minutes` + (a2f.never90_pct ? ` (${f0(a2f.never90_pct)}% of draws never, by 900 s)` : '');
  const dv = k => S.decay.find(d => d.key === k).v;
  V.ansSpread = rng(dv('bare_die_lid')[0], dv('bare_die_lid')[2], f0);
  V.ansBump = rng(S.bump_1W['2'][0], S.bump_1W['2'][2], f1);
  V.ansTc = '±' + rng(TC.abs_err[0], TC.abs_err[2], f1);

  V.k1 = `${rng(maxLo, maxHi, f1)} °C/W`;
  V.k1s = `with its own heatsink a card runs at ${rng(sinkLo, sinkHi, f1)} °C/W; bare, ${rng(B.range_still[0], B.range_still[1], f0)} in still air and ${rng(B.range_fan[0], B.range_fan[1], f0)} with a fan`;
  V.k2 = `${f0(ok('still') + ok('fan'))} of ${f0(n('still') + n('fan'))}`;
  V.k2s = `${cnt(ok('still'), n('still'))} in still air; ${cnt(ok('fan'), n('fan'))} with a fan${ok('fan') ? ` (${okTxt('fan')})` : ''}`;
  V.k3 = `${f0(a2i.t90[1])} s`;
  V.k4 = rng(dv('bare_die_lid')[0], dv('bare_die_lid')[2], f0) + ' mm';
  V.k4s = `heatsink off: die and lid together, about the die's width; the shires are ${f1(S.shire_pitch_mm)} mm apart`;

  const th = (c, i) => `${rng(C[c].theta_sink[0], C[c].theta_sink[1], f2)}${i === 0 ? ' °C/W' : ''} on ${lab(c)}`;
  V.sinkThetas = CARDS.map(th).join(', ').replace(/, ([^,]*)$/, ' and $1');
  const hi = D.transients.hot.find(r => r.load === 'idle'), hl = D.transients.hot.find(r => r.load === '+23');
  V.hotIdle = `${rng(hi.t90[0], hi.t90[2], f0)} s (median ${f0(hi.t90[1])})`;
  V.hotLoad = `${rng(hl.t90[0], hl.t90[2], f0)} s (median ${f0(hl.t90[1])})`;
  V.rLid = rng(B.R_lid_still[0], B.R_lid_still[2], f0);
  V.lidShare = `${f0(100 * B.lid_share_still[0])}–${f0(100 * B.lid_share_still[2])}%`;
  V.thStill = `${rng(B.theta_still[0], B.theta_still[2], f1)} (median ${f1(B.theta_still[1])})`;
  V.thFan = `${rng(B.theta_fan[0], B.theta_fan[2], f1)} (median ${f1(B.theta_fan[1])})`;
  V.vtStill = rng(B.theta_still[0], B.theta_still[2], f1);
  V.vtFan = `${rng(B.theta_fan[0], B.theta_fan[2], f1)} (1–2.5 m/s)`;
  const g = (cs, k) => cs.map(c => C[c].loop_gain_bare['60'][k]);
  V.gain60 = `${rng(Math.min(...g(C600, 'still_lo')), Math.max(...g(C600, 'still_hi')), f1)} in still air and ` +
    `${rng(Math.min(...g(C600, 'fan_lo')), Math.max(...g(C600, 'fan_hi')), f1)} with a fan on the three 600 MHz cards` +
    (C['aifoundry1-c0'] ? ` (${rng(C['aifoundry1-c0'].loop_gain_bare['60'].still_lo, C['aifoundry1-c0'].loop_gain_bare['60'].still_hi, f1)} and ` +
      `${rng(C['aifoundry1-c0'].loop_gain_bare['60'].fan_lo, C['aifoundry1-c0'].loop_gain_bare['60'].fan_hi, f1)} on card 0 at 300 MHz)` : '');
  const ol = (k, i) => C600.map(c => C[c].open_loop_rise[k][i]);
  V.olStill = `${rng(Math.min(...ol('still', 0)), Math.max(...ol('still', 1)), f0)} °C`;
  V.openLoop = `${rng(Math.min(...ol('still', 0)), Math.max(...ol('still', 1)), f0)} °C in still air and ` +
    `${rng(Math.min(...ol('fan', 0)), Math.max(...ol('fan', 1)), f0)} °C with a fan`;
  const c0 = C['aifoundry1-c0'];
  V.mcText = `${settle('still', 'still-air draws for the 600 MHz cards')} at idle, and ${settle('fan', 'fan draws')} ${kind('model')}.` +
    (c0 ? ` Card 0 at 300 MHz settles in ${f0(c0.equilibrium.fan.n_ok)} of its ${f0(c0.equilibrium.fan.n)} fan draws, at ` +
      `${rng(c0.equilibrium.fan.T_eq[0], c0.equilibrium.fan.T_eq[2], f0)} °C, and in ${c0.equilibrium.still.n_ok ? f0(c0.equilibrium.still.n_ok) : 'none'} ` +
      `of its still-air draws; any kernel lifts it to 600 MHz, the clock at which, with its heatsink on, it read 115–117 °C ` +
      `on 25 September until its firmware dropped it to 300 MHz.` : '');
  const P = D.package;
  V.cJ = rng(P.C_J[0], P.C_J[2], f0);
  V.rateIdle = rng(T.rates.idle[0], T.rates.idle[2], f1);
  V.rateLoad = rng(T.rates.load[0], T.rates.load[2], f1);

  const bt = o => find(T.boot, o);
  const tb = r => r.T_boot[2] >= D.traj.cap_C ? `${f0(r.T_boot[0])} °C to past ${f0(D.traj.cap_C)} °C` : `${rng(r.T_boot[0], r.T_boot[2], f0)} °C`;
  const b2 = bt({card: 'aifoundry2', air: 'still', load: 'idle'}), b1 = bt({card: 'aifoundry1-c1', air: 'still', load: 'idle'});
  V.bootA2 = `${tb(b2)} (median ${f0(b2.T_boot[1])})`;
  V.bootC1 = `${tb(b1)} (median ${f0(b1.T_boot[1])}; past 90 °C in ${f0(b1.already90_pct)}% of draws)`;
  const w = r => `${rng(r.window[0], r.window[2], f0)} s (median ${f0(r.window[1])})`;
  const b2L = bt({card: 'aifoundry2', air: 'still', load: '+23'}), b1L = bt({card: 'aifoundry1-c1', air: 'still', load: '+23'});
  V.bootWin = `on aifoundry2 in still air, ${w(b2)} at idle and ${w(b2L)} ` +
    `under 23 W more on the die; with a fan, ${w(bt({card: 'aifoundry2', air: 'fan', load: '+23'}))} under that load; on card 1 ` +
    `in still air, under that load, ${w(b1L)} ${kind('model')}.`;
  // the first answer: the die when the host is up (idle boot), and what a random-data matmul then leaves
  V.ansBootT = `${tb(b2)} (median ${f0(b2.T_boot[1])})`;
  const med95 = r => `${f0(r.window[1])} s (${rng(r.window[0], r.window[2], f0)})`;
  V.ansBootWin = `a median ${med95(b2L)} on aifoundry2 and ${med95(b1L)} on card 1`;
  // 3.1: one load per power cycle
  const burst = r => `${f0(r.window[1])} s (median; ${f0(r.window[2])} s at the 95th percentile, none in the ${f0(r.already90_pct)}% ` +
    `of draws already past 90 °C when the host is up)`;
  V.burstA2 = burst(b2L);
  V.burstC1 = burst(b1L);
  V.k3s = `5th–95th percentile ${rng(a2i.t90[0], a2i.t90[2], f0)} s in still air; once the host is up (boot assumed), a random-data ` +
    `matmul leaves a median ${f0(b2L.window[1])} s before 90 °C`;

  V.dBareLid = rng(dv('bare_lid')[0], dv('bare_lid')[2], f0);
  V.dBare = rng(dv('bare_die_lid')[0], dv('bare_die_lid')[2], f0);
  V.bump2 = rng(S.bump_1W['2'][0], S.bump_1W['2'][2], f1);
  V.bump10 = rng(S.bump_1W['10'][0], S.bump_1W['10'][2], f1);
  V.dSink = rng(dv('sink_lid')[0], dv('sink_lid')[2], f1);
  V.dDelid = rng(dv('delid')[0], dv('delid')[2], f1);
  V.dLock = rng(dv('lockin10')[0], dv('lockin5')[2], f1);
  V.tcErr = '±' + rng(TC.abs_err[0], TC.abs_err[2], f1);
  V.dieLidIdle = rng(TC.die_minus_lid_idle[0], TC.die_minus_lid_idle[2], f1);
  V.dieLidLoad = rng(TC.die_minus_lid_load[0], TC.die_minus_lid_load[2], f1);
  V.prereq = esc(D.prereq);

  const hs = D.transients.sink_measured;
  V.tNote = `Median, then the 5th–95th percentile, in seconds; 300 draws per cell, each run until 900 s. “never”: the draw had ` +
    `not reached the temperature by then. The +9 W and +23 W loads are what an all-ones and a random-data fp32 matmul on 1,024 ` +
    `minions add on the die; card 0 is shown at idle only, since any kernel lifts it to 600 MHz. The last row starts from ` +
    `aifoundry2's idle state with its heatsink, 73 °C, and takes the heatsink away at once. With the heatsink, measured: from ` +
    `an 80 °C reading, the random-data matmul reaches 90 °C in ${rng(hs.randn_80_90_s[0], hs.randn_80_90_s[1], f0)} s and the ` +
    `all-ones one in ${rng(hs.ones_80_90_s[0], hs.ones_80_90_s[1], f0)} s ${ref('R6')}.`;
})();

document.querySelectorAll('[data-v]').forEach(e => {
  const k = e.getAttribute('data-v');
  if (V[k] == null) { console.error('esperanto-without-heatsink: no value for ' + k); return; }
  e.innerHTML = V[k];
});

const TXT = (g, x, y, s, cls, a) => CK.txt(g, x, y, s, cls || 'lab', a);
const vline = (g, x, y0, y1, style) => CK.el('line', {x1: x, x2: x, y1: y0, y2: y1, style}, g);

/* ---------- chart: how fast idle power rises with temperature, against 1/theta ---------- */
(function () {
  const C = D.cards, B = D.bare, SINK = D.package.foster_total;
  const bands = [
    {key: 'still', lo: 1 / B.range_still[1], hi: 1 / B.range_still[0], label: `bare, still air (θ ${B.range_still[0]}–${B.range_still[1]} °C/W)`},
    {key: 'fan', lo: 1 / B.range_fan[1], hi: 1 / B.range_fan[0], label: `bare, fan (θ ${B.range_fan[0]}–${B.range_fan[1]} °C/W)`},
  ];
  CK.legend('slopeleg', CARDS.map(c => ({key: c, label: lab(c), color: CK.card(c).color, mark: 'line'}))
    .concat(bands.map(b => ({key: b.key, label: b.label, color: COND[b.key].color, mark: 'box'})))
    .concat([{key: 'sink', label: `with the heatsink (θ ${f2(SINK)} °C/W, aifoundry2)`, color: COND.sink.color, mark: 'dash'}]));
  CK.frame('slope', {label: 'Rise of idle board power per degree against die temperature, with 1/θ for each kind of cooling',
    height: w => (w < 600 ? 330 : 360), draw(f) {
    const L = 50, R = 14, T = 26, Bm = 40, W = f.W, H = f.H;
    const x = CK.lin(30, 120, L, W - R), y = CK.log(0.05, 5, H - Bm, T);
    CK.axes(f, {x, y, L, R, T, B: Bm, xl: 'die temperature, °C', yl: 'idle power rise, W per °C (log scale)', yt: [0.05, 0.1, 0.2, 0.5, 1, 2, 5]});
    const g = CK.el('g', {}, f.svg);
    bands.forEach(b => {
      const r = CK.el('rect', {x: L, y: y(b.hi), width: W - R - L, height: y(b.lo) - y(b.hi)}, g);
      r.style.fill = COND[b.key].color; r.style.opacity = 0.16;
    });
    const ys = y(1 / SINK);
    const sl = CK.el('line', {x1: L, x2: W - R, y1: ys, y2: ys}, g);
    sl.style.stroke = COND.sink.color; sl.style.strokeWidth = 2; sl.style.strokeDasharray = '6 4';
    TXT(g, W - R - 4, ys - 5, 'heatsink', 'lab', 'end');
    TXT(g, W - R - 4, y(bands[0].lo) - 4, 'bare, still air', 'lab', 'end');
    TXT(g, W - R - 4, y(bands[1].hi) + 13, 'bare, fan', 'lab', 'end');
    CARDS.forEach(c => {
      const pts = C[c].slope.filter(p => p[1] >= 0.05 && p[1] <= 5), fr = C[c].fit_range;
      const inR = pts.filter(p => p[0] >= fr[0] && p[0] <= fr[1]);
      const lo = pts.filter(p => p[0] <= fr[0]), hi = pts.filter(p => p[0] >= fr[1]);
      [lo, hi].forEach(seg => { if (seg.length > 1) { const p = CK.el('path', {d: CK.path(seg, x, y), class: 'ln'}, g);
        p.style.stroke = CK.card(c).color; p.style.strokeDasharray = '4 4'; p.style.opacity = 0.85; } });
      if (inR.length > 1) { const p = CK.el('path', {d: CK.path(inR, x, y), class: 'ln'}, g); p.style.stroke = CK.card(c).color; p.style.strokeWidth = 3; }
    });
    const nodes = [], ts = [];
    for (let t = 30; t <= 120; t += 5) ts.push(t);
    const wcol = (x(120) - x(30)) / (ts.length - 1);
    ts.forEach(t => {
      const hit = CK.el('rect', {x: x(t) - wcol / 2, y: T, width: wcol, height: H - Bm - T, class: 'ck-hit'}, g);
      CK.tip(f, hit, () => `<b>${t} °C</b>: idle power rises by<br>` + CARDS.map(c => {
        const s = C[c].slope.find(p => p[0] === t)[1], fr = C[c].fit_range;
        return `${esc(lab(c))}: ${f2(s)} W/°C${t < fr[0] || t > fr[1] ? ' (extrapolated)' : ''}; loop gain ${f2(SINK * s)} with a θ of ${f2(SINK)}, ` +
          `${rng(B.range_fan[0] * s, B.range_fan[1] * s, f1)} bare with a fan, ${rng(B.range_still[0] * s, B.range_still[1] * s, f1)} bare in still air`;
      }).join('<br>'));
      nodes.push(hit);
    });
    CK.keynav(f, nodes);
  }});
})();

/* ---------- chart: the largest stable theta per card, against the bare ranges ---------- */
(function () {
  const C = D.cards, B = D.bare;
  CK.legend('thetaleg', [
    {key: 'max', label: 'largest θ with a stable idle temperature', color: 'var(--ink-2)', mark: 'box'},
    {key: 'sink', label: 'θ with its own heatsink, at its idle point', color: 'var(--ink-2)', mark: 'dot'},
    {key: 'fan', label: 'bare, fan', color: COND.fan.color, mark: 'box'},
    {key: 'still', label: 'bare, still air', color: COND.still.color, mark: 'box'}]);
  CK.frame('theta', {label: 'Largest stable thermal resistance per card against the bare package', height: () => 64 + 52 * CARDS.length, draw(f) {
    const L = 14, R = 16, T = 22, Bm = 40, W = f.W, H = f.H, row = (H - T - Bm) / CARDS.length;
    const x = CK.log(0.5, 20, L, W - R);
    CK.axes(f, {x, y: CK.lin(0, 1, H - Bm, T), L, R, T, B: Bm, xl: 'thermal resistance θ, °C/W (log scale)', yt: [], grid: false,
      xt: [0.5, 1, 2, 5, 10, 20]});
    const g = CK.el('g', {}, f.svg), nodes = [];
    [['fan', B.range_fan], ['still', B.range_still]].forEach(([k, r]) => {
      const e = CK.el('rect', {x: x(r[0]), y: T, width: x(r[1]) - x(r[0]), height: H - Bm - T}, g);
      e.style.fill = COND[k].color; e.style.opacity = 0.16;
    });
    [1, 2, 5, 10].forEach(v => vline(g, x(v), T, H - Bm, 'stroke:var(--grid);stroke-width:1'));
    TXT(g, x(B.range_still[1]) - 4, T + 12, 'bare, still air', 'lab', 'end');
    TXT(g, x(B.range_fan[0]) + 4, T + 12, 'bare, fan', 'lab', 'start');
    CARDS.forEach((c, i) => {
      const yc = T + row * i + row * 0.62, cd = CK.card(c), tm = C[c].theta_max, ts = C[c].theta_sink;
      TXT(g, L, yc - 13, lab(c), 'lab-strong').classList.add('halo');
      const bar = CK.el('rect', {x: x(tm[0]), y: yc - 6, width: Math.max(3, x(tm[1]) - x(tm[0])), height: 12, rx: 3}, g);
      bar.style.fill = cd.color;
      CK.tip(f, bar, `<b>${esc(lab(c))}</b><br>a stable idle temperature exists up to θ = ${rng(tm[0], tm[1], f2)} °C/W ` +
        `(best case: a 22 °C room, least power on the die; worst: 30 °C, most); bare the package has ${rng(B.range_fan[0], B.range_fan[1], f0)} °C/W ` +
        `with a fan and ${rng(B.range_still[0], B.range_still[1], f0)} in still air`);
      const sk = CK.el('line', {x1: x(ts[0]), x2: x(ts[1]), y1: yc, y2: yc}, g);
      sk.style.stroke = 'var(--ink)'; sk.style.strokeWidth = 2;
      const m = CK.cardMark(g, c, x(Math.sqrt(ts[0] * ts[1])), yc, 5, 'var(--ink)');
      CK.tip(f, m, `<b>${esc(lab(c))}, with its own heatsink</b><br>effective θ ${rng(ts[0], ts[1], f2)} °C/W at its idle point of ` +
        `${f0(C[c].idle_T)} °C and ${f1(C[c].idle_board_w)} W (room 22–28 °C; board power)`);
      nodes.push(m, bar);
    });
    CK.keynav(f, nodes);
  }});
})();

/* ---------- the card table ---------- */
(function () {
  const C = D.cards;
  const sAt = (c, t) => C[c].slope.find(p => p[0] === t)[1];
  const law = c => C[c].law ? `${f2(C[c].law.P_fix)} + ${f2(C[c].law.A80)}·e<sup>(T−80)/${f0(C[c].law.T_L)}</sup> W`
    : `${f2(C[c].c0_law.P62)} W at 62 °C, rising ${num(C[c].c0_law.S62, 3)} W/°C there (measured at 60–64 °C only)`;
  const eq = (c, a) => { const e = C[c].equilibrium[a]; return `${f0(e.n_ok)} of ${f0(e.n)}` + (e.n_ok ? ` (${e.T_eq[0] === e.T_eq[2] ? f0(e.T_eq[1]) : rng(e.T_eq[0], e.T_eq[2], f0)} °C)` : ''); };
  let h = `<thead><tr><th>Card</th><th>Idle point</th><th>Idle law (board)</th><th class="num">Rise at 70 / 80 °C, W/°C</th>` +
    `<th class="num">θ with its heatsink, °C/W</th><th class="num">Largest stable θ, °C/W</th><th class="num">Bare loop gain at 60 °C</th>` +
    `<th>Draws that settle bare: still air; fan</th></tr></thead><tbody>`;
  CARDS.forEach(c => {
    const g = C[c].loop_gain_bare['60'];
    h += `<tr><td>${esc(lab(c))}</td><td>${f0(C[c].idle_T)} °C, ${f1(C[c].idle_board_w)} W</td><td>${law(c)}</td>` +
      `<td class="num">${f2(sAt(c, 70))} / ${f2(sAt(c, 80))}</td><td class="num">${rng(C[c].theta_sink[0], C[c].theta_sink[1], f2)}</td>` +
      `<td class="num">${rng(C[c].theta_max[0], C[c].theta_max[1], f2)}</td>` +
      `<td class="num">${rng(g.still_lo, g.still_hi, f1)} still; ${rng(g.fan_lo, g.fan_hi, f1)} fan</td><td>${eq(c, 'still')}; ${eq(c, 'fan')}</td></tr>`;
  });
  $('ctable').innerHTML = h + `</tbody>`;
  $('ctable').insertAdjacentHTML('afterend', `<p class="small">Idle laws fitted in September on each card's cooling runs at 600 MHz ` +
    `${ref('R9')}; card 0 at 300 MHz from 12,035 guard samples (<code>card0_guard.py</code>), its law above 64 °C assumed to grow ` +
    `with a 25–36 °C scale. θ with the heatsink is the card's idle rise over a 22–28 °C room divided by its idle board power ` +
    `${kind('derived')}; the largest stable θ, the loop gains and the draws are the model's, on the SoC's share of the power ` +
    `${kind('model')}.</p>`);
  CK.stackTable($('ctable'));
  const F = D.package.foster, tot = D.package.foster_total;
  let fh = `<thead><tr><th>Stage</th><th class="num">τ, s</th><th class="num">R, °C/W</th><th class="num">C = τ/R, J/K</th><th class="num">Share of R</th></tr></thead><tbody>`;
  F.forEach((s, i) => { fh += `<tr><td>${i + 1}</td><td class="num">${num(s.tau_s)}</td><td class="num">${num(s.R, 3)}</td><td class="num">${num(s.C, s.C < 100 ? 1 : 0)}</td><td class="num">${f0(100 * s.R / tot)}%</td></tr>`; });
  fh += `<tr><td>total</td><td></td><td class="num">${num(tot, 2)}</td><td></td><td></td></tr>`;
  $('ftable').innerHTML = fh + '</tbody>';
})();

/* ---------- chart: the die's temperature after power-on, aifoundry2 ---------- */
(function () {
  const TR = D.traj, t = TR.t, CAP = TR.cap_C, KEYS = ['still', 'fan', 'sink'];
  let load = 'idle';
  const seg = CK.seg('trajctl', {label: 'Load', options: [['idle', 'idle'], ['+23', '+23 W on the die (random-data matmul)']], value: load,
    onChange: v => { load = v; fr.redraw(); cap(); }});
  CK.legend('trajleg', KEYS.map(k => ({key: k, label: COND[k].label + ' (median; band: 5th–95th percentile)', color: COND[k].color, mark: 'line', dash: COND[k].dash})));
  const fr = CK.frame('traj', {label: 'aifoundry2 die temperature after a cold power-on, with and without the heatsink', height: w => (w < 600 ? 330 : 370), draw(f) {
    const L = 46, R = 14, T = 26, Bm = 40, W = f.W, H = f.H;
    const x = CK.lin(0, t[t.length - 1], L, W - R), y = CK.lin(20, CAP, H - Bm, T);
    const bw = TR.boot_window_s;
    const gb = CK.el('g', {}, f.svg);
    const box = CK.el('rect', {x: x(bw[0]), y: T, width: x(bw[1]) - x(bw[0]), height: H - Bm - T}, gb);
    box.style.fill = 'var(--grid)'; box.style.opacity = 0.7;
    CK.axes(f, {x, y, L, R, T, B: Bm, xl: 'seconds after power-on', yl: 'die temperature, °C'});
    const g = CK.el('g', {}, f.svg), C = TR.cases[load];
    // at the foot of the band, where no line passes during the boot, so the capped lines' markers never cover it
    TXT(g, x((bw[0] + bw[1]) / 2), H - Bm - 6, f.narrow ? 'host boot' : 'host boot (assumed)', 'lab', 'middle');
    const l90 = CK.el('line', {x1: L, x2: W - R, y1: y(90), y2: y(90)}, g);
    l90.style.stroke = 'var(--ink-2)'; l90.style.strokeWidth = 1; l90.style.strokeDasharray = '3 3';
    TXT(g, W - R - 4, y(90) - 5, '90 °C: the project’s stop', 'tick', 'end');
    // the model stops a run at CAP: a series is cut at its first capped point (the 150 means "past 150", not a plateau)
    const upto = arr => { const i = arr.findIndex(v => v >= CAP - 0.05); return i < 0 ? t.length - 1 : i; };
    KEYS.forEach(k => {
      const s = C[k], n = upto(s.p5) + 1;   // the band runs until every draw has passed the cap
      const up = t.slice(0, n).map((v, i) => [v, s.p95[i]]), dn = t.slice(0, n).map((v, i) => [v, s.p5[i]]).reverse();
      const band = CK.el('path', {d: CK.path(up.concat(dn), x, y) + ' Z'}, g);
      band.style.fill = COND[k].color; band.style.opacity = 0.14; band.style.stroke = 'none';
    });
    const lines = {}, ends = {};
    KEYS.forEach(k => {
      const s = C[k], e = upto(s.p50), pts = t.slice(0, e + 1).map((v, i) => [x(v), y(s.p50[i])]);
      lines[k] = pts; ends[k] = e;
      const p = CK.el('path', {d: CK.path(t.slice(0, e + 1).map((v, i) => [v, s.p50[i]]), x, y), class: 'ln'}, g);
      p.style.stroke = COND[k].color; p.style.strokeWidth = 2.5; if (COND[k].dash) p.style.strokeDasharray = COND[k].dash;
      if (s.p50[e] >= CAP - 0.05) {   // a small upward triangle: the median has passed the cap here
        const [mx, my] = pts[e], tri = CK.el('path', {d: `M${mx - 5},${my + 7} L${mx + 5},${my + 7} L${mx},${my - 1} Z`}, g);
        tri.style.fill = COND[k].color; tri.style.stroke = 'var(--page)'; tri.style.strokeWidth = 1;
      }
    });
    // direct labels: for each line, the first candidate spot (beside the line at a few heights, or at its end) whose box
    // stays inside the plot and clear of every median and of the labels already placed; none fits, the legend names it
    const boxes = [], pad = 3;
    const hitSeg = (b, [x1, y1], [x2, y2]) => {   // does the segment cross the box (Liang-Barsky)?
      let t0 = 0, t1 = 1; const dx = x2 - x1, dy = y2 - y1;
      for (const [p, q] of [[-dx, x1 - b.x0], [dx, b.x1 - x1], [-dy, y1 - b.y0], [dy, b.y1 - y1]]) {
        if (p === 0) { if (q < 0) return false; } else { const r = q / p; if (p < 0) { if (r > t1) return false; if (r > t0) t0 = r; } else { if (r < t0) return false; if (r < t1) t1 = r; } }
      }
      return true;
    };
    const clear = b => b.x0 >= L + 2 && b.x1 <= W - R - 2 && b.y0 >= T + 16 && b.y1 <= H - Bm - 2 &&
      !boxes.some(o => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0) &&
      !KEYS.some(k => lines[k].some((pt, i) => i > 0 && hitSeg(b, lines[k][i - 1], pt)));
    const xAtPx = (k, yy) => { const P = lines[k]; for (let i = 1; i < P.length; i++) if ((P[i - 1][1] - yy) * (P[i][1] - yy) <= 0) return P[i - 1][0] + (P[i][0] - P[i - 1][0]) * (yy - P[i - 1][1]) / ((P[i][1] - P[i - 1][1]) || 1); return null; };
    const xAt = (k, temp) => xAtPx(k, y(temp));
    // the 90 C label and the host-boot label are fixed: reserve their boxes first
    g.querySelectorAll('text').forEach(e => { const bb = e.getBBox(); if (bb.width) boxes.push({x0: bb.x - pad, x1: bb.x + bb.width + pad, y0: bb.y - pad, y1: bb.y + bb.height + pad}); });
    const place = (k, text) => {
      const el = TXT(g, 0, 0, text, 'lab-strong', 'start'); el.classList.add('halo');
      const bb = el.getBBox(), w = bb.width || 7 * text.length, h = bb.height || 14;
      const P = lines[k], [ex, ey] = P[P.length - 1], cands = [];
      if (ends[k] === t.length - 1) cands.push([ex - 8 - w, ey - 8], [ex - 8 - w, ey + 16]);   // runs to the end: above or below it
      // beside the line where it crosses a few temperatures: level with the crossing (steep lines), then above-left and
      // below-right of it (shallow rising lines)
      [135, 120, 105, 75, 60, 50].forEach(temp => { const xx = xAt(k, temp); if (xx != null) cands.push([xx + 7, y(temp) + 4], [xx - 7 - w, y(temp) + 4],
        [xx - 7 - w, y(temp) - 8], [xx + 7, y(temp) + 16]); });
      // a label beside its line must have no other line between them, at the label's own height
      const nearest = (cx, cy) => { const yc = cy - h / 2 + 2, own = xAtPx(k, yc); if (own == null) return true;
        return !KEYS.some(o => { if (o === k) return false; const ox = xAtPx(o, yc); return ox != null && (cx > own ? ox > own && ox < cx : ox < own && ox > cx + w); }); };
      const at = cands.find(([cx, cy]) => clear({x0: cx - pad, x1: cx + w + pad, y0: cy - h + 2 - pad, y1: cy + 2 + pad}) && nearest(cx, cy));
      if (!at) { el.remove(); return false; }
      el.setAttribute('x', at[0]); el.setAttribute('y', at[1]);
      boxes.push({x0: at[0] - pad, x1: at[0] + w + pad, y0: at[1] - h + 2 - pad, y1: at[1] + 2 + pad});
      return true;
    };
    // the two bare lines run close under load: when the still-air line has no room of its own, one label to the right of
    // the fan line names both (the still-air line is always the left one, heating faster)
    if (place('still', COND.still.label)) place('fan', COND.fan.label);
    else if (!place('fan', 'bare, still air and fan')) place('fan', COND.fan.label);
    place('sink', COND.sink.label);
    const nodes = [], step = 10, wcol = x(step) - x(0);
    for (let s0 = 0; s0 <= t[t.length - 1]; s0 += step) {
      const i = t.indexOf(s0);
      if (i < 0) continue;
      const hit = CK.el('rect', {x: x(s0) - wcol / 2, y: T, width: wcol, height: H - Bm - T, class: 'ck-hit'}, g);
      const val = v => v >= CAP - 0.05 ? `past ${f0(CAP)}` : f0(v);
      CK.tip(f, hit, () => `<b>${s0} s after power-on</b>, ${esc(load === 'idle' ? 'idle' : '+23 W on the die')}<br>` +
        KEYS.map(k => `${esc(COND[k].label)}: ${val(C[k].p50[i])} °C (${val(C[k].p5[i])}–${val(C[k].p95[i])})`).join('<br>'));
      nodes.push(hit);
    }
    CK.keynav(f, nodes);
  }});
  function cap() {
    const C = TR.cases[load], at = (k, s) => C[k].p50[TR.t.indexOf(s)];
    $('trajcap').innerHTML = `aifoundry2 from a cold power-on at room temperature, ${f0(TR.n)} draws per line ` +
      `(seed ${TR.seed}) ${kind('model')}. Bare: the two-node model with the input ranges of section 8. With the heatsink: the Foster chain ` +
      `fitted on aifoundry2 ${ref('R5')}, driven by its fitted idle law${load === 'idle' ? '' : ` plus the fitted model's ${f1(TR.sink_load_board_w)} W of board power for the random-data matmul on 1,024 minions ${ref('R6')}`}, ` +
      `from its two fitted intercepts, 22.8–28.0 °C. The load starts at power-on, before a real host could launch anything; the grey band ` +
      `is the ${TR.boot_window_s[0]}–${TR.boot_window_s[1]} s this page assumes the host takes to boot. The model stops at ${f0(CAP)} °C: ` +
      `a median line ends with a triangle where it passes ${f0(CAP)} °C, and a band ends where every draw has. ` +
      `After ${f0(TR.t[TR.t.length - 1])} s the median die is ` + KEYS.map(k => { const v = at(k, TR.t[TR.t.length - 1]);
        return `${v >= CAP - 0.05 ? `past ${f0(CAP)} °C` : `at ${f0(v)} °C`} ${COND[k].label === 'with its heatsink' ? 'with the heatsink' : COND[k].label.replace('bare, ', 'bare in ').replace('in fan', 'with a fan')}`; })
        .join(', ').replace(/, ([^,]*)$/, ' and $1') + '.';
  }
  cap();
})();

/* ---------- table: time to 90 or 120 degrees ---------- */
(function () {
  const T = D.transients;
  let lvl = 't90';
  const rows = [];
  CARDS.forEach(c => ['still', 'fan'].forEach(a => { if (T.cold.some(r => r.card === c && r.air === a)) rows.push({c, a, hot: false}); }));
  T.hot.forEach(r => { if (!rows.some(x => x.hot && x.c === r.card)) rows.push({c: r.card, a: 'still', hot: true}); });
  const cell = r => {
    if (!r) return '<td class="tcell num">—</td>';
    const p = r[lvl], nv = lvl === 't90' && r.never90_pct ? `<small>never: ${f0(r.never90_pct)}%</small>` : '';
    return `<td class="tcell num">${med(p, f0, ' s')}<small>${p595(p, f0)}</small>${nv}</td>`;
  };
  function draw() {
    let h = `<thead><tr><th>Card and cooling</th>${['idle', '+9', '+23'].map(l => `<th class="num">${esc(LOADLAB[l])}</th>`).join('')}</tr></thead><tbody>`;
    rows.forEach(rw => {
      const src = rw.hot ? T.hot : T.cold, get = l => src.find(r => r.card === rw.c && r.air === rw.a && r.load === l);
      const name = rw.hot ? `${lab(rw.c)}, heatsink taken off at ${f0(get('idle').start_T)} °C, still air` : `${lab(rw.c)}, cold, ${AIRLAB[rw.a]}`;
      h += `<tr><td>${esc(name)}</td>${['idle', '+9', '+23'].map(l => cell(get(l))).join('')}</tr>`;
    });
    $('ttable').innerHTML = h + '</tbody>';
    CK.stackTable($('ttable'));
  }
  CK.seg('tctl', {label: 'Time to', options: [['t90', '90 °C'], ['t120', '120 °C']], value: lvl, onChange: v => { lvl = v; draw(); }});
  draw();
  // the boot table
  let b = `<thead><tr><th>Card and cooling</th><th>Load after the boot</th><th class="num">Die when the host is up, °C</th><th class="num">Seconds left to 90 °C</th><th class="num">Already past 90 °C</th></tr></thead><tbody>`;
  T.boot.forEach(r => {
    b += `<tr><td>${esc(lab(r.card))}, ${AIRLAB[r.air]}</td><td>${esc(LOADLAB[r.load])}</td><td class="num">${f0(r.T_boot[1])} (${rng(r.T_boot[0], r.T_boot[2], f0)})</td>` +
      `<td class="num">${med(r.window, f0)} (${p595(r.window, f0)})</td><td class="num">${f0(r.already90_pct)}%</td></tr>`;
  });
  $('btable').innerHTML = b + '</tbody>';
  CK.stackTable($('btable'));
  CK.sortTable($('btable'));
})();

/* ---------- chart: how far heat spreads sideways ---------- */
(function () {
  const S = D.sensor, rows = S.decay;
  CK.frame('decay', {label: 'Lateral decay lengths for each view of the chip', height: () => 60 + 46 * rows.length, draw(f) {
    const L = 14, R = 16, T = 22, Bm = 40, W = f.W, H = f.H, row = (H - T - Bm) / rows.length;
    const x = CK.log(1, 300, L, W - R);
    CK.axes(f, {x, y: CK.lin(0, 1, H - Bm, T), L, R, T, B: Bm, xl: 'decay length, mm (log scale)', yt: [], grid: false, xt: [1, 2, 5, 10, 20, 50, 100, 200]});
    const g = CK.el('g', {}, f.svg), nodes = [];
    const die = CK.el('rect', {x: x(S.die_mm[0]), y: T, width: x(S.die_mm[1]) - x(S.die_mm[0]), height: H - Bm - T}, g);
    die.style.fill = 'var(--grid)'; die.style.opacity = 0.9;
    vline(g, x(S.shire_pitch_mm), T, H - Bm, 'stroke:var(--ink-2);stroke-width:1.5;stroke-dasharray:4 3');
    vline(g, x(S.lid_mm), T, H - Bm, 'stroke:var(--axis);stroke-width:1.5;stroke-dasharray:2 3');
    // a label on a page-coloured box, so the guide lines pass under it rather than through its letters
    const boxed = (xx, yy, str, cls, anchor) => {
      const e = TXT(g, xx, yy, str, cls, anchor), bb = e.getBBox();
      if (bb.width) { const bg = CK.el('rect', {x: bb.x - 2, y: bb.y - 1, width: bb.width + 4, height: bb.height + 2, rx: 2}, g);
        bg.style.fill = 'var(--page)'; g.insertBefore(bg, e); }
      return e;
    };
    boxed(x(S.shire_pitch_mm) + 4, H - Bm - 6, `shire spacing ${f1(S.shire_pitch_mm)} mm`, 'tick');
    boxed(x(S.die_mm[1]) + 4, T + 12, 'die width', 'tick');
    boxed(x(S.lid_mm) + 4, H - Bm - 6, `lid ${f0(S.lid_mm)} mm`, 'tick');
    rows.forEach((r, i) => {
      const yc = T + row * i + row * 0.66, v = r.v;
      boxed(L, yc - 11, r.what, 'lab');
      const bar = CK.el('rect', {x: x(v[0]), y: yc - 5, width: Math.max(3, x(v[2]) - x(v[0])), height: 10, rx: 3}, g);
      bar.style.fill = 'var(--ink-2)';
      const tk = CK.el('line', {x1: x(v[1]), x2: x(v[1]), y1: yc - 8, y2: yc + 8}, g);
      tk.style.stroke = 'var(--ink)'; tk.style.strokeWidth = 2;
      CK.tip(f, bar, `<b>${esc(r.what)}</b><br>${rng(v[0], v[2], v[2] < 10 ? f1 : f0)} mm (median ${v[1] < 10 ? f1(v[1]) : f0(v[1])}); ` +
        (v[1] <= 2 * S.shire_pitch_mm ? 'near the shire spacing: single shires can be told apart' : v[1] >= S.die_mm[0] ? 'the whole die at about one temperature' : 'wider than a shire'));
      nodes.push(bar);
    });
    CK.keynav(f, nodes);
  }});
})();

/* ---------- table: the options ---------- */
(function () {
  let h = `<thead><tr><th class="num">#</th><th>Option</th><th>Feasible</th><th>Risk</th><th>Cost, time (rough estimate)</th><th>What it measures that we cannot now</th><th>Who does it</th></tr></thead><tbody>`;
  D.options.forEach(o => {
    const fc = o.feasible === 'now' ? 'now' : o.feasible === 'no' ? 'no' : '';
    h += `<tr><td>${o.rank}</td><td>${esc(o.option)}</td><td><span class="opt-feas ${fc}">${esc(o.feasible)}</span></td><td>${esc(o.risk)}</td>` +
      `<td>${o.cost === '—' ? '—' : `${esc(o.cost)}; ${esc(o.time)}`}</td><td>${esc(o.measures)}</td><td>${esc(o.who)}</td></tr>`;
  });
  $('otable').innerHTML = h + '</tbody>';
  CK.stackTable($('otable'));
})();

/* ---------- the static tables in the body (vendor θJA, IR windows, imaging setups): stack them on phones ---------- */
['vtable', 'wtable', 'itable'].forEach(id => { if ($(id)) CK.stackTable($(id)); });
