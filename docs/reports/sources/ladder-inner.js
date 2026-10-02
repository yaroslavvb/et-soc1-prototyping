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
    invStates(L, p, n);
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
/* ================= the device, the atom and below, and the ring of sizes (1 October 2026) =================
   The owner: "zooming in all the way to computing transistors, and to the individual atoms, assuming it's using TSMC
   7nm ... zoom in to the lowest bits, maybe zoom in to all the way to quarks ... The goal is to learn more about
   electronics as well. So I want the electronics bits filled in." The FinFET, the fin and the channel are drawn at TSMC
   N7's published numbers (the fin 6 by 52 nm, the gate 16.5 nm: the earlier inference of 6-7 by 45-50 nm and a 20 nm
   gate is superseded), with the gate switch: press it (or G) and the drawings show the transistor on at the minion
   rail's 0.517 V. Then the silicon crystal and its band gap, one atom, its nucleus, a proton, a quark and the Planck
   length; beside them an electron, a phosphorus dopant and a DRAM cell (a DRAM process, not N7). Every number drawn is
   a fact's (D.onum; the ladder's data, docs/reports/data/2026-10-01-ladder). Each scene has a phone layout: the picture
   on top and its notes under it, in type at least 11 px on a 390 px screen. */
const IVIEW = () => ({x: MLF.x + MLF.w / 2 - 380, y: MLF.y, w: 760, h: Math.max(760, 760 * phHW())});
/* a scene's backdrop, frame, title, line and tags, and the boxes its picture and its notes go in (a phone: the column
   IVIEW, the picture over the notes; a wide screen: the frame, the notes in a column right of the picture) */
function ihead(L, o) {
  L.classList.add('inr');
  const v = PH ? IVIEW() : {x: MLF.x, y: MLF.y, w: MLF.w, h: MLF.h};
  S(E('rect', {class: 'zbd', x: MLF.x - 10, y: MLF.y - 10, width: MLF.w + 20, height: Math.max(MLF.h, v.y + v.h - MLF.y) + 30, rx: 14, 'pointer-events': 'none'}, L), {fill: 'var(--page)'});
  const fr = E('g', {class: 'ifr', 'pointer-events': 'none'}, L);
  S(E('rect', {x: v.x, y: v.y, width: v.w, height: v.h, rx: 14}, fr), {fill: o.col || 'var(--c1)', fillOpacity: 0.03, stroke: o.col || 'var(--c1)', strokeWidth: 2.5});
  let y = v.y + (PH ? 2 : 42);
  // (a phone: the title wrapped to two lines at most, its type 32 units in a column 760 wide, at least 11 px)
  (PH ? wrapW(o.title, 40).slice(0, 2) : [o.title]).forEach(t => { if (PH) y += 38; KTT(fr, v.x + 20, y, t, 'i-t'); });
  wrapW(o.sub || '', PH ? 46 : 110).forEach(t => { y += PH ? 30 : 25; KTT(fr, v.x + 20, y, t, 'i-s', 'start', o.subf); });
  if (!PH) { let xr = v.x + v.w - 18; (o.tags || []).forEach(t => { xr -= KT.tagPill(fr, xr, v.y + 18, t[0], t[1]) + 8; }); y += 22; }
  else {
    // the tags under the title, in pills sized for the phone's type
    y += 14; let xl = v.x + 20;
    (o.tags || []).forEach(t => { const w = Math.round(t[1].length * 12.6 + 28); if (xl > v.x + 20 && xl + w > v.x + v.w - 20) { xl = v.x + 20; y += 42; } const g = E('g', {class: 'tg ' + t[0]}, fr); E('rect', {x: xl, y, width: w, height: 34, rx: 17}, g); T(g, xl + w / 2, y + 25, t[1], 'i-n', 'middle'); xl += w + 8; });
    y += 54;
  }
  const pw = o.pw || 760, swh = o.sw ? 62 : 0;
  const pic = PH ? {x: v.x + 20, y, w: v.w - 40, h: Math.min(o.phh || 420, v.y + v.h - y - 250)} : {x: v.x + 22, y, w: pw, h: v.y + v.h - y - 14};
  pic.hd = pic.h - swh;   // the drawing's height, the switch under it
  const sw = o.sw ? {x: pic.x, y: pic.y + pic.h - 50} : null;
  const nb = PH ? {x: v.x + 22, y: pic.y + pic.h + 36, w: v.w - 44, fs: 25, lh: 30, ch: 49, ymax: v.y + v.h - 10} : {x: v.x + 22 + pw + 28, y: y + 14, w: v.w - pw - 72, fs: 18, lh: 23, ch: Math.floor((v.w - pw - 72) / 9.2), ymax: v.y + v.h - 10};
  return {v, pic, nb, sw};
}
/* a scene's notes: paragraphs wrapped to the column; {t, f} a line and the facts it rests on, {b} a heading, {a, b2, f}
   the two states' texts at the same place (the switch picks which shows); {ph: false} only on a wide screen */
function inotes(L, lay, items) {
  const nb = lay.nb, g = E('g', {class: 'inotes'}, L);
  let y = nb.y;
  const SA = E('g', {class: 'st-a'}, g), SB = E('g', {class: 'st-b'}, g);
  items.filter(it => !(PH && it.ph === false)).forEach(it => {
    // (what does not fit in the frame is left to the panel, where every fact is listed)
    const n0 = it.a != null ? Math.max(wrapW(it.a, nb.ch).length, wrapW(it.b2, nb.ch).length) : wrapW(it.t, nb.ch).length;
    if (y + (n0 - 1) * nb.lh > nb.ymax) { y = Infinity; return; }
    if (it.a != null) {
      const la = wrapW(it.a, nb.ch), lb = wrapW(it.b2, nb.ch);
      la.forEach((t, i) => KTT(SA, nb.x, y + i * nb.lh, t, 'i-s ist', 'start', it.f));
      lb.forEach((t, i) => KTT(SB, nb.x, y + i * nb.lh, t, 'i-s ist', 'start', it.f));
      y += Math.max(la.length, lb.length) * nb.lh + nb.lh * 0.45;
      return;
    }
    const lines = wrapW(it.t, nb.ch);
    lines.forEach((t, i) => KTT(g, nb.x, y + i * nb.lh, t, it.h ? 'i-l' : 'i-s', 'start', it.f));
    y += lines.length * nb.lh + nb.lh * (it.h ? 0.15 : 0.45);
  });
  return y;
}
/* a part of these scenes: the tree's (or the ladder's) name, lead and facts for its panel, its zoom and seat */
function ipt(L, ap, key, label, o) {
  const g = KT.comp(L, key, {}, label);
  const s0 = sc(o.node || key);
  g._info = o.info || {title: o.title || s0.name || label, lead: o.lead || s0.blurb || '', facts: o.facts || s0.facts || [], kick: o.kick};
  if (o.kid) { g._kid = o.kid; if (o.seat) ap.zs[pk(o.kid)] = {r: o.seat, g, tr: o.tr}; }
  if (o.box) g._box = o.box;
  return g;
}
/* the gate's two states, the same on the FinFET, the fin and the channel (the state holds from one to the next) */
const GATE = () => ({lab: 'The gate voltage', btn: [`Gate at ${on('v_0')} · switch on (G)`, `Gate at ${on('v_min')} · switch off (G)`],
  say: [`The gate at ${on('v_0')}: the transistor is off.`, `The gate at ${on('v_min')}, the minion rail: the transistor is on.`]});
const SWW = () => (PH ? 470 : 330);
/* a box that leaves no part of the frame empty when a scene's notes run under its picture */
const KP = (pic, wNm, hNm) => Math.min(pic.w / wNm, pic.h / hNm);
/* a point that does not move: the same "random" positions on every build (a stable drawing, and no flicker) */
const prand = i => { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };

/* ---- the FinFET from above: fins, gates and contacts at N7's pitches; one transistor (a gate over two fins) ---- */
bnode('lib.finfet', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'FinFET transistors from above, at N7’s pitches', sub: `gates ${on('n7_cpp')} apart, fins ${on('n7_fp')} apart, a dense cell ${on('n7_cell')} tall (TSMC N7)`, subf: `${onf('n7_cpp')} ${onf('n7_fp')} ${onf('n7_cell')}`,
    tags: [['documented', 'pitches: outside source'], ['generic', 'the pattern']], sw: 1});
  const p = lay.pic, ng = PH ? 6 : 7, k = Math.min(p.w / (57 * (ng - 0.4)), (p.hd - 90) / 250), fp = 30 * k, gp = 57 * k, lg = 16.5 * k, fw = 6 * k;
  const x0 = p.x + gp * 0.3, y0 = p.y + 20, ch = 240 * k;   // one 240 nm cell: 8 fin pitches
  // the cell's rows of fins: the p-type pair on top, the n-type pair below (2 fins per transistor)
  const rows = [1.5, 2.5, 5.5, 6.5], W = gp * (ng - 0.6);
  const gc = ipt(L, ap, 'cell', 'One standard cell row: 240 nm tall', {title: 'A standard-cell row', lead: 'Logic is built from cells of one height laid in rows: in N7\'s densest library a cell is 240 nm tall, 8 fin pitches, with room for two fins of p-type transistors on top and two of n-type below.', facts: ['n7.cells', 'n7.two-fin', 'n7.density-hd'], box: {x: x0 - 10, y: y0, w: W + 20, h: ch}});
  S(E('rect', {x: x0 - 10, y: y0, width: W + 20, height: ch, rx: 4}, gc), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeDasharray: '7 6'});
  const gk = ipt(L, ap, 'contacts', 'Source and drain contacts', {title: 'Source and drain', lead: 'Between the gates, metal contacts land on the fins: one side is the source, the other the drain. In N7 they are cobalt, which halved their resistance.', facts: ['n7.contacts-co', 'dope.n-sd', 'dope.p-sd'], box: {x: x0, y: y0, w: W, h: ch}});
  for (let j = 0; j < ng - 1; j++) [[0.9, 3.1], [4.9, 7.1]].forEach(([a, b]) => S(E('rect', {x: x0 + gp * j + lg / 2 + 0.12 * gp, y: y0 + a * fp, width: gp - lg - 0.24 * gp, height: (b - a) * fp, rx: 3}, gk), {fill: 'var(--c5)', fillOpacity: 0.2, stroke: 'var(--c5)', strokeWidth: 1.2}));
  // (part 1b: the fins over the contacts, so that a tap on a fin between the gates finds the fin on a phone)
  const gf = ipt(L, ap, 'fins', 'The fins: walls of silicon the current runs along', {node: 'lib.fin', box: {x: x0, y: y0, w: W, h: ch}});
  rows.forEach(r => S(E('rect', {x: x0, y: y0 + r * fp - fw / 2, width: W, height: fw}, gf), {fill: 'var(--c3)', fillOpacity: 0.6}));
  const gg = ipt(L, ap, 'gates', 'The gates: lines of metal over the fins', {node: 'lib.gate', box: {x: x0, y: y0 - 8, w: W, h: ch + 16}});
  for (let j = 0; j < ng; j++) S(E('rect', {x: x0 + gp * j - lg / 2, y: y0 - 8, width: lg, height: ch + 16, rx: 2}, gg), {fill: 'var(--c1)', fillOpacity: 0.45, stroke: 'var(--c1)', strokeWidth: 1.5});
  // one n-type transistor: the gate over the two lower fins; on, the fins under its gate fill with electrons
  const gx = x0 + gp * 2, dev = {x: gx - gp / 2, y: y0 + 4.6 * fp, w: gp, h: 2.8 * fp};
  const SB = E('g', {class: 'st-b', 'pointer-events': 'none'}, L);
  [5.5, 6.5].forEach(r => S(E('rect', {x: gx - lg / 2 - gp * 0.32, y: y0 + r * fp - fw / 2 - 2, width: lg + gp * 0.64, height: fw + 4, rx: 2}, SB), {fill: 'var(--c2)', fillOpacity: 0.85}));
  const ring = KT.comp(L, 'devring', {}, 'One transistor: a gate over two fins');
  S(E('rect', {class: 'shape', x: dev.x, y: dev.y, width: dev.w, height: dev.h, rx: 8}, ring), {fill: 'transparent', stroke: 'var(--c2)', strokeWidth: 3, strokeDasharray: '7 5'});
  ring._kid = {id: 'lib.fin'}; ring._info = {title: 'One transistor', lead: sc('lib.finfet').blurb, facts: sc('lib.finfet').facts}; ring._box = dev;
  ap.zs['lib.fin'] = {r: dev, g: ring, tr: 'jump'};
  KTT(L, dev.x + dev.w / 2, dev.y + dev.h + (PH ? 30 : 22), 'one transistor', 'i-l halo', 'middle');
  // dimensions and the switch
  const dy = y0 + ch + (PH ? 42 : 34);
  KT.wire(L, [[x0 + gp, dy], [x0 + 2 * gp, dy]]); KTT(L, x0 + 1.5 * gp, dy + (PH ? 30 : 24), on('n7_cpp'), 'i-l', 'middle', onf('n7_cpp'));
  KT.wire(L, [[x0 + W + 12, y0 + 5.5 * fp], [x0 + W + 12, y0 + 6.5 * fp]]); if (!PH) KTT(L, x0 + W + 20, y0 + 6 * fp + 6, on('n7_fp'), 'i-l', 'start', onf('n7_fp'));
  KTT(L, x0 - 16, y0 + 2 * fp + 6, 'p', 'i-l', 'end'); KTT(L, x0 - 16, y0 + 6 * fp + 6, 'n', 'i-l', 'end');
  stateSwitch(L, lay.sw.x, lay.sw.y, GATE(), {w: SWW()});
  inotes(L, lay, [
    {t: 'How it switches', h: 1},
    {a: `Gate at ${on('v_0')}: no electrons under it; the transistor is off.`, b2: `Gate at ${on('v_min')}: its field pulls a sheet of electrons into the fins under it (lit); it conducts.`, f: 'el.switch el.rails'},
    {t: `Off is not quite off: below its threshold the current falls only tenfold for every ${on('n7_ss_mv')} less on the gate, and on average (at 80 °C) each transistor here still leaks about ${on('leak_e')}.`, f: `${onf('n7_ss_mv')} ${onf('leak_e')}`},
    {t: `The energy of a switch goes as the voltage squared: at ${on('v_min')} it is ${on('half')} of what it would be at N7's nominal ${on('v_nom')}.`, f: `${onf('half')} ${onf('v_nom')}`, ph: false},
    {t: 'p-type transistors on top, n-type below; this chip\'s own cells are not published, so the pattern is generic.', f: 'n7.cells', ph: false},
  ]);
}, def: () => ({id: 'lib.fin'}), kids: () => [{id: 'lib.fin'}]});

