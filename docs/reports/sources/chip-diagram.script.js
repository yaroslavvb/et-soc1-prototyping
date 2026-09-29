/* The ET-SoC-1, interactively. D is facts.json (docs/reports/data/2026-09-27-chip-diagram/build_facts.py):
   D.facts  the facts the page uses, by id: statement, value, unit, source, kind (measured, spec, derived, inferred),
            the lab cards each covers, and the report page that quotes it
   D.num    every number the page prints outside a fact's own statement, each tied to the fact whose statement
            contains it (the build asserts that); n(key) prints one with its source on hover
   D.comp   the facts each details panel lists
   D.layout the measured 6 x 6 map of the compute shires, the die view and the memory-shire fit
   D.asks   what would settle each inferred or dashed part, and the hub's ladder row that asks for it (D.rungs: the
            titles of those rows, read from the hub's own data)
   A value the page computes (a route's hops, a model's cycles) cites the facts it comes from. Every leg is drawn on
   the route the mesh takes, as E56 measured it on 29 September (fact L104): a request x first, then y, on the logical
   map, and a reply y first, then x, back along its request's links (route and reply below). Colours are the
   template's tokens only.

   Second version (27 September). Every flow is a list of stages, shown in the stage bar under the drawing: a click
   or the Left and Right arrows go to a stage, and Space pauses everything that moves, the camera included (stepping
   while paused draws the stage's end state). The camera follows the flow (Follow, key C) or stays where the reader
   put it; then a stage on the die plays in a small picture of the die, and a stage inside a shire or a minion the
   camera is not showing marks its place. The scale control (Chip, Shire, Minion, + and -) is always there; a double
   click or Enter zooms into a shire or a minion. Every camera move eases in and out and zooms at a steady rate on a
   log scale; a flow's packet rides the zoom from one scale to the next. F presents: full screen where the frame
   allows it, else the stage fills the frame and offers F11 and a presenter window (a copy of the page in a window of
   its own). With reduced motion nothing animates: each stage draws its end state.
   Keys: 1-9 and 0 flows (in the tour, that flow's slide), B the broadcast (no tour slide: it ends the tour), Left/Right (and PageUp/PageDown) stages, crossing to the
   next tour slide at a flow's ends; Shift+Left/Right tour slides; Space pauses; + and - zoom (a second press while the
   camera moves goes on from its target); Enter on a part zooms in; Backspace zooms out; C follow; F present; P panel;
   D light and dark; T tour (it picks up where it was left); Q ends the tour; Esc leaves presenting, never the tour.
   URL flags: ?theme=light|dark, ?panel=off, ?flow=1..9|0|b, ?tour=1.

   Third version (27 September, for presenting): one drawing system (stroke weights, corner radii, type weights), --c2
   kept for what moves; a semantic zoom whose labels never swell and whose camera can be redirected mid-move; the
   stage's line as the caption; presenting mode (the tour, F) without the reader's instructions. */
(function () {
'use strict';
/* the page's own HTML, before the script changes it: the presenter window is written from it when the server's copy
   cannot be fetched */
let SRC_HTML = '';
try { SRC_HTML = '<!doctype html>\n' + document.documentElement.outerHTML; } catch (_) { /* no DOM access */ }
const F = D.facts, N = D.num, COMPF = D.comp, LAY = D.layout, ASKS = D.asks || [], RUNGS = D.rungs || {};
const HUB = 'https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability';
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
let REDUCED = !!CK.reduced;
try { const mq = matchMedia('(prefers-reduced-motion: reduce)'); mq.addEventListener('change', e => { REDUCED = e.matches; }); } catch (_) { /* old browser */ }
const fnum = (v, dp) => CK.fmt.num(v, dp);
const V = k => { if (!N[k]) throw new Error('no number ' + k); return N[k].v; };
/* how a number's text is shown: a multiplier with the sign × (the facts write 12.4x), nothing else changes */
const disp = t => String(t).replace(/(\d)x(?=$|[\s,;.)])/g, '$1×');
/* a number from D.num, with its fact attached; a unit after it never wraps onto the next line */
function n(k, unit) {
  const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; }
  return `<span class="num" data-f="${x.f}">${esc(disp(x.t))}${unit ? '\u00a0' + esc(unit) : ''}</span>`;
}
/* a number the page computes, citing the facts it comes from */
const cn = (v, fids, dp, unit) => `<span class="num" data-f="${fids}">${fnum(v, dp)}${unit ? '\u00a0' + unit : ''}</span>`;
/* an arrow in text, in a font that draws it (outside tags only) */
const ARW = html => String(html).replace(/(<[^>]*>)|([←→↑↓])/g, (m, tag, a) => tag || `<span class="arr">${a}</span>`);
const S = (node, o) => { for (const k in o) if (o[k] != null) node.style[k] = o[k]; return node; };
const E = (tag, attrs, parent) => CK.el(tag, attrs, parent);
function T(parent, x, y, str, cls, anchor, fids) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  const s = String(str);
  if (/[←→↑↓]/.test(s)) s.split(/([←→↑↓])/).forEach(p => { if (!p) return; if (/[←→↑↓]/.test(p)) E('tspan', {class: 'arr'}, t).textContent = p; else t.appendChild(document.createTextNode(p)); });
  else t.textContent = s;
  if (fids) t.setAttribute('data-f', fids);
  return t;
}
/* lines of SVG text, each under the last at 1.2 times its font's size (the size a short screen sets larger); a line
   may be {t, c, f}: its own class (size, weight) and source */
function T2(parent, x, y, lines, cls, anchor, fids, lh) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  lines.forEach((ln, i) => {
    const L = typeof ln === 'string' ? {t: ln} : ln, sp = E('tspan', {x, dy: i ? (lh || 1.2) + 'em' : 0}, t);
    sp.textContent = L.t; if (L.c) sp.setAttribute('class', L.c); if (L.f) sp.setAttribute('data-f', L.f);
  });
  if (fids) t.setAttribute('data-f', fids);
  return t;
}
const ns = cyc => cyc * 1000 / V('mhz');   // minion cycles at 600 MHz to ns

/* ================= geometry: the die drawn to scale (sizes inferred from a die plot) ================= */
const MM = 30;                                         // SVG units per mm
const TILE = V('grid_mm') / 6 * MM, STRIP = V('strip_mm') * MM;
const DW = 2 * STRIP + 6 * TILE, DH = 6 * TILE, INS = 5;
/* the drawing's frame: the die with its packages and the host, and right of them a column for the flows' charts (a
   frame 100 units wider than the die's needs costs the drawing under 2% at 1920 x 1080 and nothing at 1280 x 720,
   where the height sets its scale) */
const VB = {x: -190, y: -84, w: 1400, h: 792};
const SF = {x: 160, y: -36, w: 700, h: 700};          // where a shire is drawn when zoomed in (centred in the frame)
const MF = {x: -60, y: -70, w: 1140, h: 760};          // where a minion is drawn when zoomed in
/* Phones and narrow portrait windows (PH): the drawing fits the window's width and nothing in it scrolls sideways.
   The die is drawn with narrow LPDDR4X packages beside it and the host above it, its labels larger (FS0: 11 px on the
   screen, 29 to 32 units as the drawing is wide), and each scale has its own view (PV: the die, a shire, a minion).
   The drawing's box keeps one height whatever the scale (the tallest view's; a shorter view sits at its top), so that
   the controls under the drawing never move, and a zoom changes only the layers' transforms (the view is part of
   them), never the page's layout. While a flow or the tour plays, the box is taller by the band that the flows' charts
   fold into under the die (bandFold, phBox). PH follows the window: a phone turned, or a window resized across it,
   rebuilds the drawing (phSwitch). TOUCH: no keyboard and no hover, so no keyboard hints, and a tap on a shire or a
   minion zooms into it. */
const mqOn = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
const PHQ = '(max-width: 899px) and (max-aspect-ratio: 1/1)';
const TOUCH = mqOn('(hover: none) and (pointer: coarse)');
let PH = false, PKW = 110, PV = null, BANDX = Infinity, FS0 = 29;   // FS0: a phone's label size at the chip's scale, in units
const pkgX = west => PH ? (west ? -12 - PKW : DW + 12) : (west ? -150 : DW + 40);   // an LPDDR4X package's left edge
function phGeom() {
  PH = mqOn(PHQ);
  PKW = PH ? 40 : 110;                                 // an LPDDR4X package's width
  PV = PH ? [{x: -24 - PKW, y: -162, w: DW + 2 * (PKW + 24), h: DH + 214}, {x: SF.x - 42, y: SF.y - 50, w: SF.w + 84, h: SF.w + 160},
    {x: MF.x - 12, y: MF.y - 12, w: MF.w + 24, h: MF.h + 24}] : null;
  BANDX = PH ? PV[0].x + PV[0].w : Infinity;           // on a phone, what is drawn right of this folds under the die
  // the chip's labels 11 px on the screen, the drawing as wide as its box is now (a phone's width does not change)
  if (PH) { const bw = $('svgwrap').clientWidth || innerWidth - 32; FS0 = Math.max(29, Math.min(32, Math.ceil(11.2 * PV[0].w / bw))); }
}
// (in a frame the page's gutters are wider on a phone: CSS html.et-framed; set before the drawing is measured)
try { if (window.self !== window.top) document.documentElement.classList.add('et-framed'); } catch (_) { document.documentElement.classList.add('et-framed'); }
phGeom();
/* a phone's size for a label, in units (a wide screen keeps the class's); phFit: on a phone, a label no wider than w
   units (measured once drawn): up to 8% too wide, it is set a little narrower (textLength), keeping its height; wider,
   its size comes down too (a system font wider than the one it was set with) */
const phSize = (t, u) => { if (PH) t.style.fontSize = u + 'px'; return t; };
function phFit(t, w) {
  if (!PH) return t;
  try {
    const l = t.getComputedTextLength(); if (!(l > w)) return t;
    if (l > w * 1.08) t.style.fontSize = (parseFloat(getComputedStyle(t).fontSize) * w * 1.08 / l).toFixed(1) + 'px';
    t.setAttribute('textLength', w.toFixed(1)); t.setAttribute('lengthAdjust', 'spacingAndGlyphs');
  } catch (_) { /* not rendered */ }
  return t;
}
const COL = {cshire: 'var(--c1)', master: 'var(--c7)', pcie: 'var(--c4)', io: 'var(--c5)', memshire: 'var(--c3)'};

const CELLS = [], BYLOG = {}, BYDIE = {}, SH = {}, MSC = {};
LAY.mesh_die.forEach((row, r) => row.forEach((v, c) => {
  if (v === null) return;
  const x = c === 0 ? 0 : c === 7 ? STRIP + 6 * TILE : STRIP + (c - 1) * TILE, w = (c === 0 || c === 7) ? STRIP : TILE;
  const cell = {r, c, x, y: r * TILE, w, h: TILE, lx: r, ly: c === 0 ? -1 : c === 7 ? 6 : c - 1};
  if (typeof v === 'number') { cell.type = 'cshire'; cell.id = v; SH[v] = cell; }
  else if (/^MS\d$/.test(v)) { cell.type = 'memshire'; cell.id = +v.slice(2); MSC[cell.id] = cell; }
  else { cell.type = c === 4 ? 'master' : c === 5 ? 'pcie' : c === 6 ? 'io' : 'grey'; cell.id = cell.type === 'master' ? (r === 0 ? 'north' : 'south') : cell.type; }
  cell.sx = cell.type === 'memshire' ? x + w / 2 : x + 0.6 * w; cell.sy = cell.y + 0.6 * TILE;   // the mesh stop
  CELLS.push(cell); BYLOG[cell.lx + ',' + cell.ly] = cell; BYDIE[r + ',' + c] = cell;
}));
/* the die view must be the measured map turned onto the die (the firmware's NoC-spec drawing), with the fitted memory shires */
LAY.mesh.forEach((row, y) => row.forEach((v, x) => {
  const c = BYLOG[x + ',' + y];
  if (typeof v === 'number' ? !(c && c.type === 'cshire' && c.id === v) : !(c && c.type !== 'cshire')) console.error('die view disagrees with the map at', x, y);
}));
LAY.memshires.forEach(m => { const c = BYLOG[m.pos[0] + ',' + m.pos[1]]; if (!c || c.type !== 'memshire' || c.id !== m.id) console.error('memory shire', m.id, 'misplaced'); });
const TIE = new Set(LAY.memshires.filter(m => m.tie_break).map(m => m.id));
const hops = (a, b) => Math.abs(a.lx - b.lx) + Math.abs(a.ly - b.ly);
function xy(a, b, xFirst) {
  const out = [a]; let x = a.lx, y = a.ly;
  const step = (dx, dy) => { x += dx; y += dy; const c = BYLOG[x + ',' + y]; if (c) out.push(c); return !!c; };
  const X = () => { while (x !== b.lx) if (!step(Math.sign(b.lx - x), 0)) return false; return true; };
  const Y = () => { while (y !== b.ly) if (!step(0, Math.sign(b.ly - y))) return false; return true; };
  return (xFirst ? X() && Y() : Y() && X()) ? out : null;
}
/* The mesh's routing order, measured by E56 (29 September, aifoundry1 card 1 and aifoundry3; fact L104): a request
   goes x first, then y, on the logical map; a reply y first, then x, so it retraces its request's route backwards.
   route() draws a request: a load's or an atomic's request, a store's data, a TensorSend (E56 timed loads and stores;
   the tensor messages are drawn as requests too). reply() draws a reply: the data a load brings back. On the die view x
   runs down the rows, so a request first moves north or south. No leg drawn here needs the other order (requests
   reach a memory shire along its column, replies leave it that way); one that would cross an empty corner takes it. */
function route(a, b) { return xy(a, b, true) || xy(a, b, false) || [a, b]; }
function reply(a, b) { return xy(a, b, false) || xy(a, b, true) || [a, b]; }
/* a path through several stops, each leg a request's route (via) or a reply's (viaR) */
function via(...cs) { let out = [cs[0]]; for (let i = 1; i < cs.length; i++) out = out.concat(route(cs[i - 1], cs[i]).slice(1)); return out; }
function viaR(...cs) { let out = [cs[0]]; for (let i = 1; i < cs.length; i++) out = out.concat(reply(cs[i - 1], cs[i]).slice(1)); return out; }
const pts = cells => cells.map(c => ({x: c.sx, y: c.sy}));
/* a reply's lane: its route moved d units to the right of its direction of travel, so that a reply running back
   along a request's mesh line takes its own side of it and the two never overprint; from (a point on the request's
   line), a short step across to the lane */
function lane(P, d, from) {
  const Q = P.filter((p, i) => !i || Math.hypot(p.x - P[i - 1].x, p.y - P[i - 1].y) > 0.5);
  if (Q.length < 2) return from ? [from].concat(Q) : Q;
  const nr = (a, b) => { const dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy); return {x: -dy / L, y: dx / L}; };
  const out = Q.map((p, i) => {
    const n0 = i > 0 ? nr(Q[i - 1], p) : null, n1 = i < Q.length - 1 ? nr(p, Q[i + 1]) : null;
    if (!n0) return {x: p.x + n1.x * d, y: p.y + n1.y * d};
    if (!n1 || Math.abs(n0.x * n1.x + n0.y * n1.y) > 0.99) return {x: p.x + n0.x * d, y: p.y + n0.y * d};
    return {x: p.x + (n0.x + n1.x) * d, y: p.y + (n0.y + n1.y) * d};   // a right-angle turn: the corner of both lanes
  });
  return from ? [from].concat(out) : out;
}
const LANE = 9;
const cellName = c => !c ? 'the die edge' : c.type === 'cshire' ? 'shire ' + c.id : c.type === 'memshire' ? 'memory shire ' + c.id
  : c.type === 'master' ? (c.r === 0 ? 'master shire' : 'spare shire') : c.type === 'pcie' ? 'PCIe shire' : c.type === 'io' ? 'I/O shire' : 'grey cell';

/* ================= the SVG and its three layers ================= */
const svg = $('chip');
svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
/* the callouts' soft shadow (its strength is set by the theme, CSS #co-sh feDropShadow) */
{ const f = E('filter', {id: 'co-sh', x: '-10%', y: '-20%', width: '120%', height: '160%'}, E('defs', {}, svg)); E('feDropShadow', {dx: 0, dy: 2, stdDeviation: 3, 'flood-color': '#000'}, f); }
const LAYERS = [0, 1, 2].map(i => E('g', {class: 'lay', 'data-level': i}, svg));
LAYERS[1].style.display = 'none'; LAYERS[2].style.display = 'none';
LAYERS[1].style.opacity = 0; LAYERS[2].style.opacity = 0;   // hidden views start transparent: a zoom fades them in
const FX = [null, null, null];
const AP = [{}, {}, {}];                                // anchor points of the flows, per layer

function comp(parent, key, ctx, label) {
  const g = E('g', {class: 'comp dimmable', tabindex: 0, role: 'button', 'aria-label': label, 'data-comp': key}, parent);
  g._key = key; g._ctx = ctx || {};
  return g;
}
/* One drawing system: outlines of components 2 units (frames and the die 2.5, sub-structure 1.25), corners of 6 units
   (frames 14, the die 10); interconnect at rest thinner than a moving trail (6). o.quiet: no outline until hover or focus */
function boxShape(g, x, y, w, h, col, o) {
  o = o || {};
  const rx = o.rx == null ? 6 : o.rx;
  S(E('rect', {class: 'shape' + (o.quiet ? ' quiet' : ''), x, y, width: w, height: h, rx}, g),
    {fill: o.fill || col, fillOpacity: o.fo == null ? 0.12 : o.fo, stroke: col, strokeWidth: o.sw || 2, strokeDasharray: o.dash ? '8 6' : null});
  E('rect', {class: 'ring', x: x - 5, y: y - 5, width: w + 10, height: h + 10, rx: rx + 4}, g);
}
/* a mesh link or a link to a neighbour: one colour and width everywhere (CSS .mlink) */
const mlink = (parent, x1, y1, x2, y2) => E('line', {class: 'mlink', x1, y1, x2, y2}, parent);

function buildChip() {
  const L = LAYERS[0];
  // LPDDR4X packages off the die, two per side (datasheet Fig. 2-6, fact L23). Two memory shires share each package;
  // which two is not documented, so the pairing of neighbours is inferred and the packages are dashed (dram.pkg-pairing)
  const PKG = {};
  [[0, 1], [2, 3], [4, 5], [6, 7]].forEach(ms => {
    const a = MSC[ms[0]], b = MSC[ms[1]], west = a.c === 0;
    const x = pkgX(west), w = PKW, y = a.y + 8, h = b.y + b.h - 8 - y;
    const g = comp(L, 'dram', {ms}, `LPDDR4X package, drawn beside memory shires ${ms[0]} and ${ms[1]} (pairing inferred): details`);
    ms.forEach(m => { const c = MSC[m];
      [-14, 14].forEach((dy, k) => {
        S(E('line', {x1: west ? x + w : DW, x2: west ? 0 : x, y1: c.sy + dy, y2: c.sy + dy}, g), {stroke: 'var(--c3)', strokeWidth: 2.5});
        PKG[m + ':' + k] = {x: west ? x + w - 6 : x + 6, y: c.sy + dy};
      });
      PKG[m] = {x: x + w / 2, y: c.sy};
    });
    boxShape(g, x, y, w, h, 'var(--c3)', {fo: 0.16, dash: true});
    const cx = x + w / 2, cy = y + h / 2;
    if (PH) {
      // a narrow package: its name turned to run up its length (its channels are in its details)
      const t1 = phSize(T(g, cx + FS0 * 0.36, cy, 'LPDDR4X', 't-labb', 'middle', 'dram.pkg-pairing'), FS0);
      t1.setAttribute('transform', `rotate(-90 ${t1.getAttribute('x')} ${cy})`);
    } else {
      T(g, cx, cy - 16, 'LPDDR4X', 't-labb', 'middle', 'dram.pkg-pairing');
      T2(g, cx, cy + 10, ['four 16-bit', 'channels'], 't-sm t-fit', 'middle', 'L47');
    }
  });
  AP[0].pkg = PKG;
  // the die: its outline is the component "chip", a quiet frame; its caption is a figure caption, not a title
  const gd = comp(L, 'chip', {}, 'The ET-SoC-1 die: details');
  S(E('rect', {class: 'shape', x: 0, y: 0, width: DW, height: DH, rx: 10}, gd), {fill: 'var(--surface)', stroke: 'color-mix(in srgb, var(--ink-2) 55%, var(--surface))', strokeWidth: 2.5});
  E('rect', {class: 'ring', x: -6, y: -6, width: DW + 12, height: DH + 12, rx: 14}, gd);
  phSize(T(gd, 0, PH ? -20 : -22, `ET-SoC-1 · ${N.die_mm2.t} mm² · TSMC ${N.process.t}`, 't-dcap', 'start', 'chip.die-area chip.process'), FS0);
  // the host and the PCIe link (from the PCIe shire's top edge), now timed on three cards
  // (on a phone above the die's right end, flush with the east packages, the link running up from the PCIe shire and
  // across to it)
  const pc = CELLS.find(c => c.type === 'pcie'), hw = 150, hh = 92, hx = PH ? pkgX(false) + PKW - hw : 950, hy = PH ? -150 : -74, ly = PH ? hy + hh / 2 : -30;
  const gh = comp(L, 'host', {}, 'The host and the PCIe link: details');
  S(E('path', {d: `M${pc.sx},${pc.y + INS} V${ly} H${hx}`, fill: 'none'}, gh), {stroke: 'var(--c4)', strokeWidth: 4, strokeLinejoin: 'round'});
  boxShape(gh, hx, hy, hw, hh, 'var(--ink-2)', {fo: 0});
  T(gh, hx + hw / 2, hy + (PH ? 56 : 54), 'Host', 't-mid', 'middle').style.fontSize = (PH ? FS0 : 22) + 'px';
  phSize(T(gh, hx - 14, ly - 12, `PCIe Gen4 x8 · ${N.pcie_h2d.t} GB/s to the card`, 't-sm halo', 'end', 'pcie.h2d pcie.negotiated'), FS0);
  AP[0].host = [{x: hx + 4, y: ly}, {x: pc.sx, y: ly}, {x: pc.sx, y: pc.sy}];
  AP[0].hostBox = {x: hx, y: hy, w: hw, h: hh, ly};
  // mesh links and stops, under the translucent tiles (visual only: the tiles take the clicks)
  const LG = E('g', {class: 'dimmable links', 'pointer-events': 'none'}, L);
  AP[0].links = LG;
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hops(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly)) mlink(LG, a.sx, a.sy, b.sx, b.sy);
  }));
  CELLS.forEach(c => E('circle', {class: 'mstop', cx: c.sx, cy: c.sy, r: 5}, LG));
  // the tiles: the four cells without a compute shire are named by the firmware's map (fact fw.grey-cells)
  CELLS.forEach(c => {
    const g = comp(L, c.type, {cell: c}, tileLabel(c)); c.g = g;
    boxShape(g, c.x + INS, c.y + INS, c.w - 2 * INS, c.h - 2 * INS, COL[c.type], {fo: c.type === 'cshire' ? 0.14 : 0.12});
    const x0 = c.x + INS + (PH ? 6 : 9), y0 = c.y + INS, tw = c.w - 2 * INS - 9;
    // (on a phone the labels are larger: a memory shire's number sits under its mesh stop, the master and spare shires
    // show their number alone, as the compute shires do, and the I/O shire's Maxions are named in its details)
    const big = t => phFit(phSize(t, FS0), c.type === 'memshire' ? c.w - 2 * INS - 2 : tw);
    if (c.type === 'cshire') T(g, x0, y0 + 38, String(c.id), 't-id');
    else if (c.type === 'memshire') { big(T(g, c.x + c.w / 2, y0 + (PH ? 32 : 26), 'MS', 't-labb halo-s', 'middle')); big(T(g, c.x + c.w / 2, y0 + (PH ? 86 : 50), String(c.id), 't-labb halo-s', 'middle')); }
    else if (c.type === 'master') {
      const north = c.r === 0, id = north ? N.master_id.t : N.spare_id.t;
      big(T(g, x0, y0 + (PH ? 31 : 27), north ? 'Master' : 'Spare', 't-labb halo-s', 'start', 'fw.grey-cells'));
      if (PH) big(T(g, x0, y0 + 86, id, 't-labb halo-s', 'start', 'fw.grey-cells chip.master-shire-id'));
      else T(g, x0, y0 + 50, 'shire ' + id, 't-sm halo-s', 'start', 'fw.grey-cells chip.master-shire-id');
    }
    else if (c.type === 'pcie') big(T(g, x0, y0 + (PH ? 32 : 30), 'PCIe', 't-labb halo-s'));
    else if (c.type === 'io') { big(T(g, x0, y0 + (PH ? 31 : 27), 'I/O', 't-labb halo-s')); if (!PH) T(g, x0, y0 + 50, 'Maxions', 't-sm halo-s'); }
  });
  // the mesh as a component, and a key for what is dashed (inferred) that opens what would settle it: plain labels
  // under the die, outlined only on hover or focus
  // (on a phone larger, in a taller row, the key's words shorter)
  const rh = PH ? 38 : 30, rb = PH ? DH + 36 : DH + 29, mw = PH ? FS0 * 12.6 : 262, iw = PH ? FS0 * 11.4 : 350;
  const gm = comp(L, 'mesh', {}, 'The mesh: details');
  boxShape(gm, 0, DH + 8, mw, rh, 'var(--ink-2)', {fo: 0, quiet: true});
  phSize(T(gm, 10, rb, `The mesh: ${N.grid86.t}, ${N.stops.t} stops`, 't-sm', 'start', 'mesh.grid'), FS0);
  const gi = comp(L, 'inferred', {}, 'What the drawing infers, and what would settle it: details');
  boxShape(gi, DW - iw, DH + 8, iw, rh, 'var(--ink-2)', {fo: 0, quiet: true});
  S(E('line', {x1: DW - iw + 12, y1: rb - 6, x2: DW - iw + 48, y2: rb - 6}, gi), {stroke: 'var(--c3)', strokeWidth: 2.5, strokeDasharray: '8 6'});
  const ti = phSize(T(gi, DW - 10, rb, PH ? 'what is inferred ›' : 'inferred · what would settle it ›', 't-sm', 'end'), FS0);
  // the dashed sample sits just left of its words (measured once drawn)
  try { const tl = ti.getComputedTextLength(); if (tl > 0) { const sl = gi.querySelector('line'); sl.setAttribute('x2', DW - 10 - tl - 10); sl.setAttribute('x1', DW - 10 - tl - 46); } } catch (_) { /* not rendered */ }
  FX[0] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}
function tileLabel(c) {
  if (c.type === 'cshire') return `Shire ${c.id}, compute shire. Space for details; Enter zooms in.`;
  if (c.type === 'memshire') return `Memory shire ${c.id}: details`;
  if (c.type === 'master') return (c.r === 0 ? 'Master shire, shire 32' : 'Spare shire, shire 33') + ', from the firmware\'s map: details';
  return (c.type === 'pcie' ? 'PCIe shire' : 'I/O shire') + ': details';
}

/* ---- a shire, zoomed in: a logical block diagram (no floorplan of the inside is published; fact L114) ---- */
function buildShire(sid) {
  const L = LAYERS[1]; L.textContent = ''; AP[1] = {min: {}, minG: {}, bank: [], lane: [], nbx: []};
  const P = AP[1], cell = SH[sid], X = SF.x, Y = SF.y, W = SF.w;
  P.sid = sid;
  // an opaque backdrop the size of the frame: while the camera zooms, nothing of the view behind shows through
  S(E('rect', {class: 'zbd', x: X, y: Y, width: W, height: W, rx: 14, 'pointer-events': 'none'}, L), {fill: 'var(--page)'});
  const fr = E('g', {}, L);
  S(E('rect', {x: X, y: Y, width: W, height: W, rx: 14}, fr), {fill: 'var(--c1)', fillOpacity: 0.05, stroke: 'var(--c1)', strokeWidth: 2.5});
  T(fr, X + 22, Y + 40, `Shire ${sid}`, 't-big');
  // (on a phone, the words around the frame are a little larger: SK units)
  const SK = 24.5;
  phSize(T(fr, X + W - 22, Y + 38, `map (${cell.lx}, ${cell.ly}) · ${N.per_shire.t}`, 't-sm', 'end', 'mesh.logical-map shire.composition'), SK);
  // mesh neighbours, in die orientation
  const nb = [[-1, 0, 'N'], [1, 0, 'S'], [0, -1, 'W'], [0, 1, 'E']].map(([dr, dc, s]) => [BYDIE[(cell.r + dr) + ',' + (cell.c + dc)], s]);
  P.edge = {};
  nb.forEach(([c, s]) => {
    const lab = c ? cellName(c) : 'die edge';
    if (s === 'N') { if (c) mlink(fr, X + W / 2, Y, X + W / 2, Y - 24); phSize(T(fr, X + W / 2 + 12, Y - 18, (c ? '↑ ' : '') + lab, 't-sm'), SK); P.edge.N = {x: X + W / 2, y: Y - 24}; }
    if (s === 'S') { if (c) mlink(fr, X + W / 2, Y + W, X + W / 2, Y + W + 24); phSize(T(fr, X + W / 2 + 12, Y + W + 30, (c ? '↓ ' : '') + lab, 't-sm'), SK); P.edge.S = {x: X + W / 2, y: Y + W + 24}; }
    // on a phone the side neighbours' names run up the frame's edges, above their links (the view is the frame's width)
    const sideLab = (x, y, str, rot) => { const t = phSize(T(fr, x, y, str, 't-sm', rot < 0 ? 'start' : 'end'), SK); t.setAttribute('transform', `rotate(${rot} ${x} ${y})`); };
    if (s === 'W') { if (c) mlink(fr, X, Y + W / 2, X - 24, Y + W / 2); if (PH) sideLab(X - 10, Y + W / 2 - 14, lab, -90); else T(fr, X - 30, Y + W / 2 + 6, lab + (c ? ' ←' : ''), 't-sm', 'end'); P.edge.W = {x: X - 24, y: Y + W / 2}; }
    if (s === 'E') { if (c) mlink(fr, X + W, Y + W / 2, X + W + 24, Y + W / 2); if (PH) sideLab(X + W + 10, Y + W / 2 - 14, lab, 90); else T(fr, X + W + 30, Y + W / 2 + 6, (c ? '→ ' : '') + lab, 't-sm'); P.edge.E = {x: X + W + 24, y: Y + W / 2}; }
  });
  if (PH) {
    // key, in a row under the frame
    const kx = X, ky = Y + W + 64;
    T(fr, kx, ky, 'Key', 't-labb');
    S(E('line', {x1: kx + 62, y1: ky - 7, x2: kx + 98, y2: ky - 7}, fr), {stroke: 'var(--c4)', strokeWidth: 5, strokeLinecap: 'round'});
    S(E('line', {x1: kx + 282, y1: ky - 22, x2: kx + 282, y2: ky + 16}, fr), {stroke: 'var(--ink-2)', strokeWidth: 2.5});
    [[kx + 108, ['fast local', 'network edge']], [kx + 296, ['ET-Link to', 'the shire cache']], [kx + 496, ['Block diagram,', 'not a floorplan'], 'L114']]
      .forEach(([x, ls, f]) => phSize(T2(fr, x, ky, ls, 't-sm', 'start', f), SK));
  } else {
    // key, in the left margin
    const kx = VB.x + 14, ky = Y + 440;
    T(fr, kx, ky, 'Key', 't-labb');
    S(E('line', {x1: kx, y1: ky + 24, x2: kx + 36, y2: ky + 24}, fr), {stroke: 'var(--c4)', strokeWidth: 5, strokeLinecap: 'round'});
    T2(fr, kx + 46, ky + 30, ['fast local', 'network edge'], 't-sm');
    S(E('line', {x1: kx + 18, y1: ky + 70, x2: kx + 18, y2: ky + 104}, fr), {stroke: 'var(--ink-2)', strokeWidth: 2.5});
    T2(fr, kx + 46, ky + 86, ['ET-Link to', 'the shire cache'], 't-sm');
    T2(fr, kx, ky + 150, ['Block diagram,', 'not a floorplan'], 't-sm', 'start', 'L114');
  }
  // mesh stop
  const gs = comp(L, 'meshstop', {sid}, 'Mesh stop: details');
  boxShape(gs, X + 20, Y + 58, W - 40, 62, 'var(--ink-2)', {fo: 0.07});
  T(gs, X + 36, Y + 97, 'Mesh stop', 't-mid');
  T(gs, X + 180, Y + 97, 'lane = PA[7:6]', 't-sm', 'start', 'L103');
  for (let i = 0; i < 4; i++) {
    const lx = X + W - 40 - (4 - i) * 58 + 6;
    S(E('rect', {x: lx, y: Y + 68, width: 48, height: 42, rx: 4}, gs), {fill: 'var(--page)', stroke: 'var(--ink-2)', strokeWidth: 1.25});
    T(gs, lx + 24, Y + 96, String(i), 't-labb', 'middle', 'L103');
    P.lane[i] = {x: lx + 24, y: Y + 89};
  }
  P.stop = {x: X + W / 2, y: Y + 58};
  // four banks and the UC block; each bank's four sub-banks drawn between its title and its label
  const bw = (500 - 3 * 10) / 4;
  for (let i = 0; i < 4; i++) {
    const bx = X + 20 + i * (bw + 10), by = Y + 134;
    const g = comp(L, 'banks', {bank: i}, `Shire cache bank ${i}: details`);
    boxShape(g, bx, by, bw, 108, 'var(--c1)', {fo: 0.1});
    const sw4 = (bw - 20 - 3 * 4) / 4;
    for (let k = 0; k < 4; k++) S(E('rect', {x: bx + 10 + k * (sw4 + 4), y: by + 42, width: sw4, height: 26, rx: 3}, g), {fill: 'var(--c1)', fillOpacity: 0.12, stroke: 'var(--c1)', strokeOpacity: 0.7, strokeWidth: 1.25});
    T(g, bx + 10, by + 30, `Bank ${i}`, 't-labb');
    T(g, bx + bw / 2, by + 94, '4 sub-banks', 't-sm t-fit', 'middle', 'shire.cache-geometry');
    P.bank[i] = {x: bx + bw / 2, y: by + 54, box: {x: bx, y: by, w: bw, h: 108}};
  }
  const gu = comp(L, 'uc', {}, 'UC block: barriers, credits and atomics: details');
  boxShape(gu, X + 530, Y + 134, W - 550, 108, 'var(--c7)', {fo: 0.1});
  T(gu, X + 544, Y + 164, 'UC block', 't-labb');
  T2(gu, X + 544, Y + 190, ['barriers,', 'credits, atomics'], 't-sm t-fit');
  P.uc = {x: X + 530 + (W - 550) / 2, y: Y + 188};
  // the 4 MB in mode M0: scratchpad, L3 slice, L2
  // (the flows' colour, --c2, is kept for what moves: the L2 is --c5, which no part of a shire uses)
  const parts = [['scp', V('scp_mb'), 'Scratchpad', N.scp_mb.t, 'var(--c4)'], ['l3', V('l3_mb'), 'L3 slice', N.l3_mb.t, 'var(--c3)'], ['l2', V('l2_kb') / 1024, 'L2', N.l2_kb.t, 'var(--c5)']];
  // widths in proportion to the sizes, except the L2, drawn wider (104 units) so that its label fits
  const L2W = 104, rest = parts.filter(p => p[0] !== 'l2').reduce((s, p) => s + p[1], 0);
  let px = X + 20;
  parts.forEach(([k, mb, nm, t, col]) => {
    const w = k === 'l2' ? L2W : (500 - L2W) * mb / rest, g = comp(L, k, {sid}, `${nm}, ${t}: details`);
    boxShape(g, px, Y + 252, w - 4, 46, col, {fo: 0.2, rx: 6});
    if (w > 200) T(g, px + 10, Y + 282, `${nm} · ${t}`, 't-labb', 'start', 'shire.partition-m0');
    else T2(g, px + 8, Y + 271, [{t: nm, c: 't-labb'}, {t, c: 't-sm', f: 'shire.partition-m0'}], '', 'start', null, 1.05);
    P[k] = {x: px + w / 2, y: Y + 275};
    px += w;
  });
  T2(fr, X + 530, Y + 272, ['mode M0 split', 'L2 not to scale'], 't-sm', 'start', 'shire.partition-m0 shire.partition-measured').style.fontSize = PH ? '21px' : '';   // (no room to grow)
  // crossbar
  const gx = comp(L, 'xbar', {}, 'Crossbar: details');
  boxShape(gx, X + 20, Y + 308, W - 40, 30, 'var(--ink-2)', {fo: 0.07, rx: 6});
  T(gx, X + W / 2, Y + 330, `crossbar · ${N.xbar512.t} ET-Link buses`, 't-sm', 'middle', 'shire.crossbar');
  P.xbarY = Y + 323;
  // four neighbourhoods of eight minions, in the core-et floorplan order (fact L115)
  const LEFT = LAY.neighbourhood_floorplan.left_column_n_to_s.map(s => +s.slice(1)), RIGHT = LAY.neighbourhood_floorplan.right_column_n_to_s.map(s => +s.slice(1));
  const nw = (W - 40 - 3 * 12) / 4;
  for (let k = 0; k < 4; k++) {
    const nx = X + 20 + k * (nw + 12), ny = Y + 352, nh = 330;
    const G = E('g', {}, L);
    const gn = comp(G, 'neigh', {nb: k}, `Neighbourhood ${k}: details`);
    boxShape(gn, nx, ny, nw, nh, 'var(--c1)', {fo: 0.05});
    T(gn, nx + nw / 2, ny + 28, `Neighbourhood ${k}`, 't-sm t-fit', 'middle');
    // link up to the crossbar through the neighbourhood channel
    S(E('line', {x1: nx + nw / 2, y1: ny, x2: nx + nw / 2, y2: Y + 338}, G), {stroke: 'var(--ink-2)', strokeWidth: 2.5});
    const pos = {};
    [LEFT, RIGHT].forEach((col, ci) => col.forEach((m, ri) => {
      pos[m] = {x: nx + 8 + ci * 74, y: ny + 46 + ri * 70, w: 66, h: 44};
    }));
    for (let m = 0; m < 8; m++) {
      const p = pos[m], g = comp(G, 'minion', {sid, nb: k, mi: m}, `Minion ${m} of neighbourhood ${k}: details; Enter zooms in`);
      boxShape(g, p.x, p.y, p.w, p.h, 'var(--c1)', {fo: 0.22, rx: 6});
      T(g, p.x + p.w / 2, p.y + 30, 'M' + m, 't-labb', 'middle');
      P.min[k + ':' + m] = p; P.minG[k + ':' + m] = g;
    }
    // tree edges of the fast local network, drawn over the minions' edges (fact L115); each edge's ends are kept, so
    // that the allreduce (flow 0) recolours the edge itself
    P.fe = P.fe || {};
    LAY.neighbourhood_floorplan.fast_tree_edges.forEach(([a, b]) => {
      const A = pos[a], B = pos[b], hz = A.y === B.y, s1 = A.x < B.x || A.y < B.y ? A : B, s2 = s1 === A ? B : A;
      const q = hz ? {x1: s1.x + s1.w - 10, y1: s1.y + s1.h / 2, x2: s2.x + 10, y2: s2.y + s2.h / 2} : {x1: s1.x + s1.w / 2, y1: s1.y + s1.h - 9, x2: s2.x + s2.w / 2, y2: s2.y + 9};
      const pa = s1 === A ? {x: q.x1, y: q.y1} : {x: q.x2, y: q.y2}, pb = s1 === A ? {x: q.x2, y: q.y2} : {x: q.x1, y: q.y1};
      P.fe[k + ':' + a + '-' + b] = [pa, pb]; P.fe[k + ':' + b + '-' + a] = [pb, pa];
      S(E('line', Object.assign(q, {class: 'fln-e', 'pointer-events': 'none'}), G), {stroke: 'var(--c4)', strokeWidth: 5, strokeLinecap: 'round'});
    });
    P['ch' + k] = {x: nx + nw / 2, y: ny + 6};
    P.nbx[k] = {x: nx, y: ny, w: nw, h: nh};
  }
  FX[1] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}

/* ---- a minion, zoomed in ---- */
function buildMinion(sid, nb, mi) {
  const L = LAYERS[2]; L.textContent = ''; AP[2] = {regs: [[], []], units: [], scp: []};
  const P = AP[2], X = MF.x, Y = MF.y, W = MF.w, H = MF.h, h0 = sid * 64 + (nb * 8 + mi) * 2;
  S(E('rect', {class: 'zbd', x: X, y: Y, width: W, height: H, rx: 14, 'pointer-events': 'none'}, L), {fill: 'var(--page)'});
  const fr = E('g', {}, L);
  S(E('rect', {x: X, y: Y, width: W, height: H, rx: 14}, fr), {fill: 'var(--c1)', fillOpacity: 0.04, stroke: 'var(--c1)', strokeWidth: 2.5});
  T(fr, X + 24, Y + 44, `Minion ${mi} · neighbourhood ${nb} · shire ${sid}`, 't-big');
  T(fr, X + W - 24, Y + 42, `harts ${h0} and ${h0 + 1}`, 't-lab m-harts', 'end', 'chip.harts');   // hidden while a flow's note sits there
  // two harts
  [0, 1].forEach(t => {
    const hy = Y + 70 + t * 240, g = comp(L, 'hart', {t}, `Hart ${t}: details`);
    boxShape(g, X + 24, hy, 320, 228, 'var(--c1)', {fo: 0.08});
    T(g, X + 40, hy + 34, `Hart ${t}`, 't-mid');
    if (t === 0) T(g, X + 40, hy + 62, 'issues every tensor instruction', 't-sm', 'start', 'minion.tensor-hart0');
    else T2(g, X + 40, hy + 60, ['tensor: only TensorLoadL2Scp,', 'TensorWait and tensor_coop'], 't-sm', 'start', 'minion.tensor-hart0');
    for (let i = 0; i < 32; i++) {
      const rx = X + 40 + (i % 8) * 36, ry = hy + 94 + Math.floor(i / 8) * 25;
      P.regs[t].push(S(E('rect', {x: rx, y: ry, width: 32, height: 21, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.25, stroke: 'var(--c1)', strokeWidth: 1.25}));
    }
    T(g, X + 40, hy + 214, `f0–f31, ${N.vreg256.t}`, 't-sm', 'start', 'minion.vpu');
    P['hart' + t] = {x: X + 184, y: hy + 130};
    P['hart' + t + 'e'] = {x: X + 344, y: hy + 44};   // the box's right edge, beside its name: where a request leaves it
  });
  // integer pipeline (the core itself)
  const gi = comp(L, 'minion', {}, 'The minion core: details');
  boxShape(gi, X + 364, Y + 70, 410, 84, 'var(--ink-2)', {fo: 0.07});
  T(gi, X + 380, Y + 104, 'Integer pipeline', 't-mid');
  T(gi, X + 380, Y + 136, 'RV64IMFC · in-order · single issue', 't-sm', 'start', 'minion.isa');
  P.core = {x: X + 569, y: Y + 112};
  // vector unit: its 8 lanes hold the FMA and int8 multiply-add units that the tensor instructions also run on
  const gv = comp(L, 'vpu', {}, 'Vector unit: details');
  boxShape(gv, X + 364, Y + 166, 410, 372, 'var(--c3)', {fo: 0.08});
  T(gv, X + 380, Y + 200, `Vector unit · ${N.lanes_n.t} lanes`, 't-mid', 'start', 'minion.vpu');
  const lw = (410 - 24 - 7 * 6) / 8, UN = ['FMA', 'IMA', 'IMA', 'INT', 'TR'];
  UN.forEach(() => P.units.push([]));
  for (let l = 0; l < 8; l++) {
    const lx = X + 376 + l * (lw + 6);
    T(gv, lx + lw / 2, Y + 230, String(l), 't-sm', 'middle');
    UN.forEach((u, k) => {
      const uy = Y + 238 + k * 46;
      P.units[k].push(S(E('rect', {x: lx, y: uy, width: lw, height: 40, rx: 4, 'pointer-events': 'none'}, gv), {fill: 'var(--c3)', fillOpacity: k < 3 ? 0.3 : 0.14, stroke: 'var(--c3)', strokeWidth: 1.25}));
      T(gv, lx + lw / 2, uy + 26, u, 't-unit', 'middle');
    });
  }
  P.laneX = l => X + 376 + l * (lw + 6) + lw / 2; P.unitY = k => Y + 238 + k * 46 + 20;
  T2(gv, X + 380, Y + 482, [{t: 'FMA · 2× int8 MA · integer · transcendental', c: 't-sm t-fit', f: 'minion.vpu'}, {t: `peak ${N.vecpeak.t} per cycle, fp32,`, c: 't-labb', f: 'minion.vec-peak'},
    {t: 'the same for vector and tensor', c: 't-sm', f: 'minion.vec-peak'}], '', 'start', null, 1.1);
  P.vpu = {x: X + 569, y: Y + 350};
  // the tensor sequencer: state machines in the VPU that run TensorFMA and TensorIMA on the lanes (fact minion.vec-peak).
  // The tensor path is one colour, --c7, like the L1 tensor scratchpad; --c2 is kept for what moves
  const gt = comp(L, 'tensor', {}, 'Tensor sequencer: details');
  const tx = X + 794, tw = W - 24 - 794;
  boxShape(gt, tx, Y + 70, tw, 468, 'var(--c7)', {fo: 0.07});
  T(gt, tx + 16, Y + 104, 'Tensor sequencer', 't-mid', 'start', 'minion.vec-peak');
  S(E('rect', {x: tx + 16, y: Y + 118, width: tw - 32, height: 100, rx: 6, 'pointer-events': 'none'}, gt), {fill: 'var(--c7)', fillOpacity: 0.12, stroke: 'var(--c7)', strokeWidth: 1.25});
  T(gt, tx + 30, Y + 148, 'TensorFMA · TensorIMA', 't-labb');
  T(gt, tx + 30, Y + 174, 'C += A · B', 't-sm');
  T(gt, tx + 30, Y + 198, N.tshape.t, 't-sm', 'start', 'minion.tensor-shape');
  P.seq = {x: tx + tw / 2, y: Y + 168};
  // the arrow into the lanes: the tensor work runs there
  const ay = Y + 250;
  P.arrow = S(E('line', {x1: tx + 46, y1: ay, x2: X + 774, y2: ay, 'pointer-events': 'none'}, gt), {stroke: 'var(--c7)', strokeWidth: 4, strokeLinecap: 'round'});
  S(E('polygon', {points: `${X + 760},${ay} ${X + 778},${ay - 10} ${X + 778},${ay + 10}`, 'pointer-events': 'none'}, gt), {fill: 'var(--c7)'});
  T(gt, tx + 56, ay + 6, 'runs on the 8 VPU lanes', 't-sm', 'start', 'minion.vec-peak');
  [['TenB', 0, '(logical)'], ['TenC', 1, '']].forEach(([nm, i, q]) => {
    const bx = tx + 16 + i * ((tw - 32) / 2 + 4), bwid = (tw - 40) / 2;
    S(E('rect', {x: bx, y: Y + 286, width: bwid, height: 84, rx: 6, 'pointer-events': 'none'}, gt), {fill: 'var(--c7)', fillOpacity: 0.08, stroke: 'var(--c7)', strokeWidth: 1.25});
    T2(gt, bx + 12, Y + 314, [{t: nm, c: 't-labb'}, {t: N.tenb.t, c: 't-sm', f: 'minion.tenb-tenc'}].concat(q ? [{t: q, c: 't-sm', f: 'minion.tenb-tenc'}] : []), '', 'start', null, 1.12);
    P[nm.toLowerCase()] = {x: bx, y: Y + 286, w: bwid, h: 84};
  });
  T2(gt, tx + 16, Y + 396, [{t: 'tensor peak per cycle,', c: 't-sm'}, {t: 'on those lanes:', c: 't-sm'}, {t: `${N.peak32.t} · ${N.peak16.t}`, c: 't-labb', f: 'mm-peak'},
    {t: `${N.peak8.t} ops`, c: 't-labb', f: 'mm-peak'}, {t: `chip: ${N.tflops.t} TFLOP/s fp32`, c: 't-sm', f: 'mm-rate'}, {t: 'measured, three cards', c: 't-sm', f: 'mm-rate'}], '', 'start', null, 1.16);
  P.tensor = {x: tx + tw / 2, y: Y + 170};
  // L1 data cache: 16 sets, as the firmware leaves them (sets 0-11 tensor scratchpad, 12-13 hart 0, 14-15 hart 1)
  const gl = comp(L, 'l1d', {}, 'L1 data cache: details');
  boxShape(gl, X + 24, Y + 552, 750, 186, 'var(--c1)', {fo: 0.06});
  T(gl, X + 40, Y + 584, `L1 data cache · ${N.l1_kb.t} · as the firmware sets it`, 't-labb', 'start', 'minion.l1d minion.l1-firmware');
  const sw = (750 - 32 - 15 * 4) / 16, sx = k => X + 40 + k * (sw + 4), sy = Y + 600;
  for (let k = 12; k < 16; k++) S(E('rect', {x: sx(k), y: sy, width: sw, height: 64, rx: 4, 'pointer-events': 'none'}, gl), {fill: 'var(--c1)', fillOpacity: k < 14 ? 0.35 : 0.18, stroke: 'var(--c1)', strokeWidth: 1.25});
  T2(gl, sx(12), sy + 90, ['hart 0', N.l1_hart.t], 't-sm', 'start', 'minion.l1-modes minion.l1-firmware');
  T2(gl, sx(14), sy + 90, ['hart 1', N.l1_hart.t], 't-sm', 'start', 'minion.l1-modes minion.l1-firmware');
  const gp = comp(L, 'l1scp', {}, 'L1 tensor scratchpad: details');
  S(E('rect', {class: 'shape', x: sx(0) - 3, y: sy - 3, width: sx(11) + sw - sx(0) + 6, height: 70, rx: 6}, gp), {fill: 'transparent', stroke: 'var(--c7)', strokeWidth: 2});
  E('rect', {class: 'ring', x: sx(0) - 8, y: sy - 8, width: sx(11) + sw - sx(0) + 16, height: 80, rx: 9}, gp);
  for (let k = 0; k < 12; k++) S(E('rect', {x: sx(k), y: sy, width: sw, height: 64, rx: 4}, gp), {fill: 'var(--c7)', fillOpacity: 0.25, stroke: 'var(--c7)', strokeWidth: 1.25});
  T(gp, sx(0), sy + 90, `${N.sets011.t}: tensor scratchpad, ${N.l1_scp.t}`, 't-sm', 'start', 'minion.l1-modes');
  P.scpBox = {x: sx(0), y: sy, w: sx(11) + sw - sx(0), h: 64};
  P.l1h0 = {x: sx(12) + sw + 2, y: sy + 32};
  // ports
  const ge = comp(L, 'etlink', {}, 'ET-Link port: details');
  boxShape(ge, tx, Y + 552, tw, 96, 'var(--ink-2)', {fo: 0.07});
  T(ge, tx + 16, Y + 582, 'ET-Link port', 't-labb');
  T2(ge, tx + 16, Y + 607, [`to the shire cache: ${N.etl_min.t},`, `onto a shared ${N.etl512.t.replace(' ET-Link bus', '')} bus`], 't-sm', 'start', 'minion.etlink-width shire.neigh-link');
  P.etl = {x: tx + tw - 110, y: Y + 580};
  P.etlPort = {x: tx, y: Y + 600};   // the port's edge, where a request leaves the minion (over no text)
  const gf = comp(L, 'fln', {}, 'Fast local network: details');
  boxShape(gf, tx, Y + 658, tw, 80, 'var(--c4)', {fo: 0.1});
  T(gf, tx + 16, Y + 690, 'Fast local network', 't-labb');
  T(gf, tx + 16, Y + 716, `${N.ts_fln.t} round trip on tree edges`, 't-sm t-fit', 'start', 'ts-rt-fln');
  P.fln = {x: tx + tw - 110, y: Y + 700};
  FX[2] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}

/* ---- the small picture of the die: what a stage on the die looks like while the camera is inside ---- */
const PIP = {el: $('pip'), svg: $('pipsvg'), fx: null, tiles: {}, on: false};
function buildPip() {
  const s = PIP.svg, V0 = PH ? PV[0] : VB; s.setAttribute('viewBox', `${V0.x} ${V0.y} ${V0.w} ${V0.h}`);
  S(E('rect', {x: V0.x, y: V0.y, width: V0.w, height: V0.h}, s), {fill: 'var(--page)'});
  [[0, 1], [2, 3], [4, 5], [6, 7]].forEach(ms => {
    const a = MSC[ms[0]], b = MSC[ms[1]], west = a.c === 0, x = pkgX(west);
    S(E('rect', {x, y: a.y + 8, width: PKW, height: b.y + b.h - 16 - a.y, rx: 6}, s), {fill: 'var(--c3)', fillOpacity: 0.16, stroke: 'var(--c3)', strokeWidth: 3, strokeDasharray: '10 8'});
  });
  S(E('rect', {x: 0, y: 0, width: DW, height: DH, rx: 10}, s), {fill: 'var(--surface)', stroke: 'color-mix(in srgb, var(--ink-2) 55%, var(--surface))', strokeWidth: 3});
  const hb = AP[0].hostBox, pc = CELLS.find(c => c.type === 'pcie');
  S(E('path', {d: `M${pc.sx},${pc.y + INS} V${hb.ly} H${hb.x}`, fill: 'none'}, s), {stroke: 'var(--c4)', strokeWidth: 5});
  S(E('rect', {x: hb.x, y: hb.y, width: hb.w, height: hb.h, rx: 6}, s), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 3});
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hops(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly)) mlink(s, a.sx, a.sy, b.sx, b.sy);
  }));
  CELLS.forEach(c => {
    PIP.tiles[c.r + ',' + c.c] = S(E('rect', {class: 'pt', x: c.x + INS, y: c.y + INS, width: c.w - 2 * INS, height: c.h - 2 * INS, rx: 6}, s),
      {fill: COL[c.type], fillOpacity: 0.16, stroke: COL[c.type], strokeWidth: 3});
  });
  PIP.fx = E('g', {class: 'fx'}, s);
}

/* ================= the animation clock: everything that moves runs on it, and Space stops it ================= */
const CLK = {t: 0, on: true, last: 0, dt: 0, jobs: new Set()};
(function loop(now) {
  const dt = CLK.last ? Math.min(80, now - CLK.last) : 0; CLK.last = now; CLK.dt = dt;   // dt: this frame, paused or not
  if (CLK.on) CLK.t += dt;
  CLK.jobs.forEach(j => { try { j(); } catch (e) { CLK.jobs.delete(j); console.error(e); } });
  requestAnimationFrame(loop);
})(0);
const CANCEL = new Error('cancelled');
const alive = tok => { if (tok.dead) throw CANCEL; };
/* a token's wait and animation: on the clock; under tok.ff (drawing a stage's end state) at once */
function wait(tok, ms) {
  return new Promise((res, rej) => {
    if (tok.dead) return rej(CANCEL);
    if (tok.ff || ms <= 0) return res();
    const t0 = CLK.t, j = () => { if (tok.dead) { CLK.jobs.delete(j); rej(CANCEL); } else if (CLK.t - t0 >= ms) { CLK.jobs.delete(j); res(); } };
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
    const t0 = CLK.t, j = () => {
      if (tok.dead) { CLK.jobs.delete(j); rej(CANCEL); return; }
      const p = Math.min(1, (CLK.t - t0) / ms); fn(p);
      if (p >= 1) { CLK.jobs.delete(j); res(); }
    };
    CLK.jobs.add(j); j();
  });
}
function every(tok, fn) { const j = () => { if (tok.dead) CLK.jobs.delete(j); else fn(CLK.t); }; CLK.jobs.add(j); }
const quiet = p => p.catch(e => { if (e !== CANCEL) console.error(e); });
/* the token whose earlier stages are being drawn as end states (runFrom): what they draw appears at once, so that a
   chart or a callout that stays from stage to stage does not blink when the reader steps */
let FFTOK = null, FFEND = 0;
const noFade = () => !!(FFTOK && FFTOK.ff && !FFTOK.dead);
const easeOut = p => 1 - (1 - p) * (1 - p);
/* an element fading in on the clock (a callout, a label), with an ease out and, given rise, a short rise: nothing pops.
   At the end its inline opacity is cleared, so that the zoom's label fade (CSS) applies to it */
function fadeIn(el, ms, rise) {
  if (el && noFade()) el._ffAt = performance.now();   // drawn as an end state (see fadeOut)
  if (!el || REDUCED || !CLK.on || noFade()) return el;   // paused, or a stage's end state: shown at once
  el.style.opacity = 0; const t0 = CLK.t, d = ms || 320;
  const j = () => {
    const p = Math.min(1, (CLK.t - t0) / d), e = easeOut(p);
    el.style.opacity = e; if (rise) el.setAttribute('transform', `translate(0,${(rise * (1 - e)).toFixed(2)})`);
    if (p >= 1 || !el.isConnected) { CLK.jobs.delete(j); el.style.opacity = ''; if (rise) el.removeAttribute('transform'); }
  };
  CLK.jobs.add(j);
  return el;
}
/* an element fading out, then removed (a callout that a stage replaces) */
function fadeOut(el, ms) {
  if (!el) return;
  // drawn as a skipped stage's end state a moment ago (the reader stepped on): it goes at once, never flashes
  if (REDUCED || !CLK.on || noFade() || !el.isConnected || (el._ffAt && performance.now() - el._ffAt < 250) || performance.now() - FFEND < 250) { el.remove(); return; }
  const t0 = CLK.t, d = ms || 180, o0 = +(el.style.opacity || 1);
  el.style.pointerEvents = 'none';
  const j = () => { const p = Math.min(1, (CLK.t - t0) / d); el.style.opacity = (o0 * (1 - p)).toFixed(3); if (p >= 1 || !el.isConnected) { CLK.jobs.delete(j); el.remove(); } };
  CLK.jobs.add(j);
}
/* a packet grows in from 0.4 of its size (180 ms, ease out) */
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

/* ================= the camera ================= */
const Z = {level: 0, sid: null, nb: 0, mi: 0};
let LASTSID = 0, LASTNB = 0, LASTMI = 0;
const lerp = (a, b, t) => a + (b - a) * t;
const lerpR = (A, B, t) => ({x: lerp(A.x, B.x, t), y: lerp(A.y, B.y, t), w: lerp(A.w, B.w, t), h: lerp(A.h, B.h, t)});
/* a sine in and out, for what eases in the view (a trail, a glow): its top speed is 1.57 times its mean */
const easeS = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const band = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rmap = (A, B) => { const k = B.w / A.w; return [k, B.x - k * A.x, B.y - k * A.y]; };
const setT = (g, m) => { if (m) g.setAttribute('transform', `matrix(${m[0]},0,0,${m[0]},${m[1]},${m[2]})`); else g.removeAttribute('transform'); };
/* a pure zoom: the frame's width moves geometrically (a steady rate on a log scale) and its place with it, so the
   point where the two frames coincide stays put */
const zoomR = (A, B, e) => { const w = A.w * Math.pow(B.w / A.w, e); return lerpR(A, B, (w - A.w) / (B.w - A.w)); };
const tileRect = sid => { const c = SH[sid]; return {x: c.x + INS, y: c.y + INS, w: c.w - 2 * INS, h: c.h - 2 * INS}; };
const minRect = (nb, mi) => { const p = AP[1].min[nb + ':' + mi]; return {x: p.x, y: p.y, w: p.w, h: p.h}; };
/* a point of an inner view in its parent's coordinates: where a packet sits once the zoom has shrunk its view */
const mapOut = (A, B, p) => ({x: A.x + (p.x - B.x) * A.w / B.w, y: A.y + (p.y - B.y) * A.w / B.w});
const outOfMinion = (p, nb, mi) => mapOut(minRect(nb, mi), MF, p);
const outOfShire = (p, sid) => mapOut(tileRect(sid), SF, p);
/* While the camera moves between a view and the one inside it, the outer view is scaled up: its strokes keep their
   width on the screen (mesh links, the fast network's edges never swell into bars). */
function strokeKeeper(layer) {
  const list = [];
  layer.querySelectorAll('line, rect, path, circle, polygon').forEach(el => {
    const cs = getComputedStyle(el); if (!cs.stroke || cs.stroke === 'none') return;
    const w = parseFloat(cs.strokeWidth); if (w > 0) list.push([el, w, el.style.strokeWidth]);
  });
  let last = 1;
  return {
    set: k => { k = Math.max(1, k); if (Math.abs(Math.log(k / last)) < 0.1 && !(k === 1 && last !== 1)) return; last = k; list.forEach(([el, w]) => { el.style.strokeWidth = (w / k).toFixed(3) + 'px'; }); },
    done: () => list.forEach(([el, , s0]) => { el.style.strokeWidth = s0; }),
  };
}
/* the zoom's context: every part of a view but the target (the tile or the minion being entered or left, which stays
   as the frame), the fx group (a flow's drawing) and the backdrop excepted. Without a target, every part */
function ctxList(layer, tgt) {
  const out = [], take = s => { if (s !== tgt && !s.classList.contains('fx') && !s.classList.contains('zbd')) out.push(s); };
  if (!tgt) { [...layer.children].forEach(take); return out; }
  let el = tgt;
  while (el && el !== layer && el.parentNode) {
    const p = el.parentNode;
    [...p.children].forEach(s => { if (s !== el) take(s); });
    el = p;
  }
  return out;
}
function ctxClear(layer) {
  layer.querySelectorAll('.zdim, .ztgt, .zhi').forEach(e => e.classList.remove('zdim', 'ztgt', 'zhi'));
  layer.classList.remove('zsat');
  ['--lab', '--ctx', '--sat', '--ctxh', '--tgt', '--tsat'].forEach(k => layer.style.removeProperty(k));
}
/* how set back a view looks: a tour step's highlight (CSS #chip.dimming) and a flow's (#chip.fdim), opacity and
   saturation; a zoom out that ends on such a view ends at that look, so that nothing brightens and dims again */
const isDark = () => { const t = document.documentElement.dataset.theme; if (t === 'dark' || t === 'light') return t === 'dark'; try { return matchMedia('(prefers-color-scheme: dark)').matches; } catch (_) { return false; } };
const FULL = {o: 1, s: 1};
const DIMLOOK = {dimming: () => ({o: isDark() ? 0.45 : 0.35, s: 0.15}), fdim: () => ({o: isDark() ? 0.6 : 0.55, s: 0.3})};
/* how an element looks now, a transition in flight included: a zoom starts from exactly what is on the screen */
function lookOf(el) {
  if (!el) return FULL;
  const cs = getComputedStyle(el), o = parseFloat(cs.opacity), m = /saturate\(([\d.]+)\)/.exec(cs.filter || '');
  return {o: o >= 0 && o <= 1 ? o : 1, s: m ? Math.min(1, +m[1]) : 1};
}
const CTX_LOW = 0.3;
/* ---- the phone's view (PH) ----
   The drawing's box keeps one shape (phBox): idle, as tall as the tallest scale's view; while a flow or the tour plays,
   taller by the band under the die that a flow's charts fold into (FOLD.R units, the same for every flow, so that the
   box keeps its size through the tour). A view shorter than the box sits at its top (preserveAspectRatio xMidYMin): the
   folded charts sit under the die, and the small picture of the die (the pip, bottom right) under a shire or a minion.
   The SVG's viewBox is the box's shape, 1000 units wide; a view r is part of the transform of the layer shown (viewM:
   r's width on the box's, r's top at its top). A zoom moves it from one scale's view to the next in the transforms
   the camera sets anyway (segOpen): the box's size, its viewBox and the page's layout never change during a zoom (a
   viewBox changed at each frame would lay the page out again at each frame). */
const PHV = {flow: false, extra: 0, ar: ''};
/* the fold: parts scaled by up to K (at least KMIN, else the band grows for the flow: PHV.extra), their top FOLD.top */
const FOLD = {K: 1.4, KMIN: 1.15, top: DH + 60, gap: 36, R: 420, pad: 18};
const bandH = () => FOLD.R + PHV.extra;
const pview = lv => (lv === 0 && PHV.flow ? Object.assign({}, PV[0], {h: PV[0].h + bandH()}) : PV[lv]);
const viewM = r => { const k = 1000 / r.w; return [k, -k * r.x, -k * r.y]; };
const cmpM = (V, M) => (!V ? M : !M ? V : [V[0] * M[0], V[0] * M[1] + V[1], V[0] * M[2] + V[2]]);
/* the view r, on the layer at rest (the one shown) */
function setView(r) { setT(LAYERS[Z.level], viewM(r)); }
/* the box's shape (the tallest view's, the die's with its band while a flow or the tour plays): set when a flow or the
   tour starts or stops, and when a flow's charts outgrow the band; never during a zoom */
function phBox() {
  if (!PH) return;
  const flow = !!(TOUR || FL.k);
  if (flow !== PHV.flow) { PHV.flow = flow; PHV.extra = 0; }
  const hw = Math.max(...[0, 1, 2].map(lv => { const r = pview(lv); return r.h / r.w; }));
  const H = (1000 * hw).toFixed(1), ar = `1000 / ${H}`;
  if (ar !== PHV.ar) { PHV.ar = ar; svg.style.aspectRatio = ar; svg.setAttribute('viewBox', `0 0 1000 ${H}`); }
  if (!ZW) setView(pview(Z.level));
}
/* The charts a flow draws right of the die (the band, BAND), and the callouts that stand there, fold under the die on
   a phone, into the band the box keeps for them: each part scaled by K, in one column where it fits at FOLD.K, else in
   the two columns (a column breaks only between parts that do not overlap in height) that fit it largest. Each part
   keeps its place in the drawing (a stage's code finds it as before); only its CSS transform moves it. */
function bandFold() {
  if (!PH || !FX[0] || LAYERS[0].style.display === 'none') return;
  const atoms = [], bb = el => { try { const b = el.getBBox(); return b.width || b.height ? b : null; } catch (_) { return null; } };
  // a part: a chart's title, note or row (they keep their places in the chart: g, the chart), or a callout
  const take = (el, g) => { const b = bb(el); if (b) atoms.push({el, g: g || el, x: b.x, y: b.y, w: b.width, h: b.height}); };
  const scan = (box, deep) => [...box.children].forEach(ch => {
    const cl = ch.classList;
    if (cl.contains('band')) { [...ch.children].forEach(el => take(el, ch)); return; }
    if (ch.tagName !== 'g' || cl.contains('pk')) return;
    const b = bb(ch); if (!b) return;
    if (b.x >= BANDX) take(ch); else if (deep && cl.contains('co') && ch.querySelector(':scope > .band')) scan(ch, false);
  });
  scan(FX[0], true);
  if (!atoms.length) return;
  // each chart (or callout) starts at its column's left edge
  const gx = new Map(); atoms.forEach(a => gx.set(a.g, Math.min(a.x, gx.has(a.g) ? gx.get(a.g) : Infinity)));
  const wOf = col => Math.max(...col.map(a => a.x + a.w - gx.get(a.g)));
  atoms.sort((a, b) => a.y - b.y);
  const y0 = atoms[0].y, y1 = Math.max(...atoms.map(a => a.y + a.h));
  const avail = PV[0].w - 44, off = FOLD.top - (PV[0].y + PV[0].h);
  const kOf = o => Math.min(FOLD.K, (bandH() - off - FOLD.pad) / o.hh, (avail - o.gap) / o.ww);
  let best = {cols: [atoms], hh: y1 - y0, ww: wOf(atoms), gap: 0}; best.k = kOf(best);
  if (best.k < FOLD.K - 1e-6) {
    let bot = -Infinity;
    for (let i = 0; i < atoms.length - 1; i++) {
      bot = Math.max(bot, atoms[i].y + atoms[i].h);
      if (atoms[i + 1].y < bot - 0.5) continue;
      const c1 = atoms.slice(0, i + 1), c2 = atoms.slice(i + 1), o = {cols: [c1, c2], hh: Math.max(bot - y0, y1 - atoms[i + 1].y), ww: wOf(c1) + wOf(c2), gap: FOLD.gap};
      o.k = kOf(o);
      if (o.k > best.k + 1e-6 || (Math.abs(o.k - best.k) < 1e-6 && o.hh < best.hh)) best = o;
    }
  }
  let K = best.k;
  if (K < FOLD.KMIN) {
    // too tall for the band even at KMIN: the band grows, for as long as the flows play (one step, never back)
    K = Math.min(FOLD.KMIN, (avail - best.gap) / best.ww);
    const need = off + best.hh * K + FOLD.pad;
    if (need > bandH() + 1) { PHV.extra = Math.ceil(need - FOLD.R); phBox(); }
  }
  let x = PV[0].x + 22;
  best.cols.forEach(col => {
    const top = Math.min(...col.map(a => a.y)), ty = FOLD.top - K * top;
    col.forEach(a => { const tx = x - K * gx.get(a.g); a.el.style.transform = `translate(${tx.toFixed(1)}px,${ty.toFixed(1)}px) scale(${K.toFixed(3)})`; });
    x += wOf(col) * K + FOLD.gap;
  });
}
let foldT = 0;
function foldSoon() { if (!foldT) foldT = requestAnimationFrame(() => { foldT = 0; bandFold(); }); }
/* the step in flight between two views, left partway by a newer request: the next plan goes on from there */
let CUR = null;
/* One zoom segment between LAYERS[lo] (the outer view) and LAYERS[lo + 1] (the inner one): e = 0 shows the outer view,
   e = 1 the inner. A semantic zoom, the same both ways:
   - the outer view's labels go first (none is ever seen blown up), and its context is set back (to 0.3) while the
     target grows into the frame; the target itself comes up to full strength;
   - the inner view, on an opaque backdrop the size of its frame, comes in over the target early (e 0.10-0.32), so
     that the tile turns into the view inside it and no frame is ever empty;
   - the outer view's context stays, set back, until the zoom has pushed it off the screen (e 0.86-1);
   - the inner view's labels come last, once they are readable (e 0.62-0.88).
   A view the camera only passes through (sg.midOut, sg.midIn: the shire on the way from the chip to a minion) shows
   no labels and keeps its context set back, so that it does not flicker up at the camera's top speed. A view the
   camera rests at starts from how it looks (a tour step's or a flow's dimming, measured) or ends at the look it will
   have (sg.end), so that nothing brightens for a moment. */
function segOpen(sg, req) {
  const lo = sg.lo, outer = LAYERS[lo], inner = LAYERS[lo + 1], B = lo === 0 ? SF : MF;
  const A = lo === 0 ? tileRect(Z.sid) : minRect(Z.nb, Z.mi);
  const tgt = lo === 0 ? (SH[Z.sid] && SH[Z.sid].g) : (AP[1].minG && AP[1].minG[Z.nb + ':' + Z.mi]);
  const P = {midOut: !!sg.midOut, midIn: !!sg.midIn};
  let rest = FULL, tRest = FULL, his = [];
  const sibs = ctxList(outer, tgt);
  if (P.midOut) rest = tRest = {o: CTX_LOW, s: 1};
  else if (sg.dir > 0) {
    // the view the camera leaves, as it looks now (measured before any of the zoom's marks go on)
    const looks = sibs.map(lookOf);
    rest = looks.reduce((m, l) => (l.o < m.o ? l : m), FULL);
    tRest = lookOf(tgt);
    his = sibs.filter((s, i) => looks[i].o > rest.o + 0.1);
    clearDim();
  } else rest = tRest = sg.end || FULL;
  ctxClear(outer); ctxClear(inner);
  sibs.forEach(s => s.classList.add('zdim')); his.forEach(s => s.classList.add('zhi'));
  if (tgt) tgt.classList.add('ztgt');
  if (P.midIn) ctxList(inner, null).forEach(s => s.classList.add('zdim'));
  const keep = strokeKeeper(outer);
  // a flow's packet rides the zoom at its own size, above both views, so that it never fades out between two legs
  let cg = null, p0 = null, inOuter = false;
  const carry = req.o.carry;
  if (carry && carry.isConnected && !REDUCED && !(req.o.total === 0)) {
    const li = LAYERS.indexOf(carry.closest('.lay')), m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(carry.getAttribute('transform') || '');
    if (m && (li === lo || li === lo + 1)) { p0 = {x: +m[1], y: +m[2]}; inOuter = li === lo; cg = carry.cloneNode(true); svg.appendChild(cg); carry.style.visibility = 'hidden'; }
  }
  const frame = e => {
    // (on a phone the view, moving from one scale's to the next, is part of both transforms)
    const R = zoomR(A, B, e), Mo = rmap(A, R), Mi = rmap(B, R), V = PH ? viewM(lerpR(pview(lo), pview(lo + 1), e)) : null;
    setT(outer, cmpM(V, Mo)); setT(inner, cmpM(V, Mi));
    const oo = 1 - band(e, 0.86, 1), k = easeS(band(e, 0, 0.3)), so = outer.style;
    so.opacity = oo; so.visibility = oo > 0 ? '' : 'hidden';
    inner.style.opacity = band(e, 0.1, 0.32);
    so.setProperty('--lab', P.midOut ? '0' : (1 - band(e, 0.02, 0.2)).toFixed(3));
    so.setProperty('--ctx', lerp(rest.o, CTX_LOW, k).toFixed(3));
    so.setProperty('--sat', lerp(rest.s, 1, k).toFixed(3));
    so.setProperty('--ctxh', lerp(1, CTX_LOW, k).toFixed(3));
    so.setProperty('--tgt', lerp(tRest.o, 1, k).toFixed(3));
    so.setProperty('--tsat', lerp(tRest.s, 1, k).toFixed(3));
    outer.classList.toggle('zsat', (rest.s < 0.999 || tRest.s < 0.999) && k < 0.999);
    inner.style.setProperty('--lab', P.midIn ? '0' : band(e, 0.62, 0.88).toFixed(3));
    inner.style.setProperty('--ctx', String(CTX_LOW));
    if (oo > 0) keep.set(Mo[0]);
    if (cg) {
      const M = cmpM(V, inOuter ? Mo : Mi), q = {x: M[0] * p0.x + M[1], y: M[0] * p0.y + M[2]};
      if (V) cg.setAttribute('transform', `translate(${q.x.toFixed(1)},${q.y.toFixed(1)}) scale(${V[0].toFixed(4)})`); else at(cg, q);
    }
  };
  // the first frame goes on before either view is shown: a view un-hidden at full size and full opacity would be
  // painted for one frame
  frame(sg.e0);
  outer.style.display = ''; inner.style.display = '';
  LAYERS.forEach(l => l.classList.add('busy'));
  outer.classList.add('zout');
  return {
    lo, P, frame,
    /* a plan redirected mid-step: what the views on either side are now (only the flags change) */
    update: s => { P.midOut = !!s.midOut; P.midIn = !!s.midIn; },
    close: (e1, last, arrive) => {
      frame(e1);
      if (cg) { cg.remove(); carry.style.visibility = ''; }
      keep.done();
      outer.classList.remove('zout'); outer.style.visibility = '';
      const inIn = e1 >= 1, here = inIn ? inner : outer, gone = inIn ? outer : inner;
      gone.style.display = 'none'; ctxClear(gone);
      setT(here, null); here.style.opacity = 1;
      Z.level = inIn ? lo + 1 : lo;
      if (PH) { setView(pview(Z.level)); if (Z.level === 0) foldSoon(); }
      // the view the camera rests at loses the zoom's marks (the dimming that the step puts on arrives in the same
      // frame, arrive()); a view passed through keeps them for the next step
      if (last) { if (arrive) arrive(); ctxClear(here); LAYERS.forEach(l => l.classList.remove('busy')); }
      scaleUI();
    },
  };
}
/* the zooms from a view s to a view t: out while s is deeper than the target or beside it, then in; each step's length
   on the log scale (a tile to a shire's frame, a minion's box to a minion's frame) */
const LOGT = Math.log(SF.w / (TILE - 2 * INS)), LOGM = Math.log(MF.w / 66);
function viewsTo(s, t) {
  const out = [s]; let v = s;
  while (v.level > 0 && (v.level > t.level || v.sid !== t.sid || (v.level === 2 && (v.nb !== t.nb || v.mi !== t.mi)))) { v = Object.assign({}, v, {level: v.level - 1}); out.push(v); }
  while (v.level < t.level) { v = {level: v.level + 1, sid: t.sid, nb: t.nb, mi: t.mi}; out.push(v); }
  return out;
}
const costOfViews = vs => { let c = 0; for (let i = 1; i < vs.length; i++) c += Math.min(vs[i].level, vs[i - 1].level) === 0 ? LOGT : LOGM; return c; };
/* The camera's curve: one ease over the whole move, so that a zoom from the chip to a minion accelerates once and
   slows once, with no stop at the shire. A cubic whose start speed is m (0: from rest, its top speed 1.5 times the
   mean; a move redirected on its way starts at the speed it had) and whose end speed is 0. */
const herm = (u, m) => m * (u * u * u - 2 * u * u + u) + 3 * u * u - 2 * u * u * u;
const hermD = (u, m) => m * (3 * u * u - 4 * u + 1) + 6 * u - 6 * u * u;
/* a move's length: per ms for each unit of log scale, but a long move (the chip to a minion and further) is
   compressed, so that no move takes much more than 1.7 s (2.5 s from a minion to one in another shire) */
const moveMs = (cost, per) => { const t = per * cost; return cost <= 3 ? t : per * 3 + (t - per * 3) * 0.32; };
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
    const h0 = h ? Math.min(T, Math.max(0, h.now - h.prev)) : 0;
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
    // from the last frame's time, so that the first frame of a move (or of a redirected one) is a whole frame's step
    const t0 = h ? h.prev : CLK.last && performance.now() - CLK.last < 100 ? CLK.last : performance.now();
    if (step(h0)) return;
    let drawn = t0;
    const f = now => {
      if (done) return;
      if (stop()) { HAND = {prev: drawn, now}; fin(false); return; }
      const t = Math.min(T, Math.max(0, now - t0)); drawn = now;
      if (step(t) || t >= T) fin(true); else requestAnimationFrame(f);
    };
    requestAnimationFrame(f);
    setTimeout(() => { if (!done && !stop()) { step(T); fin(true); } }, T + 800);   // a hidden tab gets no frames
  });
}
/* The camera follows the latest request only: rapid presses never queue a chain of animations, and a request that
   comes in during a move redirects it from where it is, forwards or back, at the speed it had (a reversal slows to a
   stop first, 130 ms), with no jump. goTo() resolves once the view reaches the latest target. o.clk: a token whose
   clock (the pausable one) drives the move; o.ms: milliseconds per unit of log scale (0 for a cut); o.total: the whole
   move's length instead; o.keepFx: a flow's drawing rides it; o.carry: a flow's packet rides it; o.c1: the look the
   view ends at when the move ends on a zoom out (a step that dims it); o.arrive: run in the frame the camera
   arrives in (a step's highlight, so that it lands with no flash); o.atChip: the camera rests its eye on the chip
   halfway through an out-and-in move and this runs there (a flow's establishing shot). */
let ZT = null, ZW = false, ZWAIT = [], ZN = 0;
const zkey = () => Z.level + ':' + Z.sid + ':' + Z.nb + ':' + Z.mi;
/* where the camera is going, else where it is: + and - step from there, so that a second press is never lost */
const zNow = () => (ZT ? ZT.t : Z);
function goTo(t, o) {
  o = o || {};
  const z = zNow();
  const tt = {level: t.level || 0, sid: t.sid == null ? (z.sid == null ? LASTSID : z.sid) : t.sid, nb: t.nb || 0, mi: t.mi || 0};
  // the same target again while the camera is on its way there (a stage stepped mid-move): the move goes on as it is
  const same = ZW && ZT && ZT.t.level === tt.level && (tt.level < 1 || ZT.t.sid === tt.sid) && (tt.level < 2 || (ZT.t.nb === tt.nb && ZT.t.mi === tt.mi));
  if (same && !o.total && o.ms !== 0) { if (o.focus) ZT.o.focus = true; ['arrive', 'c1'].forEach(k => { if (o[k]) ZT.o[k] = o[k]; }); return new Promise(res => ZWAIT.push(res)); }
  ZT = {t: tt, o, n: ++ZN};
  return new Promise(res => { ZWAIT.push(res); if (!ZW) { ZW = true; zoomWorker(); } });
}
/* the plan: the segments from the view shown, or from partway through the step in flight (forwards or back, whichever
   is shorter), to the target; which views are only passed through */
function planTo(t, o) {
  const segs = [], cur = {level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi};
  let vs;
  if (CUR) {
    const Ls = CUR.lo === 0 ? LOGT : LOGM;
    const vIn = {level: CUR.lo + 1, sid: Z.sid, nb: Z.nb, mi: Z.mi}, vOut = {level: CUR.lo, sid: Z.sid, nb: Z.nb, mi: Z.mi};
    const pin = viewsTo(vIn, t), pout = viewsTo(vOut, t);
    const cin = (1 - CUR.e) * Ls + costOfViews(pin), cout = CUR.e * Ls + costOfViews(pout);
    const fwd = cin < cout - 1e-9 || (Math.abs(cin - cout) < 1e-9 && CUR.dir > 0);
    segs.push({part: true, lo: CUR.lo, dir: fwd ? 1 : -1, e0: CUR.e, e1: fwd ? 1 : 0, L: Math.max(1e-3, fwd ? (1 - CUR.e) * Ls : CUR.e * Ls)});
    vs = fwd ? pin : pout;
  } else vs = viewsTo(cur, t);
  for (let i = 1; i < vs.length; i++) {
    const a = vs[i - 1], b = vs[i], dir = b.level > a.level ? 1 : -1, lo = Math.min(a.level, b.level), inn = dir > 0 ? b : a;
    segs.push({lo, dir, e0: dir > 0 ? 0 : 1, e1: dir > 0 ? 1 : 0, L: lo === 0 ? LOGT : LOGM, sid: inn.sid, nb: inn.nb, mi: inn.mi});
  }
  segs.forEach((s, i) => {
    // the outer view sits at e = 0: where a zoom in starts, or where a zoom out ends
    const startMid = i > 0, endMid = i < segs.length - 1;
    s.midOut = s.dir > 0 ? startMid : endMid;
    s.midIn = s.dir > 0 ? endMid : startMid;
    // the establishing shot rests its eye on the chip: the chip is shown there, set back, not passed through
    if (o.atChip && s.lo === 0) s.midOut = false;
    if (s.dir < 0 && !s.midOut) s.end = i === segs.length - 1 ? (o.c1 || FULL) : (o.chipEnd || FULL);
  });
  return segs;
}
async function zoomWorker() {
  const from = {level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi}, fromKey = zkey(), hadFocus = svg.contains(document.activeElement);
  let wantFocus = false;
  try {
    for (let guard = 0; ZT && guard < 40; guard++) {
      const req = ZT, t = req.t, stop = () => ZT !== req, clk = req.o.clk || null;
      if (req.o.focus) wantFocus = true;
      // turned back while moving: slow to a stop first (130 ms), then plan from rest
      if (CUR && CUR.ctl && Math.abs(CUR.v) > 2e-4 && !REDUCED && req.o.total !== 0 && req.o.ms !== 0) {
        const probe = planTo(t, req.o)[0];
        if (probe && probe.part && probe.dir * CUR.v < 0) {
          const Ls = CUR.lo === 0 ? LOGT : LOGM, v = CUR.v, e0 = CUR.e, Tc = 130, c = CUR;
          const ok = await timeline(Tc, tt => { const q = tt / Tc, e = Math.max(0, Math.min(1, e0 + v * Tc * (q - q * q / 2) / Ls)); c.ctl.frame(e); c.e = e; }, clk, stop);
          c.v = 0;
          if (!ok) continue;
        }
      }
      // a step left at its very end (a turn-back slowed to a stop there): the camera is at that view
      if (CUR && CUR.ctl && (CUR.e <= 1e-3 || CUR.e >= 1 - 1e-3)) { CUR.ctl.close(CUR.e < 0.5 ? 0 : 1, true, null); CUR = null; }
      const segs = planTo(t, req.o);
      if (!segs.length) { if (ZT === req) ZT = null; break; }
      if (!req.o.keepFx) clearFx(true); else clearDim();
      const cost = segs.reduce((s, x) => s + x.L, 0);
      let T = req.o.total != null ? req.o.total : moveMs(cost, req.o.ms != null ? req.o.ms : 480);
      // going on the same way: start at the speed the camera has
      let m = 0;
      if (segs[0].part && CUR) {
        const v = segs[0].dir * CUR.v;
        if (v > 1e-5 && T > 0) { m = v * T / cost; if (m > 2.5) { T = 2.5 * cost / v; m = 2.5; } }
      }
      // the views the move enters are built before it starts, where they are not on the screen (no build mid-move)
      const built = {};
      segs.forEach(s => {
        if (s.part || s.dir < 0) return;
        const L = LAYERS[s.lo + 1];
        if (L.style.display !== 'none') return;
        if (s.lo === 0 && !built[1]) { buildShire(s.sid); built[1] = s.sid; }
        else if (s.lo === 1 && !built[2] && (built[1] === s.sid || (Z.level >= 1 && Z.sid === s.sid && !built[1]))) { buildMinion(s.sid, s.nb, s.mi); built[2] = s.sid + ':' + s.nb + ':' + s.mi; }
      });
      let a = 0; segs.forEach(s => { s.a = a; a += s.L; s.b = a; });
      if (segs[0].part && CUR && CUR.ctl) CUR.ctl.update(segs[0]);
      let ci = 0, ctl = segs[0].part && CUR ? CUR.ctl : null;
      const openSeg = s => {
        if (s.dir > 0) {
          if (s.lo === 0) { if (built[1] !== s.sid) buildShire(s.sid); built[1] = null; Z.sid = s.sid; LASTSID = s.sid; }
          else { const key = s.sid + ':' + s.nb + ':' + s.mi; if (built[2] !== key) buildMinion(s.sid, s.nb, s.mi); built[2] = null; Z.nb = s.nb; Z.mi = s.mi; LASTNB = s.nb; LASTMI = s.mi; }
        }
        return segOpen(s, req);
      };
      const drive = tt => {
        const u = T > 0 ? Math.min(1, tt / T) : 1, d = cost * herm(u, m);
        while (ci < segs.length) {
          const s = segs[ci];
          if (!ctl) ctl = openSeg(s);
          if (u < 1 && d < s.b - 1e-9) break;
          const last = ci === segs.length - 1;
          ctl.close(s.e1, last, last ? req.o.arrive : null);
          ctl = null; ci++; CUR = null;
          if (!last && Z.level === 0 && req.o.atChip && !req.atChipDone) { req.atChipDone = true; req.o.atChip(); }
        }
        if (ci < segs.length && ctl) {
          const s = segs[ci], p = s.b > s.a ? Math.max(0, (d - s.a) / (s.b - s.a)) : 1, e = s.e0 + (s.e1 - s.e0) * p;
          ctl.frame(e);
          CUR = {lo: s.lo, e, dir: s.e1 > s.e0 ? 1 : -1, v: (s.e1 > s.e0 ? 1 : -1) * cost * hermD(u, m) / Math.max(1, T), ctl};
        }
      };
      const ok = await timeline(T, drive, clk, stop);
      if (ok && ZT === req) ZT = null;
    }
  } catch (e) { console.error(e); }
  ZT = null; ZW = false;
  if (CUR) { try { CUR.ctl.close(CUR.e >= 0.5 ? 1 : 0, true, null); } catch (e) { console.error(e); } CUR = null; }
  if (fromKey !== zkey()) {
    select(null); scaleUI();
    // a "Zoom into" button in the panel has done its job
    $('pn-body').querySelectorAll('button[data-act="zoom"], button[data-act="zoomm"]').forEach(b => { const a = b.closest('.pn-act'); if (a) a.remove(); });
    if (hadFocus || wantFocus) { const f = zoomFocus(from); if (f) f.focus({preventScroll: true}); }
  }
  const w = ZWAIT; ZWAIT = []; w.forEach(r => r());
}
/* after a zoom, focus the part zoomed out of (a shire, a minion), else the first part of the new view */
function zoomFocus(from) {
  const L = LAYERS[Z.level];
  if (Z.level < from.level) {
    if (Z.level === 0 && SH[from.sid] && SH[from.sid].g) return SH[from.sid].g;
    if (Z.level === 1) { const m = [...L.querySelectorAll('.comp[data-comp="minion"]')].find(g => g._ctx.nb === from.nb && g._ctx.mi === from.mi); if (m) return m; }
  }
  return L.querySelector('.comp');
}
/* the reader's own zoom: while a flow plays, the camera stops following it (stepping a stage turns it back on),
   and the flow's stage is drawn again where the camera now is */
function userNav(t) {
  hideTip();
  // a flow, playing or finished, stays: its stage is drawn again at the new scale (a finished one as its last stage's
  // end state, still finished), so the arrows keep stepping its stages
  const k = FL.k, done = FL.done;
  if (k) { FL.tok.dead = true; if (FOLLOW) setFollow(false, true); }
  return goTo(t, {focus: svg.contains(document.activeElement)}).then(() => {
    if (!k || FL.k !== k || ZW) return;
    if (done) startFlow(k, FL.i, {still: true, keep: true, done: true});
    else restartStage();
  });
}
/* where the scale control goes: the shire shown (or being zoomed to), else the one selected, else the last one visited */
/* where the flow is, when a flow is on and its stage is inside a shire */
function flowAim() {
  if (!FL.k || !FL.ctx) return null;
  try { const w = FLOWS[FL.k].stages[FL.i].where(FL.ctx); return w.sid != null && SH[w.sid] ? w : null; } catch (_) { return null; }
}
function aimShire() {
  const z = zNow();
  if (z.level >= 1) return z.sid;
  if (SEL && SEL._key === 'cshire') return SEL._ctx.cell.id;
  const w = flowAim(); if (w) return w.sid;
  return LASTSID;
}
function aimMinion(sid) {
  const z = zNow();
  if (z.level === 2 && z.sid === sid) return [z.nb, z.mi];
  if (SEL && SEL._key === 'minion' && SEL._ctx.mi != null) return [SEL._ctx.nb, SEL._ctx.mi];
  const w = flowAim(); if (w && w.sid === sid && w.level === 2) return [w.nb, w.mi];
  return [LASTNB, LASTMI];
}
function scaleTo(level) {
  if (level < 0 || level > 2) return;
  if (level === 0) return userNav({level: 0});
  const sid = aimShire();
  if (level === 1) return userNav({level: 1, sid});
  const [nb, mi] = aimMinion(sid);
  return userNav({level: 2, sid, nb, mi});
}
const zoomBy = d => scaleTo(zNow().level + d);
/* a button that has nothing to do (the last stage's Next, + at a minion): marked disabled (aria-disabled, dimmed) but
   kept focusable, so that the keyboard's focus never falls to the page and a repeated Enter does nothing */
function setDis(b, dis) { b.setAttribute('aria-disabled', String(!!dis)); b.classList.toggle('dis', !!dis); }
const isDis = b => b.getAttribute('aria-disabled') === 'true';
function scaleUI() {
  const sid = aimShire(), [nb, mi] = aimMinion(sid), lv = zNow().level;
  [0, 1, 2].forEach(l => $('z-' + l).setAttribute('aria-pressed', String(lv === l)));
  $('z-1').textContent = `Shire ${sid}`; $('z-1').title = `Shire ${sid} (${Z.level === 1 ? 'shown' : 'zoom in'})`;
  $('z-2').textContent = `Minion ${mi}`; $('z-2').title = `Minion ${mi} of neighbourhood ${nb}, shire ${sid}`;
  setDis($('z-in'), lv >= 2); setDis($('z-out'), lv <= 0);
  $('cap-scale').textContent = Z.level === 0 ? 'Scale: the chip' : Z.level === 1 ? `Scale: shire ${Z.sid}` : `Scale: minion ${Z.mi}, neighbourhood ${Z.nb}, shire ${Z.sid}`;
}

/* ================= details panel ================= */
let SEL = null;
/* the selected part is ringed, and lifted out of any dimming (a tour step's highlight) */
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
  return f.kind === 'measured' ? (f.card || 'card not recorded') : '';
}
function factLi(id) {
  const f = F[id]; if (!f) { console.error('no fact ' + id); return ''; }
  const cd = cardsTxt(f);
  return `<li class="fact" tabindex="0" data-f="${id}" data-src="1" aria-describedby="srctip"><span>${esc(f.statement)}</span><span class="meta"><span class="kd ${f.kind}">${f.kind}</span>`
    + (cd ? `<span class="cd">${esc(cd)}</span>` : '')
    + (f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>` : '<span>no published page yet</span>')
    + `<span class="fid">${esc(id)}</span></span></li>`;
}
/* words (not a number) whose source is a fact: underlined, with the source on hover */
const src = (text, fids) => `<span class="num" data-f="${fids}">${text}</span>`;
const kpi = (html, lab) => `<div class="pn-kpi"><b>${html}</b><span>${lab}</span></div>`;
const K = (k, lab) => kpi(n(k), lab);
function topPage(ids) {
  const cnt = {}; ids.forEach(i => { const f = F[i]; if (f && f.url) { const u = f.url.split('#')[0]; cnt[u] = (cnt[u] || 0) + 1; } });
  const u = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a])[0];
  if (!u) return '';
  const on = ids.map(i => F[i]).filter(x => x && x.url && x.url.split('#')[0] === u), f = on[0];
  const lead = on.some(x => x.kind === 'measured') ? 'Measured and explained in' : 'More in';
  return `<p class="pn-what pn-more">${lead} <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>.</p>`;
}
/* what the drawing infers about a part, what would settle it, and the hub's row that asks for it */
const askLinks = a => [a.hub_anchor].concat(a.also || []).filter(Boolean)
  .map(id => { const r = RUNGS[id]; return `<a href="${HUB}#${esc(id)}" target="_blank" rel="noopener">${r ? `rung ${r.rung}: ${esc(r.what)}` : esc(id)} ↗</a>`; });
/* an ask's state (research/make_asks.py): open (inferred), nearly (mostly settled by a source in hand, a part still
   open), confirm (settled by a source in hand, a check on the cards would confirm it), settled */
const askState = a => a.settled ? 'settled' : a.state || 'open';
const ASK_HEAD = {open: 'Inferred', nearly: 'Nearly settled', confirm: 'To confirm', settled: 'Settled'};
const ASK_HOW = {open: 'What would settle it', nearly: 'What settles it, and what is left', confirm: 'How it is settled, and the check', settled: 'How'};
function askHtml(a) {
  const links = askLinks(a), st = askState(a);
  return `<div class="ask ${st}"><p class="ask-h">${ASK_HEAD[st]}: ${esc(a.part)}</p>`
    + `<p>${esc(a.what_is_inferred)}</p><p class="ask-s"><b>${ASK_HOW[st]}:</b> ${esc(a.what_settles_it)}</p>`
    + (links.length ? `<p class="ask-l">On the hub: ${links.join(' · ')}</p>` : '') + '</div>';
}
function asksBlock(key, open) {
  const as = ASKS.filter(a => a.comps.includes(key)); if (!as.length) return '';
  const nOpen = as.filter(a => askState(a) !== 'settled').length;
  return `<details class="asks"${open ? ' open' : ''}><summary>${nOpen ? `Inferred or open here, and what would settle it (${nOpen})` : 'Settled here'}</summary>${as.map(askHtml).join('')}</details>`;
}
/* the panel is not a live region (it holds whole fact lists); a short line announces what it now shows */
function panel(html) {
  hideTip(); const b = $('pn-body'); b.innerHTML = ARW(html); b.scrollTop = 0;
  const k = b.querySelector('.pn-kick'), t = b.querySelector('.pn-title');
  $('pn-live').textContent = (k ? k.textContent + ': ' : '') + (t ? t.textContent : '');
}
/* scroll the panel (only the panel, never the page) so that el is in view */
function pnReveal(el) {
  const sc = $('pn-body'); if (!el || !sc.contains(el)) return;
  const r = el.getBoundingClientRect(), s = sc.getBoundingClientRect();
  if (r.top < s.top + 4) sc.scrollTop += r.top - s.top - 8;
  else if (r.bottom > s.bottom - 4) sc.scrollTop += Math.min(r.bottom - s.bottom + 8, r.top - s.top - 8);
}
function factsBlock(key, title) {
  const ids = COMPF[key] || [];
  return `<p class="pn-h pn-fh">${esc(title || 'The facts')} (${ids.length}): point at one for its source</p><ul class="facts">${ids.map(factLi).join('')}</ul>`;
}
function homeInfo(c) {
  const ms = MSC[c.id % 8], h = hops(c, ms);
  let s = 0; Object.values(SH).forEach(o => { s += hops(c, o); });
  return {ms: c.id % 8, h, mean: s / Object.keys(SH).length};
}
const COMPS = {
  chip: () => ({kick: 'The chip', title: 'ET-SoC-1',
    what: `Esperanto's ET-SoC-1 has ${n('cores')} RISC-V cores on one ${n('die_mm2')} mm² die in TSMC ${n('process')}: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor. ${n('cshires')} compute shires run the kernels, at ${n('mhz')} on the lab's cards. The fp32 matmul that sustains ${n('tflops')} TFLOP/s draws ${n('mmw')} at the board across the three cards (die ${n('mmtemp')}); how much of that is idle power depends on the card and its temperature. The die view is the firmware's NoC-spec drawing, which matches the measured map in ${n('fw_pairs')} pair distances; only its east-west handedness is open.`,
    kpis: [K('cores', 'RISC-V cores'), kpi(n('tflops'), 'TFLOP/s fp32, three cards'), kpi(n('mmw'), 'board power in that matmul'), kpi(n('perw'), 'GFLOP/s per board watt')]}),
  cshire: ctx => { const c = ctx.cell, hi = homeInfo(c);
    return {kick: 'Compute shire', title: `Shire ${c.id}`,
      what: `One of the ${n('cshires')} compute shires: ${n('neigh')} of ${n('per_neigh')}, ${n('cache_mb')} of SRAM and one mesh stop. On the measured map it sits at (${c.lx}, ${c.ly}); on this die view, row ${c.r}, column ${c.c}, as in the firmware's NoC-spec map. Its L3 slice homes the lines with PA[10:6] = ${c.id}, which memory shire ${cn(hi.ms, 'L43 dram.memshire-select')} serves, ${cn(hi.h, 'mesh.logical-map L40')} ${hi.h === 1 ? 'hop' : 'hops'} away.`,
      kpis: [kpi(cn(hi.mean, 'mesh.logical-map l3.home', 2), `mean hops to the ${n('cshires')} L3 slices`), kpi(cn(V('lat_l3_a') + V('lat_l3_b') * hi.mean, 'l3.latency mesh.logical-map', 0), 'L3 hit from here by the model, cycles'), K('flb', 'shire barrier, 32 minions')],
      act: Z.level === 0 ? `<button type="button" class="st-btn" data-act="zoom" data-sid="${c.id}">Zoom into shire ${c.id}</button><span class="small">${TOUCH ? 'or tap it' : 'or double-click it'}</span>` : ''};
  },
  master: ctx => { const north = ctx.cell.r === 0;
    return {kick: north ? 'Master shire' : 'Spare shire', title: north ? `Master shire (${N.master_id.t})` : `Spare shire (${N.spare_id.t})`,
      what: `The firmware's map puts shire ${n('master_id')}, the master, whose firmware schedules the kernels, in the north cell of this column, and shire ${n('spare_id')}, the spare that waits for yield recovery, in the south one (${src('the firmware\'s maps', 'fw.grey-cells')}, which match the measured map cell for cell). Not yet confirmed on the cards: timing a counter read on shire 32 from every compute shire would.`,
      kpis: [K('mask', 'compute mask on every card'), K('cshires', 'compute shires')]};
  },
  pcie: () => ({kick: 'PCIe shire', title: 'PCIe shire',
    what: `Two PCIe controllers and an ${n('pcie_lanes')} Gen4 PHY: the chip's link to the host, trained at ${n('pcie_neg')} on every card. Timed on three cards: ${n('pcie_h2d', 'GB/s')} to the card and ${n('pcie_d2h', 'GB/s')} back with the DMA alone, ${n('pcie_h2d_pct')} and ${n('pcie_d2h_pct')} of the ${n('pcie_link')} link figure. A program's copies are staged through a host buffer first and get ${n('pcie_stg_h', 'GB/s')} (the three cards), set by each host's memcpy. The firmware's map places this cell west of the I/O shire.`,
    kpis: [kpi(n('pcie_h2d'), 'GB/s to the card, DMA only'), kpi(n('pcie_d2h'), 'GB/s back'), kpi(n('pcie_stg_h'), 'GB/s staged, a2 / a3 / a1c1'), K('pcie_link', 'link figure, per direction')]}),
  io: () => ({kick: 'I/O shire', title: 'I/O shire',
    what: `The ${n('maxions')} (out-of-order RISC-V cores) with their own cache, the service processor that boots the chip and runs the power and clock governor, a root of trust and the peripherals. The firmware's map puts it at the east end of the top row, beside the PCIe shire.`,
    kpis: [K('maxions', 'in the I/O shire')]}),
  memshire: ctx => { const m = ctx.cell.id, pos = LAY.memshires[m];
    return {kick: 'Memory shire', title: `Memory shire ${m}`,
      what: `Drives ${n('ch16')}. It serves the lines whose PA[8:6] = ${m}: those homed in L3 slices ${src(`${m}, ${m + 8}, ${m + 16} and ${m + 24}`, 'L43')} (checked on three cards). Its place, (${pos.pos[0]}, ${pos.pos[1]}) on the map and the ${pos.die.side} side on the die, comes from a fit of DRAM latencies on aifoundry2${pos.tie_break ? '' : `, and ${src('the firmware\'s map puts it in the same place', 'fw.memshires')}`}; left as fitted, the model is within ±3 cycles for ${n('ms_fit')} of loads on all three cards.${pos.tie_break ? ` The fit alone ties three places for this one, but ${src('one is an empty corner of the grid and one lies off it', 'ms2-forced L42 mesh.grid')}. The firmware's map agrees with the fit on the other seven, which leaves this one the same cell in both: ${src('it confirms the frame, not this place on its own', 'fw.memshires')}; timing a counter read on it from every compute shire would.` : ''}`,
      kpis: [kpi(`${n('lat_ms_a')} + ${n('lat_ms_b')}`, 'cycles past the L3, per hop from the home shire'), K('ms_fit', 'of loads within ±3 cycles, three cards'), K('lat_dram_chip', 'cycles of them the DRAM chip (inferred)')]};
  },
  dram: ctx => ({kick: 'Memory', title: 'LPDDR4X',
    what: `${n('channels')} channels of ${n('ch_bits')}, ${n('dram_gb')} on these cards, run at ${n('mts')} MT/s: ${n('dram_peak')} GB/s peak, and the chip streams ${n('dram_bw')} GB/s. Each package holds ${n('pkg_ch')} and serves two memory shires; which two is not documented, so the drawing's pairing of neighbours${ctx.ms ? ` (memory shires ${ctx.ms.join(' and ')} here)` : ''} is ${src('inferred', 'dram.pkg-pairing L23 L47')}: the dashed parts.`,
    kpis: [kpi(n('dram_bw', 'GB/s'), 'measured stream'), kpi(n('lat_dram'), 'cycles, a typical load'), kpi(n('e_dram', 'pJ/B'), `to read a byte, above idle (${n('e_dram_rng')} over passes)`), K('dram_gb', 'on the card')]}),
  mesh: () => ({kick: 'Network on chip', title: 'The mesh',
    what: `An ${n('grid86')} grid of ${n('stops')} stops joins the shires. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. It runs at ${n('noc_mhz')} and ${n('noc_v')} on aifoundry2. Routes are shortest paths in dimension order, ${src('measured on two cards on 29 September', 'L104')}: a request goes x first, then y, and its reply y first, back along the same links; a link that two streams share carries about ${n('route_gbs')}. The flows draw every leg so. On the die, x runs down the rows: a request first moves north or south, a reply east or west.`,
    kpis: [K('hop_cyc', 'per hop, round trip'), K('hop_mm', 'per hop (die plot)'), kpi(n('bitmm'), 'per bit and mm, free links')]}),
  host: () => ({kick: 'Host', title: 'Host and PCIe',
    what: `The card sits in a PCIe slot of the host; the link trained at ${n('pcie_neg')} on every card. Timed on three cards on 27 September: ${n('pcie_h2d', 'GB/s')} to the card with the DMA alone (${n('pcie_h2d_pct')} of the link figure); a program's staged copies get ${n('pcie_stg_h', 'GB/s')}, because the runtime first copies into a bounce buffer at the host's memcpy rate (${n('pcie_memcpy', 'GB/s')}) and only then transfers. An empty kernel on all 32 shires costs the card ${n('pcie_b2b', 'µs')} each when launches are queued; one launch waited for takes ${n('pcie_launch', 'µs')}, the extra ${n('pcie_wait_rng')} mostly the runtime's idle poll. A lone 4 KB copy takes ${n('pcie_4k', 'µs')} for the same reason: the runtime's response thread polls every ${n('poll50')} while commands are in flight and ${n('poll500')} when none are.`,
    kpis: [kpi(n('pcie_h2d'), 'GB/s to the card, DMA only'), kpi(n('pcie_b2b'), 'µs per empty kernel, queued (a2 / a3 / a1c1)'), kpi(n('pcie_4k'), 'µs, a lone 4 KB copy'), K('pcie_neg', 'negotiated on every card')]}),
  meshstop: () => ({kick: 'Shire', title: 'Mesh stop',
    what: `The shire's single attach point to the mesh: minion 31 sees the same round trips as minion 0. A shire has ${n('lanes4')}; a line takes lane PA[7:6], and the port is ${n('port512')} wide.`,
    kpis: [K('hop_cyc', 'per hop, round trip')]}),
  banks: ctx => ({kick: 'Shire cache' + (ctx.bank != null ? ` · bank ${ctx.bank}` : ''), title: 'Shire cache',
    what: `${n('bank1mb')}, each of ${n('subbanks')}. In mode M0, the reset mode and the one these cards run, it holds ${n('scp_mb')} of scratchpad, ${n('l2_kb')} of L2 and a ${n('l3_mb')} slice of the chip's L3. A line's L2 bank is PA[7:6].`,
    kpis: [K('cache_mb', 'SRAM per shire'), kpi(n('lat_l2'), 'cycles, an L2 hit')]}),
  l2: () => ({kick: 'Shire cache', title: 'L2',
    what: `${n('l2_kb')}, private to the shire's ${n('per_shire')}. A hit takes ${n('lat_l2')} cycles (${n('lat_rb')} from the read buffer); the chip streams ${n('bw_l2')} TB/s from L2 at about ${n('e_l2')} pJ per byte (${n('e_l2_rng')} pass to pass).`,
    kpis: [kpi(n('lat_l2'), 'cycles'), kpi(n('bw_l2', 'TB/s'), 'chip-wide'), kpi(n('e_l2', 'pJ/B'), `above idle (${n('e_l2_rng')} over passes)`)]}),
  l3: () => ({kick: 'Shire cache', title: 'L3 slice',
    what: `A ${n('l3_mb')} slice of the chip's ${n('l3_chip')} L3. Lines rotate over the ${n('cshires')} slices by PA[10:6], so a line's home is usually another shire: a hit costs ${n('lat_l3_a')} + ${n('lat_l3_b')} between requester and home, ${n('lat_l3_avg')} cycles averaged over the slices. ${src('A miss goes on from the home to memory and comes back through the home', 'sc.l3-miss')}.`,
    kpis: [kpi(n('lat_l3_avg'), 'cycles, average'), kpi(n('bw_l3', 'TB/s'), 'chip-wide'), kpi(n('e_l3', 'pJ/B'), `above idle (${n('e_l3_rng')} over passes)`)]}),
  scp: () => ({kick: 'Shire cache', title: 'Scratchpad',
    what: `${n('scp_mb')} that any shire can address at ${n('scp_base')}. From its own shire it is as fast as the L2 (${n('lat_scp')} cycles, ${n('bw_scp')} TB/s); from another shire it costs ${n('lat_rs_a')} + ${n('lat_rs_b')} cycles per hop, and with every shire reading one ${n('rs_hops')} away on average the chip gets ${n('bw_rs')} TB/s at ${n('e_rs0')}–${n('e_rs1')} pJ/B.`,
    kpis: [kpi(n('lat_scp'), 'cycles, own shire'), kpi(`${n('lat_rs_a')} + ${n('lat_rs_b')}`, 'cycles per hop, another shire'), kpi(`${n('e_scp0')}–${n('e_scp1')}`, 'pJ/B own (zeros to random)')]}),
  uc: () => ({kick: 'Shire', title: 'UC block',
    what: `The shire's uncacheable block: fast local barriers, fast credit counters, inter-processor interrupts and global atomics. A barrier over the shire takes ${n('flb')}; a barrier over all ${n('n1024')} minions built from these barriers, global atomics and credits takes ${n('chipbar', 'cycles')}. One contended global atomic retires every ${n('hot10')} (aifoundry2): see flow 9.`,
    kpis: [K('flb', 'shire barrier'), kpi(n('chipbar'), `cycles, chip barrier over ${n('n1024')} minions`)]}),
  xbar: () => ({kick: 'Shire', title: 'Crossbar',
    what: `A full crossbar joins the four neighbourhoods to the four banks and the UC block over ${n('xbar512')} ET-Link buses. A message between two minions that are not on a tree edge goes through it: ${n('ts_xbar')} cycles round trip, against ${n('ts_fln')} on a tree edge.`,
    kpis: [kpi(n('ts_xbar'), 'cycles, through the crossbar'), K('ts_fln', 'on a tree edge')]}),
  neigh: ctx => ({kick: 'Shire', title: `Neighbourhood ${ctx.nb != null ? ctx.nb : ''}`,
    what: `${n('per_neigh')} sharing a ${n('icache')} instruction cache, in two columns of four either side of a channel. Minions talk fastest along the reduction tree's ${n('fln7')} edges (${n('edges')}): ${n('ts_fln')} round trip, against ${n('ts_xbar')} cycles for any other pair in the shire. The hardware allreduce (TensorReduce and TensorBroadcast) climbs this tree, then the crossbar and the mesh: ${n('ar1024')} over all ${n('n1024')} minions (flow 0).`,
    kpis: [K('ts_fln', 'round trip, tree edge'), kpi(n('ts_xbar'), 'cycles, any other pair'), kpi(n('ar1024'), `allreduce over ${n('n1024')} minions`)]}),
  minion: ctx => { const at1 = ctx.mi != null, sid = at1 ? ctx.sid : Z.sid, nb = at1 ? ctx.nb : Z.nb, mi = at1 ? ctx.mi : Z.mi, h0 = sid * 64 + (nb * 8 + mi) * 2;
    return {kick: 'Minion', title: `Minion ${mi} · neighbourhood ${nb}`,
      what: `A dual-threaded (${n('harts')}), in-order, single-issue RV64IMFC core with a vector unit of ${n('lanes')}, whose FMA and int8 multiply-add units also run the tensor instructions (a sequencer in the vector unit drives them), and a ${n('l1_kb')} L1 data cache. Its harts are ${cn(h0, 'chip.harts', 0)} and ${cn(h0 + 1, 'chip.harts', 0)}. An awake minion costs ${n('awake')}.`,
      kpis: [kpi(n('vecpeak'), 'per cycle, fp32 peak, vector or tensor'), K('awake', 'awake, one hart')],
      act: at1 && Z.level === 1 ? `<button type="button" class="st-btn" data-act="zoomm" data-nb="${nb}" data-mi="${mi}">Zoom into minion ${mi}</button><span class="small">${TOUCH ? 'or tap it' : 'or double-click it'}</span>` : ''};
  },
  hart: ctx => ({kick: 'Minion', title: `Hart ${ctx.t}`,
    what: ctx.t === 0 ? `Hart 0 may issue every tensor instruction. Each hart has ${n('vregs')} (f0–f31).`
      : `Hart 1 may issue only TensorLoadL2Scp, TensorWait and tensor_coop CSR accesses; any other tensor instruction raises an illegal-instruction exception. On read-buffer and L2 hits, ${n('h1pen')} cycles than hart 0. Each hart has ${n('vregs')}.`,
    kpis: [K('harts', 'per minion')]}),
  vpu: () => ({kick: 'Minion', title: 'Vector unit',
    what: `${n('lanes')} in lockstep. Each lane has an FMA unit, two int8 multiply-add units, an integer unit and a transcendental unit (exp2, log2, reciprocal). The tensor instructions run on these same lanes, driven by state machines in the vector unit, so the fp32 peak is ${n('vecpeak')} per cycle either way. An ${n('lanes_n')}-lane fmadd.ps costs ${n('e_fmadd')} pJ on random data.`,
    kpis: [kpi(n('vecpeak'), 'per cycle, fp32, vector or tensor'), kpi(n('e_fmadd', 'pJ'), 'fmadd.ps, random data')]}),
  tensor: () => ({kick: 'Minion', title: 'Tensor sequencer',
    what: `TensorFMA and TensorIMA add no compute unit of their own: ${src('state machines in the vector unit run them on its lanes', 'minion.vec-peak')} (${n('lanes')}), on each lane's FMA and int8 multiply-add units, with operands from the L1 scratchpad and TenB. At peak that is ${n('peak32')}, ${n('peak16')} or ${n('peak8')} operations per cycle, the lanes' own peak. All ${n('n1024')} minions sustain ${n('tflops')} TFLOP/s fp32, ${n('tflops16')} fp16 and ${n('tops8')} TOP/s int8, at about ${n('e_mac32')} pJ per fp32 multiply-add (${n('e_mac32_rng')} over passes). Flow 7 plays one op.`,
    kpis: [kpi(n('tflops'), 'TFLOP/s fp32, chip'), kpi(n('e_mac32'), `pJ per fp32 MAC (${n('e_mac32_rng')} over passes)`)]}),
  l1d: () => ({kick: 'Minion', title: 'L1 data cache',
    what: `${n('l1_kb')} (${n('l1geom')}), private and not coherent. Before each launch the firmware makes ${n('l1_scp')} of it a tensor scratchpad and leaves each hart ${n('l1_hart')}. A hit takes ${n('lat_l1')} cycles and costs ${n('e_l1')} pJ per byte.`,
    kpis: [kpi(n('lat_l1'), 'cycles, a hit'), kpi(n('e_l1', 'pJ/B'), 'above idle'), kpi(n('bw_l1b', 'TB/s'), 'chip-wide, unrolled loop')]}),
  l1scp: () => ({kick: 'Minion', title: 'L1 tensor scratchpad',
    what: `${n('l1_scp')} of the L1 (${n('sets011')}): TensorLoad writes rows here and TensorFMA reads its A operand from it. A 16-line TensorLoad takes ${n('tl_l2')} cycles from the L2.`,
    kpis: [K('l1_scp', 'per minion'), kpi(n('tl_l2'), 'cycles, 16 lines from the L2')]}),
  etlink: () => ({kick: 'Minion', title: 'ET-Link port',
    what: `The minion's own request and response interfaces are ${n('etl_min')} wide. The ${n('per_neigh')} of a neighbourhood share one ${n('etl512')} to the shire cache, after the neighbourhood up-converts their requests; responses come back over a ${n('etl256')}. An L1 miss goes out here to the L2 bank chosen by PA[7:6].`,
    kpis: [K('lat_l2', 'to an L2 hit')]}),
  fln: () => ({kick: 'Minion', title: 'Fast local network',
    what: `Joins the minions of a neighbourhood along the reduction tree (${n('edges')}). A ${n('b32')} TensorSend round trip takes ${n('ts_fln')} on these edges. The hardware allreduce (TensorReduce and TensorBroadcast) climbs this tree, then the crossbar and the mesh: ${n('ar1024')} over all ${n('n1024')} minions.`,
    kpis: [K('ts_fln', 'round trip, tree edge'), kpi(n('ar1024'), `allreduce over ${n('n1024')} minions`)]}),
  inferred: () => ({kick: 'What the drawing infers', title: 'Dashed, inferred, and what would settle it',
    what: `Most of the layout is now fixed by measurement and by the firmware: the measured map of the shires equals the firmware's NoC-spec map once its boot-time renaming is applied (${n('fw_pairs')} pair distances), which also names the four cells without a compute shire and agrees with the memory shires' fit. Still inferred: the LPDDR4X pairing (dashed), the die's east-west handedness, the routes' turning order, the inside of a shire, and the sizes. Each item says what would settle it and links to the row that asks for it on the hub, whose list collects everything to ask AI Foundry for.`,
    kpis: [kpi(String(ASKS.filter(a => askState(a) !== 'settled').length), 'open items'), kpi(String(new Set(ASKS.flatMap(a => [a.hub_anchor].concat(a.also || [])).filter(Boolean)).size), 'asks on the hub')],
    act: `<a class="st-btn" href="${HUB}#ask-noc-docs" target="_blank" rel="noopener">The hub's list of asks ↗</a>`,
    all: true}),
};
function showComp(key, ctx) {
  const d = COMPS[key](ctx || {}), ids = COMPF[key] || [];
  panel(`<p class="pn-kick">${esc(d.kick)}</p><p class="pn-title">${esc(d.title)}</p><p class="pn-what">${d.what}</p>`
    + (d.kpis ? `<div class="pn-kpis">${d.kpis.join('')}</div>` : '') + (d.act ? `<div class="pn-act">${d.act}</div>` : '')
    + (d.all ? ASKS.map(askHtml).join('') : asksBlock(key, false))
    + topPage(ids) + (ids.length ? factsBlock(key) : ''));
}
function zoomInto(g) {
  const key = g._key, ctx = g._ctx;
  if (key === 'cshire' && Z.level === 0) { select(g); showComp(key, ctx); userNav({level: 1, sid: ctx.cell.id}); return true; }
  if (key === 'minion' && Z.level === 1 && ctx.mi != null) { select(g); showComp(key, ctx); userNav({level: 2, sid: Z.sid, nb: ctx.nb, mi: ctx.mi}); return true; }
  return false;
}
function activate(g) {
  const zoomable = (g._key === 'cshire' && Z.level === 0) || (g._key === 'minion' && Z.level === 1 && g._ctx.mi != null);
  if (zoomable && (SEL === g || TOUCH)) { zoomInto(g); return; }   // a second click zooms in; on a touch screen, a tap
  select(g); showComp(g._key, g._ctx); scaleUI();
}
svg.addEventListener('click', e => { const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) activate(g); });
svg.addEventListener('dblclick', e => { const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g) && SEL !== g) zoomInto(g); });
svg.addEventListener('keydown', e => {
  const g = e.target.closest && e.target.closest('.comp'); if (!g) return;
  if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); if (!zoomInto(g)) { select(g); showComp(g._key, g._ctx); } }
  else if (e.key === ' ' && !flowOn()) { e.preventDefault(); e.stopPropagation(); select(g); showComp(g._key, g._ctx); scaleUI(); }
});
$('pn-body').addEventListener('click', e => {
  const b = e.target.closest('button[data-act]'); if (!b) return;
  if (b.dataset.act === 'zoom') userNav({level: 1, sid: +b.dataset.sid});
  else if (b.dataset.act === 'zoomm') userNav({level: 2, sid: Z.sid, nb: +b.dataset.nb, mi: +b.dataset.mi});
  else if (ACTS[b.dataset.act]) ACTS[b.dataset.act](b);
});

/* ================= sources on hover and focus ================= */
const tip = $('srctip');
function tipHtml(ids, srcOnly) {
  return ids.split(/\s+/).filter(Boolean).map(id => {
    const f = F[id]; if (!f) return '';
    const cd = cardsTxt(f);
    return `<div><b>${esc(f.kind)}</b> · ${esc(id)}${cd ? ' · ' + esc(cd) : ''}`
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
/* while presenting, a pointer left on the stage shows no source tooltips (they would cover the die); the keyboard's
   focus still shows them. The pointer itself hides after 2 s without moving (CSS #stage.present.idle). */
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

/* ================= drawing a flow ================= */
/* a packet: drawn under its drawing's callouts (their text is never covered), growing in */
function packet(fx, col, r, still) {
  r = r || 11;
  const g = E('g', {class: 'pk'}, fx), inner = E('g', {}, g);
  S(E('circle', {r: r + 7}, inner), {fill: col, fillOpacity: 0.26});
  S(E('circle', {r}, inner), {fill: col, stroke: 'var(--page)', strokeWidth: 2.5});
  const co = fx.querySelector(':scope > .co'); if (co) fx.insertBefore(g, co);
  if (!still) popIn(inner);
  return g;
}
const at = (g, p) => g.setAttribute('transform', `translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`);
/* move a packet along a polyline with an ease in and out. o.even: the same time for every segment (a mesh hop costs
   the same everywhere), else a steady speed along the length. o.trail: false for none; o.onSeg(i, n) per segment;
   o.w, o.op, o.dash (true: dotted, or a dash pattern): the trail's width (6, an active trail), opacity and dashes */
async function travel(tok, fx, pk, P, ms, o) {
  o = o || {};
  const trail = o.trail === false ? null : S(E('path', {class: 'trail', fill: 'none'}, fx), {stroke: o.col || 'var(--c2)', strokeWidth: o.w || 6, strokeLinecap: 'round', strokeLinejoin: 'round', strokeOpacity: o.op || 0.75, strokeDasharray: o.dash ? (o.dash === true ? '2 13' : o.dash) : null});
  if (trail) fx.insertBefore(trail, fx.firstChild);
  const nseg = Math.max(1, P.length - 1), cum = [0];
  for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + (o.even ? 1 : Math.hypot(P[i].x - P[i - 1].x, P[i].y - P[i - 1].y)));
  const tot = cum[cum.length - 1] || 1;
  const upto = q => {
    const s = q * tot; let i = 0; while (i < nseg - 1 && cum[i + 1] < s) i++;
    const f = cum[i + 1] > cum[i] ? Math.min(1, (s - cum[i]) / (cum[i + 1] - cum[i])) : 1;
    let d = `M${P[0].x},${P[0].y}`; for (let k = 1; k <= i; k++) d += ` L${P[k].x},${P[k].y}`;
    const a = P[i], b = P[Math.min(i + 1, P.length - 1)], p = {x: lerp(a.x, b.x, f), y: lerp(a.y, b.y, f)};
    return [p, d + ` L${p.x},${p.y}`, q >= 1 ? nseg : i + (f >= 1 ? 1 : 0)];
  };
  let last = -1;
  const ez = o.linear ? (t => t) : easeS;
  const step = q => { const [p, d, si] = upto(ez(q)); at(pk, p); if (trail) trail.setAttribute('d', d); if (o.onSeg && si !== last) { last = si; o.onSeg(si, nseg); } };
  if (P.length === 1) { at(pk, P[0]); return trail; }
  await anim(tok, ms, step);
  return trail;
}
/* A labelled box: a light card with a thin border, a short accent bar in its colour and, when it points at a place
   (o.cell, o.lead), a thin leader ending in a dot on that place. With o.cell it sits beside that tile (o.side 'l' or
   'r') in the band below the tiles' id labels, so that it covers no tile's number; with o.tl or o.tr, (x, y) is its
   top-left or top-right corner; otherwise it sits on side o.side of (x, y) ('c': centred on it). o.minW: at least
   this wide. It lies above the packets of its drawing (packet() inserts them under it), and it fades in. */
const fxLevel = fx => { const L = fx && fx.closest && fx.closest('.lay'); return L ? +L.dataset.level : 0; };
function callout(fx, x, y, lines, o) {
  o = o || {};
  // on a phone a callout is larger at the chip's scale and a shire's, where the drawing is small (not one that stands
  // in the band right of the die: that one folds under the die, enlarged with the charts)
  const lv = PH ? fxLevel(fx) : 0, inBand = PH && lv === 0 && x >= BANDX, big = PH && !inBand ? [1.25, 1.1, 1][lv] : 1;
  const col = o.col || 'var(--c2)', fs = (o.fs || 22) * big, lh = fs * 1.28, pad = 11, acc = 9;
  const g = E('g', {class: 'co'}, fx), lead = E('g', {class: 'co-lead'}, g);
  const box = S(E('rect', {class: 'co-box', rx: 6, filter: 'url(#co-sh)'}, g), {stroke: `color-mix(in srgb, ${col} 55%, var(--surface))`});
  const bar = S(E('rect', {class: 'co-acc', rx: 2, width: 4}, g), {fill: col});
  const tx = lines.map((ln, i) => {
    const Lx = typeof ln === 'string' ? {t: ln} : ln, t = T(g, 0, 0, Lx.t, 'co-t' + (i === 0 ? ' b' : ''), 'start', Lx.f);
    t.style.fontSize = fs + 'px'; return t;
  });
  let w = 0; tx.forEach(t => { let tw = 0; try { tw = t.getComputedTextLength(); } catch (_) { /* not rendered */ } w = Math.max(w, tw || t.textContent.length * fs * 0.55); });
  const bw = Math.max(w + 2 * pad + acc, o.minW || 0), bh = lines.length * lh + pad;
  let bx = o.side === 'l' ? x - 20 - bw : (o.side === 'u' || o.side === 'd' || o.side === 'c') ? x - bw / 2 : x + 20;
  let by = o.side === 'u' ? y - 20 - bh : o.side === 'd' ? y + 20 : y - bh / 2;
  if (o.cell) {
    const c = o.cell;
    bx = o.side === 'l' ? c.x + 6 - bw : c.x + c.w - 6;
    by = Math.min(c.y + 58, c.y + c.h + 12 - bh);
  }
  if (o.tl) { bx = x; by = y; } else if (o.tr) { bx = x - bw; by = y; }
  // inside the drawing's frame; on a phone, inside the view of its scale, unless it stands in the band right of the die
  // (then it folds under the die with the band's charts, bandFold)
  let R = VB;
  if (PH) { if (inBand) bx = Math.max(bx, BANDX + 4); else R = PV[lv]; }
  bx = Math.max(R.x + 4, Math.min(R.x + R.w - 4 - bw, bx)); by = Math.max(R.y + 4, Math.min(R.y + R.h - 4 - bh, by));
  box.setAttribute('x', bx); box.setAttribute('y', by); box.setAttribute('width', bw); box.setAttribute('height', bh);
  bar.setAttribute('x', bx + 5); bar.setAttribute('y', by + 6); bar.setAttribute('height', Math.max(4, bh - 12));
  tx.forEach((t, i) => { t.setAttribute('x', bx + acc + pad - 2); t.setAttribute('y', by + pad / 2 + (i + 1) * lh - lh * 0.24); });
  if (o.lead || o.cell) {
    const qx = Math.max(bx, Math.min(bx + bw, x)), qy = Math.max(by, Math.min(by + bh, y));
    if (Math.hypot(qx - x, qy - y) > 8) {
      S(E('line', {x1: qx, y1: qy, x2: x, y2: y}, lead), {stroke: col, strokeWidth: 1.5});
      S(E('circle', {cx: x, cy: y, r: 4}, lead), {fill: col});
    }
  }
  g._box = {x: bx, y: by, w: bw, h: bh};
  return fadeIn(g, 300, o.tl || o.tr ? 0 : 6);
}
function pulse(tok, fx, p, ms, col, r1) {
  if (REDUCED || tok.ff) return wait(tok, tok.ff ? 0 : Math.min(ms, 600));
  const c = S(E('circle', {cx: p.x, cy: p.y, r: 8}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 4});
  return anim(tok, ms, q => { const e = easeS(q); c.setAttribute('r', 8 + (r1 || 46) * e); c.style.strokeOpacity = 1 - e * 0.85; }).then(() => c.remove(), e => { c.remove(); throw e; });
}
/* where the flow is about to happen, on the die: the tile itself glows and its outline swells, twice */
function pulseTile(tok, cell, ms) {
  ms = ms || 900;
  if (REDUCED || tok.ff || !cell) return Promise.resolve();
  const r = S(E('rect', {class: 'glow', x: cell.x + INS, y: cell.y + INS, width: cell.w - 2 * INS, height: cell.h - 2 * INS, rx: 6, 'pointer-events': 'none'}, FX[0]),
    {fill: 'var(--c2)', fillOpacity: 0, stroke: 'var(--c2)', strokeOpacity: 0, strokeWidth: 3});
  FX[0].insertBefore(r, FX[0].firstChild);
  return anim(tok, ms, q => { const v = Math.pow(Math.sin(Math.PI * 2 * q), 2); r.style.fillOpacity = (0.34 * v).toFixed(3); r.style.strokeOpacity = v.toFixed(3); r.style.strokeWidth = (3 + 7 * v).toFixed(2); })
    .then(() => r.remove(), e => { r.remove(); throw e; });
}
function ring(tok, fx, p, ms, col, label) {
  const R = 40, C = 2 * Math.PI * R;
  const bg = S(E('circle', {cx: p.x, cy: p.y, r: R}, fx), {fill: 'var(--surface)', fillOpacity: 0.85, stroke: 'var(--grid)', strokeWidth: 7});
  const c = S(E('circle', {cx: p.x, cy: p.y, r: R, transform: `rotate(-90 ${p.x} ${p.y})`}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 7, strokeDasharray: `0 ${C}`});
  const t = label ? T(fx, p.x, p.y + 8, label, 't-labb', 'middle') : null;
  return anim(tok, ms, q => { c.style.strokeDasharray = `${C * easeS(q)} ${C}`; }).then(() => [bg, c, t]);
}
function clearDim() {
  svg.classList.remove('dimming', 'fdim', 'mesh-on'); svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi'));
  if (PIP.svg) PIP.svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi'));
  if (SEL) SEL._hiSel = false;
}
/* the glows drawn inside the tiles (glowTiles) */
const clearGlow = soft => svg.querySelectorAll('.lay .comp > .glow').forEach(g => { if (soft) fadeOut(g, 260); else g.remove(); });
/* a flow's drawing goes: at once, or (soft: the tour moving on, another flow) fading out over a quarter second */
function clearFx(soft) {
  FX.forEach((f, i) => {
    if (!f) return;
    if (soft && f.firstChild && LAYERS[i].style.display !== 'none' && CLK.on && !REDUCED) {
      const g = E('g', {class: 'fxold', 'pointer-events': 'none'}, f.parentNode);
      while (f.firstChild) g.appendChild(f.firstChild);
      fadeOut(g, 260);
    } else f.textContent = '';
  });
  if (PIP.fx) PIP.fx.textContent = ''; clearGlow(soft); clearDim();
}
function hiCells(cells, dimOthers) {
  cells.forEach(c => { if (!c) return; if (c.g) c.g.classList.add('hi'); const t = PIP.tiles[c.r + ',' + c.c]; if (t) t.classList.add('hi'); });
  // a stage drawn in the small picture of the die leaves the view the reader chose undimmed
  if (dimOthers && !(FL.ctx && FL.ctx.pip)) svg.classList.add('fdim');
}
/* the LPDDR4X package drawn beside memory shire m, lit with it */
function hiPkg(m) { LAYERS[0].querySelectorAll('.comp[data-comp="dram"]').forEach(g => { if (g._ctx.ms && g._ctx.ms.includes(m)) g.classList.add('hi'); }); }
/* bars on the stage, in the column right of the die (44 units clear of the packages), with 20-22 unit text; text on a
   bar has no halo */
const BAND = {x: 966, y: 40, w: 230};
function bandChart(fx, title, rows, o) {
  o = o || {};
  const g = E('g', {class: 'band'}, fx);
  let y = o.y == null ? BAND.y : o.y;
  if (title) { T(g, BAND.x, y + 22, title, 't-labb halo'); y += 30; }
  if (o.note) { T(g, BAND.x, y + 18, o.note, 't-sm halo'); y += 26; }
  if (o.note2) { T(g, BAND.x, y + 18, o.note2, 't-sm halo'); y += 26; }
  // each row in its own group (a stage can bring a row in, or mark the one it is about); the bar's strength is the
  // theme's (CSS .bbar), its track a grey the bar stands out from in both themes
  const out = rows.map(r => {
    const rg = E('g', {class: 'brow'}, g);
    const nm = T(rg, BAND.x, y + 20, r.name, 't-lab halo', 'start', r.f);
    E('rect', {class: 'btrack', x: BAND.x, y: y + 27, width: BAND.w, height: 30, rx: 4}, rg);
    const bar = S(E('rect', {class: 'bbar', x: BAND.x, y: y + 27, width: 0, height: 30, rx: 4}, rg), {fill: r.col || 'var(--c2)'});
    const val = T(rg, BAND.x + 7, y + 49, r.val || '', 't-labb', 'start', r.f);
    const row = {g: rg, nm, bar, val, y: y + 27, set: q => bar.setAttribute('width', (Math.max(0, Math.min(1, q)) * BAND.w).toFixed(1))};
    y += 68;
    return row;
  });
  if (!o.still) fadeIn(g);
  return {g, rows: out, bottom: y};
}
/* grouped bars: per group (a card) its name and one thin bar per series, the series' colours keyed once at the top */
function bandGroups(fx, title, series, groups, o) {
  o = o || {};
  const g = E('g', {class: 'band'}, fx);
  let y = o.y == null ? BAND.y : o.y;
  T(g, BAND.x, y + 22, title, 't-labb halo'); y += 32;
  let kx = BAND.x;
  series.forEach(sr => {
    S(E('rect', {class: 'bbar', x: kx, y: y + 3, width: 16, height: 16, rx: 3}, g), {fill: sr.col});
    const t = T(g, kx + 22, y + 17, sr.name, 'bkey halo');
    let tw = 0; try { tw = t.getComputedTextLength(); } catch (_) { /* not rendered */ } kx += 22 + (tw || sr.name.length * 9) + 18;
  });
  y += 30;
  const bars = [];
  groups.forEach(gr => {
    T(g, BAND.x, y + 19, gr.name, 't-lab halo', 'start', gr.f); y += 26;
    gr.vals.forEach((v, i) => {
      E('rect', {class: 'btrack', x: BAND.x, y, width: BAND.w, height: 25, rx: 4}, g);
      const bar = S(E('rect', {class: 'bbar', x: BAND.x, y, width: 0, height: 25, rx: 4}, g), {fill: series[i].col});
      T(g, BAND.x + 7, y + 19, v.t, 't-sm', 'start', v.f).style.fill = 'var(--ink)';
      bars.push({bar, q: v.q, set: q => bar.setAttribute('width', (Math.max(0, Math.min(1, q)) * BAND.w).toFixed(1))});
      y += 29;
    });
    y += 10;
  });
  fadeIn(g);
  return {g, bars, bottom: y};
}
/* a few lines of text in the band right of the die (a number too long for a callout's place) */
function bandText(fx, title, lines, y) {
  const g = E('g', {class: 'band'}, fx); let yy = y == null ? BAND.y : y;
  T(g, BAND.x, yy + 22, title, 't-labb halo'); yy += 30;
  lines.forEach(l => { T(g, BAND.x, yy + (l.b ? 26 : 20), l.t, l.b ? 't-mid halo' : 't-sm halo', 'start', l.f); yy += l.b ? 34 : 25; });
  return fadeIn(g);
}
/* a stream drawn as a pipe under its packets */
function pipe(fx, P, col, dash) {
  const d = 'M' + P.map(p => `${p.x},${p.y}`).join(' L');
  const e = S(E('path', {d, fill: 'none'}, fx), {stroke: col, strokeWidth: 8, strokeOpacity: 0.42, strokeLinecap: 'round', strokeLinejoin: 'round', strokeDasharray: dash ? '3 14' : null});
  fx.insertBefore(e, fx.firstChild);
  return e;
}
/* A glow over each compute tile, breathing on the clock with amplitude amp (0 to 1). Every tile has the same phase:
   the data are board watts, not a measured heat per shire, so no tile may look hotter than another. On the die it is
   drawn inside each tile, right over its outline and under its number (which stays --ink); in the small picture of
   the die, under everything. At most 0.38 opaque (0.55 on a dark page). */
function glowTiles(tok, fx, amp, col, shires) {
  const inTiles = fx === FX[0];
  const gs = (shires || Object.values(SH)).map(c => {
    const r = S(E('rect', {class: 'glow', x: c.x + INS + 3, y: c.y + INS + 3, width: c.w - 2 * INS - 6, height: c.h - 2 * INS - 6, rx: 4, 'pointer-events': 'none'}, fx), {fill: col || 'var(--c2)', fillOpacity: 0});
    const sh = inTiles && c.g && c.g.querySelector('.shape');
    if (sh) c.g.insertBefore(r, sh.nextSibling); else fx.insertBefore(r, fx.firstChild);
    return r;
  });
  const st = {amp};
  // with reduced motion, or drawn as a stage's end state, the glow holds still: the amplitude still follows st.amp
  const still = REDUCED || tok.ff;
  // on a dark page the same tint reads as a muddy maroon: it is set stronger there (a warm orange)
  const k = isDark() ? 1.45 : 1;
  const draw = t => {
    if (!gs.length || !gs[0].isConnected) return;
    const v = (k * Math.min(0.38, Math.max(0, st.amp) * (REDUCED ? 0.30 : 0.30 + 0.08 * Math.sin(t / 400)))).toFixed(3);
    gs.forEach(r => { r.style.fillOpacity = v; });
  };
  draw(still ? -400 * Math.PI : CLK.t);
  every(tok, draw);
  return st;
}

/* ================= flows: each a list of stages ================= */
const ST = {rq: 0, pa: null, gs: 'g', sid: 0};
const P40 = 2 ** 32;
function mkPA(home, salt) { return 0x80 * P40 + salt * 2048 + home * 64; }   // a DRAM line (region 0x80_0000_0000) homed in L3 slice `home`
ST.pa = mkPA(13, 0x2468A);
function decode(pa) {
  const b = k => Math.floor(pa / 2 ** k);
  return {bank: b(6) % 4, home: b(6) % 32, ms: b(6) % 8, ch: b(9) % 2, db: b(10) % 8, row: b(18)};
}
function hex(pa) { const s = pa.toString(16).padStart(10, '0'); return '0x' + s.slice(0, 2) + '_' + s.slice(2, 6) + '_' + s.slice(6); }
const hopw = h => h === 1 ? 'hop' : 'hops';
/* the flows by their internal letter, in the flow bar's order; the key that plays each (B, the broadcast, is K here:
   the letter B is the ladder's) */
const FLOWS = {}, ORDER = 'ABCDEFGHIJK', KEYOF = {A: '1', B: '2', C: '3', D: '4', E: '5', F: '6', G: '7', H: '8', I: '9', J: '0', K: 'B'};
const FL = {k: null, i: 0, tok: {dead: true}, ctx: null, done: false, still: false};
let FOLLOW = true, FOLLOW_AUTO = false, LASTFLOW = null, CAPFLOW = false;
const flowOn = () => !!FL.k && !FL.done;
const HOLD = 2300, HOP_MS = 650;
function atView(w) {
  if (ZW || Z.level !== w.level) return false;
  if (w.level === 0) return true;
  return Z.sid === w.sid && (w.level === 1 || (Z.nb === w.nb && Z.mi === w.mi));
}
/* the flow's camera: on the animation clock, so that Space stops it too. Drawing an end state (paused, or stepping
   back) it still moves, on real time and quickly (600 ms), never a cut: the audience keeps the place */
async function cam(tok, w, cut, o) {
  if (!FOLLOW || atView(w)) return;
  const quick = cut || tok.ff;
  await goTo(w, Object.assign({clk: quick ? null : tok, keepFx: true, total: quick ? 600 : undefined, carry: FL.ctx && FL.ctx.tok === tok ? FL.ctx.pk : null}, o || {}));
  alive(tok);
}
/* the look a stage on the die gives it (most set the rest of the die back, CSS #chip.fdim): a zoom out to it ends there */
const stageLook = (st, w) => (w.level === 0 && st.dim !== false ? DIMLOOK.fdim() : null);
function pipOn() { PIP.el.hidden = false; $('pip-cap').textContent = `Flow ${KEYOF[FL.k]}, stage ${FL.i + 1}, on the die · ${TOUCH ? 'tap' : 'click'} to return`; }
function pipOff() { if (document.activeElement === PIP.el) $('btn-follow').focus({preventScroll: true}); PIP.el.hidden = true; }
/* the flow's packet, in this drawing: the one it has if it is already here, else a new one at p. A packet that the
   zoom carried from the last view (it rode the zoom in place) is taken over as it is, with no second grow-in */
function pkIn(c, fx, p, col, r) {
  if (!c.pk || c.pk.parentNode !== fx) { const had = !!c.pk && !c.pip; c.pk = packet(fx, col || 'var(--c2)', r || 12, had); if (p) at(c.pk, p); }
  return c.pk;
}
function sayAt(c, fx, x, y, lines, o) { unsay(c); c.co = callout(fx, x, y, lines, o); return c.co; }
function unsay(c) { if (c.co) { fadeOut(c.co); c.co = null; } }
/* a flow's kicker: its number and name, and the tour step when touring */
const flowKick = k => (TOUR ? `Tour ${TOUR.i + 1} / ${STEPS.length} · ` : '') + `Flow ${KEYOF[k]} · ${FLOWS[k].title}`;
function startFlow(k, i, o) {
  o = o || {};
  const def = FLOWS[k]; i = Math.max(0, Math.min(def.stages.length - 1, i || 0));
  const prev = (o.keep && FL.ctx && FL.ctx.k === k) ? FL.ctx.pick : null;
  // another flow: the last one's drawing fades as this one starts; the same flow redrawn: at once
  FL.tok.dead = true; clearFx(FL.k !== k && !o.still); pipOff();
  const tok = {dead: false, k, ff: false, endDone: !!o.done};
  Object.assign(FL, {k, i, tok, done: false, still: !!o.still});
  LASTFLOW = k; phBox();
  if (!o.still) CLK.on = true;
  document.querySelectorAll('[data-flow]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.flow === k)));
  const ctx = FL.ctx = {k, tok, pick: prev || (def.pick ? def.pick() : {})};
  def.setup(ctx);
  setKick(flowKick(k)); if (!TOUR) { dots(-1); CAPFLOW = true; }
  flowCapSize(k, ctx);
  renderBar(); playBtn();
  quiet(runFrom(tok, ctx, i, !!o.still, !!o.intro));
}
async function runFrom(tok, ctx, i, still, intro) {
  const sts = FLOWS[ctx.k].stages, w = sts[i].where(ctx);
  // the stage bar, the caption and the legs table show the stage at once, before the camera moves to it
  showStage(ctx, i);
  // an establishing shot, for a flow that starts inside a shire the camera is not in: the camera goes to the chip, the
  // shire lights up and pulses, and the zoom in starts while it pulses (its dimming carries on into the zoom). From
  // inside that shire already, the camera goes straight there.
  // From inside another shire it is one move, out and in, that rests its eye on the chip while the shire pulses.
  if (intro && FOLLOW && i === 0 && w.level > 0 && w.sid != null && !still && !REDUCED && !(Z.level >= 1 && Z.sid === w.sid && !ZW)) {
    const lit = () => { if (tok.dead) return; hiCells([SH[w.sid]], true); quiet(pulseTile(tok, SH[w.sid], 1000)); };
    if (Z.level > 0 || ZW) await cam(tok, w, false, {atChip: lit, chipEnd: DIMLOOK.fdim()});
    else { lit(); await wait(tok, 480); if (FOLLOW) await cam(tok, w, false); }
  }
  if (FOLLOW) await cam(tok, w, still, {c1: stageLook(sts[i], w)});
  // the stages before i: their end states, drawn at once where the camera can show them (nothing fades in)
  tok.ff = true; FFTOK = tok;
  for (let j = 0; j < i; j++) {
    const sj = sts[j], wj = sj.where(ctx);
    ctx.stage = j;
    if (atView(wj)) { ctx.fx = FX[wj.level]; ctx.pip = false; await sj.run(tok, ctx); }
    else if (wj.level === 0) { ctx.fx = PIP.fx; ctx.pip = true; await sj.run(tok, ctx); }
  }
  tok.ff = false; if (i > 0) FFEND = performance.now();
  for (let j = i; j < sts.length; j++) {
    if (j !== i) showStage(ctx, j);
    scaleUI();
    if (still) tok.ff = true;
    await playStage(tok, ctx, j);
    if (still) {
      tok.ff = false;
      // a finished flow redrawn at another scale stays finished (userNav)
      if (tok.endDone && j === sts.length - 1) { FL.still = false; FL.done = true; } else FL.still = true;
      renderBar(); playBtn(); return;
    }
    if (j < sts.length - 1) await wait(tok, sts[j].hold != null ? sts[j].hold : HOLD);
  }
  if (FL.tok === tok) { FL.done = true; renderBar(); playBtn(); }
}
/* a stage's line, as the large caption: its "Leg 3 of 6 · " goes (the stage bar says it) */
const stageLine = html => { const s = String(html || '').replace(/^Leg \d+ of \d+ · /, ''); return s.charAt(0).toUpperCase() + s.slice(1); };
/* stage j is now the flow's: the bar marks it, the large caption says what happens in it (the flow's claim is the line
   under it), the legs table lights its row, and a screen reader hears its name */
function showStage(ctx, j) {
  const sts = FLOWS[ctx.k].stages;
  FL.i = j; renderBar(); setCap(stageLine(sts[j].say ? sts[j].say(ctx) : '')); sub(CAPS[ctx.k]()); leg(j);
  $('st-live').textContent = `Stage ${j + 1} of ${sts.length}: ${sts[j].name}`;
}
async function playStage(tok, ctx, j) {
  const st = FLOWS[ctx.k].stages[j], w = st.where(ctx);
  ctx.stage = j; leg(j);
  if (FOLLOW) await cam(tok, w, false, {c1: stageLook(st, w)});
  alive(tok);
  if (atView(w)) { pipOff(); ctx.fx = FX[w.level]; ctx.pip = false; return st.run(tok, ctx); }
  if (w.level === 0) { ctx.fx = PIP.fx; ctx.pip = true; pipOn(); return st.run(tok, ctx); }
  pipOff();
  return markStage(tok, ctx, st, w);
}
/* a stage inside a shire or a minion the camera is not showing: its place is marked, with its name */
async function markStage(tok, ctx, st, w) {
  const L = Z.level, fx = FX[L]; let p = null;
  if (L === 0 && SH[w.sid]) p = {x: SH[w.sid].sx, y: SH[w.sid].sy};
  else if (L === 1 && w.level === 2 && Z.sid === w.sid && AP[1].min[w.nb + ':' + w.mi]) { const m = AP[1].min[w.nb + ':' + w.mi]; p = {x: m.x + m.w / 2, y: m.y + m.h / 2}; }
  else if (L === 2 && w.level === 1 && Z.sid === w.sid) p = AP[2].etl;
  else if (L === 1 && Z.sid !== w.sid) p = AP[1].stop;
  if (ctx.mark) { ctx.mark.remove(); ctx.mark = null; }
  if (p && fx) {
    const g = ctx.mark = E('g', {}, fx);
    const where = L === 1 && Z.sid !== w.sid ? `in shire ${w.sid}` : w.level === 2 ? `inside minion ${w.mi}` : `inside shire ${w.sid}`;
    callout(g, p.x, p.y, [{t: `Stage ${ctx.stage + 1}: ${st.name}`}].concat(st.mark ? st.mark(ctx) : []).concat([{t: where}]), {side: p.x > 460 ? 'l' : 'r', fs: 21});
    if (L === 0) hiCells([SH[w.sid]], true);
    for (let r = 0; r < 2 && !tok.ff; r++) await pulse(tok, g, p, 1300, 'var(--c2)', 52);
  }
  await wait(tok, st.dur || 2400);
}
function killFlow(soft) { FL.tok.dead = true; clearFx(soft); pipOff(); }
function stopFlow(keepCap, soft) {
  killFlow(soft); FL.k = null; FL.done = false; FL.still = false; phBox();
  document.querySelectorAll('[data-flow]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  renderBar(); playBtn();
  if (!TOUR && CAPFLOW && !keepCap) resetCap();
}
/* the reader moved the camera (or turned following on or off): draw the current stage again where the camera is */
function restartStage() { if (FL.k) startFlow(FL.k, FL.i, {still: FL.still || !CLK.on, keep: true}); }
function setFollow(on, auto) {
  FOLLOW = on; FOLLOW_AUTO = !on && !!auto;
  $('btn-follow').setAttribute('aria-pressed', String(on));
  if (on && flowOn()) { const w = FLOWS[FL.k].stages[FL.i].where(FL.ctx); if (!atView(w)) restartStage(); }
}
/* step to stage i of the active flow: animated while playing; its end state while paused */
function goStage(i) {
  if (!FL.k) return false;
  const nst = FLOWS[FL.k].stages.length; if (i < 0 || i >= nst) return false;
  if (FOLLOW_AUTO) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); }   // the step below follows
  startFlow(FL.k, i, {still: !CLK.on || FL.still, keep: true});
  return true;
}
function sub(html) { const e = $('cap-sub'); e.innerHTML = glue(html); e.classList.remove('hint'); }
/* a flow's legs: a numeric column only where some row has a number in it (an empty column still takes width) */
const legRows = rows => {
  const cols = [[2, 'cycles'], [3, 'pJ/B']].filter(([k]) => rows.some(r => r[k]));
  return `<table class="legs"><thead><tr><th>Leg</th><th>What happens</th>${cols.map(([, h]) => `<th class="num">${h}</th>`).join('')}</tr></thead><tbody>${rows.map((r, i) => `<tr class="todo" data-leg="${i}"><td>${r[0]}</td><td>${r[1]}</td>${cols.map(([k]) => `<td class="num">${r[k] || ''}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
};
function leg(i) {
  let on = null;
  document.querySelectorAll('#pn-body tr[data-leg]').forEach(tr => { const k = +tr.dataset.leg; tr.className = k < i ? '' : k === i ? 'on' : 'todo'; if (k === i) on = tr; });
  if (on) pnReveal(on);
}
function flowPanel(k, head, body) {
  panel(`<p class="pn-kick">Flow ${ORDER.indexOf(k) + 1} of ${ORDER.length}<span class="pn-key"> · key ${KEYOF[k]}</span></p><p class="pn-title">${esc(head)}</p>${body}`
    + asksBlock('flow:' + k, false) + topPage(COMPF['flow' + k]) + factsBlock('flow' + k, 'The facts this flow uses'));
}
const shireOfCamera = () => (Z.level >= 1 && SH[Z.sid] ? Z.sid : null);
/* the requester of flows 1 and 2: the shire the camera shows, unless the address's L3 home is that shire or next to it
   (then the load would not cross the mesh the flow is about); else the one picked in the panel (shire 0 at first) */
function pickRq() {
  const cam = shireOfCamera(), home = SH[decode(ST.pa).home];
  return cam != null && home && hops(SH[cam], home) >= 2 ? cam : ST.rq;
}
const side = c => c.c <= 3 ? 'r' : 'l';
function hopper(c, fx, base) {
  if (!c.hopLab || c.hopLab.parentNode !== fx) c.hopLab = T(fx, 0, 0, '', 't-labb halo');
  return si => { const p = base[Math.min(si, base.length - 1)]; c.hopLab.setAttribute('x', p.x + 16); c.hopLab.setAttribute('y', p.y - 18); c.hopLab.textContent = si ? `hop ${si}` : ''; };
}
const hopClear = c => { if (c.hopLab) c.hopLab.textContent = ''; };

/* ---- 1. a load that misses all the way to DRAM ---- */
FLOWS.A = {
  title: 'Load to DRAM',
  pick: () => { const rq = pickRq(), here = Z.level === 2 && Z.sid === rq; return {rq, nb: here ? Z.nb : 0, mi: here ? Z.mi : 0}; },
  cap: () => CAPS.A(),
  setup(c) {
    const rq = c.pick.rq; ST.rq = rq;
    const a = decode(ST.pa), rc = SH[rq], hc = SH[a.home], mc = MSC[a.ms];
    const r1 = route(rc, hc), r2 = route(hc, mc), h1 = r1.length - 1, h2 = r2.length - 1;
    const l3 = V('lat_l3_a') + V('lat_l3_b') * h1, tot = l3 + V('lat_ms_a') + V('lat_ms_b') * h2;
    Object.assign(c, {rq, nb: c.pick.nb, mi: c.pick.mi, a, rc, hc, mc, r1, r2, h1, h2, l3, tot});
    const opts = Object.keys(SH).map(Number).sort((x, y) => x - y).map(s => `<option value="${s}"${s === rq ? ' selected' : ''}>${s}</option>`).join('');
    flowPanel('A', 'A load that misses to DRAM',
      `<p class="pn-what">Hart 0 of minion ${c.mi} (neighbourhood ${c.nb}) in shire ${rq} loads one ${n('line64')} line that no cache holds. Its physical address picks every stop:</p>`
      + `<p class="pn-what"><code data-f="addr.dram-region">${hex(ST.pa)}</code>: L2 bank PA[7:6] = ${a.bank} · L3 home PA[10:6] = shire ${a.home} · memory shire PA[8:6] = ${a.ms} · channel PA[9] = ${a.ch} · DRAM bank PA[12:10] = ${a.db}</p>`
      + `<div class="pn-act"><label>Requester shire <select data-sel="rq">${opts}</select></label><button type="button" class="st-btn" data-act="newpa">New address</button><button type="button" class="st-btn" data-act="replay">Replay</button></div>`
      + legRows([
        ['L1', `miss (a hit: ${n('lat_l1')})`, '', n('e_l1')],
        [`L2 bank ${a.bank}`, `miss (a hit: ${n('lat_l2')})`, '', n('e_l2')],
        [`L3 home, shire ${a.home}`, `${cn(h1, 'mesh.logical-map', 0)} ${hopw(h1)}: a hit would be ${n('lat_l3_a')} + ${n('l3_b12')}×${h1}`, cn(l3, 'l3.latency addr.load-model', 0), n('e_l3')],
        [`memory shire ${a.ms}`, `${cn(h2, 'mesh.logical-map L40', 0)} ${hopw(h2)} on: + ${n('lat_ms_a')} + ${n('lat_ms_b')}×${h2}`, cn(tot, 'addr.load-model L45', 0), ''],
        [`LPDDR4X, channel ${a.ch}`, `bank ${a.db}: ${n('lat_dram_chip')} cycles are the DRAM chip (inferred)`, '', n('e_dram')],
        [`back to shire ${rq}`, `${src('back through the L3 home', 'sc.l3-miss')}: the model's total; typical, measured: ${n('lat_dram')}`, cn(tot, 'addr.load-model L45', 0), ''],
      ]));
  },
  stages: [
    {name: 'L1 miss', where: c => ({level: 2, sid: c.rq, nb: c.nb, mi: c.mi}),
      mark: () => [{t: `L1: miss (a hit: ${N.lat_l1.t} cycles)`, f: 'lat-l1'}],
      say: c => `Leg 1 of 6 · hart 0 of minion ${c.mi} looks in its L1 data cache: a miss (a hit takes ${n('lat_l1')} cycles)`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, h0 = P2.hart0e, pk = pkIn(c, fx, h0);
        at(pk, h0);
        // from hart 0's edge down the gutter between the harts and the vector unit, along the gutter above the L1
        const gx = MF.x + 354, gy = MF.y + 545;
        await travel(tok, fx, pk, [h0, {x: gx, y: h0.y}, {x: gx, y: gy}, {x: P2.l1h0.x, y: gy}, P2.l1h0], 1700, {w: 4});
        const sb = P2.scpBox;   // over the tensor-scratchpad sets, which a load does not use: no label is covered
        sayAt(c, fx, sb.x + sb.w / 2, sb.y + sb.h / 2, [{t: 'L1: miss'}, {t: `a hit takes ${N.lat_l1.t} cycles`, f: 'lat-l1'}], {side: 'c', fs: 21});
        await wait(tok, 2300);
        const pe = P2.etlPort;   // out along the same corridor to the ET-Link port's edge
        await travel(tok, fx, pk, [P2.l1h0, {x: P2.l1h0.x, y: gy}, {x: pe.x - 10, y: gy}, {x: pe.x - 10, y: pe.y}, pe], 1400, {w: 4});
        c.last = {level: 2, p: pe};
      }},
    {name: 'L2 bank', where: c => ({level: 1, sid: c.rq}),
      mark: c => [{t: `L2 bank ${c.a.bank}: miss (a hit: ${N.lat_l2.t} cycles)`, f: 'lat-l2'}],
      say: c => `Leg 2 of 6 · over ET-Link to L2 bank ${c.a.bank} (PA[7:6]) in shire ${c.rq}: a miss (a hit takes ${n('lat_l2')} cycles)`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, m = P1.min[c.nb + ':' + c.mi], ch = P1['ch' + c.nb], B = P1.bank[c.a.bank];
        const mc0 = {x: m.x + m.w / 2, y: m.y + m.h / 2};
        const s0 = c.last && c.last.level === 2 ? outOfMinion(c.last.p, c.nb, c.mi) : mc0;
        const pk = pkIn(c, fx, s0); at(pk, s0);
        await travel(tok, fx, pk, [s0, mc0, {x: ch.x, y: mc0.y}, ch, {x: ch.x, y: P1.xbarY}, {x: B.x, y: P1.xbarY}, B], 2400);
        sayAt(c, fx, SF.x + SF.w, B.y, [{t: `L2 bank ${c.a.bank}: miss`}, {t: `a hit takes ${N.lat_l2.t} cycles`, f: 'lat-l2'}], {side: 'r', fs: 21});   // right of the frame: no bank title covered
        await wait(tok, 2300);
        const ln = P1.lane[c.a.bank];
        await travel(tok, fx, pk, [B, {x: B.x, y: ln.y + 30}, ln], 1300);
        c.last = {level: 1, p: ln};
      }},
    {name: 'L3 home', where: () => ({level: 0}),
      say: c => `Leg 3 of 6 · over the mesh to the L3 home, shire ${c.a.home} (PA[10:6]), ${c.h1} ${hopw(c.h1)}: a hit there would take ${n('lat_l3_a')} + ${n('l3_b12')} × ${c.h1} = ${cn(c.l3, 'l3.latency', 0)} cycles`,
      run: async (tok, c) => {
        const fx = c.fx, s0 = {x: c.rc.sx, y: c.rc.sy};
        hiCells([c.rc, c.hc, c.mc], true);
        const pk = pkIn(c, fx, s0, 'var(--c2)', 12);
        if (c.last && c.last.level === 1 && !c.pip) { const q = outOfShire(c.last.p, c.rq); at(pk, q); await travel(tok, fx, pk, [q, s0], 800, {trail: false}); }
        else at(pk, s0);
        c.last = null;
        const P = pts(c.r1);
        await travel(tok, fx, pk, P, HOP_MS * Math.max(1, c.h1), {even: true, onSeg: hopper(c, fx, P)});
        hopClear(c);
        sayAt(c, fx, c.hc.sx, c.hc.sy, [{t: `L3 home, shire ${c.a.home}: miss`}, {t: `${c.h1} ${hopw(c.h1)}; a hit: ${fnum(c.l3)} cycles`, f: 'l3.latency'}], {cell: c.hc, side: side(c.hc), fs: 21});
      }},
    {name: 'Memory shire', where: () => ({level: 0}),
      say: c => `Leg 4 of 6 · on to memory shire ${c.a.ms} (PA[8:6]), ${c.h2} ${hopw(c.h2)}: + ${n('lat_ms_a')} + ${n('lat_ms_b')} × ${c.h2} cycles`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.rc, c.hc, c.mc], true); unsay(c);
        const pk = pkIn(c, fx, {x: c.hc.sx, y: c.hc.sy}, 'var(--c2)', 12);
        const P = pts(c.r2);
        await travel(tok, fx, pk, P, HOP_MS * Math.max(1, c.h2), {even: true, onSeg: hopper(c, fx, P)});
        hopClear(c);
        sayAt(c, fx, c.mc.sx, c.mc.sy, [{t: `Memory shire ${c.a.ms}`}, {t: `+ ${N.lat_ms_a.t} + ${N.lat_ms_b.t} × ${c.h2}`, f: 'dram.leg'}], {cell: c.mc, side: c.mc.c === 0 ? 'r' : 'l', fs: 21});
      }},
    {name: 'DRAM', where: () => ({level: 0}),
      say: c => `Leg 5 of 6 · channel ${c.a.ch} (PA[9]), bank ${c.a.db} (PA[12:10]): ${n('lat_dram_chip')} cycles of the load are the DRAM chip itself`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.rc, c.hc, c.mc], true); hiPkg(c.a.ms); unsay(c);
        const pc = AP[0].pkg[c.a.ms + ':' + c.a.ch], pk = pkIn(c, fx, {x: c.mc.sx, y: c.mc.sy}, 'var(--c2)', 12);
        await travel(tok, fx, pk, [{x: c.mc.sx, y: c.mc.sy}, {x: c.mc.sx, y: pc.y}, pc], 1400);
        const east = c.mc.c === 7, lines = [{t: `channel ${c.a.ch}, bank ${c.a.db}`}, {t: `${N.lat_dram_chip.t} cycles in DRAM`, f: 'lat-dram-chip'}];
        if (east) sayAt(c, fx, DW + 150, pc.y, lines, {side: 'r', fs: 22}); else sayAt(c, fx, pc.x, pc.y, lines, {side: 'd', fs: 22});
      }},
    {name: 'Back', where: () => ({level: 0}),
      say: c => `Leg 6 of 6 · back to shire ${c.rq} through the L3 home: ${cn(c.tot, 'addr.load-model L45', 0)} cycles (${cn(ns(c.tot), 'addr.load-model op-600', 0)} ns) by the model; a typical measured DRAM load takes ${n('lat_dram')} (${n('lat_dram_ns')})`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.rc, c.hc, c.mc], true); hiPkg(c.a.ms); unsay(c);
        const pc = AP[0].pkg[c.a.ms + ':' + c.a.ch], pk = pkIn(c, fx, pc, 'var(--c2)', 12);
        // a reply: its colour and its own lane beside the request's line, not a dash
        const back = lane([{x: c.mc.sx, y: pc.y}].concat(pts(viaR(c.mc, c.hc, c.rc))), LANE, pc);
        await travel(tok, fx, pk, back, HOP_MS * (c.h1 + c.h2 + 1), {col: 'var(--c7)', even: true});
        quiet(pulse(tok, fx, back[back.length - 1], 900, 'var(--c7)', 34));
        c.res = bandText(fx, 'The whole load', [{t: `${fnum(c.tot)} cycles`, b: 1, f: 'addr.load-model'}, {t: `by the model, ${fnum(ns(c.tot))} ns`, f: 'addr.load-model op-600'}, {t: `${N.lat_dram.t} typical, measured`, f: 'lat-dram-typical'}]);
        leg(6);
      }},
  ],
};

/* ---- 2. the same load hitting at each level: a latency ladder ---- */
FLOWS.B = {
  title: 'Latency ladder',
  pick: () => ({rq: pickRq()}),
  cap: () => CAPS.B(),
  setup(c) {
    const rq = c.pick.rq, a = decode(ST.pa), rc = SH[rq], hc = SH[a.home], mc = MSC[a.ms];
    const r1 = route(rc, hc), r2 = route(hc, mc), h1 = r1.length - 1, h2 = r2.length - 1;
    const l3 = V('lat_l3_a') + V('lat_l3_b') * h1, dram = l3 + V('lat_ms_a') + V('lat_ms_b') * h2, rs = V('lat_rs_a') + V('lat_rs_b') * h1;
    const rsHop = `${n('rs_hops')} mean`;
    const LV = [
      {nm: 'L1', sn: 'L1', cyc: V('lat_l1'), lab: n('lat_l1'), sv: N.lat_l1.t, e: n('e_l1'), bw: n('bw_l1b', 'TB/s'), say: `L1 hit: ${n('lat_l1')} cycles, inside the minion`},
      {nm: 'L2 read buffer', sn: 'L2 read buffer', cyc: V('lat_rb'), lab: n('lat_rb'), sv: N.lat_rb.t, e: '', bw: '', say: `L2 read buffer: ${n('lat_rb')} cycles`},
      {nm: 'L2', sn: 'L2', cyc: V('lat_l2'), lab: n('lat_l2'), sv: N.lat_l2.t, e: `${n('e_l2')} (${n('e_l2_rng')})`, bw: n('bw_l2', 'TB/s'), say: `L2 hit: ${n('lat_l2')} cycles, in the own shire`},
      {nm: 'own scratchpad', sn: 'own scratchpad', cyc: V('lat_scp'), lab: n('lat_scp'), sv: N.lat_scp.t, e: `${n('e_scp0')}–${n('e_scp1')}`, bw: n('bw_scp', 'TB/s'), say: `The shire's own scratchpad: ${n('lat_scp')} cycles, the same SRAM as the L2`},
      {nm: `scratchpad, shire ${a.home}`, sn: `scratchpad ${a.home}`, cyc: rs, lab: `${cn(rs, 'lat-scp-remote', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(rs)} · ${h1} ${hopw(h1)}`, tn: `another shire's scratchpad, ${rsHop}`, e: `${n('e_rs0')}–${n('e_rs1')}`, bw: n('bw_rs', 'TB/s'), back: reply(hc, rc), path: r1, say: `Shire ${a.home}'s scratchpad, ${h1} ${hopw(h1)}: ${n('lat_rs_a')} + ${n('lat_rs_b')} × ${h1} = ${cn(rs, 'lat-scp-remote', 0)} cycles`},
      {nm: `L3, home ${a.home}`, sn: `L3, home ${a.home}`, cyc: l3, lab: `${cn(l3, 'l3.latency', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(l3)} · ${h1} ${hopw(h1)}`, e: `${n('e_l3')} (${n('e_l3_rng')})`, bw: n('bw_l3', 'TB/s'), back: reply(hc, rc), path: r1, say: `L3 hit in home shire ${a.home}, ${h1} ${hopw(h1)}: ${n('lat_l3_a')} + ${n('l3_b12')} × ${h1} = ${cn(l3, 'l3.latency', 0)} cycles (${n('lat_l3_avg')} averaged over slices)`},
      {nm: 'DRAM', sn: `DRAM, ${N.lat_dram.t} typical`, cyc: dram, lab: `${cn(dram, 'addr.load-model', 0)} model · ${n('lat_dram')} typ.`, sv: `${fnum(dram)} model`, e: `${n('e_dram')} (${n('e_dram_rng')})`, bw: n('dram_bw', 'GB/s'), path: r1.concat(r2.slice(1)), back: viaR(mc, hc, rc), dram: true, say: `DRAM through memory shire ${a.ms}: ${cn(dram, 'addr.load-model', 0)} cycles by the model; a typical load takes ${n('lat_dram')}: ${cn(V('lat_dram') / V('lat_l1'), 'lat-l1 lat-dram-typical', 0)}× an L1 hit`},
    ];
    Object.assign(c, {rq, a, rc, hc, mc, LV, pkg: AP[0].pkg[a.ms + ':' + a.ch], max: Math.max(dram, V('lat_dram'))});
    flowPanel('B', 'The latency ladder',
      `<p class="pn-what">The same load from shire ${rq}, hitting at each level in turn. The L3 home and the scratchpad are ${h1} ${hopw(h1)} away in shire ${a.home}; memory shire ${a.ms} is ${h2} ${hopw(h2)} further. Bars are minion cycles at ${n('mhz')}.</p>`
      + `<div class="lad" id="lad">${LV.map((l, i) => `<div class="nm">${esc(l.nm)}</div><div class="tr" data-i="${i}"><u></u><s>${l.lab}</s></div>`).join('')}</div>`
      + `<table class="legs"><thead><tr><th>Level</th><th class="num">pJ/B</th><th class="num">chip-wide</th></tr></thead><tbody>${LV.map((l, i) => `<tr data-leg="${i}" class="todo"><td>${l.tn || esc(l.nm)}</td><td class="num">${l.e}</td><td class="num">${l.bw}</td></tr>`).join('')}</tbody></table>`
      + `<p class="pn-what small">Another shire's scratchpad was measured with every shire reading the one 16 IDs away, ${n('rs_hops')} on average, not at the ${h1} ${hopw(h1)} of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches ${n('bw_l1', 'TB/s')}). Energies are above idle, with their range over passes in brackets.</p>`
      + `<div class="pn-act"><button type="button" class="st-btn" data-act="replay">Replay</button></div>`);
  },
  stages: ['L1', 'Read buffer', 'L2', 'Own scratchpad', 'Remote scratchpad', 'L3 home', 'DRAM'].map((nm, i) => ({
    name: nm, where: () => ({level: 0}), say: c => c.LV[i].say,
    run: async (tok, c) => {
      const fx = c.fx, l = c.LV[i];
      hiCells([c.rc, c.hc, c.mc], true); if (l.dram) hiPkg(c.a.ms);
      if (i === 0) pnReveal($('lad'));
      if (!c.ch || c.ch.g.parentNode !== fx) c.ch = bandChart(fx, 'Latency, cycles', c.LV.map(v => ({name: v.sn, val: v.sv, f: 'lat-l1 lat-l2 l3.latency addr.load-model lat-scp-remote'})));
      fx.querySelectorAll(':scope > path.trail').forEach(p => p.remove());
      const trk = document.querySelector(`#lad .tr[data-i="${i}"]`), bar = trk && trk.querySelector('u');
      const dur = Math.max(1300, l.cyc * 17);
      const grow = anim(tok, dur, q => { const e = easeS(q); if (bar) bar.style.width = (100 * e * l.cyc / c.max).toFixed(2) + '%'; c.ch.rows[i].set(e * l.cyc / c.max); });
      if (!l.path) await Promise.all([grow, pulse(tok, fx, {x: c.rc.sx, y: c.rc.sy}, Math.max(dur, 900), 'var(--c2)', 20 + 30 * l.cyc / 47)]);
      else {
        const out = pts(l.path).concat(l.dram ? [{x: c.mc.sx, y: c.pkg.y}, c.pkg] : []);
        const ret = lane((l.dram ? [{x: c.mc.sx, y: c.pkg.y}] : []).concat(pts(l.back)), LANE, out[out.length - 1]);
        const pk = packet(fx, 'var(--c2)', 11), nO = out.length - 1, nR = ret.length - 1, dO = dur * nO / (nO + nR);
        const trip = async () => { await travel(tok, fx, pk, out, dO, {w: 5, even: true}); await travel(tok, fx, pk, ret, dur - dO, {w: 5, even: true, col: 'var(--c7)'}); };
        await Promise.all([grow, trip()]);
        pk.remove();
      }
      if (trk) trk.classList.add('done');
    }})),
};

/* ---- 3. TensorSend between shires ---- */
const PAIRS = [[0, 24], [0, 13], [0, 31], [8, 23]];
FLOWS.C = {
  title: 'TensorSend',
  cap: () => CAPS.C(),
  setup(c) {
    c.rows = PAIRS.map(([s, d]) => { const h = hops(SH[s], SH[d]), cy = V('ts_a') + V('ts_b') * h; return [s, d, h, cy]; });
    flowPanel('C', 'TensorSend between shires',
      `<p class="pn-what">A hart sends ${n('b32')} of vector registers to a minion in another shire and waits for the reply. The round trip is ${n('ts_a')} cycles to leave and re-enter the shires plus ${n('ts_b')} per hop, on all three cards. The energy, measured with 1 KB messages, is ${n('ts_e_a')} to leave the shire plus ${n('ts_e_b', 'per mean hop')}.</p>`
      + `<table class="legs"><thead><tr><th>From → to</th><th class="num">hops</th><th class="num">cycles</th><th class="num">ns</th></tr></thead><tbody>${c.rows.map((r, i) => `<tr class="todo" data-leg="${i}"><td>shire ${r[0]} → ${r[1]}</td><td class="num">${cn(r[2], 'mesh.logical-map', 0)}</td><td class="num">${cn(r[3], 'ts-rt-mesh', 0)}</td><td class="num">${cn(ns(r[3]), 'ts-rt-mesh op-600', 0)}</td></tr>`).join('')}</tbody></table>`
      + `<p class="pn-what">Inside a shire the same round trip is ${n('ts_fln')} on a tree edge and ${n('ts_xbar')} cycles otherwise. The reply is the partner's own TensorSend back, drawn like the first as a request, x first: the mesh takes a request x first and a load's reply y first (${src('measured on two cards', 'L104')}); whether a TensorSend travels as a request was not tested.</p>`);
  },
  stages: PAIRS.map(([s, d], i) => ({
    name: `Shire ${s} → ${d}`, where: () => ({level: 0}),
    say: c => { const [, , h, cyc] = c.rows[i]; return `Shire ${s} → shire ${d}: ${h} ${hopw(h)} · ${n('ts_a')} + ${n('ts_b')} × ${h} = ${cn(cyc, 'ts-rt-mesh', 0)} cycles (${cn(ns(cyc), 'ts-rt-mesh op-600', 0)} ns) round trip`; },
    run: async (tok, c) => {
      const fx = c.fx, [, , h, cyc] = c.rows[i], A = SH[s], B = SH[d];
      fx.textContent = ''; clearDim(); hiCells([A, B], true);
      const [bg, rc2, lt] = await ring(tok, fx, {x: A.sx, y: A.sy}, 2600, 'var(--c4)', N.ts_a.t);
      [bg, rc2, lt].forEach(e => e && e.remove());
      const pk = packet(fx, 'var(--c2)', 12);
      await travel(tok, fx, pk, pts(route(A, B)), Math.max(1000, 480 * h), {even: true});
      await travel(tok, fx, pk, lane(pts(route(B, A)), LANE, {x: B.sx, y: B.sy}), Math.max(1000, 480 * h), {col: 'var(--c7)', even: true});
      callout(fx, B.sx, B.sy, [{t: `${fnum(cyc)} cycles round trip`, f: 'ts-rt-mesh'}, {t: `${h} ${hopw(h)}, ${fnum(ns(cyc))} ns`, f: 'ts-rt-mesh op-600'}], {cell: B, side: B.c <= 3 ? 'r' : 'l', fs: 21});
    }})),
};

/* ---- 4. the relay: hand a block of results to the next shire, or round-trip it through DRAM. One line of it is
   drawn on its DRAM path, through its L3 home (shire 16) and memory shire 0, as a load goes (fact addr.load-path) ---- */
FLOWS.D = {
  title: 'Relay',
  cap: () => CAPS.D(),
  setup(c) {
    const A = SH[0], B = SH[1], HOME = SH[16], mc = MSC[16 % 8], pkg = AP[0].pkg[mc.id + ':0'];
    const directC = route(A, B), h = directC.length - 1;
    const bars = [['through DRAM', 'rl_e_dram', 'rl_bw_dram', 'var(--c2)'], ['to the next shire', 'rl_e_next', 'rl_bw_next', 'var(--c3)'], ['in the own scratchpad', 'rl_e_own', 'rl_bw_own', 'var(--c1)']];
    Object.assign(c, {A, B, HOME, mc, pkg, h, direct: pts(directC), bars, emax: V('rl_e_dram'), bmax: V('rl_bw_own'),
      loop: pts(via(A, HOME, mc)).concat([{x: mc.sx, y: pkg.y}, pkg, {x: mc.sx, y: pkg.y}]).concat(pts(viaR(mc, HOME, B)))});
    flowPanel('D', 'The relay: next shire or DRAM',
      `<p class="pn-what">A pipeline stage hands its output to the next stage. Through DRAM it writes its output out and the next shire reads it back, each line through its L3 home and memory shire (one line is drawn, homed in ${src('shire 16, served by memory shire 0', 'l3.home L43 addr.load-path')}); on chip it writes straight into the next shire's scratchpad (shire 0 to shire 1 here, ${cn(h, 'mesh.logical-map', 0)} ${hopw(h)}).</p>`
      + `<p class="pn-h">Energy per byte (write + read)</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[1]) / c.emax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[1], 'pJ/B')}</s></div>`).join('')}</div>`
      + `<p class="pn-h">Bandwidth, ${n('rl_stages')} on ${n('n1024')} minions</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[2]) / c.bmax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[2], 'GB/s')}</s></div>`).join('')}</div>`
      + `<p class="pn-what">Next shire against DRAM: ${n('rl_x')} less energy per byte on the three cards, and ${n('rl_speed')} the bandwidth. The dots on the die are drawn at those relative rates.</p>`);
  },
  stages: [
    {name: 'Two ways', where: () => ({level: 0}),
      say: () => `Two ways to hand a block of results to the next shire: straight into its scratchpad, or out to DRAM and back`,
      run: async (tok, c) => { relayDraw(tok, c, 0); await wait(tok, 900); }},
    {name: 'Through DRAM', where: () => ({level: 0}), hold: 0,
      say: () => `Through DRAM: ${n('rl_e_dram')} pJ/B at ${n('rl_bw_dram')} GB/s, every line to its L3 home and memory shire and back`,
      run: async (tok, c) => { relayDraw(tok, c, 1); relayStream(tok, c, 'dram'); await wait(tok, 7000); }},
    {name: 'To the next shire', where: () => ({level: 0}), hold: 0,
      say: () => `To the next shire: ${n('rl_e_next')} pJ/B at ${n('rl_bw_next')} GB/s, straight into its scratchpad`,
      run: async (tok, c) => { relayDraw(tok, c, 2); relayStream(tok, c, 'next'); await wait(tok, 7000); }},
    {name: 'Side by side', where: () => ({level: 0}),
      say: () => `Next shire: ${n('rl_e_next')} pJ/B at ${n('rl_bw_next')} GB/s · through DRAM: ${n('rl_e_dram')} pJ/B at ${n('rl_bw_dram')} GB/s · ${n('rl_13th')} of the energy`,
      run: async (tok, c) => { relayDraw(tok, c, 3); relayStream(tok, c, 'both'); await wait(tok, 1e12); }},
  ],
};
/* The relay, built up: stage 1 draws the two routes; stage 2 labels the DRAM route and brings in its bars; stage 3 the
   next shire's; stage 4 both, and the own scratchpad for scale. A counter under the charts counts the blocks each way
   delivers: side by side, about twelve to one. */
function relayDraw(tok, c, k) {
  const fx = c.fx;
  hiCells([c.A, c.B, c.HOME, c.mc], true); hiPkg(c.mc.id);
  if (!c.drawn || c.drawn.parentNode !== fx) {
    // the pipes under the streams' packets; the callouts and the charts above them (a group of class co)
    const g = c.drawn = E('g', {}, fx); fx.insertBefore(g, fx.firstChild);
    pipe(g, c.direct, 'var(--c3)'); pipe(g, c.loop, 'var(--c2)');
    c.top = E('g', {class: 'co'}, fx);
    c.coD = c.coN = c.cnt = c.ce = c.cb = null; c.shown = [false, false, false];
  }
  if (k >= 1 && !c.coD) c.coD = callout(c.top, c.HOME.sx, c.HOME.sy, [{t: 'through DRAM'}, {t: `${N.rl_e_dram.t} pJ/B`, f: 'relay-energy'}], {cell: c.HOME, side: 'r', col: 'var(--c2)', fs: 21});
  if (k >= 2 && !c.coN) c.coN = callout(c.top, c.B.sx, c.B.sy, [{t: 'next shire'}, {t: `${N.rl_e_next.t} pJ/B`, f: 'relay-energy'}], {cell: c.B, side: 'r', col: 'var(--c3)', fs: 21});
  // the charts hold the rows shown so far (DRAM's, then the next shire's, then the own scratchpad's), drawn again
  // when a row comes in: the rows already there hold still, the new one fades in and grows
  const want = [k >= 1, k >= 2, k >= 3].map((w, i) => w || c.shown[i]);
  if (want.some((w, i) => w !== c.shown[i]) || (k >= 1 && !c.ce)) {
    const nm = b => b[0].replace('in the own', 'own'), idx = [0, 1, 2].filter(i => want[i]), fresh = idx.filter(i => !c.shown[i]);
    [c.ce, c.cb].forEach(ch => { if (ch && ch.g.parentNode) ch.g.remove(); });
    if (c.cnt && c.cnt.g.parentNode) c.cnt.g.remove();
    const still = !!c.ce;
    c.ce = bandChart(c.top, 'pJ per byte', idx.map(i => c.bars[i]).map(b => ({name: nm(b), val: N[b[1]].t, col: b[3], f: 'relay-energy'})), {still});
    c.cb = bandChart(c.top, 'GB/s', idx.map(i => c.bars[i]).map(b => ({name: nm(b), val: N[b[2]].t, col: b[3], f: 'relay-bw'})), {y: c.ce.bottom + 14, still});
    idx.forEach((i, j) => [[c.ce, V(c.bars[i][1]) / c.emax], [c.cb, V(c.bars[i][2]) / c.bmax]].forEach(([ch, q]) => {
      const r = ch.rows[j];
      if (fresh.includes(i) && still) { fadeIn(r.g, 300); quiet(anim(tok, 900, p => r.set(easeS(p) * q))); }
      else if (fresh.includes(i)) quiet(anim(tok, 900, p => r.set(easeS(p) * q)));
      else r.set(q);
    }));
    want.forEach((w, i) => { c.shown[i] = w; });
    // the counter: dots delivered to the next shire, each way, as drawn at the measured rates
    const cg = E('g', {class: 'band'}, c.top), y0 = c.cb.bottom + 8, n0 = c.cnt ? c.cnt.n : {next: 0, dram: 0};
    T(cg, BAND.x, y0 + 22, 'Dots delivered, as drawn', 't-labb halo');
    const l1 = T(cg, BAND.x, y0 + 50, '', 't-lab halo'), l2 = T(cg, BAND.x, y0 + 76, '', 't-lab halo');
    c.cnt = {g: cg, n: n0, show: () => {
      const q = c.cnt.n, ls = [c.shown[1] ? `next shire: ${q.next}` : null, `through DRAM: ${q.dram}`].filter(Boolean);
      l1.textContent = ls[0] || ''; l2.textContent = ls[1] || '';
    }};
    if (!still) fadeIn(cg);
  }
  if (c.cnt) c.cnt.show();
}
function relayStream(tok, c, which) {
  if (REDUCED) return;
  c.streams = c.streams || {};
  Object.values(c.streams).forEach(s => { s.stop = true; });
  const EMIT = 380, SLOW = V('rl_bw_next') / V('rl_bw_dram'), fx = c.fx, t0 = CLK.t, st = {stop: false};
  c.streams[which] = st;
  if (c.cnt) { c.cnt.n = {next: 0, dram: 0}; c.cnt.show(); }   // each stage counts from zero
  const shoot = (P, col, ms, k) => { const pk = packet(fx, col, 12); quiet(travel(tok, fx, pk, P, ms, {trail: false, linear: true}).then(() => { pk.remove(); if (c.cnt && !st.stop) { c.cnt.n[k]++; c.cnt.show(); } }, e => { pk.remove(); throw e; })); };
  let nextD = 0, nextM = 0;
  every(tok, t => {
    if (st.stop) return;
    const dt = t - t0;
    if (which !== 'dram') while (nextD <= dt) { shoot(c.direct, 'var(--c3)', 700 * c.h, 'next'); nextD += EMIT; }
    if (which !== 'next') while (nextM <= dt) { shoot(c.loop, 'var(--c2)', 190 * (c.loop.length - 1), 'dram'); nextM += EMIT * SLOW; }
  });
}

/* ---- 5. gathers and scatters (E48): 32-bit elements on scattered lines of a table in each level ---- */
FLOWS.E = {
  title: 'Gathers',
  cap: () => CAPS.E(),
  setup(c) {
    const rq = SH[0], far = Object.values(SH).find(x => hops(x, rq) === 2 && x.lx === 2) || Object.values(SH).find(x => hops(x, rq) === 2);
    const g = ST.gs === 'g', p = g ? 'g_' : 's_';
    const LN = [['L1', 'l1'], ['L2', 'l2'], ['own scratchpad', 'sp'], ['scratchpad 2 hops', 'rs'], ['DRAM', 'dr']].map(([nm, k]) => ({nm, k, c: V(p + k + '_c'), r: p + k + '_r', e: p + k + '_e'}));
    Object.assign(c, {rq, far, g, p, LN, SCALE: 0.9, lanes: {}});
    flowPanel('E', g ? 'Gathers (E48)' : 'Scatters (E48)',
      `<p class="pn-what">Both harts of ${n('n1024')} minions run the ${n('gs_8')} (${g ? 'fgw.ps' : 'its scatter twin, fscw.ps'}) on scattered lines of a table that fits one level: ${src('each visit\'s 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order', 'gs-g-dram-256K gs-s-dram-256K')}. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.</p>`
      + `<div class="pn-act"><button type="button" class="st-btn" data-act="gs" aria-pressed="${g}">Gathers</button><button type="button" class="st-btn" data-act="gs" aria-pressed="${!g}">Scatters</button></div>`
      + `<div class="lad" id="race">${LN.map((l, i) => `<div class="nm">${l.nm}</div><div class="tr" data-i="${i}"><u></u><s></s></div>`).join('')}</div>`
      + `<table class="legs"><thead><tr><th>Table in</th><th class="num">G el./s</th><th class="num">pJ/element</th><th class="num">cycles/instr.</th></tr></thead><tbody>${LN.map((l, i) => `<tr data-leg="${i}" class="todo"><td>${l.nm}</td><td class="num">${n(l.r)}</td><td class="num">${n(l.e)}</td><td class="num">${n(p + l.k + '_c')}</td></tr>`).join('')}</tbody></table>`
      + (g ? '' : `<p class="pn-what small">For DRAM scatters the cycles per instruction (a per-hart median) and the chip's rate differ by ${src('about 5%', 'gs-s-dram-256K')}.</p>`)
      + `<p class="pn-what">These are E48's results, reduced on 27 September on all three cards, not yet on a published page.</p>`);
  },
  stages: ['L1', 'L2', 'Own scratchpad', '2 hops away', 'DRAM', 'All five at once'].map((nm, i) => ({
    name: nm, where: () => ({level: 0}), hold: i < 5 ? 0 : undefined,
    say: c => i < 5 ? `${c.g ? 'Gathers' : 'Scatters'} from ${c.LN[i].nm}: ${n(c.p + c.LN[i].k + '_c')} cycles per instruction, ${n(c.LN[i].r)} G elements/s for the chip, ${n(c.LN[i].e)} pJ each`
      : `${c.g ? 'Gathers' : 'Scatters'}, G elements/s: L1 ${n(c.p + 'l1_r')} · L2 ${n(c.p + 'l2_r')} · 2 hops ${n(c.p + 'rs_r')} · DRAM ${n(c.p + 'dr_r')}`,
    run: async (tok, c) => { gsStage(tok, c, i); await wait(tok, i < 5 ? 5200 : 1e12); }})),
};
function gsStage(tok, c, i) {
  const fx = c.fx, g = c.g, key = 'gs-' + (g ? 'g' : 's') + '-dram-512B';
  hiCells([c.rq, c.far].concat(Object.values(MSC)), true);
  if (!c.ch || c.ch.g.parentNode !== fx) {
    const SN = {l1: 'L1', l2: 'L2', sp: 'own scratchpad', rs: '2 hops away', dr: 'DRAM'};
    c.ch = bandChart(fx, g ? 'Gathers done' : 'Scatters done', c.LN.map(l => ({name: SN[l.k], val: '', f: key})), {note: 'done (log scale) · cycles each'});
    c.ch.rows.forEach((r, j) => { const y = +r.val.getAttribute('y'); T(r.g, BAND.x + BAND.w - 7, y, `${N[c.p + c.LN[j].k + '_c'].t} cyc`, 't-sm', 'end', 'gs-' + (g ? 'g' : 's') + '-dram-256K').style.fill = 'var(--ink)'; });
    c.trs = c.LN.map((l, j) => document.querySelector(`#race .tr[data-i="${j}"]`));
    c.toRq = g ? pts(reply(c.far, c.rq)) : pts(route(c.rq, c.far));
    pnReveal($('race'));
    // A count race on a log scale: each running lane's bar is log(1 + done) against the leader's, so a lane a hundred
    // times slower still shows (no bar restarts with every instruction). A lane drawn while paused shows its speed
    // instead, dimmed: the same log scale of instructions per unit time, the fastest lane full.
    const cmin = Math.min(...c.LN.map(l => l.c)), cmax = Math.max(...c.LN.map(l => l.c)), spd = l => Math.log10(10 * cmax / l.c) / Math.log10(10 * cmax / cmin);
    every(tok, t => {
      const ks = Object.keys(c.lanes).map(Number), done = {};
      ks.forEach(j => {
        if (c.lanes[j] === null && CLK.on && !REDUCED) c.lanes[j] = t;   // drawn while paused: it starts with the clock
        done[j] = REDUCED || c.lanes[j] === null ? null : Math.floor((t - c.lanes[j]) / (c.LN[j].c * c.SCALE));
      });
      const lead = Math.max(1, ...ks.map(j => done[j] || 0));
      ks.forEach(j => {
        const l = c.LN[j], tr = c.trs[j], still = done[j] === null, q = still ? spd(l) : Math.log10(1 + done[j]) / Math.log10(1 + lead);
        c.ch.rows[j].set(q); c.ch.rows[j].bar.style.opacity = still ? 0.4 : '';
        c.ch.rows[j].val.textContent = still ? '' : `${fnum(done[j], 0)} done`;
        if (tr) { const u = tr.querySelector('u'); u.style.width = (100 * q).toFixed(1) + '%'; u.style.opacity = still ? 0.4 : ''; tr.querySelector('s').textContent = still ? `${N[c.p + l.k + '_c'].t} cycles each` : `${fnum(done[j], 0)} done`; }
      });
    });
  }
  // the stage's level is the chart's marked row (the caption has its numbers); the partner two hops away is named
  c.ch.rows.forEach((r, j) => { const on = i < 5 && j === i; r.nm.style.fontWeight = on ? '700' : ''; r.nm.style.fill = on ? 'var(--ink)' : ''; });
  if (i >= 3 && (!c.farTag || c.farTag.parentNode !== fx)) c.farTag = callout(fx, c.far.sx, c.far.sy, [{t: `shire ${c.far.id}: 2 hops`, f: 'mesh.logical-map'}], {cell: c.far, side: side(c.far), fs: 20, col: 'var(--c4)'});
  const now = CLK.on ? CLK.t : null;
  if (i < 5) c.lanes[i] = now;
  else c.LN.forEach((l, j) => { c.lanes[j] = now; });   // the race: every lane from the same moment
  if (REDUCED) return;
  const shoot = (P, col) => { const pk = packet(fx, col, 10); quiet(travel(tok, fx, pk, P, 170 * (P.length - 1), {trail: false, linear: true}).then(() => pk.remove(), e => { pk.remove(); throw e; })); };
  if ((i === 3 || i === 5) && !c.rsOn) {
    c.rsOn = true; const t0 = CLK.t, d = V(c.p + 'rs_c') * c.SCALE / 8; let nx = 0;
    every(tok, t => { while (nx <= t - t0) { shoot(c.toRq, 'var(--c4)'); nx += d; } });
  }
  if ((i === 4 || i === 5) && !c.drOn) {
    c.drOn = true; const t0 = CLK.t, d = V(c.p + 'dr_c') * c.SCALE / 8; let nx = 0;
    every(tok, t => { while (nx <= t - t0) { const home = Math.floor(Math.random() * 32), hc = SH[home], mc = MSC[home % 8]; shoot(pts(g ? viaR(mc, hc, c.rq) : via(c.rq, hc, mc)), 'var(--c2)'); nx += d; } });
  }
}

/* ---- 6. the host over PCIe, timed on three cards on 27 September ---- */
FLOWS.F = {
  title: 'Host and PCIe',
  cap: () => CAPS.F(),
  setup(c) {
    c.pc = CELLS.find(x => x.type === 'pcie'); c.master = CELLS.find(x => x.type === 'master' && x.r === 0);
    flowPanel('F', 'The host over PCIe, timed',
      `<p class="pn-what">The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from ${n('dram_region')}), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.</p>`
      + legRows([
        ['the link', `trained at ${n('pcie_neg')} on every card: ${n('pcie_link')} per direction`, '', ''],
        ['DMA', `${n('pcie_h2d', 'GB/s')} to the card, ${n('pcie_d2h', 'GB/s')} back: ${n('pcie_h2d_pct')} and ${n('pcie_d2h_pct')} of the link`, '', ''],
        ['staged', `a program's copies: ${n('pcie_stg_h', 'GB/s')} (host memcpy ${n('pcie_memcpy', 'GB/s')} first, then the DMA)`, '', ''],
        ['into DRAM', `each line through its L3 home (PA[10:6]), which keeps it: ${n('pcie_l3pct')} of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the ${n('ms8')} memory shires (PA[8:6]) not timed`, '', ''],
        ['launch', `an empty kernel on ${n('cshires')} shires: ${n('pcie_b2b', 'µs')} each when queued, the card's own cost; one launch waited for takes ${n('pcie_launch', 'µs')}, the extra ${n('pcie_wait_rng')} mostly the runtime's ${n('poll500')} idle poll`, '', ''],
        ['small copies', `a lone 4 KB copy: ${n('pcie_4k', 'µs')}, the runtime's polling (${n('poll50')} in flight, ${n('poll500')} idle)`, '', ''],
      ])
      + `<p class="pn-what small">Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.</p>`);
  },
  stages: [
    {name: 'The link', where: () => ({level: 0}),
      say: () => `The host link: PCIe Gen4 x8, trained at ${n('pcie_neg')} on all three cards, ${n('pcie_link')} per direction by its figure`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.pc], true);
        for (let i = 0; i < 3; i++) { const pk = packet(fx, 'var(--c4)', 11); quiet(travel(tok, fx, pk, AP[0].host, 2000, {trail: i === 0, col: 'var(--c4)'}).then(() => pk.remove(), e => { pk.remove(); throw e; })); await wait(tok, 420); }
        await wait(tok, 1700);
        sayAt(c, fx, 1110, 70, [{t: 'PCIe Gen4 x8'}, {t: `${N.pcie_neg.t}, every card`, f: 'pcie.negotiated'}, {t: `${N.pcie_link.t} per direction`, f: 'pcie.negotiated'}], {side: 'l', col: 'var(--c4)', fs: 21});
      }},
    {name: 'DMA', where: () => ({level: 0}), hold: 0,
      say: () => `DMA alone: ${n('pcie_h2d', 'GB/s')} to the card (${n('pcie_h2d_pct')} of the link) and ${n('pcie_d2h', 'GB/s')} back (${n('pcie_d2h_pct')}), 256 MB copies`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.pc], true);
        pcieChart(c, 3);
        hostStream(tok, c, 'var(--c4)', 260);
        await wait(tok, 6000);
      }},
    {name: 'Staged', where: () => ({level: 0}), hold: 0,
      say: () => `A program's copy is staged: the runtime first copies into a bounce buffer at the host's memcpy rate (${n('pcie_memcpy', 'GB/s')}), then sends it: ${n('pcie_stg_h', 'GB/s')}`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.pc], true);
        pcieChart(c, 4);
        const hb = AP[0].hostBox;
        // (on a phone, in the band that folds under the die: under the host it would cover the I/O shire)
        const lines = [{t: 'memcpy, then DMA'}, {t: `memcpy ${N.pcie_memcpy.t} GB/s`, f: 'pcie.staged'}];
        if (PH) sayAt(c, fx, BAND.x - 20, BAND.y + 40, lines, {side: 'r', col: 'var(--c4)', fs: 20});
        else sayAt(c, fx, hb.x + hb.w / 2, hb.y + hb.h, lines, {side: 'd', col: 'var(--c4)', fs: 20});
        hostStream(tok, c, 'var(--c4)', 560, true);
        await wait(tok, 7000);
      }},
    {name: 'Into DRAM', where: () => ({level: 0}),
      say: () => `Each line of a copied buffer goes to its L3 home (PA[10:6]), which keeps it: ${n('pcie_l3pct')} of the lines then read at L3 latency (E55); the L3's later write-back to the ${n('ms8')} memory shires (PA[8:6]) is drawn dashed`,
      run: async (tok, c) => {
        const fx = c.fx; unsay(c);
        if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
        // eight lines of a buffer, their homes spread over the chip: line k's L3 home is shire k (PA[10:6]) and its
        // memory shire k % 8 (PA[8:6])
        const K = [0, 9, 18, 27, 4, 13, 22, 31];
        hiCells(K.map(k => SH[k]).concat(Object.values(MSC), [c.pc]), true);
        const legs = K.map((k, i) => quiet((async () => {
          await wait(tok, 200 * i);
          const hc = SH[k], mc = MSC[k % 8], pkg = AP[0].pkg[mc.id + ':' + (mc.id % 2)], pk = packet(fx, 'var(--c3)', 8);
          // measured (E55, fact pcie.write-l3): the host's write reaches the line's L3 home, which allocates the line
          await travel(tok, fx, pk, pts(route(c.pc, hc)), 1500, {col: 'var(--c3)', w: 4});
          await pulse(tok, fx, {x: hc.sx, y: hc.sy}, 500, 'var(--c3)', 24);
          // not timed: the L3's write-back to the memory shire and its DRAM package, a quiet dashed suggestion
          await travel(tok, fx, pk, pts(route(hc, mc)).concat([{x: mc.sx, y: pkg.y}, pkg]), 1800, {col: 'var(--c3)', w: 3, op: 0.5, dash: '6 8'});
        })()));
        await Promise.all(legs);
      }},
    {name: 'Launch', where: () => ({level: 0}),
      say: () => `The master shire (${n('master_id')}) starts the kernel on all ${n('cshires')} shires: ${n('pcie_b2b_rng')} each when queued; ${n('pcie_launch_rng')} when waited for, mostly the host's ${n('poll500')} poll`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.master, c.pc], true); unsay(c);
        if (c.hs) Object.values(c.hs).forEach(h => { h.stop = true; });   // the copies are done: the launch alone
        await travel(tok, fx, packet(fx, 'var(--c7)', 12), AP[0].host.slice(0, 2).concat(pts(route(c.pc, c.master))), 2200, {col: 'var(--c7)'});
        hiCells(Object.values(SH));
        const ps = Object.values(SH).map(x => pulse(tok, fx, {x: x.sx, y: x.sy}, 1500, 'var(--c1)', 40));
        await Promise.all(ps);
        if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
        c.bt = bandText(fx, 'An empty kernel', [{t: 'queued, each:'}, {t: N.pcie_b2b_rng.t, b: 1, f: 'pcie.launch'}, {t: "the card's own cost"}, {t: 'one, waited for:'}, {t: N.pcie_launch_rng.t, b: 1, f: 'pcie.launch'}, {t: 'mostly host polling', f: 'pcie.poll'}], 90);
      }},
    {name: 'Small copies', where: () => ({level: 0}),
      say: () => `A lone 4 KB copy takes ${n('pcie_4k_rng')}: it waits on the host's poll (every ${n('poll50')} busy, ${n('poll500')} idle), not on the link`,
      run: async (tok, c) => {
        const fx = c.fx; unsay(c);
        if (c.hs) Object.values(c.hs).forEach(h => { h.stop = true; });
        // the launch and the DRAM paths go: only the host link and the polling stay
        [...fx.children].forEach(el => { if (el !== c.bt) fadeOut(el, 320); });
        clearDim(); hiCells([c.pc], true);
        const hb = AP[0].hostBox, hc = {x: hb.x + hb.w / 2, y: hb.y + 24};
        const pk = packet(fx, 'var(--c4)', 9);
        await travel(tok, fx, pk, AP[0].host, 900, {trail: false});
        await travel(tok, fx, pk, AP[0].host.slice().reverse(), 900, {trail: false});
        pk.remove();
        const [bg, rc2, lt] = await ring(tok, fx, hc, 2600, 'var(--c4)', 'poll');
        [bg, rc2, lt].forEach(e => e && e.remove());
        if (c.bt && c.bt.parentNode) c.bt.remove();
        if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
        c.bt = bandText(fx, 'A lone 4 KB copy', [{t: N.pcie_4k_rng.t, b: 1, f: 'pcie.small'}, {t: 'the host polls every'}, {t: `${N.poll50.t} (busy)`, f: 'pcie.poll'}, {t: `${N.poll500.t} (idle)`, f: 'pcie.poll'}], 90);
      }},
  ],
};
function pcieChart(c, upto) {
  const fx = c.fx;
  if (c.ch && c.ch.g.parentNode === fx && c.chN === upto) return;
  if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
  const rows = [['link figure', 'pcie_link', 'pcie.negotiated'], ['to card, DMA', 'pcie_h2d', 'pcie.h2d'], ['back, DMA', 'pcie_d2h', 'pcie.d2h'], ['to card, staged', 'pcie_stg_h', 'pcie.staged']].slice(0, upto);
  c.ch = bandChart(fx, 'GB/s per direction', rows.map(r => ({name: r[0], val: N[r[1]].t, f: r[2], col: 'var(--c4)'})), {y: 150}); c.chN = upto;
  rows.forEach((r, i) => c.ch.rows[i].set(V(r[1]) / V('pcie_link')));
}
function hostStream(tok, c, col, every_ms, staged) {
  if (REDUCED) return;
  const fx = c.fx, t0 = CLK.t, P = AP[0].host; let nx = 0;
  c.hs = c.hs || {}; Object.values(c.hs).forEach(s => { s.stop = true; });
  const st = c.hs[staged ? 's' : 'd'] = {stop: false};
  every(tok, t => {
    if (st.stop) return;
    while (nx <= t - t0) {
      const pk = packet(fx, col, 9);
      const go = () => travel(tok, fx, pk, P, 1500, {trail: false, linear: true});
      quiet((staged ? pulse(tok, fx, P[0], 380, col, 18).then(go) : go()).then(() => pk.remove(), e => { pk.remove(); throw e; }));
      at(pk, P[0]); nx += every_ms;
    }
  });
}

/* ---- 7. a matmul on the tensor unit: TensorLoad into the L1 scratchpad, B through TenB, TensorFMA ---- */
const mmPick = () => ({sid: shireOfCamera() != null ? shireOfCamera() : ST.sid, nb: Z.level === 2 ? Z.nb : 0, mi: Z.level === 2 ? Z.mi : 0});
/* 48 slots over the L1 scratchpad's 3 KB, 16 lines each for A, B and the next A (drawn in order; which set holds
   which line is not drawn as a fact) */
function scpSlots(c, fx) {
  if (c.slots && c.slots.g.parentNode === fx) return c.slots;
  const b = AP[2].scpBox, g = E('g', {}, fx), cols = 12, rows = 4, w = b.w / cols, h = b.h / rows, cells = [];
  for (let i = 0; i < cols * rows; i++) {
    const x = b.x + (i % cols) * w, y = b.y + Math.floor(i / cols) * h;
    cells.push(S(E('rect', {x: x + 3, y: y + 2, width: w - 6, height: h - 4, rx: 2}, g), {fill: 'var(--c7)', fillOpacity: 0}));
  }
  c.slots = {g, cells, at: i => ({x: b.x + (i % cols) * w + w / 2, y: b.y + Math.floor(i / cols) * h + h / 2})};
  return c.slots;
}
async function streamRows(tok, c, fx, from, dest, ms, col, fill, via) {
  const ps = [];
  for (let r = 0; r < 16; r++) {
    const pk = packet(fx, col, 6), to = dest(r);
    const p = travel(tok, fx, pk, [from].concat(via ? via(to) : [], [to]), ms, {trail: false}).then(() => { pk.remove(); fill(r); }, e => { pk.remove(); throw e; });
    p.catch(() => {});   // handled: a stage cancelled mid-loop leaves the rows already sent without a waiter
    ps.push(p);
    await wait(tok, 110);
  }
  await Promise.all(ps);
}
/* a note in the minion view, at the right end of the frame's header (the harts' numbers there are hidden while it
   shows, CSS .m-harts): it covers no drawn part */
const NOTE_AT = () => ({x: MF.x + MF.w - 20, y: MF.y + 7});
function note(c, fx, lines, col) {
  if (c.cnt && c.cnt.parentNode) c.cnt.remove();
  const p = NOTE_AT();
  c.cnt = callout(fx, p.x, p.y, lines, {tr: true, fs: 18, col: col || 'var(--c7)'});
  c.cnt.classList.add('note');
  return c.cnt;
}
async function flashLanes(tok, ms, rows) {
  const P2 = AP[2], cells = (rows || [0]).flatMap(k => P2.units[k] || []), orig = cells.map(r => r.style.fillOpacity);
  const back = () => cells.forEach((r, i) => { r.style.fillOpacity = orig[i]; });
  try { await anim(tok, ms, q => { cells.forEach((r, i) => { r.style.fillOpacity = q >= 1 ? orig[i] : (0.3 + 0.55 * Math.abs(Math.sin(q * 40 + i * 0.7))).toFixed(2); }); }); }
  finally { back(); }
}
FLOWS.G = {
  title: 'Matmul',
  pick: mmPick,
  cap: () => CAPS.G(),
  setup(c) {
    Object.assign(c, c.pick); ST.sid = c.sid;
    flowPanel('G', 'A matmul on the tensor unit',
      `<p class="pn-what">One 16×16×16 fp32 step of a matmul, as the benchmark that sustains ${n('tflops')} TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.</p>`
      + legRows([
        ['TensorLoad A', '16 lines from the L2, three cards', n('tl_l2'), ''],
        ['B through TenB', 'streamed with a paired load, into TenB', '', ''],
        ['TensorFMA', `with B in TenB (${n('tfma546')} with B in the L1 scratchpad)`, n('tfma_tenb'), ''],
        ['the next A', 'loaded during the FMA: an op takes no longer than the FMA', n('mm_op'), ''],
        ['32 minions', `each loads from the shire's L2; the cycles with all ${n('n1024')} loading`, n('tl_all_l2'), ''],
        ['1,024 minions', `${n('tflops')} TFLOP/s fp32, against a peak of ${n('peak_tf32')}`, '', ''],
        ['fed from DRAM', `${n('mm_dram_tf')} TFLOP/s; a load with all loading: ${n('tl_all_dr')} cycles; per op:`, n('mm_dram_op'), ''],
      ])
      + `<p class="pn-what small">Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.</p>`);
  },
  stages: [
    {name: 'Load A', where: c => ({level: 2, sid: c.sid, nb: c.nb, mi: c.mi}),
      mark: () => [{t: `TensorLoad A: ${N.tl_l2.t} cycles`, f: 'tl.one'}],
      say: () => `Hart 0 issues TensorLoad: 16 lines of A (1 KB) come from the shire's L2 over ET-Link into the L1 scratchpad, bypassing the L1 cache: ${n('tl_l2')} cycles`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, sl = scpSlots(c, fx);
        note(c, fx, [{t: 'TensorLoad A: 16 lines'}]);
        await pulse(tok, fx, P2.hart0, 900, 'var(--c2)', 40);
        await streamRows(tok, c, fx, P2.etlPort, r => sl.at(r), 1200, 'var(--c7)', r => { sl.cells[r].style.fillOpacity = 0.75; });
        note(c, fx, [{t: 'A in the L1 scratchpad'}, {t: `${N.tl_l2.t} cycles from the L2`, f: 'tl.one'}]);
      }},
    {name: 'B via TenB', where: c => ({level: 2, sid: c.sid, nb: c.nb, mi: c.mi}),
      mark: () => [{t: 'B streams through TenB'}],
      say: () => `A paired TensorLoad streams the 16 rows of B into TenB, next to the lanes; the benchmark does this for every op`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, tb = P2.tenb, sl = scpSlots(c, fx); sl.cells.slice(0, 16).forEach(r => { r.style.fillOpacity = 0.75; });
        const cw = 13, rh = 17, rx0 = tb.x + tb.w - 4 * cw - 5, cell = r => ({x: rx0 + (r % 4) * cw, y: tb.y + 9 + Math.floor(r / 4) * rh});   // a 4 x 4 block right of TenB's labels
        if (!c.tbRows || c.tbRows[0].parentNode !== fx) c.tbRows = Array.from({length: 16}, (_, r) => S(E('rect', {x: cell(r).x, y: cell(r).y, width: cw - 3, height: rh - 3, rx: 2}, fx), {fill: 'var(--c2)', fillOpacity: 0}));
        note(c, fx, [{t: 'B: 16 rows through TenB'}]);
        // out of the port to the frame's right gutter, up it, and in above TenB: over no text
        const gR = MF.x + MF.w - 12, gT = MF.y + 274;
        await streamRows(tok, c, fx, P2.etl, r => ({x: cell(r).x + cw / 2, y: cell(r).y + rh / 2}), 1500, 'var(--c2)', r => { c.tbRows[r].style.fillOpacity = 0.8; },
          to => [{x: gR, y: P2.etl.y}, {x: gR, y: gT}, {x: to.x, y: gT}]);
      }},
    {name: 'TensorFMA', where: c => ({level: 2, sid: c.sid, nb: c.nb, mi: c.mi}),
      mark: () => [{t: `TensorFMA: ${N.tfma_tenb.t} cycles`, f: 'tfma.tenb'}],
      say: () => `TensorFMA: the sequencer runs C += A·B on the 8 lanes' FMA units, ${n('tfma_tenb')} cycles with B in TenB (${n('tfma546')} with B in the L1 scratchpad), the same for every data pattern`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx;
        note(c, fx, [{t: 'TensorFMA: C += A · B'}]);
        await pulse(tok, fx, P2.seq, 900, 'var(--c2)', 60);
        await flashLanes(tok, 4200, [0]);
        note(c, fx, [{t: `TensorFMA: ${N.tfma_tenb.t} cycles`, f: 'tfma.tenb'}, {t: `${N.tfma546.t} with B in the L1`, f: 'minion.tensorfma-546'}]);
      }},
    {name: 'Next A, hidden', where: c => ({level: 2, sid: c.sid, nb: c.nb, mi: c.mi}),
      mark: () => [{t: `${N.mm_op.t} cycles per op`, f: 'mm.reload'}],
      say: () => `The next A loads into the other buffer while the FMA runs: the benchmark takes ${n('mm_op')} cycles per op, no more than the FMA alone, so the ${n('tl_l2')}-cycle load is hidden`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, sl = scpSlots(c, fx); unsay(c);
        sl.cells.slice(0, 16).forEach(r => { r.style.fillOpacity = 0.75; });
        note(c, fx, [{t: 'next A loads during the FMA'}]);
        await Promise.all([flashLanes(tok, 4600, [0]), streamRows(tok, c, fx, P2.etlPort, r => sl.at(16 + r), 1200, 'var(--c7)', r => { sl.cells[16 + r].style.fillOpacity = 0.45; })]);
        note(c, fx, [{t: `${N.mm_op.t} cycles per op`, f: 'mm.reload'}, {t: 'the load is hidden'}]);
      }},
    {name: '32 minions', where: c => ({level: 1, sid: c.sid}),
      mark: () => [{t: 'every minion of the shire'}],
      say: () => `Every minion of the shire does the same, loading its tiles from the shire's L2; with all ${n('n1024')} minions loading, a 16-line load takes ${n('tl_all_l2')} cycles`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, keys = Object.keys(P1.min);
        const ps = keys.map((k, i) => { const m = P1.min[k], B = P1.bank[i % 4], pk = packet(fx, 'var(--c7)', 7), q = {x: m.x + m.w / 2, y: m.y + m.h / 2};
          at(pk, B); return wait(tok, (i % 8) * 90).then(() => travel(tok, fx, pk, [B, {x: B.x, y: P1.xbarY}, {x: P1['ch' + k[0]].x, y: P1.xbarY}, q], 1500, {trail: false})).then(() => pk.remove(), e => { pk.remove(); throw e; }); });
        await Promise.all(ps);
        await Promise.all(keys.map(k => { const m = P1.min[k]; return pulse(tok, fx, {x: m.x + m.w / 2, y: m.y + m.h / 2}, 1300, 'var(--c2)', 26); }));
        // every minion stays lit: all 32 have their tiles (a glow inside each box, under its name)
        keys.forEach(k => { const g = P1.minG[k], sh = g && g.querySelector('.shape'), m = P1.min[k]; if (!sh) return;
          const r = S(E('rect', {class: 'glow', x: m.x + 3, y: m.y + 3, width: m.w - 6, height: m.h - 6, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: isDark() ? 0.42 : 0.3});
          g.insertBefore(r, sh.nextSibling); fadeIn(r, 400); });
        sayAt(c, fx, SF.x + SF.w, SF.y + 250, [{t: '32 minions, each its own tiles'}, {t: `all 1,024 loading: ${N.tl_all_l2.t} cycles`, f: 'tl.all'}, {t: 'per 16-line load from the L2'}], {side: 'r', fs: 20});
      }},
    {name: '1,024 minions', where: () => ({level: 0}), dim: false,
      say: () => `All ${n('n1024')} minions: ${n('tflops')} TFLOP/s fp32 on all three cards, against a peak of ${n('peak_tf32')} at ${n('mhz')}`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        c.glow = glowTiles(tok, fx, 1, 'var(--c2)'); c.glowFx = fx;
        await wait(tok, 900);
        c.co6 = callout(fx, DW / 2, DH / 2, [{t: `${N.tflops.t} TFLOP/s fp32`, f: 'mm-rate'}, {t: `peak ${N.peak_tf32.t}`, f: 'mm-peak'}, {t: `${N.mm_op.t} cycles per op`, f: 'mm.reload'}], {side: 'u', fs: 24});
      }},
    {name: 'From DRAM', where: () => ({level: 0}),
      say: () => `Tiles too big for the L2: every load comes from DRAM, ${n('tl_all_dr')} cycles per 16-line load with all minions loading, and the matmul falls to ${n('mm_dram_tf')} TFLOP/s`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH).concat(Object.values(MSC)), true);
        // the rate falls: stage 6's callout goes and its glow dims where it is (no second glow on top)
        if (c.co6) { fadeOut(c.co6); c.co6 = null; }
        if (c.glow && c.glowFx === fx) c.glow.amp = 0.12; else { c.glow = glowTiles(tok, fx, 0.12, 'var(--c2)'); c.glowFx = fx; }
        if (!REDUCED) {
          const t0 = CLK.t; let nx = 0;
          // each line from its memory shire through its L3 home to the loading shire, as an L2 miss returns (fact sc.l3-miss)
          every(tok, t => { while (nx <= t - t0) { const s = Object.values(SH)[Math.floor(Math.random() * 32)], home = Math.floor(Math.random() * 32), m = MSC[home % 8], pk = packet(fx, 'var(--c3)', 8);
            const P = pts(viaR(m, SH[home], s));
            quiet(travel(tok, fx, pk, P, 380 * Math.max(4, P.length - 1), {trail: false, even: true, linear: true}).then(() => pk.remove(), e => { pk.remove(); throw e; })); nx += 240; } });
        }
        await wait(tok, 1200);
        callout(fx, DW / 2, DH / 2, [{t: `from DRAM: ${N.mm_dram_tf.t} TFLOP/s`, f: 'mm.dram'}, {t: `${N.mm_dram_op.t} cycles per op`, f: 'mm.dram'}, {t: `a load: ${N.tl_all_dr.t} cycles`, f: 'tl.all'}], {side: 'u', fs: 22, col: 'var(--c3)'});
        await wait(tok, 1e12);
      }},
  ],
};

/* ---- 8. the same matmul on different data: the watts and the heat ---- */
const WPAT = [['zeros', 'w_zeros'], ['ones', 'w_ones'], ['random', 'w_randn']];
function wattChart(c, upto) {
  const fx = c.fx;
  if (c.wc && c.wc.g.parentNode === fx && c.wcN === upto) return c.wc;
  if (c.wc && c.wc.g.parentNode) c.wc.g.remove();
  const max = V('w_randn') * 1.12;
  c.wc = bandChart(fx, 'Board watts', WPAT.slice(0, upto).map(([nm, k]) => ({name: nm, val: `${N[k].t} W`, f: 'mm.w-data', col: 'var(--c2)'})), {note: 'at the launch temp.', note2: `idle ${N.w_idle.t} W marked`});
  c.wcN = upto;
  c.wc.rows.forEach((r, i) => { r.set(V(WPAT[i][1]) / max); S(E('line', {x1: BAND.x + BAND.w * V('w_idle') / max, x2: BAND.x + BAND.w * V('w_idle') / max, y1: r.y - 4, y2: r.y + 34}, c.wc.g), {stroke: 'var(--ink)', strokeWidth: 3}); });
  return c.wc;
}
const wAmp = k => (V(k) - V('w_idle')) / (V('w_randn') - V('w_idle'));
function raceChart(tok, c, rows, title) {
  const fx = c.fx, g = E('g', {class: 'band'}, fx), X0 = BAND.x, W = BAND.w, TMAX = 602, SPEED = 50;   // s of card time per s shown
  T(g, X0, BAND.y + 22, title, 't-labb halo');
  T2(g, X0, BAND.y + 46, ['time to 90 °C;', `1 s here is ${SPEED} s`], 't-sm halo');
  const bars = rows.map((r, i) => {
    const y = BAND.y + 80 + i * 64;
    T(g, X0, y + 18, r.name, 't-lab halo', 'start', r.f);
    E('rect', {class: 'btrack', x: X0, y: y + 25, width: W, height: 26, rx: 5}, g);
    const bar = S(E('rect', {class: 'bbar', x: X0, y: y + 25, width: 0, height: 26, rx: 5}, g), {fill: r.col});
    const lab = T(g, X0 + 6, y + 44, '', 't-labb', 'start', r.f);
    return {bar, lab, r};
  });
  fadeIn(g);
  const draw = s => bars.forEach(b => {
    const end = b.r.cap != null ? b.r.cap : TMAX, now = Math.min(s, end);
    b.bar.setAttribute('width', (W * now / TMAX).toFixed(1));
    b.lab.textContent = s >= end ? (b.r.cap != null ? `${b.r.txt} s` : b.r.txt) : `${fnum(now, 0)} s`;
  });
  return anim(tok, 1000 * TMAX / SPEED, q => draw(q * TMAX));
}
FLOWS.H = {
  title: 'Data → watts',
  pick: () => ({sid: shireOfCamera() != null ? shireOfCamera() : ST.sid}),
  cap: () => CAPS.H(),
  setup(c) {
    c.sid = c.pick.sid;
    flowPanel('H', 'The same matmul, different data',
      `<p class="pn-what">The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same ${n('w_tflops')} TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included; the benchmark of flow 7 counts ${n('tflops')} TFLOP/s on the device.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.</p>`
      + legRows([
        ['zeros', `${n('w_zeros', 'W')} at the board (aifoundry2, at the launch temperature)`, '', ''],
        ['ones', `${n('w_ones', 'W')}`, '', ''],
        ['random', `${n('w_randn', 'W')}, from ${n('w_idle', 'W')} idle`, '', ''],
        ['why', `bits that flip: ${n('e_mac32')} pJ per fp32 multiply-add on random data, ${n('e_mac32z')} on zeros, above idle`, '', ''],
        ['three cards', `above zeros: ones ${n('w_ones_d', 'W')}, random ${n('w_rand_d', 'W')}`, '', ''],
        ['the heat race', `from ${n('race_t0')} to 90 °C: random ${n('race_rand', 's')}, ones ${n('race_ones', 's')}, zeros never (${n('race_zero', 's')} runs)`, '', ''],
        ['fewer minions', `random data on 768 minions: ${n('race_768', 's')}; on 128: ${n('race_128')}`, '', ''],
      ])
      + `<p class="pn-what small">The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: ${n('leak80')} at 80 °C.</p>`);
  },
  stages: [
    ...WPAT.map(([nm, k], i) => ({name: nm[0].toUpperCase() + nm.slice(1), where: () => ({level: 0}), dim: false,
      say: () => i === 0 ? `Zeros: ${n('w_zeros', 'W')} at the board (at the launch temperature), hardly above the ${n('w_idle', 'W')} idle, at ${n('w_tflops')} TFLOP/s`
        : i === 1 ? `Ones: ${n('w_ones', 'W')}, the same ${n('w_tflops')} TFLOP/s` : `Random data: ${n('w_randn', 'W')}, the same instructions and the same ${n('w_tflops')} TFLOP/s`,
      run: async (tok, c) => {
        const fx = c.fx;
        if (c.glow && c.glowFx === fx) c.glow.amp = wAmp(k); else { c.glow = glowTiles(tok, fx, wAmp(k), 'var(--c2)'); c.glowFx = fx; }
        wattChart(c, i + 1);
        // under the chart's three rows (it grows by a row a stage), in the band column: it covers no tile
        if (i === 0) c.coT = callout(fx, BAND.x, BAND.y + 30 + 52 + 3 * 68 + 18, [{t: `${N.w_tflops.t} TFLOP/s`, f: 'mm.w-data'}, {t: 'on every data set'}], {tl: true, fs: 21});
        await wait(tok, 1500);
      }})),
    {name: 'Why: bits flip', where: c => ({level: 2, sid: c.sid, nb: 0, mi: 0}),
      mark: () => [{t: `${N.e_mac32.t} pJ per MAC, random`, f: 'e-tfma-fp32'}],
      say: () => `Why: what costs energy is bits that flip. Per fp32 multiply-add, above idle: ${n('e_mac32')} pJ on random data, ${n('e_mac32z')} pJ on zeros`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, cells = P2.units[0].concat(P2.units[1], P2.units[2]), orig = cells.map(r => r.style.fillOpacity);
        const phase = async (lab, amp, ms) => {
          note(c, fx, [{t: lab}], 'var(--c2)');
          await anim(tok, ms, q => cells.forEach((r, i) => { r.style.fillOpacity = q >= 1 ? orig[i] : (0.08 + amp * 0.8 * (0.5 + 0.5 * Math.sin(q * 90 + i * 2.3 + Math.sin(i * 7.1) * 3))).toFixed(2); }));
        };
        try {
          await phase('zeros: almost nothing flips', 0.03, 2200);
          await phase('ones', wAmp('w_ones'), 2200);
          await phase('random: most bits toggle', 1, 2600);
        } finally { cells.forEach((r, i) => { r.style.fillOpacity = orig[i]; }); }
        note(c, fx, [{t: `${N.e_mac32.t} pJ per MAC, random`, f: 'e-tfma-fp32'}, {t: `${N.e_mac32z.t} pJ on zeros`, f: 'e-tfma-fp32-zeros'}], 'var(--c2)');
      }},
    {name: 'Three cards', where: () => ({level: 0}), dim: false,
      say: () => `On all three cards: ones cost ${n('w_ones_d', 'W')} more than zeros and random data ${n('w_rand_d', 'W')} more, at the board`,
      run: async (tok, c) => {
        const fx = c.fx; if (c.wc && c.wc.g.parentNode) c.wc.g.remove(); c.wcN = 0;
        if (c.coT) { fadeOut(c.coT); c.coT = null; }
        if (c.glow && c.glowFx === fx) c.glow.amp = 1; else { c.glow = glowTiles(tok, fx, 1, 'var(--c2)'); c.glowFx = fx; }
        // grouped by card (CARDNAME): ones and random data side by side, keyed once
        const G = [['a2', 'w_od_a2', 'w_rd_a2'], ['a3', 'w_od_a3', 'w_rd_a3'], ['a1c1', 'w_od_a1', 'w_rd_a1']];
        const ch = bandGroups(fx, 'Watts above zeros', [{name: 'ones', col: 'var(--c4)'}, {name: 'random', col: 'var(--c2)'}],
          G.map(([cd, ko, kr]) => ({name: CARDNAME[cd], vals: [ko, kr].map(k => ({t: `${N[k].t} W`, f: 'mm.w-3cards', q: V(k) / 30}))})), {y: 30});
        await anim(tok, 1600, q => ch.bars.forEach(b => b.set(easeS(q) * b.q)));
      }},
    {name: 'The heat race', where: () => ({level: 0}), dim: false,
      say: () => `The heat race on aifoundry2, from ${n('race_t0')} to the 90 °C cap: random data gets there in ${n('race_rand', 's')}, ones in ${n('race_ones', 's')}, zeros never in a ${n('race_zero', 's')} run`,
      run: async (tok, c) => {
        const fx = c.fx; fx.textContent = ''; clearGlow(); c.glow = null; c.wc = null; c.coT = null;
        const warm = glowTiles(tok, fx, 0.2, 'var(--c2)');
        const rows = [{name: 'random', cap: V('race_rand'), txt: N.race_rand.t, f: 'heat.race', col: 'var(--c2)'}, {name: 'ones', cap: V('race_ones'), txt: N.race_ones.t, f: 'heat.race', col: 'var(--c4)'}, {name: 'zeros', cap: null, txt: `never, ${N.race_zero.t} s`, f: 'heat.race', col: 'var(--c1)'}];
        const t0 = CLK.t; if (REDUCED) warm.amp = 1; else every(tok, t => { warm.amp = Math.min(1, 0.2 + (t - t0) / 1600); });
        await raceChart(tok, c, rows, 'All 1,024 minions');
      }},
    {name: 'Fewer minions', where: () => ({level: 0}), dim: false,
      say: () => `Random data on fewer minions per shire buys time: 768 minions ${n('race_768', 's')}, 512 ${n('race_512', 's')}, 384 ${n('race_384', 's')}, 256 ${n('race_256', 's')}, and 128 never`,
      run: async (tok, c) => {
        const fx = c.fx; fx.textContent = ''; clearGlow(); c.glow = null; c.coT = null;
        glowTiles(tok, fx, 0.55, 'var(--c2)');
        const rows = [['768', 'race_768'], ['512', 'race_512'], ['384', 'race_384'], ['256', 'race_256'], ['128', 'race_128']].map(([m, k]) => ({name: `${m} minions`, cap: N[k].t === 'never' ? null : V(k), txt: N[k].t === 'never' ? `never, ${N.race_zero.t} s` : N[k].t, f: 'heat.fewer', col: 'var(--c2)'}));
        await raceChart(tok, c, rows, 'Random data');
      }},
  ],
};

/* ---- 9. one hot line stops a shire ---- */
FLOWS.I = {
  title: 'Hot line',
  cap: () => CAPS.I(),
  setup(c) {
    c.host = SH[0]; c.rem = SH[8] && hops(SH[8], SH[0]) === 1 ? SH[8] : Object.values(SH).find(x => hops(x, SH[0]) === 1);
    flowPanel('I', 'One hot line stops a shire',
      `<p class="pn-what">One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.</p>`
      + legRows([
        ['one line', `the bank retires one atomic every ${n('hot10')}, about ${n('hot60')} for the chip`, '', ''],
        ['fair shares', `the host shire gets ${n('hot_host')} of an even share, the lowest shire ${n('hot_min')}`, '', ''],
        ['the host alone', "the host's minions read their own scratchpad", '', ''],
        ['21 requesters', `21 minions of one other shire hammer a word in the host: the host keeps ${n('hot21')}% of its rate`, '', ''],
        ['22 requesters', `the host stops: ${n('hot22')}`, '', ''],
        ['spread it', `over 32 lines, one per shire: ${n('hot031')} per atomic, ${n('hot1919')}, ${n('hot32x')}; ${n('hot_nj')} against ${n('hot_nj_s')} each, ${n('hot17x')}`, '', ''],
      ])
      + `<p class="pn-what small">Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.</p>`);
  },
  stages: [
    {name: 'One line', where: () => ({level: 0}), hold: 0,
      say: () => `Every minion hammers one global atomic in shire 0: its bank retires one every ${n('hot10')}, about ${n('hot60')} for the whole chip`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.host], true);
        // right of the die, under the host: the packets converge on shire 0 under no text
        c.co1 = callout(fx, VB.x + VB.w - 4, 26, [{t: 'one line in shire 0'}, {t: `an atomic every ${N.hot10.t}`, f: 'hot-cost'}], {tr: true, fs: 21});
        hotStream(tok, c, Object.values(SH).filter(s => s !== c.host), () => c.host, 150);
        await wait(tok, 6500);
      }},
    {name: 'Fair shares', where: () => ({level: 0}), dim: false,
      say: () => `The atomic is fair: with all 32 shires at it, the host shire gets ${n('hot_host')} of an even share and the lowest shire ${n('hot_min')}`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        if (!c.hs1) hotStream(tok, c, Object.values(SH).filter(s => s !== c.host), () => c.host, 150);
        const b = c.co1 && c.co1.parentNode === fx ? c.co1._box : null;
        const ch = c.shares = bandChart(fx, 'Shares', [{name: 'host shire', val: N.hot_host_rng.t, f: 'hot.fair'}, {name: 'lowest shire', val: N.hot_min_rng.t, f: 'hot.fair'}], {note: '1 = even, three cards', y: b ? b.y + b.h + 16 : BAND.y + 90});
        ch.rows[0].set(V('hot_host') / 1.2); ch.rows[1].set(V('hot_min') / 1.2);
        await wait(tok, 1200);
      }},
    {name: 'The host alone', where: () => ({level: 1, sid: 0}), hold: 0,
      mark: () => [{t: "the host's own loads"}],
      say: () => `Inside shire 0: its own minions read their scratchpad, through the same banks`,
      run: async (tok, c) => { hostLoads(tok, c, 1); await wait(tok, 5200); }},
    {name: '21 requesters', where: () => ({level: 1, sid: 0}), hold: 0,
      mark: c => [{t: `21: the host keeps ${N.hot21.t}%`, f: 'hot.cliff'}],
      say: () => `21 minions in one other shire hammer one word in this shire's bank: the host keeps ${n('hot21')}% of its rate`,
      run: async (tok, c) => { remoteAtomics(tok, c, 21); hostLoads(tok, c, 1); await wait(tok, 6500); }},
    {name: '22: the host stops', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: `22: ${N.hot22.t}`, f: 'hot.cliff'}],
      say: () => `22 requesters: the bank's queue is full, and the host shire's own loads stop: ${n('hot22')} of its rate`,
      run: async (tok, c) => {
        // one message says it: the host's loads stop (hostLoads' own callout, in --bad)
        remoteAtomics(tok, c, 22); hostLoads(tok, c, 0);
        await wait(tok, 2800);
      }},
    {name: 'Spread it', where: () => ({level: 0}), dim: false,
      say: () => `Spread over 32 lines, one per shire: ${n('hot031')} per atomic and ${n('hot1919')}, ${n('hot32x')} the rate, at ${n('hot_nj_s')} each against ${n('hot_nj')}: ${n('hot17x')} less energy`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        // this stage's message replaces stage 1's callout and stage 2's shares
        if (c.co1) { fadeOut(c.co1); c.co1 = null; }
        if (c.shares && c.shares.g.parentNode) { fadeOut(c.shares.g); c.shares = null; }
        const all = Object.values(SH);
        hotStream(tok, c, all, s => all[(all.indexOf(s) + 1 + Math.floor(Math.random() * 31)) % 32], 30);
        await wait(tok, 1200);
        callout(fx, DW / 2, DH / 2, [{t: `${N.hot1919.t}: ${disp(N.hot32x.t)}`, f: 'hot-cost'}, {t: `${N.hot_nj_s.t} per atomic, not ${N.hot_nj.t}`, f: 'hot-energy'}], {side: 'u', fs: 24});
        await wait(tok, 1e12);
      }},
  ],
};
function hotStream(tok, c, from, to, emit) {
  if (REDUCED) return;
  if (c.hsSt) c.hsSt.stop = true;
  const fx = c.fx, t0 = CLK.t, st = c.hsSt = {stop: false}; let nx = 0; c.hs1 = true;
  every(tok, t => { if (st.stop) return; while (nx <= t - t0) { const s = from[Math.floor(Math.random() * from.length)], d = to(s), pk = packet(fx, 'var(--c7)', 8);
    quiet(travel(tok, fx, pk, pts(route(s, d)), 320 * Math.max(1, hops(s, d)), {trail: false, even: true, linear: true}).then(() => pk.remove(), e => { pk.remove(); throw e; })); nx += emit; } });
}
/* inside the host shire: its own loads (rate 1, or 0 once stopped: they wait at the bank) and the remote atomics */
function hostLoads(tok, c, rate) {
  const P1 = AP[1], fx = c.fx, keys = Object.keys(P1.min).slice(0, 22);
  if (!c.hl || c.hl.fx !== fx) {
    c.hl = {fx, rate, t0: CLK.t, nx: 0, q: []};
    if (!REDUCED) every(tok, t => {
      const h = c.hl; if (h.rate <= 0) return;
      while (h.nx <= t - h.t0) {
        const k = keys[Math.floor(Math.random() * keys.length)], m = P1.min[k], B = P1.bank[Math.floor(Math.random() * 4)], q = {x: m.x + m.w / 2, y: m.y + m.h / 2}, pk = packet(fx, 'var(--c1)', 7);
        h.q.push(pk);
        quiet(travel(tok, fx, pk, [q, {x: P1['ch' + k[0]].x, y: q.y}, {x: P1['ch' + k[0]].x, y: P1.xbarY}, {x: B.x, y: P1.xbarY}, B], 1400, {trail: false, linear: true})
          .then(() => { if (c.hl.rate > 0) { pk.remove(); h.q.splice(h.q.indexOf(pk), 1); } }, e => { pk.remove(); throw e; }));
        h.nx += 170;
      }
    });
  }
  c.hl.rate = rate;
  if (rate <= 0 && !c.hl.pile) {
    // stopped: the host's loads wait in a row between the neighbourhoods and the crossbar, and none gets through; the
    // hot bank's queue is full of the remote atomics (drawn in its sub-bank row only)
    c.hl.q.forEach(pk => pk.remove()); c.hl.q = [];
    const pile = c.hl.pile = E('g', {}, fx), x0 = SF.x + 40, x1 = SF.x + SF.w - 40, y = SF.y + 345;
    keys.forEach((k, i) => at(packet(pile, 'var(--c1)', 5, true), {x: x0 + (x1 - x0) * i / (keys.length - 1), y}));
    const B = P1.bank[0].box, nq = Math.floor((B.w - 20) / 14);
    for (let i = 0; i < nq; i++) at(packet(pile, 'var(--c7)', 5, true), {x: B.x + 17 + i * 14, y: B.y + 55});
    fadeIn(pile);
  }
  if (c.hlab && c.hlab.parentNode) c.hlab.remove();
  const L1 = rate > 0 ? (c.remN ? [{t: "the host's loads"}, {t: `${N.hot21.t}%`, f: 'hot.cliff'}, {t: 'of their rate alone'}] : [{t: "the host's loads"}, {t: 'their rate alone'}]) : [{t: "the host's loads stop"}, {t: `${N.hot22.t} of their rate`, f: 'hot.cliff'}];
  c.hlab = callout(fx, SF.x + SF.w, SF.y + 160, L1, {side: 'r', fs: 20, col: rate > 0 ? 'var(--c1)' : 'var(--bad)'});
}
function remoteAtomics(tok, c, nreq) {
  c.remN = nreq;
  if (REDUCED || c.ra) return;
  const P1 = AP[1], fx = c.fx, B = P1.bank[0], top = {x: P1.stop.x + 90, y: SF.y - 40}, t0 = CLK.t; let nx = 0; c.ra = true;
  const path = [top, P1.stop, {x: P1.stop.x, y: B.box.y - 8}, {x: B.x, y: B.box.y - 8}, B];
  if (!c.raLab) c.raLab = callout(fx, top.x, top.y + 10, [{t: 'remote atomics from one other shire'}], {side: 'r', fs: 19, col: 'var(--c7)'});
  every(tok, t => { while (nx <= t - t0) { const pk = packet(fx, 'var(--c7)', 7);
    quiet(travel(tok, fx, pk, path, 1300, {trail: false, linear: true}).then(() => pk.remove(), er => { pk.remove(); throw er; })); nx += 95; } });
}

/* ---- 0. the allreduce tree: up with TensorReduce, back down with TensorBroadcast ---- */
const lsb = m => { let h = 0; while (m && !(m & 1)) { m >>= 1; h++; } return h; };
FLOWS.J = {
  title: 'Allreduce',
  cap: () => CAPS.J(),
  setup(c) {
    flowPanel('J', 'The allreduce tree',
      `<p class="pn-what">TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: ${src('at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared', 'ar.tree')}. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.</p>`
      + legRows([
        ['levels 0-2', `the fast network's tree edges: ${n('lv_fln')} per level`, '', ''],
        ['levels 3-4', `through the crossbar: ${n('lv_xbar')} cycles per level`, '', ''],
        ['levels 5-9', `over the mesh: ${n('lv_mesh')} cycles per level`, '', ''],
        ['back down', `TensorBroadcast: all ${n('n1024')} minions have the sum after ${n('ar1024')} (${n('ar_us')})`, '', ''],
        ['against a barrier', `a chip barrier from global atomics and credits: ${n('chipbar')} cycles (${n('chipbar_us')})`, '', ''],
      ])
      + `<p class="pn-what small">One shire's 32 minions reduce in ${n('ar32')}; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (${src('the order was measured for loads and stores', 'L104')}; whether the tree's messages travel as requests was not tested).</p>`);
  },
  stages: [
    {name: 'Levels 0-2', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: `levels 0-2: ${N.lv_fln.t}`, f: 'sync.tree-levels'}],
      say: () => `Levels 0-2, inside each neighbourhood along the fast network's tree edges: 1→0, 3→2, 5→4, 7→6, then 2→0 and 6→4, then 4→0, ${n('lv_fln')} per level`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, mc = (nb, m) => { const p = P1.min[nb + ':' + m]; return {x: p.x + p.w / 2, y: p.y + p.h / 2}; };
        // each partial sum moves on the tree edge itself, from child to parent: the trail recolours the amber edge in
        // the flow's colour (no second line beside it), and the small packet stays off the minions' names. The end state
        // shows which edges levels 0-2 used.
        const edge = (nb, a, b) => P1.fe[nb + ':' + a + '-' + b] || [mc(nb, a), mc(nb, b)];
        for (let h = 0; h < 3; h++) {
          const moves = [];
          for (let nb = 0; nb < 4; nb++) for (let m = 1; m < 8; m++) if (lsb(m) === h) moves.push(edge(nb, m, m - (1 << h)));
          await Promise.all(moves.map(([a, b]) => { const pk = packet(fx, 'var(--c2)', 7); at(pk, a); return travel(tok, fx, pk, [a, b], 1300, {w: 6, op: 1, col: 'var(--c2)'}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
          await wait(tok, 350);
        }
        for (let nb = 0; nb < 4; nb++) pulse(tok, fx, mc(nb, 0), 1100, 'var(--c2)', 30).catch(() => {});
        callout(fx, SF.x + SF.w, SF.y + 470, [{t: 'levels 0-2: tree edges'}, {t: `${N.lv_fln.t} per level`, f: 'sync.tree-levels'}, {t: 'each minion 0 has its'}, {t: "neighbourhood's sum"}], {side: 'r', fs: 20});
      }},
    {name: 'Levels 3-4', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: `levels 3-4: ${N.lv_xbar.t} cycles each`, f: 'sync.tree-levels'}],
      say: () => `Levels 3-4, across the crossbar: neighbourhood 1 → 0 and 3 → 2, then 2 → 0, ${n('lv_xbar')} cycles per level`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, m0 = nb => { const p = P1.min[nb + ':0']; return {x: p.x + p.w / 2, y: p.y + p.h / 2}; };
        const xy2 = P1.xbarY - 15;   // along the crossbar's upper edge, over no text
        const legXb = (a, b) => { const A = m0(a), B = m0(b); return [A, {x: P1['ch' + a].x, y: A.y}, {x: P1['ch' + a].x, y: xy2}, {x: P1['ch' + b].x, y: xy2}, {x: P1['ch' + b].x, y: B.y}, B]; };
        for (const lv of [[[1, 0], [3, 2]], [[2, 0]]]) {
          await Promise.all(lv.map(([a, b]) => { const pk = packet(fx, 'var(--c1)', 9); return travel(tok, fx, pk, legXb(a, b), 1900, {w: 5, col: 'var(--c1)'}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
          await wait(tok, 350);
        }
        await pulse(tok, fx, m0(0), 1200, 'var(--c2)', 40);
      }},
    {name: 'Levels 5-9', where: () => ({level: 0}), dim: false,
      say: () => `Levels 5-9, over the mesh: odd shires to the even one below, then by 2, 4, 8 and 16, into shire 0, ${n('lv_mesh')} cycles per level`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        for (let h = 0; h < 5; h++) {
          const moves = Object.values(SH).filter(s => s.id && lsb(s.id) === h).map(s => [s, SH[s.id - (1 << h)]]);
          const lab = T(fx, DW / 2, DH + 32, `level ${5 + h}`, 't-labb halo', 'middle');
          await Promise.all(moves.map(([a, b]) => { const pk = packet(fx, 'var(--c1)', 9); return travel(tok, fx, pk, pts(route(a, b)), 700 + 280 * hops(a, b), {w: 4, col: 'var(--c1)', even: true}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
          lab.remove(); await wait(tok, 300);
        }
        await pulse(tok, fx, {x: SH[0].sx, y: SH[0].sy}, 1300, 'var(--c2)', 60);
      }},
    {name: 'Back down', where: () => ({level: 0}), dim: false,
      say: () => `TensorBroadcast takes the sum back down the same tree: all ${n('n1024')} minions have it after ${n('ar1024')} (${n('ar_us')}), on all three cards`,
      run: async (tok, c) => {
        const fx = c.fx; fx.querySelectorAll('path.trail').forEach(p => { p.style.strokeOpacity = 0.25; });
        for (let h = 4; h >= 0; h--) {
          const moves = Object.values(SH).filter(s => s.id && lsb(s.id) === h).map(s => [SH[s.id - (1 << h)], s]);
          await Promise.all(moves.map(([a, b]) => { const pk = packet(fx, 'var(--c2)', 9); return travel(tok, fx, pk, pts(route(a, b)), 600 + 240 * hops(a, b), {trail: false, even: true}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
        }
        await Promise.all(Object.values(SH).map(s => pulse(tok, fx, {x: s.sx, y: s.sy}, 1200, 'var(--c2)', 36)));
        callout(fx, DW / 2, DH / 2, [{t: `${N.ar1024.t}, up and down`, f: 'sync-allreduce1024'}, {t: `${N.ar_us.t} for all 1,024 minions`, f: 'sync-allreduce1024'}], {side: 'u', fs: 24});
      }},
    {name: 'Against a barrier', where: () => ({level: 0}), dim: false,
      say: () => `A chip barrier built from global atomics and credits takes ${n('chipbar')} cycles (${n('chipbar_us')}): the hardware tree reduces and broadcasts in about a quarter of that`,
      run: async (tok, c) => {
        const fx = c.fx;
        const rows = [['allreduce, 1,024', 'ar1024', 'sync-allreduce1024', 'var(--c1)'], ['chip barrier', 'chipbar', 'sync-chip-barrier', 'var(--c7)'], ['allreduce, 32', 'ar32', 'sync-allreduce32', 'var(--c1)'], ['shire barrier', 'flb', 'sync-shire-barrier', 'var(--c7)']];
        const ch = bandChart(fx, 'Cycles', rows.map(r => ({name: r[0], val: N[r[1]].t, f: r[2], col: r[3]})));
        await anim(tok, 1800, q => ch.rows.forEach((r, i) => r.set(easeS(q) * V(rows[i][1]) / V('chipbar'))));
      }},
  ],
};

/* ---- B. one value to every minion (28 September 2026, the owner's request from the page's Talk tab; not in the
   tour). The ways the chip offers, each with what it costs where that was measured: the hardware tree (TensorBroadcast
   down the allreduce's tree: the minion that holds the value, the die, a shire, then its measured time); a relay from
   shire to shire against every shire reading DRAM; one line in memory that every minion loads (the die, then the
   line's home shire); and the multicast that every kernel launch already makes. What was not measured is said where it
   would be drawn: the tree's broadcast half on its own, the tree's energy, a relay's time to every shire, every minion
   loading one line at once, and the launch's multicast apart from the rest of a launch. ---- */
/* a minion of the shire view lit, a glow inside its box under its name (as flow 7 lights its 32 minions) */
function minGlow(k) {
  const P1 = AP[1], g = P1.minG && P1.minG[k], sh = g && g.querySelector('.shape'), m = P1.min[k];
  if (!sh || g.querySelector(':scope > .glow')) return;
  const r = S(E('rect', {class: 'glow', x: m.x + 3, y: m.y + 3, width: m.w - 6, height: m.h - 6, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--c2)', fillOpacity: isDark() ? 0.42 : 0.3});
  g.insertBefore(r, sh.nextSibling); fadeIn(r, 300);
}
/* each way's energy per byte where it was measured, per shire the byte reaches: the rows come in stage by stage (the
   rows already shown hold still, a new one fades in and grows) */
const BC_E = [['relay', 'relay hand-off', 'rl_e_next', 'relay-energy', 'var(--c3)'], ['l3', 'L3 read, mesh', 'e_l3', 'e-l3', 'var(--c1)'], ['dram', 'DRAM read', 'e_dram', 'e-dram', 'var(--c2)']];
function bcEnergy(tok, c, keys, o) {
  o = o || {};
  const fx = c.fx, want = BC_E.filter(r => keys.includes(r[0])), key = want.map(r => r[0]).join();
  const here = c.ech && c.ech.g.parentNode === fx;
  if (here && c.echK === key) return c.ech;
  const had = here ? c.echK.split(',') : [];
  if (c.ech && c.ech.g.parentNode) c.ech.g.remove();
  const still = had.length > 0;
  c.ech = bandChart(fx, 'pJ per byte', want.map(r => ({name: r[1], val: N[r[2]].t, f: r[3], col: r[4]})), {note: 'each shire it reaches', note2: o.note2, y: o.y, still});
  c.echK = key;
  want.forEach((r, i) => {
    const row = c.ech.rows[i], q = V(r[2]) / V('e_dram');
    if (had.includes(r[0])) row.set(q);
    else { if (still) fadeIn(row.g, 300); quiet(anim(tok, 900, p => row.set(easeS(p) * q))); }
  });
  return c.ech;
}
/* every shire reading its own copy from DRAM: lines from the memory shires through their L3 homes (fact sc.l3-miss),
   until a later stage stops it */
function bcDram(tok, c) {
  const st = c.ds = {stop: false};
  if (REDUCED) return;
  const fx = c.fx, t0 = CLK.t; let nx = 0;
  every(tok, t => { if (st.stop || !CLK.on) return; while (nx <= t - t0) {
    const s = c.all[Math.floor(Math.random() * 32)], home = Math.floor(Math.random() * 32), m = MSC[home % 8], pk = packet(fx, 'var(--c2)', 7), P = pts(viaR(m, SH[home], s));
    quiet(travel(tok, fx, pk, P, 280 * Math.max(4, P.length - 1), {trail: false, even: true, linear: true}).then(() => pk.remove(), e => { pk.remove(); throw e; }));
    nx += 170; } });
}
/* a load's request from a to b and its reply back, y first along the request's links, its own packet on its own lane
   (the reply colour), removed at the end */
async function bcTrip(tok, fx, a, b, ms, col) {
  const P = pts(route(a, b)), q = packet(fx, col || 'var(--c2)', 7); at(q, P[0]);
  try { await travel(tok, fx, q, P, ms, {trail: false, even: true}); } finally { q.remove(); }
  const back = lane(pts(reply(b, a)), LANE, {x: b.sx, y: b.sy}), r = packet(fx, 'var(--c7)', 7); at(r, back[0]);
  try { await travel(tok, fx, r, back, ms, {trail: false, even: true}); } finally { r.remove(); }
}
/* On a phone the text must read at 11 px or more: a callout of the chip or a shire at 21 (the callout enlarges it by
   the scale), a minion's note larger still and one line (a minion's view is drawn small there) */
const bcFs = fs => (PH ? 21 : fs);
function bcNote(c, fx, lines, one) {
  if (!PH) return note(c, fx, lines, 'var(--c2)');
  if (c.cnt && c.cnt.parentNode) c.cnt.remove();
  const p = NOTE_AT();
  c.cnt = callout(fx, p.x, p.y, [one], {tr: true, fs: 34, col: 'var(--c2)'});
  c.cnt.classList.add('note');
  return c.cnt;
}
/* a callout over the middle of the die, its top just under row 1's tile numbers and at least 340 units wide (centred
   on the die, it then covers the numbers of columns 3 to 5 whole and leaves those of columns 2 and 6), so that it hides
   a tile's number whole or not at all; on a phone, where its text is larger, it spans columns 2 to 5 */
function bcMid(fx, lines, fs) {
  if (!PH) return callout(fx, DW / 2, TILE + 30, lines, {side: 'd', fs, minW: 340});
  return callout(fx, STRIP + TILE + INS, TILE + 50, lines, {tl: true, fs: 21, minW: 4 * TILE - 2 * INS});
}
/* on a phone, whose view of a shire is its frame's width (no room beside it), a callout across the frame over a whole
   row of parts (from y): it hides their labels whole */
const bcWide = (fx, y, lines) => callout(fx, SF.x + 16, y, lines, {tl: true, fs: 21, minW: SF.w - 32});
FLOWS.K = {
  title: 'Broadcast',
  cap: () => CAPS.K(),
  setup(c) {
    const all = Object.values(SH);
    // the tree's mesh levels, top down: at level 5 + h each shire whose ID has bit h as its lowest set bit receives
    // from the shire with that bit cleared (fact ar.tree)
    const lv = [4, 3, 2, 1, 0].map(h => all.filter(s => s.id && lsb(s.id) === h).map(s => [SH[s.id - (1 << h)], s]));
    // the relay: shire to shire in ID order, each hand-off on its own route (the relay hands a slab to the next shire)
    const chain = [];
    for (let i = 1; i < 32; i++) chain.push(pts(route(SH[i - 1], SH[i])));
    Object.assign(c, {all, root: SH[0], lv, chain, master: CELLS.find(x => x.type === 'master' && x.r === 0), pc: CELLS.find(x => x.type === 'pcie')});
    flowPanel('K', 'One value to every minion',
      `<p class="pn-what">How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all ${n('n1024')} minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.</p>`
      + legRows([
        ['the value', `hart 0's ${n('vregs')}: 32 B fills one, 1 KB all of them; ${src('only hart 0 issues tensor instructions', 'minion.tensor-hart0')}`, '', ''],
        ['tree: mesh', `${src('TensorBroadcast', 'bc.tensorbroadcast')} down the allreduce's tree, levels 9 to 5 between shires: ${n('lv_mesh')} cycles a level, up and down`, '', ''],
        ['tree: shire', `levels 4 and 3 through the crossbar, ${n('lv_xbar')} cycles a level; 2 to 0 on the tree edges, ${n('lv_fln')}; in every shire at once`, '', ''],
        ['tree, timed', `with the reduction, 32 B: ${n('ar32')} (${n('ar32_us')}) over 32 minions, ${n('ar1024')} (${n('ar_us')}) over ${n('n1024')}; 1 KB: ${n('bc_1k32')} (${n('bc_1k32_us')}) and ${n('bc_1k', 'cycles')} (${n('bc_1k_us')})`, '', ''],
        ['relay or DRAM', `a hand-off to the next shire ${n('rl_e_next', 'pJ/B')}, write and read, ${n('rl_13th')} of a DRAM round trip; every shire reading DRAM ${n('e_dram', 'pJ/B')} each, the chip's ${n('dram_bw', 'GB/s')} shared`, '', ''],
        ['one line', `every minion loads one line from its L3 home: one load ${n('lat_l3_a')} + ${n('l3_b12')} cycles a hop; ${src('one request per shire at a time', 'bc.one-request')}; ${n('e_l3', 'pJ/B')} over the mesh`, '', ''],
        ['at its home', `the line's bank: an atomic every ${n('hot10')}; 31 requesters, one a shire, left the home's reader at ${n('bc_poll')}; 22 from one shire hammering it stop the home's loads (${n('hot22')})`, '', ''],
        ['the launch', `${src('one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire', 'bc.launch-multicast bc.esr-ipi')}: an empty kernel ${n('pcie_b2b_rng')} queued on 32 shires, ${n('bc_l1')} on one`, '', ''],
        ['compared', `to all ${n('n1024')}: the tree ${n('ar_us')} (32 B) or ${n('bc_1k_us')} (1 KB); a chip barrier alone ${n('chipbar_us2')}; a queued launch ${n('pcie_b2b_rng')}`, '', ''],
      ])
      + `<p class="pn-what small"><b>Not measured:</b> the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (${src('fact bc.half', 'bc.half')}); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (${src('fact bc.launch-31', 'bc.launch-31')}).</p>`
      + `<p class="pn-what small">The mesh takes a request x first and a reply y first (${src('measured for loads and stores', 'L104')}): the relay's hand-offs and the reads' requests are drawn x first, the lines they bring back y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.</p>`);
  },
  stages: [
    {name: 'The value', where: () => ({level: 2, sid: 0, nb: 0, mi: 0}),
      mark: () => [{t: '32 B in f0; 1 KB in f0–f31', f: 'minion.vpu-regs'}],
      say: () => `The value sits in hart 0's vector registers, minion 0 of shire 0: ${src('32 B fills one register, 1 KB all 32', 'minion.vpu-regs')}. ${src('Only hart 0 may issue TensorBroadcast', 'minion.tensor-hart0')}; its first step goes to ${n('bc_512')}, in shire 16`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx;
        bcNote(c, fx, [{t: 'the value: 32 B in f0', f: 'minion.vpu-regs'}], {t: 'the value: 32 B in f0', f: 'minion.vpu-regs'});
        // the registers that hold it, lit over hart 0's own (f0 for 32 B, then all 32 for 1 KB)
        const lit = P2.regs[0].map(r => S(E('rect', {x: r.getAttribute('x'), y: r.getAttribute('y'), width: 32, height: 21, rx: 3}, fx), {fill: 'var(--c2)', fillOpacity: 0}));
        await pulse(tok, fx, P2.hart0, 900, 'var(--c2)', 40);
        await anim(tok, 500, q => { lit[0].style.fillOpacity = (0.85 * easeOut(q)).toFixed(3); });
        await wait(tok, 1200);
        bcNote(c, fx, [{t: '1 KB: all 32, f0–f31', f: 'minion.vpu-regs'}], {t: '1 KB: all 32, f0–f31', f: 'minion.vpu-regs'});
        await anim(tok, 1300, q => lit.forEach((r, i) => { if (i) r.style.fillOpacity = (0.85 * band(q * 1.6, i / 32, i / 32 + 0.25)).toFixed(3); }));
        await wait(tok, 700);
        // hart 0's first TensorBroadcast: out through the ET-Link port, over the gutters (no label is crossed)
        const h0 = P2.hart0e, pe = P2.etlPort, gx = MF.x + 354, gy = MF.y + 545, pk = pkIn(c, fx, h0);
        at(pk, h0);
        await travel(tok, fx, pk, [h0, {x: gx, y: h0.y}, {x: gx, y: gy}, {x: pe.x - 10, y: gy}, {x: pe.x - 10, y: pe.y}, pe], 1600, {w: 4});
        bcNote(c, fx, [{t: 'TensorBroadcast, step 1:'}, {t: `to ${N.bc_512.t}, shire 16`, f: 'bc.tensorbroadcast'}], {t: 'step 1: to shire 16', f: 'bc.tensorbroadcast'});
      }},
    {name: 'Tree: mesh', where: () => ({level: 0}),
      say: () => `${src('TensorBroadcast', 'bc.tensorbroadcast')} down the allreduce's tree: levels 9 to 5 cross the mesh, shire 0 to 16, then to 8 and 24, and on by 4, 2 and 1, until minion 0 of every shire has the value`,
      run: async (tok, c) => {
        const fx = c.fx, r0 = {x: c.root.sx, y: c.root.sy};
        hiCells([c.root], true);
        const first = pkIn(c, fx, r0, 'var(--c2)', 10); at(first, r0);
        for (let i = 0; i < 5; i++) {
          // the level under the die (on a phone the caption says it: no room there)
          const lab = PH ? null : T(fx, DW / 2, DH + 32, `level ${9 - i}`, 't-labb halo', 'middle');
          await Promise.all(c.lv[i].map(([a, b]) => {
            const pk = i === 0 ? first : packet(fx, 'var(--c2)', 9);
            if (i) at(pk, {x: a.sx, y: a.sy});
            return travel(tok, fx, pk, pts(route(a, b)), 600 + 240 * hops(a, b), {w: 4, even: true}).then(() => { pk.remove(); hiCells([b]); }, e => { pk.remove(); throw e; });
          }));
          if (lab) lab.remove();
          await wait(tok, 250);
        }
        c.pk = null;
        c.lvT = bandText(fx, 'Levels 9 to 5', [{t: 'cross the mesh:', f: 'ar.tree'}, {t: `${N.lv_mesh.t} cycles`, b: 1, f: 'sync.tree-levels'}, {t: 'a level, up and down,'}, {t: 'in the allreduce'}]);
      }},
    {name: 'Tree: shire', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: 'levels 4 to 0, every shire', f: 'ar.tree'}],
      say: () => `In every shire at once: levels 4 and 3 cross the crossbar (neighbourhood 0 to 2, then 0 to 1 and 2 to 3), levels 2 to 0 run down ${src("the fast network's edges", 'neigh.fln-edges')}: 0→4, then 0→2 and 4→6, then to each odd minion`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, mc = k => { const p = P1.min[k]; return {x: p.x + p.w / 2, y: p.y + p.h / 2}; };
        minGlow('0:0');
        await pulse(tok, fx, mc('0:0'), 900, 'var(--c2)', 34);
        // levels 4 and 3: minion 0 of neighbourhood 0 to minion 0 of neighbourhood 2 (the shire's minion 16), then 0 to
        // 1 and 2 to 3 (minions 8 and 24), along the crossbar's upper edge; no trail stays (it would cross the
        // neighbourhoods' names and the crossbar's): the minions they reach stay lit
        const yx = P1.xbarY - 15;
        const legXb = (a, b) => { const A = mc(a + ':0'), B = mc(b + ':0'); return [A, {x: P1['ch' + a].x, y: A.y}, {x: P1['ch' + a].x, y: yx}, {x: P1['ch' + b].x, y: yx}, {x: P1['ch' + b].x, y: B.y}, B]; };
        for (const lvl of [[[0, 2]], [[0, 1], [2, 3]]]) {
          await Promise.all(lvl.map(([a, b]) => { const pk = packet(fx, 'var(--c2)', 9); return travel(tok, fx, pk, legXb(a, b), 1700, {trail: false}).then(() => { pk.remove(); minGlow(b + ':0'); }, e => { pk.remove(); throw e; }); }));
          await wait(tok, 300);
        }
        // levels 2 to 0 in every neighbourhood: the value runs down the fast network's tree edges, which take its colour
        const edge = (nb, a, b) => P1.fe[nb + ':' + a + '-' + b] || [mc(nb + ':' + a), mc(nb + ':' + b)];
        for (let h = 2; h >= 0; h--) {
          const moves = [];
          for (let nb = 0; nb < 4; nb++) for (let m = 1; m < 8; m++) if (lsb(m) === h) moves.push([nb + ':' + m, edge(nb, m - (1 << h), m)]);
          await Promise.all(moves.map(([k, [a, b]]) => { const pk = packet(fx, 'var(--c2)', 7); at(pk, a); return travel(tok, fx, pk, [a, b], 1200, {w: 6, op: 1}).then(() => { pk.remove(); minGlow(k); }, e => { pk.remove(); throw e; }); }));
          await wait(tok, 300);
        }
        const lines = [{t: 'levels 4–3: crossbar', f: 'ar.tree'}, {t: `${N.lv_xbar.t} cycles a level`, f: 'sync.tree-levels'}, {t: 'levels 2–0: tree edges', f: 'neigh.fln-edges'}, {t: `${N.lv_fln.t} a level`, f: 'sync.tree-levels'}, {t: 'allreduce, up and down'}];
        // right of the frame; on a phone across the row of banks, which this stage does not use
        if (PH) bcWide(fx, SF.y + 132, [{t: `levels 4–3: the crossbar, ${N.lv_xbar.t} cycles a level`, f: 'ar.tree sync.tree-levels'},
          {t: `levels 2–0: the tree edges, ${N.lv_fln.t} a level`, f: 'neigh.fln-edges sync.tree-levels'}, {t: 'in the allreduce, up and down'}]);
        else callout(fx, SF.x + SF.w, SF.y + 470, lines, {side: 'r', fs: 20});
      }},
    {name: 'Tree, timed', where: () => ({level: 0}), dim: false,
      say: () => `Timed with the reduction, on three cards: all ${n('n1024')} minions have 32 B after ${n('ar1024')} (${n('ar_us')}) and 1 KB after ${n('bc_1k', 'cycles')} (${n('bc_1k_us')}); ${src('the broadcast half alone was never timed', 'bc.half')}`,
      run: async (tok, c) => {
        const fx = c.fx; clearDim(); hiCells(c.all, false);
        if (c.lvT) { fadeOut(c.lvT); c.lvT = null; }
        // the tree's legs stay, set back
        fx.querySelectorAll(':scope > path.trail').forEach(p => { p.style.strokeOpacity = 0.3; });
        const rows = [['32 minions, 32 B', 'ar32', 'sync-allreduce32'], ['1,024 minions, 32 B', 'ar1024', 'sync-allreduce1024'], ['32 minions, 1 KB', 'bc_1k32', 'bc.allreduce-1kb'], ['1,024 minions, 1 KB', 'bc_1k', 'bc.allreduce-1kb']];
        const ch = bandChart(fx, 'Allreduce, cycles', rows.map(r => ({name: r[0], val: N[r[1]].t.replace(/ cycles$/, ''), f: r[2]})), {note: 'up and down,', note2: 'three cards'});
        await Promise.all([anim(tok, 1600, q => ch.rows.forEach((r, i) => r.set(easeS(q) * V(rows[i][1]) / V('bc_1k')))),
          Promise.all(c.all.map(s => pulse(tok, fx, {x: s.sx, y: s.sy}, 1200, 'var(--c2)', 30)))]);
        bcMid(fx, [{t: `all 1,024: ${N.ar_us.t} for 32 B`, f: 'sync-allreduce1024'}, {t: `${N.bc_1k_us.t} for 1 KB`, f: 'bc.allreduce-1kb'}, {t: 'with the reduction; the'}, {t: 'broadcast alone: not timed', f: 'bc.half'}], 23);
      }},
    {name: 'Relay or DRAM', where: () => ({level: 0}),
      say: () => `A buffer in memory, handed shire to shire: each hand-off costs ${n('rl_e_next', 'pJ/B')}. If every shire reads its own copy from DRAM instead, each pays ${n('e_dram', 'pJ/B')}, and all share the chip's ${n('dram_bw', 'GB/s')}`,
      run: async (tok, c) => {
        const fx = c.fx;
        if (c.ds) c.ds.stop = true;
        [...fx.children].forEach(el => fadeOut(el, 320)); c.ech = null; c.lvT = null;
        clearDim(); hiCells([c.root], true);
        bcEnergy(tok, c, ['relay', 'dram'], {note2: 'relay time: not timed'});
        // the relay: the value handed from shire to shire in ID order, one hand-off after another
        const pk = packet(fx, 'var(--c3)', 10); at(pk, {x: c.root.sx, y: c.root.sy});
        for (let i = 0; i < 31; i++) {
          const P = c.chain[i];
          await travel(tok, fx, pk, P, 70 * Math.max(1, P.length - 1), {w: 3, col: 'var(--c3)', op: 0.5, even: true});
          hiCells([SH[i + 1]]);
        }
        pk.remove();
        await wait(tok, 600);
        // every shire reading its own copy from DRAM, through the lines' L3 homes
        hiCells(Object.values(MSC)); [0, 2, 4, 6].forEach(hiPkg);
        bcDram(tok, c);
        await wait(tok, 4500);
      }},
    {name: 'One line', where: () => ({level: 0}),
      say: () => `One line that every minion loads from its home, shire 0's L3 slice: ${src('a shire sends one request for a line at a time', 'bc.one-request')}, so the home serves 32; one load from h hops takes ${n('lat_l3_a')} + ${n('l3_b12')}×h cycles`,
      run: async (tok, c) => {
        const fx = c.fx, home = c.root;
        if (c.ds) c.ds.stop = true;
        const keep = c.ech && c.ech.g.parentNode === fx ? c.ech.g : null;
        [...fx.children].forEach(el => { if (el !== keep) fadeOut(el, 320); });
        clearDim(); hiCells([home], true);
        bcEnergy(tok, c, ['relay', 'l3', 'dram'], {note2: 'relay time: not timed'});
        callout(fx, home.sx, home.sy, [{t: "home: shire 0's L3", f: 'l3.home'}, {t: 'one request a shire', f: 'bc.one-request'}], {cell: home, side: 'r', fs: bcFs(20)});
        await pulse(tok, fx, {x: home.sx, y: home.sy}, 900, 'var(--c2)', 40);
        // one request from each other shire, and the line back on its own lane
        await Promise.all(c.all.filter(s => s !== home).map((s, i) => wait(tok, (i % 8) * 80)
          .then(() => bcTrip(tok, fx, s, home, 240 * Math.max(1, hops(s, home))))
          .then(() => hiCells([s]))));
        bandText(fx, 'One load, h hops', [{t: `${N.lat_l3_a.t} + ${N.l3_b12.t} × h`, b: 1, f: 'l3.latency'}, {t: 'cycles; all 1,024'}, {t: 'at once: not timed'}], c.ech.bottom + 10);
      }},
    {name: 'At its home', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: `the line's bank: an atomic every ${N.hot10.t}`, f: 'hot-cost'}],
      say: () => `At the home, the line's bank retires one atomic every ${n('hot10')}: 31 requesters, one a shire, left the home's own reader at ${n('bc_poll')} of its rate, but 22 from one shire hammering it stop the home's loads (flow 9)`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, B = P1.bank[0], ln = P1.lane[0], yb = B.box.y - 8, top = {x: ln.x, y: SF.y - 40};
        // the tree of stage 3 (the same shire, drawn here as its end state when the reader steps) goes
        [...fx.children].forEach(el => fadeOut(el, 260)); clearGlow(true);
        // from the mesh down the line's lane to its bank, and back up beside it
        const inP = [top, ln, {x: ln.x, y: yb}, {x: B.x, y: yb}, B], outP = inP.slice().reverse().map(p => ({x: p.x + 9, y: p.y}));
        // (on a phone short: clear of the north edge's name)
        callout(fx, top.x, top.y + 12, [{t: PH ? 'from 31 shires' : 'from 31 shires, one each', f: 'bc.one-request'}], {side: 'r', fs: bcFs(19)});
        // right of the frame beside the bank; on a phone across the neighbourhoods' lower rows (the next callout takes its
        // place there), the banks being this stage's
        const NB2 = SF.y + 352 + 46 + 2 * 70 - 8;
        if (PH) sayAt(c, fx, SF.x + 16, NB2, [{t: `the line's bank: one atomic every ${N.hot10.t}`, f: 'hot-cost'}, {t: 'loads by every minion at once: not measured'}], {tl: true, fs: 21, minW: SF.w - 32});
        else callout(fx, SF.x + SF.w, B.y, [{t: "the line's bank:"}, {t: 'one atomic every'}, {t: N.hot10.t, f: 'hot-cost'}, {t: 'loads by every minion'}, {t: 'at once: not measured'}], {side: 'r', fs: 20});
        // the line's bank lit (a glow inside its box, under its name), and its lane outlined (a line across the lane's
        // number would cross the label)
        const bk = [...LAYERS[1].querySelectorAll('.comp[data-comp="banks"]')].find(g => g._ctx.bank === 0), bsh = bk && bk.querySelector('.shape');
        if (bsh && !bk.querySelector(':scope > .glow')) { const r = S(E('rect', {class: 'glow', x: B.box.x + 3, y: B.box.y + 3, width: B.box.w - 6, height: B.box.h - 6, rx: 4, 'pointer-events': 'none'}, bk), {fill: 'var(--c2)', fillOpacity: isDark() ? 0.42 : 0.3}); bk.insertBefore(r, bsh.nextSibling); fadeIn(r, 300); }
        S(E('rect', {x: ln.x - 27, y: ln.y - 24, width: 54, height: 48, rx: 6}, fx), {fill: 'none', stroke: 'var(--c2)', strokeWidth: 3.5});
        const trips = [];
        for (let i = 0; i < 31; i++) {
          const q = packet(fx, 'var(--c2)', 6);
          const p = travel(tok, fx, q, inP, 1000, {trail: false}).then(() => { q.remove(); const r = packet(fx, 'var(--c7)', 6); return travel(tok, fx, r, outP, 900, {trail: false}).then(() => r.remove(), e => { r.remove(); throw e; }); }, e => { q.remove(); throw e; });
          p.catch(() => {});
          trips.push(p);
          await wait(tok, 60);
        }
        await Promise.all(trips);
        // the home's own minions read the line too, through the crossbar
        const keys = Object.keys(P1.min);
        await Promise.all(keys.map((k, i) => wait(tok, (i % 8) * 50).then(async () => {
          const m = P1.min[k], q0 = {x: m.x + m.w / 2, y: m.y + m.h / 2}, ch = P1['ch' + k[0]];
          const P = [q0, {x: ch.x, y: q0.y}, {x: ch.x, y: P1.xbarY}, {x: B.x, y: P1.xbarY}, {x: B.x, y: B.box.y + B.box.h}];
          const q = packet(fx, 'var(--c1)', 6); at(q, q0);
          try { await travel(tok, fx, q, P, 900, {trail: false}); } finally { q.remove(); }
          const r = packet(fx, 'var(--c7)', 6);
          try { await travel(tok, fx, r, P.slice().reverse(), 900, {trail: false}); } finally { r.remove(); }
        })));
        if (PH) sayAt(c, fx, SF.x + 16, NB2, [{t: '31 requesters, one in each shire:', f: 'bc.pollers'}, {t: `the home's own reader kept ${N.bc_poll.t}`, f: 'bc.pollers'},
          {t: '22 from one shire, hammering it:'}, {t: `the home's loads fall to ${N.hot22.t}`, f: 'hot.cliff'}], {tl: true, fs: 21, minW: SF.w - 32});
        else callout(fx, SF.x + SF.w, SF.y + 440, [{t: 'one per shire, 31 in all:', f: 'bc.pollers'}, {t: `the home's reader: ${N.bc_poll.t}`, f: 'bc.pollers'}, {t: '22 from one shire,'}, {t: `hammering: loads at ${N.hot22.t}`, f: 'hot.cliff'}], {side: 'r', fs: 20});
      }},
    {name: 'The launch', where: () => ({level: 0}),
      say: () => `Every kernel launch is a broadcast: the master shire writes ${src('a 64-byte message', 'bc.launch-multicast')} into its scratchpad, ${src('one ESR broadcast', 'bc.esr-ipi')} interrupts every hart, all of them read it, and each shire answers with a global atomic`,
      run: async (tok, c) => {
        const fx = c.fx, m = c.master, mp = {x: m.sx, y: m.sy};
        if (c.ds) c.ds.stop = true;
        [...fx.children].forEach(el => fadeOut(el, 320)); c.ech = null;
        clearDim(); hiCells([m, c.pc], true);
        // the launch command from the host, over PCIe to the master shire
        await travel(tok, fx, packet(fx, 'var(--c4)', 11), AP[0].host.slice(0, 2).concat(pts(route(c.pc, m))), 1800, {col: 'var(--c4)'});
        await pulse(tok, fx, mp, 900, 'var(--c7)', 40);
        // (two lines: a taller callout beside a top-row cell would cover its neighbours' numbers)
        callout(fx, mp.x, mp.y, [{t: 'one 64-byte line, in the', f: 'bc.launch-multicast'}, {t: "master's scratchpad"}], {cell: m, side: 'l', fs: bcFs(20)});
        // one ESR broadcast raises the interrupt on every hart of every shire in the mask: its path over the mesh is not
        // documented, so it is drawn at each shire, not along a route
        hiCells(c.all);
        await Promise.all(c.all.map(s => pulse(tok, fx, {x: s.sx, y: s.sy}, 1100, 'var(--c7)', 32)));
        // every shire's harts read the message from the master's scratchpad; the last of each shire clears the shire's
        // bit of the mask beside it with a global atomic (the small packet)
        await Promise.all(c.all.map((s, i) => wait(tok, (i % 8) * 60).then(async () => {
          const ms = 200 * Math.max(1, hops(s, m));
          await bcTrip(tok, fx, s, m, ms);
          const P = pts(route(s, m)), a = packet(fx, 'var(--c5)', 5); at(a, P[0]);
          try { await travel(tok, fx, a, P, ms, {trail: false, even: true}); } finally { a.remove(); }
        })));
        const [bg, rc, lt] = await ring(tok, fx, mp, 1400, 'var(--c7)', 'poll');
        [bg, rc, lt].forEach(e => e && e.remove());
        bandText(fx, 'An empty kernel', [{t: 'queued, on 32 shires:'}, {t: N.pcie_b2b_rng.t, b: 1, f: 'pcie.launch'}, {t: 'on one shire:'}, {t: `${N.bc_l1.t} µs`, b: 1, f: 'bc.launch-31'},
          {t: 'the other 31 add'}, {t: N.bc_l31.t, b: 1, f: 'bc.launch-31'}, {t: 'waited for, alone:'}, {t: N.pcie_launch_rng.t, b: 1, f: 'pcie.launch'}, {t: 'the multicast alone'}, {t: 'was not timed', f: 'bc.launch-31'}], BAND.y);
      }},
    {name: 'Compared', where: () => ({level: 0}), dim: false,
      say: () => `To all ${n('n1024')} minions: the tree ${n('ar_us')} for 32 B and ${n('bc_1k_us')} for 1 KB, a chip barrier alone ${n('chipbar_us2')}, a queued launch ${n('pcie_b2b_rng')}; a relay's and a shared line's time, and the tree's energy, were not measured`,
      run: async (tok, c) => {
        const fx = c.fx;
        if (c.ds) c.ds.stop = true;
        [...fx.children].forEach(el => fadeOut(el, 320)); c.ech = null;
        clearDim(); hiCells(c.all, false);
        // the time to reach all 1,024 minions (a log scale, 1 µs to 1 ms), and each way's energy per byte where measured
        const L = [['tree, 32 B', 'ar_us', 'sync-allreduce1024', 'var(--c2)'], ['tree, 1 KB', 'bc_1k_us', 'bc.allreduce-1kb', 'var(--c2)'], ['chip barrier', 'chipbar_us2', 'sync-chip-barrier', 'var(--c7)'], ['kernel launch', 'pcie_b2b_rng', 'pcie.launch', 'var(--c4)']];
        // (on a phone the charts fold under the die, as large as the taller one allows: that one keeps no note there, the
        // scale in its title, and the caption says what was not measured)
        const lc = bandChart(fx, PH ? 'To all 1,024, µs, log' : 'To all 1,024, µs', L.map(r => ({name: r[0], val: N[r[1]].t, f: r[2], col: r[3]})), PH ? {} : {note: 'log scale, to 1 ms', note2: 'relay, line: not timed'});
        const ec = bandChart(fx, 'pJ per byte', BC_E.map(r => ({name: r[1], val: N[r[2]].t, f: r[3], col: r[4]})), {note: 'each shire it reaches', note2: PH ? null : 'tree, launch: none', y: lc.bottom + 14});
        await anim(tok, 1600, q => { const e = easeS(q); lc.rows.forEach((r, i) => r.set(e * Math.log10(V(L[i][1])) / 3)); ec.rows.forEach((r, i) => r.set(e * V(BC_E[i][2]) / V('e_dram'))); });
        bcMid(fx, [{t: 'In a kernel, the tree:'}, {t: `${N.ar_us.t} to every minion`, f: 'sync-allreduce1024'}, {t: 'Data in memory: one read'}, {t: 'a shire, hand-offs on chip,', f: 'bc.one-request relay-energy'}, {t: 'and never a polled line', f: 'hot.cliff'}], 23);
      }},
  ],
};

const ACTS = {
  replay: () => { if (FL.k || LASTFLOW) startFlow(FL.k || LASTFLOW, 0, {intro: true}); },
  newpa: () => { ST.pa = mkPA(Math.floor(Math.random() * 32), Math.floor(Math.random() * 2 ** 20)); startFlow('A', 0, {keep: true}); },
  gs: b => { ST.gs = b.textContent.startsWith('G') ? 'g' : 's'; startFlow('E', 0); },
};
$('pn-body').addEventListener('change', e => { if (e.target.dataset.sel === 'rq') { ST.rq = +e.target.value; if (FL.ctx && FL.ctx.k === 'A') FL.ctx.pick.rq = ST.rq; startFlow('A', 0, {keep: true, intro: true}); } });

/* ================= captions and the tour ================= */
/* each flow's claim: the line under the caption while its stages play (the caption itself says what each stage does) */
const CAPS = {
  A: () => `A load that misses everywhere pays the mesh twice, to its L3 home and on to a memory shire: about ${n('lat_dram')} cycles, ${n('lat_dram_chip')} of them in the DRAM chip.`,
  B: () => `The latency ladder: ${n('lat_l1')} cycles in L1, ${n('lat_l2')} in L2, ${n('lat_l3_a')} cycles plus ${n('l3_b12')} per mesh hop in L3, about ${n('lat_dram')} in DRAM.`,
  C: () => `TensorSend moves registers from a hart to a minion anywhere on the chip: between shires, ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip, on all three cards.`,
  D: () => `Handing a result to the next shire costs ${n('rl_e_next')} pJ per byte against ${n('rl_e_dram')} through DRAM: ${n('rl_13th')} of the energy, at ${n('rl_speed')} the bandwidth.`,
  E: () => `Gathers from scattered lines: ${n('g_l1_r')} G elements/s from L1, but only ${n('g_dr_r')} G from DRAM, at ${n('g_dr_e')} pJ each.`,
  F: () => `The host link on three cards: ${n('pcie_h2d')} GB/s to the card by DMA, ${n('pcie_stg_rng')} GB/s as a program copies; a kernel launch costs ${n('pcie_b2b_rng')} queued, ${n('pcie_launch_rng')} waited for.`,
  G: () => `A matmul step on the tensor unit: TensorLoad brings A in ${n('tl_l2')} cycles, TensorFMA takes ${n('tfma_tenb')} cycles and hides the next load: ${n('tflops')} TFLOP/s on ${n('n1024')} minions.`,
  H: () => `The same matmul, ${n('w_tflops')} TFLOP/s timed from the host (${n('tflops')} on the device), draws ${n('w_zeros', 'W')} on zeros and ${n('w_randn', 'W')} on random data at the board; random data reaches 90 °C in ${n('race_rand', 's')}.`,
  I: () => `One hot line: the atomic is fair to every shire, but 22 requesters stop its home shire's own traffic dead, while 21 leave it ${n('hot21r')} of its rate.`,
  J: () => `The allreduce tree: ten levels up with TensorReduce and back down with TensorBroadcast, ${n('ar1024')} for all ${n('n1024')} minions, about a quarter of a software barrier.`,
  K: () => `One value to all ${n('n1024')} minions, four ways: the hardware tree, within an allreduce's ${n('ar_us')}; a relay from shire to shire; one line that every minion loads; and the multicast every kernel launch makes, ${n('pcie_b2b_rng')} a queued launch.`,
};
const compG = (key, i) => LAYERS[Z.level].querySelectorAll(`.comp[data-comp="${key}"]`)[i || 0] || null;
/* the facts behind the tour's last slide: how many are measured, specified, derived and inferred */
const kindN = k => Object.values(F).filter(f => f.kind === k).length;
const STEPS = [
  {name: 'Chip', cap: () => `The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor.`,
    view: {level: 0}, panel: ['chip'], sub: () => `Dashed outlines are ${src('inferred', 'dram.pkg-pairing')}: which two memory shires share each LPDDR4X package.`},
  {name: 'Shires', cap: () => `${n('cshires')} compute shires of ${n('per_shire')} run the kernels; the master shire (${n('master_id')}) schedules them and a spare (${n('spare_id')}) waits for yield recovery.`,
    view: {level: 0}, hi: ['cshire', 'master'], panel: ['cshire', () => ({cell: SH[0]})], sel: () => SH[0].g, sub: () => `Placed by measured distances, all ${n('pairs496')} shire pairs; the firmware's NoC-spec map agrees in ${n('fw_pairs')} pair distances. Shire 0, ringed, is the one we open next.`},
  {name: 'Mesh', cap: () => `An ${n('grid86')} mesh of ${n('stops')} stops joins them. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire.`,
    view: {level: 0}, hi: ['mesh', 'links'], cls: 'mesh-on', panel: ['mesh'], sub: () => `${src("The grid's four corners are empty", 'mesh.grid')}. Routes are shortest paths: a request goes x first, its reply y first (${src('measured', 'L104')}).`},
  {name: 'Memory', cap: () => `${n('memshires')} memory shires drive ${n('channels')} LPDDR4X channels (${n('dram_gb')}), ${n('dram_peak')} GB/s peak at ${n('mts')} MT/s; the chip streams ${n('dram_bw')} GB/s.`,
    view: {level: 0}, hi: ['memshire', 'dram'], panel: ['dram', () => ({ms: [0, 1]})], sub: () => `Placed by a fit of DRAM latencies on aifoundry2, within ±3 cycles for ${n('ms_fit')} of loads on all three cards; the firmware's map agrees on the seven the fit places alone.`},
  {name: 'Shire', cap: () => `Inside a shire, ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM: ${n('scp_mb')} scratchpad, ${n('l2_kb')} L2 and a ${n('l3_mb')} slice of the L3.`,
    view: {level: 1, sid: 0}, panel: ['banks', () => ({})], sub: () => `Amber links: the fast local network's tree edges, ${n('ts_fln')} round trip against ${n('ts_xbar', 'cycles')} for other pairs.`},
  {name: 'Minion', cap: () => `A minion has ${n('harts')} and a vector unit whose ${n('lanes_n')} lanes also run the tensor instructions. ${n('n1024')} minions sustain ${n('tflops')} TFLOP/s fp32 at ${n('mhz')}.`,
    view: {level: 2, sid: 0, nb: 0, mi: 0}, panel: ['tensor'], sel: () => compG('tensor'), sub: () => `The firmware turns ${n('l1_scp')} of the ${n('l1_kb')} L1 into the tensor scratchpad and leaves each hart ${n('l1_hart')}.`},
  {flow: 'A'}, {flow: 'B'}, {flow: 'C'}, {flow: 'D'}, {flow: 'E'}, {flow: 'F'}, {flow: 'G'}, {flow: 'H'}, {flow: 'I'}, {flow: 'J'},
  {name: 'Summary', cap: () => `Every number on this diagram has a source: ${Object.keys(F).length} facts, ${kindN('measured')} of them measured on the lab's cards, ${kindN('spec')} from the specification, ${kindN('derived')} derived and ${kindN('inferred')} inferred.`,
    view: {level: 0}, hi: [], panel: ['chip'], draw: tok => factSplit(tok), sub: () => 'Each inferred part says what would settle it; the facts, their sources and the asks are listed under the diagram.'},
];
let TOUR = null, TLAST = 0;
/* the last slide: the facts behind the diagram as one bar, by kind, over the die (set back) */
function factSplit(tok) {
  const fx = FX[0]; if (!fx) return;
  const tot = Object.keys(F).length, W = 660, H = 200, x = DW / 2 - W / 2, y = DH / 2 - H / 2 - 20, bw = W - 56, by = y + 76;
  const g = E('g', {class: 'band'}, fx);
  S(E('rect', {class: 'co-box', x, y, width: W, height: H, rx: 12, filter: 'url(#co-sh)'}, g), {stroke: 'var(--border)'});
  T(g, x + 28, y + 48, `${tot} facts, each with its source`, 't-big');
  const K = [['measured', 'var(--ok)', 'measured'], ['spec', 'var(--c1)', 'specified'], ['derived', 'var(--c7)', 'derived'], ['inferred', 'var(--warn)', 'inferred']];
  let bx = x + 28, lx = x + 28;
  const segs = K.map(([k, col, lab]) => {
    const w = bw * kindN(k) / tot, r = S(E('rect', {class: 'bbar', x: bx, y: by, width: 0, height: 46, rx: 3}, g), {fill: col});
    const seg = {r, x: bx, w: Math.max(2, w - 3)}; bx += w;
    S(E('rect', {class: 'bbar', x: lx, y: y + 146, width: 16, height: 16, rx: 3}, g), {fill: col});
    const t = T(g, lx + 22, y + 160, `${kindN(k)} ${lab}`, 't-lab');
    let tw = 0; try { tw = t.getComputedTextLength(); } catch (_) { /* not rendered */ } lx += 22 + (tw || 110) + 26;
    return seg;
  });
  fadeIn(g, 300);
  // grown in on the clock; paused, drawn whole
  quiet(anim(CLK.on ? tok : {dead: false, ff: true}, 1400, q => segs.forEach((sg, i) => sg.r.setAttribute('width', (sg.w * easeS(Math.max(0, Math.min(1, q * 1.6 - i * 0.2)))).toFixed(1)))));
}
/* a number and its unit never part at a line's end (the templates write "12.46 GB/s" with a plain space) */
const UNITS = '(?:W|s|cycles?|GB/s|TB/s|pJ|pJ/B|ns|µs|°C|TFLOP/s|TOP/s|MB|KB|G|M/s|mm|hops?|minions|shires|lines)(?![\\w/])';
const GLUE1 = new RegExp('</span> (?=' + UNITS + ')', 'g'), GLUE2 = new RegExp('(\\d) (?=' + UNITS + ')', 'g');
const glue = html => ARW(String(html).replace(GLUE1, '</span>\u00a0').replace(GLUE2, '$1\u00a0'));
function setCap(html) { hideTip(); $('cap').innerHTML = `<span class="cap-in">${glue(html)}</span>`; fitCap(); }
/* the caption fits two lines: a long one is set smaller. A flow's stages share one size (the smallest any of them
   needs), so that the caption does not change size while the presenter steps */
let CAPCAP = null;
const capKey = () => innerWidth + 'x' + innerHeight + ($('stage').classList.contains('nopanel') ? 'n' : '') + ($('stage').classList.contains('present') ? 'p' : '');
function fitCap() {
  const c = $('cap'); c.style.fontSize = ''; c.style.height = '';
  if (window.matchMedia('(max-width: 899px)').matches) return 0;
  const base = parseFloat(getComputedStyle(c).fontSize), h = Math.round(base * 2.56);
  c.style.height = h + 'px';
  let fs = base;
  if (FL.k && CAPCAP && CAPCAP.k === FL.k && CAPCAP.key === capKey() && CAPCAP.fs < base) { fs = CAPCAP.fs; c.style.fontSize = fs + 'px'; }
  while (c.scrollHeight > h + 1 && fs > 13) { fs -= 1; c.style.fontSize = fs + 'px'; }
  return fs;
}
function flowCapSize(k, ctx) {
  CAPCAP = null;
  const sts = FLOWS[k].stages, c = $('cap'), keep = c.innerHTML;
  let m = Infinity;
  try { sts.forEach(st => { c.innerHTML = `<span class="cap-in">${glue(stageLine(st.say ? st.say(ctx) : ''))}</span>`; const f = fitCap(); if (f) m = Math.min(m, f); }); } catch (e) { console.error(e); }
  c.innerHTML = keep;
  if (isFinite(m)) CAPCAP = {k, key: capKey(), fs: m};
}
let fitT = 0;
window.addEventListener('resize', () => { clearTimeout(fitT); fitT = setTimeout(fitCap, 120); });
function setKick(t) { $('cap-k').innerHTML = ARW(esc(t)); }
/* the index of the button in box that has the focus (-1 for none): a rebuilt row of buttons gives it back */
const focusIn = box => { const a = document.activeElement; return a && box.contains(a) ? [...box.querySelectorAll('button')].indexOf(a) : -1; };
const refocus = (box, k) => { if (k < 0) return; const b = box.querySelectorAll('button')[k]; if (b) b.focus({preventScroll: true}); };
/* the tour's progress: a small dot per step beside the kicker (a click jumps to it) */
function dots(i) {
  const d = $('dots'), had = focusIn(d); d.textContent = '';
  if (i < 0) return;
  STEPS.forEach((s, k) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = k < i ? 'past' : k === i ? 'on' : '';
    const nm = s.flow ? `flow ${KEYOF[s.flow]}, ${FLOWS[s.flow].title}` : s.name;
    b.setAttribute('aria-label', `Tour step ${k + 1}: ${nm}`); b.title = `Step ${k + 1}: ${nm}`;
    if (k === i) b.setAttribute('aria-current', 'step');
    b.addEventListener('click', () => tourGo(k));
    d.appendChild(b);
  });
  refocus(d, had);
}
function highlight(keys) {
  svg.classList.add('dimming');
  keys.forEach(k => { if (k === 'links') AP[0].links.classList.add('hi'); else LAYERS[0].querySelectorAll(`.comp[data-comp="${k}"]`).forEach(g => g.classList.add('hi')); });
}
/* o.back: stepping back into a flow's step shows its last stage's end state, with no establishing shot */
async function tourGo(i, o) {
  if (!TOUR) return;
  o = o || {};
  i = Math.max(0, Math.min(STEPS.length - 1, i)); TOUR.i = i; TLAST = i;
  const s = STEPS[i];
  if (TOUR.tok) TOUR.tok.dead = true;
  const tok = TOUR.tok = {dead: false};
  select(null);
  dots(i);
  // presenting: every tour step starts with the camera following, whatever the reader did before
  if (!FOLLOW) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); }
  if (s.flow) {
    if (o.back) startFlow(s.flow, FLOWS[s.flow].stages.length - 1, {still: true, done: true});
    else startFlow(s.flow, 0, {intro: true});
    return;
  }
  // the last step's drawing fades; the dimming goes with the camera (the zoom starts from how the die looks now)
  stopFlow(true, true);
  setKick(`Tour ${i + 1} / ${STEPS.length} · ${s.name}`);
  setCap(s.cap()); sub(s.sub ? s.sub() : '');
  if (s.panel) showComp(s.panel[0], s.panel[1] ? s.panel[1]() : {});   // the panel changes with the caption, not after the zoom
  renderBar(); playBtn();
  // the highlight goes on in the frame the camera arrives in (a zoom out ends at its look), else it fades in (CSS)
  let lit = false;
  const light = () => { if (lit || !TOUR || TOUR.i !== i || tok.dead) return; lit = true; if (s.hi) highlight(s.hi); if (s.cls) svg.classList.add(s.cls); if (s.draw) s.draw(tok); };
  await goTo(s.view, Object.assign(CLK.on ? {clk: tok} : {total: 600}, {c1: s.hi ? DIMLOOK.dimming() : null, arrive: light}));
  if (!TOUR || TOUR.i !== i || tok.dead) return;
  light();
  if (s.sel) { const g = s.sel(); if (g) select(g); }
}
/* presenting (the tour, full screen, or the stage filling the frame): larger panel text, no reference lists, no dotted
   numbers, no reader's instructions (CSS #stage.present) */
function presentClass() {
  const st = $('stage'), was = st.classList.contains('present'), on = !!TOUR || PRES || !!fsEl();
  st.classList.toggle('present', on);
  panelAuto();
  // the caption shown before anything plays: the reader's instructions, or while presenting a title
  if (was !== on && !TOUR && !FL.k && !CAPFLOW) resetCap();
}
function startTour(at) {
  TOUR = {i: 0}; $('btn-tour').textContent = 'End tour'; $('btn-tour').classList.add('on'); phBox();
  presentClass();
  tourGo(at || 0);
}
function endTour() {
  if (!TOUR) return;
  if (TOUR.tok) TOUR.tok.dead = true;
  TLAST = TOUR.i;
  TOUR = null; $('btn-tour').textContent = 'Tour'; $('btn-tour').classList.remove('on'); phBox();
  presentClass();
  dots(-1); clearDim();
  if (flowOn() || FL.k) { setKick(flowKick(FL.k)); CAPFLOW = true; renderBar(); playBtn(); }
  else resetCap();
}
/* T and the Tour button: the tour picks up where it was left (from the start once it had reached its end) */
const toggleTour = () => { if (TOUR) { endTour(); stopFlow(); } else startTour(TLAST >= STEPS.length - 1 ? 0 : TLAST); };
const HINT = TOUCH ? 'Tap a shire, then a minion, to zoom in · pinch to enlarge'
  : 'Space pauses · ← → stages · + − zoom · double-click zooms in · F presents · P panel · C follow · T tour';
function resetCap() {
  CAPFLOW = false;
  if ($('stage').classList.contains('present')) {
    setKick('ET-SoC-1'); setCap(STEPS[0].cap()); sub(STEPS[0].sub()); renderBar(); return;
  }
  setKick('Explore');
  setCap(`${TOUCH ? 'Tap' : 'Click'} any part of the chip, zoom with the scale control, pick one of eleven flows, or press Tour to step through it all in ${STEPS.length} steps.`);
  sub(HINT); $('cap-sub').classList.add('hint'); renderBar();
}
/* the stage bar: the active flow's stages, the current one marked; in the tour on a still step, the tour's still
   steps (Chip, Shires, ... Summary); each is a button */
function renderBar() {
  const ol = $('stages'), had = focusIn(ol); ol.textContent = '';
  const k = FL.k;
  $('stage').classList.toggle('playing', flowOn() && CLK.on && !FL.still);
  const chip = (num, name, cls, title, go) => {
    const li = document.createElement('li'), b = document.createElement('button');
    if (/\bon\b/.test(cls)) { li.className = 'on'; b.setAttribute('aria-current', 'step'); }
    b.type = 'button'; b.className = 'stg' + cls;
    b.innerHTML = `<span class="sn">${num}</span><span class="st">${ARW(esc(name))}</span>`;
    b.title = title; b.setAttribute('aria-label', title);
    b.addEventListener('click', go);
    li.appendChild(b); ol.appendChild(li);
  };
  if (!k) {
    if (TOUR) {
      // the still steps by name; the ten flows between them as one chip (their stages show here when they play)
      STEPS.forEach((s, j) => {
        if (s.flow) {
          if (STEPS[j - 1] && STEPS[j - 1].flow) return;
          let e = j; while (STEPS[e + 1] && STEPS[e + 1].flow) e++;
          chip(`${j + 1}–${e + 1}`, 'Flows', e < TOUR.i ? ' past' : '', `Tour steps ${j + 1} to ${e + 1}: the ten flows`, () => tourGo(j));
        } else chip(j + 1, s.name, j < TOUR.i ? ' past' : j === TOUR.i ? ' on' : '', `Tour step ${j + 1} of ${STEPS.length}: ${s.name}. The arrows step; Shift with an arrow jumps a step`, () => tourGo(j));
        ol.lastChild.classList.add('tchip');
      });
    } else {
      const li = document.createElement('li'); li.className = 'stg-hint';
      li.textContent = TOUCH ? 'Pick a flow above to see its stages here, or press Tour' : 'Pick a flow above (keys 1 to 9, 0 and B) to see its stages here, or press Tour';
      ol.appendChild(li);
    }
    refocus(ol, had);
    setDis($('btn-prev'), TOUR ? TOUR.i === 0 : !LASTFLOW); setDis($('btn-next'), !!TOUR && TOUR.i === STEPS.length - 1);
    return;
  }
  const sts = FLOWS[k].stages;
  sts.forEach((s, i) => chip(i + 1, s.name, i < FL.i ? ' past' : i === FL.i ? ' on' : '', `Stage ${i + 1} of ${sts.length}: ${s.name}`, () => goStage(i)));
  refocus(ol, had);
  setDis($('btn-prev'), FL.i === 0 && !(TOUR && TOUR.i > 0));
  setDis($('btn-next'), FL.i === sts.length - 1 && !(TOUR && TOUR.i < STEPS.length - 1));
}
/* the Play button: Pause while a flow plays, Play when paused, Replay after; on a still tour step nothing plays, and
   it is hidden (Space still pauses the camera) */
function playBtn() {
  const b = $('btn-play'), still = !!TOUR && !STEPS[TOUR.i].flow;
  const t = FL.k ? (FL.done ? 'Replay' : (CLK.on && !FL.still ? 'Pause' : 'Play')) : still ? (CLK.on ? 'Pause' : 'Play') : LASTFLOW ? 'Replay' : 'Play';
  b.textContent = t;
  b.disabled = !FL.k && !LASTFLOW && !still;
  b.classList.toggle('void', still);   // on a still tour slide nothing plays: while presenting it takes no room
  b.setAttribute('aria-label', t + ' (Space)');
  $('stage').classList.toggle('playing', flowOn() && CLK.on && !FL.still);
}
/* Space: pause or resume everything on the clock (packets, the camera's moves, the charts); held on a stage's end
   state, go on to the next stage; after the end, replay */
function playPause() {
  if (!FL.k) {
    if (TOUR && !STEPS[TOUR.i].flow) { CLK.on = !CLK.on; playBtn(); return; }
    if (LASTFLOW) startFlow(LASTFLOW, 0, {intro: true});
    return;
  }
  if (FL.done) { startFlow(FL.k, 0, {intro: true, keep: true}); return; }
  // after the reader's own zoom, going on follows the flow again (as stepping does)
  const refollow = () => { if (FOLLOW_AUTO) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); return true; } return false; };
  if (FL.still) {
    CLK.on = true; refollow();
    if (FL.i < FLOWS[FL.k].stages.length - 1) startFlow(FL.k, FL.i + 1, {keep: true});
    else { FL.still = false; FL.done = true; renderBar(); playBtn(); }
    return;
  }
  if (!CLK.on && refollow()) { CLK.on = true; restartStage(); playBtn(); renderBar(); return; }
  CLK.on = !CLK.on; playBtn(); renderBar();
}
/* ---- presenting: full screen where the frame allows it, else the stage fills the frame ---- */
const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement;
const fsOK = () => !!(document.fullscreenEnabled || document.webkitFullscreenEnabled);
let PRES = false, toastT = 0;
function toast(html, ms) {
  const t = $('toast'); t.innerHTML = html; t.hidden = false; clearTimeout(toastT);
  if (ms) toastT = setTimeout(() => { t.hidden = true; }, ms);
}
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
/* a copy of this page in a window of its own (a top-level window may go full screen). It is written from the
   server's copy of the page when it can be fetched, else from the page as it was loaded. */
function presenterWindow() {
  let w = null;
  try { w = window.open('', 'etsoc1_presenter', `popup=yes,width=${screen.availWidth || 1280},height=${screen.availHeight || 800}`); } catch (_) { w = null; }
  if (!w) { toast('<p>The browser blocked the new window: allow pop-ups for this page, or press <kbd>F11</kbd>.</p>', 9000); return; }
  const put = html => {
    try { w.document.open(); w.document.write(html.replace(/<head([^>]*)>/i, '<head$1><script>window.__ET_PRESENTER=1<\/script>')); w.document.close(); try { w.focus(); } catch (_) { /* focus refused */ } return true; }
    catch (_) { return false; }
  };
  const fallback = () => { if (!put(SRC_HTML)) { try { w.location.href = location.href; } catch (_) { /* nothing more to try */ } } };
  if (/^https?:$/.test(location.protocol) && window.fetch) fetch(location.href, {credentials: 'same-origin'}).then(r => r.ok ? r.text() : Promise.reject(new Error('status ' + r.status))).then(h => { if (!/id="stage"/.test(h) || !put(h)) fallback(); }, fallback);
  else fallback();
  setPres(false);
  toast('<p>The presenter window is open: press <kbd>F</kbd> there for full screen.</p>', 7000);
}
$('toast').addEventListener('click', e => { const b = e.target.closest('button[data-t]'); if (!b) return; if (b.dataset.t === 'win') presenterWindow(); else hideToast(); });
/* In a frame (spacesheep shows the page in one), the keys reach the page only once the reader has clicked into it:
   until then, and whenever the frame loses the focus, a hint over the drawing says so. A click anywhere hides it. A
   touch screen has no keys: no hint there. */
const FRAMED = (() => { try { return window.self !== window.top; } catch (_) { return true; } })();
function kbdHint() { const h = $('kbd-hint'); if (h) h.hidden = TOUCH || !FRAMED || document.hasFocus() || PRES || !!fsEl(); }
if (FRAMED) {
  window.addEventListener('focus', kbdHint); window.addEventListener('blur', kbdHint);
  $('kbd-hint').addEventListener('click', () => { window.focus(); kbdHint(); });
  kbdHint(); setTimeout(kbdHint, 400);
}
/* the skip links move the focus without scrolling the stage (it clips its content) */
document.querySelectorAll('.skip a').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  const t = $(a.getAttribute('href').slice(1)); if (!t) return;
  const f = t.matches('button, [tabindex]') ? t : [...t.querySelectorAll('button:not(:disabled), a, [tabindex]')][0];
  if (f) f.focus({preventScroll: true});
}));
/* hide the details panel so that the die takes the whole width (P, the Panel button, ?panel=off) */
let PANEL = null;   // true or false once set by P, the Panel button or ?panel=off; null: automatic
const shortScreen = () => { try { return matchMedia('(max-height: 780px) and (min-width: 900px)').matches; } catch (_) { return false; } };
function panelAuto() {
  const st = $('stage'), hide = PANEL === null ? st.classList.contains('present') && shortScreen() : !PANEL;
  if (st.classList.contains('nopanel') === hide) return;
  st.classList.toggle('nopanel', hide); $('btn-panel').setAttribute('aria-pressed', String(!hide));
  setTimeout(fitCap, 60);
}
function togglePanel(show) {
  const st = $('stage');
  PANEL = show === undefined ? st.classList.contains('nopanel') : !!show;
  panelAuto();
}
window.addEventListener('resize', () => { if (PANEL === null) panelAuto(); });
/* light or dark whatever the system says (D, ?theme=light|dark); the template's tokens follow data-theme */
function setTheme(t) { if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }
function toggleTheme() {
  const cur = document.documentElement.dataset.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  setTheme(cur === 'dark' ? 'light' : 'dark');
}
/* Right: the next stage of the flow; at its last stage (or on a still slide), the next tour step. Shift: whole steps */
function next(whole) {
  if (TOUR) {
    const s = STEPS[TOUR.i];
    if (!whole && s.flow && FL.k === s.flow && goStage(FL.i + 1)) return;
    if (TOUR.i >= STEPS.length - 1) return;   // the last step: Q or End tour leaves the tour
    tourGo(TOUR.i + 1); return;
  }
  if (FL.k) { goStage(FL.i + 1); return; }
  // no flow on the stage: the last one played starts again (Space does the same); before any flow, the tour starts
  if (LASTFLOW) { startFlow(LASTFLOW, 0, {intro: true}); return; }
  startTour(0);
}
function prev(whole) {
  if (TOUR) {
    const s = STEPS[TOUR.i];
    if (!whole && s.flow && FL.k === s.flow && goStage(FL.i - 1)) return;
    // back from a step's start: the previous step as it ended (a flow's last stage, drawn still), no establishing shot
    if (TOUR.i > 0) tourGo(TOUR.i - 1, {back: !whole});
    return;
  }
  if (FL.k) { goStage(FL.i - 1); return; }
  // no flow on the stage: back to the last one played, at its last stage's end state; Left never starts the tour
  if (LASTFLOW) startFlow(LASTFLOW, FLOWS[LASTFLOW].stages.length - 1, {still: true, done: true});
}
/* Esc: leaves presenting inside the frame (full screen leaves by itself); it never ends the tour (Q and End tour do),
   so that a press meant for the full screen does not lose the presenter's place */
function back() {
  if (PRES) { setPres(false); return; }
  if (TOUR || fsEl()) return;
  if (FL.k) { stopFlow(); return; }
  if (zNow().level) zoomBy(-1);
}
/* a flow's button or key: in the tour, its tour step (the tour goes on from there); else the flow on its own */
function pickFlow(k) {
  const j = STEPS.findIndex(s => s.flow === k);
  if (TOUR && j >= 0) { tourGo(j); return; }
  // a flow the tour does not step through (B, the broadcast): the tour ends and the flow plays on its own
  if (TOUR) endTour();
  if (FOLLOW_AUTO) setFollow(true);
  startFlow(k, 0, {intro: true});
}
document.querySelectorAll('[data-flow]').forEach(b => b.addEventListener('click', () => pickFlow(b.dataset.flow)));
/* a mouse click leaves no focus on a button, a summary or a fact in the stage, so that Space then pauses (the keyboard
   keeps its focus) */
$('stage').addEventListener('click', e => { const b = e.target.closest && e.target.closest('button, summary, li.fact'); if (b && e.detail > 0) b.blur(); });
$('btn-play').addEventListener('click', playPause);
$('btn-tour').addEventListener('click', toggleTour);
$('btn-fs').addEventListener('click', present);
$('btn-panel').addEventListener('click', () => togglePanel());
$('btn-next').addEventListener('click', e => { if (!isDis(e.currentTarget)) next(false); });
$('btn-prev').addEventListener('click', e => { if (!isDis(e.currentTarget)) prev(false); });
$('btn-follow').addEventListener('click', () => setFollow(!FOLLOW));
$('z-in').addEventListener('click', e => { if (!isDis(e.currentTarget)) zoomBy(1); });
$('z-out').addEventListener('click', e => { if (!isDis(e.currentTarget)) zoomBy(-1); });
[0, 1, 2].forEach(l => $('z-' + l).addEventListener('click', () => scaleTo(l)));
PIP.el.addEventListener('click', () => { setFollow(true); });
PIP.el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setFollow(true); } });
/* on a narrow screen the stage is taller than the window (the panel stacks under the drawing): there the keys act while
   the drawing or the playback bar is in view, not while the reader is down in the panel */
const inMid = el => { const r = el.getBoundingClientRect(); return r.bottom > window.innerHeight * 0.4 && r.top < window.innerHeight * 0.6; };
const stageInView = () => window.matchMedia('(max-width: 899px)').matches ? inMid($('svgwrap')) || inMid($('bar')) : inMid($('stage'));
/* a Space that paused must not also press the focused button when the key comes up (a button clicks on keyup) */
let SPACE_EATEN = false;
document.addEventListener('keyup', e => { if ((e.key === ' ' || e.key === 'Spacebar') && SPACE_EATEN) { e.preventDefault(); SPACE_EATEN = false; } }, true);
/* The keys act on the stage only while it is in view (or presenting) and focus is in it or on the page itself, so
   that below the stage Space, PageDown and the arrows scroll as usual. Space on a button presses the button. */
document.addEventListener('keydown', e => {
  if (e.key !== 'Tab') hideTip();
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  const tg = e.target, tag = (tg.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
  const inView = !!fsEl() || PRES || stageInView();
  const inStage = inView && ($('stage').contains(tg) || tg === document.body || tg === document.documentElement);
  if (!inStage) return;
  const onControl = tg.closest && tg.closest('button, a, li.fact, summary, [role="button"]:not(.comp)');
  const presenting = !!TOUR || PRES || !!fsEl();
  switch (e.key) {
    case 'ArrowRight': case 'PageDown': e.preventDefault(); next(e.shiftKey); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); prev(e.shiftKey); break;
    case ' ': case 'Spacebar': {
      // Space on a control presses it, except where pressing it would restart what Space should pause: the active
      // flow's own button, a stage button, and, while a flow plays, a summary or a fact in the panel
      const fb = tg.closest && tg.closest('[data-flow]');
      const pause = (fb && FL.k && fb.dataset.flow === FL.k) || (tg.closest && tg.closest('.stg')) || (flowOn() && tg.closest && tg.closest('#pn-body summary, #pn-body li.fact'));
      // a link does not activate on Space: on the skip links it would scroll the page
      if (tg.closest && tg.closest('.skip a')) { e.preventDefault(); return; }
      if (onControl && !pause) return;
      e.preventDefault(); SPACE_EATEN = true; playPause(); break;
    }
    case 'f': case 'F': e.preventDefault(); present(); break;
    case 'p': case 'P': e.preventDefault(); togglePanel(); break;
    case 'd': case 'D': e.preventDefault(); toggleTheme(); break;
    case 'c': case 'C': e.preventDefault(); setFollow(!FOLLOW); break;
    case 't': case 'T': e.preventDefault(); toggleTour(); break;
    case 'q': case 'Q': if (TOUR) { e.preventDefault(); endTour(); stopFlow(); } break;
    case 'b': case 'B': e.preventDefault(); pickFlow('K'); break;
    case '+': case '=': e.preventDefault(); zoomBy(1); break;
    case '-': case '_': e.preventDefault(); zoomBy(-1); break;
    case 'Escape': back(); break;
    case 'Backspace': if (zNow().level) { e.preventDefault(); zoomBy(-1); } break;
    case 'Home': if (FL.k) { e.preventDefault(); goStage(0); } else if (TOUR) { e.preventDefault(); tourGo(0); } else if (presenting) e.preventDefault(); break;
    case 'End': if (FL.k) { e.preventDefault(); goStage(FLOWS[FL.k].stages.length - 1); } else if (TOUR) { e.preventDefault(); tourGo(STEPS.length - 1); } else if (presenting) e.preventDefault(); break;
    // a presenter's clicker: F5 (and Shift+F5) is its "start the slideshow" button, never a reload mid-talk; some send
    // Up and Down for back and forward
    case 'F5': if (presenting) { e.preventDefault(); if (!TOUR) startTour(TLAST >= STEPS.length - 1 ? 0 : TLAST); } break;
    case 'ArrowDown': if (presenting) { e.preventDefault(); next(e.shiftKey); } break;
    case 'ArrowUp': if (presenting) { e.preventDefault(); prev(e.shiftKey); } break;
    default: {
      const i = '1234567890'.indexOf(e.key);
      if (i >= 0 && e.key.length === 1) pickFlow(ORDER[i]);
    }
  }
});

/* ================= the text below the stage ================= */
function prose() {
  $('summary-text').innerHTML = [
    `<p><b>The chip.</b> The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die in TSMC ${n('process')}: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor. The diagram draws the die (width and height from a published die plot) with ${n('cshires')} compute shires, the master (${n('master_id')}) and spare (${n('spare_id')}) shires, the PCIe and I/O shires, and ${n('memshires').toLowerCase()} memory shires, on an ${n('grid86')} mesh of ${n('stops')} stops. The compute shires sit where measured distances put them, and the firmware's NoC-spec map, once its boot-time renaming is applied, puts every one in the same cell (${n('fw_pairs')} pair distances). Each mesh hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. Off the die, four LPDDR4X packages hold ${n('channels')} channels of ${n('ch_bits')}, ${n('dram_gb')}; the chip streams ${n('dram_bw')} GB/s from them against ${n('dram_peak')} GB/s peak at their ${n('mts')} MT/s. The host links through the PCIe shire: Gen4 x8, trained at ${n('pcie_neg')} on every card, ${n('pcie_h2d')} GB/s to the card by DMA. The fp32 matmul at ${n('tflops')} TFLOP/s draws ${n('mmw')} at the board on the three cards, ${n('perw')} GFLOP/s per watt.</p>`,
    `<p><b>A shire.</b> ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM in ${n('banks')}. The cards run mode M0: ${n('scp_mb')} of scratchpad that any shire can address, ${n('l2_kb')} of L2 private to the shire, and a ${n('l3_mb')} slice of the chip's ${n('l3_chip')} L3. The shire meets the mesh at one stop, and inside a neighbourhood minions talk fastest along the tree edges of the fast local network (${n('ts_fln')} round trip, against ${n('ts_xbar')} cycles for other pairs).</p>`,
    `<p><b>A minion.</b> ${n('harts')}, in-order and single-issue, a vector unit of ${n('lanes')} and a ${n('l1_kb')} L1 data cache, of which the firmware makes ${n('l1_scp')} a tensor scratchpad and leaves each hart ${n('l1_hart')}. The tensor instructions are no separate unit: state machines in the vector unit run them on its lanes' FMA and int8 multiply-add units, so the tensor peak (${n('peak32')}, ${n('peak16')} or ${n('peak8')} operations per cycle) is the lanes' peak. On ${n('n1024')} minions at ${n('mhz')} they sustain ${n('tflops')} TFLOP/s fp32.</p>`,
    `<p><b>The flows.</b> (1) A load that misses every cache: ${n('lat_l1')} cycles would have been an L1 hit and ${n('lat_l2')} an L2 hit; the L3 home is PA[10:6] and costs ${n('lat_l3_a')} + ${n('lat_l3_b')}; the memory shire is PA[8:6] and adds ${n('lat_ms_a')} + ${n('lat_ms_b')} cycles per hop; a typical DRAM load takes ${n('lat_dram')}, of which ${n('lat_dram_chip')} are the DRAM chip. (2) The ladder adds the read buffer (${n('lat_rb')}), the own scratchpad (${n('lat_scp')}) and another shire's scratchpad (${n('lat_rs_a')} + ${n('lat_rs_b')} per hop). (3) TensorSend: ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip. (4) The relay: ${n('rl_e_next')} pJ/B to the next shire against ${n('rl_e_dram')} through DRAM (${n('rl_x')} less). (5) Gathers from scattered lines: ${n('g_l1_r')}, ${n('g_l2_r')}, ${n('g_rs_r')} and ${n('g_dr_r')} G elements/s from L1, L2, a scratchpad two hops away and DRAM. (6) The host over PCIe, timed on three cards: ${n('pcie_h2d')} GB/s to the card and ${n('pcie_d2h')} back by DMA (${n('pcie_h2d_pct')} and ${n('pcie_d2h_pct')} of the link), ${n('pcie_stg_rng')} GB/s for a program's staged copies, whose lines land in their L3 homes (${n('pcie_l3pct')} then read at L3 latency); an empty kernel costs the card ${n('pcie_b2b_rng')} queued, while one launch waited for takes ${n('pcie_launch_rng')}, most of it the runtime's ${n('poll500')} idle poll. (7) A matmul step: TensorLoad ${n('tl_l2')} cycles, TensorFMA ${n('tfma_tenb')}, ${n('mm_op')} per op with the next load hidden. (8) The Horace runs of the matmul (${n('w_tflops')} TFLOP/s, timed from the host) on zeros, ones and random data: ${n('w_zeros')}, ${n('w_ones')} and ${n('w_randn')} W at the board at the launch temperature; random data reaches 90 °C in ${n('race_rand')} s, zeros never. (9) One hot line: fair shares (${n('hot_host')} for the host shire), and 22 requesters stop the host shire's own loads (${n('hot22')}). (0) The allreduce tree: ${n('ar1024')} for all ${n('n1024')} minions, against ${n('chipbar')} cycles for a chip barrier. (B) One value to every minion, four ways: the hardware tree (TensorBroadcast down the allreduce's tree) has it everywhere within the allreduce's ${n('ar1024')} (${n('ar_us')}) for 32 B and ${n('bc_1k', 'cycles')} (${n('bc_1k_us')}) for 1 KB, the broadcast half never timed alone; a relay hands a buffer from shire to shire at ${n('rl_e_next')} pJ/B a hand-off, where every shire reading its own copy from DRAM pays ${n('e_dram')} pJ per byte; one line that every minion loads costs each shire one request to its home, but hammered with atomics it is the hot line of flow 9; and every kernel launch is itself a broadcast of one 64-byte message, ${n('pcie_b2b_rng')} for an empty kernel queued on 32 shires.</p>`,
  ].join('');
  // what is measured, specified, derived and inferred
  const fs = Object.values(F), of = k => fs.filter(f => f.kind === k), meas = of('measured');
  const mc = k => meas.filter(f => f.cards.length === k).length;
  const lk = id => `<a href="#facts" data-f="${id}" class="num">${id}</a>`;
  const SETTLED = f => /^(Superseded|Settled) 2[79] Sep/.test(f.note || '');   // an inferred fact settled since: by the firmware's map (27 Sep) or E56 (29 Sep) (build_facts.py, AMEND, AMEND2)
  $('honest-text').innerHTML = `<p>The page rests on ${fs.length} facts: <b>${meas.length} measured</b>, ${of('spec').length} from the specification (the datasheet, the Programmer's Reference Manual, the core-et documents and the firmware and runtime source), ${of('derived').length} derived from others and <b>${of('inferred').length} inferred</b>. Of the measured facts, ${mc(3)} hold on all three lab cards (aifoundry2, aifoundry3 and aifoundry1 card 1), ${mc(2)} on two and ${mc(1)} on one, mostly aifoundry2${mc(0) ? `; ${mc(0)} ${mc(0) === 1 ? 'names' : 'name'} no card` : ''}. Every table here is at ${n('mhz')}, where a warm card sits.</p>`
    + `<p>What the drawing assumes, and what the second version (27 September) and the measurements of 29 September settled:</p><ul>`
    + `<li><b>Where the compute shires are</b> is measured: all ${n('pairs496')} shire pairs fit a constant plus ${n('hop_cyc')} per hop of Manhattan distance on the logical map (${lk('mesh.shortest-paths')}). <b>How that map sits on the die</b> was inferred (${lk('mesh.orientation')}, ${lk('L33')}, ${lk('L34')}); it is now the firmware's own: the "default Shire Virtual ID Map, based on the NOC spec", renamed as the boot firmware renames the shires, matches the measured map in ${n('fw_pairs')} pair distances with no rotation or mirror (${lk('fw.map-match')}; fact ${lk('L37')}, which compared the map before the renaming, is superseded). Still open: whether the silicon has this handedness or the published die plot's, its mirror (${lk('die.handedness')}, ${lk('L24')}).</li>`
    + `<li><b>The four cells without a compute shire</b>: the firmware's maps name them, the master (shire 32) in the north cell, the spare (33) in the south one, PCIe and then I/O east of the master (${lk('fw.grey-cells')}). They are drawn solid now. Timing a counter read on shire 32 from every compute shire confirms the master's cell on a card: E56 did so on 29 September, and it placed shire 32 in the firmware's cell on aifoundry1 card 1 and decided nothing on aifoundry3 (the asks below).</li>`
    + `<li><b>The memory shires' places</b> come from a fit of DRAM latencies on one card, aifoundry2 (${lk('L40')}), within ±3 cycles for ${n('ms_fit')} of loads on all three cards (${lk('ms-fit-3cards')}). The firmware's map puts the 7 memory shires the fit places on its own in the same places, if its mcN is the memory shire that PA[8:6] = N selects; memory shire 2, a tie in the fit, then has one cell left in both (${lk('fw.memshires')}, ${lk('ms2-forced')}), so the map confirms the frame, not memory shire 2 on its own. Timing a counter read on each memory shire places it directly: E56's timings (29 September) put six of the eight, memory shire 2 among them, where the drawing has them on aifoundry1 card 1, and decided nothing on aifoundry3 (the asks below).</li>`
    + `<li><b>Which two memory shires share each LPDDR4X package</b> is not documented; the drawing pairs neighbours (${lk('dram.pkg-pairing')}, ${lk('L23')}). The packages are dashed: the card's schematic settles it.</li>`
    + `<li><b>Routes</b> are measured now (${lk('L104')}, 29 September): the mesh takes a request x first, then y, on the logical map, and a reply y first, then x, back along its request's links. E56 streamed tensor loads and stores between shires in sets that share one link under one order and none under the other: loads slowed to ${n('route_rd')} of their bandwidth alone only where their replies share a link under y first, stores to ${n('route_wr')} only where their data share one under x first, on aifoundry1 card 1 and, frozen beforehand, on aifoundry3. Until then every leg here was drawn x first. Still drawn on an assumption: that a load's small request goes x first and a store's acknowledgement y first (too small to slow a link, they were not seen), that a memory shire's replies follow the same rule, and that TensorSend and the tree's messages travel as requests.</li>`
    + `<li><b>The way back</b> of a DRAM load: the data returns through the L3 home, as the shire cache specification describes an L3 miss (${lk('sc.l3-miss')}); the model pays the mesh round trip on both legs (${lk('addr.load-model')}). Each leg of the way back is a reply, drawn y first, beside its request's line: replies are told by their colour and their own lane. <b>Dashes</b> mark only what is inferred: the four LPDDR4X packages, and in flow 6 the L3's write-back of the host's lines to DRAM.</li>`
    + `<li><b>Inside a shire</b>, the drawing is a block diagram: no source gives where the banks and neighbourhoods sit in the tile (${lk('L114')}). The minions' order in a neighbourhood follows the core-et floorplan (${lk('L115')}).</li>`
    + `<li><b>Sizes</b>: the die's width and height and the tile pitch are pixel estimates on one vendor die plot scaled to ${n('die_mm2')} mm² (${lk('chip.die-dims')}, ${lk('chip.hop-pitch')}).</li>`
    + `<li><b>The host link</b> is measured now, on three cards (${lk('pcie.h2d')}, ${lk('pcie.d2h')}, ${lk('pcie.staged')}, ${lk('pcie.launch')}). Since 29 September (E55, on aifoundry1 card 1 and aifoundry3) so is the way the host's writes reach the chip: through their lines' L3 homes, which keep them, so a kernel's first touch of a freshly copied buffer hits the L3 (${lk('pcie.write-l3')}); only the L3's later write-back to DRAM is drawn dashed. Two DMA commands collide only inside one stream (${lk('pcie.conc')}).</li>`
    + `<li><b>Gathers and scatters</b> (E48) were reduced on 27 September and have no published page yet; the heat race of flow 8 is one card's (aifoundry2).</li>`
    + `<li><b>What was measured for this version.</b> Only the host link was measured anew (27 September, three cards: ${lk('pcie.h2d')}), and on 29 September the routing order (${lk('L104')}), which moved every reply onto its own route, where a host copy lands (${lk('pcie.write-l3')}), the DRAM address map's banks and rows (${lk('L50')}) and that the L2 keeps a TensorLoad's lines (${lk('minion.tensor-cache-path')}). Flows 7, 8, 9 and 0 draw measurements already in the repository: the matmul benchmark and the tensor-load timings, the Horace runs of the same matmul on different data, the hot-line passes and the allreduce ladder, each fact with its data file.</li>`
    + `<li><b>The broadcast (flow B, 28 September)</b> measures nothing new either: it draws the allreduce ladder (its 1 KB rows read from the version-3 raw files, ${lk('bc.allreduce-1kb')}), the relay, the hot line's passes and the launch timings, with the firmware source for the launch's own multicast (${lk('bc.launch-multicast')}). What was not measured is said on its stages: the tree's broadcast half on its own and the tree's energy (${lk('bc.half')}), a relay's time to reach every shire, every minion loading one line at once (${lk('bc.one-request')}), and the launch's multicast apart from the rest of a launch (${lk('bc.launch-31')}).</li></ul>`
    + `<p>The inferred facts still open:</p><ul>${of('inferred').filter(f => !SETTLED(f)).map(f => `<li>${esc(f.statement)} <span class="small">(${lk(f.id)})</span></li>`).join('')}</ul>`
    + `<p>Inferred before and settled since, by the firmware's map (27 September) or by a measurement (29 September); each fact's note says what is left:</p><ul>${of('inferred').filter(SETTLED).map(f => `<li>${esc(f.statement)} <span class="small">(${lk(f.id)}: ${esc(f.note)})</span></li>`).join('')}</ul>`;
  // the asks: what would settle each inferred part, and the hub's row that asks for it
  const BADGE = {settled: '<span class="kd measured">settled</span>', nearly: '<span class="kd spec">nearly settled</span>', confirm: '<span class="kd spec">to confirm</span>'};
  $('asktab').querySelector('tbody').innerHTML = ASKS.map(a => `<tr><td data-label="Part"><b>${esc(a.part)}</b>${BADGE[askState(a)] ? ' ' + BADGE[askState(a)] : ''}</td><td data-label="What is inferred">${esc(a.what_is_inferred)}</td><td data-label="What would settle it" class="small">${esc(a.what_settles_it)}</td><td data-label="Ask">${askLinks(a).join('<br>') || esc(a.ask_detail || '')}</td></tr>`).join('');
  // every fact
  const tb = document.querySelector('#facttab tbody');
  tb.innerHTML = Object.keys(F).sort().map(id => { const f = F[id];
    return `<tr><td data-label="Fact"><code>${esc(id)}</code></td><td data-label="Statement">${esc(f.statement)}${f.url ? ` <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)}</a>` : ''}</td><td data-label="Kind"><span class="kd ${f.kind}">${f.kind}</span></td><td data-label="Cards">${esc(cardsTxt(f))}</td><td data-label="Source" class="small">${esc(f.source)}</td></tr>`; }).join('');
  CK.sortTable('facttab', {filter: true, filterLabel: 'Filter facts'});
}

/* ================= start ================= */
buildChip();
buildPip();
/* the phone's drawing on or off (PH): the stage's class, the box's shape, the view, and the band's fold whenever a flow
   draws in the band (packets, trails, glows and pulses come and go too often to be worth a look) */
let foldObs = null;
function phApply() {
  $('stage').classList.toggle('ph', PH);
  svg.setAttribute('preserveAspectRatio', PH ? 'xMidYMin meet' : 'xMidYMid meet');
  if (foldObs) { foldObs.disconnect(); foldObs = null; }
  Object.assign(PHV, {flow: false, extra: 0, ar: ''});
  if (!PH) { svg.style.aspectRatio = ''; svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`); if (!ZW) setT(LAYERS[Z.level], null); return; }
  phBox();
  const busy = n => n.nodeType !== 1 || n.tagName === 'circle' || /\b(pk|trail|glow)\b/.test(n.getAttribute('class') || '');
  try { foldObs = new MutationObserver(ms => { if (ms.some(m => [...m.addedNodes, ...m.removedNodes].some(n => !busy(n)))) foldSoon(); }); foldObs.observe(FX[0], {childList: true, subtree: true}); } catch (_) { /* no observer */ }
}
/* The window crosses PH (a phone turned, a window resized): the die is drawn again for the new shape, at the chip's
   scale; the tour or flow that played stops. A shire or a minion is drawn anew at each zoom into it. */
let phT = 0;
function phSwitch() {
  clearTimeout(phT);
  phT = setTimeout(() => {
    if (mqOn(PHQ) === PH) return;
    if (TOUR) endTour();
    stopFlow(); select(null);
    goTo({level: 0}, {total: 0}).then(() => {
      if (mqOn(PHQ) === PH || ZW) return;
      phGeom();
      LAYERS[0].textContent = ''; buildChip();
      PIP.svg.textContent = ''; PIP.tiles = {}; buildPip();
      phApply(); scaleUI(); showComp('chip', {}); resetCap(); fitCap();
    });
  }, 250);
}
phApply();
try { matchMedia(PHQ).addEventListener('change', phSwitch); } catch (_) { /* an old browser: the shape stays as loaded */ }
/* in a frame, the page's gutters (CSS html.et-framed: spacesheep's comment tab covers the frame's left edge on a phone);
   a touch screen that cannot go full screen offers no Present button */
if (FRAMED) document.documentElement.classList.add('et-framed');
if (TOUCH) { $('stage').classList.add('touch'); if (!fsOK()) $('stage').classList.add('nofs'); }
scaleUI();
prose();
showComp('chip', {});
resetCap();
playBtn();
try {
  const q = new URLSearchParams(location.search);
  setTheme(q.get('theme'));
  if (q.get('panel') === 'off') togglePanel(false);
  const f = q.get('flow'); if (f && '1234567890'.includes(f) && f.length === 1) startFlow(ORDER['1234567890'.indexOf(f)], 0, {intro: true});
  else if (f && f.toLowerCase() === 'b') startFlow('K', 0, {intro: true});
  else if (q.get('tour') === '1') startTour(0);
} catch (_) { /* no URL flags */ }
if (window.__ET_PRESENTER) { setTimeout(() => toast('<p><b>Presenter window.</b> Press <kbd>F</kbd> for full screen; <kbd>T</kbd> starts the tour.</p>', 9000), 300); }
fitCap();
/* a read-only view of the state, for the page's tests (headless Chrome) */
window.__chipState = () => ({level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi, flow: FL.k, stage: FL.i, done: FL.done, still: FL.still,
  clockOn: CLK.on, clock: Math.round(CLK.t), follow: FOLLOW, zooming: ZW, pip: !PIP.el.hidden, pres: PRES, tour: TOUR ? TOUR.i : null,
  transform: [0, 1, 2].map(i => LAYERS[i].getAttribute('transform')), shown: [0, 1, 2].map(i => LAYERS[i].style.display !== 'none')});
})();
