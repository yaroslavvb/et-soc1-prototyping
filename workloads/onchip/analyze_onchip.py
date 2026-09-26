#!/usr/bin/env python3
"""Turn run_onchip.sh sweeps and run_onchip_power.sh telemetry into the numbers the relay report quotes.

    analyze_onchip.py <sweep.jsonl> [more...] [--power <dir>] --out onchip.json

Nothing is fitted. Rates come from the on-device cycle counter, converted at 600 MHz, because a launch costs a
few hundred microseconds either way. Every relay run verifies its own output: each element must equal the value
its slab started with plus one per stage, and for the hop medium the slab it must have started from is the one
belonging to the shire `stages` places back round the ring.

The ring runs in shire-ID order (ring_prev in kernel/onchip.c), and shire IDs do not follow the mesh. So
`hop_distance` is an offset in shire ID, not a number of mesh hops: each distance row also carries the mesh hops
that offset actually spans, from marty1885's shire map in workloads/nocbench/analyze.py.

The keys the relay page draws from (added 25 Sep; every earlier key is unchanged):
  layout, empty, ring      the shire map (shire -> [x, y]), its four empty cells, and the ring's shire order
  distance[].by_card       each card's GB/s and cycles per stage at that ring offset
  distance[].longest       the longest hand-off in the ring (mesh hops) and the (source, destination) pairs at it
  repeats                  per card, every run of the headline configuration (1 MB per shire per stage, 8 stages,
                           32 shires, one add, offset 1) with all three media, one row per sweep group
Added 26 Sep (every earlier key and value is unchanged; the rows' own fields stay the first card's):
  intensity/size/stages/shires[].by_card   each card's row at the same setting, {card: {ok, dram, scp, hop,
                           scp_over_dram, hop_over_dram}}, for every card with all three media there

The version-3 layout (added 26 Sep, for the three-card check): the sweeps may be the claims-v3 passes,
docs/reports/data/2026-09-25-claims-v3/raw/<card>/lat/p*/rl/sweep.jsonl, whose lines carry 'pass' and 'cfg' and
whose 'host' is the card id (aifoundry2, aifoundry3, aifoundry1-c1). Such rows are first reduced to one row per card
and configuration (pass_means below: the mean over the passes), so every key above holds pass means; nothing is
dropped here, because the V3-LAT reducer (tools/claims-v3/lat/reduce.py) kept every relay launch these passes
recorded (checked 26 Sep; aifoundry3 lacks four launches whose host process crashed, exit 139). With such rows:
  --cards a,b,c            the card order of 'cards' (the first card's rows are the rows' own fields); default sorted
  repeats                  one row per sweep group and pass (key 'pass')
  offsets                  the 'offsets' group, the hand-off at every ring offset d = 1..31: per offset its mesh hops,
                           longest hand-off and by_card {card: {gb_s, stage_cycles, passes}}
  offset_fit               per card, over the 16 ring geometries (offset g with its mirror 32 - g, averaged; 16 alone),
                           as the V3-LAT item LAT-R defines them: the GB/s line against the longest hand-off, r against
                           the longest and the mean hops (geometries and all 31 offsets), the stage cycles added per hop
                           of the longest hand-off with its 99% interval, the mean-hops coefficient of GB/s ~ longest +
                           mean hops with its 99% interval (LAT-R part iii), and the worst mirror pair (part iv)
  coverage                 per card, the passes read and every configuration some pass lacks
  bigsize[].by_card        (any sweep with more than one card) each card's DRAM GB/s at that size
"""
import argparse
import collections
import gzip
import importlib.util
import json
import os

import numpy as np


