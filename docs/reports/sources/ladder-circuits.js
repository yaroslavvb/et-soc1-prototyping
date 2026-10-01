/* ================= ladder-circuits.js: textbook constructions, so that every part reaches a transistor (1 October 2026) =====
   The owner, 1 Oct 09:00: "There are a few places where I hit the limit and couldn't go anymore ... for the compute units,
   can you maybe use the textbook definition of the compute units or the transistors? ... Make sure in all the places I
   eventually go all the way down to the lowest transistor level and then I go down to the atoms." The ET-SoC-1's own
   circuits are not published (its RTL names the blocks: an alignment shifter, an adder, a leading-digit detector, Booth
   encoders ...), so each block a reader can open is drawn here as the construction the textbooks give (N. Weste and D.
   Harris, CMOS VLSI Design, 4th ed., 2011; J. Rabaey et al., Digital Integrated Circuits, 2nd ed., 2003; I. Koren,
   Computer Arithmetic Algorithms, 2nd ed., 2002; and the papers each scene cites), labelled "textbook construction", down
   to a gate drawn as transistors, which leads to the FinFET, its fin and channel, the silicon crystal and its atoms.
   Then every part of the chip's drawings that had no closer drawing is joined to one (links(), at the end): the "no dead
   ends" rule, which tools/pagemotion/zoom_test.mjs T19 checks. Shared, like ladder-inner.js, whose helpers it uses. */
const GT = [['generic', 'textbook construction'], ['unknown', 'this chip’s own circuit: not published']];
const TBK = id => ({title: (sc(id).name || id), lead: sc(id).blurb || '', facts: sc(id).facts || []});
/* a scale a part leads to, with its seat (the part's box) in this drawing. A second part leading to a scale without
   instances gets its own key (lib.xor:pg), so that its double-click zooms into that part and not into the first one's;
   a scale with instances (a bank, a channel) keeps the seat its own drawing gave it */
const hasParse = id => !!(NODES[id] && NODES[id].parse);
function claim(ap, el, tag, r, g, tr, rule) {
  el = typeof el === 'string' ? {id: el} : Object.assign({}, el);
  const z = ap.zs[pk(el)];
  // (a scale whose seat comes from its own rule, the core in a minion's drawing, keeps that seat: another part leading
  // there gets an instance key; rule: that rule gives a seat in this drawing)
  if (!hasParse(el.id) && el.k == null && (z ? z.g !== g : !!rule)) el.k = String(tag);
  if (!ap.zs[pk(el)] && r) ap.zs[pk(el)] = {r, g, tr};
  return el;
}
/* a boxed part of these drawings (dotted: a textbook circuit), its panel the scale it leads to, unless o.info */
function cpart(L, ap, key, x, y, w, h, col, title, kid, o) {
  o = o || {};
  const g = KT.part(L, key, x, y, w, h, col, title, {sub: o.sub, kind: 'generic', center: o.center !== false, fo: o.fo == null ? 0.1 : o.fo, ty: o.ty || Math.min(h / 2 + 7, 34), label: o.label, tcls: o.tcls, lh: o.lh});
  g._info = o.info || TBK(kid);
  if (kid) g._kid = claim(ap, kid, key, {x, y, w, h}, g, o.tr);
  return g;
}
/* a part drawn by the caller (gate symbols, a grid of cells): a group with a transparent box under it. Its seat, where
   the camera zooms in, is one element of it (a row's first cell, a column's first): zoomed into a whole row of eight
   cells the camera would barely zoom (1.4 times in 150 ms, a blink; motion check of 1 Oct) */
function cgrp(L, ap, key, label, box, kid, o) {
  o = o || {};
  const g = KT.comp(L, key, {}, label);
  g._box = box;
  E('rect', {class: 'hit', x: box.x, y: box.y, width: box.w, height: box.h, fill: 'transparent', 'pointer-events': 'all'}, g);
  g._info = o.info || TBK(kid);
  const seat = o.seat || (box.w > 2.5 * box.h ? {x: box.x, y: box.y, w: box.h * 1.6, h: box.h} : box.h > 2.5 * box.w ? {x: box.x, y: box.y, w: box.w, h: box.w * 1.2} : box);
  if (kid) g._kid = claim(ap, kid, key, seat, g, o.tr);
  return g;
}
const cnote = (L, lines, y0, f) => lines.forEach((t, i) => KTT(L, -150, y0 + i * 24, t, 't-sm', 'start', f || null));
/* the kit's gates as symbols: nand (and with a bubble), nor (or with a bubble) */
const nandSym = (p, x, y, o) => KT.andSym(p, x, y, Object.assign({bubble: true}, o || {}));
const norSym = (p, x, y, o) => KT.andSym(p, x, y, Object.assign({or: true, bubble: true}, o || {}));
const boxG = (p, x, y, w, h, t, cls) => { E('rect', {class: 'gate', x, y, width: w, height: h, rx: 5}, p); if (t) KTT(p, x + w / 2, y + h / 2 + 6, t, cls || 't-smb', 'middle'); };

/* ---- the NOR gate and the AOI gate, in transistors (the textbook's static CMOS: Weste and Harris ch. 1) ---- */
function gate2(L, ap, kind) {
  const nor = kind === 'nor';
  KT.frame(L, {title: nor ? 'A NOR gate, in transistors' : 'An AND-OR-INVERT gate, in transistors', sub: nor ? 'out = not (A or B): two PMOS in series pull up, two NMOS side by side pull down'
    : 'out = not (A·B + C): the carry cell of a fast adder, six transistors', col: CC.logic, tags: [['generic', 'textbook']]});
  KT.rail(L, 160, 660, 40, 'VDD'); KT.rail(L, 160, 660, 580, 'GND');
  let nk;
  if (nor) {
    const p1 = KT.mosV(L, 400, 120, {p: true, lead: 40}), p2 = KT.mosV(L, 400, 230, {p: true, lead: 40});
    const n1 = KT.mosV(L, 300, 450, {lead: 40}), n2 = KT.mosV(L, 500, 450, {lead: 40, flip: true});
    KT.wire(L, [[400, p1.top.y], [400, 40]]); KT.wire(L, [[400, p1.bot.y], [400, p2.top.y]]); KT.wire(L, [[400, p2.bot.y], [400, 340]]);
    KT.wire(L, [[300, 340], [500, 340]]); KT.wire(L, [[300, 340], [300, n1.top.y]]); KT.wire(L, [[500, 340], [500, n2.top.y]]); KT.jn(L, 400, 340);
    KT.wire(L, [[300, n1.bot.y], [300, 580]]); KT.wire(L, [[500, n2.bot.y], [500, 580]]);
    KT.wire(L, [[500, 340], [640, 340]]); KT.netLab(L, 648, 346, 'OUT'); KT.jn(L, 500, 340);
    [[p1, 'A'], [p2, 'B'], [n1, 'A'], [n2, 'B']].forEach(([t, lab]) => KT.netLab(L, t.gate.x + (t.gate.x < t.x ? -6 : 6), t.gate.y + 6, lab, t.gate.x < t.x ? 'end' : 'start'));
    nk = n1;
  } else {
    const pa = KT.mosV(L, 320, 110, {p: true, lead: 36}), pb = KT.mosV(L, 480, 110, {p: true, lead: 36, flip: true}), pc = KT.mosV(L, 400, 250, {p: true, lead: 40});
    const na = KT.mosV(L, 320, 410, {lead: 36}), nb = KT.mosV(L, 320, 510, {lead: 36}), nc = KT.mosV(L, 500, 460, {lead: 36, flip: true});
    KT.wire(L, [[320, pa.top.y], [320, 40]]); KT.wire(L, [[480, pb.top.y], [480, 40]]);
    KT.wire(L, [[320, pa.bot.y], [320, 180], [480, 180], [480, pb.bot.y]]); KT.wire(L, [[400, 180], [400, pc.top.y]]); KT.jn(L, 400, 180);
    KT.wire(L, [[400, pc.bot.y], [400, 330]]); KT.wire(L, [[320, 330], [500, 330]]); KT.jn(L, 400, 330);
    KT.wire(L, [[320, 330], [320, na.top.y]]); KT.wire(L, [[320, na.bot.y], [320, nb.top.y]]); KT.wire(L, [[320, nb.bot.y], [320, 580]]);
    KT.wire(L, [[500, 330], [500, nc.top.y]]); KT.wire(L, [[500, nc.bot.y], [500, 580]]);
    KT.wire(L, [[500, 330], [640, 330]]); KT.netLab(L, 648, 336, 'OUT'); KT.jn(L, 500, 330);
    [[pa, 'A'], [pb, 'B'], [pc, 'C'], [na, 'A'], [nb, 'B'], [nc, 'C']].forEach(([t, lab]) => KT.netLab(L, t.gate.x + (t.gate.x < t.x ? -6 : 6), t.gate.y + 6, lab, t.gate.x < t.x ? 'end' : 'start'));
    nk = na;
  }
  cpart(L, ap, 'onefet', nk.x - 24, nk.y - 38, 48, 76, 'var(--c2)', '', 'lib.finfet', {label: 'One transistor', tr: 'jump', fo: 0.1});
  const tb = cgrp(L, ap, 'gtable', 'The truth table', {x: 752, y: 260, w: 220, h: nor ? 136 : 226}, 'lib.finfet', {info: TBK(nor ? 'lib.nor2' : 'lib.aoi21'), tr: 'jump'});
  if (nor) { KTT(tb, 760, 280, 'A B | OUT', 't-mono'); [[0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 0]].forEach((r, i) => KTT(tb, 760, 304 + i * 22, `${r[0]} ${r[1]} |  ${r[2]}`, 't-mono')); }
  else { KTT(tb, 760, 280, 'A B C | OUT', 't-mono'); for (let i = 0; i < 8; i++) { const a = i >> 2 & 1, b = i >> 1 & 1, c = i & 1; KTT(tb, 760, 304 + i * 22, `${a} ${b} ${c} |  ${(a && b) || c ? 0 : 1}`, 't-mono'); } }
  KTT(L, -150, 650, nor ? 'one input at 1 turns an NMOS on and pulls OUT to ground; only when both are 0 do the two PMOS in series pull it up'
    : 'in an adder\'s carry tree it computes G = Gi + Pi·Gj, inverted: one such gate and an inverter per carry cell', 't-sm', 'start', nor ? 'tb.gates' : 'tb.prefix');
}
bnode('lib.nor2', {draw: (L, ap) => gate2(L, ap, 'nor'), def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});
bnode('lib.aoi21', {draw: (L, ap) => gate2(L, ap, 'aoi'), def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}]});

