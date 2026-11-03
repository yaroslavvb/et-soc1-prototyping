"""E150 post hoc (no verdicts; nothing here changes a rule, a prediction or a score):

    python posthoc_e150.py <data dir> > posthoc.txt        # also writes posthoc.json in the data dir

1. Die rise per board W without a model, per board: (a) the 60 s step from the 120 s reference hold to the zeros hold;
   (b) each 30 s hold's measured rise over its own power step (hold W - pre-hold W), against the fitted model's 30 s
   rise per W.
2. The operand bytes: E150's features against E149's for the same kinds, as G1's A100-watt prediction (E150's bytes
   come from the same seeds on another GPU type's generator grid).
3. The board that was cancelled (an NVIDIA A10): whether its bytes matched the A10G's.
4. Phase L: each kind's y on the A10G over its y on the A100.
"""
import glob
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e149"))
import analyze_e149 as AZ  # noqa: E402


def main(d):
    out = {}
    run = os.path.join(d, "logs", "e150-20261102-r1")
    pz = json.load(open(os.path.join(d, "predictions-e150.json")))
    rH = json.load(open(os.path.join(d, "reduce-H.json")))
    sc = json.load(open(os.path.join(d, "score-e150.json")))
    print("## 1. Die rise per board W without a model\n")
    steps = {}
    for un in sorted(os.listdir(run)):
        u = AZ.load_unit(os.path.join(run, un))
        hw = {s["label"]: s["windows"][0] for s in u["steps"] if s.get("op") == "hold"}
        ts, P, T = AZ._series(u)

        def mean_in(a, b, x):
            i, j = np.searchsorted(ts, [a, b])
            return float(np.mean(x[i:j]))
        r, z = hw["heat_ref"], hw["heat_zeros"]
        pr, tr = mean_in(r["t_b"] - 10, r["t_b"], P), mean_in(r["t_b"] - 1, r["t_b"], T)
        pz_, tz = mean_in(z["t_b"] - 10, z["t_b"], P), mean_in(z["t_b"] - 1, z["t_b"], T)
        steps[un] = {"ref_w": pr, "ref_c": tr, "zeros_w": pz_, "zeros_c": tz, "c_per_w_60s": (tr - tz) / (pr - pz_)}
        print(f"board {un}: reference hold's last 10 s {pr:.1f} W, die {tr:.2f} C; zeros hold's {pz_:.1f} W, die "
              f"{tz:.2f} C: {steps[un]['c_per_w_60s']:.4f} C/W over the 60 s step")
    out["1a_step"] = steps
    per = {}
    for un, lst in sc["heat_holds"].items():
        rows = []
        for h in rH["units"][un]["holds"]:
            rec = next((x for x in lst if x["kind"] == h["kind"]), None)
            dp = (h["hold_st"].get("p_w") or 0) - (h["pre_st"].get("p_w") or 0)
            if rec and rec["valid"] and dp > 5:
                rows.append({"kind": h["kind"], "dp_w": dp, "rise_c": rec["meas_rise_c"],
                             "c_per_w": rec["meas_rise_c"] / dp, "model_c_per_w": rec["pred_rise_measP_c"] / dp})
        per[un] = {"n": len(rows), "median_c_per_w": float(np.median([r["c_per_w"] for r in rows])) if rows else None,
                   "median_model_c_per_w": float(np.median([r["model_c_per_w"] for r in rows])) if rows else None,
                   "rows": rows}
        print(f"board {un}: over {len(rows)} holds with a step above 5 W, the measured 30 s rise per W has median "
              f"{per[un]['median_c_per_w']:.4f} C/W; the fitted model driven by the same watts "
              f"{per[un]['median_model_c_per_w']:.4f}")
    out["1b_holds"] = per
    print(f"fitted (phase L, pooled): rise in 30 s per W {pz['heat']['pooled']['rise30_per_W']:.4f}, steady "
          f"{pz['heat']['pooled']['R_ss']:.4f} C/W; per board steady "
          + ", ".join(f"{u} {v['R_ss']:.4f}" for u, v in pz["heat"]["per_unit"].items()) + "\n")
    print("## 2. E150's bytes against E149's, as G1's prediction in A100 watts\n")
    p149 = json.load(open(os.path.join(d, "..", "2026-11-02-e149-gpu-model-check", "predictions-e149.json")))
    diffs = []
    for k, v in sorted(pz["kinds"].items()):
        p9 = p149["kinds"].get(k, {}).get("pred", {}).get("G1")
        same = p149["kinds"].get(k, {}).get("sha_A") == v["sha_A"]
        if p9 is not None:
            diffs.append(v["pred0"]["G1"] - p9)
            print(f"{k:<18} E150 bytes {v['pred0']['G1']:8.2f}  E149 bytes {p9:8.2f}  same bytes {same}")
    out["2_bytes"] = {"rms_w": float(np.sqrt(np.mean(np.square(diffs)))) if diffs else None, "n": len(diffs)}
    print(f"rms difference {out['2_bytes']['rms_w']:.3f} A100 W over {len(diffs)} kinds\n")
    print("## 3. The cancelled board (an NVIDIA A10)\n")
    nb = os.path.join(d, "logs", "e150-20261102-r1-not-used", "B", "features-M.json.gz")
    if os.path.exists(nb):
        fb = json.load(gzip.open(nb, "rt"))
        fa = json.load(gzip.open(os.path.join(run, "A", "features-M.json.gz"), "rt"))
        n_same = sum(1 for k in fa if k in fb and fa[k]["sha_A"] == fb[k]["sha_A"] and fa[k]["sha_B"] == fb[k]["sha_B"])
        out["3_a10_bytes"] = {"kinds": len(fa), "same": n_same}
        print(f"the A10's build matched the A10G's bytes on {n_same} of {len(fa)} kinds")
    print("\n## 4. Phase L: each kind's y on the A10G over its y on the A100 (E149's stage 1)\n")
    r1 = json.load(open(os.path.join(d, "..", "2026-11-02-e149-gpu-model-check", "reduce-stage1.json")))["kinds"]
    rat = {}
    for k, v in sorted(pz["fit_L"].items()):
        y9 = r1.get(k, {}).get("y")
        if y9 and abs(y9) > 1.0:
            rat[k] = v["y"] / y9
    for f in ("bf16", "fp16", "int8"):
        ks = sorted((k for k in rat if k.startswith(f + ".")), key=lambda k: rat[k])
        vals = [rat[k] for k in ks]
        q = np.percentile(vals, [10, 25, 50, 75, 90])
        print(f"{f}: {len(ks)} kinds, median {q[2]:.3f}, middle half {q[1]:.3f}-{q[3]:.3f}, 10-90% {q[0]:.3f}-{q[4]:.3f}")
        print("   " + ", ".join(f"{k.split('.', 1)[1]} {rat[k]:.2f}" for k in ks))
    out["4_ratio_to_a100"] = rat
    json.dump(out, open(os.path.join(d, "posthoc.json"), "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
