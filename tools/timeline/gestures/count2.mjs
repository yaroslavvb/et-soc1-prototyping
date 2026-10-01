import {launch, sleep} from './cdp.mjs';
const pg = await launch();
await pg.setViewport({w: +process.argv[3] || 390, h: 844, dsf: 3, mobile: true, touch: true, cpu: +process.argv[4] || 1});
await pg.goto('file://' + process.argv[2]); await sleep(1500);
for (const [a, b] of [[21600, 'FULL[1]'], [8 * 86400 + 6 * 3600, 10 * 86400], [9 * 86400, 9 * 86400 + 6 * 3600]]) {
  const r = await pg.eval(`(() => { S.v = clampV(${a}, ${b}); S.drawFast = false; S.fast = false; main.redraw(); S.fast = true; S.drawFast = true; main.redraw();
    const ts = []; for (let i = 0; i < 5; i++) { S.v = clampV(S.v[0] + 600, S.v[1] + 600); const t0 = performance.now(); main.redraw(); ts.push(+(performance.now() - t0).toFixed(1)); }
    S.drawFast = false; S.fast = false; const n = document.querySelectorAll('#tl svg *').length; const t0 = performance.now(); main.redraw();
    return {span_h: Math.round((S.v[1] - S.v[0]) / 3600), fast_ms: ts, fastElements: n, full_ms: +(performance.now() - t0).toFixed(1), fullElements: document.querySelectorAll('#tl svg *').length}; })()`);
  console.log(JSON.stringify(r));
}
await pg.close();
