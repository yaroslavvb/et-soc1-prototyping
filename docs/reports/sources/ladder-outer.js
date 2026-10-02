/* ================= the levels outside the chip (30 September 2026) =================
   The owner's request: "zoom out further to get to this rack ... a Studio 45, ... San Francisco, United States, Earth,
   Milky Way, Andromeda Cluster ... all the way to the meta universe". One path of 18 levels above the die, from
   "beyond what we can see" (speculative) down to the package; DESIGN §1.2 has the ladder and §3.2 what each shows.
   Each level is a scene drawn in the drawing's frame (VB) in its own units, its content inside the middle 760 units
   (a phone's view, opv). Its child sits at a seat in its drawing: a nest (the child drawn inside it, to scale: the
   maps, the rack in the room, the lid on the card) or a jump (a "powers of ten" cut: the camera zooms some 3-8 times
   into a marked box while the child grows out of it and the two cross-fade; the readout sweeps the true ratio).
   Every number a drawing prints is a fact's (D.onum, asserted in the build); the images load only when the camera
   comes near them (the folder ladder-img/ beside the page) and are decoded before the camera enters. */
const OSC = D.scales || {}, OGEO = D.geo || {}, ONUM = D.onum || {}, IMGS = D.img || {};
const IMGDIR = 'ladder-img/';
const on = k => (ONUM[k] ? ONUM[k].t : '?');
const onf = k => (ONUM[k] ? ONUM[k].f : '');
const OUTL = ['beyond', 'universe', 'laniakea', 'localgroup', 'milkyway', 'stars', 'solar', 'moon', 'earth', 'us', 'california', 'bayarea', 'sf', 'bernal', 'st29', 'studio45', 'rack', 'host', 'card', 'package'];
OUT_IDS.push(...OUTL);
const rc = (x, y, w, h) => ({x, y, w, h});
const cR = (cx, cy, r) => ({x: cx - r, y: cy - r, w: 2 * r, h: 2 * r});
/* the rect in the parent's units where the child's frame F goes, so that the child's rect a (its units) lands on the
   parent's rect b (centres aligned; the scale the geometric mean of the two rects' width and height ratios) */
function seatMap(F, a, b) {
  const k = Math.sqrt((b.w / a.w) * (b.h / a.h)), cx = b.x + b.w / 2, cy = b.y + b.h / 2, ax = a.x + a.w / 2, ay = a.y + a.h / 2;
  return {x: cx - k * (ax - F.x), y: cy - k * (ay - F.y), w: k * F.w, h: k * F.h};
}
/* a jump's marked box: an eighth of the frame's width, centred on (x, y) */
const markBox = (x, y, f) => { const w = VB.w / (f || 8), h = w * VB.h / VB.w; return {x: x - w / 2, y: y - h / 2, w, h}; };
/* a phone's view of an outside level: the middle 760 units, as tall as the box */
const opv = () => { const hw = phHW(), h = 760 * hw; return {x: 130, y: 330 - h / 2, w: 760, h}; };
/* the backdrop: the night sky for the levels in space, the page for the rest; it covers the desktop's frame and the
   phone's view (an opaque backdrop: while the camera zooms, the view behind never shows through) */
function obd(L, sky) {
  S(E('rect', {class: 'zbd', x: VB.x, y: -120, width: VB.w, height: 860, rx: 14, 'pointer-events': 'none'}, L), {fill: sky ? '#070b17' : 'var(--page)'});
  L.classList.add('oscn'); if (sky) L.classList.add('sky');
  L._sky = !!sky;
}
/* the photos on the night sky: their edges fade into it (a square of the photo's own black on the navy sky looked
   pasted on; review of 1 Oct), and the Blue Marble is cut to its disc; masks and a clip shared by every layer */
function ofDefs() {
  if (svg.querySelector('#ofdefs')) return;
  const d = E('defs', {id: 'ofdefs'}, svg);
  [['ofgx', 1, 0], ['ofgy', 0, 1]].forEach(([id, x2, y2]) => {
    const g = E('linearGradient', {id, x1: 0, y1: 0, x2, y2}, d);
    [[0, '#000'], [0.09, '#fff'], [0.91, '#fff'], [1, '#000']].forEach(([o, c]) => E('stop', {offset: o, 'stop-color': c}, g));
  });
  [['ofmx', 'ofgx'], ['ofmy', 'ofgy']].forEach(([id, gid]) => { const m = E('mask', {id, maskContentUnits: 'objectBoundingBox'}, d); E('rect', {x: 0, y: 0, width: 1, height: 1, fill: `url(#${gid})`}, m); });
  E('circle', {cx: 0.5, cy: 0.5, r: 0.445}, E('clipPath', {id: 'ofdisc', clipPathUnits: 'objectBoundingBox'}, d));
}
/* a line of text that a phone wraps (its view is 760 units wide and its type larger): split at the clause break
   nearest the middle */
function owrap(parent, x, y, str, cls, anchor, fids, max) {
  const lim = max || 46;
  if (!PH || str.length <= lim) return T(parent, x, y, str, cls, anchor, fids);
  const mid = str.length / 2; let best = -1;
  for (const sep of ['; ', ': ', ', ', ' ']) { let i = -1; while ((i = str.indexOf(sep, i + 1)) >= 0) if (best < 0 || Math.abs(i - mid) < Math.abs(best - mid)) best = i; if (best > 0 && Math.abs(best - mid) < str.length / 4) break; }
  if (best <= 0) return T(parent, x, y, str, cls, anchor, fids);
  const a = str.slice(0, best + 1).trim(), b = str.slice(best + 1).trim();
  return T2(parent, x, y, [a, b], cls, anchor, fids, 1.15);
}
/* the title, its tag (what kind of picture it is) and a line under it; on a phone the tag goes to the bottom corner */
function otitle(L, title, tag, sub, subf) {
  const g = E('g', {class: 'otl'}, L);
  T(g, 140, -40, title, 'o-t');
  if (tag) {
    const fw = PH ? 14.2 : 9.6, w = Math.round(tag.length * fw + 26), x = 880 - w, y = PH ? 690 : -62;
    S(E('rect', {x, y, width: w, height: PH ? 38 : 28, rx: 14}, g), {fill: 'none', stroke: 'currentColor', strokeWidth: 1.5});
    T(g, x + w / 2, y + (PH ? 27 : 20), tag, 'o-tag', 'middle');
  }
  if (sub) owrap(g, 140, PH ? -6 : -12, sub, 'o-s', 'start', subf);
  return g;
}
/* a scale bar: len units long, labelled */
function sbar(L, x, y, len, label, fids) {
  const g = E('g', {class: 'sbar', 'pointer-events': 'none'}, L);
  E('path', {d: `M${x},${y - 7}v7h${len}v-7`, class: 'sb'}, g);
  T(g, x + len + 10, y + 2, label, 'o-s ohalo', 'start', fids);
  return g;
}
/* an image's credit under it (on a phone, where the drawing is narrow, only in the panel's "You are here"); one line of at
   most about 130 characters, or it runs past the drawing's right edge (final check, 1 Oct: the card's and Earth's did) */
const ocredit = (L, t, y) => (PH ? null : T(L, 140, Math.min(y || 698, 698), t, 'o-cr'));
/* a part of an outside level: its panel's title, lead and facts (g._info) and, if it leads to a scale, that scale */
function opart(parent, key, label, info, kid) {
  const g = comp(parent, key, {}, label);
  g._info = info; g._kid = kid || null;
  return g;
}
/* a transparent hotspot over a picture, ringed when focused or selected */
function hot(parent, key, r, label, info, kid, o) {
  o = o || {};
  const g = opart(parent, key, label, info, kid);
  S(E('rect', {class: 'shape hotr', x: r.x, y: r.y, width: r.w, height: r.h, rx: o.rx == null ? 6 : o.rx}, g), {strokeDasharray: o.dash || null});
  E('rect', {class: 'ring', x: r.x - 5, y: r.y - 5, width: r.w + 10, height: r.h + 10, rx: (o.rx == null ? 6 : o.rx) + 4}, g);
  if (o.lab) { const t = T(g, o.lx != null ? o.lx : r.x, o.ly != null ? o.ly : r.y - 10, o.lab, o.lcls || 'o-s', o.la || 'start', o.lf); if (o.halo) t.classList.add('ohalo'); }
  return g;
}
/* an image of the folder, lazy (built only when the camera comes near); a failed load leaves the drawing and says so */
function oimg(L, file, x, y, w, h, o) {
  o = o || {};
  if (o.feather || o.clip) ofDefs();
  const host = o.feather ? E('g', {mask: 'url(#ofmx)'}, L) : L;
  const im = E('image', {href: IMGDIR + file, x, y, width: w, height: h, preserveAspectRatio: o.par || 'xMidYMid meet', 'pointer-events': 'none'}, host);
  if (o.feather) im.setAttribute('mask', 'url(#ofmy)');
  if (o.clip) im.setAttribute('clip-path', o.clip);
  im.addEventListener('error', () => { im.style.display = 'none'; T(L, x + w / 2, y + h / 2, 'photo not loaded', 'o-l', 'middle'); });
  return im;
}
/* a level's facts by number (out.<id>.<n>) */
const ofx = (id, ...ns) => ns.map(n => `out.${id}.${n}`).filter(f => F[f]);
/* the info for a part that stands for the level inside it: its name, its lead, the next level's facts */
const kidInfo = (id, lead) => ({title: (OSC[id] || {}).name || id, lead: lead || (OSC[id] || {}).blurb || '', facts: (OSC[id] || {}).facts || []});
/* a marked jump: a ring at (x, y) of radius r, labelled, its box the seat of the level inside */
function jumpMark(L, ap, kid, x, y, r, label, o) {
  o = o || {};
  const g = opart(L, 'to-' + kid, `${label}: zoom in`, kidInfo(kid, o.lead), {id: kid});
  S(E('circle', {class: 'shape mk', cx: x, cy: y, r}, g), {});
  E('circle', {class: 'ring', cx: x, cy: y, r: r + 6}, g);
  if (o.dot) S(E('circle', {cx: x, cy: y, r: o.dot, 'pointer-events': 'none'}, g), {fill: o.dotc || 'currentColor'});
  // a hit area at least 44 CSS px on a phone
  S(E('circle', {cx: x, cy: y, r: Math.max(r + 8, 36), 'pointer-events': 'all'}, g), {fill: 'transparent'});
  if (label) {
    const tx = x + (o.lx || r + 10), ty = y + (o.ly || 6), cls = o.lcls || 'o-l', fs = (PH ? 6 : 0) + (/o-l/.test(cls) ? 21 : 18), tw = label.length * fs * 0.54, an = o.la || 'start';
    // the label is part of the marker's hit area (review of 1 Oct: a click on it selected the part behind)
    S(E('rect', {x: an === 'middle' ? tx - tw / 2 - 6 : an === 'end' ? tx - tw - 6 : tx - 6, y: ty - fs - 4, width: tw + 12, height: fs * 1.35 + 8, 'pointer-events': 'all'}, g), {fill: 'transparent'});
    const t = T(g, tx, ty, label, cls, an, o.lf); if (o.halo) t.classList.add('ohalo');
  }
  ap.zs[kid] = {r: o.box || markBox(x, y, o.f), g, tr: 'jump'};
  return g;
}
/* the outline paths of the maps (km, y south) drawn at scale k with the km point (x0, y0) at (X, Y) */
function mapG(L, k, x0, y0, X, Y) { return E('g', {transform: `matrix(${k},0,0,${k},${X - k * x0},${Y - k * y0})`, class: 'map'}, L); }
const kmR = (b, k, x0, y0, X, Y) => ({x: X + k * (b[0] - x0), y: Y + k * (b[1] - y0), w: k * (b[2] - b[0]), h: k * (b[3] - b[1])});
/* a map's bbox fitted into the area A: the scale and the placement */
function fitMap(bb, A) {
  const k = Math.min(A.w / (bb[2] - bb[0]), A.h / (bb[3] - bb[1])), w = k * (bb[2] - bb[0]), h = k * (bb[3] - bb[1]);
  return {k, x0: bb[0], y0: bb[1], X: A.x + (A.w - w) / 2, Y: A.y + (A.h - h) / 2};
}
const MAPA = rc(140, 10, 740, 660);   // the area a map fills (under its title)
/* San Francisco's map leaves the right-hand column to the Studio 45 inset, so that the inset is off the map: the
   camera's dive into it never lands on a place in the city (review of 1 Oct) */
