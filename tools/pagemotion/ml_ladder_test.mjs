// ml_ladder_test.mjs PAGE [--phone] [--only=T3,T19] : the memory levels on the shared ladder (1 Oct 2026, part 2;
// /home/yaroslavvb/claude/work/ladder/DESIGN.md §5.4 for the memory levels, and the owner's updates of 1 Oct: the
// easter egg, a way back from every move, the loop through one atom, no dead end). PAGE is a local server's http://
// address (the lazily fetched facts need it). Each line PASS or FAIL; the exit code is the number of failures.
//   T0  the page loads with no error; the Up bar, the breadcrumb and the readout show the level's place as a path
//   T3  Up from the L1's minion goes out level by level (L1 → L2 → the map, each the levels' own move) and on to the package
//       (the ladder takes over), the rack and the "?" levels; the labels at the rack and below name no level above it
//   T5  + from the top of the ladder goes down through the package into the levels' map (their camera takes the stage),
//       down their default chain to a cell, on into the transistor, the fin, the channel, the crystal, an atom, a nucleus,
//       a proton, a quark and the Planck length, and round the ring to the top; every layer shown at rest within [1/30, 30]
//   T7  reduced motion: a move out of the levels' scenes and back is a cut; a link while the ladder holds the stage
//       brings the stage back to the link's level
//   T12 the ring's ways back in: each level's own cell (the DRAM's through the DRAM cell, never the N7 FinFET); Up from the
//       ring lands on the reader's level's atom, and its panel says so
//   T14 the easter egg: no level above the rack named in the Up bar, the crumbs or the menu at the rack or below; Up from
//       the rack still finds them
//   T15 the two-state electronics: G switches the gate on the transistor and the state holds into the channel
//   T17 the loop: Up from a cell passes the ring twice and lands on the same atom each time
//   T18 the navigation graph from the top and from the ring: every zoom has its seat, every glide its way back
//   T19 no dead ends: every part of every scene (the levels' own drawings included) leads in, but the keys beside the
//       maps and charts and the Planck length's ruler; every scene reaches a transistor and an atom; the DRAM's chains
//       never reach the N7 FinFET
//   T21 the hand-over: a crumb from the ladder back to a level's scene; a level's tab while the ladder holds the stage;
//       Play while the ladder holds the stage brings the camera back to the level and plays
//   T22 a part of the levels' own drawing with no scale of theirs: a double-click (a double-tap) opens the ladder's scale
//       for it, and its panel's zoom row names it
//   T13 consistency with the chip diagram (with --chip=URL, the chip diagram built from the same sources): at the same
//       places (the die, a shire, a minion, the L1's cache, an L2 bank and sub-bank, a memory shire, a mesh hop, the
//       vector unit, the L2's 6T cell) the breadcrumb up to the place and the Up button say the same on both pages, and so
//       does the panel's title below a level's top (at a level's top the memory levels show the level's own panel, and
//       below the place each page's breadcrumb goes on along its own default: the level's example on the memory levels)
//   T24 the panel after the ladder's moves: on the ladder's copy of a scene the levels draw, not at their place (another
//       bank, another shire), the scale's own panel; the arrow keys' glides between them
//   T23 the hand-over under quick input (the regression suites' fuzz run of 1 Oct): Up pressed while the levels' camera
//       moves, then a level's tab before it rests: the tab's level keeps the stage (the ladder's move waiting for the
//       levels' camera gives way); __memState().zooming stays true until a move of the ladder and its hand-over end
import { open, sleep } from './cdp.mjs';
const args = process.argv.slice(2), PAGE = args.find(a => !a.startsWith('--')), PHONE = args.includes('--phone');
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7).split(',').filter(Boolean);
const CHIP = (args.find(a => a.startsWith('--chip=')) || '').slice(7);
let fails = 0, passes = 0;
const ok = (c, what, extra) => { if (c) passes++; else fails++; console.log((c ? 'PASS ' : 'FAIL ') + what + (extra ? '  ' + String(extra).slice(0, 400) : '')); return c; };
const HIDDEN = ['Studio 45', 'San Francisco', 'Bernal', '29th', 'Bay Area', 'California', 'United States', 'US', 'Earth', 'Solar System', 'Milky Way', 'Local Group',
  'Laniakea', 'universe', 'Universe', 'Beyond', 'Ring of sizes', 'Andromeda', 'stars', 'Moon'];
