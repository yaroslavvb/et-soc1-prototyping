/* ================= memory-levels.nodes.js: the memory levels' own scenes as scales of the shared ladder (1 October 2026) =================
   Part of memory-levels.ladder.js's scope (included there, after ladder-mem.js). The levels' places in the chip
   diagram's vocabulary (DESIGN §1.3, §3.5): the map of each chip level is the die (die:l3, die:scp, die:dram: one
   scale, three drawings of it, as the levels' own camera cross-fades them); the L2's shire is shire:R inside it, R the
   requester; the L1's minion is minion:R.0.0 in that shire; the L3's home shire and its chain and the scratchpad's
   shire and its chain have node ids of their own (l3.home, l3.bank, ...; scp.shire, ...), drawn only here; their
   sizes are the chip's scales' they stand for (a shire, a bank, ...). Each
   is drawn by the levels' own builder with their example address (or another instance where the path says so: a
   bank, a shire), in the levels' frame (FR), and shown where the levels' own camera shows it (mlView). */
const LEVELS = ['l1', 'l2', 'l3', 'scp', 'dram'];
const CHIPLV = ['l3', 'scp', 'dram'];
/* the chip level the camera was last at (the L2's shire and the L1's minion sit in its map); the levels' camera picks
   the same (restLeg: the L3 until another is visited) */
let LASTV = 'l3';
const chipV = () => (CHIPLV.includes(ML.Z.lv) ? ML.Z.lv : LASTV);
const INST = lv => ML.SCENES[lv].inst;
const REQ = V0 => (ML.SCENES[V0] && ML.SCENES[V0].inst.req != null ? ML.SCENES[V0].inst.req : 0);
/* a levels' scale (level lv, scale id) as a path element of the ladder, for the example's instance */
function mlEl(lv, id, V0) {
  const i = INST(lv), R = REQ(V0 || chipV());
  switch (lv + ':' + id) {
    case 'l1:minion': return {id: 'minion', k: `${R}.0.0`};
    case 'l1:dcache': return {id: 'l1d'};
    case 'l1:lram': return {id: 'l1d.block', k: String(i.block)};
    case 'l1:row': return {id: 'l1d.row'};
    case 'l1:latch': return {id: 'lib.latch'};
    case 'l1:cmp': return {id: 'l1d.cmp'};
    case 'l2:shire': return {id: 'shire', k: String(R)};
    case 'l2:bank': return {id: 'shire.bank', k: String(i.bank)};
    case 'l2:sub': return {id: 'shire.subbank', k: `${i.bank}.${i.sub}`};
    case 'l2:panel': return {id: 'shire.panel', k: `${i.bank}.${i.sub}.${i.panel || 0}`};
    case 'l2:cell': case 'l3:cell': case 'scp:cell': return {id: 'lib.sram6t'};
    case 'l2:xing': return {id: 'shire.meshstop.xing'};
    case 'l3:chip': return {id: 'die', k: 'l3'};
    case 'l3:home': return {id: 'l3.home', k: String(i.home)};
    case 'l3:hbank': return {id: 'l3.bank', k: String(i.bank)};
    case 'l3:sub': return {id: 'l3.subbank', k: `${i.bank}.${i.sub}`};
    case 'l3:panel': return {id: 'l3.panel', k: `${i.bank}.${i.sub}.${i.panel || 0}`};
    case 'l3:hop': case 'scp:hop': return {id: 'mesh'};
    case 'l3:rep': case 'scp:rep': return {id: 'mesh.link.wire'};
    case 'scp:chip': return {id: 'die', k: 'scp'};
    case 'scp:shire': return {id: 'scp.shire', k: String(i.shire)};
    case 'scp:bank': return {id: 'scp.bank', k: `${i.bank}.${i.sub}`};
    case 'scp:panel': return {id: 'scp.panel', k: `${i.bank}.${i.sub}.${i.panel || 0}`};
    case 'scp:vmin': return {id: 'scp.vmin'};
    case 'dram:chip': return {id: 'die', k: 'dram'};
    case 'dram:ms': return {id: 'memshire', k: String(i.ms)};
    case 'dram:chan': return {id: 'dram', k: `${i.ms}.${i.ch}`};
    case 'dram:dbank': return {id: 'dram.bank', k: `${i.ms}.${i.ch}.${i.bank}`};
    case 'dram:dcell': return {id: 'dram.cell'};
    case 'dram:phy': return {id: 'memshire.phy', k: String(i.ms)};
    case 'dram:dq': return {id: 'memshire.phy.dq', k: String(i.ms)};
  }
  return null;
}
/* a place of the levels' own camera (level lv, its path of scale ids) as a path of the ladder: the levels outside it
   first (the L1's minion is in the L2's shire, which is in a chip level's map, V) */
