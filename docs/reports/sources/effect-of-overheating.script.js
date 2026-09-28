/* The effect of overheating. Every ET number comes from D (overheat.json, written by
   docs/reports/data/2026-09-28-overheating/build_overheat_data.py from E53's reductions, the analyses of the existing
   record and the arithmetic of scripts/derived.py). Outside numbers are in the prose with their sources. Citations are
   span.cite elements with a data-s list of source keys: numbered here by first appearance, outside sources [1..n], the ET's own [E1..].
   Charts use the shared toolkit CK (tokens only); cards come from the data (CK.cardsIn), never a fixed list. */
const $ = id => document.getElementById(id);
const num = CK.fmt.num, V = {};
const f0 = v => num(v, 0), f1 = v => num(v, 1), f2 = v => num(v, 2), f3 = v => num(v, 3);
const lab = c => CK.card(c).label;
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const andL = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
const rng = (a, b, f) => { const s = f(a), t = f(b); return s === t ? s : `${s}–${t}`; };
const minmax = a => [Math.min(...a), Math.max(...a)];
const sgn = v => (v > 0 ? '+' : '') + num(v, 0);
const code = p => `<code>${esc(p)}</code>`;
const an = n => { const t = String(Math.round(Math.abs(n))); return t[0] === '8' || t === '11' || t === '18' ? 'an' : 'a'; };   // "an 82 °C", "a 76 °C"
const ucf = s => s.charAt(0).toUpperCase() + s.slice(1);
const WCLS = {PASS: 'pass', FAIL: 'fail', INSUFFICIENT: 'insufficient'};
const word = w => w == null ? '<span class="word nt">not testable</span>' : `<span class="word ${WCLS[w] || 'nt'}">${esc(w)}</span>`;
const kind = k => `<span class="kind">${k}</span>`;
const OHC = CK.cardsIn(D.verdicts.cards);                  // the cards E53 ran on
const RAILC = CK.cardsIn(D.rails);                         // the cards whose rails are on record
const IDLEC = CK.cardsIn(D.idle);

/* ---------- citations: numbered by first appearance ---------- */
const SRC = {}; D.sources.forEach(s => { SRC[s.key] = s; });
const NUMS = {}, ORDER = {outside: [], et: []};
function numOf(k) {
  const s = SRC[k];
  if (!s) { console.error('effect-of-overheating: unknown source ' + k); return null; }
  if (NUMS[k] == null) { ORDER[s.group].push(k); NUMS[k] = (s.group === 'et' ? 'E' : '') + ORDER[s.group].length; }
  return NUMS[k];
}
const citeInner = keys => '[' + keys.split(',').map(k => k.trim()).filter(Boolean)
  .map(k => `<a href="#src-${k}">${numOf(k) || '?'}</a>`).join(', ') + ']';
const cite = keys => keys ? `<span class="cite" data-s="${keys}"></span>` : '';   // numbered by numberCites, in page order
const numberCites = root => (root || document).querySelectorAll('.cite[data-s]').forEach(e => {
  if (!e.dataset.done) { e.innerHTML = citeInner(e.getAttribute('data-s')); e.dataset.done = '1'; } });

