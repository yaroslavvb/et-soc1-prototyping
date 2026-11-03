#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q137(m), post hoc (after the freeze; changes nothing frozen): rerun fit_m6's nested procedure to keep every row's errors,
then 95% bootstrap intervals over kinds for M6's nested rms, M5's frozen rms, and the paired difference, per format; and the
heat rows' own noise floor (the rms of each item's standard error of dT_win over passes).

    python3 bootstrap_m6.py   # writes bootstrap-m6.json
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m6 as M  # noqa: E402


def boot(kinds, e_new, e_old, n=2000, seed=20261102):
    rng = np.random.default_rng(seed)
    ks = sorted(set(kinds))
    idx = {k: np.where(np.array(kinds) == k)[0] for k in ks}
    a, b, d = [], [], []
    for _ in range(n):
        pick = rng.choice(len(ks), len(ks))
        ii = np.concatenate([idx[ks[j]] for j in pick])
        rn = float(np.sqrt(np.mean(e_new[ii] ** 2)))
        ro = float(np.sqrt(np.mean(e_old[ii] ** 2)))
        a.append(rn), b.append(ro), d.append(rn - ro)
    q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return {"m6_nested_rms_95": q(a), "m5_frozen_rms_95": q(b), "diff_m6_minus_m5_95": q(d),
            "share_diff_ge_0": float(np.mean(np.array(d) >= 0)),
            "m6_nested_rms": float(np.sqrt(np.mean(e_new ** 2))), "m5_frozen_rms": float(np.sqrt(np.mean(e_old ** 2)))}


def main():
    rows, _, _ = M.all_rows()
    m5 = json.load(open(os.path.join(M.DD, "2026-11-01-q133b-power-model", "m5.json")))
    out = {"_note": "post hoc, after the freeze; nothing frozen changes", "power": {}, "row_errors": []}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        _, _, outer, m5e = M.run_family(fr, famname, m5)
        tys = np.array([r["type"] for r in fr])
        new = np.array([r["exp"] in M.R.NEW for r in fr])
        kinds = [r["kind"] for r in fr]
        for t in sorted(set(tys)):
            for lab, m in ((t, tys == t), (f"{t}|new_experiments", (tys == t) & new)):
                out["power"][lab] = {"n": int(m.sum()), **boot([k for k, x in zip(kinds, m) if x], outer[m], m5e[m])}
        for i, r in enumerate(fr):
            out["row_errors"].append({"exp": r["exp"], "key": r["key"], "kind": r["kind"], "D": r["D"],
                                      "m6_nested_err_w": float(outer[i]), "m5_frozen_err_w": float(m5e[i])})
    # heat noise floor
    se = {"fp32": [], "fp16": [], "int8": []}
    for r in M.heat_rows(rows):
        it = json.load(open(os.path.join(M.DD, M.EXPDIR[r["exp"]], f"{r['exp'].lower()}.json")))["items"][r["key"]]
        s = (it.get("dT_win") or {}).get("se")
        if s is not None and r["type"] in se:
            se[r["type"]].append(s)
    out["heat_noise_floor_rms_se_c"] = {t: {"n": len(v), "rms_se_c": float(np.sqrt(np.mean(np.square(v)))) if v else None} for t, v in se.items()}
    json.dump(out, open(os.path.join(HERE, "bootstrap-m6.json"), "w"), indent=1)
    for k, v in out["power"].items():
        print(k, v["n"], {a: (round(b, 3) if isinstance(b, float) else [round(x, 3) for x in b]) for a, b in v.items() if a != "n"})
    print("heat floor", out["heat_noise_floor_rms_se_c"])


if __name__ == "__main__":
    main()
