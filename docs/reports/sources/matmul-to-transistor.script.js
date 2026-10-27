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
  set('a-tog', num(tg.total_per_mac, 0));
  set('a-fins', num(tr.fins_per_signal_net, 1));
  set('a-tr', num(tr.E_aJ, 2) + ' aJ');
  set('a-el', num(tr.electrons, 0));
  set('a-land', sci(D.floor.rungs.transistor.over_Landauer_at_66C));

  /* ------------------------------------------------------------- 2. the ladder */
  (function ladder() {
    const R = D.floor.rungs;
    const rows = [
      ['mac_board', 1, '0\u20134'], ['mac_netlist', 0, '6\u20137'],
      ['bit_board', 1, '5'], ['bit_netlist', 0, '6'],
      ['clock_rise', 0, '7'], ['signal_rise', 0, '7'], ['gate_pin', 0, '7'],
      ['fin_in_cell', 0, '8'], ['transistor', 0, '8'], ['electron', 0, '9']
    ].map(r => [R[r[0]].label, R[r[0]].E_J, r[1], r[2]]);

    const land = D.floor.land66_J;
    const W = 900, rowH = 30, top = 26, H = top + rows.length * rowH + 42;
    const x0 = 300, x1 = W - 70;
    const lo = Math.log10(land) - 0.4, hi = Math.log10(rows[0][1]) + 0.4;
    const X = v => x0 + (Math.log10(v) - lo) * (x1 - x0) / (hi - lo);
    const s = el('svg', {viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'A logarithmic ladder of energy per event, from one electron across the rail at 83 zeptojoules up to one random floating-point multiply-add at the board at 5.8 picojoules, eleven orders of magnitude apart, with Landauer’s floor marked below all of them.'}, $('ladder'));
    for (let e = Math.ceil(lo); e <= Math.floor(hi); e++) {
      const x = X(Math.pow(10, e));
      el('line', {x1: x, x2: x, y1: top - 10, y2: top + rows.length * rowH - 8, stroke: 'var(--grid)'}, s);
      tx(s, x, H - 22, '10' + (e < 0 ? '−' : '') + String(Math.abs(e)).split('').map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+c]).join(''), 'tick', 'middle')
        .setAttribute('fill', 'var(--muted)');
    }
    tx(s, (x0 + x1) / 2, H - 5, 'joules per event', 'tick', 'middle').setAttribute('fill', 'var(--ink-2)');
    const lx = X(land);
    el('line', {x1: lx, x2: lx, y1: top - 14, y2: top + rows.length * rowH - 4, stroke: 'var(--ref)', 'stroke-dasharray': '4 3'}, s);
    tx(s, lx + 4, top - 17, 'Landauer, 66 ' + DEG + 'C', 'tick').setAttribute('fill', 'var(--ref)');
    rows.forEach((r, i) => {
      const y = top + i * rowH + 6;
      tx(s, x0 - 10, y + 4, r[0], 'tick', 'end').setAttribute('fill', 'var(--ink)');
      tx(s, 6, y + 4, 'step ' + r[3], 'tick').setAttribute('fill', 'var(--muted)');
      el('line', {x1: lx, x2: X(r[1]), y1: y, y2: y, stroke: 'var(--grid)'}, s);
      el('circle', {cx: X(r[1]), cy: y, r: 5.5, fill: r[2] ? 'var(--c1)' : 'var(--page)',
        stroke: r[2] ? 'var(--c1)' : 'var(--c2)', 'stroke-width': 2}, s);
      tx(s, X(r[1]) + 11, y + 4, eng(r[1]), 'tick').setAttribute('fill', 'var(--ink-2)');
    });
  }());

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
  (function boardchart() {
    const m = bd.measured, clocks = [600, 700, 800];
    const keys = Object.keys(m).sort((a, b) => m[a]['800'] - m[b]['800']);
    const nice = {randn: 'random fp32', zeros: 'zeros', ones: 'all ones', signs: 'sign bits only',
      uniform: 'uniform', mant: 'mantissa bits', pow2: 'powers of two', sparse75: '75% sparse',
      a_randn_b_ones: 'a random, b ones', a_ones_b_randn: 'a ones, b random'};
    const W = 900, H = 330, L = 56, Rt = 210, T = 16, B = 40;
    const vals = keys.map(k => clocks.map(c => m[k][String(c)])).flat();
    const ymax = Math.ceil(Math.max.apply(null, vals) / 10) * 10;
    const X = c => L + (c - 600) * (W - Rt - L) / 200, Y = v => H - B - v * (H - B - T) / ymax;
    const s = frame('boardchart', W, H,
      'Board power against clock for ten operand patterns. Zeros is the lowest line at every clock and random floating-point data the highest; the two diverge as the clock rises.');
    for (let v = 0; v <= ymax; v += 20) {
      el('line', {x1: L, x2: W - Rt, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 8, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    clocks.forEach(c => tx(s, X(c), H - B + 18, c + ' MHz', 'tick', 'middle').setAttribute('fill', 'var(--muted)'));
    tx(s, L - 8, T + 2, 'W', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    keys.forEach(k => {
      const hot = k === 'randn' || k === 'zeros';
      const col = k === 'randn' ? 'var(--c2)' : k === 'zeros' ? 'var(--c1)' : 'var(--ref)';
      const d = clocks.map((c, i) => (i ? 'L' : 'M') + X(c).toFixed(1) + ',' + Y(m[k][String(c)]).toFixed(1)).join(' ');
      el('path', {d, fill: 'none', stroke: col, 'stroke-width': hot ? 2.6 : 1.2, opacity: hot ? 1 : 0.65}, s);
      clocks.forEach(c => el('circle', {cx: X(c), cy: Y(m[k][String(c)]), r: hot ? 3.6 : 2.2, fill: col, opacity: hot ? 1 : 0.65}, s));
      const t = tx(s, W - Rt + 9, Y(m[k]['800']) + 4, (nice[k] || k) + '  ' + num(m[k]['800'], 1) + ' W', 'tick');
      t.setAttribute('fill', hot ? col : 'var(--ink-2)');
      if (hot) t.setAttribute('font-weight', '700');
    });
  }());

  /* 5b. the per-bit price list */
  (function bitchart() {
    const W = 900, H = 320, L = 52, Rt = 14, T = 20, B = 44;
    const ymax = Math.max(pb.A_max, pb.B_max) * 1.05;
    const X = i => L + i * (W - Rt - L) / 31, Y = v => H - B - v * (H - B - T) / ymax;
    const s = frame('bitchart', W, H,
      'Energy to flip one bit position, for all 32 positions of each operand. Both sides climb steeply from about 80 to 150 femtojoules at the bottom of the mantissa to 1,008 and 1,440 femtojoules at bit 22, then drop back for the exponent and sign bits.');
    for (let v = 0; v <= ymax; v += 250) {
      el('line', {x1: L, x2: W - Rt, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 8, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    tx(s, L - 8, T - 4, 'fJ', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    [[0, 22, 'mantissa'], [23, 30, 'exponent'], [31, 31, 'sign']].forEach(g => {
      const xa = X(g[0]) - 6, xb = X(g[1]) + 6;
      el('line', {x1: xa, x2: xb, y1: H - B + 20, y2: H - B + 20, stroke: 'var(--axis)'}, s);
      tx(s, (xa + xb) / 2, H - B + 34, g[2], 'tick', 'middle').setAttribute('fill', 'var(--muted)');
    });
    [0, 8, 16, 22, 31].forEach(i => tx(s, X(i), H - B + 14, String(i), 'tick', 'middle').setAttribute('fill', 'var(--muted)'));
    [['B_fJ', 'var(--c1)', 'B side (multiplier)'], ['A_fJ', 'var(--c2)', 'A side (multiplicand)']].forEach(ser => {
      const o = pb[ser[0]];
      const d = Array.from({length: 32}, (_, i) => (i ? 'L' : 'M') + X(i).toFixed(1) + ',' + Y(o[String(i)]).toFixed(1)).join(' ');
      el('path', {d, fill: 'none', stroke: ser[1], 'stroke-width': 2.2}, s);
      for (let i = 0; i < 32; i++) el('circle', {cx: X(i), cy: Y(o[String(i)]), r: 2.8, fill: ser[1]}, s);
    });
    tx(s, X(22) - 10, Y(pb.A_fJ['22']) - 9, 'A bit 22: ' + num(pb.A_max, 0) + ' fJ', 'tick', 'end').setAttribute('fill', 'var(--c2)');
    tx(s, X(22) + 8, Y(pb.B_fJ['22']) + 2, 'B bit 22: ' + num(pb.B_max, 0) + ' fJ', 'tick', 'end').setAttribute('fill', 'var(--c1)');
    tx(s, X(5), Y(pb.B_min) - 12, 'B bit 6: ' + num(pb.B_min, 0) + ' fJ', 'tick').setAttribute('fill', 'var(--c1)');
  }());

  /* 5c. what the switching energy charges */
  (function splitchart() {
    const sh = ga.split_share, pj = ga.split_pJ;
    const keys = ['transistor gates', 'wire inside the cells', 'wire between the cells'];
    const W = 900, H = 150, L = 190, Rt = 150;
    const s = frame('splitchart', W, H,
      'Of one random multiply-add’s switching energy, 20% charges transistor gates, 41% the wire inside the standard cells and 39% the wire between them.');
    const bw = W - L - Rt;
    keys.forEach((k, i) => {
      const y = 22 + i * 40;
      tx(s, L - 10, y + 15, k, 'tick', 'end').setAttribute('fill', 'var(--ink)');
      el('rect', {x: L, y, width: bw, height: 22, fill: 'var(--grid)', rx: 3}, s);
      el('rect', {x: L, y, width: Math.max(2, bw * sh[k.replace(/ /g, '_')]), height: 22,
        fill: i === 0 ? 'var(--c1)' : 'var(--ref)', rx: 3}, s);
      tx(s, L + bw + 10, y + 15, pct(sh[k.replace(/ /g, '_')], 1) + '  ·  ' + num(pj[k.replace(/ /g, '_')], 3) + ' pJ', 'tick')
        .setAttribute('fill', i === 0 ? 'var(--c1)' : 'var(--ink-2)');
    });
  }());

  /* 5d. the waterfall */
  (function waterfall() {
    const wf = D.waterfall;
    const W = 900, H = 300, T = 28, B = 56, L = 56, gap = 54;
    const ymax = wf.board_pJ * 1.12;
    const Y = v => H - B - v * (H - B - T) / ymax;
    const s = frame('waterfall', W, H,
      'A random multiply-add costs 5.78 picojoules at the board. The bottom-up count names 1.95 of them — 0.31 transistor gates, 0.62 wire inside the cells, 0.59 wire between the cells and 0.43 the cells’ own internal energy — leaving 3.84 picojoules, two thirds, unaccounted.');
    for (let v = 0; v <= 6; v += 1) {
      el('line', {x1: L, x2: W - 10, y1: Y(v), y2: Y(v), stroke: 'var(--grid)'}, s);
      tx(s, L - 8, Y(v) + 4, num(v, 0), 'tick', 'end').setAttribute('fill', 'var(--muted)');
    }
    tx(s, L - 8, T - 8, 'pJ', 'tick', 'end').setAttribute('fill', 'var(--ink-2)');
    const barw = 86;
    let x = L + 18;
    const col = (lab, v, c, sub) => {
      el('rect', {x, y: Y(v), width: barw, height: H - B - Y(v), fill: c, rx: 3}, s);
      tx(s, x + barw / 2, Y(v) - 7, num(v, 2), 'tick', 'middle').setAttribute('fill', 'var(--ink)');
      lab.split('|').forEach((ln, i) => tx(s, x + barw / 2, H - B + 16 + i * 13, ln, 'tick', 'middle').setAttribute('fill', 'var(--ink-2)'));
      if (sub) tx(s, x + barw / 2, H - B + 16 + lab.split('|').length * 13, sub, 'tick', 'middle').setAttribute('fill', 'var(--muted)');
      x += barw + 14;
    };
    col('at the|board', wf.board_pJ, 'var(--c2)', '(E38)');
    col('at the|minion rail', D.gates.rail_pJ, 'var(--ref)', '');
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
      tx(s, stackx + barw / 2, H - B + 16 + i * 13, ln, 'tick', 'middle').setAttribute('fill', 'var(--ink-2)')));
    x = stackx + barw + 14;
    // the remainder, hatched
    const d = el('defs', {}, s), p = el('pattern', {id: 'wfh', width: 7, height: 7, patternUnits: 'userSpaceOnUse',
      patternTransform: 'rotate(45)'}, d);
    el('rect', {width: 7, height: 7, fill: 'var(--surface)'}, p);
    el('line', {x1: 0, y1: 0, x2: 0, y2: 7, stroke: 'var(--axis)', 'stroke-width': 2.5}, p);
    el('rect', {x, y: Y(wf.unaccounted_pJ), width: barw, height: H - B - Y(wf.unaccounted_pJ),
      fill: 'url(#wfh)', stroke: 'var(--axis)', rx: 3}, s);
    tx(s, x + barw / 2, Y(wf.unaccounted_pJ) - 7, num(wf.unaccounted_pJ, 2), 'tick', 'middle').setAttribute('fill', 'var(--ink)');
    ['not yet|accounted'].forEach(l => l.split('|').forEach((ln, i) =>
      tx(s, x + barw / 2, H - B + 16 + i * 13, ln, 'tick', 'middle').setAttribute('fill', 'var(--ink-2)')));
    tx(s, x + barw / 2, H - B + 42, pct(wf.unaccounted_pJ / wf.board_pJ) + ' of the board', 'tick', 'middle')
      .setAttribute('fill', 'var(--muted)');
    // legend for the stack
    let ly = T + 2;
    wf.steps.forEach((st, i) => {
      el('rect', {x: W - 232, y: ly - 9, width: 11, height: 11, fill: cols[i], rx: 2}, s);
      tx(s, W - 216, ly, st.k + '  ' + num(st.pJ, 3) + ' pJ', 'tick').setAttribute('fill', 'var(--ink-2)');
      ly += 17;
    });
  }());

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
  (function predtab() {
    const r = cl.results, nice = {zeros: 'zeros', ones: 'all ones', randn_M: 'random fp32'};
    $('predtab').querySelector('tbody').innerHTML = Object.keys(nice).filter(k => r[k]).map(k =>
      '<tr><td>' + nice[k] + '</td><td class="n">' + num(r[k].burst_mhz, 0) + ' MHz</td><td class="n">' +
      num(r[k].burst_tflops, 2) + '</td><td class="n">' + num(r[k].sustained_mhz, 0) + ' MHz</td><td class="n">' +
      num(r[k].sustained_tflops, 2) + '</td></tr>').join('');
  }());
  set('op-leak', num(pb.e66_leak_W_per_C, 3) + ' W/' + DEG + 'C against the registered estimator’s ' + num(pb.a1_leak_W_per_C, 3));

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
  if (D.vault && D.vault.boxes) {
    const v = D.vault;
    const box = b => '<div class="vbox"><div class="vt">' + v.label + '</div><h4>' + b.title + '</h4><table><tbody>' +
      b.rows.map(r => '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td></tr>').join('') + '</tbody></table></div>';
    v.boxes.forEach(b => {
      const anchor = $('lv' + ({permac: 4, perbit: 5, toggles: 6, transistor: 8, closure: 9}[b.at] != null
        ? {permac: 4, perbit: 5, toggles: 6, transistor: 8, closure: 9}[b.at] : 9));
      const d = document.createElement('div');
      d.innerHTML = box(b);
      if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(d.firstChild, anchor.nextSibling);
      else $('vaultzone').appendChild(d.firstChild);
    });
    const note = document.createElement('div');
    note.className = 'vbox';
    note.innerHTML = '<div class="vt">' + v.label + '</div><h4>What these boxes are</h4><p>' + v.note + '</p>';
    $('vaultzone').appendChild(note);
  }
}());
