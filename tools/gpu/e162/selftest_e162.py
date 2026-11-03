"""E162's selftest (E162.md): run before any GPU call. Prints to stdout (committed as selftest.txt).

(a) analyze_e162's reduction, run on E149's committed stage-1 logs, reproduces E149's committed reduce-stage1.json.
(b) Synthetic feature records with a known row+K truth at (s, r) = (16, 8): the RK procedure finds (16, 8), its fully
    nested error sits at the noise, STABLE holds, and on held-out synthetic kinds BEAT holds against the G1 form.
(c) A truth in the G1 form (lag 1, no row term): RK finds no resolved gain, so BEAT fails, and STABLE fails on its
    part (ii) (its extra row terms cost out of kind against G1's form).
(d) The bootstrap rule on hand-made errors.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_e162 as Z  # noqa: E402

A9 = Z.A9


def part_a():
    run1 = os.path.join(Z.E149_DIR, "logs", "e149-20261102-r1")
    mine = Z.reduce_run(run1)
    ref = Z._jload(os.path.join(Z.E149_DIR, "reduce-stage1.json"))
    worst = 0.0
    nk = 0
    for k, v in ref["kinds"].items():
        w = mine["kinds"][k]
        assert w["n"] == v["n"] and w["n_all"] == v["n_all"], k
        if v["y"] is not None:
            worst = max(worst, abs(w["y"] - v["y"]), abs((w["se"] or 0) - (v["se"] or 0)))
            nk += 1
    print(f"(a) reduce on E149's stage-1 logs: {nk} kinds, max |dy|, |dse| = {worst:.3e} W "
          f"({'REPRODUCES' if worst < 1e-9 else 'DIFFERS'})")
    return worst < 1e-9


def _fake_fe(rng, fmt):
    W = 8 if fmt == "int8" else 16
    fe = {"fmt": fmt, "A": {}, "B": {}, "cross": {}}
    for side in ("A", "B"):
        d = {"ones": list(rng.uniform(0, 1, W))}
        for s in Z.LAGS:
            d[f"lag{s}"] = list(rng.uniform(0, 0.5, W) * rng.uniform(0, 1))
        for r in Z.RLAGS:
            d[f"rlag{r}"] = list(rng.uniform(0, 0.5, W) * rng.uniform(0, 1))
        d["row"] = d["rlag1"]
        fe[side] = d
    c = fe["cross"]
    c["nzprod"] = float(rng.uniform(0.2, 1.0))
    c["negprod"] = float(rng.uniform(0, 0.5))
    for s in Z.LAGS:
        c[f"psgn{s}"] = float(rng.uniform(0, 0.5) * rng.uniform(0, 1))
        c[f"gtr{s}"] = float(rng.uniform(0, 0.3) * rng.uniform(0, 1))
    for r in Z.RLAGS:
        c[f"gtrR{r}"] = float(rng.uniform(0, 0.3) * rng.uniform(0, 1))
    fe["acc"] = {"acc": float(rng.uniform(0, 1))}
    return fe


def _truth_rk(fe, s, r, coefs):
    names, x = Z.rk_features(fe, s, r)
    return float(np.dot(x, [coefs[fe["fmt"]].get(n, 0.0) for n in names]))


def _truth_g1(fe, coefs):
    names, x = A9.features(fe, "G1", 1)
    return float(np.dot(x, [coefs[fe["fmt"]].get(n, 0.0) for n in names]))


COEF = {"bf16": {"nzprod": 40, "gtr": -10, "gtrR": 20, "flip_sign": 15, "flip_exp": 8, "flip_mant": 10, "pos_mant": -5,
                 "asym": 3, "psgn": 20, "rflip_sign": 25, "rflip_exp": 12, "rflip_mant": 14, "rasym": 4},
        "fp16": {"nzprod": 30, "gtr": -8, "gtrR": 15, "flip_sign": 10, "flip_exp": 6, "flip_mant": 9, "asym": 2,
                 "psgn": 15, "rflip_sign": 18, "rflip_exp": 9, "rflip_mant": 11, "rasym": 3},
        "int8": {"nzprod": 20, "gtr": -6, "gtrR": 10, "flip_sign": 8, "flip_high": 9, "flip_low": 7, "asym": 2,
                 "psgn": 10, "rflip_sign": 12, "rflip_high": 10, "rflip_low": 9, "rasym": 2}}


def _sets(rng, truth, nfit=(70, 25, 25), noise=2.0):
    sets, held = {}, []
    for f, n in zip(("bf16", "fp16", "int8"), nfit):
        rows = []
        for i in range(n):
            fe = _fake_fe(rng, f)
            rows.append((f"{f}.k{i}", fe, truth(fe) + rng.normal(0, noise)))
        sets[f] = Z.RowSet(rows)
        for i in range(8):
            fe = _fake_fe(rng, f)
            held.append((f"{f}.h{i}", fe, truth(fe) + rng.normal(0, noise)))
    return sets, held


def part_bc():
    ok = True
    for label, truth, expect in (("(b) row+K truth at (16, 8)", lambda fe: _truth_rk(fe, 16, 8, COEF), "HOLDS"),
                                 ("(c) G1-form truth (lag 1, no rows)", lambda fe: _truth_g1(fe, COEF), "FAILS")):
        rng = np.random.default_rng(7)
        sets, held = _sets(rng, truth)
        rk = Z.fit_rk(sets)
        g1 = Z.fit_g_form(sets, "G1")
        st = Z.stable_rule(rk, g1)
        e_rk = [y - Z.predict_rk(rk, fe) for _, fe, y in held]
        e_g1 = [y - A9.predict_one(g1["fmts"][fe["fmt"]], fe) for _, fe, y in held]
        bt = Z.boot_beat(e_g1, e_rk)
        print(f"{label}: RK chose (s, r) = ({rk['s']}, {rk['r']}); in-sample "
              f"{ {f: round(v['rms_in'], 2) for f, v in rk['fmts'].items()} }; nested "
              f"{ {f: round(v['rms_nested'], 2) for f, v in rk['nested'].items()} }; G1-form LOKO "
              f"{ {f: round(v['rms_loko'], 2) for f, v in g1['fmts'].items()} }; STABLE {st['verdict']} (pooled nested {st['pooled']['rk_rms_nested']:.2f} vs G1 form {st['pooled']['g1form_rms_loko']:.2f}); held-out "
              f"rms RK {bt['rms_rk']:.2f} vs G1 form {bt['rms_g1']:.2f} W, ratio {bt['ratio']:.3f}, 95% "
              f"[{bt['ci95'][0]:.2f}, {bt['ci95'][1]:.2f}] -> BEAT {bt['verdict']} (expected BEAT and STABLE {expect})")
        ok &= bt["verdict"] == expect and st["verdict"] == expect
        if expect == "HOLDS":
            ok &= (rk["s"], rk["r"]) == (16, 8)
    return ok


def part_d():
    rng = np.random.default_rng(3)
    e_g1 = rng.normal(0, 10, 20)
    good = Z.boot_beat(e_g1, 0.4 * e_g1 + rng.normal(0, 0.5, 20))
    same = Z.boot_beat(e_g1, e_g1 + rng.normal(0, 0.5, 20))
    print(f"(d) bootstrap: errors 0.4x G1's -> {good['verdict']} (ratio {good['ratio']:.2f}, 95% "
          f"[{good['ci95'][0]:.2f}, {good['ci95'][1]:.2f}]); errors equal to G1's -> {same['verdict']} "
          f"(ratio {same['ratio']:.2f})")
    return good["verdict"] == "HOLDS" and same["verdict"] == "FAILS"


if __name__ == "__main__":
    oks = [part_a(), part_bc(), part_d()]
    print("SELFTEST", "PASSES" if all(oks) else "FAILS", oks)
