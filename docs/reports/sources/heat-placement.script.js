/* Where the work sits. Every number comes from D (heat.json, written by
   docs/reports/data/2026-09-28-heat-placement/build_heat_data.py from the raw blocks, the reductions and the frozen
   PREREG). Verdicts come from D.verdicts, which is null until the validation's reduction (val.json) exists: every
   verdict on the page then reads "pending". Charts use the shared toolkit CK; cards come from the data (CK.cardsIn). */
const $ = id => document.getElementById(id);
const num = CK.fmt.num, V = {};
const f0 = v => num(v, 0), f1 = v => num(v, 1), f2 = v => num(v, 2), f3 = v => num(v, 3);
const lab = c => CK.card(c).label;
/* the probe classes, grouped: "SILENT on aifoundry3 and aifoundry1 card 1" */
const probeText = () => { const pr = D.q1.probes, by = {};
  Object.keys(pr).forEach(c => { (by[pr[c].class] = by[pr[c].class] || []).push(lab(c)); });
  return Object.entries(by).map(([k, cs]) => `${k} on ${andL(cs)}`).join('; '); };
const andL = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
const rng = (a, b, f) => { const s = f(a), t = f(b); return s === t ? s : `${s}–${t}`; };
const X = v => num(Math.exp(v), 2);                      // a log ratio as a ratio
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const md = s => esc(s).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
const WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'];
const word = n => (n >= 0 && n < WORDS.length ? WORDS[n] : f0(n));
const ucf = s => s.charAt(0).toUpperCase() + s.slice(1);
const hhmm = s => s ? s.slice(11, 16) : '?';
const bare = s => String(s || '').replace(/\s*\(predicted\)\s*$/, '');
const dmy = s => s ? `${+s.slice(8, 10)} September ${s.slice(11, 16)}` : '?';

const DEV = D.dev, REG = D.registration, VER = D.verdicts, VB = D.val_blocks;
const SUM = VB && VB.summary ? VB.summary : null;             // card 1's validation blocks as the verdicts used them
const DEVCARD = DEV.card, VALCARD = D.cards.validation[0];
const IT = DEV.items, PT = IT['PLACE-t'], PTS = IT['PLACE-tS'], TRIO = DEV.trio;
const regItem = id => REG.items.find(i => i.id === id) || {};
const DZ = D.design, FZ = REG.frozen, RUNS = D.placements.runs;
const MIN = n => f0(RUNS[n].minions);                                  // minions of a placement
const PCT = b => num(100 * (Math.exp(b) - 1), 0);                      // a log band as a percentage
const PW = `±${num(DZ.band_power_w, 1)} W`, WK = `±${num(100 * DZ.band_work, 0)}%`;
const SHA = REG.prereg_sha256;
const PNAME = {'INT16@32': 'interior', 'PER16@32': 'perimeter', 'UNI32@16': 'every shire, half the minions'};
const PCOL = {'INT16@32': 'var(--c7)', 'PER16@32': 'var(--c4)', 'UNI32@16': 'var(--ink-2)'};
const PDASH = {'UNI32@16': '6 4'};
const TRIOK = ['INT16@32', 'PER16@32', 'UNI32@16'];
const ci = (c, f) => c ? `${f(c.mean)} [${f(c.lo)} to ${f(c.hi)}]` : '—';
const ciX = c => c ? `${X(c.mean)} [${X(c.lo)}–${X(c.hi)}]` : '—';
const WCLS = {PASS: 'pass', FAIL: 'fail', INSUFFICIENT: 'insufficient', 'CARD-DIFFERENT': 'fail'};
const wordHtml = w => {
  if (!w) return '<span class="word pending">pending</span>';
  const cls = WCLS[w] || (/^pending/.test(w) ? 'pending' : 'nt');
  return `<span class="word ${cls}">${esc(w)}</span>`;
};
const vItem = id => VER && VER.items ? VER.items[id] : null;
const outcome = id => { const v = vItem(id); return v ? v.outcome : null; };
/* PLACE-t's own runs on card 1 (its pair, INT16@32 and PER16@32) that the chain cap cut off: {c, n} */
const ptCut = () => { const pc = SUM.L16.placements, pr = ['INT16@32', 'PER16@32'];
  return {c: pr.reduce((a, k) => a + pc[k].censored, 0), n: pr.reduce((a, k) => a + pc[k].n, 0)}; };

/* ---------- status, lede and KPIs ---------- */
(function () {
  const dv = D.q1.dv2, fw = D.q1.firmware;
  const nIntPer = PT.sign_count.A_longer, nBlk = PT.ci99.n;
  const pw = PT.power_w;
  V.bylineSha = `PREREG SHA-256 <code>${SHA.slice(0, 12)}…</code>, ${esc(REG.written)}`;
  const regd = REG.items.filter(i => i.registered).map(i => i.id);
  const nv = REG.n_val;
  if (!VER) {
    V.statusWord = 'Validation pending.';
    V.statusText = `The frozen protocol runs on ${lab(VALCARD)}: ${f0(nv.L16)} Tier L blocks and ${f0(nv.S)} Tier S blocks, ` +
      `in two sessions at least four hours apart. The verdicts (section 8) fill in when its reduction exists; until then ` +
      `every number on this page is development data from ${lab(DEVCARD)} or ${lab(VALCARD)}'s calibration, and tests nothing.`;
  } else {
    const ws = regd.map(i => `${i} ${wordHtml(outcome(i))}`);
    V.statusWord = `Validation on ${lab(VER.card || VALCARD)}:`;
    V.statusText = `${andL(ws)}; transfer (H11) ${wordHtml(outcome('H11'))}. The summary below says which theories survived and why; section 8 has every verdict.`;
  }
  V.ledeQ1 = `The mean of the die's ${fw.sensors} shire sensors, not the hottest one: the firmware compares only that mean with ` +
    `${fw.threshold_c} °C, and on the one card whose clock moves (aifoundry2, the DVFS page's development night), in ` +
    `${word(dv.fit_mean)} of the ${word(dv.separating)} runs that tell the two apart, the clock stepped down ` +
    `${rng(dv.down_minus_mean[0], dv.down_minus_mean[1], f1)} s after the mean reached ${fw.threshold_c + 1} °C and ` +
    `${rng(dv.down_minus_high_fit[0], dv.down_minus_high_fit[1], f1)} s after the hottest sensor had` +
    (dv.neither.length ? `; the ${dv.neither.length === 1 ? 'other' : 'other ' + word(dv.neither.length)} fit${dv.neither.length === 1 ? 's' : ''} neither rule` : '') +
    `. ${ucf(word(dv.separating))} runs are fewer than DV2's frozen count asks, so as a count that test is ${esc(dv.g1t_outcome)}. ` +
    `This experiment's own clock tests could not run (section 2).`;
  const t = TRIO;
  V.ledeQ2 = `On ${lab(DEVCARD)}, yes, and by a lot: the same ${MIN('INT16@32')} minions of work took <b>${X(PT.ci99.mean)} times as long</b> ` +
    `to bring the mean from ${edgeOf(DEVCARD, 'L16')} to 66 °C when placed on the perimeter as ` +
    `in the interior (99% interval ${X(PT.ci99.lo)}–${X(PT.ci99.hi)}; longer in ${word(nIntPer)} of ${word(nBlk)} blocks; ` +
    `${f1(t['PER16@32'].t66.mean)} s against ${f1(t['INT16@32'].t66.mean)} s on average), at the same power to within ` +
    `${f2(Math.abs(pw.mean))} W of about ${f0(t['INT16@32'].sw_W.mean)} W. Spread over every shire it took ${f1(t['UNI32@16'].t66.mean)} s, ` +
    `in between. ` + (VER && SUM ? `On ${lab(VALCARD)}, under the frozen predictions, the perimeter again lasted longer in short bursts ` +
      `(${X(vItem('PLACE-tS').ci99.mean)} times, ${wordHtml(outcome('PLACE-tS'))}); in the sustained test, the primary one, ` +
      `${f0(ptCut().c)} of its ${f0(ptCut().n)} runs (${f0(SUM.L16.censored)} of all ${f0(SUM.L16.runs)} Tier L runs) had not brought the mean to 66 °C when the ${f0(SUM.C.L16)} s cap ended them, ` +
      `and the verdict is ${wordHtml(outcome('PLACE-t'))} (the summary above).`
      : VER ? `On ${lab(VALCARD)}, the frozen prediction that the perimeter lasts longer ${verdictPhrase('PLACE-t')}.`
      : `Whether the sign holds on another card, ${lab(VALCARD)}, is the frozen prediction; its verdict is pending.`);
  V.k1 = `${X(PT.ci99.mean)}×`;
  V.k1s = `99% interval ${X(PT.ci99.lo)}–${X(PT.ci99.hi)}; ${word(nIntPer)} of ${word(nBlk)} blocks; ${lab(DEVCARD)}, development`;
  V.k2 = `the mean of ${fw.sensors}`;
  V.k2s = `firmware source; on aifoundry2, ${word(dv.fit_mean)} of ${word(dv.separating)} telling runs stepped with the mean, none with the hottest sensor (development; too few runs for DV2's frozen count)`;
  V.k3 = `${num(pw.mean, 2)} W`;
  const pwV = vItem('PLACE-t/POWER');
  V.k3s = `${lab(DEVCARD)}, development: [${num(pw.lo, 2)} to ${num(pw.hi, 2)}], inside the ${PW} equal-power band; about ${f0(t['INT16@32'].sw_W.mean)} W each` +
    (pwV && pwV.ci99 ? `. ${lab(VALCARD)}, registered (sustained): ${ci(pwV.ci99, f2)} W, ${wordHtml(pwV.outcome)}` : VER ? '' : `. ${lab(VALCARD)}'s check is pending`);
  if (!VER) { V.k4 = 'pending'; V.k4s = `PLACE-t registered SIGN+ (the perimeter lasts longer), ${f0(nv.L16)} + ${f0(nv.S)} blocks`; }
  else {
    const p = vItem('PLACE-t') || {}, q = vItem('PLACE-tS') || {};
    const nPass = regd.filter(i => outcome(i) === 'PASS').length;
    V.k4 = `${f0(nPass)} of ${f0(regd.length)} PASS`;
    V.k4s = `short bursts (PLACE-tS) ${q.ci99 ? `${X(q.ci99.mean)}× [${X(q.ci99.lo)}–${X(q.ci99.hi)}]` : ''} ${esc(q.outcome || '—')}; ` +
      `sustained (PLACE-t, primary) ${p.ci99 ? `${X(p.ci99.mean)}× [${X(p.ci99.lo)}–${X(p.ci99.hi)}]` : ''} ${esc(p.outcome || '—')}` +
      (SUM ? `, ${f0(ptCut().c)} of its ${f0(ptCut().n)} runs cut off at ${f0(SUM.C.L16)} s` : '');
  }
  V.method = `theories and their predictions first; every iteration on one development card (${lab(DEVCARD)}, rounds R1–R3, ` +
    `${devSpan()}); a power step that registers an item only if the validation card can resolve it; the ` +
    `predictions, parameters, code and binaries frozen and hashed (PREREG, ${esc(REG.written)}); a calibration of the ` +
    `validation card's start temperature on a workload that is never tested; then the frozen protocol on ${lab(VALCARD)}, ` +
    `with no iteration. aifoundry2, whose governor moves the clock, was to answer Q1 the same day.`;
})();

/* ---------- the owner's summary at the top: which theories survived, in plain words (from D.verdicts and the
   blocks the frozen reduction used, D.val_blocks.summary) ---------- */