/* ---- a fast adder: Kogge and Stone's parallel prefix, 8 bits drawn (the 64-bit one has three more levels) ---- */
bnode('lib.adder', {draw: (L, ap) => {
  KT.frame(L, {title: 'A fast adder: a Kogge-Stone prefix tree', sub: '8 bits drawn: every carry at once, in log₂ n levels of carry cells, instead of one bit after another', subf: 'tb.prefix', col: CC.logic, tags: GT});
  const X = i => 950 - i * 140, y0 = 70, ys = [196, 290, 384], yS = 470;
  for (let i = 0; i < 8; i++) KTT(L, X(i), 52, `a${i} b${i}`, 't-sm', 'middle');
  const gp = cgrp(L, ap, 'pg', 'Generate and propagate: per bit, g = a·b and p = a ⊕ b', {x: X(7) - 50, y: y0, w: X(0) - X(7) + 100, h: 56}, 'lib.xor', {info: {title: 'Generate and propagate', lead: 'For each bit: generate g = a AND b (this bit makes a carry by itself) and propagate p = a XOR b (this bit passes a carry on). An XOR and a NAND with an inverter per bit.', facts: ['tb.prefix']}});
  for (let i = 0; i < 8; i++) boxG(gp, X(i) - 44, y0, 88, 56, 'g p');
  // the prefix levels: level L combines each column with the one 2^L places to its right (Kogge-Stone)
  ys.forEach((y, l) => {
    const sp = 1 << l, gl = cgrp(L, ap, 'pfx' + sp, `Carry level ${l + 1}: each carry cell joins its column with the one ${sp} to the right`, {x: X(7) - 40, y: y - 28, w: X(sp) - X(7) + 80, h: 56}, 'lib.aoi21',
      {info: {title: `Carry level ${l + 1}`, lead: `Each black cell combines its column's (G, P) with the column ${sp} place${sp > 1 ? 's' : ''} to its right: G = Gᵢ + Pᵢ·Gⱼ and P = Pᵢ·Pⱼ, an AND-OR-INVERT gate and a NAND. After level ${l + 1} each column knows the carry from ${2 * sp} bits.`, facts: ['tb.prefix', 'tb.kogge']}});
    for (let i = 0; i < 8; i++) {
      const yu = l ? ys[l - 1] + 22 : y0 + 56;
      KT.wire(L, [[X(i), yu], [X(i), y - 22]]);
      if (i >= sp) { KT.wire(L, [[X(i - sp), yu + 8], [X(i) - 12, y - 20]], 'thin'); E('rect', {class: 'gate', x: X(i) - 22, y: y - 22, width: 44, height: 44, rx: 22, style: 'fill: var(--ink-2)'}, gl); }
      else E('circle', {class: 'jn', cx: X(i), cy: y, r: 4}, L);
    }
    KTT(L, -150, y + 6, `${sp} apart`, 't-smb');
  });
  const gs = cgrp(L, ap, 'sum', 'The sums: each bit is p ⊕ the carry from the bits to its right', {x: X(7) - 50, y: yS, w: X(0) - X(7) + 100, h: 56}, 'lib.xor', {info: {title: 'The sum bits', lead: 'Each sum bit is its propagate p XOR the carry coming in from all the bits to its right, which the tree has just computed: one more XOR per bit.', facts: ['tb.prefix']}});
  for (let i = 0; i < 8; i++) { KT.wire(L, [[X(i), ys[2] + 22], [X(i), yS]]); boxG(gs, X(i) - 44, yS, 88, 56, `s${i}`); }
  KTT(L, X(0) + 50, 52, '← cin', 't-sm');
  cnote(L, ['a ripple-carry adder waits for each carry in turn, n steps; this tree takes log₂ n levels: 3 for the 8 bits drawn, 6 for 64 bits',
    'P. Kogge and H. Stone, IEEE Trans. Computers, 1973; the ET-SoC-1\'s own adders are not published: a textbook construction'], 628, 'tb.prefix tb.kogge');
}, def: () => ({id: 'lib.aoi21'}), kids: () => [{id: 'lib.aoi21'}, {id: 'lib.xor'}]});

/* ---- a logarithmic (barrel) shifter: log₂ n stages of 2:1 multiplexers, 8 bits drawn ---- */
bnode('lib.shifter', {draw: (L, ap) => {
  KT.frame(L, {title: 'A shifter: stages of 2:1 multiplexers', sub: '8 bits drawn: stage k moves every bit 2ᵏ places, or not; any shift in log₂ n stages', subf: 'tb.shifter', col: 'var(--c4)', tags: GT});
  const X = i => 900 - i * 128, ys = [150, 290, 430], amt = [4, 2, 1];
  for (let i = 0; i < 8; i++) KTT(L, X(i), 56, `d${i}`, 't-net', 'middle');
  ys.forEach((y, l) => {
    const k = amt[l], g = cgrp(L, ap, 'stage' + k, `Stage ${l + 1}: shift by ${k} or not, eight 2:1 multiplexers`, {x: X(7) - 44, y: y - 30, w: X(0) - X(7) + 88, h: 60}, 'lib.mux2',
      {info: {title: `Stage ${l + 1}: shift by ${k}, or not`, lead: `Eight 2:1 multiplexers, one per bit, all switched by one bit of the shift amount: each passes its own bit straight down or the bit ${k} place${k > 1 ? 's' : ''} to its left.`, facts: ['tb.shifter']}});
    for (let i = 0; i < 8; i++) {
      const yu = l ? ys[l - 1] + 30 : 66;
      KT.wire(L, [[X(i), yu], [X(i), y - 30]]);
      if (i + k < 8) KT.wire(L, [[X(i + k), yu + 10], [X(i) - 18, y - 30]], 'thin'); else KTT(L, X(i) - 30, y - 38, '0', 't-sm', 'middle');
      E('path', {class: 'gate', d: `M${X(i) - 30},${y - 30} L${X(i) + 30},${y - 30} L${X(i) + 20},${y + 30} L${X(i) - 20},${y + 30} Z`}, g);
    }
    KTT(L, -150, y + 6, `shift ${k}?`, 't-smb'); KTT(L, -150, y + 30, `amount bit ${2 - l}`, 't-sm');
  });
  for (let i = 0; i < 8; i++) { KT.wire(L, [[X(i), ys[2] + 30], [X(i), 520]]); KTT(L, X(i), 548, `q${i}`, 't-net', 'middle'); }
  cnote(L, ['3 stages shift 8 bits by any amount from 0 to 7; 6 stages shift 64. In the multiply-add one shifter lines c up by the exponents\' difference,',
    'another moves the sum back (normalises it). Weste and Harris, CMOS VLSI Design, ch. 11; the chip\'s own shifters are not published'], 628, 'tb.shifter in.vpu.lane.fma.norm.1');
}, def: () => ({id: 'lib.mux2'}), kids: () => [{id: 'lib.mux2'}]});

