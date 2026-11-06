#!/usr/bin/env python3
"""E180's dated note A1 (E180.md.dated-note-A1.md section 2): the noise model's level, re-read from the same pairs the registration used.

    python3 -B tools/claims-v3/e180/noise_e180_a1.py --root . --out tools/claims-v3/e180/noise/noise-e180-a1.json
    python3 -B tools/claims-v3/e180/noise_e180_a1.py --root . --out <file> --check tools/claims-v3/e180/noise/noise-e180-a1.json

The registration's sigma_d (noise_e180.py, unchanged) is the MEDIAN over pairs of vector-unit configurations of the sd over three passes
of their within-pass difference. Each such sd has 2 degrees of freedom, so for Gaussian noise its median is sqrt(ln 2) = 0.8326 of the
true sd: the median reads low (the adversarial verifier's fault 3). This re-reads exactly those pairs (the same cards, rows, band and
pairing as noise_e180.py, which it re-implements line for line and checks against the committed noise-e180.json) and gives, per card:
  - the registered median (a check: it must equal noise-e180.json's sigma_d_vec_w and n_pairs_vec);
  - the debiased median, median / sqrt(ln 2);
  - the pooled rms, sqrt(mean of the pair variances), the unbiased estimate of the variance if every pair had one sd;
  - the same two over the NEAR pairs, whose two configurations' mean power over idle differs by at most 1 W (E180's kinds sit within
    about 5 W of each other, most within 1 W);
  - the quantiles of the pair sds against the chi distribution with 2 degrees of freedom (a heavy tail reads as rms > debiased median);
  - the fifteen within-pass pairs of the catalogue's own six fadd rows (fadd.ps and fadd.pi zeros, const, random), reported.
No model enters and nothing is fitted: these are statistics of committed data, read after the registration (post hoc to it, before any
E180 datum). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import itertools
import json
import math
import os
import statistics as st
import sys

CARDS = ("aifoundry3", "aifoundry1-c1", "aifoundry2")
FADD = ("fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2", "fadd.pi/zeros/h2", "fadd.pi/const/h2", "fadd.pi/random/h2")
NEAR_W = 1.0
C2 = math.sqrt(math.log(2))          # the median of sqrt(chi2_2 / 2)


def r6(x):
    return float(f"{x:.6g}")


def chi2q(q):
    """the q-quantile of sqrt(chi2_2 / 2): chi2_2 is exponential with mean 2, so sqrt(-ln(1 - q))"""
    return math.sqrt(-math.log(1 - q))


def by_cfg(cat, card):
    bl = [b for b in cat["bursts"][card] if b.get("unit") == "instruction" and b.get("harts") == 2]
    by = {}
    for b in bl:
        by.setdefault(b["cfg"], {})[b["pass"]] = b
    return by


def pair_sds(cat, card):
    """[(sd over passes of the within-pass difference, |difference of the two configurations' means|)] for noise_e180.py's pairs"""
    by = by_cfg(cat, card)
    band = [c for c, ps in by.items() if len(ps) == 3 and all(5 <= p["over_idle_w"] <= 30 for p in ps.values())]
    vec = [c for c in band if c.split("/")[0].endswith((".ps", ".pi"))]
    pairs = []
    for x, y in itertools.combinations(vec, 2):
        px, py = by[x], by[y]
        common = sorted(set(px) & set(py))
        if len(common) < 3:
            continue
        d = [px[p]["over_idle_w"] - py[p]["over_idle_w"] for p in common]
        gap = abs(st.mean(v["over_idle_w"] for v in px.values()) - st.mean(v["over_idle_w"] for v in py.values()))
        pairs.append((st.stdev(d), gap))
    return pairs


def card_stats(cat, card):
    by = by_cfg(cat, card)
    pairs = pair_sds(cat, card)
    sds = [s for s, _ in pairs]
    near = [s for s, g in pairs if g <= NEAR_W]
    med, nmed = st.median(sds), st.median(near)
    srt = sorted(sds)
    qs = {}
    for q in (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99):
        emp = srt[min(len(srt) - 1, int(q * len(srt)))]
        qs[f"q{int(q * 100):02d}"] = {"empirical_w": r6(emp), "chi2_2_at_debiased_w": r6(chi2q(q) * med / C2)}
    fadd = {}
    for a, b in itertools.combinations(FADD, 2):
        if a in by and b in by:
            d = [by[a][p]["over_idle_w"] - by[b][p]["over_idle_w"] for p in sorted(set(by[a]) & set(by[b]))]
            fadd[f"{a} - {b}"] = {"diffs_w": [r6(v) for v in d], "sd_w": r6(st.stdev(d))}
    return {"n_pairs": len(sds), "median_w": round(med, 4), "median_w_full": r6(med), "debiased_median_w": r6(med / C2),
            "rms_w": r6(math.sqrt(st.mean(s * s for s in sds))),
            "n_near_pairs": len(near), "near_median_w": r6(nmed), "near_debiased_median_w": r6(nmed / C2),
            "near_rms_w": r6(math.sqrt(st.mean(s * s for s in near))),
            "share_above_2x_debiased": r6(sum(1 for s in sds if s > 2 * med / C2) / len(sds)),
            "share_above_2x_debiased_if_chi2_2": r6(math.exp(-4.0)),
            "quantiles": qs, "fadd_row_pairs": fadd}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", default=None, help="the committed file to compare with, byte for byte")
    a = ap.parse_args()
    cat = json.load(open(os.path.join(a.root, "docs/reports/data/2026-09-23-energy-manual/catalogue.json")))
    reg = json.load(open(os.path.join(a.root, "tools/claims-v3/e180/noise/noise-e180.json")))
    out = {"what": "E180 dated note A1: the noise level re-read from the registration's own pairs (noise_e180_a1.py)",
           "source": "docs/reports/data/2026-09-23-energy-manual/catalogue.json", "near_pair_w": NEAR_W,
           "median_to_sd_for_2_df": r6(C2), "cards": {}, "checks": {}}
    for card in CARDS:
        s = card_stats(cat, card)
        out["cards"][card] = s
        rc = reg["cards"][card]
        out["checks"][card] = {"median_equals_registered": s["median_w"] == rc["sigma_d_vec_w"],
                               "n_pairs_equal_registered": s["n_pairs"] == rc["n_pairs_vec"]}
    txt = json.dumps(out, indent=1, sort_keys=True) + "\n"
    open(a.out, "w").write(txt)
    ok = all(v for c in out["checks"].values() for v in c.values())
    for card, s in out["cards"].items():
        print(f"{card}: {s['n_pairs']} pairs; median {s['median_w']} (registered {reg['cards'][card]['sigma_d_vec_w']}), "
              f"debiased {s['debiased_median_w']}, rms {s['rms_w']}; near pairs {s['n_near_pairs']}: median {s['near_median_w']}, "
              f"debiased {s['near_debiased_median_w']}, rms {s['near_rms_w']}")
    print("registered median and pair count reproduced: " + ("yes" if ok else "NO"))
    if a.check:
        same = open(a.check).read() == txt
        print("CHECK PASS: byte for byte" if same else "CHECK FAIL")
        sys.exit(0 if same and ok else 1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
