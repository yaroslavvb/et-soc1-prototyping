/* The ET-SoC-1, interactively. D is facts.json (docs/reports/data/2026-09-27-chip-diagram/build_facts.py):
   D.facts  the facts the page uses, by id: statement, value, unit, source, kind (measured, spec, derived, inferred),
            the lab cards each covers, and the report page that quotes it
   D.num    every number the page prints outside a fact's own statement, each tied to the fact whose statement
            contains it (the build asserts that); n(key) prints one with its source on hover
   D.comp   the facts each details panel lists
   D.layout the measured 6 x 6 map of the compute shires, the inferred die view and the memory-shire fit
   A value the page computes (a route's hops, a model's cycles) cites the facts it comes from. Every leg, a reply
   included, is drawn on its own route, x first, then y, on the logical map; where x first would cross an empty
   corner (some legs from a memory shire), y first. The mesh's routing order was not measured (fact L104). Colours
   are the template's tokens only. With reduced motion there is no animation: each step draws its end state.
   Keys: 1-6 flows, arrows or PageUp/PageDown step the tour, Space pauses, F full screen, P hides the panel,
   D switches light and dark, Q or Esc ends the tour, Backspace zooms out. URL flags: ?theme=light|dark, ?panel=off. */
(function () {
'use strict';
const F = D.facts, N = D.num, COMPF = D.comp, LAY = D.layout;
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
let REDUCED = !!CK.reduced;
try { const mq = matchMedia('(prefers-reduced-motion: reduce)'); mq.addEventListener('change', e => { REDUCED = e.matches; }); } catch (_) { /* old browser */ }
const fnum = (v, dp) => CK.fmt.num(v, dp);
const V = k => { if (!N[k]) throw new Error('no number ' + k); return N[k].v; };
/* a number from D.num, with its fact attached */
function n(k, unit) {
  const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; }
  return `<span class="num" data-f="${x.f}">${esc(x.t)}${unit ? ' ' + esc(unit) : ''}</span>`;
}
/* a number the page computes, citing the facts it comes from */
const cn = (v, fids, dp, unit) => `<span class="num" data-f="${fids}">${fnum(v, dp)}${unit ? ' ' + unit : ''}</span>`;
const S = (node, o) => { for (const k in o) if (o[k] != null) node.style[k] = o[k]; return node; };
const E = (tag, attrs, parent) => CK.el(tag, attrs, parent);
function T(parent, x, y, str, cls, anchor, fids) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  t.textContent = str; if (fids) t.setAttribute('data-f', fids);
  return t;
}
const ns = cyc => cyc * 1000 / V('mhz');   // minion cycles at 600 MHz to ns

/* ================= geometry: the die drawn to scale (inferred from a die plot) ================= */
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
/* the die view must be the measured map transposed onto the die (orientation inferred), with the fitted memory shires */
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
  : c.type === 'master' ? 'master or spare' : c.type === 'pcie' ? 'PCIe shire' : c.type === 'io' ? 'I/O shire' : 'grey cell';

/* ================= the SVG and its three layers ================= */
const svg = $('chip');
svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
const LAYERS = [0, 1, 2].map(i => E('g', {class: 'lay', 'data-level': i}, svg));
LAYERS[1].style.display = 'none'; LAYERS[2].style.display = 'none';
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
  // the host and the PCIe link (from the PCIe shire's top edge)
  const pc = CELLS.find(c => c.type === 'pcie'), hx = 950, hy = -74, hw = 150, hh = 92, ly = -30;
  const gh = comp(L, 'host', {}, 'The host and the PCIe link: details');
  S(E('path', {d: `M${pc.sx},${pc.y + INS} V${ly} H${hx}`, fill: 'none'}, gh), {stroke: 'var(--c4)', strokeWidth: 6, strokeLinejoin: 'round'});
  boxShape(gh, hx, hy, hw, hh, 'var(--ink-2)', {fo: 0.08});
  T(gh, hx + hw / 2, hy + 54, 'Host', 't-mid', 'middle');
  T(gh, hx - 14, ly - 12, `PCIe Gen4 x8 · ${N.pcie_gbs.t} (link figure)`, 't-sm halo', 'end', 'bw-pcie pcie.link');
  AP[0].host = [{x: hx + 4, y: ly}, {x: pc.sx, y: ly}, {x: pc.sx, y: pc.sy}];
  // mesh links and stops, under the translucent tiles (visual only: the tiles take the clicks)
  const LG = E('g', {class: 'dimmable links', 'pointer-events': 'none'}, L);
  AP[0].links = LG;
  CELLS.forEach(a => CELLS.forEach(b => {
    if (a !== b && hops(a, b) === 1 && (a.lx < b.lx || a.ly < b.ly))
      S(E('line', {x1: a.sx, y1: a.sy, x2: b.sx, y2: b.sy}, LG), {stroke: 'var(--axis)', strokeWidth: 4, strokeLinecap: 'round'});
  }));
  CELLS.forEach(c => S(E('circle', {cx: c.sx, cy: c.sy, r: 6.5}, LG), {fill: 'var(--ink-2)'}));
  // the tiles
  CELLS.forEach(c => {
    const inferred = c.type === 'master' || c.type === 'pcie' || c.type === 'io' || (c.type === 'memshire' && TIE.has(c.id));
    const g = comp(L, c.type, {cell: c}, tileLabel(c)); c.g = g;
    boxShape(g, c.x + INS, c.y + INS, c.w - 2 * INS, c.h - 2 * INS, COL[c.type], {fo: c.type === 'cshire' ? 0.14 : 0.12, dash: inferred});
    const x0 = c.x + INS + 9, y0 = c.y + INS;
    if (c.type === 'cshire') T(g, x0, y0 + 38, String(c.id), 't-id');
    else if (c.type === 'memshire') { T(g, c.x + c.w / 2, y0 + 26, 'MS', 't-labb halo-s', 'middle'); T(g, c.x + c.w / 2, y0 + 50, String(c.id), 't-labb halo-s', 'middle'); }
    else if (c.type === 'master') { T(g, x0, y0 + 27, 'Master', 't-labb halo-s'); T(g, x0, y0 + 50, 'or spare', 't-labb halo-s'); }
    else if (c.type === 'pcie') T(g, x0, y0 + 30, 'PCIe', 't-labb halo-s');
    else if (c.type === 'io') { T(g, x0, y0 + 27, 'I/O', 't-labb halo-s'); T(g, x0, y0 + 50, 'Maxions', 't-sm halo-s'); }
  });
  // the mesh as a component, and the note on what is inferred
  const gm = comp(L, 'mesh', {}, 'The mesh: details');
 boxShape(gm, 0, DH + 9, 292, 30, 'var(--ink-2)', {fo: 0.06, rx: 15});
  T(gm, 14, DH + 31, `The mesh: ${N.grid86.t}, ${N.stops.t} stops`, 't-labb', 'start', 'mesh.grid');
  T(L, DW, DH + 31, 'orientation inferred; dashed parts also inferred', 't-sm', 'end', 'mesh.orientation L33 L32 L40 dram.pkg-pairing');
  FX[0] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}
function tileLabel(c) {
  if (c.type === 'cshire') return `Shire ${c.id}, compute shire. Enter for details; Enter again zooms in.`;
  if (c.type === 'memshire') return `Memory shire ${c.id}: details`;
  if (c.type === 'master') return `Master or spare shire (${c.r === 0 ? 'north' : 'south'} cell): details`;
  return (c.type === 'pcie' ? 'PCIe shire' : 'I/O shire') + ': details';
}

/* ---- a shire, zoomed in: a logical block diagram (no floorplan of the inside is published; fact L114) ---- */
function buildShire(sid) {
  const L = LAYERS[1]; L.textContent = ''; AP[1] = {min: {}, bank: [], lane: []};
  const P = AP[1], cell = SH[sid], X = SF.x, Y = SF.y, W = SF.w;
  const fr = E('g', {}, L);
  S(E('rect', {x: X, y: Y, width: W, height: W, rx: 22}, fr), {fill: 'var(--c1)', fillOpacity: 0.05, stroke: 'var(--c1)', strokeWidth: 3});
  T(fr, X + 22, Y + 40, `Shire ${sid}`, 't-big');
  T(fr, X + W - 22, Y + 38, `map (${cell.lx}, ${cell.ly}) · ${N.per_shire.t}`, 't-sm', 'end', 'mesh.logical-map shire.composition');
  // mesh neighbours, in die orientation
  const nb = [[-1, 0, 'N'], [1, 0, 'S'], [0, -1, 'W'], [0, 1, 'E']].map(([dr, dc, s]) => [BYDIE[(cell.r + dr) + ',' + (cell.c + dc)], s]);
  nb.forEach(([c, s]) => {
    const st = {stroke: 'var(--axis)', strokeWidth: 5, strokeLinecap: 'round'};
    const lab = c ? cellName(c) : 'die edge';
    if (s === 'N') { if (c) S(E('line', {x1: X + W / 2, y1: Y, x2: X + W / 2, y2: Y - 24}, fr), st); T(fr, X + W / 2 + 12, Y - 18, (c ? '↑ ' : '') + lab, 't-sm'); }
    if (s === 'S') { if (c) S(E('line', {x1: X + W / 2, y1: Y + W, x2: X + W / 2, y2: Y + W + 24}, fr), st); T(fr, X + W / 2 + 12, Y + W + 30, (c ? '↓ ' : '') + lab, 't-sm'); }
    if (s === 'W') { if (c) S(E('line', {x1: X, y1: Y + W / 2, x2: X - 24, y2: Y + W / 2}, fr), st); T(fr, X - 30, Y + W / 2 + 6, lab + (c ? ' ←' : ''), 't-sm', 'end'); }
    if (s === 'E') { if (c) S(E('line', {x1: X + W, y1: Y + W / 2, x2: X + W + 24, y2: Y + W / 2}, fr), st); T(fr, X + W + 30, Y + W / 2 + 6, (c ? '→ ' : '') + lab, 't-sm'); }
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
    P.bank[i] = {x: bx + bw / 2, y: by + 54};
  }
  const gu = comp(L, 'uc', {}, 'UC block: barriers, credits and atomics: details');
  boxShape(gu, X + 530, Y + 134, W - 550, 108, 'var(--c7)', {fo: 0.1});
  T(gu, X + 544, Y + 164, 'UC block', 't-labb');
  T(gu, X + 544, Y + 190, 'barriers,', 't-sm'); T(gu, X + 544, Y + 210, 'credits, atomics', 't-sm');
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
      const p = pos[m], g = comp(G, 'minion', {sid, nb: k, mi: m}, `Minion ${m} of neighbourhood ${k}: details; Enter again zooms in`);
      boxShape(g, p.x, p.y, p.w, p.h, 'var(--c1)', {fo: 0.22, rx: 6});
      T(g, p.x + p.w / 2, p.y + 30, 'M' + m, 't-labb', 'middle');
      P.min[k + ':' + m] = p;
    }
    // tree edges of the fast local network, drawn over the minions' edges (fact L115)
    LAY.neighbourhood_floorplan.fast_tree_edges.forEach(([a, b]) => {
      const A = pos[a], B = pos[b], hz = A.y === B.y, s1 = A.x < B.x || A.y < B.y ? A : B, s2 = s1 === A ? B : A;
      const q = hz ? {x1: s1.x + s1.w - 10, y1: s1.y + s1.h / 2, x2: s2.x + 10, y2: s2.y + s2.h / 2} : {x1: s1.x + s1.w / 2, y1: s1.y + s1.h - 9, x2: s2.x + s2.w / 2, y2: s2.y + 9};
      S(E('line', Object.assign(q, {'pointer-events': 'none'}), G), {stroke: 'var(--c4)', strokeWidth: 7, strokeLinecap: 'round'});
    });
    P['ch' + k] = {x: nx + nw / 2, y: ny + 6};
  }
  FX[1] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}

