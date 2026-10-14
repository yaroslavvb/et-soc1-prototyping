#!/usr/bin/env python3
"""bench_ops.py <serve-dir> [page] [hash ...]: what one camera frame's DOM writes cost in style and layout, scene by
scene: each write is done 40 times to the visible layer, each followed by a forced style and layout, and timed."""
import functools, http.server, json, sys, threading, time
from playwright.sync_api import sync_playwright
root = sys.argv[1]; page = sys.argv[2] if len(sys.argv) > 2 else 'chip/index.html'
hashes = sys.argv[3:] or ['at=die', 'at=die/shire:0', 'at=die.metal', 'at=studio45']
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BENCH = r"""() => {
  const svg = document.getElementById('chip');
  const L = [...svg.querySelectorAll(':scope > g.lay')].filter(l => l.style.display !== 'none').pop();
  const n = L.querySelectorAll('*').length, texts = L.querySelectorAll('text').length;
  const flush = () => { void document.body.offsetWidth; };
  const T = (f, N = 40) => { flush(); const t0 = performance.now(); for (let i = 0; i < N; i++) { f(i); flush(); } return +((performance.now() - t0) / N).toFixed(2); };
  const base = L.getAttribute('transform') || '';
  const m = i => `matrix(${1 + i * 0.002},0,0,${1 + i * 0.002},${i * 0.3},${i * 0.2})`;
  const r = {node: L.dataset.node, elements: n, texts};
  r.nothing = T(i => {});
  r.transform_attr = T(i => L.setAttribute('transform', m(i))); L.setAttribute('transform', base);
  r.transform_css = T(i => { L.style.transform = m(i).replace(/,/g, ', '); }); L.style.transform = '';
  r.custom_props = T(i => { const v = (0.5 + (i % 2) * 0.1).toFixed(3); for (const p of ['--lab', '--ctx', '--sat', '--ctxh', '--tgt', '--tsat']) L.style.setProperty(p, v); });
  for (const p of ['--lab', '--ctx', '--sat', '--ctxh', '--tgt', '--tsat']) L.style.removeProperty(p);
  r.opacity = T(i => { L.style.opacity = i % 2 ? 0.9 : 0.95; }); L.style.opacity = '';
  // the stroke keeper: every stroked shape's inline stroke-width
  const list = []; L.querySelectorAll('line, rect, path, circle, polygon').forEach(el => { const cs = getComputedStyle(el); if (cs.stroke && cs.stroke !== 'none') { const w = parseFloat(cs.strokeWidth); if (w > 0) list.push([el, w, el.style.strokeWidth]); } });
  r.stroked = list.length;
  r.stroke_keeper = T(i => { const k = 1 + (i % 7) * 0.3; list.forEach(([el, w]) => { el.style.strokeWidth = (w / k).toFixed(3) + 'px'; }); }, 20);
  list.forEach(([el, , s0]) => { el.style.strokeWidth = s0; });
  const ro = document.getElementById('scale-ro');
  r.readout_text = T(i => { ro.textContent = (1 + i) + '.2 µm · 10⁻⁶ m'; });
  const cr = document.getElementById('crumbs'), crumbsHTML = cr.innerHTML;
  r.crumbs_html = T(i => { cr.innerHTML = crumbsHTML + (i % 2 ? '<span class="sep">›</span>' : ''); }, 20);
  cr.innerHTML = crumbsHTML;
  const cap = document.getElementById('cap'), capHTML = cap.innerHTML;
  r.caption_html = T(i => { cap.innerHTML = '<span class="cap-in">' + (i % 2 ? 'A shorter caption line' : 'A rather longer caption line that runs on for a while') + '</span>'; }, 20);
  cap.innerHTML = capHTML;
  const pn = document.getElementById('pn-body'), pnHTML = pn.innerHTML;
  r.panel_html = T(i => { pn.innerHTML = pnHTML + (i % 2 ? '<p>one more line</p>' : ''); }, 20);
  pn.innerHTML = pnHTML;
  // is it the drawing? the readout's text with the drawing's wrapper a layout boundary, then with the drawing hidden
  const wr = document.getElementById('svgwrap'), wb = wr.getBoundingClientRect();
  wr.style.contain = 'strict'; wr.style.width = wb.width + 'px'; wr.style.height = wb.height + 'px';
  r.readout_text_svgwrap_contained = T(i => { ro.textContent = (3 + i) + '.2 µm · 10⁻⁶ m'; });
  r.crumbs_html_svgwrap_contained = T(i => { cr.innerHTML = crumbsHTML + (i % 2 ? '<span class="sep">›</span>' : ''); }, 20);
  cr.innerHTML = crumbsHTML; wr.style.contain = ''; wr.style.width = ''; wr.style.height = '';
  // the stylesheet's form: size and layout containment only, the size from the stage (no fixed width or height)
  wr.style.contain = 'size layout'; flush(); const wb2 = wr.getBoundingClientRect();
  r.svgwrap_box_same = Math.abs(wb2.width - wb.width) < 0.5 && Math.abs(wb2.height - wb.height) < 0.5;
  r.readout_text_svgwrap_sizelayout = T(i => { ro.textContent = (6 + i) + '.2 µm · 10⁻⁶ m'; });
  r.crumbs_html_svgwrap_sizelayout = T(i => { cr.innerHTML = crumbsHTML + (i % 2 ? '<span class="sep">›</span>' : ''); }, 20);
  r.up_label_svgwrap_sizelayout = T(i => { document.querySelector('#up .up-t').textContent = i % 2 ? '↑ Zoom out to the chip' : '↑ Zoom out to the wiring stack (metal layers)'; }, 20);
  r.transform_attr_svgwrap_sizelayout = T(i => L.setAttribute('transform', m(i))); L.setAttribute('transform', base);
  cr.innerHTML = crumbsHTML; wr.style.contain = '';
  // A: an explicit size only
  wr.style.width = wb.width + 'px'; wr.style.height = wb.height + 'px';
  r.A_readout_explicit_size = T(i => { ro.textContent = (7 + i) + '.2 µm · 10⁻⁶ m'; });
  wr.style.width = ''; wr.style.height = '';
  // B: the drawing absolutely positioned over its wrapper
  svg.style.position = 'absolute'; svg.style.inset = '0'; flush();
  const sb = svg.getBoundingClientRect(); r.B_svg_box_same = Math.abs(sb.width - wb.width) < 0.5 && Math.abs(sb.height - wb.height) < 0.5;
  r.B_readout_svg_absolute = T(i => { ro.textContent = (8 + i) + '.2 µm · 10⁻⁶ m'; });
  r.B_crumbs_svg_absolute = T(i => { cr.innerHTML = crumbsHTML + (i % 2 ? '<span class="sep">›</span>' : ''); }, 20);
  r.B_up_label_svg_absolute = T(i => { document.querySelector('#up .up-t').textContent = i % 2 ? '↑ Zoom out to the chip' : '↑ Zoom out to the wiring stack (metal layers)'; }, 20);
  r.B_panel_svg_absolute = T(i => { pn.innerHTML = pnHTML + (i % 2 ? '<p>one more line</p>' : ''); }, 20);
  cr.innerHTML = crumbsHTML; pn.innerHTML = pnHTML; svg.style.position = ''; svg.style.inset = '';
  svg.style.display = 'none'; r.readout_text_svg_hidden = T(i => { ro.textContent = (4 + i) + '.2 µm · 10⁻⁶ m'; }); svg.style.display = '';
  const prose = document.querySelector('.prose') || document.querySelector('main');
  if (prose) { const d0 = prose.style.display; prose.style.display = 'none'; r.readout_text_prose_hidden = T(i => { ro.textContent = (5 + i) + '.2 µm · 10⁻⁶ m'; }); prose.style.display = d0; }
  // the same writes with each box a layout boundary (fixed size, contain: strict)
  const fix = (el) => { const b = el.getBoundingClientRect(); el.style.width = b.width + 'px'; el.style.height = b.height + 'px'; el.style.contain = 'strict'; };
  fix(ro); r.readout_text_contained = T(i => { ro.textContent = (2 + i) + '.2 µm · 10⁻⁶ m'; });
  fix(cr); r.crumbs_html_contained = T(i => { cr.innerHTML = crumbsHTML + (i % 2 ? '<span class="sep">›</span>' : ''); }, 20);
  fix(cap); r.caption_html_contained = T(i => { cap.innerHTML = '<span class="cap-in">' + (i % 2 ? 'A shorter caption line' : 'A rather longer caption line that runs on for a while') + '</span>'; }, 20);
  const pnb = document.getElementById('panel'); fix(pnb); r.panel_html_contained = T(i => { pn.innerHTML = pnHTML + (i % 2 ? '<p>one more line</p>' : ''); }, 20);
  r.layout_objects_hint = document.querySelectorAll('*').length;
  return r; }"""
with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome', headless=True)
    try:
        import os; W, H = map(int, os.environ.get('VP', '1440x900').split('x')); pg = br.new_page(viewport={'width': W, 'height': H}, device_scale_factor=3 if W < 600 else 2, is_mobile=W < 600, has_touch=W < 600)
        for h in hashes:
            pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/{page}#{h}', wait_until='load'); time.sleep(3)
            print(h, json.dumps(pg.evaluate(BENCH)))
    finally:
        br.close(); srv.shutdown()
