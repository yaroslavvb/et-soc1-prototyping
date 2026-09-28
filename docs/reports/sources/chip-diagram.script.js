/* The ET-SoC-1, interactively. D is facts.json (docs/reports/data/2026-09-27-chip-diagram/build_facts.py):
   D.facts  the facts the page uses, by id: statement, value, unit, source, kind (measured, spec, derived, inferred),
            the lab cards each covers, and the report page that quotes it
   D.num    every number the page prints outside a fact's own statement, each tied to the fact whose statement
            contains it (the build asserts that); n(key) prints one with its source on hover
   D.comp   the facts each details panel lists
   D.layout the measured 6 x 6 map of the compute shires, the die view and the memory-shire fit
   D.asks   what would settle each inferred or dashed part, and the hub's ladder row that asks for it (D.rungs: the
            titles of those rows, read from the hub's own data)
   A value the page computes (a route's hops, a model's cycles) cites the facts it comes from. Every leg, a reply
   included, is drawn on its own route, x first, then y, on the logical map; where x first would cross an empty
   corner (some legs from a memory shire), y first. The mesh's routing order was not measured (fact L104). Colours
   are the template's tokens only.

   Second version (27 September). Every flow is a list of stages, shown in the stage bar under the drawing: a click
   or the Left and Right arrows go to a stage, and Space pauses everything that moves, the camera included (stepping
   while paused draws the stage's end state). The camera follows the flow (Follow, key C) or stays where the reader
   put it; then a stage on the die plays in a small picture of the die, and a stage inside a shire or a minion the
   camera is not showing marks its place. The scale control (Chip, Shire, Minion, + and -) is always there; a double
   click or Enter zooms into a shire or a minion. Every camera move eases in and out and zooms at a steady rate on a
   log scale; a flow's packet rides the zoom from one scale to the next. F presents: full screen where the frame
   allows it, else the stage fills the frame and offers F11 and a presenter window (a copy of the page in a window of
   its own). With reduced motion nothing animates: each stage draws its end state.
   Keys: 1-9 and 0 flows, Left/Right (and PageUp/PageDown) stages, crossing to the next tour slide at a flow's ends;
   Shift+Left/Right tour slides; Space pauses; + and - zoom; Enter on a part zooms in; Backspace zooms out; C follow;
   F present; P panel; D light and dark; T tour; Q or Esc end the tour. URL flags: ?theme=light|dark, ?panel=off,
   ?flow=1..9|0. */
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
/* a number from D.num, with its fact attached */
function n(k, unit) {
  const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; }
  return `<span class="num" data-f="${x.f}">${esc(x.t)}${unit ? ' ' + esc(unit) : ''}</span>`;
}
/* a number the page computes, citing the facts it comes from */
const cn = (v, fids, dp, unit) => `<span class="num" data-f="${fids}">${fnum(v, dp)}${unit ? ' ' + unit : ''}</span>`;
const S = (node, o) => { for (const k in o) if (o[k] != null) node.style[k] = o[k]; return node; };
const E = (tag, attrs, parent) => CK.el(tag, attrs, parent);
function T(parent, x, y, str, cls, anchor, fids) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  t.textContent = str; if (fids) t.setAttribute('data-f', fids);
  return t;
}
const ns = cyc => cyc * 1000 / V('mhz');   // minion cycles at 600 MHz to ns

/* ================= geometry: the die drawn to scale (sizes inferred from a die plot) ================= */
const MM = 30;                                         // SVG units per mm
const TILE = V('grid_mm') / 6 * MM, STRIP = V('strip_mm') * MM;
const DW = 2 * STRIP + 6 * TILE, DH = 6 * TILE, INS = 5;
const VB = {x: -190, y: -84, w: 1300, h: 792};
const SF = {x: 110, y: -36, w: 700, h: 700};          // where a shire is drawn when zoomed in
const MF = {x: -110, y: -70, w: 1140, h: 760};         // where a minion is drawn when zoomed in
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
/* every leg on its own route: x first, then y, on the logical map; a leg that x first would take across an empty
   corner of the grid (from a memory shire along its column towards logical row 0 or 5) goes y first */
function route(a, b) { return xy(a, b, true) || xy(a, b, false) || [a, b]; }
/* a path through several stops, each leg on its own route */
function via(...cs) { let out = [cs[0]]; for (let i = 1; i < cs.length; i++) out = out.concat(route(cs[i - 1], cs[i]).slice(1)); return out; }
const pts = cells => cells.map(c => ({x: c.sx, y: c.sy}));
const cellName = c => !c ? 'the die edge' : c.type === 'cshire' ? 'shire ' + c.id : c.type === 'memshire' ? 'memory shire ' + c.id
  : c.type === 'master' ? (c.r === 0 ? 'master shire' : 'spare shire') : c.type === 'pcie' ? 'PCIe shire' : c.type === 'io' ? 'I/O shire' : 'grey cell';

/* ================= the SVG and its three layers ================= */
const svg = $('chip');
svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
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
function boxShape(g, x, y, w, h, col, o) {
  o = o || {};
  S(E('rect', {class: 'shape', x, y, width: w, height: h, rx: o.rx == null ? 10 : o.rx}, g),
    {fill: o.fill || col, fillOpacity: o.fo == null ? 0.12 : o.fo, stroke: col, strokeWidth: o.sw || 2.5, strokeDasharray: o.dash ? '10 7' : null});
  E('rect', {class: 'ring', x: x - 5, y: y - 5, width: w + 10, height: h + 10, rx: (o.rx == null ? 10 : o.rx) + 4}, g);
}

