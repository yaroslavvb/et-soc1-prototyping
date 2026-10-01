// node zoom_test.mjs PAGE [--phone] [--only=T1,T4] [--scenes=a,b] : the chip diagram's zoom and navigation tests
// (DESIGN §6.2), driven with real input events over the DevTools protocol (cdp.mjs). Desktop 1280 x 800 with a mouse;
// --phone: 390 x 844, touch emulation, DPR 3. Each test prints PASS or FAIL lines; the exit code is the number of
// failures. The page's hooks: window.__chipState() (where the camera is) and window.__chipTest (the parts of the scale
// shown and what each zooms into, the stage a flow wants shown).
//   T1 every part: a double-click (double-tap) on one part of each kind, in each scene, enters its own scale (or, for
//      a part with none, selects it and shows the panel's zoom row); then the Up button comes back
//   T2 a click (tap) selects and never moves the camera; on touch the pill shows
//   T3 Up from the deepest default scale to the top, one level a press; the breadcrumb back down; the "…" menu
//   T4 a shire's edge links, by click (tap), Enter and the arrow keys; a glide between shires
//   T5 the dive: + from the top of the ladder to the bottom of the default chain, every step arriving, the readout
//      monotone, every visible layer's scale within [1/30, 30]; then one breadcrumb click back to the chip
//   T6 the flows: every stage of every flow lands where it wants the camera
//   T7 reduced motion: a zoom is a cut
//   T11 accessibility: every part's label says what Enter does; the Up button and the crumbs have names; the scale is
//      announced on arrival
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
    if (s.upDisabled) break;
    const parent = s.path.split('/').slice(0, -1);
    await b.ev(`document.getElementById('up').click()`); await sleep(40); await b.idle(15000);
    const s2 = await b.state();
    if (!ok(s2.path === parent.join('/'), `T3 Up ${n + 1}: to ${parent[parent.length - 1]}`, s2.path)) break;
  }
  ok(n === depth, `T3 Up pressed ${n} times for a depth of ${depth}`);
  s = await b.state();
  ok(s.upDisabled && /Top of the ladder/.test(s.up), 'T3 at the top the button is disabled and says so', s.up);
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
  // the "…" menu: every folded ancestor is reachable
  const fold = await b.ev(`(() => { const m = document.querySelector('#crumbs .more'); if (!m) return null; m.click(); const it = [...document.querySelectorAll('#crumb-menu button')].map(x => x.textContent); return it; })()`);
  if (fold) ok(fold.length > 0, `T3 the "…" menu lists ${fold.length} levels`, fold.join(' | '));
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
  let prevM = null, mono = true, bad = [], steps = 0;
  for (let i = 0; i < deep.length - 1; i++) {
    await b.key('+');
    // sample every visible layer's scale while the camera moves
    for (let j = 0; j < 400; j++) { const st = await b.state(); st.visible.forEach(v => { if (v.k > 30 || v.k < 1 / 30) bad.push(`${st.path}:${v.node}:${v.k.toFixed(3)}`); }); if (!st.zooming && j > 1) break; await sleep(16); }
    await b.idle(15000);
    s = await b.state();
    const want = deep.slice(0, i + 2).join('/');
    if (!ok(s.path === want, `T5 + ${i + 1}: ${deep[i + 1]}`, s.path)) break;
    steps++;
    if (prevM != null && s.scale_m != null && !(s.scale_m < prevM)) mono = false;
    if (s.scale_m != null) prevM = s.scale_m;
  }
  ok(steps === deep.length - 1, `T5 every step arrived (${steps})`);
  ok(mono, 'T5 the scale falls at every step');
  ok(!bad.length, 'T5 every visible layer within [1/30, 30]', bad.slice(0, 5).join(' '));
  const t0 = Date.now();
  const ci = await b.ev(`(() => { const c = [...document.querySelectorAll('#crumbs button')].find(x => x.textContent === 'Chip'); if (c) { c.click(); return 1; } const m = document.querySelector('#crumbs .more'); if (!m) return 0; m.click(); const it = [...document.querySelectorAll('#crumb-menu button')].find(x => /^The chip/.test(x.textContent)); if (it) { it.click(); return 2; } return 0; })()`);
  await sleep(60); await b.idle(15000);
  s = await b.state();
  ok(ci && s.node === 'die' && Date.now() - t0 < 6500, `T5 one breadcrumb click back to the chip (${Date.now() - t0} ms)`, s.path);
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
  for (const q of ['?at=sf', '?at=' + (await b.ev('window.__chipTest.defPath()')).split('/').slice(18).join('/')]) {
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
    ok(!r.errs.length, 'T7 no console errors', r.errs.slice(0, 3).join(' | '));
  } finally { await r.close(); }
};

/* T9 (the part run in a browser): with the images folder missing, a photo level loads with no script error and says
   "photo not loaded"; with it, the images load (zoom_static.py checks sizes, the manifest and privacy) */
T.T9 = async b => {
  const { mkdtempSync, copyFileSync } = await import('node:fs');
  const { resolve, join } = await import('node:path');
  const d = mkdtempSync(resolve(process.env.ZT_TMP || '/home/yaroslavvb/claude/work/chipzoom/tests', 'noimg-'));
  copyFileSync(PAGE, join(d, 'page.html'));
  const n0 = b.errs.length;
  await b.load(join(d, 'page.html'), '?at=rack', 2500); await b.idle(10000); await sleep(600);
  const said = await b.ev(`[...document.querySelectorAll('#chip .lay text')].some(t => t.textContent === 'photo not loaded' && t.getClientRects().length)`);
  const exc = b.errs.slice(n0).filter(e => /^EXC|^console\.error/.test(e));
  ok(said, 'T9 no images folder: the rack says "photo not loaded"');
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
