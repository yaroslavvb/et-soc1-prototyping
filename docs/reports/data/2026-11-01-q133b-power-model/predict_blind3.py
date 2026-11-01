#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q133(b): the frozen predictions for blind pool 3 (tools/claims-v3/kinds/blind3), from M5 (m5.json) and from M4 as frozen
for E103 (tools/claims-v3/kinds/predictions-e103.json), written before any card has run a pool tile.

    python3 predict_blind3.py      # writes tools/claims-v3/kinds/blind3/predictions-blind3.json and .md

Every predicted D is in W over the type's own zeros at 600 MHz, as E78's reduction reads it, on three footings:
  a3   aifoundry3 card 0, the card the constants are on (no scale);
  c1   aifoundry1 card 1, times that family's card-1 scale (M5: model-free from E82 against E78; M4: its frozen 0.9722 / 0.9721);
  new  a card with no scale of its own: the a3 figure, with the interval widened by |1 - card-1 scale| x D in quadrature
       (one card's step, a guess at the spread of cards, stated as such).
And as a ratio to the same model's prediction for its type's random anchor (fp32.randn, fp16.randn, int8.full), so a session
on any card can turn its own anchor into a prediction.

The interval: t(0.975, n - 2) x sqrt(pool^2 + x'Cx + m^2 [+ (D se_scale)^2 on c1]), pool = the rms of M5's nested
leave-one-kind-out errors on that format and card (M4: its frozen pool), C the jackknife covariance by kind, m the standard
error of the tile's three launch points.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m5 as F  # noqa: E402

POOL = os.path.join(F.K, "blind3")
ANCHOR = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
sha_file = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def m4_reproduced(rows):
    """Refit M4's form on E78's rows alone (its own fit set) and check the frozen constants come back; return the
    frozen coefficients and the jackknife covariance by kind, which predictions-e103.json does not store."""
    reg = F.load(os.path.join(F.K, "predictions-e103.json"))["models"]
    out = {}
    for fam, want, names, terms in (("float", lambda r: r["type"] != "int8", ("k_core", "k_bus", "k_rest", "a_clocked"), F.FORMS["float"]["F0_M4"]),
                                    ("int8", lambda r: r["type"] == "int8", ("k_nets", "k_bus", "a_clocked"), F.FORMS["int8"]["I0_I3"])):
        fr = [r for r in rows if want(r) and r["exp"] == "E78"]
        fam_ = F.Family(fr, {"m4": terms})
        b, _ = fam_.fit("m4", set())
        frozen = np.array([reg[fam]["coef_fJ"][q] for q in names]) * 1e-15
        rel = float(np.max(np.abs(b - frozen) / np.abs(frozen)))
        C = fam_.jackknife_cov("m4")
        out[fam] = {"b": frozen, "C": C, "terms": terms, "refit_rel_diff": rel, "n": len(fr), "scale": reg[fam]["card1_scale"],
                    "scale_se": reg[fam]["card1_scale_se"], "pool": reg[fam]["interval_pool"]}
    return out


def main():
    rows, _ = F.assemble()
    m5p = os.path.join(HERE, "m5.json")
    m5 = F.load(m5p)
    m4 = m4_reproduced(rows)
    zc = F.load(os.path.join(F.B, "counts-v2.json"))["rows"]
    zeros = {t: zc[f"{t}.zeros"]["mean"] for t in F.CPO}
    counts_p = os.path.join(POOL, "counts-blind3.json")
    cb = F.load(counts_p)["rows"]
    spec_p = os.path.join(POOL, "blind3.json")
    spec = F.load(spec_p)
    loko = F.load(os.path.join(HERE, "loko.json"))

    def feats_for(crow, t, path):
        f = F.fmt_feats(F.bench_feats(crow["mean"], zeros[t]), t)
        if path:
            f.update({k: v for k, v in F.tile_feats(path, t).items() if k != "sha256"})
        pts = [F.fmt_feats(F.bench_feats(q, zeros[t]), t) for q in crow["points"]]
        if path:
            tf = {k: v for k, v in F.tile_feats(path, t).items() if k != "sha256"}
            for p in pts:
                p.update(tf)
        return f, pts

    def model_pred(fam, f, pts, t, which):
        if which == "M5":
            M = m5["families"][fam]
            b, C, terms, s1 = np.array(M["coef_J"]), np.array(M["cov_J2"]), M["terms"], M["card1_scale"]
            pools = M["interval_pool_by_format_card"]
            pa3, pc1 = pools[f"{t}|a3"], pools[f"{t}|c1"]
            se_s = M.get("card1_scale_se", 0.0)
        else:
            M = m4[fam]
            b, C, terms, s1 = M["b"], M["C"], M["terms"], M["scale"]
            pa3 = pc1 = M["pool"]
            se_s = M["scale_se"]
        rate = F.RATE[t]
        x = np.array([rate * f[q] for q in terms])
        d = float(x @ b)
        lp = [float(np.array([rate * p[q] for q in terms]) @ b) for p in pts]
        m = float(np.std(lp, ddof=1) / math.sqrt(len(lp))) if len(lp) > 1 else 0.0
        xcx = float(x @ C @ x)
        out = {}
        for foot, sc, pool, extra in (("a3", 1.0, pa3, 0.0), ("c1", s1, pc1, (d * se_s) ** 2), ("new", 1.0, pa3, (abs(1 - s1) * d) ** 2)):
            half = F.t975(pool["n"] - 2) * math.sqrt(pool["rms_w"] ** 2 + sc * sc * xcx + (sc * m) ** 2 + extra)
            D = d * sc
            out[foot] = {"D_w": D, "lo95": D - half, "hi95": D + half, "half95": half}
        out["launch_points_w_a3"] = lp
        out["terms_w_a3"] = [float(v) for v in x * b]
        out["terms"] = terms
        return out

    # the anchors, for the ratio footing: E78's own tiles and counts
    anchors = {}
    for t, a in ANCHOR.items():
        fam = "int8" if t == "int8" else "float"
        f, pts = feats_for(zc[a], t, F.kinds_tile(t, a.split(".")[1]))
        anchors[a] = {w: model_pred(fam, f, pts, t, w)["a3"]["D_w"] for w in ("M5", "M4")}
    tiles = {}
    for name, v in sorted(spec["tiles"].items()):
        t = v["type"]
        fam = "int8" if t == "int8" else "float"
        crow = cb[name]
        path = os.path.join(POOL, v["file"])
        assert sha_file(path) == v["sha256"], name
        f, pts = feats_for(crow, t, path)
        rec = {"type": t, "kind": v["kind"], "open_case": v["open_case"], "priority": v["priority"], "group": v["group"],
               "sha256": v["sha256"], "check_mismatch_words": crow["mean"].get("check_mismatch"),
               "gate_closes": 1 - crow["mean"]["valid_slots"] / 4096.0}
        for w in ("M5", "M4"):
            p = model_pred(fam, f, pts, t, w)
            p["ratio_to_anchor"] = p["a3"]["D_w"] / anchors[ANCHOR[t]][w]
            rec[w] = p
        tiles[name] = rec
    out = {
        "experiment": "E115 (scores it); pool and predictions: Q133(b)",
        "date": "2026-11-01",
        "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6",
        "units": "D, W over the type's own zeros at 600 MHz (E78's reduction), footings a3 / c1 / new as this script's docstring says",
        "frozen_inputs": {
            "blind3.json": {"path": "tools/claims-v3/kinds/blind3/blind3.json", "sha256": sha_file(spec_p)},
            "counts-blind3.json": {"path": "tools/claims-v3/kinds/blind3/counts-blind3.json", "sha256": sha_file(counts_p)},
            "m5.json": {"path": "docs/reports/data/2026-11-01-q133b-power-model/m5.json", "sha256": sha_file(m5p)},
            "fit_m5.py": {"path": "docs/reports/data/2026-11-01-q133b-power-model/fit_m5.py", "sha256": sha_file(os.path.join(HERE, "fit_m5.py"))},
            "predict_blind3.py": {"path": "docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py", "sha256": sha_file(os.path.abspath(__file__))},
            "predictions-e103.json (M4 as frozen)": {"path": "tools/claims-v3/kinds/predictions-e103.json", "sha256": sha_file(os.path.join(F.K, "predictions-e103.json"))},
            "counts-v2.json (zeros, anchors)": {"path": "docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json", "sha256": sha_file(os.path.join(F.B, "counts-v2.json"))},
        },
        "models": {
            "M5": {fam: {k: v for k, v in M.items() if k != "cov_J2"} for fam, M in m5["families"].items()},
            "M4": {fam: {"coef_fJ": [float(x) * 1e15 for x in M["b"]], "terms": M["terms"], "card1_scale": M["scale"], "interval_pool": M["pool"],
                         "refit_on_e78_max_rel_diff": M["refit_rel_diff"], "jackknife_C_reproduced_on_e78_rows": M["n"]} for fam, M in m4.items()},
            "nested_loko_rms_w": {fam: loko["families"][fam]["nested_loko"]["all"] for fam in loko["families"]},
        },
        "anchors_predicted_a3_w": anchors,
        "tiles": tiles,
    }
    jp = os.path.join(POOL, "predictions-blind3.json")
    json.dump(out, open(jp, "w"), indent=1, sort_keys=True)
    with open(os.path.join(POOL, "predictions-blind3.md"), "w") as fo:
        w = fo.write
        w("# Blind pool 3: frozen predictions (Q133(b), for E115)\n\nWritten by `docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py`. D in W over the type's own zeros at 600 MHz; "
          "`a3` = aifoundry3 card 0 (no scale), `c1` = aifoundry1 card 1 (its scale), `new` = a card with no scale (a3's figure, wider). "
          "The commit holding this file is the freeze; no card had run a pool tile.\n\n")
        w("| tile | open case | prio | **M5 a3 [95%]** | M5 c1 [95%] | M5 new card [95%] | M4 a3 [95%] | M4 c1 | M5 / anchor |\n|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for name, r in sorted(tiles.items(), key=lambda kv: (kv[1]["open_case"], kv[0])):
            a, c, n_, q = r["M5"]["a3"], r["M5"]["c1"], r["M5"]["new"], r["M4"]["a3"]
            w(f"| `{name}` | {r['open_case']} | {r['priority']} | **{a['D_w']:.2f}** [{a['lo95']:.2f}, {a['hi95']:.2f}] | {c['D_w']:.2f} [{c['lo95']:.2f}, {c['hi95']:.2f}] | "
              f"{n_['D_w']:.2f} [{n_['lo95']:.2f}, {n_['hi95']:.2f}] | {q['D_w']:.2f} [{q['lo95']:.2f}, {q['hi95']:.2f}] | {r['M4']['c1']['D_w']:.2f} | {r['M5']['ratio_to_anchor']:.4f} |\n")
    print(json.dumps({"tiles": len(tiles), "predictions_sha256": sha_file(jp), "m4_refit_rel_diff": {k: v["refit_rel_diff"] for k, v in m4.items()}}))


if __name__ == "__main__":
    main()
