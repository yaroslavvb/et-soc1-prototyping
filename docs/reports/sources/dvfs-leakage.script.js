/* The DVFS loop and its leakage. D is dvfs.json with the three-machine block (cards) merged in by
   build_cards_data.py --merge; CK is the shared chart toolkit (docs/reports/sources/chartkit.js).
   Every number the page prints is computed here from D; the body's <span data-v="…"> fields are filled at the end. */
const num = CK.fmt.num, f0 = v => num(v, 0), f1 = v => num(v, 1), f2 = v => num(v, 2);
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

/* The governor's rule at 353f20e, as §1 reduces it: the frequency check is nested inside the thermal test. */
function rule(T, P, f) {
  if (T > TC) return f > FMIN ? {line: 1, act: 'down', test: 'thermal'} : {line: 2, act: 'hold', test: 'floor'};
  if (P > TW && f > FMIN) return {line: 3, act: 'down', test: 'power'};
  if (P < TW && f < FMAX) return {line: 4, act: 'up'};
  return {line: 5, act: 'hold'};
}
const CODE = [
  `if T &gt; ${TC} °C:`,
  `    if f &gt; ${FMIN}: step DOWN (thermal)`,
  `    else:       hold (power not tested)`,
  `elif P &gt; ${TW} W and f &gt; ${FMIN}: step DOWN (power)`,
  `elif P &lt; ${TW} W and f &lt; ${FMAX}: step UP`,
  `else:              hold`,
  `master minion idle: back to ${FMIN} MHz`];
const say = r => (r.act === 'down' ? `the ${r.test} test fires: step down`
  : r.act === 'up' ? `neither test fires and power is under ${TW} W: step up`
  : r.test === 'floor' ? 'the thermal test fires at the floor: hold, and the power tests are not reached' : 'hold');
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
            `the service processor most likely read a different value between our samples (§8).</span>`;
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
    `the service processor most likely read its sensors between our 10 Hz samples, on its own ~133 ms pass (§8).`;
  return {select(r) { stop(); if (r.run !== st.run) { st.run = r.run; seg.set(r.run); selectRun(r.run, r.i); } else setIdx(r.i); }};
})();

