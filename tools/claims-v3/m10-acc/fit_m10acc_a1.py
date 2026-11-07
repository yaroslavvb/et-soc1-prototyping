#!/usr/bin/env python3
"""Q153(m10acc), dated amendment A1 (REGISTRATION.md.dated-note-A1.md): the form ACC-L, with x_lane in place of x_acc.

    python3 -B fit_m10acc_a1.py features --job <dir> --out <dd>   # <dir>/out-a1/<sha>.json -> <dd>/features-m10acc-a1.json; checks A1-T1, A1-T2
    python3 -B fit_m10acc_a1.py fit --out <dd>                    # fit_m10acc.py's fit, unchanged, run on the A1 features in a temporary
                                                                  #   directory; its files copied as rows-, fit-, m10acc-, forecasts-e182-
                                                                  #   ...-a1.json and fit-output-a1.txt

In every A1 output the feature fit_m10acc.py names `acc` / `x_acc` is A1's x_lane (A1-2), and `tau_acc` is τ_L. The rows, checks,
estimator, leave one run out, jackknife, bootstraps, seeds, rule (R1-R3), arms, forecasts and post hoc readings are fit_m10acc.py's
code, imported and run unchanged. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m10acc as FA  # noqa: E402

NOTE = ("A1 (REGISTRATION.md.dated-note-A1.md): in this file the feature named acc / x_acc is x_lane, the accumulator words a lane's "
        "datapath takes in from one micro-op to the next, and tau_acc is tau_L; chosen after one look at the primary's result")


def cmd_features(a):
    job = os.path.abspath(a.job)
    prim = FA.load(os.path.join(a.out, "features-m10acc.json"))
    feats, t1 = {}, {"pass": True, "n": 0, "max_abs_diff": 0.0}
    for line in open(os.path.join(job, "joblist.txt")):
        if not line.strip():
            continue
        t, sha, ns = line.split()
        p = os.path.join(job, "out-a1", f"{sha}.json")
        if not os.path.exists(p):
            FA.stop(f"A1: no trace output for {sha}")
        o = json.loads(open(p).read().strip().splitlines()[-1])
        want = [int(n) for n in ns.split(",")]
        if o["type"] != t or sorted(int(n) for n in o["x"]) != want:
            FA.stop(f"A1: type or N list differs for {sha}")
        pf = prim["tiles"][sha]
        for n in want:
            d = abs(o["x"][str(n)]["x_acc"] - pf["x_acc"][str(n)]["total"])
            t1["max_abs_diff"] = max(t1["max_abs_diff"], d)
            t1["n"] += 1
            if d > 1e-6:
                FA.stop(f"A1-T1 fails for {sha} at N {n}: {o['x'][str(n)]['x_acc']} against {pf['x_acc'][str(n)]['total']}")
        if abs(o["x_bth_per_op"] - pf["x_bth"]) > 1e-6:
            FA.stop(f"A1: x_bth differs for {sha}")
        feats[sha] = {"type": t, "x_acc": {str(n): {"total": o["x"][str(n)]["x_lane"]} for n in want}, "x_bth": float(o["x_bth_per_op"]),
                      "x_acc_register": {str(n): o["x"][str(n)]["x_acc"] for n in want}, "unique_elements": o["unique_elements"],
                      "uops_per_op": o["uops_per_op"]}
    fc = FA.load(os.path.join(FA.E178T, "forecast-e178.json"))["kinds"]
    t2 = {}
    for k in FA.load(os.path.join(FA.E178T, "kinds-e178.json"))["kinds"]:
        mine = feats[k["sha256"]]["x_acc"][str(FA.N_LAUNCH_E178[k["type"]])]["total"]
        reg = fc[k["key"]]["flips_i"]["launch_mean"]["c_in"]
        t2[k["key"]] = {"x_lane": mine, "flipmodel_c_in": reg, "diff": mine - reg}
        if abs(mine - reg) > 1e-3:
            FA.stop(f"A1-T2 fails for {k['key']}: {mine} against {reg}")
    out = {"_what": "M10-ACC-L's features per tile (acctrace_m10acc_a1.c on the mini), by sha256; x_acc.<N>.total holds x_lane per op",
           "_a1": NOTE, "registration": "tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-A1.md", "launch_sizes": prim["launch_sizes"],
           "tiles": feats, "grid_e182": prim["grid_e182"],
           "checks": {"T1_e178_against_flipmodel_c_store": prim["checks"]["T1_e178_against_flipmodel_c_store"] | {"_note": "the primary's, carried"},
                      "T2_x_bth_python_against_c": prim["checks"]["T2_x_bth_python_against_c"] | {"_note": "the primary's; A1's x_bth equal on every tile"},
                      "A1_T1_x_acc_equal_to_committed": t1,
                      "A1_T2_e178_x_lane_against_flipmodel_c_in": {"pass": True, "n": len(t2),
                                                                    "max_abs_diff": max(abs(v["diff"]) for v in t2.values()), "kinds": t2}}}
    json.dump(out, open(os.path.join(a.out, "features-m10acc-a1.json"), "w"), indent=1, sort_keys=True)
    print(f"A1 features: {len(feats)} tiles; A1-T1 PASS ({t1['n']} values, max |diff| {t1['max_abs_diff']:.1e}); "
          f"A1-T2 PASS ({len(t2)} kinds, max |diff| {out['checks']['A1_T2_e178_x_lane_against_flipmodel_c_in']['max_abs_diff']:.1e})")


def cmd_fit(a):
    src = os.path.join(a.out, "features-m10acc-a1.json")
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(src, os.path.join(d, "features-m10acc.json"))
        ns = argparse.Namespace(out=d, job=None)
        FA.cmd_fit(ns)
        for name, dst in (("rows-m10acc.json", "rows-m10acc-a1.json"), ("fit-m10acc.json", "fit-m10acc-a1.json"),
                          ("m10acc.json", "m10acc-a1.json"), ("forecasts-e182-m10acc.json", "forecasts-e182-m10acc-a1.json")):
            j = FA.load(os.path.join(d, name))
            if isinstance(j, dict):
                j["_a1"] = NOTE
                if "features_sha256" in j:
                    j["features_sha256"] = FA.fsha(src)
            else:
                j = {"_a1": NOTE, "rows": j}
            json.dump(j, open(os.path.join(a.out, dst), "w"), indent=1, sort_keys=True)
        txt = open(os.path.join(d, "fit-output.txt")).read()
        open(os.path.join(a.out, "fit-output-a1.txt"), "w").write(NOTE + "\n\n" + txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("features", "fit"))
    ap.add_argument("--job")
    ap.add_argument("--out", default=os.path.join(FA.DD, "2026-11-07-q153-m10acc"))
    a = ap.parse_args()
    {"features": cmd_features, "fit": cmd_fit}[a.cmd](a)


if __name__ == "__main__":
    main()
