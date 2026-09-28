/* Anatomy of a memory access, interactively. D is facts.json (docs/reports/data/2026-09-28-memory-levels/build_facts.py):
   D.facts  every fact of the five levels, keyed "<level>:<id>": statement, value, unit, source, kind (spec, measured,
            derived, generic, unknown), badge (documented, generic, unknown), the lab cards it covers, the report page
            that quotes it, and a caveat (reimpl: Ainekko's re-implementation RTL; spec-v1.1: the Shire Cache Specification)
   D.steps  each level's accesses, their steps in one schema (block, action, latency, energy, the circuit elements that
            switch, each with its kind)
   D.num    every number the page prints outside a fact's statement, tied to the fact whose statement contains it (the
            build asserts that); n(key) prints one with its source on hover. A value the page computes cites its facts
   D.parts  the facts each details panel lists; D.asks what would settle each unknown, and D.rungs the hub's rows
   Geometry lives here; words, numbers and sources in D. Colours are the template's tokens only.

   The engine is the chip tour's (docs/reports/sources/chip-diagram.script.js; copied from its version of 27 September
   2026, 21:27, 2,715 lines): the pausable clock, the animation primitives, the camera (one ease over a chain of zooms,
   redirectable, with the labels fading by scale), the details panel with sourced numbers, the stage bar, the tour and
   presenting. It is generalised from the tour's three fixed layers (chip, shire, minion) to a tree of scales per level:
   each level is a scene with a root scale, its children and theirs, down to transistors. Every scale is drawn in the
   same frame (FR); zooming into a part grows that part's box (with the frame's aspect, centred on it) into the frame.
   Each access is a list of steps; a step plays at one scale and, with Dive on, goes down to the circuit it switches and
   back. Keys: 1-5 levels, [ ] accesses, Left/Right steps, Shift+Left/Right tour slides, Space pauses, + and - zoom,
   Enter zooms into a part, Backspace out, C follow, V dive, T tour (Shift+T every level), Q or Esc ends the tour,
   F presents, P panel, D light and dark. URL: #<level>[/<access>[/<step>[/<scale>]]], ?theme=, ?panel=off, ?dive=on,
   ?tour=1|all. */
(function () {
'use strict';
let SRC_HTML = '';
try { SRC_HTML = '<!doctype html>\n' + document.documentElement.outerHTML; } catch (_) { /* no DOM access */ }
const F = D.facts, N = D.num, PARTSF = D.parts, DSTEPS = D.steps, ASKS = D.asks || [], RUNGS = D.rungs || {};
const HUB = 'https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability';
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
let REDUCED = !!CK.reduced;
try { const mq = matchMedia('(prefers-reduced-motion: reduce)'); mq.addEventListener('change', e => { REDUCED = e.matches; }); } catch (_) { /* old browser */ }
const fnum = (v, dp) => CK.fmt.num(v, dp);
/* a touch screen (no keyboard, no hover: no keyboard hints) and a narrow portrait window (a phone: the details panel
   always shows under the stage), as the chip tour decides them */
const mqOn = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
const TOUCHSCR = mqOn('(hover: none) and (pointer: coarse)'), PHQ = '(max-width: 899px) and (max-aspect-ratio: 1/1)';
const V = k => { if (!N[k]) throw new Error('no number ' + k); return N[k].v; };
const disp = t => String(t).replace(/(\d)x(?=$|[\s,;.)])/g, '$1×').replace(/(\d) x (\d)/g, '$1 × $2');
/* a number from D.num, with its fact attached; a unit after it never wraps onto the next line */
function n(k, unit) {
  const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; }
  return `<span class="num" data-f="${x.f}">${esc(disp(x.t))}${unit ? ' ' + esc(unit) : ''}</span>`;
}
/* the text of a number, for the drawing (the SVG text carries the fact as data-f) */
const nt = k => { const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; } return disp(x.t); };
const nf = k => (N[k] ? N[k].f : '');
/* a number the page computes, citing the facts it comes from */
const cn = (v, fids, dp, unit) => `<span class="num" data-f="${fids}">${typeof v === 'number' ? fnum(v, dp) : esc(v)}${unit ? ' ' + unit : ''}</span>`;
/* words (not a number) whose source is a fact */
const src = (text, fids) => `<span class="num" data-f="${fids}">${text}</span>`;
const S = (node, o) => { for (const k in o) if (o[k] != null) node.style[k] = o[k]; return node; };
const E = (tag, attrs, parent) => CK.el(tag, attrs, parent);
function T(parent, x, y, str, cls, anchor, fids) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  t.textContent = str; if (fids) t.setAttribute('data-f', fids);
  return t;
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

/* ================= the SVG, its frame and its layers ================= */
const VB = {x: -190, y: -84, w: 1300, h: 792};
const FR = {x: -172, y: -74, w: 1264, h: 774};   // every scale is drawn in this frame
const svg = $('mem');
svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
{
  const defs = E('defs', {}, svg);
  const f = E('filter', {id: 'co-sh', x: '-10%', y: '-20%', width: '120%', height: '160%'}, defs);
  E('feDropShadow', {dx: 0, dy: 2, stdDeviation: 3, 'flood-color': '#000'}, f);
  // the rail bands: a pattern and a text label, never a colour alone (DESIGN.md §3)
  const pat = (id, w, h, draw, rot) => { const p = E('pattern', {id, width: w, height: h, patternUnits: 'userSpaceOnUse', patternTransform: rot ? `rotate(${rot})` : null}, defs); draw(p); };
  pat('pat-lv', 16, 16, p => S(E('line', {x1: 0, y1: 0, x2: 0, y2: 16}, p), {stroke: 'var(--ink-2)', strokeWidth: 2, strokeOpacity: 0.22}), 45);
  pat('pat-hv', 16, 16, p => S(E('circle', {cx: 8, cy: 8, r: 2}, p), {fill: 'var(--ink-2)', fillOpacity: 0.3}));
  pat('pat-mesh', 16, 12, p => S(E('line', {x1: 0, y1: 6, x2: 16, y2: 6}, p), {stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeOpacity: 0.25}));
  pat('pat-ddr', 12, 16, p => S(E('line', {x1: 6, y1: 0, x2: 6, y2: 16}, p), {stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeOpacity: 0.25}));
  pat('pat-hatch', 10, 10, p => S(E('line', {x1: 0, y1: 0, x2: 0, y2: 10}, p), {stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeOpacity: 0.3}), 135);
  E('marker', {id: 'arr', viewBox: '0 0 10 10', refX: 8, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse'}, defs)
    .appendChild(S(E('path', {d: 'M0,0 L10,5 L0,10 z'}), {fill: 'var(--ink-2)'}));
  E('marker', {id: 'arr2', viewBox: '0 0 10 10', refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: 'auto-start-reverse'}, defs)
    .appendChild(S(E('path', {d: 'M0,0 L10,5 L0,10 z'}), {fill: 'var(--c2)'}));
}
const MAXD = 7;
const LAYERS = [], FX = [], AP = [];
for (let i = 0; i < MAXD; i++) {
  const g = E('g', {class: 'lay', 'data-depth': i}, svg);
  g.style.display = 'none'; g.style.opacity = 0;   // hidden views start transparent: a zoom fades them in
  LAYERS.push(g); FX.push(null); AP.push({zg: {}, parts: {}});
}

/* ================= the animation clock: everything that moves runs on it, and Space stops it ================= */
const CLK = {t: 0, on: true, last: 0, dt: 0, jobs: new Set()};
(function loop(now) {
  const dt = CLK.last ? Math.min(80, now - CLK.last) : 0; CLK.last = now; CLK.dt = dt;
  if (CLK.on) CLK.t += dt;
  CLK.jobs.forEach(j => { try { j(); } catch (e) { CLK.jobs.delete(j); console.error(e); } });
  requestAnimationFrame(loop);
})(0);
const CANCEL = new Error('cancelled');
const alive = tok => { if (tok.dead) throw CANCEL; };
/* a token's wait and animation: on the clock; under tok.ff (drawing a step's end state) at once */
function wait(tok, ms) {
  return new Promise((res, rej) => {
    if (tok.dead) return rej(CANCEL);
    if (tok.ff || ms <= 0) return res();
    const t0 = CLK.t, d = ms / (tok.speed || 1), j = () => { if (tok.dead) { CLK.jobs.delete(j); rej(CANCEL); } else if (CLK.t - t0 >= d) { CLK.jobs.delete(j); res(); } };
    CLK.jobs.add(j);
  });
}
/* with reduced motion, an animation draws its end state at once and then waits out a short time */
function anim(tok, ms, fn) {
  if (tok.dead) return Promise.reject(CANCEL);
  if (tok.ff) { fn(1); return Promise.resolve(); }
  if (REDUCED) { fn(1); return wait(tok, Math.min(ms, 700)); }
  return new Promise((res, rej) => {
    if (ms <= 0) { fn(1); return res(); }
    const t0 = CLK.t, d = ms / (tok.speed || 1), j = () => {   // tok.speed: a dive plays its circuit faster
      if (tok.dead) { CLK.jobs.delete(j); rej(CANCEL); return; }
      const p = Math.min(1, (CLK.t - t0) / d); fn(p);
      if (p >= 1) { CLK.jobs.delete(j); res(); }
    };
    CLK.jobs.add(j); j();
  });
}
function every(tok, fn) { const j = () => { if (tok.dead) CLK.jobs.delete(j); else fn(CLK.t); }; CLK.jobs.add(j); }
const quiet = p => p.catch(e => { if (e !== CANCEL) console.error(e); });
let FFTOK = null;
const noFade = () => !!(FFTOK && FFTOK.ff && !FFTOK.dead);
const easeOut = p => 1 - (1 - p) * (1 - p);
function fadeIn(el, ms, rise) {
  if (!el || REDUCED || !CLK.on || noFade()) return el;
  el.style.opacity = 0; const t0 = CLK.t, d = ms || 320;
  const j = () => {
    const p = Math.min(1, (CLK.t - t0) / d), e = easeOut(p);
    el.style.opacity = e; if (rise) el.setAttribute('transform', `translate(0,${(rise * (1 - e)).toFixed(2)})`);
    if (p >= 1 || !el.isConnected) { CLK.jobs.delete(j); el.style.opacity = ''; if (rise) el.removeAttribute('transform'); }
  };
  CLK.jobs.add(j);
  return el;
}
function fadeOut(el, ms) {
  if (!el) return;
  if (REDUCED || !CLK.on || noFade() || !el.isConnected) { el.remove(); return; }
  const t0 = CLK.t, d = ms || 180, o0 = +(el.style.opacity || 1);
  el.style.pointerEvents = 'none';
  const j = () => { const p = Math.min(1, (CLK.t - t0) / d); el.style.opacity = (o0 * (1 - p)).toFixed(3); if (p >= 1 || !el.isConnected) { CLK.jobs.delete(j); el.remove(); } };
  CLK.jobs.add(j);
}
function popIn(el) {
  if (REDUCED || !CLK.on || noFade()) return;
  const t0 = CLK.t, d = 180;
  el.setAttribute('transform', 'scale(0.4)'); el.style.opacity = 0;
  const j = () => {
    const p = Math.min(1, (CLK.t - t0) / d), e = easeOut(p);
    el.setAttribute('transform', `scale(${(0.4 + 0.6 * e).toFixed(3)})`); el.style.opacity = e.toFixed(3);
    if (p >= 1 || !el.isConnected) { CLK.jobs.delete(j); el.removeAttribute('transform'); el.style.opacity = ''; }
  };
  CLK.jobs.add(j);
}

/* ================= the camera: a tree of scales per level ================= */
/* Z.path is the scale shown: the ids of the scale nodes from the level's root down. LAYERS[d] holds the drawing of
   Z.path[d]; only the deepest is shown, except while the camera moves between a scale and one inside it. */
const Z = {lv: 'l1', path: []};
const SCENES = {};
const SC = () => SCENES[Z.lv];
const NODE = id => SC().scales[id];
function pathTo(id) { const out = []; let n0 = id; while (n0) { out.unshift(n0); n0 = NODE(n0).parent; } return out; }
const samePath = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const lerp = (a, b, t) => a + (b - a) * t;
const lerpR = (A, B, t) => ({x: lerp(A.x, B.x, t), y: lerp(A.y, B.y, t), w: lerp(A.w, B.w, t), h: lerp(A.h, B.h, t)});
const easeS = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const easeOutS = t => Math.sin(Math.PI / 2 * t);
const band = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rmap = (A, B) => { const k = B.w / A.w; return [k, B.x - k * A.x, B.y - k * A.y]; };
const setT = (g, m) => { if (m) g.setAttribute('transform', `matrix(${m[0]},0,0,${m[0]},${m[1]},${m[2]})`); else g.removeAttribute('transform'); };
const zoomR = (A, B, e) => { const w = A.w * Math.pow(B.w / A.w, e); return lerpR(A, B, (w - A.w) / (B.w - A.w)); };
/* a rect with the frame's aspect, centred on r and covering it: what a zoom grows into the frame */
function fitAspect(r) {
  const k = FR.w / FR.h; let w = r.w, h = r.h;
  if (w / h > k) h = w / k; else w = h * k;
  return {x: r.x + r.w / 2 - w / 2, y: r.y + r.h / 2 - h / 2, w, h};
}
/* A tween on real time (the reader's own zoom) or on the animation clock (an access's or the tour's camera, which
   Space stops). stop() true: a newer request came in; the tween stops where it is and resolves false. */
function tween(ms, fn, clk, stop) {
  return new Promise(res => {
    let done = false;
    const fin = ok => { if (done) return; done = true; if (ok) fn(1); res(ok); };
    if (REDUCED || ms <= 0) return fin(true);
    if (clk) {
      let acc = 0;
      const j = () => {
        if (stop()) { CLK.jobs.delete(j); fin(false); return; }
        if (CLK.on || clk.dead) acc += CLK.dt;
        const p = Math.min(1, acc / ms); if (p >= 1) { CLK.jobs.delete(j); fin(true); } else fn(p);
      };
      CLK.jobs.add(j); return;
    }
    const t0 = performance.now();
    const f = now => { if (done) return; if (stop()) { fin(false); return; } const p = Math.min(1, (now - t0) / ms); if (p >= 1) fin(true); else { fn(p); requestAnimationFrame(f); } };
    requestAnimationFrame(f);
    setTimeout(() => { if (!done) fin(!stop()); }, ms + 800);   // a hidden tab gets no frames
  });
}
/* build scale `id` into LAYERS[d]; its builder fills AP[d] (anchor points, the parts by key, and zg: the part a zoom
   into each child grows from) */
function buildLayer(d, id) {
  const L = LAYERS[d]; L.textContent = ''; AP[d] = {zg: {}, parts: {}, id};
  BAP = AP[d]; try { NODE(id).build(L, AP[d], SC().inst); } finally { BAP = null; }
  // an access's marks that run under the drawing (the trails, the rings of lit parts): every label stays on top of them
  const fr = L.querySelector(':scope > g.frm');
  L._under = E('g', {class: 'fxu', 'pointer-events': 'none'});
  L.insertBefore(L._under, fr ? fr.nextSibling : L.firstChild);
  FX[d] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
  L._node = id;
  measured(L, () => { ringAll(L); fitTexts(L); kbTexts(L); });
}
/* getBBox needs the layer rendered: a hidden layer is shown, invisible, while it is measured */
function measured(L, fn) {
  const d0 = L.style.display, v0 = L.style.visibility;
  if (d0 === 'none') { L.style.visibility = 'hidden'; L.style.display = ''; }
  try { fn(); } finally { if (d0 === 'none') { L.style.display = d0; L.style.visibility = v0; } }
}
/* every part a keyboard can reach shows a ring when focused: the parts drawn without a box get one from their
   extent (WCAG 2.4.7) */
function ringAll(L) {
  L.querySelectorAll('g.comp').forEach(g => {
    if (g.querySelector(':scope > rect.ring')) return;
    let b = g._box;
    if (!b) { try { const r = g.getBBox(); if (r.width || r.height) b = {x: r.x, y: r.y, w: r.width, h: r.height}; } catch (_) { /* not rendered */ } }
    if (!b) return;
    E('rect', {class: 'ring', x: b.x - 6, y: b.y - 6, width: b.w + 12, height: b.h + 12, rx: 8}, g);
  });
}
/* a part's own labels stay inside its box at the text sizes in force (the short-screen sizes are larger): a label that
   would spill is set smaller, never below the 1920 size of its class or 15 units */
function fitTexts(L) {
  L.querySelectorAll('text[data-fit]').forEach(t => { t.style.fontSize = ''; t.removeAttribute('data-fit'); });
  L.querySelectorAll('g.comp').forEach(g => {
    const r = g.querySelector(':scope > rect.shape'); if (!r) return;
    const x = +r.getAttribute('x'), y = +r.getAttribute('y'), W = +r.getAttribute('width'), H = +r.getAttribute('height');
    if (!(W > 0 && H > 0)) return;
    g.querySelectorAll(':scope > text').forEach(t => {
      if (!t.textContent.trim() || t.classList.contains('t-q')) return;
      let b; try { b = t.getBBox(); } catch (_) { return; }
      if (!b.width) return;
      const an = t.getAttribute('text-anchor') || 'start', pad = 5;
      const avail = an === 'middle' ? W - 2 * pad : an === 'end' ? b.x + b.width - (x + pad) : x + W - pad - b.x;
      const low = y + H - 2 - (b.y + b.height);
      if (b.width <= avail && low >= 0) return;
      const fs = parseFloat(getComputedStyle(t).fontSize), floor = Math.min(fs, Math.max(15, FS_BASE[[...t.classList].find(c => FS_BASE[c])] || 17));
      let k = Math.min(1, avail / b.width);
      if (low < 0) k = Math.min(k, 1 + low / Math.max(1, b.height));
      const nfs = Math.max(floor, Math.floor(fs * k * 10) / 10);
      if (nfs < fs) { t.style.fontSize = nfs + 'px'; t.setAttribute('data-fit', '1'); }
    });
  });
}
/* Every label knocks out what runs under it (a trail, a lit ring, a wire, a rail band's hatching) in the colour of what
   it sits on, so it reads cleanly; where nothing runs under it the knockout is invisible (CSS: #mem .lay text). A part
   sets that colour for its labels (boxShape, --kb); a label on an opaque shape (a gate, a card) takes the shape's */
const KB_CLS = {gate: 'var(--surface)', ch: 'var(--surface)', bub: 'var(--surface)', 'co-box': 'var(--surface)'};
function kbTexts(L) {
  const sh = [];
  L.querySelectorAll('rect, path, circle, ellipse, polygon').forEach(e => {
    if (e.closest('.fx, .fxu, defs')) return;
    const c = e.style.fill && !/url/.test(e.style.fill) && (e.style.fillOpacity === '' || +e.style.fillOpacity >= 0.9) ? e.style.fill : KB_CLS[[...e.classList].find(k => KB_CLS[k])];
    if (!c || e.classList.contains('zbd')) return;
    let b; try { b = e.getBBox(); } catch (_) { return; }
    if (b.width && b.height) sh.push({e, c, x: b.x, y: b.y, w: b.width, h: b.height});
  });
  if (!sh.length) return;
  L.querySelectorAll('text').forEach(t => {
    if (t.closest('.fx')) return;
    let b; try { b = t.getBBox(); } catch (_) { return; }
    if (!b.width) return;
    const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    let top = null;
    for (const s0 of sh) if (cx >= s0.x && cx <= s0.x + s0.w && cy >= s0.y && cy <= s0.y + s0.h && (s0.e.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING)) top = s0;
    if (top) t.style.setProperty('--kb', top.c);
  });
}
const FS_BASE = {'t-sm': 17, 't-smb': 17, 't-mono': 17, 't-lab': 20, 't-labb': 20, 't-net': 19, 't-mid': 24, 't-big': 30};
let refitT = 0;
window.addEventListener('resize', () => { clearTimeout(refitT); refitT = setTimeout(() => LAYERS.forEach(L => { if (L.childNodes.length) measured(L, () => fitTexts(L)); }), 160); });
function tgtRect(d, child) { return fitAspect(NODE(child).target(AP[d], SC().inst)); }
const logL = child => { const nd = NODE(child); return Math.log(FR.w / (nd.tw || 260)); };
/* while the camera moves between a view and the one inside it, the outer view's strokes keep their width on screen */
function strokeKeeper(layer) {
  const list = [];
  layer.querySelectorAll('line, rect, path, circle, polygon, polyline').forEach(el => {
    const cs = getComputedStyle(el); if (!cs.stroke || cs.stroke === 'none') return;
    const w = parseFloat(cs.strokeWidth); if (w > 0) list.push([el, w, el.style.strokeWidth]);
  });
  let last = 1;
  return {
    set: k => { k = Math.max(1, k); if (Math.abs(k - last) < 0.004) return; last = k; list.forEach(([el, w]) => { el.style.strokeWidth = (w / k).toFixed(3) + 'px'; }); },
    done: () => list.forEach(([el, , s0]) => { el.style.strokeWidth = s0; }),
  };
}
function ctxMark(layer, tgt) {
  if (tgt) tgt.classList.add('ztgt');
  let el = tgt;
  if (!el) [...layer.children].forEach(s => { if (!s.classList.contains('fx') && !s.classList.contains('fxu')) s.classList.add('zdim'); });
  while (el && el !== layer && el.parentNode) {
    const p = el.parentNode;
    [...p.children].forEach(s => { if (s !== el && !s.classList.contains('fx') && !s.classList.contains('fxu') && !s.classList.contains('zbd')) s.classList.add('zdim'); });
    el = p;
  }
}
function ctxClear(layer) { layer.querySelectorAll('.zdim, .ztgt').forEach(e => e.classList.remove('zdim', 'ztgt')); }
function dimLevel(layer) {
  if (!svg.classList.contains('dimming') && !svg.classList.contains('fdim')) return 1;
  const d = layer && layer.querySelector('.dimmable:not(.hi)');
  const o = d ? parseFloat(getComputedStyle(d).opacity) : 1;
  return o > 0 && o <= 1 ? o : 1;
}
const CTX_LOW = 0.3;
/* the step in flight between LAYERS[d] (outer) and LAYERS[d + 1] (inner, scale `child`): e = 0 shows the outer view */
let CUR = null, ZGEN = 0;
async function zoomSeg(d, child, A, e0, e1, ms, efn, req, c0) {
  const outer = LAYERS[d], inner = LAYERS[d + 1], B = FR, gen = ZGEN;
  const tgt = AP[d].zg && AP[d].zg[child];
  if (!CUR || CUR.d !== d || CUR.child !== child) CUR = {d, child, A, e: e0, c0: c0 == null ? 1 : c0};
  CUR.dir = e1 > e0 ? 1 : -1;
  const cc = CUR.c0;
  const frame = e => {
    const R = zoomR(A, B, e), Mo = rmap(A, R), Mi = rmap(B, R);
    setT(outer, Mo); setT(inner, Mi);
    outer.style.opacity = 1 - band(e, 0.86, 1);
    inner.style.opacity = band(e, 0.1, 0.32);
    outer.style.setProperty('--lab', (1 - band(e, 0.02, 0.2)).toFixed(3));
    inner.style.setProperty('--lab', band(e, 0.62, 0.88).toFixed(3));
    outer.style.setProperty('--ctx', lerp(cc, CTX_LOW, easeS(band(e, 0, 0.3))).toFixed(3));
    return [Mo, Mi];
  };
  if (ms > 0 && !REDUCED) frame(e0);
  outer.style.display = ''; inner.style.display = '';
  LAYERS.forEach(l => l.classList.add('busy'));
  outer.classList.add('zout'); ctxMark(outer, tgt);
  const keep = strokeKeeper(outer);
  keep.set(rmap(A, zoomR(A, B, e0))[0]);
  let ok = false;
  try {
    ok = await tween(ms, p => {
      const e = CUR.e = e0 + (e1 - e0) * efn(p), [Mo] = frame(e);
      keep.set(Mo[0]);
    }, req.o.clk || null, () => ZT !== req || gen !== ZGEN);
  } finally { keep.done(); }
  if (!ok || gen !== ZGEN) return false;
  CUR = null;
  LAYERS.forEach(l => l.classList.remove('busy'));
  outer.classList.remove('zout'); ctxClear(outer);
  [outer, inner].forEach(l => { l.style.removeProperty('--lab'); l.style.removeProperty('--ctx'); });
  if (e1 >= 1) { outer.style.display = 'none'; setT(inner, null); inner.style.opacity = 1; Z.path = Z.path.slice(0, d + 1).concat([child]); }
  else { inner.style.display = 'none'; setT(outer, null); outer.style.opacity = 1; Z.path = Z.path.slice(0, d + 1); }
  scaleUI();
  return true;
}
/* the zooms from path s to path t: out to their common scale, then in; each step's length on the log scale */
function planFrom(s, t) {
  let k = 0; while (k < s.length && k < t.length && s[k] === t[k]) k++;
  const out = [];
  for (let i = s.length - 1; i >= Math.max(k, 1); i--) out.push({dir: -1, d: i - 1, child: s[i], L: logL(s[i])});
  for (let i = Math.max(k, 1); i < t.length; i++) out.push({dir: 1, d: i - 1, child: t[i], L: logL(t[i])});
  return out;
}
const costOf = plan => plan.reduce((s, x) => s + x.L, 0);
/* one ease over a whole chain of zooms: each step gets its slice of the curve */
function chainSegs(plan, per, ez) {
  const tot = costOf(plan) || 1, Tt = per * tot;
  const inv = f => { let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (ez(m) < f) lo = m; else hi = m; } return (lo + hi) / 2; };
  let acc = 0;
  return plan.map(st => {
    const f0 = acc / tot, f1 = (acc + st.L) / tot; acc += st.L;
    const t0 = inv(f0), t1 = inv(f1);
    return {ms: Tt * (t1 - t0), efn: p => Math.max(0, Math.min(1, (ez(t0 + p * (t1 - t0)) - f0) / (f1 - f0)))};
  });
}
/* The camera follows the latest request only; a request that comes in during a move redirects it from where it is.
   o.clk: a token whose clock drives the move; o.ms: ms per unit of log scale (0: a cut); o.total: the whole move's
   length; o.keepFx: an access's drawing stays. */
let ZT = null, ZW = false, ZWAIT = [], ZN = 0;
const zNow = () => (ZT ? ZT.t : Z.path);
function goTo(t, o) {
  o = o || {};
  const same = ZW && ZT && samePath(ZT.t, t);
  if (same && !o.total && o.ms !== 0) { if (o.focus) ZT.o.focus = true; return new Promise(res => ZWAIT.push(res)); }
  ZT = {t: t.slice(), o, n: ++ZN};
  return new Promise(res => { ZWAIT.push(res); if (!ZW) { ZW = true; zoomWorker(); } });
}
async function zoomWorker() {
  const from = Z.path.slice(), hadFocus = svg.contains(document.activeElement), gen = ZGEN;
  let wantFocus = false;
  PIP.el.hidden = true;   // the mini-map shows the scale above the one shown: hidden while the camera moves (its place in the panel is kept)
  try {
    for (let guard = 0; ZT && guard < 32 && gen === ZGEN; guard++) {
      const req = ZT, t = req.t;
      if (req.o.focus) wantFocus = true;
      let segs, redirect = false;
      if (CUR) {
        const base = Z.path.slice(0, CUR.d + 1), Ls = logL(CUR.child);
        const pin = planFrom(base.concat([CUR.child]), t), pout = planFrom(base, t);
        const cin = (1 - CUR.e) * Ls + costOf(pin), cout = CUR.e * Ls + costOf(pout);
        const fwd = cin < cout - 1e-9 || (Math.abs(cin - cout) < 1e-9 && CUR.dir > 0);
        segs = [{part: true, e1: fwd ? 1 : 0, L: Math.max(1e-3, fwd ? (1 - CUR.e) * Ls : CUR.e * Ls)}].concat(fwd ? pin : pout);
        redirect = (fwd ? 1 : -1) === CUR.dir;
      } else segs = planFrom(Z.path, t);
      if (!segs.length) { if (ZT === req) ZT = null; break; }
      const cost = costOf(segs);
      const per = req.o.total ? req.o.total / Math.max(0.05, cost) : req.o.ms != null ? req.o.ms : req.o.clk ? (req.o.cap ? Math.min(580, req.o.cap / Math.max(0.05, cost)) : 580) : 480;
      const sg = chainSegs(segs, per, redirect ? easeOutS : easeS);
      let all = true;
      for (let i = 0; i < segs.length; i++) {
        const st = segs[i], s = sg[i];
        const c0 = dimLevel(LAYERS[Z.path.length - 1]);
        if (!req.o.keepFx) clearFx(); else clearDim();
        let ok;
        if (st.part) ok = await zoomSeg(CUR.d, CUR.child, CUR.A, CUR.e, st.e1, s.ms, s.efn, req);
        else if (st.dir < 0) ok = await zoomSeg(st.d, st.child, tgtRect(st.d, st.child), 1, 0, s.ms, s.efn, req, 1);
        else { buildLayer(st.d + 1, st.child); ok = await zoomSeg(st.d, st.child, tgtRect(st.d, st.child), 0, 1, s.ms, s.efn, req, c0); }
        if (!ok) { all = false; break; }
      }
      if (all && ZT === req) ZT = null;
    }
  } catch (e) { console.error(e); }
  if (gen !== ZGEN) return;   // the level changed under it: setLevel() has reset everything
  ZT = null; ZW = false;
  if (!samePath(from, Z.path)) {
    select(null); scaleUI(); pipUpdate(); viewHash();
    $('pn-body').querySelectorAll('button[data-act="zoom"]').forEach(b => { const a = b.closest('.pn-act'); if (a) a.remove(); });
    if (hadFocus || wantFocus) { const f = zoomFocus(from); if (f) f.focus({preventScroll: true}); }
  }
  const w = ZWAIT; ZWAIT = []; w.forEach(r => r());
}
/* after a zoom, focus the part zoomed out of, else the first part of the new view */
function zoomFocus(from) {
  const d = Z.path.length - 1, L = LAYERS[d];
  if (from.length > Z.path.length) { const g = AP[d].zg[from[d + 1]]; if (g) return g; }
  return L.querySelector('.comp');
}
/* the reader's own zoom: while an access plays, the camera stops following it and its step is drawn again at the new
   scale */
function userNav(t) {
  hideTip();
  const k = AC.k, done = AC.done;
  if (k) { AC.tok.dead = true; if (FOLLOW) setFollow(false, true); }
  return goTo(t, {focus: svg.contains(document.activeElement)}).then(() => {
    if (!k || AC.k !== k || ZW) return;
    if (done) startAccess(k, AC.i, {still: true, done: true, noHash: true});
    else restartStep();
  });
}
/* the branch the scale control shows: the path to where the camera is going, then each scale's default child */
function branch() {
  const p = zNow().slice();
  for (let g = 0; g < 12; g++) { const nd = NODE(p[p.length - 1]); if (!nd.def) break; p.push(nd.def); }
  return p;
}
function scaleTo(i) {
  const b = branch(); if (i < 0 || i >= b.length) return;
  return userNav(b.slice(0, i + 1));
}
const zoomBy = dd => scaleTo(zNow().length - 1 + dd);
function scaleUI() {
  const zc = $('zc'), had = focusIn(zc), b = branch(), cur = zNow().length - 1;
  zc.textContent = '';
  const btn = (html, cls, title, go, pressed, dis) => {
    const e = document.createElement('button'); e.type = 'button'; if (cls) e.className = cls; e.innerHTML = html; e.title = title;
    if (pressed != null) e.setAttribute('aria-pressed', String(pressed)); if (dis) e.disabled = true;
    e.addEventListener('click', go); zc.appendChild(e); return e;
  };
  const lab = document.createElement('span'); lab.className = 'zlab'; lab.setAttribute('aria-hidden', 'true'); lab.textContent = 'Scale'; zc.appendChild(lab);
  btn('&#8722;', 'pm', 'Zoom out (−, Backspace)', () => zoomBy(-1), null, cur <= 0).setAttribute('aria-label', 'Zoom out (minus key)');
  const shown = b.slice(0, Math.min(b.length, cur + 2)), crumbs = [];
  shown.forEach((id, i) => {
    const nd = NODE(id);
    if (i) { const s = document.createElement('span'); s.className = 'sep'; s.setAttribute('aria-hidden', 'true'); s.textContent = '›'; zc.appendChild(s); crumbs.push(s); }
    const e = btn(esc(nd.short || nd.name), i > cur ? 'nx' : '', nd.name + (i === cur ? ' (shown)' : i > cur ? ' (zoom in)' : ''), () => scaleTo(i), i === cur);
    e.dataset.i = i; crumbs.push(e);
  });
  btn('+', 'pm', 'Zoom in (+)', () => zoomBy(1), null, cur >= b.length - 1).setAttribute('aria-label', 'Zoom in (plus key)');
  fitZc(zc, crumbs, cur);
  refocus(zc, had);
  const nd = NODE(Z.path[Z.path.length - 1]), txt = 'Scale: ' + (nd.label ? nd.label(SC().inst) : nd.name);
  if (!(accOn() && FOLLOW) && $('cap-scale').textContent !== txt) $('cap-scale').textContent = txt;   // an access's own camera is not announced
}

/* one row, always: first the label and the separators go, then the outer crumbs fold into "…" (− still reaches them) */
function fitZc(zc, crumbs, cur) {
  zc.classList.remove('tight');
  const rows = () => new Set([...zc.children].filter(e => e.offsetParent && e.getClientRects().length).map(e => { const r = e.getBoundingClientRect(); return Math.round((r.top + r.bottom) / 16); })).size;
  if (!zc.offsetParent || rows() <= 1) return;
  zc.classList.add('tight');
  if (rows() > 1) { const nx = zc.querySelector('button.nx'); if (nx) { nx.hidden = true; const s = nx.previousElementSibling; if (s && s.classList.contains('sep')) s.hidden = true; } }
  let k = 1, ell = null;
  while (rows() > 1) {
    const bt = crumbs.find(e => e.tagName === 'BUTTON' && +e.dataset.i === k);
    if (!bt || k >= cur) break;
    bt.hidden = true;
    if (!ell) { ell = document.createElement('span'); ell.className = 'ell'; ell.textContent = '…'; ell.setAttribute('aria-hidden', 'true'); bt.before(ell); }
    k++;
  }
}
window.addEventListener('resize', () => { clearTimeout(fitZcT); fitZcT = setTimeout(scaleUI, 150); });
let fitZcT = 0;
/* ---- the context mini-map: the scale above the one shown, with the part the camera is in ringed ---- */
const PIP = {el: $('pip'), svg: $('pipsvg')};
function pipUpdate() {
  const d = Z.path.length - 1;
  legendUI();
  if (d < 2 || ZW) { PIP.el.hidden = true; return; }
  const src0 = LAYERS[d - 1], s = PIP.svg; s.textContent = '';
  s.setAttribute('viewBox', `${FR.x} ${FR.y} ${FR.w} ${FR.h}`);
  const cl = src0.cloneNode(true);
  cl.removeAttribute('transform'); cl.style.display = ''; cl.style.opacity = 1;
  cl.querySelectorAll('[tabindex],[id]').forEach(e => { e.removeAttribute('tabindex'); e.removeAttribute('id'); });
  cl.querySelectorAll('.zdim,.ztgt,.hi,.sel').forEach(e => e.classList.remove('zdim', 'ztgt', 'hi', 'sel'));
  cl.querySelectorAll('.fx, .fxu').forEach(e => e.remove());
  s.appendChild(cl);
  const r = NODE(Z.path[d]).target(AP[d - 1], SC().inst);
  S(E('rect', {x: r.x - 8, y: r.y - 8, width: r.w + 16, height: r.h + 16, rx: 10}, s), {fill: 'none', stroke: 'var(--c2)', strokeWidth: 10});
  $('pip-cap').textContent = `${NODE(Z.path[d - 1]).name} · click to zoom out`;
  PIP.el.setAttribute('aria-label', `The scale above, ${NODE(Z.path[d - 1]).name}: zoom out to it`);
  PIP.el.hidden = false;
}

/* ================= the drawing kit ================= */
/* Roles (DESIGN.md §3): logic --c1, storage --c3, interconnect --c4, crossings --c5; --c2 is kept for what is active.
   One stroke scale: components 2, frames 2.5, sub-structure 1.25, moving trails 6, transistors 2 (lit 3.5). */
const COL = {logic: 'var(--c1)', store: 'var(--c3)', net: 'var(--c4)', xing: 'var(--c5)', aux: 'var(--c7)', ink: 'var(--ink-2)'};
let BAP = null;   // the anchor points of the layer being built
function comp(parent, key, ctx, label) {
  const g = E('g', {class: 'comp dimmable', tabindex: 0, role: 'button', 'aria-label': label, 'data-comp': key}, parent);
  g._key = key; g._ctx = ctx || {};
  if (BAP) (BAP.parts[key] = BAP.parts[key] || []).push(g);
  return g;
}
/* a part's outline: solid when documented, dotted when generic, dashed when unknown (DESIGN.md §3) */
const DASH = {generic: '2 5', unknown: '8 6'};
function boxShape(g, x, y, w, h, col, o) {
  o = o || {};
  const rx = o.rx == null ? 6 : o.rx;
  S(E('rect', {class: 'shape', x, y, width: w, height: h, rx}, g),
    {fill: o.fill || col, fillOpacity: o.fo == null ? 0.12 : o.fo, stroke: col, strokeWidth: o.sw || 2, strokeDasharray: DASH[o.kind] || null});
  // its labels' knockout: the box's own colour (kbTexts)
  g.style.setProperty('--kb', /url\(/.test(o.fill || '') ? 'var(--page)' : `color-mix(in srgb, ${o.fill || col} ${Math.round(100 * (o.fo == null ? 0.12 : o.fo))}%, var(--page))`);
  E('rect', {class: 'ring', x: x - 5, y: y - 5, width: w + 10, height: h + 10, rx: rx + 4}, g);
  if (!g._box) g._box = {x, y, w, h};
  if (o.kind === 'unknown' && o.q !== false) T(g, x + w - 12, y + 26, '?', 't-q', 'end');
}
/* a named part: o.sub (lines under the title), o.child (the scale Enter zooms into), o.cur (the instance the address
   picks), o.kind, o.ctx, o.label (for a screen reader), o.tcls */
function part(parent, key, x, y, w, h, col, title, o) {
  o = o || {};
  const kindWord = o.kind === 'unknown' ? ', unknown (asked)' : o.kind === 'generic' ? ', generic' : ', documented';
  const g = comp(parent, key, Object.assign({cur: !!o.cur}, o.ctx || {}), (o.label || title) + kindWord + (o.child ? '. Space for details; Enter zooms in.' : ': details'));
  boxShape(g, x, y, w, h, col, o);
  if (o.child) { g.setAttribute('data-child', o.child); if (o.cur !== false && BAP && (o.cur || !BAP.zg[o.child])) BAP.zg[o.child] = g; }
  const ty = o.ty || 28;
  if (title) T(g, o.center ? x + w / 2 : x + 12, y + ty, title, o.tcls || 't-labb', o.center ? 'middle' : 'start', o.f);
  (o.sub || []).forEach((s, i) => { const L0 = typeof s === 'string' ? {t: s} : s; T(g, o.center ? x + w / 2 : x + 12, y + ty + 23 + i * 21, L0.t, L0.c || 't-sm', o.center ? 'middle' : 'start', L0.f); });
  return g;
}
/* the corner tags of a frame, right-aligned on the title's line: [{kind, text}] */
function tagPill(parent, xr, y, kind, text) {
  const w = Math.round(text.length * 9.4 + 26), g = E('g', {class: 'tg ' + kind}, parent);
  E('rect', {x: xr - w, y, width: w, height: 26, rx: 13}, g);
  T(g, xr - w / 2, y + 18.5, text, '', 'middle');
  return w;
}
function frame(L, o) {
  S(E('rect', {class: 'zbd', x: FR.x, y: FR.y, width: FR.w, height: FR.h, rx: 14, 'pointer-events': 'none'}, L), {fill: 'var(--page)'});
  const fr = E('g', {class: 'frm'}, L);
  S(E('rect', {x: FR.x, y: FR.y, width: FR.w, height: FR.h, rx: 14}, fr), {fill: o.col || 'var(--c1)', fillOpacity: 0.03, stroke: o.col || 'var(--c1)', strokeWidth: 2.5, strokeDasharray: DASH[o.kind] || null});
  T(fr, FR.x + 22, FR.y + 42, o.title, 't-big', 'start', o.f);
  if (o.sub) T(fr, FR.x + 22, FR.y + 68, o.sub, 't-sm', 'start', o.subf);
  let xr = FR.x + FR.w - 18;
  (o.tags || []).forEach(t => { xr -= tagPill(fr, xr, FR.y + 18, t[0], t[1]) + 8; });
  return fr;
}
/* a rail band: a pattern and a label (DESIGN.md §3) */
function railBand(parent, x, y, w, h, pat, label, key, fids) {
  const g = key ? comp(parent, key, {}, label + ': details') : E('g', {}, parent);
  S(E('rect', {class: 'shape', x, y, width: w, height: h, rx: 10}, g), {fill: `url(#${pat})`, stroke: 'var(--ink-2)', strokeOpacity: 0.35, strokeWidth: 1.25, strokeDasharray: '4 6'});
  if (key) { E('rect', {class: 'ring', x: x - 5, y: y - 5, width: w + 10, height: h + 10, rx: 14}, g); g._box = {x, y, w, h}; }
  return g;
}
const wire = (parent, P, cls) => E('path', {class: 'w' + (cls ? ' ' + cls : ''), d: 'M' + P.map(p => `${p[0]},${p[1]}`).join(' L')}, parent);
const jn = (parent, x, y) => E('circle', {class: 'jn', cx: x, cy: y, r: 4}, parent);
function netLab(parent, x, y, t, anchor, fids) { return T(parent, x, y, t, 't-net halo', anchor || 'start', fids); }
function rail(parent, x1, x2, y, lab, anchor) {
  E('line', {class: 'rail', x1, y1: y, x2, y2: y}, parent);
  if (lab) netLab(parent, anchor === 'end' ? x1 - 8 : x2 + 8, y + 6, lab, anchor === 'end' ? 'end' : 'start');
}
function gnd(parent, x, y) {
  E('line', {class: 'w', x1: x, y1: y - 10, x2: x, y2: y}, parent);
  [[14, 0], [9, 6], [4, 12]].forEach(([hw, dy]) => E('line', {class: 'rail', x1: x - hw, y1: y + dy, x2: x + hw, y2: y + dy}, parent));
}
/* ---- transistors: a MOSFET drawn as a gate plate beside a channel; PMOS with a bubble. (x, y) is the channel's
   centre. The channel is the element the mos() primitive fills. ---- */
function mosV(parent, x, y, o) {
  o = o || {};
  const f = o.flip ? -1 : 1, g = E('g', {class: 'mos ' + (o.p ? 'pm' : 'nm')}, parent);
  const ch = E('rect', {class: 'ch', x: x - 4, y: y - 17, width: 8, height: 34, rx: 2}, g);
  const gx = x - f * 13;
  E('line', {class: 'gt', x1: gx, y1: y - 15, x2: gx, y2: y + 15}, g);
  if (o.p) E('circle', {class: 'bub', cx: gx - f * 6, cy: y, r: 4.5}, g);
  const gl = gx - f * (o.p ? 11 : 1), gend = gx - f * (o.lead || 26);
  E('line', {class: 'w', x1: gl, y1: y, x2: gend, y2: y}, g);
  E('line', {class: 'w', x1: x, y1: y - 17, x2: x, y2: y - 30}, g);
  E('line', {class: 'w', x1: x, y1: y + 17, x2: x, y2: y + 30}, g);
  if (o.name) T(parent, x + f * 12, y + 6, o.name, 't-sm', o.flip ? 'end' : 'start');
  return {g, ch, gate: {x: gend, y}, top: {x, y: y - 30}, bot: {x, y: y + 30}, x, y, p: !!o.p, h: false};
}
function mosH(parent, x, y, o) {
  o = o || {};
  const f = o.down ? -1 : 1, g = E('g', {class: 'mos ' + (o.p ? 'pm' : 'nm')}, parent);
  const ch = E('rect', {class: 'ch', x: x - 17, y: y - 4, width: 34, height: 8, rx: 2}, g);
  const gy = y - f * 13;
  E('line', {class: 'gt', x1: x - 15, y1: gy, x2: x + 15, y2: gy}, g);
  if (o.p) E('circle', {class: 'bub', cx: x, cy: gy - f * 6, r: 4.5}, g);
  const gl = gy - f * (o.p ? 11 : 1), gend = gy - f * (o.lead || 24);
  E('line', {class: 'w', x1: x, y1: gl, x2: x, y2: gend}, g);
  E('line', {class: 'w', x1: x - 17, y1: y, x2: x - 30, y2: y}, g);
  E('line', {class: 'w', x1: x + 17, y1: y, x2: x + 30, y2: y}, g);
  if (o.name) T(parent, x, y + f * 30, o.name, 't-sm', 'middle');
  return {g, ch, gate: {x, y: gend}, left: {x: x - 30, y}, right: {x: x + 30, y}, x, y, p: !!o.p, h: true};
}
/* gate-level symbols, 2-unit strokes; each returns its pins */
function invSym(parent, x, y, o) {
  o = o || {}; const s = o.s || 22, f = o.left ? -1 : 1, g = E('g', {}, parent);
  E('path', {class: 'gate', d: `M${x - f * s},${y - s * 0.8} L${x + f * s * 0.7},${y} L${x - f * s},${y + s * 0.8} Z`}, g);
  E('circle', {class: 'gate', cx: x + f * (s * 0.7 + 5), cy: y, r: 5}, g);
  return {g, in: {x: x - f * s, y}, out: {x: x + f * (s * 0.7 + 10), y}, shape: g.firstChild};
}
function andSym(parent, x, y, o) {
  o = o || {}; const h = o.h || 44, w = o.w || 44, g = E('g', {}, parent);
  const d = (o.or || o.xnor) ? `M${x},${y - h / 2} Q${x + w * 0.6},${y - h / 2} ${x + w},${y} Q${x + w * 0.6},${y + h / 2} ${x},${y + h / 2} Q${x + w * 0.25},${y} ${x},${y - h / 2} Z`
    : `M${x},${y - h / 2} L${x + w / 2},${y - h / 2} A${h / 2},${h / 2} 0 0 1 ${x + w / 2},${y + h / 2} L${x},${y + h / 2} Z`;
  const sh = E('path', {class: 'gate', d}, g);
  if (o.xnor) { E('path', {class: 'w', d: `M${x - 8},${y - h / 2} Q${x + w * 0.25 - 8},${y} ${x - 8},${y + h / 2}`}, g); }
  let ox = x + w;
  if (o.bubble || o.xnor) { E('circle', {class: 'gate', cx: x + w + 5, cy: y, r: 5}, g); ox += 10; }
  return {g, shape: sh, a: {x: x + (o.xnor ? -8 : 0), y: y - h / 4}, b: {x: x + (o.xnor ? -8 : 0), y: y + h / 4}, out: {x: ox, y}};
}
function mux2(parent, x, y, o) {
  o = o || {}; const w = o.w || 26, h = o.h || 56, g = E('g', {}, parent);
  const sh = E('path', {class: 'gate', d: `M${x},${y - h / 2} L${x + w},${y - h / 2 + 10} L${x + w},${y + h / 2 - 10} L${x},${y + h / 2} Z`}, g);
  return {g, shape: sh, in0: {x, y: y - h / 4}, in1: {x, y: y + h / 4}, out: {x: x + w, y}, sel: {x: x + w / 2, y: y + h / 2 - 5}};
}
function flopSym(parent, x, y, w, h, lab, o) {
  o = o || {}; const g = E('g', {}, parent);
  E('rect', {class: 'gate', x, y, width: w, height: h, rx: 3}, g);
  E('path', {class: 'w', d: `M${x},${y + h - 16} L${x + 9},${y + h - 10} L${x},${y + h - 4}`}, g);
  if (lab) T(g, x + w / 2, y + h / 2 + 6, lab, o.cls || 't-sm', 'middle');
  return {g, shape: g.firstChild, d: {x, y: y + h / 3}, q: {x: x + w, y: y + h / 3}, ck: {x, y: y + h - 10}};
}
/* an integrated clock gate: a latch holding the enable, ANDed with the clock (drawn as a box with its two gates) */
function icgSym(parent, x, y, o) {
  o = o || {}; const g = E('g', {}, parent), w = o.w || 58, h = o.h || 40;
  E('rect', {class: 'gate', x, y, width: w, height: h, rx: 5}, g);
  T(g, x + w / 2, y + h / 2 + 6, 'ICG', 't-smb', 'middle');
  return {g, shape: g.firstChild, ck: {x, y: y + h * 0.3}, en: {x, y: y + h * 0.7}, out: {x: x + w, y: y + h / 2}, box: {x, y, w, h}};
}

/* ================= details panel ================= */
let SEL = null;
function select(g) {
  if (SEL) { SEL.classList.remove('sel'); if (SEL._hiSel) { SEL.classList.remove('hi'); SEL._hiSel = false; } }
  SEL = g;
  if (g) { g.classList.add('sel'); if (!g.classList.contains('hi')) { g.classList.add('hi'); g._hiSel = true; } }
}
const CARDNAME = {a2: 'aifoundry2', a3: 'aifoundry3', a1c1: 'aifoundry1 card 1'};
function cardsTxt(f) {
  if (f.cards_txt) return f.cards_txt;
  if (f.cards.length === 3) return 'three cards';
  if (f.cards.length) return f.cards.map(c => CARDNAME[c]).join(', ');
  return f.kind === 'measured' ? 'card not recorded' : '';
}
const LVNAME = {l1: 'L1', l2: 'L2', l3: 'L3', scp: 'Scratchpad', dram: 'DRAM', chip: 'Chip tour'};
const KLAB = {spec: 'spec', measured: 'measured', derived: 'derived', generic: 'generic', unknown: 'unknown · asked'};
const CAV = {reimpl: 're-implementation RTL', 'spec-v1.1': 'spec v1.1'};
function kindChip(f) {
  return `<span class="kd ${f.kind}">${KLAB[f.kind]}</span>` + (f.caveat ? ` <span class="cav">${CAV[f.caveat]}</span>` : '');
}
function factLi(key) {
  const f = F[key]; if (!f) { console.error('no fact ' + key); return ''; }
  const cd = cardsTxt(f);
  return `<li class="fact" tabindex="0" data-f="${key}" data-src="1" aria-describedby="srctip"><span>${esc(f.statement)}</span><span class="meta">${kindChip(f)}`
    + (f.kind_note ? `<span class="cav">${esc(f.kind_note)}</span>` : '')
    + (cd ? `<span class="cd">${esc(cd)}</span>` : '')
    + (f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>` : '')
    + (f.ask ? `<span>asked: ${esc(f.ask)}</span>` : '')
    + `<span class="fid">${esc(LVNAME[f.level])} · ${esc(f.id)}</span></span></li>`;
}
const kpi = (html, lab) => `<div class="pn-kpi"><b>${html}</b><span>${lab}</span></div>`;
const K = (k, lab) => kpi(n(k), lab);
function topPage(keys) {
  const cnt = {}; keys.forEach(i => { const f = F[i]; if (f && f.url) { const u = f.url.split('#')[0]; cnt[u] = (cnt[u] || 0) + 1; } });
  const u = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a])[0];
  if (!u) return '';
  const on = keys.map(i => F[i]).filter(x => x && x.url && x.url.split('#')[0] === u), f = on[0];
  const lead = on.some(x => x.kind === 'measured') ? 'Measured and explained in' : 'More in';
  return `<p class="pn-what pn-more">${lead} <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>.</p>`;
}
/* the hub row an ask lands on (its anchor, #ask-…); a row still only proposed links to the hub's list */
function hubLink(id) {
  const r = RUNGS[id]; if (!r) return esc(id);
  if (r.proposed) return `<a href="${HUB}#improve" target="_blank" rel="noopener">proposed rung ${r.rung}: ${esc(r.what)} ↗</a>`;
  return `<a href="${HUB}#${esc(r.anchor)}" target="_blank" rel="noopener">rung ${r.rung}: ${esc(r.what)} ↗</a>`;
}
const askLinks = a => (a.extends ? a.extends : [a.id]).concat(a.also || []).map(hubLink);
function askHtml(a) {
  return `<div class="ask"><p class="ask-h">Unknown: ${esc(a.title)}</p><p>${esc(a.question)}</p>`
    + `<p class="ask-s"><b>What would settle it:</b> ${esc(a.settles)}</p>`
    + `<p class="ask-l">On the hub: ${askLinks(a).join(' · ')}</p></div>`;
}
const ASKOF = {}; ASKS.forEach(a => a.facts.forEach(k => { ASKOF[k] = a; }));
function asksBlock(keys, open) {
  const as = [...new Set(keys.map(k => ASKOF[k]).filter(Boolean))]; if (!as.length) return '';
  return `<details class="asks"${open ? ' open' : ''}><summary>Unknown here, and what would settle it (${as.length})</summary>${as.map(askHtml).join('')}</details>`;
}
function panel(html) {
  hideTip(); const b = $('pn-body'); b.innerHTML = html; b.scrollTop = 0;
  if (accOn()) return;   // while an access plays, st-live announces the steps
  const k = b.querySelector('.pn-kick'), t = b.querySelector('.pn-title');
  $('pn-live').textContent = (k ? k.textContent + ': ' : '') + (t ? t.textContent : '');
}
function pnReveal(el) {
  const sc = $('pn-body'); if (!el || !sc.contains(el)) return;
  const r = el.getBoundingClientRect(), s = sc.getBoundingClientRect();
  if (r.top < s.top + 4) sc.scrollTop += r.top - s.top - 8;
  else if (r.bottom > s.bottom - 4) sc.scrollTop += Math.min(r.bottom - s.bottom + 8, r.top - s.top - 8);
}
function factsBlock(keys, title) {
  if (!keys.length) return '';
  const v11 = keys.some(k => F[k] && F[k].caveat === 'spec-v1.1');
  return `<p class="pn-h pn-fh">${esc(title || 'The facts')} (${keys.length}): point at one for its source</p>`
    + (v11 ? `<p class="pn-what small">spec v1.1: the Shire Cache Specification in hand is v1.1, from core-et's Erbium branch; it also documents later chips (${src('l2.spec-version', 'l2:l2.spec-version')}).</p>` : '')
    + `<ul class="facts">${keys.map(factLi).join('')}</ul>`;
}
/* the badges of a part: [['documented', 'structure'], ['generic', 'circuit'], ['unknown', 'the macro inside']] */
function badges(list) {
  return list.map(([k, t]) => `<span class="kd ${k === 'documented' ? 'spec' : k}">${esc(k === 'unknown' ? 'unknown · asked' : k)}</span>${t ? ` <span class="cav">${esc(t)}</span>` : ''}`).join(' ');
}
function showPart(key, ctx) {
  const P = SC().parts[key]; if (!P) { console.error('no part ' + key); return; }
  const d = P(ctx || {}), keys = (PARTSF[Z.lv] && PARTSF[Z.lv][d.facts || key]) || [];
  panel(`<p class="pn-kick">${esc(d.kick)}</p><p class="pn-title">${esc(d.title)}</p>`
    + (d.badge ? `<p class="pn-badge">${badges(d.badge)}</p>` : '')
    + `<p class="pn-what">${d.what}</p>`
    + (d.kpis ? `<div class="pn-kpis">${d.kpis.join('')}</div>` : '') + (d.act ? `<div class="pn-act">${d.act}</div>` : '')
    + (d.extra || '') + asksBlock(keys) + topPage(keys) + factsBlock(keys));
}
function zoomInto(g) {
  const child = g.getAttribute('data-child'); if (!child) return false;
  const inst = SC().inst, c = g._ctx;
  if (c.inst) { const changed = Object.keys(c.inst).some(k => inst[k] !== c.inst[k]); Object.assign(inst, c.inst); if (changed) rebuildPath(); }
  select(null); showPart(g._key, g._ctx);
  userNav(pathTo(child));
  return true;
}
function activate(g) {
  if (g.getAttribute('data-child') && SEL === g) { zoomInto(g); return; }   // a second click zooms in
  select(g); showPart(g._key, g._ctx);
}
svg.addEventListener('click', e => { const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) activate(g); });
svg.addEventListener('dblclick', e => { const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) zoomInto(g); });
svg.addEventListener('keydown', e => {
  const g = e.target.closest && e.target.closest('.comp'); if (!g) return;
  if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); if (!zoomInto(g)) { select(g); showPart(g._key, g._ctx); } }
  else if (e.key === ' ' && !accOn()) { e.preventDefault(); e.stopPropagation(); select(g); showPart(g._key, g._ctx); }
});
$('pn-body').addEventListener('click', e => {
  const b = e.target.closest('button[data-act]'); if (!b) return;
  if (ACTS[b.dataset.act]) ACTS[b.dataset.act](b);
});

/* ================= sources on hover and focus ================= */
const tip = $('srctip');
function tipHtml(ids, srcOnly) {
  return ids.split(/\s+/).filter(Boolean).map(id => {
    const f = F[id]; if (!f) return '';
    const cd = cardsTxt(f);
    return `<div><b>${esc(KLAB[f.kind])}</b> · ${esc(LVNAME[f.level])} · ${esc(f.id)}${cd ? ' · ' + esc(cd) : ''}${f.caveat ? ' · ' + CAV[f.caveat] : ''}`
      + (srcOnly ? '' : `<span class="s">${esc(f.statement)}</span>`)
      + `<span class="s"><b>Source:</b> ${esc(f.source)}</span>${f.note ? `<span class="s"><b>Note:</b> ${esc(f.note)}</span>` : ''}</div>`;
  }).join('<hr>');
}
function showTip(elm) {
  const ids = elm.getAttribute('data-f'); if (!ids) return;
  tip.innerHTML = tipHtml(ids, elm.hasAttribute('data-src')); tip.style.display = 'block';
  const r = elm.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
  let x = Math.min(window.innerWidth - tw - 8, Math.max(8, r.left));
  let y = r.bottom + 6; if (y + th > window.innerHeight - 8) y = Math.max(8, r.top - th - 6);
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}
const hideTip = () => { tip.style.display = 'none'; };
const tipOK = t => !($('stage').classList.contains('present') && $('stage').contains(t));
let idleT = 0;
document.addEventListener('pointermove', () => {
  const st = $('stage'); st.classList.remove('idle'); clearTimeout(idleT);
  idleT = setTimeout(() => { if (st.classList.contains('present')) st.classList.add('idle'); }, 2000);
}, {passive: true});
document.addEventListener('pointerover', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t && tipOK(t)) showTip(t); else hideTip(); });
document.addEventListener('focusin', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t) showTip(t); else hideTip(); });
document.addEventListener('focusout', hideTip);
window.addEventListener('scroll', hideTip, {passive: true});

/* ================= drawing an access: packets, callouts and the activation primitives ================= */
/* the group under the drawing of fx's layer (trails and rings go there, under every label), else fx itself */
function under(fx) { const L = fx && fx.closest ? fx.closest('g.lay') : null; return L && L._under && L._under.parentNode === L ? L._under : fx; }
const putUnder = (fx, el) => { const u = under(fx); u.insertBefore(el, u.firstChild); return el; };
function packet(fx, col, r) {
  r = r || 11;
  const g = E('g', {class: 'pk'}, fx), inner = E('g', {}, g); g._r = r;
  S(E('circle', {r: r + 7}, inner), {fill: col, fillOpacity: 0.26});
  S(E('circle', {r}, inner), {fill: col, stroke: 'var(--page)', strokeWidth: 2.5});
  const co = fx.querySelector(':scope > .co'); if (co) fx.insertBefore(g, co);
  popIn(inner);
  return g;
}
const at = (g, p) => g.setAttribute('transform', `translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`);
/* a packet at rest never sits on a label: it settles at the nearest point clear of the view's labels (its trail, if
   any, is drawn on to it) */
function settle(fx, pk, p, trail) {
  const labs = labelBoxes(fx, pk).filter(b => !b.card), m = (pk._r || 11) + 5;
  const hit = (x, y) => labs.some(b => x + m > b.x && x - m < b.x + b.w && y + m > b.y && y - m < b.y + b.h);
  if (!labs.length || !hit(p.x, p.y)) return p;
  for (let rr = 3; rr <= 48; rr += 3) for (let a = 0; a < 24; a++) {
    const q = {x: p.x + rr * Math.cos(a * Math.PI / 12), y: p.y + rr * Math.sin(a * Math.PI / 12)};
    if (!hit(q.x, q.y)) { at(pk, q); if (trail) trail.setAttribute('d', (trail.getAttribute('d') || `M${p.x},${p.y}`) + ` L${q.x.toFixed(1)},${q.y.toFixed(1)}`); return q; }
  }
  return p;
}
const P2 = a => a.map(p => Array.isArray(p) ? {x: p[0], y: p[1]} : p);
async function travel(tok, fx, pk, P, ms, o) {
  o = o || {}; P = P2(P);
  const trail = o.trail === false ? null : S(E('path', {class: 'trail', fill: 'none'}, fx), {stroke: o.col || 'var(--c2)', strokeWidth: o.w || 6, strokeLinecap: 'round', strokeLinejoin: 'round', strokeOpacity: o.op || 0.75, strokeDasharray: o.dash ? (o.dash === true ? '2 13' : o.dash) : null});
  if (trail) putUnder(fx, trail);
  const nseg = Math.max(1, P.length - 1), cum = [0];
  for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + (o.even ? 1 : Math.hypot(P[i].x - P[i - 1].x, P[i].y - P[i - 1].y)));
  const tot = cum[cum.length - 1] || 1;
  const upto = q => {
    const s = q * tot; let i = 0; while (i < nseg - 1 && cum[i + 1] < s) i++;
    const f = cum[i + 1] > cum[i] ? Math.min(1, (s - cum[i]) / (cum[i + 1] - cum[i])) : 1;
    let d = `M${P[0].x},${P[0].y}`; for (let k = 1; k <= i; k++) d += ` L${P[k].x},${P[k].y}`;
    const a = P[i], b = P[Math.min(i + 1, P.length - 1)], p = {x: lerp(a.x, b.x, f), y: lerp(a.y, b.y, f)};
    return [p, d + ` L${p.x},${p.y}`];
  };
  const ez = o.linear ? (t => t) : easeS;
  if (P.length === 1) { at(pk, P[0]); if (o.settle !== false) settle(fx, pk, P[0], null); return trail; }
  await anim(tok, ms, q => { const [p, d] = upto(ez(q)); at(pk, p); if (trail) trail.setAttribute('d', d); });
  if (o.settle !== false) settle(fx, pk, P[P.length - 1], trail);
  return trail;
}
/* the labels of fx's layer (and its other callouts), as boxes in the layer's units: what a callout keeps clear of */
function labelBoxes(fx, own) {
  const L = fx && fx.closest ? fx.closest('g.lay') : null, out = [];
  if (!L) return out;
  let Li; try { Li = L.getCTM().inverse(); } catch (_) { return out; }
  L.querySelectorAll('text').forEach(t => {
    if (own.contains(t) || !t.textContent.trim()) return;
    let b, m; try { b = t.getBBox(); m = Li.multiply(t.getCTM()); } catch (_) { return; }
    if (!b.width) return;
    const x0 = m.a * b.x + m.c * b.y + m.e, y0 = m.b * b.x + m.d * b.y + m.f, x1 = m.a * (b.x + b.width) + m.c * (b.y + b.height) + m.e, y1 = m.b * (b.x + b.width) + m.d * (b.y + b.height) + m.f;
    out.push({x: Math.min(x0, x1), y: Math.min(y0, y1), w: Math.abs(x1 - x0), h: Math.abs(y1 - y0), imp: +getComputedStyle(t).fontWeight >= 600});
  });
  L.querySelectorAll('g.co').forEach(g => { if (g !== own && g._box) out.push(Object.assign({card: true}, g._box)); });
  return out;
}
/* where a callout's card goes: where it was asked for if it cuts no label and its leader crosses none; else the
   nearest place in the frame that does so. A card may hide labels whole (it floats over the drawing), never cut one: a
   card that would cut a label near its edge grows (up to 36 units a side) to take the label in whole. Returns the
   text's origin and the card's box */
function coPlace(fx, own, bx, by, bw, bh, x, y, lead, tgt) {
  const obs = labelBoxes(fx, own), none = {cx: bx, cy: by, box: {x: bx, y: by, w: bw, h: bh}};
  if (!obs.length) return none;
  const cards = obs.filter(b => b.card), labs = obs.filter(b => !b.card);
  const X0 = FR.x + 6, X1 = FR.x + FR.w - 6, Y0 = FR.y + 90, Y1 = FR.y + FR.h - 6, m = 5, GROW = 36;
  const inAnchor0 = x >= bx && x <= bx + bw && y >= by && y <= by + bh, x0a = x, y0a = y;
  const eval0 = (cx, cy) => {
    let B = {x: cx, y: cy, w: bw, h: bh}, cut = [];
    for (let it = 0; it < 3; it++) {
      cut = labs.filter(b => Math.min(B.x + B.w + m, b.x + b.w) > Math.max(B.x - m, b.x) && Math.min(B.y + B.h + m, b.y + b.h) > Math.max(B.y - m, b.y)
        && !(b.x >= B.x + 2 && b.x + b.w <= B.x + B.w - 2 && b.y >= B.y + 2 && b.y + b.h <= B.y + B.h - 2));
      if (!cut.length) break;
      const x0 = Math.min(B.x, ...cut.map(b => b.x - 6)), y0 = Math.min(B.y, ...cut.map(b => b.y - 6)), x1 = Math.max(B.x + B.w, ...cut.map(b => b.x + b.w + 6)), y1 = Math.max(B.y + B.h, ...cut.map(b => b.y + b.h + 6));
      if (cx - x0 > GROW || cy - y0 > GROW || x1 - cx - bw > GROW || y1 - cy - bh > GROW || x0 < X0 || y0 < Y0 || x1 > X1 || y1 > Y1) break;
      B = {x: x0, y: y0, w: x1 - x0, h: y1 - y0};
    }
    let c = Math.abs(cx - bx) + Math.abs(cy - by) + (B.w * B.h - bw * bh) * 0.3;
    for (const b of cut) { const w = Math.min(B.x + B.w + m, b.x + b.w) - Math.max(B.x - m, b.x), h = Math.min(B.y + B.h + m, b.y + b.h) - Math.max(B.y - m, b.y); c += 1e5 + w * h * 10; }
    for (const b of labs) if (b.x >= B.x + 2 && b.x + b.w <= B.x + B.w - 2 && b.y >= B.y + 2 && b.y + b.h <= B.y + B.h - 2) c += b.w * b.h * (b.imp ? 6 : 0.5);   // a bold label (a lit part's) is worth more
    for (const b of cards) if (Math.min(B.x + B.w + m, b.x + b.w) > Math.max(B.x - m, b.x) && Math.min(B.y + B.h + m, b.y + b.h) > Math.max(B.y - m, b.y)) c += 1e6;
    if (!inAnchor0 && x >= B.x - 8 && x <= B.x + B.w + 8 && y >= B.y - 8 && y <= B.y + B.h + 8) c += 5e4;
    if (tgt) { const w = Math.min(B.x + B.w, tgt.x + tgt.w) - Math.max(B.x, tgt.x), h = Math.min(B.y + B.h, tgt.y + tgt.h) - Math.max(B.y, tgt.y); if (w > 0 && h > 0) c += w * h * 8; }   // off its subject
    return {c, B};
  };
  const leadCost = (B, x = x0a, y = y0a) => {
    if (!lead) return 0;
    const qx = Math.max(B.x, Math.min(B.x + B.w, x)), qy = Math.max(B.y, Math.min(B.y + B.h, y)), L0 = Math.hypot(qx - x, qy - y);
    if (L0 <= 8) return 0;
    const near = labs.filter(b => b.x - 2 < Math.max(qx, x) && b.x + b.w + 2 > Math.min(qx, x) && b.y - 2 < Math.max(qy, y) && b.y + b.h + 2 > Math.min(qy, y));
    let hit = 0;
    if (near.length) for (let k = 1, n = Math.ceil(L0 / 4); k < n; k++) {
      const px = qx + (x - qx) * k / n, py = qy + (y - qy) * k / n;
      if (near.some(b => px > b.x - 2 && px < b.x + b.w + 2 && py > b.y - 2 && py < b.y + b.h + 2)) hit++;
    }
    return hit * 3e4 + L0 * 0.5;
  };
  // a leader that would cross its subject's labels to reach a point inside it ends at the subject's edge instead
  const edgeOf = B => {
    if (!tgt) return null;
    const cx = B.x + B.w / 2, cy = B.y + B.h / 2;
    if (cx > tgt.x && cx < tgt.x + tgt.w && cy > tgt.y && cy < tgt.y + tgt.h) return null;
    return [Math.max(tgt.x, Math.min(tgt.x + tgt.w, cx)), Math.max(tgt.y, Math.min(tgt.y + tgt.h, cy))];
  };
  const leadBest = B => {
    const c1 = leadCost(B); if (c1 < 3e4 || !tgt) return {c: c1, a: null};
    const e = edgeOf(B); if (!e) return {c: c1, a: null};
    const c2 = leadCost(B, e[0], e[1]) + 300; return c2 < c1 ? {c: c2, a: e} : {c: c1, a: null};
  };
  const e0 = eval0(bx, by), l0 = leadBest(e0.B);
  let best = {cx: bx, cy: by, box: e0.B, a: l0.a}, bc = e0.c + l0.c;
  if (e0.c < 1 && l0.c < 3e4) return best;
  for (let cy = Y0; cy <= Y1 - bh; cy += 10) for (let cx = X0; cx <= X1 - bw; cx += 12) {
    const e = eval0(cx, cy); if (e.c >= bc) continue;
    const l = leadBest(e.B), c = e.c + l.c; if (c < bc) { bc = c; best = {cx, cy, box: e.B, a: l.a}; }
  }
  return best;
}
/* the part a callout points at: the smallest part of the view whose box holds the point (a card keeps off it) */
function subjectOf(fx, x, y) {
  const L = fx && fx.closest ? fx.closest('g.lay') : null; if (!L) return null;
  let best = null;
  L.querySelectorAll('g.comp').forEach(g => { const b = g._box; if (b && x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h && (!best || b.w * b.h < best.w * best.h) && b.w * b.h < FR.w * FR.h * 0.25) best = b; });
  return best;
}
/* a leader's dot never sits on a label: it moves to the nearest place clear of every label */
function coAnchor(fx, own, x, y) {
  const labs = labelBoxes(fx, own).filter(b => !b.card), m = 9;
  const hit = (px, py) => labs.some(b => px + m > b.x && px - m < b.x + b.w && py + m > b.y && py - m < b.y + b.h);
  if (!hit(x, y)) return [x, y];
  for (let r = 3; r <= 45; r += 3) for (let a = 0; a < 24; a++) {
    const px = x + r * Math.cos(a * Math.PI / 12), py = y + r * Math.sin(a * Math.PI / 12);
    if (!hit(px, py)) return [px, py];
  }
  return [x, y];
}
/* a labelled box: a light card with an accent bar, a leader to its place; it fades in (the chip tour's). It keeps clear
   of the view's labels (coPlace); o.fixed keeps it where it is asked for */
function callout(fx, x, y, lines, o) {
  o = o || {};
  const col = o.col || 'var(--c2)', fs = o.fs || 21, lh = fs * 1.28, pad = 11, acc = 9;
  const g = E('g', {class: 'co'}, fx), lead = E('g', {class: 'co-lead'}, g);
  const box = S(E('rect', {class: 'co-box', rx: 6, filter: 'url(#co-sh)'}, g), {stroke: `color-mix(in srgb, ${col} 55%, var(--surface))`});
  const bar = S(E('rect', {class: 'co-acc', rx: 2, width: 4}, g), {fill: col});
  const tx = lines.map((ln, i) => {
    const Lx = typeof ln === 'string' ? {t: ln} : ln, t = T(g, 0, 0, Lx.t, 'co-t' + (i === 0 ? ' b' : ''), 'start', Lx.f);
    t.style.fontSize = fs + 'px'; return t;
  });
  let w = 0; tx.forEach(t => { let tw = 0; try { tw = t.getComputedTextLength(); } catch (_) { /* not rendered */ } w = Math.max(w, tw || t.textContent.length * fs * 0.55); });
  const bw = w + 2 * pad + acc, bh = lines.length * lh + pad;
  let bx = o.side === 'l' ? x - 20 - bw : (o.side === 'u' || o.side === 'd' || o.side === 'c') ? x - bw / 2 : x + 20;
  let by = o.side === 'u' ? y - 20 - bh : o.side === 'd' ? y + 20 : y - bh / 2;
  if (o.tl) { bx = x; by = y; } else if (o.tr) { bx = x - bw; by = y; }
  bx = Math.max(FR.x + 6, Math.min(FR.x + FR.w - 6 - bw, bx)); by = Math.max(FR.y + 90, Math.min(FR.y + FR.h - 6 - bh, by));
  const led = o.lead !== false && !o.tl && !o.tr;
  let B = {x: bx, y: by, w: bw, h: bh};
  if (!o.fixed) {
    const tgt = led ? subjectOf(fx, x, y) : null;
    if (led) [x, y] = coAnchor(fx, g, x, y);
    const pl = coPlace(fx, g, bx, by, bw, bh, x, y, led, tgt); bx = pl.cx; by = pl.cy; B = pl.box;
    if (pl.a) [x, y] = coAnchor(fx, g, pl.a[0], pl.a[1]);
  }
  box.setAttribute('x', B.x); box.setAttribute('y', B.y); box.setAttribute('width', B.w); box.setAttribute('height', B.h);
  bar.setAttribute('x', B.x + 5); bar.setAttribute('y', B.y + 6); bar.setAttribute('height', Math.max(4, B.h - 12));
  tx.forEach((t, i) => { t.setAttribute('x', bx + acc + pad - 2); t.setAttribute('y', by + pad / 2 + (i + 1) * lh - lh * 0.24); });
  if (led) {
    const qx = Math.max(B.x, Math.min(B.x + B.w, x)), qy = Math.max(B.y, Math.min(B.y + B.h, y));
    if (Math.hypot(qx - x, qy - y) > 8) {
      S(E('line', {x1: qx, y1: qy, x2: x, y2: y}, lead), {stroke: col, strokeWidth: 1.5});
      S(E('circle', {cx: x, cy: y, r: 4}, lead), {fill: col});
    }
  }
  g._box = B;
  return fadeIn(g, 300, o.tl || o.tr ? 0 : 6);
}
function pulse(tok, fx, p, ms, col, r1) {
  if (REDUCED || tok.ff) return wait(tok, tok.ff ? 0 : Math.min(ms, 600));
  const c = S(E('circle', {cx: p.x, cy: p.y, r: 8}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 4});
  return anim(tok, ms, q => { const e = easeS(q); c.setAttribute('r', 8 + (r1 || 46) * e); c.style.strokeOpacity = 1 - e * 0.85; }).then(() => c.remove(), e => { c.remove(); throw e; });
}
/* elements whose state an access changed (lit parts, transistors, idle parts): clearFx() puts them back */
const TOUCH = new Set();
function clearDim() {
  svg.classList.remove('dimming', 'fdim'); svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi'));
  if (SEL) SEL._hiSel = false;
}
function clearFx() {
  FX.forEach(f => { if (f) f.textContent = ''; });
  LAYERS.forEach(L => { if (L._under) L._under.textContent = ''; });
  TOUCH.forEach(e => e.classList.remove('on', 'off', 'idlep', 'hi', 'half', 'swap'));
  TOUCH.clear();
  clearDim();
}
const ctr = b => ({x: b.x + b.w / 2, y: b.y + b.h / 2});
/* lit(part): the part lifted out of the dimming, a --c2 ring around it (the step's block) */
function ringAround(fx, b, o) {
  o = o || {};
  const r = S(E('rect', {class: 'litring', x: b.x - 7, y: b.y - 7, width: b.w + 14, height: b.h + 14, rx: 10}, fx), {fill: 'var(--c2)', fillOpacity: o.fo == null ? 0.07 : o.fo, stroke: 'var(--c2)', strokeWidth: o.sw || 5});
  putUnder(fx, r); fadeIn(r, 260);
  return r;
}
function partsOf(c, key, i) {
  let gs = (c.ap.parts[key] || []);
  if (i != null) gs = gs.filter(g => g._ctx.i === i);
  else { const cur = gs.filter(g => g._ctx.cur); if (cur.length) gs = cur; }
  return gs;
}
function lit(c, keys, o) {
  o = o || {}; const out = [];
  [].concat(keys).forEach(k => partsOf(c, k, o.i).forEach(g => { g.classList.add('hi'); TOUCH.add(g); out.push(g); if (!o.noRing && g._box) ringAround(c.fx, g._box); }));
  svg.classList.add('fdim');
  return out;
}
const boxOf = (c, key, i) => { const g = partsOf(c, key, i)[0]; return g && g._box; };
/* sweep: a line coming alive from its driver outward, with a label (wordlines, clock-gated rows, select lines) */
async function sweep(tok, c, P, o) {
  o = o || {}; P = P2(P);
  const d = 'M' + P.map(p => `${p.x},${p.y}`).join(' L');
  const len = P.reduce((s, p, i) => i ? s + Math.hypot(p.x - P[i - 1].x, p.y - P[i - 1].y) : 0, 0) || 1;
  const e = S(E('path', {d, fill: 'none'}, c.fx), {stroke: o.col || 'var(--c2)', strokeWidth: o.w || 5, strokeLinecap: 'round', strokeLinejoin: 'round', strokeDasharray: `${len} ${len}`, strokeDashoffset: len});
  if (o.under) putUnder(c.fx, e);
  await anim(tok, o.ms || 700, q => { e.style.strokeDashoffset = (len * (1 - easeS(q))).toFixed(1); });
  if (o.label) { const p = o.at || P[P.length - 1]; fadeIn(T(c.fx, p.x + (o.dx == null ? 8 : o.dx), p.y + (o.dy == null ? -10 : o.dy), o.label, o.cls || 't-labb halo', o.anchor || 'start', o.f)); }
  return e;
}
/* droop: a node's level as a small meter, and what it does in words (qualitative for a generic circuit) */
async function droop(tok, c, x, y, o) {
  o = o || {};
  const g = E('g', {}, c.fx), H = o.h || 54;
  S(E('rect', {x: x - 8, y, width: 16, height: H + 4, rx: 3}, g), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 1.5});
  const lv = S(E('rect', {class: 'lvl', x: x - 5, y: y + 2, width: 10, height: H, rx: 2}, g), {fill: o.col || 'var(--c2)'});
  const t = o.l0 != null ? T(g, x + (o.side === 'l' ? -14 : 14), y + H / 2 + 7, o.l0, 't-smb halo', o.side === 'l' ? 'end' : 'start') : null;
  const from = o.from == null ? 1 : o.from, to = o.to == null ? 0.8 : o.to;
  const set = v => { const h = Math.max(1, H * v); lv.setAttribute('y', (y + 2 + H - h).toFixed(1)); lv.setAttribute('height', h.toFixed(1)); };
  set(from);
  await anim(tok, o.ms || 900, q => { set(lerp(from, to, easeS(q))); if (t && q >= 0.5 && o.l1) t.textContent = o.l1; });
  return g;
}
/* latch: a sense amplifier or a latch resolving to full swing: one node to 1, the other to 0 */
async function saLatch(tok, c, A, B, o) {
  o = o || {};
  await Promise.all([droop(tok, c, A.x, A.y, {from: o.a0 == null ? 0.55 : o.a0, to: 1, l0: '', l1: o.la || '1', side: o.sa, ms: o.ms || 600}),
    droop(tok, c, B.x, B.y, {from: o.b0 == null ? 0.45 : o.b0, to: 0, l0: '', l1: o.lb || '0', side: o.sb, ms: o.ms || 600})]);
}
/* mos: a transistor turning on (its channel filled, the gate at 1) or off (hollow, the gate at 0) */
function mos(c, t, on, o) {
  o = o || {};
  t.g.classList.toggle('on', !!on); t.g.classList.toggle('off', !on); TOUCH.add(t.g);
  if (o.lab !== false) {
    const gp = t.gate, lab = on ? (t.p ? '0' : '1') : (t.p ? '1' : '0');
    // o.at: the digit written after the gate's net name ("CK = 1") instead of on the gate
    const tx = o.at ? T(c.fx, gp.x + o.at[0], gp.y + o.at[1], '= ' + lab, 't-net halo gst', 'start')
      : t.h ? T(c.fx, gp.x + 9, gp.y + 10, lab, 't-net halo', 'start') : T(c.fx, gp.x + (o.lx || 0), gp.y - 9, lab, 't-net halo', 'middle');
    fadeIn(tx, 200);
  }
  if (on && o.cur) {
    const {x, y} = t, g = E('g', {}, c.fx);
    const dir = {down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0]}[o.cur], ox = t.h ? 0 : 18, oy = t.h ? -18 : 0;
    const px = x + ox + (o.cx || 0), py = y + oy + (o.cy || 0);
    S(E('line', {x1: px - dir[0] * 14, y1: py - dir[1] * 14, x2: px + dir[0] * 14, y2: py + dir[1] * 14, 'marker-end': 'url(#arr2)'}, g), {stroke: 'var(--c2)', strokeWidth: 3});
    fadeIn(g, 200);
  }
}
/* icg: clock pulses pass the gate only while its enable is high */
async function icg(tok, c, box, en, o) {
  o = o || {};
  const g = E('g', {}, c.fx), x0 = box.x + box.w + 6, y0 = box.y + box.h / 2, L0 = o.len || 90;
  const sq = (x, y, k) => `M${x},${y} ` + Array.from({length: k}, (_, i) => `h9 v-14 h9 v14`).join(' ');
  const pth = S(E('path', {d: sq(x0, y0 + 7, Math.floor(L0 / 18)), fill: 'none'}, g), {stroke: en ? 'var(--c2)' : 'var(--ink-2)', strokeWidth: en ? 3 : 2, strokeDasharray: en ? null : '3 5'});
  const lab = en ? (o.on != null ? o.on : 'clock passes') : (o.off != null ? o.off : 'gated off');
  if (lab) T(g, x0, y0 + 30, lab, 't-smb halo', 'start');
  if (en) await anim(tok, o.ms || 800, q => { pth.style.opacity = 0.35 + 0.65 * Math.abs(Math.sin(q * Math.PI * 3)); });
  pth.style.opacity = 1;
  return g;
}
/* idle: a part that does not take part, greyed with a line that says why (never colour alone) */
function idle(c, gs, why, o) {
  o = o || {};
  [].concat(gs).filter(Boolean).forEach(g => { g.classList.add('idlep'); TOUCH.add(g); });
  const g0 = [].concat(gs).filter(Boolean)[0];
  if (why && g0 && g0._box) {
    const b = g0._box, p = o.at || {x: b.x + b.w / 2, y: b.y + b.h / 2 + 6};
    fadeIn(T(c.fx, p.x, p.y, '✕ ' + why, 't-smb halo', o.anchor || 'middle'));
  }
}
/* counter: the step's cycles, where a fact gives them, at the frame's top right; else "not split: asked" */
function counter(c, html, sub) {
  const g = c.ctr = E('g', {}, c.fx), x = FR.x + FR.w - 22, y = FR.y + 68;
  const t = T(g, x, y, '', 't-labb halo', 'end');
  const a = E('tspan', {}, t); a.textContent = html;
  if (sub) { const b = E('tspan', {class: 't-sm', dx: 8}, t); b.textContent = '· ' + sub; }
  ctrFit(c);
  return fadeIn(g, 240);
}
/* the counter (and a dive's label) shares the frame's subtitle line: where the two would meet, the subtitle gives way
   while the step shows */
const ctrFit = c => subYield(c.ctr);
function subYield(g) {
  if (!g || !g.isConnected) return;
  const L = g.closest('g.lay'), sub = L && L.querySelector(':scope > g.frm > text.t-sm'); if (!sub || sub.classList.contains('swap')) return;
  let a, b; try { a = sub.getBBox(); b = g.getBBox(); } catch (_) { return; }
  if (a.width && b.width && a.x + a.width > b.x - 16) { sub.classList.add('swap'); TOUCH.add(sub); }
}
/* wave: a small timing diagram whose cursor advances. rows: [{name, pts: [[t, v], ...]}], t and v in 0..1; o.generic
   labels it as order only */
async function wave(tok, c, box, rows, o) {
  o = o || {};
  const g = E('g', {}, c.fx), rh = (box.h - 34) / rows.length, x0 = box.x + (o.lw || 96), w = box.w - (o.lw || 96) - 10;
  S(E('rect', {x: box.x, y: box.y, width: box.w, height: box.h, rx: 8}, g), {fill: 'var(--surface)', stroke: 'var(--border)', strokeWidth: 1.5});
  const lines = rows.map((r, i) => {
    const yb = box.y + 14 + (i + 1) * rh - 8, amp = rh - 16;
    T(g, box.x + 10, yb - amp / 2 + 6, r.name, 't-net', 'start');
    const d = r.pts.map(([t, v], k) => { const X = x0 + t * w, Y = yb - v * amp; if (!k) return `M${X},${Y}`; const pv = r.pts[k - 1][1]; return `L${X},${yb - pv * amp} L${X},${Y}`; }).join(' ') + ` L${x0 + w},${yb - r.pts[r.pts.length - 1][1] * amp}`;
    return S(E('path', {d, fill: 'none'}, g), {stroke: r.col || 'var(--ink-2)', strokeWidth: 2.5});
  });
  T(g, box.x + box.w - 10, box.y + box.h - 8, o.generic ? 'order only, not to scale (generic)' : (o.note || ''), 't-sm', 'end');
  const cur = S(E('line', {x1: x0, y1: box.y + 6, x2: x0, y2: box.y + box.h - 26}, g), {stroke: 'var(--c2)', strokeWidth: 3});
  const clip = lines.map(l => { l.style.strokeDasharray = '4000'; l.style.strokeDashoffset = 4000; return l; });
  fadeIn(g, 200);
  const upto = o.upto == null ? 1 : o.upto;
  await anim(tok, o.ms || 1600, q => {
    const X = x0 + w * upto * q; cur.setAttribute('x1', X); cur.setAttribute('x2', X);
    clip.forEach(l => { l.style.strokeDashoffset = 4000 - (w * upto * q + 200) * 1.8; });
  });
  if (upto >= 1) clip.forEach(l => { l.style.strokeDashoffset = 0; });
  return g;
}

/* ================= shared circuit drawings: every one a GENERIC textbook circuit, tied to ET facts only by counts
   and names; the frames carry their badges ================= */

/* ---- a 6T SRAM cell with its bitline pair and wordline, drawn in its own coordinates (BL at x = 120, BLB at x = 540,
   WL at y = 160, the cell between y = 190 and 336). Returns the transistors and the nodes. ---- */
function draw6T(g, o) {
  o = o || {};
  const BL = 120, BLB = 540, WL = 160;
  const pl = mosV(g, 270, 222, {p: true, flip: true, lead: 26}), nl = mosV(g, 270, 302, {flip: true, lead: 26});
  const pr = mosV(g, 390, 222, {p: true, lead: 26}), nr = mosV(g, 390, 302, {lead: 26});
  E('line', {class: 'rail', x1: 250, y1: 192, x2: 410, y2: 192}, g);
  E('line', {class: 'rail', x1: 250, y1: 332, x2: 410, y2: 332}, g);
  if (o.labels !== false) { netLab(g, 414, 197, 'VDD'); netLab(g, 414, 337, 'GND'); }
  const LB = pl.gate.x, RB = pr.gate.x;
  wire(g, [[LB, 222], [LB, 302]]); wire(g, [[RB, 222], [RB, 302]]);
  // Q to the right inverter's gates and QB to the left one's, each hopping over the other's gate bus
  E('path', {class: 'w', d: `M270,256 H${LB - 7} A7,7 0 0 1 ${LB + 7},256 H${RB}`}, g);
  E('path', {class: 'w', d: `M390,268 H${RB + 7} A7,7 0 0 0 ${RB - 7},268 H${LB}`}, g);
  jn(g, RB, 256); jn(g, LB, 268);
  const m5 = mosH(g, 195, 262, {lead: 24}), m6 = mosH(g, 465, 262, {lead: 24});
  wire(g, [[165, 262], [BL, 262]]); wire(g, [[225, 262], [270, 262]]); jn(g, 270, 262); jn(g, BL, 262);
  wire(g, [[435, 262], [390, 262]]); wire(g, [[495, 262], [BLB, 262]]); jn(g, 390, 262); jn(g, BLB, 262);
  wire(g, [[195, 225], [195, WL]]); wire(g, [[465, 225], [465, WL]]); jn(g, 195, WL); jn(g, 465, WL);
  if (o.labels !== false) { netLab(g, 262, 258, 'Q', 'end'); netLab(g, 398, 290, 'QB'); }
  return {pl, nl, pr, nr, m5, m6, Q: {x: 270, y: 262}, QB: {x: 390, y: 262}, BL, BLB, WL};
}

/* ---- the cell scale: one bit of a data panel, read and written (the shared view of the L2, L3 and scratchpad) ---- */
function buildCell(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c3)', kind: 'generic',
    tags: [['unknown', '? the bitcell · asked'], ['generic', 'GENERIC: textbook 6T']]});
  const BL = 120, BLB = 540, WL = 160, DLY = 552;
  // precharge and equalise (3 PMOS)
  const gp = comp(L, 'pre', {}, 'Bitline precharge and equaliser: two PMOS pull BL and BLB to VDD, one PMOS shorts them together; generic');
  E('line', {class: 'rail', x1: 70, y1: 18, x2: 590, y2: 18}, gp); netLab(gp, 594, 24, 'VDD');
  const p1 = mosV(gp, BL, 52, {p: true, lead: 26}), p2 = mosV(gp, BLB, 52, {p: true, flip: true, lead: 26}), p3 = mosH(gp, 330, 106, {p: true, lead: 18});
  wire(gp, [[BL, 22], [BL, 18]]); wire(gp, [[BLB, 22], [BLB, 18]]);
  wire(gp, [[300, 106], [BL, 106]]); wire(gp, [[360, 106], [BLB, 106]]); jn(gp, BL, 106); jn(gp, BLB, 106);
  netLab(gp, p1.gate.x - 6, 58, 'PREB', 'end'); netLab(gp, p2.gate.x + 6, 58, 'PREB'); netLab(gp, 330, p3.gate.y - 6, 'PREB', 'middle');
  gp._box = {x: 60, y: 10, w: 540, h: 112};
  // the bitlines
  const bls = E('g', {}, L);
  wire(bls, [[BL, 82], [BL, 360]]); wire(bls, [[BLB, 82], [BLB, 360]]);
  netLab(bls, BL - 10, 146, 'BL', 'end'); netLab(bls, BLB + 10, 146, 'BLB');
  // the wordline and its driver
  const gw = comp(L, 'wl', {}, 'Wordline driver: an inverter chain raises one wordline across the row; generic');
  const drv = invSym(gw, 10, WL, {s: 20});
  wire(gw, [[-40, WL], [drv.in.x, WL]]); netLab(gw, -44, WL + 6, 'row sel', 'end');
  E('line', {class: 'w bus', x1: drv.out.x, y1: WL, x2: 1010, y2: WL}, gw);
  netLab(gw, 640, WL - 12, 'WL');
  gw._box = {x: -60, y: WL - 26, w: 1080, h: 52};
  ap.wl = [{x: drv.out.x, y: WL}, {x: 1010, y: WL}];
  // the cell
  const gc = comp(L, 'cell', {}, 'The storage cell: two cross-coupled inverters and two access NMOS; generic; the ET bitcell is not documented');
  S(E('rect', {x: 150, y: 176, width: 360, height: 172, rx: 12}, gc), {fill: 'var(--c3)', fillOpacity: 0.07, stroke: 'var(--c3)', strokeWidth: 1.25, strokeDasharray: '2 5'});
  const c6 = draw6T(gc, {});
  T(gc, 156, 366, 'one cell: 6 transistors', 't-sm');
  gc._box = {x: 150, y: 176, w: 360, h: 172};
  // column mux (the selected pair) and the data lines
  const gm = comp(L, 'mux', {}, 'Column mux: NMOS pass gates connect the selected bitline pair to the sense amplifier; generic');
  const cm1 = mosV(gm, BL, 390, {lead: 26}), cm2 = mosV(gm, BLB, 390, {flip: true, lead: 26});
  netLab(gm, cm1.gate.x - 6, 396, 'YSEL', 'end'); netLab(gm, cm2.gate.x + 6, 396, 'YSEL');
  gm._box = {x: 60, y: 356, w: 540, h: 68};
  wire(L, [[BL, 420], [BL, DLY], [240, DLY]]); wire(L, [[BLB, 420], [BLB, DLY], [420, DLY]]);
  // write drivers
  const gd = comp(L, 'wd', {}, 'Write drivers: pull one bitline of the pair to ground; generic');
  const wd1 = mosV(gd, 60, 470, {lead: 22}), wd2 = mosV(gd, 600, 470, {flip: true, lead: 22});
  wire(gd, [[60, 440], [BL, 440]]); wire(gd, [[600, 440], [BLB, 440]]); jn(gd, BL, 440); jn(gd, BLB, 440);
  gnd(gd, 60, 510); gnd(gd, 600, 510);
  netLab(gd, wd1.gate.x - 4, 462, 'WE·DB', 'end'); netLab(gd, wd2.gate.x + 4, 462, 'WE·D');
  gd._box = {x: -40, y: 432, w: 700, h: 92};
  // the sense amplifier: a cross-coupled pair with an NMOS tail
  const gs = comp(L, 'sa', {}, 'Sense amplifier: a cross-coupled latch with an NMOS tail, fired by SAE; generic');
  E('line', {class: 'rail', x1: 222, y1: 482, x2: 438, y2: 482}, gs);
  const sp1 = mosV(gs, 240, 512, {p: true, flip: true, lead: 26}), sp2 = mosV(gs, 420, 512, {p: true, lead: 26});
  const sn1 = mosV(gs, 240, 592, {flip: true, lead: 26}), sn2 = mosV(gs, 420, 592, {lead: 26});
  const SL = sp1.gate.x, SR = sp2.gate.x;
  wire(gs, [[SL, 512], [SL, 592]]); wire(gs, [[SR, 512], [SR, 592]]);
  E('path', {class: 'w', d: `M240,546 H${SL - 7} A7,7 0 0 1 ${SL + 7},546 H${SR}`}, gs);
  E('path', {class: 'w', d: `M420,558 H${SR + 7} A7,7 0 0 0 ${SR - 7},558 H${SL}`}, gs);
  jn(gs, SR, 546); jn(gs, SL, 558); jn(gs, 240, DLY); jn(gs, 420, DLY);
  wire(gs, [[240, 622], [420, 622]]); jn(gs, 330, 622);
  const st = mosV(gs, 330, 652, {lead: 26});
  E('line', {class: 'rail', x1: 300, y1: 682, x2: 360, y2: 682}, gs); netLab(gs, 366, 688, 'GND');
  netLab(gs, st.gate.x - 6, 658, 'SAE', 'end');
  netLab(gs, 232, 540, 'SO', 'end'); netLab(gs, 428, 540, 'SOB');
  gs._box = {x: 200, y: 476, w: 260, h: 212};
  // the output latch
  const go = comp(L, 'olat', {}, 'Output latch: holds the resolved bit for the macro output; generic');
  wire(go, [[BLB, DLY], [578, DLY]]);
  S(E('rect', {class: 'gate', x: 578, y: 530, width: 92, height: 44, rx: 5}, go), {});
  T(go, 624, 558, 'out latch', 't-sm', 'middle');
  go._box = {x: 578, y: 530, w: 92, h: 44};
  // the neighbouring column on the same wordline: half-selected
  const gh = comp(L, 'half', {}, 'A neighbouring column on the same wordline: its cell also discharges a bitline, but the column mux does not pass it; generic');
  const B2 = 770, BB2 = 980;
  mosV(gh, B2, 52, {p: true, lead: 20}); mosV(gh, BB2, 52, {p: true, flip: true, lead: 20});
  wire(gh, [[B2, 22], [B2, 18]]); wire(gh, [[BB2, 22], [BB2, 18]]); E('line', {class: 'rail', x1: 740, y1: 18, x2: 1010, y2: 18}, gh);
  wire(gh, [[B2, 82], [B2, 360]]); wire(gh, [[BB2, 82], [BB2, 360]]);
  S(E('rect', {x: 810, y: 214, width: 130, height: 96, rx: 10}, gh), {fill: 'var(--c3)', fillOpacity: 0.1, stroke: 'var(--c3)', strokeWidth: 1.25});
  T(gh, 875, 256, 'cell', 't-smb', 'middle'); T(gh, 875, 278, 'same row', 't-sm', 'middle');
  wire(gh, [[B2, 262], [810, 262]]); wire(gh, [[940, 262], [BB2, 262]]); wire(gh, [[875, 214], [875, WL]]); jn(gh, 875, WL);
  const hm1 = mosV(gh, B2, 390, {lead: 20}), hm2 = mosV(gh, BB2, 390, {flip: true, lead: 20});
  netLab(gh, 875, 402, 'YSEL = 0', 'middle');
  T(gh, 875, 440, 'half-selected column', 't-smb', 'middle');
  T(gh, 875, 462, 'not read, but it swings', 't-sm', 'middle');
  gh._box = {x: 700, y: 10, w: 320, h: 460};
  ap.T = {p1, p2, p3, cm1, cm2, wd1, wd2, sp1, sp2, sn1, sn2, st, hm1, hm2, ...c6};
  ap.nodes = {BL: {x: BL, y: 300}, BLB: {x: BLB, y: 300}, BL2: {x: B2, y: 300}, BLB2: {x: BB2, y: 300}, SO: {x: 240, y: DLY}, SOB: {x: 420, y: DLY}, OUT: {x: 670, y: DLY}};
  ap.wave = {x: 700, y: 488, w: 380, h: 202};
  (o.note || []).forEach((t, i) => T(L, -150, 664 + i * 22, t, 't-sm', 'start', o.noteF));
  ap.gs = {pre: gp, wl: gw, cell: gc, mux: gm, wd: gd, sa: gs, olat: go, half: gh};
}

/* the cell's read, played step by step (DESIGN.md §2.6): precharge, wordline, one bitline droops, the sense amplifier
   fires, the column mux, the output latch, precharge again. o.q: the stored value (1 by default) */
async function cellRead(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T, nd = c.ap.nodes, q1 = o.q !== 0;
  // stored value: Q = 1 -> PL and NR on, NL and PR off
  mos(c, T0.pl, q1, {lab: false}); mos(c, T0.nr, q1, {lab: false}); mos(c, T0.nl, !q1, {lab: false}); mos(c, T0.pr, !q1, {lab: false});
  fadeIn(netLab(c.fx, 262, 292, q1 ? '= 1' : '= 0', 'end'));
  lit(c, ['pre', 'cell', 'wl'], {noRing: true});
  const wv = quiet(wave(tok, c, c.ap.wave, [
    {name: 'PREB', pts: [[0, 0], [0.15, 1], [0.8, 0]]},
    {name: 'WL', pts: [[0, 0], [0.22, 1], [0.72, 0]], col: 'var(--c2)'},
    {name: 'BLB', pts: [[0, 1], [0.3, 0.72], [0.8, 1]]},
    {name: 'SAE', pts: [[0, 0], [0.5, 1], [0.78, 0]], col: 'var(--c1)'},
    {name: 'OUT', pts: [[0, 0], [0.56, 1]]},
  ], {generic: true, ms: 4200, lw: 70}));
  [T0.p1, T0.p2, T0.p3].forEach(t => mos(c, t, true, {lab: false}));
  await Promise.all([droop(tok, c, nd.BL.x - 30, 200, {from: 1, to: 1, l0: 'precharged high', side: 'l', ms: 500}),
    droop(tok, c, nd.BLB.x + 30, 200, {from: 1, to: 1, l0: '', ms: 500})]);
  alive(tok);
  [T0.p1, T0.p2, T0.p3].forEach(t => mos(c, t, false, {lab: false}));
  const wlp = await sweep(tok, c, c.ap.wl, {label: 'WL rises', ms: 700, at: {x: 640, y: 160}, dy: -34});
  mos(c, T0.m5, true, {cur: q1 ? null : 'left', lab: false}); mos(c, T0.m6, true, {cur: q1 ? 'left' : null, lab: false});
  // exactly one bitline of the pair discharges: BLB when Q = 1
  c.fx.querySelectorAll('.lvl').forEach(e => e.closest('g') && e.closest('g').remove());
  await Promise.all([
    droop(tok, c, nd.BL.x - 30, 200, {from: 1, to: q1 ? 1 : 0.78, l0: q1 ? 'stays high' : 'droops', side: 'l', ms: 900}),
    droop(tok, c, nd.BLB.x + 30, 200, {from: 1, to: q1 ? 0.78 : 1, l0: q1 ? 'droops (tens of mV)' : 'stays high', ms: 900}),
    o.half ? droop(tok, c, nd.BLB2.x + 30, 200, {from: 1, to: 0.8, l0: 'swings', ms: 900}) : Promise.resolve(),
  ]);
  alive(tok);
  if (o.half) { lit(c, 'half'); }
  mos(c, T0.cm1, true, {lab: false}); mos(c, T0.cm2, true, {lab: false});
  if (o.half) { mos(c, T0.hm1, false, {lab: false}); mos(c, T0.hm2, false, {lab: false}); }
  lit(c, ['mux', 'sa'], {noRing: true});
  mos(c, T0.st, true, {cur: 'down'});
  fadeIn(netLab(c.fx, 366, 666, 'SAE fires', 'start'));
  await saLatch(tok, c, q1 ? {x: nd.SO.x - 40, y: 580} : {x: nd.SOB.x + 40, y: 580}, q1 ? {x: nd.SOB.x + 40, y: 580} : {x: nd.SO.x - 40, y: 580},
    {la: 'SO=1', lb: 'SOB=0', sa: 'l', sb: 'r', ms: 600});
  mos(c, q1 ? T0.sp1 : T0.sp2, true, {lab: false}); mos(c, q1 ? T0.sn2 : T0.sn1, true, {lab: false});
  lit(c, 'olat');
  fadeIn(T(c.fx, 624, 600, 'full swing', 't-smb halo', 'middle'));
  await wait(tok, 300);
  // the wordline falls and the precharge restores the bitlines: most of a read's array energy (generic)
  mos(c, T0.m5, false, {lab: false}); mos(c, T0.m6, false, {lab: false});
  if (wlp) { wlp.style.strokeOpacity = 0.3; wlp.style.strokeDasharray = '6 8'; wlp.style.strokeDashoffset = 0; }
  c.fx.querySelectorAll('text').forEach(t => { if (t.textContent === 'WL rises') t.textContent = 'WL falls'; });
  [T0.p1, T0.p2, T0.p3].forEach(t => mos(c, t, true, {lab: false}));
  fadeIn(T(c.fx, 330, 138, 'then precharge restores the bitline', 't-smb halo', 'middle'));
  await wv;
}
/* the cell's write: the drivers pull one bitline to ground, the wordline rises, the cell flips */
async function cellWrite(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T, nd = c.ap.nodes;
  mos(c, T0.pl, false, {lab: false}); mos(c, T0.nr, false, {lab: false}); mos(c, T0.nl, true, {lab: false}); mos(c, T0.pr, true, {lab: false});
  fadeIn(netLab(c.fx, 262, 292, '= 0', 'end'));
  lit(c, ['wd', 'cell', 'wl'], {noRing: true}); lit(c, 'wd');
  mos(c, T0.wd2, true, {cur: 'down', lab: false}); mos(c, T0.wd1, false, {lab: false});
  mos(c, T0.cm1, true, {lab: false}); mos(c, T0.cm2, true, {lab: false});
  await Promise.all([droop(tok, c, nd.BL.x - 30, 200, {from: 1, to: 1, l0: 'held at VDD', side: 'l', ms: 700}),
    droop(tok, c, nd.BLB.x + 30, 200, {from: 1, to: 0.02, l0: 'pulled to ground', ms: 700})]);
  alive(tok);
  await sweep(tok, c, c.ap.wl, {label: 'WL rises', ms: 600, at: {x: 640, y: 160}, dy: -34});
  mos(c, T0.m5, true, {lab: false}); mos(c, T0.m6, true, {cur: 'right', lab: false});
  await wait(tok, 500);
  // the cell flips: QB is pulled below the trip point, and the loop takes it
  mos(c, T0.pl, true, {lab: false}); mos(c, T0.nr, true, {lab: false}); mos(c, T0.nl, false, {lab: false}); mos(c, T0.pr, false, {lab: false});
  c.fx.querySelectorAll('text').forEach(t => { if (t.textContent === '= 0') t.textContent = '= 1'; });
  fadeIn(netLab(c.fx, 262, 314, 'it flips', 'end'));
  lit(c, 'cell');
  await wait(tok, 400);
  fadeIn(T(c.fx, 330, 128, 'a full-swing bitline to restore:', 't-smb halo', 'middle')); fadeIn(T(c.fx, 330, 150, 'a write costs more than a read', 't-smb halo', 'middle'));
}
/* leakage: current through the off transistors, all the time */
function cellLeak(c, fids) {
  const T0 = c.ap.T;
  mos(c, T0.pl, true, {lab: false}); mos(c, T0.nr, true, {lab: false}); mos(c, T0.nl, false, {lab: false}); mos(c, T0.pr, false, {lab: false});
  mos(c, T0.m5, false, {lab: false}); mos(c, T0.m6, false, {lab: false});
  [[T0.nl, 'down'], [T0.pr, 'down'], [T0.m6, 'left']].forEach(([t, d]) => {
    const g = E('g', {}, c.fx), ox = t.h ? 0 : 20, oy = t.h ? -20 : 0, dir = {down: [0, 1], left: [-1, 0]}[d];
    S(E('line', {x1: t.x + ox - dir[0] * 12, y1: t.y + oy - dir[1] * 12, x2: t.x + ox + dir[0] * 12, y2: t.y + oy + dir[1] * 12, 'marker-end': 'url(#arr)'}, g), {stroke: 'var(--ink-2)', strokeWidth: 2.5, strokeDasharray: '3 3'});
    fadeIn(g);
  });
  lit(c, 'cell');
  fadeIn(T(c.fx, -150, 236, 'leakage through the', 't-smb halo', 'start', fids)); fadeIn(T(c.fx, -150, 258, 'off transistors (dashed)', 't-smb halo', 'start', fids));
}

/* ---- the shared SRAM panel: a compiled macro's documented shell, a generic periphery, the internal geometry
   unknown. o: {title, sub, band: 'scp'|'l2'|'l3', row, facts} ---- */
function buildPanel(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c3)',
    tags: [['unknown', '? geometry'], ['generic', 'GENERIC periphery'], ['documented', 'shell']]});
  const AX = 40, CW = 50, RH = 44, Y0 = 118;
  // the rows drawn: the partition's edges and the addressed row (DESIGN.md §2.6: never thousands of rows)
  const R = o.row, rows = [0, 1, 2559, 2560, R, 3071, 3072, 4095].filter((v, i, a) => a.indexOf(v) === i).sort((a, b) => a - b);
  const bandOf = r => r < 2560 ? 'scp' : r < 3072 ? 'l2' : 'l3';
  const gpe = comp(L, 'periph', {}, 'Address latch, predecoder and wordline drivers; generic');
  S(E('rect', {class: 'gate', x: -150, y: 20, width: 200, height: 42, rx: 6}, gpe), {});
  T(gpe, -50, 47, 'address latch', 't-sm', 'middle');
  S(E('rect', {class: 'gate', x: 70, y: 20, width: 200, height: 42, rx: 6}, gpe), {});
  T(gpe, 170, 47, 'predecode', 't-sm', 'middle');
  wire(gpe, [[50, 41], [70, 41]]);
  gpe._box = {x: -150, y: 20, w: 420, h: 42};
  // the array: 8 rows x 12 columns of cells, in 3 groups of 4 columns
  const ga = comp(L, 'array', {}, 'The cell array: representative rows and columns of the 4,096 x 144 panel; its geometry is unknown');
  const cells = [];
  rows.forEach((r, k) => {
    const y = Y0 + k * RH;
    (ap.rowLab = ap.rowLab || [])[k] = T(ga, -56, y + 21, fnum(r), 't-mono', 'end');
    invSym(ga, -30, y + 15, {s: 12});
    wire(ga, [[-12, y + 15], [AX + 12 * CW, y + 15]], 'thin');
    const row = [];
    for (let j = 0; j < 12; j++) {
      const x = AX + j * CW + (j >> 2) * 8;
      row.push(E('rect', {class: 'cellq', x, y: y + 2, width: CW - 12, height: RH - 16, rx: 3}, ga));
    }
    cells.push(row);
    if (k < rows.length - 1 && rows[k + 1] !== r + 1) T(ga, AX - 40, y + RH + 4, '⋮', 't-sm', 'middle');
  });
  ga._box = {x: -60, y: Y0 - 8, w: AX + 12 * CW + 90, h: rows.length * RH + 8};
  T(ga, AX + 12 * CW + 16, Y0 + rows.length * RH - 6, '…', 't-labb');
  const yEnd = Y0 + rows.length * RH;
  // precharge row, column mux, sense amplifiers, output latch and write drivers (generic periphery)
  const gpr = comp(L, 'pre', {}, 'Precharge row; generic');
  S(E('rect', {class: 'gate', x: AX, y: Y0 - 30, width: 12 * CW + 16, height: 18, rx: 4}, gpr), {});
  T(gpr, AX + 12 * CW + 28, Y0 - 16, 'precharge', 't-sm');
  gpr._box = {x: AX, y: Y0 - 30, w: 12 * CW + 16, h: 18};
  const per = [['mux', 'column mux (4:1?)', yEnd + 10], ['sa', 'sense amplifiers', yEnd + 50], ['olat', 'out latch · write drivers', yEnd + 90]];
  per.forEach(([k, lab, y]) => {
    const g = comp(L, k, {}, lab + '; generic');
    for (let j = 0; j < 3; j++) {
      const x = AX + j * (4 * CW + 8);
      S(E('rect', {class: 'gate', x, y, width: 4 * CW - 12, height: 30, rx: 4}, g), {strokeDasharray: k === 'mux' ? '2 5' : null});
    }
    T(g, AX + 12 * CW + 28, y + 21, lab, 't-sm');
    g._box = {x: AX, y, w: 12 * CW + 16, h: 30};
  });
  T(L, AX, yEnd + 150, `${nt('l2_panel_w')} out per access: 128 data + 16 ECC`, 't-sm', 'start', nf('l2_panel_w'));
  // the partition band beside the rows
  const gb = comp(L, 'band', {}, 'The partition of the panel\'s rows: scratchpad, L2 and L3 are row ranges of the same macro');
  const BX = AX + 12 * CW + 48;
  [['scp', 'scratchpad', 'rows 0–2,559'], ['l2', 'L2', 'rows 2,560–3,071'], ['l3', 'L3', 'rows 3,072–4,095']].forEach(([b, nm, rr]) => {
    const ks = rows.map((r, k) => bandOf(r) === b ? k : -1).filter(k => k >= 0); if (!ks.length) return;
    const y0 = Y0 + ks[0] * RH, y1 = Y0 + (ks[ks.length - 1] + 1) * RH - 12, on = b === o.band;
    S(E('rect', {x: BX, y: y0, width: 14, height: y1 - y0, rx: 4}, gb), {fill: on ? 'var(--c2)' : 'var(--c3)', fillOpacity: on ? 0.7 : 0.3, stroke: on ? 'var(--c2)' : 'var(--c3)', strokeWidth: on ? 3 : 1.25});
    T(gb, BX + 24, (y0 + y1) / 2 - 2, nm, on ? 't-labb' : 't-lab', 'start', 'scp:scp.m0-rows l3:l3.same-arrays l2:l2.partition.rows');
    T(gb, BX + 24, (y0 + y1) / 2 + 19, rr, 't-sm', 'start', 'scp:scp.m0-rows l3:l3.same-arrays l2:l2.partition.rows');
  });
  gb._box = {x: BX - 4, y: Y0, w: 190, h: rows.length * RH};
  // the macro's documented shell: its clock gate and its trims
  const RX = 880, RW = 198;
  const gi = comp(L, 'icg', {}, 'The macro\'s clock gate: it opens only while the pipeline accesses this panel');
  boxShape(gi, RX, 18, RW, 96, 'var(--c1)', {fo: 0.06});
  const ig = icgSym(gi, RX + 14, 30, {w: 60, h: 38});
  T(gi, RX + 14, 96, 'one per macro', 't-sm');
  ap.icg = ig.box;
  const gt = comp(L, 'trim', {}, 'The macro\'s trims: read margin, read and write assist, write pulse; documented');
  boxShape(gt, RX, 130, RW, 216, 'var(--c1)', {fo: 0.06});
  T(gt, RX + 12, 156, 'model reset trims', 't-labb', 'start', 'l2:l2.trim.reset');
  [['RM', '0 (RME 0)'], ['RA', '1'], ['WA', '7'], ['WPULSE', '0']].forEach(([k, v], i) => { T(gt, RX + 12, 184 + i * 24, k, 't-mono'); T(gt, RX + RW - 12, 184 + i * 24, v, 't-mono', 'end', 'l2:l2.trim.reset'); });
  T(gt, RX + 12, 290, `RM0 row: ${nt('l2_rm0n')}`, 't-sm', 'start', nf('l2_rm0n'));
  T(gt, RX + 12, 312, `SRAM rail: ${nt('l2_v')} mV`, 't-sm', 'start', nf('l2_v'));
  T(gt, RX + 12, 332, 'on the die', 't-sm', 'start', nf('l2_v'));
  const gg = comp(L, 'geom', {}, 'The panel\'s internal geometry, unknown: asked');
  boxShape(gg, RX, 362, RW, 176, 'var(--warn)', {fo: 0.04, kind: 'unknown'});
  ['inside: if m4b4 in', 'the name means a', '4:1 column mux and', '4 banks, then', '≈1,024 wordlines', '× 576 bitline pairs'].forEach((t, i) => T(gg, RX + 12, 388 + i * 24, t, i >= 4 ? 't-smb' : 't-sm', 'start', 'l2:l2.macro.name-decode'));
  ap.cells = cells; ap.rows = rows; ap.rowK = rows.indexOf(R); ap.Y0 = Y0; ap.RH = RH; ap.AX = AX; ap.CW = CW;
  ap.zg.cell = ga;
  ga.setAttribute('data-child', o.cellChild || 'cell');
}
/* the panel's read of one row: the clock gate opens, the wordline rises, every column of the row swings (the unread
   ones half-selected), the muxes pass one column in four, the sense amplifiers fire */
async function panelRead(tok, c, o) {
  o = o || {};
  const ap = c.ap, k = ap.rowK, y = ap.Y0 + k * ap.RH + 15;
  lit(c, 'icg', {noRing: true});
  await icg(tok, c, ap.icg, true, {on: '', ms: 500, len: 72});
  alive(tok);
  await sweep(tok, c, [{x: -12, y}, {x: ap.AX + 12 * ap.CW + 16, y}], {ms: 700});
  if (ap.rowLab && ap.rowLab[k]) { ap.rowLab[k].classList.add('swap'); TOUCH.add(ap.rowLab[k]); }
  fadeIn(T(c.fx, -56, y + 6, fnum(ap.rows[k]), 't-net halo', 'end'));
  ap.cells[k].forEach((r, j) => { r.classList.add(j % 4 === 1 ? 'on' : 'half'); TOUCH.add(r); });
  if (!o.write) fadeIn(T(c.fx, ap.AX, ap.Y0 - 40, 'every column of the row swings; the mux passes one in four (if 4:1)', 't-smb halo', 'start'));
  lit(c, o.write ? ['olat'] : ['mux', 'sa']);
  await wait(tok, 500);
}

/* ---- the crossing: a level shifter at the LV/HV edge (generic circuit; the crossing itself is documented) ---- */
function buildXing(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c5)',
    tags: [['generic', 'GENERIC circuit'], ['documented', 'the crossing']]});
  // the path, at the top: LV neighbourhood, the VC FIFO, the HV bank
  const gpth = comp(L, 'fifo', {}, 'The neighbourhood\'s bank FIFO: a VC FIFO whose cells sit in the HV region, with level shifters at the edge; documented');
  [['neighbourhood (LV)', -150, 'var(--c1)'], ['VC FIFO + level shifters', 250, 'var(--c5)'], ['catch FIFO → bank (HV)', 650, 'var(--c1)']].forEach(([t, x, col]) => {
    S(E('rect', {x, y: 14, width: 330, height: 52, rx: 8}, gpth), {fill: col, fillOpacity: 0.1, stroke: col, strokeWidth: 2});
    T(gpth, x + 165, 47, t, 't-labb', 'middle');
  });
  wire(gpth, [[180, 40], [250, 40]]); wire(gpth, [[580, 40], [650, 40]]);
  gpth._box = {x: -150, y: 14, w: 1130, h: 52};
  S(E('line', {x1: 415, y1: 80, x2: 415, y2: 690}, L), {stroke: 'var(--ink-2)', strokeWidth: 2, strokeDasharray: '10 8'});
  T(L, 405, 102, 'LV', 't-labb', 'end'); T(L, 425, 102, 'HV', 't-labb');
  // the input inverter on the low rail
  const gl = comp(L, 'lvin', {}, 'The input inverter, on the minion rail; generic');
  E('line', {class: 'rail', x1: 110, y1: 150, x2: 250, y2: 150}, gl);
  netLab(gl, 106, 156, o.vddl || 'VDDL', 'end', o.vddlF);
  const ip = mosV(gl, 180, 184, {p: true, lead: 24}), inn = mosV(gl, 180, 264, {lead: 24}), IG = ip.gate.x;
  wire(gl, [[180, 154], [180, 150]]); wire(gl, [[IG, 184], [IG, 264]]); wire(gl, [[180, 214], [180, 234]]);
  gnd(gl, 180, 304);
  wire(gl, [[40, 224], [IG, 224]]); jn(gl, IG, 224); netLab(gl, 36, 230, 'IN', 'end');
  netLab(gl, 188, 218, 'INB');
  gl._box = {x: 20, y: 140, w: 260, h: 180};
  // the shifter on the high rail: a cross-coupled PMOS pair over an NMOS differential pair
  const gs = comp(L, 'ls', {}, 'The level shifter: a cross-coupled PMOS pair on the high rail over an NMOS differential pair; generic');
  E('line', {class: 'rail', x1: 470, y1: 150, x2: 780, y2: 150}, gs);
  netLab(gs, 784, 156, o.vddh || 'VDDH', 'start', o.vddhF);
  const p1 = mosV(gs, 540, 184, {p: true, flip: true, lead: 26}), p2 = mosV(gs, 720, 184, {p: true, lead: 26});
  const n1 = mosV(gs, 540, 304, {lead: 26}), n2 = mosV(gs, 720, 304, {flip: true, lead: 26});
  wire(gs, [[540, 154], [540, 150]]); wire(gs, [[720, 154], [720, 150]]);
  wire(gs, [[540, 214], [540, 274]]); wire(gs, [[720, 214], [720, 274]]);
  E('line', {class: 'rail', x1: 520, y1: 344, x2: 740, y2: 344}, gs); wire(gs, [[540, 334], [540, 344]]); wire(gs, [[720, 334], [720, 344]]);
  netLab(gs, 600, 368, 'GND');
  // cross-coupling: P1's gate from B, P2's gate from A (one hop)
  const g1 = p1.gate.x, g2 = p2.gate.x, n1g = n1.gate.x, n2g = n2.gate.x;
  E('path', {class: 'w', d: `M${g1},184 V230 H${g2 - 7} A7,7 0 0 1 ${g2 + 7},230 H720`}, gs);
  E('path', {class: 'w', d: `M${g2},184 V250 H540`}, gs);
  jn(gs, 720, 230); jn(gs, 540, 250);
  netLab(gs, 532, 244, 'A', 'end'); netLab(gs, 728, 290, 'B');
  // inputs: IN to N1, INB to N2 (a hop where they cross)
  E('path', {class: 'w', d: `M90,224 V400 H${n1g} V304`}, gs);
  E('path', {class: 'w', d: `M180,224 H300 V380 H${n1g - 7} A7,7 0 0 1 ${n1g + 7},380 H${n2g} V304`}, gs);
  jn(gs, 90, 224); jn(gs, 180, 224);
  wire(gs, [[720, 260], [900, 260]]); netLab(gs, 850, 250, 'OUT', 'middle');
  gs._box = {x: 470, y: 140, w: 470, h: 270};
  // the synchroniser (the VCFIFO's two flip-flops)
  const gy = comp(L, 'sync', {}, 'A two-flip-flop synchroniser in the receiving clock; generic circuit');
  const f1 = flopSym(gy, 620, 440, 90, 60, 'FF'), f2 = flopSym(gy, 760, 440, 90, 60, 'FF');
  wire(gy, [[900, 260], [930, 260], [930, 420], [600, 420], [600, f1.d.y], [620, f1.d.y]]);
  wire(gy, [[f1.q.x, f1.q.y], [760, f2.d.y]]); wire(gy, [[f2.q.x, f2.q.y], [900, f2.q.y]]); netLab(gy, 906, f2.q.y + 6, 'to the bank');
  wire(gy, [[560, 530], [835, 530]]); wire(gy, [[620, 530], [620, 490]]); wire(gy, [[760, 530], [760, 490]]); netLab(gy, 556, 536, 'HV clock', 'end');
  gy._box = {x: 456, y: 426, w: 584, h: 120};
  ap.T = {ip, inn, p1, p2, n1, n2};
  ap.wave = {x: -150, y: 440, w: 540, h: 250};
}
async function xingPlay(tok, c, up) {
  const T0 = c.ap.T;
  lit(c, ['lvin', 'ls'], {noRing: true});
  mos(c, T0.ip, false); mos(c, T0.inn, true, {cur: 'down', lab: false});
  fadeIn(netLab(c.fx, 36, 206, 'IN = 1', 'end')); if (up) fadeIn(netLab(c.fx, 36, 184, '(low swing)', 'end'));
  await wait(tok, 500);
  mos(c, T0.n1, true, {cur: 'down'}); mos(c, T0.n2, false);
  await droop(tok, c, 500, 212, {from: 1, to: 0, l0: 'A falls', side: 'l', ms: 700});
  mos(c, T0.p2, true, {cur: 'down', lab: false}); mos(c, T0.p1, false, {lab: false});
  await droop(tok, c, 760, 196, {from: 0, to: 1, l0: 'B rises to the high rail', ms: 700});
  lit(c, 'sync');
  const g = await wave(tok, c, c.ap.wave, [
    {name: 'IN', pts: [[0, 0], [0.18, 0.62]], col: 'var(--c1)'},
    {name: 'A', pts: [[0, 1], [0.3, 0]]},
    {name: 'OUT', pts: [[0, 0], [0.4, 1]], col: 'var(--c2)'},
    {name: 'sync', pts: [[0, 0], [0.8, 1]]},
  ], {generic: true, ms: 1200});
  return g;
}

/* ---- a latch bit (L1): a transmission-gate D latch, 10 transistors ---- */
function buildLatchCell(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c3)',
    tags: [['unknown', '? silicon cell · asked'], ['generic', 'GENERIC latch']]});
  // TG1: D -> X while CK = 1
  const g1 = comp(L, 'tg1', {}, 'Input transmission gate: an NMOS and a PMOS in parallel pass D to the latch node while the row\'s gated clock is high; generic');
  const t1n = mosH(g1, 0, 150, {lead: 22}), t1p = mosH(g1, 0, 230, {p: true, down: true, lead: 22});
  wire(g1, [[-30, 150], [-30, 230]]); wire(g1, [[30, 150], [30, 230]]);
  netLab(g1, 0, t1n.gate.y - 6, 'CK', 'middle'); netLab(g1, 0, t1p.gate.y + 20, 'CKB', 'middle');
  g1._box = {x: -40, y: 100, w: 80, h: 180};
  wire(L, [[-130, 190], [-30, 190]]); jn(L, -30, 190); netLab(L, -136, 196, 'D', 'end');
  T(L, -150, 226, 'write data', 't-sm'); T(L, -150, 246, '(from the', 't-sm'); T(L, -150, 266, 'write latch)', 't-sm');
  wire(L, [[30, 190], [121, 190]]); jn(L, 30, 190); jn(L, 70, 190); netLab(L, 78, 180, 'X');
  // INV1: X -> QB, INV2: QB -> Q
  const inv = (key, x, lab) => {
    const g = comp(L, key, {}, lab + ': a CMOS inverter, a PMOS and an NMOS; generic');
    E('line', {class: 'rail', x1: x - 20, y1: 104, x2: x + 20, y2: 104}, g);
    const p = mosV(g, x, 140, {p: true, lead: 26}), q = mosV(g, x, 240, {lead: 26}), gx = p.gate.x;
    wire(g, [[x, 110], [x, 104]]); wire(g, [[gx, 140], [gx, 240]]); wire(g, [[x, 170], [x, 210]]);
    E('line', {class: 'rail', x1: x - 20, y1: 276, x2: x + 20, y2: 276}, g); wire(g, [[x, 270], [x, 276]]);
    g._box = {x: gx - 6, y: 96, w: x + 24 - gx, h: 186};
    return {g, p, q, in: {x: gx, y: 190}, out: {x, y: 190}};
  };
  const i1 = inv('inv1', 160, 'Inverter 1'), i2 = inv('inv2', 330, 'Inverter 2');
  netLab(L, 150, 94, 'VDD', 'middle'); netLab(L, 150, 302, 'GND', 'middle');
  wire(L, [[160, 190], [291, 190]]); jn(L, 160, 190); netLab(L, 196, 180, 'QB');
  wire(L, [[330, 190], [560, 190]]); jn(L, 330, 190); jn(L, 420, 190); netLab(L, 440, 180, 'Q');
  T(L, 566, 184, 'Q → the row\'s read select', 't-smb'); T(L, 566, 206, 'a static read: no precharge,', 't-sm'); T(L, 566, 226, 'no sense amplifier', 't-sm');
  // TG2: the feedback, on while CK = 0
  const g2 = comp(L, 'tg2', {}, 'Feedback transmission gate: closes the loop while the clock is low, so the latch holds; generic');
  const t2n = mosH(g2, 245, 380, {lead: 22}), t2p = mosH(g2, 245, 460, {p: true, down: true, lead: 22});
  wire(g2, [[215, 380], [215, 460]]); wire(g2, [[275, 380], [275, 460]]);
  netLab(g2, 245, t2n.gate.y - 6, 'CKB', 'middle'); netLab(g2, 245, t2p.gate.y + 20, 'CK', 'middle');
  g2._box = {x: 205, y: 330, w: 80, h: 180};
  wire(L, [[275, 420], [420, 420], [420, 190]]); wire(L, [[215, 420], [70, 420], [70, 190]]);
  jn(L, 275, 420); jn(L, 215, 420);
  // the clock inverter
  const gk = comp(L, 'ckinv', {}, 'Clock inverter: makes CK̅ for the two transmission gates; generic');
  E('line', {class: 'rail', x1: 700, y1: 334, x2: 740, y2: 334}, gk);
  const kp = mosV(gk, 720, 370, {p: true, lead: 26}), kn = mosV(gk, 720, 450, {lead: 26});
  wire(gk, [[720, 340], [720, 334]]); wire(gk, [[681, 370], [681, 450]]); wire(gk, [[720, 400], [720, 420]]);
  E('line', {class: 'rail', x1: 700, y1: 486, x2: 740, y2: 486}, gk); wire(gk, [[720, 480], [720, 486]]);
  wire(gk, [[620, 410], [681, 410]]); netLab(gk, 616, 416, 'CK', 'end'); wire(gk, [[720, 410], [790, 410]]); netLab(gk, 796, 416, 'CKB');
  T(gk, 620, 520, 'row clock (gated)', 't-sm');
  gk._box = {x: 600, y: 326, w: 220, h: 166};
  // the contrast: a 6T SRAM cell, small
  const gx = comp(L, 'sram6t', {}, 'For contrast, a textbook 6T SRAM cell: the specification calls the shire cache\'s panels SRAM, their bitcell is asked; not used for the L1');
  S(E('rect', {x: 842, y: 90, width: 236, height: 290, rx: 10}, gx), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeDasharray: '2 5'});
  const sg = E('g', {class: 'nss', transform: 'translate(824,52) scale(0.46)'}, gx);
  E('line', {class: 'w', x1: 120, y1: 150, x2: 120, y2: 360}, sg); E('line', {class: 'w', x1: 540, y1: 150, x2: 540, y2: 360}, sg);
  E('line', {class: 'w bus', x1: 100, y1: 160, x2: 560, y2: 160}, sg);
  draw6T(sg, {labels: false});
  T(gx, 960, 116, 'for contrast: 6T SRAM', 't-smb', 'middle');
  T(gx, 960, 292, 'textbook; the spec calls', 't-sm', 'middle'); T(gx, 960, 312, 'the shire cache SRAM', 't-sm', 'middle');
  T(gx, 960, 332, '(cell asked); not the L1\'s', 't-sm', 'middle');
  gx._box = {x: 842, y: 90, w: 236, h: 290};
  T(L, -150, 690, `≈ ${nt('g_latch_t')} (textbook) · ${nt('l1_tr')} storage transistors per minion (estimate)`, 't-sm', 'start', nf('g_latch_t') + ' ' + nf('l1_tr'));
  ap.T = {t1n, t1p, t2n, t2p, kp, kn, i1p: i1.p, i1n: i1.q, i2p: i2.p, i2n: i2.q};
  ap.wave = {x: -150, y: 540, w: 700, h: 130};
}
/* the latch's write (CK high: TG1 passes D, the node follows) and its hold (CK low: the loop closes) */
async function latchWrite(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T;
  lit(c, ['tg1', 'ckinv'], {noRing: true});
  mos(c, T0.t1n, true, {cur: 'right', at: [22, -6]}); mos(c, T0.t1p, true, {at: [28, 20]}); mos(c, T0.t2n, false, {at: [28, -6]}); mos(c, T0.t2p, false, {at: [22, 20]});
  mos(c, T0.kp, false, {lab: false}); mos(c, T0.kn, true, {lab: false});
  fadeIn(netLab(c.fx, -80, 178, 'D = 1', 'start'));
  await wait(tok, 500);
  mos(c, T0.i1p, false, {lab: false}); mos(c, T0.i1n, true, {lab: false}); mos(c, T0.i2p, true, {lab: false}); mos(c, T0.i2n, false, {lab: false});
  lit(c, ['inv1', 'inv2'], {noRing: true});
  fadeIn(netLab(c.fx, 78, 216, '= 1', 'start')); fadeIn(netLab(c.fx, 196, 216, '= 0')); fadeIn(netLab(c.fx, 440, 216, '= 1'));
  const w = quiet(wave(tok, c, c.ap.wave, [
    {name: 'CK', pts: [[0, 0], [0.15, 1], [0.6, 0]], col: 'var(--c1)'},
    {name: 'D', pts: [[0, 0], [0.08, 1]]},
    {name: 'Q', pts: [[0, 0], [0.25, 1]], col: 'var(--c2)'},
  ], {generic: true, ms: 1400, lw: 70}));
  await wait(tok, 700);
  // the clock falls: TG1 opens, TG2 closes the loop, and the latch holds
  [...c.fx.querySelectorAll('.gst')].forEach(e => e.remove());
  mos(c, T0.t1n, false, {at: [22, -6]}); mos(c, T0.t1p, false, {at: [28, 20]}); mos(c, T0.t2n, true, {cur: 'left', at: [28, -6]}); mos(c, T0.t2p, true, {at: [22, 20]});
  mos(c, T0.kp, true, {lab: false}); mos(c, T0.kn, false, {lab: false});
  lit(c, 'tg2', {noRing: true});
  fadeIn(T(c.fx, 330, 505, 'CK low: the loop holds Q', 't-smb halo', 'start'));
  await w;
}
/* the latch at rest, read: Q drives the read select statically; o.hold: no refresh */
async function latchHold(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T;
  mos(c, T0.t1n, false, {lab: false}); mos(c, T0.t1p, false, {lab: false}); mos(c, T0.t2n, true, {lab: false}); mos(c, T0.t2p, true, {lab: false});
  mos(c, T0.i1p, false, {lab: false}); mos(c, T0.i1n, true, {lab: false}); mos(c, T0.i2p, true, {lab: false}); mos(c, T0.i2n, false, {lab: false});
  lit(c, ['inv1', 'inv2', 'tg2'], {noRing: true});
  fadeIn(netLab(c.fx, 440, 216, '= 1'));
  await sweep(tok, c, [{x: 330, y: 190}, {x: 560, y: 190}], {ms: 600, w: 5});
  fadeIn(T(c.fx, 245, 530, o.hold ? 'held while the minion rail is up: no refresh' : 'Q is read as it is: nothing is disturbed', 't-smb halo', 'middle'));
  await wait(tok, 400);
}

/* ---- the read tree of one output bit (L1): a 128:1 select as seven levels of 2:1 muxes; the 16 rows around the
   addressed one are drawn, the last three levels take the other 112 rows as groups ---- */
function drawReadTree(g, ap, row) {
  const base = row & ~15, leaf = row - base, X0 = -40, Y0 = 190, DY = 21, MX = [20, 110, 200, 290];
  const pos = [];
  for (let i = 0; i < 16; i++) { const y = Y0 + i * DY; pos.push({x: X0, y}); T(g, X0 - 10, y + 6, 'row ' + (base + i), base + i === row ? 't-smb' : 't-sm', 'end'); wire(g, [[X0, y], [MX[0], y]], 'thin'); }
  let cur = pos.map(p => ({x: MX[0], y: p.y}));
  const lvl = [];
  for (let L0 = 0; L0 < 4; L0++) {
    const nxt = [], ms = [];
    for (let i = 0; i < cur.length; i += 2) {
      const yc = (cur[i].y + cur[i + 1].y) / 2, h = Math.max(30, cur[i + 1].y - cur[i].y + 14);
      const m = mux2(g, MX[L0], yc, {w: 22, h});
      ms.push(m);
      if (L0 < 3) wire(g, [[m.out.x, yc], [MX[L0 + 1], yc]], 'thin');
      nxt.push({x: MX[L0 + 1] || m.out.x, y: yc});
    }
    lvl.push(ms); cur = nxt;
  }
  // levels 5-7: our 16 rows against the other groups
  const grpOf = (lo, hi) => `rows ${lo}–${hi}`;
  const bits = [4, 5, 6].map(b => (row >> b) & 1);
  const others = [4, 5, 6].map(b => { const sz = 1 << b, lo = ((row >> b) ^ 1) << b; return grpOf(lo, lo + sz - 1); });
  const CX = [420, 540, 660];
  let y = lvl[3][0].out.y, prev = lvl[3][0].out;
  const chain = [];
  CX.forEach((x, k) => {
    const m = mux2(g, x, y, {w: 24, h: 64});
    wire(g, [[prev.x, prev.y], [x, bits[k] ? m.in1.y : m.in0.y]]);
    const oy = bits[k] ? m.in0.y : m.in1.y;
    wire(g, [[x - 40, oy], [x, oy]], 'thin');
    // the group this mux weighs against: two short lines in the gap before the mux, on the unused input's outer side
    [['rows', bits[k] ? -26 : 20], [others[k].replace('rows ', ''), bits[k] ? -6 : 40]].forEach(([t, dy]) => T(g, x - 4, oy + dy, t, 't-sm halo', 'end'));
    chain.push(m); prev = m.out;
  });
  wire(g, [[prev.x, prev.y], [800, prev.y]]);
  const ff = flopSym(g, 800, prev.y - 30, 110, 60, 'out reg');
  T(g, 855, prev.y + 52, 'bit 5 of 64', 't-sm', 'middle');
  // the select bits under the levels
  ['a0', 'a1', 'a2', 'a3'].forEach((a, k) => T(g, MX[k] + 11, Y0 + 16 * DY + 16, a, 't-mono', 'middle'));
  ['a4', 'a5', 'a6'].forEach((a, k) => T(g, CX[k] + 12, y + 56, a, 't-mono', 'middle'));
  T(g, 290, Y0 + 16 * DY + 44, 'registered read address a6..a0 = ' + row.toString(2).padStart(7, '0'), 't-sm', 'middle');
  // the lit path, as points
  const P = [pos[leaf]];
  let idx = leaf;
  for (let L0 = 0; L0 < 4; L0++) { const m = lvl[L0][idx >> 1]; P.push({x: m.x || MX[L0], y: (idx & 1) ? m.in1.y : m.in0.y}); P.push(m.out); idx >>= 1; }
  chain.forEach((m, k) => { P.push({x: CX[k], y: bits[k] ? m.in1.y : m.in0.y}); P.push(m.out); });
  P.push({x: 800, y: prev.y});
  ap.treePath = P; ap.tree = {lvl, chain, ff};
}

/* ---- a tag comparator: an XNOR per bit and an AND tree (L1: 33 bits; four run on every access) ---- */
function buildComparator(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c1)', tags: [['generic', 'GENERIC circuit']]});
  const gx = comp(L, 'xnors', {}, 'An XNOR per tag bit: 1 where the stored bit equals the address bit; generic');
  const bitsA = [1, 0, 1, 1, 0, 1], bitsB = [1, 0, 1, 1, 0, 1], YS = [40, 120, 200, 280, 420, 500];
  T(gx, -150, 22, 'stored tag (way 2)', 't-smb'); T(gx, 120, 22, 'address PA[39:7]', 't-smb');
  const outs = [];
  YS.forEach((y, i) => {
    const k = i < 4 ? 32 - i : 1 - (i - 4);
    T(gx, -150, y + 26, `t[${k}] = ${bitsA[i]}`, 't-mono'); T(gx, 110, y + 47, `pa[${k + 7}] = ${bitsB[i]}`, 't-mono');
    wire(gx, [[-20, y + 20], [300, y + 20]], 'thin'); wire(gx, [[250, y + 40], [300, y + 40]], 'thin');
    const xg = andSym(gx, 310, y + 30, {xnor: true, w: 48, h: 44});
    outs.push(xg.out);
  });
  T(gx, 334, 372, '⋮', 't-labb', 'middle'); T(gx, 20, 372, `⋮ ${nt('g_cmp33')} in all`, 't-sm', 'start', nf('g_cmp33'));
  gx._box = {x: -150, y: 10, w: 530, h: 560};
  const ga = comp(L, 'andtree', {}, 'The AND tree: the way hits only if every bit matches; generic');
  const ag = andSym(ga, 520, 290, {w: 70, h: 200});
  outs.forEach(p => wire(ga, [[p.x, p.y], [480, p.y], [480, clamp(p.y, 200, 380)], [520, clamp(p.y, 200, 380)]], 'thin'));
  wire(ga, [[ag.out.x, 290], [680, 290]]); netLab(ga, 600, 280, 'hit2', 'start');
  ga._box = {x: 470, y: 180, w: 200, h: 220};
  const gw = comp(L, 'ways', {}, 'The four ways\' comparators and the encoder: a one-hot hit becomes the way number');
  [0, 1, 3].forEach((w, i) => { S(E('rect', {class: 'gate', x: 680, y: 60 + i * 70 + (w === 3 ? 240 : 0), width: 212, height: 50, rx: 6}, gw), {}); T(gw, 786, 90 + i * 70 + (w === 3 ? 240 : 0), `way ${w}: 33 XNOR + AND`, 't-sm', 'middle'); });
  S(E('rect', {class: 'gate', x: 920, y: 200, width: 150, height: 180, rx: 8}, gw), {});
  T(gw, 995, 280, 'one-hot', 't-smb', 'middle'); T(gw, 995, 302, '→ way', 't-smb', 'middle');
  wire(gw, [[680, 290], [920, 290]]);
  [85, 155, 405].forEach(y => wire(gw, [[892, y], [906, y], [906, clamp(y, 220, 360)], [920, clamp(y, 220, 360)]], 'thin'));
  gw._box = {x: 680, y: 60, w: 390, h: 400};
  T(L, -150, 640, `each XNOR: ${nt('g_xnor_t')} (textbook)`, 't-sm', 'start', nf('g_xnor_t'));
  T(L, -150, 664, `${nt('l1_cmp')} comparators run on every access, hit or miss`, 't-sm', 'start', nf('l1_cmp'));
  ap.hitP = [{x: ag.out.x, y: 290}, {x: 920, y: 290}];
  ap.xn = outs;
}

/* ================= the example address (the chip tour's mkPA(13, 0x2468A), a DRAM-region line) ================= */
const P40 = 2 ** 32;
const ADDR = {pa: D.addr.line + D.addr.offset};
const bits = (pa, hi, lo) => Math.floor(pa / 2 ** lo) % 2 ** (hi - lo + 1);
function hexPA(pa) { const s = Math.floor(pa).toString(16).padStart(10, '0'); return '0x' + s.slice(0, 2) + '_' + s.slice(2, 6) + '_' + s.slice(6); }
function mkPA(home, salt) { return 0x80 * P40 + salt * 2048 + home * 64; }
/* L1: set PA[9:6] in shared mode; in the firmware's split mode hart 0 has sets 12-13 and hart 1 sets 14-15 (PRM Table
   8.4, and the measured knee of 512 B per hart), so the issuing hart, not PA[7], picks the pair and PA[6] the set in it
   (the DCache Description §3.2.1 says only that both set MSBs are forced to 11: D.conflicts). The example's load is
   hart 0's. The row of the data array is {set, PA[5], way} (l1.lram-addr); block PA[4:3]. The way is an example: no
   address bit picks it. */
const L1_HART = 0;
function dec1(pa) {
  const set = 12 | (L1_HART << 1) | bits(pa, 6, 6), half = bits(pa, 5, 5), block = bits(pa, 4, 3), way = D.addr.way_l1;
  return {s: bits(pa, 9, 6), set, hart: L1_HART, half, block, way, row: set * 8 + half * 4 + way};
}
/* L2: bank PA[7:6], sub-bank PA[9:8], set PA[16:10] under M0's 7-bit mask, so rows 0x280-0x2FF (l2.decode,
   l2.partition.rows); a data row is {set, way} (the re-implementation's RTL; D.conflicts) */
function dec2(pa) {
  const bank = bits(pa, 7, 6), sub = bits(pa, 9, 8), lo = bits(pa, 16, 10), set = 0x280 + lo, way = D.addr.way_l2;
  return {bank, sub, lo, set, way, row: set * 4 + way};
}
const hex3 = v => '0x' + v.toString(16).toUpperCase().padStart(3, '0');

/* ================= L1 (key 1, #l1): latch RAM on the minion rail ================= */
function sayAt(c, x, y, lines, o) { unsay(c); c.co = callout(c.fx, x, y, lines, o); return c.co; }
function unsay(c) { if (c.co) { fadeOut(c.co); c.co = null; } }

function buildL1Minion(L, ap, inst) {
  frame(L, {title: 'Minion · where the L1 data cache sits', sub: `a logical drawing, not a floorplan · the L1 is ${nt('l1_kb')} of latch RAM, not SRAM`, subf: nf('l1_kb'),
    tags: [['unknown', '? floorplan · asked'], ['documented', 'documented']]});
  const rb = railBand(L, -150, 12, 902, 678, 'pat-lv', 'The minion rail', 'rail');
  T(rb, -136, 672, `minion rail (LV) · ${nt('l1_v')} at 600 MHz, measured`, 't-smb halo', 'start', nf('l1_v'));
  T(rb, -136, 650, `an L1 hit: ${nt('l1_rail')} of its power on this rail, ${nt('l1_rail_sram')} on the SRAM rail`, 't-sm halo', 'start', nf('l1_rail'));
  railBand(L, 772, 12, 306, 678, 'pat-hv', 'The Shire Channel', null);
  S(E('line', {x1: 762, y1: 12, x2: 762, y2: 690}, L), {stroke: 'var(--ink-2)', strokeWidth: 2, strokeDasharray: '10 8'});
  T(L, 786, 40, 'Shire Channel (HV)', 't-labb halo'); T(L, 786, 62, `SRAM rail ${nt('l2_v')} mV, measured`, 't-sm halo', 'start', nf('l2_v'));
  T(L, 786, 84, 'rail of the HV logic: unknown', 't-sm halo', 'start', 'l2:l2.rail.hv-logic');
  // the DCache pipeline, locked to the integer pipeline (l1.pipeline)
  const gp = comp(L, 'pipeline', {}, 'The DCache pipeline, locked to the integer pipeline');
  T(gp, -136, 42, `pipeline: ${nt('l1_stages')} DCache stages`, 't-labb halo', 'start', nf('l1_stages'));
  ap.stage = {};
  [['ID', 'pre-S0'], ['EX', 'S0'], ['TAG', 'S1'], ['MEM', 'S2'], ['WB', 'S3'], ['S4', 'write'], ['S5', 'bypass']].forEach(([nm, s], i) => {
    const x = -136 + i * 124, box = {x, y: 56, w: 110, h: 62};
    S(E('rect', {x, y: 56, width: 110, height: 62, rx: 6}, gp), {fill: 'var(--c1)', fillOpacity: 0.12, stroke: 'var(--c1)', strokeWidth: 2});
    T(gp, x + 55, 84, nm, 't-labb', 'middle'); T(gp, x + 55, 106, s, 't-sm', 'middle', 'l1:l1.pipeline');
    if (i) wire(gp, [[x - 14, 87], [x, 87]]);
    ap.stage[nm] = {x: x + 55, y: 132, box};
  });
  gp._box = {x: -136, y: 56, w: 854, h: 62};
  // the data cache (zoom in)
  const gd = part(L, 'dcache', -136, 150, 700, 340, COL.store, 'L1 data cache', {child: 'dcache', cur: true, fo: 0.06,
    sub: [{t: nt('l1_geom'), f: nf('l1_geom')}, {t: 'tags in latch register files · data in 4 LRAM blocks', f: 'l1:l1.lram l1:l1.metadata'}]});
  for (let w = 0; w < 4; w++) S(E('rect', {x: -116 + w * 84, y: 236, width: 74, height: 60, rx: 4, 'pointer-events': 'none'}, gd), {fill: 'var(--c3)', fillOpacity: 0.15, stroke: 'var(--c3)', strokeWidth: 1.25});
  T(gd, -116, 318, 'tags: 4 latch RFs', 't-sm');
  for (let b = 0; b < 4; b++) {
    const x = -116 + b * 168;
    S(E('rect', {x, y: 340, width: 150, height: 110, rx: 5, 'pointer-events': 'none'}, gd), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 1.25});
    T(gd, x + 75, 400, 'LRAM ' + b, 't-sm', 'middle');
  }
  T(gd, -116, 474, `data: ${nt('l1_blocks')} LRAM blocks of ${nt('l1_rows')} × ${nt('l1_rowbits')}`, 't-sm', 'start', nf('l1_rows'));
  ap.dcacheBox = {x: -136, y: 150, w: 700, h: 340};
  part(L, 'tlb', 588, 150, 150, 72, COL.logic, 'TLB', {sub: [{t: nt('l1_tlb'), f: nf('l1_tlb')}]});
  const gm = part(L, 'mh', 588, 236, 150, 110, COL.logic, 'miss', {sub: [{t: 'handlers × ' + nt('l1_mh'), f: nf('l1_mh')}]});
  for (let i = 0; i < 2; i++) S(E('rect', {x: 600 + i * 66, y: 302, width: 58, height: 32, rx: 4, 'pointer-events': 'none'}, gm), {fill: 'var(--c1)', fillOpacity: 0.18, stroke: 'var(--c1)', strokeWidth: 1.25});
  const gr = part(L, 'rq', 588, 360, 150, 130, COL.logic, 'replay', {sub: [{t: 'queue: ' + nt('l1_rq').replace(' entries', ''), f: nf('l1_rq')}]});
  ap.rqSlots = [];
  for (let i = 0; i < 8; i++) ap.rqSlots.push(S(E('rect', {x: 600 + (i % 4) * 33, y: 426 + Math.floor(i / 4) * 28, width: 27, height: 22, rx: 3, 'pointer-events': 'none'}, gr), {fill: 'var(--c1)', fillOpacity: 0.15, stroke: 'var(--c1)', strokeWidth: 1.25}));
  part(L, 'vpu', -136, 516, 340, 116, COL.aux, 'VPU · 8 lanes', {sub: [{t: `a ${nt('l1_vpu')} port: one register row a cycle`, f: nf('l1_vpu')}, 'reads the scratchpad directly']});
  part(L, 'tl', 224, 516, 340, 116, COL.aux, 'TensorLoad unit', {sub: ['TL0: into scratchpad rows', 'TL1: into the VPU\'s buffer', {t: `${nt('l1_tl4')} in flight`, f: nf('l1_tl4')}]});
  part(L, 'ports', 588, 516, 160, 116, COL.xing, 'ports', {sub: ['fill · evict · miss', 'to the', 'neighbourhood']});
  part(L, 'nbr', 800, 380, 270, 290, COL.xing, 'neighbourhood', {sub: ['Miss / Evict flops', 'arbiters', 'bank FIFOs: VC FIFOs', 'with level shifters', {t: '→ the L2 (key 2)', c: 't-smb'}]});
  ap.port = {x: 748, y: 595}; ap.nbr = {x: 935, y: 520}; ap.vpu = {x: 34, y: 560}; ap.tl = {x: 394, y: 560};
  ap.dc = {x: 214, y: 320}; ap.rq = {x: 663, y: 450}; ap.mh = {x: 663, y: 318};
}

function buildL1Cache(L, ap, inst) {
  frame(L, {title: 'L1 data cache · 16 sets × 4 ways × 64 B', sub: 'tags first, then one way\'s row: the way is part of the data row\'s address', subf: 'l1:l1.phased',
    tags: [['unknown', '? parity on silicon · asked'], ['documented', 'documented']], col: COL.store});
  ap.setY = [];
  for (let w = 0; w < 4; w++) {
    const x = -140 + w * 128;
    const g = part(L, 'tags', x, 16, 118, 196, COL.store, 'way ' + w, {ctx: {i: w}, fo: 0.08, sub: [{t: nt('l1_rf16'), f: nf('l1_rf16')}, {t: '× ' + nt('l1_entry'), f: nf('l1_entry')}]});
    for (let s = 0; s < 16; s++) wire(g, [[x + 10, 110 + s * 6], [x + 108, 110 + s * 6]], 'thin');
    ap.setY[w] = {x1: x + 10, x2: x + 108, y: 110 + inst.set * 6};
  }
  part(L, 'valid', -140, 226, 246, 54, COL.logic, 'valid: 64 flip-flops', {ty: 34});
  part(L, 'lru', 118, 226, 254, 54, COL.logic, 'LRU: 4 × 4 per set', {ty: 34});
  const gc = part(L, 'cmp', 396, 16, 150, 264, COL.logic, 'compare', {child: 'cmp', cur: true, sub: [{t: nt('l1_cmp') + ' comparators', f: nf('l1_cmp')}]});
  ap.eq = [];
  for (let w = 0; w < 4; w++) { const cy = 110 + w * 42; S(E('circle', {cx: 470, cy, r: 16, 'pointer-events': 'none'}, gc), {fill: 'var(--surface)', stroke: 'var(--c1)', strokeWidth: 2}); T(gc, 470, cy + 7, '=', 't-labb', 'middle'); ap.eq.push({x: 470, y: cy}); }
  ap.cmpBox = {x: 396, y: 16, w: 150, h: 264};
  part(L, 'hit', 576, 16, 170, 118, COL.logic, 'one-hot hit', {sub: ['→ the way', 'number'], facts: 'cmp'});
  part(L, 'pma', 576, 150, 170, 130, COL.logic, 'PMA check', {sub: ['cacheable?']});
  part(L, 's4arb', 776, 16, 302, 264, COL.logic, 'write port', {sub: [{t: nt('l1_s4') + ' clients, static priority', f: nf('l1_s4')}, '1 stores · 2 fills (SEND)', '3 L2 fills · 4 TensorLoad', '5 config clear', '6 cache-op clear · 7 debug']});
  ap.blockBox = [];
  for (let b = 0; b < 4; b++) {
    const x = -140 + b * 244, y = 306, w = 230, h = 244;
    const g = part(L, 'blocks', x, y, w, h, COL.store, `LRAM block ${b}`, {ctx: {i: b, inst: {block: b}}, child: 'lram', cur: b === inst.block, fo: 0.08, sub: [`PA[4:3] = ${b}`]});
    [0, 1].forEach(hh => {
      const mx = x + 12 + hh * 106;
      S(E('rect', {x: mx, y: y + 70, width: 98, height: 160, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.15, stroke: 'var(--c3)', strokeWidth: 1.25});
      for (let r = 0; r < 8; r++) wire(g, [[mx + 6, y + 84 + r * 19], [mx + 92, y + 84 + r * 19]], 'thin');
      T(g, mx + 49, y + 222, hh ? 'high 32' : 'low 32', 't-sm', 'middle');
    });
    ap.blockBox[b] = {x, y, w, h};
  }
  ap.rowY = 306 + 70 + 8 + (inst.row / 128) * 144;
  T(L, 850, 336, 'data row', 't-labb'); T(L, 850, 358, '{set, PA[5], way}', 't-mono', 'start', 'l1:l1.lram-addr');
  T(L, 850, 384, `= {${inst.set}, ${inst.half}, ${inst.way}}`, 't-mono', 'start', 'l1:l1.lram-addr');
  T(L, 850, 410, `= row ${inst.row} of ${nt('l1_rows')}`, 't-smb', 'start', 'l1:l1.lram-addr');
  T(L, 850, 450, 'a scalar load reads', 't-sm', 'start', 'l1:l1.bank-enables'); T(L, 850, 470, 'one block; a 32-byte', 't-sm', 'start', 'l1:l1.bank-enables'); T(L, 850, 490, 'vector load all four', 't-sm', 'start', 'l1:l1.bank-enables');
  // the set map: how the firmware's mode uses the 16 sets (l1.modes, l1.firmware-mode)
  const gs = comp(L, 'setmap', {}, 'The 16 sets as the firmware leaves them: sets 0 to 11 are the tensor scratchpad, 12 and 13 hart 0, 14 and 15 hart 1');
  T(gs, -140, 590, 'the 16 sets, as the firmware sets them', 't-labb');
  for (let s = 0; s < 16; s++) {
    const x = -140 + s * 60, col = s < 12 ? 'var(--c7)' : 'var(--c3)', on = s === inst.set;
    S(E('rect', {x, y: 602, width: 52, height: 40, rx: 4}, gs), {fill: col, fillOpacity: on ? 0.5 : s < 12 ? 0.15 : 0.28, stroke: on ? 'var(--c2)' : col, strokeWidth: on ? 3.5 : 1.25});
    T(gs, x + 26, 628, String(s), on ? 't-smb' : 't-sm', 'middle');
  }
  T(gs, -140, 666, `sets 0–11: tensor scratchpad, ${nt('l1_scp_kb')}`, 't-sm', 'start', nf('l1_scp_kb'));
  T(gs, 580, 666, 'hart 0', 't-sm', 'start', nf('l1_h0sets')); T(gs, 700, 666, 'hart 1', 't-sm', 'start', nf('l1_h1sets'));
  T(gs, 830, 592, `${nt('l1_hart')} per hart;`, 't-smb', 'start', nf('l1_hart')); T(gs, 830, 612, 'hart 1 reads', 't-smb', 'start', nf('l1_hart'));
  T(gs, 830, 634, `${nt('l1_knee_in')},`, 't-sm', 'start', nf('l1_knee_in'));
  T(gs, 830, 656, `${nt('l1_knee_out')} (cycles)`, 't-sm', 'start', nf('l1_knee_out'));
  gs._box = {x: -140, y: 576, w: 1216, h: 100};
  ap.setCell = {x: -140 + inst.set * 60, y: 602, w: 52, h: 40};
}

function buildL1Block(L, ap, inst) {
  const b = inst.block, R = inst.row;
  frame(L, {title: `LRAM block ${b} · 128 × 64 bits`, f: nf('l1_rows'),
    sub: `two ${nt('l1_macro')} macros · PA[4:3] = ${b} · the example's row {set ${inst.set}, PA[5] = ${inst.half}, way ${inst.way}} = ${R}`, subf: 'l1:l1.lram-addr l1:l1.lram-macros',
    tags: [['unknown', '? silicon macro · asked'], ['derived', 'latch-RF pattern: assumed'], ['documented', 'structure']], col: COL.store});
  part(L, 'wlatch', -150, 16, 250, 64, COL.logic, 'write-data latch', {sub: ['low phase (CKGTNLT)']});
  part(L, 'wdec', -150, 104, 116, 470, COL.logic, 'write', {sub: ['address', 'decoder', '7 → 128']});
  const r0 = R & ~4, rows = [0, 1, r0, r0 + 4, 126, 127].filter((v, i, a) => v >= 0 && v < 128 && a.indexOf(v) === i).sort((x, y) => x - y);
  const gi = comp(L, 'icg', {}, 'The per-row clock gates: the decoded write address opens one row\'s gate');
  const garr = comp(L, 'rows', {}, `The array: ${rows.length} of the 128 rows drawn, 64 latches each; Enter zooms into row ${R}`);
  garr.setAttribute('data-child', 'row');
  ap.rowYs = {}; ap.cellsOf = {};
  rows.forEach((r, k) => {
    const y = 120 + k * 64, on = r === R;
    S(E('rect', {class: 'gate', x: -24, y: y + 6, width: 30, height: 28, rx: 4}, gi), {});
    E('path', {class: 'w', d: `M${-18},${y + 26} h5 v-12 h5 v12 h5 v-12 h5`}, gi);
    wire(gi, [[-34, y + 20], [-24, y + 20]], 'thin');
    T(garr, 58, y + 26, String(r), on ? 't-smb' : 't-mono', 'end');
    const cells = [];
    [0, 1].forEach(hh => {
      const mx = 70 + hh * 368;
      for (let j = 0; j < 16; j++) cells.push(E('rect', {class: 'cellq', x: mx + j * 21, y: y + 4, width: 17, height: 32, rx: 3}, garr));
      T(garr, mx + 16 * 21 + 4, y + 26, '…', 't-sm');
    });
    wire(garr, [[6, y + 20], [22, y + 20]], 'thin');
    ap.rowYs[r] = y; ap.cellsOf[r] = cells;
    if (k < rows.length - 1 && rows[k + 1] !== r + 1) T(garr, 36, y + 58, '⋮', 't-sm', 'middle');
  });
  gi._box = {x: -26, y: 116, w: 34, h: rows.length * 64}; garr._box = {x: 22, y: 116, w: 790, h: rows.length * 64};
  T(gi, -24, 108, 'row gates', 't-sm');
  BAP.zg.row = garr;
  T(L, 90, 108, 'low 32 bits', 't-sm'); T(L, 438, 108, 'high 32 bits', 't-sm');
  const y0 = ap.rowYs[R];
  ap.rowBox = {x: 70, y: y0, w: 720, h: 40};
  part(L, 'rdreg', 826, 16, 252, 78, COL.logic, 'read address', {sub: ['register (rising edge)']});
  part(L, 'rsel', 826, 118, 252, 320, COL.logic, 'row select', {kind: 'generic', child: 'row', sub: [{t: nt('g_mux'), f: nf('g_mux')}, 'a mux tree', '(no bitlines, no sense', 'amplifier, in the model)']});
  part(L, 'oreg', 826, 462, 252, 100, COL.logic, '64-bit output', {sub: ['register → S2 data']});
  T(L, -150, 616, 'assumed: the ET latch-RF pattern (silicon: asked)', 't-smb', 'start', 'l1:l1.latch-rf l1:l1.u-cell');
  T(L, -150, 640, 'write: one row\'s clock gate fires; its 64 latches take the bus', 't-sm', 'start', 'l1:l1.latch-rf');
  T(L, -150, 664, 'read: the registered address selects the row through a mux tree', 't-sm', 'start', 'l1:l1.latch-rf');
  ap.rsel = {x: 826, y: 278}; ap.oreg = {x: 952, y: 512}; ap.rdreg = {x: 952, y: 94}; ap.wl = {x: -25, y: 48};
}

function buildL1Row(L, ap, inst) {
  const R = inst.row;
  frame(L, {title: `Row ${R} · its latches and one bit's read tree`, f: nf('l1_rowbits'),
    sub: 'the write fires the row\'s clock gate; the read selects the row through seven levels of 2:1 muxes', subf: 'l1:g.latch-read',
    tags: [['unknown', '? silicon macro · asked'], ['generic', 'GENERIC latch array']], col: COL.store});
  const gi = comp(L, 'icg', {}, 'The row\'s clock gate: the decoded write address enables it; generic circuit, ET pattern');
  const ic = icgSym(gi, -150, 16, {w: 70, h: 44});
  wire(gi, [[-80, 38], [1070, 38]], 'bus'); netLab(gi, 1070, 30, 'GCLK', 'end');
  gi._box = {x: -150, y: 16, w: 70, h: 44};
  const gr = comp(L, 'row', {}, `Row ${R}: 64 latches on one gated clock`);
  ap.lat = [];
  for (let i = 0; i < 16; i++) {
    const x = -50 + i * 66, lb = E('g', {}, gr);
    E('rect', {class: 'gate', x, y: 62, width: 56, height: 54, rx: 4}, lb);
    T(lb, x + 28, 94, 'L' + i, 't-sm', 'middle');
    wire(lb, [[x + 28, 38], [x + 28, 62]], 'thin'); wire(lb, [[x + 14, 116], [x + 14, 140]], 'thin');
    ap.lat.push({x, y: 62, w: 56, h: 54, q: {x: x + 42, y: 116}});
  }
  T(gr, 1004, 94, '… L63', 't-sm', 'start');
  wire(gr, [[-150, 140], [1070, 140]], 'bus'); netLab(gr, 1070, 164, 'write bus', 'end');
  gr._box = {x: -60, y: 56, w: 1130, h: 90};
  const lb5 = comp(L, 'latchbit', {}, 'Latch 5 of the row: the bit whose read tree is drawn; Enter zooms into its transistors');
  lb5.setAttribute('data-child', 'latch');
  const L5 = ap.lat[5];
  S(E('rect', {class: 'shape', x: L5.x - 4, y: L5.y - 4, width: L5.w + 8, height: L5.h + 8, rx: 6}, lb5), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 2.5});
  E('rect', {class: 'ring', x: L5.x - 9, y: L5.y - 9, width: L5.w + 18, height: L5.h + 18, rx: 9}, lb5);
  lb5._box = {x: L5.x - 4, y: L5.y - 4, w: L5.w + 8, h: L5.h + 8};
  BAP.zg.latch = lb5; ap.latchBox = lb5._box;
  const gt = comp(L, 'muxtree', {}, `The read tree of bit 5: 128 rows to one output, seven levels of 2:1 muxes; generic`);
  drawReadTree(gt, ap, R);
  gt._box = {x: -160, y: 176, w: 1080, h: 380};
  T(L, -150, 168, `latch 5 of every row feeds this tree; row ${R}'s is the lit input`, 't-sm');
  ap.wave = {x: 520, y: 560, w: 560, h: 130};
}

function buildL1Latch(L, ap, inst) {
  buildLatchCell(L, ap, {title: 'One latch bit · a transmission-gate D latch',
    sub: 'how ET\'s latch register files hold a bit; the cell inside the silicon macro is not documented'});
}
function buildL1Cmp(L, ap, inst) {
  buildComparator(L, ap, {title: 'Tag comparator · XNORs and an AND tree', sub: `${nt('g_cmp33')} per way, an XNOR each; all four ways compare in S1 and one hits (way 2 in the example)`});
}

SCENES.l1 = {
  lv: 'l1', title: 'L1 data cache', short: 'L1', root: 'minion', inst: {},
  setInst() { const a = dec1(ADDR.pa); this.inst = {block: a.block, row: a.row, set: a.set, half: a.half, way: a.way}; },
  head: () => `${n('l1_kb')} per minion, not SRAM: latch RAM on the ${n('l1_v')} minion rail; a hit takes ${n('l1_lat')} and about ${n('l1_e')} per 32-byte load`,
  addrFields(pa) {
    const a = dec1(pa);
    return [['hart', '', a.hart ? '1 (sets 14–15)' : '0 (sets 12–13)', 'l1:l1.modes l1:l1.knee'], ['set', '12 + 2·hart + PA[6]', a.set, 'l1:l1.modes l1:l1.scp-impl', true],
      ['half', 'PA[5]', a.half, 'l1:l1.lram-addr'], ['block', 'PA[4:3]', a.block, 'l1:l1.lram-addr', true], ['row', '{set, PA[5], way}', a.row, 'l1:l1.lram-addr', true], ['tag', 'PA[39:7]', '', 'l1:l1.metadata']];
  },
  scales: {
    minion: {name: 'Minion', short: 'Minion', parent: null, def: 'dcache', build: buildL1Minion},
    dcache: {name: 'Data cache', short: 'Cache', parent: 'minion', def: 'lram', tw: 700, target: ap => ap.dcacheBox, build: buildL1Cache},
    lram: {name: 'LRAM block', short: 'Block', parent: 'dcache', def: 'row', tw: 230, target: (ap, inst) => ap.blockBox[inst.block], build: buildL1Block, label: inst => `LRAM block ${inst.block}`},
    row: {name: 'Row and read tree', short: 'Row', parent: 'lram', def: 'latch', tw: 720, target: ap => ap.rowBox, build: buildL1Row, label: inst => `row ${inst.row}`},
    latch: {name: 'Latch cell', short: 'Latch', parent: 'row', def: null, tw: 64, target: ap => ap.latchBox, build: buildL1Latch},
    cmp: {name: 'Tag comparator', short: 'Compare', parent: 'dcache', def: null, tw: 150, target: ap => ap.cmpBox, build: buildL1Cmp},
  },
};
const L1P = SCENES.l1.parts = {
  overview: () => ({kick: 'Level 1 · key 1', title: 'The L1 data cache', badge: [['documented', 'structure, rail, timing'], ['generic', 'the latch circuit'], ['unknown', 'the silicon cell']],
    what: `Each minion has a private ${n('l1_kb')} data cache (${n('l1_geom')}). It is <b>not SRAM</b>: the data array is ${n('l1_blocks')} latch-RAM (LRAM) blocks of ${n('l1_rows')} × ${n('l1_rowbits')}, the tags are latch register files and the valid and LRU bits are flip-flops. It runs on the minion rail at ${n('l1_v')}, below the voltage the shire cache's SRAM panels are specified for, and ${src('the documents never say why; our reading is that SRAM cannot sit in the minion\'s low-voltage region', 'l1:l1.why-latch l1:l1.lv-region')}. A hit takes ${n('l1_lat')} and costs about ${n('l1_e')} per 32-byte vector load; the chip reads ${n('l1_bw')} from its L1s.`,
    kpis: [K('l1_kb', 'per minion'), K('l1_lat', 'a hit, three cards'), kpi(n('l1_e'), 'per 32 B load, above idle'), K('l1_v', 'minion rail at 600 MHz')],
    extra: ladderHtml('l1')}),
  rail: () => ({kick: 'L1 · power', title: 'The minion rail (LV)', badge: [['documented', 'measured']],
    what: `The L1's latches switch on the minion rail, ${n('l1_v')} at 600 MHz. An L1-hit loop puts ${n('l1_rail')} of its power over idle on this rail and only ${n('l1_rail_sram')} on the SRAM rail. The neighbourhood document puts the minions in a low-voltage region and says that ${src('"the memory cells used to implement the ICache data RAMs need to be placed in an HV region"', 'l1:l1.lv-region')}; that the same holds for the shire cache's SRAM panels is our inference (asked). The minion's sleep and isolation ports are unused, so the arrays are always powered.`,
    kpis: [K('l1_v', 'minion rail, 600 MHz'), K('l1_rail', 'of an L1 hit on it')]}),
  pipeline: () => ({kick: 'L1 · minion', title: 'The DCache pipeline', badge: [['documented', 'spec']],
    what: `${n('l1_stages')} DCache stages locked to the integer pipeline: ID (bids), EX (address), TAG = S1 (TLB, tags, compare, the data row's address), MEM = S2 (the data read), WB = S3 (align, return), then S4 (the write port) and S5 (store bypass). Six bidders compete for S0 (${n('l1_s0')}); the core is the lowest. A dependent load issues ${n('l1_lat5')} cycles after the previous one; the measured ${n('l1_lat')} adds the loop's overhead.`,
    kpis: [K('l1_lat', 'load to use, measured'), K('l1_ns', 'at 600 MHz')]}),
  dcache: () => ({kick: 'L1 · minion', title: 'The L1 data cache', badge: [['documented', 'spec'], ['unknown', 'parity on silicon']],
    what: `${n('l1_geom')}, write-back and write-allocate, not coherent. Tags first: the ${n('l1_cmp')} comparators find the way in S1, then S2 reads only that way's row. The metadata is ${n('l1_meta64')} of ${n('l1_entry')} (a ${n('l1_tagbits')} tag and a 2-bit state) in four latch register files. Every store is a read-modify-write. No parity or ECC appears in the open RTL.`,
    kpis: [K('l1_kb', 'per minion'), K('l1_bits', 'of latch RAM'), K('l1_lat', 'a hit')], act: `<button type="button" class="st-btn" data-act="zoom" data-to="dcache">Zoom into the data cache</button>`}),
  tlb: () => ({kick: 'L1 · minion', title: 'TLB', badge: [['documented', 'spec']], what: `An ${n('l1_tlb')} latch register file that translates in S1 (4 KB, 2 MB and 1 GB pages). The neighbourhood document notes that virtual memory is unused in A0; the kernels here use physical addresses.`}),
  mh: () => ({kick: 'L1 · minion', title: 'Miss handlers', badge: [['documented', 'spec']], what: `${n('l1_mh')} per minion: at most two cacheable line misses outstanding; a second access to a line already being filled joins its handler. A missing load parks in the replay queue while its line comes from the L2: ${n('l1_miss_l2')} cycles from the L2, ${n('l1_miss_rb')} from its read buffer, and hart 1 pays 3 more.`,
    kpis: [K('l1_miss_l2', 'cycles from the L2'), K('l1_miss_rb', 'from its read buffer')]}),
  rq: () => ({kick: 'L1 · minion', title: 'Replay queue', badge: [['documented', 'spec']], what: `A queue of ${n('l1_rq')}, pre-allocated at ID. An instruction that misses or is rejected waits here and re-enters the pipeline; when it is full the core stalls.`}),
  vpu: () => ({kick: 'L1 · minion', title: 'The vector unit\'s port', badge: [['documented', 'spec']], what: `The array feeds one ${n('l1_vpu')} register row of all 8 lanes a cycle. The VPU also reads the scratchpad sets directly: its request pre-empts S1, skips the TLB and the tags, and gets 256 bits ${n('l1_vpu_lat')} cycles later.`}),
  tl: () => ({kick: 'L1 · minion', title: 'TensorLoad', badge: [['documented', 'spec and measured']], what: `TensorLoad (TL0) writes L2 or scratchpad responses straight into the L1's scratchpad rows through the write port, ${n('l1_tl4')} in flight; TL1 fills a VPU buffer instead. One minion loads ${n('l1_tl16')} in ${n('l1_tl')} from the L2, ${n('l1_tlrate')} per line.`,
    kpis: [K('l1_tl', 'for 16 lines, three cards')]}),
  ports: () => ({kick: 'L1 · minion', title: 'Fill, evict and miss ports', badge: [['documented', 'spec']], what: `Misses leave on the miss interface, evictions and stores to the shire on the 256-bit evict interface; fills come back through the neighbourhood's Fill FIFO in two 256-bit beats. Past the minion, the neighbourhood's bank FIFOs are VC FIFOs with level shifters: the edge between the minion rail and the Shire Channel. The L2 tab follows the request from there.`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="l2">The L2 (key 2) →</button>`}),
  nbr: () => Object.assign(L1P.ports(), {facts: 'ports'}),
  tags: ctx => ({kick: 'L1 · data cache', title: `Tag register file, way ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']], what: `${n('l1_rf16')}, one per set, of ${n('l1_entry')}: the ${n('l1_tagbits')} tag PA[39:7] and a 2-bit state (invalid, shared never used, exclusive, modified). A latch register file: all four ways read the set in the same cycle, with no read latency.`}),
  valid: () => ({kick: 'L1 · data cache', title: 'Valid bits', badge: [['documented', 'spec'], ['generic', 'the flip-flop']], what: `64 valid bits (16 sets × 4 ways) in flip-flops, ${n('g_ff_t')} each (textbook).`}),
  lru: () => ({kick: 'L1 · data cache', title: 'LRU', badge: [['documented', 'spec']], what: `${n('l1_lru')}, a ${n('l1_lru44')}, in flip-flops, updated in S2 on every cacheable access. Locked ways are never victims.`}),
  cmp: () => ({kick: 'L1 · data cache', title: 'Tag comparators', badge: [['documented', 'four, 33 bits'], ['generic', 'the circuit']], what: `${n('l1_cmp')} comparators, one per way, each ${n('g_cmp33')} of XNOR into an AND tree; all four run on every access, hit or miss, and the one-hot hit becomes the way that addresses the data row.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="cmp">Zoom into a comparator</button>`}),
  hit: () => Object.assign(L1P.cmp(), {facts: 'cmp'}),
  pma: () => ({kick: 'L1 · data cache', title: 'PMA check', badge: [['documented', 'spec']], what: 'The physical memory attributes decide whether the access is cacheable, in S1, beside the tag compare.', facts: 'pipeline'}),
  s4arb: () => ({kick: 'L1 · data cache', title: 'The write port', badge: [['documented', 'spec']], what: `One write port per block with ${n('l1_s4')} clients in a static priority: stores, fills from the SEND port, L2 fills from the miss handlers, TensorLoad, configuration clear, cache-op clear, debug. A fill writes only when no store holds the port.`}),
  blocks: ctx => ({kick: 'L1 · data cache', title: `LRAM block ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'structure'], ['unknown', 'the macro inside']],
    what: `${n('l1_rows')} × ${n('l1_rowbits')} as two ${n('l1_macro')} one-read-one-write macros with their own enables (${n('l1_macros')} per minion). A block holds bytes PA[4:3] of every half-line; one row across the four blocks is ${n('l1_half')}. A scalar load enables one block, a 32-byte vector load all four.`,
    act: ctx.i != null ? `<button type="button" class="st-btn" data-act="zoom" data-to="lram" data-block="${ctx.i}">Zoom into block ${ctx.i}</button>` : ''}),
  setmap: () => ({kick: 'L1 · data cache', title: 'How the firmware uses the 16 sets', badge: [['documented', 'spec and measured']],
    what: `Before every launch the firmware sets split and scratchpad mode: sets 0–11 become a ${n('l1_scp_kb')} tensor scratchpad (hart 0's TensorLoad target), ${n('l1_h0sets')} and ${n('l1_h1sets')}: ${n('l1_hart')} of cache per hart, so the issuing hart, not an address bit, picks its pair of sets (the DCache description says only that the two set MSBs are forced to 11; the page follows the PRM). The knee confirms it on three cards: hart 1 reads ${n('l1_knee_in')} and ${n('l1_knee_out')} (a miss to the read buffer).`}),
  lram: () => ({kick: 'L1 · LRAM block', title: 'The LRAM macro', badge: [['documented', 'structure'], ['derived', 'the latch-RF pattern, assumed'], ['unknown', 'the silicon macro']],
    what: `The open release has only a behavioural model of the macro (synchronous write, synchronous read). ET's latch register-file library, which the open RTL uses for the tag files, has this mechanism, and Ainekko's re-implementation maps the LRAM onto it; the page assumes it for the LRAM: write data captured by a low-phase latch, a decoded write address enabling one row's clock gate, that row's latches transparent while its gated clock is high; the read address registered, then a combinational select, with no bitline and no sense amplifier in the model. Whether the silicon macro is this library cell for cell is asked.`}),
  wdec: () => ({kick: 'L1 · LRAM block', title: 'Write decoder and row clock gates', badge: [['derived', 'the ET latch-RF pattern, assumed for the LRAM'], ['documented', 'the clock-gate cells'], ['generic', 'the gate\'s circuit']], what: 'In the ET latch-RF pattern (assumed for the LRAM; the silicon macro is asked), the 7-bit write address is decoded to one of 128 per-row clock gates (standard cells HDBULT08_CKGTPLT when the ASIC switch is on); only that row\'s latches see a clock edge.'}),
  icg: () => Object.assign(L1P.wdec(), {facts: 'wdec'}),
  wlatch: () => ({kick: 'L1 · LRAM block', title: 'Write-data latch', badge: [['derived', 'the ET latch-RF pattern, assumed for the LRAM']], what: 'In the ET latch-RF pattern (assumed for the LRAM; the silicon macro is asked), a latch captures the write data on the low phase (a negative clock gate, HDBULT08_CKGTNLT) half a cycle before the write, and holds it steady while the row\'s latches are transparent.'}),
  rdreg: () => ({kick: 'L1 · LRAM block', title: 'Registered read address', badge: [['derived', 'the ET latch-RF pattern, assumed for the LRAM'], ['documented', 'a synchronous read'], ['generic', 'the select']], what: 'The behavioural model documents a synchronous read. In the ET latch-RF pattern (assumed for the LRAM; the silicon macro is asked), the read address is registered on the rising edge, the read is then a combinational select of the row, rf[rd_addr_reg], and the 64-bit output is registered for S3.'}),
  rsel: () => Object.assign(L1P.muxtree(), {facts: 'muxtree'}),
  oreg: () => Object.assign(L1P.rdreg(), {facts: 'rdreg'}),
  rows: () => ({kick: 'L1 · LRAM block', title: 'The rows', badge: [['documented', 'the row address'], ['unknown', 'the cell']], what: `${n('l1_rows')} of ${n('l1_rowbits')}; the row address is {set, PA[5], way}, ${n('l1_rowaddr')}. A 64-byte line is two rows; the four ways of a half-line sit in four adjacent rows.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="row">Zoom into the row</button>`}),
  row: () => ({kick: 'L1 · row', title: 'One row', badge: [['generic', 'the circuit'], ['documented', 'the counts']], what: `${n('l1_rowbits')} of latches on one gated clock: a write turns them all transparent at once and they take the write bus; a read never touches them, it only selects their outputs.`}),
  latchbit: () => ({kick: 'L1 · row', title: 'Latch 5', badge: [['generic', 'the circuit']], what: 'The bit whose read tree is drawn. Enter or a second click zooms into its transistors.', facts: 'row',
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="latch">Zoom into its transistors</button>`}),
  muxtree: () => ({kick: 'L1 · row', title: 'The read tree of one bit', badge: [['generic', 'textbook'], ['documented', 'the pattern']], what: `A ${n('g_mux')}: seven levels of 2:1 muxes, each level switched by one bit of the registered row address. Only the nodes whose value changes spend energy, so a latch array's read energy depends on the data (textbook). No wordline, no bitline precharge, no sense amplifier, if the silicon macro is the latch pattern: that is asked.`}),
  tg1: () => L1P.latch(), tg2: () => L1P.latch(), inv1: () => L1P.latch(), inv2: () => L1P.latch(), ckinv: () => L1P.latch(),
  latch: () => ({facts: 'latch', kick: 'L1 · latch cell', title: 'A transmission-gate D latch', badge: [['generic', 'textbook'], ['unknown', 'the silicon cell']],
    what: `A static CMOS latch: two cross-coupled inverters with a clocked feedback path, ${n('g_latch_t')} (textbook). While the row's gated clock is high the input gate passes D and the node follows; when it falls the feedback gate closes the loop and the bit holds, full swing, with no precharge, no sense amplifier and no refresh. At that count the L1's ${n('l1_bits')} hold ${n('l1_tr')} storage transistors per minion (an estimate). Which cell the silicon macro uses is asked.`}),
  sram6t: () => ({kick: 'L1 · for contrast', title: 'A 6T SRAM cell', badge: [['generic', 'textbook']], what: `Two cross-coupled inverters and two access NMOS on a bitline pair: ${n('g_6t')} transistors a bit. A read needs precharged bitlines and a sense amplifier, and the cell needs a minimum voltage for read stability and writability, which is why SRAM usually gets its own higher rail. The documents call the shire cache's panels SRAM, and the neighbourhood's instruction-cache data RAM is a macro of the same family (${src('saduls, 1PUHD', 'l1:l1.icache-sram')}); the bitcell inside either is not documented (asked). The L1 is latch RAM.`}),
  xnors: () => Object.assign(L1P.cmp(), {facts: 'cmp'}), andtree: () => Object.assign(L1P.cmp(), {facts: 'cmp'}), ways: () => Object.assign(L1P.cmp(), {facts: 'cmp'}),
  energy: () => ({kick: 'L1 · energy', title: 'What an L1 access costs', badge: [['documented', 'measured, three cards'], ['unknown', 'the split']],
    what: `A 32-byte vector load that hits costs ${n('l1_e')} (${n('l1_e_pjb')}) on random data and ${n('l1_e0')} on zeros, the instruction included; a scalar flw ${n('l1_flw')}, an fsw ${n('l1_fsw')}, a 32-byte store ${n('l1_vst')}: a store costs ${n('l1_ratio')} a load, as a read-modify-write would. Filling a line from the own scratchpad costs ${n('l1_fill')} (${n('l1_fill0')} on zeros). How a load's energy splits between the array, the tags and the pipeline is asked.`}),
};

/* ---- the L1's accesses: each step plays at one scale (where) and, with Dive on, goes down to its circuit (dive) ---- */
const INS = () => SC().inst;
const stageRing = (c, nm) => { lit(c, 'pipeline', {noRing: true}); return ringAround(c.fx, c.ap.stage[nm].box, {fo: 0.22}); };
const slotOn = (c, r) => { const b = r.getBBox ? {x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height')} : null; if (b) S(E('rect', {x: b.x, y: b.y, width: b.w, height: b.h, rx: 3}, c.fx), {fill: 'var(--c2)', fillOpacity: 0.8}); };
async function stageHop(tok, c, from, to, ms) {
  const pk = packet(c.fx, 'var(--c2)', 11); at(pk, c.ap.stage[from]);
  await travel(tok, c.fx, pk, [c.ap.stage[from], c.ap.stage[to]], ms || 700);
  return pk;
}
/* the four way register files read the set, the comparators run, one way (or none) hits */
async function tagLookup(tok, c, hitWay) {
  lit(c, 'tags', {noRing: true});
  await Promise.all(c.ap.setY.map(s => sweep(tok, c, [{x: s.x1, y: s.y}, {x: s.x2, y: s.y}], {ms: 500, w: 4})));
  alive(tok);
  lit(c, 'cmp');
  c.ap.eq.forEach((p, k) => fadeIn(T(c.fx, p.x + 24, p.y + 6, k === hitWay ? 'hit' : 'no', k === hitWay ? 't-smb halo' : 't-sm halo')));
  await wait(tok, 450);
}
const rowCells = (c, r, cls) => { (c.ap.cellsOf[r] || []).forEach(e => { e.classList.add(cls || 'on'); TOUCH.add(e); }); };
function rowSweep(tok, c, r, o) {
  const y = c.ap.rowYs[r] + 20;
  ringAround(c.fx, {x: 66, y: c.ap.rowYs[r] + 2, w: 728, h: 36}, {fo: 0.05, sw: 4});
  rowCells(c, r, (o && o.cls) || 'on');
  return sweep(tok, c, [{x: 66, y}, {x: 800, y}], {ms: (o && o.ms) || 600, w: 4, under: true});
}
async function treeRead(tok, c) {
  lit(c, 'muxtree', {noRing: true});
  await sweep(tok, c, c.ap.treePath, {ms: 1600, w: 5, label: 'bit 5 selected', at: c.ap.treePath[c.ap.treePath.length - 1], dx: -60, dy: -36});
  lit(c, 'latchbit');
}
async function rowWrite(tok, c, wholeRow) {
  lit(c, 'icg');
  await sweep(tok, c, [{x: -80, y: 38}, {x: 1070, y: 38}], {ms: 700, w: 5, label: 'GCLK pulses', at: {x: 760, y: 38}, dy: -8});
  lit(c, 'row', {noRing: true});
  c.ap.lat.forEach(l => ringAround(c.fx, l, {fo: 0.25, sw: 3}));
  fadeIn(T(c.fx, 500, 190, wholeRow ? 'all 64 latches of the row take the bus' : 'the row\'s latches are transparent: they take the bus', 't-smb halo', 'middle'));
  await wave(tok, c, c.ap.wave, [
    {name: 'CK', pts: [[0, 0], [0.15, 1], [0.45, 0], [0.65, 1], [0.95, 0]], col: 'var(--ink-2)'},
    {name: 'EN', pts: [[0, 0], [0.1, 1], [0.5, 0]], col: 'var(--c1)'},
    {name: 'GCLK', pts: [[0, 0], [0.15, 1], [0.45, 0]], col: 'var(--c2)'},
    {name: 'Q', pts: [[0, 0], [0.2, 1]]},
  ], {generic: true, ms: 1400, lw: 76});
}
const L1A = SCENES.l1.access = {};
const stepF = (k, i) => `l1:l1.seq.${k}.${i}`;
L1A['load-hit'] = {
  led: [0, 1, 2, 3, 4, 5].map(i => [src(String(i), stepF('load-hit', i + 1)), null]),
  tot: () => ({c: `${n('l1_lat')} measured`, e: `${n('l1_e')} per 32 B load`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `An L1 hit: ${n('l1_lat5')} cycles issue to issue by the documented pipeline, ${n('l1_lat')} measured on three cards; about ${n('l1_e')} per 32-byte load.`,
  steps: [
    {name: 'ID', where: 'minion', say: () => `ID: the load bids for the data cache, the lowest of ${n('l1_s0')} bidders, and a replay-queue entry is kept for it`,
      run: async (tok, c) => {
        stageRing(c, 'ID'); lit(c, 'rq'); slotOn(c, c.ap.rqSlots[0]);
        counter(c, 'cycle 0 · ID', 'the documented pipeline');
        const pk = packet(c.fx, 'var(--c2)', 11); at(pk, c.ap.stage.ID);
        await pulse(tok, c.fx, c.ap.stage.ID, 1000);
      }},
    {name: 'EX', where: 'minion', say: () => 'EX: the adder forms the virtual address from the base register and the offset',
      run: async (tok, c) => {
        stageRing(c, 'EX'); counter(c, 'cycle 1 · EX', 'the documented pipeline');
        await stageHop(tok, c, 'ID', 'EX');
        sayAt(c, c.ap.stage.EX.x, c.ap.stage.EX.y + 34, ['EX: base + offset', 'the virtual address'], {side: 'd'});
      }},
    {name: 'TAG (S1)', where: 'dcache', dive: ['cmp'], say: () => `TAG: the four way register files read set ${INS().set}; the ${n('l1_cmp')} comparators run and way ${INS().way} hits`,
      run: async (tok, c) => {
        counter(c, 'cycle 2 · TAG (S1)', 'the documented pipeline');
        await tagLookup(tok, c, INS().way);
        lit(c, 'hit'); lit(c, 'blocks', {i: INS().block});
        const bb = c.ap.blockBox[INS().block];
        sayAt(c, 850, 498, [`way ${INS().way} hits`, `row {${INS().set}, ${INS().half}, ${INS().way}} = ${INS().row}`, `block ${INS().block} enabled`], {tl: true});
        await sweep(tok, c, [{x: bb.x + bb.w / 2, y: bb.y + 70}, {x: bb.x + bb.w / 2, y: c.ap.rowY}], {ms: 400, w: 4});
      },
      deep: {cmp: async (tok, c) => {
        lit(c, 'xnors', {noRing: true});
        c.ap.xn.forEach(p => fadeIn(T(c.fx, p.x + 8, p.y - 10, '1', 't-net halo')));
        await wait(tok, 500);
        lit(c, 'andtree');
        await sweep(tok, c, c.ap.hitP, {ms: 700, label: 'hit2 = 1', at: {x: 700, y: 290}, dy: -14});
        lit(c, 'ways', {noRing: true});
        fadeIn(T(c.fx, 995, 330, 'way 2', 't-smb halo', 'middle'));
      }}},
    {name: 'MEM (S2)', where: 'lram', dive: ['row', 'latch'], say: () => `MEM: block ${INS().block} reads row ${INS().row}, ${n('l1_rowbits')}, through its row select; the other three blocks stay idle`,
      run: async (tok, c) => {
        counter(c, 'cycle 3 · MEM (S2)', 'the documented pipeline');
        lit(c, 'rdreg');
        await sweep(tok, c, [c.ap.rdreg, {x: c.ap.rdreg.x, y: 118}], {ms: 300, w: 4});
        await rowSweep(tok, c, INS().row);
        lit(c, 'rsel');
        await sweep(tok, c, [{x: 800, y: c.ap.rowYs[INS().row] + 20}, c.ap.rsel, {x: c.ap.oreg.x, y: 462}], {ms: 600, w: 5});
        lit(c, 'oreg');
        sayAt(c, 430, 612, [`row ${INS().row}: 64 bits out`, 'nothing precharged, no sense amplifier', '(if the macro is the latch pattern)'], {tl: true, col: 'var(--ink-2)'});
      },
      deep: {row: treeRead, latch: (tok, c) => latchHold(tok, c, {})}},
    {name: 'WB (S3)', where: 'minion', say: () => 'WB: the 8 bytes are aligned, sign-extended and written to the register file',
      run: async (tok, c) => {
        stageRing(c, 'WB'); counter(c, 'cycle 4 · WB (S3)', 'the documented pipeline');
        await stageHop(tok, c, 'MEM', 'WB');
        sayAt(c, c.ap.stage.WB.x, c.ap.stage.WB.y + 34, ['WB: align, sign-extend', 'write the register file'], {side: 'd'});
      }},
    {name: 'next ID', where: 'minion', say: () => `A dependent load can issue ${n('l1_lat5')} cycles after the first: measured ${n('l1_lat')} on three cards, about ${n('l1_e')} per 32-byte load`,
      run: async (tok, c) => {
        stageRing(c, 'ID'); counter(c, `${nt('l1_lat')} load to use`, 'measured, three cards');
        await stageHop(tok, c, 'WB', 'ID', 900);
        sayAt(c, c.ap.stage.ID.x, c.ap.stage.ID.y + 34, [`${nt('l1_lat')} measured`, `${nt('l1_e')} per 32 B load`], {side: 'd'});
      }},
  ]};
L1A['store-hit'] = {
  led: [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null]],
  tot: () => ({c: 'not measured apart', e: `${n('l1_vst')} per 32 B store`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `A store hit is a read-modify-write of the row: ${n('l1_vst')} per 32-byte store, ${n('l1_fsw')} per scalar fsw, ${n('l1_ratio')} a load.`,
  steps: [
    {name: 'ID–S1', where: 'dcache', say: () => `As a load: the tags are read and compared, way ${INS().way} hits; the store data is sent in S1`,
      run: async (tok, c) => { counter(c, 'ID → TAG (S1)', 'as a load'); await tagLookup(tok, c, INS().way); lit(c, 'blocks', {i: INS().block}); }},
    {name: 'S2 read', where: 'lram', say: () => `S2 reads row ${INS().row} first: every store is a read-modify-write of the array`,
      run: async (tok, c) => { counter(c, 'S2: read the row'); await rowSweep(tok, c, INS().row); lit(c, 'rsel'); sayAt(c, 430, 612, ['S2: read the row', 'the store will merge into it'], {tl: true}); }},
    {name: 'S3 merge', where: 'minion', say: () => 'S3 merges the new bytes into the row it read',
      run: async (tok, c) => { stageRing(c, 'WB'); counter(c, 'S3: merge'); await stageHop(tok, c, 'MEM', 'WB'); sayAt(c, c.ap.stage.WB.x, c.ap.stage.WB.y + 34, ['S3: merge the new bytes'], {side: 'd'}); }},
    {name: 'S4 write', where: 'lram', dive: ['row', 'latch'], say: () => `S4 writes: the decoded row's clock gate fires and its ${n('l1_rowbits')} of latches take the new value`,
      run: async (tok, c) => {
        counter(c, 'S4: the write port');
        lit(c, 'wlatch'); lit(c, 'wdec');
        await sweep(tok, c, [{x: -34, y: c.ap.rowYs[INS().row] + 20}, {x: 22, y: c.ap.rowYs[INS().row] + 20}], {ms: 400, w: 5, label: 'row gate fires', at: {x: 70, y: c.ap.rowYs[INS().row] + 54}, dx: 0, dy: 0});
        await rowSweep(tok, c, INS().row, {ms: 700});
        sayAt(c, 430, 612, [`S4: row ${INS().row} written`, 'its latches transparent while the gated clock is high'], {tl: true});
      },
      deep: {row: (tok, c) => rowWrite(tok, c, false), latch: latchWrite}},
    {name: 'Metadata', where: 'dcache', say: () => 'A first store to a clean line rewrites its state to modified: one 35-bit latch-RF write',
      run: async (tok, c) => { counter(c, 'S4: metadata'); lit(c, 'tags', {i: INS().way}); const s = c.ap.setY[INS().way]; await sweep(tok, c, [{x: s.x1, y: s.y}, {x: s.x2, y: s.y}], {ms: 500, label: 'modified', at: {x: s.x2, y: s.y}, dx: -90, dy: -12}); }},
    {name: 'S5 bypass', where: 'minion', say: () => `S5 keeps the store one more cycle for a younger load; ${n('l1_vst')} per 32-byte store, ${n('l1_ratio')} a load`,
      run: async (tok, c) => { stageRing(c, 'S5'); counter(c, `${nt('l1_vst')} per store`, 'measured, three cards'); await stageHop(tok, c, 'S4', 'S5'); sayAt(c, c.ap.stage.S5.x, c.ap.stage.S5.y + 34, [`${nt('l1_vst')} per 32 B store`, `${nt('l1_ratio')} a load`], {side: 'd'}); }},
  ]};
L1A.miss = {
  led: [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]],
  tot: () => ({c: `${n('l1_miss_l2')} from the L2, ${n('l1_miss_rb')} from its read buffer`, e: `${n('l1_fill')} to fill the line`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `A miss: a miss handler asks the L2, the load waits in the replay queue, the line is written as two rows, and the replay hits: ${n('l1_miss_l2')} cycles from the L2.`,
  steps: [
    {name: 'No way matches', where: 'dcache', say: () => 'No way matches: the LRU picks the victim way (locked ways excluded)',
      run: async (tok, c) => { counter(c, 'S1: miss'); await tagLookup(tok, c, -1); lit(c, 'lru'); sayAt(c, 245, 300, ['no way matches', 'the LRU picks a victim'], {side: 'd'}); }},
    {name: 'Miss handler', where: 'minion', say: () => `A miss handler (1 of ${n('l1_mh')}) takes the miss; the load parks in the replay queue and the core carries on`,
      run: async (tok, c) => {
        stageRing(c, 'MEM'); lit(c, ['mh', 'rq']);
        const pk = packet(c.fx, 'var(--c2)', 11); at(pk, c.ap.stage.MEM);
        await travel(tok, c.fx, pk, [c.ap.stage.MEM, {x: c.ap.stage.MEM.x, y: 318}, c.ap.mh], 800);
        slotOn(c, c.ap.rqSlots[0]);
        sayAt(c, 588, 318, ['a miss handler takes it', 'the load waits in the replay queue'], {side: 'l'});
      }},
    {name: 'Victim out', where: 'dcache', say: () => 'If the victim is dirty, the write-back unit reads its two rows, 256 bits a cycle, and sends 512 bits to the L2',
      run: async (tok, c) => { lit(c, 'blocks'); counter(c, 'two reads of 256 bits'); sayAt(c, 400, 600, ['a dirty victim: two full-row reads', 'across all four blocks, then out'], {side: 'u'}); await wait(tok, 600); }},
    {name: 'Fill request', where: 'minion', handoff: {lv: 'l2', k: 'load-hit', at: 1, label: 'Continue at the L2'}, say: () => 'The fill request leaves for the L2 bank that PA[7:6] picks: the L2 tab follows it',
      run: async (tok, c) => {
        lit(c, ['mh', 'ports', 'nbr']);
        const pk = packet(c.fx, 'var(--c2)', 12); at(pk, c.ap.mh);
        await travel(tok, c.fx, pk, [c.ap.mh, {x: 663, y: 595}, c.ap.port, {x: 935, y: 595}], 1300);
        sayAt(c, 935, 600, ['to the L2', 'continue at the L2 (key 2)'], {side: 'u'});
      }},
    {name: 'Fill writes', where: 'lram', dive: ['row'], say: () => 'The 512-bit fill writes the line\'s two rows in all four blocks: 8 row clock gates, 512 latches',
      run: async (tok, c) => {
        counter(c, 'the fill: two rows', 'in all four blocks');
        lit(c, 'wdec');
        const r0 = INS().row & ~4;
        await Promise.all([rowSweep(tok, c, r0), rowSweep(tok, c, r0 + 4)]);
        sayAt(c, 430, 612, [`rows ${r0} and ${r0 + 4} written`, 'here and in the other three blocks'], {tl: true});
      },
      deep: {row: (tok, c) => rowWrite(tok, c, true)}},
    {name: 'Metadata', where: 'dcache', say: () => 'The miss handler writes the new tag and state (exclusive for a load) and sets the valid bit',
      run: async (tok, c) => { lit(c, ['valid']); lit(c, 'tags', {i: INS().way}); const s = c.ap.setY[INS().way]; await sweep(tok, c, [{x: s.x1, y: s.y}, {x: s.x2, y: s.y}], {ms: 500, label: 'new tag', at: {x: s.x2, y: s.y}, dx: -90, dy: -12}); }},
    {name: 'Replay hits', where: 'minion', say: () => `The waiting load re-enters and hits: ${n('l1_miss_l2')} cycles load to use from the L2, ${n('l1_miss_rb')} from its read buffer`,
      run: async (tok, c) => {
        lit(c, 'rq'); stageRing(c, 'WB'); counter(c, `${nt('l1_miss_l2')} cycles from the L2`, 'measured, three cards');
        const pk = packet(c.fx, 'var(--c2)', 11); at(pk, c.ap.rq);
        await travel(tok, c.fx, pk, [c.ap.rq, {x: 663, y: 130}, c.ap.stage.ID, c.ap.stage.EX, c.ap.stage.TAG, c.ap.stage.MEM, c.ap.stage.WB], 1600);
      }},
  ]};
L1A['scp-read'] = {
  led: [[null, null], [null, null], [src(nt('l1_vpu_lat') + ' after S1', nf('l1_vpu_lat')), null]],
  tot: () => ({c: `${n('l1_vpu_lat')} cycles after the request`, e: 'not measured apart'}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `The VPU reads the L1's scratchpad sets directly: no TLB, no tags, 256 bits ${n('l1_vpu_lat')} cycles later.`,
  steps: [
    {name: 'VPU request', where: 'minion', say: () => 'The VPU\'s scratchpad read pre-empts S1: no TLB and no tag check',
      run: async (tok, c) => { lit(c, 'vpu'); stageRing(c, 'TAG'); const pk = packet(c.fx, 'var(--c7)', 11); at(pk, c.ap.vpu); await travel(tok, c.fx, pk, [c.ap.vpu, {x: 34, y: 130}, c.ap.stage.TAG], 900); }},
    {name: 'Four blocks', where: 'dcache', say: () => 'All four blocks read one 256-bit row of the scratchpad sets (0–11)',
      run: async (tok, c) => { lit(c, 'blocks'); lit(c, 'setmap'); for (let s = 0; s < 12; s++) ringAround(c.fx, {x: -140 + s * 60, y: 602, w: 52, h: 40}, {sw: 2, fo: 0.2}); await wait(tok, 600); }},
    {name: 'To the VPU', where: 'minion', say: () => `The 256 bits reach the VPU ${n('l1_vpu_lat')} cycles after the request (one extra register stage)`,
      run: async (tok, c) => { lit(c, 'vpu'); counter(c, `${nt('l1_vpu_lat')} cycles`, 'spec'); const pk = packet(c.fx, 'var(--c7)', 12); at(pk, c.ap.dc); await travel(tok, c.fx, pk, [c.ap.dc, c.ap.vpu], 900); }},
  ]};
L1A.tensorload = {
  led: [[null, null], [null, null], [null, null]],
  tot: () => ({c: `${n('l1_tl')} for ${n('l1_tl16')}`, e: 'in the scratchpad level'}), ask: {c: 'ask-cache-latency'},
  cap: () => `TensorLoad fills the L1's scratchpad rows from the L2 or the scratchpad, ${n('l1_tl4')} in flight: ${n('l1_tl')} for ${n('l1_tl16')}.`,
  steps: [
    {name: 'Start', where: 'minion', say: () => 'A tensor_load CSR write starts the TL0 state machine; each line\'s address goes through S0 and S1 for the TLB and PMA',
      run: async (tok, c) => { lit(c, 'tl'); stageRing(c, 'TAG'); const pk = packet(c.fx, 'var(--c7)', 11); at(pk, c.ap.tl); await travel(tok, c.fx, pk, [c.ap.tl, {x: 394, y: 130}, c.ap.stage.TAG], 900); }},
    {name: 'In flight', where: 'minion', say: () => `The state machine keeps ${n('l1_tl4')} in flight to the L2 or the scratchpad`,
      run: async (tok, c) => {
        lit(c, ['tl', 'ports', 'nbr']);
        await Promise.all([0, 1, 2, 3].map(async i => { await wait(tok, i * 220); const pk = packet(c.fx, 'var(--c7)', 9); at(pk, c.ap.tl); await travel(tok, c.fx, pk, [c.ap.tl, {x: 520, y: 595}, c.ap.port, {x: 935, y: 595}], 1100); }));
      }},
    {name: 'Rows written', where: 'dcache', handoff: {lv: 'scp', k: 'own-load', label: 'The source: the scratchpad (key 4)'}, say: () => `Each 512-bit response is written as two scratchpad rows through the write port: ${n('l1_tl')} for ${n('l1_tl16')}, ${n('l1_tlrate')} per line`,
      run: async (tok, c) => { lit(c, ['s4arb', 'blocks', 'setmap']); counter(c, `${nt('l1_tl')} for 16 lines`, 'measured, three cards'); for (let s = 0; s < 12; s++) ringAround(c.fx, {x: -140 + s * 60, y: 602, w: 52, h: 40}, {sw: 2, fo: 0.2}); await wait(tok, 700); }},
  ]};
L1A.refresh = {
  led: [[null, null]], tot: () => ({c: 'none', e: 'leakage only'}),
  cap: () => 'Refresh? None: latches, like SRAM, hold their value while the rail is up.',
  steps: [
    {name: 'No refresh', where: 'latch', say: () => 'Nothing to do: the latches hold their value while the minion rail is up, so the L1 has no refresh (the DRAM does)',
      run: async (tok, c) => { counter(c, 'no refresh', 'static storage'); await latchHold(tok, c, {hold: true}); }},
  ]};
SCENES.l1.accOrder = [['load-hit', 'Load hit', 'Load'], ['store-hit', 'Store hit', 'Store'], ['miss', 'Miss → L2', 'Miss'], ['scp-read', 'VPU scratchpad read', 'VPU read'], ['tensorload', 'TensorLoad', 'TLoad'], ['refresh', 'Refresh?', 'Refresh?']];
SCENES.l1.tour = [
  {name: 'The minion', path: ['minion'], panel: 'rail', hi: ['rail', 'dcache'],
    cap: () => `The L1 sits inside each minion, on the minion rail: ${n('l1_v')}, and ${n('l1_rail')} of an L1 hit's power`,
    sub: () => 'A logical drawing: the minion\'s floorplan is not published (asked).'},
  {name: 'The data cache', path: ['minion', 'dcache'], panel: 'setmap', hi: ['setmap', 'blocks'],
    cap: () => `${n('l1_geom')}; the firmware leaves each hart ${n('l1_hart')} and makes ${n('l1_scp_kb')} a tensor scratchpad`,
    sub: () => `The knee confirms it: hart 1 reads ${n('l1_knee_in')} and ${n('l1_knee_out')}, past it.`},
  {access: 'load-hit'},
  {name: 'The LRAM block', path: ['minion', 'dcache', 'lram'], panel: 'lram', hi: ['icg', 'rsel', 'rows'],
    cap: () => 'Latch RAM: a per-row clock gate for the write, a mux-tree select for the read (ET\'s latch register-file pattern, assumed for the LRAM)',
    sub: () => 'What is inside the silicon macro is not in the open release: asked.'},
  {name: 'The latch cell', path: ['minion', 'dcache', 'lram', 'row', 'latch'], panel: 'latch', hi: ['tg1', 'inv1', 'inv2', 'tg2', 'sram6t'], dive: true, play: latchWrite,
    cap: () => `One bit: a latch of about ${n('g_latch_t')}, against ${n('g_6t')} for an SRAM cell; no precharge, no sense amplifier`,
    sub: () => 'Why latches: the neighbourhood document puts its ICache\'s memory cells in the high-voltage region; that the minion\'s low-voltage region rules out SRAM panels is our reading (asked).'},
  {access: 'store-hit'},
  {access: 'miss'},
  {name: 'What is asked', path: ['minion'], panel: 'overview', hi: ['dcache', 'rail'],
    cap: () => 'Unknown and asked: the silicon cell, why latches, the per-stage cycles, the energy split, parity, the floorplan',
    sub: () => 'Each dashed part and each "not split" cell names its ask; the list is under the diagram.'},
];

/* ================= L2 (key 2, #l2): 512 KB of the shire cache ================= */
function buildL2Shire(L, ap, inst) {
  frame(L, {title: 'Shire · the L2 is 512 KB of the shire cache', sub: '4 neighbourhoods of 8 minions over 4 banks · a logical drawing, not a floorplan',
    tags: [['unknown', '? floorplan · asked'], ['documented', 'documented']]});
  railBand(L, -150, 12, 1228, 244, 'pat-lv', 'The minions\' low-voltage region', 'lvband');
  railBand(L, -150, 262, 1228, 428, 'pat-hv', 'The Shire Channel, on the shire clock', 'rail');
  S(E('line', {x1: -150, y1: 259, x2: 1078, y2: 259}, L), {stroke: 'var(--ink-2)', strokeWidth: 2, strokeDasharray: '10 8'});
  T(L, 1066, 206, 'LV', 't-labb halo', 'end', 'l2:l2.domain'); T(L, 1066, 228, 'minion rail', 't-sm halo', 'end', nf('l1_v')); T(L, 1066, 248, nt('l1_v'), 't-sm halo', 'end', nf('l1_v'));
  T(L, 1066, 284, 'HV', 't-labb halo', 'end', 'l2:l2.domain'); T(L, 1066, 304, 'Shire Channel (rail asked)', 't-sm halo', 'end', 'l2:l2.domain l2:l2.rail.hv-logic');
  ap.min = []; ap.fifo = []; ap.arb = [];
  for (let k = 0; k < 4; k++) {
    const x = -136 + k * 276, w = 266;
    const g = part(L, 'nbr', x, 22, w, 206, COL.logic, `neighbourhood ${k}`, {ctx: {i: k}, fo: 0.05});
    ap.min[k] = [];
    for (let m = 0; m < 8; m++) {
      const mx = x + 12 + (m % 4) * 62, my = 42 + Math.floor(m / 4) * 44;
      S(E('rect', {x: mx, y: my + 12, width: 56, height: 34, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.2, stroke: 'var(--c1)', strokeWidth: 1.25});
      T(g, mx + 28, my + 35, 'M' + m, 't-sm', 'middle');
      ap.min[k].push({x: mx + 28, y: my + 29});
    }
    S(E('rect', {x: x + 12, y: 146, width: w - 24, height: 34, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.1, stroke: 'var(--c1)', strokeWidth: 1.25});
    T(g, x + w / 2, 169, 'arbiters · pre-process', 't-sm', 'middle', 'l2:l2.path.nbr-request');
    ap.arb[k] = {x: x + w / 2, y: 140};
    // the bank FIFOs: VC FIFOs across the LV/HV edge (four banks and the UC)
    const gf = part(L, 'fifo', x + 12, 204, w - 24, 72, COL.xing, '', {ctx: {i: k}, child: k === 0 ? 'xing' : null, cur: k === 0, fo: 0.08, label: `Neighbourhood ${k}'s bank FIFOs: VC FIFOs with level shifters`});
    ap.fifo[k] = [];
    ['0', '1', '2', '3', 'UC'].forEach((b, i) => {
      const fx0 = x + 20 + i * 47;
      S(E('rect', {x: fx0, y: 212, width: 40, height: 56, rx: 4, 'pointer-events': 'none'}, gf), {fill: 'var(--c5)', fillOpacity: 0.18, stroke: 'var(--c5)', strokeWidth: 1.25});
      T(gf, fx0 + 20, 246, b, 't-sm', 'middle');
      ap.fifo[k].push({x: fx0 + 20, y: 240});
    });
  }
  ap.xingBox = {x: -124, y: 204, w: 242, h: 72};
  part(L, 'reqxbar', -136, 318, 1204, 34, COL.net, 'request crossbar: 5 clients → 4 banks + UC, routed over the banks', {ty: 25, tcls: 't-sm', fo: 0.14});
  ap.bank = [];
  for (let b = 0; b < 4; b++) {
    const x = -136 + b * 252, w = 238;
    const g = part(L, 'banks', x, 362, w, 132, COL.store, `bank ${b}`, {ctx: {i: b, inst: {bank: b}}, child: 'bank', cur: b === inst.bank, fo: 0.08, sub: [`PA[7:6] = ${b}`]});
    for (let s = 0; s < 4; s++) S(E('rect', {x: x + 12 + s * 56, y: 424, width: 48, height: 58, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.18, stroke: 'var(--c3)', strokeWidth: 1.25});
    ap.bank[b] = {x: x + w / 2, y: 452, box: {x, y: 362, w, h: 132}};
  }
  part(L, 'uc', 872, 362, 196, 132, COL.aux, 'UC block', {sub: ['barriers, credits', 'atomics']});
  part(L, 'rspxbar', -136, 506, 1204, 34, COL.net, 'response crossbar: 4 banks + UC → 5 clients', {ty: 25, tcls: 't-sm', fo: 0.14});
  // one sub-bank's rows: scratchpad, L2 and L3 in the same RAMs (M0)
  const gp = comp(L, 'partition', {}, 'One sub-bank\'s 1,024 sets in mode M0: scratchpad, L2 and L3 are row ranges of the same RAMs');
  T(gp, -136, 574, 'one sub-bank\'s 1,024 sets (mode M0)', 't-smb halo');
  [['scratchpad · sets 0–639', 0, 640, 'var(--c7)'], ['L2 · 640–767', 640, 128, 'var(--c2)'], ['L3 · 768–1023', 768, 256, 'var(--c3)']].forEach(([t, s0, ns, col]) => {
    const x = -136 + s0 / 1024 * 820, w = ns / 1024 * 820, on = col === 'var(--c2)';
    S(E('rect', {x, y: 584, width: w - 3, height: 36, rx: 4}, gp), {fill: col, fillOpacity: on ? 0.45 : 0.2, stroke: col, strokeWidth: on ? 3 : 1.25});
    T(gp, x + 8, 608, t.split(' · ')[0], on ? 't-smb' : 't-sm', 'start', 'l2:l2.partition.rows');
    T(gp, x + 4, 640, t.split(' · ')[1], 't-sm', 'start', 'l2:l2.partition.rows');
  });
  T(gp, -136, 664, `${nt('l2_part')} per shire`, 't-sm halo', 'start', nf('l2_part'));
  gp._box = {x: -136, y: 584, w: 820, h: 40};
  part(L, 'meshstop', 710, 556, 358, 124, COL.net, 'to the mesh (to_l3)', {sub: [{t: `${nt('l2_link')} port, 4 lanes`, f: nf('l2_link')}, 'VC FIFO, 2-flop synchronisers', {t: '→ the L3 (key 3)', c: 't-smb'}]});
  T(L, -136, 686, `the SRAM arrays' rail: ${nt('l2_set705')} set point (${nt('l2_rail750')} in the power tree); the logic's rail is asked`, 't-sm halo', 'start', nf('l2_set705') + ' l2:l2.rail.hv-logic');
  ap.xbarY = 335; ap.rxbarY = 523; ap.mesh = {x: 1010, y: 590};   // the mesh stop's point: clear of its labels
}

const STG = ['ag', 'ad', 'rqa', 'tap', 'ta', 'ta0', 'ta1', 'te', 'tc', 'dap', 'da', 'da0', 'da1', 'de', 'dc'];
function buildL2Bank(L, ap, inst) {
  frame(L, {title: `Bank ${inst.bank} (PA[7:6]) · one of four`, sub: 'an independent L2 cache: its own request queue, pipeline and ports',
    tags: [['unknown', '? read-buffer storage, prefetcher · asked'], ['documented', 'documented']]});
  const gq = part(L, 'reqq', -150, 14, 400, 186, COL.logic, 'request queue', {sub: [{t: `${nt('l2_reqq')} · ${nt('l2_reqq21')} for the L3 (hatched)`, f: nf('l2_reqq')}]});
  ap.q = [];
  for (let i = 0; i < 64; i++) {
    const x = -138 + (i % 16) * 24, y = 88 + Math.floor(i / 16) * 26, l3 = i >= 43;
    ap.q.push(S(E('rect', {x, y, width: 20, height: 20, rx: 3, 'pointer-events': 'none'}, gq), {fill: l3 ? 'url(#pat-hatch)' : 'var(--c1)', fillOpacity: l3 ? 1 : 0.15, stroke: 'var(--c1)', strokeWidth: 1}));
  }
  part(L, 'arb', 266, 14, 200, 86, COL.logic, 'arbitration', {sub: ['per sub-bank, L3 first', 'busy ones masked']});
  part(L, 'order', 266, 114, 200, 86, COL.logic, 'ordering', {sub: ['per-address lists']});
  const gr = part(L, 'rbuf', 482, 14, 200, 186, COL.logic, 'read buffer', {sub: [{t: `${nt('l2_rbuf')} of clean data`, f: nf('l2_rbuf')}]});
  ap.rb = [];
  for (let i = 0; i < 8; i++) ap.rb.push(S(E('rect', {x: 494 + (i % 4) * 46, y: 90 + Math.floor(i / 4) * 34, width: 40, height: 26, rx: 3, 'pointer-events': 'none'}, gr), {fill: 'var(--c1)', fillOpacity: 0.15, stroke: 'var(--c1)', strokeWidth: 1}));
  T(gr, 494, 188, 'storage: unknown', 't-sm', 'start', 'l2:l2.rbuf.storage');
  part(L, 'dataq', 698, 14, 184, 186, COL.store, 'data queue', {sub: [{t: 'a line per entry', f: 'l2:l2.dataq'}, 'two-port RF']});
  part(L, 'cbuf', 898, 14, 180, 86, COL.logic, 'coalescing', {sub: [{t: nt('l2_cbuf'), f: nf('l2_cbuf')}]});
  part(L, 'atomic', 898, 114, 180, 86, COL.logic, 'atomic unit', {sub: ['read, op, write']});
  ap.sub = [];
  for (let s = 0; s < 4; s++) {
    const x = -150 + s * 212, w = 200;
    const g = part(L, 'subbanks', x, 222, w, 206, COL.store, `sub-bank ${s}`, {ctx: {i: s, inst: {sub: s}}, child: 'sub', cur: s === inst.sub, fo: 0.08, sub: [`PA[9:8] = ${s}`]});
    S(E('rect', {x: x + 12, y: 284, width: 36, height: 128, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 1.25});
    S(E('rect', {x: x + 52, y: 284, width: 24, height: 128, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 1.25});
    for (let p = 0; p < 4; p++) S(E('rect', {x: x + 84 + p * 28, y: 284, width: 24, height: 128, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.28, stroke: 'var(--c3)', strokeWidth: 1.25});
    ap.sub[s] = {x: x + w / 2, y: 330, box: {x, y: 222, w, h: 206}};
  }
  part(L, 'perfmon', 698, 222, 184, 94, COL.logic, 'perf monitor', {sub: ['3 counters,', 'M-mode only']});
  part(L, 'hpf', 698, 330, 184, 98, COL.logic, 'prefetcher?', {kind: 'unknown', sub: ['in the RTL; on', 'silicon: asked']});
  part(L, 'rspmux', 898, 222, 180, 206, COL.net, 'response', {sub: ['mux and', 'queues, one per', 'neighbourhood']});
  // the pipeline, 15 named stages (2-cycle RAMs)
  const gpp = comp(L, 'pipe', {}, 'The bank\'s pipeline: 15 named stages from the queue to data complete');
  T(gpp, -150, 470, `pipeline · ${nt('l2_stages')} named stages`, 't-labb', 'start', nf('l2_stages'));
  ap.stg = {};
  STG.forEach((s, i) => {
    const x = -150 + i * 82;
    S(E('rect', {x, y: 486, width: 74, height: 50, rx: 5}, gpp), {fill: i >= 3 && i <= 6 || i >= 9 && i <= 12 ? 'var(--c3)' : 'var(--c1)', fillOpacity: 0.14, stroke: i >= 3 && i <= 6 || i >= 9 && i <= 12 ? 'var(--c3)' : 'var(--c1)', strokeWidth: 1.5});
    T(gpp, x + 37, 517, s, 't-mono', 'middle', 'l2:l2.stages');
    ap.stg[s] = {x, y: 486, w: 74, h: 50};
  });
  [['tag and tag-state RAMs', 3, 6], ['data RAMs', 9, 12]].forEach(([t, a, b]) => { const x0 = -150 + a * 82, x1 = -150 + b * 82 + 74; wire(gpp, [[x0, 548], [x0, 556], [x1, 556], [x1, 548]], 'thin'); T(gpp, (x0 + x1) / 2, 576, t, 't-sm', 'middle'); });
  T(gpp, -150, 610, `2-cycle RAMs: a sub-bank takes a new request every other cycle; different sub-banks every cycle`, 't-sm', 'start', 'l2:l2.subbank-busy l2:l2.throughput');
  gpp._box = {x: -150, y: 486, w: 1224, h: 50};
  part(L, 'tol3', -150, 632, 460, 56, COL.net, 'to_l3 master → the mesh (a miss)', {ty: 36, facts: 'meshstop'});
  ap.rbufC = {x: 582, y: 107}; ap.rq = {x: 50, y: 107}; ap.rsp = {x: 988, y: 325}; ap.dq = {x: 790, y: 107};
}

function buildL2Sub(L, ap, inst) {
  const a = inst, band = [640, 768];
  frame(L, {title: `Sub-bank ${a.sub} (PA[9:8]) of bank ${a.bank}`, sub: `a tag RAM, a tag-state RAM and four data panels; the L2's rows are sets ${hex3(0x280)}–${hex3(0x2FF)}`, subf: 'l2:l2.partition.rows',
    tags: [['documented', 'documented']], col: COL.store});
  const macro = (key, x, w, title, sub, rowsN, i, o) => {
    o = o || {};
    const g = part(L, key, x, 14, w, 420, COL.store, title, Object.assign({fo: 0.06, sub}, o));
    const top = 110, H = 300, yOf = r => top + r / rowsN * H;
    S(E('rect', {x: x + 12, y: top, width: w - 24, height: H, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.12, stroke: 'var(--c3)', strokeWidth: 1.25});
    // the band of this level's rows
    const b0 = yOf(o.b0), b1 = yOf(o.b1);
    S(E('rect', {x: x + 12, y: b0, width: w - 24, height: b1 - b0, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: 0.18});
    const ic = icgSym(g, x + w / 2 - 26, 74, {w: 52, h: 34});
    return {g, yOf, x, w, icg: ic.box, rowY: yOf(o.row)};
  };
  const tr = macro('tagram', -150, 150, 'tag RAM', [{t: nt('l2_mtag_s'), f: nf('l2_mtag_s')}], 1024, 0, {b0: band[0], b1: band[1], row: a.set});
  const sr = macro('stateram', 12, 150, 'tag state', [{t: nt('l2_mstate_s'), f: nf('l2_mstate_s')}], 1024, 0, {b0: band[0], b1: band[1], row: a.set});
  T(L, 87, 452, 'two-port', 't-sm', 'middle', 'l2:l2.tag-state-ram');
  part(L, 'ecc', 186, 14, 210, 84, COL.logic, 'te: tag ECC', {ctx: {i: 0}, sub: ['SECDED, 23 + 6 bits']});
  const gc = part(L, 'cmp', 186, 112, 210, 180, COL.logic, 'tc: compare', {sub: ['4 × 23 bits']});
  ap.eq = [];
  for (let w = 0; w < 4; w++) { const cx = 212 + w * 48, cy = 236; S(E('circle', {cx, cy, r: 17, 'pointer-events': 'none'}, gc), {fill: 'var(--surface)', stroke: 'var(--c1)', strokeWidth: 2}); T(gc, cx, cy + 7, '=', 't-labb', 'middle'); ap.eq.push({x: cx, y: cy}); }
  part(L, 'zero', 186, 306, 210, 64, COL.logic, 'zero bit', {sub: ['zeros: skip the data']});
  part(L, 'rowaddr', 186, 384, 210, 50, COL.logic, `row ${fnum(a.row)}`, {ty: 32});
  ap.panels = [];
  for (let p = 0; p < 4; p++) {
    const m = macro('data', 414 + p * 166, 154, `panel ${p}`, [{t: nt('l2_mdata_s'), f: nf('l2_mdata_s')}], 4096, p, {b0: 2560, b1: 3072, row: a.row, ctx: {i: p, inst: {panel: p}}, child: 'panel', cur: p === a.panel});
    ap.panels.push(m);
  }
  ap.macros = {tag: tr, state: sr};
  part(L, 'ecc', 414, 452, 652, 70, COL.logic, 'de: data ECC', {ctx: {i: 1}, sub: [{t: `8 × SECDED, ${nt('l2_ecc')}`, f: nf('l2_ecc')}], ty: 26});
  part(L, 'dc', 414, 536, 652, 56, COL.net, 'dc: data complete → the response mux and the read buffer', {ty: 35, tcls: 't-sm'});
  T(L, -150, 486, 'shaded: the L2\'s rows', 't-smb', 'start', 'l2:l2.partition.rows');
  T(L, -150, 508, `tag RAMs: sets ${hex3(0x280)}–${hex3(0x2FF)}`, 't-sm', 'start', 'l2:l2.partition.rows');
  T(L, -150, 530, 'data panels: rows 2,560–3,071 ({set, way})', 't-sm', 'start', 'scp:scp.m0-rows l3:l3.same-arrays');
  T(L, -150, 568, `this line: set ${hex3(a.set)} = PA[16:10] + ${hex3(0x280)}, way ${a.way}`, 't-sm', 'start', 'l2:l2.decode');
  T(L, -150, 590, `→ data row {set, way} = ${fnum(a.row)}`, 't-smb', 'start', 'l2:l2.decode');
  T(L, -150, 640, 'the other sub-banks\' RAM inputs stay frozen', 't-sm', 'start', 'l2:l2.panel-select');
  ap.panelBox = ap.panels[a.panel] ? {x: ap.panels[a.panel].x, y: 14, w: 154, h: 420} : null;
}

function buildL2Panel(L, ap, inst) {
  buildPanel(L, ap, {title: `Data panel ${inst.panel} · ${nt('l2_mdata_s')} · 1PUHD`, f: nf('l2_mdata_s'), band: 'l2', row: inst.row,
    sub: 'saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11: a compiled macro, "SRAM memory panels" in the spec'});
}
function buildL2Cell(L, ap, inst) {
  buildCell(L, ap, {title: 'One bit · a 6T SRAM cell (generic)',
    sub: 'the spec says SRAM panels; the lab lead said the chip is not using SRAM; the bitcell is not documented (asked)',
    note: [`a shire's arrays: ≈ ${nt('l2_tr')}`, 'cell transistors if 6T/8T (estimate)'], noteF: nf('l2_tr')});
}
function buildL2Xing(L, ap, inst) {
  buildXing(L, ap, {title: 'The crossing · a level shifter', sub: 'the neighbourhood\'s bank FIFO is a VC FIFO with level shifters built in (documented); the circuit is generic',
    vddl: `VDDL ${nt('l1_v')}`, vddlF: nf('l1_v'), vddh: 'VDDH (rail asked)', vddhF: 'l2:l2.rail.hv-logic'});
}

SCENES.l2 = {
  lv: 'l2', title: 'L2 (shire cache)', short: 'L2', root: 'shire', inst: {},
  setInst() { const a = dec2(ADDR.pa); this.inst = {bank: a.bank, sub: a.sub, set: a.set, way: a.way, row: a.row, panel: 0}; },
  head: () => `${n('l2_kb')} per shire in ${n('l2_sets')} of the shire cache's panels; a hit takes ${n('l2_lat')}, ${n('l2_lat_rb')} from the read buffer`,
  addrFields(pa) {
    const a = dec2(pa);
    return [['bank', 'PA[7:6]', a.bank, 'l2:l2.bank-select', true], ['sub-bank', 'PA[9:8]', a.sub, 'l2:l2.decode', true],
      ['set', 'PA[16:10] + 0x280', hex3(a.set), 'l2:l2.decode l2:l2.partition.rows', true], ['data row', '{set, way}', fnum(a.row), 'l2:l2.decode', true], ['tag', 'above PA[16]', '', 'l2:l2.decode']];
  },
  scales: {
    shire: {name: 'Shire', short: 'Shire', parent: null, def: 'bank', build: buildL2Shire},
    bank: {name: 'Bank', short: 'Bank', parent: 'shire', def: 'sub', tw: 238, target: (ap, inst) => ap.bank[inst.bank].box, build: buildL2Bank, label: inst => `bank ${inst.bank}`},
    sub: {name: 'Sub-bank', short: 'Sub-bank', parent: 'bank', def: 'panel', tw: 200, target: (ap, inst) => ap.sub[inst.sub].box, build: buildL2Sub, label: inst => `sub-bank ${inst.sub} of bank ${inst.bank}`},
    panel: {name: 'Data panel', short: 'Panel', parent: 'sub', def: 'cell', tw: 154, target: ap => ap.panelBox, build: buildL2Panel, label: inst => `data panel ${inst.panel}`},
    cell: {name: 'Cell', short: 'Cell', parent: 'panel', def: null, tw: 90, target: ap => { const k = ap.rowK, y = ap.Y0 + k * ap.RH; return {x: ap.AX + ap.CW, y: y + 2, w: ap.CW - 12, h: ap.RH - 16}; }, build: buildL2Cell},
    xing: {name: 'Crossing', short: 'Crossing', parent: 'shire', def: null, tw: 264, target: ap => ap.xingBox, build: buildL2Xing},
  },
};
const L2P = SCENES.l2.parts = {
  overview: () => ({kick: 'Level 2 · key 2', title: 'The L2', badge: [['documented', 'structure, timing, energy'], ['generic', 'the cell'], ['unknown', 'the bitcell, the floorplan']],
    what: `The L2 is ${n('l2_kb')} per shire: ${src('sets 0x280–0x2FF of every sub-bank', 'l2:l2.partition.rows')} in the ${n('l2_sc')} shire cache, whose other rows hold the scratchpad and a slice of the L3. ${n('l2_banks')} (PA[7:6]) of ${n('l2_sub')} each; the tags are read first, then one way's row of four ${n('l2_panel_w')} panels. The spec calls the arrays "SRAM memory panels" and names compiled macros; ${src('the lab lead said the chip is not using SRAM', 'l2:l2.storage-question')}, and no source gives the bitcell. A hit takes ${n('l2_lat')} (the spec: ${n('l2_spec')} shire clocks inside the cache, so ${n('l2_over')} outside it), ${n('l2_lat_rb')} from the read buffer. The chip streams ${n('l2_bw')} from its L2s, ${n('l2_bw128')}, half the four banks' ${n('l2_bw256')}: which block caps it is asked. Reading it costs about ${n('l2_e')}.`,
    kpis: [K('l2_kb', 'per shire (mode M0)'), K('l2_lat', 'a hit, three cards'), K('l2_e', 'above idle'), kpi(n('l2_v') + ' mV', 'SRAM rail, on the die')],
    extra: ladderHtml('l2')}),
  lvband: () => ({kick: 'L2 · shire', title: 'The minions\' low-voltage region', badge: [['documented', 'spec and measured']], what: `The minions and most of each neighbourhood run on the minion rail (${n('l1_v')}) and the neighbourhood clock; the neighbourhoods' north ports are the high-voltage interface. A request crosses into the Shire Channel through the bank FIFOs.`}),
  rail: () => ({kick: 'L2 · shire', title: 'The Shire Channel (HV)', badge: [['documented', 'spec and measured'], ['unknown', 'the logic\'s rail']],
    what: `The shire cache, the UC block and the instruction-cache memories are a separate high-voltage region on the shire clock, one shire-cache cycle per minion cycle at ${n('l2_mhz')}. The SRAM rail measures ${n('l2_v_rng')} on the die, at a ${n('l2_set705')} set point (${n('l2_rail750')} is the card's power-tree figure and the boot default; the firmware limits it to ${n('l2_limits')}). Whether that rail also feeds the cache's logic or only the macros is not stated: asked. At idle it draws ${n('l2_leak')} for the chip, ${n('l2_leak67')} and ${n('l2_leak82')} on one card.`,
    kpis: [kpi(n('l2_v') + ' mV', 'on the die, idle'), K('l2_leak', 'the rail at idle, chip')]}),
  nbr: ctx => ({kick: 'L2 · shire', title: `Neighbourhood ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']],
    what: `Eight minions' misses go through a 2:1 minion arbiter, a two-stage 13:1 round-robin and a one-cycle pre-processing stage into one of five bank FIFOs: at least ${n('l2_nbr6')} each way for a minion's request. Requests are ${n('l2_req256')} wide inside the neighbourhood, responses and the link into each bank ${n('l2_link')}.`}),
  fifo: () => ({kick: 'L2 · shire', title: 'Bank FIFOs: the crossing', badge: [['documented', 'the crossing exists'], ['generic', 'the circuit']],
    what: 'The neighbourhood\'s per-bank output FIFOs double as the clock and voltage crossing: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the LV/HV edge; their cells sit in the HV region "as performance and access time improve with the voltage". Responses cross back through a VC FIFO at the neighbourhood\'s input.',
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="xing">Zoom into the crossing</button>`}),
  reqxbar: () => ({kick: 'L2 · shire', title: 'Request crossbar', badge: [['documented', 'spec']], what: 'A full crossbar from the 5 clients (4 neighbourhoods and the RBOX) to the 4 banks and the UC block, one catch FIFO per neighbourhood at each bank, routed on top of the banks.'}),
  rspxbar: () => ({kick: 'L2 · shire', title: 'Response crossbar', badge: [['documented', 'spec']], what: 'The same module in reverse. Neighbourhoods never push back (their space is reserved); it arbitrates only when two banks answer the same neighbourhood in one cycle.'}),
  banks: ctx => ({kick: 'L2 · shire', title: `Bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']],
    what: `One of ${n('l2_banks')}, chosen by PA[7:6]: an independent L2 cache with its own request queue, pipeline and ports, ${n('l2_sub')}. It takes one request and returns one ${n('l2_link')} line a cycle at most.`,
    act: ctx.i != null ? `<button type="button" class="st-btn" data-act="zoom" data-to="bank" data-bank="${ctx.i}">Zoom into bank ${ctx.i}</button>` : ''}),
  uc: () => ({kick: 'L2 · shire', title: 'UC block', badge: [['documented', 'spec']], what: 'The uncacheable block: barriers, credit counters and global atomics. Not on an L2 access\'s path.', facts: 'banks'}),
  meshstop: () => ({kick: 'L2 · shire', title: 'To the mesh', badge: [['documented', 'spec']], what: `On a miss the bank's request queue issues a read on its ${n('l2_link')} to_l3 port; it is arbitrated with the other banks onto 4 mesh lanes and crosses to the NoC's clock and voltage through a VC FIFO with 2-stage synchronisers. The L3 tab follows it.`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="l3">The L3 (key 3) →</button>`}),
  tol3: () => Object.assign(L2P.meshstop(), {facts: 'meshstop'}),
  partition: () => ({kick: 'L2 · shire', title: 'One sub-bank\'s rows', badge: [['documented', 'spec']],
    what: `In mode M0 (the reset mode and the one these cards run) every sub-bank's 1,024 sets are split: sets 0–639 scratchpad, ${n('l2_sets')} L2 (${n('l2_128')}), 768–1023 L3: ${n('l2_part')} per shire. They are row ranges of the same macros, not separate memories. Every lab card's driver reports these sizes.`}),
  reqq: () => ({kick: 'L2 · bank', title: 'Request queue', badge: [['documented', 'spec']], what: `${n('l2_reqq')}, the bank's MSHRs: an entry lives from allocation through any miss, fill and victim write-back; ${n('l2_reqq21')} are reserved for L3-slave requests. The winner is chosen in three steps (round-robin per sub-bank, L3 before the neighbourhoods, busy sub-banks masked); requests to one address keep their order.`}),
  arb: () => Object.assign(L2P.reqq(), {facts: 'reqq'}), order: () => Object.assign(L2P.reqq(), {facts: 'reqq'}),
  rbuf: () => ({kick: 'L2 · bank', title: 'Read buffer', badge: [['documented', 'spec and measured'], ['unknown', 'its storage']],
    what: `${n('l2_rbuf')}, fully associative, per bank (${n('l2_rbuf2k')}): lines are installed on L2 and scratchpad read hits and served "without touching the RAM panels, as these memory panels are slow and power hungry". It is on by default and the cards show it: a ${n('l2_rbuf_plateau')} for small working sets. What it is built from on silicon is asked.`,
    kpis: [K('l2_lat_rb', 'a read-buffer hit'), K('l2_lat', 'from the panels')]}),
  dataq: () => ({kick: 'L2 · bank', title: 'Data queue', badge: [['documented', 'spec']], what: `One line per request-queue entry in a two-port register file (BIST sees ${n('l2_dataq')} plus a small side RAM). Read hits normally bypass it.`}),
  cbuf: () => ({kick: 'L2 · bank', title: 'Coalescing buffer', badge: [['documented', 'spec']], what: `${n('l2_cbuf')}: merges write-arounds (TensorStores to the L3 or a remote scratchpad) until all four quadwords of a line are written.`}),
  atomic: () => ({kick: 'L2 · bank', title: 'Atomic unit', badge: [['documented', 'spec']], what: 'Swap, add, logic, min and max on 32, 64 and 256 bits; an atomic keeps its sub-bank busy from the read through the operation to the write.'}),
  perfmon: () => ({kick: 'L2 · bank', title: 'Performance monitor', badge: [['documented', 'spec']], what: 'A cycle counter and two event counters per bank (read-buffer hits, tag hits and misses, victims, opcodes), M-mode only; a U-mode kernel reads them with the firmware\'s default qualifier, which does not separate hits from misses.'}),
  hpf: () => ({kick: 'L2 · bank', title: 'A hardware prefetcher?', badge: [['unknown', 'asked']], what: 'The original RTL has an L2 hardware-prefetcher interface (shire_cache_bank_l2hpf); the re-implementation stubs it out. Whether the silicon has one is asked.'}),
  subbanks: ctx => ({kick: 'L2 · bank', title: `Sub-bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']],
    what: `Chosen by PA[9:8]: its own tag RAM, tag-state RAM, four data panels and ECC; ${src('4,096 lines = 1,024 sets × 4 ways', 'l2:l2.sets')}.`,
    act: ctx.i != null ? `<button type="button" class="st-btn" data-act="zoom" data-to="sub" data-sub="${ctx.i}">Zoom into sub-bank ${ctx.i}</button>` : ''}),
  pipe: () => ({kick: 'L2 · bank', title: 'The bank\'s pipeline', badge: [['documented', 'spec'], ['derived', 'the budget']],
    what: `${n('l2_stages')} named stages for a read hit with 2-cycle RAMs: ag (allocate), ad (dependencies), rqa (arbitration), tap ta ta0 ta1 (tag and tag-state RAMs), te (tag ECC), tc (compare), dap da da0 da1 (data RAMs), de (data ECC), dc (data complete). The spec gives an L2 hit ${n('l2_spec')} shire clocks from request to response; if each stage is one cycle, about 6 are left for the crossbars and the response mux (our reading). The RAM access time is one setting, ${n('l2_ramdelay')} cycles by default.`}),
  rspmux: () => ({kick: 'L2 · bank', title: 'Response mux', badge: [['documented', 'spec']], what: 'Per-neighbourhood queues and an arbiter, then the response crossbar back to the requester.'}),
  dc: () => Object.assign(L2P.rspmux(), {facts: 'rspmux'}),
  tagram: () => ({kick: 'L2 · sub-bank', title: 'Tag RAM', badge: [['documented', 'spec'], ['unknown', 'the bitcell']],
    what: `A compiled macro of ${n('l2_mtag')} (type 1PUHD): one row per set holding all four ways' tags, ${n('l2_tag23')} each, read and compared in parallel. Its L2 rows are ${n('l2_sets')}.`}),
  stateram: () => ({kick: 'L2 · sub-bank', title: 'Tag-state RAM', badge: [['documented', 'spec']],
    what: `A two-port macro of ${n('l2_mstate')} (type 2PUHDRF; the spec says the state RAM is two-ported): each way's valid, locked, zero and dirty bits, a 5-bit LRU code and 7 ECC bits, a ${n('l2_state')}. It is read and written on every request, the update through its second port in the same pass.`}),
  data: ctx => ({kick: 'L2 · sub-bank', title: `Data panel ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec'], ['unknown', 'the geometry, the bitcell']],
    what: `A compiled macro of ${n('l2_mdata')} (type 1PUHD), one of four per sub-bank, each holding one 128-bit quadword and 16 ECC bits: a line is one row across the four, ${n('l2_line')}. Only the panels an access needs are clocked, and their inputs are held still between accesses.`,
    act: ctx.i != null ? `<button type="button" class="st-btn" data-act="zoom" data-to="panel" data-panel="${ctx.i}">Zoom into panel ${ctx.i}</button>` : ''}),
  ecc: () => ({kick: 'L2 · sub-bank', title: 'ECC', badge: [['documented', 'spec'], ['generic', 'the XOR trees']], what: `SECDED on every shire-cache RAM: 6 bits per tag, 7 per tag-state row, ${n('l2_ecc')}, checked in the stages te and de. No background scrub on this chip.`}),
  cmp: () => ({kick: 'L2 · sub-bank', title: 'Tag compare', badge: [['documented', 'four comparators'], ['generic', 'the circuit']], what: 'Four 23-bit comparators find the hit way in stage tc; the data RAM\'s address includes the way, so a hit reads only that way\'s row.'}),
  zero: () => ({kick: 'L2 · sub-bank', title: 'The zero bit', badge: [['documented', 'spec and RTL'], ['unknown', 'partial writes']], what: 'Each way\'s tag state has a zero bit: when it is set the data RAM is neither read nor written and zeros are returned (esr_sc_zero_state_enable, on by default). A fill or a full-line write of an all-zero line sets it (the re-implementation RTL, as at the L3); whether a partial write that leaves the line all zero does is asked.'}),
  rowaddr: () => ({kick: 'L2 · sub-bank', title: 'The data row', badge: [['documented', 'spec and RTL']], what: `The set is PA[16:10] under mode M0's 7-bit mask, offset to ${hex3(0x280)}; the data row is {set, way} (the re-implementation's RTL: set-major, which puts the L2 in rows 2,560–3,071 of each panel; the L2 file writes "{way, set}", a conflict listed under the diagram).`}),
  icg: () => ({kick: 'L2 · panel', title: 'The macro\'s clock gate', badge: [['documented', 'spec'], ['generic', 'the circuit']], what: 'Module-level clock gaters stop a bank\'s clock with nothing outstanding; each RAM\'s clock is gated on only for its access (in the re-implementation). An integrated clock gate is a latch holding the enable, ANDed with the clock (textbook).'}),
  panel: () => ({kick: 'L2 · panel', title: 'A data panel', badge: [['documented', 'the shell'], ['generic', 'the periphery'], ['unknown', 'the geometry']],
    what: `The macro saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11: ${n('l2_mdata')}, "IP acquired from a third party vendor", tested with a Synopsys-style BIST. ${n('l2_macros')} per shire (${n('l2_macros96')} macros with the tags). What is inside (rows, columns, column mux, sense amplifiers) is not documented; a compiler's usual naming would read m4b4 as a 4:1 column mux and 4 banks, which nothing confirms.`, facts: 'panel'}),
  array: () => Object.assign(L2P.panel(), {facts: 'panel'}),
  periph: () => ({kick: 'L2 · panel', title: 'The periphery', badge: [['generic', 'textbook']], what: 'Address latch, predecoder, wordline drivers, precharge, column mux, sense amplifiers, output latch and write drivers: the parts every SRAM macro has, drawn from the textbook.'}),
  pre: () => ({kick: 'L2 · cell', title: 'Precharge and equalise', badge: [['generic', 'textbook']], what: 'Two PMOS hold the bitline pair at the supply between accesses and a third shorts them together; they switch off just before the wordline rises and on again after, restoring the discharged bitline, most of a read\'s array energy (textbook).'}),
  mux: () => ({kick: 'L2 · cell', title: 'Column mux', badge: [['generic', 'textbook'], ['unknown', 'the ratio']], what: `NMOS pass gates connect one pair of bitlines in each group to a sense amplifier. With a 4:1 mux, ${n('half4')} for every bit read; whether m4 means 4:1 is asked.`, facts: 'half'}),
  sa: () => ({kick: 'L2 · cell', title: 'Sense amplifier', badge: [['generic', 'textbook']], what: 'A cross-coupled latch with an NMOS tail: when SAE fires it resolves the small difference between the bitlines to full swing. Read-margin settings delay SAE so more swing develops, slower and safer at low voltage (textbook).'}),
  olat: () => Object.assign(L2P.sa(), {facts: 'sa'}),
  wl: () => ({kick: 'L2 · cell', title: 'Wordline', badge: [['generic', 'textbook']], what: 'The row decoder selects one wordline driver, which raises the wordline across the row; a read-assist setting may lower it slightly (textbook; RA = 1 is the reset value in the functional model, what the silicon holds is asked).', facts: 'periph'}),
  cell: () => ({kick: 'L2 · cell', title: 'The storage cell', badge: [['generic', 'drawn: a textbook 6T cell'], ['unknown', 'the ET bitcell']],
    what: `Drawn as a 6T cell: two cross-coupled inverters and two access NMOS on the bitline pair. The spec calls the arrays SRAM and names Synopsys-style macros; ${src('the lab lead said the chip is not using SRAM', 'l2:l2.storage-question')}, perhaps meaning the L1 and the register files, which are latches. If the single-port macros use a 6T cell and the two-port file an 8T one, a shire's arrays hold about ${n('l2_tr')} cell transistors (an estimate).`}),
  wd: () => ({kick: 'L2 · cell', title: 'Write drivers', badge: [['generic', 'textbook'], ['documented', 'the trims']], what: 'They pull one bitline of each written column to ground; the wordline rises and the access transistor overpowers the cell\'s pull-up, so the cell flips. Write assist (WA = 7, the reset value in the functional model; the silicon\'s is asked) and the write pulse set the margin. A full-swing bitline costs more to restore, so a write costs more than a read.'}),
  half: () => ({kick: 'L2 · cell', title: 'A half-selected column', badge: [['generic', 'textbook']], what: `Every cell on the raised wordline discharges its bitline, not only the column being read: with a 4:1 mux, ${n('half4')} for every bit delivered.`}),
  leak: () => ({kick: 'L2 · cell', title: 'Leakage', badge: [['generic', 'the mechanism'], ['documented', 'the bound, measured']], what: `Every cell leaks all the time through its off transistors, more at higher temperature. The SRAM rail at idle bounds it: ${n('leak_mb')} at 80 °C, all 128 MB counted.`}),
  lvin: () => Object.assign(L2P.ls(), {facts: 'ls'}), sync: () => Object.assign(L2P.ls(), {facts: 'ls'}),
  ls: () => ({kick: 'L2 · crossing', title: 'The level shifter', badge: [['generic', 'textbook'], ['documented', 'that it is there']],
    what: `A request bit leaves the minion rail at ${n('l1_v')} and enters the HV region. A low-to-high shifter is typically a cross-coupled PMOS pair on the high rail driven by an NMOS differential pair: the input pulls one side down and the PMOS pair snaps the other to the high rail (textbook). The ET RTL models it as a buffer; the physical cell and the HV logic's rail are not documented.`}),
  energy: () => ({kick: 'L2 · energy', title: 'What an L2 access costs', badge: [['documented', 'measured'], ['unknown', 'the split']],
    what: `Reading the L2 with tensor loads on every minion costs ${n('l2_e')}, about ${n('l2_e_line')} per line for the whole path. On one card on 19 September an L2 hit split into ${n('l2_e_sram')} on the SRAM rail, ${n('l2_e_min')} on the minion rail and ${n('l2_e_noc')} on the NoC rail, of ${n('l2_e_tot')}. A scratchpad write costs about twice a read (${n('l2_e_wr')}); a random fsw through the L1 costs ${n('l2_fsw')}. How much of the SRAM rail's share is the arrays and how much the logic is asked.`}),
};

Object.assign(L2P, {
  trim: () => ({kick: 'L2 · panel', title: 'The macro\'s trims', badge: [['documented', 'spec, reset values, measured rail'], ['unknown', 'the live settings']],
    what: `Each RAM group has read margin (RM, with its enable RME), read assist (RA), write assist (WA) and write-pulse (WPULSE) bits, by default the spec's RM0 row "to allow nominal 650 mV operation": ${n('l2_rm0')}, ${n('l2_trims')}; the table runs to ${n('l2_rm5')}. The emulator's reset values are exactly that row and no firmware writes them. The rail measures ${n('l2_v')} mV on the die, so the arrays run above RM0's nominal with its assists; what the cards actually program is asked.`}),
  geom: () => ({kick: 'L2 · panel', title: 'Inside the macro: unknown', badge: [['unknown', 'asked']], what: `A memory compiler's usual naming would read m4 and b4 in the macro's name as a 4:1 column mux and 4 internal banks: about 1,024 wordlines by 576 bitline pairs, each output bit chosen from 4 columns. No source defines the fields; the macro's datasheet settles it. It decides how many bitlines swing per access (${n('half4')} per bit if 4:1).`}),
  band: () => ({kick: 'L2 · panel', title: 'The panel\'s rows', badge: [['documented', 'spec and RTL']], what: `The scratchpad is the lowest ${n('scp_rows')} rows of each panel, the L3 ${n('l3_rows')}; the L2 is the 512 rows between (sets 640–767 times 4 ways), the rows this level lights.`}),
});
const PKM = (c, p, col, r) => { const pk = packet(c.fx, col || 'var(--c2)', r || 11); at(pk, p); settle(c.fx, pk, p, null); return pk; };
const B2 = () => SC().inst;
/* the request's way down from minion 0 of neighbourhood 0 to its bank FIFO, and on through the crossbar */
function reqPath(c, upto) {
  const a = c.ap, b = B2().bank, m = a.min[0][0], f = a.fifo[0][b];
  const P = [m, {x: m.x - 34, y: m.y}, {x: m.x - 34, y: 140}, a.arb[0], {x: x0Gap(a), y: 140}, {x: x0Gap(a), y: 194}, {x: f.x, y: 194}, f];   // clear of the arbiters' label
  if (upto === 'bank') P.push({x: f.x, y: a.xbarY}, {x: a.bank[b].x, y: a.xbarY}, a.bank[b]);
  return P;
}
function rspPath(c) {
  const a = c.ap, b = B2().bank, m = a.min[0][0], f = a.fifo[0][b];
  return [a.bank[b], {x: a.bank[b].x, y: a.rxbarY}, {x: f.x - 14, y: a.rxbarY}, {x: f.x - 14, y: 250}, {x: m.x + 20, y: 250}, {x: m.x + 20, y: m.y}];
}
function stgLit(c, names) { names.forEach(s => ringAround(c.fx, c.ap.stg[s], {fo: 0.25, sw: 3})); lit(c, 'pipe', {noRing: true}); }
async function macroRead(tok, c, m, lab, o) {
  o = o || {};
  lit(c, o.key, {i: o.i});
  await icg(tok, c, m.icg, true, {on: '', ms: 400, len: 36});
  const ls = String(lab || '').split('\n');
  await sweep(tok, c, [{x: m.x + 12, y: m.rowY}, {x: m.x + m.w - 12, y: m.rowY}], {ms: 450, w: 5, label: ls[ls.length - 1], at: {x: m.x + 14, y: m.rowY}, dx: 0, dy: -8, cls: 't-smb halo'});
  ls.slice(0, -1).forEach((t, i, a) => fadeIn(T(c.fx, m.x + 14, m.rowY - 8 - 22 * (a.length - i), t, 't-smb halo', 'start')));   // the lines above the last
}
const L2A = SCENES.l2.access = {};
const lf = k => nf(k);
L2A['load-hit'] = {
  led: [[null, null], [src('≥ ' + nt('l2_nbr6'), lf('l2_nbr6')), null], [null, null], [null, null], [null, null], [src(nt('l2_ramdelay'), lf('l2_ramdelay')), null], [null, null], [null, null],
    [src(nt('l2_ramdelay'), lf('l2_ramdelay')), null], [null, null], [null, null], [null, null], [src('≥ ' + nt('l2_rsp6'), lf('l2_rsp6')), null]],
  tot: () => ({c: `${n('l2_lat')} measured (the spec: ${n('l2_spec')} inside the cache)`, e: `about ${n('l2_e_line')} per line`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `An L2 hit: ${n('l2_lat')} load to use on three cards, ${n('l2_spec')} shire clocks of it inside the cache by the spec; about ${n('l2_e_line')} per line.`,
  steps: [
    {name: 'L1 miss', where: 'shire', say: () => 'The load has missed the L1 of minion 0 (the L1 tab plays that): a miss handler sends a line read',
      run: async (tok, c) => { lit(c, 'nbr', {i: 0}); const m = c.ap.min[0][0]; PKM(c, m); sayAt(c, m.x, m.y, ['the L1 missed', 'see the L1 (key 1)'], {side: 'r'}); await pulse(tok, c.fx, m, 1000); }},
    {name: 'To FIFO', where: 'shire', dive: ['xing'], say: () => `Through the neighbourhood's arbiters to the FIFO of bank ${B2().bank}, across the LV/HV edge: at least ${n('l2_nbr6')}`,
      run: async (tok, c) => {
        lit(c, 'nbr', {i: 0}); lit(c, 'fifo', {i: 0}); counter(c, `≥ ${nt('l2_nbr6')}`, 'the minimum, spec');
        const P = reqPath(c), pk = PKM(c, P[0]); await travel(tok, c.fx, pk, P, 1500);
        sayAt(c, P[P.length - 1].x, P[P.length - 1].y, ['bank FIFO: a VC FIFO', 'level shifters to the HV region'], {side: 'r'});
      },
      deep: {xing: (tok, c) => xingPlay(tok, c, true)}},
    {name: 'Req xbar', where: 'shire', say: () => `The request crossbar admits it to bank ${B2().bank} (PA[7:6]), one request per bank per cycle`,
      run: async (tok, c) => {
        lit(c, 'reqxbar'); lit(c, 'banks', {i: B2().bank});
        const b = B2().bank, f = c.ap.fifo[0][b], pk = PKM(c, f);
        await travel(tok, c.fx, pk, [f, {x: f.x, y: c.ap.xbarY}, {x: c.ap.bank[b].x, y: c.ap.xbarY}, c.ap.bank[b]], 1100);
      }},
    {name: 'Queue', where: 'bank', say: () => `A request-queue entry is allocated; the address is checked against the ${n('l2_rbuf')} of the read buffer: a miss`,
      run: async (tok, c) => {
        lit(c, 'reqq'); stgLit(c, ['ag', 'ad']); counter(c, 'ag, ad');
        slotOn(c, c.ap.q[5]);
        await wait(tok, 400); lit(c, 'rbuf');
        c.ap.rb.forEach(r => { const x = +r.getAttribute('x'), y = +r.getAttribute('y'); fadeIn(T(c.fx, x + 20, y + 19, '≠', 't-smb halo', 'middle')); });
        sayAt(c, 700, 40, ['read buffer: no match', 'on to the pipeline'], {tl: true});
        await wait(tok, 500);
      }},
    {name: 'Arbitrate', where: 'bank', say: () => `Arbitration (rqa): round-robin per sub-bank, L3 requests first, busy sub-banks masked; sub-bank ${B2().sub} (PA[9:8]) wins`,
      run: async (tok, c) => { lit(c, 'arb'); stgLit(c, ['rqa']); lit(c, 'subbanks', {i: B2().sub}); counter(c, 'rqa'); const pk = PKM(c, c.ap.rq); await travel(tok, c.fx, pk, [c.ap.rq, {x: 50, y: 212}, {x: c.ap.sub[B2().sub].x, y: 212}, c.ap.sub[B2().sub]], 900); }},
    {name: 'Tag reads', where: 'sub', dive: ['cell'], say: () => `The tag and tag-state RAMs read set ${hex3(B2().set)}: ${n('l2_ramdelay')} cycles; the other sub-banks' RAMs stay still`,
      run: async (tok, c) => {
        counter(c, `tap … ta1: ${nt('l2_ramdelay')} cycles`, 'the RAM delay, spec default');
        await Promise.all([macroRead(tok, c, c.ap.macros.tag, `set ${hex3(B2().set)}:\n116 bits`, {key: 'tagram'}), macroRead(tok, c, c.ap.macros.state, '40 bits', {key: 'stateram'})]);
      },
      deep: {cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'Tag ECC', where: 'sub', say: () => 'Tag ECC (te): SECDED checks and repairs each way\'s 23 + 6-bit tag',
      run: async (tok, c) => { lit(c, 'ecc', {i: 0}); counter(c, 'te'); await sweep(tok, c, [{x: -2, y: c.ap.macros.tag.rowY}, {x: 186, y: 56}], {ms: 500, w: 4}); }},
    {name: 'Compare', where: 'sub', say: () => `Tag compare (tc): four comparators find way ${B2().way}; the new LRU code and flags go back through the tag-state RAM's second port`,
      run: async (tok, c) => {
        lit(c, 'cmp'); counter(c, 'tc');
        c.ap.eq.forEach((p, k) => fadeIn(T(c.fx, p.x, p.y - 24, k === B2().way ? 'hit' : 'no', k === B2().way ? 't-smb halo' : 't-sm halo', 'middle')));
        await wait(tok, 400);
        const m = c.ap.macros.state; lit(c, 'stateram');
        await sweep(tok, c, [{x: m.x + m.w - 12, y: m.rowY + 6}, {x: m.x + 12, y: m.rowY + 6}], {ms: 500, w: 4, col: 'var(--c7)', label: 'LRU', at: {x: m.x + 14, y: m.rowY + 6}, dx: 0, dy: 22});
        fadeIn(T(c.fx, m.x + 14, m.rowY + 50, 'written', 't-labb halo', 'start'));
      }},
    {name: 'Data read', where: 'sub', dive: ['panel', 'cell'], say: () => `The four panels read row ${fnum(B2().row)} = {set, way}: ${n('l2_line')} in ${n('l2_ramdelay')} cycles; only this sub-bank's panels are clocked`,
      run: async (tok, c) => {
        counter(c, `dap … da1: ${nt('l2_ramdelay')} cycles`, 'the RAM delay, spec default');
        await Promise.all(c.ap.panels.map((m, p) => macroRead(tok, c, m, p ? '' : `row ${fnum(B2().row)}`, {key: 'data', i: p})));
        fadeIn(T(c.fx, 740, 616, `${nt('l2_line')} out: 512 data + 64 ECC`, 't-smb halo', 'middle', lf('l2_line')));
      },
      deep: {panel: (tok, c) => panelRead(tok, c), cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'Data ECC', where: 'sub', say: () => `Data ECC (de): eight SECDED checks, one per 64-bit word, ${n('l2_ecc')}`,
      run: async (tok, c) => { lit(c, 'ecc', {i: 1}); counter(c, 'de'); await wait(tok, 600); }},
    {name: 'Complete', where: 'bank', say: () => 'Data complete (dc): the line goes to the response mux and is installed in the read buffer',
      run: async (tok, c) => { stgLit(c, ['dc']); lit(c, ['rspmux', 'rbuf']); counter(c, 'dc'); slotOn(c, c.ap.rb[0]); const s = c.ap.sub[B2().sub], pk = PKM(c, s); await travel(tok, c.fx, pk, [s, {x: s.x, y: 440}, {x: 988, y: 440}, c.ap.rsp], 1000); }},
    {name: 'Rsp xbar', where: 'shire', say: () => 'The response mux and the response crossbar send the line back to neighbourhood 0',
      run: async (tok, c) => { lit(c, 'rspxbar'); lit(c, 'banks', {i: B2().bank}); const P = rspPath(c), pk = PKM(c, P[0], 'var(--c7)'); await travel(tok, c.fx, pk, P.slice(0, 4), 1100, {col: 'var(--c7)'}); }},
    {name: 'To the L1', where: 'shire', dive: ['xing'], say: () => `Back across the HV/LV edge, the Fill FIFO, two 256-bit beats into the L1: ${n('l2_lat')} load to use, measured on three cards`,
      run: async (tok, c) => {
        lit(c, 'fifo', {i: 0}); lit(c, 'nbr', {i: 0}); counter(c, `${nt('l2_lat')} load to use`, 'measured, three cards');
        const P = rspPath(c), pk = PKM(c, P[3], 'var(--c7)'); await travel(tok, c.fx, pk, P.slice(3), 900, {col: 'var(--c7)'});
        sayAt(c, P[P.length - 1].x, P[P.length - 1].y, [`${nt('l2_lat')}`, `${nt('l2_e_line')} per line`], {side: 'r'});
      },
      deep: {xing: (tok, c) => xingPlay(tok, c, false)}},
  ]};
L2A['rbuf-hit'] = {
  led: [[src('≥ ' + nt('l2_nbr6'), lf('l2_nbr6')), null], [null, null], [null, null], [src('≥ ' + nt('l2_rsp6'), lf('l2_rsp6')), null]],
  tot: () => ({c: `${n('l2_lat_rb')} measured (the spec: ${n('l2_spec_rb')} inside)`, e: 'not measured'}), ask: {c: 'ask-cache-latency'},
  cap: () => `A read-buffer hit: the panels stay dark. ${n('l2_lat_rb')} against ${n('l2_lat')}: the ${n('l2_spec_rb')} against ${n('l2_spec')} shire clocks of the spec, the same ${cn(V('l2_lat') - V('l2_lat_rb'), 'l2:l2.lat.measured l2:l2.lat.spec', 0)} saved.`,
  steps: [
    {name: 'To the bank', where: 'shire', say: () => `As a load: through the neighbourhood and the crossbar to bank ${B2().bank}`,
      run: async (tok, c) => { lit(c, ['reqxbar']); lit(c, 'fifo', {i: 0}); const P = reqPath(c, 'bank'), pk = PKM(c, P[0]); await travel(tok, c.fx, pk, P, 1700); }},
    {name: 'RB hit', where: 'bank', say: () => 'The address matches a read-buffer entry at allocation: no tag, tag-state or data RAM is touched',
      run: async (tok, c) => {
        lit(c, ['reqq', 'rbuf']); slotOn(c, c.ap.rb[2]);
        { const r = c.ap.rb[2]; fadeIn(T(c.fx, +r.getAttribute('x') + 20, +r.getAttribute('y') - 4, 'hit', 't-smb halo', 'middle')); }
        idle(c, c.ap.parts.subbanks, 'not read: the read buffer has it', {at: {x: 170, y: 470}, anchor: 'start'});
        idle(c, c.ap.parts.pipe, '');
        await wait(tok, 700);
      }},
    {name: 'RB out', where: 'bank', say: () => 'The line comes out of the read buffer into its FIFO, then the response mux',
      run: async (tok, c) => { lit(c, ['rbuf', 'rspmux']); idle(c, c.ap.parts.subbanks, ''); const pk = PKM(c, c.ap.rbufC, 'var(--c7)'); await travel(tok, c.fx, pk, [c.ap.rbufC, {x: 582, y: 210}, {x: 988, y: 210}, c.ap.rsp], 1000, {col: 'var(--c7)'}); }},
    {name: 'Back', where: 'shire', say: () => `Back to the minion: ${n('l2_lat_rb')} load to use, measured on three cards`,
      run: async (tok, c) => { lit(c, ['rspxbar']); counter(c, `${nt('l2_lat_rb')} load to use`, 'measured, three cards'); const P = rspPath(c), pk = PKM(c, P[0], 'var(--c7)'); await travel(tok, c.fx, pk, P, 1500, {col: 'var(--c7)'}); }},
  ]};
L2A['write-back'] = {
  led: [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null]],
  tot: () => ({c: 'not measured apart', e: `${n('l2_fsw')} per random fsw (allocate and write back)`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `A write-back: the L1 evicts a dirty line and the bank writes it into the hit way's row; a scratchpad write costs about twice a read.`,
  steps: [
    {name: 'L1 evicts', where: 'shire', say: () => 'The L1 is write-back: a dirty line leaves as two 256-bit transfers, re-joined in the Evict flop',
      run: async (tok, c) => { lit(c, 'nbr', {i: 0}); const m = c.ap.min[0][0]; await Promise.all([0, 1].map(async i => { await wait(tok, i * 300); const pk = PKM(c, m, 'var(--c2)', 9); await travel(tok, c.fx, pk, [m, {x: m.x - 34, y: m.y}, {x: m.x - 34, y: 140}, c.ap.arb[0]], 800); })); }},
    {name: 'To the bank', where: 'shire', dive: ['xing'], say: () => 'The same path as a load, with 512 bits of data: every bit crosses up through a level shifter',
      run: async (tok, c) => { lit(c, 'fifo', {i: 0}); lit(c, 'reqxbar'); const P = reqPath(c, 'bank'), pk = PKM(c, P[2]); await travel(tok, c.fx, pk, P.slice(2), 1400, {w: 9}); },
      deep: {xing: (tok, c) => xingPlay(tok, c, true)}},
    {name: 'Data queue', where: 'bank', say: () => 'A request-queue entry, and the 64 bytes written into its data-queue line',
      run: async (tok, c) => { lit(c, ['reqq', 'dataq']); slotOn(c, c.ap.q[6]); const pk = PKM(c, c.ap.rq); await travel(tok, c.fx, pk, [c.ap.rq, {x: 260, y: 107}, c.ap.dq], 800); }},
    {name: 'Tags', where: 'sub', say: () => 'The tags are read and compared as for a load; the state write marks the quadwords dirty',
      run: async (tok, c) => { await Promise.all([macroRead(tok, c, c.ap.macros.tag, 'tags', {key: 'tagram'}), macroRead(tok, c, c.ap.macros.state, 'dirty', {key: 'stateram'})]); lit(c, 'cmp'); }},
    {name: 'Data write', where: 'sub', dive: ['panel', 'cell'], say: () => 'The line is written into row {set, way} of the panels; only panels with written quadwords are enabled',
      run: async (tok, c) => { counter(c, 'a write: about 2× a read', 'measured, scratchpad'); await Promise.all(c.ap.panels.map((m, p) => macroRead(tok, c, m, p ? '' : 'written', {key: 'data', i: p}))); },
      deep: {panel: (tok, c) => panelRead(tok, c, {write: true}), cell: cellWrite}},
    {name: 'Ack', where: 'shire', say: () => `The bank acknowledges once the write completes; a random fsw through the L1 to the L2 costs ${n('l2_fsw')}`,
      run: async (tok, c) => { lit(c, 'rspxbar'); counter(c, `${nt('l2_fsw')} per fsw`, 'measured, three cards'); const P = rspPath(c), pk = PKM(c, P[0], 'var(--c7)', 8); await travel(tok, c.fx, pk, P, 1400, {col: 'var(--c7)'}); }},
  ]};
L2A.miss = {
  led: [[null, null], [null, null], [null, null], [null, null], [null, null]],
  tot: () => ({c: 'the L3 tab times it', e: '—'}), ask: {c: 'ask-cache-latency'},
  cap: () => `An L2 miss: the bank asks the line's L3 home over the mesh, fills the way the LRU picks, and writes a dirty victim back.`,
  steps: [
    {name: 'Tag miss', where: 'sub', say: () => 'Tag compare (tc): no way matches, so the data stages are skipped for this pass',
      run: async (tok, c) => {
        await macroRead(tok, c, c.ap.macros.tag, 'tags', {key: 'tagram'}); lit(c, 'cmp');
        c.ap.eq.forEach(p => fadeIn(T(c.fx, p.x, p.y - 24, 'no', 't-sm halo', 'middle')));
        idle(c, c.ap.parts.data, 'not read: a miss', {at: {x: 740, y: 470}});
      }},
    {name: 'To the L3', where: 'shire', handoff: {lv: 'l3', k: 'load-hit', label: 'Continue at the L3'}, say: () => `A read goes out on the bank's ${n('l2_link')} to_l3 port, through a VC FIFO with 2-flop synchronisers, to the line's L3 home`,
      run: async (tok, c) => { lit(c, ['banks', 'meshstop'], {}); const b = c.ap.bank[B2().bank], pk = PKM(c, b); await travel(tok, c.fx, pk, [b, {x: b.x, y: 552}, {x: c.ap.mesh.x, y: 552}, c.ap.mesh], 1300); sayAt(c, c.ap.mesh.x, c.ap.mesh.y, ['to the L3 home', 'continue at the L3 (key 3)'], {side: 'u'}); }},
    {name: 'Fill returns', where: 'shire', say: () => 'The line comes back and goes straight to the neighbourhood, and into the entry\'s data-queue line',
      run: async (tok, c) => { lit(c, ['meshstop', 'rspxbar']); const f = c.ap.fifo[0][B2().bank], pk = PKM(c, c.ap.mesh, 'var(--c7)'); await travel(tok, c.fx, pk, [c.ap.mesh, {x: c.ap.mesh.x, y: c.ap.rxbarY}, {x: f.x - 14, y: c.ap.rxbarY}, {x: f.x - 14, y: 250}, c.ap.min[0][0]], 1500, {col: 'var(--c7)'}); }},
    {name: 'Fill write', where: 'sub', say: () => 'L2_Fill: the LRU way is the victim (read first if dirty), then the new tag, state and 576-bit row are written',
      run: async (tok, c) => { await Promise.all([macroRead(tok, c, c.ap.macros.tag, 'new tag', {key: 'tagram'}), macroRead(tok, c, c.ap.macros.state, 'state', {key: 'stateram'})]); await Promise.all(c.ap.panels.map((m, p) => macroRead(tok, c, m, p ? '' : 'filled', {key: 'data', i: p}))); }},
    {name: 'Victim out', where: 'shire', say: () => 'A dirty victim goes to its L3 home as a write; later reads of that address wait behind it',
      run: async (tok, c) => { lit(c, ['banks', 'meshstop']); const b = c.ap.bank[B2().bank], pk = PKM(c, b, 'var(--c5)'); await travel(tok, c.fx, pk, [b, {x: b.x, y: 552}, {x: c.ap.mesh.x, y: 552}, c.ap.mesh], 1200, {col: 'var(--c5)'}); }},
  ]};
L2A.refresh = {
  led: [[null, null], [null, null]], tot: () => ({c: 'none', e: `${n('l2_leak')} at idle, the chip's SRAM rail`}),
  cap: () => `Refresh? None: static cells hold while the rail is up; the cost is leakage, ${n('l2_leak67')} to ${n('l2_leak82')} on one card.`,
  steps: [
    {name: 'Static cells', where: 'cell', say: () => `No refresh: the cells hold while the rail is up, if they are SRAM; the cost is leakage, at most ${n('leak_mb')} at 80 °C`,
      run: async (tok, c) => { counter(c, 'no refresh', 'static storage (if SRAM)'); cellLeak(c, 'l3:l3.leakage'); await wait(tok, 1200); }},
    {name: 'No scrub, no sleep', where: 'shire', say: () => 'No background ECC scrub on this chip; deep sleep only for shires not in use; no wake-up delay measured',
      run: async (tok, c) => { lit(c, 'rail'); counter(c, `${nt('l2_leak')} at idle`, 'the chip\'s SRAM rail'); sayAt(c, 200, 470, ['no background scrub (a reserved bit)', `no wake-up: ${nt('l2_sleep')} after any idle`], {side: 'd'}); await wait(tok, 800); }},
  ]};
SCENES.l2.accOrder = [['load-hit', 'Load hit', 'Load'], ['rbuf-hit', 'Read-buffer hit', 'RB hit'], ['write-back', 'Write-back', 'Write'], ['miss', 'Miss → L3', 'Miss'], ['refresh', 'Refresh?', 'Refresh?']];
SCENES.l2.tour = [
  {name: 'The shire', path: ['shire'], panel: 'partition', hi: ['partition', 'banks'],
    cap: () => `The L2 is ${n('l2_kb')} of each shire cache: ${n('l2_sets')} of every sub-bank, between the scratchpad and the L3`,
    sub: () => 'The three are row ranges of the same macros (mode M0, the cards\' mode).'},
  {name: 'The bank', path: ['shire', 'bank'], panel: 'pipe', hi: ['pipe', 'reqq', 'rbuf'],
    cap: () => `A bank: a ${n('l2_reqq_adj')} request queue, an ${n('l2_rbuf_adj')} read buffer and a ${n('l2_stages')}-stage pipeline`,
    sub: () => 'The tags are read first, then one way\'s row: the data RAM\'s address includes the way.'},
  {access: 'load-hit', dive: true},
  {access: 'rbuf-hit'},
  {name: 'The sub-bank', path: ['shire', 'bank', 'sub'], panel: 'data', hi: ['tagram', 'stateram', 'data'],
    cap: () => `A sub-bank: a tag RAM, a two-port tag-state RAM and four ${n('l2_mdata_adj')} panels, each a compiled macro`,
    sub: () => 'The shaded band is the L2\'s rows; the rest is the scratchpad below and the L3 above.'},
  {name: 'The panel', path: ['shire', 'bank', 'sub', 'panel'], panel: 'trim', hi: ['trim', 'icg', 'geom'],
    cap: () => `A panel's trims default to the spec's ${n('l2_rm0n')} row; the SRAM rail measures ${n('l2_v')} mV on the die`,
    sub: () => 'Inside the macro (rows, columns, the column mux) nothing is documented: asked.'},
  {name: 'The cell', path: ['shire', 'bank', 'sub', 'panel', 'cell'], panel: 'cell', hi: ['cell'], play: (tok, c) => cellRead(tok, c, {half: true}),
    cap: () => 'The cell is drawn as a textbook 6T SRAM cell: the spec says SRAM, the lab lead said the chip is not using SRAM',
    sub: () => 'The bitcell is not documented. Which memories are not SRAM, and what cell these macros use, is the first ask.'},
  {name: 'Energy and asks', path: ['shire'], panel: 'energy', hi: ['rail', 'banks'],
    cap: () => `About ${n('l2_e_line')} per line read (${n('l2_e')}); on one card, ${n('l2_e_sram')} of an L2 hit was on the SRAM rail`,
    sub: () => 'How that splits between the arrays and the logic around them is asked, as are the per-stage cycles.'},
];

/* ================= accesses: each a list of steps, played on the clock ================= */
const LEVELS = ['l1', 'l2', 'l3', 'scp', 'dram'];
const AC = {k: null, i: 0, tok: {dead: true}, ctx: null, done: false, still: false};
let FOLLOW = true, FOLLOW_AUTO = false, DIVE = false, DIVE_USER = false, CAPACC = false;
const accOn = () => !!AC.k && !AC.done;
const HOLD = 2300;
const accDef = k => SC().access[k];
const stepsOf = k => accDef(k).steps;
const dataOf = k => DSTEPS[Z.lv][k];
const atView = path => !ZW && samePath(Z.path, path);
const accTitle = k => (SC().accOrder.find(a => a[0] === k) || [k, k])[1];
/* the access's camera: on the animation clock, so that Space stops it; drawing an end state it moves quickly (600 ms) */
async function cam(tok, path, cut, o) {
  if (!FOLLOW || atView(path)) return;
  const quick = cut || tok.ff;
  await goTo(path, Object.assign({clk: quick ? null : tok, keepFx: true, total: quick ? 600 : undefined, cap: 3200}, o || {}));   // a long chain of zooms takes at most 3.2 s
  alive(tok);
}
/* the scene's instance (which bank, sub-bank, row) follows the example address; the layers on the path are redrawn */
function rebuildPath() {
  if (ZW) return;
  Z.path.forEach((id, d) => buildLayer(d, id));
  scaleUI(); pipUpdate(); addrUI();
}
function applyInst() {
  const sc = SC(), before = JSON.stringify(sc.inst); sc.setInst();
  if (JSON.stringify(sc.inst) !== before) rebuildPath();
}
const accKick = k => (TOUR ? `Tour ${TOUR.i + 1} / ${TOUR.list.length} · ` : '') + `${SC().short} · ${accTitle(k)}`;
function startAccess(k, i, o) {
  o = o || {};
  const def = accDef(k); if (!def) return;
  i = clamp(i || 0, 0, def.steps.length - 1);
  AC.tok.dead = true; clearFx();
  const tok = {dead: false, k, ff: false, endDone: !!o.done};
  Object.assign(AC, {k, i, tok, done: false, still: !!o.still});
  SC().lastAcc = k;
  if (!o.still) CLK.on = true;
  accButtonsUI();
  if (!o.keepInst) applyInst();
  const ctx = AC.ctx = {k, tok, lv: Z.lv};
  liveCap(false);   // while an access plays, st-live alone announces each step
  setKick(accKick(k)); if (!TOUR) { dots(-1); CAPACC = true; }
  accPanel(k);
  renderBar(); playBtn();
  if (!o.noHash) setHash(Z.lv, k, o.still ? i + 1 : null);
  quiet(runFrom(tok, ctx, i, !!o.still, !!o.quick));
}
const liveCap = on => ['cap', 'cap-k'].forEach(id => { if (on) $(id).setAttribute('aria-live', 'polite'); else $(id).removeAttribute('aria-live'); });
async function runFrom(tok, ctx, i, still, quick) {
  const sts = stepsOf(ctx.k);
  showStep(ctx, i);
  if (FOLLOW) await cam(tok, pathTo(sts[i].where), still || quick);   // a step the reader picked: a short camera move
  for (let j = i; j < sts.length; j++) {
    if (j !== i) showStep(ctx, j);
    scaleUI();
    if (still) { tok.ff = true; FFTOK = tok; }
    await playStep(tok, ctx, j);
    if (still) {
      tok.ff = false;
      if (tok.endDone && j === sts.length - 1) { AC.still = false; AC.done = true; } else AC.still = true;
      renderBar(); playBtn(); return;
    }
    if (j < sts.length - 1) await wait(tok, sts[j].hold != null ? sts[j].hold : HOLD);
  }
  if (AC.tok === tok) { AC.done = true; renderBar(); playBtn(); }
}
const stageLine = html => { const s = String(html || ''); return /^[a-z0-9]{1,4}[:( …]/.test(s) ? s : s.charAt(0).toUpperCase() + s.slice(1); };
function showStep(ctx, j) {
  const sts = stepsOf(ctx.k), st = sts[j];
  AC.i = j; renderBar(); setCap(stageLine(st.say ? st.say(ctx) : st.name)); sub(accDef(ctx.k).cap()); ledgerOn(j); stepBox(ctx, j);
  $('st-live').textContent = `Step ${j + 1} of ${sts.length}: ${st.name}`;
}
function setCtx(ctx) { const d = Z.path.length - 1; ctx.d = d; ctx.fx = FX[d]; ctx.ap = AP[d]; }
async function playStep(tok, ctx, j) {
  const st = stepsOf(ctx.k)[j], path = pathTo(st.where);
  ctx.step = j; ledgerOn(j);
  if (FOLLOW) await cam(tok, path);
  alive(tok);
  clearFx(); unsay(ctx);
  if (atView(path)) { setCtx(ctx); await st.run(tok, ctx); }
  else {
    // the reader sits at one of the step's circuit scales: the circuit plays there
    const dv = (st.dive || []).find(id => atView(pathTo(id)));
    if (dv) { setCtx(ctx); await st.deep[dv](tok, ctx); return; }
    return markStep(tok, ctx, st, path);
  }
  if (DIVE && FOLLOW && st.dive && st.dive.length && !tok.ff) {
    // the camera passes the intermediate scales and plays only the deepest circuit, then comes back up: about 5 s in all
    await wait(tok, 200);
    const id = st.dive[st.dive.length - 1];
    await cam(tok, pathTo(id), false, {cap: 1100}); alive(tok);
    clearFx(); unsay(ctx); setCtx(ctx);
    const dl = T(ctx.fx, FR.x + FR.w - 22, FR.y + 68, `dive · step ${j + 1}: ${st.name}`, 't-smb halo', 'end'); subYield(dl); fadeIn(dl);
    tok.speed = 1.7;
    try { await st.deep[id](tok, ctx); } finally { tok.speed = 1; }
    alive(tok);
    await wait(tok, 500);
    await cam(tok, path, false, {cap: 900}); alive(tok);
    // the step's end state again, at its own scale
    clearFx(); unsay(ctx); setCtx(ctx);
    tok.ff = true; FFTOK = tok; await st.run(tok, ctx); tok.ff = false;
  }
}
/* a step at a scale the camera is not showing: its place is marked, with its name */
async function markStep(tok, ctx, st, path) {
  const d = Z.path.length - 1, fx = FX[d], ap = AP[d];
  setCtx(ctx);
  let p = null, where = '';
  const prefix = path.length > Z.path.length && samePath(path.slice(0, Z.path.length), Z.path);
  if (prefix) {
    const child = path[Z.path.length], g = ap.zg[child];
    if (g && g._box) p = ctr(g._box);
    where = `inside the ${NODE(child).name.toLowerCase()}`;
  } else { p = {x: FR.x + 90, y: FR.y + 120}; where = `at the ${NODE(st.where).name.toLowerCase()} scale`; }
  if (p && fx) {
    const g = E('g', {}, fx);
    callout(g, p.x, p.y, [{t: `Step ${ctx.step + 1}: ${st.name}`}, {t: where}, {t: 'C follows it'}], {side: p.x > 460 ? 'l' : 'r', fs: 21});
    for (let r = 0; r < 2 && !tok.ff; r++) await pulse(tok, g, p, 1300, 'var(--c2)', 52);
  }
  await wait(tok, st.dur || 2400);
}
function killAccess() { AC.tok.dead = true; clearFx(); }
function stopAccess(keepCap) {
  const had = !!AC.k;
  killAccess(); AC.k = null; AC.done = false; AC.still = false;
  applyInst();   // a level whose instance follows the access (the scratchpad's remote target) goes back to its own
  accButtonsUI(); renderBar(); playBtn(); liveCap(true);
  if (!TOUR && CAPACC && !keepCap) resetCap();
  if (had && !keepCap && !TOUR) { showPart(SEL ? SEL._key : 'overview', SEL && SEL._ctx); viewHash(); }
}
/* the address of the view without an access: #<level>[/<scale>] */
function viewHash() { if (!AC.k && !TOUR) setHash(Z.lv, null, null, Z.path.length > 1 ? Z.path[Z.path.length - 1] : null); }
function restartStep() { if (AC.k) startAccess(AC.k, AC.i, {still: AC.still || !CLK.on, keepInst: true, noHash: true}); }
function setFollow(on, auto) {
  FOLLOW = on; FOLLOW_AUTO = !on && !!auto;
  $('btn-follow').setAttribute('aria-pressed', String(on));
  if (on && accOn()) { const w = pathTo(stepsOf(AC.k)[AC.i].where); if (!atView(w)) restartStep(); }
}
function setDive(on, auto) {
  if (!auto) DIVE_USER = on;
  DIVE = on; $('btn-dive').setAttribute('aria-pressed', String(on));
  renderBar();
}
function goStep(i) {
  if (!AC.k) return false;
  const nst = stepsOf(AC.k).length; if (i < 0 || i >= nst) return false;
  if (FOLLOW_AUTO) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); }
  startAccess(AC.k, i, {still: !CLK.on || AC.still, keepInst: true, noHash: !!TOUR, quick: true});
  if (!CLK.on || AC.still) setHash(Z.lv, AC.k, i + 1);
  return true;
}
/* ---- the access's panel: this step (its block, action, numbers and the circuit elements that switch), the ledger ---- */
function stepBox(ctx, j) {
  const box = $('stepbox'); if (!box) return;
  const ds = dataOf(ctx.k).steps[j], st = stepsOf(ctx.k)[j];
  if (!ds) { box.innerHTML = ''; return; }
  const fk = (ds.facts || [])[0];
  const circ = (ds.circuit || []).map(c => `<li><span class="el">${esc(c.el)}</span>${c.does ? ': ' + esc(c.does) : ''} <span class="kd ${c.kind}">${KLAB[c.kind]}</span>${c.kind_note ? ` <span class="cav">${esc(c.kind_note)}</span>` : ''}</li>`).join('');
  const kindF = fk && F[fk] ? kindChip(F[fk]) : `<span class="kd ${ds.kind}">${KLAB[ds.kind]}</span>`;
  box.innerHTML = `<div class="step"${fk ? ` data-f="${fk}" data-src="1"` : ''}><p class="blk">Step ${j + 1} of ${stepsOf(ctx.k).length} · ${esc(ds.block || st.name)}</p>`
    + (ds.stage ? `<p class="small">${esc(ds.stage)}</p>` : '')
    + `<p>${esc(ds.action)}</p>`
    + (ds.latency ? `<p><b>Time:</b> ${esc(ds.latency)}</p>` : '') + (ds.energy ? `<p><b>Energy:</b> ${esc(ds.energy)}</p>` : '')
    + `<p class="meta">${kindF}${fk ? ` <span class="fid">${esc(F[fk].id)}</span>` : ''}</p>`
    + (!fk && ds.source ? `<p class="small"><b>Source:</b> ${esc(ds.source)}</p>` : '')
    + (circ ? `<p class="pn-h">What switches</p><ul class="circ">${circ}</ul>` : '')
    + (st.dive && st.dive.length ? `<p class="small">${DIVE ? 'Dive is on: the camera goes down to the transistors.' : 'Press V (Dive) to go down to the transistors on this step.'}</p>` : '')
    + (st.handoff ? `<div class="pn-act"><button type="button" class="st-btn" data-act="handoff">${esc(st.handoff.label)} →</button></div>` : '')
    + '</div>';
}
function legTable(k) {
  const a = accDef(k), sts = a.steps, led = (typeof a.led === 'function' ? a.led() : a.led) || sts.map(() => [null, null]);
  const rows = sts.map((s, i) => ({name: s.name, c: led[i] ? led[i][0] : null, e: led[i] ? led[i][1] : null}));
  const spans = col => { const out = {}; let i = 0; while (i < rows.length) { if (rows[i][col] != null) { out[i] = {n: 1, v: rows[i][col]}; i++; } else { let j = i; while (j < rows.length && rows[j][col] == null) j++; out[i] = {n: j - i, v: null}; i = j; } } return out; };
  const sc = spans('c'), se = spans('e');
  const askA = id => { const a = ASKS.find(x => x.id === id); return `<a href="#q-${esc(id)}" title="${esc(a ? a.title : '')}">asked ↓</a>`; };
  const ns = (ask, nr) => nr > 1 || ask ? `not split${ask ? `: ${askA(ask)}` : ''}` : '—';
  let h = `<table class="legs"><thead><tr><th>#</th><th>Step</th><th class="num">cycles</th><th class="num">energy</th></tr></thead><tbody>`;
  rows.forEach((r, i) => {
    h += `<tr class="todo" data-leg="${i}"><td>${i + 1}</td><td>${esc(r.name)}</td>`;
    if (sc[i]) h += sc[i].v != null ? `<td class="num">${sc[i].v}</td>` : `<td class="ns" rowspan="${sc[i].n}">${ns(a.ask && a.ask.c, sc[i].n)}</td>`;
    if (se[i]) h += se[i].v != null ? `<td class="num">${se[i].v}</td>` : `<td class="ns" rowspan="${se[i].n}">${ns(a.ask && a.ask.e, se[i].n)}</td>`;
    h += '</tr>';
  });
  const t = a.tot ? a.tot() : null;
  if (t) h += `<tr class="tot"><td></td><td>whole access</td><td>${t.c || ''}</td><td>${t.e || ''}</td></tr>`;
  return h + '</tbody></table>';
}
function ledgerOn(i) {
  let on = null;
  document.querySelectorAll('#pn-body tr[data-leg]').forEach(tr => { const k = +tr.dataset.leg; tr.className = k < i ? '' : k === i ? 'on' : 'todo'; if (k === i) on = tr; });
  if (on) pnReveal(on);
}
function accPanel(k) {
  const a = accDef(k), d = dataOf(k);
  const keys = [...new Set(d.steps.flatMap(s => s.facts || []))];
  const unk = Object.keys(F).filter(f => F[f].level === Z.lv && F[f].kind === 'unknown' && ASKOF[f] && a.ask && Object.values(a.ask).includes(ASKOF[f].id));
  panel(`<p class="pn-kick">${esc(SC().title)} · access</p><p class="pn-title">${esc(accTitle(k))}</p><p class="pn-what">${a.cap()}</p>`
    + `<div id="stepbox"></div>`
    + `<p class="pn-h">The steps, their cycles and energy (where a fact gives them)</p>` + legTable(k)
    + asksBlock(unk) + factsBlock(keys, 'The steps\' facts'));
}

/* ================= the chip, shared by the L3, the scratchpad and the DRAM: the measured logical map of the mesh
   (the chip tour's layout, D.layout: marty1885's map, confirmed by latency on three cards, and the memory shires where
   a DRAM-latency fit puts them, one hop outside the grid). x runs across, y down; memory shires 0-3 sit above the grid
   (y = -1) and 4-7 below it (y = 6). On the die this map is turned a quarter (the chip tour draws the die view). ======= */
const LAYM = D.layout;
const CELLS = [], BYLOG = {}, SHC = {}, MSC = {};
LAYM.mesh.forEach((row, y) => row.forEach((v, x) => {
  const c = {lx: x, ly: y, type: typeof v === 'number' ? 'cshire' : 'grey', id: typeof v === 'number' ? v : null};
  if (c.type === 'grey') c.name = LAYM.mesh_grey_labels[`(${x},${y})`] || 'no compute shire';
  CELLS.push(c); BYLOG[x + ',' + y] = c; if (c.type === 'cshire') SHC[c.id] = c;
}));
LAYM.memshires.forEach(m => { const c = {lx: m.pos[0], ly: m.pos[1], type: 'memshire', id: m.id, tie: !!m.tie_break}; CELLS.push(c); BYLOG[c.lx + ',' + c.ly] = c; MSC[m.id] = c; });
const ckey = c => c.type === 'cshire' ? 's' + c.id : c.type === 'memshire' ? 'm' + c.id : 'g' + c.lx + '_' + c.ly;
const hopsC = (a, b) => Math.abs(a.lx - b.lx) + Math.abs(a.ly - b.ly);
/* a route on the map: x first, then y, as the chip tour draws it (the order is not documented: l3.route, asked) */
function xyRoute(a, b, xFirst) {
  const out = [a]; let x = a.lx, y = a.ly;
  const step = (dx, dy) => { x += dx; y += dy; const c = BYLOG[x + ',' + y]; if (c) out.push(c); return !!c; };
  const X = () => { while (x !== b.lx) if (!step(Math.sign(b.lx - x), 0)) return false; return true; };
  const Y = () => { while (y !== b.ly) if (!step(0, Math.sign(b.ly - y))) return false; return true; };
  return (xFirst ? X() && Y() : Y() && X()) ? out : null;
}
const routeC = (a, b) => xyRoute(a, b, true) || xyRoute(a, b, false) || [a, b];
/* the chip-wide mean hop count of a line's home from a requester (the average over the 32 homes) */
const meanHops = r => Object.values(SHC).reduce((s, c) => s + hopsC(r, c), 0) / 32;
const MAPF = 'chip:mesh.logical-map chip:L40';

/* The map, cell size C from (X0, Y0). o.tile(c) decorates a tile: {key, ctx, child, cur, hi, sub, label}. The anchor
   points go to ap.P[ckey] (the mesh stop) and ap.B[ckey] (the tile). o.pkg: the LPDDR4X packages beyond the memory
   shires, dashed, since which two memory shires share one is not documented. */
function chipMap(L, ap, o) {
  const C = o.C, X0 = o.X0, Y0 = o.Y0, IN = 3;
  ap.P = {}; ap.B = {}; ap.C = C;
  CELLS.forEach(c => { const x = X0 + c.lx * C, y = Y0 + (c.ly + 1) * C; ap.B[ckey(c)] = {x: x + IN, y: y + IN, w: C - 2 * IN, h: C - 2 * IN}; ap.P[ckey(c)] = {x: x + C * 0.64, y: y + C * 0.66}; });
  if (o.pkg) {
    [[0, 1], [2, 3], [4, 5], [6, 7]].forEach(pr => {
      const a = ap.B['m' + pr[0]], b = ap.B['m' + pr[1]], top = MSC[pr[0]].ly < 0;
      const y = top ? a.y - o.pkg - 12 : a.y + a.h + 12, x = a.x, w = b.x + b.w - a.x;
      const g = part(L, 'pkg', x, y, w, o.pkg, COL.store, 'LPDDR4X', {kind: 'unknown', q: false, ctx: {ms: pr}, fo: 0.1, ty: o.pkg / 2 - 2, center: true, tcls: 't-smb', label: `An LPDDR4X package of four 16-bit channels, drawn beside memory shires ${pr[0]} and ${pr[1]}: the pairing is not documented`});
      T(g, x + w / 2, y + o.pkg / 2 + 18, 'pairing ?', 't-sm', 'middle', 'dram:dram.topo.packages dram:dram.topo.pkg-pairing');
      pr.forEach(m => { const B0 = ap.B['m' + m]; [0.35, 0.65].forEach(f => S(E('line', {x1: B0.x + B0.w * f, x2: B0.x + B0.w * f, y1: top ? y + o.pkg : B0.y + B0.h, y2: top ? B0.y : y}, g), {stroke: 'var(--c3)', strokeWidth: 3})); });
      ap.pkgBox = ap.pkgBox || {}; ap.pkgBox[pr[0]] = ap.pkgBox[pr[1]] = {x, y, w, h: o.pkg};
    });
  }
  // the links and the stops (drawn under the tiles, which take the clicks)
  const LG = ap.LG = E('g', {class: 'dimmable', 'pointer-events': 'none'}, L);
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hopsC(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly)) { const p = ap.P[ckey(a)], q = ap.P[ckey(b)]; S(E('line', {x1: p.x, y1: p.y, x2: q.x, y2: q.y}, LG), {stroke: 'var(--c4)', strokeWidth: 3.5, strokeOpacity: 0.6}); }
  }));
  CELLS.forEach(c => { const p = ap.P[ckey(c)]; S(E('circle', {cx: p.x, cy: p.y, r: 4.5}, LG), {fill: 'var(--c4)'}); });
  // the tiles
  CELLS.forEach(c => {
    const b = ap.B[ckey(c)], d = (o.tile && o.tile(c)) || {};
    const col = c.type === 'cshire' ? COL.logic : c.type === 'memshire' ? COL.store : 'var(--ink-2)';
    const lab = c.type === 'cshire' ? `Shire ${c.id}` : c.type === 'memshire' ? `Memory shire ${c.id}` : `A cell without a compute shire (${c.name})`;
    const g = part(L, d.key || (c.type === 'cshire' ? 'shire' : c.type === 'memshire' ? 'memshire' : 'grey'), b.x, b.y, b.w, b.h, col, '',
      {ctx: Object.assign({id: c.id, cell: c}, d.ctx || {}), child: d.child || null, cur: d.cur, fo: d.fo != null ? d.fo : c.type === 'grey' ? 0.04 : 0.1, label: d.label || lab, rx: 5});
    if (c.type === 'cshire') T(g, b.x + 7, b.y + 22, String(c.id), d.hi ? 't-labb' : 't-lab');
    // a memory shire's 'MS' and number, stacked above and left of its mesh stop: the links cross the tile at the stop's
    // height and, in the bottom row, come down to the stop from the tile above, so neither line runs through the text
    else if (c.type === 'memshire') { const ny = ap.P[ckey(c)].y - 4; T(g, b.x + 7, ny - 17, 'MS', 't-smb'); T(g, b.x + 7, ny, String(c.id), d.hi ? 't-labb' : 't-smb'); }
    (d.marks || []).forEach((m, i) => mapMark(g, b, m, i));
    if (d.hi) S(E('rect', {x: b.x - 1, y: b.y - 1, width: b.w + 2, height: b.h + 2, rx: 6, 'pointer-events': 'none'}, g), {fill: 'none', stroke: 'var(--c2)', strokeWidth: 4});
  });
}
/* a route drawn on the map: dashed, over the links and under the tiles, so that the tiles' numbers and letters stay on top */
function routeLine(L, ap, P) {
  const e = S(E('path', {d: 'M' + P.map(p => `${p.x},${p.y}`).join(' L'), fill: 'none', 'pointer-events': 'none'}, L), {stroke: 'var(--c2)', strokeWidth: 4, strokeDasharray: '10 7', strokeLinecap: 'round'});
  if (ap.LG && ap.LG.parentNode === L) ap.LG.after(e);
  return e;
}
/* a letter on a tile (R the requester, H the home, M the memory shire, T the target): a filled pill with its letter */
function mapMark(g, b, m, i) {
  const x = b.x + b.w - 15 - i * 28, y = b.y + b.h - 15;
  S(E('circle', {cx: x, cy: y, r: 12, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', stroke: 'var(--page)', strokeWidth: 2});
  S(T(g, x, y + 6, m, 't-smb', 'middle'), {fill: 'var(--page)'});
}
/* the stops of a route, as points */
const routeP = (ap, a, b) => routeC(a, b).map(c => ap.P[ckey(c)]);
/* a packet along a route, a counter of hops beside it */
async function hopTravel(tok, c, a, b, o) {
  o = o || {};
  const cells = routeC(a, b), P = cells.map(x => c.ap.P[ckey(x)]), n0 = cells.length - 1;
  const pk = packet(c.fx, o.col || 'var(--c2)', o.r || 11); at(pk, P[0]);
  if (!n0) { await pulse(tok, c.fx, P[0], 900, o.col); return pk; }
  // the running count goes after the frame's counter (top right), where it covers no tile's number
  const ct = o.label && c.ctr && c.ctr.isConnected ? c.ctr.querySelector('text') : null;
  const lab = ct ? E('tspan', {class: 't-smb', dx: 10}, ct) : null;
  for (let k = 1; k <= n0; k++) {
    await travel(tok, c.fx, pk, [P[k - 1], P[k]], o.per || 380, {col: o.col, w: o.w || 6, linear: true, settle: k === n0});
    if (lab) { lab.textContent = '· ' + o.label(k, n0); ctrFit(c); }
  }
  return pk;
}

/* ---- one mesh hop, up close (the L3 and the remote scratchpad): the requester bank's to_l3 master, the voltage and
   clock crossing into the mesh, a router, one link, the next router, the far shire's L3-slave port. The numbers are
   ET's; the router is a textbook one; its pipeline is unknown (asked). o: {title, sub, lane, laneF, to} ---- */
function buildHop(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, subf: 'l3:l3.ports l3:l3.hop', col: 'var(--c4)',
    tags: [['unknown', '? router pipeline · asked'], ['generic', 'GENERIC router'], ['documented', 'ports, rails, numbers']]});
  railBand(L, -150, 12, 1228, 176, 'pat-hv', 'The Shire Channel');
  T(L, -136, 180, `Shire Channel · arrays ${nt('l3_sram_v')} · logic rail asked · ${nt('l3_clk')}`, 't-sm halo', 'start', nf('l3_sram_v') + ' l3:u.rail-of-logic ' + nf('l3_clk'));
  railBand(L, -150, 200, 1228, 300, 'pat-mesh', 'The mesh rail');
  T(L, -136, 490, `mesh rail: ${nt('l3_mesh_v')}, ${nt('l3_noc')} (measured)`, 't-sm halo', 'start', nf('l3_mesh_v'));
  // the requester's side, in the Shire Channel
  part(L, 'bankR', -136, 26, 200, 130, COL.logic, 'bank ' + (o.bank != null ? o.bank : ''), {sub: ['request queue:', 'the miss leaves', 'on to_l3']});
  part(L, 'tol3', 90, 26, 300, 130, COL.net, 'to_l3 master', {sub: [{t: `lane = ${o.lane}`, f: o.laneF || 'l3:l3.lane'}, {t: o.laneNote || '4 per shire', f: o.laneF || 'l3:l3.lane'}, {t: 'ET-Link → AXI read (AR)', f: 'l3:l3.flits'}]});
  const gx = part(L, 'vcdown', 416, 26, 300, 130, COL.xing, 'VC FIFO', {sub: [{t: 'level shifters, down to 485 mV', f: 'l3:l3.ports l3:g.crossing l3:u.rail-of-logic'}, {t: '2-flop synchroniser → 400 MHz', f: 'l3:l3.ports l3:g.crossing'}]});
  ap.vcBox = {x: 416, y: 26, w: 300, h: 130};
  part(L, 'slave', 744, 26, 334, 130, COL.xing, o.to || 'far shire: L3-slave port', {sub: [{t: 'VC FIFO back up to the', f: 'l3:l3.ports'}, {t: 'Shire Channel\'s rail', f: 'l3:l3.ports l3:u.rail-of-logic'}, {t: '4 ports of 512 bits', f: 'l3:l3.ports'}]});
  wire(L, [[64, 142], [90, 142]]); wire(L, [[390, 142], [416, 142]]);
  // the mesh: a router, a link, the next router
  const gr = part(L, 'router', -136, 214, 380, 262, COL.net, 'router (one of 9 layers)', {kind: 'generic', f: 'chip:L105'});
  [['input VC buffers', 272], ['route · VC and switch allocators', 318], ['crossbar: 8 ports', 364], ['output drivers → link', 410]].forEach(([t, y]) => {
    S(E('rect', {x: -118, y: y - 22, width: 344, height: 34, rx: 4, 'pointer-events': 'none'}, gr), {fill: 'var(--surface)', stroke: 'var(--c4)', strokeWidth: 1.25, strokeDasharray: '2 5'});
    T(gr, -106, y + 1, t, 't-sm');
  });
  T(gr, -118, 452, '4 VC slots a port; parity, no ECC', 't-sm', 'start', 'chip:L105');
  ap.router = {x: 244, y: 345};
  const gl = comp(L, 'link', {}, `One mesh link: a bundle of wires broken by repeaters, about ${nt('l3_hopmm')} per hop`);
  const LX0 = 256, LX1 = 700, LY = 345;
  E('line', {class: 'w bus', x1: LX0, y1: LY, x2: LX1, y2: LY}, gl);
  ap.reps = [];
  for (let k = 0; k < 5; k++) {
    const x = LX0 + 44 + k * 86;
    E('path', {class: 'gate', d: `M${x - 13},${LY - 15} L${x + 13},${LY} L${x - 13},${LY + 15} Z`}, gl);
    ap.reps.push({x, y: LY});
  }
  T(gl, (LX0 + LX1) / 2, LY - 30, `one hop ≈ ${nt('l3_hopmm')} of wire`, 't-smb', 'middle', nf('l3_hopmm'));
  T(gl, (LX0 + LX1) / 2, LY + 42, 'repeaters (inverter pairs), generic', 't-sm', 'middle', 'l3:g.router');
  gl._box = {x: LX0, y: LY - 50, w: LX1 - LX0, h: 100};
  E('rect', {class: 'ring', x: LX0 - 5, y: LY - 55, width: LX1 - LX0 + 10, height: 110, rx: 10}, gl);
  gl.setAttribute('data-child', 'rep');
  ap.repBox = {x: ap.reps[2].x - 20, y: LY - 20, w: 40, h: 40};
  BAP.zg.rep = gl;
  const gr2 = part(L, 'router2', 700, 250, 180, 190, COL.net, 'next router', {kind: 'generic', sub: ['4 NoC cycles a', 'hop each way', '', '', '(derived)']});
  part(L, 'more', 900, 250, 178, 190, COL.net, '… hops', {kind: 'generic', sub: [{t: `${nt('l3_hopcyc')} per hop,`, f: nf('l3_hopcyc')}, {t: `${nt('l3_hopns')} round trip`, f: nf('l3_hopns')}]});
  wire(L, [[880, 345], [900, 345]]);
  // the packet's way: under the parts' text rows, out of the router's right side onto the link, round the far side
  ap.hopP = [{x: 64, y: 142}, {x: 240, y: 142}, {x: 566, y: 142}, {x: 566, y: 196}, {x: 252, y: 196}, {x: 252, y: 345}, {x: LX0, y: LY}, {x: LX1, y: LY}, {x: 790, y: 345}, {x: 990, y: 345}, {x: 1085, y: 345}, {x: 1085, y: 142}, {x: 910, y: 142}];
  // the flits
  const gf = comp(L, 'flits', {}, 'What crosses a hop: a request of about 80 bits; the reply carries the 512-bit line');
  T(gf, -136, 536, 'what crosses', 't-labb');
  S(E('rect', {x: 40, y: 518, width: 80, height: 26, rx: 3}, gf), {fill: 'var(--c4)', fillOpacity: 0.3, stroke: 'var(--c4)', strokeWidth: 1.5});
  T(gf, 130, 537, `request (AR): ${nt('l3_req_bits')}`, 't-sm', 'start', nf('l3_req_bits'));
  S(E('rect', {x: 40, y: 554, width: 512, height: 26, rx: 3}, gf), {fill: 'var(--c4)', fillOpacity: 0.3, stroke: 'var(--c4)', strokeWidth: 1.5});
  S(E('rect', {x: 552, y: 554, width: 16, height: 26, rx: 2}, gf), {fill: 'var(--c7)', fillOpacity: 0.4, stroke: 'var(--c7)', strokeWidth: 1.25});
  S(E('rect', {x: 568, y: 554, width: 30, height: 26, rx: 2}, gf), {fill: 'none', stroke: 'var(--warn)', strokeWidth: 1.5, strokeDasharray: '4 3'});
  T(gf, 612, 566, `reply: ${nt('l3_reply')}`, 't-sm', 'start', nf('l3_reply'));
  T(gf, 612, 586, '+ RID, RRESP, RLAST; a header of unknown width', 't-sm', 'start', 'l3:l3.flits');
  gf._box = {x: -136, y: 512, w: 1214, h: 80};
  E('rect', {class: 'ring', x: -141, y: 507, width: 1224, height: 90, rx: 10}, gf);
  // the energy of a hop, and what is unknown
  part(L, 'hopE', -136, 604, 600, 84, COL.aux, 'a 64 B reply over one hop', {sub: [{t: `≈ ${nt('l3_hop69')} on the mesh rail (derived); ${nt('l3_hop47')} measured`, f: nf('l3_hop69') + ' ' + nf('l3_hop47')}]});
  part(L, 'nochop', 480, 604, 598, 84, 'var(--warn)', 'unknown: the router pipeline per hop', {kind: 'unknown', sub: [{t: 'which of the 9 layers, flit width, dimension order', f: 'l3:u.noc-hop'}]});
}
/* the request's (or the reply's) way through the hop drawing */
async function hopPlay(tok, c, o) {
  o = o || {};
  const P = c.ap.hopP, segs = [[[0, 3], ['bankR', 'tol3', 'vcdown']], [[3, 8], ['router', 'link', 'router2']], [[8, 12], ['more', 'slave']]];
  const order = o.back ? segs.slice().reverse() : segs;
  let pk = null;
  for (const [[a, b], keys] of order) {
    lit(c, keys, {noRing: keys.length > 2});
    if (keys.includes('link')) c.ap.reps.forEach(r => ringAround(c.fx, {x: r.x - 16, y: r.y - 18, w: 32, h: 36}, {fo: 0.25, sw: 2.5}));
    const pts = P.slice(a, b + 1); if (o.back) pts.reverse();
    if (!pk) { pk = packet(c.fx, o.col || 'var(--c2)', 11); at(pk, pts[0]); }
    await travel(tok, c.fx, pk, pts, keys.includes('link') ? 1600 : 1100, {col: o.col});
  }
  return pk;
}

/* ---- a link bit and a crossing, transistor by transistor (generic circuits; ET numbers only where a fact gives them):
   a repeater pair driving a wire, and the level shifter that lifts a mesh signal back to the Shire Channel ---- */
function buildWire(L, ap, o) {
  frame(L, {title: o.title, sub: o.sub, col: 'var(--c4)', tags: [['generic', 'GENERIC circuits'], ['documented', 'rails, energy per bit']]});
  // repeater 1: a CMOS inverter on the mesh rail
  const inv = (key, x, lab) => {
    const g = comp(L, key, {}, lab + ': a CMOS inverter, a PMOS and an NMOS; generic');
    E('line', {class: 'rail', x1: x - 22, y1: 40, x2: x + 22, y2: 40}, g);
    const p = mosV(g, x, 76, {p: true, lead: 26}), q = mosV(g, x, 176, {lead: 26}), gx0 = p.gate.x;
    wire(g, [[x, 46], [x, 40]]); wire(g, [[gx0, 76], [gx0, 176]]); wire(g, [[x, 106], [x, 146]]);
    E('line', {class: 'rail', x1: x - 22, y1: 212, x2: x + 22, y2: 212}, g); wire(g, [[x, 206], [x, 212]]);
    g._box = {x: gx0 - 8, y: 32, w: x + 30 - gx0, h: 188};
    E('rect', {class: 'ring', x: gx0 - 13, y: 27, width: x + 40 - gx0, height: 198, rx: 8}, g);
    return {g, p, q, in: {x: gx0, y: 126}, out: {x, y: 126}};
  };
  const r1 = inv('rep1', -40, 'Repeater, first inverter'), r2 = inv('rep2', 560, 'Repeater, next inverter');
  netLab(L, -62, 34, `VDD mesh ${nt('l3_mesh_v')}`, 'start', nf('l3_mesh_v'));
  wire(L, [[-150, 126], [r1.in.x, 126]]); netLab(L, -150, 116, 'in', 'start');
  // the wire: a line with its capacitance drawn as three capacitors to ground
  const gw = comp(L, 'wireC', {}, 'The wire between two repeaters: its capacitance must be charged on every 0-to-1 transition; generic');
  E('line', {class: 'w bus', x1: r1.out.x, y1: 126, x2: r2.in.x, y2: 126}, gw);
  ap.caps = [];
  [140, 280, 420].forEach(x => {
    jn(gw, x, 126); wire(gw, [[x, 126], [x, 160]]);
    E('line', {class: 'rail', x1: x - 18, y1: 160, x2: x + 18, y2: 160}, gw); E('line', {class: 'rail', x1: x - 18, y1: 170, x2: x + 18, y2: 170}, gw);
    wire(gw, [[x, 170], [x, 196]]); gnd(gw, x, 206);
    ap.caps.push({x, y: 126});
  });
  T(gw, 280, 100, 'a few hundred µm of wire: its capacitance C', 't-sm', 'middle', 'l3:g.wire-energy');
  gw._box = {x: 20, y: 90, w: 500, h: 130};
  E('rect', {class: 'ring', x: 15, y: 85, width: 510, height: 140, rx: 10}, gw);
  wire(L, [[r2.out.x, 126], [640, 126]]); netLab(L, 646, 132, '→ next');
  const ge = part(L, 'bitE', 740, 30, 338, 190, COL.aux, 'energy per bit', {sub: [{t: 'a 0 → 1 costs ≈ C · V²', f: 'l3:g.wire-energy'}, {t: 'a 0 after a 0: nothing', f: 'l3:g.wire-energy'}, {t: `${nt('l3_fj')} per random`, f: nf('l3_fj')}, {t: 'bit and mm, mesh rail (derived)', f: nf('l3_fj')}]});
  ap.rep = {r1, r2};
  // the level shifter: the reply lifted from the mesh rail to the Shire Channel (cross-coupled PMOS over an NMOS pair)
  S(E('line', {x1: -150, y1: 262, x2: 1078, y2: 262}, L), {stroke: 'var(--border)', strokeWidth: 1.5});
  T(L, -150, 296, 'at the far shire: the reply is lifted back to the Shire Channel', 't-labb');
  const gi = comp(L, 'lsin', {}, 'The input inverter, on the mesh rail; generic');
  E('line', {class: 'rail', x1: -80, y1: 330, x2: 40, y2: 330}, gi); netLab(gi, -86, 336, 'VDDL', 'end');
  const ip = mosV(gi, 0, 366, {p: true, lead: 24}), inn = mosV(gi, 0, 446, {lead: 24}), IG = ip.gate.x;
  wire(gi, [[0, 336], [0, 330]]); wire(gi, [[IG, 366], [IG, 446]]); wire(gi, [[0, 396], [0, 416]]); gnd(gi, 0, 486);
  wire(gi, [[-130, 406], [IG, 406]]); jn(gi, IG, 406); netLab(gi, -134, 412, 'IN', 'end'); netLab(gi, 8, 400, 'INB');
  gi._box = {x: -150, y: 320, w: 200, h: 180};
  const gs = comp(L, 'ls', {}, 'The level shifter: a cross-coupled PMOS pair on the high rail over an NMOS differential pair; generic');
  E('line', {class: 'rail', x1: 250, y1: 330, x2: 560, y2: 330}, gs); netLab(gs, 566, 336, 'VDDH (asked)', 'start', 'l3:u.rail-of-logic');
  const p1 = mosV(gs, 320, 366, {p: true, flip: true, lead: 26}), p2 = mosV(gs, 500, 366, {p: true, lead: 26});
  const n1 = mosV(gs, 320, 486, {lead: 26}), n2 = mosV(gs, 500, 486, {flip: true, lead: 26});
  wire(gs, [[320, 336], [320, 330]]); wire(gs, [[500, 336], [500, 330]]);
  wire(gs, [[320, 396], [320, 456]]); wire(gs, [[500, 396], [500, 456]]);
  E('line', {class: 'rail', x1: 300, y1: 526, x2: 520, y2: 526}, gs); wire(gs, [[320, 516], [320, 526]]); wire(gs, [[500, 516], [500, 526]]); netLab(gs, 380, 548, 'GND');
  const g1 = p1.gate.x, g2 = p2.gate.x, n1g = n1.gate.x, n2g = n2.gate.x;
  E('path', {class: 'w', d: `M${g1},366 V412 H${g2 - 7} A7,7 0 0 1 ${g2 + 7},412 H500`}, gs);
  E('path', {class: 'w', d: `M${g2},366 V432 H320`}, gs);
  jn(gs, 500, 412); jn(gs, 320, 432);
  netLab(gs, 312, 426, 'A', 'end'); netLab(gs, 508, 472, 'B');
  E('path', {class: 'w', d: `M-110,406 V580 H${n1g} V486`}, gs);
  E('path', {class: 'w', d: `M0,406 H80 V562 H${n1g - 7} A7,7 0 0 1 ${n1g + 7},562 H${n2g} V486`}, gs);
  jn(gs, -110, 406); jn(gs, 0, 406);
  wire(gs, [[500, 442], [680, 442]]); netLab(gs, 686, 448, 'OUT');
  gs._box = {x: 250, y: 320, w: 480, h: 270};
  const gy = part(L, 'sync', 770, 330, 308, 160, COL.xing, 'then a 2-flop synchroniser', {sub: [{t: 'into the shire clock', f: 'l3:l3.ports'}, {t: '2–3 receiving cycles (generic)', f: 'l3:g.crossing'}]});
  ap.ls = {ip, inn, p1, p2, n1, n2};
  ap.wave = {x: -150, y: 596, w: 700, h: 98};
  T(L, 580, 640, 'the ET RTL models the shifter as a buffer;', 't-sm', 'start', 'l2:l2.vc-fifo'); T(L, 580, 662, 'the physical cell is not documented', 't-sm', 'start', 'l2:l2.vc-fifo');
}
/* a 0 -> 1 on the link: the first inverter's PMOS charges the wire; a 0 after a 0 moves nothing */
async function repToggle(tok, c, o) {
  o = o || {};
  const R = c.ap.rep;
  lit(c, ['rep1', 'wireC', 'rep2'], {noRing: true});
  if (o.zeros) {
    mos(c, R.r1.p, false, {lab: false}); mos(c, R.r1.q, true, {lab: false}); mos(c, R.r2.p, true, {lab: false}); mos(c, R.r2.q, false, {lab: false});
    fadeIn(netLab(c.fx, -150, 150, 'in = 1 (was 1)', 'start'));
    fadeIn(T(c.fx, 280, 250, 'a zero after a zero: no node moves, no energy', 't-smb halo', 'middle'));
    await wait(tok, 900); return;
  }
  mos(c, R.r1.p, false, {lab: false}); mos(c, R.r1.q, true, {lab: false});
  fadeIn(netLab(c.fx, -150, 150, 'in: 1 → 0', 'start'));
  await wait(tok, 400);
  mos(c, R.r1.q, false, {lab: false}); mos(c, R.r1.p, true, {cur: 'down', lab: false});
  lit(c, 'wireC');
  await Promise.all(c.ap.caps.map((p, k) => droop(tok, c, p.x + 24, 136, {from: 0, to: 1, l0: k === 1 ? 'to VDD' : '', ms: 700 + k * 150})));
  alive(tok);
  mos(c, R.r2.p, false, {lab: false}); mos(c, R.r2.q, true, {cur: 'down', lab: false});
  fadeIn(T(c.fx, 280, 250, 'C · V² drawn from the mesh rail, once per 0 → 1', 't-smb halo', 'middle', 'l3:g.wire-energy'));
  lit(c, 'bitE');
  await wait(tok, 500);
}
async function lsLift(tok, c) {
  const T0 = c.ap.ls;
  lit(c, ['lsin', 'ls'], {noRing: true});
  mos(c, T0.ip, false); mos(c, T0.inn, true, {cur: 'down', lab: false});
  fadeIn(netLab(c.fx, -150, 446, 'IN = 1', 'start')); fadeIn(T(c.fx, -150, 468, '(mesh swing)', 't-sm halo', 'start'));
  await wait(tok, 500);
  mos(c, T0.n1, true, {cur: 'down'}); mos(c, T0.n2, false);
  await droop(tok, c, 280, 380, {from: 1, to: 0, l0: 'A falls', side: 'l', ms: 700});
  mos(c, T0.p2, true, {cur: 'down', lab: false}); mos(c, T0.p1, false, {lab: false});
  await droop(tok, c, 540, 378, {from: 0, to: 1, l0: 'B rises to the high rail', ms: 700});
  lit(c, 'sync');
  await wave(tok, c, c.ap.wave, [
    {name: 'IN', pts: [[0, 0], [0.18, 0.62]], col: 'var(--c1)'},
    {name: 'A', pts: [[0, 1], [0.3, 0]]},
    {name: 'OUT', pts: [[0, 0], [0.4, 1]], col: 'var(--c2)'},
  ], {generic: true, ms: 1200, lw: 70});
}

/* ================= L3 (key 3, #l3): the top quarter of every shire's panels, across the mesh ================= */
/* L3 decode (default swizzle0, mode M0): home shire PA[10:6], bank PA[12:11], sub-bank PA[14:13], set PA[22:15] under
   the L3's base 0x300 (l3.decode, l3.partition-m0); the data row is {set, way} (l3.same-arrays); the memory shire a
   miss goes to is PA[8:6] (l3.miss-path). The way is the example's (no address bit picks it). */
function dec3(pa) {
  const home = bits(pa, 10, 6), bank = bits(pa, 12, 11), sub = bits(pa, 14, 13), s8 = bits(pa, 22, 15), set = 768 + s8, way = D.addr.way_l2;
  return {home, bank, sub, s8, set, way, row: set * 4 + way, ms: bits(pa, 8, 6), qw: bits(pa, 5, 4)};
}
const kickAs = (fn, kick, facts) => ctx => Object.assign({}, fn(ctx), {kick}, facts ? {facts} : {});
const I3 = () => SCENES.l3.inst;
const fit3 = h => V('l3_fit_c') + V('l3_fit_hop') * h;   // l3.lat-fit: 110.5 + 11.99 cycles per hop, three cards

function buildL3Chip(L, ap, inst) {
  const R = SHC[inst.req], H = SHC[inst.home], hh = hopsC(R, H);
  frame(L, {title: `Chip · the L3: ${nt('l3_mb')} in 32 slices`, f: nf('l3_mb'), sub: 'the measured map of the mesh; a line lives in the slice of its home shire, PA[10:6]', subf: MAPF + ' l3:l3.homes',
    tags: [['unknown', '? route order · asked'], ['documented', 'measured']]});
  chipMap(L, ap, {C: 74, X0: -150, Y0: 22, tile: c => c.type === 'cshire'
    ? {marks: [c.id === inst.home ? 'H' : null, c.id === inst.req ? 'R' : null].filter(Boolean), hi: c.id === inst.home || c.id === inst.req, child: c.id === inst.home ? 'home' : null, cur: c.id === inst.home}
    : c.type === 'memshire' ? {marks: c.id === inst.ms ? ['M'] : [], fo: 0.06} : {}});
  // the route R -> H, drawn x first (the order is not documented), and the first hop to zoom into
  const rc = routeC(R, H), P = rc.map(c => ap.P[ckey(c)]);
  if (P.length > 1) routeLine(L, ap, P);
  const a0 = rc[0], b0 = rc[1] || CELLS.find(x => hopsC(x, a0) === 1), p0 = ap.P[ckey(a0)], q0 = ap.P[ckey(b0)];
  ap.hopBox = {x: (p0.x + q0.x) / 2 - 17, y: (p0.y + q0.y) / 2 - 17, w: 34, h: 34};
  part(L, 'link', ap.hopBox.x, ap.hopBox.y, 34, 34, COL.net, '', {child: 'hop', cur: true, fo: 0.3, rx: 17, label: 'A mesh hop on the route: Enter zooms into it'});
  T(L, -150, 640, 'the map: measured on three cards;', 't-sm', 'start', MAPF);
  T(L, -150, 661, 'memory shires: a latency fit; routes', 't-sm', 'start', MAPF);
  T(L, -150, 682, 'drawn x first (the order: not documented)', 't-sm', 'start', 'l3:l3.route');
  // the line's home and the requester
  const X = 330, W = 748;
  part(L, 'homebox', X, 18, W, 96, COL.logic, `home = PA[10:6] = ${inst.home} → shire ${inst.home}`, {f: 'l3:l3.homes l3:l3.decode', fo: 0.06,
    sub: [{t: `requester R = shire ${inst.req} · ${hh} hop${hh === 1 ? '' : 's'} apart · pick R: a shire's details panel`, f: 'l3:l3.home-measured'}]});
  const f0 = fit3(hh);
  const gfit = part(L, 'fit', X, 128, 364, 150, COL.logic, 'load to use, by the fit', {fo: 0.06, sub: [{t: nt('l3_fit_c'), f: nf('l3_fit_c')}, {t: 'on each of three cards', f: nf('l3_fit_c')}]});
  T(gfit, X + 12, 262, `R → H: ${fnum(f0, 1)} cycles`, 't-mid', 'start', 'l3:l3.lat-fit');
  part(L, 'mean', X + 384, 128, W - 384, 150, COL.logic, 'over the whole chip', {fo: 0.06, sub: [{t: `a home is ${nt('l3_mean')} away on average`, f: nf('l3_mean')}, {t: nt('l3_mean_c'), f: nf('l3_mean_c')}, {t: `the L3's ${nt('l3_bw')} chip-wide`, f: nf('l3_bw')}]});
  // latency against distance: the medians by home from shire 0 (aifoundry2) and the three-card fit
  const gb = part(L, 'byhome', X, 292, W, 262, COL.logic, 'an L3 hit against hops (from shire 0)', {fo: 0.03, f: 'l3:l3.lat-by-home'});
  const px = h => X + 84 + h * 62, py = cy => 522 - (cy - 100) * 1.3;
  S(E('line', {x1: px(0), y1: py(100), x2: px(10), y2: py(100)}, gb), {stroke: 'var(--axis)', strokeWidth: 1.5});
  [100, 150, 200].forEach(v => { S(E('line', {x1: px(0), y1: py(v), x2: px(10), y2: py(v)}, gb), {stroke: 'var(--grid)', strokeWidth: 1}); T(gb, px(0) - 10, py(v) + 6, String(v), 't-sm', 'end'); });
  [0, 2, 4, 6, 8, 10].forEach(h => T(gb, px(h), py(100) + 22, String(h), 't-sm', 'middle'));
  T(gb, px(10), py(100) + 22, '', 't-sm', 'end');
  T(gb, px(0) - 10, py(200) - 22, 'cycles', 't-sm', 'end'); T(gb, px(9), py(100) + 22, 'hops', 't-sm', 'middle');
  S(E('line', {x1: px(0), y1: py(fit3(0)), x2: px(10), y2: py(fit3(10))}, gb), {stroke: 'var(--c1)', strokeWidth: 2.5});
  // the fit's label above the line's right end: the line falls to the left, away from the text
  T(gb, px(10), py(fit3(10)) - 14, nt('lad_l3'), 't-sm', 'end', nf('lad_l3'));
  [[0, 109], [1, 121.5], [2, 133.5], [4, 157.5], [6, 181.5], [9, 218]].forEach(([h, v]) => S(E('circle', {cx: px(h), cy: py(v), r: 6, 'data-f': 'l3:l3.lat-by-home'}, gb), {fill: 'var(--c1)', stroke: 'var(--page)', strokeWidth: 2}));
  S(E('line', {x1: px(hh), y1: py(235), x2: px(hh), y2: py(100)}, gb), {stroke: 'var(--c2)', strokeWidth: 3, strokeDasharray: '6 5'});
  T(gb, px(hh) + (hh > 6 ? -8 : 8), py(235) + 14, `R → H: ${hh} hops`, 't-smb halo', hh > 6 ? 'end' : 'start', 'l3:l3.lat-fit');
  ap.chart = {px, py};
  railBand(L, X, 568, W, 58, 'pat-mesh', 'The mesh rail');
  T(L, X + 14, 604, `mesh: ${nt('l3_mesh_v')}, ${nt('l3_noc')} · a hop: ${nt('l3_hopcyc')} round trip (${nt('l3_hopns')})`, 't-sm halo', 'start', nf('l3_mesh_v') + ' ' + nf('l3_hopcyc'));
  T(L, X, 662, `a miss goes on to memory shire PA[8:6] = ${inst.ms} (M): the DRAM tab`, 't-sm', 'start', 'l3:l3.miss-path');
}

function buildL3Home(L, ap, inst) {
  frame(L, {title: `Home shire ${inst.home} · its 1 MB slice`, sub: 'a logical drawing: where the banks sit relative to the mesh stop is not documented', subf: 'l3:u.slice-floorplan',
    tags: [['unknown', '? floorplan · asked'], ['documented', 'documented']]});
  railBand(L, -150, 12, 1228, 118, 'pat-mesh', 'The mesh rail');
  railBand(L, -150, 140, 1228, 550, 'pat-hv', 'The Shire Channel', 'rail');
  T(L, 1066, 130, `mesh ${nt('l3_mesh_v')}`, 't-sm halo', 'end', nf('l3_mesh_v'));
  T(L, 1066, 687, `Shire Channel: SRAM arrays on ${nt('l3_sram_v')}; the logic's rail asked`, 't-sm halo', 'end', nf('l3_sram_v') + ' l3:u.rail-of-logic');
  part(L, 'tol3m', -136, 22, 440, 88, COL.net, 'to_l3 masters × 4', {sub: [{t: 'this shire\'s own L2 misses leave here', f: 'l3:l3.ports'}]});
  part(L, 'stop', 330, 22, 420, 88, COL.net, 'mesh stop', {sub: [{t: 'requests from other shires arrive here', f: 'l3:l3.ports'}]});
  part(L, 'tosys', 776, 22, 292, 88, COL.net, 'to_sys master', {sub: [{t: `a miss → memory shire ${inst.ms}`, f: 'l3:l3.miss-path'}]});
  const gp = part(L, 'ports', 330, 148, 420, 40, COL.xing, '', {label: 'The four L3-slave ports: VC FIFOs back up to the Shire Channel'});
  ap.port = [];
  for (let k = 0; k < 4; k++) { const x = 346 + k * 100; S(E('rect', {x, y: 154, width: 88, height: 28, rx: 4, 'pointer-events': 'none'}, gp), {fill: 'var(--c5)', fillOpacity: 0.2, stroke: 'var(--c5)', strokeWidth: 1.25}); T(gp, x + 44, 174, 'slave ' + k, 't-sm', 'middle'); ap.port.push({x: x + 44, y: 168}); }
  T(L, 318, 162, 'L3-slave ports:', 't-sm halo', 'end', nf('l3_ports_w')); T(L, 318, 183, nt('l3_ports_w'), 't-sm halo', 'end', nf('l3_ports_w'));
  part(L, 'xbar', -136, 200, 1204, 34, COL.net, 'crossbar: an L3 request goes to bank PA[12:11]', {ty: 25, tcls: 't-sm', fo: 0.14, f: 'l3:l3.lane'});
  ap.bank = [];
  for (let b = 0; b < 4; b++) {
    const x = -136 + b * 252, w = 238;
    const g = part(L, 'banks', x, 246, w, 190, COL.store, `bank ${b}`, {ctx: {i: b, inst: {bank: b}}, child: b === inst.bank ? 'hbank' : null, cur: b === inst.bank, fo: 0.08, sub: [`PA[12:11] = ${b}`]});
    for (let s = 0; s < 4; s++) {
      const sx = x + 12 + s * 56;
      S(E('rect', {x: sx, y: 310, width: 48, height: 112, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.16, stroke: 'var(--c3)', strokeWidth: 1.25});
      S(E('rect', {x: sx, y: 394, width: 48, height: 28, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: b === inst.bank ? 0.45 : 0.2});
    }
    ap.bank[b] = {x: x + w / 2, y: 360, box: {x, y: 246, w, h: 190}};
  }
  T(L, -136, 456, 'shaded: the L3\'s quarter of each sub-bank (sets 768–1023)', 't-sm', 'start', 'l3:l3.partition-m0');
  part(L, 'uc', 872, 246, 196, 190, COL.aux, 'UC block', {sub: ['barriers, credits', 'not on the path']});
  for (let k = 0; k < 4; k++) part(L, 'nbr', -136 + k * 252, 474, 238, 96, COL.logic, `neighbourhood ${k}`, {ctx: {i: k}, fo: 0.03, sub: [{t: 'loses a sub-bank to L3', f: 'l3:l3.priority'}]});
  part(L, 'slice', -136, 586, 740, 80, COL.aux, 'the slice: 1 MB per shire', {fo: 0.06, sub: [{t: nt('l3_slice'), f: nf('l3_slice')}, {t: `${nt('l3_lines')}, all in the same macros as the L2`, f: nf('l3_lines')}]});
  part(L, 'floor', 620, 586, 448, 80, 'var(--warn)', 'floorplan: unknown', {kind: 'unknown', sub: [{t: 'the banks against the mesh stop', f: 'l3:u.slice-floorplan'}]});
  ap.stop = {x: 540, y: 90}; ap.xbarY = 217;
}

function buildL3Bank(L, ap, inst) {
  frame(L, {title: `Bank ${inst.bank} of home shire ${inst.home}`, sub: 'the same bank as the L2\'s: its L3-slave side serves the other shires', subf: 'l3:l3.ports l3:l3.reqq',
    tags: [['documented', 'documented']]});
  part(L, 'l3fifo', -150, 14, 220, 186, COL.xing, 'L3-slave FIFO', {sub: ['from the port,', 'one request a cycle']});
  const gq = part(L, 'reqq', 86, 14, 400, 186, COL.logic, 'request queue', {sub: [{t: `64 entries · ${nt('l3_reqq21')} for L3 (hatched)`, f: nf('l3_reqq21')}]});
  ap.q = [];
  for (let i = 0; i < 64; i++) {
    const x = 98 + (i % 16) * 24, y = 88 + Math.floor(i / 16) * 26, l3 = i >= 43;
    ap.q.push(S(E('rect', {x, y, width: 20, height: 20, rx: 3, 'pointer-events': 'none'}, gq), {fill: l3 ? 'url(#pat-hatch)' : 'var(--c1)', fillOpacity: l3 ? 1 : 0.15, stroke: 'var(--c1)', strokeWidth: 1}));
  }
  part(L, 'arb', 502, 14, 190, 186, COL.logic, 'arbitration', {sub: [{t: 'per sub-bank:', f: 'l3:l3.priority'}, {t: 'L3-slave first', f: 'l3:l3.priority'}]});
  const gr = part(L, 'rbuf', 708, 14, 180, 186, COL.logic, 'read buffer', {fo: 0.02, sub: ['8 lines:', 'L3 reads', 'never use it']});
  gr.insertBefore(S(E('line', {x1: 720, y1: 190, x2: 876, y2: 34, 'pointer-events': 'none'}), {stroke: 'var(--ink-2)', strokeWidth: 2}), gr.querySelector('text'));
  part(L, 'atomic', 904, 14, 174, 186, COL.logic, 'atomic block', {sub: ['read · op · write', 'the sub-bank', 'held busy']});
  ap.sub = [];
  for (let s = 0; s < 4; s++) {
    const x = -150 + s * 212, w = 200;
    const g = part(L, 'subbanks', x, 222, w, 206, COL.store, `sub-bank ${s}`, {ctx: {i: s, inst: {sub: s}}, child: 'sub', cur: s === inst.sub, fo: 0.08, sub: [`PA[14:13] = ${s}`]});
    [[12, 36], [52, 24]].concat([0, 1, 2, 3].map(p => [84 + p * 28, 24])).forEach(([dx, ww], k) => {
      S(E('rect', {x: x + dx, y: 284, width: ww, height: 128, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: k < 2 ? 0.2 : 0.28, stroke: 'var(--c3)', strokeWidth: 1.25});
      S(E('rect', {x: x + dx, y: 380, width: ww, height: 32, rx: 2, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: s === inst.sub ? 0.45 : 0.2});
    });
    ap.sub[s] = {x: x + w / 2, y: 330, box: {x, y: 222, w, h: 206}};
  }
  part(L, 'tosys', 698, 222, 380, 96, COL.net, 'to_sys → memory', {sub: [{t: `a miss: memory shire PA[8:6] = ${inst.ms}`, f: 'l3:l3.miss-path'}]});
  part(L, 'partial', 698, 332, 380, 96, COL.logic, 'partial lines', {sub: [{t: 'left by write-arounds; a read', f: 'l3:l3.partial'}, {t: 'evicts one first', f: 'l3:l3.partial'}]});
  const gpp = comp(L, 'pipe', {}, 'The bank\'s pipeline: tags first, then the hit way\'s data');
  T(gpp, -150, 470, `the same ${nt('l2_stages')} stages as an L2 hit`, 't-labb', 'start', 'l3:l3.pipeline');
  ap.stg = {};
  STG.forEach((s, i) => {
    const x = -150 + i * 82, ram = i >= 3 && i <= 6 || i >= 9 && i <= 12;
    S(E('rect', {x, y: 486, width: 74, height: 50, rx: 5}, gpp), {fill: ram ? 'var(--c3)' : 'var(--c1)', fillOpacity: 0.14, stroke: ram ? 'var(--c3)' : 'var(--c1)', strokeWidth: 1.5});
    T(gpp, x + 37, 517, s, 't-mono', 'middle', 'l3:l3.pipeline');
    ap.stg[s] = {x, y: 486, w: 74, h: 50};
  });
  [['tag and tag-state RAMs', 3, 6], ['data RAMs: the hit way only', 9, 12]].forEach(([t, a0, b0]) => { const x0 = -150 + a0 * 82, x1 = -150 + b0 * 82 + 74; wire(gpp, [[x0, 548], [x0, 556], [x1, 556], [x1, 548]], 'thin'); T(gpp, (x0 + x1) / 2, 576, t, 't-sm', 'middle', 'l3:l3.hit-way-read'); });
  gpp._box = {x: -150, y: 486, w: 1224, h: 50};
  T(L, -150, 612, `each RAM access: ${nt('l3_ram2')} (esr_sc_ram_delay, the default); a hit also writes the LRU through the tag-state RAM's second port`, 't-sm', 'start', nf('l3_ram2') + ' l3:l3.mru-write');
  T(L, -150, 636, 'an L3 read never uses the read buffer: every hit reads the tag, state and data macros', 't-sm', 'start', 'l3:l3.no-rbuf');
  T(L, -150, 668, `the spec: an L3 hit takes ${nt('l3_spec30')} at the slave, crossbars included`, 't-smb', 'start', nf('l3_spec30'));
  ap.fifo = {x: -40, y: 107}; ap.rq = {x: 286, y: 107}; ap.arbP = {x: 597, y: 107}; ap.atom = {x: 991, y: 107}; ap.tosysP = {x: 888, y: 270};
}

function buildL3Sub(L, ap, inst) {
  const a = inst;
  frame(L, {title: `Sub-bank ${a.sub} (PA[14:13]) of bank ${a.bank}`, sub: 'the L3 is the top quarter of the same macros: tag rows 768–1023, data rows 3,072–4,095', subf: 'l3:l3.same-arrays',
    tags: [['documented', 'documented']], col: COL.store});
  const macro = (key, x, w, title, sub, rowsN, o) => {
    const g = part(L, key, x, 14, w, 420, COL.store, title, Object.assign({fo: 0.06, sub}, o));
    const top = 110, H = 300, yOf = r => top + r / rowsN * H;
    S(E('rect', {x: x + 12, y: top, width: w - 24, height: H, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.12, stroke: 'var(--c3)', strokeWidth: 1.25});
    S(E('rect', {x: x + 12, y: yOf(o.b0), width: w - 24, height: yOf(o.b1) - yOf(o.b0), 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: 0.18});
    const ic = icgSym(g, x + w / 2 - 26, 74, {w: 52, h: 34});
    return {g, x, w, icg: ic.box, rowY: yOf(o.row)};
  };
  const tr = macro('tagram', -150, 150, 'tag RAM', [{t: nt('l2_mtag_s'), f: nf('l2_mtag_s')}], 1024, {b0: 768, b1: 1024, row: a.set});
  const sr = macro('stateram', 12, 150, 'tag state', [{t: nt('l2_mstate_s'), f: nf('l2_mstate_s')}], 1024, {b0: 768, b1: 1024, row: a.set});
  T(L, 87, 452, 'two-port', 't-sm', 'middle', 'l3:l3.mru-write');
  part(L, 'ecc', 186, 14, 210, 84, COL.logic, 'te: tag ECC', {ctx: {i: 0}, sub: ['SECDED per tag']});
  const gc = part(L, 'cmp', 186, 112, 210, 150, COL.logic, 'tc: compare', {sub: ['4 × 23 bits']});
  ap.eq = [];
  for (let w = 0; w < 4; w++) { const cx = 212 + w * 48, cy = 218; S(E('circle', {cx, cy, r: 17, 'pointer-events': 'none'}, gc), {fill: 'var(--surface)', stroke: 'var(--c1)', strokeWidth: 2}); T(gc, cx, cy + 7, '=', 't-labb', 'middle'); ap.eq.push({x: cx, y: cy}); }
  // the zero-line path: a 512-bit NOR as the line arrives sets the way's zero bit; a zero line never touches the data macros
  const gz = part(L, 'zero', 186, 276, 210, 158, COL.logic, 'zero line', {sub: [{t: 'NOR of 512 bits', f: 'l3:l3.zero-state'}]});
  const nor = andSym(gz, 260, 370, {or: true, bubble: true, w: 50, h: 44});
  wire(gz, [[206, nor.a.y], [nor.a.x + 6, nor.a.y]], 'thin'); wire(gz, [[206, nor.b.y], [nor.b.x + 6, nor.b.y]], 'thin'); T(gz, 214, 408, '⋮ 512', 't-sm');
  wire(gz, [[nor.out.x, 370], [386, 370]]); T(gz, 380, 422, '→ zero bit', 't-sm', 'end');
  ap.norOut = {x: nor.out.x, y: 370};
  ap.panels = [];
  for (let p = 0; p < 4; p++) ap.panels.push(macro('data', 414 + p * 166, 154, `panel ${p}`, [{t: nt('l2_mdata_s'), f: nf('l2_mdata_s')}], 4096, {b0: 3072, b1: 4096, row: a.row, ctx: {i: p, inst: {panel: p}}, child: 'panel', cur: p === a.panel}));
  ap.macros = {tag: tr, state: sr};
  part(L, 'ecc', 414, 452, 652, 70, COL.logic, 'de: data ECC', {ctx: {i: 1}, sub: [{t: `8 × SECDED, ${nt('l2_ecc')}`, f: nf('l2_ecc')}], ty: 26});
  part(L, 'dc', 414, 536, 652, 56, COL.net, 'dc: data complete → the L3-slave response', {ty: 35, tcls: 't-sm'});
  T(L, -150, 486, 'shaded: the L3\'s rows', 't-smb', 'start', 'l3:l3.same-arrays');
  T(L, -150, 508, `tag rows 768 + PA[22:15] = ${a.set}`, 't-sm', 'start', 'l3:l3.decode');
  T(L, -150, 530, `data row {set, way} = ${fnum(a.row)}`, 't-smb', 'start', 'l3:l3.same-arrays');
  T(L, -150, 566, `trims at reset: the RM0 row (${nt('l2_rm0n')} nominal)`, 't-sm', 'start', 'l3:l3.trim-reset l3:l3.trim-table');
  T(L, -150, 588, `the rail, ${nt('l3_sram_v')}:`, 't-sm', 'start', nf('l3_rm55')); T(L, -150, 609, nt('l3_rm55'), 't-sm', 'start', nf('l3_rm55'));
  T(L, -150, 640, 'a read clocks all four panels; a write only the written quadwords\'', 't-sm', 'start', 'l3:l3.panels l3:l3.clock-gating');
  T(L, -150, 664, `ECC errors are corrected, never written back: no scrub`, 't-sm', 'start', 'l3:l3.ecc-scrub');
  ap.panelBox = ap.panels[a.panel] ? {x: ap.panels[a.panel].x, y: 14, w: 154, h: 420} : null;
}
function buildL3Panel(L, ap, inst) {
  buildPanel(L, ap, {title: `Data panel ${inst.panel} · ${nt('l2_mdata_s')} · 1PUHD`, band: 'l3', row: inst.row,
    sub: 'the same compiled macro as the L2\'s and the scratchpad\'s; the L3 is its top 1,024 rows'});
}
function buildL3Cell(L, ap, inst) {
  buildCell(L, ap, {title: 'One bit · a 6T SRAM cell (generic)',
    sub: 'the spec says SRAM; the lab lead said not SRAM; the bitcell is not documented (asked)',
    note: [`if static: no refresh; ≤ ${nt('leak_mb')}`, `at 80 °C: the L3 ≤ ${nt('l3_leakW')}`], noteF: nf('leak_mb') + ' ' + nf('l3_leakW') + ' l3:g.no-refresh'});
}
function buildL3Hop(L, ap, inst) {
  buildHop(L, ap, {title: 'One mesh hop, up close', sub: `from shire ${inst.req}'s bank to the home's L3-slave port; the reply comes back the same way`, bank: bits(ADDR.pa, 7, 6),
    lane: `PA[12:11] = ${inst.bank}`, laneF: 'l3:l3.lane', laneNote: '(re-impl. RTL, to confirm)', to: `shire ${inst.home}: L3-slave port`});
}
function buildL3Wire(L, ap, inst) {
  buildWire(L, ap, {title: 'A link bit, and the crossing', sub: 'a repeater charging a wire; the level shifter at the far shire (textbook)'});
}

SCENES.l3 = {
  lv: 'l3', title: 'L3 (across the mesh)', short: 'L3', root: 'chip', inst: {}, req: 0, zero: false,
  setInst() { const a = dec3(ADDR.pa); this.inst = Object.assign(a, {req: this.req, panel: a.qw}); this.inst.hops = hopsC(SHC[this.req], SHC[a.home]); },
  head: () => `${n('l3_mb')} in 1 MB slices, homed by PA[10:6]; a hit costs ${n('lad_l3')} and ${n('lad_e_l3')} per byte`,
  addrFields(pa) {
    const a = dec3(pa);
    return [['home', 'PA[10:6]', `${a.home}`, 'l3:l3.homes l3:l3.decode', true], ['bank', 'PA[12:11]', a.bank, 'l3:l3.decode', true], ['sub-bank', 'PA[14:13]', a.sub, 'l3:l3.decode', true],
      ['set', '768 + PA[22:15]', a.set, 'l3:l3.decode l3:l3.partition-m0', true], ['data row', '{set, way}', fnum(a.row), 'l3:l3.same-arrays']];
  },
  scales: {
    chip: {name: 'Chip', short: 'Chip', parent: null, def: 'home', build: buildL3Chip},
    home: {name: 'Home shire', short: 'Home', parent: 'chip', def: 'hbank', tw: 68, target: (ap, inst) => ap.B['s' + inst.home], build: buildL3Home, label: inst => `home shire ${inst.home}`},
    hbank: {name: 'Home bank', short: 'Bank', parent: 'home', def: 'sub', tw: 238, target: (ap, inst) => ap.bank[inst.bank].box, build: buildL3Bank, label: inst => `bank ${inst.bank} of shire ${inst.home}`},
    sub: {name: 'Sub-bank', short: 'Sub-bank', parent: 'hbank', def: 'panel', tw: 200, target: (ap, inst) => ap.sub[inst.sub].box, build: buildL3Sub, label: inst => `sub-bank ${inst.sub} of bank ${inst.bank}`},
    panel: {name: 'Data panel', short: 'Panel', parent: 'sub', def: 'cell', tw: 154, target: ap => ap.panelBox, build: buildL3Panel, label: inst => `data panel ${inst.panel}`},
    cell: {name: 'Cell', short: 'Cell', parent: 'panel', def: null, tw: 90, target: ap => { const k = ap.rowK, y = ap.Y0 + k * ap.RH; return {x: ap.AX + ap.CW, y: y + 2, w: ap.CW - 12, h: ap.RH - 16}; }, build: buildL3Cell},
    hop: {name: 'Mesh hop', short: 'Hop', parent: 'chip', def: 'rep', tw: 34, target: ap => ap.hopBox, build: buildL3Hop},
    rep: {name: 'Repeater and level shifter', short: 'Transistors', parent: 'hop', def: null, tw: 40, target: ap => ap.repBox, build: buildL3Wire},
  },
};
const L3P = SCENES.l3.parts = {
  overview: () => ({kick: 'Level 3 · key 3', title: 'The L3', badge: [['documented', 'structure, timing, energy'], ['generic', 'the cell, the router'], ['unknown', 'the bitcell, the hop, the split']],
    what: `The L3 is memory-side and spread over the chip: each of the 32 compute shires gives the top quarter of its shire cache to a chip-wide L3 of ${n('l3_mb')}, and a line lives in the slice of its home shire, PA[10:6]. It is not a separate memory: it is ${src('rows 3,072–4,095 of the same data panels', 'l3:l3.same-arrays')} that hold the L2 and the scratchpad. A hit costs ${n('lad_l3')} load to use, the hops counted between the requester and the home (three cards), and ${n('lad_e_l3')} per byte; zeros cost ${n('l3_e_cont')}. The spec's cycle counts do not add up to the measurement, and where the fixed ${n('l3_61')} go is asked.`,
    kpis: [K('l3_mb', 'the chip\'s L3'), kpi(n('lad_l3'), 'load to use'), K('lad_e_l3', 'per byte, above idle'), K('l3_bw', 'chip-wide')],
    act: `<button type="button" class="st-btn tog" data-act="zero" aria-pressed="${SCENES.l3.zero}">Zero line: the example line all zeros</button>`,
    extra: ladderHtml('l3')}),
  shire: ctx => {
    const id = ctx.id, I = I3(), H = SHC[I.home], c = SHC[id], h = hopsC(c, H);
    return {kick: 'L3 · chip', title: `Shire ${id}${id === I.home ? ': the home' : ''}${id === I.req ? ' (the requester)' : ''}`, badge: [['documented', 'measured map']], facts: 'shire',
      what: `Map cell (${c.lx}, ${c.ly}). ${id === I.home ? `This line's home: PA[10:6] = ${id}, so its slice holds the line.` : `Its slice holds the lines whose PA[10:6] = ${id}.`} From here the line's home, shire ${I.home}, is ${h} hop${h === 1 ? '' : 's'} away: by the three-card fit an L3 hit costs ${cn(fit3(h), 'l3:l3.lat-fit', 1)} cycles from here. The average home is ${cn(meanHops(c), 'l3:l3.mean-hops', 2)} hops from this shire.`,
      act: `<button type="button" class="st-btn" data-act="req" data-id="${id}">Requester here</button>` + (id === I.home ? ` <button type="button" class="st-btn" data-act="zoom" data-to="home">Zoom into the home shire</button>` : '')};
  },
  memshire: ctx => ({kick: 'L3 · chip', title: `Memory shire ${ctx.id}`, badge: [['documented', 'measured, a latency fit']], facts: 'memshire',
    what: `It serves the lines whose PA[8:6] = ${ctx.id}. An L3 miss leaves its home through the to_sys port for this memory shire and costs ${n('l3_dram91')} more; the DRAM tab follows it.${ctx.cell && ctx.cell.tie ? ' Its place is a tie-break of the fit: three places fit equally.' : ''}`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="dram">The DRAM (key 5) →</button>`}),
  grey: ctx => ({kick: 'L3 · chip', title: 'A cell without a compute shire', badge: [['documented', 'measured map']], facts: 'shire', what: `${esc(ctx.cell ? ctx.cell.name : '')}: a mesh stop that homes no L3 lines. Routes pass through it: latency stays linear in the hop count over all pairs.`}),
  link: () => ({kick: 'L3 · chip', title: 'A mesh hop', badge: [['documented', 'measured cost'], ['generic', 'the router'], ['unknown', 'its pipeline']], facts: 'hop',
    what: `Each hop adds ${n('l3_hopcyc')} to the round trip (${n('l3_hopns')}, the same for L3 hits, remote scratchpad and TensorSend). Zoom in to see a router, a link and the crossings.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="hop">Zoom into a hop</button>`}),
  homebox: () => ({kick: 'L3 · chip', title: 'Which shire is the home', badge: [['documented', 'spec and measured']],
    what: `The home field is 5 bits, PA[10:6], for 32 shires: consecutive 64-byte lines rotate over the 32 homes. The rule holds on silicon: ${n('l3_home1498')} timed from shire 0 fall within 4 cycles of the fit (aifoundry2), ${n('l3_home99')} of lines on each of three cards. Two-shire aliasing keeps PA[10] in the tag, so a dead shire's lines could be moved 16 IDs away.`}),
  fit: () => ({kick: 'L3 · latency', title: 'An L3 hit, load to use', badge: [['documented', 'measured, three cards'], ['unknown', 'the split']],
    what: `${n('l3_fit_c')} between the requester and the home, on each of three cards: ${n('l3_109')} when the home is the requester's own shire, ${n('l3_218')}. Chases at 600 and 800 MHz split the constant: ${n('l3_72')} scale with the core clock and ${n('l3_61')} do not, plus ${n('l3_20ns')}. The spec's ${n('l2_spec_miss')} shire clocks for the L2 miss and ${n('l3_spec30')} for the L3 hit do not reconcile with that; where the cycles go is asked.`,
    kpis: [kpi(n('lad_l3'), 'load to use'), K('l3_hopns', 'per hop, round trip')]}),
  mean: () => ({kick: 'L3 · latency', title: 'Averaged over the chip', badge: [['documented', 'derived from the map and the fit']],
    what: `On the measured map a requester is ${n('l3_mean')} from a line's home on average (all 32 × 32 pairs, self included): by the fit an average L3 hit costs ${n('l3_mean_c')} chip-wide. With every minion streaming, the L3 delivers ${n('l3_bw')}.`}),
  byhome: () => ({kick: 'L3 · latency', title: 'Latency against distance', badge: [['documented', 'measured']], facts: 'fit',
    what: `The dots are the median of each home's lines timed from shire 0 on aifoundry2 (19 September): ${n('l3_109')} at home, ${n('l3_218')}; the line is the three-card fit, ${n('l3_fit_c')}. A 32-byte TensorSend between two shires costs ${n('l3_tsend')}: the same 12 per hop, a larger constant.`}),
  rail: () => ({kick: 'L3 · power', title: 'The Shire Channel and the mesh', badge: [['documented', 'measured rails']], facts: 'rails',
    what: `The slice's macros sit on the SRAM rail, ${n('l3_sram_v')} on the die, and the shire cache runs on the shire clock, ${n('l3_clk')}; the mesh runs on its own rail, ${n('l3_mesh_v')}, at ${n('l3_noc')}. Every request crosses down and every reply back up through VC FIFOs with level shifters and 2-flop synchronisers.`}),
  tol3m: () => ({kick: 'L3 · home shire', title: 'to_l3 masters', badge: [['documented', 'spec']], facts: 'ports', what: 'Four to_l3 master ports carry this shire\'s own L2 misses to their homes. An L3 request takes the lane of the bank it will use at the home, PA[12:11] (in the re-implementation RTL; the chip tour draws PA[7:6], a correction to confirm).'}),
  stop: () => ({kick: 'L3 · home shire', title: 'The mesh stop', badge: [['documented', 'spec']], facts: 'ports', what: 'Each shire meets the mesh with 4 L3-slave ports (requests from other shires, 512 bits, one a cycle each), 4 to_l3 masters and 1 to_sys master to memory; the AXI channels cross into the NoC through voltage-changing FIFOs with 2-stage synchronisers.'}),
  ports: () => Object.assign(L3P.stop(), {title: 'L3-slave ports'}),
  tosys: () => ({kick: 'L3 · home', title: 'to_sys: the way to memory', badge: [['documented', 'spec and measured']], facts: 'miss',
    what: `An L3 miss leaves its home through the single to_sys port for memory shire PA[8:6]; the line returns as an L3 fill, which may evict a victim (written back over to_sys if dirty). Past the L3 a DRAM load adds ${n('l3_dram91')}.`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="dram">The DRAM (key 5) →</button>`}),
  xbar: () => ({kick: 'L3 · home shire', title: 'The crossbar', badge: [['documented', 'spec']], facts: 'ports', what: 'The same request crossbar as the L2\'s, with the L3-slave FIFOs as clients: an incoming request goes to bank PA[12:11], and its sub-bank is PA[14:13].'}),
  banks: ctx => ({kick: 'L3 · home shire', title: `Bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']], facts: 'banks',
    what: `One of four; the L3's quarter of it is sets 768–1023 of each of its four sub-banks, ${n('l3_bank_lines')}. The same bank serves the shire's own L2 and scratchpad from the lower rows.`,
    act: ctx.i === I3().bank ? `<button type="button" class="st-btn" data-act="zoom" data-to="hbank">Zoom into bank ${ctx.i}</button>` : ''}),
  uc: () => ({kick: 'L3 · home shire', title: 'UC block', badge: [['documented', 'spec']], facts: 'banks', what: 'Barriers, credit counters and global atomics that go through the UC: not on an L3 read\'s path.'}),
  nbr: () => ({kick: 'L3 · home shire', title: 'The home\'s own neighbourhoods', badge: [['documented', 'spec and measured']], facts: 'priority',
    what: 'The home shire keeps running its own work. Its minions\' requests lose each sub-bank\'s arbitration to L3-slave requests unless esr_sc_l3_yield_priority_cnt is set; two errata record neighbourhood requests starved or hung behind L3-slave traffic.'}),
  slice: () => ({kick: 'L3 · home shire', title: 'One slice', badge: [['documented', 'spec, derived']], facts: 'slice',
    what: `${n('l3_slice')}: ${n('l3_lines')}. In mode M0 (the cards' mode) the L3 is sets 768–1023 of every sub-bank, base 0x300; the firmware computes it as scratchpad size + L2 size.`}),
  floor: () => ({kick: 'L3 · home shire', title: 'The slice\'s floorplan', badge: [['unknown', 'asked']], facts: 'floor', what: `Where the four banks, and so the L3 slice's quarters, sit in the shire tile (a hop, ${n('l3_hopmm')}, across) against the mesh stop and the four L3-slave ports is not documented: the drawing is logical.`}),
  l3fifo: () => ({kick: 'L3 · home bank', title: 'L3-slave FIFO', badge: [['documented', 'spec']], facts: 'reqq', what: 'Requests from other shires, converted from AXI to ET-Link, wait here for a request-queue entry: two entries can be allocated each cycle, one for a neighbourhood request and one for an L3 request.'}),
  reqq: () => ({kick: 'L3 · home bank', title: 'Request queue', badge: [['documented', 'spec']], facts: 'reqq', what: `The bank's ${n('l2_reqq')}, with up to ${n('l3_reqq21')} reserved for L3-slave requests (hatched).`}),
  arb: () => ({kick: 'L3 · home bank', title: 'Arbitration', badge: [['documented', 'spec']], facts: 'priority', what: 'Per sub-bank, three steps: round-robin, then L3-slave requests before the shire\'s own, then busy sub-banks masked.'}),
  rbuf: () => ({kick: 'L3 · home bank', title: 'The read buffer: not for the L3', badge: [['documented', 'spec']], facts: 'rbuf', what: 'L3 reads never use the bank\'s 8-entry read buffer: every L3 hit reads the tag, tag-state and data macros. L2 and scratchpad reads can be served from it.'}),
  atomic: () => ({kick: 'L3 · home bank', title: 'The atomic block', badge: [['documented', 'spec and measured']], facts: 'atomic',
    what: `Global atomics run here, in the line's home bank: read, operate (32, 64 or 256 bits), write, with the sub-bank busy throughout. One contended line retires an atomic every ${n('l3_atomic')}; an uncontended remote atomic takes ${n('l3_atom216')}. Atomics on home-L3 lines draw ${n('l3_atomW')} over idle on aifoundry2.`}),
  partial: () => ({kick: 'L3 · home bank', title: 'Partial lines', badge: [['documented', 'spec']], facts: 'write', what: 'The L3, unlike the L2, can hold lines only partly written by write-arounds; a read that hits one first evicts it to memory and reads the whole line back.'}),
  subbanks: ctx => ({kick: 'L3 · home bank', title: `Sub-bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']], facts: 'sub',
    what: 'Chosen by PA[14:13]: its tag RAM, tag-state RAM and four data panels, the L3 in their top quarter (shaded).',
    act: ctx.i === I3().sub ? `<button type="button" class="st-btn" data-act="zoom" data-to="sub">Zoom into sub-bank ${ctx.i}</button>` : ''}),
  pipe: () => ({kick: 'L3 · home bank', title: 'The pipeline, for an L3 hit', badge: [['documented', 'spec']], facts: 'pipe',
    what: `Two phases, tag then data: ag, ad, rqa, tap … ta1 (tag and tag-state RAMs), te (tag ECC), tc (compare), then dap … da1 (the data RAMs), de (ECC), dc. Only the hit way is read, since the data address {set, hit way} is formed after the compare. Each RAM access is ${n('l3_ram2')}; the spec gives an L3 hit ${n('l3_spec30')} at the slave.`}),
  tagram: () => ({kick: 'L3 · sub-bank', title: 'Tag RAM', badge: [['documented', 'spec'], ['unknown', 'the bitcell']], facts: 'tagram', what: `A compiled macro of ${n('l2_mtag')} (type 1PUHD): the L3's rows are 768–1023, four ways' 23-bit tags and 6 ECC bits each, read in parallel.`}),
  stateram: () => ({kick: 'L3 · sub-bank', title: 'Tag-state RAM', badge: [['documented', 'spec']], facts: 'stateram', what: `A two-port macro of ${n('l2_mstate')} (type 2PUHDRF): valid, locked, zero and four quadword-enable bits per way, a 5-bit LRU code and 7 ECC bits. A hit writes the new LRU code through its second port in the same pass.`}),
  data: ctx => ({kick: 'L3 · sub-bank', title: `Data panel ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec'], ['unknown', 'the geometry, the bitcell']], facts: 'data',
    what: `A compiled macro of ${n('l2_mdata')}, one quadword and its ECC per row; the L3's lines are rows 3,072–4,095 of it. A read clocks all four panels, a write only those whose quadword enable is set.`,
    act: ctx.i === I3().panel ? `<button type="button" class="st-btn" data-act="zoom" data-to="panel">Zoom into panel ${ctx.i}</button>` : ''}),
  ecc: kickAs(L2P.ecc, 'L3 · sub-bank'), cmp: kickAs(L2P.cmp, 'L3 · sub-bank'),
  zero: () => ({kick: 'L3 · sub-bank', title: 'Zero lines skip the data macros', badge: [['documented', 'spec'], ['unknown', 'how much it saves']], facts: 'zero',
    what: `When a fill or a full-line write brings an all-zero line, the bank takes the NOR of its 512 bits, sets the way's zero bit and does not write the data macros; a later read does not read them either and returns zeros (esr_sc_zero_state_enable = 1 by default). L3 reads cost ${n('l3_e_cont')}; how much of that saving is this skip and how much is data-dependent switching elsewhere is asked (and would be settled by one run with the bit cleared).`,
    act: `<button type="button" class="st-btn tog" data-act="zero" aria-pressed="${SCENES.l3.zero}">Zero line: the example line all zeros</button>`}),
  dc: () => ({kick: 'L3 · sub-bank', title: 'Data complete', badge: [['documented', 'spec']], facts: 'pipe', what: 'The line is OR\'d out of the sub-bank to the L3-slave response mux and goes back over the mesh as one 512-bit data beat.'}),
  energy: () => ({kick: 'L3 · energy', title: 'What an L3 access costs', badge: [['documented', 'measured'], ['unknown', 'the zero-line share']], facts: 'energy',
    what: `An L3 byte costs ${n('lad_e_l3')} above idle (three cards), ${n('l3_e_line')} per line: about ${cn(V('lad_e_l3') / V('l2_e'), 'l3:l3.energy l2:l2.e.level', 1)} times an L2 byte and about an eighth of a DRAM byte (${cn(V('lad_e_dram') / V('lad_e_l3'), 'l3:l3.energy dram:dram.e.per-byte', 1)} times less). Random data costs ${n('l3_e_cont')}. Per load with a local home, ${n('l3_load643')}: ${n('l3_306')} on the SRAM rail, ${n('l3_120')} on the mesh, ${n('l3_110')} on the minions. Far homes add ${n('l3_59')}.`}),
  latency: () => ({kick: 'L3 · latency', title: 'The cycles that do not add up', badge: [['documented', 'spec and measured'], ['unknown', 'the split']], facts: 'latency',
    what: `Measured: ${n('l3_fit_c')}; of the constant, ${n('l3_72')} scale with the core clock and ${n('l3_61')} do not. The spec: an L2 miss ${n('l2_spec_miss')} shire clocks plus an L3 hit ${n('l3_spec30')}, ${cn(V('l2_spec_miss') + V('l3_spec30'), 'l2:l2.lat.spec l3:l3.spec-latency', 0)} in all, and the L1 and neighbourhood path about ${n('l2_over')} more: about ${cn(V('l2_spec_miss') + V('l3_spec30') + V('l2_over'), 'l2:l2.lat.spec l3:l3.spec-latency l2:l2.lat.overhead', 0)}, against the ${n('l3_72')} of the constant that scale with the clock. The page draws each step without a cycle count ("not split: asked") until the team gives the stage-by-stage latencies.`}),
  // the mesh hop
  bankR: () => ({kick: 'L3 · mesh hop', title: 'The requester\'s bank', badge: [['documented', 'spec']], facts: 'ports', what: 'The L2 missed: the bank\'s request-queue entry stays to receive the fill, and the read goes out on a to_l3 port.'}),
  tol3: () => ({kick: 'L3 · mesh hop', title: 'to_l3 master', badge: [['documented', 'spec, re-implementation RTL']], facts: 'lane',
    what: 'The lane is the bank the request will use at the home, PA[12:11] under swizzle0, not PA[7:6] (which picks the lane only for remote scratchpad): so says the re-implementation RTL alone, to confirm. The ET-Link read becomes an AXI read address (AR), about 75–85 bits.'}),
  vcdown: () => ({kick: 'L3 · mesh hop', title: 'Into the mesh: a VC FIFO', badge: [['documented', 'that it is there'], ['generic', 'the circuit']], facts: 'xing',
    what: `A voltage-changing FIFO with 2-stage synchronisers: the request leaves the Shire Channel (its SRAM arrays on ${n('l3_sram_v')}, its logic on a rail that is asked; ${n('l3_clk')}) for the mesh (${n('l3_mesh_v')}, ${n('l3_noc')}). Level shifters change the swing; the synchroniser costs 2–3 receiving-clock cycles (textbook).`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="rep">Zoom into the transistors</button>`}),
  slave: () => ({kick: 'L3 · mesh hop', title: 'The home\'s L3-slave port', badge: [['documented', 'spec']], facts: 'ports', what: 'The request climbs back into the Shire Channel through the port\'s VC FIFO, becomes an ET-Link request and waits in the bank\'s L3-slave FIFO.'}),
  router: () => ({kick: 'L3 · mesh hop', title: 'A router', badge: [['generic', 'textbook stages'], ['documented', 'layers, ports'], ['unknown', 'its pipeline']], facts: 'router',
    what: 'Each mesh stop has 9 main-NoC routers (layers 0–8) and a debug router, with 8 ports of 4 virtual-channel slots each, parity-protected. Inside, textbook stages: input VC buffers, route computation, VC and switch allocators, a crossbar and output drivers. Which layer carries L3 traffic, the flit width, the pipeline depth and the dimension order are asked.'}),
  router2: () => L3P.router(), more: () => L3P.link(),
  link: () => ({kick: 'L3 · mesh hop', title: 'A link', badge: [['documented', 'the energy, the length'], ['generic', 'repeaters']], facts: 'wire',
    what: `One hop is about ${n('l3_hopmm')} of wire, broken by repeaters. A random bit costs ${n('l3_fj')} per mm on the mesh rail, so a 64-byte reply over one hop is ${n('l3_hop69')} (derived), close to the ${n('l3_hop47')} measured per line per hop. Zeros do not toggle the wires: they cost several times less.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="rep">Zoom into a repeater</button>`}),
  flits: () => ({kick: 'L3 · mesh hop', title: 'What crosses a hop', badge: [['documented', 'spec'], ['unknown', 'the header']], facts: 'flits', what: `A read request is ${n('l3_req_bits')} (AXI AR); the reply is ${n('l3_reply')} plus RID, RRESP and RLAST, and a NetSpeed header of unknown width. Only the reply carries the line.`}),
  hopE: () => L3P.link(),
  nochop: () => ({kick: 'L3 · mesh hop', title: 'The hop\'s pipeline: unknown', badge: [['unknown', 'asked']], facts: 'nochop', what: `Measured: ${n('l3_hopcyc')} per hop round trip, which is 4 NoC cycles each way if both directions take the same (derived). Not documented: the router's stages, which of the 9 layers carry L3 requests and replies, the flit width and the order of the dimensions.`}),
  rep1: () => ({kick: 'L3 · transistors', title: 'A repeater', badge: [['generic', 'textbook']], facts: 'wire', what: `Long wires are broken every few hundred microns by inverters. When the data goes 0 → 1, a PMOS charges the next stretch of wire from the mesh rail (${n('l3_mesh_v')}); a 0 after a 0 moves nothing. That is why random data costs several times zeros on the mesh.`}),
  rep2: () => L3P.rep1(), wireC: () => L3P.rep1(), bitE: () => L3P.link(),
  lsin: () => ({kick: 'L3 · transistors', title: 'The level shifter', badge: [['generic', 'textbook'], ['documented', 'that it is there']], facts: 'xing',
    what: `The reply arrives at the mesh rail's swing, ${n('l3_mesh_v')}, and must drive the Shire Channel's logic, whose rail is asked (its SRAM arrays sit on ${n('l3_sram_v')}). A cross-coupled PMOS pair on the high rail over an NMOS pair driven by the signal and its complement: the input pulls one side down and the pair snaps the other up to the high rail. The ET RTL models it as a buffer; the physical cell is not documented.`}),
  ls: () => L3P.lsin(), sync: () => L3P.lsin(),
};
// the shared panel and cell drawings: the L2's panels, relabelled (their facts come from D.parts.l3)
['periph', 'pre', 'mux', 'sa', 'olat', 'wl', 'cell', 'wd', 'half', 'leak', 'icg', 'trim', 'geom', 'band', 'array', 'panel'].forEach(k => {
  L3P[k] = kickAs(L2P[k], /^(periph|icg|trim|geom|band|array|panel)$/.test(k) ? 'L3 · panel' : 'L3 · cell');
});

L3P.band = () => ({kick: 'L3 · panel', title: 'The panel\'s rows', badge: [['documented', 'spec and RTL']], facts: 'band',
  what: `The scratchpad is the lowest ${n('scp_rows')} rows of each panel and the L2 the 512 above them; the L3 is the top quarter, ${n('l3_rows')}, the rows this level lights.`});
/* ---- the L3's accesses ---- */
const tileOf = (c, key, id) => (c.ap.parts[key] || []).filter(g => g._ctx.id === id);
function litTile(c, key, id) { const gs = tileOf(c, key, id); gs.forEach(g => { g.classList.add('hi'); TOUCH.add(g); if (g._box) ringAround(c.fx, g._box); }); svg.classList.add('fdim'); return gs; }
const RH3 = () => { const I = I3(); return [SHC[I.req], SHC[I.home]]; };
async function subTags(tok, c, lab) {
  await Promise.all([macroRead(tok, c, c.ap.macros.tag, lab || `row ${I3().set}`, {key: 'tagram'}), macroRead(tok, c, c.ap.macros.state, '', {key: 'stateram'})]);
}
const L3A = SCENES.l3.access = {};
L3A['load-hit'] = {
  led: () => [[null, null], [src(nt('l2_spec_miss') + ' (spec)', nf('l2_spec_miss')), null], [null, null], [cn(12 * I3().hops, 'l3:l3.hop', 0) + ' both ways', null], [null, null],
    [src(nt('l3_ram2'), nf('l3_ram2')), null], [src(nt('l3_ram2'), nf('l3_ram2')), null], [null, src('≈ ' + nt('l3_hop69') + ' a hop', nf('l3_hop69'))], [null, null]],
  tot: () => ({c: `${n('l3_fit_c')}: ${cn(fit3(I3().hops), 'l3:l3.lat-fit', 1)} here`, e: `${n('lad_e_l3')}/B, ${n('l3_e_line')} a line`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `An L3 hit, load to use: ${n('l3_fit_c')} (three cards); from shire ${I3().req} to home ${I3().home}, ${I3().hops} hops: ${cn(fit3(I3().hops), 'l3:l3.lat-fit', 1)} cycles.`,
  steps: [
    {name: 'L1 miss', where: 'chip', say: () => `At the requester R, shire ${I3().req}, the load misses its L1: a miss handler asks the L2 bank PA[7:6] (the L1 tab plays this)`,
      run: async (tok, c) => { const [R] = RH3(); litTile(c, 'shire', R.id); const p = c.ap.P[ckey(R)]; PKM(c, p); sayAt(c, p.x, p.y, ['R: the L1 missed', 'see the L1 (key 1)'], {side: 'r'}); await pulse(tok, c.fx, p, 1000); }},
    {name: 'L2 miss', where: 'chip', say: () => `R's L2 misses too: its request-queue entry stays for the fill, and the read leaves for the line's home (the spec: ${n('l2_spec_miss')} shire clocks for that path)`,
      run: async (tok, c) => { const [R] = RH3(); litTile(c, 'shire', R.id); const p = c.ap.P[ckey(R)]; PKM(c, p); sayAt(c, p.x, p.y, ['R\'s L2 misses', `the spec: ${nt('l2_spec_miss')} shire clocks`, 'see the L2 (key 2)'], {side: 'r'}); counter(c, `${nt('l2_spec_miss')} shire clocks`, 'the spec, both ways'); await pulse(tok, c.fx, p, 1000); }},
    {name: 'Into the mesh', where: 'hop', dive: ['rep'], say: () => `The to_l3 master takes lane PA[12:11] = ${I3().bank}, the bank it will use at the home (re-implementation RTL, to confirm); a VC FIFO drops it to the mesh's ${n('l3_mesh_v')}`,
      run: async (tok, c) => {
        lit(c, ['bankR', 'tol3', 'vcdown'], {noRing: true});
        const P = c.ap.hopP, pk = packet(c.fx, 'var(--c2)', 11); at(pk, P[0]);
        await travel(tok, c.fx, pk, P.slice(0, 4), 1500);
        sayAt(c, 566, 190, [`lane PA[12:11] = ${I3().bank}`, '(re-implementation RTL, to confirm)', 'level shifters, 2-flop synchroniser'], {side: 'd'});
      },
      deep: {rep: async (tok, c) => { await lsLift(tok, c); fadeIn(T(c.fx, 580, 686, 'drawn: up; down needs only an inverter (textbook)', 't-sm halo', 'start')); }}},
    {name: 'Across the mesh', where: 'chip', dive: ['rep'], say: () => `The request crosses ${I3().hops} hop${I3().hops === 1 ? '' : 's'} to the home, shire ${I3().home}: ${n('l3_hopcyc')} per hop, counted both ways`,
      run: async (tok, c) => {
        const [R, H] = RH3(); litTile(c, 'shire', R.id); litTile(c, 'shire', H.id);
        counter(c, `${I3().hops} hops × ${nt('l3_hopcyc')}`, 'round trip, measured');
        await hopTravel(tok, c, R, H, {label: (k, n0) => `hop ${k} of ${n0}`});
      },
      deep: {rep: (tok, c) => repToggle(tok, c, {})}},
    {name: 'L3-slave port', where: 'hbank', say: () => `At the home, the L3-slave FIFO and a request-queue entry (${n('l3_reqq21')} are kept for L3 requests); L3 requests win the sub-bank over the shire's own`,
      run: async (tok, c) => {
        lit(c, ['l3fifo', 'reqq']); slotOn(c, c.ap.q[50]);
        const pk = PKM(c, c.ap.fifo); await travel(tok, c.fx, pk, [c.ap.fifo, c.ap.rq, c.ap.arbP], 1100);
        lit(c, 'arb'); lit(c, 'subbanks', {i: I3().sub});
        const s = c.ap.sub[I3().sub]; await travel(tok, c.fx, pk, [c.ap.arbP, {x: 597, y: 212}, {x: s.x, y: 212}, s], 800);
        sayAt(c, 597, 200, ['L3-slave requests', 'win the sub-bank'], {side: 'd'});
      }},
    {name: 'Tag phase', where: 'sub', dive: ['cell'], say: () => `The tag and tag-state macros read row ${I3().set} (768 + PA[22:15]): ${n('l3_ram2')}; ECC; four compares find way ${I3().way}`,
      run: async (tok, c) => {
        counter(c, `tap … ta1: ${nt('l3_ram2')}`, 'the RAM delay, spec default');
        await subTags(tok, c); alive(tok);
        lit(c, 'ecc', {i: 0}); lit(c, 'cmp');
        c.ap.eq.forEach((p, k) => fadeIn(T(c.fx, p.x, p.y - 24, k === I3().way ? 'hit' : 'no', k === I3().way ? 't-smb halo' : 't-sm halo', 'middle')));
        await wait(tok, 400);
      },
      deep: {cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'Data phase', where: 'sub', dive: ['panel', 'cell'], say: () => SCENES.l3.zero ? 'A zero line: the zero bit is set, so the data macros are not clocked and the bank returns zeros; the LRU is still written'
      : `The four panels read row ${fnum(I3().row)} = {set, hit way}: ${n('l2_line')}; ECC; the new LRU code goes back through the tag-state RAM's second port`,
      run: async (tok, c) => {
        if (SCENES.l3.zero) {
          lit(c, 'zero'); idle(c, c.ap.parts.data, 'not clocked: a zero line', {at: {x: 740, y: 470}});
          await sweep(tok, c, [c.ap.norOut, {x: 386, y: 370}], {ms: 500, label: 'zero bit = 1', at: {x: 300, y: 350}, dx: 0, dy: -10});
        } else {
          counter(c, `dap … da1: ${nt('l3_ram2')}`, 'the RAM delay, spec default');
          await Promise.all(c.ap.panels.map((m, p) => macroRead(tok, c, m, p ? '' : `row ${fnum(I3().row)}`, {key: 'data', i: p})));
          lit(c, 'ecc', {i: 1});
        }
        const m = c.ap.macros.state; lit(c, 'stateram');
        await sweep(tok, c, [{x: m.x + m.w - 12, y: m.rowY + 6}, {x: m.x + 12, y: m.rowY + 6}], {ms: 500, w: 4, col: 'var(--c7)', label: 'LRU', at: {x: m.x + 14, y: m.rowY + 6}, dx: 0, dy: -40});
        fadeIn(T(c.fx, m.x + 14, m.rowY - 12, 'written', 't-labb halo', 'start'));   // above the row: the L3's rows are near the macro's foot
      },
      deep: {panel: (tok, c) => panelRead(tok, c), cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'The reply', where: 'chip', dive: ['rep'], say: () => `The ${n('l3_reply')} goes back ${I3().hops} hop${I3().hops === 1 ? '' : 's'} to R: ${n('l3_hop69')} per hop on the mesh rail for random data (derived), ${n('l3_hop47')} measured`,
      run: async (tok, c) => {
        const [R, H] = RH3(); litTile(c, 'shire', R.id); litTile(c, 'shire', H.id);
        counter(c, `≈ ${nt('l3_hop69')} a hop`, 'mesh rail, random data (derived)');
        await hopTravel(tok, c, H, R, {col: 'var(--c7)', w: 9, label: (k, n0) => `hop ${k} of ${n0}`});
      },
      deep: {rep: (tok, c) => repToggle(tok, c, {})}},
    {name: 'Fills', where: 'chip', say: () => `R's L2 is filled (the tags, the state and four panels, none for a zero line), then its L1: ${cn(fit3(I3().hops), 'l3:l3.lat-fit', 1)} cycles by the fit`,
      run: async (tok, c) => {
        const [R] = RH3(); litTile(c, 'shire', R.id); const p = c.ap.P[ckey(R)];
        counter(c, `${fnum(fit3(I3().hops), 1)} cycles`, 'the fit, three cards');
        PKM(c, p, 'var(--c7)'); await pulse(tok, c.fx, p, 900, 'var(--c7)');
        sayAt(c, p.x, p.y, [`${fnum(fit3(I3().hops), 1)} cycles load to use`, `${nt('lad_e_l3')}/B, three cards`], {side: 'r'});
      }},
  ]};
L3A['write-around'] = {
  led: [[null, null], [null, null], [null, null]], tot: () => ({c: 'not measured apart', e: 'not measured apart'}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => 'Writes reach the L3 as victims or write-arounds: only the written quadwords\' panels are enabled, and an all-zero line sets the zero bit instead.',
  steps: [
    {name: 'Scalar store', where: 'chip', say: () => 'A scalar store allocates its line in the L1; the dirty line later leaves the L1, then the L2, whose victim goes over to_l3 to its home',
      run: async (tok, c) => { const [R, H] = RH3(); litTile(c, 'shire', R.id); litTile(c, 'shire', H.id); await hopTravel(tok, c, R, H, {col: 'var(--c5)'}); sayAt(c, c.ap.P[ckey(H)].x, c.ap.P[ckey(H)].y, ['an L2 victim', 'written at its home'], {side: 'r'}); }},
    {name: 'Tensor store', where: 'chip', say: () => `A tensor store is a write-around: its quadwords coalesce in R's L2 buffer (${n('l3_coal')}) and the line goes to the home when all four are written`,
      run: async (tok, c) => { const [R, H] = RH3(); litTile(c, 'shire', R.id); const p = c.ap.P[ckey(R)]; sayAt(c, p.x, p.y, ['coalesced in R\'s L2', 'then sent when full'], {side: 'r'}); await wait(tok, 600); await hopTravel(tok, c, R, H, {col: 'var(--c5)', w: 9}); }},
    {name: 'L3 write', where: 'sub', dive: ['cell'], say: () => 'At the home: tags and state read; only the panels of written quadwords are enabled; an all-zero full line sets the zero bit and writes no data',
      run: async (tok, c) => {
        await subTags(tok, c, 'dirty');
        await Promise.all(c.ap.panels.slice(0, 2).map((m, p) => macroRead(tok, c, m, p ? '' : 'written', {key: 'data', i: p})));
        idle(c, [c.ap.parts.data[2], c.ap.parts.data[3]].filter(Boolean), 'not enabled', {at: {x: 996, y: 470}});
      },
      deep: {cell: cellWrite}},
  ]};
L3A.miss = {
  led: [[src(nt('l3_miss42') + ' (spec)', nf('l3_miss42')), null], [src(nt('l3_dram91'), nf('l3_dram91')), null], [null, null], [null, null]],
  tot: () => ({c: `+ ${n('l3_dram91')}: the DRAM tab`, e: '—'}), ask: {c: 'ask-cache-latency'},
  cap: () => `An L3 miss: the home asks memory shire PA[8:6] = ${I3().ms} over to_sys, then fills the line: ${n('l3_dram91')} more.`,
  steps: [
    {name: 'Tag miss', where: 'sub', say: () => `No way matches at the home; the LRU code picks the victim way (the spec: an L3 miss ${n('l3_miss42')} before the NoC and memory)`,
      run: async (tok, c) => { await subTags(tok, c); lit(c, 'cmp'); c.ap.eq.forEach(p => fadeIn(T(c.fx, p.x, p.y - 24, 'no', 't-sm halo', 'middle'))); idle(c, c.ap.parts.data, 'not read: a miss', {at: {x: 740, y: 470}}); }},
    {name: 'To memory', where: 'chip', handoff: {lv: 'dram', k: 'load', at: 0, label: 'Continue at the DRAM'}, say: () => `The read leaves over to_sys for memory shire ${I3().ms} (PA[8:6]): ${n('l3_dram91')} more; the DRAM tab follows it`,
      run: async (tok, c) => {
        const H = SHC[I3().home], M = MSC[I3().ms]; litTile(c, 'shire', H.id); litTile(c, 'memshire', M.id);
        const h = hopsC(H, M); counter(c, `${fnum(V('l3_dram91'))} + 12 × ${h} hops`, 'the leg past the L3, measured');
        await hopTravel(tok, c, H, M, {col: 'var(--c5)'});
        sayAt(c, c.ap.P[ckey(M)].x, c.ap.P[ckey(M)].y, ['to the memory shire', 'continue at the DRAM (key 5)'], {side: 'r'});
      }},
    {name: 'Fill', where: 'sub', dive: ['cell'], say: () => 'The fill reads the victim (written back over to_sys if dirty) and writes the tag, the state and the four panels; an all-zero line sets the zero bit instead',
      run: async (tok, c) => { await subTags(tok, c, 'new tag'); await Promise.all(c.ap.panels.map((m, p) => macroRead(tok, c, m, p ? '' : 'victim out,\nline in', {key: 'data', i: p}))); counter(c, 'a sub-bank held 4 cycles', 'read then write, 2-cycle RAMs'); },
      deep: {cell: cellWrite}},
    {name: 'Partial line', where: 'hbank', say: () => 'A read that hits a partial line (left by write-arounds) first writes it to memory, then reads the whole line back',
      run: async (tok, c) => { lit(c, ['partial', 'tosys']); const pk = PKM(c, c.ap.sub[I3().sub], 'var(--c5)'); await travel(tok, c.fx, pk, [c.ap.sub[I3().sub], {x: c.ap.sub[I3().sub].x, y: 440}, {x: 888, y: 440}, c.ap.tosysP], 1000, {col: 'var(--c5)'}); }},
  ]};
L3A.atomic = {
  led: [[src(nt('l3_atomic'), nf('l3_atomic')), src(nt('l3_atomW'), nf('l3_atomW'))]], tot: () => ({c: `${n('l3_atomic')} each, contended`, e: `${n('l3_atomW')} over idle`}),
  cap: () => `A global atomic runs in the line's home bank: read, operate, write, the sub-bank busy throughout; ${n('l3_atomic')} per contended atomic.`,
  steps: [
    {name: 'Atomic block', where: 'hbank', say: () => `The home bank's atomic block reads the line, applies the operation and writes it back: ${n('l3_atomic')} per contended atomic, ${n('l3_atom216')} for an uncontended remote one`,
      run: async (tok, c) => {
        lit(c, ['atomic', 'reqq']); lit(c, 'subbanks', {i: I3().sub}); counter(c, nt('l3_atomic'), 'per contended atomic, measured');
        const s = c.ap.sub[I3().sub], pk = PKM(c, c.ap.atom, 'var(--c5)');
        for (let k = 0; k < 2; k++) { await travel(tok, c.fx, pk, [c.ap.atom, {x: c.ap.atom.x, y: 212}, {x: s.x, y: 212}, s], 600, {col: 'var(--c5)'}); await travel(tok, c.fx, pk, [s, {x: s.x, y: 212}, {x: c.ap.atom.x, y: 212}, c.ap.atom], 600, {col: 'var(--c5)'}); }
        sayAt(c, 991, 200, ['read · op · write', 'the sub-bank busy'], {side: 'd'});
      }},
  ]};
L3A.refresh = {
  led: [[null, null]], tot: () => ({c: 'none', e: `leakage: at most ${n('l3_leakW')} for the L3`}),
  cap: () => `Refresh? None: the spec describes none for these RAMs. The standing cost is leakage, at most ${n('leak_mb')} at 80 °C.`,
  steps: [
    {name: 'No refresh', where: 'cell', say: () => `No refresh: the spec describes none, only deep sleep and shutdown for idle shires; the cells leak, at most ${n('leak_mb')} at 80 °C`,
      run: async (tok, c) => { counter(c, 'no refresh', 'static storage (if SRAM)'); cellLeak(c, 'l3:l3.leakage'); await wait(tok, 1200); }},
  ]};
SCENES.l3.accOrder = [['load-hit', 'Load hit', 'Load'], ['write-around', 'Write-around', 'Write'], ['miss', 'Miss → DRAM', 'Miss'], ['atomic', 'Atomic', 'Atomic'], ['refresh', 'Refresh?', 'Refresh?']];
SCENES.l3.tour = [
  {name: 'The chip', path: ['chip'], panel: 'homebox', hi: ['homebox', 'shire', 'fit'],
    cap: () => `The L3 is ${n('l3_mb')} spread over the 32 compute shires: a line's home is PA[10:6], and each hop to it costs ${n('l3_hopcyc')}`,
    sub: () => `The map is measured; the hop count between requester and home sets the latency: ${n('l3_fit_c')}.`},
  {access: 'load-hit'},
  {name: 'A mesh hop', path: ['chip', 'hop'], panel: 'link', hi: ['vcdown', 'router', 'link', 'flits'], play: (tok, c) => hopPlay(tok, c),
    cap: () => `A hop: VC FIFOs into and out of the ${n('l3_mesh_v')} mesh, a router, ${n('l3_hopmm')} of repeated wire`,
    sub: () => 'The router is drawn from the textbook: its pipeline, layer and flit width are asked.'},
  {name: 'The home bank', path: ['chip', 'home', 'hbank'], panel: 'arb', hi: ['arb', 'reqq', 'rbuf'],
    cap: () => 'At the home, L3 requests win the sub-bank over the shire\'s own, and never use the read buffer',
    sub: () => `${n('l3_reqq21')} of the request queue are kept for them; two errata record the home's own requests starved.`},
  {name: 'Zero lines', path: ['chip', 'home', 'hbank', 'sub'], panel: 'zero', hi: ['zero', 'data'],
    cap: () => `A zero line sets the zero bit and skips the data macros: L3 reads cost ${n('l3_e_cont')}`,
    sub: () => 'How much of that saving is the skip and how much is data-dependent switching is an experiment away (asked).'},
  {name: 'The cell', path: ['chip', 'home', 'hbank', 'sub', 'panel', 'cell'], panel: 'cell', hi: ['cell'], dive: true, play: (tok, c) => cellRead(tok, c, {half: true}),
    cap: () => `The same cell as the L2's, drawn as a textbook 6T cell; it leaks at most ${n('leak_mb')} at 80 °C`,
    sub: () => 'The spec says SRAM; the lab lead said the chip is not using SRAM; the bitcell is the first ask.'},
  {access: 'miss'},
  {name: 'What does not add up', path: ['chip'], panel: 'latency', hi: ['fit', 'byhome'],
    cap: () => `Of the fitted constant, ${n('l3_72')} scale with the clock and ${n('l3_61')} do not; the spec's shire clocks add up to more`,
    sub: () => 'Where each cycle goes, the router pipeline, the bitcell and the zero-line share are asked; the list is under the diagram.'},
];

/* ================= Scratchpad (key 4, #scp): the same panels, without the tags ================= */
/* The scratchpad's own address format (scp.addr): [39:31] = 9'h1, [30] format, [29:23] shire (0x7F: the requester's
   own), [22:12] set, [11:10] way, [9:8] sub-bank, [7:6] bank, [5:0] byte; a line sits in panel row PA[21:10] of its
   sub-bank's four panels (scp.addr-row). The example: set 0x123, way 2, sub-bank 1, bank 3, byte 8, in the own shire
   (the 'self' ID, as the vendor's scw_power_virus uses it); a remote access targets the shire 16 IDs away, as the
   measurements do (scp.bw-remote, scp.e-remote). */
const SCPA = {set: 0x123, way: 2, sub: 1, bank: 3, off: 8};
const SELF = 0x7F;
function scpPA(shire) { return 2 ** 31 + shire * 2 ** 23 + SCPA.set * 2 ** 12 + SCPA.way * 2 ** 10 + SCPA.sub * 2 ** 8 + SCPA.bank * 2 ** 6 + SCPA.off; }
function decS(pa) {
  const shire = bits(pa, 29, 23), set = bits(pa, 22, 12), way = bits(pa, 11, 10), sub = bits(pa, 9, 8), bank = bits(pa, 7, 6);
  return {region: bits(pa, 39, 31), fmt: bits(pa, 30, 30), shire, set, way, sub, bank, row: set * 4 + way, qw: bits(pa, 5, 4), byte: bits(pa, 5, 0)};
}
const IS = () => SCENES.scp.inst;
const fitS = h => V('scp_remote') + V('scp_hop12') * h;   // scp.lat-remote: 99.84 + 12.00 cycles per hop, three cards
const REMOTE = new Set(['remote-load', 'remote-store', 'atomic']);
const scpRemote = () => !!(AC.k && REMOTE.has(AC.k) && Z.lv === 'scp');

/* the address format bar: the 40 bits, each field its width, the example's values */
function scpFmt(L, ap, x0, y0, w, pa) {
  const a = decS(pa), k = w / 40;
  const F0 = [['region', 39, 31, '9\'h1'], ['fmt', 30, 30, a.fmt], ['shire', 29, 23, a.shire === SELF ? '0x7F self' : a.shire], ['set', 22, 12, '0x' + a.set.toString(16)], ['way', 11, 10, a.way], ['sub', 9, 8, a.sub], ['bank', 7, 6, a.bank], ['byte', 5, 0, a.byte]];
  const g = comp(L, 'fmt', {}, 'The scratchpad\'s address format: region, format, shire, set, way, sub-bank, bank, byte');
  ap.fld = {};
  F0.forEach(([nm, hi, lo, v]) => {
    // the one-bit fmt field takes 14 units from region, so that its name fits
    const x = x0 + (39 - hi) * k - (nm === 'fmt' ? 14 : 0), ww = (hi - lo + 1) * k + (nm === 'fmt' ? 14 : nm === 'region' ? -14 : 0);
    S(E('rect', {x, y: y0, width: ww - 3, height: 64, rx: 4}, g), {fill: nm === 'region' || nm === 'fmt' ? 'var(--ink-2)' : 'var(--c7)', fillOpacity: 0.12, stroke: nm === 'region' || nm === 'fmt' ? 'var(--ink-2)' : 'var(--c7)', strokeWidth: 1.5});
    T(g, x + ww / 2, y0 + 24, ww > 110 ? `${nm} [${hi}:${lo}]` : nm, 't-sm', 'middle', 'scp:scp.addr');
    T(g, x + ww / 2, y0 + 50, String(v), 't-smb', 'middle', 'scp:scp.addr');
    ap.fld[nm] = {x, y: y0, w: ww - 3, h: 64};
  });
  g._box = {x: x0, y: y0, w, h: 64};
  E('rect', {class: 'ring', x: x0 - 5, y: y0 - 5, width: w + 10, height: 74, rx: 8}, g);
  return g;
}

function buildScpChip(L, ap, inst) {
  const R = SHC[inst.req], Tg = SHC[inst.shire], hh = hopsC(R, Tg);
  frame(L, {title: `Chip · ${nt('scp_80')} of scratchpad`, f: nf('scp_80'), sub: `${nt('scp_size')} in every shire, addressable by any agent; the address names the shire`, subf: nf('scp_size') + ' scp:scp.what',
    tags: [['documented', 'measured, spec']]});
  scpFmt(L, ap, -150, 12, 1228, inst.pa);
  chipMap(L, ap, {C: 66, X0: -150, Y0: 96, tile: c => c.type === 'cshire'
    ? {marks: [c.id === inst.req ? 'R' : null, inst.remote && c.id === inst.shire ? 'T' : null].filter(Boolean), hi: c.id === inst.req || c.id === inst.shire,
      child: c.id === inst.shire ? 'shire' : null, cur: c.id === inst.shire}
    : {fo: 0.04}});
  const rc = routeC(R, inst.remote ? Tg : SHC[(inst.req + 16) % 32]), P = rc.map(c => ap.P[ckey(c)]);
  if (inst.remote && P.length > 1) routeLine(L, ap, P);
  const p0 = P[0], q0 = P[1] || ap.P[ckey(CELLS.find(x => hopsC(x, R) === 1))];
  ap.hopBox = {x: (p0.x + q0.x) / 2 - 15, y: (p0.y + q0.y) / 2 - 15, w: 30, h: 30};
  part(L, 'link', ap.hopBox.x, ap.hopBox.y, 30, 30, COL.net, '', {child: 'hop', cur: true, fo: 0.3, rx: 15, label: 'A mesh hop: Enter zooms into it'});
  T(L, -150, 672, `the map: measured on three cards${inst.remote ? ` · R → T: ${hh} hops` : ''}`, 't-sm', 'start', MAPF);
  const X = 290, W = 788;
  part(L, 'own', X, 96, 384, 164, COL.logic, 'from its own shire', {fo: 0.06, sub: [{t: `${nt('lad_scp_lat')} load to use`, f: nf('lad_scp_lat')}, {t: `as fast as an L2 hit; never a miss`, f: 'scp:scp.same-as-l2'}, {t: `${nt('scp_bw')} chip-wide`, f: nf('scp_bw')}, {t: `${nt('lad_e_scp')}–${nt('lad_e_scp1')} pJ/B (zeros–random)`, f: nf('lad_e_scp')}]});
  part(L, 'remote', X + 404, 96, W - 404, 164, COL.net, 'from another shire', {fo: 0.06, sub: [{t: nt('scp_remote'), f: nf('scp_remote')}, {t: `leaving the shire: ${nt('scp_leave')}`, f: nf('scp_leave')}, {t: `${nt('scp_bw_rem')} chip-wide, 16 IDs away`, f: nf('scp_bw_rem')}, {t: `${nt('scp_rem1')} pJ/B random`, f: nf('scp_rem1')}]});
  part(L, 'size', X, 276, W, 96, COL.store, 'the same macros as the L2 and the L3', {fo: 0.06, sub: [{t: `rows 0–2,559 of every data panel (mode M0); ${nt('scp_panels64')} per shire`, f: 'scp:scp.m0-rows ' + nf('scp_panels64')}, {t: 'no tags: the way is PA[11:10], and nothing is ever evicted', f: 'scp:scp.always-hit scp:scp.no-victims'}]});
  part(L, 'fmt1', X, 388, W, 76, COL.logic, 'format 1: lines spread over shires', {fo: 0.04, sub: [{t: 'bit 30 = 1 (minions only): the shire ID in bits [29:28] and [10:6]', f: 'scp:scp.format1'}]});
  part(L, 'relay', X, 480, W, 110, COL.aux, 'handing work to the next shire', {fo: 0.06, sub: [{t: `${nt('scp_relay')} (DRAM / next shire / own)`, f: nf('scp_relay')}, {t: `${nt('scp_relay_bw')} GB/s through DRAM`, f: nf('scp_relay_bw')}]});
  railBand(L, X, 606, W, 50, 'pat-mesh', 'The mesh rail');
  T(L, X + 14, 638, `mesh: ${nt('l3_mesh_v')} · each hop ${nt('scp_hop12')} round trip`, 't-sm halo', 'start', nf('l3_mesh_v') + ' ' + nf('scp_hop12'));
}

/* the shire: the minion's TensorLoad into its L1 scratchpad (latch RAM), the neighbourhoods, the crossbars, the banks;
   the four candidates for the bandwidth cap carry a ? (scp.u-bw) */
function buildScpShire(L, ap, inst) {
  frame(L, {title: `Shire ${inst.shire}${inst.remote ? ' (the target)' : ''} · ${nt('scp_size')} of scratchpad`, f: nf('scp_size'), sub: 'a logical drawing; the four ? mark the candidates for the 128 B per cycle cap', subf: 'scp:scp.u-bw',
    tags: [['unknown', '? what caps it · asked'], ['documented', 'documented']]});
  railBand(L, -150, 12, 1228, 252, 'pat-lv', 'The minions\' low-voltage region', 'lvband');
  railBand(L, -150, 270, 1228, 420, 'pat-hv', 'The Shire Channel', 'rail');
  S(E('line', {x1: -150, y1: 267, x2: 1078, y2: 267}, L), {stroke: 'var(--ink-2)', strokeWidth: 2, strokeDasharray: '10 8'});
  ap.min = []; ap.fifo = []; ap.arb = [];
  for (let k = 0; k < 4; k++) {
    const x = -136 + k * 276, w = 266;
    const g = part(L, 'nbr', x, 22, w, 170, COL.logic, `neighbourhood ${k}`, {ctx: {i: k}, fo: 0.05});
    ap.min[k] = [];
    for (let m = 0; m < 8; m++) {
      const mx = x + 12 + (m % 4) * 62, my = 42 + Math.floor(m / 4) * 44;
      S(E('rect', {x: mx, y: my + 12, width: 56, height: 34, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.2, stroke: 'var(--c1)', strokeWidth: 1.25});
      T(g, mx + 28, my + 35, 'M' + m, 't-sm', 'middle');
      ap.min[k].push({x: mx + 28, y: my + 29});
    }
    S(E('rect', {x: x + 12, y: 146, width: w - 24, height: 34, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c5)', fillOpacity: 0.12, stroke: 'var(--c5)', strokeWidth: 1.25});
    T(g, x + w / 2, 169, 'Fill FIFO · 512-bit link', 't-sm', 'middle', 'scp:scp.bw-spec-port');
    ap.arb[k] = {x: x + w / 2, y: 140};   // the requests run in the gap above the Fill FIFO's label
    const gf = part(L, 'fifo', x + 12, 204, w - 24, 56, COL.xing, '', {ctx: {i: k}, fo: 0.08, label: `Neighbourhood ${k}'s bank FIFOs: into the HV region`});
    ap.fifo[k] = [];
    ['0', '1', '2', '3', 'UC'].forEach((b, i) => { const fx0 = x + 20 + i * 47; S(E('rect', {x: fx0, y: 210, width: 40, height: 44, rx: 4, 'pointer-events': 'none'}, gf), {fill: 'var(--c5)', fillOpacity: 0.18, stroke: 'var(--c5)', strokeWidth: 1.25}); T(gf, fx0 + 20, 238, b, 't-sm', 'middle'); ap.fifo[k].push({x: fx0 + 20, y: 232}); });
  }
  // minion 0's TensorLoad unit and its L1 scratchpad (latch RAM, the L1 tab)
  part(L, 'l1scp', -124, 54, 56, 34, COL.store, '', {fo: 0.3, label: 'Minion 0: its TensorLoad unit and its L1 scratchpad, latch RAM (the L1 tab)'});
  ap.tl = ap.min[0][0];
  part(L, 'reqxbar', -136, 286, 1204, 32, COL.net, 'request crossbar: 5 clients → 4 banks + UC', {ty: 23, tcls: 't-sm', fo: 0.14});
  ap.bank = [];
  for (let b = 0; b < 4; b++) {
    const x = -136 + b * 252, w = 238;
    const g = part(L, 'banks', x, 330, w, 124, COL.store, `bank ${b}`, {ctx: {i: b, inst: {bank: b}}, child: 'bank', cur: b === inst.bank, fo: 0.08, sub: [`PA[7:6] = ${b}`]});
    for (let s = 0; s < 4; s++) S(E('rect', {x: x + 12 + s * 56, y: 392, width: 48, height: 52, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.18, stroke: 'var(--c3)', strokeWidth: 1.25});
    ap.bank[b] = {x: x + w / 2, y: 418, box: {x, y: 330, w, h: 124}};
  }
  part(L, 'uc', 872, 330, 196, 124, COL.aux, 'UC block', {sub: ['atomics to the', 'scratchpad go here']});
  part(L, 'rspxbar', -136, 466, 1204, 32, COL.net, 'response crossbar: broadcasts a cooperative line to every neighbourhood', {ty: 23, tcls: 't-sm', fo: 0.14, f: 'scp:scp.coop'});
  // one sub-bank's rows: the scratchpad is sets 0-639
  const gp = comp(L, 'partition', {}, 'One sub-bank\'s 1,024 sets in mode M0: the scratchpad is sets 0 to 639');
  T(gp, -136, 532, 'one sub-bank\'s 1,024 sets (mode M0)', 't-smb halo');
  [['scratchpad · sets 0–639', 0, 640, 'var(--c2)'], ['L2 · 640–767', 640, 128, 'var(--c7)'], ['L3 · 768–1023', 768, 256, 'var(--c3)']].forEach(([t, s0, ns, col]) => {
    const x = -136 + s0 / 1024 * 820, w = ns / 1024 * 820, on = col === 'var(--c2)';
    S(E('rect', {x, y: 542, width: w - 3, height: 34, rx: 4}, gp), {fill: col, fillOpacity: on ? 0.45 : 0.2, stroke: col, strokeWidth: on ? 3 : 1.25});
    T(gp, x + 8, 565, t.split(' · ')[0], on ? 't-smb' : 't-sm', 'start', 'scp:scp.m0-rows');
    T(gp, x + 4, 596, t.split(' · ')[1], 't-sm', 'start', 'scp:scp.m0-rows');
  });
  gp._box = {x: -136, y: 542, w: 820, h: 34};
  part(L, 'meshstop', 710, 512, 358, 110, COL.net, 'mesh stop', {sub: [{t: 'remote requests: 4 L3-slave ports', f: 'scp:scp.what l3:l3.ports'}, {t: 'they win the sub-bank', f: 'scp:scp.reqq'}]});
  T(L, -136, 632, `own-shire stream: ${nt('scp_128')}, half the four banks' 256 B`, 't-sm halo', 'start', nf('scp_128'));
  T(L, -136, 654, `one neighbourhood alone: ${nt('scp_50')}`, 't-sm halo', 'start', nf('scp_50'));
  // the ? of the bandwidth question, on its four candidates
  const gq = comp(L, 'bneck', {}, 'What caps the stream at 128 B per shire-cycle: sub-bank busy time, the response crossbar, the Fill FIFO or the minion\'s 256-bit port; unknown, asked');
  [[-136 + inst.bank * 252 + 214, 344], [1050, 482], [106, 163], [-65, 93]].forEach(([x, y]) => {
    S(E('circle', {cx: x, cy: y, r: 13}, gq), {fill: 'var(--surface)', stroke: 'var(--warn)', strokeWidth: 2, strokeDasharray: '4 3'});
    T(gq, x, y + 9, '?', 't-q', 'middle');
  });
  gq._box = {x: -136, y: 40, w: 1210, h: 450};
  ap.xbarY = 302; ap.rxbarY = 482; ap.mesh = {x: 889, y: 560};
}

function buildScpBank(L, ap, inst) {
  frame(L, {title: `Bank ${inst.bank} (PA[7:6]) of shire ${inst.shire}`, sub: 'the L2\'s bank and pipeline; for a scratchpad address the tag reads are squashed', subf: 'scp:scp.always-hit',
    tags: [['documented', 'spec; tags squashed: re-implementation RTL']]});
  const gq = part(L, 'reqq', -150, 14, 330, 170, COL.logic, 'request queue', {sub: [{t: `64 · ${nt('l3_reqq21')} for L3-slave`, f: 'scp:scp.reqq ' + nf('l3_reqq21')}]});
  ap.q = [];
  for (let i = 0; i < 48; i++) { const x = -138 + (i % 12) * 26, y = 84 + Math.floor(i / 12) * 24; ap.q.push(S(E('rect', {x, y, width: 22, height: 19, rx: 3, 'pointer-events': 'none'}, gq), {fill: 'var(--c1)', fillOpacity: 0.15, stroke: 'var(--c1)', strokeWidth: 1})); }
  part(L, 'arb', 196, 14, 200, 170, COL.logic, 'arbitration', {sub: [{t: 'remote (L3-slave)', f: 'scp:scp.reqq'}, {t: 'requests first', f: 'scp:scp.reqq'}, {t: 'range: < 640 sets', f: 'scp:scp.size'}]});
  const gr = part(L, 'rbuf', 412, 14, 200, 170, COL.logic, 'read buffer', {sub: [{t: '8 lines; scratchpad', f: 'scp:scp.rbuf'}, {t: 'reads install here,', f: 'scp:scp.rbuf'}, {t: 'remote ones too', f: 'scp:scp.rbuf'}]});
  ap.rb = []; for (let i = 0; i < 8; i++) ap.rb.push(S(E('rect', {x: 424 + (i % 4) * 46, y: 136 + Math.floor(i / 4) * 22, width: 40, height: 17, rx: 3, 'pointer-events': 'none'}, gr), {fill: 'var(--c1)', fillOpacity: 0.15, stroke: 'var(--c1)', strokeWidth: 1}));
  part(L, 'dataq', 628, 14, 200, 170, COL.store, 'data queue', {sub: ['a line per entry:', 'store data waits', 'here']});
  part(L, 'atomic', 844, 14, 234, 170, COL.logic, 'atomic block', {sub: [{t: `${nt('scp_atomic')} each`, f: nf('scp_atomic')}, 'read · ALU · write', 'via the L3 slave']});
  ap.sub = [];
  for (let s = 0; s < 4; s++) {
    const x = -150 + s * 308, w = 296, on = s === inst.sub;
    const g = part(L, 'subbanks', x, 202, w, 268, COL.store, `sub-bank ${s}`, {ctx: {i: s}, fo: 0.06, sub: [`PA[9:8] = ${s}`]});
    // the tag macros, idle for a scratchpad access
    [[x + 10, 34, 'tag'], [x + 48, 30, 'state']].forEach(([mx, mw, lab]) => {
      S(E('rect', {x: mx, y: 262, width: mw, height: 196, rx: 3, 'pointer-events': 'none'}, g), {fill: 'url(#pat-hatch)', stroke: 'var(--ink-2)', strokeWidth: 1.25, strokeDasharray: '4 4'});
    });
    const px = [];
    for (let p = 0; p < 4; p++) {
      const mx = x + 90 + p * 50;
      S(E('rect', {x: mx, y: 262, width: 44, height: 196, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.2, stroke: 'var(--c3)', strokeWidth: 1.25});
      S(E('rect', {x: mx, y: 262, width: 44, height: 196 * 0.625, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: on ? 0.35 : 0.14});
      px.push({x: mx, y: 262, w: 44, h: 196});
    }
    ap.sub[s] = {x: x + w / 2, y: 330, box: {x, y: 202, w, h: 268}, panels: px};
  }
  // the lit sub-bank's panel of the example's quadword: where the zoom goes
  const pb = ap.sub[inst.sub].panels[inst.panel];
  const gz = part(L, 'data', pb.x, pb.y, pb.w, pb.h, COL.store, '', {ctx: {i: inst.panel}, child: 'panel', cur: true, fo: 0, label: `Data panel ${inst.panel} of sub-bank ${inst.sub}: Enter zooms in`});
  ap.panelBox = pb; ap.rowY = pb.y + (inst.row / 4096) * pb.h;
  { const sb = ap.sub[inst.sub].box; T(L, sb.x + sb.w - 10, 250, `row ${fnum(inst.row)}`, 't-smb halo', 'end', 'scp:scp.addr-row'); }
  // the pipeline: the tag stages elapse with nothing to read
  const gpp = comp(L, 'pipe', {}, 'The pipeline: the tag stages elapse with nothing read, which is why a scratchpad read takes as long as an L2 hit');
  ap.stg = {};
  STG.forEach((s, i) => {
    const x = -150 + i * 82, tag = i >= 3 && i <= 8, ram = i >= 9 && i <= 12;
    S(E('rect', {x, y: 494, width: 74, height: 46, rx: 5}, gpp), {fill: tag ? 'url(#pat-hatch)' : ram ? 'var(--c3)' : 'var(--c1)', fillOpacity: tag ? 1 : 0.14, stroke: tag ? 'var(--ink-2)' : ram ? 'var(--c3)' : 'var(--c1)', strokeWidth: 1.5, strokeDasharray: tag ? '4 4' : null});
    T(gpp, x + 37, 523, s, 't-mono', 'middle', 'scp:scp.pipe-stages');
    ap.stg[s] = {x, y: 494, w: 74, h: 46};
  });
  [['tag stages: squashed, but they elapse', 3, 8], ['data panels: 2 cycles', 9, 12]].forEach(([t, a0, b0]) => { const x0 = -150 + a0 * 82, x1 = -150 + b0 * 82 + 74; wire(gpp, [[x0, 552], [x0, 560], [x1, 560], [x1, 552]], 'thin'); T(gpp, (x0 + x1) / 2, 580, t, 't-sm', 'middle', 'scp:scp.pipe-stages scp:scp.always-hit'); });
  gpp._box = {x: -150, y: 494, w: 1224, h: 46};
  part(L, 'rules', -150, 600, 1228, 90, COL.logic, 'no misses, no victims, no zero-line shortcut', {fo: 0.03, sub: [{t: `writes of ${nt('scp_16B')} or more go straight to the panels, no read-modify-write`, f: nf('scp_16B')}, {t: 'the zero bit lives in the tag state, which is never read: zeros still read the panels', f: 'scp:scp.zero-state'}]});
  ap.rq = {x: 15, y: 60}; ap.arbP = {x: 296, y: 100}; ap.rbC = {x: 512, y: 100}; ap.dq = {x: 728, y: 100}; ap.atom = {x: 961, y: 100};
}

function buildScpPanel(L, ap, inst) {
  buildPanel(L, ap, {title: `Data panel ${inst.panel} · ${nt('l2_mdata_s')} · 1PUHD`, band: 'scp', row: inst.row,
    sub: `the scratchpad's rows are 0–2,559; this line is row PA[21:10] = ${fnum(inst.row)}`});
  const gt = ap.parts.trim[0];
  gt.setAttribute('data-child', 'vmin'); BAP.zg.vmin = gt; ap.trimBox = gt._box;
}
/* the Vmin inset: the data panel's trim table against the chip's three rails (why the L1 cannot be these panels) */
function buildVmin(L, ap, inst) {
  frame(L, {title: 'Vmin against the rails', sub: 'the data panel\'s trim table (spec) against the rails measured on the die', subf: 'scp:scp.vmin-table',
    tags: [['unknown', '? why latches · asked'], ['documented', 'spec, measured']]});
  const xv = v => -40 + (v - 450) * 1.95, Y0 = 70, RH = 60;
  const ga = comp(L, 'axis', {}, 'The voltage axis');
  S(E('line', {x1: xv(450), y1: 470, x2: xv(1000), y2: 470}, ga), {stroke: 'var(--axis)', strokeWidth: 1.5});
  [450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000].forEach(v => { S(E('line', {x1: xv(v), y1: 60, x2: xv(v), y2: 470}, ga), {stroke: 'var(--grid)', strokeWidth: 1}); T(ga, xv(v), 494, String(v), 't-sm', 'middle'); });
  T(ga, xv(1000), 518, 'mV', 't-sm', 'end');
  // the minion rail's range, by the firmware's limits (400-620 mV; the axis starts at 450)
  const gr0 = comp(L, 'railRange', {}, 'The minion rail\'s range under the firmware\'s limits, 400 to 620 millivolts');
  S(E('rect', {x: xv(450), y: 56, width: xv(620) - xv(450), height: 414}, gr0), {fill: 'var(--c1)', fillOpacity: 0.07, stroke: 'none'});
  T(gr0, xv(452), 522, `shaded: the minion rail's range, ${nt('l1_vlim')} (firmware)`, 't-sm halo', 'start', nf('l1_vlim'));
  gr0._box = {x: xv(450), y: 56, w: xv(620) - xv(450), h: 414};
  const rows = [['RM5', 'scp_rm5', 855, 950], ['RM4', 'scp_rm4', 765, 850], ['RM3', 'scp_rm3', 675, 750], ['RM2', 'scp_rm2', 650, 722], ['RM1', 'scp_rm1', 630, 700], ['RM0', 'scp_rm0', 585, 650]];
  ap.rm = {};
  const labs = E('g', {class: 'dimmable'}, L);   // the rows' labels sit beside the bars, clear of the rail lines (drawn over the bars)
  rows.forEach(([nm, key, vmin, vnom], i) => {
    const y = Y0 + i * RH, g = comp(L, 'rm', {i}, `Trim row ${nm}: minimum ${vmin} millivolts, nominal ${vnom}`), on = nm === 'RM0';
    S(E('rect', {class: 'shape', x: xv(vmin), y, width: xv(vnom) - xv(vmin), height: 34, rx: 5}, g), {fill: 'var(--c3)', fillOpacity: on ? 0.35 : 0.16, stroke: 'var(--c3)', strokeWidth: on ? 3 : 1.5});
    S(E('circle', {cx: xv(vmin), cy: y + 17, r: 6}, g), {fill: 'var(--c3)'});
    T(labs, xv(vmin) - 12, y + 24, nm + (on ? ' (reset)' : ''), on ? 't-smb halo' : 't-sm halo', 'end', 'scp:scp.trim-reset');
    T(labs, Math.max(xv(vnom) + 10, xv(765)), y + 24, `${nt(key)} mV`, 't-sm halo', 'start', nf(key));
    g._box = {x: xv(vmin), y, w: xv(vnom) - xv(vmin), h: 34};
    E('rect', {class: 'ring', x: xv(vmin) - 5, y: y - 5, width: xv(vnom) - xv(vmin) + 10, height: 44, rx: 8}, g);
    ap.rm[nm] = {x: xv(vmin), y: y + 17};
  });
  T(L, xv(450), 52, 'the data panel\'s trim rows: Vmin (dot) to Vnom', 't-smb', 'start', 'scp:scp.vmin-table');
  const rail = (key, v, lab, fids, dash) => {
    const g = comp(L, key, {}, lab);
    S(E('line', {x1: xv(v), y1: 56, x2: xv(v), y2: 470}, g), {stroke: 'var(--c2)', strokeWidth: 4, strokeDasharray: dash || null});
    g._box = {x: xv(v) - 8, y: 56, w: 16, h: 414};
    E('rect', {class: 'ring', x: xv(v) - 13, y: 51, width: 26, height: 424, rx: 8}, g);
    return g;
  };
  const gs = rail('railSram', 705, 'The SRAM rail, measured on the die', nf('l2_v'));
  T(gs, xv(705) + 10, 548, `SRAM rail ${nt('l2_v')} mV (measured)`, 't-smb halo', 'start', nf('l2_v'));
  T(gs, xv(705) + 10, 570, `${nt('scp_margin')} RM0's Vmin`, 't-sm halo', 'start', nf('scp_margin'));
  const gm = rail('railMin', 517, 'The minion rail, measured', nf('l1_v'));
  T(gm, xv(517) - 10, 548, `minion rail ${nt('l1_v')}`, 't-smb halo', 'end', nf('l1_v'));
  T(gm, xv(517) - 10, 570, `${fnum(V('scp_vmin') - 1000 * V('l1_v'))} mV below RM0's Vmin`, 't-sm halo', 'end', 'l1:l1.voltage scp:scp.vmin-table');
  const gn = rail('railMesh', 485, 'The mesh rail, measured', nf('l3_mesh_v'), '8 6');
  T(gn, xv(485) - 10, 606, `mesh ${nt('l3_mesh_v')}`, 't-sm halo', 'end', nf('l3_mesh_v'));
  const g7 = rail('rail750', 750, 'The power-tree figure\'s SRAM rail', nf('l2_rail750'), '3 6');
  T(g7, xv(750) + 10, 606, `${nt('l2_rail750')} in the power-tree figure`, 't-sm halo', 'start', nf('l2_rail750'));
  L.appendChild(labs);
  part(L, 'why', -150, 624, 1228, 70, 'var(--warn)', 'our reading: the L1 is latches, which are logic, not these panels', {kind: 'unknown', f: 'l1:l1.why-latch', sub: [{t: 'an argument from these macros\' listed Vmin, not a proof; the documents never say why: asked', f: 'l1:l1.why-latch l1:l1.u-why'}]});
}
function buildScpCell(L, ap, inst) {
  buildCell(L, ap, {title: 'One bit · a 6T SRAM cell (generic)',
    sub: 'the spec says SRAM; the lab lead said not SRAM; the bitcell is not documented (asked)',
    note: ['one bitline droops whatever the bit,', `yet random costs ${nt('scp_90')}`], noteF: 'scp:scp.g-read-data ' + nf('scp_90')});
}
function buildScpHop(L, ap, inst) {
  buildHop(L, ap, {title: 'One mesh hop, up close', sub: `from shire ${inst.req}'s bank to shire ${inst.remote ? inst.shire : (inst.req + 16) % 32}'s L3-slave port`, bank: inst.bank,
    lane: `PA[7:6] = ${inst.bank}`, laneF: 'l3:l3.lane', to: `shire ${inst.remote ? inst.shire : (inst.req + 16) % 32}: L3-slave port`});
}

SCENES.scp = {
  lv: 'scp', title: 'Scratchpad', short: 'Scratch', root: 'chip', inst: {}, req: 0,
  pa() { return scpPA(scpRemote() ? (this.req + 16) % 32 : SELF); }, paF: 'scp:scp.addr',
  setInst() {
    const remote = scpRemote(), pa = this.pa(), a = decS(pa), shire = remote ? a.shire : this.req;
    this.inst = Object.assign(a, {pa, remote, req: this.req, shire, panel: a.qw});
  },
  newAddr() { SCPA.set = Math.floor(Math.random() * 640); SCPA.way = Math.floor(Math.random() * 4); SCPA.sub = Math.floor(Math.random() * 4); SCPA.bank = Math.floor(Math.random() * 4); },
  head: () => `${n('scp_size')} per shire in rows 0–2,559 of the same panels; never a miss; ${n('lad_scp_lat')} from the own shire, ${n('scp_remote')} from another`,
  addrFields(pa) {
    const a = decS(pa);
    return [['shire', '[29:23]', a.shire === SELF ? '0x7F: own' : a.shire, 'scp:scp.addr', true], ['set', '[22:12]', '0x' + a.set.toString(16), 'scp:scp.addr', true], ['way', '[11:10]', a.way, 'scp:scp.addr'],
      ['sub-bank', '[9:8]', a.sub, 'scp:scp.addr', true], ['bank', '[7:6]', a.bank, 'scp:scp.addr', true], ['panel row', 'PA[21:10]', fnum(a.row), 'scp:scp.addr-row', true]];
  },
  scales: {
    chip: {name: 'Chip', short: 'Chip', parent: null, def: 'shire', build: buildScpChip},
    shire: {name: 'Shire', short: 'Shire', parent: 'chip', def: 'bank', tw: 60, target: (ap, inst) => ap.B['s' + inst.shire], build: buildScpShire, label: inst => `shire ${inst.shire}`},
    bank: {name: 'Bank and sub-bank', short: 'Bank', parent: 'shire', def: 'panel', tw: 238, target: (ap, inst) => ap.bank[inst.bank].box, build: buildScpBank, label: inst => `bank ${inst.bank} of shire ${inst.shire}`},
    panel: {name: 'Data panel', short: 'Panel', parent: 'bank', def: 'cell', tw: 44, target: ap => ap.panelBox, build: buildScpPanel, label: inst => `data panel ${inst.panel} of sub-bank ${inst.sub}`},
    cell: {name: 'Cell', short: 'Cell', parent: 'panel', def: null, tw: 90, target: ap => { const k = ap.rowK, y = ap.Y0 + k * ap.RH; return {x: ap.AX + ap.CW, y: y + 2, w: ap.CW - 12, h: ap.RH - 16}; }, build: buildScpCell},
    vmin: {name: 'Vmin inset', short: 'Vmin', parent: 'panel', def: null, tw: 198, target: ap => ap.trimBox, build: buildVmin},
    hop: {name: 'Mesh hop', short: 'Hop', parent: 'chip', def: 'rep', tw: 30, target: ap => ap.hopBox, build: buildScpHop},
    rep: {name: 'Repeater and level shifter', short: 'Transistors', parent: 'hop', def: null, tw: 40, target: ap => ap.repBox, build: buildL3Wire},
  },
};
const SP = SCENES.scp.parts = {
  overview: () => ({kick: 'Level 4 · key 4', title: 'The scratchpad', badge: [['documented', 'structure, timing, energy'], ['generic', 'the cell'], ['unknown', 'the bitcell, the bandwidth cap']],
    what: `Each shire's scratchpad is ${n('scp_size')} of its shire cache run as software-managed memory, ${n('scp_80')} over the chip: ${src('rows 0–2,559 of the same data panels', 'scp:scp.m0-rows')} that hold the L2 and the L3, with no tags, so never a miss and never a victim. From its own shire a load takes ${n('lad_scp_lat')}, exactly an L2 hit, because the tag stages still elapse; from another shire ${n('scp_remote')}. Reading it costs ${n('lad_e_scp')}–${n('lad_e_scp1')} pJ/B (zeros–random), ${n('scp_69')} of it on the SRAM rail. Its destination is the L1 scratchpad, which is latch RAM, not SRAM.`,
    kpis: [K('scp_size', 'per shire (mode M0)'), K('lad_scp_lat', 'own shire, three cards'), K('scp_bw', 'chip-wide'), kpi(`${n('lad_e_scp')}–${n('lad_e_scp1')}`, 'pJ/B, zeros–random')],
    extra: ladderHtml('scp')}),
  fmt: () => ({kick: 'Scratchpad · address', title: 'The scratchpad\'s address', badge: [['documented', 'spec']], facts: 'fmt',
    what: 'Bits [39:31] = 9\'h1 mark the scratchpad region; bit [30] picks the format (0 here: the PRM\'s format 0, the one a minion issues); [29:23] name the shire (0x7F: the requester\'s own), [22:12] the set, [11:10] the way, [9:8] the sub-bank, [7:6] the bank. So a 64-byte line sits at bank PA[7:6], sub-bank PA[9:8], panel row PA[21:10] of that sub-bank\'s four panels, 16 bytes a panel; consecutive lines rotate over the banks and then the sub-banks, so one 1 KB TensorLoad touches each of the 16 sub-banks once.'}),
  own: () => ({kick: 'Scratchpad · latency', title: 'From the own shire', badge: [['documented', 'measured, three cards']], facts: 'own',
    what: `${n('lad_scp_lat')} load to use for a load that misses the L1 (${n('scp_ns')}), the same as an L2 hit; ${n('scp_rb36')} from the read buffer. The spec accounts for 21 shire clocks inside the shire cache; the other ${n('scp_split26')} are the minion, the L1 miss and the neighbourhood's paths. One minion's TensorLoad takes ${n('scp_tl')}, ${n('scp_tl10')} per extra line with 4 in flight. All 1,024 minions stream ${n('scp_bw')}.`}),
  remote: () => ({kick: 'Scratchpad · latency', title: 'From another shire', badge: [['documented', 'measured'], ['unknown', 'where the 53 cycles go']], facts: 'remote',
    what: `${n('scp_remote')} at 600 MHz (all 124 points within a cycle, on three cards); fitted over three clocks, ${n('scp_rsplit')}. Leaving the shire costs ${n('scp_leave')} before the first hop; where they go is asked. Every shire reading the scratchpad 16 IDs away moves ${n('scp_bw_rem')}; each byte costs ${n('scp_rem0')} on zeros, ${n('scp_rem1')} pJ/B on random data, plus ${n('scp_hop_e')} per hop.`}),
  size: () => ({kick: 'Scratchpad · storage', title: 'The same macros, no tags', badge: [['documented', 'spec, derived']], facts: 'size',
    what: `In mode M0 each sub-bank's sets 0–639 are scratchpad: the lowest ${n('scp_rows')} rows of each of its four data panels, ${n('scp_panels64')} per shire. A scratchpad read never reads the tag or tag-state RAMs (squashed), takes the way from PA[11:10] and writes no LRU; nothing is evicted and nothing is filled from below.`}),
  fmt1: () => ({kick: 'Scratchpad · address', title: 'Format 1', badge: [['documented', 'spec']], facts: 'fmt', what: 'Address bit 30 = 1 (minions only) selects format 1, which puts the shire ID in bits [29:28] and [10:6]: consecutive 64-byte lines land in different shires\' scratchpads.'}),
  relay: () => ({kick: 'Scratchpad · energy', title: 'Handing work to the next shire', badge: [['documented', 'measured']], facts: 'relay',
    what: `A pipeline that hands each stage's output to the next shire's scratchpad instead of DRAM: energy per byte moved ${n('scp_relay')} (DRAM / next shire / own), and ${n('scp_relay_bw')} GB/s through DRAM. The next-shire stage reads the previous shire's scratchpad with 32-byte loads over the mesh and writes its own with TensorStores.`}),
  shire: ctx => {
    const I = IS(), c = SHC[ctx.id];
    return {kick: 'Scratchpad · chip', title: `Shire ${ctx.id}`, badge: [['documented', 'measured map']], facts: 'remote',
      what: `Its ${n('scp_size')} scratchpad is reached from shire ${I.req} in ${hopsC(SHC[I.req], c)} hops: ${ctx.id === I.req ? n('lad_scp_lat') : cn(fitS(hopsC(SHC[I.req], c)), 'scp:scp.lat-remote', 1, 'cycles')} by the fits.`,
      act: `<button type="button" class="st-btn" data-act="req" data-id="${ctx.id}">Requester here</button>` + (ctx.id === I.shire ? ` <button type="button" class="st-btn" data-act="zoom" data-to="shire">Zoom into shire ${ctx.id}</button>` : '')};
  },
  memshire: () => ({kick: 'Scratchpad · chip', title: 'A memory shire', badge: [['documented', 'measured']], facts: 'relay', what: 'The scratchpad never reaches memory by itself: it has no misses. TensorLoadL2Scp can fill it from the L3 or DRAM, and a relay through DRAM costs 13 times one through the next shire\'s scratchpad.'}),
  grey: () => L3P.grey({cell: {name: 'no compute shire'}}),
  link: () => Object.assign(L3P.link(), {kick: 'Scratchpad · chip', what: `Each hop adds ${n('scp_hop12')} to the round trip and ${n('scp_hop_e')} per byte. Zoom in for a router, a link and the crossings.`}),
  // the shire
  nbr: ctx => ({kick: 'Scratchpad · shire', title: `Neighbourhood ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']], facts: 'nbrpath',
    what: 'A minion\'s 256-bit request enters the neighbourhood\'s arbiter and a 3-deep bank FIFO, crosses from the minion region into the high-voltage region on the shire clock and is up-converted onto the neighbourhood\'s one 512-bit link; responses come back through its 4-entry Fill FIFO, one per cycle, one every other cycle to one agent, then two 256-bit beats into the minion.'}),
  l1scp: () => ({kick: 'Scratchpad · shire', title: 'Where a TensorLoad lands', badge: [['documented', 'spec']], facts: 'tl',
    what: `TensorLoad (hart 0, CSR 0x83F) reads up to ${n('scp_tlrows')} and writes them into consecutive lines of the L1 scratchpad, sets 0–11 of the minion's L1 data cache: latch RAM, 4 LRAM blocks of 128 × 64 bits, not SRAM. The L1 tab (key 1) draws it down to the latch.`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="l1">The L1 (key 1) →</button>`}),
  fifo: () => ({kick: 'Scratchpad · shire', title: 'Bank FIFOs: the crossing', badge: [['documented', 'the crossing exists'], ['generic', 'the circuit']], facts: 'nbrpath', what: 'The neighbourhood\'s per-bank FIFOs carry each request from the minions\' low-voltage region into the Shire Channel; level shifters and voltage-crossing FIFOs separate the two.'}),
  reqxbar: () => ({kick: 'Scratchpad · shire', title: 'Request crossbar', badge: [['documented', 'spec']], facts: 'xbar', what: 'A full crossbar joins the 4 neighbourhoods and the RBOX to the 4 banks and the UC block; each bank has a catch FIFO per neighbourhood and a round-robin arbiter.'}),
  rspxbar: () => ({kick: 'Scratchpad · shire', title: 'Response crossbar', badge: [['documented', 'spec']], facts: 'xbar', what: 'Lines go back through an identical crossbar. For a cooperative TensorLoad the bank\'s response mux broadcasts the line to every cooperating neighbourhood: identical requests from minions across the neighbourhoods travel as one ReadCoop.'}),
  banks: ctx => ({kick: 'Scratchpad · shire', title: `Bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec']], facts: 'banks',
    what: 'One of four, picked by PA[7:6]; each holds a quarter of the scratchpad, the L2 and the L3, takes at most one request and returns at most one 512-bit line a cycle.',
    act: ctx.i === IS().bank ? `<button type="button" class="st-btn" data-act="zoom" data-to="bank">Zoom into bank ${ctx.i}</button>` : ''}),
  uc: () => ({kick: 'Scratchpad · shire', title: 'UC block', badge: [['documented', 'spec']], facts: 'atomic', what: 'Atomics to the scratchpad are not accepted from a neighbourhood directly: they go to the UC block, then over the mesh to the home shire\'s L3 slave. Through the self ID 0x7F they are a bus error.'}),
  partition: () => ({kick: 'Scratchpad · shire', title: 'One sub-bank\'s rows', badge: [['documented', 'spec, derived']], facts: 'size', what: `Mode M0: sets 0x000–0x27F scratchpad (640), 0x280–0x2FF L2, 0x300–0x3FF L3. The scratchpad is the lowest ${n('scp_rows')} rows of each panel.`}),
  meshstop: () => ({kick: 'Scratchpad · shire', title: 'The mesh stop', badge: [['documented', 'spec and measured']], facts: 'starve',
    what: `A request for this shire's scratchpad from another shire arrives on an L3-slave port. Such requests win each sub-bank's arbitration over the shire's own: ${n('scp_starve')} of one other shire hammering one word stop the host shire's own scratchpad reads.`}),
  bneck: () => ({kick: 'Scratchpad · bandwidth', title: 'What caps a shire at 128 B per cycle?', badge: [['documented', 'measured'], ['unknown', 'the block, asked']], facts: 'bneck',
    what: `Own-scratchpad streams reach exactly ${n('scp_4b')}, ${n('scp_128')}: half the four banks' 256 B. One neighbourhood alone gets ${n('scp_50')}; returning to one bank every time drops the stream to ${n('scp_614')}. The candidates: a sub-bank's busy time, the response crossbar, the neighbourhood's Fill FIFO and 512-bit link, or the minions' 256-bit response ports. A stride sweep and the design team would settle it.`}),
  rail: () => ({kick: 'Scratchpad · power', title: 'The Shire Channel', badge: [['documented', 'measured'], ['unknown', 'what else is on the rail']], facts: 'rail',
    what: `The panels sit on the SRAM rail, ${n('l2_v')} mV on the die, ${n('scp_margin')} the data panels' RM0 Vmin. Its regulator is an LTM4680 rated 60 A. Whether it also feeds the shire cache's logic is asked. Streaming random data from the own scratchpad puts ${n('scp_69')} of the power on it.`}),
  lvband: () => ({kick: 'Scratchpad · shire', title: 'The minions\' region', badge: [['documented', 'spec and measured']], facts: 'nbrpath', what: `The minions and most of each neighbourhood run at ${n('l1_v')} on the minion rail; a scratchpad request crosses into the Shire Channel at the bank FIFOs, and the line crosses back.`}),
  // the bank
  reqq: () => ({kick: 'Scratchpad · bank', title: 'Request queue', badge: [['documented', 'spec']], facts: 'reqq', what: `The bank's 64-entry request queue (up to ${n('l3_reqq21')} for L3-slave requests), with a data-queue line per entry, the 8-entry read buffer and the 32-entry coalescing buffer. Per sub-bank, remote (L3-slave) requests win.`}),
  arb: () => SP.reqq(), dataq: () => SP.reqq(),
  rbuf: () => ({kick: 'Scratchpad · bank', title: 'Read buffer', badge: [['documented', 'spec and measured']], facts: 'rbuf', what: `Scratchpad reads install into the bank's 8-entry read buffer, remote ones included; a repeat read of a clean line is served without the panels: ${n('scp_rb36')} against ${n('lad_scp_lat')}.`}),
  atomic: () => ({kick: 'Scratchpad · bank', title: 'The atomic block', badge: [['documented', 'measured']], facts: 'atomic', what: `A global atomic on a scratchpad word is done by its home bank after it arrives on the L3-slave port: read, ALU, write, the sub-bank busy throughout; ${n('scp_atomic')} each. An uncontended remote atomic takes ${n('l3_atom216')}.`}),
  subbanks: ctx => ({kick: 'Scratchpad · bank', title: `Sub-bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'spec, derived']], facts: 'sub',
    what: 'PA[9:8]. For a scratchpad line only its four data panels are clocked; the tag and tag-state panels stay idle (hatched). The shaded top of each panel is the scratchpad\'s rows 0–2,559.'}),
  data: () => ({kick: 'Scratchpad · bank', title: `Data panel ${IS().panel}`, badge: [['documented', 'spec'], ['unknown', 'the geometry, the bitcell']], facts: 'panel', what: `A full 64-byte read raises one row in each of the four panels of one sub-bank and senses ${n('scp_576')}; the other 15 sub-banks stay idle.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="panel">Zoom into the panel</button>`}),
  pipe: () => ({kick: 'Scratchpad · bank', title: 'No tags, and as fast as an L2 hit', badge: [['documented', 'spec, measured'], ['derived', 'why']], facts: 'pipe',
    what: `The pipeline does not stall and its stages are fixed: for a scratchpad address the tag and tag-state reads are squashed, but tap … tc still elapse. So a scratchpad load takes ${n('lad_scp_lat')}, the same as an L2 hit, and skipping the tags saves no time; on each of three cards the L2-minus-scratchpad energy difference included zero.`}),
  rules: () => ({kick: 'Scratchpad · bank', title: 'What a scratchpad access skips', badge: [['documented', 'spec, derived']], facts: 'rules',
    what: `No misses, no victims, no fills from below; a write of ${n('scp_16B')} or more goes straight to the panels with per-quadword enables, with no read-modify-write. The zero-line shortcut lives in the tag state, which a scratchpad access never reads: an all-zero line is still read from the panels, and a write always writes them.`}),
  // the panel and the Vmin inset
  trim: () => ({kick: 'Scratchpad · panel', title: 'The trims, and Vmin', badge: [['documented', 'spec, reset values'], ['unknown', 'the live settings']], facts: 'trim',
    what: `The data panel's trim table runs from RM0, Vmin ${n('scp_vmin')}, to RM5; the reset trim is RM0's "nominal 650 mV" row and the open firmware never writes it. The rail measures ${n('l2_v')} mV on the die. Enter zooms into the Vmin inset: the table against the chip's rails.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="vmin">The Vmin inset</button>`}),
  rm: ctx => ({kick: 'Scratchpad · Vmin', title: 'A trim row', badge: [['documented', 'spec']], facts: 'trim', what: 'Each row sets read margin, read assist and write assist for a voltage range: the minimum voltage the macro is specified for (the dot) and its nominal voltage. The reset value is RM0.'}),
  axis: () => SP.rm({}),
  railSram: () => SP.rail(), rail750: () => SP.rail(),
  railMin: () => ({kick: 'Scratchpad · Vmin', title: 'The minion rail', badge: [['documented', 'measured, firmware limits']], facts: 'why', what: `The L1's latches run at ${n('l1_v')} at 600 MHz (${n('l1_v800')}); the firmware lets the rail range over ${n('l1_vlim')}. The lowest Vmin in the data panels' table is ${n('scp_vmin')} (${n('l2_vmin_st')} for the tag-state RAM). The neighbourhood document says that "the memory cells used to implement the ICache data RAMs need to be placed in an HV region".`}),
  railRange: () => SP.railMin(),
  railMesh: () => ({kick: 'Scratchpad · Vmin', title: 'The mesh rail', badge: [['documented', 'measured']], facts: 'rail', what: `The mesh runs lower still, ${n('l3_mesh_v')}: no memory panel sits on it.`}),
  why: () => ({kick: 'Scratchpad · Vmin', title: 'Why the L1 is latches (our reading)', badge: [['derived', 'from the documents'], ['unknown', 'asked']], facts: 'why',
    what: `The neighbourhood document says only that the ICache's data-RAM cells must sit in the high-voltage region; applying that to the shire cache's panels is our inference. A voltage argument is consistent with it, though it concerns these macros' listed Vmin only and proves nothing: the data panel's lowest Vmin is ${n('scp_vmin')} at RM0 (${n('l2_vmin_st')} for the tag-state RAM), while the firmware keeps the minion rail within ${n('l1_vlim')} and it measures ${n('l1_v')} at 600 MHz; only near the top of its range (${n('l1_v800')}) would it clear that Vmin. The SRAM rail, ${n('l2_v')} mV, sits ${n('scp_margin')} it. Latches are ordinary logic and work wherever logic does. No document gives this reason: it is derived here, and it is the first ask.`,
    act: `<button type="button" class="st-btn" data-act="level" data-lv="l1">The L1's latch (key 1) →</button>`}),
  cell: () => ({kick: 'Scratchpad · cell', title: 'The cell, and the zeros puzzle', badge: [['generic', 'a textbook 6T cell'], ['unknown', 'the ET bitcell']], facts: 'cell',
    what: `Drawn as a 6T cell: the spec calls the panels SRAM; the lab lead said the chip is not using SRAM; no source gives the cell. In a differential read exactly one bitline of each pair discharges whatever the cell holds, so the array's read energy is to first order independent of the data. Yet on the SRAM rail random data costs ${n('scp_90')}, and the zero-line shortcut does not apply here: the difference must sit after the sense amplifiers (outputs, buses, ECC), or the macro reads through a precharged single-ended line. Writing costs ${n('scp_21x')} a read (random data, zeros).`}),
};
['periph', 'pre', 'mux', 'sa', 'olat', 'wl', 'wd', 'half', 'leak', 'icg', 'geom', 'band', 'array', 'panel'].forEach(k => {
  SP[k] = kickAs(L2P[k], /^(periph|icg|geom|band|array|panel)$/.test(k) ? 'Scratchpad · panel' : 'Scratchpad · cell');
});
SP.band = () => ({kick: 'Scratchpad · panel', title: 'The panel\'s rows', badge: [['documented', 'spec and RTL']], facts: 'band', what: `The scratchpad is the lowest ${n('scp_rows')} rows of each panel, the rows this level lights; the L2 is the 512 above and the L3 the top ${n('l3_rows')}.`});
['bankR', 'tol3', 'vcdown', 'slave', 'router', 'router2', 'more', 'flits', 'hopE', 'nochop', 'rep1', 'rep2', 'wireC', 'bitE', 'lsin', 'ls', 'sync'].forEach(k => { SP[k] = kickAs(L3P[k], 'Scratchpad · mesh hop'); });
SP.tol3 = () => ({kick: 'Scratchpad · mesh hop', title: 'to_l3 master', badge: [['documented', 'spec']], facts: 'lane', what: 'For a remote scratchpad request the lane is PA[7:6], the bank (for an L3 request it is the home bank PA[12:11]). The ET-Link read becomes an AXI read address, about 75–85 bits.'});

/* ---- the scratchpad's accesses ---- */
/* the right edge of neighbourhood 0's Fill FIFO box, where a request drops to its bank FIFO clear of the label */
const x0Gap = a => a.min[0][3].x + 34;
function sReq(c) {
  const a = c.ap, b = IS().bank, m = a.min[0][0], f = a.fifo[0][b], B0 = a.bank[b];
  return [m, {x: m.x - 34, y: m.y}, {x: m.x - 34, y: 140}, a.arb[0], {x: x0Gap(a), y: 140}, {x: x0Gap(a), y: 196}, {x: f.x, y: 196}, f, {x: f.x, y: a.xbarY}, {x: B0.x, y: a.xbarY}, B0];
}
function sRsp(c) {
  const a = c.ap, b = IS().bank, m = a.min[0][0], f = a.fifo[0][b], B0 = a.bank[b];
  return [B0, {x: B0.x, y: a.rxbarY}, {x: f.x - 14, y: a.rxbarY}, {x: f.x - 14, y: 186}, {x: m.x - 34, y: 186}, {x: m.x - 34, y: m.y}];   // up the neighbourhood's left edge into M0, clear of its label
}
const TR = () => SHC[(IS().req + 16) % 32];
function tagsIdle(c) {
  const s = c.ap.sub[IS().sub].box;
  callout(c.fx, s.x + 44, s.y + 160, ['✕ no tag read'], {side: 'l', fs: 19});
  ['tap', 'ta', 'ta0', 'ta1', 'te', 'tc'].forEach(k => { const b = c.ap.stg[k]; fadeIn(T(c.fx, b.x + 37, b.y - 6, '✕', 't-smb halo', 'middle')); });
}
async function sPanelsLit(tok, c, lab) {
  const s = c.ap.sub[IS().sub];
  lit(c, 'subbanks', {i: IS().sub});
  await Promise.all(s.panels.map((p, k) => sweep(tok, c, [{x: p.x + 2, y: c.ap.rowY}, {x: p.x + p.w - 2, y: c.ap.rowY}], {ms: 450, w: 5, under: true, label: k ? '' : lab, at: {x: p.x, y: c.ap.rowY}, dx: 0, dy: -10})));
}
const SA = SCENES.scp.access = {};
SA['own-load'] = {
  led: [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [src(nt('l3_ram2'), nf('l3_ram2')), src('≈ ' + nt('scp_182'), nf('scp_182'))], [null, null], [null, null], [null, null], [null, null]],
  tot: () => ({c: `${n('lad_scp_lat')}; ${n('scp_tl')}`, e: `${n('lad_e_scp')}–${n('lad_e_scp1')} pJ/B`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `A load from the own scratchpad: ${n('lad_scp_lat')} load to use, like an L2 hit; a TensorLoad of ${n('scp_tl')}; ${n('lad_e_scp')}–${n('lad_e_scp1')} pJ/B, ${n('scp_69')} of it on the SRAM rail.`,
  steps: [
    {name: 'TensorLoad', where: 'shire', say: () => `Hart 0 writes the TensorLoad CSR: its state machine expands it into up to 16 line reads and keeps 4 in flight (${n('scp_tl')})`,
      run: async (tok, c) => { lit(c, 'l1scp', {noRing: true}); lit(c, 'nbr', {i: 0}); counter(c, `${nt('scp_tl10')} per extra line`, '4 in flight, measured'); const m = c.ap.min[0][0], a = c.ap.arb[0];
        await Promise.all([0, 1, 2, 3].map(async i => { await wait(tok, i * 260); const pk = PKM(c, m, 'var(--c7)', 9); await travel(tok, c.fx, pk, [m, {x: m.x - 34, y: m.y}, {x: m.x - 34, y: 140}, a], 900, {col: 'var(--c7)'}); })); }},
    {name: 'Decode', where: 'chip', say: () => 'Bits [39:31] = 9\'h1: the scratchpad; the shire field is 0x7F, the requester\'s own; the bank is PA[7:6]',
      run: async (tok, c) => { lit(c, 'fmt', {noRing: true}); ['region', 'shire', 'bank'].forEach(k => ringAround(c.fx, c.ap.fld[k], {fo: 0.2})); litTile(c, 'shire', IS().req); sayAt(c, c.ap.fld.shire.x + 40, 90, ['region: the scratchpad', 'shire 0x7F: this one', `bank PA[7:6] = ${IS().bank}`], {side: 'd'}); await wait(tok, 900); }},
    {name: 'Neighbourhood', where: 'shire', say: () => `The 256-bit request crosses the neighbourhood's arbiter and a bank FIFO, from the minion region into the Shire Channel, onto the 512-bit link`,
      run: async (tok, c) => { lit(c, 'nbr', {i: 0}); lit(c, 'fifo', {i: 0}); const P = sReq(c).slice(0, 8), pk = PKM(c, P[0]); await travel(tok, c.fx, pk, P, 1400); }},
    {name: 'Req xbar', where: 'shire', say: () => `The request crossbar admits it to bank ${IS().bank}, one source a bank a cycle`,
      run: async (tok, c) => { lit(c, 'reqxbar'); lit(c, 'banks', {i: IS().bank}); const P = sReq(c).slice(7), pk = PKM(c, P[0]); await travel(tok, c.fx, pk, P, 1000); }},
    {name: 'Queue', where: 'bank', say: () => 'A request-queue entry; the read buffer has no copy; the set is inside the scratchpad\'s 640; the sub-bank\'s arbitration',
      run: async (tok, c) => { lit(c, ['reqq', 'rbuf']); slotOn(c, c.ap.q[5]); c.ap.rb.forEach(r => fadeIn(T(c.fx, +r.getAttribute('x') + 20, +r.getAttribute('y') + 14, '≠', 't-smb halo', 'middle'))); await wait(tok, 500); lit(c, 'arb'); const pk = PKM(c, c.ap.rq); await travel(tok, c.fx, pk, [c.ap.rq, c.ap.arbP], 700); }},
    {name: 'Tag stages', where: 'bank', say: () => `No tags: the tag and tag-state reads are squashed, but their stages elapse, so the scratchpad takes exactly as long as an L2 hit (${n('lad_scp_lat')})`,
      run: async (tok, c) => { lit(c, 'pipe', {noRing: true}); ['tap', 'ta', 'ta0', 'ta1', 'te', 'tc'].forEach(k => ringAround(c.fx, c.ap.stg[k], {fo: 0.15, sw: 2.5})); lit(c, 'subbanks', {i: IS().sub}); tagsIdle(c); counter(c, 'the tag stages elapse', 'nothing is read'); await wait(tok, 1000); }},
    {name: 'Four panels', where: 'panel', dive: ['cell'], say: () => `The four panels of sub-bank ${IS().sub} read row PA[21:10] = ${fnum(IS().row)}: ${n('scp_576')} in ${n('l3_ram2')}; about ${n('scp_182')} on the SRAM rail`,
      run: async (tok, c) => { counter(c, `dap … da1: ${nt('l3_ram2')}`, 'the RAM delay, spec default'); await panelRead(tok, c); sayAt(c, 40, 640, [`≈ ${nt('scp_182')} on the SRAM rail`], {tl: true}); },
      deep: {cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'ECC', where: 'bank', say: () => 'Data ECC (de): SECDED over 8 × (64 + 8) bits; a single-bit error is corrected, a double reported; nothing is written back',
      run: async (tok, c) => { lit(c, 'pipe', {noRing: true}); ringAround(c.fx, c.ap.stg.de, {fo: 0.25}); counter(c, 'de'); await wait(tok, 700); }},
    {name: 'Complete', where: 'bank', say: () => 'Data complete (dc): the line is OR\'d out of the sub-bank, installed in the read buffer and sent to the response mux',
      run: async (tok, c) => { lit(c, 'rbuf'); slotOn(c, c.ap.rb[0]); const s = c.ap.sub[IS().sub], pk = PKM(c, s, 'var(--c7)'); await travel(tok, c.fx, pk, [s, {x: s.x, y: 196}, {x: 512, y: 196}, c.ap.rbC], 900, {col: 'var(--c7)'}); }},
    {name: 'Response', where: 'shire', say: () => 'Back through the response crossbar and the neighbourhood\'s Fill FIFO, then down the minion\'s 256-bit port in two beats',
      run: async (tok, c) => { lit(c, ['rspxbar', 'fifo']); lit(c, 'nbr', {i: 0}); const P = sRsp(c), pk = PKM(c, P[0], 'var(--c7)'); await travel(tok, c.fx, pk, P, 1500, {col: 'var(--c7)'}); }},
    {name: 'L1 scratchpad', where: 'shire', handoff: {lv: 'l1', k: 'tensorload', at: 2, label: 'See the L1'}, say: () => 'The line is written into the L1 scratchpad: latch RAM, not SRAM (the L1 tab draws it down to the latch)',
      run: async (tok, c) => { lit(c, 'l1scp'); counter(c, `${nt('lad_scp_lat')} load to use`, 'three cards'); const m = c.ap.min[0][0]; PKM(c, m, 'var(--c7)'); await pulse(tok, c.fx, m, 900, 'var(--c7)'); sayAt(c, m.x - 28, m.y, ['into the L1 scratchpad:', 'latch RAM (key 1)'], {side: 'd'}); }},   // to M0's left edge: the ? marks sit between the minions
  ]};
SA['own-store'] = {
  led: [[null, null], [null, null], [null, null], [src(nt('l3_ram2'), nf('l3_ram2')), src('≈ ' + nt('scp_389'), nf('scp_389'))], [null, null]],
  tot: () => ({c: 'not measured apart', e: `${n('scp_e_st')} pJ/B`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `A TensorStore into the own scratchpad: only the written quadwords' panels are clocked; ${n('scp_bw_st')} chip-wide, ${n('scp_e_st')} pJ/B, ${n('scp_21x')} a read on the SRAM rail.`,
  steps: [
    {name: 'TensorStore', where: 'shire', say: () => 'TensorStore reads rows from the vector registers and sends them as writes, a 64-byte row in two 256-bit beats, bypassing the L1 and L2',
      run: async (tok, c) => { lit(c, ['l1scp']); lit(c, 'nbr', {i: 0}); const P = sReq(c); await Promise.all([0, 1].map(async i => { await wait(tok, i * 300); const pk = PKM(c, P[0], 'var(--c2)', 9); await travel(tok, c.fx, pk, P, 1800); })); }},
    {name: 'Data queue', where: 'bank', say: () => 'A request-queue entry, and the data waits in its data-queue line',
      run: async (tok, c) => { lit(c, ['reqq', 'dataq']); slotOn(c, c.ap.q[6]); const pk = PKM(c, c.ap.rq); await travel(tok, c.fx, pk, [c.ap.rq, {x: 15, y: 196}, {x: 728, y: 196}, c.ap.dq], 1000); }},
    {name: 'Pipeline', where: 'bank', say: () => `Tag reads squashed; a write of ${n('scp_16B')} or more is a full-quadword write, no read-modify-write; any read-buffer copy is cleared`,
      run: async (tok, c) => { lit(c, 'pipe', {noRing: true}); tagsIdle(c); lit(c, ['rbuf', 'rules']); callout(c.fx, 512, 175, ['✕ copy cleared'], {side: 'd', fs: 19}); await wait(tok, 900); }},
    {name: 'Panels written', where: 'panel', dive: ['cell'], say: () => `Only the panels whose quadwords are written are clocked: a 64-byte row writes all four; about ${n('scp_389')} on the SRAM rail, ${n('scp_21x')} a read`,
      run: async (tok, c) => { counter(c, 'a write', `${nt('scp_21x')} a read, SRAM rail`); await panelRead(tok, c, {write: true}); },
      deep: {cell: cellWrite}},
    {name: 'Ack', where: 'shire', say: () => `The acknowledgement goes back; TensorWait retires the store. All minions together store ${n('scp_bw_st')}, half the read rate`,
      run: async (tok, c) => { lit(c, 'rspxbar'); const P = sRsp(c), pk = PKM(c, P[0], 'var(--c7)', 8); await travel(tok, c.fx, pk, P, 1300, {col: 'var(--c7)'}); }},
  ]};
SA['remote-load'] = {
  led: () => { const h = hopsC(SHC[IS().req], SHC[IS().shire]); return [[null, null], [null, null], [cn(12 * h, 'scp:scp.lat-remote', 0) + ' both ways', src(nt('scp_hop_e') + ' a hop', nf('scp_hop_e'))], [null, null], [src(nt('l3_ram2'), nf('l3_ram2')), null], [null, null]]; },
  tot: () => ({c: `${n('scp_remote')}: ${cn(fitS(hopsC(SHC[IS().req], SHC[IS().shire])), 'scp:scp.lat-remote', 1)} here`, e: `${n('scp_rem0')} / ${n('scp_rem1')} pJ/B`}), ask: {c: 'ask-cache-latency', e: 'ask-memory-macros'},
  cap: () => `Another shire's scratchpad: ${n('scp_remote')}; from shire ${IS().req} to shire ${IS().shire}, ${hopsC(SHC[IS().req], SHC[IS().shire])} hops.`,
  steps: [
    {name: 'Shire field', where: 'chip', say: () => `The shire field names shire ${IS().shire}, not this one: the bank's request queue sends a Mesh_Read instead of using its pipeline`,
      run: async (tok, c) => { lit(c, 'fmt', {noRing: true}); ringAround(c.fx, c.ap.fld.shire, {fo: 0.25}); litTile(c, 'shire', IS().req); const p = c.ap.P[ckey(SHC[IS().req])]; PKM(c, p); sayAt(c, p.x, p.y, [`shire ${IS().shire}, not this one:`, 'a Mesh_Read'], {side: 'r'}); await pulse(tok, c.fx, p, 900); }},
    {name: 'Into the mesh', where: 'hop', dive: ['rep'], say: () => `The to_l3 master takes lane PA[7:6] = ${IS().bank}; ET-Link becomes AXI, through a voltage and clock crossing into the mesh`,
      run: async (tok, c) => { lit(c, ['bankR', 'tol3', 'vcdown'], {noRing: true}); const P = c.ap.hopP, pk = packet(c.fx, 'var(--c2)', 11); at(pk, P[0]); await travel(tok, c.fx, pk, P.slice(0, 4), 1500); },
      deep: {rep: lsLift}},
    {name: 'Across the mesh', where: 'chip', dive: ['rep'], say: () => `${hopsC(SHC[IS().req], SHC[IS().shire])} hops to shire ${IS().shire}: ${n('scp_hop12')} per hop round trip, ${n('scp_hop_e')}`,
      run: async (tok, c) => { const R = SHC[IS().req], Tg = SHC[IS().shire]; litTile(c, 'shire', R.id); litTile(c, 'shire', Tg.id); counter(c, `${hopsC(R, Tg)} hops × ${nt('scp_hop12')}`, 'round trip, measured'); await hopTravel(tok, c, R, Tg, {label: (k, n0) => `hop ${k} of ${n0}`}); },
      deep: {rep: (tok, c) => repToggle(tok, c, {})}},
    {name: 'Target port', where: 'shire', say: () => `At shire ${IS().shire} the request arrives on an L3-slave port and goes to bank ${IS().bank}; it wins the sub-bank over that shire's own requests`,
      run: async (tok, c) => { lit(c, ['meshstop']); lit(c, 'banks', {i: IS().bank}); const B0 = c.ap.bank[IS().bank], pk = PKM(c, c.ap.mesh); await travel(tok, c.fx, pk, [c.ap.mesh, {x: c.ap.mesh.x, y: 508}, {x: B0.x, y: 508}, B0], 1100); }},
    {name: 'Target bank', where: 'bank', dive: ['panel', 'cell'], say: () => 'The target bank runs the local pipeline: tags squashed, the four panels read (the read buffer may hit, and is filled)',
      run: async (tok, c) => { lit(c, ['reqq', 'arb']); tagsIdle(c); await sPanelsLit(tok, c, ''); lit(c, 'rbuf'); slotOn(c, c.ap.rb[1]); },
      deep: {panel: (tok, c) => panelRead(tok, c), cell: (tok, c) => cellRead(tok, c, {half: true})}},
    {name: 'Back', where: 'chip', say: () => `The line crosses back to shire ${IS().req}'s bank and on to the minion: ${cn(fitS(hopsC(SHC[IS().req], SHC[IS().shire])), 'scp:scp.lat-remote', 1)} cycles by the fit`,
      run: async (tok, c) => { const R = SHC[IS().req], Tg = SHC[IS().shire]; litTile(c, 'shire', R.id); counter(c, `${fnum(fitS(hopsC(R, Tg)), 1)} cycles`, 'the fit, three cards'); await hopTravel(tok, c, Tg, R, {col: 'var(--c7)', w: 9}); }},
  ]};
SA['remote-store'] = {
  led: [[null, null], [null, null], [null, null]], tot: () => ({c: `${n('scp_hop12')} per hop`, e: `${n('scp_relay')}`}), ask: {c: 'ask-cache-latency'},
  cap: () => `Writing another shire's scratchpad: the relay hands data to the next shire for ${n('scp_relay')} (DRAM / next / own).`,
  steps: [
    {name: 'Local bank', where: 'chip', say: () => 'A plain remote write leaves from the data queue straight to the mesh; a TensorStore write-around coalesces in the local L2 first and goes when the line is full',
      run: async (tok, c) => { litTile(c, 'shire', IS().req); const p = c.ap.P[ckey(SHC[IS().req])]; PKM(c, p, 'var(--c5)'); sayAt(c, p.x, p.y, ['from the data queue,', 'or coalesced first'], {side: 'r'}); await pulse(tok, c.fx, p, 900, 'var(--c5)'); }},
    {name: 'Across the mesh', where: 'chip', say: () => `AXI write address and data cross ${hopsC(SHC[IS().req], SHC[IS().shire])} hops into shire ${IS().shire}'s L3-slave port`,
      run: async (tok, c) => { const R = SHC[IS().req], Tg = SHC[IS().shire]; litTile(c, 'shire', Tg.id); await hopTravel(tok, c, R, Tg, {col: 'var(--c5)', w: 9}); }},
    {name: 'Target write', where: 'panel', dive: ['cell'], say: () => 'The target\'s L3 slave writes its scratchpad through its pipeline, like a local write, and acknowledges',
      run: async (tok, c) => { counter(c, 'written, then acknowledged'); await panelRead(tok, c, {write: true}); },
      deep: {cell: cellWrite}},
  ]};
SA.fill = {
  led: [[null, null], [null, null]], tot: () => ({c: 'not measured separately', e: 'not measured separately'}), ask: {c: 'ask-cache-latency'},
  cap: () => 'TensorLoadL2Scp copies up to 16 lines from memory into this shire\'s scratchpad, bypassing the L1 and L2: not measured separately.',
  steps: [
    {name: 'Mesh read', where: 'chip', say: () => 'CSR 0x85F (hart 1 may issue it): for each line the bank issues a Mesh_Read of the source, an L3 home, DRAM or a remote scratchpad',
      run: async (tok, c) => { const R = SHC[IS().req], S0 = TR(); litTile(c, 'shire', R.id); litTile(c, 'shire', S0.id); await hopTravel(tok, c, R, S0, {r: 9}); await hopTravel(tok, c, S0, R, {col: 'var(--c7)', w: 9}); }},
    {name: 'SCP_Fill', where: 'panel', dive: ['cell'], say: () => 'When the line returns, an SCP_Fill writes it into the local scratchpad row: no victim, no tag',
      run: async (tok, c) => { counter(c, 'SCP_Fill', 'no victim, no tag'); await panelRead(tok, c, {write: true}); },
      deep: {cell: cellWrite}},
  ]};
SA.atomic = {
  led: [[null, null], [src(nt('scp_atomic'), nf('scp_atomic')), null]], tot: () => ({c: `${n('scp_atomic')} at the bank`, e: 'not measured apart'}),
  cap: () => `A global atomic on a scratchpad word: through the UC block and the mesh to the word's shire, where its bank does it in ${n('scp_atomic')}.`,
  steps: [
    {name: 'Via the UC', where: 'chip', say: () => 'Atomics to the scratchpad go through the UC block and the mesh to the shire\'s L3 slave; through the self ID 0x7F they are a bus error',
      run: async (tok, c) => { const R = SHC[IS().req], Tg = SHC[IS().shire]; litTile(c, 'shire', R.id); litTile(c, 'shire', Tg.id); await hopTravel(tok, c, R, Tg, {col: 'var(--c5)'}); }},
    {name: 'Atomic block', where: 'bank', say: () => `The bank reads the word's panels, its atomic block applies the operation, and it writes them back: ${n('scp_atomic')}; ${n('scp_starve')} hammering one word stop the host's own reads`,
      run: async (tok, c) => {
        lit(c, ['atomic', 'arb']); lit(c, 'subbanks', {i: IS().sub}); counter(c, nt('scp_atomic'), 'per atomic, measured');
        const s = c.ap.sub[IS().sub], pk = PKM(c, c.ap.atom, 'var(--c5)');
        for (let k = 0; k < 2; k++) { await travel(tok, c.fx, pk, [c.ap.atom, {x: 961, y: 196}, {x: s.x, y: 196}, s], 600, {col: 'var(--c5)'}); await travel(tok, c.fx, pk, [s, {x: s.x, y: 196}, {x: 961, y: 196}, c.ap.atom], 600, {col: 'var(--c5)'}); }
      }},
  ]};
SA.refresh = {
  led: [[null, null], [null, null], [null, null]], tot: () => ({c: 'none', e: `leakage, at most ${n('leak_mb')}`}),
  cap: () => 'Miss? Refresh? Neither: every in-range address is a hit, nothing is evicted, and static cells need no refresh.',
  steps: [
    {name: 'No misses', where: 'bank', say: () => 'No misses and no victims: every address inside the 640 sets is a hit; one beyond them returns an error, and nothing is ever evicted',
      run: async (tok, c) => { lit(c, 'rules'); counter(c, 'never a miss'); await wait(tok, 1000); }},
    {name: 'No refresh', where: 'cell', say: () => `No refresh, if the cells are static (SRAM-type) storage (textbook); the standing cost is leakage, at most ${n('leak_mb')} at 80 °C`,
      run: async (tok, c) => { counter(c, 'no refresh', 'static storage (if SRAM)'); cellLeak(c, 'scp:scp.leak'); await wait(tok, 1200); }},
    {name: 'No scrub', where: 'bank', say: () => 'No ECC scrubbing on this chip: stage de corrects a single-bit error on the way out, never in the array (a reserved bit for future chips)',
      run: async (tok, c) => { lit(c, 'pipe', {noRing: true}); ringAround(c.fx, c.ap.stg.de, {fo: 0.25}); counter(c, 'no scrub'); await wait(tok, 1000); }},
  ]};
SCENES.scp.accOrder = [['own-load', 'Own load', 'Load'], ['own-store', 'Own store', 'Store'], ['remote-load', 'Remote load', 'Remote'], ['remote-store', 'Remote store', 'R-store'], ['fill', 'Fill', 'Fill'], ['atomic', 'Atomic', 'Atomic'], ['refresh', 'Miss? Refresh?', 'Refresh?']];
SCENES.scp.tour = [
  {name: 'The address', path: ['chip'], panel: 'fmt', hi: ['fmt', 'own', 'remote'],
    cap: () => `The address names the shire: the own shire in ${n('lad_scp_lat')}, another in ${n('scp_remote')}`,
    sub: () => `${n('scp_80')} over the chip, ${n('scp_size')} in each shire, in the same macros as the L2 and the L3.`},
  {access: 'own-load'},
  {name: 'No tags', path: ['chip', 'shire', 'bank'], panel: 'pipe', hi: ['pipe', 'subbanks'],
    cap: () => 'No tags, no misses, no victims: yet exactly as fast as an L2 hit, because the tag stages still elapse',
    sub: () => 'The tag and tag-state reads are squashed (hatched); only the four data panels of one sub-bank are clocked.'},
  {name: 'Vmin', path: ['chip', 'shire', 'bank', 'panel', 'vmin'], panel: 'why', hi: ['why', 'railMin', 'railSram', 'rm'],
    cap: () => `The panels' lowest Vmin is ${n('scp_vmin')}; the minion rail runs at ${n('l1_v')} within ${n('l1_vlim')}: our reading of why the L1 is latches`,
    sub: () => 'An argument from these macros\' listed Vmin, not a proof; the documents never say why: it is the first ask.'},
  {name: 'The cell', path: ['chip', 'shire', 'bank', 'panel', 'cell'], panel: 'cell', hi: ['cell', 'sa'], dive: true, play: (tok, c) => cellRead(tok, c, {half: true}),
    cap: () => `A differential read discharges one bitline whatever the bit; yet random data costs ${n('scp_90')} on the SRAM rail`,
    sub: () => 'The zero-line shortcut does not apply to the scratchpad, so the difference must sit after the sense amplifiers, or the cell is not what is drawn.'},
  {access: 'remote-load'},
  {name: 'The bandwidth question', path: ['chip', 'shire'], panel: 'bneck', hi: ['bneck', 'banks', 'rspxbar'],
    cap: () => `Every shire streams exactly ${n('scp_128')}, half its banks' 256 B: which block caps it is asked`,
    sub: () => 'The four ? mark the candidates; a stride sweep and the design team would settle it. The asks are under the diagram.'},
];

/* ================= DRAM (key 5, #dram): LPDDR4X behind eight memory shires ================= */
/* The map (dram.addr.*): memory shire PA[8:6], channel (controller) PA[9], then PA[9:6] stripped; inside a channel
   bank PA[12:10], row PA[34:18], column PA[17:13] and PA[5:1] (a 2 KB page of 1,024 16-bit columns); a 64-byte line is
   two BL16 bursts from one row, PA[5] picking the half. Measured by one-bit flips on three cards. */
function dec5(pa) {
  return {ms: bits(pa, 8, 6), ch: bits(pa, 9, 9), bank: bits(pa, 12, 10), row: bits(pa, 34, 18), colHi: bits(pa, 17, 13), half: bits(pa, 5, 5), home: bits(pa, 10, 6)};
}
const I5 = () => SCENES.dram.inst;
const load5 = (h1, h2) => V('dr_c110') + V('l3_hopcyc') * h1 + V('dr_model') + V('l3_hopcyc') * h2;   // dram.lat.model: 110 + 12 h1 + 91 + 12 h2 (fitted on aifoundry2)

function buildDramChip(L, ap, inst) {
  const R = SHC[inst.req], H = SHC[inst.home], M = MSC[inst.ms], h1 = hopsC(R, H), h2 = hopsC(H, M);
  frame(L, {title: `Card and chip · ${nt('dr_gb')} of LPDDR4X`, f: nf('dr_gb'), sub: `8 memory shires drive ${nt('dr_ch')} of 16 bits at ${nt('dr_mts')}`, subf: 'dram:dram.topo.memshires ' + nf('dr_mts'),
    tags: [['unknown', '? package pairing · asked'], ['documented', 'measured, spec']]});
  chipMap(L, ap, {C: 62, X0: -150, Y0: 86, pkg: 56, tile: c => c.type === 'cshire'
    ? {marks: [c.id === inst.home ? 'H' : null, c.id === inst.req ? 'R' : null].filter(Boolean), hi: c.id === inst.home || c.id === inst.req, fo: 0.07}
    : c.type === 'memshire' ? {marks: c.id === inst.ms ? ['M'] : [], hi: c.id === inst.ms, child: c.id === inst.ms ? 'ms' : null, cur: c.id === inst.ms} : {fo: 0.03}});
  const P = routeP(ap, H, M);
  if (P.length > 1) routeLine(L, ap, P);
  T(L, -150, 672, `the map measured; memory shires by a latency fit · H → M: ${h2} hops`, 't-sm', 'start', MAPF);
  const X = 262, W = 816;
  const gm = part(L, 'model', X, 14, W, 132, COL.logic, 'a whole DRAM load', {fo: 0.06, f: 'dram:dram.lat.model', sub: [{t: nt('dr_model'), f: nf('dr_model')}]});
  T(gm, X + 12, 102, `R = shire ${inst.req} → home ${inst.home} (${h1} hops) → memory shire ${inst.ms} (${h2} hops):`, 't-sm', 'start', 'dram:dram.lat.model l3:l3.homes dram:dram.addr.memshire');
  T(gm, X + 12, 134, `= ${fnum(load5(h1, h2))} cycles by the fit`, 't-mid', 'start', 'dram:dram.lat.model');
  part(L, 'typical', X, 160, 480, 150, COL.logic, 'measured', {fo: 0.06, sub: [{t: `a typical load: ${nt('lad_dram')}`, f: nf('lad_dram')}, {t: `a pointer chase: ${nt('dr_chase')}`, f: nf('dr_chase')}, {t: `the DRAM's own: ${nt('dr_share')}`, f: nf('dr_share')}, {t: `home miss + memory shire: ${nt('dr_ms63s')}`, f: nf('dr_ms63s') + ' dram:dram.lat.l3-miss'}]});
  part(L, 'rate', X + 496, 160, W - 496, 150, COL.net, 'the channels', {fo: 0.06, sub: [{t: `${nt('dr_mts')}, not 4,266`, f: nf('dr_mts')}, {t: `peak ${nt('dr_peak')}`, f: nf('dr_peak')}, {t: `measured ${nt('dr_bw')}`, f: nf('dr_bw')}, {t: `${nt('dr_ch')}, 2 GB each`, f: nf('dr_ch') + ' dram:dram.org.capacity'}]});
  part(L, 'energy', X, 324, W, 120, COL.aux, 'energy', {fo: 0.06, sub: [{t: `${nt('lad_e_dram')} per byte above idle, ${nt('dr_e_line')} a line`, f: nf('lad_e_dram') + ' ' + nf('dr_e_line')}, {t: `about ${nt('dr_unmet')} of it on no metered rail`, f: nf('dr_unmet')}, {t: `${nt('dr_vs')} the own scratchpad, random data`, f: nf('dr_vs')}]});
  part(L, 'pll', X, 458, 400, 80, COL.logic, 'two memory PLLs', {fo: 0.04, sub: [{t: 'in memory shires 0 and 4 only', f: 'dram:dram.topo.pll'}]});
  part(L, 'addrmap', X + 416, 458, W - 416, 80, COL.logic, 'which memory shire', {fo: 0.04, sub: [{t: 'PA[8:6]: lines rotate over all 8', f: 'dram:dram.addr.memshire'}]});
  railBand(L, X, 552, W, 60, 'pat-ddr', 'The memory shires\' rail', 'vddr');
  T(L, X + 14, 588, `VDD_DDR: ${nt('dr_vddr')}, ${nt('dr_vmeas')} measured (no current sensor)`, 't-sm halo', 'start', nf('dr_vddr') + ' ' + nf('dr_vmeas'));
  T(L, X, 640, `the fitted model is within ±3 cycles for ${nt('dr_fit93')}–${nt('dr_fit97')} of loads on three cards`, 't-sm', 'start', 'dram:dram.lat.model');
}

function buildMS(L, ap, inst) {
  frame(L, {title: `Memory shire ${inst.ms} · two controllers, one PHY`, sub: `a logical drawing; the up-to-63 cycles past the DRAM's timing (home and memory shire) are not split (asked)`, subf: 'dram:dram.lat.ms-internal',
    tags: [['unknown', '? the 63 cycles · asked'], ['documented', 'spec, firmware']]});
  railBand(L, -150, 12, 170, 580, 'pat-mesh', 'The mesh side');
  railBand(L, 30, 12, 1048, 580, 'pat-ddr', 'VDD_DDR', 'vddr');
  T(L, -140, 586, 'mesh', 't-sm halo', 'start', 'l3:l3.mesh-rail'); T(L, 40, 590, `VDD_DDR ${nt('dr_vmeas')}`, 't-sm halo', 'start', nf('dr_vmeas'));
  part(L, 'noc', -140, 30, 150, 200, COL.net, 'NoC port', {sub: [{t: '512-bit AXI', f: 'dram:dram.topo.noc-port'}, {t: nt('dr_noc32'), f: nf('dr_noc32')}]});
  part(L, 'xing', 36, 30, 150, 200, COL.xing, 'crossing', {sub: [{t: '400 MHz mesh', f: 'l3:l3.mesh-rail'}, {t: `→ ${nt('dr_dfi')} DFI`, f: nf('dr_dfi')}, {t: 'place: inferred', f: 'dram:dram.seq.load.03'}]});
  const gs = part(L, 'strip', 204, 30, 170, 200, COL.logic, 'address', {sub: [{t: 'PA[9] → controller', f: 'dram:dram.addr.channel'}, {t: 'PA[9:6] removed', f: 'dram:dram.addr.strip'}]});
  const mx = mux2(gs, 330, 170, {w: 26, h: 60}); ap.stripMux = mx;
  part(L, 'settings', -140, 246, 150, 314, COL.logic, 'switched off', {fo: 0.03, sub: [{t: 'power-down', f: 'dram:dram.ctl.power-down'}, {t: 'self-refresh', f: 'dram:dram.ctl.power-down'}, {t: 'auto ZQ', f: 'dram:dram.ctl.zq'}, {t: 'ECC', f: 'dram:dram.ctl.ecc'}, {t: 'on: DFI updates', f: 'dram:dram.ctl.dfi-update'}, {t: nt('dr_dfiupd'), f: nf('dr_dfiupd')}]});
  part(L, 'atomic', 36, 246, 338, 150, COL.logic, 'atomic unit', {sub: [{t: 'global atomics on memory', f: 'dram:dram.ctl.atomic-unit'}, {t: 'a small atomic cache', f: 'dram:dram.ctl.atomic-unit'}]});
  part(L, 'perfmon', 36, 410, 338, 156, COL.logic, 'perf monitor', {sub: [{t: nt('dr_perf'), f: nf('dr_perf')}, {t: 'counts mesh reads, writes', f: 'dram:dram.ctl.perfmon'}, {t: 'commands: M-mode only', f: 'dram:dram.ctl.perfmon'}]});
  ap.ctl = [];
  for (let k = 0; k < 2; k++) {
    const y = 20 + k * 290, on = k === inst.ch;
    const g = part(L, 'ctl', 392, y, 360, 276, COL.logic, `uMCTL2 controller ${k}`, {ctx: {i: k}, fo: on ? 0.1 : 0.04, sub: [`channel ${k} (PA[9] = ${k})`]});
    [[`AXI ports: P0 prio ${nt('dr_p0')}, P1 prio ${nt('dr_p1')}`, 'dram:dram.ctl.ports'], ['address map: bank, row, column', 'dram:dram.addr.addrmap'], [`CAM: ${nt('dr_cam')}, low priority`, nf('dr_cam')],
      [`in runs of ${nt('dr_runs')}`, nf('dr_runs')], ['open page; no auto-precharge', 'dram:dram.ctl.page-policy'], [`refresh timer: every ${nt('dr_trefi')}`, nf('dr_trefi')]].forEach(([t, f], i) => {
      S(E('rect', {x: 404, y: y + 76 + i * 32, width: 336, height: 28, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.06, stroke: 'var(--c1)', strokeWidth: 1, strokeOpacity: 0.6});
      T(g, 414, y + 96 + i * 32, t, 't-sm', 'start', f);
    });
    ap.ctl[k] = {x: 572, y: y + 138, box: {x: 392, y, w: 360, h: 276}, cam: {x: 744, y: y + 156}, sch: {x: 744, y: y + 188}, ref: {x: 744, y: y + 252}};   // the rows' points at their right ends, clear of their labels
  }
  part(L, 'dfi', 768, 20, 70, 566, COL.net, '', {label: 'DFI: the controller-to-PHY interface, 1:2 with the DRAM clock'});
  T(L, 803, 300, 'DFI', 't-labb', 'middle'); T(L, 803, 324, '1:2', 't-sm', 'middle', 'dram:dram.ctl.clock');
  part(L, 'phy', 854, 20, 116, 566, COL.xing, 'PHY', {child: 'phy', cur: true, sub: [{t: 'one for', f: 'dram:dram.topo.phy'}, {t: 'both', f: 'dram:dram.topo.phy'}, {t: 'channels', f: 'dram:dram.topo.phy'}]});
  ap.phyBox = {x: 854, y: 20, w: 116, h: 566};
  ap.die = [];
  for (let k = 0; k < 2; k++) {
    const y = 20 + k * 290, on = k === inst.ch;
    const g = part(L, 'die', 988, y, 90, 276, COL.store, '', {ctx: {i: k}, child: on ? 'chan' : null, cur: on, fo: on ? 0.16 : 0.06, label: `The LPDDR4X channel ${k}: a 16-bit die in a package off the chip`});
    T(g, 1033, y + 30, 'ch ' + k, 't-labb', 'middle'); T(g, 1033, y + 54, 'x16', 't-sm', 'middle', 'dram:dram.org.part');
    ['CA[5:0]', 'DQ[15:0]', 'DQS'].forEach((t, i) => { const yy = y + 110 + i * 56; S(E('line', {x1: 970, y1: yy, x2: 988, y2: yy, 'pointer-events': 'none'}, g), {stroke: 'var(--c3)', strokeWidth: 3}); T(g, 1033, yy + 6, t, 't-sm', 'middle', 'dram:dram.topo.phy'); });
    ap.die[k] = {x: 1033, y: y + 150, box: {x: 988, y, w: 90, h: 276}};
  }
  // the hatched bar: the memory shire's time, not split
  const gl = comp(L, 'lat63', {}, 'The L3 home\'s miss path and the memory shire, at most about 63 cycles of a load: not split, asked');
  S(E('rect', {x: -140, y: 606, width: 1218, height: 50, rx: 6}, gl), {fill: 'url(#pat-hatch)', stroke: 'var(--warn)', strokeWidth: 2, strokeDasharray: '8 6'});
  T(gl, -124, 638, `the L3 home's miss path and this memory shire: ${nt('dr_ms63s')} · how it splits: asked`, 't-smb halo', 'start', nf('dr_ms63') + ' dram:dram.lat.ms-internal');
  gl._box = {x: -140, y: 606, w: 1218, h: 50}; E('rect', {class: 'ring', x: -145, y: 601, width: 1228, height: 60, rx: 10}, gl);
  T(L, -140, 684, `the DRAM's own timing: ${nt('dr_share')}; the constant past an L3 hit: ${nt('l3_dram91')}`, 't-sm', 'start', nf('dr_share') + ' ' + nf('l3_dram91'));
  ap.noc = {x: -65, y: 130}; ap.xg = {x: 111, y: 130}; ap.st = {x: 289, y: 130}; ap.dfiP = {x: 803, y: 0}; ap.phyP = {x: 912, y: 0};
}

/* the channel: one rank of 8 banks; the open row; the command and data timeline drawn to scale from the programmed
   timings (dram.ctl.*), which is ET's; the die's circuits are JEDEC/textbook */
const TLX = ns => -60 + ns * 22.2;
function buildChan(L, ap, inst) {
  frame(L, {title: `Channel ${inst.ch} (PA[9]) · 8 banks`, sub: `${nt('dr_geom')}; a line is ${nt('dr_1_32')} of a page`, subf: nf('dr_geom') + ' ' + nf('dr_1_32'),
    tags: [['unknown', '? the part · asked'], ['generic', 'GENERIC die'], ['documented', 'geometry, timings']]});
  ap.bank = [];
  for (let b = 0; b < 8; b++) {
    const x = -150 + (b % 4) * 214, y = 14 + Math.floor(b / 4) * 222, w = 200, h = 208, on = b === inst.bank;
    const g = part(L, 'dbanks', x, y, w, h, COL.store, `bank ${b}`, {ctx: {i: b}, child: on ? 'dbank' : null, cur: on, fo: on ? 0.1 : 0.05, sub: [`PA[12:10] = ${b}`]});
    S(E('rect', {x: x + 8, y: y + 64, width: 14, height: 112, rx: 2, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.2, stroke: 'var(--c1)', strokeWidth: 1});
    S(E('rect', {x: x + 28, y: y + 64, width: w - 40, height: 112, rx: 2, 'pointer-events': 'none'}, g), {fill: 'var(--c3)', fillOpacity: 0.14, stroke: 'var(--c3)', strokeWidth: 1});
    for (let r = 0; r < 7; r++) wire(g, [[x + 30, y + 72 + r * 15], [x + w - 14, y + 72 + r * 15]], 'thin');
    S(E('rect', {x: x + 28, y: y + 180, width: w - 40, height: 12, rx: 2, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.2, stroke: 'var(--c1)', strokeWidth: 1});
    ap.bank[b] = {x: x + w / 2, y: y + 120, box: {x, y, w, h}, rowY: y + 64 + (inst.row / 131072) * 112, ax: x + 28, aw: w - 40, saY: y + 186};
  }
  const B0 = ap.bank[inst.bank];
  T(L, B0.box.x + B0.box.w - 8, B0.box.y + 28, `row ${fnum(inst.row)}`, 't-sm', 'end', 'dram:dram.addr.pa-map');
  part(L, 'cmd', 712, 14, 366, 122, COL.logic, 'command decoder', {kind: 'generic', sub: [{t: '6-bit CA bus, single data rate', f: 'dram:gen.commands'}, {t: 'ACT: 2 parts · READ: RD + CAS', f: 'dram:gen.commands'}]});
  part(L, 'prefetch', 712, 150, 366, 130, COL.logic, '16n prefetch, 16:1 out', {kind: 'generic', sub: [{t: `${nt('dr_256')} per READ`, f: nf('dr_256')}, {t: 'BL16 on each of 16 pins', f: 'dram:dram.ctl.burst'}]});
  part(L, 'pins', 712, 294, 366, 142, COL.net, 'DQ[15:0] · 2 DQS · 2 DMI', {sub: [{t: nt('dr_mts'), f: nf('dr_mts')}, {t: 'read and write DBI on', f: 'dram:dram.ctl.dbi'}, {t: 'data masking enabled', f: 'dram:dram.ctl.dbi'}]});
  // the timeline, to scale in ns
  const gt = comp(L, 'tl', {}, 'The command and data timeline of a load to a closed row, drawn to scale from the programmed timings');
  S(E('rect', {x: -150, y: 452, width: 1228, height: 238, rx: 8}, gt), {fill: 'var(--surface)', stroke: 'var(--border)', strokeWidth: 1.5});
  ap.tlTitle = T(gt, 1064, 478, 'a load to a closed row, to scale in ns', 't-smb', 'end', 'dram:dram.ctl.tRCD dram:dram.ctl.RL-WL dram:dram.ctl.burst');
  [0, 10, 20, 30, 40, 50].forEach(v => { S(E('line', {x1: TLX(v), y1: 492, x2: TLX(v), y2: 664}, gt), {stroke: 'var(--grid)', strokeWidth: 1}); T(gt, TLX(v), 684, String(v), 't-sm', 'middle'); });
  T(gt, -136, 530, 'CA', 't-net'); T(gt, -136, 590, 'DQ', 't-net'); T(gt, -136, 640, 'bank', 't-net');
  const box = (x0, x1, y, h, col, lab, f) => { S(E('rect', {x: TLX(x0), y, width: Math.max(4, TLX(x1) - TLX(x0)), height: h, rx: 3}, gt), {fill: col, fillOpacity: 0.3, stroke: col, strokeWidth: 1.5}); if (lab) T(gt, (TLX(x0) + TLX(x1)) / 2, y + h / 2 + 6, lab, 't-sm', 'middle', f); };
  box(0, 2.1, 512, 30, 'var(--c1)', '', 'dram:dram.seq.load.05'); T(gt, TLX(0) + 6, 506, 'ACT', 't-smb', 'start', 'dram:gen.commands');
  box(18.2, 20.3, 512, 30, 'var(--c1)', '', 'dram:dram.ctl.tRCD'); T(gt, (TLX(18.2) + TLX(20.3)) / 2, 506, 'RD', 't-smb', 'middle');
  box(22.5, 24.6, 512, 30, 'var(--c1)', '', 'dram:dram.ctl.burst'); T(gt, (TLX(22.5) + TLX(24.6)) / 2, 506, 'RD', 't-smb', 'middle');
  box(37.5, 41.8, 572, 30, 'var(--c2)', '32 B', 'dram:dram.ctl.RL-WL dram:dram.ctl.burst'); box(41.8, 46.1, 572, 30, 'var(--c2)', '32 B', 'dram:dram.ctl.burst');
  box(0, 46.1, 624, 26, 'var(--c3)', 'row open (it stays open: open page)', 'dram:dram.ctl.page-policy');
  const brk = (x0, x1, y, lab, f) => { wire(gt, [[TLX(x0), y + 6], [TLX(x0), y], [TLX(x1), y], [TLX(x1), y + 6]], 'thin'); T(gt, (TLX(x0) + TLX(x1)) / 2, y - 6, lab, 't-sm', 'middle', f); };
  brk(0, 18.2, 486, `tRCD ${nt('dr_trcd')}`, nf('dr_trcd')); brk(18.2, 37.5, 560, `RL ${nt('dr_rl')}`, nf('dr_rl'));
  T(gt, TLX(37.5) - 10, 594, `two bursts of ${nt('dr_burst')}`, 't-sm', 'end', nf('dr_burst'));
  gt._box = {x: -150, y: 452, w: 1228, h: 238};
  ap.tlY = 494; ap.tlX = TLX;
}

/* the bank, inside: mats of cells between sense-amplifier stripes and sub-wordline drivers (textbook; the vendor's
   organisation below the bank is not published) */
function buildDBank(L, ap, inst) {
  frame(L, {title: `Bank ${inst.bank} (PA[12:10]) · inside`, sub: `${nt('dr_rows')} of a 2 KB page; the mats are textbook, the vendor's not published`, subf: nf('dr_rows') + ' dram:dram.org.die-internals',
    tags: [['unknown', '? die internals · asked'], ['generic', 'GENERIC mats'], ['documented', 'rows, page']]});
  const MX = [-60, 150, 360, 570], MY = [40, 230, 420], MW = 190, MH = 150;
  part(L, 'rowdec', -150, 40, 70, 530, COL.logic, '', {kind: 'generic', label: 'The row decoder: one of 131,072 rows; generic'});
  T(L, -115, 300, 'row', 't-sm', 'middle'); T(L, -115, 320, 'dec.', 't-sm', 'middle');
  ap.mat = []; const lr = 1;
  MY.forEach((y, r) => MX.forEach((x, k) => {
    const on = r === lr, g = part(L, 'mat', x, y, MW, MH, COL.store, '', {ctx: {i: r * 4 + k}, kind: 'generic', fo: on ? 0.14 : 0.06, label: 'A mat of cells: local wordlines across, bitline pairs down; generic'});
    for (let j = 0; j < 8; j++) wire(g, [[x + 14 + j * 23, y + 8], [x + 14 + j * 23, y + MH - 8]], 'thin');
    for (let j = 0; j < 5; j++) wire(g, [[x + 6, y + 22 + j * 27], [x + MW - 6, y + 22 + j * 27]], 'thin');
    ap.mat.push({x, y, w: MW, h: MH, on});
  }));
  MX.forEach((x, k) => { const g = comp(L, 'swd', {i: k}, 'Sub-wordline drivers: raise the local wordline to the boosted voltage; generic'); S(E('rect', {x: x - 18, y: 40, width: 14, height: 530, rx: 2}, g), {fill: 'var(--c1)', fillOpacity: 0.18, stroke: 'var(--c1)', strokeWidth: 1, strokeDasharray: '2 5'}); g._box = {x: x - 18, y: 40, w: 14, h: 530}; });
  [200, 390, 580].forEach((y, i) => { const g = comp(L, 'blsa', {i}, 'A stripe of bitline sense amplifiers: each latches a bitline pair; generic'); S(E('rect', {x: -60, y: y - 8, width: 820, height: 22, rx: 3}, g), {fill: 'var(--c1)', fillOpacity: 0.2, stroke: 'var(--c1)', strokeWidth: 1.25, strokeDasharray: '2 5'}); g._box = {x: -60, y: y - 8, w: 820, h: 22}; });
  T(L, 752, 398, 'sense amplifiers', 't-sm halo', 'end', 'dram:gen.sense'); T(L, 752, 208, 'sense amplifiers', 't-sm halo', 'end', 'dram:gen.sense');
  part(L, 'coldec', -60, 612, 820, 34, COL.logic, 'column decoder: column-select lines (CSL)', {kind: 'generic', ty: 24, tcls: 't-sm'});
  part(L, 'gio', 800, 40, 278, 606, COL.net, 'I/O', {kind: 'generic', sub: [{t: 'local → global I/O', f: 'dram:gen.column'}, {t: 'secondary sense', f: 'dram:gen.column'}, {t: 'amplifiers', f: 'dram:gen.column'}, {t: `${nt('dr_256')} per READ`, f: nf('dr_256')}, {t: 'to the 16:1', f: 'dram:gen.column'}, {t: 'serialisers', f: 'dram:gen.column'}]});
  const m = ap.mat[lr * 4 + 1];
  ap.wlY = m.y + 22 + 2 * 27;
  ap.cellBox = {x: m.x + 14 + 3 * 23 - 20, y: m.y + MH - 44, w: 46, h: 40};
  const gc = part(L, 'cellpick', ap.cellBox.x, ap.cellBox.y, ap.cellBox.w, ap.cellBox.h, COL.store, '', {child: 'dcell', cur: true, fo: 0.25, kind: 'generic', label: 'One bitline pair and its sense amplifier: Enter zooms into the transistors'});
  T(L, -150, 664, `one activate raises one row across the mats: ${nt('dr_16k_n')} sense amplifiers latch the page`, 't-sm', 'start', nf('dr_16k'));
  T(L, -150, 686, 'open or folded bitlines, cells per bitline, mats: the vendor\'s choice (generic here)', 't-sm', 'start', 'dram:dram.org.die-internals');
}

/* ---- the cell and its sense amplifier: two 1T1C cells on a folded bitline pair, the three-NMOS equaliser, the
   2N + 2P latch, the column-select pair to the local I/O lines. A textbook LPDDR circuit (dram's gen.* facts). ---- */
function buildDCell(L, ap, inst) {
  frame(L, {title: 'A bitline pair · 1T1C cells, sense amp', sub: 'a textbook DRAM sense circuit (a folded pair drawn for clarity; the vendor\'s array is asked)', subf: 'dram:gen.cell dram:dram.org.die-internals',
    tags: [['unknown', '? vendor circuit · asked'], ['generic', 'GENERIC: textbook 1T1C']], col: 'var(--c3)', kind: 'generic'});
  const BL = 120, BLB = 540;
  // the wordline drivers (boosted)
  const gw = comp(L, 'wld', {}, 'Wordline drivers: the selected one pulls its wordline to a boosted voltage above the array voltage; generic');
  const d0 = invSym(gw, -70, 40, {s: 18}), d1 = invSym(gw, -70, 140, {s: 18});
  wire(gw, [[-150, 40], [d0.in.x, 40]]); wire(gw, [[-150, 140], [d1.in.x, 140]]);
  netLab(gw, -150, 28, 'row 0'); netLab(gw, -150, 128, 'row 1');
  E('line', {class: 'w bus', x1: d0.out.x, y1: 40, x2: 640, y2: 40}, gw); E('line', {class: 'w bus', x1: d1.out.x, y1: 140, x2: 640, y2: 140}, gw);
  netLab(gw, 644, 46, 'WL0'); netLab(gw, 644, 146, 'WL1');
  gw._box = {x: -150, y: 16, w: 830, h: 150};
  ap.wl0 = [{x: d0.out.x, y: 40}, {x: 640, y: 40}];
  // the bitlines
  const bls = E('g', {}, L);
  wire(bls, [[BL, 20], [BL, 640]]); wire(bls, [[BLB, 20], [BLB, 640]]);
  netLab(bls, BL - 10, 216, 'BL', 'end'); netLab(bls, BLB + 10, 216, 'BLB');
  // cell A on BL under WL0; cell B on BLB under WL1
  const cell = (key, x, y, side, lab) => {
    const g = comp(L, key, {}, lab);
    const t = mosH(g, x, y, {lead: 24});
    const tx = side > 0 ? x + 30 : x - 30, cx = tx + side * 30;
    wire(g, [[side > 0 ? x - 30 : x + 30, y], [side > 0 ? BL : BLB, y]]); jn(g, side > 0 ? BL : BLB, y);
    wire(g, [[tx, y], [cx, y], [cx, y + 16]]);
    E('line', {class: 'rail', x1: cx - 16, y1: y + 16, x2: cx + 16, y2: y + 16}, g); E('line', {class: 'rail', x1: cx - 16, y1: y + 26, x2: cx + 16, y2: y + 26}, g);
    wire(g, [[cx, y + 26], [cx, y + 40]]); E('line', {class: 'rail', x1: cx - 18, y1: y + 40, x2: cx + 18, y2: y + 40}, g);
    netLab(g, cx + side * 22, y + 46, 'VPL', side > 0 ? 'start' : 'end');
    g._box = {x: Math.min(x - 34, cx - 20), y: y - 40, w: Math.abs(cx - x) + 56, h: 90};
    E('rect', {class: 'ring', x: g._box.x - 5, y: g._box.y - 5, width: g._box.w + 10, height: g._box.h + 10, rx: 8}, g);
    return {t, cap: {x: cx, y: y + 21}};
  };
  const cA = cell('cellA', 170, 77, 1, 'A 1T1C cell on BL: an access NMOS whose gate is WL0, in series with a storage capacitor; generic');
  const cB = cell('cellB', 490, 177, -1, 'A 1T1C cell on BLB, on WL1: not selected; generic');
  T(L, 104, 108, '⋮ many cells per bitline', 't-sm', 'end', 'dram:dram.org.die-internals');
  // the equaliser: three NMOS; VBLP = half the array voltage
  const ge = comp(L, 'eq', {}, 'The precharge and equalise circuit: three NMOS hold BL and BLB at half the array voltage between accesses; generic');
  const e3 = mosH(ge, 330, 262, {lead: 12});
  wire(ge, [[BL, 262], [300, 262]]); wire(ge, [[360, 262], [BLB, 262]]); jn(ge, BL, 262); jn(ge, BLB, 262);
  const e1 = mosV(ge, 200, 322, {lead: 10}), e2 = mosV(ge, 460, 322, {flip: true, lead: 10});
  wire(ge, [[BL, 292], [200, 292]]); wire(ge, [[BLB, 292], [460, 292]]); jn(ge, BL, 292); jn(ge, BLB, 292);
  E('line', {class: 'rail', x1: 190, y1: 356, x2: 470, y2: 356}, ge); wire(ge, [[200, 352], [200, 356]]); wire(ge, [[460, 352], [460, 356]]);
  netLab(ge, 330, 380, 'VBLP = VARY/2', 'middle'); netLab(ge, 330, 232, 'EQ', 'middle'); netLab(ge, 168, 328, 'EQ', 'end'); netLab(ge, 492, 328, 'EQ');
  ge._box = {x: 150, y: 218, w: 360, h: 170};
  // the sense amplifier: a cross-coupled latch, PMOS to SAP, NMOS to SAN, and the NMOS that fires SAN
  const gs = comp(L, 'sa', {}, 'The bitline sense amplifier: two NMOS and two PMOS cross-coupled; SAN and SAP fire it; generic');
  E('line', {class: 'rail', x1: 222, y1: 410, x2: 438, y2: 410}, gs); netLab(gs, 444, 416, 'SAP');
  const sp1 = mosV(gs, 240, 440, {p: true, flip: true, lead: 26}), sp2 = mosV(gs, 420, 440, {p: true, lead: 26});
  const sn1 = mosV(gs, 240, 520, {flip: true, lead: 26}), sn2 = mosV(gs, 420, 520, {lead: 26});
  const SL = sp1.gate.x, SR = sp2.gate.x;
  wire(gs, [[SL, 440], [SL, 520]]); wire(gs, [[SR, 440], [SR, 520]]);
  E('path', {class: 'w', d: `M240,474 H${SL - 7} A7,7 0 0 1 ${SL + 7},474 H${SR}`}, gs);
  E('path', {class: 'w', d: `M420,486 H${SR + 7} A7,7 0 0 0 ${SR - 7},486 H${SL}`}, gs);
  jn(gs, SR, 474); jn(gs, SL, 486);
  wire(gs, [[BL, 480], [240, 480]]); wire(gs, [[BLB, 480], [420, 480]]); jn(gs, BL, 480); jn(gs, BLB, 480); jn(gs, 240, 480); jn(gs, 420, 480);
  E('line', {class: 'rail', x1: 222, y1: 550, x2: 438, y2: 550}, gs); netLab(gs, 444, 556, 'SAN');
  const sd = mosV(gs, 330, 584, {lead: 20}); wire(gs, [[330, 550], [330, 554]]); gnd(gs, 330, 624); netLab(gs, sd.gate.x - 6, 584, 'SA_EN', 'end');
  gs._box = {x: 200, y: 400, w: 260, h: 230};
  // the column select to the local I/O lines
  const gcs = comp(L, 'csl', {}, 'Column select: two NMOS connect the pair to the local I/O lines when CSL rises; generic');
  const cs1 = mosV(gcs, BL, 612, {lead: 22}), cs2 = mosV(gcs, BLB, 612, {flip: true, lead: 22});
  wire(gcs, [[BL, 642], [BL, 664], [760, 664]]); wire(gcs, [[BLB, 642], [BLB, 686], [760, 686]]);
  netLab(gcs, cs1.gate.x - 4, 618, 'CSL', 'end'); netLab(gcs, cs2.gate.x + 4, 618, 'CSL');
  netLab(gcs, 766, 656, 'LIO'); netLab(gcs, 766, 692, 'LIOB');
  gcs._box = {x: 36, y: 602, w: 784, h: 92};
  // the write driver (a store) on the I/O lines
  part(L, 'wdrv', 860, 582, 218, 110, COL.logic, 'write driver', {kind: 'generic', sub: [{t: 'strong CMOS:', f: 'dram:dram.seq.store.04'}, {t: 'overpowers the', f: 'dram:dram.seq.store.04'}, {t: 'sense amplifier', f: 'dram:dram.seq.store.04'}]});
  ap.T = {a: cA.t, b: cB.t, e1, e2, e3, sp1, sp2, sn1, sn2, sd, cs1, cs2};
  ap.capA = cA.cap; ap.nodes = {BL: {x: BL, y: 300}, BLB: {x: BLB, y: 300}};
  ap.wave = {x: 690, y: 196, w: 388, h: 278};
  T(L, 690, 500, 'the bit is the charge on a capacitor;', 't-sm', 'start', 'dram:gen.cell'); T(L, 690, 521, 'it leaks: each row is refreshed', 't-sm', 'start', nf('dr_trefw'));
  T(L, 690, 542, `about every ${nt('dr_trefw')}`, 't-sm', 'start', nf('dr_trefw')); T(L, 690, 563, `(an all-bank REFRESH every ${nt('dr_trefi')})`, 't-sm', 'start', nf('dr_trefi') + ' dram:gen.refresh');
}
/* an activate: the equaliser lets go, the wordline rises, the cell shares its charge, the latch fires and restores */
async function dActivate(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T, nd = c.ap.nodes;
  [T0.e1, T0.e2, T0.e3].forEach(t => mos(c, t, true, {lab: false}));
  lit(c, ['eq', 'wld'], {noRing: true});
  await Promise.all([droop(tok, c, nd.BL.x - 34, 250, {from: 0.5, to: 0.5, l0: 'VARY/2', side: 'l', ms: 400}), droop(tok, c, nd.BLB.x + 34, 250, {from: 0.5, to: 0.5, l0: 'VARY/2', ms: 400})]);
  alive(tok);
  [T0.e1, T0.e2, T0.e3].forEach(t => mos(c, t, false, {lab: false}));
  fadeIn(T(c.fx, 250, 196, 'EQ off: the pair floats', 't-smb halo', 'middle'));
  await sweep(tok, c, c.ap.wl0, {label: 'WL0 rises, boosted', ms: 700, at: {x: 360, y: 40}, dy: -8});
  mos(c, T0.a, true, {cur: 'left', lab: false});
  lit(c, 'cellA');
  c.fx.querySelectorAll('.lvl').forEach(e => e.closest('g') && e.closest('g').remove());
  await Promise.all([droop(tok, c, nd.BL.x - 34, 250, {from: 0.5, to: 0.58, l0: 'VARY/2 + δ', side: 'l', ms: 800}), droop(tok, c, nd.BLB.x + 34, 250, {from: 0.5, to: 0.5, l0: 'VARY/2: the reference', ms: 800})]);
  alive(tok);
  fadeIn(T(c.fx, c.ap.capA.x + 70, c.ap.capA.y - 18, 'charge shared', 't-smb halo', 'start'));
  lit(c, 'sa');
  mos(c, T0.sd, true, {cur: 'down'});
  mos(c, T0.sn2, true, {cur: 'down', lab: false}); mos(c, T0.sn1, false, {lab: false});
  await wait(tok, 350);
  mos(c, T0.sp1, true, {lab: false}); mos(c, T0.sp2, false, {lab: false});
  c.fx.querySelectorAll('.lvl').forEach(e => e.closest('g') && e.closest('g').remove());
  await Promise.all([droop(tok, c, nd.BL.x - 34, 250, {from: 0.58, to: 1, l0: 'full: 1', side: 'l', ms: 600}), droop(tok, c, nd.BLB.x + 34, 250, {from: 0.5, to: 0, l0: 'ground: 0', ms: 600})]);
  fadeIn(T(c.fx, c.ap.capA.x + 70, c.ap.capA.y + 4, 'restored: the cell', 't-smb halo cell-note', 'start')); fadeIn(T(c.fx, c.ap.capA.x + 70, c.ap.capA.y + 26, 'is rewritten', 't-smb halo cell-note', 'start'));
  if (!o.noWave) await wave(tok, c, c.ap.wave, [
    {name: 'EQ', pts: [[0, 1], [0.12, 0]]},
    {name: 'WL0', pts: [[0, 0], [0.2, 1]], col: 'var(--c2)'},
    {name: 'BL', pts: [[0, 0.5], [0.3, 0.58], [0.5, 1]]},
    {name: 'BLB', pts: [[0, 0.5], [0.45, 0.5], [0.5, 0]]},
    {name: 'SA_EN', pts: [[0, 0], [0.42, 1]], col: 'var(--c1)'},
    {name: 'CSL', pts: [[0, 0], [0.7, o.col ? 1 : 0], [0.85, 0]]},
  ], {generic: true, ms: 1500, lw: 80});
}
async function dColumn(tok, c) {
  const T0 = c.ap.T;
  lit(c, 'csl');
  mos(c, T0.cs1, true, {cur: 'down', lab: false}); mos(c, T0.cs2, true, {lab: false});
  await sweep(tok, c, [{x: 120, y: 664}, {x: 760, y: 664}], {ms: 600, label: 'LIO: the bit, out', at: {x: 560, y: 664}, dy: -8});
  fadeIn(T(c.fx, -150, 560, `${nt('dr_256')} of the page`, 't-smb halo', 'start', nf('dr_256'))); fadeIn(T(c.fx, -150, 582, 'per READ', 't-smb halo', 'start', nf('dr_256')));
}
async function dPrecharge(tok, c) {
  const T0 = c.ap.T;
  mos(c, T0.a, false, {lab: false}); [T0.sp1, T0.sp2, T0.sn1, T0.sn2, T0.sd].forEach(t => mos(c, t, false, {lab: false}));
  c.fx.querySelectorAll('text').forEach(t => { if (t.textContent === 'WL0 rises, boosted') t.remove(); });
  fadeIn(T(c.fx, 360, 32, 'WL0 falls: the cell is isolated', 't-smb halo', 'middle'));
  await wait(tok, 400);
  [T0.e1, T0.e2, T0.e3].forEach(t => mos(c, t, true, {lab: false}));
  lit(c, 'eq');
  c.fx.querySelectorAll('.lvl').forEach(e => e.closest('g') && e.closest('g').remove());
  await Promise.all([droop(tok, c, c.ap.nodes.BL.x - 34, 250, {from: 1, to: 0.5, l0: 'back to VARY/2', side: 'l', ms: 600}), droop(tok, c, c.ap.nodes.BLB.x + 34, 250, {from: 0, to: 0.5, l0: 'back to VARY/2', ms: 600})]);
}
async function dWrite(tok, c) {
  await dActivate(tok, c, {noWave: true}); alive(tok);
  const T0 = c.ap.T;
  lit(c, ['wdrv', 'csl']);
  mos(c, T0.cs1, true, {lab: false}); mos(c, T0.cs2, true, {lab: false});
  await sweep(tok, c, [{x: 860, y: 664}, {x: 120, y: 664}], {ms: 600, label: 'the write driver pulls LIO low', at: {x: 130, y: 664}, dy: -8});
  mos(c, T0.sp1, false, {lab: false}); mos(c, T0.sn1, true, {cur: 'down', lab: false}); mos(c, T0.sp2, true, {lab: false}); mos(c, T0.sn2, false, {lab: false});
  c.fx.querySelectorAll('.lvl').forEach(e => e.closest('g') && e.closest('g').remove());
  await Promise.all([droop(tok, c, c.ap.nodes.BL.x - 34, 250, {from: 1, to: 0, l0: 'forced to 0', side: 'l', ms: 600}), droop(tok, c, c.ap.nodes.BLB.x + 34, 250, {from: 0, to: 1, l0: 'the latch flips', ms: 600})]);
  c.fx.querySelectorAll('text.cell-note').forEach(t => t.remove());
  ['the capacitor', 'discharges through', 'the open access NMOS'].forEach((t, i) => fadeIn(T(c.fx, c.ap.capA.x + 70, c.ap.capA.y - 18 + i * 22, t, 't-smb halo', 'start')));
  c.fx.querySelectorAll('text').forEach(t => { if (t.textContent === 'charge shared') t.remove(); });
  fadeIn(T(c.fx, -150, 520, 'write recovery:', 't-smb halo', 'start', nf('dr_nwr'))); fadeIn(T(c.fx, -150, 542, nt('dr_nwr'), 't-smb halo', 'start', nf('dr_nwr')));
}

/* ---- the PHY: DFI in, CA and DQ lanes out; trained receivers ---- */
function buildPHY(L, ap, inst) {
  frame(L, {title: 'PHY · one for both channels', sub: 'the lanes from the open RTL (derived); the circuits are generic', subf: 'dram:dram.topo.phy',
    tags: [['generic', 'GENERIC circuits'], ['documented', 'lanes, clock, rails']]});
  railBand(L, -150, 12, 1228, 678, 'pat-ddr', 'VDD_DDR and VDDQ');
  part(L, 'dfiin', -136, 30, 190, 620, COL.net, 'DFI', {sub: [{t: `${nt('dr_dfi')}, 1:2`, f: nf('dr_dfi')}, {t: 'from the two', f: 'dram:dram.topo.controllers'}, {t: 'controllers', f: 'dram:dram.topo.controllers'}]});
  part(L, 'pll', 70, 30, 200, 120, COL.logic, 'DRAM clock', {sub: [{t: nt('dr_dclk'), f: nf('dr_dclk')}, {t: `data: ${nt('dr_mts')}`, f: nf('dr_mts')}]});
  ap.lane = [];
  for (let k = 0; k < 2; k++) {
    const y = 170 + k * 250, on = k === inst.ch;
    part(L, 'anib', 70, y, 200, 220, COL.logic, `channel ${k}: CA`, {ctx: {i: k}, fo: on ? 0.1 : 0.04, sub: [{t: 'address/command', f: 'dram:dram.topo.phy'}, {t: 'blocks (ANIBs)', f: 'dram:dram.topo.phy'}, {t: 'CA[5:0], CK, CS', f: 'dram:gen.commands'}]});
    for (let b = 0; b < 2; b++) {
      const x = 290 + b * 290, g = part(L, 'dbyte', x, y, 274, 220, COL.xing, `DBYTE ${b}`, {ctx: {i: k * 2 + b}, fo: on ? 0.1 : 0.04, sub: [{t: `DQ[${b * 8 + 7}:${b * 8}], DQS, DMI`, f: 'dram:dram.topo.phy'}, {t: 'serialiser, driver,', f: 'dram:gen.io'}, {t: 'trained receiver', f: 'dram:dram.seq.load.09'}]});
      if (on && b === 0) { S(E('rect', {x: x + 14, y: y + 128, width: 70, height: 70, rx: 5, 'pointer-events': 'none'}, g), {fill: 'var(--surface)', stroke: 'var(--c5)', strokeWidth: 1.5}); T(g, x + 49, y + 170, 'DQ0', 't-smb', 'middle'); ap.dqBox = {x: x + 14, y: y + 128, w: 70, h: 70}; }
    }
    ap.lane[k] = {y: y + 110};
  }
  const gq = part(L, 'dqdrv', ap.dqBox.x, ap.dqBox.y, ap.dqBox.w, ap.dqBox.h, COL.xing, '', {child: 'dq', cur: true, fo: 0.15, label: 'The driver of pin DQ0: Enter zooms into its transistors'});
  part(L, 'topkg', 880, 30, 198, 620, COL.store, 'to the package', {sub: [{t: 'LPDDR4X, off the chip', f: 'dram:dram.topo.packages'}, {t: 'x16 per channel', f: 'dram:dram.topo.memshires'}, {t: `VDDQ ${nt('dr_vddq')}`, f: nf('dr_vddq')}, {t: '(aifoundry2)', f: nf('dr_vddq')}]});
  T(L, 70, 676, `the rails: VDD_DDR ${nt('dr_vddr')}; VDDQ ${nt('dr_vddq')}; no current sensor on either`, 't-sm halo', 'start', nf('dr_vddr') + ' ' + nf('dr_vddq'));
}
/* ---- the DQ pin: an LVSTL driver (N-over-N pull-up to VDDQ, NMOS pull-down), the trace, the receiver's termination
   to ground: a 1 costs current, a 0 almost none; DBI inverts a byte with more than four 1s (gen.io, dram.ctl.dbi) ---- */
function buildDQ(L, ap, inst) {
  frame(L, {title: 'One DQ pin · an LVSTL driver and its receiver', sub: 'LPDDR4X signalling from the JEDEC standard; the transistors are the vendor\'s choice', subf: 'dram:gen.io',
    tags: [['generic', 'GENERIC: LVSTL'], ['documented', 'DBI on, the rails']], col: 'var(--c5)', kind: 'generic'});
  const gd = comp(L, 'drv', {}, 'The output driver: an NMOS pull-up to VDDQ and an NMOS pull-down to ground; generic');
  E('line', {class: 'rail', x1: 160, y1: 40, x2: 260, y2: 40}, gd); netLab(gd, 266, 46, `VDDQ ${nt('dr_vddq')}`, 'start', nf('dr_vddq'));
  const pu = mosV(gd, 210, 110, {lead: 30}), pd = mosV(gd, 210, 250, {lead: 30});
  wire(gd, [[210, 80], [210, 40]]); wire(gd, [[210, 140], [210, 220]]); gnd(gd, 210, 290);
  jn(gd, 210, 180);
  netLab(gd, pu.gate.x - 6, 102, 'D', 'end'); netLab(gd, pd.gate.x - 6, 242, 'D̄', 'end');
  gd._box = {x: 120, y: 30, w: 170, h: 280};
  const gp = part(L, 'predrv', -150, 90, 190, 180, COL.logic, 'pre-driver', {sub: [{t: 'serialised data', f: 'dram:gen.io'}, {t: 'after DBI', f: 'dram:dram.ctl.dbi'}]});
  wire(L, [[40, 110], [pu.gate.x, 110]]); wire(L, [[40, 250], [pd.gate.x, 250]]);
  const gt = comp(L, 'trace', {}, 'The pad, the package and the board trace to the DRAM');
  wire(gt, [[210, 180], [700, 180]], 'bus'); T(gt, 455, 166, 'pad · package · trace', 't-sm', 'middle');
  gt._box = {x: 210, y: 150, w: 490, h: 50};
  const gr = comp(L, 'rx', {}, 'The receiver: its termination to ground (ODT) and a comparator against VREF; generic');
  E('path', {class: 'w', d: 'M720,180 V200 l10,6 l-20,12 l20,12 l-20,12 l20,12 l-10,6 V290'}, gr); jn(gr, 720, 180); gnd(gr, 720, 300);
  netLab(gr, 740, 260, 'ODT to ground');
  const cmp = E('path', {class: 'gate', d: 'M800,140 L880,180 L800,220 Z'}, gr);
  wire(gr, [[720, 180], [720, 160], [800, 160]]); wire(gr, [[770, 200], [800, 200]]); netLab(gr, 796, 224, 'VREF', 'end'); wire(gr, [[880, 180], [1000, 180]]); netLab(gr, 1006, 186, 'D');
  gr._box = {x: 700, y: 130, w: 330, h: 190};
  ap.T = {pu, pd};
  // DBI: a byte with more than four 1s goes inverted
  const gb = comp(L, 'dbi', {}, 'Data-bus inversion: a byte with more than four 1s is sent inverted, with the DBI pin high');
  T(gb, -150, 380, 'DBI, on for reads and writes', 't-labb', 'start', 'dram:dram.ctl.dbi');
  ap.byteY = 410; ap.byteX = -150;
  gb._box = {x: -150, y: 356, w: 1228, h: 150};
  ap.wave = {x: -150, y: 520, w: 800, h: 170};
  part(L, 'ioE', 680, 520, 398, 170, COL.aux, 'where the energy goes', {sub: [{t: `${nt('dr_unmet')} of a DRAM byte is on`, f: nf('dr_unmet')}, {t: 'no metered rail: PHY I/O,', f: 'dram:dram.e.unmetered'}, {t: 'DRAM core and I/O', f: 'dram:dram.e.unmetered'}, {t: 'the split: not measurable', f: 'dram:dram.e.split-unknown'}]});
}
async function dqDrive(tok, c, o) {
  o = o || {};
  const T0 = c.ap.T;
  lit(c, ['drv', 'trace', 'rx'], {noRing: true});
  mos(c, T0.pu, true, {cur: 'down', lab: false}); mos(c, T0.pd, false, {lab: false});
  fadeIn(netLab(c.fx, 60, 100, 'D = 1', 'start'));
  await sweep(tok, c, [{x: 210, y: 180}, {x: 720, y: 180}, {x: 720, y: 290}], {ms: 700, label: 'a 1: current from VDDQ through the termination', at: {x: 300, y: 180}, dy: -36});
  await wait(tok, 300);
  mos(c, T0.pu, false, {lab: false}); mos(c, T0.pd, true, {cur: 'down', lab: false});
  fadeIn(T(c.fx, 300, 236, 'a 0: the pull-down holds the pad', 't-smb halo', 'start')); fadeIn(T(c.fx, 300, 258, 'at ground: almost no current', 't-smb halo', 'start'));
  lit(c, 'dbi');
  const bitsIn = [1, 1, 1, 1, 0, 1, 1, 1], inv = bitsIn.filter(b => b).length > 4, out = inv ? bitsIn.map(b => 1 - b) : bitsIn;
  const g = E('g', {}, c.fx);
  const row = (y, arr, lab) => { T(g, c.ap.byteX, y + 24, lab, 't-sm'); arr.forEach((b, i) => { S(E('rect', {x: c.ap.byteX + 220 + i * 46, y, width: 40, height: 34, rx: 4}, g), {fill: b ? 'var(--c2)' : 'var(--surface)', fillOpacity: b ? 0.55 : 1, stroke: 'var(--ink-2)', strokeWidth: 1.25}); T(g, c.ap.byteX + 240 + i * 46, y + 24, String(b), 't-smb', 'middle'); }); };
  row(c.ap.byteY, bitsIn, 'the byte: seven 1s');
  fadeIn(g); await wait(tok, 500);
  row(c.ap.byteY + 46, out, 'sent inverted, DBI = 1');
  fadeIn(T(g, c.ap.byteX + 620, c.ap.byteY + 60, 'two 1s on the nine wires (one data', 't-smb', 'start'));
  fadeIn(T(g, c.ap.byteX + 620, c.ap.byteY + 82, 'bit and the DBI pin) instead of seven', 't-smb', 'start'));
  await wave(tok, c, c.ap.wave, [{name: 'DQ0', pts: [[0, 0], [0.2, 1], [0.45, 0], [0.7, 1]], col: 'var(--c2)'}, {name: 'DBI', pts: [[0, 0], [0.45, 1]]}], {generic: true, ms: 1300, lw: 70});
}

SCENES.dram = {
  lv: 'dram', title: 'DRAM (LPDDR4X)', short: 'DRAM', root: 'chip', inst: {},
  setInst() { const a = dec5(ADDR.pa); this.inst = Object.assign(a, {req: SCENES.l3.req}); },
  head: () => `${n('dr_ch')} of LPDDR4X at ${n('dr_mts')} behind 8 memory shires; a typical load takes ${n('lad_dram')} (${n('dr_500')}), ${n('dr_share')} of them in the DRAM, and ${n('lad_e_dram')} per byte`,
  addrFields(pa) {
    const a = dec5(pa);
    return [['memory shire', 'PA[8:6]', a.ms, 'dram:dram.addr.memshire', true], ['channel', 'PA[9]', a.ch, 'dram:dram.addr.channel', true], ['bank', 'PA[12:10]', a.bank, 'dram:dram.addr.pa-map', true],
      ['row', 'PA[34:18]', fnum(a.row), 'dram:dram.addr.pa-map', true], ['column', 'PA[17:13], PA[5:1]', a.colHi * 32, 'dram:dram.addr.pa-map'], ['half', 'PA[5]', a.half, 'dram:dram.addr.pa-map']];
  },
  scales: {
    chip: {name: 'Card and chip', short: 'Chip', parent: null, def: 'ms', build: buildDramChip},
    ms: {name: 'Memory shire', short: 'Memory shire', parent: 'chip', def: 'chan', tw: 56, target: (ap, inst) => ap.B['m' + inst.ms], build: buildMS, label: inst => `memory shire ${inst.ms}`},
    chan: {name: 'Channel and die', short: 'Channel', parent: 'ms', def: 'dbank', tw: 90, target: (ap, inst) => ap.die[inst.ch].box, build: buildChan, label: inst => `channel ${inst.ch}`},
    dbank: {name: 'Bank and subarray', short: 'Bank', parent: 'chan', def: 'dcell', tw: 200, target: (ap, inst) => ap.bank[inst.bank].box, build: buildDBank, label: inst => `bank ${inst.bank}`},
    dcell: {name: 'Cell and sense amplifier', short: 'Cell', parent: 'dbank', def: null, tw: 46, target: ap => ap.cellBox, build: buildDCell},
    phy: {name: 'PHY and pins', short: 'PHY', parent: 'ms', def: 'dq', tw: 116, target: ap => ap.phyBox, build: buildPHY},
    dq: {name: 'DQ driver', short: 'DQ driver', parent: 'phy', def: null, tw: 70, target: ap => ap.dqBox, build: buildDQ},
  },
};
const DP = SCENES.dram.parts = {
  overview: () => ({kick: 'Level 5 · key 5', title: 'The DRAM', badge: [['documented', 'topology, timings, map, energy'], ['generic', 'the die\'s circuits'], ['unknown', 'the part, the 63 cycles, the energy split']],
    what: `${n('dr_gb')} of LPDDR4X from Micron on the V3 cards, ${n('dr_ch')} of 16 bits, each memory shire driving two. The firmware runs them at ${n('dr_mts')} (not the datasheet's 4,266): ${n('dr_peak')} peak, ${n('dr_bw')} measured. A typical load from shire 0 takes ${n('lad_dram')}: ${n('dr_share')} of it is the DRAM's own timing and ${n('dr_ms63')} the L3 home's miss path and the memory shire, not split. A byte costs ${n('lad_e_dram')}, about ${n('dr_unmet')} of it on no metered rail; on random data a DRAM byte is ${n('dr_vs')} one from the own scratchpad (${n('dr_e1')} against ${n('lad_e_scp1')} pJ/B). The cell is the textbook 1T1C, a capacitor that leaks: the controller sends an all-bank REFRESH every ${n('dr_trefi')}, and each row, so each cell, is refreshed about every ${n('dr_trefw')} (${n('dr_8192')}).`,
    kpis: [K('dr_gb', 'on the V3 cards'), K('lad_dram', 'a typical load'), K('lad_e_dram', 'per byte, above idle'), K('dr_mts', 'programmed')],
    extra: ladderHtml('dram')}),
  shire: ctx => ({kick: 'DRAM · chip', title: `Shire ${ctx.id}${ctx.id === I5().home ? ': the L3 home' : ''}${ctx.id === I5().req ? ' (the requester)' : ''}`, badge: [['documented', 'measured map']], facts: 'chipmap',
    what: `A load that misses the L3 goes from the line's home (PA[10:6] = ${I5().home}) to memory shire PA[8:6] = ${I5().ms}, always the home's low three bits. From this shire the whole load costs ${cn(load5(hopsC(SHC[ctx.id], SHC[I5().home]), hopsC(SHC[I5().home], MSC[I5().ms])), 'dram:dram.lat.model', 0, 'cycles')} by the fit.`,
    act: `<button type="button" class="st-btn" data-act="req" data-id="${ctx.id}">Requester here</button>`}),
  memshire: ctx => ({kick: 'DRAM · chip', title: `Memory shire ${ctx.id}`, badge: [['documented', 'spec, measured fit']], facts: 'memshire',
    what: `It serves the lines whose PA[8:6] = ${ctx.id}, those homed in L3 slices ${ctx.id}, ${ctx.id + 8}, ${ctx.id + 16} and ${ctx.id + 24}. Its two controllers drive two 16-bit channels through one PHY. Its place, one hop outside the grid, comes from a fit of DRAM latencies${ctx.cell && ctx.cell.tie ? '; for this one three places fit equally (a tie-break)' : ''}.`,
    act: ctx.id === I5().ms ? `<button type="button" class="st-btn" data-act="zoom" data-to="ms">Zoom into memory shire ${ctx.id}</button>` : ''}),
  grey: () => L3P.grey({cell: {name: 'no compute shire'}}),
  pkg: ctx => ({kick: 'DRAM · card', title: 'An LPDDR4X package', badge: [['documented', 'four packages, four channels each'], ['unknown', 'which memory shires share one']], facts: 'pkg',
    what: 'Four LPDDR4X packages on the card, each with four 16-bit channels (64 bits a package, 256 in all); two memory shires share each package. Which two is not documented: the drawing pairs neighbours on an assumption, dashed. The card\'s schematic would settle it.'}),
  model: () => ({kick: 'DRAM · latency', title: 'A whole DRAM load', badge: [['documented', 'measured, three cards']], facts: 'model',
    what: `${n('dr_model')}: the L3 part (${n('dr_c110')} + ${n('l3_hopcyc')} per hop to the home) and the rest (${n('l3_dram91')} to the memory shire). Left as fitted on aifoundry2, it is within ±3 cycles for ${n('dr_fit93')}–${n('dr_fit97')} of loads on each of three cards. The memory shire's position adds ${n('dr_mshops')}. At 800 MHz the fit splits a load into ${n('dr_clk')}: most of it does not scale with the minion clock.`}),
  typical: () => ({kick: 'DRAM · latency', title: 'Where the ~300 cycles go', badge: [['documented', 'measured'], ['derived', 'the DRAM\'s share'], ['unknown', 'the split of the rest']], facts: 'model',
    what: `A typical load: ${n('lad_dram')} (${n('dr_500')}); a pointer chase ${n('dr_chase')}. The constant past an L3 hit at the same home is ${n('l3_dram91')}: ${n('dr_share')} of it are the DRAM's own timing (the activate and the read latency with two bursts); the rest, ${n('dr_ms63')}, is the L3 home's miss path and its To_Sys crossings (about 12 cycles by the spec: an L3 miss is ${n('l3_miss42')} against ${n('l3_spec30')} for a hit) plus the memory shire's port, crossing, controller and PHY, not split.`}),
  rate: () => ({kick: 'DRAM · bandwidth', title: 'The channels', badge: [['documented', 'firmware, measured']], facts: 'rate',
    what: `The firmware hard-codes the "933 MHz" DDR mode on every card: the controller clock is ${n('dr_dfi')}, the DRAM clock ${n('dr_dclk')} and the data rate ${n('dr_mts')}, not the datasheet's 4,266. A channel peaks at ${n('dr_peakch')}, the chip at ${n('dr_peak')}; streaming, the chip reaches ${n('dr_bw')}. Each memory shire's NoC side (${n('dr_noc32')}) has about twice its DRAM side.`}),
  energy: () => ({kick: 'DRAM · energy', title: 'What a DRAM byte costs', badge: [['documented', 'measured'], ['unknown', 'the split']], facts: 'energy',
    what: `${n('lad_e_dram')} per byte above idle, ${n('dr_e_line')} per line; ${n('dr_e0')} on zeros against ${n('dr_e1')} on random data: even DRAM is data-dependent. About ${n('dr_unmet')} lands on no metered rail (${n('dr_73')} pJ per byte on aifoundry2 and aifoundry3 in the PHY, the I/O rail and the DRAM chips): how it splits cannot be measured on the card. Row hits and misses cost the same (${n('dr_rows_e')} pJ/B), so an activation is too small to see; a store costs what a load does, and a store through the L1 ${n('dr_wb')}.`}),
  pll: () => ({kick: 'DRAM · chip', title: 'The memory PLLs', badge: [['documented', 'firmware']], facts: 'rate', what: 'The boot firmware programs the memory PLL in memory shire 0 and memory shire 4 only: one PLL per side of the die.'}),
  addrmap: () => ({kick: 'DRAM · address', title: 'The address map', badge: [['documented', 'spec, measured by bit flips']], facts: 'addrmap',
    what: 'PA[8:6] picks the memory shire, so consecutive 64-byte lines rotate over all eight; PA[9] the controller (channel), alternating every 512 bytes; the memory shire removes PA[9:6]. Inside a channel: bank PA[12:10], row PA[34:18], column PA[17:13] and PA[5:1] (a 2 KB page). A 256 KB aligned block touches one row in each of the 128 channel-banks.'}),
  vddr: () => ({kick: 'DRAM · power', title: 'The memory rails', badge: [['documented', 'measured, the card\'s figure']], facts: 'rails',
    what: `VDD_DDR feeds the memory shires: ${n('dr_vddr')}, read ${n('dr_vmeas')} at idle by their own monitors, and it droops ${n('dr_droop')} of off-rail DRAM power: a proxy DRAM meter. VDD_QLP is the LPDDR4X I/O supply, ${n('dr_vddq')}. None of the three memory rails reports current.`}),
  // the memory shire
  noc: () => ({kick: 'DRAM · memory shire', title: 'The NoC port', badge: [['documented', 'spec']], facts: 'mspath', what: `An AXI slave with a 512-bit data path, a whole 64-byte line per beat; the NoC side delivers at most ${n('dr_noc32')} per memory shire. Two more ports carry global-atomic responses and ESR accesses.`}),
  xing: () => ({kick: 'DRAM · memory shire', title: 'The clock crossing', badge: [['documented', 'the clocks'], ['derived', 'its place']], facts: 'mspath', what: `From the mesh's 400 MHz into the controller's ${n('dr_dfi')}. Where exactly the crossing sits in the memory shire is inferred, and its share of the memory shire's cycles is part of what is asked.`}),
  strip: () => ({kick: 'DRAM · memory shire', title: 'Channel select and address strip', badge: [['documented', 'spec, firmware'], ['derived', 'the steering mux']], facts: 'addrmap', what: 'PA[9] picks the controller: the memory shire\'s control register resets with its controller-select field at bit 9, both controllers enabled, and the default boot never rewrites it. The memory shire then removes PA[9:6], so each controller sees its own lines as one contiguous space.'}),
  settings: () => ({kick: 'DRAM · memory shire', title: 'What the firmware switches off', badge: [['documented', 'firmware']], facts: 'settings', what: `No power-down and no self-refresh ("for performance reasons"): an idle channel stays in active standby. No automatic ZQ calibration. DRAM ECC off. The controller does request PHY re-trims (DFI updates) every ${n('dr_dfiupd')}.`}),
  atomic: () => ({kick: 'DRAM · memory shire', title: 'The atomic unit', badge: [['documented', 'spec']], facts: 'settings', what: 'The memory shire has an atomic unit with a small atomic cache (a register flags which of its entries hold dirty data): the datasheet lists LPDDR4X support for global atomic operations.'}),
  perfmon: () => ({kick: 'DRAM · memory shire', title: 'Performance monitor', badge: [['documented', 'spec']], facts: 'settings', what: `${n('dr_perf')} and two event counters; the firmware sets them to count mesh reads and writes, which a user kernel can sample. The same monitor could count activates, precharges and refreshes per bank, but only M-mode can select that.`}),
  ctl: ctx => ({kick: 'DRAM · memory shire', title: `uMCTL2 controller ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'firmware']], facts: 'ctl',
    what: `A Synopsys uMCTL2 per 16-bit channel. Two AXI ports with aging, port 0 at priority ${n('dr_p0')} and port 1 at ${n('dr_p1')}; the address map; a transaction store giving ${n('dr_cam')} to low-priority reads; a scheduler that serves ${n('dr_runs')} of one kind before switching; open-page policy, no page-close timer, no auto-precharge; all-bank refresh every ${n('dr_trefi')}.`}),
  dfi: () => ({kick: 'DRAM · memory shire', title: 'DFI', badge: [['documented', 'firmware']], facts: 'ctl', what: `The controller-to-PHY interface, at ${n('dr_dfi')}, 1:2 with the DRAM clock (${n('dr_dclk')}).`}),
  phy: () => ({kick: 'DRAM · memory shire', title: 'One PHY for two channels', badge: [['derived', 'firmware and RTL'], ['documented', 'the lanes']], facts: 'phy',
    what: 'The firmware writes one PHY training message block per memory shire, with MR14 set for channel A and channel B; the open RTL gives the memory shire\'s DDR subsystem 4 data-byte lanes (2 per channel) and 6 address/command blocks. The datasheet says two PHYs share one controller: the page follows the firmware and the RTL.',
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="phy">Zoom into the PHY</button>`}),
  die: ctx => ({kick: 'DRAM · memory shire', title: `Channel ${ctx.i != null ? ctx.i : ''}: an LPDDR4X die`, badge: [['documented', 'capacity, geometry'], ['unknown', 'the part']], facts: 'part',
    what: `2 GB per channel: ${n('dr_geom')}. Whether a channel is one x16 die or two byte-mode dies, the die's density and the Micron part number are not in any source; the firmware reads them from mode registers at every boot but no log has been captured.`,
    act: ctx.i === I5().ch ? `<button type="button" class="st-btn" data-act="zoom" data-to="chan">Zoom into channel ${ctx.i}</button>` : ''}),
  lat63: () => ({kick: 'DRAM · memory shire', title: 'The cycles past the DRAM\'s timing', badge: [['derived', 'the bound'], ['unknown', 'the split']], facts: 'lat63',
    what: `The constant past an L3 hit is ${n('l3_dram91')}; ${n('dr_share')} are the DRAM's own. The rest, ${n('dr_ms63')}, holds the L3 home's miss handling and To_Sys crossings (about 12 cycles by the spec's ${n('l3_miss42')} against ${n('l3_spec30')}) and the memory shire: its NoC port and clock crossing, the address strip, the controller's port, CAM and scheduler, the DFI and the PHY's paths. How they split is asked; the memory shire's own counters could time some of it.`}),
  // the channel
  dbanks: ctx => ({kick: 'DRAM · channel', title: `Bank ${ctx.i != null ? ctx.i : ''}`, badge: [['documented', 'geometry (derived)'], ['generic', 'the insides']], facts: 'geom',
    what: `One of 8 in the channel's one rank: ${n('dr_rows')} of a 2 KB page (1,024 columns of 16 bits). A channel puts consecutive lines of its own in consecutive banks; a bank's row holds 32 lines 8 KB apart, which can be read as row hits while the row stays open.`,
    act: ctx.i === I5().bank ? `<button type="button" class="st-btn" data-act="zoom" data-to="dbank">Zoom into bank ${ctx.i}</button>` : ''}),
  cmd: () => ({kick: 'DRAM · channel', title: 'Commands', badge: [['generic', 'JEDEC'], ['documented', 'the timings']], facts: 'cmd', what: 'LPDDR4 commands travel on a 6-bit single-data-rate bus: an activate is two 2-clock parts, a read or write RD-1/WR-1 plus CAS-2, a precharge 2 clocks.'}),
  prefetch: () => ({kick: 'DRAM · channel', title: 'Prefetch and serialiser', badge: [['generic', 'JEDEC']], facts: 'column', what: `A READ fetches 16 bits per DQ pin at once (16n prefetch): ${n('dr_256')} for a x16 channel, serialised 16:1 onto each pin as one BL16 burst of 32 bytes in ${n('dr_burst')}; a 64-byte line takes two READs to the same row.`}),
  pins: () => ({kick: 'DRAM · channel', title: 'The data pins', badge: [['documented', 'firmware'], ['generic', 'LVSTL, the pin count']], facts: 'io', what: `16 DQ pins, two DQS strobe pairs and two DMI (mask/inversion) pins, one of each per byte, at ${n('dr_mts')}; data-bus inversion is on for reads and writes and data masking is enabled (the controller's DBICTL).`}),
  tl: () => ({kick: 'DRAM · channel', title: 'The timeline, to scale', badge: [['documented', 'the programmed timings'], ['generic', 'the JEDEC comparison']], facts: 'timings',
    what: `Activate at 0; the first READ after tRCD ${n('dr_trcd')} (${n('dr_trcd_c')}); the second one burst later; data after RL ${n('dr_rl')}, two bursts of ${n('dr_burst')}; no precharge (open page). Writes: WL ${n('dr_wl')}, write recovery ${n('dr_nwr')}. A conflict: tRP ${n('dr_trp')}, tRC ${n('dr_trc')}. An all-bank refresh every ${n('dr_trefi')}, lasting ${n('dr_trfc')}. Compared with JEDEC LPDDR4 as recalled, not checked against the standard (generic): the timings are close to its limits for this density and rate, tREFI just under its ${n('g_trefi_max')} maximum, and RL and WL are the fixed values for the rate.`}),
  // the bank inside and the cell
  rowdec: () => ({kick: 'DRAM · bank', title: 'Row decoder', badge: [['generic', 'textbook']], facts: 'wordline', what: 'Decodes the 17-bit row to one of 131,072 rows and tells the sub-wordline drivers of that row\'s mats to fire.'}),
  mat: () => ({kick: 'DRAM · bank', title: 'A mat', badge: [['generic', 'textbook'], ['unknown', 'the vendor\'s organisation']], facts: 'mat', what: 'A block of cells: local wordlines across, bitline pairs down, bounded by sub-wordline drivers and sense-amplifier stripes. An activate raises one local wordline in each mat of a row of mats, so the whole 2 KB page is sensed. Cells per bitline, mats per bank and open or folded bitlines are the vendor\'s and not published.'}),
  swd: () => ({kick: 'DRAM · bank', title: 'Sub-wordline drivers', badge: [['generic', 'textbook']], facts: 'wordline', what: 'Local drivers pull a local wordline to a boosted voltage, above the array voltage, so each access NMOS passes a full level.'}),
  blsa: () => ({kick: 'DRAM · bank', title: 'Sense-amplifier stripes', badge: [['generic', 'textbook']], facts: 'sense', what: `Each bitline pair ends in a latch; together the ${n('dr_16k_n')} latches of an activated row are the open page, the "row buffer".`}),
  coldec: () => ({kick: 'DRAM · bank', title: 'Column decoder', badge: [['generic', 'textbook']], facts: 'column', what: 'A READ raises one column-select line, connecting the chosen sense amplifiers to the local and global I/O lines.'}),
  gio: () => DP.coldec(), cellpick: () => DP.cellA(),
  wld: () => ({kick: 'DRAM · cell', title: 'The wordline', badge: [['generic', 'textbook']], facts: 'wordline', what: 'The activate: the row decoder selects the (sub-)wordline driver, which pulls its wordline to a boosted voltage above the array voltage, so every access NMOS on the row turns fully on.'}),
  cellA: () => ({kick: 'DRAM · cell', title: 'A 1T1C cell', badge: [['generic', 'textbook'], ['unknown', 'the vendor\'s cell']], facts: 'cell',
    what: 'One access NMOS, its gate the wordline, its drain the bitline, in series with a storage capacitor: the charge is the bit. It leaks away, hence refresh, and reading it is destructive until the sense amplifier restores it.'}),
  cellB: () => DP.cellA(),
  eq: () => ({kick: 'DRAM · cell', title: 'Precharge and equalise', badge: [['generic', 'textbook']], facts: 'eq', what: 'Between accesses three NMOS hold the pair at half the array voltage (VBLP = VARY/2): two tie BL and BLB to it, one shorts them together. EQ turns off just before a wordline rises; after a precharge it turns back on.'}),
  sa: () => ({kick: 'DRAM · cell', title: 'The sense amplifier', badge: [['generic', 'textbook']], facts: 'sense', what: 'The cell shares its charge with its bitline, nudging it slightly above or below half the voltage. Then the NMOS side is pulled to ground and the PMOS side to the array voltage: the cross-coupled latch drives the pair to full rail, which also rewrites the cell.'}),
  csl: () => ({kick: 'DRAM · cell', title: 'Column select', badge: [['generic', 'textbook']], facts: 'column', what: `A READ raises CSL: two NMOS connect the latched pair to the local I/O lines, and secondary amplifiers pass the bits on. ${n('dr_256')} of the page leave per READ.`}),
  wdrv: () => ({kick: 'DRAM · cell', title: 'A write', badge: [['generic', 'textbook']], facts: 'write', what: `The write drivers, strong CMOS, overpower the selected sense amplifiers through the column-select transistors; the latches flip and, through the still-open access transistors, charge or discharge the cells. Write recovery, ${n('dr_nwr')}, must pass before a precharge.`}),
  // the PHY and the pin
  dfiin: () => DP.dfi(), pll2: () => DP.rate(),
  anib: () => ({kick: 'DRAM · PHY', title: 'Address and command lanes', badge: [['derived', 'RTL'], ['generic', 'the circuits']], facts: 'phy', what: 'The PHY\'s address/command blocks drive each channel\'s CA pins, clock and chip select at the DRAM clock, with the same LVSTL drivers as the data pins.'}),
  dbyte: () => ({kick: 'DRAM · PHY', title: 'A data-byte lane', badge: [['derived', 'RTL'], ['generic', 'the circuits']], facts: 'io', what: 'Eight DQ pins, a strobe pair and the mask/inversion pin: serialisers and drivers out, and receivers trained at boot to capture the data on the strobe coming in.'}),
  dqdrv: () => DP.drv(), topkg: () => DP.pkg({}),
  drv: () => ({kick: 'DRAM · pin', title: 'An LVSTL driver', badge: [['generic', 'JEDEC, textbook']], facts: 'io',
    what: `Each DQ driver pulls up to VDDQ (${n('dr_vddq')} on aifoundry2; the standard's ${n('dr_vddq6')}) or down to ground, and the receiver terminates to ground: a driven 1 draws current through the termination, a 0 almost none. LPDDR4X's pull-up is usually an NMOS (N-over-N); the transistors are the vendor's.`}),
  predrv: () => DP.drv(), trace: () => DP.drv(), rx: () => DP.drv(),
  dbi: () => ({kick: 'DRAM · pin', title: 'Data-bus inversion', badge: [['documented', 'on (the firmware)'], ['generic', 'how it works']], facts: 'io', what: 'A byte with more than four 1s is sent inverted, with the DBI pin high: at most four 1s cross on its nine wires, the DBI pin included, and since only 1s draw current through the termination, DBI saves I/O energy on data full of 1s.'}),
  ioE: () => DP.energy(),
};

/* ---- the DRAM's accesses ---- */
/* a token that draws a circuit's state at once (a recap before the part the step is about) and dies with its step */
const ffOf = tok => ({get dead() { return tok.dead; }, ff: true});
const H5 = () => { const I = I5(); return [SHC[I.req], SHC[I.home], MSC[I.ms]]; };
async function msIn(tok, c, o) {
  o = o || {};
  const a = c.ap, k = I5().ch, C0 = a.ctl[k];
  const pk = PKM(c, a.noc, o.col);
  await travel(tok, c.fx, pk, [a.noc, a.xg, a.st], 900, {col: o.col});
  return pk;
}
function tlCursor(c, ns, lab) {
  const x = c.ap.tlX(ns), g = E('g', {}, c.fx);
  S(E('line', {x1: x, y1: 488, x2: x, y2: 666}, g), {stroke: 'var(--c2)', strokeWidth: 3});
  if (lab) T(g, x + 6, 668, lab, 't-smb halo', 'start');
  return fadeIn(g);
}
async function tlSweep(tok, c, a, b, lab) {
  const X = c.ap.tlX, tt = c.ap.tlTitle;
  if (lab && tt) {
    let bb = null; try { bb = tt.getBBox(); } catch (_) { /* not rendered */ }
    if (bb) { tt.classList.add('swap'); TOUCH.add(tt); }   // the drawn title gives way to the access's
    fadeIn(S(T(c.fx, 1064, 478, `${lab} · to scale in ns`, 't-smb', 'end'), {fill: 'var(--c2)'}));
  }
  await sweep(tok, c, [{x: X(a), y: 459}, {x: X(b), y: 459}], {ms: 700, w: 5});
}
const DA = SCENES.dram.access = {};
DA.load = {
  led: () => { const [, H, M] = H5(); return [[src(nt('l3_miss42') + ' (spec)', nf('l3_miss42')), null], [cn(12 * hopsC(H, M), 'dram:dram.lat.model', 0) + ' both ways', null], [null, null], [null, null], [null, null], [null, null],
    [src(nt('dr_trcd_c'), nf('dr_trcd_c')), null], [src('tCCD ' + nt('dr_burst'), nf('dr_burst')), null], [src(nt('dr_rl17'), nf('dr_rl17')), null], [null, null], [null, null]]; },
  tot: () => { const [R, H, M] = H5(); return {c: `${n('lad_dram')} typical; ${cn(load5(hopsC(R, H), hopsC(H, M)), 'dram:dram.lat.model', 0)} by the fit here`, e: `${n('lad_e_dram')}/B, ${n('dr_e_line')} a line`}; },
  ask: {c: 'ask-memshire', e: 'rung20'},
  cap: () => `A DRAM load to a closed row: ${n('lad_dram')} typical, ${n('dr_share')} of it in the DRAM; ${n('lad_e_dram')} per byte, about ${n('dr_unmet')} on no metered rail.`,
  steps: [
    {name: 'L3 miss', where: 'chip', say: () => `The line's L3 home, shire ${I5().home}, misses and sends a 64-byte read over its 512-bit To_Sys port (the spec: ${n('l3_miss42')} for the miss)`,
      run: async (tok, c) => { const [, H] = H5(); litTile(c, 'shire', H.id); const p = c.ap.P[ckey(H)]; PKM(c, p); sayAt(c, p.x, p.y, ['the L3 home misses', 'see the L3 (key 3)'], {side: 'r'}); counter(c, `${nt('l3_miss42')}`, 'the spec, idle'); await pulse(tok, c.fx, p, 900); }},
    {name: 'To memory', where: 'chip', say: () => `The read crosses ${hopsC(SHC[I5().home], MSC[I5().ms])} hops to memory shire PA[8:6] = ${I5().ms}: ${n('l3_hopcyc')} a hop, counted both ways`,
      run: async (tok, c) => { const [, H, M] = H5(); litTile(c, 'shire', H.id); litTile(c, 'memshire', M.id); counter(c, `${hopsC(H, M)} hops × 12`, 'round trip, measured'); await hopTravel(tok, c, H, M, {label: (k, n0) => `hop ${k} of ${n0}`}); }},
    {name: 'Port, crossing', where: 'ms', say: () => `The memory shire takes the read, crosses from the mesh clock to its own, uses PA[9] = ${I5().ch} to pick controller ${I5().ch}, and strips PA[9:6]`,
      run: async (tok, c) => { lit(c, ['noc', 'xing', 'strip']); counter(c, 'part of the ≤ 63 cycles', 'not split: asked'); await msIn(tok, c); sayAt(c, 289, 250, [`PA[9] = ${I5().ch}: controller ${I5().ch}`, 'PA[9:6] removed'], {side: 'd'}); }},
    {name: 'Controller', where: 'ms', say: () => `Controller ${I5().ch} maps the address to bank ${I5().bank}, row ${fnum(I5().row)}; the read waits in its CAM; the bank is closed (a refresh closed it)`,
      run: async (tok, c) => { const C0 = c.ap.ctl[I5().ch]; lit(c, 'ctl', {i: I5().ch}); const pk = PKM(c, c.ap.st); await travel(tok, c.fx, pk, [c.ap.st, {x: 380, y: C0.cam.y}, C0.cam, C0.sch], 1000); sayAt(c, C0.x, C0.box.y + C0.box.h, [`bank ${I5().bank}, row ${fnum(I5().row)}`, 'the bank is closed'], {side: 'd'}); }},
    {name: 'ACT', where: 'ms', say: () => `The controller issues ACTIVATE (two parts) with the bank and row; the PHY drives it onto the channel's CA pins at ${n('dr_dclk')}`,
      run: async (tok, c) => { const C0 = c.ap.ctl[I5().ch], D0 = c.ap.die[I5().ch]; lit(c, ['dfi', 'phy']); lit(c, 'die', {i: I5().ch}); const pk = PKM(c, C0.sch); await travel(tok, c.fx, pk, [C0.sch, {x: 803, y: C0.sch.y}, {x: 912, y: C0.sch.y}, {x: 912, y: D0.y - 40}, {x: 988, y: D0.y - 40}], 1100); sayAt(c, 988, D0.y - 40, ['ACT on CA[5:0]'], {side: 'l'}); }},
    {name: 'Wordline', where: 'dbank', dive: ['dcell'], say: () => `In bank ${I5().bank}, the equalisers let go and the row's wordline rises, boosted: the access transistors of the page's ${n('dr_16k')} turn on`,
      run: async (tok, c) => {
        lit(c, ['rowdec', 'swd']); const ms = c.ap.mat.filter(m => m.on);
        await Promise.all(ms.map(m => sweep(tok, c, [{x: m.x + 6, y: c.ap.wlY}, {x: m.x + m.w - 6, y: c.ap.wlY}], {ms: 700, w: 5})));
        ms.forEach(m => ringAround(c.fx, m, {fo: 0.08, sw: 3}));
        sayAt(c, 360, 330, ['one local wordline in each mat', 'of the row: the whole page'], {side: 'd'});
      },
      deep: {dcell: (tok, c) => dActivate(tok, c, {noWave: true})}},
    {name: 'Sense', where: 'dcell', say: () => `The sense amplifiers fire and latch the whole row, restoring every cell; the bank is open once tRCD, ${n('dr_trcd')} (${n('dr_trcd_c')}), has passed`,
      run: async (tok, c) => { counter(c, `tRCD ${nt('dr_trcd')}`, nt('dr_trcd_c') + ', programmed'); await dActivate(tok, c); }},
    {name: 'Two READs', where: 'chan', dive: ['dcell'], say: () => `Two READs, one ${n('dr_burst')} after the other, fetch the line's two 32-byte halves from the open row: ${n('dr_512of')}`,
      run: async (tok, c) => {
        const B0 = c.ap.bank[I5().bank]; lit(c, 'dbanks', {i: I5().bank}); lit(c, 'tl', {noRing: true});
        await sweep(tok, c, [{x: B0.ax, y: B0.rowY}, {x: B0.ax + B0.aw, y: B0.rowY}], {ms: 500, w: 4, col: 'var(--c3)'});
        const seg = B0.aw / 32, x0 = B0.ax + I5().colHi * seg;
        S(E('rect', {x: x0, y: B0.rowY - 7, width: seg, height: 14, rx: 2}, c.fx), {fill: 'var(--c2)'});
        callout(c.fx, x0 + seg / 2, B0.rowY, [{t: `the line: ${nt('dr_1_32')} of the page`, f: nf('dr_1_32')}], {side: 'r', fs: 19});
        await tlSweep(tok, c, 0, 24.6, 'ACT … RD, RD');
      },
      deep: {dcell: async (tok, c) => { await dActivate(ffOf(tok), c, {noWave: true}); alive(tok); await dColumn(tok, c); }}},
    {name: 'DQ bursts', where: 'phy', dive: ['dq'], say: () => `After the read latency, ${n('dr_rl')}, the DRAM drives two 32-byte bursts at ${n('dr_mts')} with read DBI; the PHY's trained receivers capture them (${n('dr_rl17')})`,
      run: async (tok, c) => { lit(c, ['dbyte', 'topkg']); const pk = PKM(c, {x: 979, y: c.ap.lane[I5().ch].y}, 'var(--c7)'); await travel(tok, c.fx, pk, [{x: 979, y: c.ap.lane[I5().ch].y}, {x: 580, y: c.ap.lane[I5().ch].y}, {x: 170, y: c.ap.lane[I5().ch].y}, {x: -41, y: c.ap.lane[I5().ch].y}], 1400, {col: 'var(--c7)', w: 9}); counter(c, `RL + 2 bursts: ${nt('dr_rl17')}`, 'programmed'); },
      deep: {dq: (tok, c) => dqDrive(tok, c, {})}},
    {name: 'Back', where: 'ms', say: () => 'The line goes back through the controller and the clock crossing onto the 512-bit NoC port. The row stays open: no precharge follows (open page)',
      run: async (tok, c) => { const C0 = c.ap.ctl[I5().ch]; lit(c, ['ctl', 'noc']); const pk = PKM(c, {x: 912, y: C0.sch.y}, 'var(--c7)'); await travel(tok, c.fx, pk, [{x: 912, y: C0.sch.y}, C0.sch, {x: 380, y: C0.sch.y}, c.ap.st, c.ap.xg, c.ap.noc], 1300, {col: 'var(--c7)'}); sayAt(c, 572, C0.box.y + 30, ['the row stays open'], {side: 'u'}); }},
    {name: 'To the requester', where: 'chip', say: () => { const [R, H, M] = H5(); return `The line returns to the L3 home, which installs it, and on to the requester: ${cn(load5(hopsC(R, H), hopsC(H, M)), 'dram:dram.lat.model', 0)} cycles by the fit, ${n('lad_dram')} typical`; },
      run: async (tok, c) => { const [R, H, M] = H5(); litTile(c, 'memshire', M.id); litTile(c, 'shire', R.id); counter(c, `${fnum(load5(hopsC(R, H), hopsC(H, M)))} cycles`, 'the fit, three cards'); await hopTravel(tok, c, M, H, {col: 'var(--c7)', w: 9}); await hopTravel(tok, c, H, R, {col: 'var(--c7)', w: 9}); }},
  ]};
DA['row-hit'] = {
  led: [[src('− ' + nt('dr_rowhit'), nf('dr_rowhit')), src(nt('dr_rows_e'), nf('dr_rows_e'))]], tot: () => ({c: `saves ${n('dr_rowhit')}`, e: 'the same per byte'}),
  cap: () => `A row hit: the row is still open, so no activate: it saves ${n('dr_rowhit')}; the energy per byte is the same.`,
  steps: [
    {name: 'Row open', where: 'chan', dive: ['dcell'], say: () => `The row is still open (no refresh, no other row since): the controller issues the READs at once and saves ${n('dr_rowhit')}`,
      run: async (tok, c) => { lit(c, 'tl', {noRing: true}); lit(c, 'dbanks', {i: I5().bank}); const X = c.ap.tlX; S(E('line', {x1: X(0), y1: 527, x2: X(18.2), y2: 527}, c.fx), {stroke: 'var(--ink)', strokeWidth: 3}); fadeIn(T(c.fx, X(9), 548, '✕ no ACT, no tRCD', 't-smb halo', 'middle')); counter(c, `− ${nt('dr_rowhit')}`, 'measured, three cards'); await tlSweep(tok, c, 18.2, 46.1, 'READs at once'); },
      deep: {dcell: async (tok, c) => { await dActivate(ffOf(tok), c, {noWave: true}); alive(tok); await dColumn(tok, c); }}},
  ]};
DA['row-conflict'] = {
  led: [[src('+ ' + nt('dr_seq10') + ' / + ' + nt('dr_conf37'), nf('dr_conf37')), src(nt('dr_rows_e'), nf('dr_rows_e'))]], tot: () => ({c: `+ ${n('dr_seq10')} after, + ${n('dr_conf37')} together`, e: 'not separable'}),
  cap: () => `A row conflict: another row of the bank is open, so PRECHARGE, then ACTIVATE: + ${n('dr_seq10')} one after the other, + ${n('dr_conf37')} when issued together.`,
  steps: [
    {name: 'PRE, then ACT', where: 'dbank', dive: ['dcell'], say: () => `Another row of the bank is open: the controller precharges it (tRP ${n('dr_trp')}), then activates the new one, no sooner than tRC ${n('dr_trc')} after the last activate`,
      run: async (tok, c) => { lit(c, ['rowdec', 'blsa']); counter(c, `+ ${nt('dr_seq10')} · + ${nt('dr_conf37')}`, 'after · together, measured'); const ms = c.ap.mat.filter(m => m.on); await Promise.all(ms.map(m => sweep(tok, c, [{x: m.x + 6, y: c.ap.wlY - 27}, {x: m.x + m.w - 6, y: c.ap.wlY - 27}], {ms: 500, w: 4, col: 'var(--ink-2)'}))); callout(c.fx, 360, c.ap.wlY - 27, ['the old row closes'], {side: 'u', fs: 19}); await Promise.all(ms.map(m => sweep(tok, c, [{x: m.x + 6, y: c.ap.wlY}, {x: m.x + m.w - 6, y: c.ap.wlY}], {ms: 700, w: 5}))); },
      deep: {dcell: async (tok, c) => { await dActivate(ffOf(tok), c, {noWave: true}); alive(tok); await dPrecharge(tok, c); alive(tok); c.fx.textContent = ''; TOUCH.forEach(e => e.classList.remove('on', 'off')); await dActivate(tok, c, {noWave: true}); }}},
  ]};
DA.store = {
  led: [[null, null], [null, null], [src('WL ' + nt('dr_wl'), nf('dr_wl')), null], [src(nt('dr_nwr'), nf('dr_nwr')), null], [null, src(nt('dr_st1'), nf('dr_st1'))]],
  tot: () => ({c: 'not measured apart', e: `${n('dr_st0')} / ${n('dr_st1')} pJ/B (tensor store)`}), ask: {c: 'ask-memshire', e: 'rung20'},
  cap: () => `A store reaches DRAM only when its dirty line leaves the L3: WRITE after WL ${n('dr_wl')}; the energy is a load's; through the L1, ${n('dr_wb')}.`,
  steps: [
    {name: 'L3 victim', where: 'chip', say: () => 'A dirty line leaves the L3 (an eviction, a flush, or a tensor store that bypasses the caches) as a 64-byte write to memory shire PA[8:6]',
      run: async (tok, c) => { const [, H, M] = H5(); litTile(c, 'shire', H.id); litTile(c, 'memshire', M.id); await hopTravel(tok, c, H, M, {col: 'var(--c5)', w: 9}); }},
    {name: 'Write queue', where: 'ms', say: () => `The write waits with its data in the controller's write store; the scheduler drains writes in runs of ${n('dr_runs')} and pays the read/write turnarounds`,
      run: async (tok, c) => { const C0 = c.ap.ctl[I5().ch]; lit(c, 'ctl', {i: I5().ch}); const pk = await msIn(tok, c, {col: 'var(--c5)'}); await travel(tok, c.fx, pk, [c.ap.st, {x: 380, y: C0.sch.y}, C0.sch], 700, {col: 'var(--c5)'}); sayAt(c, C0.x, C0.box.y + C0.box.h, [`runs of ${nt('dr_runs')}`], {side: 'd'}); }},
    {name: 'WRITE', where: 'phy', dive: ['dq'], say: () => `WRITE on the CA pins; ${n('dr_wl')} later the PHY drives 32 bytes on DQ, with write DBI and data masking available`,
      run: async (tok, c) => { lit(c, ['dbyte', 'anib']); const y = c.ap.lane[I5().ch].y, pk = PKM(c, {x: -41, y}, 'var(--c5)'); await travel(tok, c.fx, pk, [{x: -41, y}, {x: 170, y}, {x: 580, y}, {x: 979, y}], 1300, {col: 'var(--c5)', w: 9}); },
      deep: {dq: (tok, c) => dqDrive(tok, c, {})}},
    {name: 'Into the cells', where: 'dbank', dive: ['dcell'], say: () => `The DRAM's write drivers overpower the selected sense amplifiers through the column-select transistors; the latches flip and rewrite the cells; ${n('dr_nwr')} before any precharge`,
      run: async (tok, c) => { lit(c, ['coldec', 'gio', 'blsa']); const ms = c.ap.mat.filter(m => m.on); ms.forEach(m => ringAround(c.fx, m, {fo: 0.08, sw: 3})); counter(c, `nWR ${nt('dr_nwr')}`, 'programmed'); await sweep(tok, c, [{x: 800, y: 629}, {x: -60, y: 629}], {ms: 800, w: 5, under: true, label: 'CSL: the written columns', at: {x: 420, y: 629}, dy: 6}); },
      deep: {dcell: dWrite}},
    {name: 'Measured', where: 'chip', say: () => `Tensor stores to DRAM run at ${n('dr_bw')} and cost ${n('dr_st0')} pJ/B on zeros, ${n('dr_st1')} on random data: indistinguishable from loads. Stores through the L1 cost ${n('dr_wb')}: each allocates its line first`,
      run: async (tok, c) => { const [, , M] = H5(); litTile(c, 'memshire', M.id); counter(c, `${nt('dr_st1')} pJ/B`, 'random data, three cards'); const p = c.ap.P[ckey(M)]; sayAt(c, p.x, p.y, [`${nt('dr_st0')} / ${nt('dr_st1')} pJ/B`, 'the same as a load'], {side: 'r'}); await pulse(tok, c.fx, p, 900); }},
  ]};
DA.refresh = {
  led: [[src(nt('dr_trefi'), nf('dr_trefi')), null], [src(nt('dr_trfc'), nf('dr_trfc')), null], [src('≤ ' + nt('dr_ref208'), nf('dr_ref208')), null], [null, null]],
  tot: () => ({c: `every ${n('dr_ref')}`, e: 'not measured'}), ask: {e: 'rung20'},
  cap: () => `Refresh: every ${n('dr_trefi')} each channel refreshes all 8 banks for ${n('dr_trfc')}; measured every ${n('dr_ref')} on every card.`,
  steps: [
    {name: 'The timer', where: 'ms', say: () => `Every tREFI, ${n('dr_trefi')}, the controller closes the channel's open rows and issues an all-bank REFRESH: no per-bank refresh, no temperature derating (measured: every ${n('dr_ref')})`,
      run: async (tok, c) => { const C0 = c.ap.ctl[I5().ch]; lit(c, 'ctl', {i: I5().ch}); ringAround(c.fx, {x: 404, y: C0.ref.y - 20, w: 336, h: 28}, {fo: 0.3}); counter(c, `every ${nt('dr_trefi')}`, 'programmed; measured the same'); const pk = PKM(c, C0.ref, 'var(--c5)'); await travel(tok, c.fx, pk, [C0.ref, {x: 912, y: C0.ref.y}, {x: 988, y: C0.ref.y}], 900, {col: 'var(--c5)'}); }},
    {name: 'All 8 banks', where: 'chan', dive: ['dcell'], say: () => `The die's counter activates and precharges a batch of rows in all 8 banks at once, about ${n('dr_gen16')} (textbook, for this density), with no column access: ${n('dr_trfc')}`,
      run: async (tok, c) => { lit(c, 'dbanks'); c.ap.bank.forEach(B0 => quiet(sweep(tok, c, [{x: B0.ax, y: B0.box.y + 100}, {x: B0.ax + B0.aw, y: B0.box.y + 100}], {ms: 600, w: 4}))); counter(c, `tRFCab ${nt('dr_trfc')}`, 'programmed'); await wait(tok, 900); },
      deep: {dcell: async (tok, c) => { await dActivate(tok, c, {noWave: true}); alive(tok); await wait(tok, 300); await dPrecharge(tok, c); fadeIn(T(c.fx, -150, 520, 'no column access:', 't-smb halo', 'start')); fadeIn(T(c.fx, -150, 542, 'refresh only restores', 't-smb halo', 'start')); }}},
    {name: 'Loads wait', where: 'chan', say: () => `A load that meets a refresh waits up to ${n('dr_ref208')}; ${n('dr_duty')} of loads at random times do. The next load finds its row closed and pays an activate`,
      run: async (tok, c) => { lit(c, 'tl', {noRing: true}); counter(c, `≤ ${nt('dr_ref208')}`, `${nt('dr_duty')} of loads, measured`); await tlSweep(tok, c, 0, 46.1, 'waits, then activates'); }},
    {name: 'Energy?', where: 'ms', say: () => 'Refresh energy is part of the idle power, which the card\'s meters do not split: it is not measured (current sensing below the regulators is not possible on the card)',
      run: async (tok, c) => { lit(c, 'lat63'); counter(c, 'not measured', 'asked'); sayAt(c, 460, 606, ['refresh energy: part of idle,', 'not split by any meter'], {side: 'u'}); await wait(tok, 900); }},
  ]};
SCENES.dram.accOrder = [['load', 'Load (closed row)', 'Load'], ['row-hit', 'Row hit', 'Row hit'], ['row-conflict', 'Row conflict', 'Conflict'], ['store', 'Store', 'Store'], ['refresh', 'Refresh', 'Refresh']];
SCENES.dram.tour = [
  {name: 'Card and chip', path: ['chip'], panel: 'pkg', hi: ['pkg', 'memshire', 'model'],
    cap: () => `Eight memory shires drive ${n('dr_ch')} in four LPDDR4X packages; which two share a package is not documented`,
    sub: () => `A line's memory shire is PA[8:6]: a whole load is ${n('dr_model')}.`},
  {name: 'The memory shire', path: ['chip', 'ms'], panel: 'lat63', hi: ['lat63', 'ctl', 'phy'],
    cap: () => `Two controllers and one PHY: with the L3 home's miss path, ${n('dr_ms63')} of every load are spent here, and how is not split`,
    sub: () => 'The firmware switches off power-down, self-refresh, automatic ZQ and ECC.'},
  {name: 'The timings', path: ['chip', 'ms', 'chan'], panel: 'tl', hi: ['tl', 'dbanks'], play: (tok, c) => tlSweep(tok, c, 0, 46.1, 'a closed-row load'),
    cap: () => `The programmed timings, to scale: tRCD ${n('dr_trcd')}, RL ${n('dr_rl')}, bursts of ${n('dr_burst')}`,
    sub: () => `${n('dr_mts')}, not the datasheet's 4,266; close to JEDEC's limits for this rate (a generic comparison, unverified).`},
  {access: 'load', dive: true},
  {name: 'Sense and restore', path: ['chip', 'ms', 'chan', 'dbank', 'dcell'], panel: 'sa', hi: ['sa', 'cellA', 'eq'], dive: true, play: async (tok, c) => { await dActivate(tok, c); await dColumn(tok, c); },
    cap: () => 'A cell shares its charge with its bitline; the latch amplifies the difference to full rail and so rewrites the cell',
    sub: () => 'A textbook circuit: the vendor\'s cell, voltages and sense amplifier are not published (asked).'},
  {name: 'Row hits and conflicts', path: ['chip', 'ms', 'chan'], panel: 'tl', hi: ['tl'],
    cap: () => `A row hit saves ${n('dr_rowhit')}; a conflict costs ${n('dr_seq10')} after, ${n('dr_conf37')} together`,
    sub: () => `The energy per byte is the same either way (${n('dr_rows_e')} pJ/B).`},
  {access: 'refresh'},
  {name: 'Energy', path: ['chip'], panel: 'energy', hi: ['energy', 'vddr'],
    cap: () => `${n('lad_e_dram')} per byte; on random data ${n('dr_vs')} the own scratchpad; about ${n('dr_unmet')} of it on no metered rail`,
    sub: () => 'The memory shires\' rail droops with DRAM power, a proxy meter; the split between PHY, DRAM core and I/O is not measurable.'},
  {name: 'What is asked', path: ['chip'], panel: 'overview', hi: ['pkg', 'model'],
    cap: () => 'Asked: the DRAM part, the package pairing, the 63 cycles of the home and the memory shire; not measurable: the energy split',
    sub: () => 'The asks are under the diagram, each tied to the hub\'s ladder.'},
];

/* ================= levels, tabs, accesses, the address ================= */
function tabsUI() {
  document.querySelectorAll('#tabs [role="tab"]').forEach(t => { const on = t.dataset.lv === Z.lv; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; });
  $('stage-view').setAttribute('aria-labelledby', 'tab-' + Z.lv);
}
function accButtonsUI() {
  const row = $('acc-row'), had = focusIn(row), sc = SC();
  row.innerHTML = '<span class="lab2">Accesses</span>' + sc.accOrder.map(([k, lg, sh], i) => `<button type="button" class="st-btn" data-acc="${k}" aria-pressed="${AC.k === k}" title="${esc(lg)} ([ and ] step through the accesses)"><span class="al">${esc(lg)}</span><span class="as">${esc(sh)}</span></button>`).join('');
  row.querySelectorAll('button[data-acc]').forEach(b => b.addEventListener('click', () => pickAccess(b.dataset.acc)));
  fitHead();
  refocus(row, had);
}
function fitHead() {
  const row = $('acc-row'), tabs = $('tabs'); row.classList.remove('nolab', 'short');
  if (window.matchMedia('(max-width: 899px)').matches) return;
  const wraps = () => row.getBoundingClientRect().top > tabs.getBoundingClientRect().top + 6;
  if (wraps()) row.classList.add('nolab');
  if (wraps()) row.classList.add('short');
}
window.addEventListener('resize', () => { clearTimeout(fitHeadT); fitHeadT = setTimeout(fitHead, 150); });
let fitHeadT = 0;
/* the legend: the three badges, the part colours, and the rail bands this level draws */
const BANDS = {'pat-lv': 'minion rail (LV region)', 'pat-hv': 'Shire Channel (HV; its logic\'s rail: asked)', 'pat-mesh': 'mesh rail',
  'pat-ddr': 'VDD_DDR (memory shires)', 'pat-hatch': 'hatched: idle, or not split (asked)'};
const BAND_SW = {'pat-lv': '<pattern id="lg-lv" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="var(--ink-2)" stroke-width="1.5"/></pattern>',
  'pat-hv': '<pattern id="lg-hv" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="var(--ink-2)"/></pattern>',
  'pat-mesh': '<pattern id="lg-mesh" width="5" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="2" x2="5" y2="2" stroke="var(--ink-2)" stroke-width="1.2"/></pattern>',
  'pat-ddr': '<pattern id="lg-ddr" width="4" height="5" patternUnits="userSpaceOnUse"><line x1="2" y1="0" x2="2" y2="5" stroke="var(--ink-2)" stroke-width="1.2"/></pattern>',
  'pat-hatch': '<pattern id="lg-hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(135)"><line x1="0" y1="0" x2="0" y2="4" stroke="var(--ink-2)" stroke-width="1.2"/></pattern>'};
function legendUI() {
  const used = new Set();
  [LAYERS[0], LAYERS[Z.path.length - 1]].forEach(L => L && L.querySelectorAll('[style*="pat-"], [fill*="pat-"]').forEach(e => {
    const m = /#(pat-[a-z]+)/.exec((e.getAttribute('style') || '') + ' ' + (e.getAttribute('fill') || '')); if (m) used.add(m[1]);
  }));
  const bands = Object.keys(BANDS).filter(k => used.has(k)).map(k => `<span><svg width="16" height="12" aria-hidden="true"><defs>${BAND_SW[k]}</defs><rect width="16" height="12" rx="2" fill="url(#lg-${k.slice(4)})" stroke="var(--ink-2)"/></svg>${esc(BANDS[k])}</span>`).join('');
  const html = '<span><span class="kd spec">documented</span></span><span><span class="kd generic">generic</span></span><span><span class="kd unknown">unknown · asked</span></span>'
    + '<span><i style="border-color:var(--c1);background:color-mix(in srgb,var(--c1) 14%,transparent)"></i>logic</span><span><i style="border-color:var(--c3);background:color-mix(in srgb,var(--c3) 14%,transparent)"></i>storage</span>'
    + '<span><i style="border-color:var(--c4)"></i>interconnect</span><span><i style="border-color:var(--c5)"></i>crossing</span>' + bands;
  const f = $('pn-foot'); if (f && f.innerHTML !== html) f.innerHTML = html;
}
function addrUI() {
  const el = $('addr'), sc = SC(), pa = sc.pa ? sc.pa() : ADDR.pa, f = sc.addrFields(pa);
  el.innerHTML = `<span>example line</span><span class="pa" data-f="${sc.paF || 'dram:dram.addr.region'}" title="${sc.pa ? 'a scratchpad line' : 'a DRAM-region line'}">${hexPA(pa)}</span>`
    + '<span class="flds">' + f.map(([nm, b, v, fid, hi]) => `<span class="fld${hi ? ' hi' : ''}" data-f="${fid}">${esc(nm)}${b ? ` <span>${esc(b)}</span>` : ''}${v !== '' ? ` <b>${esc(String(v))}</b>` : ''}</span>`).join('') + '</span>'
    + (f.length ? '<button type="button" class="st-btn" data-act="newpa">New address</button>' : '')
    + `<button type="button" class="st-btn fit" data-act="fit" aria-pressed="${$('svgwrap').classList.contains('fitted')}" title="The whole level at the screen's width (small text); again: a readable size, scrolling sideways">Fit to screen</button>`;
}
$('addr').addEventListener('click', e => { const b = e.target.closest('button[data-act]'); if (b && ACTS[b.dataset.act]) ACTS[b.dataset.act](b); });
async function setLevel(lv, o) {
  o = o || {};
  if (!SCENES[lv]) return;
  if (Z.lv === lv && Z.path.length && !o.force) { if (!o.noHash) setHash(lv); return; }
  if (TOUR && !o.keepTour) endTour();
  killAccess(); AC.k = null; AC.done = false; AC.still = false; liveCap(true);
  ZGEN++; ZT = null; CUR = null;
  if (ZW) { ZW = false; const w = ZWAIT; ZWAIT = []; w.forEach(r => r()); }
  Z.lv = lv;
  SC().setInst();
  LAYERS.forEach(L => { L.textContent = ''; L.style.display = 'none'; L.style.opacity = 0; setT(L, null); L.classList.remove('busy', 'zout'); L.style.removeProperty('--lab'); L.style.removeProperty('--ctx'); });
  Z.path = [SC().root];
  buildLayer(0, SC().root); LAYERS[0].style.display = ''; LAYERS[0].style.opacity = 1;
  select(null); clearFx();
  tabsUI(); accButtonsUI(); scaleUI(); pipUpdate(); addrUI();
  showPart('overview');
  if (!TOUR) resetCap();
  renderBar(); playBtn();
  if (!o.noHash) setHash(lv);
  $('lvl-live').textContent = 'Level: ' + SC().title;
}
document.querySelectorAll('#tabs [role="tab"]').forEach(t => {
  t.addEventListener('click', () => setLevel(t.dataset.lv));
  t.addEventListener('keydown', e => {
    const tabs = [...document.querySelectorAll('#tabs [role="tab"]')], i = tabs.indexOf(t);
    let j = -1;
    if (e.key === 'ArrowRight') j = (i + 1) % tabs.length; else if (e.key === 'ArrowLeft') j = (i + tabs.length - 1) % tabs.length;
    else if (e.key === 'Home') j = 0; else if (e.key === 'End') j = tabs.length - 1;
    if (j < 0) return;
    e.preventDefault(); e.stopPropagation();
    tabs[j].focus(); setLevel(tabs[j].dataset.lv);
  });
});
function pickAccess(k) {
  if (TOUR) { const j = TOUR.list.findIndex(it => it.lv === Z.lv && it.s.access === k); if (j >= 0) { tourGo(j); return; } endTour(); }
  if (FOLLOW_AUTO) setFollow(true);
  startAccess(k, 0);
}
function stepAccess(d) {
  const ord = SC().accOrder.map(a => a[0]); if (!ord.length) return;
  const cur = AC.k ? ord.indexOf(AC.k) : (d > 0 ? -1 : 0);
  pickAccess(ord[(cur + d + ord.length) % ord.length]);
}
/* ---- the address bar keeps the view: #<level>[/<access>[/<step>[/<scale>]]] ---- */
const LV_ALIAS = {l1: 'l1', l2: 'l2', l3: 'l3', scp: 'scp', scratchpad: 'scp', dram: 'dram'};
function parseHash(h) {
  const m = /^#?([a-z0-9]+)(?:\/([\w-]+))?(?:\/(\d+))?(?:\/([\w-]+))?$/i.exec(h || '');
  if (!m) return null;
  const lv = LV_ALIAS[m[1].toLowerCase()]; if (!lv) return null;
  // #<level>/<scale> (no access) is a zoomed view
  if (m[2] && !m[3] && !m[4] && !SCENES[lv].access[m[2]] && SCENES[lv].scales[m[2]]) return {lv, acc: null, step: null, scale: m[2]};
  return {lv, acc: m[2] || null, step: m[3] ? +m[3] : null, scale: m[4] || null};
}
function setHash(lv, acc, step, scale) {
  const h = '#' + [lv, acc, step, scale].filter(x => x != null && x !== '').join('/');
  if (location.hash === h) return;
  try { history.replaceState(null, '', location.pathname + location.search + h); } catch (_) { /* sandboxed */ }
  if (window.parent !== window) { try { window.parent.postMessage({type: 'ss-hash', hash: h}, '*'); } catch (_) { /* no parent */ } }
}
async function applyHash(h, o) {
  const p = parseHash(h); if (!p) return false;
  await setLevel(p.lv, {noHash: true, force: p.lv !== Z.lv || !Z.path.length});
  const sc = SCENES[p.lv];
  const scale = p.scale && sc.scales[p.scale] ? p.scale : null;
  if (p.acc && sc.access[p.acc]) {
    const i = p.step ? clamp(p.step - 1, 0, sc.access[p.acc].steps.length - 1) : 0;
    if (scale) { sc.setInst(); await goTo(pathTo(scale), {ms: 0}); setFollow(false, true); }
    startAccess(p.acc, i, {still: !!p.step, noHash: true});
    setHash(p.lv, p.acc, p.step ? i + 1 : null, scale);
  } else { if (scale) await goTo(pathTo(scale), {ms: 0}); setHash(p.lv, null, null, scale); }
  if (o && o.scroll) { try { $('stage').scrollIntoView({block: 'start'}); } catch (_) { /* no layout */ } }
  return true;
}
window.addEventListener('hashchange', () => { if (parseHash(location.hash)) applyHash(location.hash, {scroll: true}); });

/* ================= captions and the tour ================= */
const glue = html => String(html).replace(/<\/span> (?=(?:W|s|cycles|GB\/s|TB\/s|pJ|pJ\/B|ns|µs|°C|MB|KB|mV|V|mm|bits?|rows?|hops?)\b)/g, '</span> ');
function setCap(html) { hideTip(); $('cap').innerHTML = `<span class="cap-in">${glue(html)}</span>`; fitCap(); }
function fitCap() {
  const c = $('cap'); c.style.fontSize = ''; c.style.height = '';
  if (window.matchMedia('(max-width: 899px)').matches) return;
  const base = parseFloat(getComputedStyle(c).fontSize), h = Math.round(base * 2.56);
  c.style.height = h + 'px';
  let fs = base;
  while (c.scrollHeight > h + 1 && fs > 13) { fs -= 1; c.style.fontSize = fs + 'px'; }
}
let fitT = 0;
window.addEventListener('resize', () => { clearTimeout(fitT); fitT = setTimeout(fitCap, 120); });
function setKick(t) { $('cap-k').textContent = t; }
function sub(html) { const e = $('cap-sub'); e.innerHTML = glue(html); e.classList.remove('hint'); }
const focusIn = box => { const a = document.activeElement; return a && box.contains(a) ? [...box.querySelectorAll('button')].indexOf(a) : -1; };
const refocus = (box, k) => { if (k < 0) return; const b = box.querySelectorAll('button')[k]; if (b) b.focus({preventScroll: true}); };
let TOUR = null;
const slideName = it => it.s.access ? `${SCENES[it.lv].short}: ${accTitleOf(it.lv, it.s.access)}` : `${SCENES[it.lv].short}: ${it.s.name}`;
const accTitleOf = (lv, k) => (SCENES[lv].accOrder.find(a => a[0] === k) || [k, k])[1];
function dots(i) {
  const d = $('dots'), had = focusIn(d); d.textContent = '';
  if (i < 0 || !TOUR) return;
  TOUR.list.forEach((it, k) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = k < i ? 'past' : k === i ? 'on' : '';
    b.setAttribute('aria-label', `Tour slide ${k + 1}: ${slideName(it)}`); b.title = `Slide ${k + 1}: ${slideName(it)}`;
    if (k === i) b.setAttribute('aria-current', 'step');
    b.addEventListener('click', () => tourGo(k));
    d.appendChild(b);
  });
  refocus(d, had);
}
function highlight(keys) {
  svg.classList.add('dimming');
  const d = Z.path.length - 1;
  keys.forEach(k => (AP[d].parts[k] || []).forEach(g => g.classList.add('hi')));
}
function tourList(all) { const lvs = all ? LEVELS : [Z.lv]; return lvs.flatMap(lv => (SCENES[lv].tour || []).map(s => ({lv, s}))); }
async function tourGo(i, o) {
  if (!TOUR) return;
  o = o || {};
  i = clamp(i, 0, TOUR.list.length - 1); TOUR.i = i;
  const it = TOUR.list[i], s = it.s;
  if (TOUR.tok) TOUR.tok.dead = true;
  const tok = TOUR.tok = {dead: false};
  select(null);
  if (it.lv !== Z.lv) await setLevel(it.lv, {keepTour: true});
  if (!TOUR || TOUR.i !== i) return;
  dots(i);
  if (!FOLLOW) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); }
  setDive(s.dive ? true : DIVE_USER, true);
  if (s.access) {
    if (o.back) startAccess(s.access, stepsOf(s.access).length - 1, {still: true, done: true, noHash: true});
    else startAccess(s.access, 0, {noHash: true});
    return;
  }
  stopAccess(true);
  setKick(`Tour ${i + 1} / ${TOUR.list.length} · ${SCENES[it.lv].short} · ${s.name}`);
  setCap(s.cap()); sub(s.sub ? s.sub() : '');
  if (s.panel) showPart(s.panel);
  renderBar(); playBtn();
  await goTo(s.path, CLK.on ? {clk: tok, cap: 3200} : {total: 600});   // a tour's long dives are capped at 3.2 s
  if (!TOUR || TOUR.i !== i || tok.dead) return;
  if (s.hi) highlight(s.hi);
  // a slide may play its circuit once the camera is there (the latch, a cell's read, a hop)
  if (s.play && CLK.on) { const c = {}; setCtx(c); quiet(s.play(tok, c)); }
}
function presentClass() { $('stage').classList.toggle('present', !!TOUR || PRES || !!fsEl()); }
function startTour(all, at) {
  const list = tourList(all);
  if (!list.length) return;
  TOUR = {list, i: 0, all: !!all}; $('btn-tour').textContent = 'End tour'; $('btn-tour').classList.add('on');
  presentClass();
  tourGo(at || 0);
}
function endTour() {
  if (!TOUR) return;
  if (TOUR.tok) TOUR.tok.dead = true;
  TOUR = null; $('btn-tour').textContent = 'Tour'; $('btn-tour').classList.remove('on');
  presentClass(); dots(-1); clearDim();
  if (!AC.k) clearFx();
  setDive(DIVE_USER, true);
  if (AC.k) { setKick(accKick(AC.k)); CAPACC = true; renderBar(); playBtn(); } else resetCap();
}
const toggleTour = all => { if (TOUR) { endTour(); stopAccess(); } else startTour(all, 0); };
const HINT = TOUCHSCR ? 'Tap a part for its details, again to zoom in · swipe the drawing sideways, or Fit to screen'
  : '1–5 levels · [ ] accesses · Space pauses · ← → steps · + − zoom · V dive · F presents · P panel · C follow · T tour';
function resetCap() {
  CAPACC = false;
  setKick(`${SC().title} · explore`);
  setCap(stageLine(SC().head()));
  sub(HINT); $('cap-sub').classList.add('hint'); renderBar();
}
function renderBar() {
  const ol = $('stages'), had = focusIn(ol); ol.textContent = '';
  const k = AC.k;
  $('stage').classList.toggle('playing', accOn() && CLK.on && !AC.still);
  const chip = (num, name, cls, title, go, dv) => {
    const li = document.createElement('li'), b = document.createElement('button');
    if (/\bon\b/.test(cls)) { li.className = 'on'; b.setAttribute('aria-current', 'step'); }
    b.type = 'button'; b.className = 'stg' + cls;
    b.innerHTML = `<span class="sn">${num}</span><span class="st">${esc(name)}</span>${dv ? '<span class="dv" aria-hidden="true">▾</span>' : ''}`;
    b.title = title; b.setAttribute('aria-label', title);
    b.addEventListener('click', go);
    li.appendChild(b); ol.appendChild(li);
  };
  ol.classList.remove('many');
  if (!k) {
    if (TOUR) TOUR.list.forEach((it, j) => { if (it.lv !== Z.lv) return; const nm = it.s.access ? accTitleOf(it.lv, it.s.access) + ' ▸' : it.s.name; chip(j + 1, nm, j < TOUR.i ? ' past' : j === TOUR.i ? ' on' : '', `Tour slide ${j + 1} of ${TOUR.list.length}: ${it.s.access ? 'the access ' + accTitleOf(it.lv, it.s.access) : it.s.name}`, () => tourGo(j)); });
    else { const li = document.createElement('li'); li.className = 'stg-hint'; li.textContent = 'Pick an access above to see its steps here, or press Tour'; ol.appendChild(li); }
    refocus(ol, had);
    $('btn-prev').disabled = TOUR ? TOUR.i === 0 : false; $('btn-next').disabled = !!TOUR && TOUR.i === TOUR.list.length - 1;
    return;
  }
  const sts = stepsOf(k);
  ol.classList.toggle('many', sts.length > 9);
  sts.forEach((s, i) => chip(i + 1, s.name, i < AC.i ? ' past' : i === AC.i ? ' on' : '', `Step ${i + 1} of ${sts.length}: ${s.name}${s.dive ? ' (it has a circuit: V dives into it)' : ''}`, () => goStep(i), s.dive && s.dive.length));
  refocus(ol, had);
  $('btn-prev').disabled = AC.i === 0 && !(TOUR && TOUR.i > 0);
  $('btn-next').disabled = AC.i === sts.length - 1 && !(TOUR && TOUR.i < TOUR.list.length - 1);
}
function playBtn() {
  const b = $('btn-play'), still = !!TOUR && !TOUR.list[TOUR.i].s.access;
  const t = AC.k ? (AC.done ? 'Replay' : (CLK.on && !AC.still ? 'Pause' : 'Play')) : still ? (CLK.on ? 'Pause' : 'Play') : 'Play';
  b.textContent = t;
  b.style.visibility = still ? 'hidden' : '';
  b.setAttribute('aria-label', t + ' (Space)');
  $('stage').classList.toggle('playing', accOn() && CLK.on && !AC.still);
}
function playPause() {
  if (!AC.k) {
    if (TOUR && !TOUR.list[TOUR.i].s.access) { CLK.on = !CLK.on; playBtn(); return; }
    const k = SC().lastAcc || (SC().accOrder[0] || [])[0]; if (k) startAccess(k, 0);
    return;
  }
  if (AC.done) { startAccess(AC.k, 0, {keepInst: true}); return; }
  if (AC.still) {
    CLK.on = true;
    if (AC.i < stepsOf(AC.k).length - 1) startAccess(AC.k, AC.i + 1, {keepInst: true, noHash: true});
    else { AC.still = false; AC.done = true; renderBar(); playBtn(); }
    return;
  }
  CLK.on = !CLK.on; playBtn(); renderBar();
}
/* ---- presenting (the chip tour's): full screen where the frame allows it, else the stage fills the frame ---- */
const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement;
const fsOK = () => !!(document.fullscreenEnabled || document.webkitFullscreenEnabled);
let PRES = false, toastT = 0;
function toast(html, ms) { const t = $('toast'); t.innerHTML = html; t.hidden = false; clearTimeout(toastT); if (ms) toastT = setTimeout(() => { t.hidden = true; }, ms); }
const hideToast = () => { $('toast').hidden = true; };
function present() {
  if (fsEl()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
  if (PRES) { setPres(false); return; }
  const st = $('stage'), r = st.requestFullscreen || st.webkitRequestFullscreen;
  if (fsOK() && r) {
    let p = null; try { p = r.call(st); } catch (_) { p = null; }
    if (p && p.then) p.then(() => {}, () => setPres(true, true));
    else setTimeout(() => { if (!fsEl()) setPres(true, true); }, 300);
    return;
  }
  setPres(true, true);
}
function setPres(on, blocked) {
  PRES = on; document.documentElement.classList.toggle('et-pres', on); $('stage').classList.toggle('pres', on);
  fsLabel(); kbdHint();
  if (on && blocked) toast(`<p><b>Presenting inside the page's frame.</b> The frame does not allow full screen here.</p>`
    + `<p>For the whole screen, press <kbd>F11</kbd> (on a Mac <kbd>Ctrl</kbd>+<kbd>⌘</kbd>+<kbd>F</kbd>), or open the page in a window of its own, where <kbd>F</kbd> goes full screen. <kbd>Esc</kbd> or <kbd>F</kbd> leaves.</p>`
    + `<div class="tb"><button type="button" class="st-btn primary" data-t="win">Open a presenter window</button><button type="button" class="st-btn" data-t="ok">Stay in the frame</button></div>`, 14000);
  else hideToast();
  setTimeout(() => { fitCap(); }, 80);
}
const fsLabel = () => { $('btn-fs').textContent = (fsEl() || PRES) ? 'Exit' : 'Present'; presentClass(); setTimeout(fitCap, 80); };
document.addEventListener('fullscreenchange', fsLabel); document.addEventListener('webkitfullscreenchange', fsLabel);
function presenterWindow() {
  let w = null;
  try { w = window.open('', 'etsoc1_memlevels_presenter', `popup=yes,width=${screen.availWidth || 1280},height=${screen.availHeight || 800}`); } catch (_) { w = null; }
  if (!w) { toast('<p>The browser blocked the new window: allow pop-ups for this page, or press <kbd>F11</kbd>.</p>', 9000); return; }
  const put = html => {
    try { w.document.open(); w.document.write(html.replace(/<head([^>]*)>/i, '<head$1><script>window.__ET_PRESENTER=1<\/script>')); w.document.close(); try { w.focus(); } catch (_) { /* refused */ } return true; }
    catch (_) { return false; }
  };
  const fallback = () => { if (!put(SRC_HTML)) { try { w.location.href = location.href; } catch (_) { /* nothing more */ } } };
  if (/^https?:$/.test(location.protocol) && window.fetch) fetch(location.href, {credentials: 'same-origin'}).then(r => r.ok ? r.text() : Promise.reject(new Error('status ' + r.status))).then(h => { if (!/id="stage"/.test(h) || !put(h)) fallback(); }, fallback);
  else fallback();
  setPres(false);
  toast('<p>The presenter window is open: press <kbd>F</kbd> there for full screen.</p>', 7000);
}
$('toast').addEventListener('click', e => { const b = e.target.closest('button[data-t]'); if (!b) return; if (b.dataset.t === 'win') presenterWindow(); else hideToast(); });
const FRAMED = (() => { try { return window.self !== window.top; } catch (_) { return true; } })();
function kbdHint() { const h = $('kbd-hint'); if (h) h.hidden = TOUCHSCR || !FRAMED || document.hasFocus() || PRES || !!fsEl(); }
if (FRAMED) {
  window.addEventListener('focus', kbdHint); window.addEventListener('blur', kbdHint);
  $('kbd-hint').addEventListener('click', () => { window.focus(); kbdHint(); });
  kbdHint(); setTimeout(kbdHint, 400);
}
document.querySelectorAll('.skip a').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  const t = $(a.getAttribute('href').slice(1)); if (!t) return;
  const f = t.matches('button, [tabindex]') ? t : [...t.querySelectorAll('button:not(:disabled), a, [tabindex]')][0];
  if (f) f.focus({preventScroll: true});
}));
function togglePanel(show) {
  const st = $('stage'), hide = show === undefined ? !st.classList.contains('nopanel') : !show;
  st.classList.toggle('nopanel', hide); $('btn-panel').setAttribute('aria-pressed', String(!hide));
  setTimeout(fitCap, 60);
}
function setTheme(t) { if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }
function toggleTheme() {
  const cur = document.documentElement.dataset.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  setTheme(cur === 'dark' ? 'light' : 'dark');
}
function next(whole) {
  if (TOUR) {
    const it = TOUR.list[TOUR.i];
    if (!whole && it.s.access && AC.k === it.s.access && goStep(AC.i + 1)) return;
    if (TOUR.i >= TOUR.list.length - 1) return;
    tourGo(TOUR.i + 1); return;
  }
  if (AC.k) { if (!goStep(AC.i + 1) && AC.done) { const st = stepsOf(AC.k)[AC.i]; if (st.handoff) ACTS.handoff(); } return; }
  const k = SC().lastAcc || (SC().accOrder[0] || [])[0]; if (k) startAccess(k, 0);
}
function prev(whole) {
  if (TOUR) {
    const it = TOUR.list[TOUR.i];
    if (!whole && it.s.access && AC.k === it.s.access && goStep(AC.i - 1)) return;
    if (TOUR.i > 0) tourGo(TOUR.i - 1, {back: !whole});
    return;
  }
  if (AC.k) { goStep(AC.i - 1); return; }
  const k = SC().lastAcc; if (k) startAccess(k, stepsOf(k).length - 1, {still: true, done: true});
}
function back() {
  if (PRES) { setPres(false); return; }
  if (TOUR || fsEl()) return;
  if (AC.k) { stopAccess(); return; }
  if (zNow().length > 1) zoomBy(-1);
}
const ACTS = {
  zoom: b => {
    const to = b.dataset.to, inst = SC().inst; let changed = false;
    Object.keys(b.dataset).forEach(k => { if (k !== 'act' && k !== 'to' && inst[k] !== +b.dataset[k]) { inst[k] = +b.dataset[k]; changed = true; } });
    if (changed) rebuildPath();
    userNav(pathTo(to));
  },
  level: b => setLevel(b.dataset.lv),
  handoff: () => {
    if (!AC.k) return;
    const h = stepsOf(AC.k)[AC.i].handoff; if (!h) return;
    const k = h.k; setLevel(h.lv).then(() => { if (k && SC().access[k]) startAccess(k, h.at || 0); });
  },
  newpa: () => {
    if (SC().newAddr) SC().newAddr(); else ADDR.pa = mkPA(Math.floor(Math.random() * 32), Math.floor(Math.random() * 2 ** 20)) + D.addr.offset;
    const k = AC.k; SC().setInst(); if (!ZW) rebuildPath(); addrUI();
    if (k) startAccess(k, 0, {keepInst: true});
  },
  // the requester (L3, scratchpad, DRAM): a shire's details panel moves it; the drawing and a running access follow
  req: b => {
    const id = +b.dataset.id; ['l3', 'scp'].forEach(lv => { SCENES[lv].req = id; });
    const k = AC.k; SC().setInst(); if (!ZW) rebuildPath(); addrUI();
    if (k) startAccess(k, AC.i, {keepInst: true, still: AC.still || !CLK.on}); else showPart(SEL && SEL._key || 'overview', SEL && SEL._ctx);
    toast(`<p>The requester is now shire ${id}.</p>`, 2500);
  },
  // the L3's zero-line toggle: with it on, a load's data phase skips the data macros (the zero bit)
  zero: b => {
    SCENES.l3.zero = !SCENES.l3.zero; b.setAttribute('aria-pressed', String(SCENES.l3.zero));
    toast(`<p>Zero line ${SCENES.l3.zero ? 'on: the example line is all zeros, so its data macros are skipped' : 'off'}.</p>`, 3000);
    if (AC.k && Z.lv === 'l3') restartStep();
  },
  // a narrow window: the drawing keeps a readable size, scrolling sideways from its left edge; Fit fits it to the width
  fit: b => { const w = $('svgwrap'), on = !w.classList.contains('fitted'); w.classList.toggle('fitted', on); w.scrollLeft = 0; b.setAttribute('aria-pressed', String(on)); },
};
document.querySelectorAll('#btn-play').forEach(b => b.addEventListener('click', playPause));
$('btn-tour').addEventListener('click', e => toggleTour(e.shiftKey));
$('btn-fs').addEventListener('click', present);
$('btn-panel').addEventListener('click', () => togglePanel());
$('btn-next').addEventListener('click', () => next(false));
$('btn-prev').addEventListener('click', () => prev(false));
$('btn-follow').addEventListener('click', () => setFollow(!FOLLOW));
$('btn-dive').addEventListener('click', () => setDive(!DIVE));
PIP.el.addEventListener('click', () => zoomBy(-1));
PIP.el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); zoomBy(-1); } });
$('stage').addEventListener('click', e => { const b = e.target.closest && e.target.closest('button, summary, li.fact'); if (b && e.detail > 0) b.blur(); });
const inMid = el => { const r = el.getBoundingClientRect(); return r.bottom > window.innerHeight * 0.4 && r.top < window.innerHeight * 0.6; };
const stageInView = () => window.matchMedia('(max-width: 899px)').matches ? inMid($('svgwrap')) || inMid($('bar')) : inMid($('stage'));
let SPACE_EATEN = false;
document.addEventListener('keyup', e => { if ((e.key === ' ' || e.key === 'Spacebar') && SPACE_EATEN) { e.preventDefault(); SPACE_EATEN = false; } }, true);
document.addEventListener('keydown', e => {
  if (e.key !== 'Tab') hideTip();
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  const tg = e.target, tag = (tg.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
  const inView = !!fsEl() || PRES || stageInView();
  const inStage = inView && ($('stage').contains(tg) || tg === document.body || tg === document.documentElement);
  if (!inStage) return;
  if (tg.closest && tg.closest('#tabs') && /^(ArrowLeft|ArrowRight|Home|End)$/.test(e.key)) return;   // the tab list's own keys
  const onControl = tg.closest && tg.closest('button, a, li.fact, summary, [role="button"]:not(.comp)');
  switch (e.key) {
    case 'ArrowRight': case 'PageDown': e.preventDefault(); next(e.shiftKey); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); prev(e.shiftKey); break;
    case ' ': case 'Spacebar': {
      const ab = tg.closest && tg.closest('[data-acc]');
      const pause = (ab && AC.k && ab.dataset.acc === AC.k) || (tg.closest && tg.closest('.stg')) || (accOn() && tg.closest && tg.closest('#pn-body summary, #pn-body li.fact'));
      if (onControl && !pause) return;
      e.preventDefault(); SPACE_EATEN = true; playPause(); break;
    }
    case 'f': case 'F': e.preventDefault(); present(); break;
    case 'p': case 'P': e.preventDefault(); togglePanel(); break;
    case 'd': case 'D': e.preventDefault(); toggleTheme(); break;
    case 'c': case 'C': e.preventDefault(); setFollow(!FOLLOW); break;
    case 'v': case 'V': e.preventDefault(); setDive(!DIVE); break;
    case 't': case 'T': e.preventDefault(); toggleTour(e.shiftKey); break;
    case 'q': case 'Q': if (TOUR) { e.preventDefault(); endTour(); stopAccess(); } break;
    case '[': e.preventDefault(); stepAccess(-1); break;
    case ']': e.preventDefault(); stepAccess(1); break;
    case '+': case '=': e.preventDefault(); zoomBy(1); break;
    case '-': case '_': e.preventDefault(); zoomBy(-1); break;
    case 'Escape': back(); break;
    case 'Backspace': if (zNow().length > 1) { e.preventDefault(); zoomBy(-1); } break;
    case 'Home': if (AC.k) { e.preventDefault(); goStep(0); } else if (TOUR) { e.preventDefault(); tourGo(0); } break;
    case 'End': if (AC.k) { e.preventDefault(); goStep(stepsOf(AC.k).length - 1); } break;
    default: {
      const i = '12345'.indexOf(e.key);
      if (i >= 0 && e.key.length === 1) {
        e.preventDefault();
        if (TOUR && TOUR.all) { const j = TOUR.list.findIndex(it => it.lv === LEVELS[i]); if (j >= 0) { tourGo(j); break; } }
        setLevel(LEVELS[i]);
      }
    }
  }
});

/* ---- the ladder: every level's latency and energy per byte, on log scales, this level lit ---- */
function ladderHtml(lv) {
  const L0 = [['l1', 'L1', 'l1_lat'], ['l2', 'L2', 'l2_lat'], ['scp', 'scratchpad', 'lad_scp_lat'], ['l3', 'L3', 'lad_l3'], ['dram', 'DRAM', 'lad_dram']].map(r => r.concat([V(r[2])]));
  const E0 = [['l1', 'L1', () => n('l1_e_pjb'), V('l1_e_pjb')], ['l2', 'L2', () => n('l2_e'), V('l2_e')], ['scp', 'scratchpad', () => `${n('lad_e_scp')}–${n('lad_e_scp1')} pJ/B`, V('lad_e_scp1')], ['l3', 'L3', () => `${n('lad_e_l3')}/B`, V('lad_e_l3')], ['dram', 'DRAM', () => `${n('lad_e_dram')}/B`, V('lad_e_dram')]];
  const wl = v => (100 * Math.log10(v) / Math.log10(360)).toFixed(1), we = v => (100 * (Math.log10(v) - Math.log10(0.3)) / (Math.log10(150) - Math.log10(0.3))).toFixed(1);
  const row = (k, nm, html, w) => `<div class="nm${k === lv ? ' cur' : ''}">${esc(nm)}</div><div class="tr${k === lv ? ' cur' : ''}"><u style="width:${w}%"></u><s>${html}</s></div>`;
  return `<p class="pn-h">Every level, on log scales</p><p class="lad-h">latency, minion cycles</p><div class="lad">`
    + L0.map(([k, nm, key, v]) => row(k, nm, n(key), wl(v))).join('') + `</div><p class="lad-h">energy to read a byte, above idle</p><div class="lad">`
    + E0.map(([k, nm, f, v]) => row(k, nm, f(), we(v))).join('') + '</div>';
}

/* ================= the text below the stage ================= */
const fl = (key, txt) => { const f = F[key]; return f ? `<a href="#facts" class="num" data-f="${key}">${esc(txt || f.id)}</a>` : esc(key); };
const kd = key => F[key] ? kindChip(F[key]) : '';
function prose() {
  // SRAM or not: what each level is built from (DESIGN.md §1.4)
  const R = [
    ['L1 data array', 'latch RAM', `"4 LRAM (Latch-RAM) blocks of 128 rows and 64 bits per row", in the design document and the public datasheet`, 'l1:l1.lram'],
    ['L1 tags and TLB', 'latch register files', 'the four way tag files and the 8-entry TLB are latch register files', 'l1:l1.metadata l1:l1.tlb'],
    ['L1 valid and LRU bits', 'flip-flops', '64 valid bits and a 4 × 4 LRU matrix per set', 'l1:l1.metadata l1:l1.lru'],
    ['Neighbourhood instruction-cache data', 'a compiled macro of the data panels\' family (saduls, 1PUHD), in the HV region; the bitcell unknown', 'the spec lists it beside the data panels, which it calls "SRAM memory panels", and the PRM calls the family SRAMs; moved out of the minions\' low-voltage region because "the memory cells used to implement the ICache data RAMs need to be placed in an HV region"', 'l1:l1.icache-sram l1:l1.lv-region'],
    ['Shire cache: L2, L3, scratchpad', '"SRAM memory panels" (the spec); the bitcell unknown', 'compiled macros named as 1PUHD and 2PUHDRF types; the datasheet counts 140 MB of on-die SRAM; no source gives the cell', 'l2:l2.macro.data l3:l3.macros scp:scp.panel l2:l2.sc.chip-total l2:l2.storage-question'],
    ['DRAM', 'LPDDR4X (a Micron part); the cell is the textbook 1T1C', '32 GB on the V3 cards; a DRAM bit is an access transistor and a capacitor, which leaks and is refreshed', 'dram:dram.org.capacity dram:gen.cell'],
  ];
  $('sram-text').innerHTML = `<p>What each level is built from, answered from the documents where they answer it. The lab lead said the chip is "not using SRAM"; the remark, relayed by the page's author, is not recorded in the repository, so this page quotes it as relayed. The documents agree for the L1 and disagree for the shire cache:</p>`
    + `<div class="table-wrap"><table id="sramtab" class="stack"><thead><tr><th>Level</th><th>Storage</th><th>What the sources say</th><th>Kind</th><th>Facts</th></tr></thead><tbody>`
    + R.map(([lv, st, what, keys]) => { const ks = keys.split(' '); return `<tr><td data-label="Level"><b>${esc(lv)}</b></td><td data-label="Storage">${esc(st)}</td><td data-label="What the sources say">${esc(what)}</td><td data-label="Kind">${[...new Set(ks.map(k => F[k] && F[k].kind))].map(k => `<span class="kd ${k}">${KLAB[k]}</span>`).join(' ')}</td><td data-label="Facts" class="small">${ks.map(k => fl(k)).join(', ')}</td></tr>`; }).join('')
    + '</tbody></table></div>'
    + `<p><b>Why the L1 is not built from those panels (our reading).</b> The neighbourhood document says that ${src('"the memory cells used to implement the ICache data RAMs need to be placed in an HV region"', 'l1:l1.lv-region')}; it says nothing of the data cache, and applying it to the shire cache's panels is our inference. A voltage argument is consistent with it, though it concerns these macros' listed minimum voltages only and proves nothing: the data panel's lowest listed Vmin is ${n('scp_vmin')} at trim RM0 (${n('l2_vmin_st')} for the tag-state RAM), while the firmware keeps the minion rail within ${n('l1_vlim')} and it measures ${n('l1_v')} at 600 MHz; only near the top of that range (${n('l1_v800')}) would it clear the panels' Vmin. Latches are ordinary logic and run wherever logic does. The documents never state this reason: it is derived here (${fl('l1:l1.why-latch')}) and asked (${hubLink('ask-not-sram')}).</p>`
    + `<p><b>The contradiction.</b> The Shire Cache Specification calls the L2, L3 and scratchpad arrays "SRAM memory panels" and names compiled macros; the datasheet counts 140 MB of SRAM; the Programmer's Reference Manual calls the same macro families SRAMs. Against that, the lab lead's remark. It may mean the L1 and the register files, which are latches; it may mean the shire cache's cell is something else. The diagrams draw the shire cache's cell as a generic 6T SRAM cell with an unknown badge until the team says which.</p>`;
  // one load, level by level: the text version of the diagrams
  $('summary-text').innerHTML = `<p>Every access of every level, step by step, with the numbers the sources give. The same text is in the details panel as each step plays.</p>`
    + LEVELS.map(lv => {
      const sc = SCENES[lv];
      return `<details class="more"${lv === 'l1' ? ' open' : ''}><summary>${esc(sc.title)} <span class="more-hint">· ${sc.accOrder.length} accesses</span></summary><p>${sc.head()}.</p>`
        + sc.accOrder.map(([k, lg]) => { const d = DSTEPS[lv][k]; return `<p><b>${esc(lg)}.</b>${d.measured ? ' ' + esc(d.measured) + '.' : ''}</p><ol>${d.steps.map(s => `<li><b>${esc(s.block)}</b>: ${esc(s.action)}${s.latency ? ` <span class="small">(${esc(s.latency)})</span>` : ''}${s.energy ? ` <span class="small">(${esc(s.energy)})</span>` : ''}</li>`).join('')}</ol>`; }).join('')
        + '</details>';
    }).join('');
  // what is documented, what is generic, what is unknown
  const cnt = D.meta.counts, KS = ['spec', 'measured', 'derived', 'generic', 'unknown'];
  const tot = k => LEVELS.reduce((s, lv) => s + (cnt[lv][k] || 0), 0);
  $('honest-text').innerHTML = `<p>The page rests on ${Object.keys(F).filter(k => F[k].level !== 'chip').length} facts over the five levels, and on ${Object.keys(F).filter(k => F[k].level === 'chip').length} of the chip tour's (the measured map of the mesh, the memory shires' places, the routers), listed under "Chip tour". <b>Documented</b> for the ET-SoC-1 means specified (a manual, a design document, the RTL or the firmware), measured on the lab's cards, or derived from those; <b>generic</b> is a textbook circuit drawn as an illustration, never carrying an ET-looking number; <b>unknown</b> is a question for the team, each one in one ask below.</p>`
    + `<div class="table-wrap"><table class="stack"><thead><tr><th>Level</th>${KS.map(k => `<th class="num"><span class="kd ${k}">${KLAB[k]}</span></th>`).join('')}</tr></thead><tbody>`
    + LEVELS.map(lv => `<tr><td data-label="Level"><b>${esc(SCENES[lv].title)}</b></td>${KS.map(k => `<td class="num" data-label="${KLAB[k]}">${cnt[lv][k] || 0}</td>`).join('')}</tr>`).join('')
    + `<tr><td><b>all</b></td>${KS.map(k => `<td class="num" data-label="${KLAB[k]}"><b>${tot(k)}</b></td>`).join('')}</tr></tbody></table></div>`
    + `<p>Two markers qualify a documented fact: <i>re-implementation RTL</i> when its only source is Ainekko's re-implementation of the CORE-ET RTL (external/core-et-main, co-simulated against the original shire cache), and <i>spec v1.1</i> for the Shire Cache Specification in hand, from core-et's Erbium branch, which also documents later chips. Where the sources disagree:</p>`
    + `<div class="table-wrap"><table id="conftab" class="stack"><thead><tr><th>What</th><th>The sources</th><th>What the page does</th></tr></thead><tbody>`
    + D.conflicts.map(c => `<tr><td data-label="What"><b>${esc(c.what)}</b></td><td data-label="The sources">${c.sources.map(esc).join('<br>')}</td><td data-label="What the page does">${esc(c.resolution)}</td></tr>`).join('') + '</tbody></table></div>';
  // the asks
  $('asktab').querySelector('tbody').innerHTML = ASKS.map(a => `<tr id="q-${esc(a.id)}"><td data-label="Ask"><b>${esc(a.title)}</b><br><span class="small">${a.extends ? 'adds to an existing row' : RUNGS[a.id] && !RUNGS[a.id].proposed ? `a new row, rung ${RUNGS[a.id].rung}` : 'proposed new row'} · ${a.levels.map(l => LVNAME[l]).join(', ')}</span></td><td data-label="What is unknown" class="small">${esc(a.question)}</td><td data-label="What would settle it" class="small">${esc(a.settles)}</td><td data-label="Unknown facts" class="small">${a.facts.map(k => fl(k, `${LVNAME[F[k].level]} ${F[k].id}`)).join(', ')}</td><td data-label="On the hub">${askLinks(a).join('<br>')}</td></tr>`).join('');
  // every fact
  $('facttab').querySelector('tbody').innerHTML = Object.keys(F).map(key => { const f = F[key];
    return `<tr><td data-label="Level">${esc(LVNAME[f.level])}</td><td data-label="Fact"><code>${esc(f.id)}</code></td><td data-label="Statement">${esc(f.statement)}${f.url ? ` <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)}</a>` : ''}${cardsTxt(f) ? ` <span class="small">(${esc(cardsTxt(f))})</span>` : ''}</td><td data-label="Kind">${kindChip(f)}</td><td data-label="Source" class="small">${esc(f.source)}</td></tr>`; }).join('');
  CK.sortTable('facttab', {filter: true, filterLabel: 'Filter facts'});
  // sources
  $('sources-text').innerHTML = `<ul>`
    + `<li><b>The manuals</b> (external/et-man, read with pdftotext; pages are PDF pages): the ET Preliminary Datasheet Rev 1.0, the Programmer's Reference Manual, the Minion Overview, the ET-SoC Errata and the ET-PCIe-Dev-Card-V3.</li>`
    + `<li><b>The micro-architecture documents</b> (external/core-et/docs, the Erbium branch): the Minion DCache Description, the Minion Description, FE-Intpipe, the CORE-ET Neighborhood MAS, the Minion Shire Description, the Shire Cache Specification v1.1 and the ET-Link Specification.</li>`
    + `<li><b>The RTL</b>: external/core-et/rtl (the Erbium branch; the latch register-file library, the D-cache, the behavioural LRAM macro) and external/core-et-main (Ainekko's re-implementation, co-simulated against the original shire cache; facts from it only are marked).</li>`
    + `<li><b>The firmware and runtime</b>: external/et-platform (the memory-controller and shire-cache ESR code, the emulator's reset values).</li>`
    + `<li><b>The measurements</b>: this repository's data, cited per fact (the version-3 latency results on three cards, the energy manual, the power telemetry).</li>`
    + `<li><b>The page's data</b>: docs/reports/data/2026-09-28-memory-levels (build_facts.py merges the five levels' research files in research/ and refuses to build if a printed number has no source, a reference is missing or an unknown has no ask). ${Object.keys(F).length} facts, ${Object.keys(N).length} printed numbers.</li>`
    + `<li><b>The chip-scale views</b> of the L3, the scratchpad and the DRAM draw the chip tour's layout (docs/reports/data/2026-09-27-chip-diagram/facts.json, <code>layout</code>): the logical 6 × 6 map measured by latency on three cards, with the memory shires where a DRAM-latency fit puts them. The die is this map turned a quarter; the chip tour draws the die view.</li>`
    + `<li><b>The engine</b> is the chip tour's (docs/reports/sources/chip-diagram.script.js), copied on 27 September 2026 and generalised to a tree of scales.</li></ul>`;
}

/* ================= start ================= */
LEVELS.forEach(lv => SCENES[lv].setInst());
// the page's gutters in a frame (CSS html.et-framed: spacesheep's comment tab covers the frame's left edge on a phone);
// a touch screen that cannot go full screen offers no Present button
if (FRAMED) document.documentElement.classList.add('et-framed');
// (the portrait window's class follows the window: a phone turned)
const phClass = () => $('stage').classList.toggle('ph', mqOn(PHQ));
phClass(); try { matchMedia(PHQ).addEventListener('change', phClass); } catch (_) { /* an old browser: as loaded */ }
if (TOUCHSCR) { $('stage').classList.add('touch'); if (!fsOK()) $('stage').classList.add('nofs'); }
prose();
(async () => {
  let q = null; try { q = new URLSearchParams(location.search); } catch (_) { /* no URL flags */ }
  if (q) { setTheme(q.get('theme')); if (q.get('panel') === 'off') togglePanel(false); if (q.get('dive') === 'on') setDive(true); }
  const h = location.hash;
  let done = false;
  if (h && parseHash(h)) { try { done = await applyHash(h, {scroll: true}); } catch (e) { console.error(e); } }
  // a hash that names a section of the page (#asks, #facts, from another page) is kept and scrolled to; one that names
  // neither a view nor a section is replaced
  let sec = null;
  if (!done && h.length > 1) { try { sec = document.getElementById(decodeURIComponent(h.slice(1))); } catch (_) { /* a malformed hash */ } }
  if (!done) await setLevel('l1', {noHash: !h || h === '#' || !!sec, force: true});
  if (sec) { try { sec.scrollIntoView({block: 'start'}); } catch (_) { /* no layout */ } }
  if (q && q.get('tour')) { const all = q.get('tour') === 'all', lst = tourList(all); startTour(all, Math.max(0, lst.findIndex(it => it.lv === Z.lv))); }
  if (window.__ET_PRESENTER) setTimeout(() => toast('<p><b>Presenter window.</b> Press <kbd>F</kbd> for full screen; <kbd>T</kbd> starts the tour.</p>', 9000), 300);
  fitCap();
})();
/* a read-only view of the state, for the page's tests (headless Chrome) */
window.__memState = () => ({lv: Z.lv, path: Z.path.slice(), acc: AC.k, step: AC.i, done: AC.done, still: AC.still, clockOn: CLK.on,
  follow: FOLLOW, dive: DIVE, zooming: ZW, tour: TOUR ? TOUR.i : null, pip: !PIP.el.hidden, hash: location.hash});
})();
