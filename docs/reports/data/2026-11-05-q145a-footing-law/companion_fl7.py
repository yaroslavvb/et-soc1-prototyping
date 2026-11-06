#!/usr/bin/env python3
"""heat-q145a FL7 (post hoc): the first-order one-footing companion of the footing law's arm, from the registered scorer's own output.

The law arm (the registered scorer on a reduction at the law's k) measures D on the law while M10 and M9 stay fitted on Q139(u)'s footing.
To first order a footing change of dk is a gain f = 1 - c1 dk on every row's D (FOOTING-LAW.md, Why 5), so a model refitted on rows
re-reduced at the law predicts f x its old values; the session scale re-read on its anchors then cancels f on the floats. So: M10's float
primary stays as the arm wrote it; M10's int8 (no session scale), M10's a-priori arm (s = 1) and M9 are multiplied by f. The rules are
recomputed with the scorer's own statistics (its paired bootstrap with the same seed and draws, KA's sums and band), on the same tiles.
At f = 1 this reproduces the arm's figures exactly (checked and printed).

    python3 -B companion_fl7.py <scored law json> <f> <name>
"""
import json
import math
import random
import sys


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def paired(ea, eb, sel, draws, seed):
    d0 = rms([ea[t] for t in sel]) - rms([eb[t] for t in sel])
    rng = random.Random(seed)
    ds = []
    for _ in range(draws):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(rms([ea[t] for t in s]) - rms([eb[t] for t in s]))
    ds.sort()
    lo, hi = ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds)) - 1]
    return {"verdict": "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED"), "d_rms": d0, "lo95": lo, "hi95": hi, "n": len(sel)}


def companion(o, f):
    pr = o["primary"]
    rows = pr["rows"]
    ep, e9, e0, inside = {}, {}, {}, {}
    for t, r in rows.items():
        if "D_w" not in r:
            continue
        D = r["D_w"]
        isf = r.get("type") in ("fp32", "fp16")
        m10 = r["M10_primary_w"] if isf else f * r["M10_primary_w"]
        ep[t] = D - m10
        e0[t] = D - f * r["M10_a_priori_w"]
        e9[t] = D - f * r["M9_w"]
        lo, hi = r["M10_primary_95"]
        if not isf:
            lo, hi = f * lo, f * hi
        inside[t] = lo <= D <= hi
    R = pr["rules"]
    out = {}
    for rule, a, b in (("P8-M1", ep, e9), ("P8-M1f", ep, e9), ("P8-M1i", ep, e9), ("P8-A1", ep, e0)):
        v = R[rule]
        sel = sorted(v["tiles"])
        out[rule] = paired(a, b, sel, v["draws"], v["seed"])
    ka = R["P8-KA"]
    kt = sorted(ka["tiles"])
    s_p = sum(ep[t] ** 2 for t in kt)
    s_0 = sum(e0[t] ** 2 for t in kt)
    out["P8-KA"] = {"verdict": "PASS" if (s_p < s_0 and all(inside[t] for t in kt)) else "FAIL", "sum_e_primary_sq": s_p,
                    "sum_e_a_priori_sq": s_0, "all_inside": all(inside[t] for t in kt), "n": len(kt)}
    b2 = R["P8-B2"]
    m = sum(ep[t] for t in b2["tiles"]) / len(b2["tiles"])
    lo, hi = b2["line"]
    out["P8-B2"] = {"verdict": "PASS" if lo <= m <= hi else ("FAIL HIGH" if m < lo else "FAIL LOW"), "mean": m, "line": [lo, hi]}
    b1 = R["P8-B1"]
    m = sum(ep[t] for t in b1["tiles"]) / len(b1["tiles"])
    lo, hi = b1["line"]
    out["P8-B1"] = {"verdict": "PASS" if lo <= m <= hi else ("FAIL HIGH" if m < lo else "FAIL LOW"), "mean": m, "line": [lo, hi]}
    # KA's rows for pooling
    out["_ka_rows"] = [{"tile": t, "e_primary": ep[t], "e_a_priori": e0[t], "inside_power": inside[t]} for t in kt]
    return out


def main():
    path, f, name = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    o = json.load(open(path))
    chk = companion(o, 1.0)
    worst = 0.0
    for r in ("P8-M1", "P8-M1f", "P8-M1i", "P8-A1"):
        for k in ("d_rms", "lo95", "hi95"):
            worst = max(worst, abs(chk[r][k] - o["primary"]["rules"][r][k]))
    ka0 = o["primary"]["rules"]["P8-KA"]
    worst = max(worst, abs(chk["P8-KA"]["sum_e_primary_sq"] - ka0["sum_e_primary_sq"]), abs(chk["P8-KA"]["sum_e_a_priori_sq"] - ka0["sum_e_a_priori_sq"]))
    worst = max(worst, abs(chk["P8-B2"]["mean"] - o["primary"]["rules"]["P8-B2"]["mean"]))
    c = companion(o, f)
    print(json.dumps({"name": name, "f": f, "reproduces_arm_at_f1_worst": worst,
                      "rules": {k: v for k, v in c.items() if not k.startswith("_")}, "ka_rows": c["_ka_rows"]}))


if __name__ == "__main__":
    main()
