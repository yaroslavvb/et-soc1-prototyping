// node zoom_test.mjs PAGE [--phone] [--only=T1,T4] [--scenes=a,b] : the chip diagram's zoom and navigation tests
// (DESIGN §6.2), driven with real input events over the DevTools protocol (cdp.mjs). Desktop 1280 x 800 with a mouse;
// --phone: 390 x 844, touch emulation, DPR 3. Each test prints PASS or FAIL lines; the exit code is the number of
// failures. The page's hooks: window.__chipState() (where the camera is) and window.__chipTest (the parts of the scale
// shown and what each zooms into, the stage a flow wants shown).
//   T1 every part: a double-click (double-tap) on one part of each kind, in each scene, enters its own scale (or, for
//      a part with none, selects it and shows the panel's zoom row); then the Up button comes back
//   T2 a click (tap) selects and never moves the camera; on touch the pill shows
//   T3 Up from the deepest default scale (since 1 Oct the Planck length) to the top, one level a press; at the top Up
//      says only "?", and (since 1 Oct evening) goes round the loop straight to the same Planck length: one cross-fade,
//      the readout from 10²⁶ to 10⁻³⁵ m, a note, nothing zoomed in; its panel says so and offers the ring of sizes; Up
//      from there through a quark, a proton, the nucleus and the atom to the die; the breadcrumb back down; the "…" menu
//   T4 a shire's edge links, by click (tap), Enter and the arrow keys; a glide between shires; since the owner's second
//      update, the memory, PCIe and I/O shires' links too, each with its link back (T4b)
//   T5 the dive: + from the top of the ladder to the bottom of the default chain (the Planck length), every step
//      arriving, the readout monotone, every visible layer's scale within [1/30, 30]; then + round the loop straight
//      back to the top (one cross-fade, not by the ring); then one breadcrumb click back to the chip
//   T6 the flows: every stage of every flow lands where it wants the camera
//   T7 reduced motion: a zoom is a cut, and so is the loop (Up at the top) and a move off the ring
//   T11 accessibility: every part's label says what Enter does; the Up button and the crumbs have names; the scale is
//      announced on arrival
//   T12 the ring of sizes, off the loop since 1 Oct evening: #at=p.wrap opens it, and the top's panel and the Planck
//      length's (after coming round) link to it, but no Up or + leads there; its ways back in (an atom of the
//      multiply-add; an atom of an L2 memory cell, drawn as a 6T cell; the Planck length under the first atom, which its Up takes, while +
//      goes to the top) each land where they say and Up climbs their branch; the landing panel says the reader came
//      round, and offers the way back
//   T14 the easter egg (the owner, 1 Oct 07:25): no level above the rack is named in the page's text, the breadcrumb,
//      the Up button or the panel at the rack or below; pressing Up from the rack still reaches them
//   T15 the two-state electronics: G, the drawing's switch and the panel's button switch the state; it holds from the
//      fin into the channel; switching runs no script per frame
//   T16 the dive by double-clicks (a double-tap on a phone): from the die, each scale's part for the next scale of the
//      default chain, down to a quark
//   T17 the loop (the owner, 1 Oct 09:00: "make sure it loops"; 17:10: "The loop should always go in one direction"):
//      Up pressed again and again from the die goes out past the top straight to the Planck length, then a quark, a
//      proton, the nucleus and the same atom, and round again, three times; every lap the same 40 presses; every press
//      one level out (the top's: round to the Planck length), never by the ring; no press zooms in (no layer grows on
//      the screen)
//   T18 the navigation graph ("make sure all the things navigate"): every scale reached from the top and the ring by
//      any exit; every zoom has a seat; every cell of the die has its four edge links and each its link back; every
//      sideways glide has its glide back; every scale reaches the die and the die reaches every scale (no one-way exit;
//      the ring by the top's panel link, the only way to it besides its address)
//   T19 no dead ends ("make sure in all the places I eventually go all the way down to the lowest transistor level and
//      then I go down to the atoms"): every part from the rack down zooms somewhere (but the die's key, a legend); from
//      every scale zoom-ins reach a transistor (a FinFET, a DRAM cell's or a power transistor's on its own process) and
//      then an atom; by double-clicks, a vector add from the chip through a textbook adder to an atom, and (part 1b) a
//      PCIe lane, the card's boot switches and its core regulator down to an atom
//   T20 (part 1b) every scene by its path (window.__chipTest.walk): every part of every drawing leads in, its seat there
//      in that drawing; every zoom to a transistor comes from a drawing in transistors; every scale reaches a transistor
//      and an atom; the DRAM's and the regulators' chains never reach the N7 FinFET; the walk leaves no layer behind
//   T21 links (1 Oct, the owner: "individual clicks like data->watts come with anchors"): each flow's button (1-9, 0, B)
//      writes #flow=<key>-<name> and the page opened with it plays that flow; a key and the tour's slides (#tour=N, a
//      flow's slide its flow's); a flow held at a stage (&stage=N) opens held there; the scale at rest (#at=, a deep
//      circuit, the rack, a shire, a level of the easter egg named alone) opens at the same place; a hashchange takes the
//      stage there by a move; fragments that name nothing warn and open the first view; #facts stays; Copy link (a
//      mocked clipboard, Enter, the spacesheep and GitHub Pages addresses, the forbidden clipboard's selected link);
//      reduced motion; in a frame (an http page) only ss-hash is posted, and a new fragment in the frame's src moves the
//      camera without a reload
//   T22 the replay's speed (1 Oct, the owner: "Next to the pause button in the replay ... Give an option to go to 2X or
//      1x speed"): the button beside Play/Pause on its row (1×, 2×; a phone's row does not wrap), the click and S;
//      flow 8 at 2x takes about half the time of 1x and plays the same stages in the same order; the clock's pace;
//      pause, the arrows, Follow and the tour at 2x; switching mid-flow, a camera move included; &speed=2 in the
//      address (opened, held, reloaded, a hashchange, a bad value); reduced motion at 2x
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
/* a move, sampled until the camera rests (call it right after the press): the layers it showed (node@depth), the kinds
   of its steps, the readouts on the way, the loop's note while it showed, every layer whose scale on the screen grew
   between two samples (a zoom in), every scale outside [1/30, 30] and every transform that is not a scale and a shift */
