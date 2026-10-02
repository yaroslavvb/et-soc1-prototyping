// node ui_test.mjs page.html: drive the transport with real input events and check the state after each action
import { resolve } from 'node:path';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { startChrome } from './cdp.mjs';   // (since 1 Oct the installed Chrome or Chromium of cdp.mjs, a Mac's or Linux's, on a port of its own)
const udd = mkdtempSync(resolve(process.env.TMPDIR || tmpdir(), 'zd-ui-'));
const {ch, tl} = await startChrome(['--headless=new', '--window-size=1280,800', '--no-sandbox', 'about:blank'], udd, 80);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ws = new WebSocket(tl.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map(), errs = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.method === 'Runtime.exceptionThrown') errs.push(d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text); if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push(d.params.args.map(a => a.value || a.description).join(' ')); if (pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const call = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({id: i, method, params})); });
const ev = async e => (await call('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true})).result.result.value;
await call('Page.enable'); await call('Runtime.enable');
await call('Page.navigate', {url: 'file://' + resolve(process.argv[2]) + '#dram/load'}); await sleep(2500);
const KEYS = {' ': ['Space', 32, ' '], ArrowRight: ['ArrowRight', 39], ArrowLeft: ['ArrowLeft', 37], End: ['End', 35], Home: ['Home', 36]};
const key = async k => { const [code, kc, text] = KEYS[k]; await call('Input.dispatchKeyEvent', {type: text ? 'keyDown' : 'rawKeyDown', key: k, code, windowsVirtualKeyCode: kc, text}); await call('Input.dispatchKeyEvent', {type: 'keyUp', key: k, code, windowsVirtualKeyCode: kc}); };
const st = () => ev(`(() => { const s = __memState(), t = document.getElementById('scrub-track'); return {step: s.step, still: s.still, clock: s.clockOn, done: s.done, path: s.path.join('/'), play: document.getElementById('btn-play').textContent, lab: document.getElementById('scrub-lab').textContent, now: t.getAttribute('aria-valuenow'), fill: document.getElementById('scrub-fill').style.width}; })()`);
const mouse = async (type, x, y) => call('Input.dispatchMouseEvent', {type, x, y, button: 'left', buttons: type === 'mouseReleased' ? 0 : 1, clickCount: 1});
const track = await ev(`(() => { const r = document.getElementById('scrub-track').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()`);
const log = async (what) => console.log(what.padEnd(34), JSON.stringify(await st()));
await log('autoplay after 2.5 s');
await sleep(1500); await log('1.5 s later (fill grows)');
// focus the page body first so that keys reach it
await mouse('mousePressed', 5, 790); await mouse('mouseReleased', 5, 790);
await key(' '); await sleep(300); await log('Space: paused');
await key('ArrowRight'); await sleep(900); await log('Right arrow: next step, still');
await key('ArrowRight'); await sleep(900); await log('Right arrow again');
await key('ArrowLeft'); await sleep(900); await log('Left arrow');
// click at 80% of the track: step 9 of 11
const x = track[0] + track[2] * 0.8, y = track[1] + track[3] / 2;
await mouse('mousePressed', x, y); await sleep(120); await log('press on the track at 80% (preview)'); await mouse('mouseReleased', x, y); await sleep(1200); await log('released: goes to that step');
// drag from 20% to 50%
const x0 = track[0] + track[2] * 0.2, x1 = track[0] + track[2] * 0.5;
await mouse('mousePressed', x0, y); for (let k = 1; k <= 6; k++) await mouse('mouseMoved', x0 + (x1 - x0) * k / 6, y); await sleep(100);
await log('dragging to 50% (preview)'); await mouse('mouseReleased', x1, y); await sleep(1200); await log('drag released');
await key(' '); await sleep(1500); await log('Space: plays on from there');
await key('End'); await sleep(1500); await log('End');
await ev(`document.getElementById('btn-play').click()`); await sleep(1000); await log('Play button (Replay)');
await key('t'.toUpperCase() === 'T' ? ' ' : ' '); 
console.log(errs.length ? 'ERRORS ' + JSON.stringify(errs.slice(0, 5)) : 'no errors');
ws.close(); ch.kill(); await sleep(200); rmSync(udd, {recursive: true, force: true});
