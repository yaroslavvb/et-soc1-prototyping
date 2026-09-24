#!/usr/bin/env python3
"""Which flows of each hop-distance config route through the four cells with no compute shire
((0,3),(0,4),(0,5),(5,3): master/IO/PCIe-type stops per the datasheet's 8x6 grid), and which touch the mesh edge."""
import json
from linkload import MESH, targets_at_distance, route
EMPTY = {(0, 3), (0, 4), (0, 5), (5, 3)}
res = {}
for d in (1, 2, 3, 4, 5, 6, 8):
    t, used, load = targets_at_distance(d)
    r = {}
    for order in ("XY", "YX"):
        thru = 0; nodes = 0; edge = 0; tot = 0
        for s in used:
            L = route(t[s], s, order)
            inner = [b for (a, b) in L[:-1]]
            if any(n in EMPTY for n in inner): thru += 1
            tot += len(L)
            edge += sum(1 for (a, b) in L if (a[0] == b[0] and a[0] in (0, 5)) or (a[1] == b[1] and a[1] in (0, 5)))
        r[order] = {"flows_through_empty": thru, "frac_linkhops_on_edge": edge / tot}
    res[d] = {"n": len(used), **r, "pairs": [(s, t[s]) for s in used]}
    print(d, len(used), {o: r[o] for o in r})
print("d=8 pairs (reader<-target):", [(s, MESH[s], t, MESH[t]) for s, t in res[8]["pairs"]])
