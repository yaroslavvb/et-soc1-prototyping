// ml_access_test.mjs PAGE [--dive] [--par=4] : every access of the memory levels plays to its end (the gate of the
// 30 Sep page-motion work, results/correctness.txt there, kept for the shared ladder of 1 Oct 2026: the levels' own
// camera still plays them, the ladder's Up bar beside it). Each access is loaded as #<level>/<access> (with ?dive=on,
// --dive: the camera goes down to the circuit of each step that has one) and played until it says done; then the
// camera is sent out to the package and back with the Up bar, and Play is pressed: the access plays again from its
// level. PASS or FAIL per access; the exit code is the number of failures.
import { open, sleep } from './cdp.mjs';
const args = process.argv.slice(2), PAGE = args.find(a => !a.startsWith('--')), DIVE = args.includes('--dive');
const PAR = +((args.find(a => a.startsWith('--par=')) || '').slice(6) || 4);
let fails = 0;
const ok = (c, what, extra) => { if (!c) fails++; console.log((c ? 'PASS ' : 'FAIL ') + what + (extra ? '  ' + String(extra).slice(0, 300) : '')); };
const b0 = await open({w: 1280, h: 800}); await b0.load(PAGE, '', 2500);
const list = await b0.ev("MLB.LEVELS.flatMap(lv => MLB.SCENES[lv].accOrder.map(a => lv + '/' + a[0]))");
await b0.close();
async function one(acc) {
  const b = await open({w: 1280, h: 800});
  try {
    await b.load(PAGE, (DIVE ? '?dive=on' : '') + '#' + acc, 2500);
    const t0 = Date.now(); let s = null;
    while (Date.now() - t0 < 240000) { await sleep(500); s = await b.ev('(() => { const s = __memState(); return {done: s.done, acc: s.acc, step: s.step}; })()'); if (s.done) break; }
    const t1 = Date.now() - t0;
    // out to the package with the ladder, then Play: the camera comes back to the level and the access plays again
    const lv = acc.split('/')[0];
    for (let i = 0; i < 8; i++) { const st = await b.ev('__memState().ladder'); if (st.node === 'package') break; await b.ev("document.getElementById('up').click()"); await sleep(1600); }
    const out = await b.ev('__memState().ladder');
    await b.ev("document.getElementById('btn-play').click()");
    let back = null;
    for (let i = 0; i < 40; i++) { await sleep(500); back = await b.ev('(() => { const s = __memState(); return {lv: s.lv, on: s.ladder.on, acc: s.acc, clock: s.clockOn}; })()'); if (!back.on && back.acc) break; }
    // (going out of the L1 or the L2 passes their tabs on to the chip level outside, whose access Play then plays)
    ok(!!(s && s.done) && out.node === 'package' && back && !back.on && (back.lv === lv || ['l3', 'scp', 'dram'].includes(back.lv)) && back.acc && !b.errs.length,
      `${acc}${DIVE ? ' (Dive)' : ''}: plays to its end (${(t1 / 1000).toFixed(0)} s), out to the package and back to play again`, `done=${s && s.done} out=${out.node} back=${JSON.stringify(back)} errors=${b.errs.join(' | ') || 'none'}`);
  } catch (e) { ok(false, acc + ' ran', String(e)); }
  await b.close();
}
const q = list.slice();
await Promise.all(Array.from({length: PAR}, async () => { while (q.length) await one(q.shift()); }));
console.log(`${list.length} accesses, ${fails} failed`);
process.exit(fails);