const open1 = o => open(Object.assign(PHONE ? {w: 390, h: 844, touch: true} : {w: 1280, h: 800}, o || {}));
const S = b => b.ev('(() => { const s = __memState(), l = s.ladder; return {lv: s.lv, path: s.path.join("/"), on: l.on, lp: l.path, node: l.node, depth: l.depth, z: s.zooming || l.zooming, up: l.up, crumbs: l.crumbs, readout: l.readout, panel: l.panel, ston: l.ston, wrapin: l.wrapin, visible: l.visible, acc: s.acc, clock: s.clockOn}; })()');
async function rest(b, max = 12000) {
  const t0 = Date.now();
  while (Date.now() - t0 < max) { await sleep(60); const s = await S(b); if (!s.z) { await sleep(180); const t = await S(b); if (!t.z) return t; } }
  return S(b);
}
const up = async b => { await b.ev("document.getElementById('up').click()"); return rest(b); };
const plus = async b => { await b.ev("document.querySelector('#pmz [data-ci=plus]').click()"); return rest(b); };
const T = {};

T.T0 = async () => {
  const b = await open1(); await b.load(PAGE, '', 3000);
  const s = await rest(b);
  ok(s.lv === 'l1' && !s.on, 'T0 the page starts at the L1, the levels\' camera holding the stage', `${s.lv} ${s.on}`);
  ok(/Zoom out to shire 0/.test(s.up), 'T0 the Up button names the scale outside (the L2\'s shire)', s.up);
  // (a phone's narrower bar folds the outer crumbs into "…" sooner)
  ok((s.crumbs.includes('Chip') || (PHONE && s.crumbs.includes('…'))) && s.crumbs.includes('Shire 0') && s.crumbs.includes('Minion 0'), 'T0 the breadcrumb names the place as a path (… › Chip › Shire 0 › Minion 0)', s.crumbs.join(' › '));
  ok(/µm|mm/.test(s.readout), 'T0 the readout gives the scale\'s size', s.readout);
  ok(!b.errs.length, 'T0 no error at load', b.errs.join(' | '));
  await b.close();
};

T.T3 = async () => {
  const b = await open1(); await b.load(PAGE, '#l1', 3000); await rest(b);
  const seq = [];
  for (let i = 0; i < 8; i++) { const s = await up(b); seq.push(s); }
  ok(seq[0].lv === 'l2' && !seq[0].on && seq[0].node === 'shire', 'T3 Up from the L1\'s minion: the L2\'s shire (the levels\' own move, the L2 tab)', `${seq[0].lv} ${seq[0].node}`);
  ok(seq[1].lv === 'l3' && !seq[1].on && seq[1].node === 'die', 'T3 Up again: the chip level\'s map (the L3, the last visited)', `${seq[1].lv} ${seq[1].node}`);
  ok(seq[2].on && seq[2].node === 'package', 'T3 Up from the map: the package (the ladder takes the stage)', seq[2].node);
  ok(seq.slice(3, 5).map(s => s.node).join(',') === 'card,host', 'T3 then the card and the host', seq.slice(3, 5).map(s => s.node).join(','));
  ok(seq[5].node === 'rack' && seq[5].up === '↑ ?', 'T3 at the rack the Up button says only "?"', `${seq[5].node} ${seq[5].up}`);
  ok(seq[6].node === 'studio45', 'T3 Up from the rack still finds the level above it', seq[6].node);
  ok(!b.errs.length, 'T3 no error', b.errs.join(' | '));
  await b.close();
};

