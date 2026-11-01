#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""A second model from the same counts, frozen per tile for E95 before its data: the operand bus gets its own price.

    predict_m4.py --counts <this dir> --data <docs/reports/data> --out m4-bench-prediction.json --table m4-bench-prediction.md

M4, floats, fitted on E78's 33 fp32 and fp16 kinds and on nothing else:

    D = rate * ( k_core * d(multiplier + adder and normaliser nets) + k_bus * d(lane operand bus nets) + k_rest * d(other nets) + a * d(clocked bits) )

I3, int8, fitted on E78's 15 int8 kinds alone, because its arithmetic is behavioural:

    D = rate * ( k * d(nets other than the lane operand bus) + k_bus * d(lane operand bus nets) + a * d(clocked bits) )

Why the bus: M2 runs low on every kind whose operands move on lanes the gate has closed, and a long wire costs more than a local net. The form was
chosen after reading E78, E82, E86, E88, E90, E92, E65, E67, E70, E60, E79 and E94 (see the README's section 11): so E94 is not a test of it. E95 is, as
long as this file's commit precedes E95's data commit; this script opens no E95 data.

The interval has the same form as predict_e94_e95.py's: t(0.975, n - 2) * sqrt(s^2 + x' C x + m^2), s from out-of-sample errors already read.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import re
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load  # noqa: E402

RANDOM = {"fp32": "randn", "fp16": "randn", "int8": "full"}
CPO = {"fp32": 546, "fp16": 546, "int8": 318}


def t975(nu):
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * nu) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * nu ** 2)


def x_float(m, z):
    s, q = m["vpu"]["by_stage"], z["vpu"]["by_stage"]
    core = s["multiplier"] + s["adder_norm"] - q["multiplier"] - q["adder_norm"]
    bus = s["lane_operand_bus"] - q["lane_operand_bus"]
    rest = m["vpu"]["nets_map"] - z["vpu"]["nets_map"] - core - bus
    return [core, bus, rest, m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]]


def x_int8(m, z):
    s, q = m["vpu"]["by_stage"], z["vpu"]["by_stage"]
    bus = s["lane_operand_bus"] - q["lane_operand_bus"]
    return [m["vpu"]["nets_map"] - z["vpu"]["nets_map"] - bus, bus, m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]]


def fit(X, y):
    sc = np.abs(X).max(axis=0)
    sc[sc == 0] = 1
    return np.linalg.lstsq(X / sc, y, rcond=None)[0] / sc


