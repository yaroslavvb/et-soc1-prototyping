/* The DVFS loop and its leakage. D is dvfs.json with the three-machine block (cards) merged in by
   build_cards_data.py --merge; CK is the shared chart toolkit (docs/reports/sources/chartkit.js).
   Every number the page prints is computed here from D; the body's <span data-v="…"> fields are filled at the end. */
const num = CK.fmt.num, f0 = v => num(v, 0), f1 = v => num(v, 1), f2 = v => num(v, 2), f3 = v => num(v, 3);
const sgn = (v, dp) => (v > 0 ? '+' : '') + num(v, dp);          // true minus sign, + on positives, none on zero
const pct = v => num(100 * v, 0) + '%';
const WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
const word = n => (n >= 0 && n < 10 ? WORDS[n] : f0(n));          // counts in running prose
const srange = vs => { const a = Math.min(...vs), b = Math.max(...vs); return a === b ? sgn(a) : sgn(a) + ' to ' + sgn(b); };   // signed values
const range = (a, b, dp, sep) => (num(a, dp) === num(b, dp) ? num(a, dp) : num(a, dp) + (sep || '–') + num(b, dp));
const TH = D.thresholds, TC = TH.temp_c, TW = TH.tdp_w;
const OPS = [...D.operating_points].sort((a, b) => a.mhz - b.mhz);
const FMIN = OPS[0].mhz, FMAX = OPS[OPS.length - 1].mhz;
const V = {};                                                      // values for the body's data-v fields
const short = w => (w && w.startsWith('unattributed') ? 'unattributed' : w);
// cause of a down-step: colour and a second, shape encoding (the grey class is not separable from red by colour alone)
const CAUSE = {thermal: {c: 'var(--c7)', m: 'dot'}, 'thermal+power': {c: 'var(--bad)', m: 'box'},
  power: {c: 'var(--c4)', m: 'dot'}, unattributed: {c: 'var(--ref)', m: 'ring'}};
const UPC = 'var(--c3)';
// days as prose: ['2026-09-21', '2026-09-23'] -> '21 and 23 September'; three or more in a row -> '22–24 September'
const dayList = ds => {
  const d = [...new Set(ds)].sort().map(x => +x.slice(8, 10)), run = d.every((v, k) => !k || v === d[k - 1] + 1);
  return (d.length === 1 ? d[0] : run && d.length > 2 ? d[0] + '–' + d[d.length - 1]
    : d.slice(0, -1).join(', ') + ' and ' + d[d.length - 1]) + ' September';
};
const G = D.governor_days;                                         // the governor on aifoundry2, two days
const IS = D.idle_sessions.summary, S2 = IS.aifoundry2, S3 = IS.aifoundry3;   // the idle law, session by session

/* The idle law and its split. The law's total and slope are well determined; its split into fixed and leakage
   power is not: D.leak_split refits the split at the two ends of the leakage temperature scales that fit the
   idle readings about as well as the central fit, so every share is quoted as the range between those ends. */
const LAW = (() => {
  const busy = D.busy_randn_80c;
  const mk = (P_fix, A, T_L) => {
    const leak = T => A * Math.exp((T - 80) / T_L), law = T => P_fix + leak(T);
    return {P_fix, A, T_L, leak, law, slope: T => leak(T) / T_L, SW: busy - law(80)};   // SW: the matmul's switching watts at 80 °C
  };
  const c = mk(D.leak_model.P_fix, D.leak_model.A_at_80, D.leak_model.T_L);
  const ends = D.leak_split.ends.map(e => mk(e.P_fix, e.A_at_80, e.T_L));
  const idleSh = (f, T) => f.leak(T) / f.law(T), busySh = (f, T) => f.leak(T) / (f.law(T) + f.SW);
  const span = g => { const v = ends.map(g); return [Math.min(...v), Math.max(...v)]; };
  return {c, ends, idleSh, busySh, span, busy};
})();
const pctR = ([a, b]) => range(100 * a, 100 * b, 0) + '%';
const T3 = Math.round(D.cards.launch.aifoundry3.T);               // aifoundry3's launch temperature, whole degrees
Object.assign(V, {
  slope80: f2(LAW.c.slope(80)),
  slopeR: range(...LAW.span(f => f.slope(80)), 2),
  leakR: range(...LAW.span(f => f.A), 0),
  fixR: range(...LAW.span(f => f.P_fix), 0),
  tlR: range(...D.leak_split.T_L, 0, ' to '),
  idleShR: pctR(LAW.span(f => LAW.idleSh(f, 80))),
  busyShR: pctR(LAW.span(f => LAW.busySh(f, 80))),
  busy3R: pctR(LAW.span(f => LAW.busySh(f, T3))),
  T3: f0(T3),
  busyW: f0(LAW.busy),
});

/* The three-card check of 25-26 September (D.v3, written by analyze_dvfs.py --v3 from
   docs/reports/data/2026-09-25-claims-v3): the numbers the prose and the verdict table quote from it. */
const V3 = D.v3;
const orList = vs => { const u = [...new Set([...vs].sort((a, b) => Math.abs(a) - Math.abs(b)).map(v => sgn(v, 1).replace(/\.0$/, '')))]; return u.length <= 2 ? u.join(' or ') : srange(vs); };
const median = vs => { const s = [...vs].sort((a, b) => a - b), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
const cardLab = c => CK.card(c).label;
// A card's cooling-cycle offset from the idle law on the basis the text and the energy manual use: each cycle's mean over
// its whole-degree bins, then the mean over the cycles (V3.idle.a for IDLE-a, V3.idle.b for aifoundry2's IDLE-b). The
// per-cycle figures in D.idle_sessions weight every sample alike instead, so they lean to each cycle's cool end.
const binOff = c => { const I = (D.v3 && D.v3.idle) || {}; return (I.a && I.a[c] && I.a[c].offset_W) || (I.b && I.b[c] && I.b[c].cycle_offset_W) || null; };
(function () {
  const W3 = V3.wakeup, ids = CK.cardsIn(W3), probes = ids.flatMap(c => W3[c].probes.map(p => Object.assign({card: c}, p)));
  const lv = (p, n) => p.levels.find(l => l.level === n).paired_delta_cycles;
  V.wakeN = `${word(probes.length)} probes, ${word(W3[ids[0]].probes.length)} per card, 26 September`;
  V.wakeV3 = `in the ${V.wakeN.split(',')[0]} of the check, L1 ${orList(probes.map(p => lv(p, 'L1')))} (both ways of placing the line), ` +
    `L2 ${orList(probes.map(p => lv(p, 'L2')))}, L3 ${orList(probes.map(p => lv(p, 'L3')))} and DRAM ${srange(probes.map(p => lv(p, 'DRAM')))} cycles`;
  const k2 = V3.idle.k.aifoundry2, sh = k2.cycles.flatMap(c => c.share_range);
  V.kBusy = `${pct(Math.min(...sh))} to ${pct(Math.max(...sh))}`;
  // IDLE-k: each aifoundry2 cooling cycle fitted on its own (the check's profile over the leakage temperature scale)
  const spans = k2.cycles.map(c => c.T_span[1] - c.T_span[0]), lr = k2.cycles.map(c => c.T_L_range), kr = k2.law_resid_70_85_W;
  const fT = D.leak_model.idle_curve.map(b => b.T);
  V.fitT0 = range(Math.min(...fT), Math.max(...fT), 0);
  V.kcyc = `The three-card check tried to narrow the split with ${word(k2.cycles.length)} cooling cycles on aifoundry2 (26 September) and could not. ` +
    `Each covers only ${f0(Math.min(...spans))} to ${f0(Math.max(...spans))} °C of cooling, and fitted one by one, leakage temperature scales from ` +
    `${range(Math.min(...lr.map(r => r[0])), Math.max(...lr.map(r => r[0])), 0)} to ${range(Math.min(...lr.map(r => r[1])), Math.max(...lr.map(r => r[1])), 0)} °C ` +
    `match each cycle about as well (the law's own readings, spanning ${V.fitT0} °C, allow ${range(...D.leak_split.T_L, 0, ' to ')} °C), and put leakage at ` +
    `anywhere from ${V.kBusy} of the busy card. So leakage above Kanter's 30% of a busy card is not established. The cycles do agree with the law's ` +
    `total: ${sgn(kr.mean, 2)} W from 70 to 85 °C (99% interval ${sgn(kr.ci99[0], 2)} to ${sgn(kr.ci99[1], 2)} W).`;
  // the SP pass (TEL-P1, P3, P5) and the board refresh per poller (TEL-S), per card
  const sp = V3.sp_pass_ms, rf = V3.refresh_ms, cs = CK.cardsIn(sp);
  const q = c => f0(median(sp[c].quiet_ms)), e = c => f0(median(sp[c].e10_ms));
  // every card in the data, in the registry's order: the first named in full, the others in brackets
  const andC = a => (a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]);
  V.passQ = `${q(cs[0])} ms on ${cardLab(cs[0])}` + (cs.length > 1 ? ` (${cs.slice(1).map(c => `${q(c)} ms on ${cardLab(c)}`).join(', ')})` : '');
  V.passE = `${andC(cs.map(e))} ms`;
  V.passE2 = e('aifoundry2');
  /* the board value's refresh the stream shows under the same sampler (TEL-S, the mean over the passes), and how much
     longer the SP trace's own pass under the sampler runs than that refresh, per card: the two methods differ */
  const mh = c => rf[c].P_H.reduce((a, b) => a + b, 0) / rf[c].P_H.length;
  V.refH = `${andC(cs.filter(c => rf[c]).map(c => f0(mh(c))))} ms`;
  const dd = cs.filter(c => rf[c]).map(c => median(sp[c].e10_ms) - mh(c));
  V.methodDiff = range(Math.min(...dd), Math.max(...dd), 0);
  V.passAll = cs.map(c => `${q(c)} ms on ${cardLab(c)}`).join(', ');
  V.passAllE = cs.map(c => `${e(c)}`).join(', ') + ' ms';
  const rr = (c, k) => range(Math.min(...rf[c][k]), Math.max(...rf[c][k]), 0);
  V.refresh = `seen by a light poller (one query per 0.1 s) every ${CK.cardsIn(rf).map(c => `${rr(c, 'P_L')} ms on ${cardLab(c)}`).join(', ').replace(/, ([^,]*)$/, ' and $1')}, ` +
    `and by a 10 Hz telemetry sampler every ${CK.cardsIn(rf).map(c => rr(c, 'P_H')).join(', ').replace(/, ([^,]*)$/, ' and $1')} ms respectively (26 September, ${word(rf.aifoundry2.P_L.length)} passes per card)`;
  // the spin loop over idle (ABL-T6) and switching against active minions (ABL-T7), four runs per point and card
  const ab = V3.abl, ac = CK.cardsIn(ab), sp1 = c => ab[c].spin_over_idle;
  const real = ac.filter(c => sp1(c).lo > 0), zero = ac.filter(c => sp1(c).lo <= 0);
  V.spin = real.map(c => `${sgn(sp1(c).mean, 1)} W over idle on ${cardLab(c)} (99% interval ${sgn(sp1(c).lo, 1)} to ${sgn(sp1(c).hi, 1)} W)`).join(', ') +
    (zero.length ? `, and ${zero.map(c => `${sgn(sp1(c).mean, 1)} W on ${cardLab(c)}`).join(' and ')}, intervals that include zero` : '') +
    ` (${word(sp1(ac[0]).n)} runs each, 26 September)`;
  const mw = c => Object.entries(ab[c].switching_by_minions).map(([n, v]) => ({n: +n, mw: 1000 * v.switching_W / +n, runs: v.runs})).sort((a, b) => a.n - b.n);
  const [c2, ...others] = ac, m2 = mw(c2), ln = ac.map(c => ab[c].line);
  const and3 = xs => (xs.length > 1 ? xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1] : xs.join(''));
  V.minions = `${and3(m2.map((v, k) => `${f1(v.mw)}${k ? '' : ' mW per minion'} at ${num(v.n, 0)}${k ? '' : ' active'}`))} ` +
    `(${word(m2[0].runs)} runs per count, 26 September). On ${others.map(cardLab).join(' and ')} the cost per minion rises more with the count ` +
    `(${others.map(c => and3(mw(c).map(v => f1(v.mw))) + ' mW').join('; ')}): at 1,024 minions it is ${and3(others.map(c => f2(ab[c].ratio_1024_256.point)))} ` +
    `times the cost at 256, against ${f2(ab[c2].ratio_1024_256.point)} on ${cardLab(c2)}. On every card a straight line through the three counts has a slope of ` +
    `${range(Math.min(...ln.map(l => l.slope)) * 1000, Math.max(...ln.map(l => l.slope)) * 1000, 0)} mW per minion and an intercept ` +
    `${f1(-Math.max(...ln.map(l => l.intercept)))} to ${f1(-Math.min(...ln.map(l => l.intercept)))} W below zero, so power per minion grows a little with the count`;
})();

/* The governor the cards run (§1, §3, §9): the thermal loop's sleep in the service processor's own time, from its heartbeat
   in the development night's trace rings (D.dv2), and what the three-card check's samples say about each card's service
   processor (D.v3.sp_readouts: its own clock range, which a statistics reset does not clear, and the hottest mean; its
   system-temperature statistic, which the SP takes from the PMIC only at a reset, is not quoted as a per-sample reading). */
(function () {
  const L = D.dv2.cards[CK.cardsIn(D.dv2.cards)[0]].lines, SR = V3.sp_readouts || {};
  V.tickLoop = f2(1000 * L.heartbeat.tick_us / 1e6);
  V.rmsIdle = f2(D.leak_model.rms_idle_W);
  const c1 = SR['aifoundry1-c1'];
  const hrs = r => f1((r.t_last_ms - r.t_first_ms) / 3.6e6);
  V.a1gov = c1 ? `Its governor does not act: in all ${num(c1.samples, 0)} samples of the three-card check, spanning ${hrs(c1)} h, the service ` +
    `processor's own minimum and maximum of the clock read ${c1.sp_mhz_min === c1.sp_mhz_max ? 'both ' + c1.sp_mhz_min : c1.sp_mhz_min + ' and ' + c1.sp_mhz_max} MHz (a statistics ` +
    `reset does not clear them, so they reach back past the check, to the service processor's start), although ${num(c1.busy_cool, 0)} of those ` +
    `samples were busy (45–65 W) at a mean of 64 °C or less, where a live governor climbs, and the mean reached ${c1.die_mean_max} °C, where it ` +
    `steps down. Whether its active power management is off or its state latched early cannot be told read-only.` : '';
  const ids = CK.cardsIn(SR);
  V.noLimit = `The evidence is the telemetry itself: the hottest means the three-card check recorded, ` +
    `${ids.map(c => `${SR[c].die_mean_max} °C on ${cardLab(c)}`).join(', ')}, all ran at ` +
    `${[...new Set(ids.map(c => SR[c].mhz_at_die_mean_max))].join(', ')} MHz with no response from the card.`;
  const G3 = V3.governor, tm = (V3.idle.tmax || {}).aifoundry3 || [];
  V.a3latch = `The readings fit it: the three-card check heated aifoundry3 to a mean of ${range(Math.min(...tm), Math.max(...tm), 0)} °C in its ` +
    `cooling-cycle passes before it read any of its trace windows, and those windows held ${G3.aifoundry3.governor_lines === 0 ? 'no governor line at all' : G3.aifoundry3.governor_lines + ' governor lines'}; ` +
    `and a read-only query on 28 September found every throttle-state residency counter, which the source updates only when a loop ends, still ` +
    `at zero after more than two days up (development; noted in the night's record, <code>plan/DEV-RESULTS.md</code>; the query's output is ` +
    `<a href="https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/reports/data/2026-09-28-dvfs2-aifoundry2/raw-aifoundry3/z2.json"><code>raw-aifoundry3/z2.json</code></a> in the night's data).`;
})();

/* ---------- the seven cool-start runs and their 36 clock changes ---------- */
const RUNS = [...D.traces].sort((a, b) => a.session.localeCompare(b.session) || a.proc - b.proc);
const TR = D.transitions.map(r => {
  const run = RUNS.findIndex(q => q.session === r.session && q.proc === r.proc);
  const i = run < 0 ? -1 : RUNS[run].t.findIndex(t => Math.abs(t - r.t) < 0.006);
  if (i < 1) throw new Error('dvfs.json: a transition has no matching trace sample (' + r.session + ' ' + r.t + ' s)');
  return Object.assign({}, r, {run, i, why: short(r.why), why_prev: short(r.why_prev)});
});
const DOWN = TR.filter(r => r.dir === 'down'), UP = TR.filter(r => r.dir === 'up');
const tally = (rows, k) => rows.reduce((m, r) => ((m[r[k]] = (m[r[k]] || 0) + 1), m), {});
const byAfter = tally(DOWN, 'why'), byBefore = tally(DOWN, 'why_prev');
const nOf = (m, k) => m[k] || 0;

/* The governor's rule as the cards run it (0.20.0, §1), reduced to what one sample can show: a mean above 65 starts the
   thermal loop (a step down every 0.40 s until the mean reads 65, then the boot point), which locks the power branch
   out, so at the floor nothing else is tested; below it, the power branch steps down above the TDP and climbs below it. */
function rule(T, P, f) {
  if (T > TC) return f > FMIN ? {line: 1, act: 'down', test: 'thermal'} : {line: 2, act: 'hold', test: 'floor'};
  if (P > TW && f > FMIN) return {line: 3, act: 'down', test: 'power'};
  if (P < TW && f < FMAX) return {line: 4, act: 'up'};
  return {line: 5, act: 'hold'};
}
const CODE = [
  `if mean T &gt; ${TC} °C:`,
  `    if f &gt; ${FMIN}: thermal loop: step DOWN`,
  `    else:       hold (power branch locked out)`,
  `elif P &gt; ${TW} W and f &gt; ${FMIN}: step DOWN (power)`,
  `elif P &lt; ${TW} W and f &lt; ${FMAX}: climb to ${FMAX}`,
  `else:              hold`,
  `idle, or the loop's exit: back to ${FMIN} MHz`];
const say = r => (r.act === 'down' ? (r.test === 'thermal' ? 'the mean is above the threshold: the thermal loop steps down' : 'the power test fires: step down')
  : r.act === 'up' ? `neither test fires and power is under ${TW} W: climb`
  : r.test === 'floor' ? 'the thermal loop holds the floor, and the power branch is locked out' : 'hold');
const predicts = r => [rule(r.T_prev, r.P_prev, r.f0).act === r.dir, rule(r.T, r.P, r.f0).act === r.dir];

/* A legend built like CK.legend's, for marks it has no swatch for (triangles, shaded spans). */
function legendHTML(id, items) {
  const h = document.getElementById(id); h.className = 'ck-legend'; h.textContent = '';
  for (const it of items) {
    const s = document.createElement('span'); s.className = 'ck-li';
    const svg = CK.el('svg', {viewBox: '0 0 18 12', width: 18, height: 12, 'aria-hidden': 'true'});
    const e = it.mark === 'down' || it.mark === 'up'
      ? CK.el('polygon', {points: it.mark === 'down' ? '3,1.5 15,1.5 9,11' : '3,11 15,11 9,1.5'}, svg)
      : it.mark === 'shade' ? CK.el('rect', {x: 1, y: 0, width: 16, height: 12}, svg)
      : it.mark === 'box' ? CK.el('rect', {x: 4, y: 1, width: 10, height: 10, rx: 1.5}, svg)
      : it.mark === 'dot' || it.mark === 'ring' ? CK.el('circle', {cx: 9, cy: 6, r: it.mark === 'ring' ? 4 : 4.5}, svg)
      : CK.el('line', {x1: 1, x2: 17, y1: 6, y2: 6}, svg);
    if (it.mark === 'ring') it.hollow = true;
    if (it.mark === 'shade') { e.style.fill = it.color; e.style.opacity = it.op || 0.25; }
    else if (it.mark === 'dash' || it.mark === 'line') { e.style.stroke = it.color; e.style.strokeWidth = it.w || 2; if (it.mark === 'dash') e.style.strokeDasharray = '4 3'; }
    else if (it.hollow) { e.style.fill = 'var(--surface)'; e.style.stroke = it.color; e.style.strokeWidth = 1.8; }
    else e.style.fill = it.color;
    s.append(svg, document.createTextNode(it.label)); h.appendChild(s);
  }
}

