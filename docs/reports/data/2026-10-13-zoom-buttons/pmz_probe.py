#!/usr/bin/env python3
"""Measure how far the Up bar's - and + buttons move while the camera zooms (chip diagram, memory levels).

usage: uv run --with playwright python pmz_probe.py <serve-dir> <out.json> [--hash at=die.metal] [--seq m6,p12]
           [--vp 1920x1080,...] [--shots DIR]

Serves <serve-dir> (a built page as index.html, with a copy of docs/reports/ladder-img/ beside it) on 127.0.0.1, opens
it in one headless Chrome, and per viewport: records the - and + buttons' boxes on every animation frame while it
presses - and + (--seq: m6,p12 is six presses of -, then twelve of +; each press waits for the camera to rest), and
checks before each press whether the point where - first sat still hits the - button (a person pressing again at the
same spot). Widths under 600 emulate a touch phone. Prints one line per viewport (dx, dy: the largest spread of each
button's position over all frames; "at rest": over the moments before each press) and writes every press to <out.json>.
The installed Google Chrome by default (Playwright's channel "chrome"); CHROME=<path> to another Chrome or Chromium.
Written 13 Oct 2026 for Q107 (the README beside it has the numbers).
"""
import argparse, functools, http.server, json, os, threading, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('root'); ap.add_argument('out')
ap.add_argument('--hash', default='at=die.metal')
ap.add_argument('--seq', default='m6,p12')
ap.add_argument('--vp', default='1920x1080,1440x900,1280x800,1100x800,1024x768,820x1180,390x844')
ap.add_argument('--shots', default='')
a = ap.parse_args()

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=a.root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/index.html' + (f'#{a.hash}' if a.hash else '')

SAMPLER = r"""() => {
  const q = s => document.querySelector(s);
  const mi = q('#pmz [data-ci="minus"]'), pl = q('#pmz [data-ci="plus"]'), ub = q('#upbar'), ro = q('#scale-ro');
  window.__S = [];
  const f = () => {
    const A = mi.getBoundingClientRect(), B = pl.getBoundingClientRect(), U = ub.getBoundingClientRect();
    window.__S.push([+A.x.toFixed(1), +A.y.toFixed(1), +B.x.toFixed(1), +B.y.toFixed(1), +U.y.toFixed(1), +U.height.toFixed(1),
      ro.className.includes('mv') ? 1 : 0]);
    requestAnimationFrame(f);
  };
  requestAnimationFrame(f);
}"""
BUSY = "() => (typeof ZW !== 'undefined' && ZW) || document.querySelector('#scale-ro').className.includes('mv')"
STATE = r"""() => ({crumbs: [...document.querySelectorAll('#crumbs button')].map(b => b.textContent).join(' › '),
  up: document.querySelector('#up').textContent, ro: document.querySelector('#scale-ro').textContent})"""
HIT = r"""([x, y]) => { const e = document.elementFromPoint(x, y); const b = e && e.closest('button');
  return b ? (b.dataset.ci || b.id || b.className || 'button') : (e ? (e.id || e.className || e.tagName) : 'none'); }"""

def rest(page, t0=0.15, cap=8.0):
    time.sleep(t0)
    end, calm = time.time() + cap, 0
    while time.time() < end:
        calm = calm + 1 if not page.evaluate(BUSY) else 0
        if calm >= 3: return True
        time.sleep(0.1)
    return False

def rng(v): return round(max(v) - min(v), 1) if v else 0.0

res = {'url': URL, 'seq': a.seq, 'viewports': {}}
steps = []
for part in a.seq.split(','):
    steps += [('minus' if part[0] == 'm' else 'plus')] * int(part[1:])
with sync_playwright() as p:
    exe = os.environ.get('CHROME')
    br = p.chromium.launch(executable_path=exe, headless=True) if exe else p.chromium.launch(channel='chrome', headless=True)
    try:
        for vp in a.vp.split(','):
            w, h = map(int, vp.split('x'))
            phone = w < 600
            ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, is_mobile=phone, has_touch=phone)
            page = ctx.new_page()
            page.goto(URL, wait_until='load')
            time.sleep(1.5); rest(page, 0, 10)
            m0 = page.locator('#pmz [data-ci="minus"]').bounding_box()
            pt = [m0['x'] + m0['width'] / 2, m0['y'] + m0['height'] / 2]
            page.evaluate(SAMPLER)
            log, misses = [], 0
            for i, s in enumerate(steps):
                hit = page.evaluate(HIT, pt)
                if s == 'minus' and hit != 'minus': misses += 1
                st = page.evaluate(STATE)
                mb = page.locator('#pmz [data-ci="minus"]').bounding_box()
                pb = page.locator('#pmz [data-ci="plus"]').bounding_box()
                ub0 = page.locator('#upbar').bounding_box()
                log.append({'step': i, 'press': s, 'minus_at': [round(mb['x'], 1), round(mb['y'], 1)], 'hit_at_first_spot': hit,
                            'plus_right_inside_bar': round(ub0['x'] + ub0['width'] - (pb['x'] + pb['width']), 1),
                            'bar_w': round(ub0['width'], 1), 'bar_h': round(ub0['height'], 1), **st})
                if a.shots and i % 3 == 0:
                    os.makedirs(a.shots, exist_ok=True)
                    ub = page.locator('#upbar').bounding_box()
                    page.screenshot(path=os.path.join(a.shots, f'{vp}-{i:02d}.png'),
                                    clip={'x': 0, 'y': max(0, ub['y'] - 6), 'width': w, 'height': ub['height'] + 12})
                page.click(f'#pmz [data-ci="{s}"]', timeout=8000, force=True)
                rest(page)
            S = page.evaluate('window.__S')
            r = {'frames': len(S),
                 'minus_dx': rng([x[0] for x in S]), 'minus_dy': rng([x[1] for x in S]),
                 'plus_dx': rng([x[2] for x in S]), 'plus_dy': rng([x[3] for x in S]),
                 'upbar_dy': rng([x[4] for x in S]), 'upbar_dh': rng([x[5] for x in S]),
                 'minus_dx_rest': rng([e['minus_at'][0] for e in log]), 'minus_dy_rest': rng([e['minus_at'][1] for e in log]),
                 'presses_missing_minus_at_first_spot': misses,
                 'plus_right_inside_bar': sorted({e['plus_right_inside_bar'] for e in log}),
                 'bar_w': sorted({e['bar_w'] for e in log}), 'bar_h': sorted({e['bar_h'] for e in log}), 'log': log}
            res['viewports'][vp] = r
            print(f"{vp:>10}  frames {r['frames']:5d}  minus dx {r['minus_dx']:6.1f} dy {r['minus_dy']:5.1f}  "
                  f"plus dx {r['plus_dx']:6.1f} dy {r['plus_dy']:5.1f}  upbar dy {r['upbar_dy']:4.1f} dh {r['upbar_dh']:4.1f}  "
                  f"at rest: dx {r['minus_dx_rest']:5.1f} dy {r['minus_dy_rest']:4.1f}  misses {misses}/{steps.count('minus')}  "
                  f"+ to bar's right edge {r['plus_right_inside_bar']}  bar w {r['bar_w']} h {r['bar_h']}", flush=True)
            ctx.close()
    finally:
        br.close()
        srv.shutdown()
with open(a.out, 'w') as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