/* ---- a minion, zoomed in ---- */
function buildMinion(sid, nb, mi) {
  const L = LAYERS[2]; L.textContent = ''; AP[2] = {};
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
      S(E('rect', {x: rx, y: ry, width: 32, height: 21, rx: 3, 'pointer-events': 'none'}, g), {fill: 'var(--c1)', fillOpacity: 0.25, stroke: 'var(--c1)', strokeWidth: 1});
    }
    T(g, X + 40, hy + 214, `f0–f31, ${N.vreg256.t}`, 't-sm', 'start', 'minion.vpu');
    P['hart' + t] = {x: X + 184, y: hy + 130};
  });
  // integer pipeline (the core itself)
  const gi = comp(L, 'minion', {}, 'The minion core: details');
  boxShape(gi, X + 364, Y + 70, 410, 84, 'var(--ink-2)', {fo: 0.07});
  T(gi, X + 380, Y + 104, 'Integer pipeline', 't-mid');
  T(gi, X + 380, Y + 136, 'RV64IMFC · in-order · single issue', 't-sm', 'start', 'minion.isa');
  // vector unit: its 8 lanes hold the FMA and int8 multiply-add units that the tensor instructions also run on
  const gv = comp(L, 'vpu', {}, 'Vector unit: details');
  boxShape(gv, X + 364, Y + 166, 410, 372, 'var(--c3)', {fo: 0.08});
  T(gv, X + 380, Y + 200, `Vector unit · ${N.lanes_n.t} lanes`, 't-mid', 'start', 'minion.vpu');
  const lw = (410 - 24 - 7 * 6) / 8, UN = ['FMA', 'IMA', 'IMA', 'INT', 'TR'];
  for (let l = 0; l < 8; l++) {
    const lx = X + 376 + l * (lw + 6);
    T(gv, lx + lw / 2, Y + 230, String(l), 't-sm', 'middle');
    UN.forEach((u, k) => {
      const uy = Y + 238 + k * 46;
      S(E('rect', {x: lx, y: uy, width: lw, height: 40, rx: 4, 'pointer-events': 'none'}, gv), {fill: 'var(--c3)', fillOpacity: k < 3 ? 0.3 : 0.14, stroke: 'var(--c3)', strokeWidth: 1.2});
      T(gv, lx + lw / 2, uy + 26, u, 't-sm', 'middle');
    });
  }
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
  // the arrow into the lanes: the tensor work runs there
  const ay = Y + 250;
  S(E('line', {x1: tx + 46, y1: ay, x2: X + 774, y2: ay, 'pointer-events': 'none'}, gt), {stroke: 'var(--c2)', strokeWidth: 6, strokeLinecap: 'round'});
  S(E('polygon', {points: `${X + 760},${ay} ${X + 778},${ay - 11} ${X + 778},${ay + 11}`, 'pointer-events': 'none'}, gt), {fill: 'var(--c2)'});
  T(gt, tx + 56, ay + 6, 'runs on the 8 VPU lanes', 't-sm', 'start', 'minion.vec-peak');
  [['TenB', 0, '(logical)'], ['TenC', 1, '']].forEach(([nm, i, q]) => {
    const bx = tx + 16 + i * ((tw - 32) / 2 + 4);
    S(E('rect', {x: bx, y: Y + 286, width: (tw - 40) / 2, height: 84, rx: 8, 'pointer-events': 'none'}, gt), {fill: 'var(--c2)', fillOpacity: 0.1, stroke: 'var(--c2)', strokeWidth: 1.5});
    T(gt, bx + 12, Y + 314, nm, 't-labb');
    T(gt, bx + 12, Y + 338, N.tenb.t, 't-sm', 'start', 'minion.tenb-tenc');
    if (q) T(gt, bx + 12, Y + 360, q, 't-sm', 'start', 'minion.tenb-tenc');
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
  P.l1h0 = {x: sx(12) + sw + 2, y: sy + 32};
  // ports
  const ge = comp(L, 'etlink', {}, 'ET-Link port: details');
  boxShape(ge, tx, Y + 552, tw, 96, 'var(--ink-2)', {fo: 0.07});
  T(ge, tx + 16, Y + 582, 'ET-Link port', 't-labb');
  T(ge, tx + 16, Y + 607, `to the shire cache: ${N.etl_min.t},`, 't-sm', 'start', 'minion.etlink-width');
  T(ge, tx + 16, Y + 630, `onto a shared ${N.etl512.t.replace(' ET-Link bus', '')} bus`, 't-sm', 'start', 'shire.neigh-link');
  P.etl = {x: tx + tw - 30, y: Y + 596};
  const gf = comp(L, 'fln', {}, 'Fast local network: details');
  boxShape(gf, tx, Y + 658, tw, 80, 'var(--c4)', {fo: 0.1});
  T(gf, tx + 16, Y + 690, 'Fast local network', 't-labb');
  T(gf, tx + 16, Y + 716, `${N.ts_fln.t} round trip on tree edges`, 't-sm', 'start', 'ts-rt-fln');
  FX[2] = E('g', {class: 'fx', 'pointer-events': 'none'}, L);
}

/* ================= zoom ================= */
const Z = {level: 0, sid: null, nb: 0, mi: 0};
const lerp = (a, b, t) => a + (b - a) * t;
const lerpR = (A, B, t) => ({x: lerp(A.x, B.x, t), y: lerp(A.y, B.y, t), w: lerp(A.w, B.w, t), h: lerp(A.h, B.h, t)});
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const band = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rmap = (A, B) => { const k = B.w / A.w; return [k, B.x - k * A.x, B.y - k * A.y]; };
const setT = (g, m) => { if (m) g.setAttribute('transform', `matrix(${m[0]},0,0,${m[0]},${m[1]},${m[2]})`); else g.removeAttribute('transform'); };
function realTween(ms, fn) {
  return new Promise(res => {
    let done = false;
    const fin = () => { if (!done) { done = true; fn(1); res(); } };
    if (REDUCED || ms <= 0) return fin();
    const t0 = performance.now();
    const f = now => { if (done) return; const p = Math.min(1, (now - t0) / ms); if (p >= 1) fin(); else { fn(p); requestAnimationFrame(f); } };
    requestAnimationFrame(f);
    setTimeout(fin, ms + 600);   // a hidden tab gets no frames
  });
}
const tileRect = sid => { const c = SH[sid]; return {x: c.x + INS, y: c.y + INS, w: c.w - 2 * INS, h: c.h - 2 * INS}; };
const minRect = (nb, mi) => { const p = AP[1].min[nb + ':' + mi]; return {x: p.x, y: p.y, w: p.w, h: p.h}; };
async function zoomStep(dir, A, ms) {
  const lo = dir > 0 ? Z.level : Z.level - 1, outer = LAYERS[lo], inner = LAYERS[lo + 1], B = lo === 0 ? SF : MF;
  outer.style.display = ''; inner.style.display = '';
  LAYERS.forEach(l => l.classList.add('busy'));
  await realTween(ms, p => {
    const e = ease(dir > 0 ? p : 1 - p), R = lerpR(A, B, e);
    setT(outer, rmap(A, R)); setT(inner, rmap(B, R));
    outer.style.opacity = 1 - band(e, 0.3, 0.85); inner.style.opacity = band(e, 0.12, 0.7);
  });
  LAYERS.forEach(l => l.classList.remove('busy'));
  if (dir > 0) { outer.style.display = 'none'; setT(inner, null); inner.style.opacity = 1; Z.level = lo + 1; }
  else { inner.style.display = 'none'; setT(outer, null); outer.style.opacity = 1; Z.level = lo; }
}
/* Zooming follows the latest request only: rapid key presses never queue a chain of animations. goTo() resolves
   once the view reaches the latest target (a superseded caller's flow has been stopped by then). */
let ZT = null, ZW = false, ZWAIT = [];
const zkey = () => Z.level + ':' + Z.sid + ':' + Z.nb + ':' + Z.mi;
function goTo(t, o) {
  ZT = {t: {level: t.level || 0, sid: t.sid == null ? Z.sid : t.sid, nb: t.nb || 0, mi: t.mi || 0}, o: o || {}, n: ((ZT && ZT.n) || 0) + 1};
  return new Promise(res => { ZWAIT.push(res); if (!ZW) { ZW = true; zoomWorker(); } });
}
function nextStep(w) {
  if (Z.level === 2 && (w.level < 2 || Z.sid !== w.sid || Z.nb !== w.nb || Z.mi !== w.mi)) return ms => zoomStep(-1, minRect(Z.nb, Z.mi), ms);
  if (Z.level === 1 && (w.level < 1 || Z.sid !== w.sid)) return ms => zoomStep(-1, tileRect(Z.sid), ms);
  if (w.level >= 1 && Z.level === 0) return ms => { buildShire(w.sid); Z.sid = w.sid; return zoomStep(1, tileRect(w.sid), ms); };
  if (w.level === 2 && Z.level === 1) return ms => { buildMinion(w.sid, w.nb, w.mi); Z.nb = w.nb; Z.mi = w.mi; return zoomStep(1, minRect(w.nb, w.mi), ms); };
  return null;
}
async function zoomWorker() {
  const from = {level: Z.level, sid: Z.sid, nb: Z.nb, mi: Z.mi}, fromKey = zkey(), hadFocus = svg.contains(document.activeElement);
  let seen = ZT ? ZT.n : 0, wantFocus = false;
  try {
    for (let guard = 0; ZT && guard < 12; guard++) {
      if (ZT.o.focus) wantFocus = true;
      const st = nextStep(ZT.t); if (!st) break;
      clearFx();
      const rush = ZT.n !== seen || ZT.o.fast; seen = ZT.n;   // a newer request came in: hurry
      await st(rush ? 480 : 900);
    }
  } catch (e) { console.error(e); }
  ZT = null; ZW = false;
  if (fromKey !== zkey()) {
    select(null); crumbs();
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
function crumbs() {
  const c = $('crumbs'); c.textContent = '';
  const items = [['ET-SoC-1', {level: 0}]];
  if (Z.level >= 1) items.push([`Shire ${Z.sid}`, {level: 1, sid: Z.sid}]);
  if (Z.level === 2) items.push([`Minion ${Z.mi}, n'hood ${Z.nb}`, {level: 2, sid: Z.sid, nb: Z.nb, mi: Z.mi}]);
  items.forEach(([t, tg], i) => {
    if (i) { const s = document.createElement('span'); s.className = 'sep'; s.textContent = '›'; c.appendChild(s); }
    const last = i === items.length - 1, b = document.createElement(last ? 'span' : 'button');
    b.className = 'crumb'; b.textContent = t;
    if (last) b.setAttribute('aria-current', 'true');
    else { b.type = 'button'; b.addEventListener('click', () => { const sid = Z.sid; endTour(); haltFlow(); goTo(tg, {focus: true}); showComp(i === 0 ? 'chip' : 'cshire', i === 0 ? {} : {cell: SH[sid]}); }); }
    c.appendChild(b);
  });
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
    what: `Esperanto's ET-SoC-1 has ${n('cores')} RISC-V cores on one ${n('die_mm2')} mm² die in TSMC ${n('process')}: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor. ${n('cshires')} compute shires run the kernels, at ${n('mhz')} on the lab's cards. The fp32 matmul that sustains ${n('tflops')} TFLOP/s draws ${n('mmw')} at the board across the three cards (die ${n('mmtemp')}); how much of that is idle power depends on the card and its temperature.`,
    kpis: [K('cores', 'RISC-V cores'), kpi(n('tflops'), 'TFLOP/s fp32, three cards'), kpi(n('mmw'), 'board power in that matmul'), kpi(n('perw'), 'GFLOP/s per board watt')]}),
  cshire: ctx => { const c = ctx.cell, hi = homeInfo(c);
    return {kick: 'Compute shire', title: `Shire ${c.id}`,
      what: `One of the ${n('cshires')} compute shires: ${n('neigh')} of ${n('per_neigh')}, ${n('cache_mb')} of SRAM and one mesh stop. On the measured map it sits at (${c.lx}, ${c.ly}); on this die view, row ${c.r}, column ${c.c} (the map is transposed onto the die, an inferred orientation). Its L3 slice homes the lines with PA[10:6] = ${c.id}, which memory shire ${cn(hi.ms, 'L43 dram.memshire-select')} serves, ${cn(hi.h, 'mesh.logical-map L40')} ${hi.h === 1 ? 'hop' : 'hops'} away.`,
      kpis: [kpi(cn(hi.mean, 'mesh.logical-map l3.home', 2), `mean hops to the ${n('cshires')} L3 slices`), kpi(cn(V('lat_l3_a') + V('lat_l3_b') * hi.mean, 'l3.latency mesh.logical-map', 0), 'L3 hit from here by the model, cycles'), K('flb', 'shire barrier, 32 minions')],
      act: Z.level === 0 ? `<button type="button" class="st-btn" data-act="zoom" data-sid="${c.id}">Zoom into shire ${c.id}</button><span class="small">or click it again</span>` : ''};
  },
  master: ctx => ({kick: 'Master or spare shire', title: 'Master or spare',
    what: `One of the four grey cells of the measured map. It holds the master shire (shire ${n('master_id')}, whose firmware schedules kernels) or the spare (shire ${n('spare_id')}); which of the two cells is which was never measured. The ${ctx.cell.r === 0 ? 'north' : 'south'} cell is highlighted.`,
    kpis: [K('mask', 'compute mask on every card'), K('cshires', 'compute shires')]}),
  pcie: () => ({kick: 'PCIe shire', title: 'PCIe shire',
    what: `Two PCIe controllers and an ${n('pcie_lanes')} Gen4 PHY: the chip's link to the host. ${n('pcie_gbs')} per direction is the Gen4 x8 figure; host transfers were not timed on these cards. The two sources that place it disagree on whether PCIe or I/O is further east.`,
    kpis: [K('pcie_gbs', 'per direction (link figure)')]}),
  io: () => ({kick: 'I/O shire', title: 'I/O shire',
    what: `The ${n('maxions')} (out-of-order RISC-V cores) with their own cache, the service processor that boots the chip and runs the power and clock governor, a root of trust and the peripherals. Its cell is inferred.`,
    kpis: [K('maxions', 'in the I/O shire')]}),
  memshire: ctx => { const m = ctx.cell.id, pos = LAY.memshires[m];
    return {kick: 'Memory shire', title: `Memory shire ${m}`,
      what: `Drives ${n('ch16')}. It serves the lines whose PA[8:6] = ${m}: those homed in L3 slices ${src(`${m}, ${m + 8}, ${m + 16} and ${m + 24}`, 'L43')} (checked on three cards). Its place, (${pos.pos[0]}, ${pos.pos[1]}) on the map and the ${pos.die.side} side on the die, comes from a fit of DRAM latencies on aifoundry2; left as fitted, the model with these places is within ±3 cycles for ${n('ms_fit')} of loads on all three cards.${pos.tie_break ? ` This one's fit ties three places, but ${src('one is an empty corner of the grid and one lies off it', 'ms2-forced L42 mesh.grid')}, so this is the only place left.` : ''}`,
      kpis: [kpi(`${n('lat_ms_a')} + ${n('lat_ms_b')}`, 'cycles past the L3, per hop from the home shire'), K('ms_fit', 'of loads within ±3 cycles, three cards'), K('lat_dram_chip', 'cycles of them the DRAM chip (inferred)')]};
  },
  dram: ctx => ({kick: 'Memory', title: 'LPDDR4X',
    what: `${n('channels')} channels of ${n('ch_bits')}, ${n('dram_gb')} on these cards, run at ${n('mts')} MT/s: ${n('dram_peak')} GB/s peak, and the chip streams ${n('dram_bw')} GB/s. Each package holds ${n('pkg_ch')} and serves two memory shires; which two is not documented, so the drawing's pairing of neighbours${ctx.ms ? ` (memory shires ${ctx.ms.join(' and ')} here)` : ''} is ${src('inferred', 'dram.pkg-pairing L23 L47')}.`,
    kpis: [kpi(n('dram_bw', 'GB/s'), 'measured stream'), kpi(n('lat_dram'), 'cycles, a typical load'), kpi(n('e_dram', 'pJ/B'), `to read a byte, above idle (${n('e_dram_rng')} over passes)`), K('dram_gb', 'on the card')]}),
  mesh: () => ({kick: 'Network on chip', title: 'The mesh',
    what: `An ${n('grid86')} grid of ${n('stops')} stops joins the shires. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. It runs at ${n('noc_mhz')} and ${n('noc_v')} on aifoundry2. Routes are shortest paths; whether x or y goes first was not measured. The flows draw every leg, replies included, on its own route: x first on the measured map, and y first where x first would cross an empty corner (some legs from a memory shire).`,
    kpis: [K('hop_cyc', 'per hop, round trip'), K('hop_mm', 'per hop (die plot)'), kpi(n('bitmm'), 'per bit and mm, free links')]}),
  host: () => ({kick: 'Host', title: 'Host and PCIe',
    what: `The card sits in a PCIe slot of the host; the link is Gen4 x8, ${n('pcie_gbs')} per direction by the link's figure. Host transfers were never timed on these cards.`,
    kpis: [K('pcie_gbs', 'per direction, not measured')]}),
  meshstop: () => ({kick: 'Shire', title: 'Mesh stop',
    what: `The shire's single attach point to the mesh: minion 31 sees the same round trips as minion 0. A shire has ${n('lanes4')}; a line takes lane PA[7:6], and the port is ${n('port512')} wide.`,
    kpis: [K('hop_cyc', 'per hop, round trip')]}),
  banks: ctx => ({kick: 'Shire cache' + (ctx.bank != null ? ` · bank ${ctx.bank}` : ''), title: 'Shire cache',
    what: `${n('bank1mb')}, each of ${n('subbanks')}. In mode M0, the reset mode and the one these cards run, it holds ${n('scp_mb')} of scratchpad, ${n('l2_kb')} of L2 and a ${n('l3_mb')} slice of the chip's L3. A line's L2 bank is PA[7:6].`,
    kpis: [K('cache_mb', 'SRAM per shire'), kpi(n('lat_l2'), 'cycles, an L2 hit')]}),
  l2: () => ({kick: 'Shire cache', title: 'L2',
    what: `${n('l2_kb')}, private to the shire's ${n('per_shire')}. A hit takes ${n('lat_l2')} cycles (${n('lat_rb')} from the read buffer); the chip streams ${n('bw_l2')} TB/s from L2 at about ${n('e_l2')} pJ per byte (${n('e_l2_rng')} pass to pass).`,
    kpis: [kpi(n('lat_l2'), 'cycles'), kpi(n('bw_l2', 'TB/s'), 'chip-wide'), kpi(n('e_l2', 'pJ/B'), `above idle (${n('e_l2_rng')} over passes)`)]}),
  l3: () => ({kick: 'Shire cache', title: 'L3 slice',
    what: `A ${n('l3_mb')} slice of the chip's ${n('l3_chip')} L3. Lines rotate over the ${n('cshires')} slices by PA[10:6], so a line's home is usually another shire: a hit costs ${n('lat_l3_a')} + ${n('lat_l3_b')} between requester and home, ${n('lat_l3_avg')} cycles averaged over the slices.`,
    kpis: [kpi(n('lat_l3_avg'), 'cycles, average'), kpi(n('bw_l3', 'TB/s'), 'chip-wide'), kpi(n('e_l3', 'pJ/B'), `above idle (${n('e_l3_rng')} over passes)`)]}),
  scp: () => ({kick: 'Shire cache', title: 'Scratchpad',
    what: `${n('scp_mb')} that any shire can address at ${n('scp_base')}. From its own shire it is as fast as the L2 (${n('lat_scp')} cycles, ${n('bw_scp')} TB/s); from another shire it costs ${n('lat_rs_a')} + ${n('lat_rs_b')} cycles per hop, and with every shire reading one ${n('rs_hops')} away on average the chip gets ${n('bw_rs')} TB/s at ${n('e_rs0')}–${n('e_rs1')} pJ/B.`,
    kpis: [kpi(n('lat_scp'), 'cycles, own shire'), kpi(`${n('lat_rs_a')} + ${n('lat_rs_b')}`, 'cycles per hop, another shire'), kpi(`${n('e_scp0')}–${n('e_scp1')}`, 'pJ/B own (zeros to random)')]}),
  uc: () => ({kick: 'Shire', title: 'UC block',
    what: `The shire's uncacheable block: fast local barriers, fast credit counters, inter-processor interrupts and global atomics. A barrier over the shire takes ${n('flb')}; a barrier over all ${n('n1024')} minions built from these barriers, global atomics and credits takes ${n('chipbar', 'cycles')}. One contended global atomic retires every ${n('hot10')} (aifoundry2).`,
    kpis: [K('flb', 'shire barrier'), kpi(n('chipbar'), `cycles, chip barrier over ${n('n1024')} minions`)]}),
  xbar: () => ({kick: 'Shire', title: 'Crossbar',
    what: `A full crossbar joins the four neighbourhoods to the four banks and the UC block over ${n('xbar512')} ET-Link buses. A message between two minions that are not on a tree edge goes through it: ${n('ts_xbar')} cycles round trip, against ${n('ts_fln')} on a tree edge.`,
    kpis: [kpi(n('ts_xbar'), 'cycles, through the crossbar'), K('ts_fln', 'on a tree edge')]}),
  neigh: ctx => ({kick: 'Shire', title: `Neighbourhood ${ctx.nb != null ? ctx.nb : ''}`,
    what: `${n('per_neigh')} sharing a ${n('icache')} instruction cache, in two columns of four either side of a channel. Minions talk fastest along the reduction tree's ${n('fln7')} edges (${n('edges')}): ${n('ts_fln')} round trip, against ${n('ts_xbar')} cycles for any other pair in the shire. The hardware allreduce (TensorReduce and TensorBroadcast) climbs this tree, then the crossbar and the mesh: ${n('ar1024')} over all ${n('n1024')} minions.`,
    kpis: [K('ts_fln', 'round trip, tree edge'), kpi(n('ts_xbar'), 'cycles, any other pair'), kpi(n('ar1024'), `allreduce over ${n('n1024')} minions`)]}),
  minion: ctx => { const at1 = ctx.mi != null, sid = at1 ? ctx.sid : Z.sid, nb = at1 ? ctx.nb : Z.nb, mi = at1 ? ctx.mi : Z.mi, h0 = sid * 64 + (nb * 8 + mi) * 2;
    return {kick: 'Minion', title: `Minion ${mi} · neighbourhood ${nb}`,
      what: `A dual-threaded (${n('harts')}), in-order, single-issue RV64IMFC core with a vector unit of ${n('lanes')}, whose FMA and int8 multiply-add units also run the tensor instructions (a sequencer in the vector unit drives them), and a ${n('l1_kb')} L1 data cache. Its harts are ${cn(h0, 'chip.harts', 0)} and ${cn(h0 + 1, 'chip.harts', 0)}. An awake minion costs ${n('awake')}.`,
      kpis: [kpi(n('vecpeak'), 'per cycle, fp32 peak, vector or tensor'), K('awake', 'awake, one hart')],
      act: at1 && Z.level === 1 ? `<button type="button" class="st-btn" data-act="zoomm" data-nb="${nb}" data-mi="${mi}">Zoom into minion ${mi}</button><span class="small">or click it again</span>` : ''};
  },
  hart: ctx => ({kick: 'Minion', title: `Hart ${ctx.t}`,
    what: ctx.t === 0 ? `Hart 0 may issue every tensor instruction. Each hart has ${n('vregs')} (f0–f31).`
      : `Hart 1 may issue only TensorLoadL2Scp, TensorWait and tensor_coop CSR accesses; any other tensor instruction raises an illegal-instruction exception. On read-buffer and L2 hits, ${n('h1pen')} cycles than hart 0. Each hart has ${n('vregs')}.`,
    kpis: [K('harts', 'per minion')]}),
  vpu: () => ({kick: 'Minion', title: 'Vector unit',
    what: `${n('lanes')} in lockstep. Each lane has an FMA unit, two int8 multiply-add units, an integer unit and a transcendental unit (exp2, log2, reciprocal). The tensor instructions run on these same lanes, driven by state machines in the vector unit, so the fp32 peak is ${n('vecpeak')} per cycle either way. An ${n('lanes_n')}-lane fmadd.ps costs ${n('e_fmadd')} pJ on random data.`,
    kpis: [kpi(n('vecpeak'), 'per cycle, fp32, vector or tensor'), kpi(n('e_fmadd', 'pJ'), 'fmadd.ps, random data')]}),
  tensor: () => ({kick: 'Minion', title: 'Tensor sequencer',
    what: `TensorFMA and TensorIMA add no compute unit of their own: ${src('state machines in the vector unit run them on its lanes', 'minion.vec-peak')} (${n('lanes')}), on each lane's FMA and int8 multiply-add units, with operands from the L1 scratchpad and TenB. At peak that is ${n('peak32')}, ${n('peak16')} or ${n('peak8')} operations per cycle, the lanes' own peak. All ${n('n1024')} minions sustain ${n('tflops')} TFLOP/s fp32, ${n('tflops16')} fp16 and ${n('tops8')} TOP/s int8, at about ${n('e_mac32')} pJ per fp32 multiply-add (${n('e_mac32_rng')} over passes).`,
    kpis: [kpi(n('tflops'), 'TFLOP/s fp32, chip'), kpi(n('e_mac32'), `pJ per fp32 MAC (${n('e_mac32_rng')} over passes)`)]}),
  l1d: () => ({kick: 'Minion', title: 'L1 data cache',
    what: `${n('l1_kb')} (${n('l1geom')}), private and not coherent. Before each launch the firmware makes ${n('l1_scp')} of it a tensor scratchpad and leaves each hart ${n('l1_hart')}. A hit takes ${n('lat_l1')} cycles and costs ${n('e_l1')} pJ per byte.`,
    kpis: [kpi(n('lat_l1'), 'cycles, a hit'), kpi(n('e_l1', 'pJ/B'), 'above idle'), kpi(n('bw_l1b', 'TB/s'), 'chip-wide, unrolled loop')]}),
  l1scp: () => ({kick: 'Minion', title: 'L1 tensor scratchpad',
    what: `${n('l1_scp')} of the L1 (${n('sets011')}): TensorLoad writes rows here and TensorFMA reads its A operand from it.`,
    kpis: [K('l1_scp', 'per minion')]}),
  etlink: () => ({kick: 'Minion', title: 'ET-Link port',
    what: `The minion's own request and response interfaces are ${n('etl_min')} wide. The ${n('per_neigh')} of a neighbourhood share one ${n('etl512')} to the shire cache, after the neighbourhood up-converts their requests; responses come back over a ${n('etl256')}. An L1 miss goes out here to the L2 bank chosen by PA[7:6].`,
    kpis: [K('lat_l2', 'to an L2 hit')]}),
  fln: () => ({kick: 'Minion', title: 'Fast local network',
    what: `Joins the minions of a neighbourhood along the reduction tree (${n('edges')}). A ${n('b32')} TensorSend round trip takes ${n('ts_fln')} on these edges. The hardware allreduce (TensorReduce and TensorBroadcast) climbs this tree, then the crossbar and the mesh: ${n('ar1024')} over all ${n('n1024')} minions.`,
    kpis: [K('ts_fln', 'round trip, tree edge'), kpi(n('ar1024'), `allreduce over ${n('n1024')} minions`)]}),
};
function showComp(key, ctx) {
  const d = COMPS[key](ctx || {}), ids = COMPF[key] || [];
  panel(`<p class="pn-kick">${esc(d.kick)}</p><p class="pn-title">${esc(d.title)}</p><p class="pn-what">${d.what}</p>`
    + (d.kpis ? `<div class="pn-kpis">${d.kpis.join('')}</div>` : '') + (d.act ? `<div class="pn-act">${d.act}</div>` : '')
    + topPage(ids) + factsBlock(key));
}
function activate(g) {
  const key = g._key, ctx = g._ctx;
  const zoomS = key === 'cshire' && Z.level === 0, zoomM = key === 'minion' && Z.level === 1 && ctx.mi != null;
  if ((zoomS || zoomM) && SEL === g) {
    endTour(); haltFlow();
    if (zoomS) goTo({level: 1, sid: ctx.cell.id}); else goTo({level: 2, sid: Z.sid, nb: ctx.nb, mi: ctx.mi});
    return;
  }
  select(g); showComp(key, ctx);
}
svg.addEventListener('click', e => { const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) activate(g); });
svg.addEventListener('keydown', e => {
  const g = e.target.closest && e.target.closest('.comp');
  if (g && (e.key === 'Enter' || (e.key === ' ' && !TOUR && !flowRunning()))) { e.preventDefault(); e.stopPropagation(); activate(g); }
});
$('pn-body').addEventListener('click', e => {
  const b = e.target.closest('button[data-act]'); if (!b) return;
  if (b.dataset.act === 'zoom' || b.dataset.act === 'zoomm') {
    endTour(); haltFlow();
    if (b.dataset.act === 'zoom') goTo({level: 1, sid: +b.dataset.sid}, {focus: true});
    else goTo({level: 2, sid: Z.sid, nb: +b.dataset.nb, mi: +b.dataset.mi}, {focus: true});
  } else if (ACTS[b.dataset.act]) { endTour(); ACTS[b.dataset.act](b); }
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

/* ================= animation clock (pausable) ================= */
const CLK = {t: 0, on: true, last: 0, jobs: new Set()};
(function loop(now) {
  const dt = CLK.last ? Math.min(80, now - CLK.last) : 0; CLK.last = now;
  if (CLK.on) CLK.t += dt;
  CLK.jobs.forEach(j => { try { j(); } catch (e) { CLK.jobs.delete(j); console.error(e); } });
  requestAnimationFrame(loop);
})(0);
const CANCEL = new Error('cancelled');
let RUN = {dead: true};
const alive = tok => { if (tok.dead) throw CANCEL; };
function wait(tok, ms) {
  return new Promise((res, rej) => {
    if (tok.dead) return rej(CANCEL);
    const t0 = CLK.t, j = () => { if (tok.dead) { CLK.jobs.delete(j); rej(CANCEL); } else if (CLK.t - t0 >= ms) { CLK.jobs.delete(j); res(); } };
    CLK.jobs.add(j);
  });
}
/* with reduced motion, an animation draws its end state at once and then waits out its time */
function anim(tok, ms, fn) {
  if (REDUCED && !tok.dead) { fn(1); return wait(tok, ms); }
  return new Promise((res, rej) => {
    if (tok.dead) return rej(CANCEL);
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

function packet(fx, col, r) {
  r = r || 11;
  const g = E('g', {class: 'pk'}, fx);
  S(E('circle', {r: r + 8}, g), {fill: col, fillOpacity: 0.28});
  S(E('circle', {r}, g), {fill: col, stroke: 'var(--page)', strokeWidth: 3});
  return g;
}
const at = (g, p) => g.setAttribute('transform', `translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`);
/* move a packet along a polyline, the same time for every segment (a mesh hop costs the same everywhere) */
async function travel(tok, fx, pk, P, ms, o) {
  o = o || {};
  const trail = o.trail === false ? null : S(E('path', {fill: 'none'}, fx), {stroke: o.col || 'var(--c2)', strokeWidth: o.w || 7, strokeLinecap: 'round', strokeLinejoin: 'round', strokeOpacity: 0.75, strokeDasharray: o.dash ? '2 13' : null});
  if (trail) fx.insertBefore(trail, fx.firstChild);
  const nseg = Math.max(1, P.length - 1);
  const upto = q => {
    const s = q * nseg, i = Math.min(nseg - 1, Math.floor(s)), f = Math.min(1, s - i);
    let d = `M${P[0].x},${P[0].y}`; for (let k = 1; k <= i; k++) d += ` L${P[k].x},${P[k].y}`;
    const a = P[i], b = P[Math.min(i + 1, P.length - 1)], p = {x: lerp(a.x, b.x, f), y: lerp(a.y, b.y, f)};
    return [p, d + ` L${p.x},${p.y}`, s >= nseg ? nseg : i + (f >= 1 ? 1 : 0)];
  };
  let last = -1;
  const step = q => { const [p, d, si] = upto(q); at(pk, p); if (trail) trail.setAttribute('d', d); if (o.onSeg && si !== last) { last = si; o.onSeg(si, nseg); } };
  if (REDUCED) { step(1); await wait(tok, Math.min(ms, 450)); return trail; }
  await anim(tok, ms, step);
  return trail;
}
/* A labelled box. With o.cell it sits beside that tile (o.side 'l' or 'r') in the band below the tiles' id labels,
   so that it covers no tile's number; otherwise it sits on side o.side of (x, y). It goes under the packets. */
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
  let bx = o.side === 'l' ? x - 20 - bw : (o.side === 'u' || o.side === 'd') ? x - bw / 2 : x + 20;
  let by = o.side === 'u' ? y - 20 - bh : o.side === 'd' ? y + 20 : y - bh / 2;
  if (o.cell) {
    const c = o.cell;
    bx = o.side === 'l' ? c.x + 6 - bw : c.x + c.w - 6;
    by = Math.min(c.y + 58, c.y + c.h + 12 - bh);
  }
  bx = Math.max(VB.x + 4, Math.min(VB.x + VB.w - 4 - bw, bx)); by = Math.max(VB.y + 4, Math.min(VB.y + VB.h - 4 - bh, by));
  box.setAttribute('x', bx); box.setAttribute('y', by); box.setAttribute('width', bw); box.setAttribute('height', bh);
  tx.forEach((t, i) => { t.setAttribute('x', bx + pad); t.setAttribute('y', by + pad / 2 + (i + 1) * lh - lh * 0.24); });
  return g;
}
function pulse(tok, fx, p, ms, col, r1) {
  if (REDUCED) return wait(tok, ms);
  const c = S(E('circle', {cx: p.x, cy: p.y, r: 8}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 5});
  return anim(tok, ms, q => { c.setAttribute('r', 8 + (r1 || 46) * q); c.style.strokeOpacity = 1 - q * 0.85; }).then(() => c.remove(), e => { c.remove(); throw e; });
}
function ring(tok, fx, p, ms, col, label) {
  const R = 40, C = 2 * Math.PI * R;
  const bg = S(E('circle', {cx: p.x, cy: p.y, r: R}, fx), {fill: 'var(--surface)', fillOpacity: 0.85, stroke: 'var(--grid)', strokeWidth: 8});
  const c = S(E('circle', {cx: p.x, cy: p.y, r: R, transform: `rotate(-90 ${p.x} ${p.y})`}, fx), {fill: 'none', stroke: col || 'var(--c2)', strokeWidth: 8, strokeDasharray: `0 ${C}`});
  const t = label ? T(fx, p.x, p.y + 8, label, 't-labb', 'middle') : null;
  return anim(tok, ms, q => { c.style.strokeDasharray = `${C * q} ${C}`; }).then(() => [bg, c, t]);
}
function clearFx() { FX.forEach(f => { if (f) f.textContent = ''; }); svg.classList.remove('dimming', 'fdim'); svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi')); }
function hiCells(cells, dimOthers) { cells.forEach(c => c && c.g && c.g.classList.add('hi')); if (dimOthers) svg.classList.add('fdim'); }

/* ================= flows ================= */
const ST = {rq: 0, pa: null, pair: 0, gs: 'g'};
const P40 = 2 ** 32;
function mkPA(home, salt) { return 0x80 * P40 + salt * 2048 + home * 64; }   // a DRAM line (region 0x80_0000_0000) homed in L3 slice `home`
ST.pa = mkPA(13, 0x2468A);
function decode(pa) {
  const b = k => Math.floor(pa / 2 ** k);
  return {bank: b(6) % 4, home: b(6) % 32, ms: b(6) % 8, ch: b(9) % 2, db: b(10) % 8, row: b(18)};
}
function hex(pa) { const s = pa.toString(16).padStart(10, '0'); return '0x' + s.slice(0, 2) + '_' + s.slice(2, 6) + '_' + s.slice(6); }
const hopw = h => h === 1 ? 'hop' : 'hops';
const FLOWS = {}, FLOWTITLE = {A: 'Load to DRAM', B: 'Latency ladder', C: 'TensorSend', D: 'Relay', E: 'Gathers', F: 'Host and PCIe'};
let LASTFLOW = null, CAPFLOW = false;
function startFlow(k) {
  stopFlow(); const tok = RUN = {dead: false, k}; LASTFLOW = k;
  document.querySelectorAll('[data-flow]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.flow === k)));
  if (!TOUR) { setKick(`Flow ${'ABCDEF'.indexOf(k) + 1} · ${FLOWTITLE[k]}`); setCap(CAPS[k]()); sub(''); dots(-1); CAPFLOW = true; }
  CLK.on = true; playBtn();
  quiet(FLOWS[k](tok)).then(() => { if (RUN === tok) { tok.done = true; playBtn(); } });
}
function stopFlow() {
  RUN.dead = true; clearFx();
  document.querySelectorAll('[data-flow]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  playBtn();
}
/* stop a flow because the reader zoomed or went elsewhere: its caption goes too */
function haltFlow() { stopFlow(); if (!TOUR && CAPFLOW) resetCap(); }
const flowRunning = () => !RUN.dead && !RUN.done;
function sub(html) { $('cap-sub').innerHTML = html; }
const legRows = rows => `<table class="legs"><thead><tr><th>Leg</th><th>What happens</th><th class="num">cycles</th><th class="num">pJ/B</th></tr></thead><tbody>${rows.map((r, i) => `<tr class="todo" data-leg="${i}"><td>${r[0]}</td><td>${r[1]}</td><td class="num">${r[2] || ''}</td><td class="num">${r[3] || ''}</td></tr>`).join('')}</tbody></table>`;
function leg(i) {
  let on = null;
  document.querySelectorAll('#pn-body tr[data-leg]').forEach(tr => { const k = +tr.dataset.leg; tr.className = k < i ? '' : k === i ? 'on' : 'todo'; if (k === i) on = tr; });
  if (on) pnReveal(on);
}
function flowPanel(k, head, body) {
  panel(`<p class="pn-kick">Flow ${'ABCDEF'.indexOf(k) + 1} of 6</p><p class="pn-title">${esc(head)}</p>${body}` + topPage(COMPF['flow' + k]) + factsBlock('flow' + k, 'The facts this flow uses'));
}
const HOP_MS = 300;

/* ---- bars on the stage, in the free band right of the die (flows 2, 4 and 5), with 19-20 unit text ---- */
const BAND = {x: 932, y: 40, w: 172};
function bandChart(fx, title, rows, o) {
  o = o || {};
  const g = E('g', {class: 'band'}, fx);
  let y = o.y == null ? BAND.y : o.y;
  if (title) { T(g, BAND.x, y + 22, title, 't-labb halo'); y += 30; }
  if (o.note) { T(g, BAND.x, y + 18, o.note, 't-sm halo'); y += 26; }
  const out = rows.map(r => {
    T(g, BAND.x, y + 20, r.name, 't-lab halo', 'start', r.f).style.fontSize = '19px';
    S(E('rect', {x: BAND.x, y: y + 27, width: BAND.w, height: 30, rx: 5}, g), {fill: 'var(--grid)'});
    const bar = S(E('rect', {x: BAND.x, y: y + 27, width: 0, height: 30, rx: 5}, g), {fill: `color-mix(in srgb, ${r.col || 'var(--c2)'} 55%, transparent)`});
    const val = T(g, BAND.x + 7, y + 49, r.val || '', 't-labb', 'start', r.f);
    y += 68;
    return {bar, val, set: q => bar.setAttribute('width', (Math.max(0, Math.min(1, q)) * BAND.w).toFixed(1))};
  });
  return {g, rows: out, bottom: y};
}
/* a stream drawn as a pipe under its packets */
function pipe(fx, P, col, dash) {
  const d = 'M' + P.map(p => `${p.x},${p.y}`).join(' L');
  const e = S(E('path', {d, fill: 'none'}, fx), {stroke: col, strokeWidth: 9, strokeOpacity: 0.35, strokeLinecap: 'round', strokeLinejoin: 'round', strokeDasharray: dash ? '3 14' : null});
  fx.insertBefore(e, fx.firstChild);
  return e;
}

/* (a) a load that misses all the way to DRAM */
FLOWS.A = async tok => {
  const rq = ST.rq, a = decode(ST.pa), rc = SH[rq], hc = SH[a.home], mc = MSC[a.ms];
  const r1 = route(rc, hc), r2 = route(hc, mc), h1 = r1.length - 1, h2 = r2.length - 1;
  const l3 = V('lat_l3_a') + V('lat_l3_b') * h1, tot = l3 + V('lat_ms_a') + V('lat_ms_b') * h2;
  const opts = Object.keys(SH).map(Number).sort((x, y) => x - y).map(s => `<option value="${s}"${s === rq ? ' selected' : ''}>${s}</option>`).join('');
  flowPanel('A', 'A load that misses to DRAM',
    `<p class="pn-what">Hart 0 of minion 0 in shire ${rq} loads one ${n('line64')} line that no cache holds. Its physical address picks every stop:</p>`
    + `<p class="pn-what"><code data-f="addr.dram-region">${hex(ST.pa)}</code>: L2 bank PA[7:6] = ${a.bank} · L3 home PA[10:6] = shire ${a.home} · memory shire PA[8:6] = ${a.ms} · channel PA[9] = ${a.ch} · DRAM bank PA[12:10] = ${a.db}</p>`
    + `<div class="pn-act"><label>Requester shire <select data-sel="rq">${opts}</select></label><button type="button" class="st-btn" data-act="newpa">New address</button><button type="button" class="st-btn" data-act="replay">Replay</button></div>`
    + legRows([
      ['L1', `miss (a hit: ${n('lat_l1')})`, '', n('e_l1')],
      [`L2 bank ${a.bank}`, `miss (a hit: ${n('lat_l2')})`, '', n('e_l2')],
      [`L3 home, shire ${a.home}`, `${cn(h1, 'mesh.logical-map', 0)} ${hopw(h1)}: a hit would be ${n('lat_l3_a')} + ${n('l3_b12')}×${h1}`, cn(l3, 'l3.latency addr.load-model', 0), n('e_l3')],
      [`memory shire ${a.ms}`, `${cn(h2, 'mesh.logical-map L40', 0)} ${hopw(h2)} on: + ${n('lat_ms_a')} + ${n('lat_ms_b')}×${h2}`, cn(tot, 'addr.load-model L45', 0), ''],
      [`LPDDR4X, channel ${a.ch}`, `bank ${a.db}: ${n('lat_dram_chip')} cycles are the DRAM chip (inferred)`, '', n('e_dram')],
      [`back to shire ${rq}`, `the model's total; the reply's path is not established (drawn back through the L3 home); a typical measured load takes ${n('lat_dram')}`, cn(tot, 'addr.load-model L45', 0), ''],
    ]));
  hiCells([rc, hc, mc]);
  // leg 0: the minion
  await goTo({level: 2, sid: rq, nb: 0, mi: 0}, {fast: true}); alive(tok);
  leg(0); sub(`Leg 1 of 6 · hart 0 looks in its L1 data cache: a miss (a hit takes ${n('lat_l1')} cycles)`);
  let co = null;
  const say = (...a) => { if (co && co.parentNode) co.remove(); co = callout(...a); };
  const unsay = () => { if (co) co.remove(); co = null; };
  const P2 = AP[2]; let pk = packet(FX[2], 'var(--c2)', 13);
  await travel(tok, FX[2], pk, [P2.hart0, P2.l1h0], 800);
  say(FX[2], P2.l1h0.x, P2.l1h0.y - 70, [{t: 'L1: miss'}, {t: `a hit takes ${N.lat_l1.t} cycles`, f: 'lat-l1'}], {side: 'u'});
  await wait(tok, 1500);
  await travel(tok, FX[2], pk, [P2.l1h0, {x: P2.etl.x, y: P2.l1h0.y}, P2.etl], 700);
  // leg 1: the shire
  await goTo({level: 1, sid: rq}); alive(tok);
  leg(1); sub(`Leg 2 of 6 · over ET-Link to L2 bank ${a.bank} (PA[7:6]) in shire ${rq}: a miss (a hit takes ${n('lat_l2')} cycles)`);
  const P1 = AP[1], m0 = P1.min['0:0'], B = P1.bank[a.bank];
  pk = packet(FX[1], 'var(--c2)', 12);
  await travel(tok, FX[1], pk, [{x: m0.x + m0.w / 2, y: m0.y + m0.h / 2}, {x: P1.ch0.x, y: m0.y - 10}, P1.ch0, {x: P1.ch0.x, y: P1.xbarY}, {x: B.x, y: P1.xbarY}, B], 1300);
  say(FX[1], B.x, B.y, [{t: `L2 bank ${a.bank}: miss`}, {t: `a hit takes ${N.lat_l2.t} cycles`, f: 'lat-l2'}], {side: 'r'});
  await wait(tok, 1500);
  await travel(tok, FX[1], pk, [B, {x: B.x, y: P1.lane[a.bank].y + 30}, P1.lane[a.bank]], 700);
  // leg 2: over the mesh to the L3 home
  await goTo({level: 0}); alive(tok);
  hiCells([rc, hc, mc], true);
  leg(2); sub(`Leg 3 of 6 · to the L3 home, shire ${a.home} (PA[10:6]), ${h1} ${hopw(h1)}: a hit there would take ${n('lat_l3_a')} + ${n('l3_b12')} × ${h1} = ${cn(l3, 'l3.latency', 0)} cycles`);
  pk = packet(FX[0], 'var(--c2)', 13);
  const hopLab = T(FX[0], 0, 0, '', 't-labb halo');
  const hopper = base => (si, nseg) => { const p = base[Math.min(si, base.length - 1)]; hopLab.setAttribute('x', p.x + 16); hopLab.setAttribute('y', p.y - 18); hopLab.textContent = si ? `hop ${si}` : ''; };
  await travel(tok, FX[0], pk, pts(r1), HOP_MS * Math.max(1, h1), {onSeg: hopper(pts(r1))});
  hopLab.textContent = '';
  const side = c => c.c <= 3 ? 'r' : 'l';
  say(FX[0], hc.sx, hc.sy, [{t: `L3 home, shire ${a.home}: miss`}, {t: `${h1} ${hopw(h1)}; a hit: ${fnum(l3)} cycles`, f: 'l3.latency'}], {cell: hc, side: side(hc), fs: 21});
  await wait(tok, 1600); alive(tok);
  // leg 3: to the memory shire (the callout goes first, so that it never hides the packet)
  unsay();
  leg(3); sub(`Leg 4 of 6 · on to memory shire ${a.ms} (PA[8:6]), ${h2} ${hopw(h2)}: + ${n('lat_ms_a')} + ${n('lat_ms_b')} × ${h2} cycles`);
  await travel(tok, FX[0], pk, pts(r2), HOP_MS * Math.max(1, h2), {onSeg: hopper(pts(r2))});
  hopLab.textContent = '';
  say(FX[0], mc.sx, mc.sy, [{t: `Memory shire ${a.ms}`}, {t: `+ ${N.lat_ms_a.t} + ${N.lat_ms_b.t} × ${h2}`, f: 'dram.leg'}], {cell: mc, side: mc.c === 0 ? 'r' : 'l', fs: 21});
  await wait(tok, 1400); alive(tok);
  // leg 4: the DRAM chip
  unsay();
  leg(4); sub(`Leg 5 of 6 · channel ${a.ch} (PA[9]), bank ${a.db} (PA[12:10]): ${n('lat_dram_chip')} cycles of the load are the DRAM chip itself`);
  const pc = AP[0].pkg[a.ms + ':' + a.ch];
  await travel(tok, FX[0], pk, [{x: mc.sx, y: mc.sy}, {x: mc.sx, y: pc.y}, pc], 700);
  say(FX[0], pc.x, pc.y, [{t: `channel ${a.ch}, bank ${a.db}`}, {t: `${N.lat_dram_chip.t} cycles in DRAM`, f: 'lat-dram-chip'}], {side: 'd', fs: 22});
  await wait(tok, 1500); alive(tok);
  // leg 5: back, each leg on its own route: memory shire to the L3 home, the home to the requester
  unsay();
  leg(5); sub(`Leg 6 of 6 · back to shire ${rq}: ${cn(tot, 'addr.load-model L45', 0)} cycles (${cn(ns(tot), 'addr.load-model op-600', 0)} ns) by the model; a typical measured DRAM load takes ${n('lat_dram')} (${n('lat_dram_ns')})`);
  const back = [pc, {x: mc.sx, y: pc.y}].concat(pts(via(mc, hc, rc)));
  await travel(tok, FX[0], pk, back, HOP_MS * (h1 + h2 + 1), {col: 'var(--c7)', dash: true});
  say(FX[0], rc.sx, rc.sy, [{t: `${fnum(tot)} cycles, by the model`, f: 'addr.load-model'}, {t: `${N.lat_dram.t} typical, measured`, f: 'lat-dram-typical'}], {cell: rc, side: side(rc), fs: 21});
  leg(6);
};

/* (b) the same load hitting at each level: a latency ladder */
FLOWS.B = async tok => {
  const rq = ST.rq, a = decode(ST.pa), rc = SH[rq], hc = SH[a.home], mc = MSC[a.ms];
  const r1 = route(rc, hc), r2 = route(hc, mc), h1 = r1.length - 1, h2 = r2.length - 1;
  const l3 = V('lat_l3_a') + V('lat_l3_b') * h1, dram = l3 + V('lat_ms_a') + V('lat_ms_b') * h2, rs = V('lat_rs_a') + V('lat_rs_b') * h1;
  const pkg = AP[0].pkg[a.ms + ':' + a.ch];
  const rsHop = `${n('rs_hops')} mean`;
  const LV = [
    {nm: 'L1', sn: 'L1', cyc: V('lat_l1'), lab: n('lat_l1'), sv: N.lat_l1.t, e: n('e_l1'), bw: n('bw_l1b', 'TB/s'), say: `L1 hit: ${n('lat_l1')} cycles, inside the minion`},
    {nm: 'L2 read buffer', sn: 'L2 read buffer', cyc: V('lat_rb'), lab: n('lat_rb'), sv: N.lat_rb.t, e: '', bw: '', say: `L2 read buffer: ${n('lat_rb')} cycles`},
    {nm: 'L2', sn: 'L2', cyc: V('lat_l2'), lab: n('lat_l2'), sv: N.lat_l2.t, e: `${n('e_l2')} (${n('e_l2_rng')})`, bw: n('bw_l2', 'TB/s'), say: `L2 hit: ${n('lat_l2')} cycles, in the own shire`},
    {nm: 'own scratchpad', sn: 'own scratchpad', cyc: V('lat_scp'), lab: n('lat_scp'), sv: N.lat_scp.t, e: `${n('e_scp0')}–${n('e_scp1')}`, bw: n('bw_scp', 'TB/s'), say: `The shire's own scratchpad: ${n('lat_scp')} cycles, the same SRAM as the L2`},
    {nm: `scratchpad, shire ${a.home}`, sn: `scratchpad ${a.home}`, cyc: rs, lab: `${cn(rs, 'lat-scp-remote', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(rs)} · ${h1} ${hopw(h1)}`, tn: `another shire's scratchpad, ${rsHop}`, e: `${n('e_rs0')}–${n('e_rs1')}`, bw: n('bw_rs', 'TB/s'), back: route(hc, rc), path: r1, say: `Shire ${a.home}'s scratchpad, ${h1} ${hopw(h1)}: ${n('lat_rs_a')} + ${n('lat_rs_b')} × ${h1} = ${cn(rs, 'lat-scp-remote', 0)} cycles`},
    {nm: `L3, home ${a.home}`, sn: `L3, home ${a.home}`, cyc: l3, lab: `${cn(l3, 'l3.latency', 0)} · ${h1} ${hopw(h1)}`, sv: `${fnum(l3)} · ${h1} ${hopw(h1)}`, e: `${n('e_l3')} (${n('e_l3_rng')})`, bw: n('bw_l3', 'TB/s'), back: route(hc, rc), path: r1, say: `L3 hit in home shire ${a.home}, ${h1} ${hopw(h1)}: ${n('lat_l3_a')} + ${n('l3_b12')} × ${h1} = ${cn(l3, 'l3.latency', 0)} cycles (${n('lat_l3_avg')} averaged over slices)`},
    {nm: 'DRAM', sn: `DRAM, ${N.lat_dram.t} typical`, cyc: dram, lab: `${cn(dram, 'addr.load-model', 0)} model · ${n('lat_dram')} typ.`, sv: `${fnum(dram)} model`, e: `${n('e_dram')} (${n('e_dram_rng')})`, bw: n('dram_bw', 'GB/s'), path: r1.concat(r2.slice(1)), back: via(mc, hc, rc), dram: true, say: `DRAM through memory shire ${a.ms}: ${cn(dram, 'addr.load-model', 0)} cycles by the model; a typical measured load takes ${n('lat_dram')}`},
  ];
  const max = Math.max(dram, V('lat_dram'));
  flowPanel('B', 'The latency ladder',
    `<p class="pn-what">The same load from shire ${rq}, hitting at each level in turn. The L3 home and the scratchpad are ${h1} ${hopw(h1)} away in shire ${a.home}; memory shire ${a.ms} is ${h2} ${hopw(h2)} further. Bars are minion cycles at ${n('mhz')}.</p>`
    + `<div class="lad" id="lad">${LV.map((l, i) => `<div class="nm">${esc(l.nm)}</div><div class="tr" data-i="${i}"><u></u><s>${l.lab}</s></div>`).join('')}</div>`
    + `<table class="legs"><thead><tr><th>Level</th><th class="num">pJ/B</th><th class="num">chip-wide</th></tr></thead><tbody>${LV.map(l => `<tr><td>${l.tn || esc(l.nm)}</td><td class="num">${l.e}</td><td class="num">${l.bw}</td></tr>`).join('')}</tbody></table>`
    + `<p class="pn-what small">Another shire's scratchpad was measured with every shire reading the one 16 IDs away, ${n('rs_hops')} on average, not at the ${h1} ${hopw(h1)} of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches ${n('bw_l1', 'TB/s')}). Energies are above idle, with their range over passes in brackets.</p>`
    + `<div class="pn-act"><button type="button" class="st-btn" data-act="replay">Replay</button></div>`);
  await goTo({level: 0}); alive(tok);
  hiCells([rc, hc, mc], true);
  pnReveal($('lad'));
  const ch = bandChart(FX[0], 'Latency, cycles', LV.map(l => ({name: l.sn, val: l.sv, f: 'lat-l1 lat-l2 l3.latency addr.load-model lat-scp-remote'})));
  const CYC_MS = 11;
  for (let i = 0; i < LV.length; i++) {
    const l = LV[i], trk = document.querySelector(`#lad .tr[data-i="${i}"]`), bar = trk && trk.querySelector('u');
    sub(l.say);
    const dur = l.cyc * CYC_MS, grow = anim(tok, dur, q => { if (bar) bar.style.width = (100 * q * l.cyc / max).toFixed(2) + '%'; ch.rows[i].set(q * l.cyc / max); });
    if (!l.path) await Promise.all([grow, pulse(tok, FX[0], {x: rc.sx, y: rc.sy}, Math.max(dur, 240), 'var(--c2)', 20 + 30 * l.cyc / 47)]);
    else {
      const out = pts(l.path).concat(l.dram ? [{x: mc.sx, y: pkg.y}, pkg, {x: mc.sx, y: pkg.y}] : []), ret = pts(l.back).slice(1);
      const pk = packet(FX[0], 'var(--c2)', 11);
      await Promise.all([grow, travel(tok, FX[0], pk, out.concat(ret), dur, {w: 5})]);
      pk.remove();
    }
    if (trk) trk.classList.add('done');
    await wait(tok, 550);
    FX[0].querySelectorAll(':scope > path').forEach(p => p.remove());
  }
  sub(`From ${n('lat_l1')} cycles in L1 to about ${n('lat_dram')} in DRAM: ${cn(V('lat_dram') / V('lat_l1'), 'lat-l1 lat-dram-typical', 0)}× the latency`);
};

/* (c) TensorSend between shires */
const PAIRS = [[0, 24], [0, 13], [0, 31], [8, 23]];
FLOWS.C = async tok => {
  const rows = PAIRS.map(([s, d]) => { const h = hops(SH[s], SH[d]), c = V('ts_a') + V('ts_b') * h; return [s, d, h, c]; });
  flowPanel('C', 'TensorSend between shires',
    `<p class="pn-what">A hart sends ${n('b32')} of vector registers to a minion in another shire and waits for the reply. The round trip is ${n('ts_a')} cycles to leave and re-enter the shires plus ${n('ts_b')} per hop, on all three cards. The energy, measured with 1 KB messages, is ${n('ts_e_a')} to leave the shire plus ${n('ts_e_b', 'per mean hop')}.</p>`
    + `<table class="legs"><thead><tr><th>From → to</th><th class="num">hops</th><th class="num">cycles</th><th class="num">ns</th></tr></thead><tbody>${rows.map((r, i) => `<tr class="todo" data-leg="${i}"><td>shire ${r[0]} → ${r[1]}</td><td class="num">${cn(r[2], 'mesh.logical-map', 0)}</td><td class="num">${cn(r[3], 'ts-rt-mesh', 0)}</td><td class="num">${cn(ns(r[3]), 'ts-rt-mesh op-600', 0)}</td></tr>`).join('')}</tbody></table>`
    + `<p class="pn-what">Inside a shire the same round trip is ${n('ts_fln')} on a tree edge and ${n('ts_xbar')} cycles otherwise. The reply takes its own route, x first.</p>`);
  await goTo({level: 0}); alive(tok);
  const CYC_MS = 14;
  for (let k = 0; ; k++) {
    const i = (ST.pair + k) % PAIRS.length, [s, d, h, cyc] = rows[i], A = SH[s], B = SH[d];
    clearFx(); hiCells([A, B], true); leg(i);
    sub(`Shire ${s} → shire ${d}: ${h} ${hopw(h)} · ${n('ts_a')} + ${n('ts_b')} × ${h} = ${cn(cyc, 'ts-rt-mesh', 0)} cycles (${cn(ns(cyc), 'ts-rt-mesh op-600', 0)} ns) round trip`);
    const [bg, rc2, lt] = await ring(tok, FX[0], {x: A.sx, y: A.sy}, V('ts_a') * CYC_MS, 'var(--c4)', N.ts_a.t);
    [bg, rc2, lt].forEach(e => e && e.remove());
    const pk = packet(FX[0], 'var(--c2)', 12);
    await travel(tok, FX[0], pk, pts(route(A, B)), Math.max(1, V('ts_b') / 2 * h * CYC_MS));
    await travel(tok, FX[0], pk, pts(route(B, A)), Math.max(1, V('ts_b') / 2 * h * CYC_MS), {col: 'var(--c7)', dash: true});
    callout(FX[0], B.sx, B.sy, [{t: `${fnum(cyc)} cycles round trip`, f: 'ts-rt-mesh'}, {t: `${h} ${hopw(h)}, ${fnum(ns(cyc))} ns`, f: 'ts-rt-mesh op-600'}], {cell: B, side: B.c <= 3 ? 'r' : 'l', fs: 21});
    ST.pair = (i + 1) % PAIRS.length;
    await wait(tok, 2200);
  }
};

/* (d) the relay: hand a slab to the next shire, or round-trip it through DRAM. One line of the slab is drawn on
   its DRAM path, through its L3 home (shire 16) and memory shire 0, as a load goes (fact addr.load-path). */
FLOWS.D = async tok => {
  const A = SH[0], B = SH[1], HOME = SH[16], mc = MSC[16 % 8], pkg = AP[0].pkg[mc.id + ':0'];
  const directC = route(A, B), direct = pts(directC), h = directC.length - 1;
  const loop = pts(via(A, HOME, mc)).concat([{x: mc.sx, y: pkg.y}, pkg, {x: mc.sx, y: pkg.y}]).concat(pts(via(mc, HOME, B)));
  const bars = [['through DRAM', 'rl_e_dram', 'rl_bw_dram', 'var(--c2)'], ['to the next shire', 'rl_e_next', 'rl_bw_next', 'var(--c3)'], ['in the own scratchpad', 'rl_e_own', 'rl_bw_own', 'var(--c1)']];
  const emax = V('rl_e_dram'), bmax = V('rl_bw_own');
  flowPanel('D', 'The relay: next shire or DRAM',
    `<p class="pn-what">A pipeline stage hands its output to the next stage. Through DRAM it writes the slab out and the next shire reads it back, each line through its L3 home and memory shire (one line is drawn, homed in ${src('shire 16, served by memory shire 0', 'l3.home L43 addr.load-path')}); on chip it writes straight into the next shire's scratchpad (shire 0 to shire 1 here, ${cn(h, 'mesh.logical-map', 0)} ${hopw(h)}).</p>`
    + `<p class="pn-h">Energy per byte (write + read)</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[1]) / emax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[1], 'pJ/B')}</s></div>`).join('')}</div>`
    + `<p class="pn-h">Bandwidth, ${n('rl_stages')} on ${n('n1024')} minions</p><div class="lad">${bars.map(b => `<div class="nm">${b[0]}</div><div class="tr"><u style="width:${(100 * V(b[2]) / bmax).toFixed(1)}%;background:color-mix(in srgb,${b[3]} 50%,transparent)"></u><s>${n(b[2], 'GB/s')}</s></div>`).join('')}</div>`
    + `<p class="pn-what">Next shire against DRAM: ${n('rl_x')} less energy per byte on the three cards, and ${n('rl_speed')} the bandwidth. The dots on the die are drawn at those relative rates.</p>`);
  await goTo({level: 0}); alive(tok);
  hiCells([A, B, HOME, mc], true);
  pipe(FX[0], direct, 'var(--c3)');
  pipe(FX[0], loop, 'var(--c2)', true);
  callout(FX[0], B.sx, B.sy, [{t: 'next shire'}, {t: `${N.rl_e_next.t} pJ/B`, f: 'relay-energy'}], {cell: B, side: 'r', col: 'var(--c3)', fs: 21});
  callout(FX[0], HOME.sx, HOME.sy, [{t: 'through DRAM'}, {t: `${N.rl_e_dram.t} pJ/B`, f: 'relay-energy'}], {cell: HOME, side: 'r', col: 'var(--c2)', fs: 21});
  const ce = bandChart(FX[0], 'pJ per byte', bars.map(b => ({name: b[0].replace('in the own', 'own'), val: N[b[1]].t, col: b[3], f: 'relay-energy'})));
  const cb = bandChart(FX[0], 'GB/s', bars.map(b => ({name: b[0].replace('in the own', 'own'), val: N[b[2]].t, col: b[3], f: 'relay-bw'})), {y: ce.bottom + 14});
  bars.forEach((b, i) => { ce.rows[i].set(V(b[1]) / emax); cb.rows[i].set(V(b[2]) / bmax); });
  sub(`Next shire: ${n('rl_e_next')} pJ/B at ${n('rl_bw_next')} GB/s · through DRAM: ${n('rl_e_dram')} pJ/B at ${n('rl_bw_dram')} GB/s · ${n('rl_13th')} of the energy`);
  if (REDUCED) { await wait(tok, 1e12); return; }
  const EMIT = 190, SLOW = V('rl_bw_next') / V('rl_bw_dram');
  const shoot = (P, col, ms) => { const pk = packet(FX[0], col, 12); quiet(travel(tok, FX[0], pk, P, ms, {trail: false}).then(() => pk.remove())); };
  let nextD = 0, nextM = 0;
  const t0 = CLK.t;
  every(tok, t => {
    const dt = t - t0;
    while (nextD <= dt) { shoot(direct, 'var(--c3)', 120 * h); nextD += EMIT; }
    while (nextM <= dt) { shoot(loop, 'var(--c2)', 120 * (loop.length - 1)); nextM += EMIT * SLOW; }
  });
  await wait(tok, 1e12);
};

/* (e) gathers and scatters (E48): 32-bit elements on scattered lines of a table in each level */
FLOWS.E = async tok => {
  const rq = SH[0], far = Object.values(SH).find(c => hops(c, rq) === 2 && c.lx === 2) || Object.values(SH).find(c => hops(c, rq) === 2);
  const g = ST.gs === 'g', p = g ? 'g_' : 's_';
  const LN = [['L1', 'l1'], ['L2', 'l2'], ['own scratchpad', 'sp'], ['scratchpad 2 hops', 'rs'], ['DRAM', 'dr']].map(([nm, k]) => ({nm, k, c: V(p + k + '_c'), r: p + k + '_r', e: p + k + '_e'}));
  const SCALE = 0.6;   // ms of animation per minion cycle
  flowPanel('E', g ? 'Gathers (E48)' : 'Scatters (E48)',
    `<p class="pn-what">Both harts of ${n('n1024')} minions run the ${n('gs_8')} (${g ? 'fgw.ps' : 'its scatter twin, fscw.ps'}) on scattered lines of a table that fits one level: ${src('each visit\'s 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order', 'gs-g-dram-256K gs-s-dram-256K')}. The bars run at the measured cycles per instruction and count the instructions each lane has done.</p>`
    + `<div class="pn-act"><button type="button" class="st-btn" data-act="gs" aria-pressed="${g}">Gathers</button><button type="button" class="st-btn" data-act="gs" aria-pressed="${!g}">Scatters</button></div>`
    + `<div class="lad" id="race">${LN.map((l, i) => `<div class="nm">${l.nm}</div><div class="tr" data-i="${i}"><u></u><s></s></div>`).join('')}</div>`
    + `<table class="legs"><thead><tr><th>Table in</th><th class="num">G el./s</th><th class="num">pJ/element</th><th class="num">cycles/instr.</th></tr></thead><tbody>${LN.map(l => `<tr><td>${l.nm}</td><td class="num">${n(l.r)}</td><td class="num">${n(l.e)}</td><td class="num">${n(p + l.k + '_c')}</td></tr>`).join('')}</tbody></table>`
    + (g ? '' : `<p class="pn-what small">For DRAM scatters the cycles per instruction (a per-hart median) and the chip's rate differ by ${src('about 5%', 'gs-s-dram-256K')}.</p>`)
    + `<p class="pn-what">These are E48's results, reduced on 27 September on all three cards, not yet on a published page.</p>`);
  await goTo({level: 0}); alive(tok);
  hiCells([rq, far].concat(Object.values(MSC)), true);
  pnReveal($('race'));
  callout(FX[0], rq.sx, rq.sy, [{t: `shire 0 ${g ? 'gathers' : 'scatters'}`}, {t: `L1: ${N[p + 'l1_r'].t} G el./s`, f: 'gs-' + (g ? 'g' : 's') + '-dram-512B'}], {cell: rq, side: 'r', fs: 21});
  sub(`${g ? 'Gathers' : 'Scatters'}, G elements/s: L1 ${n(p + 'l1_r')} · L2 ${n(p + 'l2_r')} · 2 hops ${n(p + 'rs_r')} · DRAM ${n(p + 'dr_r')}`);
  const SN = {l1: 'L1', l2: 'L2', sp: 'own scratchpad', rs: '2 hops away', dr: 'DRAM'};
  const ch = bandChart(FX[0], g ? 'Gathers done' : 'Scatters done', LN.map(l => ({name: SN[l.k], val: '', f: 'gs-' + (g ? 'g' : 's') + '-dram-512B'})), {note: 'count · cycles each'});
  ch.rows.forEach((r, i) => { const y = +r.val.getAttribute('y'); T(ch.g, BAND.x + BAND.w - 7, y, N[p + LN[i].k + '_c'].t, 't-sm halo', 'end', 'gs-' + (g ? 'g' : 's') + '-dram-256K').style.fontSize = '18px'; });
  const trs = LN.map((l, i) => document.querySelector(`#race .tr[data-i="${i}"]`));
  // the data's direction: from the table to the requester for gathers, the other way for scatters
  const toRq = g ? pts(route(far, rq)) : pts(route(rq, far));
  if (REDUCED) {
    LN.forEach((l, i) => { const tr = trs[i]; if (tr) { tr.querySelector('u').style.width = '100%'; tr.querySelector('s').textContent = `${N[p + l.k + '_c'].t} cycles each`; } ch.rows[i].set(1); });
    pipe(FX[0], toRq, 'var(--c4)');
    await wait(tok, 1e12); return;
  }
  const t0 = CLK.t;
  let nextR = 0, nextM = 0;
  const shoot = (P, col) => { const pk = packet(FX[0], col, 10); quiet(travel(tok, FX[0], pk, P, 90 * (P.length - 1), {trail: false}).then(() => pk.remove())); };
  every(tok, t => {
    const dt = t - t0;
    LN.forEach((l, i) => {
      const dur = l.c * SCALE, done = Math.floor(dt / dur), fr = (dt % dur) / dur, tr = trs[i];
      ch.rows[i].set(fr); ch.rows[i].val.textContent = fnum(done, 0);
      if (!tr) return;
      tr.querySelector('u').style.width = (100 * fr).toFixed(1) + '%';
      tr.querySelector('s').textContent = `${fnum(done, 0)} done`;
    });
    const rsDur = V(p + 'rs_c') * SCALE / 8, drDur = V(p + 'dr_c') * SCALE / 8;
    while (nextR <= dt) { shoot(toRq, 'var(--c4)'); nextR += rsDur; }
    while (nextM <= dt) {
      const home = Math.floor(Math.random() * 32), hc = SH[home], mc = MSC[home % 8];
      shoot(pts(g ? via(mc, hc, rq) : via(rq, hc, mc)), 'var(--c2)'); nextM += drDur;
    }
  });
  await wait(tok, 1e12);
};

/* (f) the host pushes work over PCIe */
FLOWS.F = async tok => {
  const pc = CELLS.find(c => c.type === 'pcie'), ms = CELLS.filter(c => c.type === 'master');
  flowPanel('F', 'The host pushes a kernel over PCIe',
    `<p class="pn-what">The host writes the kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from ${n('dram_region')}), then posts the launch to the master shire, whose firmware starts it on the compute shires. The steps follow the specification and the firmware; no host transfer was timed, and the paths inside the chip are drawn x first.</p>`
    + legRows([
      ['host → PCIe shire', `PCIe Gen4 x8: ${n('pcie_gbs')} per direction (the link's figure; never timed here)`, '', ''],
      ['PCIe → memory shires', `lines rotate over the ${n('ms8')} memory shires (PA[8:6]) into LPDDR4X; the path from the PCIe shire is not established`, '', ''],
      ['PCIe → master shire', `shire ${n('master_id')}: one of the two cells marked master or spare; which one was not measured`, '', ''],
      ['master → compute shires', `the kernel starts on the ${n('cshires')} compute shires (mask ${n('mask')} on every card)`, '', ''],
    ]));
  await goTo({level: 0}); alive(tok);
  // leg 0
  leg(0); sub(`Host to the PCIe shire over PCIe Gen4 x8: ${n('pcie_gbs')} per direction by the link's figure; host transfers were not timed`);
  hiCells([pc], true);
  for (let i = 0; i < 3; i++) { const pk = packet(FX[0], 'var(--c4)', 11); quiet(travel(tok, FX[0], pk, AP[0].host, 1300, {trail: i === 0, col: 'var(--c4)'}).then(() => pk.remove())); await wait(tok, 260); }
  await wait(tok, 1300);
  callout(FX[0], 1110, 70, [{t: 'PCIe Gen4 x8'}, {t: `${N.pcie_gbs.t} each way`, f: 'bw-pcie'}, {t: 'link figure, not measured'}], {side: 'l', col: 'var(--c4)', fs: 21});
  await wait(tok, 1200);
  // leg 1: into DRAM through the memory shires
  leg(1); sub(`Buffers go to device DRAM: lines rotate over the ${n('ms8')} memory shires by PA[8:6] (the path from the PCIe shire is not established)`);
  hiCells(Object.values(MSC));
  const legs1 = [];
  for (let m = 0; m < 8; m++) {
    const mc = MSC[m], pkg = AP[0].pkg[m + ':' + (m % 2)], pk = packet(FX[0], 'var(--c3)', 10);
    legs1.push(quiet(travel(tok, FX[0], pk, pts(route(pc, mc)).concat([{x: mc.sx, y: pkg.y}, pkg]), 1900, {col: 'var(--c3)', w: 5, dash: true})));
    await wait(tok, 140);
  }
  await Promise.all(legs1); await wait(tok, 900);
  // leg 2: the launch to the master shire (one of two cells): a "?" in each, clear of the labels
  leg(2); sub(`The launch goes to the master shire (shire ${n('master_id')}), one of the two master-or-spare cells; which one was not measured`);
  hiCells(ms);
  await Promise.all(ms.map(c => travel(tok, FX[0], packet(FX[0], 'var(--c7)', 11), pts(route(pc, c)), 1500, {col: 'var(--c7)', dash: true})));
  ms.forEach(c => { const q = T(FX[0], c.x + INS + 24, c.y + c.h - 14, '?', 't-id halo-s', 'middle', 'L32 chip.master-shire-id'); q.style.fill = 'var(--c7)'; });
  await wait(tok, 1500);
  // leg 3: the compute shires start
  leg(3); sub(`The master's firmware starts the kernel on the ${n('cshires')} compute shires (compute mask ${n('mask')} on every card)`);
  hiCells(Object.values(SH));
  const ps = Object.values(SH).map(c => pulse(tok, FX[0], {x: c.sx, y: c.sy}, 1100, 'var(--c1)', 40));
  await Promise.all(ps); await Promise.all(Object.values(SH).map(c => pulse(tok, FX[0], {x: c.sx, y: c.sy}, 1100, 'var(--c1)', 40)));
  leg(4);
};
const ACTS = {
  replay: () => { if (LASTFLOW) startFlow(LASTFLOW); },
  newpa: () => { ST.pa = mkPA(Math.floor(Math.random() * 32), Math.floor(Math.random() * 2 ** 20)); startFlow('A'); },
  gs: b => { ST.gs = b.textContent.startsWith('G') ? 'g' : 's'; startFlow('E'); },
};
$('pn-body').addEventListener('change', e => { if (e.target.dataset.sel === 'rq') { ST.rq = +e.target.value; startFlow('A'); } });

/* ================= captions and the tour ================= */
const CAPS = {
  A: () => `A load that misses everywhere pays the mesh twice, to its L3 home and on to a memory shire: about ${n('lat_dram')} cycles, ${n('lat_dram_chip')} of them in the DRAM chip.`,
  B: () => `The latency ladder: ${n('lat_l1')} cycles in L1, ${n('lat_l2')} in L2, ${n('lat_l3_a')} + ${n('lat_l3_b')} in L3, about ${n('lat_dram')} in DRAM.`,
  C: () => `TensorSend moves registers from a hart to a minion anywhere on the chip: between shires, ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip, on all three cards.`,
  D: () => `Handing a result to the next shire costs ${n('rl_e_next')} pJ per byte against ${n('rl_e_dram')} through DRAM: ${n('rl_13th')} of the energy, at ${n('rl_speed')} the bandwidth.`,
  E: () => `Gathers from scattered lines: ${n('g_l1_r')} G elements/s from L1, but only ${n('g_dr_r')} G from DRAM, at ${n('g_dr_e')} pJ each.`,
  F: () => `The host writes the kernel's buffers into device DRAM over PCIe Gen4 x8, and the master shire starts it on the ${n('cshires')} compute shires.`,
};
const compG = (key, i) => LAYERS[Z.level].querySelectorAll(`.comp[data-comp="${key}"]`)[i || 0] || null;
const STEPS = [
  {cap: () => `The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor.`,
    view: {level: 0}, panel: ['chip'], sub: () => 'Every part is clickable. Dashed: an inferred identity or place; every die position rests on the inferred orientation.'},
  {cap: () => `${n('cshires')} compute shires of ${n('per_shire')} run the kernels; the master shire schedules them and a spare waits for yield recovery.`,
    view: {level: 0}, hi: ['cshire', 'master'], panel: ['cshire', () => ({cell: SH[13]})], sel: () => SH[13].g, sub: () => `Placed by measured distances: all ${n('pairs496')} shire pairs fit a constant + ${n('hop_cyc')} per hop. Shire 13 is ringed.`},
  {cap: () => `An ${n('grid86')} mesh of ${n('stops')} stops joins them. Each hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire.`,
    view: {level: 0}, hi: ['mesh', 'links'], panel: ['mesh'], sel: () => compG('mesh'), sub: () => 'Routes are shortest paths; the flows draw each leg x first (the order was not measured).'},
  {cap: () => `${n('memshires')} memory shires drive ${n('channels')} LPDDR4X channels (${n('dram_gb')}), ${n('dram_peak')} GB/s peak at this clock; the chip streams ${n('dram_bw')} GB/s.`,
    view: {level: 0}, hi: ['memshire', 'dram'], panel: ['dram', () => ({ms: [0, 1]})], sel: () => compG('dram'), sub: () => `Their places come from a fit on aifoundry2 that holds for ${n('ms_fit')} of DRAM loads, within ±3 cycles, on all three cards.`},
  {cap: () => `Inside a shire, ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM: ${n('scp_mb')} scratchpad, ${n('l2_kb')} L2 and a ${n('l3_mb')} slice of the L3.`,
    view: {level: 1, sid: 13}, panel: ['banks', () => ({})], sub: () => `Orange links: the fast local network's tree edges, ${n('ts_fln')} round trip against ${n('ts_xbar')} for other pairs.`},
  {cap: () => `A minion has ${n('harts')} and a vector unit whose ${n('lanes_n')} lanes also run the tensor instructions. ${n('n1024')} minions sustain ${n('tflops')} TFLOP/s fp32 at ${n('mhz')}.`,
    view: {level: 2, sid: 13, nb: 0, mi: 0}, panel: ['tensor'], sel: () => compG('tensor'), sub: () => `The firmware turns ${n('l1_scp')} of the ${n('l1_kb')} L1 into the tensor scratchpad and leaves each hart ${n('l1_hart')}.`},
  {flow: 'A'}, {flow: 'B'}, {flow: 'C'}, {flow: 'D'}, {flow: 'E'}, {flow: 'F'},
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
function dots(i) {
  const d = $('dots'); d.textContent = '';
  if (i < 0) return;
  STEPS.forEach((s, k) => { const e = document.createElement('i'); e.className = k < i ? 'past' : k === i ? 'on' : ''; d.appendChild(e); });
}
function highlight(keys) {
  svg.classList.add('dimming');
  keys.forEach(k => { if (k === 'links') AP[0].links.classList.add('hi'); else LAYERS[0].querySelectorAll(`.comp[data-comp="${k}"]`).forEach(g => g.classList.add('hi')); });
}
async function tourGo(i) {
  if (!TOUR) return;
  i = Math.max(0, Math.min(STEPS.length - 1, i)); TOUR.i = i;
  const s = STEPS[i];
  stopFlow(); select(null);
  setKick(`Tour · step ${i + 1} of ${STEPS.length}`); dots(i);
  $('btn-prev').disabled = i === 0; $('btn-next').disabled = i === STEPS.length - 1;
  if (s.flow) { setCap(CAPS[s.flow]()); sub(''); startFlow(s.flow); return; }
  setCap(s.cap()); sub(s.sub ? s.sub() : '');
  if (s.panel) showComp(s.panel[0], s.panel[1] ? s.panel[1]() : {});   // the panel changes with the caption, not after the zoom
  playBtn();
  await goTo(s.view);
  if (!TOUR || TOUR.i !== i) return;
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
  TOUR = null; $('btn-tour').textContent = 'Tour'; $('btn-tour').classList.remove('on');
  $('stage').classList.remove('present');
  $('btn-prev').disabled = false; $('btn-next').disabled = false;
  dots(-1); clearFx(); resetCap(); playBtn();
}
const HINT = 'Space pauses · F full screen · P hides the panel · Q ends the tour · Backspace zooms out';
function resetCap() {
  CAPFLOW = false;
  setKick('Explore');
  setCap(`Click any part of the chip, pick a data flow, or press Tour to step through it in ${STEPS.length} steps.`);
  sub(HINT);
}
/* the Play button: Pause while a flow runs, Play when paused, Replay after; nothing to play on a still tour step */
function playBtn() {
  const b = $('btn-play'), running = flowRunning(), still = !!TOUR && !STEPS[TOUR.i].flow;
  const t = still ? 'Play' : running && CLK.on ? 'Pause' : running ? 'Play' : (TOUR || LASTFLOW) ? 'Replay' : 'Play';
  b.textContent = t;
  b.disabled = still || (!running && !LASTFLOW && !TOUR);
  b.setAttribute('aria-label', t + ' (Space)');
}
function playPause() {
  if (TOUR) {
    const s = STEPS[TOUR.i];
    if (!s.flow) return;                                             // a still step: Space holds it
    if (flowRunning() && RUN.k === s.flow) { CLK.on = !CLK.on; playBtn(); }
    else tourGo(TOUR.i);                                             // this step's flow again
    return;
  }
  if (flowRunning()) { CLK.on = !CLK.on; playBtn(); }
  else if (LASTFLOW) startFlow(LASTFLOW);
}
function toggleFS() {
  const st = $('stage');
  if (document.fullscreenElement || document.webkitFullscreenElement) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
  else { const r = (st.requestFullscreen || st.webkitRequestFullscreen); if (r) { const p = r.call(st); if (p && p.catch) p.catch(() => {}); } }
}
const fsLabel = () => { $('btn-fs').textContent = (document.fullscreenElement || document.webkitFullscreenElement) ? 'Exit full screen' : 'Full screen'; setTimeout(fitCap, 80); };
document.addEventListener('fullscreenchange', fsLabel); document.addEventListener('webkitfullscreenchange', fsLabel);
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
function next() {
  if (!TOUR) return startTour(0);
  if (TOUR.i >= STEPS.length - 1) { sub('End of the tour: Q or End tour leaves it; the Left arrow steps back.'); return; }
  tourGo(TOUR.i + 1);
}
function prev() { if (TOUR) { if (TOUR.i > 0) tourGo(TOUR.i - 1); } else startTour(0); }
function back() {
  if (TOUR) { endTour(); stopFlow(); return; }
  if (flowRunning() || RUN.done) { stopFlow(); RUN = {dead: true}; resetCap(); return; }
  if (Z.level === 2) goTo({level: 1, sid: Z.sid}, {focus: svg.contains(document.activeElement)}); else if (Z.level === 1) goTo({level: 0}, {focus: svg.contains(document.activeElement)});
}
document.querySelectorAll('[data-flow]').forEach(b => b.addEventListener('click', () => { endTour(); startFlow(b.dataset.flow); }));
$('stage').addEventListener('click', e => { const b = e.target.closest && e.target.closest('button'); if (b && e.detail > 0) b.blur(); });
$('btn-play').addEventListener('click', playPause);
$('btn-tour').addEventListener('click', () => { if (TOUR) endTour(); else startTour(0); });
$('btn-fs').addEventListener('click', toggleFS);
$('btn-panel').addEventListener('click', () => togglePanel());
$('btn-next').addEventListener('click', next);
$('btn-prev').addEventListener('click', prev);
const stageInView = () => { const r = $('stage').getBoundingClientRect(); return r.bottom > window.innerHeight * 0.4 && r.top < window.innerHeight * 0.6; };
/* The keys act on the stage only while it is in view (or full screen) and focus is in it or on the page itself, so
   that below the stage Space, PageDown and the arrows scroll as usual. Space on a button presses the button. */
document.addEventListener('keydown', e => {
  if (e.key !== 'Tab') hideTip();
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  const tg = e.target, tag = (tg.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
  const fs = !!(document.fullscreenElement || document.webkitFullscreenElement), inView = fs || stageInView();
  const inStage = inView && ($('stage').contains(tg) || tg === document.body || tg === document.documentElement);
  if (!inStage) return;
  const onControl = tg.closest && tg.closest('button, a, li.fact');
  switch (e.key) {
    case 'ArrowRight': case 'PageDown': e.preventDefault(); next(); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); prev(); break;
    case ' ': case 'Spacebar': if (onControl) return; e.preventDefault(); playPause(); break;
    case 'f': case 'F': e.preventDefault(); toggleFS(); break;
    case 'p': case 'P': e.preventDefault(); togglePanel(); break;
    case 'd': case 'D': e.preventDefault(); toggleTheme(); break;
    case 'q': case 'Q': if (TOUR) { e.preventDefault(); endTour(); stopFlow(); } break;
    case 'Escape': back(); break;
    case 'Backspace': if (Z.level) { e.preventDefault(); endTour(); haltFlow(); goTo({level: Z.level - 1, sid: Z.sid}, {focus: svg.contains(document.activeElement)}); } break;
    default: if (/^[1-6]$/.test(e.key)) { endTour(); startFlow('ABCDEF'[+e.key - 1]); }
  }
});

/* ================= the text below the stage ================= */
function prose() {
  $('summary-text').innerHTML = [
    `<p><b>The chip.</b> The ET-SoC-1 has ${n('cores')} RISC-V cores on a ${n('die_mm2')} mm² die in TSMC ${n('process')}: ${n('minions')} minions in ${n('shires')} shires, ${n('maxions')} and a service processor. The diagram draws the die (width and height from a published die plot) with ${n('cshires')} compute shires, the master and spare shires, the PCIe and I/O shires, and ${n('memshires').toLowerCase()} memory shires, on an ${n('grid86')} mesh of ${n('stops')} stops. The compute shires sit where measured distances put them; each mesh hop adds ${n('hop_cyc')} (${n('hop_ns')}) to a round trip and is about ${n('hop_mm')} of wire. Off the die, four LPDDR4X packages hold ${n('channels')} channels of ${n('ch_bits')}, ${n('dram_gb')}; the chip streams ${n('dram_bw')} GB/s from them against ${n('dram_peak')} GB/s peak at their ${n('mts')} MT/s. The host links through the PCIe shire (Gen4 x8, ${n('pcie_gbs')} per direction by the link's figure, never timed here). The fp32 matmul at ${n('tflops')} TFLOP/s draws ${n('mmw')} at the board on the three cards, ${n('perw')} GFLOP/s per watt.</p>`,
    `<p><b>A shire.</b> ${n('neigh')} of ${n('per_neigh')} share ${n('cache_mb')} of SRAM in ${n('banks')}. The cards run mode M0: ${n('scp_mb')} of scratchpad that any shire can address, ${n('l2_kb')} of L2 private to the shire, and a ${n('l3_mb')} slice of the chip's ${n('l3_chip')} L3. The shire meets the mesh at one stop, and inside a neighbourhood minions talk fastest along the tree edges of the fast local network (${n('ts_fln')} round trip, against ${n('ts_xbar')} cycles for other pairs).</p>`,
    `<p><b>A minion.</b> ${n('harts')}, in-order and single-issue, a vector unit of ${n('lanes')} and a ${n('l1_kb')} L1 data cache, of which the firmware makes ${n('l1_scp')} a tensor scratchpad and leaves each hart ${n('l1_hart')}. The tensor instructions are no separate unit: state machines in the vector unit run them on its lanes' FMA and int8 multiply-add units, so the tensor peak (${n('peak32')}, ${n('peak16')} or ${n('peak8')} operations per cycle) is the lanes' peak. On ${n('n1024')} minions at ${n('mhz')} they sustain ${n('tflops')} TFLOP/s fp32.</p>`,
    `<p><b>The flows.</b> (1) A load that misses every cache: ${n('lat_l1')} cycles would have been an L1 hit and ${n('lat_l2')} an L2 hit; the L3 home is PA[10:6] and costs ${n('lat_l3_a')} + ${n('lat_l3_b')}; the memory shire is PA[8:6] and adds ${n('lat_ms_a')} + ${n('lat_ms_b')} cycles per hop; a typical DRAM load takes ${n('lat_dram')}, of which ${n('lat_dram_chip')} are the DRAM chip. (2) The ladder adds the read buffer (${n('lat_rb')}), the own scratchpad (${n('lat_scp')}) and another shire's scratchpad (${n('lat_rs_a')} + ${n('lat_rs_b')} per hop). (3) TensorSend: ${n('ts_a')} cycles plus ${n('ts_b')} per hop, round trip. (4) The relay: ${n('rl_e_next')} pJ/B to the next shire against ${n('rl_e_dram')} through DRAM (${n('rl_x')} less). (5) Gathers from scattered lines: ${n('g_l1_r')}, ${n('g_l2_r')}, ${n('g_rs_r')} and ${n('g_dr_r')} G elements/s from L1, L2, a scratchpad two hops away and DRAM. (6) The host writes buffers into DRAM through the PCIe shire and the master shire (${n('master_id')}) starts the kernel on the compute shires.</p>`,
  ].join('');
  // what is measured, specified, derived and inferred
  const fs = Object.values(F), of = k => fs.filter(f => f.kind === k), meas = of('measured');
  const mc = k => meas.filter(f => f.cards.length === k).length;
  const lk = id => `<a href="#facts" data-f="${id}" class="num">${id}</a>`;
  $('honest-text').innerHTML = `<p>The page rests on ${fs.length} facts: <b>${meas.length} measured</b>, ${of('spec').length} from the specification (the datasheet, the Programmer's Reference Manual, the core-et documents and the firmware source), ${of('derived').length} derived from others and <b>${of('inferred').length} inferred</b>. Of the measured facts, ${mc(3)} hold on all three lab cards (aifoundry2, aifoundry3 and aifoundry1 card 1), ${mc(2)} on two and ${mc(1)} on one, mostly aifoundry2${mc(0) ? `; ${mc(0)} name no card` : ''}. Every table here is at ${n('mhz')}, where a warm card sits.</p>`
    + `<p>What the drawing assumes:</p><ul>`
    + `<li><b>Where the compute shires are</b> is measured: all ${n('pairs496')} shire pairs fit a constant plus ${n('hop_cyc')} per hop of Manhattan distance on the logical map (${lk('mesh.shortest-paths')}). <b>Transposing that map onto the die</b> (logical x to die rows, y to die columns) is inferred (${lk('mesh.orientation')}, ${lk('L33')}, ${lk('L34')}): distances alone cannot tell a rotation from a reflection. Every die position, dashed or solid, rests on it.</li>`
    + `<li><b>The four grey cells</b> hold the master, spare, PCIe and I/O shires; which is which is inferred (${lk('L32')}), and two sources draw PCIe and I/O in opposite order (${lk('L24')}). They are dashed.</li>`
    + `<li><b>The memory shires' places</b> come from a fit of DRAM latencies on one card, aifoundry2 (${lk('L40')}). Left as fitted, the model with these places is within ±3 cycles for ${n('ms_fit')} of loads on all three cards (${lk('ms-fit-3cards')}). Memory shire 2's fit ties three places, but one is an empty corner of the grid and one lies off it, so one place is left (${lk('L42')}, ${lk('ms2-forced')}); it stays dashed.</li>`
    + `<li><b>Which two memory shires share each LPDDR4X package</b> is not documented; the drawing pairs neighbours (${lk('dram.pkg-pairing')}, ${lk('L23')}). The packages are dashed.</li>`
    + `<li><b>Routes</b>: every leg, a reply included, is drawn on its own route, x first, then y, on the logical map; where x first would cross an empty corner of the grid (some legs from a memory shire), y first. The mesh's routing order was never measured (${lk('L104')}); only the hop count is.</li>`
    + `<li><b>The way back</b> of a DRAM load is not established; the model pays the mesh round trip on both legs (${lk('addr.load-model')}), and the diagram draws the reply from the memory shire through the L3 home to the requester.</li>`
    + `<li><b>Inside a shire</b>, the drawing is a block diagram: no source gives where the banks and neighbourhoods sit in the tile (${lk('L114')}). The minions' order in a neighbourhood follows the core-et floorplan (${lk('L115')}).</li>`
    + `<li><b>Sizes</b>: the die's width and height and the tile pitch are pixel estimates on one vendor die plot scaled to ${n('die_mm2')} mm² (${lk('chip.die-dims')}, ${lk('chip.hop-pitch')}).</li>`
    + `<li><b>Gathers and scatters</b> (E48) were reduced on 27 September and have no published page yet.</li></ul>`
    + `<p>The inferred facts:</p><ul>${of('inferred').map(f => `<li>${esc(f.statement)} <span class="small">(${lk(f.id)})</span></li>`).join('')}</ul>`;
  // every fact
  const tb = document.querySelector('#facttab tbody');
  tb.innerHTML = Object.keys(F).sort().map(id => { const f = F[id];
    return `<tr><td data-label="Fact"><code>${esc(id)}</code></td><td data-label="Statement">${esc(f.statement)}${f.url ? ` <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)}</a>` : ''}</td><td data-label="Kind"><span class="kd ${f.kind}">${f.kind}</span></td><td data-label="Cards">${esc(cardsTxt(f))}</td><td data-label="Source" class="small">${esc(f.source)}</td></tr>`; }).join('');
  CK.sortTable('facttab', {filter: true, filterLabel: 'Filter facts'});
}

/* ================= start ================= */
buildChip();
crumbs();
prose();
showComp('chip', {});
sub(HINT);
try {
  const q = new URLSearchParams(location.search);
  setTheme(q.get('theme'));
  if (q.get('panel') === 'off') togglePanel(false);
} catch (_) { /* no URL flags */ }
playBtn();
fitCap();
/* on a narrow screen the drawing scrolls sideways: start at its middle, the compute shires */
try { const w = $('svgwrap'); if (w.scrollWidth > w.clientWidth + 4) w.scrollLeft = (w.scrollWidth - w.clientWidth) / 2; } catch (_) { /* not laid out */ }
})();
