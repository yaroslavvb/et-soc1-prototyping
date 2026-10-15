// crawl.mjs URL OUTDIR [--shots] [--max=N] [--only=static,scales,flows,tour]
// Dumps what a reader of the chip diagram sees: the static sections, every scale's own panel and every part's panel
// (by real clicks), every flow stage's caption and panel, every tour slide. Reduced motion, so the camera cuts.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { writeFileSync, mkdirSync } from 'node:fs';

const args = process.argv.slice(2);
const URL = args[0], OUT = args[1];
const SHOTS = args.includes('--shots');
const MAX = +((args.find(a => a.startsWith('--max=')) || '--max=100000').slice(6));
const ONLY = ((args.find(a => a.startsWith('--only=')) || '--only=static,scales,flows,tour').slice(7)).split(',');
mkdirSync(OUT + '/shots', {recursive: true});
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

const b = await open({w: 1440, h: 900, dpr: 1, reduced: true});
await b.load(URL, '', 6000);
await b.idle(20000);
await sleep(3000); // the lazy deep-zoom data arrives at idle

const panel = () => b.ev(`(() => { const e = document.getElementById('pn-body'); if (!e) return null; e.querySelectorAll('details').forEach(d => { d.open = true; }); return e.innerText; })()`);
const caption = () => b.ev(`(() => { const t = id => (document.getElementById(id) || {}).innerText || ''; return {k: t('cap-k'), cap: t('cap'), live: t('st-live'), sub: t('cap-sub'), scale: t('cap-scale'),
  stages: [...document.querySelectorAll('#stages button, #stages .stg')].map(x => x.innerText), crumbs: t('crumbs'), ro: t('scale-ro')}; })()`);
const go = async (hash, wait = 400) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(150); };
const safe = s => s.replace(/[^A-Za-z0-9_.-]+/g, '_').slice(0, 150);

if (ONLY.includes('static')) {
  await b.ev(`(() => { document.getElementById('facttab').scrollIntoView(); return 1; })()`); await sleep(4000);
  await b.ev(`(() => { document.getElementById('summary').scrollIntoView(); return 1; })()`); await sleep(1500);
  await b.ev(`(() => { window.scrollTo(0, 0); return 1; })()`); await sleep(500);
  const stat = await b.ev(`(() => { const T = id => { const e = document.getElementById(id); return e ? e.textContent : null; };
    const rows = sel => [...document.querySelectorAll(sel)].map(tr => [...tr.cells].map(c => c.textContent.trim()));
    return {summary: T('summary-text'), honest: T('honest-text'), asks: rows('#asktab tr'), facts: rows('#facttab tr'), electrons: rows('#eltab tr'),
      bodytext: document.body.innerText}; })()`);
  writeFileSync(OUT + '/static.json', JSON.stringify(stat, null, 1));
  log('static: facts rows', stat.facts.length, 'asks rows', stat.asks.length);
}

if (ONLY.includes('scales')) {
  const graph = await b.ev('window.__chipTest.graph()');
  writeFileSync(OUT + '/graph.json', JSON.stringify(graph, null, 1));
  log('graph scales', graph.length);
  const out = [];
  let n = 0;
  for (const g of graph) {
    if (n++ >= MAX) break;
    if (g.err) { out.push({path: g.path, err: g.err}); continue; }
    const hash = '#at=' + g.path.replace(/:/g, '%3A');
    try {
      await go(hash);
      const st = await b.state();
      const here = await panel();
      const cap = await caption();
      const parts = await b.ev('window.__chipTest.parts()');
      if (SHOTS) await b.shot(`${OUT}/shots/scale-${String(n).padStart(3, '0')}-${safe(g.id)}.png`);
      const pp = [];
      for (const p of parts) {
        if (p.w < 1 || p.h < 1 || p.x < 0 || p.y < 0 || p.x > 1440 || p.y > 900) { pp.push({label: p.label, key: p.key, kid: p.kid, offscreen: true}); continue; }
        await b.click(p.x, p.y); await sleep(120);
        const s2 = await b.state();
        pp.push({label: p.label, key: p.key, kid: p.kid, selected: s2.sel, panel: await panel()});
        if (s2.path !== st.path) await go(hash); // a click moved the camera: come back
      }
      out.push({path: g.path, id: g.id, at: hash, shown: st.path, node: st.node, scale_m: st.scale_m, here, cap, parts: pp});
      log(n, g.path, 'parts', parts.length);
    } catch (e) { out.push({path: g.path, err: String(e)}); log('ERR', g.path, String(e).slice(0, 200)); }
    if (n % 20 === 0) writeFileSync(OUT + '/scales.json', JSON.stringify(out, null, 1));
  }
  writeFileSync(OUT + '/scales.json', JSON.stringify(out, null, 1));
}

if (ONLY.includes('flows')) {
  const KEY = {A: '1', B: '2', C: '3', D: '4', E: '5', F: '6', G: '7', H: '8', I: '9', J: '0', K: 'b'};
  const out = [];
  for (const [F, k] of Object.entries(KEY)) {
    await go('#flow=' + k + '&stage=0', 1200);
    const ns = await b.ev('window.__chipTest.nstages()');
    const fl = {flow: F, key: k, nstages: ns, stages: []};
    for (let i = 0; i < ns; i++) {
      await go('#flow=' + k + '&stage=' + i, 1500);
      const st = await b.state();
      const cap = await caption();
      if (SHOTS) await b.shot(`${OUT}/shots/flow-${k}-stage-${i}.png`);
      fl.stages.push({i, state: {flow: st.flow, stage: st.stage, path: st.path}, cap, panel: await panel()});
    }
    out.push(fl); log('flow', F, k, ns);
    writeFileSync(OUT + '/flows.json', JSON.stringify(out, null, 1));
  }
}

if (ONLY.includes('tour')) {
  const out = [];
  for (let i = 1; i <= 17; i++) {
    await go('#tour=' + i, 1500);
    const st = await b.state();
    if (SHOTS) await b.shot(`${OUT}/shots/tour-${String(i).padStart(2, '0')}.png`);
    out.push({i, state: {tour: st.tour, flow: st.flow, stage: st.stage, path: st.path}, cap: await caption(), panel: await panel()});
  }
  writeFileSync(OUT + '/tour.json', JSON.stringify(out, null, 1));
  log('tour done');
}
writeFileSync(OUT + '/errors.json', JSON.stringify(b.errs, null, 1));
log('errors', b.errs.length);
await b.close();