T.T5 = async () => {
  const b = await open1(); await b.load(PAGE, '?at=beyond', 3000); await rest(b);
  const seen = []; let bad = [], handed = false, back = false;
  for (let i = 0; i < 60; i++) {
    const s = await plus(b); seen.push(s.node);
    if (!s.on && s.node === 'die') handed = true;
    if (handed && s.on && /^lib\./.test(s.node)) back = true;
    (s.visible || []).forEach(v => { if (v.k < 1 / 30 || v.k > 30) bad.push(`${s.node}:${v.node}:${v.k}`); });
    if (s.node === 'beyond' && i > 5) break;
  }
  const want = ['package', 'die', 'lib.finfet', 'lib.fin', 'lib.channel', 'lib.si', 'p.atom', 'p.nucleus', 'p.nucleon', 'p.quark', 'p.planck', 'p.wrap', 'beyond'];
  const order = want.map(w => seen.indexOf(w));
  ok(order.every((x, i) => x >= 0 && (!i || x > order[i - 1])), 'T5 + from the top: the package, the map, a cell, the transistor, the fin, the channel, the crystal, an atom, its nucleus, a proton, a quark, the Planck length, the ring, the top', seen.join(' '));
  ok(handed, 'T5 at the map the levels\' camera takes the stage (their own scenes, their own moves)');
  ok(back, 'T5 below their cell the ladder takes it again (the transistor and below)');
  ok(!bad.length, 'T5 every layer shown at rest within [1/30, 30]', bad.slice(0, 6).join(' '));
  ok(!b.errs.length, 'T5 no error', b.errs.join(' | '));
  await b.close();
};

T.T7 = async () => {
  const b = await open1({reduced: true}); await b.load(PAGE, '#l3', 3000); await rest(b);
  await b.ev("document.getElementById('up').click()"); await sleep(120);
  const s = await S(b);
  ok(s.on && s.node === 'package' && !s.z, 'T7 reduced motion: Up from the map is a cut to the package', `${s.node} ${s.z}`);
  await b.ev("document.querySelector('#pmz [data-ci=plus]').click()"); await sleep(400);
  const t = await S(b);
  ok(!t.on && t.node === 'die', 'T7 and + back into the map is a cut, the levels\' camera holding the stage', `${t.node} ${t.on}`);
  // a link while the ladder holds the stage (under reduced motion a link is drawn at once): the stage comes back to the
  // link's level (it stayed with the ladder before 1 Oct evening)
  await b.ev("document.getElementById('up').click()"); await sleep(300);
  await b.ev("location.hash = '#dram'"); await sleep(600);
  const u = await rest(b);
  ok(!u.on && u.lv === 'dram' && u.path === 'chip', 'T7 a link (#dram) from the package: the DRAM\'s map, the levels\' camera holding the stage', `${u.on} ${u.lv} ${u.path}`);
  ok(!b.errs.length, 'T7 no error', b.errs.join(' | '));
  await b.close();
};

T.T12 = async () => {
  const b = await open1(); await b.load(PAGE, '#dram', 3000); await rest(b);
  const ex = await b.ev('MLH.test.exits()');
  ok(ex.length >= 1 && /dram\.cell\/lib\.dramcell/.test(ex[0].path) && !/lib\.finfet/.test(ex[0].path), 'T12 the DRAM\'s way in from the ring: its cell, the DRAM process\'s transistor, never N7\'s FinFET', ex[0] && ex[0].path.split('/').slice(-5).join('/'));
  for (const lv of ['l1', 'l2', 'l3', 'scp']) {
    await b.ev(`document.getElementById('tab-${lv}').click()`); await rest(b);
    const e = await b.ev('MLH.test.exits()');
    const want = {l1: /lib\.latch\/lib\.inverter\/lib\.finfet/, l2: /lib\.sram6t\/lib\.finfet/, l3: /l3\.panel:[\d.]+\/lib\.sram6t\/lib\.finfet/, scp: /scp\.panel:[\d.]+\/lib\.sram6t\/lib\.finfet/}[lv];
    ok(want.test(e[0].path) && /p\.atom$/.test(e[0].path), `T12 the ${lv.toUpperCase()}'s way in: its own cell, down to an atom`, e[0].path.split('/').slice(-6).join('/'));
  }
  // round the ring from the L2: Up from the ring lands on that atom, and the panel says the reader came round
  await b.ev("document.getElementById('tab-l2').click()"); await rest(b);
  await b.ev("MLH.test.go('p.wrap')"); await rest(b);
  const r = await S(b);
  ok(r.node === 'p.wrap' && /round the ring/i.test(r.up), 'T12 the ring: Up goes round it', r.up);
  const a = await up(b);
  ok(a.node === 'p.atom' && /lib\.sram6t/.test(a.lp) && a.wrapin, 'T12 Up from the ring lands on an atom of the L2\'s cell, marked as come round', a.lp.split('/').slice(-5).join('/'));
  ok(!b.errs.length, 'T12 no error', b.errs.join(' | '));
  await b.close();
};

