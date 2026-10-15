// parse.mjs: the five scales whose parse is +k (topic 3, section 3), given a non-number in the address, by every way an
// address reaches the page (?at= at load, #at= at load, #at= set later), and by the page's own path code (atPath, nameOf).
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const PAGE = 'http://127.0.0.1:8918/chip.html';
const BAD = [
  'die/shire:abc', 'die/shire:', 'die/shire:1e1', 'die/shire:0x1f', 'die/shire:-1', 'die/shire:99', 'die/shire:1.5',
  'die/shire:0/shire.neigh:x', 'die/shire:0/minion:0.0.0/l1d/l1d.block:x', 'die/shire:0/minion:0.0.0/vpu/vpu.lane:x',
  'die/pcie/pcie.phy/pcie.lane:x', 'die/shire:0/minion:0.0.0/vpu/vpu.lane:', 'die/pcie/pcie.phy/pcie.lane:99',
  'shire:abc', 'shire:20/minion:20.x.3',
];
const rd = b => b.ev(`(() => { const s = __chipState(); return {node: s.node, path: s.path.split('/').slice(-3).join('/'), panel: s.panel, up: s.up,
  crumbs: (document.getElementById('crumbs') || {}).innerText, title: document.title, hash: location.hash}; })()`);
const b = await open({w: 1440, h: 900, reduced: true});
for (const s of BAD) {
  for (const how of ['?at=', '#at=']) {
    b.errs.length = 0;
    const warns = [];
    await b.load(PAGE, how + encodeURIComponent(s).replace(/%2F/g, '/'), 4000);
    await b.idle(10000); await sleep(300);
    const r = await rd(b);
    const nan = JSON.stringify(r).includes('NaN');
    console.log(JSON.stringify({how, s, nan, ...r, errs: b.errs.slice(0, 2)}));
  }
}
// later: a #at= set while the page runs, and the page's own functions given the bad paths directly
await b.load(PAGE, '', 4000); await b.idle(10000);
for (const s of BAD) {
  await b.ev(`(() => { location.hash = ${JSON.stringify('#at=' + s)}; return 1; })()`); await sleep(600); await b.idle(10000);
  const r = await rd(b);
  const direct = await b.ev(`(() => { try { const P = atPath(${JSON.stringify(s)}); const els = pathFrom(${JSON.stringify(s)}); return {atPath: P ? pkeys(P) : null, names: els.map(e => { try { return nameOf(e); } catch (x) { return 'ERR ' + x.message; } })}; } catch (e) { return {err: String(e)}; } })()`);
  console.log(JSON.stringify({how: 'hash-later', s, nan: JSON.stringify(r).includes('NaN'), ...r, direct}));
}
console.log('errors', JSON.stringify(b.errs.slice(0, 6)));
await b.close();
