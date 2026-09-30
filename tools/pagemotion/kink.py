"""kink.py RUN: per camera move, the largest frame-to-frame change of the camera's velocity (screen px/frame at the
frame centre) and of its zoom rate, relative to the move's peak speed: a smooth move changes a little each frame."""
import json, os, sys, math, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(HERE, 'motion.py'), sys.argv[1]], capture_output=True, text=True).stdout.splitlines()
rows = []
for l in out:
    m = re.match(r'\s*(\d+) dt=\s*([\d.]+) v=\(\s*([-\d.]+),\s*([-\d.]+)\) \|v\|=\s*([\d.]+) dir=\s*(\S+) zoom/frame=\s*([-\d.]+)e-3 (.*?) (Step \d+ of \d+: .*)$', l)
    if m: rows.append((int(m[1]), float(m[3]), float(m[4]), float(m[7]), m[9]))
moves = []; cur = []
for r in rows:
    if cur and (r[0] != cur[-1][0] + 1): moves.append(cur); cur = []
    cur.append(r)
if cur: moves.append(cur)
for mv in moves:
    peak = max(math.hypot(r[1], r[2]) for r in mv) or 1; zpk = max(abs(r[3]) for r in mv) or 1
    dv = max(math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(mv, mv[1:])) if len(mv) > 1 else 0
    dz = max(abs(b[3] - a[3]) for a, b in zip(mv, mv[1:])) if len(mv) > 1 else 0
    # rests: frames inside the move where the camera nearly stops
    rests = [r[0] for r in mv[3:-3] if math.hypot(r[1], r[2]) < 0.05 * peak and abs(r[3]) < 0.05 * zpk]
    print(f"{mv[0][4][:26]:26s} frames {len(mv):4d} peak {peak:5.1f} px/f  max dv/frame {dv:5.2f} px ({100*dv/peak:4.1f}% of peak)  max dzoom/frame {100*dz/zpk:4.1f}% of peak  rests {len(rests)}")