/* ---- the fins in section under the gate: N7's fin, 6 by 52 nm, tapered, its top rounded; the gate stack over it ---- */
/* a fin's outline: tapered from about 6 nm near its top to about 9 nm at the oxide, its top rounded (k units per nm) */
const finPath = (cx, top, base, k) => { const t = 3 * k, b = 4.5 * k, r = 3 * k; return `M${cx - b},${base}L${cx - t},${top + r}Q${cx - t},${top} ${cx},${top}Q${cx + t},${top} ${cx + t},${top + r}L${cx + b},${base}Z`; };
bnode('lib.fin', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'Fins in section, under the gate', sub: `each fin ${on('n7_fw')} wide and ${on('n7_fh')} tall, ${on('n7_fp')} apart (TSMC N7)`, subf: `${onf('n7_fw')} ${onf('n7_fh')} ${onf('n7_fp')}`,
    tags: [['documented', 'fin: outside source'], ['generic', 'its profile, the gate stack']], sw: 1});
  const p = lay.pic, nf = PH ? 2 : 3, k = Math.min(p.w / (30 * nf + 20), (p.hd - 12) / (16 + 52 + 10 + 8)), fp = 30 * k;
  const cx0 = p.x + p.w / 2 - fp * (nf - 1) / 2, top = p.y + 16 * k, base = top + 52 * k, sti = 10 * k;
  const gs = ipt(L, ap, 'substrate', 'The silicon wafer, and the oxide between the fins', {title: 'The wafer and the trench oxide', lead: 'The fins stand up from the silicon wafer; between them an insulating oxide (shallow trench isolation) keeps neighbouring transistors apart. A heavily doped layer at the fin\'s base stops current leaking under the channel.', facts: ['dope.levels', 'n7.fin-height'], box: {x: p.x, y: base, w: p.w, h: sti + 8 * k}});
  S(E('rect', {x: p.x, y: base, width: p.w, height: sti}, gs), {fill: 'var(--ink-2)', fillOpacity: 0.16});
  S(E('rect', {x: p.x, y: base + sti, width: p.w, height: 8 * k}, gs), {fill: 'var(--c3)', fillOpacity: 0.25, stroke: 'var(--c3)', strokeWidth: 1.5});
  KTT(gs, p.x + 8, base + sti - 8, 'oxide', 'i-n'); KTT(gs, p.x + 8, base + sti + 8 * k - 8, 'silicon wafer', 'i-n');
  // the gate: a metal fill over the stack, which wraps each fin
  const gg = ipt(L, ap, 'gatestack', 'The gate stack: metal on a thin high-k oxide, over three sides of each fin', {node: 'lib.gate', box: {x: p.x, y: p.y, w: p.w, h: base - p.y}});
  S(E('rect', {x: p.x, y: p.y, width: p.w, height: base - p.y}, gg), {fill: 'var(--c1)', fillOpacity: 0.14, stroke: 'var(--c1)', strokeWidth: 1.5});
  const gsk = E('g', {'pointer-events': 'none'}, gg);
  for (let i = 0; i < nf; i++) {
    const cx = cx0 + i * fp;
    // the stack around the fin, from the outside in: work-function metal (TiAl), HfO2, the interfacial SiO2
    S(E('path', {d: finPathW(cx, top, base, k, 4.2)}, gsk), {fill: 'var(--c7)', fillOpacity: 0.45});
    S(E('path', {d: finPathW(cx, top, base, k, 2.6)}, gsk), {fill: 'var(--c4)', fillOpacity: 0.5});
    S(E('path', {d: finPathW(cx, top, base, k, 0.8)}, gsk), {fill: 'var(--ink-2)', fillOpacity: 0.35});
  }
  const gf = [];
  for (let i = 0; i < nf; i++) {
    const cx = cx0 + i * fp, mid = i === (nf - 1) >> 1;
    const g = ipt(L, ap, mid ? 'thefin' : 'fin' + i, mid ? 'The fin under the gate: the channel' : 'A fin', mid ? {node: 'lib.channel', kid: {id: 'lib.channel'}, seat: {x: cx - 5 * k, y: top, w: 10 * k, h: base - top}, box: {x: cx - 5 * k, y: top, w: 10 * k, h: base - top}}
      : {node: 'lib.fin', box: {x: cx - 5 * k, y: top, w: 10 * k, h: base - top}});
    S(E('path', {class: 'shape', d: finPath(cx, top, base, k)}, g), {fill: 'var(--c3)', fillOpacity: 0.9, stroke: 'var(--c3)', strokeWidth: 1});
    gf.push(g);
  }
  // on: a sheet of electrons a nanometre inside the fin's three surfaces
  const SB = E('g', {class: 'st-b', 'pointer-events': 'none'}, L);
  for (let i = 0; i < nf; i++) S(E('path', {d: finPathW(cx0 + i * fp, top, base, k, -0.9).replace(/Z$/, ''), fill: 'none'}, SB), {stroke: 'var(--c2)', strokeWidth: Math.max(2.5, 1.2 * k), strokeLinejoin: 'round'});
  // labels and dimensions
  const c1 = cx0 + ((nf - 1) >> 1) * fp, lx = cx0 + (nf - 1) * fp + 9 * k;
  KT.wire(L, [[c1 - 3 * k, top - 8 * k], [c1 + 3 * k, top - 8 * k]]); KTT(L, c1, top - 8 * k - 10, on('n7_fw'), 'i-l halo', 'middle', onf('n7_fw'));
  KT.wire(L, [[lx, top], [lx, base]]); KTT(L, lx + 8, (top + base) / 2, on('n7_fh'), 'i-l halo', 'start', onf('n7_fh'));
  // (the fin pitch, between two fins' centres, in the oxide band: under the switch, review of 1 Oct, it was hidden)
  if (!PH) { const yp = base + 0.3 * sti; KT.wire(L, [[cx0, yp], [cx0 + fp, yp]]); KTT(L, cx0 + fp / 2, yp + 22, on('n7_fp'), 'i-l halo', 'middle', onf('n7_fp')); }
  const lk = E('g', {class: 'gkey', 'pointer-events': 'none'}, L), kx = p.x + 4, ky = p.y + 8;
  [['var(--c7)', PH ? on('tial') : `${on('tial')} work-function metal`], ['var(--c4)', PH ? on('hfo2') : `${on('hfo2')}, ${on('k24')}`], ['var(--ink-2)', PH ? 'SiO₂' : 'SiO₂, under 1 nm']].forEach(([c, t], i) => {
    S(E('rect', {x: kx + 4, y: ky + i * (PH ? 30 : 24), width: 16, height: 16, rx: 3}, lk), {fill: c, fillOpacity: 0.6});
    KTT(lk, kx + 28, ky + 14 + i * (PH ? 30 : 24), t, 'i-n halo', 'start', i === 0 ? onf('tial') : i === 1 ? onf('hfo2') : 'gate.eot');
  });
  stateSwitch(L, lay.sw.x, lay.sw.y, GATE(), {w: SWW()});
  inotes(L, lay, [
    {t: 'The gate wraps three sides', h: 1},
    {a: 'Gate off: the fin has almost no free electrons; nothing flows along it.', b2: `Gate on: a thin sheet of electrons lines the fin's two sides and its top: ${on('n7_weff')} of channel width per fin.`, f: 'el.switch n7.weff'},
    {t: `The insulator is ${on('hfo2')}, a high-k oxide, on a thin layer of silicon oxide: electrically like 1 nm of SiO₂, but a thicker barrier: several orders of magnitude fewer electrons tunnel through it.`, f: 'gate.hfo2 gate.eot'},
    {t: `The metal over it, ${on('tial')} for n-type and ${on('tin')} for p-type, sets where the transistor turns on by its work function, ${on('wf')}; tungsten or aluminium fills the rest (the industry's practice: TSMC does not publish N7's stack).`, f: 'gate.metals', ph: false},
    {t: 'The taper and the rounded top follow published sections of 10 nm-class fins; TSMC does not publish N7\'s exact profile.', f: 'cmp.tsmc10 cmp.intel10'},
  ]);
}, def: () => ({id: 'lib.channel'}), kids: () => [{id: 'lib.channel'}]});
/* the fin's outline grown (or shrunk, d < 0) by d nm all round: the layers of the gate stack */
function finPathW(cx, top, base, k, d) { const t = (3 + d) * k, b = (4.5 + d) * k, r = Math.max(0.5, 3 + d) * k, tp = top - d * k; return `M${cx - b},${base}L${cx - t},${tp + r}Q${cx - t},${tp} ${cx},${tp}Q${cx + t},${tp} ${cx + t},${tp + r}L${cx + b},${base}Z`; }

