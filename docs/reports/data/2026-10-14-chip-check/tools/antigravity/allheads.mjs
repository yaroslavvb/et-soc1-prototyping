// allheads.mjs [W H] [--font=FAMILY]: every scale of the ladder (the crawl's graph.json), its frame's title lines against
// its tag pills (KT.frame: g.frm text.t-big; ihead: g.ifr text.i-t; otitle: g.otl text.o-t and its pill), in the frame's
// own units: the horizontal gap from each title line's right end to the nearest pill on the same band (negative: overlap).
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
const args = process.argv.slice(2);
const W = +(args[0] || 1440), H = +(args[1] || 900);
const FONT = (args.find(a => a.startsWith('--font=')) || '').slice(7);
const OUT = '/home/yaroslavvb/claude/work/chip-check-1014/ag/out';
mkdirSync(OUT, {recursive: true});
const graph = JSON.parse(readFileSync('/home/yaroslavvb/claude/work/chip-check-1014/crawl/after/graph.json', 'utf8'));
const b = await open({w: W, h: H, dpr: 1, reduced: true, touch: W < 600});
await b.load('http://127.0.0.1:8918/chip.html', '', 5000);
await b.idle(20000); await sleep(2500);
if (FONT) await b.ev(`(() => { const s = document.createElement('style'); s.textContent = '#chip text{font-family:${FONT}!important}'; document.head.appendChild(s); return 1; })()`);
const go = async (hash, wait = 400) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(250); };
const res = [];
for (const g of graph) {
  if (g.err) continue;
  await go('#at=' + g.path.replace(/:/g, '%3A'));
  const r = await b.ev(`(() => {
    const L = [...document.querySelectorAll('#chip g.lay')].filter(l => l.style.display !== 'none' && l.dataset.node === ${JSON.stringify(g.id)}).pop();
    if (!L) return {err: 'no layer'};
    const out = [];
    L.querySelectorAll('g.frm, g.ifr, g.otl').forEach(fr => {
      const titles = [...fr.querySelectorAll(':scope > text.t-big, :scope > text.i-t, :scope > text.o-t')];
      const pills = [...fr.querySelectorAll(':scope > g.tg > rect, :scope > rect')].filter(r => r.getAttribute('rx')).map(r => ({x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height'), t: (r.parentNode.querySelector('text') || {}).textContent || (r.nextElementSibling || {}).textContent || ''}))
        .filter(p => p.h < 60);
      titles.forEach(t => { const bb = t.getBBox();
        pills.forEach(p => { const vov = Math.min(bb.y + bb.height, p.y + p.h) - Math.max(bb.y, p.y);
          if (vov <= 0) return;
          const gap = p.x >= bb.x ? p.x - (bb.x + bb.width) : bb.x - (p.x + p.w);
          out.push({title: t.textContent.slice(0, 70), cls: t.getAttribute('class'), right: +(bb.x + bb.width).toFixed(1), pill: p.t.slice(0, 50), pillX: p.x, gap: +gap.toFixed(1)}); }); });
    });
    return {pairs: out};
  })()`);
  const pairs = (r.pairs || []);
  const worst = pairs.length ? pairs.reduce((a, c) => (c.gap < a.gap ? c : a)) : null;
  res.push({id: g.id, path: g.path, worst, n: pairs.length, err: r.err});
  if (worst && worst.gap < 20) console.log(JSON.stringify({id: g.id, ...worst}));
}
writeFileSync(`${OUT}/allheads-${W}x${H}${FONT ? '-' + FONT.replace(/[^A-Za-z]/g, '') : ''}.json`, JSON.stringify(res, null, 1));
console.log('scales', res.length, 'with a title and pill on one band', res.filter(x => x.worst).length, 'gap<20', res.filter(x => x.worst && x.worst.gap < 20).length, 'overlap', res.filter(x => x.worst && x.worst.gap < 0).length);
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