async function sampleMove(b, max = 15000) {
  const t0 = Date.now(), last = new Map(), o = {layers: new Set(), kinds: new Set(), ro: new Set(), note: '', grew: [], bad: [], nonsc: []};
  for (let j = 0; Date.now() - t0 < max; j++) {
    const q = await b.ev(`(() => { const s = window.__chipState(), n = document.querySelector('.loopnote');
      return {s, ro: document.getElementById('scale-ro').textContent, note: n && !n.hidden && +getComputedStyle(n).opacity > 0.05 ? n.textContent : '',
        tf: [...document.querySelectorAll('#chip > g.lay')].filter(l => l.style.display !== 'none').map(l => l.getAttribute('transform') || '').filter(t => t && !/^matrix\\([-\\d.e]+,0,0,[-\\d.e]+,[-\\d.e]+,[-\\d.e]+\\)$/.test(t))}; })()`);
    const s = q.s;
    if (s.step) o.kinds.add(s.step.kind);
    if (s.zooming) o.ro.add(q.ro);
    if (q.note) o.note = q.note;
    o.nonsc.push(...q.tf);
    s.visible.forEach(v => {
      const key = v.node + '@' + v.depth, k0 = last.get(key);
      o.layers.add(key);
      if (k0 != null && v.k > k0 * 1.005) o.grew.push(`${key} ${k0.toFixed(3)}→${v.k.toFixed(3)}`);
      if (v.k > 30 || v.k < 1 / 30) o.bad.push(`${s.path.split('/').pop()}:${key}:${v.k.toFixed(3)}`);
      last.set(key, v.k);
    });
    if (!s.zooming && j > 1) break;
    await sleep(12);
  }
  return o;
}

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
  // at the top the button is never disabled: it says only "?" and goes round the loop (since 1 Oct evening, the owner:
  // "When zooming up, skip this slide [the ring] ... it should directly go at the lowest level")
  s = await b.state();
  ok(!s.upDisabled && /^↑ \?$/.test(s.up.trim()), 'T3 at the top, Up says only "?" (the easter egg)', s.up);
  const pt = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].map(x => x.textContent + ' → ' + x.dataset.to)`);
  ok(pt.some(t => /^↑ Zoom out: \?/.test(t)) && pt.some(t => /ring of sizes.* → p\.wrap$/.test(t)), 'T3 the top\'s panel: "Zoom out: ?" too, and a link to the ring of sizes', pt.join(' | '));
  await b.ev(`document.getElementById('up').click()`);
  const mv = await sampleMove(b); await b.idle(15000);
  s = await b.state();
  ok(s.path === deep, 'T3 Up past the top: straight to the Planck length the climb started from (the loop\'s, under the atom of the multiply-add)', s.path.split('/').slice(-3).join('/'));
  ok([...mv.kinds].join() === 'wrap' && [...mv.layers].sort().join(' ') === `beyond@0 p.planck@${depth}`, 'T3 one step, a cross-fade of the two ends: nothing between them drawn, the ring not shown', `${[...mv.kinds]} | ${[...mv.layers].join(' ')}`);
  ok([...mv.ro].some(r => /round the loop: 10²⁶ m → 10⁻³⁵ m/.test(r)), 'T3 the readout on the way: from 10²⁶ m to 10⁻³⁵ m', [...mv.ro].join(' | '));
  ok(/Round the loop: from the observable universe to the Planck length/.test(mv.note), 'T3 a note over the drawing: from the observable universe to the Planck length', mv.note);
  ok(!mv.grew.length && !mv.bad.length, 'T3 the step only zooms out: neither end grows on the screen, both within [1/30, 30]', mv.grew.concat(mv.bad).slice(0, 3).join(' | '));
  const pn = await b.ev(`document.getElementById('pn-body').textContent`), ro = await b.ev(`document.getElementById('scale-ro').textContent`);
  // (since the fact review of 1 Oct the landing says it is no journey through space, and names the fixed point)
  ok(/round the loop/.test(pn) && /Not further out in space/.test(pn) && /XOR gate/.test(pn) && /The ring of sizes/.test(pn) && /10⁻³⁵ m/.test(ro), 'T3 its panel says the reader came round the loop (a picture, not a place), names the fixed atom, and offers the ring of sizes; the readout at rest gives the Planck length', `${ro} | ${pn.slice(0, 220)}`);
  // and up again to the die: 19 presses (a quark, a proton, the nucleus, the atom, the crystal, the channel, the fin, the
  // FinFET, the XOR, the full adder, the 4:2, the column, the tree, the multiply-add, the lane, the vector unit, the
  // minion, the shire, the chip)
  let m = 0; const seen = [];
  for (; m < 30 && s.node !== 'die'; m++) { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); s = await b.state(); seen.push(s.node); }
  ok(s.node === 'die' && m === depth - di && seen.slice(0, 4).join(' ') === 'p.quark p.nucleon p.nucleus p.atom', `T3 from the Planck length up to the die: ${m} presses (${depth - di}), through a quark, a proton, the nucleus and the atom`, seen.slice(0, 5).join(' '));
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
  // + at the Planck length goes round the loop straight to the top (since 1 Oct evening, not by the ring): the loop inward
  await b.key('+'); const mv = await sampleMove(b); await b.idle(15000); s = await b.state();
  bad.push(...mv.bad); nonsc.push(...mv.nonsc);
  ok(s.path === root && [...mv.kinds].join() === 'wrap' && [...mv.layers].sort().join(' ') === `${root}@0 p.planck@${deep.length - 1}`, 'T5 + at the Planck length: straight to the top of the ladder, one cross-fade (the ring not shown)', `${s.path} | ${[...mv.kinds]} | ${[...mv.layers].join(' ')}`);
  ok([...mv.ro].some(r => /round the loop: 10⁻³⁵ m → 10²⁶ m/.test(r)) && /Round the loop: from the Planck length to the observable universe/.test(mv.note), 'T5 on the way the readout goes from 10⁻³⁵ m to 10²⁶ m, and the note says so', `${[...mv.ro].join(' | ')} | ${mv.note}`);
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
    ok(/\/p\.planck$/.test(w.path) && !w.zooming, 'T7 reduced motion: the loop (Up at the top, to the Planck length) is a cut too', w.path.split('/').slice(-2).join('/'));
    await r.load(PAGE, '?at=p.wrap', 1500);
    await r.ev(`document.getElementById('up').click()`); await sleep(60);
    const w2 = await r.state();
    ok(/\/p\.planck$/.test(w2.path) && !w2.zooming, 'T7 reduced motion: off the ring (Up) is a cut', w2.path.split('/').slice(-2).join('/'));
    ok(!r.errs.length, 'T7 no console errors', r.errs.slice(0, 3).join(' | '));
  } finally { await r.close(); }
};

/* T9 (the part run in a browser): with the images folder missing, a photo level loads with no script error and says
   "photo not loaded"; with it, the images load (zoom_static.py checks sizes, the manifest and privacy) */
T.T9 = async b => {
  const { mkdtempSync, copyFileSync } = await import('node:fs');
  const { resolve, join } = await import('node:path');
  // (ZT_TMP, else TMPDIR, else the system's: no one machine's folder; code review of 1 Oct)
  const { tmpdir } = await import('node:os');
  const d = mkdtempSync(resolve(process.env.ZT_TMP || process.env.TMPDIR || tmpdir(), 'noimg-'));
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
  // the ring opens by its address (the query and, since the links of 1 Oct, the fragment)
  let s = await goScene(b, 'p.wrap');
  ok(s.path === 'p.wrap', 'T12 ?at=p.wrap opens the ring of sizes', s.path);
  await b.send('Page.navigate', {url: 'about:blank'}); await sleep(120); await b.load(PAGE, '#at=p.wrap', 1500); await b.idle(10000);
  s = await b.state();
  ok(s.path === 'p.wrap' && await b.ev('location.hash') === '#at=p.wrap', 'T12 #at=p.wrap opens the ring of sizes', `${s.path} ${await b.ev('location.hash')}`);
  const xs = await b.ev('window.__chipTest.exits()');
  ok(xs.length === 3 && /lib\.xor\/lib\.finfet\/lib\.fin\/lib\.channel\/lib\.si\/p\.atom$/.test(xs[0].path) && /lib\.sram6t\/lib\.finfet\/lib\.fin\/lib\.channel\/lib\.si\/p\.atom$/.test(xs[1].path) && /p\.atom\/p\.nucleus\/p\.nucleon\/p\.quark\/p\.planck$/.test(xs[2].path),
    'T12 the ring\'s ways back in: an atom of the multiply-add, an atom of an L2 memory cell (drawn as 6T), the Planck length under the first', xs.map(x => x.id).join(', '));
  const parts = (await b.ev('window.__chipTest.parts()')).filter(p => /^exit-/.test(p.key));
  ok(parts.length === (b.touch ? 0 : 3), `T12 the ways back in are parts of the drawing${b.touch ? ' (a phone: in the panel)' : ''}`, parts.map(p => p.label).join(' | '));
  const pb = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].map(x => x.textContent)`);
  ok(pb.filter(t => /^An atom|^The tail/.test(t)).length === 3, 'T12 the panel offers the three ways back in', pb.join(' | '));
  ok(await b.ev('window.__chipTest.upExit()') === 'planck', 'T12 Up (from the top, and from the ring) takes the Planck length under the atom of the multiply-add');
  const up = async () => { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); return b.state(); };
  const climb = async n => { const seen = []; for (let i = 0; i < n; i++) seen.push((await up()).node); return seen; };
  s = await up();
  ok(s.path === xs[2].path, 'T12 Up from the ring lands on the Planck length under that atom', s.path.split('/').slice(-3).join('/'));
  const pn = await b.ev(`document.getElementById('pn-body').textContent`);
  ok(/You came round the ring/.test(pn) && /Back to the ring/.test(pn) && await b.ev('window.__chipTest.wrapin()') === s.path, 'T12 its panel says the reader came round, and offers the way back', pn.slice(0, 160));
  // the ring is off the loop: + from the Planck length goes to the top, and Up from the top to the Planck length
  await b.key('+'); await sleep(40); await b.idle(15000); s = await b.state();
  ok(s.path === 'beyond', 'T12 + from the Planck length: the top of the ladder, not the ring', s.path);
  s = await up();
  ok(s.path === xs[2].path, 'T12 Up from the top: the Planck length again, not the ring', s.path.split('/').slice(-3).join('/'));
  // the links to it: the Planck length's panel after coming round, and the top's panel
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => x.dataset.to === 'p.wrap').click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.path === 'p.wrap', 'T12 the Planck length\'s panel, after coming round the loop, links to the ring', s.path);
  await goScene(b, 'beyond');
  const tb = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].filter(x => x.dataset.to === 'p.wrap').map(x => x.textContent)`);
  ok(tb.length === 1 && /ring of sizes/.test(tb[0]), 'T12 the top\'s panel links to the ring of sizes', tb.join(' | '));
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => x.dataset.to === 'p.wrap').click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.path === 'p.wrap', 'T12 and goes there', s.path);
  await b.key('+'); await sleep(40); await b.idle(15000); s = await b.state();
  ok(s.path === 'beyond', 'T12 + on the ring: the top', s.path);
  // the other ways in, from the ring's panel
  await goScene(b, 'p.wrap');
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => /^An atom of the multiply/.test(x.textContent)).click()`); await sleep(40); await b.idle(15000);
  s = await b.state();
  ok(s.path === xs[0].path, 'T12 the panel\'s compute way in lands on the atom of the multiply-add', s.path.split('/').slice(-4).join('/'));
  let seen = await climb(5);
  ok(seen.join(' ') === 'lib.si lib.channel lib.fin lib.finfet lib.xor', 'T12 Up climbs the compute branch: the crystal, the channel, the fin, the FinFET, the XOR gate', seen.join(' '));
  await goScene(b, 'p.wrap');
  // (since the fact review of 1 Oct the shire cache's cell is "drawn as" a 6T cell: its bitcell is not published)
  await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].find(x => /^An atom of an L2 memory cell/.test(x.textContent)).click()`); await sleep(40); await b.idle(15000);
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

/* the loop: Up, again and again, from the die (each move sampled: no layer may grow on the screen) */
T.T17 = async b => {
  await goScene(b, 'die');
  const xs = await b.ev('window.__chipTest.exits()'), PL = xs.find(x => x.id === 'planck').path, AT = xs.find(x => x.id === 'compute').path;
  const lands = [], planckAt = [], ring = [], grew = [], wrong = [];
  let s = await b.state(), prev = s.path, stuck = 0, n = 0;
  for (; n < 140 && planckAt.length < 3; n++) {
    await b.ev(`document.getElementById('up').click()`);
    const mv = await sampleMove(b); await b.idle(15000);
    s = await b.state();
    if (s.path === prev) stuck++;
    const top = !prev.includes('/'), want = top ? PL : prev.split('/').slice(0, -1).join('/');
    if (s.path !== want) wrong.push(`press ${n + 1}: ${prev.split('/').pop()} → ${s.path.split('/').pop()}`);
    if (mv.grew.length) grew.push(`press ${n + 1} (${prev.split('/').pop()} → ${s.node}): ${mv.grew.slice(0, 2).join(', ')}`);
    if (s.node === 'p.wrap' || mv.layers.has('p.wrap@0')) ring.push(n + 1);
    if (s.path === PL) planckAt.push(n + 1);
    lands.push(s.path); prev = s.path;
  }
  ok(!stuck, 'T17 every Up press moved the camera', String(stuck));
  ok(planckAt.length === 3 && planckAt[0] === 21 && !ring.length, `T17 Up from the die: out past the top straight to the Planck length (press ${planckAt[0]}), and round again (presses ${planckAt.slice(1).join(' and ')}), never by the ring`, JSON.stringify({planckAt, ring}));
  const laps = planckAt.slice(1).map((p, i) => p - planckAt[i]);
  ok(laps.length === 2 && laps.every(l => l === 40), `T17 every lap the same number of presses: ${laps.join(', ')} (40: a quark, a proton, the nucleus, the atom, on up to the top, and round)`);
  const after = planckAt.slice(0, 2).map(p => lands.slice(p, p + 4).map(x => x.split('/').pop()).join(' '));
  ok(after.length === 2 && after.every(x => x === 'p.quark p.nucleon p.nucleus p.atom') && planckAt.slice(0, 2).every(p => lands[p + 3] === AT), 'T17 every lap from the Planck length: a quark, a proton, the nucleus and the same atom of the multiply-add', after.join(' | '));
  ok(!wrong.length, `T17 every press one level out, the top's round the loop to the Planck length (${n} presses)`, wrong.slice(0, 4).join(' | '));
  ok(!grew.length, 'T17 no press zooms in: no layer ever grows on the screen, the loop\'s step included', grew.slice(0, 4).join(' | '));
};

