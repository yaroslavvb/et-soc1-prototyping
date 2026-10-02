// take.mjs: how long the path camera's take-over of the stage takes at a few of the levels' places (the work done in
// the press's own frame before a hand-over move starts)
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion/cdp.mjs';
const b = await open({w: 1280, h: 800});
for (const h of ['#l3', '#l2', '#l1', '#l2/cell', '#dram']) {
  await b.load('http://127.0.0.1:8766/p2m/ml.html', h, 3500);
  const r = [];
  for (let i = 0; i < 3; i++) {
    r.push(await b.ev(`(() => { const t = performance.now(); MLH.test.take(); return +(performance.now() - t).toFixed(1); })()`));
    await b.ev('MLH.test.back()'); await sleep(600);
  }
  console.log(h, 'takeOver ms', JSON.stringify(r));
}
await b.close();