/* ---- radix-4 Booth recoding: three bits of the multiplier pick 0, ±X or ±2X for a row of partial product ---- */
bnode('lib.booth', {draw: (L, ap) => {
  KT.frame(L, {title: 'A Booth encoder and its selectors', sub: 'radix 4: two bits of the multiplier per row of partial product, so half as many rows to add', subf: 'tb.booth', col: CC.logic, tags: GT});
  const bx = i => 470 - i * 64;
  for (let i = -1; i < 8; i++) KTT(L, bx(i), 70, i < 0 ? '(0)' : `y${i}`, 't-net', 'middle');
  KTT(L, -150, 70, 'the multiplier', 't-smb');
  const ge = cgrp(L, ap, 'enc', 'The encoders: each looks at three overlapping bits of the multiplier', {x: bx(7) - 40, y: 100, w: bx(-1) - bx(7) + 80, h: 120}, 'lib.xor',
    {info: {title: 'The Booth encoders', lead: 'Each encoder looks at three overlapping bits of the multiplier (bits 2i+1, 2i and 2i-1) and decides what its row adds: 0, the multiplicand X, twice it, or minus either. A few XOR gates per encoder.', facts: ['tb.booth', 'tb.booth.table']}});
  for (let j = 0; j < 4; j++) {
    const x0 = bx(2 * j + 1), x1 = bx(2 * j - 1);
    E('path', {class: 'w', d: `M${x0 - 16},92 L${x0 - 16},104 L${x1 + 16},104 L${x1 + 16},92`}, ge);
    boxG(ge, (x0 + x1) / 2 - 56, 134, 112, 60, `row ${j}`);
  }
  // the table of the five choices
  const tx = 640;
  KTT(L, tx, 70, 'bits → the row adds', 't-smb', 'start', 'tb.booth.table');
  [['000', '0'], ['001', '+X'], ['010', '+X'], ['011', '+2X'], ['100', '−2X'], ['101', '−X'], ['110', '−X'], ['111', '0']].forEach(([b, r], i) => KTT(L, tx + (i >> 2) * 210, 100 + (i & 3) * 26, `${b} → ${r}`, 't-mono'));
  // one row's selectors: a 2:1 mux per bit (X or 2X), then an XOR (minus)
  const sx = j => 900 - j * 112, sy = 330;
  KTT(L, -150, sy + 8, 'one row:', 't-smb');
  const gm = cgrp(L, ap, 'sel', 'The row\'s selectors: per bit, a 2:1 multiplexer picks X or 2X (X shifted one place)', {x: sx(7) - 34, y: sy - 34, w: sx(0) - sx(7) + 68, h: 68}, 'lib.mux2',
    {info: {title: 'The selectors', lead: 'For each bit of the row a 2:1 multiplexer picks bit j of X (for ±X) or bit j-1 (for ±2X: X shifted one place), or neither (for 0).', facts: ['tb.booth']}});
  const gx = cgrp(L, ap, 'neg', 'The negation: per bit, an XOR inverts the bit when the row is negative', {x: sx(7) - 34, y: sy + 70, w: sx(0) - sx(7) + 68, h: 68}, 'lib.xor',
    {info: {title: 'Negation', lead: 'Minus X is made by inverting every bit (an XOR with the sign) and adding a 1 at the row\'s lowest place, which the adder tree takes as one more bit.', facts: ['tb.booth']}});
  for (let j = 0; j < 8; j++) {
    E('path', {class: 'gate', d: `M${sx(j) - 24},${sy - 30} L${sx(j) + 24},${sy - 20} L${sx(j) + 24},${sy + 20} L${sx(j) - 24},${sy + 30} Z`}, gm);
    xorSym(gx, sx(j) - 20, sy + 104, {w: 44, h: 50});
    KT.wire(L, [[sx(j), sy + 30], [sx(j), sy + 80]]); KTT(L, sx(j), sy - 44, `x${j}`, 't-sm', 'middle');
  }
  KTT(L, sx(0) + 46, sy + 110, 'row: 0, ±X or ±2X', 't-sm');
  cnote(L, [`a signed 8-bit multiplier makes 4 rows (drawn; an unsigned one, one more); the multiply-add's 32-bit one makes ${on('pp17')}, which its tree adds`,
    'A. Booth (1951), O. MacSorley (1961, radix 4); Koren, Computer Arithmetic Algorithms, ch. 6; the chip\'s own encoder is not published'], 628, `tb.booth ${onf('pp17')}`);
}, def: () => ({id: 'lib.mux2'}), kids: () => [{id: 'lib.mux2'}, {id: 'lib.xor'}]});

/* ---- a leading-zero detector: a tree of small cells, 8 bits drawn (Oklobdzija 1994) ---- */
bnode('lib.lzd', {draw: (L, ap) => {
  KT.frame(L, {title: 'A leading-zero counter: a tree of cells', sub: '8 bits drawn: how many zeros before the first 1, so how far the normaliser must shift the sum', subf: 'tb.lzd', col: 'var(--c4)', tags: GT});
  const X = i => 900 - i * 128;
  for (let i = 0; i < 8; i++) KTT(L, X(i), 64, `b${i}`, 't-net', 'middle');
  const gl = cgrp(L, ap, 'leaf', 'Level 1: each cell looks at two bits: is either a 1, and is it the left one', {x: X(7) - 60, y: 110, w: X(0) - X(7) + 120, h: 70}, 'lib.nor2',
    {info: {title: 'The first level', lead: 'Each cell takes two neighbouring bits and says whether either is a 1 (v: a NOR and an inverter) and, if so, whether the first 1 is the right one (p: the left bit inverted).', facts: ['tb.lzd']}});
  for (let j = 0; j < 4; j++) { const xa = X(2 * j + 1), xb = X(2 * j); KT.wire(L, [[xa, 74], [xa, 110]]); KT.wire(L, [[xb, 74], [xb, 110]]); boxG(gl, xa - 30, 110, xb - xa + 60, 70, 'v p'); }
  const gm = cgrp(L, ap, 'merge', 'Levels 2 and 3: each cell joins two cells: the left one if it has a 1, else the right one', {x: X(7) - 60, y: 250, w: X(0) - X(7) + 120, h: 210}, 'lib.mux2',
    {info: {title: 'The merging levels', lead: 'Each cell joins a left and a right cell: there is a 1 if either has one (an OR), and the position comes from the left cell if it has a 1, else from the right one with one more bit set: a 2:1 multiplexer per bit of the count.', facts: ['tb.lzd']}});
  const lc = j => (X(2 * j + 1) + X(2 * j)) / 2;
  [[3, 2], [1, 0]].forEach(([hi, lo]) => { const mc = (lc(hi) + lc(lo)) / 2; KT.wire(L, [[lc(hi), 180], [mc - 40, 250]]); KT.wire(L, [[lc(lo), 180], [mc + 40, 250]]); boxG(gm, mc - 140, 250, 280, 70, 'v, 2 bits'); });
  KT.wire(L, [[(lc(3) + lc(2)) / 2, 320], [(X(7) + X(0)) / 2 - 40, 390]]); KT.wire(L, [[(lc(1) + lc(0)) / 2, 320], [(X(7) + X(0)) / 2 + 40, 390]]);
  boxG(gm, (X(7) + X(0)) / 2 - 200, 390, 400, 70, 'v, 3 bits: the count');
  KT.wire(L, [[(X(7) + X(0)) / 2, 460], [(X(7) + X(0)) / 2, 520]]); KTT(L, (X(7) + X(0)) / 2, 546, 'leading zeros: 0 to 7 (v = 0: all zero)', 't-net', 'middle');
  cnote(L, ['log₂ n levels: 3 for 8 bits, 6 for 64. An anticipator guesses the count from the adder\'s inputs, alongside the addition, at most one off',
    'V. Oklobdzija, IEEE Trans. VLSI 1994; M. Schmookler and K. Nowka, ARITH 2001; the chip\'s detector (txfma_lxd in its RTL) is not published'], 628, 'tb.lzd tb.lza in.vpu.lane.fma.norm.1');
}, def: () => ({id: 'lib.mux2'}), kids: () => [{id: 'lib.mux2'}, {id: 'lib.nor2'}]});

/* ---- a decoder: n address bits pick one of 2ⁿ rows (3 to 8 drawn) ---- */
bnode('lib.decoder', {draw: (L, ap) => {
  KT.frame(L, {title: 'A decoder: 3 bits pick one of 8 rows', sub: 'one AND gate per row, fed by each bit or its complement; the row\'s driver raises its line', subf: 'tb.decoder', col: CC.logic, tags: GT});
  const gi = cgrp(L, ap, 'inv', 'The inverters: each address bit and its complement', {x: -150, y: 40, w: 230, h: 220}, 'lib.inverter');
  const rx = [140, 200, 260, 320, 380, 440];
  [0, 1, 2].forEach(b => {
    const y = 70 + b * 80; KT.netLab(L, -140, y + 6, `a${2 - b}`, 'start');
    KT.wire(L, [[-100, y], [rx[2 * b], y]]); KT.jn(L, -60, y); KT.wire(L, [[-60, y], [-60, y + 36], [-20, y + 36]]); KT.invSym(gi, 0, y + 36, {s: 18});
    KT.wire(L, [[30, y + 36], [rx[2 * b + 1], y + 36]]);
  });
  rx.forEach(x => KT.wire(L, [[x, 70], [x, 620]], 'thin'));
  const ga = cgrp(L, ap, 'ands', 'The row gates: one 3-input AND per row (a NAND and an inverter)', {x: 500, y: 40, w: 120, h: 590}, 'lib.nand2');
  const gd = cgrp(L, ap, 'drv', 'The row drivers: wide inverters that raise the selected line', {x: 650, y: 40, w: 160, h: 590}, 'lib.inverter');
  for (let r = 0; r < 8; r++) {
    const y = 70 + r * 72, a = KT.andSym(ga, 520, y, {w: 50, h: 46});
    [0, 1, 2].forEach(b => { const bit = r >> (2 - b) & 1, x = rx[2 * b + (bit ? 0 : 1)]; KT.jn(L, x, y - 12 + b * 12); KT.wire(L, [[x, y - 12 + b * 12], [520, y - 12 + b * 12]], 'thin'); });
    KT.wire(L, [[a.out.x, y], [672, y]]); KT.invSym(gd, 690, y, {s: 16}); KT.wire(L, [[716, y], [840, y]]); KT.netLab(L, 846, y + 6, `row ${r}`);
  }
  cnote(L, ['a memory\'s row decoder: 7 bits pick one of 128 rows; big ones decode 2-3 bits first (predecoding), then AND those', 'Weste and Harris, CMOS VLSI Design, ch. 12'], 668, 'tb.decoder');
}, def: () => ({id: 'lib.nand2'}), kids: () => [{id: 'lib.nand2'}, {id: 'lib.inverter'}]});

