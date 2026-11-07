#!/usr/bin/env python3
"""Q153(m10acc), POST HOC, after the registered fit (fit_m10acc.py fit): why the accumulator-toggle term carries nothing beyond M10.
Readings only; nothing here is fitted into M10-ACC, and no rule reads it.

    python3 -B posthoc_m10acc.py --out <data dir>      # reads rows-m10acc.json there and M9's committed rows; writes posthoc-m10acc.json, .txt

(1) The single-bit lists' steps (rows (c), 70): does a step's measured watts follow its x_acc step (the item's x_acc less its zero's)?
    Pearson r of the measured step with z_acc's step, and with M10 as frozen's step (pred_w), and by bit field.
(2) M10's float whole tiles (M9's rows less E147's steps): how much of x_acc M10's own float features already carry (r with c_end,
    the R^2 of x_acc on the frozen form's ten features).
(3) x_acc per micro-op by class: pool 8's class S, M10's S class, E178's one-word floats, M10's other whole tiles.
(4) One-number int8 kinds: x_acc depends on the product of the two words' bytes only, so (a, b) and (b, a) read the same.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M9ROWS = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q140m-m9", "rows-m9.json")
M10J = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q142m-m10", "m10.json")
UOPS = {"fp32": 512, "fp16": 512, "int8": 256}


def r_of(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def q(xs):
    xs = np.asarray(xs, float)
    return {"n": int(len(xs)), "p10": float(np.percentile(xs, 10)), "median": float(np.median(xs)), "p90": float(np.percentile(xs, 90))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = json.load(open(os.path.join(a.out, "rows-m10acc.json")))
    out, L = {"_what": "POST HOC readings after M10-ACC's registered fit (posthoc_m10acc.py); none is a test"}, []
    # (1) the lists' steps
    c = [r for r in rows if r["src"] == "c"]
    meas = [r["e"] for r in c]
    terms = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-06-q145b-m10-s", "note2-term-s-reg-99.json")))["steps"]
    by = {(s["run"], f"{s['fmt']}.{s['item']}"): s for s in terms}
    mw = [by[(r["exp"], r["key"])]["meas_w"] for r in c]
    pw = [by[(r["exp"], r["key"])]["pred_w"] for r in c]
    za = [r["z"][0] for r in c]
    xa = [r["x_acc"] for r in c]
    out["lists_steps"] = {"n": len(c), "r_measured_step_with_z_acc_step": r_of(mw, za), "r_measured_step_with_M10_step": r_of(mw, pw),
                          "x_acc_step_per_uop": q([x / UOPS[r["type"]] for x, r in zip(xa, c)]),
                          "measured_step_w": q(mw)}
    fields = {}
    for r, m_, z_ in zip(c, mw, za):
        fields.setdefault(r.get("field") or "?", []).append((m_, z_))
    out["lists_steps"]["r_by_field"] = {k: {"n": len(v), "r": r_of([x[0] for x in v], [x[1] for x in v])} for k, v in sorted(fields.items())}
    L.append(f"(1) the lists' 70 steps: r(measured step, z_acc step) {out['lists_steps']['r_measured_step_with_z_acc_step']:+.3f}; "
             f"r(measured step, M10's step) {out['lists_steps']['r_measured_step_with_M10_step']:+.3f}; x_acc's step per micro-op: median "
             f"{out['lists_steps']['x_acc_step_per_uop']['median']:+.2f} (p10 {out['lists_steps']['x_acc_step_per_uop']['p10']:+.2f}, p90 "
             f"{out['lists_steps']['x_acc_step_per_uop']['p90']:+.2f}); measured steps median {out['lists_steps']['measured_step_w']['median']:.3f} W")
    for k, v in out["lists_steps"]["r_by_field"].items():
        L.append(f"    field {k}: n {v['n']}, r {v['r'] if v['r'] is None else round(v['r'], 3)}")
    # (2) M10's float whole tiles: x_acc against M10's own features
    m9 = {(x["exp"], x["card"], x["key"]): x for x in json.load(open(M9ROWS))}
    terms10 = json.load(open(M10J))["families"]["float"]["terms"]
    X, y, ce = [], [], []
    for r in rows:
        if r["src"] != "a" or r["fam"] != "float" or r["exp"] == "E147":
            continue
        s = m9.get((r["exp"], r["card"], r["key"]))
        if s is None:
            continue
        X.append([float(s["f"][t]) for t in terms10])
        y.append(r["x_acc"])
        ce.append(float(s["f"]["c_end"]))
    X, y = np.array(X), np.array(y)
    coef, *_ = np.linalg.lstsq(np.column_stack([X, np.ones(len(y))]), y, rcond=None)
    yh = np.column_stack([X, np.ones(len(y))]) @ coef
    r2 = 1 - float(np.sum((y - yh) ** 2)) / float(np.sum((y - y.mean()) ** 2))
    out["m10_float_whole_tiles"] = {"n": int(len(y)), "r_x_acc_with_c_end": r_of(y, ce), "R2_x_acc_on_m10_features": r2,
                                    "features": terms10}
    L.append(f"(2) M10's float whole tiles (M9's rows, no steps): n {len(y)}; r(x_acc, c_end) {out['m10_float_whole_tiles']['r_x_acc_with_c_end']:+.3f}; "
             f"R^2 of x_acc on M10's ten float features {r2:.3f}")
    # (3) x_acc per micro-op by class
    cls = {"pool 8 class S": [r for r in rows if r["src"] == "b" and r.get("s_class")],
           "M10 S class": [r for r in rows if r["src"] == "a" and r.get("s_class")],
           "E178 one-word floats": [r for r in rows if r["src"] == "d" and r["fam"] == "float"],
           "M10 other float whole tiles": [r for r in rows if r["src"] == "a" and r["fam"] == "float" and not r.get("s_class") and r["exp"] != "E147"],
           "E178 int8": [r for r in rows if r["src"] == "d" and r["fam"] == "int8"],
           "M10 int8 whole tiles": [r for r in rows if r["src"] == "a" and r["fam"] == "int8"]}
    out["x_acc_per_uop_by_class"] = {k: q([r["x_acc"] / UOPS[r["type"]] for r in v]) for k, v in cls.items()}
    L.append("(3) x_acc per micro-op (the lanes of one micro-op summed), p10 / median / p90:")
    for k, v in out["x_acc_per_uop_by_class"].items():
        L.append(f"    {k:30s} n {v['n']:4d}  {v['p10']:7.2f} / {v['median']:7.2f} / {v['p90']:7.2f}")
    # (4) one-number int8: (a, b) and (b, a)
    fe = json.load(open(os.path.join(a.out, "forecasts-e182-m10acc.json")))["kinds"]
    i8 = {(k["a"], k["b"]): k["x_acc_per_op"] for k in fe if k["type"] == "int8"}
    pairs = [(x, y_) for (x, y_) in i8 if x < y_]
    same = sum(1 for (x, y_) in pairs if abs(i8[(x, y_)] - i8[(y_, x)]) < 1e-9)
    out["int8_one_number_symmetry"] = {"pairs": len(pairs), "equal": same}
    L.append(f"(4) one-number int8 grid: {same} of {len(pairs)} (a, b) / (b, a) pairs read the same x_acc (the step is 4 x a x b)")
    json.dump(out, open(os.path.join(a.out, "posthoc-m10acc.json"), "w"), indent=1, sort_keys=True)
    txt = "POST HOC (after the registered fit; readings, not tests)\n" + "\n".join(L) + "\n"
    open(os.path.join(a.out, "posthoc-m10acc.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