/* ---------- V1: watch the governor decide ---------- */
const GOV = (function () {
  const st = {run: 2, i: 0, timer: null};                 // opens on run 3 (all ones), the hunting run
  const allT = RUNS.flatMap(r => r.T), allP = RUNS.flatMap(r => r.P);
  const Tlo = Math.floor(Math.min(...allT)) - 0.5, Thi = Math.ceil(Math.max(...allT)) + 0.5;
  const Plo = Math.floor(Math.min(...allP) / 10) * 10, Phi = Math.ceil(Math.max(...allP) / 10) * 10 + 5;
  const changes = k => TR.filter(r => r.run === k).map(r => r.i).sort((a, b) => a - b);
  const readEl = CK.readout('gov-read'), ruleEl = document.getElementById('gov-rule');
  ruleEl.innerHTML = CODE.map(l => `<span>${l}</span>`).join('');
  const lines = [...ruleEl.children];
  legendHTML('gov-leg', [
    {mark: 'dash', color: 'var(--bad)', label: `thresholds: ${TC} °C and ${TW} W`},
    {mark: 'shade', color: 'var(--c7)', label: `die reads above ${TC} °C`},
    {mark: 'shade', color: 'var(--bad)', label: `board above ${TW} W`},
    {mark: 'shade', color: 'var(--ref)', label: 'no launch running'},
    {mark: 'down', color: CAUSE.thermal.c, label: 'step down: thermal'},
    {mark: 'down', color: CAUSE['thermal+power'].c, label: 'thermal+power'},
    {mark: 'down', color: CAUSE.unattributed.c, hollow: true, label: 'unattributed'},
    {mark: 'up', color: UPC, label: 'step up'}]);

  function draw(f) {
    const tr = RUNS[st.run], n = tr.t.length, W = f.W, H = f.H, svg = f.svg;
    const L = 46, R = 12, B = 34, top = 38, gap = 26;
    const avail = H - top - B - 2 * gap, hc = avail * 0.24, hT = avail * 0.34, hP = avail - hc - hT;
    const c0 = top, T0 = c0 + hc + gap, P0 = T0 + hT + gap, bot = P0 + hP;
    const tEnd = k => (k + 1 < n ? tr.t[k + 1] : tr.t[n - 1] + 0.1);
    const x = CK.lin(tr.t[0], tEnd(n - 1), L, W - R);
    const yc = CK.lin(FMIN - 45, FMAX + 45, c0 + hc, c0), yT = CK.lin(Tlo, Thi, T0 + hT, T0), yP = CK.lin(Plo, Phi, bot, P0);
    Object.assign(f, {x, yc, yT, yP, c0, bot});
    const span = (test, fill, op) => {
      for (let k = 0; k < n;) {
        if (!test(k)) { k++; continue; }
        let j = k; while (j + 1 < n && test(j + 1)) j++;
        CK.el('rect', {x: x(tr.t[k]), y: c0, width: x(tEnd(j)) - x(tr.t[k]), height: bot - c0, fill, opacity: op}, svg);
        k = j + 1;
      }
    };
    span(k => tr.t[k] < 0 || tr.t[k] > tr.dur, 'var(--ref)', 0.12);
    span(k => tr.T[k] > TC, 'var(--c7)', 0.12);
    span(k => tr.P[k] > TW, 'var(--bad)', 0.12);
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    const hline = (y, lab) => { CK.el('line', {x1: L, x2: W - R, y1: y, y2: y, class: 'grid-line'}, g); if (lab != null) CK.txt(g, L - 6, y + 4, lab, 'tick', 'end'); };
    for (const o of OPS) hline(yc(o.mhz), f0(o.mhz));
    for (let v = Math.ceil(Tlo); v <= Thi; v++) hline(yT(v), (v - TC) % 2 === 0 ? f0(v) : null);
    for (let v = Math.ceil(Plo / 20) * 20 + 10; v <= Phi; v += 20) hline(yP(v), f0(v));
    CK.el('line', {x1: L, x2: W - R, y1: bot, y2: bot, class: 'ck-axis'}, g);
    for (let s = Math.ceil(tr.t[0]); s <= tEnd(n - 1); s++) CK.txt(g, x(s), bot + 16, f0(s), 'tick', 'middle');
    CK.txt(g, (L + W - R) / 2, H - 4, 'seconds since the first launch of the run', 'lab', 'middle');
    CK.txt(g, 2, 12, 'minion clock, MHz · clock changes', 'lab');
    CK.txt(g, 2, T0 - 9, 'die temperature, °C (whole degrees)', 'lab');
    CK.txt(g, 2, P0 - 9, 'board power, W', 'lab');
    const dash = y => CK.el('line', {x1: L, x2: W - R, y1: y, y2: y, stroke: 'var(--bad)', 'stroke-width': 1.3, 'stroke-dasharray': '5 4'}, svg);
    dash(yT(TC + 0.5)); dash(yP(TW));                     // the thermal test fires on readings above 65, i.e. 66 and up
    const stairs = (a, y) => a.map((v, k) => `${k ? 'L' : 'M'}${x(tr.t[k]).toFixed(1)},${y(v).toFixed(1)}L${x(tEnd(k)).toFixed(1)},${y(v).toFixed(1)}`).join('');
    const line = (a, y, c) => CK.el('path', {d: stairs(a, y), fill: 'none', stroke: c, 'stroke-width': 2, 'stroke-linejoin': 'round'}, svg);
    line(tr.mhz, yc, 'var(--c1)'); line(tr.T, yT, 'var(--c7)'); line(tr.P, yP, 'var(--c2)');
    // the cursor, moved by place()
    const cur = CK.el('g', {'pointer-events': 'none'}, svg);
    f.cur = {line: CK.el('line', {y1: c0 - 4, y2: bot, stroke: 'var(--ink)', 'stroke-width': 1.2}, cur),
      dots: [[tr.mhz, yc, 'var(--c1)'], [tr.T, yT, 'var(--c7)'], [tr.P, yP, 'var(--c2)']].map(([a, y, c]) =>
        ({a, y, e: CK.el('circle', {r: 4.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 2}, cur)}))};
    // pointer scrubbing over the plot (vertical page scroll still works on touch)
    const hit = CK.el('rect', {x: L, y: c0, width: W - L - R, height: bot - c0, class: 'ck-hit'}, svg);
    hit.style.touchAction = 'pan-y';
    const at = ev => { const b = svg.getBoundingClientRect(), tv = x.inv(ev.clientX - b.left); let k = 0; while (k + 1 < n && tEnd(k) <= tv) k++; stop(); setIdx(k); };
    hit.addEventListener('pointermove', ev => { if (ev.pointerType === 'mouse' || ev.buttons) at(ev); });
    hit.addEventListener('pointerdown', at);
    // one marker per clock change, coloured by cause; a keyboard group that moves the time slider
    const ts = TR.filter(r => r.run === st.run).sort((a, b) => a.i - b.i);
    const nodes = ts.map(r => {
      const cx = x(tr.t[r.i]), cy = 24, up = r.dir === 'up', c = up ? {c: UPC, m: 'dot'} : CAUSE[r.why];
      const p = CK.el('polygon', {points: up ? `${cx - 6},${cy + 5} ${cx + 6},${cy + 5} ${cx},${cy - 6}` : `${cx - 6},${cy - 6} ${cx + 6},${cy - 6} ${cx},${cy + 5}`,
        fill: c.m === 'ring' ? 'var(--surface)' : c.c, stroke: c.m === 'ring' ? c.c : 'var(--surface)', 'stroke-width': c.m === 'ring' ? 1.8 : 1}, svg);
      p.setAttribute('role', 'img');
      p.setAttribute('aria-label', `${f2(tr.t[r.i])} s: step ${r.dir}, ${r.f0} to ${r.f1} MHz${up ? '' : ', ' + r.why}`);
      p.style.cursor = 'pointer';
      p.addEventListener('click', () => { stop(); setIdx(r.i); });
      return p;
    });
    CK.keynav(f, nodes, {onFocus: (n_, k) => { stop(); setIdx(ts[k].i); }});
    place(f);
  }
  function place(f) {
    const tr = RUNS[st.run], i = st.i, cx = f.x(tr.t[i]);
    f.cur.line.setAttribute('x1', cx); f.cur.line.setAttribute('x2', cx);
    for (const d of f.cur.dots) { d.e.setAttribute('cx', cx); d.e.setAttribute('cy', d.y(d.a[i])); }
  }
  function panel() {
    const tr = RUNS[st.run], i = st.i, t = tr.t[i];
    const head = `<b>Run ${st.run + 1} · ${tr.values}</b> · t ${f2(t)} s · `;
    const chg = i > 0 && tr.mhz[i] !== tr.mhz[i - 1];
    let html, on = null, on2 = null;
    if (chg) {
      const dir = tr.mhz[i] > tr.mhz[i - 1] ? 'up' : 'down';
      const b = rule(tr.T[i - 1], tr.P[i - 1], tr.mhz[i - 1]), a = rule(tr.T[i], tr.P[i], tr.mhz[i - 1]);
      html = head + `clock ${tr.mhz[i - 1]}→${tr.mhz[i]} MHz (${tr.mv[i - 1]}→${tr.mv[i]} mV)` +
        `<span class="sub">before the step (${f2(tr.t[i - 1])} s): die ${f0(tr.T[i - 1])} °C, board ${f1(tr.P[i - 1])} W → ${say(b)}</span>` +
        `<span class="sub">after it: die ${f0(tr.T[i])} °C, board ${f1(tr.P[i])} W → ${say(a)}</span>`;
      // a drop from the top point straight to the boot point is not one table step: §2 reads it as the idle reset
      const jump = dir === 'down' && tr.mhz[i - 1] === FMAX && tr.mhz[i] === FMIN;
      if (b.act !== dir && a.act !== dir)
        html += jump
          ? `<span class="sub"><b>The clock dropped straight to ${FMIN} MHz, and on our 10 Hz samples neither test fires</b>: ` +
            `this one looks like the boot-point reset (§1, last bullet), not a thermal step.</span>`
          : `<span class="sub"><b>The clock stepped ${dir}, but on our 10 Hz samples the rule says ${b.act === 'hold' ? 'hold' : 'step ' + b.act}</b>: ` +
            (dir === 'down' && tr.mhz[i] === FMIN ? `a 700→600 MHz step at a reading of ${TC} °C is the thermal loop's exit to the boot point, or ` : '') +
            `the service processor read a different mean between our samples (§1).</span>`;
      on = b.line; on2 = a.line;
    } else if (t < 0) {
      html = head + `${tr.mhz[i]} MHz · die ${f0(tr.T[i])} °C · board ${f1(tr.P[i])} W` +
        `<span class="sub">before the first launch the master minion is idle, and the clock sits at the boot point</span>`;
      on = 6;
    } else {
      const r = rule(tr.T[i], tr.P[i], tr.mhz[i]);
      html = head + `${tr.mhz[i]} MHz (${tr.mv[i]} mV) · die ${f0(tr.T[i])} °C · board ${f1(tr.P[i])} W` +
        `<span class="sub">→ ${say(r)}${t > tr.dur ? ' (after the last launch; the loop stops once the master minion reports idle)' : ''}</span>`;
      on = r.line;
    }
    readEl.set(html);
    lines.forEach((e, k) => { e.classList.toggle('on', k === on); e.classList.toggle('on2', k === on2 && k !== on); });
  }
  function setIdx(i, fromRange) {
    const tr = RUNS[st.run];
    st.i = Math.max(0, Math.min(tr.t.length - 1, i));
    place(frame); panel();
    if (!fromRange) {
      rng.input.value = st.i;
      const s = f2(tr.t[st.i]) + ' s'; rng.el.querySelector('output').textContent = s; rng.input.setAttribute('aria-valuetext', s);
    }
  }
  function selectRun(k, i) {
    st.run = k;
    const tr = RUNS[k];
    rng.input.max = tr.t.length - 1;
    frame.redraw();
    setIdx(i != null ? i : changes(k)[0]);
  }
  const seg = CK.seg('gov-runs', {label: 'Run', options: RUNS.map((r, k) => [k, `${k + 1} ${r.values}`]), value: st.run,
    onChange: v => { if (v !== st.run) { stop(); selectRun(v); } }});
  const rng = CK.range('gov-scrub', {label: 'Time', min: 0, max: RUNS[st.run].t.length - 1, step: 1, value: 0,
    fmt: v => f2(RUNS[st.run].t[v] ?? 0) + ' s', onInput: v => { stop(); setIdx(v, true); }});
  rng.el.classList.add('wide-range');
  rng.input.addEventListener('keydown', ev => {                 // Page Up / Page Down: previous / next clock change
    if (ev.key !== 'PageUp' && ev.key !== 'PageDown') return;
    ev.preventDefault(); stop();
    const c = changes(st.run), j = ev.key === 'PageDown' ? c.find(k => k > st.i) : [...c].reverse().find(k => k < st.i);
    if (j != null) setIdx(j);
  });
  const play = document.getElementById('gov-play');
  play.setAttribute('aria-pressed', 'false');
  play.textContent = CK.reduced ? 'Play, change by change' : 'Play';
  function stop() {
    if (!st.timer) return;
    clearInterval(st.timer); st.timer = null;
    play.textContent = CK.reduced ? 'Play, change by change' : 'Play'; play.setAttribute('aria-pressed', 'false');
    readEl.setAttribute('aria-live', 'polite');
  }
  function start() {
    const tr = RUNS[st.run];
    if (st.i >= tr.t.length - 1) setIdx(0);
    play.textContent = 'Pause'; play.setAttribute('aria-pressed', 'true');
    readEl.setAttribute('aria-live', 'off');                  // no announcement every 100 ms
    st.timer = setInterval(() => {                              // real time (one 10 Hz sample per 100 ms), or one change per 1.2 s
      const tr = RUNS[st.run];
      let j = CK.reduced ? changes(st.run).find(k => k > st.i) : st.i + 1;
      if (j == null || j >= tr.t.length) j = tr.t.length - 1;
      setIdx(j);
      if (j >= tr.t.length - 1) stop();
    }, CK.reduced ? 1200 : 100);
  }
  play.addEventListener('click', () => (st.timer ? stop() : start()));
  const tr0 = RUNS[st.run];
  st.i = changes(st.run).find(k => tr0.mhz[k] < tr0.mhz[k - 1]);   // opens on the run's first down-step
  const frame = CK.frame('cycle', {height: W => (W < 600 ? 380 : 360), minW: 300, maxW: 900,
    label: 'Minion clock, die temperature and board power of the selected run, one 10 Hz sample at a time', draw});
  setIdx(st.i);
  // the summary under the chart: what the rule predicts on the samples either side of each change
  const pr = TR.map(predicts), nB = pr.filter(p => p[0]).length, nA = pr.filter(p => p[1]).length, nN = pr.filter(p => !p[0] && !p[1]).length;
  const nJ = TR.filter((r, k) => !pr[k][0] && !pr[k][1] && r.dir === 'down' && r.f0 === FMAX && r.f1 === FMIN).length;   // drops to the boot point
  document.getElementById('gov-sum').innerHTML =
    `Across the seven runs: ${TR.length} clock changes, ${UP.length} up and ${DOWN.length} down. The rule, applied to the last ` +
    `sample before each change, predicts ${nB} of them; applied to the first sample after it, ${nA}. Neither sample predicts ${nN}: ` +
    (nJ ? `${word(nJ)} ${nJ > 1 ? 'are drops' : 'is a drop'} straight to the boot point, and for the rest ` : '') +
    `the thermal loop exited to the boot point, or the service processor read its sensors between our 10 Hz samples, on its own pass ` +
    `(about ${V.passE2} ms while we sample) or inside its loop (every ${V.tickLoop} s, §1).`;
  return {select(r) { stop(); if (r.run !== st.run) { st.run = r.run; seg.set(r.run); selectRun(r.run, r.i); } else setIdx(r.i); }};
})();

/* ---------- the governor's rule as a plane: die temperature x board power, shaded by the branch that fires,
   with a card seg (top 12, item 4(b)) that moves the TDP line from aifoundry2's 65 W to aifoundry3's 0 W, where the
   step-up region has no height left to draw. aifoundry3 pairs no die reading with its throttle-down log, so its
   events show as a board-power rug instead of points on the plane. The cards and their settings are the three-card
   check's readouts (D.v3.governor, 26 September) when present, else the 22 September readouts (D.cards.config); a card
   with neither clock steps nor a governor log (aifoundry1's card 1) shows its plane and says why it has no points. */
