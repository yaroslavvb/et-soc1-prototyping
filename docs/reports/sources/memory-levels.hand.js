/* ================= memory-levels.hand.js: the two cameras hand over, one Up bar for both (1 October 2026) =================
   Part of memory-levels.ladder.js's scope (its last include). ON: the path camera holds the stage (its SVG shown, the
   levels' hidden); else the levels' own camera does, and the Up bar, the breadcrumb and the readout show its place as a
   path (sync). Every move a reader asks of the ladder (the Up bar, a crumb, the "…" menu, + and −, a panel's zoom
   button, a part of the ladder's scenes, the ring's ways in) comes through pageNav (ladder-core.js's userNav), and every
   move of the levels' own controls that leaves their scenes through toLevel or zoomBy here:
   - between two of the levels' places: their own move (a tab's, smooth, out and in; their cross-fade between maps);
   - from one of their places to a scale of the ladder: the path camera takes over at rest (the same picture), then moves;
   - back: the path camera moves to their place and hands over at rest; a move that changes the chip level under it (the
     L3's map to the DRAM's) first goes out to the map it is on, the levels cross-fade, and it goes on in from there. */
let ON = false, NAVG = 0, TAKEN = null, TAKENT = -1e9;
/* a move the levels ask of their own camera (a tab, a link, an access, the tour) cancels a hand-over still on its way
   (review of 1 Oct: a move of the ladder waits for their camera to rest before it takes the stage, and a tab clicked
   meanwhile lost its level to it); the moves a hand-over asks of their camera are marked as its own (o.hand), and do not */
const mlMove = () => { NAVG++; };
const stage = $('stage');
/* a tap, a click or a double-click that began on the levels' drawing does not go on to the ladder's drawing that took
   its place (a quick third tap after a double-tap that zoomed in from the levels' scene, review of 1 Oct) */
['pointerup', 'click', 'dblclick'].forEach(t => svg.addEventListener(t, e => { if (performance.now() - TAKENT < 900) e.stopImmediatePropagation(); }, true));
/* the path camera takes the stage at P (one of the levels' places, at rest, or a scale of the ladder: ?at=) */
function takeOver(P) {
  phGeom(); overlayFit(); phBox && phBox();
  Z.path = P.slice();
  const d = P.length - 1, L = built(P, d);
  LYR.forEach(l => { if (l !== L) { l.style.display = 'none'; l.style.opacity = 0; } });
  setT(L, restMat()); L.style.opacity = 1; L.style.visibility = ''; L.style.display = '';
  ctxClear(L); L.classList.remove('nolab', 'zout', 'busy', 'pan');
  skyBg();
  ON = true; TAKEN = pkeys(P); TAKENT = performance.now();
  stage.classList.add('lad-on');
  ML.onLadder(true);
  scaleUI(true);
}
/* the levels' camera takes the stage back at their place m (the path camera rests on the same picture) */
async function handBack(m) {
  if (m.V && CHIPLV.includes(m.V)) LASTV = m.V;
  // (a phone: the ladder's view of the levels' scene is their window where it is scrolled; the levels' camera, drawing the
  // scene at once, keeps that window)
  const wr = $('svgwrap'), sl = PH ? wr.scrollLeft : null;
  await ML.showAt(m.lv, m.path, m.V);
  if (sl != null && Math.abs(wr.scrollLeft - sl) > 1) wr.scrollLeft = sl;
  ON = false; TAKEN = null;
  stage.classList.remove('lad-on');
  LYR.forEach(l => { l.style.display = 'none'; l.style.opacity = 0; });
  svg.classList.remove('skyon');
  ML.onLadder(false);
  sync(true);
}
/* the levels' place now, as a path (the place their camera is going to, during a move) */
const mlNow = () => mlPath(ML.Z.lv, ML.zNow());
const dieK = P => { const e = P[OUT_IDS.length]; return e && e.id === 'die' ? (e.k || chipV()) : null; };
/* a path of the ladder with the die's view filled in (the core's ?at= and pathOf give the die without one) */
function fixDie(P) {
  const d = OUT_IDS.length;
  if (!P || P.length <= d || P[d].id !== 'die' || P[d].k) return P;
  const Q = P.slice(); Q[d] = {id: 'die', k: chipV()}; return Q;
}
const frames = n => new Promise(r => { const f = () => (--n > 0 ? requestAnimationFrame(f) : r()); requestAnimationFrame(f); });
/* where the reader goes: T, a path of the ladder; o as userNav's */
async function navTo(T, o) {
  o = o || {};
  T = fixDie(T);
  const gen = ++NAVG, live = () => gen === NAVG;
  const mT = mlOf(T);
  if (!ON) {
    if (mT) return ML.goTo(mT.lv, mT.path, Object.assign({}, o, {V: mT.V}));
    // out of the levels' scenes: the path camera takes over where they are (their move under way ends first)
    await ML.rest(); if (!live()) return;
    const P0 = mlNow();
    // (a target under another chip level's map: the levels go out to their map and cross-fade to that one first)
    const kT = dieK(T), k0 = dieK(P0);
    if (kT && k0 && kT !== k0) {
      const c = mlCut(T); if (!c) return;
      await ML.goTo(c.m.lv, c.m.path, {V: c.m.V}); if (!live()) return;
      if (pkeys(c.P) === pkeys(T)) return;
      takeOver(c.P);
    } else takeOver(P0);
    // two frames of the take-over's own (the same picture, drawn and painted by the path camera) before its move, so
    // that the move's first frame is a frame's step and not the take-over's long frame (review of 1 Oct, motion: the
    // hand-over's moves began with a jump, 58% of their top speed in one frame, where the chip's own ease in)
    if (!REDUCED) { await frames(2); if (!live()) return; }
  }
  // the path camera holds the stage: a target under another chip level's map is reached through the levels' own camera
  const kT = dieK(T), k0 = dieK(Z.path);
  if (kT && k0 && kT !== k0 && !isWrap(Z.path) && !isWrap(T)) {
    await goTo(Z.path.slice(0, OUT_IDS.length + 1), o); if (!live()) return;
    await handBack(mlOf(Z.path));
    return navTo(T, o);
  }
  await goTo(T, o); if (!live()) return;
  const m = mlOf(Z.path);
  if (m && !ZW) await handBack(m);
}
/* the moves the ladder's controls asked for, until each ends (its hand-over back to the levels' camera included): the
   ladder moves while one is on its way or its own camera moves */