/* ---- a register file: rows of latch bits, a write decoder and clock gates, read multiplexers (8 by 8 drawn) ---- */
bnode('lib.regfile', {draw: (L, ap) => {
  KT.frame(L, {title: 'A register file: rows of latches', sub: '8 words of 8 bits drawn: a write opens one row\'s clock; a read picks one row per bit through multiplexers', subf: 'tb.regfile', col: CC.store, tags: GT});
  const cx = c => 230 + c * 70, ry = r => 70 + r * 56;
  const gw = cgrp(L, ap, 'wdec', 'The write decoder: the write address picks one row', {x: -150, y: 50, w: 150, h: 460}, 'lib.decoder');
  boxG(gw, -140, 60, 130, 440, 'decoder');
  const gc = cgrp(L, ap, 'icg', 'The row clock gates: only the written row\'s latches see the clock', {x: 30, y: 50, w: 140, h: 460}, 'lib.icg');
  for (let r = 0; r < 8; r++) { KT.wire(L, [[-10, ry(r) + 18], [50, ry(r) + 18]], 'thin'); boxG(gc, 50, ry(r), 100, 36, 'ICG', 't-sm'); KT.wire(L, [[150, ry(r) + 18], [cx(0) - 24, ry(r) + 18]], 'thin'); }
  const gl = cgrp(L, ap, 'cells', 'The storage: one latch per bit, 64 here', {x: cx(0) - 30, y: 50, w: cx(7) - cx(0) + 60, h: 460}, 'lib.latch');
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) E('rect', {class: 'gate', x: cx(c) - 22, y: ry(r), width: 44, height: 36, rx: 4}, gl);
  KTT(L, cx(0) - 24, 44, 'write data, 8 bits ↓', 't-sm');
  const gm = cgrp(L, ap, 'rmux', 'The read multiplexers: per bit, a tree of 2:1 multiplexers picks the addressed row', {x: cx(0) - 30, y: 530, w: cx(7) - cx(0) + 60, h: 80}, 'lib.mux2');
  for (let c = 0; c < 8; c++) { KT.wire(L, [[cx(c), ry(7) + 36], [cx(c), 540]], 'thin'); E('path', {class: 'gate', d: `M${cx(c) - 28},540 L${cx(c) + 28},540 L${cx(c) + 16},590 L${cx(c) - 16},590 Z`}, gm); }
  KTT(L, cx(7) + 40, 570, '← read address', 't-sm'); KTT(L, cx(0) - 24, 616, 'read data, 8 bits', 't-sm');
  cnote(L, ['a minion\'s registers are of this kind: the core\'s integer file is 64 words of 64 bits (two threads of 32), latches, with two read ports and one write', 'Weste and Harris, CMOS VLSI Design, ch. 12'], 648, 'tb.regfile in.core.irf.1');
}, def: () => ({id: 'lib.latch'}), kids: () => [{id: 'lib.latch'}, {id: 'lib.decoder'}, {id: 'lib.icg'}, {id: 'lib.mux2'}]});

/* ---- a clock gate: a latch holds the enable while the clock is high, an AND passes the clock only when enabled ---- */
bnode('lib.icg', {draw: (L, ap) => {
  KT.frame(L, {title: 'A clock gate: a latch and an AND gate', sub: 'a block with nothing to do gets no clock edges, so its flip-flops and clock wires switch nothing', subf: 'tb.icg', col: 'var(--c7)', tags: [['generic', 'textbook']]});
  KT.netLab(L, -140, 186, 'EN', 'start'); KT.netLab(L, -140, 386, 'CLK', 'start');
  cpart(L, ap, 'latch', 60, 120, 260, 150, CC.store, 'latch', 'lib.latch', {sub: ['holds EN while', 'CLK is high'], ty: 56, info: {title: 'The enable latch', lead: 'Transparent while the clock is low, it holds the enable steady while the clock is high, so the gated clock never has a glitch.', facts: ['tb.icg']}});
  const ga = cgrp(L, ap, 'and', 'The AND gate: the clock passes only while the enable is 1', {x: 470, y: 230, w: 160, h: 130}, 'lib.nand2', {info: {title: 'The AND gate', lead: 'A NAND and an inverter: the gated clock follows the clock only while the latched enable is 1.', facts: ['tb.icg']}});
  const a = KT.andSym(ga, 500, 296, {w: 90, h: 86});
  KT.wire(L, [[-100, 180], [60, 180]]); KT.wire(L, [[320, 195], [420, 195], [420, a.a.y], [500, a.a.y]]);
  KT.wire(L, [[-100, 380], [420, 380], [420, a.b.y], [500, a.b.y]]); KT.jn(L, 0, 380); KT.wire(L, [[0, 380], [0, 250], [60, 250]]); KTT(L, 8, 316, 'CK', 't-sm');
  KT.wire(L, [[a.out.x, 296], [760, 296]]); KT.netLab(L, 768, 302, 'GCLK');
  // the waveforms: the clock, the enable, the gated clock
  const wx = x => 60 + x * 64, wv = (y, bits) => { let d = `M${wx(0)},${y + (bits[0] ? 0 : 30)}`; bits.forEach((b, i) => { d += ` L${wx(i)},${y + (b ? 0 : 30)} L${wx(i + 1)},${y + (b ? 0 : 30)}`; }); E('path', {class: 'w', d}, L); };
  const CK = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], EN = [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0], GK = CK.map((c, i) => (c && EN[i - 1 >= 0 ? i - 1 : 0] ? 1 : 0));
  [['CLK', CK, 450], ['EN', EN, 510], ['GCLK', GK, 570]].forEach(([t, b, y]) => { KTT(L, -40, y + 24, t, 't-sm', 'end'); wv(y, b); });
  cnote(L, ['the multiply-add\'s first stage gates its operands\' clock this way: a zero operand costs almost nothing', 'Weste and Harris, CMOS VLSI Design, ch. 10'], 650, 'tb.icg in.vpu.lane.fma.1');
}, def: () => ({id: 'lib.latch'}), kids: () => [{id: 'lib.latch'}, {id: 'lib.nand2'}]});

/* ---- control logic: what any block whose netlist is not published is made of, at the gate level ---- */
bnode('lib.logic', {draw: (L, ap) => {
  KT.frame(L, {title: 'Control logic: standard cells', sub: 'flip-flops hold the state; gates compute the next state and the outputs, every clock', subf: 'tb.stdcell', col: CC.logic, tags: GT});
  const gs = [
    ['nand', 'lib.nand2', 'A NAND gate', 60, 90, (p, x, y) => nandSym(p, x, y, {w: 64, h: 60})],
    ['nor', 'lib.nor2', 'A NOR gate', 60, 230, (p, x, y) => norSym(p, x, y, {w: 64, h: 60})],
    ['aoi', 'lib.aoi21', 'An AND-OR-INVERT gate', 60, 370, (p, x, y) => boxG(p, x, y - 34, 90, 68, 'AOI')],
    ['xor', 'lib.xor', 'An XOR gate', 260, 160, (p, x, y) => xorSym(p, x, y, {w: 64, h: 60})],
    ['inv', 'lib.inverter', 'An inverter', 260, 300, (p, x, y) => KT.invSym(p, x + 20, y, {s: 26})],
    ['mux', 'lib.mux2', 'A 2:1 multiplexer', 270, 440, (p, x, y) => KT.mux2(p, x, y, {w: 40, h: 80})],
  ];
  gs.forEach(([k, id, lab, x, y, draw]) => { const g = cgrp(L, ap, k, lab, {x: x - 24, y: y - 50, w: 140, h: 100}, id); draw(g, x, y); });
  [[90, 'in₀'], [230, 'in₁'], [370, 'in₂']].forEach(([y, t]) => { KT.wire(L, [[-110, y], [40, y]]); KT.netLab(L, -146, y + 6, t); });
  [[124, 90, 160], [124, 230, 160], [150, 370, 300], [124, 230, 300]].forEach(([x1, y1, y2]) => KT.wire(L, [[x1, y1], [200, y1], [200, y2], [244, y2]], 'thin'));
  const gf = cgrp(L, ap, 'ff', 'The state: a row of flip-flops', {x: 520, y: 100, w: 150, h: 400}, 'lib.flipflop');
  for (let i = 0; i < 3; i++) { KT.flopSym(gf, 540, 120 + i * 130, 100, 100, `D  Q`); KT.wire(L, [[340, 160 + i * 130], [540, 160 + i * 130]], 'thin'); KT.wire(L, [[640, 152 + i * 130], [820, 152 + i * 130]]); KT.netLab(L, 828, 158 + i * 130, `state ${i} / out ${i}`); }
  KT.wire(L, [[760, 152], [760, 600], [-120, 600], [-120, 300], [-10, 300]], 'thin'); KTT(L, 300, 590, 'the state feeds back into the gates', 't-sm');
  const gc = cgrp(L, ap, 'icg', 'The clock gate: the flip-flops get a clock edge only when the block has work', {x: 520, y: 510, w: 150, h: 70}, 'lib.icg');
  boxG(gc, 540, 520, 100, 48, 'ICG'); KT.wire(L, [[590, 520], [590, 470]], 'thin');
  cnote(L, ['synthesis turns a block\'s description (its RTL) into thousands of cells like these, from a library of a few hundred kinds; this chip\'s netlists are not published'], 660, 'tb.stdcell');
}, def: () => ({id: 'lib.flipflop'}), kids: () => [{id: 'lib.flipflop'}, {id: 'lib.nand2'}, {id: 'lib.nor2'}, {id: 'lib.aoi21'}, {id: 'lib.inverter'}, {id: 'lib.mux2'}, {id: 'lib.xor'}, {id: 'lib.icg'}]});

