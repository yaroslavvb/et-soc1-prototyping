/* ================= ladder-core.js: the path camera and the Up bar, shared (1 October 2026) =================
   The camera of the chip diagram's deep zoom (30 September), moved out of chip-diagram.script.js so that the memory
   levels can stand on the same ladder (/home/yaroslavvb/claude/work/ladder/DESIGN.md: one path vocabulary, one
   camera). The page includes it with an include line (build-report.py expands it in place: it shares the page
   script's scope, and the build refuses a name declared twice at the top level). What it defines: the scale nodes
   (NODES, node, pk, pkeys, prm, elOf, pathFrom), the camera (Z, LYR, layerAt, built, seatOf, mkStep, routeSteps,
   planTo, openStep, openPan, goTo, userNav, zoomWorker), the Up bar, the breadcrumb, its menu and the readout
   (zoomBy, scaleUI, crumbsUI, plusUI, menuToggle, readout, roRest), the sizes (fmtLen, sizeTxt, sizeWords,
   sizeHtml), the arrow keys' moves (arrowNav, sibInDir, focusDir) and ?at= (atPath). What it uses from the page (the
   chip defines them before the include): the drawing's svg, VB, PH, TOUCH, REDUCED, the clock (CLK, DTMAX), the
   view helpers (lerp, rmap, setT, cmpM, simZoom, ...), the trio of layers the page animates in (bindTrio, LAYERS,
   pinfo, pathOf, TRIO, PVIEW, pview), and the page's reactions to a move (clearFx, clearDim, select, showHere,
   prefetch, FL, TOUR, playBtn, renderBar, startFlow, restartStage, setFollow, FOLLOW, goNeighbour, shCell, BYDIE).
   Since 1 October it also holds the wrap (the ring of sizes), the easter egg's "?" (the levels above the rack), the
   two-state electronics (stateSwitch, stateToggle) and the lazily fetched data (lazyData). The hooks every page that
   includes it must define (build-report.py refuses a page without them): pageExits() the ways back in from the ring,
   [{id, lab, short, path()}]; pageBusy() true while a flow or an access holds the stage; pageLazy(ok) the lazy data has
   arrived (or failed): redraw what showed it. */
/*@hooks pageExits pageBusy pageLazy*/
/* ================= the path camera (30 September 2026) =================
   One engine for a ladder of any depth (the owner's "zoom out ... all the way to the meta universe" and "double-click
   ... until I get individual circuit components"). The camera rests on a path of scale nodes from the root down
   (Z.path); each scale is a scene drawn in its own coordinates in a layer of its own. A move is a list of steps, each
   between a scale and one inside it: out to the deepest scale the two paths share, then in (or, between two siblings
   side by side in their parent's drawing, a sideways glide). The steps one way form a leg, eased once, which goes
   through the rest of every scale it passes and turns smoothly there (the blend of the chip's camera of 30 September,
   BLEND). Every frame is computed in the coordinates of the step it is in (at most one map from a neighbouring scale),
   never in the root's: 36 orders of magnitude from the universe to the silicon lattice do not fit one coordinate
   system, in doubles or in the browser's float32 transforms. Three kinds of step: nest (the inner scale drawn inside
   the outer, which zooms smoothly; as since 27 September), jump (a "powers of ten" cut: the outer zooms some 8 times
   into a marker while the inner grows into it and the two cross-fade; the readout sweeps the true ratio) and pan. */
let CUR = null;
const ID = [1, 0, 0];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
/* the root of the ladder down to the die (empty until the outside levels arrive); DIE: the die's depth */
const OUT_IDS = [];
let DIE = 0;
/* the scale nodes by id: {name(p), short(p), size(p), frame(p), view(p), pv(p), build(L, ap, p, P, d), tr, def(p),
   kids(p), parse(k)} */
const NODES = {};
const node = (id, o) => { NODES[id] = Object.assign({id, tr: 'nest'}, o); return NODES[id]; };
const pk = el => el.id + (el.k != null && el.k !== '' ? ':' + el.k : '');
const pkeys = P => P.map(pk).join('/');
const samePath = (a, b) => a.length === b.length && a.every((x, i) => pk(x) === pk(b[i]));
const prm = el => { const N0 = NODES[el.id]; return N0 && N0.parse ? N0.parse(el.k) : {}; };
const elOf = s => { const i = s.indexOf(':'); return i < 0 ? {id: s} : {id: s.slice(0, i), k: s.slice(i + 1)}; };
/* the die, a shire and a minion as a path (the flows' and the tour's views stay {level, sid, nb, mi}) */
function pathOf(w) {
  const P = OUT_IDS.map(id => ({id})).concat([{id: 'die'}]);
  if (w.level >= 1) P.push({id: 'shire', k: String(w.sid)});
  if (w.level >= 2) P.push({id: 'minion', k: `${w.sid}.${w.nb}.${w.mi}`});
  return P;
}
/* what a path is in the flows' terms: level -1 above the die, 0-2 the die, a shire, a minion, 3 any other scale on the
   chip; the shire and minion it is in */
function pinfo(P) {
  const o = {path: P, depth: P.length - 1, level: -1, sid: null, nb: null, mi: null};
  const d = P.findIndex(e => e.id === 'die');
  if (d < 0) return o;
  const lv = P.length - 1 - d, sh = P[d + 1], mn = P[d + 2];
  if (sh && sh.id === 'shire') o.sid = +sh.k;
  if (mn && mn.id === 'minion') { const q = String(mn.k).split('.').map(Number); o.nb = q[1]; o.mi = q[2]; }
  o.level = lv === 0 ? 0 : lv === 1 && sh.id === 'shire' ? 1 : lv === 2 && sh.id === 'shire' && mn.id === 'minion' ? 2 : 3;
  return o;
}
let LASTSID = 0, LASTNB = 0, LASTMI = 0;
const Z = {path: [{id: 'die'}]};
Object.defineProperties(Z, {
  level: {get: () => pinfo(Z.path).level},
  sid: {get: () => { const i = pinfo(Z.path); return i.sid != null ? i.sid : LASTSID; }},
  nb: {get: () => { const i = pinfo(Z.path); return i.nb != null ? i.nb : LASTNB; }},
  mi: {get: () => { const i = pinfo(Z.path); return i.mi != null ? i.mi : LASTMI; }},
});
/* ---- layers: one per scale on a path, keyed by the path to it; LAYERS[0..2] the die's, the shire's and the
   minion's (the flows draw there), AP and FX theirs ---- */
const LYR = new Map();
function layerAt(P, d) {
  const key = pkeys(P.slice(0, d + 1));
  let L = LYR.get(key);
  if (!L) {
    L = E('g', {class: 'lay', 'data-depth': d, 'data-level': d - DIE, 'data-node': P[d].id});
    L.style.display = 'none'; L.style.opacity = 0;   // hidden views start transparent: a zoom fades them in
    const after = [...svg.querySelectorAll(':scope > g.lay')].find(x => +x.dataset.depth > d);
    svg.insertBefore(L, after || null);
    L._key = key; L._el = P[d]; L._path = P.slice(0, d + 1); L._depth = d; L._built = false; L._ap = {zs: {}};
    LYR.set(key, L);
  }
  return L;
}
/* the layer of P[d], built (a scale is drawn once per path to it; a move off the path drops it, prune()) */
function built(P, d) {
  const L = layerAt(P, d);
  if (!L._built) buildInto(L, P, d);
  return L;
}
function buildInto(L, P, d) {
  const el = P[d], N0 = NODES[el.id];
  L.textContent = ''; ctxClear(L); L._sky = false;
  const ap = L._ap = {zs: {}};
  N0.build(L, ap, prm(el), P, d);
  if (typeof chipSeats === 'function') chipSeats(L, ap, el);
  if (L.classList.contains('ckt')) CKT.hitAreas(L);
  if (TOUCH && !N0.out) minHits(L, P, d);
  L._fx = ap.fx && ap.fx.parentNode === L ? ap.fx : E('g', {class: 'fx', 'pointer-events': 'none'}, L);
  L._built = true;
  ariaFix(L);
  bindTrio(P);
}
/* On a touch screen a thin part gets a transparent hit area at least 24 CSS px across its thin side, as far as that
   covers no other part (review of 1 Oct: in the circuits some parts were 6-15 px on one side, hard to tap) */
function minHits(L, P, d) {
  const v = viewOf(P[d]), wr = $('svgwrap'), bw = wr.clientWidth || innerWidth - 32, bh = wr.clientHeight || innerHeight / 2;
  const pxu = PH ? bw / v.w : Math.min(bw / VB.w, bh / VB.h) * VB.w / v.w;
  if (!(pxu > 0)) return;
  const need = 24 / pxu, comps = [...L.querySelectorAll('.comp')], box = new Map();
  const bb = g => { if (g._box) return g._box; try { const r = g.getBBox(); return r.width || r.height ? {x: r.x, y: r.y, w: r.width, h: r.height} : null; } catch (_) { return null; } };
  const run = () => comps.forEach(g => { const b = bb(g); if (b) box.set(g, b); });
  if (CKT && CKT.kit && CKT.kit.measured) CKT.kit.measured(L, run); else run();
  const hit = (a, b) => Math.min(a.x + a.w, b.x + b.w) > Math.max(a.x, b.x) + 0.5 && Math.min(a.y + a.h, b.y + b.h) > Math.max(a.y, b.y) + 0.5;
  comps.forEach(g => {
    const b = box.get(g); if (!b || Math.min(b.w, b.h) >= need) return;
    for (const f of [1, 0.6, 0.3]) {
      const ex = b.w < need ? (need - b.w) / 2 * f : 0, ey = b.h < need ? (need - b.h) / 2 * f : 0;
      const r = {x: b.x - ex, y: b.y - ey, w: b.w + 2 * ex, h: b.h + 2 * ey};
      if ([...box].some(([o, ob]) => o !== g && !o.contains(g) && !g.contains(o) && hit(r, ob))) continue;
      const e = E('rect', {class: 'hit', x: r.x, y: r.y, width: r.w, height: r.h, fill: 'transparent', 'pointer-events': 'all'});
      g.insertBefore(e, g.firstChild);
      return;
    }
  });
}
/* every part says what Enter does: zoom in where it has a scale of its own, else its details (a screen reader hears the
   same rule everywhere) */
function ariaFix(L) {
  L.querySelectorAll('.comp').forEach(g => {
    const l0 = g.getAttribute('aria-label') || '', base = l0.replace(/(\.\s*Space for details; Enter zooms in\.?|:\s*details(; Enter zooms in)?\.?|; Enter zooms in\.?)\s*$/, '');
    const k = kidOf(g);
    g.setAttribute('aria-label', base + (k ? (k.up ? '. Space for details; Enter goes out to it.' : '. Space for details; Enter zooms in.') : ': details'));
  });
}
const TRIO = ['die', 'shire', 'minion'];
function bindTrio(P) {
  const d = P.findIndex(e => e.id === 'die'); if (d < 0) return;
  const fx0 = FX[0];
  for (let i = 0; i < 3; i++) {
    const el = P[d + i]; if (!el || el.id !== TRIO[i]) break;
    const L = LYR.get(pkeys(P.slice(0, d + i + 1)));
    if (L && L._built) { LAYERS[i] = L; AP[i] = L._ap; FX[i] = L._fx; }
  }
  // the band's fold (a phone) watches the die's flow drawing: a new one is watched instead
  if (FX[0] !== fx0 && foldObs) watchFold();
}
/* after a move: the layers off the path go (the die's, and the shire's and minion's the flows hold, stay hidden) */
function prune(keep) {
  const on = new Set(Z.path.map((_, i) => pkeys(Z.path.slice(0, i + 1))));
  LYR.forEach((L, key) => {
    if (on.has(key) || LAYERS.includes(L) || (keep && keep.has(L))) { if (!on.has(key)) { L.style.display = 'none'; L.style.opacity = 0; } return; }
    L.remove(); LYR.delete(key);
  });
}
const restLayer = () => LYR.get(pkeys(Z.path));
/* ---- frames, seats and views ----
   frame: the box in a scale's own units that its seat in the parent's drawing grows into; view: the scale's rest view
   (desktop: the drawing's frame VB unless the node says; a phone: its own view, pv) */
