#!/usr/bin/env python3
"""RL-X4's FLOP side for tools/claims-v3/rl/reduce.py --flop, from V3-ABL-A's reduced runs.

    python3 tools/claims-v3/rl/export_flop.py --runs <results>/abla.runs.json --out <results>/inputs/flop.json

PLAN3 V3-RL, RL-X4: "FLOP side over V3-ABL-A blocks". One value per V3-ABL-A block (a pass) and card, for the fp32
rows RL-X4 uses: fp32_randn ("random") and fp32_zeros ("zeros"). The per-run quantity is the one the energy manual's
tensor bars use (tools/ettelem/build_energy_manual.py, v3_bar), which the ridge page divides by 2 for its FLOP side
(scripts/ridge-points.py: tensor.bars / 2):

    pJ per MAC = switching / per_s * 1e12

over the runs abla/reduce.py marked kept, in the passes it used (abla.runs.json "passes_used"), averaged within each
pass (V3-ABL-A runs every configuration once per block, so a pass holds one run of each). The file keeps pJ/MAC with
"unit": "pJ/MAC"; rl/reduce.py halves it to pJ/FLOP. Shape: {"unit": "pJ/MAC", "<card>": {"random": [...],
"zeros": [...]}, ...} with the values in pass order; "passes" and "source" are records, not read by the reducer.
"""
import argparse
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
OPS = {"random": "fp32_randn", "zeros": "fp32_zeros"}   # RL-X4's operands -> V3-ABL-A configurations


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="abla.runs.json (tools/claims-v3/abla/reduce.py's per-run table)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ar = json.load(open(a.runs))
    out = {"unit": "pJ/MAC", "quantity": "switching / per_s * 1e12 per kept run in passes_used, mean per pass "
           "(build_energy_manual.py v3_bar); rl/reduce.py halves it to pJ/FLOP",
           "source": os.path.relpath(os.path.abspath(a.runs)), "passes": {}}
    for card, runs in ar["runs"].items():
        used = set(ar["passes_used"].get(card, []))
        kept = [r for r in runs if r.get("kept") and r["pass"] in used]
        passes = sorted({r["pass"] for r in kept if r["config"] in OPS.values()})
        out[card], out["passes"][card] = {}, {}
        for op, cfg in OPS.items():
            by_pass = {k: [r["switching"] / r["per_s"] * 1e12 for r in kept if r["config"] == cfg and r["pass"] == k]
                       for k in passes}
            ks = [k for k in passes if by_pass[k]]
            out[card][op] = [round(statistics.fmean(by_pass[k]), 6) for k in ks]
            out["passes"][card][op] = ks
            print(f"{card} {op:6s} ({cfg}) pJ/MAC per pass {dict(zip(ks, out[card][op]))} "
                  f"mean {statistics.fmean(out[card][op]):.4f}" if ks else f"{card} {op}: no kept run")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
