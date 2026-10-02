/* ================= links (1 Oct 2026): an address for what the stage shows =================
   The owner: "Make sure individual clicks like data->watts come with anchors so that I can share link to specific
   experiment." The #fragment follows the stage (history.replaceState, never a new entry): #flow=8-data-watts (a flow:
   its key 1-9, 0 or b, then its name; #flow=8 opens it too), &stage=3 while a flow is held at a stage (paused, or
   stepped while paused), #tour=3 on the tour's still slides, and with nothing playing the scale the camera rests on as
   ?at= names it, #at=shire%3A20/minion%3A20.1.3 (above the rack only the level shown: the easter egg's rule), written
   once the camera rests. The die, the first view, has none. A flow or the tour played at 2x (the speed button, S; 1
   Oct) adds &speed=2, and opens at 2x (a fragment without it keeps the page's speed: 1x when it opens). In a frame
   each new fragment is posted to the viewer as ss-hash (the only message), which spacesheep mirrors into the reader's
   address; the viewer forwards the outer fragment in, and a hashchange goes there as any move does. At load the
   fragment wins over ?flow=, ?tour=, ?at=; one that names nothing warns and is ignored (the address then says what is
   shown); any other (#facts) is left alone.
   Copy link copies spacesheep's address of the page (the frame's origin is no address to share), elsewhere this one's;
   where the frame forbids the clipboard, the link is shown selected. Hooks: lnkStart() at load, lnkSoon() in
   renderBar, pageArrived() in the core's arrived(). */