function mlPath(lv, path, V0) {
  const V1 = CHIPLV.includes(lv) ? lv : V0 || chipV();
  const pre = lv === 'l1' ? [{id: 'die', k: V1}, mlEl('l2', 'shire', V1)] : lv === 'l2' ? [{id: 'die', k: V1}] : [];
  return OUT_IDS.map(id => ({id})).concat(pre, path.map(id => mlEl(lv, id, V1)));
}
/* the levels' place a path of the ladder is, if their own camera can show it: {lv, path}; else null */
function mlOf(P) {
  const d = OUT_IDS.length;
  if (!P || P.length <= d || P[d].id !== 'die') return null;
  const V0 = P[d].k || chipV(); if (!CHIPLV.includes(V0)) return null;
  const key = pkeys(P);
  for (const lv of LEVELS) {
    const sc = ML.SCENES[lv];
    for (const id of Object.keys(sc.scales)) {
      const p = ML.pathIn(lv, id);
      if (pkeys(mlPath(lv, p, V0)) === key) return {lv, path: p, V: V0};
    }
  }
  return null;
}
/* the deepest place of the levels' own camera on a path (where a move from the ladder's scales hands over to them) */
function mlCut(P) {
  for (let i = P.length; i > OUT_IDS.length; i--) { const m = mlOf(P.slice(0, i)); if (m) return {P: P.slice(0, i), m}; }
  return null;
}

/* ---- the scenes the levels draw: one node per scale of theirs; built by their builder into the path camera's layer,
   with their example (and the instance the path names), every part with a data-child seated for the scale it opens ---- */
const MLSC = {};   // node id -> [level, scale id]
/* a phone: the levels' frame whole, letterboxed into the box's shape (the chip diagram's fit) */
function mlFit() { const v = MFR, hw = PV[0].h / PV[0].w; return v.h / v.w <= hw ? {x: v.x, y: v.y, w: v.w, h: v.w * hw} : {x: v.x + v.w / 2 - v.h / hw / 2, y: v.y, w: v.h / hw, h: v.h}; }
function mnode(id, lv, sid, o) {
  MLSC[id] = [lv, sid];
  const s0 = (D.scales || {})[id] || {};
  return node(id, Object.assign({
    name: () => s0.name || ML.SCENES[lv].scales[sid].name, short: () => s0.short || ML.SCENES[lv].scales[sid].short,
    to: () => inName(s0.name || ML.SCENES[lv].scales[sid].name),
    // (a phone: the levels' own window where the scene is their example's, the camera handing over there; another
    // instance's, another bank or shire, is the ladder's alone, and is fitted whole: review of 1 Oct, its parts were cut
    // off and could not be scrolled to)
    size: () => scSz(o.sizeOf ? (D.scales || {})[o.sizeOf] : s0), frame: () => MFR, view: () => mlView(), pv: (p, el) => (el && el.k != null && pk(el) !== pk(mlEl(lv, sid)) ? mlFit() : mlView()), inside: true, mlv: true,
  }, o, {build: (L, ap, p, P, d) => {
    const patch = o.patch ? o.patch(p, P) : {};
    ML.buildScene(L, ap, lv, sid, patch);
    mlSeats(L, ap, lv, sid, P.slice(0, d + 1), patch);
    if (o.after) o.after(L, ap, p, P, d);
  }}));
}
/* the seats of the scales a levels' scene opens: every part with a data-child, for the instance its context names (a
   bank of four), the example's at its own target (the box the levels' camera zooms into) */
