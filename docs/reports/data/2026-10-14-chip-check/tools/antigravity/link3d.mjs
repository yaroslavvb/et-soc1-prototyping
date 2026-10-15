// link3d.mjs: the chip page's "Explore this in 3D" link (topic 3, section 4) and the 3D page's way back: each back-link
// anchor the 3D page uses opens a scale; which panels carry the link, and where it points, for the scale and for a
// selected part (a click on it), on the four scales and on lib.xor, lib.sram6t and lib.wire.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const PAGE = 'http://127.0.0.1:8918/chip.html';
const PRE = 'beyond/universe/laniakea/localgroup/milkyway/stars/solar/moon/earth/us/california/bayarea/sf/bernal/st29/studio45/rack/host/card/package/die/';
const FMA = PRE + 'shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma';
const XOR = FMA + '/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor';
const SC = {
  'die.metal': PRE + 'die.metal', 'lib.finfet': XOR + '/lib.finfet', 'lib.fin': XOR + '/lib.finfet/lib.fin', 'lib.channel': XOR + '/lib.finfet/lib.fin/lib.channel',
  'lib.xor': XOR, 'lib.sram6t': FMA + '/lib.icg/lib.latch/lib.sram6t', 'lib.wire': PRE + 'shire:0/minion:0.0.0/vpu/lib.wire',
  'lib.inverter': XOR.replace(/lib\.xor$/, 'lib.xor/lib.inverter'), 'mesh.link.wire': PRE + 'shire:0/minion:0.0.0/mesh.link.wire',
};
const b = await open({w: 1440, h: 900, reduced: true});
await b.load(PAGE, '', 5000); await b.idle(20000); await sleep(2000);
const go = async (hash, wait = 500) => { await b.ev(`(() => { location.hash = ${JSON.stringify(hash)}; return 1; })()`); await sleep(wait); await b.idle(15000); await sleep(300); };
const pn = () => b.ev(`(() => { const p = document.getElementById('pn-body'); const a = p.querySelector('.pn-3d a'); return {title: (p.querySelector('.pn-title') || {}).textContent || '', kick: (p.querySelector('.pn-kick') || {}).textContent || '', link: a ? a.getAttribute('href').replace(/^.*#/, '#') : null}; })()`);
// 1. the 3D page's back-link anchors, as written in content.js
for (const a of ['die.metal', 'die.metal/lib.finfet', 'die.metal/lib.finfet/lib.fin', 'die.metal/lib.finfet/lib.fin/lib.channel']) {
  await go('#at=' + a);
  const s = await b.state();
  console.log(JSON.stringify({back: a, node: s.node, path: s.path.split('/').slice(-4).join('/'), panel: s.panel, hash: await b.ev('location.hash')}));
}
// 2. each scale: its own panel's link, then every part clicked: the part's panel title and its link
for (const [id, p] of Object.entries(SC)) {
  await go('#at=' + p.replace(/:/g, '%3A'));
  const s = await b.state();
  const own = await pn();
  const parts = await b.ev('window.__chipTest.parts()');
  const out = [];
  for (const q of parts) {
    if (q.x < 0 || q.y < 0 || q.x > 1440 || q.y > 900 || q.w < 1) continue;
    await b.click(q.x, q.y); await sleep(150);
    const s2 = await b.state();
    const r = await pn();
    out.push({part: (q.label || '').slice(0, 40), kid: q.kid, title: r.title.slice(0, 40), link: r.link});
    if (s2.path !== s.path) await go('#at=' + p.replace(/:/g, '%3A'));
  }
  console.log(JSON.stringify({scale: id, node: s.node, own: own.link, ownTitle: own.title}));
  out.forEach(o => console.log('   ', JSON.stringify(o)));
}
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
