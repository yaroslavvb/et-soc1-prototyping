#!/usr/bin/env python3
"""Q138(g), fix pass after verification (C2): does each batch's run time show the settled-value comparison?

    python3 checked_signature.py [sims dir] > checked_signature.txt

run_tile.py's comparison with the bench VCD (on unless --no-check) walks every net at every clock edge of every unit: a cost per
run that does not grow with the events simulated. For every batch (a sims file x netlist x tile group: the middle point, the other
two launch points, the kinds) this fits a run's recorded seconds against the events it simulated (timed toggles of the 16 units,
ports included) and prints the intercept in events' worth of simulation (intercept / slope). Batches with the comparison carry
more of it than batches without. Reads the committed records only; simulates nothing.
"""
import json, os, sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sims")
FILES = ["primary", "vstyle", "skew150", "wire0", "wire3", "jitter20"]


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return my - b * mx, b


print("# Q138(g): a run's fixed cost, in events' worth of simulation, per batch (checked_signature.py over sims/*.json)")
print("| sims file | netlist | tiles | runs | `checked` | intercept, s | slope, s per million events | fixed cost, million events |")
print("|---|---|---|---:|---|---:|---:|---:|")
by_flag = {}
for f in FILES:
    d = json.load(open(os.path.join(D, f + ".json")))
    groups = {}
    for key, r in d.items():
        net, tile, pt = key.split("__")
        grp = "kinds" if tile.startswith("kind_") else ("other two points" if pt != "471698" else "middle point")
        ev = r["total"]["timed"] + sum(i.get("timed_ports_in", 0) for i in r["instances"].values())
        groups.setdefault((net, grp), []).append((ev, r["seconds"], r.get("checked")))
    for (net, grp), lst in sorted(groups.items()):
        a, b = fit([e for e, s, c in lst], [s for e, s, c in lst])
        flags = sorted({str(c) for e, s, c in lst})
        fixed = a / b / 1e6
        by_flag.setdefault("/".join(flags), []).append(fixed)
        print(f"| `{f}` | `{net}` | {grp} | {len(lst)} | {'/'.join(flags)} | {a:.2f} | {b * 1e6:.2f} | {fixed:.2f} |")
print()
for flag, v in sorted(by_flag.items()):
    print(f"checked {flag}: {len(v)} batches, fixed cost {min(v):.2f}-{max(v):.2f} million events")
