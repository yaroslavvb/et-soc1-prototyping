"""near.py M.json id[,id] [gap_units]: pairs of texts in a scale whose advance boxes overlap horizontally and whose ink
boxes are closer than gap_units vertically (negative: they overlap), in the layer's units."""
import json, sys

d = json.load(open(sys.argv[1]))
ids = sys.argv[2].split(',')
gmax = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
for m in d['res']:
    if m['id'] not in ids:
        continue
    T = m['texts']
    print(f"== {m['id']} k={m['k']} texts={len(T)}")
    out = []
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            a, c = T[i], T[j]
            ox = min(a['x1'], c['x1']) - max(a['x0'], c['x0'])
            if ox <= 0.5:
                continue
            # vertical gap between ink boxes, in units (k: px per unit of the text)
            top, bot = (a, c) if a['iy0'] <= c['iy0'] else (c, a)
            gap = (bot['iy0'] - top['iy1']) / a['kt']
            if gap < gmax:
                out.append((gap, top['s'], bot['s'], top['fs'], bot['fs'], ox / a['kt'], top['uy'], bot['uy']))
    for g in sorted(out):
        print(f"   gap {g[0]:6.1f}u  {g[1][:44]!r} ({g[3]}px, y {g[6]}) over {g[2][:44]!r} ({g[4]}px, y {g[7]}); x overlap {g[5]:.0f}u")