/* ---- the channel: the fin under the gate, from the side; the electrons in it, on and off; its band picture ---- */
bnode('lib.channel', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'The channel: the fin under the gate, from the side', sub: `${on('n7_lg')} long between source and drain: about ${on('ch_at')} silicon atoms`, subf: `${onf('n7_lg')} ${onf('ch_at')}`,
    tags: [['documented', 'length: outside source'], ['unknown', 'electrons: an estimate']], sw: 1});
  const p = lay.pic, k = Math.min(p.w * (PH ? 0.58 : 0.66) / (16.5 + 2 * 22), (p.hd - 50) / (52 + 18)), lg = 16.5 * k, h = 52 * k, sdw = 22 * k;
  const x0 = p.x + sdw, y0 = p.y + 18 * k;
  const gsd = ipt(L, ap, 'sd', 'The source and the drain', {title: 'Source and drain', lead: 'Silicon packed with phosphorus atoms, about one atom in thirty. Only about one in thirteen of them is active and gives up its spare electron, still far more free electrons than the channel has, so the source and drain conduct. Electrons enter at the source and leave at the drain.', facts: ['dope.n-sd', 'dope.count-sd', 'p.dopant.5'], box: {x: x0 - sdw, y: y0, w: lg + 2 * sdw, h}});
  S(E('rect', {x: x0 - sdw, y: y0, width: sdw, height: h, rx: 6}, gsd), {fill: 'var(--c5)', fillOpacity: 0.22, stroke: 'var(--c5)', strokeWidth: 1.5});
  S(E('rect', {x: x0 + lg, y: y0, width: sdw, height: h, rx: 6}, gsd), {fill: 'var(--c5)', fillOpacity: 0.22, stroke: 'var(--c5)', strokeWidth: 1.5});
  KTT(gsd, x0 - sdw / 2, y0 + 30, 'source', 'i-l', 'middle'); KTT(gsd, x0 + lg + sdw / 2, y0 + 30, 'drain', 'i-l', 'middle');
  const gch = ipt(L, ap, 'chan', 'The channel under the gate', {node: 'lib.channel', box: {x: x0, y: y0, w: lg, h}});
  S(E('rect', {class: 'shape', x: x0, y: y0, width: lg, height: h}, gch), {fill: 'var(--c3)', fillOpacity: 0.25, stroke: 'var(--c3)', strokeWidth: 1.5});
  const gate = E('g', {'pointer-events': 'none'}, L);
  S(E('rect', {x: x0 - 3, y: y0 - 14 * k, width: lg + 6, height: 11 * k, rx: 4}, gate), {fill: 'var(--c1)', fillOpacity: 0.4, stroke: 'var(--c1)', strokeWidth: 1.5});
  KTT(gate, x0 + lg / 2, y0 - 8.5 * k + 7, 'gate', 'i-l', 'middle');
  // on: about a hundred electrons in the channel, and the current from source to drain; off: none, and the leak
  const SB = E('g', {class: 'st-b', 'pointer-events': 'none'}, L), SA = E('g', {class: 'st-a', 'pointer-events': 'none'}, L);
  for (let i = 0; i < 100; i++) S(E('circle', {cx: x0 + 4 + prand(i) * (lg - 8), cy: y0 + 6 + prand(i + 500) * (h - 12), r: Math.max(2.4, 0.42 * k)}, SB), {fill: 'var(--c2)'});
  for (let i = 0; i < 3; i++) { const y = y0 + h * (0.25 + 0.25 * i); KT.wire(SB, [[x0 - sdw + 10, y], [x0 + lg + sdw - 14, y]], 'thin'); E('path', {class: 'w', d: `M${x0 + lg + sdw - 24},${y - 7}L${x0 + lg + sdw - 14},${y}L${x0 + lg + sdw - 24},${y + 7}`}, SB); }
  KTT(SB, x0 - sdw, y0 + h + (PH ? 34 : 26), `on: ${on('ch_e')} here (an estimate)`, 'i-l halo', 'start', onf('ch_e'));
  KTT(SA, x0 - sdw, y0 + h + (PH ? 34 : 26), `off: ${on('off_e')} here on average`, 'i-l halo', 'start', onf('off_e'));
  // a dopant atom of the source, and a patch of the crystal: the scenes inside
  const dp = {x: x0 - sdw / 2 - 10, y: y0 + h * 0.62, w: 20, h: 20};
  const gd = ipt(L, ap, 'dopant', 'A phosphorus atom of the source', {node: 'p.dopant', kid: {id: 'p.dopant'}, seat: dp, tr: 'jump', box: dp});
  S(E('circle', {class: 'shape', cx: dp.x + 10, cy: dp.y + 10, r: 8}, gd), {fill: 'var(--c5)', stroke: 'var(--ink)', strokeWidth: 1.5});
  KTT(L, x0 - sdw + 6, dp.y + 44, PH ? 'a P atom' : 'a phosphorus atom', 'i-n halo', 'start');
  const pa = {x: x0 + lg / 2 - 0.9 * k, y: y0 + h * 0.4, w: 1.8 * k, h: 1.8 * k}, a = 0.5431 * k;
  const gl = ipt(L, ap, 'lattice', 'A patch of the silicon crystal', {node: 'lib.si', kid: {id: 'lib.si'}, seat: {x: pa.x, y: pa.y, w: a, h: a}, tr: 'jump', box: pa});
  for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) S(E('circle', {cx: pa.x + 0.2 * k + i * a * 0.75, cy: pa.y + 0.2 * k + j * a * 0.75, r: 1.6, 'pointer-events': 'none'}, gl), {fill: 'var(--ink)'});
  E('rect', {class: 'ring', x: pa.x - 6, y: pa.y - 6, width: pa.w + 12, height: pa.h + 12, rx: 4}, gl);
  if (!PH) KTT(L, pa.x + pa.w + 10, pa.y - 4, 'the atoms', 'i-n halo');
  // the band picture: the energy an electron needs along the channel, a barrier when off, pulled down when on
  const bx = x0 + lg + sdw + 24, by = y0 + 10, bw = Math.min(260, p.x + p.w - bx), bh = PH ? 190 : 150;
  const gbn = ipt(L, ap, 'bands', 'The band picture: the barrier the gate lowers', {title: 'The barrier the gate controls', lead: 'Across the channel an electron from the source meets an energy barrier. With the gate at 0 V the barrier is high and almost none get over it; with the gate at the rail the barrier drops and they flow. Below the threshold each 65 mV less on the gate cuts the current tenfold.', facts: ['el.switch', 'n7.ss', 'el.off-not-off', 'si.bandgap'], box: {x: bx, y: by, w: bw, h: bh}});
  S(E('rect', {class: 'shape', x: bx, y: by, width: bw, height: bh, rx: 8}, gbn), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 1.25});
  const bs = bw * 0.28, bd = bw - 2 * bs, ylo = by + bh - 40;
  KT.wire(gbn, [[bx + 10, ylo], [bx + bs, ylo]]); KT.wire(gbn, [[bx + bs + bd, ylo], [bx + bw - 10, ylo]]);
  const ba = E('g', {class: 'st-a'}, gbn), bb = E('g', {class: 'st-b'}, gbn);
  KT.wire(ba, [[bx + bs, ylo], [bx + bs + 10, by + 34], [bx + bs + bd - 10, by + 34], [bx + bs + bd, ylo]]);
  KT.wire(bb, [[bx + bs, ylo], [bx + bs + 10, ylo - 26], [bx + bs + bd - 10, ylo - 26], [bx + bs + bd, ylo]]);
  KTT(gbn, bx + 10, by + bh - 12, 'source', 'i-n'); KTT(gbn, bx + bw - 10, by + bh - 12, 'drain', 'i-n', 'end');
  KTT(ba, bx + bw / 2, by + 26, 'off: a barrier', 'i-n', 'middle'); KTT(bb, bx + bw / 2, ylo - 34, 'on: pulled down', 'i-n', 'middle');
  KTT(gbn, bx, by - 10, 'an electron\'s energy', 'i-n');
  stateSwitch(L, lay.sw.x, lay.sw.y, GATE(), {w: SWW()});
  inotes(L, lay, [
    {t: 'Where the current flows', h: 1},
    {a: `Off: the channel holds ${on('off_e')} on average; still, about ${on('leak_e')} slip through.`, b2: `On: ${on('ch_e')} sit in the channel, each crossing it in about ${on('cross_t')}.`, f: 'el.off-channel el.channel-electrons si.mobility'},
    {t: `Only ${on('ch_dop')} (often none) are in the channel itself: the gate's metal, not doping, sets where it turns on.`, f: `${onf('ch_dop')} gate.undoped-vt`},
    {t: `Across the fin's 6 nm stand ${on('si_pw')} of atoms: electronics here is counted in atoms.`, f: onf('si_pw'), ph: false},
  ]);
}, def: () => ({id: 'lib.si'}), kids: () => [{id: 'lib.si'}, {id: 'p.dopant'}]});

