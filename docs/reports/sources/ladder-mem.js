/* ================= ladder-mem.js: the memory chains as scales of the ladder, shared (1 October 2026) =================
   The memory levels' drawings (circuitkit.js) as nodes of the path camera: the L1 to a latch, the shire cache to a 6T
   cell, a mesh hop to its wire, the memory shire to a DQ driver and the DRAM to a cell. Split from
   chip-diagram.inside.js (30 September); the seats on the chip's own drawings (meshSeat, dramSeat, chipSeats) are
   the chip's. */
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
    size: () => scSz(s),
    frame: () => MLF, view: () => MLV, inside: true, egg: !!s.egg,
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