const MAPAS = () => ({sf: rc(140, 20, 740, 650)});
const geoFit = id => fitMap(OGEO[id].bbox_km, MAPAS()[id] || MAPA);
const geoSeat = (childId, bbParent, fp) => seatMap(VB, (() => { const f = geoFit(childId); return kmR(OGEO[childId].bbox_km, f.k, f.x0, f.y0, f.X, f.Y); })(), kmR(bbParent, fp.k, fp.x0, fp.y0, fp.X, fp.Y));
function onode(id, o) {
  const s = OSC[id] || {};
  return node(id, Object.assign({
    name: () => s.name || id, short: () => s.short || id, to: () => (s.name || id).replace(/^The /, 'the '),
    size: () => scSz(s) || {m: null, kind: 'unknown', f: s.f || null},
    frame: () => VB, pv: () => opv(), out: true, egg: !!s.egg,
    def: () => (o.kid ? {id: o.kid} : null), kids: () => (o.kid ? [{id: o.kid}] : []),
    imgs: () => (o.img || []).map(f => IMGDIR + f),
  }, o));
}

/* ---- beyond what we can see: our sphere among others that may or may not be there ---- */
const U = {cx: 510, cy: 345, r: 330};   // the observable universe's circle in its own scene (on a phone, lower: cy 375)
const UC = () => (PH ? Object.assign({}, U, {cy: 375}) : U);
onode('beyond', {kid: 'universe', to: () => 'what lies beyond (speculative)', build: (L, ap) => {
  obd(L, true);
  otitle(L, 'Beyond what we can see', 'speculative', 'how far space goes on is unknown: a hypothesis, not an observation', 'out.beyond.3');
  const B = {cx: 510, cy: 335, r: U.r / 2.7};
  const go = opart(L, 'others', 'Other regions, perhaps other universes: details', {title: 'Other regions (speculative)', kick: 'Beyond · hypothesis',
    lead: 'Space is measured to be flat to within a fraction of a percent, which suggests it goes on well past what we can see. Whether there are other universes, a multiverse, is a hypothesis: nothing observed so far confirms or rules it out.', facts: ofx('beyond', 1, 2, 3)});
  [[230, 210, 105], [800, 230, 120], [300, 520, 95], [760, 520, 110], [520, 80, 70], [150, 380, 60], [880, 390, 70]].forEach(([x, y, r], i) => {
    S(E('circle', {class: 'shape ghost', cx: x, cy: y, r}, go), {opacity: 0.55 - i * 0.05});
  });
  E('rect', {class: 'ring', x: 120, y: 60, width: 800, height: 580, rx: 20}, go);
  T(go, 230, 340, 'other regions?', 'o-s', 'middle'); T(go, 780, 610, 'size unknown', 'o-s', 'middle');
  const g = opart(L, 'obs', 'Our observable universe: zoom in', kidInfo('universe'), {id: 'universe'});
  S(E('circle', {class: 'shape univ', cx: B.cx, cy: B.cy, r: B.r}, g), {});
  E('circle', {class: 'ring', cx: B.cx, cy: B.cy, r: B.r + 7}, g);
  T(g, B.cx, B.cy - 6, 'our observable', 'o-l', 'middle'); T(g, B.cx, B.cy + 20, 'universe', 'o-l', 'middle');
  ap.zs.universe = {r: seatMap(VB, cR(UC().cx, UC().cy, U.r), cR(B.cx, B.cy, B.r)), g};
  owrap(L, 140, PH ? 630 : 690, 'No scale: the size of the whole is unknown, so this frame is only a picture.', 'o-s');
}});
/* ---- the observable universe ---- */
onode('universe', {kid: 'laniakea', img: ['cmb.webp'], build: (L, ap) => {
  const U = UC();
  obd(L, true);
  otitle(L, 'The observable universe', 'drawn to scale', `${on('u_age')} since the Big Bang; ${on('u_rad')} in radius`, `${onf('u_age')} ${onf('u_rad')}`);
  const g = opart(L, 'sphere', 'The observable universe: details', {title: 'Everything we can see', kick: 'Universe · part', lead: (OSC.universe || {}).blurb, facts: ofx('universe', 1, 2, 4)});
  S(E('circle', {class: 'shape univ2', cx: U.cx, cy: U.cy, r: U.r}, g), {});
  E('circle', {class: 'ring', cx: U.cx, cy: U.cy, r: U.r + 8}, g);
  const gc = opart(L, 'cmb', 'The cosmic microwave background: details', {title: 'The cosmic microwave background', kick: 'Universe · part',
    lead: 'The oldest light we can see. It left its source about 380,000 years after the Big Bang, and it reaches us from every direction: the edge of what we can see.', facts: ofx('universe', 3)});
  S(E('circle', {class: 'shape cmbr', cx: U.cx, cy: U.cy, r: U.r - 6}, gc), {});
  S(E('circle', {cx: U.cx, cy: U.cy, r: U.r - 6, 'pointer-events': 'stroke'}, gc), {fill: 'none', stroke: 'transparent', strokeWidth: 44});
  E('circle', {class: 'ring', cx: U.cx, cy: U.cy, r: U.r + 2}, gc);
  if (PH) T2(gc, U.cx - 90, U.cy + U.r - 104, ['the oldest light:', `${on('u_cmb')} after the Big Bang`], 'o-s ohalo', 'middle', onf('u_cmb'), 1.15);
  else T(gc, U.cx, U.cy + U.r - 64, `the oldest light: ${on('u_cmb')} after the Big Bang`, 'o-s ohalo', 'middle', onf('u_cmb'));
  jumpMark(L, ap, 'laniakea', U.cx, U.cy, 26, 'you are here: Laniakea, a dot at this scale', {dot: 3, lx: -14, ly: 52, la: 'middle', lcls: 'o-s', halo: true});
  // the whole sky, as we see it from inside (WMAP)
  const ix = PH ? 650 : 900, iy = PH ? 560 : 40, iw = PH ? 230 : 300;
  const gi = opart(L, 'wmap', 'The microwave sky (WMAP): details', {title: 'The whole sky, as we see it', kick: 'Universe · image',
    lead: 'A map of the microwave background over the whole sky, seen from inside the sphere (the Mollweide projection of a globe). Its spots are the seeds of the galaxies.', facts: ofx('universe', 3)});
  oimg(gi, 'cmb.webp', ix, iy, iw, iw / 2);
  E('rect', {class: 'shape hotr', x: ix, y: iy, width: iw, height: iw / 2, rx: 6}, gi); E('rect', {class: 'ring', x: ix - 5, y: iy - 5, width: iw + 10, height: iw / 2 + 10, rx: 9}, gi);
  if (!PH) T(gi, ix, iy + iw / 2 + 24, 'the whole sky as we see it (WMAP)', 'o-s');
  sbar(L, 140, 680, 10 * 330 / 46.2, '10 billion light-years', onf('u_rad'));
}});
/* ---- Laniakea ---- */
onode('laniakea', {kid: 'localgroup', build: (L, ap) => {
  obd(L, true);
  otitle(L, 'Laniakea', 'schematic', `our supercluster: ${on('lan_n')}, ${on('lan_size')} across`, `${onf('lan_n')} ${onf('lan_size')}`);
  const cx = 500, cy = 350, R = 290, pts = [];
  for (let i = 0; i < 24; i++) { const a = i / 24 * 2 * Math.PI, r = R * (0.86 + 0.14 * Math.sin(3 * a + 0.7) + 0.06 * Math.cos(5 * a)); pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a) * 0.9]); }
  const n = pts.length, f1 = v => v.toFixed(1);
  let d = `M${f1(pts[0][0])},${f1(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    d += `C${f1(p1[0] + (p2[0] - p0[0]) / 6)},${f1(p1[1] + (p2[1] - p0[1]) / 6)} ${f1(p2[0] - (p3[0] - p1[0]) / 6)},${f1(p2[1] - (p3[1] - p1[1]) / 6)} ${f1(p2[0])},${f1(p2[1])}`;
  }
  d += 'Z';
  const g = opart(L, 'flow', 'Laniakea: details', {title: 'Laniakea, "immeasurable heaven"', kick: 'Laniakea · part', lead: (OSC.laniakea || {}).blurb, facts: ofx('laniakea', 1, 2)});
  S(E('path', {class: 'shape lani', d}, g), {});
  const ga = {x: cx + 40, y: cy + 30};
  for (let i = 0; i < 14; i++) {
    const a = i / 14 * 2 * Math.PI + 0.2, r0 = R * 0.95, x0 = cx + r0 * Math.cos(a), y0 = cy + r0 * Math.sin(a) * 0.9;
    E('path', {class: 'flowl', d: `M${x0.toFixed(1)},${y0.toFixed(1)} Q${((x0 + ga.x) / 2 + 40 * Math.sin(a)).toFixed(1)},${((y0 + ga.y) / 2 - 40 * Math.cos(a)).toFixed(1)} ${ga.x},${ga.y}`}, g);
  }
  E('path', {class: 'ring', d}, g);
  S(E('circle', {cx: ga.x, cy: ga.y, r: 8}, g), {fill: '#ffd27a'});
  if (PH) T2(g, ga.x + 14, ga.y + 30, ['where the galaxies’', 'motions converge'], 'o-s ohalo', 'start', null, 1.15); else T(g, ga.x + 14, ga.y + 30, 'where the galaxies’ motions converge', 'o-s');
  owrap(L, 140, PH ? 636 : 680, 'shape simplified: no openly licensed map; the outline and flows are a sketch of Tully et al. 2014', 'o-s');
  const lg = {x: cx - R * 0.72, y: cy - R * 0.52};
  jumpMark(L, ap, 'localgroup', lg.x, lg.y, 18, 'the Local Group', {dot: 3, lx: 26, ly: -8});
  sbar(L, PH ? 140 : 600, PH ? 600 : 650, 100 * 2 * R * 0.93 / 520, '100 million light-years', onf('lan_size'));
}});
/* ---- the Local Group ---- */
const LGK = 120;   // units per million light-years
onode('localgroup', {kid: 'milkyway', img: ['andromeda.webp'], build: (L, ap) => {
  obd(L, true);
  otitle(L, 'The Local Group', 'drawn to scale, positions schematic', `our galaxy's neighbourhood: more than 130 known galaxies, most of them faint dwarfs, over nearly ${on('lg_size')}`, `${onf('lg_size')} out.localgroup.5`);
  const mw = {x: 280, y: 400}, m31 = {x: mw.x + 2.5 * LGK, y: mw.y}, m33 = {x: mw.x + 2.92 * LGK, y: mw.y - 0.68 * LGK};
  S(E('line', {x1: mw.x, y1: mw.y, x2: m31.x, y2: m31.y, 'pointer-events': 'none'}, L), {stroke: '#7a86a6', strokeWidth: 1.5, strokeDasharray: '6 6'});
  T(L, (mw.x + m31.x) / 2, mw.y + 34, on('lg_m31'), 'o-s', 'middle', onf('lg_m31'));
  const ga = opart(L, 'm31', 'Andromeda (M31): details', {title: 'Andromeda (M31)', kick: 'Local Group · galaxy', lead: 'The nearest big galaxy, larger than ours. The light we see from it left 2.5 million years ago. It and the Milky Way may collide in some billions of years: about a coin flip within ten billion.', facts: ofx('localgroup', 2, 4)});
  S(E('ellipse', {class: 'shape gal', cx: m31.x, cy: m31.y, rx: 0.13 * LGK, ry: 0.045 * LGK, transform: `rotate(-35 ${m31.x} ${m31.y})`}, ga), {});
  S(E('circle', {cx: m31.x, cy: m31.y, r: 30}, ga), {fill: 'transparent'}); E('circle', {class: 'ring', cx: m31.x, cy: m31.y, r: 26}, ga);
  T(ga, m31.x, m31.y - 30, 'Andromeda (M31)', 'o-l', 'middle');
  const gm = opart(L, 'm33', 'Triangulum (M33): details', {title: 'Triangulum (M33)', kick: 'Local Group · galaxy', lead: 'The third largest galaxy of the group, near Andromeda.', facts: ofx('localgroup', 3)});
  S(E('ellipse', {class: 'shape gal', cx: m33.x, cy: m33.y, rx: 4, ry: 2.5}, gm), {});
  S(E('circle', {cx: m33.x, cy: m33.y, r: 24}, gm), {fill: 'transparent'}); E('circle', {class: 'ring', cx: m33.x, cy: m33.y, r: 18}, gm);
  T(gm, m33.x - 12, m33.y - 12, `M33, ${on('lg_m33')}`, 'o-s', 'end', onf('lg_m33'));
  const gl = opart(L, 'lmc', 'The Large Magellanic Cloud: details', {title: 'The Large Magellanic Cloud', kick: 'Local Group · galaxy', lead: 'A small galaxy orbiting our own, 160,000 light-years away: seen from the southern hemisphere as a faint cloud.', facts: ofx('localgroup', 3)});
  S(E('circle', {cx: mw.x - 0.1 * LGK, cy: mw.y + 0.12 * LGK, r: 2.5, 'pointer-events': 'none'}, gl), {fill: '#c9d3ea'});
  S(E('circle', {cx: mw.x - 0.1 * LGK, cy: mw.y + 0.12 * LGK, r: 22, 'pointer-events': 'all'}, gl), {fill: 'transparent'}); E('circle', {class: 'ring', cx: mw.x - 0.1 * LGK, cy: mw.y + 0.12 * LGK, r: 14}, gl);
  T(gl, PH ? mw.x - 120 : mw.x - 30, mw.y + (PH ? 76 : 60), `LMC, ${on('lg_lmc')} ly`, 'o-s', PH ? 'start' : 'end', onf('lg_lmc'));
  S(E('ellipse', {cx: mw.x, cy: mw.y, rx: 0.05 * LGK, ry: 0.018 * LGK, 'pointer-events': 'none'}, L), {fill: '#e7ecff'});
  jumpMark(L, ap, 'milkyway', mw.x, mw.y, 16, 'the Milky Way', PH ? {lx: -10, ly: -26, la: 'middle'} : {lx: -8, ly: -26, la: 'end'});
  // Andromeda, photographed (GALEX, ultraviolet)
  const ix = PH ? 600 : 700, iy = PH ? 440 : 70, iw = PH ? 270 : 330, ih = iw * 357 / 480;
  const gp = opart(L, 'm31photo', 'Andromeda, photographed: details', {title: 'Andromeda, photographed', kick: 'Local Group · image', lead: 'Andromeda in ultraviolet light from NASA’s GALEX telescope: bluer than to the eye. It spans 260,000 light-years.', facts: ofx('localgroup', 2)});
  oimg(gp, 'andromeda.webp', ix, iy, iw, ih, {feather: true});
  E('rect', {class: 'shape hotr', x: ix, y: iy, width: iw, height: ih, rx: 6}, gp); E('rect', {class: 'ring', x: ix - 5, y: iy - 5, width: iw + 10, height: ih + 10, rx: 9}, gp);
  // (on a phone the credit is short, under the photo's right edge: the full one is in the panel)
  if (PH) T(gp, ix + iw, iy + ih + 22, 'GALEX, ultraviolet', 'o-cr', 'end'); else T(gp, ix, iy + ih + 24, 'Andromeda (NASA/JPL-Caltech GALEX, ultraviolet)', 'o-cr');
  if (!PH) S(E('line', {x1: m31.x, y1: m31.y - 12, x2: ix + iw * 0.3, y2: iy + ih, 'pointer-events': 'none'}, L), {stroke: '#7a86a6', strokeWidth: 1.2, strokeDasharray: '4 5'});
  sbar(L, 140, 680, LGK, '1 million light-years');
}});
/* ---- the Milky Way (an artist's concept) ---- */
const MWI = {x: 170, y: -4, s: 680};
onode('milkyway', {kid: 'stars', img: ['milkyway.webp'], build: (L, ap) => {
  obd(L, true);
  const g = opart(L, 'disc', 'The Milky Way: details', {title: 'The Milky Way', kick: 'Milky Way · part', lead: (OSC.milkyway || {}).blurb, facts: ofx('milkyway', 1, 3)});
  S(E('ellipse', {cx: 510, cy: MWI.y + 0.495 * MWI.s, rx: 300, ry: 300, 'pointer-events': 'none'}, g), {fill: '#1b2440'});
  oimg(g, 'milkyway.webp', MWI.x, MWI.y, MWI.s, MWI.s, {feather: true});
  E('rect', {class: 'shape hotr', x: MWI.x, y: MWI.y, width: MWI.s, height: MWI.s, rx: 6}, g);
  E('rect', {class: 'ring', x: MWI.x - 5, y: MWI.y - 5, width: MWI.s + 10, height: MWI.s + 10, rx: 9}, g);
  otitle(L, 'The Milky Way', 'an artist’s concept', `about ${on('mw_size')} across`, onf('mw_size'));
  const sun = {x: MWI.x + 0.5 * MWI.s, y: MWI.y + 0.691 * MWI.s}, ctr = {x: MWI.x + 0.5 * MWI.s, y: MWI.y + 0.495 * MWI.s};
  S(E('line', {x1: sun.x, y1: sun.y - 20, x2: ctr.x, y2: ctr.y, 'pointer-events': 'none'}, L), {stroke: '#ffd27a', strokeWidth: 2, strokeDasharray: '6 5'});
  T(L, ctr.x + 12, (sun.y + ctr.y) / 2, on('mw_sun'), 'o-l ohalo', 'start', onf('mw_sun'));
  const gc = opart(L, 'centre', 'The centre of the galaxy: details', {title: 'The centre of the Milky Way', kick: 'Milky Way · part', lead: 'The Sun is about 26,000 light-years from the centre, in a small arm called the Orion Spur.', facts: ofx('milkyway', 2)});
  S(E('circle', {cx: ctr.x, cy: ctr.y, r: 26}, gc), {fill: 'transparent'}); E('circle', {class: 'ring', cx: ctr.x, cy: ctr.y, r: 22}, gc);
  jumpMark(L, ap, 'stars', sun.x, sun.y, 20, 'you are here: the Sun', {lx: 28, ly: 8, halo: true, lcls: 'o-l'});
  ocredit(L, 'Image: NASA/JPL-Caltech/R. Hurt (SSC/Caltech), PIA10748, an artist’s concept: nobody has seen the galaxy from outside', 712);
  sbar(L, 140, 666, 20000 / (282.1 * 480 / MWI.s), '20,000 light-years');
}});
/* ---- the nearest stars ---- */
onode('stars', {kid: 'solar', build: (L, ap) => {
  obd(L, true);
  otitle(L, 'The nearest stars', 'drawn to scale', 'a frame 20 light-years across, the Sun at its middle');
  const k = 700 / 20, c = {x: 510, y: 345}, pr = 4.2 * k, a = 3.55;
  S(E('circle', {cx: c.x, cy: c.y, r: pr, 'pointer-events': 'none'}, L), {fill: 'none', stroke: '#5b6787', strokeWidth: 1.5, strokeDasharray: '6 6'});
  const px = c.x + pr * Math.cos(a), py = c.y + pr * Math.sin(a);
  const gp = opart(L, 'proxima', 'Proxima Centauri: details', {title: 'Proxima Centauri', kick: 'Nearest stars · star', lead: 'The nearest star after the Sun: its light left it more than four years ago.', facts: ofx('stars', 1, 2)});
  S(E('circle', {cx: px, cy: py, r: 4}, gp), {fill: '#ffb07a'}); S(E('circle', {cx: px, cy: py, r: 26}, gp), {fill: 'transparent'}); E('circle', {class: 'ring', cx: px, cy: py, r: 20}, gp);
  T(gp, PH ? px + 40 : px - 10, PH ? py - 40 : py - 18, 'Proxima and α Centauri', 'o-l', PH ? 'middle' : 'end');
  T(gp, px - 10, py + 34, on('st_prox'), 'o-s', 'end', onf('st_prox'));
  S(E('circle', {cx: c.x, cy: c.y, r: 4, 'pointer-events': 'none'}, L), {fill: '#ffe08a'});
  jumpMark(L, ap, 'solar', c.x, c.y, 16, 'the Sun', {lx: 24, ly: 6});
  owrap(L, 140, PH ? 610 : 650, 'one light-year: 9.46 × 10¹⁵ m, about 1,050 times the width of Neptune’s orbit', 'o-s', 'start', 'out.stars.2');
  sbar(L, 140, 690, 5 * k, '5 light-years');
}});
/* ---- the Solar System ---- */
const AU = 330 / 30.07;
onode('solar', {kid: 'moon', build: (L, ap) => {
  obd(L, true);
  otitle(L, 'The Solar System', 'orbits to scale, planets not', `the planets' orbits out to Neptune's, ${on('so_nep')}`, onf('so_nep'));
  const c = {x: 510, y: 350};
  const orb = [['Mercury', 0.387], ['Venus', 0.723], ['Earth', 1], ['Mars', 1.524], ['Jupiter', 5.2], ['Saturn', 9.57], ['Uranus', 19.17], ['Neptune', 30.07]];
  const gp = opart(L, 'planets', 'The planets: details', {title: 'The Sun and its planets', kick: 'Solar System · part', lead: (OSC.solar || {}).blurb, facts: ofx('solar', 1, 2)});
  orb.forEach(([nm, a], i) => {
    S(E('circle', {class: 'orb', cx: c.x, cy: c.y, r: a * AU}, gp), {});
    if (i >= 4) { const an = -0.9 + i * 0.5, x = c.x + a * AU * Math.cos(an), y = c.y + a * AU * Math.sin(an); S(E('circle', {cx: x, cy: y, r: 4}, gp), {fill: '#cdd6ee'}); T(gp, x + 10, y - 8, nm, 'o-s'); }
  });
  E('rect', {class: 'ring', x: c.x - 340, y: c.y - 340, width: 680, height: 680, rx: 340}, gp);
  S(E('circle', {cx: c.x, cy: c.y, r: 340}, gp), {fill: 'transparent'});
  S(E('circle', {cx: c.x, cy: c.y, r: 3.5, 'pointer-events': 'none'}, L), {fill: '#ffe08a'});
  if (PH) T2(L, c.x + 30, c.y + 170, ['Mercury to Mars:', 'the small rings'], 'o-s ohalo', 'start', null, 1.15); else T(L, c.x - 30, c.y + 52, 'Mercury to Mars: the small rings', 'o-s ohalo', 'end');
  const ea = -0.75, ex = c.x + AU * Math.cos(ea), ey = c.y + AU * Math.sin(ea);
  jumpMark(L, ap, 'moon', ex, ey, 9, PH ? `Earth: ${on('so_earth')} of light` : `Earth, ${on('so_earth')} of light from the Sun`, {dot: 2.5, lx: 16, ly: -14, lf: onf('so_earth'), halo: true});
  const gv = opart(L, 'voyager', 'Voyager 1: details', {title: 'Voyager 1', kick: 'Solar System · spacecraft', lead: 'The farthest spacecraft: on 18 November 2026 it is one light-day from Earth, so a command takes a day to arrive and the answer another day.', facts: ofx('solar', 3)});
  E('path', {class: 'voy', d: `M${c.x + 250},${c.y - 250} L${c.x + 330},${c.y - 330}`}, gv); E('path', {class: 'voy', d: `M${c.x + 316},${c.y - 334} L${c.x + 332},${c.y - 332} L${c.x + 330},${c.y - 316}`}, gv);
  S(E('rect', {x: c.x + 236, y: c.y - 370, width: 150, height: 130}, gv), {fill: 'transparent'}); E('rect', {class: 'ring', x: c.x + 231, y: c.y - 375, width: 160, height: 140, rx: 8}, gv);
  if (PH) { T(gv, c.x + 235, c.y - 262, `Voyager 1: ${on('so_voy')},`, 'o-s ohalo', 'end', onf('so_voy')); T(gv, c.x + 235, c.y - 236, 'one light-day (off the frame)', 'o-s ohalo', 'end'); }
  else { T(gv, c.x + 340, c.y - 344, `Voyager 1: ${on('so_voy')},`, 'o-s', 'start', onf('so_voy')); T(gv, c.x + 340, c.y - 322, 'one light-day (off the frame)', 'o-s'); }
  sbar(L, 140, PH ? 652 : 690, 5 * AU, '5 au (1 au: Earth to the Sun)');
}});
/* ---- Earth and the Moon ---- */
onode('moon', {kid: 'earth', build: (L, ap) => {
  obd(L, true);
  otitle(L, 'Earth and the Moon', 'orbit to scale', `the Moon ${on('mo_dist')} away: ${on('mo_light')} for light`, `${onf('mo_dist')} ${onf('mo_light')}`);
  const c = {x: 510, y: 350}, R = 300, k = R / 384400;
  S(E('circle', {cx: c.x, cy: c.y, r: R, 'pointer-events': 'none'}, L), {fill: 'none', stroke: '#5b6787', strokeWidth: 1.5, strokeDasharray: '6 6'});
  const ma = -0.5, mx = c.x + R * Math.cos(ma), my = c.y + R * Math.sin(ma);
  const gm = opart(L, 'moonp', 'The Moon: details', {title: 'The Moon', kick: 'Earth and Moon · part', lead: 'Light takes 1.28 seconds to reach the Moon: in that time the chip’s clock ticks 770 million times.', facts: ofx('moon', 1, 2)});
  S(E('circle', {cx: mx, cy: my, r: Math.max(2.5, 1737.4 * k)}, gm), {fill: '#cfd3dc'}); S(E('circle', {cx: mx, cy: my, r: 26}, gm), {fill: 'transparent'}); E('circle', {class: 'ring', cx: mx, cy: my, r: 18}, gm);
  T(gm, PH ? mx - 16 : mx + 16, PH ? my - 26 : my - 12, 'the Moon', 'o-l', PH ? 'end' : 'start');
  S(E('circle', {cx: c.x, cy: c.y, r: 6371 * k, 'pointer-events': 'none'}, L), {fill: '#5f8fe0'});
  jumpMark(L, ap, 'earth', c.x, c.y, 14, 'Earth', {lx: 20, ly: 24});
  sbar(L, 140, 690, 100000 * k, '100,000 km');
}});
/* ---- Earth: Natural Earth's land on an orthographic globe at 38 N 100 W, to scale with the US map ---- */
const EG = {cx: 510, cy: 345, r: 310};
onode('earth', {kid: 'us', img: ['earth.webp'], build: (L, ap) => {
  obd(L, true);
  otitle(L, 'Earth', 'drawn to scale', `${on('ea_r')} km to the centre; light circles it in ${on('ea_eq')}`, `${onf('ea_r')} ${onf('ea_eq')}`);
  const ge = OGEO.earth, k = EG.r / ge.radius_km;
  const g = opart(L, 'globe', 'Earth: details', {title: 'Earth', kick: 'Earth · part', lead: (OSC.earth || {}).blurb, facts: ofx('earth', 1, 2)});
  S(E('circle', {class: 'shape ocean', cx: EG.cx, cy: EG.cy, r: EG.r}, g), {});
  E('circle', {class: 'ring', cx: EG.cx, cy: EG.cy, r: EG.r + 7}, g);
  const m = mapG(g, k, 0, 0, EG.cx, EG.cy);
  E('path', {class: 'land', d: ge.path}, m);
  const bb = ge.us_bbox_km, ur = kmR(bb, k, 0, 0, EG.cx, EG.cy);
  const gu = opart(L, 'tous', 'The United States: zoom in', kidInfo('us'), {id: 'us'});
  S(E('rect', {class: 'shape kidbox', x: ur.x, y: ur.y, width: ur.w, height: ur.h, rx: 4}, gu), {});
  E('rect', {class: 'ring', x: ur.x - 5, y: ur.y - 5, width: ur.w + 10, height: ur.h + 10, rx: 8}, gu);
  T(gu, ur.x + ur.w / 2, ur.y - 10, 'the United States', 'o-l ohalo', 'middle');
  ap.zs.us = {r: geoSeat('us', bb, {k, x0: 0, y0: 0, X: EG.cx, Y: EG.cy}), g: gu};
  // the Blue Marble, as an inset (a photograph centred elsewhere: it does not line up with the drawn globe)
  const ix = PH ? 700 : 880, iy = PH ? 496 : 470, iw = PH ? 170 : 210;
  const gp = opart(L, 'marble', 'The Blue Marble image: details', {title: 'The Blue Marble', kick: 'Earth · image', lead: 'Earth as NASA’s Blue Marble shows it, the Americas in view: not one photograph but a composite of many satellite images (from the MODIS instrument) laid over a globe.', facts: ofx('earth', 1)});
  oimg(gp, 'earth.webp', ix, iy, iw, iw, {clip: 'url(#ofdisc)'});
  E('rect', {class: 'shape hotr', x: ix, y: iy, width: iw, height: iw, rx: iw / 2}, gp); E('rect', {class: 'ring', x: ix - 5, y: iy - 5, width: iw + 10, height: iw + 10, rx: iw / 2 + 5}, gp);
  if (!PH) T(gp, ix + iw / 2, iy - 12, 'the Blue Marble (NASA, a composite)', 'o-cr', 'middle');
  ocredit(L, 'Land: Natural Earth 1:110m, orthographic at 38 N 100 W. Image: NASA Goddard, The Blue Marble, a composite. Both public domain.', 712);
  sbar(L, 140, PH ? 680 : 664, 2000 * k, '2,000 km');
}});
/* ---- the maps: the US, California, the Bay Area, San Francisco (US Census outlines, public domain) ---- */
/* the ring a map's part shows when focused or selected: around the map's outline */
function mapRing(g, bb, f) { const r = kmR(bb, f.k, f.x0, f.y0, f.X, f.Y); E('rect', {class: 'ring', x: r.x - 6, y: r.y - 6, width: r.w + 12, height: r.h + 12, rx: 8}, g); }
function mapScene(L, ap, id, o) {
  obd(L, false);
  otitle(L, (OSC[id] || {}).name || id, 'map, to scale', o.sub, o.subf);
  const f = geoFit(id), m = mapG(L, f.k, f.x0, f.y0, f.X, f.Y);
  return {f, m};
}
onode('us', {kid: 'california', build: (L, ap) => {
  const ge = OGEO.us, {f, m} = mapScene(L, ap, 'us', {sub: `San Francisco to New York in fibre: ${on('us_sfny')} one way, on a straight cable`, subf: onf('us_sfny')});
  const gs = opart(L, 'states', 'The lower 48 states: details', {title: 'The United States', kick: 'United States · part', lead: (OSC.us || {}).blurb, facts: ofx('us', 1, 2)});
  ge.states.forEach(s0 => { if (s0.state !== 'California') E('path', {class: 'st', d: s0.path}, m); });
  E('rect', {class: 'ring', x: f.X, y: f.Y, width: f.k * (ge.bbox_km[2] - ge.bbox_km[0]), height: f.k * (ge.bbox_km[3] - ge.bbox_km[1]), rx: 8}, gs);
  gs.insertBefore(m, gs.firstChild);
  const P = c => ({x: f.X + f.k * (c[0] - f.x0), y: f.Y + f.k * (c[1] - f.y0)}), a = P(ge.sf_centre_km), b = P(ge.nyc_centre_km);
  const gl = opart(L, 'sfny', 'San Francisco to New York: details', {title: 'San Francisco to New York', kick: 'United States · distance', lead: 'Even on a perfectly straight fibre a signal takes about 20 ms one way: 12 million ticks of the chip’s clock. Real cables are longer and routers add delay.', facts: ofx('us', 2)});
  E('path', {class: 'arc', d: `M${a.x},${a.y} Q${(a.x + b.x) / 2},${Math.min(a.y, b.y) - 90} ${b.x},${b.y}`}, gl);
  [a, b].forEach(p => S(E('circle', {cx: p.x, cy: p.y, r: 5}, gl), {fill: 'var(--c2)'}));
  S(E('path', {d: `M${a.x},${a.y} Q${(a.x + b.x) / 2},${Math.min(a.y, b.y) - 90} ${b.x},${b.y}`, 'stroke-width': 16}, gl), {stroke: 'transparent', fill: 'none'});
  E('path', {class: 'ring', d: `M${a.x},${a.y} Q${(a.x + b.x) / 2},${Math.min(a.y, b.y) - 90} ${b.x},${b.y}`}, gl);
  T(gl, (a.x + b.x) / 2, Math.min(a.y, b.y) - 56, `${on('us_sfny_km')}: ${on('us_sfny')} in fibre`, 'o-s ohalo', 'middle', onf('us_sfny'));
  T(gl, b.x + 8, b.y + 24, 'New York', 'o-s', 'end');
  const ca = ge.states.find(s0 => s0.state === 'California'), cr = kmR(ge.california_bbox_km, f.k, f.x0, f.y0, f.X, f.Y);
  const gc = opart(L, 'toca', 'California: zoom in', kidInfo('california'), {id: 'california'});
  E('path', {class: 'st hl', d: ca.path, transform: m.getAttribute('transform')}, gc);
  E('rect', {class: 'ring', x: cr.x - 5, y: cr.y - 5, width: cr.w + 10, height: cr.h + 10, rx: 8}, gc);
  T(gc, cr.x + cr.w / 2, cr.y - 10, 'California', 'o-l ohalo', 'middle');
  ap.zs.california = {r: geoSeat('california', ge.california_bbox_km, f), g: gc};
  sbar(L, 140, PH ? 680 : 664, 1000 * f.k, '1,000 km');
  ocredit(L, 'Outlines: US Census Bureau, 2023 cartographic boundaries (public domain); Albers equal-area', 712);
}});
onode('california', {kid: 'bayarea', build: (L, ap) => {
  const ge = OGEO.california, {f, m} = mapScene(L, ap, 'california', {sub: `${on('ca_ns')} north to south: ${on('ca_ms')} in fibre`, subf: onf('ca_ns')});
  const g = opart(L, 'state', 'California: details', {title: 'California', kick: 'California · part', lead: (OSC.california || {}).blurb, facts: ofx('california', 1, 2)});
  g.appendChild(m); E('path', {class: 'st', d: ge.path}, m);
  mapRing(g, ge.bbox_km, f);
  const br = kmR(ge.bayarea_bbox_km, f.k, f.x0, f.y0, f.X, f.Y);
  const gb = opart(L, 'toba', 'The Bay Area: zoom in', kidInfo('bayarea'), {id: 'bayarea'});
  S(E('rect', {class: 'shape kidbox', x: br.x, y: br.y, width: br.w, height: br.h, rx: 4}, gb), {});
  E('rect', {class: 'ring', x: br.x - 5, y: br.y - 5, width: br.w + 10, height: br.h + 10, rx: 8}, gb);
  T(gb, PH ? br.x + br.w / 2 : br.x - 8, PH ? br.y - 14 : br.y + 20, 'the Bay Area', 'o-l ohalo', PH ? 'middle' : 'end');
  ap.zs.bayarea = {r: geoSeat('bayarea', ge.bayarea_bbox_km, f), g: gb};
  sbar(L, 640, 640, 200 * f.k, '200 km');
}});
onode('bayarea', {kid: 'sf', build: (L, ap) => {
  const ge = OGEO.bayarea, {f, m} = mapScene(L, ap, 'bayarea', {sub: `nine counties around the bay: ${on('ba_ms')} across in fibre`, subf: onf('ba_ms')});
  const g = opart(L, 'counties', 'The nine counties: details', {title: 'The Bay Area', kick: 'Bay Area · part', lead: (OSC.bayarea || {}).blurb, facts: ofx('bayarea', 1, 2, 3)});
  g.appendChild(m);
  ge.counties.forEach(c => { if (c.county !== 'San Francisco') E('path', {class: 'st', d: c.path}, m); });
  mapRing(g, ge.bbox_km, f);
  const sf = ge.counties.find(c => c.county === 'San Francisco');
  const gs = opart(L, 'tosf', 'San Francisco: zoom in', kidInfo('sf'), {id: 'sf'});
  E('path', {class: 'st hl', d: sf.path, transform: m.getAttribute('transform')}, gs);
  const sr = kmR(ge.sf_bbox_km, f.k, f.x0, f.y0, f.X, f.Y);
  E('rect', {class: 'ring', x: sr.x - 5, y: sr.y - 5, width: sr.w + 10, height: sr.h + 10, rx: 8}, gs);
  S(E('rect', {x: sr.x, y: sr.y, width: sr.w, height: sr.h}, gs), {fill: 'transparent'});
  // (a hit area of about 44 px on a phone: the city is small on this map)
  S(E('circle', {cx: sr.x + sr.w / 2, cy: sr.y + sr.h / 2, r: Math.max(50, sr.w / 2), 'pointer-events': 'all'}, gs), {fill: 'transparent'});
  T(gs, sr.x - 8, sr.y + 20, 'San Francisco', 'o-l ohalo', 'end');
  ap.zs.sf = {r: geoSeat('sf', ge.sf_bbox_km, f), g: gs};
  sbar(L, 640, 660, 50 * f.k, '50 km');
}});
/* ---- San Francisco: the city's outline, and in it the neighbourhood the owner names (1 Oct 2026: "Studio 45 is
   located on 29th Street, in Bernal Heights"): the camera nests into Bernal Heights' outline. No point, block or
   address of the studio is drawn on any map (AGENT.md §10): the street and the neighbourhood only. ---- */