(function () {
  const ul = $('sumlist');
  if (!VER || !SUM) {
    V.sumHead = `${wordHtml(null)}: this fills in from the frozen reduction of ${lab(VALCARD)}'s validation blocks.`;
    ul.innerHTML = `<li>Until then every number on this page is development data from ${lab(DEVCARD)} or ${lab(VALCARD)}'s calibration, and tests nothing.</li>`;
    V.sumCaveats = `Only signs were predicted for the validation card, never sizes.`;
    return;
  }
  const pS = vItem('PLACE-tS') || {}, pL = vItem('PLACE-t') || {}, pw = vItem('PLACE-t/POWER') || {}, TH = VER.theories || {};
  const wL = vItem('PLACE-t/WORK') || {}, wS = vItem('PLACE-tS/WORK') || {};
  const scS = VB.items['PLACE-tS'].sign_count || {}, scL = VB.items['PLACE-t'].sign_count || {};
  const Lt = SUM.L16, St = SUM.S, CL = SUM.C.L16, band = SUM.band;
  const regd = REG.items.filter(i => i.registered).map(i => i.id);
  const ws = regd.map(outcome), nPass = ws.filter(w => w === 'PASS').length, nFail = ws.filter(w => w === 'FAIL').length;
  const tS = n => St.placements[n].mean_crossed;
  // Tier L: the blocks in which the pair was decided, and the last session
  const dec = Lt.blocks.filter(b => b.pair === 'perimeter longer' || b.pair === 'interior longer');
  const tt = r => r.censored ? `over ${f0(CL)} s` : `${f1(r.t66)} s`;
  const decTxt = dec.map(b => `perimeter ${tt(b.runs['PER16@32'])}, interior ${tt(b.runs['INT16@32'])} (block ${b.pass})`).join('; ');
  const lastS = Lt.blocks.length ? Lt.blocks[Lt.blocks.length - 1].session : null, last = lastS != null ? Lt.by_session[lastS] : null;
  const lastAll = last && last.runs && last.censored === last.runs;
  // decided blocks of the pair (one run outlasted the other): card 1's validation, then development, never pooled
  const sumK = (cs, k) => cs.reduce((a, c) => a + (c[k] || 0), 0);
  const A1 = sumK([scL, scS], 'A_longer'), B1 = sumK([scL, scS], 'B_longer');
  const dL1 = (scL.A_longer || 0) + (scL.B_longer || 0), dS1 = (scS.A_longer || 0) + (scS.B_longer || 0);
  const Ad = sumK([PT.sign_count, PTS.sign_count], 'A_longer'), Bd = sumK([PT.sign_count, PTS.sign_count], 'B_longer');
  const swL = n => { const v = Object.values(D.traces[VALCARD] || {}).filter(b => b.type === 'L16').flatMap(b => b.runs.filter(r => r.name === n && r.sw_W != null).map(r => r.sw_W));
    return v.length ? v.reduce((a, x) => a + x, 0) / v.length : null; };
  const v0e = D.v0.edges.find(e => e.edge === D.v0.settled) || {t66: []}, v0t = v0e.t66.filter(x => x != null);
  const a2rest = D.q1.a2.map(a => a.rest_c);
  const conc = (vItem('CONC') || {}).value, map = (vItem('MAP') || {}).value;
  const pct = v => num(100 * v, 3);
  V.sumHead = (nPass === regd.length ? `Every registered prediction held on ${lab(VALCARD)}.` :
    `By the frozen rules, no theory counts as survived on the second card (${lab(VALCARD)}): ` +
    `${word(nPass)} of the ${word(regd.length)} registered predictions held, the one for short bursts, but the primary test, sustained heating, ` +
    `is ${wordHtml(outcome('PLACE-t'))}, with most of its runs cut off by the ${f0(CL)} s cap, and transfer (H11) with it.`) +
    ` ${nFail ? `${ucf(word(nFail))} registered prediction${nFail > 1 ? 's' : ''} failed.` : 'Nothing was refuted.'} What each theory now rests on:`;
  const L = [
    `<b>H2, the edges trip later: held in short bursts, undecided for sustained heating.</b> ` +
    `In short bursts (Tier S: one ${f0(DZ.S_launch_s)} s launch from ${FZ.S_S} °C) the same ${MIN('PER16@32')} minions took <b>${X(pS.ci99.mean)} times as long</b> ` +
    `to bring the mean to 66 °C on the perimeter as in the interior (99% interval ${X(pS.ci99.lo)}–${X(pS.ci99.hi)}; ${f2(tS('PER16@32'))} s against ` +
    `${f2(tS('INT16@32'))} s on average), longer in ${word(scS.A_longer)} of ${word(pS.ci99.n)} blocks: PLACE-tS ${wordHtml(pS.outcome)}. ` +
    `${lab(DEVCARD)} had shown ${X(PTS.ci99.mean)} times; only the sign was predicted. In sustained heating (Tier L: chains from ${FZ.S_L} °C, ` +
    `up to ${f0(CL)} s), the primary test, PLACE-t is ${wordHtml(pL.outcome)}: ${X(pL.ci99.mean)} times [${X(pL.ci99.lo)}–${X(pL.ci99.hi)}]. ` +
    `Of its ${f0(ptCut().n)} runs, ${f0(ptCut().c)} had not brought the mean to 66 °C when the cap ended them (${f0(Lt.censored)} of all ${f0(Lt.runs)} Tier L runs); in ${word(Lt.pairs['both censored'])} of ` +
    `${word(Lt.blocks.length)} blocks both the interior and the perimeter run were cut off, which counts as equal times. ` +
    (dec.length ? `The ${word(dec.length)} block${dec.length > 1 ? 's' : ''} that decided went ${Lt.pairs['interior longer'] ? 'both ways' : 'the predicted way'}: ${decTxt}. ` : '') +
    `The frozen rule rests H2 on the primary test, so H2 is not counted as survived.`,
    `<b>H3, the centre trips later: not registered, and no support.</b> On ${lab(VALCARD)}, ${word(A1 + B1)} blocks were decided (one run outlasted the other: ` +
    `${word(dL1)} Tier L, ${word(dS1)} Tier S), and the interior outlasted the perimeter in ${B1 ? word(B1) : 'none'}; card 1's short-burst interval lies wholly above 0. ` +
    `In development on ${lab(DEVCARD)}, the data that chose the prediction, the perimeter outlasted the interior in ${word(Ad)} of ${word(Ad + Bd)} blocks ` +
    `(${word(PT.sign_count.A_longer)} Tier L, ${word(PTS.sign_count.A_longer)} Tier S). ` +
    `PLACE-t was registered ${esc(TH.registered_as || '')}, so DESIGN2's frozen table gives H3 no entry of its own.`,
    `<b>H4, only total power matters: not registered; not supported in short bursts</b> (a reading outside the frozen table). Card 1's short-burst interval, ${X(pS.ci99.lo)}–${X(pS.ci99.hi)} times, lies wholly ` +
    `outside the ±${PCT(band)}% band that would mean "placement does not matter"; for sustained heating the interval (${X(pL.ci99.lo)}–${X(pL.ci99.hi)}) cannot tell. ` +
    `As for H3, the frozen table gives it no entry.`,
    `<b>H11, the development card's signs transfer: undecided</b> (${wordHtml(outcome('H11'))}): it needs every registered sign prediction to hold, and the primary one is ${wordHtml(pL.outcome)}.`,
    `<b>H13, equal power: undecided</b> (${wordHtml(pw.outcome)}): perimeter less interior ${ci(pw.ci99, f2)} W in sustained heating, at about ` +
    `${f0(swL('INT16@32'))} W each; the interval is not wholly inside ${PW}. Equal work held in both tiers ` +
    `(${wordHtml(wL.outcome)}, ${wordHtml(wS.outcome)}: within ${pct(Math.max(Math.abs(wL.ci99.lo), Math.abs(wL.ci99.hi), Math.abs(wS.ci99.lo), Math.abs(wS.ci99.hi)))}%).`,
    `<b>H1 against H1′, does the governor watch the mean or the hottest sensor: not tested on a card here.</b> ${lab(VALCARD)}'s clock never leaves 600 MHz ` +
    `(probe ${esc(D.q1.probes[VALCARD].class)}; TRIG-A waived, departure 19), and aifoundry2 rested at ${rng(Math.min(...a2rest), Math.max(...a2rest), f0)} °C, already in its ` +
    `thermal loop, at both attempts. The answer, the mean, rests on the firmware source and the DVFS page's development night ` +
    `(${word(D.q1.dv2.fit_mean)} of ${word(D.q1.dv2.separating)} telling runs; section 2).`,
    `<b>Not tested:</b> H3′ (an airflow gradient), H6 (linearity), H8 (the memory-strip side) and H9 (the bare edges), all dropped with the half-power blocks; ` +
    `H7 (concentration lifts the hottest sensor) and H10 (the I/O corner), reported only` +
    (conc && map ? ` (card 1: ${ci(conc, f2)} °C and ${ci(map, f2)} °C)` : '') + `; H12, aifoundry2's clock (section 9).`,
  ];
  ul.innerHTML = L.map(x => `<li>${x}</li>`).join('');
  const d39 = D.departures.find(d => d.n === 39) || {};
  // the stopped first copy of a validation block and its re-run (departure 39): minutes from the stop to the re-run
  const stopped = D.timeline.find(r => r.card === VALCARD && /guard-stop/.test(r.dir || '') && r.t1);
  const rerun = stopped ? D.timeline.find(r => r.card === VALCARD && r.pass === stopped.pass && r.status === 'ok' && r.t0) : null;
  const gap = stopped && rerun ? (Date.parse(rerun.t0.replace(' ', 'T')) - Date.parse(stopped.t1.replace(' ', 'T'))) / 60000 : null;
  V.sumCaveats = `<b>Caveats.</b> <i>Censoring at ${f0(CL)} s.</i> Chains were capped at ${f0(CL)} s (the owner's limit), and a run cut off there counts ` +
    `as ${f0(CL)} s. Card 1's calibration chains (${MIN('ALL24')} minions, never a tested workload) were slower in the validation's Tier L blocks than ` +
    `when its start edge was set: ${f1(Lt.cal_t66.min)}–${f1(Lt.cal_t66.max)} s (median ${f1(Lt.cal_t66.median)} s) against ${f1(Math.min(...v0t))}–${f1(Math.max(...v0t))} s ` +
    `(median ${f1(v0e.median)} s) at ${D.v0.settled} °C in the calibration` + (lastAll ? `, and in the last session (blocks ${last.blocks.join(' and ')}) every Tier L run was cut off` : '') + `. ` +
    `<i>Departure 39.</i> ${esc(String(d39.title || '').replace(/\*\*/g, ''))}: the first session stopped on the idle-power guard, which compares each start with the ` +
    `session's first run and fires by construction when a Tier S block (hotter start, more idle power) follows a Tier L block; that block was re-run` +
    (gap != null ? ` ${num(gap, 1)} min after the stop (the design asks at least 15 min between queue entries)` : '') + `, the ` +
    `stopped copy is kept and never reduced, and every later session started with a Tier S block. It changed the order of blocks, not a locked file, ` +
    `parameter or analysis. <i>Scope.</i> One validation card, ${word(REG.n_val.L16)} blocks per tier; only signs were predicted, never sizes.`;
})();

function devSpan() {
  const tl = D.timeline.filter(r => r.card === DEVCARD);
  return `${dmy(tl[0].t0).replace(/ (\d\d:)/, ', $1')}–${hhmm(tl[tl.length - 1].t1)} PDT`;
}
function edgeOf(card, typ) {
  const t = D.timeline.filter(r => r.card === card && r.type === typ && r.edges.length);
  const e = [...new Set(t.flatMap(r => r.edges))];
  return e.length === 1 ? e[0] : e.join('/');
}
function verdictPhrase(id) {
  const o = outcome(id);
  return o === 'PASS' ? 'held (PASS)' : o === 'FAIL' ? 'failed (FAIL)' : `was ${o ? o.toLowerCase() : 'pending'}`;
}