const frameOf = el => NODES[el.id].frame(prm(el));
const PVIEW = {die: 0, shire: 1, minion: 2};
function viewOf(el) {
  const N0 = NODES[el.id], p = prm(el);
  if (!PH) return N0.view ? N0.view(p) : VB;
  if (PVIEW[el.id] != null) return pview(PVIEW[el.id]);
  if (N0.pv) return N0.pv(p);
  // a phone: the rest view letterboxed into the box's shape, at its top (the box is the tallest of the trio's views)
  const v = N0.view ? N0.view(p) : VB, hw = phHW();
  return v.h / v.w <= hw ? {x: v.x, y: v.y, w: v.w, h: v.w * hw} : {x: v.x + v.w / 2 - v.h / hw / 2, y: v.y, w: v.h / hw, h: v.h};
}
const phHW = () => Math.max(...[0, 1, 2].map(lv => { const r = pview(lv); return r.h / r.w; }));
const isVB = r => r === VB || (Math.abs(r.x - VB.x) < 1e-9 && Math.abs(r.y - VB.y) < 1e-9 && Math.abs(r.w - VB.w) < 1e-9);
/* the transform that shows view r on the screen: a phone's (viewM, 1000 units wide), else r fitted to the frame VB */
const vmat = r => (PH ? viewM(r) : isVB(r) ? null : rmap(r, VB));
const restMat = () => vmat(viewOf(Z.path[Z.path.length - 1]));
/* a box with aspect k (width / height), centred on r and covering it */
function fitTo(r, k) {
  let w = r.w, h = r.h;
  if (Math.abs(w / h - k) < 1e-6) return r;
  if (w / h > k) h = w / k; else w = h * k;
  return {x: r.x + r.w / 2 - w / 2, y: r.y + r.h / 2 - h / 2, w, h};
}
/* where P[d] sits in the drawing of P[d - 1]: the part its builder registered (ap.zs, by the child's key), else the
   node's own rule */
function seatOf(P, d) {
  const Lp = built(P, d - 1), s = Lp._ap.zs[pk(P[d])];
  if (s) return s;
  const N0 = NODES[P[d].id];
  const r = N0.seat ? N0.seat(Lp._ap, prm(P[d]), P[d - 1], Lp) : null;
  return !r ? null : r.r ? r : {r, g: null};
}
const sizeOf = el => { const N0 = NODES[el.id]; return N0.size ? N0.size(prm(el)) : null; };
/* ---- the steps of a move ---- */
function mkStep(P, d, dir) {
  const st = seatOf(P, d);
  if (!st) throw new Error('no seat for ' + pkeys(P.slice(0, d + 1)));
  const B = frameOf(P[d]);
  let A = fitTo(st.r, B.w / B.h), kind = st.tr || NODES[P[d].id].tr || 'nest';
  // a seat so small that the inner scale would be drawn at under a twenty-eighth of its own size: a "powers of ten"
  // jump from a box an eighth of the parent's view around it, so that no layer shown is ever scaled beyond [1/30, 30]
  // (float32 transforms, sub-pixel drawings); the chip's own steps (a shire's minion is 17 times) stay nests
  if (B.w / A.w > 28) { const vw = viewOf(P[d - 1]).w, w = vw / 8, c = {x: A.x + A.w / 2, y: A.y + A.h / 2}; A = {x: c.x - w / 2, y: c.y - w * B.h / B.w / 2, w, h: w * B.h / B.w}; kind = 'jump'; }
  const Q = rmap(A, B), lq = Math.log(Q[0]);
  // a jump's time: its drawn zoom plus a little for the decades it skips (the readout sweeps them)
  const so = sizeOf(P[d - 1]), si = sizeOf(P[d]);
  const tru = so && si && so.m > 0 && si.m > 0 ? Math.log(so.m / si.m) : lq;
  const L = kind === 'jump' ? lq + 0.15 * Math.max(0, tru - lq) : lq;
  return {o: d - 1, P: P.slice(0, d + 1), dir, e0: dir > 0 ? 0 : 1, e1: dir > 0 ? 1 : 0, A, B, Q, lq, L, kind, tgt: st.g || null, so, si};
}
/* the steps from the scale P (at rest) to T: out to the deepest scale they share, then in; o.pan: two siblings side by
   side in their parent's drawing glide instead */
function routeSteps(P, T, o) {
  // different roots (only the ring has a root of its own): one wrap step joins the ring to the top of the ladder, or to
  // the Planck length at the bottom of a branch
  if (P[0].id !== T[0].id) {
    const top = [{id: 'beyond'}], low = Q => Q[Q.length - 1].id === PLANCK;
    if (isWrap(P)) return low(T) ? [wrapStep(P, T)] : [wrapStep(P, top)].concat(routeSteps(top, T, o));
    if (isWrap(T)) return low(P) ? [wrapStep(P, T)] : routeSteps(P, top, o).concat([wrapStep(top, T)]);
  }
  let k = 0; while (k < P.length && k < T.length && pk(P[k]) === pk(T[k])) k++;
  if (o && o.pan && P.length === T.length && k === P.length - 1 && k >= 1) { const ps = panStep(P, T); if (ps) return [ps]; }
  const out = [];
  for (let d = P.length - 1; d >= k; d--) out.push(mkStep(P, d, -1));
  for (let d = Math.max(1, k); d < T.length; d++) out.push(mkStep(T, d, 1));
  return out;
}
const costOf = ss => ss.reduce((c, s) => c + s.L, 0);
/* two siblings side by side: the camera glides from one to the other at their scale, the parent not shown */
function panStep(P, T) {
  const d = P.length - 1, s1 = seatOf(P, d), s2 = seatOf(T, d);
  if (!s1 || !s2) return null;
  const B1 = frameOf(P[d]), B2 = frameOf(T[d]), A1 = fitTo(s1.r, B1.w / B1.h), A2 = fitTo(s2.r, B2.w / B2.h);
  const dist = Math.hypot(A2.x + A2.w / 2 - A1.x - A1.w / 2, A2.y + A2.h / 2 - A1.y - A1.h / 2) / A1.w;
  if (dist > 1.6) return null;
  const Q1 = rmap(A1, B1), Q2 = rmap(A2, B2);
  return {pan: true, o: d - 1, P, T, dir: 1, e0: 0, e1: 1, A1, A2, B1, B2, Q1, Q2, dist, L: 0.6, kind: 'pan'};
}
/* a wrap step, between the ring and a scale of the ladder (the top, beyond, or the Planck length at the bottom of a
   branch): the ring's layer and the other's cross-fade, as in a jump, the other growing out of (or shrinking into) its
   mark on the ring, the head for the top and the tail's tip for the Planck length; a marker runs along the ring's arc
   (a stroke-dashoffset in the ring's own drawing). Its own leg, like a glide. */
function wrapStep(F, T) {
  const ring = isWrap(F) ? F : T, other = isWrap(F) ? T : F;
  return {wrap: true, kind: 'wrap', F, T, ring, other, toRing: isWrap(T), dir: 1, e0: 0, e1: 1, L: 2.6, o: 0, P: other.slice(), dist: 0};
}
function openWrap(s, req) {
  const R = built(s.ring, 0), O = built(s.other, s.other.length - 1), bd = BANDS.jump;
  const ap = R._ap, head = s.other[0].id === 'beyond', mk = head ? ap.headBox : ap.tailBox;
  // the other's frame drawn into its mark on the ring at its smallest (an eighth of the ring's view at most), the ring
  // zoomed in on the mark by as much at the other's rest
  const B = frameOf(s.other[s.other.length - 1]), A = fitTo(mk || {x: 0, y: 0, w: 100, h: 100}, B.w / B.h), Q = rmap(A, B);
  const vr = viewOf(s.ring[0]), vo = viewOf(s.other[s.other.length - 1]);
  const run = ap.run || null, runL = ap.runLen || 1;
  const frame = q => {
    // e: 0 the ring at rest, 1 the other at rest
    const e = s.toRing ? 1 - q : q, R0 = zoomR(A, B, e), Mo = rmap(A, R0), Mi = rmap(B, R0);
    const V = vmat(isVB(vr) && isVB(vo) ? VB : lerpR(vr, vo, e));
    setT(R, cmpM(V, Mo)); setT(O, cmpM(V, Mi));
    const oo = 1 - band(e, bd.oo[0], bd.oo[1]), io = band(e, bd.ii[0], bd.ii[1]);
    R.style.opacity = oo; R.style.visibility = oo > 0 ? '' : 'hidden'; O.style.opacity = io;
    R.style.setProperty('--lab', (1 - band(e, 0.02, 0.2)).toFixed(3)); O.style.setProperty('--lab', band(e, bd.li[0], bd.li[1]).toFixed(3));
    // the marker: along the arc from the head to the tail's tip (the way Up goes round), drawn as far as it has run
    // (across the mouth only between the ring and the Planck length: from the head to the tail's tip going in, back again
    // going out)
    if (run) { const f = head ? 0 : clamp(s.toRing ? 1 - q : q, 0, 1); run.style.strokeDashoffset = (runL * (1 - f)).toFixed(1) + 'px'; }
    svg.classList.toggle('skyon', !!(oo > 0.5 ? R._sky : O._sky));
    readout(s, q);
  };
  ctxClear(R); ctxClear(O); clearDim();
  frame(0);
  R.style.display = ''; O.style.display = '';
  svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.add('busy'));
  return {
    s, frame, update: () => {},
    close: (e1, last, arrive) => {
      const to = e1 >= 0.5;
      frame(to ? 1 : 0);
      const here = (to ? s.T : s.F), hereL = isWrap(here) ? R : O, gone = hereL === R ? O : R;
      gone.style.display = 'none'; ctxClear(gone); gone.style.removeProperty('--lab'); hereL.style.removeProperty('--lab');
      hereL.style.opacity = 1; hereL.style.visibility = '';
      if (run) run.style.strokeDashoffset = runL + 'px';
      Z.path = here.slice();
      // in from the ring: which way back in was taken (Up takes the other one next time round)
      if (!isWrap(here) && typeof pageExits === 'function') { const x = pageExits().find(x0 => samePath(x0.path(), here)); if (x) LASTEXIT = x.id; }
      bindTrio(Z.path);
      setT(hereL, restMat());
      if (last) { if (arrive) arrive(); svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.remove('busy')); }
      scaleUI();
    },
  };
}
/* the plan: the steps from the view shown, or from partway through the step in flight (forwards or back, whichever is
   shorter), to the target; which views are only passed through */