/* ---------- the numbers the prose needs ---------- */
(function () {
  const fw = D.fw, g = D.gap, dv = D.derived, pk = D.peaks, c0 = D.card0, t = D.timing, cr = D.correct;
  V.nOut = f0(D.sources.filter(s => s.group === 'outside').length);
  V.fwThr = f0(fw.threshold_c); V.fwAct = f0(fw.acts_at_c); V.fwSensors = V.fwSensors2 = f0(fw.sensors);
  V.fwBuild2 = `BL2 ${esc(fw.build)}`;
  V.fwPmic = f0(fw.pmic_c); V.fwSafe = f0(fw.safe_mhz);
  // each card's build and what its governor does (14-card-behaviour.md), and the SP's own readouts (the DVFS page's data)
  const B = D.builds, SPR = D.sp_readouts, bc = c => B[c];
  const byBuild = {};
  CK.cardsIn(Object.keys(B).filter(k => k !== 'src')).forEach(c => { (byBuild[bc(c).bl2] = byBuild[bc(c).bl2] || []).push(c); });
  V.fwBuilds = Object.entries(byBuild).map(([bl2, cs]) => `${andL(cs.map(lab))} ${cs.length > 1 ? 'run' : 'runs'} release ` +
      `${esc(bc(cs[0]).release)} (BL2 ${esc(bl2)})`).join('; ') +
    ` (${code(B.src)}). The public source closest to 0.20.0 is et-platform ${code(fw.commit)}, read here.`;
  const c1s = SPR['aifoundry1-c1'];
  V.fwGov = `Of our cards it acts only on aifoundry2. On aifoundry3 the zero power limit set by a boot service latches the ` +
    `governor, and it makes no thermal step at any temperature. Card 1's 0.18.0 build held ${f0(c1s.sp_mhz_min)} MHz in all ` +
    `${f0(c1s.samples)} samples of the three-card check, by the service processor's own minimum and maximum of the clock, busy or ` +
    `idle, up to ${an(c1s.die_mean_max)} ${f0(c1s.die_mean_max)} °C mean. Card 0's 0.21.2 governor acts only while a kernel runs and ` +
    `idles at 300 MHz; after reading 115–117 °C on 25 September the card did leave 600 MHz for 300 MHz, whether by that idle point ` +
    `or by its PMIC's safe state is not established (${code(B.src)}; ${code('docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json')}).`;
  const sprC = CK.cardsIn(Object.keys(SPR)), sprN = sprC.reduce((a, c) => a + SPR[c].pmic_temp_samples, 0),
    sprNZ = sprC.reduce((a, c) => a + SPR[c].pmic_temp_nonzero, 0);
  V.sysC = `the service processor reads it only when its statistics are reset and feeds the statistic a literal 0 on every ` +
    `other pass ${cite('et-thermal-c')}, and that statistic read ${sprNZ ? 'non-zero ' + f0(sprNZ) + ' times in' : '0 in all'} ${f0(sprN)} ` +
    `samples of the three-card check (${andL(sprC.map(lab))}) and ${c0.system_c.every(v => v === 0) ? '0' : c0.system_c.map(f0).join(', ')} ` +
    `in all ${f0(c0.guard_samples)} of card 0's guard samples ${kind('measured')}.`;
  V.a2W = f1(D.gap.a2_p11.peak_board_w);
  V.pmicW = `aifoundry2's board reached ${f1(D.gap.a2_p11.peak_board_w)} W in its 90–103 °C catalogue pass and stayed at 600 MHz ` +
    `with no safe state (${code(B.src)}) ${kind('measured')}.`;

  // mean against hottest at the governor's point
  const at = m => g.near65.filter(r => r.mean === m);
  const span = m => { const rs = at(m); return {lo: Math.min(...rs.map(r => r.min)), hi: Math.max(...rs.map(r => r.max)),
    med: rs.map(r => r.median), n: rs.reduce((a, r) => a + r.n, 0)}; };
  const s65 = span(65), s66 = span(66);
  const medTxt = s => { const u = [...new Set(s.med)]; return u.length === 1 ? f0(u[0]) : u.map(f0).join(' and '); };
  V.near65 = `when the mean reads ${f0(fw.threshold_c)} °C, the hottest sensor reads ${rng(s65.lo, s65.hi, f0)} °C (median ` +
    `${medTxt(s65)}); at ${f0(fw.acts_at_c)} °C, the first reading the 0.20.0 rule acts on, it reads ${rng(s66.lo, s66.hi, f0)} °C ` +
    `(median ${medTxt(s66)}). From ${f0(g.near65_windows)} one-second windows on ${andL(OHC.map(lab))} ${kind('measured')}. ` +
    `These are statistics of the sensors: neither card's governor acts (section 1.3).`;
  const ld = code => g.load.filter(r => r.code === code);
  const gl = codes => { const rs = codes.flatMap(ld); const md = minmax(rs.map(r => r.median)), mx = Math.max(...rs.map(r => r.max));
    return `median ${md[0] === md[1] ? sgn(md[0]) : sgn(md[0]) + ' to ' + sgn(md[1])} (max ${sgn(mx)})`; };
  V.gapLoad = `idle ${gl(['IDLE'])}; one shire at full load ${gl(['ONE-C', 'ONE-NE'])}; the central 2 × 2 block ${gl(['B4C'])}; ` +
    `the whole-chip heater ${gl(['HEAT'])}. In all ${f0(g.oh1_windows)} OH-1 windows the largest gap was ${sgn(g.oh1_max)} °C, ` +
    `and all three OH-1 verdicts pass (section 7). One shire's 0.9 W barely moves its own sensor above the others.`;
  const a3 = g.oh2d.aifoundry3 || null;
  const nAll = g.temp.reduce((a, r) => a + r.n, 0);
  const band = (c, b) => g.oh2d[c] && g.oh2d[c].bands[b] ? g.oh2d[c].bands[b].median : null;
  const growC = OHC.filter(c => g.oh2d[c] && g.oh2d[c].growth != null);
  V.gapTemp = (growC.length ? growC.map(c => `under the whole-chip heater on ${lab(c)} the median gap went from ` +
      `${sgn(band(c, '60-70'))} at 60–70 °C to ${sgn(band(c, '80-85'))} at 80–85 °C`).join('; ') : '') +
    ` (registered: 0 or +1; PASS). Over all ${f0(nAll)} OH-2 windows, rests and batteries included, +4 occurred ${f0(g.n4_total)} times ` +
    `(${OHC.map(c => `${lab(c)} ${f0(g.n4[c])}`).join(', ')}) and +5 ${g.n5 ? f0(g.n5) + ' times' : 'never'}.`;
  const p11 = g.a2_p11;
  V.gapWorst = `aifoundry2's hottest catalogue pass peaked at ${an(p11.max_mean_c)} ${f0(p11.max_mean_c)} °C mean with one sensor at ` +
    `${f0(p11.max_hottest_c)} °C (at its highest board power, ${f1(p11.peak_board_w)} W, the mean read ${f0(p11.mean_c_at_peak)} ` +
    `and the hottest ${f0(p11.hottest_c_at_peak)}); card 0's standing peak-holds are ${an(c0.sp_mean_max)} ${f0(c0.sp_mean_max)} °C mean and a ` +
    `${f0(c0.sensor_peak_hold)} °C sensor (not necessarily at the same moment). Heat-placement's 1 s windows (E52) never passed ` +
    `${sgn(g.e52_max)}, and DV2's runs (E51) ${sgn(Math.min(...Object.values(g.e51).map(x => x.min)))} to ` +
    `${sgn(Math.max(...Object.values(g.e51).map(x => x.max)))}.`;
  V.ohMaxA3 = `a mean of ${f0(Math.max(...OHC.map(c => D.oh_max[c].mean)))}`;
  V.density = `at aifoundry2's highest board power the metered core, SRAM and mesh rails drew ${f1(p11.rails_w)} W, ` +
    `${f2(p11.rails_w_per_mm2)} W/mm² over the 570 mm² die ${cite('ditzel-hc33')}; a loaded A100 runs about 0.40 W/mm² of board ` +
    `power (${code('docs/findings/13-why-low-power.md')}), and the literature's large gaps come from dense CPU and GPU units.`;
  V.softmax = f1(dv.softmax_width_C['0.9']);
  V.teff = dv.teff_34_regions_at_90C.map(r => f1(r.effective)).join(', ') + ' °C, while the means are ' +
    rng(dv.teff_34_regions_at_90C[0].mean, dv.teff_34_regions_at_90C[3].mean, f1) + ' °C and the maxima ' +
    rng(dv.teff_34_regions_at_90C[0].max, dv.teff_34_regions_at_90C[3].max, f0) + ' °C';
  const tr = dv.lognormal_tail.rows, tt = h => tr.filter(r => r.hot_by === h).map(r => r.times_design);
  V.tail = `one region 10 °C hotter gives ${rng(Math.min(...tt(10)), Math.max(...tt(10)), f1)} times as many failures by the ` +
    `design life, a 3 °C gap ${rng(Math.min(...tt(3)), Math.max(...tt(3)), f1)} times ${kind('derived')}; the lifetimes are ` +
    `taken as lognormal, as electromigration's are ${cite('hauschildt')}, with spreads (σ 0.3 and 0.5) assumed.`;
  V.dilution = f0(dv.dilution_local_rise_per_1C_of_mean['1']);

  const w1 = OHC.map(c => { const a = g.load.find(r => r.card === c && r.code === 'ONE-C'), b = g.load.find(r => r.card === c && r.code === 'IDLE');
    return a && b ? a.board_w - b.board_w : null; }).filter(v => v != null);
  V.shireW = `${rng(Math.min(...w1), Math.max(...w1), f1)} W over idle by the board meter`;
  V.hot66 = rng(s66.lo, s66.hi, f0);
  V.cost = V.cost2 = `about ${medTxt({med: at(66).map(r => r.median - 66)})} °C (${rng(s66.lo - 66, s66.hi - 66, f0)})`;
  // peaks
  const pr = c => pk[c] ? `${lab(c)} ${an(pk[c].mean)} ${f0(pk[c].mean)} °C mean with one sensor at ${f0(pk[c].high)} °C` : '';
  V.peaksText = `${pr('aifoundry2')}, in a whole catalogue pass run at a 90–103 °C mean, all at 600 MHz, in which nothing tripped ` +
    `(${code('docs/findings/14-card-behaviour.md')}); ${['aifoundry3', 'aifoundry1-c1'].filter(c => pk[c]).map(pr).join('; ')}; and ` +
    `aifoundry1 card 0, whose cooling failed on 25 September, ${an(c0.sp_mean_max)} ${f0(c0.sp_mean_max)} °C mean with one sensor at ${f0(c0.sensor_peak_hold)} °C ` +
    `(section 4.4). Scanned from ${f0(Object.values(pk).reduce((a, p) => a + p.samples, 0))} telemetry samples ` +
    `(${code('docs/reports/data/2026-09-28-overheating/analysis/max_temps.json')}).`;

  // rails
  const rs = k => RAILC.map(c => D.rails[c][k].median);
  const mv = v => f0(v) + ' mV';
  V.railsText = `the cores' rail reads ${RAILC.map(c => `${mv(D.rails[c].minion.median)} (${lab(c)})`).join(', ')} on the die; ` +
    `the mesh ${rng(Math.min(...rs('noc')), Math.max(...rs('noc')), f0)} mV; the SRAM arrays ${rng(Math.min(...rs('sram')), Math.max(...rs('sram')), f0)} mV ` +
    `(medians of every idle sample at 600 MHz in the September check). At 800 MHz, which aifoundry2 reaches only below about 68 °C, ` +
    `the cores run at ${f0(D.fw.mv_800)} mV (${code('docs/findings/16-dvfs-and-leakage.md')}).`;
  const rv = minmax(rs('minion'));
  V.ansRail = `${num(rv[0] / 1000, 2)}–${num(rv[1] / 1000, 2)} V`;
  V.ansRail2 = V.ansRail;

  // work per cycle and the clock
  const c1w = t.c1_warm, catp = t.catalogue.passes;
  const hotT = minmax(catp.H.map(p => p[1])), warmT = minmax(catp.W.map(p => p[1]));
  V.cyclesText = `on aifoundry3 every one of ${f0(t.oh2b_a3_n)} kernel metrics (tensor multiply-adds in fp32, fp16 and int8 at ` +
    `several sparsities, a GEMV, two matmul benchmarks, the DRAM and mesh relays) took the same cycles at an 80–85 °C mean as at ` +
    `rest, to within ${num(t.oh2b_a3_max_abs, 3)}% (the registered limit was 0.1%: OH2-b PASS). Card 1 never got hotter than a ` +
    `${f0(D.oh_max['aifoundry1-c1'].mean)} °C mean, so its registered test is INSUFFICIENT; at 70–80 °C ${f0(c1w.n_within_0p1pct)} of ` +
    `${f0(c1w.n_metrics)} of its metrics were within 0.1% of rest, and the DRAM relay was ${num(c1w.items['K7-relay-dram'].diff_pct, 2)}% off, ` +
    `inside that kernel's own ${num(t.oh2b_a3['K7-relay-dram'].rest_spread_pct, 2)}% launch-to-launch spread at rest. Before E53, ` +
    `the heater's ${f3(t.heater_prior_cpo[0])} cycles per operation held from ${f0(t.heater_prior_range_c[0])} to ` +
    `${f0(t.heater_prior_range_c[1])} °C on ${t.heater_prior_cards.length === 3 ? 'three' : f0(t.heater_prior_cards.length)} cards, and aifoundry2's catalogue did the same work per cycle ` +
    `hot (${rng(hotT[0], hotT[1], f0)} °C) as warm (${rng(warmT[0], warmT[1], f0)} °C): median ${num(t.catalogue.median_pct, 2)}%, range ` +
    `${num(t.catalogue.min_pct, 2)} to +${num(t.catalogue.max_pct, 2)}% over ${f0(t.catalogue.n_configs)} configurations.`;
  const cc = Object.entries(t.oh2c), ghz = minmax(cc.map(([k, v]) => v.ghz_median));
  const bands = minmax(cc.flatMap(([k]) => k.split(' ')[1].split('-').map(Number)));
  V.clockText = `the heater's implied clock was ${num(ghz[0], 4)}–${num(ghz[1], 4)} GHz in every 5 °C band from ${f0(bands[0])} to ` +
    `${f0(bands[1])} °C (OH2-c, PASS on both cards). A phase-locked loop sets the clock; heat does not move it.`;
  const dr = (c, k) => { const o = D.droop[c]; const ks = Object.keys(o).filter(x => x.startsWith(k + ' ')).sort();
    return [o[ks[0]].median, o[ks[ks.length - 1]].median]; };
  const drT = c => `${f0(dr(c, 'minion')[0])} → ${f0(dr(c, 'minion')[1])} mV on ${lab(c)}`;
  V.droopText = `from 50–55 °C to each card's hottest band the cores' rail on the die moved ${OHC.map(drT).join(' and ')}; ` +
    `the SRAM ${OHC.map(c => `${f0(dr(c, 'sram')[0])} → ${f0(dr(c, 'sram')[1])}`).join(' and ')} mV; the mesh ` +
    `${OHC.map(c => `${f0(dr(c, 'noc')[0])} → ${f0(dr(c, 'noc')[1])}`).join(' and ')} mV ${kind('measured')}.`;
  const bad = cr.prior_bad;
  V.dvfsFail = `${bad.length === 2 ? 'two' : f0(bad.length)} DRAM relay launches with wrong elements on ${andL([...new Set(bad.map(b => lab(b.card)))])} ` +
    `at ${an(Math.min(...bad.map(b => b.mean_c)))} ${rng(Math.min(...bad.map(b => b.mean_c)), Math.max(...bad.map(b => b.mean_c)), f0)} °C mean (23 September), both while ` +
    `the governor stepped the clock from 800 to 600 MHz inside the launch (${code('docs/findings/16-dvfs-and-leakage.md')}); ` +
    `aifoundry2's Master Minion hang of 28 September also came at a clock step, at a 60–62 °C mean (${code('docs/findings/05-claims.md')}).`;
  V.ansCycles = `On our cards the cycles per operation at an 80–85 °C mean matched rest to within ${num(t.oh2b_a3_max_abs, 2)}%.`;

  // DRAM refresh
  V.fwRefresh = `${f0(D.fw.refresh_dfi_clocks)} memory-controller clocks at ${f0(D.fw.ddr_dfi_mhz)} MHz, ${num(D.fw.refresh_us, 3)} µs, which is ` +
    `${f1(D.fw.refresh_cycles_600)} cycles of the 600 MHz core clock ${cite('et-ddr')}`;
  const rf = Object.entries(D.refresh);
  V.refreshText = `E53 measured exactly that period with the memory probe: ${f1(rf[0][1].best_period)} cycles in every pass, at die means of ` +
    `${andL(rf.map(([k, v]) => f0(v.die_mean) + ' °C').sort())} (OH2-e, PASS; the hot-end passes ran at ` +
    `${andL(rf.filter(([k, v]) => v.band === 'B4').map(([k, v]) => `${f0(v.die_mean)} °C on ${lab(k.split(' ')[0])}`))}, below the band's ` +
    `82 °C target), as the September check did on three cards (${code('docs/findings/05-claims.md')}).`;

  // correctness
  const oh = cr.oh_hottest, hot = OHC.reduce((a, c) => (oh[c].mean_c > oh[a].mean_c ? c : a), OHC[0]);
  const b8085 = cr.oh_8085[hot];
  const priorChk = cr.cells.reduce((a, x) => a + x.prior_checked, 0);
  const a2p = cr.prior_hottest.aifoundry2;
  V.corrText = `<b>Not in anything that was checked.</b> In E53, <b>${f0(cr.oh_checked)} exact-checked launches</b> ` +
    `(${f0(cr.oh_records)} compared results: tensor multiply-adds, a GEMV, two matmul benchmarks, the DRAM and mesh relays with ` +
    `element-by-element checks, a cross-shire scratchpad probe; the stopped attempts included) returned <b>${f0(cr.oh_bad)} wrong ` +
    `results, tensor-unit errors or failed launches</b>, the hottest at ${an(oh[hot].mean_c)} ${f0(oh[hot].mean_c)} °C mean with a sensor at ` +
    `${f0(oh[hot].high_c)} °C (${lab(hot)}; ${f0(b8085.checked)} launches at 80–85 °C, which put the failure rate there below 1 in ` +
    `${f0(1 / b8085.upper95_per_launch)} with 95% confidence) ${kind('measured')}. The DRAM relay, never checked above 66 °C ` +
    `before, now is to ${f0(oh[hot].mean_c)} °C. In the September record, ${f0(cr.prior_launches_telemetry)} launches joined to ` +
    `telemetry, ${f0(priorChk)} of them with their results checked, the only wrong results were the two at a clock step ` +
    `(section 3.2); aifoundry2's matmul checks passed up to ${an(a2p.mean_c)} ${f0(a2p.mean_c)} °C mean. Its hottest catalogue pass (91–103 °C) ` +
    `completed on every core, but that catalogue checks no arithmetic.`;

  // card 0 and the 120 C story
  const r25 = c0.reported_25sep;
  V.card0Text = `aifoundry1's card 0 overheated on 25 September, a cooling fault: after about ten minutes of short tests it read ` +
    `${rng(r25.hot_c[0], r25.hot_c[1], f0)} °C with nothing running and drew ${rng(r25.hot_idle_w[0], r25.hot_idle_w[1], f0)} W at ` +
    `600 MHz, until it dropped to 300 MHz and cooled; whether its 1.4.1 build's idle point or its PMIC's safe state did that is not ` +
    `established (${code(r25.src)}). Its service processor's statistics, never ` +
    `reset since, still hold a highest mean of ${f0(c0.sp_mean_max)} °C, one sensor at ${f0(c0.sensor_peak_hold)} °C and the I/O ` +
    `shire at ${f0(c0.io_peak_hold)} °C. Watched read-only through E53 (${f0(c0.guard_samples)} samples), it idles at ` +
    `${rng(c0.mean_range[0], c0.mean_range[1], f0)} °C and ${rng(c0.board_w_range[0], c0.board_w_range[1], f1)} W at ` +
    `${f0(c0.mhz[0])} MHz and ${rng(c0.minion_mv[0], c0.minion_mv[1], f0)} mV. At the same operating point before the episode it drew ` +
    `${rng(r25.idle_w[0], r25.idle_w[1], f1)} W at a die temperature that was not recorded, so the comparison is loose: no sign of ` +
    `damage in what can be read, but not strong evidence against it. What its kernels computed at those temperatures is not in the ` +
    `repository.`;
  V.ansCard0 = `aifoundry1 card 0 overheated in September: its statistics still hold ${an(c0.sp_mean_max)} ${f0(c0.sp_mean_max)} °C mean with one sensor ` +
    `at ${f0(c0.sensor_peak_hold)} °C, and today it answers every query and idles at about the power it drew before.`;
  const ex = IDLEC.map(c => D.idle[c].e44.extrapolated_w['116']);
  const t88 = IDLEC.map(c => D.idle[c].t_matmul_88w).filter(x => x != null);
  V.powerText = `Leakage is current drawn from the same supplies as the work. At ${rng(r25.hot_c[0], r25.hot_c[1], f0)} °C card 0's ` +
    `whole board drew ${rng(r25.hot_idle_w[0], r25.hot_idle_w[1], f0)} W with nothing running (its fixed part plus leakage), and it did ` +
    `not stop; the other three cards' September idle laws extrapolate to ` +
    `${andL(ex.map(f0))} W at 116 °C. A random-data matmul on all 1,024 cores adds about 27.2 W (a flip-count estimate, ` +
    `${code('docs/findings/12-heat-management.md')}), so the same work there would ask ${rng(dv.hot_idle_plus_matmul_w[0], dv.hot_idle_plus_matmul_w[1], f0)} W ` +
    `of a card whose 12 V input is rated ${f0(dv.card_input_max_w)} W (${code('docs/research/power-telemetry.md')}); by the idle laws such ` +
    `work would reach ${f0(dv.card_input_max_w)} W at a mean of about ${rng(Math.min(...t88), Math.max(...t88), f0)} °C, depending on the card ` +
    `${kind('derived, extrapolated')}. aifoundry2's hottest pass already drew ${f1(p11.peak_board_w)} W at ${an(p11.mean_c_at_peak)} ${f0(p11.mean_c_at_peak)} °C mean. ` +
    `A current limit or a brown-out would stop the card and clear itself as it cooled and drew less; what this card's hot-swap ` +
    `controller and regulators actually do at their limits is not established.`;
  V.ansPower = `at ${rng(r25.hot_c[0], r25.hot_c[1], f0)} °C card 0's whole board drew ${rng(r25.hot_idle_w[0], r25.hot_idle_w[1], f0)} W ` +
    `with nothing running, its fixed part plus leakage, and did not stop; a full matmul on top would ask ` +
    `${rng(dv.hot_idle_plus_matmul_w[0], dv.hot_idle_plus_matmul_w[1], f0)} W of a card whose input is rated ${f0(dv.card_input_max_w)} W ` +
    `${kind('derived')}. A PCIe link that drops is another candidate.`;
  V.pcieText = `Card 0's link already logs about one corrected receive error per second at its root port, at a rate that changes ` +
    `from boot to boot (${code('docs/findings/14-card-behaviour.md')}) ${kind('measured')}. A link's transceivers recover the clock ` +
    `from the data with oscillators whose frequency drifts with temperature, like any PLL's ${cite('adi-pll')}; if heat took ` +
    `away the rest of that margin, the host would lose the card until the link retrained or the host rebooted, and the card ` +
    `would look fine once cool ${kind('inference')}.`;
  const allMed = minmax(g.load.map(r => r.median));
  V.ansGap = `in E53's second-by-second readings the hottest sensor ran typically ${rng(allMed[0], allMed[1], f0)} °C above the mean, ` +
    `+4 in ${f0(g.n4_total)} of ${f0(nAll)} windows and never more, so where the 0.20.0 rule acts it fires when the hottest sensor reads about ` +
    `${rng(s66.lo, s66.hi, f0)} °C. The bigger gap is elsewhere: on the 0.20.0 and 0.18.0 builds nothing limits the temperature ` +
    `once the clock is at 600 MHz.`;

  // lifetime
  const ap = dv.af_pairs, h65 = pk.aifoundry2 ? pk.aifoundry2.high : null;
  V.ansHour = rng(ap['0.7']['65->117'], ap['0.9']['65->117'], f0);
  V.arrText = `At 0.7–0.9 eV, an hour at 117 °C wears a chip like ${rng(ap['0.7']['85->117'], ap['0.9']['85->117'], f1)} hours at 85 °C, or ` +
    `${rng(ap['0.7']['65->117'], ap['0.9']['65->117'], f0)} hours at 65 °C; at aifoundry2's hottest sensor, ${f0(h65)} °C, the rate is ` +
    `${rng(ap['0.7']['65->106'], ap['0.9']['65->106'], f0)} times the 65 °C rate ${kind('derived')}. The 3 °C between the ET's mean and its ` +
    `hottest sensor near the 0.20.0 rule's point is worth ${rng(ap['0.7']['66->69'], ap['0.9']['66->69'], f2)} times. TI's own table is steeper ` +
    `than Arrhenius above 105 °C: 0.30 of the life at 120 °C ${cite('ti-lifetime')}, as if the activation energy were ` +
    `${f1(dv.ti_equiv_Ea_eV['120'])} eV ${kind('derived')}.`;
  const hr = e => minmax(Object.values(dv.halving_rise_C[e]));
  V.halving = `The “life halves every 10 °C” rule matches activation energies of about 0.7–0.9 eV, where life halves every ` +
    `${rng(Math.min(hr('0.7')[0], hr('0.9')[0]), Math.max(hr('0.7')[1], hr('0.9')[1]), f0)} °C between 60 and 120 °C; at 0.5 eV it ` +
    `halves every ${rng(hr('0.5')[0], hr('0.5')[1], f0)} °C ${kind('derived')}.`;
  const cm = dv.coffin_manson;
  V.ansCycle = rng(cm.damage_ratio['2'], cm.damage_ratio['2.35'], f1);
  V.cycleText = `RAMP models the cycles to failure with the Coffin–Manson law, falling as the swing to the power 2.35 for the ` +
    `package ${cite('ramp')}; JEDEC uses a power of 2 for solder joints, qualifies parts with 700 cycles from −55 to +125 °C with none ` +
    `allowed to fail, and takes a desktop's use as 2,000 swings of 40 °C in five years ${cite('jesd47')}. By those laws one swing from ` +
    `${f0(cm.from_c)} to ${f0(cm.hot_c)} °C and back fatigues the joints ${V.ansCycle} times as much as one to ${f0(cm.ref_c)} °C ` +
    `${kind('derived')}. The ET cards' own cycles (boots, resets, heating runs) are not counted anywhere.`;
  V.wp221 = f1(dv.wp221_doubling_C);

  // idle power and runaway
  const dbl = [];
  IDLEC.forEach(c => { dbl.push(D.idle[c].e44.fit.doubling_C); if (D.idle[c].oh3) dbl.push(D.idle[c].oh3.b.best.doubling_C); });
  V.ansDouble = rng(Math.min(...dbl), Math.max(...dbl), f0);
  const i3 = D.idle.aifoundry3 && D.idle.aifoundry3.e44;
  const oh3c = IDLEC.filter(c => D.idle[c].oh3);
  V.idleText = (i3 ? `On aifoundry3 idle board power rose from ${f1(i3.bins[0].board_w)} W at ${f0(i3.bins[0].T)} °C to ` +
    `${f1(i3.bins[i3.bins.length - 1].board_w)} W at ${f0(i3.bins[i3.bins.length - 1].T)} °C in September's cooling runs. ` : '') +
    `By each card's fit the leakage part doubles every ${IDLEC.map(c => `${f1(D.idle[c].e44.fit.doubling_C)} °C (${lab(c)})`).join(', ')} ` +
    `${kind('measured, fitted')}. E53's idle stretches still follow those laws: every whole degree within ` +
    `${num(Math.max(...oh3c.map(c => D.idle[c].oh3.a.max_abs_diff)), 2)} W of the card's law (OH3-a PASS), and a refitted doubling of ` +
    `${oh3c.map(c => `${f1(D.idle[c].oh3.b.best.doubling_C)} °C on ${lab(c)}`).join(' and ')} (OH3-b PASS).`;
  const ra = D.runaway, eq = ra.equilibria;
  V.runawayText = `Can it run away? The feedback is strong: in aifoundry2's lumped thermal model each degree of leakage heating ` +
    `returns ${f2(ra.model.loop_gain_at_80)} of a degree at 80 °C, and the loop gain passes 1 at ${f1(ra.gain_one_at_c)} °C; but the same ` +
    `model, with its afternoon ambient, has no stable temperature at all, which every cooling run on record contradicts, so it ` +
    `cannot place a runaway point ${kind('derived')}. No card on record ran away: card 0 cooled from 104 to 78 °C in eight minutes ` +
    `after its drop to 300 MHz (${code('docs/findings/14-card-behaviour.md')}).`;

  // KPIs
  V.k1 = `${rng(s66.lo, s66.hi, f0)} °C`;
  V.k1s = `median ${medTxt(s66)}, ${f0(s66.n)} one-second windows on ${andL(OHC.map(lab))} (E53), a statistic of the sensors: ` +
    `neither card's governor acts; at a mean of 65 it reads ${rng(s65.lo, s65.hi, f0)}`;
  const mx = Math.max(g.oh1_max, ...OHC.map(c => g.temp.filter(r => r.card === c).reduce((a, r) => Math.max(a, r.max), 0)));
  V.k2 = `${sgn(mx)} °C`;
  V.k2s = `in ${f0(g.n4_total)} of ${f0(nAll)} whole-chip windows, never +5; at most ${sgn(g.oh1_max)} with one shire or a 2 × 2 block (E53)`;
  V.k3 = `0 of ${f0(cr.oh_checked)}`;
  V.k3s = `E53, up to ${an(oh[hot].mean_c)} ${f0(oh[hot].mean_c)} °C mean (a sensor at ${f0(oh[hot].high_c)}); before it, 2 wrong of ${f0(priorChk)}, both at a clock step`;
  V.k4 = `within ${num(t.oh2b_a3_max_abs, 2)}%`;
  V.k4s = `${f0(t.oh2b_a3_n)} kernel metrics at an 80–85 °C mean against rest, aifoundry3 (E53); the heater's ${f3(t.heater_prior_cpo[0])} cycles per op at every temperature`;

  // the experiments
  const vd = D.verdicts, pr0 = D.prereg;
  V.expIntro = `Two experiments registered before any data, and one by-product, ran on ${andL(OHC.map(lab))} on 28 September; ` +
    `nothing ran on aifoundry2, and card 0 was only read by a guard. <b>OH-1</b>: the gap under the most concentrated load. <b>OH-2</b>: ` +
    `nine exact-checked kernels from rest to the hottest the heater reaches, the DRAM refresh period hot, and a cooling tail. ` +
    `<b>OH-3</b>: idle power from the idle stretches. <b>${f0(vd.n_pass)} of the ${f0(vd.n_registered)} registered verdicts pass</b>; ` +
    `the one gap is card 1's work-per-cycle test, ${word('INSUFFICIENT')}, because card 1 never got hotter than a ` +
    `${f0(D.oh_max['aifoundry1-c1'].mean)} °C mean, and for the same reason its gap-growth test was not testable.`;
  V.vNote = `One verdict per item and card; an item with several parts (kernels, bands, loads) passes when every part does. The rules ` +
    `are in ${code('tools/claims-v3/oh/prereg/PREREG.md')}, the results in ${code('reductions/verdicts.json')}.`;
  const sh = s => `<code>${s.slice(0, 12)}…</code>`;
  V.freeze = `The predictions and decision rules were frozen at ${pr0.orig.time} PDT, before any OH-1 or OH-2 block (SHA-256 ` +
    `${sh(pr0.orig.sha)}); amendment 1 at ${pr0.a1.time} (${sh(pr0.a1.sha)}); amendment 2 at ${pr0.a2.time}, the current file ` +
    `(${sh(pr0.a2.sha)}). No registered prediction or rule changed.`;
  V.am1 = `${ucf(esc(pr0.a1.why))}. The stopped attempts are kept (${code('p201.aborted-a1')}), outside the verdicts; their checked launches count in the totals.`;
  V.am2 = `${ucf(esc(pr0.a2.why))}. Kept as ${code('p201.aborted-a2')}.`;
  V.cardTime = `About ${OHC.map(c => `${f0(D.card_time_min[c])} min on ${lab(c)}`).join(' and ')} with the card lock held, ` +
    (new Set(OHC.map(c => D.card_time_aborted_min[c])).size === 1 ? `${f0(D.card_time_aborted_min[OHC[0]])} min of each` :
      `${andL(OHC.map(c => f0(D.card_time_aborted_min[c])))} min respectively`) + ` in the stopped attempts. The hottest: ` +
    OHC.map(c => `${lab(c)} ${an(D.oh_max[c].mean)} ${f0(D.oh_max[c].mean)} °C mean, a sensor at ${f0(D.oh_max[c].high)} °C, ${f1(D.oh_max[c].board_w)} W`).join('; ') +
    `. No soft cap or hard stop ever acted.`;
  V.rules = `Every device process under ${code('timeout 10')} with the card lock held; back-to-back launches in chains of at most 150 s; ` +
    `a hard stop at 88 °C on the mean or any sensor, or at 82 W (soft caps 86 °C on a sensor, 85 °C on the mean, 78 W); the one write ` +
    `to a card was the service processor's statistics reset once a second, as in E52; card 0 only read.`;
  const tel = Object.values(pk).reduce((a, p) => a + p.samples, 0);
  V.methodRecord = `The analyses of the existing record scan every telemetry and launch file under ${code('docs/reports/data')} ` +
    `(${f0(tel)} telemetry samples; ${f0(cr.prior_records)} launch records for correctness, leaving out E53's own directory, which its ` +
    `reducer covers).`;
})();

