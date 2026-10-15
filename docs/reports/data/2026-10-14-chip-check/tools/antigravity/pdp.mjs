// pdp.mjs: cdp.mjs's open(), plus a patched page: requests for chip.html (or ml.html) are answered with the built page
// read from the repository with each [from, to] replacement applied once (each must match exactly once), so that a
// proposed source change can be tried in the real page without touching a file of the repository.
import { startChrome, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { tmpdir } from 'node:os';
const SRC = {
  'chip.html': '/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/2026-09-27-et-soc1-chip-diagram.html',
  'ml.html': '/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/2026-09-28-et-soc1-memory-levels.html',
};
export function patchText(text, patches) {
  for (const [a, b] of patches || []) {
    const n = text.split(a).length - 1;
    if (n !== 1) throw new Error(`patch matches ${n} times: ${a.slice(0, 90)}`);
    text = text.replace(a, () => b);
  }
  return text;
}
export async function openPatched(o = {}, patches = {}) {
  const W = o.w || 1440, H = o.h || 900, DPR = o.dpr || 1;
  const udd = mkdtempSync(resolve(process.env.TMPDIR || tmpdir(), 'pdp-chrome-'));
  const {ch, tl} = await startChrome(['--headless=new', `--window-size=${W},${H}`, '--no-first-run', '--no-default-browser-check',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--hide-scrollbars', '--no-sandbox', 'about:blank'], udd);
  if (!tl) throw new Error('no Chrome page target');
  const ws = new WebSocket(tl.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let idc = 0; const pend = new Map(); const errs = [];
  const bodies = {};
  for (const [k, file] of Object.entries(SRC)) bodies[k] = Buffer.from(patchText(readFileSync(file, 'utf8'), patches[k] || [])).toString('base64');
  const send = (method, params = {}) => new Promise((res, rej) => { const id = ++idc; pend.set(id, {res, rej}); ws.send(JSON.stringify({id, method, params})); });
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.method === 'Fetch.requestPaused') {
      const u = d.params.request.url.split(/[?#]/)[0], k = Object.keys(SRC).find(n => u.endsWith('/' + n));
      if (k) send('Fetch.fulfillRequest', {requestId: d.params.requestId, responseCode: 200, responseHeaders: [{name: 'Content-Type', value: 'text/html; charset=utf-8'}], body: bodies[k]});
      else send('Fetch.continueRequest', {requestId: d.params.requestId});
      return;
    }
    if (d.method === 'Runtime.exceptionThrown') errs.push('EXC ' + String(d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text).slice(0, 400));
    if (d.method === 'Runtime.consoleAPICalled' && (d.params.type === 'error' || d.params.type === 'warning')) errs.push('console.' + d.params.type + ' ' + d.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 400));
    if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); }
  };
  await send('Page.enable'); await send('Runtime.enable');
  await send('Fetch.enable', {patterns: [{urlPattern: '*', requestStage: 'Request'}]});
  await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: DPR, mobile: !!o.touch});
  if (o.touch) await send('Emulation.setTouchEmulationEnabled', {enabled: true, maxTouchPoints: 5});
  const feats = [];
  if (o.reduced) feats.push({name: 'prefers-reduced-motion', value: 'reduce'});
  if (o.touch) feats.push({name: 'hover', value: 'none'}, {name: 'pointer', value: 'coarse'});
  if (feats.length) await send('Emulation.setEmulatedMedia', {features: feats});
  const ev = async e => { const r = await send('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true}); if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text)); return r.result.value; };
  const b = {
    send, ev, errs,
    async load(url, wait = 4000) { await send('Page.navigate', {url}); await sleep(wait); },
    async idle(max = 8000, settle = 120) { const t0 = Date.now(); let q = 0; while (Date.now() - t0 < max) { const z = await ev('window.__chipState ? window.__chipState().zooming : (window.__memState ? window.__memState().zooming : false)'); if (!z) { q += 40; if (q >= settle) return; } else q = 0; await sleep(40); } },
    state: () => ev('window.__chipState()'),
    async mouse(type, x, y, clickCount = 1) { await send('Input.dispatchMouseEvent', {type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount}); },
    async click(x, y) { await b.mouse('mouseMoved', x, y); await b.mouse('mousePressed', x, y, 1); await b.mouse('mouseReleased', x, y, 1); },
    async shot(out) { const r = await send('Page.captureScreenshot', {format: 'png'}); writeFileSync(out, Buffer.from(r.data, 'base64')); },
    async close() { try { ws.close(); } catch (_) {} ch.kill('SIGTERM'); await sleep(250); try { rmSync(udd, {recursive: true, force: true}); } catch (_) {} },
  };
  return b;
}
