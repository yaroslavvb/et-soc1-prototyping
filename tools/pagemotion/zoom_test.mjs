// node zoom_test.mjs PAGE [--phone] [--only T4,T1] : the chip diagram's zoom and navigation tests (DESIGN §6.2), driven
// with real input events over the DevTools protocol (cdp.mjs). Desktop 1280 x 800 with a mouse; --phone: 390 x 844,
// touch emulation, DPR 3. Each test prints PASS or FAIL lines; the exit code is the number of failures.
import { open, sleep } from './cdp.mjs';
const args = process.argv.slice(2), PAGE = args.find(a => !a.startsWith('--')), PHONE = args.includes('--phone');
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7).split(',').filter(Boolean);
let fails = 0, passes = 0;
const ok = (c, what, extra) => { if (c) passes++; else fails++; console.log(`${c ? 'PASS' : 'FAIL'} ${what}${extra ? '  ' + extra : ''}`); return c; };
const T = {};

/* T4: a shire's edge labels are links to its neighbours: click (tap), Tab+Enter; the die edge is no link; focus comes
   back to the link toward the shire left */
T.T4 = async b => {
  const cellOf = `(() => { const s = window.__chipState(); return s; })()`;
  for (const sid of [20, 0, 7, 24, 31]) {
    await b.load(PAGE, `?at=shire:${sid}`, 1200);
    // until ?at= exists, zoom there with the page's own keyboard path: select the tile and press Enter
    let s = await b.state();
    if (s.level !== 1 || s.sid !== sid) {
      await b.ev(`(() => { const g = [...document.querySelectorAll('#chip .comp[data-comp="cshire"]')].find(g => g.getAttribute('aria-label').startsWith('Shire ${sid},')); g.focus(); })()`);
      await b.key('Enter'); await b.idle();
      s = await b.state();
    }
    if (!ok(s.level === 1 && s.sid === sid, `T4 shire ${sid} shown`, JSON.stringify([s.level, s.sid]))) continue;
    const links = await b.ev(`[...document.querySelectorAll('#chip .lay[data-level="1"] .nbr')].filter(g => g.getClientRects().length).map(g => ({l: g.getAttribute('aria-label'), role: g.getAttribute('role'), tab: g.tabIndex}))`);
    const edges = await b.ev(`[...document.querySelectorAll('#chip .lay[data-level="1"] text')].filter(t => /die edge/.test(t.textContent)).map(t => ({focusable: t.closest('[tabindex]') ? 1 : 0}))`);
    ok(links.every(l => l.role === 'link' && l.tab === 0), `T4 shire ${sid}: ${links.length} links, role link, focusable`, links.map(l => l.l).join(' | '));
    ok(edges.every(e => !e.focusable), `T4 shire ${sid}: ${edges.length} die-edge labels not focusable`);
    for (let i = 0; i < links.length; i++) {
      const lab = links[i].l, m = /Go to (shire (\d+)|.+), (north|south|east|west)/.exec(lab), tgt = m && m[2] != null ? +m[2] : null;
      for (const how of b.touch ? ['tap'] : ['click', 'enter']) {
        // back to the shire (cut) before each try
        await b.load(PAGE, `?at=shire:${sid}`, 1200);
        s = await b.state();
        if (s.level !== 1 || s.sid !== sid) { await b.ev(`(() => { const g = [...document.querySelectorAll('#chip .comp[data-comp="cshire"]')].find(g => g.getAttribute('aria-label').startsWith('Shire ${sid},')); g.focus(); })()`); await b.key('Enter'); await b.idle(); }
        const sel = `js:[...document.querySelectorAll('#chip .lay[data-level="1"] .nbr')].find(g => g.getAttribute('aria-label') === ${JSON.stringify(lab)})`;
        const bx = await b.box(sel);
        if (how === 'click') await b.click(bx.x, bx.y);
        else if (how === 'tap') await b.tap(bx.x, bx.y);
        else { await b.ev(`(${sel.slice(3)}).focus()`); await b.key('Enter'); }
        await sleep(100); await b.idle(9000);
        s = await b.state();
        if (tgt != null) {
          const back = await b.ev(`(() => { const a = document.activeElement; return a && a.classList && a.classList.contains('nbr') ? a.getAttribute('aria-label') : (a ? a.tagName + '.' + (a.getAttribute('class') || '') : null); })()`);
          ok(s.level === 1 && s.sid === tgt, `T4 shire ${sid} → ${lab} by ${how}`, JSON.stringify([s.level, s.sid]));
          if (how === 'enter') ok(new RegExp(`Go to shire ${sid},`).test(back || ''), `T4 shire ${sid} → ${tgt}: focus on the link back`, back);
        } else {
          const selName = await b.ev(`(() => { const g = document.querySelector('#chip .comp.sel'); return g ? g.getAttribute('aria-label') : null; })()`);
          const title = await b.ev(`document.querySelector('#pn-body .pn-title').textContent`);
          ok(s.level === 0 && !!selName, `T4 shire ${sid} → ${lab} by ${how}: die, cell selected`, `${selName} | panel: ${title}`);
        }
      }
    }
  }
};

const b = await open(PHONE ? {w: 390, h: 844, dpr: 3, touch: true} : {w: 1280, h: 800, dpr: 1});
try {
  for (const [k, fn] of Object.entries(T)) {
    if (ONLY.length && !ONLY.includes(k)) continue;
    console.log(`== ${k} ${PHONE ? '(phone)' : '(desktop)'}`);
    try { await fn(b); } catch (e) { ok(false, `${k} threw`, e.message); }
  }
  ok(!b.errs.length, 'no console errors', b.errs.slice(0, 6).join(' || '));
} finally { await b.close(); }
console.log(`${passes} passed, ${fails} failed`);
process.exitCode = fails;