T.T14 = async () => {
  const b = await open1(); await b.load(PAGE, '?at=rack', 3000); await rest(b);
  const s = await S(b);
  const txt = [s.up, ...s.crumbs].join(' | ');
  const hits = HIDDEN.filter(h => new RegExp('\\b' + h + '\\b').test(txt));
  ok(!hits.length && s.up === '↑ ?', 'T14 at the rack: the Up button and the crumbs name no level above it', txt);
  await b.ev("(() => { const m = document.querySelector('#crumbs .more'); if (m) m.click(); })()"); await sleep(200);
  const menu = await b.ev("document.getElementById('crumb-menu').textContent");
  ok(!HIDDEN.some(h => new RegExp('\\b' + h + '\\b').test(menu)), 'T14 the "…" menu names none either', menu.slice(0, 200));
  for (const q of ['#l1', '#l3', '#dram', '#l2/cell']) {
    const b2 = await open1(); await b2.load(PAGE, q, 2500); const t = await rest(b2);
    const tx = [t.up, ...t.crumbs].join(' | '), h2 = HIDDEN.filter(h => new RegExp('\\b' + h + '\\b').test(tx));
    ok(!h2.length, `T14 ${q}: the Up bar names no level above the rack`, tx);
    await b2.close();
  }
  const u = await up(b);
  ok(u.node === 'studio45', 'T14 Up from the rack still reaches the level above it', u.node);
  ok(!b.errs.length, 'T14 no error', b.errs.join(' | '));
  await b.close();
};

T.T15 = async () => {
  const b = await open1(); await b.load(PAGE, '#l2/cell', 3000); await rest(b);
  const s0 = await plus(b);
  ok(s0.node === 'lib.finfet' && !s0.ston, 'T15 + from the 6T cell: the transistor, its gate at 0 V', `${s0.node} ${s0.ston}`);
  await b.key('g'); await sleep(400);
  const s1 = await S(b);
  ok(s1.ston, 'T15 G switches the gate on');
  const s2 = await plus(b); const s3 = await plus(b);
  ok(s3.node === 'lib.channel' && s3.ston, 'T15 the state holds from the transistor to the channel', `${s3.node} ${s3.ston}`);
  ok(!b.errs.length, 'T15 no error', b.errs.join(' | '));
  await b.close();
};

T.T17 = async () => {
  const b = await open1(); await b.load(PAGE, '#l3/cell', 3000); await rest(b);
  const atoms = []; let n = 0, laps = [], last = 0;
  for (let i = 0; i < 80 && atoms.length < 2; i++) {
    const s = await up(b); n++;
    if (s.node === 'p.atom') { atoms.push(s.lp); laps.push(n - last); last = n; }
  }
  ok(atoms.length === 2, 'T17 Up from the L3\'s cell passes the ring twice', `${atoms.length} in ${n} presses`);
  ok(atoms.length === 2 && atoms[0] === atoms[1], 'T17 and lands on the same atom each time', atoms.map(a => a.split('/').slice(-4).join('/')).join(' | '));
  ok(laps.length === 2 && laps[1] >= 25 && laps[1] <= 40, 'T17 one lap is a few dozen presses', laps.join(', '));
  ok(!b.errs.length, 'T17 no error', b.errs.join(' | '));
  await b.close();
};

