/* ================= chip-diagram.blocks.js: the chip's block scenes and its compute chain (1 October 2026) =================
   Split from chip-diagram.inside.js (30 September): the logical drawings of the blocks no floorplan shows, and a
   vector lane's multiply-add down to one column of its compressor tree. The chip page only. */
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
bnode('pcie.phy', {draw: (L, ap, p, P) => blockScene('pcie.phy', L, ap, p, P, {inst: {n: 8, id: 'pcie.lane', el: () => ({id: 'pcie.lane'}), title: i => `lane ${i}`, sub: () => '16 GT/s', h: 120}})});
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
  etlink: (c, P) => { const i = P.findIndex(e => e.id === 'shire'); return i < 0 ? [] : [{lab: 'The crossing into the shire’s clock and voltage (level shifter, FIFO)', to: P.slice(0, i + 1).concat([{id: 'shire.meshstop'}, {id: 'shire.meshstop.xing'}])}]; },
  fln: (c, P) => { const i = P.findIndex(e => e.id === 'die'); return i < 0 ? [] : [{lab: 'A wire and its repeaters (a mesh link, up close)', to: P.slice(0, i + 1).concat([{id: 'mesh'}, {id: 'mesh.link.wire'}]), made: true}]; },
  chip: (c, P) => [{lab: 'The die in cross-section: transistors and the wiring stack', to: P.concat([{id: 'die.metal'}])}, {lab: 'A compute shire', to: P.concat([{id: 'shire', k: String(isShire(LASTSID) ? LASTSID : 0)}])}],
});

