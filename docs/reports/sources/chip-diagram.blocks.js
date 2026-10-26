/* ================= chip-diagram.blocks.js: the chip's block scenes and its compute chain (1 October 2026) =================
   Split from chip-diagram.inside.js (30 September): the logical drawings of the blocks no floorplan shows, and a
   vector lane's multiply-add down to one column of its compressor tree. The chip page's, and since 1 Oct (the shared
   ladder, part 2) the memory levels' too: their parts open the same block scenes (a crossbar, the UC, the core, the
   vector unit, the tensor unit, the PCIe and I/O shires), and the textbook constructions draw with its helpers. */
/* ================= the block scenes, and the compute ladder down to the silicon crystal (Phase 3b) =================
   A block of the chip whose inside is described but not published as a floorplan (a router, a crossbar, a core, the
   vector unit and its lanes, the tensor sequencer, the PCIe and I/O shires) is drawn from the tree's data: its parts as
   labelled boxes, a logical drawing, not a floorplan; a part with a drawing of its own zooms into it, the others give
   their text and what they are made of. Then the compute ladder, hand-drawn: a lane's fused multiply-add, its
   compressor tree, one column, a 4:2 compressor, a full adder, an XOR gate's transistors, the FinFET at TSMC N7's
   pitches, its fin in section, the channel, and the silicon crystal. Circuits are textbook unless a chip document
   gives them; facts from core-et's Erbium RTL carry that caveat. */
const KT = CKT.kit, CC = CKT.COL;
const sc = id => ISC[id] || {};
/* a node's first sentence, cut at a word to at most `max` characters with "…" (final check, 1 Oct: cutting at the first
   colon or semicolon left 30 boxes ending "lanes:", "One block:"; a wide box now shows as much as its lines hold) */
const firstClause = (t, max = 96) => {
  const s = String(t || ''), m = /^.*?[.!?](?=\s|$)/.exec(s), s0 = m ? m[0] : s;
  return s0.length > max ? s0.slice(0, max - 1).replace(/\s+\S*$/, '').replace(/[\s,;:]+$/, '') + '…' : s0;
};
/* words wrapped into lines of at most n characters */
function wrapW(t, n) {
  const out = []; let cur = '';
  String(t || '').split(/\s+/).forEach(w => { if (!w) return; if (cur && (cur + ' ' + w).length > n) { out.push(cur); cur = w; } else cur = cur ? cur + ' ' + w : w; });
  if (cur) out.push(cur);
  return out;
}
/* a part of the drawings drawn here: its panel from the tree (title, lead, facts) unless given; its zoom, its seat */
function ipart(L, ap, key, x, y, w, h, col, title, o) {
  o = o || {};
  const g = KT.part(L, key, x, y, w, h, col, title, {sub: o.sub, kind: o.kind, ctx: o.ctx, center: o.center, fo: o.fo, tcls: o.tcls, ty: o.ty, label: o.label, lh: o.lh});
  const s0 = sc(o.node || key);
  g._info = o.info || {title: s0.name || title, lead: s0.blurb || '', facts: s0.facts || [], kick: o.kick};
  if (o.kid) { g._kid = o.kid; ap.zs[pk(o.kid)] = {r: o.seat || {x, y, w, h}, g, tr: o.tr}; }
  if (o.opts) g._opts = o.opts;
  return g;
}
/* the shared circuits a part is made of, as zoom options (each drawn in this scene's "made of" row) */
const madeOf = id => P => (sc(id).see || []).filter(x => NODES[x]).map(x => ({lab: sc(x).name || x, to: P.concat([{id: x}]), made: true}));
/* a copied scene's line under its frame's title, its notes and its other one-line labels (a part's own, where the part
   has no box for fitTexts to fit them in): where the type in force (a short screen's or a phone's, 21 units, not 17) or a
   wide face carries one that starts inside the frame past its inner edge, it is set smaller to fit, never below 15 units
   (Antigravity's audit of 14 Oct: at 1280 x 720 seven of these lines and fifteen notes ran past the frame, ten of them
   off the screen). The ladder's buildInto runs it on every copied scene. */
