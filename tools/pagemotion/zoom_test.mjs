// node zoom_test.mjs PAGE [--phone] [--only=T1,T4] [--scenes=a,b] : the chip diagram's zoom and navigation tests
// (DESIGN §6.2), driven with real input events over the DevTools protocol (cdp.mjs). Desktop 1280 x 800 with a mouse;
// --phone: 390 x 844, touch emulation, DPR 3. Each test prints PASS or FAIL lines; the exit code is the number of
// failures. The page's hooks: window.__chipState() (where the camera is) and window.__chipTest (the parts of the scale
// shown and what each zooms into, the stage a flow wants shown).
//   T1 every part: a double-click (double-tap) on one part of each kind, in each scene, enters its own scale (or, for
//      a part with none, selects it and shows the panel's zoom row); then the Up button comes back
//   T2 a click (tap) selects and never moves the camera; on touch the pill shows
//   T3 Up from the deepest default scale (since 1 Oct the Planck length) to the top, one level a press; then round the
//      ring of sizes (the wrap) and in again as an atom of the multiply-add (the owner's second update, 1 Oct 09:00);
//      Up from it to the die; the breadcrumb back down; the "…" menu
//   T4 a shire's edge links, by click (tap), Enter and the arrow keys; a glide between shires; since the owner's second
//      update, the memory, PCIe and I/O shires' links too, each with its link back (T4b)
//   T5 the dive: + from the top of the ladder to the bottom of the default chain (the Planck length), every step
//      arriving, the readout monotone, every visible layer's scale within [1/30, 30]; then + round the ring back to the
//      top; then one breadcrumb click back to the chip
//   T6 the flows: every stage of every flow lands where it wants the camera
//   T7 reduced motion: a zoom is a cut
//   T11 accessibility: every part's label says what Enter does; the Up button and the crumbs have names; the scale is
//      announced on arrival
//   T12 the wrap: the ring's ways back in (an atom of the multiply-add, which Up always takes; an atom of a 6T memory
//      cell; the Planck length under the first atom); each lands where it says and Up climbs its branch; the landing
//      panel says the reader came round, and offers the way back
//   T14 the easter egg (the owner, 1 Oct 07:25): no level above the rack is named in the page's text, the breadcrumb,
//      the Up button or the panel at the rack or below; pressing Up from the rack still reaches them
//   T15 the two-state electronics: G, the drawing's switch and the panel's button switch the state; it holds from the
//      fin into the channel; switching runs no script per frame
//   T16 the dive by double-clicks (a double-tap on a phone): from the die, each scale's part for the next scale of the
//      default chain, down to a quark
//   T17 the loop (the owner, 1 Oct 09:00: "make sure it loops"): Up pressed again and again from the die goes out past
//      the observable universe, round the ring and in as one atom, twice, the same atom each time, and on round
//   T18 the navigation graph ("make sure all the things navigate"): every scale reached from the top and the ring by
//      any exit; every zoom has a seat; every cell of the die has its four edge links and each its link back; every
//      sideways glide has its glide back; every scale reaches the die and the die reaches every scale (no one-way exit)
//   T19 no dead ends ("make sure in all the places I eventually go all the way down to the lowest transistor level and
//      then I go down to the atoms"): every part from the rack down zooms somewhere (but the few that are not the
//      ET-SoC-1's, listed); from every scale zoom-ins reach a transistor (a FinFET, or a DRAM cell's on its own process)
//      and then an atom; and a vector add, by double-clicks, from the chip down through a textbook adder to an atom
import { open, sleep } from './cdp.mjs';
const args = process.argv.slice(2), PAGE = args.find(a => !a.startsWith('--')), PHONE = args.includes('--phone');
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7).split(',').filter(Boolean);
const SCENES = ((args.find(a => a.startsWith('--scenes=')) || '').slice(9) || process.env.SCENES || 'die,shire:20,shire:20/minion:20.1.3').split(',').filter(Boolean);
let fails = 0, passes = 0;
const ok = (c, what, extra) => { if (c) passes++; else fails++; console.log(`${c ? 'PASS' : 'FAIL'} ${what}${extra ? '  ' + extra : ''}`); return c; };
const T = {};
const atq = s => (s === 'die' ? '' : `?at=${s}`);
async function goScene(b, s) { await b.load(PAGE, atq(s), 1100); await b.idle(10000); return b.state(); }
/* a point inside the part (its centre, else a point of its box that the part itself is under) */
async function hitPoint(b, label) {
  return b.ev(`(() => {
    const g = [...document.querySelectorAll('#chip .comp')].find(g => g.getAttribute('aria-label') === ${JSON.stringify(label)} && g.getClientRects().length);
    if (!g) return null;
    const r = g.getBoundingClientRect();
    const pts = [[.5, .5], [.3, .5], [.7, .5], [.5, .3], [.5, .7], [.2, .2], [.8, .8], [.2, .8], [.8, .2], [.1, .5], [.9, .5], [.5, .02], [.02, .5], [.98, .5], [.5, .98], [.15, .15]].map(([fx, fy]) => [r.left + r.width * fx, r.top + r.height * fy]);
    // then the middles of the part's own shapes (a part drawn as dots, bonds or contacts between other parts)
    [...g.querySelectorAll('rect, circle, path, line, ellipse, polygon, text')].slice(0, 60).forEach(c => { const q = c.getBoundingClientRect(); if (q.width || q.height) pts.push([q.left + q.width / 2, q.top + q.height / 2]); });
    for (const [x, y] of pts) {
      const e = document.elementFromPoint(x, y);
      if (e && g.contains(e) && x > 0 && y > 0 && x < innerWidth && y < innerHeight) return {x, y};
    }
    return null; })()`);
}
async function scrollStage(b) { if (b.touch) await b.ev(`(() => { const r = document.getElementById('upbar').getBoundingClientRect(); window.scrollTo(0, Math.max(0, r.top + scrollY - 8)); })()`); await sleep(120); }

