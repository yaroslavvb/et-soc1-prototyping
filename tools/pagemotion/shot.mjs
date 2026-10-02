// node shot.mjs <page.html or url> <hash> <out.png> [w h dpr] [waitMs] [js] [fullPage]
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';
const [page, hash, outp, W = '1280', H = '800', DPR = '1', WAIT = '2500', JS = '', FULL = ''] = process.argv.slice(2);
import { tmpdir } from 'node:os';
import { startChrome } from './cdp.mjs';   // (a Mac's or Linux's Chrome, or CHROME: code review of 1 Oct; on a port of its own)
const udd = process.env.UDD || mkdtempSync(resolve(process.env.TMPDIR || tmpdir(), 'zd-shot-'));
const flags = process.env.DARK ? ['--force-dark-mode', '--blink-settings=preferredColorScheme=0'] : [];
const {ch, tl} = await startChrome(['--headless=new', `--window-size=${W},${H}`, '--hide-scrollbars', ...flags, 'about:blank'], udd, 80);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ws = new WebSocket(tl.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map(), errs = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.method === 'Runtime.exceptionThrown') errs.push(d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text); if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push(d.params.args.map(a => a.value || a.description).join(' ')); if (pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const call = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({id: i, method, params})); });
await call('Page.enable'); await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride', {width: +W, height: +H, deviceScaleFactor: +DPR, mobile: +W < 600});
if (+W < 600) await call('Emulation.setTouchEmulationEnabled', {enabled: true, maxTouchPoints: 5});
const url = /^https?:/.test(page) ? page + hash : 'file://' + resolve(page) + hash;
await call('Page.navigate', {url}); await sleep(+WAIT);
if (JS) { const r = await call('Runtime.evaluate', {expression: JS, awaitPromise: true, returnByValue: true}); if (r.result && r.result.result && r.result.result.value !== undefined) console.log('js:', JSON.stringify(r.result.result.value).slice(0, 2000)); await sleep(+(process.env.WAIT2 || 600)); }
const r = await call('Page.captureScreenshot', {format: 'png', captureBeyondViewport: !!FULL});
writeFileSync(outp, Buffer.from(r.result.data, 'base64'));
if (errs.length) console.log('ERRORS', errs.slice(0, 5));
ws.close(); ch.kill(); await sleep(200); if (!process.env.UDD) { try { rmSync(udd, {recursive: true, force: true}); } catch (_) {} }
console.log('shot', outp);