/* ---- the silicon crystal: one cubic cell of the diamond lattice; why pure silicon barely conducts (the band gap) ---- */
bnode('lib.si', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'The silicon crystal: one cell of the diamond lattice', sub: `a cube ${on('si_a')} on a side; neighbours ${on('si_nn')} apart`, subf: `${onf('si_a')} ${onf('si_nn')}`,
    tags: [['documented', 'lattice: NIST CODATA'], ['generic', 'drawn to scale']]});
  const p = lay.pic, bw0 = PH ? 220 : 210, A = Math.min((p.w - bw0 - 40) / 1.32, (p.h - 80) / 1.27), az = 0.42, el = 0.36, ox = p.x + 10, oy = p.y + 14 + 1.14 * A;
  const P = (x, y, z) => ({x: ox + (x * Math.cos(az) + y * Math.sin(az)) * A, y: oy + ((x * Math.sin(az) - y * Math.cos(az)) * Math.sin(el) - z * Math.cos(el)) * A * 0.9});
  const fcc = [];
  [0, 1].forEach(x => [0, 1].forEach(y => [0, 1].forEach(z => fcc.push([x, y, z]))));
  [[0.5, 0.5, 0], [0.5, 0.5, 1], [0.5, 0, 0.5], [0.5, 1, 0.5], [0, 0.5, 0.5], [1, 0.5, 0.5]].forEach(q => fcc.push(q));
  const inner = [[0.25, 0.25, 0.25], [0.25, 0.75, 0.75], [0.75, 0.25, 0.75], [0.75, 0.75, 0.25]];
  const gcube = ipt(L, ap, 'cube', 'The cubic cell: 8 atoms’ worth, in a cube 0.543 nm on a side', {title: 'The unit cell', node: 'lib.si'});
  [[[0, 0, 0], [1, 0, 0]], [[0, 0, 0], [0, 1, 0]], [[0, 0, 0], [0, 0, 1]], [[1, 0, 0], [1, 1, 0]], [[1, 0, 0], [1, 0, 1]], [[0, 1, 0], [1, 1, 0]], [[0, 1, 0], [0, 1, 1]], [[0, 0, 1], [1, 0, 1]], [[0, 0, 1], [0, 1, 1]], [[1, 1, 0], [1, 1, 1]], [[1, 0, 1], [1, 1, 1]], [[0, 1, 1], [1, 1, 1]]]
    .forEach(([a, b]) => { const q = P(...a), r = P(...b); S(E('line', {x1: q.x, y1: q.y, x2: r.x, y2: r.y}, gcube), {stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '5 6'}); });
  gcube._box = {x: ox - A, y: oy - A, w: 2 * A, h: A * 1.1};
  const gb = ipt(L, ap, 'bonds', 'The bonds: each atom joined to four neighbours at the corners of a tetrahedron', {title: 'The bonds', lead: 'Each silicon atom shares an electron pair with each of its four nearest neighbours, which sit at the corners of a tetrahedron around it, 0.235 nm away. Every outer electron is held in a bond: none is free to carry current.', facts: ['si.lattice', 'p.atom.3', 'si.bandgap']});
  inner.forEach(c => fcc.forEach(f => { const d = Math.hypot(c[0] - f[0], c[1] - f[1], c[2] - f[2]); if (Math.abs(d - Math.sqrt(3) / 4) < 1e-6) { const q = P(...c), r = P(...f); S(E('line', {x1: q.x, y1: q.y, x2: r.x, y2: r.y}, gb), {stroke: 'var(--c2)', strokeWidth: 4, strokeLinecap: 'round'}); } }));
  gb._box = {x: ox - A, y: oy - A, w: 2 * A, h: A};
  const ga = ipt(L, ap, 'atoms', 'The atoms', {title: 'Silicon atoms', lead: 'At the corners and the faces of the cube, and four inside it: the diamond lattice. About 50 atoms in every cubic nanometre.', facts: ['si.density', 'p.atom.4']});
  const rad = Math.max(12, A * 0.045);
  fcc.concat(inner).map(q => ({q, s: P(...q), d: -(q[0] * Math.sin(az) - q[1] * Math.cos(az))})).sort((a, b) => a.d - b.d).forEach(({q, s}) => {
    const isIn = inner.some(i => i[0] === q[0] && i[1] === q[1] && i[2] === q[2]);
    S(E('circle', {cx: s.x, cy: s.y, r: isIn ? rad * 1.2 : rad}, ga), {fill: isIn ? 'var(--c1)' : 'color-mix(in srgb, var(--c1) 45%, var(--surface))', stroke: 'var(--ink)', strokeWidth: 1.5});
  });
  ga._box = {x: ox - A, y: oy - A, w: 2 * A, h: A};
  // one atom inside the cell: the scene of one atom
  const a1 = P(0.75, 0.25, 0.75), ab = {x: a1.x - rad * 1.6, y: a1.y - rad * 1.6, w: rad * 3.2, h: rad * 3.2};
  const g1 = ipt(L, ap, 'oneatom', 'One silicon atom', {node: 'p.atom', kid: {id: 'p.atom'}, seat: ab, tr: 'jump', box: ab});
  S(E('circle', {class: 'shape', cx: a1.x, cy: a1.y, r: rad * 1.25}, g1), {fill: 'var(--c2)', fillOpacity: 0.85, stroke: 'var(--ink)', strokeWidth: 2});
  KTT(L, a1.x + rad * 1.6, a1.y - rad * 1.6, 'one atom', 'i-l halo');
  const q0 = P(0, 0, 0), q1 = P(1, 0, 0);
  KT.wire(L, [[q0.x, q0.y + 30], [q1.x, q1.y + 30]]); KTT(L, (q0.x + q1.x) / 2, (q0.y + q1.y) / 2 + 58, `a = ${on('si_a')}`, 'i-l', 'middle', onf('si_a'));
  // the band gap against the heat's energy
  const bx = p.x + p.w - bw0, by = p.y + 10, bw = bw0, bh = Math.min(300, p.h - 20);
  const gg = ipt(L, ap, 'gap', 'The band gap', {title: 'The band gap', lead: 'An electron held in a bond must gain 1.12 eV to break free and conduct. The heat of the room gives a typical electron only 25.9 meV, 43 times less, so almost none break free: pure silicon is nearly an insulator.', facts: ['si.bandgap', 'el.kt', 'si.ni'], box: {x: bx, y: by, w: bw, h: bh}});
  S(E('rect', {class: 'shape', x: bx, y: by, width: bw, height: bh, rx: 8}, gg), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 1.25});
  const ev = by + bh - 70, ec = by + 60, sc0 = (ev - ec) / 1.12;
  S(E('rect', {x: bx + 14, y: ec - 34, width: bw - 28, height: 34, rx: 3}, gg), {fill: 'var(--c3)', fillOpacity: 0.12, stroke: 'var(--c3)', strokeWidth: 1});
  S(E('rect', {x: bx + 14, y: ev, width: bw - 28, height: 34, rx: 3}, gg), {fill: 'var(--c3)', fillOpacity: 0.55, stroke: 'var(--c3)', strokeWidth: 1});
  KTT(gg, bx + bw / 2, ec - 12, 'free (empty)', 'i-n', 'middle'); KTT(gg, bx + bw / 2, ev + 24, 'in bonds (full)', 'i-n', 'middle');
  KT.wire(gg, [[bx + 40, ec], [bx + 40, ev]]); KTT(gg, bx + 50, (ec + ev) / 2, on('gap'), 'i-l', 'start', onf('gap'));
  S(E('rect', {x: bx + bw - 46, y: ev - 0.0259 * sc0 - 0.5, width: 18, height: Math.max(2, 0.0259 * sc0)}, gg), {fill: 'var(--c2)'});
  KTT(gg, bx + bw - 50, ev - 10, `kT ${on('kt')}`, 'i-n', 'end', onf('kt'));
  inotes(L, lay, [
    {t: 'Why a chip is made of silicon', h: 1},
    {t: `Every outer electron is held in a bond; freeing one takes ${on('gap')}, ${on('kt43')} at room temperature: pure silicon has only ${on('ni')}.`, f: `${onf('gap')} ${onf('kt43')} ${onf('ni')}`},
    {t: `So the electrons a transistor switches come from the doped source, freed by only ${on('dop_e')} each.`, f: onf('dop_e')},
    {t: `Across a 6 nm fin lie ${on('si_pw')} of atoms.`, f: onf('si_pw'), ph: false},
  ]);
}, def: () => ({id: 'p.atom'}), kids: () => [{id: 'p.atom'}]});

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
/* the copied drawings' own transistors and gates lead on down the ladder: since 1 Oct every transistor-level drawing
   (DESIGN §1.5): the latch's inverters and transmission gates, the comparator's XNORs, the 6T cell and the SRAM's sense
   amplifier, precharge, write drivers and column mux, a mesh link's repeaters and level shifter, the crossing into a
   shire, the DQ pin's driver (on the ET die, N7) and, never to the N7 FinFET, the DRAM's cells (a DRAM process) */
const libLink = (id, map, kids, after) => {
  const N0 = NODES[id], b0 = N0.build;
  N0.build = (L, ap, p, P, d) => { b0(L, ap, p, P, d); Object.entries(map).forEach(([key, el]) => mlSibs(L, ap, key, () => ({el, tr: 'jump'}))); if (after) after(L, ap); };
  N0.def = () => kids[0]; N0.kids = () => kids;
};
const INV = {id: 'lib.inverter'}, FET = {id: 'lib.finfet'};
libLink('lib.latch', {inv1: INV, inv2: INV, ckinv: INV, tg1: {id: 'lib.mux2'}, tg2: {id: 'lib.mux2'}, sram6t: {id: 'lib.sram6t'}}, [INV, {id: 'lib.mux2'}],
  L => bitStates(L, {x: -138, y: 470, rail: 'v_min', e: 'latch_e'}));
libLink('lib.sram6t', {cell: FET, sa: FET, pre: FET, wd: FET, mux: FET, wl: INV, olat: {id: 'lib.latch'}}, [FET, INV],
  L => bitStates(L, {x: 712, y: 516, rail: 'v_sram', e: 'sram_e', w: 368}));   // (review of 1 Oct: at x 800, y 420 it covered the half-selected column)
libLink('l1d.cmp', {xnors: {id: 'lib.xor'}}, [{id: 'lib.xor'}]);
libLink('mesh.link.wire', {rep1: INV, rep2: INV, lsin: INV, ls: FET, sync: {id: 'lib.flipflop'}}, [INV, FET, {id: 'lib.flipflop'}]);
libLink('shire.meshstop.xing', {ls: FET, lvin: INV, sync: {id: 'lib.flipflop'}, fifo: {id: 'lib.flipflop'}}, [FET, INV, {id: 'lib.flipflop'}]);
libLink('memshire.phy.dq', {drv: FET, predrv: INV, rx: {id: 'lib.diffamp'}}, [FET, INV, {id: 'lib.diffamp'}]);
libLink('dram.cell', {cellA: {id: 'lib.dramcell'}, cellB: {id: 'lib.dramcell'}}, [{id: 'lib.dramcell'}]);
/* the minion's default way down is now the compute ladder: the vector unit, a lane, its multiply-add */
NODES.minion.def = () => ({id: 'vpu'});
NODES.minion.kids = () => [{id: 'vpu'}, {id: 'core'}, {id: 'tensor'}, {id: 'l1d'}];
NODES.shire.kids = p => [{id: 'shire.bank', k: String(L2X().bank)}, {id: 'shire.meshstop'}, {id: 'shire.uc'}, {id: 'shire.xbar'}, {id: 'shire.neigh', k: '0'}];
NODES.die.kids = () => [{id: 'shire', k: '32'}, {id: 'memshire', k: '0'}, {id: 'dram', k: `0.${DRX().ch}`}, {id: 'mesh'}, {id: 'pcie'}, {id: 'io'}, {id: 'die.metal'}];
/* the 2:1 multiplexer: two transmission gates, one open at a time */
bnode('lib.mux2', {draw: (L, ap) => {
  KT.frame(L, {title: 'A 2:1 multiplexer, in transistors', sub: 'two transmission gates (an NMOS and a PMOS side by side): S picks which input reaches the output', col: CC.logic, tags: [['generic', 'textbook']]});
  const tg = (y, lab, on) => {
    // (short gate leads, each labelled beside its own end: review of 1 Oct, the two 30-unit leads met in one line and
    // looked like one gate)
    const n = KT.mosH(L, 400, y + 40, {lead: 14}), p = KT.mosH(L, 400, y - 40, {p: true, down: true, lead: 14});
    KT.wire(L, [[200, y], [340, y], [340, y - 40], [370, y - 40]]); KT.wire(L, [[340, y], [340, y + 40], [370, y + 40]]); KT.jn(L, 340, y);
    KT.wire(L, [[430, y - 40], [460, y - 40], [460, y + 40], [430, y + 40]]); KT.jn(L, 460, y);
    KT.netLab(L, 192, y + 6, lab, 'end');
    KT.netLab(L, n.gate.x - 8, n.gate.y + 4, on ? 'S' : "S'", 'end'); KT.netLab(L, p.gate.x - 8, p.gate.y + 12, on ? "S'" : 'S', 'end');
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

/* ---- one silicon atom: its fourteen electrons in three shells (a picture: electrons are clouds), the four outer ones
   in the bonds; the nucleus a speck at the middle ---- */
bnode('p.atom', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'A silicon atom', sub: `${on('at_14')}: ${on('at_shells')}`, subf: onf('at_shells'),
    tags: [['documented', 'shells: NIST'], ['generic', 'a picture: electrons are clouds, not orbits']]});
  const p = lay.pic, c = {x: p.x + p.w / 2, y: p.y + p.h / 2}, R = Math.min(p.w, p.h) * 0.42;
  // the neighbours the four bonds reach: a tetrahedron, drawn flat
  const gb = ipt(L, ap, 'bonds', 'The four bonds to the neighbouring atoms', {title: 'The bonds', lead: 'The four outer electrons each pair with an electron of a neighbouring atom: four bonds pointing to the corners of a tetrahedron. They are what holds the crystal together, and what an electron must leave to conduct.', facts: ['p.atom.3', 'p.atom.5', 'si.bandgap']});
  [45, 135, 225, 315].forEach((a, i) => {
    const t = a * Math.PI / 180, q = {x: c.x + Math.cos(t) * R * 1.55, y: c.y + Math.sin(t) * R * 1.12};
    S(E('line', {x1: c.x + Math.cos(t) * R, y1: c.y + Math.sin(t) * R, x2: q.x, y2: q.y}, gb), {stroke: 'var(--c2)', strokeWidth: 5, strokeLinecap: 'round', strokeOpacity: 0.7});
    S(E('circle', {cx: q.x, cy: q.y, r: R * 0.16}, gb), {fill: 'color-mix(in srgb, var(--c1) 35%, var(--surface))', stroke: 'var(--ink-2)', strokeWidth: 1.5});
  });
  gb._box = {x: c.x - R * 1.6, y: c.y - R * 1.2, w: R * 3.2, h: R * 2.4};
  // the electron cloud and the shells
  const gs = ipt(L, ap, 'shells', 'The inner ten electrons: two shells held tight', {title: 'The inner electrons', lead: 'Ten electrons fill the first two shells, close around the nucleus and bound about 12 to 230 times more tightly than the outer four: chemistry and electronics never move them. They screen most of the nucleus\'s charge from the outer four.', facts: ['p.core.1', 'p.core.2', 'p.core.3', 'p.atom.2']});
  S(E('circle', {cx: c.x, cy: c.y, r: R}, gs), {fill: 'var(--c3)', fillOpacity: 0.07, stroke: 'none'});
  [[0.16, 2], [0.45, 8]].forEach(([f, n]) => {
    S(E('circle', {cx: c.x, cy: c.y, r: R * f}, gs), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '4 5'});
    for (let i = 0; i < n; i++) { const t = i / n * 2 * Math.PI + f; S(E('circle', {cx: c.x + Math.cos(t) * R * f, cy: c.y + Math.sin(t) * R * f, r: 5}, gs), {fill: 'var(--ink-2)'}); }
  });
  gs._box = {x: c.x - R * 0.5, y: c.y - R * 0.5, w: R, h: R};
  S(E('circle', {cx: c.x, cy: c.y, r: R, 'pointer-events': 'none'}, L), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '4 5'});
  // the four outer electrons: one ringed, the scene of an electron
  const gv = ipt(L, ap, 'valence', 'The four outer electrons, in the bonds', {title: 'The outer four', lead: 'Only these four take part in bonds and in electronics. Freeing one from its bond in the crystal takes the band gap, 1.12 eV; pulling it off a lone atom takes 8.15 eV.', facts: ['p.atom.1', 'p.atom.2', 'si.bandgap']});
  [45, 135, 225, 315].forEach(a => { const t = a * Math.PI / 180; S(E('circle', {cx: c.x + Math.cos(t) * R, cy: c.y + Math.sin(t) * R, r: 9}, gv), {fill: 'var(--c2)', stroke: 'var(--ink)', strokeWidth: 1.5}); });
  gv._box = {x: c.x - R - 12, y: c.y - R - 12, w: 2 * R + 24, h: 2 * R + 24};
  const t0 = 315 * Math.PI / 180, e0 = {x: c.x + Math.cos(t0) * R - 14, y: c.y + Math.sin(t0) * R - 14, w: 28, h: 28};
  const ge = ipt(L, ap, 'oneelectron', 'One electron', {node: 'p.electron', kid: {id: 'p.electron'}, seat: {x: e0.x + 9, y: e0.y + 9, w: 10, h: 10}, tr: 'jump', box: e0});
  S(E('circle', {class: 'shape', cx: e0.x + 14, cy: e0.y + 14, r: 13}, ge), {fill: 'transparent', stroke: 'var(--c2)', strokeWidth: 2.5, strokeDasharray: '5 4'});
  KTT(L, e0.x + 34, e0.y + 4, 'an electron', 'i-l halo');
  // the nucleus, a speck at the middle
  const nb = {x: c.x - 8, y: c.y - 8, w: 16, h: 16};
  const gn = ipt(L, ap, 'nucleus', 'The nucleus: a speck at the middle', {node: 'p.nucleus', kid: {id: 'p.nucleus'}, seat: nb, box: nb});
  S(E('circle', {class: 'shape', cx: c.x, cy: c.y, r: 6}, gn), {fill: 'var(--c5)', stroke: 'var(--ink)', strokeWidth: 1.5});
  S(E('circle', {cx: c.x, cy: c.y, r: 26, 'pointer-events': 'all'}, gn), {fill: 'transparent'});
  KTT(L, c.x, c.y + R * 0.16 + 26, 'the nucleus (drawn far too big)', 'i-n halo', 'middle');
  inotes(L, lay, [
    {t: 'Fourteen electrons, four that matter', h: 1},
    {t: `The outer four bond and conduct: pulling one off a lone atom costs ${on('at_ion')} eV; the first of the inner ten, ${on('at_ion5')}.`, f: onf('at_ion')},
    {t: `To scale, the nucleus would be a speck: the atom's share of the crystal is ${on('at_29k')} wider.`, f: onf('at_29k')},
    {t: 'The rings are a picture: electrons are clouds of probability, densest at these radii, not little balls on orbits.', f: 'p.core.4', ph: false},
  ]);
}, def: () => ({id: 'p.nucleus'}), kids: () => [{id: 'p.nucleus'}, {id: 'p.electron'}]});