/* ---------- section 2: Q1 ---------- */
(function () {
  const dv = D.q1.dv2, fw = D.q1.firmware, pr = D.q1.probes, a2 = D.q1.a2;
  V.q1Fw = `The service processor's thermal test reads one temperature: the integer mean of the minion-shire sensors ` +
    `that return a sample (all ${fw.sensors} when every one does), each truncated to a whole degree first, compared with ${fw.threshold_c} °C strictly, so it acts ` +
    `when the mean reads ${fw.threshold_c + 1}. No per-sensor or hottest-sensor path changes the clock, and the host's ` +
    `<code>temp_c.minshire[0]</code> is the same function (et-platform <code>${esc(fw.commit)}</code>, the service processor's BL2: the mean at ` +
    `<code>${esc(fw.mean_at)}</code>, the threshold <code>TEMP_THRESHOLD_SW_MANAGED</code> ${fw.threshold_c} at <code>${esc(fw.threshold_at)}</code>; ` +
    `<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage#the-loop-as-built">DVFS page, §1</a>).`;
  const idle = dv.idle && dv.idle[0];
  V.q1Dv2 = `aifoundry2 is the only card whose governor moves the clock. On its development night (28 September, E51) the ` +
    `clock held 800 MHz for at least a second after the hottest sensor read ${fw.threshold_c + 2} °C or more in ` +
    `${dv.hold_runs === dv.runs ? 'all ' + word(dv.runs) : word(dv.hold_runs) + ' of ' + word(dv.runs)} placement runs (up to ` +
    `${fw.threshold_c + dv.max_over_thr} °C). ${ucf(word(dv.separating))} runs in ${word(dv.blocks)} blocks tell the two rules apart (the hottest ` +
    `sensor read 66 °C at least 1.5 s before the mean did): ${word(dv.fit_mean)} stepped ${rng(dv.down_minus_mean[0], dv.down_minus_mean[1], f1)} s ` +
    `after the mean first read 66, and ${dv.fit_max ? word(dv.fit_max) : 'none'} within ${num(dv.window_s[0], 1)} to +${num(dv.window_s[1], 1)} s of the ` +
    `hottest sensor's 66 (all ${word(dv.separating)} came ${rng(dv.down_minus_high[0], dv.down_minus_high[1], f1)} s after it). ` +
    dv.neither.map(n => `One run (${esc(n.name)}, block ${n.block}) stepped ${f1(Math.abs(n.down_minus_mean))} s ${n.down_minus_mean < 0 ? 'before' : 'after'} the mean read 66 and fits neither rule. `).join('') +
    `${ucf(word(dv.separating))} runs over ${word(dv.blocks)} blocks are fewer than DV2's frozen count rule asks (at least ${word(dv.g1t_min.runs)} over ` +
    `${word(dv.g1t_min.blocks)} blocks), so as a count the timing test is ${esc(dv.g1t_outcome)}.` +
    (idle ? ` On the idle card at ${idle.time} the mean read ${idle.mean} °C while the hottest sensor read ${idle.high_max} °C in all ` +
      `${word(idle.samples)} samples, and the governor stayed out of its thermal state.` : '') +
    ` That is development data: its frozen validation waits for the card, whose Master Minion hung at 02:50 on 28 September ` +
    `(<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage#what-triggers-a-step-down-and-does-placement-delay-it">DVFS page, §8</a>).`;
  const p3 = pr[DEVCARD], p1 = pr[VALCARD];
  V.q1Here = `the design registered its own clock tests only where they could work: TRIG-A (the clock's step against the ` +
    `two readings) on a card whose clock moves from a die below 66 °C, TRIG-B (the governor's own trace lines) on a card ` +
    `whose probe shows its governor alive. One launch before any other work probed each card: ${lab(DEVCARD)} read ` +
    `${p3.class} (${esc(bare(p3.silent_reason))}: its zero TDP latches the governor) and ${lab(VALCARD)} ${p1.class} ` +
    `(${esc(bare(p1.silent_reason))}: its clock never leaves 600 MHz), both as predicted, so neither test was registered there. ` +
    `aifoundry2's part ran the same day, 27 September, from whatever temperature it rested at: ` +
    a2.map(a => `${a.rest_c} °C at ${hhmm(a.time)} (${a.branch})`).join(' and ') + `, both inside its thermal loop at 600 MHz, ` +
    `where the pre-registered result is NOT OBSERVABLE. So no on-card test of Q1 ran in this experiment.`;
  const t = $('q1table');
  const rows = [[lab(DEVCARD), `R0 probe, ${hhmm((D.timeline.find(r => r.card === DEVCARD && r.pass === 801) || {}).t0)}`, `${p3.rest_c} °C`, p3.class, esc(p3.prediction), p3.prediction_met ? 'yes' : 'no'],
    [lab(VALCARD), `R0 probe, ${hhmm((D.timeline.find(r => r.card === VALCARD && r.pass === 801) || {}).t0)}`, `${p1.rest_c} °C`, p1.class, esc(p1.prediction), p1.prediction_met ? 'yes' : 'no']]
    .concat(a2.map(a => ['aifoundry2', `A2 attempt ${a.attempt}, ${hhmm(a.time)}`, `${a.rest_c} °C`, a.probe_class || '—', esc(a.note), a.branch]));
  t.innerHTML = '<thead><tr><th>Card</th><th>What</th><th class="num">Rest</th><th>Probe class</th><th>Predicted, or result</th><th>Met / branch</th></tr></thead><tbody>' +
    rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td><td class="num">${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td>${r[5]}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
  V.q1Note = `A probe is one short launch with no sampler, bracketed by two dumps of the service processor's 4 KB trace ring: ` +
    `ALIVE if the governor logs, STUCK if it logs a latched thermal state, SILENT if it logs nothing. aifoundry2's branch is ` +
    `set by its rest reading: WARM at 66 °C or more (documentation only; re-checks at least two hours apart, before 22:00).`;
})();

/* ---------- section 3: the placements (chip map) ---------- */
(function () {
  const P = D.placements, G = P.grid, R = P.runs;
  const order = [['Registered (Tier L and Tier S)', ['INT16@32', 'PER16@32', 'UNI32@16']], ['Tier S only (MAP)', ['B4NE', 'B4SW']],
    ['Dropped with L8 and G8', ['INT16@16', 'PER16@16', 'MEM8', 'EDGE8', 'CEN8', 'W8b', 'E8b', 'N8b', 'S8b']], ['Calibration and preheat', ['ALL24']]];
  const sel = $('plsel');
  order.forEach(([g, names]) => {
    const og = document.createElement('optgroup'); og.label = g;
    names.filter(n => R[n]).forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = `${n} (${f0(R[n].minions)} minions)`; og.appendChild(o); });
    sel.appendChild(og);
  });
  let cur = 'PER16@32';
  sel.value = cur;
  const WHERE = {INT16: 'the 16 interior shires', PER16: 'the 16 perimeter shires', UNI32: 'all 32 shires', MEM8: 'the 8 shires beside the memory strips (west and east columns)',
    EDGE8: 'the 8 shires on the bare north and south edges', CEN8: 'the 8 shires of the centre band', W8b: 'a western block of 8', E8b: 'its mirror image in the east',
    N8b: 'a northern block of 8', S8b: 'its mirror image in the south', B4NE: '4 shires beside the I/O and PCIe corner', B4SW: 'the 4 shires of the far corner'};
  const cellOf = {};
  G.forEach((row, r) => row.forEach((lbl, c) => { const m = /^S(\d+)$/.exec(lbl); if (m) cellOf[+m[1]] = [r, c]; }));
  const f = CK.frame('plmap', {label: 'Chip map of the selected placement', minW: 300, maxW: 560, height: W => Math.round(W * 0.86) + 30, draw: f => {
    const pl = R[cur], on = new Set(pl.shires), pad = 30, side = Math.min(f.W - 2 * pad, f.H - 2 * pad - 8), cs = side / 6, x0 = (f.W - side) / 2, y0 = 22;
    const g = CK.el('g', {}, f.svg), nodes = [];
    CK.txt(g, f.W / 2, 14, 'north die edge: I/O and PCIe', 'lab', 'middle');
    CK.txt(g, f.W / 2, y0 + side + 18, 'south die edge', 'lab', 'middle');
    G.forEach((row, r) => row.forEach((lbl, c) => {
      const m = /^S(\d+)$/.exec(lbl), s = m ? +m[1] : null, x = x0 + c * cs, y = y0 + r * cs;
      const act = s != null && on.has(s), p = act ? pl.per_shire / 32 : 0;
      const cg = CK.el('g', {}, g);
      const rect = CK.el('rect', {x: x + 1.5, y: y + 1.5, width: cs - 3, height: cs - 3, rx: 4}, cg);
      if (s == null) { rect.style.fill = 'var(--code-bg)'; rect.style.stroke = 'var(--axis)'; rect.setAttribute('stroke-dasharray', '3 3'); }
      else { rect.style.fill = act ? CK.ramp(p) : 'var(--surface)'; rect.style.stroke = act ? 'none' : 'var(--grid)'; }
      const ink = act ? CK.rampInk(p) : 'var(--ink-2)';
      const t1 = CK.txt(cg, x + cs / 2, y + cs / 2 - (s != null ? 2 : -4), lbl === 'M/S' ? 'M/S' : lbl === 'IO/PCIe' ? 'I/O' : lbl, s != null ? 'lab-strong' : 'tick', 'middle');
      t1.style.fill = ink; if (cs < 50) t1.style.fontSize = '11px';
      if (s != null) { const t2 = CK.txt(cg, x + cs / 2, y + cs / 2 + 13, act ? `${pl.per_shire}` : '0', 'tick', 'middle'); t2.style.fill = ink; }
      const tip = s != null ? `<b>Shire ${s}</b> (row ${r}, column ${c + 1})<br>${act ? `${pl.per_shire} of 32 minions at work in ${esc(cur)}` : `idle in ${esc(cur)}`}`
        : lbl === 'M/S' ? '<b>Master or spare shire</b>: has a sensor in the mean; runs no kernels' : '<b>I/O and PCIe shires</b>: the I/O sensor is not in the mean; PCIe has none';
      CK.tip(f, cg, tip); nodes.push(cg);
    }));
    const [cr, cc] = pl.centroid_rc, cx = x0 + (cc - 1 + 0.5) * cs, cy = y0 + (cr + 0.5) * cs;
    const mk = CK.el('g', {'aria-hidden': 'true'}, g);
    CK.el('circle', {cx, cy, r: 5, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 2}, mk);
    CK.el('line', {x1: cx - 9, x2: cx + 9, y1: cy, y2: cy, stroke: 'var(--ink)', 'stroke-width': 1.5}, mk);
    CK.el('line', {x1: cx, x2: cx, y1: cy - 9, y2: cy + 9, stroke: 'var(--ink)', 'stroke-width': 1.5}, mk);
    CK.keynav(f, nodes);
  }});
  const read = () => {
    const pl = R[cur];
    $('plread').innerHTML = `<b>${esc(cur)}</b>: ${WHERE[pl.group] || esc(pl.group)}, ${pl.per_shire} minions each, ` +
      `${f0(pl.minions)} minions (<code>--shires ${pl.mask} --per-shire ${pl.per_shire}</code>); centroid at row ${f2(pl.centroid_rc[0])}, column ${f2(pl.centroid_rc[1])} (the cross); ` +
      `beside the I/O–PCIe cells: ${pl.by_io}, the master or spare: ${pl.by_ms}; used in ${esc(pl.types)}; ${pl.status}.`;
  };
  sel.addEventListener('change', () => { cur = sel.value; f.redraw(); read(); });
  read();
  const t = $('pltable');
  t.innerHTML = '<thead><tr><th>Placement</th><th>Mask</th><th class="num">Per shire</th><th class="num">Minions</th><th>Where</th><th class="num">Centroid (row, col)</th><th>Used in</th><th>Status</th></tr></thead><tbody>' +
    order.flatMap(o => o[1]).filter(n => R[n]).map(n => { const r = R[n]; return `<tr><td>${esc(n)}</td><td><code>${r.mask}</code></td><td class="num">${r.per_shire}</td><td class="num">${f0(r.minions)}</td>` +
      `<td>${WHERE[r.group] || esc(r.group)}</td><td class="num">${f2(r.centroid_rc[0])}, ${f2(r.centroid_rc[1])}</td><td>${esc(r.types)}</td><td>${r.status}</td></tr>`; }).join('') + '</tbody>';
  CK.sortTable(t);
  CK.stackTable(t);
  V.plIntro = `The grid is the shires' order on the mesh as the latency measurements place it (the die frame is inferred: a ` +
    `mirror image would swap west and east, or north and south, but no class). The perimeter ring holds ${f0(R['PER16@32'].shires.length)} ` +
    `compute shires and the interior ${f0(R['INT16@32'].shires.length)}; together they are all 32, and at 16 minions each they are ` +
    `exactly UNI32@16's minions. Pick a placement to see it:`;
  V.plNote = `Identities the placement code asserts: ${esc(P.identities.join('; '))}. Source: ${esc(P.source)}; ` +
    `<code>tools/claims-v3/hp/placements.py --check</code> re-derives every mask.`;
})();

