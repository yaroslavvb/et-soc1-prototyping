// loadtm.mjs: where the memory levels' page spends its load (a phone at 4x CPU): the markers of the timing build
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion/cdp.mjs';
const runs = [];
for (let i = 0; i < 3; i++) {
  const b = await open({w: 390, h: 844, dpr: 3, touch: true, cpu: 4});
  await b.load('http://127.0.0.1:8766/p2tm/ml.html', '', 9000);
  const r = await b.ev(`(() => { const n = performance.getEntriesByType('navigation')[0], T = window.__TM, o = {resp: Math.round(n.responseEnd), dcl: Math.round(n.domContentLoadedEventEnd)};
    let p = T.s0; o.s0 = Math.round(T.s0); for (const k of Object.keys(T)) { if (k === 's0') continue; o[k] = Math.round(T[k] - p); p = T[k]; } return o; })()`);
  runs.push(r); console.log(JSON.stringify(r));
  await b.close();
}