/* ---- the silicon-28 nucleus: 14 protons and 14 neutrons, packed ---- */
bnode('p.nucleus', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'The silicon-28 nucleus', sub: `${on('nu_pn')}, ${on('nu_size')} across: ${on('nu_mass')} of the atom's mass`, subf: `${onf('nu_pn')} ${onf('nu_size')} ${onf('nu_mass')}`,
    tags: [['documented', 'radius: measured (IAEA)'], ['generic', 'the packing: a picture']]});
  const p = lay.pic, c = {x: p.x + p.w / 2, y: p.y + p.h / 2}, R = Math.min(p.w, p.h) * 0.4, r = R * 0.205;
  // 28 places: the hexagonal grid's points nearest the middle
  const pts = [];
  for (let i = -6; i <= 6; i++) for (let j = -6; j <= 6; j++) { const x = (i + (j & 1) * 0.5) * 1.72 * r, y = j * 1.5 * r; pts.push({x, y, d: Math.hypot(x, y)}); }
  pts.sort((a, b) => a.d - b.d || a.x - b.x);
  const at = pts.slice(0, 28);
  const gn = ipt(L, ap, 'nucleons', 'Fourteen protons and fourteen neutrons', {title: 'Protons and neutrons', lead: sc('p.nucleus').blurb, facts: ['p.nucleus.1', 'p.nucleus.5', 'p.nucleus.7', 'p.nucleus.8'], box: {x: c.x - R, y: c.y - R, w: 2 * R, h: 2 * R}});
  S(E('circle', {cx: c.x, cy: c.y, r: R * 1.04}, gn), {fill: 'var(--c5)', fillOpacity: 0.06, stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '5 5'});
  let pi = null;
  at.forEach((q, i) => {
    const prot = i % 2 === 0, x = c.x + q.x, y = c.y + q.y;
    S(E('circle', {cx: x, cy: y, r: r * 1.02}, gn), {fill: prot ? 'color-mix(in srgb, var(--c2) 70%, var(--surface))' : 'color-mix(in srgb, var(--ink-2) 35%, var(--surface))', stroke: 'var(--ink)', strokeWidth: 1.25});
    if (prot && pi == null && q.d > 0) pi = {x, y};
  });
  const pb = {x: pi.x - r, y: pi.y - r, w: 2 * r, h: 2 * r};
  const gp = ipt(L, ap, 'proton', 'One proton', {node: 'p.nucleon', kid: {id: 'p.nucleon'}, seat: pb, tr: 'jump', box: pb});
  S(E('circle', {class: 'shape', cx: pi.x, cy: pi.y, r: r * 1.15}, gp), {fill: 'transparent', stroke: 'var(--c2)', strokeWidth: 3});
  KTT(L, pi.x + r * 1.3, pi.y - r * 1.2, 'a proton', 'i-l halo');
  const lx = PH ? p.x : c.x + R + 20;
  [['color-mix(in srgb, var(--c2) 70%, var(--surface))', 'proton (+)'], ['color-mix(in srgb, var(--ink-2) 35%, var(--surface))', 'neutron']].forEach(([f, t], i) => {
    S(E('circle', {cx: lx + 12, cy: p.y + 20 + i * 34, r: 11, 'pointer-events': 'none'}, L), {fill: f, stroke: 'var(--ink)', strokeWidth: 1.25});
    KTT(L, lx + 30, p.y + 27 + i * 34, t, 'i-n');
  });
  inotes(L, lay, [
    {t: 'Almost all the mass, almost none of the room', h: 1},
    {t: `The strong force binds them with ${on('nu_bind')}: about a million times a chemical bond, which is why no chip ever changes a nucleus.`, f: `${onf('nu_bind')} p.nucleus.8`},
    {t: `Its measured charge radius is ${on('nu_rms')} fm; a nucleus has a soft edge, so any size is a convention.`, f: `${onf('nu_rms')} size.p.nucleus`},
  ]);
}, def: () => ({id: 'p.nucleon'}), kids: () => [{id: 'p.nucleon'}]});

/* ---- a proton: three quarks in a field of gluons (a picture: quarks are not little balls) ---- */
bnode('p.nucleon', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'A proton: three quarks', sub: `${on('pr_uud')}, bound by gluons; radius ${on('pr_r')} fm, mass ${on('pr_m')}`, subf: `${onf('pr_uud')} ${onf('pr_r')} ${onf('pr_m')}`,
    tags: [['documented', 'measured (CODATA, PDG)'], ['generic', 'a picture: quarks are not little balls']]});
  const p = lay.pic, c = {x: p.x + p.w / 2, y: p.y + p.h / 2}, R = Math.min(p.w, p.h) * 0.42;
  const gf = ipt(L, ap, 'field', 'The gluon field: most of the proton\'s mass', {title: 'The gluon field', lead: 'The quarks\' own masses are about 1% of the proton\'s. The rest is energy: the quarks\' motion and the field of gluons that binds them (E = mc²).', facts: ['p.quark.3', 'p.quark.4', 'p.quark.6', 'p.quark.8']});
  S(E('circle', {cx: c.x, cy: c.y, r: R}, gf), {fill: 'var(--c7)', fillOpacity: 0.10, stroke: 'var(--c7)', strokeWidth: 1.5, strokeDasharray: '6 5'});
  const q = [[-90, 'u', 'var(--c2)'], [30, 'u', 'var(--c3)'], [150, 'd', 'var(--c4)']].map(([a, t, col]) => ({x: c.x + Math.cos(a * Math.PI / 180) * R * 0.45, y: c.y + Math.sin(a * Math.PI / 180) * R * 0.45, t, col}));
  for (let i = 0; i < 3; i++) { const a = q[i], b = q[(i + 1) % 3], n = 9; let d = `M${a.x},${a.y}`; for (let j = 1; j <= n; j++) { const f = j / n, x = a.x + (b.x - a.x) * f, y = a.y + (b.y - a.y) * f, s = (j % 2 ? 1 : -1) * 9, nx = -(b.y - a.y), ny = b.x - a.x, l = Math.hypot(nx, ny); d += ` Q${x - (b.x - a.x) / n / 2 + nx / l * s},${y - (b.y - a.y) / n / 2 + ny / l * s} ${x},${y}`; } S(E('path', {d}, gf), {fill: 'none', stroke: 'var(--c7)', strokeWidth: 2}); }
  gf._box = {x: c.x - R, y: c.y - R, w: 2 * R, h: 2 * R};
  const gq = ipt(L, ap, 'quarks', 'Two up quarks and a down quark', {title: 'The three quarks', lead: 'Up quarks carry +2/3 of the electron\'s charge (with the opposite sign), down quarks -1/3: two ups and a down make the proton\'s +1. Their colours stand for the strong force\'s "colour charge", not colours.', facts: ['p.nucleon.4', 'p.quark.3', 'p.quark.7']});
  q.forEach(o => { S(E('circle', {cx: o.x, cy: o.y, r: 16}, gq), {fill: o.col, stroke: 'var(--ink)', strokeWidth: 1.5}); KTT(gq, o.x, o.y + 7, o.t, 'i-l', 'middle'); });
  gq._box = {x: c.x - R * 0.6, y: c.y - R * 0.6, w: R * 1.2, h: R * 1.2};
  const qb = {x: q[2].x - 18, y: q[2].y - 18, w: 36, h: 36};
  const gk = ipt(L, ap, 'onequark', 'One quark', {node: 'p.quark', kid: {id: 'p.quark'}, seat: {x: qb.x + 13, y: qb.y + 13, w: 10, h: 10}, tr: 'jump', box: qb});
  S(E('circle', {class: 'shape', cx: q[2].x, cy: q[2].y, r: 24}, gk), {fill: 'transparent', stroke: 'var(--c2)', strokeWidth: 2.5, strokeDasharray: '5 4'});
  KTT(L, q[2].x - 30, q[2].y + 46, 'a down quark', 'i-l halo', 'middle');
  inotes(L, lay, [
    {t: 'Mass from energy', h: 1},
    {t: `The quarks themselves weigh ${on('qk_u')} MeV (up) and ${on('qk_d')} MeV (down): together ${on('pr_1pc')}'s mass. The rest is the energy inside it.`, f: onf('qk_u')},
    {t: 'A quark is never found alone: pull one out and the energy makes new quarks.', f: 'p.quark.7'},
  ]);
}, def: () => ({id: 'p.quark'}), kids: () => [{id: 'p.quark'}]});