T.T1 = async b => {
  for (const sc of SCENES) {
    let s = await goScene(b, sc);
    const base = s.path;
    if (!ok(!!base, `T1 ${sc}: scene shown`, base)) continue;
    const parts = await b.ev('window.__chipTest.parts()');
    const byKey = new Map(); parts.forEach(p => { const l = byKey.get(p.key) || []; l.push(p); byKey.set(p.key, l); });
    for (const [key, list] of byKey) {
      const p0 = list.find(q => q.kid) ? list.filter(q => q.kid)[Math.floor(list.filter(q => q.kid).length / 2)] : list[0];
      // (parts of one kind with one label, a DRAM bank's twelve mats: the first of them is the one found by its label)
      const p = parts.find(q => q.label === p0.label) || p0;
      s = await goScene(b, sc); await scrollStage(b);
      const pt = await hitPoint(b, p.label);
      if (!ok(!!pt, `T1 ${sc} · ${key}: reachable`, p.label)) continue;
      if (b.touch) await b.dtap(pt.x, pt.y); else await b.dblclick(pt.x, pt.y);
      await sleep(80); await b.idle(12000);
      s = await b.state();
      if (p.kid && p.kid.startsWith('go:')) {
        // a way back in from the ring of sizes: a path of its own, the Planck length of a branch
        ok(s.path === p.kid.slice(3), `T1 ${sc} · ${key}: double-${b.touch ? 'tap' : 'click'} goes in at ${p.kid.slice(3).split('/').pop()}`, s.path.split('/').slice(-3).join('/'));
        continue;
      }
      if (p.kid && p.kid.startsWith('up:')) {
        const id = p.kid.slice(3);
        ok(s.path.split('/').pop().split(':')[0] === id && base.startsWith(s.path), `T1 ${sc} · ${key}: goes out to ${id}`, s.path);
        continue;
      }
      if (p.kid) {
        ok(s.path === base + '/' + p.kid, `T1 ${sc} · ${key}: double-${b.touch ? 'tap' : 'click'} enters ${p.kid}`, s.path);
        await b.ev(`document.getElementById('up').click()`); await sleep(60); await b.idle(12000);
        s = await b.state();
        ok(s.path === base, `T1 ${sc} · ${key}: Up returns`, s.path);
      } else {
        const zr = await b.ev(`(() => { const z = document.querySelector('#pn-body .pn-zoom'); return z ? {nz: !!z.querySelector('.nz'), btns: z.querySelectorAll('button').length} : null; })()`);
        ok(s.path === base && s.sel === p.label && !!zr, `T1 ${sc} · ${key}: no scale of its own: selected, zoom row shown`, JSON.stringify({path: s.path, sel: s.sel, zr}));
      }
    }
  }
};

T.T2 = async b => {
  for (const sc of SCENES) {
    let s = await goScene(b, sc);
    const base = s.path, tf = JSON.stringify(s.visible);
    const parts = await b.ev('window.__chipTest.parts()');
    const p = parts.find(q => q.kid) || parts[0]; if (!p) continue;
    await scrollStage(b);
    const pt = await hitPoint(b, p.label); if (!ok(!!pt, `T2 ${sc}: a part to click`, p.label)) continue;
    if (b.touch) await b.tap(pt.x, pt.y); else await b.click(pt.x, pt.y);
    await sleep(700);
    s = await b.state();
    ok(s.path === base && JSON.stringify(s.visible) === tf && !s.zooming, `T2 ${sc}: a ${b.touch ? 'tap' : 'click'} does not move the camera`, s.path);
    ok(s.sel === p.label && !!s.panel, `T2 ${sc}: it selects and the panel shows it`, `${s.sel} | ${s.panel}`);
    if (b.touch) ok(s.pill === !!p.kid || (s.pill && !p.kid), `T2 ${sc}: the pill shows`, String(s.pill));
  }
};

T.T3 = async b => {
  let s = await goScene(b, 'die');
  const deep = await b.ev('window.__chipTest.defPath()');
  // the deepest default path, relative to the root's ladder: load it through ?at= (from the die down)
  const rel = deep.split('/'), di = rel.indexOf('die');
  s = await goScene(b, rel.slice(di).join('/'));
  ok(s.path === deep, 'T3 the deepest default scale', s.path);
  const depth = s.depth;
  let n = 0;
  for (; n < 80; n++) {
    s = await b.state();
    if (s.depth === 0) break;
    const parent = s.path.split('/').slice(0, -1);
    await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000);
    const s2 = await b.state();
    if (!ok(s2.path === parent.join('/'), `T3 Up ${n + 1}: to ${parent[parent.length - 1]}`, s2.path)) break;
  }
  ok(n === depth, `T3 Up pressed ${n} times for a depth of ${depth}`);
  // at the top the button is never disabled: it goes round the ring of sizes (the wrap, 1 Oct)
  s = await b.state();
  ok(!s.upDisabled && /\?/.test(s.up), 'T3 at the top, Up says only "?" (the easter egg)', s.up);
  await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  const ro = await b.ev(`document.getElementById('scale-ro').textContent`), pn = await b.ev(`document.getElementById('pn-body').textContent`);
  ok(s.path === 'p.wrap' && /conceptual link/.test(ro), 'T3 Up past the top: the ring of sizes, no size but "conceptual link"', `${s.path} | ${ro}`);
  ok(/not further out in space/.test(pn) && /Round the ring/.test(s.up), 'T3 the ring says it is not a place; Up goes round it', s.up);
  await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.node === 'p.atom' && /lib\.xor\/lib\.finfet\/lib\.fin\/lib\.channel\/lib\.si\/p\.atom$/.test(s.path), 'T3 Up from the ring: in again as an atom of the multiply-add', s.path.split('/').slice(-6).join('/'));
  // and up again to the die: 15 presses (the crystal, the channel, the fin, the FinFET, the XOR, the full adder, the 4:2,
  // the column, the tree, the multiply-add, the lane, the vector unit, the minion, the shire, the chip)
  let m = 0; for (; m < 30 && s.node !== 'die'; m++) { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); s = await b.state(); }
  ok(s.node === 'die' && m === 15, `T3 from the atom up to the die: ${m} presses (15)`, s.path.split('/').slice(-2).join('/'));
  // the breadcrumb: back down to the chip in one click, then to the deepest crumb is the default chain's next crumb
  await b.load(PAGE, '?at=' + rel.slice(di).join('/'), 1100); await b.idle(10000);
  const crumbs = await b.ev(`[...document.querySelectorAll('#crumbs button')].map(x => ({t: x.textContent, ci: x.dataset.ci, name: x.getAttribute('aria-label') || x.textContent}))`);
  ok(crumbs.every(c => c.name && c.name.trim()), 'T3 every crumb has a name', crumbs.map(c => c.t).join(' '));
  const chip = crumbs.find(c => c.t === 'Chip');
  if (chip) {
    await b.ev(`document.querySelector('#crumbs button[data-ci="${chip.ci}"]').click()`); await sleep(60); await b.idle(15000);
    s = await b.state(); ok(s.path.split('/').pop() === 'die', 'T3 the "Chip" crumb goes to the chip', s.path);
  } else {
    const more = crumbs.find(c => c.ci === 'more');
    ok(!!more, 'T3 the chip crumb is folded into the "…" menu', crumbs.map(c => c.t).join(' '));
  }
  // the "…" menu: every folded ancestor is reachable, the easter egg's as "?"
  const fold = await b.ev(`(() => { const m = document.querySelector('#crumbs .more'); if (!m) return null; m.click(); const it = [...document.querySelectorAll('#crumb-menu button')].map(x => x.textContent); return it; })()`);
  if (fold) ok(fold.length > 0 && fold[0] === '?', `T3 the "…" menu lists ${fold.length} levels, the egg's as "?"`, fold.join(' | '));
};

