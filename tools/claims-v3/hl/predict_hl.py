#!/usr/bin/env python3
"""V3-HL predictions, written before any card run: replays every fma item's tiles through the multiply-add RTL and
prices the counted toggles with the 21 Sep fit (rtl-sim/fma_toggle, tools/ettelem/predict_heat.py).

    python3 tools/claims-v3/hl/predict_hl.py <gen-dir> --out <gen-dir>/predictions.json [--jobs 6]
        [--model docs/reports/data/2026-09-21-horace-aifoundry2/model.json]

<gen-dir> is make_hl.py's output (manifest.json, tiles/). Needs rtl-sim/fma_toggle/obj_dir/Vtb (Verilator 5; built
on aifoundry2). Per item: the four kinds of switching per op and minion, averaged over two points of a launch
(accumulators after 1e3 and 4e5 ops, as predict_heat.py does), and the board power the 21 Sep price list gives at an
80 C launch on aifoundry2 (predict_heat.predict: switching + state machines + idle at 80 C). The anchors are
replayed from tiles drawn the way sparsity_host draws them (tiles.py patterns zeros, ones, pi, randn).
ec items have no RTL here (the bench models only the multiply-add unit): they get no prediction from this script.
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "fma_toggle"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ettelem"))
import toggles as tg            # noqa: E402
import predict_heat as ph       # noqa: E402

POINTS = (1000, 400000)


def job(args):
    name, pattern, path, n0 = args
    return name, n0, tg.run(pattern, path, n0, 4, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gen")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--model", default=os.path.join(ROOT, "docs/reports/data/2026-09-21-horace-aifoundry2/model.json"))
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.gen, "manifest.json")))
    jobs = []
    for it in man["items"]:
        if it["kind"] != "fma":
            continue
        if it["family"] == "anchor":
            jobs += [(it["name"], it["values"], None, n0) for n0 in POINTS]
        else:
            jobs += [(it["name"], "custom", os.path.join(a.gen, "tiles", it["name"] + ".bin"), n0) for n0 in POINTS]
    with Pool(a.jobs) as p:
        done = p.map(job, jobs)
    model = json.load(open(a.model))
    if "T_amb" not in model:
        model["T_amb"] = model["sessions"][0]["T_amb"]
    out = {"model": os.path.relpath(a.model, ROOT), "points": list(POINTS), "items": {}}
    for it in man["items"]:
        if it["kind"] != "fma":
            continue
        pts = [r for n, _, r in done if n == it["name"]]
        mult = sum(sum(v for k, v in p["by_block"].items() if any(s in k for s in ph.MULT_BLOCKS)) for p in pts) / len(pts)
        mean = lambda k: sum(p[k] for p in pts) / len(pts)
        flips = {"ffclk": mean("ff_clocked"), "mult": mult, "rest": mean("nets") - mult, "bus": mean("bus"),
                 "valid": mean("lane_valid")}
        pred = ph.predict(model, flips, 1024, 80.0, 90.0, 10.0)
        out["items"][it["name"]] = {
            "flips_per_op": flips, "nets": mean("nets"), "ff_toggles": mean("ff_toggles"),
            "watts_by_class": pred["watts_by_class"], "p_switching_w": pred["p_switching"],
            "p_board_80c_w": pred["p_board_at_start"], "p_idle_80c_w": pred["p_idle_at_start"],
            "by_point": [{"n0": p["n0"], "nets": p["nets"], "bus": p["bus"], "ff_clocked": p["ff_clocked"]} for p in pts]}
        r = out["items"][it["name"]]
        print(f"{it['name']:18s} nets {r['nets']/1e6:7.2f} M  tree {flips['mult']/1e6:6.2f} M  rest {flips['rest']/1e6:6.2f} M  "
              f"bus {flips['bus']/1e3:7.1f} k  ffclk {flips['ffclk']/1e6:5.2f} M  valid {flips['valid']:5.0f}  "
              f"-> switching {r['p_switching_w']:5.1f} W, board at 80 C {r['p_board_80c_w']:5.1f} W", flush=True)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