/* ---- the compute ladder: a lane's fused multiply-add down to the silicon crystal ---- */
const KTT = (...a) => KT.T(...a);   // the kit's text: a memory-levels fact gets its prefix, the chip's own ids pass
const arrowR = (L, x1, y, x2, cls) => { KT.wire(L, [[x1, y], [x2, y]], cls); E('path', {class: 'w', d: `M${x2 - 9},${y - 6} L${x2},${y} L${x2 - 9},${y + 6}`}, L); };
/* the fused multiply-add: a x b + c, the multiplier, the adder and the normaliser, as the RTL names them */
bnode('vpu.lane.fma', {draw: (L, ap) => {
  KT.frame(L, {title: 'The fused multiply-add (TXFMA): a × b + c, rounded once', sub: `one fp32 or two fp16 multiply-adds a cycle; a pipeline of ${on('fma_st')}, the first gating the operands’ clock`, subf: onf('fma_st'),
    col: CC.logic, tags: [['unknown', 'blocks: Erbium RTL'], ['generic', 'stages: textbook']]});
  const y = 250;
  KTT(L, -150, y - 70, 'a', 't-net'); KTT(L, -150, y + 6, 'b', 't-net'); KTT(L, -150, y + 150, 'c', 't-net');
  KTT(L, -130, y - 96, 'fp32 or 2 × fp16', 't-sm'); KTT(L, -130, y + 124, 'the addend', 't-sm');
  const bo = ipart(L, ap, 'fmabooth', -70, y - 60, 190, 140, CC.logic, 'Booth encoders', {node: 'vpu.lane.fma.booth', sub: [{t: on('pp17'), f: onf('pp17')}, 'of the multiplicand']});
  KT.wire(L, [[-130, y - 76], [-90, y - 76], [-90, y - 20], [-70, y - 20]]); KT.wire(L, [[-130, y], [-70, y]]);
  arrowR(L, 120, y + 10, 170);
  ipart(L, ap, 'fmatree', 170, y - 80, 230, 180, CC.logic, 'compressor tree', {node: 'vpu.lane.fma.tree', kid: {id: 'vpu.lane.fma.tree'}, sub: ['17 rows → 2', 'in levels of 4:2', 'most of the area']});
  arrowR(L, 400, y + 10, 450);
  const al = ipart(L, ap, 'fmaalign', 170, y + 130, 230, 90, 'var(--c4)', 'align c', {node: 'vpu.lane.fma.norm', sub: ['shift by the exponents']});
  KT.wire(L, [[-130, y + 144], [170, y + 144]]);
  KT.wire(L, [[400, y + 174], [474, y + 174], [474, y + 100]]);
  ipart(L, ap, 'fmaadd', 450, y - 50, 160, 150, 'var(--c4)', 'adder', {node: 'vpu.lane.fma.norm', sub: ['two rows', 'and c: one sum']});
  arrowR(L, 610, y + 10, 650);
  ipart(L, ap, 'fmalzd', 650, y - 50, 140, 150, 'var(--c4)', 'lead zeros', {node: 'vpu.lane.fma.norm', sub: ['how far', 'to shift']});
  arrowR(L, 790, y + 10, 830);
  ipart(L, ap, 'fmanorm', 830, y - 50, 120, 150, 'var(--c4)', 'normalise', {node: 'vpu.lane.fma.norm', sub: ['shift']});
  arrowR(L, 950, y + 10, 980);
  ipart(L, ap, 'fmarnd', 980, y - 50, 100, 150, 'var(--c4)', 'round', {node: 'vpu.lane.fma.norm', sub: ['once']});
  KTT(L, 1080, y + 130, 'a × b + c', 't-net', 'end');
  // the energy note: zeros clock nothing
  const gz = KT.comp(L, 'fmazero', {}, 'A zero operand: the lane’s clock is withheld');
  S(E('rect', {class: 'shape', x: -150, y: 520, width: 760, height: 120, rx: 8}, gz), {fill: 'var(--c2)', fillOpacity: 0.06, stroke: 'var(--c2)', strokeWidth: 1.5, strokeDasharray: '6 5'});
  gz._box = {x: -150, y: 520, w: 760, h: 120};
  KTT(gz, -134, 552, 'Why random data costs more than zeros', 't-smb');
  KTT(gz, -134, 578, 'a zero operand word: the lane’s clock is withheld, nothing toggles;', 't-sm');
  KTT(gz, -134, 600, 'random operands toggle tens of thousands of nets in the tree each op', 't-sm');
  gz._info = {title: 'Zeros and random data', lead: 'A zero operand switches nothing: the lane’s clock is withheld when an operand word is zero. Random data toggles the multiplier tree’s nets, and each toggle costs energy.', facts: sc('vpu.lane.fma').facts};
  KTT(L, 640, 560, 'textbook stages; the blocks are the RTL’s modules', 't-sm');
  KTT(L, 640, 582, '(core-et’s Erbium branch: not confirmed', 't-sm'); KTT(L, 640, 604, 'to match the silicon)', 't-sm');
}, def: () => ({id: 'vpu.lane.fma.tree'}), kids: () => [{id: 'vpu.lane.fma.tree'}]});
/* the compressor tree: 17 rows of partial-product bits reduced to 2, a column of it ringed */
bnode('vpu.lane.fma.tree', {draw: (L, ap) => {
  KT.frame(L, {title: 'The compressor tree: 17 rows of bits become 2', sub: `${on('pp17')} of about ${on('pp33')}, each Booth row shifted two places; about ${on('tree_tr')} (an estimate)`, subf: `${onf('pp17')} ${onf('tree_tr')}`,
    col: CC.logic, tags: [['generic', 'textbook schedule'], ['unknown', 'modules: Erbium RTL']]});
  const NC = 65, D = 13.6, X0 = -140, Y0 = 34, RH = 12.6;
  const g = KT.comp(L, 'treedots', {}, 'The 17 partial products, each a row of bits');
  g._info = {title: 'The partial products', lead: sc('vpu.lane.fma.booth').blurb, facts: sc('vpu.lane.fma.booth').facts};
  for (let r = 0; r < 17; r++) for (let c = 0; c < 33; c++) E('circle', {cx: X0 + (NC - 1 - (2 * r + c)) * D, cy: Y0 + r * RH, r: 2.7, class: 'jn'}, g);
  g._box = {x: X0 - 8, y: Y0 - 10, w: NC * D + 8, h: 17 * RH + 12};
  KTT(L, X0 + NC * D + 10, Y0 + 8 * RH, '17 rows', 't-smb');
  // the levels that follow, smaller, in a row of four under it
  const lv = [[9, '4:2 compressors'], [5, '4:2 compressors'], [3, '4:2 compressors'], [2, 'full adders: 3 → 2']], d = 4.4, rh = 9;
  const gl = KT.comp(L, 'treelevels', {}, 'The levels of the tree: 17 rows to 9, 5, 3 and 2');
  gl._info = {title: 'The levels of the tree', lead: sc('vpu.lane.fma.tree').blurb, facts: sc('vpu.lane.fma.tree').facts};
  lv.forEach(([n, how], i) => {
    const x = X0 + i * 300, y = 350;
    for (let r = 0; r < n; r++) for (let c = 0; c < NC; c++) E('circle', {cx: x + c * d, cy: y + r * rh, r: 1.7, class: 'jn'}, gl);
    KTT(gl, x, y - 18, `${n} rows`, 't-smb'); KTT(gl, x, y + n * rh + 20, how, 't-sm');
    if (i < 3) arrowR(gl, x + NC * d + 6, y + 10, x + 294);
  });
  gl._box = {x: X0 - 6, y: 322, w: 1200, h: 140};
  arrowR(L, X0 + 30 * D, Y0 + 17 * RH + 16, X0 + 30 * D + 1);
  KT.wire(L, [[X0 + 20, Y0 + 17 * RH + 14], [X0 + 20, 320]], 'thin');
  KTT(L, X0 + 30, 300, 'level by level, every four bits of a column become two', 't-sm');
  // one column, ringed: the seat of the column's own drawing
  const cx = X0 + (NC - 1 - 32) * D, cr = {x: cx - 11, y: Y0 - 12, w: 22, h: 17 * RH + 16};
  ipart(L, ap, 'treecol', cr.x, cr.y, cr.w, cr.h, 'var(--c2)', '', {node: 'fma.tree.col', kid: {id: 'fma.tree.col'}, fo: 0.15, label: 'One column of the tree'});
  KTT(L, cx, Y0 + 17 * RH + 34, 'one column', 't-smb', 'middle');
  KTT(L, -150, 560, 'two rows remain: one wide adder (the next box of the multiply-add) makes them one', 't-sm');
  KTT(L, -150, 676, 'a textbook schedule for 17 rows; the RTL has Wallace-tree, 4:2 and carry-save modules, its own schedule not drawn', 't-sm');
}, def: () => ({id: 'fma.tree.col'}), kids: () => [{id: 'fma.tree.col'}]});
/* one column of the tree: 17 bits down through 4:2 compressors to 2, carries to and from the neighbouring columns */
bnode('fma.tree.col', {draw: (L, ap) => {
  KT.frame(L, {title: 'One column of the tree', sub: 'its 17 bits pass down through 4:2 compressors; each sends a carry to the next column and takes one from the last', col: CC.logic, tags: [['generic', 'textbook']]});
  const X = i => 40 + i * 52;
  const gd = KT.comp(L, 'colbits', {}, 'The column’s 17 bits, one from each partial product');
  for (let i = 0; i < 17; i++) E('circle', {cx: X(i), cy: 40, r: 6, class: 'jn'}, gd);
  gd._box = {x: X(0) - 10, y: 28, w: X(16) - X(0) + 20, h: 24};
  gd._info = {title: 'The column’s bits', lead: 'One bit from each of the 17 partial products that falls in this column: the multiplier adds them, with the carries from the column before.', facts: sc('vpu.lane.fma.booth').facts};
  KTT(L, X(16) + 20, 46, '17 bits', 't-smb');
  const levels = [{y: 110, n: 4, pass: 1}, {y: 270, n: 2, pass: 1}, {y: 420, n: 1, pass: 1}, {y: 560, n: 1, fa: true}];
  let first = null;
  levels.forEach((lv, li) => {
    for (let j = 0; j < lv.n; j++) {
      const x = 60 + j * 230, w = 170, h = 74, fa = !!lv.fa;
      const g = ipart(L, ap, fa ? 'colfa' : 'colc42', x, lv.y, w, h, CC.logic, fa ? 'full adder' : '4:2', {node: fa ? 'lib.fa' : 'lib.cmp42', center: true, ty: 34,
        sub: [fa ? '3 bits → 2' : '4 bits → 2'], kid: {id: fa ? 'lib.fa' : 'lib.cmp42'}});
      if (!first && !fa) first = g;
      KT.wire(L, [[x + w / 2, lv.y - 14], [x + w / 2, lv.y]]);
      E('path', {class: 'w', d: `M${x - 6},${lv.y + 22} H${x - 40}`}, L); KTT(L, x - 44, lv.y + 18, li === 0 && j === 0 ? 'cout →' : '', 't-sm', 'end');
      KT.wire(L, [[x + w + 40, lv.y + 52], [x + w + 6, lv.y + 52]], 'thin');
      KT.wire(L, [[x + 50, lv.y + h], [x + 50, lv.y + h + 26]]); KT.wire(L, [[x + 120, lv.y + h], [x + 120, lv.y + h + 26]], 'thin');
    }
    if (lv.pass) { const px = 60 + lv.n * 230; KT.wire(L, [[px + 40, lv.y - 14], [px + 40, lv.y + 100]], 'thin'); KTT(L, px + 52, lv.y + 40, 'a bit passes', 't-sm'); }
    KTT(L, -150, lv.y + 44, ['17 → 9', '9 → 5', '5 → 3', '3 → 2'][li], 't-smb');
  });
  KTT(L, -150, 652, 'each 4:2 takes a carry in from the column on its right and sends one to the column on its left (cout);', 't-sm');
  KTT(L, -150, 678, 'its own carry goes down a column to the left', 't-sm');
  ap.zs['lib.cmp42'] = {r: {x: 60, y: 110, w: 170, h: 74}, g: first};
}, def: () => ({id: 'lib.cmp42'}), kids: () => [{id: 'lib.cmp42'}, {id: 'lib.fa'}]});