/* ---------- fill the prose, then number every citation in it ---------- */
document.querySelectorAll('[data-v]').forEach(e => {
  const k = e.getAttribute('data-v');
  if (V[k] == null) { console.error('effect-of-overheating: no value for ' + k); return; }
  e.innerHTML = V[k];
});
numberCites();
['vendtable', 'mechtable', 'practable'].forEach(id => CK.stackTable($(id)));

/* ---------- shared drawing helpers; the charts and tables run after the prose's citations are numbered ---------- */
const LATER = [];
const TXT = (g, x, y, s, cls, a) => CK.txt(g, x, y, s, cls || 'lab', a);
function rowLabel(g, x, y, s, strong) { return TXT(g, x, y, s, strong ? 'lab-strong' : 'lab'); }
const legendItems = items => items.map(it => Object.assign({key: it.key || it.label}, it));

/* ---------- chart: the ladder of limits ---------- */
LATER.push(function () {
  const rows = D.limits.map(r => ({name: r.name, short: r.short, marks: r.marks, src: r.src}));
  const fw = D.fw;
  rows.push({name: `ET-SoC-1 firmware (BL2 ${fw.build})`, short: `ET-SoC-1 (BL2 ${fw.build})`, et: 'fw', marks: [
    {t: 'throttle', at: fw.acts_at_c, what: `slows the clock while the MEAN of ${fw.sensors} sensors exceeds ${fw.threshold_c} °C (first acts at ${fw.acts_at_c}); nothing below 600 MHz. It acts on aifoundry2; it is latched on aifoundry3, and card 1's 0.18.0 build never moves its clock`},
    {t: 'pmic', at: fw.pmic_c, what: `PMIC alarm at ${fw.pmic_c} °C, on the PMIC's own "system temperature", not the die; it reads 0, and on 0.20.0 the handler does not reprogram the PLL`}], src: 'et-thermal-h,et-thermal-c,et-pmic'});
  CK.cardsIn(D.peaks).forEach(c => rows.push({name: `${lab(c)}: highest mean and hottest sensor on record`, short: `${lab(c)}, on record`, et: 'obs', card: c,
    marks: [{t: 'obs', lo: D.peaks[c].mean, hi: D.peaks[c].high, what: `highest mean ${D.peaks[c].mean} °C, hottest single sensor ${D.peaks[c].high} °C`}]}));
  const KIND = {rating: {label: 'rated range', color: 'var(--c1)', mark: 'box'},
    budget: {label: 'limited time or derated', color: 'var(--c5)', mark: 'box'},
    throttle: {label: 'throttle', color: 'var(--c2)', mark: 'diamond'},
    shutdown: {label: 'shutdown', color: 'var(--c7)', mark: 'box'},
    qual: {label: 'qualification test', color: 'var(--c3)', mark: 'dot'}};
  CK.legend('ladleg', Object.entries(KIND).map(([k, v]) => ({key: k, label: v.label, color: v.color, mark: v.mark}))
    .concat([{key: 'obs', label: 'ET-SoC-1 on record: mean → hottest sensor', color: 'var(--ink-2)', mark: 'line'}]));
  const X0 = 40, X1 = 130, RH = 38;
  CK.frame('ladder', {label: 'Temperature limits of processors and the ET-SoC-1', height: () => 30 + rows.length * RH + 36, draw(f) {
    const L = 12, R = 14, T = 16, W = f.W, H = f.H, B = 36;
    const x = CK.lin(X0, X1, L, W - R), y0 = T;
    CK.axes(f, {x, y: CK.lin(0, 1, H - B, T), yt: [], L, R, T, B, xl: 'junction (die) temperature, °C', grid: false});
    const g = CK.el('g', {}, f.svg);
    x.ticks(Math.max(3, Math.round((W - L - R) / 70))).forEach(t => CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: H - B, class: 'grid-line'}, g));
    const nodes = [];
    rows.forEach((r, i) => {
      const yb = y0 + i * RH + 24;
      const from = r.marks.filter(m => m.lo != null && m.lo < X0).map(m => m.lo);
      rowLabel(g, L, yb - 10, (f.narrow && r.short ? r.short : r.name) + (from.length ? ` (from ${from[0]} °C)` : ''), !!r.et);
      r.marks.forEach(m => {
        const tipTxt = `<b>${esc(r.name)}</b><br>${esc(m.what)}${r.src ? ' ' + citeInner(r.src) : ''}`;
        let node;
        if (m.t === 'rating' || m.t === 'budget') {
          const a = Math.max(X0, m.lo), b = Math.min(X1, m.hi);
          node = CK.el('rect', {x: x(a), y: yb - 3, width: Math.max(2, x(b) - x(a)), height: 7, rx: 3.5}, g);
          node.style.fill = KIND[m.t].color; node.style.opacity = m.t === 'rating' ? 0.55 : 0.75;
        } else if (m.t === 'obs') {
          CK.el('line', {x1: x(m.lo), x2: x(Math.min(X1, m.hi)), y1: yb, y2: yb, style: 'stroke:var(--ink-2);stroke-width:2'}, g);
          CK.el('line', {x1: x(m.lo), x2: x(m.lo), y1: yb - 5, y2: yb + 5, style: 'stroke:var(--ink-2);stroke-width:2'}, g);
          node = CK.cardMark(g, r.card, x(Math.min(X1, m.hi)), yb, 5);
          if (m.hi > 118) TXT(g, x(m.lo) - 8, yb + 4, `${m.lo} → ${m.hi} °C`, 'tick', 'end');
          else TXT(g, x(Math.min(X1, m.hi)) + 10, yb + 4, `${m.lo} → ${m.hi} °C`, 'tick');
        } else {
          const cx = x(m.at != null ? m.at : (m.lo + m.hi) / 2), k = m.t === 'pmic' ? 'throttle' : m.t;
          if (m.lo != null && m.hi != null) {
            const seg = CK.el('rect', {x: x(m.lo), y: yb - 2, width: x(m.hi) - x(m.lo), height: 4, rx: 2}, g); seg.style.fill = KIND[k].color; seg.style.opacity = 0.6;
          }
          if (k === 'throttle') node = CK.el('polygon', {points: `${cx},${yb - 6} ${cx + 6},${yb} ${cx},${yb + 6} ${cx - 6},${yb}`}, g);
          else if (k === 'shutdown') node = CK.el('rect', {x: cx - 5, y: yb - 5, width: 10, height: 10, rx: 1}, g);
          else node = CK.el('circle', {cx, cy: yb, r: 5.5}, g);
          if (r.et === 'fw') { const pm = m.t === 'pmic', t0 = f.narrow ? String(m.at) : pm ? `${m.at} (PMIC reading)` : `${m.at} (mean)`;
            TXT(g, pm || !f.narrow ? cx + 9 : cx - 9, yb + 4, t0, 'tick', pm || !f.narrow ? 'start' : 'end'); }
          if (m.t === 'pmic') { node.style.fill = 'var(--surface)'; node.style.stroke = KIND.throttle.color; node.style.strokeWidth = '2'; }
          else { node.style.fill = KIND[k].color; node.style.stroke = 'var(--surface)'; node.style.strokeWidth = '1.5'; }
        }
        CK.tip(f, node, tipTxt);
        nodes.push(node);
      });
    });
    CK.keynav(f, nodes);
  }});
  $('ladcap').innerHTML = `Each row is one design's published limits, from its own document (hover or focus a mark for the words and the ` +
    `source); ranges that start below 40 °C are cut at the left edge. The ET rows: the firmware's two thresholds ${cite('et-thermal-h,et-pmic')}, and each card's ` +
    `highest whole-degree mean (tick) and hottest single sensor (mark) in every telemetry file on record ${kind('measured')}. Card 0's are the ` +
    `peak-holds its service processor still holds from its September cooling fault.`;
});

