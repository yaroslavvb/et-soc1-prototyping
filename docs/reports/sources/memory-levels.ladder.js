/* ================= memory-levels.ladder.js: the shared ladder on the memory levels (1 October 2026, part 2) =================
   The owner, 1 Oct: "the memory levels should also have the up button to zoom out, and also it should go down to the
   original items ... make the diagrams, the memory levels, and the ETSOC interactive ... consistent with each other";
   and at 09:00 the easter egg above the rack, a way back from every move, the loop through one atom and no dead end
   (/home/yaroslavvb/claude/work/ladder/OWNER-REQUEST.md; the design: DESIGN.md there, §1, §3, §5.6 B0-B4).

   How it stands on the page. The memory levels keep their own camera for their own scenes: the five levels' drawings,
   the level tabs, the accesses with their Dive, the player bar, the phone's sideways window and the level moves the
   owner asked smooth on 30 September (953f85c). Beside it, in this scope of its own, runs the chip diagram's path
   camera (ladder-core.js) with the shared scales: outward from the chip's map to the package, the card, the rack and
   on (the easter egg) to the ring of sizes, and inward from the levels' deepest drawings to the transistor, the fin,
   the channel, the crystal, the atom, its nucleus, a proton, a quark and the Planck length, with the textbook
   constructions of every part the levels draw without a drawing of their own (ladder-circuits.js). One Up bar, one
   breadcrumb and one readout serve both: the path camera's (the chip's markup and code), fed with the levels' place as a
   path of the same vocabulary while their own camera holds the stage.

   Why not one camera (DESIGN D2 asked for one, with B1-lite as its fallback): the levels' camera draws a move in its
   root's coordinates and cannot span the ladder's 45 decades (code-audit §3.3); porting the 28 accesses, Dive, the
   phone window, the cross-fades between the chip levels' maps and the tuned level moves onto the path camera risks the
   smoothness the owner asked for, and B1-lite would have left the outer and inner scales to the chip page. So the two
   hand over at rest, on a scene both draw the same way: the path camera draws a level's scene with the level's own
   builder (the same code, the same example address) at the same place on the screen, so the hand-over is not seen.
   A move between the levels' own scenes is theirs; a move that leaves them starts at their scene (the path camera takes
   over at rest) and one that comes back ends there (the levels' camera takes over at rest). A move from outside to
   outside that would pass through the levels' scenes goes in three legs, each from rest: out of the shared scales to
   the scene where they meet the levels', the levels' own move, and on in. The levels' camera already rests between two
   legs of a move between levels.

   The scales: the chip's node ids (DESIGN §1.1, §3.5). The levels' places as paths: the map of a chip level is
   die:l3, die:scp or die:dram; the L2's shire is shire:R in the map it was entered from (R the requester); the L1's minion
   minion:R.0.0 in it; the chains below are the chip's (ladder-mem.js: l1d, shire.bank, ... dram.cell), the L3's and the
   scratchpad's own drawings shire.l3, shire.bank.l3, ..., shire.scp, ... (new here). A scene of another instance than
   the example's (another bank, another shire) is the path camera's, drawn by the levels' builder all the same. */
