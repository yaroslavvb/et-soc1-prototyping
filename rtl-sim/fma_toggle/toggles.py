#!/usr/bin/env python3
"""Runs the FMA toggle bench for value patterns and tabulates switching activity per TensorFMA32 op.

    toggles.py --out toggles.json [--patterns zeros,ones,...] [--tiles-dir DIR] [--ops 4] [--jobs 4]

For each pattern the bench runs at several points of a launch (the accumulators start at n * A.B for
n = 0, 1e3, 4e5 ops), because what the adder sees depends on how large C has grown; the mean leaves out
n = 0, the one multiply pass that starts a launch. With --tiles-dir, every <pattern>.<seed>.bin dumped by
sparsity_host --dump-tiles is replayed (the card's exact operands) and the seeds are averaged. Numbers are
per op (512 micro-ops on 8 lanes, 4,096 multiply-adds), for one minion.

  nets        toggles of every named net and register bit inside the eight txfma_top units (Verilator
              toggle coverage; clocks excluded; zero-delay, so no glitches)
  by_block    the same, split by RTL file
  ff_clocked  register bits that saw a clock edge with their enable high
  ff_toggles  register bits that changed
  bus         toggles of the operand words presented to the lanes (a, b, c)
  lane_valid  lane-cycles with a valid multiply-add (max 4,096); clock_on: cycles with the unit's clock on
"""
import argparse
import collections
import json
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
POINTS = [0, 1000, 400000]


def parse_cov(path):
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


def run(pattern, tiles_bin, n0, ops, seed):
    with tempfile.TemporaryDirectory() as d:
        hexf, cov = os.path.join(d, "t.hex"), os.path.join(d, "cov.dat")
        cmd = ["python3", os.path.join(HERE, "tiles.py"), pattern, hexf, "--iters-before", str(n0), "--seed", str(seed)]
        if tiles_bin:
            cmd += ["--from-bin", tiles_bin]
        subprocess.run(cmd, check=True)
        out = subprocess.run([os.path.join(HERE, "obj_dir/Vtb"), f"+tiles={hexf}", f"+ops={ops}",
                              f"+warm={0 if n0 == 0 else 1}", f"+mul={1 if n0 == 0 else 0}",
                              f"+verilator+coverage+file+{cov}"], capture_output=True, text=True, check=True).stdout
        acct = json.loads(next(l for l in out.splitlines() if l.startswith("ACCT"))[5:])
        by_block, clock = parse_cov(cov)
    per = lambda v: v / acct["ops"]
    return {"n0": n0, "nets": per(sum(by_block.values())), "clock_nets": per(clock),
            "by_block": {k: per(v) for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]) if v},
            "ff_clocked": per(acct["ff_clocked_bits"]), "ff_toggles": per(acct["ff_toggles"]),
            "bus": per(acct["bus_toggles"]), "lane_valid": per(acct["lane_valid"]), "clock_on": per(acct["clock_on"]),
            "cycles": per(acct["cycles"])}


def one(job):
    p, tb, n0, ops, seed = job
    return p, seed, run(p, tb, n0, ops, seed)


def main():
    import glob
    import multiprocessing
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--patterns", default="zeros,ones,twos,pi,checker,ternary,onebit,sparse75,uniform,randn")
    ap.add_argument("--tiles-dir", help="directory of <pattern>.<seed>.bin tiles dumped by sparsity_host --dump-tiles")
    ap.add_argument("--ops", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    jobs, source = [], {}
    for p in a.patterns.split(","):
        bins = sorted(glob.glob(os.path.join(a.tiles_dir, p + ".*.bin"))) if a.tiles_dir else []
        source[p] = "card" if bins else "drawn"
        for tb, seed in ([(b, int(b.split(".")[-2])) for b in bins] or [(None, a.seed)]):
            jobs += [(p, tb, n0, a.ops, seed) for n0 in POINTS]
    with multiprocessing.Pool(a.jobs) as pool:
        done = pool.map(one, jobs)
    res = {}
    for p in a.patterns.split(","):
        pts = [r for q, _, r in done if q == p]
        late = [r for r in pts if r["n0"] > 0]
        mean = {k: sum(pt[k] for pt in late) / len(late) for k in late[0] if k not in ("n0", "by_block")}
        blocks = collections.Counter()
        for pt in late:
            for k, v in pt["by_block"].items():
                blocks[k] += v / len(late)
        mean["by_block"] = dict(blocks)
        seeds = sorted({s for q, s, _ in done if q == p})
        per_seed = {s: sum(r["nets"] for q, s2, r in done if q == p and s2 == s and r["n0"] > 0) /
                       max(1, sum(1 for q, s2, r in done if q == p and s2 == s and r["n0"] > 0)) for s in seeds}
        res[p] = {"points": [{k: v for k, v in pt.items() if k != "by_block"} for pt in pts], "mean": mean,
                  "tiles": source[p], "seeds": seeds, "nets_by_seed": per_seed}
        m = mean
        print(f"{p:16s} {source[p]:5s} seeds {len(seeds)}  nets {m['nets']:10.0f}  ff_clocked {m['ff_clocked']:9.0f}  "
              f"ff_toggles {m['ff_toggles']:8.0f}  bus {m['bus']:8.0f}  valid {m['lane_valid']:6.0f}", flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
