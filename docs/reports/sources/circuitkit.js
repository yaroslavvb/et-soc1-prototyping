/* ================= circuitkit.js: the memory levels' drawings, for the chip diagram's deep zoom =================
   Written by docs/reports/data/2026-09-27-chip-diagram/research/make_circuitkit.py (do not edit by hand: edit the
   memory levels' page or the head and tail beside the script, and run it again). The chip page's script includes this
   file with an include line (the build-report.py directive @include, in a comment), which scripts/build-report.py
   expands.
   Copied on 30 September 2026 from docs/reports/sources/memory-levels.script.js, each declaration with the lines it
   came from: the drawing kit, the shared circuit drawings (generic textbook circuits tied to ET facts by counts and
   names), the example address, the scenes of the L1, shire-cache, mesh and DRAM chains, and the texts of their parts.
   One closure keeps the copies' names (comp, part, boxShape, frame, T, n ...) apart from the chip page's. ENV gives
   them what they used on their own page: the SVG primitives, that page's numbers (D.mlnum) and facts (the chip page's
   build imports exactly those cited, as ml:<level>:<id>; a data-f here gets the prefix, so every source tooltip finds
   its fact), its example address (D.mladdr), and the chip's layout. The accesses (lit paths, mos(), callouts,
   waveforms) are not copied: here the drawings stand still. */