T.T4 = async b => {
  for (const sid of [20, 0, 7, 24, 31, 32]) {
    let s = await goScene(b, `shire:${sid}`);
    if (!ok(s.level === 1 && s.sid === sid, `T4 shire ${sid} shown`, JSON.stringify([s.level, s.sid]))) continue;
    const links = await b.ev(`[...document.querySelectorAll('#chip .lay[data-level="1"] .nbr')].filter(g => g.getClientRects().length).map(g => ({l: g.getAttribute('aria-label'), role: g.getAttribute('role'), tab: g.tabIndex}))`);
    const edges = await b.ev(`[...document.querySelectorAll('#chip .lay[data-level="1"] text')].filter(t => /die edge/.test(t.textContent)).map(t => ({focusable: t.closest('[tabindex]') ? 1 : 0}))`);
    ok(links.every(l => l.role === 'link' && l.tab === 0), `T4 shire ${sid}: ${links.length} links, role link, focusable`, links.map(l => l.l).join(' | '));
    ok(edges.every(e => !e.focusable), `T4 shire ${sid}: ${edges.length} die-edge labels not focusable`);
    for (const lk of links) {
      const lab = lk.l, m = /Go to (shire (\d+)|master shire|spare shire|.+), (north|south|east|west)/.exec(lab);
      const tgt = m && m[2] != null ? +m[2] : /master shire/.test(lab) ? 32 : /spare shire/.test(lab) ? 33 : null;
      const dir = {north: 'ArrowUp', south: 'ArrowDown', west: 'ArrowLeft', east: 'ArrowRight'}[m[3]];
      for (const how of b.touch ? ['tap'] : ['click', 'enter', 'arrow']) {
        s = await goScene(b, `shire:${sid}`); await scrollStage(b);
        const sel = `[...document.querySelectorAll('#chip .lay[data-level="1"] .nbr')].find(g => g.getAttribute('aria-label') === ${JSON.stringify(lab)})`;
        const bx = await b.box('js:' + sel);
        if (how === 'click') await b.click(bx.x, bx.y);
        else if (how === 'tap') await b.tap(bx.x, bx.y);
        else if (how === 'enter') { await b.ev(`(${sel}).focus()`); await b.key('Enter'); }
        else { await b.ev(`(${sel}).focus()`); await b.key(dir); }
        // sample the move: a glide shows two shire layers and no die
        let maxSh = 0, die = false;
        for (let i = 0; i < 60; i++) { const st = await b.state(); const v = st.visible.filter(x => x.node === 'shire').length; maxSh = Math.max(maxSh, v); if (st.visible.some(x => x.node === 'die')) die = true; if (!st.zooming && i > 2) break; await sleep(25); }
        await b.idle(9000);
        s = await b.state();
        if (tgt != null) {
          const back = await b.ev(`(() => { const a = document.activeElement; return a && a.classList && a.classList.contains('nbr') ? a.getAttribute('aria-label') : (a ? a.tagName + '.' + (a.getAttribute('class') || '') : null); })()`);
          ok(s.level === 1 && s.sid === tgt, `T4 shire ${sid} → ${lab} by ${how}`, JSON.stringify([s.level, s.sid]));
          ok(maxSh === 2 && !die, `T4 shire ${sid} → ${tgt} by ${how}: a glide (two shires shown, no die)`, JSON.stringify({maxSh, die}));
          if (how !== 'click' && how !== 'tap') ok(new RegExp(`Go to (shire ${sid}|master shire|spare shire),`).test(back || ''), `T4 shire ${sid} → ${tgt}: focus on the link back`, back);
        } else {
          // a memory shire, the PCIe or the I/O shire: a glide to its own scale (since the scales inside the die)
          const want = /memory shire (\d+)/.exec(lab) ? 'memshire:' + /memory shire (\d+)/.exec(lab)[1] : /PCIe/.test(lab) ? 'pcie' : /I\/O/.test(lab) ? 'io' : null;
          ok(want ? s.path.endsWith('die/' + want) : s.level === 0 && !!s.sel, `T4 shire ${sid} → ${lab} by ${how}: ${want || 'die, cell selected'}`, s.path.split('/').slice(-2).join('/'));
          if (want) ok(!die, `T4 shire ${sid} → ${want} by ${how}: a glide (no die)`, JSON.stringify({maxSh, die}));
        }
      }
    }
  }
  // with a flow on the stage, the arrows step its stages instead
  await b.load(PAGE, '?flow=1', 2500);
  const st0 = (await b.state()).stage;
  await b.key('ArrowRight'); await sleep(300);
  const st1 = (await b.state()).stage;
  ok(st1 === st0 + 1, 'T4 with a flow on, Right steps the stage', `${st0} → ${st1}`);
};

T.T5 = async b => {
  let s = await goScene(b, 'die');
  const deep = (await b.ev('window.__chipTest.defPath()')).split('/');
  const root = deep[0];
  s = await goScene(b, root);
  ok(s.depth === 0, 'T5 the top of the ladder', s.path);
  let prevM = null, mono = true, bad = [], steps = 0, nonsc = [];
  const watch = async () => { for (let j = 0; j < 400; j++) { const st = await b.state(); st.visible.forEach(v => { if (v.k > 30 || v.k < 1 / 30) bad.push(`${st.path.split('/').pop()}:${v.node}:${v.k.toFixed(3)}`); }); const tf = await b.ev(`[...document.querySelectorAll('#chip > g.lay')].filter(l => l.style.display !== 'none').map(l => l.getAttribute('transform') || '').filter(t => t && !/^matrix\\([-\\d.e]+,0,0,[-\\d.e]+,[-\\d.e]+,[-\\d.e]+\\)$/.test(t))`); nonsc.push(...tf); if (!st.zooming && j > 1) break; await sleep(16); } };
  for (let i = 0; i < deep.length - 1; i++) {
    await b.key('+');
    await watch();
    await b.idle(15000);
    s = await b.state();
    const want = deep.slice(0, i + 2).join('/');
    if (!ok(s.path === want, `T5 + ${i + 1}: ${deep[i + 1]}`, s.path.split('/').slice(-2).join('/'))) break;
    steps++;
    if (prevM != null && s.scale_m != null && !(s.scale_m < prevM)) mono = false;
    if (s.scale_m != null) prevM = s.scale_m;
  }
  ok(steps === deep.length - 1 && deep[deep.length - 1] === 'p.planck', `T5 every step arrived (${steps}), down to the Planck length`);
  ok(mono, 'T5 the scale falls at every step');
  // + at the Planck length goes round the ring, and + on the ring to the top: the loop inward
  await b.key('+'); await watch(); await b.idle(15000); s = await b.state();
  ok(s.path === 'p.wrap', 'T5 + at the Planck length: the ring of sizes', s.path);
  await b.key('+'); await watch(); await b.idle(15000); s = await b.state();
  ok(s.path === root, 'T5 + on the ring: the top of the ladder again', s.path);
  ok(!bad.length, 'T5 every visible layer within [1/30, 30]', bad.slice(0, 5).join(' '));
  ok(!nonsc.length, 'T5 every layer transform is a scale and a translation', nonsc.slice(0, 3).join(' '));
  const t0 = Date.now();
  await goScene(b, deep.slice(deep.indexOf('die')).join('/'));
  const ci = await b.ev(`(() => { const c = [...document.querySelectorAll('#crumbs button')].find(x => x.textContent === 'Chip'); if (c) { c.click(); return 1; } const m = document.querySelector('#crumbs .more'); if (!m) return 0; m.click(); const it = [...document.querySelectorAll('#crumb-menu button')].find(x => /^The chip/.test(x.textContent)); if (it) { it.click(); return 2; } return 0; })()`);
  const t1 = Date.now();
  await sleep(60); await b.idle(15000);
  s = await b.state();
  ok(ci && s.node === 'die' && Date.now() - t1 < 6500, `T5 one breadcrumb click back to the chip (${Date.now() - t1} ms)`, s.path.split('/').slice(-2).join('/'));
};

