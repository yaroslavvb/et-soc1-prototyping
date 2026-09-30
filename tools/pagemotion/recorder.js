// injected before the page's scripts: one row per animation frame, and the long animation frames
window.__LOG = []; window.__LOAF = []; window.__WALL = [];
(() => {
  const ids = new WeakMap(); let nid = 0;
  const idOf = el => { if (!el) return 0; let v = ids.get(el); if (!v) { v = ++nid; ids.set(el, v); } return v; };
  function rec(now) {
    const out = [];
    document.querySelectorAll('#mem > g.lay').forEach(g => {
      if (g.style.display === 'none') return;
      out.push([+g.dataset.depth, idOf(g.firstElementChild), g.getAttribute('transform') || '', g.style.opacity === '' ? 1 : +g.style.opacity,
        g.style.getPropertyValue('--lab'), g.style.getPropertyValue('--ctx'), g.style.visibility || '']);
    });
    const sl = document.getElementById('st-live');
    let st = null; try { st = window.__memState && window.__memState(); } catch (_) {}
    window.__LOG.push([now, sl ? sl.textContent : '', out, st ? st.path.join('/') : '', st ? st.zooming : null]);
    const W = window.__WALL, key = (sl ? sl.textContent : '') + '|' + (st ? st.zooming : '');
    if (!W.length || W[W.length - 1][1] !== key) W.push([Date.now() / 1000, key]);
    requestAnimationFrame(rec);
  }
  requestAnimationFrame(rec);
  try {
    new PerformanceObserver(l => l.getEntries().forEach(e => window.__LOAF.push({start: e.startTime, dur: e.duration, block: e.blockingDuration,
      render: e.renderStart, style: e.styleAndLayoutStart, scripts: (e.scripts || []).map(s => ({inv: s.invoker, fn: s.sourceFunctionName, pos: s.sourceCharPosition, dur: s.duration, forced: s.forcedStyleAndLayoutDuration}))}))).observe({type: 'long-animation-frame', buffered: true});
  } catch (e) { window.__LOAF.push({err: String(e)}); }
})();