/* ---------- the down-steps against the two thresholds ---------- */
(function () {
  let mode = 'after';
  CK.seg('attrib-mode', {label: 'Read the sample', options: [['after', 'just after the step'], ['before', 'just before it']],
    value: mode, onChange: v => { mode = v; frame.redraw(); }});
  const tip = (r, why) => `<b>Run ${r.run + 1} · ${r.values}</b>, ${r.f0}→${r.f1} MHz at ${f2(r.t)} s<br>` +
    `just before: die ${f0(r.T_prev)} °C, board ${f1(r.P_prev)} W → ${r.why_prev}<br>` +
    `just after: die ${f0(r.T)} °C, board ${f1(r.P)} W → ${r.why}<br>Selecting it replays the step in the chart above`;
  function draw(f) {
    const W = f.W, H = f.H, L = 44, R = 12, T = 26, B = 40;
    const x = CK.lin(62.5, 68.5, L, W - R), y = CK.lin(25, 95, H - B, T);
    CK.axes(f, {x, y, L, R, T, B, xt: [63, 64, 65, 66, 67, 68], yt: [30, 50, 70, 90],
      xl: 'die temperature on that sample, °C (whole degrees)', yl: 'board power on that sample, W'});
    const dash = a => CK.el('line', Object.assign({stroke: 'var(--bad)', 'stroke-width': 1.3, 'stroke-dasharray': '5 4'}, a), f.svg);
    dash({x1: x(TC + 0.5), x2: x(TC + 0.5), y1: T, y2: H - B}); dash({x1: L, x2: W - R, y1: y(TW), y2: y(TW)});
    CK.txt(f.svg, x(TC + 0.5) + 5, T + 12, 'thermal test fires →', 'lab');
    CK.txt(f.svg, L + 4, y(TW) - 5, `power test fires above ${TW} W`, 'lab');
    const pts = DOWN.map(r => mode === 'after' ? {r, T: r.T, P: r.P, why: r.why} : {r, T: r.T_prev, P: r.P_prev, why: r.why_prev});
    const groups = {};
    pts.forEach(p => (groups[p.T + '|' + Math.round(p.P / 2)] = groups[p.T + '|' + Math.round(p.P / 2)] || []).push(p));
    Object.values(groups).forEach(g => g.forEach((p, k) => (p.dx = (k - (g.length - 1) / 2) * 0.22)));
    pts.sort((a, b) => a.T + a.dx - (b.T + b.dx) || a.P - b.P);
    const nodes = pts.map(p => {
      const cx = x(p.T + p.dx), cy = y(p.P), c = CAUSE[p.why];
      const node = c.m === 'box' ? CK.el('rect', {x: cx - 5.5, y: cy - 5.5, width: 11, height: 11, rx: 1.5, fill: c.c, stroke: 'var(--surface)', 'stroke-width': 1.5}, f.svg)
        : c.m === 'ring' ? CK.el('circle', {cx, cy, r: 5.5, fill: 'var(--surface)', stroke: c.c, 'stroke-width': 2.2}, f.svg)
        : CK.el('circle', {cx, cy, r: 6, fill: c.c, stroke: 'var(--surface)', 'stroke-width': 1.5}, f.svg);
      CK.tip(f, node, tip(p.r));
      node.style.cursor = 'pointer';
      node.addEventListener('click', () => GOV.select(p.r));
      return node;
    });
    CK.keynav(f, nodes, {onEnter: (n_, k) => GOV.select(pts[k].r)});
    const cnt = tally(pts, 'why');
    CK.legend('attrib-leg', Object.keys(CAUSE).filter(k => cnt[k]).map(k => ({key: k, label: `${k} (${cnt[k]})`, mark: CAUSE[k].m, color: CAUSE[k].c})));
  }
  const frame = CK.frame('attrib', {height: W => (W < 600 ? 300 : 320), minW: 280, maxW: 640,
    label: 'Every down-step by the die temperature and board power on the chosen sample', draw});
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
  const R = [['Any mature design runs a DVFS loop that steps voltage and frequency to stay inside a power and thermal envelope.', 'confirmed',
    `Three operating points, ${OPS.map(o => o.mhz + ' MHz at ' + f2(o.volts) + ' V').join(', ')}. Voltage moved with frequency in all ${TR.length} observed transitions.`],
  ['The chip counts bus bits and execution-unit activity factors and computes its own power estimate on millisecond timescales.', 'not on this chip',
    'The loop reads the PMIC’s measured board power over I2C and the on-die PVT temperature. There is no activity counter anywhere in it, in the 353f20e source or in the older governor.'],
  ['Thermal sensors are part of the same loop, because leakage depends on temperature.', 'confirmed, and thermal has priority',
    `The temperature test comes before the power tests; ${nOf(byAfter, 'thermal')} of ${DOWN.length} down-steps were thermal only on the sample after the step (${nOf(byBefore, 'thermal')} on the sample before), and none was the power test alone.`],
  ['Cache data arrays sit behind leakage-suppression transistors; a lookup un-suppresses only the part it needs, at a small wake-up latency.', 'tied off in the open RTL',
    `The open RTL (Erbium, a later configuration of the same core, not the ET-SoC-1 chip) has per-minion sleep and isolation ports, tied off; no firmware line drives any power gating; and after 27 ms of idle no cache level shows a wake-up. Paired shifts: ${w.levels.map(l => l.level + ' ' + sgn(l.paired_delta_cycles)).join(', ')} cycles. The L2 shift comes from a slow no-idle baseline, and the DRAM one is a row closing.`],
  ['Leakage is typically 5–30% of a design’s power, about 20% common.', 'this card is worse',
    `${pct(D.leak_fraction.busy_randn_80c)} of a ${f0(D.busy_randn_80c)} W random-data matmul and ${pct(D.leak_fraction.idle_80c_law)} of an idle card at 80 °C (the idle law, <a href="#what-that-costs">§5</a>).`],
  ['Leakage costs power, not correctness.', 'consistent, weakly tested',
    `Every result checked in this work was correct: the matmul benchmark checks its outputs bit-exact against a host reference, and the relay checks every element. The power sessions’ launches were not compared with a reference (none raised the tensor unit’s error flag). The idle of about ${f1(ic.hours_idle)} hours cannot show errors either way: nothing computed, DRAM ECC is compiled off and the SRAM ECC interrupt sources are never enabled.`]];
  const t = document.getElementById('verdict');
  t.innerHTML = '<thead><tr><th>What David Kanter said (paraphrased)</th><th>Verdict on the ET-SoC-1</th><th>Evidence</th></tr></thead><tbody>' +
    R.map(v => `<tr><td>${v[0]}</td><td class="lvl">${v[1]}</td><td class="small">${v[2]}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
})();

/* ---------- §3: the three machines ---------- */
(function () {
  const C = D.cards, cf = C.config, sp = C.sptrace_aifoundry3;
  const R = [['Firmware release / PMIC', '1.3.1 / 1.5.0', '1.3.1 / 1.5.0', 'not readable'],     // read by hand (§8)
    ['TDP the <i>driver</i> reports', C.driver_tdp.aifoundry2 + ' W', C.driver_tdp.aifoundry3 + ' W', C.driver_tdp.aifoundry1 + ' W'],
    ['TDP the <i>service processor</i> reports', cf.aifoundry2.tdp_w + ' W', '<b>' + cf.aifoundry3.tdp_w + ' W</b>', '—'],
    ['Software temperature threshold', cf.aifoundry2.temp_threshold_c + ' °C', cf.aifoundry3.temp_threshold_c + ' °C', '—'],
    ['Power state the firmware reports', cf.aifoundry2.power_state_name, '<b>' + cf.aifoundry3.power_state_name + '</b>', '—'],
    ['Minion clock ever observed above 600 MHz', 'yes, 700 and 800', '<b>no</b>', '—'],
    ['Usable for these measurements', 'yes', 'yes', '<b>no</b>']];
  const t = document.getElementById('cardcfg');
  t.innerHTML = '<thead><tr><th>&nbsp;</th><th>aifoundry2</th><th>aifoundry3</th><th>aifoundry1 (2 cards)</th></tr></thead><tbody>' +
    R.map(r => `<tr><td class="small">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join('') + '</tbody>';
  CK.stackTable(t);
  const ev = D.sptrace_events;
  if (sp) document.getElementById('spcount').innerHTML = `That 8 KB window of the card's trace buffer holds <b>${sp.down_events} throttle-down events</b>` +
    (ev ? ` alternating with <b>${ev.idle} idle events</b>` + (ev.consecutive_idle_pairs ? ` (one idle event follows another ${ev.consecutive_idle_pairs === 1 ? 'once' : ev.consecutive_idle_pairs + ' times'})` : '') : '') +
    `, and <b>${sp.up_events} throttle-up events</b>, every one of them printing a TDP level of ${sp.tdp_levels.join(', ')}. ` +
    'One throttle-down per busy period is how the older governor logs, once per change of state (<a href="#method-and-what-is-not-established">§8</a>); ' +
    'the 353f20e source would log on every pass or, at the lowest operating point, not at all.';
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
})();

/* ---------- V2: one law, three checks ---------- */
(function () {
  const m = D.leak_model, ic = D.idle_check, on = D.overnight_idle, lk = D.cards.leakage;
  const leak = T => m.A_at_80 * Math.exp((T - 80) / m.T_L), law = T => m.P_fix + leak(T), slope = T => leak(T) / m.T_L;
  const SW = D.busy_randn_80c - law(80);                         // switching watts of the random-data matmul at 80 °C
  const K = D.leak_fraction.kanter_range, OFF = lk.mean_offset_W;
  const fitT = m.idle_curve.map(b => b.T);
  const st = {T: 80, busy: false, shift: false};
  const read = CK.readout('law-read');
  CK.range('law-T', {label: 'Die temperature', min: 45, max: 95, step: 1, value: st.T, fmt: v => f0(v) + ' °C', onInput: v => { st.T = v; frame.redraw(); }});
  const toggle = (id, key) => { const b = document.getElementById(id); b.addEventListener('click', () => { st[key] = !st[key]; b.setAttribute('aria-pressed', String(st[key])); frame.redraw(); }); };
  toggle('law-busy', 'busy'); toggle('law-shift', 'shift');
  document.getElementById('law-shift').textContent = `Shift the law by aifoundry3's offset (${sgn(OFF, 2)} W, mean of the four bins)`;
  legendHTML('law-leg', [{mark: 'shade', color: 'var(--ref)', op: 0.3, label: `fixed, ${f1(m.P_fix)} W`}, {mark: 'shade', color: 'var(--c1)', op: 0.3, label: 'leakage'},
    {mark: 'line', color: 'var(--ink)', label: 'the idle law'}, {mark: 'ring', color: 'var(--c1)', label: 'fit readings (size: samples)'},
    {mark: 'dot', color: 'var(--c3)', label: 'checks on the same card'}, {mark: 'box', color: 'var(--c7)', label: 'a different card (aifoundry3)'}]);
  const pts = [
    ...m.idle_curve.map(b => ({T: b.T, P: b.P, kind: 'fit', html: `<b>${f0(b.T)} °C, aifoundry2, a fit reading</b><br>measured ${f2(b.P)} W, law ${f2(law(b.T))} W (${sgn(b.P - law(b.T), 2)} W)<br>${num(b.n, 0)} samples`, n: b.n})),
    {T: on.die_c, P: on.board_w, kind: 'chk', lab: 'overnight rest, 21 Sep', html: `<b>Overnight rest, 21 September</b> (before the first cool-start launch)<br>measured ${f2(on.board_w)} ± ${f2(on.board_sd)} W at ${f0(on.die_c)} °C<br>law ${f2(on.law_w)} W (${sgn(on.board_w - on.law_w, 2)} W); ${on.samples} samples`},
    {T: ic.die_c, P: ic.board_w, kind: 'chk', lab: `22 Sep, ${f1(ic.hours_idle)} h idle`, html: `<b>22 September, after about ${f1(ic.hours_idle)} h idle</b><br>measured ${f2(ic.board_w)} ± ${f2(ic.board_sd)} W at ${f1(ic.die_c)} °C<br>law ${f2(ic.model_pred_w)} W (${sgn(ic.board_w - ic.model_pred_w, 2)} W); ${ic.samples} samples`},
    ...lk.idle_curve.map(b => ({T: b.T, P: b.W, kind: 'a3', html: `<b>${f0(b.T)} °C, aifoundry3</b><br>measured ${f2(b.W)} W, aifoundry2's law ${f2(b.card2_law_W)} W (${sgn(b.W - b.card2_law_W, 2)} W)<br>${num(b.n, 0)} samples`}))
  ].sort((a, b) => a.T - b.T);
  const nmax = Math.max(...m.idle_curve.map(b => b.n));
  function draw(f) {
    const W = f.W, H = f.H, L = 44, R = 12, T = 24, svg = f.svg;
    const SH = 58, mainB = H - SH - 40;                           // the leakage-share strip sits under the plot
    const x = CK.lin(45, 95, L, W - R), y = CK.lin(0, st.busy ? 80 : 50, mainB, T);
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
    if (st.shift) {
      CK.el('path', {d: CK.path(Ts.map(t => [t, law(t) + OFF]), x, y), fill: 'none', stroke: 'var(--c7)', 'stroke-width': 1.6, 'stroke-dasharray': '5 4'}, svg);
      CK.txt(svg, x(47), y(law(47) + OFF) - 8, `law ${sgn(OFF, 2)} W`, 'lab');
    }
    // cursor at the chosen temperature
    CK.el('line', {x1: x(st.T), x2: x(st.T), y1: T, y2: mainB, stroke: 'var(--ink-2)', 'stroke-width': 1}, svg);
    CK.el('circle', {cx: x(st.T), cy: y(law(st.T)), r: 4, fill: 'var(--ink)', stroke: 'var(--surface)', 'stroke-width': 2, 'pointer-events': 'none'}, svg);
    if (st.busy) CK.el('circle', {cx: x(st.T), cy: y(law(st.T) + SW), r: 4, fill: 'var(--c2)', stroke: 'var(--surface)', 'stroke-width': 2, 'pointer-events': 'none'}, svg);
    const nodes = pts.map(p => {
      const cx = x(p.T), cy = y(p.P);
      const node = p.kind === 'fit' ? CK.el('circle', {cx, cy, r: 4 + 5 * Math.sqrt(p.n / nmax), fill: 'var(--surface)', 'fill-opacity': 0.6, stroke: 'var(--c1)', 'stroke-width': 2}, svg)
        : p.kind === 'a3' ? CK.el('rect', {x: cx - 5, y: cy - 5, width: 10, height: 10, rx: 1.5, fill: 'var(--c7)', stroke: 'var(--surface)', 'stroke-width': 1.5}, svg)
        : CK.el('circle', {cx, cy, r: 5.5, fill: 'var(--c3)', stroke: 'var(--surface)', 'stroke-width': 2}, svg);
      CK.tip(f, node, st.shift && p.kind === 'a3' ? p.html + `<br>law ${sgn(OFF, 2)} W: ${sgn(p.P - law(p.T) - OFF, 2)} W` : p.html);
      return node;
    });
    for (const p of pts.filter(q => q.lab))                          // direct labels for the two same-card checks, below the curve
      CK.txt(svg, x(p.T) + 8, y(p.P) + 18, p.lab, 'lab-strong');
    CK.keynav(f, nodes);
    // the share strip: leakage as a share of idle and of a random-data matmul, against Kanter's typical range
    const s0 = mainB + 40, sx = CK.lin(0, 1, L, W - R), sy = s0 + SH / 2;
    const idleS = leak(st.T) / law(st.T), busyS = leak(st.T) / (law(st.T) + SW);
    const kr = range(100 * K[0], 100 * K[1], 0) + '%';
    CK.txt(svg, 2, s0 - 2, `leakage share at ${f0(st.T)} °C; shaded: Kanter's typical ${kr}`, 'lab');
    CK.el('rect', {x: sx(K[0]), y: sy - 9, width: sx(K[1]) - sx(K[0]), height: 18, fill: 'var(--c3)', opacity: 0.22}, svg);
    CK.txt(svg, (sx(K[0]) + sx(K[1])) / 2, sy + 24, kr, 'tick', 'middle');
    CK.el('line', {x1: L, x2: W - R, y1: sy, y2: sy, stroke: 'var(--axis)'}, svg);
    for (const v of [0, 0.5, 1]) CK.txt(svg, sx(v), sy + 24, pct(v), 'tick', v ? (v < 1 ? 'middle' : 'end') : 'start');
    const mark = (v, c, box, lab, below) => {
      if (box) CK.el('rect', {x: sx(v) - 5, y: sy - 5, width: 10, height: 10, rx: 1.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.5}, svg);
      else CK.el('circle', {cx: sx(v), cy: sy, r: 5.5, fill: c, stroke: 'var(--surface)', 'stroke-width': 1.5}, svg);
      CK.txt(svg, sx(v), below ? sy + 24 : sy - 11, lab, 'lab-strong', 'middle');
    };
    mark(busyS, 'var(--c2)', true, `matmul ${pct(busyS)}`);
    mark(idleS, 'var(--c1)', false, `idle ${pct(idleS)}`);
    const out = st.T < Math.min(...fitT) || st.T > Math.max(...fitT);
    read.set(`At ${f0(st.T)} °C: idle ${f1(law(st.T))} W = ${f1(m.P_fix)} W fixed + ${f1(leak(st.T))} W leakage → leakage is ` +
      `<b>${pct(idleS)} of idle</b> and <b>${pct(busyS)} of a random-data matmul</b>; slope ${f2(slope(st.T))} W/°C` +
      (out ? ` (extrapolated: the fit's idle readings span ${f0(Math.min(...fitT))}–${f0(Math.max(...fitT))} °C)` : '') +
      (st.busy ? `. The matmul's switching watts are held at their 80 °C value, ${f1(SW)} W.` : ''));
  }
  const frame = CK.frame('leaklaw', {height: W => (W < 600 ? 400 : 410), minW: 280, maxW: 640,
    label: 'Idle board power against die temperature: the fitted law, its fit readings and three out-of-sample checks', draw});
  // aifoundry3's bins as a table (the numbers without the chart)
  document.getElementById('leaktab').innerHTML = '<thead><tr><th class="num">aifoundry3 die °C</th><th class="num">measured idle W</th>' +
    '<th class="num">aifoundry2 law W</th><th class="num">difference</th><th class="num">samples</th></tr></thead><tbody>' +
    lk.idle_curve.map(r => `<tr><td class="num">${f0(r.T)}</td><td class="num">${f2(r.W)}</td><td class="num">${f2(r.card2_law_W)}</td>` +
      `<td class="num">${sgn(r.W - r.card2_law_W, 2)}</td><td class="num">${num(r.n, 0)}</td></tr>`).join('') +
    `<tr><td colspan="3"><b>mean of the four bins</b></td><td class="num"><b>${sgn(OFF, 2)}</b></td><td class="num"></td></tr>` +
    `<tr><td colspan="3">mean by sample</td><td class="num">${sgn(lk.mean_offset_W_by_sample, 2)}</td><td class="num">${num(lk.idle_curve.reduce((a, r) => a + r.n, 0), 0)}</td></tr></tbody>`;
  // the prose around the chart
  const groups = []; for (const t of fitT) { const g = groups[groups.length - 1]; if (g && t === g[1] + 1) g[1] = t; else groups.push([t, t]); }
  V.fitT = groups.map(g => range(g[0], g[1], 0)).join(' and ');
  const hw = T => f1(slope(T) / 2);
  V.checks = `the card's rest after a cool night, <b>${f2(on.board_w)} W at ${f0(on.die_c)} °C</b> on 21 September, against <b>${f2(on.law_w)} W</b>; ` +
    `and its idle on 22 September, after about ${f1(ic.hours_idle)} hours with no workload (apart from the ${V.probe} wake-up probe of §4, ` +
    `five minutes before) in a warmer room, <b>${f2(ic.board_w)} ± ${f2(ic.board_sd)} W at ${f1(ic.die_c)} °C</b>, in the gap between the fit's ` +
    `readings, against <b>${f2(ic.model_pred_w)} W</b>. Both agree within what the sensor's whole-degree readings allow ` +
    `(±${hw(on.die_c)} W at ${f0(on.die_c)} °C, ±${hw(ic.die_c)} W at ${f0(ic.die_c)} °C)`;
  V.unsensed = f1(ic.board_minus_rails);
  const a3T = lk.idle_curve.map(r => r.T), dif = lk.idle_curve.map(r => r.W - r.card2_law_W), lo = Math.min(...fitT);
  V.a3law = `The idle law, extrapolated ${lo - Math.max(...a3T)} to ${lo - Math.min(...a3T)} °C below its fit range onto aifoundry3, which idled ` +
    `at ${f0(Math.min(...a3T))} to ${f0(Math.max(...a3T))} °C, predicts that card's idle to within a watt: aifoundry3 reads ` +
    `${range(Math.min(...dif), Math.max(...dif), 1)} W above it, ${sgn(OFF, 2)} W on the mean of the four temperature bins ` +
    `(${sgn(lk.mean_offset_W_by_sample, 2)} W weighted by sample). The chart's second button shifts the law by that offset.`;
  V.idle65 = pct(D.leak_fraction.idle_80c_law);
  V.idle65of = `${f1(m.A_at_80)} of the idle law's ${f1(m.P_fix + m.A_at_80)} W`;
  const c64 = m.idle_curve.find(b => b.T === 64), c66 = m.idle_curve.find(b => b.T === 66);
  V.idleslope = f1((c66.P - c64.P) / 2); V.idleslopeT = '64–66';
})();

/* ---------- §6: the second card, in one paragraph ---------- */
(function () {
  const C = D.cards, rr = C.patterns.map(p => p.a3 / p.model), a3 = C.patterns.map(p => p.a3);
  document.getElementById('card2').innerHTML =
    `aifoundry3, held at 600 MHz, ran the same strict protocol at a ${f1(C.launch.aifoundry3.T)} °C launch. The flip-counting ` +
    `model fitted on aifoundry2 carries over with one per-card scale factor. Unchanged, it overestimates aifoundry3's switching ` +
    `power by ${pct(1 - C.scale)} (least squares; ${f0(100 * (1 - Math.max(...rr)))}–${pct(1 - Math.min(...rr))} pattern by pattern), ` +
    `${f2(C.rms_raw)} W rms. Multiplied by <b>${f2(C.scale)}</b>, it is within <b>${f2(C.rms_scaled)} W rms</b> over ` +
    `${f1(Math.min(...a3))}–${f0(Math.max(...a3))} W. The operating point cannot explain the gap: aifoundry3's ${C.voltage.a3_mv} mV ` +
    `against ${C.voltage.a2_mv} mV would predict ${pct(C.voltage.cv2f_ratio - 1)} <em>more</em> switching power. The chart and the ` +
    `leave-one-out calibration are in <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-second-card-and-what-transfers">§10 ` +
    `of the Horace experiment</a>. How the idle law transfers to this card is in <a href="#what-that-costs">What that costs</a>.`;
  V.a3launch = `${f2(C.launch.aifoundry3.T)} ± ${f2(C.launch.aifoundry3.T_sd)} °C`;
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
  });
  document.querySelectorAll('[data-v]').forEach(e => {
    const k = e.getAttribute('data-v');
    if (V[k] == null) throw new Error('dvfs-leakage: no value for data-v="' + k + '"');
    e.innerHTML = V[k];
  });
})();
