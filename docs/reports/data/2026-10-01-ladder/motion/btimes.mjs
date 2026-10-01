// node btimes.mjs PAGE at... : how long each scale on the path takes to draw (ms) and its node count, three times
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion/cdp.mjs';
const [PAGE, ...ats] = process.argv.slice(2);
const b = await open({w: 1280, h: 800, dpr: 1});
try {
  await b.load(PAGE, '', 1500); await b.idle(10000);
  for (const at of ats) {
    const runs = [];
    for (let i = 0; i < 3; i++) runs.push(await b.ev(`JSON.stringify(window.__chipTest.buildTimes(${JSON.stringify(at)}))`));
    const R = runs.map(r => JSON.parse(r));
    if (!R[0]) { console.log(at, 'no path'); continue; }
    console.log('==', at);
    R[0].forEach((x, i) => console.log('  ', x[0].padEnd(22), R.map(r => String(r[i][1]).padStart(6)).join(' '), 'ms', String(x[2]).padStart(6), 'nodes'));
  }
} finally { await b.close(); }