T.T18 = async () => {
  const b = await open1(); await b.load(PAGE, '', 3000); await rest(b);
  const G = await b.ev('MLH.test.graph()');
  const errs = G.filter(g => g.err), noseat = [], oneway = [];
  G.forEach(g => {
    (g.parts || []).forEach(p => { if ((p.kid || p.go) && !p.seat) noseat.push(`${g.path.split('/').slice(-1)[0]}:${p.key}`); });
    (g.kids || []).forEach(k => { if (!k.seat) noseat.push(`${g.path.split('/').slice(-1)[0]}+${k.kid}`); });
    Object.entries(g.side || {}).forEach(([d, x]) => { if (x.to && !x.back) oneway.push(`${g.path.split('/').slice(-1)[0]} ${d} ${x.to}`); });
  });
  ok(G.length > 60, 'T18 the graph from the top and from the ring reaches the scales', G.length);
  ok(!errs.length, 'T18 every scale reached is drawn', errs.slice(0, 4).map(g => g.path + ' ' + g.err).join(' | '));
  ok(!noseat.length, 'T18 every zoom has its seat in the drawing it starts from', noseat.slice(0, 8).join(' '));
  ok(!oneway.length, 'T18 every glide between siblings has its way back', oneway.slice(0, 8).join(' | '));
  ok(G.every(g => g.up || g.path === 'beyond' || g.path === 'p.wrap' || /p\.wrap/.test(g.path)), 'T18 every scale has its way out (Up)');
  ok(!b.errs.length, 'T18 no error', b.errs.join(' | '));
  await b.close();
};

T.T19 = async () => {
  const b = await open1(); await b.load(PAGE, '', 3000); await rest(b);
  const W = await b.ev('MLH.test.walk()');
  const dead = [], nxt = {};
  W.forEach(s => {
    nxt[s.id] = nxt[s.id] || new Set();
    if (s.err) dead.push(s.path + ' ERR ' + s.err);
    (s.parts || []).forEach(p => {
      if (p.to && p.seat) nxt[s.id].add(p.to);
      if (!p.to && !p.up && !p.ext && s.id !== 'p.planck') dead.push(`${s.id}:${p.key}`);
      if (p.to && !p.seat) dead.push(`${s.id}:${p.key}->${p.to} (no seat)`);
    });
    (s.kids || []).forEach(k => { if (k.seat) nxt[s.id].add(k.to); });
  });
  ok(W.length > 200, 'T19 the walk from every level\'s scenes and from the rack', `${W.length} scenes`);
  ok(!dead.length, 'T19 every part leads in (but the keys beside the maps and charts, and the Planck length\'s ruler)', dead.slice(0, 10).join(' '));
  const reach = (a, avoid) => { const seen = new Set([a]), st = [a]; while (st.length) { const x = st.pop(); (nxt[x] || []).forEach(y => { if (!seen.has(y) && !(avoid && avoid.has(y))) { seen.add(y); st.push(y); } }); } return seen; };
  const TR = ['lib.finfet', 'lib.dramcell', 'lib.powerfet'], FLOOR = /^(p\.|lib\.(si|channel|fin)$)/;
  const bad = Object.keys(nxt).filter(i => !FLOOR.test(i) && !(W.find(s => s.id === i) || {}).egg).filter(i => { const r = reach(i); return !(TR.includes(i) || TR.some(t => r.has(t))) || !TR.some(t => (t === i || r.has(t)) && reach(t).has('p.atom')); });
  ok(!bad.length, 'T19 every scene reaches a transistor and then an atom', bad.join(' '));
  const dr = Object.keys(nxt).filter(i => /^dram/.test(i) || i === 'lib.dramcell').filter(i => reach(i, new Set(['lib.si', 'p.atom'])).has('lib.finfet'));
  ok(!dr.length, 'T19 the DRAM\'s chains never reach the N7 FinFET', dr.join(' '));
  const ids = new Set(W.map(s => s.id)), want = ['die', 'shire', 'minion', 'l1d', 'l1d.block', 'l1d.row', 'lib.latch', 'l1d.cmp', 'shire.bank', 'shire.subbank', 'shire.panel', 'lib.sram6t', 'shire.meshstop.xing',
    'l3.home', 'l3.bank', 'l3.subbank', 'l3.panel', 'mesh', 'mesh.link.wire', 'scp.shire', 'scp.bank', 'scp.panel', 'scp.vmin', 'memshire', 'dram', 'dram.bank', 'dram.cell', 'memshire.phy', 'memshire.phy.dq'];
  ok(want.every(i => ids.has(i)), 'T19 the walk covers every scene of the five levels', want.filter(i => !ids.has(i)).join(' '));
  ok(!b.errs.length, 'T19 no error', b.errs.join(' | '));
  await b.close();
};

