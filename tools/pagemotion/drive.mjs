// node drive.mjs <page.html> <hash> <out.json> [width height dpr] [maxSeconds]
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';
import { tmpdir } from 'node:os';
const [page, hash, outp, W = '1280', H = '800', DPR = '2', MAXS = '150'] = process.argv.slice(2);
// (the installed Chrome or Chromium cdp.mjs finds, a Mac's or Linux's; CHROME overrides it: code review of 1 Oct)
import { startChrome } from './cdp.mjs';
const udd = process.env.UDD || mkdtempSync(resolve(process.env.TMPDIR || tmpdir(), 'zd-chrome-'));
const args = ['--headless=new', `--window-size=${W},${H}`, `--force-device-scale-factor=${DPR}`,
  '--no-first-run', '--no-default-browser-check', '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows', '--hide-scrollbars', ...(process.env.CHROME_FLAGS ? process.env.CHROME_FLAGS.split(' ') : []), 'about:blank'];
let ch = null;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws, idc = 0; const pend = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const id = ++idc; pend.set(id, {res, rej}); ws.send(JSON.stringify({id, method, params})); });
try {
  // (Chrome on a port of its own: cdp.mjs startChrome)
  const S = await startChrome(args, udd); ch = S.ch; const tl = S.tl;
  if (!tl) throw new Error('no page target');
  ws = new WebSocket(tl.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  const TEV = [], CASTF = [], ERRS = []; let tdone = null; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.method === 'Tracing.dataCollected') { TEV.push(...d.params.value); return; } if (d.method === 'Tracing.tracingComplete') { tdone && tdone(); return; } if (d.method === 'Runtime.exceptionThrown') { ERRS.push('EXC ' + (d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text).slice(0, 300)); return; } if (d.method === 'Runtime.consoleAPICalled' && (d.params.type === 'error' || d.params.type === 'warning')) { ERRS.push(d.params.type + ' ' + d.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 300)); return; } if (d.method === 'Page.screencastFrame') { CASTF.push({ts: d.params.metadata.timestamp, data: d.params.data}); ws.send(JSON.stringify({id: ++idc, method: 'Page.screencastFrameAck', params: {sessionId: d.params.sessionId}})); return; } if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); } };
  await send('Page.enable'); await send('Runtime.enable');
  if (process.env.CPU) await send('Emulation.setCPUThrottlingRate', {rate: +process.env.CPU});
  await send('Page.addScriptToEvaluateOnNewDocument', {source: readFileSync(new URL(process.env.REC || './recorder.js', import.meta.url), 'utf8') + (process.env.PRE || '')});
  if (process.env.TRACE) await send('Tracing.start', {transferMode: 'ReportEvents', traceConfig: {includedCategories: (process.env.TRACE_CATS || 'devtools.timeline,disabled-by-default-devtools.timeline,v8,cc,gpu,toplevel').split(',')}});
  if (process.env.CAST) await send('Page.startScreencast', {format: 'jpeg', quality: 80, everyNthFrame: 1});
  // (a page on a local server, http://..., as it is: its lazily fetched data then loads, which file:// forbids)
  const url = (/^https?:/.test(page) ? page : 'file://' + resolve(page)) + (hash || '');
  await send('Page.navigate', {url});
  const ev = async e => (await send('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true})).result.value;
  const t0 = Date.now(); let st = null, lastStep = '';
  if (process.env.AFTERLOAD) { await sleep(1500); await ev(process.env.AFTERLOAD); }
  const KEYS = {'+': ['Equal', 187, '+'], '-': ['Minus', 189, '-'], 'ArrowRight': ['ArrowRight', 39], 'ArrowLeft': ['ArrowLeft', 37], ' ': ['Space', 32, ' '], 'Enter': ['Enter', 13, '\r'], 'Backspace': ['Backspace', 8], 'Escape': ['Escape', 27]};
  const key = async (k, mod = 0) => { const [code, kc, text] = KEYS[k] || ['Key' + k.toUpperCase(), k.toUpperCase().charCodeAt(0), k];
    await send('Input.dispatchKeyEvent', {type: text ? 'keyDown' : 'rawKeyDown', key: k, code, windowsVirtualKeyCode: kc, text: text || undefined, modifiers: mod});
    await send('Input.dispatchKeyEvent', {type: 'keyUp', key: k, code, windowsVirtualKeyCode: kc, modifiers: mod}); };
  if (process.env.SCEN) { await sleep(+(process.env.SCEN_DELAY || 1500)); for (const a of JSON.parse(process.env.SCEN)) { if (a.wait) await sleep(a.wait); if (a.key) await key(a.key, a.mod || 0); if (a.eval) await ev(a.eval); if (a.click) await ev(`(() => { const e = document.querySelector(${JSON.stringify(a.click)}); if (e) e.click(); return !!e; })()`); } }
  while (Date.now() - t0 < +MAXS * 1000) {
    await sleep(500);
    st = await ev(process.env.STATE || 'window.__memState ? window.__memState() : null');
    const sl = await ev(process.env.STEPTXT || "(document.getElementById('st-live')||{}).textContent");
    if (sl !== lastStep) { lastStep = sl; process.stderr.write(`${((Date.now() - t0) / 1000).toFixed(1)}s ${sl}\n`); }
    if (st && (process.env.UNTIL ? await ev(process.env.UNTIL) : (st.done && st.acc))) { await sleep(800); break; }
  }
  const out = await ev('JSON.stringify({wall: window.__WALL, log: window.__LOG, T: window.__T || [], loaf: window.__LOAF, st: (window.__memState || window.__chipState || (() => null))(), vw: innerWidth, vh: innerHeight, dpr: devicePixelRatio, svg: (() => { const r = (document.getElementById("mem") || document.getElementById("chip")).getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()})');
  writeFileSync(outp, out);
  if (ERRS.length) process.stderr.write('ERRORS:\n  ' + [...new Set(ERRS)].join('\n  ') + '\n'); else process.stderr.write('no console errors\n');
  if (process.env.CAST) { const { mkdirSync } = await import('node:fs'); mkdirSync(process.env.CAST, {recursive: true}); CASTF.forEach((f, i) => writeFileSync(`${process.env.CAST}/f${String(i).padStart(5, '0')}_${f.ts.toFixed(3)}.jpg`, Buffer.from(f.data, 'base64'))); process.stderr.write(`cast ${CASTF.length} frames\n`); }
  if (process.env.TRACE) { const p = new Promise(r => { tdone = r; }); await send('Tracing.end'); await p; writeFileSync(process.env.TRACE, JSON.stringify({traceEvents: TEV})); process.stderr.write(`trace ${TEV.length} events\n`); }
  process.stderr.write(`saved ${outp} (${(out.length / 1e6).toFixed(1)} MB) in ${((Date.now() - t0) / 1000).toFixed(1)} s; state ${JSON.stringify(st)}\n`);
} catch (e) { console.error(e); process.exitCode = 1; }
finally { try { ws && ws.close(); } catch (_) {} ch && ch.kill('SIGTERM'); await sleep(300); if (!process.env.UDD) { try { rmSync(udd, {recursive: true, force: true}); } catch (_) {} } }
