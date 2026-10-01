/* ================= inside the chip: the scales under the die, the shire and the minion (30 September 2026) =================
   The owner's request: "double-click on individual parts of the chip like the L1 cache and zoom in until I get
   individual circuit components. This was done in the anatomy of the DRAM access." The memory levels' chains are
   drawn by their own builders, copied into circuitkit.js (CKT): the L1 down to a latch and the tag comparator, the
   shire cache down to a 6T cell, one mesh hop down to its wire and repeater, the memory shire, its PHY and DQ driver,
   and the DRAM down to a cell. Each is a scale of the tree (research/inside.json, D.scales: its name, its lead, its
   size, its facts); a scale's key carries the instance it shows (a bank, a block, a channel), so every sibling part
   double-clicks, and the example address of the memory levels picks the default. Sizes here are order-of-magnitude
   estimates: no floorplan of the chip's inside is published. */
const ISC = D.scales || {};
const MLF = CKT.FR;
/* the copied drawings' rest view: their frame, centred in the drawing's box */
const MLV = {x: MLF.x + MLF.w / 2 - VB.w / 2, y: VB.y, w: VB.w, h: VB.h};
/* a part's box in a built layer: the first rect.shape of the comp with that key (and, optionally, that context) */
function partBox(L, key, test) {
  const g = [...L.querySelectorAll(`.comp[data-comp="${key}"]`)].find(x => !test || test(x._ctx || {}));
  if (!g) return null;
  const r = g.querySelector('rect.shape');
  const b = r ? {x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height')} : g._box;
  return b ? {r: b, g} : null;
}
/* the scale a copied drawing's part leads to: its data-child mapped onto the tree's scale (map[child](ctx, g) gives
   the path element and its seat in this drawing); every part with that child gets it */
function mlKids(L, ap, map) {
  L.querySelectorAll('.comp').forEach(g => {
    const c = g.getAttribute('data-child'), m = c && map[c];
    if (!m) return;
    const r = m(g._ctx || {}, g, ap); if (!r) return;
    g._kid = r.el;
    const key = pk(r.el);
    if (!ap.zs[key] || r.main) ap.zs[key] = {r: r.seat || g._box, g, tr: r.tr};
  });
}
/* siblings: the copies mark only the example's part as zoomable (their access follows one address); here every bank,
   block or channel is, each with its own instance (key) */
function mlSibs(L, ap, key, fn) {
  L.querySelectorAll(`.comp[data-comp="${key}"]`).forEach(g => {
    const r = fn(g._ctx || {}, g, ap); if (!r) return;
    g._kid = r.el; g.setAttribute('data-child', r.el.id);
    const k = pk(r.el); if (!ap.zs[k]) ap.zs[k] = {r: r.seat || g._box, g, tr: r.tr};
  });
}
/* a scale of the tree, drawn by a copied builder in its frame (MLF) */
function inode(id, o) {
  const s = ISC[id] || {};
  return node(id, Object.assign({
    name: () => s.name || id, short: () => s.short || id, to: () => inName(s.name && s.name.length <= 34 ? s.name : s.short || id),
    size: () => (s.m > 0 ? {m: s.m, kind: s.kind, f: s.f || null} : null),
    frame: () => MLF, view: () => MLV, inside: true,
  }, o));
}
const n0 = v => (v == null || isNaN(v) ? 0 : v);
/* a scale's name inside a sentence: "the fused multiply-add unit", "the vector unit", but "LRAM block 1", "XOR / XNOR
   gate", "the FinFET transistor" (a word with capitals inside keeps them; a name with no article and no number gets
   "the": review of 1 Oct) */
const inName = t => {
  const s0 = String(t).replace(/^(The|A|An|One) /, m => m.toLowerCase()).replace(/^([A-Z])([a-z]+)(?=[\s,]|$)/, (m, a, b) => (/^(Booth|Wallace)$/.test(a + b) ? m : a.toLowerCase() + b));
  return /^(the|a|an|one) /.test(s0) || /\d\s*$/.test(s0) ? s0 : 'the ' + s0;
};
const L1X = () => CKT.INST.l1(), L2X = () => CKT.INST.l2(), DRX = () => CKT.INST.dram();

/* ---- the L1 data cache: latch RAM on the minion rail ---- */
inode('l1d', {
  build: (L, ap) => {
    const inst = L1X();
    CKT.build(CKT.buildL1Cache, L, ap, inst, CKT.parts.l1);
    mlSibs(L, ap, 'blocks', c => ({el: {id: 'l1d.block', k: String(c.i)}, seat: ap.blockBox[c.i]}));
    mlKids(L, ap, {cmp: () => ({el: {id: 'l1d.cmp'}, seat: ap.cmpBox})});
  },
  seat: (ap, p, pel, Lp) => partBox(Lp, 'l1d'),
  def: () => ({id: 'l1d.block', k: String(L1X().block)}), kids: () => [{id: 'l1d.block', k: String(L1X().block)}, {id: 'l1d.cmp'}]});
inode('l1d.block', {parse: k => ({block: +k}), name: p => `LRAM block ${p.block}`, to: p => `LRAM block ${p.block}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildL1Block, L, ap, Object.assign(L1X(), {block: p.block}), CKT.parts.l1);
    mlKids(L, ap, {row: () => ({el: {id: 'l1d.row'}, seat: ap.rowBox, main: true})});
  },
  def: () => ({id: 'l1d.row'}), kids: () => [{id: 'l1d.row'}]});
inode('l1d.row', {
  build: (L, ap) => {
    CKT.build(CKT.buildL1Row, L, ap, L1X(), CKT.parts.l1);
    mlKids(L, ap, {latch: () => ({el: {id: 'lib.latch'}, seat: ap.latchBox})});
  },
  def: () => ({id: 'lib.latch'}), kids: () => [{id: 'lib.latch'}]});
inode('lib.latch', {build: (L, ap) => CKT.build(CKT.buildL1Latch, L, ap, L1X(), CKT.parts.l1)});
inode('l1d.cmp', {build: (L, ap) => CKT.build(CKT.buildL1Cmp, L, ap, L1X(), CKT.parts.l1)});

/* ---- the shire cache: four banks, sub-banks, SRAM panels, one 6T cell ---- */
const bsp = k => { const q = String(k).split('.').map(Number); return {bank: n0(q[0]), sub: n0(q[1]), panel: n0(q[2])}; };
inode('shire.bank', {parse: k => bsp(k), name: p => `Cache bank ${p.bank}`, short: p => `Bank ${p.bank}`, to: p => `cache bank ${p.bank}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildL2Bank, L, ap, Object.assign(L2X(), {bank: p.bank}), CKT.parts.l2);
    mlSibs(L, ap, 'subbanks', c => (ap.sub[c.i] ? {el: {id: 'shire.subbank', k: `${p.bank}.${c.i}`}, seat: ap.sub[c.i].box} : null));
  },
  def: p => ({id: 'shire.subbank', k: `${p.bank}.${L2X().sub}`}), kids: p => [0, 1, 2, 3].map(s => ({id: 'shire.subbank', k: `${p.bank}.${s}`}))});
