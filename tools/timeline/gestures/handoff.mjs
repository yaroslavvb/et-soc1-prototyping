import {launch, sleep} from './cdp.mjs';
const pg = await launch();
await pg.setViewport({w: 390, h: 844, dsf: 3, mobile: true, touch: true, cpu: 1});
await pg.goto('file://' + process.argv[2]); await sleep(1500);
await pg.eval(`(() => { stopMotion(); S.v = clampV(${8 * 86400 + 6 * 3600}, ${10 * 86400}); redrawAll(true); document.getElementById('tl').scrollIntoView({block: 'start'}); window.scrollBy(0, -60);
  window.__ev = []; for (const t of ['pointerdown', 'pointermove', 'pointercancel', 'pointerup']) window.addEventListener(t, e => __ev.push(t.slice(7) + e.pointerId % 100 + '@' + Math.round(e.clientX) + ':' + Math.round(S.v[1] - S.v[0])), true); })()`);
await sleep(400);
const r = await pg.eval(`(() => { const b = document.querySelector('#tl svg').getBoundingClientRect(); return {x: b.left, y: b.top, w: b.width}; })()`);
const y0 = r.y + (await pg.eval(`layout(main.W).rows.conc.y`)) + 20, x0 = r.x + r.w * 0.55;
const P = (id, x) => ({x, y: y0, id, radiusX: 6, radiusY: 6, force: 1});
await pg.s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [P(1, x0 - 40)]}); await sleep(16);
await pg.s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [P(1, x0 - 40), P(2, x0 + 40)]}); await sleep(16);
for (let i = 1; i <= 5; i++) { await pg.s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [P(1, x0 - 40 - 4 * i), P(2, x0 + 40 + 4 * i)]}); await sleep(16); }
await pg.s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: [P(1, x0 - 60)]}); await sleep(16);
for (let i = 1; i <= 3; i++) { await pg.s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [P(2, x0 + 60 - 12 * i)]}); await sleep(16); }
await pg.s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []}); await sleep(300);
console.log((await pg.eval('__ev.join(" ")')));
await pg.close();
