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
      ? (e.chips === 1 ? 'fits one chip’s 72 MB of SRAM' : 'needs ' + fmtCount(e.chips) + ' chips’ SRAM, ' + fmtWr(e.chips * ET.idle_W.lo, e.chips * ET.idle_W.hi) + ' at rest')
      : (e.chips === 1 ? 'fits one card’s 32 GB of DRAM' : 'needs ' + fmtCount(e.chips) + ' cards’ DRAM');
    const idleShare = S.etQ(lam, 0) > 0 ? (e.chips * ET.idle_W.lo / lam) / S.etQ(lam, 0) : 0;
    const qs = D.owner.query_energy_J;
    read.set('<b>ET-SoC-1</b>: the index ' + fits + '; a pass of Q = ' + Q + ' takes ' + fmtT(e.t) + ', bound by ' + e.bound + '. '
      + '<b>H100</b>: ' + (hl.l2 ? 'pinned in L2' : hl.gpus > 1 ? 'spread over ' + intf(hl.gpus) + ' GPUs’ HBM' : 'too big to pin in L2, read from HBM')
      + ' in ' + fmtT(hl.t) + ', bound by ' + hl.bound + '. '
      + (full ? '' : 'At ' + perS(lam) + ' the ET card’s idle is ' + (idleShare > 0.9999 ? 'over 99.99%' : pct(idleShare)) + ' of its energy per query. ')
      + (S.cpuOK ? 'The host CPU would spend ' + fmtJr(c[0], c[1]) + ' per query. ' : 'Too big for one host’s memory. ')
      + 'Scoring is ' + share(h[0] / qs[1], h[1] / qs[0]) + ' the H100 energy of the query’s own gradient and iHVP at 8B (' + fmtJr(qs[0], qs[1]) + ').');
    capFrame.redraw(); rateFrame.redraw();
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
        [ET.sram_usable_B.v, 'ET chip SRAM 72 MB', 'var(--c1)', 'top', 'end', false],
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
  recompute();

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
          : '<b>' + r.label + '</b>: ' + fmtT(r.s) + ' and ' + fmtJ(r.J[0]) + ' at the matmul benchmark’s board power (estimate: the fraction of peak a persistent kernel sustains is unmeasured)';
        CK.tip(f, bar, html); nodes.push(bar);
      });
      CK.keynav(f, nodes);
    },
  });
})();