const PEND = new Set();
const moving = () => ZW || UIP || PEND.size > 0;
/* the core's hook (userNav): every move the ladder's controls ask for */
function pageNav(t, o) {
  hideTip(); pillOff(); menuOff();
  ML.stopFollow();
  const p = navTo(t, Object.assign({focus: svg.contains(document.activeElement)}, o || {}));
  PEND.add(p); const done = () => PEND.delete(p); p.then(done, done);
  return p;
}
/* the Up bar shows the levels' place while their camera holds the stage */
function sync(force) {
  if (ON) return;
  stage.classList.remove('offchip');
  Z.path = mlNow();
  if (CHIPLV.includes(ML.Z.lv)) LASTV = ML.Z.lv;
  scaleUI(!!force);
}
/* + and −, Backspace, from the levels' keys: − is Up (from a level's top, the level outside it, then the ladder), + the
   selected part's scale, else the default */
function zoomBy2(d) {
  if (ON) return zoomBy(d);
  // (the keys keep the levels' key pace, 480 ms a unit of scale, as before; a click or a tap takes theirs: key)
  const P = mlNow(), o = {key: true};
  if (d < 0) { const U = upOf(P); return U ? pageNav(U, o) : null; }
  const g = ML.sel();
  if (g) { const k = kidOfML(g); if (k) return pageNav(k, o); }
  const N0 = nextOf(P); return N0 ? pageNav(N0, o) : null;
}
const canUp = () => !!upOf(ON ? Z.path : mlNow());
/* a level's tab (or 1-5) while the path camera holds the stage: back to the levels' place, then their move */
function toLevel(lv, path) {
  const p = path || [ML.SCENES[lv].root];
  return pageNav(mlPath(lv, p, CHIPLV.includes(lv) ? lv : chipV()));
}
/* the path a part of the levels' own drawing opens: the same part in the ladder's copy of the scene (drawn by the same
   builder, with the same example) says where (memory-levels.links.js, the textbook constructions; their data-child
   their own camera's scale) */