/* ---------- section 4: the metric and the traces ---------- */
(function () {
  const F = REG.frozen, tr3 = D.traces[DEVCARD];
  V.metric1 = `The trip is the first time the mean reads 66 °C, so the metric is the time the same work takes to get there ` +
    `from the same start. The die's temperature at the start matters more than anything else, so every run starts from ` +
    `the same whole-degree reading of the mean, falling, after the same preheat:`;
  V.targets = `${FZ.target_S} °C before a Tier S run (start edge ${FZ.S_S} °C), the edge + ${FZ.target_L_over} °C before a Tier L run (development's edge ${edgeOf(DEVCARD, 'L16')} °C, ` +
    `${lab(VALCARD)}'s ${F.S_L} °C)`;
  const A = RUNS['ALL24'];
  V.mStep1 = `if the mean is below the target, ${word(DZ.preheat_s)}-second bursts of ${f0(A.minions)} minions (${A.per_shire} per shire everywhere) until it reads the target`;
  V.mStep3 = `in Tier L a chain of ${word(DZ.chain_launch_s)}-second launches, each a separate process under <code>timeout 10</code>, that stops ${word(DZ.chain_after_66)} ` +
    `launches after the mean reads 66 °C or at ${f0(FZ.chain_cap_s)} s; in Tier S one ${word(DZ.S_launch_s)}-second launch.`;
  V.mStep4 = `a run that never gets there counts as ${f0(DZ.C_L)} s (${f0(DZ.C_S)} s in Tier S), never dropped.`;
  const L = TRIO;
  V.metric2 = `On ${lab(DEVCARD)} a Tier L run of ${MIN('INT16@32')} minions from ${edgeOf(DEVCARD, 'L16')} °C needed ${rng(L['INT16@32'].t66.min, L['PER16@32'].t66.max, f0)} s; ` +
    `a Tier S run from ${FZ.S_S} °C crossed in ${rng(L['INT16@32'].t66_S.min, L['PER16@32'].t66_S.max, f2)} s. Tier L is the primary tier: its runs span ` +
    `many service-processor passes and add far more heat than a Tier S run, so where each sensor sits within its whole degree at the start ` +
    `matters less. The chart shows every registered run of one block; the mean is a whole number of degrees, so it steps.`;
  const cards = CK.cardsIn(Object.keys(D.traces).filter(c => Object.keys(D.traces[c]).length));
  let card = cards[0], tier = 'L16', pass = null;
  const passes = () => Object.values(D.traces[card] || {}).filter(b => b.type === tier).map(b => b.pass).sort((a, b) => a - b);
  let bseg = null;
  const mkBlock = () => {
    const ps = passes(); if (!ps.includes(pass)) pass = ps[ps.length - 1];
    bseg = CK.seg('trblock', {label: 'Block', options: ps.map(p => [p, String(p)]), value: pass, onChange: v => { pass = v; f.redraw(); cap(); }});
  };
  if (cards.length > 1) CK.cardSeg('trcard', {cards, value: card, bus: 'trcard', onChange: v => { card = v; mkBlock(); f.redraw(); cap(); }});
  else $('trcard').remove();
  CK.seg('trtier', {label: 'Tier', options: [['L16', `L: chains to ${f0(FZ.chain_cap_s)} s`], ['S', `S: one ${f0(DZ.S_launch_s)} s launch`]], value: tier, onChange: v => { tier = v; mkBlock(); f.redraw(); cap(); }});
  mkBlock();
  CK.legend('trleg', TRIOK.map(n => ({key: n, label: `${n}, ${PNAME[n]}`, color: PCOL[n], mark: PDASH[n] ? 'dash' : 'line'})));
  const f = CK.frame('traces', {label: 'Mean die temperature against time from the first launch, three placements', height: W => W < 600 ? 290 : 340, draw: f => {
    const b = (D.traces[card] || {})[pass]; if (!b) return;
    const L = f.narrow ? 36 : 44, R = f.narrow ? 12 : 110, T = 24, B = 40;
    const runs = b.runs.filter(r => TRIOK.includes(r.name));
    const tmax = Math.max(...runs.map(r => r.pts.length ? r.pts[r.pts.length - 1][0] : 0), b.type === 'S' ? 7 : 10);
    const xmax = b.type === 'S' ? Math.ceil(tmax) : Math.ceil(tmax / 10) * 10;
    const lo = Math.min(b.edge - 1, ...runs.flatMap(r => r.pts.map(p => p[1]))), hi = 67;
    const x = CK.lin(b.type === 'S' ? -1 : -3, xmax, L, f.W - R), y = CK.lin(lo - 0.5, hi + 0.5, f.H - B, T);
    const yt = []; for (let v = lo; v <= hi; v++) yt.push(v);
    CK.axes(f, {x, y, L, R, T, B, yt, yfmt: v => f0(v), xl: 'seconds from the first launch', yl: 'mean, °C'});
    const g = CK.el('g', {}, f.svg), nodes = [];
    CK.el('line', {x1: L, x2: f.W - R, y1: y(66), y2: y(66), stroke: 'var(--ref)', 'stroke-width': 1.5, 'stroke-dasharray': '6 4'}, g);
    CK.inside(f, [CK.txt(g, L + 4, y(66) - 6, 'the trip: the mean reads 66 °C', 'lab')]);
    CK.el('line', {x1: x(0), x2: x(0), y1: T, y2: f.H - B, stroke: 'var(--axis)', 'stroke-width': 1}, g);
    const labs = [];
    runs.forEach(r => {
      const pts = []; r.pts.forEach((p, k) => { if (k) pts.push([p[0], r.pts[k - 1][1]]); pts.push(p); });
      const ln = CK.el('path', {d: CK.path(pts, x, y), fill: 'none', 'stroke-width': 2, 'stroke-linejoin': 'round'}, g);
      ln.style.stroke = PCOL[r.name]; if (PDASH[r.name]) ln.setAttribute('stroke-dasharray', PDASH[r.name]);
      const tx = r.t66 != null ? r.t66 : r.C, ty = r.t66 != null ? 66 : r.pts[r.pts.length - 1][1];
      const mg = CK.el('g', {}, g);
      CK.el('circle', {cx: x(tx), cy: y(ty), r: 11, class: 'ck-hit', fill: 'transparent'}, mg);
      const c = CK.el('circle', {cx: x(tx), cy: y(ty), r: 4.5, 'stroke-width': 2}, mg);
      c.style.fill = 'var(--surface)'; c.style.stroke = PCOL[r.name];
      CK.tip(f, mg, `<b>${esc(r.name)}</b> (${PNAME[r.name]}), block ${b.pass}, ${lab(card)}<br>` +
        (r.t66 != null ? `mean first read 66 °C at ${f2(r.t66)} s` : `never read 66 °C within ${f0(r.C)} s (counted as ${f0(r.C)} s)`) +
        `<br>start edge ${b.edge} °C; switching power ${r.sw_W != null ? f2(r.sw_W) + ' W' : '— (no window before the crossing)'}; edge-cooling time ${f2(r.tau_c)} s`);
      nodes.push(mg);
      labs.push({y: y(ty), t: `${PNAME[r.name].split(',')[0]} ${r.t66 != null ? (b.type === 'S' ? f2(r.t66) : f1(r.t66)) + ' s' : '≥ ' + f0(r.C) + ' s'}`, c: PCOL[r.name], x: x(tx)});
    });
    // direct labels at the right edge, in the order of the crossings, spaced apart
    labs.sort((a, b2) => a.x - b2.x);
    const lx = f.W - R + 6; let yy = T + 10;
    if (!f.narrow) labs.forEach(l => { const t = CK.txt(g, lx, yy, l.t, 'lab'); t.style.fill = 'var(--ink-2)';
      const sw = CK.el('line', {x1: lx - 4, x2: lx - 4, y1: yy - 9, y2: yy + 2, 'stroke-width': 3}, g); sw.style.stroke = l.c; yy += 16; });
    CK.keynav(f, nodes);
  }});
  const cap = () => {
    const b = (D.traces[card] || {})[pass]; if (!b) { $('trcap').textContent = ''; return; }
    const rs = b.runs.filter(r => TRIOK.includes(r.name)), g = n => rs.find(r => r.name === n) || {};
    const i = g('INT16@32'), p = g('PER16@32');
    const tt = r => r.t66 != null ? `${b.type === 'S' ? f2(r.t66) : f1(r.t66)} s` : `more than ${f0(r.C)} s`;
    $('trcap').innerHTML = `Block ${b.pass} (${b.round.toUpperCase()}, ${lab(card)}), start edge ${b.edge} °C: 66 °C after ` +
      TRIOK.map(n => `${tt(g(n))} ${PNAME[n].split(',')[0]}`).join(', ') + '. ' +
      (i.t66 != null && p.t66 != null ? `The perimeter run took ${num(p.t66 / i.t66, 2)} times as long as the interior run (L = ${f3(Math.log(Math.min(p.t66, p.C) / Math.min(i.t66, i.C)))}). ` : '') +
      `Circles mark each run's first reading of 66 °C; hover or tab to one for its values. Before 0 s the mean is at the edge, falling; the flicker is the ` +
      `whole-degree mean crossing a degree back and forth.`;
  };
  cap();
})();

