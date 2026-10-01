// frames.mjs <page.html> <outdir> : a frame sequence of a slow touch pan on a 390-px phone (one screenshot per step),
// then the glide after the finger lifts; and a contact sheet
import {launch, sleep} from './cdp.mjs';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const [, , file, out] = process.argv;
fs.mkdirSync(out, {recursive: true});
const pg = await launch();
await pg.setViewport({w: 390, h: 844, dsf: 2, mobile: true, touch: true, cpu: 1});
await pg.goto('file://' + file); await sleep(1500);
await pg.eval(`(() => { if (typeof stopMotion === 'function') stopMotion(); S.v = clampV(${8 * 86400 + 6 * 3600}, ${10 * 86400}); redrawAll(true); document.getElementById('tl').scrollIntoView({block: 'start'}); })()`);
await sleep(500);
const r = await pg.eval(`(() => { const b = document.querySelector('#tl svg').getBoundingClientRect(); return {x: b.left, y: b.top, sy: scrollY, w: b.width, h: b.height, conc: layout(main.W).rows.conc.y}; })()`);
const clip = {x: 0, y: r.y + r.sy, width: 390, height: Math.min(r.h, 420)};
const x0 = r.x + r.w * 0.3, y0 = r.y + r.conc + 20;
const ev = (type, x) => pg.s('Input.dispatchTouchEvent', {type, touchPoints: type === 'touchEnd' ? [] : [{x, y: y0, id: 1, radiusX: 6, radiusY: 6, force: 1}]});
let n = 0; const shot = async () => pg.shot(`${out}/f${String(n++).padStart(2, '0')}.png`, clip);
await ev('touchStart', x0); await shot();
for (let i = 1; i <= 6; i++) { await ev('touchMove', x0 + i * 25); await sleep(16); await shot(); }
await ev('touchEnd'); for (let i = 0; i < 5; i++) { await sleep(120); await shot(); }
await pg.close();
execFileSync('python3', ['-c', `
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('${out}/f*.png')); ims = [Image.open(f).convert('RGB') for f in fs]
w, h = ims[0].size; sc = 0.5; cols = 4; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (int(w * sc) * cols, (int(h * sc) + 18) * rows), 'white'); d = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    X, Y = (i % cols) * int(w * sc), (i // cols) * (int(h * sc) + 18)
    sheet.paste(im.resize((int(w * sc), int(h * sc))), (X, Y + 18)); d.text((X + 4, Y + 3), ('finger down' if i == 0 else f'move {i}' if i <= 6 else f'after lift +{(i - 6) * 120} ms'), fill='black')
sheet.save('${out}/sheet.png')
`]);
console.log('frames', n);
