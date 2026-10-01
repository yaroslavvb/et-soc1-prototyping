// suite.mjs <page.html> <outdir> : the session timeline's gesture tests, phone and desktop, as the page checker's browser
// (chrome-headless-shell) runs them. Prints a table and writes <outdir>/results.json, screenshots and a frame sequence.
import {launch, sleep} from './cdp.mjs';
import fs from 'node:fs';
const [, , file, outdir] = process.argv;
fs.mkdirSync(outdir, {recursive: true});
const R = {page: file, when: new Date().toISOString(), phone: {}, desktop: {}};

// in-page instruments: rAF intervals, draw times of the two frames, long tasks
const INSTR = `(() => {
  if (!window.__ft) {
    window.__ft = {raf: [], draws: [], long: [], on: false};
    try { new PerformanceObserver(l => l.getEntries().forEach(e => __ft.on && __ft.long.push(Math.round(e.duration)))).observe({type: 'longtask'}); } catch (_) {}
    const wrap = f => { if (!f || f.__w) return; const r = f.redraw; f.redraw = function () { const t0 = performance.now(); const x = r.apply(this, arguments); if (__ft.on) __ft.draws.push(+(performance.now() - t0).toFixed(1)); return x; }; f.__w = 1; };
    window.__wrapFrames = () => { wrap(typeof main !== 'undefined' ? main : null); wrap(typeof detail !== 'undefined' ? detail : null); };
  }
  __wrapFrames();
  __ft.raf = []; __ft.draws = []; __ft.long = []; __ft.on = true; __ft.v = [];
  const loop = t => { if (!__ft.on) return; __ft.raf.push(t); __ft.v.push(S.v[0]); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
})()`;
const STOP = `(() => { __ft.on = false; const d = []; for (let i = 1; i < __ft.raf.length; i++) d.push(__ft.raf[i] - __ft.raf[i - 1]);
  const s = d.slice().sort((a, b) => a - b), q = p => s.length ? +s[Math.min(s.length - 1, Math.floor(p * s.length))].toFixed(1) : null;
  const moved = []; for (let i = 1; i < __ft.v.length; i++) if (__ft.v[i] !== __ft.v[i - 1]) moved.push(i);
  return {frames: d.length, mean: d.length ? +(d.reduce((a, b) => a + b, 0) / d.length).toFixed(1) : null, p50: q(0.5), p95: q(0.95), max: q(1), over50: d.filter(x => x > 50).length,
    draws: __ft.draws.length, drawMean: __ft.draws.length ? +(__ft.draws.reduce((a, b) => a + b, 0) / __ft.draws.length).toFixed(1) : null, drawMax: __ft.draws.length ? Math.max(...__ft.draws) : null,
    long: __ft.long.length, longMax: __ft.long.length ? Math.max(...__ft.long) : 0, framesWithViewChange: moved.length}; })()`;
const STATE = `(() => { const f = main, t = f.tip; return {y: Math.round(scrollY), v0: Math.round(S.v[0]), v1: Math.round(S.v[1]), span: Math.round(S.v[1] - S.v[0]), vv: visualViewport.scale,
  tip: t.style.display === 'block' ? t.textContent.slice(0, 60) : null, pinned: !!f.pinned}; })()`;
const chartRect = pg => pg.eval(`(() => { const b = document.querySelector('#tl svg').getBoundingClientRect(); return {x: b.left, y: b.top, w: b.width, h: b.height, L: main.L, R: main.R, W: main.W}; })()`);
async function view(pg, a, b) {   // put the timeline at [a, b] (seconds) with no animation, and the chart at the top of the viewport
  await pg.eval(`(() => { if (typeof stopMotion === 'function') stopMotion(); cancelAnimationFrame(anim); animating = false; S.v = clampV(${a}, ${b}); redrawAll(true); document.getElementById('tl').scrollIntoView({block: 'start'}); window.scrollBy(0, -60); })()`);
  await sleep(400);
}
const rowY = (pg, row) => pg.eval(`layout(main.W).rows[${JSON.stringify(row)}].y`);
const diff = (a, b) => ({dy: b.y - a.y, dv0: b.v0 - a.v0, dspan: b.span - a.span, vv: b.vv, tip: b.tip, pinned: b.pinned});

