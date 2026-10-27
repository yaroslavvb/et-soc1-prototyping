#!/usr/bin/env python3
"""E68 stage-map predictions: run the fma_toggle RTL bench on every sm item and split its toggles by stage.

    python3 predict_sm.py --gen <sm-gen dir> --bench <rtl-sim/fma_toggle> --out predictions.json [--ops 4]

For each item the bench is run at two accumulator points (1e3 and 4e5 ops, toggles.py's convention, leaving out
the n=0 multiply pass) and the two are averaged. Toggles are per TensorFMA32 op (4,096 multiply-adds, one minion).
Every item is then differenced against the zero of its partner, as the card measurement is.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

POINTS = [1000, 400000]

# RTL file -> stage group. tfma.stages: f0 capture; f1 Booth + tree levels 1-2; f2 tree levels 3-4 + product
# adder; f3 align; f4 add + leading-one; f5 normalise; f6 round.  The coverage counter keys by FILE, so a leaf
# instantiated in two stages merges; MAP_NOTE records every such case.
GROUP = {
    # ---- multiplier (f1 + f2): the Booth rows, the Wallace tree, its compressors and the product adder
    "txfma_booth_ppg_32r4": "mul", "txfma_booth_ppg_32r4_msb": "mul", "txfma_booth_ppg_32r4_norm": "mul",
    "txfma_wallace1": "mul", "txfma_wallace2": "mul", "txfma_csa": "mul",
    "txfma_4_2_compressor": "mul", "txfma_4_2_compressor_array": "mul",
    "txfma_f1": "mul", "txfma_f2": "mul",
    # ---- back end
    "txfma_align_shf": "align", "txfma_f3": "align", "txfma_ediff_opdorder_logic": "align",
    "txfma_adder": "add", "txfma_f4": "add", "txfma_lxd": "add",
    "txfma_norm_shf": "norm", "txfma_f5": "norm", "txfma_frac_zero_detect": "norm",
    "txfma_trz": "norm", "txfma_trz2": "norm",
    "txfma_rnd_adder": "round", "txfma_f6": "round",
    # ---- capture and the control/exponent pipelines
    "txfma_f0": "f0",
    "txfma_top": "ctl", "txfmactl_top": "ctl", "txfmafrac_top": "ctl", "txfmaexp_top": "ctl",
    "txfma_exp_special_detect": "ctl",
}
for _i in range(7):
    GROUP.setdefault(f"txfma_c{_i}", "ctl")
    GROUP.setdefault(f"txfma_e{_i}", "ctl")
GROUPS = ["mul", "align", "add", "norm", "round", "f0", "ctl", "other"]


def parse_cov(path):
    by_block, clock = collections.Counter(), 0
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


def run_point(bench, tiles_bin, n0, ops, py):
    with tempfile.TemporaryDirectory() as d:
        hexf, cov = os.path.join(d, "t.hex"), os.path.join(d, "cov.dat")
        subprocess.run([py, os.path.join(bench, "tiles.py"), "randn", hexf,
                        "--iters-before", str(n0), "--from-bin", tiles_bin], check=True,
                       stdout=subprocess.DEVNULL)
        out = subprocess.run([os.path.join(bench, "obj_dir/Vtb"), f"+tiles={hexf}", f"+ops={ops}",
                              "+warm=1", "+mul=0", f"+verilator+coverage+file+{cov}"],
                             capture_output=True, text=True, check=True).stdout
        acct = json.loads(next(l for l in out.splitlines() if l.startswith("ACCT"))[5:])
        by_block, clock = parse_cov(cov)
    n = acct["ops"]
    return {"by_block": {k: v / n for k, v in by_block.items()}, "clock_nets": clock / n,
            "ff_clocked": acct["ff_clocked_bits"] / n, "ff_toggles": acct["ff_toggles"] / n,
            "bus": acct["bus_toggles"] / n, "lane_valid": acct["lane_valid"] / n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ops", type=int, default=4)
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.gen, "manifest.json")))
    res, unmapped = {}, set()
    for it in man["items"]:
        if "flips" not in it:
            continue
        tb = os.path.join(a.gen, "tiles", it["name"] + ".bin")
        pts = [run_point(a.bench, tb, n0, a.ops, a.python) for n0 in POINTS]
        mean = {k: sum(p[k] for p in pts) / len(pts) for k in pts[0] if k != "by_block"}
        blocks = collections.Counter()
        for p in pts:
            for k, v in p["by_block"].items():
                blocks[k] += v / len(pts)
        g = collections.Counter()
        for k, v in blocks.items():
            grp = GROUP.get(k)
            if grp is None:
                unmapped.add(k)
                grp = "other"
            g[grp] += v
        mean["by_block"] = dict(sorted(blocks.items(), key=lambda kv: -kv[1]))
        mean["by_stage"] = {k: g.get(k, 0.0) for k in GROUPS}
        mean["nets"] = sum(blocks.values())
        res[it["name"]] = mean
        print(f"{it['name']:12s} nets {mean['nets']:8.1f}  " +
              "  ".join(f"{k} {mean['by_stage'][k]:7.1f}" for k in GROUPS if mean['by_stage'][k]), flush=True)
    # differences from each item's own zero, as the card measures them
    diffs = {}
    for it in man["items"]:
        if "flips" not in it or it["name"] in ("smz_q", "smz_b"):
            continue
        z = res[it["zero"]]
        d = {k: res[it["name"]]["by_stage"][k] - z["by_stage"][k] for k in GROUPS}
        d["nets"] = res[it["name"]]["nets"] - z["nets"]
        d["ff_clocked"] = res[it["name"]]["ff_clocked"] - z["ff_clocked"]
        d["zero"] = it["zero"]
        d["mask_bits"] = it["mask_bits"]
        diffs[it["name"]] = d
    json.dump({"ops": a.ops, "points": POINTS, "group_map": GROUP, "absolute": res, "minus_zero": diffs,
               "unmapped_files": sorted(unmapped)}, open(a.out, "w"), indent=1)
    print("\n--- minus its own zero, per TensorFMA32 op (4,096 multiply-adds, one minion) ---")
    print(f"{'item':12s} {'nets':>9s} " + " ".join(f"{k:>8s}" for k in GROUPS[:5]))
    for k, d in diffs.items():
        print(f"{k:12s} {d['nets']:9.1f} " + " ".join(f"{d[g]:8.1f}" for g in GROUPS[:5]))
    if unmapped:
        print("UNMAPPED FILES (counted as 'other'):", sorted(unmapped))


if __name__ == "__main__":
    main()
