#!/usr/bin/env python3
"""jit_analyze.py <jit.json> [-v]: per move, the late frames (over 25 ms; where in the move) and the camera's zoom
rate frame to frame (its largest jump as a share of the move's top rate: an eased move changes a few % a frame)."""
import json, math, re, statistics, sys
from collections import OrderedDict
D = json.load(open(sys.argv[1])); V = '-v' in sys.argv
MAT = re.compile(r'matrix\(([^)]+)\)')
def scale(tr):
    m = MAT.search(tr or '')
    if not m: return None
    a = [float(x) for x in re.split(r'[ ,]+', m.group(1).strip())]
    return math.hypot(a[0], a[1])
print(f"{D['vp']} dpr {D['dpr']} cpu {D['cpu']}; errors: {D.get('errors')}")
for run in D['runs']:
    fr = run['frames']
    moves = OrderedDict()
    for i in range(1, len(fr)):
        t0, t1 = fr[i - 1][0], fr[i][0]
        moves.setdefault(fr[i][2], []).append((t1 - t0, fr[i - 1], fr[i]))
    tot_late = tot = 0; rows = []
    for tag, fs in moves.items():
        # the frames where the camera moved: some layer shown in both frames changed its scale or position
        mv = []
        for dt, a, b in fs:
            A = {x[0]: x[1] for x in a[3]}; B = {x[0]: x[1] for x in b[3]}
            com = [n for n in B if n in A]
            changed = any(A[n] != B[n] for n in com) or set(A) != set(B)
            if changed:
                ks = [(scale(A[n]), scale(B[n])) for n in com]
                ks = [math.log(k2 / k1) for k1, k2 in ks if k1 and k2]
                mv.append((dt, statistics.median(ks) if ks else 0.0, b[0]))
        if len(mv) < 3: continue
        n = len(mv); late = [(j, dt) for j, (dt, _, _) in enumerate(mv) if dt > 25]
        rate = [abs(x[1]) / max(x[0], 1) for x in mv]   # |dlog k| per ms
        peak = max(rate) or 1
        kink = max(abs(rate[j] - rate[j - 1]) for j in range(1, n)) / peak if peak > 1e-9 else 0
        where = ''.join('s' if j < n * 0.2 else 'e' if j > n * 0.8 else 'm' for j, _ in late)
        tot += n; tot_late += len(late)
        rows.append((tag, n, len(late), max(dt for dt, _, _ in mv), where, kink, sum(dt for dt, _, _ in mv)))
    print(f"\n== {run['label']}: {tot} moving frames, {tot_late} late ({100 * tot_late / max(tot, 1):.1f}%)")
    for tag, n, nl, mx, where, kink, dur in rows:
        if V or nl or kink > 0.5:
            print(f"  {tag[:46]:46s} frames {n:4d} {dur:6.0f} ms  late {nl:3d} (max {mx:5.0f} ms) at {where[:12]:12s} kink {kink:4.2f}")
