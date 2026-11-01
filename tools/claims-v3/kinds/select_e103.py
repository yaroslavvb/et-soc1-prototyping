#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103 (Q132): choose the tiles and freeze every model's prediction for them. Desk compute; nothing here opens a card.

    python3 tools/claims-v3/kinds/select_e103.py --pool <dir> --counts <counts-pool.json[,more]> --simple <simple-pool.json[,more]> \\
        --data docs/reports/data --bench docs/reports/data/2026-11-01-q132-rtl-bench

Reads: the pool's tiles and the bench's counts of them, Q130(n)'s predictor and E92's flop-price refit on them, and experiments already read (E78, E82, E86,
E88, E90, E92, E94, and E95 if it is on main). It writes e103/tiles/, e103/e103.json, e103/pool-predictions.json, and predictions-e103.json.

The selection is fixed by QUOTAS and the score below, and looks at no measurement of any pool tile, because none exists: inside each family of each format, take the
tiles where the bench's model and the simple predictors disagree most, with at most one tile from a design's stem. A tile the functional check flags cannot be chosen.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs/reports/data/2026-11-01-q132-rtl-bench"))
from predict_m4 import fit, rows, t975, x_float, x_int8  # noqa: E402

E82_NODIPS = "2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json"
# E82's per-type card scale, the one E94 registered for Q130(n)'s predictor (scored.json cross_card.primary.x3.per_type_median): aifoundry3 over card 1
RANDOM = {"fp32": "randn", "fp16": "randn", "int8": "full"}
CPO = {"fp32": 546, "fp16": 546, "int8": 318}

# (format, family test, how many, a label[, "m2"]): the families follow make_e103_pool.py. A test is a prefix, or a tuple of prefixes; "=name" is that tile alone. The score is the
# disagreement between the model and the simple predictors, except for the two rows marked "m2", where it is the disagreement between M4 and M2: there the tile tests the bus's own price.
QUOTAS = [
    ("fp32", ("s_abs", "s_arow_adds", "s_bhalf_adds", "s_a_rand", "s_b_rand", "s_kalt"), 1, "sign structure: moving sums, adder rarely alternates"),
    ("fp32", ("=s_bhalf_alt",), 1, "sign structure: moving sums, the adder alternates each cycle"),
    ("fp32", "c_", 1, "near-cancelling sums"), ("fp32", "e_", 1, "exponent spread"),
    ("fp32", "t_", 1, "truncated mantissas"), ("fp32", "h_a_", 2, "A side (named weak spot)"), ("fp32", "o_a_", 1, "A's order (named weak spot, E60's pair)"),
    ("fp32", "g_", 1, "gate share (named weak spot)"), ("fp32", "g_", 1, "gate share, operands moving on closed lanes", "m2"), ("fp32", "z_", 1, "-0.0 and denormal words"), ("fp32", "x_", 2, "combinations"),
    ("fp16", "s_", 1, "sign structure: moving sums, adder rarely alternates"), ("fp16", "c_", 1, "near-cancelling sums"), ("fp16", "e_", 1, "exponent spread"),
    ("fp16", "t_", 1, "truncated mantissas"), ("fp16", "h_a_", 1, "A side (named weak spot)"), ("fp16", "o_", 1, "order"),
    ("fp16", "g_", 1, "gate share (named weak spot)"), ("fp16", "g_", 1, "gate share, operands moving on closed lanes", "m2"), ("fp16", "f_", 1, "fp16's two elements"), ("fp16", "x_", 1, "combinations"),
    ("int8", "i_w", 2, "operand widths"), ("int8", ("i_afull", "i_a1_", "i_a127", "i_asign"), 2, "one side busy, the other still"),
    ("int8", ("i_bpair", "i_bword", "i_arow", "i_scatter"), 2, "gate share and zero bytes"), ("int8", ("i_sort", "i_anti", "i_bline"), 1, "order"),
]


def stem(name):
    """Tiles from one design differ only in a number or a suffix: at most one per stem. The H family's stem keeps its position."""
    if name.startswith(("i_w", "t_")):
        return name          # each pair of widths is its own design
    p = re.sub(r"\d+", "", name).split("_")
    return "_".join(p[:3] if name.startswith("h_") else p[:2])


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def x_m2(m, z):
    return [m["vpu"]["nets_map"] - z["vpu"]["nets_map"], m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]]


