#!/usr/bin/env python3
"""Re-counts the multiply-add's switching activity four ways, on the same stream as toggles.py.

    recount.py --out recount.json [--patterns ...] [--tiles-dir DIR] [--tiles-glob 'DIR/*.bin']
               [--uops 64] [--lanes 8] [--seeds 1,2] [--jobs 5]

toggles.py reports one number per pattern, `nets`: Verilator's toggle coverage over every named signal
bit in the eight multiply-add units. That number counts a net once per RTL name it carries (a module
port is named again at each level of the hierarchy) and it counts every value the scheduler assigns
while a cycle settles, not only the value the cycle ends on. This runs the same stimulus with a VCD
window open and counts, per RTL module:

  nets            the coverage counter, as toggles.py reports it (one run, both counters)
  nets_vcd_raw    every value change in the VCD, per RTL name: the coverage counter's unit, re-derived
  nets_settled    changes between consecutive settled cycles, at most one per bit per cycle, per RTL name
  nets_ids        the same, counted once per VCD identifier (Verilator's own alias merging)
  nets_hier       the same, counted once per NET: names with one waveform are merged when one scope is an
                  ancestor of the other, which is a port carried up the hierarchy. THE FIGURE TO QUOTE,
                  and the one a refit should use -- see docs/reports/data/2026-10-26-toggle-recount/
  n_hier          how many switching nets a lane that leaves, after the merge
  nets_distinct   the same with ancestry ignored: a LOWER BOUND, and it collapses under a period-2 stream
  n_distinct      how many distinct switching waveforms the window held

Everything is scaled to one TensorFMA32 op on one minion (512 micro-ops x 8 lanes = 4,096 multiply-adds),
the unit toggles.json uses, from a window of --uops micro-op cycles on --lanes lanes.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import glob
import json
import multiprocessing
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
POINTS = [0, 1000, 400000]
PY = sys.executable


def parse_cov(path):
    """Verilator toggle coverage by RTL file, as toggles.py reads it."""
    by_block = collections.Counter()
    clock = 0
    for line in open(path, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        fields = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        f = os.path.basename(fields.get("f", "?"))
        name = fields.get("o", "")
        if f in ("tb.sv", "ff_acct.sv"):
            continue
        n = int(count)
        if re.search(r"clk|clock", name):
            clock += n
            continue
        by_block[f.replace(".v", "")] += n
    return by_block, clock


def run(job):
    pattern, tiles_bin, n0, seed, a = job
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        hexf = os.path.join(d, "t.hex")
        cov = os.path.join(d, "cov.dat")
        vcd = os.path.join(d, "t.vcd")
        js = os.path.join(d, "s.json")
        cmd = [PY, os.path.join(HERE, "tiles.py"), pattern, hexf, "--iters-before", str(n0), "--seed", str(seed)]
        if tiles_bin:
            cmd += ["--from-bin", tiles_bin]
        subprocess.run(cmd, check=True)
        out = subprocess.run(
            [os.path.join(HERE, "obj_dir_trace/Vtrace"), f"+tiles={hexf}", "+ops=4",
             f"+warm={0 if n0 == 0 else 1}", f"+mul={1 if n0 == 0 else 0}",
             f"+dump={vcd}", f"+dump_uops={a.uops}",
             f"+verilator+coverage+file+{cov}"],
            capture_output=True, text=True, check=True).stdout
        acct = json.loads(next(l for l in out.splitlines() if l.startswith("ACCT"))[5:])
        subprocess.run([os.path.join(HERE, "settle_count"), vcd, "--modmap", a.modmap, "--out", js,
                        "--phase", a.phase, "--skip", str(a.skip)],
                       check=True, capture_output=True)
        sc = json.load(open(js))
        by_block, clock = parse_cov(cov)

    # The run stops at the end of the trace window, so every counter covers exactly `uop_cycles`
    # micro-op cycles on all 8 lanes. One TensorFMA32 op is 512 micro-ops, so scale by 512/uop_cycles;
    # the VCD holds one fewer settled cycle than that, and `--skip` drops more.
    per = lambda v: v * 512.0 / acct["uop_cycles"]
    scale = 512.0 / sc["sample_cycles"] if sc["sample_cycles"] else 0.0
    mods = sc["by_module"]
    res = {
        "n0": n0, "seed": seed,
        "nets": per(sum(by_block.values())), "clock_nets": per(clock),
        "by_block": {k: per(v) for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]) if v},
        "ff_clocked": per(acct["ff_clocked_bits"]), "ff_toggles": per(acct["ff_toggles"]),
        "ff_present": per(acct["ff_present_bits"]),
        "bus": per(acct["bus_toggles"]), "lane_valid": per(acct["lane_valid"]),
        "clock_on": per(acct["clock_on"]), "cycles": per(acct["cycles"]),
        "window": {"uop_cycles": acct["uop_cycles"], "sample_cycles": sc["sample_cycles"],
                   "lanes": acct["lanes"], "scale": scale,
                   "n_ids": sc["n_ids"], "n_bits": sc["n_bits"], "xz_values": sc["xz_values"]},
        "nets_vcd_raw": sc["total"]["name_raw"] * scale,
        "nets_settled": sc["total"]["name_settled"] * scale,
        "nets_ids_raw": sc["total"]["id_raw"] * scale,
        "nets_ids": sc["total"]["id_settled"] * scale,
        "nets_hier": sc["total"]["hier_settled"] * scale,
        "n_hier": sc["total"]["n_hier"] / acct["lanes"],
        "nets_distinct": sc["total"]["distinct_settled"] * scale,
        "n_distinct": sc["total"]["n_distinct"] / acct["lanes"],
        "by_block_vcd_raw": {k: v["name_raw"] * scale for k, v in mods.items() if v["name_raw"]},
        "by_block_settled": {k: v["name_settled"] * scale for k, v in mods.items() if v["name_settled"]},
        "by_block_ids": {k: v["id_settled"] * scale for k, v in mods.items() if v["id_settled"]},
        "by_block_hier": {k: v["hier_settled"] * scale for k, v in mods.items() if v["hier_settled"]},
        "by_block_distinct": {k: v["distinct_settled"] * scale for k, v in mods.items() if v["distinct_settled"]},
        "n_hier_by_block": {k: v["n_hier"] / acct["lanes"] for k, v in mods.items() if v["n_hier"]},
        "n_distinct_by_block": {k: v["n_distinct"] / acct["lanes"] for k, v in mods.items() if v["n_distinct"]},
    }
    return pattern, seed, res


SCALARS = ["nets", "clock_nets", "ff_clocked", "ff_toggles", "ff_present", "bus", "lane_valid", "clock_on", "cycles",
           "nets_vcd_raw", "nets_settled", "nets_ids_raw", "nets_ids", "nets_hier", "n_hier",
           "nets_distinct", "n_distinct"]
BLOCKS = ["by_block", "by_block_vcd_raw", "by_block_settled", "by_block_ids", "by_block_hier",
          "by_block_distinct", "n_hier_by_block", "n_distinct_by_block"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--patterns", default="zeros,ones,pi,sparse50,uniform,randn,signs,pow2,mant,"
                                          "a_randn_b_ones,a_ones_b_randn,ternary,sparse75,checker")
    ap.add_argument("--tiles-dir", help="directory of <pattern>.<seed>.bin tiles the card ran")
    ap.add_argument("--tiles-glob", help="glob of <name>.<tag>.bin files, each its own item (E60's ladder)")
    ap.add_argument("--points", default=",".join(str(p) for p in POINTS))
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--uops", type=int, default=64)
    ap.add_argument("--skip", type=int, default=1, help="settled cycles dropped at the window's start")
    ap.add_argument("--phase", default="even")
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--modmap", default=os.path.join(HERE, "scopes.tsv"))
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    points = [int(p) for p in a.points.split(",")]

    jobs, source = [], {}
    if a.tiles_glob:
        items = {}
        for path in sorted(glob.glob(a.tiles_glob)):
            base = os.path.basename(path)
            name = base.rsplit(".", 2)[0]
            items.setdefault(name, []).append(path)
        names = sorted(items)
        for name in names:
            source[name] = "card"
            for path in items[name]:
                jobs += [(name, path, n0, 1, a) for n0 in points]
    else:
        names = a.patterns.split(",")
        for p in names:
            bins = sorted(glob.glob(os.path.join(a.tiles_dir, p + ".*.bin"))) if a.tiles_dir else []
            keep = [int(s) for s in a.seeds.split(",")]
            bins = [b for b in bins if int(b.split(".")[-2]) in keep]
            source[p] = "card" if bins else "drawn"
            pairs = [(b, int(b.split(".")[-2])) for b in bins] or [(None, s) for s in keep]
            for tb, seed in pairs:
                jobs += [(p, tb, n0, seed, a) for n0 in points]

    with multiprocessing.Pool(a.jobs) as pool:
        done = pool.map(run, jobs)

    res = {}
    for p in names:
        pts = [r for q, _, r in done if q == p]
        late = [r for r in pts if r["n0"] > 0] or pts
        mean = {k: sum(pt[k] for pt in late) / len(late) for k in SCALARS}
        for key in BLOCKS:
            acc = collections.Counter()
            for pt in late:
                for k, v in pt[key].items():
                    acc[k] += v / len(late)
            mean[key] = dict(acc)
        res[p] = {"points": [{k: v for k, v in pt.items() if k not in BLOCKS} for pt in pts],
                  "mean": mean, "tiles": source[p],
                  "seeds": sorted({s for q, s, _ in done if q == p})}
        m = mean
        print(f"{p:18s} {source[p]:5s} cov {m['nets']:12,.0f} vcd_raw {m['nets_vcd_raw']:12,.0f} "
              f"settled {m['nets_settled']:11,.0f} ids {m['nets_ids']:10,.0f} "
              f"hier {m['nets_hier']:10,.0f}/{m['n_hier']:6,.0f} "
              f"distinct {m['nets_distinct']:9,.0f}/{m['n_distinct']:6,.0f}", flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
