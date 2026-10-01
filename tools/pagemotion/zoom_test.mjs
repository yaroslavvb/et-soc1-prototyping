// node zoom_test.mjs PAGE [--phone] [--only=T1,T4] [--scenes=a,b] : the chip diagram's zoom and navigation tests
// (DESIGN §6.2), driven with real input events over the DevTools protocol (cdp.mjs). Desktop 1280 x 800 with a mouse;
// --phone: 390 x 844, touch emulation, DPR 3. Each test prints PASS or FAIL lines; the exit code is the number of
// failures. The page's hooks: window.__chipState() (where the camera is) and window.__chipTest (the parts of the scale
// shown and what each zooms into, the stage a flow wants shown).
//   T1 every part: a double-click (double-tap) on one part of each kind, in each scene, enters its own scale (or, for
//      a part with none, selects it and shows the panel's zoom row); then the Up button comes back
//   T2 a click (tap) selects and never moves the camera; on touch the pill shows
//   T3 Up from the deepest default scale (since 1 Oct the Planck length) to the top, one level a press; then round the
//      ring of sizes (the wrap) and in again at the Planck length; the breadcrumb back down; the "…" menu
//   T4 a shire's edge links, by click (tap), Enter and the arrow keys; a glide between shires
//   T5 the dive: + from the top of the ladder to the bottom of the default chain (the Planck length), every step
//      arriving, the readout monotone, every visible layer's scale within [1/30, 30]; then + round the ring back to the
//      top; then one breadcrumb click back to the chip
//   T6 the flows: every stage of every flow lands where it wants the camera
//   T7 reduced motion: a zoom is a cut
//   T11 accessibility: every part's label says what Enter does; the Up button and the crumbs have names; the scale is
//      announced on arrival
//   T12 the wrap: the ring's two ways back in, Up taking the compute gate first and the memory cell the next time
//      round; each lands at the Planck length of its branch and Up climbs that branch
//   T14 the easter egg (the owner, 1 Oct 07:25): no level above the rack is named in the page's text, the breadcrumb,
//      the Up button or the panel at the rack or below; pressing Up from the rack still reaches them
//   T15 the two-state electronics: G, the drawing's switch and the panel's button switch the state; it holds from the
//      fin into the channel; switching runs no script per frame
//   T16 the dive by double-clicks (a double-tap on a phone): from the die, each scale's part for the next scale of the
//      default chain, down to a quark
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
      const p = list.find(q => q.kid) ? list.filter(q => q.kid)[Math.floor(list.filter(q => q.kid).length / 2)] : list[0];
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
  ok(s.node === 'p.planck', 'T3 Up from the ring: in at the Planck length', s.path.split('/').slice(-3).join('/'));
  // and up again to the die: 19 presses through the compute gate
  let m = 0; for (; m < 30 && s.node !== 'die'; m++) { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); s = await b.state(); }
  ok(s.node === 'die' && m === 19, `T3 from the Planck length up to the die: ${m} presses (19 by the compute gate)`, s.path.split('/').slice(-2).join('/'));
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
  ok(xs.length === 2 && xs.every(x => /p\.planck$/.test(x.path)), 'T12 the ring has two ways back in, each to a Planck length', xs.map(x => x.id).join(', '));
  const parts = (await b.ev('window.__chipTest.parts()')).filter(p => /^exit-/.test(p.key));
  ok(parts.length === (b.touch ? 0 : 2), `T12 the ways back in are parts of the drawing${b.touch ? ' (a phone: in the panel)' : ''}`, parts.map(p => p.label).join(' | '));
  const pb = await b.ev(`[...document.querySelectorAll('#pn-body .pn-zoom button')].map(x => x.textContent)`);
  ok(pb.filter(t => /^Through /.test(t)).length === 2, 'T12 the panel offers both ways back in', pb.join(' | '));
  ok(await b.ev('window.__chipTest.upExit()') === 'compute', 'T12 Up takes the compute gate first');
  const up = async () => { await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000); return b.state(); };
  const climb = async n => { const seen = []; for (let i = 0; i < n; i++) seen.push((await up()).node); return seen; };
  s = await up();
  ok(s.path === xs[0].path, 'T12 Up from the ring lands on the compute branch\'s Planck length', s.path.split('/').slice(-4).join('/'));
  // + at the Planck length goes round the ring again; Up then takes the other way in
  await b.key('+'); await sleep(40); await b.idle(15000); s = await b.state();
  ok(s.path === 'p.wrap' && await b.ev('window.__chipTest.upExit()') === 'memory', 'T12 the next time round, Up takes the memory cell', s.path);
  s = await up();
  ok(s.path === xs[1].path, 'T12 Up from the ring lands on the memory branch\'s Planck length', s.path.split('/').slice(-4).join('/'));
  let seen = await climb(9);
  ok(seen[8] === 'lib.sram6t' && seen.includes('lib.finfet'), 'T12 Up climbs the memory branch: the FinFET, then the 6T cell', seen.join(' '));
  await goScene(b, 'p.wrap'); await up(); seen = await climb(9);
  ok(seen[8] === 'lib.xor', 'T12 Up climbs the compute branch: the FinFET, then the XOR gate', seen.join(' '));
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