def model_on(counts_sets, zc, want, f):
    """X, y over several (counts, items) sets, with f as the feature map"""
    X, y = [], []
    for counts, items in counts_sets:
        for k, v in counts.items():
            t, name = v["type"], v["kind"]
            if not want(t) or name == "zeros":
                continue
            it = items.get(k) or items.get(f"{t}.real_{name}")
            if not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                continue
            rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) else 600e6 / CPO[t] * 1024 * 0.9963
            X.append([c * rate for c in f(v["mean"], zc[t + ".zeros"]["mean"])])
            y.append(it["D"]["mean"])
    return np.array(X, float), np.array(y, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--simple", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--bench", required=True)
    a = ap.parse_args()
    dd, cd = a.data, a.bench
    load = lambda p: json.load(open(p))
    pool = load(os.path.join(a.pool, "pool.json"))
    counts, simple = {}, {}
    for p in a.counts.split(","):
        counts.update(load(p)["rows"])
    for p in a.simple.split(","):
        simple.update(load(p))
    zc = load(f"{cd}/counts-v2.json")["rows"]
    e78 = load(f"{dd}/2026-10-31-e78-kinds-energy-matrix/e78.json")["items"]
    e82nd = load(f"{dd}/{E82_NODIPS}")["items"]
    x82 = load(f"{dd}/2026-10-31-e82-kinds-aifoundry1/scored.json")["cross_card"]["primary"]["x3"]["per_type_median"]
    flop = load(f"{dd}/2026-11-01-e92-sign-split/posthoc-fit.json")
    rate = {t: e78[f"{t}.{RANDOM[t]}"]["rate"]["mean"] for t in RANDOM}
    S = {n: (load(f"{cd}/{c}")["rows"], load(f"{dd}/{j}")["items"]) for n, (j, c) in {
        "E86": ("2026-10-31-e86-real-tensors-energy/e86.json", "counts-e86.json"), "E90": ("2026-10-31-e90-signs-spread/e90.json", "counts-e90.json"),
        "E92": ("2026-11-01-e92-sign-split/e92.json", "counts-e92.json"), "E88": ("2026-10-31-e88-result-path/e88.json", "counts-e88.json")}.items()}
    c9495 = load(f"{cd}/counts-e94e95.json")["rows"]
    S["E94"] = ({k: v for k, v in c9495.items() if not v["kind"].startswith(("r2_", "real_"))}, load(f"{dd}/2026-11-01-e94-tile-spread/e94.json")["items"])
    e95f = glob.glob(f"{dd}/2026-11-01-e95*/e95.json")
    if e95f:
        S["E95"] = ({k: v for k, v in c9495.items() if v["kind"].startswith(("r2_", "real_"))}, load(e95f[0])["items"])

    FAM = {"float": (lambda t: t != "int8", x_float), "int8": (lambda t: t == "int8", x_int8)}
    frozen = {}
    for fam, (want, f) in FAM.items():
        X, y = model_on([(zc, e78)], zc, want, f)
        b = fit(X, y)
        loo = [float(y[i] - X[i] @ fit(np.delete(X, i, 0), np.delete(y, i))) for i in range(len(y))]
        jk = np.array([fit(np.delete(X, i, 0), np.delete(y, i)) for i in range(len(y))])
        d = jk - jk.mean(axis=0)
        C = d.T @ d * (len(y) - 1) / len(y)
        X82, y82 = model_on([(zc, e82nd)], zc, want, f)
        p82 = X82 @ b
        s = float((p82 @ y82) / (p82 @ p82))
        js = [float((np.delete(p82, i) @ np.delete(y82, i)) / (np.delete(p82, i) @ np.delete(p82, i))) for i in range(len(y82))]
        se_s = math.sqrt(sum((v - sum(js) / len(js)) ** 2 for v in js) * (len(js) - 1) / len(js))
        # card 1's out-of-sample errors already read
        errs = list(y82 - s * p82)
        by = {"E82 after scale": float(np.sqrt(np.mean(np.square(errs))))}
        for n in ("E88", "E94"):
            Xo, yo = model_on([S[n]], zc, want, f)
            if len(yo):
                e = list(yo - s * (Xo @ b))
                errs += e
                by[n] = float(np.sqrt(np.mean(np.square(e))))
        pool_s = {"rms_w": float(np.sqrt(np.mean(np.square(errs)))), "n": len(errs)}
        # M2 (the first model): one net price
        X2, y2 = model_on([(zc, e78)], zc, want, x_m2)
        b2 = fit(X2, y2)
        X282, y282 = model_on([(zc, e82nd)], zc, want, x_m2)
        s2 = float(((X282 @ b2) @ y282) / ((X282 @ b2) @ (X282 @ b2)))
        # the same form fitted on every aifoundry3 kinds-like set already read (reported, never a rule)
        sets = [(zc, e78)] + [S[n] for n in ("E86", "E90", "E92", "E95") if n in S]
        XA, yA = model_on(sets, zc, want, f)
        bA = fit(XA, yA)
        pA = X82 @ bA
        sA = float((pA @ y82) / (pA @ pA))
        frozen[fam] = {"b": b, "C": C, "s": s, "se_s": se_s, "pool": pool_s, "by": by, "b2": b2, "s2": s2, "bA": bA, "sA": sA, "nA": len(yA), "n": len(y),
                       "fit_rms": float(np.sqrt(np.mean((y - X @ b) ** 2))), "loo_rms": float(np.sqrt(np.mean(np.square(loo))))}

    def fl(t, c):
        mod = flop["models"][f"{t}: four prices + flops"]
        ops = flop["ops_per_s"]
        return mod["F_w"] * c["live"] + sum(mod["prices_fj"][q] * 1e-15 * c[q] * ops for q in ("bus", "prod", "res", "flops"))

    preds = {}
    excluded = {}
    for k, v in sorted(counts.items()):
        t = v["type"]
        fam = "int8" if t == "int8" else "float"
        F = frozen[fam]
        f = FAM[fam][1]
        z = zc[t + ".zeros"]["mean"]
        x = np.array(f(v["mean"], z), float) * rate[t]
        s, b = F["s"], F["b"]
        p0 = float(x @ b)
        pts = [float((np.array(f(q, z), float) * rate[t]) @ b) * s for q in v["points"]]
        m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
        var = F["pool"]["rms_w"] ** 2 + s * s * float(x @ F["C"] @ x) + (p0 * F["se_s"]) ** 2 + m * m
        half = t975(F["pool"]["n"] - 2) * math.sqrt(var)
        r = {"type": t, "name": v["kind"], "M": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts,
             "terms_w": [float(c) * s for c in x * b], "M2": float(np.array(x_m2(v["mean"], z), float) @ F["b2"]) * rate[t] * F["s2"], "Mall": float(x @ F["bA"]) * F["sA"],
             "check_mismatch_words": v["mean"]["check_mismatch"], "gate_closes": 1 - v["mean"]["valid_slots"] / 4096, "bus_bits_per_op": pool[k]["bus_bits_per_op"],
             "q130n": simple[k]["q130n_w"] / x82[t], "q130n_outside_e78_range": simple[k]["q130n_outside"]}
        r["gate_law"] = (1 - r["gate_closes"]) * e82nd[f"{t}.{RANDOM[t]}"]["D"]["mean"]
        if t != "int8":
            r["flop"] = fl(t, simple[k]["counts_e92"]) / x82[t]
            r["dis"] = max(abs(r["M"] - r["q130n"]), abs(r["M"] - r["flop"]))
        else:
            r["flop"] = None
            r["dis"] = abs(r["M"] - r["q130n"])
        if v["mean"]["check_mismatch"] > 0:
            excluded[k] = f"the functional check flags {v['mean']['check_mismatch']:.1f} words"
        preds[k] = r

    chosen = {}
    for q in QUOTAS:
        t, test, n, label = q[:4]
        pre = (test,) if isinstance(test, str) else test
        match = lambda name: any(name == x[1:] if x.startswith("=") else name.startswith(x) for x in pre)
        score_of = (lambda k: -abs(preds[k]["M"] - preds[k]["M2"])) if len(q) > 4 else (lambda k: -preds[k]["dis"])
        cand = sorted((k for k, r in preds.items() if r["type"] == t and match(r["name"]) and k not in excluded and k not in chosen), key=score_of)
        taken = 0
        stems = set()
        for k in cand:
            st_ = stem(preds[k]["name"])
            if st_ in stems:
                continue
            stems.add(st_)
            chosen[k] = label
            taken += 1
            if taken == n:
                break
        assert taken == n, (t, test, taken)

    # write the tiles and e103.json
    T = os.path.join(HERE, "e103")
    if os.path.isdir(os.path.join(T, "tiles")):
        shutil.rmtree(os.path.join(T, "tiles"))
    tiles = {}
    for k, label in sorted(chosen.items()):
        t, name = k.split(".", 1)
        src = os.path.join(a.pool, t, name + ".bin")
        os.makedirs(os.path.join(T, "tiles", t), exist_ok=True)
        shutil.copy(src, os.path.join(T, "tiles", t, name + ".bin"))
        raw = open(src, "rb").read()
        assert hashlib.sha256(raw).hexdigest() == pool[k]["sha256"], k
        tiles[k] = {"type": t, "kind": name, "group": label, "rule": f"make_e103_pool.py, seed sha256('E103/{t}/{name}')", "file": f"tiles/{t}/{name}.bin", "bytes": len(raw),
                    "sha256": pool[k]["sha256"], "sha256_a": hashlib.sha256(raw[:1024]).hexdigest(), "sha256_b": hashlib.sha256(raw[1024:]).hexdigest(),
                    "stats": {"gated_lane_frac": pool[k]["gated_lane_frac"], "bus_bits_per_op": pool[k]["bus_bits_per_op"]}}
    by = lambda t, pre=(): sorted((k for k in chosen if k.startswith(t) and preds[k]["name"].startswith(pre or ("",))), key=lambda k: -preds[k]["M"])
    smoke = ["anchor_pi", by("fp32", ("g_",))[0], by("fp32", ("h_a_",))[0], "fp32.zeros", "fp32.randn", by("fp16")[0], by("int8")[0], "int8.zeros"]
    json.dump({"experiment": "E103", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/make_e103_pool.py, chosen by tools/claims-v3/kinds/select_e103.py", "smoke": smoke, "tiles": tiles},
              open(os.path.join(T, "e103.json"), "w"), indent=1, sort_keys=True)
    # every pool tile's predictions, so the choice can be checked
    json.dump({k: {q: (round(w, 4) if isinstance(w, float) else w) for q, w in r.items() if q not in ("launch_points_w", "terms_w")} for k, r in preds.items()},
              open(os.path.join(T, "pool-predictions.json"), "w"), indent=0, sort_keys=True)
    models = {}
    for fam, F in frozen.items():
        names = ["k_core", "k_bus", "k_rest", "a_clocked"] if fam == "float" else ["k_nets", "k_bus", "a_clocked"]
        models[fam] = {"primary": "M4" if fam == "float" else "I3", "coef_fJ": dict(zip(names, [float(v) * 1e15 for v in F["b"]])),
                       "coef_jackknife_se_fJ": dict(zip(names, [float(v) * 1e15 for v in np.sqrt(np.diag(F["C"]))])), "n_fit": F["n"], "fit_rms_w": F["fit_rms"], "loo_rms_w": F["loo_rms"],
                       "card1_scale": F["s"], "card1_scale_se": F["se_s"], "card1_scale_source": E82_NODIPS + " (E82, dips removed, E103's frame), through the origin over its kinds of this family",
                       "interval_pool": F["pool"], "out_of_sample_rms_w_card1": F["by"],
                       "M2": {"coef_fJ": {"k": float(F["b2"][0]) * 1e15, "a": float(F["b2"][1]) * 1e15}, "card1_scale": F["s2"]},
                       "Mall": {"coef_fJ": [float(v) * 1e15 for v in F["bA"]], "fitted_on_tiles": F["nA"], "card1_scale": F["sA"], "sets": ["E78"] + [n for n in ("E86", "E90", "E92", "E95") if n in S]}}
    out = {"models": models, "e82_per_type_scale_for_q130n_and_flop": x82, "chosen": {k: preds[k] for k in chosen}, "group": chosen, "excluded": excluded, "pool_size": len(preds), "e95_on_main_when_frozen": bool(e95f)}
    json.dump(out, open(os.path.join(T, "selection.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({k: {q: v for q, v in m.items() if q in ("coef_fJ", "card1_scale", "interval_pool", "n_fit", "fit_rms_w", "loo_rms_w", "out_of_sample_rms_w_card1")} for k, m in models.items()}, indent=0)[:1600])
    print("pool", len(preds), "excluded", len(excluded), excluded)
    print(f"{'tile':26s} {'g':>5s} {'M':>6s} [{'lo':>5s},{'hi':>6s}] {'M2':>6s} {'Mall':>6s} {'q130n':>6s} {'flop':>6s} {'gate':>6s} {'dis':>5s}  group")
    for k in sorted(chosen, key=lambda q: (q[:4], chosen[q])):
        r = preds[k]
        print(f"{k:26s} {r['gate_closes']:5.2f} {r['M']:6.2f} [{r['lo95']:5.2f},{r['hi95']:6.2f}] {r['M2']:6.2f} {r['Mall']:6.2f} {r['q130n']:6.2f} {(r['flop'] if r['flop'] is not None else float('nan')):6.2f} {r['gate_law']:6.2f} {r['dis']:5.2f}  {chosen[k]}")


if __name__ == "__main__":
    main()