/* ---------- section 5: development ---------- */
(function () {
  const tl = D.timeline.filter(r => r.card === DEVCARD);
  const nL = tl.filter(r => r.type === 'L16').length, nS = tl.filter(r => r.type === 'S').length;
  const t0 = tl[0].t0, t1 = tl[tl.length - 1].t1;
  const mins = tl.reduce((a, r) => a + (r.minutes || 0), 0);
  const l8 = DEV.l8_block, l8m = l8.runs.filter(r => r.role === 'meas');
  const l8c = l8m.filter(r => r.censored), l8u = l8m.find(r => r.name === 'UNI32@16');
  const n = (rd, ty) => tl.filter(r => r.round === rd && r.type === ty && !r.skipped).length;
  const nVoid = DEV.blocks.filter(b => b.void && b.void.length).length;
  V.dev1 = `${lab(DEVCARD)} (release 1.3.1, clock pinned at 600 MHz) ran every development round on 27 September, ` +
    `${hhmm(t0)}–${hhmm(t1)} PDT, ${f0(mins)} minutes of blocks: R0 (a probe and a smoke run); R1 (${word(n('r1', 'SCOUT'))} scouting ` +
    `blocks that set the start edges, then ${word(n('r1', 'S'))} Tier S and ${word(n('r1', 'L16'))} Tier L blocks; the one-shot trace test ` +
    `did not apply, as the probe read ${esc(D.q1.probes[DEVCARD].class)}); R2 (${word(n('r2', 'L8'))} half-power L8 block, then ` +
    `${word(n('r2', 'L16'))} more Tier L blocks once L8 was dropped); and R3 (${word(n('r3', 'L16'))} Tier L and ${word(n('r3', 'S'))} Tier S ` +
    `blocks under the final parameters and code, the protocol the validation runs): ${word(nL)} Tier L blocks and ${word(nS)} Tier S ` +
    `blocks in all, ${nVoid ? word(nVoid) + ' void' : 'none void'}. In ${word(PT.sign_count.A_longer)} of the ` +
    `${word(PT.ci99.n)} Tier L blocks the perimeter run took longer than the interior run:`;
  let item = 'PLACE-t';
  CK.seg('ptitem', {label: 'Item', options: [['PLACE-t', 'Tier L (PLACE-t)'], ['PLACE-tS', 'Tier S (PLACE-tS)']], value: item, onChange: v => { item = v; f.redraw(); cap(); }});
  const cardsWith = () => CK.cardsIn([DEVCARD].concat(VB && VB.items && VB.items[item] && VB.items[item].values.length ? [VALCARD] : []));
  CK.legend('ptleg', CK.cardLegend(CK.cardsIn([DEVCARD, VALCARD])).map(l => Object.assign(l, {label: l.key === DEVCARD ? `${l.label} (development)` : `${l.label} (validation${VER ? '' : ', pending'})`}))
    .concat([{key: 'band', label: `±${PCT(PT.band)}%: a negligible effect`, mark: 'box', color: 'color-mix(in srgb, var(--ref) 25%, transparent)'}]));
  const t66Of = (card, pass, name) => {
    const b = card === DEVCARD ? DEV.blocks.find(x => x.pass === pass) : null;
    if (b) { const r = b.runs.find(x => x.name === name && x.role === 'meas' && !x.void.length); return r ? r.t66 : null; }
    const tb = (D.traces[card] || {})[pass]; if (!tb) return null; const r = tb.runs.find(x => x.name === name); return r ? (r.censored ? -r.C : r.t66) : null;
  };
  const tS = v => v < 0 ? `over ${f0(-v)} s (cut off)` : `${f2(v)} s`;
  const f = CK.frame('placet', {label: 'Log ratio of perimeter to interior time to 66 °C, per block, with 99% intervals per card', height: W => {
    const cs = cardsWith(); const n = cs.reduce((a, c) => a + rowsOf(c).length + 2, 0); return 60 + n * 20; }, draw: f => {
    const cs = cardsWith(), L = f.narrow ? 92 : 130, R = 16, T = 26, B = 40;
    const allv = cs.flatMap(c => rowsOf(c).map(r => r[1]));
    const civ = cs.flatMap(c => { const k = ciOf(c); return k ? [k.lo, k.hi] : []; });
    const xmin = Math.min(-0.15, ...allv, ...civ) - 0.03, xmax = Math.max(0.8, ...allv, ...civ) + 0.03;
    const x = CK.lin(xmin, xmax, L, f.W - R), band = regItem(item).band || PT.band;
    let yy = T + 8; const rowsY = [];
    cs.forEach(c => { rowsY.push({c, head: yy}); yy += 20; rowsOf(c).forEach(() => { yy += 20; }); yy += 20; });
    const H = f.H, g = CK.el('g', {}, f.svg), nodes = [];
    const xt = x.ticks(f.narrow ? 4 : 7);
    const im = (IT[item] || PT).ci99.mean;
    CK.axes(f, {x, y: CK.lin(0, 1, H - B, T), L, R, T, B, xt, yt: [], grid: false, xfmt: v => num(v, 1), xl: `L = ln(perimeter t66 / interior t66); ${f2(im)} is ${X(im)} times as long`});
    const bg = CK.el('rect', {x: x(-band), y: T, width: x(band) - x(-band), height: H - B - T}, g); bg.style.fill = 'color-mix(in srgb, var(--ref) 25%, transparent)';
    CK.el('line', {x1: x(0), x2: x(0), y1: T, y2: H - B, stroke: 'var(--ink-2)', 'stroke-width': 1}, g);
    xt.forEach(v => { if (v) CK.el('line', {x1: x(v), x2: x(v), y1: T, y2: H - B, class: 'grid-line'}, g); });
    let y0 = T + 8;
    cs.forEach(c => {
      CK.txt(g, 4, y0 + 4, lab(c) + (c === DEVCARD ? ', development' : ', validation'), 'lab-strong'); y0 += 20;
      rowsOf(c).forEach(([p, v]) => {
        CK.txt(g, L - 8, y0 + 4, `block ${p}`, 'tick', 'end');
        const mg = CK.el('g', {}, g);
        CK.el('rect', {x: x(v) - 10, y: y0 - 9, width: 20, height: 18, class: 'ck-hit', fill: 'transparent'}, mg);
        CK.cardMark(mg, c, x(v), y0, 4.5);
        const nm = item === 'PLACE-t' ? ['PER16@32', 'INT16@32'] : ['PER16@32', 'INT16@32'];
        const tp = t66Of(c, p, nm[0]), ti = t66Of(c, p, nm[1]);
        const cut = tp != null && ti != null && (tp < 0 || ti < 0);
        CK.tip(f, mg, `<b>Block ${p}</b>, ${lab(c)}<br>L = ${f3(v)}: ` + (cut ? (tp < 0 && ti < 0 ? `both runs cut off at the cap, counted as equal` : `the perimeter took at least ${X(v)} times as long`)
          : `the perimeter took ${X(v)} times as long`) + (tp != null && ti != null ? `<br>perimeter ${tS(tp)}, interior ${tS(ti)}` : ''));
        nodes.push(mg); y0 += 20;
      });
      const k = ciOf(c);
      if (k) {
        const cg = CK.el('g', {}, g);
        CK.el('rect', {x: x(k.lo) - 2, y: y0 - 9, width: x(k.hi) - x(k.lo) + 4, height: 18, class: 'ck-hit', fill: 'transparent'}, cg);
        const ln = CK.el('line', {x1: x(k.lo), x2: x(k.hi), y1: y0, y2: y0, 'stroke-width': 3, 'stroke-linecap': 'round'}, cg); ln.style.stroke = CK.card(c).color;
        const d = CK.el('rect', {x: x(k.mean) - 5, y: y0 - 5, width: 10, height: 10, transform: `rotate(45 ${x(k.mean)} ${y0})`}, cg); d.style.fill = 'var(--ink)';
        CK.txt(g, L - 8, y0 + 4, 'mean, 99%', 'lab', 'end');
        CK.tip(f, cg, `<b>${lab(c)}</b>, ${item}, ${f0(k.n)} blocks<br>mean ${f3(k.mean)} [99%: ${f3(k.lo)} to ${f3(k.hi)}]<br>` +
          `${X(k.mean)} times as long [${X(k.lo)}–${X(k.hi)}]`);
        nodes.push(cg);
      }
      y0 += 20;
    });
    CK.keynav(f, nodes);
  }});
  function rowsOf(c) {
    if (c === DEVCARD) return (IT[item] || {}).values || [];
    return VB && VB.items && VB.items[item] ? VB.items[item].values : [];
  }
  function ciOf(c) {
    if (c === DEVCARD) return (IT[item] || {}).ci99;
    const v = vItem(item); return v && v.ci99 && v.ci99.n >= 2 ? v.ci99 : null;
  }
  const cap = () => {
    const it = IT[item];
    $('ptcap').innerHTML = `Each mark is one block: the log of the perimeter run's time to 66 °C over the interior run's, from the same start. ` +
      `The shaded band is ±ln 1.10, the design's band for "no effect worth the name": a SIGN+ item fails if its whole interval lies inside it. ` +
      `${lab(DEVCARD)}: ${ci(it.ci99, f3)} over ${f0(it.ci99.n)} blocks (${ciX(it.ci99)} times as long). ` +
      (VER ? `${lab(VALCARD)}'s blocks are the ones the frozen reduction used` + (SUM && item === 'PLACE-t' && SUM.L16.pairs['both censored'] ?
        `; in ${word(SUM.L16.pairs['both censored'])} of them both runs were cut off at ${f0(SUM.C.L16)} s, which counts as L = 0 (section 8).` : '.')
        : `${lab(VALCARD)}'s validation blocks appear here when its reduction exists.`);
  };
  cap();
  const t = TRIO, pw = PT.power_w, sp = IT.SPREAD.ci99, pts = PTS.ci99;
  V.dev2 = `<b>Equal power, equal work.</b> The three placements drew ${f2(t['INT16@32'].sw_W.mean)}, ${f2(t['PER16@32'].sw_W.mean)} and ` +
    `${f2(t['UNI32@16'].sw_W.mean)} W over idle on average (interior, perimeter, everywhere); the perimeter less the interior, block by block: ` +
    `${ci(pw, f2)} W, inside the ${PW} band. Their work rates matched to within ${num(100 * Math.max(Math.abs(PT.work.lo), Math.abs(PT.work.hi)), 3)}%. ` +
    `Corrected for the small power difference, the effect is ${ci(PT.L_P, f3)}. So the perimeter's extra time does not come from drawing ` +
    `less power. Whether the edge sheds heat faster, or the 34 sensors of the mean see less of heat made beside the die's edge and the unsensed ` +
    `I/O and PCIe cells, the host cannot tell apart: it reads only the mean and two unnamed extremes.`;
  V.dev3 = `<b>The other contrasts.</b> In Tier S (one ${f0(DZ.S_launch_s)} s launch from ${FZ.S_S} °C) the perimeter took ${ciX(pts)} times as long as the interior ` +
    `(${word(PTS.sign_count.A_longer)} of ${word(pts.n)} blocks; ${f2(t['PER16@32'].t66_S.mean)} against ${f2(t['INT16@32'].t66_S.mean)} s). Spreading the work ` +
    `over every shire (UNI32@16) against the interior: ${ciX(sp)} times as long (L = ${f3(sp.mean)}). If heating added up linearly that would be ` +
    `half of PLACE-t (${f3(PT.ci99.mean / 2)}) plus a term for using half of every shire's minions rather than whole shires, which only the dropped L8 ` +
    `blocks could have separated. The hottest sensor's rise over the mean (CONC, Tier S) did not grow when the work was concentrated: ` +
    `${ci(IT.CONC.ci99, f2)} °C against a predicted positive difference. The I/O sensor warmed more with the work beside it than in the far corner ` +
    `(MAP): ${ci(IT.MAP.ci99, f2)} °C. ` +
    (PT.dhot ? `By the time the mean reached 66 °C, the hottest sensor's lead over the mean had grown ${f0(Math.abs(PT.dhot.mean))} °C ${PT.dhot.mean < 0 ? 'less' : 'more'} with the ` +
      `perimeter work than with the interior work` + (PT.dhot.lo === PT.dhot.hi ? `, in every one of the ${word(PT.dhot.n)} blocks` : ` (${ci(PT.dhot, f2)} °C)`) +
      ` (whole-degree readings; reported, not an item). ` : '') +
    `At half power (${MIN('INT16@16')} minions, L8 block ${l8.pass}, from ${edgeOfPass(l8.pass)} °C) ${word(l8c.length)} of ${word(l8m.length)} placements never ` +
    `brought the mean to 66 °C within ${f0(FZ.chain_cap_s)} s; only UNI32@16, at ${MIN('UNI32@16')} minions, did (${f1(l8u.t66)} s). That is why L8 and G8 were dropped (section 9).`;
  // the per-block table
  const tb = $('devtable'), rows = [];
  DEV.blocks.filter(b => ['L16', 'S', 'L8'].includes(b.type)).forEach(b => {
    const g = n => b.runs.find(r => r.name === n && r.role === 'meas' && !r.void.length) || {};
    const i = g('INT16@32'), p = g('PER16@32'), u = g('UNI32@16');
    const Lv = (IT[b.type === 'S' ? 'PLACE-tS' : 'PLACE-t'].values.find(v => v[0] === b.pass) || [])[1];
    const tt = r => r.t66 != null ? (b.type === 'S' ? f2(r.t66) : f1(r.t66)) : (r.censored ? `> ${f0(FZ.chain_cap_s)}` : '—');
    rows.push(`<tr><td>${b.pass}</td><td>${b.round.toUpperCase()}</td><td>${b.type}</td><td class="num">${edgeOfPass(b.pass)}</td>` +
      `<td class="num">${tt(i)}</td><td class="num">${tt(p)}</td><td class="num">${tt(u)}</td><td class="num">${Lv != null ? f3(Lv) : '—'}</td>` +
      `<td class="num">${i.sw_W != null ? f2(i.sw_W) : '—'}</td><td class="num">${p.sw_W != null ? f2(p.sw_W) : '—'}</td><td class="num">${u.sw_W != null ? f2(u.sw_W) : '—'}</td>` +
      `<td class="num">${(tc => tc.length ? rng(Math.min(...tc), Math.max(...tc), f1) : '—')(b.runs.filter(r => r.role === 'meas' && !r.void.length && r.tau_c != null).map(r => r.tau_c))}</td></tr>`);
  });
  tb.innerHTML = '<thead><tr><th>Block</th><th>Round</th><th>Type</th><th class="num">Edge, °C</th><th class="num">t66 interior, s</th><th class="num">t66 perimeter, s</th>' +
    '<th class="num">t66 everywhere, s</th><th class="num">L</th><th class="num">Power interior, W</th><th class="num">Power perimeter, W</th><th class="num">Power everywhere, W</th><th class="num">Edge-cooling time, measured runs, s</th></tr></thead><tbody>' + rows.join('') + '</tbody>';
  CK.sortTable(tb); CK.stackTable(tb);
  const tcL = (D.tauc_roles || {}).L16;
  V.devNote = `Power is the median board power over idle from 1 s after the launch to the crossing: none for an interior Tier S run on ${lab(DEVCARD)}, which crossed in ` +
    `${rng(t['INT16@32'].t66_S.min, t['INT16@32'].t66_S.max, f3)} s. ` +
    `L8 block ${l8.pass} ran INT16@16 and PER16@16 (${MIN('INT16@16')} minions); "> ${f0(FZ.chain_cap_s)}" is a run that never read 66 °C. The edge-cooling time (the mean's last degree ` +
    `before the launch) is the pre-registered covariate; with β = ${f3(DEV.beta)} the adjusted contrast was never the primary. The column gives the measured runs only, as the block-void rule reads them` +
    (tcL && tcL.first_cal ? ` (section 11): on ${andL(tcL.cards.map(lab))} the burn-in calibration run that opens a Tier L block fell through its last degree in ` +
      `${rng(tcL.first_cal[0], tcL.first_cal[1], f1)} s, the measured runs in ${rng(tcL.meas[0], tcL.meas[1], f1)} s` : '') +
    `. Source: <code>reductions/dev-r3.json</code>.`;
  function edgeOfPass(p) { const r = D.timeline.find(x => x.pass === p && x.card === DEVCARD); return r && r.edges.length ? r.edges.join('/') : '—'; }
  // the timeline table
  const tt = $('timetable');
  tt.innerHTML = '<thead><tr><th>Card</th><th>Pass</th><th>Round</th><th>Type</th><th>Start (PDT)</th><th class="num">Minutes</th><th class="num">Edge, °C</th><th>Record</th></tr></thead><tbody>' +
    D.timeline.map(r => `<tr><td>${lab(r.card)}</td><td>${esc(r.pass)}</td><td>${esc((r.round || '').toUpperCase())}</td><td>${esc(r.type || '')}</td>` +
      `<td>${esc(r.t0 ? r.t0.slice(5, 16) : '')}</td><td class="num">${r.minutes != null ? f1(r.minutes) : '—'}</td><td class="num">${r.edges.join('/') || '—'}</td>` +
      `<td class="small">${esc(r.note || '')}</td></tr>`).join('') + '</tbody>';
  CK.sortTable(tt, {filter: true, filterLabel: 'Filter blocks'}); CK.stackTable(tt);
})();

