"""motion.py RUN [step-substring]: the camera's screen motion per frame (velocity vector of the frame centre and zoom rate),
to find kinks at the boundaries between scales."""
import json, sys, math, re
R = json.load(open(sys.argv[1])); log = R['log']; want = sys.argv[2] if len(sys.argv) > 2 else ''
sx, sy, sw, sh = R['svg']; kpx = min(sw / 1300, sh / 792)
def mat(s):
    if not s: return (1.0, 0.0, 0.0)
    m = re.match(r'matrix\(([^,]+),0,0,([^,]+),([^,]+),([^)]+)\)', s); return (float(m.group(1)), float(m.group(3)), float(m.group(4)))
C = (-172 + 1264 / 2, -74 + 774 / 2)
prev = None; out = []
for i in range(1, len(log)):
    t0, s0, L0, p0, z0 = log[i - 1]; t1, s1, L1, p1, z1 = log[i]
    if not z1 or want not in s1: continue
    a = {(l[0], l[1]): l for l in L0}; b = {(l[0], l[1]): l for l in L1}
    com = [k for k in b if k in a]
    if not com: continue
    k = max(com, key=lambda q: b[q][3])
    (k0, x0, y0), (k1, x1, y1) = mat(a[k][2]), mat(b[k][2])
    # where the layer point under the frame centre in frame i-1 is now: the centre's motion; and the zoom rate
    px, py = (C[0] - x0) / k0, (C[1] - y0) / k0
    vx, vy = (k1 * px + x1 - C[0]) * kpx, (k1 * py + y1 - C[1]) * kpx
    zr = math.log(k1 / k0)
    dt = t1 - t0
    out.append((i, dt, vx / dt * 16.67, vy / dt * 16.67, zr / dt * 16.67, len(L1), ' '.join(f"d{l[0]}:{l[3]:.2f}" for l in L1), s1[:22]))
for o in out:
    i, dt, vx, vy, zr, n, lays, st = o
    ang = math.degrees(math.atan2(vy, vx)) if abs(vx) + abs(vy) > 0.05 else float('nan')
    print(f"{i:5d} dt={dt:5.1f} v=({vx:7.2f},{vy:7.2f}) |v|={math.hypot(vx, vy):6.2f} dir={ang:7.1f} zoom/frame={zr*1000:7.2f}e-3 {lays} {st}")