const BERN = OGEO.bernal || null;
// the Bernal Heights level's frame (km on the San Francisco map's projection): the neighbourhood and the whole of 29th
// Street, which runs west into Noe Valley, with room for the neighbours' names
if (BERN) BERN.bbox_km = [0.1, 0.75, 3.6, 3.45];
onode('sf', {kid: 'bernal', build: (L, ap) => {
  const ge = OGEO.sf, {f, m} = mapScene(L, ap, 'sf', {sub: `about 11 km across: ${on('sf_us')} in fibre`, subf: onf('sf_us')});
  const g = opart(L, 'city', 'San Francisco: details', {title: 'San Francisco', kick: 'San Francisco · part', lead: (OSC.sf || {}).blurb, facts: ofx('sf', 1, 2, 3, 4)});
  g.appendChild(m); E('path', {class: 'st hl', d: ge.path}, m);
  mapRing(g, ge.bbox_km, f);
  if (BERN) {
    const gb = opart(L, 'tobernal', 'Bernal Heights: zoom in', kidInfo('bernal'), {id: 'bernal'});
    E('path', {class: 'st hood', d: BERN.bernal.path}, mapG(gb, f.k, f.x0, f.y0, f.X, f.Y));
    const br = kmR(BERN.bernal.bbox_km, f.k, f.x0, f.y0, f.X, f.Y);
    E('rect', {class: 'ring', x: br.x - 6, y: br.y - 6, width: br.w + 12, height: br.h + 12, rx: 8}, gb);
    // (a hit area of about 44 px on a phone: the neighbourhood is small on this map)
    S(E('circle', {cx: br.x + br.w / 2, cy: br.y + br.h / 2, r: Math.max(48, br.w * 0.6), 'pointer-events': 'all'}, gb), {fill: 'transparent'});
    T(gb, br.x + br.w + 12, br.y + br.h / 2 + 7, 'Bernal Heights', 'o-l ohalo');
    ap.zs.bernal = {r: geoSeat('bernal', BERN.bbox_km, f), g: gb};
  }
  sbar(L, 440, 650, 2 * f.k, '2 km');
}});
/* ---- Bernal Heights (DataSF's outlines, simplified; research/bernal-geo.json of the ladder's data): the hill and its
   park, the roads that bound it, the neighbours, and 29th Street drawn whole, never a point on it ---- */