function planTo(t, o) {
  let steps;
  if (CUR && !CUR.s.pan && !CUR.s.wrap) {
    const s = CUR.s, Ls = s.L;
    const Pin = s.P, Pout = s.P.slice(0, -1);
    const pin = routeSteps(Pin, t, null), pout = routeSteps(Pout, t, null);
    const cin = (1 - CUR.e) * Ls + costOf(pin), cout = CUR.e * Ls + costOf(pout);
    const fwd = cin < cout - 1e-9 || (Math.abs(cin - cout) < 1e-9 && CUR.dir > 0);
    steps = [Object.assign({}, s, {part: true, dir: fwd ? 1 : -1, e0: CUR.e, e1: fwd ? 1 : 0, L: Math.max(1e-3, fwd ? (1 - CUR.e) * Ls : CUR.e * Ls)})].concat(fwd ? pin : pout);
  } else steps = routeSteps(Z.path, t, o);
  steps.forEach((s, i) => {
    // the outer view sits at e = 0: where a zoom in starts, or where a zoom out ends
    const startMid = i > 0, endMid = i < steps.length - 1;
    s.midOut = s.dir > 0 ? startMid : endMid;
    s.midIn = s.dir > 0 ? endMid : startMid;
    // the establishing shot rests its eye on the chip: the chip is shown there, set back, not passed through
    if (o.atChip && !s.wrap && s.P[s.o].id === 'die') s.midOut = false;
    if (s.dir < 0 && !s.midOut) s.end = i === steps.length - 1 ? (o.c1 || FULL) : (o.chipEnd || FULL);
  });
  return steps;
}
/* A step's look (the chip's semantic zoom of 27 September, the same both ways):
   - the outer view's labels go first (none is ever seen blown up), and its context is set back (to 0.3) while the
     target grows into the frame; the target itself comes up to full strength;
   - nest: the inner view, on an opaque backdrop the size of its frame, comes in over the target early (e 0.10-0.32),
     so that the tile turns into the view inside it and no frame is ever empty; the outer view's context stays, set
     back, until the zoom has pushed it off the screen (e 0.86-1), or until the inner covers the screen (a scale passed
     off its centre);
   - jump: the two views cross-fade around the middle (in 0.40-0.65, out 0.55-0.80);
   - the inner view's labels come last, once they are readable (e 0.62-0.88; a jump's 0.80-0.95).
   A view the camera only passes through (s.midOut, s.midIn) shows no labels (not painted, .nolab) and keeps its context
   set back, so that it does not flicker up at the camera's top speed. A view the camera rests at starts from how it
   looks (a tour step's or a flow's dimming, measured) or ends at the look it will have (s.end). */
const COV0 = 0.8;
function cover(V, T) {
  const w = Math.min(V.x + V.w, T.x + T.w) - Math.max(V.x, T.x), h = Math.min(V.y + V.h, T.y + T.h) - Math.max(V.y, T.y);
  return w > 0 && h > 0 ? Math.sqrt(w * h / (V.w * V.h)) : 0;
}
const BANDS = {nest: {ii: [0.1, 0.32], oo: [0.86, 1], li: [0.62, 0.88]}, jump: {ii: [0.4, 0.65], oo: [0.55, 0.8], li: [0.8, 0.95]}};
/* the shire and minion last entered: the scale control and the flows aim there */
function visited(P) {
  const i = pinfo(P);
  if (i.sid != null) LASTSID = i.sid;
  if (i.mi != null) { LASTNB = i.nb; LASTMI = i.mi; }
}
function openStep(s, req) {
  if (s.pan) return openPan(s, req);
  if (s.wrap) return openWrap(s, req);
  if (s.dir > 0) visited(s.P);
  const outer = built(s.P, s.o), inner = built(s.P, s.o + 1), A = s.A, B = s.B, bd = BANDS[s.kind] || BANDS.nest;
  const tgt = s.tgt;
  const vo = viewOf(s.P[s.o]), vi = viewOf(s.P[s.o + 1]);
  const P = {midOut: !!s.midOut, midIn: !!s.midIn};
  let rest = FULL, tRest = FULL, his = [];
  const sibs = ctxList(outer, tgt);
  if (P.midOut) rest = tRest = {o: CTX_LOW, s: 1};
  else if (s.dir > 0) {
    // the view the camera leaves, as it looks now (measured before any of the zoom's marks go on)
    const looks = sibs.map(lookOf);
    rest = looks.reduce((m, l) => (l.o < m.o ? l : m), FULL);
    tRest = lookOf(tgt);
    his = sibs.filter((x, i) => looks[i].o > rest.o + 0.1);
    clearDim();
  } else rest = tRest = s.end || FULL;
  ctxClear(outer); ctxClear(inner);
  sibs.forEach(x => x.classList.add('zdim')); his.forEach(x => x.classList.add('zhi'));
  if (tgt) tgt.classList.add('ztgt');
  if (P.midIn) ctxList(inner, null).forEach(x => x.classList.add('zdim'));
  const keep = strokeKeeper(outer);
  // a flow's packet rides the zoom at its own size, above both views, so that it never fades out between two legs
  let cg = null, p0 = null, inOuter = false;
  const carry = req.o.carry;
  if (carry && carry.isConnected && !REDUCED && !(req.o.total === 0)) {
    const cl = carry.closest('.lay'), m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(carry.getAttribute('transform') || '');
    if (m && (cl === outer || cl === inner)) { p0 = {x: +m[1], y: +m[2]}; inOuter = cl === outer; cg = carry.cloneNode(true); svg.appendChild(cg); carry.style.visibility = 'hidden'; }
  }
  // style writes only when a value changed (a frame's custom properties restyle the layer)
  const st = {oo: -1, io: -1, ol: '', il: '', nol: null, nil: null, sky: null};
  const setLab = (L, v, k) => { const nl = v <= 0; if (nl !== st[k]) { st[k] = nl; L.classList.toggle('nolab', nl); } };
  const frame = (e, R0) => {
    // R0: where the target is (in the drawing's units, before the view), from the leg's one zoom (else the step's own)
    const R = R0 || zoomR(A, B, e), Mo = rmap(A, R), Mi = rmap(B, R);
    const V = vmat(isVB(vo) && isVB(vi) ? VB : lerpR(vo, vi, e));
    setT(outer, cmpM(V, Mo)); setT(inner, cmpM(V, Mi));
    let oo = 1 - band(e, bd.oo[0], bd.oo[1]);
    // a nest passed off its centre: the outer view goes once the inner, fully in, covers the screen
    if (s.kind !== 'jump' && e > 0.32) { const scr = simR(simInv(Mi), isVB(vo) && isVB(vi) ? VB : lerpR(vo, vi, e)), cv = cover(scr, B); if (cv > COV0) oo = Math.min(oo, 1 - band(cv, COV0, 1) * band(e, 0.32, 0.45)); }
    const k = easeS(band(e, 0, 0.3)), so = outer.style;
    if (Math.abs(oo - st.oo) > 1e-4) { st.oo = oo; so.opacity = oo; so.visibility = oo > 0 ? '' : 'hidden'; }
    const io = band(e, bd.ii[0], bd.ii[1]);
    if (Math.abs(io - st.io) > 1e-4) { st.io = io; inner.style.opacity = io; }
    const ol = P.midOut ? 0 : 1 - band(e, 0.02, 0.2), il = P.midIn ? 0 : band(e, bd.li[0], bd.li[1]);
    so.setProperty('--lab', ol.toFixed(3)); setLab(outer, ol, 'nol');
    so.setProperty('--ctx', lerp(rest.o, CTX_LOW, k).toFixed(3));
    so.setProperty('--sat', lerp(rest.s, 1, k).toFixed(3));
    so.setProperty('--ctxh', lerp(1, CTX_LOW, k).toFixed(3));
    so.setProperty('--tgt', lerp(tRest.o, 1, k).toFixed(3));
    so.setProperty('--tsat', lerp(tRest.s, 1, k).toFixed(3));
    outer.classList.toggle('zsat', (rest.s < 0.999 || tRest.s < 0.999) && k < 0.999);
    inner.style.setProperty('--lab', il.toFixed(3)); setLab(inner, il, 'nil');
    inner.style.setProperty('--ctx', String(CTX_LOW));
    if (oo > 0) keep.set(Mo[0]);
    // the whole box is night sky while the view mostly shown is in space (CSS #chip.skyon): between two levels in
    // space throughout, from Earth to the US until the globe fades (the colour itself fades, CSS)
    const sky = !!(oo > 0.5 && e < 0.9 ? outer._sky : inner._sky); if (sky !== st.sky) { st.sky = sky; svg.classList.toggle('skyon', sky); }
    if (cg) {
      const M = cmpM(V, inOuter ? Mo : Mi), q = {x: M[0] * p0.x + M[1], y: M[0] * p0.y + M[2]};
      if (V) cg.setAttribute('transform', `translate(${q.x.toFixed(1)},${q.y.toFixed(1)}) scale(${V[0].toFixed(4)})`); else at(cg, q);
    }
    readout(s, e);
  };
  // the first frame goes on before either view is shown: a view un-hidden at full size and full opacity would be
  // painted for one frame
  frame(s.e0);
  outer.style.display = ''; inner.style.display = '';
  svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.add('busy'));
  outer.classList.add('zout');
  return {
    s, P, frame,
    /* a plan redirected mid-step: what the views on either side are now (only the flags change) */
    update: x => { P.midOut = !!x.midOut; P.midIn = !!x.midIn; },
    close: (e1, last, arrive) => {
      frame(e1);
      if (cg) { cg.remove(); carry.style.visibility = ''; }
      keep.done();
      outer.classList.remove('zout', 'nolab'); inner.classList.remove('nolab'); outer.style.visibility = '';
      const inIn = e1 >= 1, here = inIn ? inner : outer, gone = inIn ? outer : inner;
      gone.style.display = 'none'; ctxClear(gone);
      here.style.opacity = 1;
      Z.path = inIn ? s.P.slice() : s.P.slice(0, -1);
      bindTrio(Z.path);
      setT(here, restMat());
      if (PH && Z.level === 0) foldSoon();
      // the view the camera rests at loses the zoom's marks (the dimming that the step puts on arrives in the same
      // frame, arrive()); a view passed through keeps them for the next step
      if (last) { if (arrive) arrive(); ctxClear(here); svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.remove('busy')); }
      scaleUI();
    },
  };
}
/* a glide between two siblings: both views at one scale, side by side as in their parent's drawing (which is not
   shown); their labels dip to 0.4 on the way */
function openPan(s, req) {
  visited(s.T);
  const L1 = built(s.P, s.o + 1), L2 = built(s.T, s.o + 1);
  const v1 = viewOf(s.P[s.o + 1]), v2 = viewOf(s.T[s.o + 1]);
  const End = cmpM(s.Q2, simInv(s.Q1));   // the first view's transform when the second rests
  const M21 = cmpM(s.Q1, simInv(s.Q2));   // the second's coordinates in the first's
  const frame = q => {
    const M1 = simZoom(ID, End, q), M2 = cmpM(M1, M21), V = vmat(isVB(v1) && isVB(v2) ? VB : lerpR(v1, v2, q));
    setT(L1, cmpM(V, M1)); setT(L2, cmpM(V, M2));
    const lab = (1 - 0.6 * Math.sin(Math.PI * clamp(q, 0, 1))).toFixed(3);
    L1.style.setProperty('--lab', lab); L2.style.setProperty('--lab', lab);
    readout(s, q);
  };
  ctxClear(L1); ctxClear(L2); clearDim();
  L1.classList.add('pan'); L2.classList.add('pan');
  frame(0);
  L1.style.display = ''; L2.style.display = ''; L1.style.opacity = 1; L2.style.opacity = 1;
  svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.add('busy'));
  PANKEEP = L1;
  return {
    s, frame, update: () => {},
    close: (e1, last, arrive) => {
      const to = e1 >= 0.5, here = to ? L2 : L1, gone = to ? L1 : L2;
      frame(to ? 1 : 0);
      gone.style.display = 'none'; ctxClear(gone); gone.style.removeProperty('--lab'); here.style.removeProperty('--lab');
      L1.classList.remove('pan'); L2.classList.remove('pan');
      Z.path = (to ? s.T : s.P).slice();
      bindTrio(Z.path);
      setT(here, restMat());
      if (last) { if (arrive) arrive(); svg.querySelectorAll(':scope > g.lay').forEach(l => l.classList.remove('busy')); }
      scaleUI();
    },
  };
}
let PANKEEP = null;
/* The camera's curve: one ease over the whole move, so that a zoom from the chip to a minion accelerates once and
   slows once, with no stop at the shire. A cubic whose start speed is m (0: from rest, its top speed 1.5 times the
   mean; a move redirected on its way starts at the speed it had) and whose end speed is 0. */
