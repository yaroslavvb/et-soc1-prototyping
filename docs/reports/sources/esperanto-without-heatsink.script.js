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

/* ---------- section 5's numbers: D.lowclock (lowclock_calc.py, imaging_calc.py and lc_plan_calc.py, read by make_page_data.py) ---------- */
const LC = D.lowclock;
const pct = v => `${f0(100 * v)}%`;
const m595 = (p, f, u) => (f(p[0]) === f(p[2]) ? `${f(p[1])}${u || ''}` : `${f(p[1])}${u || ''} (${rng(p[0], p[2], f)})`);   // "1.8 W (1.0–2.5)"
const lcPt = (c, pol, f) => ((LC.pts[c] || {})[pol] || []).find(r => r.f === f);
const lcWin = (c, air, load, f, pol) => LC.window[`${c}|${air}|${load}|${f}|${pol}`];
(function () {
  const A2 = LC.answers.aifoundry2, P = LC.plan, X = LC.imgx;
  const th100 = c => lcPt(c, 'floor+NoC', 100).idle.th85, th600 = c => lcPt(c, 'boot', 600).idle.th85;
  const look = (c, air, f, pol) => lcWin(c, air, 'pattern', f, pol);
  V.lcA10 = `${f2(A2.ten_MHz_more[1])} W`;
  V.lcAClk = `${rng(A2.clock_only_100[0], A2.clock_only_100[2], f1)} W (median ${f1(A2.clock_only_100[1])})`;
  V.lcAIdle = `${f1(A2.idle600_60C[1])} W`;
  V.lcAClkPlan = `${rng(P.step_100_plan[0], P.step_100_plan[2], f1)} W`;
  V.lcALeft = `${f1(A2.left_100_floorNoC[1])} W (${rng(A2.left_100_floorNoC[0], A2.left_100_floorNoC[2], f1)})`;
  V.lcATh = `about ${f1(th100('aifoundry2')[1])} °C/W (${rng(Math.min(th100('aifoundry2')[0], th100('aifoundry3')[0]), Math.max(th100('aifoundry2')[2], th100('aifoundry3')[2]), f1)} on aifoundry2 and aifoundry3)`;
  const best = c => lcPt(c, 'floor+NoC', 100).idle.fan;
  const b2 = best('aifoundry2'), b3 = best('aifoundry3');
  V.lcABestFan = pct(b2) === pct(b3) ? pct(b2) : `${pct(Math.min(b2, b3))}–${pct(Math.max(b2, b3))}`;
  V.lcBlowEq = `${f0(P.equilibrium_central_pct.blower)}%`;
  V.lcBlowPon = `${f0(P.power_on_central.blower.both)}%`;
  const wf = look('aifoundry2', 'fan', 100, 'floor+NoC'), ws = look('aifoundry2', 'still', 100, 'floor+NoC');
  V.lcAWin = `a median of ${f0(wf.look['75'][1])} s with a fan, and none in ${pct(wf.none['75'])} of power-ons; in still air ` +
    `none in ${pct(ws.none['75'])} of power-ons`;
  V.lcAChk = `${f0(LC.lockin.lid_tape.checkerboard['100'][1])} s`;
  V.k5 = `≤ ${f1(th100('aifoundry2')[1])} °C/W`;
  V.k5s = `at the floor voltages with the NoC lowered (aifoundry2); 600 MHz needs ≤ ${f1(th600('aifoundry2')[1])}. A fan on the bare lid ` +
    `gives 2–7 °C/W, so ${V.lcABestFan} of draws settle; none in still air`;
  // 5.2
  const an = LC.anchors;
  V.lcAcc = `${f1(100 * an.accept_frac)}%`;
  V.lcD = `${f2(an.D_minion_W[1])} W (${rng(an.D_minion_W[0], an.D_minion_W[2], f2)})`;
  V.lcG = `${f2(an.G_minion_398mV[1])} (${rng(an.G_minion_398mV[0], an.G_minion_398mV[2], f2)})`;
  V.lcGs = `${f2(an.G_sram_660mV[1])} (${rng(an.G_sram_660mV[0], an.G_sram_660mV[2], f2)})`;
  const dc = LC.decomp['aifoundry2|60'];
  V.lcDecA2 = `of ${f1(dc.board[1])} W is ${f1(dc.fixed[1])} W that no minion clock or voltage touches (the service processor, ` +
    `PCIe, the memory shires and DRAM, the NoC, the board and the regulators' losses), ${f1(dc.leak[1])} W of minion and SRAM leakage, and ` +
    `${f1(dc.clock_tree[1])} W of clock tree, ${pct(dc.clock_tree[1] / dc.board[1])} (the minion's and the SRAM's, with their regulators' ` +
    `loss; the minion's alone is ${f2(an.D_minion_W[1])} W on the die)`;
  V.lcBclk = V.lcAClk;
  const p600 = lcPt('aifoundry2', 'boot', 600), p100 = lcPt('aifoundry2', 'boot', 100);
  V.lcBslope = p600.dP60[1] === p100.dP60[1] ? `${num(p600.dP60[1], 3)} W/°C at the board at a 60 °C die, at both clocks`
    : `${num(p600.dP60[1], 3)} W/°C at the board at 600 MHz and ${num(p100.dP60[1], 3)} at 100 MHz, at a 60 °C die`;
  V.lcBfloor = `${rng(A2.voltage_floor_more[0], A2.voltage_floor_more[2], f1)} W (median ${f1(A2.voltage_floor_more[1])})`;
  V.lcBnoc = `${rng(A2.noc_more[0], A2.noc_more[2], f1)} W (median ${f1(A2.noc_more[1])})`;
  V.lcBleft = V.lcALeft;
  V.lcBsoc = `${f0(LC.floor['aifoundry2|floor+NoC'].soc60[1])} W`;
  V.lcBdslope = `${f2(A2.dPdT_soc_100_floorNoC[1])} W/°C instead of ${f2(A2.dPdT_soc_600[1])}`;
  V.lcB10 = `${rng(A2.ten_MHz_more[0], A2.ten_MHz_more[2], f2)} W (median ${f2(A2.ten_MHz_more[1])})`;
  V.lcCT100 = `${f2(LC.ct_left_100[1])} W (${rng(LC.ct_left_100[0], LC.ct_left_100[2], f2)})`;
  const fl = k => LC.floor['aifoundry2|' + k];
  V.lcBzero = `on aifoundry2 at a 60 °C die, ${f1(fl('boot').board60[1])} W with the voltages left, ${f1(fl('floor').board60[1])} W ` +
    `at the floors and ${f1(fl('floor+NoC').board60[1])} W with the NoC lowered as well (${f1(fl('boot').board25[1])}, ` +
    `${f1(fl('floor').board25[1])} and ${f1(fl('floor+NoC').board25[1])} W at a 25 °C die, the fitted laws extrapolated 30 °C below ` +
    `the measured 54–85 °C). Taking the clock to zero removes ${pct(fl('boot').frac60[1])} of the 600 MHz idle (100 MHz removes ` +
    `${pct(A2.clock_only_100[1] / A2.idle600_60C[1])}); the floors and the NoC take that to ${pct(fl('floor+NoC').frac60[1])}`;
  const ld = A2.load16_board;
  V.lcBload = `${f1(ld['600|boot'][1])} W at the board at 600 MHz (${rng(ld['600|boot'][0], ld['600|boot'][2], f1)}), ` +
    `${f1(ld['100|boot'][1])} W at 100 MHz with the voltages left and ${f1(ld['100|floor'][1])} W at the floors`;
  // 5.3
  const th = (c, pol, f) => lcPt(c, pol, f).idle.th85[1];
  V.lcThRise = `On aifoundry2 at idle it rises from about ${f2(th('aifoundry2', 'boot', 600))} °C/W at 600 MHz to ` +
    `${f2(th('aifoundry2', 'floor', 100))} at 100 MHz at the floor voltages and ${f2(th('aifoundry2', 'floor+NoC', 100))} with the NoC ` +
    `lowered too`;
  const fb = c => pct(lcPt(c, 'floor+NoC', 100).idle.fan);
  const net = c => pct(lcPt(c, 'floor+NoC', 100).idle.fan_net), te = LC.theta_eff_fan;
  V.lcFanBest = `${V.lcABestFan} of draws on aifoundry2 and aifoundry3 and ${fb('aifoundry1-c1')} on card 1 (${fb('aifoundry1-c0')} on ` +
    `card 0, which is excluded). It needs a thermal resistance of at most ${m595(th100('aifoundry2'), f2, ' °C/W')} ` +
    `on aifoundry2, on the SoC's share of the power in a 25 °C room, against ${f2(p600.idle.th85[1])} °C/W at 600 MHz. The share mostly ` +
    `reflects the assumed 2–7 °C/W: on the transient model's own network, which gives a fan ${rng(te[0], te[2], f1)} °C/W and also counts ` +
    `the board's heating by the off-die power, ${net('aifoundry2')} of aifoundry2's draws settle`;
  V.lcBlowTh = `a θ<sub>JA</sub> of ${rng(P.blower_theta[0], P.blower_theta[2], f1)} °C/W (median ${f1(P.blower_theta[1])})`;
  V.lcBlow = `a stable idle temperature in ${f0(P.equilibrium_central_pct.blower)}% of draws (${f0(P.equilibrium_rival_pct.blower)}% under ` +
    `the rival leakage law, n = 1.8), but only ${f0(P.power_on_central.blower.both)}% of cold power-ons that stay below an 80 °C stop and ` +
    `end at or below 70 °C (with an ordinary fan ${f0(P.power_on_central.fan.both)}%, in still air ${f0(P.power_on_central.still.both)}%), ` +
    `the board's path to the air taken from the same formulas (${rng(P.blower_rba[0], P.blower_rba[2], f1)} °C/W)`;
  const env = (c, pol) => LC.envelope[`${c}|heatsink|pattern|${pol}`].hi90;
  V.lcSinkEnv = `at least 90% of draws settle at ${env('aifoundry2', 'floor')} MHz or below at the floor voltages on aifoundry2 and at ` +
    `${env('aifoundry3', 'floor')} MHz or below on aifoundry3 (${env('aifoundry1-c1', 'floor')} MHz on card 1, whose voltages must not be ` +
    `set); with the voltages left, at ${env('aifoundry3', 'boot')} MHz or below on aifoundry3 and at no settable clock on aifoundry2 ` +
    `(${pct(p100.pattern.heatsink)} at 100 MHz)`;
  V.lcSinkA2 = pct(p100.pattern.heatsink);
  const be = LC.window['aifoundry2|still|boot_end'], bf = LC.window['aifoundry2|fan|boot_end'];
  V.lcBootT = `a median ${f0(be.T[1])} °C (${rng(be.T[0], be.T[2], f0)}) in still air and ${f0(bf.T[1])} °C with a fan, and at or ` +
    `above 85 °C in ${pct(be.ge85)} and ${pct(bf.ge85)} of draws (section 3.1's figures come from the same model with its own draws)`;
  // 5.4
  const ps = X.p_shire_mW;
  V.lcPshire = `about ${f2(ps['600|boot'] / 1000)} W on an active shire's die at 600 MHz, falling with f·V² to ${f2(ps['300|boot'] / 1000)} W ` +
    `at 300 MHz with the voltages left, ${f2(ps['300|floor'] / 1000)} W at 300 MHz at the floor and ${num(ps['100|floor'] / 1000, 3)} W at ` +
    `100 MHz at the floor`;
  V.lcTau = `${rng(X.tau_window[0], X.tau_window[2], f2)} (median ${f2(X.tau_window[1])})`;
  const thr = X.threshold_mK;
  V.lcThr = `To be seen, a contrast must exceed about ${f0(thr['diff 1 s/state'][1])} mK in a difference image of two 1 s states. With ` +
    `lock-in it is the pattern's modulated amplitude, a fraction of these settled contrasts, that must exceed about ` +
    `${f1(thr['lock-in 60 s'][1])} mK after a minute, ${f2(thr['lock-in 600 s'][1])} mK after 10 minutes and ${f2(thr['lock-in 3600 s'][1])} mK ` +
    `after an hour. Each threshold is three times the noise of a pair of shire regions and includes a 4-fold allowance for drift`;
  const C = X.contrast_mK, LQ = LC.least_clock, LK = LC.lockin;
  const g3 = v => (v >= 1000 ? num(v, 0) : v >= 100 ? f0(v) : v >= 10 ? num(v, 2 - Math.floor(Math.log10(v))) : num(v, 2 - Math.floor(Math.log10(v))));
  V.lcLidCut = `a checkerboard reads ${g3(C.lid_tape.checkerboard[0])} mK on the taped lid against ${g3(C.die_coated.checkerboard[0])} on a ` +
    `coated die, and a half die ${g3(C.lid_tape['half die'][0])} against ${g3(C.die_coated['half die'][0])} mK, at 600 MHz`;
  const mins = s_ => (s_ < 120 ? `${f0(s_)} s` : `${f0(s_ / 60)} minutes`);
  V.lcLidLook = `A difference image of two 1 s states shows a checkerboard down to about ${f0(LQ.lid_tape.checkerboard['diff 1 s/state'])} MHz ` +
    `and one shire down to about ${f0(LQ.lid_tape['one shire']['diff 1 s/state'])} MHz; below that it takes lock-in. At 100 MHz at the floor a ` +
    `checkerboard takes a median ${f0(LK.lid_tape.checkerboard['100'][1])} s of lock-in and the other patterns 10 s or less; at 10 MHz a ` +
    `checkerboard would take about ${mins(LK.lid_tape.checkerboard['10'][1])} and one shire about ${mins(LK.lid_tape['one shire']['10'][1])}`;
  const all10 = k => Object.values(LK[k]).every(d => d['10'][1] <= 10.0001);
  V.lcDieLook = `${g3(C.die_coated.checkerboard[0])} mK for a checkerboard at 600 MHz; a difference image of two 1 s states shows a ` +
    `checkerboard down to about ${f0(LQ.die_coated.checkerboard['diff 1 s/state'])} MHz, and lock-in shows ` +
    (all10('die_coated') ? 'every pattern within 10 s even at 10 MHz' : `every pattern within 10 s down to ${Math.min(...Object.values(LK.die_coated).map(d => +Object.keys(d).filter(f => d[f][1] <= 10.0001).sort((a, b) => a - b)[0]))} MHz`);
  V.lcDieSi = `about ${f0(LQ.die_si.checkerboard['diff 1 s/state'])} MHz for the same checkerboard image`;
  const mp = X.map_steady_C;
  V.lcMap = `${f2(Math.min(...mp.centre))}–${f2(Math.max(...mp.centre))} °C with the sensor at its tile's centre and ` +
    `${f2(Math.min(...mp.edge))}–${f2(Math.max(...mp.edge))} °C at the tile's edge`;
  const Q = X.quantiser, q = (k, r, d) => Q[`${k}|${r}|${d}`];
  const seenR = (k, d) => `${pct(Math.min(q(k, 0.02, d).frac_seen, q(k, 0.09, d).frac_seen))}–${pct(Math.max(q(k, 0.02, d).frac_seen, q(k, 0.09, d).frac_seen))}`;
  V.lcStock = `on a steady die, a 10 s look at 600 MHz shows the block at only ${seenR('stock, 600 MHz', 'steady die')} of starting ` +
    `temperatures within a degree, and the ${f0(X.stock_lockin_100_s)} s lock-in at 100 MHz at the floor at ${seenR('stock, 100 MHz, floor', 'steady die')} ` +
    `(raw sensor noise 0.02–0.09 °C). A slow dither of the chip's power over two degrees, about ${f0(q('stock, 600 MHz', 0.02, '2 C dither').T_s / 2)} s ` +
    `a cycle, restores it at ${seenR('stock, 100 MHz, floor', '2 C dither')} of them, in about ${f0(q('stock, 600 MHz', 0.02, '2 C dither').T_s)} s at ` +
    `600 MHz and ${f0(q('stock, 100 MHz, floor', 0.02, '2 C dither').T_s)} s at 100 MHz`;
  // 5.5
  V.lcOpt1 = `about ${f0(q('stock, 600 MHz', 0.02, '2 C dither').T_s)} s at 600 MHz and ${f0(q('stock, 100 MHz, floor', 0.02, '2 C dither').T_s)} s ` +
    `at 100 MHz at the floor (a steady die shows it in only some 10 s looks)`;
  V.lcOpt1Sink = `${env('aifoundry2', 'floor')} MHz or less at the floor voltages on aifoundry2 (${env('aifoundry3', 'floor')} MHz on aifoundry3)`;
  V.lcOpt3Look = `a look of a median ${f0(wf.look['75'][1])} s before the 75 °C stop, none in ${pct(wf.none['75'])} of power-ons`;
  // 5.6
  V.lcPlanA = `${f0(P.stageA_min[0])} minutes of card time, ${f0(P.stageA_min[1])} without the optional items`;
  V.lcPlanB = `${f0(P.stageB_min)} minutes of card time`;
  V.lcPlanStep = `${rng(P.step_100_plan[0], P.step_100_plan[2], f1)} W by the plan's model and ${rng(P.step_100_envelope[0], P.step_100_envelope[2], f1)} W ` +
    `by this page's (5th–95th percentiles), of aifoundry3's ${f1(LC.decomp['aifoundry3|56'] ? LC.decomp['aifoundry3|56'].board[1] : 25.3)} W idle ` +
    `at 56 °C`;
  V.lcPlanLow = `${rng(P.low_point_56C_plan[0], P.low_point_56C_plan[2], f1)} W`;
  V.lcPlanPon = `${f0(P.power_on_central.blower.both)}% with a 3–6 m/s blower, ${f0(P.power_on_central.fan.both)}% with an ordinary ` +
    `fan, ${f0(P.power_on_central.still.both)}% in still air`;
  // 9
  const r2 = (a_, b_) => `${f1(Math.min(a_[0], b_[0]))}–${f1(Math.max(a_[2], b_[2]))}`;
  V.lcBar600 = r2(th600('aifoundry2'), th600('aifoundry3'));
  V.lcBar100 = r2(th100('aifoundry2'), th100('aifoundry3'));
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
      `(seed ${TR.seed}) ${kind('model')}. Bare: the two-node model with the input ranges of section 9. With the heatsink: the Foster chain ` +
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
    const fc = o.feasible === 'now' ? 'now' : /^no/.test(o.feasible) ? 'no' : '';
    h += `<tr><td>${o.rank}</td><td>${esc(o.option)}</td><td><span class="opt-feas ${fc}">${esc(o.feasible)}</span></td><td>${esc(o.risk)}</td>` +
      `<td>${o.cost === '—' ? '—' : `${esc(o.cost)}; ${esc(o.time)}`}</td><td>${esc(o.measures)}</td><td>${esc(o.who)}</td></tr>`;
  });
  $('otable').innerHTML = h + '</tbody>';
  CK.stackTable($('otable'));
})();