def load(paths):
    rows = []
    for p in paths:
        for line in open(p):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def shire_map():
    """marty1885's (x, y) of each compute shire on the 6x6 mesh and the Manhattan-distance function, as
    workloads/nocbench/analyze.py holds them (the map the on-chip communication report checks against latency)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nocbench", "analyze.py")
    spec = importlib.util.spec_from_file_location("nocbench_analyze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MARTY, mod.hops


def shire_empty():
    """The four empty cells of the 6x6 mesh (no compute shire), from the same file."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nocbench", "analyze.py")
    spec = importlib.util.spec_from_file_location("nocbench_analyze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.EMPTY


def ring_hops(back):
    """Mesh hops between each of the 32 compute shires and the shire `back` places before it in ID order, which
    is the shire it reads from when all 32 run. Returns the mean and the range over the 32 shires."""
    layout, hops = shire_map()
    ids = sorted(layout)
    h = [hops(s, ids[(i - back) % len(ids)], layout) for i, s in enumerate(ids)]
    return {"mean": float(np.mean(h)), "min": int(min(h)), "max": int(max(h))}


def longest_handoff(back):
    """The longest hand-off in the ring at this offset: its mesh hops and every (source, destination) pair at it.
    Shire s reads from the shire `back` places before it in ID order, so the data moves source -> s."""
    layout, hops = shire_map()
    ids = sorted(layout)
    pairs = [(ids[(i - back) % len(ids)], s) for i, s in enumerate(ids)]
    h = [hops(a, b, layout) for a, b in pairs]
    return {"hops": int(max(h)), "pairs": [[int(a), int(b)] for (a, b), x in zip(pairs, h) if x == max(h)]}


HEADLINE_CONFIG = {"stage_bytes": 1048576, "stages": 8, "shires": 32, "work": 1}


def repeats(rows, card):
    """Every run of the headline configuration on one card that has all three media, one row per sweep group
    (the distance group runs the hand-off only, so it is not here), and per pass when the rows carry one."""
    by = collections.defaultdict(dict)
    for r in rows:
        if (r.get("test") == "relay" and r["host"] == card and r.get("hop_distance", 1) == 1
                and all(r.get(k) == v for k, v in HEADLINE_CONFIG.items())):
            by[(r["group"], r.get("pass"))][r["medium"]] = r["gb_s"]
    return [{"group": g, **({"pass": p} if p is not None else {}), **m,
             "hop_over_dram": m["hop"] / m["dram"], "scp_over_dram": m["scp"] / m["dram"]}
            for (g, p), m in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)) if len(m) == 3]


RELAY_KEY = ("host", "group", "medium", "stage_bytes", "stages", "work", "shires", "hop_distance")
MEAN_FIELDS = ("gb_s", "cycles_max", "cycles_mean", "wall_s", "bytes_per_cycle", "gflop_s")


def pass_means(rows):
    """Reduce claims-v3 relay rows (with 'pass') to one row per card and configuration: MEAN_FIELDS are the mean over
    the passes that ran it, 'ok' holds only if every pass's run was ok, 'wrong_elements' is their sum, 'passes' is
    the number of passes and 'gb_s_passes' each pass's GB/s (in pass order); the other fields are the first pass's
    ('shire0_final' must agree across passes, or it is None). Rows without 'pass' (the 22 September sweeps), and
    probe rows, are returned unchanged."""
    out, groups = [], collections.OrderedDict()
    for r in rows:
        if "pass" not in r or r.get("test") != "relay":
            out.append(r)
            continue
        groups.setdefault(tuple(r.get(k) for k in RELAY_KEY), []).append(r)
    for rs in groups.values():
        rs = sorted(rs, key=lambda q: q["pass"])
        m = dict(rs[0])
        for k in MEAN_FIELDS:
            if all(k in q for q in rs):
                m[k] = float(np.mean([q[k] for q in rs]))
        m["ok"] = all(q.get("ok") for q in rs)
        m["wrong_elements"] = int(sum(q.get("wrong_elements", 0) for q in rs))
        sf = {q.get("shire0_final") for q in rs}
        m["shire0_final"] = sf.pop() if len(sf) == 1 else None
        m["passes"] = len(rs)
        m["gb_s_passes"] = [q["gb_s"] for q in rs]
        m.pop("pass", None), m.pop("cfg", None)
        out.append(m)
    return out


T995 = {13: 3.0123, 14: 2.9768}   # two-sided 99% Student t quantiles for the offset fits (16 geometries)