const herm = (u, m) => m * (u * u * u - 2 * u * u + u) + 3 * u * u - 2 * u * u * u;
const hermD = (u, m) => m * (3 * u * u - 4 * u + 1) + 6 * u - 6 * u * u;
/* a move's length: per ms for each unit of log scale, but a long move (the chip to a minion and further) is
   compressed, so that no move takes much more than 1.7 s (2.5 s from a minion to one in another shire); since 30
   September a reader's move is capped at 4.5 s (the universe to the die is 17 steps), a single jump at 1.1 s */
const moveMs = (cost, per) => { const t = per * cost; return cost <= 3 ? t : per * 3 + (t - per * 3) * 0.32; };
const MOVECAP = 4500, JUMPCAP = 1100, WRAPCAP = 1500;
/* a timeline on real time (the reader's own zoom) or on the animation clock (a flow's or the tour's camera, which
   Space stops); fn(t) runs at once for t = 0, then every frame. stop() true: a newer request came in; the timeline
   stops where it is and resolves false. A clock timeline whose token died goes on in real time, so that a stopped
   flow never leaves the camera halfway. */
/* a timeline that stopped for a newer request, in a frame it did not draw: when it last drew (prev) and this frame
   (now). The next timeline, started in the same frame, draws a whole frame's step at once, so a redirect never shows
   the same position twice */
let HAND = null;
function timeline(T, fn, clk, stop) {
  return new Promise(res => {
    let done = false;
    const fin = ok => { if (!done) { done = true; res(ok); } };
    const step = t => { try { fn(t); } catch (e) { console.error(e); fin(true); return true; } return false; };
    const h = HAND && HAND.now === CLK.last ? HAND : null; HAND = null;
    if (REDUCED || T <= 0) { step(T); return fin(true); }
    const h0 = h ? Math.min(T, DTMAX, Math.max(0, h.now - h.prev)) : 0;
    if (clk) {
      let acc = h && (CLK.on || clk.dead) ? h0 : 0, drawn = CLK.last;
      if (step(acc)) return;
      const j = () => {
        if (done) { CLK.jobs.delete(j); return; }
        if (stop()) { CLK.jobs.delete(j); HAND = {prev: drawn, now: CLK.last}; fin(false); return; }
        if (CLK.on || clk.dead) acc += CLK.dt;
        const t = Math.min(T, acc); drawn = CLK.last;
        if (step(t) || t >= T) { CLK.jobs.delete(j); fin(true); }
      };
      CLK.jobs.add(j); return;
    }
    // from the last frame's time, so that the first frame of a move (or of a redirected one) is a whole frame's step;
    // each frame moves the time on by at most DTMAX
    const t0 = h ? h.prev : CLK.last && performance.now() - CLK.last < 100 ? CLK.last : performance.now();
    if (step(h0)) return;
    let drawn = h ? h.now : t0, acc = h0;
    const f = now => {
      if (done) return;
      if (stop()) { HAND = {prev: drawn, now}; fin(false); return; }
      acc += Math.min(DTMAX, Math.max(0, now - drawn)); drawn = now;
      const t = Math.min(T, acc);
      if (step(t) || t >= T) fin(true); else requestAnimationFrame(f);
    };
    requestAnimationFrame(f);
    setTimeout(() => { if (!done && !stop()) { step(T); fin(true); } }, T + 800);   // a hidden tab gets no frames
  });
}
/* The camera follows the latest request only: rapid presses never queue a chain of animations, and a request that
   comes in during a move redirects it from where it is, forwards or back, at the speed it had (a reversal slows to a
   stop first, 130 ms), with no jump. goTo() resolves once the view reaches the latest target. The target is a path,
   or a view of the flows' kind ({level, sid, nb, mi}). o.clk: a token whose clock (the pausable one) drives the move;
   o.ms: milliseconds per unit of log scale (0 for a cut); o.total: the whole move's length instead; o.keepFx: a flow's
   drawing rides it; o.carry: a flow's packet rides it; o.c1: the look the view ends at when the move ends on a zoom out
   (a step that dims it); o.arrive: run in the frame the camera arrives in (a step's highlight, so that it lands with no
   flash); o.atChip: the camera rests its eye on the chip halfway through an out-and-in move and this runs there (a
   flow's establishing shot); o.pan: a sibling beside this scale is reached by a glide. */
let ZT = null, ZW = false, ZWAIT = [], ZN = 0;
const zkey = () => pkeys(Z.path);
/* where the camera is going, else where it is: + and - step from there, so that a second press is never lost */
const zNow = () => pinfo(ZT ? ZT.t : Z.path);
function goTo(t, o) {
  o = o || {};
  let tp;
  if (Array.isArray(t)) tp = t.slice();
  else { const z = zNow(); tp = pathOf({level: t.level || 0, sid: t.sid == null ? (z.sid == null ? LASTSID : z.sid) : t.sid, nb: t.nb || 0, mi: t.mi || 0}); }
  // the same target again while the camera is on its way there (a stage stepped mid-move): the move goes on as it is
  const same = ZW && ZT && samePath(ZT.t, tp);
  if (same && !o.total && o.ms !== 0) { if (o.focus) ZT.o.focus = true; ['arrive', 'c1'].forEach(k => { if (o[k]) ZT.o[k] = o[k]; }); return new Promise(res => ZWAIT.push(res)); }
  ZT = {t: tp, o, n: ++ZN};
  return new Promise(res => { ZWAIT.push(res); if (!ZW) { ZW = true; zoomWorker(); } scaleUI(); });
}
/* the warp of a leg whose steps take time out of proportion to their zoom (a jump: its readout sweeps the decades it
   skips): progress p (0-1) shares the leg's time by each step's cost, and maps to the leg's log position piecewise */