const CKT = (ENV => {
  const {E, S, esc, CK} = ENV;
  const D = {addr: ENV.addr, layout: ENV.layout};
  const N = ENV.num;
  const fnum = (v, dp) => CK.fmt.num(v, dp);
  const disp = t => String(t).replace(/(\d)x(?=$|[\s,;.)])/g, '$1×').replace(/(\d) x (\d)/g, '$1 × $2');
  // a memory-levels fact id gets its ml: prefix; the chip page's own ids (in.*, chip facts) pass as they are
  const pre = fids => String(fids || '').split(/\s+/).filter(Boolean).map(f => (/^(l1|l2|l3|scp|dram|g):/.test(f) ? 'ml:' + f : f)).join(' ');
  const V = k => { if (!N[k]) throw new Error('no number ' + k); return N[k].v; };
  function n(k, unit) {
    const x = N[k]; if (!x) { console.error('no memory-levels number ' + k); return '?'; }
    return `<span class="num" data-f="${x.f}">${esc(disp(x.t))}${unit ? ' ' + esc(unit) : ''}</span>`;
  }
  const nt = k => { const x = N[k]; if (!x) { console.error('no memory-levels number ' + k); return '?'; } return disp(x.t); };
  const nf = k => (N[k] ? N[k].f : '');
  const cn = (v, fids, dp, unit) => `<span class="num" data-f="${pre(fids)}">${typeof v === 'number' ? fnum(v, dp) : esc(v)}${unit ? ' ' + unit : ''}</span>`;
  const src = (text, fids) => `<span class="num" data-f="${pre(fids)}">${text}</span>`;
  function T(parent, x, y, str, cls, anchor, fids) {
    const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
    t.textContent = str; if (fids) t.setAttribute('data-f', pre(fids));
    return t;
  }
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const kpi = (html, lab) => `<div class="pn-kpi"><b>${html}</b><span>${lab}</span></div>`;
  const K = (k, lab) => kpi(n(k), lab);
  const ladderHtml = () => '';
  // the DRAM level's instance, which some of its parts' texts read (here, the memory levels' example address)
  const I5 = () => Object.assign({}, INST.dram(), {req: 0});
  const FR = {x: -172, y: -74, w: 1264, h: 774};   // every copied scale is drawn in this frame
  let SUBLH = 21;   // the pitch of the lines under a part's title (build sets it)
  let BAP = null;   // the anchor points of the layer being built
  /* getBBox needs the layer rendered: a hidden layer is shown, invisible, while it is measured */
  function measured(L, fn) {
    const d0 = L.style.display, v0 = L.style.visibility;
    if (d0 === 'none') { L.style.visibility = 'hidden'; L.style.display = ''; }
    try { fn(); } finally { if (d0 === 'none') { L.style.display = d0; L.style.visibility = v0; } }
  }
  /* the badges of a part: [['documented', 'structure'], ['generic', 'circuit'], ['unknown', 'the macro inside']] */
  // (the chip page's copy: a caveat that only repeats the badge's word, "spec spec", is left out; review of 1 Oct)
  const badges = list => list.map(([k, t]) => { const w = k === 'unknown' ? 'unknown · asked' : k; return `<span class="kd ${k === 'documented' ? 'spec' : k}">${esc(w)}</span>${t && t !== w ? ` <span class="cav">${esc(t)}</span>` : ''}`; }).join(' ');

/* ---- the drawing kit ---- */
// kickAs: memory-levels.script.js at 290cb9c, lines 3862-3862
const kickAs = (fn, kick, facts) => ctx => Object.assign({}, fn(ctx), {kick}, facts ? {facts} : {});
// KB_CLS: memory-levels.script.js at 290cb9c, lines 303-306
/* Every label knocks out what runs under it (a trail, a lit ring, a wire, a rail band's tint) in the colour of what
   it sits on, so it reads cleanly; where nothing runs under it the knockout is invisible (CSS: #mem .lay text). A part
   sets that colour for its labels (boxShape, --kb); a label on an opaque shape (a gate, a card) takes the shape's */
const KB_CLS = {gate: 'var(--surface)', ch: 'var(--surface)', bub: 'var(--surface)', 'co-box': 'var(--surface)'};
// COL: memory-levels.script.js at 290cb9c, lines 1170-1172
/* Roles (DESIGN.md §3): logic --c1, storage --c3, interconnect --c4, crossings --c5; --c2 is kept for what is active.
   One stroke scale: components 2, frames 2.5, sub-structure 1.25, moving trails 6, transistors 2 (lit 3.5). */
const COL = {logic: 'var(--c1)', store: 'var(--c3)', net: 'var(--c4)', xing: 'var(--c5)', aux: 'var(--c7)', ink: 'var(--ink-2)'};
// DASH: memory-levels.script.js at 290cb9c, lines 1180-1181
/* a part's outline: solid when documented, dotted when generic, dashed when unknown (DESIGN.md §3) */
const DASH = {generic: '2 5', unknown: '8 6'};
// BAND_FILL: memory-levels.script.js at 290cb9c, lines 104-109
/* the rail bands: a light tint and a text label; the label, not the colour, names the band (DESIGN.md §3). Tints in
   hues the part colours do not use, since 28 Sep: the earlier stripes and dots behind the labels made text hard to read.
   The keys keep their old pattern names ('pat-…'): data-band on each tinted shape tells the legend which bands a view has. */
const BAND_FILL = {'pat-lv': 'color-mix(in srgb, var(--c7) 9%, transparent)', 'pat-hv': 'color-mix(in srgb, var(--ref) 12%, transparent)',
  'pat-mesh': 'color-mix(in srgb, var(--c4) 10%, transparent)', 'pat-ddr': 'color-mix(in srgb, var(--c5) 8%, transparent)',
  'pat-hatch': 'color-mix(in srgb, var(--ink-2) 13%, transparent)'};
// FS_BASE: memory-levels.script.js at 290cb9c, lines 327-327
const FS_BASE = {'t-sm': 17, 't-smb': 17, 't-mono': 17, 't-lab': 20, 't-labb': 20, 't-net': 19, 't-mid': 24, 't-big': 30};
// comp: memory-levels.script.js at 290cb9c, lines 1174-1179
function comp(parent, key, ctx, label) {
  const g = E('g', {class: 'comp dimmable', tabindex: 0, role: 'button', 'aria-label': label, 'data-comp': key}, parent);
  g._key = key; g._ctx = ctx || {};
  if (BAP) (BAP.parts[key] = BAP.parts[key] || []).push(g);
  return g;
}
// boxShape: memory-levels.script.js at 290cb9c, lines 1182-1192
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
// part: memory-levels.script.js at 290cb9c, lines 1193-1208
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
  // (o.lh: a line pitch for the lines under the title, else 21; the chip diagram's blocks give theirs, and since the
  // code review of 1 Oct this kit, drawing them for the shared ladder here, keeps it as the chip's copy does)
  const lh = o.lh || Math.max(21, SUBLH);
  (o.sub || []).forEach((s, i) => { const L0 = typeof s === 'string' ? {t: s} : s; T(g, o.center ? x + w / 2 : x + 12, y + ty + 23 + i * lh, L0.t, L0.c || 't-sm', o.center ? 'middle' : 'start', L0.f); });
  return g;
}
// tagPill: memory-levels.script.js at 290cb9c, lines 1209-1215
/* the corner tags of a frame, right-aligned on the title's line: [{kind, text}] */
function tagPill(parent, xr, y, kind, text) {
  const w = Math.round(text.length * 9.4 + 26), g = E('g', {class: 'tg ' + kind}, parent);
  E('rect', {x: xr - w, y, width: w, height: 26, rx: 13}, g);
  T(g, xr - w / 2, y + 18.5, text, '', 'middle');
  return w;
}
// frame: memory-levels.script.js at 290cb9c, lines 1216-1225
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
// railBand: memory-levels.script.js at 290cb9c, lines 1226-1232
/* a rail band: a pattern and a label (DESIGN.md §3) */
function railBand(parent, x, y, w, h, pat, label, key, fids) {
  const g = key ? comp(parent, key, {}, label + ': details') : E('g', {}, parent);
  S(E('rect', {class: 'shape', x, y, width: w, height: h, rx: 10, 'data-band': pat}, g), {fill: BAND_FILL[pat], stroke: 'var(--ink-2)', strokeOpacity: 0.35, strokeWidth: 1.25, strokeDasharray: '4 6'});
  if (key) { E('rect', {class: 'ring', x: x - 5, y: y - 5, width: w + 10, height: h + 10, rx: 14}, g); g._box = {x, y, w, h}; }
  return g;
}
// wire: memory-levels.script.js at 290cb9c, lines 1233-1233
const wire = (parent, P, cls) => E('path', {class: 'w' + (cls ? ' ' + cls : ''), d: 'M' + P.map(p => `${p[0]},${p[1]}`).join(' L')}, parent);
// jn: memory-levels.script.js at 290cb9c, lines 1234-1234
const jn = (parent, x, y) => E('circle', {class: 'jn', cx: x, cy: y, r: 4}, parent);
// netLab: memory-levels.script.js at 290cb9c, lines 1235-1235
function netLab(parent, x, y, t, anchor, fids) { return T(parent, x, y, t, 't-net halo', anchor || 'start', fids); }
// rail: memory-levels.script.js at 290cb9c, lines 1236-1239
function rail(parent, x1, x2, y, lab, anchor) {
  E('line', {class: 'rail', x1, y1: y, x2, y2: y}, parent);
  if (lab) netLab(parent, anchor === 'end' ? x1 - 8 : x2 + 8, y + 6, lab, anchor === 'end' ? 'end' : 'start');
}
// gnd: memory-levels.script.js at 290cb9c, lines 1240-1243
function gnd(parent, x, y) {
  E('line', {class: 'w', x1: x, y1: y - 10, x2: x, y2: y}, parent);
  [[14, 0], [9, 6], [4, 12]].forEach(([hw, dy]) => E('line', {class: 'rail', x1: x - hw, y1: y + dy, x2: x + hw, y2: y + dy}, parent));
}
// mosV: memory-levels.script.js at 290cb9c, lines 1244-1259
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
// mosH: memory-levels.script.js at 290cb9c, lines 1260-1273
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
// invSym: memory-levels.script.js at 290cb9c, lines 1274-1280
/* gate-level symbols, 2-unit strokes; each returns its pins */
function invSym(parent, x, y, o) {
  o = o || {}; const s = o.s || 22, f = o.left ? -1 : 1, g = E('g', {}, parent);
  E('path', {class: 'gate', d: `M${x - f * s},${y - s * 0.8} L${x + f * s * 0.7},${y} L${x - f * s},${y + s * 0.8} Z`}, g);
  E('circle', {class: 'gate', cx: x + f * (s * 0.7 + 5), cy: y, r: 5}, g);
  return {g, in: {x: x - f * s, y}, out: {x: x + f * (s * 0.7 + 10), y}, shape: g.firstChild};
}
// andSym: memory-levels.script.js at 290cb9c, lines 1281-1290
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
// mux2: memory-levels.script.js at 290cb9c, lines 1291-1295
function mux2(parent, x, y, o) {
  o = o || {}; const w = o.w || 26, h = o.h || 56, g = E('g', {}, parent);
  const sh = E('path', {class: 'gate', d: `M${x},${y - h / 2} L${x + w},${y - h / 2 + 10} L${x + w},${y + h / 2 - 10} L${x},${y + h / 2} Z`}, g);
  return {g, shape: sh, in0: {x, y: y - h / 4}, in1: {x, y: y + h / 4}, out: {x: x + w, y}, sel: {x: x + w / 2, y: y + h / 2 - 5}};
}
// flopSym: memory-levels.script.js at 290cb9c, lines 1296-1302
function flopSym(parent, x, y, w, h, lab, o) {
  o = o || {}; const g = E('g', {}, parent);
  E('rect', {class: 'gate', x, y, width: w, height: h, rx: 3}, g);
  E('path', {class: 'w', d: `M${x},${y + h - 16} L${x + 9},${y + h - 10} L${x},${y + h - 4}`}, g);
  if (lab) T(g, x + w / 2, y + h / 2 + 6, lab, o.cls || 't-sm', 'middle');
  return {g, shape: g.firstChild, d: {x, y: y + h / 3}, q: {x: x + w, y: y + h / 3}, ck: {x, y: y + h - 10}};
}
// icgSym: memory-levels.script.js at 290cb9c, lines 1303-1309
/* an integrated clock gate: a latch holding the enable, ANDed with the clock (drawn as a box with its two gates) */
function icgSym(parent, x, y, o) {
  o = o || {}; const g = E('g', {}, parent), w = o.w || 58, h = o.h || 40;
  E('rect', {class: 'gate', x, y, width: w, height: h, rx: 5}, g);
  T(g, x + w / 2, y + h / 2 + 6, 'ICG', 't-smb', 'middle');
  return {g, shape: g.firstChild, ck: {x, y: y + h * 0.3}, en: {x, y: y + h * 0.7}, out: {x: x + w, y: y + h / 2}, box: {x, y, w, h}};
}
// ringAll: memory-levels.script.js at 290cb9c, lines 268-278
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
// fitTexts: memory-levels.script.js at 290cb9c, lines 279-302
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
// kbTexts: memory-levels.script.js at 290cb9c, lines 307-326
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

