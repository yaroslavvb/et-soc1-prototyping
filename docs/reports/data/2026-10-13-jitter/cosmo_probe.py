#!/usr/bin/env python3
"""cosmo_probe.py <serve-dir> <out-dir> [--vp 1440x900] [--presses 46] [--flows] [--hash at=die.metal]

The chip diagram's cosmetic consistency, measured. One headless Chrome. From the address, presses + again and again
(the default chain: down to the Planck length, round the loop, out through the levels above the rack and in again),
then (with --flows) plays every flow stage by stage. On every animation frame it records the page's chrome: box and
type size of the Up button, the crumbs, the readout, - and +, the drawing, the caption and the bar. At each rest it
saves a screenshot and the on-screen size of every visible label in the drawing, by class.
Writes <out-dir>/frames.json (per frame), rests.json (per rest) and rest-NN.png."""
import argparse, functools, http.server, json, os, threading, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('root'); ap.add_argument('out')
ap.add_argument('--vp', default='1440x900'); ap.add_argument('--presses', type=int, default=46)
ap.add_argument('--hash', default='at=die.metal'); ap.add_argument('--flows', action='store_true')
ap.add_argument('--page', default='index.html')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=a.root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/{a.page}#{a.hash}'

EL = ['#up', '#up .up-t', '#crumbs', '#scale-ro', '#pmz', '#svgwrap', '.st-bar', '#cap', '#cap-sub', '.st-cap',
      '#panel .pn-title', '.st-head', '#zstrip', '.kbd-hint']
SAMPLER = r"""(EL) => { window.__F = []; window.__tag = '';
  const f = () => { const row = {t: Math.round(performance.now()), tag: window.__tag, e: {}};
    for (const s of EL) { const e = document.querySelector(s); if (!e) continue; const r = e.getBoundingClientRect();
      if (!r.width && !r.height) { row.e[s] = null; continue; }
      const cs = getComputedStyle(e); row.e[s] = [+r.x.toFixed(1), +r.y.toFixed(1), +r.width.toFixed(1), +r.height.toFixed(1),
        cs.fontSize, cs.fontWeight, cs.color, cs.lineHeight]; }
    window.__F.push(row); requestAnimationFrame(f); };
  requestAnimationFrame(f); }"""
# the on-screen size of every visible label of the drawing, by its first class
LABELS = r"""() => { const out = {}; const svg = document.getElementById('chip');
  for (const t of svg.querySelectorAll('text')) {
    if (!t.getClientRects().length) continue; const r = t.getBoundingClientRect(); if (r.width < 1) continue;
    let op = 1, n = t; while (n && n !== svg) { const o = parseFloat(getComputedStyle(n).opacity); if (!isNaN(o)) op *= o; n = n.parentNode; }
    if (op < 0.5) continue;
    const m = t.getScreenCTM(); if (!m) continue; const px = parseFloat(getComputedStyle(t).fontSize) * Math.hypot(m.a, m.b);
    const k = (t.getAttribute('class') || '-').split(/\s+/)[0] || '-';
    (out[k] = out[k] || []).push([+px.toFixed(1), (t.textContent || '').slice(0, 40)]);
  }
  return out; }"""
BUSY = "() => { const s = window.__chipState && window.__chipState(); return !!(s && s.zooming) || document.querySelector('#scale-ro').className.includes('mv'); }"
STATE = "() => { const s = window.__chipState(); return {path: s.path, node: s.node, flow: s.flow, stage: s.stage, panel: s.panel, ro: document.querySelector('#scale-ro').textContent, up: document.querySelector('#up').textContent}; }"

def rest(pg, t0=0.2, cap=10.0, need=4):
    time.sleep(t0); end, calm = time.time() + cap, 0
    while time.time() < end:
        calm = calm + 1 if not pg.evaluate(BUSY) else 0
        if calm >= need: return True
        time.sleep(0.1)
    return False

rests = []
def snap(pg, tag):
    i = len(rests); st = pg.evaluate(STATE); st['tag'] = tag; st['labels'] = pg.evaluate(LABELS)
    pg.screenshot(path=os.path.join(a.out, f'rest-{i:03d}.png'))
    rests.append(st)

w, h = map(int, a.vp.split('x'))
with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome', headless=True)
    try:
        ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, is_mobile=w < 600, has_touch=w < 600)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL, wait_until='load'); time.sleep(2); rest(pg, 0, 12)
        pg.evaluate(SAMPLER, EL)
        snap(pg, 'start')
        for i in range(a.presses):
            pg.evaluate(f"window.__tag = 'plus {i}'")
            pg.click('#pmz [data-ci="plus"]', force=True); rest(pg)
            snap(pg, f'plus {i}')
        F_walk = pg.evaluate('window.__F')   # (a reload below starts a new record)
        if a.flows:
            # the flows: back to the die, then each flow's key and every stage by the arrow key
            pg.goto(URL.split('#')[0] + '#at=die', wait_until='load'); time.sleep(2); rest(pg, 0, 12)
            pg.evaluate(SAMPLER, EL)
            for key in '1234567890b':
                pg.evaluate(f"window.__tag = 'flow {key}'")
                pg.keyboard.press(key); time.sleep(0.5); rest(pg, 0.3, 15)
                pg.keyboard.press(' ')   # pause the flow: the stages are stepped by the arrow key
                n = pg.evaluate("window.__chipTest.nstages()") or 0
                snap(pg, f'flow {key} stage 0')
                for s in range(1, n):
                    pg.evaluate(f"window.__tag = 'flow {key} stage {s}'")
                    pg.keyboard.press('ArrowRight'); time.sleep(0.4); rest(pg, 0.2, 15)
                    snap(pg, f'flow {key} stage {s}')
                pg.keyboard.press('Escape'); time.sleep(0.5); rest(pg, 0.2, 10)
        F = F_walk + (pg.evaluate('window.__F') if a.flows else [])
        json.dump({'url': URL, 'vp': a.vp, 'errors': errs, 'frames': F}, open(os.path.join(a.out, 'frames.json'), 'w'))
        json.dump(rests, open(os.path.join(a.out, 'rests.json'), 'w'), ensure_ascii=False, indent=0)
        print(f'{a.vp}: {len(F)} frames, {len(rests)} rests, page errors: {errs[:3]}')
    finally:
        br.close(); srv.shutdown()
