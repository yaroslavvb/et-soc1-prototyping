/* ================= ladder-inner.js: the circuits and the device, shared (1 October 2026) =================
   Split from chip-diagram.inside.js (30 September): the textbook circuits (the 4:2 compressor, the full adder, the
   XOR, the inverter and NAND, the flip-flop, the multiplexer), the FinFET at TSMC N7's pitches, the fin, the channel,
   the silicon crystal and the die in section, and the links from the memory drawings' transistors into them. */
/* the 4:2 compressor: two full adders, as the RTL's r42cmp computes it */
bnode('lib.cmp42', {draw: (L, ap) => {
  KT.frame(L, {title: 'A 4:2 compressor: two full adders', sub: 'four bits of a column and a carry in become a sum and two carries', col: CC.logic, tags: [['unknown', 'logic: Erbium RTL'], ['generic', 'the circuit: textbook']]});
  const f1 = ipart(L, ap, 'fa1', 120, 150, 240, 170, CC.logic, 'full adder 1', {node: 'lib.fa', center: true, ty: 92, kid: {id: 'lib.fa'}});
  ipart(L, ap, 'fa2', 520, 330, 240, 170, CC.logic, 'full adder 2', {node: 'lib.fa', center: true, ty: 92});
  ['x1', 'x2', 'x3'].forEach((t, i) => { const x = 170 + i * 70; KT.wire(L, [[x, 60], [x, 150]]); KT.netLab(L, x, 52, t, 'middle'); });
  KT.wire(L, [[700, 60], [700, 330]]); KT.netLab(L, 700, 52, 'x4', 'middle');
  KT.wire(L, [[900, 410], [760, 410]]); KT.netLab(L, 906, 416, '← cin');
  KT.wire(L, [[240, 320], [240, 380], [520, 380]]); KT.netLab(L, 380, 372, 's1', 'middle');
  KT.wire(L, [[120, 250], [-60, 250]]); KT.netLab(L, -66, 256, 'cout ←', 'end');
  KTT(L, 600, 120, 'cin comes from the 4:2 of the column on the right;', 't-sm'); KTT(L, 600, 142, 'cout goes to the column on the left', 't-sm');
  KT.wire(L, [[580, 500], [580, 580]]); KT.netLab(L, 580, 604, 'sum', 'middle');
  KT.wire(L, [[700, 500], [700, 580]]); KT.netLab(L, 700, 604, 'carry', 'middle');
  KTT(L, -150, 640, 'sum = x1 ⊕ x2 ⊕ x3 ⊕ x4 ⊕ cin; cout = majority(x1, x2, x3)', 't-mono', 'start', 'in.lib.cmp42.1');
  KTT(L, -150, 668, 'the RTL’s r42cmp writes the same in AND, OR and XOR (core-et’s Erbium branch; not confirmed to match the silicon)', 't-sm', 'start', 'in.lib.cmp42.1');
  ap.zs['lib.fa'] = {r: {x: 120, y: 150, w: 240, h: 170}, g: f1};
}, def: () => ({id: 'lib.fa'}), kids: () => [{id: 'lib.fa'}]});
/* the full adder in gates: two XORs for the sum, the majority for the carry */
function xorSym(parent, x, y, o) {
  const s0 = KT.andSym(parent, x, y, Object.assign({or: true}, o || {}));
  E('path', {class: 'w', d: `M${x - 9},${y - (o && o.h || 44) / 2} Q${x + (o && o.w || 44) * 0.25 - 9},${y} ${x - 9},${y + (o && o.h || 44) / 2}`}, parent);
  return {g: s0.g, a: {x: x - 9, y: y - (o && o.h || 44) / 4}, b: {x: x - 9, y: y + (o && o.h || 44) / 4}, out: s0.out, shape: s0.shape};
}
bnode('lib.fa', {draw: (L, ap) => {
  KT.frame(L, {title: 'A full adder, in gates', sub: `three bits in, a sum and a carry out; built of transistors, about ${on('fa_tr')} as a static mirror adder`, subf: onf('fa_tr'), col: CC.logic, tags: [['generic', 'textbook']]});
  const gx = ipart(L, ap, 'xor1', 160, 60, 110, 100, CC.logic, '', {node: 'lib.xor', kid: {id: 'lib.xor'}, tr: 'jump', fo: 0.06, label: 'XOR gate 1'});
  const x1 = xorSym(gx, 190, 110, {w: 60, h: 60});
  const g2 = KT.comp(L, 'xor2', {}, 'XOR gate 2'); g2._info = {title: 'XOR gate', lead: sc('lib.xor').blurb, facts: sc('lib.xor').facts}; g2._kid = {id: 'lib.xor'};
  const x2 = xorSym(g2, 450, 140, {w: 60, h: 60}); g2._box = {x: 430, y: 100, w: 100, h: 80};
  const ga = KT.comp(L, 'majority', {}, 'The carry: the majority of the three bits');
  ga._info = {title: 'The carry', lead: 'The carry is 1 when at least two of the three bits are: two AND gates and an OR.', facts: sc('lib.fa').facts};
  const a1 = KT.andSym(ga, 190, 330, {w: 56, h: 56}), a2 = KT.andSym(ga, 450, 400, {w: 56, h: 56}), o1 = KT.andSym(ga, 680, 370, {w: 60, h: 60, or: true});
  ga._box = {x: 170, y: 290, w: 580, h: 150};
  // the wires: a, b, cin from the left
  const ys = {a: 80, b: 140, c: 210};
  KT.netLab(L, -90, ys.a + 6, 'a', 'end'); KT.netLab(L, -90, ys.b + 6, 'b', 'end'); KT.netLab(L, -90, ys.c + 6, 'cin', 'end');
  KT.wire(L, [[-80, ys.a], [x1.a.x, ys.a + 15]]); KT.wire(L, [[-80, ys.b], [x1.b.x, x1.b.y]]);
  KT.wire(L, [[0, ys.a], [0, 316], [a1.a.x, a1.a.y]]); KT.wire(L, [[40, ys.b], [40, 344], [a1.b.x, a1.b.y]]); KT.jn(L, 0, ys.a); KT.jn(L, 40, ys.b);
  KT.wire(L, [[x1.out.x, x1.out.y], [380, x1.out.y], [380, x2.a.y], [x2.a.x, x2.a.y]]);
  KT.wire(L, [[-80, ys.c], [300, ys.c], [300, x2.b.y], [x2.b.x, x2.b.y]]);
  KT.wire(L, [[380, x2.a.y], [380, 386], [a2.a.x, a2.a.y]]); KT.jn(L, 380, x2.a.y);
  KT.wire(L, [[300, ys.c], [300, 414], [a2.b.x, a2.b.y]]); KT.jn(L, 300, ys.c);
  KT.wire(L, [[a1.out.x, a1.out.y], [620, a1.out.y], [620, 355], [o1.a.x, o1.a.y]]); KT.wire(L, [[a2.out.x, a2.out.y], [620, a2.out.y], [620, 385], [o1.b.x, o1.b.y]]);
  KT.wire(L, [[x2.out.x, x2.out.y], [880, x2.out.y]]); KT.netLab(L, 888, x2.out.y + 6, 'sum');
  KT.wire(L, [[o1.out.x, o1.out.y], [880, o1.out.y]]); KT.netLab(L, 888, o1.out.y + 6, 'carry');
  // the truth table
  const tb = KT.comp(L, 'fatable', {}, 'The full adder’s truth table');
  tb._info = {title: 'The truth table', lead: 'Every combination of the three input bits and what the adder gives: the sum is 1 when an odd number of inputs are 1, the carry when two or more are.', facts: sc('lib.fa').facts};
  const tx = 760, ty = 470;
  KTT(tb, tx, ty, 'a b cin | sum carry', 't-mono');
  for (let i = 0; i < 8; i++) { const a = i >> 2 & 1, b = i >> 1 & 1, c = i & 1, s0 = a ^ b ^ c, cy = (a + b + c) >= 2 ? 1 : 0; KTT(tb, tx, ty + 24 + i * 22, `${a} ${b}  ${c}  |  ${s0}     ${cy}`, 't-mono'); }
  tb._box = {x: tx - 8, y: ty - 20, w: 220, h: 210};
  ap.zs['lib.xor'] = {r: {x: 160, y: 60, w: 110, h: 100}, g: gx, tr: 'jump'};
}, def: () => ({id: 'lib.xor'}), kids: () => [{id: 'lib.xor'}]});
/* the XOR in transistors: a static CMOS gate (the complementary networks and two inverters, 12 in all) */
bnode('lib.xor', {draw: (L, ap) => {
  KT.frame(L, {title: 'An XOR gate, in transistors', sub: `out = A ⊕ B: static CMOS, ${on('xor_tr')} as gates of this kind are built (here 12)`, subf: onf('xor_tr'), col: CC.logic, tags: [['generic', 'textbook']]});
  const xl = 300, xr = 470;
  KT.rail(L, 220, 560, 20, 'VDD');
  const p1 = KT.mosV(L, xl, 90, {p: true, lead: 30}), p2 = KT.mosV(L, xr, 90, {p: true, lead: 30, flip: true});
  const p3 = KT.mosV(L, xl, 210, {p: true, lead: 30}), p4 = KT.mosV(L, xr, 210, {p: true, lead: 30, flip: true});
  const n1 = KT.mosV(L, xl, 350, {lead: 30}), n2 = KT.mosV(L, xl, 450, {lead: 30}), n3 = KT.mosV(L, xr, 350, {lead: 30, flip: true}), n4 = KT.mosV(L, xr, 450, {lead: 30, flip: true});
  [p1, p2].forEach(t => KT.wire(L, [[t.top.x, t.top.y], [t.top.x, 20]]));
  KT.wire(L, [[p1.bot.x, p1.bot.y], [p1.bot.x, 150], [p2.bot.x, 150], [p2.bot.x, p2.bot.y]]); KT.wire(L, [[(xl + xr) / 2, 150], [p3.top.x, 150], [p3.top.x, p3.top.y]]); KT.wire(L, [[p4.top.x, p4.top.y], [p4.top.x, 150]]);
  KT.jn(L, xl, 150); KT.jn(L, xr, 150); KT.netLab(L, (xl + xr) / 2, 144, 'X', 'middle');
  KT.wire(L, [[p3.bot.x, p3.bot.y], [p3.bot.x, 280], [p4.bot.x, 280], [p4.bot.x, p4.bot.y]]);
  KT.wire(L, [[xl, 280], [n1.top.x, n1.top.y]]); KT.wire(L, [[xr, 280], [n3.top.x, n3.top.y]]); KT.jn(L, xl, 280); KT.jn(L, xr, 280);
  KT.wire(L, [[xr, 280], [700, 280]]); KT.netLab(L, 708, 286, 'OUT = A ⊕ B');
  KT.wire(L, [[n1.bot.x, n1.bot.y], [n2.top.x, n2.top.y]]); KT.wire(L, [[n3.bot.x, n3.bot.y], [n4.top.x, n4.top.y]]);
  KT.wire(L, [[n2.bot.x, n2.bot.y], [n2.bot.x, 520]]); KT.wire(L, [[n4.bot.x, n4.bot.y], [n4.bot.x, 520]]); KT.rail(L, 220, 560, 520, 'GND');
  [[p1, 'A'], [p2, 'B'], [p3, "A'"], [p4, "B'"], [n1, 'A'], [n2, 'B'], [n3, "A'"], [n4, "B'"]].forEach(([t, lab]) => KT.netLab(L, t.gate.x + (t.gate.x < t.x ? -6 : 6), t.gate.y + 6, lab, t.gate.x < t.x ? 'end' : 'start'));
  const gu = KT.comp(L, 'pun', {}, 'The pull-up network: PMOS transistors that connect OUT to VDD when A and B differ');
  gu._info = {title: 'The pull-up network', lead: 'P-type transistors conduct when their gate is 0. Two parallel pairs in series connect the output to VDD exactly when A and B differ: then OUT is 1.', facts: sc('lib.xor').facts};
  S(E('rect', {x: 220, y: 50, width: 340, height: 200, rx: 10}, gu), {fill: 'var(--c1)', fillOpacity: 0.04, stroke: 'var(--c1)', strokeWidth: 1.25, strokeDasharray: '2 5'}); gu._box = {x: 220, y: 50, w: 340, h: 200};
  const gd = KT.comp(L, 'pdn', {}, 'The pull-down network: NMOS transistors that connect OUT to ground when A and B agree');
  gd._info = {title: 'The pull-down network', lead: 'N-type transistors conduct when their gate is 1. Two series pairs in parallel connect the output to ground when A and B agree: then OUT is 0.', facts: sc('lib.xor').facts};
  S(E('rect', {x: 220, y: 300, width: 340, height: 200, rx: 10}, gd), {fill: 'var(--c3)', fillOpacity: 0.04, stroke: 'var(--c3)', strokeWidth: 1.25, strokeDasharray: '2 5'}); gd._box = {x: 220, y: 300, w: 340, h: 200};
  // one transistor ringed: the device below it
  ipart(L, ap, 'onefet', xl - 22, 314, 44, 72, 'var(--c2)', '', {node: 'lib.finfet', kid: {id: 'lib.finfet'}, tr: 'jump', fo: 0.1, label: 'One transistor'});
  // the inverters that make A' and B'
  const gi = KT.comp(L, 'xinv', {}, 'Two inverters make A’ and B’: four more transistors');
  gi._info = {title: 'The input inverters', lead: sc('lib.inverter').blurb, facts: sc('lib.inverter').facts}; gi._kid = {id: 'lib.inverter'};
  const i1 = KT.invSym(gi, -60, 120, {s: 26}), i2 = KT.invSym(gi, -60, 220, {s: 26});
  KT.netLab(gi, i1.in.x - 8, 126, 'A', 'end'); KT.netLab(gi, i1.out.x + 8, 126, "A'"); KT.netLab(gi, i2.in.x - 8, 226, 'B', 'end'); KT.netLab(gi, i2.out.x + 8, 226, "B'");
  gi._box = {x: -110, y: 90, w: 130, h: 160};
  ap.zs['lib.inverter'] = {r: gi._box, g: gi};
  const tb = KT.comp(L, 'xtable', {}, 'The XOR’s truth table'); tb._info = {title: 'XOR', lead: sc('lib.xor').blurb, facts: sc('lib.xor').facts};
  KTT(tb, 760, 380, 'A B | OUT', 't-mono'); [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]].forEach((r, i) => KTT(tb, 760, 404 + i * 22, `${r[0]} ${r[1]} |  ${r[2]}`, 't-mono'));
  tb._box = {x: 752, y: 360, w: 130, h: 136};
}, def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}, {id: 'lib.inverter'}]});
/* the inverter and the NAND: the simplest gates */
function gateScene(L, ap, which) {
  const nand = which === 'nand';
  KT.frame(L, {title: nand ? 'A NAND gate, in transistors' : 'An inverter, in transistors', sub: nand ? `out = not (A and B): ${on('nand_tr')}` : 'out = not IN: one PMOS, one NMOS', subf: nand ? onf('nand_tr') : null, col: CC.logic, tags: [['generic', 'textbook']]});
  KT.rail(L, 160, 640, 40, 'VDD'); KT.rail(L, 160, 640, 560, 'GND');
  let nTop;
  if (!nand) {
    const p = KT.mosV(L, 400, 140, {p: true, lead: 40}), n = KT.mosV(L, 400, 440, {lead: 40});
    KT.wire(L, [[400, p.top.y], [400, 40]]); KT.wire(L, [[400, p.bot.y], [400, n.top.y]]); KT.wire(L, [[400, n.bot.y], [400, 560]]);
    KT.wire(L, [[p.gate.x, p.gate.y], [p.gate.x, n.gate.y]]); KT.wire(L, [[p.gate.x, 290], [180, 290]]); KT.jn(L, p.gate.x, 290); KT.netLab(L, 172, 296, 'IN', 'end');
    KT.wire(L, [[400, 290], [620, 290]]); KT.jn(L, 400, 290); KT.netLab(L, 628, 296, 'OUT');
    nTop = n;
  } else {
    const p1 = KT.mosV(L, 300, 140, {p: true, lead: 40}), p2 = KT.mosV(L, 500, 140, {p: true, lead: 40, flip: true});
    const n1 = KT.mosV(L, 400, 360, {lead: 40}), n2 = KT.mosV(L, 400, 470, {lead: 40});
    [p1, p2].forEach(t => KT.wire(L, [[t.x, t.top.y], [t.x, 40]]));
    KT.wire(L, [[300, p1.bot.y], [300, 250], [500, 250], [500, p2.bot.y]]); KT.wire(L, [[400, 250], [400, n1.top.y]]); KT.jn(L, 400, 250);
    KT.wire(L, [[400, n1.bot.y], [400, n2.top.y]]); KT.wire(L, [[400, n2.bot.y], [400, 560]]);
    KT.wire(L, [[500, 250], [620, 250]]); KT.netLab(L, 628, 256, 'OUT');
    KT.netLab(L, p1.gate.x - 6, p1.gate.y + 6, 'A', 'end'); KT.netLab(L, p2.gate.x + 6, p2.gate.y + 6, 'B'); KT.netLab(L, n1.gate.x - 6, n1.gate.y + 6, 'A', 'end'); KT.netLab(L, n2.gate.x - 6, n2.gate.y + 6, 'B', 'end');
    nTop = n1;
  }
  ipart(L, ap, 'onefet', nTop.x - 22, nTop.y - 36, 44, 72, 'var(--c2)', '', {node: 'lib.finfet', kid: {id: 'lib.finfet'}, tr: 'jump', fo: 0.1, label: 'One transistor'});
  const tb = KT.comp(L, 'gtable', {}, 'The truth table'); tb._info = {title: 'The truth table', lead: sc(nand ? 'lib.nand2' : 'lib.inverter').blurb, facts: sc(nand ? 'lib.nand2' : 'lib.inverter').facts};
  if (nand) { KTT(tb, 760, 300, 'A B | OUT', 't-mono'); [[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 0]].forEach((r, i) => KTT(tb, 760, 324 + i * 22, `${r[0]} ${r[1]} |  ${r[2]}`, 't-mono')); }
  else { KTT(tb, 760, 300, 'IN | OUT', 't-mono'); KTT(tb, 760, 324, ' 0 |  1', 't-mono'); KTT(tb, 760, 346, ' 1 |  0', 't-mono'); }
  tb._box = {x: 752, y: 280, w: 130, h: 136};
  KTT(L, -150, 640, nand ? 'P-type transistors conduct when their gate is 0, N-type when it is 1: one network always pulls OUT up or down' : 'a 0 in turns the PMOS on and the NMOS off: OUT is pulled to VDD; a 1 does the opposite', 't-sm');
}
bnode('lib.inverter', {draw: (L, ap) => gateScene(L, ap, 'inv'), def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});
bnode('lib.nand2', {draw: (L, ap) => gateScene(L, ap, 'nand'), def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});
/* the flip-flop: two latches on opposite phases of the clock */
bnode('lib.flipflop', {draw: (L, ap) => {
  KT.frame(L, {title: 'A flip-flop: two latches back to back', sub: 'the master follows D while the clock is low, the slave while it is high: the output changes only at the rising edge', col: CC.logic, tags: [['generic', 'textbook']]});
  ipart(L, ap, 'master', 120, 160, 260, 200, CC.store, 'master latch', {node: 'lib.latch', kid: {id: 'lib.latch'}, center: true, ty: 92, sub: ['transparent', 'while CK = 0']});
  ipart(L, ap, 'slave', 540, 160, 260, 200, CC.store, 'slave latch', {node: 'lib.latch', center: true, ty: 92, sub: ['transparent', 'while CK = 1']});
  KT.wire(L, [[-40, 260], [120, 260]]); KT.netLab(L, -48, 266, 'D', 'end');
  KT.wire(L, [[380, 260], [540, 260]]); KT.wire(L, [[800, 260], [960, 260]]); KT.netLab(L, 968, 266, 'Q');
  KT.wire(L, [[-40, 460], [660, 460], [660, 360]]); KT.wire(L, [[250, 460], [250, 400]]); KT.netLab(L, -48, 466, 'CK', 'end');
  KT.invSym(L, 250, 380, {s: 16}); KT.jn(L, 250, 460);
  KTT(L, -150, 640, 'pipelines are rows of these between blocks of logic: each takes its input at the clock’s edge', 't-sm');
}, def: () => ({id: 'lib.latch'}), kids: () => [{id: 'lib.latch'}]});
/* the FinFET from above, at TSMC N7's published pitches (this chip's own layout is not published) */
bnode('lib.finfet', {draw: (L, ap) => {
  KT.frame(L, {title: 'FinFET transistors from above, at N7’s pitches', sub: `fins ${on('fin_p')} apart, gates ${on('gate_p')} apart (TSMC N7, published); this chip’s own cells are not published`, subf: onf('gate_p'),
    col: CC.logic, tags: [['documented', 'pitches: outside source'], ['generic', 'the pattern']]});
  const k = 2.9, fp = 30 * k, gp = 57 * k, lg = 20 * k, fw = 6.5 * k, x0 = -110, y0 = 60, nf = 6, ng = 7, W = gp * (ng - 0.4), Hh = fp * (nf - 1) + 40;
  const gf = KT.comp(L, 'fins', {}, 'The fins: walls of silicon the current runs along');
  gf._info = {title: 'The fins', lead: sc('lib.fin').blurb, facts: sc('lib.fin').facts};
  for (let i = 0; i < nf; i++) S(E('rect', {x: x0, y: y0 + 20 + i * fp - fw / 2, width: W, height: fw}, gf), {fill: 'var(--c3)', fillOpacity: 0.55});
  gf._box = {x: x0, y: y0, w: W, h: Hh};
  const gc = KT.comp(L, 'contacts', {}, 'Source and drain contacts');
  gc._info = {title: 'Source and drain', lead: 'Between the gates, metal contacts land on the fins: one side is the source, the other the drain. Current flows along the fins between them when the gate is on.', facts: sc('lib.finfet').facts};
  for (let j = 0; j < ng - 1; j++) S(E('rect', {x: x0 + gp * j + lg / 2 + 10, y: y0 + 4, width: gp - lg - 20, height: Hh - 8, rx: 4}, gc), {fill: 'var(--c5)', fillOpacity: 0.22, stroke: 'var(--c5)', strokeWidth: 1.2});
  gc._box = {x: x0, y: y0, w: W, h: Hh};
  const gg = KT.comp(L, 'gates', {}, 'The gates: lines of metal over the fins');
  gg._info = {title: 'The gates', lead: sc('lib.gate').blurb, facts: sc('lib.gate').facts};
  for (let j = 0; j < ng; j++) S(E('rect', {x: x0 + gp * j - lg / 2, y: y0 - 10, width: lg, height: Hh + 20, rx: 3}, gg), {fill: 'var(--c1)', fillOpacity: 0.45, stroke: 'var(--c1)', strokeWidth: 1.5});
  gg._box = {x: x0, y: y0 - 10, w: W, h: Hh + 20};
  // one two-fin transistor: gate 3 over fins 2 and 3
  const gx = x0 + gp * 3, dev = {x: gx - gp / 2 - 6, y: y0 + 20 + 2 * fp - fp / 2, w: gp + 12, h: fp * 2};
  ipart(L, ap, 'onedev', dev.x, dev.y, dev.w, dev.h, 'var(--c2)', '', {node: 'lib.fin', kid: {id: 'lib.fin'}, tr: 'jump', fo: 0.08, label: 'One transistor: a gate over two fins'});
  KTT(L, dev.x + dev.w + 8, dev.y - 8, 'one transistor: a gate over two fins', 't-smb halo');
  // dimension marks
  const dy = y0 + Hh + 40;
  KT.wire(L, [[x0 + gp, dy], [x0 + 2 * gp, dy]]); KTT(L, x0 + 1.5 * gp, dy + 26, `gate pitch ${on('gate_p')}`, 't-sm', 'middle', onf('gate_p'));
  KT.wire(L, [[x0 + W + 16, y0 + 20], [x0 + W + 16, y0 + 20 + fp]]); KTT(L, x0 + W + 24, y0 + 20 + fp / 2 + 6, `fin pitch ${on('fin_p')}`, 't-sm', 'start', onf('fin_p'));
  KT.wire(L, [[-110, 650], [-110 + 100 * k, 650]], 'bus'); KTT(L, -110 + 100 * k + 12, 656, '100 nm', 't-sm');
  KTT(L, 300, 656, 'gates blue, fins green, contacts between the gates', 't-sm');
}, def: () => ({id: 'lib.fin'}), kids: () => [{id: 'lib.fin'}]});
/* the fins in section, the gate wrapped over three sides */
bnode('lib.fin', {draw: (L, ap) => {
  KT.frame(L, {title: 'Fins in section, under a gate', sub: `each fin about ${on('fin_w')} wide and ${on('fin_h')} tall (inferred from 10 nm-class sections); ${on('fin_p')} apart`, subf: `${onf('fin_w')} ${onf('fin_p')}`,
    col: CC.logic, tags: [['unknown', 'fin shape: inferred'], ['documented', 'pitch: outside source']]});
  const k = 7.6, fp = 30 * k, fw = 6.5 * k, fh = 47 * k, base = 560, sti = 40, cx0 = 460 - fp;
  const gs = KT.comp(L, 'substrate', {}, 'The silicon wafer, and the oxide between the fins');
  gs._info = {title: 'The wafer and the trench oxide', lead: 'The fins stand up from the silicon wafer; between them, an insulating oxide (shallow trench isolation) keeps neighbouring transistors apart.', facts: sc('lib.fin').facts};
  S(E('rect', {x: -150, y: base, width: 1220, height: 110}, gs), {fill: 'var(--c3)', fillOpacity: 0.25, stroke: 'var(--c3)', strokeWidth: 1.5});
  S(E('rect', {x: -150, y: base - sti * k / 7.6 * 1, width: 1220, height: sti}, gs), {fill: 'var(--ink-2)', fillOpacity: 0.16});
  KTT(gs, -140, base + 60, 'silicon wafer', 't-sm'); KTT(gs, -140, base - 10, 'oxide (trench isolation)', 't-sm');
  gs._box = {x: -150, y: base - sti, w: 1220, h: 150};
  const gg = KT.comp(L, 'gatestack', {}, 'The gate stack: metal on a thin high-k oxide, over three sides of each fin');
  gg._info = {title: 'The gate stack', lead: sc('lib.gate').blurb, facts: sc('lib.gate').facts};
  S(E('rect', {x: -150, y: base - sti - fh - 90, width: 1220, height: fh + 90}, gg), {fill: 'var(--c1)', fillOpacity: 0.16, stroke: 'var(--c1)', strokeWidth: 1.5});
  KTT(gg, -140, base - sti - fh - 60, 'the gate: metal over a high-k oxide a few atoms thick', 't-sm');
  gg._box = {x: -150, y: base - sti - fh - 90, w: 1220, h: fh + 90};
  for (let i = 0; i < 3; i++) {
    const cx = cx0 + i * fp, top = base - sti - fh;
    S(E('rect', {x: cx - fw / 2 - 2.2 * k, y: top - 2.2 * k, width: fw + 4.4 * k, height: fh + 2.2 * k, rx: 8, 'pointer-events': 'none'}, L), {fill: 'var(--c7)', fillOpacity: 0.5});
    const g = i === 1 ? ipart(L, ap, 'thefin', cx - fw / 2, top, fw, fh + sti, 'var(--c3)', '', {node: 'lib.channel', kid: {id: 'lib.channel'}, fo: 0.9, label: 'The fin under the gate: the channel'})
      : null;
    if (!g) S(E('rect', {x: cx - fw / 2, y: top, width: fw, height: fh + sti, rx: 6, 'pointer-events': 'none'}, L), {fill: 'var(--c3)', fillOpacity: 0.9});
  }
  const top = base - sti - fh;
  KT.wire(L, [[cx0 + fp - fw / 2, top - 40], [cx0 + fp + fw / 2, top - 40]]); KTT(L, cx0 + fp, top - 52, `${on('fin_w')}`, 't-sm', 'middle', onf('fin_w'));
  KT.wire(L, [[cx0 + 2 * fp + 70, top], [cx0 + 2 * fp + 70, base - sti]]); KTT(L, cx0 + 2 * fp + 80, top + fh / 2, `${on('fin_h')} above the oxide`, 't-sm', 'start', onf('fin_h'));
  KT.wire(L, [[cx0, base - sti - fh - 110], [cx0 + fp, base - sti - fh - 110]]); KTT(L, cx0 + fp / 2, base - sti - fh - 120, `fin pitch ${on('fin_p')}`, 't-sm', 'middle', onf('fin_p'));
  KT.wire(L, [[-110, 690], [-110 + 10 * k, 690]], 'bus'); KTT(L, -110 + 10 * k + 10, 696, '10 nm', 't-sm');
  KTT(L, 300, 696, 'the current flows into the page, along each fin, under the gate', 't-sm');
}, def: () => ({id: 'lib.channel'}), kids: () => [{id: 'lib.channel'}]});
/* the channel: the strip of fin under the gate, seen from the side; a patch of its atoms */
bnode('lib.channel', {draw: (L, ap) => {
  KT.frame(L, {title: 'The channel: the fin under the gate, from the side', sub: `about 6 × 20 × 45 nm: some ${on('ch_at')} silicon atoms (inferred); the gate about ${on('lg')} long`, subf: `${onf('ch_at')} ${onf('lg')}`,
    col: CC.logic, tags: [['unknown', 'sizes: inferred']]});
  const k = 11, lg = 20 * k, h = 45 * k, x0 = 460 - lg / 2, y0 = 120;
  const gsd = KT.comp(L, 'sd', {}, 'The source and the drain');
  gsd._info = {title: 'Source and drain', lead: 'Doped silicon on either side of the gate: electrons enter at the source and leave at the drain.', facts: sc('lib.channel').facts};
  S(E('rect', {x: x0 - 360, y: y0, width: 360, height: h, rx: 6}, gsd), {fill: 'var(--c5)', fillOpacity: 0.2, stroke: 'var(--c5)', strokeWidth: 1.5});
  S(E('rect', {x: x0 + lg, y: y0, width: 360, height: h, rx: 6}, gsd), {fill: 'var(--c5)', fillOpacity: 0.2, stroke: 'var(--c5)', strokeWidth: 1.5});
  KTT(gsd, x0 - 180, y0 + h / 2, 'source', 't-labb', 'middle'); KTT(gsd, x0 + lg + 180, y0 + h / 2, 'drain', 't-labb', 'middle');
  gsd._box = {x: x0 - 360, y: y0, w: lg + 720, h};
  const gch = KT.comp(L, 'chan', {}, 'The channel under the gate');
  gch._info = {title: 'The channel', lead: sc('lib.channel').blurb, facts: sc('lib.channel').facts};
  S(E('rect', {x: x0, y: y0, width: lg, height: h}, gch), {fill: 'var(--c3)', fillOpacity: 0.3, stroke: 'var(--c3)', strokeWidth: 1.5});
  gch._box = {x: x0, y: y0, w: lg, h};
  S(E('rect', {x: x0 - 10, y: y0 - 70, width: lg + 20, height: 60, rx: 4, 'pointer-events': 'none'}, L), {fill: 'var(--c1)', fillOpacity: 0.4, stroke: 'var(--c1)', strokeWidth: 1.5});
  KTT(L, x0 + lg / 2, y0 - 32, 'gate', 't-labb', 'middle');
  for (let i = 0; i < 9; i++) { const y = y0 + 40 + i * 50; KT.wire(L, [[x0 - 300, y], [x0 + lg + 300, y]], 'thin'); E('path', {class: 'w', d: `M${x0 + lg + 290},${y - 6} L${x0 + lg + 300},${y} L${x0 + lg + 290},${y + 6}`}, L); }
  KTT(L, x0 + lg + 300, y0 + h + 30, 'electrons flow when the gate is on', 't-sm', 'end');
  // a patch of the crystal, the seat of the lattice's own drawing
  const pa = {x: x0 + lg / 2 - 24, y: y0 + h / 2 - 24, w: 48, h: 48};
  const gl = ipart(L, ap, 'lattice', pa.x, pa.y, pa.w, pa.h, 'var(--c2)', '', {node: 'lib.si', kid: {id: 'lib.si'}, fo: 0.05, label: 'A patch of the silicon crystal'});
  const a = 0.5431 * k;
  for (let i = 0; i < 9; i++) for (let j = 0; j < 9; j++) S(E('circle', {cx: pa.x + 2 + i * a, cy: pa.y + 2 + j * a, r: 1.3, 'pointer-events': 'none'}, gl), {fill: 'var(--ink)'});
  KTT(L, pa.x + pa.w + 10, pa.y - 6, 'the atoms', 't-smb halo');
  KT.wire(L, [[-110, 690], [-110 + 5 * k, 690]], 'bus'); KTT(L, -110 + 5 * k + 10, 696, '5 nm', 't-sm');
}, def: () => ({id: 'lib.si'}), kids: () => [{id: 'lib.si'}]});
/* the silicon crystal: one cubic cell of the diamond lattice, its tetrahedral bonds */
bnode('lib.si', {draw: (L, ap) => {
  KT.frame(L, {title: 'The silicon crystal: one cell of the diamond lattice', sub: `a cube ${on('si_a')} on a side; neighbours ${on('si_nn')} apart; a 6 nm fin is about ${on('si_pl')} of atoms across`, subf: `${onf('si_a')} ${onf('si_nn')} ${onf('si_pl')}`,
    col: CC.logic, tags: [['documented', 'lattice: NIST CODATA'], ['generic', 'drawn to scale']]});
  const A = 430, az = 0.42, el = 0.36, ox = 220, oy = 560;
  const P = (x, y, z) => ({x: ox + (x * Math.cos(az) + y * Math.sin(az)) * A, y: oy + ((x * Math.sin(az) - y * Math.cos(az)) * Math.sin(el) - z * Math.cos(el)) * A * 0.9});
  const fcc = [];
  [0, 1].forEach(x => [0, 1].forEach(y => [0, 1].forEach(z => fcc.push([x, y, z]))));
  [[0.5, 0.5, 0], [0.5, 0.5, 1], [0.5, 0, 0.5], [0.5, 1, 0.5], [0, 0.5, 0.5], [1, 0.5, 0.5]].forEach(p => fcc.push(p));
  const inner = [[0.25, 0.25, 0.25], [0.25, 0.75, 0.75], [0.75, 0.25, 0.75], [0.75, 0.75, 0.25]];
  const gcube = KT.comp(L, 'cube', {}, 'The cubic cell: 8 atoms’ worth, in a cube 0.543 nm on a side');
  gcube._info = {title: 'The unit cell', lead: sc('lib.si').blurb, facts: sc('lib.si').facts};
  [[[0, 0, 0], [1, 0, 0]], [[0, 0, 0], [0, 1, 0]], [[0, 0, 0], [0, 0, 1]], [[1, 0, 0], [1, 1, 0]], [[1, 0, 0], [1, 0, 1]], [[0, 1, 0], [1, 1, 0]], [[0, 1, 0], [0, 1, 1]], [[0, 0, 1], [1, 0, 1]], [[0, 0, 1], [0, 1, 1]], [[1, 1, 0], [1, 1, 1]], [[1, 0, 1], [1, 1, 1]], [[0, 1, 1], [1, 1, 1]]]
    .forEach(([a, b]) => { const p = P(...a), q = P(...b); S(E('line', {x1: p.x, y1: p.y, x2: q.x, y2: q.y}, gcube), {stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '5 6'}); });
  const gb = KT.comp(L, 'bonds', {}, 'The bonds: each atom joined to four neighbours at the corners of a tetrahedron');
  gb._info = {title: 'The bonds', lead: 'Each silicon atom shares an electron pair with each of its four nearest neighbours, which sit at the corners of a tetrahedron around it: 0.235 nm away.', facts: sc('lib.si').facts};
  inner.forEach(c => fcc.forEach(f => { const d = Math.hypot(c[0] - f[0], c[1] - f[1], c[2] - f[2]); if (Math.abs(d - Math.sqrt(3) / 4) < 1e-6) { const p = P(...c), q = P(...f); S(E('line', {x1: p.x, y1: p.y, x2: q.x, y2: q.y}, gb), {stroke: 'var(--c2)', strokeWidth: 4, strokeLinecap: 'round'}); } }));
  gb._box = {x: ox - A, y: oy - A, w: 2 * A, h: A};
  const ga = KT.comp(L, 'atoms', {}, 'The atoms');
  ga._info = {title: 'Silicon atoms', lead: 'At the corners and the faces of the cube, and four inside it: the diamond lattice. About 50 atoms per cubic nanometre.', facts: sc('lib.si').facts};
  fcc.concat(inner).map(p => ({p, q: P(...p), d: -(p[0] * Math.sin(az) - p[1] * Math.cos(az))})).sort((a, b) => a.d - b.d).forEach(({p, q}) => {
    const isIn = inner.some(i => i[0] === p[0] && i[1] === p[1] && i[2] === p[2]);
    S(E('circle', {cx: q.x, cy: q.y, r: isIn ? 22 : 18}, ga), {fill: isIn ? 'var(--c1)' : 'color-mix(in srgb, var(--c1) 45%, var(--surface))', stroke: 'var(--ink)', strokeWidth: 1.5});
  });
  ga._box = {x: ox - A, y: oy - A, w: 2 * A, h: A};
  const p0 = P(0, 0, 0), p1 = P(1, 0, 0);
  KT.wire(L, [[p0.x, p0.y + 46], [p1.x, p1.y + 46]]); KTT(L, (p0.x + p1.x) / 2, (p0.y + p1.y) / 2 + 78, `a = ${on('si_a')}`, 't-smb', 'middle', onf('si_a'));
  KTT(L, 760, 200, 'the bottom of the ladder:', 't-smb'); KTT(L, 760, 224, 'below this are the atoms’ nuclei', 't-sm'); KTT(L, 760, 246, 'and electrons, which no picture', 't-sm'); KTT(L, 760, 268, 'of a chip resolves', 't-sm');
}});
/* the die in section: the transistors at the bottom, the wiring above, the bumps on top */
bnode('die.metal', {draw: (L, ap) => {
  KT.frame(L, {title: 'The die in section: transistors, then the wiring', sub: `the finest wires ${on('m_pitch')} apart (TSMC N7); ${on('masks')} make the chip; heights not to scale`, subf: `${onf('m_pitch')} ${onf('masks')}`,
    col: CC.logic, tags: [['unknown', 'layer count: not published'], ['documented', 'pitch: outside source']]});
  const gt = ipart(L, ap, 'fets', -150, 560, 1220, 90, 'var(--c3)', 'the transistors (fins and gates)', {node: 'lib.finfet', kid: {id: 'lib.finfet'}, ty: 52, fo: 0.2});
  // a row of fins under their gates, as a glyph (the FinFET scene has them to scale)
  for (let x = 560; x < 1040; x += 26) S(E('rect', {x, y: 596, width: 7, height: 34, 'pointer-events': 'none'}, gt), {fill: 'var(--c3)', fillOpacity: 0.7});
  S(E('rect', {x: 548, y: 586, width: 500, height: 12, rx: 2, 'pointer-events': 'none'}, gt), {fill: 'var(--c1)', fillOpacity: 0.45});
  KTT(L, -150, 680, 'drawn face up, the bumps on top: in the package the die is flipped, face down on its bumps', 't-sm');
  let y = 540;
  const layers = [[6, 10, 12, 'M0-M4: the finest wires'], [3, 18, 22, 'middle layers'], [3, 30, 40, 'thick top layers: power and long wires (how many: not published)']];
  const gw = KT.comp(L, 'wires', {}, 'The wiring stack: copper wires in insulator, vias between');
  gw._info = {title: 'The wiring stack', lead: sc('die.metal').blurb, facts: sc('die.metal').facts};
  layers.forEach(([n, hgt, pitch, lab]) => {
    for (let i = 0; i < n; i++) {
      y -= hgt + 22;
      for (let x = -140; x < 1060; x += pitch * 1.6) S(E('rect', {x, y, width: pitch * 0.8, height: hgt}, gw), {fill: 'var(--c5)', fillOpacity: 0.55});
      if (i % 2) for (let x = -140 + pitch * 0.4; x < 1060; x += pitch * 6.4) S(E('rect', {x, y: y + hgt, width: 3, height: 22}, gw), {fill: 'var(--c5)'});
    }
    KTT(L, 1080, y + 10, lab, 't-sm halo', 'end');
  });
  gw._box = {x: -150, y, w: 1220, h: 540 - y};
  const gp = KT.comp(L, 'bumps', {}, 'The bumps that join the die to the package');
  gp._info = {title: 'The bumps', lead: 'On top of the wiring, small solder bumps join the die, face down, to the package: more than 30,000 of them.', facts: (sc('package') || {}).facts || []};
  for (let x = -100; x < 1000; x += 120) S(E('circle', {cx: x, cy: y - 40, r: 26}, gp), {fill: 'var(--ink-2)', fillOpacity: 0.35, stroke: 'var(--ink-2)', strokeWidth: 1.5});
  KTT(gp, 1080, y - 34, 'bumps', 't-sm', 'end');
  gp._box = {x: -150, y: y - 70, w: 1220, h: 60};
}, seat: (ap, p, pel, Lp) => ({r: {x: DW * 0.45, y: DH * 0.45, w: DW * 0.1, h: DH * 0.06}, g: partBox(Lp, 'chip') ? partBox(Lp, 'chip').g : null, tr: 'jump'}),
def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});
/* the copied drawings' own transistors and gates lead on down the ladder */
const libLink = (id, map) => { const N0 = NODES[id], b0 = N0.build; N0.build = (L, ap, p, P, d) => { b0(L, ap, p, P, d); Object.entries(map).forEach(([key, el]) => mlSibs(L, ap, key, () => ({el, tr: 'jump'}))); }; };
libLink('lib.latch', {inv1: {id: 'lib.inverter'}, inv2: {id: 'lib.inverter'}});
libLink('lib.sram6t', {cell: {id: 'lib.finfet'}});
libLink('l1d.cmp', {xnors: {id: 'lib.xor'}});
NODES['lib.latch'].def = () => ({id: 'lib.inverter'}); NODES['lib.latch'].kids = () => [{id: 'lib.inverter'}];
NODES['lib.sram6t'].def = () => ({id: 'lib.finfet'}); NODES['lib.sram6t'].kids = () => [{id: 'lib.finfet'}];
NODES['l1d.cmp'].def = () => ({id: 'lib.xor'}); NODES['l1d.cmp'].kids = () => [{id: 'lib.xor'}];
/* the minion's default way down is now the compute ladder: the vector unit, a lane, its multiply-add */
NODES.minion.def = () => ({id: 'vpu'});
NODES.minion.kids = () => [{id: 'vpu'}, {id: 'core'}, {id: 'tensor'}, {id: 'l1d'}];
NODES.shire.kids = p => [{id: 'shire.bank', k: String(L2X().bank)}, {id: 'shire.meshstop'}, {id: 'shire.uc'}, {id: 'shire.xbar'}, {id: 'shire.neigh', k: '0'}];
NODES.die.kids = () => [{id: 'shire', k: '32'}, {id: 'memshire', k: '0'}, {id: 'dram', k: `0.${DRX().ch}`}, {id: 'mesh'}, {id: 'pcie'}, {id: 'io'}, {id: 'die.metal'}];
/* the 2:1 multiplexer: two transmission gates, one open at a time */
bnode('lib.mux2', {draw: (L, ap) => {
  KT.frame(L, {title: 'A 2:1 multiplexer, in transistors', sub: 'two transmission gates (an NMOS and a PMOS side by side): S picks which input reaches the output', col: CC.logic, tags: [['generic', 'textbook']]});
  const tg = (y, lab, on) => {
    const n = KT.mosH(L, 400, y + 40, {lead: 30}), p = KT.mosH(L, 400, y - 40, {p: true, down: true, lead: 30});
    KT.wire(L, [[200, y], [340, y], [340, y - 40], [370, y - 40]]); KT.wire(L, [[340, y], [340, y + 40], [370, y + 40]]); KT.jn(L, 340, y);
    KT.wire(L, [[430, y - 40], [460, y - 40], [460, y + 40], [430, y + 40]]); KT.jn(L, 460, y);
    KT.netLab(L, 192, y + 6, lab, 'end');
    KT.netLab(L, n.gate.x, n.gate.y + 22, on ? 'S' : "S'", 'middle'); KT.netLab(L, p.gate.x, p.gate.y - 10, on ? "S'" : 'S', 'middle');
    return {n, p, out: {x: 460, y}};
  };
  const a = tg(170, 'A', false), b = tg(430, 'B', true);
  KT.wire(L, [[460, 170], [600, 170], [600, 430], [460, 430]]); KT.wire(L, [[600, 300], [760, 300]]); KT.jn(L, 600, 300); KT.netLab(L, 768, 306, 'OUT');
  ipart(L, ap, 'onefet', 378, 186, 44, 48, 'var(--c2)', '', {node: 'lib.finfet', kid: {id: 'lib.finfet'}, tr: 'jump', fo: 0.1, label: 'One transistor'});
  const tb = KT.comp(L, 'mtable', {}, 'What the multiplexer does'); tb._info = {title: 'The multiplexer', lead: sc('lib.mux2').blurb, facts: sc('lib.mux2').facts};
  KTT(tb, 840, 280, 'S | OUT', 't-mono'); KTT(tb, 840, 304, '0 |  A', 't-mono'); KTT(tb, 840, 326, '1 |  B', 't-mono');
  tb._box = {x: 832, y: 260, w: 120, h: 80};
  KTT(L, -150, 640, 'a transmission gate passes both a 0 and a 1 fully: the NMOS passes zeros well, the PMOS ones', 't-sm');
}, def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});
