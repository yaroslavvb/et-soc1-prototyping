import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
for f in sys.argv[1:]:
    out = subprocess.run([sys.executable, os.path.join(HERE, 'analyze.py'), f], capture_output=True, text=True).stdout.splitlines()
    z = [l for l in out if l.startswith('zoom frames')][0]
    moves = [l for l in out if l.startswith('  Step')]
    worst = max(float(l.split('max move')[1].split('px')[0]) for l in moves) if moves else 0
    print(f"{f:28s} {z}  worst-move {worst:.0f}px")