async function phone(w, h) {
  const out = {};
  const pg = await launch();
  await pg.setViewport({w, h, dsf: 3, mobile: true, touch: true, cpu: 4});
  await pg.goto('file://' + file);
  await sleep(2500);
  const D2 = [8 * 86400 + 6 * 3600, 10 * 86400];   // 27 Sep 06:00 to 29 Sep 00:00: a zoomed view, so a pan moves
  // 1. vertical swipe starting on the chart (over the agents' track)
  await view(pg, ...D2);
  let r = await chartRect(pg), y0 = r.y + await rowY(pg, 'conc') + 20, x0 = r.x + r.w * 0.6;
  let a = JSON.parse(JSON.stringify(await pg.eval(STATE)));
  await pg.eval(INSTR);
  await pg.touchPath(Array.from({length: 16}, (_, i) => [x0, y0 - i * 18]), 16);
  await sleep(900);
  out.vertical = Object.assign(diff(a, await pg.eval(STATE)), {timing: await pg.eval(STOP)});
  // 2. horizontal swipe (a pan to the earlier side: the finger moves right)
  await view(pg, ...D2);
  r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20; x0 = r.x + r.w * 0.3;
  a = await pg.eval(STATE);
  await pg.eval(INSTR);
  await pg.touchPath(Array.from({length: 16}, (_, i) => [x0 + i * 12, y0 + (i % 2)]), 16);
  const atLift = await pg.eval(STATE);
  await sleep(1200);
  const settled = await pg.eval(STATE);
  out.horizontal = Object.assign(diff(a, settled), {timing: await pg.eval(STOP), expectDv0: -Math.round(15 * 12 * a.span / (r.W - r.L - r.R)),
    afterLift: settled.v0 - atLift.v0});
  // a frame sequence of the same pan, one screenshot per step (not timed): what the reader sees during and after
  if (w === 390) {
    await view(pg, ...D2);
    r = await chartRect(pg);
    const dir = `${outdir}/frames-${w}`; fs.mkdirSync(dir, {recursive: true});
    const clip = {x: 0, y: Math.max(0, r.y), width: w, height: Math.min(r.h, 460)};
    const ev = (type, x) => pg.s('Input.dispatchTouchEvent', {type, touchPoints: type === 'touchEnd' ? [] : [{x, y: y0, id: 1, radiusX: 6, radiusY: 6, force: 1}]});
    await ev('touchStart', x0); await pg.shot(`${dir}/f00.png`, clip);
    for (let i = 1; i <= 8; i++) { await ev('touchMove', x0 + i * 20); await sleep(16); await pg.shot(`${dir}/f${String(i).padStart(2, '0')}.png`, clip); }
    await ev('touchEnd'); for (let i = 9; i <= 14; i++) { await sleep(80); await pg.shot(`${dir}/f${String(i).padStart(2, '0')}.png`, clip); }
  }
  // 3. diagonal swipe (45 degrees), and a mostly horizontal swipe with a vertical drift
  await view(pg, ...D2);
  r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20; x0 = r.x + r.w * 0.3;
  a = await pg.eval(STATE);
  await pg.touchPath(Array.from({length: 14}, (_, i) => [x0 + i * 12, y0 - i * 12]), 16);
  await sleep(900);
  out.diagonal45 = diff(a, await pg.eval(STATE));
  await view(pg, ...D2);
  r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20; x0 = r.x + r.w * 0.3;
  a = await pg.eval(STATE);
  await pg.touchPath(Array.from({length: 14}, (_, i) => [x0 + i * 14, y0 - i * 4]), 16);
  await sleep(900);
  out.driftHorizontal = diff(a, await pg.eval(STATE));
  await view(pg, ...D2); a = await pg.eval(STATE);
  await pg.touchPath(Array.from({length: 14}, (_, i) => [x0 + i * 4, y0 - i * 14 + 150]), 16);
  await sleep(900);
  out.driftVertical = diff(a, await pg.eval(STATE));
  // 4. two-finger pinch out (zoom in), centred on the chart
  await view(pg, ...D2);
  r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20; x0 = r.x + r.w * 0.55;
  a = await pg.eval(STATE);
  await pg.eval(INSTR);
  await pg.pinch(x0, y0, 30, 100, 20, 16);
  await sleep(900);
  out.pinch = Object.assign(diff(a, await pg.eval(STATE)), {timing: await pg.eval(STOP)});
  // 4b. a pinch, then one finger lifts and the other moves sideways: the pinch hands over to a drag
  await view(pg, ...D2);
  r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20; x0 = r.x + r.w * 0.55;
  {
    const P = (id, x) => ({x, y: y0, id, radiusX: 6, radiusY: 6, force: 1});
    await pg.s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [P(1, x0 - 40)]}); await sleep(16);
    await pg.s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [P(1, x0 - 40), P(2, x0 + 40)]}); await sleep(16);
    for (let i = 1; i <= 5; i++) { await pg.s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [P(1, x0 - 40 - 4 * i), P(2, x0 + 40 + 4 * i)]}); await sleep(16); }
    const mid = await pg.eval(STATE);
    await pg.s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: [P(1, x0 - 60)]}); await sleep(16);   // finger 1 lifts
    for (let i = 1; i <= 8; i++) { await pg.s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [P(2, x0 + 60 - 12 * i)]}); await sleep(16); }
    await pg.s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []}); await sleep(700);
    out.pinchHandoff = Object.assign(diff(mid, await pg.eval(STATE)), {note: 'after the lift: dv0 > 0 means the remaining finger panned'});
  }
  // 5. tap on a highlight flag, then on a bar (a card interval)
  await view(pg, ...D2);
  const flag = await pg.eval(`(() => { const g = [...document.querySelectorAll('#tl svg g[data-hl]')].find(g => g.getBoundingClientRect().left > 90) || document.querySelector('#tl svg g[data-hl]'); if (!g) return null; const b = g.getBoundingClientRect(); return {x: b.left + b.width / 2, y: b.top + b.height / 2, n: g.getAttribute('data-hl')}; })()`);
  a = await pg.eval(STATE);
  if (flag) { await pg.tap(flag.x, flag.y); await sleep(150); out.tapFlag = Object.assign(diff(a, await pg.eval(STATE)), {flag: flag.n}); await sleep(900); out.tapFlagAfter = diff(a, await pg.eval(STATE));
    const f2 = await pg.eval(`(() => { const g = document.querySelector('#tl svg g[data-hl="${flag.n}"]'); if (!g) return null; const b = g.getBoundingClientRect(); return {x: b.left + b.width / 2, y: b.top + b.height / 2}; })()`);
    if (f2) { await pg.tap(f2.x, f2.y); await sleep(1200); out.tapFlagAgain = diff(a, await pg.eval(STATE)); } }
  await view(pg, ...D2);
  const bar = await pg.eval(`(() => { const svg = document.querySelector('#tl svg'), rows = layout(main.W).rows, top = svg.getBoundingClientRect().top;
    const c = [...svg.querySelectorAll('rect[tabindex]')].map(n => n.getBoundingClientRect()).filter(b => b.width > 4 && b.left > 80 && b.top - top >= rows.card0.y - 2 && b.top - top < rows.inuse.y).sort((p, q) => q.width - p.width);
    const b = c[0]; return b ? {x: b.left + b.width / 2, y: b.top + b.height / 2} : null; })()`);
  a = await pg.eval(STATE);
  if (bar) { await pg.tap(bar.x, bar.y); await sleep(300); out.tapBar = diff(a, await pg.eval(STATE)); }
  // a tap with a 6 px jitter (a real finger): still a tap, not a pan
  if (bar) { await pg.eval('CK.hide(main)'); await sleep(200); a = await pg.eval(STATE); await pg.touchPath([[bar.x, bar.y], [bar.x + 3, bar.y + 1], [bar.x + 6, bar.y + 2]], 30); await sleep(300); out.tapJitter = diff(a, await pg.eval(STATE)); }
  await pg.shot(`${outdir}/phone-${w}.png`, Object.assign(await chartRect(pg), {x: 0, width: w, height: Math.min(h, 800)}));
  out.touchAction = await pg.eval(`getComputedStyle(document.querySelector('#tl svg')).touchAction`);
  out.overscrollX = await pg.eval(`(() => { const e = document.querySelector('#tl .ck-plot') || document.getElementById('tl'); return getComputedStyle(e).overscrollBehaviorX + ' / ' + getComputedStyle(document.getElementById('tl')).overscrollBehaviorX; })()`);
  out.logs = pg.logs;
  await pg.close();
  return out;
}
function FULLEND() { return 'FULL[1]'; }