/* ---- a quark, and an electron: no size has ever been measured; the disc is only the limit ---- */
function pointScene(L, ap, o) {
  const lay = ihead(L, {title: o.title, sub: o.sub, subf: o.subf, tags: [['documented', 'the limit: measured'], ['generic', 'the point: as far as anyone can tell']]});
  const p = lay.pic, c = {x: p.x + p.w / 2, y: p.y + p.h / 2}, R = Math.min(p.w, p.h) * 0.42;
  const gb = ipt(L, ap, 'bound', 'The limit: if it has a size, it is smaller than this', {title: 'The limit, not the particle', lead: o.boundLead, facts: o.facts});
  S(E('circle', {cx: c.x, cy: c.y, r: R}, gb), {fill: 'var(--c4)', fillOpacity: 0.05, stroke: 'var(--c4)', strokeWidth: 2, strokeDasharray: '9 7'});
  KTT(gb, c.x, c.y - R - 12, o.boundLab, 'i-l halo', 'middle', o.boundF);
  gb._box = {x: c.x - R, y: c.y - R, w: 2 * R, h: 2 * R};
  const pb = {x: c.x - 14, y: c.y - 14, w: 28, h: 28};
  const gp = ipt(L, ap, 'point', o.pointLab, {node: 'p.planck', kid: {id: 'p.planck'}, seat: {x: pb.x + 9, y: pb.y + 9, w: 10, h: 10}, tr: 'jump', box: pb, info: {title: o.pointTitle, lead: o.pointLead, facts: o.facts}});
  S(E('circle', {class: 'shape', cx: c.x, cy: c.y, r: 4}, gp), {fill: 'var(--ink)'});
  S(E('circle', {cx: c.x, cy: c.y, r: 30, 'pointer-events': 'all'}, gp), {fill: 'transparent'});
  KTT(L, c.x + 16, c.y + 34, o.pointLab, 'i-n halo');
  inotes(L, lay, o.notes);
}
bnode('p.quark', {pv: () => IVIEW(), draw: (L, ap) => pointScene(L, ap, {title: 'A quark: as far as we know, a point', sub: `no size measured: a radius under ${on('qk_b')}`, subf: onf('qk_b'),
  boundLab: `the limit: ${on('qk_b')}`, boundF: onf('qk_b'), boundLead: sc('p.quark').blurb, facts: sc('p.quark').facts,
  pointLab: 'the quark: a point', pointTitle: 'A quark', pointLead: sc('p.quark').blurb,
  notes: [{t: 'No size found', h: 1}, {t: `The proton is at least ${on('qk_1955')} wider than a quark could be.`, f: onf('qk_1955')},
    {t: `Below this lie ${on('pl_16')} that no experiment has reached, down to the Planck length.`, f: onf('pl_16')}]}),
  def: () => ({id: 'p.planck'}), kids: () => [{id: 'p.planck'}]});
bnode('p.electron', {pv: () => IVIEW(), draw: (L, ap) => pointScene(L, ap, {title: 'An electron: as far as we know, a point', sub: `no size measured: a radius under ${on('el_b')}`, subf: onf('el_b'),
  boundLab: `the limit: ${on('el_b')}`, boundF: onf('el_b'), boundLead: sc('p.electron').blurb, facts: sc('p.electron').facts,
  pointLab: 'the electron: a point', pointTitle: 'An electron', pointLead: sc('p.electron').blurb,
  notes: [{t: 'What carries every current in the chip', h: 1}, {t: `Its charge is ${on('el_q')}, exactly: it defines the coulomb.`, f: onf('el_q')},
    {t: `It is round: its charge sits within ${on('el_edm')} of its centre (the limit on its dipole moment).`, f: onf('el_edm')}]}),
  def: () => ({id: 'p.planck'}), kids: () => [{id: 'p.planck'}]});

/* ---- the Planck length: a ruler from the proton down to where known physics stops ---- */
bnode('p.planck', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'The Planck length: where known physics stops', sub: `${on('pl_l')}: below the quark's limit lie ${on('pl_16')} nobody has explored`, subf: `${onf('pl_l')} ${onf('pl_16')}`,
    tags: [['documented', 'CODATA'], ['hypothesis', 'a smallest length? open']]});
  const p = lay.pic, top = -14, bot = -35, x = p.x + (PH ? 130 : 160), y0 = p.y + 10, y1 = p.y + p.h - 20, yl = e => y0 + (top - e) / (top - bot) * (y1 - y0);
  const gr = ipt(L, ap, 'ruler', 'A ruler of sizes, from a proton down to the Planck length', {title: 'Twenty powers of ten', lead: sc('p.planck').blurb, facts: sc('p.planck').facts, box: {x: x - 20, y: y0, w: 40, h: y1 - y0}});
  S(E('line', {x1: x, y1: y0, x2: x, y2: y1}, gr), {stroke: 'var(--ink)', strokeWidth: 3});
  for (let e = top; e >= bot; e--) {
    const y = yl(e); S(E('line', {x1: x - 10, y1: y, x2: x + 10, y2: y}, gr), {stroke: 'var(--ink-2)', strokeWidth: 1.5});
    if ((e - bot) % (PH ? 3 : 2) === 0) KTT(gr, x - 18, y + 6, `10${String(e).split('').map(ch => SUP[ch]).join('')} m`, 'i-n', 'end');
  }
  const mark = (e, lab, f, col, dy) => { const y = yl(e); S(E('circle', {cx: x, cy: y, r: 7, 'pointer-events': 'none'}, L), {fill: col || 'var(--c2)', stroke: 'var(--ink)', strokeWidth: 1.25}); KTT(L, x + 22, y + 6 + (dy || 0), lab, 'i-l halo', 'start', f); };
  mark(Math.log10(1.68e-15), 'a proton', 'p.nucleon.1');
  // (on a phone the two limits, 1.3 powers of ten apart, are labelled apart: review of 1 Oct, they collided)
  const gapQE = yl(Math.log10(4e-20)) - yl(Math.log10(8.6e-19)), sep = Math.max(0, (PH ? 40 : 30) - gapQE) / 2;
  mark(Math.log10(8.6e-19), `a quark's limit: ${on('qk_b')}`, onf('qk_b'), null, -sep);
  mark(Math.log10(4e-20), `an electron's limit: ${on('el_b')}`, onf('el_b'), null, sep);
  const gu = ipt(L, ap, 'unexplored', 'Sixteen powers of ten that no experiment has reached', {title: 'Unexplored', lead: 'Between the smallest limit any experiment has set and the Planck length lie some sixteen powers of ten: nobody knows what is there.', facts: ['p.planck.3', 'p.planck.4']});
  const ua = yl(Math.log10(4e-20)) + 18, ub = yl(Math.log10(1.6e-35)) - 18;
  S(E('rect', {x: x + 18, y: ua, width: PH ? 300 : 420, height: ub - ua, rx: 8}, gu), {fill: 'var(--c4)', fillOpacity: 0.06, stroke: 'var(--c4)', strokeWidth: 1.25, strokeDasharray: '6 6'});
  KTT(gu, x + 34, (ua + ub) / 2 + 6, `unexplored: ${on('pl_16')}`, 'i-l');
  gu._box = {x: x + 18, y: ua, w: PH ? 300 : 420, h: ub - ua};
  mark(Math.log10(1.616255e-35), `the Planck length, ${on('pl_l')}`, onf('pl_l'), 'var(--c7)');
  // (the loop, ladder-core.js: Up from the top of the ladder shrinks it into this mark)
  ap.loopAt = {x, y: yl(Math.log10(1.616255e-35))};
  inotes(L, lay, [
    {t: 'The floor', h: 1},
    {t: 'Here gravity, quantum mechanics and the speed of light meet: space and time themselves would need a quantum description that nobody has yet.', f: 'p.planck.1 p.planck.4'},
    {t: 'Whether anything can be smaller is open (a hypothesis, not a measurement).', f: 'p.planck.4'},
    {t: `From here to the edge of what we can see is ${on('pl_617')}.`, f: onf('pl_617'), ph: false},
  ]);
}});

/* ---- a dopant: a phosphorus atom in a silicon site, its fifth electron loosely held ---- */
bnode('p.dopant', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'A dopant: phosphorus in the crystal', sub: `its fifth electron is held by only ${on('dp_p')}: at room temperature it is free`, subf: onf('dp_p'),
    tags: [['documented', 'binding: Ioffe'], ['generic', 'the crystal drawn flat']]});
  const p = lay.pic, n = PH ? 4 : 5, a = Math.min(p.w, p.h) / (n + 0.4), x0 = p.x + (p.w - (n - 1) * a) / 2, y0 = p.y + (p.h - (n - 1) * a) / 2, mid = (n - 1) >> 1;
  const gl = ipt(L, ap, 'lattice', 'The silicon around it', {title: 'The crystal, drawn flat', lead: 'Each silicon atom bonds to four neighbours (in three dimensions, the corners of a tetrahedron; drawn flat here). The phosphorus atom takes one silicon atom\'s place.', facts: ['si.lattice', 'p.dopant.3']});
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    const x = x0 + i * a, y = y0 + j * a;
    if (i < n - 1) S(E('line', {x1: x, y1: y, x2: x + a, y2: y}, gl), {stroke: 'var(--ink-2)', strokeWidth: 2});
    if (j < n - 1) S(E('line', {x1: x, y1: y, x2: x, y2: y + a}, gl), {stroke: 'var(--ink-2)', strokeWidth: 2});
  }
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== mid || j !== mid) S(E('circle', {cx: x0 + i * a, cy: y0 + j * a, r: a * 0.16}, gl), {fill: 'color-mix(in srgb, var(--c1) 40%, var(--surface))', stroke: 'var(--ink)', strokeWidth: 1.25});
  gl._box = {x: x0 - a / 2, y: y0 - a / 2, w: n * a, h: n * a};
  const c = {x: x0 + mid * a, y: y0 + mid * a};
  const ge = ipt(L, ap, 'fifth', 'The fifth electron: loosely held, free at room temperature', {title: 'The spare electron', lead: sc('p.dopant').blurb, facts: ['p.dopant.1', 'p.dopant.2', 'dope.donor-acceptor', 'el.kt']});
  S(E('circle', {cx: c.x, cy: c.y, r: a * 1.35}, ge), {fill: 'var(--c2)', fillOpacity: 0.07, stroke: 'var(--c2)', strokeWidth: 2, strokeDasharray: '6 6'});
  S(E('circle', {cx: c.x + a * 1.35 * Math.cos(-0.6), cy: c.y + a * 1.35 * Math.sin(-0.6), r: 9}, ge), {fill: 'var(--c2)', stroke: 'var(--ink)', strokeWidth: 1.5});
  ge._box = {x: c.x - a * 1.4, y: c.y - a * 1.4, w: a * 2.8, h: a * 2.8};
  const gp = ipt(L, ap, 'phos', 'The phosphorus atom: five outer electrons, four in bonds', {title: 'Phosphorus', lead: 'Phosphorus has five outer electrons, one more than the four bonds need. Boron, used for p-type transistors, has three: it leaves a gap, a hole, that carries current the other way.', facts: ['p.dopant.1', 'dope.n-sd', 'dope.p-sd', 'dope.donor-acceptor']});
  S(E('circle', {cx: c.x, cy: c.y, r: a * 0.2}, gp), {fill: 'var(--c5)', stroke: 'var(--ink)', strokeWidth: 2});
  KTT(gp, c.x, c.y + 8, 'P', 'i-l', 'middle');
  gp._box = {x: c.x - a * 0.25, y: c.y - a * 0.25, w: a * 0.5, h: a * 0.5};
  KTT(L, c.x + a * 0.3, c.y - a * 1.5, 'its fifth electron', 'i-l halo');
  inotes(L, lay, [
    {t: 'How the source and drain conduct', h: 1},
    {t: `Freeing the spare electron takes ${on('dp_p')}, about twice the thermal energy at room temperature: nearly every dopant in a silicon site gives its electron up.`, f: `${onf('dp_p')} p.dopant.2`},
    {t: `In the source and drain up to ${on('dop_sd')} phosphorus atoms per cm³, ${on('sd_29')}; so many crowd in that only about ${on('sd_13')} is active.`, f: `${onf('dop_sd')} ${onf('sd_29')}`},
    {t: 'p-type transistors use boron (three outer electrons) in silicon-germanium instead.', f: 'dope.p-sd', ph: false},
  ]);
}});