/* ---- shared circuit drawings (generic textbook circuits; ET facts by counts and names) ---- */
// draw6T: memory-levels.script.js at 290cb9c, lines 1828-1850
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
// buildCell: memory-levels.script.js at 290cb9c, lines 1852-1937
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
  (o.note || []).forEach((t, i) => T(L, -150, 664 + i * Math.max(22, SUBLH), t, 't-sm', 'start', o.noteF));
  ap.gs = {pre: gp, wl: gw, cell: gc, mux: gm, wd: gd, sa: gs, olat: go, half: gh};
}
// buildPanel: memory-levels.script.js at 290cb9c, lines 2027-2109
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
// buildXing: memory-levels.script.js at 290cb9c, lines 2127-2182
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
// buildLatchCell: memory-levels.script.js at 290cb9c, lines 2203-2262
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
// drawReadTree: memory-levels.script.js at 290cb9c, lines 2302-2351
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
// buildComparator: memory-levels.script.js at 290cb9c, lines 2353-2385
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

/* ---- the example address and its decoders ---- */
// P40: memory-levels.script.js at 290cb9c, lines 2387-2388
/* ================= the example address (the chip tour's mkPA(13, 0x2468A), a DRAM-region line) ================= */
const P40 = 2 ** 32;
// ADDR: memory-levels.script.js at 290cb9c, lines 2389-2389
const ADDR = {pa: D.addr.line + D.addr.offset};
// bits: memory-levels.script.js at 290cb9c, lines 2390-2390
const bits = (pa, hi, lo) => Math.floor(pa / 2 ** lo) % 2 ** (hi - lo + 1);
// mkPA: memory-levels.script.js at 290cb9c, lines 2392-2392
function mkPA(home, salt) { return 0x80 * P40 + salt * 2048 + home * 64; }
// L1_HART: memory-levels.script.js at 290cb9c, lines 2393-2398
/* L1: set PA[9:6] in shared mode; in the firmware's split mode hart 0 has sets 12-13 and hart 1 sets 14-15 (PRM Table
   8.4, and the measured knee of 512 B per hart), so the issuing hart, not PA[7], picks the pair and PA[6] the set in it
   (the DCache Description §3.2.1 says only that both set MSBs are forced to 11: D.conflicts). The example's load is
   hart 0's. The row of the data array is {set, PA[5], way} (l1.lram-addr); block PA[4:3]. The way is an example: no
   address bit picks it. */