def offset_fit(offsets, card):
    """The ring-offset sweep of one card reduced to the 16 geometries LAT-R uses (offset g and its mirror 32 - g
    hand the same pairs of shires the slab in opposite directions, so the two are averaged; 16 is its own mirror)."""
    G = {r["hop_distance"]: r["by_card"][card] for r in offsets if card in r["by_card"]}
    if sorted(G) != list(range(1, 32)):
        return None
    geo = {g: {k: (G[g][k] + G[32 - g][k]) / 2 if g < 16 else G[16][k] for k in ("gb_s", "stage_cycles")}
           for g in range(1, 17)}
    L = np.array([longest_handoff(g)["hops"] for g in range(1, 17)], float)
    MH = np.array([ring_hops(g)["mean"] for g in range(1, 17)], float)
    y = np.array([geo[g]["gb_s"] for g in range(1, 17)])
    c = np.array([geo[g]["stage_cycles"] for g in range(1, 17)])

    def ols(X, v, j):
        beta, *_ = np.linalg.lstsq(X, v, rcond=None)
        res = v - X @ beta
        df = len(v) - X.shape[1]
        se = float(np.sqrt(float(res @ res) / df * np.linalg.inv(X.T @ X)[j, j]))
        return beta, se, df

    X1 = np.vstack([np.ones(16), L]).T
    b1, _, _ = ols(X1, y, 1)
    bc, sec, dfc = ols(X1, c, 1)
    X2 = np.vstack([np.ones(16), L, MH]).T
    b2, se2, df2 = ols(X2, y, 2)
    d31 = sorted(G)
    L31 = [longest_handoff(d)["hops"] for d in d31]
    M31 = [ring_hops(d)["mean"] for d in d31]
    g31 = [G[d]["gb_s"] for d in d31]
    mir = {d: G[32 - d]["gb_s"] / G[d]["gb_s"] - 1 for d in range(1, 16)}
    wm = max(mir, key=lambda d: abs(mir[d]))
    best = max(d31, key=lambda d: G[d]["gb_s"])
    return {"geometries": 16, "passes_min": int(min(G[d].get("passes", 1) for d in d31)),
            "gb_s_line": {"a": float(b1[0]), "b_per_hop": float(b1[1])},
            "r_longest": float(np.corrcoef(L, y)[0, 1]), "r_mean": float(np.corrcoef(MH, y)[0, 1]),
            "r_longest_offsets": float(np.corrcoef(L31, g31)[0, 1]), "r_mean_offsets": float(np.corrcoef(M31, g31)[0, 1]),
            "stage_cycles_per_hop": float(bc[1]),
            "stage_cycles_per_hop_ci99": [float(bc[1] - T995[dfc] * sec), float(bc[1] + T995[dfc] * sec)],
            "mean_hops_coef": float(b2[2]), "mean_hops_coef_ci99": [float(b2[2] - T995[df2] * se2), float(b2[2] + T995[df2] * se2)],
            "worst_mirror": {"offset": int(wm), "mirror": int(32 - wm), "rel": float(mir[wm])},
            "best": {"offset": int(best), "gb_s": float(G[best]["gb_s"])},
            "slowest": {"offset": int(min(d31, key=lambda d: G[d]["gb_s"])), "gb_s": float(min(g31))}}


def coverage(raw, card):
    """The passes read for a card and every relay configuration that some pass lacks (claims-v3 rows only)."""
    rs = [r for r in raw if r.get("host") == card and r.get("test") == "relay" and "pass" in r]
    if not rs:
        return None
    passes = sorted({r["pass"] for r in rs})
    have = collections.defaultdict(set)
    for r in rs:
        have[tuple(r.get(k) for k in RELAY_KEY[1:])].add(r["pass"])
    short = [{**dict(zip(RELAY_KEY[1:], k)), "passes": sorted(p)} for k, p in sorted(have.items(), key=str) if len(p) < len(passes)]
    return {"passes": passes, "configs": len(have), "short": short}


def by_medium(rows, group, key, host=None):
    d = collections.defaultdict(dict)
    for r in rows:
        if r.get("group") == group and r.get("test") == "relay" and (host is None or r["host"] == host):
            d[r[key]][r["medium"]] = r
    out = []
    for k in sorted(d):
        m = d[k]
        if len(m) < 3:
            continue
        out.append({key: k, "ok": all(m[x]["ok"] for x in m),
                    **{x: {"gb_s": m[x]["gb_s"], "cycles": m[x]["cycles_max"], "bytes": m[x]["bytes"]}
                       for x in ("dram", "scp", "hop")},
                    "scp_over_dram": m["scp"]["gb_s"] / m["dram"]["gb_s"],
                    "hop_over_dram": m["hop"]["gb_s"] / m["dram"]["gb_s"]})
    return out


