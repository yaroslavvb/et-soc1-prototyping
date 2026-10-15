// blocks.mjs [W H] : for each block scene (blockScene), the boxes' titles against their full names (a title cut to its
// first wrapped line), the blurbs' lines and whether they end in "…", and the "made of" pills drawn against the list the
// scene computes (a pill past the card's width is dropped). Read only.
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const [W = '1440', H = '900', BASE = 'http://127.0.0.1:8918/chip.html'] = process.argv.slice(2);
const b = await open({w: +W, h: +H, dpr: 1, reduced: true, touch: +W < 600});
await b.load(BASE, '', 6000);
await b.idle(20000);
const graph = await b.ev('window.__chipTest.graph()');
const IDS = ['shire.meshstop', 'shire.meshstop.router', 'shire.uc', 'shire.xbar', 'shire.neigh', 'core', 'vpu', 'vpu.lane', 'tensor', 'pcie', 'pcie.phy', 'io'];
let truncTotal = 0, boxes = 0;
for (const id of IDS) {
  const g = graph.find(x => x.id === id);
  if (!g) { console.log('no path', id); continue; }
  await b.ev(`(() => { location.hash = ${JSON.stringify('#at=' + g.path.replace(/:/g, '%3A'))}; return 1; })()`);
  await sleep(400); await b.idle(15000); await sleep(300);
  const r = await b.ev(`(() => {
    const st = window.__chipState(), svg = document.getElementById('chip');
    const L = [...svg.querySelectorAll(':scope > g.lay')].find(l => l._key === st.path);
    const ISC = D.scales || {}, NN = new Set(window.__chipTest.nodes()), NODES = new Proxy({}, {get: (o, k) => NN.has(k)}); const id = ${JSON.stringify(id)}, s0 = ISC[id] || {};
    const INSTID = {'pcie.phy': 'pcie.lane', vpu: 'vpu.lane', 'shire.neigh': 'minion'}; const kids = (s0.kids || []).filter(k => ISC[k] && ISC[k].name && k !== INSTID[id]);
    const see = [...new Set([].concat(s0.see || [], ...kids.map(k => (ISC[k] || {}).see || [])))].filter(x => NODES[x]);
    const comps = [...L.querySelectorAll(':scope > g.comp')];
    const out = {path: st.path, kids: [], see, pills: [], seeNames: see.map(x => (ISC[x] || {}).short || x)};
    comps.forEach(c => {
      const k = c.getAttribute('data-comp') || c._key; const ts = [...c.querySelectorAll(':scope > text')].map(t => t.textContent);
      if (kids.includes(k)) out.kids.push({k, title: ts[0], name: String((ISC[k] || {}).name || k), short: (ISC[k] || {}).short || '', lines: ts.slice(1), blurb: (ISC[k] || {}).blurb || ''});
      if (see.includes(k)) out.pills.push(k);
    });
    return out; })()`);
  console.log(`\n== ${id}: ${r.kids.length} boxes; made of: ${r.see.length} listed, ${r.pills.length} drawn` + (r.pills.length < r.see.length ? ` (dropped: ${r.see.filter(x => !r.pills.includes(x)).join(', ')})` : ''));
  r.kids.forEach(k => {
    boxes++;
    const nm = k.name.replace(/\s*\(.*$/, '');
    const cut = k.title !== nm && k.title !== k.short;
    const ell = k.lines.length && /…$/.test(k.lines[k.lines.length - 1]);
    if (ell) truncTotal++;
    console.log(`  ${cut ? 'TITLE CUT ' : ''}${ell ? '… ' : '  '}[${k.k}] "${k.title}"${cut ? ` (name "${nm}", short "${k.short}")` : ''} :: ${k.lines.join(' / ')}`);
  });
}
console.log(`\nboxes ${boxes}, blurbs ending in an ellipsis ${truncTotal}`);
console.log('errors', JSON.stringify(b.errs.slice(0, 5)));
await b.close();
