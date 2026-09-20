const STATUS = {works_now: 'works now', needs_tooling: 'tooling', needs_fw_change: 'firmware', research_only: 'research', impossible_on_silicon: 'not on silicon'};
const CHECK = {confirmed: 'confirmed by two reviewers', disputed: 'reviewers corrected details; the row reflects them', unverified: 'not reviewed', refuted: 'refuted'};
const NS = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function txt(parent, x, y, s, cls, anchor) { const t = el('text', {x, y, class: cls || 'tick', 'text-anchor': anchor || 'start'}, parent); t.textContent = s; return t; }
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
const chip = s => `<span class="chip ${s}">${STATUS[s]}</span>`;
const verif = c => `<span class="verif ${c}" title="${CHECK[c]}">${c === 'confirmed' ? '✓' : c === 'disputed' ? '±' : '·'}</span>`;

/* ---------- granularity figure ---------- */
(function () {
  const rows = D.ladder.filter(r => r.sec);
  const W = 900, H = 60 + rows.length * 19, L = 250, R = 20, T = 28;
  const host = document.getElementById('gran'); host.innerHTML = '';
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img'}, host);
  const tip = document.createElement('div'); tip.className = 'tip'; host.appendChild(tip);
  const lx = v => Math.log10(v);
  const x = v => L + (lx(v) - lx(1e-9)) / (lx(10) - lx(1e-9)) * (W - L - R);
  const ticks = [[1e-9, '1 ns'], [1e-8, '10 ns'], [1e-7, '100 ns'], [1e-6, '1 µs'], [1e-5, '10 µs'], [1e-4, '100 µs'], [1e-3, '1 ms'], [1e-2, '10 ms'], [1e-1, '100 ms'], [1, '1 s'], [10, '10 s']];
  for (const [v, s] of ticks) { el('line', {x1: x(v), x2: x(v), y1: T - 6, y2: H - 22, class: 'grid-line'}, svg); txt(svg, x(v), H - 6, s, 'tick', 'middle'); }
  txt(svg, x(1.67e-9) + 4, T - 12, '1 cycle at 600 MHz', 'lab');
  el('line', {x1: x(1.67e-9), x2: x(1.67e-9), y1: T - 8, y2: H - 22, stroke: 'var(--axis)', 'stroke-width': 1, 'stroke-dasharray': '3 3'}, svg);
  rows.forEach((r, i) => {
    const y = T + 8 + i * 19;
    const g = el('g', {}, svg);
    txt(g, L - 8, y + 4, r.level, 'lab', 'end');
    el('line', {x1: L, x2: W - R, y1: y, y2: y, class: 'grid-line', opacity: 0.5}, g);
    const col = {works_now: 'var(--ok)', needs_tooling: 'var(--warn)', needs_fw_change: 'var(--c1)', research_only: 'var(--muted)', impossible_on_silicon: 'var(--bad)'}[r.status];
    el('circle', {cx: x(r.sec), cy: y, r: 6, fill: col, stroke: 'var(--surface)', 'stroke-width': 2}, g);
    el('rect', {x: 0, y: y - 9, width: W, height: 18, fill: 'transparent'}, g);
    const show = ev => { tip.innerHTML = `<b>${esc(r.level)}</b><br>${esc(r.gran)}<br>${chip(r.status)}`; tip.style.display = 'block';
      const b = host.getBoundingClientRect(); const p = ev.touches ? ev.touches[0] : ev;
      tip.style.left = Math.min(p.clientX - b.left + 12, b.width - 300) + 'px'; tip.style.top = (p.clientY - b.top + 12) + 'px'; };
    g.addEventListener('mousemove', show); g.addEventListener('touchstart', show, {passive: true});
    g.addEventListener('mouseleave', () => tip.style.display = 'none');
  });
  const leg = document.createElement('div'); leg.className = 'legend';
  leg.innerHTML = Object.keys(STATUS).map(k => chip(k)).join(' ') + ' <span class="small">· rows without a time scale (whole-program traces, one-shot dumps) are in the table only</span>';
  host.appendChild(leg);
})();

/* ---------- ladder table with filter ---------- */
(function () {
  let filter = 'all';
  const fbox = document.getElementById('filters');
  const opts = [['all', 'all rows'], ['works_now', 'works now'], ['needs_tooling', 'needs tooling'], ['needs_fw_change', 'needs firmware'], ['research_only', 'research'], ['impossible_on_silicon', 'not on silicon']];
  const t = document.getElementById('ladder');
  function render() {
    fbox.innerHTML = opts.map(([k, n]) => `<button type="button" aria-pressed="${filter === k}" data-k="${k}">${n}</button>`).join('');
    fbox.querySelectorAll('button').forEach(b => b.onclick = () => { filter = b.dataset.k; render(); });
    const rows = D.ladder.filter(r => filter === 'all' || r.status === filter);
    t.innerHTML = '<thead><tr><th>Instrument</th><th>What it shows</th><th>Finest granularity</th><th>How</th><th>Who</th><th>Status</th><th>Check</th></tr></thead><tbody>' +
      rows.map(r => `<tr><td class="lvl">${esc(r.level)}</td><td>${esc(r.what)}${r.note ? `<div class="small">${esc(r.note)}</div>` : ''}</td><td>${esc(r.gran)}</td><td>${esc(r.instrument)}</td><td>${esc(r.access)}</td><td>${chip(r.status)}</td><td>${verif(r.check)}</td></tr>`).join('') +
      '</tbody>';
  }
  render();
})();

/* ---------- next steps ---------- */
document.getElementById('steps').innerHTML = '<thead><tr><th>Step</th><th>What it unlocks</th><th>Effort</th><th>Needs</th></tr></thead><tbody>' +
  D.steps.map((s, i) => `<tr><td class="lvl">${i + 1}. ${esc(s.what)}</td><td>${esc(s.unlocks)}</td><td>${esc(s.effort)}</td><td>${esc(s.needs)}</td></tr>`).join('') + '</tbody>';

/* ---------- contrast ---------- */
document.getElementById('contrast').innerHTML = '<thead><tr><th>Topic</th><th>ET-SoC-1</th><th>A100/H100</th><th>Sources</th></tr></thead><tbody>' +
  D.contrast.map(c => `<tr><td class="lvl">${esc(c.topic)}</td><td>${esc(c.et)}</td><td>${esc(c.gpu)}</td><td class="small">${esc(c.src)}</td></tr>`).join('') + '</tbody>';
