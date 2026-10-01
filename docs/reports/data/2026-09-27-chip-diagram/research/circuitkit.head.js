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
  const badges = list => list.map(([k, t]) => { const w = k === 'unknown' ? 'unknown · asked' : k === 'documented' ? 'spec' : k; return `<span class="kd ${k === 'documented' ? 'spec' : k}">${esc(w)}</span>${t && t !== w ? ` <span class="cav">${esc(t)}</span>` : ''}`; }).join(' ');