(function () {
  let mode = 'after';
  const G3 = D.v3 && D.v3.governor, SP3 = D.cards.sptrace_aifoundry3;
  const CFG = G3 ? Object.fromEntries(Object.keys(G3).map(c => [c, G3[c].config[0]])) : D.cards.config;
  const cardIds = CK.cardsIn(CFG);
  let cardId = cardIds[0];
  CK.seg('attrib-mode', {label: 'Read the sample', options: [['after', 'just after the step'], ['before', 'just before it']],
    value: mode, onChange: v => { mode = v; frame.redraw(); }});
  CK.cardSeg('attrib-card', {cards: cardIds, bus: 'dvfs-attrib-card', value: cardId, onChange: v => { cardId = v; frame.redraw(); }});
  const tip = r => `<b>Run ${r.run + 1} · ${r.values}</b>, ${r.f0}→${r.f1} MHz at ${f2(r.t)} s<br>` +
    `just before: die ${f0(r.T_prev)} °C, board ${f1(r.P_prev)} W${r.why_prev ? ' → ' + r.why_prev : ' → neither test fires'}<br>` +
    `just after: die ${f0(r.T)} °C, board ${f1(r.P)} W${r.why ? ' → ' + r.why : ' → neither test fires'}<br>Selecting it replays the step in the chart above`;
  const cap = document.getElementById('attrib-cap');
  function draw(f) {
    const W = f.W, H = f.H, L = 44, R = 12, T = 26, B = 40;
    const x = CK.lin(62.5, 68.5, L, W - R), y = CK.lin(25, 95, H - B, T);
    const cfg = CFG[cardId], cTC = cfg.temp_threshold_c, cTW = cfg.tdp_w;
    const xTC = x(cTC + 0.5), yTWraw = y(cTW), yTW = Math.min(Math.max(yTWraw, T), H - B), offChart = yTWraw > H - B + 0.5;
    // the three branches of rule(): thermal-down (right of xTC), power-down (below xTC, above the TDP line), step-up (below both)
    CK.el('rect', {x: xTC, y: T, width: (W - R) - xTC, height: (H - B) - T, fill: 'var(--c7)', opacity: 0.12}, f.svg);
    CK.el('rect', {x: L, y: T, width: xTC - L, height: yTW - T, fill: 'var(--c4)', opacity: 0.14}, f.svg);
    if (!offChart) CK.el('rect', {x: L, y: yTW, width: xTC - L, height: (H - B) - yTW, fill: UPC, opacity: 0.12}, f.svg);
    CK.axes(f, {x, y, L, R, T, B, xt: [63, 64, 65, 66, 67, 68], yt: [30, 50, 70, 90],
      xl: 'die temperature on that sample, °C (whole degrees)', yl: 'board power on that sample, W'});
    const dash = a => CK.el('line', Object.assign({stroke: 'var(--bad)', 'stroke-width': 1.3, 'stroke-dasharray': '5 4'}, a), f.svg);
    dash({x1: xTC, x2: xTC, y1: T, y2: H - B});
    CK.txt(f.svg, xTC + 5, T + 12, 'thermal test fires →', 'lab');
    if (offChart) CK.txt(f.svg, L + 4, H - B - 6, `power test fires above ${cTW} W: always true here`, 'lab');
    else { dash({x1: L, x2: W - R, y1: yTW, y2: yTW}); CK.txt(f.svg, L + 4, yTW - 5, `power test fires above ${cTW} W`, 'lab'); }
    const nodes = [], legItems = [];
    if (cardId === 'aifoundry2') {
      const pts = TR.map(r => mode === 'after' ? {r, T: r.T, P: r.P, why: r.why} : {r, T: r.T_prev, P: r.P_prev, why: r.why_prev});
      const groups = {};
      pts.forEach(p => (groups[p.T + '|' + Math.round(p.P / 2)] = groups[p.T + '|' + Math.round(p.P / 2)] || []).push(p));
      Object.values(groups).forEach(g => g.forEach((p, k) => (p.dx = (k - (g.length - 1) / 2) * 0.22)));
      pts.sort((a, b) => a.T + a.dx - (b.T + b.dx) || a.P - b.P);
      pts.forEach(p => {
        const cx = x(p.T + p.dx), cy = y(p.P);
        const node = p.r.dir === 'up'
          ? CK.el('polygon', {points: `${cx},${cy - 6} ${cx + 6},${cy + 5} ${cx - 6},${cy + 5}`, fill: UPC, stroke: 'var(--surface)', 'stroke-width': 1.3}, f.svg)
          : CAUSE[p.why].m === 'box' ? CK.el('rect', {x: cx - 5.5, y: cy - 5.5, width: 11, height: 11, rx: 1.5, fill: CAUSE[p.why].c, stroke: 'var(--surface)', 'stroke-width': 1.5}, f.svg)
          : CAUSE[p.why].m === 'ring' ? CK.el('circle', {cx, cy, r: 5.5, fill: 'var(--surface)', stroke: CAUSE[p.why].c, 'stroke-width': 2.2}, f.svg)
          : CK.el('circle', {cx, cy, r: 6, fill: CAUSE[p.why].c, stroke: 'var(--surface)', 'stroke-width': 1.5}, f.svg);
        CK.tip(f, node, tip(p.r));
        node.style.cursor = 'pointer';
        node.addEventListener('click', () => GOV.select(p.r));
        nodes.push(node);
      });
      CK.keynav(f, nodes, {onEnter: (n_, k) => GOV.select(pts[k].r)});
      const cnt = tally(pts.filter(p => p.r.dir === 'down'), 'why'), nUp = pts.filter(p => p.r.dir === 'up').length;
      Object.keys(CAUSE).filter(k => cnt[k]).forEach(k => legItems.push({mark: CAUSE[k].m, color: CAUSE[k].c, label: `${k} down (${cnt[k]})`}));
      if (nUp) legItems.push({mark: 'up', color: UPC, label: `step up (${nUp})`});
      if (cap) cap.innerHTML = 'Points within one whole degree are spread sideways so each is visible. Select a point ' +
        '(click, tap or Enter) to replay its step in the chart above.';
    } else if (cardId !== 'aifoundry3') {
      // a card whose clock never left 600 MHz in the check and whose trace windows held no governor line
      const lab = CK.card(cardId).label, h = (D.v3 && D.v3.clock_mhz[cardId]) || {}, n = Object.values(h).reduce((a, b) => a + b, 0);
      CK.txt(f.svg, L + 6, H - B - 10, 'no step to place', 'lab');
      const sr = D.v3 && D.v3.sp_readouts && D.v3.sp_readouts[cardId];
      if (cap) cap.innerHTML = `${lab} reads the same settings as aifoundry2 (${cTW} W, ${cTC} °C), so the plane is aifoundry2's. ` +
        `Its clock read ${Object.keys(h).join(', ')} MHz in all ${num(n, 0)} samples of the three-card check` +
        (sr && sr.busy_cool ? `, ${num(sr.busy_cool, 0)} of them busy at a mean of 64 °C or less and under ${cTW} W, in the plane's step-up corner` : '') +
        `, and its trace windows held no governor line: its governor does not act (<a href="#method-and-what-is-not-established">§9</a>), so it has no step to place.`;
    } else {
      const pw = (SP3 && SP3.pwr_mw) || [], rx = W - R - 9;
      pw.forEach(mw => {
        const w = mw / 1000, cy = y(Math.min(95, Math.max(25, w)));
        const node = CK.el('rect', {x: rx - 5, y: cy - 2, width: 10, height: 4, rx: 1, fill: 'var(--ref)'}, f.svg);
        CK.tip(f, node, `<b>${cardId} down-event</b>: board ${f1(w)} W<br>die temperature not recorded by this trace`);
        nodes.push(node);
      });
      CK.txt(f.svg, rx, T + 12, 'board W ↓', 'lab', 'middle');
      CK.keynav(f, nodes);
      legItems.push({mark: 'dash', color: 'var(--ref)', label: `${cardId} down-events, board power only (${pw.length})`});
      if (cap) cap.innerHTML = `${CK.card(cardId).label}'s TDP reads 0 W (a boot service sets it), so the power test is always true and every launch logs a down-event ` +
        `(${SP3 ? f0(SP3.down_events) : '?'} in the trace window of 22 September; the check's windows of 26 September held no governor line); its die temperature is not in that log, so the ` +
        `${word(pw.length)} readings we have sit in a rug at the right, by board power alone.`;
    }
    legendHTML('attrib-leg', legItems);
  }
  const frame = CK.frame('attrib', {height: W => (W < 600 ? 300 : 320), minW: 280, maxW: 640,
    label: "The governor's rule as a die-temperature by board-power plane, shaded by the branch that fires, with the selected card's own events", draw});
})();

/* ---------- the down-steps as a table ---------- */
document.getElementById('trans').innerHTML = '<thead><tr><th>Run, time</th><th class="num">MHz</th><th class="num">mV</th>' +
  '<th class="num">die °C</th><th class="num">board W</th><th>Cause</th></tr></thead><tbody>' +
  DOWN.map(r => `<tr><td>${r.run + 1} · ${r.values}, ${f2(r.t)} s</td><td class="num">${r.f0}→${r.f1}</td>` +
    `<td class="num">${r.mv0}→${r.mv1}</td><td class="num">${f0(r.T)}</td><td class="num">${f1(r.P)}</td><td>${r.why}` +
    (r.why_prev !== r.why ? ` <span class="small">(sample before: ${r.why_prev})</span>` : '') + '</td></tr>').join('') + '</tbody>';

