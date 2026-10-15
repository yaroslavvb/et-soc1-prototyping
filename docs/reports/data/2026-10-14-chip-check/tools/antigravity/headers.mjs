// headers.mjs [W H] [--shots] [--font=FAMILY]: for each scale the audit names (topic 3, section 1), the frame's title
// against its tag pills, measured in the built page (SVG user units of the frame, and CSS px), at rest, reduced motion.
// --font forces the drawing's text into another family (a stand-in for a Mac's system-ui metrics).
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
import { writeFileSync, mkdirSync } from 'node:fs';
const args = process.argv.slice(2);
const W = +(args[0] || 1440), H = +(args[1] || 900);
const SHOTS = args.includes('--shots');
const FONT = (args.find(a => a.startsWith('--font=')) || '').slice(7);
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const OUT = '/home/yaroslavvb/claude/work/chip-check-1014/codex/topic3-work/out';
mkdirSync(OUT, {recursive: true});
const PRE = 'beyond/universe/laniakea/localgroup/milkyway/stars/solar/moon/earth/us/california/bayarea/sf/bernal/st29/studio45/rack/host/card/package/die/';
const FMA = PRE + 'shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma';
let T = {
  'lib.fifo': PRE + 'shire:0/shire.bank:0/lib.fifo',
  'lib.channel': FMA + '/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet/lib.fin/lib.channel',
  'die.metal': PRE + 'die.metal',
  'lib.counter': PRE + 'shire:0/minion:0.0.0/tensor/lib.counter',
  'vpu.lane.fma': FMA,
  'lib.lzd': FMA + '/lib.lzd',
  'lib.pll': PRE + 'io/lib.pll',
  'lib.round': FMA + '/lib.round',
  'pcie.lane': PRE + 'pcie/pcie.phy/pcie.lane:0',
};
if (ONLY) T = Object.fromEntries(Object.entries(T).filter(([k]) => ONLY.split(',').includes(k)));
const b = await open({w: W, h: H, dpr: 1, reduced: true, touch: W < 600});
await b.load('http://127.0.0.1:8918/chip.html', '', 5000);
await b.idle(20000); await sleep(2500);
if (FONT) await b.ev(`(() => { const s = document.createElement('style'); s.textContent = '#chip text{font-family:${FONT}!important}'; document.head.appendChild(s); return 1; })()`);
const go = async (hash, wait = 500) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(400); };
const res = [];
for (const [id, p] of Object.entries(T)) {
  await go('#at=' + p.replace(/:/g, '%3A'));
  const st = await b.state();
  const r = await b.ev(`(() => {
    const L = [...document.querySelectorAll('#chip g.lay')].filter(l => l.style.display !== 'none' && l.dataset.node === ${JSON.stringify(id)}).pop();
    if (!L) return {err: 'no layer'};
    const fr = L.querySelector('g.frm, g.ifr');
    if (!fr) return {err: 'no frame'};
    const tt = [...fr.querySelectorAll(':scope > text.t-big, :scope > text.i-t')];
    const pills = [...fr.querySelectorAll(':scope > g.tg')].map(g => { const rc = g.querySelector('rect'), tx = g.querySelector('text');
      const bb = tx.getBBox(); return {text: tx.textContent, x: +rc.getAttribute('x'), w: +rc.getAttribute('width'), y: +rc.getAttribute('y'), h: +rc.getAttribute('height'), textW: +bb.width.toFixed(1),
        sx: +rc.getBoundingClientRect().left.toFixed(1), sr: +rc.getBoundingClientRect().right.toFixed(1)}; });
    const titles = tt.map(t => { const bb = t.getBBox(), cr = t.getBoundingClientRect(); return {text: t.textContent, x: +bb.x.toFixed(1), right: +(bb.x + bb.width).toFixed(1), y: +bb.y.toFixed(1), bottom: +(bb.y + bb.height).toFixed(1),
      sl: +cr.left.toFixed(1), sr: +cr.right.toFixed(1), font: getComputedStyle(t).fontFamily.slice(0, 40), fs: getComputedStyle(t).fontSize}; });
    const box = fr.querySelector('rect'); const fb = {x: +box.getAttribute('x'), w: +box.getAttribute('width'), y: +box.getAttribute('y')};
    const minPill = pills.length ? Math.min(...pills.map(q => q.x)) : null;
    const t0 = titles[0];
    // the first title line against the leftmost pill (in the frame's own units), and whether they share a band
    const gap = minPill == null || !t0 ? null : +(minPill - t0.right).toFixed(1);
    const vband = !pills.length || !t0 ? null : (t0.y < pills[0].y + pills[0].h && t0.bottom > pills[0].y);
    const k = L.getScreenCTM ? L.getScreenCTM().a : null;
    return {frame: fb, titles, pills, gap, vband, scale: k};
  })()`);
  if (SHOTS) await b.shot(`${OUT}/hdr-${W}x${H}${FONT ? '-' + FONT.replace(/[^A-Za-z]/g, '') : ''}-${id}.png`);
  res.push({id, node: st.node, at: st.path.split('/').slice(-2).join('/'), ...r});
  console.log(JSON.stringify({id, node: st.node, gap: r.gap, vband: r.vband, title: r.titles && r.titles.map(t => [t.text, t.x, t.right, t.font, t.fs]), pills: r.pills && r.pills.map(q => [q.text, q.x, q.w])}));
}
writeFileSync(`${OUT}/headers-${W}x${H}${FONT ? '-' + FONT.replace(/[^A-Za-z]/g, '') : ''}.json`, JSON.stringify(res, null, 1));
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
