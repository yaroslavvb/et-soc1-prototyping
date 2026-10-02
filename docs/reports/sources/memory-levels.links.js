/* ================= memory-levels.links.js: where every part of the memory levels' own drawings leads (1 October 2026) =================
   Part of memory-levels.ladder.js's scope (after ladder-circuits.js, whose links() it uses). The owner's second update
   of 1 Oct: "make sure in all the places I eventually go all the way down to the lowest transistor level and then I go
   down to the atoms": a part of the levels' drawings with a scale of its own in their chain opens it (their own
   camera); every other part opens a scale of the ladder, as the same part does on the chip diagram (the textbook
   constructions of ladder-circuits.js where the chip's own circuit is not published, the chip's block scenes where it
   has one), and through it a transistor and its atoms. A box of numbers or a note beside a drawing, not a part of the
   chip, is a key (false: its panel says there is nothing inside it). The same table serves the levels' own camera
   (kidOfML reads the ladder's copy of the scene). A rail's band opens the wiring stack that carries it. */
/* the scales inside the levels' places, by default (+) and in the panel's "Zoom into" row */
NODES.minion.def = () => ({id: 'l1d'});
NODES.minion.kids = () => [{id: 'l1d'}, {id: 'core'}, {id: 'vpu'}, {id: 'tensor'}];
NODES.shire.def = () => mlEl('l2', 'bank');
NODES.shire.kids = p => [mlEl('l2', 'bank'), {id: 'shire.meshstop.xing'}, {id: 'lib.xbar'}, {id: 'shire.uc'}, {id: 'minion', k: `${p.sid}.0.0`}];
NODES.die.kids = p => ({l3: [mlEl('l3', 'home', 'l3'), {id: 'mesh'}], scp: [mlEl('scp', 'shire', 'scp'), {id: 'mesh'}], dram: [mlEl('dram', 'ms', 'dram')]}[p.lv] || [])
  .concat([{id: 'shire', k: String(REQ(p.lv))}, {id: 'pcie'}, {id: 'io'}, {id: 'die.metal'}]);
/* the package opens the chip as the map of the chip level last visited */
NODES.package.def = () => ({id: 'die', k: chipV()});
NODES.package.kids = () => [{id: 'die', k: chipV()}];
const keys = list => Object.fromEntries(list.map(k => [k, false]));
const RAIL = 'die.metal';
/* the levels' maps: a tile opens its shire (the L2's drawing; the requester's is the L2 level itself, the home's the
   L3's), a memory shire its own drawing, a package a channel, the cells without a compute shire the chip's scenes, the
   memory PLLs the textbook PLL, the memory shires' rail its wiring; the charts and boxes of numbers beside a map are keys */
links('die', Object.assign({
  shire: c => (c.id != null ? {id: 'shire', k: String(c.id)} : null),
  memshire: c => (c.id != null ? {id: 'memshire', k: String(c.id)} : null),
  pkg: c => (c.ms ? {id: 'dram', k: `${c.ms[0]}.${INST('dram').ch}`} : null),
  grey: c => { const nm = String((c.cell || {}).name || ''); return /master/.test(nm) ? {id: 'shire', k: (c.cell || {}).lx === 0 ? '32' : '33'} : /PCIe/.test(nm) ? ((c.cell || {}).ly === 4 ? {id: 'io'} : {id: 'pcie'}) : null; },
  pll: 'lib.pll', vddr: RAIL,
}, keys(['homebox', 'fit', 'mean', 'byhome', 'fmt', 'own', 'remote', 'size', 'fmt1', 'relay', 'model', 'typical', 'rate', 'energy', 'addrmap'])));
/* the L2's shire: a neighbourhood opens its first minion (the requester's neighbourhood 0 is the L1 level itself), the
   crossbars the textbook crossbar, the UC its block, the mesh stop the crossing into the mesh, the row partition the
   6T cell its rows are made of */