/* the navigation graph, built in the page (window.__chipTest.graph) */
const FLOOR = new Set(['p.atom', 'p.cu', 'p.electron', 'p.nucleus', 'p.nucleon', 'p.quark', 'p.planck', 'p.wrap']);
const DEVICE = new Set(['lib.finfet', 'lib.fin', 'lib.gate', 'lib.channel', 'lib.si', 'p.dopant', 'lib.dramcell', 'lib.powerfet']);
// the transistors: the N7 FinFET, a DRAM cell's own (a DRAM process) and a regulator's power transistor (since part 1b)
const TRANS = new Set(['lib.finfet', 'lib.dramcell', 'lib.powerfet']), ATOM = new Set(['p.atom', 'p.cu']);
// (part 1b) the one part with no zoom: the die's key, a legend of the drawing, not a part of the chip
const EXT = new Set(['die · inferred']);
// a zoom straight to a transistor from a drawing not made of transistors: only where the drawing is a section that shows
// the transistors themselves (the die's bottom layer, the contact under a wire)
const SECT = new Set(['die.metal · fets', 'lib.wire · contact']);
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
  // the ring of sizes is off the loop (1 Oct evening): no Up or + leads to it, its Up and + lead to the Planck length and
  // the top, the top's Up goes round to the Planck length, and the top's panel links to it (read from the panel: an edge)
  const toRing = G.filter(s => s.id !== 'p.wrap' && [s.up, s.next].some(x => x && id(x) === 'p.wrap')).map(s => s.id);
  ok(!toRing.length, 'T18 no scale\'s Up or + leads to the ring of sizes', toRing.join(' '));
  const RG = by.get('p.wrap'), TP = by.get('beyond');
  ok(!!RG && id(RG.up || '') === 'p.planck' && RG.next === 'beyond' && !!TP && id(TP.up || '') === 'p.planck', 'T18 the ring\'s Up goes to the Planck length and its + to the top; the top\'s Up round the loop to the Planck length', `${RG && RG.up} | ${RG && RG.next} | ${TP && TP.up}`);
  await goScene(b, 'beyond');
  const link = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].some(x => x.dataset.to === 'p.wrap')`);
  ok(link, 'T18 the top\'s panel links to the ring of sizes');
  if (link && E.has('beyond') && E.has('p.wrap')) E.get('beyond').add('p.wrap');
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
  ok(ext.every(e => EXT.has(e)), `T19 the parts that do not, ${[...new Set(ext)].length}: only the die's key, a legend (since part 1b the host's processor, memory and supply and the card's regulators and switches lead in too)`, [...new Set(ext)].filter(e => !EXT.has(e)).join(' | '));
  const kidsOf = s => [...new Set((s.parts || []).filter(p => p.id).map(p => p.id).concat((s.kids || []).map(k => k.id)).concat((s.parts || []).filter(p => p.go).map(p => p.go.split('/').pop().split(':')[0])))];
  const reach = (from, goal) => { const seen = new Set([from]), Q = [from]; while (Q.length) { const x = Q.shift(); if (goal(x)) return true; const s = by.get(x); if (!s) continue; kidsOf(s).forEach(k => { if (!seen.has(k)) { seen.add(k); Q.push(k); } }); } return false; };
  const noT = [], noA = [];
  G.forEach(s => { if (FLOOR.has(s.id)) return; if (!DEVICE.has(s.id) && !reach(s.id, x => TRANS.has(x))) noT.push(s.id); if (!reach(s.id, x => ATOM.has(x))) noA.push(s.id); });
  ok(!noT.length, `T19 from every scale (${G.filter(s => !FLOOR.has(s.id) && !DEVICE.has(s.id)).length} above the device) zoom-ins reach a transistor`, noT.join(' '));
  ok(!noA.length, 'T19 and from every scale zoom-ins reach an atom', noA.join(' '));
  // the DRAM's transistors are its own process's: never the N7 FinFET
  const dramT = ['dram', 'dram.bank', 'dram.cell', 'lib.dramcell'].filter(i => by.has(i) && reach(i, x => x === 'lib.finfet'));
  ok(!dramT.length, 'T19 the DRAM (its own process) leads to its cell\'s transistor, never to the N7 FinFET', dramT.join(' '));
  // the owner's case: a vector add, by double-clicks, down to an atom
  const DEV5 = [['lib.finfet', 'onefet'], ['lib.fin', 'devring'], ['lib.channel', 'thefin'], ['lib.si', 'lattice'], ['p.atom', 'oneatom']];
  await dclickChain(b, 'die', 'the vector add', [['shire', 'cshire'], ['minion', 'minion'], ['vpu', 'vpu'], ['vpu.lane', 'vpu.lane'], ['vpu.lane.fma', 'vpu.lane.fma'], ['lib.adder', 'fmaadd'], ['lib.aoi21', 'pfx1']].concat(DEV5),
    'from the chip to a silicon atom, through a textbook adder');
  // (part 1b) the places that stopped short before: a PCIe lane, the card's boot switches and its core regulator
  await dclickChain(b, 'die', 'a PCIe lane', [['pcie', 'pcie'], ['pcie.phy', 'pcie.phy'], ['pcie.lane', 'pcie.lane'], ['lib.diffamp', 'ctle'], ['lib.finfet', 'pair']].concat(DEV5.slice(1)),
    'from the chip through a SerDes lane and its equaliser to a silicon atom');
  await dclickChain(b, 'card:board', 'the boot switches', [['lib.strap', 'dip'], ['lib.inverter', 'rx']].concat(DEV5), 'from the card\'s DIP switches through the chip\'s input receiver to a silicon atom');
  await dclickChain(b, 'card:board', 'the core regulator', [['lib.buck', 'vrm'], ['lib.powerfet', 'hs'], ['lib.si', 'cell'], ['p.atom', 'oneatom']], 'from the card\'s regulator through its power transistor to a silicon atom');
};
/* double-clicks (double-taps) down a chain of [scale, part key] from a scene, each into the scale it names */
async function dclickChain(b, from, name, chain, what) {
  await goScene(b, from);
  let n = 0;
  for (const [want, key] of chain) {
    await scrollStage(b);
    const parts = await b.ev('window.__chipTest.parts()');
    const p = parts.filter(q => q.key === key && q.kid && q.kid.split(':')[0] === want)[0] || parts.filter(q => q.kid && q.kid.split(':')[0] === want)[0];
    if (!ok(!!p, `T19 ${name}: a part leads to ${want}`, parts.map(q => q.key).slice(0, 10).join(' '))) break;
    const pt = await hitPoint(b, p.label);
    if (!ok(!!pt, `T19 ${name}: the part for ${want} can be ${b.touch ? 'tapped' : 'clicked'}`, p.label)) break;
    if (b.touch) await b.dtap(pt.x, pt.y); else await b.dblclick(pt.x, pt.y);
    await sleep(80); await b.idle(15000);
    const s = await b.state();
    if (!ok(s.node === want, `T19 ${name}, double-${b.touch ? 'tap' : 'click'} ${n + 1}: into ${want}`, s.path.split('/').slice(-2).join('/'))) break;
    n++;
  }
  ok(n === chain.length, `T19 ${name} in ${n} double-${b.touch ? 'taps' : 'clicks'}: ${what}`);
}
/* (part 1b) every scene by its path, not one per scale: window.__chipTest.walk() follows every zoom-in from the die and
   from the rack, one path per shape (the scales along it; a cell of the die by its instance), and reports each scene's
   parts, what each leads to, whether its seat is there in that drawing, and how many transistors each drawing shows */
