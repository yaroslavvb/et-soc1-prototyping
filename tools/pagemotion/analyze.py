"""analyze.py RUN.json: frame timing and camera motion of a recorded access."""
import json, sys, math, re, collections
R = json.load(open(sys.argv[1]))
log, T, loaf = R['log'], R['T'], R['loaf']
VERB = '-v' in sys.argv
def mat(s):
    if not s: return (1.0, 0.0, 0.0)
    m = re.match(r'matrix\(([^,]+),0,0,([^,]+),([^,]+),([^)]+)\)', s)
    return (float(m.group(1)), float(m.group(3)), float(m.group(4)))
# svg units -> css px: the viewBox 1300 x 792 in the svg's box, meet
sx, sy, sw, sh = R['svg']; k_px = min(sw / 1300, sh / 792)
FR = (-172, -74, 1264, 774)
pts = [(FR[0], FR[1]), (FR[0] + FR[2], FR[1]), (FR[0], FR[1] + FR[3]), (FR[0] + FR[2], FR[1] + FR[3]), (FR[0] + FR[2] / 2, FR[1] + FR[3] / 2)]
rows = []
for i in range(1, len(log)):
    t0, s0, L0, p0, z0 = log[i - 1]; t1, s1, L1, p1, z1 = log[i]
    a = {(l[0], l[1]): l for l in L0}; b = {(l[0], l[1]): l for l in L1}
    common = [k for k in b if k in a]
    mv = None
    if common:
        # the motion of the screen: M1 o M0^-1 for a layer shown in both frames (the layers move together)
        k = max(common, key=lambda q: b[q][3])
        (k0, x0, y0), (k1, x1, y1) = mat(a[k][2]), mat(b[k][2])
        s = k1 / k0
        # screen point p (svg units) was at layer point (p - t0)/k0, now at k1 * that + t1
        mv = max(math.hypot(k1 * (px - x0) / k0 + x1 - px, k1 * (py - y0) / k0 + y1 - py) for px, py in pts) * k_px
    op = max((abs(b[q][3] - a[q][3]) for q in common), default=0)
    rows.append(dict(i=i, t=t1, dt=t1 - t0, step=s1, zoom=z1, mv=mv, nl=len(L1), dop=op, path=p1, lays=L1))
# frame timing
dts = [r['dt'] for r in rows]
zd = [r['dt'] for r in rows if r['zoom']]
def stats(v):
    v = sorted(v); n = len(v)
    return f"n={n} median={v[n//2]:.1f} p95={v[int(n*.95)]:.1f} max={v[-1]:.1f} late(>25ms)={sum(x > 25 for x in v)} ({100*sum(x > 25 for x in v)/max(1,n):.1f}%)"
print('all frames :', stats(dts))
print('zoom frames:', stats(zd) if zd else '-')
# camera moves: runs of zoom frames
moves = []; cur = None
for r in rows:
    if r['zoom']:
        if cur is None: cur = [r]
        else: cur.append(r)
    elif cur: moves.append(cur); cur = None
if cur: moves.append(cur)
print(f'{len(moves)} camera moves')
for m in moves:
    mvs = [r['mv'] or 0 for r in m]; dts = [r['dt'] for r in m]
    # a jump: a frame whose motion is > 1.8x the larger of its neighbours' (or a stall: no motion between moving frames)
    jumps = []
    for j in range(1, len(m) - 1):
        a, b, c = mvs[j - 1], mvs[j], mvs[j + 1]
        if b > 1.8 * max(a, c) and b > 4: jumps.append((j, round(b, 1), round(m[j]['dt'], 1)))
        if b < 0.2 and a > 3 and c > 3: jumps.append((j, 'stall', round(m[j]['dt'], 1)))
    late = [(j, round(d, 1)) for j, d in enumerate(dts) if d > 25]
    print(f"  {m[0]['step'][:34]:34s} {m[0]['path']:>22s} -> {m[-1]['path']:<22s} {len(m):4d} frames {m[-1]['t'] - m[0]['t']:6.0f} ms  max move {max(mvs):6.1f} px/frame  late {late}  jumps {jumps}")
    if VERB:
        for j, r in enumerate(m):
            print(f"      {j:3d} dt={r['dt']:5.1f} mv={(r['mv'] or 0):6.1f} dop={r['dop']:.2f} " + ' | '.join(f"d{l[0]}#{l[1]} op={l[3]:.2f} lab={l[4] or '-'} {l[2][:44]}" for l in r['lays']))
# slow functions
agg = collections.defaultdict(list)
for n, t, ms in T: agg[n].append(ms)
print('function times (ms): name count total max')
for n, v in sorted(agg.items(), key=lambda x: -sum(x[1])):
    print(f'  {n:14s} {len(v):5d} {sum(v):8.1f} {max(v):7.1f}')
print('long animation frames:', len(loaf))
for e in loaf[:40]:
    if 'err' in e: print(e); continue
    sc = sorted(e['scripts'], key=lambda s: -s['dur'])[:2]
    print(f"  t={e['start']:8.0f} dur={e['dur']:6.1f} block={e['block']:6.1f} " + '; '.join(f"{s['inv'][:40]} {s['fn']} {s['dur']:.0f}ms forced={s['forced']:.0f}" for s in sc))