function legWarp(g) {
  const W = g.W, n = W.length - 1;
  g.span = W[n].l - W[0].l;
  const ws = g.sOf.map(s => Math.max(1e-9, s.L)), C = ws.reduce((a, b) => a + b, 0);
  g.cw = ws.map(w => w / C);
  g.uniform = g.sOf.every(s => s.kind !== 'jump');
}
const warpL = (g, p) => {   // progress -> log position along the leg
  const W = g.W, n = W.length - 1;
  if (g.uniform) return W[0].l + p * g.span;
  let c = 0;
  for (let i = 0; i < n; i++) { const w = g.cw[i]; if (p <= c + w || i === n - 1) { const f = w > 0 ? (i === n - 1 ? (p - c) / w : clamp((p - c) / w, 0, 1)) : 1; return W[i].l + f * (W[i + 1].l - W[i].l); } c += w; }
  return W[n].l;
};
const warpD = (g, p) => {   // d(log position)/dp
  if (g.uniform) return g.span;
  const W = g.W, n = W.length - 1; let c = 0;
  for (let i = 0; i < n; i++) { const w = g.cw[i]; if (p <= c + w || i === n - 1) return w > 0 ? (W[i + 1].l - W[i].l) / w : 0; c += w; }
  return g.span;
};
async function zoomWorker() {
  const from = Z.path.slice(), fromKey = zkey(), hadFocus = svg.contains(document.activeElement);
  let wantFocus = false, wantPanel = false;
  svg.classList.add('zmv'); pillOff(); menuOff();
  try {
    for (let guard = 0; ZT && guard < 40; guard++) {
      const req = ZT, t = req.t, stop = () => ZT !== req, clk = req.o.clk || null;
      if (req.o.focus) wantFocus = true;
      if (req.o.pfocus) wantPanel = true;
      // a glide or a wrap in flight is not turned: it lands where it is nearer, at once
      if (CUR && (CUR.s.pan || CUR.s.wrap)) { try { CUR.ctl.close(CUR.e >= 0.5 ? 1 : 0, true, null); } catch (e) { console.error(e); } CUR = null; }
      // turned back while moving: slow to a stop first (130 ms), then plan from rest
      if (CUR && CUR.ctl && Math.abs(CUR.v) > 2e-4 && !REDUCED && req.o.total !== 0 && req.o.ms !== 0) {
        const probe = planTo(t, req.o)[0];
        if (probe && probe.part && probe.dir * CUR.v < 0) {
          const Ls = CUR.s.lq, v = CUR.v, e0 = CUR.e, Tc = 130, c = CUR;
          const ok = await timeline(Tc, tt => { const q = tt / Tc, e = clamp(e0 + v * Tc * (q - q * q / 2) / Ls, 0, 1), R = c.Rof ? c.Rof(e) : null; c.ctl.frame(e, R); c.e = e; if (R) c.R = R; }, clk, stop);
          c.v = 0;
          if (!ok) continue;
        }
      }
      // a step left at its very end (a turn-back slowed to a stop there): the camera is at that view
      if (CUR && CUR.ctl && (CUR.e <= 1e-3 || CUR.e >= 1 - 1e-3)) { CUR.ctl.close(CUR.e < 0.5 ? 0 : 1, true, null); CUR = null; }
      let steps;
      try { steps = planTo(t, req.o); } catch (e) { console.error(e); if (ZT === req) ZT = null; break; }
      if (!steps.length) { if (ZT === req) ZT = null; break; }
      if (!req.o.keepFx) clearFx(true); else clearDim();
      // every scale the move enters is built before it starts (a build is a layout of a whole drawing: mid-move it
      // would be a late frame)
      try { steps.forEach(s0 => { if (s0.wrap) { built(s0.ring, 0); built(s0.other, s0.other.length - 1); } else if (s0.pan) { built(s0.P, s0.o + 1); built(s0.T, s0.o + 1); } else { built(s0.P, s0.o); built(s0.P, s0.o + 1); } }); } catch (e) { console.error(e); }
      const cost = costOf(steps);
      const user = !clk && req.o.total == null;
      const pan = steps.length === 1 && steps[0].pan;
      let T = req.o.total != null ? req.o.total : pan ? 380 + 260 * steps[0].dist : moveMs(cost, req.o.ms != null ? req.o.ms : 480);
      if (user && !pan) { T = Math.min(T, MOVECAP); if (steps.every(s => s.kind === 'jump')) T = Math.min(T, JUMPCAP * steps.length); if (steps.every(s => s.wrap)) T = Math.min(T, WRAPCAP * steps.length); T = Math.max(T, 110 * steps.length); }
      // a flow's or the tour's camera that starts off the chip's three scales (the reader had gone out to the universe
      // or down to the atom) comes back within the reader's cap; within the three its pace is as it was
      else if (!pan && req.o.total == null && steps.some(s => !TRIO.includes(s.P[s.P.length - 1].id))) T = Math.min(T, MOVECAP);
      // images a scale shows are decoded before the camera enters it
      const imgs = [];
      steps.forEach(s => { if (!s.pan && !s.wrap && s.dir > 0) { const N0 = NODES[s.P[s.o + 1].id]; if (N0.imgs) imgs.push(...N0.imgs(prm(s.P[s.o + 1]))); } });
      // (at most 300 ms, and not past a newer request: a slow or stalled image pops in later, as on the way out; review
      // of 1 Oct: with no limit the camera froze and queued every press until the decode settled)
      if (imgs.length && !REDUCED) {
        const t0 = performance.now();
        await Promise.race([imgReady(imgs), new Promise(r => { const tick = () => (ZT !== req || performance.now() - t0 > 300 ? r() : setTimeout(tick, 25)); tick(); })]);
        if (ZT !== req) continue;
      }
      // going on the same way: start at the speed the camera has
      let m = 0;
      if (steps[0].part && CUR && !steps[0].pan) {
        const v = steps[0].dir * CUR.v;
        if (v > 1e-5 && T > 0) { m = v * T / cost; if (m > 2.5) { T = 2.5 * cost / v; m = 2.5; } }
      }
      // the legs: the steps one way (in, or out) are one leg, eased once, and a leg out and a leg in meet at rest, where
      // the move turns
      const legs = [], legOf = [];
      steps.forEach((s, i) => { const g = legs[legs.length - 1], solo = !!(s.pan || s.wrap); if (g && !g.pan && !solo && g.dir === s.dir) g.ix.push(i); else legs.push({dir: s.dir, ix: [i], pan: solo}); });
      let ca = 0;
      legs.forEach((g, k) => { g.ix.forEach(i => { legOf[i] = g; }); g.cost = g.ix.reduce((c, i) => c + steps[i].L, 0); g.T0 = cost > 0 ? T * ca / cost : 0; ca += g.cost; g.T1 = cost > 0 ? T * ca / cost : T; g.m = k === 0 ? m : 0; });
      if (steps[0].part && CUR && CUR.ctl) CUR.ctl.update(steps[0]);
      let ci = 0, ctl = steps[0].part && CUR ? CUR.ctl : null;
      const startR = steps[0].part && CUR ? CUR.R : null;
      // a leg's waypoints, each a view at rest (or the start, partway) in the coordinates of a scale on it (d): the
      // leg's log position l, with the rests at the scales' log scale; a frame interpolates between two of them, in the
      // coordinates of the outer of the two (at most one map, through one step)
      const legPath = g => {
        const ss = g.ix.map(i => steps[i]), byO = ss.slice().sort((x, y) => x.o - y.o);
        g.a = byO[0].o; g.st = byO; g.lam = [0];
        byO.forEach((s, j) => g.lam.push(g.lam[j] + s.lq));
        const first = ss[0];
        let W0;
        if (first.part && startR) { const M = rmap(first.A, startR); W0 = {d: first.o, M, l: g.lam[first.o - g.a] + Math.log(M[0])}; }
        else if (g.dir > 0) W0 = {d: g.a, M: ID, l: 0};
        else W0 = {d: g.a + byO.length, M: ID, l: g.lam[byO.length]};
        g.W = [W0].concat(ss.map(s => { const r = s.o - g.a + (g.dir > 0 ? 1 : 0); return {d: g.a + r, M: ID, l: g.lam[r]}; }));
        g.sOf = ss;
        legWarp(g);
      };
      // a layer's transform at depth d1 as the transform of the layer at d2 (|d1 - d2| <= 1), through the step between
      const reD = (g, M, d1, d2) => {
        if (d1 === d2) return M;
        if (d2 === d1 - 1) return cmpM(M, g.st[d2 - g.a].Q);
        if (d2 === d1 + 1) return cmpM(M, simInv(g.st[d1 - g.a].Q));
        throw new Error(`no map from depth ${d1} to ${d2}`);
      };
      const on = (g, i, l) => {
        const a = g.W[i], b = g.W[i + 1], d = Math.min(a.d, b.d), dl = b.l - a.l;
        return {d, M: simZoom(reD(g, a.M, a.d, d), reD(g, b.M, b.d, d), Math.abs(dl) > 1e-9 ? (l - a.l) / dl : 1)};
      };
      // the view at log position l of leg g: its scale geometric in l, its place on the blended path (around each rest
      // the two zooms blend over BLEND of the shorter's log length, in that rest's own coordinates)
      const legG = (g, l) => {
        const W = g.W, n = W.length - 1, dir = W[n].l >= W[0].l ? 1 : -1;
        let i = 0; while (i < n - 1 && (l - W[i + 1].l) * dir > 0) i++;
        let G = on(g, i, l);
        for (let b = Math.max(1, i); b <= Math.min(n - 1, i + 1); b++) {
          const w = BLEND * Math.min(Math.abs(W[b].l - W[b - 1].l), Math.abs(W[b + 1].l - W[b].l)), dd = (l - W[b].l) * dir;
          if (w > 1e-9 && Math.abs(dd) < w) {
            const x = (dd + w) / (2 * w), beta = x * x * (3 - 2 * x), A = on(g, b - 1, l), B = on(g, b, l), d = W[b].d;
            const SA = reD(g, A.M, A.d, d), SB = reD(g, B.M, B.d, d);
            G = {d, M: [SA[0], lerp(SA[1], SB[1], beta), lerp(SA[2], SB[2], beta)]};
          }
        }
        return G;
      };
      // step s of leg g where the leg's view is G: how far the step has gone (e), and where its target is
      // (a frame more than one scale away from the step, as a cut's single frame is, has passed it or not reached it)
      const stepAt = (g, s, G) => {
        if (G.d > s.o + 1) return {e: 1, R: null};
        if (G.d < s.o) return {e: 0, R: null};
        const Mo = reD(g, G.M, G.d, s.o); return {e: clamp(Math.log(Mo[0]) / s.lq, 0, 1), R: simR(Mo, s.A)};
      };
      const drive = tt => {
        let kk = 0; while (kk < legs.length - 1 && tt >= legs[kk].T1 - 1e-9) kk++;
        const gk = legs[kk], Tk = gk.T1 - gk.T0, u = Tk > 0 ? clamp((tt - gk.T0) / Tk, 0, 1) : 1, p = herm(u, gk.m);
        const fin = tt >= T - 1e-9;
        while (ci < steps.length) {
          const s = steps[ci], g = legOf[ci], last = ci === steps.length - 1;
          if (!ctl) ctl = openStep(s, req);
          if (s.pan || s.wrap) {
            if (g === gk && (u < 1 || (last && !fin))) { ctl.frame(p); CUR = {s, e: p, dir: 1, v: 0, ctl}; break; }
          } else {
            if (!g.W) legPath(g);
            if (g === gk) {
              const G = legG(g, warpL(g, p)), at = stepAt(g, s, G);
              const reached = s.dir > 0 ? at.e >= 1 - 1e-7 : at.e <= 1e-7;
              if (!reached || (last && !fin)) {
                ctl.frame(at.e, at.R);
                CUR = {s, e: at.e, dir: s.e1 > s.e0 ? 1 : -1, v: Tk > 0 ? warpD(g, p) * hermD(u, gk.m) / Tk : 0, ctl, R: at.R,
                  // where the target is for another e of this step, on the leg's path (a turn-back slows along it)
                  Rof: e => stepAt(g, s, legG(g, g.lam[s.o - g.a] + e * s.lq)).R};
                break;
              }
            }
          }
          ctl.close(s.e1, last, last ? req.o.arrive : null);
          ctl = null; ci++; CUR = null;
          if (!last && Z.level === 0 && req.o.atChip && !req.atChipDone) { req.atChipDone = true; req.o.atChip(); }
        }
      };
      const ok = await timeline(T, drive, clk, stop);
      if (ok && ZT === req) ZT = null;
    }
  } catch (e) { console.error(e); }
  ZT = null; ZW = false;
  if (CUR) { try { CUR.ctl.close(CUR.e >= 0.5 ? 1 : 0, true, null); } catch (e) { console.error(e); } CUR = null; }
  svg.classList.remove('zmv');
  prune(PANKEEP ? new Set([PANKEEP]) : null); PANKEEP = null;
  skyBg();
  readout(null);
  if (fromKey !== zkey()) {
    select(null);
    // the panel, the crumbs and the prefetch after the frame the camera lands in (review of 1 Oct: built inside it,
    // they made the last frame of every move a long one); __chipState reports the move until they are done
    const fin = () => {
      UIP = false;
      if (ZW) return;   // a newer move took over: its own end does this
      // (the code that awaited the move may have selected a part already, a neighbour link's cell: its panel and its
      // focus stand)
      const late = !!SEL;
      scaleUI(true); arrived(from);
      if (late) return;
      if (hadFocus || wantFocus) { const f = zoomFocus(from); if (f) f.focus({preventScroll: true}); }
      if (wantPanel) { const b = $('pn-body').querySelector('.pn-zoom button'); (b || $('pn-body')).focus({preventScroll: true}); }
    };
    if (REDUCED) fin(); else { UIP = true; setTimeout(fin, 0); }
  } else scaleUI();
  const w = ZWAIT; ZWAIT = []; w.forEach(r => r());
}
let UIP = false;
/* at rest, the box is night sky where the level shown is in space */
function skyBg() { const L = restLayer(); svg.classList.toggle('skyon', !!(L && L._sky)); }
/* images a scene shows, decoded before the camera enters it (a first frame never waits for a decode) */
const IMGDONE = new Set();
function imgReady(list) {
  const todo = list.filter(u => u && !IMGDONE.has(u));
  if (!todo.length) return Promise.resolve();
  return Promise.all(todo.map(u => { const im = new Image(); im.src = u; return (im.decode ? im.decode() : Promise.resolve()).then(() => IMGDONE.add(u), () => IMGDONE.add(u)); }));
}
/* after a zoom, focus the part zoomed out of, else the first part of the new view */
function zoomFocus(from) {
  const L = restLayer(); if (!L) return null;
  // arrived by a neighbour link: the link back to the shire left, so that Tab and Enter return
  const nbk = NBRBACK; NBRBACK = null;
  const fi = pinfo(from);
  if (nbk && Z.level === 1 && fi.level === 1 && fi.sid === nbk.sid && AP[1].nbr && AP[1].nbr[nbk.dir]) return AP[1].nbr[nbk.dir];
  if (from.length > Z.path.length && samePath(from.slice(0, Z.path.length), Z.path)) {
    const s = L._ap.zs[pk(from[Z.path.length])]; if (s && s.g && s.g.isConnected) return s.g;
  }
  // a glide to a sibling: its part in the same place, else the first part
  return L.querySelector('.comp');
}
/* the reader's own zoom: while a flow plays, the camera stops following it (stepping a stage turns it back on),
   and the flow's stage is drawn again where the camera now is */
