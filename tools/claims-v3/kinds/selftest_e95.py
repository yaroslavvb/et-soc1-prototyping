#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E95 self-test: E95's reduction and scorer on SYNTHETIC data with known answers, before any card data exist.

    /usr/bin/python3 tools/claims-v3/kinds/selftest_e95.py <scratch dir> [--passes 4] [--seed 1]

Part 1: it writes fake passes with E78's own generator (selftest_e78.make_pass: the layout run_e78.py writes, 10 Hz telemetry,
heaters, the quiet rule, integer die readings, a lagging rail, a drifting idle) after installing E95's items and order, so
every pass is E95's registered 53-run order, and runs reduce_e95.py (E78's reduction, unchanged) and score_e95.py on two worlds:
  (a) "frozen": every real2 tile at its frozen (a) point, E86's three at their frozen points, every E78 kind at E78's D;
  (b) "law":    gated tiles at the gate law (c), -0.0 gated, no-zero float tiles at 1.01 x random, the calibrations and the forward
      pass moved so that the claims with a FAIL branch fail.
Part 2: every claim's PASS, FAIL, INCONCLUSIVE and UNDER-RESOLVED branch on small tables of per-pass values, through the
scorer's own functions and thresholds. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e95_common as e95  # noqa: E402

e95.install()
import e78_common as ec  # noqa: E402
import score_e95 as sc  # noqa: E402
import selftest_e78 as st  # noqa: E402

F = json.load(open(e95.FROZEN_JSON))
REG = json.load(open(os.path.join(HERE, "predictions-e95.json")))
CL = F["claims"]["E95"]
KEY = {short: key for short, key, _ in sc.CLAIMS}
FN = {short: fn for short, _, fn in sc.CLAIMS}


def base_truth():
    e78 = json.load(open(os.path.join(ROOT, REG["inputs_frozen"]["e78_reduction"]["path"])))
    return {n: v["D"]["mean"] for n, v in e78["items"].items()}


def frozen_world():
    D = base_truth()
    for k, t in F["tiles"].items():
        D[e95.item_of(k)] = t["a_aifoundry3_600mhz"]["D_w"]
    D.update(REG["items"]["e86_partner_frozen_points_w"])
    return D


def law_world():
    D = frozen_world()
    ref = {t: D[sc.REF[t]] for t in sc.TYPES}
    for k, t in F["tiles"].items():
        ty = k.split("/")[0]
        if "c_gate_law" in t:
            D[e95.item_of(k)] = t["c_gate_law"]["D_w"]
        elif ty in ("fp32", "fp16"):
            D[e95.item_of(k)] = 1.01 * ref[ty]
    D[e95.item_of("fp32/vit_l11_down")] = CL["C9_negative_zero"]["prediction_if_gate_took_numeric_zero"]["D_w"]
    D["fp16.real_l6_mlp_down"] = 21.0
    D[e95.item_of("fp16/gpt2_l6_mlp_down_fp16fwd")] = 22.0                 # +1 W: C11 FAIL
    D["int8.real_l6_mlp_down"] = 5.5
    D[e95.item_of("int8/gpt2_l6_down_per_token")] = 4.5                    # -1 W: C7 FAIL
    D[e95.item_of("int8/gpt2_l6_down_p999")] = 5.5
    D[e95.item_of("int8/gpt2_l6_down_p9999")] = 5.5
    D[e95.item_of("int8/gpt2_l11_down_maxabs")] = 2.82
    D[e95.item_of("int8/gpt2_l11_down_p999")] = 3.32                       # +0.5 W: C6 FAIL
    D[e95.item_of("int8/vgg16_fc2")] = 4.82
    D[e95.item_of("int8/vgg16_fc2_asym")] = 3.82                           # -1 W: C8 FAIL
    return D


