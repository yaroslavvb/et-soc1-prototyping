/* sparse-parity.script.js: the page "Sparse parity on the ET-SoC-1".
   D is docs/reports/data/2026-09-29-sparse-parity/page.json (make_page_data.py beside it); CK is the chart toolkit. */
(function () {
  'use strict';
  const V = D.v;
  document.querySelectorAll('[data-v]').forEach(e => {
    const k = e.getAttribute('data-v');
    if (!(k in V)) throw new Error('page.json has no v.' + k);
    e.innerHTML = V[k];
  });

  const num = CK.fmt.num;
  const NB = ' ';
  const g3 = x => (x >= 1000 ? num(Math.round(x), 0) : Number(x).toPrecision(3));
  function fmtS(t) {
    if (t == null || !isFinite(t)) return '—';
    if (t < 1e-3) return g3(t * 1e6) + NB + 'µs';
    if (t < 0.1) return g3(t * 1e3) + NB + 'ms';
    if (t < 120) return g3(t) + NB + 's';
    return g3(t / 60) + NB + 'min';
  }
  const tTick = v => (v < 1e-3 ? num(v * 1e6) + ' µs' : v < 1 ? num(v * 1e3) + ' ms' : num(v) + ' s');
  const SUP = {'-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
    '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'};
  const expo = v => { const e = Math.floor(Math.log10(Math.abs(v))); return [v / Math.pow(10, e), e]; };
  const sciU = (v, d) => { const [m, e] = expo(v); return num(m, d == null ? 1 : d) + '×10' + String(e).split('').map(c => SUP[c]).join(''); };
  const sciH = (v, d) => { const [m, e] = expo(v); return num(m, d == null ? 1 : d) + '×10<sup>' + String(e).replace('-', '−') + '</sup>'; };
  const x2 = v => (v < 10 ? Number(v).toPrecision(2) : num(Math.round(v), 0));
  const rngX = (a, b) => { const lo = x2(Math.min(a, b)), hi = x2(Math.max(a, b)); return (lo === hi ? lo : lo + '–' + hi) + '×'; };
  const INST = {};
  D.inst.forEach(i => { INST[i.id] = i; });
  const LAB = id => INST[id].label;
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const mix = (c, p) => `color-mix(in srgb, ${c} ${p}%, var(--surface))`;

  /* ---- tables ---- */
  function table(id, head, rows, o) {
    o = o || {};
    const t = document.getElementById(id);
    if (!t) throw new Error('no table #' + id);
    t.textContent = '';
    const th = t.createTHead().insertRow();
    head.forEach(h => { const c = document.createElement('th'); c.innerHTML = h.html || h; if (h.num) c.className = 'num'; th.appendChild(c); });
    const tb = t.createTBody();
    rows.forEach(r => {
      const tr = tb.insertRow();
      r.forEach((v, k) => {
        const c = tr.insertCell();
        c.innerHTML = v == null ? '—' : v;
        if (head[k] && head[k].num) c.className = 'num';
      });
    });
    if (t.classList.contains('stack')) CK.stackTable(t);
    if (o.sort) CK.sortTable(t);
    return t;
  }
  const sub = s => `<span class="sub">${s}</span>`;
  const word = (s, ok) => `<span class="word ${ok ? 'pass' : 'fail'}">${s}</span>`;

  /* ---- a panel's axes: horizontal grid, y ticks, baseline, x ticks ---- */
  function panelAxes(g, b, x, y, yt, xt, o) {
    o = o || {};
    const labs = [];
    yt.forEach(t => {
      CK.el('line', {x1: b.x0, x2: b.x1, y1: y(t), y2: y(t), class: 'grid-line'}, g);
      if (o.ylab !== false) labs.push(CK.txt(g, b.x0 - 6, y(t) + 4, (o.yfmt || tTick)(t), 'tick', 'end'));
    });
    CK.el('line', {x1: b.x0, x2: b.x1, y1: b.y1, y2: b.y1, class: 'ck-axis'}, g);
    xt.forEach(t => labs.push(CK.txt(g, x(t.v), b.y1 + 16, t.label, 'tick', 'middle')));
    return labs;
  }

  /* ================= 1. one core's time over n, k, eta ================= */
  const G = D.grid;
  const NCOL = {};
  G.ns.forEach((n, i) => { NCOL[n] = CK.color(i); });
  CK.legend('gridleg', G.ns.map(n => ({key: 'n' + n, label: 'n = ' + n, color: NCOL[n], mark: 'line'})).concat([
    {key: 'ge', label: 'GF(2) elimination, noiseless', color: 'var(--ink-2)', mark: 'diamond'},
    {key: 'big', label: 'work ≥ 10¹²', color: 'var(--ink-2)', mark: 'dot'},
    {key: 'small', label: 'work < 10¹²', color: 'var(--ink-2)', mark: 'ring'}]));
  const showKey = {};
  Object.entries(G.show).forEach(([id, t]) => { showKey[t.join(',')] = id; });

  function drawGrid(f) {
    const W = f.W, wide = W >= 700, L = 62, R = 12, T = 30, ph = 200, stride = ph + 76;
    const pw = wide ? (W - L - R - 40) / 3 : W - L - R;
    const nodes = [], labs = [];
    const y0s = G.ks.map((k, i) => (wide ? T : T + i * stride));
    G.ks.forEach((k, i) => {
      const b = {x0: wide ? L + i * (pw + 20) : L, y0: y0s[i]};
      b.x1 = b.x0 + pw; b.y1 = b.y0 + ph;
      const x = CK.lin(-0.035, 0.435, b.x0 + 4, b.x1 - 4), y = CK.log(3e-5, 4e3, b.y1, b.y0);
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      labs.push(...panelAxes(g, b, x, y, [1e-4, 1e-3, 1e-2, 0.1, 1, 10, 100, 1000],
        G.etas.map(e => ({v: e, label: num(e, e ? 1 : 0)})), {ylab: !wide || i === 0}));
      const c512 = G.pts.find(p => p.n === 512 && p.k === k).cand;
      labs.push(CK.txt(g, b.x0, b.y0 - 12, `k = ${k}`, 'lab-strong'));
      labs.push(CK.txt(g, b.x0 + 40, b.y0 - 12, `C(512, ${k}) = ${sciU(c512)}`, 'lab'));
      if (!wide || i === 1) labs.push(CK.txt(g, (b.x0 + b.x1) / 2, b.y1 + 34, 'noise η', 'lab', 'middle'));
      G.ns.forEach(n => {
        const pts = G.pts.filter(p => p.n === n && p.k === k).sort((a, c) => a.eta - c.eta);
        CK.el('path', {d: CK.path(pts.map(p => [p.eta, p.t]), x, y), class: 'ln', style: `stroke:${NCOL[n]}`, 'data-series': 'n' + n}, f.svg);
      });
      /* noiseless elimination: one diamond per n at eta = 0, a little left of the scan's point */
      G.ge.forEach(ge => {
        const gx = x(0) - 9, gy = y(ge.s), gg = CK.el('g', {'data-series': 'n' + ge.n}, f.svg);
        CK.el('circle', {cx: gx, cy: gy, r: 10, class: 'ck-hit'}, gg);
        const d = CK.el('polygon', {points: `${gx},${gy - 5} ${gx + 5},${gy} ${gx},${gy + 5} ${gx - 5},${gy}`}, gg);
        d.style.fill = NCOL[ge.n]; d.style.stroke = 'var(--surface)'; d.style.strokeWidth = '1.5';
        CK.tip(f, gg, `<b>GF(2) elimination, noiseless, n = ${ge.n}</b><br>${fmtS(ge.s)} on one core (median, k = 3; any k)` +
          `<br>full rank by m = n + ${ge.extra_max} in all ${ge.runs} runs`);
        nodes.push(gg);
      });
      G.ns.forEach(n => {
        G.pts.filter(p => p.n === n && p.k === k).sort((a, c) => a.eta - c.eta).forEach(p => {
          const px = x(p.eta), py = y(p.t), gg = CK.el('g', {'data-series': 'n' + n}, f.svg);
          CK.el('circle', {cx: px, cy: py, r: 11, class: 'ck-hit'}, gg);
          const big = p.W >= 1e12;
          const c = CK.el('circle', {cx: px, cy: py, r: 4.5}, gg);
          c.style.fill = big ? NCOL[n] : 'var(--surface)'; c.style.stroke = big ? 'var(--surface)' : NCOL[n];
          c.style.strokeWidth = big ? '1.5' : '2';
          const sk = showKey[[n, k, p.eta].join(',')];
          CK.tip(f, gg, `<b>n = ${n}, k = ${k}, η = ${p.eta}</b>${sk ? ' · ' + LAB(sk) : ''}<br>m = ${num(p.m, 0)} samples (${p.msrc}); ` +
            `${sciH(p.cand, 2)} candidates; work ${sciH(p.W, 2)}<br>one core: <b>${fmtS(p.t)}</b> (${p.tsrc})`);
          nodes.push(gg);
          if (sk) {
            const ring = CK.el('circle', {cx: px, cy: py, r: 9, 'aria-hidden': 'true'}, f.svg);
            ring.style.fill = 'none'; ring.style.stroke = 'var(--ink)'; ring.style.strokeWidth = '1.5';
            labs.push(CK.txt(f.svg, px - 12, py - 10, LAB(sk), 'lab-strong', 'end'));
          }
        });
      });
    });
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('gridchart', {label: "One core's time for the exhaustive scan against noise, by n and k",
    height: W => (W >= 700 ? 30 + 200 + 46 : 3 * 276), draw: drawGrid});

  const gridRows = [];
  G.ns.forEach(n => G.ks.forEach(k => {
    const ps = G.pts.filter(p => p.n === n && p.k === k).sort((a, c) => a.eta - c.eta);
    gridRows.push([String(n), String(k), sciH(ps[0].cand, 2)].concat(ps.map(p => `${fmtS(p.t)}${sub('m = ' + num(p.m, 0) + (p.msrc === 'model' ? ' (model)' : ''))}`)));
  }));
  table('gridtable', [{html: 'n'}, {html: 'k'}, {html: 'C(n,k)', num: true}].concat(G.etas.map(e => ({html: 'η = ' + num(e, e ? 1 : 0), num: true}))), gridRows);

  const cpu = D.cpu.per;
  table('showtable', ['Size', '(n, k, η, m)', {html: 'Candidates C(n,k)', num: true}, {html: 'Work C(n,k)·m', num: true},
    {html: "One core, SP3's scan", num: true}, {html: 'One core, tuned scan', num: true}],
  D.inst.map(i => {
    const p = G.pts.find(q => q.n === i.n && q.k === i.k && q.eta === i.eta);
    return [`<b>${i.label}</b>`, `(${i.n}, ${i.k}, ${i.eta}, ${num(i.m, 0)})`, num(i.cand, 0), sciH(i.W, 2),
      fmtS(p.t) + sub(p.tsrc + ', aifoundry1'), fmtS(cpu[i.id].one_core) + sub('<code>spbase vexh</code>, aifoundry3')];
  }));

  /* ================= 2. the diagram ================= */
  const SH = [0, 1, 2, 3, 4];  // the first five blocks, dealt to shires 0-4
  function drawTiles(f) {
    const W = f.W, NR = 10, NC = 8, c0 = [0, 0, 1, 1, 2, 2, 3, 4, 5, 6];
    const gx = 20, gy = 26, cell = Math.min(24, (W - gx - 6) / NC), labs = [];
    labs.push(CK.txt(f.svg, gx, 14, 'features j, 16 per column tile →', 'lab'));
    for (let r = 0; r < NR; r++) {
      const blk = Math.floor(r / 2), strip = CK.el('rect', {x: 4, y: gy + r * cell + 1, width: 9, height: cell - 2, rx: 2, 'aria-hidden': 'true'}, f.svg);
      strip.style.fill = CK.color(SH[blk]);
      for (let c = 0; c < NC; c++) {
        const valid = c >= c0[r], edge = c === c0[r];
        const rect = CK.el('rect', {x: gx + c * cell + 1, y: gy + r * cell + 1, width: cell - 2, height: cell - 2, rx: 2, 'aria-hidden': 'true'}, f.svg);
        rect.style.fill = valid ? mix('var(--ink)', edge ? 10 : 24) : 'var(--page)';
        rect.style.stroke = valid ? 'var(--surface)' : 'var(--grid)';
      }
    }
    const hr = 6, hc = 5, hg = CK.el('g', {}, f.svg);
    const hi = CK.el('rect', {x: gx + hc * cell + 1, y: gy + hr * cell + 1, width: cell - 2, height: cell - 2, rx: 2}, hg);
    hi.style.fill = mix('var(--c1)', 55); hi.style.stroke = 'var(--c1)'; hi.style.strokeWidth = '2';
    CK.tip(f, hg, '<b>One output tile</b><br>16 rows × 16 features: S = ⌈m/64⌉ int8 tensor ops of 64 samples each, accumulated in int32; L2 has S = 29');
    const edgeG = CK.el('g', {}, f.svg);
    const er = 4, ec = c0[er];
    const hitE = CK.el('rect', {x: gx + ec * cell + 1, y: gy + er * cell + 1, width: cell - 2, height: cell - 2, class: 'ck-hit'}, edgeG);
    CK.tip(f, edgeG, '<b>A boundary tile</b><br>computed whole; the entries with j ≤ max R are masked in the epilogue');
    void hitE;
    labs.push(CK.txt(f.svg, gx, gy + NR * cell + 16, '↓ rows R, 16 per row tile, colex order', 'lab'));
    CK.inside(f, labs);
    CK.keynav(f, [hg, edgeG]);
  }
  CK.frame('dgtiles', {label: 'The staircase of tiles', minW: 200, maxW: 420, height: W => 26 + 10 * Math.min(24, (W - 26) / 8) + 24, draw: drawTiles});

  function drawChip(f) {
    const W = f.W, cols = 8, rows = 4, gap = 4, sw = (W - 8 - gap * (cols - 1)) / cols, sh = sw * 0.72, nodes = [], labs = [];
    for (let s = 0; s < 32; s++) {
      const cx = 4 + (s % cols) * (sw + gap), cy = 4 + Math.floor(s / cols) * (sh + gap), g = CK.el('g', {}, f.svg);
      const box = CK.el('rect', {x: cx, y: cy, width: sw, height: sh, rx: 3}, g);
      const k = SH.indexOf(s);
      box.style.fill = k >= 0 ? mix(CK.color(k), 30) : 'var(--page)';
      box.style.stroke = k >= 0 ? CK.color(k) : 'var(--axis)';
      for (let m = 0; m < 32; m++) {
        const d = CK.el('circle', {cx: cx + sw * ((m % 8) + 1) / 9, cy: cy + sh * (Math.floor(m / 8) + 1) / 5, r: Math.max(0.8, Math.min(1.6, sw / 24)), 'aria-hidden': 'true'}, g);
        d.style.fill = 'var(--ink-2)';
      }
      CK.tip(f, g, `<b>Shire ${s}</b>: 32 minions, a 2.5 MB scratchpad holding the features; blocks ${s}, ${s + 32}, ${s + 64} and ${s + 96} of the plan's 4,096 go to its minions 0–3, and so on`);
      nodes.push(g);
    }
    labs.push(CK.txt(f.svg, 4, 4 + rows * (sh + gap) + 14, 'block q → shire q mod 32 (first five coloured)', 'lab'));
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('dgchip', {label: 'The 32 shires of 32 minions', minW: 200, maxW: 420,
    height: W => { const sw = (W - 8 - 28) / 8; return 4 + 4 * (sw * 0.72 + 4) + 22; }, draw: drawChip});

  /* ================= 3. the ladder ================= */
  const LD = D.ladder, MS = LD.ms.map(m => m.id);
  CK.legend('ladleg', [
    {key: 'card', label: 'card, measured', color: 'var(--c1)', mark: 'dot'},
    {key: 'design', label: "design's first prediction", color: 'var(--ref)', mark: 'ring'},
    {key: 'cpu1', label: 'CPU, one core (tuned scan)', color: 'var(--c2)', mark: 'line'},
    {key: 'cpu6', label: 'CPU, six threads, best method', color: 'var(--c3)', mark: 'line'}]);
  function drawLadder(f) {
    const W = f.W, wide = W >= 720, L = 52, R = 50, T = 30, ph = 210, stride = ph + 90, ids = ['L1', 'L2', 'F5'];
    const ow = wide ? (W - 24) / 3 : W, nodes = [], labs = [];
    const y0s = ids.map((id, i) => (wide ? T : T + i * stride));
    ids.forEach((id, i) => {
      const ox = wide ? i * (ow + 12) : 0, b = {x0: ox + L, x1: ox + ow - R, y0: y0s[i]};
      b.y1 = b.y0 + ph;
      const y = CK.log(0.03, 30, b.y1, b.y0), slot = j => b.x0 + (j + 0.5) * (b.x1 - b.x0) / MS.length;
      const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
      labs.push(...panelAxes(g, b, v => v, y, [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20], MS.map((m, j) => ({v: slot(j), label: m})),
        {yfmt: v => num(v) + ' s'}));
      const I = INST[id];
      const tup = `(${I.n}, ${I.k}, ${I.eta}, ${num(I.m, 0)})`;
      if (id === 'F5') labs.push(CK.txt(g, b.x0, b.y0 - 12, tup, 'lab-strong'));
      else { labs.push(CK.txt(g, b.x0, b.y0 - 12, I.label, 'lab-strong')); labs.push(CK.txt(g, b.x0 + 22, b.y0 - 12, tup, 'lab')); }
      /* CPU reference lines, labelled in the right margin */
      const refs = [['cpu1', LD.cpu1[id], 'var(--c2)', '1 core', `CPU, one core: the tuned AVX-512 scan, one stage: <b>${fmtS(LD.cpu1[id])}</b>`],
        ['cpu6', LD.cpu6[id].s, 'var(--c3)', '6 thr.', `CPU, six threads: ${LD.cpu6[id].method}, P(loss) ${LD.cpu6[id].ploss ? sciH(LD.cpu6[id].ploss, 1) : '0 (it verifies every hit)'}: <b>${fmtS(LD.cpu6[id].s)}</b>`]];
      let lastY = -99;
      refs.sort((a, c) => c[1] - a[1]).forEach(([key, v, col, short, tipText]) => {
        const rg = CK.el('g', {}, f.svg), yy = y(v);
        CK.el('line', {x1: b.x0, x2: b.x1, y1: yy, y2: yy, class: 'ck-hit', style: 'stroke:transparent;stroke-width:12'}, rg);
        const ln = CK.el('line', {x1: b.x0, x2: b.x1, y1: yy, y2: yy}, rg);
        ln.style.stroke = col; ln.style.strokeWidth = '2';
        CK.tip(f, rg, tipText);
        nodes.push(rg);
        let ty = yy + 4;
        if (ty - lastY < 13) ty = lastY + 13;
        lastY = ty;
        labs.push(CK.txt(f.svg, b.x1 + 5, ty, short, 'lab'));
      });
      /* design predictions (M3 private loads, M4 cooperative loads) */
      ['M3', 'M4'].forEach(m => {
        const v = LD.design[id][m], j = MS.indexOf(m), gg = CK.el('g', {}, f.svg);
        CK.el('circle', {cx: slot(j), cy: y(v), r: 10, class: 'ck-hit'}, gg);
        const c = CK.el('circle', {cx: slot(j), cy: y(v), r: 5}, gg);
        c.style.fill = 'var(--surface)'; c.style.stroke = 'var(--ref)'; c.style.strokeWidth = '2';
        CK.tip(f, gg, `<b>DESIGN.md's first prediction, ${m}</b><br>${m === 'M3' ? 'private operand loads' : 'cooperative operand loads (never built)'}: ${fmtS(v)}`);
        nodes.push(gg);
      });
      /* the card */
      const pts = LD.series[id];
      CK.el('path', {d: CK.path(pts.map(p => [slot(MS.indexOf(p.ms)), p.s]), v => v, y), class: 'ln', style: 'stroke:var(--c1)', 'aria-hidden': 'true'}, f.svg);
      pts.forEach((p, k) => {
        const px = slot(MS.indexOf(p.ms)), py = y(p.s), gg = CK.el('g', {}, f.svg);
        CK.el('circle', {cx: px, cy: py, r: 11, class: 'ck-hit'}, gg);
        const c = CK.el('circle', {cx: px, cy: py, r: 5}, gg);
        c.style.fill = 'var(--c1)'; c.style.stroke = 'var(--surface)'; c.style.strokeWidth = '2';
        CK.tip(f, gg, `<b>${I.label}, ${p.ms}: ${fmtS(p.s)}</b><br>${esc(p.note)}`);
        nodes.push(gg);
        /* the card's times as a row under the milestone labels, the last in bold */
        labs.push(CK.txt(f.svg, px, b.y1 + 32, fmtS(p.s), k === pts.length - 1 ? 'lab-strong' : 'lab', 'middle'));
      });
      if (!wide || i === 1) labs.push(CK.txt(g, (b.x0 + b.x1) / 2, b.y1 + 50, 'milestone · card time', 'lab', 'middle'));
    });
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('ladchart', {label: 'Time per solve at each milestone against the CPU', height: W => (W >= 720 ? 30 + 210 + 58 : 3 * 300), draw: drawLadder});

  const r1 = D.cpu.r1, r6 = D.cpu.r6, r16 = D.cpu.r16;
  const m5by = {};
  D.m5.forEach(r => { m5by[r.id] = r; });
  table('cmptable', ['Size', {html: 'Card, two-stage', num: true}, {html: 'Card, one stage', num: true},
    {html: 'CPU, 1 core', num: true}, {html: 'CPU, 6 threads', num: true}, {html: 'CPU, 16 threads, extrapolated', num: true},
    {html: 'Card vs 1 core', num: true}, {html: 'vs 6 threads', num: true}, {html: 'vs 16 threads', num: true}],
  D.inst.map(i => {
    const c = cpu[i.id], m = m5by[i.id];
    return [`<b>${i.label}</b>`, `<b>${fmtS(m.solve)}</b>`, fmtS(m.one_stage), fmtS(c.one_core) + sub('tuned AVX-512 scan'),
      fmtS(c.best6) + sub(c.best6_short + (c.best6_ploss ? ', P(loss) ' + sciH(c.best6_ploss, 1) : '')),
      `${fmtS(c.best16[0])}–${fmtS(c.best16[1])}`, x2(r1[i.id]) + '×', x2(r6[i.id]) + '×', rngX(r16[i.id][0], r16[i.id][1])];
  }));

  table('laddertable', ['Size', 'Milestone', {html: 'Time', num: true}, 'What ran', 'Data'],
    D.ladder_rows.map(r => [`<b>${LAB(r.id)}</b>`, r.ms, fmtS(r.s), esc(r.note),
      r.file.split(', ').map(p => `<code>${esc(p.replace('workloads/sparseparity/data/', ''))}</code>`).join('<br>')]));

  const M1TXT = {
    'm1-c0-scalar': ['C0 (32, 3, 0.1, 128), scalar path, 1 minion', 'every one of the 4,960 correlations equal to the CPU\'s'],
    'm1-c0-tensor': ['C0, tensor path, 1 minion', 'every correlation equal to the CPU\'s'],
    'm1-neg-drop': ['control: one tile dropped', 'both closed forms must fail'],
    'm1-neg-dup': ['control: one tile scanned twice', 'both closed forms must fail'],
    'm1-neg-mask': ['control: one tile\'s staircase shifted', 'both closed forms must fail'],
    'm1-tie': ['the tie instance, 1 minion', 'solved must be false: two candidates tie'],
    'm1-c1': ['C1 (128, 4, 0.2, 192), 1 minion, rows resident (S = 3)', 'closed forms, oracle'],
    'm1-l1-timing': ['L1 slice 0 of 64, 1 minion, no epilogue (S = 7)', 'cycles per op against 280'],
    'm1-l1': ['L1 slice 0 of 64, 1 minion, with the epilogue', 'oracle'],
    'm1-l2-timing': ['L2 slice 0 of 200, 1 minion, no epilogue (S = 29)', 'cycles per op against 280'],
    'm1-l2': ['L2 slice 0 of 200, 1 minion, with the epilogue', 'oracle'],
  };
  const m1rows = D.m1.map(r => {
    const t = M1TXT[r.step] || [r.step, ''];
    const expectFail = /neg-/.test(r.step), ok = expectFail ? r.status === 'FAIL' : r.status !== 'FAIL';
    return [`<code>${r.step}</code>`, t[0] + sub(t[1]), word(r.status, ok) + (expectFail ? sub('as designed') : ''), fmtS(r.launch), num(r.cyc_op, 0)];
  });
  m1rows.push(['<code>m1-c1-32-seed1…20</code>', 'C1 on one shire\'s 32 minions, seeds 1–20' + sub('closed forms on each'), word(V.seeds + ' PASS', true) + sub('solved on ' + V.seedsSolved), '—', '—']);
  m1rows.push(['<code>probe-*</code>', 'the hand-off probe: 16–32 minions consume each row tile right after it is published' + sub('scratchpad and DRAM staging, 1 and 2 buffers'), word(V.probes + ' PASS', true) + sub('full oracle on every minion'), '—', '—']);
  D.knee.forEach(k => m1rows.push([`<code>m2-knee-p${k.p}-timing</code>`, `L1 slice on ${k.p} minion${k.p > 1 ? 's' : ''} of one shire, the same work each` + sub('no epilogue'), word('TIMING', true), '—', num(k.cyc_op, 0)]));
  m1rows.push(['<code>m2-l1-full</code>', 'all of L1 on one shire (32 minions)' + sub('closed forms'), word('PASS', true) + sub('slowest minion ' + V.m2imb + '× the median'), V.m2L1, '—']);
  m1rows.push(['<code>m2-l2-q0-nowait</code>', 'L2 slice without the manual\'s TensorWait before an A reload' + sub('silicon only'), word(V.nowait, false) + sub('a wrong result: the wait is needed'), '—', '—']);
  table('m1table', ['Step', 'What it runs', 'Result', {html: 'Launch', num: true}, {html: 'Cycles per op', num: true}], m1rows);

  const AB = ['m1', 'a', 'b', 'c', 'm4', 'm4d'];
  table('abtable', ['Size'].concat(AB.map(v => ({html: v === 'b' ? '<b>b</b>' : v, num: true}))),
    D.m4ab.map(r => [`<b>${LAB(r.id)}</b>`].concat(AB.map(v => (r.vals[v] == null ? '—'
      : (v === 'b' ? `<b>${fmtS(r.vals[v])}</b>` : fmtS(r.vals[v])) + sub(num(r.cyc[v], 0) + ' cyc/op'))))));

  table('m5table', ['Size', 'Stage 1', {html: 'P(loss)', num: true}, {html: 'Survivors', num: true}, {html: 'Launch', num: true},
    {html: 'Readback + stage 2', num: true}, {html: 'Solve', num: true}, {html: 'One stage (b)', num: true}, 'Full oracle, offline'],
  D.m5.map(r => [`<b>${LAB(r.id)}</b>`, `m<sub>1</sub> = ${num(r.m1, 0)}, τ<sub>1</sub> = ${r.tau1}`, sciH(r.ploss, 1),
    num(r.found, 0) + sub(`${num(r.found / r.expected, 3)}× expected; ${num(r.log_mb, 0)} MB of logs`), fmtS(r.launch),
    `${fmtS(r.readback)} + ${fmtS(r.stage2)}`, `<b>${fmtS(r.solve)}</b>` + sub('model ' + fmtS(r.model)), fmtS(r.one_stage),
    esc(r.offline.replace('1024', '1,024'))]));
  document.getElementById('m5note').innerHTML = `Every run found the secret, and it survived stage 1. Stage 2 runs on six host threads and
    re-derives every logged c<sub>1</sub>. A resident stage 1 at L1 (m<sub>1</sub> = ${D.res192.m1}, τ<sub>1</sub> = ${D.res192.tau1})
    risked more: P(loss) ${sciH(D.res192.ploss, 1)}, ${sciH(D.res192.found, 1)} survivors, ${fmtS(D.res192.solve)} to solve.
    The one-stage column is variant b in M4's A/B; M5's session reran it at L1 and L2 in
    ${D.m5.filter(r => r.one_stage_rerun).map(r => fmtS(r.one_stage_rerun)).join(' and ')}.
    The controls below ran on one shire or a slice and must fail as shown.`;
  table('ctltable', ['Control', 'What it does', 'Result'], D.controls.map(c => [`<code>${c.step}</code>`, esc(c.what),
    word(c.status, c.status === c.expect) + sub('expected ' + c.expect)]));

  /* ================= 4. energy ================= */
  CK.legend('enleg', [
    {key: 'over', label: 'card board above idle', color: 'var(--c1)', mark: 'ring'},
    {key: 'total', label: 'card board, idle included', color: 'var(--c1)', mark: 'dot'},
    {key: 'host', label: "+ the host's package (assumed)", color: 'var(--c1)', mark: 'dash'},
    {key: 'cpu', label: 'CPU package, assumed 125–251 W', color: 'var(--c2)', mark: 'box'}]);
  function drawEnergy(f) {
    const W = f.W, L = W < 480 ? 58 : 70, R = 14, T = 12, rowH = 76, rows = D.energy, nodes = [], labs = [];
    const x = CK.log(1, 2000, L, W - R), ytop = T, ybot = T + rows.length * rowH;
    const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    [1, 3, 10, 30, 100, 300, 1000].forEach(t => {
      CK.el('line', {x1: x(t), x2: x(t), y1: ytop, y2: ybot, class: 'grid-line'}, g);
      labs.push(CK.txt(g, x(t), ybot + 16, num(t) + ' J', 'tick', 'middle'));
    });
    CK.el('line', {x1: L, x2: W - R, y1: ybot, y2: ybot, class: 'ck-axis'}, g);
    labs.push(CK.txt(g, (L + W - R) / 2, ybot + 34, 'joules per solve (log scale)', 'lab', 'middle'));
    rows.forEach((e, i) => {
      const yc = T + i * rowH + 16;
      labs.push(CK.txt(f.svg, L - 10, yc + 4, LAB(e.id), 'lab-strong', 'end'));
      labs.push(CK.txt(f.svg, L - 10, yc + 22, 'CPU', 'lab', 'end'));
      /* card + host range */
      const hg = CK.el('g', {}, f.svg), h0 = x(e.j_total + e.host[0]), h1 = x(e.j_total + e.host[1]);
      CK.el('rect', {x: h0 - 4, y: yc - 10, width: h1 - h0 + 8, height: 20, class: 'ck-hit'}, hg);
      const hl = CK.el('line', {x1: h0, x2: h1, y1: yc, y2: yc}, hg);
      hl.style.stroke = 'var(--c1)'; hl.style.strokeWidth = '2'; hl.style.strokeDasharray = '4 3';
      [h0, h1].forEach(xx => { const t = CK.el('line', {x1: xx, x2: xx, y1: yc - 5, y2: yc + 5}, hg); t.style.stroke = 'var(--c1)'; t.style.strokeWidth = '2'; });
      CK.tip(f, hg, `<b>${LAB(e.id)}: the card's board plus the host's package, assumed</b><br>${num(e.j_total + e.host[0], 1)}–${num(e.j_total + e.host[1], 1)} J per solve (the host: ${num(e.host[0], 1)}–${num(e.host[1], 1)} J)`);
      /* card: above idle (ring), total (dot) */
      const og = CK.el('g', {}, f.svg);
      CK.el('circle', {cx: x(e.j_over), cy: yc, r: 10, class: 'ck-hit'}, og);
      const oc = CK.el('circle', {cx: x(e.j_over), cy: yc, r: 5}, og);
      oc.style.fill = 'var(--surface)'; oc.style.stroke = 'var(--c1)'; oc.style.strokeWidth = '2';
      CK.tip(f, og, `<b>${LAB(e.id)}: the board above idle</b><br>${num(e.j_over, 2)} J per solve (the SP's board average less the leakage's rise, ±3%)`);
      const tg = CK.el('g', {}, f.svg);
      CK.el('circle', {cx: x(e.j_total), cy: yc, r: 10, class: 'ck-hit'}, tg);
      const tc = CK.el('circle', {cx: x(e.j_total), cy: yc, r: 5.5}, tg);
      tc.style.fill = 'var(--c1)'; tc.style.stroke = 'var(--surface)'; tc.style.strokeWidth = '2';
      CK.tip(f, tg, `<b>${LAB(e.id)}: the board, idle included</b><br>${num(e.j_total, 1)} J per solve; ${num(e.solves_per_s, 2)} solves per second`);
      labs.push(CK.txt(f.svg, x(e.j_total), yc - 11, num(e.j_total, e.j_total < 50 ? 1 : 0) + ' J', 'lab-strong', 'middle'));
      /* CPU, assumed */
      const cg = CK.el('g', {}, f.svg), c0 = x(e.cpu_j[0]), c1 = x(e.cpu_j[1]);
      const cr = CK.el('rect', {x: c0, y: yc + 13, width: Math.max(2, c1 - c0), height: 12, rx: 2}, cg);
      cr.style.fill = mix('var(--c2)', 35); cr.style.stroke = 'var(--c2)'; cr.style.strokeWidth = '1.5'; cr.style.strokeDasharray = '4 2';
      labs.push(CK.txt(f.svg, c1 + 6, yc + 23, `${num(e.cpu_j[0], e.cpu_j[0] < 50 ? 1 : 0)}–${num(e.cpu_j[1], 0)} J`, 'lab'));
      CK.tip(f, cg, `<b>${LAB(e.id)}: the CPU's package, assumed</b><br>${num(e.cpu_j[0], 1)}–${num(e.cpu_j[1], 0)} J = ${fmtS(e.cpu_s)} (six threads, ${esc(e.cpu_method)}) × 125–251 W, idle included; not measured`);
      labs.push(CK.txt(f.svg, L, yc + 44, `CPU ÷ card: ${rngX(e.ratio_board[0], e.ratio_board[1])} (board), ${rngX(e.ratio_host[0], e.ratio_host[1])} (with the host)`, 'lab'));
      nodes.push(og, tg, hg, cg);
    });
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('enchart', {label: "Joules per solve: the card's board against the CPU's assumed package", height: () => 8 + 3 * 76 + 44, draw: drawEnergy});

  table('entable', ['Size', 'Solves', 'Board: burst / idle', 'J per solve: above idle / with idle',
    'Rails above idle, J: minion / SRAM / NoC / unmetered', 'CPU, J (<span class="assumed">assumed</span>)', 'CPU ÷ card'],
  D.energy.map(e => {
    const bw = Array.isArray(e.board_w) ? e.board_w.map(v => num(v, 1)).join(', ') : num(e.board_w, 1);
    const sv = Array.isArray(e.solves) ? e.solves.join(' + ') + ' halves' : String(e.solves);
    const rj = e.rails_j;
    return [`<b>${LAB(e.id)}</b>`, sv + sub(num(e.solves_per_s, 2) + ' solves/s'), `${bw} / ${num(e.idle_w, 1)} W` + sub(`die ${num(e.die[0], 0)} → ${num(e.die[1], 1)} °C`),
      `${num(e.j_over, 2)} / <b>${num(e.j_total, 1)}</b>` + sub('catalogue method ' + num(e.j_catalogue, 2) + ' above idle'),
      `${num(rj.minion, 2)} / ${num(rj.sram, 2)} / ${num(rj.noc, 2)} / ${num(rj.unmetered, 2)}`,
      `${num(e.cpu_j[0], 1)}–${num(e.cpu_j[1], 0)}` + sub(fmtS(e.cpu_s) + ' × 125–251 W'),
      rngX(e.ratio_board[0], e.ratio_board[1]) + sub('with the host ' + rngX(e.ratio_host[0], e.ratio_host[1]))];
  }));

  /* ================= 5. where the time goes ================= */
  const PARTS = [['op', 'tensor op'], ['epi', 'epilogue'], ['smt', 'issue-slot sharing'], ['wait', "waiting for hart 1's rows"], ['other', 'other overhead']];
  CK.legend('cycleg', PARTS.map(([k, l], i) => ({key: k, label: l, color: CK.color(i), mark: 'box'})));
  const CR = [];
  D.cycles.runs.forEach(r => {
    const nm = r.run === 'm3-l1' ? 'L1' : 'L2';
    CR.push({lab: `M3 ${nm} (S = ${r.S}), mean minion`, parts: r.mean, total: r.mean_total});
    CR.push({lab: `M3 ${nm}, busiest minion`, parts: r.busiest, total: r.busiest_model_total, meas: r.busiest_meas});
  });
  function drawCycles(f) {
    const W = f.W, L = 8, R = 16, T = 34, rowH = 50, barH = 18, nodes = [], labs = [];
    const x = CK.lin(0, 1750, L, W - R), ybot = T + CR.length * rowH;
    const g = CK.el('g', {'aria-hidden': 'true'}, f.svg);
    [0, 250, 500, 750, 1000, 1250, 1500, 1750].forEach(t => {
      CK.el('line', {x1: x(t), x2: x(t), y1: T - 4, y2: ybot, class: 'grid-line'}, g);
      if (t % 500 === 0 || W >= 560) labs.push(CK.txt(g, x(t), ybot + 16, num(t, 0), 'tick', 'middle'));
    });
    CK.el('line', {x1: L, x2: W - R, y1: ybot, y2: ybot, class: 'ck-axis'}, g);
    labs.push(CK.txt(g, (L + W - R) / 2, ybot + 34, 'cycles per tensor op, hart 0, at 600 MHz', 'lab', 'middle'));
    CR.forEach((r, i) => {
      const yb = T + i * rowH + 18;
      labs.push(CK.txt(f.svg, L, yb - 6, r.lab, 'lab'));
      let acc = 0;
      PARTS.forEach(([k, l], j) => {
        const v = r.parts[k] || 0;
        if (v <= 0.5) return;
        const sg = CK.el('g', {}, f.svg), x0 = x(acc), w = x(acc + v) - x0;
        const rect = CK.el('rect', {x: x0, y: yb, width: Math.max(1, w - (w > 3 ? 2 : 0)), height: barH, rx: 2}, sg);
        rect.style.fill = CK.color(j);
        CK.tip(f, sg, `<b>${r.lab}</b><br>${l}: ${num(v, 0)} cycles per op (${num(100 * v / r.total, 0)}% of ${num(r.total, 0)})`);
        nodes.push(sg);
        acc += v;
      });
      if (r.meas) {
        const mg = CK.el('g', {}, f.svg), mx = x(r.meas);
        CK.el('rect', {x: mx - 6, y: yb - 6, width: 12, height: barH + 12, class: 'ck-hit'}, mg);
        const ml = CK.el('line', {x1: mx, x2: mx, y1: yb - 5, y2: yb + barH + 5}, mg);
        ml.style.stroke = 'var(--ink)'; ml.style.strokeWidth = '2';
        CK.tip(f, mg, `<b>${r.lab}: measured</b><br>${num(r.meas, 0)} cycles per op (the model: ${num(r.total, 0)})`);
        nodes.push(mg);
      }
    });
    [[270, '270'], [512, '512']].forEach(([v, t]) => {
      CR.forEach((r, i) => {
        const yb = T + i * rowH + 18, rl = CK.el('line', {x1: x(v), x2: x(v), y1: yb - 4, y2: yb + barH + 4, 'aria-hidden': 'true'}, f.svg);
        rl.style.stroke = 'var(--ink)'; rl.style.strokeWidth = '1.5'; rl.style.strokeDasharray = '3 2';
      });
      labs.push(CK.txt(f.svg, x(v), T - 14, t, 'lab-strong', 'middle'));
    });
    CK.inside(f, labs);
    CK.keynav(f, nodes);
  }
  CK.frame('cycchart', {label: "Cycles per tensor op in M3, split by the fitted model", height: () => 34 + 4 * 50 + 40, draw: drawCycles});

  table('cyctable', ['Minion', {html: 'Tensor op', num: true}, {html: 'Epilogue', num: true}, {html: 'Issue-slot sharing', num: true},
    {html: 'Waiting for rows', num: true}, {html: 'Other', num: true}, {html: 'Total (model)', num: true}, {html: 'Measured', num: true}],
  CR.map(r => [r.lab].concat(PARTS.map(([k]) => num(r.parts[k] || 0, 0)), [num(r.total, 0), r.meas ? num(r.meas, 0) : '—'])));

  table('latertable', ['Run', {html: 'Busiest minion, cycles per op', num: true}, {html: 'Busiest / median minion', num: true},
    {html: 'Launch', num: true}, {html: 'Floor at 512 cycles per op', num: true}],
  D.later.map(r => [esc(r.label), num(r.cyc_op, 0), r.imb ? num(r.imb, 2) : '—', r.launch ? fmtS(r.launch) : '—',
    r.floor ? fmtS(r.floor) : '—']));
})();