/* ---------- the verdict table ---------- */
(function () {
  const s = D.transition_summary, w = D.wakeup, ic = D.idle_check, m = D.leak_model;
  const vAll = G.voltage_tracks_strictly === G.changes ? `, and in all ${f0(G.changes)} clock changes of eight sessions on ${dayList(G.days)}` : '';
  const R = [['Any mature design runs a DVFS loop that steps voltage and frequency to stay inside a power and thermal envelope.', 'confirmed on aifoundry2',
    `On aifoundry2, three operating points, ${OPS.map(o => o.mhz + ' MHz at ' + f2(o.volts) + ' V').join(', ')}. Voltage moved with frequency in all ${TR.length} transitions of the cool-start runs${vAll}. On aifoundry3 a zero power limit, set at every boot, holds the clock at the first point (<a href="#the-same-firmware-on-three-cards">§3</a>).`],
  ['The chip counts bus bits and execution-unit activity factors and computes its own power estimate on millisecond timescales.', 'not on this chip',
    'The loop reads the PMIC’s measured board power over I2C and the mean of the on-die PVT sensors. There is no activity counter anywhere in it, in the build the cards run (0.20.0), the older one or the September 2024 rewrite.'],
  ['Thermal sensors are part of the same loop, because leakage depends on temperature.', 'confirmed, and thermal has priority',
    `The temperature test comes first: a mean above ${TC} °C starts a loop that locks the power tests out (<a href="#the-loop-as-built">§1</a>). It reads the mean of 34 sensors, never the hottest one, and on a development night the step followed that mean (<a href="#what-triggers-a-step-down-and-does-placement-delay-it">§8</a>, not yet validated). On aifoundry2, ${nOf(byAfter, 'thermal')} of the ${DOWN.length} down-steps in the seven cool-start runs were thermal only on the sample after the step (${nOf(byBefore, 'thermal')} on the sample before), and none was the power test alone.`],
  ['Cache data arrays sit behind leakage-suppression transistors; a lookup un-suppresses only the part it needs, at a small wake-up latency.', 'tied off in the open RTL',
    `The open RTL (Erbium, a later configuration of the same core, not the ET-SoC-1 chip) has per-minion sleep and isolation ports, tied off; no firmware line drives any power gating; and after 27 ms of idle no cache level shows a wake-up, on any of three cards (${V.wakeN}). Paired shifts on 22 September: ${w.levels.map(l => l.level + ' ' + sgn(l.paired_delta_cycles)).join(', ')} cycles; ${V.wakeV3}. The L2 shift comes from a slow no-idle baseline, and the DRAM ones from rows opening and closing.`],
  ['Leakage is typically 5–30% of a design’s power, about 20% common.', 'worse at idle; under load, not established',
    `On aifoundry2 at 80 °C, leakage is ${V.leakR} W: ${V.idleShR} of an idle card and ${V.busyShR} of a ${V.busyW} W random-data matmul. ` +
    `The idle readings fix its slope, ${V.slope80} W/°C, but not its split from the fixed power, hence the ranges (the idle law, <a href="#what-that-costs">§5</a>). ` +
    `The three-card check's cooling cycles could not narrow the split: they allow ${V.kBusy} of a busy card, so leakage above 30% under load is not established. ` +
    `At ${V.T3} °C, where aifoundry3 ran, the same law puts it at ${V.busy3R} of a busy card.`]];
  const t = document.getElementById('verdict');
  t.innerHTML = '<thead><tr><th>What David Kanter said (paraphrased)</th><th>Verdict on the ET-SoC-1</th><th>Evidence</th></tr></thead><tbody>' +
    R.map(v => `<tr><td>${v[0]}</td><td class="lvl">${v[1]}</td><td class="small">${v[2]}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
})();

/* ---------- §3: the three machines ---------- */
(function () {
  // The governor readouts of the three-card check (D.v3.governor: TEL-G, three passes per card, 26 September), one
  // column per card in registry order; a value that differed between passes would show every value seen.
  const C = D.cards, cf = C.config, sp = C.sptrace_aifoundry3, V3 = D.v3, G3 = V3.governor;
  const ids = CK.cardsIn(G3), one = (c, f) => [...new Set(G3[c][f.split('.')[0]].map(v => f.split('.').slice(1).reduce((o, k) => o[k], v)))].join(' / ');
  const clk = c => { const h = V3.clock_mhz[c] || {}, n = Object.values(h).reduce((a, b) => a + b, 0), hi = Object.keys(h).filter(k => +k > FMIN);
    const sr = (V3.sp_readouts || {})[c];
    const at = `all ${num(n, 0)} of its samples in the check at ${Object.keys(h).join(', ')} MHz`;
    if (hi.length) return `${hi.join(', ')} MHz in the check`;
    if (G3[c].config[0].tdp_w === 0) return `no: ${at}`;
    if (sr && sr.busy_cool) return `no: ${at}, ${num(sr.busy_cool, 0)} of them busy at a mean of 64 °C or less and under ${TW} W, where a live governor climbs: its governor does not act (§9)`;
    return `not in the check, which never found it cool and busy: ${at}`; };
  const bold = (c, v, odd) => (odd ? '<b>' + v + '</b>' : v);
  const R = [['Firmware release / PMIC', c => G3[c].fw.map(f => f.join(' / ')).join('; '), c => G3[c].fw[0][0] !== G3.aifoundry2.fw[0][0]],
    ['TDP the <i>driver</i> reports', c => one(c, 'driver.tdp_w') + ' W'],
    ['TDP the <i>service processor</i> reports', c => one(c, 'config.tdp_w') + ' W', c => G3[c].config[0].tdp_w !== TW],
    ['Software temperature threshold', c => one(c, 'config.temp_threshold_c') + ' °C'],
    ['Power state the firmware reports', c => one(c, 'config.power_state_name'), c => G3[c].config[0].tdp_w !== TW],
    ['Minion clock ever observed above 600 MHz', c => (c === 'aifoundry2' ? 'yes, 700 and 800, from a cool die (21 and 23 Sep; 28 Sep, §8); ' : '') + clk(c), c => c !== 'aifoundry2'],
    ['Usable for these measurements', () => 'yes']];
  const t = document.getElementById('cardcfg');
  t.innerHTML = '<thead><tr><th>&nbsp;</th>' + ids.map(c => `<th>${CK.card(c).label}</th>`).join('') + '</tr></thead><tbody>' +
    R.map(r => `<tr><td class="small">${r[0]}</td>` + ids.map(c => `<td>${bold(c, r[1](c), r[2] && r[2](c))}</td>`).join('') + '</tr>').join('') + '</tbody>';
  CK.stackTable(t);
  const same = ['aifoundry2', 'aifoundry3'].every(c => G3[c].config.length === 1 && G3[c].config[0].tdp_w === cf[c].tdp_w &&
    G3[c].config[0].power_state_name === cf[c].power_state_name && G3[c].config[0].temp_threshold_c === cf[c].temp_threshold_c);
  document.getElementById('cardcfg-note').innerHTML = `Read over the management interface and the driver in ${word(G3.aifoundry2.passes)} passes per card on ` +
    `26 September, in the three-card check (V3-TEL); every pass gave the same values, and every one of the ${f0(ids.reduce((a, c) => a + G3[c].launches, 0))} ` +
    `timed launches ran at ${range(Math.min(...ids.map(c => G3[c].launch_ghz[0])) * 1000, Math.max(...ids.map(c => G3[c].launch_ghz[1])) * 1000, 1)} MHz. ` +
    (same ? 'aifoundry2 and aifoundry3 gave the same readouts on 22 September. ' : '') +
    'aifoundry1’s card 0 (firmware 1.4.1) overheats and was left out of the check (amendment A4).';
  const ev = D.sptrace_events, gl = ids.map(c => G3[c].governor_lines);
  if (sp) document.getElementById('spcount').innerHTML = `That 8 KB window of the card's trace buffer, read on 22 September, holds <b>${sp.down_events} throttle-down events</b>` +
    (ev ? ` alternating with <b>${ev.idle} idle events</b>` + (ev.consecutive_idle_pairs ? ` (one idle event follows another ${ev.consecutive_idle_pairs === 1 ? 'once' : ev.consecutive_idle_pairs + ' times'})` : '') : '') +
    `, and <b>${sp.up_events} throttle-up events</b>, every one of them printing a TDP level of ${sp.tdp_levels.join(', ')}. ` +
    'One throttle-down per busy period is how the cards\' governor logs, once per change of state (<a href="#the-loop-as-built">§1</a>); ' +
    'the 353f20e source would log on every pass or, at the lowest operating point, not at all. ' +
    `The three-card check read the same window after five launches in each of its passes on 26 September and found ` +
    (gl.every(v => v === 0) ? `<b>no governor line at all, on any card</b>: every window held only host-interface and performance-request messages. So this pattern rests on the one 22 September window.`
      : `${ids.map((c, k) => `${gl[k]} governor lines on ${CK.card(c).label}`).join(', ')}.`) +
    (gl.every(v => v === 0) ? ' The cards\' source predicts that aifoundry3\'s lines never come back (below).' : '');
})();

/* ---------- V3: every repeat of the wake-up probe ---------- */
(function () {
  const w = D.wakeup, s32 = v => (v >= 2147483648 ? v - 4294967296 : v);   // analyze_dvfs.py writes int32; guards a u32 copy
  const perMs = w.idle_cycles[w.idle_cycles.length - 1] / w.idle_ms[w.idle_ms.length - 1];   // cycles per ms of idle
  const ms = w.idle_cycles.map(c => c / perMs);
  const idleLab = k => (k === 0 ? 'no idle' : ms[k] < 1 ? num(ms[k] * 1000, ms[k] < 0.01 ? 1 : 0) + ' µs' : num(ms[k], ms[k] < 10 ? 1 : 0) + ' ms');
  const COL = {'L1 (line left in place)': 'var(--c1)', L1: 'var(--c3)', L2: 'var(--c4)', L3: 'var(--c7)', DRAM: 'var(--bad)'};
  const LV = w.levels.map(l => {
    const reps = l.paired_by_repeat.map(r => r.map(s32));
    // a load that reads exactly 128 cycles off its level's median: the kernel's cycle-counter correction misfired
    const mis = reps.map(r => r.map((v, k) => k > 0 && Math.abs(v) >= 100 && [128, -128].some(o => Math.abs(v + o - l.paired_median_by_idle[k]) <= 6)));
    return {l, reps, mis};
  });
  const CLIP = 40, A = [9, 14], NEAR = 6;
  const st = {lev: LV.findIndex(v => v.l.level === 'DRAM'), k: ms.length - 1};
  const count = (lv, k) => {
    const d = lv.reps.map(r => r[k]), a = d.filter(v => v >= A[0] && v <= A[1]).length, b = d.filter(v => Math.abs(v) <= NEAR).length;
    const o = lv.reps.map((r, j) => ({v: r[k], mis: lv.mis[j][k]})).filter(e => !(e.v >= A[0] && e.v <= A[1]) && Math.abs(e.v) > NEAR);
    return {n: d.length, a, b, o};
  };
  const countText = (lv, k) => {
    const c = count(lv, k), parts = [];
    if (c.a) parts.push(`${c.a} at ${sgn(A[0])} to ${sgn(A[1])} cycles`);
    if (c.b) parts.push(`${c.b} within ${NEAR} of zero`);
    const mis = c.o.filter(e => e.mis), rest = c.o.filter(e => !e.mis);
    if (rest.length === 1) parts.push(`1 outlier (${sgn(rest[0].v)})`);
    else if (rest.length) parts.push(`${rest.length} at ${srange(rest.map(e => e.v))} cycles`);
    if (mis.length) parts.push(`${mis.length} at ${mis.map(e => sgn(e.v)).join(', ')} (a counter misfire)`);
    parts[0] = parts[0].replace(/^(\d+)/, `$1 of ${c.n}`);
    return parts.join(', ');
  };
  const read = CK.readout('wake-count'), off = document.getElementById('wake-off');
  CK.seg('wake-level', {label: 'Level', options: LV.map((v, j) => [j, v.l.level]), value: st.lev, onChange: v => { st.lev = v; frame.redraw(); }});
  CK.range('wake-idle', {label: 'Count the repeats at', stops: ms.map((_, k) => k).slice(1), value: st.k, fmt: idleLab,
    onInput: v => { st.k = v; frame.redraw(); }});
  function draw(f) {
    const lv = LV[st.lev], W = f.W, H = f.H, L = 44, R = 12, T = 24, B = 40, svg = f.svg;
    legendHTML('wake-leg', [{mark: 'line', color: 'var(--ref)', w: 1.3, label: `one repeat (${lv.reps.length})`},
      {mark: 'line', color: COL[lv.l.level] || 'var(--c1)', w: 3, label: `median of the ${lv.reps.length}`}]
      .concat(lv.l.level === 'DRAM' ? [{mark: 'dash', color: 'var(--ink-2)', label: '+11: one row activate (tRCD)'}] : []));
    const x0 = L + 12, lx = CK.log(1e-3, 30, L + 46, W - R);      // "no idle" sits left of a break in the log axis
    const X = k => (k === 0 ? x0 : lx(ms[k])), y = CK.lin(-CLIP, CLIP, H - B, T);
    CK.axes(f, {x: lx, y, L, R, T, B, yt: [-40, -20, 0, 20, 40], xt: [1e-3, 1e-2, 1e-1, 1, 10],
      xfmt: v => (v < 1 ? num(v * 1000, 0) + ' µs' : num(v, 0) + ' ms'), yfmt: v => sgn(v, 0),
      xl: 'how long the line sat untouched', yl: 'cycles, against the same repeat with no idle'});
    CK.txt(svg, x0, H - B + 16, '0', 'tick', 'middle');
    CK.txt(svg, (x0 + lx(1e-3)) / 2 + 4, H - B + 4, '//', 'tick', 'middle');
    CK.el('line', {x1: L, x2: W - R, y1: y(0), y2: y(0), stroke: 'var(--axis)', 'stroke-width': 1.2}, svg);
    if (lv.l.level === 'DRAM') {
      CK.el('line', {x1: L, x2: W - R, y1: y(11), y2: y(11), stroke: 'var(--ink-2)', 'stroke-width': 1.2, 'stroke-dasharray': '5 4'}, svg);
    }
    CK.el('line', {x1: X(st.k), x2: X(st.k), y1: T, y2: H - B, stroke: 'var(--ink-2)', 'stroke-width': 1, opacity: 0.6}, svg);
    const cl = v => Math.max(-CLIP, Math.min(CLIP, v));
    const nodes = lv.reps.map((r, j) => {
      const g = CK.el('g', {}, svg), d = CK.path(r.map((v, k) => [k, cl(v)]), X, y);
      CK.el('path', {d, class: 'rep', fill: 'none', stroke: 'var(--ref)', 'stroke-width': 1.3, opacity: 0.75, 'stroke-linejoin': 'round'}, g);
      CK.el('path', {d, fill: 'none', stroke: 'transparent', 'stroke-width': 10, 'pointer-events': 'stroke'}, g);
      CK.tip(f, g, `<b>repeat ${j}</b>: ${r.map(v => sgn(v)).join(', ')} cycles<br>(at ${ms.map((_, k) => idleLab(k)).join(', ')})` +
        (lv.mis[j].some(Boolean) ? '<br>' + sgn(r.find((v, k) => lv.mis[j][k])) + ' is a cycle-counter carry misfire, not a wake-up' : ''), {role: 'img'});
      return g;
    });
    CK.el('path', {d: CK.path(lv.l.paired_median_by_idle.map((v, k) => [k, v]), X, y), fill: 'none', stroke: COL[lv.l.level] || 'var(--c1)',
      'stroke-width': 3, 'stroke-linejoin': 'round', 'pointer-events': 'none'}, svg);
    // values past the scale: a small arrow at the edge (one per idle and edge)
    const edge = {};
    lv.reps.forEach((r, j) => r.forEach((v, k) => { if (Math.abs(v) > CLIP) (edge[k + (v > 0 ? '+' : '-')] = edge[k + (v > 0 ? '+' : '-')] || []).push({v, j, mis: lv.mis[j][k]}); }));
    for (const key in edge) {
      const k = +key.slice(0, -1), upE = key.endsWith('+'), cx = X(k), cy = upE ? T - 2 : H - B + 2;
      CK.el('polygon', {points: upE ? `${cx - 5},${cy + 7} ${cx + 5},${cy + 7} ${cx},${cy}` : `${cx - 5},${cy - 7} ${cx + 5},${cy - 7} ${cx},${cy}`,
        fill: edge[key].every(e => e.mis) ? 'var(--surface)' : 'var(--ink-2)', stroke: 'var(--ink-2)', 'stroke-width': 1.2, 'pointer-events': 'none'}, svg);
    }
    // a misfire that repeats on every idle of one repeat gets its own label on the chart
    lv.mis.forEach((m, j) => {
      if (m.filter(Boolean).length < 3) return;
      const v = lv.reps[j][m.findIndex(Boolean)];
      CK.txt(svg, W - R - 2, v < 0 ? H - B - 16 : T + 24, `${sgn(v)} (repeat ${j}): a counter misfire, not a wake-up`, 'lab', 'end');
    });
    CK.keynav(f, nodes);
    read.set(`At ${idleLab(st.k)}: ${countText(lv, st.k)}.`);
    // the list of values past the scale, in words
    const items = [], many = new Set();
    lv.reps.forEach((r, j) => {
      const ks = r.map((v, k) => (Math.abs(v) > CLIP ? k : -1)).filter(k => k >= 0);
      if (ks.length >= 3) many.add(j);
      if (ks.length >= 3) items.push({k: ks[0], s: `repeat ${j} at ${ks.length === r.length - 1 ? 'every idle' : ks.length + ' idles'}: ${srange(ks.map(k => r[k]))}` +
        (ks.every(k => lv.mis[j][k]) ? ' (its no-idle load read 128 cycles too long)' : '')});
    });
    const byk = {};
    lv.reps.forEach((r, j) => r.forEach((v, k) => { if (Math.abs(v) > CLIP && !many.has(j)) (byk[k] = byk[k] || []).push(sgn(v) + (lv.mis[j][k] ? ' (misfire)' : '')); }));
    for (const k in byk) items.push({k: +k, s: `at ${idleLab(+k)}: ${byk[k].sort().join(', ')}`});
    items.sort((a, b) => a.k - b.k);
    off.textContent = items.length ? `Off the scale (marked by arrows at the edge): ${items.map(it => it.s).join('; ')}.` : 'Every value of this level is on the scale.';
  }
  const frame = CK.frame('wake', {height: W => (W < 600 ? 300 : 320), minW: 280, maxW: 640,
    label: 'Load latency after each idle, minus the same repeat with no idle, one line per repeat', draw});
  const dram = LV.find(v => v.l.level === 'DRAM'), c = count(dram, ms.length - 1), rest = c.o.filter(e => !e.mis);
  V.wakecount = `${c.a} of the ${c.n} paired differences at ${idleLab(ms.length - 1)} are ${sgn(A[0])} to ${sgn(A[1])} cycles, ${word(c.b)} are ` +
    `within ${NEAR} cycles of zero and ` + (rest.length === 1 ? `one is an outlier (${sgn(rest[0].v)} cycles)` : `${word(rest.length)} are outliers`);
  // loads on which the kernel's cycle-counter correction misfired: a repeat marked at every idle is one bad no-idle load
  V.misfires = word(LV.reduce((a, v) => a + v.mis.reduce((b, m) => { const k = m.filter(Boolean).length; return b + (k === m.length - 1 ? 1 : k); }, 0), 0));
  V.probe = f1(w.idle_cycles.reduce((a, b) => a + b, 0) * (w.reps || 20) * w.levels.length / perMs / 1000) + ' s';

  // The same probe on three cards (D.v3.wakeup: the check's kept probes, three per card, 26 September), at its longest
  // idle, with the chart's classes; the 22 September probe first, for comparison
  const W3 = V3.wakeup, ids = CK.cardsIn(W3), FAST = [-A[1], -(NEAR + 1)];
  const cls = reps => { const d = reps.map(r => s32(r[r.length - 1]));
    const a = d.filter(v => v >= A[0] && v <= A[1]).length, b = d.filter(v => Math.abs(v) <= NEAR).length, fa = d.filter(v => v >= FAST[0] && v <= FAST[1]);
    return {a, b, f: fa.length, fv: fa, o: d.length - a - b - fa.length, n: d.length}; };
  const lvl = (levels, n) => levels.find(l => l.level === n);
  const row = (lab, levels) => { const c = cls(lvl(levels, 'DRAM').paired_by_repeat), l1 = [lvl(levels, 'L1 (line left in place)'), lvl(levels, 'L1')].map(l => l.paired_delta_cycles);
    return {c, html: `<tr><td class="small">${lab}</td><td class="num">${orList(l1)}</td><td class="num">${sgn(lvl(levels, 'L2').paired_delta_cycles, 1).replace(/\.0$/, '')}</td>` +
      `<td class="num">${sgn(lvl(levels, 'L3').paired_delta_cycles, 1).replace(/\.0$/, '')}</td><td class="num">${sgn(lvl(levels, 'DRAM').paired_delta_cycles, 1).replace(/\.0$/, '')}</td>` +
      `<td class="num">${c.a} · ${c.b} · ${c.f} · ${c.o}</td></tr>`}; };
  const rows = [row('aifoundry2 · 22 Sep (the chart)', w.levels)];
  const v3rows = ids.flatMap(c => W3[c].probes.map(p => Object.assign({card: c, probe: p}, row(`${cardLab(c)} · 26 Sep, probe ${p.probe.replace('p', '')}`, p.levels))));
  document.getElementById('wake3').innerHTML = '<thead><tr><th>Card · probe</th><th class="num">L1</th><th class="num">L2</th><th class="num">L3</th>' +
    `<th class="num">DRAM</th><th class="num">DRAM lines at 27 ms: ${sgn(A[0])} to ${sgn(A[1])} · within ${NEAR} · ${sgn(FAST[0])} to ${sgn(FAST[1])} · other</th></tr></thead><tbody>` +
    rows.concat(v3rows).map(r => r.html).join('') + '</tbody>';
  const clocks = ids.flatMap(c => W3[c].probes.flatMap(p => [...Object.keys(p.clock.pre), ...Object.keys(p.clock.post)]));
  const a3 = v3rows.filter(r => r.card === 'aifoundry3'), fv = a3.flatMap(r => r.c.fv), dm = v3rows.map(r => lvl(r.probe.levels, 'DRAM').paired_delta_cycles);
  document.getElementById('wake3-note').innerHTML = `Paired median shift at 27 ms, in cycles, per level (L1: the line left in place and placed by an evict; on a narrow screen the L1 and L3 columns are hidden). ` +
    `The check's probes add two shorter idles, 0.17 and 0.5 µs. The minion clock read ${[...new Set(clocks)].join(', ')} MHz in the samples just before and after every one of them; no level on any card shows a shift of 5 cycles or more common to 18 of the 20 lines at 27 ms (${ids.map(c => `${cardLab(c)}: ${W3[c].decision.replace(/^no wake-up.*\(P5 (\d) of (\d)\)$/, '$1 of $2 probes')}`).join('; ')}).`;
  V.wakeDram = `The check's ${word(v3rows.length)} probes on three cards (26 September) split the DRAM lines the same way, into groups about ` +
    `ten cycles apart, but not in the same proportion (the table above): at 27 ms, ${Math.min(...v3rows.map(r => r.c.a))} to ` +
    `${Math.max(...v3rows.map(r => r.c.a))} of the 20 lines paid ${sgn(A[0])} to ${sgn(A[1])} cycles, and on aifoundry3 ` +
    `${Math.min(...a3.map(r => r.c.f))} to ${Math.max(...a3.map(r => r.c.f))} lines read ${-Math.max(...fv)} to ${-Math.min(...fv)} cycles <i>faster</i> ` +
    `after the idle than with none, a slow no-idle load as in L2; so the median shift runs from ${srange(dm)} cycles by card and probe`;
})();

/* ---------- V2: one law, three checks ---------- */
(function () {
  const m = D.leak_model, ic = D.idle_check, on = D.overnight_idle, lk = D.cards.leakage;
  const leak = LAW.c.leak, law = LAW.c.law, slope = LAW.c.slope;   // the central fit: model.json's own
  const SW = LAW.c.SW;                                           // switching watts of the random-data matmul at 80 °C
  const K = D.leak_fraction.kanter_range;
  const fitT = m.idle_curve.map(b => b.T);
  const st = {T: 80, busy: false, cyc: false};
  // the three-card check's cooling cycles (D.idle_sessions, campaign "v3"): per card, each whole-degree bin's idle
  // power averaged over the cycles that reached it (the cycles' bins are the check's own, analyze_dvfs.py --v3)
  const CYC = (() => {
    const by = {};
    for (const r of D.idle_sessions.sessions.filter(q => q.campaign === 'v3'))
      for (const b of r.bins) ((by[r.card] = by[r.card] || {})[b.T] = by[r.card][b.T] || []).push(b.W);
    return CK.cardsIn(by).map(c => ({card: c, pts: Object.keys(by[c]).map(Number).sort((a, b) => a - b)
      .map(T => ({T, P: by[c][T].reduce((a, b) => a + b, 0) / by[c][T].length, k: by[c][T].length}))}));
  })();
  const read = CK.readout('law-read');
  CK.range('law-T', {label: 'Die temperature', min: 45, max: 95, step: 1, value: st.T, fmt: v => f0(v) + ' °C', onInput: v => { st.T = v; frame.redraw(); }});
  const toggle = (id, key) => { const b = document.getElementById(id); b.addEventListener('click', () => { st[key] = !st[key]; b.setAttribute('aria-pressed', String(st[key])); frame.redraw(); }); };
  toggle('law-busy', 'busy'); toggle('law-cyc', 'cyc');
  document.getElementById('law-cyc').textContent = `The three cards' cooling cycles (26 Sep)`;
  const legend = () => { legendHTML('law-leg', [{mark: 'shade', color: 'var(--ref)', op: 0.3, label: `fixed (central fit, ${f1(m.P_fix)} W)`}, {mark: 'shade', color: 'var(--c1)', op: 0.3, label: 'leakage (central fit)'},
    {mark: 'line', color: 'var(--ink)', label: 'the idle law (aifoundry2)'}, {mark: 'ring', color: 'var(--c1)', label: 'fit readings (size: samples)'},
    {mark: 'dot', color: 'var(--c5)', label: 'single checks on the same card'}, {mark: 'box', color: 'var(--c7)', label: 'aifoundry3, first session (22 Sep)'}]);
    if (st.cyc) { const tmp = document.createElement('div');                // the cards' marks, from the registry
      CK.legend(tmp, CK.cardLegend(CYC.map(c => c.card)).map(it => Object.assign(it, {label: it.label + ', cooling cycles (26 Sep)'})));
      document.getElementById('law-leg').append(...tmp.childNodes); } };
  legend();
  document.getElementById('law-cyc').addEventListener('click', legend);
  const pts = [
    ...m.idle_curve.map(b => ({T: b.T, P: b.P, kind: 'fit', html: `<b>${f0(b.T)} °C, aifoundry2, a fit reading</b><br>measured ${f2(b.P)} W, law ${f2(law(b.T))} W (${sgn(b.P - law(b.T), 2)} W)<br>${num(b.n, 0)} samples`, n: b.n})),
    {T: on.die_c, P: on.board_w, kind: 'chk', lab: 'overnight rest, 21 Sep', html: `<b>Overnight rest, 21 September</b> (one ${f1(on.seconds)} s reading before the first cool-start launch)<br>measured ${f2(on.board_w)} ± ${f2(on.board_sd)} W at ${f0(on.die_c)} °C<br>law ${f2(on.law_w)} W (${sgn(on.board_w - on.law_w, 2)} W); ${on.samples} samples`},
    {T: ic.die_c, P: ic.board_w, kind: 'chk', lab: `22 Sep, ${f1(ic.hours_idle)} h idle`, html: `<b>22 September, about ${f1(ic.hours_idle)} h after our last recorded workload</b> (one session)<br>measured ${f2(ic.board_w)} ± ${f2(ic.board_sd)} W at ${f1(ic.die_c)} °C<br>law ${f2(ic.model_pred_w)} W (${sgn(ic.board_w - ic.model_pred_w, 2)} W); ${ic.samples} samples`},
    ...lk.idle_curve.map(b => ({T: b.T, P: b.W, kind: 'a3', html: `<b>${f0(b.T)} °C, aifoundry3, 22 September</b> (its first session)<br>measured ${f2(b.W)} W, aifoundry2's law ${f2(b.card2_law_W)} W (${sgn(b.W - b.card2_law_W, 2)} W)<br>${num(b.n, 0)} samples`}))
  ].sort((a, b) => a.T - b.T);
  const nmax = Math.max(...m.idle_curve.map(b => b.n));
  function draw(f) {
    const W = f.W, H = f.H, L = 44, R = 12, T = 24, svg = f.svg;
    const SH = 58, mainB = H - SH - 40;                           // the leakage-share strip sits under the plot
    const x = CK.lin(45, 95, L, W - R), y = CK.lin(0, st.busy ? 80 : st.cyc ? 55 : 50, mainB, T);
    CK.axes(f, {x, y, L, R, T, B: H - mainB, xt: [50, 60, 70, 80, 90], xfmt: v => f0(v) + ' °C',
      yl: st.busy ? 'board power, W' : 'board power at idle, W'});
    const Ts = []; for (let t = 45; t <= 95; t += 0.5) Ts.push(t);
    const area = (lo, hi) => CK.path(Ts.map(t => [t, hi(t)]).concat(Ts.slice().reverse().map(t => [t, lo(t)])), x, y) + 'Z';
    CK.el('path', {d: area(() => 0, () => m.P_fix), fill: 'var(--ref)', opacity: 0.2}, svg);
    CK.el('path', {d: area(() => m.P_fix, law), fill: 'var(--c1)', opacity: 0.2}, svg);
    if (st.busy) {
      CK.el('path', {d: area(law, t => law(t) + SW), fill: 'var(--c2)', opacity: 0.2}, svg);
      CK.el('path', {d: CK.path(Ts.map(t => [t, law(t) + SW]), x, y), fill: 'none', stroke: 'var(--c2)', 'stroke-width': 2}, svg);
      CK.txt(svg, x(47), y(law(47) + SW / 2) + 4, `switching, random matmul, ${f1(SW)} W`, 'lab');
    }
    CK.txt(svg, x(47), y(m.P_fix / 2) + 4, `fixed ${f1(m.P_fix)} W`, 'lab');
    CK.txt(svg, x(47), y((m.P_fix + law(47)) / 2) + 4, 'leakage', 'lab');
    CK.el('path', {d: CK.path(Ts.map(t => [t, law(t)]), x, y), fill: 'none', stroke: 'var(--ink)', 'stroke-width': 2}, svg);
    // cursor at the chosen temperature
    CK.el('line', {x1: x(st.T), x2: x(st.T), y1: T, y2: mainB, stroke: 'var(--ink-2)', 'stroke-width': 1}, svg);
    CK.el('circle', {cx: x(st.T), cy: y(law(st.T)), r: 4, fill: 'var(--ink)', stroke: 'var(--surface)', 'stroke-width': 2, 'pointer-events': 'none'}, svg);
    if (st.busy) CK.el('circle', {cx: x(st.T), cy: y(law(st.T) + SW), r: 4, fill: 'var(--c2)', stroke: 'var(--surface)', 'stroke-width': 2, 'pointer-events': 'none'}, svg);
    const nodes = pts.map(p => {
      const cx = x(p.T), cy = y(p.P);
      const node = p.kind === 'fit' ? CK.el('circle', {cx, cy, r: 4 + 5 * Math.sqrt(p.n / nmax), fill: 'var(--surface)', 'fill-opacity': 0.6, stroke: 'var(--c1)', 'stroke-width': 2}, svg)
        : p.kind === 'a3' ? CK.el('rect', {x: cx - 5, y: cy - 5, width: 10, height: 10, rx: 1.5, fill: 'var(--c7)', stroke: 'var(--surface)', 'stroke-width': 1.5}, svg)
        : CK.el('circle', {cx, cy, r: 5.5, fill: 'var(--c5)', stroke: 'var(--surface)', 'stroke-width': 2}, svg);   // not --c3: the registry's aifoundry1 card 1
      CK.tip(f, node, p.html);
      return node;
    });
    if (st.cyc) for (const c of CYC) {                               // each card's cooling cycles: a thin line and its bins
      const k = CK.card(c.card);
      CK.el('path', {d: CK.path(c.pts.map(p => [p.T, p.P]), x, y), fill: 'none', stroke: k.color, 'stroke-width': 1.5, opacity: 0.8}, svg);
      for (const p of c.pts) {
        const node = CK.cardMark(svg, c.card, x(p.T), y(p.P), 3.5);
        CK.tip(f, node, `<b>${f0(p.T)} °C, ${k.label}, cooling cycles of 26 September</b> (mean of ${word(p.k)} cycle${p.k === 1 ? '' : 's'})<br>` +
          `measured ${f2(p.P)} W, aifoundry2's law ${f2(law(p.T))} W (${sgn(p.P - law(p.T), 2)} W)`);
        nodes.push(node);
      }
    }
    for (const p of pts.filter(q => q.lab))                          // direct labels for the two same-card checks, below the curve
      CK.txt(svg, x(p.T) + 8, y(p.P) + 18, p.lab, 'lab-strong');
    CK.keynav(f, nodes);
    // the share strip: leakage as a share of idle and of a random-data matmul, against Kanter's typical range;
    // each share is a bar across the split's range (D.leak_split) with the central fit marked on it
    const s0 = mainB + 40, sx = CK.lin(0, 1, L, W - R), sy = s0 + SH / 2;
    const idleS = LAW.idleSh(LAW.c, st.T), busyS = LAW.busySh(LAW.c, st.T);
    const idleR = LAW.span(f => LAW.idleSh(f, st.T)), busyR = LAW.span(f => LAW.busySh(f, st.T)), leakW = LAW.span(f => f.leak(st.T));
    const kr = range(100 * K[0], 100 * K[1], 0) + '%';
    CK.txt(svg, 2, s0 - 2, `leakage share at ${f0(st.T)} °C (bar: range); shaded: Kanter's ${kr}`, 'lab');
    CK.el('rect', {x: sx(K[0]), y: sy - 9, width: sx(K[1]) - sx(K[0]), height: 18, fill: 'var(--c3)', opacity: 0.22}, svg);
    CK.txt(svg, (sx(K[0]) + sx(K[1])) / 2, sy + 24, kr, 'tick', 'middle');
    CK.el('line', {x1: L, x2: W - R, y1: sy, y2: sy, stroke: 'var(--axis)'}, svg);
    for (const v of [0, 0.5, 1]) CK.txt(svg, sx(v), sy + 24, pct(v), 'tick', v ? (v < 1 ? 'middle' : 'end') : 'start');
    const mark = (v, r, c, box, lab) => {
      CK.el('rect', {x: sx(r[0]), y: sy - 3.5, width: Math.max(2, sx(r[1]) - sx(r[0])), height: 7, rx: 3.5, fill: c, opacity: 0.45}, svg);
      if (box) CK.el('rect', {x: sx(v) - 5, y: sy - 5, width: 10, height: 10, rx: 1.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.5}, svg);
      else CK.el('circle', {cx: sx(v), cy: sy, r: 5.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.5}, svg);
      CK.txt(svg, sx(v), sy - 11, lab, 'lab-strong', 'middle');
    };
    mark(busyS, busyR, 'var(--c2)', true, 'matmul');
    mark(idleS, idleR, 'var(--c1)', false, 'idle');
    const out = st.T < Math.min(...fitT) || st.T > Math.max(...fitT);
    read.set(`At ${f0(st.T)} °C: idle ${f1(law(st.T))} W, rising ${f2(slope(st.T))} W/°C; leakage ${range(leakW[0], leakW[1], 0)} W of it ` +
      `(${f1(leak(st.T))} W in the central fit drawn) → leakage is <b>${pctR(idleR)} of idle</b> and <b>${pctR(busyR)} of a random-data matmul</b>` +
      (out ? ` (extrapolated: the fit's idle readings span ${f0(Math.min(...fitT))}–${f0(Math.max(...fitT))} °C)` : '') +
      (st.busy ? `. The matmul's switching watts are held at their 80 °C value, ${f1(SW)} W.` : '') +
      (st.cyc ? (st.busy ? ' ' : '. ') + `Cooling cycles at ${f0(st.T)} °C: ` + (CYC.map(c => { const p = c.pts.find(q => q.T === st.T);
        return p ? `${CK.card(c.card).label} ${f1(p.P)} W (${sgn(p.P - law(st.T), 1)} W)` : null; }).filter(Boolean).join(', ') || 'none reached this temperature') + '.' : ''));
  }
  const frame = CK.frame('leaklaw', {height: W => (W < 600 ? 400 : 410), minW: 280, maxW: 640,
    label: 'Idle board power against die temperature: the fitted law, its fit readings and three out-of-sample checks', draw});
  // aifoundry3's first session, bin by bin (the squares on the chart), and every session the law was not fitted on
  document.getElementById('leaktab').innerHTML = '<thead><tr><th class="num">aifoundry3 die °C</th><th class="num">measured idle W</th>' +
    '<th class="num">aifoundry2 law W</th><th class="num">difference</th><th class="num">samples</th></tr></thead><tbody>' +
    lk.idle_curve.map(r => `<tr><td class="num">${f0(r.T)}</td><td class="num">${f2(r.W)}</td><td class="num">${f2(r.card2_law_W)}</td>` +
      `<td class="num">${sgn(r.W - r.card2_law_W, 2)}</td><td class="num">${num(r.n, 0)}</td></tr>`).join('') +
    `<tr><td colspan="3"><b>mean of the four bins</b></td><td class="num"><b>${sgn(lk.mean_offset_W, 2)}</b></td><td class="num"></td></tr>` +
    `<tr><td colspan="3">mean by sample</td><td class="num">${sgn(lk.mean_offset_W_by_sample, 2)}</td><td class="num">${num(lk.idle_curve.reduce((a, r) => a + r.n, 0), 0)}</td></tr></tbody>`;
  const cardOrder = CK.cardsIn([...new Set([...Object.keys(IS), ...D.idle_sessions.sessions.map(r => r.card)])]);   // registry order
  // the sessions of 21-24 September first, then the three-card check's cooling cycles (campaign "v3"), each by card
  const SES = [...D.idle_sessions.sessions].sort((a, b) => (a.campaign === 'v3') - (b.campaign === 'v3') ||
    cardOrder.indexOf(a.card) - cardOrder.indexOf(b.card) || a.session.localeCompare(b.session));
  const sname = r => (r.campaign === 'v3' ? `claims-v3 · ${cardLab(r.card)} · cooling cycle ${r.pass}`
    : r.session.replace(/\.jsonl(\.gz)?$/, '').replace(/^\d{4}-\d{2}-\d{2}-/, ''));
  const IS3 = D.idle_sessions.summary_v3 || {};
  document.getElementById('sesstab').innerHTML = '<thead><tr><th>Session (the card is in its name)</th><th class="num">die °C</th>' +
    '<th class="num">idle samples</th><th class="num">measured − law, W</th></tr></thead><tbody>' +
    SES.map(r => `<tr><td class="small">${+r.day.slice(8, 10)} Sep · ${sname(r)}</td><td class="num">${range(r.T[0], r.T[1], 0)}</td>` +
      `<td class="num">${num(r.n, 0)}</td><td class="num">${sgn(r.offset_W, 2)}</td></tr>`).join('') +
    CK.cardsIn(IS).map(c => `<tr><td colspan="3"><b>${c}: mean of ${IS[c].sessions} sessions</b> ` +
      `(range ${sgn(IS[c].min_W, 2)} to ${sgn(IS[c].max_W, 2)})</td><td class="num"><b>${sgn(IS[c].mean_W, 2)}</b></td></tr>`).join('') +
    CK.cardsIn(IS3).map(c => { const bo = binOff(c);
      return bo ? `<tr><td colspan="3"><b>${cardLab(c)}: its ${word(IS3[c].sessions)} cooling cycles, 26 September, mean over whole-degree bins</b> ` +
        `(99% interval ${sgn(bo.ci99[0], 2)} to ${sgn(bo.ci99[1], 2)}; the figure the text and the energy manual give). Weighted by sample, as in the ` +
        `rows above, which leans to each cycle's cool end: mean ${sgn(IS3[c].mean_W, 2)} (range ${sgn(IS3[c].min_W, 2)} to ${sgn(IS3[c].max_W, 2)})</td>` +
        `<td class="num"><b>${sgn(bo.mean, 2)}</b></td></tr>`
      : `<tr><td colspan="3"><b>${cardLab(c)}: mean of its ${word(IS3[c].sessions)} cooling cycles, 26 September, weighted by sample</b> ` +
        `(range ${sgn(IS3[c].min_W, 2)} to ${sgn(IS3[c].max_W, 2)})</td><td class="num"><b>${sgn(IS3[c].mean_W, 2)}</b></td></tr>`; }).join('') + '</tbody>';
  // the prose around the chart
  const groups = []; for (const t of fitT) { const g = groups[groups.length - 1]; if (g && t === g[1] + 1) g[1] = t; else groups.push([t, t]); }
  V.fitT = groups.map(g => range(g[0], g[1], 0)).join(' and ');
  const hw = T => f1(slope(T) / 2), lo = Math.min(...fitT);
  V.checks = `the idle of every aifoundry2 session it was not fitted on to within ${f1(Math.ceil(S2.max_abs_W * 10) / 10)} W ` +
    `(<b>${S2.sessions} sessions, ${dayList(S2.days)}</b>; on average the law reads ${f1(-S2.mean_W)} W high). Two single ` +
    `readings test it where the fit has no data: the card's rest after a cool night, <b>${f2(on.board_w)} W at ${f0(on.die_c)} °C</b> ` +
    `on 21 September (one ${f1(on.seconds)} s reading, ${word(lo - Math.round(on.die_c))} degrees below the fit's lowest bin), against <b>${f2(on.law_w)} W</b>; ` +
    `and its idle on 22 September, about ${f1(ic.hours_idle)} hours after our last recorded workload (the lab log puts the ${V.probe} ` +
    `wake-up probe of §4 five minutes before), on a die that rested ${f0(ic.die_c - on.die_c)} °C warmer than on 21 September (the room itself was not measured), ` +
    `<b>${f2(ic.board_w)} ± ${f2(ic.board_sd)} W at ${f1(ic.die_c)} °C</b>, in the gap between the fit's ` +
    `readings, against <b>${f2(ic.model_pred_w)} W</b>. Both agree within what the sensor's whole-degree readings allow ` +
    `(±${hw(on.die_c)} W at ${f0(on.die_c)} °C, ±${hw(ic.die_c)} W at ${f0(ic.die_c)} °C)`;
  // the three-card check's cooling cycles on aifoundry2 (IDLE-b): every bin that all its cycles reached, and the cycles' mean
  const b2 = V3.idle.b.aifoundry2, bT = Object.keys(b2.bins).map(Number).sort((a, b) => a - b), bm = bT.map(T => b2.bins[T].mean);
  const cT = Object.values(b2.T_range), co = b2.cycle_offset_W;
  V.checksV3 = `The three-card check then heated aifoundry2 to ${f0(Math.max(...V3.idle.tmax.aifoundry2))} °C and let it cool for 15 minutes, ` +
    `${word(co.n)} times (26 September, ${f0(Math.min(...cT.map(t => t[0])))}–${f0(Math.max(...cT.map(t => t[1])))} °C): in every whole-degree bin all ` +
    `${word(co.n)} cycles reached, ${f0(bT[0])} to ${f0(bT[bT.length - 1])} °C, the idle read ${srange(bm.map(v => +v.toFixed(2)))} W against the law ` +
    `(the cycles' mean ${sgn(co.mean, 2)} W, 99% interval ${sgn(co.ci99[0], 2)} to ${sgn(co.ci99[1], 2)} W). So the law holds there to a tenth of a watt, ` +
    `and the ${f1(-S2.mean_W)} W by which it read high in those sessions does not carry over`;
  V.unsensed = f1(ic.board_minus_rails);
  const d2 = V3.idle.d.aifoundry2;
  V.unsensedV3 = `The three-card check's cooling cycles passed 73 °C in only ${word(d2.cycles.length)} of ${word(co.n)} on aifoundry2, too few ` +
    `to confirm this by its own rule; ${d2.cycles.length === 2 ? 'both' : 'they'} put ${f2(d2.components_W.unsensed.mean)} W on no rail sensor at 73 °C`;
  // the three-card check's cooling cycles on aifoundry3 and aifoundry1 card 1 (IDLE-a): the residual bin by bin, cycle by cycle
  const ra = c => V3.idle.a[c].resid_by_bin.flatMap(cy => Object.entries(cy).map(([T, v]) => ({T: +T, v})));
  const r3 = ra('aifoundry3'), T3lo = Math.min(...r3.map(e => e.T)), T3hi = Math.max(...r3.map(e => e.T));
  const low3 = r3.filter(e => e.T <= 62).map(e => e.v), top3 = r3.filter(e => e.T === T3hi).map(e => e.v);
  const a3s = V3.idle.a.aifoundry3.resid_slope_W_per_C, a3o = V3.idle.a.aifoundry3.offset_W;
  const r1 = ra('aifoundry1-c1'), a1s = V3.idle.a['aifoundry1-c1'].resid_slope_W_per_C, tm = [].concat(...Object.values(V3.idle.tmax));
  V.a3law = `Across ${word(S3.sessions)} aifoundry3 sessions (${dayList(S3.days)}), idling at ${f0(S3.T[0])} to ${f0(S3.T[1])} °C, ` +
    `${lo - S3.T[1]} to ${lo - S3.T[0]} °C below the law's fit range, the law predicted that card's idle to within a watt: aifoundry3 read ` +
    `<b>${sgn(S3.mean_W, 1)} W</b> above it on average (${sgn(S3.min_W, 1)} to ${sgn(S3.max_W, 1)} W session by session), where aifoundry2's ` +
    `own sessions read ${sgn(S2.mean_W, 1)} W. But the offset is not a constant. The three-card check heated each card to ` +
    `${range(Math.min(...tm), Math.max(...tm), 0)} °C and let it cool for 15 minutes, ${word(a3o.n)} times per card (26 September): aifoundry3 then read ` +
    `${sgn(Math.min(...low3), 2)} to ${sgn(Math.max(...low3), 2)} W above the law from ${f0(T3lo)} to 62 °C and <b>${sgn(Math.min(...top3), 2)} to ${sgn(Math.max(...top3), 2)} W</b> ` +
    `at ${f0(T3hi)} °C, the gap growing ${f3(a3s.mean)} W per °C (99% interval ${f3(a3s.ci99[0])} to ${f3(a3s.ci99[1])}; ${sgn(a3o.mean, 2)} W averaged over its bins, ` +
    `${sgn(a3o.ci99[0], 2)} to ${sgn(a3o.ci99[1], 2)}). So a fixed ${sgn(S3.mean_W, 1)} W holds only near the temperatures that card idles at. ` +
    `aifoundry1's card 1, on older firmware (1.2.0), is far off the law: it idles ${sgn(Math.min(...r1.map(e => e.v)), 1)} to ${sgn(Math.max(...r1.map(e => e.v)), 1)} W ` +
    `above it between ${f0(Math.min(...r1.map(e => e.T)))} and ${f0(Math.max(...r1.map(e => e.T)))} °C, the gap growing ${f2(a1s.mean)} W per °C. ` +
    `The chart's second button draws the three cards' cycles; its squares are aifoundry3's first session, 22 September.`;
  const c64 = m.idle_curve.find(b => b.T === 64), c66 = m.idle_curve.find(b => b.T === 66);
  V.idleslope = f1((c66.P - c64.P) / 2); V.idleslopeT = '64–66';
})();

/* ---------- §5: every idle session's offset from the law, one row per card and campaign ---------- */
// A strip plot of D.idle_sessions.sessions[].offset_W (measured − law over the session's binned idle samples), one row
// per card in registry order for the sessions of 21-24 September, then one per card for the three-card check's cooling
// cycles of 26 September (campaign "v3"), with each row's mean ± sd from D.idle_sessions.summary / summary_v3 (or, for
// a row the summaries lack, computed here from its sessions the same way: mean and the ddof=1 standard deviation).
// Marks within a row are dodged into lanes so none hides another.
(function () {
  const SES = D.idle_sessions.sessions, IS3 = D.idle_sessions.summary_v3 || {};
  const sname = r => (r.campaign === 'v3' ? `cooling cycle ${r.pass} (claims-v3)` : r.session.replace(/\.jsonl(\.gz)?$/, '').replace(/^\d{4}-\d{2}-\d{2}-/, ''));
  const ids = CK.cardsIn([...new Set([...Object.keys(IS), ...SES.map(r => r.card)])]);
  const stat = ([c, v3]) => {
    const rs = SES.filter(r => r.card === c && (r.campaign === 'v3') === v3), v = rs.map(r => r.offset_W), s = (v3 ? IS3 : IS)[c];
    if (s) return {n: s.sessions, mean: s.mean_W, sd: s.sd_W, min: s.min_W, max: s.max_W, T: s.T, days: s.days, rs};
    const n = v.length, mean = v.reduce((a, b) => a + b, 0) / n;
    const sd = n > 1 ? Math.sqrt(v.reduce((a, b) => a + (b - mean) * (b - mean), 0) / (n - 1)) : null;
    return {n, mean, sd, min: Math.min(...v), max: Math.max(...v), T: [Math.min(...rs.map(r => r.T[0])), Math.max(...rs.map(r => r.T[1]))],
      days: [...new Set(rs.map(r => r.day))].sort(), rs};
  };
  const ROWS = [false, true].flatMap(v3 => ids.map(c => Object.assign({card: c, v3}, stat([c, v3])))).filter(r => r.rs.length);
  const what = r => (r.v3 ? `cooling cycle${r.n === 1 ? '' : 's'}` : `session${r.n === 1 ? '' : 's'}`);
  const allV = ROWS.flatMap(r => r.rs.map(q => q.offset_W).concat(r.sd == null ? [] : [r.mean - r.sd, r.mean + r.sd])).concat([0]);
  const span = Math.max(...allV) - Math.min(...allV), X0 = Math.min(...allV) - 0.06 * span, X1 = Math.max(...allV) + 0.06 * span;
  const R = 5, STEP = 2 * R + 2, LABH = 22, MEANH = 24, GAP = 14, TOP = 6, B = 40;
  const tempR = T => range(T[0], T[1], 0) + ' °C';
  const msd = r => `mean ${sgn(r.mean, 2)} W` + (r.sd == null ? '' : `, sd ${f2(r.sd)} W`);
  // lanes: each mark, taken in order of offset, goes to the nearest lane (0, −1, +1, −2, …) where it clears the others
  function lanes(r, x) {
    const pts = [...r.rs].sort((a, b) => a.offset_W - b.offset_W).map(q => ({q, px: x(q.offset_W)})), last = {};
    for (const p of pts) {
      for (let k = 0; ; k++) {
        const lane = k % 2 ? -(k + 1) / 2 : k / 2;
        if (last[lane] == null || p.px - last[lane] >= STEP) { p.lane = lane; last[lane] = p.px; break; }
      }
    }
    const lo = Math.min(...pts.map(p => p.lane)), hi = Math.max(...pts.map(p => p.lane));
    return {pts, lo, hi, h: LABH + (hi - lo + 1) * STEP + MEANH + GAP};
  }
  const L = 14, RR = 14;
  const lay = W => { const x = CK.lin(X0, X1, L, W - RR); return {x, rows: ROWS.map(r => lanes(r, x))}; };
  const height = W => { const l = lay(W); return TOP + l.rows.reduce((a, r) => a + r.h, 0) + B; };
  CK.legend('off-leg', CK.cardLegend([...new Set(ROWS.map(r => r.card))]).concat([{key: 'msd', label: 'mean ± sd across the row', mark: 'line', color: 'var(--ink-2)'}]));
  function draw(f) {
    const W = f.W, H = f.H, svg = f.svg, {x, rows} = lay(W), yAx = CK.lin(0, 1, H - B, TOP);
    const xt = x.ticks(Math.max(3, Math.round((W - L - RR) / 80)));
    for (const t of xt) if (t) CK.el('line', {x1: x(t), x2: x(t), y1: TOP, y2: H - B, class: 'grid-line'}, svg);
    CK.axes(f, {x, y: yAx, L, R: RR, T: TOP, B, yt: [], xt, xfmt: v => sgn(v, 1),
      xl: f.narrow ? 'measured − law, W' : 'idle measured − the aifoundry2 idle law, W (per session)'});
    const zero = (ya, yb) => CK.el('line', {x1: x(0), x2: x(0), y1: ya, y2: yb, stroke: 'var(--ink-2)', 'stroke-width': 1.5, 'stroke-dasharray': '4 3'}, svg);
    const nodes = [];
    let y0 = TOP;
    rows.forEach((l, ri) => {
      const r = ROWS[ri], c = CK.card(r.card);
      if (ri) CK.el('line', {x1: L, x2: W - RR, y1: y0, y2: y0, class: 'grid-line'}, svg);
      zero(y0 + LABH - 2, y0 + l.h);                                // the law, below the row's label
      const g = CK.el('g', {}, svg);
      const lab = CK.txt(g, L, y0 + 15, '', 'lab');
      Object.assign(lab.style, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '4px', strokeLinejoin: 'round'});   // a halo over the grid
      const b = CK.el('tspan', {class: 'lab-strong'}, lab); b.textContent = c.label;
      const bo = r.v3 ? binOff(r.card) : null;
      CK.el('tspan', {}, lab).textContent = ` · ${r.n} ${f.narrow && r.v3 ? 'cycles' : what(r)}${r.v3 && !f.narrow ? ', 26 Sep' : ''} · ` +
        (r.v3 ? (f.narrow ? `by sample ${sgn(r.mean, 2)} W` : `by sample ${sgn(r.mean, 2)} W` + (bo ? ` (by bin ${sgn(bo.mean, 2)})` : ''))
          : f.narrow && r.sd != null ? `${sgn(r.mean, 2)} ± ${f2(r.sd)} W` : msd(r));
      const yc = y0 + LABH + (-l.lo) * STEP + STEP / 2;
      for (const p of l.pts) {
        const q = p.q, m = CK.cardMark(g, r.card, p.px, yc + p.lane * STEP, R);
        CK.tip(f, m, `<b>${+q.day.slice(8, 10)} Sep · ${sname(q)}</b><br>${c.label}, die ${tempR(q.T)}<br>` +
          `${num(q.n, 0)} idle samples<br>measured − law: <b>${sgn(q.offset_W, 2)} W</b>`);
        m._row = ri; m._x = p.px; nodes.push(m);
      }
      const ym = y0 + LABH + (l.hi - l.lo + 1) * STEP + MEANH / 2;
      const mg = CK.el('g', {}, svg);
      if (r.sd != null) {
        const a = x(r.mean - r.sd), z = x(r.mean + r.sd);
        CK.el('line', {x1: a, x2: z, y1: ym, y2: ym, stroke: c.color, 'stroke-width': 2}, mg);
        for (const e of [a, z]) CK.el('line', {x1: e, x2: e, y1: ym - 5, y2: ym + 5, stroke: c.color, 'stroke-width': 2}, mg);
      }
      const lo = r.sd == null ? x(r.mean) - 6 : Math.min(x(r.mean - r.sd), x(r.mean) - 6), hi = r.sd == null ? x(r.mean) + 6 : Math.max(x(r.mean + r.sd), x(r.mean) + 6);
      CK.el('rect', {class: 'ck-hit', x: lo - 4, y: ym - 10, width: hi - lo + 8, height: 20}, mg);
      CK.el('rect', {x: x(r.mean) - 2, y: ym - 8, width: 4, height: 16, rx: 1, fill: c.color}, mg);
      const bt = r.v3 ? binOff(r.card) : null;
      CK.tip(f, mg, `<b>${c.label}: ${r.n} ${what(r)}</b><br>${r.v3 ? 'weighted by sample: ' : ''}${msd(r)}<br>` +
        `range ${sgn(r.min, 2)} to ${sgn(r.max, 2)} W<br>die ${tempR(r.T)}; ${dayList(r.days)}` +
        (bt ? `<br>mean over whole-degree bins (the text's and the energy manual's figure): <b>${sgn(bt.mean, 2)} W</b>` : ''));
      mg._row = ri; mg._x = x(r.mean); nodes.push(mg);
      y0 += l.h;
    });
    CK.txt(svg, x(0) + 4, H - B - 4, 'law', 'lab');
    // Up and Down move to the nearest mark in the row above or below; Left and Right step through a row
    CK.keynav(f, nodes, {step: (k, K) => {
      if (K !== 'ArrowUp' && K !== 'ArrowDown') return null;
      const row = nodes[k]._row + (K === 'ArrowDown' ? 1 : -1), cand = nodes.map((n, j) => j).filter(j => nodes[j]._row === row);
      if (!cand.length) return k;
      return cand.reduce((b, j) => (Math.abs(nodes[j]._x - nodes[k]._x) < Math.abs(nodes[b]._x - nodes[k]._x) ? j : b), cand[0]);
    }});
  }
  CK.frame('offstrip', {height, minW: 280, maxW: 640, draw,
    label: 'Idle offset from the aifoundry2 idle law, one mark per session or cooling cycle, one row per card and campaign, with each row’s mean ± sd'});
  document.getElementById('off-sum').innerHTML = ROWS.map(r => { const bo = r.v3 ? binOff(r.card) : null;
    return `${CK.card(r.card).label}: ${word(r.n)} ${what(r)} (${dayList(r.days)}, die ${tempR(r.T)}), ${sgn(r.min, 2)} to ${sgn(r.max, 2)} W, ` +
      (r.v3 ? `weighted by sample ${msd(r)}` + (bo ? `; over whole-degree bins ${sgn(bo.mean, 2)} W` : '') : msd(r)); }).join('; ') + '.';
  const bh = ROWS.filter(r => r.v3 && binOff(r.card));
  if (bh.length) document.getElementById('off-basis').textContent = ` Each mark weights its idle samples alike, and a cooling cycle spends ` +
    `most of its 15 minutes near its cool end, so a cycle's mark sits below the mean over its whole-degree bins, which is the ` +
    `figure this section's text and the energy manual give: ${bh.map(r => `${sgn(binOff(r.card).mean, 2)} W on ${CK.card(r.card).label} ` +
    `(${sgn(r.mean, 2)} by sample)`).join('; ')}.`;
})();

