/* ================= ladder-panel.js: the details panel's zoom rows and the gestures, shared (1 October 2026) =================
   From chip-diagram.script.js (30 September): the "You are here" entry and a part's zoom row, double-click, the
   touch screen's double-tap and its "Zoom in" pill, Enter, and the sources on hover. It uses the page's panel(),
   select(), showPart's helpers (showMLPart, showNodePart, showComp), ACTS, goNeighbour and flowOn. */
let DETOPEN = false;
try { DETOPEN = localStorage.getItem('et-chip-details') === '1'; } catch (_) { /* no storage */ }
const detBlock = html => `<details class="pn-det"${DETOPEN ? ' open' : ''}><summary>More detail and the sources</summary><div class="pn-det-b">${html}</div></details>`;
$('pn-body').addEventListener('toggle', e => {
  if (!e.target.matches || !e.target.matches('details.pn-det')) return;
  DETOPEN = e.target.open;
  try { localStorage.setItem('et-chip-details', DETOPEN ? '1' : '0'); } catch (_) { /* no storage */ }
}, true);
/* ---- the panel's zoom row (30 September: "when I double-click on a component, maybe it can display below it and
   give me extra options to zoom in"): directly under a part's lead, the scale its double-click enters, then what it is
   made of and the other zooms it offers; after a zoom, the scene's "You are here" entry with the zooms inside it ---- */
const capFirst = s => String(s).charAt(0).toUpperCase() + String(s).slice(1);
const dcHint = () => (TOUCH ? '(double-tap)' : '(double-click)');
const zbtn = (path, label, pri, hint) => `<button type="button" class="st-btn${pri ? ' pri' : ''}" data-act="go" data-to="${esc(pkeys(path))}">${esc(label)}${hint ? ` <span class="dc">${esc(hint)}</span>` : ''}</button>`;
const zrow = (lab, btns) => (btns.length ? `<div class="zr">${lab ? `<span class="zl">${esc(lab)}</span>` : ''}${btns.slice(0, 6).join('')}${btns.length > 6 ? `<details class="zmore"><summary>more…</summary><div class="zr">${btns.slice(6).join('')}</div></details>` : ''}</div>` : '');
function zoomRowPart(g, title) {
  const P = layerPath(g) || Z.path, k = kidOf(g), rows = [];
  if (g._go) rows.push(zrow('Go in:', [zbtn(g._go(), capFirst(String(g.getAttribute('aria-label') || '').replace(/[.:].*$/, '')), true, dcHint())]));
  else if (k && k.up) { const up = upPath(k.up); if (up) rows.push(zrow('', [zbtn(up, `Go to ${toOf({id: k.up})} (zooms out)`, true, dcHint())])); }
  else if (k) rows.push(zrow('Zoom in:', [zbtn(P.concat([k]), capFirst(toOf(k)), true, dcHint())]));
  const ex = g._opts ? g._opts(P) : OPTS[g._key] ? OPTS[g._key](g._ctx || {}, P, g) : [];
  const made = ex.filter(x => x.made), other = ex.filter(x => !x.made);
  if (other.length) rows.push(zrow(k ? 'Also:' : 'Zoom in:', other.map(x => zbtn(x.to, x.lab, !k && x === other[0]))));
  if (made.length) rows.push(zrow('Made of:', made.map(x => zbtn(x.to, x.lab, false))));
  const none = !k && !ex.length;
  // (since 1 Oct every part leads further in, since part 1b the host's and the card's too; what is left without a zoom
  // is the die's key, a legend)
  return `<div class="pn-zoom">${none ? `<p class="nz">${g._ext ? 'A key to the drawing, not a part of the chip: there is nothing inside it to zoom into.' : `No closer drawing of ${esc(title || 'this part')}.`}</p>` : rows.join('')}</div>`;
}
function zoomRowHere(P) {
  const ks = kidsOf(P), d = defKid(P), rows = [];
  if (ks.length) rows.push(zrow('Zoom into:', ks.map(k => zbtn(P.concat([k]), capFirst(toOf(k)), d && pk(k) === pk(d), d && pk(k) === pk(d) ? '(+)' : ''))));
  else if (atPlanck(P) && nextOf(P)) rows.push(zrow('', [zbtn(nextOf(P), '? (+)', false, '')]));
  else if (!isWrap(P)) rows.push('<p class="nz">The bottom of this branch: nothing smaller is drawn here.</p>');
  const U = upOf(P);
  if (U && isWrap(P)) rows.push(zrow('', [zbtn(U, '↑ Round the ring: the Planck length', false, '(Backspace)')]));
  else if (U) rows.push(zrow('', [zbtn(U, egg(U[U.length - 1]) || isTop(P) ? '↑ Zoom out: ?' : `↑ Zoom out to ${toOf(U[U.length - 1])}`, false, '(Backspace)')]));
  // (the top, the last level of the easter egg: the ring of sizes, off the loop since 1 Oct evening, by its link)
  if (isTop(P) && NODES[WRAP]) rows.push(zrow('', [zbtn([{id: WRAP}], '↻ The ring of sizes: every size at once', false, '')]));
  return `<div class="pn-zoom">${rows.join('')}</div>`;
}
function hereKick(P) { return `You are here · <span class="pn-sz">${sizeHtml(sizeOf(P[P.length - 1]))}</span>`; }
function flashZoomRow() {
  const z = $('pn-body').querySelector('.pn-zoom'); if (!z) return;
  z.classList.remove('flash'); void z.offsetWidth; z.classList.add('flash'); pnReveal(z);
}
/* a part's panel: its key's text (COMPS, LEADS) or, for the scales' parts, the tree's (showNodePart) */
function showPart(g) {
  if (g._mlp) showMLPart(g);
  else if (g._info) showNodePart(g);
  else if (COMPS[g._key]) showComp(g._key, g._ctx, {g});
  else if (typeof showNodePart === 'function') showNodePart(g);
}
/* where the camera rests: the scale's own panel with the zooms inside it */
function showHere() {
  const P = Z.path, el = P[P.length - 1], N0 = NODES[el.id];
  if (N0 && N0.here) N0.here(prm(el), P);
  else if (typeof showScene === 'function') showScene(P);
}
/* a double-click, a double-tap, Enter, or the pill: into the part's own scale; a part with none is selected, its panel
   brought into view at the zoom row, which says so and offers what it has */