def power(dirname):
    tp = os.path.join(dirname, "telemetry.jsonl")
    if os.path.exists(tp + ".gz"):
        tel = [json.loads(l) for l in gzip.open(tp + ".gz", "rt") if l.startswith("{")]
    elif os.path.exists(tp):
        tel = [json.loads(l) for l in open(tp) if l.startswith("{")]
    else:
        return None
    runs = [json.loads(l) for l in open(os.path.join(dirname, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    f = {k: np.array([(s[p][k][0] if p else s[k]) for s in tel])   # rails are [avg, min, max]
         for k, p in (("board_w", None), ("minion_w", "sp"), ("sram_w", "sp"), ("noc_w", "sp"))}
    f["die_c"] = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])   # whole-degree die reading
    # A single relay launch lasts a few milliseconds, less than one telemetry sample, so the window for a
    # medium is the whole burst of back-to-back launches carrying its label.
    span = {}
    for r in runs:
        a0, b0 = r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0
        lo, hi = span.get(r["label"], (a0, b0))
        span[r["label"]] = (min(lo, a0), max(hi, b0))
    busy = np.zeros(len(t), bool)
    for lo, hi in span.values():
        busy |= (t >= lo - 1.0) & (t <= hi + 1.0)
    idle = ~busy
    out = {"idle": {k: float(v[idle].mean()) for k, v in f.items()}}
    out["idle"]["n"] = int(idle.sum())
    out["media"] = []
    for med in ("dram", "scp", "hop"):
        rs = [r for r in runs if r["label"] == med]
        if not rs:
            continue
        lo, hi = span[med]
        m = (t >= lo + 1.0) & (t <= hi - 0.2)   # skip the first second, while the card settles
        if m.sum() < 3:
            continue
        # Bytes per second on the card, from the cycle counter, not the wall clock.
        total = float(sum(r["bytes"] for r in rs))
        devs = float(sum(r["cycles_max"] for r in rs)) / 0.6e9   # seconds the card was actually working
        wall = hi - lo                                            # wall seconds the burst occupied
        over = float(f["board_w"][m].mean() - out["idle"]["board_w"])
        # Energy above idle per byte moved. The gaps between launches draw idle power and so add nothing to
        # the numerator, which is why the wall span is the right multiplier here even at 83% duty.
        out["media"].append({"medium": med, "runs": len(rs), "bytes": total, "device_s": devs,
                             "wall_s": wall, "duty": devs / wall, "bytes_per_s": total / devs,
                             "over_idle_w": over, "pj_per_byte": over * wall / total * 1e12,
                             "n": int(m.sum()), **{k: float(v[m].mean()) for k, v in f.items()}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweeps", nargs="+")
    ap.add_argument("--power")
    ap.add_argument("--cards", help="comma-separated card order for 'cards' (default: sorted); the first card's rows "
                                    "are the rows' own fields")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = load(a.sweeps)
    rows = pass_means(raw)
    present = sorted({r["host"] for r in rows if "host" in r})
    order = [c.strip() for c in a.cards.split(",")] if a.cards else []
    out = {"cards": [c for c in order if c in present] + [c for c in present if c not in order]}
    for grp, key in (("headline", "medium"), ("intensity", "work"), ("size", "stage_bytes"),
                     ("stages", "stages"), ("shires", "shires")):
        if grp == "headline":
            out["headline"] = {r["host"]: {x["medium"]: x for x in rows
                                           if x.get("group") == "headline" and x["host"] == r["host"]}
                               for r in rows if r.get("group") == "headline"}
            continue
        out[grp] = by_medium(rows, grp, key, out["cards"][0])
        per = {c: {r[key]: {k: v for k, v in r.items() if k != key} for r in by_medium(rows, grp, key, c)}
               for c in out["cards"]}
        for r in out[grp]:
            r["by_card"] = {c: per[c][r[key]] for c in out["cards"] if r[key] in per[c]}
    # hop_distance is how many shire IDs back round the ring a slab comes from; mesh_hops is how far that is
    # on the mesh (every run in this group uses all 32 shires, so the ring is all 32 in ID order).
    out["distance"] = sorted([{"hop_distance": r["hop_distance"], "gb_s": r["gb_s"], "ok": r["ok"],
                               "mesh_hops": ring_hops(r["hop_distance"]) if r["shires"] == 32 else None}
                              for r in rows
                              if r.get("group") == "distance" and r["host"] == out["cards"][0]],
                             key=lambda r: r["hop_distance"])
    for d in out["distance"]:
        d["by_card"] = {r["host"]: {"gb_s": r["gb_s"], "stage_cycles": r["cycles_max"] / r["stages"]}
                        for r in rows if r.get("group") == "distance" and r["hop_distance"] == d["hop_distance"]}
        if d["mesh_hops"]:
            d["longest"] = longest_handoff(d["hop_distance"])
    layout, _ = shire_map()
    out["layout"] = {str(k): list(v) for k, v in layout.items()}
    out["empty"] = [list(e) for e in shire_empty()]
    out["ring"] = sorted(layout)
    out["repeats"] = {c: repeats(raw, c) for c in out["cards"]}
    # claims-v3 only: the hand-off at every ring offset d = 1..31, and each card's fit over the 16 geometries
    offs = sorted({r["hop_distance"] for r in rows if r.get("group") == "offsets" and r.get("test") == "relay"})
    if offs:
        out["offsets"] = []
        for dd in offs:
            bc = {r["host"]: {"gb_s": r["gb_s"], "stage_cycles": r["cycles_max"] / r["stages"], "passes": r.get("passes", 1)}
                  for r in rows if r.get("group") == "offsets" and r.get("test") == "relay" and r["hop_distance"] == dd}
            out["offsets"].append({"hop_distance": dd, "mesh_hops": ring_hops(dd), "longest": longest_handoff(dd),
                                   "ok": all(r["ok"] for r in rows if r.get("group") == "offsets" and r["hop_distance"] == dd),
                                   "by_card": {c: bc[c] for c in out["cards"] if c in bc}})
        out["offset_fit"] = {c: offset_fit(out["offsets"], c) for c in out["cards"]}
    cov = {c: coverage(raw, c) for c in out["cards"]}
    if any(cov.values()):
        out["coverage"] = cov
    out["bigsize"] = sorted([{"stage_bytes": r["stage_bytes"], "gb_s": r["gb_s"]}
                             for r in rows
                             if r.get("group") in ("size", "bigsize") and r.get("medium") == "dram"
                             and r["host"] == out["cards"][0]],
                            key=lambda r: r["stage_bytes"])
    if len(out["cards"]) > 1:   # added 26 Sep: every card's DRAM rate at the same size
        for b in out["bigsize"]:
            b["by_card"] = {c: r["gb_s"] for c in out["cards"] for r in rows
                            if r.get("group") in ("size", "bigsize") and r.get("medium") == "dram" and r.get("test") == "relay"
                            and r["host"] == c and r["stage_bytes"] == b["stage_bytes"]}
    out["probe"] = [{k: r[k] for k in ("method_name", "remote_words_wrong", "ok", "host", "pass") if k in r}
                    for r in rows if r.get("group") == "probe"]
    if a.power:
        out["power"] = power(a.power)
    json.dump(out, open(a.out, "w"), indent=1)

    h = out["headline"][out["cards"][0]]
    print("headline, 1 MB per shire per stage, 8 stages, one add per element:")
    for m in ("dram", "scp", "hop"):
        print(f"  {m:5s} {h[m]['gb_s']:8.1f} GB/s  shire 0 ends holding {h[m]['shire0_final']:5.1f}  ok={h[m]['ok']}")
    print(f"  own scratchpad {h['scp']['gb_s'] / h['dram']['gb_s']:.1f}x DRAM; "
          f"next shire {h['hop']['gb_s'] / h['dram']['gb_s']:.1f}x DRAM")
    if out.get("power"):
        p = out["power"]
        print(f"\nenergy (idle {p['idle']['board_w']:.2f} W):")
        for m in p["media"]:
            print(f"  {m['medium']:5s} {m['bytes_per_s'] / 1e9:8.1f} GB/s on the card  "
                  f"{m['over_idle_w']:5.2f} W over idle  {m['pj_per_byte']:7.2f} pJ/byte  "
                  f"(duty {100 * m['duty']:.0f}%)")
        d = next(m for m in p["media"] if m["medium"] == "dram")
        for m in p["media"]:
            if m["medium"] != "dram":
                print(f"  {m['medium']} uses {d['pj_per_byte'] / m['pj_per_byte']:.0f}x less energy per byte than DRAM")


if __name__ == "__main__":
    main()