/* ---- a counter: a register and an incrementer (half adders), 4 bits drawn ---- */
bnode('lib.counter', {draw: (L, ap) => {
  KT.frame(L, {title: 'A counter: a register and an incrementer', sub: '4 bits drawn: on each step the register takes its value plus one, as barrier, credit and performance counters do', subf: 'tb.counter', col: CC.logic, tags: GT});
  const X = i => 700 - i * 230;
  const gh = cgrp(L, ap, 'ha', 'The incrementer: a half adder per bit (sum = q ⊕ carry, carry = q · carry)', {x: X(3) - 90, y: 110, w: X(0) - X(3) + 180, h: 120}, 'lib.xor',
    {info: {title: 'The incrementer', lead: 'Adding one is a chain of half adders: each bit flips when the carry from the bits to its right is 1 (an XOR) and passes a carry on when it is itself 1 (an AND).', facts: ['tb.counter']}});
  const gf = cgrp(L, ap, 'ff', 'The register: one flip-flop per bit', {x: X(3) - 90, y: 300, w: X(0) - X(3) + 180, h: 120}, 'lib.flipflop');
  for (let i = 0; i < 4; i++) {
    boxG(gh, X(i) - 70, 120, 140, 100, 'half adder');
    KT.flopSym(gf, X(i) - 60, 310, 120, 100, `q${i}`);
    KT.wire(L, [[X(i), 220], [X(i), 310]]); KT.wire(L, [[X(i) + 70, 410], [X(i) + 90, 410], [X(i) + 90, 260], [X(i) + 50, 260], [X(i) + 50, 220]], 'thin');
    if (i < 3) { KT.wire(L, [[X(i) - 70, 150], [X(i + 1) + 70, 150]]); KTT(L, (X(i) + X(i + 1)) / 2, 140, 'carry', 't-sm', 'middle'); }
  }
  KT.wire(L, [[X(0) + 70, 150], [X(0) + 150, 150]]); KTT(L, X(0) + 156, 156, '+1', 't-net');
  const gq = cgrp(L, ap, 'cmp', 'The compare: equal to the target count (a barrier is reached)', {x: X(3) - 90, y: 480, w: X(0) - X(3) + 180, h: 90}, 'lib.cmpeq');
  boxG(gq, X(3) - 80, 490, X(0) - X(3) + 160, 70, 'count = target?');
  for (let i = 0; i < 4; i++) KT.wire(L, [[X(i), 410], [X(i), 490]], 'thin');
  cnote(L, ['the shire\'s fast barriers are 32 such counters, 8 bits each; a cache bank\'s performance counters are the same, 40 bits wide', 'Weste and Harris, CMOS VLSI Design, ch. 11'], 640, 'tb.counter in.shire.uc.flb.1 ml:l2:l2.perfmon');
}, def: () => ({id: 'lib.flipflop'}), kids: () => [{id: 'lib.flipflop'}, {id: 'lib.xor'}, {id: 'lib.cmpeq'}]});

/* ---- an equality comparator: an XNOR per bit, then an AND tree ---- */
bnode('lib.cmpeq', {draw: (L, ap) => {
  KT.frame(L, {title: 'A comparator: are two numbers equal?', sub: '8 bits drawn: an XNOR per bit says "these agree"; a tree of NANDs and NORs says "all agree"', subf: 'tb.compare', col: CC.logic, tags: GT});
  const X = i => 900 - i * 130;
  const gx = cgrp(L, ap, 'xnor', 'The XNORs: one per bit, 1 when the two bits agree', {x: X(7) - 50, y: 90, w: X(0) - X(7) + 100, h: 110}, 'lib.xor');
  for (let i = 0; i < 8; i++) { KTT(L, X(i), 64, `a${i} b${i}`, 't-sm', 'middle'); xorSym(gx, X(i) - 28, 150, {w: 56, h: 56, bubble: true}); }
  const gt = cgrp(L, ap, 'tree', 'The AND tree: NANDs, then NORs: 1 only when every bit agrees', {x: X(7) - 50, y: 250, w: X(0) - X(7) + 100, h: 300}, 'lib.nand2');
  // (the gates drawn turned: inputs from above, the output below)
  const gate = (x, y, nor) => { E('path', {class: 'gate', d: nor ? `M${x - 28},${y - 22} Q${x},${y - 10} ${x + 28},${y - 22} Q${x + 24},${y + 14} ${x},${y + 26} Q${x - 24},${y + 14} ${x - 28},${y - 22} Z` : `M${x - 28},${y - 22} L${x + 28},${y - 22} L${x + 28},${y} A28,28 0 0 1 ${x - 28},${y} Z`}, gt); E('circle', {class: 'gate', cx: x, cy: y + 32, r: 5}, gt); return {x, top: y - 22, out: y + 37}; };
  const n1 = [0, 1, 2, 3].map(j => { const xm = (X(2 * j) + X(2 * j + 1)) / 2, g = gate(xm, 300, false); KT.wire(L, [[X(2 * j) + 22, 180], [xm + 12, g.top]], 'thin'); KT.wire(L, [[X(2 * j + 1) + 22, 180], [xm - 12, g.top]], 'thin'); return g; });
  const n2 = [[3, 2], [1, 0]].map(([a, b]) => { const xm = (n1[a].x + n1[b].x) / 2, g = gate(xm, 420, true); KT.wire(L, [[n1[a].x, n1[a].out], [xm - 12, g.top]], 'thin'); KT.wire(L, [[n1[b].x, n1[b].out], [xm + 12, g.top]], 'thin'); return g; });
  const xa = (n2[0].x + n2[1].x) / 2, ga = KT.andSym(gt, xa - 26, 520, {w: 52, h: 48});
  KT.wire(L, [[n2[0].x, n2[0].out], [n2[0].x, 508], [xa - 26, 508]], 'thin'); KT.wire(L, [[n2[1].x, n2[1].out], [n2[1].x, 532], [xa - 26, 532]], 'thin');
  KT.wire(L, [[ga.out.x, 520], [ga.out.x + 60, 520]]); KTT(L, ga.out.x + 68, 526, 'equal', 't-net');
  cnote(L, ['a cache\'s tag check is one of these per way, as wide as the tag (23 bits in the shire cache); the first way to say "equal" is the hit', 'Weste and Harris, CMOS VLSI Design, ch. 11'], 640, 'tb.compare ml:l2:l2.tag-ram');
}, def: () => ({id: 'lib.xor'}), kids: () => [{id: 'lib.xor'}, {id: 'lib.nand2'}]});

/* ---- a queue (FIFO): a small register file and two pointers ---- */
bnode('lib.fifo', {draw: (L, ap) => {
  KT.frame(L, {title: 'A queue: a register file and two counters', sub: 'requests wait their turn: written at the tail, read at the head, in order', subf: 'tb.fifo', col: CC.store, tags: GT});
  const gs = cgrp(L, ap, 'store', 'The entries: a small register file', {x: 240, y: 120, w: 420, h: 330}, 'lib.regfile');
  for (let i = 0; i < 4; i++) boxG(gs, 260, 140 + i * 76, 380, 60, `entry ${i}`, 't-sm');
  KT.wire(L, [[-100, 290], [240, 290]]); KT.netLab(L, -140, 280, 'in →'); KT.wire(L, [[660, 290], [900, 290]]); KT.netLab(L, 908, 296, '→ out');
  const gw = cgrp(L, ap, 'wptr', 'The write pointer: a counter that steps on every push', {x: -40, y: 470, w: 240, h: 90}, 'lib.counter');
  boxG(gw, -30, 480, 220, 70, 'tail (write)');
  const gr = cgrp(L, ap, 'rptr', 'The read pointer: a counter that steps on every pop', {x: 700, y: 470, w: 240, h: 90}, 'lib.counter');
  boxG(gr, 710, 480, 220, 70, 'head (read)');
  const gc = cgrp(L, ap, 'cmp', 'Full and empty: the two pointers compared', {x: 330, y: 500, w: 240, h: 90}, 'lib.cmpeq');
  boxG(gc, 340, 510, 220, 70, 'full? empty?');
  KT.wire(L, [[190, 515], [340, 545]], 'thin'); KT.wire(L, [[710, 515], [560, 545]], 'thin'); KT.wire(L, [[80, 480], [300, 440]], 'thin'); KT.wire(L, [[820, 480], [600, 440]], 'thin');
  cnote(L, ['queues of this kind wait at the ports of the shire cache, its crossbar and the mesh\'s routers', 'Weste and Harris, CMOS VLSI Design, ch. 12 (serial-access memories)'], 640, 'tb.fifo');
}, def: () => ({id: 'lib.regfile'}), kids: () => [{id: 'lib.regfile'}, {id: 'lib.counter'}, {id: 'lib.cmpeq'}]});