T.T6 = async b => {
  const keys = '1234567890b'.split('');
  let total = 0, good = 0;
  for (const k of keys) {
    await b.load(PAGE, `?flow=${k}`, 1500);
    await b.idle(20000);
    const n = await b.ev('window.__chipTest.nstages()');
    for (let i = 0; i < n; i++) {
      if (i) { await b.key('ArrowRight'); await sleep(150); await b.idle(15000); }
      const s = await b.state(), want = await b.ev('window.__chipTest.want()');
      total++;
      if (s.path === want && s.stage === i) good++;
      else console.log(`  flow ${k} stage ${i + 1}: at ${s.path} (stage ${s.stage + 1}), wants ${want}`);
    }
  }
  ok(good === total, `T6 every flow stage lands where it wants (${good}/${total})`);
  await b.load(PAGE, '?tour=1', 1500);
  let s = await b.state();
  for (let i = 0; i < 40 && s.tour != null && s.tour < 16; i++) { await b.key('ArrowRight', 8); await sleep(200); await b.idle(15000); s = await b.state(); }
  ok(s.tour === 16, 'T6 the tour steps to its end', String(s.tour));
  // a flow started far from the chip (San Francisco, or the silicon lattice) brings the camera back to it
  for (const q of ['?at=sf', '?at=p.wrap', '?at=' + (await b.ev('window.__chipTest.defPath()')).split('/').slice(20).join('/')]) {
    await b.load(PAGE, q, 1500); await b.idle(10000);
    await b.key('1'); await sleep(400);
    let t0 = Date.now(); while (Date.now() - t0 < 12000) { const st = await b.state(); if (!st.zooming && st.path === await b.ev('window.__chipTest.want()')) break; await sleep(100); }
    s = await b.state();
    ok(s.flow === 'A' && s.path === await b.ev('window.__chipTest.want()'), `T6 flow 1 started from ${q.slice(4, 30)}… comes to its stage`, s.path.split('/').slice(-2).join('/'));
  }
};

T.T7 = async b => {
  const r = await open(b.touch ? {w: 390, h: 844, dpr: 3, touch: true, reduced: true} : {w: 1280, h: 800, dpr: 1, reduced: true});
  try {
    await r.load(PAGE, '', 1500);
    const p = (await r.ev('window.__chipTest.parts()')).find(q => q.kid && q.key === 'cshire');
    await scrollStage(r);
    const pt = await hitPoint(r, p.label);
    if (r.touch) await r.dtap(pt.x, pt.y); else await r.dblclick(pt.x, pt.y);
    await sleep(60);
    const s = await r.state();
    ok(s.path.endsWith('die/' + p.kid) && !s.zooming, 'T7 reduced motion: a zoom is a cut', s.path);
    // (since 1 Oct the readout gives the size only; the current crumb names the scale)
    const ro = await r.ev(`document.getElementById('scale-ro').textContent + ' | ' + ((document.querySelector('#crumbs [aria-current]') || {}).textContent || '')`);
    ok(/3\.7 mm/.test(ro) && /Shire/.test(ro), 'T7 the readout and the current crumb are at the new scale', ro);
    await r.load(PAGE, '?at=beyond', 1500);
    await r.ev(`document.getElementById('up').click()`); await sleep(60);
    const w = await r.state();
    ok(w.path === 'p.wrap' && !w.zooming, 'T7 reduced motion: the wrap is a cut too', w.path);
    ok(!r.errs.length, 'T7 no console errors', r.errs.slice(0, 3).join(' | '));
  } finally { await r.close(); }
};

/* T9 (the part run in a browser): with the images folder missing, a photo level loads with no script error and says
   "photo not loaded"; with it, the images load (zoom_static.py checks sizes, the manifest and privacy) */
T.T9 = async b => {
  const { mkdtempSync, copyFileSync } = await import('node:fs');
  const { resolve, join } = await import('node:path');
  const d = mkdtempSync(resolve(process.env.ZT_TMP || '/home/yaroslavvb/claude/work/chipzoom/tests', 'noimg-'));
  // (a page on a local server is fetched: the copy alone, without its folder)
  if (/^https?:/.test(PAGE)) { const { writeFileSync } = await import('node:fs'); writeFileSync(join(d, 'page.html'), await (await fetch(PAGE)).text()); }
  else copyFileSync(PAGE, join(d, 'page.html'));
  const n0 = b.errs.length;
  await b.load(join(d, 'page.html'), '?at=rack', 2500); await b.idle(10000); await sleep(600);
  const said = await b.ev(`[...document.querySelectorAll('#chip .lay text')].some(t => t.textContent === 'photo not loaded' && t.getClientRects().length)`);
  const exc = b.errs.slice(n0).filter(e => /^EXC|^console\.error/.test(e));
  ok(said, 'T9 no images folder: the rack says "photo not loaded"');
  const nl = await b.ev(`(() => { const d = document.querySelector('#pn-body details'); if (d) d.open = true; return document.getElementById('pn-body').textContent; })()`);
  ok(/Sources not loaded/.test(nl), 'T9 no data file: the panel says "sources not loaded"', nl.slice(-120));
  ok(!exc.length, 'T9 no images folder: no script error', exc.slice(0, 2).join(' | '));
  b.errs.splice(n0);   // the missing files' own load errors are expected here
  await b.load(PAGE, '?at=rack', 2500); await b.idle(10000); await sleep(600);
  const loaded = await b.ev(`(() => { const im = document.querySelector('#chip .lay image'); return im ? im.getBBox().width > 0 && !document.querySelector('#chip .lay text') ? true : [...document.querySelectorAll('#chip .lay text')].every(t => t.textContent !== 'photo not loaded') : false; })()`);
  ok(loaded, 'T9 with the folder: the photo loads');
};