def rows(counts, items, zc, want):
    """-> keys, X (with each item's own rate), y for tiles with a measured D"""
    K, X, y = [], [], []
    for k, v in counts.items():
        t, name = v["type"], v["kind"]
        if not want(t) or name == "zeros":
            continue
        it = items.get(k) or items.get(f"{t}.real_{name}")
        if not it or not isinstance(it.get("D"), dict):
            continue
        rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) else 600e6 / CPO[t] * 1024 * 0.9963
        f = x_int8 if t == "int8" else x_float
        K.append(k)
        X.append([c * rate for c in f(v["mean"], zc[t + ".zeros"]["mean"])])
        y.append(it["D"]["mean"])
    return K, np.array(X, float), np.array(y, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--table", required=True)
    a = ap.parse_args()
    cd, dd = a.counts, a.data
    zc = load(f"{cd}/counts-v2.json")["rows"]
    e78 = load(f"{dd}/2026-10-31-e78-kinds-energy-matrix/e78.json")["items"]
    e82 = load(f"{dd}/2026-10-31-e82-kinds-aifoundry1/e82.json")["items"]
    rate = {t: e78[f"{t}.{RANDOM[t]}"]["rate"]["mean"] for t in RANDOM}
    tiles = load(f"{cd}/counts-e94e95.json")["rows"]
    real2 = load(f"{a.kinds}/real2/real2.json")["tiles"]
    res = {}
    sets = {"e86": ("2026-10-31-e86-real-tensors-energy/e86.json", "counts-e86.json"), "e90": ("2026-10-31-e90-signs-spread/e90.json", "counts-e90.json"),
            "e92": ("2026-11-01-e92-sign-split/e92.json", "counts-e92.json"), "e88": ("2026-10-31-e88-result-path/e88.json", "counts-e88.json")}
    out = {"_note": "M4 and I3: chosen after E94 was read, frozen before E95's data. No E95 measurement is in this file's inputs.", "families": {}, "e95_aifoundry3": {}, "e94_card1_not_blind": {}}
    for fam, want, f in (("float", lambda t: t != "int8", x_float), ("int8", lambda t: t == "int8", x_int8)):
        K, X, y = rows(zc, e78, zc, want)
        b = fit(X, y)
        loo = [float(y[i] - X[i] @ fit(np.delete(X, i, 0), np.delete(y, i))) for i in range(len(y))]
        jk = np.array([fit(np.delete(X, i, 0), np.delete(y, i)) for i in range(len(y))])
        d = jk - jk.mean(axis=0)
        C = d.T @ d * (len(y) - 1) / len(y)
        K82, X82, y82 = rows(zc, e82, zc, want)
        p82 = X82 @ b
        s = float((p82 @ y82) / (p82 @ p82))
        js = [float((np.delete(p82, i) @ np.delete(y82, i)) / (np.delete(p82, i) @ np.delete(p82, i))) for i in range(len(y82))]
        ms = sum(js) / len(js)
        se_s = math.sqrt(sum((x - ms) ** 2 for x in js) * (len(js) - 1) / len(js))
        # out-of-sample errors already read
        e_a3 = list(loo)
        by = {"E78 leave-one-out": float(np.sqrt(np.mean(np.square(loo))))}
        for n in ("e86", "e90", "e92"):
            j, c = sets[n]
            _, Xo, yo = rows(load(f"{cd}/{c}")["rows"], load(f"{dd}/{j}")["items"], zc, want)
            if len(yo):
                er = list(yo - Xo @ b)
                e_a3 += er
                by[n] = float(np.sqrt(np.mean(np.square(er))))
        e_c1 = list(y82 - s * p82)
        by["e82 after scale"] = float(np.sqrt(np.mean(np.square(e_c1))))
        _, X88, y88 = rows(load(f"{cd}/counts-e88.json")["rows"], load(f"{dd}/2026-10-31-e88-result-path/e88.json")["items"], zc, want)
        if len(y88):
            er = list(y88 - s * (X88 @ b))
            e_c1 += er
            by["e88 with e82's scale"] = float(np.sqrt(np.mean(np.square(er))))
        c94 = {k: v for k, v in tiles.items() if not v["kind"].startswith(("r2_", "real_"))}
        _, X94, y94 = rows(c94, load(f"{dd}/2026-11-01-e94-tile-spread/e94.json")["items"], zc, want)
        er = list(y94 - s * (X94 @ b))
        e_c1 += er
        by["e94 with e82's scale"] = float(np.sqrt(np.mean(np.square(er))))
        sa3 = {"rms_w": float(np.sqrt(np.mean(np.square(e_a3)))), "n": len(e_a3)}
        sc1 = {"rms_w": float(np.sqrt(np.mean(np.square(e_c1)))), "n": len(e_c1)}
        out["families"][fam] = {"coef_fJ": [float(x) * 1e15 for x in b], "terms": ["core nets", "lane operand bus nets", "other nets", "clocked bits"] if fam == "float" else ["nets other than the lane operand bus", "lane operand bus nets", "clocked bits"],
                                "coef_jackknife_se_fJ": [float(x) * 1e15 for x in np.sqrt(np.diag(C))], "n_fit": len(y), "fit_rms_w": float(np.sqrt(np.mean((y - X @ b) ** 2))), "loo_rms_w": by["E78 leave-one-out"],
                                "card1_scale_from_e82": s, "card1_scale_se": se_s, "out_of_sample_rms_w": by, "interval_pool": {"aifoundry3": sa3, "card1": sc1}}
        for k, v in tiles.items():
            if not want(v["type"]):
                continue
            t, name = v["type"], v["kind"]
            z = zc[t + ".zeros"]["mean"]
            x = np.array(f(v["mean"], z), float) * rate[t]
            p0 = float(x @ b)
            is95 = name.startswith(("r2_", "real_"))
            sc = 1.0 if is95 else s
            pts = [float((np.array(f(q, z), float) * rate[t]) @ b) * sc for q in v["points"]]
            m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
            pool = sa3 if is95 else sc1
            var = pool["rms_w"] ** 2 + sc * sc * float(x @ C @ x) + (0 if is95 else (p0 * se_s) ** 2) + m * m
            half = t975(pool["n"] - 2) * math.sqrt(var)
            row = {"type": t, "D_w": p0 * sc, "lo95": max(p0 * sc - half, 0.0), "hi95": p0 * sc + half, "half95": half, "terms_w": [float(c) * sc for c in x * b], "gate_closes": 1 - v["mean"]["valid_slots"] / 4096, "check_mismatch_words": v["mean"]["check_mismatch"]}
            if name.startswith("r2_"):
                row.update({"group": real2[t][name[3:]].get("group"), "blind": True})
                out["e95_aifoundry3"][k] = row
            elif name.startswith("real_"):
                row.update({"group": "E86 partner", "blind": False})
                out["e95_aifoundry3"][k] = row
            else:
                row.update({"rule": re.sub(r"_e9[04]d\d+$", "", name), "fresh": "_e94d" in name, "blind": False})
                out["e94_card1_not_blind"][k] = row
    json.dump(out, open(a.out, "w"), indent=1)
    with open(a.table, "w") as f_:
        w = f_.write
        w("# M4 and I3: frozen for E95\n\nWritten by `predict_m4.py`; D in W over the type's own zeros, on aifoundry3 card 0 at 600 MHz; no scale. The commit holding this file is the freeze. E94 is not a test of this form: it was read before the form was chosen.\n\n")
        for fam, F in out["families"].items():
            w(f"**{fam}:** " + ", ".join(f"{n} {c:.3f} ± {e:.3f} fJ" for n, c, e in zip(F["terms"], F["coef_fJ"], F["coef_jackknife_se_fJ"])) + f"; E78 fit rms {F['fit_rms_w']:.3f} W, leave-one-out {F['loo_rms_w']:.3f} W, over {F['n_fit']} kinds. Out-of-sample rms already read: " + ", ".join(f"{n} {v:.3f}" for n, v in F["out_of_sample_rms_w"].items() if n != "E78 leave-one-out") + f". Interval pool on this card: rms {F['interval_pool']['aifoundry3']['rms_w']:.3f} W over {F['interval_pool']['aifoundry3']['n']}.\n\n")
        w("| tile | group | g | **D, W [95%]** | core | bus | other nets | clocks |\n|---|---|---:|---:|---:|---:|---:|---:|\n")
        for k, r in sorted(out["e95_aifoundry3"].items(), key=lambda kv: (kv[0][:4], -kv[1]["D_w"])):
            tw = r["terms_w"]
            cols = f"{tw[0]:.2f} | {tw[1]:.2f} | {tw[2]:.2f} | {tw[3]:.2f}" if len(tw) == 4 else f"(all nets {tw[0]:.2f}) | {tw[1]:.2f} | | {tw[2]:.2f}"
            w(f"| `{k}`{'' if r['blind'] else ' (E86 read)'} | {r['group']} | {r['gate_closes']:.3f} | **{r['D_w']:.2f}** [{r['lo95']:.2f}, {r['hi95']:.2f}] | {cols} |\n")
    for fam, F in out["families"].items():
        print(fam, [round(c, 3) for c in F["coef_fJ"]], "fit", round(F["fit_rms_w"], 3), "loo", round(F["loo_rms_w"], 3), "scale", round(F["card1_scale_from_e82"], 4), {k: round(v, 3) for k, v in F["out_of_sample_rms_w"].items()}, F["interval_pool"])


if __name__ == "__main__":
    main()
