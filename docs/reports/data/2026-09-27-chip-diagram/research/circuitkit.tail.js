
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