inode('shire.subbank', {parse: k => bsp(k), name: p => `Sub-bank ${p.sub} of bank ${p.bank}`, short: p => `Sub-bank ${p.sub}`, to: p => `sub-bank ${p.sub}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildL2Sub, L, ap, Object.assign(L2X(), {bank: p.bank, sub: p.sub}), CKT.parts.l2);
    mlKids(L, ap, {panel: () => ({el: {id: 'shire.panel', k: `${p.bank}.${p.sub}.${L2X().panel}`}, seat: ap.panelBox, main: true})});
  },
  def: p => ({id: 'shire.panel', k: `${p.bank}.${p.sub}.${L2X().panel}`}), kids: p => [{id: 'shire.panel', k: `${p.bank}.${p.sub}.${L2X().panel}`}]});
inode('shire.panel', {parse: k => bsp(k), name: p => `Data panel ${p.panel}, sub-bank ${p.sub}, bank ${p.bank}`, short: p => `Panel ${p.panel}`, to: p => `data panel ${p.panel}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildL2Panel, L, ap, Object.assign(L2X(), {bank: p.bank, sub: p.sub, panel: p.panel}), CKT.parts.l2);
    const k = ap.rowK, y = ap.Y0 + k * ap.RH;
    ap.zs['lib.sram6t'] = {r: {x: ap.AX + ap.CW, y: y + 2, w: ap.CW - 12, h: ap.RH - 16}, g: ap.zg.cell || null};
    if (ap.zg.cell) ap.zg.cell._kid = {id: 'lib.sram6t'};
  },
  def: () => ({id: 'lib.sram6t'}), kids: () => [{id: 'lib.sram6t'}]});