async function desktop() {
  const out = {};
  const pg = await launch();
  await pg.setViewport({w: 1280, h: 800, dsf: 1, mobile: false, touch: false, cpu: 1});
  await pg.goto('file://' + file);
  await sleep(2000);
  const D2 = [8 * 86400 + 6 * 3600, 10 * 86400];
  await view(pg, ...D2);
  let r = await chartRect(pg), y0 = r.y + await rowY(pg, 'conc') + 20, x0 = r.x + r.w * 0.5;
  await pg.mouse('mouseMoved', x0, y0);
  // 1. plain vertical wheel over the chart: the page must scroll
  let a = await pg.eval(STATE);
  for (let i = 0; i < 6; i++) { await pg.wheel(x0, y0, 0, 100); await sleep(40); }
  await sleep(500);
  out.wheelVertical = diff(a, await pg.eval(STATE));
  // 2. a trackpad's horizontal swipe (deltaX): pans
  await view(pg, ...D2); r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20;
  a = await pg.eval(STATE);
  await pg.eval(INSTR);
  for (let i = 0; i < 12; i++) { await pg.wheel(x0, y0, 30, 2); await sleep(16); }
  await sleep(500);
  out.wheelDeltaX = Object.assign(diff(a, await pg.eval(STATE)), {timing: await pg.eval(STOP)});
  // 2b. a trackpad swipe that starts vertical and drifts horizontal (latched vertical: the page scrolls)
  await view(pg, ...D2); r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20;
  a = await pg.eval(STATE);
  for (let i = 0; i < 12; i++) { await pg.wheel(x0, y0, i < 4 ? 0 : 20, i < 4 ? 30 : 12); await sleep(16); }
  await sleep(500);
  out.wheelMixed = diff(a, await pg.eval(STATE));
  // 3. Shift + wheel: pans
  await view(pg, ...D2); r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20;
  a = await pg.eval(STATE);
  for (let i = 0; i < 5; i++) { await pg.wheel(x0, y0, 0, 100, 8); await sleep(40); }
  await sleep(500);
  out.shiftWheel = diff(a, await pg.eval(STATE));
  // 4. Ctrl + wheel (a trackpad pinch): zooms about the pointer
  await view(pg, ...D2); r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20;
  const px = r.x + r.w * 0.3;
  const tAt = () => pg.eval(`main.x.inv(${px} - document.querySelector('#tl svg').getBoundingClientRect().left)`);
  a = await pg.eval(STATE); const t0 = await tAt();
  await pg.eval(INSTR);
  for (let i = 0; i < 10; i++) { await pg.wheel(px, y0, 0, -20, 2); await sleep(16); }
  await sleep(600);
  const t1 = await tAt();
  out.ctrlWheel = Object.assign(diff(a, await pg.eval(STATE)), {focalDriftS: Math.round(t1 - t0), timing: await pg.eval(STOP)});
  // 5. a mouse drag pans
  await view(pg, ...D2); r = await chartRect(pg); y0 = r.y + await rowY(pg, 'conc') + 20;
  a = await pg.eval(STATE);
  await pg.eval(INSTR);
  await pg.mouse('mouseMoved', x0, y0); await pg.mouse('mousePressed', x0, y0, 1);
  for (let i = 1; i <= 20; i++) { await pg.mouse('mouseMoved', x0 - i * 10, y0, 1); await sleep(16); }
  await pg.mouse('mouseReleased', x0 - 200, y0, 0);
  await sleep(500);
  out.mouseDrag = Object.assign(diff(a, await pg.eval(STATE)), {timing: await pg.eval(STOP)});
  // 6. keyboard on the time axis
  await view(pg, ...D2);
  a = await pg.eval(STATE);
  await pg.eval(`document.querySelector('#tl svg [data-axis]').focus()`);
  await pg.key('ArrowRight'); await sleep(600);
  const k1 = await pg.eval(STATE);
  await pg.key('+', 'Equal', '+'); await sleep(600);
  const k2 = await pg.eval(STATE);
  await pg.key('0', 'Digit0', '0'); await sleep(600);
  const k3 = await pg.eval(STATE);
  out.keyboard = {right: k1.v0 - a.v0, plusSpan: k2.span - k1.span, zeroSpan: k3.span, focused: await pg.eval(`document.activeElement && document.activeElement.hasAttribute('data-axis')`)};
  // 7. a zoom button's animation: frame times of the whole animation
  await view(pg, ...D2);
  await pg.eval(INSTR);
  await pg.eval(`document.querySelector('#tl-zoom button[aria-label="Zoom out"]').click()`);
  await sleep(900);
  out.zoomButton = Object.assign(diff(a, await pg.eval(STATE)), {timing: await pg.eval(STOP)});
  out.overscrollX = await pg.eval(`(() => { const e = document.querySelector('#tl .ck-plot') || document.getElementById('tl'); return getComputedStyle(e).overscrollBehaviorX + ' / ' + getComputedStyle(document.getElementById('tl')).overscrollBehaviorX; })()`);
  await pg.shot(`${outdir}/desktop.png`, Object.assign(await chartRect(pg), {x: 0, width: 1280, height: 780}));
  out.logs = pg.logs;
  await pg.close();
  return out;
}