/* ---- a DRAM cell in section: one transistor and one capacitor, on a DRAM process (not TSMC N7) ---- */
bnode('lib.dramcell', {pv: () => IVIEW(), draw: (L, ap) => {
  const lay = ihead(L, {title: 'A DRAM cell in section: a transistor and a capacitor', sub: 'generic: a DRAM process, not TSMC N7; this card\'s DRAM generation is not known', subf: 'size.lib.dramcell',
    tags: [['generic', 'textbook'], ['unknown', 'the card\'s DRAM: asked']], col: 'var(--c3)', sw: 1});
  const p = lay.pic, k = Math.min(p.w / 760, p.hd / 580), X = v => p.x + v * k, Y = v => p.y + 14 + v * k;
  const gs = ipt(L, ap, 'si', 'The silicon underneath', {node: 'lib.si', kid: {id: 'lib.si'}, seat: {x: X(60), y: Y(470), w: 40 * k, h: 40 * k}, tr: 'jump', box: {x: X(0), y: Y(440), w: 700 * k, h: 120 * k},
    info: {title: 'The silicon', lead: 'A DRAM is made on its own process, not TSMC N7, but its transistors are silicon too: the same crystal, the same band gap.', facts: ['si.lattice', 'si.bandgap', 'size.lib.dramcell']}});
  S(E('rect', {class: 'shape', x: X(0), y: Y(440), width: 700 * k, height: 120 * k}, gs), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 1.5});
  KTT(gs, X(14), Y(540), 'silicon', 'i-n');
  const gt = ipt(L, ap, 'access', 'The access transistor: its gate is the wordline', {title: 'The access transistor', lead: 'Its gate is the wordline. Raised, it connects the capacitor to the bitline, to be read or written; lowered, it isolates the capacitor, which must then hold its charge on its own.', facts: ['el.dram-cell', 'ml:dram:gen.cell'].filter(f => F[f])});
  S(E('rect', {x: X(150), y: Y(440), width: 110 * k, height: 40 * k, rx: 4}, gt), {fill: 'var(--c5)', fillOpacity: 0.3, stroke: 'var(--c5)', strokeWidth: 1.25});
  S(E('rect', {x: X(370), y: Y(440), width: 110 * k, height: 40 * k, rx: 4}, gt), {fill: 'var(--c5)', fillOpacity: 0.3, stroke: 'var(--c5)', strokeWidth: 1.25});
  S(E('rect', {x: X(270), y: Y(380), width: 90 * k, height: 60 * k, rx: 4}, gt), {fill: 'var(--c1)', fillOpacity: 0.4, stroke: 'var(--c1)', strokeWidth: 1.5});
  KTT(gt, X(315), Y(372), PH ? 'wordline' : 'wordline (gate)', 'i-n halo', 'middle');
  gt._box = {x: X(150), y: Y(380), w: 330 * k, h: 100 * k};
  const gb = ipt(L, ap, 'bitline', 'The bitline and its contact', {title: 'The bitline', lead: 'A wire shared by the cells of a column: reading, the cell\'s small charge nudges it above or below half the array voltage, and a sense amplifier decides which.', facts: ['ml:dram:gen.sense', 'el.dram-cell'].filter(f => F[f])});
  S(E('rect', {x: X(185), y: Y(240), width: 40 * k, height: 200 * k}, gb), {fill: 'var(--ink-2)', fillOpacity: 0.35});
  S(E('rect', {x: X(20), y: Y(220), width: 260 * k, height: 26 * k, rx: 3}, gb), {fill: 'var(--c4)', fillOpacity: 0.45, stroke: 'var(--c4)', strokeWidth: 1.25});
  KTT(gb, X(24), Y(210), 'bitline', 'i-n');
  gb._box = {x: X(20), y: Y(220), w: 260 * k, h: 220 * k};
  // the capacitor: a tall cylinder, far taller than wide; its charge is the bit
  const gc = ipt(L, ap, 'cap', 'The storage capacitor: its charge is the bit', {title: 'The capacitor', lead: sc('lib.dramcell').blurb, facts: ['el.dram-cell', 'el.dram-leak']});
  const cx = X(395), cw = 80 * k, ct = Y(20), cb = Y(430);
  S(E('rect', {x: X(405), y: cb, width: 40 * k, height: 10 * k}, gc), {fill: 'var(--ink-2)', fillOpacity: 0.35});
  S(E('rect', {class: 'shape', x: cx, y: ct, width: cw, height: cb - ct, rx: 10}, gc), {fill: 'var(--surface)', stroke: 'var(--ink)', strokeWidth: 2});
  const SA = E('g', {class: 'st-a', 'pointer-events': 'none'}, gc), SB = E('g', {class: 'st-b', 'pointer-events': 'none'}, gc);
  S(E('rect', {x: cx + 6, y: ct + 10, width: cw - 12, height: cb - ct - 16, rx: 6}, SA), {fill: 'var(--c2)', fillOpacity: 0.55});
  S(E('rect', {x: cx + 6, y: ct + (cb - ct) * 0.45, width: cw - 12, height: (cb - ct) * 0.55 - 6, rx: 6}, SB), {fill: 'var(--c2)', fillOpacity: 0.4});
  E('path', {class: 'w', d: `M${cx + cw + 12},${cb - 40}C${cx + cw + 60},${cb - 20} ${cx + cw + 60},${cb + 30} ${cx + cw + 30},${cb + 60}`}, SB);
  E('path', {class: 'w', d: `M${cx + cw + 22},${cb + 52}L${cx + cw + 30},${cb + 60}L${cx + cw + 40},${cb + 50}`}, SB);
  S(E('rect', {x: cx - 18, y: ct - 16, width: cw + 36, height: 16 * k + 8, rx: 4}, gc), {fill: 'var(--c3)', fillOpacity: 0.45});
  KTT(L, cx + cw / 2, ct - 22, 'plate', 'i-n', 'middle');
  KTT(SA, cx + cw + 16, ct + 60, 'charged: a 1', 'i-l halo');
  KTT(SB, cx + cw + 16, ct + 60, '32 ms later: leaking', 'i-l halo');
  gc._box = {x: cx - 18, y: ct - 16, w: cw + 36, h: cb - ct + 16};
  stateSwitch(L, lay.sw.x, lay.sw.y, {lab: 'The DRAM cell\'s charge', btn: ['Just written · 32 ms later (G)', '32 ms later · just written (G)'],
    say: ['The cell just written: charged.', 'The cell 32 ms later: some charge has leaked; it must be refreshed.']}, {w: SWW()});
  inotes(L, lay, [
    {t: 'A bit with no circuit to hold it', h: 1},
    {a: `Charged, the capacitor holds ${on('dram_e')}: fifty times an SRAM bit's, because nothing restores it.`, b2: `It leaks: to last the ${on('dram_ms')} refresh window it may lose only ${on('dram_fa')}. Every row is read and rewritten in time.`, f: 'el.dram-cell el.dram-leak'},
    {t: 'An SRAM bit is held by two inverters that keep restoring it, so it needs no refresh, but takes six transistors.', f: 'el.sram-electrons'},
  ]);
}, def: () => ({id: 'lib.si'}), kids: () => [{id: 'lib.si'}]});

/* ---- the ring of sizes (the wrap): a picture of every size at once, the smallest meeting the largest; on the night
   sky like the levels in space. Not further out in space: the readout shows no size, and the camera reaches it by a
   cross-fade, never a zoom. The idea is Sheldon Glashow's, as drawn by Primack and Abrams (2006); this drawing is the
   page's own. ---- */