MLH = (function (DM) {
'use strict';
const ML = MLB;   // the levels' own camera and drawings (memory-levels.script.js fills it before this runs)
/* ---- the data: the ladder's scales, maps, numbers and images (D.ladder, copied from the chip's facts.json by
   build_facts.py), its facts fetched lazily from ladder-img/ladder-data.json; the levels' own facts are theirs ---- */
const D = Object.assign({facts: {}, num: {}}, DM.ladder || {});
const F = D.facts, N = D.num, ASKS = [], RUNGS = {};
Object.entries(F).forEach(([k, f]) => { f.id = k; if (!f.cards) f.cards = []; });
const KINDS9 = ['measured', 'spec', 'derived', 'inferred', 'outside', 'generic', 'owner', 'hypothesis', 'unknown'];
const HUB = 'https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability';
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
let REDUCED = !!CK.reduced;
try { const mq = matchMedia('(prefers-reduced-motion: reduce)'); mq.addEventListener('change', e => { REDUCED = e.matches; }); } catch (_) { /* old browser */ }
const fnum = (v, dp) => CK.fmt.num(v, dp);
const V = k => { if (!N[k]) throw new Error('no number ' + k); return N[k].v; };
const disp = t => String(t).replace(/(\d)x(?=$|[\s,;.)])/g, '$1×');
function n(k, unit) {
  const x = N[k]; if (!x) { console.error('no number ' + k); return '?'; }
  return `<span class="num" data-f="${x.f}">${esc(disp(x.t))}${unit ? ' ' + esc(unit) : ''}</span>`;
}
const cn = (v, fids, dp, unit) => `<span class="num" data-f="${fids}">${fnum(v, dp)}${unit ? ' ' + unit : ''}</span>`;
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
function T2(parent, x, y, lines, cls, anchor, fids, lh) {
  const t = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, parent);
  lines.forEach((ln, i) => {
    const L = typeof ln === 'string' ? {t: ln} : ln, sp = E('tspan', {x, dy: i ? (lh || 1.2) + 'em' : 0}, t);
    sp.textContent = L.t; if (L.c) sp.setAttribute('class', L.c); if (L.f) sp.setAttribute('data-f', L.f);
  });
  if (fids) t.setAttribute('data-f', fids);
  return t;
}
const mqOn = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };

/* ---- the drawing: the path camera's own SVG (#chip, so that the shared scales' CSS, ladder.css, is theirs here too),
   stacked over the levels' drawing in the same box; its frame is the chip's (the shared scenes are drawn in it) ---- */