/* ---------- the static tables in the body (vendor θJA, IR windows, imaging setups): stack them on phones ---------- */
['vtable', 'wtable', 'itable', 'lcotable'].forEach(id => { if ($(id)) CK.stackTable($(id)); });

/* ---------- section 5.4: the contrast table (imaging_calc.out, read by make_page_data.py) ---------- */
(function () {
  const C = LC.imgx.contrast_mK, S = LC.imgx.sensors_mK, PT = ['checkerboard', 'one shire', '2x2 block moving', 'half die'];
  const g = v => (v == null ? '—' : v >= 1000 ? num(v, 0) : v >= 100 ? f0(v) : v >= 10 ? (Math.round(v * 10) / 10 >= 100 ? f0(v) : num(v, 1).replace(/\.0$/, ''))
    : v >= 1 ? num(v, 2).replace(/0$/, '') : num(v, 2 - Math.floor(Math.log10(v))));
  const rows = [['Delidded die, coated black', p => C.die_coated[p]], ['Delidded die, coated, under an IR-window cooler', p => C.die_win[p]],
    ['Lid, heatsink off, taped', p => C.lid_tape[p]], ['Lid, heatsink off, bare plating', p => C.lid_bare[p]],
    ['The 34 on-die sensors, heatsink on', p => [S['600'][p], S['100'][p], null]]];
  let h = '<thead><tr><th>View</th><th class="num">Checkerboard</th><th class="num">One shire</th><th class="num">2×2 block, moving</th>' +
    '<th class="num">Half die</th></tr></thead><tbody>';
  rows.forEach(([name, get]) => { h += `<tr><td>${esc(name)}</td>` + PT.map(p => `<td class="num">${get(p).map(g).join(' / ')}</td>`).join('') + '</tr>'; });
  $('lcctable').innerHTML = h + '</tbody>';
  CK.stackTable($('lcctable'));
})();