/* ---------- §6: the second card, in one paragraph ---------- */
(function () {
  const C = D.cards, rr = C.patterns.map(p => p.a3 / p.model), a3 = C.patterns.map(p => p.a3);
  document.getElementById('card2').innerHTML =
    `aifoundry3, held at 600 MHz, ran the same strict protocol in one session on 22 September, at a ${f1(C.launch.aifoundry3.T)} °C launch. The flip-counting ` +
    `model fitted on aifoundry2 carries over with one per-card scale factor. Unchanged, it overestimates aifoundry3's switching ` +
    `power by ${pct(1 - C.scale)} (least squares; ${f0(100 * (1 - Math.max(...rr)))}–${pct(1 - Math.min(...rr))} pattern by pattern), ` +
    `${f2(C.rms_raw)} W rms. Multiplied by <b>${f2(C.scale)}</b>, it is within <b>${f2(C.rms_scaled)} W rms</b> over ` +
    `${f1(Math.min(...a3))}–${f0(Math.max(...a3))} W. The operating point cannot explain the gap: aifoundry3's ${C.voltage.a3_mv} mV ` +
    `against ${C.voltage.a2_mv} mV would predict ${pct(C.voltage.cv2f_ratio - 1)} <em>more</em> switching power. The chart and the ` +
    `leave-one-out calibration are in <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-second-card-and-what-transfers">§10 ` +
    `of the Horace experiment</a>. How the idle law transfers to this card is in <a href="#what-that-costs">What that costs</a>.`;
  V.a3launch = `${f2(C.launch.aifoundry3.T)} ± ${f2(C.launch.aifoundry3.T_sd)} °C`;
})();