function kidOfML(g) {
  const L = g && g.closest && g.closest('g.lay'); if (!L || !L._lv) return null;
  const lv = L._lv, P = mlPath(lv, ML.pathIn(lv, L._node), dieK(mlNow()) || chipV()), d = P.length - 1;
  let H0; try { H0 = built(P, d); } catch (e) { console.error(e); return null; }
  const mine = [...L.querySelectorAll('.comp')], theirs = [...H0.querySelectorAll('.comp')], h = theirs[mine.indexOf(g)];
  if (!h || h._key !== g._key) return null;
  if (h._go) return fixDie(h._go());
  const k = kidOf(h); if (!k) return null;
  if (k.up) { const i = P.findIndex(e => e.id === k.up); return i >= 0 ? P.slice(0, i + 1) : null; }
  return fixDie(P.concat([k]));
}
/* whether a part of the levels' own drawing is a key (a box of numbers, a note), with nothing inside it */
function extML(g) {
  const L = g && g.closest && g.closest('g.lay'); if (!L || !L._lv) return false;
  const P = mlPath(L._lv, ML.pathIn(L._lv, L._node), dieK(mlNow()) || chipV());
  let H0; try { H0 = built(P, P.length - 1); } catch (_) { return false; }
  const h = [...H0.querySelectorAll('.comp')][[...L.querySelectorAll('.comp')].indexOf(g)];
  return !!(h && h._ext);
}
/* a part of the levels' own drawing: a double-click, a double-tap, Enter or the pill */
function zoomML(g) {
  const T = kidOfML(g);
  if (!T) return false;
  pageNav(T);
  return true;
}
/* the panel's zoom row for a part of the levels' own drawing (the chip's: where its double-click goes) */
function zoomRowML(g, title) {
  const T = kidOfML(g);
  if (!T) return `<div class="pn-zoom"><p class="nz">${extML(g) ? 'A key to the drawing, not a part of the chip: there is nothing inside it to zoom into.' : `No closer drawing of ${esc(title || 'this part')}.`}</p></div>`;
  const el = T[T.length - 1];
  return `<div class="pn-zoom">${zrow('Zoom in:', [zbtn(T, capFirst(toOf(el)), true, dcHint())])}</div>`;
}
/* a touch screen's strip under the drawing for a part of the levels' own drawing: its name, Zoom in where it leads */
let PILLML = null;
function pillML(g) {
  const pl = $('zpill');
  if (!TOUCH || !g || ON) { PILLML = null; return; }
  PILLML = g;
  const k = g.getAttribute('data-child') || kidOfML(g), t = $('pn-body').querySelector('.pn-title');
  $('zpill-in').hidden = !k; $('zpill-in').textContent = 'Zoom in ▸';
  pl.querySelector('.zs-name').textContent = t ? t.textContent : '';
  pl.hidden = false;
}
$('zpill-in').addEventListener('click', () => { if (!ON && PILLML && PILLML.isConnected) { const g = PILLML; pillOff(); PILLML = null; ML.zoomInto(g); } });
/* the ways back in from the ring: the reader's level's own cell, down to an atom (DESIGN §1.6: the L1 through its latch,
   the L2, the L3 and the scratchpad through a 6T cell, the DRAM through its cell and the DRAM process's transistor,
   never N7's); Up from the ring takes the first, always the same while the level is */
function ringExits() {
  const lv = ML.Z.lv, sc = ML.SCENES[lv];
  const cellId = {l1: 'latch', l2: 'cell', l3: 'cell', scp: 'cell', dram: 'dcell'}[lv];
  const base = mlPath(lv, ML.pathIn(lv, cellId), CHIPLV.includes(lv) ? lv : chipV());
  const lab = {l1: 'a silicon atom in a latch of the L1 (minion 0)', l2: 'a silicon atom in a 6T cell of the L2', l3: 'a silicon atom in a 6T cell of the L3 slice',
    scp: 'a silicon atom in a 6T cell of the scratchpad', dram: 'a silicon atom of a DRAM cell (a DRAM process, not N7)'}[lv];
  const short = {l1: 'an atom of an L1 latch', l2: 'an atom of an L2 cell', l3: 'an atom of an L3 cell', scp: 'an atom of a scratchpad cell', dram: 'an atom of a DRAM cell'}[lv];
  return [
    {id: 'level', lab, short, path: () => chainTo(base, 'p.atom')},
    {id: 'planck', lab: `the Planck length, under that atom of the ${sc.short}`, short: 'the tail: the Planck length', path: () => chainTo(base, PLANCK)},
  ];
}
/* "You are here" after a reader's move of the levels' own camera (the chip's panel, DESIGN §3.3): at a level's top its
   own panel (the level, its numbers, its asks) with the scale's zooms under its title; deeper, the scale's panel from
   the ladder's tree (its name, its lead, its zooms, ↑ Zoom out) */