function userNav(t, o) {
  hideTip(); pillOff(); menuOff();
  // a flow, playing or finished, stays: its stage is drawn again at the new scale (a finished one as its last stage's
  // end state, still finished), so the arrows keep stepping its stages
  const k = FL.k, done = FL.done;
  if (k) { FL.tok.dead = true; if (FOLLOW) setFollow(false, true); }
  return goTo(t, Object.assign({focus: svg.contains(document.activeElement), user: true}, o || {})).then(() => {
    if (!k || FL.k !== k || ZW) return;
    // the flow waits off the chip's three scales, paused (Play or a step brings the camera back to its stage; review of
    // 1 Oct: its clock ran on, with nothing to show)
    if (Z.level < 0 || Z.level > 2) { if (CLK.on && !done) { CLK.on = false; playBtn(); renderBar(); } return; }
    if (done) startFlow(k, FL.i, {still: true, keep: true, done: true});
    else restartStage();
  });
}
/* an HTML element (E makes SVG ones) */
const H = (tag, attrs, parent) => { const e = document.createElement(tag); Object.entries(attrs || {}).forEach(([k, v]) => { if (v != null) e.setAttribute(k, v); }); if (parent) parent.appendChild(e); return e; };
/* ---- names and sizes of the scales ---- */
const nameOf = el => { const N0 = NODES[el.id]; return N0 ? N0.name(prm(el)) : el.id; };
const shortOf = el => { const N0 = NODES[el.id]; return N0 && N0.short ? N0.short(prm(el)) : nameOf(el); };
/* the name inside a sentence ("Zoom out to the chip", "Zoom into shire 20") */
const toOf = el => { const N0 = NODES[el.id]; return N0 && N0.to ? N0.to(prm(el)) : nameOf(el).replace(/^The /, 'the '); };
/* a path from its string (?at=, the panel's buttons): elements by '/', each id or id:params */
const pathFrom = s => String(s || '').split('/').filter(Boolean).map(elOf);
/* a length for a reader: the unit that keeps it between 1 and 1,000 (light-years beyond a tenth of one) */
const LY = 9.4607304725808e15;
function fmtLen(m, sig) {
  sig = sig || 3;
  const r = (v, u) => { const t = Number(v.toPrecision(sig)); return (t >= 1000 ? t.toLocaleString('en-US', {maximumFractionDigits: 0}) : String(t)) + ' ' + u; };
  if (!(m > 0)) return '';
  if (m >= 0.1 * LY) { const y = m / LY; return y >= 1e9 ? r(y / 1e9, 'billion ly') : y >= 1e6 ? r(y / 1e6, 'million ly') : r(y, 'ly'); }
  if (m >= 1e12) return r(m / 1e12, 'billion km');
  if (m >= 1e9) return r(m / 1e9, 'million km');
  if (m >= 1000) return r(m / 1000, 'km');
  if (m >= 1) return r(m, 'm');
  if (m >= 0.1) return r(m * 100, 'cm');
  if (m >= 1e-3) return r(m * 1e3, 'mm');
  if (m >= 1e-6) return r(m * 1e6, 'µm');
  if (m >= 1e-10) return r(m * 1e9, 'nm');
  // (since 1 Oct the ladder goes on down: the atom in picometres, the nucleus and the proton in femtometres, then powers
  // of ten)
  if (m >= 1e-12) return r(m * 1e12, 'pm');
  if (m >= 1e-16) return r(m * 1e15, 'fm');
  const e = Math.floor(Math.log10(m) + 1e-9), mt = Number((m / Math.pow(10, e)).toPrecision(sig));
  return `${mt} × 10${String(e).split('').map(c => SUP[c]).join('')} m`;
}
const SUP = {'-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹'};
const pow10 = m => '10' + String(Math.floor(Math.log10(m) + 1e-9)).split('').map(c => SUP[c]).join('') + ' m';
/* a scale's size as the Up bar and the panel print it: ≈ for an inference or an estimate */
const APPROX = new Set(['inferred', 'unknown']);
/* one word for each kind of fact, the same on both pages (DESIGN §3.3: the chip printed "spec", the memory levels
   "documented"; 1 Oct) and a caveat's words */
const KWORD = {measured: 'measured', spec: 'documented', derived: 'model', inferred: 'inference', outside: 'outside source', generic: 'textbook', owner: 'the owner’s word', hypothesis: 'speculative', unknown: 'unknown · asked'};
const CAVW = {'erbium-rtl': 'Erbium RTL', 'spec-v1.1': 'spec v1.1', reimpl: 're-implementation RTL'};
/* (since 1 Oct a size may be a bound, a quark's or an electron's: no size measured, "< 4.3 × 10⁻¹⁹ m"; and the ring
   of sizes has none: it is a picture, "↻ conceptual link") */
const sizeTxt = sz => (!sz ? '' : sz.conceptual ? '↻ conceptual link' : sz.bound ? sz.bound.txt : sz.m > 0 ? (APPROX.has(sz.kind) ? '≈ ' + fmtLen(sz.m, 2) : fmtLen(sz.m)) : '');
const sizeWords = sz => (!sz ? 'size unknown' : sz.conceptual ? 'a picture of all sizes, not a place' : sz.bound ? sz.bound.words
  : sz.m > 0 ? (APPROX.has(sz.kind) ? 'about ' + fmtLen(sz.m, 2) : fmtLen(sz.m)) + ' across' : 'size unknown');
const sizeHtml = sz => (!sz ? '<span>size unknown</span>' : sz.conceptual ? '<span class="ro-ring">↻ conceptual link</span>'
  : sz.bound ? `<span class="num"${sz.f ? ` data-f="${esc(sz.f)}"` : ''}>${esc(sz.bound.txt)}</span> · no size measured`
  : !(sz.m > 0) ? '<span>size unknown</span>'
  : `<span class="${APPROX.has(sz.kind) ? 'inf ' : ''}num"${sz.f ? ` data-f="${esc(sz.f)}"` : ''}>${esc(sizeTxt(sz))}</span>${ro10(sz.m)}`);
/* the readout's power of ten after a length, unless the length is written as one (below a tenth of a femtometre) */
function ro10(m) { return m >= 1e-16 ? ' · ' + pow10(m) : ''; }
/* a scale's size from its record in the data (D.scales): metres, kind and fact, a bound, or none (the ring) */
const scSz = s => (!s ? null : s.conceptual ? {m: null, kind: 'unknown', conceptual: true} : s.m > 0 ? {m: s.m, kind: s.kind, f: s.f || null, bound: s.bound || null} : null);
/* ---- the easter egg (the owner, 1 Oct 2026, 07:25): the levels above the rack are never named in advance. A scale
   flagged egg (D.scales) shows its own name once the camera is there, but the Up button, the breadcrumb, its menu and
   the panel's "zoom out" call a level of the egg further out "?" ---- */
const egg = el => !!(el && NODES[el.id] && NODES[el.id].egg);
/* the facts no list in the page may show in advance: those of the easter egg's levels (their own facts and sizes, unless
   a level outside the egg cites them too), and any whose statement names one of its levels */