/* ---------- section 5.2–5.3: idle power and the cooling it needs, against the minion clock (D.lowclock) ---------- */
(function () {
  const STY = {
    boot: {label: 'voltages left (the clock command alone)', color: 'var(--ref)', dash: '6 4', w: 2},
    floor: {label: 'floor voltages (400 / 660 mV at 300 MHz and below)', color: 'var(--ink-2)', w: 2},
    'floor+NoC': {label: 'floor voltages, and the NoC at 200 MHz / 400 mV', color: 'var(--ink)', w: 2.5}};
  const POL = LC.policies, CLK = LC.clocks.slice().sort((a, b) => a - b), SETT = new Set(LC.settable);
  const B = D.bare;
  let card = 'aifoundry2', load = 'idle';
  // a policy's points from 10 to 600 MHz; the floor policies' 600 MHz point is the card's own (the voltages are not lowered there)
  const series = (c, pol) => CLK.map(f => lcPt(c, pol, f) || (f === 600 ? lcPt(c, 'boot', 600) : null)).filter(Boolean);
  const pw = r => (load === 'idle' ? r.P['60'] : r.P16);
  const th = r => r[load].th85;
  const LOADS = {idle: 'idle', pattern: 'random data on 16 shires'};
  CK.seg('lccard', {label: 'Card', options: LC.cards.map(c => [c, CK.card(c).label]), value: card,
    onChange: v => { card = v; fr.redraw(); table(); caption(); }});
  CK.seg('lcload', {label: 'Load', options: [['idle', 'idle'], ['pattern', 'random data on 16 shires']], value: load,
    onChange: v => { load = v; fr.redraw(); caption(); }});
  CK.legend('lcleg', POL.map(p => ({key: p, label: STY[p].label, color: STY[p].color, mark: 'line', dash: STY[p].dash}))
    .concat([{key: 'fan', label: 'bare, fan (2–7 °C/W, outlined)', color: COND.fan.color, mark: 'dash'},
             {key: 'still', label: 'bare, still air (4–12 °C/W, shaded)', color: `color-mix(in srgb, ${COND.still.color} 35%, transparent)`, mark: 'box'},
             {key: 'sink', label: 'its heatsink (board basis)', color: COND.sink.color, mark: 'dash'}]));
  const fr = CK.frame('lcchart', {label: 'Board power at a 60 °C die, and the largest thermal resistance that settles at or below 85 °C, against the minion clock',
    height: w => (w < 600 ? 560 : 600), draw(f) {
    const L = 50, R = 14, T1 = 28, gap = 64, Bm = 40, W = f.W, H = f.H;
    const h1 = Math.round((H - T1 - gap - Bm) * 0.46), B1 = T1 + h1, T2 = B1 + gap, B2 = H - Bm;
    const x = CK.log(8, 760, L, W - R), xt = f.narrow ? [10, 25, 100, 300, 600] : [10, 25, 50, 100, 200, 300, 600];
    const S = POL.map(p => ({p, pts: series(card, p)}));
    const vals = S.flatMap(s => s.pts.flatMap(r => [pw(r)[0], pw(r)[2]]));
    const lo = Math.floor(Math.min(...vals) - 1), hi = Math.ceil(Math.max(...vals) + 1);
    const y1 = CK.lin(lo, hi, B1, T1), y2 = CK.log(0.7, 15, B2, T2);
    // not settable: below 100 MHz no PLL mode exists
    const gz = CK.el('g', {}, f.svg);
    [[T1, B1], [T2, B2]].forEach(([a, b]) => { const r = CK.el('rect', {x: L, y: a, width: x(100) - L, height: b - a}, gz); r.style.fill = 'var(--grid)'; r.style.opacity = 0.55; });
    CK.axes(f, {x, y: y1, L, R, T: T1, B: H - B1, xt, xfmt: v => '', yl: `board power at a 60 °C die, W (${LOADS[load]})`});
    CK.axes(f, {x, y: y2, L, R, T: T2, B: Bm, xt, yt: [1, 1.5, 2, 3, 5, 10, 15], yfmt: v => (v % 1 ? f1(v) : f0(v)), xl: 'minion clock, MHz (log scale)',
      yl: 'θ that settles at or below 85 °C, °C/W (log scale)'});
    const g = CK.el('g', {}, f.svg);
    TXT(g, (L + x(100)) / 2, T1 + 14, f.narrow ? 'no PLL mode' : 'not settable: no PLL mode', 'tick', 'middle');
    // the bare bands and the heatsink, in the lower panel
    // still air as a fill, the fan as an outline, so that their overlap (4-7 C/W) makes no third colour
    { const r = B.range_still, e = CK.el('rect', {x: L, y: y2(Math.min(r[1], 15)), width: W - R - L, height: y2(r[0]) - y2(Math.min(r[1], 15))}, g);
      e.style.fill = COND.still.color; e.style.opacity = 0.14; }
    { const r = B.range_fan, e = CK.el('rect', {x: L + 1, y: y2(r[1]), width: W - R - L - 2, height: y2(r[0]) - y2(r[1])}, g);
      e.style.fill = 'none'; e.style.stroke = COND.fan.color; e.style.strokeWidth = 1.5; e.style.strokeDasharray = '5 3'; }
    TXT(g, W - R - 4, y2(12) + 13, 'bare, still air', 'lab', 'end');
    TXT(g, x(100) + 4, y2(3.4) + 4, 'bare, fan', 'lab', 'start');
    const ts = D.cards[card].theta_sink, tsm = Math.sqrt(ts[0] * ts[1]);
    const sl = CK.el('line', {x1: L, x2: W - R, y1: y2(tsm), y2: y2(tsm)}, g);
    sl.style.stroke = COND.sink.color; sl.style.strokeWidth = 2; sl.style.strokeDasharray = '6 4';
    TXT(g, W - R - 4, y2(tsm) + 14, f.narrow ? `heatsink, ${rng(ts[0], ts[1], f1)}` : `its heatsink, ${rng(ts[0], ts[1], f1)} °C/W`, 'tick', 'end');
    // each policy: the 5th–95th band, then the median; dashed where not settable (below 100 MHz)
    S.forEach(({p, pts}) => {
      [[y1, pw], [y2, th]].forEach(([yy, get]) => {
        const up = pts.map(r => [r.f, get(r)[2]]), dn = pts.map(r => [r.f, get(r)[0]]).reverse();
        const band = CK.el('path', {d: CK.path(up.concat(dn), x, yy) + ' Z'}, g);
        band.style.fill = STY[p].color; band.style.opacity = 0.10; band.style.stroke = 'none';
      });
    });
    S.forEach(({p, pts}) => {
      [[y1, pw], [y2, th]].forEach(([yy, get]) => {
        const sett = pts.filter(r => r.f >= 100), not = pts.filter(r => r.f <= 100);
        [[sett, STY[p].dash || null, 1], [not, '2 3', 0.75]].forEach(([seg, dash, op]) => {
          if (seg.length < 2) return;
          const e = CK.el('path', {d: CK.path(seg.map(r => [r.f, get(r)[1]]), x, yy), class: 'ln'}, g);
          e.style.stroke = STY[p].color; e.style.strokeWidth = STY[p].w; e.style.opacity = op;
          if (dash) e.style.strokeDasharray = dash;
        });
        pts.filter(r => SETT.has(r.f)).forEach(r => {
          const c = CK.el('circle', {cx: x(r.f), cy: yy(get(r)[1]), r: 3.5}, g);
          c.style.fill = STY[p].color; c.style.stroke = 'var(--page)'; c.style.strokeWidth = 1.5;
        });
      });
    });
    // direct labels in the upper panel, at 200 MHz: the top line above, the two floor lines above and below their pair
    const at = (p, f) => pw(series(card, p).find(r => r.f === f))[1];
    const lx = x(200);
    const put = (p, yy, txt) => { const e = TXT(g, lx, yy, txt, 'lab', 'middle'); e.classList.add('halo'); };
    put('boot', y1(at('boot', 200)) - 7, 'voltages left');
    put('floor', y1(at('floor', 200)) - 7, 'floor');
    put('floor+NoC', y1(at('floor+NoC', 200)) + 16, 'floor + NoC');
    // a column per clock: the tooltip gives every policy's numbers there
    const nodes = [];
    CLK.forEach((fq, i) => {
      const xl = i === 0 ? L : (x(CLK[i - 1]) + x(fq)) / 2, xr = i === CLK.length - 1 ? W - R : (x(fq) + x(CLK[i + 1])) / 2;
      const hit = CK.el('rect', {x: xl, y: T1, width: xr - xl, height: B2 - T1, class: 'ck-hit'}, g);
      CK.tip(f, hit, () => `<b>${fq} MHz</b>${SETT.has(fq) ? '' : ' (not settable)'}, ${esc(CK.card(card).label)}, ${LOADS[load]}<br>` +
        POL.map(p => { const r = series(card, p).find(q => q.f === fq); if (!r) return '';
          const s = r[load];
          return `<b>${esc(STY[p].label)}</b>: ${f1(pw(r)[1])} W (${rng(pw(r)[0], pw(r)[2], f1)}) at the board; settles at or below 85 °C ` +
            `with θ ≤ ${f2(th(r)[1])} °C/W; bare: ${pct(s.still)} of draws in still air, ${pct(s.fan)} with a fan; with its heatsink ${pct(s.heatsink)}`; })
          .filter(Boolean).join('<br>'));
      nodes.push(hit);
    });
    CK.keynav(f, nodes);
  }});
  function caption() {
    $('lccap').innerHTML = `${esc(CK.card(card).label)}, ${LOADS[load]} ${kind('model')}. Upper panel: board power at a 60 °C die ` +
      `(median, band 5th–95th percentile). Lower panel: θ<sub>85</sub>, the largest thermal resistance (on the SoC's share of the power, ` +
      `a 25 °C room) at which the die settles at or below 85 °C, against what bare cooling gives (still air shaded, a fan outlined): ` +
      `the part of a band above a line is cooling that cannot hold the card, the part below it can. Dots: settable clocks; below 100 MHz the lines are dotted, since no PLL mode exists there. The heatsink's line is its ` +
      `effective θ at the card's idle point, on board power. From <code>lowclock_calc.py</code>, ${f0(LC.draws)} draws.` +
      (card === 'aifoundry1-c1' ? ' Card 1\'s floor lines are for comparison only: its firmware has no voltage range check and writes NoC settings to flash, so its voltages must not be set.' : '');
  }
  // the table of operating points, for the chosen card
  const ROWS = [[600, 'boot'], [400, 'floor'], [300, 'floor'], [100, 'boot'], [100, 'floor'], [100, 'floor+NoC'], [10, 'floor+NoC']];
  function table() {
    const name = (r, pol) => `${r.f} MHz, ${f0(r.mV[0])} / ${f0(r.mV[1])} mV${pol === 'floor+NoC' ? `, NoC ${f0(r.noc[0])} MHz / ${f0(r.noc[1])} mV` : ''}` +
      (SETT.has(r.f) ? '' : ' (not settable)');
    let h = `<thead><tr><th>Minion clock, minion / SRAM voltage</th><th class="num">Idle board at a 60 °C die, W</th><th class="num">Rise, W/°C</th>` +
      `<th class="num">With 16 shires of random data, W</th><th class="num">Settles bare at idle: still air / fan</th><th class="num">With its heatsink: idle / 16 shires</th>` +
      `<th class="num">θ<sub>85</sub> at idle, °C/W</th></tr></thead><tbody>`;
    ROWS.forEach(([fq, pol]) => {
      const r = lcPt(card, pol, fq); if (!r) return;
      h += `<tr><td>${esc(name(r, pol))}${/forbidden/.test(r.status) ? '<small> (forbidden on this card: no range check, NoC writes go to flash)</small>' : ''}</td>` +
        `<td class="num">${m595(r.P['60'], f1)}</td><td class="num">${num(r.dP60[1], 3)}</td><td class="num">${f1(r.P16[1])}</td>` +
        `<td class="num">${pct(r.idle.still)} / ${pct(r.idle.fan)}</td><td class="num">${pct(r.idle.heatsink)} / ${pct(r.pattern.heatsink)}</td>` +
        `<td class="num">${m595(r.idle.th85, f2)}</td></tr>`;
    });
    $('lctable').innerHTML = h + '</tbody>';
    CK.stackTable($('lctable'));
    $('lctnote').innerHTML = `${esc(CK.card(card).label)} ${kind('model')}: medians, with the 5th–95th percentile in brackets; “settles” = the ` +
      `share of ${f0(LC.draws)} draws whose die settles below 85 °C. The rise is the board's per degree at 60 °C. 600 MHz is the card's own ` +
      `point; “floor” rows hold minion 400 mV (398 on the die) and SRAM 660 mV, the 10 MHz row cannot be set. Card 0, excluded, idles at ` +
      `300 MHz and 399 mV: ${f1(lcPt('aifoundry1-c0', 'floor', 300).P['60'][1])} W at 60 °C in the model, and settles with a fan in ` +
      `${pct(lcPt('aifoundry1-c0', 'floor', 300).idle.fan)} of draws.`;
  }
  table(); caption();
})();