/* ---------- section 6: theories ---------- */
(function () {
  const r = id => regItem(id), dvi = id => (IT[id] || {}).ci99;
  const regText = id => { const x = r(id); return x.registered ? `<b>${x.prediction}</b> (${x.type}, n = ${f0(REG.n_val[x.type])})` : `reported, not tested: ${esc((x.reason || '').replace('(got None)', '(its 99% interval includes 0)'))}`; };
  const devText = (id, f, unit) => { const c = dvi(id); return c ? `${ci(c, f)}${unit || ''} (${f0(c.n)} blocks)` : 'no development data (type dropped)'; };
  const th = VER ? VER.theories : null;
  const a2 = D.q1.a2, bandPT = r('PLACE-t').band;
  const a2rest = a2.map(a => a.rest_c), a2br = [...new Set(a2.map(a => a.branch))];
  const H1why = `not registered: probes ${esc(probeText())}; aifoundry2 ${esc(a2br.join('/'))} at ${rng(Math.min(...a2rest), Math.max(...a2rest), f0)} °C`;
  const surv = {
    H1: ['TRIG-A, TRIG-B (clock tests)', H1why, 'firmware and DV2 development: the mean', 'not tested on a card here'],
    "H1'": ['TRIG-A, TRIG-B', 'not registered', 'contradicted by the firmware and DV2 development', 'not tested on a card here'],
    H2: ['PLACE-t (primary), PLACE-tS', `${regText('PLACE-t')}; ${regText('PLACE-tS')}`, `${devText('PLACE-t', f3)}; Tier S ${devText('PLACE-tS', f3)}`, th ? th.H2 : null],
    H3: ['PLACE-t, registered SIGN−', `not registered (PLACE-t was registered ${esc(r('PLACE-t').prediction || '')})`, devText('PLACE-t', f3), th ? th.H3 : null],
    H4: [`PLACE-t, registered EQUIV (±${PCT(bandPT)}%)`, `not registered (PLACE-t was registered ${esc(r('PLACE-t').prediction || '')})`, devText('PLACE-t', f3), th ? th.H4 : null],
    "H3'": ['GRAD-EW, GRAD-NS (G8)', regText('GRAD-EW'), 'no data: G8 dropped', 'not tested'],
    H6: ['LIN (L8)', regText('LIN'), 'no data: L8 dropped', 'not tested'],
    H7: ['CONC (Tier S)', regText('CONC'), devText('CONC', f2, ' °C'), 'not tested'],
    H8: ['MEM (L8)', regText('MEM'), 'one block, no crossing: L8 dropped', 'not tested'],
    H9: ['EDGE (L8)', regText('EDGE'), 'one block, no crossing: L8 dropped', 'not tested'],
    H10: ['MAP (Tier S)', regText('MAP'), devText('MAP', f2, ' °C'), 'not tested'],
    H11: ['every registered SIGN item', `${andL(REG.items.filter(i => i.registered).map(i => i.id))} ${REG.items.filter(i => i.registered).length === 2 ? 'both' : 'all'} PASS`, 'development cannot test transfer', th ? `${th.H11} (${th.H11_word})` : null],
    H12: ['DVFS-PLACE (aifoundry2 same day)', `NOT OBSERVABLE: aifoundry2 rested at ${rng(Math.min(...a2rest), Math.max(...a2rest), f0)} °C`, `DV2 development: the perimeter held 800 MHz ${num(D.q1.dv2.q2.ratio[0], 1)} and ≥ ${num(D.q1.dv2.q2.ratio[1], 1)} times as long (2 blocks)`, 'not tested here'],
    H13: ['POWER, WORK on every registered pair', `EQUIV ${PW} (Tier L; waived in Tier S for INT16@32) and ${WK}`, `${ci(PT.power_w, f2)} W`, th ? `${th.H13} (${th.H13_word})` : null],
  };
  V.th1 = `The design (27 September, before any card work) set out these theories and, for each, the item that would test it. ` +
    `Development then registered a prediction for card 1 mechanically: an item became a candidate only if its development ` +
    `interval excluded 0 (a sign) or lay inside its band (equivalence), and was registered only if card 1, with its own ` +
    `scatter, could resolve it in ${f0(DZ.n_min)}–${f0(DZ.n_max)} blocks. ${ucf(word(REG.family_size))} items were registered, both SIGN+ ` +
    `(PLACE-t, PLACE-tS), with POWER and WORK equivalence on their pair; the rest are reported, not tested.`;
  const t = $('thtable'), ths = D.theories;
  t.innerHTML = '<thead><tr><th>Theory</th><th>Hypothesis</th><th>Item</th><th>Registered on card 1</th><th>Development evidence</th><th>Survived?</th></tr></thead><tbody>' +
    ths.map(h => { const s = surv[h.id] || ['', '', '', '']; const w = s[3];
      return `<tr><td><b>${esc(h.id)}</b></td><td>${esc(h.text)}</td><td>${s[0]}</td><td>${s[1]}</td><td>${s[2]}</td><td>${w == null ? wordHtml(null) : `<span class="word ${/not registered/.test(w) ? 'nt' : /survived|PASS/.test(w) ? 'pass' : /refuted|FAIL/.test(w) ? 'fail' : /INSUFF|undecided/.test(w) ? 'insufficient' : 'nt'}">${esc(w)}</span>`}</td></tr>`; }).join('') + '</tbody>';
  CK.stackTable(t);
  V.thNote = `H2, H3 and H4 share one item: by DESIGN2's frozen table each survives only if PLACE-t is registered with its prediction (SIGN+, SIGN− or ` +
    `EQUIV) and PASSes, and PLACE-t could be registered with only one. Development evidence is ${lab(DEVCARD)}'s unless the row names another source (aifoundry2's DV2 night, the firmware). ` +
    `Values are the 99% interval over development blocks: L, the log ratio of times, for PLACE-t and PLACE-tS; °C for CONC and MAP; ` +
    `watts for POWER. Family: ${f0(REG.family_size)} registered items at 99% (each SIGN item holds falsely with probability 0.005 under the null); ` +
    `no correction for multiplicity. Only signs transfer between cards, never sizes.`;
})();

/* ---------- section 7: card 1's calibration ---------- */
(function () {
  const v = D.v0, cv = REG.cv, pt = r => regItem(r);
  const e0 = v.edges[0], e1 = v.edges[v.edges.length - 1];
  V.v01 = `${lab(VALCARD)} heats faster than ${lab(DEVCARD)}: from the same edge, ${e0.edge} °C, its calibration chains crossed 66 °C in a median ` +
    `${f1(e0.median)} s against ${f1(v.T_cal_s)} s, so development's start edge would not give it runs of the same kind. Before the freeze, a pre-set rule chose its edge on a workload ` +
    `that is never tested (${MIN('ALL24')} minions, three chains per edge): aim for a median t66 within ${num(v.lo_s / v.T_cal_s, 1)}–${num(v.hi_s / v.T_cal_s, 0)} times ${lab(DEVCARD)}'s ` +
    `(${f1(v.T_cal_s)} s, its R3 calibration chains at ${edgeOf(DEVCARD, 'L16')} °C), lower the edge if faster, raise it if slower or if any chain never crosses.`;
  CK.legend('v0leg', CK.cardLegend(CK.cardsIn([VALCARD, DEVCARD])).map(l => Object.assign(l, {label: l.key === DEVCARD ? `${l.label}: its R3 calibration chains (T_cal)` : `${l.label}: V0 chains`}))
    .concat([{key: 'band', label: `accept: ${num(D.v0.lo_s / D.v0.T_cal_s, 1)}–${num(D.v0.hi_s / D.v0.T_cal_s, 0)} × T_cal`, mark: 'box', color: 'color-mix(in srgb, var(--ref) 22%, transparent)'}]));
  const a3 = DEV.cal_r3_L16;
  CK.frame('v0chart', {label: 'Calibration chain t66 by start edge', height: W => W < 600 ? 260 : 290, draw: f => {
    const L = 44, R = 16, T = 24, B = 44;
    const cats = [{k: 'a3', label: `${lab(DEVCARD)}, ${edgeOf(DEVCARD, 'L16')} °C`, card: DEVCARD, vals: a3}]
      .concat(v.edges.map(e => ({k: String(e.pass), label: `${lab(VALCARD)}, ${e.edge} °C`, card: VALCARD, vals: e.t66, e})));
    const x = CK.lin(-0.5, cats.length - 0.5, L, f.W - R), y = CK.lin(0, Math.max(60, Math.ceil(v.hi_s / 10) * 10 + 5), f.H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xt: [], yl: 't66, s'});
    const g = CK.el('g', {}, f.svg), nodes = [];
    const bd = CK.el('rect', {x: L, y: y(v.hi_s), width: f.W - R - L, height: y(v.lo_s) - y(v.hi_s)}, g); bd.style.fill = 'color-mix(in srgb, var(--ref) 22%, transparent)';
    CK.el('line', {x1: L, x2: f.W - R, y1: y(v.T_cal_s), y2: y(v.T_cal_s), stroke: 'var(--ref)', 'stroke-width': 1.5, 'stroke-dasharray': '6 4'}, g);
    CK.inside(f, [CK.txt(g, f.W - R - 4, y(v.T_cal_s) - 6, `T_cal ${f1(v.T_cal_s)} s`, 'lab', 'end'), CK.txt(g, f.W - R - 4, y(v.lo_s) + 14, `0.5 × T_cal`, 'tick', 'end')]);
    cats.forEach((c, i) => {
      const t1 = CK.txt(g, x(i), f.H - B + 16, c.label, 'tick', 'middle');
      if (f.narrow) t1.textContent = c.label.replace(lab(c.card) + ', ', c.card === DEVCARD ? 'a3, ' : 'card 1, ');
      c.vals.forEach((val, j) => {
        if (val == null) return;
        const mg = CK.el('g', {}, g), xx = x(i) + (j - (c.vals.length - 1) / 2) * 14;
        CK.el('circle', {cx: xx, cy: y(val), r: 10, class: 'ck-hit', fill: 'transparent'}, mg);
        CK.cardMark(mg, c.card, xx, y(val), 4.5);
        CK.tip(f, mg, `<b>${esc(c.label)}</b>, chain ${j + 1}<br>t66 ${f2(val)} s` + (c.e ? `<br>pass ${c.e.pass}; median ${f2(c.e.median)} s: ${c.e.rule}` : `<br>R3 calibration chain; the median is T_cal`));
        nodes.push(mg);
      });
      if (c.e) CK.txt(g, x(i), y(Math.max(...c.vals)) - 12, c.e.rule, 'lab', 'middle');
    });
    CK.inside(f, [...f.svg.querySelectorAll('text')]);
    CK.keynav(f, nodes);
  }});
  $('v0cap').textContent = `Each mark is one calibration chain's time to 66 °C. From ${e0.edge} °C card 1 crossed in a median ${f1(e0.median)} s, under half of T_cal, so the rule lowered the edge; ` +
    `from ${e1.edge} °C the median was ${f1(e1.median)} s, inside the band, and the edge settled at ${v.settled} °C. The third calibration block ended at once, as the rule had settled.`;
  const p = pt('PLACE-t'), ps = pt('PLACE-tS');
  V.v02 = `The same chains set how noisy card 1 is: the run-to-run spread of ln t66 was ${f3(cv.card1)} on card 1 against ${f3(cv.aifoundry3)} on ` +
    `${lab(DEVCARD)}, a ratio of ${f2(cv.ratio_used)}, so development's block-to-block spread was scaled up by that much before asking how many ` +
    `blocks card 1 needs. PLACE-t: spread ${f3(p.s_card1)}, projected 99% half-width ${f3(p.h_at_n_val)} at n = ${f0(REG.n_val.L16)}, under ` +
    `0.7 × the development estimate (${f3(p.target_h)}): registered with ${f0(REG.n_val.L16)} blocks. PLACE-tS: ${f3(ps.h_at_n_val)} against ${f3(ps.target_h)}, ` +
    `${f0(REG.n_val.S)} blocks. The frozen parameters: Tier L from ${REG.frozen.S_L} °C (preheat to ${REG.frozen.S_L + REG.frozen.target_L_over}), Tier S from ` +
    `${REG.frozen.S_S} °C (preheat to ${REG.frozen.target_S}), chains capped at ${f0(REG.frozen.chain_cap_s)} s.`;
})();