function buildChip() {
  const L = LAYERS[0];
  // LPDDR4X packages off the die, two per side (datasheet Fig. 2-6, fact L23). Two memory shires share each package;
  // which two is not documented, so the pairing of neighbours is inferred and the packages are dashed (dram.pkg-pairing)
  const PKG = {};
  [[0, 1], [2, 3], [4, 5], [6, 7]].forEach(ms => {
    const a = MSC[ms[0]], b = MSC[ms[1]], west = a.c === 0;
    const x = west ? -150 : DW + 40, w = 110, y = a.y + 8, h = b.y + b.h - 8 - y;
    const g = comp(L, 'dram', {ms}, `LPDDR4X package, drawn beside memory shires ${ms[0]} and ${ms[1]} (pairing inferred): details`);
    ms.forEach(m => { const c = MSC[m];
      [-14, 14].forEach((dy, k) => {
        S(E('line', {x1: west ? x + w : DW, x2: west ? 0 : x, y1: c.sy + dy, y2: c.sy + dy}, g), {stroke: 'var(--c3)', strokeWidth: 3.5});
        PKG[m + ':' + k] = {x: west ? x + w - 6 : x + 6, y: c.sy + dy};
      });
      PKG[m] = {x: x + w / 2, y: c.sy};
    });
    boxShape(g, x, y, w, h, 'var(--c3)', {fo: 0.16, sw: 3, dash: true});
    const cx = x + w / 2, cy = y + h / 2;
    T(g, cx, cy - 16, 'LPDDR4X', 't-labb', 'middle', 'dram.pkg-pairing');
    T(g, cx, cy + 10, 'four 16-bit', 't-sm', 'middle', 'L47');
    T(g, cx, cy + 31, 'channels', 't-sm', 'middle', 'L47');
  });
  AP[0].pkg = PKG;
  // the die: its outline is the component "chip"
  const gd = comp(L, 'chip', {}, 'The ET-SoC-1 die: details');
  S(E('rect', {class: 'shape', x: 0, y: 0, width: DW, height: DH, rx: 16}, gd), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 3});
  E('rect', {class: 'ring', x: -6, y: -6, width: DW + 12, height: DH + 12, rx: 20}, gd);
  T(gd, 0, -24, `ET-SoC-1 · ${N.die_mm2.t} mm² · TSMC ${N.process.t}`, 't-mid', 'start', 'chip.die-area chip.process');
  // the host and the PCIe link (from the PCIe shire's top edge), now timed on three cards
  const pc = CELLS.find(c => c.type === 'pcie'), hx = 950, hy = -74, hw = 150, hh = 92, ly = -30;
  const gh = comp(L, 'host', {}, 'The host and the PCIe link: details');
  S(E('path', {d: `M${pc.sx},${pc.y + INS} V${ly} H${hx}`, fill: 'none'}, gh), {stroke: 'var(--c4)', strokeWidth: 6, strokeLinejoin: 'round'});
  boxShape(gh, hx, hy, hw, hh, 'var(--ink-2)', {fo: 0.08});
  T(gh, hx + hw / 2, hy + 54, 'Host', 't-mid', 'middle');
  T(gh, hx - 14, ly - 12, `PCIe Gen4 x8 · ${N.pcie_h2d.t} GB/s to the card`, 't-sm halo', 'end', 'pcie.h2d pcie.negotiated');
  AP[0].host = [{x: hx + 4, y: ly}, {x: pc.sx, y: ly}, {x: pc.sx, y: pc.sy}];
  AP[0].hostBox = {x: hx, y: hy, w: hw, h: hh, ly};
  // mesh links and stops, under the translucent tiles (visual only: the tiles take the clicks)
  const LG = E('g', {class: 'dimmable links', 'pointer-events': 'none'}, L);
  AP[0].links = LG;
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hops(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly))
      S(E('line', {x1: a.sx, y1: a.sy, x2: b.sx, y2: b.sy}, LG), {stroke: 'var(--axis)', strokeWidth: 4, strokeLinecap: 'round'});
  }));
  CELLS.forEach(c => S(E('circle', {cx: c.sx, cy: c.sy, r: 6.5}, LG), {fill: 'var(--ink-2)'}));
  // the tiles: the four cells without a compute shire are named by the firmware's map (fact fw.grey-cells)
  CELLS.forEach(c => {
    const g = comp(L, c.type, {cell: c}, tileLabel(c)); c.g = g;
    boxShape(g, c.x + INS, c.y + INS, c.w - 2 * INS, c.h - 2 * INS, COL[c.type], {fo: c.type === 'cshire' ? 0.14 : 0.12});
    const x0 = c.x + INS + 9, y0 = c.y + INS;
    if (c.type === 'cshire') T(g, x0, y0 + 38, String(c.id), 't-id');
    else if (c.type === 'memshire') { T(g, c.x + c.w / 2, y0 + 26, 'MS', 't-labb halo-s', 'middle'); T(g, c.x + c.w / 2, y0 + 50, String(c.id), 't-labb halo-s', 'middle'); }
    else if (c.type === 'master') { const north = c.r === 0; T(g, x0, y0 + 27, north ? 'Master' : 'Spare', 't-labb halo-s', 'start', 'fw.grey-cells'); T(g, x0, y0 + 50, 'shire ' + (north ? N.master_id.t : N.spare_id.t), 't-sm halo-s', 'start', 'fw.grey-cells chip.master-shire-id'); }
    else if (c.type === 'pcie') T(g, x0, y0 + 30, 'PCIe', 't-labb halo-s');
    else if (c.type === 'io') { T(g, x0, y0 + 27, 'I/O', 't-labb halo-s'); T(g, x0, y0 + 50, 'Maxions', 't-sm halo-s'); }
  });
  // the mesh as a component, and a button for what is inferred and what would settle it
  const gm = comp(L, 'mesh', {}, 'The mesh: details');
  boxShape(gm, 0, DH + 9, 292, 30, 'var(--ink-2)', {fo: 0.06, rx: 15});
  T(gm, 14, DH + 31, `The mesh: ${N.grid86.t}, ${N.stops.t} stops`, 't-labb', 'start', 'mesh.grid');
  const gi = comp(L, 'inferred', {}, 'What the drawing infers, and what would settle it: details');
  boxShape(gi, DW - 372, DH + 9, 372, 30, 'var(--c1)', {fo: 0.07, rx: 15});
  T(gi, DW - 186, DH + 30, 'Dashed: inferred · what would settle it ›', 't-sm', 'middle').style.fill = 'var(--ink)';
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
  const fr = E('g', {}, L);
  S(E('rect', {x: X, y: Y, width: W, height: W, rx: 22}, fr), {fill: 'var(--c1)', fillOpacity: 0.05, stroke: 'var(--c1)', strokeWidth: 3});
  T(fr, X + 22, Y + 40, `Shire ${sid}`, 't-big');
  T(fr, X + W - 22, Y + 38, `map (${cell.lx}, ${cell.ly}) · ${N.per_shire.t}`, 't-sm', 'end', 'mesh.logical-map shire.composition');
  // mesh neighbours, in die orientation
  const nb = [[-1, 0, 'N'], [1, 0, 'S'], [0, -1, 'W'], [0, 1, 'E']].map(([dr, dc, s]) => [BYDIE[(cell.r + dr) + ',' + (cell.c + dc)], s]);
  P.edge = {};
  nb.forEach(([c, s]) => {
    const st = {stroke: 'var(--axis)', strokeWidth: 5, strokeLinecap: 'round'};
    const lab = c ? cellName(c) : 'die edge';
    if (s === 'N') { if (c) S(E('line', {x1: X + W / 2, y1: Y, x2: X + W / 2, y2: Y - 24}, fr), st); T(fr, X + W / 2 + 12, Y - 18, (c ? '↑ ' : '') + lab, 't-sm'); P.edge.N = {x: X + W / 2, y: Y - 24}; }
    if (s === 'S') { if (c) S(E('line', {x1: X + W / 2, y1: Y + W, x2: X + W / 2, y2: Y + W + 24}, fr), st); T(fr, X + W / 2 + 12, Y + W + 30, (c ? '↓ ' : '') + lab, 't-sm'); P.edge.S = {x: X + W / 2, y: Y + W + 24}; }
    if (s === 'W') { if (c) S(E('line', {x1: X, y1: Y + W / 2, x2: X - 24, y2: Y + W / 2}, fr), st); T(fr, X - 30, Y + W / 2 + 6, lab + (c ? ' ←' : ''), 't-sm', 'end'); P.edge.W = {x: X - 24, y: Y + W / 2}; }
    if (s === 'E') { if (c) S(E('line', {x1: X + W, y1: Y + W / 2, x2: X + W + 24, y2: Y + W / 2}, fr), st); T(fr, X + W + 30, Y + W / 2 + 6, (c ? '→ ' : '') + lab, 't-sm'); P.edge.E = {x: X + W + 24, y: Y + W / 2}; }
  });
  // key, in the left margin
  const kx = VB.x + 14, ky = Y + 440;
  T(fr, kx, ky, 'Key', 't-labb');
  S(E('line', {x1: kx, y1: ky + 24, x2: kx + 36, y2: ky + 24}, fr), {stroke: 'var(--c4)', strokeWidth: 6, strokeLinecap: 'round'});
  T(fr, kx + 46, ky + 30, 'fast local', 't-sm'); T(fr, kx + 46, ky + 50, 'network edge', 't-sm');
  S(E('line', {x1: kx + 18, y1: ky + 70, x2: kx + 18, y2: ky + 104}, fr), {stroke: 'var(--ink-2)', strokeWidth: 4});
  T(fr, kx + 46, ky + 86, 'ET-Link to', 't-sm'); T(fr, kx + 46, ky + 106, 'the shire cache', 't-sm');
  T(fr, kx, ky + 150, 'Block diagram,', 't-sm'); T(fr, kx, ky + 170, 'not a floorplan', 't-sm', 'start', 'L114');
  // mesh stop
  const gs = comp(L, 'meshstop', {sid}, 'Mesh stop: details');
  boxShape(gs, X + 20, Y + 58, W - 40, 62, 'var(--ink-2)', {fo: 0.07});
  T(gs, X + 36, Y + 97, 'Mesh stop', 't-mid');
  T(gs, X + 180, Y + 97, 'lane = PA[7:6]', 't-sm', 'start', 'L103');
  for (let i = 0; i < 4; i++) {
    const lx = X + W - 40 - (4 - i) * 58 + 6;
    S(E('rect', {x: lx, y: Y + 68, width: 48, height: 42, rx: 6}, gs), {fill: 'var(--page)', stroke: 'var(--ink-2)', strokeWidth: 2});
    T(gs, lx + 24, Y + 96, String(i), 't-labb', 'middle', 'L103');
    P.lane[i] = {x: lx + 24, y: Y + 89};
  }
  P.stop = {x: X + W / 2, y: Y + 58};
  // four banks and the UC block
  const bw = (500 - 3 * 10) / 4;
  for (let i = 0; i < 4; i++) {
    const bx = X + 20 + i * (bw + 10), by = Y + 134;
    const g = comp(L, 'banks', {bank: i}, `Shire cache bank ${i}: details`);
    boxShape(g, bx, by, bw, 108, 'var(--c1)', {fo: 0.1});
    for (let k = 1; k < 4; k++) S(E('line', {x1: bx + k * bw / 4, y1: by + 52, x2: bx + k * bw / 4, y2: by + 100}, g), {stroke: 'var(--c1)', strokeOpacity: 0.5, strokeWidth: 2});
    T(g, bx + 10, by + 30, `Bank ${i}`, 't-labb');
    T(g, bx + bw / 2, by + 84, '4 sub-banks', 't-sm halo-s', 'middle', 'shire.cache-geometry');
    P.bank[i] = {x: bx + bw / 2, y: by + 54, box: {x: bx, y: by, w: bw, h: 108}};
  }
  const gu = comp(L, 'uc', {}, 'UC block: barriers, credits and atomics: details');
  boxShape(gu, X + 530, Y + 134, W - 550, 108, 'var(--c7)', {fo: 0.1});
  T(gu, X + 544, Y + 164, 'UC block', 't-labb');
  T(gu, X + 544, Y + 190, 'barriers,', 't-sm'); T(gu, X + 544, Y + 210, 'credits, atomics', 't-sm');
  P.uc = {x: X + 530 + (W - 550) / 2, y: Y + 188};
  // the 4 MB in mode M0: scratchpad, L3 slice, L2
  const parts = [['scp', V('scp_mb'), 'Scratchpad', N.scp_mb.t, 'var(--c4)'], ['l3', V('l3_mb'), 'L3 slice', N.l3_mb.t, 'var(--c3)'], ['l2', V('l2_kb') / 1024, 'L2', N.l2_kb.t, 'var(--c2)']];
  // widths in proportion to the sizes, except the L2, drawn wider (104 units) so that its label fits
  const L2W = 104, rest = parts.filter(p => p[0] !== 'l2').reduce((s, p) => s + p[1], 0);
  let px = X + 20;
  parts.forEach(([k, mb, nm, t, col]) => {
    const w = k === 'l2' ? L2W : (500 - L2W) * mb / rest, g = comp(L, k, {sid}, `${nm}, ${t}: details`);
    boxShape(g, px, Y + 252, w - 4, 46, col, {fo: 0.2, rx: 6});
    if (w > 200) T(g, px + 10, Y + 282, `${nm} · ${t}`, 't-labb', 'start', 'shire.partition-m0');
    else { T(g, px + 8, Y + 271, nm, 't-labb'); T(g, px + 8, Y + 292, t, 't-sm', 'start', 'shire.partition-m0').style.fontSize = '18px'; }
    P[k] = {x: px + w / 2, y: Y + 275};
    px += w;
  });
  T(fr, X + 530, Y + 272, 'mode M0 split', 't-sm', 'start', 'shire.partition-m0 shire.partition-measured');
  T(fr, X + 530, Y + 292, 'L2 not to scale', 't-sm', 'start', 'shire.partition-m0');
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
    T(gn, nx + nw / 2, ny + 28, `Neighbourhood ${k}`, 't-sm', 'middle');
    // link up to the crossbar through the neighbourhood channel
    S(E('line', {x1: nx + nw / 2, y1: ny, x2: nx + nw / 2, y2: Y + 338}, G), {stroke: 'var(--ink-2)', strokeWidth: 4});
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
    // tree edges of the fast local network, drawn over the minions' edges (fact L115)
    LAY.neighbourhood_floorplan.fast_tree_edges.forEach(([a, b]) => {
      const A = pos[a], B = pos[b], hz = A.y === B.y, s1 = A.x < B.x || A.y < B.y ? A : B, s2 = s1 === A ? B : A;
      const q = hz ? {x1: s1.x + s1.w - 10, y1: s1.y + s1.h / 2, x2: s2.x + 10, y2: s2.y + s2.h / 2} : {x1: s1.x + s1.w / 2, y1: s1.y + s1.h - 9, x2: s2.x + s2.w / 2, y2: s2.y + 9};
      S(E('line', Object.assign(q, {'pointer-events': 'none'}), G), {stroke: 'var(--c4)', strokeWidth: 7, strokeLinecap: 'round'});
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
  const fr = E('g', {}, L);
  S(E('rect', {x: X, y: Y, width: W, height: H, rx: 24}, fr), {fill: 'var(--c1)', fillOpacity: 0.04, stroke: 'var(--c1)', strokeWidth: 3});
  T(fr, X + 24, Y + 44, `Minion ${mi} · neighbourhood ${nb} · shire ${sid}`, 't-big');
  T(fr, X + W - 24, Y + 42, `harts ${h0} and ${h0 + 1}`, 't-lab', 'end', 'chip.harts');
  // two harts
  [0, 1].forEach(t => {
    const hy = Y + 70 + t * 240, g = comp(L, 'hart', {t}, `Hart ${t}: details`);
    boxShape(g, X + 24, hy, 320, 228, 'var(--c1)', {fo: 0.08});
    T(g, X + 40, hy + 34, `Hart ${t}`, 't-mid');
    if (t === 0) T(g, X + 40, hy + 62, 'issues every tensor instruction', 't-sm', 'start', 'minion.tensor-hart0');
    else { T(g, X + 40, hy + 60, 'tensor: only TensorLoadL2Scp,', 't-sm', 'start', 'minion.tensor-hart0'); T(g, X + 40, hy + 81, 'TensorWait and tensor_coop', 't-sm', 'start', 'minion.tensor-hart0'); }
    for (let i = 0; i < 32; i++) {
      const rx = X + 40 + (i % 8) * 36, ry = hy + 94 + Math.floor(i / 8) * 25;
      P.regs[t].push(S(E('rect', {x: rx, y: ry, width: 32, height: 21, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.25, stroke: 'var(--c1)', strokeWidth: 1}));
    }
    T(g, X + 40, hy + 214, `f0–f31, ${N.vreg256.t}`, 't-sm', 'start', 'minion.vpu');
    P['hart' + t] = {x: X + 184, y: hy + 130};
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
      P.units[k].push(S(E('rect', {x: lx, y: uy, width: lw, height: 40, rx: 4, 'pointer-events': 'none'}, gv), {fill: 'var(--c3)', fillOpacity: k < 3 ? 0.3 : 0.14, stroke: 'var(--c3)', strokeWidth: 1.2}));
      T(gv, lx + lw / 2, uy + 26, u, 't-sm', 'middle');
    });
  }
  P.laneX = l => X + 376 + l * (lw + 6) + lw / 2; P.unitY = k => Y + 238 + k * 46 + 20;
  T(gv, X + 380, Y + 486, 'FMA · 2× int8 MA · integer · transcendental', 't-sm', 'start', 'minion.vpu');
  T(gv, X + 380, Y + 510, `peak ${N.vecpeak.t} per cycle, fp32,`, 't-labb', 'start', 'minion.vec-peak');
  T(gv, X + 380, Y + 531, 'the same for vector and tensor', 't-sm', 'start', 'minion.vec-peak');
  P.vpu = {x: X + 569, y: Y + 350};
  // the tensor sequencer: state machines in the VPU that run TensorFMA and TensorIMA on the lanes (fact minion.vec-peak)
  const gt = comp(L, 'tensor', {}, 'Tensor sequencer: details');
  const tx = X + 794, tw = W - 24 - 794;
  boxShape(gt, tx, Y + 70, tw, 468, 'var(--c2)', {fo: 0.07});
  T(gt, tx + 16, Y + 104, 'Tensor sequencer', 't-mid', 'start', 'minion.vec-peak');
  S(E('rect', {x: tx + 16, y: Y + 118, width: tw - 32, height: 100, rx: 8, 'pointer-events': 'none'}, gt), {fill: 'var(--c2)', fillOpacity: 0.16, stroke: 'var(--c2)', strokeWidth: 2});
  T(gt, tx + 30, Y + 148, 'TensorFMA · TensorIMA', 't-labb');
  T(gt, tx + 30, Y + 174, 'C += A · B', 't-sm');
  T(gt, tx + 30, Y + 198, N.tshape.t, 't-sm', 'start', 'minion.tensor-shape');
  P.seq = {x: tx + tw / 2, y: Y + 168};
  // the arrow into the lanes: the tensor work runs there
  const ay = Y + 250;
  P.arrow = S(E('line', {x1: tx + 46, y1: ay, x2: X + 774, y2: ay, 'pointer-events': 'none'}, gt), {stroke: 'var(--c2)', strokeWidth: 6, strokeLinecap: 'round'});
  S(E('polygon', {points: `${X + 760},${ay} ${X + 778},${ay - 11} ${X + 778},${ay + 11}`, 'pointer-events': 'none'}, gt), {fill: 'var(--c2)'});
  T(gt, tx + 56, ay + 6, 'runs on the 8 VPU lanes', 't-sm', 'start', 'minion.vec-peak');
  [['TenB', 0, '(logical)'], ['TenC', 1, '']].forEach(([nm, i, q]) => {
    const bx = tx + 16 + i * ((tw - 32) / 2 + 4), bwid = (tw - 40) / 2;
    S(E('rect', {x: bx, y: Y + 286, width: bwid, height: 84, rx: 8, 'pointer-events': 'none'}, gt), {fill: 'var(--c2)', fillOpacity: 0.1, stroke: 'var(--c2)', strokeWidth: 1.5});
    T(gt, bx + 12, Y + 314, nm, 't-labb');
    T(gt, bx + 12, Y + 338, N.tenb.t, 't-sm', 'start', 'minion.tenb-tenc');
    if (q) T(gt, bx + 12, Y + 360, q, 't-sm', 'start', 'minion.tenb-tenc');
    P[nm.toLowerCase()] = {x: bx, y: Y + 286, w: bwid, h: 84};
  });
  T(gt, tx + 16, Y + 402, 'tensor peak per cycle,', 't-sm');
  T(gt, tx + 16, Y + 423, 'on those lanes:', 't-sm');
  T(gt, tx + 16, Y + 450, `${N.peak32.t} · ${N.peak16.t}`, 't-labb', 'start', 'mm-peak');
  T(gt, tx + 16, Y + 474, `${N.peak8.t} ops`, 't-labb', 'start', 'mm-peak');
  T(gt, tx + 16, Y + 504, `chip: ${N.tflops.t} TFLOP/s fp32`, 't-sm', 'start', 'mm-rate');
  T(gt, tx + 16, Y + 527, 'measured, three cards', 't-sm', 'start', 'mm-rate');
  P.tensor = {x: tx + tw / 2, y: Y + 170};
  // L1 data cache: 16 sets, as the firmware leaves them (sets 0-11 tensor scratchpad, 12-13 hart 0, 14-15 hart 1)
  const gl = comp(L, 'l1d', {}, 'L1 data cache: details');
  boxShape(gl, X + 24, Y + 552, 750, 186, 'var(--c1)', {fo: 0.06});
  T(gl, X + 40, Y + 584, `L1 data cache · ${N.l1_kb.t} · as the firmware sets it`, 't-labb', 'start', 'minion.l1d minion.l1-firmware');
  const sw = (750 - 32 - 15 * 4) / 16, sx = k => X + 40 + k * (sw + 4), sy = Y + 600;
  for (let k = 12; k < 16; k++) S(E('rect', {x: sx(k), y: sy, width: sw, height: 64, rx: 4, 'pointer-events': 'none'}, gl), {fill: 'var(--c1)', fillOpacity: k < 14 ? 0.35 : 0.18, stroke: 'var(--c1)', strokeWidth: 1.5});
  T(gl, sx(12), sy + 90, 'hart 0', 't-sm', 'start', 'minion.l1-modes'); T(gl, sx(12), sy + 112, N.l1_hart.t, 't-sm', 'start', 'minion.l1-firmware');
  T(gl, sx(14), sy + 90, 'hart 1', 't-sm', 'start', 'minion.l1-modes'); T(gl, sx(14), sy + 112, N.l1_hart.t, 't-sm', 'start', 'minion.l1-firmware');
  const gp = comp(L, 'l1scp', {}, 'L1 tensor scratchpad: details');
  S(E('rect', {class: 'shape', x: sx(0) - 3, y: sy - 3, width: sx(11) + sw - sx(0) + 6, height: 70, rx: 6}, gp), {fill: 'transparent', stroke: 'var(--c7)', strokeWidth: 2.5});
  E('rect', {class: 'ring', x: sx(0) - 8, y: sy - 8, width: sx(11) + sw - sx(0) + 16, height: 80, rx: 9}, gp);
  for (let k = 0; k < 12; k++) S(E('rect', {x: sx(k), y: sy, width: sw, height: 64, rx: 4}, gp), {fill: 'var(--c7)', fillOpacity: 0.25, stroke: 'var(--c7)', strokeWidth: 1.5});
  T(gp, sx(0), sy + 90, `${N.sets011.t}: tensor scratchpad, ${N.l1_scp.t}`, 't-sm', 'start', 'minion.l1-modes');
  P.scpBox = {x: sx(0), y: sy, w: sx(11) + sw - sx(0), h: 64};
  P.l1h0 = {x: sx(12) + sw + 2, y: sy + 32};
  // ports
  const ge = comp(L, 'etlink', {}, 'ET-Link port: details');
  boxShape(ge, tx, Y + 552, tw, 96, 'var(--ink-2)', {fo: 0.07});
  T(ge, tx + 16, Y + 582, 'ET-Link port', 't-labb');
  T(ge, tx + 16, Y + 607, `to the shire cache: ${N.etl_min.t},`, 't-sm', 'start', 'minion.etlink-width');
  T(ge, tx + 16, Y + 630, `onto a shared ${N.etl512.t.replace(' ET-Link bus', '')} bus`, 't-sm', 'start', 'shire.neigh-link');
  P.etl = {x: tx + tw - 110, y: Y + 580};
  const gf = comp(L, 'fln', {}, 'Fast local network: details');
  boxShape(gf, tx, Y + 658, tw, 80, 'var(--c4)', {fo: 0.1});
  T(gf, tx + 16, Y + 690, 'Fast local network', 't-labb');
  T(gf, tx + 16, Y + 716, `${N.ts_fln.t} round trip on tree edges`, 't-sm', 'start', 'ts-rt-fln');
  P.fln = {x: tx + tw - 110, y: Y + 700};
  FX[2] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}

/* ---- the small picture of the die: what a stage on the die looks like while the camera is inside ---- */
const PIP = {el: $('pip'), svg: $('pipsvg'), fx: null, tiles: {}, on: false};
function buildPip() {
  const s = PIP.svg; s.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
  S(E('rect', {x: VB.x, y: VB.y, width: VB.w, height: VB.h}, s), {fill: 'var(--page)'});
  [[0, 1], [2, 3], [4, 5], [6, 7]].forEach(ms => {
    const a = MSC[ms[0]], b = MSC[ms[1]], west = a.c === 0, x = west ? -150 : DW + 40;
    S(E('rect', {x, y: a.y + 8, width: 110, height: b.y + b.h - 16 - a.y, rx: 10}, s), {fill: 'var(--c3)', fillOpacity: 0.16, stroke: 'var(--c3)', strokeWidth: 5, strokeDasharray: '12 8'});
  });
  S(E('rect', {x: 0, y: 0, width: DW, height: DH, rx: 16}, s), {fill: 'var(--surface)', stroke: 'var(--ink-2)', strokeWidth: 5});
  const hb = AP[0].hostBox, pc = CELLS.find(c => c.type === 'pcie');
  S(E('path', {d: `M${pc.sx},${pc.y + INS} V${hb.ly} H${hb.x}`, fill: 'none'}, s), {stroke: 'var(--c4)', strokeWidth: 8});
  S(E('rect', {x: hb.x, y: hb.y, width: hb.w, height: hb.h, rx: 10}, s), {fill: 'var(--ink-2)', fillOpacity: 0.1, stroke: 'var(--ink-2)', strokeWidth: 5});
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hops(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly)) S(E('line', {x1: a.sx, y1: a.sy, x2: b.sx, y2: b.sy}, s), {stroke: 'var(--axis)', strokeWidth: 6});
  }));
  CELLS.forEach(c => {
    PIP.tiles[c.r + ',' + c.c] = S(E('rect', {class: 'pt', x: c.x + INS, y: c.y + INS, width: c.w - 2 * INS, height: c.h - 2 * INS, rx: 10}, s),
      {fill: COL[c.type], fillOpacity: 0.16, stroke: COL[c.type], strokeWidth: 5});
  });
  PIP.fx = E('g', {class: 'fx'}, s);
}