inode('lib.sram6t', {build: (L, ap) => CKT.build(CKT.buildL2Cell, L, ap, L2X(), CKT.parts.l2)});
inode('shire.meshstop.xing', {build: (L, ap) => CKT.build(CKT.buildL2Xing, L, ap, L2X(), CKT.parts.l2)});

/* ---- the mesh: one hop, its wire, a repeater ---- */
inode('mesh', {name: () => 'One mesh hop', short: () => 'Hop', to: () => 'one mesh hop',
  // (its size is one hop's wire, the tile pitch, not the whole mesh's: review of 1 Oct)
  size: () => ({m: 3.72e-3, kind: 'inferred', f: 'chip.hop-pitch'}),
  build: (L, ap) => {
    CKT.build(CKT.buildMeshHop, L, ap, {}, CKT.parts.l3);
    if (ap.repBox) { ap.zs['mesh.link.wire'] = {r: ap.repBox, g: ap.zg.rep || null}; if (ap.zg.rep) ap.zg.rep._kid = {id: 'mesh.link.wire'}; }
  },
  seat: (ap, p, pel, Lp) => meshSeat(Lp),
  def: () => ({id: 'mesh.link.wire'}), kids: () => [{id: 'mesh.link.wire'}]});
inode('mesh.link.wire', {name: () => 'A link bit: a repeater and a level shifter', short: () => 'Wire and repeater', to: () => 'a link bit',
  build: (L, ap) => CKT.build(CKT.buildL3Wire, L, ap, {}, CKT.parts.l3)});
/* the hop's seat on the die: a link between two compute shires in the middle of the grid (shire 21 to shire 13) */
function meshSeat(Lp) {
  const a = SH[21], b = SH[13];
  const cx = (a.sx + b.sx) / 2, cy = (a.sy + b.sy) / 2, w = TILE * 1.2;
  return {r: {x: cx - w / 2, y: cy - w * MLF.h / MLF.w / 2, w, h: w * MLF.h / MLF.w}, g: partBox(Lp, 'mesh') ? partBox(Lp, 'mesh').g : null};
}