/* ---------- section 8: verdicts ---------- */
(function () {
  const regd = REG.items.filter(i => i.registered);
  const rowsIds = [];
  regd.forEach(i => { rowsIds.push(i.id); (i.power_work_pairs || []).forEach(() => { rowsIds.push(i.id + '/POWER'); rowsIds.push(i.id + '/WORK'); }); });
  rowsIds.push('H11', 'TRIG-A');
  const pred = id => { const b = id.split('/')[0], r = regItem(b); if (id === 'H11') return 'every SIGN item PASS'; if (id === 'TRIG-A') return 'the mean (source)';
    if (/POWER$/.test(id)) return `EQUIV ${PW}`; if (/WORK$/.test(id)) return `EQUIV ${WK}`; return `${r.prediction}, band ±${f3(r.band)}`; };
  const valStr = (id, x) => {
    if (!x || !x.ci99) return x && x.of ? esc(andL(x.of.map((o, k) => `${o} ${x.words[k]}`))) : '—';
    const c = x.ci99;
    if (/POWER$/.test(id)) return `${ci(c, f2)} W` + (x.tier_L_ci99 ? `; Tier L ${ci(x.tier_L_ci99, f2)} W` : '');
    if (/WORK$/.test(id)) return `${ci(c, v => num(100 * v, 3))}%`;
    return `${ci(c, f3)}; ${ciX(c)}×`;
  };
  const TRIGA_NOTE = `waived in PREREG (departure 19): no card-1 clock-step protocol, and card 1's clock never leaves 600 MHz (probe ${esc(D.q1.probes[VALCARD].class)})`;
  const isWaived = id => /\/POWER$/.test(id) && (regItem(id.split('/')[0]).power_waived_pairs || []).length > 0;
  // the waiver's reason, scoped to the card it held on: the reducer's own note gives aifoundry3's "< 1 s"
  const intS3 = TRIO['INT16@32'].t66_S, intS1 = SUM ? SUM.S.placements['INT16@32'] : null;
  const WAIVE_WHY = `waived in PREREG (departure 37): on ${lab(DEVCARD)} an interior Tier S run crossed in ${rng(intS3.min, intS3.max, f3)} s, before the 1 s power window opens`;
  const waiveNote = id => WAIVE_WHY + (intS1 && intS1.t66.length ? `; on ${lab(VALCARD)} it crossed in ${rng(Math.min(...intS1.t66), Math.max(...intS1.t66), f2)} s, so the reduction ` +
    `computed a value (reported here, not an outcome); the reducer's note repeats the development reason` : '');
  const t = $('vtable');
  t.innerHTML = '<thead><tr><th>Item</th><th>Prediction</th><th>Card 1 value [99%]</th><th>Outcome</th><th>Note</th></tr></thead><tbody>' +
    rowsIds.map(id => { const x = vItem(id); return `<tr><td>${esc(id)}</td><td>${pred(id)}</td><td>${VER ? valStr(id, x) : 'pending'}</td>` +
      `<td>${VER ? wordHtml(x ? x.outcome : '—') : wordHtml(id === 'TRIG-A' ? 'not tested (waived in PREREG)' : isWaived(id) ? 'waived: no window in Tier S; see Tier L' : null)}</td><td class="small">${id === 'TRIG-A' ? TRIGA_NOTE : isWaived(id) ? waiveNote(id) : x && (x.reason || x.note) ? esc(x.reason || x.note) : ''}</td></tr>`; }).join('') + '</tbody>';
  CK.stackTable(t);
  const OUTCOME_WORDS = `Outcome words: PASS (the prediction holds), FAIL (the opposite sign, or an interval wholly inside the band), ` +
    `INSUFFICIENT (neither, or fewer than the frozen number of usable blocks). Tier S POWER is waived for pairs with INT16@32, because on ${lab(DEVCARD)} ` +
    `its power window was empty (it crossed in under a second; see the row's note for ${lab(VALCARD)}); the Tier L value stands for it.`;
  if (!VER) {
    V.vIntro = `<span class="word pending">Pending.</span> The validation on ${lab(VALCARD)} runs the frozen protocol: ${f0(REG.n_val.L16)} Tier L and ` +
      `${f0(REG.n_val.S)} Tier S blocks, each type's first ${f0(REG.n_val.L16)} usable blocks in pass order, never more; every block checks the PREREG ` +
      `hash, the parameters, the code and the binaries before it touches the card. This section fills in from its reduction (<code>val.json</code>, ` +
      `<code>reduce.py --val</code>), with no other change to the page.`;
    V.vNote = OUTCOME_WORDS;
  } else {
    const b = VER.blocks || {};
    V.vIntro = `The frozen reduction of ${lab(VER.card || VALCARD)}'s validation blocks (${esc(D.val_json || 'val.json')}): ` +
      `${Object.entries(b.used || {}).map(([k, n]) => `${f0(n)} of ${f0((b.n_val || {})[k])} ${k} blocks used`).join(', ')}` +
      `${VER.lock ? `; the PREREG lock held (${esc(VER.lock.why || '')})` : ''}.`;
    const ex = Object.entries(b.extra_blocks_not_used || {}).map(([k, ps]) => `${k} ${ps.join(', ')}`);
    const vo = Object.entries(b.void_or_incomplete || {}).map(([k, bs]) => `${k} ${bs.map(x => x.pass).join(', ')}`);
    V.vNote = OUTCOME_WORDS + ' ' + (vo.length ? `Void or incomplete, replaced by later blocks where there were any: ${esc(vo.join('; '))}. ` : 'No validation block was void or incomplete. ') +
      (ex.length ? `Usable blocks beyond the frozen number, listed and never used: ${esc(ex.join('; '))}.` : 'No block beyond the frozen number ran.');
  }
  if (!VER || !SUM) {
    V.vCens = `Card 1's blocks, run by run, appear here with the verdicts.`;
    $('vbtable').innerHTML = '';
    V.vbNote = `Pending: no validation block has been reduced.`;
  } else {
    const Lt = SUM.L16, CL = SUM.C.L16, sc = VB.items['PLACE-t'].sign_count || {};
    const bySess = Lt.blocks.reduce((a, b) => { if (!a.includes(b.session)) a.push(b.session); return a; }, []);
    V.vCens = `<b>The primary test, ${wordHtml(outcome('PLACE-t'))}: most runs met the ${f0(CL)} s cap.</b> On ${lab(VALCARD)}, from its frozen start edge of ${FZ.S_L} °C, ` +
      `${f0(Lt.censored)} of the ${f0(Lt.runs)} Tier L runs never brought the mean to 66 °C before the cap ended them: ` +
      `${andL(TRIOK.map(n => `${n} ${f0(Lt.placements[n].censored)} of ${f0(Lt.placements[n].n)}`))}; by session, ` +
      `${andL(bySess.map(k => `${f0(Lt.by_session[k].censored)} of ${f0(Lt.by_session[k].runs)} in session ${k}`))}. The reduction counts a cut-off run at the cap, as fixed ` +
      `in the design, so a block with both runs cut off gives L = 0: the perimeter was longer in ${word(sc.A_longer)} blocks, the interior in ` +
      `${sc.B_longer ? word(sc.B_longer) : 'none'}, and ${word(sc.ties)} were tied (exact two-sided p = ${f2(sc.p_two_sided)}). The mean of L, ${f3(vItem('PLACE-t').ci99.mean)}, ` +
      `mixes ${word(sc.A_longer + (sc.B_longer || 0))} measured contrasts with ${word(sc.ties)} ties forced by the cap, so its interval is wide.`;
    const tl = p => D.timeline.find(r => r.card === VALCARD && r.pass === p && r.status === 'ok') || {};
    const rows = ['L16', 'S'].flatMap(ty => SUM[ty].blocks.map(b => {
      const C = SUM.C[ty], fmt = ty === 'S' ? f2 : f1, t = r => !r ? '—' : r.censored ? `> ${f0(C)}` : fmt(r.t66);
      const Lv = (VB.items[ty === 'S' ? 'PLACE-tS' : 'PLACE-t'].values.find(v => v[0] === b.pass) || [])[1];
      return `<tr><td>${b.pass}</td><td>${ty === 'S' ? 'S' : 'L'}</td><td>${esc(b.session || '')}</td><td>${esc((tl(b.pass).t0 || '').slice(5, 16))}</td>` +
        `<td class="num">${t(b.runs['INT16@32'])}</td><td class="num">${t(b.runs['PER16@32'])}</td><td class="num">${t(b.runs['UNI32@16'])}</td>` +
        `<td class="num">${Lv != null ? f3(Lv) : '—'}</td><td class="num">${b.cal_t66.length ? b.cal_t66.map(fmt).join(', ') : '—'}</td></tr>`;
    }));
    const vt = $('vbtable');
    vt.innerHTML = '<thead><tr><th>Block</th><th>Tier</th><th>Session</th><th>Start (PDT)</th><th class="num">t66 interior, s</th><th class="num">t66 perimeter, s</th>' +
      '<th class="num">t66 everywhere, s</th><th class="num">L</th><th class="num">Calibration chains, s</th></tr></thead><tbody>' + rows.join('') + '</tbody>';
    CK.sortTable(vt); CK.stackTable(vt);
    const st = Object.entries(SUM.sessions).sort((a, b) => a[1] < b[1] ? -1 : 1).map(([k, v]) => `${k} from ${dmy(v)}`);
    V.vbNote = `The ${f0(Lt.blocks.length + SUM.S.blocks.length)} blocks the frozen reduction used. "> ${f0(CL)}" (Tier L) or "> ${f0(SUM.C.S)}" (Tier S) is a run the cap ended ` +
      `before the mean read 66 °C. L is ln(perimeter t66 / interior t66) with a cut-off run counted at the cap. Calibration chains: the block's ${MIN('ALL24')}-minion ` +
      `preheat-and-check runs, never a tested workload (a missed edge voids one). Sessions, from the queue logs: ${esc(andL(st))}. The stopped first copy of 9101 ` +
      `(departure 39) is kept in the data with status "fail" and is not a block the reduction reads.`;
  }
  const th = VER ? VER.theories : null;
  const S = [
    ['H1: the mean', 'not tested on a card in this experiment', `firmware source; DV2 development on aifoundry2 (${D.q1.dv2.fit_mean} of ${D.q1.dv2.separating} telling runs)`],
    ["H1': the hottest sensor", 'not tested on a card in this experiment', 'contradicted by the same evidence'],
    ['H2: the edges trip later', th ? `${th.H2} (PLACE-t ${outcome('PLACE-t')})` : 'pending', 'PLACE-t' + (th && th.H2_S ? `; Tier S, PLACE-tS: ${th.H2_S}` : '')],
    ['H3: the centre trips later', th ? th.H3 : 'pending', `needs PLACE-t registered SIGN−; it was registered ${regItem('PLACE-t').prediction}` +
      (th && th.H3_reading ? `. Outside the frozen rules, this page's reading of PLACE-t's interval against 0: ${th.H3_reading}` : '') +
      (th && vItem('PLACE-tS') && vItem('PLACE-tS').ci99 && vItem('PLACE-tS').ci99.lo > 0 ? '; Tier S (reported): the interval lies above 0' : '')],
    ['H4: only total power matters', th ? th.H4 : 'pending', `needs PLACE-t registered EQUIV; it was registered ${regItem('PLACE-t').prediction}` +
      (th && th.H4_reading ? `. Outside the frozen rules, this page's reading of PLACE-t's interval against the ±${PCT(REG.items.find(i => i.id === 'PLACE-t').band)}% band: ${th.H4_reading}` : '') +
      (th && vItem('PLACE-tS') && vItem('PLACE-tS').ci99 && vItem('PLACE-tS').ci99.lo > REG.items.find(i => i.id === 'PLACE-t').band ? '; Tier S (reported): wholly above it' : '')],
    ['H11: the sign transfers to another card', th ? `${th.H11} (${th.H11_word})` : 'pending', andL(REG.items.filter(i => i.registered).map(i => i.id))],
    ['H13: equal power', th ? `${th.H13} (${th.H13_word})` : 'pending', "POWER on PLACE-t's pair"],
    ["H3', H6, H7, H8, H9, H10, H12", 'not tested', 'section 9: dropped, or not registered'],
  ];
  const st = $('survtable');
  st.innerHTML = '<thead><tr><th>Theory</th><th>Result</th><th>On what</th></tr></thead><tbody>' +
    S.map(s => `<tr><td>${esc(s[0])}</td><td>${/pending/.test(s[1]) ? wordHtml(null) : `<span class="word ${/not registered/.test(s[1]) ? 'nt' : /survived|PASS/.test(s[1]) ? 'pass' : /refuted|FAIL/.test(s[1]) ? 'fail' : /INSUFF|undecided/.test(s[1]) ? 'insufficient' : 'nt'}">${esc(s[1])}</span>`}</td><td>${esc(s[2])}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(st);
  const bp = REG.items.find(i => i.id === 'PLACE-t').band;
  V.survNote = `DESIGN2's frozen table ("Theories survived"): "H2 / H3 / H4: PLACE-t registered SIGN+ / SIGN− / EQUIV, and it PASSes"; ` +
    `"H11: every registered SIGN item PASSes". PLACE-t was registered ${esc(regItem('PLACE-t').prediction)}, so only H2 has a frozen entry, and H3 and H4 are ` +
    `"not registered". The table defines only "survived": this page calls a theory refuted when its registered item FAILs, and undecided otherwise. ` +
    `The readings of H3 and H4 in the last column are the page's own, outside the frozen rules, from PLACE-t's 99% interval on card 1 once it has its ` +
    `${f0(REG.n_val.L16)} blocks: for H3, above 0 against it and below 0 for it; for H4, wholly outside ±${f3(bp)} (±${PCT(bp)}%) against it and wholly inside for it; ` +
    `anything else undecided. "Not tested" and "not registered" never count as survived.`;
})();

/* ---------- section 9: dropped ---------- */
(function () {
  const l8 = DEV.l8_block, l8m = l8.runs.filter(r => r.role === 'meas'), l8c = l8m.filter(r => r.censored);
  const dep = n => D.departures.find(d => d.n === n) || {};
  const r = id => regItem(id);
  const k = DEV.kappa;
  const edgeP = p => { const x = D.timeline.find(y => y.card === DEVCARD && y.pass === p); return x && x.edges.length ? x.edges.join('/') : '?'; };
  const half = RUNS['INT16@16'].minions;
  const sc = DEV.blocks.find(b => b.type === 'SCOUT' && b.runs.some(x => x.role === 'meas' && RUNS[x.name] && RUNS[x.name].minions === half));
  const scm = sc.runs.filter(x => x.role === 'meas' && !x.void.length);
  const L = [
    `<b>L8 and G8</b> (half power, ${MIN('INT16@16')} minions: MEM, EDGE, PLACE8-t, LIN; the airflow pairs GRAD-EW and GRAD-NS). The rule set in advance (D-L8): ` +
    `move the half-power start edge until a scouting run reaches 66 °C, and if even the highest allowed edge, ${DZ.ranges.S_L8[1]} °C, leaves one short within ` +
    `${f0(FZ.chain_cap_s)} s, drop both types. The scouting block at ${edgeP(sc.pass)} °C (R1b, ${sc.pass}) crossed in ${scm.filter(x => !x.censored).length ? word(scm.filter(x => !x.censored).length) : 'none'} of its ${word(scm.length)} half-power runs ` +
    `(${esc(andL([...new Set(scm.map(x => x.name))]))}), so the edge rose to ${edgeP(l8.pass)} °C; there R2's L8 block (${l8.pass}) crossed with ` +
    `${word(l8m.length - l8c.length)} of its ${word(l8m.length)} placements, the one at ${MIN('UNI32@16')} minions, while ${andL(l8c.map(x => x.name))} never did. ` +
    `At half power the die's steady state on ${lab(DEVCARD)} lies near or under 66 °C, so their time to the trip would measure how close the steady state is, not placement. ` +
    `R2 ran ${word(D.timeline.filter(x => x.card === DEVCARD && x.round === 'r2' && x.type === 'L16').length)} more Tier L blocks instead (the design's fallback), and the ` +
    `memory-strip, bare-edge, linearity and airflow theories (H8, H9, H6, H3') were not tested.`,
    `<b>The coupling gain κ</b> (PLACE-κ, PLACE-κ-S: a thermal-network fit per run). Its gate, a ${f0(100 * DZ.kappa_gate)}% whole-degree match between the fitted network and the readings, ` +
    `passed in ${word(k.L16[0])} of ${f0(k.L16[1])} Tier L runs (the blocks' networks matched ${f2(k.match[0])}–${f2(k.match[1])} of their calibration samples). Development could have ` +
    `lowered the gate to ${num(DZ.ranges.kappa_gate[0], 2)}; it was kept at the design's ${num(DZ.kappa_gate, 2)} before any validation data (departure 38), so both items are reported, not tested.`,
    `<b>CONC</b> (H7, concentration lifts the hottest sensor): its fixed prediction, SIGN+, was not supported by development (${ci((IT.CONC || {}).ci99, f2)} °C), so it was not registered.`,
    `<b>MAP</b> (H10): development supported SIGN+ (${ci((IT.MAP || {}).ci99, f2)} °C), but card 1 could not resolve it at ${f0(REG.n_val.S)} blocks: ${esc(r('MAP').reason || '')}.`,
    `<b>Q1 on a card</b> (TRIG-A, TRIG-B, H12): the probes read ${esc(probeText())}, and aifoundry2 rested in its thermal loop at every attempt (${esc(D.q1.a2.map(a => a.rest_c + ' °C').join(', '))}; section 2). ` +
    `TRIG-A on card 1 is also waived by design (departure 19): its clock never moves.`,
    `<b>Tier S power for INT16@32 pairs</b>: on ${lab(DEVCARD)} an interior Tier S run crossed in ${rng(TRIO['INT16@32'].t66_S.min, TRIO['INT16@32'].t66_S.max, f3)} s, before the 1 s power window opens, ` +
    `so POWER was waived there before the freeze and rests on Tier L (departure 37); WORK is not waived.` +
    (SUM && vItem('PLACE-tS/POWER') && vItem('PLACE-tS/POWER').ci99 ? ` On ${lab(VALCARD)} the interior run crossed in ${rng(Math.min(...SUM.S.placements['INT16@32'].t66), Math.max(...SUM.S.placements['INT16@32'].t66), f2)} s, ` +
      `so a value exists: ${ci(vItem('PLACE-tS/POWER').ci99, f2)} W, inside ${PW}, reported and not an outcome (the waiver stands as frozen).` : ''),
    `<b>G0</b>, a thermal-network fit of earlier heat curves to predict the half-power steady state before R2, was not implemented (departure 17); R2's L8 block answered the same question on the card.`,
  ];
  $('droplist').innerHTML = L.map(x => `<li>${x}</li>`).join('');
})();

/* ---------- section 10: departures ---------- */
(function () {
  const ds = D.departures;
  V.depN = f0(ds.length);
  const late = ds.filter(d => /coordinator decision/.test(d.text));
  const post = ds.filter(d => /^\*\*[^*]+\*\* \(recorded [^)]*after the validation/.test(d.text));
  V.dep1 = `The code departs from the design in ${word(ds.length) === f0(ds.length) ? f0(ds.length) : word(ds.length)} places, each written into the tools' README with its reason, ` +
    `most of them before any data or while development ran, none after the freeze in a locked file (seeds, pass numbering, the ring parser, the statistics' edge cases, ` +
    `the safety guards, and fixes found in development such as the reducer reading each block's own parameters). ${ucf(word(late.length))} were decisions made after ` +
    `development data and before any validation data, or during the validation without changing a locked file: ` +
    late.map(d => `${d.n}, ${esc(d.title.replace(/\*\*/g, ''))}`).join('; ') + `. The last, after the first validation session's safety stop: card 1's idle power grows ` +
    `with the die temperature, so a Tier S block after a Tier L block tripped the 2 W idle-power guard by construction; every session since starts with a Tier S block.` +
    (post.length ? ` ${post.length === 1 ? 'One was' : ucf(word(post.length)) + ' were'} recorded after the validation, from its review, for a reading the locked reducer already ` +
      `applied: ` + post.map(d => `${d.n}, ${esc(d.title.replace(/\*\*/g, ''))}`).join('; ') + '.' : '');
  $('deplist').innerHTML = ds.map(d => `<li value="${d.n}"${/coordinator decision/.test(d.text) ? ' class="late"' : ''}>${md(d.text)}</li>`).join('');
})();

/* ---------- section 11: method ---------- */
(function () {
  V.mCards = `Development on ${lab(DEVCARD)} (firmware 1.3.1; its zero TDP pins the clock at 600 MHz and latches the governor). Calibration and ` +
    `validation on ${lab(VALCARD)} (1.2.0; 600 MHz in every sample). aifoundry2 (1.3.1, the only card whose governor moves the clock) only for Q1's ` +
    `same-day attempts. Every sample of every kept run read 600 MHz.`;
  const nVoidDev = DEV.blocks.filter(b => b.void && b.void.length && ['L16', 'S', 'L8'].includes(b.type)).length;
  V.mSafety = `No run may take the die to ${DZ.abs_stop_c} °C: a run ends at ${word(DZ.cap_consecutive)} samples in a row with the mean at ${DZ.cap_mean_c} °C, a hottest ` +
    `sensor at ${DZ.cap_high_c} °C or board power at ${DZ.cap_board_w} W, and the session stops at ${DZ.abs_stop_c} °C. On aifoundry1, card 0 overheats and is never ` +
    `used: a read-only sampler watched it through every card-1 block and would have stopped card 1's work had it read above ${DZ.guard_stop_c} °C, and card 1's idle ` +
    `power at each start edge could rise by at most ${num(DZ.guard_widle_rise_w, 0)} W over the session's first measured run (the proxy that stopped the first validation ` +
    `session, departure 39). Every process ran under <code>timeout 10</code> with the card's lock held; nothing on any card was set except, where allowed, the ` +
    `service processor's log level (never needed: every probe read ${esc([...new Set(Object.values(D.q1.probes).map(p => p.class).concat(D.q1.a2.map(a => a.probe_class).filter(Boolean)))].join(' or '))}).`;
  V.mVoid = `a run is void on a heater error, a sample off 600 MHz, a missed edge (${f0(DZ.edge_wait_cap_s)} s), a sampler gap over 1 s, a safety stop, or work ` +
    `outside ±${f0(100 * DZ.void_work)}% of the block median, and is re-run once at the block's end; a block is void if a measured run's edge-cooling time falls outside ` +
    `${num(DZ.void_tauc_lo, 1)}–${num(DZ.void_tauc_hi, 0)} × the block median or its idle power ranges over more than ${num(DZ.void_widle_range_w, 0)} W. ` +
    `${nVoidDev ? ucf(word(nVoidDev)) + ' development blocks were void.' : 'No development block was void.'}` + (() => {
      const tl = (D.tauc_roles || {}).L16; if (!tl || !tl.first_cal) return '';
      return ` The design's words are "any run's"; the locked reducer reads the measured runs only (departure 40). The burn-in calibration run that opens a Tier L block ` +
        `is reached by preheat bursts from a cooler die, and fell through its last degree in ${rng(tl.first_cal[0], tl.first_cal[1], f1)} s against ` +
        `${rng(tl.meas[0], tl.meas[1], f1)} s for the measured runs; counted, it would void ${tl.literal_void === tl.blocks ? 'every one' : f0(tl.literal_void)} of the ` +
        `${word(tl.blocks)} Tier L blocks on ${andL(tl.cards.map(lab))}.`; })();
  V.mStats = `The unit is the block; samples and launches are never the unit. A SIGN+ item holds when its 99% interval over the blocks lies above 0, fails ` +
    `when it lies below 0 <i>or wholly inside ±band</i> (the effect shown negligible), and is inconclusive otherwise; EQUIV holds inside ±band. The time band ` +
    `is ln ${num(Math.exp(DZ.band_t), 2)} (±${PCT(DZ.band_t)}%), power ${PW}, work ${WK}. Only signs transfer between cards, never magnitudes: ${lab(VALCARD)} ` +
    `heats faster than ${lab(DEVCARD)} from the same start (section 7).`;
  V.dataVal = VER ? `from these and from <code>val.json</code>, the validation's frozen reduction` : `from these; it reads <code>val.json</code>, the validation's frozen reduction, when that file exists`;
  V.shaFull = SHA;
})();

/* ---------- fill ---------- */
document.querySelectorAll('[data-v]').forEach(e => {
  const k = e.getAttribute('data-v');
  if (V[k] == null) { console.error('heat-placement: no value for ' + k); return; }
  e.innerHTML = V[k];
});