/* ---------- charts: the gap by load, and by temperature (bubble matrices) ---------- */
LATER.push(function () {
  const g = D.gap;
  let cur = OHC[0];
  const cs = CK.cardSeg('gapcard', {cards: OHC, value: cur, onChange: v => { cur = v; fl.redraw(); ft.redraw(); caps(); }});
  const LOADS = ['idle', 'one central shire', 'one shire by the I/O corner', 'central 2 × 2 block', 'whole-chip heater'];
  const GAPS = [0, 1, 2, 3, 4, 5];
  function bubbles(f, rowsSpec, xlab) {
    const L = f.narrow ? 12 : 190, R = 14, T = 18, B = 42, W = f.W, H = f.H;
    const x = CK.lin(-0.5, GAPS.length - 0.5, L + (f.narrow ? 0 : 0), W - R);
    const nR = rowsSpec.length, rh = (H - T - B) / nR;
    const g0 = CK.el('g', {}, f.svg);
    GAPS.forEach(v => { CK.el('line', {x1: x(v), x2: x(v), y1: T, y2: H - B, class: 'grid-line'}, g0); TXT(g0, x(v), H - B + 16, sgn(v), 'tick', 'middle'); });
    CK.el('line', {x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ck-axis'}, g0);
    TXT(g0, (L + W - R) / 2, H - 6, xlab, 'lab', 'middle');
    const rmax = Math.min(rh * (f.narrow ? 0.36 : 0.46), (x(1) - x(0)) * 0.46), nodes = [];
    rowsSpec.forEach((rs, i) => {
      const yc = T + (i + 0.5) * rh + (f.narrow ? 7 : 0);
      if (f.narrow) TXT(g0, L, T + i * rh + 11, rs.label, 'lab'); else TXT(g0, L - 8, yc + 4, rs.label, 'lab', 'end');
      if (!rs.n) { TXT(g0, x(2.5), yc + 4, 'no windows', 'tick', 'middle'); return; }
      Object.entries(rs.dist).forEach(([gap, n]) => {
        const share = n / rs.n, r = Math.max(2.5, rmax * Math.sqrt(share));
        const c = CK.el('circle', {cx: x(+gap), cy: yc, r}, g0);
        c.style.fill = `color-mix(in srgb, ${CK.card(cur).color} 30%, var(--surface))`; c.style.stroke = CK.card(cur).color; c.style.strokeWidth = '2';
        CK.tip(f, c, `<b>${esc(lab(cur))}, ${esc(rs.label)}</b><br>gap ${sgn(+gap)} °C in ${f0(n)} of ${f0(rs.n)} windows (${num(100 * share, 0)}%)`);
        if (r >= 14) TXT(g0, x(+gap), yc + 4, num(100 * share, 0) + '%', 'lab', 'middle').style.fill = 'var(--ink)';
        nodes.push(c);
      });
    });
    CK.keynav(f, nodes);
  }
  const fl = CK.frame('gapload', {label: 'Hottest sensor minus mean, by load', height: w => (w < 600 ? 380 : 330), draw(f) {
    const rs = LOADS.map(l => { const r = g.load.find(x => x.card === cur && x.load === l); return r ? {label: l, n: r.n, dist: r.dist} : {label: l, n: 0, dist: {}}; });
    bubbles(f, rs, 'hottest sensor minus the mean, °C (whole degrees)');
  }});
  const ft = CK.frame('gaptemp', {label: 'Hottest sensor minus mean, by die temperature', height: w => (w < 600 ? 470 : 400), draw(f) {
    const rs = g.temp.filter(r => r.card === cur).map(r => ({label: `mean ${r.band.replace('-', '–')} °C`, n: r.n, dist: r.dist}));
    bubbles(f, rs, 'hottest sensor minus the mean, °C (whole degrees)');
  }});
  function caps() {
    const rows = g.load.filter(x => x.card === cur);
    $('gaploadcap').innerHTML = `Each circle's area is the share of that load's one-second windows with that gap; ${esc(lab(cur))}, E53 ` +
      `(${rows.map(r => `${esc(r.load)} ${f0(r.n)}`).join(', ')} windows). Idle and the single-shire and 2 × 2 loads are OH-1's; the whole-chip ` +
      `heater is every OH-2 window inside a heater launch. The switch above changes the card for both charts.`;
    const tr = g.temp.filter(r => r.card === cur);
    $('gaptempcap').innerHTML = `Every one-second window of OH-2 on ${esc(lab(cur))} (heating, holds, checked kernels and the cooling tail; ` +
      `${f0(tr.reduce((a, r) => a + r.n, 0))} windows), by the die's mean. ${cur === 'aifoundry1-c1' ? 'Card 1 never got past a 76 °C mean.' : ''}`;
  }
  caps();
});

/* ---------- chart: temperature inversion (an illustration) ---------- */
LATER.push(function () {
  const inv = D.inversion;
  let cur = RAILC.includes('aifoundry3') ? 'aifoundry3' : RAILC[0];
  CK.cardSeg('invcard', {cards: RAILC, value: cur, label: 'Rails of', onChange: v => { cur = v; draw(); f.redraw(); }});
  let series = [];
  function draw() {
    const r = D.rails[cur];
    series = [
      {key: 'noc', label: `mesh, ${f0(r.noc.median)} mV`, v: Math.round(r.noc.median), color: 'var(--c3)'},
      {key: 'minion', label: `cores at 600 MHz, ${f0(r.minion.median)} mV`, v: Math.round(r.minion.median), color: 'var(--c1)'},
      {key: 'm800', label: `cores at 800 MHz, ${f0(D.fw.mv_800)} mV`, v: D.fw.mv_800, color: 'var(--c7)', dash: '6 4'},
      {key: 'sram', label: `SRAM arrays, ${f0(r.sram.median)} mV`, v: Math.round(r.sram.median), color: 'var(--c2)'},
    ].map(s => Object.assign(s, {pts: inv.curves[String(s.v)]})).filter(s => s.pts);
    CK.legend('invleg', series.map(s => ({key: s.key, label: s.label, color: s.color, mark: s.dash ? 'dash' : 'line'})));
  }
  draw();
  const f = CK.frame('inversion', {label: 'Relative gate delay against temperature', height: w => (w < 600 ? 300 : 320), draw(f) {
    const L = 48, R = f.narrow ? 16 : 150, T = 24, B = 40, W = f.W, H = f.H;
    const all = series.flatMap(s => s.pts.map(p => p[1]));
    const x = CK.lin(0, 125, L, W - R), y = CK.lin(Math.min(0.8, Math.floor(Math.min(...all) * 20) / 20), Math.max(1.3, Math.ceil(Math.max(...all) * 20) / 20), H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xl: 'temperature, °C', yl: 'delay relative to 25 °C (lower is faster)', yfmt: v => num(v, 2)});
    const g = CK.el('g', {}, f.svg);
    const band = CK.el('rect', {x: x(50), y: T, width: x(85) - x(50), height: H - B - T}, g); band.style.fill = 'var(--grid)'; band.style.opacity = 0.5;
    TXT(g, x(67.5), T + 12, 'where the cards run', 'tick', 'middle');
    CK.el('line', {x1: L, x2: W - R, y1: y(1), y2: y(1), style: 'stroke:var(--axis);stroke-width:1'}, g);
    series.forEach(s => {
      const p = CK.el('path', {d: CK.path(s.pts, x, y), class: 'ln'}, g); p.style.stroke = s.color; if (s.dash) p.style.strokeDasharray = s.dash;
      if (!f.narrow) { const last = s.pts[s.pts.length - 1]; TXT(g, x(last[0]) + 6, y(last[1]) + 4, s.label.split(',')[0], 'lab'); }
    });
    // crosshair: one hit column per 5 degrees
    const nodes = [];
    const cols = series[0].pts.map(p => p[0]);
    cols.forEach((t, k) => {
      const w = (x(125) - x(0)) / (cols.length - 1);
      const hit = CK.el('rect', {x: x(t) - w / 2, y: T, width: w, height: H - B - T, class: 'ck-hit'}, g);
      CK.tip(f, hit, () => `<b>${t} °C</b><br>` + series.map(s => `${esc(s.label)}: ${num(s.pts[k][1], 3)}`).join('<br>'));
      nodes.push(hit);
    });
    CK.keynav(f, nodes);
  }});
  const z = inv.ztc_V;
  $('invnote').innerHTML = `<b>An illustration, not a measurement or a model of this chip.</b> The curves use the textbook form behind ` +
    `the sources ${cite('dasdan,salamin')}: delay ∝ V / (μ(T) (V − V<sub>th</sub>(T))<sup>α</sup>), with mobility falling as T<sup>−${num(inv.m, 1)}</sup>, ` +
    `a threshold voltage of ${num(inv.vth0_V, 2)} V at 27 °C falling ${num(inv.kappa_mV_per_K, 1)} mV per kelvin, and α = ${num(inv.alpha, 1)}. ` +
    `Those parameters are chosen, not fitted, to put the crossover at about ${num(z['60'], 2)} V (${rng(Math.min(z['25'], z['100']), Math.max(z['25'], z['100']), v => num(v, 3))} V from 25 to 100 °C), where a simulation places it ` +
    `for a whole 7 nm processor ${cite('salamin')}. Only the shape is meant: lines below the crossover fall with heat, lines above it rise. ` +
    `The voltages are the selected card's own, measured on the die at 600 MHz; the 800 MHz point is aifoundry2's.`;
});

/* ---------- chart: what heat does, by temperature ---------- */
LATER.push(function () {
  const CLS = {reversible: {label: 'recovers when it cools', color: 'var(--c1)'},
    reset: {label: 'needs a reset or power cycle; lost data stays lost', color: 'var(--c2)'},
    permanent: {label: 'permanent (accumulates)', color: 'var(--c7)'},
    design: {label: 'a designed response', color: 'var(--c5)'},
    qual: {label: 'qualification: parts must survive this', color: 'var(--c3)'}};
  CK.legend('mechleg', Object.entries(CLS).map(([k, v]) => ({key: k, label: v.label, color: v.color, mark: 'box'})));
  const rows = D.mech, X0 = 40, X1 = 160, RH = 40;
  const refs = [{t: D.fw.acts_at_c, s: 'ET 0.20.0 rule (mean)'}]
    .concat(CK.cardsIn(D.peaks).filter(c => c === 'aifoundry2' || c === 'aifoundry1-c0').map(c => ({t: D.peaks[c].high, s: `${lab(c)} hottest`})));
  CK.frame('mechchart', {label: 'Effects of heat by temperature and whether they reverse', height: () => 34 + rows.length * RH + 40, draw(f) {
    const L = 12, R = 14, T = 30, B = 40, W = f.W, H = f.H;
    const x = CK.lin(X0, X1, L, W - R);
    CK.axes(f, {x, y: CK.lin(0, 1, H - B, T), yt: [], L, R, T, B, xl: 'temperature, °C (die; the DRAM row is its case)', grid: false});
    const g = CK.el('g', {}, f.svg), nodes = [];
    x.ticks(Math.max(3, Math.round((W - L - R) / 70))).forEach(t => CK.el('line', {x1: x(t), x2: x(t), y1: T, y2: H - B, class: 'grid-line'}, g));
    refs.forEach((r, i) => {
      CK.el('line', {x1: x(r.t), x2: x(r.t), y1: T - 4, y2: H - B, style: 'stroke:var(--ink-2);stroke-width:1.5;stroke-dasharray:3 3'}, g);
      TXT(g, x(r.t), 10 + (i % 2) * 11, f.narrow ? f0(r.t) : `${r.s} ${f0(r.t)}`, 'tick', 'middle');
    });
    rows.forEach((r, i) => {
      const yb = T + i * RH + 26;
      rowLabel(g, L, yb - 10, f.narrow && r.short ? r.short : r.what, !!r.et);
      const a = Math.max(X0, r.lo), b = Math.min(X1, r.hi);
      const bar = CK.el('rect', {x: x(a), y: yb - 3, width: Math.max(4, x(b) - x(a)), height: 8, rx: 4}, g);
      bar.style.fill = CLS[r.cls].color; bar.style.opacity = r.grad ? 0.45 : 0.9;
      const rt = r.grad ? 'at every temperature' : r.hi >= X1 ? `from ${f0(r.lo)} °C` : `${f0(r.lo)}–${f0(r.hi)} °C`;
      if (!r.grad) { if (x(b) + 90 < W - R) TXT(g, x(b) + 6, yb + 5, rt, 'tick'); else TXT(g, x(a) - 6, yb + 5, rt, 'tick', 'end'); }
      CK.tip(f, bar, `<b>${esc(r.what)}</b><br>${esc(r.note)}<br><i>${esc(CLS[r.cls].label)}</i>${r.src ? ' ' + citeInner(r.src) : ''}`);
      nodes.push(bar);
    });
    CK.keynav(f, nodes);
  }});
  $('mechcap').innerHTML = `Each bar starts where the sources put the effect's onset; faint bars act at every temperature and grow with it. ` +
    `Dashed lines: the first mean the ET's 0.20.0 rule acts on, and the hottest single sensors on record on aifoundry2 and on card 0 ` +
    `${kind('measured')}. The ET row is derived from the September idle laws of the cards and a 27.2 W estimate for a full random matmul ` +
    `(section 4.4). Off the scale: solder melts at 217 °C and reflow peaks at 260 °C ${cite('sac305,jstd020')}.`;
});

/* ---------- table: exact-checked launches by temperature ---------- */
LATER.push(function () {
  const cr = D.correct, BINS = cr.bins, cards = CK.cardsIn(cr.cells.map(c => c.card));
  const BL = {'0-60': 'below 60', '60-70': '60–70', '70-80': '70–80', '80-90': '80–90', '90-100': '90–100', '100-130': '100 and up'};
  const cell = (c, b) => cr.cells.find(x => x.card === c && x.bin === b);
  const tot = x => x ? x.prior_checked + x.oh_checked : 0;
  const mx = Math.max(...cr.cells.map(tot));
  let h = `<thead><tr><th>Card</th>${BINS.map(b => `<th class="num">${BL[b]} °C</th>`).join('')}</tr></thead><tbody>`;
  cards.forEach(c => {
    h += `<tr><td>${esc(lab(c))}</td>`;
    BINS.forEach(b => {
      const x = cell(c, b), n = tot(x), badN = x ? x.prior_bad + x.oh_bad : 0;
      if (!x || (n === 0 && !x.prior_launches)) { h += `<td class="cellv" data-sort="0">—</td>`; return; }
      const p = n ? Math.log10(n + 1) / Math.log10(mx + 1) : 0;
      const bg = n ? CK.ramp(p) : 'transparent', ink = n ? CK.rampInk(p) : 'var(--muted)';
      const sub = n ? (x.oh_checked ? `E53: ${f0(x.oh_checked)}` : '') : `${f0(x.prior_launches)} unchecked`;
      h += `<td class="cellv" style="background:${bg};color:${ink}" data-sort="${n}"><b>${f0(n)}</b>` +
        (badN ? ` · ${f0(badN)} wrong` : '') + (sub ? `<small>${sub}</small>` : '') + `</td>`;
    });
    h += `</tr>`;
  });
  $('corrtable').innerHTML = h + '</tbody>';
  const bad = cr.prior_bad;
  $('corrcap').innerHTML = `Checked launches (results compared against a known answer) by the die's mean during the launch; the shade grows ` +
    `with the count. “E53” is the part from this page's experiment, stopped attempts included; the rest is the September record ` +
    `(${code('docs/reports/data/2026-09-28-overheating/analysis/correct_vs_temp.json')}). The ${f0(bad.length)} wrong ${bad.length === 1 ? 'result' : 'results'} (aifoundry2, 60–70 °C) came ` +
    `during a clock step, not from heat. A cell with only unchecked launches (the heater, the energy catalogue) shows their number; ` +
    `${Object.entries(cr.prior_notel).map(([c, v]) => `${lab(c)} ${f0(v.checked)}`).join(', ')} checked launches have no telemetry and are not shown.`;
});

/* ---------- chart: Arrhenius ---------- */
LATER.push(function () {
  const dv = D.derived, EAS = dv.ea_list.map(String), COL = ['var(--c3)', 'var(--c1)', 'var(--c2)', 'var(--c7)', 'var(--ref)'];
  const WHY = {'0.5': 'Renesas’ worked example', '0.7': 'JEDEC, TI', '0.9': 'Cu electromigration (RAMP)', '1.2': 'Cu electromigration, top of a review’s range'};
  const S = EAS.map((e, i) => ({key: e, label: `${e} eV${WHY[e] ? ' · ' + WHY[e] : ''}`, color: COL[i], pts: dv.af_curve[e]}));
  CK.legend('arrleg', S.map(s => ({key: s.key, label: s.label, color: s.color, mark: 'line'})));
  const refs = [{t: D.fw.threshold_c, s: `ET threshold ${D.fw.threshold_c}`}];
  if (D.peaks.aifoundry2) refs.push({t: D.peaks.aifoundry2.high, s: `aifoundry2 ${D.peaks.aifoundry2.high}`});
  if (D.peaks['aifoundry1-c0']) refs.push({t: D.peaks['aifoundry1-c0'].high, s: `card 0 ${D.peaks['aifoundry1-c0'].high}`});
  CK.frame('arrhenius', {label: 'Wear-out acceleration against temperature', height: w => (w < 600 ? 320 : 340), draw(f) {
    const L = 52, R = 16, T = 26, B = 40, W = f.W, H = f.H;
    const x = CK.lin(40, 130, L, W - R), y = CK.log(0.05, 1000, H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xl: 'junction temperature, °C', yl: 'wear rate relative to 65 °C (log scale)', yt: [0.1, 1, 10, 100, 1000]});
    const g = CK.el('g', {}, f.svg);
    refs.forEach((r, i) => { CK.el('line', {x1: x(r.t), x2: x(r.t), y1: T, y2: H - B, style: 'stroke:var(--ink-2);stroke-width:1;stroke-dasharray:3 3'}, g);
      TXT(g, x(r.t) + (i === refs.length - 1 && i > 0 ? -4 : 4), i === 0 ? T + 10 : H - B - 8 - 14 * (i - 1), r.s, 'tick', i === refs.length - 1 && i > 0 ? 'end' : 'start'); });
    S.forEach(s => { const p = CK.el('path', {d: CK.path(s.pts, x, y), class: 'ln'}, g); p.style.stroke = s.color; });
    const nodes = [], ts = S[0].pts.map(p => p[0]), w = (x(130) - x(40)) / (ts.length - 1);
    ts.forEach((t, k) => {
      const hit = CK.el('rect', {x: x(t) - w / 2, y: T, width: w, height: H - B - T, class: 'ck-hit'}, g);
      CK.tip(f, hit, () => `<b>${t} °C</b>: wears this many times as fast as at 65 °C<br>` + S.map(s => `${s.key} eV: ${num(s.pts[k][1], s.pts[k][1] < 10 ? 2 : 0)}×`).join('<br>'));
      nodes.push(hit);
    });
    CK.keynav(f, nodes);
  }});
  $('arrcap').innerHTML = `Arrhenius acceleration, exp(E<sub>a</sub>/k (1/T<sub>65</sub> − 1/T)) ${cite('jesd47')}, relative to the ET firmware's 65 °C ` +
    `${kind('derived')}; the script reproduces JEDEC's worked example (0.7 eV, 55 → 125 °C: ${num(dv['check_jesd47_0.7eV_55_125'], 1)} against ` +
    `78.6 with its rounded constants). Activation energies: 0.5 eV (Renesas' worked example ${cite('renesas')}), 0.7 eV (JEDEC's and TI's ` +
    `working value ${cite('jesd47,ti-lifetime')}), 0.9 eV (copper electromigration in RAMP ${cite('ramp')}) and 1.2 eV (the top of a ` +
    `review's 0.8–1.2 eV range for copper ${cite('babu-review')}). Vertical lines: the firmware's threshold and the ` +
    `hottest single sensors on record.`;
});