def run_world(scratch, world, D, passes, seed):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(passes):
        p = e95.FIRST_PASS + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        dirs.append(d)
    j = os.path.join(scratch, f"{world}-e95.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e95.py"), *dirs, "--out", j, "--no-refit",
                        "--txt", os.path.join(scratch, f"{world}-reduce.txt")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit(f"reduce_e95.py failed ({world})")
    s = os.path.join(scratch, f"{world}-scored.json")
    r2 = subprocess.run([sys.executable, os.path.join(HERE, "score_e95.py"), "--e95", j, "--json", s,
                         "--md", os.path.join(scratch, f"{world}-results.md")], capture_output=True, text=True)
    if r2.returncode:
        print(r2.stdout[-2000:], r2.stderr[-3000:])
        sys.exit(f"score_e95.py failed ({world})")
    return json.load(open(j)), json.load(open(s))


# ---- part 2: small tables

PASSES = [1, 2, 3, 4]
REFS = {"fp32.randn": 24.7, "fp16.randn": 22.0, "int8.full": 7.0}
NOISE = [-1.0, 1.0, -1.0, 1.0]        # a pattern with mean 0: value +- s, standard error s / 2, 95% half-width 1.591 s


def res_of(values, passes=PASSES):
    """A reduction's shape from {item: scalar or per-pass list}; refs fixed at REFS."""
    pp = {}
    for i, p in enumerate(passes):
        e = {k: {"D": v, "S": v, "p80": v} for k, v in REFS.items()}
        for k, v in values.items():
            x = v[i] if isinstance(v, (list, tuple)) else v
            if x is not None:
                e[k] = {"D": x, "S": x, "p80": x}
        pp[str(p)] = e
    return {"passes": passes, "per_pass": pp, "items": {}}


def noisy(mean, s):
    return [mean + s * n for n in NOISE]


def verdict(short, values, passes=PASSES):
    return FN[short](sc.View(res_of(values, passes)), CL[KEY[short]], F)["verdict"]