/* ---- a phase-locked loop: the clocks' source ---- */
bnode('lib.pll', {draw: (L, ap) => {
  KT.frame(L, {title: 'A phase-locked loop: a clock multiplier', sub: 'a detector compares the divided output with the reference and nudges an oscillator until they agree: out = N × ref', subf: 'tb.pll', col: 'var(--c7)', tags: GT});
  const y = 250;
  KT.netLab(L, -140, y - 30, 'ref'); KT.wire(L, [[-100, y - 36], [-40, y - 36]]);
  cpart(L, ap, 'pfd', -40, y - 80, 180, 140, CC.logic, 'phase detector', 'lib.flipflop', {sub: ['two flip-flops', 'and an AND'], ty: 50, info: {title: 'The phase-frequency detector', lead: 'Two flip-flops, set by the reference\'s edge and by the divided output\'s, and reset together: whichever comes first says "faster" or "slower".', facts: ['tb.pll']}});
  KT.wire(L, [[140, y - 10], [200, y - 10]]);
  cpart(L, ap, 'cp', 200, y - 80, 170, 140, 'var(--c5)', 'charge pump', 'lib.finfet', {sub: ['two switched', 'current sources'], ty: 50, tr: 'jump', info: {title: 'The charge pump', lead: 'Two transistors used as switched current sources push charge into the loop filter or pull it out, as the detector says.', facts: ['tb.pll']}});
  KT.wire(L, [[370, y - 10], [430, y - 10]]);
  cpart(L, ap, 'lf', 430, y - 80, 160, 140, 'var(--c3)', 'loop filter', 'lib.finfet', {sub: ['a resistor and', 'a capacitor'], ty: 50, tr: 'jump', info: {title: 'The loop filter', lead: 'Smooths the pump\'s pulses into a control voltage. On a chip its capacitor is usually a transistor\'s gate over its channel (a MOS capacitor).', facts: ['tb.pll']}});
  KT.wire(L, [[590, y - 10], [650, y - 10]]);
  const gv = cgrp(L, ap, 'vco', 'The oscillator: a ring of an odd number of inverters', {x: 650, y: y - 90, w: 330, h: 170}, 'lib.inverter', {info: {title: 'The voltage-controlled oscillator', lead: 'A ring of an odd number of inverters can never settle: each passes its flip to the next, so the ring oscillates; the control voltage sets how fast each inverter switches.', facts: ['tb.pll']}});
  for (let i = 0; i < 5; i++) KT.invSym(gv, 680 + i * 60, y - 10, {s: 16});
  KT.wire(L, [[960, y - 10], [970, y - 10], [970, y + 60], [668, y + 60], [668, y - 10]], 'thin'); KTT(L, 820, y - 50, 'oscillator', 't-smb', 'middle');
  KT.wire(L, [[970, y - 10], [1040, y - 10]]); KT.netLab(L, 1000, y - 24, 'out');
  const gd = cgrp(L, ap, 'div', 'The divider: a counter that gives one edge per N of the output\'s', {x: 380, y: y + 150, w: 260, h: 110}, 'lib.counter', {info: {title: 'The divider', lead: 'A counter: one output edge for every N of the oscillator\'s, fed back to the detector, so the loop settles where the output is N times the reference.', facts: ['tb.pll']}});
  boxG(gd, 390, y + 160, 240, 90, '÷ N');
  KT.wire(L, [[1010, y - 10], [1010, y + 205], [630, y + 205]]); KT.wire(L, [[390, y + 205], [50, y + 205], [50, y + 60]]);
  cnote(L, ['the chip\'s PLLs multiply its 24 or 100 MHz reference clock up; each minion shire has its own', 'Weste and Harris, CMOS VLSI Design, ch. 13; the chip\'s own PLLs are not published'], 640, 'tb.pll in.shire.clock.2 shire.clock');
}, def: () => ({id: 'lib.inverter'}), kids: () => [{id: 'lib.inverter'}, {id: 'lib.flipflop'}, {id: 'lib.counter'}, {id: 'lib.finfet'}]});

/* ---- error correction (SECDED): check bits from XOR trees, a syndrome that points at a flipped bit ---- */
bnode('lib.ecc', {draw: (L, ap) => {
  KT.frame(L, {title: 'Error correction (SECDED)', sub: '8 data bits and 5 check bits drawn: each check bit is the parity of some bits; on a read the mismatches point at a flipped bit', subf: 'tb.ecc', col: CC.logic, tags: GT});
  const cols = 13, X = c => 140 + c * 62, rows = 5, Y = r => 110 + r * 50;
  for (let c = 0; c < cols; c++) KTT(L, X(c), 80, c < 8 ? `d${c}` : `c${c - 8}`, 't-sm', 'middle');
  const H = [];   // the Hamming positions 1..12 and an overall parity
  for (let c = 0; c < 8; c++) { const pos = [3, 5, 6, 7, 9, 10, 11, 12][c]; H.push([0, 1, 2, 3].map(b => pos >> b & 1).concat([1])); }
  for (let c = 0; c < 5; c++) H.push([0, 1, 2, 3, 4].map(r => (r === c || r === 4 ? 1 : 0)));
  const ge = cgrp(L, ap, 'enc', 'The check bits: each an XOR tree over the data bits marked in its row', {x: X(0) - 30, y: Y(0) - 24, w: X(12) - X(0) + 60, h: Y(4) - Y(0) + 48}, 'lib.xor',
    {info: {title: 'The parity-check matrix', lead: 'Each row is one check bit: the XOR of the data bits marked in it. Every data bit is in a different combination of rows, so a single flipped bit shows up as its own pattern of mismatches.', facts: ['tb.ecc']}});
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) E('circle', {cx: X(c), cy: Y(r), r: H[c][r] ? 9 : 3, class: H[c][r] ? 'jn' : 'w'}, ge);
  KTT(L, -150, Y(2) + 6, 'XOR rows', 't-smb');
  cpart(L, ap, 'syn', -110, 400, 300, 110, CC.logic, 'syndrome', 'lib.xor', {sub: ['stored vs recomputed', 'check bits: 5 XORs'], ty: 40, info: {title: 'The syndrome', lead: 'On a read the check bits are computed again and XORed with the stored ones: all zeros means no error; otherwise the pattern names the bit.', facts: ['tb.ecc']}});
  cpart(L, ap, 'fix', 260, 400, 300, 110, CC.logic, 'correct', 'lib.decoder', {sub: ['the syndrome decoded', 'flips that one bit'], ty: 40, info: {title: 'Correction', lead: 'A decoder turns the syndrome into a one-hot mask, and an XOR per bit flips the bad one back.', facts: ['tb.ecc']}});
  cpart(L, ap, 'ded', 630, 400, 300, 110, CC.logic, 'detect two', 'lib.nor2', {sub: ['a syndrome but even', 'overall parity: two errors'], ty: 40, info: {title: 'Double errors', lead: 'If the syndrome is not zero but the overall parity checks out, two bits flipped: that is reported, not corrected.', facts: ['tb.ecc']}});
  cnote(L, ['64 data bits take 8 check bits: one flipped bit corrected, two detected. The shire cache keeps such codes on its tags, tag states and data', 'R. Hamming (1950), M. Hsiao (1970); Weste and Harris, CMOS VLSI Design, ch. 11'], 628, 'tb.ecc ml:l2:l2.ecc');
}, def: () => ({id: 'lib.xor'}), kids: () => [{id: 'lib.xor'}, {id: 'lib.decoder'}, {id: 'lib.nor2'}]});