/* ---------- chart: idle power against temperature ---------- */
LATER.push(function () {
  const cards = IDLEC, c0 = D.card0, dv = D.derived;
  CK.legend('idleleg', CK.cardLegend(cards).map(it => Object.assign(it, {label: it.label + (D.idle[it.key].oh3 ? ': September law, E53 points' : ': September law')}))
    .concat([{key: 'c0', label: 'aifoundry1 card 0 (25 Sep hot; now at 300 MHz)', color: 'var(--ref)', mark: 'box'},
      {key: 'in', label: `card input limit, ${dv.card_input_max_w} W`, color: 'var(--ink-2)', mark: 'dash'}]));
  CK.frame('idle', {label: 'Idle board power against die temperature', height: w => (w < 600 ? 320 : 360), draw(f) {
    const L = 46, R = 16, T = 24, B = 40, W = f.W, H = f.H;
    const x = CK.lin(50, 120, L, W - R), y = CK.lin(0, 125, H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xl: 'die mean, °C', yl: 'idle board power, W'});
    const g = CK.el('g', {}, f.svg), nodes = [];
    const lim = CK.el('line', {x1: L, x2: W - R, y1: y(dv.card_input_max_w), y2: y(dv.card_input_max_w), style: 'stroke:var(--ink-2);stroke-width:1.5;stroke-dasharray:6 4'}, g);
    TXT(g, L + 4, y(dv.card_input_max_w) - 5, `${dv.card_input_max_w} W: the card's 12 V input`, 'tick');
    cards.forEach(c => {
      const e = D.idle[c].e44, fit = e.fit, P = t => fit.P_fix + fit.A * Math.exp((t - 80) / fit.T_L);
      const inPts = [], exPts = [];
      for (let t = e.range[0]; t <= e.range[1]; t += 1) inPts.push([t, P(t)]);
      for (let t = e.range[1]; t <= 120; t += 1) { if (P(t) > 125) break; exPts.push([t, P(t)]); }
      const p1 = CK.el('path', {d: CK.path(inPts, x, y), class: 'ln'}, g); p1.style.stroke = CK.card(c).color;
      const p2 = CK.el('path', {d: CK.path(exPts, x, y), class: 'ln'}, g); p2.style.stroke = CK.card(c).color; p2.style.strokeDasharray = '4 4'; p2.style.opacity = 0.8;
      const lawTip = `<b>${esc(lab(c))}, September idle law</b><br>${f2(fit.P_fix)} + ${f2(fit.A)}·e<sup>(T−80)/${fit.T_L}</sup> W, fitted ${e.range[0]}–${e.range[1]} °C ` +
        `(rms ${num(fit.rms, 3)} W); at 116 °C ${f0(e.extrapolated_w['116'])} W (extrapolated)`;
      const hl = CK.el('path', {d: CK.path(inPts.concat(exPts), x, y), style: 'fill:none;stroke:transparent;stroke-width:14'}, g);
      CK.tip(f, hl, lawTip); nodes.push(hl);
      const o = D.idle[c].oh3;
      if (o) o.bins.forEach(b => { const m = CK.cardMark(g, c, x(b.T), y(b.board_w), 3.5);
        CK.tip(f, m, `<b>${esc(lab(c))}, E53 idle, ${b.T} °C</b><br>${f2(b.board_w)} W median of ${f0(b.n)} samples; the September law says ${f2(b.e44)} W`); nodes.push(m); });
    });
    const r25 = c0.reported_25sep;
    const bx = CK.el('rect', {x: x(r25.hot_c[0]), y: y(r25.hot_idle_w[1]), width: x(r25.hot_c[1]) - x(r25.hot_c[0]), height: y(r25.hot_idle_w[0]) - y(r25.hot_idle_w[1])}, g);
    bx.style.fill = 'var(--ref)'; bx.style.opacity = 0.8;
    CK.tip(f, bx, `<b>aifoundry1 card 0, 25 September</b><br>${r25.hot_idle_w[0]}–${r25.hot_idle_w[1]} W idle at ${r25.hot_c[0]}–${r25.hot_c[1]} °C and 600 MHz (reported in docs/findings/14-card-behaviour.md; firmware 1.4.1)`);
    TXT(g, x(r25.hot_c[0]) - 4, y(r25.hot_idle_w[1]) - 4, 'card 0, 25 Sep', 'tick', 'end');
    const nb = CK.el('rect', {x: x(c0.mean_range[0]), y: y(c0.board_w_range[1]), width: Math.max(4, x(c0.mean_range[1]) - x(c0.mean_range[0])), height: Math.max(3, y(c0.board_w_range[0]) - y(c0.board_w_range[1]))}, g);
    nb.style.fill = 'var(--ref)'; nb.style.opacity = 0.8;
    CK.tip(f, nb, `<b>aifoundry1 card 0 today</b><br>${f1(c0.board_w_range[0])}–${f1(c0.board_w_range[1])} W at ${c0.mean_range[0]}–${c0.mean_range[1]} °C, ${c0.mhz[0]} MHz (E53's guard, ${f0(c0.guard_samples)} samples)`);
    nodes.push(bx, nb);
    CK.keynav(f, nodes);
  }});
  $('idlecap').innerHTML = `Lines: each card's idle law, fitted in September to nine cooling runs at 600 MHz (solid over the fitted range, ` +
    `dashed where extrapolated) ${kind('fitted')}; marks: the median board power per whole degree in E53's idle stretches ${kind('measured')}. ` +
    `Card 0's boxes: its 25 September reading at 600 MHz, and its idle today at 300 MHz, a lower voltage and clock. The laws' split into a fixed ` +
    `part and a leakage part is only loosely fixed by idle data, so the extrapolations are indicative.`;
});

