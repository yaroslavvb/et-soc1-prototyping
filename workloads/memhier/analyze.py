#!/usr/bin/env python3
"""Summarize memhier results into the numbers and chart data used by the report.

    python3 workloads/memhier/analyze.py docs/reports/data/2026-09-18-memhier-aifoundry2 \
        [--embed docs/reports/2026-09-18-et-soc1-memory-hierarchy.html]

The data directory holds the chase-*.jsonl files from memhier_host and energy/ from run_energy.py.
The script prints the plateau latency of each level (L3 and DRAM per clock: the governor ran some chases at
600 MHz and some at 800), the clock models of L3, DRAM and a remote scratchpad load, the scratchpad latency
matrix and the energy table (superseded, 18 September). With --embed it also replaces the JSON inside the
report's <script type="application/json" id="memhier-data"> tag with the chart data: the latency curves, every
L3 and DRAM chase with its clock, the clock models (fits, scp_model), the per-requester L3 latency, the scratchpad
matrix and marty1885's shire layout (imported from workloads/nocbench/analyze.py).
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _nocbench():
    """workloads/nocbench/analyze.py, for marty1885's shire layout (MARTY, EMPTY) and hops()."""
    spec = importlib.util.spec_from_file_location("nocbench_analyze", os.path.join(HERE, "..", "nocbench", "analyze.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

GHZ = 0.6  # minion base clock reported by DM_CMD_GET_ASIC_FREQUENCIES
# The governor's operating points on these cards are 600, 700 and 800 MHz (DVFS report); nothing runs outside them.
GHZ_MIN, GHZ_MAX = 0.6, 0.8
MIN_WALL_S = 0.01  # chases shorter than this are dominated by launch overhead
# Anatomy of a memory access, section 3 ("L3: 110 cycles plus 12 per hop", timed from shire 0 at 600 MHz): the L3
# model that workloads/memprobe/analyze.py uses. main() refits it from that report's summary.json when present.
ANATOMY_L3 = {"base": 110, "per_hop": 12}
ANATOMY_SUMMARY = os.path.join(HERE, "..", "..", "docs", "reports", "data", "2026-09-19-memprobe-aifoundry2", "summary.json")

# Working-set ranges (bytes) that sit on each plateau of the latency curve.
LEVELS = [
    ("L1", 0, 512),
    ("L2 read buffer", 768, 2048),
    ("L2 / local scratchpad", 4096, 512 * 1024),
    ("L3", 768 * 1024, 8 << 20),
    ("DRAM", 128 << 20, 1 << 40),
]


def point_ghz(r):
    """Clock during one chase: its cycles over its wall time, when the run is long enough to tell.

    The wall time includes the warm-up steps, which are most of the chase, so the estimate is approximate: it reads
    up to 5% off on most L3 and DRAM chases and 10-16% high on the 48 and 64 MB chains, and a chase whose clock
    changed during its warm-up gets a value in between. It is therefore kept inside the 600-800 MHz operating range.
    Runs shorter than MIN_WALL_S fall back to the 600 MHz base clock. That is also the right conversion for on-chip
    levels, whose latency in cycles does not change with the clock."""
    if r["wall_s"] >= MIN_WALL_S:
        ghz = r["cycles_per_load"] * (r["warm_steps"] + r["steps"]) / r["wall_s"] / 1e9
        if 0.55 <= ghz <= 0.95:
            return min(max(ghz, GHZ_MIN), GHZ_MAX)
    return GHZ


def op_point(r):
    """The operating point a chase ran at, 0.6 or 0.8 GHz: point_ghz() is approximate, so it only picks the side of
    700 MHz. No L3 or DRAM chase here ran at 700 MHz (their cycle counts fall into a 600 and an 800 MHz group)."""
    return 0.6 if point_ghz(r) < 0.7 else 0.8


def level_of(r):
    """'L3' for chains of 768 KB-8 MB, 'DRAM' for 128 MB and up, else None (on-chip levels, or the 16-64 MB chains,
    which mix L3 and DRAM hits)."""
    return "L3" if (768 << 10) <= r["size"] <= (8 << 20) else "DRAM" if r["size"] >= (128 << 20) else None


def fit_clock(fs, ys):
    """Least squares of cycles = c + t * f (f in GHz): c minion cycles that scale with the clock plus t ns that do not."""
    A = np.vstack([np.ones(len(fs)), np.asarray(fs, float)]).T
    (c, t), *_ = np.linalg.lstsq(A, np.asarray(ys, float), rcond=None)
    return float(c), float(t), float(np.abs(np.asarray(ys, float) - A @ np.array([c, t])).max())


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            out.append(json.loads(line.split(" ", 1)[1] if line.startswith("MEMHIER") else line))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data_dir")
    p.add_argument("--embed", metavar="REPORT_HTML")
    args = p.parse_args()
    d = args.data_dir

    rows = {os.path.basename(f)[:-6]: load(f) for f in glob.glob(os.path.join(d, "chase-*.jsonl"))}
    bad = [name for name, rs in rows.items() for r in rs if not r["ok"]]
    if bad:
        raise SystemExit(f"chases that failed the pointer check: {bad}")

    curves = {}
    for name, label in [("chase-dram", "shire 0"), ("chase-dram-sweep-from24", "shire 24"),
                        ("chase-scp-local", "local scratchpad, shire 0")]:
        if name in rows:
            # [bytes, cycles per load, ns at the chase's own clock, that clock in GHz]
            curves[label] = [[r["size"], round(r["cycles_per_load"], 2), round(r["cycles_per_load"] / point_ghz(r), 1),
                              round(point_ghz(r), 3)] for r in rows[name]]

    # Plateaus. On-chip levels are fixed in cycles; L3 and DRAM are part minion cycles and part fixed nanoseconds, so
    # they are summarised per operating point (600 or 800 MHz; nothing here ran at 700), never converted across.
    print(f"latency plateaus (cycles; on-chip levels in ns at {GHZ} GHz, L3 and DRAM at each chase's own clock):")
    plateaus = {}
    far = [r for rs in rows.values() for r in rs if r["where"] == "dram" and r["thread"] == 0 and level_of(r)]
    for level, lo, hi in LEVELS:
        if level in ("L3", "DRAM"):  # L3: every 768 KB-8 MB chain; DRAM: every chain of >= 128 MB; all runs and shires
            by = {}
            for r in far:
                if level_of(r) == level:
                    by.setdefault(op_point(r), []).append(r["cycles_per_load"])
            plateaus[level] = {}
            for g, v in sorted(by.items()):
                med = statistics.median(v)
                plateaus[level][f"{g * 1000:.0f}"] = {"median": med, "min": min(v), "max": max(v), "n": len(v)}
                print(f"  {level + ' at ' + f'{g * 1000:.0f} MHz':22s} median {med:7.1f}  range {min(v):6.1f}-{max(v):6.1f} cycles"
                      f"  = {med / g:6.1f} ns ({min(v) / g:.0f}-{max(v) / g:.0f})  n={len(v)}")
            continue
        vals = [c for label in ("shire 0", "shire 24") for s, c, _, _ in curves.get(label, []) if lo <= s <= hi]
        if not vals:
            continue
        plateaus[level] = {"median": statistics.median(vals), "min": min(vals), "max": max(vals), "n": len(vals)}
        print(f"  {level:22s} median {statistics.median(vals):7.1f}  range {min(vals):6.1f}-{max(vals):6.1f} cycles"
              f"  = {statistics.median(vals) / GHZ:6.1f} ns ({min(vals) / GHZ:.0f}-{max(vals) / GHZ:.0f})  n={len(vals)}")

    t1 = {r["size"]: r["cycles_per_load"] for r in rows.get("chase-dram-thread1", [])}
    if t1:
        print(f"hart 1: {t1}")

    matrix, raw = {}, {}
    for name, rs in rows.items():
        m = re.match(r"chase-scp-map(?:-from(\d+))?$", name)
        if m:
            src = int(m.group(1) or 0)
            raw[src] = [r["cycles_per_load"] for r in sorted(rs, key=lambda r: r["scp_shire"])]
            matrix[src] = [round(v, 1) for v in raw[src]]
    remote = [v for src, vals in matrix.items() for t, v in enumerate(vals) if t != src]
    if remote:
        print(f"scratchpad: local {matrix[0][0]:.1f} cycles; remote {min(remote):.0f}-{max(remote):.0f} cycles, "
              f"median {statistics.median(remote):.0f} ({len(remote)} pairs from sources {sorted(matrix)})")

    # Clock models. A remote scratchpad load is c minion cycles + (t0 + t_hop x hops) ns of mesh time: rows 0 and 31
    # ran at 600 and 800 MHz throughout, so their two lines against the hop count give c, t0 and t_hop
    # (the same derivation as workloads/nocbench/analyze.py).
    noc = _nocbench()
    hops = noc.hops
    scp_model = None
    lines = {}
    for src in (0, 31):
        if src in matrix:
            xs = [hops(src, t) for t in range(32) if t != src]
            ys = [raw[src][t] for t in range(32) if t != src]
            lines[src] = noc.fit_line(xs, ys)[:2]
    if len(lines) == 2:
        (a0, b0), (a31, b31) = lines[0], lines[31]
        f_fast = 0.6 * b31 / b0
        t_hop = b0 / 0.6
        t0 = (a31 - a0) / (f_fast - 0.6)
        # fit_rows: the rows the four numbers come from; the other rows are the out-of-sample test of the model.
        scp_model = {"c": round(a0 - t0 * 0.6, 2), "t0": round(t0, 2), "hop": round(t_hop, 2), "fit_rows": [0, 31]}
        near = n = near_out = n_out = 0
        for src, vals in raw.items():
            for t, v in enumerate(vals):
                if t == src:
                    continue
                pred = [scp_model["c"] + (scp_model["t0"] + scp_model["hop"] * hops(src, t)) * g for g in (0.6, 0.7, 0.8)]
                ok = min(abs(v - q) for q in pred) <= 1
                n += 1
                near += ok
                if src not in scp_model["fit_rows"]:
                    n_out += 1
                    near_out += ok
        print(f"remote scratchpad load = {scp_model['c']:.2f} minion cycles + ({scp_model['t0']:.2f} ns + "
              f"{scp_model['hop']:.2f} ns x hops), fitted to rows 0 and 31; {near} of {n} loads within 1 cycle of it at the "
              f"nearest operating point, {near_out} of {n_out} in the rows it was not fitted to")

    # L3: shire 24 is the one requester measured at both clocks, so its chases give c cycles + t ns; t is the fixed
    # part (mesh at 400 MHz, slice), and 20 ns of it per hop of the mean trip from the requester to the 32 slices.
    fits = {}
    mean_hops = {s: sum(hops(s, t) for t in noc.MARTY) / len(noc.MARTY) for s in noc.MARTY}
    l3_by_requester = {}
    for s in sorted({r["chaser_shire"] for r in far if level_of(r) == "L3"}):
        v = [r["cycles_per_load"] for r in far if level_of(r) == "L3" and r["chaser_shire"] == s and op_point(r) == 0.6]
        if v:
            l3_by_requester[str(s)] = round(statistics.median(v), 1)
    s24 = [r for r in far if level_of(r) == "L3" and r["chaser_shire"] == 24]
    if scp_model and len({op_point(r) for r in s24}) == 2:
        c, t, worst = fit_clock([op_point(r) for r in s24], [r["cycles_per_load"] for r in s24])
        ns0 = t - scp_model["hop"] * mean_hops[24]
        fits["L3"] = {"cycles": round(c, 1), "ns0": round(ns0, 1), "ns_per_hop": round(scp_model["hop"], 1),
                      "mean_hops": {str(s): mean_hops[s] for s in sorted(int(k) for k in l3_by_requester)},
                      "fit_on": "shire 24 at 600 and 800 MHz"}
        res = [r["cycles_per_load"] - (c + (ns0 + scp_model["hop"] * mean_hops[r["chaser_shire"]]) * op_point(r))
               for r in far if level_of(r) == "L3"]
        fits["L3"]["worst_residual"] = round(max(abs(x) for x in res), 2)
        fits["L3"]["n"] = len(res)
        print(f"L3 = {c:.1f} minion cycles + ({ns0:.1f} ns + {scp_model['hop']:.1f} ns x mean hops to the 32 slices) "
              f"(fit on shire 24, {t:.1f} ns there); all {len(res)} L3 chases within {max(abs(x) for x in res):.2f} cycles")
        for s, v in l3_by_requester.items():
            pred = c + (ns0 + scp_model["hop"] * mean_hops[int(s)]) * 0.6
            print(f"  from shire {s:>2s}: mean {mean_hops[int(s)]:.2f} hops, {v:.1f} cycles at 600 MHz, model {pred:.1f}")
    dram = [r for r in far if level_of(r) == "DRAM"]
    if len({op_point(r) for r in dram}) == 2:
        c, t, worst = fit_clock([op_point(r) for r in dram], [r["cycles_per_load"] for r in dram])
        fits["DRAM"] = {"cycles": round(c, 1), "ns": round(t, 1), "n": len(dram), "worst_residual": round(worst, 1)}
        print(f"DRAM = {c:.1f} minion cycles + {t:.1f} ns (n={len(dram)}, worst residual {worst:.1f} cycles): "
              + ", ".join(f"{c / g + t:.0f} ns at {g * 1000:.0f} MHz" for g in (0.6, 0.7, 0.8)))

    anatomy = dict(ANATOMY_L3)
    if os.path.exists(ANATOMY_SUMMARY):
        sl = json.load(open(ANATOMY_SUMMARY))["decomp"]["l3_by_slice"]
        a, b, r2, _ = noc.fit_line([v["hops"] for v in sl.values()], [v["med"] for v in sl.values()])
        print(f"Anatomy's L3 by slice from shire 0: {a:.1f} + {b:.2f} x hops cycles (r2 {r2:.4f}); its model "
              f"{anatomy['base']} + {anatomy['per_hop']} x hops")

    # Energy: every run directory named energy*/ (the runs are independent; report mean and range). These are the
    # 18 September values, superseded by the energy manual's re-runs at a pinned 600 MHz; they are printed, not embedded.
    energy_runs = []
    for ef in sorted(glob.glob(os.path.join(d, "energy*", "results.json"))):
        energy_runs.append(json.load(open(ef)))
    if energy_runs:
        print(f"energy (superseded, 18 September): {len(energy_runs)} runs, idle "
              f"{[round(e['idle_w'], 2) for e in energy_runs]} W")
        for name in energy_runs[0]["results"]:
            rs = [e["results"][name] for e in energy_runs if name in e["results"]]
            def col(key):
                vals = [r[key] for r in rs if r.get(key) is not None]
                return {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)} if vals else None
            lv = {"gb_per_s": col("gb_per_s"), "mean_w": col("mean_w"), "above_idle_w": col("above_idle_w"),
                  "pj_per_byte": col("pj_per_byte_vs_idle"), "pj_per_byte_vs_spin": col("pj_per_byte_vs_spin")}
            pj = lv["pj_per_byte"]
            print(f"  {name:11s} {lv['gb_per_s']['mean']:8.1f} GB/s  {lv['mean_w']['mean']:6.2f} W  "
                  f"+{lv['above_idle_w']['mean']:5.2f} W  "
                  + (f"{pj['mean']:7.2f} pJ/B ({pj['min']:.2f}-{pj['max']:.2f})" if pj else "")
                  + (f"  vs spin {lv['pj_per_byte_vs_spin']['mean']:.2f} pJ/B" if lv["pj_per_byte_vs_spin"] else ""))

    # Every L3 and DRAM chase (hart 0): [requesting shire, bytes, cycles per load, operating point in GHz].
    chases = sorted([r["chaser_shire"], r["size"], round(r["cycles_per_load"], 2), op_point(r)] for r in far)
    data = {"ghz": GHZ, "curves": curves, "plateaus": plateaus, "chases": chases, "fits": fits,
            "scp_model": scp_model, "l3_by_requester": l3_by_requester, "anatomy_l3": anatomy,
            "scp_matrix": {str(k): v for k, v in sorted(matrix.items())},
            "layout": {str(s): list(xy) for s, xy in noc.MARTY.items()}, "empty_cells": [list(c) for c in noc.EMPTY]}
    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="memhier-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one memhier-data script tag")
        html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":")) + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded report data into {args.embed}")


if __name__ == "__main__":
    main()