/* ---- a read-only memory: a transistor where a 0 is stored ---- */
bnode('lib.rom', {draw: (L, ap) => {
  KT.frame(L, {title: 'A read-only memory (NOR ROM)', sub: '4 words of 4 bits drawn: precharged bitlines; a transistor where a bit is 0 pulls its line down when its row rises', subf: 'tb.rom', col: CC.store, tags: GT});
  const bx = c => 300 + c * 150, wy = r => 180 + r * 100, DATA = [[1, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 1], [0, 0, 1, 0]];
  const gp = cgrp(L, ap, 'pre', 'The precharge: a PMOS per bitline pulls it high before each read', {x: bx(0) - 40, y: 60, w: bx(3) - bx(0) + 80, h: 80}, 'lib.finfet', {tr: 'jump'});
  for (let c = 0; c < 4; c++) { KT.mosV(gp, bx(c), 100, {p: true, lead: 30}); KT.wire(L, [[bx(c), 130], [bx(c), 560]]); KTT(L, bx(c) + 8, 552, `bit ${c}`, 't-sm'); }
  KT.rail(L, bx(0) - 60, bx(3) + 60, 70, '');
  const gd = cgrp(L, ap, 'dec', 'The row decoder: the address raises one wordline', {x: -150, y: 150, w: 240, h: 360}, 'lib.decoder');
  boxG(gd, -140, 160, 200, 340, 'row decoder');
  const gc = cgrp(L, ap, 'cells', 'The cells: a transistor where the stored bit is 0, none where it is 1', {x: bx(0) - 70, y: wy(0) - 40, w: bx(3) - bx(0) + 140, h: wy(3) - wy(0) + 80}, 'lib.finfet', {tr: 'jump'});
  for (let r = 0; r < 4; r++) {
    KT.wire(L, [[60, wy(r)], [bx(3) + 50, wy(r)]], 'thin'); KTT(L, 66, wy(r) - 8, `word ${r}`, 't-sm');
    for (let c = 0; c < 4; c++) if (!DATA[r][c]) { const m = KT.mosV(gc, bx(c) - 44, wy(r) + 40, {lead: 18}); KT.wire(gc, [[m.gate.x, m.gate.y], [m.gate.x, wy(r)]]); KT.jn(gc, m.gate.x, wy(r)); KT.wire(gc, [[m.x, m.top.y], [m.x, wy(r) + 6], [bx(c), wy(r) + 6]]); KT.jn(gc, bx(c), wy(r) + 6); KT.gnd(gc, m.x, m.bot.y + 10); }
  }
  const go = cgrp(L, ap, 'out', 'The outputs: an inverter per bitline gives the bit', {x: bx(0) - 40, y: 566, w: bx(3) - bx(0) + 80, h: 70}, 'lib.inverter');
  for (let c = 0; c < 4; c++) KT.invSym(go, bx(c) + 14, 600, {s: 16});
  cnote(L, ['the vector unit\'s transcendental functions (2ˣ, log₂ x, 1/x) read their coefficients from small tables of this kind', 'Weste and Harris, CMOS VLSI Design, ch. 12'], 668, 'tb.rom et.trans-rom');
}, def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}, {id: 'lib.decoder'}, {id: 'lib.inverter'}]});

/* ---- an SRAM sense amplifier: a latch that turns a small difference into a full 0 or 1 ---- */
bnode('lib.senseamp', {draw: (L, ap) => {
  KT.frame(L, {title: 'A sense amplifier, in transistors', sub: 'two cross-coupled inverters and a tail switch: tens of millivolts between two bitlines become a full 0 or 1', subf: 'tb.senseamp', col: CC.store, tags: [['generic', 'textbook']]});
  KT.rail(L, 160, 700, 40, 'VDD'); KT.rail(L, 160, 700, 600, 'GND');
  const gl = cgrp(L, ap, 'pair', 'The cross-coupled pair: two inverters, each driving the other\'s input', {x: 230, y: 110, w: 380, h: 330}, 'lib.inverter',
    {info: {title: 'The cross-coupled inverters', lead: 'Two inverters in a loop, like an SRAM cell\'s: once the tail switch fires, whichever side starts a little lower is pulled to 0 and the other to 1.', facts: ['tb.senseamp']}});
  const pl = KT.mosV(gl, 300, 170, {p: true, lead: 30}), pr = KT.mosV(gl, 540, 170, {p: true, lead: 30, flip: true}), nl = KT.mosV(gl, 300, 370, {lead: 30}), nr = KT.mosV(gl, 540, 370, {lead: 30, flip: true});
  KT.wire(L, [[300, 40], [300, pl.top.y]]); KT.wire(L, [[540, 40], [540, pr.top.y]]);
  KT.wire(L, [[300, pl.bot.y], [300, nl.top.y]]); KT.wire(L, [[540, pr.bot.y], [540, nr.top.y]]);
  KT.wire(L, [[300, 270], [430, 270], [pr.gate.x + 0, 200], [pr.gate.x, nr.gate.y]], 'thin'); KT.wire(L, [[540, 270], [410, 270], [pl.gate.x, 200], [pl.gate.x, nl.gate.y]], 'thin');
  KT.jn(L, 300, 270); KT.jn(L, 540, 270);
  KT.wire(L, [[300, nl.bot.y], [300, 470], [540, 470], [540, nr.bot.y]]);
  cpart(L, ap, 'tail', 380, 470, 80, 90, 'var(--c2)', '', 'lib.finfet', {label: 'The tail switch: SAE fires the amplifier', tr: 'jump', info: {title: 'The tail switch', lead: 'One NMOS under the pair: while it is off the amplifier waits; when the sense-enable (SAE) turns it on, the pair resolves in a few tens of picoseconds.', facts: ['tb.senseamp']}});
  const tn = KT.mosV(L, 420, 515, {lead: 30}); KT.wire(L, [[420, 470], [420, tn.top.y]]); KT.wire(L, [[420, tn.bot.y], [420, 600]]); KT.netLab(L, tn.gate.x - 8, tn.gate.y + 6, 'SAE', 'end');
  KT.wire(L, [[300, 270], [120, 270]]); KT.netLab(L, 112, 276, 'BL', 'end'); KT.wire(L, [[540, 270], [760, 270]]); KT.netLab(L, 768, 276, 'BL̄');
  cpart(L, ap, 'pre', 640, 330, 300, 110, 'var(--c5)', 'precharge', 'lib.finfet', {sub: ['PMOS hold both bitlines', 'high between reads'], ty: 40, tr: 'jump', info: {title: 'Precharge and equalise', lead: 'Between reads, PMOS transistors hold both bitlines at the supply and short them together, so that a read starts from equal voltages.', facts: ['tb.senseamp']}});
  cnote(L, ['a read lets the cell pull one bitline down a little; the amplifier makes it a full 0 long before the line itself would get there', 'Weste and Harris, CMOS VLSI Design, ch. 12'], 648, 'tb.senseamp');
}, def: () => ({id: 'lib.finfet'}), kids: () => [{id: 'lib.finfet'}, {id: 'lib.inverter'}]});

/* ================= every part leads somewhere (the "no dead ends" rule) =================
   For each scale, the parts that had no closer drawing: the scale they now lead to (a textbook construction above,
   or a drawing of the chip's own), by the part's key. A string is a scale with no instances (its seat is the part's
   box, an instance key added when another part already leads there); a function gives the path element; false marks a
   part that is not the ET-SoC-1's (the host's processor, the card's regulators): its panel says so, and the test lets
   it be (EXT below). */
function linkParts(L, ap, map, P) {
  const todo = [...L.querySelectorAll('.comp')].filter(g => g._kid == null && !g._go && map[g._key] !== undefined && !kidOf(g));
  if (!todo.length) return;
  const need = todo.filter(g => !g._box);
  if (need.length) KT.measured(L, () => need.forEach(g => { try { const r = g.getBBox(); if (r.width || r.height) g._box = {x: r.x, y: r.y, w: r.width, h: r.height}; } catch (_) { /* not rendered */ } }));
  const n = {};
  todo.forEach(g => {
    const m = map[g._key];
    if (m === false) { g._ext = true; return; }
    // a part whose closer drawing is further in, through the scales between (the card's edge: its lanes end at the chip's
    // PCIe PHY): a path of its own, as the ring's ways back in are
    if (m.go) { g._go = () => m.go(P); g._kid = {id: m.kid}; return; }
    const i = n[g._key] = (n[g._key] || 0) + 1;
    const el = typeof m === 'function' ? m(g._ctx || {}, g, P, i) : m;
    if (!el) return;
    const e0 = typeof el === 'string' ? {id: el} : el, N0 = NODES[e0.id];
    let rule = null; if (N0 && N0.seat && !hasParse(e0.id)) { try { rule = N0.seat(ap, prm(e0), P[P.length - 1], L); } catch (_) { rule = null; } }
    g._kid = claim(ap, el, g._key + (i > 1 ? i : ''), g._box, g, typeof m === 'string' && /^lib\.(finfet|si|channel)$|^p\./.test(m) ? 'jump' : null, rule);
  });
}
const LINKS = {};
function links(id, map) {
  const N0 = NODES[id]; if (!N0) { console.error('links: no scale ' + id); return; }
  LINKS[id] = map;
  const b0 = N0.build;
  N0.build = (L, ap, p, P, d) => { b0(L, ap, p, P, d); linkParts(L, ap, map, P.slice(0, d + 1)); };
}
const MS0 = (c, g, P) => { const e = P.find(x => x.id === 'memshire' || x.id === 'memshire.phy'); return e ? String(e.k).split('.')[0] : '0'; };
links('card', {lpddr: (c, g, P, i) => {
  // (which memory shires each package serves is not recorded: each opens a channel of a memory shire of its own, as an
  // example, and its panel says so)
  if (g._info && !/not recorded/.test(g._info.lead || '')) g._info = Object.assign({}, g._info, {lead: (g._info.lead || '') + ' Which two memory shires each package serves is not recorded: the zoom opens one channel as an example.'});
  return {id: 'dram', k: `${2 * (i - 1)}.${DRX().ch}`};
}, edge: {kid: 'package', go: P => P.concat([{id: 'package'}, {id: 'die'}, {id: 'pcie'}, {id: 'pcie.phy'}])}, vrm: false, ltm: false, dip: false, board: 'package'});
links('host', {board: 'card', cpu: false, dimms: false, psu: false});
links('rack', {photo: 'host'});
links('package', {body: 'die', side: 'die', balls: 'die'});
links('die', {inferred: false});
/* the die itself (its outline on the die's drawing) opens the die in section, at the section's own seat */
KIDS.chip = () => ({id: 'die.metal'});
links('dram', {cmd: (c, g, P) => ({id: 'dram.bank', k: `${dk(P[P.length - 1].k).ms}.${dk(P[P.length - 1].k).ch}.${DRX().bank}`}),
  prefetch: (c, g, P) => ({id: 'dram.bank', k: `${dk(P[P.length - 1].k).ms}.${dk(P[P.length - 1].k).ch}.${DRX().bank}`}),
  pins: (c, g, P) => ({id: 'dram.bank', k: `${dk(P[P.length - 1].k).ms}.${dk(P[P.length - 1].k).ch}.${DRX().bank}`}),
  tl: (c, g, P) => ({id: 'dram.bank', k: `${dk(P[P.length - 1].k).ms}.${dk(P[P.length - 1].k).ch}.${DRX().bank}`})});
