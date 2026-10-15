// verify-n0.mjs: the audit's proposal for its section 3 (n0(+k) in the five parses), served patched: what a bad address
// does then, against today's page (each refused with a warning).
import { openPatched } from './pdp.mjs';
import { sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const N0P = [
  ["node('shire', {parse: k => ({sid: +k}),", "node('shire', {parse: k => ({sid: n0(+k)}),"],
  ["bnode('shire.neigh', {parse: k => ({nb: +k}),", "bnode('shire.neigh', {parse: k => ({nb: n0(+k)}),"],
  ["bnode('vpu.lane', {parse: k => ({lane: +k}),", "bnode('vpu.lane', {parse: k => ({lane: n0(+k)}),"],
  ["bnode('pcie.lane', {parse: k => ({lane: +k}),", "bnode('pcie.lane', {parse: k => ({lane: n0(+k)}),"],
  ["inode('l1d.block', {parse: k => ({block: +k}),", "inode('l1d.block', {parse: k => ({block: n0(+k)}),"],
];
const OFF = process.argv.includes('--off');
const CASES = ['die/shire:abc', 'die/shire:0/shire.neigh:x', 'die/shire:0/minion:0.0.0/l1d/l1d.block:x', 'die/shire:0/minion:0.0.0/vpu/vpu.lane:x',
  'die/pcie/pcie.phy/pcie.lane:x', 'die/shire:5', 'die/shire:0/shire.neigh:1'];
const b = await openPatched({w: 1440, h: 900, reduced: true}, OFF ? {} : {'chip.html': N0P});
for (const s of CASES) {
  await b.load('http://127.0.0.1:8918/chip.html#at=' + encodeURIComponent(s).replace(/%2F/g, '/'), 4000); await b.idle(10000); await sleep(300);
  const r = await b.ev(`(() => { const s = __chipState(); return {node: s.node, path: s.path.split('/').slice(-2).join('/'), panel: s.panel, hash: location.hash,
    crumbs: (document.getElementById('crumbs') || {}).innerText.replace(/\\n›\\n/g, ' › ').slice(-60)}; })()`);
  console.log(JSON.stringify({s, ...r}));
}
console.log('errors/warnings', JSON.stringify(b.errs.slice(0, 8)));
await b.close();