const VB = {x: -190, y: -84, w: 1400, h: 792};
const MVB = ML.VB, MFR = ML.FR;   // the levels' frame (1,300 wide) and the box every one of their scales is drawn in
const svg = $('chip'), LADW = $('ladwrap');
svg.setAttribute('viewBox', `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
const TOUCH = mqOn('(hover: none) and (pointer: coarse)');
/* a phone (a portrait window under 900 px): the shared scenes take their phone views, in a box the shape of the levels'
   visible window, 1,000 units wide (the chip's rule) */
const PHQ = '(max-width: 899px) and (max-aspect-ratio: 1/1)';
let PH = mqOn(PHQ), PV = null, PKW = 110;
/* the box: the overlay over the levels' drawing's visible part, measured; a view of a level's scene at rest is the part
   of the levels' drawing their own camera shows there (mlView), so that the two pictures coincide */
function boxWH() { const w = $('svgwrap'); return {w: w.clientWidth || 1, h: w.clientHeight || 1}; }
function phGeom() {
  PH = mqOn(PHQ);
  const b = boxWH(), hw = b.h / b.w;
  PV = [0, 1, 2].map(() => ({x: 0, y: 0, w: 1000, h: 1000 * hw}));
}
phGeom();
const pview = () => mlView();
/* the levels' visible window in their units: on a wide screen their whole frame, fitted (meet) in the box; on a phone
   the part of their wider drawing the sideways scroll shows. As the path camera's view (vmat): on a wide screen a rect
   whose map onto the chip's frame puts the levels' units where the levels' own SVG puts them; on a phone the window. */
function mlView() {
  const m = $('mem'), w = $('svgwrap');
  if (PH) {
    const mr = m.getBoundingClientRect(), wr = w.getBoundingClientRect(), s = mr.width / MVB.w;
    if (!(s > 0)) return {x: MVB.x, y: MVB.y, w: MVB.w, h: MVB.w * PV[0].h / 1000};
    const x0 = MVB.x + (wr.left + w.clientLeft - mr.left) / s, y0 = MVB.y + (wr.top + w.clientTop - mr.top) / s;
    return {x: x0, y: y0, w: w.clientWidth / s, h: w.clientWidth / s * PV[0].h / 1000};
  }
  const b = boxWH(), sM = Math.min(b.w / MVB.w, b.h / MVB.h), sH = Math.min(b.w / VB.w, b.h / VB.h), k = sM / sH;
  const tx = VB.x + VB.w / 2 - k * (MVB.x + MVB.w / 2), ty = VB.y + VB.h / 2 - k * (MVB.y + MVB.h / 2);
  return {x: (VB.x - tx) / k, y: (VB.y - ty) / k, w: VB.w / k, h: VB.h / k};
}
/* the overlay sits over the levels' drawing's visible box */
function overlayFit() {
  const w = $('svgwrap'), v = w.parentNode;
  if (!w || !LADW) return;
  const r = w.getBoundingClientRect(), pr = v.getBoundingClientRect();
  S(LADW, {left: (r.left - pr.left + w.clientLeft) + 'px', top: (r.top - pr.top + w.clientTop) + 'px', width: w.clientWidth + 'px', height: w.clientHeight + 'px'});
}

/* ---- the clock and the view helpers (the chip page's; the clock is the levels' own, so Space stops both) ---- */
const CLK = ML.CLK, DTMAX = ML.DTMAX;
const lerp = (a, b, t) => a + (b - a) * t;
const lerpR = (A, B, t) => ({x: lerp(A.x, B.x, t), y: lerp(A.y, B.y, t), w: lerp(A.w, B.w, t), h: lerp(A.h, B.h, t)});
const easeS = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const band = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rmap = (A, B) => { const k = B.w / A.w; return [k, B.x - k * A.x, B.y - k * A.y]; };
const setT = (g, m) => { if (m) g.setAttribute('transform', `matrix(${m[0]},0,0,${m[0]},${m[1]},${m[2]})`); else g.removeAttribute('transform'); };
const zoomR = (A, B, e) => { const w = A.w * Math.pow(B.w / A.w, e); return lerpR(A, B, (w - A.w) / (B.w - A.w)); };
const viewM = r => { const k = 1000 / r.w; return [k, -k * r.x, -k * r.y]; };
const cmpM = (V0, M) => (!V0 ? M : !M ? V0 : [V0[0] * M[0], V0[0] * M[1] + V0[1], V0[0] * M[2] + V0[2]]);
const BLEND = 0.45;
const simInv = S0 => [1 / S0[0], -S0[1] / S0[0], -S0[2] / S0[0]];
const simR = (S0, A) => ({x: S0[0] * A.x + S0[1], y: S0[0] * A.y + S0[2], w: S0[0] * A.w, h: S0[0] * A.h});
function simZoom(S0, S1, p) {
  const r = S1[0] / S0[0];
  if (Math.abs(Math.log(r)) < 1e-9) return [S0[0], lerp(S0[1], S1[1], p), lerp(S0[2], S1[2], p)];
  const px = (S1[1] - r * S0[1]) / (1 - r), py = (S1[2] - r * S0[2]) / (1 - r), q = Math.pow(r, p);
  return [S0[0] * q, px + q * (S0[1] - px), py + q * (S0[2] - py)];
}
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
function ctxList(layer, tgt) {
  const out = [], take = s => { if (s !== tgt && !s.classList.contains('fx') && !s.classList.contains('zbd')) out.push(s); };
  if (!tgt) { [...layer.children].forEach(take); return out; }
  let el = tgt;
  while (el && el !== layer && el.parentNode) {
    const p = el.parentNode;
    [...p.children].forEach(s0 => { if (s0 !== el) take(s0); });
    el = p;
  }
  return out;
}
function ctxClear(layer) {
  layer.querySelectorAll('.zdim, .ztgt, .zhi').forEach(e => e.classList.remove('zdim', 'ztgt', 'zhi'));
  layer.classList.remove('zsat');
  ['--lab', '--ctx', '--sat', '--ctxh', '--tgt', '--tsat'].forEach(k => layer.style.removeProperty(k));
}
const FULL = {o: 1, s: 1};
function lookOf(el) {
  if (!el) return FULL;
  const cs = getComputedStyle(el), o = parseFloat(cs.opacity), m = /saturate\(([\d.]+)\)/.exec(cs.filter || '');
  return {o: o >= 0 && o <= 1 ? o : 1, s: m ? Math.min(1, +m[1]) : 1};
}
const CTX_LOW = 0.3;

/* ---- what the core reads from a page that has flows (the chip): here there are none; the levels' accesses are the
   levels' own, and hold the stage through pageBusy ---- */
const LAYERS = [], FX = [], AP = [];
const FL = {k: null, i: 0, tok: {dead: true}, ctx: null, done: false, still: false};
const TOUR = null;
const FOLLOW = false;
const setFollow = () => {}, startFlow = () => {}, restartStage = () => {}, playBtn = () => {}, renderBar = () => {};
/* (an access holds the stage as a flow does on the chip: Space on a part of the ladder's drawing does not pick the part
   while one is on; review of 1 Oct) */
const flowOn = () => ML.accOn();
const foldSoon = () => {}, watchFold = () => {};
const foldObs = null;
const goNeighbour = () => {};
const cellOfEl = () => null;
let NBRBACK = null;
const BYDIE = {};
/* the chip's die geometry, which the shared files' seats on the chip's own die read; here the die is the levels' map,
   whose own seats come first (DIE_SEATS below), so these are never reached but stay defined */
const TILE = 120, DW = 960, DH = 720, INS = 5, CELLS = [], SH = {}, MSC = {};
const isShire = () => false;
const shCell = () => null;
const pts = cells => cells.map(c => ({x: c.sx, y: c.sy}));
const ns = cyc => cyc;
const PIP = {el: null};
const COMPS = {}, LEADS = {};
const ACTS = {};
const PAGE_TIPS = false;   // the source tooltips are the levels' (their handler finds a fact of either page)

/* ---- the panel (the levels' #pn-body; the chip's way of writing it) ---- */
let SEL = null;
function select(g) {
  if (SEL) { SEL.classList.remove('sel'); if (SEL._hiSel) { SEL.classList.remove('hi'); SEL._hiSel = false; } }
  SEL = g;
  if (!g) pillOff();
  if (g) { g.classList.add('sel'); if (!g.classList.contains('hi')) { g.classList.add('hi'); g._hiSel = true; } }
}
const CARDNAME = {a2: 'aifoundry2', a3: 'aifoundry3', a1c1: 'aifoundry1 card 1'};
function cardsTxt(f) {
  if (f.cards_txt) return f.cards_txt;
  const cs = f.cards || [];
  if (cs.length === 3) return 'three cards';
  if (cs.length) return cs.map(c => CARDNAME[c]).join(', ');
  return f.kind === 'measured' ? (f.card || 'card not recorded') : '';
}
function factLi(id) {
  const f = F[id]; if (!f) { if (LAZY.st === 'idle' || LAZY.st === 'loading') return lazyLi('loading the sources…'); if (LAZY.st === 'failed') return lazyLi('sources not loaded'); return ''; }
  const cd = cardsTxt(f);
  return `<li class="fact" tabindex="0" data-f="${id}" data-src="1" aria-describedby="srctip"><span>${esc(f.statement)}</span><span class="meta"><span class="kd ${f.kind}">${KWORD[f.kind] || f.kind}</span>${CAVW[f.caveat] ? `<span class="kd erbium">${CAVW[f.caveat]}</span>` : ''}`
    + (cd ? `<span class="cd">${esc(cd)}</span>` : '')
    + (f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.page)} ↗</a>` : '')
    + `<span class="fid">${esc(id)}</span></span></li>`;
}
const src = (text, fids) => `<span class="num" data-f="${fids}">${text}</span>`;
const kpi = (html, lab) => `<div class="pn-kpi"><b>${html}</b><span>${lab}</span></div>`;
const K = (k, lab) => kpi(n(k), lab);
function panel(html) {
  ML.hideTip(); const b = $('pn-body'); b.innerHTML = ARW(html); b.scrollTop = 0;
  const k = b.querySelector('.pn-kick'), t = b.querySelector('.pn-title');
  $('pn-live').textContent = (k ? k.textContent + ': ' : '') + (t ? t.textContent : '');
}
function pnReveal(el) {
  const sc = $('pn-body'); if (!el || !sc.contains(el) || !el.getClientRects().length) return;
  const r = el.getBoundingClientRect(), s0 = sc.getBoundingClientRect();
  if (r.top < s0.top + 4) sc.scrollTop += r.top - s0.top - 8;
  else if (r.bottom > s0.bottom - 4) sc.scrollTop += Math.min(r.bottom - s0.bottom + 8, r.top - s0.top - 8);
}
const refocus = (box, k) => { if (k < 0) return; const b = box.querySelectorAll('button')[k]; if (b) b.focus({preventScroll: true}); };
function showComp() {}
function sub() {}
function clearDim() { svg.classList.remove('dimming', 'fdim'); svg.querySelectorAll('.hi').forEach(e => e.classList.remove('hi')); if (SEL) SEL._hiSel = false; }
function clearFx() { clearDim(); }
/* the chip page's part drawing (the shared scales' opart draws with it) */
function comp(parent, key, ctx, label) {
  const g = E('g', {class: 'comp dimmable', tabindex: 0, role: 'button', 'aria-label': label, 'data-comp': key}, parent);
  g._key = key; g._ctx = ctx || {};
  return g;
}

