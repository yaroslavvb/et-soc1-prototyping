#!/usr/bin/env python3
"""E180's noise model, from the energy catalogue's committed repeat runs (catalogue.json, 26 Sep 2026: three shuffled
passes on each of three cards, every configuration once a pass, 3 s bursts between idle brackets).

    python3 noise_e180.py --root <repo> --out noise-e180.json

For each card it reads every two-hart instruction configuration of the catalogue (unit "instruction", harts 2) and
gives, in watts above idle (over_idle_w, the reduction's leakage-corrected value):
  - sigma1: the pooled sd of one burst about its configuration's mean (df = sum of n - 1);
  - sigma_d: the median, over pairs of configurations in the same 5-30 W band, of the sd over passes of their
    within-pass difference (the noise of one pass's difference of two kinds, its pass-to-pass common part removed);
  - the same for the vector-unit configurations alone (the .ps / .pi rows), the class E180 measures;
  - the fadd rows themselves (zeros, const, random under fadd.ps and fadd.pi), per pass, and const - zeros per card.
No model enters; nothing is fitted.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import itertools
import json
import math
import os
import statistics as st

CARDS = ("aifoundry3", "aifoundry1-c1", "aifoundry2")
ROWS = ("fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2", "fadd.pi/zeros/h2", "fadd.pi/const/h2",
        "fadd.pi/random/h2")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cat = json.load(open(os.path.join(a.root, "docs/reports/data/2026-09-23-energy-manual/catalogue.json")))
    out = {"source": "docs/reports/data/2026-09-23-energy-manual/catalogue.json", "cards": {}}
    for card in CARDS:
        bl = [b for b in cat["bursts"][card] if b.get("unit") == "instruction" and b.get("harts") == 2]
        by = {}
        for b in bl:
            by.setdefault(b["cfg"], {})[b["pass"]] = b
        ss, df = 0.0, 0
        for cfg, ps in by.items():
            v = [p["over_idle_w"] for p in ps.values()]
            if len(v) >= 2:
                m = st.mean(v)
                ss += sum((x - m) ** 2 for x in v)
                df += len(v) - 1
        sigma1 = math.sqrt(ss / df)

        def pair_sd(cfgs):
            sds = []
            for x, y in itertools.combinations(cfgs, 2):
                px, py = by[x], by[y]
                common = sorted(set(px) & set(py))
                if len(common) < 3:
                    continue
                d = [px[p]["over_idle_w"] - py[p]["over_idle_w"] for p in common]
                sds.append(st.stdev(d))
            return st.median(sds) if sds else None, len(sds)

        band = [c for c, ps in by.items() if len(ps) == 3 and all(5 <= p["over_idle_w"] <= 30 for p in ps.values())]
        vec = [c for c in band if c.split("/")[0].endswith((".ps", ".pi"))]
        sd_band, n_band = pair_sd(band)
        sd_vec, n_vec = pair_sd(vec)
        # one burst's sd, the vector rows alone
        ssv, dfv = 0.0, 0
        for cfg in vec:
            v = [p["over_idle_w"] for p in by[cfg].values()]
            m = st.mean(v)
            ssv += sum((x - m) ** 2 for x in v)
            dfv += len(v) - 1
        rows = {}
        for r in ROWS:
            ps = by.get(r, {})
            rows[r] = {"pj_per_op": [round(ps[p]["pj_per_op"], 4) for p in sorted(ps)],
                       "over_idle_w": [round(ps[p]["over_idle_w"], 4) for p in sorted(ps)],
                       "ops_per_s": [ps[p]["ops_per_s"] for p in sorted(ps)],
                       "ops_per_cycle_per_hart": [ps[p]["ops_per_cycle_per_hart"] for p in sorted(ps)]}
        cz = {}
        for mode in ("fadd.ps", "fadd.pi"):
            z = rows[f"{mode}/zeros/h2"]["pj_per_op"]
            k = rows[f"{mode}/const/h2"]["pj_per_op"]
            rnd = rows[f"{mode}/random/h2"]["pj_per_op"]
            for name, x in (("const", k), ("random", rnd)):
                d = st.mean(x) - st.mean(z)
                se = math.sqrt(st.variance(x) / len(x) + st.variance(z) / len(z))
                cz[f"{mode}/{name}-zeros"] = {"pj": round(d, 4), "se_pj": round(se, 4)}
        out["cards"][card] = {"sigma1_w": round(sigma1, 4), "sigma1_df": df, "sigma1_vec_w": round(math.sqrt(ssv / dfv), 4),
                              "sigma1_vec_df": dfv, "sigma_d_band_w": round(sd_band, 4), "n_pairs_band": n_band,
                              "sigma_d_vec_w": round(sd_vec, 4), "n_pairs_vec": n_vec, "n_vec_cfgs": len(vec),
                              "rows": rows, "above_zeros": cz}
    json.dump(out, open(a.out, "w"), indent=1)
    for card, d in out["cards"].items():
        print(card, {k: v for k, v in d.items() if k not in ("rows",)})


if __name__ == "__main__":
    main()