function mlSeats(L, ap, lv, sid, P, patch) {
  const sc = ML.SCENES[lv], inst = Object.assign({}, sc.inst, patch || {});
  L.querySelectorAll('.comp[data-child]').forEach(g => {
    const cid = g.getAttribute('data-child'), c = g._ctx || {}, ip = Object.assign({}, inst, c.inst || {});
    const el = ML.withInst(lv, ip, () => mlEl(lv, cid, P[OUT_IDS.length].k));
    if (!el) return;
    let r = g._box || null;
    try { const t = sc.scales[cid].target(ap, ip); if (t && t.w > 0) r = t; } catch (_) { /* a part with no target */ }
    if (!r) return;
    const key = pk(el);
    if (!ap.zs[key] || c.cur || (c.inst && ip.bank === inst.bank)) ap.zs[key] = {r, g};
    g._kid = el;
  });
}
const PARSE_LV = k => ({lv: CHIPLV.includes(k) ? k : chipV()});
const DIESIDE = ['homebox', 'fit', 'mean', 'byhome', 'fmt', 'own', 'remote', 'size', 'fmt1', 'relay', 'model', 'typical', 'rate', 'energy', 'addrmap'];
/* the chip: the map of a chip level (its frame the cells of the die; its packages around it on the DRAM's) */
node('die', {parse: PARSE_LV, name: () => 'The chip', short: () => 'Chip', to: () => 'the chip', size: () => scSz((D.scales || {}).die),
  frame: p => { const g = ML.mapGeom(p.lv); return {x: g.X0, y: g.Y0, w: 6 * g.C, h: 8 * g.C}; },
  view: () => mlView(), pv: () => mlView(), mlv: true,
  build: (L, ap, p, P, d) => {
    ML.buildScene(L, ap, p.lv, 'chip', {}); mlSeats(L, ap, p.lv, 'chip', P.slice(0, d + 1), {}); dieSeats(L, ap, p, P.slice(0, d + 1));
    // the boxes of numbers and the charts beside the map fade with the labels when the camera leaves the map (review of 1
    // Oct: on the way out to the package they shrank into the die's box and the chart spilled over the ball grid)
    DIESIDE.forEach(k => L.querySelectorAll(`.comp[data-comp="${k}"]`).forEach(g => g.classList.add('mlside')));
  },
  seat: (ap, p, pel, Lp) => (pel.id === 'package' && Lp._ap.zs.die ? Lp._ap.zs.die : null),
  def: p => mlEl(p.lv, ML.SCENES[p.lv].scales.chip.def, p.lv),
  here: () => mlHere()});
/* the L2's shire: shire:R in a chip level's map (R the requester); another shire's is the same drawing, its own panel */
mnode('shire', 'l2', 'shire', {parse: k => ({sid: +k}), name: p => (p.sid === 32 ? 'Shire 32, the master' : p.sid === 33 ? 'Shire 33, the spare' : `Shire ${p.sid}`), short: p => `Shire ${p.sid}`, to: p => `shire ${p.sid}`,
  size: () => scSz((D.scales || {}).shire),
  seat: (ap, p, pel, Lp) => (pel.id === 'die' && Lp._ap.B && Lp._ap.B['s' + p.sid] ? {r: Lp._ap.B['s' + p.sid], g: tileOf(Lp, p.sid)} : null),
  // (another shire's copy says its number in the title; the example's keeps the levels' own title, so that the two
  // cameras' pictures still coincide at a hand-over: review of 1 Oct, every copy read "Shire")
  after: (L, ap, p) => {
    const ex = mlEl('l2', 'shire'); if (!ex || p.sid === +ex.k) return;
    const t = L.querySelector('.frm > text.t-big'); if (t && /^Shire\b/.test(t.textContent)) t.textContent = t.textContent.replace(/^Shire\b/, `Shire ${p.sid}`);
  },
  def: () => mlEl('l2', 'bank'), here: () => mlHere()});
