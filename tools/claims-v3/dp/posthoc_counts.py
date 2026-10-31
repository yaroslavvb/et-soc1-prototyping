#!/usr/bin/env python3
"""E81 POST HOC, labelled (departure D2): not registered, not scored, chosen after the data were seen.

    python3 tools/claims-v3/dp/posthoc_counts.py docs/reports/data/2026-10-31-e81-dram-pattern [--builtins DIR]

How far can per-line counts account for E81's ten data items? Least squares, with no intercept (zeros is the origin:
0 counts, 0 W), of each item's headline power over zeros (dp.json headline.items_over_zeros_W, converted to pJ per
64 B line with the measured line rate headline.lines_per_s) on candidate per-line counts from gen/counts.json
(copied into dp.json `counts` by the registered reducer). The counts themselves are registered (make_dp.py --check);
the model search is not.

The seven candidate counts:
  w          ones per line
  k          bits changed between consecutive lines of a hart's stream
  beat16     toggles between consecutive 16-bit pieces of the stream (in-order mapping, as make_dp.py counts them)
  beat32     the same for 32-bit pieces
  beat64     the same for 64-bit pieces
  half       bits that differ between a line's two 32 B halves
  k_if_long  k, counted only when the stream has more than 4 distinct lines (alphabet_size > 4: dp_bern and
             dp_random); this covariate was built AFTER the data showed that a 4-line cycle costs what a 2-line one does
Every 2-, 3- and 4-subset that contains w is fitted: 6 + 15 + 20 = 41 models, all printed, best first. With ten items
and up to four free coefficients, the best of 41 is a description of these items, not a measurement of a mechanism.

--builtins DIR adds a second candidate encoding, named after the verification of 31 Oct 2026: LPDDR4x read DBI-DC
(a byte with more than four ones is sent inverted, with its DBI pin driven high; E75's registration named data-bus
inversion as a risk). Its count, dbi_dc, is the pins driven high per line after inversion (per byte: the ones if
there are at most four, else 9 - ones, the DBI pin included), read from the image bytes: gen/srcs/<item>.bin for the
eight file images, and DIR/random.bin and DIR/bern50.bin for the two built-in operands, rebuilt by src_replica.cpp
with a GCC libstdc++ and checked against counts.json's sha256 before use. Only four head-to-head fits are printed
(the 16-bit-toggle model and the DBI-DC model, at three and at four counts), so this adds no search of its own.
"""
import argparse
import hashlib
import itertools
import json
import os

import numpy as np

NAMES = ["dp_c1", "dp_s1", "dp_c2", "dp_s2", "dp_c4", "dp_s4", "dp_bern", "dp_c2r", "dp_s2r", "dp_random"]
COUNTS = ["w", "k", "beat16", "beat32", "beat64", "half", "k_if_long"]


def fit(F, y, combo):
    X = np.vstack([F[c] for c in combo]).T
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    return float(np.sqrt(np.mean(res ** 2))), coef, res


def show(rms, combo, coef, res):
    print("rms %6.1f pJ/line  %s" % (rms, "  ".join("%s %.3f pJ" % (c, v) for c, v in zip(combo, coef))))
    print("      residuals:", " ".join("%s %+.0f" % (n[3:], v) for n, v in zip(NAMES, res)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="the E81 data directory (dp.json, gen/)")
    ap.add_argument("--builtins", help="directory with random.bin and bern50.bin from src_replica.cpp")
    a = ap.parse_args()

    d = json.load(open(os.path.join(a.data, "dp.json")))
    H, C = d["headline"], d["counts"]
    lps = H["lines_per_s"]
    y = np.array([H["items_over_zeros_W"][n]["mean"] / lps * 1e12 for n in NAMES])   # pJ per line over zeros
    long_ = np.array([1.0 if C[n]["alphabet_size"] > 4 else 0.0 for n in NAMES])
    F = {c: np.array([C[n][c] for n in NAMES], dtype=float) for c in COUNTS if c != "k_if_long"}
    F["k_if_long"] = F["k"] * long_

    print("E81 POST HOC (D2): per-line count models of the ten data items; headline passes %s; line rate %.4e lines/s"
          % (d["passes_headline"], lps))
    print("pJ per line over zeros:", dict(zip(NAMES, [float(v) for v in np.round(y, 1)])))
    out = []
    for r in (2, 3, 4):
        for combo in itertools.combinations(COUNTS, r):
            if "w" in combo:
                out.append((combo,) + fit(F, y, combo))
    out.sort(key=lambda t: t[1])
    print("%d models (every 2-, 3- and 4-subset of %s that contains w), best first:" % (len(out), ", ".join(COUNTS)))
    for i, (combo, rms, coef, res) in enumerate(out, 1):
        print("#%-2d " % i, end="")
        show(rms, combo, coef, res)

    # how much of random floats' saving over random bits (dp_bern - dp_random) the best model accounts for
    combo, rms, coef, res = out[0]
    ib, ir = NAMES.index("dp_bern"), NAMES.index("dp_random")
    parts = {c: float(v * (F[c][ib] - F[c][ir])) for c, v in zip(combo, coef)}
    print("\nthe best model (#1) on dp_bern - dp_random: predicted %+.1f pJ/line (%s) against measured %+.1f pJ/line"
          % (sum(parts.values()), ", ".join("%s %+.1f" % kv for kv in parts.items()), y[ib] - y[ir]))

    if a.builtins:
        pop = np.array([bin(i).count("1") for i in range(256)])
        dbi = np.where(pop > 4, 9 - pop, pop)                  # pins driven high per byte, DBI pin included
        F["dbi_dc"] = np.zeros(len(NAMES))
        print("\nLPDDR4x read DBI-DC, the second candidate encoding (named after the verification):")
        for i, n in enumerate(NAMES):
            if n in ("dp_random", "dp_bern"):
                fn = "random.bin" if n == "dp_random" else "bern50.bin"
                buf = open(os.path.join(a.builtins, fn), "rb").read()
                ok = hashlib.sha256(buf).hexdigest() == C[n].get("sha256")
                print("  %s: %s sha256 %s counts.json" % (n, fn, "matches" if ok else "DOES NOT MATCH"))
                if not ok:
                    raise SystemExit("the built-in image is not the one counts.json describes")
            else:
                buf = open(os.path.join(a.data, "gen", "srcs", n + ".bin"), "rb").read()
            lines = np.frombuffer(buf, dtype=np.uint8).reshape(-1, 64)
            F["dbi_dc"][i] = dbi[lines].sum(1).mean()
        print("  dbi_dc per line:", {n: round(float(v), 1) for n, v in zip(NAMES, F["dbi_dc"])})
        print("  head to head (the same number of counts, each with w and k_if_long):")
        for combo in (("w", "beat16", "k_if_long"), ("w", "dbi_dc", "k_if_long"),
                      ("w", "beat16", "half", "k_if_long"), ("w", "dbi_dc", "half", "k_if_long")):
            rms, coef, res = fit(F, y, combo)
            print("  ", end="")
            show(rms, combo, coef, res)


if __name__ == "__main__":
    main()
