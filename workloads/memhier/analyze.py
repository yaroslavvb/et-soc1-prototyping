#!/usr/bin/env python3
"""Summarize memhier results into the numbers and chart data used by the report.

    python3 workloads/memhier/analyze.py docs/reports/data/2026-09-18-memhier-aifoundry2 \
        [--embed docs/reports/2026-09-18-et-soc1-memory-hierarchy.html]

The data directory holds the chase-*.jsonl files from memhier_host and energy/ from run_energy.py.
The script prints the plateau latency of each level, the spread of DRAM latency, the scratchpad latency
matrix and the energy table. With --embed it also replaces the JSON inside the report's
<script type="application/json" id="memhier-data"> tag.
"""
import argparse
import glob
import json
import os
import re
import statistics

GHZ = 0.6  # minion base clock reported by DM_CMD_GET_ASIC_FREQUENCIES
# The governor's operating points on these cards are 600, 700 and 800 MHz (DVFS report); nothing runs outside them.
GHZ_MIN, GHZ_MAX = 0.6, 0.8
MIN_WALL_S = 0.01  # chases shorter than this are dominated by launch overhead

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
            curves[label] = [[r["size"], round(r["cycles_per_load"], 2), round(r["cycles_per_load"] / point_ghz(r), 1)]
                             for r in rows[name]]

    print(f"latency plateaus (cycles @ {GHZ} GHz, ns):")
    plateaus = {}
    for level, lo, hi in LEVELS:
        vals = [c for label in ("shire 0", "shire 24") for s, c, _ in curves.get(label, []) if lo <= s <= hi]
        if level == "DRAM":  # every chain of >= 128 MB, from every run and shire
            vals = [r["cycles_per_load"] for rs in rows.values() for r in rs
                    if r["where"] == "dram" and r["size"] >= (128 << 20) and r["thread"] == 0]
        if level == "L3":  # 4 MB chains from every run and shire
            vals = [r["cycles_per_load"] for rs in rows.values() for r in rs
                    if r["where"] == "dram" and (768 << 10) <= r["size"] <= (8 << 20) and r["thread"] == 0]
        if not vals:
            continue
        plateaus[level] = {"median": statistics.median(vals), "min": min(vals), "max": max(vals), "n": len(vals)}
        print(f"  {level:22s} median {statistics.median(vals):7.1f}  range {min(vals):6.1f}-{max(vals):6.1f} cycles"
              f"  = {statistics.median(vals) / GHZ:6.1f} ns ({min(vals) / GHZ:.0f}-{max(vals) / GHZ:.0f})  n={len(vals)}")

    t1 = {r["size"]: r["cycles_per_load"] for r in rows.get("chase-dram-thread1", [])}
    if t1:
        print(f"hart 1: {t1}")

    matrix = {}
    for name, rs in rows.items():
        m = re.match(r"chase-scp-map(?:-from(\d+))?$", name)
        if m:
            src = int(m.group(1) or 0)
            matrix[src] = [round(r["cycles_per_load"], 1) for r in sorted(rs, key=lambda r: r["scp_shire"])]
    remote = [v for src, vals in matrix.items() for t, v in enumerate(vals) if t != src]
    if remote:
        print(f"scratchpad: local {matrix[0][0]:.1f} cycles; remote {min(remote):.0f}-{max(remote):.0f} cycles, "
              f"median {statistics.median(remote):.0f} ({len(remote)} pairs from sources {sorted(matrix)})")

    # Energy: every run directory named energy*/ (the runs are independent; report mean and range).
    energy_runs = []
    for ef in sorted(glob.glob(os.path.join(d, "energy*", "results.json"))):
        energy_runs.append(json.load(open(ef)))
    energy = None
    if energy_runs:
        energy = {"runs": len(energy_runs), "idle_w": [e["idle_w"] for e in energy_runs], "levels": {}}
        print(f"energy: {len(energy_runs)} runs, idle {[round(w, 2) for w in energy['idle_w']]} W")
        for name in energy_runs[0]["results"]:
            rs = [e["results"][name] for e in energy_runs if name in e["results"]]
            def col(key):
                vals = [r[key] for r in rs if r.get(key) is not None]
                return {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)} if vals else None
            lv = {"what": rs[0]["what"], "gb_per_s": col("gb_per_s"), "mean_w": col("mean_w"),
                  "above_idle_w": col("above_idle_w"), "pj_per_byte": col("pj_per_byte_vs_idle"),
                  "pj_per_byte_vs_spin": col("pj_per_byte_vs_spin")}
            energy["levels"][name] = lv
            pj = lv["pj_per_byte"]
            print(f"  {name:11s} {lv['gb_per_s']['mean']:8.1f} GB/s  {lv['mean_w']['mean']:6.2f} W  "
                  f"+{lv['above_idle_w']['mean']:5.2f} W  "
                  + (f"{pj['mean']:7.2f} pJ/B ({pj['min']:.2f}-{pj['max']:.2f})" if pj else "")
                  + (f"  vs spin {lv['pj_per_byte_vs_spin']['mean']:.2f} pJ/B" if lv["pj_per_byte_vs_spin"] else ""))

    # L3 / DRAM in ns: the DVFS governor moves the minion clock (600-800 MHz), so convert each chase with
    # its own clock, inferred from its cycles and wall time (warm-up + timed loads, all at the same level).
    ns = {"L3": [], "DRAM": []}
    for rs in rows.values():
        for r in rs:
            if r["where"] != "dram" or r["thread"] != 0 or r["wall_s"] < MIN_WALL_S:
                continue
            level = "L3" if (768 << 10) <= r["size"] <= (8 << 20) else "DRAM" if r["size"] >= (128 << 20) else None
            if level:
                ns[level].append(r["cycles_per_load"] / point_ghz(r))
    for level, vals in ns.items():
        if vals:
            plateaus[level]["ns_measured_clock"] = {"median": statistics.median(vals), "min": min(vals),
                                                    "max": max(vals), "n": len(vals)}
            print(f"{level} at each run's own clock: median {statistics.median(vals):.0f} ns, "
                  f"range {min(vals):.0f}-{max(vals):.0f} ns (n={len(vals)})")

    data = {"ghz": GHZ, "curves": curves, "plateaus": plateaus, "scp_matrix": {str(k): v for k, v in sorted(matrix.items())},
            "dram_samples": sorted(round(r["cycles_per_load"], 1) for rs in rows.values() for r in rs
                                   if r["where"] == "dram" and r["size"] >= (128 << 20) and r["thread"] == 0),
            "energy": energy}
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
