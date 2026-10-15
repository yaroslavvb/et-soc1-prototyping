// phone.mjs [W H] [--shots]: the outside levels the audit names (topic 3, section 2): st29's 'sea level' and the package's
// section heading, where each text lies against the drawing's visible box (#svgwrap) on a phone, and what it shares a row with.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { writeFileSync, mkdirSync } from 'node:fs';
const args = process.argv.slice(2);
const W = +(args[0] || 390), H = +(args[1] || 844);
const SHOTS = args.includes('--shots');
const FONT = (args.find(a => a.startsWith('--font=')) || '').slice(7);
const OUT = '/home/yaroslavvb/claude/work/chip-check-1014/codex/topic3-work/out';
mkdirSync(OUT, {recursive: true});
const PRE = 'beyond/universe/laniakea/localgroup/milkyway/stars/solar/moon/earth/us/california/bayarea/sf/bernal/';
const T = {st29: PRE + 'st29', package: PRE + 'st29/studio45/rack/host/card/package', bernal: PRE.slice(0, -1)};
const b = await open({w: W, h: H, dpr: 2, reduced: true, touch: W < 600});
await b.load('http://127.0.0.1:8918/chip.html', '', 5000);
await b.idle(20000); await sleep(2500);
if (FONT) await b.ev(`(() => { const s = document.createElement('style'); s.textContent = '#chip text{font-family:${FONT}!important}'; document.head.appendChild(s); return 1; })()`);
const go = async (hash, wait = 500) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(600); };
const res = {};
for (const [id, p] of Object.entries(T)) {
  await go('#at=' + p.replace(/:/g, '%3A'));
  const st = await b.state();
  const r = await b.ev(`(() => {
    const L = [...document.querySelectorAll('#chip g.lay')].filter(l => l.style.display !== 'none' && l.dataset.node === ${JSON.stringify(id)}).pop();
    if (!L) return {err: 'no layer'};
    const wr = document.getElementById('svgwrap').getBoundingClientRect();
    const sv = document.getElementById('chip').getBoundingClientRect();
    const vb = document.getElementById('chip').getAttribute('viewBox');
    const m = L.getScreenCTM();
    const texts = [...L.querySelectorAll('text')].filter(t => t.getClientRects().length).map(t => { const c = t.getBoundingClientRect(), bb = t.getBBox();
      return {t: t.textContent.slice(0, 90), cls: t.getAttribute('class'), anchor: t.getAttribute('text-anchor'), x: +t.getAttribute('x'), y: +t.getAttribute('y'),
        ux: +bb.x.toFixed(1), ur: +(bb.x + bb.width).toFixed(1), uy: +bb.y.toFixed(1), ub: +(bb.y + bb.height).toFixed(1),
        l: +c.left.toFixed(1), r: +c.right.toFixed(1), top: +c.top.toFixed(1), bot: +c.bottom.toFixed(1), fs: getComputedStyle(t).fontSize,
        offR: +(c.right - Math.min(wr.right, innerWidth)).toFixed(1), offL: +(Math.max(wr.left, 0) - c.left).toFixed(1)}; });
    const rects = [...L.querySelectorAll('g.otl rect, g.sbar path')].map(e => { const c = e.getBoundingClientRect(); return {tag: e.tagName, cls: e.parentNode.getAttribute('class'), l: +c.left.toFixed(1), r: +c.right.toFixed(1), top: +c.top.toFixed(1), bot: +c.bottom.toFixed(1)}; });
    return {wrap: {l: wr.left, r: wr.right, t: wr.top, b: wr.bottom}, svg: {l: sv.left, r: sv.right, t: sv.top, b: sv.bottom}, vb, inner: [innerWidth, innerHeight], k: m && m.a, ph: document.getElementById('stage').classList.contains('ph'), texts, rects};
  })()`);
  if (SHOTS) await b.shot(`${OUT}/phone-${W}x${H}${FONT ? '-' + FONT.replace(/[^A-Za-z]/g, '') : ''}-${id}.png`);
  res[id] = {node: st.node, ...r};
  const bad = (r.texts || []).filter(t => t.offR > 0 || t.offL > 0);
  console.log(id, 'node', st.node, 'ph', r.ph, 'wrap', JSON.stringify(r.wrap), 'vb', r.vb, 'k', r.k);
  console.log('  off-screen or clipped:', JSON.stringify(bad.map(t => [t.t, t.l, t.r, t.offR, t.offL])));
}
writeFileSync(`${OUT}/phone-${W}x${H}${FONT ? '-' + FONT.replace(/[^A-Za-z]/g, '') : ''}.json`, JSON.stringify(res, null, 1));
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