/* ================= the animation clock: everything that moves runs on it, and Space stops it ================= */
const CLK = {t: 0, on: true, last: 0, jobs: new Set()};
(function loop(now) {
  const dt = CLK.last ? Math.min(80, now - CLK.last) : 0; CLK.last = now;
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
/* an element fading in on the clock (a callout, a label): nothing pops */
function fadeIn(el, ms) {
  if (!el || REDUCED || !CLK.on) return el;   // paused (a stage's end state): shown at once
  el.style.opacity = 0; const t0 = CLK.t, d = ms || 380;
  const j = () => { const p = Math.min(1, (CLK.t - t0) / d); el.style.opacity = p; if (p >= 1 || !el.isConnected) CLK.jobs.delete(j); };
  CLK.jobs.add(j);
  return el;
}

/* ================= the camera ================= */
const Z = {level: 0, sid: null, nb: 0, mi: 0};
let LASTSID = 13, LASTNB = 0, LASTMI = 0;
const lerp = (a, b, t) => a + (b - a) * t;
const lerpR = (A, B, t) => ({x: lerp(A.x, B.x, t), y: lerp(A.y, B.y, t), w: lerp(A.w, B.w, t), h: lerp(A.h, B.h, t)});
const easeIO = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const easeS = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const band = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rmap = (A, B) => { const k = B.w / A.w; return [k, B.x - k * A.x, B.y - k * A.y]; };
const setT = (g, m) => { if (m) g.setAttribute('transform', `matrix(${m[0]},0,0,${m[0]},${m[1]},${m[2]})`); else g.removeAttribute('transform'); };
/* a pure zoom: the frame's width moves geometrically (a steady rate on a log scale) and its place with it, so the
   point where the two frames coincide stays put */
const zoomR = (A, B, e) => { const w = A.w * Math.pow(B.w / A.w, e); return lerpR(A, B, (w - A.w) / (B.w - A.w)); };
/* a tween on real time (the reader's own zoom) or on the animation clock (a flow's or the tour's camera, which Space
   stops); a dead token finishes it at once */
function tween(ms, fn, clk) {
  return new Promise(res => {
    let done = false;
    const fin = () => { if (!done) { done = true; fn(1); res(); } };
    if (REDUCED || ms <= 0) return fin();
    if (clk) {
      const t0 = CLK.t, j = () => { if (clk.dead) { CLK.jobs.delete(j); fin(); return; } const p = Math.min(1, (CLK.t - t0) / ms); if (p >= 1) { CLK.jobs.delete(j); fin(); } else fn(p); };
      CLK.jobs.add(j); return;
    }
    const t0 = performance.now();
    const f = now => { if (done) return; const p = Math.min(1, (now - t0) / ms); if (p >= 1) fin(); else { fn(p); requestAnimationFrame(f); } };
    requestAnimationFrame(f);
    setTimeout(fin, ms + 800);   // a hidden tab gets no frames
  });
}
const tileRect = sid => { const c = SH[sid]; return {x: c.x + INS, y: c.y + INS, w: c.w - 2 * INS, h: c.h - 2 * INS}; };
const minRect = (nb, mi) => { const p = AP[1].min[nb + ':' + mi]; return {x: p.x, y: p.y, w: p.w, h: p.h}; };
/* a point of an inner view in its parent's coordinates: where a packet sits once the zoom has shrunk its view */
const mapOut = (A, B, p) => ({x: A.x + (p.x - B.x) * A.w / B.w, y: A.y + (p.y - B.y) * A.w / B.w});
const outOfMinion = (p, nb, mi) => mapOut(minRect(nb, mi), MF, p);
const outOfShire = (p, sid) => mapOut(tileRect(sid), SF, p);
async function zoomStep(dir, A, ms, efn, clk, carry) {
  const lo = dir > 0 ? Z.level : Z.level - 1, outer = LAYERS[lo], inner = LAYERS[lo + 1], B = lo === 0 ? SF : MF;
  // the zoom's first frame goes on before either view is shown: a view un-hidden at full size and full opacity would
  // be painted for one frame (the next animation job may run only after a paint)
  const frame = e => {
    const R = zoomR(A, B, e), Mo = rmap(A, R), Mi = rmap(B, R);
    setT(outer, Mo); setT(inner, Mi);
    outer.style.opacity = 1 - band(e, 0.3, 0.85); inner.style.opacity = band(e, 0.12, 0.7);
    return [Mo, Mi];
  };
  if (ms > 0 && !REDUCED) frame(dir > 0 ? 0 : 1);
  outer.style.display = ''; inner.style.display = '';
  LAYERS.forEach(l => l.classList.add('busy'));
  // a flow's packet rides the zoom at its own size, above both views, so that it never fades out between two legs
  let cg = null, p0 = null, inOuter = false;
  if (carry && carry.isConnected && ms > 0 && !REDUCED) {
    const li = LAYERS.indexOf(carry.closest('.lay')), m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(carry.getAttribute('transform') || '');
    if (m && (li === lo || li === lo + 1)) { p0 = {x: +m[1], y: +m[2]}; inOuter = li === lo; cg = carry.cloneNode(true); svg.appendChild(cg); carry.style.visibility = 'hidden'; }
  }
  try {
    await tween(ms, p => {
      const s = efn(p), [Mo, Mi] = frame(dir > 0 ? s : 1 - s);
      if (cg) { const M = inOuter ? Mo : Mi; at(cg, {x: M[0] * p0.x + M[1], y: M[0] * p0.y + M[2]}); }
    }, clk);
  } finally { if (cg) { cg.remove(); carry.style.visibility = ''; } }
  LAYERS.forEach(l => l.classList.remove('busy'));
  if (dir > 0) { outer.style.display = 'none'; setT(inner, null); inner.style.opacity = 1; Z.level = lo + 1; }
  else { inner.style.display = 'none'; setT(outer, null); outer.style.opacity = 1; Z.level = lo; }
  scaleUI();
}
/* the zooms from the current view to t: out while the view is deeper than the target or beside it, then in; each
   step's length on the log scale (a tile to a shire's frame, a minion's box to a minion's frame) */
const LOGT = Math.log(SF.w / (TILE - 2 * INS)), LOGM = Math.log(MF.w / 66);
function planChain(t) {
  const out = []; let lv = Z.level; const sid = Z.sid, nb = Z.nb, mi = Z.mi;
  while (lv > 0 && (lv > t.level || sid !== t.sid || (lv === 2 && (nb !== t.nb || mi !== t.mi)))) { out.push({dir: -1, L: lv === 2 ? LOGM : LOGT}); lv--; }
  while (lv < t.level) { out.push({dir: 1, L: lv === 0 ? LOGT : LOGM}); lv++; }
  return out;
}
/* one ease-in-out over a whole chain of zooms: each step gets its slice of the curve, so a zoom from the chip to a
   minion accelerates once and slows once, with no stop at the shire */
function chainSegs(plan, per) {
  const tot = plan.reduce((s, x) => s + x.L, 0), Tt = per * tot;
  const inv = f => { let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (easeIO(m) < f) lo = m; else hi = m; } return (lo + hi) / 2; };
  let acc = 0;
  return plan.map(st => {
    const f0 = acc / tot, f1 = (acc + st.L) / tot; acc += st.L;
    const t0 = inv(f0), t1 = inv(f1);
    return {ms: Tt * (t1 - t0), efn: p => Math.max(0, Math.min(1, (easeIO(t0 + p * (t1 - t0)) - f0) / (f1 - f0)))};
  });
}
/* The camera follows the latest request only: rapid presses never queue a chain of animations. goTo() resolves
   once the view reaches the latest target. o.clk: a token whose clock (the pausable one) drives the move;
   o.ms: milliseconds per unit of log scale (0 for a cut); o.keepFx: a flow's drawing rides the zoom. */
let ZT = null, ZW = false, ZWAIT = [], ZN = 0;
const zkey = () => Z.level + ':' + Z.sid + ':' + Z.nb + ':' + Z.mi;
function goTo(t, o) {
  o = o || {};
  const tt = {level: t.level || 0, sid: t.sid == null ? (Z.sid == null ? LASTSID : Z.sid) : t.sid, nb: t.nb || 0, mi: t.mi || 0};
  ZT = {t: tt, o, n: ++ZN};
  return new Promise(res => { ZWAIT.push(res); if (!ZW) { ZW = true; zoomWorker(); } });
}
async function zoomWorker() {
  const from = {level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi}, fromKey = zkey(), hadFocus = svg.contains(document.activeElement);
  let wantFocus = false, plan = [], sg = [], pi = 0, planN = -1;
  try {
    for (let guard = 0; ZT && guard < 16; guard++) {
      if (ZT.o.focus) wantFocus = true;
      if (ZT.n !== planN || pi >= plan.length) {
        const rush = planN !== -1 && ZT.n !== planN;   // a newer request came in on the way: hurry
        plan = planChain(ZT.t); pi = 0; planN = ZT.n;
        if (!plan.length) break;
        const per = ZT.o.ms != null ? ZT.o.ms : ZT.o.clk ? 760 : 430;
        sg = chainSegs(plan, per * (rush ? 0.5 : 1));
      }
      const st = plan[pi], s = sg[pi], clk = ZT.o.clk || null, t = ZT.t, carry = ZT.o.carry || null;
      if (!ZT.o.keepFx) clearFx(); else clearDim();
      if (st.dir < 0) await zoomStep(-1, Z.level === 2 ? minRect(Z.nb, Z.mi) : tileRect(Z.sid), s.ms, s.efn, clk, carry);
      else if (Z.level === 0) { buildShire(t.sid); Z.sid = t.sid; LASTSID = t.sid; await zoomStep(1, tileRect(t.sid), s.ms, s.efn, clk, carry); }
      else { buildMinion(t.sid, t.nb, t.mi); Z.nb = t.nb; Z.mi = t.mi; LASTNB = t.nb; LASTMI = t.mi; await zoomStep(1, minRect(t.nb, t.mi), s.ms, s.efn, clk, carry); }
      pi++;
    }
  } catch (e) { console.error(e); }
  ZT = null; ZW = false;
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
    if (!k || FL.k !== k) return;
    if (done) startFlow(k, FL.i, {still: true, keep: true, done: true});
    else restartStage();
  });
}
/* where the scale control goes: the shire shown, else the one selected, else the last one visited */
/* where the flow is, when a flow is on and its stage is inside a shire */
function flowAim() {
  if (!FL.k || !FL.ctx) return null;
  try { const w = FLOWS[FL.k].stages[FL.i].where(FL.ctx); return w.sid != null && SH[w.sid] ? w : null; } catch (_) { return null; }
}
function aimShire() {
  if (Z.level >= 1) return Z.sid;
  if (SEL && SEL._key === 'cshire') return SEL._ctx.cell.id;
  const w = flowAim(); if (w) return w.sid;
  return LASTSID;
}
function aimMinion(sid) {
  if (Z.level === 2 && Z.sid === sid) return [Z.nb, Z.mi];
  if (SEL && SEL._key === 'minion' && SEL._ctx.mi != null) return [SEL._ctx.nb, SEL._ctx.mi];
  const w = flowAim(); if (w && w.sid === sid && w.level === 2) return [w.nb, w.mi];
  return [LASTNB, LASTMI];
}
function scaleTo(level) {
  if (level <= 0) return userNav({level: 0});
  const sid = aimShire();
  if (level === 1) return userNav({level: 1, sid});
  const [nb, mi] = aimMinion(sid);
  return userNav({level: 2, sid, nb, mi});
}
function scaleUI() {
  const sid = aimShire(), [nb, mi] = aimMinion(sid);
  [0, 1, 2].forEach(l => $('z-' + l).setAttribute('aria-pressed', String(Z.level === l)));
  $('z-1').textContent = `Shire ${sid}`; $('z-1').title = `Shire ${sid} (${Z.level === 1 ? 'shown' : 'zoom in'})`;
  $('z-2').textContent = `Minion ${mi}`; $('z-2').title = `Minion ${mi} of neighbourhood ${nb}, shire ${sid}`;
  $('z-in').disabled = Z.level >= 2; $('z-out').disabled = Z.level <= 0;
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
  return `<p class="pn-what">${lead} <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>.</p>`;
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
  return `<details class="asks"${open === false ? '' : ' open'}><summary>${nOpen ? `Inferred or open here, and what would settle it (${nOpen})` : 'Settled here'}</summary>${as.map(askHtml).join('')}</details>`;
}
/* the panel is not a live region (it holds whole fact lists); a short line announces what it now shows */
function panel(html) {
  hideTip(); const b = $('pn-body'); b.innerHTML = html; b.scrollTop = 0;
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
      act: Z.level === 0 ? `<button type="button" class="st-btn" data-act="zoom" data-sid="${c.id}">Zoom into shire ${c.id}</button><span class="small">or double-click it</span>` : ''};
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
    what: `An ${n('grid86')} grid of ${n('stops')} stops joins the shires. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. It runs at ${n('noc_mhz')} and ${n('noc_v')} on aifoundry2. Routes are shortest paths; whether x or y goes first was not measured. The flows draw every leg, replies included, on its own route: x first on the measured map, and y first where x first would cross an empty corner (some legs from a memory shire).`,
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
      act: at1 && Z.level === 1 ? `<button type="button" class="st-btn" data-act="zoomm" data-nb="${nb}" data-mi="${mi}">Zoom into minion ${mi}</button><span class="small">or double-click it</span>` : ''};
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
    what: `Most of the layout is now fixed by measurement and by the firmware: the measured map of the shires equals the firmware's NoC-spec map once its boot-time renaming is applied (${n('fw_pairs')} pair distances), which also names the four grey cells and agrees with the memory shires' fit. Still inferred: the LPDDR4X pairing (dashed), the die's east-west handedness, the routes' turning order, the inside of a shire, and the sizes. Each item says what would settle it and links to the row that asks for it on the hub, whose list collects everything to ask AI Foundry for.`,
    kpis: [kpi(String(ASKS.filter(a => askState(a) !== 'settled').length), 'open items'), kpi(String(new Set(ASKS.flatMap(a => [a.hub_anchor].concat(a.also || [])).filter(Boolean)).size), 'asks on the hub')],
    act: `<a class="st-btn" href="${HUB}#ask-noc-docs" target="_blank" rel="noopener">The hub's list of asks ↗</a>`,
    all: true}),
};
function showComp(key, ctx) {
  const d = COMPS[key](ctx || {}), ids = COMPF[key] || [];
  panel(`<p class="pn-kick">${esc(d.kick)}</p><p class="pn-title">${esc(d.title)}</p><p class="pn-what">${d.what}</p>`
    + (d.kpis ? `<div class="pn-kpis">${d.kpis.join('')}</div>` : '') + (d.act ? `<div class="pn-act">${d.act}</div>` : '')
    + (d.all ? ASKS.map(askHtml).join('') : asksBlock(key, !TOUR))
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
  if (zoomable && SEL === g) { zoomInto(g); return; }   // a second click zooms in
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
/* while presenting, the stage caption shows no source tooltips (a pointer left on it would cover the die) */
const tipOK = t => !(TOUR && t.closest('#cap, #cap-sub'));
document.addEventListener('pointerover', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t && tipOK(t)) showTip(t); else hideTip(); });
document.addEventListener('focusin', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t) showTip(t); else hideTip(); });
document.addEventListener('focusout', hideTip);
window.addEventListener('scroll', hideTip, {passive: true});

/* ================= drawing a flow ================= */
function packet(fx, col, r) {
  r = r || 11;
  const g = E('g', {class: 'pk'}, fx);
  S(E('circle', {r: r + 8}, g), {fill: col, fillOpacity: 0.28});
  S(E('circle', {r}, g), {fill: col, stroke: 'var(--page)', strokeWidth: 3});
  return g;
}
const at = (g, p) => g.setAttribute('transform', `translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`);
/* move a packet along a polyline with an ease in and out. o.even: the same time for every segment (a mesh hop costs
   the same everywhere), else a steady speed along the length. o.trail: false for none; o.onSeg(i, n) per segment */
