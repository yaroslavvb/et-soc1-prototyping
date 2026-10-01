// A small DevTools-protocol driver for the page tests (zoom_test.mjs): headless Chrome, real input events (mouse,
// touch, keys), evaluation, screenshots. No packages: Node's own WebSocket and fetch.
//   const b = await open({w, h, dpr, touch, dark, reduced, udd, cpu}); await b.load(page, query); ... await b.close();
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { tmpdir, homedir } from 'node:os';

const CANDIDATES = [process.env.CHROME, resolve(homedir(), '.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'),
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome'].filter(Boolean);
export const CHROME = CANDIDATES.find(p => existsSync(p));
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function open(o = {}) {
  const W = o.w || 1280, H = o.h || 800, DPR = o.dpr || 1;
  const port = 9500 + Math.floor(Math.random() * 400);
  const udd = o.udd || mkdtempSync(resolve(process.env.TMPDIR || tmpdir(), 'zt-chrome-'));
  const args = ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, `--window-size=${W},${H}`, '--no-first-run',
    '--no-default-browser-check', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--hide-scrollbars', '--no-sandbox', 'about:blank'];
  const ch = spawn(CHROME, args, {stdio: 'ignore'});
  let tl = null;
  for (let i = 0; i < 100 && !tl; i++) { await sleep(100); try { tl = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page'); } catch (_) { /* not up */ } }
  if (!tl) throw new Error('no Chrome page target (CHROME=' + CHROME + ')');
  const ws = new WebSocket(tl.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let idc = 0; const pend = new Map(); const errs = [];
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.method === 'Runtime.exceptionThrown') errs.push('EXC ' + String(d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text).slice(0, 400));
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push('console.error ' + d.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 400));
    if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') errs.push('log ' + d.params.entry.text.slice(0, 300));
    if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); }
  };
  const send = (method, params = {}) => new Promise((res, rej) => { const id = ++idc; pend.set(id, {res, rej}); ws.send(JSON.stringify({id, method, params})); });
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: DPR, mobile: !!o.touch});
  if (o.touch) await send('Emulation.setTouchEmulationEnabled', {enabled: true, maxTouchPoints: 5});
  const feats = [];
  if (o.reduced) feats.push({name: 'prefers-reduced-motion', value: 'reduce'});
  if (o.dark === 'os') feats.push({name: 'prefers-color-scheme', value: 'dark'});
  if (o.touch) feats.push({name: 'hover', value: 'none'}, {name: 'pointer', value: 'coarse'});
  if (feats.length) await send('Emulation.setEmulatedMedia', {features: feats});
  if (o.cpu) await send('Emulation.setCPUThrottlingRate', {rate: o.cpu});
  if (o.pre) await send('Page.addScriptToEvaluateOnNewDocument', {source: o.pre});
  if (o.dark === true) await send('Page.addScriptToEvaluateOnNewDocument', {source: "(function f() { if (document.documentElement) document.documentElement.dataset.theme = 'dark'; else setTimeout(f, 0); })()"});
  const ev = async (e) => {
    const r = await send('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true});
    if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text));
    return r.result.value;
  };
  const b = {
    send, ev, errs, W, H, touch: !!o.touch,
    async load(page, query = '', wait = 1800) { await send('Page.navigate', {url: (/^https?:/.test(page) ? page : 'file://' + resolve(page)) + query}); await sleep(wait); },
    // the centre of the first element matching a selector (or a JS expression returning an element), in CSS px
    async box(sel) {
      return ev(`(() => { const e = ${sel.startsWith('js:') ? sel.slice(3) : `document.querySelector(${JSON.stringify(sel)})`}; if (!e) return null;
        const r = e.getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height}; })()`);
    },
    async mouse(type, x, y, clickCount = 1) { await send('Input.dispatchMouseEvent', {type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount}); },
    async click(x, y) { await b.mouse('mouseMoved', x, y); await b.mouse('mousePressed', x, y, 1); await b.mouse('mouseReleased', x, y, 1); },
    async dblclick(x, y) { await b.mouse('mouseMoved', x, y); await b.mouse('mousePressed', x, y, 1); await b.mouse('mouseReleased', x, y, 1); await sleep(60); await b.mouse('mousePressed', x, y, 2); await b.mouse('mouseReleased', x, y, 2); },
    async tap(x, y) {
      await send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x, y, radiusX: 4, radiusY: 4, force: 1, id: 1}]});
      await sleep(40);
      await send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
    },
    async dtap(x, y, gap = 150) { await b.tap(x, y); await sleep(gap); await b.tap(x, y); },
    async key(k, mod = 0) {
      const KEYS = {'+': ['Equal', 187, '+'], '-': ['Minus', 189, '-'], ArrowRight: ['ArrowRight', 39], ArrowLeft: ['ArrowLeft', 37], ArrowUp: ['ArrowUp', 38], ArrowDown: ['ArrowDown', 40],
        ' ': ['Space', 32, ' '], Enter: ['Enter', 13, '\r'], Backspace: ['Backspace', 8], Escape: ['Escape', 27], Tab: ['Tab', 9], PageDown: ['PageDown', 34], PageUp: ['PageUp', 33], Home: ['Home', 36], End: ['End', 35]};
      const [code, kc, text] = KEYS[k] || ['Key' + k.toUpperCase(), k.toUpperCase().charCodeAt(0), k];
      await send('Input.dispatchKeyEvent', {type: text ? 'keyDown' : 'rawKeyDown', key: k, code, windowsVirtualKeyCode: kc, text: text || undefined, modifiers: mod});
      await send('Input.dispatchKeyEvent', {type: 'keyUp', key: k, code, windowsVirtualKeyCode: kc, modifiers: mod});
    },
    // wait until the camera rests (no move in flight) for `settle` ms, at most `max` ms
    async idle(max = 8000, settle = 120) {
      const t0 = Date.now(); let quiet = 0;
      while (Date.now() - t0 < max) { const z = await ev('window.__chipState ? window.__chipState().zooming : false'); if (!z) { quiet += 40; if (quiet >= settle) return Date.now() - t0; } else quiet = 0; await sleep(40); }
      return -1;
    },
    state: () => ev('window.__chipState()'),
    async shot(out) { const r = await send('Page.captureScreenshot', {format: 'png'}); writeFileSync(out, Buffer.from(r.data, 'base64')); },
    async close() { try { ws.close(); } catch (_) { /* closed */ } ch.kill('SIGTERM'); await sleep(250); if (!o.udd) { try { rmSync(udd, {recursive: true, force: true}); } catch (_) { /* gone */ } } },
  };
  return b;
}