const BROADS = {'Cesar Chavez St': [0.6, -14], 'San Jose Ave': [0.35, 22], 'US 101': [0.55, 22], 'I-280': [0.45, 26], 'Mission St': [0.62, 22], 'Cortland Ave': [0.5, 24]};
/* the middle of a path's points (km), for a label */
function pathAt(d, t) { const pts = (d.match(/-?[\d.]+,-?[\d.]+/g) || []).map(p => p.split(',').map(Number)); if (!pts.length) return null; return pts[Math.min(pts.length - 1, Math.floor(t * pts.length))]; }
onode('bernal', {kid: 'st29', build: (L, ap) => {
  const B = BERN, {f, m} = mapScene(L, ap, 'bernal', {sub: `${on('b_area')} on a hill, its summit ${on('b_sum')} high`, subf: `${onf('b_area')} ${onf('b_sum')}`});
  const P = c => ({x: f.X + f.k * (c[0] - f.x0), y: f.Y + f.k * (c[1] - f.y0)}), inF = c => c && c[0] > B.bbox_km[0] + 0.15 && c[0] < B.bbox_km[2] - 0.15 && c[1] > B.bbox_km[1] + 0.1 && c[1] < B.bbox_km[3] - 0.1;
  // the neighbours, in thin lines with their names
  const gn = opart(L, 'neigh', 'The neighbouring neighbourhoods: details', {title: 'Its neighbours', kick: 'Bernal Heights · part', lead: 'The city\'s analysis neighbourhoods around Bernal Heights: the Mission to the north, Noe Valley and Glen Park to the west, the Excelsior and Portola to the south, Bayview to the east.', facts: ['b.1']});
  const mn = mapG(gn, f.k, f.x0, f.y0, f.X, f.Y);
  Object.entries(B.neighbours).forEach(([nm, n]) => { if (nm !== 'Bernal Heights') E('path', {class: 'nbh', d: n.path}, mn); });
  gn.insertBefore(mn, gn.firstChild); gn._box = {x: f.X, y: f.Y, w: f.k * (B.bbox_km[2] - B.bbox_km[0]), h: f.k * (B.bbox_km[3] - B.bbox_km[1])};
  Object.entries(B.neighbours).forEach(([nm, n]) => { if (nm !== 'Bernal Heights' && inF(n.c)) { const q = P(n.c); T(gn, q.x, q.y, nm.replace('Bayview Hunters Point', 'Bayview').replace('Castro/Upper Market', 'Castro'), 'o-s nbl', 'middle'); } });
  // Bernal Heights itself
  const gb = opart(L, 'hood', 'Bernal Heights: details', {title: 'Bernal Heights', kick: 'Bernal Heights · part', lead: (OSC.bernal || {}).blurb, facts: ['b.1', 'b.2', 'b.3', 'b.9']});
  E('path', {class: 'st hl', d: B.bernal.path}, mapG(gb, f.k, f.x0, f.y0, f.X, f.Y));
  mapRing(gb, B.bernal.bbox_km, f);
  // the park and the summit (the one point drawn: a public landmark)
  const gp = opart(L, 'hill', 'The hill and its park: details', {title: 'The hill: red chert', kick: 'Bernal Heights · part', lead: 'The hill is folded layers of red chert: quartz, silicon dioxide, from the shells of plankton that settled on the sea floor 200 to 100 million years ago. Refined, the same silicon is the die.', facts: ['b.4', 'b.5', 'b.6', 'b.7']});
  E('path', {class: 'park', d: B.park.path}, mapG(gp, f.k, f.x0, f.y0, f.X, f.Y));
  const sm = P(B.summit.xy_km);
  E('path', {class: 'summit', d: `M${sm.x - 9},${sm.y + 7}L${sm.x},${sm.y - 9}L${sm.x + 9},${sm.y + 7}Z`}, gp);
  T(gp, sm.x + 14, sm.y - 8, `summit ${on('b_sum')}`, 'o-s ohalo', 'start', onf('b_sum'));
  T(gp, sm.x + 14, sm.y + 16, `park ${on('b_park')}`, 'o-s ohalo', 'start', onf('b_park'));
  S(E('circle', {cx: sm.x, cy: sm.y, r: 40, 'pointer-events': 'all'}, gp), {fill: 'transparent'});
  E('circle', {class: 'ring', cx: sm.x, cy: sm.y, r: 30}, gp);
  // the roads that bound it, and its main street
  const gr = E('g', {class: 'roads', 'pointer-events': 'none'}, L), mr = mapG(gr, f.k, f.x0, f.y0, f.X, f.Y);
  Object.entries(B.roads).forEach(([nm, d]) => { E('path', {class: 'road', d}, mr); const at = BROADS[nm], c = at && pathAt(d, at[0]); if (c && inF(c) && !PH) { const q = P(c); T(gr, q.x, q.y + at[1], nm, 'o-s ohalo road-l', 'middle'); } });
  // 29th Street, the whole of it: the jump into its side view
  const gs = opart(L, 'to29', '29th Street: zoom in', kidInfo('st29'), {id: 'st29'});
  const ms = mapG(gs, f.k, f.x0, f.y0, f.X, f.Y);
  E('path', {class: 'st29h', d: B.st29.path}, ms); E('path', {class: 'st29', d: B.st29.path}, ms);
  const sp = (B.st29.path.match(/-?[\d.]+,-?[\d.]+/g) || []).map(p => P(p.split(',').map(Number)));
  const sx0 = Math.min(...sp.map(q => q.x)), sx1 = Math.max(...sp.map(q => q.x)), sy = sp.reduce((a, q) => a + q.y, 0) / sp.length;
  E('rect', {class: 'ring', x: sx0 - 10, y: sy - 22, width: sx1 - sx0 + 20, height: 44, rx: 10}, gs);
  T(gs, (sx0 + sx1) / 2, sy - 18, '29th Street', 'o-l ohalo', 'middle');
  gs._box = {x: sx0 - 10, y: sy - 22, w: sx1 - sx0 + 20, h: 44};
  ap.zs.st29 = {r: lineSeat(ST29X[0], ST29X[1], ST29Y(), sx0, sx1, sy), g: gs, tr: 'jump'};
  sbar(L, PH ? 150 : 640, PH ? 600 : 650, 0.5 * f.k, '500 m');
  owrap(L, 140, PH ? 652 : 690, 'the street is drawn whole: where on it the studio is, is not shown', 'o-s', 'start', null, 40);
}});
/* the rect in the parent where a child drawn in VB goes so that its line from cx0 to cx1 at height cy lands on the
   parent's line from px0 to px1 at py (a map's street becoming the side view's street) */