/* ---------- section 5.3: the look after the host boots, aifoundry2 with the pattern running ---------- */
(function () {
  const ROWS = [[600, 'boot', '600 MHz, its own voltages'], [400, 'floor', '400 MHz, 438 mV'], [300, 'floor', '300 MHz, floor voltages'],
    [200, 'floor', '200 MHz, floor voltages'], [100, 'boot', '100 MHz, voltages left'], [100, 'floor', '100 MHz, floor voltages'],
    [100, 'floor+NoC', '100 MHz, floor voltages and NoC']];
  const sec = v => (v == null ? '30 min or more' : `${f0(v)} s`);
  const cell = w => { const t = w.look['75'];
    return `<td class="tcell num">${t[1] == null ? 'over 30 min' : `${f0(t[1])} s`}<small>${sec(t[0])} to ${sec(t[2])}</small>` +
      `<small>none left: ${pct(w.none['75'])}</small><small>set at boot, to 85 °C: ${w.t85[1] == null ? 'never' : `${f0(w.t85[1])} s`}</small></td>`; };
  let h = `<thead><tr><th>aifoundry2, the pattern running</th><th class="num">Still air</th><th class="num">Fan</th></tr></thead><tbody>`;
  ROWS.forEach(([fq, pol, name]) => {
    h += `<tr><td>${esc(name)}</td>${['still', 'fan'].map(a => cell(lcWin('aifoundry2', a, 'pattern', fq, pol))).join('')}</tr>`;
  });
  $('lcwtable').innerHTML = h + '</tbody>';
  CK.stackTable($('lcwtable'));
  const a3 = (a, fq, pol) => lcWin('aifoundry3', a, 'pattern', fq, pol);
  const w80 = (a, fq, pol) => lcWin('aifoundry2', a, 'pattern', fq, pol);
  $('lcwnote').innerHTML = `The look: seconds from the low point being set to a die of 75 °C, the plan's software stop, with random data on ` +
    `16 shires; median, then the 5th–95th percentile, and the share of power-ons that reach the stop before the point is set ` +
    `(at 600 MHz nothing needs setting) ${kind('model')}. The host boots for 30–90 s and the point takes 20–60 s to set, both at ` +
    `600 MHz idle ${kind('assumed')}. To the plan's 80 °C relay a fan leaves a median ` +
    `${f0(w80('fan', 100, 'floor+NoC').look['80'][1])} s at 100 MHz with the floors and the NoC lowered (none in ${pct(w80('fan', 100, 'floor+NoC').none['80'])}). ` +
    `“Set at boot”: the seconds to 85 °C had the point been set the instant the host came up, which nothing in the lab can do. ` +
    `aifoundry3 is close: at 100 MHz with the floors and the NoC lowered a fan leaves a median ${f0(a3('fan', 100, 'floor+NoC').look['75'][1])} s ` +
    `(none in ${pct(a3('fan', 100, 'floor+NoC').none['75'])}), still air none in ${pct(a3('still', 100, 'floor+NoC').none['75'])}.`;
})();