T.T11 = async b => {
  for (const sc of SCENES) {
    await goScene(b, sc);
    const bad = await b.ev(`window.__chipTest.parts().filter(p => !(p.kid ? /\\. Space for details; Enter (zooms in|goes out to it)\\.$/.test(p.label) : /: details$/.test(p.label))).map(p => p.label)`);
    ok(!bad.length, `T11 ${sc}: every part's label says what Enter does`, bad.slice(0, 4).join(' | '));
  }
  const up = await b.ev(`document.getElementById('up').getAttribute('aria-label')`);
  ok(!!up, 'T11 the Up button has a name', up);
  await goScene(b, 'die');
  const p = (await b.ev('window.__chipTest.parts()')).find(q => q.kid && q.key === 'cshire');
  await b.ev(`[...document.querySelectorAll('#chip .comp')].find(g => g.getAttribute('aria-label') === ${JSON.stringify(p.label)}).focus()`);
  await b.key('Enter'); await sleep(60); await b.idle(10000);
  const cs = await b.ev(`document.getElementById('cap-scale').textContent`);
  ok(/Scale: Shire/.test(cs), 'T11 the scale is announced on arrival', cs);
  const foc = await b.ev(`document.activeElement && document.activeElement.closest && document.activeElement.closest('#chip') ? document.activeElement.getAttribute('aria-label') : null`);
  ok(!!foc, 'T11 focus is in the new scale after Enter', foc);
  await b.key('Backspace'); await sleep(60); await b.idle(10000);
  const foc2 = await b.ev(`document.activeElement ? document.activeElement.getAttribute('aria-label') : null`);
  ok(foc2 === p.label, 'T11 zooming out focuses the part zoomed out of', foc2);
};

