// profile.mjs <page.html> [w] : a CPU profile of a horizontal touch pan on the phone (4x CPU): the top self-time functions,
// and the frame's own costs (script, style, layout, paint) from a trace
import {launch, sleep} from './cdp.mjs';
import fs from 'node:fs';
const [, , file, W = '390'] = process.argv;
const pg = await launch();
const w = +W;
await pg.setViewport({w, h: 844, dsf: 3, mobile: true, touch: true, cpu: 4});
await pg.goto('file://' + file);
await sleep(2000);
await pg.eval(`(() => { cancelAnimationFrame(anim); animating = false; S.v = clampV(${8 * 86400 + 6 * 3600}, ${10 * 86400}); redrawAll(true); document.getElementById('tl').scrollIntoView({block: 'start'}); window.scrollBy(0, -60); })()`);
await sleep(500);
const r = await pg.eval(`(() => { const b = document.querySelector('#tl svg').getBoundingClientRect(); return {x: b.left, y: b.top, w: b.width}; })()`);
const y0 = r.y + (await pg.eval(`layout(main.W).rows.conc.y`)) + 20, x0 = r.x + r.w * 0.3;
await pg.s('Profiler.enable');
await pg.s('Profiler.setSamplingInterval', {interval: 200});
// a trace of the same pan: script, style, layout, paint per frame
const events = [];
pg.on(m => { if (m.method === 'Tracing.dataCollected') events.push(...m.params.value); });
const done = new Promise(res => pg.on(m => { if (m.method === 'Tracing.tracingComplete') res(); }));
await pg.s('Tracing.start', {traceConfig: {includedCategories: ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'blink.user_timing']}, transferMode: 'ReportEvents'});
await pg.s('Profiler.start');
await pg.touchPath(Array.from({length: 30}, (_, i) => [x0 + i * 6, y0]), 16);
await sleep(600);
const {profile} = await pg.s('Profiler.stop');
await pg.s('Tracing.end');
await done;
// self time per function
const byId = new Map(profile.nodes.map(n => [n.id, n]));
const self = new Map();
const dt = profile.timeDeltas;
profile.samples.forEach((id, i) => { const n = byId.get(id); const k = `${n.callFrame.functionName || '(anon)'}:${n.callFrame.lineNumber}`; self.set(k, (self.get(k) || 0) + (dt[i] || 0)); });
const tot = [...self.values()].reduce((a, b) => a + b, 0);
console.log('profile total ms', (tot / 1000).toFixed(0));
[...self.entries()].sort((a, b) => b[1] - a[1]).slice(0, 25).forEach(([k, v]) => console.log(String((v / 1000).toFixed(1)).padStart(8), k));
// the trace: total duration by event name, on the renderer main thread
const main = events.filter(e => e.ph === 'X' && e.dur);
const agg = new Map();
for (const e of main) agg.set(e.name, (agg.get(e.name) || 0) + e.dur);
console.log('\ntrace (ms, all threads, complete events):');
[...agg.entries()].sort((a, b) => b[1] - a[1]).slice(0, 22).forEach(([k, v]) => console.log(String((v / 1000).toFixed(1)).padStart(8), k));
if (process.argv[4]) fs.writeFileSync(process.argv[4], JSON.stringify(events.slice(0, 200000)));   // [trace.json]
await pg.close();