function lineSeat(cx0, cx1, cy, px0, px1, py) { const k = (px1 - px0) / (cx1 - cx0); return {x: px0 - k * (cx0 - VB.x), y: py - k * (cy - VB.y), w: k * VB.w, h: k * VB.h}; }
/* ---- 29th Street: a side view, not a map. Its height along its length (USGS lidar, every 40 m), the vertical scale
   stretched and labelled so, the cross streets as ticks; no stretch of it marked, and Studio 45 in an inset beside the
   drawing, never at a point on the street ---- */
const ST29X = [140, 880], ST29Y = () => (PH ? 330 : 380);
onode('st29', {kid: 'studio45', build: (L, ap) => {
  const B = BERN.st29, pr = B.profile_m, len = pr[pr.length - 1][0], X0 = ST29X[0], W = ST29X[1] - ST29X[0];
  obd(L, false);
  otitle(L, '29th Street', 'side view, heights stretched', `${on('st_len')} long, it falls ${on('st_drop')}; light runs it in ${on('st_light')}`, `${onf('st_len')} ${onf('st_drop')} ${onf('st_light')}`);
  const Y0 = PH ? 400 : 600, kz = PH ? 1.9 : 2.8, kx = W / len, xm = d => X0 + d * kx, ym = h => Y0 - h * kz;
  const g = opart(L, 'street', '29th Street, in profile: details', {title: '29th Street, in profile', kick: '29th Street · part', lead: (OSC.st29 || {}).blurb, facts: ['st.1', 'st.2', 'st.3']});
  const line = pr.map(([d, h], i) => `${i ? 'L' : 'M'}${xm(d).toFixed(1)},${ym(h).toFixed(1)}`).join('');
  E('path', {class: 'ground', d: `${line}L${xm(len)},${Y0}L${X0},${Y0}Z`}, g);
  E('path', {class: 'st29', d: line}, g);
  E('rect', {class: 'ring', x: X0 - 8, y: ym(150) - 8, width: W + 16, height: Y0 - ym(150) + 16, rx: 10}, g);
  E('line', {class: 'sea', x1: X0, y1: Y0, x2: X0 + W, y2: Y0}, L);
  T(L, X0 + W + 10, Y0 + 6, 'sea level', 'o-s');
  T(g, xm(0) + 6, ym(pr[0][1]) - 12, on('st_top'), 'o-s ohalo', 'start', onf('st_top'));
  T(g, xm(len) - 4, ym(pr[pr.length - 1][1]) - 14, on('st_bot'), 'o-s ohalo', 'end', onf('st_bot'));
  // the hill's summit, for comparison: a level line
  E('line', {class: 'sumln', x1: X0, y1: ym(142), x2: X0 + W, y2: ym(142)}, L);
  T(L, X0 + W, ym(142) - 10, `Bernal Heights' summit, ${on('b_sum')}`, 'o-s', 'end', onf('b_sum'));
  // the cross streets, ticks along the street with their names
  const gc = E('g', {class: 'xst', 'pointer-events': 'none'}, L);
  B.cross.forEach((c, i) => {
    const x = xm(c.d_m), h = pr.reduce((a, q) => (Math.abs(q[0] - c.d_m) < Math.abs(a[0] - c.d_m) ? q : a))[1], y = ym(h);
    E('line', {class: 'xtick', x1: x, y1: y - 6, x2: x, y2: y + 6}, gc);
    const t = T(gc, x + 4, Y0 + 24, c.name, 'o-s', 'start'); t.setAttribute('transform', `rotate(${PH ? 62 : 40} ${x + 4} ${Y0 + 24})`);
  });
  T(L, X0, PH ? Y0 + 182 : Y0 + 100, `heights drawn ${(kz / kx).toFixed(1)} times their scale`, 'o-s');
  // Studio 45, beside the drawing (its place on the street is not shown): the jump's seat
  const ib = PH ? {x: 520, y: Y0 + 210, w: 340, h: 120} : {x: 940, y: 240, w: 230, h: 124};
  const gs = opart(L, 'to45', 'Studio 45, on 29th Street: zoom in', kidInfo('studio45'), {id: 'studio45'});
  S(E('rect', {class: 'shape inset', x: ib.x, y: ib.y, width: ib.w, height: ib.h, rx: 6}, gs), {});
  E('rect', {class: 'ring', x: ib.x - 5, y: ib.y - 5, width: ib.w + 10, height: ib.h + 10, rx: 9}, gs);
  S(E('rect', {x: ib.x + ib.w / 2 - 36, y: ib.y + 14, width: 72, height: 30, rx: 2, 'pointer-events': 'none'}, gs), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 1.5});
  T(gs, ib.x + ib.w / 2, ib.y + 74, 'Studio 45', 'o-l', 'middle'); T(gs, ib.x + ib.w / 2, ib.y + 100, 'on 29th Street', 'o-s', 'middle');
  T2(L, PH ? 140 : ib.x, PH ? ib.y + 30 : ib.y + ib.h + 30, ['its place on the street', 'is not shown'], 'o-s', 'start', null, 1.2);
  ap.zs.studio45 = {r: ib, g: gs, tr: 'jump'};
}});
/* ---- Studio 45: the building at its address in plan and in section, schematic, to scale (DataSF's footprint, 37 by
   9 m); the rack to scale, its place in the building not recorded ---- */