T.T12 = async b => {
  let s = await goScene(b, 'p.wrap');
  const xs = await b.ev('window.__chipTest.exits()');
  ok(xs.length === 3 && /lib\.xor\/lib\.finfet\/lib\.fin\/lib\.channel\/lib\.si\/p\.atom$/.test(xs[0].path) && /lib\.sram6t\/lib\.finfet\/lib\.fin\/lib\.channel\/lib\.si\/p\.atom$/.test(xs[1].path) && /p\.atom\/p\.nucleus\/p\.nucleon\/p\.quark\/p\.planck$/.test(xs[2].path),
    'T12 the ring\'s ways back in: an atom of the multiply-add, an atom of a 6T cell, the Planck length under the first', xs.map(x => x.id).join(', '));
  const parts = (await b.ev('window.__chipTest.parts()')).filter(p => /^exit-/.test(p.key));
  ok(parts.length === (b.touch ? 0 : 3), `T12 the ways back in are parts of the drawing${b.touch ? ' (a phone: in the panel)' : ''}`, parts.map(p => p.label).join(' | '));
  const pb = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].map(x => x.textContent)`);
  ok(pb.filter(t => /^An atom|^The tail/.test(t)).length === 3, 'T12 the panel offers the three ways back in', pb.join(' | '));
  ok(await b.ev('window.__chipTest.upExit()') === 'compute', 'T12 Up takes the atom of the multiply-add');
  const up = async () => { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); return b.state(); };
  const climb = async n => { const seen = []; for (let i = 0; i < n; i++) seen.push((await up()).node); return seen; };
  s = await up();
  ok(s.path === xs[0].path, 'T12 Up from the ring lands on the atom of the multiply-add', s.path.split('/').slice(-4).join('/'));
  const pn = await b.ev(`document.getElementById('pn-body').textContent`);
  ok(/You came round the ring/.test(pn) && /Back to the ring/.test(pn) && await b.ev('window.__chipTest.wrapin()') === s.path, 'T12 its panel says the reader came round, and offers the way back', pn.slice(0, 160));
  // + from the atom goes down to the Planck length and round to the ring (the loop backwards); Up from the ring lands on the
  // same atom again (one fixed point)
  for (let i = 0; i < 5; i++) { await b.key('+'); await sleep(40); await b.idle(15000); }
  s = await b.state();
  ok(s.path === 'p.wrap', 'T12 + from that atom: the nucleus, a proton, a quark, the Planck length, round to the ring', s.path);
  s = await up();
  ok(s.path === xs[0].path, 'T12 Up from the ring again: the same atom', s.path.split('/').slice(-3).join('/'));
  let seen = await climb(5);
  ok(seen.join(' ') === 'lib.si lib.channel lib.fin lib.finfet lib.xor', 'T12 Up climbs the compute branch: the crystal, the channel, the fin, the FinFET, the XOR gate', seen.join(' '));
  // the other ways in, from the panel
  await goScene(b, 'p.wrap');
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => /^An atom of a 6T/.test(x.textContent)).click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.path === xs[1].path, 'T12 the panel\'s memory-cell way in lands on its atom', s.path.split('/').slice(-4).join('/'));
  seen = await climb(5);
  ok(seen[4] === 'lib.sram6t' && seen[3] === 'lib.finfet', 'T12 Up climbs the memory branch: the FinFET, then the 6T cell', seen.join(' '));
  await goScene(b, 'p.wrap');
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => /^The tail/.test(x.textContent)).click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.path === xs[2].path, 'T12 the panel\'s tail way in lands on the Planck length', s.path.split('/').slice(-3).join('/'));
  seen = await climb(4);
  ok(seen.join(' ') === 'p.quark p.nucleon p.nucleus p.atom', 'T12 Up climbs from the Planck length: a quark, a proton, the nucleus, the atom', seen.join(' '));
};

/* the easter egg: the names of the levels above the rack */
const HIDDEN = ['Studio 45', 'San Francisco', 'Bernal', '29th Street', 'Bay Area', 'California', 'United States', 'Earth', 'Solar System', 'Milky Way', 'Local Group', 'Laniakea', 'observable universe', 'Beyond what we can see', 'Ring of sizes', 'ring of sizes', 'Andromeda', 'nearest stars'];
const visText = b => b.ev(`[...(function* () { const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let t; while ((t = tw.nextNode())) yield t; })()].filter(t => t.parentElement && t.parentElement.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) && !t.parentElement.closest('script,style')).map(t => t.textContent).join(' ')`);
T.T14 = async b => {
  for (const sc of ['die', 'rack', 'host', 'shire:0', 'shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet']) {
    await goScene(b, sc);
    await b.ev(`(() => { const t = document.getElementById('facttab'); t.scrollIntoView(); return 1; })()`); await sleep(400); await b.ev('window.scrollTo(0, 0)'); await sleep(150);
    const txt = (await visText(b)) + ' ' + await b.ev(`document.getElementById('up').getAttribute('aria-label') + ' ' + [...document.querySelectorAll('#crumbs button')].map(x => x.title + ' ' + (x.getAttribute('aria-label') || '')).join(' ')`);
    const hits = HIDDEN.filter(h => txt.includes(h));
    ok(!hits.length, `T14 ${sc}: no level above the rack is named on the page`, hits.join(', '));
  }
  const s0 = await goScene(b, 'rack');
  ok(/^↑ \?$/.test(s0.up.trim()), 'T14 at the rack the Up button says only "?"', s0.up);
  const cr = await b.ev(`[...document.querySelectorAll('#crumbs button')].map(x => x.textContent)`);
  ok(cr[0] === '?', 'T14 the breadcrumb shows the levels further out as one "?"', cr.join(' | '));
  await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000);
  const s1 = await b.state();
  ok(s1.node === 'studio45', 'T14 pressing Up from the rack still finds them', s1.path.split('/').slice(-2).join('/'));
  const s2 = await goScene(b, 'p.wrap');
  ok(/\?/.test(await b.ev(`[...document.querySelectorAll('#crumbs button')].map(x => x.textContent).join(' ')`)), 'T14 on the ring, the top of the ladder is "?" in the breadcrumb');
};

T.T15 = async b => {
  const D2 = 'shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet/lib.fin';
  await goScene(b, D2);
  ok(await b.ev('window.__chipTest.ston()') === false, 'T15 the gate starts at 0 V');
  const op = () => b.ev(`(() => { const a = document.querySelector('#chip .lay[data-node="lib.fin"] .st-b'); return a ? +getComputedStyle(a).opacity : -1; })()`);
  await b.key('g'); await sleep(400);
  ok(await b.ev('window.__chipTest.ston()') === true && await op() > 0.99, 'T15 G switches the gate on (the on state drawn)', String(await op()));
  const sw = await b.box('#chip .lay[data-node="lib.fin"] .stsw');
  if (b.touch) await b.tap(sw.x, sw.y); else await b.click(sw.x, sw.y);
  await sleep(400);
  ok(await b.ev('window.__chipTest.ston()') === false, 'T15 the drawing\'s switch switches it back');
  await b.ev(`document.querySelector('#pn-body button[data-act="state"]').click()`); await sleep(300);
  ok(await b.ev('window.__chipTest.ston()') === true, 'T15 the panel\'s button switches it');
  await b.key('+'); await sleep(60); await b.idle(15000);
  const sB = await b.ev(`(() => { const a = document.querySelector('#chip .lay[data-node="lib.channel"] .st-b'); return a ? +getComputedStyle(a).opacity : -1; })()`);
  ok((await b.state()).node === 'lib.channel' && sB > 0.99, 'T15 the state holds from the fin into the channel', String(sB));
  const sws = await b.ev(`[...document.querySelectorAll('#chip .stsw')].filter(g => g.getClientRects().length).map(g => [g.getAttribute('role'), g.getAttribute('aria-checked')])`);
  ok(sws.length && sws.every(x => x[0] === 'switch' && x[1] === 'true'), 'T15 the switch is a role="switch" with aria-checked', JSON.stringify(sws));
  // switching runs no script per frame: the animation frames requested in a second with the switch pressed twice are
  // those of a second at rest (the page's animation clock, which ticks every frame since 27 September)
  await b.ev(`(() => { window.__raf = 0; const r = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = f => { window.__raf++; return r(f); }; return 1; })()`);
  await sleep(300); await b.ev('window.__raf = 0'); await sleep(1000);
  const n0 = await b.ev('window.__raf');
  await b.ev('window.__raf = 0'); await b.key('g'); await sleep(450); await b.key('g'); await sleep(550);
  const n1 = await b.ev('window.__raf');
  ok(n1 - n0 <= 4, `T15 the switch adds no animation frames: ${n1} in a second with it pressed twice, ${n0} at rest`);
};

T.T16 = async b => {
  await goScene(b, 'die');
  const deep = (await b.ev('window.__chipTest.defPath()')).split('/'), di = deep.indexOf('die'), qi = deep.findIndex(x => x === 'p.quark');
  let n = 0;
  for (let i = di; i < qi; i++) {
    const want = deep[i + 1];
    await scrollStage(b);
    const parts = await b.ev('window.__chipTest.parts()');
    const p = parts.filter(q => q.kid === want)[0];
    if (!ok(!!p, `T16 ${deep[i]}: a part leads to ${want}`, parts.map(q => q.kid).filter(Boolean).slice(0, 8).join(' '))) break;
    const pt = await hitPoint(b, p.label);
    if (!ok(!!pt, `T16 ${deep[i]}: the part for ${want} can be ${b.touch ? 'tapped' : 'clicked'}`, p.label)) break;
    if (b.touch) await b.dtap(pt.x, pt.y); else await b.dblclick(pt.x, pt.y);
    await sleep(80); await b.idle(15000);
    const s = await b.state();
    if (!ok(s.path === deep.slice(0, i + 2).join('/'), `T16 double-${b.touch ? 'tap' : 'click'} ${n + 1}: into ${want}`, s.path.split('/').slice(-2).join('/'))) break;
    n++;
  }
  ok(n === qi - di, `T16 from the die to a quark in ${n} double-${b.touch ? 'taps' : 'clicks'}`);
};

/* the cells of the die beside the shires: a memory shire, the PCIe and the I/O shire, each with its four edge links;
   from a shire to each and back by its links (click or tap, Enter, the arrow keys) */
T.T4b = async b => {
  const C = await (async () => { await goScene(b, 'die'); return b.ev('window.__chipTest.cells()'); })();
  const bad = [], OPP = {N: 'S', S: 'N', W: 'E', E: 'W'}, by = new Map(C.map(c => [c.cell, c]));
  C.forEach(c => { Object.entries(c.want).forEach(([d, n]) => { if (!c.have[d] || c.have[d].cell !== n) bad.push(`${c.cell} ${d}: ${n}`); }); Object.entries(c.have).forEach(([d, h]) => { const o = by.get(h.cell); if (o && (!o.have[OPP[d]] || o.have[OPP[d]].cell !== c.cell)) bad.push(`${c.cell} ${d} → ${h.cell}: no way back`); }); });
  ok(C.length === 44 && !bad.length, `T4b every cell of the die with a scale (${C.length}) has a link to each neighbour, and each its link back`, bad.slice(0, 6).join(' | '));
  const nav = async (from, lab, how, want) => {
    await goScene(b, from); await scrollStage(b);
    const sel = `[...document.querySelectorAll('#chip .lay .nbr')].filter(g => g.getClientRects().length).find(g => g.getAttribute('aria-label') === ${JSON.stringify(lab)})`;
    const bx = await b.box('js:' + sel);
    if (!ok(!!bx, `T4b ${from}: a link "${lab}"`)) return null;
    let die = false;
    if (how === 'click') await b.click(bx.x, bx.y); else if (how === 'tap') await b.tap(bx.x, bx.y);
    else { await b.ev(`(${sel}).focus()`); await b.key(how === 'enter' ? 'Enter' : {north: 'ArrowUp', south: 'ArrowDown', west: 'ArrowLeft', east: 'ArrowRight'}[/, (\w+)$/.exec(lab)[1]]); }
    for (let i = 0; i < 60; i++) { const st = await b.state(); if (st.visible.some(x => x.node === 'die')) die = true; if (!st.zooming && i > 2) break; await sleep(25); }
    await b.idle(9000);
    const s = await b.state();
    ok(s.path.endsWith('die/' + want) && !die, `T4b ${from} → ${want} by ${how}: a glide, no die`, s.path.split('/').slice(-2).join('/'));
    return s;
  };
  const pairs = [['shire:24', 'Go to memory shire 0, west', 'memshire:0', 'Go to shire 24, east', 'shire:24'], ['memshire:0', 'Go to memory shire 1, south', 'memshire:1', 'Go to memory shire 0, north', 'memshire:0'],
    ['shire:32', 'Go to PCIe shire, east', 'pcie', 'Go to master shire, west', 'shire:32'], ['pcie', 'Go to I/O shire, east', 'io', 'Go to PCIe shire, west', 'pcie'],
    ['io', 'Go to shire 28, south', 'shire:28', 'Go to I/O shire, north', 'io'], ['shire:7', 'Go to memory shire 7, east', 'memshire:7', 'Go to shire 7, west', 'shire:7']];
  for (const [a, la, x, lb, back] of pairs) {
    for (const how of b.touch ? ['tap'] : ['click', 'enter', 'arrow']) {
      const s1 = await nav(a, la, how, x); if (!s1) continue;
      if (how !== 'click' && how !== 'tap') { const f = await b.ev(`document.activeElement && document.activeElement.classList.contains('nbr') ? document.activeElement.getAttribute('aria-label') : null`); ok(f === lb, `T4b ${a} → ${x} by ${how}: focus on the link back`, f); }
      await nav(x, lb, how, back);
    }
  }
};

/* the loop: Up, again and again, from the die */
T.T17 = async b => {
  await goScene(b, 'die');
  const atoms = [], ringAt = []; let n = 0, s = await b.state(), last = s.path, stuck = 0;
  for (; n < 120 && atoms.length < 2; n++) {
    await b.ev(`document.getElementById('up').click()`); await sleep(30); await b.idle(15000);
    s = await b.state();
    if (s.path === last) stuck++;
    last = s.path;
    if (s.node === 'p.wrap') ringAt.push(n + 1);
    if (s.node === 'p.atom') atoms.push({n: n + 1, path: s.path});
  }
  ok(!stuck, 'T17 every Up press moved the camera', String(stuck));
  ok(atoms.length === 2 && ringAt.length === 2 && ringAt[0] === atoms[0].n - 1 && ringAt[1] === atoms[1].n - 1, `T17 Up from the die: past the top, the ring, an atom (press ${atoms[0] && atoms[0].n}), and round again (press ${atoms[1] && atoms[1].n})`, JSON.stringify({ringAt, atoms: atoms.map(a => a.n)}));
  ok(atoms.length === 2 && atoms[0].path === atoms[1].path && /vpu\.lane:0\/vpu\.lane\.fma\/.*lib\.channel\/lib\.si\/p\.atom$/.test(atoms[0].path), 'T17 both times the same atom: a silicon atom in a transistor of lane 0\'s multiply-add', atoms[0] ? atoms[0].path.split('/').slice(-8).join('/') : '');
  ok(atoms.length === 2 && atoms[1].n - atoms[0].n === 37, `T17 one lap is ${atoms.length === 2 ? atoms[1].n - atoms[0].n : '?'} presses (37: 15 up to the die, 21 to the top, the ring, the atom)`);
};

/* the navigation graph, built in the page (window.__chipTest.graph) */
const FLOOR = new Set(['p.atom', 'p.electron', 'p.nucleus', 'p.nucleon', 'p.quark', 'p.planck', 'p.wrap']);
const DEVICE = new Set(['lib.finfet', 'lib.fin', 'lib.gate', 'lib.channel', 'lib.si', 'p.dopant', 'lib.dramcell']);
const EXT = new Set(['host · cpu', 'host · dimms', 'host · psu', 'card · vrm', 'card · ltm', 'card · dip', 'die · inferred']);
let GRAPH = null;
const graph = async b => { if (!GRAPH) { await goScene(b, 'die'); GRAPH = await b.ev('window.__chipTest.graph()'); } return GRAPH; };
T.T18 = async b => {
  const G = await graph(b), by = new Map(G.map(s => [s.id, s]));
  ok(G.length >= 90 && !G.some(s => s.err), `T18 ${G.length} scales reached from the top and the ring, each drawn`, G.filter(s => s.err).map(s => s.id + ': ' + s.err).slice(0, 3).join(' | '));
  const noseat = [];
  G.forEach(s => (s.parts || []).forEach(p => { if ((p.kid || p.go) && !p.seat) noseat.push(`${s.id} · ${p.key} → ${p.kid || p.go}`); }));
  G.forEach(s => (s.kids || []).forEach(k => { if (!k.seat) noseat.push(`${s.id} → ${k.kid}`); }));
  ok(!noseat.length, 'T18 every zoom, a part\'s or a scale\'s own, has its seat to zoom into', noseat.slice(0, 6).join(' | '));
  const bottom = G.filter(s => s.here).map(s => s.id);
  ok(!bottom.length, 'T18 no scale says "the bottom of this branch"', bottom.join(' '));
  const side1 = [], miss = [];
  G.forEach(s => Object.entries(s.side || {}).forEach(([d, v]) => { if (v.missing) miss.push(`${s.id} ${d}: ${v.missing}`); if (v.back === false) side1.push(`${s.path.split('/').pop()} ${d} → ${v.to}`); }));
  ok(!miss.length, 'T18 every cell of the die reached has a link to each neighbour', miss.slice(0, 6).join(' | '));
  ok(!side1.length, 'T18 every sideways glide (the arrow keys between siblings) has its glide back', side1.slice(0, 6).join(' | '));
  // the graph of scales: every exit an edge; no one-way exit means every scale reaches the die and the die every scale
  const id = p => p.split('/').pop().split(':')[0], E = new Map(G.map(s => [s.id, new Set()]));
  G.forEach(s => {
    const add = t => { if (t && by.has(t)) E.get(s.id).add(t); };
    (s.parts || []).forEach(p => add(p.id || (p.go && id(p.go)) || (p.up && p.up)));
    (s.kids || []).forEach(k => add(k.id)); add(s.up && id(s.up)); add(s.next && id(s.next));
    Object.values(s.side || {}).forEach(v => add(v.to && v.to !== 'die' ? id(v.to) : v.to));
  });
  const reach = (from, edges) => { const seen = new Set([from]), Q = [from]; while (Q.length) { const x = Q.shift(); (edges.get(x) || []).forEach(t => { if (!seen.has(t)) { seen.add(t); Q.push(t); } }); } return seen; };
  const R = new Map(G.map(s => [s.id, new Set()])); E.forEach((ts, f) => ts.forEach(t => R.get(t).add(f)));
  const fromDie = reach('die', E), toDie = reach('die', R);
  const notFrom = G.filter(s => !fromDie.has(s.id)).map(s => s.id), notTo = G.filter(s => !toDie.has(s.id)).map(s => s.id);
  ok(!notFrom.length, 'T18 the die reaches every scale', notFrom.join(' '));
  ok(!notTo.length, 'T18 every scale reaches the die (no one-way exit, no trap)', notTo.join(' '));
  // a zoom in is undone by Up: a part's or a scale's zoom from A lands on a path whose parent is A; a path of its own (the
  // card's edge) passes A on its way, so Up climbs back through it; only the ring's ways in do not (the loop)
  const oneway = [];
  G.forEach(s => (s.parts || []).forEach(p => { if (p.go && s.id !== 'p.wrap' && !p.go.startsWith(s.path + '/')) oneway.push(`${s.id} · ${p.key}`); }));
  ok(!oneway.length, 'T18 every path of its own starts from where its part is, so Up comes back', oneway.join(' | '));
};
T.T19 = async b => {
  const G = await graph(b), by = new Map(G.map(s => [s.id, s]));
  const dead = [], ext = [];
  G.forEach(s => { if (s.egg || FLOOR.has(s.id)) return; (s.parts || []).forEach(p => { if (p.ext) ext.push(`${s.id} · ${p.key}`); else if (!p.kid && !p.go && !p.up) dead.push(`${s.id} · ${p.key}`); }); });
  ok(!dead.length, `T19 every part from the rack down leads further in (${G.filter(s => !s.egg && !FLOOR.has(s.id)).reduce((n, s) => n + s.parts.length, 0)} parts)`, dead.slice(0, 8).join(' | '));
  ok(ext.every(e => EXT.has(e)), `T19 the parts that do not, ${[...new Set(ext)].length}, are not the ET-SoC-1's (the host's processor, memory and supply; the card's regulators and switches; the die's key)`, [...new Set(ext)].filter(e => !EXT.has(e)).join(' | '));
  const kidsOf = s => [...new Set((s.parts || []).filter(p => p.id).map(p => p.id).concat((s.kids || []).map(k => k.id)).concat((s.parts || []).filter(p => p.go).map(p => p.go.split('/').pop().split(':')[0])))];
  const reach = (from, goal) => { const seen = new Set([from]), Q = [from]; while (Q.length) { const x = Q.shift(); if (goal(x)) return true; const s = by.get(x); if (!s) continue; kidsOf(s).forEach(k => { if (!seen.has(k)) { seen.add(k); Q.push(k); } }); } return false; };
  const noT = [], noA = [];
  G.forEach(s => { if (FLOOR.has(s.id)) return; if (!DEVICE.has(s.id) && !reach(s.id, x => x === 'lib.finfet' || x === 'lib.dramcell')) noT.push(s.id); if (!reach(s.id, x => x === 'p.atom')) noA.push(s.id); });
  ok(!noT.length, `T19 from every scale (${G.filter(s => !FLOOR.has(s.id) && !DEVICE.has(s.id)).length} above the device) zoom-ins reach a transistor`, noT.join(' '));
  ok(!noA.length, 'T19 and from every scale zoom-ins reach an atom', noA.join(' '));
  // the DRAM's transistors are its own process's: never the N7 FinFET
  const dramT = ['dram', 'dram.bank', 'dram.cell', 'lib.dramcell'].filter(i => by.has(i) && reach(i, x => x === 'lib.finfet'));
  ok(!dramT.length, 'T19 the DRAM (its own process) leads to its cell\'s transistor, never to the N7 FinFET', dramT.join(' '));
  // the owner's case: a vector add, by double-clicks, down to an atom
  const chain = [['shire', 'cshire'], ['minion', 'minion'], ['vpu', 'vpu'], ['vpu.lane', 'vpu.lane'], ['vpu.lane.fma', 'vpu.lane.fma'], ['lib.adder', 'fmaadd'], ['lib.aoi21', 'pfx1'],
    ['lib.finfet', 'onefet'], ['lib.fin', 'devring'], ['lib.channel', 'thefin'], ['lib.si', 'lattice'], ['p.atom', 'oneatom']];
  await goScene(b, 'die');
  let n = 0;
  for (const [want, key] of chain) {
    await scrollStage(b);
    const parts = await b.ev('window.__chipTest.parts()');
    const p = parts.filter(q => q.key === key && q.kid && q.kid.split(':')[0] === want)[0] || parts.filter(q => q.kid && q.kid.split(':')[0] === want)[0];
    if (!ok(!!p, `T19 the vector add: a part leads to ${want}`, parts.map(q => q.key).slice(0, 10).join(' '))) break;
    const pt = await hitPoint(b, p.label);
    if (!ok(!!pt, `T19 the vector add: the part for ${want} can be ${b.touch ? 'tapped' : 'clicked'}`, p.label)) break;
    if (b.touch) await b.dtap(pt.x, pt.y); else await b.dblclick(pt.x, pt.y);
    await sleep(80); await b.idle(15000);
    const s = await b.state();
    if (!ok(s.node === want, `T19 the vector add, double-${b.touch ? 'tap' : 'click'} ${n + 1}: into ${want}`, s.path.split('/').slice(-2).join('/'))) break;
    n++;
  }
  ok(n === chain.length, `T19 a vector add from the chip to a silicon atom in ${n} double-${b.touch ? 'taps' : 'clicks'}, through a textbook adder`);
};

const b = await open(PHONE ? {w: 390, h: 844, dpr: 3, touch: true} : {w: 1280, h: 800, dpr: 1});
try {
  for (const [k, fn] of Object.entries(T)) {
    if (ONLY.length && !ONLY.includes(k)) continue;
    console.log(`== ${k} ${PHONE ? '(phone)' : '(desktop)'}`);
    try { await fn(b); } catch (e) { ok(false, `${k} threw`, e.message); }
  }
  ok(!b.errs.length, 'no console errors', b.errs.slice(0, 6).join(' || '));
} finally { await b.close(); }
console.log(`${passes} passed, ${fails} failed`);
process.exitCode = fails;