function eggFacts() {
  const S0 = D.scales || {}, eggF = new Set(), pub = new Set(), names = [];
  Object.entries(S0).forEach(([id, s]) => {
    (s.facts || []).concat(s.f ? [s.f] : []).forEach(f => (s.egg ? eggF : pub).add(f));
    if (s.egg) [s.name, s.short].forEach(t => { if (t && t.length > 3) names.push(String(t).replace(/\s*\(.*$/, '').replace(/^The /, '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); });
  });
  pub.forEach(f => eggF.delete(f));
  const rx = names.length ? new RegExp('\\b(' + [...new Set(names)].join('|') + ')\\b') : null;
  if (rx) Object.entries(F).forEach(([id, f]) => { if (rx.test(f.statement || '')) eggF.add(id); });
  return eggF;
}
/* ---- what a part zooms into ---- */
/* the scale a part's double-click enters: a scale inside the one it is drawn in ({id, k}), or {up: id}, a scale further
   out that the part stands for (the host beside the die); null: no closer drawing */
/* the other zooms a part offers, by its key: [{lab, to: path, made}] (filled in by the scales below the shire) */
const OPTS = {};
const KIDS = {
  cshire: c => ({id: 'shire', k: String(c.cell.id)}),
  master: c => ({id: 'shire', k: String(c.cell.r === 0 ? 32 : 33)}),
  minion: c => (c.mi != null ? {id: 'minion', k: `${c.sid}.${c.nb}.${c.mi}`} : null),
};
function kidOf(g) {
  if (!g) return null;
  if (g._kid !== undefined) return g._kid;
  const f = KIDS[g._key], k = f ? f(g._ctx || {}, g) : null;
  return k && (k.up ? NODES[k.up] : NODES[k.id]) ? k : null;
}
/* the path of the scale a part is drawn in */
const layerPath = g => { const L = g && g.closest && g.closest('g.lay'); return L && L._path ? L._path : null; };
/* the path to a scale further out, by its id (the host from the die) */
const upPath = id => { const P = zNow().path, i = P.findIndex(e => e.id === id); return i >= 0 ? P.slice(0, i + 1) : null; };
/* the default child of the scale at the end of P (the + key, the breadcrumb's next crumb) */
function defKid(P) {
  const el = P[P.length - 1], N0 = NODES[el.id];
  const k = N0 && N0.def ? N0.def(prm(el), P) : null;
  return k && NODES[k.id] ? k : null;
}
/* ---- the wrap (1 Oct 2026, the owner: "when I zoom out to observable universe, I get elementary particles, quarks ...
   and then maybe I end up in one of the computing transistor units ... or one of the memory units"): the ring of sizes,
   p.wrap, is a root of its own. Up from the top of the ladder (beyond) goes to the ring; Up from the ring goes in at the
   Planck length under one of the page's ways back in (pageExits: a memory cell or a compute gate), and every Up after
   that climbs: quark, proton, nucleus, atom, crystal, channel, fin, FinFET, the cell or the gate, and on up through the
   page's own scales. + runs the loop backwards: from the Planck length to the ring, from the ring to beyond. A move onto
   or off the ring is a cross-fade with a marker running along the ring (a wrap step), never a zoom through space. ---- */
const WRAP = 'p.wrap', PLANCK = 'p.planck';
const isWrap = P => P.length === 1 && P[0].id === WRAP;
let LASTEXIT = null;
/* the way back in that Up takes from the ring: the other one from last time round, the page's first the first time */
function upExit() {
  const xs = typeof pageExits === 'function' ? pageExits() : [];
  if (!xs.length) return null;
  const i = xs.findIndex(x => x.id === LASTEXIT);
  return xs[i < 0 ? 0 : (i + 1) % xs.length];
}
/* the path from P down its default chain to the Planck length (a way back in from the ring) */
function chainTo(P, id) { let Q = P.slice(); for (let i = 0; i < 60 && Q[Q.length - 1].id !== id; i++) { const k = defKid(Q); if (!k) return null; Q = Q.concat([k]); } return Q[Q.length - 1].id === id ? Q : null; }
/* Up from P: its parent; at the top of the ladder, the ring; on the ring, in at the Planck length */
function upOf(P) {
  if (isWrap(P)) { const x = upExit(); return x ? x.path() : null; }
  if (P.length > 1) return P.slice(0, -1);
  return P[0].id === 'beyond' && NODES[WRAP] ? [{id: WRAP}] : null;
}
/* + from P with nothing selected: the default child; round the ring from the Planck length, and from the ring to the top */
function nextOf(P) {
  if (isWrap(P)) return NODES.beyond ? [{id: 'beyond'}] : null;
  if (P[P.length - 1].id === PLANCK && NODES[WRAP]) return [{id: WRAP}];
  const k = defKid(P); return k ? P.concat([k]) : null;
}
/* the scales a scene offers to zoom into, the default first */
function kidsOf(P) {
  const el = P[P.length - 1], N0 = NODES[el.id], d = defKid(P);
  const ks = (N0 && N0.kids ? N0.kids(prm(el), P) : []).filter(k => k && NODES[k.id]);
  if (d && !ks.some(k => pk(k) === pk(d))) ks.unshift(d);
  return ks;
}
function zoomBy(d) {
  const P = zNow().path;
  if (d < 0) { const U = upOf(P); if (U) return userNav(U); return; }
  // in: the selected part's own scale, else the scale's default child
  if (SEL && SEL.isConnected) {
    const lp = layerPath(SEL), k = kidOf(SEL);
    if (SEL._go && lp && samePath(lp, P)) return userNav(SEL._go());   // a way back in from the ring: a path of its own
    if (k && !k.up && lp && samePath(lp, P)) return userNav(P.concat([k]));
  }
  const N = nextOf(P); if (N) return userNav(N);
}
/* a button that has nothing to do (the last stage's Next, the Up bar at the top): marked disabled (aria-disabled,
   dimmed) but kept focusable, so that the keyboard's focus never falls to the page and a repeated Enter does nothing */
function setDis(b, dis) { b.setAttribute('aria-disabled', String(!!dis)); b.classList.toggle('dis', !!dis); }
const isDis = b => b.getAttribute('aria-disabled') === 'true';
/* ---- the Up bar: the wide button, the breadcrumb and the readout (drawn for where the camera is going) ---- */
let UPKEY = '';
function scaleUI(force) {
  const P = zNow().path, key = pkeys(P) + '|' + PH;
  plusUI(P);
  if (!force && key === UPKEY) return;
  UPKEY = key;
  const b = $('up'), U = upOf(P);
  if (!U) {
    b.innerHTML = '<span class="up-t">Top of the ladder</span>';
    setDis(b, true); b.setAttribute('aria-label', 'Top of the ladder'); b.title = '';
  } else if (isWrap(P)) {
    // the ring: Up goes round it, in at the Planck length (the readout shows no size: the ring is a picture)
    const x = upExit();
    b.innerHTML = `<span class="up-t">↑ Round the ring: in at the Planck length</span>`;
    setDis(b, false); b.setAttribute('aria-label', `Round the ring: in at the Planck length, then up ${x ? 'through ' + x.lab : ''}`); b.title = 'Round the ring (Backspace or −)';
  } else {
    const par = U[U.length - 1], sz = sizeOf(par);
    if (egg(par)) {
      // a level of the easter egg further out: never named in advance
      b.innerHTML = '<span class="up-t">↑ ?</span>';
      setDis(b, false); b.setAttribute('aria-label', 'Zoom out: ?'); b.title = 'Zoom out one level (Backspace or −)';
    } else {
      b.innerHTML = `<span class="up-t">↑ Zoom out to ${esc(toOf(par))}</span>` + (sz && (sz.m > 0 || sz.bound) ? `<span class="up-s">· ${esc(sizeTxt(sz))}</span>` : '');
      setDis(b, false); b.setAttribute('aria-label', `Zoom out to ${toOf(par)}, ${sizeWords(sz)}`); b.title = 'Zoom out one level (Backspace or −)';
    }
  }
  // the readout first: the crumbs fold to the width it leaves them (review of 1 Oct: measured before it, the crumbs
  // overflowed and clipped the + button)
  if (!ZW) roRest();
  crumbsUI(P);
}
/* the crumbs of a path: one per scale, except that a run of the easter egg's levels further out than the current one is
   one "?" crumb (it goes to the nearest of them) */
function crumbItems(P) {
  const out = [];
  P.forEach((el, i) => {
    const cur = i === P.length - 1;
    if (egg(el) && !cur) {
      const last = out[out.length - 1];
      if (last && last.egg) { last.ci = i; return; }
      out.push({ci: i, t: '?', title: 'Further out: press to see', egg: true});
      return;
    }
    out.push({ci: i, t: (isWrap(P) ? '↻ ' : '') + shortOf(el), title: nameOf(el), cur});
  });
  return out;
}
function crumbsUI(P) {
  const nav = $('crumbs'), fi = document.activeElement && nav.contains(document.activeElement) ? document.activeElement.dataset.ci : null;
  P = P || zNow().path;
  const N = nextOf(P), nx = N ? N[N.length - 1] : null, items = crumbItems(P);
  const draw = (fold, noNext) => {
    nav.textContent = '';
    const add = (tag, cls, txt, o) => { const e = H(tag, Object.assign({class: cls || ''}, o || {}), nav); e.textContent = txt; return e; };
    if (fold > 0) {
      const mb = add('button', 'more', '…', {type: 'button', 'aria-haspopup': 'menu', 'aria-expanded': 'false', 'aria-label': `${fold} levels further out`, 'data-ci': 'more'});
      mb._items = items.slice(0, fold); add('span', 'sep', '›', {'aria-hidden': 'true'});
    }
    items.forEach((it, j) => {
      if (j < fold) return;
      const bt = add('button', it.egg ? 'egg' : '', it.t, {type: 'button', 'data-ci': String(it.ci), 'data-ii': String(j), title: it.title, 'aria-label': it.egg ? 'Further out: ?' : null});
      if (it.cur) bt.setAttribute('aria-current', 'location');
      if (!it.cur) add('span', 'sep', '›', {'aria-hidden': 'true'});
    });
    if (nx && !noNext) {
      add('span', 'sep', '›', {'aria-hidden': 'true'});
      const e = egg(nx);
      add('button', 'nx', e || nx.id === WRAP ? '?' : shortOf(nx), {type: 'button', 'data-ci': 'next', title: e || nx.id === WRAP ? 'Zoom in (+)' : `Zoom into ${toOf(nx)} (+)`, 'aria-label': e || nx.id === WRAP ? 'Zoom in: ?' : `Zoom into ${toOf(nx)}`});
    }
  };
  // the outer crumbs fold into the "…" menu until the rest fits (the current one always shows; − and + sit outside the
  // crumbs, never clipped): drawn whole, measured, drawn folded by the measured widths, then folded one more while it
  // still overflows (review of 1 Oct: an estimate alone left the last crumbs clipped)
  draw(0);
  const over = () => nav.scrollWidth > nav.clientWidth + 1;
  if (over()) {
    const avail = nav.clientWidth, need = nav.scrollWidth, kids = [...nav.children], w = {};
    // a crumb folded frees its own width, its separator's and the gaps between them
    kids.forEach((e, j) => { const ii = e.dataset.ii; if (ii != null) { const sp = kids[j + 1]; w[ii] = e.getBoundingClientRect().width + (sp && sp.classList.contains('sep') ? sp.getBoundingClientRect().width + 4 : 2); } });
    let fold = 0, cut = 0; const more = 34;
    while (fold < items.length - 1 && need - cut + more > avail) { cut += w[String(fold)] || 0; fold++; }
    draw(fold);
    while (fold < items.length - 1 && over()) draw(++fold);
    // still too wide: the next crumb goes (the + button and the panel offer it)
    if (over() && nx) draw(fold, true);
  }
  plusUI(P);
  if (fi) { const e = nav.querySelector(`[data-ci="${fi}"]`); if (e) e.focus({preventScroll: true}); }
}
/* the − and + buttons: − off at the top of the ladder; + on while the selected part or the scale has something inside
   to zoom into */
function plusUI(P) {
  const pl = $('pmz').querySelector('[data-ci="plus"]'), mi = $('pmz').querySelector('[data-ci="minus"]');
  const k = SEL && SEL.isConnected ? kidOf(SEL) : null;
  setDis(pl, !nextOf(P) && !(k && !k.up));
  setDis(mi, !upOf(P));
}
/* A click with the mouse leaves no focus on the Up bar (Space would press the button again instead of pausing a
   flow); the button is blurred before the camera moves, since the bar is redrawn for the new target. A crumb takes no
   double-click: the crumbs are redrawn for the new target on the first click, so a second would land on another
   crumb (review of 1 Oct); a second tap within 400 ms is ignored the same way. */
const blurClick = (e, b) => { if (e.detail > 0 && b && b.contains(document.activeElement)) document.activeElement.blur(); };
let CRUMBT = -1e9, CRUMBPT = '';
$('crumbs').addEventListener('pointerdown', e => { CRUMBPT = e.pointerType; });
$('crumbs').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b || isDis(b)) return;
  if (e.detail > 1 || (e.detail > 0 && CRUMBPT === 'touch' && e.timeStamp - CRUMBT < 400)) return;
  CRUMBT = e.timeStamp;
  const ci = b.dataset.ci, P = zNow().path;
  if (ci === 'more') { menuToggle(b); return; }
  blurClick(e, b);
  if (ci === 'next') { const N = nextOf(P); if (N) userNav(N); return; }
  const i = +ci; if (i < P.length - 1) userNav(P.slice(0, i + 1));
});
$('pmz').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b || isDis(b)) return;
  blurClick(e, b);
  zoomBy(b.dataset.ci === 'minus' ? -1 : 1);
});
$('up').addEventListener('click', e => { const b = e.currentTarget; blurClick(e, b); if (!isDis(b)) zoomBy(-1); });
/* the crumbs fold again when the bar's width changes (a window resized, the panel shown or hidden) */
try { let upW = 0, upT = 0; new ResizeObserver(es => { const w = Math.round(es[0].contentRect.width); if (w === upW) return; upW = w; cancelAnimationFrame(upT); upT = requestAnimationFrame(() => crumbsUI()); }).observe($('upbar')); } catch (_) { /* no observer: the crumbs fold on the next move */ }
/* the "…" menu: the folded crumbs, outermost first */
function menuToggle(b) {
  const m = $('crumb-menu');
  if (!m.hidden) { menuOff(); return; }
  const P = zNow().path; m.textContent = '';
  (b._items || []).forEach(x => {
    const it = H('button', {type: 'button', role: 'menuitem', tabindex: '-1', 'data-ci': String(x.ci)}, m);
    // (the easter egg's levels stay unnamed here too: "?")
    const el = P[x.ci], sz = el && !x.egg ? sizeOf(el) : null;
    it.textContent = x.egg ? '?' : nameOf(el) + (sz && (sz.m > 0 || sz.bound) ? ' · ' + sizeTxt(sz) : '');
  });
  const wr = $('svgwrap').getBoundingClientRect(), br = b.getBoundingClientRect();
  m.style.left = Math.max(0, br.left - wr.left) + 'px'; m.style.top = '4px';
  m.hidden = false; b.setAttribute('aria-expanded', 'true');
  const f = m.querySelector('button'); if (f) f.focus({preventScroll: true});
}
function menuOff(refocus) {
  const m = $('crumb-menu'); if (m.hidden) return;
  m.hidden = true; const b = $('crumbs').querySelector('.more'); if (b) { b.setAttribute('aria-expanded', 'false'); if (refocus) b.focus({preventScroll: true}); }
}
$('crumb-menu').addEventListener('click', e => { const b = e.target.closest('button'); if (!b || e.detail > 1) return; const i = +b.dataset.ci; menuOff(e.detail === 0); userNav(zNow().path.slice(0, i + 1)); });
$('crumb-menu').addEventListener('keydown', e => {
  if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); menuOff(true); return; }
  // Tab leaves the menu: it closes, and focus goes on from its "…" button
  if (e.key === 'Tab') { menuOff(true); return; }
  const bs = [...$('crumb-menu').querySelectorAll('button')], i = bs.indexOf(document.activeElement);
  const j = e.key === 'ArrowDown' ? (i + 1) % bs.length : e.key === 'ArrowUp' ? (i - 1 + bs.length) % bs.length : e.key === 'Home' ? 0 : e.key === 'End' ? bs.length - 1 : -1;
  if (j >= 0) { e.preventDefault(); e.stopPropagation(); bs[j].focus(); }
});
document.addEventListener('pointerdown', e => { if (!$('crumb-menu').hidden && !e.target.closest('#crumb-menu, #crumbs .more')) menuOff(); }, true);
/* the readout: at rest, the scale's size; while the camera moves, the size it passes, log-linearly through each step
   (a jump sweeps the decades it skips mostly in its middle) */