def tests():
    C1 = CL[KEY["C1"]]
    cells = C1["cells"]
    all_tiles = [(k, t) for tt in cells.values() for t in tt for k in [t.split("/")[0]]]

    def c1vals(rf):
        return {e95.item_of(t): noisy(REFS[sc.REF[ty]] * rf, 0.001 * REFS[sc.REF[ty]]) for ty, t in all_tiles}
    T = []
    T.append(("C1 r 1.000 +- small: PASS", verdict("C1", c1vals(1.0)), sc.PASS))
    T.append(("C1 r 0.95: FAIL", verdict("C1", c1vals(0.95)), sc.FAIL))
    T.append(("C1 r 0.98 straddles the band's end: INCONCLUSIVE", verdict("C1", c1vals(0.98)), sc.INC))
    v = c1vals(1.0)
    del v[e95.item_of("fp32/bert_l6_up")]
    T.append(("C1 one tile missing: UNDER-RESOLVED", verdict("C1", v), sc.UNDER))
    v = c1vals(1.0)
    del v[e95.item_of("fp32/bert_l6_up")]
    v[e95.item_of("fp16/bert_l6_up")] = noisy(0.9 * 22.0, 0.01)
    T.append(("C1 one tile missing and a cell fails: FAIL stands", verdict("C1", v), sc.FAIL))
    C2 = CL[KEY["C2"]]

    def c2vals(rf):
        return {e95.item_of(t): noisy(REFS[sc.REF[ty]] * rf, 0.001 * REFS[sc.REF[ty]]) for ty, tt in C2["tiles"].items() for t in tt}
    T += [("C2 r 0.99: PASS", verdict("C2", c2vals(0.99)), sc.PASS), ("C2 r 1.01: FAIL", verdict("C2", c2vals(1.01)), sc.FAIL),
          ("C2 r 1.00: INCONCLUSIVE", verdict("C2", c2vals(1.0)), sc.INC)]
    C3 = CL[KEY["C3a"]]

    def c3vals(off=None):
        off = off or {}
        return {e95.item_of(t): noisy(F["tiles"][t]["c_gate_law"]["D_w"] + off.get(t, 0.0), 0.01) for ty, tt in C3["tiles"].items() for t in tt}
    T.append(("C3a all at the law: PASS", verdict("C3a", c3vals()), sc.PASS))
    T.append(("C3a one 10 W off: INCONCLUSIVE", verdict("C3a", c3vals({"fp32/vgg16_fc2": 10.0})), sc.INC))
    T.append(("C3a two 10 W off: FAIL", verdict("C3a", c3vals({"fp32/vgg16_fc2": 10.0, "fp16/vgg16_fc2": 10.0})), sc.FAIL))
    v = c3vals()
    del v[e95.item_of("fp16/vgg16_fc2")]
    T.append(("C3a one missing, none outside: UNDER-RESOLVED", verdict("C3a", v), sc.UNDER))
    v = c3vals({"fp32/vgg16_fc2": 10.0, "fp32/resnet18_l3c1": 10.0})
    del v[e95.item_of("fp16/vgg16_fc2")]
    T.append(("C3a one missing, two outside: FAIL stands", verdict("C3a", v), sc.FAIL))
    T.append(("C3b tiles on the law: PASS (slope/L = (L - G)/L)", verdict("C3b", c3vals()), sc.PASS))

    def c3flat():
        return {e95.item_of(t): noisy(5.0 + 2.0 * (1 - F["tiles"][t]["gated_lane_frac"]), 0.01) for tt in C3["tiles"].values() for t in tt}
    T.append(("C3b a flat line: FAIL", verdict("C3b", c3flat()), sc.FAIL))
    v = c3vals()
    del v[e95.item_of("fp16/vgg16_fc2")]
    T.append(("C3b one missing: UNDER-RESOLVED", verdict("C3b", v), sc.UNDER))
    C4 = CL[KEY["C4"]]

    def c4vals(d, s=0.001):
        out = {}
        for _, (hi, lo) in C4["pairs"].items():
            out[e95.item_of(lo)] = [0.3 * 24.7] * 4
            out[e95.item_of(hi)] = [(0.3 + d + s * n) * 22.0 for n in NOISE]
        return out
    T += [("C4 +0.05: PASS", verdict("C4", c4vals(0.05)), sc.PASS), ("C4 -0.05: FAIL", verdict("C4", c4vals(-0.05)), sc.FAIL),
          ("C4 0: INCONCLUSIVE", verdict("C4", c4vals(0.0)), sc.INC)]
    C5 = CL[KEY["C5"]]
    ks = C5["tiles"]
    a0, c0 = C5["predicted"][ks[0]]["a_w"], C5["predicted"][ks[0]]["c_w"]
    a1, c1_ = C5["predicted"][ks[1]]["a_w"], C5["predicted"][ks[1]]["c_w"]
    i0, i1 = e95.item_of(ks[0]), e95.item_of(ks[1])
    T += [("C5 both at (a): PASS", verdict("C5", {i0: noisy(a0, .01), i1: noisy(a1, .01)}), sc.PASS),
          ("C5 both at (c): FAIL", verdict("C5", {i0: noisy(c0, .01), i1: noisy(c1_, .01)}), sc.FAIL),
          ("C5 one each: INCONCLUSIVE", verdict("C5", {i0: noisy(a0, .01), i1: noisy(c1_, .01)}), sc.INC),
          ("C5 one missing: UNDER-RESOLVED", verdict("C5", {i0: noisy(a0, .01)}), sc.UNDER)]

    def pair_vals(short, d, s=0.05, base=1.0):
        a, b = CL[KEY[short]]["pair"]
        return {e95.item_of(a): noisy(base + d, s), e95.item_of(b): [base] * 4}
    T += [("C6 +3 W: PASS", verdict("C6", pair_vals("C6", 3.0)), sc.PASS), ("C6 +1 W: FAIL", verdict("C6", pair_vals("C6", 1.0)), sc.FAIL),
          ("C6 +2 W: INCONCLUSIVE", verdict("C6", pair_vals("C6", 2.0)), sc.INC),
          ("C8 +1 W: PASS", verdict("C8", pair_vals("C8", 1.0)), sc.PASS), ("C8 -1 W: FAIL", verdict("C8", pair_vals("C8", -1.0)), sc.FAIL),
          ("C8 +0.25 W: INCONCLUSIVE", verdict("C8", pair_vals("C8", 0.25)), sc.INC),
          ("C11 0 W: PASS", verdict("C11", pair_vals("C11", 0.0)), sc.PASS), ("C11 +1 W: FAIL", verdict("C11", pair_vals("C11", 1.0)), sc.FAIL),
          ("C11 +0.5 W: INCONCLUSIVE", verdict("C11", pair_vals("C11", 0.5)), sc.INC)]
    C7 = CL[KEY["C7"]]

    def c7vals(tok, p999, p9999, s=0.02):
        r = C7["reference"]
        return {r: [5.0] * 4, e95.item_of("int8/gpt2_l6_down_per_token"): noisy(5.0 + tok, s), e95.item_of("int8/gpt2_l6_down_p999"): noisy(5.0 + p999, s),
                e95.item_of("int8/gpt2_l6_down_p9999"): noisy(5.0 + p9999, s)}
    T += [("C7 +0.2, +0.3, 0: PASS", verdict("C7", c7vals(.2, .3, 0)), sc.PASS), ("C7 per-token -0.2: FAIL", verdict("C7", c7vals(-.2, .3, 0)), sc.FAIL),
          ("C7 p999 -0.2: FAIL", verdict("C7", c7vals(.2, -.2, 0)), sc.FAIL), ("C7 p9999 +1: FAIL", verdict("C7", c7vals(.2, .3, 1.0)), sc.FAIL),
          ("C7 p9999 +0.40: INCONCLUSIVE", verdict("C7", c7vals(.2, .3, .40)), sc.INC), ("C7 per-token 0: INCONCLUSIVE", verdict("C7", c7vals(0, .3, 0)), sc.INC)]
    i9 = e95.item_of(CL[KEY["C9"]]["tile"])
    end = CL[KEY["C9"]]["prediction_if_gate_took_numeric_zero"]["scoring_interval_w"][1]
    T += [("C9 20 W: PASS", verdict("C9", {i9: noisy(20.0, .1)}), sc.PASS), ("C9 9 W: FAIL", verdict("C9", {i9: noisy(9.0, .1)}), sc.FAIL),
          ("C9 at the threshold: INCONCLUSIVE", verdict("C9", {i9: noisy(end, .1)}), sc.INC),
          ("C9 missing: UNDER-RESOLVED", verdict("C9", {}), sc.UNDER)]
    i10 = e95.item_of(CL[KEY["C10"]]["tile"])
    T += [("C10 r 0.91: PASS", verdict("C10", {i10: noisy(.91 * 24.7, .02)}), sc.PASS), ("C10 r 1: FAIL", verdict("C10", {i10: noisy(24.7, .02)}), sc.FAIL),
          ("C10 r 0.97: INCONCLUSIVE", verdict("C10", {i10: noisy(.97 * 24.7, .02)}), sc.INC)]
    tier1 = [k for k, t in F["tiles"].items() if t["tier"] == 1]

    def c12vals(n_inside, drop=0):
        out = {}
        for i, k in enumerate(tier1):
            if i < drop:
                continue
            a = F["tiles"][k]["a_aifoundry3_600mhz"]
            x = a["D_w"] if i - drop < n_inside else a["scoring_interval_w"][1] + 5.0
            out[e95.item_of(k)] = noisy(x, 0.01)
        return out
    T += [("C12 25 of 25: PASS", verdict("C12", c12vals(25)), sc.PASS), ("C12 20 of 25: PASS", verdict("C12", c12vals(20)), sc.PASS),
          ("C12 19 of 25: INCONCLUSIVE", verdict("C12", c12vals(19)), sc.INC), ("C12 18 of 25: INCONCLUSIVE", verdict("C12", c12vals(18)), sc.INC),
          ("C12 17 of 25: FAIL", verdict("C12", c12vals(17)), sc.FAIL), ("C12 one missing, 24 inside: UNDER-RESOLVED", verdict("C12", c12vals(24, drop=1)), sc.UNDER),
          ("C12 five missing, 12 inside: FAIL stands (12 + 5 < 18)", verdict("C12", c12vals(12, drop=5)), sc.FAIL)]
    # two passes: every frozen claim NOT SCORED
    s2 = sc.score({"passes": [1, 2], "per_pass": res_of({}, [1, 2])["per_pass"], "items": {}}, F, REG)
    T.append(("fewer than 3 kept passes: every claim NOT SCORED", {v["verdict"] for v in s2["claims"].values()} == {sc.NOTSC}, True))
    return T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    ok_all = True

    def check(name, good, val):
        nonlocal ok_all
        ok_all &= bool(good)
        print(f"{'ok  ' if good else 'FAIL'} {name}: {val}")

    # part 2 first: it is cheap
    for name, have, want in tests():
        check(name, have == want, have)
    # part 1
    D = frozen_world()
    e, s = run_world(a.scratch, "frozen", D, a.passes, a.seed)
    names = list(e95.POOL) + list(ec.ANCHORS) + [ec.TIE]
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    check("frozen: passes kept", len(e["passes"]) == a.passes, len(e["passes"]))
    check("frozen: runs kept, all", e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}")
    check("frozen: 53 runs a pass", e["runs"] == 53 * a.passes, e["runs"])
    check("frozen: D recovered within 0.15 W (every tile and anchor)", worst <= 0.15, round(worst, 4))
    check("frozen: every dumped tile passes the sha256 gate", not any("tile dump" in " ".join(f[3]) for f in e["failed"]), len(e["failed"]))
    check("frozen: experiment is E95", e.get("experiment") == "E95", e.get("experiment"))
    C = s["claims"]
    want = {"C1": sc.FAIL, "C2": sc.PASS, "C3b": sc.PASS, "C4": sc.PASS, "C5": sc.PASS, "C6": sc.PASS, "C8": sc.PASS,
            "C9": sc.PASS, "C10": sc.PASS, "C11": sc.PASS, "C12": sc.PASS}
    for k, w in want.items():
        check(f"frozen: {k} {w}", C[k]["verdict"] == w, C[k]["verdict"])
    # (a) lies outside the law's interval for fp16 VGG, and within 0.06 W of its end for fp16 ResNet and T5, so the noise decides
    out3 = sorted(k for k, v in C["C3a"]["tiles"].items() if not v["inside"])
    truth3 = sum(1 for k, v in C["C3a"]["tiles"].items() if not v["interval_w"][0] <= D[e95.item_of(k)] <= v["interval_w"][1])
    check("frozen: C3a's outside count agrees with the truth's within the two tiles near an end",
          abs(len(out3) - truth3) <= 2 and C["C3a"]["verdict"] == (sc.FAIL if len(out3) >= 2 else sc.INC), (C["C3a"]["verdict"], out3))
    check("frozen: C7 PASS or INCONCLUSIVE (steps at the noise)", C["C7"]["verdict"] in (sc.PASS, sc.INC), C["C7"]["verdict"])
    check("frozen: C9 lands on the blind reading", C["C9"]["lands_on"] == "gate blind to -0.0", C["C9"]["lands_on"])
    check("frozen: C12 25 of 25", C["C12"]["inside"] == 25, C["C12"]["inside"])
    D2 = law_world()
    e2, s2 = run_world(a.scratch, "law", D2, a.passes, a.seed + 1)
    C = s2["claims"]
    worst = max(abs(e2["items"][n]["D"]["mean"] - D2[n]) for n in names)
    check("law: D recovered within 0.15 W", worst <= 0.15, round(worst, 4))
    want = {"C1": sc.PASS, "C2": sc.FAIL, "C3a": sc.PASS, "C3b": sc.PASS, "C4": sc.PASS, "C5": sc.FAIL, "C6": sc.FAIL, "C7": sc.FAIL, "C8": sc.FAIL,
            "C9": sc.FAIL, "C10": sc.FAIL, "C11": sc.FAIL}
    for k, w in want.items():
        check(f"law: {k} {w}", C[k]["verdict"] == w, C[k]["verdict"])
    check("law: C9 lands on the gated reading", C["C9"]["lands_on"] == "gate took -0.0", C["C9"]["lands_on"])
    n_in = sum(1 for k, t in F["tiles"].items() if t["tier"] == 1
               and t["a_aifoundry3_600mhz"]["scoring_interval_w"][0] <= D2[e95.item_of(k)] <= t["a_aifoundry3_600mhz"]["scoring_interval_w"][1])
    check("law: C12's count agrees with the truth's within 1", abs(C["C12"]["inside"] - n_in) <= 1, f"{C['C12']['inside']} against {n_in}")
    print("tallies on synthetic data (meaningless as a result):", s["tally"], s2["tally"])
    print("SELFTEST", "PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