/* ---------- §8: the development night of 27-28 September on aifoundry2 (D.dv2, written by
   tools/ettelem/build_dv2_data.py --merge from docs/reports/data/2026-09-28-dvfs2-aifoundry2). Development data: every
   chart title, caption and sentence here says so. The block holds one entry per card (D.dv2.cards); every chart reads its
   card from a selector that appears only when more than one card has such a night, so another card's night slots in. */
const DV = D.dv2, DVC = CK.cardsIn(DV.cards);
const PDT = ms => new Date(ms - 7 * 3600e3).toISOString().slice(11, 16);      // PDT is UTC-7 in September (DV.tz)
const hhmm = t => (t || '').slice(0, 5);
const PLACE = {B4C: 'the 4 central shires', INT16: '16 interior shires', PER16: '16 perimeter shires', UNI32: 'all 32 shires'};
const placeOf = name => { const [g, n] = name.split('@'); return `${PLACE[g] || g}, ${n} minions each`; };
const ucf = s => s.charAt(0).toUpperCase() + s.slice(1);
/* A card selector for one chart, shown only when there is a choice; returns a getter for the selected card. */
function dvCard(hostId, onChange) {
  const h = document.getElementById(hostId);
  if (DVC.length < 2) { const box = h.parentElement; h.remove(); if (box && !box.children.length) box.style.display = 'none'; return; }
  CK.cardSeg(hostId, {cards: DVC, bus: 'dvfs-dv2-card', value: DVC[0], onChange});
}
const dvRuns = c => DV.cards[c].runs.filter(r => r.kind === 'T' && r.valid);

/* The section's prose, from the first card with a night (aifoundry2). */
(function () {
  const N = DV.cards[DVC[0]], L = N.lines, Z = N.z1.filter(c => !c.skipped), skip = N.z1.filter(c => c.skipped);
  const nat = N.sessions.filter(s => s.kind === 'NAT');
  const tens = Z.filter(c => c.pass < 'p1100'), twos = Z.filter(c => c.pass >= 'p1100');
  V.dvIntro = `On the night of 27–28 September aifoundry2 ran the development half of a pre-registered design (DV2): ${Z.length} ` +
    `read-only watch cycles from ${hhmm(Z[0].time)} to ${hhmm(Z[Z.length - 1].time)} PDT and ${word(nat.length)} heating sessions. These runs ` +
    `chose the parameters and the rules of a validation plan that was frozen afterwards; they test nothing, and every number in this ` +
    `section is theirs. The validation began at 20:45 PDT on 28 September and is not yet reduced (the end of this section). The night ended with the card's Master Minion hung; ` +
    `a management reset restored it at 08:32 that morning.`;
  const and2 = xs => (xs.length > 1 ? xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1] : xs.join(''));
  const WHY = {'night stop': 'the night stop that ended the first session', 'slot passed': 'while a session held the card'};
  const skipBy = [...new Set(skip.map(c => c.reason))].map(r => `${and2(skip.filter(c => c.reason === r).map(c => c.slot))} ` +
    `(${WHY[r] || r || 'no record'})`);
  V.dvWatch = `${ucf(word(Z.length))} cycles: every 10 minutes from ${hhmm(tens[0].time)}, where ${word(skip.length)} slots did not run: ` +
    `${skipBy.join('; ')}; then every 2 minutes from ${hhmm(twos[0].time)} to ${hhmm(Z[Z.length - 1].time)}.`;
  const NOTE = {p6035: 'ended early by a rule set in advance, since from a start of 65 °C none of its four runs reached 800 MHz',
    p6038: 'three blocks of four runs, with the power-adder and reset runs around them',
    p6041: 'the Master Minion hung at its first run, below'};
  V.dvSessions = nat.map(s => `a ${s.branch} session at ${hhmm(s.start)}–${hhmm(s.end)}, from a rest of ${s.r0} °C (${NOTE[s.pass] || s.note})`).join('; ') +
    `; and a single 2 s launch at ${hhmm((N.sessions.find(s => s.kind === 'SMOKE') || {}).start)} to check the tools. A fourth kind of session, ` +
    `a 600 MHz placement run on a warm card, was skipped by its own rule: the card had rested at 64 °C or less within the hour`;
  // Q1
  const q = N.q1, sep = q.separating, fitM = sep.filter(r => r.fits_mean), off = sep.filter(r => !r.fits_mean && !r.fits_max);
  const dmm = fitM.map(r => r.down_minus_mean), dmh = sep.map(r => r.down_minus_high);
  const s0 = N.sessions.find(s => s.pass === (N.runs[0] || {}).session) || {};
  V.q1Text = (q.g1h.holds === q.T_runs ? `In all ${word(q.T_runs)} valid runs of the session at ${hhmm(s0.start)}` : `In ${word(q.g1h.holds)} of the ${word(q.T_runs)} valid runs of the session at ${hhmm(s0.start)}`) + `, the clock held 800 MHz for at least a ` +
    `second after the hottest sensor had risen to ${TC + 2} °C or more, up to ${TC + q.g1h.max_over_thr} °C; a rule on the hottest shire, ` +
    `acting at 66, would have stepped within about half a second of its first 66. ${ucf(word(sep.length))} runs, in ${word(q.blocks.length)} blocks, ` +
    `tell the two rules apart (the hottest sensor read 66 °C at least 1.5 s before the mean did): ${word(fitM.length)} of them stepped ` +
    `${range(Math.min(...dmm), Math.max(...dmm), 1)} s after the mean first read 66, and none near the hottest sensor's first 66; ` +
    `their steps came ${range(Math.min(...dmh), Math.max(...dmh), 1)} s after it. ` +
    (off.length ? `The ${off.length === 1 ? 'other' : 'others'} stepped ${off.map(r => f1(-r.down_minus_mean)).join(' and ')} s before our samples ` +
      `saw the mean at 66, which fits neither rule's window (the service processor reads the mean on its own pass, between our samples). ` : '') +
    `The frozen rule asks for at least six such runs over at least three blocks, so as a count this falls short of a test; its direction is all the mean's.`;
  const ic = q.idle_separating[0], cyc = ic ? Z.find(z => z.pass === ic.pass) : null;
  const before = cyc ? L.crossings.filter(c => c.host_ms < cyc.t_ms) : [], after = cyc ? L.crossings.filter(c => c.host_ms > cyc.t_ms) : [];
  const passMs = median(V3.sp_pass_ms[DVC[0]].quiet_ms);
  V.q1Idle = ic ? `<b>The idle card agrees.</b> At ${hhmm(ic.time)} its mean read ${ic.mean} °C while its hottest sensor read ` +
    `${range(ic.high_min, ic.high_max, 0)} °C in all ${word(ic.samples)} samples of that watch cycle. The governor had left its loop at ` +
    `${before.length ? before[before.length - 1].time : '?'} and did not enter it again until ${after.length ? after[0].time : '?'} (its trace ring); ` +
    `a rule on the hottest shire would have entered within one pass, about ${f0(passMs)} ms. That is one such cycle; the validation asks for ` +
    `five over three separate stretches.` : '';
  // Q2
  const g = N.q2, fin = g.blocks.filter(b => b.final_candidate && b.L != null), first = g.blocks.find(b => !b.final_candidate);
  const tx = (b, k) => (b['censored_' + k] ? 'at least ' : '') + f1(b['t800_' + k]) + ' s';
  V.q2Text = `From the same start, a mean falling to 62 °C, the same work on ${fin.length ? fin[0].minions : '?'} minions held 800 MHz ` +
    `${range(g.ratio[0], g.ratio[1], 1)} times as long before the first step when placed on the perimeter as when placed in the interior, ` +
    `in both blocks run under the final settings: ` + fin.map((b, k) => `${tx(b, 'int')}${k ? '' : ' interior'} against ${tx(b, 'per')}${k ? '' : ' perimeter'} in block ${b.block}` +
      (b.censored_per ? ', where the perimeter run held to its kernel’s end' : '')).join(', and ') + '. ' +
    `The mean log ratio is ${f2(g.L_mean)} (standard deviation ${f2(g.L_sd)} over ${word(g.n)} blocks), ${f2(g.L_P_mean)} after correcting for the ` +
    `two placements' slightly different power. ` + (first ? `On ${first.minions} minions (block ${first.block}) neither placement stepped within its launch. ` : '') +
    `Placement can act only through the mean (§1): spread over the perimeter, the same heat raises the 34-sensor mean more slowly. ` +
    `A heat-only model built on aifoundry3's placement runs of 27 September predicted ${f2(g.L_pred)} ± ${f2(g.b)}, below the development value; that ` +
    `comparison is reported, not registered. Its inputs are frozen as numbers in <code>plan/prereg-val.json</code>, and the ` +
    `placement runs they come from are the heat-placement experiment's development blocks (E52), in ` +
    `<a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-28-heat-placement/">docs/reports/data/2026-09-28-heat-placement</a> ` +
    `(<code>reductions/dev-r3.json</code>). Two blocks give no confidence interval; the frozen test asks for the log ratio above zero at 99% over ` +
    `at least ${word(g.g4s_min_blocks)} blocks.`;
  // the loop
  const th = L.thermal, en = th.filter(x => x.kind === 'ENTER'), ex = th.filter(x => x.kind === 'EXIT');
  const pr = a => [...new Set(a.map(x => x.T))].join(' and ');
  const lp = L.loop, kc = {}; lp.forEach(x => (kc[x.k] = (kc[x.k] || 0) + 1));
  const maxRes = Math.max(...lp.map(x => Math.abs(x.resid_ms)));
  const exI = L.exit_next.filter(x => x.idle), exP = exI.filter(x => x.next === 'PIDLE'), enI = L.enter_prev.filter(x => x.idle);
  const b = N.bands;
  V.loopText = `The trace ring shows the loop itself. All ${en.length} ENTER lines of the night (“Thermal throttle down event”) printed a mean ` +
    `of ${pr(en)} °C and all ${ex.length} EXIT lines (“Thermal idle state event”) ${pr(ex)} °C: no dead band. The ${lp.length} intervals under a ` +
    `minute from an ENTER to the EXIT after it (${lp.filter(x => x.idle).length} on the idle card, ${word(lp.filter(x => !x.idle).length)} at the start ` +
    `of a session) all lie within ${f1(maxRes)} ms of a whole number of ${f3(L.loop_period_s)} s periods: ` +
    Object.keys(kc).sort().map(k => `${kc[k]} at ${k}`).join(', ') + '. One period is the loop’s sleep of 1000 ticks, ' +
    `${V.tickLoop} s, plus its own work; zero periods mean the loop's first re-read found the mean back at 65. The September 2024 rewrite, ` +
    `stepping once per pass with no loop, cannot give that grid. Every idle EXIT was followed, as the next governor line, by the idle reset ` +
    `(${exP.length} of ${exI.length}, within ${f2(Math.max(...exP.map(x => x.dt_s)))} s, one pass), and ` +
    (enI.every(x => x.prev === 'PIDLE') ? `every idle ENTER with a line before it (${enI.length})` : `${enI.filter(x => x.prev === 'PIDLE').length} of the ${enI.length} idle ENTERs with a line before them`) +
    ` came straight after the service processor had itself called the card idle: the thermal branch does not wait ` +
    `for a kernel. On the host's 10 Hz samples the heating runs agree: all ${b['G2-C'].le1} of ${b['G2-C'].n} climbs from 600 MHz passed 700 MHz in ` +
    `at most one sample, the one-call climb, and all ${b['G2-D'].in_band} of ${b['G2-D'].n} descents to 600 MHz spent 0.3–0.7 s at 700 MHz ` +
    `(median ${f1(b['G2-D'].dwell_median_s)} s), one period.`;
  // the rest
  const zm = Z.map(c => c.mean), lo = Z.find(c => c.mean === Math.min(...zm)), hi = Z.find(c => c.mean === Math.max(...zm));
  const cr = L.crossings, res = N.residency, good = res.vs_episodes.filter(x => Math.abs(x.diff_ms) < 5), bad = res.vs_episodes.filter(x => Math.abs(x.diff_ms) >= 5);
  const hs = N.host_sensors, dd = us => us / 86400e6;
  V.tdDays = f2(dd(res.thermal_down.cumulative_us)); V.upDays = f2(res.uptime_days);
  V.restText = `Watched through the night with no work of ours, aifoundry2's idle mean moved between ${Math.min(...zm)} and ${Math.max(...zm)} °C ` +
    `within 10 to 30 minutes, and idle power followed it: ${f1(lo.board_w)} W at ${lo.mean} °C, ${f1(hi.board_w)} W at ${hi.mean} °C. What drives the ` +
    `swing is not established: the host's ACPI zones read a constant ${hs.acpi_1 ? f1(hs.acpi_1[0]) : '?'} and ${hs.acpi_2 ? f1(hs.acpi_2[0]) : '?'} °C (probably ` +
    `not live readings), its drive ${hs.nvme ? range(hs.nvme[0], hs.nvme[1], 0) : '?'} °C${hs.cpu_package ? ` and its CPU package ${range(hs.cpu_package[0], hs.cpu_package[1], 0)} °C` : ''}. Each time the mean crossed 65/66 °C the ring shows a burst of ENTER and EXIT ` +
    `lines, ${word(cr.length)} crossings in all, the governor flickering in and out of its loop for up to ${f1(Math.max(...cr.map(c => c.dur_s)))} s. ` +
    `Its residency counter, read at ${hhmm(res.at)}, had the card in the thermal state for ${V.tdDays} of the ${V.upDays} days since the service ` +
    `processor last started, the longest stay ${f1(dd(res.thermal_down.maximum_us))} days; across the ${word(good.length)} intervals whose episodes ` +
    `the ring kept${good.some(x => x.busy) ? ` (${word(good.filter(x => x.busy).length)} of them around a session's start)` : ''}, the counter grew by the episodes' length to within ${f1(Math.max(...good.map(x => Math.abs(x.diff_ms))))} ms` +
    (bad.length ? `, and across the ${word(bad.length)} that spanned a heating session, whose lines our sampler pushed out of the ring, ` +
      `it did not (by ${bad.map(x => f1(x.diff_ms / 1000) + ' s').join(' and ')})` : '') + '.';
  // the validation and the hang
  const P = DV.prereg, H = N.incident, l1 = H.lifts[0], l2 = H.lifts[1], h2 = H.lift2 || {};
  V.valG4 = `${f2(P.g4.L_pred)} ± ${f2(P.g4.b)} for the log ratio over at least ${word(P.g4.g4_min_blocks)} blocks; the prediction comes from ` +
    `aifoundry3's placement runs of 27 September, E52's development blocks, reduced in <code>docs/reports/data/2026-09-28-heat-placement/reductions/dev-r3.json</code>`;
  V.valText = `The plan was frozen at about 03:15 PDT on 28 September, after the last development pass, as ` +
    `<a href="https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/reports/data/2026-09-28-dvfs2-aifoundry2/plan/PREREG-VAL.md">PREREG-VAL.md</a> ` +
    `(SHA-256 <code>${P.sha256.slice(0, 12)}…</code>); a lock file (SHA-256 <code>${P.lock_sha256.slice(0, 12)}…</code>) fixes the code, the numbers and ` +
    `the schedules it runs, and every pass refuses to start if any of them has changed. It tests the step's trigger, the placement effect's sign, ` +
    `the loop, the absent dead band, the latencies and the residency counter, on the idle card and in heating sessions, each with a pass and a ` +
    `fail rule written before any validation data. Only aifoundry2's governor moves the clock (aifoundry3's is stuck, aifoundry1's card 1 does ` +
    `not act), so the validation is a replication on the same card in a later session. The owner accepted the same-card replication and ` +
    `chose the full schedule, idle watch and heating sessions (the Master Minion they need was restored at 08:32 on 28 September, below), ` +
    `and it started on aifoundry2 at 20:45:39 PDT on 28 September, after the plan's earliest start of ` +
    `${P.not_before.replace('2026-09-28T', '')}. Its NAT-4 replication ran the plan's limit of three heating sessions: p6051 (22:13–22:30 PDT, ` +
    `one block of four runs), p6052 (22:42–23:06, two blocks) and p6053 (23:19–23:56, four blocks), seven complete placement blocks where G4-S ` +
    `needs at least six. The Master Minion did not hang. The idle card read 73–75 °C from 20:45 to 21:09 PDT and 59 °C by 22:12, and ` +
    `73–74 °C again from 00:11 to 01:00 with no session running. The read-only watch cycles go on ` +
    `until about 16:45 PDT on 29 September, the end of the plan's 20-hour window, and the frozen reducer runs after that. <b>No item has a ` +
    `verdict yet</b>, so every number in this section is still the development night's.`;
  const sr = H.kernel_log || [], last = sr[sr.length - 1], KL = H.kernel_log_last || {};
  const c1 = l1.calib || {}, c2 = l2.calib || {}, st = l1.stream || {};
  V.hangText = `In the last session's first run, lift 1 ran normally. A lift is a stream of short kernels on all 32 shires ` +
    `lasting about 7 s: a ${f0(1000 * c1.wall_s)} ms calibration kernel, then ${word(st.kernels)} back-to-back kernels of ` +
    `${range(st.wall_s[0], st.wall_s[1], 2)} s. Lift 1's clock climbed to 800 MHz, and the device was held for ` +
    `${f2(parseFloat((l1.message || '').replace(/[^0-9.]/g, '')))} s. Lift 2 was launched ${f1(l2.gap_s)} s after lift 1 ended, with the clock still at ` +
    `${h2.mhz_at_start} MHz; ${f2(h2.first_600_s)} s later, at ${h2.first_600_at}, the host read the idle reset's 600 MHz, and the device was ready ` +
    `${f2(l2.ready_s)} s after the launch. Lift 2's calibration kernel then ran, ${f0(h2.calib_after_first_600_ms)} ms after that reading, at ${c2.start}, ` +
    `and returned ${c2.ok ? 'normally' : 'an error'}, measuring ${f2(c2.ghz)} GHz, between the two points, as if the clock changed while it ran. The next ` +
    `kernel, the first of the stream, never completed: from ${f1(h2.board_idle_from_s)} s the board read the ${f0(l2.board_w[0])} W idle and the clock stayed at ` +
    `${(h2.mhz_after_1s || []).join(', ')} MHz, until the heater gave up (“${l2.message}”). Lifts 3 and 4 failed at runtime creation ` +
    `(“Couldn't use the HPSQ. Perhaps the Master Minion is hanged?”). The host's kernel log has an SP runtime-error event for the card ` +
    (last ? `at ${(KL.pdt || '').slice(0, 10)} (±${f2(KL.pm_s)} s, its boot-relative stamp mapped to wall time; ${f1(KL.after_lift2_calib_end_s)} s after the ` +
      `calibration kernel ended): “${last.desc}, ${last.syndrome}”, the counter's ${['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh'][sr.length] || f0(sr.length) + 'th'}. ` +
      `The first ${word(sr.length - 1)}, on ${dayList(sr.slice(0, -1).map(e => (e.pdt || '').slice(0, 10)))}, did not stop the card, so the event ` +
      `need not be the hang's` : '') +
    `. The service processor still answered: at ${H.sp_after.map(x => hhmm(x.time)).join(' and ')} it read ${[...new Set(H.sp_after.map(x => x.mhz.join('/')))].join('/')} MHz, ` +
    `${range(Math.min(...H.sp_after.map(x => x.board_w)), Math.max(...H.sp_after.map(x => x.board_w)), 1)} W, a mean of ` +
    `${range(Math.min(...H.sp_after.map(x => x.mean)), Math.max(...H.sp_after.map(x => x.mean)), 0)} °C and its threshold at ${H.sp_after[0].threshold_c} °C. ` +
    `No reset was attempted that night (the card rules). At 06:39 the sysfs per-card reset re-attached the device but left the Master Minion ` +
    `hung (launches at 06:40 and 06:47 failed the same way); at 08:32, with the owner's approval, the management reset ` +
    `(<code>DM_CMD_RESET_ETSOC</code>) restored it, and a test on one minion then ran three launches, each ok, at 600 MHz ` +
    `(<a href="https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/reports/data/2026-09-28-dvfs2-aifoundry2/incident/recovery.txt"><code>incident/recovery.txt</code></a>). ` +
    `The cause is not established. The ${H.launches_before} heater launches before it that night all ran, among them ${b['G2-C'].n} climbs ` +
    `and ${b['G2-D'].n} full descents of the clock; that this one met the clock change is a hypothesis, and the plan's heating sessions launch ` +
    `the same way, a risk it states.`;
  V.dvFits = `${L.offset_fits} fits within ${f1(L.offset_spread_ms_max)} ms; one fit made from a single request line, ` +
    `${L.offset_fits_dropped_s.map(v => f0(Math.abs(v))).join(', ')} s off the others, is set aside here, which the frozen reducer does not do`;
  V.hbMed = f2(L.heartbeat.median_s); V.hbN = f0(L.heartbeat.n);
})();