function fitLines(L) {
  const FR = CKT.FR, xr = FR.x + FR.w - 18;
  KT.measured(L, () => L.querySelectorAll(':scope > g.frm > text.t-sm, :scope > text.t-sm, :scope > g.comp > text.t-sm').forEach(t => {
    if ((t.getAttribute('text-anchor') || 'start') !== 'start' || t.hasAttribute('transform') || [...t.children].some(s => parseFloat(s.getAttribute('dy')))) return;
    if (t.parentNode.classList.contains('comp') && t.parentNode.querySelector(':scope > rect.shape')) return;
    let b; try { b = t.getBBox(); } catch (_) { return; }
    if (!b.width || b.x >= xr || b.x + b.width <= xr) return;
    const fs = parseFloat(getComputedStyle(t).fontSize) || 17, nfs = Math.max(Math.min(fs, 15), Math.floor(fs * (xr - b.x) / b.width * 10) / 10);
    if (nfs < fs) t.style.fontSize = nfs + 'px';
  }));
}
/* a node drawn here: the tree's name, lead and size; its frame the copied drawings' frame */
function bnode(id, o) { return inode(id, Object.assign({}, o, {build: (L, ap, p, P, d) => CKT.build((L2, ap2, inst) => o.draw(L2, ap2, p, P, d), L, ap, {}, null)})); }
/* ---- a block scene from the tree: its children as boxes, instances in a row, what they are made of below ---- */
function blockScene(id, L, ap, p, P, o) {
  o = o || {};
  const s0 = sc(id);
  KT.frame(L, {title: o.title || s0.name, sub: firstClause(s0.blurb), col: CC.logic,
    tags: [['documented', 'logical drawing, not a floorplan']].concat(s0.erbium ? [['unknown', 'some facts: Erbium RTL']] : [])});
  const kids = (o.kids || s0.kids || []).filter(k => sc(k).name && !(o.inst && k === o.inst.id));
  const see = [...new Set([].concat(s0.see || [], ...kids.map(k => sc(k).see || [])))].filter(x => NODES[x]);
  const X0 = -150, W = 1220;
  let y = 20;
  if (o.inst) {
    const n = o.inst.n, gw = 14, bw = (W - gw * (n - 1)) / n, bh = o.inst.h || 150;
    for (let i = 0; i < n; i++) {
      const x = X0 + i * (bw + gw), el = o.inst.el(i), s1 = sc(el.id);
      ipart(L, ap, el.id, x, y, bw, bh, o.inst.col || CC.logic, o.inst.title(i), {node: el.id, ctx: {i}, kid: NODES[el.id] ? el : null, center: true, ty: bh / 2 - 6,
        sub: o.inst.sub ? [o.inst.sub(i)] : [], info: {title: o.inst.title(i), lead: s1.blurb || '', facts: s1.facts || []}});
    }
    y += bh + 26;
  }
  // (review of 1 Oct: at 1024 x 768 the type is 21 units and the lines, 21 apart, touched and ran into the boxes'
  // right edges: the text wraps for that size, a line is 25 units, a box shows at most three lines, the rest is in its
  // panel, and the boxes share the card's height)
  const H = (see.length ? 560 : 650) - y, n = kids.length, LH = 25, CW = 11.6;
  if (n) {
    const cols = n <= 3 ? n : n <= 4 ? 2 : n <= 6 ? 3 : 4, rows = Math.ceil(n / cols), gw = 18, gh = 18;
    const bw = (W - gw * (cols - 1)) / cols, wrapAt = Math.max(16, Math.floor((bw - 24) / CW));
    // the boxes as tall as their text needs (title and up to three lines), the group centred in the card's free height
    const most = Math.min(3, Math.max(1, ...kids.map(k => wrapW(firstClause(sc(k).blurb, 3 * wrapAt), wrapAt).length)));
    const bh = Math.min(260, (H - gh * (rows - 1)) / rows, 50 + 23 + LH * most + 22);
    const y1 = y + Math.max(0, (H - rows * bh - gh * (rows - 1)) * 0.4);
    kids.forEach((k, i) => {
      const r = Math.floor(i / cols), c = i % cols, x = X0 + c * (bw + gw), yy = y1 + r * (bh + gh), s1 = sc(k);
      const cap = Math.max(1, Math.min(3, Math.floor((bh - 50) / LH))), all = wrapW(firstClause(s1.blurb, cap * wrapAt), wrapAt);
      const lines = all.slice(0, cap); if (all.length > cap) lines[cap - 1] = lines[cap - 1].replace(/[,;:.]?\s*\S*$/, '…');
      // (since 1 Oct a part with no scale of its own leads to a textbook construction, ladder-circuits.js LINKS: it is drawn
      // as a part with a zoom too)
      const lk = typeof LINKS !== 'undefined' && LINKS[id] ? LINKS[id][k] : undefined, has = !!NODES[k] || (lk != null && lk !== false), nm = String(s1.name || k).replace(/\s*\(.*$/, '');
      ipart(L, ap, k, x, yy, bw, bh, has ? CC.logic : 'var(--ink-2)', nm.length < bw / 11 ? nm : s1.short && s1.short.length < bw / 11 ? s1.short : wrapW(nm, Math.floor(bw / 11))[0],
        {node: k, kid: NODES[k] ? {id: k} : null, sub: lines, fo: has ? 0.12 : 0.06, opts: has ? null : madeOf(k), lh: LH, ty: 40});
    });
  }
  if (see.length) {
    T(L, X0, 600, 'made of:', 't-smb');
    let x = X0 + 90;
    see.forEach(sid => {
      const nm = sc(sid).short || sid, w = Math.max(110, nm.length * 10 + 26);
      if (x + w > X0 + W) return;
      ipart(L, ap, sid, x, 578, w, 44, 'var(--c3)', nm, {node: sid, kid: {id: sid}, center: true, ty: 28, fo: 0.14, tcls: 't-sm'});
      x += w + 10;
    });
  }
  T(L, X0, 676, 'a logical drawing: what the parts are and what they do; no floorplan of the inside is published', 't-sm');
}
const shireOf = P => { const i = P.findIndex(e => e.id === 'shire'); return i >= 0 ? +P[i].k : 0; };
bnode('shire.meshstop', {draw: (L, ap, p, P) => blockScene('shire.meshstop', L, ap, p, P), seat: (ap, p, pel, Lp) => partBox(Lp, 'meshstop'),
  def: () => ({id: 'shire.meshstop.router'}), kids: () => [{id: 'shire.meshstop.router'}, {id: 'shire.meshstop.xing'}]});
bnode('shire.meshstop.router', {draw: (L, ap, p, P) => blockScene('shire.meshstop.router', L, ap, p, P), def: () => ({id: 'lib.flipflop'})});
bnode('shire.uc', {draw: (L, ap, p, P) => blockScene('shire.uc', L, ap, p, P), seat: (ap, p, pel, Lp) => partBox(Lp, 'uc'), def: () => ({id: 'lib.flipflop'})});
bnode('shire.xbar', {draw: (L, ap, p, P) => blockScene('shire.xbar', L, ap, p, P), seat: (ap, p, pel, Lp) => partBox(Lp, 'xbar'), def: () => ({id: 'lib.mux2'})});
bnode('shire.neigh', {parse: k => ({nb: +k}), name: p => `Neighbourhood ${p.nb}`, short: p => `Neighbourhood ${p.nb}`, to: p => `neighbourhood ${p.nb}`,
  draw: (L, ap, p, P) => { const sid = shireOf(P); blockScene('shire.neigh', L, ap, p, P, {title: `Neighbourhood ${p.nb} of shire ${sid}`,
    inst: {n: 8, id: 'minion', el: i => ({id: 'minion', k: `${sid}.${p.nb}.${i}`}), title: i => `M${i}`, sub: i => `minion ${i}`, h: 130}}); },
  seat: (ap, p, pel, Lp) => (ap.nbx && ap.nbx[p.nb] ? {r: ap.nbx[p.nb], g: partBox(Lp, 'neigh', c => c.nb === p.nb) ? partBox(Lp, 'neigh', c => c.nb === p.nb).g : null} : null),
  def: (p, P) => ({id: 'minion', k: `${shireOf(P)}.${p.nb}.0`})});
bnode('core', {draw: (L, ap, p, P) => blockScene('core', L, ap, p, P, {title: 'The minion core'}), seat: (ap, p, pel, Lp) => partBox(Lp, 'minion', c => c.mi == null), def: () => ({id: 'lib.flipflop'})});
bnode('vpu', {draw: (L, ap, p, P) => blockScene('vpu', L, ap, p, P, {inst: {n: 8, id: 'vpu.lane', el: i => ({id: 'vpu.lane', k: String(i)}), title: i => `lane ${i}`, sub: () => '32 bits', h: 170}}),
  seat: (ap, p, pel, Lp) => partBox(Lp, 'vpu'), def: () => ({id: 'vpu.lane', k: '0'}), kids: () => [0, 1, 2, 3, 4, 5, 6, 7].map(i => ({id: 'vpu.lane', k: String(i)}))});
bnode('vpu.lane', {parse: k => ({lane: +k}), name: p => `Lane ${p.lane} of the vector unit`, short: p => `Lane ${p.lane}`, to: p => `lane ${p.lane}`,
  draw: (L, ap, p, P) => blockScene('vpu.lane', L, ap, p, P, {title: `Lane ${p.lane} of the vector unit`}), def: () => ({id: 'vpu.lane.fma'}), kids: () => [{id: 'vpu.lane.fma'}]});
bnode('tensor', {draw: (L, ap, p, P) => blockScene('tensor', L, ap, p, P), seat: (ap, p, pel, Lp) => partBox(Lp, 'tensor'), def: () => ({id: 'lib.latch'})});
bnode('pcie', {draw: (L, ap, p, P) => blockScene('pcie', L, ap, p, P), seat: (ap, p, pel, Lp) => cellSeat(Lp, 'pcie'), def: () => ({id: 'pcie.phy'})});
bnode('pcie.phy', {draw: (L, ap, p, P) => blockScene('pcie.phy', L, ap, p, P, {inst: {n: 8, id: 'pcie.lane', el: i => ({id: 'pcie.lane', k: String(i)}), title: i => `lane ${i}`, sub: () => '16 GT/s', h: 120}})});
bnode('io', {draw: (L, ap, p, P) => blockScene('io', L, ap, p, P), seat: (ap, p, pel, Lp) => cellSeat(Lp, 'io')});
function cellSeat(Lp, type) { const c = CELLS.find(x => x.type === type); return c ? {r: {x: c.x + INS, y: c.y + INS, w: c.w - 2 * INS, h: c.h - 2 * INS}, g: c.g || null} : null; }
Object.assign(KIDS, {
  minion: c => (c.mi != null ? {id: 'minion', k: `${c.sid}.${c.nb}.${c.mi}`} : {id: 'core'}),
  vpu: () => ({id: 'vpu'}), tensor: () => ({id: 'tensor'}), meshstop: () => ({id: 'shire.meshstop'}), uc: () => ({id: 'shire.uc'}), xbar: () => ({id: 'shire.xbar'}),
  neigh: c => ({id: 'shire.neigh', k: String(c.nb != null ? c.nb : 0)}), pcie: () => ({id: 'pcie'}), io: () => ({id: 'io'}),
});
/* parts with no scale of their own: the zooms they do have */
Object.assign(OPTS, {
  hart: (c, P) => [{lab: 'The minion core (its integer registers)', to: P.concat([{id: 'core'}])}, {lab: 'The vector unit (its vector registers)', to: P.concat([{id: 'vpu'}])}],
  // (the minion's own neighbourhood's bank FIFOs, not the mesh stop's crossing: review of 14 Oct)
  etlink: (c, P) => { const i = P.findIndex(e => e.id === 'shire'), m = P.find(e => e.id === 'minion'), nb = m ? String(m.k).split('.')[1] || '0' : '0';
    return i < 0 ? [] : [{lab: 'The crossing into the shire’s clock and voltage (level shifter, FIFO)', to: P.slice(0, i + 1).concat([{id: 'shire.neigh', k: nb}, {id: 'shire.neigh.xing'}])}]; },
  fln: (c, P) => { const i = P.findIndex(e => e.id === 'die'); return i < 0 ? [] : [{lab: 'A wire and its repeaters (a mesh link, up close)', to: P.slice(0, i + 1).concat([{id: 'mesh'}, {id: 'mesh.link.wire'}]), made: true}]; },
  chip: (c, P) => [{lab: 'The die in cross-section: transistors and the wiring stack', to: P.concat([{id: 'die.metal'}])}, {lab: 'A compute shire', to: P.concat([{id: 'shire', k: String(isShire(LASTSID) ? LASTSID : 0)}])}],
});

/* ---- the compute ladder: a lane's fused multiply-add down to the silicon crystal ---- */
const KTT = (...a) => KT.T(...a);   // the kit's text: a memory-levels fact gets its prefix, the chip's own ids pass
const arrowR = (L, x1, y, x2, cls) => { KT.wire(L, [[x1, y], [x2, y]], cls); E('path', {class: 'w', d: `M${x2 - 9},${y - 6} L${x2},${y} L${x2 - 9},${y + 6}`}, L); };
// TensorFMA32 (23 Oct 2026): the multiply-add as built, from Esperanto's ET-SoC-1 RTL (txfma_7s), down its Wallace tree
const inFma = (P, d) => !!P && P.slice(0, d).some(e => e.id === 'vpu.lane.fma');   // a shared scene reached from the multiply-add (it may then name the multiply-add's own circuits)
const LVA = {1: 4, 2: 2, 3: 1, 4: 1};                                          // arrays per level (txfma_wallace1/2)
const LVIO = {1: '16 → 8 rows', 2: '8 → 4 rows', 3: '4 → 2 rows', 4: '2 rows + row 17 + the sign row → 2'};
const LVST = {1: 'f1', 2: 'f1', 3: 'f2', 4: 'f2'};
const TFARR = {1: ['csa42_11', 'csa42_12', 'csa42_13', 'csa42_14'], 2: ['csa42_21', 'csa42_22'], 3: ['csa42_31'], 4: ['csa41_41']};
const SPAN = {1: [[0, 38], [8, 46], [16, 54], [24, 62]], 2: [[0, 46], [16, 62]], 3: [[0, 62]], 4: [[0, 63]]};   // kept by synthesis
const F32 = {1: [null, [8, 46], [16, 54], [24, 62]], 2: [[8, 46], [16, 62]], 3: [[8, 62]], 4: [[8, 63]]};      // can switch in fp32
const inSpan = (s, i) => !!s && i >= s[0] && i <= s[1];
const LVTR = {1: '10,153', 2: '4,513', 3: '4,537', 4: '2,907'};                  // transistors as built, lane 0 (level 4 with the adder's first layer)
const LVKEPT = {1: '156', 2: '94', 3: '63', 4: '64'};                            // compressors kept by synthesis, per level
const LVBL = {1: 'Rows 1-4, 5-8, 9-12 and 13-16 each go into one array of 64 4:2 compressors and come out as a sum row and a carry row: 16 rows become 8.',
  2: 'The carry rows move one column left; each pair of level-1 arrays goes into one array: 8 rows become 4, which the register between f1 and f2 holds.',
  3: 'After the register, one array takes the four rows to two.', 4: 'The last array adds level 3’s two rows, row 17 and the sign row: 2 rows remain for the product adder.'};
function colIn(lv, a, i) {   // the four inputs of level lv, array a (0-based), column i, in the RTL's order x0..x3; null = a constant 0
  const pp = r => { const b = i - 2 * (r - 1); return b >= 0 && b <= 32 ? `row ${r} bit ${b}` : null; };
  const cr = nm => (i >= 1 ? `${nm}[${i - 1}] (carry, column ${i - 1})` : null), sm = nm => `${nm}[${i}]`;
  if (lv === 1) { const r = 4 * a + 1; return [pp(r) || (a === 0 && i === 33 ? 'the magic one (a constant 1)' : null), pp(r + 1), pp(r + 2), pp(r + 3)]; }
  if (lv === 2) { const q = a ? ['c13', 's13', 'c14', 's14'] : ['c11', 's11', 'c12', 's12']; return [cr(q[0]), sm(q[1]), cr(q[2]), sm(q[3])]; }
  if (lv === 3) return [cr('C21'), sm('S21'), cr('C22'), sm('S22')];
  const x2 = i >= 32 ? `row 17 bit ${i - 32}` : null;
  const x3 = i < 32 ? (i % 2 ? null : `Cin: the +1 of row ${i / 2 + 1}`) : i === 32 ? null : i % 2 ? `Sxt: NOT the sign of row ${(i - 31) / 2}` : 'Sxt: a constant 1';
  return [cr('C31'), sm('S31'), x2, x3];
}
const colShort = s => (!s ? '0' : s.replace(/ \(carry, column \d+\)$/, '').replace(/^Cin: the \+1 of row (\d+)$/, 'Cin of row $1'));
function c42Look(r, lv, a, i) {   // a compressor's box: kept and able to switch in fp32 / kept but idle in fp32 / cut by synthesis
  const kept = inSpan(SPAN[lv][a], i), live = kept && inSpan(F32[lv][a], i);
  if (live) S(r, {fill: 'var(--c1)', fillOpacity: 0.18, stroke: 'var(--c1)', strokeOpacity: 0.6, strokeWidth: 1});
  else if (kept) { r.setAttribute('fill', 'none'); S(r, {stroke: 'var(--c1)', strokeOpacity: 0.4, strokeWidth: 1}); }
  else { r.setAttribute('fill', 'none'); S(r, {stroke: 'var(--grid)', strokeWidth: 1, strokeDasharray: '2 3'}); }
  return {kept, live};
}
const TFR = [255, 223, 606, 340, 263, 238, 146], TFFF = [229, 213, 492, 322, 248, 213, 134];   // the register that starts each stage: RTL bits, flip-flops (lane 0)
const TFST = [
  {t: 'Capture and unpack', lead: 'The operand registers take a, b and c, each behind its own clock gate; the unit splits sign, exponent and significand, reads a denormal as zero, and flags infinities and NaNs. Lane stage F2.', f: ['tfma.stages', 'tfma.regs.stage']},
  {t: 'Booth rows, tree levels 1-2', lead: 'a is Booth-recoded; 16 rows (and row 17) of b are selected and levels 1 and 2 of the Wallace tree take 16 rows to 4. In parallel the product’s exponent ea + eb − 127 and its difference from c’s.', f: ['tfma.booth.rows', 'tfma.tree.levels']},
  {t: 'Levels 3-4, the product', lead: 'The 353-bit register hands the four rows to levels 3 and 4; row 17 and the sign row join at level 4; a 64-bit adder makes the exact product. Control decides which addend to shift and by how much, and the sticky bit from trailing zeros.', f: ['tfma.tree.levels', 'tfma.reg12', 'tfma.padd']},
  {t: 'Align and merge', lead: 'The addend with the smaller exponent (c or the product) is shifted right, inverted if the signs make it a subtraction, and a row of 52 full adders merges it with the other.', f: ['tfma.stages', 'tfma.frame', 'tfma.side']},
  {t: 'Add, anticipate', lead: 'A 52-bit adder sums the two rows while a leading-one anticipator, working on the same inputs, guesses how far the result must shift.', f: ['tfma.stages', 'tb.lza']},
  {t: 'Normalise, decide rounding', lead: 'The sum is shifted into a 34-bit window (a one-bit correction fixes the anticipator’s guess) and the last kept bit, the round bit and the sticky bit decide the rounding.', f: ['tfma.stages', 'tb.round']},
  {t: 'Round, write', lead: 'A 33-bit adder rounds; overflow, underflow, NaN and infinity are settled and six flags set; the result goes to the lane’s register file. Lane stage F8.', f: ['tfma.stages', 'tfma.underflow']},
];
const TFOP = 'The operand register: 32 flip-flops behind a clock gate that opens only for a valid multiply-add.';
const TFPART = [   // [stage, key, y, h, title, sub lines, kid, colour, panel lead (null: the kid's own), facts]
  [0, 'opA', 96, 72, 'a', [], 'lib.flipflop', 'var(--c3)', TFOP, ['tfma.regs.stage', 'tfma.zero']],
  [0, 'opB', 176, 72, 'b', [], 'lib.flipflop', 'var(--c3)', TFOP, ['tfma.regs.stage', 'tfma.zero']],
  [0, 'opC', 256, 72, 'c', [], 'lib.flipflop', 'var(--c3)', TFOP, ['tfma.regs.stage', 'tfma.zero']],
  [0, 'unpack', 340, 110, 'unpack', ['sign · exponent', 'significand', 'denormal → 0'], 'lib.mux2', 'var(--c4)', 'Format multiplexers split sign, exponent and significand; a zero exponent makes the operand a zero (denormals are read as zero).', ['tfma.stages', 'tfma.underflow']],
  [1, 'ppg', 96, 120, 'Booth rows', ['a recoded:', '16 rows + row 17', 'of b'], 'vpu.lane.fma.booth', CC.logic, null],
  [1, 'tree12', 230, 130, 'tree levels 1-2', ['16 → 8 → 4 rows', '4:2 compressors'], 'vpu.lane.fma.tree', CC.logic, null],
  [1, 'trz', 376, 74, 'trailing zeros', ['of a, b, c'], 'lib.lzd', 'var(--c4)', 'Trailing-zero counts of the three significands: later they decide the sticky bit without looking at the shifted-out bits.', ['tfma.stages']],
  [2, 'tree34', 96, 120, 'tree levels 3-4', ['4 + row 17 +', 'sign row → 2'], 'vpu.lane.fma.tree', CC.logic, null],
  [2, 'padd', 230, 90, '64-bit adder', ['the product'], 'lib.adder', CC.logic, 'Adds the tree’s last two rows into the exact 48-bit significand product, in a 64-bit frame.', ['tfma.padd', 'tfma.frame']],
  [2, 'ediff', 336, 114, 'which to shift', ['and how far;', 'sticky from', 'trailing zeros'], 'lib.logic', 'var(--c4)', 'From the exponents: whether c or the product is shifted, by how many places (0 to 49, or zapped beyond), and the sticky bit from trailing zeros.', ['tfma.stages']],
  [3, 'align', 96, 120, 'align', ['shift right', '0-49 places'], 'lib.shifter', 'var(--c4)', 'A 48-bit operand shifted right in a 50-bit window: whichever of c and the product has the smaller exponent.', ['tfma.stages', 'tfma.frame']],
  [3, 'neg', 230, 60, 'invert?', ['if subtracting'], 'lib.xor', 'var(--c4)', 'On an effective subtraction the aligned operand is inverted; its +1 comes later as a carry-in.', ['tfma.stages']],
  [3, 'csa3', 304, 110, '3:2 merge', ['52 full adders'], 'lib.fa', 'var(--c4)', 'A row of 52 full adders merges the two addends (and a third input, zero here) into a sum and a carry row.', ['tfma.stages', 'tfma.side']],
  [4, 'cadd', 96, 150, '52-bit adder', ['the sum'], 'lib.adder', 'var(--c4)', 'A 52-bit carry-propagate adder: the sum of c and the product.', ['tfma.stages']],
  [4, 'lza', 260, 110, 'leading one', ['anticipated', 'from the inputs'], 'lib.lzd', 'var(--c4)', 'Guesses the normalising shift from the adder’s inputs, so it finishes with the adder; it can be one place off.', ['tfma.stages', 'tb.lza']],
  [5, 'norm', 96, 150, 'normalise', ['shift into', '34 bits'], 'lib.shifter', 'var(--c4)', 'Shifts the sum left (or right) into a 34-bit window; a one-bit correction fixes the anticipator’s guess.', ['tfma.stages']],
  [5, 'rdec', 260, 110, 'round?', ['L, R, sticky'], 'lib.round', 'var(--c4)', 'The last kept bit, the round bit and the sticky bit decide whether to add one at the last place (round to nearest even).', ['tfma.stages', 'tb.round']],
  [6, 'rnd', 96, 120, 'round adder', ['33 bits'], 'lib.round', 'var(--c4)', 'A 33-bit adder adds the rounding increment; a carry out bumps the exponent.', ['tfma.stages']],
  [6, 'exc', 230, 120, 'result', ['specials,', '6 flags'], 'lib.logic', 'var(--c4)', 'Overflow, underflow (judged after rounding), NaN and infinity; the result word and six flags go to the lane’s register file.', ['tfma.stages', 'tfma.underflow']],
];
/* the fused multiply-add: a x b + c, the multiplier, the adder and the normaliser, as the RTL names them */
bnode('vpu.lane.fma', {draw: (L, ap) => {
  KT.frame(L, {title: 'TensorFMA32: c + a × b in seven pipeline stages (the TXFMA)', sub: 'one fp32 multiply-add a cycle in each of the 8 lanes, each result 7 cycles later; a is broadcast to all 8 lanes, b is the lane’s own, c the accumulator',
    subf: 'tfma.stages tfma.operands', col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL'], ['documented', 'Esperanto’s stage diagrams']]});
  const sx = i => -140 + i * 172;
  ap.tf = {st: [], reg: [], parts: {}, out: {x: 1068, y: 250}, meter: {x: 556, y: 388, tl: true}};   // (the meter: under f4's and f5's parts, where the columns are empty)
  const hdr = [];   // the stages' headers: each goes in where the first block of its stage does (below)
  for (let i = 0; i < 7; i++) {
    const x = sx(i);
    S(E('rect', {x, y: 64, width: 156, height: 406, rx: 10}, L), {fill: 'var(--c1)', fillOpacity: 0.03, stroke: 'var(--grid)', strokeWidth: 1.25});
    ap.tf.st[i] = {x, y: 64, w: 156, h: 406};
    hdr[i] = ipart(L, ap, 'st' + i, x, 24, 156, 34, CC.logic, 'f' + i, {center: true, ty: 24, label: `Stage f${i}: ${TFST[i].t}`, info: {title: `f${i}: ${TFST[i].t}`, lead: TFST[i].lead, facts: TFST[i].f}});
    KTT(L, x + 78, 84, 'lane stage F' + (i + 2), 't-sm', 'middle', 'tfma.stages');
    KTT(L, x + 78, 488, `${fnum(TFR[i], 0)} bits`, 't-sm', 'middle', 'tfma.regs.stage');
    KTT(L, x + 78, 508, `${fnum(TFFF[i], 0)} flip-flops`, 't-sm', 'middle', 'tfma.regs.stage');
    if (i < 6) arrowR(L, x + 148, 150, x + 162);
  }
  TFPART.forEach(([i, key, y, h, title, sub, kid, col, lead, facts]) => {
    const x = sx(i) + 8, w = 140, info = lead ? {title: TFST[i].t.split(',')[0] + ': ' + title, lead, facts} : TBK(kid);
    let g;
    if (/^op/.test(key)) {
      g = dpart(L, ap, key, x, y, w, h, col, title, {id: kid}, {ty: 22, label: `Operand ${title}`, info: Object.assign({}, info, {title: `Operand ${title}: its register`})});
      KTT(g, x + w - 10, y + 22, '32 bits', 't-sm', 'end', 'tfma.regs.stage');
    } else {
      const ty = Math.max(28, Math.round(h / 2 - sub.length * 10.5 + 6));
      g = kid === 'vpu.lane.fma.booth' ? ipart(L, ap, key, x, y, w, h, col, title, {node: kid, kid: {id: kid}, sub, center: true, ty})
        : dpart(L, ap, key, x, y, w, h, col, title, {id: kid}, {sub, center: true, ty, info});
    }
    ap.tf.parts[key] = {x, y, w, h};
    if (!hdr[i]._kid && g._kid) hdr[i]._kid = g._kid;   // its stage's header: the same way in, the same seat
  });
  for (let i = 0; i < 7; i++) {   // the register that starts each stage
    const b = {x: sx(i) - 12, y: 64, w: 8, h: 406};
    ap.tf.reg[i] = b;
    if (i === 2) dpart(L, ap, 'regs', b.x, b.y, b.w, b.h, 'var(--c3)', '', {id: 'lib.flipflop'}, {fo: 0.35, label: 'The register into f2',
      info: {title: 'The register into f2', lead: '606 bits in the RTL, 492 flip-flops: the tree’s 353-bit carry-save state, the operands for later stages, the exponents and the control word.', facts: ['tfma.regs.stage', 'tfma.reg12']}});
    else S(E('rect', {x: b.x, y: b.y, width: b.w, height: b.h, rx: 2}, L), {fill: 'var(--c3)', fillOpacity: 0.35});
  }
  arrowR(L, 1040, 250, 1066);
  const ot = KTT(L, 1074, 340, 'to the register file', 't-sm', 'middle', 'tfma.stages'); ot.setAttribute('transform', 'rotate(90 1074 340)');
  const eb = dpart(L, ap, 'expband', -140, 522, 1188, 46, 'var(--c4)', 'exponent path', {id: 'lib.adder'}, {ty: 18, tcls: 't-smb', fo: 0.08, info: {title: 'The exponent path',
    lead: 'Beside the significands, the exponents: ea + eb − 127 for the product and its difference from c’s (f1), the shift amount and which addend to shift (f2), the result’s exponent minus the normalising shift (f5), +1 if rounding carries out (f6).', facts: ['tfma.stages']}});
  KTT(eb, -128, 560, 'f1: ea + eb − 127 and its difference from ec · f2: the shift amount · f5: e − the shift · f6: +1 if rounding carries out', 't-sm', 'start', 'tfma.stages');
  const zb = {x: -140, y: 578, w: 680, h: 72};
  const gz = KT.comp(L, 'fmazero', {}, 'A zero word: no valid bit, no stage clocks');
  S(E('rect', {class: 'shape', x: zb.x, y: zb.y, width: zb.w, height: zb.h, rx: 8}, gz), {fill: 'var(--c2)', fillOpacity: 0.06, stroke: 'var(--c2)', strokeWidth: 1.5, strokeDasharray: '6 5'});
  gz._box = zb;
  KTT(gz, zb.x + 14, zb.y + 22, 'A zero word: no valid bit, no stage clocks', 't-smb');
  KTT(gz, zb.x + 14, zb.y + 44, 'accumulate passes: an operand word of exactly 0 withholds the valid bit;', 't-sm', 'start', 'tfma.zero');
  KTT(gz, zb.x + 14, zb.y + 64, `the stage clock gates stay shut: ${N.tf_z.t} flip-flops clocked instead of ${N.tf_flops.t}`, 't-sm', 'start', 'tfma.zero tfma.clocked');
  gz._info = {title: 'Zeros: no valid bit, no stage clocks', lead: `A zero operand word switches almost nothing: in a TensorFMA’s accumulate passes a lane gets no valid bit when its a or b word is exactly 0 (a zero a gates all 8 lanes, a zero b its own lane), so none of the unit’s stage clock gates opens: ${N.tf_z.t} flip-flops are clocked instead of ${N.tf_flops.t}. −0.0, denormals and the first pass are not gated.`, facts: ['tfma.zero', 'tfma.clocked', 'e-tfma-fp32-zeros']};
  gz._kid = claim(ap, {id: 'lib.icg'}, 'fmazero', zb, gz);
  dpart(L, ap, 'gates', 556, 578, 340, 72, 'var(--c7)', '13 clock gates in the unit', {id: 'lib.icg'}, {ty: 22, lh: 20, sub: ['one per operand, stage, control word;', '27 per lane after synthesis'],
    info: {title: 'The clock gates', lead: 'Esperanto’s RTL places 13 clock gates in the unit: one per operand register, one for the transcendental-ROM registers, the control word, each stage f0-f5 and two for the multiply-type registers. Synthesis added 13 more, and the lane has its own: 27 per lane.', facts: ['tfma.icg', 'tfma.zero']}});
  cpart(L, ap, 'tbBooth', 912, 578, 148, 72, 'var(--c3)', 'textbook Booth', {id: 'lib.booth'}, {ty: 42, tcls: 't-smb'});
  KTT(L, -150, 676, 'as the ET-SoC-1 RTL builds it (txfma_f0 … txfma_f6); Esperanto’s own stage diagrams draw the same blocks', 't-sm', 'start', 'tfma.stages');
}, def: () => ({id: 'vpu.lane.fma.tree'}), kids: () => [{id: 'vpu.lane.fma.tree'}, {id: 'vpu.lane.fma.booth'}, {id: 'lib.adder'}, {id: 'lib.shifter'}, {id: 'lib.lzd'}, {id: 'lib.round'}, {id: 'lib.icg'}, {id: 'lib.flipflop'}, {id: 'lib.booth'}]});
function sideTo(g, P, d, id) {   // a part that glides to a sibling scene (the Booth multiplier and the tree, both under the multiply-add); its kid unseated, as linkParts' go: parts have
  g._kid = null; if (P && d > 0) { g._kid = {id}; g._side = true; g._go = () => P.slice(0, d).concat([{id}]); }
  return g;
}
bnode('vpu.lane.fma.booth', {draw: (L, ap, p, P, d) => {
  KT.frame(L, {title: 'The multiplier: 16 Booth rows of b, chosen by a, plus row 17', sub: 'a’s significand is read three bits at a time; each group picks 0, ±b or ±2b for its row, shifted two places per row', subf: 'tfma.booth.rows',
    col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL'], ['documented', 'Esperanto’s hand design']]});
  const BX = col => 1052 - col * 14.6, rowY = k => 80 + (k - 1) * 21, mx = b => 300 + (31 - b) * 23;
  const gm = cgrp(L, ap, 'mplr', 'The multiplier: a’s significand, read three bits at a time', {x: 292, y: 6, w: 772, h: 58}, {id: 'fma.benc', k: 'mplr'},
    {seat: {x: 300, y: 26, w: 68, h: 20}, info: {title: 'The multiplier, a', lead: 'a’s 24-bit significand in bits 31-8 of the multiplier (its low 8 bits are zero in fp32). Each row k reads bits 2k−1, 2k−2 and 2k−3.', facts: ['tfma.booth.rows', 'tfma.operands']}});
  for (let b = 31; b >= -1; b--) {
    const r = S(E('rect', {x: mx(b), y: 26, width: 22, height: 20, rx: 3}, gm), {fill: b === 31 ? 'var(--c1)' : 'var(--surface)', fillOpacity: b === 31 ? 0.3 : 1, stroke: 'var(--ink-2)', strokeWidth: 1});
    if (b < 8) r.style.opacity = b < 0 ? 0.5 : 0.35;
    if (b < 0) { r.style.strokeDasharray = '3 3'; KTT(gm, mx(b) + 11, 41, '0', 't-sm', 'middle'); }
  }
  for (let k = 1; k <= 16; k++) {
    const x1 = mx(2 * k - 1) + 2, x2 = mx(2 * k - 3) + 20, yb = 52 + (k % 2) * 5;
    E('path', {class: 'w thin', d: `M${x1},${yb - 4} L${x1},${yb} L${x2},${yb} L${x2},${yb - 4}`}, gm);
  }
  KTT(L, mx(31) + 11, 20, 'hidden 1', 't-sm', 'middle', 'tfma.booth.rows'); KTT(L, mx(3.5) + 11, 20, 'zero in fp32', 't-sm', 'middle', 'tfma.booth.fp32');
  KTT(L, 286, 42, 'a', 't-net', 'end');
  const gr = cgrp(L, ap, 'rows', 'The partial products: 16 rows of 33 bits and row 17', {x: 126, y: 76, w: 936, h: 356}, {id: 'fma.psel', k: 'rows'},
    {seat: {x: BX(34) - 8, y: rowY(8) - 2, w: 16, h: 16}, info: {title: 'The partial products', lead: 'Each row is 0, ±b or ±2b, shifted two places further left than the row above: row k starts at column 2(k−1). A negative row is b inverted, its +1 waiting in the sign row. Row 17 adds b once more for a’s top bit.', facts: ['tfma.booth.rows', 'tfma.booth.fp32']}});
  for (let k = 1; k <= 17; k++) {
    const c0 = k === 17 ? 32 : 2 * (k - 1), nb = k === 17 ? 32 : 33, y = rowY(k), rg = E('g', {}, gr);
    if (k <= 4) rg.style.opacity = 0.3;
    for (let j = 0; j < nb; j++) S(E('rect', {x: BX(c0 + j) - 6, y, width: 12, height: 12, rx: 2}, rg), {fill: 'var(--c1)', fillOpacity: 0.16, stroke: 'var(--c1)', strokeOpacity: 0.55, strokeWidth: 1});
    KTT(L, 120, y + 10, 'row ' + k, 't-sm', 'end');
  }
  S(E('circle', {cx: BX(33), cy: rowY(1) + 6, r: 4.5}, L), {fill: 'var(--c2)'});
  KTT(L, BX(33) - 9, rowY(1) + 11, 'the magic 1', 't-sm halo', 'end', 'tfma.booth.rows');
  const gs = cgrp(L, ap, 'sxt', 'The sign row: the carry-ins of negative rows and the sign extension', {x: 126, y: 440, w: 936, h: 24}, {id: 'fma.benc', k: 'sxt'},
    {seat: {x: BX(0) - 6, y: 446, w: 12, h: 12}, info: {title: 'The sign row', lead: 'A negative row is only inverted; its +1 goes in here (Cin). Instead of extending every row’s sign to bit 63, the rows’ inverted signs (Sxt), a pattern of constant ones and one more 1 at bit 33 of row 1 (the ‘magic one’) do the same for all rows at once. This row enters the tree at level 4.', facts: ['tfma.booth.rows']}});
  for (let c = 0; c <= 63; c++) {
    if ((c <= 30 && c % 2 === 0) || (c >= 33 && c % 2)) S(E('rect', {x: BX(c) - 6, y: 446, width: 12, height: 12, rx: 2}, gs), {fill: 'var(--c4)', fillOpacity: 0.3, stroke: 'var(--c4)', strokeWidth: 1});
    else if (c >= 34) S(E('rect', {x: BX(c) - 3, y: 449, width: 6, height: 6}, gs), {fill: 'var(--ink-2)'});
  }
  KTT(L, 120, 456, 'sign row', 't-sm', 'end');
  ipart(L, ap, 'enc', -150, 80, 200, 230, CC.logic, 'Booth encoders', {node: 'fma.benc', kid: {id: 'fma.benc'}, center: true, ty: 96, sub: ['one per row: 3 bits', 'of a → 0, ±b, ±2b']});
  KTT(L, -150, 336, 'a’s 3 bits → the row', 't-smb', 'start', 'tfma.booth.rows');
  [['000', '0'], ['001', '+b'], ['010', '+b'], ['011', '+2b'], ['100', '−2b'], ['101', '−b'], ['110', '−b'], ['111', '0']].forEach(([b, r], i) => KTT(L, -150 + (i >> 2) * 104, 360 + (i & 3) * 22, `${b} → ${r}`, 't-mono', 'start', 'tfma.booth.rows'));
  const sx0 = BX(34), sy0 = rowY(8);
  ipart(L, ap, 'sel', sx0 - 8, sy0 - 2, 16, 16, 'var(--c2)', '', {node: 'fma.psel', kid: {id: 'fma.psel'}, label: 'One bit of a row', fo: 0.3});
  S(KT.wire(L, [[sx0 + 8, sy0 + 14], [712, 376]], 'thin'), {stroke: 'var(--c2)'});
  KTT(L, 720, 388, 'each bit: picks b(j) or b(j−1),', 't-sm', 'start', 'tfma.psel'); KTT(L, 720, 408, 'inverts it if the row is negative', 't-sm', 'start', 'tfma.psel');
  arrowD(L, 594, 464, 484);
  sideTo(ipart(L, ap, 'tree', 126, 486, 936, 44, CC.logic, 'to the Wallace tree: 18 rows → 2', {node: 'vpu.lane.fma.tree', center: true, ty: 30, label: 'The Wallace tree: the 18 rows go on to it'}), P, d, 'vpu.lane.fma.tree');
  cpart(L, ap, 'tb', -150, 486, 250, 44, 'var(--c3)', 'the textbook encoder', {id: 'lib.booth'}, {tcls: 't-smb', ty: 28});
  KTT(L, -150, 628, 'fp32: a’s low 8 bits are zero, so rows 1-4 (faint) never switch; at most 13 rows carry data (a = π: 10)', 't-sm', 'start', 'tfma.booth.fp32');
  KTT(L, -150, 652, 'as built (one lane): about 21,300 transistors in the encoders, the 560 selector bits and the fan-out of a and b', 't-sm', 'start', 'tfma.asbuilt.cells tfma.sel.asbuilt');
  KTT(L, -150, 676, 'Esperanto’s hand-placed version of this 7-stage datapath draws the encoder and the bit (zoom in); the silicon makes the same rows with other gates', 't-sm', 'start', 'tfma.hand tfma.sel.asbuilt');
  ap.tf = {pp: (r, b) => ({x: BX(r === 17 ? 32 + b : 2 * (r - 1) + b), y: rowY(r) + 6}), dig: r => ({x: 124, y: rowY(r) + 10})};
}, def: () => ({id: 'fma.benc'}), kids: () => [{id: 'fma.benc'}, {id: 'fma.psel'}, {id: 'lib.booth'}]});
bnode('vpu.lane.fma.tree', {draw: (L, ap, p, P, d) => {
  KT.frame(L, {title: 'The Wallace tree as built: 18 rows to 2 in four levels', sub: 'f1: the 16 Booth rows → 8 → 4; a 353-bit register; f2: → 2, then with row 17 and the sign row → 2; then one 64-bit adder',
    subf: 'tfma.tree.levels tfma.reg12', col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL'], ['measured', `synthesis keeps ${on('tf_kept').replace(/ compressors$/, '')}`]]});
  const X = col => 1046 - col * 15.4, ry = k => (k <= 16 ? 26 + (k - 1) * 8.2 : k === 17 ? 26 + 16 * 8.2 + 4 : 26 + 16 * 8.2 + 14);
  const Y1 = 200, Y2 = 278, YR = 322, Y3 = 384, Y4 = 428, YA = 472, YP = 508;
  const top = (lv, a) => (lv === 1 ? Y1 + a * 13 : lv === 2 ? Y2 + a * 13 : lv === 3 ? Y3 : Y4);
  S(E('rect', {x: X(40) - 8, y: 18, width: 16, height: YP + 8 - 18, rx: 4}, L), {fill: 'var(--c2)', fillOpacity: 0.05, stroke: 'var(--c2)', strokeOpacity: 0.7, strokeWidth: 1.25});
  const lab = (y, lines) => lines.forEach(([t, f], k) => { S(KTT(L, -150, y + k * 18, t, k ? 't-sm' : 't-smb', 'start', f || null), {fontSize: '16px'}); });   // (a fixed size: the column is narrow)
  const ppBox = {x: 60, y: 18, w: 1000, h: ry(18) - 10};
  const gp = sideTo(cgrp(L, ap, 'pp', 'The Booth multiplier: the Booth rows, row 17 and the sign row come from it', ppBox, null, {info: TBK('vpu.lane.fma.booth')}), P, d, 'vpu.lane.fma.booth');
  const dot = (x, y) => `M${(x - 2.3).toFixed(1)},${y.toFixed(1)}a2.3,2.3 0 1,0 4.6,0a2.3,2.3 0 1,0 -4.6,0`;   // a row of dots is one path (1,000 dots: build time)
  for (let k = 1; k <= 18; k++) {
    const y = ry(k), cs = k <= 16 ? Array.from({length: 33}, (_, j) => 2 * (k - 1) + j) : k === 17 ? Array.from({length: 32}, (_, j) => 32 + j)
      : Array.from({length: 64}, (_, c) => c).filter(c => (c <= 30 && c % 2 === 0) || (c >= 33 && c % 2));
    const d = E('path', {class: 'jn', d: cs.map(c => dot(X(c), y)).join('')}, gp);
    if (k <= 4) d.style.opacity = 0.3;
    if (k === 18) { let q = ''; for (let c = 34; c <= 62; c += 2) q += `M${X(c) - 2},${y - 2}h4v4h-4z`; S(E('path', {d: q}, gp), {fill: 'var(--ink-2)'}); }
  }
  S(E('circle', {cx: X(33), cy: ry(1), r: 3}, gp), {fill: 'var(--c2)'});
  lab(40, [['Booth rows · f1'], ['16 rows of 33 bits,'], ['row 17, the sign row']]);
  KT.wire(L, [[1052, ry(17)], [1062, ry(17)], [1062, Y4 + 5], [1052, Y4 + 5]], 'thin');
  const bt = KTT(L, 1074, (ry(17) + Y4) / 2, 'row 17, sign row', 't-sm', 'middle', 'tfma.tree.levels'); bt.setAttribute('transform', `rotate(90 1074 ${(ry(17) + Y4) / 2})`);
  [1, 2, 3, 4].forEach(lv => {
    const n = LVA[lv], bx = {x: 70, y: top(lv, 0) - 3, w: 984, h: n * 13 + 3};
    const g = cgrp(L, ap, 'lv' + lv, `Level ${lv}: ${LVIO[lv]}`, bx, {id: 'fma.lvl', k: String(lv)}, {seat: bx, info: {title: `Level ${lv} (${LVST[lv]})`, lead: LVBL[lv], facts: ['tfma.tree.levels', 'tfma.tree.synth', 'tfma.asbuilt.cells']}});
    for (let a = 0; a < n; a++) for (let i = 0; i < 64; i++) c42Look(E('rect', {x: X(i) - 6.5, y: top(lv, a), width: 13, height: 10, rx: 2}, g), lv, a, i);
  });
  lab(Y1 + 8, [['Level 1 · f1'], ['16 → 8 rows, 4 arrays', 'tfma.tree.levels'], ['array 1: idle in fp32', 'tfma.tree.fp32']]);
  lab(Y2 + 8, [['Level 2 · f1'], ['8 → 4, 2 arrays', 'tfma.tree.levels']]);
  const rb = {x: 70, y: YR, w: 984, h: 32};
  const gr = cgrp(L, ap, 'reg', 'The register between f1 and f2', rb, {id: 'lib.flipflop'}, {seat: rb, info: {title: 'The register between f1 and f2',
    lead: '353 bits in the RTL: level 2’s four rows (4 × 64), the carry-in row Cin (32), the sign row Sxt (32) and row 17 (33). Synthesis keeps 253 flip-flops, of which 205 can change in fp32.', facts: ['tfma.reg12', 'tfma.regs.stage']}});
  S(E('rect', {x: rb.x, y: rb.y, width: rb.w, height: rb.h, rx: 4}, gr), {fill: 'var(--c3)', fillOpacity: 0.12, stroke: 'var(--c3)', strokeOpacity: 0.5, strokeWidth: 1});
  [YR + 4, YR + 10, YR + 19, YR + 25].forEach(y => { let d = ''; for (let i = 0; i < 64; i++) d += `M${X(i)},${y}v4`; E('path', {class: 'w thin', d}, gr); });
  S(E('path', {class: 'w thin', d: `M70,${YR + 16} H1054`}, gr), {strokeDasharray: '6 5'});
  lab(YR + 8, [['Register · f1 | f2'], [`${on('tf_reg')}, ${on('tf_ff')}`, onf('tf_reg')]]);
  lab(Y3 + 8, [['Level 3 · f2'], ['4 → 2 rows', 'tfma.tree.levels']]);
  lab(Y4 + 8, [['Level 4 · f2'], ['2 + row 17 + sign → 2', 'tfma.tree.levels']]);
  const ab = {x: 70, y: YA, w: 984, h: 20};
  const ga = cgrp(L, ap, 'padd', 'The 64-bit product adder', ab, {id: 'lib.adder'}, {seat: ab, info: {title: 'The product adder', lead: 'Adds the tree’s last two rows into the exact product: 64 bits, written as a + b in the RTL and synthesized as a parallel-prefix adder.', facts: ['tfma.padd', 'tfma.frame']}});
  for (let i = 0; i < 64; i++) S(E('rect', {x: X(i) - 6.5, y: YA, width: 13, height: 20, rx: 2}, ga), {fill: 'var(--c4)', fillOpacity: 0.16, stroke: 'var(--c4)', strokeOpacity: 0.6, strokeWidth: 1});
  lab(YA + 8, [['64-bit adder · f2'], ['2 rows → the product', 'tfma.padd']]);
  const pb = {x: 70, y: YP, w: 984, h: 8};
  const gq = cgrp(L, ap, 'preg', 'The product register: 64 flip-flops, to f3', {x: 70, y: YP - 4, w: 984, h: 16}, {id: 'lib.flipflop'}, {seat: {x: 70, y: YP - 4, w: 984, h: 16},
    info: {title: 'The product register', lead: 'The product’s 64 bits, held for f3, where it is lined up with c.', facts: ['tfma.regs.stage', 'tfma.padd']}});
  S(E('rect', {x: pb.x, y: pb.y, width: pb.w, height: pb.h, rx: 3}, gq), {fill: 'var(--c3)', fillOpacity: 0.35});
  lab(YP + 18, [['product register'], ['64 flip-flops → f3', 'tfma.regs.stage']]);
  ipart(L, ap, 'col40', X(40) - 48, YP + 16, 96, 28, 'var(--c2)', 'column 40', {node: 'fma.tree.col', kid: {id: 'fma.tree.col'}, center: true, ty: 20, tcls: 't-sm'});
  KTT(L, -150, 604, 'each level: arrays of 64 4:2 compressors, one per bit; a sideways carry does not wait for the one coming in, so nothing ripples', 't-sm', 'start', 'tfma.tree.arrays tfma.cmp42');
  KTT(L, -150, 628, `RTL: 8 arrays, ${on('tf_cmp')}, ${on('tf_fa')}; synthesis keeps ${on('tf_kept')} (dashed: cut, inputs constant); in fp32 level 1’s first array never switches`, 't-sm', 'start', 'tfma.tree.arrays tfma.tree.synth tfma.tree.fp32');
  KTT(L, -150, 652, `as built (one lane): ${on('tree_tr')} in the four levels, ${N.tf_fac.t} full-adder cells and XOR, majority and compound gates, no 4:2 cell`, 't-sm', 'start', 'tfma.asbuilt.cells');
  KTT(L, -150, 676, 'an earlier version of this drawing showed a textbook schedule, 17 → 9 → 5 → 3 → 2 rows; the design does it in four 4:2 levels', 't-sm', 'start', 'tfma.tree.levels');
  ap.tf = {pp: (r, b) => ({x: X(r === 17 ? 32 + b : 2 * (r - 1) + b), y: ry(r)}), ry, cell: (lv, a, i) => ({x: X(i) - 6.5, y: top(lv, a), w: 13, h: 10}),
    reg: i => ({x: X(i), y: YR + 16}), add: i => ({x: X(i) - 6.5, y: YA, w: 13, h: 20}), bus: {x: 1062, y1: ry(17), y2: Y4 + 5},
    lab: {1: {x: 66, y: Y1 + 24}, 2: {x: 66, y: Y2 + 12}, reg: {x: 66, y: YR + 16}, 3: {x: 66, y: Y3 + 5}, 4: {x: 66, y: Y4 + 5}, add: {x: 66, y: YA + 10}},
    band: {1: Y1, 2: Y2 - 2, reg: YR - 1, 3: Y3 - 7, 4: Y4 - 7, add: YA - 7}, right: 1048, rows: {x: 1048, y: ry(9) - 4},   // the callouts: right of the lit columns (0-24 never light for this flip), clear of the labels
    meter: {x: 72, y: 1, tl: true}};   // the meter: the empty corner above the Booth rows, left of a's digits
}, def: () => ({id: 'fma.lvl', k: '1'}), kids: () => [1, 2, 3, 4].map(l => ({id: 'fma.lvl', k: String(l)})).concat([{id: 'fma.tree.col'}, {id: 'lib.adder'}, {id: 'lib.flipflop'}])});
bnode('fma.lvl', {parse: k => ({lv: Math.max(1, Math.min(4, +k || 1))}), name: p => `Level ${p.lv} of the Wallace tree`, short: p => `Level ${p.lv}`, to: p => `level ${p.lv} of the tree`, blurb: p => LVBL[p.lv],
  draw: (L, ap, p) => {
    const lv = p.lv, n = LVA[lv], cw = 18.6, h = n === 4 ? 74 : n === 2 ? 110 : 150, y0 = a => (n === 4 ? 76 + a * 136 : n === 2 ? 100 + a * 230 : 170);
    KT.frame(L, {title: `Level ${lv} (${LVST[lv]}): ${n} array${n > 1 ? 's' : ''} of 64 4:2 compressors, ${LVIO[lv]}`, sub: 'bit 63 left, bit 0 right; each box is one column, four bits in and a sum and two carries out; filled: can switch in fp32, outlined: idle in fp32, dashed: cut', subf: 'tfma.cmp42 tfma.tree.synth tfma.tree.fp32',
      col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL'], ['measured', `synthesis keeps ${LVKEPT[lv]}`]]});
    const bx = i => -150 + (63 - i) * cw;
    [63, 56, 48, 40, 32, 24, 16, 8, 0].forEach(i => KTT(L, bx(i) + (cw - 3) / 2, y0(0) - 34, String(i), 't-sm', 'middle'));
    const ARL = {1: a => `array ${a + 1}: rows ${4 * a + 1}-${4 * a + 4}${a === 0 ? ' (zero in fp32: never switches)' : ''}`, 2: a => (a ? 'array 2: level 1’s arrays 3 and 4' : 'array 1: level 1’s arrays 1 and 2'),
      3: () => 'the register’s four rows (C21, S21, C22, S22)', 4: () => 'level 3’s two rows, row 17 and the sign row'};
    for (let a = 0; a < n; a++) {
      const y = y0(a);
      KTT(L, -150, y - 8, ARL[lv](a), 't-sm', 'start', a === 0 && lv === 1 ? 'tfma.tree.fp32' : 'tfma.tree.levels');
      for (let i = 0; i < 64; i++) {
        const x = bx(i), ins = colIn(lv, a, i), kept = inSpan(SPAN[lv][a], i), live = kept && inSpan(F32[lv][a], i);
        const g = ipart(L, ap, 'c42', x, y, cw - 3, h, CC.logic, '', {node: 'lib.cmp42', ctx: {a, i}, label: `Array ${a + 1}, column ${i}`, kid: {id: 'fma.col', k: `${lv}.${a}.${i}`}, fo: kept ? 0.1 : 0.03,
          info: {title: `Level ${lv}${n > 1 ? `, array ${a + 1}` : ''}, column ${i}`, lead: `Column ${i} of array ${a + 1}: in ${ins.map(x0 => x0 || '0').join(', ')}; ${kept ? (live ? 'can switch in fp32' : 'kept by synthesis, idle in fp32') : 'cut by synthesis: its inputs are constant'}.`,
            facts: ['tfma.cmp42', 'tfma.tree.synth', 'tfma.tree.fp32']}});
        const r = g.querySelector(':scope > rect.shape');
        if (r && !kept) S(r, {stroke: 'var(--axis)', strokeDasharray: '2 3', fillOpacity: 0, strokeWidth: 1});
        else if (r && !live) S(r, {strokeOpacity: 0.35, fillOpacity: 0, strokeWidth: 1});
        else if (r) S(r, {fillOpacity: 0.26});
        if (i < 63) E('path', {class: 'w thin', d: `M${x},${y + h / 2} h-3`}, L);
      }
      S(E('rect', {x: -150, y: y + h + 6, width: 64 * cw - 3, height: 4, rx: 2}, L), {fill: 'var(--c1)', fillOpacity: 0.4});
      S(E('rect', {x: -150 - cw, y: y + h + 13, width: 64 * cw - 3, height: 4, rx: 2}, L), {fill: 'var(--c4)', fillOpacity: 0.45});
      if (a === n - 1) KTT(L, -150, y + h + 34, lv < 4 ? `the outputs: s → level ${lv + 1}, same column; c → level ${lv + 1}, one column left` : 'the outputs: s, c → the 64-bit adder (c one column left)', 't-sm', 'start', 'tfma.tree.arrays');
    }
    KTT(L, -150, 628, 'column i’s compressor takes four bits of weight 2^i and a carry from column i − 1, and gives a sum (2^i)', 't-sm', 'start', 'tfma.cmp42');
    KTT(L, -150, 652, 'and two carries (2^(i+1)): one sideways, which does not depend on the carry coming in, and one down a level', 't-sm', 'start', 'tfma.cmp42');
    KTT(L, -150, 676, `as built (one lane): ${LVTR[lv]} transistors in this level${lv === 4 ? ', with the adder’s first layer' : ''}; synthesis keeps columns ${SPAN[lv].map(s => `${s[0]}-${s[1]}`).join(', ')}`, 't-sm', 'start', 'tfma.asbuilt.cells tfma.tree.synth');
  }, def: p => ({id: 'fma.col', k: `${p.lv}.${p.lv === 1 ? 1 : 0}.40`}), kids: p => [{id: 'fma.col', k: `${p.lv}.${p.lv === 1 ? 1 : 0}.40`}]});
function colLine(lv, i) {   // where column i is kept, and live in fp32, at one level
  const n = LVA[lv], kept = [], live = [];
  for (let a = 0; a < n; a++) if (inSpan(SPAN[lv][a], i)) { kept.push(a + 1); if (inSpan(F32[lv][a], i)) live.push(a + 1); }
  const arr = xs => (xs.length === 1 ? `array ${xs[0]}` : `arrays ${xs.join(', ')}`), idle = kept.filter(a => !live.includes(a));
  const where = n === 1 ? (kept.length ? 'kept' : 'cut by synthesis') : kept.length ? `kept in ${arr(kept)}` : 'cut in every array';
  return `level ${lv} (${LVST[lv]}): ${where}` + (!kept.length ? '' : !idle.length ? '; can switch in fp32' : n === 1 ? '; idle in fp32' : `; ${arr(idle)} idle in fp32`);
}
bnode('fma.col', {parse: k => { const q = String(k || '1.1.40').split('.').map(Number); const lv = Math.max(1, Math.min(4, q[0] || 1)); return {lv, a: Math.max(0, Math.min(LVA[lv] - 1, q[1] || 0)), i: Math.max(0, Math.min(63, q[2] == null || isNaN(q[2]) ? 40 : q[2]))}; },
  name: p => `Column ${p.i}, level ${p.lv}${LVA[p.lv] > 1 ? `, array ${p.a + 1}` : ''}`, short: p => `Column ${p.i}`, to: p => `column ${p.i}`,
  draw: (L, ap, p) => {
    const {lv, a, i} = p, n = LVA[lv], ins = colIn(lv, a, i), kept = inSpan(SPAN[lv][a], i), live = kept && inSpan(F32[lv][a], i);
    KT.frame(L, {title: `Column ${i} of level ${lv}${n > 1 ? `, array ${a + 1}` : ''}: one 4:2 compressor`, sub: i ? `four bits of weight 2^${i} and a carry from column ${i - 1} in; a sum and two carries out` : 'four bits of weight 2^0 and a carry in of 0; a sum and two carries out',
      subf: 'tfma.cmp42', col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL'], kept ? ['measured', 'kept by synthesis'] : ['measured', 'cut by synthesis: constant inputs']].concat(kept && !live ? [['derived', 'idle in fp32']] : [])});
    const nb = (x, t) => { const g = E('g', {}, L); g.style.opacity = 0.35; S(E('rect', {x, y: 260, width: 200, height: 150, rx: 8}, g), {fill: 'var(--c1)', fillOpacity: 0.08, stroke: 'var(--c1)', strokeWidth: 1.5}); KTT(g, x + 100, 342, t, 't-labb', 'middle'); };
    if (i < 63) nb(40, `← column ${i + 1}`);
    if (i > 0) nb(720, `column ${i - 1} →`);
    ipart(L, ap, 'c42', 330, 230, 300, 210, CC.logic, '4:2 compressor', {node: 'lib.cmp42', kid: {id: 'lib.cmp42'}, center: true, ty: 110, sub: ['two full adders'], fo: kept ? 0.12 : 0.04});
    [370, 440, 510, 590].forEach((x, k) => {
      KT.wire(L, [[x, 152], [x, 230]]); KT.netLab(L, x, 144, 'x' + k, 'middle');
      const t = S(KTT(L, x - 4, 122, ins[k] || '0 (constant)', 't-sm', 'start', lv === 1 ? 'tfma.booth.rows' : 'tfma.tree.arrays'), {fontSize: '17px'});
      t.setAttribute('transform', `rotate(-30 ${x - 4} 122)`);
    });
    if (i > 0) { KT.wire(L, [[720, 380], [630, 380]]); KTT(L, 720, 436, `cin ← cout of column ${i - 1}`, 't-sm', 'start', 'tfma.tree.arrays'); KTT(L, 720, 460, 'arrow keys: the next column', 't-sm'); }
    else { KT.wire(L, [[700, 380], [630, 380]]); KTT(L, 708, 386, 'cin = 0', 't-sm', 'start', 'tfma.tree.arrays'); }
    if (i < 63) { KT.wire(L, [[330, 290], [240, 290]]); KTT(L, 40, 436, `cout → cin of column ${i + 1}`, 't-sm', 'start', 'tfma.tree.arrays'); }
    else { KT.wire(L, [[330, 290], [260, 290]]); KTT(L, 252, 296, 'cout: dropped', 't-sm', 'end', 'tfma.tree.arrays'); }
    arrowD(L, 430, 440, 520); arrowD(L, 530, 440, 520);
    KT.netLab(L, 430, 542, 's', 'middle'); KT.netLab(L, 530, 542, 'c', 'middle');
    KTT(L, 420, 566, lv < 4 ? `s → level ${lv + 1}, column ${i}` : `s → the adder, bit ${i}`, 't-sm', 'end', 'tfma.tree.arrays');
    KTT(L, 540, 566, i === 63 ? 'c: dropped (the product fits in 64 bits)' : lv < 4 ? `c → level ${lv + 1}, column ${i + 1}` : `c → the adder, bit ${i + 1}`, 't-sm', 'start', 'tfma.tree.arrays');
    KTT(L, -150, 596, `column ${i} at each level`, 't-smb', 'start', 'tfma.tree.synth');
    [1, 2, 3, 4].forEach((l, k) => S(KTT(L, -150, 618 + k * 20, colLine(l, i), 't-sm', 'start', 'tfma.tree.synth tfma.tree.fp32'), {fontSize: '17px'}));
    KTT(L, 1070, 676, 'x0 + x1 + x2 + x3 + cin = s + 2 (c + cout)', 't-mono', 'end', 'tfma.cmp42');
  }, def: () => ({id: 'lib.cmp42'}), kids: () => [{id: 'lib.cmp42'}]});
/* one column of the tree: 17 bits down through 4:2 compressors to 2, carries to and from the neighbouring columns */
bnode('fma.tree.col', {draw: (L, ap) => {
  KT.frame(L, {title: 'Column 40 of the Wallace tree, as built: 8 compressor positions', sub: 'every bit of weight 2^40 on its way down: carries come in from column 39 and leave for column 41', subf: 'tfma.tree.arrays', col: CC.logic, tags: [['documented', 'as built: the ET-SoC-1 RTL']]});
  const B1 = [-120, 160, 440, 720], rowX = r => B1[Math.floor((r - 1) / 4)] + 30 + ((r - 1) % 4) * 60;
  for (let r = 1; r <= 16; r++) {
    const x = rowX(r);
    if (r >= 5) { E('circle', {cx: x, cy: 40, r: 7, class: 'jn'}, L); KTT(L, x, 66, 'r' + r, 't-sm', 'middle', 'tfma.booth.fp32'); KT.wire(L, [[x, 76], [x, 110]], 'thin'); }
    else S(E('circle', {cx: x, cy: 40, r: 7, fill: 'none'}, L), {stroke: 'var(--axis)', strokeWidth: 1.5, strokeDasharray: '2 3'});
  }
  KTT(L, (rowX(1) + rowX(4)) / 2, 66, 'r1-r4: none', 't-sm', 'middle', 'tfma.booth.fp32');
  const side = (x, y, w, h, labs) => {   // the sideways carries: in from column 39 on the right, out to column 41 on the left
    arrowL(L, x + w + 30, y + h - 22, x + w + 2); arrowL(L, x - 2, y + 22, x - 30);
    if (labs) { KTT(L, x + w + 36, y + h - 16, 'cin (column 39)', 't-sm', 'start', 'tfma.tree.arrays'); KTT(L, x - 36, y + 28, 'cout (column 41)', 't-sm', 'end', 'tfma.tree.arrays'); }
  };
  const box = (lv, a, x, y, w) => {
    const ins = colIn(lv, a, 40).map(colShort), kept = inSpan(SPAN[lv][a], 40), nm = `Level ${lv}${LVA[lv] > 1 ? `, array ${a + 1}` : ''}, column 40`;
    if (!kept) {
      const g = dpart(L, ap, `c42_${lv}${a + 1}`, x, y, w, 80, 'var(--axis)', 'level 1, array 1', {id: 'fma.col', k: `${lv}.${a}.40`}, {center: true, ty: 26, lh: 20, fo: 0, sub: ['cut: rows 1-4 end', 'at column 38'], label: nm,
        info: {title: nm + ': cut', lead: 'Rows 1-4 end at column 38, so this compressor’s inputs are constant and synthesis removed it.', facts: ['tfma.tree.synth', 'tfma.cmp42']}});
      const r = g.querySelector(':scope > rect.shape'); if (r) S(r, {strokeDasharray: '4 4'});
      return;
    }
    // (the label over its wire's top: beside it, the first level's ran past the frame; Antigravity's audit, 14 Oct)
    dpart(L, ap, `c42_${lv}${a + 1}`, x, y, w, 80, CC.logic, `level ${lv}${LVA[lv] > 1 ? `, array ${a + 1}` : ''}`, {id: 'lib.cmp42'}, {center: true, ty: 26, lh: 20, sub: [`${ins[0]}, ${ins[1]}`, `${ins[2]}, ${ins[3]}`], label: nm,
      info: {title: nm, lead: `In: ${colIn(lv, a, 40).map(s => s || '0').join(', ')}; out: a sum to column 40 of the next level, a carry to its column 41, and a sideways carry to column 41 of this level.`, facts: ['tfma.cmp42', 'tfma.tree.arrays']}});
  };
  [1, 2, 3, 0].forEach(a => box(1, a, B1[a], 110, 240));
  B1.forEach(x => side(x, 110, 240, 80, false));
  [[0, 20], [1, 580]].forEach(([a, x]) => { box(2, a, x, 250, 300); side(x, 250, 300, 80, false); });
  [[1, 2], [3, 4]].forEach(([p, q], k) => { const xt = [20, 580][k] + 150; [p, q].forEach(j => { if (j > 1) KT.wire(L, [[B1[j - 1] + 120, 190], [B1[j - 1] + 120, 220], [xt + (j === p ? -40 : 40), 220], [xt + (j === p ? -40 : 40), 250]], 'thin'); }); });
  S(KT.wire(L, [[-150, 370], [1070, 370]], 'thin'), {strokeDasharray: '7 6'}); KTT(L, 1070, 362, 'register: f1 | f2', 't-sm', 'end', 'tfma.reg12');
  [170, 730].forEach(x => KT.wire(L, [[x, 330], [x, 360], [x < 400 ? 430 : 510, 380], [x < 400 ? 430 : 510, 400]], 'thin'));
  box(3, 0, 300, 400, 340); side(300, 400, 340, 80, true);
  KT.wire(L, [[470, 480], [470, 520]], 'thin');
  box(4, 0, 300, 520, 340); side(300, 520, 340, 80, true);
  KTT(L, 470, 622, 's → adder bit 40, c → adder bit 41', 't-sm', 'middle', 'tfma.tree.arrays');
  dpart(L, ap, 'fachip', 850, 540, 200, 40, CC.logic, 'its full adders', {id: 'lib.fa'}, {center: true, ty: 27, tcls: 't-smb', info: TBK('lib.fa')});
  KTT(L, -150, 652, 'a column takes up to 16 Booth bits (columns 30-32; in fp32 at most 12, columns 30-40), plus row 17’s bit and the sign row’s at level 4', 't-sm', 'start', 'tfma.tree.arrays tfma.booth.fp32');
  KTT(L, -150, 676, 'every level is the same 4:2 compressor; no bit passes a level untouched; the carries down (c) go to column 41 of the next level', 't-sm', 'start', 'tfma.tree.arrays');
}, def: () => ({id: 'lib.cmp42'}), kids: () => [{id: 'lib.cmp42'}, {id: 'lib.fa'}]});
