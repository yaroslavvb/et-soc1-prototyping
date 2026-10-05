// prompts.mjs <page.html> <outdir> : the owner's words on the session timeline (5 Oct 2026). On a desktop: hovering a
// message's mark shows the start of its words; a click opens the prompt reader; → steps to the next message; Escape
// closes it; §3's "read it whole" opens it too. On a phone: a tap pins the details with the words, a second tap opens the
// reader. Prints one line per check and writes screenshots; exits 1 if a check fails.
import {launch, sleep} from './cdp.mjs';
import fs from 'node:fs';
const [, , file, outdir] = process.argv;
fs.mkdirSync(outdir, {recursive: true});
const OCT1 = 12 * 86400;   // the page's seconds since Sat 19 Sep 00:00 PDT
const A = OCT1 + 5 * 3600, B = OCT1 + 18 * 3600;   // 1 Oct, 05:00-18:00: the chip diagram's requests
let bad = 0;
const esc = pg => pg.s('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27})
  .then(() => pg.s('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27}));
const check = (name, ok, extra = '') => { console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${extra ? '  ' + extra : ''}`); if (!ok) bad++; };

async function at(pg) {   // the timeline at [A, B], at the top of the viewport; the first readable mark in view
  await pg.eval(`(() => { if (typeof stopMotion === 'function') stopMotion(); cancelAnimationFrame(anim); animating = false;
    S.v = clampV(${A}, ${B}); redrawAll(true); document.getElementById('tl').scrollIntoView({block: 'start'}); })()`);
  await sleep(500);
  return pg.eval(`(() => { const n = [...document.querySelectorAll('#tl svg [data-go]')].map(g => g.getBoundingClientRect())
    .filter(r => r.width && r.left > 60 && r.right < innerWidth - 10 && r.top > 0 && r.bottom < innerHeight)[0];
    return n ? {x: n.left + n.width / 2, y: n.top + n.height / 2} : null; })()`);
}
const TIP = `(() => { const t = main.tip; return {shown: t.style.display === 'block', words: !!t.querySelector('.tip-prompt'),
  text: t.textContent.slice(0, 90), pinned: !!main.pinned}; })()`;
const PV = `(() => { const d = document.getElementById('pv'); return {open: d.open, sum: document.getElementById('pv-sum').textContent,
  pos: document.getElementById('pv-pos').textContent, chars: document.getElementById('pv-text').textContent.length}; })()`;

// desktop
{
  const pg = await launch();
  await pg.setViewport({w: 1280, h: 800});
  await pg.goto('file://' + file);
  await sleep(1500);
  const m = await at(pg);
  check('desktop: a readable mark in view', !!m, JSON.stringify(m));
  if (m) {
    await pg.mouse('mouseMoved', m.x, m.y); await sleep(300);
    const t = await pg.eval(TIP);
    check('desktop: hover shows the words', t.shown && t.words, t.text);
    const sy = await pg.eval('scrollY');   // a clip is in page coordinates
    await pg.shot(`${outdir}/desktop-hover.png`, {x: Math.max(0, m.x - 120), y: Math.max(0, sy + m.y - 40), width: 640, height: 380});
    await pg.mouse('mousePressed', m.x, m.y, 1); await pg.mouse('mouseReleased', m.x, m.y); await sleep(400);
    const p = await pg.eval(PV);
    check('desktop: a click opens the reader', p.open && p.chars > 0, `${p.pos}: ${p.sum} (${p.chars} chars)`);
    await pg.shot(`${outdir}/desktop-reader.png`);
    await pg.key('ArrowRight', 'ArrowRight'); await sleep(200);
    const q = await pg.eval(PV);
    check('desktop: → steps to the next message', q.open && q.pos !== p.pos, `${p.pos} -> ${q.pos}`);
    await esc(pg); await sleep(200);
    check('desktop: Escape closes it', !(await pg.eval(PV)).open);
  }
  const b = await pg.eval(`(() => { const b = document.querySelector('#asked-list button.ask-read'); b.scrollIntoView({block: 'center'});
    const r = b.getBoundingClientRect(); return {x: r.left + r.width / 2, y: r.top + r.height / 2}; })()`);
  await sleep(300);
  await pg.mouse('mousePressed', b.x, b.y, 1); await pg.mouse('mouseReleased', b.x, b.y); await sleep(300);
  const r = await pg.eval(PV);
  check('desktop: "read it whole" in §3 opens the reader', r.open && r.chars > 0, `${r.pos}: ${r.sum}`);
  await esc(pg); await sleep(200);
  const nb = await pg.eval(`document.querySelectorAll('#asked-nb .ask-read').length`);
  check('desktop: the other sessions\' messages have their words in §3', nb > 50, `${nb} buttons`);
  check('desktop: no script errors', !pg.logs.some(l => l.type === 'exception'), JSON.stringify(pg.logs.slice(0, 3)));
  await pg.close();
}

// phone
{
  const pg = await launch();
  await pg.setViewport({w: 390, h: 844, dsf: 3, mobile: true, touch: true});
  await pg.goto('file://' + file);
  await sleep(1500);
  const m = await at(pg);
  check('phone: a readable mark in view', !!m, JSON.stringify(m));
  if (m) {
    await pg.tap(m.x, m.y); await sleep(400);
    const t = await pg.eval(TIP);
    check('phone: a tap pins the details with the words', t.shown && t.words && t.pinned, t.text);
    await pg.shot(`${outdir}/phone-tap.png`);
    await pg.tap(m.x, m.y); await sleep(400);
    const p = await pg.eval(PV);
    check('phone: a second tap opens the reader', p.open && p.chars > 0, `${p.pos}: ${p.sum}`);
    await pg.shot(`${outdir}/phone-reader.png`);
  }
  check('phone: no script errors', !pg.logs.some(l => l.type === 'exception'), JSON.stringify(pg.logs.slice(0, 3)));
  await pg.close();
}
process.exit(bad ? 1 : 0);