var LNK = {ready: false, last: '', t: 0, q: false, bad: false, sayT: 0, pop: null};   // (var: the hooks may run first)
const LNK_HOME = 'https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram';
const lnkSlug = k => FLOWS[k].title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
// (the viewer takes letters, digits and _ . = % & / - only)
const lnkEnc = s => encodeURIComponent(s).replace(/[!'()*~]/g, c => '%' + c.charCodeAt(0).toString(16).toUpperCase());
/* the shortest ?at= path that atPath takes back to P: from the die down, else from the deepest level of the ladder */
function lnkPath(P) {
  const tries = [], d = P.findIndex(e => e.id === 'die'), D0 = pathOf({level: 0});
  if (isWrap(P)) tries.push(WRAP);
  if (d >= 0 && d < D0.length && samePath(P.slice(0, d + 1), D0)) tries.push(d === P.length - 1 ? 'die' : pkeys(P.slice(d + 1)));
  for (let i = P.length - 1; i >= 0; i--) if (OUT_IDS.includes(P[i].id) && P.slice(0, i).every((e, j) => pk(e) === OUT_IDS[j])) tries.push(pkeys(P.slice(i)));
  tries.push(pkeys(P));
  return tries.find(s => { try { const Q = lnkPrefix(s); return !!Q && samePath(Q, P); } catch (_) { return false; } }) || null;
}
/* the path an ?at= string names, as atPath reads it, without atPath's check that each scale has its seat in the one
   above (the final check of 2 Oct 2026, as the memory levels' atPrefix since 11b6e45): lnkPath only asks which string
   names a place the camera is at, whose seats are there, and the check drew every scene on the way: after the loop's
   jump to the Planck length, about 100 ms at 1x and 350 ms at 4x, 400 ms after the arrival, so that an Up pressed then
   waited for it (a 350-370 ms first frame at 4x). A string read from the address still goes through atPath (lnkWhat). */
function lnkPrefix(s) {
  const els = pathFrom(s); if (!els.length || !els.every(e => NODES[e.id])) return null;
  if (els[0].id === WRAP) return els.length === 1 ? [{id: WRAP}] : null;
  const oi = OUT_IDS.indexOf(els[0].id);
  if (oi >= 0) return OUT_IDS.slice(0, oi).map(id => ({id})).concat(els);
  if (els[0].id === 'die') return OUT_IDS.map(id => ({id})).concat(els);
  return pathOf({level: 0}).concat(els);
}
/* (the first view has no anchor, unless the address's query asks for something else) */
function lnkAt(P) {
  if (samePath(P, pathOf({level: 0}))) return LNK.q ? 'at=die' : '';
  const s = lnkPath(P);
  return s ? 'at=' + s.split('/').map(lnkEnc).join('/') : '';
}
const lnkFlow = (k, i, held) => `flow=${KEYOF[k].toLowerCase()}-${lnkSlug(k)}` + (held ? '&stage=' + (i + 1) : '');
/* the replay's speed, after a flow's or the tour's anchor: at 2x only (s: a speed asked for, else the page's) */
const lnkRate = s => ((s || CLK.rate) === 2 ? '&speed=2' : '');
function lnkAnchor() {
  const tf = TOUR && STEPS[TOUR.i] ? STEPS[TOUR.i].flow : null;
  if (TOUR && !(tf && FL.k === tf)) return 'tour=' + (TOUR.i + 1) + lnkRate();
  if (FL.k) return lnkFlow(FL.k, FL.i, !FL.done && (FL.still || !CLK.on)) + lnkRate();
  return lnkAt(zNow().path);
}
/* a fragment's fields; null for one not of these forms */
function lnkFields(h) {
  const s = String(h || '').replace(/^#/, ''), o = {};
  if (!/^(flow|tour|at|stage)=/i.test(s)) return null;
  s.split('&').forEach(kv => {
    const i = kv.indexOf('='), k = (i < 0 ? kv : kv.slice(0, i)).toLowerCase();
    if (k in o) return;
    try { o[k] = decodeURIComponent(i < 0 ? '' : kv.slice(i + 1)); } catch (_) { o[k] = '\u0000'; }
  });
  return o;
}
/* what it asks for: {flow, i, held}, {tour}, {at}; {bad} when it names nothing; fix: a bad stage, the flow from its
   start, or a bad speed; speed: &speed=1 or 2 (any other warns and is dropped) */
function lnkAsk(o) {
  const r = lnkWhat(o);
  if (o.speed != null && !r.bad) {
    if (o.speed === '1' || o.speed === '2') r.speed = +o.speed;
    else { console.warn(`&speed=${o.speed}: the replay plays at 1× or 2×`); r.fix = true; }
  }
  return r;
}
function lnkWhat(o) {
  if (o.flow != null) {
    const v = String(o.flow).toLowerCase(), m = /^([0-9b])(?:-[a-z0-9-]*)?$/.exec(v);
    const k = m ? (m[1] === 'b' ? 'K' : ORDER['1234567890'.indexOf(m[1])]) : ORDER.split('').find(x => lnkSlug(x) === v);
    if (!k || !FLOWS[k]) return {bad: `#flow=${o.flow}: no such flow (1-9, 0 or b)`};
    if (o.stage == null) return {flow: k};
    const n = /^\d{1,2}$/.test(o.stage) ? +o.stage : 0;
    if (n >= 1 && n <= FLOWS[k].stages.length) return {flow: k, i: n - 1, held: true};
    console.warn(`#stage=${o.stage}: flow ${KEYOF[k]} has stages 1 to ${FLOWS[k].stages.length}; it plays from its start`);
    return {flow: k, fix: true};
  }
  if (o.tour != null) { const n = /^\d{1,2}$/.test(o.tour) ? +o.tour : 0; return n >= 1 && n <= STEPS.length ? {tour: n - 1} : {bad: `#tour=${o.tour}: the tour has steps 1 to ${STEPS.length}`}; }
  if (o.at != null) { let P = null; try { P = o.at ? atPath(o.at) : null; } catch (_) { P = null; } return P ? {at: P} : {bad: `#at=${o.at}: no such scale`}; }
  return {bad: '#stage= alone names no flow'};
}
const lnkOf = r => (r.flow ? lnkFlow(r.flow, r.i, r.held) + lnkRate(r.speed) : r.tour != null ? 'tour=' + (r.tour + 1) + lnkRate(r.speed) : lnkAt(r.at));
/* go there: at load at once (as the query does), on a hashchange by the reader's own kind of move */
function lnkGo(r, smooth) {
  if (r.speed) setRate(r.speed);
  if (r.flow && !r.held) { pickFlow(r.flow); return; }
  if (r.flow) { if (TOUR) endTour(); if (FOLLOW_AUTO) setFollow(true); startFlow(r.flow, r.i, {still: true}); return; }
  if (r.tour != null) { if (TOUR) tourGo(r.tour); else startTour(r.tour); return; }
  if (TOUR) endTour();
  if (FL.k) stopFlow();
  if (smooth) userNav(r.at);
  else goTo(r.at, {total: 0}).then(() => { scaleUI(true); showHere(); });
}
/* write the address (and tell the viewer); the camera's place waits until it rests, a flow's or the tour's does not */
function lnkWrite() {
  clearTimeout(LNK.t); LNK.t = 0;
  if (!LNK.ready) return;
  if (!FL.k && !TOUR && (ZW || UIP)) { LNK.t = setTimeout(lnkWrite, 300); return; }
  const a = lnkAnchor(); if (a === LNK.last) return;
  LNK.last = a;
  const h = a ? '#' + a : '';
  try { history.replaceState(history.state, '', location.pathname + location.search + h); } catch (_) { /* no history */ }
  if (window.parent !== window) { try { window.parent.postMessage({type: 'ss-hash', hash: h || '#'}, '*'); } catch (_) { /* no parent */ } }
}
function lnkSoon(ms) { if (!LNK || !LNK.ready) return; clearTimeout(LNK.t); LNK.t = setTimeout(lnkWrite, ms || 150); }
function pageArrived() { lnkSoon(400); }   // (a run of quick moves writes once)
/* at load, before the query's flags (true: the fragment was applied, and they are not); what the address asked for is
   what it says already, so nothing is written until the reader changes something */
function lnkStart() {
  try {
    const q = new URLSearchParams(location.search), o = lnkFields(location.hash);
    LNK.q = ['flow', 'tour', 'at'].some(n => q.get(n));
    let r = o ? lnkAsk(o) : null;
    if (r && r.bad) { console.warn(r.bad + '; the page opens as it would without it'); LNK.bad = true; r = null; }
    if (r && r.fix) LNK.bad = true;
    if (r) lnkGo(r, false);
    // (after the query's flow, tour or move has started)
    queueMicrotask(() => { LNK.ready = true; if (LNK.bad) { LNK.last = '\u0000'; lnkSoon(); } else LNK.last = lnkAnchor(); });
    return !!r;
  } catch (e) { console.warn('links: ' + e); LNK.ready = true; return false; }
}
window.addEventListener('hashchange', () => {
  if (!LNK.ready) return;
  const o = lnkFields(location.hash); if (!o) return;
  let r = lnkAsk(o), fix = !!r.fix;
  if (r.bad) { console.warn(r.bad + '; back to the first view'); r = {at: pathOf({level: 0})}; fix = true; }
  // the speed first: a fragment that changes only the speed changes nothing else; one without it keeps the page's, and
  // at 2x the address then says so
  if (r.speed) setRate(r.speed);
  else if (CLK.rate === 2 && (r.flow || r.tour != null)) fix = true;
  LNK.last = fix ? '\u0000' : lnkOf(r);   // (the address says it already, unless it named nothing)
  if (lnkOf(r) !== lnkAnchor()) lnkGo(r, true);
  if (fix) lnkSoon();
});
/* ---- Copy link ---- */
function lnkUrl(host) {
  const a = lnkAnchor(), h = a ? '#' + a : '';
  return /(^|\.)spacesheep\.(app|dev)$/.test(host == null ? location.hostname : host) ? LNK_HOME + h : location.href.split('#')[0] + h;
}
function lnkSay(t) {
  const b = $('btn-link'), s = $('lnk').querySelector('.lnk-say');
  s.textContent = t; b.textContent = t === 'Copied' ? t : 'Copy link'; b.classList.toggle('done', t === 'Copied');
  clearTimeout(LNK.sayT); LNK.sayT = setTimeout(() => { b.textContent = 'Copy link'; b.classList.remove('done'); s.textContent = ''; }, 2000);
}
/* the async clipboard where the frame allows it, else the copy command on a selected text */
function lnkClip(t, cb) {
  const exec = () => {
    const a = document.activeElement, ta = H('textarea', {readonly: '', 'aria-hidden': 'true', tabindex: '-1', class: 'lnk-ta'}, document.body);
    ta.value = t; ta.focus({preventScroll: true}); ta.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
    ta.remove(); if (a && a.focus) a.focus({preventScroll: true});
    return ok;
  };
  let allowed = true;
  try { const fp = document.permissionsPolicy || document.featurePolicy; if (fp && fp.allowsFeature) allowed = fp.allowsFeature('clipboard-write'); } catch (_) { /* no policy API */ }
  const cl = navigator.clipboard;
  if (!(allowed && cl && cl.writeText && window.isSecureContext)) { cb(exec()); return; }
  let p; try { p = cl.writeText(t); } catch (_) { p = Promise.reject(new Error('clipboard')); }
  Promise.resolve(p).then(() => cb(true), () => cb(exec()));
}
/* the clipboard forbidden: the link shown selected above the button */
function lnkPop(url) {
  let p = LNK.pop;
  if (!p) {
    p = LNK.pop = H('div', {class: 'lnk-pop', role: 'group', 'aria-label': 'The link'}, $('lnk'));
    H('label', {for: 'lnk-in'}, p);
    const i = H('input', {id: 'lnk-in', type: 'text', readonly: '', spellcheck: 'false', autocomplete: 'off'}, p);
    i.addEventListener('keydown', e => { if (e.key === 'Escape' || e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); lnkPopOff(true); } else if (e.key === 'Tab') lnkPopOff(false); });
    i.addEventListener('copy', () => setTimeout(() => { lnkPopOff(true); lnkSay('Copied'); }, 0));
    document.addEventListener('pointerdown', e => { if (!p.hidden && !(e.target.closest && e.target.closest('#lnk'))) lnkPopOff(false); }, true);
  }
  const mac = /Mac|iPhone|iPad|iPod/.test((navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '');
  const say = TOUCH ? 'Selected: press and hold it to copy' : `Copy with ${mac ? '⌘' : 'Ctrl'}-C`, i = p.querySelector('input');
  p.querySelector('label').textContent = say; $('lnk').querySelector('.lnk-say').textContent = say;
  i.value = url; p.hidden = false;
  i.focus({preventScroll: true}); i.select(); try { i.setSelectionRange(0, url.length); } catch (_) { /* selected */ }
}
function lnkPopOff(refocus) { const p = LNK.pop; if (!p || p.hidden) return; p.hidden = true; if (refocus) $('btn-link').focus({preventScroll: true}); }
$('btn-link').addEventListener('click', () => {
  lnkWrite();   // (the address bar too, if it waited for the camera)
  const url = lnkUrl();
  lnkPopOff(false);
  lnkClip(url, ok => { if (ok) lnkSay('Copied'); else lnkPop(url); });
});
/* for the page's tests */
window.__chipLinks = {anchor: () => lnkAnchor(), url: host => lnkUrl(host)};