T.T20 = async b => {
  await goScene(b, 'die');
  const n0 = await b.ev(`document.querySelectorAll('#chip > g.lay').length`);
  const W = await b.ev('window.__chipTest.walk()');
  const n1 = await b.ev(`document.querySelectorAll('#chip > g.lay').length`);
  const ids = new Set(W.map(s => s.id));
  ok(W.length >= 300 && ids.size >= 85 && !W.some(s => s.err), `T20 ${W.length} scenes by path (${ids.size} scales, ${W.filter(s => !s.dup).length} drawn anew), each drawn`, W.filter(s => s.err).map(s => s.path.split('/').slice(-2).join('/') + ': ' + s.err).slice(0, 3).join(' | '));
  ok(n1 === n0, `T20 the walk leaves no layer behind (${n0} before, ${n1} after)`);
  const dead = new Set(), noseat = new Set(), ext = new Set(), skip = new Set();
  let nparts = 0;
  W.forEach(s => {
    if (s.err || s.egg || FLOOR.has(s.id)) return;
    s.parts.forEach(p => {
      nparts++;
      const k = `${s.id} · ${p.key}`;
      if (p.ext) ext.add(k); else if (!p.to && !p.up) dead.add(k); else if (p.to && !p.seat) noseat.add(`${k} → ${p.to} @ ${s.shape.split('/').slice(-3).join('/')}`);
      if (TRANS.has(p.to) && !DEVICE.has(s.id) && !(s.mos >= 2 || p.mos >= 1 || SECT.has(k))) skip.add(`${k} → ${p.to}`);
    });
    s.kids.filter(x => !x.seat).forEach(x => noseat.add(`${s.id} (its own zoom) → ${x.to}`));
  });
  ok(!dead.size, `T20 every part of every scene from the rack down leads further in (${nparts} parts on ${W.filter(s => !s.egg && !FLOOR.has(s.id)).length} scenes)`, [...dead].slice(0, 8).join(' | '));
  ok([...ext].every(e => EXT.has(e)), `T20 the only part without a zoom is the die's key, a legend`, [...ext].filter(e => !EXT.has(e)).join(' | '));
  ok(!noseat.size, 'T20 in every drawing every zoom has its seat there (not only in the first drawing of a scale)', [...noseat].slice(0, 6).join(' | '));
  ok(!skip.size, 'T20 every zoom to a transistor comes from a drawing in transistors (a gate, a cell, an amplifier): no block jumps straight to the FinFET', [...skip].slice(0, 8).join(' | '));
  const E = new Map();
  W.forEach(s => { if (s.err) return; const e = E.get(s.id) || new Set(); s.parts.forEach(p => p.to && e.add(p.to)); s.kids.forEach(k => e.add(k.to)); E.set(s.id, e); });
  const reach = (from, goal) => { const seen = new Set([from]), Q = [from]; while (Q.length) { const x = Q.shift(); if (goal(x)) return true; (E.get(x) || []).forEach(t => { if (!seen.has(t)) { seen.add(t); Q.push(t); } }); } return false; };
  const noT = [], noA = [];
  E.forEach((_, id) => { if (FLOOR.has(id)) return; if (!DEVICE.has(id) && !reach(id, x => TRANS.has(x))) noT.push(id); if (!reach(id, x => ATOM.has(x))) noA.push(id); });
  ok(!noT.length, `T20 from every scale zoom-ins reach a transistor (${[...E.keys()].filter(i => !FLOOR.has(i) && !DEVICE.has(i)).length} scales above the devices)`, noT.join(' '));
  ok(!noA.length, 'T20 and an atom', noA.join(' '));
  // each transistor on its own process: the DRAM's and the regulators' never lead to the N7 FinFET
  const wrong = ['dram.cell', 'lib.dramcell', 'lib.powerfet'].filter(i => E.has(i) && reach(i, x => x === 'lib.finfet'));
  ok(!wrong.length, 'T20 a DRAM cell\'s and a power transistor\'s chains never reach the N7 FinFET', wrong.join(' '));
  const want = ['pcie.lane', 'lib.diffamp', 'lib.xbar', 'lib.round', 'lib.wire', 'p.cu', 'lib.buck', 'lib.powerfet', 'lib.strap'];
  ok(want.every(i => ids.has(i)), 'T20 the scenes part 1b added are reached by zoom-ins: ' + want.join(', '), want.filter(i => !ids.has(i)).join(' '));
};

