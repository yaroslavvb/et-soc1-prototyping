#!/usr/bin/env python3
import json, sys
d = json.load(open(sys.argv[1]))
maxd = int(sys.argv[2]) if len(sys.argv) > 2 else 2
print(f"{'d':>1} {'cells':>7} {'trans':>8} {'flops':>6} {'lat':>3} {'area4x':>9}  module / path")
for b in d["blocks"]:
    if b["depth"] <= maxd and b["cells"] >= 20:
        print(f"{b['depth']:1d} {int(b['cells']):7d} {int(b['transistors']):8d} {int(b['flops']):6d} "
              f"{int(b['latches']):3d} {b['area']:9.1f}  {b['module'][:26]:26s} {b['path'][:70]}")
print("TOTAL", json.dumps(d["total"]))