function zoomInto(g) {
  const k = kidOf(g), P = layerPath(g) || Z.path;
  select(g); showPart(g); pillOff();
  if (g._go) { userNav(g._go()); return true; }
  if (!k) { flashZoomRow(); return false; }
  if (k.up) { const up = upPath(k.up); if (up) userNav(up); return !!up; }
  userNav(P.concat([k]));
  return true;
}
/* a click or a tap selects (since 30 September a click never moves the camera: with every part zoomable, a second
   click that zoomed would turn reading into flying) */
function activate(g) { select(g); showPart(g); scaleUI(); if (TOUCH) pillFor(g); }
let PILLT = 0;
/* ---- touch: our own double-tap (two taps on one part, the second touch within 400 ms of the first lift and 30 px of
   it, timed by the events' own time stamps: a long frame between the taps does not break it; #chip has touch-action:
   manipulation, so the browser's own double-tap zoom is off on the drawing while pinch-zoom of the page works), and
   the strip under the drawing with the selected part's "Zoom in" ---- */
let TAP = null, TOUCHUP = 0, TDOWN = 0;
svg.addEventListener('pointerdown', e => { if (e.pointerType === 'touch') TDOWN = e.timeStamp; });
svg.addEventListener('pointerup', e => {
  if (e.pointerType !== 'touch') return;
  TOUCHUP = performance.now();
  const g = e.target.closest && e.target.closest('.comp');
  if (!g || !svg.contains(g)) { TAP = null; return; }
  if (TAP && TAP.g === g && TDOWN - TAP.t < 400 && TDOWN >= TAP.t && Math.hypot(e.clientX - TAP.x, e.clientY - TAP.y) < 30) { TAP = null; zoomInto(g); return; }
  TAP = {g, t: e.timeStamp, x: e.clientX, y: e.clientY};
});
function pillFor(g) {
  const pl = $('zpill');
  if (!TOUCH || !g || ZW || !g.isConnected || $('stage').classList.contains('present')) { pillOff(); return; }
  const k = kidOf(g), t = $('pn-body').querySelector('.pn-title');
  $('zpill-in').hidden = !k; $('zpill-in').textContent = k && k.up ? 'Go out ▸' : 'Zoom in ▸';
  pl.querySelector('.zs-name').textContent = t ? t.textContent : '';
  pl.hidden = false;
}
function pillOff() { clearTimeout(PILLT); $('zpill').hidden = true; }
$('zpill-in').addEventListener('click', () => { if (SEL) zoomInto(SEL); });
$('zpill-det').addEventListener('click', () => { const p = $('panel'); if (p) p.scrollIntoView({behavior: REDUCED ? 'auto' : 'smooth', block: 'start'}); });
$('zpill').addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); pillOff(); if (SEL) SEL.focus({preventScroll: true}); } });
svg.addEventListener('click', e => {
  const l = e.target.closest && e.target.closest('.nbr'); if (l && svg.contains(l)) { pillOff(); goNeighbour(l._ctx); return; }
  const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) activate(g); else pillOff();
});
svg.addEventListener('dblclick', e => {
  if (performance.now() - TOUCHUP < 600) return;   // a double-tap was handled on its pointerup
  const g = e.target.closest && e.target.closest('.comp'); if (g && svg.contains(g)) zoomInto(g);
});
svg.addEventListener('keydown', e => {
  const l = e.target.closest && e.target.closest('.nbr');
  if (l && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); e.stopPropagation(); goNeighbour(l._ctx); return; }
  const g = e.target.closest && e.target.closest('.comp'); if (!g) return;
  if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); zoomInto(g); }
  else if (e.key === ' ' && !flowOn()) { e.preventDefault(); e.stopPropagation(); select(g); showPart(g); scaleUI(); }
});
/* a zoom started below the drawing (a phone's panel, under the stage): the drawing scrolls into view first, so that the
   move is seen (review of 1 Oct) */