R.phone['390x844'] = await phone(390, 844);
R.phone['360x740'] = await phone(360, 740);
R.desktop['1280x800'] = await desktop();
fs.writeFileSync(`${outdir}/results.json`, JSON.stringify(R, null, 1));
const fmtT = t => t ? `frames ${t.frames}, rAF mean ${t.mean} p95 ${t.p95} max ${t.max} ms, >50ms ${t.over50}, draws ${t.draws} (mean ${t.drawMean}, max ${t.drawMax} ms), long tasks ${t.long} (max ${t.longMax})` : '';
for (const [k, o] of Object.entries(R.phone)) {
  console.log(`\nPHONE ${k}: touch-action ${o.touchAction}; overscroll-x ${o.overscrollX}`);
  for (const [t, v] of Object.entries(o)) if (v && typeof v === 'object' && 'dy' in v) console.log(`  ${t.padEnd(16)} dy=${v.dy} dv0=${v.dv0}s dspan=${v.dspan}s vv=${v.vv} tip=${v.tip ? JSON.stringify(v.tip.slice(0, 30)) : '-'} pinned=${v.pinned}${v.expectDv0 != null ? ' expectDv0≈' + v.expectDv0 + ' movedAfterLift=' + v.afterLift + 's' : ''}${v.timing ? '\n      ' + fmtT(v.timing) : ''}`);
  if (o.logs.length) console.log('  logs', JSON.stringify(o.logs));
}
for (const [k, o] of Object.entries(R.desktop)) {
  console.log(`\nDESKTOP ${k}: overscroll-x ${o.overscrollX}`);
  for (const [t, v] of Object.entries(o)) if (v && typeof v === 'object' && 'dy' in v) console.log(`  ${t.padEnd(16)} dy=${v.dy} dv0=${v.dv0}s dspan=${v.dspan}s${v.focalDriftS != null ? ' focalDrift=' + v.focalDriftS + 's' : ''}${v.timing ? '\n      ' + fmtT(v.timing) : ''}`);
  console.log('  keyboard', JSON.stringify(o.keyboard));
  if (o.logs.length) console.log('  logs', JSON.stringify(o.logs));
}
