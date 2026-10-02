"""moves.py RUN.json...: per camera move, in order: frames, duration, late frames, peak px/frame, the largest
frame-to-frame velocity change as % of peak (kink), and the first frame's speed as % of peak (a move that starts with a jump).
Every move the recording marks as zooming, whatever its step text: summ.py and kink.py read only the moves of an
access or a flow ("Step N of M"), so a run of level tabs or of the ladder's moves reports no move there (the code
review of 1 Oct 2026 wrote this; px are the chip frame's, 1400 x 792 units, which the percentages do not depend on)."""
import json, sys, math, re
def mat(s):
    if not s: return (1.0, 0.0, 0.0)
    m = re.match(r'matrix\(([^,]+),0,0,([^,]+),([^,]+),([^)]+)\)', s)
    return (float(m.group(1)), float(m.group(3)), float(m.group(4)))
def moves(path):
    R = json.load(open(path)); log = R['log']; sx, sy, sw, sh = R['svg']
    k_px = min(sw / 1400, sh / 792)
    rows = []
    for i in range(1, len(log)):
        t0, s0, L0, p0, z0 = log[i - 1]; t1, s1, L1, p1, z1 = log[i]
        a = {(l[0], l[1]): l for l in L0}; b = {(l[0], l[1]): l for l in L1}
        common = [k for k in b if k in a]
        v = None
        if common:
            k = max(common, key=lambda q: b[q][3])
            (k0, x0, y0), (k1, x1, y1) = mat(a[k][2]), mat(b[k][2])
            # the frame centre's motion (svg units -> px) and the zoom rate
            cx, cy = 510, 312
            px = (k1 * (cx - x0) / k0 + x1 - cx) * k_px; py = (k1 * (cy - y0) / k0 + y1 - cy) * k_px
            f = 16.67 / max(1.0, t1 - t0); v = (px * f, py * f, math.log(k1 / k0) * f)
        rows.append((t1 - t0, z1, v))
    out, cur = [], None
    for dt, z, v in rows:
        if z:
            cur = cur or []; cur.append((dt, v))
        elif cur: out.append(cur); cur = None
    if cur: out.append(cur)
    res = []
    for m in out:
        vs = [x[1] or (0, 0, 0) for x in m]
        sp = [math.hypot(v[0], v[1]) for v in vs]; zr = [abs(v[2]) for v in vs]
        pk = max(sp) or 1e-9; zp = max(zr) or 1e-9
        dv = max((math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(vs, vs[1:])), default=0)
        dz = max((abs(b[2] - a[2]) for a, b in zip(vs, vs[1:])), default=0)
        first = max(sp[0] / pk, zr[0] / zp) if vs else 0
        res.append(dict(n=len(m), ms=round(sum(x[0] for x in m)), late=sum(1 for x in m if x[0] > 25), maxdt=round(max(x[0] for x in m), 1), peak=round(pk, 1), kink=round(100 * max(dv / pk, dz / zp)), first=round(100 * first)))
    return res
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('==', p)
        for i, r in enumerate(moves(p)): print(f"  {i:2d} n={r['n']:4d} {r['ms']:5d} ms late {r['late']} max {r['maxdt']:5.1f}  peak {r['peak']:6.1f}  kink {r['kink']:3d}%  first {r['first']:3d}%")
