// parse2.mjs: positive controls for parse.mjs (valid instances reach their scale), and the warnings the page gives a
// bad address; also whether any built-in path can hand a parse a non-number (the panel's buttons, the crumbs).
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const PAGE = 'http://127.0.0.1:8918/chip.html';
const CASES = [
  'die/shire:5', 'die/shire:0/shire.neigh:1', 'die/pcie/pcie.phy/pcie.lane:3', 'die/shire:0/minion:0.0.0/vpu/vpu.lane:2',
  'die/shire:0/minion:0.0.0/l1d/l1d.block:1', 'die/shire:1e1', 'die/shire:abc', 'die/shire:0/shire.neigh:x', 'die/pcie/pcie.phy/pcie.lane:x',
  'die/shire:0/minion:0.0.0/vpu/vpu.lane:x', 'die/shire:0/minion:0.0.0/l1d/l1d.block:x', 'die/shire:0/shire.neigh:9', 'die/pcie/pcie.phy/pcie.lane:16',
];
const PRE = "window.__warns = []; (function () { const w = console.warn.bind(console); console.warn = (...a) => { try { window.__warns.push(a.map(String).join(' ')); } catch (_) {} w(...a); }; })();";
const rd = b => b.ev(`(() => { const s = __chipState(); return {node: s.node, path: s.path.split('/').slice(-3).join('/'), panel: s.panel,
  hash: location.hash, warns: (window.__warns || []).slice(-2), toast: [...document.querySelectorAll('.toast')].map(t => t.innerText).join(' | ').slice(0, 200)}; })()`);
const b = await open({w: 1440, h: 900, reduced: true, pre: PRE});
for (const s of CASES) {
  for (const how of ['?at=', '#at=']) {
    await b.load(PAGE, how + encodeURIComponent(s).replace(/%2F/g, '/'), 4000);
    await b.idle(10000); await sleep(300);
    const r = await rd(b);
    console.log(JSON.stringify({how, s, nan: JSON.stringify(r).includes('NaN'), ...r}));
  }
}
console.log('errors', JSON.stringify(b.errs.slice(0, 6)));
await b.close();