const L1_HART = 0;
// dec1: memory-levels.script.js at 290cb9c, lines 2399-2402
function dec1(pa) {
  const set = 12 | (L1_HART << 1) | bits(pa, 6, 6), half = bits(pa, 5, 5), block = bits(pa, 4, 3), way = D.addr.way_l1;
  return {s: bits(pa, 9, 6), set, hart: L1_HART, half, block, way, row: set * 8 + half * 4 + way};
}
// dec2: memory-levels.script.js at 290cb9c, lines 2403-2408
/* L2: bank PA[7:6], sub-bank PA[9:8], set PA[16:10] under M0's 7-bit mask, so rows 0x280-0x2FF (l2.decode,
   l2.partition.rows); a data row is {set, way} (the re-implementation's RTL; D.conflicts) */
function dec2(pa) {
  const bank = bits(pa, 7, 6), sub = bits(pa, 9, 8), lo = bits(pa, 16, 10), set = 0x280 + lo, way = D.addr.way_l2;
  return {bank, sub, lo, set, way, row: set * 4 + way};
}
// hex3: memory-levels.script.js at 290cb9c, lines 2409-2409
const hex3 = v => '0x' + v.toString(16).toUpperCase().padStart(3, '0');
// dec5: memory-levels.script.js at 290cb9c, lines 4827-4832
/* The map (dram.addr.*): memory shire PA[8:6], channel (controller) PA[9], then PA[9:6] stripped; inside a channel
   bank PA[12:10], row PA[34:18], column PA[17:13] and PA[5:1] (a 2 KB page of 1,024 16-bit columns); a 64-byte line is
   two BL16 bursts from one row, PA[5] picking the half. Measured by one-bit flips on three cards. */