async function travel(tok, fx, pk, P, ms, o) {
  o = o || {};
  const trail = o.trail === false ? null : S(E('path', {class: 'trail', fill: 'none'}, fx), {stroke: o.col || 'var(--c2)', strokeWidth: o.w || 7, strokeLinecap: 'round', strokeLinejoin: 'round', strokeOpacity: 0.75, strokeDasharray: o.dash ? '2 13' : null});
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
/* A labelled box. With o.cell it sits beside that tile (o.side 'l' or 'r') in the band below the tiles' id labels,
   so that it covers no tile's number; otherwise it sits on side o.side of (x, y) ('c': centred on it). It goes under
   the packets, and it fades in. */
function callout(fx, x, y, lines, o) {
  o = o || {};
  const g = E('g', {class: 'co'}, fx), fs = o.fs || 24, lh = fs * 1.28, pad = 11;
  const pk1 = [...fx.children].find(c => c.classList && c.classList.contains('pk')); if (pk1) fx.insertBefore(g, pk1);
  const box = S(E('rect', {class: 'co-box', rx: 9}, g), {stroke: o.col || 'var(--c2)'});
  const tx = lines.map((ln, i) => {
    const Lx = typeof ln === 'string' ? {t: ln} : ln, t = T(g, 0, 0, Lx.t, 'co-t' + (i === 0 ? ' b' : ''), 'start', Lx.f);
    t.style.fontSize = fs + 'px'; return t;
  });
  let w = 0; tx.forEach(t => { let tw = 0; try { tw = t.getComputedTextLength(); } catch (_) { /* not rendered */ } w = Math.max(w, tw || t.textContent.length * fs * 0.55); });
  const bw = w + 2 * pad, bh = lines.length * lh + pad;
  let bx = o.side === 'l' ? x - 20 - bw : (o.side === 'u' || o.side === 'd' || o.side === 'c') ? x - bw / 2 : x + 20;
  let by = o.side === 'u' ? y - 20 - bh : o.side === 'd' ? y + 20 : y - bh / 2;
  if (o.cell) {
    const c = o.cell;
    bx = o.side === 'l' ? c.x + 6 - bw : c.x + c.w - 6;
    by = Math.min(c.y + 58, c.y + c.h + 12 - bh);
  }
  bx = Math.max(VB.x + 4, Math.min(VB.x + VB.w - 4 - bw, bx)); by = Math.max(VB.y + 4, Math.min(VB.y + VB.h - 4 - bh, by));
  box.setAttribute('x', bx); box.setAttribute('y', by); box.setAttribute('width', bw); box.setAttribute('height', bh);
  tx.forEach((t, i) => { t.setAttribute('x', bx + pad); t.setAttribute('y', by + pad / 2 + (i + 1) * lh - lh * 0.24); });
  return fadeIn(g);
}
function pulse(tok, fx, p, ms, col, r1) {
  if (REDUCED || tok.ff) return wait(tok, tok.ff ? 0 : Math.min(ms, 600));
  const c = S(E('circle', {cx: p.x, cy: p.y, r: 8}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 5});
  return anim(tok, ms, q => { const e = easeS(q); c.setAttribute('r', 8 + (r1 || 46) * e); c.style.strokeOpacity = 1 - e * 0.85; }).then(() => c.remove(), e => { c.remove(); throw e; });
}
function ring(tok, fx, p, ms, col, label) {
  const R = 40, C = 2 * Math.PI * R;
  const bg = S(E('circle', {cx: p.x, cy: p.y, r: R}, fx), {fill: 'var(--surface)', fillOpacity: 0.85, stroke: 'var(--grid)', strokeWidth: 8});
  const c = S(E('circle', {cx: p.x, cy: p.y, r: R, transform: `rotate(-90 ${p.x} ${p.y})`}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 8, strokeDasharray: `0 ${C}`});
  const t = label ? T(fx, p.x, p.y + 8, label, 't-labb', 'middle') : null;
  return anim(tok, ms, q => { c.style.strokeDasharray = `${C * easeS(q)} ${C}`; }).then(() => [bg, c, t]);
}
function clearDim() {
  svg.classList.remove('dimming', 'fdim'); svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi'));
  if (PIP.svg) PIP.svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi'));
  if (SEL) SEL._hiSel = false;
}
function clearFx() { FX.forEach(f => { if (f) f.textContent = ''; }); if (PIP.fx) PIP.fx.textContent = ''; clearDim(); }
function hiCells(cells, dimOthers) {
  cells.forEach(c => { if (!c) return; if (c.g) c.g.classList.add('hi'); const t = PIP.tiles[c.r + ',' + c.c]; if (t) t.classList.add('hi'); });
  if (dimOthers) svg.classList.add('fdim');
}
/* bars on the stage, in the free band right of the die, with 19-20 unit text */
const BAND = {x: 932, y: 40, w: 172};
function bandChart(fx, title, rows, o) {
  o = o || {};
  const g = E('g', {class: 'band'}, fx);
  let y = o.y == null ? BAND.y : o.y;
  if (title) { T(g, BAND.x, y + 22, title, 't-labb halo'); y += 30; }
  if (o.note) { T(g, BAND.x, y + 18, o.note, 't-sm halo'); y += 26; }
  if (o.note2) { T(g, BAND.x, y + 18, o.note2, 't-sm halo'); y += 26; }
  const out = rows.map(r => {
    T(g, BAND.x, y + 20, r.name, 't-lab halo', 'start', r.f).style.fontSize = '19px';
    S(E('rect', {x: BAND.x, y: y + 27, width: BAND.w, height: 30, rx: 5}, g), {fill: 'var(--grid)'});
    const bar = S(E('rect', {x: BAND.x, y: y + 27, width: 0, height: 30, rx: 5}, g), {fill: `color-mix(in srgb, ${r.col || 'var(--c2)'} 55%, transparent)`});
    const val = T(g, BAND.x + 7, y + 49, r.val || '', 't-labb', 'start', r.f);
    const row = {bar, val, y: y + 27, set: q => bar.setAttribute('width', (Math.max(0, Math.min(1, q)) * BAND.w).toFixed(1))};
    y += 68;
    return row;
  });
  fadeIn(g);
  return {g, rows: out, bottom: y};
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
  const e = S(E('path', {d, fill: 'none'}, fx), {stroke: col, strokeWidth: 9, strokeOpacity: 0.35, strokeLinecap: 'round', strokeLinejoin: 'round', strokeDasharray: dash ? '3 14' : null});
  fx.insertBefore(e, fx.firstChild);
  return e;
}
/* a translucent glow over each compute tile, pulsing on the clock with amplitude amp (0 to 1) */
function glowTiles(tok, fx, amp, col, shires) {
  const gs = (shires || Object.values(SH)).map(c => S(E('rect', {x: c.x + INS + 4, y: c.y + INS + 4, width: c.w - 2 * INS - 8, height: c.h - 2 * INS - 8, rx: 8}, fx), {fill: col || 'var(--c2)', fillOpacity: 0}));
  fx.querySelectorAll('.pk').forEach(p => fx.appendChild(p));
  const st = {amp};
  // with reduced motion the glow holds still: the amplitude still follows st.amp, nothing oscillates
  const draw = t => gs.forEach((r, i) => { r.style.fillOpacity = (st.amp * (0.32 + (REDUCED ? 0 : 0.22 * Math.sin(t / 260 + i * 1.7)))).toFixed(3); });
  if (REDUCED || tok.ff) draw(0);
  every(tok, draw);
  return st;
}

/* ================= flows: each a list of stages ================= */
const ST = {rq: 0, pa: null, gs: 'g', sid: 13};
const P40 = 2 ** 32;
function mkPA(home, salt) { return 0x80 * P40 + salt * 2048 + home * 64; }   // a DRAM line (region 0x80_0000_0000) homed in L3 slice `home`
ST.pa = mkPA(13, 0x2468A);
function decode(pa) {
  const b = k => Math.floor(pa / 2 ** k);
  return {bank: b(6) % 4, home: b(6) % 32, ms: b(6) % 8, ch: b(9) % 2, db: b(10) % 8, row: b(18)};
}
function hex(pa) { const s = pa.toString(16).padStart(10, '0'); return '0x' + s.slice(0, 2) + '_' + s.slice(2, 6) + '_' + s.slice(6); }
const hopw = h => h === 1 ? 'hop' : 'hops';
const FLOWS = {}, ORDER = 'ABCDEFGHIJ', KEYOF = {A: '1', B: '2', C: '3', D: '4', E: '5', F: '6', G: '7', H: '8', I: '9', J: '0'};
const FL = {k: null, i: 0, tok: {dead: true}, ctx: null, done: false, still: false};
let FOLLOW = true, FOLLOW_AUTO = false, LASTFLOW = null, CAPFLOW = false;
const flowOn = () => !!FL.k && !FL.done;
const HOLD = 2300, HOP_MS = 650;
function atView(w) {
  if (ZW || Z.level !== w.level) return false;
  if (w.level === 0) return true;
  return Z.sid === w.sid && (w.level === 1 || (Z.nb === w.nb && Z.mi === w.mi));
}
/* the flow's camera: on the animation clock, so that Space stops it too; a cut when drawing an end state */
async function cam(tok, w, cut) {
  if (!FOLLOW || atView(w)) return;
  await goTo(w, {clk: tok, keepFx: true, ms: (cut || tok.ff) ? 0 : undefined, carry: FL.ctx && FL.ctx.tok === tok ? FL.ctx.pk : null});
  alive(tok);
}
function pipOn() { PIP.el.hidden = false; $('pip-cap').textContent = `Flow ${ORDER.indexOf(FL.k) + 1}, stage ${FL.i + 1}, on the die · click for the chip`; }
function pipOff() { PIP.el.hidden = true; }
/* the flow's packet, in this drawing: the one it has if it is already here, else a new one at p */
function pkIn(c, fx, p, col, r) {
  if (!c.pk || c.pk.parentNode !== fx) { c.pk = packet(fx, col || 'var(--c2)', r || 12); if (p) at(c.pk, p); }
  return c.pk;
}
function sayAt(c, fx, x, y, lines, o) { unsay(c); c.co = callout(fx, x, y, lines, o); return c.co; }
function unsay(c) { if (c.co) { c.co.remove(); c.co = null; } }
function startFlow(k, i, o) {
  o = o || {};
  const def = FLOWS[k]; i = Math.max(0, Math.min(def.stages.length - 1, i || 0));
  const prev = (o.keep && FL.ctx && FL.ctx.k === k) ? FL.ctx.pick : null;
  FL.tok.dead = true; clearFx(); pipOff();
  const tok = {dead: false, k, ff: false, endDone: !!o.done};
  Object.assign(FL, {k, i, tok, done: false, still: !!o.still});
  LASTFLOW = k;
  if (!o.still) CLK.on = true;
  document.querySelectorAll('[data-flow]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.flow === k)));
  const ctx = FL.ctx = {k, tok, pick: prev || (def.pick ? def.pick() : {})};
  def.setup(ctx);
  if (!TOUR) { setKick(`Flow ${KEYOF[k]} · ${def.title}`); setCap(def.cap()); dots(-1); CAPFLOW = true; }
  renderBar(); playBtn();
  quiet(runFrom(tok, ctx, i, !!o.still, !!o.intro));
}
async function runFrom(tok, ctx, i, still, intro) {
  const sts = FLOWS[ctx.k].stages, w = sts[i].where(ctx);
  // the stage bar, the sub-caption and the legs table show the stage at once, before the camera moves to it
  showStage(ctx, i);
  // an establishing shot: a flow that starts inside a shire or a minion first shows where it is on the die
  if (intro && FOLLOW && i === 0 && w.level > 0 && !still && !REDUCED && !(Z.level === 0 && !ZW)) {
    await cam(tok, {level: 0});
  }
  if (intro && FOLLOW && i === 0 && w.level > 0 && !still && !REDUCED && Z.level === 0) {
    hiCells([SH[w.sid]], true);
    const p = {x: SH[w.sid].sx, y: SH[w.sid].sy};
    await pulse(tok, FX[0], p, 1100, 'var(--c2)', 60);
    clearDim();
  }
  if (FOLLOW) await cam(tok, w, still);
  // the stages before i: their end states, drawn at once where the camera can show them
  tok.ff = true;
  for (let j = 0; j < i; j++) {
    const sj = sts[j], wj = sj.where(ctx);
    ctx.stage = j;
    if (atView(wj)) { ctx.fx = FX[wj.level]; ctx.pip = false; await sj.run(tok, ctx); }
    else if (wj.level === 0) { ctx.fx = PIP.fx; ctx.pip = true; await sj.run(tok, ctx); }
  }
  tok.ff = false;
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
/* stage j is now the flow's: the bar marks it, the sub-caption says it, the legs table lights its row, and a screen
   reader hears its name */
function showStage(ctx, j) {
  const sts = FLOWS[ctx.k].stages;
  FL.i = j; renderBar(); sub(sts[j].say ? sts[j].say(ctx) : ''); leg(j);
  $('st-live').textContent = `Stage ${j + 1} of ${sts.length}: ${sts[j].name}`;
}
async function playStage(tok, ctx, j) {
  const st = FLOWS[ctx.k].stages[j], w = st.where(ctx);
  ctx.stage = j; leg(j);
  if (FOLLOW) await cam(tok, w);
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
function killFlow() { FL.tok.dead = true; clearFx(); pipOff(); }
function stopFlow(keepCap) {
  killFlow(); FL.k = null; FL.done = false; FL.still = false;
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
function sub(html) { $('cap-sub').innerHTML = html; }
const legRows = rows => `<table class="legs"><thead><tr><th>Leg</th><th>What happens</th><th class="num">cycles</th><th class="num">pJ/B</th></tr></thead><tbody>${rows.map((r, i) => `<tr class="todo" data-leg="${i}"><td>${r[0]}</td><td>${r[1]}</td><td class="num">${r[2] || ''}</td><td class="num">${r[3] || ''}</td></tr>`).join('')}</tbody></table>`;
function leg(i) {
  let on = null;
  document.querySelectorAll('#pn-body tr[data-leg]').forEach(tr => { const k = +tr.dataset.leg; tr.className = k < i ? '' : k === i ? 'on' : 'todo'; if (k === i) on = tr; });
  if (on) pnReveal(on);
}
function flowPanel(k, head, body) {
  panel(`<p class="pn-kick">Flow ${ORDER.indexOf(k) + 1} of ${ORDER.length} · key ${KEYOF[k]}</p><p class="pn-title">${esc(head)}</p>${body}`
    + asksBlock('flow:' + k, !TOUR) + topPage(COMPF['flow' + k]) + factsBlock('flow' + k, 'The facts this flow uses'));
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
        [`back to shire ${rq}`, `the model's total; the data comes back through the L3 home, ${src('as the shire cache specification has it', 'sc.l3-miss')}, each leg drawn x first; a typical measured load takes ${n('lat_dram')}`, cn(tot, 'addr.load-model L45', 0), ''],
      ]));
  },
  stages: [
    {name: 'L1 miss', where: c => ({level: 2, sid: c.rq, nb: c.nb, mi: c.mi}),
      mark: () => [{t: `L1: miss (a hit: ${N.lat_l1.t} cycles)`, f: 'lat-l1'}],
      say: c => `Leg 1 of 6 · hart 0 of minion ${c.mi} looks in its L1 data cache: a miss (a hit takes ${n('lat_l1')} cycles)`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, pk = pkIn(c, fx, P2.hart0);
        at(pk, P2.hart0);
        const gx = MF.x + 354, gy = MF.y + 545;   // the gap right of the harts, then along the L1's top edge
        await travel(tok, fx, pk, [P2.hart0, {x: gx, y: P2.hart0.y}, {x: gx, y: gy}, {x: P2.l1h0.x, y: gy}, P2.l1h0], 1700);
        const sb = P2.scpBox;   // over the tensor-scratchpad sets, which a load does not use: no label is covered
        sayAt(c, fx, sb.x + sb.w / 2, sb.y + sb.h / 2, [{t: 'L1: miss'}, {t: `a hit takes ${N.lat_l1.t} cycles`, f: 'lat-l1'}], {side: 'c', fs: 21});
        await wait(tok, 2300);
        await travel(tok, fx, pk, [P2.l1h0, {x: P2.etl.x, y: P2.l1h0.y}, P2.etl], 1400);
        c.last = {level: 2, p: P2.etl};
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
        const pk = pkIn(c, fx, s0, 'var(--c2)', 13);
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
        const pk = pkIn(c, fx, {x: c.hc.sx, y: c.hc.sy}, 'var(--c2)', 13);
        const P = pts(c.r2);
        await travel(tok, fx, pk, P, HOP_MS * Math.max(1, c.h2), {even: true, onSeg: hopper(c, fx, P)});
        hopClear(c);
        sayAt(c, fx, c.mc.sx, c.mc.sy, [{t: `Memory shire ${c.a.ms}`}, {t: `+ ${N.lat_ms_a.t} + ${N.lat_ms_b.t} × ${c.h2}`, f: 'dram.leg'}], {cell: c.mc, side: c.mc.c === 0 ? 'r' : 'l', fs: 21});
      }},
    {name: 'DRAM', where: () => ({level: 0}),
      say: c => `Leg 5 of 6 · channel ${c.a.ch} (PA[9]), bank ${c.a.db} (PA[12:10]): ${n('lat_dram_chip')} cycles of the load are the DRAM chip itself`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.rc, c.hc, c.mc], true); unsay(c);
        const pc = AP[0].pkg[c.a.ms + ':' + c.a.ch], pk = pkIn(c, fx, {x: c.mc.sx, y: c.mc.sy}, 'var(--c2)', 13);
        await travel(tok, fx, pk, [{x: c.mc.sx, y: c.mc.sy}, {x: c.mc.sx, y: pc.y}, pc], 1400);
        sayAt(c, fx, pc.x, pc.y, [{t: `channel ${c.a.ch}, bank ${c.a.db}`}, {t: `${N.lat_dram_chip.t} cycles in DRAM`, f: 'lat-dram-chip'}], {side: 'd', fs: 22});
      }},
    {name: 'Back', where: () => ({level: 0}),
      say: c => `Leg 6 of 6 · back to shire ${c.rq} through the L3 home: ${cn(c.tot, 'addr.load-model L45', 0)} cycles (${cn(ns(c.tot), 'addr.load-model op-600', 0)} ns) by the model; a typical measured DRAM load takes ${n('lat_dram')} (${n('lat_dram_ns')})`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.rc, c.hc, c.mc], true); unsay(c);
        const pc = AP[0].pkg[c.a.ms + ':' + c.a.ch], pk = pkIn(c, fx, pc, 'var(--c2)', 13);
        const back = [pc, {x: c.mc.sx, y: pc.y}].concat(pts(via(c.mc, c.hc, c.rc)));
        await travel(tok, fx, pk, back, HOP_MS * (c.h1 + c.h2 + 1), {col: 'var(--c7)', even: true});   // a reply: its colour, not a dash
        sayAt(c, fx, c.rc.sx, c.rc.sy, [{t: `${fnum(c.tot)} cycles, by the model`, f: 'addr.load-model'}, {t: `${N.lat_dram.t} typical, measured`, f: 'lat-dram-typical'}], {cell: c.rc, side: side(c.rc), fs: 21});
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
      {nm: `scratchpad, shire ${a.home}`, sn: `scratchpad ${a.home}`, cyc: rs, lab: `${cn(rs, 'lat-scp-remote', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(rs)} · ${h1} ${hopw(h1)}`, tn: `another shire's scratchpad, ${rsHop}`, e: `${n('e_rs0')}–${n('e_rs1')}`, bw: n('bw_rs', 'TB/s'), back: route(hc, rc), path: r1, say: `Shire ${a.home}'s scratchpad, ${h1} ${hopw(h1)}: ${n('lat_rs_a')} + ${n('lat_rs_b')} × ${h1} = ${cn(rs, 'lat-scp-remote', 0)} cycles`},
      {nm: `L3, home ${a.home}`, sn: `L3, home ${a.home}`, cyc: l3, lab: `${cn(l3, 'l3.latency', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(l3)} · ${h1} ${hopw(h1)}`, e: `${n('e_l3')} (${n('e_l3_rng')})`, bw: n('bw_l3', 'TB/s'), back: route(hc, rc), path: r1, say: `L3 hit in home shire ${a.home}, ${h1} ${hopw(h1)}: ${n('lat_l3_a')} + ${n('l3_b12')} × ${h1} = ${cn(l3, 'l3.latency', 0)} cycles (${n('lat_l3_avg')} averaged over slices)`},
      {nm: 'DRAM', sn: `DRAM, ${N.lat_dram.t} typical`, cyc: dram, lab: `${cn(dram, 'addr.load-model', 0)} model · ${n('lat_dram')} typ.`, sv: `${fnum(dram)} model`, e: `${n('e_dram')} (${n('e_dram_rng')})`, bw: n('dram_bw', 'GB/s'), path: r1.concat(r2.slice(1)), back: via(mc, hc, rc), dram: true, say: `DRAM through memory shire ${a.ms}: ${cn(dram, 'addr.load-model', 0)} cycles by the model; a typical load takes ${n('lat_dram')}: ${cn(V('lat_dram') / V('lat_l1'), 'lat-l1 lat-dram-typical', 0)}× an L1 hit`},
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
      hiCells([c.rc, c.hc, c.mc], true);
      if (i === 0) pnReveal($('lad'));
      if (!c.ch || c.ch.g.parentNode !== fx) c.ch = bandChart(fx, 'Latency, cycles', c.LV.map(v => ({name: v.sn, val: v.sv, f: 'lat-l1 lat-l2 l3.latency addr.load-model lat-scp-remote'})));
      fx.querySelectorAll(':scope > path.trail').forEach(p => p.remove());
      const trk = document.querySelector(`#lad .tr[data-i="${i}"]`), bar = trk && trk.querySelector('u');
      const dur = Math.max(1300, l.cyc * 17);
      const grow = anim(tok, dur, q => { const e = easeS(q); if (bar) bar.style.width = (100 * e * l.cyc / c.max).toFixed(2) + '%'; c.ch.rows[i].set(e * l.cyc / c.max); });
      if (!l.path) await Promise.all([grow, pulse(tok, fx, {x: c.rc.sx, y: c.rc.sy}, Math.max(dur, 900), 'var(--c2)', 20 + 30 * l.cyc / 47)]);
      else {
        const out = pts(l.path).concat(l.dram ? [{x: c.mc.sx, y: c.pkg.y}, c.pkg, {x: c.mc.sx, y: c.pkg.y}] : []), ret = pts(l.back).slice(1);
        const pk = packet(fx, 'var(--c2)', 11);
        await Promise.all([grow, travel(tok, fx, pk, out.concat(ret), dur, {w: 5, even: true})]);
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
      + `<p class="pn-what">Inside a shire the same round trip is ${n('ts_fln')} on a tree edge and ${n('ts_xbar')} cycles otherwise. The reply takes its own route, x first.</p>`);
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
      await travel(tok, fx, pk, pts(route(B, A)), Math.max(1000, 480 * h), {col: 'var(--c7)', even: true});
      callout(fx, B.sx, B.sy, [{t: `${fnum(cyc)} cycles round trip`, f: 'ts-rt-mesh'}, {t: `${h} ${hopw(h)}, ${fnum(ns(cyc))} ns`, f: 'ts-rt-mesh op-600'}], {cell: B, side: B.c <= 3 ? 'r' : 'l', fs: 21});
    }})),
};

