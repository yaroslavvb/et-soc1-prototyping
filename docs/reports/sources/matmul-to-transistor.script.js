/* The matmul-to-transistor page. Every value comes from D, which build_data.py assembles from the
   committed data directories; nothing numeric is written here. The vault block at the end renders
   whatever an optional D.vault carries and nothing at all when it is absent. */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const $ = id => document.getElementById(id);
  const el = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a || {}) if (a[k] != null) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
  const tx = (p, x, y, s, cls, an) => { const t = el('text', {x, y, class: cls || 'tick', 'text-anchor': an || 'start'}, p); t.textContent = s; return t; };
  const set = (id, s) => { const e = $(id); if (e) e.textContent = s; };
  const MINUS = '−', NB = ' ', TIMES = '×', PM = '±', DEG = '°';

  function num(v, dp) {
    if (v == null || !isFinite(v)) return '—';
    if (dp == null) dp = v === 0 ? 0 : Math.min(6, Math.max(0, 2 - Math.floor(Math.log10(Math.abs(v)))));
    const s = Number(v).toLocaleString('en-GB', {minimumFractionDigits: dp, maximumFractionDigits: dp});
    return s.replace('-', MINUS);
  }
  const pct = (v, dp) => num(100 * v, dp == null ? 0 : dp) + '%';
  /* an energy in joules, printed in the unit that suits it */
  function eng(J) {
    const u = [[1e-12, 'pJ'], [1e-15, 'fJ'], [1e-18, 'aJ'], [1e-21, 'zJ']];
    for (const [s, n] of u) if (Math.abs(J) >= s) return num(J / s, Math.abs(J / s) >= 100 ? 0 : 2) + NB + n;
    return num(J / 1e-24, 2) + NB + 'yJ';
  }
  function sci(v) {
    if (v < 1e4) return num(v, 0);
    const e = Math.floor(Math.log10(v)), m = v / Math.pow(10, e);
    return num(m, 1) + NB + TIMES + NB + '10' + String(e).split('').map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+c]).join('');
  }
  const tile = (n, u, l, hi) =>
    '<div class="tile' + (hi ? ' hi' : '') + '"><div class="n">' + n + (u ? ' <span class="u">' + u + '</span>' : '') +
    '</div><div class="l">' + l + '</div></div>';

  /* Every chart is drawn into a viewBox as wide as its own container, so one user unit is one CSS pixel and
     12px chart type stays 12px on a phone. Before this the charts were fixed at 760-900 units behind a
     min-width of 660, which meant a 390px phone saw about half of each one -- the ladder lost its whole
     value column and the waterfall's last label was cut mid-word. Each draw() therefore takes its width and
     lays itself out for it, and the chart is redrawn when the container changes size. */
  function responsive(host, draw) {
    const box = $(host);
    if (!box) return;
    let last = -1;
    const run = () => {
      const w = Math.max(300, Math.min(900, Math.round(box.clientWidth || 900)));
      if (Math.abs(w - last) < 8) return;
      last = w;
      while (box.firstChild) box.removeChild(box.firstChild);
      draw(w);
    };
    run();
    if (window.ResizeObserver) new window.ResizeObserver(run).observe(box);
    else window.addEventListener('resize', run);
  }

  /* The same, for an element the callback rewrites itself (a table that transposes on a phone rather than
     scrolling sideways and hiding its last two columns). */
  function onWidth(host, draw) {
    const e = $(host);
    if (!e) return;
    const box = e.parentNode || e;
    let last = -1;
    const run = () => {
      const w = Math.max(300, Math.round(box.clientWidth || 900));
      if (Math.abs(w - last) < 8) return;
      last = w;
      draw(w);
    };
    run();
    if (window.ResizeObserver) new window.ResizeObserver(run).observe(box);
    else window.addEventListener('resize', run);
  }

  /* ---------------------------------------------------------------- 1. tiles */
  const sp = D.speed, bd = D.board, pm = D.permac, pb = D.perbit, tg = D.toggles, ga = D.gates, tr = D.transistor;
  const w800 = bd.measured.zeros['800'], r800 = bd.measured.randn['800'];
  $('tiles').innerHTML = [
    tile(num(sp.burst.pct, 0) + '%', 'faster', 'Zeros against random fp32, first 8 s on a cool die: ' +
      num(sp.burst.zeros_tflops, 1) + ' against ' + num(sp.burst.randn_tflops, 1) + ' TFLOPS', 1),
    tile(num(sp.sustained.pct, 0) + '%', 'faster', 'Sustained, once the thermal test takes over: ' +
      num(sp.sustained.zeros_tflops, 1) + ' against ' + num(sp.sustained.randn_tflops, 1) + ' TFLOPS', 1),
    tile(TIMES + num(r800 / w800, 2), 'the power', 'Board power at a fixed 800 MHz: ' + num(w800, 1) +
      ' against ' + num(r800, 1) + ' W'),
    tile(num(pm.mean_randn_pJ, 2), 'pJ', 'Per random fp32 multiply-add over idle, against ' +
      num(pm.mean_zeros_pJ, 2) + ' pJ on zeros'),
    tile(num(pb.e68_band_fJ[0], 0) + MINUS.replace(MINUS, '–') + num(pb.e68_band_fJ[1], 0), 'fJ',
      'Per flipped bit of an operand, at the board'),
    tile(num(tg.total_per_mac, 0), 'toggles', 'Physical net transitions per random multiply-add, on a placed open netlist'),
    tile(num(tr.electrons, 0), 'electrons', 'One minimum transistor’s gate, at the 0.517 V rail — ' +
      num(tr.E_aJ, 2) + ' aJ'),
    tile(sci(D.floor.rungs.transistor.over_Landauer_at_66C),
      TIMES + ' Landauer', 'The same switch against kT ln 2 at the die’s 66 ' + DEG + 'C trip')
  ].join('');

  set('a-burst', num(sp.burst.zeros_tflops, 1) + ' TFLOPS');
  set('a-burstr', num(sp.burst.randn_tflops, 1) + ' TFLOPS');
  set('a-burstpct', num(sp.burst.pct, 0) + '%');
  set('a-sus', num(sp.sustained.zeros_tflops, 1) + ' against ' + num(sp.sustained.randn_tflops, 1) + ' TFLOPS, ' + num(sp.sustained.pct, 0) + '%');
  set('a-wz', num(w800, 1) + ' W');
  set('a-wr', num(r800, 1) + ' W');
  set('a-pz', num(pm.mean_zeros_pJ, 2) + ' pJ');
  set('a-pr', num(pm.mean_randn_pJ, 2) + ' pJ');
  set('a-bit', num(pb.e68_band_fJ[0], 0) + '–' + num(pb.e68_band_fJ[1], 0) + ' fJ');
  set('a-pdata', num(pm.this_work_data_pJ, 2) + ' pJ');
  set('a-bits', num(pm.changed_bits, 1));
  set('a-perbit-chk', num(pm.data_per_changed_bit_fJ, 0) + ' fJ');
  set('a-tog', num(tg.total_per_mac, 0));
  set('a-fins', num(tr.fins_per_signal_net, 1));
  set('a-tr', num(tr.E_aJ, 2) + ' aJ');
  set('a-el', num(tr.electrons, 0));
  set('a-land', sci(D.floor.rungs.transistor.over_Landauer_at_66C));

  /* ------------------------------------------------------------- 2. the ladder */
  const DECADES = Math.log10(D.floor.rungs.mac_board.E_J / D.floor.rungs.electron.E_J);
  const DECW = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve'][Math.round(DECADES)] || num(DECADES, 1);
  /* "just under eight", not the "eleven" this page carried on its first build: the ladder runs from
     8.28e-20 J to 5.78e-12 J, which is 7.84 decades, and the chart's own axis shows it. */
  const DECPHRASE = (DECADES < Math.round(DECADES) ? 'just under ' : 'just over ') + DECW;
  set('a-dec', DECPHRASE);

  responsive('ladder', function (W) {
    const R = D.floor.rungs;
    const rows = [
      ['mac_board', 1, '0\u20134'], ['mac_netlist', 0, '6\u20137'],
      ['bit_board', 1, '5'], ['bit_netlist', 0, '6'],
      ['clock_rise', 0, '7'], ['signal_rise', 0, '7'], ['gate_pin', 0, '7'],
      ['fin_in_cell', 0, '8'], ['transistor', 0, '8'], ['electron', 0, '9']
    ].map(r => [R[r[0]].label, R[r[0]].E_J, r[1], r[2], R[r[0]].short || R[r[0]].label]);
    const land = D.floor.land66_J;
    const narrow = W < 620;
    const ROW = narrow ? 46 : 42, top = 38, padR = 6;
    const valW = narrow ? 58 : 76, VALX = W - padR;
    const legRows = narrow ? 2 : 1;
    const H = top + rows.length * ROW + 20 + legRows * 17;
    const L = 14, Rx = VALX - valW - 10;               // axis ends before the value column
    const lo = Math.log10(land) - 0.3, hi = Math.log10(rows[0][1]) + 0.25;
    const X = v => L + (Math.log10(v) - lo) * (Rx - L) / (hi - lo);
    const base = top + rows.length * ROW + 6;          // below the last rung: ticks, then the legend
    const s = el('svg', {viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'A logarithmic ladder of energy per event, from one electron across the rail at 83 zeptojoules up to one random floating-point multiply-add at the board at 5.8 picojoules \u2014 ' +
        DECPHRASE + ' orders of magnitude \u2014 with Landauer\u2019s floor marked below all of them.'}, $('ladder'));
    const sup = e => '10' + (e < 0 ? '\u2212' : '') + String(Math.abs(e)).split('').map(c => '\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079'[+c]).join('');
    const every = narrow ? 3 : 3;
    for (let e = Math.ceil(lo); e <= Math.floor(hi); e += 1) {
      const x = X(Math.pow(10, e));
      el('line', {x1: x, x2: x, y1: top + 4, y2: base - 10, stroke: 'var(--grid)'}, s);
      if (e % every === 0) tx(s, x, base + 4, sup(e), 'tick', 'middle').setAttribute('fill', 'var(--muted)');
    }
    if (!narrow) tx(s, L, base + 4, 'joules per event', 'tick').setAttribute('fill', 'var(--ink-2)');
    const lx = X(land);
    el('line', {x1: lx, x2: lx, y1: top - 4, y2: base - 10, stroke: 'var(--ref)', 'stroke-dasharray': '4 3'}, s);
    tx(s, lx, top - 12, narrow ? 'Landauer' : 'Landauer\u2019s floor, 66 ' + DEG + 'C', 'tick')
      .setAttribute('fill', 'var(--ref)');
    rows.forEach((r, i) => {
      const yl = top + 14 + i * ROW, ya = yl + 16;
      const t = tx(s, L, yl, narrow ? r[4] : r[0], narrow ? 'tick sm' : 'tick');
      t.setAttribute('fill', 'var(--ink)');
      if (r[2]) t.setAttribute('font-weight', '600');
      if (!narrow) tx(s, VALX, yl, 'step ' + r[3], 'tick', 'end').setAttribute('fill', 'var(--muted)');
      el('line', {x1: lx, x2: X(r[1]), y1: ya, y2: ya, stroke: 'var(--grid)', 'stroke-width': 2}, s);
      el('circle', {cx: X(r[1]), cy: ya, r: 5.5, fill: r[2] ? 'var(--c1)' : 'var(--page)',
        stroke: r[2] ? 'var(--c1)' : 'var(--c2)', 'stroke-width': 2}, s);
      tx(s, VALX, ya + 4, eng(r[1]), 'tick', 'end')
        .setAttribute('fill', r[2] ? 'var(--c1)' : 'var(--ink-2)');
    });
    const ly = base + 21;
    el('circle', {cx: L + 6, cy: ly - 4, r: 5, fill: 'var(--c1)'}, s);
    tx(s, L + 16, ly, 'measured on a card', 'tick').setAttribute('fill', 'var(--ink-2)');
    const l2x = narrow ? L + 6 : L + 150, l2y = narrow ? ly + 17 : ly;
    el('circle', {cx: l2x, cy: l2y - 4, r: 5, fill: 'var(--page)', stroke: 'var(--c2)', 'stroke-width': 2}, s);
    tx(s, l2x + 10, l2y, 'modelled or simulated', 'tick').setAttribute('fill', 'var(--ink-2)');
  });

  /* ---------------------------------------------------- 3. per-level fill-ins */
  set('lv0-big', num(sp.burst.zeros_tflops, 1) + ' against ' + num(sp.burst.randn_tflops, 1) +
    ' TFLOPS burst (' + num(sp.burst.pct, 0) + '%), ' + num(sp.sustained.zeros_tflops, 1) + ' against ' +
    num(sp.sustained.randn_tflops, 1) + ' sustained (' + num(sp.sustained.pct, 0) + '%)');
  const comp = Object.values(sp.comparators);
  set('lv0-range', TIMES + num(Math.min.apply(null, comp), 3) + ' to ' + TIMES + num(Math.max.apply(null, comp), 3));

  const gv = D.governor;
  set('lv1-big', num(gv.cap_W, 0) + ' W on a ' + num(gv.tau_s, 1) + ' s average of board power; a ' +
    num(gv.trip_C, 0) + ' ' + DEG + 'C die reading');
  set('lv1-tau', num(gv.tau_s, 1) + ' s');
  set('lv1-n', gv.n);
  set('lv1-rms', num(gv.rms_mhz, 1) + ' MHz rms');

  set('lv2-big', num(w800, 1) + ' W on zeros against ' + num(r800, 1) + ' W on random fp32, at a fixed 800 MHz');
  set('lv2-static', num(bd.static_B_W['600'], 2) + ' / ' + num(bd.static_B_W['700'], 2) + ' / ' + num(bd.static_B_W['800'], 2) + ' W');
  set('lv2-step', num(bd.step_W, 2) + ' W');

  set('lv3-big', num(D.rail.range[0], 2) + '–' + num(D.rail.range[1], 2) + ' of the board step reaches the minion rail');
  set('lv3-pair', num(D.rail.lq_ratio, 3) + ' and ' + num(D.rail.lb_ratio, 3));

  set('lv4-big', num(pm.mean_randn_pJ, 2) + ' pJ random, ' + num(pm.mean_ones_pJ, 2) + ' pJ all-ones, ' +
    num(pm.mean_zeros_pJ, 2) + ' pJ zeros');
  set('lv4-split', num(pm.budget_600_pJ.clocking, 2) + ' pJ of clocking and ' +
    num(pm.budget_600_pJ.data, 2) + ' pJ of data switching');

  set('lv5-big', num(pb.e68_band_fJ[0], 1) + '–' + num(pb.e68_band_fJ[1], 1) +
    ' fJ at the board; ' + num(pb.B_min, 0) + ' fJ to ' + num(pb.B_max, 0) + ' fJ depending on which bit');
  set('sat-naive', num(D.closure.superposition.naive_W.both, 1) + ' W');
  set('sat-meas', num(D.closure.superposition.measured_W.both_random, 1) + ' W');
  set('sat-x', TIMES + num(D.closure.superposition.naive_W.both / D.closure.superposition.measured_W.both_random, 2));
  const rows5 = pb.ladder_rows;
  set('sat-flat', num(Math.min.apply(null, rows5.map(r => r.meas_fJ_per_bit)), 0) + '–' +
    num(Math.max.apply(null, rows5.map(r => r.meas_fJ_per_bit)), 0) + ' fJ');
  set('sat-pred', num(Math.min.apply(null, rows5.map(r => r.naive_fJ_per_bit)), 0) + '–' +
    num(Math.max.apply(null, rows5.map(r => r.naive_fJ_per_bit)), 0) + ' fJ');
  set('sat-beta', num(pb.beta, 3));

  set('lv6-big', num(tg.total_per_mac, 0) + ' net toggles per random multiply-add, on about ' +
    num(tg.open_netlist_wires, 0) + ' distinct wires');
  set('lv7-big', num(ga.signal.E_per_toggle_fJ, 3) + ' fJ per signal-net toggle, ' +
    pct(ga.signal.share_transistor) + ' of it transistor gate; over the whole multiply-add, ' +
    pct(ga.split_share.transistor_gates));
  set('lv8-big', num(tr.E_aJ, 2) + ' aJ, ' + num(tr.Q_per_fin_aC, 1) + ' aC, ' + num(tr.electrons, 0) + ' electrons');
  set('lv8-cell', num(tr.in_a_cell.E_per_fin_aJ, 2) + ' aJ and ' + num(tr.in_a_cell.electrons_per_fin, 0) + ' electrons per fin');
  set('lv8-span', num(tr.range_aJ[0], 2) + '–' + num(tr.range_aJ[1], 2) + ' aJ');
  set('lv8-sc', pct(tr.short_circuit['0p517'].max_excess_share, 1));
  set('lv9-big', num(D.floor.land66_zJ, 3) +
    ' zJ is the floor; one electron across the rail is already ' +
    num(D.floor.rungs.electron.over_Landauer_at_66C, 1) + TIMES + ' it');

  /* -------------------------------------------------------- 4. the floor table */
  (function floortab() {
    const R = D.floor.rungs;
    $('floortab').querySelector('tbody').innerHTML = D.floor.order.map(k => {
      const r = R[k];
      return '<tr><td>' + r.label + '</td><td class="n">' + eng(r.E_J) + '</td><td class="n">' +
        sci(r.electrons) + '</td><td class="n">' + sci(r.over_Landauer_at_66C) + '</td></tr>';
    }).join('');
  }());

  /* ------------------------------------------------------------- 5. the charts */
  function frame(host, w, h, label) {
    const s = el('svg', {viewBox: '0 0 ' + w + ' ' + h, role: 'img', 'aria-label': label}, $(host));
    return s;
  }

  /* 5a. board power by pattern and clock */
  responsive('boardchart', function (W) {
    const m = bd.measured, clocks = [600, 700, 800];
    const keys = Object.keys(m).sort((a, b) => m[a]['800'] - m[b]['800']);
    const nice = {randn: 'random fp32', zeros: 'zeros', ones: 'all ones', signs: 'sign bits only',
      uniform: 'uniform', mant: 'mantissa bits', pow2: 'powers of two', sparse75: '75% sparse',
      a_randn_b_ones: 'a random, b ones', a_ones_b_randn: 'a ones, b random'};
    const narrow = W < 700;
    const H = narrow ? 290 : 330, L = narrow ? 40 : 56, Rt = narrow ? 10 : 210, T = narrow ? 26 : 16, B = 40;
    const vals = keys.map(k => clocks.map(c => m[k][String(c)])).flat();
    const ymax = Math.ceil(Math.max.apply(null, vals) / 10) * 10;
    const X = c => L + (c - 600) * (W - Rt - L) / 200, Y = v => H - B - v * (H - B - T) / ymax;
    const s = frame('boardchart', W, H,
      'Board power against clock for ten operand patterns. Zeros is the lowest line at every clock and random floating-point data the highest; the two diverge as the clock rises.');
    for (let v = 0; v <= ymax; v += 20) {
      el('line', {x1: L, x2: W - Rt, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 6, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    clocks.forEach((c, i) => tx(s, X(c), H - B + 18, narrow ? String(c) : c + ' MHz', 'tick',
      narrow ? (i === 0 ? 'start' : i === 2 ? 'end' : 'middle') : 'middle').setAttribute('fill', 'var(--muted)'));
    if (narrow) tx(s, W - Rt, H - B + 31, 'MHz', 'tick', 'end').setAttribute('fill', 'var(--muted)');
    tx(s, L - 6, T - 6, 'W', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    keys.forEach(k => {
      const hot = k === 'randn' || k === 'zeros';
      const col = k === 'randn' ? 'var(--c2)' : k === 'zeros' ? 'var(--c1)' : 'var(--ref)';
      const d = clocks.map((c, i) => (i ? 'L' : 'M') + X(c).toFixed(1) + ',' + Y(m[k][String(c)]).toFixed(1)).join(' ');
      el('path', {d, fill: 'none', stroke: col, 'stroke-width': hot ? 2.6 : 1.2, opacity: hot ? 1 : 0.65}, s);
      clocks.forEach(c => el('circle', {cx: X(c), cy: Y(m[k][String(c)]), r: hot ? 3.6 : 2.2, fill: col, opacity: hot ? 1 : 0.65}, s));
    });
    if (!narrow) {
      /* Three patterns sit within 4 W of each other at 800 MHz, so their right-hand labels used to print
         on top of one another. Place them in y order with a minimum gap, nudging down then back up. */
      const GAP = 15, top0 = T + 4, bot0 = H - B;
      const lab = keys.map(k => ({k, y: Y(m[k]['800']) + 4})).sort((a, b) => a.y - b.y);
      for (let i = 1; i < lab.length; i++) if (lab[i].y - lab[i - 1].y < GAP) lab[i].y = lab[i - 1].y + GAP;
      const over = lab[lab.length - 1].y - bot0;
      if (over > 0) for (let i = lab.length - 1; i >= 0; i--) {
        lab[i].y -= over;
        if (i && lab[i].y - lab[i - 1].y >= GAP) break;
      }
      if (lab[0].y < top0) lab[0].y = top0;
      lab.forEach(function (q) {
        const hot = q.k === 'randn' || q.k === 'zeros';
        const col = q.k === 'randn' ? 'var(--c2)' : q.k === 'zeros' ? 'var(--c1)' : 'var(--ref)';
        const yline = Y(m[q.k]['800']);
        if (Math.abs(q.y - 4 - yline) > 2)              // a nudged label gets a leader to its own point
          el('line', {x1: W - Rt + 2, x2: W - Rt + 7, y1: yline, y2: q.y - 4,
            stroke: 'var(--axis)', 'stroke-width': 1}, s);
        const t = tx(s, W - Rt + 9, q.y, (nice[q.k] || q.k) + '  ' + num(m[q.k]['800'], 1) + ' W', 'tick');
        t.setAttribute('fill', hot ? col : 'var(--ink-2)');
        if (hot) t.setAttribute('font-weight', '700');
      });
    }
    if (narrow) {                                       // label the two lines that carry the finding
      [['randn', -11, 'var(--c2)'], ['zeros', 17, 'var(--c1)']].forEach(function (q) {
        const t = tx(s, X(800) - 6, Y(m[q[0]]['800']) + q[1],
          nice[q[0]] + ' ' + num(m[q[0]]['800'], 1) + ' W', 'tick', 'end');
        t.setAttribute('fill', q[2]);
        t.setAttribute('font-weight', '700');
      });
      tx(s, L, T - 12, 'eight more patterns in grey', 'tick').setAttribute('fill', 'var(--muted)');
    }
  });

  /* 5b. the per-bit price list */
  responsive('bitchart', function (W) {
    const narrow = W < 620;
    const H = narrow ? 280 : 320, L = narrow ? 40 : 52, Rt = narrow ? 10 : 14, T = 20, B = 44;
    const ymax = Math.max(pb.A_max, pb.B_max) * 1.05;
    const X = i => L + i * (W - Rt - L) / 31, Y = v => H - B - v * (H - B - T) / ymax;
    const s = frame('bitchart', W, H,
      'Energy to flip one bit position, for all 32 positions of each operand. Both sides climb steeply from about 80 to 150 femtojoules at the bottom of the mantissa to 1,008 and 1,440 femtojoules at bit 22, then drop back for the exponent and sign bits.');
    for (let v = 0; v <= ymax; v += (narrow ? 500 : 250)) {
      el('line', {x1: L, x2: W - Rt, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 6, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    tx(s, L - 6, T - 4, 'fJ', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    [[0, 22, 'mantissa'], [23, 30, narrow ? 'exp' : 'exponent'], [31, 31, narrow ? 'sgn' : 'sign']].forEach(g => {
      const xa = X(g[0]) - 6, xb = X(g[1]) + 6;
      el('line', {x1: xa, x2: xb, y1: H - B + 20, y2: H - B + 20, stroke: 'var(--axis)'}, s);
      tx(s, Math.min((xa + xb) / 2, W - 14), H - B + 34, g[2], 'tick', 'middle').setAttribute('fill', 'var(--muted)');
    });
    (narrow ? [0, 8, 16, 22, 31] : [0, 8, 16, 22, 31]).forEach(i =>
      tx(s, X(i), H - B + 14, String(i), 'tick', 'middle').setAttribute('fill', 'var(--muted)'));
    [['B_fJ', 'var(--c1)', 'B side (multiplier)'], ['A_fJ', 'var(--c2)', 'A side (multiplicand)']].forEach(ser => {
      const o = pb[ser[0]];
      const d = Array.from({length: 32}, (_, i) => (i ? 'L' : 'M') + X(i).toFixed(1) + ',' + Y(o[String(i)]).toFixed(1)).join(' ');
      el('path', {d, fill: 'none', stroke: ser[1], 'stroke-width': narrow ? 1.8 : 2.2}, s);
      for (let i = 0; i < 32; i++) el('circle', {cx: X(i), cy: Y(o[String(i)]), r: narrow ? 1.9 : 2.8, fill: ser[1]}, s);
    });
    if (narrow) {
      /* The two peaks sit on top of each other at this width, so their callouts go in the empty corner
         above the low mantissa bits instead of next to the points. */
      tx(s, L + 4, T + 8, 'A bit 22: ' + num(pb.A_max, 0) + ' fJ', 'tick sm').setAttribute('fill', 'var(--c2)');
      tx(s, L + 4, T + 23, 'B bit 22: ' + num(pb.B_max, 0) + ' fJ', 'tick sm').setAttribute('fill', 'var(--c1)');
      tx(s, L + 4, T + 38, 'B bit 6: ' + num(pb.B_min, 0) + ' fJ', 'tick sm').setAttribute('fill', 'var(--muted)');
    } else {
      tx(s, X(22) - 10, Y(pb.A_fJ['22']) - 9, 'A bit 22: ' + num(pb.A_max, 0) + ' fJ', 'tick', 'end').setAttribute('fill', 'var(--c2)');
      tx(s, X(22) + 8, Y(pb.B_fJ['22']) + 2, 'B bit 22: ' + num(pb.B_max, 0) + ' fJ', 'tick', 'end').setAttribute('fill', 'var(--c1)');
      tx(s, X(5), Y(pb.B_min) - 12, 'B bit 6: ' + num(pb.B_min, 0) + ' fJ', 'tick').setAttribute('fill', 'var(--c1)');
    }
  });

  /* 5c. what the switching energy charges */
  responsive('splitchart', function (W) {
    const sh = ga.split_share, pj = ga.split_pJ;
    const keys = ['transistor gates', 'wire inside the cells', 'wire between the cells'];
    const narrow = W < 680;
    const ROW = narrow ? 54 : 40, H = (narrow ? 14 : 22) + keys.length * ROW + (narrow ? 4 : 10);
    const L = narrow ? 0 : 190, Rt = narrow ? 0 : 150;
    const s = frame('splitchart', W, H,
      'Of one random multiply-add’s switching energy, 20% charges transistor gates, 41% the wire inside the standard cells and 39% the wire between them.');
    const bw = W - L - Rt;
    keys.forEach((k, i) => {
      const key = k.replace(/ /g, '_');
      const col = i === 0 ? 'var(--c1)' : 'var(--ref)';
      const val = pct(sh[key], 1) + '  ·  ' + num(pj[key], 3) + ' pJ';
      if (narrow) {                                     // label over the bar, value at the right of it
        const y = 14 + i * ROW;
        tx(s, 0, y, k, 'tick').setAttribute('fill', 'var(--ink)');
        tx(s, W - 2, y, val, 'tick', 'end').setAttribute('fill', col);
        el('rect', {x: 0, y: y + 8, width: bw, height: 20, fill: 'var(--grid)', rx: 3}, s);
        el('rect', {x: 0, y: y + 8, width: Math.max(2, bw * sh[key]), height: 20, fill: col, rx: 3}, s);
        return;
      }
      const y = 22 + i * ROW;
      tx(s, L - 10, y + 15, k, 'tick', 'end').setAttribute('fill', 'var(--ink)');
      el('rect', {x: L, y, width: bw, height: 22, fill: 'var(--grid)', rx: 3}, s);
      el('rect', {x: L, y, width: Math.max(2, bw * sh[key]), height: 22, fill: col, rx: 3}, s);
      tx(s, L + bw + 10, y + 15, val, 'tick').setAttribute('fill', i === 0 ? 'var(--c1)' : 'var(--ink-2)');
    });
  });

  /* 5d. the waterfall */
  responsive('waterfall', function (W) {
    const wf = D.waterfall;
    const narrow = W < 700;
    /* On a phone the four bars and their labels have to fit the screen, and the stack's legend moves under
       the axis instead of into a right-hand gutter. */
    const T = 28, L = narrow ? 32 : 56, padR = narrow ? 4 : 10;
    const inner = narrow ? 8 : 14, gap = narrow ? 16 : 54;
    const B = narrow ? 128 : 56, H = narrow ? 340 : 300;
    const startx = L + (narrow ? 4 : 18);
    const barw = narrow
      ? Math.max(30, Math.floor((W - padR - startx - 2 * inner - (inner + gap)) / 4))
      : 86;
    const ymax = wf.board_pJ * 1.12;
    const Y = v => H - B - v * (H - B - T) / ymax;
    /* The label is built from the data, so a rebuilt ledger cannot leave a screen reader on the old one. */
    const s = frame('waterfall', W, H,
      'A random multiply-add costs ' + num(wf.board_pJ, 2) + ' picojoules at the board and '
      + num(wf.rail_pJ, 2) + ' reach the minion rail. The bottom-up count names '
      + wf.steps.map(st => num(st.pJ, 2) + ' ' + st.k).join(', ') + ', leaving '
      + num(wf.unaccounted_pJ, 2) + ' picojoules of the rail unaccounted'
      + (wf.unaccounted_band_pJ ? ' — ' + num(wf.unaccounted_band_pJ[0], 2) + ' to '
        + num(wf.unaccounted_band_pJ[1], 2) + ' over the transport reading' : '') + '.');
    for (let v = 0; v <= 6; v += 1) {
      el('line', {x1: L, x2: W - padR, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 6, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    tx(s, L - 6, T - 8, 'pJ', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    let x = startx;
    const col = (lab, v, c, sub) => {
      el('rect', {x, y: Y(v), width: barw, height: H - B - Y(v), fill: c, rx: 3}, s);
      tx(s, x + barw / 2, Y(v) - 7, num(v, 2), 'tick', 'middle').setAttribute('fill', 'var(--ink)');
      lab.split('|').forEach((ln, i) => tx(s, x + barw / 2, H - B + 16 + i * 13, ln,
        narrow ? 'tick sm' : 'tick', 'middle').setAttribute('fill', 'var(--ink-2)'));
      if (sub) tx(s, x + barw / 2, H - B + 16 + lab.split('|').length * 13, sub,
        narrow ? 'tick sm' : 'tick', 'middle').setAttribute('fill', 'var(--muted)');
      x += barw + inner;
    };
    col('at the|board', wf.board_pJ, 'var(--c2)', '(E38)');
    /* Q129 measured the rail instead of carrying it across, so the bar reads the waterfall's own figure. */
    col(narrow ? 'at the|rail' : 'at the|minion rail', wf.rail_pJ, 'var(--ref)',
      wf.version === 'q129' ? '(measured)' : '');
    x += gap;
    // stacked accounted bar
    const stackx = x, cols = ['var(--c1)', 'var(--c3)', 'var(--c4)', 'var(--c7)'];
    let acc = 0;
    wf.steps.forEach((st, i) => {
      el('rect', {x: stackx, y: Y(acc + st.pJ), width: barw, height: Y(acc) - Y(acc + st.pJ), fill: cols[i]}, s);
      acc += st.pJ;
    });
    el('rect', {x: stackx, y: Y(acc), width: barw, height: H - B - Y(acc), fill: 'none', stroke: 'var(--axis)'}, s);
    tx(s, stackx + barw / 2, Y(acc) - 7, num(acc, 2), 'tick', 'middle').setAttribute('fill', 'var(--ink)');
    ['counted|bottom-up'].forEach(l => l.split('|').forEach((ln, i) =>
      tx(s, stackx + barw / 2, H - B + 16 + i * 13, ln, narrow ? 'tick sm' : 'tick', 'middle')
        .setAttribute('fill', 'var(--ink-2)')));
    x = stackx + barw + inner;
    // the remainder, hatched
    const d = el('defs', {}, s), p = el('pattern', {id: 'wfh', width: 7, height: 7, patternUnits: 'userSpaceOnUse',
      patternTransform: 'rotate(45)'}, d);
    el('rect', {width: 7, height: 7, fill: 'var(--surface)'}, p);
    el('line', {x1: 0, y1: 0, x2: 0, y2: 7, stroke: 'var(--axis)', 'stroke-width': 2.5}, p);
    el('rect', {x, y: Y(wf.unaccounted_pJ), width: barw, height: H - B - Y(wf.unaccounted_pJ),
      fill: 'url(#wfh)', stroke: 'var(--axis)', rx: 3}, s);
    tx(s, x + barw / 2, Y(wf.unaccounted_pJ) - 7, num(wf.unaccounted_pJ, 2), 'tick', 'middle').setAttribute('fill', 'var(--ink)');
    ['not yet|accounted'].forEach(l => l.split('|').forEach((ln, i) =>
      tx(s, x + barw / 2, H - B + 16 + i * 13, ln, narrow ? 'tick sm' : 'tick', 'middle')
        .setAttribute('fill', 'var(--ink-2)')));
    /* Q128's remainder was against the board; Q129's is against the measured rail, because the
       board-to-rail step now has its own account. The data names its own denominator. */
    const den = wf.unaccounted_of_pJ || wf.board_pJ, denName = wf.unaccounted_of || 'the board';
    tx(s, Math.min(x + barw / 2, W - padR - 24), H - B + 42,
      pct(wf.unaccounted_pJ / den) + (narrow ? '' : ' of ' + denName),
      narrow ? 'tick sm' : 'tick', 'middle').setAttribute('fill', 'var(--muted)');
    // legend for the stack: a right-hand gutter when there is one, otherwise under the axis
    let ly = narrow ? H - B + 70 : T + 2;
    const lgx = narrow ? L - 24 : W - 232;
    wf.steps.forEach((st, i) => {
      el('rect', {x: lgx, y: ly - 9, width: 11, height: 11, fill: cols[i], rx: 2}, s);
      tx(s, lgx + 16, ly, (narrow && st.short ? st.short : st.k) + '  ' + num(st.pJ, 3) + ' pJ',
        narrow ? 'tick sm' : 'tick')
        .setAttribute('fill', 'var(--ink-2)');
      ly += 17;
    });
  });

  set('cl-cap', pct(1 - ga.capacitance_priced, 1));

  /* --------------------------------------------------- 6. back up the ladder */
  const cl = D.closure;
  $('predtiles').innerHTML = [
    tile(TIMES + num(cl.burst_pred, 3), 'predicted', 'Burst gap, zeros over random, from board power and the governor’s cap', 1),
    tile(TIMES + num(Math.min.apply(null, cl.burst_measured), 3) + '–' + num(Math.max.apply(null, cl.burst_measured), 3),
      'measured', 'The same gap, over four published ways of reading it'),
    tile(TIMES + num(cl.sustained_pred, 3), 'a clamp', 'Sustained gap: both patterns are pinned to an end of the clock range, so the ratio is 800/600 by construction'),
    tile(TIMES + num(cl.bottom_up_burst[0], 2) + '–' + num(cl.bottom_up_burst[1], 2), 'from one bit',
      'Starting from the price of a single flipped bit instead: a range, because the saturation law is not pinned')
  ].join('');
  set('pb-pred', TIMES + num(cl.burst_pred, 3));
  set('pb-meas', TIMES + num(Math.min.apply(null, cl.burst_measured), 3) + ' to ' + TIMES + num(Math.max.apply(null, cl.burst_measured), 3));
  set('pb-band', TIMES + num(cl.burst_band[0], 3) + ' to ' + TIMES + num(cl.burst_band[1], 3));
  set('ps-win', num(cl.clamp_width_W, 1) + ' W');
  set('pb-bu', TIMES + num(cl.bottom_up_burst[0], 2) + ' to ' + TIMES + num(cl.bottom_up_burst[1], 2));

  /* Which candidate caps are inside the clamp window, counted from the data. The page said "every" one of
     them until 2026-10-27; E64's own measured sustained randn point is above the window, and at that cap
     random would settle above the 600 MHz floor instead of on it. */
  (function caps() {
    const ins = Object.keys(cl.caps_inside || {}), out = Object.keys(cl.caps_outside || {});
    const nw = ['no', 'one', 'two', 'three', 'four', 'five', 'six'];
    set('ps-caps', nw[ins.length] || String(ins.length));
    set('ps-capn', nw[ins.length + out.length] || String(ins.length + out.length));
    if (!out.length) { const w = $('ps-exc-wrap'); if (w) w.style.display = 'none'; return; }
    const hi = cl.clamp_window_W[1];
    set('ps-exc', 'The fourth — ' + out.map(k => k + ', at ' + num(cl.caps_outside[k], 1) + NB + 'W')
      .join('; and ') + ' — is above the window, which ends at ' + num(hi, 1) + NB + 'W. At that cap ' +
      'random data would settle above the governor’s floor instead of on it, and the ratio would fall ' +
      'to about ' + TIMES + '1.30. So the clamp holds for ' + (nw[ins.length] || ins.length) + ' of the ' +
      (nw[ins.length + out.length] || (ins.length + out.length)) + ' caps, not all of them, and the ' +
      'ordinal claim is the part that survives either way. The reason that cap is on the list at all: ' +
      cl.cap_source_note);
  }());

  (function predtab() {
    const r = cl.results, mm = cl.measured_mhz || {}, mt = cl.measured_tflops || {};
    const nice = {zeros: 'zeros', ones: 'all ones', randn_M: 'random fp32'};
    /* measured_mhz / measured_tflops are keyed on the pattern, with random split burst/sustained */
    const meas = {
      zeros: {bm: mm.zeros, bt: (mt.zeros || [])[0], sm: mm.zeros, st: (mt.zeros || [])[1]},
      ones: {bm: null, bt: (mt.ones || [])[0], sm: mm.ones, st: (mt.ones || [])[1]},
      randn_M: {bm: mm.randn_burst, bt: (mt.randn || [])[0], sm: mm.randn_sustained, st: (mt.randn || [])[1]}
    };
    const MISS = 0.03;                                  // flag a prediction more than 3% off the measurement
    const cell = (p, m, unit, dp) => {
      const pv = num(p, dp) + (unit || ''), off = (p != null && m != null && m) ? Math.abs(p / m - 1) : 0;
      if (m == null) return '<td class="n">' + pv + '</td>';
      return '<td class="n">' + pv + '<br><span class="' + (off > MISS ? 'miss' : 'ms') + '">' +
        num(m, dp) + (unit || '') + '</span></td>';
    };
    const pats = Object.keys(nice).filter(k => r[k]);
    const metrics = [
      ['Burst clock', 'burst_mhz', 'bm', ' MHz', 0], ['Burst TFLOPS', 'burst_tflops', 'bt', '', 2],
      ['Sustained clock', 'sustained_mhz', 'sm', ' MHz', 0], ['Sustained TFLOPS', 'sustained_tflops', 'st', '', 2]
    ];
    const SUB = '<span class="sub">predicted · measured</span>';
    /* Five columns scroll off a phone, and the two that scroll off are the sustained pair -- the only place
       the chain actually misses. So the table transposes instead: patterns across, metrics down. */
    onWidth('predtab', function (w) {
      const narrow = w < 620;
      if (narrow) {
        const shrt = {zeros: 'zeros', ones: 'ones', randn_M: 'random'};
        $('predtab').innerHTML =
          '<thead><tr><th>' + SUB + '</th>' + pats.map(k => '<th class="n">' + shrt[k] + '</th>').join('') +
          '</tr></thead><tbody>' + metrics.map(mt =>
            '<tr><td>' + mt[0] + '</td>' +
            pats.map(k => cell(r[k][mt[1]], meas[k][mt[2]], mt[3], mt[4])).join('') + '</tr>').join('') +
          '</tbody>';
        return;
      }
      $('predtab').innerHTML =
        '<thead><tr><th>Pattern</th>' + metrics.map(mt => '<th class="n">' + mt[0] + '<br>' + SUB + '</th>').join('') +
        '</tr></thead><tbody>' + pats.map(k =>
          '<tr><td>' + nice[k] + '</td>' + metrics.map(mt => cell(r[k][mt[1]], meas[k][mt[2]], mt[3], mt[4])).join('') +
          '</tr>').join('') + '</tbody>';
    });
    const pmhz = r.ones && r.ones.sustained_mhz, mmhz = mm.ones;
    if (pmhz && mmhz) {
      set('pm-miss', 'All-ones operands sustained, in red above: the chain predicts ' + num(pmhz, 0) +
        NB + 'MHz and the card held ' + num(mmhz, 0) + NB + 'MHz, ' +
        pct(pmhz / mmhz - 1, 1) + ' high. It is the only quantitative prediction here that misses, and it ' +
        'is not the price list’s fault: E64’s own measured surface misses the same point further, ' +
        'at 791' + NB + 'MHz. What is missing is a temperature term in the static power B(f) — the ' +
        'sustained points run 6–8' + DEG + 'C hotter than the ladder runs that fixed it, and E65’s ' +
        '0.18' + NB + 'W/' + DEG + 'C leakage slope covers only about 1.4' + NB + 'W of the roughly 4' + NB +
        'W needed. Zeros and random both clamp to an end of the clock range, so all-ones is the one row ' +
        'where the model is free to be wrong.');
    }
  }());
  set('op-leak', num(pb.e66_leak_W_per_C, 3) + ' W/' + DEG + 'C against the registered estimator’s ' + num(pb.a1_leak_W_per_C, 3));

  /* ------------------------------------------- 6b. Q129, 28 October 2026
     Every span the 28 October pass added, filled from D.q129 so the prose cannot drift from the data block
     either. A page built from the 27 October data (data-2026-10-27-q128.json) has no q129 block, and set()
     on a missing element and this guard together leave that build exactly as it was. */
  if (D.q129) (function q129() {
    const q = D.q129, wf = D.waterfall, k = q.knob, t = q.temperature_term, st = q.saturation,
      v = q.voltage, lk = q.leak, hp = q.heat_path, at = q.atoms, kr = q.kernels;
    /* Several of these are quoted in more than one section, so each is filled by its data-q key on every
       occurrence rather than by id, which would reach only the first. */
    const set = (k, v) => { const ns = document.querySelectorAll('[data-q="' + k + '"]');
      for (let i = 0; i < ns.length; i++) ns[i].textContent = v; };
    const band = (a, dp, u) => num(a[0], dp) + '–' + num(a[1], dp) + (u || '');
    const rng = (a, dp, u) => num(Math.min.apply(null, a), dp) + '–' + num(Math.max.apply(null, a), dp) + (u || '');

    /* the footer: how much of this block the build re-checks against the lane directories' own JSON */
    set('sampled', num(q.sampled_against_lane_json.figures, 0) + ' figures across '
      + num(q.sampled_against_lane_json.directories, 0) + ' of those directories');
    /* named from the directory list itself, so the footer cannot claim a lane the build does not read */
    set('read-whole', q.sampled_against_lane_json.read_whole.map(function (d) {
      const m = /-e(\d+)-/.exec(d); return m ? 'E' + m[1] : d;
    }).join(', ').replace(/, ([^,]*)$/, ' and $1'));

    /* §1 and §4: the knob, and the temperature term */
    set('knob', num(k.cells_in_band[0], 0) + ' of ' + num(k.cells_in_band[1], 0) + ' cells inside their '
      + 'registered band, with an error of ' + num(k.rms_mhz, 2) + NB + 'MHz against a ' + num(k.bar_mhz, 0)
      + NB + 'MHz bar');
    set('knob-ones', num(k.ones_at_45W_mhz[0], 0) + ' and ' + num(k.ones_at_45W_mhz[1], 1) + NB + 'MHz '
      + '(predicted ' + num(k.ones_at_45W_pred_mhz, 1) + ') with ' + k.ones_at_45W_steps.join(' and ')
      + ' power-down steps, where the card’s own 65' + NB + 'W cap gives it none at all');
    set('knob-thr', num(k.sustained_thr65_mhz, 1) + NB + 'MHz with ' + num(k.thermal_steps_thr65, 0)
      + ' thermal steps at a 65' + DEG + 'C threshold against ' + num(k.sustained_thr70_mhz, 1)
      + NB + 'MHz and ' + num(k.thermal_steps_thr70, 0) + ' at 70' + DEG + 'C — at least '
      + num(k.threshold_sensitivity_mhz, 1) + NB + 'MHz');
    set('knob-flip', num(k.cause_flip_at_50W.mhz, 1) + NB + 'MHz with the limiter moving from '
      + num(k.thermal_steps_thr65, 0) + ' thermal and 0 power steps to '
      + num(k.cause_flip_at_50W.thermal_steps, 0) + ' and ' + num(k.cause_flip_at_50W.power_steps, 0));
    set('knob-randn', num(k.randn_mhz['65'], 0) + ' and ' + num(k.randn_mhz['55'], 1) + NB + 'MHz at 65 and '
      + '55' + NB + 'W (predicted ' + num(k.randn_pred_mhz['65'], 1) + ' and '
      + num(k.randn_pred_mhz['55'], 1) + '), and with all-ones on one side '
      + num(k.a_ones_b_randn_mhz['65'], 1) + ' → ' + num(k.a_ones_b_randn_mhz['55'], 1) + ' → '
      + num(k.a_ones_b_randn_mhz['45'], 1) + NB + 'MHz at 65 → 55 → 45' + NB + 'W (predicted '
      + num(k.a_ones_b_randn_pred_mhz['65'], 1) + ' → ' + num(k.a_ones_b_randn_pred_mhz['55'], 1) + ' → '
      + num(k.a_ones_b_randn_pred_mhz['45'], 1) + ')');
    set('temp', 'from ' + num(t.chain_pred_mhz, 0) + MINUS + num(t.all_ones_measured_mhz, 0) + ' = +'
      + num(t.chain_pred_mhz - t.all_ones_measured_mhz, 0) + NB + 'MHz to between +'
      + num(t.t1_miss_mhz[1], 1) + ' and ' + MINUS + num(-t.t1_miss_mhz[0], 1) + NB + 'MHz out of sample, '
      + 'and the nine-cell error from ' + num(t.e64_cap_rms_mhz, 1) + ' to '
      + band(t.nine_cell_rms_mhz, 1) + NB + 'MHz');

    /* §2 step 3: the rail, measured */
    set('rail', num(wf.rail_pJ, 2) + NB + 'pJ, band ' + band(wf.rail_band_pJ, 2) + NB + 'pJ ('
      + num(wf.rail_pJ / wf.board_pJ, 3) + ' of the board), against the ' + num(wf.v1.rail_pJ, 3)
      + NB + 'pJ this page carried from E60');
    set('rail-step', num(wf.board_pJ - wf.rail_pJ, 2) + NB + 'pJ, of which '
      + num(wf.regulators_pJ, 3) + NB + 'pJ is the regulators’ delivery loss and logic in step with the '
      + 'rails, at most 0.13' + NB + 'pJ the SRAM and NoC rails together, and '
      + num(wf.board_to_rail.fit_residual_pJ, 3) + NB + 'pJ the fit’s own residual');

    /* §2 step 5: the price list */
    set('sat', st.answer + ' — ' + num(st.layout_contrast_W, 3) + PM + num(st.layout_contrast_se_W, 3)
      + NB + 'W between two layouts at the same Hamming weight, ' + num(st.layout_contrast_SE, 1)
      + ' standard errors from the zero a “how many” law needs');
    set('sat-law', num(st.law_rms_W, 3) + NB + 'W (' + num(st.law_rms_frozen_W, 3)
      + ' with the curvature frozen before the run) against ' + num(st.best_in_h_alone_W, 3)
      + NB + 'W for the best possible law in Hamming weight alone and ' + num(st.pure_additivity_W, 3)
      + NB + 'W for pure additivity');
    set('carry', num(st.carry_over, 3) + PM + num(st.carry_over_se, 3) + ', replacing the choice between '
      + num(st.q128_choice[0], 2) + ' and ' + num(st.q128_choice[1], 2));
    set('volt', num(v.fJ_600, 2) + PM + num(v.fJ_600_se, 2) + NB + 'fJ at 600' + NB + 'MHz against '
      + num(v.fJ_800, 2) + PM + num(v.fJ_800_se, 2) + ' on the same card at 800');
    set('volt-n', 'between ' + num(v.exponent_rail[0], 2) + ' and ' + num(v.exponent_board[1], 2)
      + ', not pinned at 2 — the board family brackets it from above (' + band(v.exponent_board, 2)
      + ') and the rail family from below (' + band(v.exponent_rail, 2) + ')');
    set('volt-clock', num(v.clock_scaling_exponent, 3) + ', excluded by every reduction at '
      + num(v.clock_scaling_excluded_SE, 1) + ' standard errors or more');
    set('leak', num(lk.a3_58_62, 4) + PM + num(lk.a3_58_62_se, 4) + NB + 'W/' + DEG + 'C over 58–62'
      + DEG + 'C on aifoundry3 and ' + num(lk.a2_58_62, 4) + ' over the same band on aifoundry2 (sd '
      + num(lk.a2_58_62_sd, 4) + '), against ' + num(lk.a2_51_58, 4) + ' over 51–58' + DEG + 'C');
    set('leak-band', rng(lk.band_share_of_the_gap_pct, 1, '%'));
    set('leak-prices', 'group means ' + num(lk.group_shifts_pct[1], 1) + '% to '
      + num(lk.group_shifts_pct[0], 1) + '%, individual positions +' + num(lk.item_shifts_pct[0], 1)
      + '% to ' + num(lk.item_shifts_pct[1], 1) + '%, and ' + num(lk.verdicts_moved, 0) + ' of '
      + num(lk.verdicts_scored, 0) + ' registered verdicts moved');

    /* §3: the waterfall */
    set('wf-acc', band(wf.accounted_band_pJ, 2) + NB + 'pJ');
    set('wf-unacc', band(wf.unaccounted_vs_board_pJ, 2) + NB + 'pJ against the board and '
      + band(wf.unaccounted_band_pJ, 2) + ' against the rail');
    set('wf-unacc-band', band(wf.unaccounted_vs_board_band_pJ, 2) + NB + 'pJ');
    set('wf-closure-short', band(wf.closure_vs_board.map(x => 100 * x), 0, '%'));
    /* the bottom-up rows alone, which is the number 27 October's 34% can be compared with: the row above
       counts the measured board-to-rail step's regulator term, which is a named account but not a
       bottom-up one. */
    set('wf-closure-rail', band(wf.closure_vs_rail.map(x => 100 * x), 0, '%') + ' of it (band '
      + band(wf.closure_vs_rail_band.map(x => 100 * x), 0, '%') + ')');
    set('wf-closure-bottomup', band(wf.closure_vs_board_bottom_up.map(x => 100 * x), 0, '%'));
    set('wf-closure-bottomup-band', band(wf.closure_vs_board_bottom_up_band.map(x => 100 * x), 0, '%'));
    set('wf-closure-v1-bottomup', pct(wf.closure_v1_vs_board_bottom_up));
    set('wf-regulators', num(wf.regulators_pJ, 3) + NB + 'pJ');
    set('wf-regulators-band', band(wf.regulators_band_pJ, 3));
    set('wf-closure', band(wf.closure_vs_board.map(x => 100 * x), 0, '%') + ' of the board (band '
      + band(wf.closure_vs_board_band.map(x => 100 * x), 0, '%') + ') and '
      + band(wf.closure_vs_rail.map(x => 100 * x), 0, '%') + ' of the rail');
    /* The step is part measurement and part scaling, and the sentence says which is which: x1.331 is the
       MEASURED energy ratio of the switching term alone (+0.500 pJ), while the cells' internal energy is
       scaled by the signal-transition count (x1.680, +0.281 pJ) because the glitch run does not price
       internal energy. x1.331 x the zero-delay figure does not reach 2.705; the composite x1.406 does. */
    set('glitch', TIMES + num(wf.glitch_toggle_ratio, 3) + ' the toggles and ' + TIMES
      + num(wf.glitch_energy_ratio, 3) + ' the energy of its zero-delay twin on the switching term, worth +'
      + num(wf.glitch_split.switching_measured_pJ, 3) + NB + 'pJ measured — and +'
      + num(wf.glitch_moved_pJ, 3) + NB + 'pJ in all, because the cells’ internal energy is not measured '
      + 'glitched but scaled by the ' + TIMES + num(wf.glitch_split.internal_scale_applied, 3)
      + ' transition count (' + pct(wf.glitch_split.scaled_share_of_step) + ' of the step, so the factor '
      + 'the ledger applies is the composite ' + TIMES
      + num(wf.glitch_split.composite_ratio_applied, 3) + ')');
    set('recon', num(wf.v1.accounted_pJ, 4) + ' ' + MINUS + num(-wf.reconciliation.routed_wire_delta_pJ, 4)
      + ' + ' + num(wf.reconciliation.unpriced_capacitance_delta_pJ, 4) + ' = '
      + num(wf.reconciliation.walked_forward_pJ, 4) + NB + 'pJ against a measured '
      + num(wf.reconciliation.measured_zero_delay_pJ, 4) + ', '
      + num(Math.abs(wf.reconciliation.they_agree_to_pJ), 4) + NB + 'pJ apart');
    set('transport', num(wf.transport.low_pJ, 3) + ' to ' + num(wf.transport.high_pJ, 3) + NB + 'pJ');
    set('transport-zeros', pct(wf.transport.zero_operand_share_of_transport) + ' of it ('
      + num(wf.transport.zero_operand_floor_pJ, 3) + NB + 'pJ: '
      + num(wf.transport.zero_operand_clock_pJ, 3) + ' of clock nets and '
      + num(wf.transport.zero_operand_signal_pJ, 3) + ' of signal)');
    set('transport-bound', num(wf.transport.zero_operand_floor_pJ, 3) + NB + 'pJ where the whole board '
      + 'costs ' + num(wf.transport.card_zeros_bound_pJ, 2) + NB + 'pJ per multiply-add in the same '
      + 'stimulus — ' + num(wf.transport.zero_operand_floor_pJ / wf.transport.card_zeros_bound_pJ, 2)
      + TIMES + ' it');
    set('leakrow', num(wf.leakage.rail_at_each_slope_pJ.registered, 3) + ', '
      + num(wf.leakage.rail_at_each_slope_pJ.measured_within_run, 3) + ' and '
      + num(wf.leakage.rail_at_each_slope_pJ.e66_idle, 3) + NB + 'pJ over the three slopes, a spread of '
      + num(wf.leakage.spread_pJ, 3) + NB + 'pJ');

    /* §2 step 9: stop 9 */
    set('atoms', num(at.aJ_per_edge, 2) + NB + 'aJ per edge, ' + num(at.electrons, 0) + ' electrons, '
      + num(at.landauer_x, 0) + TIMES + ' Landauer at an 80' + DEG + 'C floor and '
      + num(at.landauer_x_at_58C, 0) + TIMES + ' at 58' + DEG + 'C');
    set('atoms-rungs', num(at.bare_fins_x, 0) + TIMES + ' for that pin’s six bare fins and '
      + num(at.min_inverter_x, 0) + TIMES + ' for the library’s real minimum inverter, INVxp33');
    set('atoms-heat', num(at.channel_share_pct, 1) + '% (band ' + band(at.channel_band_pct, 0, '%')
      + ' over the driver’s fin count and the metal layer) although ' + num(at.wire_share_of_capacitance_pct, 0)
      + '% of the net’s capacitance is wire');
    set('atoms-phonons', num(at.phonons_per_edge, 2) + ' optical phonons of '
      + num(at.phonon_meV, 1) + NB + 'meV per edge, and about '
      + (at.phonons_per_mac / 1e8).toFixed(1) + ' × 10⁸ per multiply-add (range '
      + (at.optical_phonon_range[0] / 1e8).toFixed(1) + '–'
      + (at.optical_phonon_range[1] / 1e8).toFixed(1) + ' over the rail share)');

    /* §5: the heat path and the kernels */
    set('heat', num(hp.pole_s, 1) + NB + 's pole [' + band(hp.pole_ci_s, 1) + '] plus '
      + num(hp.delay_s, 2) + NB + 's of extra lag [' + band(hp.delay_ci_s, 2) + '], group delay '
      + num(hp.group_delay_s, 2) + NB + 's; one pole alone is excluded at ΔAIC +'
      + num(hp.one_pole_alone_dAIC, 2) + ' and both pre-registered rivals are refuted by the phase at '
      + band(hp.rivals_refuted_SE, 2) + ' standard errors');
    set('heat-gain', num(hp.G0_mK_per_W, 1) + NB + 'mK/W [' + band(hp.G0_ci, 0) + '] from the fit, whose '
      + 'own 0.05' + NB + 'Hz value sits 2.7 line-standard-errors below the measured line, or about '
      + num(hp.line_implies_mK_per_W, 0) + NB + 'mK/W if that measured line is taken through the fitted '
      + num(hp.attenuation_at_0p05Hz, 4) + ' attenuation');
    set('kernels', 'E74 in ' + num(kr.e74_card_minutes, 1) + ', E75 in '
      + num(kr.e75_card_minutes, 1) + ' and E76 in ' + num(kr.e76_card_minutes, 1)
      + ' card-minutes, 41 in all on one card');
    set('e74', 'e_cell < ' + num(kr.e74_bound_fJ, 2) + NB + 'fJ per flipped cell bit at '
      + pct(kr.e74_bound_conf) + ' — a bound, because the board ladder does not resolve it: the point is '
      + num(kr.e74_point_fJ, 3) + NB + 'fJ with a 95% interval of [' + MINUS
      + num(-kr.e74_ci_fJ[0], 2) + ', +' + num(kr.e74_ci_fJ[1], 2) + '] that contains zero');
    /* the rail arm is reported beside the board one, never instead of it — that is how it was registered */
    set('e74-rail', num(kr.e74_rail_fJ, 3) + NB + 'fJ, 95% [' + band(kr.e74_rail_ci_fJ, 3) + ']');
    set('e74-mac', num(kr.e74_per_mac_pJ, 3) + NB + 'pJ per multiply-add at the point and at most '
      + num(kr.e74_per_mac_bound_pJ, 3) + ' at 95%, on ' + num(kr.e74_bits_per_mac, 0)
      + ' bits of register content — ' + pct(kr.e74_share_of_v1_remainder, 1) + ' of the 27 October '
      + 'remainder and at most ' + pct(kr.e74_share_of_v1_remainder_bound, 1));
    set('e74-mac-short', num(kr.e74_per_mac_pJ, 3) + NB + 'pJ per multiply-add, at most '
      + num(kr.e74_per_mac_bound_pJ, 3) + ' at 95%');
    /* E75: two of the four changed-bit prices are coefficients, two are bounds (non-monotone k-arms), and
       a bound is rounded away from zero so that rounding never understates a ceiling. An interval that
       spans zero is written with a comma, because an en dash between a negative and a positive misreads. */
    const ci = (a, dp) => a[0] < 0 ? num(a[0], dp) + ', ' + (a[1] >= 0 ? '+' : '') + num(a[1], dp)
      : band(a, dp);
    const up = (v, dp) => num(Math.ceil(v * Math.pow(10, dp)) / Math.pow(10, dp), dp);
    set('e75', kr.e75_levels.map(function (l) {
      const dp = Math.abs(l.e_flip_pJ) < 0.1 ? 4 : 3;
      return l.level + ' ' + (l.e_flip_resolved
        ? num(l.e_flip_pJ, dp) + NB + 'pJ [' + ci(l.e_flip_ci_pJ, dp) + ']'
        : '< ' + up(l.e_flip_ci_pJ[1], 2) + NB + 'pJ (not resolved)');
    }).join(', '));
    set('e75-ones', 'nothing at L1 (' + num(kr.e75_levels[0].e_one_pJ, 4) + NB + 'pJ, 95% ['
      + ci(kr.e75_levels[0].e_one_ci_pJ, 4) + ']) and ' + num(kr.e75_levels[3].e_one_pJ, 3)
      + NB + 'pJ at DRAM [' + ci(kr.e75_levels[3].e_one_ci_pJ, 3) + ']');
    set('e75-share', 'of the ' + num(kr.e75_dram_closure_pJ_per_line, 0) + NB
      + 'pJ per 64' + NB + 'B line the two counts explain, ' + pct(kr.e75_dram_ones_share)
      + ' is carried ones');
    set('e75-chord', num(kr.e75_levels[0].chord_pJ_per_B, 3) + NB + 'pJ/B at L1 against the catalogue’s '
      + num(kr.e75_catalogue_chord_pJ_per_B.l1, 2) + ', and ' + num(kr.e75_dram_chord_pJ_per_line_B, 1)
      + NB + 'pJ per line byte at DRAM against ' + num(kr.e75_catalogue_chord_pJ_per_B.dram, 0)
      + '; the two arms account for ' + num(kr.e75_levels[0].chord_accounted_pct, 1) + '% of the first and '
      + num(kr.e75_levels[3].chord_accounted_pct, 1) + '% of the second');
    set('e76', num(kr.e76_trapped, 0) + ' of ' + num(kr.e76_trapped, 0)
      + ' trap on silicon, each ending the hart’s kernel with 0 ops, with '
      + num(kr.e76_controls, 0) + ' of ' + num(kr.e76_controls, 0) + ' controls returning normally');
    /* the registered predictions that failed, and what did not run — the strings the data block carries,
       so a summary of this page cannot soften them */
    set('e74-failed', kr.e74_failed);
    set('e74-leverage', kr.e74_leverage);
    set('e75-failed', kr.e75_failed);
    set('e76-failed', kr.e76_failed);
    set('e76-did-not-run', kr.e76_did_not_run);
    set('e75-dram-pattern', 'the two designed arms explain '
      + num(kr.e75_levels[3].chord_accounted_pct, 1) + '% of DRAM’s zeros-to-random chord, 95% ['
      + band(kr.e75_dram_chord_share_ci_pct, 1, '%') + ']. ' + kr.e75_dram_newly_open);
    set('archive', q.archive.say);
    set('archive-when', q.archive.when);
    set('wf-unacc-v1', num(wf.v1.unaccounted_pJ, 2) + NB + 'pJ against the board and '
      + num(wf.v1.rail_pJ - wf.v1.accounted_pJ, 2) + ' against the rail');
    set('wf-unacc-board', band(wf.unaccounted_vs_board_pJ, 2) + NB + 'pJ');
  }());

  /* ------------------------------------------------------------- 7. sources */
  (function srctab() {
    const g = 'https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/reports/data/';
    const rows = [
      ['0–2', 'E64 · the power limit, not the temperature limit', g + '2026-10-23-e64-horace-power-limit/README.md'],
      ['3, 5', 'E60 · the bit-flip Hamming ladder', g + '2026-10-20-bitflip-ladder/README.md'],
      ['3', 'E63 · the camera half of the ladder', g + '2026-10-23-e63-camera-hamming-ladder/README.md'],
      ['4', 'E38 · operand sparsity on three cards', 'https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute'],
      ['5', 'E65 · 32 B-side bit positions, the flow-M flip, the hart ladder', g + '2026-10-26-e65-bit-prices-hart-ladder/README.md'],
      ['5', 'E67 · 32 A-side bit positions and the operand grid', g + '2026-10-27-e67-a-side-bit-prices/README.md'],
      ['5', 'E68 · the stage map, and the price as a band', g + '2026-10-27-e68-stage-map/README.md'],
      ['5', 'E66 · the overnight idle leakage measurement', g + '2026-10-27-e66-idle-long/README.md'],
      ['6', 'The toggle recount: what the bench’s 21,331 counted', g + '2026-10-26-toggle-recount/README.md'],
      ['6–7', 'The open netlist: the same RTL through Yosys and OpenROAD', g + '2026-10-26-open-netlist/README.md'],
      ['7', 'The cell energy table from an open 7 nm kit', g + '2026-10-26-asap7-cell-energies/README.md'],
      ['7–9', 'The transistor ledger: nets, gates, fins, electrons, the floor', g + '2026-10-27-transistor-ledger/README.md'],
      ['8', 'One switch, in SPICE on BSIM-CMG devices at 0.517 V', g + '2026-10-26-asap7-one-switch/README.md'],
      ['2–5', 'The load-to-watts model', g + '2026-10-26-load-model/README.md'],
      ['all', 'The chain closure: every rung joined and scored', g + '2026-10-27-chain-closure/README.md'],
      ['context', 'The multiply-add drawn as built, down to one gate’s transistors',
        'https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram#flow=m-tensorfma32'],
      ['context', 'Seven weeks of this work as a timeline', 'https://spacesheep.dev/@yaroslavvb/transistor-heat-timeline']
    ];
    $('srctab').querySelector('tbody').innerHTML = rows.map(r =>
      '<tr><td class="n">' + r[0] + '</td><td>' + r[1] + '</td><td><a href="' + r[2] + '">' +
      (r[2].indexOf('spacesheep') > 0 ? 'page' : 'data') + '</a></td></tr>').join('');
  }());

  /* ------------------------------------------- 8. the optional private boxes */
  /* A build that carries archive boxes says so above the fold as well as beside each box: the rule for a
     page holding vault material is that it is marked Confidential, deployed private and shared by name,
     and until 2026-10-27 the private build's first screen was indistinguishable from the public one's,
     so a screenshot or a print of it could not be told apart. */
  if (D.meta && D.meta.private) {
    const h1 = document.querySelector('h1[data-ss-id="title"]') || document.querySelector('main h1');
    if (h1) {
      if (D.vault && D.vault.title_suffix) h1.textContent = h1.textContent + D.vault.title_suffix;
      const b = document.createElement('p');
      b.className = 'cbanner';
      b.setAttribute('data-ss-id', 'confidential');
      b.setAttribute('data-ss-react', 'off');
      b.innerHTML = '<b>Confidential · ' + ((D.vault && D.vault.label) || 'NDA') + '</b><span>' +
        ((D.vault && D.vault.banner) ||
          'This build carries material from a private development archive. Do not forward, re-post or ' +
          'publish it; the public build of the same page is the one to share.') + '</span>';
      h1.parentNode.insertBefore(b, h1);
    }
  }
  if (D.vault && D.vault.boxes) {
    const v = D.vault;
    const slug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').split('-').slice(0, 6).join('-');
    const box = b => '<div class="vbox" data-ss-id="archive-' + slug(b.title) + '"><div class="vt">' + v.label +
      '</div><h4>' + b.title + '</h4><table><tbody>' +
      b.rows.map(r => '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td></tr>').join('') + '</tbody></table></div>';
    /* A box says where it goes: one of the chain-stop keys below, or, since 2026-10-28, any element id on
       this page (the ledger table, a later stop), so a build can place a box beside a section these five
       keys never foresaw. An unknown name falls back to the last stop, as it always did. */
    const LVAT = {permac: 4, perbit: 5, toggles: 6, transistor: 8, closure: 9};
    v.boxes.forEach(b => {
      const anchor = (LVAT[b.at] != null ? $('lv' + LVAT[b.at]) : $(b.at)) || $('lv9');
      const d = document.createElement('div');
      d.innerHTML = box(b);
      if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(d.firstChild, anchor.nextSibling);
      else $('vaultzone').appendChild(d.firstChild);
    });
    const note = document.createElement('div');
    note.className = 'vbox';
    note.setAttribute('data-ss-id', 'archive-what-these-boxes-are');
    note.innerHTML = '<div class="vt">' + v.label + '</div><h4>What these boxes are</h4><p>' + v.note + '</p>';
    $('vaultzone').appendChild(note);
  }
}());
