// A small Chrome DevTools Protocol driver for the session timeline's gesture tests (Node 24: built-in WebSocket).
// launch() starts Playwright's chrome-headless-shell (the page checker's browser) with a debugging port.
// Adapted from ~/claude/work/memlevels-zoom/cdp.mjs.
import {spawn} from 'node:child_process';
import fs from 'node:fs';

const HS = process.env.CHROME_HEADLESS || `${process.env.HOME}/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`;
const WORK = process.env.GESTURE_WORK || `${process.env.HOME}/claude/work/timeline-gestures`;   // throwaway browser profiles (kept out of /tmp)
fs.mkdirSync(WORK, {recursive: true});

export async function launch(opts = {}) {
  const udd = fs.mkdtempSync(`${WORK}/.chrome-`);
  const args = ['--headless', '--no-sandbox', '--hide-scrollbars', '--remote-debugging-port=0', `--user-data-dir=${udd}`,
    '--window-size=1280,800', ...(opts.args || []), 'about:blank'];
  const proc = spawn(HS, args, {stdio: ['ignore', 'ignore', 'pipe']});
  const wsUrl = await new Promise((res, rej) => {
    let buf = '';
    const t = setTimeout(() => rej(new Error('chrome did not start: ' + buf)), 20000);
    proc.stderr.on('data', d => { buf += d; const m = /DevTools listening on (ws:\/\/\S+)/.exec(buf); if (m) { clearTimeout(t); res(m[1]); } });
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pend = new Map(), listeners = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pend.has(m.id)) { const {res, rej} = pend.get(m.id); pend.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); }
    else listeners.forEach(l => l(m));
  };
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, {res, rej}); ws.send(JSON.stringify({id: i, method, params, sessionId})); });
  const {targetInfos} = await send('Target.getTargets');
  const pg = targetInfos.find(t => t.type === 'page');
  const {sessionId} = await send('Target.attachToTarget', {targetId: pg.targetId, flatten: true});
  const s = (method, params) => send(method, params, sessionId).catch(e => { throw new Error(method + ' ' + JSON.stringify(params).slice(0, 300) + ': ' + e.message); });
  const on = fn => listeners.push(m => { if (m.sessionId === sessionId) fn(m); });
  const logs = [];
  on(m => {
    if (m.method === 'Runtime.exceptionThrown') logs.push({type: 'exception', text: m.params.exceptionDetails.exception ? m.params.exceptionDetails.exception.description : m.params.exceptionDetails.text});
    if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) logs.push({type: 'console.' + m.params.type, text: m.params.args.map(a => a.value !== undefined ? a.value : a.description).join(' ')});
  });
  await s('Runtime.enable'); await s('Page.enable');
  const page = {
    s, on, logs, proc,
    async setViewport(v) {
      await s('Emulation.setDeviceMetricsOverride', {width: v.w, height: v.h, deviceScaleFactor: v.dsf || 1, mobile: !!v.mobile});
      await s('Emulation.setTouchEmulationEnabled', v.touch ? {enabled: true, maxTouchPoints: 5} : {enabled: false});
      const feats = [];
      if (v.touch) feats.push({name: 'hover', value: 'none'}, {name: 'pointer', value: 'coarse'}, {name: 'any-hover', value: 'none'}, {name: 'any-pointer', value: 'coarse'});
      if (v.dark) feats.push({name: 'prefers-color-scheme', value: 'dark'});
      await s('Emulation.setEmulatedMedia', {features: feats});
      await s('Emulation.setCPUThrottlingRate', {rate: v.cpu || 1});
    },
    async goto(url) {
      const loaded = new Promise(res => { const l = m => { if (m.method === 'Page.loadEventFired') res(); }; on(l); });
      await s('Page.navigate', {url}); await loaded;
    },
    async eval(expr) {
      const r = await s('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
      if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text));
      return r.result.value;
    },
    // a one-finger touch path: pts = [[x, y], ...] in CSS px (viewport), one move every dt ms
    async touchPath(pts, dt = 16, id = 1) {
      await s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x: pts[0][0], y: pts[0][1], id, radiusX: 6, radiusY: 6, force: 1}]});
      for (let i = 1; i < pts.length; i++) {
        await sleep(dt);
        await s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [{x: pts[i][0], y: pts[i][1], id, radiusX: 6, radiusY: 6, force: 1}]});
      }
      await sleep(dt);
      await s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
    },
    // two fingers moving apart (or together) around (cx, cy): from half-distance d0 to d1, n steps
    async pinch(cx, cy, d0, d1, n = 20, dt = 16) {
      const tp = d => [{x: cx - d, y: cy, id: 1, radiusX: 6, radiusY: 6, force: 1}, {x: cx + d, y: cy, id: 2, radiusX: 6, radiusY: 6, force: 1}];
      await s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [tp(d0)[0]]});
      await sleep(dt);
      await s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: tp(d0)});
      for (let i = 1; i <= n; i++) { await sleep(dt); await s('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: tp(d0 + (d1 - d0) * i / n)}); }
      await sleep(dt);
      await s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
    },
    async tap(x, y) {
      await s('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x, y, id: 1, radiusX: 6, radiusY: 6, force: 1}]});
      await sleep(60);
      await s('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
    },
    async wheel(x, y, dx, dy, mods = 0) {
      await s('Input.dispatchMouseEvent', {type: 'mouseWheel', x, y, deltaX: dx, deltaY: dy, modifiers: mods});
    },
    async mouse(type, x, y, buttons = 0) {
      await s('Input.dispatchMouseEvent', {type, x, y, button: type === 'mouseMoved' ? 'none' : 'left', buttons, clickCount: type === 'mouseMoved' ? 0 : 1});
    },
    async key(key, code, text, mods = 0) {
      const vk = {ArrowLeft: 37, ArrowRight: 39, '+': 187, '-': 189, '0': 48, Tab: 9, Enter: 13}[key];
      await s('Input.dispatchKeyEvent', {type: 'keyDown', key, code: code || key, text, windowsVirtualKeyCode: vk, modifiers: mods});
      await s('Input.dispatchKeyEvent', {type: 'keyUp', key, code: code || key, windowsVirtualKeyCode: vk, modifiers: mods});
    },
    async shot(path, clip) {
      const r = await s('Page.captureScreenshot', Object.assign({format: 'png'}, clip ? {clip: Object.assign({scale: 1}, clip)} : {}));
      fs.writeFileSync(path, Buffer.from(r.data, 'base64'));
    },
    async screencast(o = {}) {
      const frames = [];
      const l = async m => {
        if (m.method !== 'Page.screencastFrame') return;
        frames.push({t: m.params.metadata.timestamp, data: m.params.data});
        try { await s('Page.screencastFrameAck', {sessionId: m.params.sessionId}); } catch (_) { /* stopped */ }
      };
      on(l);
      await s('Page.startScreencast', {format: 'jpeg', quality: 70, maxWidth: o.maxWidth || 1280, maxHeight: o.maxHeight || 1400, everyNthFrame: 1});
      return async () => { await s('Page.stopScreencast'); return frames; };
    },
    sleep,
    async close() { try { await send('Browser.close'); } catch (_) { /* gone */ } proc.kill(); try { fs.rmSync(udd, {recursive: true, force: true}); } catch (_) { /* kept */ } },
  };
  return page;
}
export const sleep = ms => new Promise(r => setTimeout(r, ms));