/* T21 links (1 Oct, the owner: "make sure individual clicks like data->watts come with anchors so that I can share link to
   specific experiment"): the address follows the stage (chip-diagram.links.js) and opens it again */
T.T21 = async b => {
  const VIEWER = /^#[A-Za-z0-9_.=%&/-]*$/;   // what spacesheep's viewer mirrors into its own address
  const LET = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 0: 'J', b: 'K'};
  const NAME = {1: 'load-to-dram', 2: 'latency-ladder', 3: 'tensorsend', 4: 'relay', 5: 'gathers', 6: 'host-and-pcie', 7: 'matmul', 8: 'data-watts', 9: 'hot-line', 0: 'allreduce', b: 'broadcast'};
  // a new document each time (a navigation that changes only the fragment would not load the page again)
  const fresh = async (q, wait = 1500) => { await b.send('Page.navigate', {url: 'about:blank'}); await sleep(120); await b.load(PAGE, q, wait); await b.idle(15000); };
  const hash = () => b.ev('location.hash');
  const press = async sel => { const bx = await b.box(sel); if (!bx) return false; if (b.touch) await b.tap(bx.x, bx.y); else await b.click(bx.x, bx.y); return true; };
  const short = p => String(p).split('/').slice(-2).join('/');
  const {identifier} = await b.send('Page.addScriptToEvaluateOnNewDocument', {source: "window.__warns = []; (() => { const w = console.warn; console.warn = function (...a) { window.__warns.push(a.map(String).join(' ')); return w.apply(this, a); }; })();"});
  try {
    await fresh('');
    const D0 = (await b.state()).path;
    ok(await hash() === '' && await b.ev('window.__chipLinks.anchor()') === '', 'T21 the first view (the die) has no fragment');
    // every flow by its button: its address, and the page opened with that address plays the same flow
    for (const k of '1234567890b') {
      await fresh('');
      await press(`[data-flow="${LET[k]}"]`); await sleep(700);
      const h = await hash(), want = `#flow=${k}-${NAME[k]}`;
      ok(h === want && VIEWER.test(h), `T21 flow ${k}'s button writes ${want}`, h);
      await fresh(h);
      const s = await b.state();
      ok(s.flow === LET[k] && !s.done && await hash() === h, `T21 opened with ${want}: flow ${k} plays, the address left as it is`, JSON.stringify([s.flow, s.stage, s.done]));
    }
    // a flow's key, and the tour (its still slides, and a flow's slide, which gives the flow's own address)
    await fresh('');
    await b.key('3'); await sleep(700);
    ok(await hash() === '#flow=3-tensorsend', 'T21 the key 3 writes #flow=3-tensorsend', await hash());
    await fresh('#tour=1');
    let s = await b.state();
    ok(s.tour === 0 && await hash() === '#tour=1', 'T21 #tour=1 opens the tour', String(s.tour));
    await b.key('ArrowRight', 8); await sleep(700);
    ok(await hash() === '#tour=2', 'T21 the tour\'s next slide writes #tour=2', await hash());
    await b.key('1'); await sleep(900);
    s = await b.state();
    ok(s.tour === 6 && s.flow === 'A' && await hash() === '#flow=1-load-to-dram', 'T21 the tour\'s slide of flow 1 writes #flow=1-load-to-dram', `${s.tour} ${s.flow} ${await hash()}`);
    await fresh('#tour=2');
    s = await b.state();
    ok(s.tour === 1 && !s.flow, 'T21 #tour=2 opens the tour at its second slide', String(s.tour));
    // a flow held at a stage (paused, then stepped): &stage=, and it opens there, held; playing again drops it
    await fresh('#flow=8');
    await b.ev(`document.getElementById('btn-play').click()`); await sleep(500);
    s = await b.state();
    let h = await hash();
    ok(h === `#flow=8-data-watts&stage=${s.stage + 1}` && VIEWER.test(h), 'T21 flow 8 paused writes its stage', h);
    await b.key('ArrowRight'); await sleep(900); await b.idle(15000);
    s = await b.state(); h = await hash();
    ok(h === `#flow=8-data-watts&stage=${s.stage + 1}` && s.still, 'T21 stepped while paused: the next stage', h);
    const held = s.stage;
    await fresh(h);
    s = await b.state();
    ok(s.flow === 'H' && s.stage === held && s.still && await hash() === h, `T21 opened with ${h}: flow 8 held at stage ${held + 1}`, JSON.stringify([s.flow, s.stage, s.still]));
    await b.ev(`document.getElementById('btn-play').click()`); await sleep(700);
    ok(await hash() === '#flow=8-data-watts', 'T21 playing on drops the stage', await hash());
    // the scale the camera rests on (each reached by the Up button), and the page opened with it at the same place
    const DEEP = 'shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor';
    for (const [from, name, want] of [[DEEP + '/lib.finfet', 'a deep circuit (an XOR gate in transistors)', '#at=' + DEEP.replace(/:/g, '%3A')],
      ['host', 'the rack', '#at=rack'], ['shire:20/minion:20.1.3', 'a shire', '#at=shire%3A20'], ['rack', 'a level of the easter egg (only its own name)', '#at=studio45']]) {
      await fresh('?at=' + from);
      await b.ev(`document.getElementById('up').click()`); await sleep(80); await b.idle(15000); await sleep(900);
      s = await b.state(); h = await hash();
      ok(h === want && VIEWER.test(h), `T21 ${name}: the camera at rest writes ${want}`, `${h} at ${short(s.path)}`);
      await fresh(h);
      const s2 = await b.state();
      ok(s2.path === s.path && await hash() === h, `T21 ${name}: opened with it, the same place`, short(s2.path));
    }
    // the fragment changed (the viewer forwards the outer address's): the stage goes there, the camera by a move
    await fresh('');
    const moveTo = async (frag, cond, what) => {
      await b.ev(`location.hash = ${JSON.stringify(frag)}`);
      let moved = false;
      for (let i = 0; i < 30 && !moved; i++) { await sleep(40); moved = (await b.state()).zooming; }
      await b.idle(15000); await sleep(300);
      const st = await b.state();
      ok(cond(st, moved), `T21 a hashchange to ${frag}: ${what}`, JSON.stringify({at: short(st.path), flow: st.flow, tour: st.tour, moved}));
    };
    await moveTo('#at=shire%3A9', (st, mv) => mv && st.path === D0 + '/shire:9', 'the camera moves there (a move, not a cut)');
    await moveTo('#flow=3', st => st.flow === 'C' && !st.done, 'flow 3 plays');
    await moveTo('#tour=4', st => st.tour === 3 && !st.flow, 'the tour, at its fourth slide');
    await moveTo('#at=rack', (st, mv) => mv && st.tour == null && !st.flow && st.node === 'rack', 'the tour ends, the camera moves to the rack');
    ok(await hash() === '#at=rack', 'T21 after a hashchange the address is left as it is', await hash());
    // fragments that name nothing: a console warning, the first view, and the address says what is shown
    const nerr = b.errs.length;
    for (const f of ['#flow=zz', '#at=no/such/scale', '#tour=99', '#at=shire%3A99', '#stage=2']) {
      await fresh(f); await sleep(500);
      s = await b.state();
      const w = await b.ev('window.__warns.length');
      ok(!s.flow && s.tour == null && s.path === D0 && w > 0 && await hash() === '', `T21 ${f}: a warning, the first view, the address cleared`, JSON.stringify({flow: s.flow, tour: s.tour, at: short(s.path), warns: w, hash: await hash()}));
    }
    await fresh('#flow=8&stage=99'); await sleep(500);
    s = await b.state();
    ok(s.flow === 'H' && !s.still && await b.ev('window.__warns.length') > 0 && await hash() === '#flow=8-data-watts', 'T21 #flow=8&stage=99: a warning, flow 8 from its start, the address corrected', JSON.stringify([s.flow, s.stage, await hash()]));
    await moveTo('#at=nowhere', (st) => st.path === D0 && !st.flow, 'a warning, back to the first view');
    ok(b.errs.length === nerr, 'T21 no error from any of them', b.errs.slice(nerr).join(' | '));
    // #facts (the page's own anchor) still opens the facts table, and is left alone
    await fresh('#facts'); await sleep(800);
    const facts = await b.ev(`document.querySelectorAll('#facttab tbody tr').length`);
    ok(await hash() === '#facts' && facts > 100 && await b.ev('window.__warns.length') === 0, 'T21 #facts opens the facts table and stays', `${await hash()} ${facts} rows`);
    // Copy link: a mocked clipboard (headless Chrome may refuse the real one); the keyboard; the hosts; the fallback
    await fresh('#flow=8');
    const mock = good => `(() => { window.__copied = null; Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {writeText: t => ${good ? '(window.__copied = t, Promise.resolve())' : 'Promise.reject(new Error("blocked by the frame"))'}}}); ${good ? '' : 'document.execCommand = () => false;'} return true; })()`;
    await b.ev(mock(true));
    await b.ev(`document.getElementById('btn-link').scrollIntoView({block: 'center'})`); await sleep(200);
    const lay = await b.ev(`(() => { const r = document.getElementById('btn-link').getBoundingClientRect(); return {l: Math.round(r.left), r: Math.round(r.right), h: Math.round(r.height), iw: innerWidth, sw: document.documentElement.scrollWidth}; })()`);
    ok(lay.l >= 0 && lay.r <= lay.iw && lay.h >= 28 && lay.sw <= lay.iw, `T21 Copy link shows, inside the window (${b.W} px wide)`, JSON.stringify(lay));
    await press('#btn-link'); await sleep(400);
    let c = await b.ev(`({copied: window.__copied, href: location.href, label: document.getElementById('btn-link').textContent})`);
    const base = c.href.split('#')[0], want8 = base + '#flow=8-data-watts';
    ok(c.copied === want8 && c.label === 'Copied', 'T21 Copy link copies the address of what is shown and says "Copied"', JSON.stringify(c));
    await b.ev(`(window.__copied = null, document.getElementById('btn-link').focus(), true)`); await b.key('Enter'); await sleep(400);
    ok(await b.ev('window.__copied') === want8, 'T21 Copy link from the keyboard (Enter)', await b.ev('window.__copied'));
    const u1 = await b.ev(`window.__chipLinks.url('6cfdea5c-a598-438e-bd1a-613093ede523.spacesheep.app')`), u2 = await b.ev(`window.__chipLinks.url('yaroslavvb.github.io')`);
    ok(u1 === 'https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram#flow=8-data-watts', 'T21 on spacesheep the link is the viewer\'s address', u1);
    ok(u2 === want8, 'T21 on GitHub Pages (or any other host) it is the page\'s own address', u2);
    await b.ev(mock(false));
    await b.ev(`document.activeElement && document.activeElement.blur && document.activeElement.blur()`);
    await press('#btn-link'); await sleep(400);
    c = await b.ev(`(() => { const p = document.querySelector('.lnk-pop'), i = document.getElementById('lnk-in'); if (!p || !i) return null; const r = p.getBoundingClientRect();
      return {shown: !p.hidden && r.width > 0, value: i.value, focus: document.activeElement === i, sel: [i.selectionStart, i.selectionEnd], say: p.querySelector('label').textContent, l: Math.round(r.left), r: Math.round(r.right), iw: innerWidth}; })()`);
    ok(!!c && c.shown && c.value === want8 && c.focus && c.sel[0] === 0 && c.sel[1] === want8.length && (b.touch ? /press and hold/.test(c.say) : /^Copy with (Ctrl|⌘)-C$/.test(c.say)) && c.l >= 0 && c.r <= c.iw,
      'T21 the clipboard forbidden: the link shown selected, with how to copy it, inside the window', JSON.stringify(c));
    await b.key('Escape'); await sleep(200);
    c = await b.ev(`({hidden: document.querySelector('.lnk-pop').hidden, focus: document.activeElement && document.activeElement.id, flow: window.__chipState().flow})`);
    ok(c.hidden && c.focus === 'btn-link' && c.flow === 'H', 'T21 Escape closes it, the focus back on Copy link (the flow plays on)', JSON.stringify(c));
    // reduced motion: an address opens at once, and a hashchange is a cut
    const r = await open(b.touch ? {w: 390, h: 844, dpr: 3, touch: true, reduced: true} : {w: 1280, h: 800, dpr: 1, reduced: true});
    try {
      await r.load(PAGE, '#at=shire%3A5', 1500);
      let rs = await r.state();
      ok(rs.path === D0 + '/shire:5' && !rs.zooming, 'T21 reduced motion: #at=shire%3A5 opens there', short(rs.path));
      await r.ev(`location.hash = '#at=rack'`); await sleep(120);
      rs = await r.state();
      ok(rs.node === 'rack' && !rs.zooming && await r.ev('location.hash') === '#at=rack', 'T21 reduced motion: a hashchange is a cut', short(rs.path));
      ok(!r.errs.length, 'T21 reduced motion: no console errors', r.errs.slice(0, 3).join(' | '));
    } finally { await r.close(); }
    // in a frame (as spacesheep's viewer shows it; the page on a server): each new fragment posted to the parent as
    // ss-hash, nothing else; the viewer's forward (the frame's src with a new fragment) moves the camera, no reload
    if (/^https?:/.test(PAGE)) {
      // (the viewer stands in a document of the page's own origin, one of its images: the frame's state can be read)
      await b.send('Page.navigate', {url: new URL('ladder-img/milkyway.webp', PAGE).href}); await sleep(400);
      await b.ev(`(() => { document.documentElement.innerHTML = '<head></head><body style="margin:0"></body>'; window.__msgs = []; addEventListener('message', e => window.__msgs.push(e.data));
        const f = document.createElement('iframe'); f.id = 'fr'; f.style.cssText = 'border:0;display:block;width:${b.W}px;height:${b.H}px'; f.src = ${JSON.stringify(PAGE)}; document.body.appendChild(f); return true; })()`);
      const F = `document.getElementById('fr').contentWindow`;
      const fidle = async () => { for (let i = 0; i < 150; i++) { await sleep(100); if (await b.ev(`!!(${F}.__chipState) && !${F}.__chipState().zooming`)) return; } };
      for (let i = 0; i < 80; i++) { await sleep(100); if (await b.ev(`!!(${F}.__chipState)`)) break; }
      await fidle(); await sleep(400);
      const fb = await b.ev(`(() => { const e = ${F}.document.querySelector('[data-flow="H"]'), q = e.getBoundingClientRect(), f = document.getElementById('fr').getBoundingClientRect(); return {x: f.left + q.left + q.width / 2, y: f.top + q.top + q.height / 2}; })()`);
      if (b.touch) await b.tap(fb.x, fb.y); else await b.click(fb.x, fb.y);
      await sleep(800);
      let m = await b.ev('window.__msgs');
      ok(m.some(x => x && x.type === 'ss-hash' && x.hash === '#flow=8-data-watts'), 'T21 framed: flow 8\'s button posts #flow=8-data-watts to the viewer', JSON.stringify(m));
      await b.ev(`(() => { const f = document.getElementById('fr'); f.contentWindow.__t21 = 1; f.src = f.src.split('#')[0] + '#at=shire%3A9'; return true; })()`);
      let moved = false;
      for (let i = 0; i < 40 && !moved; i++) { await sleep(40); moved = await b.ev(`${F}.__chipState().zooming`); }
      await fidle(); await sleep(300);
      const fs = await b.ev(`({mark: ${F}.__t21, path: ${F}.__chipState().path, flow: ${F}.__chipState().flow})`);
      ok(fs.mark === 1 && moved && fs.path === D0 + '/shire:9' && !fs.flow, 'T21 framed: the viewer\'s forward of #at=shire%3A9 stops the flow and moves the camera there (no reload)', JSON.stringify({mark: fs.mark, moved, at: short(fs.path), flow: fs.flow}));
      await b.ev(`${F}.document.getElementById('up').click()`); await sleep(100); await fidle(); await sleep(900);
      m = await b.ev('window.__msgs');
      ok(m.length && m[m.length - 1].hash === '#', 'T21 framed: back at the die (the first view), the viewer is told to clear its fragment', JSON.stringify(m.slice(-2)));
      ok(m.every(x => x && x.type === 'ss-hash' && Object.keys(x).length === 2 && VIEWER.test(x.hash)), `T21 framed: nothing but ss-hash is posted, each a fragment the viewer mirrors (${m.length} messages)`, JSON.stringify(m.slice(0, 8)));
    } else console.log('  (T21 framed: skipped, the page is not on a server)');
  } finally { await b.send('Page.removeScriptToEvaluateOnNewDocument', {identifier}); }
};

