#!/usr/bin/env python3
"""Replicate enercat's targetsAtDistance (host/main.cpp, HEAD) and route every flow on the 6x6 interior mesh
under XY and YX dimension-order routing. Data (responses) flow target -> reader; requests reader -> target.
Report per d: participants, 2-reader targets, flows per directed link (max/mean over used links), link-hops,
and the fraction of each flow's hops that are x vs y."""
import collections, json, sys
MESH = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
def hops(a, b):
    (xa, ya), (xb, yb) = MESH[a], MESH[b]; return abs(xa - xb) + abs(ya - yb)

def targets_at_distance(d, mask=0xffffffff, axis="any"):
    t = [0]*32; load = [0]*32; used = []
    for s in range(32):
        if not (mask >> s) & 1: continue
        best = -1
        for c in range(32):
            if c == s or hops(s, c) != d or load[c] >= 2: continue
            ps, pc = MESH[s], MESH[c]
            if axis == "x" and ps[1] != pc[1]: continue
            if axis == "y" and ps[0] != pc[0]: continue
            if best < 0 or load[c] < load[best]: best = c
        if best >= 0:
            t[s] = best; load[best] += 1; used.append(s)
    return t, used, load

def route(a, b, order):
    """list of directed links (from_xy, to_xy) from shire a to shire b"""
    (x, y), (xb, yb) = MESH[a], MESH[b]
    links = []
    def stepx():
        nonlocal x
        while x != xb:
            nx = x + (1 if xb > x else -1); links.append(((x, y), (nx, y))); x = nx
    def stepy():
        nonlocal y
        while y != yb:
            ny = y + (1 if yb > y else -1); links.append(((x, y), (x, ny))); y = ny
    if order == "XY": stepx(); stepy()
    else: stepy(); stepx()
    return links

out = {}
for axis in ("any", "x", "y"):
    for d in range(1, 11):
        t, used, load = targets_at_distance(d, axis=axis)
        if not used: continue
        rec = {"participants": len(used), "targets_with_2": sum(1 for l in load if l == 2),
               "targets_with_1": sum(1 for l in load if l == 1)}
        xh = sum(abs(MESH[s][0]-MESH[t[s]][0]) for s in used); yh = sum(abs(MESH[s][1]-MESH[t[s]][1]) for s in used)
        rec["x_hop_frac"] = xh / (xh + yh)
        for order in ("XY", "YX"):
            cnt = collections.Counter(); cntreq = collections.Counter()
            for s in used:
                for l in route(t[s], s, order): cnt[l] += 1     # data: target -> reader
                for l in route(s, t[s], order): cntreq[l] += 1  # requests: reader -> target
            v = list(cnt.values())
            # shared links: links carrying data of >1 flow; and links carrying both data and requests
            both = sum(1 for l in cnt if l in cntreq)
            # per flow: max sharing along its path (bottleneck)
            bott = [max(cnt[l] for l in route(t[s], s, order)) for s in used]
            rec[order] = {"links_used": len(v), "max_flows_per_link": max(v), "mean_flows_per_used_link": sum(v)/len(v),
                          "link_hops": sum(v), "frac_linkhops_shared": sum(c for c in v if c > 1)/sum(v),
                          "mean_bottleneck_flows": sum(bott)/len(bott), "links_carrying_req_and_data": both}
        out[f"{axis}/d{d}"] = rec
        print(f"{axis:3s} d={d:2d} n={rec['participants']:2d} 2-reader targets={rec['targets_with_2']:2d} xfrac={rec['x_hop_frac']:.2f} | " +
              " | ".join(f"{o}: max {rec[o]['max_flows_per_link']} mean {rec[o]['mean_flows_per_used_link']:.2f} shared {rec[o]['frac_linkhops_shared']:.2f} bott {rec[o]['mean_bottleneck_flows']:.2f} req&data {rec[o]['links_carrying_req_and_data']}" for o in ("XY","YX")))
json.dump(out, open("linkload.json", "w"), indent=1)
