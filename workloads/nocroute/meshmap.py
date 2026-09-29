"""The logical mesh of the ET-SoC-1, routes on it, and the R32 stream sets (EXPERIMENT nocr, hub rungs 31 and 32).

Coordinates are marty1885's logical map as workloads/nocbench/analyze.py has it (MARTY, EMPTY): (x, y), x = 0..5,
y = 0..5, 32 compute shires plus four grey cells that route traffic but run no kernel. The memory shires sit off the
y ends (y = -1 and y = 6) in this frame (docs/reports/data/2026-09-27-chip-diagram/research/firmware_map.json).
"x first" in this file means x of THIS map, which is what the chip diagram and heat-per-mm's route() assume (fact L104).

Nothing here touches a card. `python3 meshmap.py` prints the stream sets and checks them.
"""
import itertools
import json
import sys

# Copied from workloads/nocbench/analyze.py (MARTY, EMPTY); tools/claims-v3/nocr/reduce.py checks the copy is equal.
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
EMPTY = [(0, 3), (0, 4), (0, 5), (5, 3)]
CELL = {xy: s for s, xy in MARTY.items()}

# What the chip diagram draws today (firmware_map.json): the master shire at (0, 3), the spare at (5, 3), memory shire
# k at (k + 1, -1) for k < 4 and (k - 3, 6) for k >= 4. These are the predictions R31 tests.
FW_MASTER = (0, 3)
FW_SPARE = (5, 3)
FW_MS = {0: (1, -1), 1: (2, -1), 2: (3, -1), 3: (4, -1), 4: (1, 6), 5: (2, 6), 6: (3, 6), 7: (4, 6)}

GRID = [(x, y) for y in range(6) for x in range(6)]
RING = [(x, y) for y in range(-1, 7) for x in range(-1, 7) if not (0 <= x <= 5 and 0 <= y <= 5)]


def hops(a, b):
    """Manhattan distance between two cells (tuples) or shires (ints)."""
    a = MARTY[a] if isinstance(a, int) else a
    b = MARTY[b] if isinstance(b, int) else b
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def route(src, dst, order):
    """The cells a packet visits from src to dst under dimension-order routing: order 'xy' moves along x first."""
    (x, y), (x1, y1) = src, dst
    out = [(x, y)]
    for axis in order:
        if axis == "x":
            while x != x1:
                x += 1 if x1 > x else -1
                out.append((x, y))
        else:
            while y != y1:
                y += 1 if y1 > y else -1
                out.append((x, y))
    return out


def links(path):
    return list(zip(path[:-1], path[1:]))


def link_loads(flows, order):
    """flows: list of (src_cell, dst_cell) for the DATA (a read's target -> reader; a write's writer -> destination).
    Returns {directed link: [flow indices]} under dimension order `order`."""
    load = {}
    for i, (s, d) in enumerate(flows):
        for l in links(route(s, d, order)):
            load.setdefault(l, []).append(i)
    return load


def max_share(flows, order):
    ld = link_loads(flows, order)
    return max((len(v) for v in ld.values()), default=0)


# Bandwidth of one reader shire (32 minions, 1 KB tensor loads, two in flight) from a scratchpad d hops away, GB/s
# at 600 MHz: E27 (catalogue.json; SYNTHESIS.md 1c), identical on aifoundry2 and aifoundry3. Beyond d = 8: 1/bw is
# near linear in d (r = 0.985), so extrapolate the 1-8 line. Used only for predictions, never in a decision.
BW_E27 = {1: 46.8, 2: 41.8, 3: 37.4, 4: 32.8, 5: 30.9, 6: 26.7, 8: 25.5}