T.T21 = async () => {
  const b = await open1(); await b.load(PAGE, '#l2/cell', 3000); await rest(b);
  await plus(b); await plus(b);
  const s0 = await S(b);
  ok(s0.on && s0.node === 'lib.fin', 'T21 + twice from the 6T cell: the fin (the ladder holds the stage)', s0.node);
  // a crumb back to a level's scene: the data panel (on a phone, from the "…" menu if its crumb is folded); then the
  // "…" menu's bank
  const crumbTo = async (re, menuRe) => b.ev(`(() => { const bt = [...document.querySelectorAll('#crumbs button')].find(x => ${re}.test(x.textContent));
    if (bt) { bt.click(); return 'crumb'; } const m = document.querySelector('#crumbs .more'); if (!m) return null; m.click();
    const it = [...document.querySelectorAll('#crumb-menu button')].find(x => ${menuRe}.test(x.textContent)); if (it) { it.click(); return 'menu'; } return null; })()`);
  const how = await crumbTo('/^Panel/', '/^Data panel 0/');
  const s1 = await rest(b);
  ok(!!how && !s1.on && s1.lv === 'l2' && s1.path === 'shire/bank/sub/panel', `T21 the ${how} "Panel 0" from the fin: back to the L2's data panel, the levels' camera holding the stage`, `${how} ${s1.on} ${s1.lv} ${s1.path}`);
  await plus(b); await plus(b); await plus(b);
  await b.ev(`(() => { const m = document.querySelector('#crumbs .more'); if (m) m.click(); })()`); await sleep(250);
  const hasBank = await b.ev(`(() => { const it = [...document.querySelectorAll('#crumb-menu button')].find(x => /^Cache bank 1/.test(x.textContent)); if (it) it.click(); return !!it; })()`);
  const s1b = await rest(b);
  ok(hasBank && !s1b.on && s1b.lv === 'l2' && s1b.path === 'shire/bank', 'T21 the "…" menu\'s "Cache bank 1" from below the cell: back to the L2\'s bank', `${hasBank} ${s1b.on} ${s1b.path}`);
  // a level's tab while the ladder holds the stage
  await b.ev("document.getElementById('up').click()"); await rest(b);
  await b.ev("MLH.test.go('package')"); const s2 = await rest(b);
  ok(s2.on && s2.node === 'package', 'T21 the package (the ladder holds the stage)', s2.node);
  await b.ev("document.getElementById('tab-dram').click()"); const s3 = await rest(b, 15000);
  ok(!s3.on && s3.lv === 'dram' && s3.path === 'chip', 'T21 the DRAM tab from the package: the DRAM\'s map', `${s3.on} ${s3.lv} ${s3.path}`);
  // Play while the ladder holds the stage: the camera comes back to the level, and the access plays
  await b.ev("MLH.test.go('package')"); await rest(b);
  await b.ev("document.getElementById('btn-play').click()"); await sleep(400); const s4 = await rest(b, 15000); await sleep(1500);
  const s5 = await S(b);
  ok(!s5.on && s5.lv === 'dram' && !!s5.acc, 'T21 Play from the package: back to the DRAM, its access playing', `${s5.on} ${s5.lv} ${s5.acc}`);
  ok(!b.errs.length, 'T21 no error', b.errs.join(' | '));
  await b.close();
};