/* ---- 4. the relay: hand a slab to the next shire, or round-trip it through DRAM. One line of the slab is drawn on
   its DRAM path, through its L3 home (shire 16) and memory shire 0, as a load goes (fact addr.load-path) ---- */
FLOWS.D = {
  title: 'Relay',
  cap: () => CAPS.D(),
  setup(c) {
    const A = SH[0], B = SH[1], HOME = SH[16], mc = MSC[16 % 8], pkg = AP[0].pkg[mc.id + ':0'];
    const directC = route(A, B), h = directC.length - 1;
    const bars = [['through DRAM', 'rl_e_dram', 'rl_bw_dram', 'var(--c2)'], ['to the next shire', 'rl_e_next', 'rl_bw_next', 'var(--c3)'], ['in the own scratchpad', 'rl_e_own', 'rl_bw_own', 'var(--c1)']];
    Object.assign(c, {A, B, HOME, mc, pkg, h, direct: pts(directC), bars, emax: V('rl_e_dram'), bmax: V('rl_bw_own'),
      loop: pts(via(A, HOME, mc)).concat([{x: mc.sx, y: pkg.y}, pkg, {x: mc.sx, y: pkg.y}]).concat(pts(via(mc, HOME, B)))});
    flowPanel('D', 'The relay: next shire or DRAM',
      `<p class="pn-what">A pipeline stage hands its output to the next stage. Through DRAM it writes the slab out and the next shire reads it back, each line through its L3 home and memory shire (one line is drawn, homed in ${src('shire 16, served by memory shire 0', 'l3.home L43 addr.load-path')}); on chip it writes straight into the next shire's scratchpad (shire 0 to shire 1 here, ${cn(h, 'mesh.logical-map', 0)} ${hopw(h)}).</p>`
      + `<p class="pn-h">Energy per byte (write + read)</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[1]) / c.emax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[1], 'pJ/B')}</s></div>`).join('')}</div>`
      + `<p class="pn-h">Bandwidth, ${n('rl_stages')} on ${n('n1024')} minions</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[2]) / c.bmax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[2], 'GB/s')}</s></div>`).join('')}</div>`
      + `<p class="pn-what">Next shire against DRAM: ${n('rl_x')} less energy per byte on the three cards, and ${n('rl_speed')} the bandwidth. The dots on the die are drawn at those relative rates.</p>`);
  },
  stages: [
    {name: 'Two ways', where: () => ({level: 0}),
      say: () => `Two ways to hand a slab to the next shire: straight into its scratchpad, or out to DRAM and back`,
      run: async (tok, c) => { relayDraw(c); await wait(tok, 900); }},
    {name: 'Through DRAM', where: () => ({level: 0}), hold: 0,
      say: () => `Through DRAM: ${n('rl_e_dram')} pJ/B at ${n('rl_bw_dram')} GB/s, every line to its L3 home and memory shire and back`,
      run: async (tok, c) => { relayDraw(c); relayStream(tok, c, 'dram'); await wait(tok, 7000); }},
    {name: 'To the next shire', where: () => ({level: 0}), hold: 0,
      say: () => `To the next shire: ${n('rl_e_next')} pJ/B at ${n('rl_bw_next')} GB/s, straight into its scratchpad`,
      run: async (tok, c) => { relayDraw(c); relayStream(tok, c, 'next'); await wait(tok, 7000); }},
    {name: 'Side by side', where: () => ({level: 0}),
      say: () => `Next shire: ${n('rl_e_next')} pJ/B at ${n('rl_bw_next')} GB/s · through DRAM: ${n('rl_e_dram')} pJ/B at ${n('rl_bw_dram')} GB/s · ${n('rl_13th')} of the energy`,
      run: async (tok, c) => { relayDraw(c); relayStream(tok, c, 'both'); await wait(tok, 1e12); }},
  ],
};
function relayDraw(c) {
  const fx = c.fx;
  hiCells([c.A, c.B, c.HOME, c.mc], true);
  if (c.drawn && c.drawn.parentNode === fx) return;
  const g = c.drawn = E('g', {}, fx);
  pipe(g, c.direct, 'var(--c3)'); pipe(g, c.loop, 'var(--c2)');
  callout(g, c.B.sx, c.B.sy, [{t: 'next shire'}, {t: `${N.rl_e_next.t} pJ/B`, f: 'relay-energy'}], {cell: c.B, side: 'r', col: 'var(--c3)', fs: 21});
  callout(g, c.HOME.sx, c.HOME.sy, [{t: 'through DRAM'}, {t: `${N.rl_e_dram.t} pJ/B`, f: 'relay-energy'}], {cell: c.HOME, side: 'r', col: 'var(--c2)', fs: 21});
  const ce = bandChart(g, 'pJ per byte', c.bars.map(b => ({name: b[0].replace('in the own', 'own'), val: N[b[1]].t, col: b[3], f: 'relay-energy'})));
  const cb = bandChart(g, 'GB/s', c.bars.map(b => ({name: b[0].replace('in the own', 'own'), val: N[b[2]].t, col: b[3], f: 'relay-bw'})), {y: ce.bottom + 14});
  c.bars.forEach((b, i) => { ce.rows[i].set(V(b[1]) / c.emax); cb.rows[i].set(V(b[2]) / c.bmax); });
}
function relayStream(tok, c, which) {
  if (REDUCED) return;
  c.streams = c.streams || {};
  Object.values(c.streams).forEach(s => { s.stop = true; });
  const EMIT = 380, SLOW = V('rl_bw_next') / V('rl_bw_dram'), fx = c.fx, t0 = CLK.t, st = {stop: false};
  c.streams[which] = st;
  const shoot = (P, col, ms) => { const pk = packet(fx, col, 12); quiet(travel(tok, fx, pk, P, ms, {trail: false, linear: true}).then(() => pk.remove(), e => { pk.remove(); throw e; })); };
  let nextD = 0, nextM = 0;
  every(tok, t => {
    if (st.stop) return;
    const dt = t - t0;
    if (which !== 'dram') while (nextD <= dt) { shoot(c.direct, 'var(--c3)', 260 * c.h); nextD += EMIT; }
    if (which !== 'next') while (nextM <= dt) { shoot(c.loop, 'var(--c2)', 190 * (c.loop.length - 1)); nextM += EMIT * SLOW; }
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
      `<p class="pn-what">Both harts of ${n('n1024')} minions run the ${n('gs_8')} (${g ? 'fgw.ps' : 'its scatter twin, fscw.ps'}) on scattered lines of a table that fits one level: ${src('each visit\'s 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order', 'gs-g-dram-256K gs-s-dram-256K')}. The bars run at the measured cycles per instruction and count the instructions each lane has done.</p>`
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
    c.ch = bandChart(fx, g ? 'Gathers done' : 'Scatters done', c.LN.map(l => ({name: SN[l.k], val: '', f: key})), {note: 'count · cycles each'});
    c.ch.rows.forEach((r, j) => { const y = +r.val.getAttribute('y'); T(c.ch.g, BAND.x + BAND.w - 7, y, N[c.p + c.LN[j].k + '_c'].t, 't-sm halo', 'end', 'gs-' + (g ? 'g' : 's') + '-dram-256K').style.fontSize = '18px'; });
    callout(fx, c.rq.x + INS, c.rq.y + 30, [{t: `shire 0 ${g ? 'gathers' : 'scatters'}`}, {t: `L1: ${N[c.p + 'l1_r'].t} G el./s`, f: key}], {side: 'l', fs: 21});   // left of shire 0: the die's empty corner and the margin
    c.trs = c.LN.map((l, j) => document.querySelector(`#race .tr[data-i="${j}"]`));
    c.toRq = g ? pts(route(c.far, c.rq)) : pts(route(c.rq, c.far));
    pnReveal($('race'));
    every(tok, t => {
      Object.keys(c.lanes).forEach(jj => {
        const j = +jj, l = c.LN[j], tr = c.trs[j];
        if (c.lanes[j] === null && CLK.on && !REDUCED) c.lanes[j] = t;   // drawn while paused: it starts with the clock
        const still = REDUCED || c.lanes[j] === null;
        const dur = l.c * c.SCALE, dt = still ? 0 : t - c.lanes[j], done = Math.floor(dt / dur), fr = (dt % dur) / dur;
        c.ch.rows[j].set(still ? 1 : fr); c.ch.rows[j].val.textContent = still ? '' : fnum(done, 0);
        if (tr) { tr.querySelector('u').style.width = (100 * (still ? 1 : fr)).toFixed(1) + '%'; tr.querySelector('s').textContent = still ? `${N[c.p + l.k + '_c'].t} cycles each` : `${fnum(done, 0)} done`; }
      });
    });
  }
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
    every(tok, t => { while (nx <= t - t0) { const home = Math.floor(Math.random() * 32), hc = SH[home], mc = MSC[home % 8]; shoot(pts(g ? via(mc, hc, c.rq) : via(c.rq, hc, mc)), 'var(--c2)'); nx += d; } });
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
        ['into DRAM', `lines rotate over the ${n('ms8')} memory shires (PA[8:6]); the path from the PCIe shire is not established`, '', ''],
        ['launch', `an empty kernel on ${n('cshires')} shires: ${n('pcie_b2b', 'µs')} each when queued, the card's own cost; one launch waited for takes ${n('pcie_launch', 'µs')}, the extra ${n('pcie_wait_rng')} mostly the runtime's ${n('poll500')} idle poll`, '', ''],
        ['small copies', `a lone 4 KB copy: ${n('pcie_4k', 'µs')}, the runtime's polling (${n('poll50')} in flight, ${n('poll500')} idle)`, '', ''],
      ]).replace('<th class="num">cycles</th><th class="num">pJ/B</th>', '<th class="num"></th><th class="num"></th>')
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
        sayAt(c, fx, hb.x + hb.w / 2, hb.y + hb.h, [{t: 'memcpy, then DMA'}, {t: `memcpy ${N.pcie_memcpy.t} GB/s`, f: 'pcie.staged'}], {side: 'd', col: 'var(--c4)', fs: 20});
        hostStream(tok, c, 'var(--c4)', 560, true);
        await wait(tok, 7000);
      }},
    {name: 'Into DRAM', where: () => ({level: 0}),
      say: () => `Buffers go to device DRAM: lines rotate over the ${n('ms8')} memory shires by PA[8:6]; the path from the PCIe shire is not established (drawn dashed)`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(MSC).concat([c.pc]), true); unsay(c);
        if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
        const legs1 = [];
        for (let m = 0; m < 8; m++) {
          const mc = MSC[m], pkg = AP[0].pkg[m + ':' + (m % 2)], pk = packet(fx, 'var(--c3)', 10);
          legs1.push(quiet(travel(tok, fx, pk, pts(route(c.pc, mc)).concat([{x: mc.sx, y: pkg.y}, pkg]), 2600, {col: 'var(--c3)', w: 5, dash: true})));
          await wait(tok, 200);
        }
        await Promise.all(legs1);
      }},
    {name: 'Launch', where: () => ({level: 0}),
      say: () => `The launch goes to the master shire (${n('master_id')}), whose firmware starts the ${n('cshires')} compute shires: queued, an empty kernel costs the card ${n('pcie_b2b_rng')}; waited for, ${n('pcie_launch_rng')}, most of it the host's ${n('poll500')} idle poll`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.master, c.pc], true); unsay(c);
        await travel(tok, fx, packet(fx, 'var(--c7)', 12), AP[0].host.slice(0, 2).concat(pts(route(c.pc, c.master))), 2200, {col: 'var(--c7)'});
        hiCells(Object.values(SH));
        const ps = Object.values(SH).map(x => pulse(tok, fx, {x: x.sx, y: x.sy}, 1500, 'var(--c1)', 40));
        await Promise.all(ps);
        if (c.ch && c.ch.g.parentNode) c.ch.g.remove();
        c.bt = bandText(fx, 'An empty kernel', [{t: 'queued, each:'}, {t: N.pcie_b2b_rng.t, b: 1, f: 'pcie.launch'}, {t: "the card's own cost"}, {t: 'one, waited for:'}, {t: N.pcie_launch_rng.t, b: 1, f: 'pcie.launch'}, {t: 'mostly host polling', f: 'pcie.poll'}], 90);
      }},
    {name: 'Small copies', where: () => ({level: 0}),
      say: () => `A lone 4 KB copy takes ${n('pcie_4k', 'µs')}: the runtime's thread polls for completions every ${n('poll50')} while commands are in flight and every ${n('poll500')} when none are, so small copies wait on the host, not the link`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.pc], true); unsay(c);
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
async function streamRows(tok, c, fx, from, dest, ms, col, fill) {
  const ps = [];
  for (let r = 0; r < 16; r++) {
    const pk = packet(fx, col, 6), to = dest(r);
    const p = travel(tok, fx, pk, [from, to], ms, {trail: false}).then(() => { pk.remove(); fill(r); }, e => { pk.remove(); throw e; });
    p.catch(() => {});   // handled: a stage cancelled mid-loop leaves the rows already sent without a waiter
    ps.push(p);
    await wait(tok, 110);
  }
  await Promise.all(ps);
}
/* a note in the minion view, over hart 1's register grid (hart 1 issues no tensor instruction in flows 7 and 8): it
   covers no title or label */