function dec5(pa) {
  return {ms: bits(pa, 8, 6), ch: bits(pa, 9, 9), bank: bits(pa, 12, 10), row: bits(pa, 34, 18), colHi: bits(pa, 17, 13), half: bits(pa, 5, 5), home: bits(pa, 10, 6)};
}

/* ---- the chains' scenes ---- */
// STG: memory-levels.script.js at 290cb9c, lines 2970-2970
const STG = ['ag', 'ad', 'rqa', 'tap', 'ta', 'ta0', 'ta1', 'te', 'tc', 'dap', 'da', 'da0', 'da1', 'de', 'dc'];
// TLX: memory-levels.script.js at 290cb9c, lines 4905-4907
/* the channel: one rank of 8 banks; the open row; the command and data timeline drawn to scale from the programmed
   timings (dram.ctl.*), which is ET's; the die's circuits are JEDEC/textbook */
const TLX = ns => -60 + ns * 22.2;
// buildL1Cache: memory-levels.script.js at 290cb9c, lines 2463-2514
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
// buildL1Block: memory-levels.script.js at 290cb9c, lines 2516-2557
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
// buildL1Row: memory-levels.script.js at 290cb9c, lines 2559-2592
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
// buildL1Latch: memory-levels.script.js at 290cb9c, lines 2594-2597
function buildL1Latch(L, ap, inst) {
  buildLatchCell(L, ap, {title: 'One latch bit · a transmission-gate D latch',
    sub: 'how ET\'s latch register files hold a bit; the cell inside the silicon macro is not documented'});
}
// buildL1Cmp: memory-levels.script.js at 290cb9c, lines 2598-2600
function buildL1Cmp(L, ap, inst) {
  buildComparator(L, ap, {title: 'Tag comparator · XNORs and an AND tree', sub: `${nt('g_cmp33')} per way, an XNOR each; all four ways compare in S1 and one hits (way 2 in the example)`});
}
// buildL2Bank: memory-levels.script.js at 290cb9c, lines 2971-3016
function buildL2Bank(L, ap, inst) {
  frame(L, {title: `Bank ${inst.bank} (PA[7:6]) · one of four`, sub: 'an independent L2 cache: its own request queue, pipeline and ports',
    tags: [['unknown', '? read-buffer storage, prefetcher · asked'], ['documented', 'documented']]});
  const gq = part(L, 'reqq', -150, 14, 400, 186, COL.logic, 'request queue', {sub: [{t: `${nt('l2_reqq')} · ${nt('l2_reqq21')} for the L3 (grey)`, f: nf('l2_reqq')}]});
  ap.q = [];
  for (let i = 0; i < 64; i++) {
    const x = -138 + (i % 16) * 24, y = 88 + Math.floor(i / 16) * 26, l3 = i >= 43;
    ap.q.push(S(E('rect', {x, y, width: 20, height: 20, rx: 3, 'pointer-events': 'none', 'data-band': l3 ? 'pat-hatch' : null}, gq), {fill: l3 ? BAND_FILL['pat-hatch'] : 'var(--c1)', fillOpacity: l3 ? 1 : 0.15, stroke: 'var(--c1)', strokeWidth: 1}));
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
// buildL2Sub: memory-levels.script.js at 290cb9c, lines 3018-3057
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
// buildL2Panel: memory-levels.script.js at 290cb9c, lines 3059-3062
function buildL2Panel(L, ap, inst) {
  buildPanel(L, ap, {title: `Data panel ${inst.panel} · ${nt('l2_mdata_s')} · 1PUHD`, f: nf('l2_mdata_s'), band: 'l2', row: inst.row,
    sub: 'saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11: a compiled macro, "SRAM memory panels" in the spec'});
}
// buildL2Cell: memory-levels.script.js at 290cb9c, lines 3063-3067
function buildL2Cell(L, ap, inst) {
  buildCell(L, ap, {title: 'One bit · a 6T SRAM cell (generic)',
    sub: 'the spec says SRAM panels; the lab lead said the chip is not using SRAM; the bitcell is not documented (asked)',
    note: [`a shire's arrays: ≈ ${nt('l2_tr')}`, 'cell transistors if 6T/8T (estimate)'], noteF: nf('l2_tr')});
}
// buildL2Xing: memory-levels.script.js at 290cb9c, lines 3068-3071
function buildL2Xing(L, ap, inst) {
  buildXing(L, ap, {title: 'The crossing · a level shifter', sub: 'the neighbourhood\'s bank FIFO is a VC FIFO with level shifters built in (documented); the circuit is generic',
    vddl: `VDDL ${nt('l1_v')}`, vddlF: nf('l1_v'), vddh: 'VDDH (rail asked)', vddhF: 'l2:l2.rail.hv-logic'});
}
// buildHop: memory-levels.script.js at 290cb9c, lines 3670-3731
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
  part(L, 'hopE', -136, 604, 600, 84, COL.aux, 'a 64 B reply over one hop', {sub: [{t: `≈ ${nt('l3_hop69')} on the mesh rail (derived); ${nt('l3_hop_rb')} on the board (measured)`, f: nf('l3_hop69') + ' ' + nf('l3_hop_rb')}]});
  part(L, 'nochop', 480, 604, 598, 84, 'var(--warn)', 'unknown: the router pipeline per hop', {kind: 'unknown', sub: [{t: 'which of the 9 layers, the flit width', f: 'l3:u.noc-hop'}]});
}
// buildWire: memory-levels.script.js at 290cb9c, lines 3748-3812
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
// buildL3Wire: memory-levels.script.js at 290cb9c, lines 4039-4041
function buildL3Wire(L, ap, inst) {
  buildWire(L, ap, {title: 'A link bit, and the crossing', sub: 'a repeater charging a wire; the level shifter at the far shire (textbook)'});
}
// buildMS: memory-levels.script.js at 290cb9c, lines 4860-4903
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
  // the grey bar: the memory shire's time, not split
  const gl = comp(L, 'lat63', {}, 'The L3 home\'s miss path and the memory shire, at most about 63 cycles of a load: not split, asked');
  S(E('rect', {x: -140, y: 606, width: 1218, height: 50, rx: 6, 'data-band': 'pat-hatch'}, gl), {fill: BAND_FILL['pat-hatch'], stroke: 'var(--warn)', strokeWidth: 2, strokeDasharray: '8 6'});
  T(gl, -124, 638, `the L3 home's miss path and this memory shire: ${nt('dr_ms63s')} · how it splits: asked`, 't-smb halo', 'start', nf('dr_ms63') + ' dram:dram.lat.ms-internal');
  gl._box = {x: -140, y: 606, w: 1218, h: 50}; E('rect', {class: 'ring', x: -145, y: 601, width: 1228, height: 60, rx: 10}, gl);
  T(L, -140, 684, `the DRAM's own timing: ${nt('dr_share')}; the constant past an L3 hit: ${nt('l3_dram91')}`, 't-sm', 'start', nf('dr_share') + ' ' + nf('l3_dram91'));
  ap.noc = {x: -65, y: 130}; ap.xg = {x: 111, y: 130}; ap.st = {x: 289, y: 130}; ap.dfiP = {x: 803, y: 0}; ap.phyP = {x: 912, y: 0};
}
// buildChan: memory-levels.script.js at 290cb9c, lines 4908-4943
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
// buildDBank: memory-levels.script.js at 290cb9c, lines 4945-4971
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
// buildDCell: memory-levels.script.js at 290cb9c, lines 4973-5046
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
// buildPHY: memory-levels.script.js at 290cb9c, lines 5114-5134
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
// buildDQ: memory-levels.script.js at 290cb9c, lines 5135-5166
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