const RINGD = D.ring || {ticks: [], epochs: []};
const RG = () => (PH ? {cx: 510, cy: 270, r: 165} : {cx: 330, cy: 330, r: 255});
const ringAng = m => { const lo = Math.log10(1.616255e-35), hi = Math.log10(8.74e26); return (-98 - (Math.log10(m) - lo) / (hi - lo) * 344) * Math.PI / 180; };
onode('p.wrap', {kid: null, pv: () => opv(), build: (L, ap) => {
  obd(L, true);
  otitle(L, 'The ring of sizes', 'a picture, not a place', 'not further out in space: every size at once; the links across it are physics');
  const G = RG(), at = (m, rr) => ({x: G.cx + Math.cos(ringAng(m)) * (rr || G.r), y: G.cy + Math.sin(ringAng(m)) * (rr || G.r)});
  // the serpent: thin at its tail (the Planck length), thick at its head (the observable universe)
  const gs = opart(L, 'ring', 'The ring: every size from the Planck length to the observable universe: details', {title: 'Every size at once', kick: 'Ring of sizes · part', lead: (OSC['p.wrap'] || {}).blurb, facts: ['p.wrap.1', 'p.wrap.2', 'p.wrap.3', 'ring.mid', 'p.planck.5']});
  const N = 72, lo = Math.log10(1.616255e-35), hi = Math.log10(8.74e26);
  for (let i = 0; i < N; i++) {
    const m0 = Math.pow(10, lo + (hi - lo) * i / N), m1 = Math.pow(10, lo + (hi - lo) * (i + 1) / N), a = at(m0), b = at(m1);
    S(E('line', {x1: a.x, y1: a.y, x2: b.x, y2: b.y}, gs), {stroke: '#9fb0dc', strokeWidth: 3 + 17 * i / N, strokeLinecap: 'round', strokeOpacity: 0.85});
  }
  const hd = at(8.74e26);
  S(E('circle', {cx: hd.x, cy: hd.y, r: 16}, gs), {fill: '#cfd8ff'});
  S(E('circle', {cx: G.cx, cy: G.cy, r: G.r + 26, 'pointer-events': 'stroke'}, gs), {fill: 'none', stroke: 'transparent', strokeWidth: 60});
  E('circle', {class: 'ring', cx: G.cx, cy: G.cy, r: G.r + 14}, gs);
  // the ticks: the ladder's own scales at their sizes
  const gt = E('g', {class: 'rticks', 'pointer-events': 'none'}, L);
  let lastA = null, stag = 0, inLow = 0;
  RINGD.ticks.forEach((t, i) => {
    const ang = ringAng(t.m), a = at(t.m, G.r - 16), b = at(t.m, G.r + 16);
    S(E('line', {x1: a.x, y1: a.y, x2: b.x, y2: b.y}, gt), {stroke: '#ffd27a', strokeWidth: 2.5});
    if (i === 0 || i === RINGD.ticks.length - 1) return;   // the ends are named at the mouth
    // (ticks close together: every other one named inside the ring, beside its tick; review of 1 Oct, a second row
    // further out left "Fin" far from its tick and ran "L1 cache" into "Chip" on a phone)
    stag = lastA != null && Math.abs(ang - lastA) < (PH ? 0.3 : 0.2) ? (stag + 1) % 2 : 0; lastA = ang;
    const inside = stag === 1, q = at(t.m, inside ? G.r - 30 : G.r + 30), right = Math.cos(ang) > 0.15, left = Math.cos(ang) < -0.15, low = Math.sin(ang) > 0.9;
    const nm = NODES[t.id] ? shortOf({id: t.id}) : t.id, lowIn = low && inside ? inLow++ : 0;
    T(gt, q.x, q.y + 6 + (low ? (inside ? -12 - 28 * (lowIn % 2) : 12) : 0), nm, 'o-s', inside ? (right ? 'end' : left ? 'start' : 'middle') : (right ? 'start' : left ? 'end' : 'middle'), t.f || null);
  });
  // the middle of all sizes, opposite the mouth: named at the ring's centre, a dotted line to its tick (review of 1 Oct:
  // beside the tick it crossed the band)
  const mm = at(1.2e-4, G.r - 22);
  S(E('line', {x1: G.cx, y1: G.cy + 12, x2: mm.x, y2: mm.y, 'pointer-events': 'none'}, L), {stroke: '#ffd27a', strokeWidth: 1.5, strokeDasharray: '3 5', strokeOpacity: 0.7});
  T(L, G.cx, G.cy, `the middle: ${on('ring_mid')}`, 'o-s ohalo', 'middle', onf('ring_mid'));
  // the mouth: the head (the observable universe) meets the tail's tip (the Planck length); the marker runs across it
  // (each mark an eighth of the frame wide: the other scene grows from it, and the ring is never zoomed more than 8 times)
  const tl = at(1.616255e-35), mk = VB.w / 16, am = at(2.352e-10);
  ap.headBox = {x: hd.x - mk, y: hd.y - mk * VB.h / VB.w, w: 2 * mk, h: 2 * mk * VB.h / VB.w};
  ap.tailBox = {x: tl.x - mk, y: tl.y - mk * VB.h / VB.w, w: 2 * mk, h: 2 * mk * VB.h / VB.w};
  // (a way back in to an atom: the marker runs from the head across the mouth, then up the tail to the atom's tick, where
  // the atom grows from; since 1 Oct evening Up from the ring takes the tail's tip, the Planck length)
  ap.atomBox = {x: am.x - mk, y: am.y - mk * VB.h / VB.w, w: 2 * mk, h: 2 * mk * VB.h / VB.w};
  const run = E('path', {class: 'rrun', d: `M${hd.x},${hd.y} A${G.r},${G.r} 0 0 0 ${tl.x},${tl.y} A${G.r},${G.r} 0 0 0 ${am.x},${am.y}`, 'pointer-events': 'none'}, L);
  const runPl = 2 * Math.PI * G.r * 16 / 360, runLen = runPl + 2 * Math.PI * G.r * Math.abs(ringAng(1.616255e-35) - ringAng(2.352e-10)) / (2 * Math.PI) + 4;
  run.setAttribute('stroke-dasharray', `${runLen} ${runLen}`); run.style.strokeDashoffset = runLen + 'px';
  ap.run = run; ap.runLen = runLen; ap.runLenPl = runPl + 4;
  S(E('circle', {cx: am.x, cy: am.y, r: 9, 'pointer-events': 'none'}, L), {fill: '#ffd27a', stroke: '#1d2540', strokeWidth: 2});
  T(L, hd.x + 18, hd.y - 18, 'the observable universe', 'o-s ohalo', 'start');
  T(L, tl.x - 18, tl.y - 18, 'the Planck length', 'o-s ohalo', 'end');
  // looking out is looking back: the epochs, as times and temperatures, never as sizes
  const ex = PH ? 150 : 740, ey = PH ? 520 : 60, lh = PH ? 30 : 27;
  const ge = opart(L, 'epochs', 'Looking out is looking back: details', {title: 'Looking out is looking back', kick: 'Ring of sizes · physics', lead: 'The farther out we look, the older the light: at the edge of what we can see the universe was young, hot and small, and before that a sea of quarks. The largest scale and the smallest meet in the early universe.', facts: ['e.cmb.1', 'e.cmb.2', 'e.cmb.3', 'e.bbn.1', 'e.qcd.1', 'e.qcd.2', 'e.qcd.4', 'e.ew.2', 'e.planck.1', 'e.cmb.6']});
  T(ge, ex, ey, 'Looking out is looking back:', 'o-l');
  RINGD.epochs.forEach((e, i) => T(ge, ex, ey + (i + 1) * lh, `${e.lab}: ${on(e.num)}`, 'o-s', 'start', onf(e.num)));
  const ew = PH ? 600 : 430; S(E('rect', {x: ex - 10, y: ey - 26, width: ew, height: (RINGD.epochs.length + 1) * lh + 16, rx: 8}, ge), {fill: 'transparent'}); E('rect', {class: 'ring', x: ex - 14, y: ey - 30, width: ew + 8, height: (RINGD.epochs.length + 1) * lh + 24, rx: 10}, ge);
  if (PH) return;   // (a phone: the stars and the ways back in are in the panel)
  const gd = opart(L, 'stardust', 'The chip\'s silicon was made in stars: details', {title: 'Made in stars', kick: 'Ring of sizes · physics', lead: 'The silicon in the chip\'s fins was forged in stars of the Milky Way before the Sun formed, from protons and neutrons that formed some 14 to 24 microseconds after the Big Bang: a physical link between the top of the ladder and its bottom.', facts: ['e.stars.1', 'e.stars.2', 'e.stars.3', 'e.stars.4', 'e.qcd.5']});
  const sy = ey + (RINGD.epochs.length + 1) * lh + 30;
  wrapW(`The chip's silicon was made in stars before the Sun formed, ${on('ep_sun')} ago.`, PH ? 44 : 44).forEach((t, i) => T(gd, ex, sy + i * lh, t, 'o-s', 'start', onf('ep_sun')));
  S(E('rect', {x: ex - 10, y: sy - 24, width: ew, height: PH ? 70 : 60, rx: 8}, gd), {fill: 'transparent'}); E('rect', {class: 'ring', x: ex - 14, y: sy - 28, width: ew + 8, height: PH ? 78 : 66, rx: 10}, gd);
  // the ways back in: Up takes the one marked
  const xs = typeof pageExits === 'function' ? pageExits() : [], up = upExit();
  const bx = ex, by = sy + (PH ? 70 : 72);
  T(L, bx, by, 'In again:', 'o-l');
  xs.forEach((x, i) => {
    const tip = x.path()[x.path().length - 1];
    const XP = x.path() || [];
    const g = opart(L, 'exit-' + x.id, `In again: ${x.lab}`, {title: `In again: ${x.lab}`, kick: 'Ring of sizes · a way back in', lead: tip.id === PLANCK
      ? `In at the tail's tip, the Planck length, under ${x.where || 'that atom'}: Up climbs ${climbWords(XP, 4)}, then on up to the chip.`
      : `In as ${x.where || x.lab}: Up climbs from there through ${climbWords(XP, 4)}, on up to the chip, and round again.`, facts: ['p.wrap.1']}, {id: tip.id});
    g._go = x.path;
    const yy = by + 16 + i * (PH ? 50 : 44), w = PH ? 600 : 460;
    S(E('rect', {class: 'shape exitb', x: bx - 6, y: yy, width: w, height: PH ? 42 : 36, rx: 18}, g), {});
    E('rect', {class: 'ring', x: bx - 10, y: yy - 4, width: w + 8, height: (PH ? 42 : 36) + 8, rx: 22}, g);
    T(g, bx + 10, yy + (PH ? 29 : 25), `→ ${x.short}${up && x.id === up.id ? ' (Up)' : ''}`, 'o-s');
  });
  if (!PH) ocredit(L, 'The idea: Sheldon Glashow’s uroboros, as drawn by Primack and Abrams (2006); this drawing is the page’s own.', 712);
}, here: (p, P) => ringHere(P)});
/* the ring's "You are here": what it is, the ways back in (Up takes the marked one), and out to the top */
function ringHere(P) {
  const s = OSC['p.wrap'] || {}, xs = typeof pageExits === 'function' ? pageExits() : [], up = upExit();
  const facts = (s.facts || []).filter(f => F[f]);
  const isUp = x => !!(up && x.id === up.id);
  const rows = `<div class="pn-zoom">${zrow('In again:', xs.map(x => zbtn(x.path(), capFirst(x.short), isUp(x), isUp(x) ? '(Up)' : '')))}${zrow('', [zbtn([{id: 'beyond'}], '? (+)', false, '')])}</div>`;
  panel(`<p class="pn-kick">${hereKick(P)}</p><p class="pn-title">The ring of sizes: a picture, not a place</p><p class="pn-lead">${esc(s.blurb || '')}</p>` + rows
    + '<p class="pn-cred">The idea: Sheldon Glashow’s uroboros, as drawn by Joel Primack and Nancy Ellen Abrams, <i>The View from the Center of the Universe</i> (2006); this drawing is the page’s own.</p>'
    + detBlock((facts.length ? `<p class="pn-h pn-fh">The facts (${facts.length}): point at one for its source</p><ul class="facts">${facts.map(factLi).join('')}</ul>` : '') + lazyNote(s.facts)));
}

/* ---- the two-state circuits: the inverter's input, a stored bit ---- */
function invStates(L, p, n) {
  const SA = E('g', {class: 'st-a', 'pointer-events': 'none'}, L), SB = E('g', {class: 'st-b', 'pointer-events': 'none'}, L);
  S(E('rect', {x: p.x - 46, y: p.y - 56, width: 92, height: 112, rx: 12}, SA), {fill: 'var(--c2)', fillOpacity: 0.16, stroke: 'var(--c2)', strokeWidth: 3});
  S(E('rect', {x: n.x - 46, y: n.y - 56, width: 92, height: 112, rx: 12}, SB), {fill: 'var(--c2)', fillOpacity: 0.16, stroke: 'var(--c2)', strokeWidth: 3});
  KTT(SA, 470, 230, `IN = 0: the PMOS conducts; OUT = 1, at the rail (${on('v_min')})`, 'i-l halo', 'start', onf('v_min'));
  KTT(SB, 470, 476, `IN = 1: the NMOS conducts; OUT = 0 (${on('v_0')})`, 'i-l halo', 'start', onf('v_0'));   // (beside the NMOS, under the truth table: review of 1 Oct)
  stateSwitch(L, -150, 545, {lab: 'The inverter\'s input', btn: ['IN = 0 · switch to 1 (G)', 'IN = 1 · switch to 0 (G)'], say: ['Input 0: the p-type transistor conducts, the output is 1.', 'Input 1: the n-type transistor conducts, the output is 0.']}, {w: 300});
}
/* a stored bit, on a copied drawing of an SRAM or latch cell: which way it holds, and how many electrons that is */
function bitStates(L, o) {
  const g = E('g', {class: 'bitst', 'pointer-events': 'none'}, L), x = o.x, y = o.y, w = o.w || 300;
  const lines = wrapW(`the charged node holds ${on(o.e)} (an estimate); the inverters restore it: no refresh`, Math.floor((w - 24) / 8.6)).slice(0, 4);
  const h = 44 + lines.length * 21 + 12;   // (the box as tall as its lines: the title, the rails, the electrons)
  S(E('rect', {x: x - 12, y: y - 28, width: w, height: h, rx: 10}, g), {fill: 'var(--surface)', stroke: 'var(--c2)', strokeWidth: 1.5});
  const SA = E('g', {class: 'st-a'}, g), SB = E('g', {class: 'st-b'}, g);
  KTT(SA, x, y, 'holding 0: Q low, Q̄ high', 't-smb'); KTT(SB, x, y, 'holding 1: Q high, Q̄ low', 't-smb');
  KTT(g, x, y + 22, `low ${on('v_0')}, high the rail, ${on(o.rail)}`, 't-sm', 'start', `${onf(o.rail)} el.rails`);
  lines.forEach((t, i) => KTT(g, x, y + 44 + i * 21, t, 't-sm', 'start', onf(o.e)));
  stateSwitch(L, x - 12, y - 28 + h + 8, {lab: 'The stored bit', btn: ['Holding 0 · store a 1 (G)', 'Holding 1 · store a 0 (G)'], say: ['The cell holds a 0.', 'The cell holds a 1.']}, {w: w});
}