T.T22 = async () => {
  const cases = [['#l2', 'reqxbar', 'lib.xbar'], ['#l2', 'uc', 'shire.uc'], ['#l1', 'tlb', 'lib.regfile'], ['#l3/home', 'tol3m', 'lib.fifo'], ['#scp/vmin', 'rm', 'lib.sram6t'], ['#dram', 'memshire', 'memshire']];
  for (const [q, key, want] of cases) {
    const b = await open1(); await b.load(PAGE, q, 3000); await rest(b);
    const box = await b.ev(`(() => { const L = [...document.querySelectorAll('#mem > g.lay')].filter(l => l.style.display !== 'none' && l.style.visibility !== 'hidden').pop();
      const g = [...L.querySelectorAll('.comp[data-comp="${key}"]')].filter(x => x.getClientRects().length && !x.getAttribute('data-child'))[0]; if (!g) return null; g.scrollIntoView({block: 'nearest', inline: 'nearest'});
      const r = g.getBoundingClientRect(); return {x: r.x + Math.min(r.width / 2, 24), y: r.y + Math.min(r.height / 2, 16)}; })()`);
    if (!ok(!!box, `T22 ${q}: a ${key} part to ${PHONE ? 'tap' : 'click'}`)) { await b.close(); continue; }
    if (PHONE) await b.tap(box.x, box.y); else await b.click(box.x, box.y);
    await sleep(300);
    const zr = await b.ev("(() => { const z = document.querySelector('#pn-body .pn-zoom'); return z ? z.textContent : ''; })()");
    ok(/Zoom in/.test(zr), `T22 ${q} ${key}: a ${PHONE ? 'tap' : 'click'} selects it, its panel's zoom row says where it leads`, zr.slice(0, 80));
    await sleep(700);   // (a reader's double-tap comes after reading, not within 400 ms of the tap that selected)
    if (PHONE) await b.dtap(box.x, box.y); else await b.dblclick(box.x, box.y);
    const s = await rest(b);
    ok(s.on && s.node === want, `T22 ${q} ${key}: a double-${PHONE ? 'tap' : 'click'} opens ${want}`, `${s.on} ${s.node}`);
    ok(!b.errs.length, `T22 ${q} no error`, b.errs.join(' | '));
    await b.close();
  }
};

T.T23 = async () => {
  const b = await open1(); await b.load(PAGE, '#l1', 3000); await rest(b);
  // the L3's tab (the levels' camera moves out of the L1), Up while it moves (a move of the ladder, which waits for the
  // levels' camera to rest), then the L2's tab: the L2 keeps the stage
  await b.ev("document.getElementById('tab-l3').click()"); await sleep(150);
  await b.ev("document.getElementById('up').click()"); await sleep(200);
  await b.ev("document.getElementById('tab-l2').click()");
  const s1 = await rest(b, 15000); await sleep(600); const s1b = await S(b);
  ok(!s1b.on && s1b.lv === 'l2' && s1b.path === 'shire', 'T23 tab, Up and another tab within 0.4 s: the last tab\'s level holds the stage', `${s1b.on} ${s1b.lv} ${s1b.path} ${s1b.node}`);
  // from the package (the ladder holding the stage) the L3's tab: the ladder's camera goes in to the L3's map and hands
  // the stage over; until it has, the page says it is moving
  await b.ev("MLH.test.go('package')"); await rest(b);
  await b.ev("document.getElementById('tab-l3').click()");
  const t0 = Date.now(); let first = null, n = 0;
  while (Date.now() - t0 < 15000) {
    const r = await b.ev('(() => { const s = __memState(); return {z: s.zooming, on: MLH.on(), lv: s.lv, dlv: s.dlv, path: s.path.join("/")}; })()'); n++;
    if (!r.z) { first = r; break; }
    await sleep(25);
  }
  ok(!!first && !first.on && first.lv === 'l3' && first.dlv === 'l3' && first.path === 'chip' && n > 3, 'T23 the L3\'s tab from the package: zooming until the L3\'s map holds the stage, at rest', JSON.stringify(first) + ' polls ' + n);
  ok(!b.errs.length, 'T23 no error', b.errs.join(' | '));
  await b.close();
};