links('dram.bank', {rowdec: 'dram.cell', mat: 'dram.cell', swd: 'dram.cell', blsa: 'dram.cell', coldec: 'dram.cell', gio: 'dram.cell'});
links('dram.cell', {wld: 'lib.dramcell', eq: 'lib.dramcell', sa: 'lib.dramcell', csl: 'lib.dramcell', wdrv: 'lib.dramcell'});
links('lib.dramcell', {access: 'lib.si', bitline: 'lib.si', cap: 'p.electron'});
links('pcie', {'pcie.ctrl': 'lib.logic'});
links('pcie.phy', {'pcie.lane': 'lib.inverter'});
links('io', {'io.maxion': 'lib.logic', 'io.sp': 'core', 'io.pll': 'lib.pll', 'io.pvt': 'lib.logic', 'io.periph': 'lib.logic'});
links('memshire', {vddr: (c, g, P) => ({id: 'memshire.phy', k: MS0(c, g, P)}), noc: 'lib.fifo', xing: 'shire.meshstop.xing', strip: 'lib.mux2', settings: 'lib.flipflop',
  atomic: 'lib.adder', perfmon: 'lib.counter', ctl: 'lib.logic', dfi: 'lib.flipflop', lat63: 'lib.fifo'});
links('memshire.phy', {dfiin: 'lib.flipflop', pll: 'lib.pll', anib: (c, g, P) => ({id: 'memshire.phy.dq', k: MS0(c, g, P)}), dbyte: (c, g, P) => ({id: 'memshire.phy.dq', k: MS0(c, g, P)}),
  topkg: (c, g, P) => ({id: 'memshire.phy.dq', k: MS0(c, g, P)})});
links('memshire.phy.dq', {trace: 'die.metal', dbi: 'lib.xor', ioE: 'lib.finfet'});
links('mesh', {bankR: 'lib.fifo', tol3: 'lib.fifo', vcdown: 'shire.meshstop.xing', slave: 'lib.fifo', router: 'shire.meshstop.router', router2: 'shire.meshstop.router',
  more: 'mesh.link.wire', flits: 'mesh.link.wire', hopE: 'mesh.link.wire', nochop: 'shire.meshstop.router'});
links('mesh.link.wire', {wireC: 'die.metal', bitE: 'lib.inverter'});
links('die.metal', {wires: 'lib.finfet', bumps: 'lib.finfet'});
links('shire.meshstop.router', {'shire.meshstop.router.buf': 'lib.fifo', 'shire.meshstop.router.alloc': 'lib.logic', 'shire.meshstop.router.xbar': 'lib.mux2'});
links('shire.uc', {'shire.uc.flb': 'lib.counter', 'shire.uc.fcc': 'lib.counter'});
links('shire.xbar', {'shire.xbar.req': 'lib.mux2', 'shire.xbar.rsp': 'lib.mux2'});
links('shire.neigh', {'shire.neigh.icache': 'lib.sram6t', 'shire.neigh.l0': 'lib.regfile', 'shire.neigh.req': 'lib.fifo', 'shire.neigh.rsp': 'lib.fifo', 'shire.neigh.pmu': 'lib.counter'});
links('shire.bank', {reqq: 'lib.fifo', arb: 'lib.logic', order: 'lib.logic', rbuf: 'lib.regfile', dataq: 'lib.regfile', cbuf: 'lib.regfile', atomic: 'lib.adder',
  perfmon: 'lib.counter', hpf: 'lib.logic', rspmux: 'lib.mux2', pipe: 'lib.flipflop', tol3: 'lib.fifo'});
links('shire.subbank', {tagram: 'lib.sram6t', stateram: 'lib.sram6t', ecc: 'lib.ecc', cmp: 'lib.cmpeq', zero: 'lib.sram6t', rowaddr: 'lib.decoder', dc: 'lib.mux2'});
links('shire.panel', {periph: 'lib.decoder', pre: 'lib.sram6t', mux: 'lib.mux2', sa: 'lib.senseamp', olat: 'lib.latch', band: 'lib.sram6t', icg: 'lib.icg', trim: 'lib.sram6t', geom: 'lib.sram6t'});
links('lib.sram6t', {half: 'lib.finfet'});
links('minion', {hart: 'core', etlink: 'shire.meshstop.xing', fln: 'mesh.link.wire'});
links('core', {'core.fe': 'lib.logic', 'core.irf': 'lib.regfile', 'core.alu': 'lib.adder', 'core.muldiv': 'lib.booth', 'core.csr': 'lib.flipflop'});
links('vpu', {'vpu.shsw': 'lib.mux2'});
links('vpu.lane', {'vpu.lane.vrf': 'lib.regfile', 'vpu.lane.tima': 'lib.booth', 'vpu.lane.trans': 'lib.rom'});
links('tensor', {'tensor.fsm': 'lib.counter', 'tensor.tenb': 'lib.regfile', 'tensor.tenc': 'lib.regfile'});
links('l1d', {tags: 'lib.regfile', valid: 'lib.flipflop', lru: 'lib.flipflop', hit: 'l1d.cmp', pma: 'lib.cmpeq', s4arb: 'lib.logic', setmap: () => ({id: 'l1d.block', k: String(L1X().block)})});
links('l1d.cmp', {andtree: 'lib.nand2', ways: 'lib.nor2'});
links('l1d.block', {wlatch: 'lib.latch', wdec: 'lib.decoder', icg: 'lib.icg', rdreg: 'lib.flipflop', oreg: 'lib.flipflop'});
links('l1d.row', {icg: 'lib.icg', row: 'lib.latch', muxtree: 'lib.mux2'});
links('vpu.lane.fma', {fmabooth: 'lib.booth', fmaalign: 'lib.shifter', fmaadd: 'lib.adder', fmalzd: 'lib.lzd', fmanorm: 'lib.shifter', fmarnd: 'lib.adder', fmazero: 'lib.icg'});
links('vpu.lane.fma.tree', {treedots: 'lib.booth', treelevels: 'lib.cmp42'});
links('fma.tree.col', {colbits: 'lib.booth'});
links('lib.cmp42', {fa2: 'lib.fa'});
links('lib.fa', {majority: 'lib.nand2', fatable: 'lib.xor'});
links('lib.xor', {pun: 'lib.finfet', pdn: 'lib.finfet', xtable: 'lib.finfet'});
links('lib.inverter', {gtable: 'lib.finfet'});
links('lib.nand2', {gtable: 'lib.finfet'});
links('lib.mux2', {mtable: 'lib.finfet'});
links('lib.flipflop', {slave: 'lib.latch'});
links('lib.finfet', {cell: 'lib.fin', fins: 'lib.fin', contacts: 'lib.channel', gates: 'lib.fin'});
links('lib.fin', {substrate: 'lib.si', gatestack: 'lib.channel', fin0: 'lib.channel', fin1: 'lib.channel', fin2: 'lib.channel'});
links('lib.channel', {sd: 'p.dopant', chan: 'lib.si', bands: 'lib.si'});
links('lib.si', {cube: 'p.atom', bonds: 'p.atom', atoms: 'p.atom', gap: 'p.atom'});
links('p.dopant', {lattice: 'p.atom', fifth: 'p.electron', phos: 'p.nucleon'});
Object.assign(NODES['p.dopant'], {def: () => ({id: 'p.atom'}), kids: () => [{id: 'p.atom'}, {id: 'p.electron'}, {id: 'p.nucleon'}]});
links('p.atom', {bonds: 'p.electron', shells: 'p.electron', valence: 'p.electron'});
links('p.nucleus', {nucleons: 'p.nucleon'});
links('p.nucleon', {field: 'p.quark', quarks: 'p.quark'});
links('p.quark', {bound: 'p.planck'});
links('p.electron', {bound: 'p.planck'});
/* the scales that had no way further in: the I/O shire and the PCIe PHY */
Object.assign(NODES.io, {def: () => ({id: 'core'}), kids: () => [{id: 'core'}, {id: 'lib.pll'}, {id: 'lib.logic'}]});
Object.assign(NODES['pcie.phy'], {def: () => ({id: 'lib.inverter'}), kids: () => [{id: 'lib.inverter'}]});
NODES.pcie.kids = () => [{id: 'pcie.phy'}, {id: 'lib.logic'}];