const SK45 = 19;   // units per metre
const S45P = {x: 150, y: 60, w: 37 * SK45, h: 9 * SK45};
const RK = {x: S45P.x + 22 * SK45, y: S45P.y + 5 * SK45, w: 1.5 * SK45, h: 0.6 * SK45};
onode('studio45', {kid: 'rack', build: (L, ap) => {
  obd(L, false);
  otitle(L, 'Studio 45', 'schematic, to scale', `a co-working space and workshop for hardware, ${on('s45_l')} by ${on('s45_w')}; light crosses it in ${on('s45_light')}`, `${onf('s45_l')} ${onf('s45_light')}`);
  const fl = S45P;
  const g = opart(L, 'bldg', 'The building: details', {title: 'Studio 45', kick: 'Studio 45 · part', lead: (OSC.studio45 || {}).blurb, facts: ['s45.2', 's45.3', 's45.4', 's45.5', 's45.6', 's45.7']});
  S(E('rect', {class: 'shape floor', x: fl.x, y: fl.y, width: fl.w, height: fl.h, rx: 3}, g), {});
  E('rect', {class: 'ring', x: fl.x - 6, y: fl.y - 6, width: fl.w + 12, height: fl.h + 12, rx: 7}, g);
  // the walls stay drawn while the camera dives to the rack, until the rack's photo covers the screen
  S(E('rect', {x: fl.x, y: fl.y, width: fl.w, height: fl.h, rx: 3, 'pointer-events': 'none'}, L), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 2, strokeDasharray: '10 8'});
  T(g, fl.x + 14, fl.y + 28, 'in plan: what is where inside is not recorded', 'o-s');
  T(g, fl.x + 14, fl.y + fl.h - 14, `${on('s45_l')} deep`, 'o-s', 'start', onf('s45_l'));
  // in section: two storeys, 6 to 8 m tall
  const sy = PH ? 470 : 470, sh = 7 * SK45, gsct = opart(L, 'section', 'The building in section: details', {title: 'Two storeys', kick: 'Studio 45 · part', lead: 'Two floors of co-working space over a street-level warehouse and courtyard, with a wood shop: the building is 6 to 8 m tall.', facts: ['s45.3', 's45.6']});
  S(E('rect', {class: 'shape floor', x: fl.x, y: sy - sh, width: fl.w, height: sh, rx: 2}, gsct), {});
  S(E('line', {x1: fl.x, y1: sy - sh / 2, x2: fl.x + fl.w, y2: sy - sh / 2, 'pointer-events': 'none'}, gsct), {stroke: 'var(--ink-2)', strokeWidth: 1.5, strokeDasharray: '6 6'});
  S(E('line', {x1: fl.x - 30, y1: sy, x2: fl.x + fl.w + 30, y2: sy, 'pointer-events': 'none'}, gsct), {stroke: 'var(--ink)', strokeWidth: 2.5});
  E('rect', {class: 'ring', x: fl.x - 6, y: sy - sh - 6, width: fl.w + 12, height: sh + 12, rx: 6}, gsct);
  T(gsct, fl.x + 14, sy - sh + 26, 'co-working upstairs', 'o-s'); T(gsct, fl.x + 14, sy - 14, 'street-level warehouse, shop and courtyard', 'o-s');
  T(gsct, PH ? fl.x + fl.w - 10 : fl.x + fl.w + 12, PH ? sy - sh - 12 : sy - sh / 2 + 6, `${on('s45_h')} tall`, 'o-s', PH ? 'end' : 'start', onf('s45_h'));
  // a person and the CNC router's bed, to scale
  const gp = opart(L, 'person', 'A person, for scale: details', {title: 'A person, for scale', kick: 'Studio 45 · scale', lead: 'A person 1.7 m tall, drawn to the building\'s scale: light crosses the building in 123 ns, 74 ticks of the chip\'s clock.', facts: ['s45.7']});
  const px = fl.x + 30 * SK45, ph = 1.7 * SK45;
  S(E('circle', {cx: px, cy: sy - ph + 3.5, r: 3.5}, gp), {fill: 'var(--ink-2)'}); S(E('rect', {x: px - 3, y: sy - ph + 7, width: 6, height: ph - 7, rx: 2}, gp), {fill: 'var(--ink-2)'});
  S(E('circle', {cx: px, cy: sy - ph / 2, r: 22, 'pointer-events': 'all'}, gp), {fill: 'transparent'}); E('circle', {class: 'ring', cx: px, cy: sy - ph / 2, r: 24}, gp);
  T(gp, PH ? px - 14 : px + 14, sy - ph - 8, 'a person, 1.7 m', 'o-s ohalo', PH ? 'end' : 'start');
  const gk = opart(L, 'cnc', 'The CNC router\'s bed: details', {title: 'A 4 × 8 ft CNC router', kick: 'Studio 45 · tools', lead: 'The shop\'s three-axis CNC router cuts a 4 by 8 foot sheet: 1.22 by 2.44 m, drawn here to the building\'s scale.', facts: ['s45.3', 's45.8']});
  const cx = fl.x + 6 * SK45, cy = fl.y + 3 * SK45;
  S(E('rect', {class: 'shape cncb', x: cx, y: cy, width: 2.44 * SK45, height: 1.22 * SK45, rx: 1}, gk), {});
  E('rect', {class: 'ring', x: cx - 5, y: cy - 5, width: 2.44 * SK45 + 10, height: 1.22 * SK45 + 10, rx: 4}, gk);
  S(E('rect', {x: cx - 12, y: cy - 12, width: 2.44 * SK45 + 24, height: 1.22 * SK45 + 24, 'pointer-events': 'all'}, gk), {fill: 'transparent'});
  T(gk, cx, cy + 1.22 * SK45 + 22, `${on('s45_cnc')} CNC bed`, 'o-s', 'start', onf('s45_cnc'));
  // the rack: to scale, its place in the building not recorded
  const gr = opart(L, 'torack', 'The rack: zoom in', kidInfo('rack'), {id: 'rack'});
  S(E('circle', {cx: RK.x + RK.w / 2, cy: RK.y + RK.h / 2, r: 40, 'pointer-events': 'all'}, gr), {fill: 'transparent'});
  S(E('rect', {class: 'shape rackp', x: RK.x, y: RK.y, width: RK.w, height: RK.h, rx: 2}, gr), {});
  E('rect', {class: 'ring', x: RK.x - 6, y: RK.y - 6, width: RK.w + 12, height: RK.h + 12, rx: 5}, gr);
  if (PH) T2(gr, RK.x - 10, RK.y + 44, ['the rack (to scale;', 'its place is not recorded)'], 'o-s', 'middle', null, 1.15);
  else T(gr, RK.x + RK.w / 2, RK.y + 40, 'the rack (to scale; its place is not recorded)', 'o-s', 'middle');
  // (the rack is small in the building: a powers-of-ten jump from a box an eighth of the view around it, so that no
  // layer is ever scaled past 30 times, on a phone either)
  ap.zs.rack = {r: markBox(RK.x + RK.w / 2, RK.y + RK.h / 2), g: gr, tr: 'jump'};
  sbar(L, 150, PH ? 560 : 560, 5 * SK45, '5 m');
}});
/* ---- the rack: the owner's photo, its machines' labels blurred ---- */
const RKS = 0.69;   // units per pixel of the 1000 x 988 copy (a phone: 0.66, lower, under the wrapped line)
const RACKPH0 = {x: 165, y: 4, w: 1000 * RKS, h: 988 * RKS}, RACKPHP = {x: 180, y: 48, w: 660, h: 988 * 0.66};
const RACKPHf = () => (PH ? RACKPHP : RACKPH0);
onode('rack', {kid: 'host', img: ['rack.webp'], build: (L, ap) => {
  const RACKPH = RACKPHf(), RKS = RACKPH.w / 1000;
  obd(L, false);
  const g = opart(L, 'photo', 'The rack photo: details', {title: 'The rack', kick: 'Rack · photo', lead: (OSC.rack || {}).blurb, facts: ofx('rack', 1, 2, 3, 4, 5)});
  S(E('rect', {x: RACKPH.x, y: RACKPH.y, width: RACKPH.w, height: RACKPH.h, rx: 4, 'pointer-events': 'none'}, g), {fill: 'var(--grid)'});
  oimg(g, 'rack.webp', RACKPH.x, RACKPH.y, RACKPH.w, RACKPH.h);
  E('rect', {class: 'shape hotr', x: RACKPH.x, y: RACKPH.y, width: RACKPH.w, height: RACKPH.h, rx: 4}, g);
  E('rect', {class: 'ring', x: RACKPH.x - 5, y: RACKPH.y - 5, width: RACKPH.w + 10, height: RACKPH.h + 10, rx: 8}, g);
  otitle(L, 'The rack', 'photo', `light crosses it in ${on('rack_ns')}: 3 ticks of the chip’s clock`, onf('rack_ns'));
  const cp = [180, 185, 490, 495], cr = rc(RACKPH.x + cp[0] * RKS, RACKPH.y + cp[1] * RKS, (cp[2] - cp[0]) * RKS, (cp[3] - cp[1]) * RKS);
  const gh = hot(L, 'tohost', cr, 'One of the rack’s machines: zoom in', kidInfo('host', 'One of the rack’s open-frame computers. Which three machines are the lab’s is not recorded, so this one only illustrates what a host is.'), {id: 'host'},
    {dash: '8 6', lab: 'one of the rack’s machines', ly: cr.y + cr.h + 26, lcls: 'o-l', halo: true});
  gh.classList.add('ophoto');
  ap.zs.host = {r: cr, g: gh, tr: 'jump'};
  owrap(L, RACKPH.x + RACKPH.w - 12, RACKPH.y + RACKPH.h - (PH ? 44 : 16), 'which three machines are the lab’s is not recorded', 'o-s ohalo', 'end', null, 30);
  if (!PH) T(L, RACKPH.x + RACKPH.w + 12, RACKPH.y + RACKPH.h, 'Photo: the page’s author, 2026; machine labels blurred', 'o-cr', 'start').setAttribute('transform', `rotate(-90 ${RACKPH.x + RACKPH.w + 12} ${RACKPH.y + RACKPH.h})`);
}});
/* ---- a host computer: an ATX board from above, to scale, the card in its slot ---- */
const HK = 1.4;   // units per mm
const CARDIN = {x: 600, y: 330, w: 167.6 * HK, h: 111.8 * HK};
onode('host', {kid: 'card', build: (L, ap) => {
  obd(L, false);
  otitle(L, 'A host computer', 'drawing to scale', 'an ATX board seen from above; the card stands in a PCIe slot');
  const B = {x: 150, y: 70, w: 305 * HK, h: 244 * HK};
  const gb = opart(L, 'board', 'The motherboard: details', {title: 'The motherboard', kick: 'Host · part', lead: 'An ATX board, 30.5 by 24.4 cm: the processor, its memory and the slots the cards plug into.', facts: ofx('host', 2, 4)});
  S(E('rect', {class: 'shape pcb', x: B.x, y: B.y, width: B.w, height: B.h, rx: 4}, gb), {});
  E('rect', {class: 'ring', x: B.x - 6, y: B.y - 6, width: B.w + 12, height: B.h + 12, rx: 8}, gb);
  T(gb, B.x + 12, B.y + B.h - 14, 'ATX board, 305 × 244 mm', 'o-s');
  const gc = opart(L, 'cpu', 'The processor and its cooler: details', {title: 'The host’s processor', kick: 'Host · part', lead: 'An Intel desktop processor under a tower cooler. The whole ET card, at most 88 W, draws less than the bigger host processor’s 125 W base power; in turbo that processor may draw up to 251 W.', facts: ofx('host', 1, 5, 6)});
  const cx = B.x + 150 * HK, cy = B.y + 75 * HK, cs = 120 * HK;
  S(E('rect', {class: 'shape cool', x: cx - cs / 2, y: cy - cs / 2, width: cs, height: cs, rx: 6}, gc), {});
  S(E('circle', {cx, cy, r: cs * 0.42, 'pointer-events': 'none'}, gc), {fill: 'none', stroke: 'var(--ink-2)', strokeWidth: 1.5});
  E('rect', {class: 'ring', x: cx - cs / 2 - 5, y: cy - cs / 2 - 5, width: cs + 10, height: cs + 10, rx: 9}, gc);
  T(gc, cx, cy + 6, 'CPU and cooler', 'o-s', 'middle');
  const gd = opart(L, 'dimms', 'The memory modules: details', {title: 'The host’s memory', kick: 'Host · part', lead: 'Memory modules beside the processor: 32 to 128 GB on the lab’s three hosts.', facts: ofx('host', 1, 6)});
  for (let i = 0; i < 4; i++) S(E('rect', {class: 'shape dimm', x: B.x + 240 * HK + i * 10 * HK, y: B.y + 18 * HK, width: 6 * HK, height: 133 * HK, rx: 1}, gd), {});
  E('rect', {class: 'ring', x: B.x + 240 * HK - 5, y: B.y + 18 * HK - 5, width: 36 * HK + 10, height: 133 * HK + 10, rx: 5}, gd);
  S(E('rect', {x: B.x + 240 * HK - 20, y: B.y + 18 * HK, width: 36 * HK + 40, height: 133 * HK, 'pointer-events': 'all'}, gd), {fill: 'transparent'});
  T(gd, B.x + 258 * HK, B.y + 12 * HK, 'memory', 'o-s', 'middle');
  for (let i = 1; i < 3; i++) S(E('rect', {x: B.x + 40 * HK, y: B.y + (180 + i * 18) * HK, width: 89 * HK, height: 6 * HK, rx: 1, 'pointer-events': 'none'}, L), {fill: 'var(--ink-2)', fillOpacity: 0.35});
  // the card, edge-on in the first slot (it stands up from the board), and face-on in the inset: the jump's seat
  const gk = opart(L, 'tocard', 'The ET card: zoom in', kidInfo('card'), {id: 'card'});
  S(E('rect', {class: 'shape cardedge', x: B.x + 30 * HK, y: B.y + 166 * HK, width: 167.6 * HK, height: 4 * HK, rx: 1}, gk), {});
  S(E('rect', {class: 'shape cardface', x: CARDIN.x, y: CARDIN.y, width: CARDIN.w, height: CARDIN.h, rx: 4}, gk), {});
  S(E('rect', {x: CARDIN.x + 70 * HK, y: CARDIN.y + 35 * HK, width: 45 * HK, height: 45 * HK, rx: 2, 'pointer-events': 'none'}, gk), {fill: 'var(--c1)', fillOpacity: 0.3, stroke: 'var(--c1)', strokeWidth: 1.5});
  E('path', {class: 'lead', d: `M${B.x + 197.6 * HK},${B.y + 170 * HK} L${CARDIN.x},${CARDIN.y + CARDIN.h}`}, gk);
  E('rect', {class: 'ring', x: CARDIN.x - 5, y: CARDIN.y - 5, width: CARDIN.w + 10, height: CARDIN.h + 10, rx: 8}, gk);
  T(gk, CARDIN.x, CARDIN.y - 12, 'the ET card, face-on', 'o-l');
  T(gk, B.x + 30 * HK, B.y + 166 * HK - 12, 'the card, edge-on in its slot', 'o-s');
  ap.zs.card = {r: seatMap(VB, CARDPH, CARDIN), g: gk, tr: 'jump'};
  const gs = opart(L, 'psu', 'The power supply: details', {title: 'The power supply', kick: 'Host · part', lead: 'An ATX power supply, 150 by 86 mm across and 140 deep: it feeds the board, and the card through the slot and its own cables.', facts: ofx('host', 8, 7)});
  S(E('rect', {class: 'shape psu', x: 600, y: 70, width: 150 * HK, height: 140 * HK, rx: 4}, gs), {});
  E('rect', {class: 'ring', x: 595, y: 65, width: 150 * HK + 10, height: 140 * HK + 10, rx: 8}, gs);
  T(gs, 600 + 75 * HK, 70 + 70 * HK, 'power supply', 'o-s', 'middle');
  sbar(L, 150, PH ? 596 : 640, 100 * HK, '10 cm');
  owrap(L, 150, PH ? 630 : 676, 'aifoundry2’s board is an ATX board of exactly this size; the slot each card uses is not recorded', 'o-s', 'start', 'out.host.2');
}});
/* ---- the card: the vendor's photo with its parts ---- */
const CPX = 740 / 720;   // units per pixel of the 720 x 479 photo
const CARDPH = {x: 140, y: 40, w: 720 * CPX, h: 479 * CPX};
const cpr = b => rc(CARDPH.x + b[0] * CPX, CARDPH.y + b[1] * CPX, (b[2] - b[0]) * CPX, (b[3] - b[1]) * CPX);
onode('card', {kid: 'package', img: ['card.webp'], build: (L, ap) => {
  obd(L, false);
  otitle(L, 'The PCIe card', 'photo', `${on('card_w')}, at most ${on('card_88')} from the host`, `${onf('card_w')} ${onf('card_88')}`);
  const g = opart(L, 'board', 'The card: details', {title: 'The PCIe card', kick: 'Card · photo', lead: (OSC.card || {}).blurb, facts: ofx('card', 1, 2, 6, 9, 10, 12)});
  oimg(g, 'card.webp', CARDPH.x, CARDPH.y, CARDPH.w, CARDPH.h);
  E('rect', {class: 'shape hotr', x: CARDPH.x, y: CARDPH.y, width: CARDPH.w, height: CARDPH.h, rx: 4}, g);
  E('rect', {class: 'ring', x: CARDPH.x - 5, y: CARDPH.y - 5, width: CARDPH.w + 10, height: CARDPH.h + 10, rx: 8}, g);
  const H = ((OSC.card || {}).img || {}).hotspots_px || {};
  const lid = cpr(H['lid (the package)'] || [275, 161, 467, 356]);
  const gl = hot(L, 'topkg', lid, 'The chip’s package under its lid: zoom in', kidInfo('package'), {id: 'package'}, {lab: 'the ET-SoC-1, under its lid', lcls: 'o-l', halo: true});
  ap.zs.package = {r: seatMap(VB, PKGLID, lid), g: gl};
  const dr = ['LPDDR4X U11', 'LPDDR4X U20', 'LPDDR4X U12', 'LPDDR4X U21'];
  dr.forEach((k, i) => {
    if (!H[k]) return;
    const r = cpr(H[k]);
    hot(L, 'lpddr', r, `LPDDR4X memory package ${k.split(' ')[1]}: details`, {title: `LPDDR4X memory (${k.split(' ')[1]})`, kick: 'Card · part', lead: 'One of the four memory packages that hold the card’s 32 GB; each serves two of the chip’s eight memory shires.', facts: ofx('card', 3, 4, 5)}, null, {});
  });
  const pw = H['TPSM831D31 and its four inductors (cores, network)'];
  if (pw) hot(L, 'vrm', cpr(pw), 'The core regulator and its four inductors: details', {title: 'The core power regulator', kick: 'Card · part', lead: `The cores run at about ${on('card_v')}, 23 times lower than the 12 V input, so the current is about 23 times higher. One regulator module makes it: three of its four phases (three of the four large inductors) feed the cores, and the fourth feeds the on-chip network.`, facts: ofx('card', 7, 6)}, null, {});
  const sr = H['LTM4680 (SRAM rail)'];
  if (sr) hot(L, 'ltm', cpr(sr), 'The SRAM rail regulator: details', {title: 'The SRAM rail’s regulator', kick: 'Card · part', lead: 'A separate regulator module feeds the SRAM, which runs at a higher voltage than the cores.', facts: ofx('card', 8)}, null, {});
  const dp = H['DIP switches (boot options)'];
  if (dp) hot(L, 'dip', cpr(dp), 'The DIP switches: details', {title: 'DIP switches', kick: 'Card · part', lead: 'Small switches that set the chip’s boot options.', facts: ofx('card', 10)}, null, {});
  const ed = H['PCIe card edge'];
  if (ed) hot(L, 'edge', cpr(ed), 'The PCIe card edge: details', {title: 'The PCIe card edge', kick: 'Card · part', lead: 'The gold fingers that plug into the host’s slot: 8 lanes of PCIe Gen 4 in an x16 edge, and 12 V of power.', facts: ofx('card', 1, 2, 6)}, null, {});
  T2(L, 140, CARDPH.y + CARDPH.h + 30, PH ? ['Its parts: the lid, the four memory packages,', 'the core regulator and its inductors, the SRAM', 'regulator, the boot switches, the card edge.']
    : ['Click a part: the lid, the four memory packages, the core regulator and its four inductors,', 'the SRAM regulator, the boot switches, the card edge.'], 'o-s', 'start', null, 1.15);
  sbar(L, 140, 650, 50 * 4.296 * CPX, '5 cm');
  ocredit(L, 'Photo: Esperanto Technologies, PCIe Dev Card (V3), github.com/aifoundry-org/et-man (Apache-2.0): the vendor’s card, not a lab card', 690);
}});
/* ---- the package: Fig. 9-1 of the datasheet, drawn ---- */
const PKK = 7.6;   // units per mm
const PKGB = {x: 150, y: 40, w: 45 * PKK, h: 45 * PKK};
const PKGLID = {x: PKGB.x + 0.1 * PKK, y: PKGB.y + 0.1 * PKK, w: 44.8 * PKK, h: 44.8 * PKK};
const PKGDIE = {x: PKGB.x + (45 - 25.6) / 2 * PKK, y: PKGB.y + (45 - 22.2) / 2 * PKK, w: 25.6 * PKK, h: 22.2 * PKK};
onode('package', {kid: 'die', tr: 'nest', build: (L, ap) => {
  obd(L, false);
  otitle(L, 'The package', 'drawing to scale', `a ${on('pkg_body')} ball-grid array, ${on('pkg_balls')} solder balls`, `${onf('pkg_body')}`);
  const gb = opart(L, 'body', 'The package and its lid: details', {title: 'The package', kick: 'Package · part', lead: (OSC.package || {}).blurb, facts: ofx('package', 1, 6, 7)});
  S(E('rect', {class: 'shape pkgb', x: PKGB.x, y: PKGB.y, width: PKGB.w, height: PKGB.h, rx: 6}, gb), {});
  S(E('rect', {x: PKGLID.x, y: PKGLID.y, width: PKGLID.w, height: PKGLID.h, rx: 10, 'pointer-events': 'none'}, gb), {fill: 'var(--ink-2)', fillOpacity: 0.08, stroke: 'var(--ink-2)', strokeWidth: 1.5});
  E('rect', {class: 'ring', x: PKGB.x - 6, y: PKGB.y - 6, width: PKGB.w + 12, height: PKGB.h + 12, rx: 10}, gb);
  T(gb, PKGB.x + 12, PKGB.y + 28, `top view: the lid, ${on('pkg_lid')}`, 'o-s', 'start', onf('pkg_lid'));
  const gd = opart(L, 'todie', 'The die under the lid: zoom in', kidInfo('die'), {id: 'die'});
  S(E('rect', {class: 'shape diedash', x: PKGDIE.x, y: PKGDIE.y, width: PKGDIE.w, height: PKGDIE.h, rx: 3}, gd), {});
  E('rect', {class: 'ring', x: PKGDIE.x - 6, y: PKGDIE.y - 6, width: PKGDIE.w + 12, height: PKGDIE.h + 12, rx: 6}, gd);
  T(gd, PKGDIE.x + PKGDIE.w / 2, PKGDIE.y + PKGDIE.h / 2 - 16, 'the die', 'o-l', 'middle');
  T(gd, PKGDIE.x + PKGDIE.w / 2, PKGDIE.y + PKGDIE.h / 2 + 10, on('pkg_die'), 'o-s', 'middle', onf('pkg_die'));
  T(gd, PKGDIE.x + PKGDIE.w / 2, PKGDIE.y + PKGDIE.h / 2 + 34, 'position assumed', 'o-s', 'middle');
  ap.zs.die = {r: PKGDIE, g: gd, tr: 'jump'};
  // the side view, heights drawn five times their scale
  const sx = PKGB.x, sy = PKGB.y + PKGB.h + (PH ? 92 : 60), V5 = 5 * PKK;
  const gs = opart(L, 'side', 'The package in section: details', {title: 'The package, cut in half', kick: 'Package · part', lead: 'Under the lid the die sits face down on more than 30,000 tiny bumps; the substrate below fans them out to 2,494 solder balls, about 12 bumps per ball.', facts: ofx('package', 1, 3)});
  const lay = [['lid', 1.2, 'var(--ink-2)'], ['die', 0.8, 'var(--c1)'], ['bumps', 0.15, 'var(--c2)'], ['substrate', 1.6, 'var(--c4)'], ['balls', 0.5, 'var(--c5)']];
  let yy = sy, ly = -Infinity;
  lay.forEach(([nm, hmm, col]) => {
    const w = nm === 'die' ? PKGDIE.w : nm === 'bumps' ? PKGDIE.w : PKGB.w, x = nm === 'die' || nm === 'bumps' ? PKGDIE.x : sx;
    if (nm === 'balls') { for (let i = 0; i < 26; i++) S(E('circle', {cx: sx + (i + 0.5) * PKGB.w / 26, cy: yy + hmm * V5 / 2, r: hmm * V5 / 2, 'pointer-events': 'none'}, gs), {fill: col, fillOpacity: 0.6}); }
    else if (nm === 'bumps') { for (let i = 0; i < 40; i++) S(E('circle', {cx: x + (i + 0.5) * w / 40, cy: yy + 1.5, r: 1.6, 'pointer-events': 'none'}, gs), {fill: col}); }
    else S(E('rect', {x, y: yy, width: w, height: hmm * V5, rx: 1, 'pointer-events': 'none'}, gs), {fill: col, fillOpacity: 0.25, stroke: col, strokeWidth: 1.2});
    ly = Math.max(yy + hmm * V5 / 2 + 6, ly + (PH ? 29 : 23)); T(gs, sx + PKGB.w + 12, ly, nm, 'o-s');
    yy += hmm * V5;
  });
  S(E('rect', {x: sx, y: sy, width: PKGB.w, height: yy - sy}, gs), {fill: 'transparent'});
  E('rect', {class: 'ring', x: sx - 6, y: sy - 6, width: PKGB.w + 12, height: yy - sy + 12, rx: 6}, gs);
  T(gs, sx, sy - 12, `in section, heights ×5 (${on('pkg_h')} in all; layer heights generic)`, 'o-s', 'start', onf('pkg_h'));
  // the ball grid from below
  const bx = 540, by = PKGB.y, bw = 45 * PKK * 0.9;
  const gg = opart(L, 'balls', 'The ball grid: details', {title: 'The ball grid', kick: 'Package · part', lead: `${on('pkg_balls')} solder balls on a ${on('pkg_pitch')} grid join the package to the card.`, facts: ofx('package', 1, 2, 3)});
  const nb = 53, p = bw / nb;
  S(E('rect', {class: 'shape pkgb', x: bx, y: by, width: bw, height: bw, rx: 6}, gg), {});
  for (let i = 0; i < nb; i += 2) for (let j = 0; j < nb; j += 2) E('circle', {class: 'ball', cx: bx + (i + 0.5) * p, cy: by + (j + 0.5) * p, r: p * 0.42}, gg);
  E('rect', {class: 'ring', x: bx - 6, y: by - 6, width: bw + 12, height: bw + 12, rx: 10}, gg);
  if (PH) T2(gg, bx, by + bw + 30, ['from below: one in four', `of the ${on('pkg_pitch')} grid drawn`], 'o-s', 'start', onf('pkg_pitch'), 1.15);
  else { T(gg, bx, by + bw + 26, `from below: one in four of the ${on('pkg_pitch')} grid drawn`, 'o-s', 'start', onf('pkg_pitch')); T(gg, bx, by + bw + 50, '(the datasheet’s Fig. 9-1 has the exact map)', 'o-s'); }
  sbar(L, 150, 690, 10 * PKK, '10 mm');
}});
/* the host beside the die stands for the level further out */
KIDS.host = () => ({up: 'host'});
/* the scales' panels: a part of a level (its _info), and "You are here" at a level (D.scales) */
function showNodePart(g) {
  const i = g._info || {}, P = layerPath(g) || Z.path, el = P[P.length - 1];
  const facts = (i.facts || []).filter(f => F[f]);
  const det = (facts.length ? `<p class="pn-h pn-fh">The facts (${facts.length}): point at one for its source</p><ul class="facts">${facts.map(factLi).join('')}</ul>` : '') + lazyNote(i.facts);
  panel(`<p class="pn-kick">${esc(i.kick || shortOf(el) + ' · part')}</p><p class="pn-title">${esc(i.title || '')}</p>`
    + (i.lead ? `<p class="pn-lead">${i.lead}</p>` : '') + zoomRowPart(g, i.title) + (det ? detBlock(det) : ''));
}
function showScene(P) {
  const el = P[P.length - 1], s = OSC[el.id] || {}, N0 = NODES[el.id];
  const blurb = N0 && N0.blurb ? N0.blurb(prm(el)) : s.blurb;
  const facts = (s.facts || []).filter(f => F[f]);
  const im = s.img ? `<p class="pn-cred">Image: ${esc(s.img.credit)} · ${s.img.licence_url ? `<a href="${esc(s.img.licence_url)}" target="_blank" rel="noopener">${esc(s.img.licence)} ↗</a>` : esc(s.img.licence)}</p>` : '';
  const det = (s.note ? `<p class="pn-what"><b>Its size:</b> ${esc(s.note)}</p>` : '') + (s.notes || []).map(t => `<p class="pn-what">${esc(t)}</p>`).join('')
    + (s.erbium ? '<p class="pn-what"><span class="kd erbium">Erbium RTL</span> Some facts here come from core-et’s RTL on its Erbium branch: the same Minion core lineage as the ET-SoC-1, in a later configuration; that the silicon matches it is not confirmed.</p>' : '')
    + (facts.length ? `<p class="pn-h pn-fh">The facts (${facts.length}): point at one for its source</p><ul class="facts">${facts.map(factLi).join('')}</ul>` : '') + lazyNote(s.facts);
  // a scene drawn in two states (1 Oct): the panel's switch beside the drawing's (G)
  const L = LYR.get(pkeys(P)), st = L && L._states;
  const sw = st ? `<div class="pn-act"><button type="button" class="st-btn" data-act="state" aria-pressed="${STON}">${esc(st.btn[STON ? 1 : 0])}</button></div>` : '';
  // came round the loop (Up from the top) or from the ring: where the reader now is, and the ring (only after coming
  // round: the easter egg is never named in advance)
  const came = !(WRAPIN && WRAPIN === pkeys(P)) ? '' : WRAPVIA === 'loop'
    ? `<p class="pn-lead pn-came">↻ You came round the loop: past the observable universe, the largest scale, back to the smallest, ${esc(toOf(el))}, under one atom of this chip. Up climbs from here through ${esc(P.slice(Math.max(1, P.length - 5), -1).reverse().map(toOf).join(', ').replace(/, ([^,]*)$/, ' and $1'))}, on up to the chip and round again.</p>${NODES[WRAP] ? `<div class="pn-zoom">${zrow('', [zbtn([{id: WRAP}], '↻ The ring of sizes: every size at once', false, '')])}</div>` : ''}`
    : `<p class="pn-lead pn-came">↻ You came round the ring of sizes: past the observable universe, back to the smallest things, and ${el.id === 'p.atom' ? 'in as one atom of this chip: a silicon atom in the channel of one of its transistors' : `in at ${esc(toOf(el))}, under an atom of this chip`}. Up climbs from here to the chip and on round the loop.</p><div class="pn-zoom">${zrow('', [zbtn([{id: WRAP}], '↻ Back to the ring of sizes', false, '')])}</div>`;
  panel(`<p class="pn-kick">${hereKick(P)}</p><p class="pn-title">${esc(nameOf(el))}</p>` + came + (blurb ? `<p class="pn-lead">${esc(blurb)}</p>` : '')
    + sw + zoomRowHere(P) + im + (det ? detBlock(det) : ''));
  if (st) $('pn-body').querySelectorAll('button[data-act="state"]').forEach(b => { b._lab = st.btn; });
}
/* images of the levels near the camera are fetched ahead (two levels either way), and decoded before it enters one */
function prefetch() {
  const P = Z.path, d = P.length - 1, ids = new Set();
  for (let i = Math.max(0, d - 2); i <= d; i++) ids.add(P[i].id);
  let Q = P.slice(); for (let i = 0; i < 2; i++) { const k = defKid(Q); if (!k) break; ids.add(k.id); Q = Q.concat([k]); }
  ids.forEach(id => { const N0 = NODES[id]; if (N0 && N0.imgs) N0.imgs({}).forEach(u => { if (!IMGDONE.has(u)) { const im = new Image(); im.src = u; } }); });
}
