/* Influence functions on the ET-SoC-1: the page's numbers and charts, all computed from D (analysis.json,
   written by docs/reports/data/2026-09-25-influence-on-et/make_analysis.py) with the shared toolkit CK. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const num = CK.fmt.num;
  const SUP = {'-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹'};
  const sup = n => String(n).split('').map(c => SUP[c] || c).join('');
  const pow10 = e => '10' + sup(e);
  /* a×10ⁿ with two significant digits for large or small numbers, plain otherwise */
  function sci(v) {
    if (v == null || !isFinite(v)) return '—';
    if (v === 0) return '0';
    const a = Math.abs(v);
    if (a >= 1e-3 && a < 1e4) return num(v);
    let e = Math.floor(Math.log10(a)), m = +(v / Math.pow(10, e)).toPrecision(2);
    if (Math.abs(m) >= 10) { m /= 10; e += 1; }
    return (m === 1 ? '' : num(m) + '×') + pow10(e);
  }
  const intf = v => num(Math.round(v), 0);
  const r2 = v => (v >= 1e5 ? sci(v) : num(+(+v).toPrecision(2), 0));  /* rates: two significant digits */
  const pct = v => num(100 * v, 0) + '%';
  function range(a, b, f) {
    const s = f(a), t = f(b);
    return s === t ? s : s + '–' + t;
  }
  /* energy with a unit chosen by the larger end */
  const EU = [[1e6, 'MJ'], [1e3, 'kJ'], [1, 'J'], [1e-3, 'mJ'], [1e-6, 'µJ'], [1e-9, 'nJ']];
  function unitFor(v, units) { for (const u of units) if (Math.abs(v) >= u[0] * 0.9995) return u; return units[units.length - 1]; }
  function sig(v) { const a = Math.abs(v); return a >= 100 ? num(v, 0) : a >= 10 ? num(v, 1).replace(/\.0$/, '') : num(+v.toPrecision(2)); }
  function fmtJ(v) { if (v > 1e9) return sci(v) + ' J'; const u = unitFor(v, EU); return sig(v / u[0]) + ' ' + u[1]; }
  function fmtJr(a, b) {
    if (b > 1e9) return range(a, b, sci) + ' J';
    const u = unitFor(b, EU), s = sig(a / u[0]), t = sig(b / u[0]);
    return (s === t ? s : s + '–' + t) + ' ' + u[1];
  }
  const TU = [[1, 's'], [1e-3, 'ms'], [1e-6, 'µs'], [1e-9, 'ns']];
  function fmtT(v) { if (v >= 3600) return sig(v / 3600) + ' h'; const u = unitFor(v, TU); return sig(v / u[0]) + ' ' + u[1]; }
  const BU = [[1e18, 'EB'], [1e15, 'PB'], [1e12, 'TB'], [1e9, 'GB'], [1e6, 'MB'], [1e3, 'KB'], [1, 'B']];
  function fmtB(v) { const u = unitFor(v, BU); return sig(v / u[0]) + ' ' + u[1]; }
  const fmtBtick = v => { const u = unitFor(v, BU); return num(v / u[0], 0) + ' ' + u[1]; };
  function fmtRate(v) { return v >= 1e4 ? pow10(Math.round(Math.log10(v))) : num(v); }
  const perS = v => fmtRate(v) + (v === 1 ? ' query/s' : ' queries/s');
  const r2s = v => (isFinite(v) ? (v >= 1e5 ? sci(v) : num(Math.max(1, +(+v).toPrecision(2)), 0)) : '∞');
  function fmtCount(v) { return v >= 1e7 ? sci(v) : num(v, 0); }

  /* ---------------------------------------------------------------- numbers in the text: <span data-d="path"> */
  function get(path) { return path.split('.').reduce((o, k) => (o == null ? o : o[k]), D); }
  document.querySelectorAll('[data-d]').forEach(el => {
    const v = get(el.getAttribute('data-d'));
    if (v == null) return;
    const s = +(el.getAttribute('data-s') || 1), dp = el.getAttribute('data-dp'), f = el.getAttribute('data-f');
    const one = x => {
      x *= s;
      if (f === 'sci') return sci(x);
      if (f === 'int') return intf(x);
      if (f === 'r2') return r2(x);
      if (f === 'pct') return num(100 * x, 0);
      return num(x, dp == null ? null : +dp);
    };
    el.textContent = (Array.isArray(v) ? range(v[0], v[1], one) : one(v)) + (f === 'pct' ? '%' : '');
  });

  /* ---------------------------------------------------------------- the model (same as make_analysis.py) */
  const M = D.model, ET = M.et, HH = M.h100, CPU = M.cpu, BP = M.bytes_per;
  const PREC = {bit: '1 bit', int8: 'int8', fp16: 'fp16', fp32: 'fp32'};
  /* query tiles re-read from SRAM: a minion's 3 KB L1 scratchpad cannot hold a query, so each minion loads the
     Q query rows once for every tile of 16 codes it holds (as make_analysis.py's query_bytes) */
  function queryBytes(n, k, prec, Q, chips) {
    const perMinion = Math.ceil(n / (chips * 1024));
    return chips * 1024 * Math.ceil(perMinion / 16) * Q * k * BP[prec];
  }
  function etPass(n, k, prec, Q, where, rows16) {
    const B = n * k * BP[prec];
    const cap = where === 'sram' ? ET.sram_usable_B.v : ET.dram_B.v;
    const chips = Math.max(1, Math.ceil(B / cap));
    const Bq = queryBytes(n, k, prec, Q, chips);
    const Qc = rows16 && prec !== 'bit' ? Math.ceil(Q / 16) * 16 : Q;
    const pk = prec === 'bit' ? ET.bit : ET.peak[prec];
    const ops = (prec === 'bit' ? 1 : 2) * Qc * n * k;
    const sram = where === 'sram';
    const tl = sram ? (B + Bq) / chips / ET.sram_bw.v : Math.max(B / ET.dram_bw.v, Bq / ET.sram_bw.v) / chips;
    const eb = sram ? (B + Bq) * ET.sram_pj_B.v : B * ET.dram_pj_B.v + Bq * ET.sram_pj_B.v;
    const tc = ops / chips / pk.ops_per_s, t = Math.max(tl, tc);
    const ea = Math.max(eb, ops * pk.pj_op) * 1e-12;
    const bound = tl >= tc ? (sram || B / ET.dram_bw.v >= Bq / ET.sram_bw.v ? (sram ? 'SRAM bandwidth' : 'DRAM bandwidth') : 'SRAM bandwidth (query tiles)')
      : (prec === 'bit' ? 'the vector unit (no popcount)' : 'the tensor unit');
    return {B, Bq, chips, t, ea, bound};
  }
  function hPass(n, k, prec, Q, hi) {
    const B = n * k * BP[prec];
    const gpus = Math.max(1, Math.ceil(B / HH.hbm_B.v)), l2 = B <= HH.l2_pin_B.v;
    const bw = l2 ? HH.l2_bw.v : HH.hbm_bw.v, pjB = (l2 ? HH.l2_pj_B : HH.hbm_pj_B).v;
    const pk = prec === 'bit' ? HH.bit : HH.peak[prec], ops = (prec === 'bit' ? 1 : 2) * Q * n * k;
    const tm = B / gpus / bw, tc = ops / gpus / (pk.ops_per_s * M.h_eff), t = Math.max(tm, tc) + HH.launch_s.v;
    const e = gpus * (hi ? HH.idle_W.hi : HH.idle_W.lo) * t + (B * pjB + ops * pk.pj_op) * 1e-12;
    const bound = HH.launch_s.v > Math.max(tm, tc) ? 'kernel launch' : tm >= tc ? (l2 ? 'L2 bandwidth' : 'HBM bandwidth') : 'tensor cores';
    return {B, gpus, l2, t, e, bound};
  }
  function cpuPass(n, k, prec, Q, hi) {
    const B = n * k * BP[prec], ops = (prec === 'bit' ? 1 : 2) * Q * n * k;
    const t = Math.max(B / CPU.bw.v, ops / CPU.rate[prec]);
    return {t, e: t * (hi ? CPU.inc_W.hi : CPU.inc_W.lo)};
  }
  const HOST_MEM = 1e12;  // E: one host's memory; above it the host CPU is not shown as a scorer

  /* ---------------------------------------------------------------- 1. the pipeline dot plot */
  const FIT = {
    no: {label: 'not a fit: dense work or too big', color: 'var(--ref)', mark: 'dot'},
    killed: {label: 'ET-shaped, but killed', color: 'var(--c2)', mark: 'dot'},
    research: {label: 'survives as research (S1)', color: 'var(--c1)', mark: 'dot'},
    feature: {label: 'only as part of S1', color: 'var(--c1)', mark: 'ring'},
  };
  const KIND = D.kinds;
  CK.legend('pipe-leg', Object.keys(FIT).map(k => ({key: k, label: FIT[k].label, color: FIT[k].color, mark: FIT[k].mark})));
  const fmtH = h => (h >= 0.01 ? num(h) : sci(h));
  const Q8 = D.owner.amortized_query_h100h;
  const rows = D.pipeline;
  function pipeTip(p) {
    return '<b>' + p.label + '</b><br>' + fmtH(p.h) + ' H100-hours ' + p.per + ' (' + fmtJ(p.J) + ' at 700 W)'
      + '<br>' + FIT[p.fit].label + ': ' + p.why + '<br><span style="color:var(--muted)">' + p.k + ': ' + KIND[p.k.split('/')[0]] + '</span>';
  }
  CK.frame('pipe', {
    label: 'Influence-function steps by cost in H100-hours, log scale, coloured by fit to the ET-SoC-1',
    height: W => (W < 600 ? 44 + rows.length * 40 + 40 : 36 + rows.length * 27 + 44),
    draw(f) {
      const W = f.W, narrow = f.narrow, T = narrow ? 30 : 30, B = 40, rh = narrow ? 40 : 27;
      const LW = narrow ? 0 : Math.min(340, Math.round(W * 0.42));
      const x0 = narrow ? 14 : LW + 12, x1 = W - 16;
      const x = CK.log(1e-10, 1e4, x0, x1);
      const yEnd = T + rows.length * rh;
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      const xt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1, 100, 1e4];
      const labs = [];
      for (const t of xt) {
        CK.el('line', {x1: x(t), x2: x(t), y1: T - 6, y2: yEnd, class: 'grid-line'}, g);
        labs.push(CK.txt(g, x(t), yEnd + 16, t === 1 ? '1' : t === 100 ? '100' : pow10(Math.round(Math.log10(t))), 'tick', 'middle'));
      }
      labs.push(CK.txt(g, (x0 + x1) / 2, yEnd + 34, 'H100-hours, per the unit each step is paid in', 'lab', 'middle'));
      for (const [v, s] of [[Q8, 'one 8B query'], [Q8 * 1e-6, 'a millionth of it']]) {
        CK.el('line', {x1: x(v), x2: x(v), y1: T - 8, y2: yEnd, style: 'stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 3'}, g);
        labs.push(CK.txt(g, x(v) - 4, T - 12, s, 'lab', 'end'));
      }
      CK.inside(f, labs);
      const nodes = [];
      rows.forEach((p, i) => {
        const yr = T + i * rh;
        const yl = narrow ? yr + 13 : yr + rh / 2 + 4, yd = narrow ? yr + 27 : yr + rh / 2;
        CK.el('line', {x1: x0, x2: x1, y1: yd, y2: yd, class: 'grid-line', 'aria-hidden': 'true'}, f.svg);
        const bg = narrow ? CK.el('rect', {x: 1, y: yl - 12, height: 16, width: 0, 'aria-hidden': 'true', style: 'fill:var(--page)'}, f.svg) : null;
        const lab = CK.txt(f.svg, 4, yl, p.label, p.fit === 'no' ? 'lab' : 'lab-strong');
        lab.setAttribute('aria-hidden', 'true');
        if (bg) {  /* a plain background under the label, so the grid and the reference lines do not run through it */
          let w = 0; try { w = lab.getComputedTextLength(); } catch (_) { /* no layout */ }
          bg.setAttribute('width', (w > 0 ? w : 6.6 * p.label.length) + 8);
        }
        const c = FIT[p.fit];
        const dot = CK.el('circle', {cx: x(p.h), cy: yd, r: 6.5}, f.svg);
        if (c.mark === 'ring') { dot.style.fill = 'var(--surface)'; dot.style.stroke = c.color; dot.style.strokeWidth = '2.5'; }
        else { dot.style.fill = c.color; dot.style.stroke = 'var(--surface)'; dot.style.strokeWidth = '2'; }
        CK.tip(f, dot, pipeTip(p));
        nodes.push(dot);
      });
      CK.keynav(f, nodes);
    },
  });
  const ptb = $('pipe-table').tBodies[0];
  rows.forEach(p => {
    const tr = document.createElement('tr');
    [p.label, p.per, fmtH(p.h), FIT[p.fit].label + ': ' + p.why].forEach((t, j) => {
      const td = document.createElement('td'); td.textContent = t; if (j === 2) td.className = 'num'; tr.appendChild(td);
    });
    ptb.appendChild(tr);
  });
  CK.stackTable('pipe-table');
  CK.stackTable('k-table');

  /* ---------------------------------------------------------------- 2. the explorer */
  const st = {n: 16000, k: 4096, prec: 'int8', where: 'sram', Q: 1, lam: 1, rows16: false};
  let quiet = false;
  const N_STOPS = [1e3, 2e3, 5e3, 1e4, 16000, 2e4, 5e4, 1e5, 270000, 5e5, 1e6, 1e7, 1e8, 1e9, 1e10];
  const K_STOPS = [64, 256, 1024, 4096, 8192, 16384, 65536, 262144, 1e6, 3e6];
  const Q_STOPS = [1, 2, 4, 8, 16, 32, 64, 100, 128, 256, 512, 1024];
  const L_STOPS = [0.01, 0.1, 1, 10, 100, 1e3, 1e4, 1e5];
  const upd = () => { if (!quiet) recompute(); };
  const cN = CK.range('x-n', {label: 'Training examples in the index, N', stops: N_STOPS, value: st.n, fmt: fmtCount, onInput: v => { st.n = v; upd(); }});
  const cK = CK.range('x-k', {label: 'Sketch dimension, k', stops: K_STOPS, value: st.k, fmt: fmtCount, onInput: v => { st.k = v; upd(); }});
  const cP = CK.seg('x-prec', {label: 'Bits per coordinate', options: [['bit', '1 bit'], ['int8', 'int8'], ['fp16', 'fp16'], ['fp32', 'fp32']], value: st.prec, onChange: v => { st.prec = v; upd(); }});
  const cW = CK.seg('x-where', {label: 'The ET holds it in', options: [['sram', 'on-chip SRAM'], ['dram', 'card DRAM']], value: st.where, onChange: v => { st.where = v; upd(); }});
  const cQ = CK.range('x-q', {label: 'Queries per pass, Q', stops: Q_STOPS, value: st.Q, fmt: v => num(v, 0), onInput: v => { st.Q = v; upd(); }});
  const cL = CK.range('x-lam', {label: 'Queries arriving per second', stops: L_STOPS, value: st.lam, fmt: fmtRate, onInput: v => { st.lam = v; upd(); }});
  CK.seg('x-rows', {label: 'ET tensor ops with fewer than 16 rows', options: [['scale', 'cost in proportion (as in fp32)'], ['full', 'cost a full 16 rows']], value: 'scale', onChange: v => { st.rows16 = v === 'full'; upd(); }});
  /* presets: momentary buttons that set every control */
  (function () {
    const host = $('x-preset'); host.classList.add('controls');
    const lab = document.createElement('span'); lab.className = 'ck-seg-label'; lab.textContent = 'Try:'; host.appendChild(lab);
    D.presets.forEach(p => {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = p.label;
      b.addEventListener('click', () => {
        quiet = true;
        cN.set(p.n); cK.set(p.k); cP.set(p.prec); cW.set(p.where); cQ.set(p.Q); cL.set(p.lam);
        quiet = false; recompute();
      });
      host.appendChild(b);
    });
  })();
  const read = CK.readout('x-read');
  let S = null;  // the current computed state, read by the two charts

  function compute() {
    const {n, k, prec, where, Q, lam, rows16} = st;
    const e = etPass(n, k, prec, Q, where, rows16);
    const hl = hPass(n, k, prec, Q, false), hh = hPass(n, k, prec, Q, true);
    const cl = cpuPass(n, k, prec, Q, false), ch = cpuPass(n, k, prec, Q, true);
    const idle = [ET.idle_W.lo, ET.idle_W.hi];
    const etQ = (l, j) => e.chips * idle[j] / l + e.ea / Q;
    const h = [hl.e / Q, hh.e / Q], c = [cl.e / Q, ch.e / Q];
    const a = e.ea / Q;
    const be = [h[1] > a ? e.chips * idle[0] / (h[1] - a) : Infinity, h[0] > a ? e.chips * idle[1] / (h[0] - a) : Infinity];
    const bec = [c[1] > a ? e.chips * idle[0] / (c[1] - a) : Infinity, c[0] > a ? e.chips * idle[1] / (c[0] - a) : Infinity];
    return {e, hl, hh, cl, ch, etQ, h, c, be, bec, capE: Q / e.t, capH: Q / hl.t, capC: Q / cl.t, cpuOK: e.B <= HOST_MEM};
  }

  function recompute() {
    S = compute();
    const {e, hl, h, c, be, bec, capE, capH} = S, {n, k, prec, where, Q, lam} = st;
    $('x-size').textContent = fmtB(e.B);
    $('x-size-sub').textContent = fmtCount(n) + ' codes × ' + fmtCount(k) + ' × ' + PREC[prec];
    const full = lam > capE;
    $('x-et').textContent = full ? 'full' : fmtJr(S.etQ(lam, 0), S.etQ(lam, 1));
    $('x-et-sub').textContent = full
      ? 'serves at most ' + r2s(capE) + ' queries/s at Q = ' + Q + '; raise Q or add chips'
      : 'at ' + perS(lam) + ', idle included; ' + fmtCount(e.chips) + (where === 'sram' ? ' chip' : ' card') + (e.chips > 1 ? 's' : '');
    const hfull = lam > capH;
    $('x-h').textContent = fmtJr(h[0], h[1]);
    $('x-h-sub').textContent = 'the pass only: ' + fmtT(hl.t) + ' from ' + (hl.l2 ? 'L2' : 'HBM') + (hl.gpus > 1 ? ' on ' + intf(hl.gpus) + ' GPUs' : '')
      + (hfull ? '; full at this rate' : '');
    const inR = v => isFinite(v);
    $('x-be').textContent = !inR(be[0]) ? 'never' : !inR(be[1]) ? r2s(be[0]) + '/s' : range(be[0], be[1], r2s) + '/s';
    $('x-be-sub').textContent = !inR(be[0]) ? 'the H100 pass costs less than the ET’s own work'
      : (be[0] > capE ? 'but the ET is full at ' + r2s(capE) + '/s at this Q' : 'queries a second (host CPU: ' + (inR(bec[0]) ? range(bec[0], bec[1], r2s) + '/s' : 'never') + ')');
    // readout: what binds, and the scale of the step
    const fits = where === 'sram'
      ? (e.chips === 1 ? 'fits one chip’s scratchpads (72 MB usable)' : 'needs ' + fmtCount(e.chips) + ' chips’ scratchpads, ' + fmtWr(e.chips * ET.idle_W.lo, e.chips * ET.idle_W.hi) + ' at rest')
      : (e.chips === 1 ? 'fits one card’s 32 GB of DRAM' : 'needs ' + fmtCount(e.chips) + ' cards’ DRAM');
    const idleShare = S.etQ(lam, 0) > 0 ? (e.chips * ET.idle_W.lo / lam) / S.etQ(lam, 0) : 0;
    const qs = D.owner.query_energy_J;
    read.set('<b>ET-SoC-1</b>: the index ' + fits + '; a pass of Q = ' + Q + ' takes ' + fmtT(e.t) + ', bound by ' + e.bound + '. '
      + '<b>H100</b>: ' + (hl.l2 ? 'pinned in L2' : hl.gpus > 1 ? 'spread over ' + intf(hl.gpus) + ' GPUs’ HBM' : 'too big to pin in L2, read from HBM')
      + ' in ' + fmtT(hl.t) + ', bound by ' + hl.bound + '. '
      + (full ? '' : 'At ' + perS(lam) + ' the ET card’s idle is ' + (idleShare > 0.9999 ? 'over 99.99%' : pct(idleShare)) + ' of its energy per query. ')
      + (S.cpuOK ? 'The host CPU would spend ' + fmtJr(c[0], c[1]) + ' per query. ' : 'Too big for one host’s memory. ')
      + 'Scoring is ' + share(h[0] / qs[1], h[1] / qs[0]) + ' the H100 energy of the query’s own gradient and iHVP at 8B (' + fmtJr(qs[0], qs[1]) + ').');
    capFrame.redraw(); rateFrame.redraw(); s1qFrame.redraw();
  }
  function fmtW(w) { const u = unitFor(w, [[1e12, 'TW'], [1e9, 'GW'], [1e6, 'MW'], [1e3, 'kW'], [1, 'W']]); return sig(w / u[0]) + ' ' + u[1]; }
  function fmtWr(a, b) {
    const u = unitFor(b, [[1e12, 'TW'], [1e9, 'GW'], [1e6, 'MW'], [1e3, 'kW'], [1, 'W']]);
    return range(a / u[0], b / u[0], sig) + ' ' + u[1];
  }
  /* a share: a×10⁻ⁿ when tiny, a percentage below one, a multiple above */
  function share(a, b) {
    if (b < 1e-3) return range(a, b, sci) + ' of';
    if (b < 1) return range(100 * a, 100 * b, v => num(+v.toPrecision(2))) + '% of';
    return range(a, b, v => num(+v.toPrecision(2))) + ' times';
  }

  /* capacity strip: the index against each memory */
  const capFrame = CK.frame('cap', {
    label: 'The index size on a log scale against the ET chip SRAM, ET card DRAM, H100 pinned L2 and H100 HBM',
    height: () => 112,
    draw(f) {
      if (!S) return;
      const W = f.W, x = CK.log(1e4, 1e18, 14, W - 14);
      const yT = 16, y0 = 44, y1 = 56, yB = 88;
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
      CK.el('rect', {x: x(1e4), y: y0, width: x(1e18) - x(1e4), height: y1 - y0, rx: 3, style: 'fill:var(--grid)'}, g);
      for (let e10 = 4; e10 <= 18; e10 += 2) labs.push(CK.txt(g, x(Math.pow(10, e10)), 108, fmtBtick(Math.pow(10, e10)), 'tick', 'middle'));
      const refs = [
        [ET.sram_usable_B.v, 'ET scratchpads, 72 MB usable', 'var(--c1)', 'top', 'end', false],
        [ET.dram_B.v, 'ET card DRAM 32 GB', 'var(--c1)', 'top', 'start', true],
        [HH.l2_pin_B.v, 'H100 L2 37.5 MB', 'var(--c2)', 'bot', 'end', false],
        [HH.hbm_B.v, 'H100 HBM 80 GB', 'var(--c2)', 'bot', 'start', true],
      ];
      for (const [v, s, col, where, anchor, dash] of refs) {
        CK.el('line', {x1: x(v), x2: x(v), y1: where === 'top' ? yT + 6 : y0 - 4, y2: where === 'top' ? y1 + 4 : yB - 10,
          style: 'stroke:' + col + ';stroke-width:2' + (dash ? ';stroke-dasharray:4 3' : '')}, g);
        labs.push(CK.txt(g, x(v) + (anchor === 'end' ? -4 : 4), where === 'top' ? yT + 10 : yB - 8, s, 'lab', anchor));
      }
      CK.inside(f, labs);
      const B = S.e.B, xm = Math.max(x(1e4), Math.min(x(1e18), x(B)));
      const mk = CK.el('polygon', {points: [xm, y0 - 7, xm + 7, (y0 + y1) / 2, xm, y1 + 7, xm - 7, (y0 + y1) / 2].join(' '),
        style: 'fill:var(--ink);stroke:var(--surface);stroke-width:2'}, f.svg);
      CK.tip(f, mk, 'This index: ' + fmtB(B) + '<br>ET: ' + (st.where === 'sram' ? intf(S.e.chips) + ' chip' + (S.e.chips > 1 ? 's' : '') + '’ SRAM' : intf(S.e.chips) + ' card' + (S.e.chips > 1 ? 's' : '') + '’ DRAM')
        + '<br>H100: ' + (S.hl.l2 ? 'fits the pinned L2' : intf(S.hl.gpus) + ' GPU' + (S.hl.gpus > 1 ? 's' : '') + '’ HBM'));
    },
  });

  /* energy per query against the arrival rate */
  CK.legend('rate-leg', [
    {key: 'et', label: 'ET-SoC-1 card, idle charged', color: 'var(--c1)', mark: 'box'},
    {key: 'h', label: 'H100 in the server, pass only', color: 'var(--c2)', mark: 'box'},
    {key: 'c', label: 'host CPU, pass only', color: 'var(--c3)', mark: 'box'},
    {key: 'be', label: 'ET breaks even with the H100', color: 'var(--ref)', mark: 'box'},
  ]);
  const LX = [1e-2, 1e5];
  const rateFrame = CK.frame('rate', {
    label: 'Energy per query on a log scale against queries arriving per second, for the ET-SoC-1, an H100 and the host CPU',
    height: W => (W < 600 ? 300 : 340),
    draw(f) {
      if (!S) return;
      const {e, h, c} = S, L = 58, R = 14, T = 24, B = 42;
      const x = CK.log(LX[0], LX[1], L, f.W - R);
      const endE = Math.min(LX[1], S.capE), endH = Math.min(LX[1], S.capH), endC = Math.min(LX[1], S.capC);
      const vals = [h[0], h[1]];
      if (S.cpuOK) vals.push(S.c[0], S.c[1]);
      if (endE >= LX[0]) vals.push(S.etQ(LX[0], 1), S.etQ(endE, 0));
      let lo = Math.min(...vals), hi = Math.max(...vals);
      lo = Math.pow(10, Math.floor(Math.log10(lo * 0.6))); hi = Math.pow(10, Math.ceil(Math.log10(hi * 1.6)));
      const y = CK.log(lo, hi, f.H - B, T);
      const decades = Math.log10(hi / lo), every = Math.max(1, Math.ceil(decades / Math.max(3, Math.floor((f.H - T - B) / 34))));
      const yt = []; for (let d = Math.log10(lo); d <= Math.log10(hi) + 1e-9; d += every) yt.push(Math.pow(10, d));
      const xt = [1e-2, 1e-1, 1, 10, 100, 1e3, 1e4, 1e5].filter((t, i) => !f.narrow || i % 2 === 0);
      CK.axes(f, {x, y, L, R, T, B, xt, yt, xfmt: v => (v >= 1e4 ? pow10(Math.round(Math.log10(v))) : num(v)),
        yfmt: v => fmtJ(v).replace(' ', ' '), xl: 'queries arriving per second', yl: 'energy per query'});
      // break-even column
      const bx0 = Math.max(LX[0], Math.min(LX[1], S.be[0])), bx1 = Math.max(LX[0], Math.min(LX[1], isFinite(S.be[1]) ? S.be[1] : LX[1]));
      if (isFinite(S.be[0]) && S.be[0] <= LX[1] && bx1 > bx0) {
        const r = CK.el('rect', {x: x(bx0), y: T, width: Math.max(2, x(bx1) - x(bx0)), height: f.H - T - B, style: 'fill:var(--ref);fill-opacity:0.16'}, f.svg);
        CK.tip(f, r, 'The ET card breaks even with the H100 at ' + range(S.be[0], S.be[1], r2s) + ' queries a second'
          + (S.be[0] > S.capE ? ', beyond what it can serve at Q = ' + st.Q : ''));
      }
      const band = (x0, x1, fl, fh, col, key) => {
        if (x1 <= x0) return null;
        const pts = 48, xs = [];
        for (let i = 0; i <= pts; i++) xs.push(Math.pow(10, Math.log10(x0) + (Math.log10(x1) - Math.log10(x0)) * i / pts));
        const top = xs.map(v => [v, fh(v)]), bot = xs.map(v => [v, fl(v)]);
        const cy = v => Math.max(T, Math.min(f.H - B, y(v)));
        const d = top.map((p, i) => (i ? 'L' : 'M') + x(p[0]).toFixed(1) + ',' + cy(p[1]).toFixed(1)).join(' ')
          + ' ' + bot.reverse().map(p => 'L' + x(p[0]).toFixed(1) + ',' + cy(p[1]).toFixed(1)).join(' ') + ' Z';
        CK.el('path', {d, 'data-series': key, style: 'fill:' + col + ';fill-opacity:0.2;stroke:none'}, f.svg);
        for (const fn of [fl, fh]) CK.el('path', {d: xs.map((v, i) => (i ? 'L' : 'M') + x(v).toFixed(1) + ',' + cy(fn(v)).toFixed(1)).join(' '),
          class: 'ln', 'data-series': key, style: 'stroke:' + col + ';stroke-width:1.6'}, f.svg);
        return true;
      };
      band(LX[0], endH, () => h[0], () => h[1], 'var(--c2)', 'h');
      if (S.cpuOK) band(LX[0], endC, () => S.c[0], () => S.c[1], 'var(--c3)', 'c');
      if (endE >= LX[0]) band(LX[0], endE, v => S.etQ(v, 0), v => S.etQ(v, 1), 'var(--c1)', 'et');
      const labs = [];
      if (S.capE < LX[1] && S.capE >= LX[0]) labs.push(CK.txt(f.svg, x(S.capE) + 4, y(S.etQ(S.capE, 0)) + 4, 'ET full', 'lab'));
      // the chosen rate and a point per device
      const lam = st.lam, xl = x(lam);
      CK.el('line', {x1: xl, x2: xl, y1: T, y2: f.H - B, style: 'stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:3 3', 'aria-hidden': 'true'}, f.svg);
      const nodes = [];
      const pt = (v, col, html) => {
        const cy = Math.max(T, Math.min(f.H - B, y(v)));
        const d = CK.el('circle', {cx: xl, cy, r: 6}, f.svg);
        d.style.fill = col; d.style.stroke = 'var(--surface)'; d.style.strokeWidth = '2';
        CK.tip(f, d, html); nodes.push(d);
      };
      const eMid = Math.sqrt(S.etQ(lam, 0) * S.etQ(lam, 1));
      if (lam <= S.capE) pt(eMid, 'var(--c1)', '<b>ET-SoC-1</b> at ' + perS(lam) + ': ' + fmtJr(S.etQ(lam, 0), S.etQ(lam, 1)) + ' per query<br>idle '
        + fmtJr(e.chips * ET.idle_W.lo / lam, e.chips * ET.idle_W.hi / lam) + ', work ' + fmtJ(e.ea / st.Q) + '; pass ' + fmtT(e.t) + ', bound by ' + e.bound);
      if (lam <= S.capH) pt(Math.sqrt(h[0] * h[1]), 'var(--c2)', '<b>H100</b>, pass only: ' + fmtJr(h[0], h[1]) + ' per query<br>pass ' + fmtT(S.hl.t) + ', bound by ' + S.hl.bound);
      if (S.cpuOK && lam <= S.capC) pt(Math.sqrt(S.c[0] * S.c[1]), 'var(--c3)', '<b>Host CPU</b>, pass only: ' + fmtJr(S.c[0], S.c[1]) + ' per query<br>pass ' + fmtT(S.cl.t) + ' (estimate)');
      CK.inside(f, labs);
      CK.keynav(f, nodes);
    },
  });

  /* S1's lead against queries per pass (the "Few queries per pass" bullet): mJ per query, ET against H100, as Q
     grows, for the int8 and fp16 shards from D.s1.parity_*. Linked to the explorer's Q slider: a point sets it. */
  const s1 = D.s1;
  let s1qPrec = 'int8';
  CK.legend('s1q-leg', [
    {key: 'et', label: 'ET-SoC-1 card, idle charged', color: 'var(--c1)', mark: 'box'},
    {key: 'h', label: 'H100 in the server, pass only', color: 'var(--c2)', mark: 'box'},
  ]);
  CK.seg('s1q-prec', {label: 'Shard', options: [['int8', 'int8, 65.5 MB'], ['fp16', 'fp16, 32 MB']], value: s1qPrec,
    onChange: v => { s1qPrec = v; s1qFrame.redraw(); }});
  const s1qFrame = CK.frame('s1q', {
    label: 'Energy per query on a log scale against queries per pass, for the ET-SoC-1 and an H100, int8 and fp16 shards',
    height: W => (W < 600 ? 280 : 300),
    draw(f) {
      const P = s1[s1qPrec === 'int8' ? 'parity_int8' : 'parity_fp16'], rows = P.table, qCross = P.Q;
      const L = 60, R = 14, T = 20, B = 40;
      const qs = rows.map(r => r.Q);
      const x = CK.log(qs[0], qs[qs.length - 1], L, f.W - R);
      const vals = rows.reduce((a, r) => a.concat(r.et_mJ_per_q, r.h100_mJ_per_q), []);
      const lo = Math.pow(10, Math.floor(Math.log10(Math.min(...vals) * 0.85))), hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...vals) * 1.15)));
      const y = CK.log(lo, hi, f.H - B, T);
      const xt = qs.filter((q, i) => !f.narrow || i % 2 === 0 || q === qs[qs.length - 1]);
      CK.axes(f, {x, y, L, R, T, B, xt, yt: y.ticks(5), xfmt: v => num(v, 0), yfmt: v => fmtJ(v * 1e-3), xl: 'queries per pass, Q', yl: 'energy per query'});
      if (qCross && qCross[0] != null && qCross[1] != null) {
        const bx0 = Math.max(qs[0], qCross[0]), bx1 = Math.min(qs[qs.length - 1], qCross[1]);
        if (bx1 >= bx0) {
          const r = CK.el('rect', {x: x(bx0), y: T, width: Math.max(2, x(bx1) - x(bx0)), height: f.H - T - B, style: 'fill:var(--ref);fill-opacity:0.16'}, f.svg);
          CK.tip(f, r, 'The lead is gone by Q ≈ ' + intf(qCross[0]) + '–' + intf(qCross[1]) + ' in this page’s model');
        }
      }
      const band = (key, col, get) => {
        const top = rows.map(r => [r.Q, get(r)[1]]), bot = rows.map(r => [r.Q, get(r)[0]]);
        const d = top.map((p, i) => (i ? 'L' : 'M') + x(p[0]).toFixed(1) + ',' + y(p[1]).toFixed(1)).join(' ')
          + ' ' + bot.slice().reverse().map(p => 'L' + x(p[0]).toFixed(1) + ',' + y(p[1]).toFixed(1)).join(' ') + ' Z';
        CK.el('path', {d, 'data-series': key, style: 'fill:' + col + ';fill-opacity:0.2;stroke:none'}, f.svg);
      };
      band('et', 'var(--c1)', r => r.et_mJ_per_q);
      band('h', 'var(--c2)', r => r.h100_mJ_per_q);
      const nodes = [];
      const setQ = r => { const was = quiet; quiet = true; cQ.set(r.Q); quiet = was; recompute(); };
      const dot = (r, key, col, get) => {
        const v = get(r), cur = st.Q === r.Q, cx = x(r.Q), cy = y(Math.sqrt(v[0] * v[1]));
        const d = CK.el('circle', {cx, cy, r: cur ? 7 : 5}, f.svg);
        d.style.fill = col; d.style.stroke = cur ? 'var(--ink)' : 'var(--surface)'; d.style.strokeWidth = cur ? '2.5' : '1.5';
        CK.tip(f, d, '<b>' + (key === 'et' ? 'ET-SoC-1' : 'H100') + '</b>, Q = ' + r.Q + ': ' + fmtJr(v[0] * 1e-3, v[1] * 1e-3) + ' per query' + (cur ? ' (the explorer’s Q)' : ''));
        d.style.cursor = 'pointer';
        d.addEventListener('click', () => setQ(r));
        nodes.push(d);
      };
      rows.forEach(r => dot(r, 'et', 'var(--c1)', rr => rr.et_mJ_per_q));
      rows.forEach(r => dot(r, 'h', 'var(--c2)', rr => rr.h100_mJ_per_q));
      CK.keynav(f, nodes, {onEnter: (n, k) => setQ(rows[k % rows.length])});
      CK.readout('s1q-read').set(qCross && qCross[0] != null
        ? 'For the ' + (s1qPrec === 'int8' ? 'int8' : 'fp16') + ' shard, the ET’s lead over the H100 is gone by Q ≈ ' + intf(qCross[0]) + '–' + intf(qCross[1]) + ' queries per pass.'
        : '');
    },
  });
  recompute();

  /* ---------------------------------------------------------------- S3: scatter-add, measured (E48) */
  /* updates per second against nJ per update, log-log, for each method and where its buckets live (D.model.et.gs,
     from the energy manual's manual.json gs); the dashed line is the 10 G updates a second the page asked for */
  (function s3chart() {
    const G = ET.gs;
    if (!G || !$('s3')) return;
    const P = [
      ['upd_l1', 'gather + fadd + scatter, buckets in the hart’s L1', 0], ['upd_l2', 'gather + fadd + scatter, buckets in the L2', 0],
      ['upd_scp', 'gather + fadd + scatter, buckets in the own scratchpad', 0], ['upd_dram', 'gather + fadd + scatter, buckets in DRAM', 0],
      ['famoadd_l', 'packed atomic famoaddl.pi, a table per shire', 1], ['famoadd_g', 'packed atomic famoaddg.pi, one table for the chip', 1],
      ['amoadd_l', 'scalar atomic amoaddl.w, a table per shire', 1], ['amoadd_g', 'scalar atomic amoaddg.w, one table for the chip', 1],
    ].filter(p => G[p[0]]);
    /* the energy manual's families and marks (its section 6 chart of the same E48 rows), so a point looks the same on
       both pages: the vector unit on private buckets, an atomic add on a shared table (packed or scalar), the hot line */
    const GR = [['gather, fadd.ps and scatter, private buckets', 'var(--c4)', 'box'], ['an atomic add on a shared table: packed famoadd*.pi or scalar amoadd*.w', 'var(--c7)', 'dot'],
      ['global atomics spread over 32 lines (the hot line, before S3)', 'var(--c5)', 'ring']];
    CK.legend('s3-leg', GR.map((g, i) => ({key: 'g' + i, label: g[0], color: g[1], mark: g[2]})));
    const read = CK.readout('s3-read');
    const nj = v => (v < 0.1 ? num(v, 3) : v < 10 ? num(v, 2) : num(v, 0)) + ' nJ';
    const gps = v => (v >= 1e11 ? num(v / 1e9, 0) : v >= 1e10 ? num(v / 1e9, 1) : num(v / 1e9, 2)) + ' G/s';
    read.set('Only the points right of the dashed line reach 10 G updates a second: every one keeps its buckets inside a shire.');
    CK.frame('s3', {
      label: 'Scatter-add on the ET-SoC-1: updates per second against nanojoules per update, log-log, by method and where the buckets live',
      height: W => (W < 600 ? 300 : 320),
      draw(f) {
        const L = 56, R = 16, T = 24, B = 42, x = CK.log(1e8, 1e12, L, f.W - R), y = CK.log(0.01, 100, f.H - B, T);
        /* no x tick in the corner, where it would meet the lowest y tick */
        CK.axes(f, {x, y, L, R, T, B, xt: [1e9, 1e10, 1e11, 1e12], yt: [0.01, 0.1, 1, 10, 100], xfmt: v => (v >= 1e9 ? num(v / 1e9, 0) + ' G' : num(v / 1e6, 0) + ' M'),
          yfmt: v => num(v), xl: 'updates per second over the chip (log)', yl: 'nJ per update, above idle (log)'});
        const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
        CK.el('line', {x1: x(1e10), x2: x(1e10), y1: T, y2: f.H - B, style: 'stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:5 4'}, g);
        CK.inside(f, [CK.txt(g, x(1e10) + 5, T + 10, '10 G updates/s', 'lab', 'start')]);
        const nodes = [];
        const pt = (v, e, gr, html) => {
          const gg = CK.el('g', {}, f.svg), cx = x(v), cy = y(e), [, col, mk] = gr;
          CK.el('circle', {cx, cy, r: 9, class: 'ck-hit'}, gg);
          const c = mk === 'box' ? CK.el('rect', {x: cx - 4.5, y: cy - 4.5, width: 9, height: 9, rx: 1.5}, gg) : CK.el('circle', {cx, cy, r: mk === 'ring' ? 4.5 : 5}, gg);
          if (mk === 'ring') { c.style.fill = 'var(--surface)'; c.style.stroke = col; c.style.strokeWidth = '2'; }
          else { c.style.fill = col; c.style.stroke = 'var(--surface)'; c.style.strokeWidth = '1.5'; }
          CK.tip(f, gg, html); gg.addEventListener('focus', () => read.set(html)); nodes.push(gg);
        };
        P.forEach(([k, lab, gi]) => { const d = G[k]; pt(d.ops_per_s, d.nj, GR[gi], '<b>' + lab + '</b>: ' + gps(d.ops_per_s) + ' at ' + nj(d.nj) + ' per update [' + nj(d.lo) + '–' + nj(d.hi) + ']'); });
        const A = ET.atomics_spread;
        if (A) pt(A.ops_per_s, A.nj, GR[2], '<b>Global atomics spread over 32 lines</b> (the hot-line report, before S3): ' + gps(A.ops_per_s) + ' at ' + nj(A.nj));
        CK.keynav(f, nodes);
      },
    });
  })();

  /* ---------------------------------------------------------------- 5. the first experiment's verdict */
  /* Board energy (log) against time for one query over the 65.5 MB int8 shard: the rule's pass box (D.experiment) and
     kill region (its absolute line, and a third of the modelled H100's pass), with the model's predictions (s1.hbm_case,
     s1.hbm_case_rows16), the H100's own pass, and the one measured pass (the anchor layer, model.et.anchor). Every bar
     spans the idle range of its device, charged over the pass. */
  (function verdictChart() {
    const X = D.experiment, A = ET.anchor, c1 = s1.hbm_case, c16 = s1.hbm_case_rows16;
    if (!X || !$('verdict') || !c1 || !c16) return;
    const gpuKill = [c1.h100_mJ[0] / X.kill_gpu_within, c1.h100_mJ[1] / X.kill_gpu_within];
    const killAt = Math.min(X.kill_mJ, gpuKill[0]);  // the lowest energy at which the rule could kill S1, as modelled
    const where = (us, mJ) => (mJ[0] >= X.kill_mJ ? 'killed' : mJ[0] >= killAt ? 'at the kill line' : us <= X.pass_us && mJ[1] <= X.pass_mJ ? 'inside the pass box'
      : us <= X.pass_us && mJ[0] <= X.pass_mJ ? 'across the pass line' : 'out of the pass box, short of the kill line');
    const mj = v => num(v, v < 1 ? 2 : 1), mjr = v => range(v[0], v[1], mj) + ' mJ';
    const PTS = [
      {key: 's1', lab: 'S1 as modelled', col: 'var(--c1)', fill: true, us: c1.et_us, mJ: c1.et_mJ,
        html: () => '<b>S1 as this page models it</b>: one query over the ' + num(c1.MB, 1) + ' MB int8 shard, ' + num(c1.et_us, 1) + ' µs and ' + mjr(c1.et_mJ)
          + ' of board energy (the lower end at aifoundry3’s idle, the upper at aifoundry2’s), bound by ' + (c1.et_bound === 'memory' ? 'SRAM bandwidth' : 'the tensor unit') + ': ' + where(c1.et_us, c1.et_mJ)
          + ' before the fused top-k; the dashed extension is the upper end with a top-k at the rule’s ' + pct(X.topk_max) + ' limit, ' + mj(c1.et_mJ[1] * (1 + X.topk_max)) + ' mJ'},
      {key: 'r16', lab: 'if every op costs 16 rows', short: '16-row ops', col: 'var(--c1)', fill: false, us: c16.et_us, mJ: c16.et_mJ,
        html: () => '<b>The same, if every tensor op costs a full 16 rows</b> (the third weakest assumption): ' + num(c16.et_us, 1) + ' µs and ' + mjr(c16.et_mJ)
          + ', bound by ' + (c16.et_bound === 'memory' ? 'SRAM bandwidth' : 'the tensor unit') + ': ' + where(c16.et_us, c16.et_mJ)},
      {key: 'h', lab: 'H100 from HBM', col: 'var(--c2)', fill: true, us: c1.h100_us, mJ: c1.h100_mJ,
        html: () => '<b>An H100 reading the same shard from HBM</b> (this page’s estimate): ' + num(c1.h100_us, 1) + ' µs and ' + mjr(c1.h100_mJ)
          + '; a third of it, ' + mjr(gpuKill) + ', is where “the GPU comes within ' + X.kill_gpu_within + '×” would kill S1'},
      {key: 'm', lab: 'measured: a 16.8 MB layer', short: 'measured layer', col: 'var(--ink)', fill: true, sq: true, us: A.t_us, mJ: [A.board_j * 1e3, A.board_j * 1e3],
        html: () => '<b>The one pass measured</b>: a 1024×4096 fp32 layer (' + num(A.bytes / 1e6, 1) + ' MB) read from the scratchpads in ' + num(A.t_us, 1) + ' µs for '
          + mj(A.board_j * 1e3) + ' mJ of board energy (aifoundry3, one run); the model reproduces its energy above idle to within ' + num(100 * A.model_over_measured, 0) + '%'},
    ];
    CK.legend('verdict-leg', [
      {key: 'et', label: 'ET-SoC-1, this page’s model', color: 'var(--c1)', mark: 'dot'},
      {key: 'h', label: 'H100, this page’s estimate', color: 'var(--c2)', mark: 'dot'},
      {key: 'm', label: 'measured on a card', color: 'var(--ink)', mark: 'box'},
      {key: 'pass', label: 'the rule’s pass box', color: 'color-mix(in srgb, var(--ok) 30%, var(--surface))', mark: 'box'},
      {key: 'kill', label: 'kill', color: 'color-mix(in srgb, var(--bad) 26%, var(--surface))', mark: 'box'},
    ]);
    const read = CK.readout('verdict-read');
    const in1 = where(c1.et_us, c1.et_mJ), in16 = where(c16.et_us, c16.et_mJ);
    const spareE = [1 - c1.et_mJ[1] / X.pass_mJ, 1 - c1.et_mJ[0] / X.pass_mJ], spareT = 1 - c1.et_us / X.pass_us;
    /* the model has no selection cost: the fused top-k, which the rule lets add up to X.topk_max, comes on top */
    const tk = 1 + X.topk_max, tkHi = c1.et_mJ[1] * tk, tkRoom = X.pass_mJ / c1.et_mJ[1] - 1;
    const tkNote = in1 === 'inside the pass box' ? (tkHi > X.pass_mJ
      ? '; the fused top-k is not in the model, and at the rule’s ' + pct(X.topk_max) + ' limit it would take the upper end to ' + mj(tkHi) + ' mJ (and ' + num(c1.et_us * tk, 0) + ' µs), over the '
        + num(X.pass_mJ, 1) + ' mJ line: the upper end stays inside only if the top-k adds at most ' + pct(tkRoom)
      : '; the fused top-k is not in the model, and even at the rule’s ' + pct(X.topk_max) + ' limit the upper end stays inside, at ' + mj(tkHi) + ' mJ') : '';
    const summary = 'As modelled, before the fused top-k, one query takes ' + num(c1.et_us, 0) + ' µs and ' + mjr(c1.et_mJ) + ': ' + in1
      + (in1 === 'inside the pass box' ? ', with ' + range(100 * spareE[0], 100 * spareE[1], v => num(v, 0)) + '% to spare on energy and ' + num(100 * spareT, 0) + '% on time' : '') + tkNote
      + '. If every tensor op costs a full 16 rows it takes ' + mjr(c16.et_mJ) + ': ' + in16 + '. The H100’s own pass, ' + mjr(c1.h100_mJ) + ', puts “within '
      + X.kill_gpu_within + '×” at ' + mjr(gpuKill) + ', next to the rule’s ' + num(X.kill_mJ, 0) + ' mJ.';
    read.set(summary);
    $('verdict-lead').textContent = 'Where the verdict would fall: this page’s model puts one query over the ' + num(c1.MB, 1) + ' MB shard '
      + in1 + (in1 === 'inside the pass box' ? ', before the fused top-k it leaves out' + (tkHi > X.pass_mJ ? ' (a top-k at the rule’s ' + pct(X.topk_max) + ' limit would take the upper end over the pass line)' : '') : '') + (in16 !== in1 ? '; its third weakest assumption alone (tensor ops that cost a full 16 rows) moves it ' + (in16 === 'killed' || in16 === 'at the kill line' ? 'to the kill line' : 'out of the box, though not to the kill line') : '') + '.';
    $('verdict-cap').innerHTML = 'Each bar spans its device’s idle charged over the pass: the ET card at ' + range(ET.idle_W.lo, ET.idle_W.hi, v => num(v, 1)) + ' W <span class="ev m">M</span>, the H100 at '
      + range(HH.idle_W.lo, HH.idle_W.hi, v => num(v, 0)) + ' W <span class="ev e">E</span>. The rule is this section’s, set before any run <span class="ev e">E</span>: pass at ' + num(X.pass_us, 0) + ' µs and ' + num(X.pass_mJ, 1)
      + ' mJ or less with the fused top-k adding at most ' + pct(X.topk_max) + '; kill at ' + num(X.kill_mJ, 0) + ' mJ or more, or within ' + X.kill_gpu_within + '× of the GPU (the hatched band under the kill line, from a third of the modelled H100’s pass, ' + mjr(gpuKill) + ')'
      + '. The model has no top-k: the faint dashed extension above S1’s bar is its upper end with a top-k at that ' + pct(X.topk_max) + ' limit. Only the square was measured, and on a smaller layer, not on the shard.';
    CK.frame('verdict', {
      label: 'Board energy per query against time per pass: the first experiment’s pass box and kill region, with the model’s predictions for S1, an H100, and the one measured pass',
      height: W => (W < 600 ? 330 : 360),
      draw(f) {
        const L = 52, R = 14, T = 24, B = 42, xMax = 50;
        const x = CK.lin(0, xMax, L, f.W - R), y = CK.log(0.1, 20, f.H - B, T);
        CK.axes(f, {x, y, L, R, T, B, xt: [0, 10, 20, 30, 40, 50], yt: [0.1, 0.3, 1, 3, 10], xfmt: v => num(v, 0), yfmt: v => num(v),
          xl: 'time for one query, µs', yl: 'board energy for one query, mJ (log)'});
        const g = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [], nodes = [];
        /* the regions: the pass box, the kill region from the rule's line, and the band a third of the modelled H100 adds */
        const box = (x0, x1, y0, y1, fill) => CK.el('rect', {x: x(x0), y: y(y1), width: x(x1) - x(x0), height: y(y0) - y(y1), style: 'fill:' + fill}, g);
        box(0, X.pass_us, 0.1, X.pass_mJ, 'color-mix(in srgb, var(--ok) 16%, transparent)');
        box(0, xMax, X.kill_mJ, 20, 'color-mix(in srgb, var(--bad) 14%, transparent)');
        if (killAt < X.kill_mJ) {  /* the band "within 3× of the GPU" adds: hatched, with its own label */
          const pat = CK.el('pattern', {id: 'verdict-hatch', width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)'}, CK.el('defs', {}, g));
          const hl = CK.el('line', {x1: 0, y1: 0, x2: 0, y2: 6, 'stroke-width': 2.5}, pat); hl.style.stroke = 'color-mix(in srgb, var(--bad) 55%, transparent)';
          box(0, xMax, killAt, X.kill_mJ, 'url(#verdict-hatch)');
          const edge = CK.el('line', {x1: x(0), x2: x(xMax), y1: y(killAt), y2: y(killAt), 'stroke-width': 1, 'stroke-dasharray': '2 3'}, g); edge.style.stroke = 'var(--bad)';
          /* its label just above the kill line, at the right, where the kill region is empty */
          labs.push(CK.txt(g, x(xMax) - 4, y(X.kill_mJ) - 6, (f.narrow ? 'within ' : 'kill: within ') + X.kill_gpu_within + '× of the H100, ' + mjr(gpuKill) + ' (hatched)', 'lab', 'end'));
        }
        const line = (x1_, y1_, x2_, y2_, col, dash) => CK.el('line', {x1: x1_, y1: y1_, x2: x2_, y2: y2_, style: 'stroke:' + col + ';stroke-width:1.4' + (dash ? ';stroke-dasharray:5 4' : '')}, g);
        line(x(0), y(X.pass_mJ), x(X.pass_us), y(X.pass_mJ), 'var(--ok)', true);
        line(x(X.pass_us), y(0.1), x(X.pass_us), y(X.pass_mJ), 'var(--ok)', true);
        line(x(0), y(X.kill_mJ), x(xMax), y(X.kill_mJ), 'var(--bad)', true);
        labs.push(CK.txt(g, x(1), y(0.1) - 8, 'pass: ≤ ' + num(X.pass_us, 0) + ' µs and ≤ ' + num(X.pass_mJ, 1) + ' mJ', 'lab-strong'));
        labs.push(CK.txt(g, x(1), y(20) + 16, 'kill: ≥ ' + num(X.kill_mJ, 0) + ' mJ, or within ' + X.kill_gpu_within + '× of the GPU', 'lab-strong'));
        labs.push(CK.txt(g, x(1), (y(X.pass_mJ) + y(killAt)) / 2 + 4, 'neither pass nor kill', 'tick', 'start'));
        /* the points: a bar over the idle range with caps, and a mark at each end (the square: one measured value) */
        PTS.forEach(p => {
          const gg = CK.el('g', {}, f.svg), cx = x(p.us), ya = y(p.mJ[0]), yb = y(p.mJ[1]);
          CK.el('rect', {x: cx - 11, y: yb - 11, width: 22, height: ya - yb + 22, class: 'ck-hit'}, gg);
          if (p.sq) {
            const s = CK.el('rect', {x: cx - 5.5, y: ya - 5.5, width: 11, height: 11, rx: 1.5}, gg); s.style.fill = p.col; s.style.stroke = 'var(--surface)'; s.style.strokeWidth = '1.5';
          } else {
            if (p.key === 's1' && X.topk_max) {  /* S1's upper end with a top-k at the rule's limit: a faint dashed whisker and cap */
              const yt = y(p.mJ[1] * (1 + X.topk_max)), wk = CK.el('line', {x1: cx, x2: cx, y1: yb, y2: yt, 'stroke-width': 1.5, 'stroke-dasharray': '3 3', opacity: 0.6}, gg); wk.style.stroke = p.col;
              const cap = CK.el('line', {x1: cx - 5, x2: cx + 5, y1: yt, y2: yt, 'stroke-width': 1.5, opacity: 0.6}, gg); cap.style.stroke = p.col;
            }
            const bar = CK.el('line', {x1: cx, x2: cx, y1: ya, y2: yb}, gg); bar.style.stroke = p.col; bar.style.strokeWidth = '3';
            if (!p.fill) bar.style.strokeDasharray = '3 2';
            [ya, yb].forEach(yy => {
              const m = CK.el('circle', {cx, cy: yy, r: 5}, gg);
              m.style.fill = p.fill ? p.col : 'var(--surface)'; m.style.stroke = p.fill ? 'var(--surface)' : p.col; m.style.strokeWidth = p.fill ? '1.5' : '2';
            });
          }
          const right = p.key !== 'h';  /* the H100's label goes left, clear of S1's bars */
          const lt = CK.txt(f.svg, cx + (right ? 12 : -12), (ya + yb) / 2 + 4, f.narrow && p.short ? p.short : p.lab, 'lab', right ? 'start' : 'end');
          lt.setAttribute('aria-hidden', 'true'); labs.push(lt);
          CK.tip(f, gg, p.html);
          gg.addEventListener('focus', () => read.set(p.html()));
          gg.addEventListener('blur', () => read.set(summary));
          nodes.push(gg);
        });
        CK.inside(f, labs);
        CK.keynav(f, nodes);
      },
    });
  })();

  /* ---------------------------------------------------------------- 3. S2: the atlas scan */
  const s2 = D.s2;
  const s2rows = [{label: 'A100, measured (the author’s atlas)', s: s2.a100_s, J: s2.a100_J, gpu: true}]
    .concat(s2.et.map(r => ({label: 'ET-SoC-1, ' + r.prec + ' at ' + pct(r.eff) + ' of its measured peak', s: r.s, J: [r.J, r.J], eff: r.eff, prec: r.prec})));
  let s2mode = 's';
  CK.seg('s2-ctl', {label: 'The atlas scan (100 queries × 10 logits × 60,000 digits), in', options: [['s', 'seconds'], ['J', 'joules']], value: 's',
    onChange: v => { s2mode = v; s2f.redraw(); }});
  const s2f = CK.frame('s2', {
    label: 'The atlas scan on the A100 as measured, against the ET-SoC-1 at several fractions of its peak',
    height: W => (W < 600 ? 40 + s2rows.length * 42 + 36 : 30 + s2rows.length * 30 + 40),
    draw(f) {
      const narrow = f.narrow, rh = narrow ? 42 : 30, T = narrow ? 14 : 10, LW = narrow ? 0 : Math.min(300, Math.round(f.W * 0.38));
      const x0 = narrow ? 4 : LW + 10, x1 = f.W - (narrow ? 70 : 90);
      const val = r => (s2mode === 's' ? r.s : r.J[1]);
      const max = Math.max(...s2rows.map(val)) * 1.05;
      const x = CK.lin(0, max, x0, x1), yEnd = T + s2rows.length * rh;
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg), labs = [];
      for (const t of x.ticks(narrow ? 4 : 6)) {
        CK.el('line', {x1: x(t), x2: x(t), y1: T - 4, y2: yEnd, class: 'grid-line'}, g);
        labs.push(CK.txt(g, x(t), yEnd + 16, num(t), 'tick', 'middle'));
      }
      labs.push(CK.txt(g, (x0 + x1) / 2, yEnd + 32, s2mode === 's' ? 'seconds' : 'joules of board energy', 'lab', 'middle'));
      const ref = s2mode === 's' ? s2.a100_s : null;
      if (ref) CK.el('line', {x1: x(ref), x2: x(ref), y1: T - 4, y2: yEnd, style: 'stroke:var(--c2);stroke-width:1.2;stroke-dasharray:4 3'}, g);
      if (!ref) CK.el('rect', {x: x(s2.a100_J[0]), y: T - 4, width: x(s2.a100_J[1]) - x(s2.a100_J[0]), height: yEnd - T + 4, style: 'fill:var(--c2);fill-opacity:0.12'}, g);
      CK.inside(f, labs);
      const nodes = [];
      s2rows.forEach((r, i) => {
        const yr = T + i * rh, yb = narrow ? yr + 18 : yr + 6, bh = 14;
        CK.txt(f.svg, narrow ? 4 : 4, narrow ? yr + 12 : yr + 17, r.label, r.gpu ? 'lab-strong' : 'lab').setAttribute('aria-hidden', 'true');
        const v = val(r);
        const bar = CK.el('rect', {x: x0, y: yb, width: Math.max(2, x(v) - x0), height: bh, rx: 3}, f.svg);
        bar.style.fill = r.gpu ? 'var(--c2)' : 'var(--c1)';
        let txt;
        if (s2mode === 's') txt = fmtT(r.s);
        else txt = r.gpu ? fmtJr(r.J[0], r.J[1]) : fmtJ(r.J[0]);
        CK.txt(f.svg, x(v) + 6, yb + 11, txt, 'lab', 'start').setAttribute('aria-hidden', 'true');
        const html = r.gpu
          ? '<b>A100, measured</b>: the scan took ' + fmtT(s2.a100_s) + ' (' + num(s2.a100_tflops_nominal) + ' TFLOP/s nominal); at 250–400 W that is ' + fmtJr(s2.a100_J[0], s2.a100_J[1]) + ' (power estimated)'
          : '<b>' + r.label + '</b>: ' + fmtT(r.s) + ' and ' + fmtJ(r.J[0]) + ' at its board power on random operands (aifoundry2, 80 °C; estimate: the fraction of peak a persistent kernel sustains is unmeasured)';
        CK.tip(f, bar, html); nodes.push(bar);
      });
      CK.keynav(f, nodes);
    },
  });
})();