/* V9 (§8, Q1): one run at a time, the clock, the mean and the hottest sensor, with the three moments the rules turn on. */
(function () {
  let card;
  const st = {k: 0};
  const runs = () => dvRuns(card);
  const pick = () => { const R = runs(), k = R.findIndex(r => r.block === 2 && r.name.startsWith('B4C')); return k < 0 ? 0 : k; };
  const read = CK.readout('q1-read');
  let seg;
  const mkSeg = () => { const R = runs();
    seg = CK.seg('q1-run', {label: 'Run', options: R.map((r, k) => [k, `b${r.block} ${r.name}`]), value: st.k, onChange: v => { st.k = v; frame.redraw(); }}); };
  card = DVC[0];
  dvCard('q1-card', v => { card = v; st.k = pick(); mkSeg(); frame.redraw(); strip.redraw(); });
  st.k = pick(); mkSeg();
  legendHTML('q1-leg', [{mark: 'line', color: 'var(--c1)', label: 'minion clock'},
    {mark: 'line', color: 'var(--c7)', label: 'mean of the 34 shire sensors (the governor’s input)'},
    {mark: 'line', color: 'var(--c5)', w: 1.6, label: 'hottest sensor (peak since the reset at 63 °C)'},
    {mark: 'dash', color: 'var(--bad)', label: `the governor acts above ${TC} °C`}]);
  function draw(f) {
    const r = runs()[st.k], T = r.tel, n = T.t.length, W = f.W, H = f.H, svg = f.svg;
    const L = 46, R = 12, B = 34, top = 34, gap = 26;
    const avail = H - top - B - gap, hc = avail * 0.28, hT = avail - hc, c0 = top, T0 = c0 + hc + gap, bot = T0 + hT;
    const tEnd = k => (k + 1 < n ? T.t[k + 1] : T.t[n - 1] + 0.1);
    const x = CK.lin(T.t[0], tEnd(n - 1), L, W - R);
    const vals = T.mean.concat(T.high).filter(v => v != null);
    const lo = Math.min(...vals, TC) - 0.5, hi = Math.max(...vals, TC + 1) + 0.5;
    const yc = CK.lin(FMIN - 45, FMAX + 45, c0 + hc, c0), yT = CK.lin(lo, hi, bot, T0);
    // outside the launch
    for (const [a, z] of [[T.t[0], 0], [r.t_end, tEnd(n - 1)]]) if (z > a) CK.el('rect', {x: x(a), y: c0, width: x(z) - x(a), height: bot - c0, fill: 'var(--ref)', opacity: 0.12}, svg);
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    const hline = (y, lab) => { CK.el('line', {x1: L, x2: W - R, y1: y, y2: y, class: 'grid-line'}, g); if (lab != null) CK.txt(g, L - 6, y + 4, lab, 'tick', 'end'); };
    for (const o of OPS) hline(yc(o.mhz), f0(o.mhz));
    const every = hT / (hi - lo) >= 16 ? 1 : 2;
    for (let v = Math.ceil(lo); v <= hi; v++) hline(yT(v), v % every === 0 ? f0(v) : null);
    CK.el('line', {x1: L, x2: W - R, y1: bot, y2: bot, class: 'ck-axis'}, g);
    const step = (x.domain[1] - x.domain[0]) / Math.max(2, (W - L - R) / 60) > 1 ? 2 : 1;
    for (let s = Math.ceil(T.t[0]); s <= tEnd(n - 1); s++) if (s % step === 0) CK.txt(g, x(s), bot + 16, f0(s), 'tick', 'middle');
    CK.txt(g, (L + W - R) / 2, H - 4, 'seconds since the launch (shaded: no kernel running)', 'lab', 'middle');
    CK.txt(g, 2, 12, 'minion clock, MHz', 'lab');
    CK.txt(g, 2, T0 - 9, 'die temperature, °C (whole degrees)', 'lab');
    CK.el('line', {x1: L, x2: W - R, y1: yT(TC + 0.5), y2: yT(TC + 0.5), stroke: 'var(--bad)', 'stroke-width': 1.3, 'stroke-dasharray': '5 4'}, svg);
    const stairs = (a, y) => { let d = '', pen = false;
      a.forEach((v, k) => { if (v == null) { pen = false; return; } d += `${pen ? 'L' : 'M'}${x(T.t[k]).toFixed(1)},${y(v).toFixed(1)}L${x(tEnd(k)).toFixed(1)},${y(v).toFixed(1)}`; pen = true; }); return d; };
    CK.el('path', {d: stairs(T.mhz, yc), fill: 'none', stroke: 'var(--c1)', 'stroke-width': 2, 'stroke-linejoin': 'round'}, svg);
    CK.el('path', {d: stairs(T.mean, yT), fill: 'none', stroke: 'var(--c7)', 'stroke-width': 2.2, 'stroke-linejoin': 'round'}, svg);
    CK.el('path', {d: stairs(T.high, yT), fill: 'none', stroke: 'var(--c5)', 'stroke-width': 1.6, 'stroke-linejoin': 'round'}, svg);
    // the three moments: a thin line through both panels and a mark above the clock panel
    const M = [['t_hi', 'var(--c5)', 'diamond', 'the hottest sensor first reads 66 °C at 800 MHz'], ['t_m', 'var(--c7)', 'dot', 'the mean first reads 66 °C'],
      ['t_down', 'var(--ink)', 'down', 'the clock steps 800→700 MHz']].filter(m => r[m[0]] != null);
    const nodes = M.map(([k, c, shape, what], j) => {
      const cx = x(r[k]), cy = c0 - 12 - (j % 2) * 0;
      CK.el('line', {x1: cx, x2: cx, y1: c0 - 4, y2: bot, stroke: c, 'stroke-width': k === 't_down' ? 1.6 : 1.2, opacity: 0.9}, svg);
      const node = shape === 'down' ? CK.el('polygon', {points: `${cx - 6},${cy - 5} ${cx + 6},${cy - 5} ${cx},${cy + 6}`, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.2}, svg)
        : shape === 'diamond' ? CK.el('polygon', {points: `${cx},${cy - 6} ${cx + 6},${cy} ${cx},${cy + 6} ${cx - 6},${cy}`, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.2}, svg)
        : CK.el('circle', {cx, cy, r: 5.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.2}, svg);
      CK.tip(f, node, `<b>${f2(r[k])} s</b>: ${what}`);
      return node;
    });
    CK.keynav(f, nodes);
    const held = r.t_down == null;
    read.set(`<b>Block ${r.block} · ${r.name}</b> (${placeOf(r.name)}, ${num(r.minions, 0)} minions; ${hhmm(r.time)} PDT, development): ` +
      `800 MHz ${f1(r.t_up)} s after the launch; the hottest sensor read 66 °C at ${f1(r.t_hi)} s` + (r.t_hi2 != null ? ` and 67 at ${f1(r.t_hi2)} s` : '') + '; ' +
      (held ? `the mean ${r.t_m == null ? 'never read 66 within the launch' : `read 66 at ${f1(r.t_m)} s`}, and the clock held 800 MHz to the kernel's end at ${f1(r.t_end)} s: ` +
          `${f1(r.t_end - r.t_up)} s at 800 MHz, a run held to the end.`
        : `the mean read 66 at ${f1(r.t_m)} s and the clock stepped at ${f1(r.t_down)} s, ${sgn(+(r.t_down - r.t_m).toFixed(2), 1)} s from the mean's first 66 ` +
          `and ${sgn(+(r.t_down - r.t_hi).toFixed(2), 1)} s from the hottest sensor's: ${f1(r.trip_s)} s at 800 MHz.`));
  }
  const frame = CK.frame('q1', {height: W => (W < 600 ? 340 : 320), minW: 280, maxW: 640, draw,
    label: 'One development run at 800 MHz: the minion clock, the 34-sensor mean and the hottest sensor, sample by sample, with the moments the two rules turn on'});

  // the strip: every separating run's step, against each reading's first 66 °C
  legendHTML('q1s-leg', [{mark: 'dot', color: CK.card(card).color, label: 'one run that tells the rules apart'},
    {mark: 'shade', color: 'var(--ref)', op: 0.3, label: 'where a rule on that reading steps (−0.3 to +0.6 s)'}]);
  function drawS(f) {
    const S = DV.cards[card].q1.separating, W = f.W, H = f.H, svg = f.svg, L = 14, R = 14, B = 36, top = 4;
    const vals = S.flatMap(r => [r.down_minus_mean, r.down_minus_high]).filter(v => v != null);
    const x = CK.lin(Math.min(-1.5, Math.floor(Math.min(...vals))), Math.ceil(Math.max(...vals)) + 0.5, L, W - R);
    const rows = [['down_minus_mean', 'after the mean first read 66 °C'], ['down_minus_high', 'after the hottest sensor first read 66 °C']];
    const rh = (H - top - B) / 2, [w0, w1] = DV.cards[card].q1.window_s;
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    for (const t of x.ticks(Math.max(3, Math.round((W - L - R) / 70)))) { CK.el('line', {x1: x(t), x2: x(t), y1: top, y2: H - B, class: 'grid-line'}, g); CK.txt(g, x(t), H - B + 16, sgn(t, 0), 'tick', 'middle'); }
    CK.el('line', {x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ck-axis'}, g);
    CK.txt(g, (L + W - R) / 2, H - 4, 'seconds from that reading’s first 66 °C to the step', 'lab', 'middle');
    const nodes = [];
    rows.forEach(([k, lab], i) => {
      const y0 = top + i * rh, yc = y0 + 20 + (rh - 24) / 2;
      CK.el('rect', {x: x(w0), y: y0 + 20, width: x(w1) - x(w0), height: rh - 24, fill: 'var(--ref)', opacity: 0.22}, svg);
      CK.el('line', {x1: x(0), x2: x(0), y1: y0 + 20, y2: y0 + rh - 4, stroke: 'var(--ink-2)', 'stroke-width': 1.3}, svg);
      const t = CK.txt(svg, L, y0 + 13, lab, 'lab-strong');
      Object.assign(t.style, {paintOrder: 'stroke', stroke: 'var(--page)', strokeWidth: '4px', strokeLinejoin: 'round'});
      const pts = S.filter(r => r[k] != null).map(r => ({r, v: r[k], px: x(r[k])})).sort((a, b) => a.v - b.v), last = {};
      for (const p of pts) { for (let j = 0; ; j++) { const lane = j % 2 ? -(j + 1) / 2 : j / 2; if (last[lane] == null || p.px - last[lane] >= 12) { p.lane = lane; last[lane] = p.px; break; } } }
      for (const p of pts) {
        const m = CK.cardMark(svg, card, p.px, yc + p.lane * 10, 4.5);
        CK.tip(f, m, `<b>Block ${p.r.block} · ${p.r.name}</b> (development): the step came ${sgn(p.r.down_minus_mean, 1)} s from the mean's first 66 °C ` +
          `and ${sgn(p.r.down_minus_high, 1)} s from the hottest sensor's` + (p.r.fits_mean ? '' : '; it fits neither window'));
        nodes.push(m);
      }
    });
    CK.keynav(f, nodes);
  }
  const strip = CK.frame('q1s', {height: 216, minW: 280, maxW: 640, draw: drawS,
    label: 'For each development run that tells the two rules apart, the time from the mean’s first 66 °C to the step, and from the hottest sensor’s first 66 °C to the step'});
  const S0 = DV.cards[card].q1;
  document.getElementById('q1s-cap').textContent = `Each mark is one of the ${word(S0.separating.length)} runs, in ${word(S0.blocks.length)} blocks, in which the ` +
    `hottest sensor read 66 °C at least 1.5 s before the mean did. A rule on a reading predicts the step inside that reading's shaded window; ` +
    `the steps line up with the mean and come seconds after the hottest sensor. Development counts (the frozen rule needs six runs over three blocks).`;
})();

/* V10 (§8, Q2): time at 800 MHz before the first step, interior against perimeter, per block, beside the placements' map. */
(function () {
  const COL = {INT16: 'var(--c4)', PER16: 'var(--c7)'};
  let card = DVC[0];
  dvCard('q2-card', v => { card = v; frame.redraw(); });
  legendHTML('q2-leg', [{mark: 'shade', color: COL.INT16, op: 0.85, label: 'interior: 16 shires (INT16)'}, {mark: 'shade', color: COL.PER16, op: 0.85, label: 'perimeter: 16 shires (PER16)'},
    {mark: 'box', color: 'var(--ink-2)', hollow: true, label: 'held 800 MHz to the kernel’s end (at least)'}]);
  const P = DV.placements, grp = {};
  for (const k of ['INT16', 'PER16']) for (const s of P.groups[k]) grp['S' + s] = k;
  const B4 = new Set(P.groups.B4C.map(s => 'S' + s));
  function draw(f) {
    const q = DV.cards[card].q2, W = f.W, H = f.H, svg = f.svg, wide = W >= 560;
    const mapS = wide ? 22 : 20, mapW = mapS * 6, mapH = mapS * 6;
    const mx = wide ? 8 : Math.round((W - mapW) / 2), my = 20;
    CK.txt(svg, wide ? mx : W / 2, 12, 'shires on the die (inferred grid)', 'lab', wide ? 'start' : 'middle');
    P.grid.forEach((row, i) => row.forEach((c, j) => {
      const k = grp[c], x0 = mx + j * mapS, y0 = my + i * mapS;
      const rect = CK.el('rect', {x: x0 + 1, y: y0 + 1, width: mapS - 2, height: mapS - 2, rx: 2, fill: k ? COL[k] : 'var(--grid)', opacity: k ? 0.85 : 1}, svg);
      if (B4.has(c)) CK.el('rect', {x: x0 + 2.5, y: y0 + 2.5, width: mapS - 5, height: mapS - 5, rx: 2, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 1.6}, svg);
      if (!k) Object.assign(CK.txt(svg, x0 + mapS / 2, y0 + mapS / 2 + 4, c.startsWith('IO') ? 'IO' : c, 'tick', 'middle').style, {fontSize: '11px', fill: 'var(--ink)'});
      rect.setAttribute('aria-hidden', 'true');
    }));
    CK.txt(svg, mx, my + mapH + 14, 'outlined: B4C, the 4 central', 'tick');
    // the bars
    const L0 = wide ? mx + mapW + 28 : 12, T0 = wide ? 20 : my + mapH + 30, R = 60, B = 36;
    const blocks = q.blocks, rowH = (H - T0 - B) / blocks.length, barH = Math.min(14, rowH / 3.4);
    const tmax = Math.ceil(Math.max(...blocks.flatMap(b => [b.t800_int, b.t800_per])) + 0.5);
    const x = CK.lin(0, tmax, L0, W - R);
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    for (let t = 0; t <= tmax; t++) { CK.el('line', {x1: x(t), x2: x(t), y1: T0, y2: H - B, class: 'grid-line'}, g); if (t % (tmax > 8 ? 2 : 1) === 0) CK.txt(g, x(t), H - B + 16, f0(t), 'tick', 'middle'); }
    CK.el('line', {x1: L0, x2: W - R, y1: H - B, y2: H - B, class: 'ck-axis'}, g);
    CK.txt(g, (L0 + W - R) / 2, H - 4, 'seconds at 800 MHz before the first step', 'lab', 'middle');
    const nodes = [];
    blocks.forEach((b, i) => {
      const y0 = T0 + i * rowH;
      CK.txt(svg, L0, y0 + 12, `block ${b.block} · ${num(b.minions, 0)} minions` + (b.final_candidate ? '' : ' (dropped: both held)'), 'lab-strong');
      [['int', 'INT16', b.int], ['per', 'PER16', b.per]].forEach(([k, grpK, name], j) => {
        const t = b['t800_' + k], cen = b['censored_' + k], yb = y0 + 18 + j * (barH + 4);
        const rect = CK.el('rect', {x: x(0), y: yb, width: Math.max(2, x(t) - x(0)), height: barH, rx: 3,
          fill: cen ? 'var(--surface)' : COL[grpK], stroke: COL[grpK], 'stroke-width': cen ? 2 : 0}, svg);
        if (cen) CK.el('polygon', {points: `${x(t) + 1},${yb} ${x(t) + 8},${yb + barH / 2} ${x(t) + 1},${yb + barH}`, fill: COL[grpK]}, svg);
        CK.txt(svg, x(t) + (cen ? 11 : 5), yb + barH - 2, (cen ? '≥ ' : '') + f1(t) + ' s', 'tick');
        CK.tip(f, rect, `<b>Block ${b.block} · ${name}</b> (${placeOf(name)}; development): ${cen ? 'held 800 MHz to its kernel’s end, at least ' : ''}${f2(t)} s at 800 MHz before the first step`);
        nodes.push(rect);
      });
      if (b.L != null) CK.txt(svg, W - 4, y0 + 18 + barH + 6, '×' + f2(Math.exp(b.L)) + (b.censored_per || b.censored_int ? '+' : ''), 'lab-strong', 'end');
    });
    CK.keynav(f, nodes);
  }
  const q = DV.cards[card].q2;
  const frame = CK.frame('q2', {height: W => (W < 560 ? 176 + 36 + 62 * q.blocks.length : Math.max(190, 56 + 62 * q.blocks.length)), minW: 280, maxW: 640, draw,
    label: 'Development: seconds at 800 MHz before the first step for interior and perimeter placement, block by block, beside a map of the two placements'});
  document.getElementById('q2-cap').innerHTML = `Right-hand figures: perimeter over interior time, per block (+: the perimeter run held to its kernel's end, so at least that). ` +
    `The map is the shire grid as inferred for the die frame (<code>tools/claims-v3/dv2/placements.json</code>); the governor sees neither, only the 34-sensor mean. ` +
    `Mean log ratio over the ${word(q.n)} blocks under the final settings ${f2(q.L_mean)} (development; the frozen reducer gives ${f2(q.reducer_L_mean)}).`;
})();

/* V11 (§8, the loop): every ENTER -> EXIT interval under a minute, against whole periods of the loop, and its residual. */
(function () {
  let card = DVC[0];
  dvCard('loop-card', v => { card = v; frame.redraw(); });
  legendHTML('loop-leg', [{mark: 'dot', color: CK.card(card).color, label: 'idle card'}, {mark: 'ring', color: 'var(--ref)', label: 'at the start of a session'},
    {mark: 'dash', color: 'var(--ink-2)', label: 'whole periods of the loop'}]);
  const L = 20, R = 16, top = 26, B = 36, gap = 50, STEP = 11, LANE = 8;
  // the residual strip's lanes at a given width: marks closer than 9 px stack upwards
  const lanes = (lp, W) => {
    const rmax = Math.max(2, Math.ceil(Math.max(...lp.map(q => Math.abs(q.resid_ms))))), xr = CK.lin(-rmax, rmax, L, W - R), last = {};
    const out = [...lp].sort((a, b) => a.resid_ms - b.resid_ms).map(q => { const px = xr(q.resid_ms); let k = 0;
      while (last[k] != null && px - last[k] < 9) k++; last[k] = px; return {q, px, lane: k}; });
    return {xr, rmax, out, n: Math.max(...out.map(o => o.lane)) + 1};
  };
  const colMax = lp => Math.max(...Object.values(lp.reduce((m, q) => ((m[q.k] = (m[q.k] || 0) + 1), m), {})));
  const geom = W => { const lp = DV.cards[card].lines.loop, hTop = 16 + colMax(lp) * STEP, ln = lanes(lp, W);
    return {lp, hTop, ln, H: top + hTop + gap + 14 + ln.n * LANE + B}; };
  function draw(f) {
    const Lz = DV.cards[card].lines, P = Lz.loop_period_s, W = f.W, H = f.H, svg = f.svg, G = geom(W), lp = G.lp;
    const kmax = Math.max(...lp.map(x => x.k)), y1 = top + G.hTop, y2t = y1 + gap, y2 = H - B;
    const x = CK.lin(-0.08, (kmax + 0.35) * P, L, W - R);
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    for (let k = 0; k <= kmax; k++) {
      CK.el('line', {x1: x(k * P), x2: x(k * P), y1: top - 6, y2: y1, stroke: 'var(--ink-2)', 'stroke-width': 1.2, 'stroke-dasharray': '4 3'}, g);
      CK.txt(g, x(k * P), y1 + 15, k ? `${k} × ${f3(P)} s` : '0', 'tick', 'middle');
    }
    CK.el('line', {x1: L, x2: W - R, y1, y2: y1, class: 'ck-axis'}, g);
    CK.txt(g, 2, 12, 'ENTER → EXIT interval, service-processor time', 'lab');
    const nodes = [], byK = {};
    lp.forEach(q => (byK[q.k] = byK[q.k] || []).push(q));
    Object.keys(byK).sort((a, b) => a - b).forEach(k => byK[k].sort((p, q) => q.idle - p.idle || p.d_s - q.d_s).forEach((q, j) => {
      const cx = x(q.d_s), cy = y1 - 7 - j * STEP;
      const m = q.idle ? CK.cardMark(svg, card, cx, cy, 4.5) : CK.el('circle', {cx, cy, r: 4, fill: 'var(--surface)', stroke: 'var(--ref)', 'stroke-width': 2}, svg);
      CK.tip(f, m, `<b>${q.time} PDT</b>${q.idle ? '' : ', at the start of a session'}: ENTER → EXIT ${f3(q.d_s)} s = ${q.k} × ${f3(P)} s ${sgn(q.resid_ms, 2)} ms (development)`);
      nodes.push(m);
    }));
    // the residuals, on their own scale
    const {xr, rmax, out} = G.ln;
    CK.txt(g, 2, y2t - 12, 'distance from the nearest whole period, ms', 'lab');
    for (let v = -rmax; v <= rmax; v++) { CK.el('line', {x1: xr(v), x2: xr(v), y1: y2t, y2, class: 'grid-line'}, g); CK.txt(g, xr(v), y2 + 16, sgn(v, 0), 'tick', 'middle'); }
    CK.el('line', {x1: L, x2: W - R, y1: y2, y2, class: 'ck-axis'}, g);
    CK.el('line', {x1: xr(0), x2: xr(0), y1: y2t, y2, stroke: 'var(--ink-2)', 'stroke-width': 1.2}, svg);
    for (const o of out) {
      const cy = y2 - 6 - o.lane * LANE;
      const m = o.q.idle ? CK.cardMark(svg, card, o.px, cy, 3.5) : CK.el('circle', {cx: o.px, cy, r: 3, fill: 'var(--surface)', stroke: 'var(--ref)', 'stroke-width': 1.8}, svg);
      m.setAttribute('aria-hidden', 'true');
    }
    CK.keynav(f, nodes);
  }
  const frame = CK.frame('loopq', {height: W => geom(W).H, minW: 280, maxW: 640, draw,
    label: 'Development: every interval under a minute between the governor\u2019s ENTER and EXIT lines, against whole periods of its thermal loop, with each interval\u2019s distance from the nearest period'});
  const P = DV.cards[card].lines.loop_period_s, th = DV.cards[card].lines.thermal;
  document.getElementById('loop-cap').textContent = `Upper: one mark per interval, stacked where they coincide; the dashed lines are whole periods of ${f3(P)} s. ` +
    `Lower: the same intervals' distance from the nearest period, in milliseconds (the frozen validation allows 15 ms). Every line of the night printed ` +
    ['ENTER', 'EXIT'].map(k => { const a = th.filter(x => x.kind === k); return `${[...new Set(a.map(x => x.T))].join(' or ')} °C on ${k === 'ENTER' ? 'entry' : 'exit'} (${a.length} lines)`; }).join(' and ') + '.';
})();

/* V12 (§8, the night): the idle mean and hottest sensor at each watch cycle, the governor's crossings, the sessions. */
(function () {
  let card = DVC[0];
  dvCard('night-card', v => { card = v; frame.redraw(); });
  legendHTML('night-leg', [{mark: 'dot', color: CK.card(card).color, label: 'idle mean at a watch cycle'},
    {mark: 'line', color: 'var(--c5)', label: 'up to the hottest sensor in that second'},
    {mark: 'up', color: 'var(--ink-2)', label: 'into the loop (warming past 66)'}, {mark: 'down', color: 'var(--ink-2)', hollow: true, label: 'out of it (cooling past 65)'},
    {mark: 'shade', color: 'var(--ref)', label: 'a heating session of ours'}, {mark: 'dash', color: 'var(--bad)', label: `the governor acts above ${TC} °C`}]);
  function draw(f) {
    const N = DV.cards[card], Z = N.z1.filter(c => !c.skipped), C = N.lines.crossings, S = N.sessions.filter(s => s.status !== 'skipped' && s.t0_ms);
    const hang = N.incident.lifts[1] && N.incident.lifts[1].t_start_ms;
    const W = f.W, H = f.H, svg = f.svg, L = 40, R = 14, T = 30, B = 38;
    const ts = Z.map(c => c.t_ms).concat(C.map(c => c.host_ms), S.flatMap(s => [s.t0_ms, s.t1_ms]));
    const x = CK.lin(Math.min(...ts) - 5 * 60e3, Math.max(...ts) + 5 * 60e3, L, W - R);
    const ys = Z.flatMap(c => [c.mean, c.high_max]);
    const y = CK.lin(Math.min(...ys, TC) - 2, Math.max(...ys) + 1, H - B, T);
    // sessions first, under everything
    const nodes = [];
    for (const s of S) {
      const a = x(s.t0_ms), w = Math.max(3, x(s.t1_ms) - a);
      const r = CK.el('rect', {x: a, y: T, width: w, height: H - B - T, fill: 'var(--ref)', opacity: 0.2}, svg);
      CK.tip(f, r, `<b>${s.branch || s.kind} (${s.pass})</b>, ${hhmm(s.start)}–${hhmm(s.end)} PDT: start reading ${s.r0 == null ? '—' : s.r0 + ' °C'}, ${s.launches} launches` +
        (s.status === 'ok' ? '' : `; ${s.pass === 'p6041' ? 'the Master Minion hung' : 'ended early'}`));
      nodes.push(r);
      if (w > 24 && s.branch) CK.txt(svg, a + w / 2, T - 6, s.branch, 'tick', 'middle');
    }
    const g = CK.el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, svg);
    for (let v = Math.ceil(y.domain[0]); v <= y.domain[1]; v++) if (v % 2 === 0) { CK.el('line', {x1: L, x2: W - R, y1: y(v), y2: y(v), class: 'grid-line'}, g); CK.txt(g, L - 6, y(v) + 4, f0(v), 'tick', 'end'); }
    CK.el('line', {x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ck-axis'}, g);
    const first = Math.ceil(x.domain[0] / 1800e3) * 1800e3;
    const every = (W - L - R) / ((x.domain[1] - x.domain[0]) / 1800e3) < 60 ? 2 : 1;
    for (let t = first, k = 0; t <= x.domain[1]; t += 1800e3, k++) if (k % every === 0) CK.txt(g, x(t), H - B + 16, PDT(t), 'tick', 'middle');
    CK.txt(g, (L + W - R) / 2, H - 4, 'time of night, PDT, 27–28 September', 'lab', 'middle');
    CK.txt(g, 2, 12, 'die temperature at idle, °C', 'lab');
    CK.el('line', {x1: L, x2: W - R, y1: y(TC + 0.5), y2: y(TC + 0.5), stroke: 'var(--bad)', 'stroke-width': 1.3, 'stroke-dasharray': '5 4'}, svg);
    if (hang) { CK.el('line', {x1: x(hang), x2: x(hang), y1: T, y2: H - B, stroke: 'var(--bad)', 'stroke-width': 1.6}, svg);
      CK.txt(svg, x(hang) - 4, H - B - 8, 'hang', 'lab-strong', 'end'); }
    const items = [];
    for (const c of Z) items.push({t: c.t_ms, draw: () => {
      CK.el('line', {x1: x(c.t_ms), x2: x(c.t_ms), y1: y(c.mean), y2: y(c.high_max), stroke: 'var(--c5)', 'stroke-width': 2}, svg);
      const m = CK.cardMark(svg, card, x(c.t_ms), y(c.mean), 4.5);
      CK.tip(f, m, `<b>${c.time} PDT</b> (watch cycle, development): mean ${c.mean} °C, hottest sensor ${range(c.high_min, c.high_max, 0)} °C, ` +
        `board ${f1(c.board_w)} W, ${c.mhz.join('/')} MHz` + (c.state ? `; the ring puts the governor ${c.state === 'IN' ? 'in' : 'out of'} its loop` : ''));
      return m; }});
    for (const c of C) items.push({t: c.host_ms, draw: () => {
      const cx = x(c.host_ms), cy = y(TC + 0.5), up = c.ends === 'ENTER';
      const m = CK.el('polygon', {points: up ? `${cx - 6},${cy + 5} ${cx + 6},${cy + 5} ${cx},${cy - 6}` : `${cx - 6},${cy - 5} ${cx + 6},${cy - 5} ${cx},${cy + 6}`,
        fill: up ? 'var(--ink-2)' : 'var(--surface)', stroke: 'var(--ink-2)', 'stroke-width': 1.6}, svg);
      CK.tip(f, m, `<b>${c.time} PDT</b>: the mean crossed ${up ? '66 °C warming' : '65 °C cooling'}${c.idle ? '' : ' (at the start of a session)'}; ` +
        `${c.enter} ENTER and ${c.exit} EXIT lines over ${f2(c.dur_s)} s, ending ${up ? 'in' : 'out of'} the loop`);
      return m; }});
    items.sort((a, b) => a.t - b.t).forEach(it => nodes.push(it.draw()));
    CK.keynav(f, nodes);
  }
  const frame = CK.frame('night', {height: W => (W < 600 ? 300 : 320), minW: 280, maxW: 640, draw,
    label: 'Development: aifoundry2 through the night of 27–28 September: the idle mean and hottest sensor at each watch cycle, the governor’s threshold crossings from its trace ring, and the heating sessions'});
  const N = DV.cards[card], hs = N.host_sensors;
  document.getElementById('night-cap').textContent = `Each dot is one watch cycle's 1 s sample (its median mean); the line above it reaches the hottest sensor's ` +
    `peak in that second. Triangles are the bursts of governor lines in the trace ring, at host time (the ring's clock mapped through the host's ` +
    `own requests). The host's own sensors (${hs.samples} readings, ${hhmm(hs.from)}–${hhmm(hs.to)}) are not drawn: see the text.`;
})();

/* ---------- the body's computed fields ---------- */
(function () {
  const ic = D.idle_check, upT = UP.map(r => r.T), first = D.transition_summary.first_change_s;
  Object.assign(V, {
    hours: f1(ic.hours_idle),
    upT: range(Math.min(...upT), Math.max(...upT), 0, ' to '),
    ntrans: f0(TR.length),
    ndown: f0(DOWN.length),
    ops: OPS.map((o, k) => `${o.mhz}${k ? '' : ' MHz'} at ${num(o.volts, 3)}${k ? '' : ' V'}`).join(', '),
    prevsplit: `${nOf(byBefore, 'thermal')} thermal, ${nOf(byBefore, 'thermal+power')} above both thresholds and ${nOf(byBefore, 'unattributed')} unattributed`,
    // what moves between the two readings: power readings that appear only after the step, and die readings just before it
    prevwhy: (() => {
      const lag = DOWN.filter(r => r.why === 'thermal+power' && r.why_prev === 'thermal');
      const hot = DOWN.filter(r => r.why === 'unattributed' && r.why_prev === 'thermal');
      const parts = [];
      if (lag.length) parts.push(`the ${lag.map(r => f1(r.P)).join(' and ')} W readings (run${lag.length > 1 ? 's' : ''} ` +
        `${lag.map(r => r.run + 1).join(' and ')}) appear only after their step, because the board meter lags the clock`);
      if (hot.length) parts.push(`${word(hot.length)} step${hot.length > 1 ? 's' : ''} counted as unattributed ` +
        `(${hot.map(r => `run ${r.run + 1}, ${r.values}, at ${f2(r.t)} s`).join('; ')}) read ${[...new Set(hot.map(r => f0(r.T_prev)))].join(' and ')} °C on the sample before`);
      return parts.join(', and ');
    })(),
    prevnote: `taking the sample just before each step instead of just after gives ${nOf(byBefore, 'thermal')} thermal, ` +
      `${nOf(byBefore, 'thermal+power')} thermal+power and ${nOf(byBefore, 'unattributed')} unattributed (against ${nOf(byAfter, 'thermal')}, ` +
      `${nOf(byAfter, 'thermal+power')} and ${nOf(byAfter, 'unattributed')})`,
    first: range(Math.min(...first), Math.max(...first), 2, ' to '),
    direct10: `${ucf(word(UP.filter(r => r.f0 === FMIN && r.f1 === FMAX).length))} of the ${UP.length}`,
  });
  // the governor on aifoundry2 over two days (D.governor_days): every cool-start session of 21 and 23 September
  const upAll = Object.values(G.up_T), nUp = upAll.reduce((a, u) => a + u.n, 0), fc = G.first_change_s, gp = G.change_gap_s;
  const rs = G.reset, ml = G.meter_lag_s, bd = Object.entries(G.boundaries);
  // aifoundry2's SP pass while ettelem samples at 10 Hz, as it did in every session timed here (TEL-P3, 26 September:
  // about 160 ms; 133 ms with no sampler, TEL-P1)
  const PASS = median(V3.sp_pass_ms.aifoundry2.e10_ms) / 1000;
  const bText = ([k, v], i) => { const [day, cls] = k.split(' ');
    const gap = cls === '<=10ms' ? '1–2 ms' : cls === '100-300ms' ? 'about 0.2 s' : cls === '10-100ms' ? '10–100 ms' : 'over 0.3 s';
    const where = (v.sessions < 3 ? `in ${word(v.sessions)} session${v.sessions === 1 ? '' : 's'} ` : '') +   // n in words below three
      `on ${dayList([day])}, with ${gap} between launches, `;
    return where + (i === 0 ? `${v.drop_800_600} of the ${v.n} launch boundaries crossed with the clock above ${FMIN} MHz dropped it to the boot point`
      : `${v.drop_800_600} of ${v.n} did`); };
  Object.assign(V, {
    up66: `of ${f0(nUp)} up-steps on ${dayList(G.days)}, ${word(upAll.reduce((a, u) => a + u.above_65_both, 0))} read ` +
      `${Math.max(...upAll.map(u => u.max))} °C on both neighbouring samples, and none read higher`,
    hunt: `${word(G.sessions.length)} sessions on ${dayList(G.days)}, ${f0(G.changes)} clock changes`,
    firstMed: f1(fc.median), firstR: range(fc.min, fc.max, 2, ' to '), firstN: f0(fc.n), firstPasses: word(Math.round(fc.median / PASS)),
    gapMed: f1(gp.median), gapR: range(gp.p10, gp.p90, 1, ' to '), gapPasses: word(Math.round(gp.median / PASS)),
    direct: `${f0(G.sessions.reduce((a, x) => a + x.direct_600_800, 0))} of ${f0(nUp)} over both days`,
    resetMed: f1(rs.settle_s.median), resetR: range(rs.settle_s.min, rs.settle_s.max, 1, ' to '), resetN: word(rs.settle_s.n),
    resetUp: word(rs.up_after_end), resetEnds: f0(rs.block_ends),
    bnd: bd.map(bText).join('; '),
    splitRms: range(...LAW.span(f => D.leak_split.ends.find(e => e.T_L === f.T_L).rms_W), 2),
    splitRms0: f2(D.leak_split.central_refit.rms_W),
    meterLag: `about ${f1(ml.median)} s (${range(ml.min, ml.max, 1, ' to ')} s at ${f0(ml.n)} up-steps on ${dayList(G.days)})`,
  });
  document.querySelectorAll('[data-v]').forEach(e => {
    const k = e.getAttribute('data-v');
    if (V[k] == null) throw new Error('dvfs-leakage: no value for data-v="' + k + '"');
    e.innerHTML = V[k];
  });
})();
