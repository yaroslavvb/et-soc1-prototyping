// boxfit.mjs W H OUT.json [ids] : for every part (g.comp with its own rect.shape) of every scale at rest, its own labels
// (direct text children, as fitTexts sees them) that run past the box (fitTexts' 5-unit pad) at the type in force; the
// font size each was set to (data-fit: shrunk by fitTexts). Read only. env FONT: a face for the SVG's text.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { writeFileSync } from 'node:fs';
const [W = '1440', H = '900', OUT = '/tmp/b.json', ONLY = '', BASE = 'http://127.0.0.1:8918/chip.html'] = process.argv.slice(2);
const b = await open({w: +W, h: +H, dpr: 1, reduced: true, touch: +W < 600});
await b.load(BASE, '', 6000);
await b.idle(20000);
if (process.env.FONT) await b.ev(`(() => { const st = document.createElement('style'); st.textContent = '#chip text:not(.t-net):not(.t-mono){font-family:' + ${JSON.stringify(process.env.FONT || '')} + ' !important}'; document.head.appendChild(st); return 1; })()`);
const graph = await b.ev('window.__chipTest.graph()');
const want = ONLY ? ONLY.split(',') : null;
const res = [];
for (const g of graph.filter(x => !x.err && (!want || want.includes(x.id)))) {
  await b.ev(`(() => { location.hash = ${JSON.stringify('#at=' + g.path.replace(/:/g, '%3A'))}; return 1; })()`);
  await sleep(350); await b.idle(15000); await sleep(250);
  const r = await b.ev(`(() => {
    const st = window.__chipState(), svg = document.getElementById('chip');
    const L = [...svg.querySelectorAll(':scope > g.lay')].find(l => l._key === st.path);
    if (!L) return {err: 'no layer'};
    const out = [];
    L.querySelectorAll('g.comp').forEach(c => {
      const r = c.querySelector(':scope > rect.shape'); if (!r) return;
      const x = +r.getAttribute('x'), y = +r.getAttribute('y'), w = +r.getAttribute('width'), h = +r.getAttribute('height');
      if (!(w > 0 && h > 0)) return;
      c.querySelectorAll(':scope > text').forEach(t => {
        if (!t.textContent.trim() || t.classList.contains('t-q')) return;
        let bb; try { bb = t.getBBox(); } catch (_) { return; }
        if (!bb.width) return;
        const an = t.getAttribute('text-anchor') || 'start', pad = 5;
        const right = bb.x + bb.width - (x + w - pad), left = (x + pad) - bb.x, low = (bb.y + bb.height) - (y + h - 2);
        if (right > 0.5 || left > 0.5) out.push({comp: c.getAttribute('data-comp') || '', s: t.textContent, fs: parseFloat(getComputedStyle(t).fontSize), fit: t.hasAttribute('data-fit'), right: +right.toFixed(1), left: +left.toFixed(1), low: +low.toFixed(1), anchor: an, boxW: w});
      });
    });
    return {path: st.path, out}; })()`);
  r.id = g.id; res.push(r);
  if (r.out && r.out.length) { console.log('==', g.id); r.out.forEach(o => console.log(`   [${o.comp}] ${JSON.stringify(o.s)} ${o.fs}px${o.fit ? ' (shrunk)' : ''}: past the box by ${Math.max(o.right, o.left)}u (box ${o.boxW}u wide)`)); }
}
writeFileSync(OUT, JSON.stringify(res));
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
