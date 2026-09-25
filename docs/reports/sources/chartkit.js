/* chartkit.js: the shared chart toolkit of the ET-SoC-1 reports (global CK; no library).
   Source-built pages get it from report.template.html (scripts/build-report.py inlines it before the page script);
   standalone pages get this file, the template's chartkit CSS and token aliases from scripts/paste-chartkit.py.
   Colours are the template tokens only: series var(--c1..c5, c7), --ref, --ink/--ink-2/--muted, --grid/--axis,
   --surface/--page. No hex colours. A frame's viewBox is its CSS width, so 12-unit text is 12 px on a phone.
   API (see PLAN2 §2.5): el txt path frame lin log axes fmt tip keynav legend showSeries seg range readout bus
   stackTable reduced ramp rampInk color, and inside(f, labels) to keep a page's own end-of-axis labels in the frame. Every mark with a tooltip is reachable from the keyboard. */
window.CK = (function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg', frames = [], buses = {};
  let uid = 0;
  const $ = h => (typeof h === 'string' ? document.getElementById(h) : h);
  const mm = q => (window.matchMedia ? window.matchMedia(q) : {matches: false});
  const reduced = mm('(prefers-reduced-motion: reduce)').matches;

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, str, cls, anchor) {
    const t = el('text', {x, y, class: cls || 'tick', 'text-anchor': anchor || 'start'}, parent);
    t.textContent = str;
    return t;
  }
  const path = (pts, x, y) => pts.map((p, i) => (i ? 'L' : 'M') + x(p[0]).toFixed(1) + ',' + y(p[1]).toFixed(1)).join(' ');

  /* ---- numbers ---- */
  function num(v, dp) {
    if (v == null || !isFinite(v)) return '\u2014';
    const auto = dp == null;  // no dp: three significant digits, trailing zeros dropped
    if (auto) dp = v === 0 ? 0 : Math.min(6, Math.max(0, 2 - Math.floor(Math.log10(Math.abs(v)))));
    const s = Number(v).toLocaleString('en-GB', {minimumFractionDigits: auto ? 0 : dp, maximumFractionDigits: dp});
    return /[1-9]/.test(s) ? s.replace('-', '\u2212') : s.replace('-', '');  // true minus; never "−0.00"
  }
  const fmt = {
    num,
    range: (a, b, dp, unit) => {
      const s = num(a, dp), t = num(b, dp), u = unit ? '\u00a0' + unit : '';
      return s === t ? s + u : s + (b < 0 ? ' to ' : '\u2013') + t + u;
    },
    pct: (v, dp) => num(100 * v, dp == null ? 0 : dp) + '%',
  };

  /* ---- scales ---- */
  function niceTicks(a, b, n) {
    const lo = Math.min(a, b), hi = Math.max(a, b);
    if (!(hi > lo)) return Object.assign([lo], {step: 1});
    const raw = (hi - lo) / Math.max(1, n || 5), p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    const step = (m >= 7.5 ? 10 : m >= 3.5 ? 5 : m >= 1.5 ? 2 : 1) * p, out = [];
    for (let i = Math.ceil(lo / step - 1e-9); i * step <= hi + step * 1e-9; i++) out.push(+(i * step).toPrecision(12));
    out.step = step;
    return out;
  }
  const tickDp = t => (t.step ? Math.max(0, -Math.floor(Math.log10(t.step) + 1e-9)) : null);
  function lin(d0, d1, r0, r1) {
    const s = v => r0 + (v - d0) * (r1 - r0) / (d1 - d0);
    s.inv = p => d0 + (p - r0) * (d1 - d0) / (r1 - r0);
    s.ticks = n => niceTicks(d0, d1, n);
    s.domain = [d0, d1]; s.range = [r0, r1];
    return s;
  }
  function log(d0, d1, r0, r1) {
    const l0 = Math.log10(d0), l1 = Math.log10(d1);
    const s = v => r0 + (Math.log10(v) - l0) * (r1 - r0) / (l1 - l0);
    s.inv = p => Math.pow(10, l0 + (p - r0) * (l1 - l0) / (r1 - r0));
    s.ticks = n => {
      const lo = Math.min(l0, l1), hi = Math.max(l0, l1), k0 = Math.ceil(lo - 1e-9), k1 = Math.floor(hi + 1e-9);
      const dec = k1 - k0 + 1, every = Math.max(1, Math.ceil(dec / (n || 6))), out = [];
      const add = v => { v = +v.toPrecision(12); const lv = Math.log10(v); if (lv >= lo - 1e-9 && lv <= hi + 1e-9) out.push(v); };
      if (dec <= 2) { for (let k = k0 - 1; k <= k1; k++) for (const m of [1, 2, 5]) add(m * Math.pow(10, k)); }
      else for (let k = k0; k <= k1; k += every) add(Math.pow(10, k));
      return out;
    };
    s.domain = [d0, d1]; s.range = [r0, r1]; s.log = true;
    return s;
  }
  const logFmt = v => num(v, v >= 1 ? 0 : Math.ceil(-Math.log10(v) - 1e-9));

  /* ---- frame: a responsive SVG sized to its host ---- */
  function frame(hostId, o) {
    const host = $(hostId);
    if (!host) throw new Error('CK.frame: no element ' + hostId);
    host.classList.add('ck-frame'); host.classList.remove('scroll');
    host.textContent = '';
    const plot = document.createElement('div'); plot.className = 'ck-plot'; host.appendChild(plot);
    const svg = el('svg', {role: 'group', 'aria-label': o.label || null}, plot);
    const tip = document.createElement('div'); tip.className = 'ck-tip'; tip.setAttribute('aria-hidden', 'true');
    host.appendChild(tip);
    const minW = o.minW == null ? 320 : o.minW, maxW = o.maxW == null ? 900 : o.maxW;
    const f = {svg, host, tip, W: 0, H: 0, narrow: false, seriesOn: null, pinned: null, active: null, navIndex: 0};
    const width = () => {
      const cs = getComputedStyle(host), cw = host.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      return Math.round(Math.max(minW, Math.min(maxW, cw > 0 ? cw : maxW)));
    };
    f.redraw = () => {
      const W = width(), H = Math.round(typeof o.height === 'function' ? o.height(W) : (o.height || 300));
      f.refocus = svg.contains(document.activeElement) ? f.navIndex : null;
      hide(f, true);
      Object.assign(f, {W, H, narrow: W < 600, navNodes: []});
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W); svg.setAttribute('height', H);
      svg.style.width = W + 'px';
      o.draw(f);
      if (f.seriesOn) showSeries(f, f.seriesOn);
    };
    f.redraw();
    frames.push(f);
    if (window.ResizeObserver) {
      let timer;
      new ResizeObserver(() => { clearTimeout(timer); timer = setTimeout(() => { if (width() !== f.W) f.redraw(); }, 150); }).observe(host);
    }
    return f;
  }

  /* ---- axes: horizontal grid, tick labels, baseline, axis titles (y title sits above the plot) ---- */
  function axes(f, o) {
    const {x, y} = o, W = f.W, H = f.H;
    const L = o.L == null ? 44 : o.L, R = o.R == null ? 12 : o.R, T = o.T == null ? 22 : o.T, B = o.B == null ? 38 : o.B;
    const g = el('g', {class: 'ck-axes', 'aria-hidden': 'true'}, f.svg);
    const yt = o.yt || y.ticks(Math.max(3, Math.round((H - T - B) / 48)));
    const xt = o.xt || x.ticks(Math.max(2, Math.round((W - L - R) / 90)));
    const auto = (s, t) => (s.log ? logFmt : v => num(v, tickDp(t)));
    const xf = o.xfmt || auto(x, xt), yf = o.yfmt || auto(y, yt), labs = [];
    for (const t of yt) {
      if (o.grid !== false) el('line', {x1: L, x2: W - R, y1: y(t), y2: y(t), class: 'grid-line'}, g);
      labs.push(txt(g, L - 6, y(t) + 4, yf(t), 'tick', 'end'));
    }
    el('line', {x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ck-axis'}, g);
    for (const t of xt) labs.push(txt(g, x(t), H - B + 16, xf(t), 'tick', 'middle'));
    if (o.xl) labs.push(txt(g, (L + W - R) / 2, H - 6, o.xl, 'lab', 'middle'));
    if (o.yl) txt(g, 2, Math.max(12, T - 13), o.yl, 'lab');
    inside(f, labs);
    return g;
  }
  /* Keep labels inside the frame (0..f.W, 0..f.H, less pad): one that would cross the left or right edge is anchored
     at that edge instead (text-anchor start or end, so its outer end sits pad px from the edge in any font; an end
     tick label still covers its tick), and one that would cross the top or bottom is moved in. Labels already inside
     are not touched. Widths are measured in the page's font; a chart drawn while hidden has no layout, so they are
     estimated at 0.6 em a character. Vertically the glyphs are taken as 0.75 em above the baseline and 0.25 em below. */
  function inside(f, labels, pad) {
    pad = pad == null ? 2 : pad;
    const m = labels.map(t => {
      let w = 0, fs = 12;
      try { w = t.getComputedTextLength(); fs = parseFloat(getComputedStyle(t).fontSize) || 12; } catch (_) { /* no layout */ }
      return {w: w > 0 ? w : 0.6 * fs * t.textContent.length, fs};
    });
    labels.forEach((t, k) => {
      const {w, fs} = m[k], a = t.getAttribute('text-anchor') || 'start', x = +t.getAttribute('x'), y = +t.getAttribute('y');
      const x0 = a === 'end' ? x - w : a === 'middle' ? x - w / 2 : x;
      if (x0 < pad) { t.setAttribute('text-anchor', 'start'); t.setAttribute('x', pad); }
      else if (x0 + w > f.W - pad) { t.setAttribute('text-anchor', 'end'); t.setAttribute('x', +(f.W - pad).toFixed(1)); }
      if (y - 0.75 * fs < pad) t.setAttribute('y', +(pad + 0.75 * fs).toFixed(1));
      else if (y + 0.25 * fs > f.H - pad) t.setAttribute('y', +(f.H - pad - 0.25 * fs).toFixed(1));
    });
    return labels;
  }

  /* ---- tooltip: pointer, keyboard focus and touch all show the same text ---- */
  const strip = html => new DOMParser().parseFromString(String(html).replace(/<br\s*\/?>/gi, '; '), 'text/html')
    .body.textContent.replace(/\s+/g, ' ').trim();
  function place(f, cx, cy) {
    const t = f.tip; t.style.display = 'block';
    const hw = f.host.clientWidth, hh = f.host.clientHeight, tw = t.offsetWidth, th = t.offsetHeight;
    let top = cy + 14;
    if (top + th > hh && cy - th - 10 >= 0) top = cy - th - 10;  // flip above the pointer
    t.style.left = Math.max(0, Math.min(cx + 12, hw - tw)) + 'px';
    t.style.top = top + 'px';
  }
  function show(f, node, html, cx, cy) {
    if (f.active && f.active !== node) f.active.classList.remove('ck-active');
    f.active = node; node.classList.add('ck-active');
    f.tip.innerHTML = typeof html === 'function' ? html() : html;
    if (cx == null) {
      const r = node.getBoundingClientRect(), b = f.host.getBoundingClientRect();
      cx = r.left + r.width / 2 - b.left; cy = r.top + r.height / 2 - b.top;
    }
    place(f, cx, cy);
  }
  function hide(f, force) {
    if (f.pinned && !force) return;
    f.pinned = null; f.tip.style.display = 'none';
    if (f.active) f.active.classList.remove('ck-active');
    f.active = null;
  }
  function tip(f, node, html, o) {
    o = o || {};
    if (!node.hasAttribute('data-ck-nav')) node.setAttribute('tabindex', '0');
    node.setAttribute('role', o.role || 'img');
    node.setAttribute('aria-label', strip(typeof html === 'function' ? html() : html));
    node._ckTip = html;
    const at = ev => { const b = f.host.getBoundingClientRect(); show(f, node, html, ev.clientX - b.left, ev.clientY - b.top); };
    node.addEventListener('pointerenter', ev => { if (ev.pointerType !== 'touch' && !f.pinned) at(ev); });
    node.addEventListener('pointermove', ev => { if (ev.pointerType !== 'touch' && !f.pinned) at(ev); });
    node.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') hide(f); });
    node.addEventListener('pointerdown', ev => {  // touch: a tap toggles the tooltip and pins it until the next tap
      if (ev.pointerType !== 'touch') return;
      f.touchT = Date.now();
      if (f.active === node && f.tip.style.display === 'block') hide(f, true); else { hide(f, true); at(ev); f.pinned = node; }
    });
    node.addEventListener('focus', () => { if (Date.now() - (f.touchT || 0) > 600 && !f.pinned) show(f, node, html); });
    node.addEventListener('blur', () => hide(f));
    node.addEventListener('keydown', ev => { if (ev.key === 'Escape') hide(f, true); });
    return node;
  }
  document.addEventListener('pointerdown', ev => {  // a tap elsewhere unpins
    for (const f of frames) if (f.pinned && !f.pinned.contains(ev.target)) hide(f, true);
  }, true);

  /* ---- keynav: one tab stop per mark group; arrows step, Home/End jump, Enter pins, Escape hides ---- */
  function keynav(f, nodes, o) {
    o = o || {};
    nodes = nodes.filter(Boolean);
    if (!nodes.length) return;
    const seen = n => !n.closest('.ck-hidden');
    const next = (k, d) => { for (let j = k + d; j >= 0 && j < nodes.length; j += d) if (seen(nodes[j])) return j; return k; };
    let cur = Math.min(f.navIndex || 0, nodes.length - 1);
    nodes.forEach((n, k) => {
      n.setAttribute('data-ck-nav', '');
      n.setAttribute('tabindex', k === cur ? '0' : '-1');
      n.addEventListener('focus', () => {
        nodes.forEach(m => m.setAttribute('tabindex', '-1')); n.setAttribute('tabindex', '0');
        f.navIndex = k;
        if (o.onFocus) o.onFocus(n, k);
      });
      n.addEventListener('keydown', ev => {
        const K = ev.key;
        let j = null;
        if (o.step) j = o.step(k, K, nodes);
        if (j == null) {
          if (K === 'ArrowRight' || K === 'ArrowDown') j = next(k, 1);
          else if (K === 'ArrowLeft' || K === 'ArrowUp') j = next(k, -1);
          else if (K === 'Home') j = next(-1, 1);
          else if (K === 'End') j = next(nodes.length, -1);
        }
        if (K === 'Enter' || K === ' ') {
          ev.preventDefault();
          if (n._ckTip) { if (f.pinned === n) hide(f, true); else { hide(f, true); show(f, n, n._ckTip); f.pinned = n; } }
          if (o.onEnter) o.onEnter(n, k);
        } else if (j != null) { ev.preventDefault(); if (j !== k) { hide(f, true); nodes[j].focus(); } }
      });
    });
    f.navNodes = (f.navNodes || []).concat([nodes]);
    if (f.refocus != null && nodes[f.refocus]) { nodes[f.refocus].focus(); f.refocus = null; }
  }

  /* ---- legend (HTML, above the chart) and series toggling ---- */
  function swatch(it) {
    const s = el('svg', {viewBox: '0 0 18 10', width: 18, height: 10, 'aria-hidden': 'true'}), c = it.color || 'var(--c1)';
    const m = it.mark || 'box';
    const e = m === 'dot' ? el('circle', {cx: 9, cy: 5, r: 4}, s) : m === 'ring' ? el('circle', {cx: 9, cy: 5, r: 3.5}, s)
      : m === 'box' ? el('rect', {x: 3, y: 0, width: 12, height: 10, rx: 2}, s) : el('line', {x1: 1, x2: 17, y1: 5, y2: 5}, s);
    if (m === 'dot' || m === 'box') e.style.fill = c;
    else { e.style.fill = 'none'; e.style.stroke = c; e.style.strokeWidth = '2'; }
    if (m === 'dash') e.style.strokeDasharray = '4 3';
    return s;
  }
  function legend(hostEl, items, o) {
    o = o || {};
    const h = $(hostEl); h.textContent = ''; h.classList.add('ck-legend');
    const on = new Set(items.map(it => it.key)), btn = {};
    for (const it of items) {
      const b = document.createElement(o.toggle ? 'button' : 'span'); b.className = 'ck-li';
      b.append(swatch(it), document.createTextNode(it.label));
      if (o.toggle) {
        b.type = 'button'; b.setAttribute('aria-pressed', 'true');
        b.addEventListener('click', () => {
          const was = on.has(it.key);
          if (was && on.size === 1) return;  // keep at least one series
          if (was) on.delete(it.key); else on.add(it.key);
          b.setAttribute('aria-pressed', String(!was));
          if (o.onChange) o.onChange([...on]);
        });
      }
      btn[it.key] = b; h.appendChild(b);
    }
    return {el: h, on, set(keys) { on.clear(); keys.forEach(k => on.add(k)); for (const k in btn) if (o.toggle) btn[k].setAttribute('aria-pressed', String(on.has(k))); }};
  }
  function showSeries(f, keysOn) {
    f.seriesOn = [...keysOn];
    f.svg.querySelectorAll('[data-series]').forEach(n => n.classList.toggle('ck-hidden', !f.seriesOn.includes(n.getAttribute('data-series'))));
    for (const group of f.navNodes || []) {  // keep one reachable tab stop per group
      const vis = group.filter(n => !n.closest('.ck-hidden'));
      if (vis.length && !vis.some(n => n.getAttribute('tabindex') === '0')) { group.forEach(n => n.setAttribute('tabindex', '-1')); vis[0].setAttribute('tabindex', '0'); }
    }
    if (f.active && f.active.closest('.ck-hidden')) hide(f, true);
  }

  /* ---- controls ---- */
  function seg(hostEl, o) {
    const h = $(hostEl); h.textContent = ''; h.classList.add('ck-seg');
    const g = document.createElement('div'); g.setAttribute('role', 'radiogroup'); g.className = 'ck-seg-group';
    if (o.label) {
      const s = document.createElement('span'); s.className = 'ck-seg-label'; s.id = 'ck-l' + (++uid); s.textContent = o.label;
      h.appendChild(s); g.setAttribute('aria-labelledby', s.id);
    }
    const opts = o.options, api = {el: h, value: o.value == null ? opts[0][0] : o.value};
    const btns = opts.map(([v, t], k) => {
      const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'radio'); b.textContent = t;
      b.addEventListener('click', () => set(v, true));
      b.addEventListener('keydown', ev => {
        const d = ev.key === 'ArrowRight' || ev.key === 'ArrowDown' ? 1 : ev.key === 'ArrowLeft' || ev.key === 'ArrowUp' ? -1 : 0;
        if (!d) return;
        ev.preventDefault();
        const j = (k + d + opts.length) % opts.length;
        set(opts[j][0], true); btns[j].focus();
      });
      g.appendChild(b); return b;
    });
    function set(v, fire) {
      api.value = v;
      btns.forEach((b, k) => { const c = opts[k][0] === v; b.setAttribute('aria-checked', String(c)); b.tabIndex = c ? 0 : -1; });
      if (fire && o.onChange) o.onChange(v);
    }
    h.appendChild(g); set(api.value, false);
    api.set = v => set(v, true);
    return api;
  }
  function range(hostEl, o) {
    const h = $(hostEl); h.textContent = ''; h.classList.add('ck-range');
    const id = 'ck-r' + (++uid), stops = o.stops, f1 = o.fmt || (v => num(v));
    const lab = document.createElement('label'); lab.htmlFor = id; lab.textContent = o.label;
    const inp = document.createElement('input'); inp.type = 'range'; inp.id = id;
    const out = document.createElement('output'); out.setAttribute('for', id);
    if (stops) { inp.min = 0; inp.max = stops.length - 1; inp.step = 1; } else { inp.min = o.min; inp.max = o.max; inp.step = o.step == null ? 'any' : o.step; }
    const val = () => (stops ? stops[+inp.value] : +inp.value);
    const put = v => { inp.value = stops ? stops.reduce((b, s, k) => (Math.abs(s - v) < Math.abs(stops[b] - v) ? k : b), 0) : v; };
    const upd = fire => { const v = val(), s = f1(v); out.textContent = s; inp.setAttribute('aria-valuetext', s); if (fire && o.onInput) o.onInput(v); };
    inp.addEventListener('input', () => upd(true));
    h.append(lab, inp, out); put(o.value == null ? (stops ? stops[0] : o.min) : o.value); upd(false);
    return {el: h, input: inp, get value() { return val(); }, set(v) { put(v); upd(true); }};
  }
  function readout(hostEl) {
    const h = $(hostEl); h.classList.add('ck-readout'); h.setAttribute('aria-live', 'polite');
    h.set = html => { h.innerHTML = html; };
    return h;
  }
  function bus(name) {
    if (!buses[name]) { const fns = []; buses[name] = {value: undefined, on(fn) { fns.push(fn); }, emit(v, from) { this.value = v; fns.forEach(fn => fn(v, from)); }}; }
    return buses[name];
  }
  /* Card layout for a table under 600 px: each cell shows its column's header (CSS table.stack). */
  function stackTable(table) {
    const t = $(table), heads = [], hr = t.tHead && t.tHead.rows[t.tHead.rows.length - 1];
    if (hr) for (const c of hr.cells) for (let k = 0; k < (c.colSpan || 1); k++) heads.push(c.textContent.replace(/\s+/g, ' ').trim());
    for (const tb of t.tBodies) for (const r of tb.rows) { let k = 0; for (const c of r.cells) { if (heads[k]) c.setAttribute('data-label', heads[k]); k += c.colSpan || 1; } }
    t.classList.add('stack');
    return t;
  }

  /* ---- colour: series in fixed order (no cycling: past six series use --ref), a one-hue sequential ramp ---- */
  const SERIES = [1, 2, 3, 4, 5, 7];
  const color = i => (i >= 0 && i < SERIES.length ? `var(--c${SERIES[i]})` : 'var(--ref)');
  const clamp01 = p => Math.max(0, Math.min(1, +p || 0));
  const ramp = p => `color-mix(in srgb, var(--c1) ${(15 + 85 * clamp01(p)).toFixed(1)}%, var(--surface))`;
  function rgb(css) {  // resolve any CSS colour (tokens, color-mix) to linear-light luminance via a probe
    const s = document.createElement('span'); s.style.color = css; s.style.display = 'none';
    document.body.appendChild(s);
    const c = getComputedStyle(s).color; s.remove();
    const v = (c.match(/[\d.]+/g) || [0, 0, 0]).map(Number), unit = /^color\(/.test(c) ? 1 : 255;
    const lin1 = x => { x /= unit; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
    return 0.2126 * lin1(v[0]) + 0.7152 * lin1(v[1]) + 0.0722 * lin1(v[2]);
  }
  const contrast = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  /* Text colour for a ramp cell, chosen for the current theme: whichever of --ink and --page contrasts more. */
  function rampInk(p) {
    const bg = rgb(ramp(p));
    return contrast(bg, rgb('var(--ink)')) >= contrast(bg, rgb('var(--page)')) ? 'var(--ink)' : 'var(--page)';
  }
  const redrawAll = () => frames.forEach(f => f.redraw());  // rampInk depends on the theme
  if (window.MutationObserver) new MutationObserver(redrawAll).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
  const dark = mm('(prefers-color-scheme: dark)');
  if (dark.addEventListener) dark.addEventListener('change', redrawAll);

  return {el, txt, path, frame, lin, log, axes, inside, fmt, tip, keynav, legend, showSeries, seg, range, readout, bus,
    stackTable, reduced, ramp, rampInk, color, hide: f => hide(f, true)};
})();