/* the L1's minion: minion:R.n.m in the L2's shire (the example is minion 0 of neighbourhood 0) */
mnode('minion', 'l1', 'minion', {parse: k => { const q = String(k).split('.').map(Number); return {sid: q[0], nb: q[1] || 0, mi: q[2] || 0}; },
  name: p => `Minion ${p.mi} · neighbourhood ${p.nb} · shire ${p.sid}`, short: p => `Minion ${p.mi}`, to: p => `minion ${p.mi} of neighbourhood ${p.nb}`,
  size: () => scSz((D.scales || {}).minion),
  seat: (ap, p, pel, Lp) => { const r = minRect(p.nb, p.mi); return pel.id === 'shire' ? {r, g: nbOf(Lp, p.nb)} : null; },
  def: () => ({id: 'l1d'}), here: () => mlHere()});
/* a minion's box in the L2's shire drawing (buildL2Shire: four neighbourhoods of two rows of four) */
const minRect = (nb, mi) => ({x: -136 + nb * 276 + 12 + (mi % 4) * 62, y: 42 + Math.floor(mi / 4) * 44 + 12, w: 56, h: 34});
const tileOf = (L, sid) => [...L.querySelectorAll('.comp[data-comp="shire"]')].find(g => g._ctx && g._ctx.id === sid) || null;
const nbOf = (L, nb) => [...L.querySelectorAll('.comp[data-comp="nbr"]')].find(g => g._ctx && g._ctx.i === nb) || null;
/* the L3's home shire and its chain, the scratchpad's shire and its chain: the levels' own drawings */
const bsk = k => { const q = String(k).split('.').map(Number); return {bank: q[0] || 0, sub: q[1] || 0, panel: q[2] || 0}; };
mnode('l3.home', 'l3', 'home', {sizeOf: 'shire', parse: k => ({sid: +k}), name: p => `Shire ${p.sid}, the L3 home`, short: p => `Shire ${p.sid}`, to: p => `shire ${p.sid}, the line's L3 home`,
  patch: p => ({home: p.sid}),
  seat: (ap, p, pel, Lp) => (Lp._ap.B && Lp._ap.B['s' + p.sid] ? {r: Lp._ap.B['s' + p.sid], g: tileOf(Lp, p.sid)} : null),
  def: () => mlEl('l3', 'hbank'), here: () => mlHere()});
mnode('l3.bank', 'l3', 'hbank', {sizeOf: 'shire.bank', parse: k => bsk(k), name: p => `L3 slice in bank ${p.bank}`, short: p => `L3 slice ${p.bank}`, to: p => `the L3 slice in bank ${p.bank}`,
  patch: (p, P) => ({bank: p.bank, home: homeOf(P)}), def: p => ({id: 'l3.subbank', k: `${p.bank}.${INST('l3').sub}`}), here: () => mlHere()});
mnode('l3.subbank', 'l3', 'sub', {sizeOf: 'shire.subbank', parse: k => bsk(k), name: p => `Sub-bank ${p.sub} of bank ${p.bank} (L3)`, short: p => `Sub-bank ${p.sub}`, to: p => `sub-bank ${p.sub}`,
  patch: (p, P) => ({bank: p.bank, sub: p.sub, home: homeOf(P)}), def: p => ({id: 'l3.panel', k: `${p.bank}.${p.sub}.${INST('l3').panel || 0}`}), here: () => mlHere()});
