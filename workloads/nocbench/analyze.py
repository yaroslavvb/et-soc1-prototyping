#!/usr/bin/env python3
"""Summarize nocbench results into the numbers and chart data used by the report.

    python3 workloads/nocbench/analyze.py docs/reports/data/2026-09-18-nocbench-aifoundry2 \
        [--memhier docs/reports/data/2026-09-18-memhier-aifoundry2] [--search] [--reruns RERUNS_JSON] [--embed REPORT_HTML]

The data directory holds the NOCBENCH lines of each run (*.jsonl, from run_lab.sh), clock.csv (minion clock
and board power sampled during those runs) and energy-*/results.json (run_energy.py, one directory per run).
--memhier: the memory-hierarchy data, for its scratchpad latency rows and the 600 MHz bandwidth of a remote
    scratchpad TensorLoad (the reference row of the energy chart).
--search: 12 simulated-annealing restarts from random layouts (about 30 s); records each restart.
--reruns: the energy manual's pooled re-runs of these rings (default docs/reports/data/2026-09-23-energy-manual/
    reruns.json), embedded with their fit against the mean hop count (pooled, and per card over the rings both cards
    kept) and, per card, the range of watts over idle of the ring bursts behind them (re-reduced from the rerun
    directories the file names, with tools/ettelem/analyze_reruns.py).

The shire layout: marty1885 inferred where each logical shire sits on the physical 6x6 mesh from
shire-to-shire bandwidth (clehaxze.tw, "Investigating the ET-SoC-1 NoC", 2026-04-27). This script checks it
against latency on this card: every round-trip time should be a + b * (Manhattan distance), and it also
searches for the best grid placement from scratch, without that map, to see whether the data picks the same one.
"""
import argparse
import bisect
import glob
import json
import math
import os
import random
import re
import statistics

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
RERUNS = os.path.join(ROOT, "docs", "reports", "data", "2026-09-23-energy-manual", "reruns.json")

# marty1885's physical (x, y) of each logical compute shire on the 6x6 mesh. The four cells without a compute
# shire are (0,3), (0,4), (0,5) and (5,3); his bandwidth data shows (5,3) routes traffic.
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
EMPTY = [(0, 3), (0, 4), (0, 5), (5, 3)]


def _load_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hops(a, b, layout=MARTY):
    (xa, ya), (xb, yb) = layout[a], layout[b]
    return abs(xa - xb) + abs(ya - yb)


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line.startswith("NOCBENCH "):
            out.append(json.loads(line.split(" ", 1)[1]))
    return out


def load_clock(path):
    """(epoch_ms, MHz) samples from run_lab.sh's clock.csv, sorted."""
    rows = []
    if os.path.exists(path):
        for line in open(path):
            parts = line.strip().split(",")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1]:
                rows.append((int(parts[0]), float(parts[1])))
    return sorted(rows)


class Clocks:
    """Minion clock during a launch: the median service-processor sample inside it, else the nearest one,
    else the launch's own estimate (its longest kernel's cycles over its wall time)."""

    def __init__(self, samples):
        self.t = [s[0] for s in samples]
        self.mhz = [s[1] for s in samples]

    def ghz(self, launch):
        if not self.t:
            return launch.get("ghz") or 0.6
        t0, t1 = launch["t_start_ms"], launch.get("t_end_ms", launch["t_start_ms"])
        i0, i1 = bisect.bisect_left(self.t, t0), bisect.bisect_right(self.t, t1)
        inside = self.mhz[i0:i1]
        if inside:
            return statistics.median(inside) / 1000
        j = min(range(len(self.t)), key=lambda k: abs(self.t[k] - (t0 + t1) / 2))
        return self.mhz[j] / 1000


def pairs_with_launch(rows):
    """Attach to every pair line the launch line printed before it."""
    launch = None
    for r in rows:
        if r.get("kind") == "launch":
            launch = r
        elif r.get("kind") == "pair":
            r["launch"] = launch
            yield r


