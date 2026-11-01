#!/usr/bin/env python3
"""E99 step 1, POST HOC, labelled: not registered, not scored, chosen after E75's and E81's data were seen.

    python3 tools/claims-v3/dm/posthoc_desk.py --e75 <E75 data dir> --e81 <E81 data dir> --builtins <dir> --out <json>

For every committed E75 and E81 DRAM image, the high-pin and pin-toggle counts per line (dm_enc.py), and least-squares
fits of the two experiments' measured watts over their own zeros anchors. --builtins holds src_replica.cpp's random.bin
and bern50.bin, checked against E81's counts.json sha256. The fits print how much of E81's 1.636 W (dp_bern - dp_c2)
and of the 63 % of E75's chord that counting bits missed each one gives back.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
from dm_enc import counts, lines_of  # noqa: E402
from make_mf import image, two_values  # noqa: E402

E81_ITEMS = ["dp_c1", "dp_s1", "dp_c2", "dp_s2", "dp_c4", "dp_s4", "dp_c2r", "dp_s2r", "dp_random", "dp_bern"]


def e75_points(mf):
    L = mf["levels"]["dram"]
    rungs = {}
    ks, ws, zs, rs = [], [], [], []
    for p in L["per_pass"]:
        ks.append(p["k"]["p80_W"])
        ws.append(p["w"]["p80_W"])
        zs.append(p["zeros_W"])
        rs.append(p["random_W"])
    ks, ws, zs, rs = (np.array(x, dtype=float) for x in (ks, ws, zs, rs))
    for j, k in enumerate(L["per_pass"][0]["k"]["x"]):
        rungs["mf_k%d" % k] = float((ks[:, j] - zs).mean())
    for j, w in enumerate(L["per_pass"][0]["w"]["x"]):
        rungs["mf_w%d" % w] = float((ws[:, j] - zs).mean())
    rungs["mf_random"] = float((rs - zs).mean())
    return rungs, float(L["transfers_per_s"])


def fit(X, y, terms, F, names):
    A = np.vstack([np.ones(len(names))] + [F[t] for t in terms]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    return coef, pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e75", required=True)
    ap.add_argument("--e81", required=True)
    ap.add_argument("--builtins", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(os.path.join(a.e81, "dp.json")))
    mf = json.load(open(os.path.join(a.e75, "mf.json")))

    imgs = {}
    for n in E81_ITEMS:
        if n in ("dp_random", "dp_bern"):
            buf = open(os.path.join(a.builtins, "random.bin" if n == "dp_random" else "bern50.bin"), "rb").read()
            if hashlib.sha256(buf).hexdigest() != d["counts"][n]["sha256"]:
                raise SystemExit("%s is not the image E81's counts.json describes" % n)
            imgs[n] = buf
        else:
            imgs[n] = open(os.path.join(a.e81, "gen", "srcs", n + ".bin"), "rb").read()
    for k in (0, 128, 256, 384, 512):
        imgs["mf_k%d" % k] = image(512, 4, *two_values(512, 4, k, 256))
    for w in (128, 384):
        imgs["mf_w%d" % w] = image(512, 4, *two_values(512, 4, 256, w))
    imgs["mf_random"] = imgs["dp_random"]
    C = {n: counts(lines_of(b)) for n, b in imgs.items()}

    y = {n: float(d["headline"]["items_over_zeros_W"][n]["mean"]) for n in E81_ITEMS}
    e75, lps = e75_points(mf)
    y.update(e75)
    names = list(y)
    Y = np.array([y[n] for n in names])
    F = {t: np.array([C[n][t] for n in names]) for t in
         ("w", "k", "hi", "t_enc", "t_raw", "half", "k_chan", "tx_enc")}
    print("E99 step 1, POST HOC: %d measured points, %d from E81 and %d from E75, watts over each experiment's own zeros"
          % (len(names), len(E81_ITEMS), len(e75)))
    print("%-10s %8s %7s %7s %7s %7s %7s %7s %7s" % ("item", "W/zeros", "w", "k", "hi", "t_enc", "t_raw", "half", "k_chan"))
    for n in names:
        c = C[n]
        print("%-10s %8.3f %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f"
              % (n, y[n], c["w"], c["k"], c["hi"], c["t_enc"], c["t_raw"], c["half"], c["k_chan"]))

    ix = {n: i for i, n in enumerate(names)}
    models = {
        "bits": ["w", "k"],
        "dbi": ["hi", "t_enc"],
        "bits+dbi": ["w", "hi", "t_enc"],
        "raw_pins": ["w", "t_raw"],
        "bits+chan": ["w", "k", "k_chan"],
        "dbi+chan": ["hi", "t_enc", "k_chan"],
        "w+hi+chan": ["w", "hi", "k_chan"],
        "w+t_raw+chan": ["w", "t_raw", "k_chan"],
        "w+t_enc+chan": ["w", "t_enc", "k_chan"],
        "w+hi+t_enc+chan": ["w", "hi", "t_enc", "k_chan"],
    }
    res = {"counts": C, "measured_W_over_zeros": y, "line_rate_per_s": lps, "models": {}}
    print("\nFits: floor + terms, watts; a term's price also in pJ per count at the measured line rate.")
    for name, terms in models.items():
        coef, pred = fit(None, Y, terms, F, names)
        r = Y - pred
        rms = float(np.sqrt(np.mean(r ** 2)))
        total = pred[ix["dp_bern"]] - pred[ix["dp_c2"]]
        arr = pred[ix["dp_s2"]] - pred[ix["dp_c2"]]
        per = pred[ix["dp_bern"]] - pred[ix["dp_s2"]]
        chord_pred = pred[ix["dp_random"]]                     # zeros is the origin, so the model's value over zeros
        floor = float(coef[0])
        prices = {t: float(v) for t, v in zip(terms, coef[1:])}
        print("%-16s rms %.3f W | floor %+.3f W | %s" % (
            name, rms, floor, "  ".join("%s %.3f pJ" % (t, v / lps * 1e12) for t, v in prices.items())))
        print("   dp_bern-dp_c2 %.3f of 1.636 W (%.0f %%) | arrangement s2-c2 %.3f of 0.996 | period bern-s2 %.3f of 0.640"
              " | zeros-to-random: %.3f of 3.222 W if the floor counts, %.3f if it does not"
              % (total, 100 * total / 1.636, arr, per, chord_pred, chord_pred - floor))
        print("   residuals W:", " ".join("%s %+.2f" % (n.replace("dp_", "").replace("mf_", "m"), v) for n, v in zip(names, r)))
        res["models"][name] = {"terms": terms, "floor_W": floor, "prices_W": prices,
                               "prices_pJ": {t: v / lps * 1e12 for t, v in prices.items()}, "rms_W": rms,
                               "residuals_W": {n: float(v) for n, v in zip(names, r)},
                               "pred_pattern_total_W": float(total), "pred_arrangement_W": float(arr),
                               "pred_period_W": float(per), "pred_random_over_zeros_W": float(chord_pred)}
    # how far the data can separate the counts
    print("\nCorrelations among the counts across these %d points:" % len(names))
    ts = ["w", "k", "hi", "t_enc", "t_raw", "half", "k_chan"]
    M = np.corrcoef(np.vstack([F[t] for t in ts]))
    print("        " + " ".join("%6s" % t for t in ts))
    for i, t in enumerate(ts):
        print("%-7s " % t + " ".join("%6.2f" % v for v in M[i]))
    res["correlations"] = {t: {u: float(M[i][j]) for j, u in enumerate(ts)} for i, t in enumerate(ts)}
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
