// shots.mjs URL OUTDIR : clean screenshots (no hover tooltip) of every scale in OUTDIR/graph.json, every flow stage and
// every tour slide, at 1440x900, reduced motion; the mouse rests outside the drawing and the source tooltip is hidden.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { readFileSync, mkdirSync } from 'node:fs';

const [URL, OUT] = process.argv.slice(2);
mkdirSync(OUT + '/shots', {recursive: true});
const ONLY = process.argv[4] || 'scales,flows,tour';
const graph = ONLY.includes('scales') ? JSON.parse(readFileSync(OUT + '/graph.json', 'utf8')) : [];
const b = await open({w: 1440, h: 900, dpr: 1, reduced: true});
await b.load(URL, '', 6000);
await b.idle(20000);
const go = async (hash, wait = 400) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(200); };
const clean = async () => { await b.mouse('mouseMoved', 1436, 896); await sleep(80);
  await b.ev(`(() => { const t = document.getElementById('srctip'); if (t) t.hidden = true; document.querySelectorAll('.tip, .srctip').forEach(e => { e.style.display = 'none'; }); return 1; })()`); await sleep(60); };
const safe = s => s.replace(/[^A-Za-z0-9_.-]+/g, '_').slice(0, 150);
let n = 0;
for (const g of graph) {
  n++;
  if (g.err) continue;
  await go('#at=' + g.path.replace(/:/g, '%3A'));
  await clean();
  await b.shot(`${OUT}/shots/scale-${String(n).padStart(3, '0')}-${safe(g.id)}.png`);
}
console.log('scales', n);
const KEY = {A: '1', B: '2', C: '3', D: '4', E: '5', F: '6', G: '7', H: '8', I: '9', J: '0', K: 'b'};
for (const k of (ONLY.includes('flows') ? Object.values(KEY) : [])) {
  await go('#flow=' + k + '&stage=0', 1200);
  const ns = await b.ev('window.__chipTest.nstages()');
  for (let i = 0; i < ns; i++) { await go('#flow=' + k + '&stage=' + i, 1500); await clean(); await b.shot(`${OUT}/shots/flow-${k}-stage-${i}.png`); }
  console.log('flow', k, ns);
}
for (let i = 1; i <= 17 && ONLY.includes('tour'); i++) { await go('#tour=' + i, 1500); await clean(); await b.shot(`${OUT}/shots/tour-${String(i).padStart(2, '0')}.png`); }
console.log('tour done; errors', b.errs.length);
await b.close();