function stageIntoView() {
  const r = $('svgwrap').getBoundingClientRect(), vis = Math.min(r.bottom, innerHeight) - Math.max(r.top, 0);
  if (vis < Math.min(r.height, innerHeight) * 0.6) $('upbar').scrollIntoView({block: 'start', behavior: REDUCED ? 'auto' : 'smooth'});
}
$('pn-body').addEventListener('click', e => {
  const b = e.target.closest('button[data-act]'); if (!b) return;
  // pressed from the keyboard: after the move, focus goes to the new panel's zoom row (it is rebuilt on arrival)
  if (b.dataset.act === 'go') { stageIntoView(); userNav(pathFrom(b.dataset.to), {pfocus: e.detail === 0}); }
  else if (b.dataset.act === 'state') stateToggle();
  else if (ACTS[b.dataset.act]) ACTS[b.dataset.act](b);
});

/* ================= sources on hover and focus ================= */
const tip = $('srctip');
function tipHtml(ids, srcOnly) {
  return ids.split(/\s+/).filter(Boolean).map(id => {
    const f = F[id]; if (!f) return LAZY.st === 'failed' ? `<div>${esc(id)}: source not loaded</div>` : LAZY.st === 'done' ? '' : `<div>${esc(id)}: loading the source…</div>`;
    const cd = cardsTxt(f);
    return `<div><b>${esc(KWORD[f.kind] || f.kind)}</b>${CAVW[f.caveat] ? ' · ' + CAVW[f.caveat] : ''} · ${esc(id)}${cd ? ' · ' + esc(cd) : ''}`
      + (srcOnly ? '' : `<span class="s">${esc(f.statement)}</span>`)
      + `<span class="s"><b>Source:</b> ${esc(f.source)}</span>${f.note ? `<span class="s"><b>Note:</b> ${esc(f.note)}</span>` : ''}</div>`;
  }).join('<hr>');
}
function showTip(elm) {
  const ids = elm.getAttribute('data-f'); if (!ids) return;
  tip.innerHTML = tipHtml(ids, elm.hasAttribute('data-src')); tip.style.display = 'block';
  const r = elm.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
  let x = Math.min(window.innerWidth - tw - 8, Math.max(8, r.left));
  let y = r.bottom + 6; if (y + th > window.innerHeight - 8) y = Math.max(8, r.top - th - 6);
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}
const hideTip = () => { tip.style.display = 'none'; };
/* while presenting, a pointer left on the stage shows no source tooltips (they would cover the die); the keyboard's
   focus still shows them. The pointer itself hides after 2 s without moving (CSS #stage.present.idle). */
const tipOK = t => !($('stage').classList.contains('present') && $('stage').contains(t));
let idleT = 0;
// (a page whose own handlers show the sources, the memory levels', sets PAGE_TIPS false: they find a fact of either)
if (typeof PAGE_TIPS === 'undefined' || PAGE_TIPS) {
  document.addEventListener('pointermove', () => {
    const st = $('stage'); st.classList.remove('idle'); clearTimeout(idleT);
    idleT = setTimeout(() => { if (st.classList.contains('present')) st.classList.add('idle'); }, 2000);
  }, {passive: true});
  document.addEventListener('pointerover', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t && tipOK(t)) showTip(t); else hideTip(); });
  document.addEventListener('focusin', e => { const t = e.target.closest && e.target.closest('[data-f]'); if (t) showTip(t); else hideTip(); });
  document.addEventListener('focusout', hideTip);
  window.addEventListener('scroll', hideTip, {passive: true});
}

