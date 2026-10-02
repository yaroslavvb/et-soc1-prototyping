// firstload.mjs BASEURL NEWURL [runs] : first paint and load of two builds, a phone profile at CPU x4 (DESIGN §5.1: the
// first load within ±10 %), interleaved runs, a fresh profile each
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion/cdp.mjs';
const [A, B, runs = '3'] = process.argv.slice(2);
const res = {A: [], B: []};
for (let i = 0; i < +runs; i++) for (const [k, u] of [['A', A], ['B', B]]) {
  const b = await open({w: 390, h: 844, dpr: 3, touch: true, cpu: 4});
  await b.load(u, '', 9000);
  const r = await b.ev(`(() => { const n = performance.getEntriesByType('navigation')[0], p = performance.getEntriesByType('paint'); const f = p.find(x => x.name === 'first-contentful-paint');
    return {fcp: f ? Math.round(f.startTime) : null, dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd)}; })()`);
  res[k].push(r); console.log(k, i, JSON.stringify(r));
  await b.close();
}
const med = (arr, f) => { const v = arr.map(x => x[f]).sort((a, b) => a - b); return v[Math.floor(v.length / 2)]; };
for (const f of ['fcp', 'dcl', 'load']) console.log(f, 'base', med(res.A, f), 'new', med(res.B, f), `${(100 * (med(res.B, f) / med(res.A, f) - 1)).toFixed(1)}%`);