/* ---------- section 5.4: how long the camera needs to see a pattern, against the clock ---------- */
(function () {
  const VIEWS = [
    {k: 'die_coated', label: 'delidded die, coated black', color: 'var(--c1)'},
    {k: 'die_si', label: 'delidded die, bare silicon', color: 'var(--c7)', dash: '6 3'},
    {k: 'lid_tape', label: 'lid, heatsink off, taped', color: 'var(--c3)'},
    {k: 'lid_bare', label: 'lid, heatsink off, bare plating', color: 'var(--c4)', dash: '6 3'}];
  const PATS = [['checkerboard', 'checkerboard'], ['one shire', 'one shire'], ['2x2 block moving', '2×2 block, moving'], ['half die', 'half die']];
  const CLK = Object.keys(LC.lockin.die_coated.checkerboard).map(Number).sort((a, b) => a - b);
  const FLOOR = 10, YMAX = 3e6;
  let pat = 'checkerboard';
  CK.seg('lcipat', {label: 'Pattern', options: PATS, value: pat, onChange: v => { pat = v; fr.redraw(); }});
  CK.legend('lcileg', VIEWS.map(v => ({key: v.k, label: v.label, color: v.color, mark: 'line', dash: v.dash}))
    .concat([{key: 'win', label: 'taped lid only: the look a bare card leaves, still air to fan', color: 'color-mix(in srgb, var(--ink-2) 30%, transparent)', mark: 'box'}]));
  // the look after boot (aifoundry2, the pattern running, the point set 20-60 s after the boot, to the 75 C stop), floor voltages
  // below 600 MHz: still air (median) to fan (median); a median of 0 s sits on the axis
  const WIN = [[600, 'boot'], [400, 'floor'], [300, 'floor'], [200, 'floor'], [100, 'floor']]
    .map(([fq, pol]) => ({f: fq, still: lcWin('aifoundry2', 'still', 'pattern', fq, pol).look['75'][1], fan: lcWin('aifoundry2', 'fan', 'pattern', fq, pol).look['75'][1]}));
  const TICK = {10: '10 s', 60: '1 min', 600: '10 min', 3600: '1 h', 86400: '1 day', 864000: '10 days'};
  const fr = CK.frame('lcimg', {label: 'Lock-in time to see the pattern against the minion clock, per view', height: w => (w < 600 ? 360 : 390), draw(f) {
    const L = 58, R = 14, T = 26, Bm = 40, W = f.W, H = f.H;
    const x = CK.log(8, 760, L, W - R), y = CK.log(3, YMAX, H - Bm, T);
    const gz = CK.el('g', {}, f.svg);
    const z = CK.el('rect', {x: L, y: T, width: x(100) - L, height: H - Bm - T}, gz); z.style.fill = 'var(--grid)'; z.style.opacity = 0.55;
    const fl = CK.el('rect', {x: L, y: y(FLOOR), width: W - R - L, height: H - Bm - y(FLOOR)}, gz); fl.style.fill = 'var(--grid)'; fl.style.opacity = 0.45;
    CK.axes(f, {x, y, L, R, T, B: Bm, xt: f.narrow ? [10, 25, 100, 300, 600] : [10, 25, 50, 100, 200, 300, 600], yt: Object.keys(TICK).map(Number), yfmt: v => TICK[v] || '',
      xl: 'minion clock, MHz (log scale)', yl: 'lock-in time to see the pattern (log scale)'});
    const g = CK.el('g', {}, f.svg);
    TXT(g, (L + x(100)) / 2, T + 14, f.narrow ? 'no PLL mode' : 'not settable', 'tick', 'middle');
    TXT(g, W - R - 4, y(FLOOR) + 18, '10 s or less', 'tick', 'end');
    // the bare card's window: a band from still air to fan
    const cl = v => Math.max(v, 3);
    const up = WIN.map(r => [r.f, cl(Math.max(r.fan, r.still))]), dn = WIN.map(r => [r.f, cl(Math.min(r.fan, r.still))]).reverse();
    const wb = CK.el('path', {d: CK.path(up.concat(dn), x, y) + ' Z'}, g);
    wb.style.fill = 'var(--ink-2)'; wb.style.opacity = 0.3; wb.style.stroke = 'none';
    // each view's median; points at the 10 s floor are an upper bound, nudged apart so overlapping lines stay visible
    VIEWS.forEach((v, i) => {
      const d = LC.lockin[v.k][pat], off = (i - 1.5) * 4.5;
      const yy = t => (t <= FLOOR + 1e-9 ? y(FLOOR) - 3 + off : y(Math.min(t, YMAX)));
      const pts = CLK.map(fq => [x(fq), yy(d[fq][1])]);
      const e = CK.el('path', {d: pts.map((p, j) => (j ? 'L' : 'M') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' '), class: 'ln'}, g);
      e.style.stroke = v.color; e.style.strokeWidth = 2; if (v.dash) e.style.strokeDasharray = v.dash;
      pts.forEach(([px, py]) => { const c = CK.el('circle', {cx: px, cy: py, r: 3.5}, g); c.style.fill = v.color; c.style.stroke = 'var(--page)'; c.style.strokeWidth = 1.5; });
    });
    const dur = s => s == null ? 'beyond the range' : s <= FLOOR + 1e-9 ? '10 s or less' : s < 120 ? `${f0(s)} s` : s < 7200 ? `${f0(s / 60)} min` : s < 172800 ? `${f1(s / 3600)} h` : `${f0(s / 86400)} days`;
    const nodes = [];
    CLK.forEach((fq, i) => {
      const xl = i === 0 ? L : (x(CLK[i - 1]) + x(fq)) / 2, xr = i === CLK.length - 1 ? W - R : (x(fq) + x(CLK[i + 1])) / 2;
      const hit = CK.el('rect', {x: xl, y: T, width: xr - xl, height: H - Bm - T, class: 'ck-hit'}, g);
      const w = WIN.find(r => r.f === fq);
      CK.tip(f, hit, () => `<b>${fq} MHz</b>${fq < 100 ? ' (not settable)' : ''}, ${esc(PATS.find(p => p[0] === pat)[1])}: lock-in time, median (5th–95th)<br>` +
        VIEWS.map(v => { const t = LC.lockin[v.k][pat][fq]; return `${esc(v.label)}: ${dur(t[1])} (${dur(t[0])} to ${dur(t[2])})`; }).join('<br>') +
        (w ? `<br>taped lid only: a bare aifoundry2 leaves a look of ${f0(w.still)} s in still air and ${f0(w.fan)} s with a fan (median), from setting the point to the 75 °C stop` : ''));
      nodes.push(hit);
    });
    CK.keynav(f, nodes);
  }});
  $('lcicap').innerHTML = `Lock-in time for the pattern to show at three times the noise, median over the imaging model's draws, ` +
    `with fp32 random data and the voltage at its floor below 600 MHz ${kind('model')}; the best modulation frequency, at least 20 ` +
    `periods and 10 s. A point on the grey floor means 10 s or less; points there are spread apart a little so that each line shows. ` +
    `Grey band, for the taped lid only: the look a bare aifoundry2 leaves, with the pattern running, from setting the point to the ` +
    `plan's 75 °C stop (median, still air to fan; section 5.3) ${kind('model')}; a median of none sits on the axis. A view can be ` +
    `taken bare where its line lies inside or below the band. A delidded die has no lid's heat capacity, so its look would be ` +
    `shorter still. Not shown: the chip's own sensors with the heatsink on, which need no window (section 5.4).`;
})();