def bw_model(d):
    if d in BW_E27:
        return BW_E27[d]
    xs = sorted(BW_E27)
    ys = [1.0 / BW_E27[x] for x in xs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return 1.0 / (my + b * (d - mx))


def packet_links(src, dst, mode, reply_order, request_order):
    """The directed links of one flow's packets: [(network, link, kind)], kind 'data' (the packets that carry the
    bytes) or 'ctl' (the small ones going the other way). A read (dst tensor-loads from src): requests dst -> src
    under the request order (ctl), replies src -> dst under the reply order (data). A write (src tensor-stores into
    dst): the stores src -> dst under the request order (data), their acknowledgements dst -> src under the reply
    order (ctl). Under dimension order the request path dst -> src is the reverse of the path src -> dst under the
    OTHER order, so a set whose replies share no link under one order has requests sharing the reversed link."""
    if mode == "read":
        parts = (("rep", route(src, dst, reply_order), "data"), ("req", route(dst, src, request_order), "ctl"))
    else:
        parts = (("req", route(src, dst, request_order), "data"), ("rep", route(dst, src, reply_order), "ctl"))
    return [(net, l, kind) for net, path, kind in parts for l in links(path)]


def maxmin_w(uses, demand, cap):
    """Max-min fair rates (progressive filling). uses: {resource: [(flow, weight)]}; each resource carries at most
    `cap` (a number, or {resource: capacity}), and flow i loads it with weight x rate[i]; flow i asks for demand[i]."""
    capof = cap.get if isinstance(cap, dict) else (lambda key: cap)
    n = len(demand)
    rate = [0.0] * n
    frozen = [False] * n
    while not all(frozen):
        active = [i for i in range(n) if not frozen[i]]
        # the largest equal increment before a flow meets its demand or a resource fills
        inc = min(demand[i] - rate[i] for i in active)
        for key, u in uses.items():
            w = sum(wt for i, wt in u if not frozen[i])
            if w > 0:
                inc = min(inc, (capof(key) - sum(rate[i] * wt for i, wt in u)) / w)
        inc = max(inc, 0.0)
        for i in active:
            rate[i] += inc
        for i in active:
            if rate[i] >= demand[i] - 1e-9:
                frozen[i] = True
        for key, u in uses.items():
            if sum(rate[i] * wt for i, wt in u) >= capof(key) - 1e-9:
                for i, wt in u:
                    if wt > 0:
                        frozen[i] = True
    return rate


def rates(flows, demand, mode="read", reply_order="xy", request_order="xy", cap=102.4, c=0.0, net="split",
          cap_req=None):
    """Max-min rates of flows (src_cell, dst_cell) when every directed link carries at most `cap` GB/s of data and a
    control packet (a read's request, a write's acknowledgement) costs c times the data it stands for. net 'split':
    requests and replies travel on separate networks (each link of each has `cap`, or `cap_req` on the request
    network when given); 'shared': one network."""
    uses = {}
    for i, (s, d) in enumerate(flows):
        for nw, l, kind in packet_links(s, d, mode, reply_order, request_order):
            w = 1.0 if kind == "data" else c
            if w > 0:
                uses.setdefault((nw if net == "split" else "one", l), []).append((i, w))
    if cap_req is not None and net == "split":
        return maxmin_w(uses, demand, {k: (cap_req if k[0] == "req" else cap) for k in uses})
    return maxmin_w(uses, demand, cap)


def maxmin(flows, demand, order, cap):
    """Replies alone (control packets free): the model the first draft registered."""
    return rates(flows, demand, "read", order, order, cap, 0.0)


def share_profile(flows, order):
    """Under dimension order `order` (requests and replies alike): the most flows whose replies share one directed
    link, the most whose requests do, and the most flows on a directed link that carries a reply of one flow and a
    request of another (1 when no link mixes them)."""
    rep, req = {}, {}
    for i, (s, d) in enumerate(flows):
        for l in links(route(s, d, order)):
            rep.setdefault(l, set()).add(i)
        for l in links(route(d, s, order)):
            req.setdefault(l, set()).add(i)
    mixed = max((len(rep[l] | req[l]) for l in set(rep) & set(req)), default=1)
    return {"reply": max((len(v) for v in rep.values()), default=0),
            "request": max((len(v) for v in req.values()), default=0), "mixed": mixed}


def _family(name, share_order, link, targets, readers, note):
    """Nested stream sets through one directed link: the i-th nearest target pairs with the i-th reader (readers
    listed straight-through first, then by growing offset), so the smallest sets hold the shortest flows."""
    flows = [(t, r) for t, r in zip(targets, readers)]
    return {"family": name, "share_order": share_order, "link": link, "flows": flows, "note": note}


# The families (data flows src -> dst). Under `share_order` every flow of a family crosses `link`; under the other
# order no two flows of the family share any directed link. check_sets() proves both for every nested subset.
FAMILIES = [
    _family("rowE", "xy", ((4, 1), (5, 1)),
            [(4, 1), (3, 1), (2, 1), (1, 1), (0, 1)], [(5, 1), (5, 0), (5, 2), (5, 4), (5, 5)],
            "sources along row 1, sinks down column 5: x first sends all five along row 1 through (4,1)->(5,1)"),
    _family("rowF", "xy", ((4, 2), (5, 2)),
            [(4, 2), (3, 2), (2, 2), (1, 2), (0, 2)], [(5, 2), (5, 1), (5, 4), (5, 0), (5, 5)],
            "the same through row 2 ((5, 3) is grey, so the sinks skip it): a second eastward place for k = 5"),
    _family("rowW", "xy", ((1, 2), (0, 2)),
            [(1, 2), (2, 2), (3, 2)], [(0, 2), (0, 1), (0, 0)],
            "sources along row 2, sinks in column 0 (only rows 0-2 of column 0 are compute shires): westward links"),
    _family("colS", "yx", ((2, 4), (2, 5)),
            [(2, 4), (2, 3), (2, 2), (2, 1), (2, 0)], [(2, 5), (1, 5), (3, 5), (4, 5), (5, 5)],
            "the transpose of rowE: sources up column 2, sinks along row 5; y first sends all through (2,4)->(2,5)"),
    _family("colN", "yx", ((3, 1), (3, 0)),
            [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)], [(3, 0), (2, 0), (4, 0), (1, 0), (5, 0)],
            "sources down column 3, sinks along row 0: northward links"),
]
# Positive controls: straight flows, the same path under either order, all three through one link.
POSITIVE = [
    {"name": "posRow", "link": ((2, 0), (3, 0)), "flows": [((2, 0), (3, 0)), ((1, 0), (4, 0)), ((0, 0), (5, 0))]},
    {"name": "posCol", "link": ((4, 2), (4, 3)), "flows": [((4, 2), (4, 3)), ((4, 1), (4, 4)), ((4, 0), (4, 5))]},
]
LEVELS = {"rowE": [2, 3, 5], "rowF": [2, 3, 5], "rowW": [2, 3], "colS": [2, 3, 5], "colN": [2, 3, 5]}