const NOTE_AT = () => ({x: MF.x + 184, y: MF.y + 452});
function note(c, fx, lines, col) {
  if (c.cnt && c.cnt.parentNode) c.cnt.remove();
  const p = NOTE_AT();
  c.cnt = callout(fx, p.x, p.y, lines, {side: 'c', fs: 19, col: col || 'var(--c7)'});
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
        ['TensorLoad A', `16 lines from the L2: ${n('tl_l2')} cycles (three cards)`, n('tl_l2'), ''],
        ['B through TenB', 'streamed with a paired load, into TenB', '', ''],
        ['TensorFMA', `with B in TenB: ${n('tfma_tenb')} cycles (${n('tfma546')} with B in the L1 scratchpad)`, n('tfma_tenb'), ''],
        ['the next A', `loaded during the FMA: ${n('mm_op')} cycles per op, no more than the FMA`, n('mm_op'), ''],
        ['32 minions', `every minion of the shire, from its L2; all ${n('n1024')} loading: ${n('tl_all_l2')} cycles per load`, '', ''],
        ['1,024 minions', `${n('tflops')} TFLOP/s fp32, against a peak of ${n('peak_tf32')}`, '', ''],
        ['fed from DRAM', `tiles in DRAM: ${n('mm_dram_tf')} TFLOP/s; a 16-line load with all minions loading: ${n('tl_all_dr')} cycles`, n('mm_dram_op'), ''],
      ]).replace('<th class="num">pJ/B</th>', '<th class="num"></th>')
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
        await streamRows(tok, c, fx, P2.etl, r => sl.at(r), 1200, 'var(--c7)', r => { sl.cells[r].style.fillOpacity = 0.75; });
        note(c, fx, [{t: 'A in the L1 scratchpad'}, {t: `${N.tl_l2.t} cycles from the L2`, f: 'tl.one'}]);
      }},
    {name: 'B via TenB', where: c => ({level: 2, sid: c.sid, nb: c.nb, mi: c.mi}),
      mark: () => [{t: 'B streams through TenB'}],
      say: () => `A paired TensorLoad streams the 16 rows of B into TenB, next to the lanes; the benchmark does this for every op`,
      run: async (tok, c) => {
        const P2 = AP[2], fx = c.fx, tb = P2.tenb, sl = scpSlots(c, fx); sl.cells.slice(0, 16).forEach(r => { r.style.fillOpacity = 0.75; });
        const rx0 = tb.x + tb.w - 64, cw = 14, rh = 17, cell = r => ({x: rx0 + (r % 4) * cw, y: tb.y + 8 + Math.floor(r / 4) * rh});   // a 4 x 4 block right of TenB's labels
        if (!c.tbRows || c.tbRows[0].parentNode !== fx) c.tbRows = Array.from({length: 16}, (_, r) => S(E('rect', {x: cell(r).x, y: cell(r).y, width: cw - 3, height: rh - 3, rx: 2}, fx), {fill: 'var(--c2)', fillOpacity: 0}));
        note(c, fx, [{t: 'B: 16 rows through TenB'}]);
        await streamRows(tok, c, fx, P2.etl, r => ({x: cell(r).x + cw / 2, y: cell(r).y + rh / 2}), 1100, 'var(--c2)', r => { c.tbRows[r].style.fillOpacity = 0.8; });
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
        await Promise.all([flashLanes(tok, 4600, [0]), streamRows(tok, c, fx, P2.etl, r => sl.at(16 + r), 1200, 'var(--c7)', r => { sl.cells[16 + r].style.fillOpacity = 0.45; })]);
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
        sayAt(c, fx, SF.x + SF.w, SF.y + 250, [{t: '32 minions, each its own tiles'}, {t: `all 1,024 loading: ${N.tl_all_l2.t} cycles`, f: 'tl.all'}, {t: 'per 16-line load from the L2'}], {side: 'r', fs: 20});
      }},
    {name: '1,024 minions', where: () => ({level: 0}),
      say: () => `All ${n('n1024')} minions: ${n('tflops')} TFLOP/s fp32 on all three cards, against a peak of ${n('peak_tf32')} at ${n('mhz')}`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        glowTiles(tok, fx, 1, 'var(--c2)');
        await wait(tok, 900);
        callout(fx, DW / 2, DH / 2, [{t: `${N.tflops.t} TFLOP/s fp32`, f: 'mm-rate'}, {t: `peak ${N.peak_tf32.t}`, f: 'mm-peak'}, {t: `${N.mm_op.t} cycles per op`, f: 'mm.reload'}], {side: 'u', fs: 24});
      }},
    {name: 'From DRAM', where: () => ({level: 0}),
      say: () => `Tiles too big for the L2: every load comes from DRAM, ${n('tl_all_dr')} cycles per 16-line load with all minions loading, and the matmul falls to ${n('mm_dram_tf')} TFLOP/s`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH).concat(Object.values(MSC)), true);
        glowTiles(tok, fx, 0.12, 'var(--c2)');
        if (!REDUCED) {
          const t0 = CLK.t; let nx = 0;
          // each line from its memory shire through its L3 home to the loading shire, as an L2 miss returns (fact sc.l3-miss)
          every(tok, t => { while (nx <= t - t0) { const s = Object.values(SH)[Math.floor(Math.random() * 32)], home = Math.floor(Math.random() * 32), m = MSC[home % 8], pk = packet(fx, 'var(--c3)', 8);
            const P = pts(via(m, SH[home], s));
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
  T(g, X0, BAND.y + 46, 'time to 90 °C;', 't-sm halo'); T(g, X0, BAND.y + 66, `1 s here is ${SPEED} s`, 't-sm halo');
  const bars = rows.map((r, i) => {
    const y = BAND.y + 80 + i * 64;
    T(g, X0, y + 18, r.name, 't-lab halo', 'start', r.f).style.fontSize = '19px';
    S(E('rect', {x: X0, y: y + 25, width: W, height: 26, rx: 5}, g), {fill: 'var(--grid)'});
    const bar = S(E('rect', {x: X0, y: y + 25, width: 0, height: 26, rx: 5}, g), {fill: `color-mix(in srgb, ${r.col} 60%, transparent)`});
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
        ['the heat race', `80 to 90 °C: random ${n('race_rand', 's')}, ones ${n('race_ones', 's')}, zeros never (${n('race_zero', 's')} runs)`, '', ''],
        ['fewer minions', `random data on 768 minions: ${n('race_768', 's')}; on 128: ${n('race_128')}`, '', ''],
      ]).replace('<th class="num">cycles</th><th class="num">pJ/B</th>', '<th class="num"></th><th class="num"></th>')
      + `<p class="pn-what small">The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: ${n('leak80')} at 80 °C.</p>`);
  },
  stages: [
    ...WPAT.map(([nm, k], i) => ({name: nm[0].toUpperCase() + nm.slice(1), where: () => ({level: 0}),
      say: () => i === 0 ? `Zeros: ${n('w_zeros', 'W')} at the board (at the launch temperature), hardly above the ${n('w_idle', 'W')} idle, at ${n('w_tflops')} TFLOP/s`
        : i === 1 ? `Ones: ${n('w_ones', 'W')}, the same ${n('w_tflops')} TFLOP/s` : `Random data: ${n('w_randn', 'W')}, the same instructions and the same ${n('w_tflops')} TFLOP/s`,
      run: async (tok, c) => {
        const fx = c.fx;
        if (c.glow && c.glowFx === fx) c.glow.amp = wAmp(k); else { c.glow = glowTiles(tok, fx, wAmp(k), 'var(--c2)'); c.glowFx = fx; }
        wattChart(c, i + 1);
        if (i === 0) callout(fx, DW / 2, DH + 10, [{t: `${N.w_tflops.t} TFLOP/s on every data set`, f: 'mm.w-data'}], {side: 'u', fs: 21});
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
    {name: 'Three cards', where: () => ({level: 0}),
      say: () => `On all three cards: ones cost ${n('w_ones_d', 'W')} more than zeros and random data ${n('w_rand_d', 'W')} more, at the board`,
      run: async (tok, c) => {
        const fx = c.fx; if (c.wc && c.wc.g.parentNode) c.wc.g.remove(); c.wcN = 0;
        c.glow = glowTiles(tok, fx, 1, 'var(--c2)'); c.glowFx = fx;
        const rows = [['random, a2', 'w_rd_a2'], ['random, a3', 'w_rd_a3'], ['random, a1c1', 'w_rd_a1'], ['ones, a2', 'w_od_a2'], ['ones, a3', 'w_od_a3'], ['ones, a1c1', 'w_od_a1']];
        const ch = bandChart(fx, 'W above zeros', rows.map(r => ({name: r[0], val: N[r[1]].t, f: 'mm.w-3cards', col: r[0].startsWith('r') ? 'var(--c2)' : 'var(--c4)'})), {y: 10});
        await anim(tok, 1600, q => ch.rows.forEach((r, i) => r.set(easeS(q) * V(rows[i][1]) / 30)));
      }},
    {name: 'The heat race', where: () => ({level: 0}),
      say: () => `The heat race on aifoundry2, from 80 °C to the 90 °C cap: random data gets there in ${n('race_rand', 's')}, ones in ${n('race_ones', 's')}, zeros never in a ${n('race_zero', 's')} run`,
      run: async (tok, c) => {
        const fx = c.fx; fx.textContent = ''; c.glow = null; c.wc = null;
        const warm = glowTiles(tok, fx, 0.2, 'var(--c2)');
        const rows = [{name: 'random', cap: V('race_rand'), txt: N.race_rand.t, f: 'heat.race', col: 'var(--c2)'}, {name: 'ones', cap: V('race_ones'), txt: N.race_ones.t, f: 'heat.race', col: 'var(--c4)'}, {name: 'zeros', cap: null, txt: `never, ${N.race_zero.t} s`, f: 'heat.race', col: 'var(--c1)'}];
        const t0 = CLK.t; if (REDUCED) warm.amp = 1; else every(tok, t => { warm.amp = Math.min(1, 0.2 + (t - t0) / 1600); });
        await raceChart(tok, c, rows, 'All 1,024 minions');
      }},
    {name: 'Fewer minions', where: () => ({level: 0}),
      say: () => `Random data on fewer minions per shire buys time: 768 minions ${n('race_768', 's')}, 512 ${n('race_512', 's')}, 384 ${n('race_384', 's')}, 256 ${n('race_256', 's')}, and 128 never`,
      run: async (tok, c) => {
        const fx = c.fx; fx.textContent = '';
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
      ]).replace('<th class="num">cycles</th><th class="num">pJ/B</th>', '<th class="num"></th><th class="num"></th>')
      + `<p class="pn-what small">Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.</p>`);
  },
  stages: [
    {name: 'One line', where: () => ({level: 0}), hold: 0,
      say: () => `Every minion hammers one global atomic in shire 0: its bank retires one every ${n('hot10')}, about ${n('hot60')} for the whole chip`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells([c.host], true);
        callout(fx, c.host.sx, c.host.sy, [{t: 'one line in shire 0'}, {t: `an atomic every ${N.hot10.t}`, f: 'hot-cost'}], {cell: c.host, side: 'r', fs: 21});
        hotStream(tok, c, Object.values(SH).filter(s => s !== c.host), () => c.host, 150);
        await wait(tok, 6500);
      }},
    {name: 'Fair shares', where: () => ({level: 0}),
      say: () => `The atomic is fair: with all 32 shires at it, the host shire gets ${n('hot_host')} of an even share and the lowest shire ${n('hot_min')}`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        if (!c.hs1) hotStream(tok, c, Object.values(SH).filter(s => s !== c.host), () => c.host, 150);
        const ch = bandChart(fx, 'Shares', [{name: 'host shire', val: N.hot_host_rng.t, f: 'hot.fair'}, {name: 'lowest shire', val: N.hot_min_rng.t, f: 'hot.fair'}], {note: '1 = even, three cards'});
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
        const fx = c.fx; remoteAtomics(tok, c, 22); hostLoads(tok, c, 0);
        const B = AP[1].bank[0];
        await wait(tok, 1800);
        sayAt(c, fx, B.x, B.y + 40, [{t: 'the host stops'}, {t: `${N.hot22.t} of its rate`, f: 'hot.cliff'}], {side: 'r', fs: 21, col: 'var(--bad)'});
        await wait(tok, 1e3);
      }},
    {name: 'Spread it', where: () => ({level: 0}),
      say: () => `Spread over 32 lines, one per shire: ${n('hot031')} per atomic and ${n('hot1919')}, ${n('hot32x')} the rate, at ${n('hot_nj_s')} each against ${n('hot_nj')}: ${n('hot17x')} less energy`,
      run: async (tok, c) => {
        const fx = c.fx; hiCells(Object.values(SH), false);
        const all = Object.values(SH);
        hotStream(tok, c, all, s => all[(all.indexOf(s) + 1 + Math.floor(Math.random() * 31)) % 32], 30);
        await wait(tok, 1200);
        callout(fx, DW / 2, DH / 2, [{t: `${N.hot1919.t}: ${N.hot32x.t}`, f: 'hot-cost'}, {t: `${N.hot_nj_s.t} per atomic, not ${N.hot_nj.t}`, f: 'hot-energy'}], {side: 'u', fs: 24});
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
  if (rate <= 0 && !c.hl.pile) {   // stopped: the host's loads wait at the banks and none gets through
    c.hl.q.forEach(pk => pk.remove()); c.hl.q = [];
    c.hl.pile = E('g', {}, fx);
    keys.forEach((k, i) => { const B = P1.bank[i % 4], pk = packet(c.hl.pile, 'var(--c1)', 7); at(pk, {x: B.box.x + 16 + Math.floor(i / 4) * 17, y: B.box.y + B.box.h - 14}); });
    fadeIn(c.hl.pile);
  }
  if (c.hlab && c.hlab.parentNode) c.hlab.remove();
  const L1 = rate > 0 ? (c.remN ? [{t: "the host's loads"}, {t: `${N.hot21.t}%`, f: 'hot.cliff'}, {t: 'of their rate alone'}] : [{t: "the host's loads"}, {t: 'their rate alone'}]) : [{t: "the host's loads stop"}, {t: `${N.hot22.t} of their rate`, f: 'hot.cliff'}];
  c.hlab = callout(fx, SF.x + SF.w, SF.y + 160, L1, {side: 'r', fs: 20, col: 'var(--c1)'});
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
      ]).replace('<th class="num">cycles</th><th class="num">pJ/B</th>', '<th class="num"></th><th class="num"></th>')
      + `<p class="pn-what small">One shire's 32 minions reduce in ${n('ar32')}; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); the mesh legs are drawn x first like every route here.</p>`);
  },
  stages: [
    {name: 'Levels 0-2', where: () => ({level: 1, sid: 0}),
      mark: () => [{t: `levels 0-2: ${N.lv_fln.t}`, f: 'sync.tree-levels'}],
      say: () => `Levels 0-2, inside each neighbourhood along the fast network's tree edges: 1→0, 3→2, 5→4, 7→6, then 2→0 and 6→4, then 4→0, ${n('lv_fln')} per level`,
      run: async (tok, c) => {
        const P1 = AP[1], fx = c.fx, mc = (nb, m) => { const p = P1.min[nb + ':' + m]; return {x: p.x + p.w / 2, y: p.y + p.h / 2}; };
        // the partial sums' trails in the flow's own colour, over the orange tree edges they follow, so that the end
        // state shows which edges levels 0-2 used
        for (let h = 0; h < 3; h++) {
          const moves = [];
          for (let nb = 0; nb < 4; nb++) for (let m = 1; m < 8; m++) if (lsb(m) === h) moves.push([mc(nb, m), mc(nb, m - (1 << h))]);
          await Promise.all(moves.map(([a, b]) => { const pk = packet(fx, 'var(--c2)', 8); at(pk, a); return travel(tok, fx, pk, [a, b], 1300, {w: 6, col: 'var(--c2)'}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
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
        const legXb = (a, b) => { const A = m0(a), B = m0(b); return [A, {x: P1['ch' + a].x, y: A.y}, {x: P1['ch' + a].x, y: P1.xbarY}, {x: P1['ch' + b].x, y: P1.xbarY}, {x: P1['ch' + b].x, y: B.y}, B]; };
        for (const lv of [[[1, 0], [3, 2]], [[2, 0]]]) {
          await Promise.all(lv.map(([a, b]) => { const pk = packet(fx, 'var(--c1)', 9); return travel(tok, fx, pk, legXb(a, b), 1900, {w: 5, col: 'var(--c1)'}).then(() => pk.remove(), e => { pk.remove(); throw e; }); }));
          await wait(tok, 350);
        }
        await pulse(tok, fx, m0(0), 1200, 'var(--c2)', 40);
      }},
    {name: 'Levels 5-9', where: () => ({level: 0}),
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
    {name: 'Back down', where: () => ({level: 0}),
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
    {name: 'Against a barrier', where: () => ({level: 0}),
      say: () => `A chip barrier built from global atomics and credits takes ${n('chipbar')} cycles (${n('chipbar_us')}): the hardware tree reduces and broadcasts in about a quarter of that`,
      run: async (tok, c) => {
        const fx = c.fx;
        const rows = [['allreduce, 1,024', 'ar1024', 'sync-allreduce1024', 'var(--c1)'], ['chip barrier', 'chipbar', 'sync-chip-barrier', 'var(--c7)'], ['allreduce, 32', 'ar32', 'sync-allreduce32', 'var(--c1)'], ['shire barrier', 'flb', 'sync-shire-barrier', 'var(--c7)']];
        const ch = bandChart(fx, 'Cycles', rows.map(r => ({name: r[0], val: N[r[1]].t, f: r[2], col: r[3]})));
        await anim(tok, 1800, q => ch.rows.forEach((r, i) => r.set(easeS(q) * V(rows[i][1]) / V('chipbar'))));
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
const CAPS = {
  A: () => `A load that misses everywhere pays the mesh twice, to its L3 home and on to a memory shire: about ${n('lat_dram')} cycles, ${n('lat_dram_chip')} of them in the DRAM chip.`,
  B: () => `The latency ladder: ${n('lat_l1')} cycles in L1, ${n('lat_l2')} in L2, ${n('lat_l3_a')} + ${n('lat_l3_b')} in L3, about ${n('lat_dram')} in DRAM.`,
  C: () => `TensorSend moves registers from a hart to a minion anywhere on the chip: between shires, ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip, on all three cards.`,
  D: () => `Handing a result to the next shire costs ${n('rl_e_next')} pJ per byte against ${n('rl_e_dram')} through DRAM: ${n('rl_13th')} of the energy, at ${n('rl_speed')} the bandwidth.`,
  E: () => `Gathers from scattered lines: ${n('g_l1_r')} G elements/s from L1, but only ${n('g_dr_r')} G from DRAM, at ${n('g_dr_e')} pJ each.`,
  F: () => `The host link, timed on three cards: ${n('pcie_h2d')} GB/s to the card by DMA, ${n('pcie_stg_rng')} GB/s the way a program copies; an empty kernel costs the card ${n('pcie_b2b_rng')}, a lone launch waited for ${n('pcie_launch_rng')}, mostly the host's polling.`,
  G: () => `A matmul step on the tensor unit: TensorLoad brings A in ${n('tl_l2')} cycles, TensorFMA takes ${n('tfma_tenb')}, the next load hides behind it: ${n('tflops')} TFLOP/s on ${n('n1024')}.`,
  H: () => `The same matmul at the same ${n('w_tflops')} TFLOP/s draws ${n('w_zeros')} W on zeros and ${n('w_randn')} W on random data at the board, and random data reaches 90 °C in ${n('race_rand')} s.`,
  I: () => `One hot line: the atomic is fair to every shire, but 22 requesters stop its home shire's own traffic dead, while 21 leave it ${n('hot21r')} of its rate.`,
  J: () => `The allreduce tree: ten levels up with TensorReduce and back down with TensorBroadcast, ${n('ar1024')} for all ${n('n1024')}, a quarter of a software barrier.`,
};
const compG = (key, i) => LAYERS[Z.level].querySelectorAll(`.comp[data-comp="${key}"]`)[i || 0] || null;
const STEPS = [
  {cap: () => `The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor.`,
    view: {level: 0}, panel: ['chip'], sub: () => 'Every part is clickable. Dashed: inferred (the LPDDR4X pairing); the button under the die lists what would settle each inferred part.'},
  {cap: () => `${n('cshires')} compute shires of ${n('per_shire')} run the kernels; the master shire (${n('master_id')}) schedules them and a spare (${n('spare_id')}) waits for yield recovery.`,
    view: {level: 0}, hi: ['cshire', 'master'], panel: ['cshire', () => ({cell: SH[13]})], sel: () => SH[13].g, sub: () => `Placed by measured distances, all ${n('pairs496')} shire pairs; the firmware's NoC-spec map agrees in ${n('fw_pairs')} pair distances. Shire 13 is ringed.`},
  {cap: () => `An ${n('grid86')} mesh of ${n('stops')} stops joins them. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire.`,
    view: {level: 0}, hi: ['mesh', 'links'], panel: ['mesh'], sel: () => compG('mesh'), sub: () => 'Routes are shortest paths; the flows draw each leg x first (the order was not measured).'},
  {cap: () => `${n('memshires')} memory shires drive ${n('channels')} LPDDR4X channels (${n('dram_gb')}), ${n('dram_peak')} GB/s peak at this clock; the chip streams ${n('dram_bw')} GB/s.`,
    view: {level: 0}, hi: ['memshire', 'dram'], panel: ['dram', () => ({ms: [0, 1]})], sel: () => compG('dram'), sub: () => `Their places come from a fit on aifoundry2 that holds for ${n('ms_fit')} of DRAM loads, within ±3 cycles, on all three cards; the firmware's map agrees on the seven the fit places on its own.`},
  {cap: () => `Inside a shire, ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM: ${n('scp_mb')} scratchpad, ${n('l2_kb')} L2 and a ${n('l3_mb')} slice of the L3.`,
    view: {level: 1, sid: 13}, panel: ['banks', () => ({})], sub: () => `Orange links: the fast local network's tree edges, ${n('ts_fln')} round trip against ${n('ts_xbar')} for other pairs.`},
  {cap: () => `A minion has ${n('harts')} and a vector unit whose ${n('lanes_n')} lanes also run the tensor instructions. ${n('n1024')} minions sustain ${n('tflops')} TFLOP/s fp32 at ${n('mhz')}.`,
    view: {level: 2, sid: 13, nb: 0, mi: 0}, panel: ['tensor'], sel: () => compG('tensor'), sub: () => `The firmware turns ${n('l1_scp')} of the ${n('l1_kb')} L1 into the tensor scratchpad and leaves each hart ${n('l1_hart')}.`},
  {flow: 'A'}, {flow: 'B'}, {flow: 'C'}, {flow: 'D'}, {flow: 'E'}, {flow: 'F'}, {flow: 'G'}, {flow: 'H'}, {flow: 'I'}, {flow: 'J'},
];
let TOUR = null;
function setCap(html) { hideTip(); $('cap').innerHTML = `<span class="cap-in">${html}</span>`; fitCap(); }
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
/* the index of the button in box that has the focus (-1 for none): a rebuilt row of buttons gives it back */
const focusIn = box => { const a = document.activeElement; return a && box.contains(a) ? [...box.querySelectorAll('button')].indexOf(a) : -1; };
const refocus = (box, k) => { if (k < 0) return; const b = box.querySelectorAll('button')[k]; if (b) b.focus({preventScroll: true}); };
function dots(i) {
  const d = $('dots'), had = focusIn(d); d.textContent = '';
  if (i < 0) return;
  STEPS.forEach((s, k) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = k < i ? 'past' : k === i ? 'on' : '';
    const nm = s.flow ? `flow ${KEYOF[s.flow]}, ${FLOWS[s.flow].title}` : `slide ${k + 1}`;
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
async function tourGo(i) {
  if (!TOUR) return;
  i = Math.max(0, Math.min(STEPS.length - 1, i)); TOUR.i = i;
  const s = STEPS[i];
  if (TOUR.tok) TOUR.tok.dead = true;
  const tok = TOUR.tok = {dead: false};
  select(null);
  setKick(`Tour · step ${i + 1} of ${STEPS.length}`); dots(i);
  // presenting: every tour step starts with the camera following, whatever the reader did before
  if (!FOLLOW) { FOLLOW = true; FOLLOW_AUTO = false; $('btn-follow').setAttribute('aria-pressed', 'true'); }
  if (s.flow) { setCap(CAPS[s.flow]()); sub(''); startFlow(s.flow, 0, {intro: true}); return; }
  stopFlow(true);
  setCap(s.cap()); sub(s.sub ? s.sub() : '');
  if (s.panel) showComp(s.panel[0], s.panel[1] ? s.panel[1]() : {});   // the panel changes with the caption, not after the zoom
  renderBar(); playBtn();
  await goTo(s.view, {clk: tok, ms: CLK.on ? undefined : 0});
  if (!TOUR || TOUR.i !== i || tok.dead) return;
  if (s.hi) highlight(s.hi);
  if (s.sel) { const g = s.sel(); if (g) select(g); }
}
/* presenting: the tour turns on larger panel text and hides the reference lists (CSS #stage.present) */
function startTour(at) {
  TOUR = {i: 0}; $('btn-tour').textContent = 'End tour'; $('btn-tour').classList.add('on');
  $('stage').classList.add('present');
  tourGo(at || 0);
}
function endTour() {
  if (!TOUR) return;
  if (TOUR.tok) TOUR.tok.dead = true;
  TOUR = null; $('btn-tour').textContent = 'Tour'; $('btn-tour').classList.remove('on');
  $('stage').classList.remove('present');
  dots(-1); clearDim();
  if (flowOn() || FL.k) { const k = FL.k; setKick(`Flow ${KEYOF[k]} · ${FLOWS[k].title}`); CAPFLOW = true; renderBar(); playBtn(); }
  else resetCap();
}
const HINT = 'Space pauses · ← → stages · + − zoom · double-click zooms in · F presents · P panel · C follow · T tour';
function resetCap() {
  CAPFLOW = false;
  setKick('Explore');
  setCap(`Click any part of the chip, zoom with the scale control under the drawing, pick one of ten flows, or press Tour to step through it all in ${STEPS.length} steps.`);
  sub(HINT); renderBar();
}
/* the stage bar: the active flow's stages, the current one marked; each is a button */
function renderBar() {
  const ol = $('stages'), had = focusIn(ol); ol.textContent = '';
  const k = FL.k;
  $('stage').classList.toggle('playing', flowOn() && CLK.on && !FL.still);
  if (!k) {
    const li = document.createElement('li'); li.className = 'stg-hint';
    li.textContent = TOUR ? `Tour step ${TOUR.i + 1} of ${STEPS.length}: the arrows step, Shift with an arrow jumps a step` : 'Pick a flow above (keys 1 to 9 and 0) to see its stages here, or press Tour';
    ol.appendChild(li);
    $('btn-prev').disabled = TOUR ? TOUR.i === 0 : !LASTFLOW; $('btn-next').disabled = !!TOUR && TOUR.i === STEPS.length - 1;
    return;
  }
  const sts = FLOWS[k].stages;
  sts.forEach((s, i) => {
    const li = document.createElement('li'), b = document.createElement('button');
    if (i === FL.i) li.className = 'on';
    b.type = 'button'; b.className = 'stg' + (i < FL.i ? ' past' : i === FL.i ? ' on' : '');
    if (i === FL.i) b.setAttribute('aria-current', 'step');
    b.innerHTML = `<span class="sn">${i + 1}</span><span class="st">${esc(s.name)}</span>`;
    b.title = `Stage ${i + 1} of ${sts.length}: ${s.name}`;
    b.setAttribute('aria-label', `Stage ${i + 1} of ${sts.length}: ${s.name}`);
    b.addEventListener('click', () => goStage(i));
    li.appendChild(b); ol.appendChild(li);
  });
  refocus(ol, had);
  $('btn-prev').disabled = FL.i === 0 && !(TOUR && TOUR.i > 0);
  $('btn-next').disabled = FL.i === sts.length - 1 && !(TOUR && TOUR.i < STEPS.length - 1);
}
/* the Play button: Pause while a flow plays, Play when paused, Replay after */
function playBtn() {
  const b = $('btn-play'), still = !!TOUR && !STEPS[TOUR.i].flow;
  const t = FL.k ? (FL.done ? 'Replay' : (CLK.on && !FL.still ? 'Pause' : 'Play')) : still ? (CLK.on ? 'Pause' : 'Play') : LASTFLOW ? 'Replay' : 'Play';
  b.textContent = t;
  b.disabled = !FL.k && !LASTFLOW && !still;
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
  if (FL.still) {
    CLK.on = true;
    if (FL.i < FLOWS[FL.k].stages.length - 1) startFlow(FL.k, FL.i + 1, {keep: true});
    else { FL.still = false; FL.done = true; renderBar(); playBtn(); }
    return;
  }
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
  fsLabel();
  if (on && blocked) toast(`<p><b>Presenting inside the page's frame.</b> The frame does not allow full screen here.</p>`
    + `<p>For the whole screen, press <kbd>F11</kbd> (on a Mac <kbd>Ctrl</kbd>+<kbd>⌘</kbd>+<kbd>F</kbd>), or open the page in a window of its own, where <kbd>F</kbd> goes full screen. <kbd>Esc</kbd> or <kbd>F</kbd> leaves.</p>`
    + `<div class="tb"><button type="button" class="st-btn primary" data-t="win">Open a presenter window</button><button type="button" class="st-btn" data-t="ok">Stay in the frame</button></div>`, 14000);
  else hideToast();
  setTimeout(() => { fitCap(); }, 80);
}
const fsLabel = () => { $('btn-fs').textContent = (fsEl() || PRES) ? 'Exit' : 'Present'; setTimeout(fitCap, 80); };
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
   until then, and whenever the frame loses the focus, a hint over the drawing says so. A click anywhere hides it. */
const FRAMED = (() => { try { return window.self !== window.top; } catch (_) { return true; } })();
function kbdHint() { const h = $('kbd-hint'); if (h) h.hidden = !FRAMED || document.hasFocus() || PRES || !!fsEl(); }
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
function togglePanel(show) {
  const st = $('stage'), hide = show === undefined ? !st.classList.contains('nopanel') : !show;
  st.classList.toggle('nopanel', hide); $('btn-panel').setAttribute('aria-pressed', String(!hide));
  setTimeout(fitCap, 60);
}
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
    if (TOUR.i >= STEPS.length - 1) { sub('End of the tour: Q or End tour leaves it; the Left arrow steps back.'); return; }
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
    if (TOUR.i > 0) tourGo(TOUR.i - 1);
    return;
  }
  if (FL.k) { goStage(FL.i - 1); return; }
  // no flow on the stage: back to the last one played, at its last stage's end state; Left never starts the tour
  if (LASTFLOW) startFlow(LASTFLOW, FLOWS[LASTFLOW].stages.length - 1, {still: true, done: true});
}
function back() {
  if (PRES) { setPres(false); return; }
  if (TOUR) { endTour(); stopFlow(); return; }
  if (FL.k) { stopFlow(); return; }
  if (Z.level) scaleTo(Z.level - 1);
}
document.querySelectorAll('[data-flow]').forEach(b => b.addEventListener('click', () => { if (TOUR) endTour(); if (FOLLOW_AUTO) setFollow(true); startFlow(b.dataset.flow, 0, {intro: true}); }));
/* a mouse click leaves no focus on a button, a summary or a fact in the stage, so that Space then pauses (the keyboard
   keeps its focus) */
$('stage').addEventListener('click', e => { const b = e.target.closest && e.target.closest('button, summary, li.fact'); if (b && e.detail > 0) b.blur(); });
$('btn-play').addEventListener('click', playPause);
$('btn-tour').addEventListener('click', () => { if (TOUR) { endTour(); stopFlow(); } else startTour(0); });
$('btn-fs').addEventListener('click', present);
$('btn-panel').addEventListener('click', () => togglePanel());
$('btn-next').addEventListener('click', () => next(false));
$('btn-prev').addEventListener('click', () => prev(false));
$('btn-follow').addEventListener('click', () => setFollow(!FOLLOW));
$('z-in').addEventListener('click', () => scaleTo(Z.level + 1));
$('z-out').addEventListener('click', () => scaleTo(Z.level - 1));
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
  switch (e.key) {
    case 'ArrowRight': case 'PageDown': e.preventDefault(); next(e.shiftKey); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); prev(e.shiftKey); break;
    case ' ': case 'Spacebar': {
      // Space on a control presses it, except where pressing it would restart what Space should pause: the active
      // flow's own button, a stage button, and, while a flow plays, a summary or a fact in the panel
      const fb = tg.closest && tg.closest('[data-flow]');
      const pause = (fb && FL.k && fb.dataset.flow === FL.k) || (tg.closest && tg.closest('.stg')) || (flowOn() && tg.closest && tg.closest('#pn-body summary, #pn-body li.fact'));
      if (onControl && !pause) return;
      e.preventDefault(); SPACE_EATEN = true; playPause(); break;
    }
    case 'f': case 'F': e.preventDefault(); present(); break;
    case 'p': case 'P': e.preventDefault(); togglePanel(); break;
    case 'd': case 'D': e.preventDefault(); toggleTheme(); break;
    case 'c': case 'C': e.preventDefault(); setFollow(!FOLLOW); break;
    case 't': case 'T': e.preventDefault(); if (TOUR) { endTour(); stopFlow(); } else startTour(0); break;
    case 'q': case 'Q': if (TOUR) { e.preventDefault(); endTour(); stopFlow(); } break;
    case '+': case '=': e.preventDefault(); scaleTo(Z.level + 1); break;
    case '-': case '_': e.preventDefault(); scaleTo(Z.level - 1); break;
    case 'Escape': back(); break;
    case 'Backspace': if (Z.level) { e.preventDefault(); scaleTo(Z.level - 1); } break;
    case 'Home': if (FL.k) { e.preventDefault(); goStage(0); } break;
    case 'End': if (FL.k) { e.preventDefault(); goStage(FLOWS[FL.k].stages.length - 1); } break;
    default: {
      const i = '1234567890'.indexOf(e.key);
      if (i >= 0 && e.key.length === 1) { if (TOUR) endTour(); if (FOLLOW_AUTO) setFollow(true); startFlow(ORDER[i], 0, {intro: true}); }
    }
  }
});

/* ================= the text below the stage ================= */
function prose() {
  $('summary-text').innerHTML = [
    `<p><b>The chip.</b> The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die in TSMC ${n('process')}: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor. The diagram draws the die (width and height from a published die plot) with ${n('cshires')} compute shires, the master (${n('master_id')}) and spare (${n('spare_id')}) shires, the PCIe and I/O shires, and ${n('memshires').toLowerCase()} memory shires, on an ${n('grid86')} mesh of ${n('stops')} stops. The compute shires sit where measured distances put them, and the firmware's NoC-spec map, once its boot-time renaming is applied, puts every one in the same cell (${n('fw_pairs')} pair distances). Each mesh hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. Off the die, four LPDDR4X packages hold ${n('channels')} channels of ${n('ch_bits')}, ${n('dram_gb')}; the chip streams ${n('dram_bw')} GB/s from them against ${n('dram_peak')} GB/s peak at their ${n('mts')} MT/s. The host links through the PCIe shire: Gen4 x8, trained at ${n('pcie_neg')} on every card, ${n('pcie_h2d')} GB/s to the card by DMA. The fp32 matmul at ${n('tflops')} TFLOP/s draws ${n('mmw')} at the board on the three cards, ${n('perw')} GFLOP/s per watt.</p>`,
    `<p><b>A shire.</b> ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM in ${n('banks')}. The cards run mode M0: ${n('scp_mb')} of scratchpad that any shire can address, ${n('l2_kb')} of L2 private to the shire, and a ${n('l3_mb')} slice of the chip's ${n('l3_chip')} L3. The shire meets the mesh at one stop, and inside a neighbourhood minions talk fastest along the tree edges of the fast local network (${n('ts_fln')} round trip, against ${n('ts_xbar')} cycles for other pairs).</p>`,
    `<p><b>A minion.</b> ${n('harts')}, in-order and single-issue, a vector unit of ${n('lanes')} and a ${n('l1_kb')} L1 data cache, of which the firmware makes ${n('l1_scp')} a tensor scratchpad and leaves each hart ${n('l1_hart')}. The tensor instructions are no separate unit: state machines in the vector unit run them on its lanes' FMA and int8 multiply-add units, so the tensor peak (${n('peak32')}, ${n('peak16')} or ${n('peak8')} operations per cycle) is the lanes' peak. On ${n('n1024')} minions at ${n('mhz')} they sustain ${n('tflops')} TFLOP/s fp32.</p>`,
    `<p><b>The flows.</b> (1) A load that misses every cache: ${n('lat_l1')} cycles would have been an L1 hit and ${n('lat_l2')} an L2 hit; the L3 home is PA[10:6] and costs ${n('lat_l3_a')} + ${n('lat_l3_b')}; the memory shire is PA[8:6] and adds ${n('lat_ms_a')} + ${n('lat_ms_b')} cycles per hop; a typical DRAM load takes ${n('lat_dram')}, of which ${n('lat_dram_chip')} are the DRAM chip. (2) The ladder adds the read buffer (${n('lat_rb')}), the own scratchpad (${n('lat_scp')}) and another shire's scratchpad (${n('lat_rs_a')} + ${n('lat_rs_b')} per hop). (3) TensorSend: ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip. (4) The relay: ${n('rl_e_next')} pJ/B to the next shire against ${n('rl_e_dram')} through DRAM (${n('rl_x')} less). (5) Gathers from scattered lines: ${n('g_l1_r')}, ${n('g_l2_r')}, ${n('g_rs_r')} and ${n('g_dr_r')} G elements/s from L1, L2, a scratchpad two hops away and DRAM. (6) The host over PCIe, timed on three cards: ${n('pcie_h2d')} GB/s to the card and ${n('pcie_d2h')} back by DMA (${n('pcie_h2d_pct')} and ${n('pcie_d2h_pct')} of the link), ${n('pcie_stg_rng')} GB/s for a program's staged copies; an empty kernel costs the card ${n('pcie_b2b_rng')} queued, while one launch waited for takes ${n('pcie_launch_rng')}, most of it the runtime's ${n('poll500')} idle poll. (7) A matmul step: TensorLoad ${n('tl_l2')} cycles, TensorFMA ${n('tfma_tenb')}, ${n('mm_op')} per op with the next load hidden. (8) The Horace runs of the matmul (${n('w_tflops')} TFLOP/s, timed from the host) on zeros, ones and random data: ${n('w_zeros')}, ${n('w_ones')} and ${n('w_randn')} W at the board at the launch temperature; random data reaches 90 °C in ${n('race_rand')} s, zeros never. (9) One hot line: fair shares (${n('hot_host')} for the host shire), and 22 requesters stop the host shire's own loads (${n('hot22')}). (0) The allreduce tree: ${n('ar1024')} for all ${n('n1024')} minions, against ${n('chipbar')} cycles for a chip barrier.</p>`,
  ].join('');
  // what is measured, specified, derived and inferred
  const fs = Object.values(F), of = k => fs.filter(f => f.kind === k), meas = of('measured');
  const mc = k => meas.filter(f => f.cards.length === k).length;
  const lk = id => `<a href="#facts" data-f="${id}" class="num">${id}</a>`;
  const SETTLED = f => /^(Superseded|Settled) 27 Sep/.test(f.note || '');   // an inferred fact the firmware's map has since settled (build_facts.py, AMEND)
  $('honest-text').innerHTML = `<p>The page rests on ${fs.length} facts: <b>${meas.length} measured</b>, ${of('spec').length} from the specification (the datasheet, the Programmer's Reference Manual, the core-et documents and the firmware and runtime source), ${of('derived').length} derived from others and <b>${of('inferred').length} inferred</b>. Of the measured facts, ${mc(3)} hold on all three lab cards (aifoundry2, aifoundry3 and aifoundry1 card 1), ${mc(2)} on two and ${mc(1)} on one, mostly aifoundry2${mc(0) ? `; ${mc(0)} name no card` : ''}. Every table here is at ${n('mhz')}, where a warm card sits.</p>`
    + `<p>What the drawing assumes, and what the second version (27 September) settled:</p><ul>`
    + `<li><b>Where the compute shires are</b> is measured: all ${n('pairs496')} shire pairs fit a constant plus ${n('hop_cyc')} per hop of Manhattan distance on the logical map (${lk('mesh.shortest-paths')}). <b>How that map sits on the die</b> was inferred (${lk('mesh.orientation')}, ${lk('L33')}, ${lk('L34')}); it is now the firmware's own: the "default Shire Virtual ID Map, based on the NOC spec", renamed as the boot firmware renames the shires, matches the measured map in ${n('fw_pairs')} pair distances with no rotation or mirror (${lk('fw.map-match')}; fact ${lk('L37')}, which compared the map before the renaming, is superseded). Still open: whether the silicon has this handedness or the published die plot's, its mirror (${lk('die.handedness')}, ${lk('L24')}).</li>`
    + `<li><b>The four grey cells</b>: the firmware's maps name them, the master (shire 32) in the north cell, the spare (33) in the south one, PCIe and then I/O east of the master (${lk('fw.grey-cells')}). They are drawn solid now; timing a counter read on shire 32 from every compute shire would confirm the master's cell on the cards.</li>`
    + `<li><b>The memory shires' places</b> come from a fit of DRAM latencies on one card, aifoundry2 (${lk('L40')}), within ±3 cycles for ${n('ms_fit')} of loads on all three cards (${lk('ms-fit-3cards')}). The firmware's map puts the 7 memory shires the fit places on its own in the same places, if its mcN is the memory shire that PA[8:6] = N selects; memory shire 2, a tie in the fit, then has one cell left in both (${lk('fw.memshires')}, ${lk('ms2-forced')}), so the map confirms the frame, not memory shire 2 on its own. Timing a counter read on each memory shire would place it directly.</li>`
    + `<li><b>Which two memory shires share each LPDDR4X package</b> is not documented; the drawing pairs neighbours (${lk('dram.pkg-pairing')}, ${lk('L23')}). The packages are dashed: the card's schematic settles it.</li>`
    + `<li><b>Routes</b>: every leg, a reply included, is drawn on its own route, x first, then y, on the logical map; where x first would cross an empty corner of the grid (some legs from a memory shire), y first. The mesh's routing order was never measured (${lk('L104')}); only the hop count is.</li>`
    + `<li><b>The way back</b> of a DRAM load: the data returns through the L3 home, as the shire cache specification describes an L3 miss (${lk('sc.l3-miss')}); the model pays the mesh round trip on both legs (${lk('addr.load-model')}). Only each leg's route is drawn on an assumption, the same for a request and a reply: replies are told by their colour. <b>Dashes</b> mark only what is inferred: the four LPDDR4X packages, and the host's path from the PCIe shire into DRAM in flow 6.</li>`
    + `<li><b>Inside a shire</b>, the drawing is a block diagram: no source gives where the banks and neighbourhoods sit in the tile (${lk('L114')}). The minions' order in a neighbourhood follows the core-et floorplan (${lk('L115')}).</li>`
    + `<li><b>Sizes</b>: the die's width and height and the tile pitch are pixel estimates on one vendor die plot scaled to ${n('die_mm2')} mm² (${lk('chip.die-dims')}, ${lk('chip.hop-pitch')}).</li>`
    + `<li><b>The host link</b> is measured now, on three cards (${lk('pcie.h2d')}, ${lk('pcie.d2h')}, ${lk('pcie.staged')}, ${lk('pcie.launch')}); which way the host's writes reach DRAM (through the L3 homes or straight to the memory shires) is not established.</li>`
    + `<li><b>Gathers and scatters</b> (E48) were reduced on 27 September and have no published page yet; the heat race of flow 8 is one card's (aifoundry2).</li>`
    + `<li><b>What was measured for this version.</b> Only the host link was measured anew (27 September, three cards: ${lk('pcie.h2d')}). Flows 7, 8, 9 and 0 draw measurements already in the repository: the matmul benchmark and the tensor-load timings, the Horace runs of the same matmul on different data, the hot-line passes and the allreduce ladder, each fact with its data file.</li></ul>`
    + `<p>The inferred facts still open:</p><ul>${of('inferred').filter(f => !SETTLED(f)).map(f => `<li>${esc(f.statement)} <span class="small">(${lk(f.id)})</span></li>`).join('')}</ul>`
    + `<p>Inferred before 27 September and settled since by the firmware's map (each fact's note says what is left):</p><ul>${of('inferred').filter(SETTLED).map(f => `<li>${esc(f.statement)} <span class="small">(${lk(f.id)}: ${esc(f.note)})</span></li>`).join('')}</ul>`;
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
} catch (_) { /* no URL flags */ }
if (window.__ET_PRESENTER) { setTimeout(() => toast('<p><b>Presenter window.</b> Press <kbd>F</kbd> for full screen; <kbd>T</kbd> starts the tour.</p>', 9000), 300); }
fitCap();
/* a read-only view of the state, for the page's tests (headless Chrome) */
window.__chipState = () => ({level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi, flow: FL.k, stage: FL.i, done: FL.done, still: FL.still,
  clockOn: CLK.on, clock: Math.round(CLK.t), follow: FOLLOW, zooming: ZW, pip: !PIP.el.hidden, pres: PRES, tour: TOUR ? TOUR.i : null,
  transform: [0, 1, 2].map(i => LAYERS[i].getAttribute('transform')), shown: [0, 1, 2].map(i => LAYERS[i].style.display !== 'none')});
/* on a narrow screen the drawing scrolls sideways: start at its middle, the compute shires */
try { const w = $('svgwrap'); if (w.scrollWidth > w.clientWidth + 4) w.scrollLeft = (w.scrollWidth - w.clientWidth) / 2; } catch (_) { /* not laid out */ }
})();
