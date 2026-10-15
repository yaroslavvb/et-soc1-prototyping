// measure.mjs W H OUT.json [ids,comma,separated] [base]
// For every scale of the chip diagram (the page's own graph: one path per scale), at rest at W x H (a phone below 600 px),
// reduced motion: every visible text of the rest layer with its box on screen (advance box, and ink from canvas metrics),
// the frame's box (.frm or .ifr), the visible part of the SVG, the texts that cross the frame or the visible area, and the
// pairs of texts whose ink boxes intersect. Read only.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { writeFileSync } from 'node:fs';

const [W = '1440', H = '900', OUT = '/tmp/x.json', ONLY = '', BASE = 'http://127.0.0.1:8918/chip.html'] = process.argv.slice(2);
const touch = +W < 600;
const b = await open({w: +W, h: +H, dpr: 1, reduced: true, touch});
await b.load(BASE, '', 6000);
await b.idle(20000);
if (process.env.FONT) await b.ev(`(() => { const st = document.createElement('style'); st.textContent = '#chip text:not(.t-net):not(.t-mono){font-family:' + ${JSON.stringify(process.env.FONT || '')} + ' !important}'; document.head.appendChild(st); return 1; })()`);
const graph = await b.ev('window.__chipTest.graph()');
const want = ONLY ? ONLY.split(',') : null;
const list = graph.filter(g => !g.err && (!want || want.includes(g.id)));
console.log('scales', graph.length, 'measuring', list.length);

const MEASURE = `(() => {
  const st = window.__chipState();
  const svg = document.getElementById('chip');
  const L = [...svg.querySelectorAll(':scope > g.lay')].find(l => l._key === st.path);
  if (!L) return {err: 'no layer', path: st.path};
  const wr = document.getElementById('svgwrap').getBoundingClientRect(), sr = svg.getBoundingClientRect();
  const view = {x0: Math.max(wr.left, sr.left, 0), x1: Math.min(wr.right, sr.right, innerWidth), y0: Math.max(wr.top, sr.top), y1: Math.min(wr.bottom, sr.bottom)};
  const lc = L.getScreenCTM(), k = lc ? Math.hypot(lc.a, lc.b) : 1;
  const frR = L.querySelector(':scope > g.frm > rect, :scope > g.ifr > rect');
  const fr = frR ? frR.getBoundingClientRect() : null;
  const cv = document.createElement('canvas').getContext('2d');
  const effOp = el => { let o = 1; for (let e = el; e && e !== svg; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
  const T = [];
  L.querySelectorAll('text').forEach(t => {
    if (t.closest('.fx')) return;
    const s = t.textContent; if (!s.trim()) return;
    const op = effOp(t); if (op < 0.05) return;
    const r = t.getBoundingClientRect(); if (!r.width) return;
    const cs = getComputedStyle(t), m0 = t.getScreenCTM(), kt = m0 ? Math.hypot(m0.a, m0.b) : k, rot = m0 && Math.abs(m0.b) > 1e-6;
    cv.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
    const mm = cv.measureText(s);
    let iy0 = r.top, iy1 = r.bottom;
    if (!rot && m0) {
      const yb = +(t.getAttribute('y') || 0), xb = +(t.getAttribute('x') || 0);
      const by = m0.b * xb + m0.d * yb + m0.f;
      iy0 = by - mm.actualBoundingBoxAscent * kt; iy1 = by + mm.actualBoundingBoxDescent * kt;
    }
    const cls = t.getAttribute('class') || '';
    const sw = parseFloat(cs.strokeWidth) || 0, hasStroke = cs.stroke && cs.stroke !== 'none' && sw > 0;
    const g = t.closest('g.comp');
    T.push({s, cls, fs: parseFloat(cs.fontSize), kt: +kt.toFixed(4), x0: r.left, x1: r.right, y0: r.top, y1: r.bottom, iy0, iy1,
      halo: hasStroke ? sw / 2 * kt : 0, comp: g ? (g.getAttribute('data-comp') || g._key || '') : '', anchor: t.getAttribute('text-anchor') || 'start',
      ux: +(t.getAttribute('x') || 0), uy: +(t.getAttribute('y') || 0), fit: t.hasAttribute('data-fit'), rot, idx: T.length});
  });
  const P = [];
  for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
    const a = T[i], c = T[j];
    const ox = Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0), oy = Math.min(a.iy1, c.iy1) - Math.max(a.iy0, c.iy0);
    if (ox > 1 && oy > 1) P.push({i, j, a: a.s, b: c.s, ox: +ox.toFixed(1), oy: +oy.toFixed(1), fsA: a.fs, fsB: c.fs});
  }
  const out = [];
  T.forEach(t => {
    const o = {};
    if (fr) { o.fr = +(t.x1 - fr.right).toFixed(1); o.fl = +(fr.left - t.x0).toFixed(1); o.fb = +(t.iy1 - fr.bottom).toFixed(1); }
    o.vr = +(t.x1 - view.x1).toFixed(1); o.vl = +(view.x0 - t.x0).toFixed(1); o.vb = +(t.iy1 - view.y1).toFixed(1); o.vt = +(view.y0 - t.iy0).toFixed(1);
    if ((o.fr > 0.5) || (o.fl > 0.5) || (o.fb > 0.5) || o.vr > 0.5 || o.vl > 0.5 || o.vb > 0.5 || o.vt > 0.5) out.push(Object.assign({s: t.s, cls: t.cls, fs: t.fs, ux: t.ux, uy: t.uy, kt: t.kt, x0: +t.x0.toFixed(1), x1: +t.x1.toFixed(1)}, o));
  });
  return {path: st.path, node: st.node, zooming: st.zooming, lcls: L.getAttribute('class'), k: +k.toFixed(4), view, fr: fr ? {l: fr.left, r: fr.right, t: fr.top, b: fr.bottom} : null,
    n: T.length, over: out, pairs: P, texts: T};
})()`;

const res = [];
for (const g of list) {
  const hash = '#at=' + g.path.replace(/:/g, '%3A');
  await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`);
  await sleep(350); await b.idle(15000); await sleep(250);
  let st = await b.state();
  if (st.path !== g.path) { await sleep(800); await b.idle(15000); st = await b.state(); }
  let m;
  try { m = await b.ev(MEASURE); } catch (e) { m = {err: String(e)}; }
  m.id = g.id; m.want = g.path; m.egg = g.egg; m.atOk = st.path === g.path;
  res.push(m);
  console.log(g.id, m.atOk ? '' : 'NOT AT ' + st.path, 'texts', m.n, 'over', (m.over || []).length, 'pairs', (m.pairs || []).length);
}
writeFileSync(OUT, JSON.stringify({W: +W, H: +H, graphN: graph.length, res}, null, 0));
console.log('errors', JSON.stringify(b.errs.slice(0, 10)));
await b.close();