let ROTXT = '', ROCLS = '';
/* (while the camera moves the readout changes every frame: plain text, and its class only when it changes) */
let ROT = 0;
function roSet(html, cls, plain) {
  const r = $('scale-ro');
  if (html !== ROTXT) { ROTXT = html; if (plain) r.textContent = html; else r.innerHTML = html; }
  const c = 'scale-ro' + (cls ? ' ' + cls : ''); if (c !== ROCLS) { ROCLS = c; r.className = c; }
}
function roRest() {
  const P = Z.path, el = P[P.length - 1], sz = sizeOf(el);
  roSet(sizeHtml(sz));
  $('scale-ro').removeAttribute('aria-hidden');
}
const smoother = x => x * x * x * (x * (x * 6 - 15) + 10);
function readout(s, e) {
  if (!s) { roRest(); return; }
  if (s.wrap) { if (ROCLS.indexOf('mv') < 0) $('scale-ro').setAttribute('aria-hidden', 'true'); roSet('↻ round the ring: a conceptual link', 'mv ring', true); return; }
  const so = s.pan ? null : s.so, si = s.pan ? null : s.si;
  if (!so || !si || !(so.m > 0) || !(si.m > 0)) return;
  // the moving readout changes about ten times a second, not every frame: each change is a layout of the bar, which
  // on a slow phone costs a frame its deadline, and nobody reads a number that changes faster
  const t = performance.now(); if (e < 1 && t - ROT < 100 && ROCLS.indexOf('mv') >= 0) return; ROT = t;
  const w = s.kind === 'jump' ? smoother(clamp(e, 0, 1)) : clamp(e, 0, 1), m = Math.exp(lerp(Math.log(so.m), Math.log(si.m), w));
  if (ROCLS.indexOf('mv') < 0) $('scale-ro').setAttribute('aria-hidden', 'true');
  roSet(`${fmtLen(m, 2)}${ro10(m)}`, 'mv' + (s.kind === 'jump' ? ' jump' : ''), true);
}
/* after a move: announce the scale, and (unless a flow or the tour holds the panel) show where the camera is */
function arrived() {
  const P = Z.path, el = P[P.length - 1];
  $('stage').classList.toggle('offchip', Z.level < 0 || Z.level > 2);
  $('cap-scale').textContent = `Scale: ${nameOf(el)}, ${sizeWords(sizeOf(el))}`;
  // off the page's own scales, the deep zoom's facts are fetched now if they have not been
  if (Z.level < 0 || Z.level > 2) lazyData();
  prefetch();
  if (!FL.k && !TOUR && !SEL) showHere();
}
/* ---- the arrow keys with no flow or tour on the stage (and not presenting): in a shire, to the neighbour that way
   (as its edge link does); in any scale with siblings side by side (a minion), a glide to the one that way; elsewhere
   the keyboard's focus moves to the nearest part that way ---- */
const DIRV = {N: [0, -1], S: [0, 1], W: [-1, 0], E: [1, 0]};
const DIRRC = {N: [-1, 0], S: [1, 0], W: [0, -1], E: [0, 1]};
function arrowNav(dir) {
  const P = zNow().path, el = P[P.length - 1];
  if (el.id === 'shire') {
    const sid = +el.k, c = shCell(sid); if (!c) return false;
    const n0 = BYDIE[(c.r + DIRRC[dir][0]) + ',' + (c.c + DIRRC[dir][1])];
    if (n0) { goNeighbour({cell: n0, dir}, sid); return true; }
    return false;
  }
  const sib = sibInDir(P, dir);
  if (sib) { userNav(sib, {pan: true}); return true; }
  return focusDir(dir);
}
/* the sibling of P's last scale whose seat in the parent's drawing lies that way (within 45 degrees), nearest first */
function sibInDir(P, dir) {
  if (P.length < 2) return null;
  const d = P.length - 1, Lp = layerAt(P, d - 1);
  if (!Lp._built) return null;
  const zs = Lp._ap.zs, me = zs[pk(P[d])]; if (!me) return null;
  const c0 = {x: me.r.x + me.r.w / 2, y: me.r.y + me.r.h / 2}, [vx, vy] = DIRV[dir];
  let best = null, bs = Infinity;
  Object.entries(zs).forEach(([key, s]) => {
    const el = elOf(key); if (el.id !== P[d].id || key === pk(P[d])) return;
    const dx = s.r.x + s.r.w / 2 - c0.x, dy = s.r.y + s.r.h / 2 - c0.y, along = dx * vx + dy * vy, perp = Math.abs(dx * vy - dy * vx);
    if (along <= 1e-6 || perp > along) return;
    const sc = along + 2 * perp; if (sc < bs) { bs = sc; best = el; }
  });
  return best ? P.slice(0, d).concat([best]) : null;
}
/* the keyboard's focus to the nearest part that way, from the focused part (else from the middle of the drawing) */
function focusDir(dir) {
  const L = restLayer(); if (!L) return false;
  const parts = [...L.querySelectorAll('.comp, .nbr')].filter(g => g.getClientRects().length);
  if (!parts.length) return false;
  const a = document.activeElement, from = a && L.contains(a) && parts.includes(a) ? a : null;
  const ctr = r => ({x: r.left + r.width / 2, y: r.top + r.height / 2});
  const sv = svg.getBoundingClientRect(), c0 = from ? ctr(from.getBoundingClientRect()) : {x: sv.left + sv.width / 2, y: sv.top + sv.height / 2};
  const [vx, vy] = DIRV[dir];
  let best = null, bs = Infinity;
  parts.forEach(g => {
    if (g === from) return;
    const c = ctr(g.getBoundingClientRect()), dx = c.x - c0.x, dy = c.y - c0.y, along = dx * vx + dy * vy, perp = Math.abs(dx * vy - dy * vx);
    if (from && (along <= 1 || perp > 2 * along)) return;
    const sc = Math.max(0, along) + 2 * perp; if (sc < bs) { bs = sc; best = g; }
  });
  if (!best) return false;
  best.focus({preventScroll: true});
  return true;
}
/* ?at=<path> (read once at load; the viewer drops #hash): elements by '/', each id or id:params. An id of a scale
   above the die alone expands to the ladder down to it (?at=sf); a path under the die starts from the die
   (?at=shire:20/minion:20.1.3). Tests start anywhere with it. */
function atPath(s) {
  const els = pathFrom(s); if (!els.length || !els.every(e => NODES[e.id])) return null;
  if (els[0].id === WRAP) return els.length === 1 ? [{id: WRAP}] : null;
  const oi = OUT_IDS.indexOf(els[0].id);
  let P;
  if (oi >= 0) P = OUT_IDS.slice(0, oi).map(id => ({id})).concat(els);
  else if (els[0].id === 'die') P = OUT_IDS.map(id => ({id})).concat(els);
  else P = pathOf({level: 0}).concat(els);
  // every scale on the way must have its seat in the one above it
  try { for (let d = 1; d < P.length; d++) if (!seatOf(P, d)) return null; } catch (_) { return null; }
  return P;
}
/* ---- the two-state electronics (DESIGN §4.2; the owner: "the goal is to learn more about electronics"): a scene drawn
   in two states, its .st-a and .st-b groups (the gate at 0 V or at the rail, a bit holding 0 or 1, a DRAM cell charged
   or after its refresh window), switched for the whole page by the svg's class st-on: a 250 ms CSS fade, no script per
   frame. The switch is a button in the drawing (.stsw, role switch), the panel's button, and the G key; the state
   holds from one scene to the next (zooming from the fin into the channel keeps the gate on). ---- */
let STON = false;
function stateSet(on) {
  STON = !!on;
  svg.classList.toggle('st-on', STON);
  svg.querySelectorAll('.stsw').forEach(b => { b.setAttribute('aria-checked', String(STON)); const t = b.querySelector('.stsw-t'); if (t && b._lab) t.textContent = b._lab[STON ? 1 : 0]; });
  $('pn-body').querySelectorAll('button[data-act="state"]').forEach(b => { b.setAttribute('aria-pressed', String(STON)); if (b._lab) b.textContent = b._lab[STON ? 1 : 0]; });
  const L = restLayer(), st = L && L._states;
  if (st) $('pn-live').textContent = st.say ? st.say[STON ? 1 : 0] : '';
}
const stateToggle = () => stateSet(!STON);
/* a scene's switch in its drawing at (x, y): a pill with the state it is in and what pressing it does */
function stateSwitch(L, x, y, st, o) {
  o = o || {};
  const g = E('g', {class: 'stsw', role: 'switch', tabindex: '0', 'aria-checked': String(STON), 'aria-label': st.lab, transform: `translate(${x},${y})`}, L);
  const w = o.w || 300, h = o.h || 46;
  E('rect', {class: 'stsw-hit', x: -6, y: -6, width: w + 12, height: h + 12, rx: (h + 12) / 2}, g);
  E('rect', {class: 'stsw-bg', x: 0, y: 0, width: w, height: h, rx: h / 2}, g);
  E('circle', {class: 'stsw-k', cx: h / 2, cy: h / 2, r: h / 2 - 6}, g);
  const t = T(g, h + 10, h / 2 + 7, st.btn[STON ? 1 : 0], 'stsw-t');
  g._lab = st.btn;
  L._states = st;
  return g;
}
svg.addEventListener('click', e => { const b = e.target.closest && e.target.closest('.stsw'); if (b && svg.contains(b)) { e.stopPropagation(); stateToggle(); } }, true);
svg.addEventListener('keydown', e => { const b = e.target.closest && e.target.closest('.stsw'); if (b && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); e.stopPropagation(); stateToggle(); } }, true);
/* ---- the lazy data (DESIGN §2.4, §5.1): the deep zoom's facts (the circuits', the levels', the device's, the particles')
   live in a file beside the page, D.lazy.url (ladder-img/ladder-data.json), fetched once, at idle after the first paint,
   or at once if the camera leaves the page's own scales first. Until they arrive a source tooltip and a fact list say
   "loading the sources…"; a failed fetch (the page opened without its folder) leaves every drawing and says "sources not
   loaded". The page's hook pageLazy(ok) redraws what showed them. ---- */
const LAZY = {st: D.lazy ? 'idle' : 'done', cbs: []};
let LAZYLI = 0;
/* a fact list's one line for its facts still on their way (factLi gives it once per list: the panel is drawn in one go) */
/* a panel's line for facts not there yet: "loading the sources…", or "sources not loaded" */
const lazyNote = ids => ((ids || []).some(f => !F[f]) && LAZY.st !== 'done' ? `<p class="pn-what lz">${LAZY.st === 'failed' ? 'Sources not loaded: the page\'s data folder is missing.' : 'Loading the sources…'}</p>` : '');
const lazyLi = t => { const now = performance.now(); if (now - LAZYLI < 50) return ''; LAZYLI = now; return `<li class="fact lz"><span>${esc(t)}</span></li>`; };
function lazyData(cb) {
  if (LAZY.st === 'done' || LAZY.st === 'failed') { if (cb) cb(); return; }
  if (cb) LAZY.cbs.push(cb);
  if (LAZY.st === 'loading') return;
  LAZY.st = 'loading';
  const fin = ok => {
    LAZY.st = ok ? 'done' : 'failed';
    const c = LAZY.cbs; LAZY.cbs = [];
    c.forEach(f => { try { f(); } catch (e) { console.error(e); } });
    if (typeof pageLazy === 'function') { try { pageLazy(ok); } catch (e) { console.error(e); } }
  };
  try {
    fetch(D.lazy.url).then(r => (r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))).then(d => { Object.assign(F, d.facts || {}); fin(true); }, () => fin(false));
  } catch (_) { fin(false); }
}
/* at idle after the first paint, and only while the camera rests and nothing plays (pageBusy: a flow or the tour), so
   that parsing the file never takes a moving frame's time; the scales that need the facts fetch them on arrival */
function lazyIdle() {
  if (LAZY.st !== 'idle') return;
  if (ZW || (typeof pageBusy === 'function' && pageBusy())) { setTimeout(lazyIdle, 1500); return; }
  lazyData();
}
try { (window.requestIdleCallback || (f => setTimeout(f, 1200)))(lazyIdle, {timeout: 2500}); } catch (_) { setTimeout(lazyIdle, 1200); }