/* ---- the parts' texts (each part's panel) ---- */
// L1P: memory-levels.script.js at 290cb9c, lines 2620-2678
const L1P = {
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
// L2P: memory-levels.script.js at 290cb9c, lines 3091-3164
const L2P = {
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
    what: `Reading the L2 with tensor loads on every minion costs ${n('l2_e')}, about ${n('l2_e_line')} per line for the whole path. No L2 hit has been split between the rails on three cards; read as the own scratchpad, the same arrays put ${n('l2_rails_sram')} of the power on the SRAM rail and ${n('l2_rails_min')} on the minion rail (aifoundry2, aifoundry3 and aifoundry1 card 1). A scratchpad write costs about twice a read (${n('l2_e_wr')}); a random fsw through the L1 costs ${n('l2_fsw')}. How much of the SRAM rail's share is the arrays and how much the logic is asked.`}),
};
// DP: memory-levels.script.js at 290cb9c, lines 5208-5287
const DP = {
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
// L3P: memory-levels.script.js at 290cb9c, lines 4063-4157
const L3P = {
  link: () => ({kick: 'L3 · chip', title: 'A mesh hop', badge: [['documented', 'measured cost'], ['generic', 'the router'], ['unknown', 'its pipeline']], facts: 'hop',
    what: `Each hop adds ${n('l3_hopcyc')} to the round trip (${n('l3_hopns')}, the same for L3 hits, remote scratchpad and TensorSend). Zoom in to see a router, a link and the crossings.`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="hop">Zoom into a hop</button>`}),
  bankR: () => ({kick: 'L3 · mesh hop', title: 'The requester\'s bank', badge: [['documented', 'spec']], facts: 'ports', what: 'The L2 missed: the bank\'s request-queue entry stays to receive the fill, and the read goes out on a to_l3 port.'}),
  tol3: () => ({kick: 'L3 · mesh hop', title: 'to_l3 master', badge: [['documented', 'spec, re-implementation RTL']], facts: 'lane',
    what: 'The lane is the bank the request will use at the home, PA[12:11] under swizzle0, not PA[7:6] (which picks the lane only for remote scratchpad): so says the re-implementation RTL alone, to confirm. The ET-Link read becomes an AXI read address (AR), about 75–85 bits.'}),
  vcdown: () => ({kick: 'L3 · mesh hop', title: 'Into the mesh: a VC FIFO', badge: [['documented', 'that it is there'], ['generic', 'the circuit']], facts: 'xing',
    what: `A voltage-changing FIFO with 2-stage synchronisers: the request leaves the Shire Channel (its SRAM arrays on ${n('l3_sram_v')}, its logic on a rail that is asked; ${n('l3_clk')}) for the mesh (${n('l3_mesh_v')}, ${n('l3_noc')}). Level shifters change the swing; the synchroniser costs 2–3 receiving-clock cycles (textbook).`,
    act: `<button type="button" class="st-btn" data-act="zoom" data-to="rep">Zoom into the transistors</button>`}),
  slave: () => ({kick: 'L3 · mesh hop', title: 'The home\'s L3-slave port', badge: [['documented', 'spec']], facts: 'ports', what: 'The request climbs back into the Shire Channel through the port\'s VC FIFO, becomes an ET-Link request and waits in the bank\'s L3-slave FIFO.'}),
  router: () => ({kick: 'L3 · mesh hop', title: 'A router', badge: [['generic', 'textbook stages'], ['documented', 'layers, ports'], ['unknown', 'its pipeline']], facts: 'router',
    what: `Each mesh stop has 9 main-NoC routers (layers 0–8) and a debug router, with 8 ports of 4 virtual-channel slots each, parity-protected. Inside, textbook stages: input VC buffers, route computation, VC and switch allocators, a crossbar and output drivers. Which layer carries L3 traffic, the flit width and the pipeline depth are asked; ${src('the dimension order was measured on 29 September', 'l3:l3.route chip:L104')}: a request goes x first, its reply y first.`}),
  router2: () => L3P.router(), more: () => L3P.link(),
  link: () => ({kick: 'L3 · mesh hop', title: 'A link', badge: [['documented', 'the energy, the length'], ['generic', 'repeaters']], facts: 'wire',
    what: `One hop is about ${n('l3_hopmm')} of wire, broken by repeaters. A random bit costs ${n('l3_fj')} per mm on the mesh rail, so a 64-byte reply over one hop is ${n('l3_hop69')} on the mesh rail (derived); measured on board power, a hop adds ${n('l3_hop_r')} and ${n('l3_hop_z')}. Zeros do not toggle the wires: they cost several times less.`,
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

  /* ---- the adapter: a copied scene drawn into one of the chip page's layers ---- */
  function build(fn, L, ap, inst, parts) {
    // the small type's size where the page is now (a short or narrow screen sets it larger): the lines under a part's
    // title are set 1.2 times that apart
    try { const t = E('text', {class: 't-sm'}, L); SUBLH = Math.round(1.2 * (parseFloat(getComputedStyle(t).fontSize) || 17)); t.remove(); } catch (_) { SUBLH = 21; }
    BAP = ap; ap.zg = {}; ap.parts = {};
    try { fn(L, ap, inst); } finally { BAP = null; }
    L.classList.add('ckt');
    L.querySelectorAll('.comp').forEach(g => { g._mlp = parts || null; });
    measured(L, () => { ringAll(L); fitTexts(L); kbTexts(L); });
  }
  /* a part drawn in strokes only (a row of gate symbols, a level shifter) gets a transparent hit area under its strokes,
     so that a click, a tap or a double-tap anywhere on it finds it; never where it would cover a part drawn before it */
  function hitAreas(L) {
    const comps = [...L.querySelectorAll('.comp')], box = new Map();
    measured(L, () => comps.forEach(g => {
      let b = g._box;
      if (!b) { try { const r = g.getBBox(); if (r.width && r.height) b = {x: r.x, y: r.y, w: r.width, h: r.height}; } catch (_) { /* not rendered */ } }
      if (b) box.set(g, b);
    }));
    const ov = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    comps.forEach((g, i) => {
      const b = box.get(g);
      if (!b || g.querySelector(':scope > rect.shape, :scope > rect.hit')) return;
      if (comps.slice(0, i).some(o => box.get(o) && !o.contains(g) && ov(b, box.get(o)) > 0.2 * box.get(o).w * box.get(o).h)) return;
      const r = E('rect', {class: 'hit', x: b.x, y: b.y, width: b.w, height: b.h, fill: 'transparent', 'pointer-events': 'all'});
      g.insertBefore(r, g.firstChild);
    });
  }
  /* a part's panel text, from its scene's parts (kick, title, badges, what, kpis); null when it has none */
  function partText(g) {
    const P = g._mlp && g._mlp[g._key]; if (!P) return null;
    let d; try { d = P(g._ctx || {}); } catch (e) { console.error(e); return null; }
    return {kick: d.kick, title: d.title, badge: d.badge ? badges(d.badge) : '', what: d.what || '', kpis: d.kpis || []};
  }
  /* the example address's instance at each chain (the memory levels' own example: a DRAM-region line) */
  const INST = {
    l1: () => { const a = dec1(ADDR.pa); return {block: a.block, row: a.row, set: a.set, half: a.half, way: a.way}; },
    l2: () => { const a = dec2(ADDR.pa); return {bank: a.bank, sub: a.sub, set: a.set, way: a.way, row: a.row, panel: 0}; },
    dram: () => dec5(ADDR.pa),
  };
  /* one mesh hop, as the L3 level draws it from a requester to the home's L3-slave port */
  const buildMeshHop = (L, ap, o) => buildHop(L, ap, Object.assign({title: 'One mesh hop, up close', sub: 'from a shire’s cache bank to the next shire’s port; a reply comes back the same way',
    bank: 0, lane: 'PA[7:6]', laneF: 'l3:l3.lane', to: 'the next shire’s port'}, o || {}));
  return {build, hitAreas, partText, INST, FR, COL, DASH, buildMeshHop,
    buildL1Cache, buildL1Block, buildL1Row, buildL1Latch, buildL1Cmp, buildL2Bank, buildL2Sub, buildL2Panel, buildL2Cell, buildL2Xing,
    buildWire, buildL3Wire, buildMS, buildChan, buildDBank, buildDCell, buildPHY, buildDQ,
    parts: {l1: L1P, l2: L2P, l3: L3P, dram: DP},
    kit: {comp, part, boxShape, tagPill, frame, railBand, wire, jn, netLab, rail, gnd, mosV, mosH, invSym, andSym, mux2, flopSym, icgSym, T, measured, ringAll, fitTexts, kbTexts,
      setBAP: ap => { BAP = ap; }}};
})({E, S, esc, CK, num: D.mlnum || {}, addr: D.mladdr || {}, layout: D.layout});