/* ---------- table: the registered verdicts ---------- */
LATER.push(function () {
  const vd = D.verdicts, cards = OHC;
  let h = `<thead><tr><th>Item</th><th>What it tests</th>${cards.map(c => `<th>${esc(lab(c))}</th>`).join('')}</tr></thead><tbody>`;
  vd.rows.forEach(r => { h += `<tr><td>${esc(r.item)}</td><td>${esc(r.rule)}</td>${cards.map(c => `<td>${word(r.cards[c])}</td>`).join('')}</tr>`; });
  $('vtable').innerHTML = h + '</tbody>';
  CK.stackTable($('vtable'));
  const bt = D.oh_blocks;
  let b = `<thead><tr><th>Card</th><th>Block</th><th>Status</th><th class="num">Minutes</th><th class="num">Launches</th><th class="num">Highest mean °C</th><th class="num">Hottest sensor °C</th><th class="num">Board max W</th></tr></thead><tbody>`;
  const WHAT = d => d.startsWith('p1') ? 'OH-1' : d.startsWith('p9') ? 'smoke' : d.includes('aborted') ? 'OH-2, stopped' : 'OH-2';
  bt.forEach(x => { b += `<tr><td>${esc(lab(x.card))}</td><td>${esc(x.dir)} (${WHAT(x.dir)})</td><td>${esc(x.status)}</td><td class="num">${f1(x.minutes)}</td>` +
    `<td class="num">${x.launches == null ? '—' : f0(x.launches)}</td><td class="num">${x.mean_max == null ? '—' : f0(x.mean_max)}</td>` +
    `<td class="num">${x.high_max == null ? '—' : f0(x.high_max)}</td><td class="num">${x.board_max_w == null ? '—' : f1(x.board_max_w)}</td></tr>`; });
  $('blocktable').innerHTML = b + '</tbody>';
  CK.sortTable($('blocktable'));
});

/* ---------- draw, then number what the captions added, then the source lists ---------- */
LATER.forEach(fn => fn());
(function () {
  numberCites();
  const item = k => { const s = SRC[k], et = s.group === 'et';
    return `<li id="src-${k}"${et ? '' : ` value="${NUMS[k]}"`}>${et ? `<b>[${NUMS[k]}]</b> ` : ''}${esc(s.cite)}. <a href="${esc(s.url)}">${esc(s.url.replace(/^https?:\/\//, '').slice(0, 70))}${s.url.length > 78 ? '…' : ''}</a>` +
      `${s.flag ? ` <span class="flag">(${esc(s.flag)})</span>` : ''}<br><span class="used">Used: ${esc(s.used)}</span></li>`; };
  $('srclist').innerHTML = ORDER.outside.map(item).join('');
  $('etsrclist').innerHTML = ORDER.et.map(item).join('');
  const never = D.sources.filter(s => NUMS[s.key] == null).map(s => s.key);
  if (never.length) console.error('effect-of-overheating: sources in the data but never cited: ' + never.join(', '));
})();