function mlHere(levelChanged) {
  // (the path camera holds the stage on its copy of a scene the levels draw, not at their place: another bank, another
  // shire, a minion of another neighbourhood; the scale's panel from the ladder's tree, as for any of its scales; review
  // of 1 Oct evening: the panel of the place left stayed)
  if (ON) { showScene(Z.path); return; }
  const P = mlNow(), m = mlOf(P); if (!m) { showScene(P); return; }
  if (m.path.length === 1) {
    if (!levelChanged) ML.overview();
    const b = $('pn-body'), t = b.querySelector('.pn-lead') || b.querySelector('.pn-badge') || b.querySelector('.pn-title');
    if (t && !b.querySelector('.pn-zoom')) t.insertAdjacentHTML('afterend', zoomRowHere(P));
  } else showScene(P);
}

/* ---- the controls: the Up bar's markup is the chip's; its handlers are the core's, through pageNav ---- */
/* keys while the path camera holds the stage (the levels' handler routes + − Backspace here, and G) */
function onKey(e) {
  if (!ON) return false;
  const tg = e.target, onDraw = svg.contains(tg) || tg === document.body || tg === document.documentElement;
  switch (e.key) {
    case 'ArrowRight': if (onDraw) { e.preventDefault(); arrowNav('E'); return true; } return false;
    case 'ArrowLeft': if (onDraw) { e.preventDefault(); arrowNav('W'); return true; } return false;
    case 'ArrowDown': if (svg.contains(tg)) { e.preventDefault(); arrowNav('S'); return true; } return false;
    case 'ArrowUp': if (svg.contains(tg)) { e.preventDefault(); arrowNav('N'); return true; } return false;
  }
  return false;
}
window.addEventListener('resize', () => {
  clearTimeout(RSZ); RSZ = setTimeout(() => {
    const ph0 = PH; phGeom(); overlayFit();
    if (ON) { if (PH !== ph0) { const P = Z.path.slice(); LYR.forEach(l => { l._built = false; }); takeOver(P); } else { phBox && phBox(); const L = restLayer(); if (L) setT(L, restMat()); } }
  }, 150);
});
let RSZ = 0;
/* the levels' drawing's box changes without the window (the panel hidden, presenting, full screen): the overlay follows,
   and the scale at rest keeps its view */