def fit_line(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    A = np.vstack([np.ones_like(x), x]).T
    (a, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = a + b * x
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum()) or 1e-12
    return float(a), float(b), 1 - ss_res / ss_tot, float(np.abs(y - pred).max())


def search_layout(shires, lat, iters=60000, restarts=12, seed=1):
    """Simulated annealing: place the shires on a 6x6 grid so that latency = a + b * Manhattan distance
    fits best. `lat` maps (i, j) with i < j to a latency. Returns (cost, layout, restarts): the best restart's
    cost and layout, and [cost, same hop distances as marty1885's map] for every restart."""
    idx = {s: k for k, s in enumerate(shires)}
    pairs = sorted(lat)
    I = np.array([idx[i] for i, _ in pairs])
    J = np.array([idx[j] for _, j in pairs])
    y = np.array([lat[p] for p in pairs], float)
    cells = [(x, yy) for yy in range(6) for x in range(6)]
    rng = random.Random(seed)

    def cost(pos):
        d = np.abs(pos[I, 0] - pos[J, 0]) + np.abs(pos[I, 1] - pos[J, 1])
        A = np.vstack([np.ones_like(d), d]).T.astype(float)
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return float(((y - A @ coef) ** 2).sum())

    best = (math.inf, None)
    runs = []
    for _ in range(restarts):
        order = cells[:]
        rng.shuffle(order)
        slots = order  # slots[k] = cell of shire k for k < n; the rest are empty
        pos = np.array(slots[: len(shires)])
        cur = cost(pos)
        T = cur / 50 + 1e-9
        for it in range(iters):
            a, b = rng.randrange(36), rng.randrange(36)
            if a == b or (a >= len(shires) and b >= len(shires)):
                continue
            slots[a], slots[b] = slots[b], slots[a]
            pos = np.array(slots[: len(shires)])
            new = cost(pos)
            if new <= cur or rng.random() < math.exp((cur - new) / T):
                cur = new
            else:
                slots[a], slots[b] = slots[b], slots[a]
            T *= 0.9998
        found = {s: tuple(slots[k]) for k, s in enumerate(shires)}
        runs.append([round(cur, 1), same_distances(found, MARTY, shires)])
        if cur < best[0]:
            best = (cur, found)
    return best[0], best[1], runs


def same_distances(la, lb, shires):
    return all(hops(i, j, la) == hops(i, j, lb) for i in shires for j in shires if i < j)


def one_hop_ring(layout=MARTY):
    """A cycle through every compute shire in which each step is one mesh hop (depth-first search that tries
    the neighbour with the fewest free neighbours first). Returns the shire order starting at shire 0."""
    nbr = {s: [t for t in layout if t != s and hops(s, t, layout) == 1] for s in layout}

    def dfs(path, seen):
        if len(path) == len(layout):
            return path if hops(path[-1], path[0], layout) == 1 else None
        for t in sorted(nbr[path[-1]], key=lambda u: len([v for v in nbr[u] if v not in seen])):
            if t not in seen:
                seen.add(t)
                found = dfs(path + [t], seen)
                if found:
                    return found
                seen.discard(t)
        return None

    return dfs([0], {0})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data_dir")
    p.add_argument("--memhier", help="memhier data directory, for its scratchpad latency rows")
    p.add_argument("--embed", metavar="REPORT_HTML")
    p.add_argument("--search", action="store_true", help="also search for the layout from scratch (slow)")
    p.add_argument("--reruns", default=RERUNS, help="the energy manual's reruns.json (pooled re-runs of these rings)")
    args = p.parse_args()
    d = args.data_dir
    runs = {os.path.basename(f)[:-6]: load(f) for f in sorted(glob.glob(os.path.join(d, "*.jsonl")))}
    clocks = Clocks(load_clock(os.path.join(d, "clock.csv")))
    data = {"layout": {str(s): xy for s, xy in MARTY.items()}, "empty_cells": EMPTY}

    bad = {name: sum(1 for r in rs if r.get("ok") is False) for name, rs in runs.items()}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        print(f"WARNING: lines with ok=false: {bad}")

    # Scratchpad rows from memhier (load latency, cycles) against the map.
    if args.memhier:
        rows = {}
        for f in glob.glob(os.path.join(args.memhier, "chase-scp-map*.jsonl")):
            m = re.search(r"from(\d+)", f)
            src = int(m.group(1)) if m else 0
            rows[src] = {json.loads(l.split(" ", 1)[1] if l.startswith("MEMHIER") else l)["scp_shire"]:
                         json.loads(l.split(" ", 1)[1] if l.startswith("MEMHIER") else l)["cycles_per_load"]
                         for l in open(f) if l.strip()}
        data["scp_rows"] = {}
        for src, row in sorted(rows.items()):
            xs = [hops(src, t) for t in row if t != src]
            ys = [row[t] for t in row if t != src]
            a, b, r2, worst = fit_line(xs, ys)
            print(f"scratchpad loads from shire {src:2d}: {a:6.1f} + {b:5.2f} x hops  (r2 {r2:.4f}, worst {worst:.1f} cycles)")
            data["scp_rows"][str(src)] = {"a": a, "b": b, "r2": r2, "points": [[hops(src, t), row[t], t] for t in row if t != src]}
        # Rows 0 and 7 ran at 600 MHz and row 31 at 800 MHz (its per-hop slope is 16/12 of theirs). If a load costs
        # c minion cycles + (t0 + t_hop * hops) ns of fixed-time mesh transit, then per clock f (GHz):
        # a(f) = c + t0 * f and b(f) = t_hop * f. Two clocks give c, t0 and t_hop.
        fast, slow = data["scp_rows"].get("31"), data["scp_rows"].get("0")
        if fast and slow:
            f_slow, f_fast = 0.6, 0.6 * fast["b"] / slow["b"]
            t_hop = slow["b"] / f_slow
            t0 = (fast["a"] - slow["a"]) / (f_fast - f_slow)
            c = slow["a"] - t0 * f_slow
            print(f"scratchpad load = {c:.1f} minion cycles + ({t0:.1f} ns + {t_hop:.2f} ns x hops) of mesh time "
                  f"(row 31 ran at {f_fast * 1000:.0f} MHz)")

    # Round trips by distance class: pingpong, credits, flags.
    classes = {}
    for name in ("classes-pingpong", "classes-fcc", "classes-flag"):
        for r in pairs_with_launch(runs.get(name, [])):
            ghz = clocks.ghz(r["launch"])
            if r["a_shire"] == r["b_shire"]:
                cls = "same neighbourhood" if r["a_minion"] // 8 == r["b_minion"] // 8 else "same shire"
                h = 0
            else:
                h = hops(r["a_shire"], r["b_shire"])
                cls = f"{h} hops"
            key = f"{r['a_shire']}.{r['a_minion']}-{r['b_shire']}.{r['b_minion']}"
            classes.setdefault(r["mode"], []).append({
                "pair": key, "class": cls, "hops": h, "rtt_cycles": r["cycles_per_iter"], "ghz": ghz,
                "rtt_ns": r["cycles_per_iter"] / ghz, "ok": r["ok"]})
    for mode, rows in classes.items():
        print(f"\n{mode} round trips by distance:")
        for c in rows:
            print(f"  {c['pair']:10s} {c['class']:20s} {c['rtt_cycles']:8.1f} cycles  {c['rtt_ns']:7.1f} ns  @{c['ghz']:.3f} GHz")
    data["classes"] = classes

    # Shire-to-shire matrices: fit against the map, and optionally search.
    matrices = {}
    for name, rs in runs.items():
        if not name.startswith("matrix-"):
            continue
        pts = list(pairs_with_launch(rs))
        if not pts:
            continue
        ghz = clocks.ghz(pts[0]["launch"])
        lat = {(min(r["a_shire"], r["b_shire"]), max(r["a_shire"], r["b_shire"])): r["cycles_per_iter"] for r in pts}
        xs = [hops(i, j) for i, j in lat]
        ys = list(lat.values())
        a, b, r2, worst = fit_line(xs, ys)
        print(f"\n{name}: {len(lat)} pairs @{ghz:.3f} GHz: rtt = {a:.1f} + {b:.2f} x hops cycles "
              f"= {a / ghz:.1f} + {b / ghz:.2f} x hops ns  (r2 {r2:.4f}, worst residual {worst:.1f} cycles)")
        by_h = {}
        for (i, j), v in lat.items():
            by_h.setdefault(hops(i, j), []).append(v)
        print("  by hops: " + ", ".join(f"{h}: {statistics.median(v):.1f} (n={len(v)})" for h, v in sorted(by_h.items())))
        print(f"  range {min(ys) / ghz:.0f}-{max(ys) / ghz:.0f} ns, median {statistics.median(ys) / ghz:.0f} ns")
        matrices[name] = {"ghz": ghz, "a": a, "b": b, "r2": r2, "worst": worst,
                          "pairs": [[i, j, v] for (i, j), v in sorted(lat.items())]}
        if name == "matrix-pingpong-c32":
            # 1 KB round trips: +12 cycles per hop up to a knee, steeper beyond it. Two lines, split at the knee that
            # fits best (each side needs at least two hop counts).
            best = None
            for k in range(2, max(by_h) - 1):
                near = [(h, v) for (i, j), v in lat.items() for h in [hops(i, j)] if h <= k]
                far = [(h, v) for (i, j), v in lat.items() for h in [hops(i, j)] if h > k]
                f1, f2 = fit_line(*zip(*near)), fit_line(*zip(*far))
                sse = sum((v - f1[0] - f1[1] * h) ** 2 for h, v in near) + sum((v - f2[0] - f2[1] * h) ** 2 for h, v in far)
                if best is None or sse < best[0]:
                    best = (sse, k, f1, f2)
            _, k, f1, f2 = best
            med = {h: statistics.median(v) for h, v in by_h.items()}
            matrices[name]["knee"] = {"hops": k, "near": {"a": f1[0], "b": f1[1], "r2": f1[2], "worst": f1[3]},
                                      "far": {"a": f2[0], "b": f2[1], "r2": f2[2], "worst": f2[3]},
                                      "median_by_hops": {str(h): med[h] for h in sorted(med)}}
            print(f"  two lines, knee after {k} hops: {f1[0]:.1f} + {f1[1]:.2f} x hops up to {k} (worst {f1[3]:.1f}), "
                  f"{f2[0]:.1f} + {f2[1]:.2f} x hops beyond (worst {f2[3]:.1f}); step {k}->{k + 1} hops: "
                  f"{med[k + 1] - med[k]:.1f} cycles")
        if args.search and name == "matrix-pingpong":
            shires = sorted({s for p in lat for s in p})
            best_cost, found, restarts = search_layout(shires, lat)
            same = same_distances(found, MARTY, shires)
            print(f"  layout search from scratch: residual {best_cost:.1f}; same hop distances as marty1885's map: {same}")
            print(f"  every restart [residual, same distances]: {restarts}")
            matrices[name]["search"] = {"cost": best_cost, "same_as_marty": same, "restarts": restarts,
                                        "layout": {str(s): xy for s, xy in found.items()}}
    data["matrices"] = matrices

    # Minion pairs inside one shire: which pairs are on the fast local network (one round trip per pair).
    intra = {}
    for name in ("intra-pingpong", "intra-pingpong-s24"):
        pts = list(pairs_with_launch(runs.get(name, [])))
        if not pts:
            continue
        fast = sorted([r["a_minion"], r["b_minion"]] for r in pts if r["cycles_per_iter"] < 90)
        slow = [r["cycles_per_iter"] for r in pts if r["cycles_per_iter"] >= 90]
        shire = pts[0]["a_shire"]
        intra[str(shire)] = {"fast_pairs": fast, "fast_cycles": statistics.median(r["cycles_per_iter"] for r in pts
                                                                                  if r["cycles_per_iter"] < 90),
                             "other_cycles": statistics.median(slow), "other_min": min(slow), "other_max": max(slow),
                             "n_fast": len(fast), "n_other": len(slow)}
        print(f"\nshire {shire}: {len(fast)} fast pairs at {intra[str(shire)]['fast_cycles']:.0f} cycles, "
              f"{len(slow)} others at {min(slow):.0f}-{max(slow):.0f}: {fast}")

    # Message size: round trip (pingpong) and per-message time (stream) against COUNT.
    sizes = {}
    for name in ("counts-pingpong", "counts-stream"):
        for r in pairs_with_launch(runs.get(name, [])):
            ghz = clocks.ghz(r["launch"])
            key = f"{r['a_shire']}.{r['a_minion']}-{r['b_shire']}.{r['b_minion']}"
            sizes.setdefault(r["mode"], {}).setdefault(key, []).append(
                {"count": r["count"], "bytes": r["count"] * 32, "cycles": r["cycles_per_iter"], "ghz": ghz})
    for mode, per in sizes.items():
        print(f"\n{mode} by message size (cycles per {'round trip' if mode == 'pingpong' else 'message'}):")
        for key, pts in per.items():
            pts.sort(key=lambda q: q["count"])
            a, b, r2, _ = fit_line([q["count"] for q in pts], [q["cycles"] for q in pts])
            print(f"  {key:10s} " + " ".join(f"{q['bytes']}B:{q['cycles']:.0f}" for q in pts)
                  + f"   fit {a:.1f} + {b:.2f} x COUNT (r2 {r2:.4f})")
            if mode == "stream":
                print(f"  {'':10s} one link: " + " ".join(f"{q['bytes']}B:{q['bytes'] / q['cycles'] * q['ghz']:.2f}GB/s"
                                                        for q in pts if q["bytes"] in (1024, 4064)))
    data["sizes"] = sizes

    # Combine functions.
    functs = {}
    for name, rs in runs.items():
        if name.startswith("functs-"):
            for r in pairs_with_launch(rs):
                key = f"{r['a_shire']}.{r['a_minion']}-{r['b_shire']}.{r['b_minion']}"
                functs.setdefault(name[7:], []).append({"pair": key, "count": r["count"], "cycles": r["cycles_per_iter"]})
    if functs:
        print("\ncombine functions (round-trip cycles):")
        for f, rows in functs.items():
            print(f"  {f:5s} " + "  ".join(f"{q['pair']} c{q['count']}: {q['cycles']:.1f}" for q in rows))

    # Allreduce trees.
    allreduce = {}
    for name, rs in runs.items():
        if "allreduce-" in name:  # allreduce-*: trees inside shires; xallreduce-*: trees across shires
            for r in rs:
                if r.get("kind") == "allreduce":
                    ghz = clocks.ghz(r)
                    allreduce.setdefault(str(r["count"]), []).append(
                        {"levels": r["levels"], "minions": r["minions"], "trees": r.get("trees", 1),
                         "cycles": r["cycles_per_iter"], "ghz": ghz, "ns": r["cycles_per_iter"] / ghz, "ok": r["ok"]})
    if allreduce:
        print("\nallreduce (TensorReduce up + TensorBroadcast down), cycles per allreduce:")
        for c, rows in allreduce.items():
            rows.sort(key=lambda q: (q["minions"], q["trees"]))
            print(f"  COUNT {c:>2s}: " + ", ".join(f"{q['minions']}x{q['trees']}: {q['cycles']:.0f} ({q['ns']:.0f} ns)"
                                                   for q in rows))
    data["allreduce"] = allreduce

    # Barriers.
    barriers = []
    for name, rs in runs.items():
        if name.startswith("barrier-"):
            for r in rs:
                if r.get("kind") == "barrier":
                    ghz = clocks.ghz(r)
                    barriers.append({"name": name, "scope": r["scope"], "participants": r["participants"],
                                     "cycles": r["cycles_per_iter_mean"], "ns": r["cycles_per_iter_mean"] / ghz, "ghz": ghz})
    for b in barriers:
        print(f"barrier {b['name']:16s} {b['participants']:5d} minions: {b['cycles']:8.1f} cycles, {b['ns']:7.1f} ns")

    # The in-shire primitives a TensorSend layout is built from (the page's layout diagram): the round trip on a
    # tree edge and elsewhere in the shire, the tree's edges in one neighbourhood, a 32-minion barrier with every
    # shire doing it at once, and a 32-minion allreduce (32 B, one tree).
    prim = {}
    if "0" in intra:
        prim["tree_hop"] = intra["0"]["fast_cycles"]
        prim["other_hop"] = intra["0"]["other_cycles"]
        prim["tree_pairs"] = [p_ for p_ in intra["0"]["fast_pairs"] if max(p_) < 8]
    sb = [b for b in barriers if b["name"] == "barrier-shire32"]
    if sb:
        prim["shire_barrier"] = sb[0]["cycles"]
    a32 = [q for q in allreduce.get("1", []) if q["minions"] == 32 and q["trees"] == 1]
    if a32:
        prim["allreduce32"] = a32[0]["cycles"]
    data["primitives"] = prim
    print(f"primitives for the layout diagram: {prim}")

    # Energy per byte of ring traffic, against the local idle next to each configuration, averaged over runs.
    energy_runs = [json.load(open(ef)) for ef in sorted(glob.glob(os.path.join(d, "energy-*", "results.json")))]
    energy = {"runs": len(energy_runs), "idle_w": [e["idle_w"] for e in energy_runs], "configs": {}}
    if energy_runs:
        print(f"\nenergy ({len(energy_runs)} runs, idle {[round(w, 2) for w in energy['idle_w']]} W):")
        for name in energy_runs[0]["results"]:
            rs = [e["results"][name] for e in energy_runs if name in e["results"]]
            k = int(name[6:].split("-")[0]) if name.startswith("xshire") else 0
            mean_hops = sum(hops(s_, (s_ + k) % 32) for s_ in range(32)) / 32 if k else 0.0
            pj = [r.get("pj_per_byte_vs_local_idle") for r in rs]
            c = {"what": rs[0]["what"], "gb_per_s": statistics.mean(r["gb_per_s"] for r in rs),
                 "above_idle_w": statistics.mean(r.get("above_local_idle_w", r["above_idle_w"]) for r in rs),
                 "pj_per_byte": statistics.mean(pj) if None not in pj else None, "pj_runs": pj,
                 "mean_hops": mean_hops, "count": 4 if name.endswith("c4") else 32}
            energy["configs"][name] = c
            print(f"  {name:11s} {c['gb_per_s']:8.1f} GB/s  +{c['above_idle_w']:5.2f} W  "
                  + (f"{c['pj_per_byte']:6.2f} pJ/B {['%.2f' % v for v in pj]}" if c["pj_per_byte"] else "")
                  + (f"  mean hops {mean_hops:.2f}" if k else ""))
        mesh = [(c["mean_hops"], c["pj_per_byte"]) for n, c in energy["configs"].items()
                if n.startswith("xshire") and c["count"] == 32]
        if len(mesh) >= 3:
            a, b, r2, _ = fit_line([m[0] for m in mesh], [m[1] for m in mesh])
            energy["mesh_fit"] = {"a": a, "b": b, "r2": r2}
            print(f"  1 KB messages over the mesh: {a:.1f} + {b:.2f} pJ/B per hop (r2 {r2:.3f})")
    data["energy"] = energy

    # The same rings re-run on 23 September, three passes on each of two cards, pooled by the energy manual
    # (tools/ettelem/analyze_reruns.py): mean and pass range per ring, and the fit over the six 1 KB mesh rings
    # against their mean hop count. The references are the manual's per-level reads at a pinned 600 MHz.
    if args.reruns and os.path.exists(args.reruns):
        rr = json.load(open(args.reruns))
        rings = {k: {q: v[q] for q in ("mean", "lo", "hi", "n")} for k, v in rr["rings_pj_per_byte"].items()}
        mesh = [(energy["configs"][k]["mean_hops"], v["mean"]) for k, v in rings.items()
                if k.startswith("xshire") and not k.endswith("-c4") and k in energy["configs"]]
        a, b, r2, _ = fit_line([m[0] for m in mesh], [m[1] for m in mesh])
        levels = {k: {q: rr["levels_pj_per_byte"][k][q] for q in ("mean", "lo", "hi")} for k in ("l2", "scp-remote", "dram")}
        data["reruns"] = {"rings": rings, "mesh_fit": {"a": a, "b": b, "r2": r2, "n": len(mesh)}, "levels": levels}
        print(f"re-run on two cards (23 September): 1 KB messages over the mesh {a:.2f} + {b:.2f} pJ/B per mean hop "
              f"(r2 {r2:.3f}, {len(mesh)} rings); inside a shire " + ", ".join(
                  f"{k} {rings[k]['mean']:.2f}" for k in ("pair", "neigh", "shire", "shire-c4") if k in rings))
        # The cards differ in the mesh slope, so fit each card's own ring means, over the 1 KB mesh rings both cards
        # kept (aifoundry2's s <-> s+16 passes were dropped: that ring starves its service processor).
        pc = {k: v.get("per_card", {}) for k, v in rr["rings_pj_per_byte"].items()
              if k.startswith("xshire") and not k.endswith("-c4") and k in energy["configs"]}
        cards = sorted({h for v in pc.values() for h in v})
        common = [k for k, v in pc.items() if all(h in v for h in cards)]
        data["reruns"]["mesh_fit_per_card"] = {}
        for h in cards:
            a_, b_, r2_, _ = fit_line([energy["configs"][k]["mean_hops"] for k in common], [pc[k][h]["mean"] for k in common])
            data["reruns"]["mesh_fit_per_card"][h] = {"a": a_, "b": b_, "r2": r2_, "n": len(common)}
            print(f"  {h}: {a_:.2f} + {b_:.2f} pJ/B per mean hop (r2 {r2_:.3f}, the {len(common)} rings both cards kept)")
        # Watts over idle of the same ring bursts, per card: each pass reduced and filtered as the energy manual does
        # (tools/ettelem/analyze_reruns.py), so the range covers exactly the bursts behind the pJ/B above.
        ar = _load_module(os.path.join(ROOT, "tools", "ettelem", "analyze_reruns.py"), "analyze_reruns")
        watts = {}
        for rd in rr.get("dirs", []):
            for pd in sorted(glob.glob(os.path.join(ROOT, rd, "rl-pass*[0-9]"))):
                if not ar.complete(pd):
                    continue
                for lab, b in ar.reduce_dir(pd).items():
                    if lab in rings and b["clock_moved_frac"] <= 0.02 and b["sampler_median_ms"] <= 60:
                        watts.setdefault(ar.host_of(rd), []).append(b["over_idle_w"])
        data["reruns"]["over_idle_w_per_card"] = {h: {"lo": min(v), "hi": max(v), "n": len(v)} for h, v in sorted(watts.items())}
        print("  over idle, every ring burst kept: " + ", ".join(
            f"{h} {min(v):.2f}-{max(v):.2f} W ({len(v)})" for h, v in sorted(watts.items())))

    # Bulk data between shires for comparison: every minion streaming 1 KB TensorLoads from the scratchpad 16 shire
    # IDs away (the memory-hierarchy probe), median GB/s of its launches at 600 MHz (as scripts/ridge-points.py).
    if args.memhier:
        runs_mh = [json.loads(l) for d_ in ("energy", "energy2") for l in open(os.path.join(args.memhier, d_, "runs.jsonl"))
                   if l.strip()]
        at600 = [r["bytes"] / r["wall_s"] / 1e9 for r in runs_mh if r.get("config") == "scp-remote"
                 and r.get("launch", -1) >= 0 and r["bytes"] > 0 and 0.59 <= r["implied_ghz"] <= 0.61]
        if at600:
            data["scp_remote_gbps_600"] = statistics.median(at600)
            print(f"TensorLoad from the scratchpad 16 shire IDs away: {statistics.median(at600):.0f} GB/s "
                  f"({len(at600)} launches at 600 MHz)")

    # Latency with 16 cross-shire pairs at once, against the same pairs one at a time.
    loaded = {}
    for name in ("isolated-pairs", "loaded-pairs"):
        for r in pairs_with_launch(runs.get(name, [])):
            loaded.setdefault(name, []).append([r["a_shire"], r["b_shire"], hops(r["a_shire"], r["b_shire"]),
                                                r["count"], r["cycles_per_iter"]])
    if loaded.get("isolated-pairs") and loaded.get("loaded-pairs"):
        iso = {(a, b, c): v for a, b, h, c, v in loaded["isolated-pairs"]}
        worst = max(abs(v / iso[(a, b, c)] - 1) for a, b, h, c, v in loaded["loaded-pairs"] if (a, b, c) in iso)
        print(f"\n16 cross-shire pairs at once vs one at a time: worst change {worst * 100:.1f}%")

    ring = one_hop_ring()
    print("one-hop ring through all 32 shires: " + " ".join(map(str, ring)))
    print(f"shire-ID order 0..31 instead: {sum(hops(s_, s_ + 1) for s_ in range(31))} hops over 31 steps, "
          f"up to {max(hops(s_, s_ + 1) for s_ in range(31))}")

    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="nocbench-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one nocbench-data script tag")
        html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":")) + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded report data into {args.embed}")


if __name__ == "__main__":
    main()
