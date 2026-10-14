#!/usr/bin/env python3
"""cosmo_analyze.py <probe-out-dir> [--sheets]: what changes size or moves in the chip diagram's chrome, the labels'
on-screen sizes by class across the scales, and (with --sheets) contact sheets of the rest screenshots."""
import json, os, statistics, sys
from collections import defaultdict
d = sys.argv[1]
F = json.load(open(os.path.join(d, 'frames.json')))
R = json.load(open(os.path.join(d, 'rests.json')))
frames = F['frames']
print(f"{F['vp']}: {len(frames)} frames, {len(R)} rests; page errors: {F['errors'][:3]}")

# 1. type size, weight and colour of each chrome element: every distinct value, with the moves it showed in
print('\n== chrome type (distinct size / weight over all frames; the moves where the less common ones showed)')
for el in sorted({k for f in frames for k in f['e']}):
    vals = defaultdict(lambda: [0, set()])
    for f in frames:
        v = f['e'].get(el)
        if v: vals[(v[4], v[5])][0] += 1; vals[(v[4], v[5])][1].add(f['tag'])
    if len(vals) > 1:
        common = max(vals, key=lambda k: vals[k][0])
        print(f'  {el}: ' + '; '.join(f"{k[0]} w{k[1]} x{v[0]}" + ('' if k == common else f" (in {sorted(v[1])[:4]})") for k, v in sorted(vals.items(), key=lambda kv: -kv[1][0])))

# 2. boxes that should not move: their spread over all frames
print('\n== chrome boxes: spread of x, y, w, h over all frames (px), and the moves where they changed most')
for el in ['#svgwrap', '.st-bar', '.st-head', '#pmz', '#up', '.st-cap', '#zstrip', '#crumbs', '#scale-ro', '#cap', '#cap-sub', '#panel .pn-title']:
    rows = [(f['tag'], f['e'].get(el)) for f in frames if f['e'].get(el)]
    if not rows: continue
    sp = [max(r[1][i] for r in rows) - min(r[1][i] for r in rows) for i in range(4)]
    flag = '  <--' if (el in ('#svgwrap', '.st-bar', '.st-head', '#pmz') and max(sp) > 0.5) or (el in ('#up', '.st-cap', '#zstrip') and max(sp[1], sp[3]) > 0.5) else ''
    where = ''
    if max(sp) > 0.5:
        base = rows[0][1]; tags = defaultdict(float)
        for t, v in rows:
            dv = max(abs(v[i] - base[i]) for i in range(4))
            tags[t] = max(tags[t], dv)
        where = ' ' + ', '.join(f'{t}:{v:.0f}' for t, v in sorted(tags.items(), key=lambda kv: -kv[1])[:5])
    print(f"  {el:18s} x {sp[0]:6.1f} y {sp[1]:6.1f} w {sp[2]:6.1f} h {sp[3]:6.1f}{flag}{where}")

# 3. the labels' on-screen size by class, scale by scale
print('\n== drawing labels: median on-screen px by class, per rest (classes with 3+ labels)')
bycls = defaultdict(list)
for i, r in enumerate(R):
    for k, v in r['labels'].items():
        px = [x[0] for x in v]
        if len(px) >= 1: bycls[k].append((i, r['node'], statistics.median(px), min(px), max(px), len(px)))
for k, rows in sorted(bycls.items(), key=lambda kv: -len(kv[1])):
    meds = [x[2] for x in rows]
    if len(rows) < 2: continue
    lo, hi = min(meds), max(meds)
    print(f"  .{k}: {len(rows)} rests, median {statistics.median(meds):.1f}px, range {lo:.1f}-{hi:.1f}" + ('  <-- varies' if hi > 1.35 * lo else ''))
    if hi > 1.35 * lo:
        for x in sorted(rows, key=lambda x: x[2])[:3] + sorted(rows, key=lambda x: x[2])[-3:]:
            print(f"      rest {x[0]:3d} {x[1]:24s} median {x[2]:5.1f} (min {x[3]:.1f}, max {x[4]:.1f}, n {x[5]})")
print('\n== small labels: any under 10 px on screen, per rest')
for i, r in enumerate(R):
    small = [(k, px, t) for k, v in r['labels'].items() for px, t in v if px < 10]
    if small: print(f"  rest {i:3d} {r['node']:24s} {len(small)}: " + '; '.join(f'.{k} {px} "{t[:22]}"' for k, px, t in small[:4]))

if '--sheets' in sys.argv:
    from PIL import Image, ImageDraw
    pngs = sorted(p for p in os.listdir(d) if p.startswith('rest-') and p.endswith('.png'))
    per, cols = 12, 3
    for s in range(0, len(pngs), per):
        ims = [Image.open(os.path.join(d, p)) for p in pngs[s:s + per]]
        tw = 640; th = int(ims[0].height * tw / ims[0].width)
        sheet = Image.new('RGB', (cols * tw, ((len(ims) + cols - 1) // cols) * (th + 22)), 'white')
        dr = ImageDraw.Draw(sheet)
        for j, im in enumerate(ims):
            x, y = (j % cols) * tw, (j // cols) * (th + 22)
            sheet.paste(im.convert('RGB').resize((tw, th)), (x, y + 22))
            i = s + j; dr.text((x + 4, y + 4), f"{i}: {R[i]['tag']} | {R[i]['node']}", fill='black')
        out = os.path.join(d, f'sheet-{s // per:02d}.png'); sheet.save(out); print('sheet', out)