mnode('l3.panel', 'l3', 'panel', {sizeOf: 'shire.panel', parse: k => bsk(k), name: p => `Data panel ${p.panel}, sub-bank ${p.sub}, bank ${p.bank} (L3)`, short: p => `Panel ${p.panel}`, to: p => `data panel ${p.panel}`,
  patch: (p, P) => ({bank: p.bank, sub: p.sub, panel: p.panel, home: homeOf(P)}), def: () => ({id: 'lib.sram6t'}), here: () => mlHere()});
const homeOf = P => { const e = P.find(x => x.id === 'l3.home' || x.id === 'scp.shire'); return e ? +e.k : 0; };
mnode('scp.shire', 'scp', 'shire', {sizeOf: 'shire', parse: k => ({sid: +k}), name: p => `Shire ${p.sid}, its scratchpad`, short: p => `Shire ${p.sid}`, to: p => `shire ${p.sid}'s scratchpad`,
  patch: p => ({shire: p.sid}),
  seat: (ap, p, pel, Lp) => (Lp._ap.B && Lp._ap.B['s' + p.sid] ? {r: Lp._ap.B['s' + p.sid], g: tileOf(Lp, p.sid)} : null),
  def: () => mlEl('scp', 'bank'), here: () => mlHere()});
mnode('scp.bank', 'scp', 'bank', {sizeOf: 'shire.bank', parse: k => bsk(k), name: p => `Scratchpad in bank ${p.bank}`, short: p => `Scratchpad ${p.bank}`, to: p => `the scratchpad in bank ${p.bank}`,
  patch: (p, P) => ({bank: p.bank, sub: p.sub, shire: homeOf(P)}), def: p => ({id: 'scp.panel', k: `${p.bank}.${p.sub}.${INST('scp').panel || 0}`}), here: () => mlHere()});
mnode('scp.panel', 'scp', 'panel', {sizeOf: 'shire.panel', parse: k => bsk(k), name: p => `Data panel ${p.panel} of sub-bank ${p.sub} (scratchpad)`, short: p => `Panel ${p.panel}`, to: p => `data panel ${p.panel}`,
  patch: (p, P) => ({bank: p.bank, sub: p.sub, panel: p.panel, shire: homeOf(P)}), def: () => ({id: 'lib.sram6t'}), here: () => mlHere()});
mnode('scp.vmin', 'scp', 'vmin', {sizeOf: 'shire.panel', name: () => 'The SRAM\'s lowest voltage (Vmin)', short: () => 'Vmin', to: () => 'the SRAM\'s lowest voltage', def: () => ({id: 'lib.sram6t'}), here: () => mlHere()});

/* ---- the shared chains (ladder-mem.js) drawn here with the levels' own builders: their view is the levels' (mlView); the
   6T cell and a mesh hop take the drawing of the level whose chain they are on (the L3's and the scratchpad's cells and
   hops are the levels' own variants) ---- */
// (a phone: another instance than the example's, another bank or memory shire, is the ladder's alone and fitted whole,
// as the levels' own scales above: review of 1 Oct)
const CHAINLV = {'l1d.block': ['l1', 'lram'], 'shire.bank': ['l2', 'bank'], 'shire.subbank': ['l2', 'sub'], 'shire.panel': ['l2', 'panel'], memshire: ['dram', 'ms'],
  dram: ['dram', 'chan'], 'dram.bank': ['dram', 'dbank'], 'memshire.phy': ['dram', 'phy'], 'memshire.phy.dq': ['dram', 'dq']};