def _endpoints_ok(flows):
    cells = [c for f in flows for c in f]
    return len(cells) == len(set(cells)) and all(c in CELL for c in cells)


def _disjoint_both(flows):
    return max_share(flows, "xy") <= 1 and max_share(flows, "yx") <= 1


def negative_controls(pool):
    """Two sets of flows from `pool` that share no directed link under either order and no endpoint: neg1 from the
    straight one-hop flows first (the heaviest load with no sharing), neg2 from the bent flows."""
    out = []
    for name, keep in (("neg1", lambda f: hops(*f) <= 2), ("neg2", lambda f: f[0][0] != f[1][0] and f[0][1] != f[1][1])):
        chosen = []
        for f in sorted((f for f in pool if keep(f)), key=lambda f: (hops(*f), f)):
            if _endpoints_ok(chosen + [f]) and _disjoint_both(chosen + [f]):
                chosen.append(f)
        out.append({"name": name, "flows": chosen})
    return out


def build_sets():
    """The R32 sets as registered: every set, its flows as shire pairs (src>dst), and the checks' numbers."""
    sets = []
    pool = []
    for fam in FAMILIES:
        for k in LEVELS[fam["family"]]:
            fl = fam["flows"][:k]
            sets.append({"name": f"{fam['family']}{k}", "kind": "family", "family": fam["family"],
                         "share_order": fam["share_order"], "k": k, "link": fam["link"], "flows": fl})
        pool += fam["flows"]
    for p in POSITIVE:
        sets.append({"name": p["name"], "kind": "positive", "family": p["name"], "share_order": "both",
                     "k": len(p["flows"]), "link": p["link"], "flows": p["flows"]})
        pool += p["flows"]
    for n in negative_controls(pool):
        sets.append({"name": n["name"], "kind": "negative", "family": n["name"], "share_order": "none",
                     "k": len(n["flows"]), "link": None, "flows": n["flows"]})
    uniq = []
    for f in pool:
        if f not in uniq:
            uniq.append(f)
    return sets, uniq