/* ---- the DRAM: a memory shire, its PHY and a DQ driver; a package's die, a bank, a cell ---- */
const dk = k => { const q = String(k).split('.').map(Number); return {ms: n0(q[0]), ch: n0(q[1]), bank: n0(q[2])}; };
const dinst = p => Object.assign(DRX(), {ms: p.ms, ch: p.ch != null ? p.ch : DRX().ch, bank: p.bank != null ? p.bank : DRX().bank});
inode('memshire', {parse: k => dk(k), name: p => `Memory shire ${p.ms}`, short: p => `Memory shire ${p.ms}`, to: p => `memory shire ${p.ms}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildMS, L, ap, dinst({ms: p.ms}), CKT.parts.dram);
    mlSibs(L, ap, 'die', c => ({el: {id: 'dram', k: `${p.ms}.${c.i}`}, seat: ap.die[c.i] && ap.die[c.i].box}));
    mlKids(L, ap, {phy: () => ({el: {id: 'memshire.phy', k: String(p.ms)}, seat: ap.phyBox})});
  },
  def: p => ({id: 'dram', k: `${p.ms}.${DRX().ch}`}), kids: p => [{id: 'dram', k: `${p.ms}.${DRX().ch}`}, {id: 'memshire.phy', k: String(p.ms)}]});
inode('memshire.phy', {parse: k => dk(k), name: p => `The DRAM PHY of memory shire ${p.ms}`, short: () => 'PHY',
  build: (L, ap, p) => {
    CKT.build(CKT.buildPHY, L, ap, dinst({ms: p.ms}), CKT.parts.dram);
    mlKids(L, ap, {dq: () => ({el: {id: 'memshire.phy.dq', k: String(p.ms)}, seat: ap.dqBox, main: true})});
  },
  def: p => ({id: 'memshire.phy.dq', k: String(p.ms)}), kids: p => [{id: 'memshire.phy.dq', k: String(p.ms)}]});
inode('memshire.phy.dq', {parse: k => dk(k), build: (L, ap, p) => CKT.build(CKT.buildDQ, L, ap, dinst({ms: p.ms}), CKT.parts.dram)});
inode('dram', {parse: k => dk(k), name: p => `LPDDR4X channel ${p.ch} of memory shire ${p.ms}`, short: p => `Channel ${p.ch}`, to: p => `channel ${p.ch}`,
  // (zoomed in from a memory shire the size grows: say why; review of 1 Oct)
  blurb: () => `${(ISC.dram || {}).blurb || ''} The size here grows: the channel’s memory is in a package beside the chip, larger than the memory shire on the die that drives it.`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildChan, L, ap, dinst({ms: p.ms, ch: p.ch}), CKT.parts.dram);
    mlSibs(L, ap, 'dbanks', c => (ap.bank[c.i] ? {el: {id: 'dram.bank', k: `${p.ms}.${p.ch}.${c.i}`}, seat: ap.bank[c.i].box} : null));
  },
  seat: (ap, p, pel) => (pel.id === 'die' ? dramSeat(ap, p) : null),
  def: p => ({id: 'dram.bank', k: `${p.ms}.${p.ch}.${DRX().bank}`}), kids: p => [{id: 'dram.bank', k: `${p.ms}.${p.ch}.${DRX().bank}`}]});
/* a package on the die: the dashed box beside its two memory shires */
function dramSeat(ap, p) {
  const m = ap.pkg && ap.pkg[p.ms]; if (!m) return null;
  const w = PKW, h = TILE * 1.4;
  return {x: m.x - w / 2, y: m.y - h / 2, w, h};
}
inode('dram.bank', {parse: k => dk(k), name: p => `DRAM bank ${p.bank}, channel ${p.ch}`, short: p => `Bank ${p.bank}`, to: p => `DRAM bank ${p.bank}`,
  build: (L, ap, p) => {
    CKT.build(CKT.buildDBank, L, ap, dinst(p), CKT.parts.dram);
    mlKids(L, ap, {dcell: () => ({el: {id: 'dram.cell'}, seat: ap.cellBox, main: true})});
  },
  def: () => ({id: 'dram.cell'}), kids: () => [{id: 'dram.cell'}]});
inode('dram.cell', {build: (L, ap) => CKT.build(CKT.buildDCell, L, ap, DRX(), CKT.parts.dram)});

/* ---- what the chip's own parts zoom into ---- */
Object.assign(KIDS, {
  l1d: () => ({id: 'l1d'}),
  l1scp: () => ({id: 'l1d'}),
  banks: c => ({id: 'shire.bank', k: String(c.bank != null ? c.bank : 0)}),
  l2: () => ({id: 'shire.bank', k: String(L2X().bank)}),
  l3: () => ({id: 'shire.bank', k: '0'}),
  scp: () => ({id: 'shire.bank', k: '0'}),
  memshire: c => ({id: 'memshire', k: String(c.cell.id)}),
  dram: c => ({id: 'dram', k: `${c.ms[0]}.${DRX().ch}`}),
  mesh: () => ({id: 'mesh'}),
});
/* the seats of those scales in the chip's own drawings (the die's and the shire's parts) */
function chipSeats(L, ap, el) {
  if (el.id === 'die') {
    CELLS.forEach(c => { if (c.type === 'memshire' && c.g) ap.zs['memshire:' + c.id] = {r: {x: c.x + INS, y: c.y + INS, w: c.w - 2 * INS, h: c.h - 2 * INS}, g: c.g}; });
    L.querySelectorAll('.comp[data-comp="dram"]').forEach(g => { const ms = g._ctx.ms; const r = dramSeat(ap, {ms: ms[0]}); if (r) ap.zs[`dram:${ms[0]}.${DRX().ch}`] = {r, g}; });
    ap.zs.mesh = meshSeat(L);
  }
  if (el.id === 'shire') {
    (ap.bank || []).forEach((b, i) => { const pb = partBox(L, 'banks', c => c.bank === i); ap.zs['shire.bank:' + i] = {r: b.box, g: pb ? pb.g : null}; });
  }
}
/* a part of a copied drawing: its panel from the copy's parts texts, with the tree's zoom row */
function showMLPart(g) {
  const d = CKT.partText(g);
  if (!d) { showNodePart(Object.assign(g, {_info: {title: (g.getAttribute('aria-label') || '').replace(/[:.].*$/, ''), lead: ''}})); return; }
  const P = layerPath(g) || Z.path, el = P[P.length - 1];
  // a beginner's line above the zoom row, as the chip's own parts have (LEADS): the tree's line for the scale the part
  // opens, else the first sentence of its text, whose rest stays under Details (review of 1 Oct: 133 kinds of part
  // showed only a title and badges)
  const k = kidOf(g), kb = k && !k.up && ISC[k.id] ? ISC[k.id].blurb : '';
  const ss = String(d.what || '').split(/(?<=[.!?])\s+(?=[A-Z(])/);
  const lead = kb ? esc(kb) : ss[0] || '', rest = kb ? d.what : ss.slice(1).join(' ');
  panel(`<p class="pn-kick">${esc(d.kick || shortOf(el))}</p><p class="pn-title">${esc(d.title || '')}</p>`
    + (lead ? `<p class="pn-lead">${lead}</p>` : '') + zoomRowPart(g, d.title)
    + detBlock((d.badge ? `<p class="pn-badge">${d.badge}</p>` : '') + (rest ? `<p class="pn-what">${rest}</p>` : '') + (d.kpis.length ? `<div class="pn-kpis">${d.kpis.join('')}</div>` : '')));
}

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
const firstClause = t => { const s0 = String(t || '').split(/(?<=[.;:])\s/)[0]; return s0.length > 96 ? s0.slice(0, 94).replace(/\s+\S*$/, '') + '…' : s0; };
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
    const most = Math.min(3, Math.max(1, ...kids.map(k => wrapW(firstClause(sc(k).blurb), wrapAt).length)));
    const bh = Math.min(260, (H - gh * (rows - 1)) / rows, 50 + 23 + LH * most + 22);
    const y1 = y + Math.max(0, (H - rows * bh - gh * (rows - 1)) * 0.4);
    kids.forEach((k, i) => {
      const r = Math.floor(i / cols), c = i % cols, x = X0 + c * (bw + gw), yy = y1 + r * (bh + gh), s1 = sc(k);
      const cap = Math.max(1, Math.min(3, Math.floor((bh - 50) / LH))), all = wrapW(firstClause(s1.blurb), wrapAt);
      const lines = all.slice(0, cap); if (all.length > cap) lines[cap - 1] = lines[cap - 1].replace(/[,;:.]?\s*\S*$/, '…');
      const has = !!NODES[k], nm = String(s1.name || k).replace(/\s*\(.*$/, '');
      ipart(L, ap, k, x, yy, bw, bh, has ? CC.logic : 'var(--ink-2)', nm.length < bw / 11 ? nm : s1.short && s1.short.length < bw / 11 ? s1.short : wrapW(nm, Math.floor(bw / 11))[0],
        {node: k, kid: has ? {id: k} : null, sub: lines, fo: has ? 0.12 : 0.06, opts: has ? null : madeOf(k), lh: LH, ty: 40});
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