try {
  let w0 = 0, h0 = 0;
  new ResizeObserver(() => {
    const w = $('svgwrap'); if (w.clientWidth === w0 && w.clientHeight === h0) return; w0 = w.clientWidth; h0 = w.clientHeight;
    phGeom(); overlayFit();
    if (ON && !ZW) { phBox(); const L = restLayer(); if (L) setT(L, restMat()); }
  }).observe($('svgwrap'));
} catch (_) { /* no observer: the window's resize does it */ }
/* the phone's box: the overlay's shape (the levels' visible window), 1,000 units wide */
function phBox() {
  if (!PH) { svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`); return; }
  const H = (1000 * PV[0].h / PV[0].w).toFixed(1);
  svg.setAttribute('viewBox', `0 0 1000 ${H}`);
}

/* ---- the start: the ladder's place from the address (?at= or #at=), else the levels' ---- */
DIE = OUT_IDS.length;
{
  let at = null;
  try { const q = new URLSearchParams(location.search); at = q.get('at'); if (!at && /^#at=/.test(location.hash)) at = decodeURIComponent(location.hash.slice(4)); } catch (_) { /* no URL */ }
  const P = at ? fixDie(atPath(at)) : null;
  if (P) {
    const m = mlOf(P);
    if (m) ML.goTo(m.lv, m.path, {ms: 0, V: m.V});
    else setTimeout(() => { takeOver(P); arrived(); }, 0);
  }
  phGeom(); overlayFit();
  sync(true);
}
/* ---- the tests' walks (as the chip diagram's __chipTest.walk and graph, part 1b): every scene by its path ---- */
/* every scene reached by zoom-ins from each of the levels' places and from the rack, one path per shape (the ids along
   it), each with its parts, what each leads to and whether its seat is there; layers are dropped as the walk leaves */
function walk(o) {
  o = o || {};
  const out = [], sig = new Map(), shapes = new Set(), MAX = o.max || 6000, PRE = new Set(LYR.keys());
  const shapeOf = P => P.map(e => (/^(shire|memshire|die)$/.test(e.id) ? pk(e) : e.id)).join('/');
  const drop = P => { const key = pkeys(P); if (ON && Z.path.length >= P.length && samePath(Z.path.slice(0, P.length), P)) return; const L = LYR.get(key); if (L && !PRE.has(key)) { L.remove(); LYR.delete(key); } };
  const seat1 = C => { try { return !!seatOf(C, C.length - 1); } catch (_) { return false; } };
  const seatAll = C => { try { for (let d = 1; d < C.length; d++) if (!seatOf(C, d)) return false; return true; } catch (_) { return false; } };
  const visit = P => {
    const shape = shapeOf(P);
    if (shapes.has(shape) || out.length >= MAX) return;
    shapes.add(shape);
    const d = P.length - 1, el = P[d];
    let L; try { L = built(P, d); } catch (e) { out.push({shape, path: pkeys(P), id: el.id, err: String(e)}); return; }
    const next = [];
    const parts = [...L.querySelectorAll('.comp')].map(g => {
      const k = kidOf(g), go = g._go ? g._go() : null, r = {key: g._key, ext: !!g._ext, mos: g.querySelectorAll('g.mos').length, label: g.getAttribute('aria-label')};
      if (go) { r.go = go.map(e => e.id).join('/'); r.to = go[go.length - 1].id; r.seat = seatAll(go); next.push(fixDie(go)); }
      else if (k && k.up) r.up = k.up;
      else if (k) { const C = fixDie(P.concat([k])); r.to = k.id; r.seat = seat1(C); if (r.seat) next.push(C); }
      return r;
    });
    const kids = kidsOf(P).map(k => { const C = fixDie(P.concat([k])), s0 = seat1(C); if (s0) next.push(C); return {to: k.id, seat: s0}; });
    const s1 = JSON.stringify(parts.map(q => [q.key, q.to || '', q.up || '', q.ext ? 1 : 0]).sort()) + '|' + kids.map(k => k.to).join(',');
    const dup = sig.has(el.id) && sig.get(el.id) === s1;
    if (!sig.has(el.id)) sig.set(el.id, s1);
    out.push({shape, path: pkeys(P), id: el.id, egg: egg(el), ml: !!mlOf(P), dup, mos: L.querySelectorAll('g.mos').length, parts, kids});
    if (!dup) next.forEach(C => visit(C));
    drop(P);
  };
  const roots = o.roots || LEVELS.flatMap(lv => Object.keys(ML.SCENES[lv].scales).map(id => mlPath(lv, ML.pathIn(lv, id), CHIPLV.includes(lv) ? lv : 'l3'))).concat([OUT_IDS.slice(0, OUT_IDS.indexOf('rack') + 1).map(id => ({id}))]);
  roots.forEach(P => visit(P));
  LYR.forEach((L, key) => { if (!PRE.has(key) && !(ON && L === restLayer())) { L.remove(); LYR.delete(key); } });
  return out;
}
/* the navigation graph from the top and from the ring (the chip's T18): each scale's exits, and whether each glide has its
   way back */
function graph() {
  const out = [], seen = new Set(), Q = [[{id: 'beyond'}], [{id: WRAP}]], OPP = {N: 'S', S: 'N', W: 'E', E: 'W'};
  // (one path per scale, as the chip's: a scale's instances are its siblings, their glides checked from the one met)
  const push = P => { if (!P || !P.length) return; P = fixDie(P); const id = P[P.length - 1].id === 'die' ? pk(P[P.length - 1]) : P[P.length - 1].id; if (!seen.has(id)) { seen.add(id); Q.push(P); } };
  const seatOk = P => { try { for (let d = 1; d < P.length; d++) if (!seatOf(P, d)) return false; return true; } catch (_) { return false; } };
  const PRE = new Set(LYR.keys());
  while (Q.length && out.length < 600) {
    const P = Q.shift(), el = P[P.length - 1], d = P.length - 1;
    let L; try { L = built(P, d); } catch (e) { out.push({id: el.id, path: pkeys(P), err: String(e)}); continue; }
    const parts = [...L.querySelectorAll('.comp')].map(g => {
      const k = kidOf(g), go = g._go ? g._go() : null, r = {key: g._key, ext: !!g._ext};
      if (go) { r.go = pkeys(go); r.seat = seatOk(go); push(go); }
      else if (k && k.up) r.up = k.up;
      else if (k) { const C = P.concat([k]); r.kid = pk(k); r.seat = seatOk(C); if (r.seat) push(C); }
      return r;
    });
    const kids = kidsOf(P).map(k => { const C = P.concat([k]); const ok = seatOk(C); if (ok) push(C); return {kid: pk(k), seat: ok}; });
    const U = upOf(P), N0 = nextOf(P); push(U); push(N0);
    const side = {};
    if (P.length > 1) ['N', 'S', 'W', 'E'].forEach(dir => { const S1 = sibInDir(P, dir); if (S1) { const B = sibInDir(S1, OPP[dir]); side[dir] = {to: pk(S1[S1.length - 1]), back: !!B && samePath(B, P)}; } });
    out.push({id: el.id, path: pkeys(P), ml: !!mlOf(P), depth: d, egg: egg(el), parts, kids, up: U ? pkeys(U) : null, next: N0 ? pkeys(N0) : null, side});
    if (!PRE.has(pkeys(P)) && !(ON && samePath(P, Z.path))) { const L1 = LYR.get(pkeys(P)); if (L1) { L1.remove(); LYR.delete(pkeys(P)); } }
  }
  return out;
}
/* the state for the page's tests (headless Chrome): the path camera's place and what it shows */
const ladState = () => ({on: ON, path: pkeys(ON ? Z.path : mlNow()), node: (ON ? Z.path : mlNow()).slice(-1)[0].id, depth: (ON ? Z.path : mlNow()).length - 1,
  zooming: moving(), die: DIE, ml: ON ? null : mlOf(mlNow()),
  visible: ON ? [...svg.querySelectorAll(':scope > g.lay')].filter(l => l.style.display !== 'none').map(l => {
    const m = /matrix\(([-\d.e]+)/.exec(l.getAttribute('transform') || ''); return {depth: +l.dataset.depth, node: l.dataset.node, k: m ? +m[1] : 1, op: l.style.opacity}; }) : [],
  step: CUR ? {kind: CUR.s.kind, e: +CUR.e.toFixed(4), o: CUR.s.o} : null,
  scale_m: (sizeOf((ON ? Z.path : mlNow()).slice(-1)[0]) || {}).m || null,
  up: $('up').textContent, upDisabled: isDis($('up')), crumbs: [...$('crumbs').querySelectorAll('button')].map(b => b.textContent),
  readout: $('scale-ro').textContent, ston: STON, wrapin: WRAPIN, panel: ($('pn-body').querySelector('.pn-title') || {}).textContent || ''});
/* the light state a recorder reads every frame (tools/pagemotion/recorder-mlchip.js): the ladder's place, and whether it moves */
const where = () => ({on: ON, zooming: moving(), path: pkeys(ON ? Z.path : mlNow())});
return {on: () => ON, moving, where, mlMove, sync, here: mlHere, detBlock, zoomBy: zoomBy2, canUp, toLevel, kidOfML, zoomML, zoomRowML, onKey, stateToggle, pillFor: g => pillML(g), pillOff,
  fact: id => F[id] || null, kword: k => KWORD[k] || k, cavw: c => CAVW[c] || '', navTo: pageNav, state: ladState, home: () => toLevel(ML.Z.lv),
  test: {walk: o => walk(o), graph: () => graph(), take: () => takeOver(mlNow()), back: () => handBack(mlOf(Z.path)), mlOf: P => mlOf(fixDie(pathFrom(P))), mlPath: (lv, p) => pkeys(mlPath(lv, p)), atPath: s => pkeys(fixDie(atPath(s)) || []), exits: () => ringExits().map(x => ({id: x.id, path: pkeys(x.path() || [])})),
    nodes: () => Object.keys(NODES), go: s => { const P = fixDie(atPath(s)); return P ? pageNav(P) : null; }, egg: () => [...eggFacts()],
    name: () => nameOf((ON ? Z.path : mlNow()).slice(-1)[0])}};