['l1d', 'l1d.block', 'l1d.row', 'lib.latch', 'l1d.cmp', 'shire.bank', 'shire.subbank', 'shire.panel', 'lib.sram6t', 'shire.meshstop.xing', 'mesh', 'mesh.link.wire',
  'memshire', 'memshire.phy', 'memshire.phy.dq', 'dram', 'dram.bank', 'dram.cell'].forEach(id => {
  const N0 = NODES[id]; if (!N0) { console.error('memory levels: no scale ' + id); return; }
  const c = CHAINLV[id];
  N0.view = () => mlView(); N0.pv = (p, el) => (c && el && el.k != null && pk(el) !== pk(mlEl(c[0], c[1])) ? mlFit() : mlView()); N0.mlv = true;
  N0.here = () => mlHere();
});
const chainOf = P => (P.some(e => e.id === 'l3.home' || (e.id === 'die' && e.k === 'l3' && P.some(x => x.id === 'mesh'))) ? 'l3' : P.some(e => /^scp\./.test(e.id) || (e.id === 'die' && e.k === 'scp' && P.some(x => x.id === 'mesh'))) ? 'scp' : null);
{
  const N6 = NODES['lib.sram6t'], b6 = N6.build;
  N6.build = (L, ap, p, P, d) => {
    const c = chainOf(P.slice(0, d + 1));
    if (!c) { b6(L, ap, p, P, d); return; }
    ML.buildScene(L, ap, c, 'cell', {});
  };
  const NM = NODES.mesh, bm = NM.build;
  NM.build = (L, ap, p, P, d) => {
    const c = chainOf(P.slice(0, d + 1));
    if (!c) { bm(L, ap, p, P, d); return; }
    ML.buildScene(L, ap, c, 'hop', {});
    if (ap.repBox) { ap.zs['mesh.link.wire'] = {r: ap.repBox, g: ap.zg.rep || null}; if (ap.zg.rep) ap.zg.rep._kid = {id: 'mesh.link.wire'}; }
  };
  NM.seat = (ap, p, pel, Lp) => (pel.id === 'die' && Lp._ap.hopBox ? {r: Lp._ap.hopBox, g: Lp._ap.zg.hop || null} : null);
  const NW = NODES['mesh.link.wire'], bw = NW.build;
  NW.build = (L, ap, p, P, d) => {
    const c = chainOf(P.slice(0, d + 1));
    if (!c) { bw(L, ap, p, P, d); return; }
    ML.buildScene(L, ap, c, 'rep', {});
  };
}
/* the die's other seats on a levels' map: every compute shire's tile (its L2 drawing), the memory shires, the LPDDR4X
   packages (a channel), the master and spare shires, the I/O and PCIe cells (the chip's block scenes) */
function dieSeats(L, ap, p, P) {
  const B = ap.B || {};
  L.querySelectorAll('.comp').forEach(g => {
    const c = g._ctx || {};
    if (g._key === 'shire' && c.id != null && !g._kid) { const el = {id: 'shire', k: String(c.id)}; if (!ap.zs[pk(el)]) ap.zs[pk(el)] = {r: B['s' + c.id], g}; }
    if (g._key === 'memshire' && c.id != null && !g._kid) { const el = {id: 'memshire', k: String(c.id)}; if (!ap.zs[pk(el)]) ap.zs[pk(el)] = {r: B['m' + c.id], g}; }
    if (g._key === 'pkg' && c.ms) { const el = {id: 'dram', k: `${c.ms[0]}.${INST('dram').ch}`}; if (!ap.zs[pk(el)]) ap.zs[pk(el)] = {r: g._box, g}; }
    if (g._key === 'grey' && c.cell) {
      const nm = String(c.cell.name || ''), r = B[`g${c.cell.lx}_${c.cell.ly}`];
      const el = /master/.test(nm) ? {id: 'shire', k: c.cell.lx === 0 ? '32' : '33'} : /PCIe/.test(nm) ? (c.cell.ly === 4 ? {id: 'io'} : {id: 'pcie'}) : null;
      if (el && r && !ap.zs[pk(el)]) ap.zs[pk(el)] = {r, g};
    }
  });
  ap.zs['die.metal'] = ap.zs['die.metal'] || {r: {x: ML.mapGeom(p.lv).X0 + 2 * ML.mapGeom(p.lv).C, y: ML.mapGeom(p.lv).Y0 + 3.5 * ML.mapGeom(p.lv).C, w: ML.mapGeom(p.lv).C, h: ML.mapGeom(p.lv).C * MFR.h / MFR.w}, g: null, tr: 'jump'};
}
