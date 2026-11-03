#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q137(m): M6's frozen predictions (and M5's, for comparison) for blind pool 4, for E140 on aifoundry3 at 600 MHz.

    python3 predict_blind4.py    # reads m6.json, counts-blind4.json, the pool; writes the pool's predictions-blind4.json and .md

Power: D, W over the type's own zeros at 600 MHz, aifoundry3 card 0's footing (the card E140 runs). 95% interval: 1.96 x the
nested leave-one-kind-out rms of the type on aifoundry3 (interval_pool_by_format_card), in quadrature with the constants'
jackknife covariance. Heat: die rise over the kinds harness's window (T_run 4.5 s, launch at the pass's median reading) from
S = D + the type's zeros' S on aifoundry3 (the mean of the training experiments' zeros items on that card), and, beside it, the rise the
same S would reach in a long hold, from E97's settled plateau and the step response frozen in m6.json.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m6 as M  # noqa: E402
F = M.F
ROOT = M.R.ROOT
POOL = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind4")
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    m6 = json.load(open(os.path.join(HERE, "m6.json")))
    m5 = json.load(open(os.path.join(M.DD, "2026-11-01-q133b-power-model", "m5.json")))
    counts = json.load(open(os.path.join(HERE, "counts-blind4.json")))["rows"]
    pool = json.load(open(os.path.join(POOL, "blind4.json")))
    hr = json.load(open(os.path.join(HERE, "heat-rows.json")))
    zc = json.load(open(os.path.join(M.DD, "2026-11-01-q132-rtl-bench", "counts-v2.json")))["rows"]
    zeros = {t: zc[f"{t}.zeros"]["mean"] for t in F.CPO}
    szero = {}
    for t in ("fp32", "fp16", "int8"):
        v = []
        for e, d in M.EXPDIR.items():
            j = json.load(open(os.path.join(M.DD, d, f"{e.lower()}.json")))
            z = j["items"].get(f"{t}.zeros")
            if j.get("card", "").startswith("aifoundry3") and z and isinstance(z.get("S"), dict) and z["S"].get("mean") is not None:
                v.append(float(z["S"]["mean"]))
        szero[t] = {"mean": statistics.mean(v), "sd": statistics.pstdev(v) if len(v) > 1 else None, "n": len(v)}
    H = m6["heat"]
    hc = H["coef"]
    step = H["step_response"]
    taus, ws = np.array(step["tau_s"]), np.array(step["weights"])
    Fstep = lambda t: float(1 - np.sum(ws * np.exp(-t / taus)))
    c_a3 = H["steady_c_per_board_w"]["aifoundry3"]["value"]
    out = {"_note": "Q137(m) M6 frozen predictions for blind pool 4; E140 scores them on aifoundry3 at 600 MHz",
           "m6_sha256": sha(open(os.path.join(HERE, "m6.json"), "rb").read()),
           "pool_blind4_json_sha256": sha(open(os.path.join(POOL, "blind4.json"), "rb").read()),
           "counts_blind4_sha256": sha(open(os.path.join(HERE, "counts-blind4.json"), "rb").read()),
           "zeros_S_aifoundry3_w": szero, "tiles": {}}
    for meta in sorted(pool["tiles"], key=lambda m: m["name"]):
        name = meta["name"]
        t = meta["type"]
        p = os.path.join(POOL, meta["file"])
        raw = open(p, "rb").read()
        crow = counts.get(name)
        if crow is None:
            out["tiles"][name] = {"error": "no bench count"}
            continue
        f = F.fmt_feats(F.bench_feats(crow["mean"], zeros[t]), t)
        f.update({k: v for k, v in F.tile_feats(p, t).items() if k != "sha256"})
        f.update(M.flip_feats(p, t))
        rate = F.RATE[t]
        fam = "int8" if t == "int8" else "float"
        rec = {"type": t, "sha256": sha(raw), "sha256_pool": meta["sha256"]["whole"] if isinstance(meta.get("sha256"), dict) else None, "check_mismatch": crow["mean"].get("check_mismatch"), "features": f}
        for lab, mod in (("M6", m6["families"][fam]), ("M5", m5["families"][fam])):
            x = np.array([rate * f[q] for q in mod["terms"]])
            b = np.array(mod["coef_J"])
            C = np.array(mod["cov_J2"])
            d = float(x @ b)
            pool_rms = mod["interval_pool_by_format_card"][f"{t}|a3"]["rms_w"]
            hw = 1.96 * math.sqrt(pool_rms ** 2 + float(x @ C @ x))
            rec[f"{lab}_D_w"] = round(d, 4)
            rec[f"{lab}_D_95"] = [round(d - hw, 4), round(d + hw, 4)]
        S = rec["M6_D_w"] + szero[t]["mean"]
        card = "aifoundry3"
        g = hc.get(f"S|{card}", 0.0)
        dT = g * S
        hw_h = 1.96 * H["interval_pool_c"][t]
        rec["M6_S_w"] = round(S, 4)
        rec["M6_dT_win_c"] = round(dT, 3)
        rec["M6_dT_win_95"] = [round(dT - hw_h, 3), round(dT + hw_h, 3)]
        rec["M6_hold_rise_c"] = {"60 s": round(c_a3 * S * Fstep(60), 2), "300 s": round(c_a3 * S * Fstep(300), 2), "plateau": round(c_a3 * S, 2)}
        rec["priority"] = meta.get("priority")
        rec["case"] = meta.get("case")
        out["tiles"][name] = rec
    js = os.path.join(POOL, "predictions-blind4.json")
    json.dump(out, open(js, "w"), indent=1, sort_keys=True)
    L = ["# M6's frozen predictions for blind pool 4 (Q137(m)), for E140", "",
         f"m6.json sha256 `{out['m6_sha256']}`; blind4.json `{out['pool_blind4_json_sha256']}`; counts-blind4.json `{out['counts_blind4_sha256']}`.",
         "D is W over the type's own zeros at 600 MHz on aifoundry3; dT is the die rise over the kinds harness's 4.5 s run from launch; hold = the same S held (E97's plateau, 0.9 C per board W, and the frozen step response).", "",
         "| tile | prio | M6 D (W) | 95% | M5 D (W) | M6 dT (C) | 95% | hold 60 s / 300 s / plateau (C) |", "|---|---|---:|---|---:|---:|---|---|"]
    for n, r in out["tiles"].items():
        if "error" in r:
            L.append(f"| `{n}` | | no count | | | | | |")
            continue
        h = r["M6_hold_rise_c"]
        L.append(f"| `{n}` | {r['priority']} | {r['M6_D_w']:.3f} | [{r['M6_D_95'][0]:.2f}, {r['M6_D_95'][1]:.2f}] | {r['M5_D_w']:.3f} | {r['M6_dT_win_c']:.2f} | [{r['M6_dT_win_95'][0]:.2f}, {r['M6_dT_win_95'][1]:.2f}] | {h['60 s']} / {h['300 s']} / {h['plateau']} |")
    open(os.path.join(POOL, "predictions-blind4.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