T.T13 = async () => {
  if (!CHIP) { console.log('(T13 skipped: no --chip=URL)'); return; }
  const places = [['die', false], ['die/shire:0', false], ['die/shire:0/minion:0.0.0', false], ['die/shire:0/minion:0.0.0/l1d', true],
    ['die/shire:0/shire.bank:0', true], ['die/shire:0/shire.bank:0/shire.subbank:0.0', true], ['die/memshire:0', true], ['die/mesh', true],
    ['die/shire:0/minion:0.0.0/vpu', true], ['die/shire:0/shire.bank:1/shire.subbank:1.3/shire.panel:1.3.0/lib.sram6t', true]];
  const c = await open1(), m = await open1();
  await m.load(PAGE, '#l3', 3000); await rest(m);
  // (the breadcrumb up to the place shown, aria-current; after it each page's own default way in: on the memory levels
  // the level's example, the memory path, on the chip the compute default)
  const rd = b => b.ev(`(() => { const bs = [...document.querySelectorAll('#crumbs button')], i = bs.findIndex(x => x.getAttribute('aria-current') === 'location');
    return {crumbs: bs.slice(0, i + 1).map(x => x.textContent).join(' › '), up: document.getElementById('up').textContent, title: (document.querySelector('#pn-body .pn-title') || {}).textContent || ''}; })()`);
  for (const [p, title] of places) {
    await c.load(CHIP, '?at=' + encodeURIComponent(p), 2800);
    const a = await rd(c);
    const ok0 = await m.ev(`MLH.test.go(${JSON.stringify(p)}) !== null`);
    await rest(m, 15000); await sleep(300);
    const z = await rd(m);
    // (a phone folds the outer crumbs into "…" as the row's width allows: the memory levels' Up bar also holds Fit, so
    // it may show a crumb fewer; the names are compared where both show them, at least the place itself, and the Up
    // button names its parent)
    const strip = t => t.split(' › ').filter(x => x !== '…'), A = strip(a.crumbs), B = strip(z.crumbs), n = Math.min(A.length, B.length);
    const same = n >= 1 && (PHONE ? A.slice(-n).join(' › ') === B.slice(-n).join(' › ') : a.crumbs === z.crumbs);
    ok(ok0 && same && a.up === z.up && (!title || a.title === z.title),
      `T13 ${p.split('/').slice(-1)[0]}: the breadcrumb and the Up button${title ? ', and the panel\'s title,' : ''} as on the chip diagram`,
      `${a.crumbs} | ${z.crumbs} || ${a.up} | ${z.up}${title ? ` || ${a.title} | ${z.title}` : ''}`);
  }
  ok(!c.errs.length && !m.errs.length, 'T13 no error', c.errs.concat(m.errs).join(' | '));
  await c.close(); await m.close();
};

T.T24 = async () => {
  const b = await open1(); await b.load(PAGE, '#l1', 3000); await rest(b);
  const here = async what => { const s = await rest(b); const nm = await b.ev('MLH.test.name()'); return {s, nm, what}; };
  const chk = (r, wantOn, label) => ok(r.s.on === wantOn && r.s.panel === r.nm, `T24 ${label}: ${wantOn ? 'the ladder holds the stage' : 'the levels hold the stage'}, the panel's title is the scale's name`, `on=${r.s.on} panel="${r.s.panel}" name="${r.nm}" at ${r.s.lp.split('/').slice(-2).join('/')}`);
  await b.ev("MLH.test.go('die/shire:0/minion:0.0.0/l1d')"); chk(await here(), false, 'the L1\'s cache');
  await b.ev("MLH.test.go('die/shire:0/shire.bank:0')"); chk(await here(), true, 'from the L1\'s cache to bank 0 of the L2 (not the example\'s bank)');
  await b.ev("MLH.test.go('die/shire:1')"); chk(await here(), true, 'shire 1 (not the requester)');
  // a glide by the arrow keys from shire 1 (an edge link): the panel follows
  await b.ev('document.activeElement && document.activeElement.blur && document.activeElement.blur()');
  await b.key('ArrowRight'); const g = await here();
  ok(g.s.lp !== 'x' && /shire:\d+$/.test(g.s.lp) && !/shire:1$/.test(g.s.lp), 'T24 ArrowRight from shire 1 glides to its neighbour', g.s.lp.split('/').slice(-1)[0]);
  ok(g.s.panel === g.nm, 'T24 and the panel names the neighbour', `panel="${g.s.panel}" name="${g.nm}" on=${g.s.on}`);
  ok(!b.errs.length, 'T24 no error', b.errs.join(' | '));
  await b.close();
};

for (const k of Object.keys(T)) {
  if (ONLY.length && !ONLY.includes(k)) continue;
  try { await T[k](); } catch (e) { ok(false, `${k} ran`, String(e).slice(0, 300)); }
}
console.log(`${passes} passed, ${fails} failed`);
process.exit(fails);
