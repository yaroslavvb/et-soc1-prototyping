#!/usr/bin/env python3
"""jit_probe.py <serve-dir> <out.json> [--page chip/index.html] [--vp 1440x900] [--dpr 2] [--cpu 1] [--presses 46]
           [--flows] [--trace trace.json]

Frame timing of the chip diagram's camera, with as little measuring as possible: on every animation frame it stores
performance.now() and the transform of each layer shown (attribute reads only, no layout), tagged with the current
move. The walk: + pressed again and again from #at=die.metal (each press waits for the camera to rest); --flows:
every flow, stage by stage. --cpu N slows the CPU N times (DevTools). --trace records a Chrome trace of the run."""
import argparse, functools, http.server, json, os, threading, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('root'); ap.add_argument('out')
ap.add_argument('--page', default='chip/index.html'); ap.add_argument('--hash', default='at=die.metal')
ap.add_argument('--vp', default='1440x900'); ap.add_argument('--dpr', type=float, default=2)
ap.add_argument('--cpu', type=float, default=1); ap.add_argument('--presses', type=int, default=46)
ap.add_argument('--flows', action='store_true'); ap.add_argument('--trace', default='')
ap.add_argument('--keys', default='')   # instead of + presses: a key sequence, e.g. "-,-,-,+,+"
a = ap.parse_args()

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=a.root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{srv.server_address[1]}/{a.page}'

REC = r"""() => { window.__J = []; window.__tag = 'load';
  const svg = document.getElementById('chip');
  const f = (t) => { const L = svg.querySelectorAll(':scope > g.lay'); const tr = [];
    for (const l of L) if (l.style.display !== 'none') tr.push([l.dataset.node, l.getAttribute('transform') || '', l.style.opacity || '']);
    window.__J.push([t, performance.now(), window.__tag, tr]); requestAnimationFrame(f); };
  requestAnimationFrame(f); }"""
BUSY = "() => { const s = window.__chipState && window.__chipState(); return !!(s && s.zooming); }"

def rest(pg, t0=0.25, cap=12.0, need=5):
    time.sleep(t0); end, calm = time.time() + cap, 0
    while time.time() < end:
        calm = calm + 1 if not pg.evaluate(BUSY) else 0
        if calm >= need: return True
        time.sleep(0.1)
    return False

w, h = map(int, a.vp.split('x'))
out = {'vp': a.vp, 'dpr': a.dpr, 'cpu': a.cpu, 'runs': []}
with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome', headless=True)
    try:
        ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=a.dpr, is_mobile=w < 600, has_touch=w < 600)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        cdp = ctx.new_cdp_session(pg)
        if a.cpu != 1: cdp.send('Emulation.setCPUThrottlingRate', {'rate': a.cpu})
        def walk(url, steps, label):
            pg.goto(url, wait_until='load'); time.sleep(2.5); rest(pg, 0, 15)
            pg.evaluate(REC)
            for i, (kind, arg) in enumerate(steps):
                pg.evaluate(f"window.__tag = {json.dumps(f'{label} {i} {kind} {arg}')}")
                if kind == 'click': pg.click(arg, force=True)
                else: pg.keyboard.press(arg)
                time.sleep(0.3); rest(pg)
            pg.evaluate("window.__tag = 'end'"); time.sleep(0.3)
            out['runs'].append({'label': label, 'frames': pg.evaluate('window.__J')})
        if a.trace: br.start_tracing(page=pg, path=a.trace, screenshots=False,
                                     categories=['devtools.timeline', 'disabled-by-default-devtools.timeline', 'v8', 'blink', 'cc', 'gpu', 'disabled-by-default-devtools.timeline.frame', 'disabled-by-default-v8.cpu_profiler'])
        if a.keys:
            walk(f'{BASE}#{a.hash}', [('key', k) for k in a.keys.split(',')], 'keys')
        else:
            walk(f'{BASE}#{a.hash}', [('click', '#pmz [data-ci="plus"]')] * a.presses, 'walk')
        if a.flows:
            # each flow from its first stage to its last, played by the arrow key, the camera following
            steps = []
            for k in '1234567890b':
                steps.append(('key', k)); steps.append(('key', ' '))
                steps += [('key', 'ArrowRight')] * 9
                steps.append(('key', 'Escape'))
            walk(f'{BASE}#at=die', steps, 'flows')
        if a.trace: br.stop_tracing()
        out['errors'] = errs
        json.dump(out, open(a.out, 'w'))
        print(f"{a.vp} dpr {a.dpr} cpu {a.cpu}: " + ', '.join(f"{r['label']} {len(r['frames'])} frames" for r in out['runs']) + f"; errors {errs[:2]}")
    finally:
        br.close(); srv.shutdown()