links('shire', {
  nbr: (c, g, P) => ({id: 'minion', k: `${P[P.length - 1].k}.${c.i || 0}.0`}),
  reqxbar: 'lib.xbar', rspxbar: 'lib.xbar', uc: 'shire.uc', meshstop: 'shire.meshstop.xing', partition: 'lib.sram6t',
  fifo: 'shire.meshstop.xing', lvband: RAIL, rail: RAIL,
});
/* the L1's minion: the pipeline is the minion core's, the TLB a small CAM (a register file), the miss handlers and the
   replay queue flip-flops and a queue, the VPU the vector unit, the TensorLoad unit the tensor unit, the ports and the
   neighbourhood the crossing out of the minion's low-voltage plane */
links('minion', {pipeline: 'core', tlb: 'lib.regfile', mh: 'lib.flipflop', rq: 'lib.fifo', vpu: 'vpu', tl: 'tensor', ports: 'shire.meshstop.xing', nbr: 'shire.meshstop.xing', rail: RAIL});
/* the L3's home shire: its banks' L3 slices, the to_l3 and to_sys masters (queues), the mesh stop and the L3-slave ports
   (crossings), the crossbar, the UC, its neighbourhoods' first minions; the floorplan is unknown (a key) */
const homeK = P => { const e = P.find(x => x.id === 'l3.home' || x.id === 'scp.shire'); return e ? e.k : '0'; };
links('l3.home', Object.assign({
  rail: RAIL, tol3m: 'lib.fifo', stop: 'shire.meshstop.xing', tosys: 'lib.fifo', ports: 'shire.meshstop.xing', xbar: 'lib.xbar', uc: 'shire.uc',
  banks: c => ({id: 'l3.bank', k: String(c.inst && c.inst.bank != null ? c.inst.bank : c.i || 0)}),
  nbr: (c, g, P) => ({id: 'minion', k: `${homeK(P)}.${c.i || 0}.0`}), slice: 'lib.sram6t',
}, keys(['floor'])));
/* a bank's L3 slice, its sub-bank and a data panel: as the L2's (the same macros), and the L3's own queues */
links('l3.bank', Object.assign({}, LINKS['shire.bank'], {l3fifo: 'lib.fifo', tosys: 'lib.fifo', partial: 'lib.logic'}));
links('l3.subbank', Object.assign({}, LINKS['shire.subbank']));
links('l3.panel', Object.assign({}, LINKS['shire.panel']));
/* the scratchpad's shire: as the L2's shire; the L1 scratchpad is the L1's latch RAM; the note on what caps a stream is a key */
links('scp.shire', Object.assign({
  nbr: (c, g, P) => ({id: 'minion', k: `${homeK(P)}.${c.i || 0}.0`}), fifo: 'shire.meshstop.xing', l1scp: 'l1d',
  reqxbar: 'lib.xbar', rspxbar: 'lib.xbar', uc: 'shire.uc', partition: 'lib.sram6t', meshstop: 'shire.meshstop.xing', lvband: RAIL, rail: RAIL,
}, keys(['bneck'])));
links('scp.bank', Object.assign({}, LINKS['shire.bank'], {
  subbanks: (c, g, P) => { const e = P[P.length - 1], b = String(e.k || '0').split('.')[0]; return {id: 'scp.panel', k: `${b}.${c.i || 0}.0`}; },
}, keys(['rules'])));
links('scp.panel', Object.assign({}, LINKS['shire.panel']));
/* the Vmin inset: a chart of the SRAM's trims and the rails; a trim row opens the cell it trims, a rail its wiring */
links('scp.vmin', Object.assign({rm: 'lib.sram6t', railSram: RAIL, railMin: RAIL, railMesh: RAIL, rail750: RAIL}, keys(['axis', 'railRange', 'why'])));
/* the 6T cell and the latch are the levels' own scenes here (their camera shows them, with their accesses' animations):
   the ladder's copy of them, which the hand-over shows for a moment, is drawn as theirs, without the chip diagram's
   stored-bit box and its switch (ladder-inner.js's bitStates); the two states are the transistor's, its fin's and its
   channel's below */
['lib.sram6t', 'lib.latch'].forEach(id => {
  const N0 = NODES[id], b0 = N0.build;
  N0.build = (L, ap, p, P, d) => { b0(L, ap, p, P, d); L.querySelectorAll('.bitst, .stsw').forEach(e => e.remove()); L._states = null; };
});