T.T22 = async b => {
  const fresh = async (q, wait = 1500) => { await b.send('Page.navigate', {url: 'about:blank'}); await sleep(120); await b.load(PAGE, q, wait); await b.idle(15000); };
  const hash = () => b.ev('location.hash');
  // a real click (a tap on the phone) on a control, scrolled into view first
  const press = async sel => {
    await b.ev(`(() => { const e = document.querySelector(${JSON.stringify(sel)}), r = e.getBoundingClientRect(); if (r.top < 60 || r.bottom > innerHeight - 60) e.scrollIntoView({block: 'center'}); return true; })()`); await sleep(150);
    const bx = await b.box(sel); if (!bx) return false; if (b.touch) await b.tap(bx.x, bx.y); else await b.click(bx.x, bx.y); return true;
  };
  // the clock's pace: its milliseconds per millisecond of the reader's time
  const pace = async (r = b, ms = 900) => { const a = await r.ev('[window.__chipState().clock, performance.now()]'); await sleep(ms); const c = await r.ev('[window.__chipState().clock, performance.now()]'); return +((c[0] - a[0]) / (c[1] - a[1])).toFixed(2); };
  const near = (v, w, tol = 0.2) => Math.abs(v - w) <= tol;
  const untilSt = async (cond, max = 30000) => { const t0 = Date.now(); let s = await b.state(); while (!cond(s) && Date.now() - t0 < max) { await sleep(80); s = await b.state(); } return s; };
  const want = () => b.ev('window.__chipTest.want()');
  const {identifier} = await b.send('Page.addScriptToEvaluateOnNewDocument', {source: "window.__warns = []; (() => { const w = console.warn; console.warn = function (...a) { window.__warns.push(a.map(String).join(' ')); return w.apply(this, a); }; })();"});
  try {
    // the button: right of Play (Pause while a flow plays), on its row with the arrows, Follow and Tour, in the window
    const geo = () => b.ev(`(() => { const s = document.getElementById('btn-speed'), p = document.getElementById('btn-play'), r = s.getBoundingClientRect(), q = p.getBoundingClientRect();
      return {text: s.textContent, play: p.textContent, label: s.getAttribute('aria-label'), next: p.nextElementSibling === s, gap: Math.round(r.left - q.right), w: Math.round(r.width), h: Math.round(r.height), l: Math.round(r.left), r: Math.round(r.right),
        rows: ['btn-play', 'btn-speed', 'btn-prev', 'btn-next', 'btn-follow', 'btn-tour'].map(id => Math.round(document.getElementById(id).getBoundingClientRect().top)), iw: innerWidth, sw: document.documentElement.scrollWidth}; })()`);
    const placed = g => g.next && g.gap >= 0 && g.gap <= 12 && g.w >= 28 && g.h >= 28 && g.l >= 0 && g.r <= g.iw && g.sw <= g.iw && Math.max(...g.rows) - Math.min(...g.rows) <= 2;
    await fresh('');
    let g = await geo();
    ok(placed(g) && g.text === '1×' && g.label === 'Speed 1×, press for 2× (S)', `T22 the speed button: 1× beside Play, on the playback row (${b.W} px wide)`, JSON.stringify(g));
    await press('[data-flow="H"]'); await sleep(900);
    g = await geo();
    ok(placed(g) && g.play === 'Pause', 'T22 beside Pause while flow 8 plays, the row unwrapped', JSON.stringify(g));
    ok(near(await pace(), 1, 0.15), 'T22 at 1x the clock keeps the reader\'s time');
    await press('#btn-speed'); await sleep(300);
    let s = await b.state(); g = await geo();
    ok(s.rate === 2 && g.text === '2×' && g.label === 'Speed 2×, press for 1× (S)' && placed(g) && await hash() === '#flow=8-data-watts&speed=2', 'T22 a press: 2×, and the address says &speed=2', JSON.stringify([s.rate, g.text, await hash()]));
    const p2 = await pace();
    ok(near(p2, 2, 0.25), 'T22 at 2x the clock runs twice as fast', String(p2));
    await b.key('s'); await sleep(300);
    s = await b.state();
    ok(s.rate === 1 && await b.ev(`document.getElementById('btn-speed').textContent`) === '1×' && await hash() === '#flow=8-data-watts', 'T22 S: back to 1×, the address without it', JSON.stringify([s.rate, await hash()]));
    await b.key('S'); await sleep(200);
    ok((await b.state()).rate === 2, 'T22 S again: 2×');

    // flow 8 whole at 1x and at 2x (the speed set before it starts): the same stages in the same order, in about half the time
    const run8 = async () => {
      await b.ev(`(() => { const L = window.__t22 = {st: [], done: 0}; const live = document.getElementById('st-live'), play = document.getElementById('btn-play');
        new MutationObserver(() => { const t = live.textContent; if (/^Stage /.test(t) && (!L.st.length || L.st[L.st.length - 1][1] !== t)) L.st.push([performance.now(), t]); }).observe(live, {childList: true, characterData: true, subtree: true});
        new MutationObserver(() => { if (play.textContent === 'Replay' && !L.done) L.done = performance.now(); }).observe(play, {childList: true, characterData: true, subtree: true});
        return true; })()`);
      await b.key('8');
      for (let i = 0; i < 1200 && !await b.ev('window.__t22.done'); i++) await sleep(100);
      const L = await b.ev('window.__t22');
      return {ms: L.done && L.st.length ? L.done - L.st[0][0] : NaN, st: L.st.map(x => x[1]), per: L.st.map((x, i) => Math.round((i + 1 < L.st.length ? L.st[i + 1][0] : L.done) - x[0]))};
    };
    await fresh('');
    const r1 = await run8();
    await fresh('');
    await b.key('s'); await sleep(200);
    const r2 = await run8();
    const ratio = r2.ms / r1.ms;
    ok(r1.st.length === 7 && JSON.stringify(r1.st) === JSON.stringify(r2.st), 'T22 flow 8 at 2x plays the same seven stages in the same order', `${r1.st.length} and ${r2.st.length} stages`);
    ok(ratio >= 0.42 && ratio <= 0.6, `T22 flow 8 at 2x takes about half the time of 1x (${(r2.ms / 1000).toFixed(1)} s against ${(r1.ms / 1000).toFixed(1)} s, ${ratio.toFixed(2)})`, `per stage ${JSON.stringify(r1.per)} | ${JSON.stringify(r2.per)}`);

    // opened at 2x; paused (the address holds its stage and its speed); the arrows step, while paused; Play goes on at 2x
    await fresh('#flow=8-data-watts&speed=2');
    s = await b.state();
    ok(s.flow === 'H' && !s.done && s.rate === 2 && await b.ev(`document.getElementById('btn-speed').textContent`) === '2×' && await hash() === '#flow=8-data-watts&speed=2', 'T22 opened with #flow=8-data-watts&speed=2: flow 8 plays at 2×, the address left as it is', JSON.stringify([s.flow, s.rate, await hash()]));
    await b.ev(`document.getElementById('btn-play').click()`); await sleep(400);
    s = await b.state();
    const held = s.stage, c0 = s.clock;
    await sleep(500);
    ok(!s.clockOn && (await b.state()).clock === c0 && await hash() === `#flow=8-data-watts&stage=${held + 1}&speed=2`, 'T22 paused at 2x: the clock stops, the address holds the stage and the speed', await hash());
    await b.key('ArrowRight'); await sleep(300); await b.idle(15000);
    s = await b.state();
    ok(s.stage === held + 1 && s.still && s.rate === 2 && s.path === await want() && await hash() === `#flow=8-data-watts&stage=${held + 2}&speed=2`, 'T22 Right while paused at 2x: the next stage, held, where it wants the camera', JSON.stringify([s.stage, s.still, await hash()]));
    await b.key('ArrowLeft'); await sleep(300); await b.idle(15000);
    s = await b.state();
    ok(s.stage === held && s.still && s.path === await want(), 'T22 Left: back a stage, held', JSON.stringify([s.stage, s.still]));
    await b.ev(`document.getElementById('btn-play').click()`); await sleep(200);
    s = await b.state();
    const pp = await pace();
    ok(s.clockOn && !s.still && s.stage === held + 1 && near(pp, 2, 0.25) && await hash() === '#flow=8-data-watts&speed=2', 'T22 Play goes on to the next stage at 2x', JSON.stringify([s.stage, pp, await hash()]));
    // the stages from where flow 8 enters a minion: every one lands where it wants the camera, stepped while playing at 2x
    s = await untilSt(x => x.stage >= 3 && !x.zooming, 20000);
    let good = 0, tot = 0;
    for (let i = s.stage; i < 7; i++) {
      if (i > s.stage) { await b.key('ArrowRight'); await sleep(150); await b.idle(15000); }
      const st = await b.state(); tot++;
      if (st.stage === i && st.path === await want()) good++; else console.log(`  flow 8 stage ${i + 1} at 2x: at ${st.path} (stage ${st.stage + 1}), wants ${await want()}`);
    }
    ok(tot >= 3 && good === tot, `T22 at 2x every stage stepped to lands where it wants the camera (${good}/${tot})`);

    // switching mid-flow: 1x to 2x and back while flow 8 plays, and in the middle of its camera's move into a minion
    await fresh('#flow=8');
    await sleep(400);
    const q1 = await pace();
    await press('#btn-speed'); await sleep(100);
    const q2 = await pace();
    s = await b.state();
    const st0 = s.stage;
    s = await untilSt(x => x.stage > st0, 6000);
    ok(near(q1, 1, 0.15) && near(q2, 2, 0.25) && s.stage === st0 + 1 && s.rate === 2, 'T22 switched to 2x mid-flow: the clock doubles at once, the flow goes on to its next stage', JSON.stringify({q1, q2, from: st0, now: s.stage}));
    await b.key('s'); await sleep(100);
    const q3 = await pace();
    ok(near(q3, 1, 0.15) && (await b.state()).flow === 'H' && await hash() === '#flow=8-data-watts', 'T22 and back to 1x mid-flow', JSON.stringify({q3, hash: await hash()}));
    await fresh('#flow=8-data-watts&stage=3');
    await b.ev(`document.getElementById('btn-play').click()`);
    let moving = false;
    for (let i = 0; i < 40 && !moving; i++) { await sleep(25); moving = (await b.state()).zooming; }
    await sleep(250);
    await b.key('s');
    await b.idle(15000); await sleep(200);
    s = await b.state();
    ok(moving && s.stage === 3 && s.rate === 2 && s.path === await want() && s.clockOn, 'T22 switched during the camera\'s move into a minion: it lands where the stage wants it, and plays on at 2x', JSON.stringify({moving, stage: s.stage, at: s.path.split('/').slice(-2).join('/')}));

    // Follow at 2x: off, the stage plays without moving the camera; on again, the camera goes to it
    await fresh('#flow=8-data-watts&stage=3&speed=2');
    await b.key('c'); await sleep(100);
    await b.ev(`document.getElementById('btn-play').click()`); await sleep(700);
    s = await b.state();
    const die = s.path;
    ok(!s.follow && s.stage === 3 && !s.zooming && s.path.endsWith('/die') && s.rate === 2, 'T22 Follow off at 2x: the stage in a minion plays, the camera stays on the die', JSON.stringify({follow: s.follow, stage: s.stage, at: s.path.split('/').slice(-1)[0]}));
    await b.key('c'); await sleep(200); await b.idle(15000);
    s = await b.state();
    ok(s.follow && s.stage === 3 && s.path !== die && s.path === await want(), 'T22 Follow on again: the camera goes to the stage', s.path.split('/').slice(-2).join('/'));

    // the tour at 2x: its address, its slides, a flow's slide
    await fresh('#tour=1&speed=2');
    s = await b.state();
    ok(s.tour === 0 && s.rate === 2 && await hash() === '#tour=1&speed=2', 'T22 #tour=1&speed=2 opens the tour at 2x', JSON.stringify([s.tour, s.rate, await hash()]));
    for (let i = 0; i < 4; i++) { await b.key('ArrowRight', 8); await sleep(150); await b.idle(15000); }
    s = await b.state();
    ok(s.tour === 4 && !s.zooming && await hash() === '#tour=5&speed=2', 'T22 the tour steps its slides at 2x, the address with them', JSON.stringify([s.tour, await hash()]));
    await b.key('8'); await sleep(600); await b.idle(15000);
    s = await b.state();
    ok(s.flow === 'H' && s.tour != null && s.rate === 2 && await hash() === '#flow=8-data-watts&speed=2' && near(await pace(), 2, 0.25), 'T22 the tour\'s slide of flow 8 plays at 2x', JSON.stringify([s.tour, s.flow, await hash()]));

    // the address: without &speed= 1x; held at a stage; a hashchange that changes only the speed; a bad speed
    await fresh('#flow=8-data-watts');
    ok((await b.state()).rate === 1 && await b.ev(`document.getElementById('btn-speed').textContent`) === '1×', 'T22 #flow=8-data-watts (no speed) opens at 1x');
    await fresh('#flow=8-data-watts&stage=3&speed=2');
    s = await b.state();
    ok(s.flow === 'H' && s.stage === 2 && s.still && s.rate === 2 && await hash() === '#flow=8-data-watts&stage=3&speed=2', 'T22 #flow=8-data-watts&stage=3&speed=2 opens held at stage 3, at 2x', JSON.stringify([s.stage, s.still, s.rate]));
    await fresh('#flow=8-data-watts');
    s = await untilSt(x => x.stage >= 1, 8000);
    const before = s.stage;
    await b.ev(`location.hash = '#flow=8-data-watts&speed=2'`); await sleep(400);
    s = await b.state();
    ok(s.rate === 2 && s.flow === 'H' && s.stage >= before && await hash() === '#flow=8-data-watts&speed=2', 'T22 a hashchange adding &speed=2: 2x, and the flow goes on (not restarted)', JSON.stringify({before, now: s.stage, rate: s.rate}));
    const nerr = b.errs.length;
    await fresh('#flow=8&speed=7'); await sleep(400);
    s = await b.state();
    ok(s.flow === 'H' && s.rate === 1 && await b.ev('window.__warns.length') > 0 && await hash() === '#flow=8-data-watts' && b.errs.length === nerr, 'T22 #flow=8&speed=7: a warning, flow 8 at 1x, the address corrected', JSON.stringify([s.rate, await hash()]));

    // reduced motion at 2x: nothing animates (the camera cuts), and the stages advance on their own twice as fast
    const r = await open(b.touch ? {w: 390, h: 844, dpr: 3, touch: true, reduced: true} : {w: 1280, h: 800, dpr: 1, reduced: true});
    try {
      await r.load(PAGE, '#flow=8-data-watts&stage=3&speed=2', 1500);
      let rs = await r.state();
      ok(rs.rate === 2 && rs.stage === 2 && rs.still, 'T22 reduced motion: #flow=8-data-watts&stage=3&speed=2 opens held, at 2x', JSON.stringify([rs.rate, rs.stage]));
      await r.ev(`document.getElementById('btn-play').click()`);
      const t0 = Date.now(); await sleep(120);
      rs = await r.state();
      ok(rs.stage === 3 && !rs.zooming && rs.path === await r.ev('window.__chipTest.want()'), 'T22 reduced motion at 2x: the camera cuts to the stage in a minion', rs.path.split('/').slice(-2).join('/'));
      let n = rs.stage;
      while (n === 3 && Date.now() - t0 < 15000) { await sleep(50); n = (await r.state()).stage; }
      const adv = Date.now() - t0, rp = await pace(r);
      // (stage 4 under reduced motion: its three phases wait 0.7 s each, then it holds 2.3 s: 4.4 s of the clock, 2.2 s at 2x)
      ok(near(rp, 2, 0.25) && n === 4 && adv > 1600 && adv < 3200, `T22 reduced motion at 2x: the clock at 2x, and stage 4 gives way to stage 5 on its own after ${(adv / 1000).toFixed(1)} s (4.4 at 1x)`, JSON.stringify({pace: rp, stage: n}));
      ok(!r.errs.length, 'T22 reduced motion: no console errors', r.errs.slice(0, 3).join(' | '));
    } finally { await r.close(); }
  } finally { await b.send('Page.removeScriptToEvaluateOnNewDocument', {identifier}); }
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