def check_sets(sets):
    """Every property the design claims, per set; returns a list of failures (empty when all hold). Requests count:
    under dimension order a read's request travels dst -> src, the reverse of its reply's path under the other
    order, so every family shares a link under BOTH orders, on replies under one and on requests under the other."""
    bad = []
    for s in sets:
        fl = s["flows"]
        if not _endpoints_ok(fl):
            bad.append(f"{s['name']}: endpoints not distinct compute shires")
        prof = {o: share_profile(fl, o) for o in ("xy", "yx")}
        for o in ("xy", "yx"):
            if prof[o]["mixed"] > 1:
                bad.append(f"{s['name']}: a link carries replies and requests of different flows under {o}")
        k = len(fl)
        if s["kind"] == "family":
            o = s["share_order"]
            other = "yx" if o == "xy" else "xy"
            link = tuple(s["link"])
            back = (link[1], link[0])
            if len(link_loads(fl, o).get(link, [])) != k:
                bad.append(f"{s['name']}: not every reply crosses {s['link']} under {o}")
            if prof[o]["request"] != 1:
                bad.append(f"{s['name']}: requests share a link under {o}")
            if prof[other]["reply"] != 1:
                bad.append(f"{s['name']}: replies share a link under {other}")
            req_back = sum(1 for sd in fl if back in links(route(sd[1], sd[0], other)))
            if req_back != k or prof[other]["request"] != k:
                bad.append(f"{s['name']}: under {other} not every request crosses {back}")
        elif s["kind"] == "positive":
            link = tuple(s["link"])
            for o in ("xy", "yx"):
                if len(link_loads(fl, o).get(link, [])) != k:
                    bad.append(f"{s['name']}: not all replies cross {s['link']} under {o}")
                if prof[o]["request"] != k:
                    bad.append(f"{s['name']}: not all requests share a link under {o}")
        else:
            if not _disjoint_both(fl) or any(prof[o]["request"] > 1 for o in prof):
                bad.append(f"{s['name']}: flows share a link (replies or requests)")
            if k < 3:
                bad.append(f"{s['name']}: fewer than 3 flows")
    return bad


# Request cost c: a control packet (a read's line request) loads its link c times as much as the reply it asks for.
# c = 0: requests are free (the first draft's model); c = 1: every packet costs the same (links limited by packets,
# or a request as wide as a reply). A request never costs more than its reply (c <= 1), registered in PREREG.md.
PRED_CAPS = (51.2, 102.4, 204.8)
PRED_CS = (0.0, 0.5, 1.0)


def predictions(sets, caps=PRED_CAPS, cs=PRED_CS):
    """rho (set bandwidth over the sum of its flows' solo bandwidths) that max-min sharing predicts for READS, per set,
    per dimension order (requests and replies the same), per link capacity in GB/s and per request cost c, with
    E27's solo bandwidths as demands. Keys: '<order>@<cap>/c<c>'."""
    out = {}
    for s in sets:
        dem = [bw_model(hops(*f)) for f in s["flows"]]
        row = {"demand_gbs": round(sum(dem), 1), "d": [hops(*f) for f in s["flows"]]}
        for o in ("xy", "yx"):
            for cap in caps:
                for c in cs:
                    r = rates(s["flows"], dem, "read", o, o, cap, c)
                    row[f"{o}@{cap:g}/c{c:g}"] = round(sum(r) / sum(dem), 3)
        out[s["name"]] = row
    return out


def as_pairs(flows):
    """'src>dst,...' in shire ids."""
    return ",".join(f"{CELL[s]}>{CELL[d]}" for s, d in flows)


def export():
    sets, pool = build_sets()
    return {
        "about": "R32 stream sets (tools/claims-v3/nocr). A flow is DATA src>dst in shire ids: for a read launch the "
                 "dst shire's 32 minions tensor-load from the src shire's scratchpad; for a write launch the src "
                 "shire's minions tensor-store into the dst shire's scratchpad. 'share' counts, per dimension order, the "
                 "most flows sharing one directed link on replies (data src>dst) and on requests (dst>src). "
                 "Generated by workloads/nocroute/meshmap.py; do not edit by hand.",
        "sets": [{**s, "pairs": as_pairs(s["flows"]), "flows": [[list(a), list(b)] for a, b in s["flows"]],
                  "link": [list(c) for c in s["link"]] if s["link"] else None,
                  "share": {o: share_profile(s["flows"], o) for o in ("xy", "yx")}} for s in sets],
        "flows": [{"pair": as_pairs([f]), "src": list(f[0]), "dst": list(f[1]), "d": hops(*f)} for f in pool],
        "checks_failed": check_sets(sets),
        "predictions": predictions(sets),
    }


if __name__ == "__main__":
    e = export()
    if "--json" in sys.argv:
        json.dump(e, sys.stdout, indent=1)
        print()
        sys.exit(1 if e["checks_failed"] else 0)
    for s in e["sets"]:
        p = e["predictions"][s["name"]]
        sh = s["share"]
        print(f"{s['name']:7s} {s['kind']:8s} k={s['k']} d={p['d']} demand {p['demand_gbs']:6.1f} GB/s  share "
              f"xy {sh['xy']['reply']}/{sh['xy']['request']} yx {sh['yx']['reply']}/{sh['yx']['request']}   {s['pairs']}")
        for o in ("xy", "yx"):
            print("        " + o + ": " + "  ".join(f"{k[3:]}={v:.2f}" for k, v in p.items() if k.startswith(o + "@")))
    print(f"{len(e['flows'])} distinct flows; checks failed: {e['checks_failed'] or 'none'}")