/* ---- the levels' drawing kit and builders for the shared chains (ladder-mem.js draws with CKT on the chip, from a
   copy of the levels' code, circuitkit.js; here the same calls draw with the levels' own code) ---- */
const LVOF = {buildL1Cache: 'l1', buildL1Block: 'l1', buildL1Row: 'l1', buildL1Latch: 'l1', buildL1Cmp: 'l1', buildL2Bank: 'l2', buildL2Sub: 'l2',
  buildL2Panel: 'l2', buildL2Cell: 'l2', buildL2Xing: 'l2', buildWire: 'l3', buildL3Wire: 'l3', buildMeshHop: 'l3', buildMS: 'dram', buildChan: 'dram',
  buildDBank: 'dram', buildDCell: 'dram', buildPHY: 'dram', buildDQ: 'dram'};
const CKT = (() => {
  const B = {};
  Object.keys(LVOF).forEach(k => { const f = ML.builders[k]; if (!f) throw new Error('memory levels: no builder ' + k); f._lv = LVOF[k]; B[k] = f; });
  return Object.assign(B, {
    /* a scene drawn into a layer of the path camera by the levels' own builder: their example address, their type
       sizes and knockouts (the levels' buildInto does the same for their own layers) */
    build: (fn, L, ap, inst, parts) => ML.buildWith(fn, L, ap, inst, parts, fn._lv),
    hitAreas: L => ML.hitAreas(L),
    partText: g => ML.partText(g),
    INST: ML.INST, FR: MFR, COL: ML.COL, DASH: ML.DASH,
    parts: ML.parts,
    kit: ML.kit,
  });
})();
/* the core's hooks: the ways back in from the ring (the reader's level's own cell: DESIGN §1.6), a level's access holds
   the stage, the lazy facts arrived */
function pageExits() { return ringExits(); }
function pageBusy() { return ML.accOn() || ML.zw(); }   // (and while their camera moves: the lazy fetch and parse waits; code review of 1 Oct)
function pageLazy() { if (!ZW && ON && !SEL) showHere(); }
/*@include ladder-core.js*/
/*@include ladder-outer.js*/
/*@include ladder-mem.js*/
/*@include memory-levels.nodes.js*/
/*@include chip-diagram.blocks.js*/
/*@include ladder-inner.js*/
/*@include ladder-circuits.js*/
/*@include ladder-panel.js*/
/*@include memory-levels.links.js*/
/*@include memory-levels.hand.js*/
})(D);
