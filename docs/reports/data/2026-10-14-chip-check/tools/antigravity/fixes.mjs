// fixes.mjs: the proposed source changes of topic 3, as replacements in the built pages (the same text as in the sources:
// ladder-core.js, ladder-outer.js and chip-diagram.script.js are included in the pages verbatim, comments aside).
export const FITHEADS_FN = `/* a frame's title keeps clear of the tag pills on its line (discussion topic 3, 14 Oct 2026: in a wide system font,
   Noto Sans on Linux, "A counter: a register and an incrementer" ran into its "this chip’s own circuit: not published"):
   a title line that would come within 16 units of a pill on its band is set smaller, down to 22 units, and only then
   narrower (textLength) */
function fitHeads(L) {
  const run = () => L.querySelectorAll('g.frm, g.ifr').forEach(fr => {
    const pills = [...fr.querySelectorAll(':scope > g.tg > rect')].map(r => ({x: +r.getAttribute('x'), y: +r.getAttribute('y'), h: +r.getAttribute('height')}));
    if (!pills.length) return;
    fr.querySelectorAll(':scope > text.t-big, :scope > text.i-t').forEach(t => {
      let b; try { b = t.getBBox(); } catch (_) { return; }
      const band = pills.filter(p => p.x > b.x && p.y < b.y + b.height && p.y + p.h > b.y);
      if (!b.width || !band.length) return;
      const room = Math.min(...band.map(p => p.x)) - 16 - b.x;
      if (b.width <= room) return;
      const fs = parseFloat(getComputedStyle(t).fontSize) || 30;
      t.style.fontSize = Math.max(22, Math.floor(fs * room / b.width * 10) / 10) + 'px';
      if (t.getComputedTextLength() > room) { t.setAttribute('textLength', room.toFixed(1)); t.setAttribute('lengthAdjust', 'spacingAndGlyphs'); }
    });
  });
  if (CKT && CKT.kit && CKT.kit.measured) CKT.kit.measured(L, run); else run();
}
`;
export const FITHEADS = [
  ['N0.build(L, ap, prm(el), P, d);', 'N0.build(L, ap, prm(el), P, d);\n  fitHeads(L);'],
  ['function buildInto(L, P, d) {', FITHEADS_FN + 'function buildInto(L, P, d) {'],
];
// panel(): a panel that is one of the four scales' own text (its title that scale's name) links that scale's 3D view;
// any other panel, as now, the view of the scale shown
export const LINK3D = [
  ['  const current3d = Z.path.length && view3d[Z.path[Z.path.length - 1].id];',
   "  const pt = /<p class=\"pn-title\">([\\s\\S]*?)<\\/p>/.exec(html), named = pt && Object.keys(view3d).find(id => esc(nameOf({id})) === pt[1]);\n" +
   '  const current3d = named ? view3d[named] : Z.path.length && view3d[Z.path[Z.path.length - 1].id];'],
];
// st29: on a phone 'sea level' at the line's east end, above it (it started at x = 890, the phone view's right edge)
export const SEALEVEL = [
  ["  T(L, X0 + W + 10, Y0 + 6, 'sea level', 'o-s');",
   "  if (PH) T(L, X0 + W, Y0 - 10, 'sea level', 'o-s ohalo', 'end'); else T(L, X0 + W + 10, Y0 + 6, 'sea level', 'o-s');"],
];
