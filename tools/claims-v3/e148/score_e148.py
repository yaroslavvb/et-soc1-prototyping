#!/usr/bin/env python3
"""E148 scorer (Q138): score E148's reduction with predictions-e148.json's frozen rules. Written before any E148 data.

    python3 tools/claims-v3/e148/score_e148.py --primary e148.json [--relaxed e148-relaxed.json] --pred tools/claims-v3/e148/predictions-e148.json \
        --out scored.json --md results.md [--e129 docs/reports/data/2026-11-02-e129-int8-noissue/e129.json]

Every statistic is computed per kept pass, paired inside the pass, then its mean and 95% t interval over passes (the pass is the unit of replication):
  N  = S(m0.int8.zeros)   - S(m0.fp32.zeros)      (E124's Y1, E129's N)
  N1 = S(m0r1.int8.zeros) - S(m0r1.fp32.zeros)    (E129's V1)
  N2 = S(m0r2.int8.zeros) - S(m0r2.fp32.zeros)    (NEW: two A rows)
  D21 = N2 - N1 (rule W1 against the frozen readings W, T, C; W2 its sign); N - N1 (reported)
S is over the run's idle bracket (E78's reduction). The set-aside rule (predictions-e148.json > set_aside_rule) picks the reduction that carries the
verdicts. Standard library only.
SPDX-License-Identifier: Apache-2.0"""
import argparse
import json
import math

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179}


def ci(v):
    n = len(v)
    if n == 0:
        return {"mean": None, "half": None, "lo": None, "hi": None, "n": 0, "per_pass": []}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "half": None, "lo": None, "hi": None, "n": n, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "sd": sd, "per_pass": v}


def S(e, item):
    return e[item]["S"]


def per_pass_stats(red):
    pp = red["per_pass"]
    keys = sorted(pp, key=int)
    out = {"passes": [int(k) for k in keys]}
    N = [S(pp[k], "m0.int8.zeros") - S(pp[k], "m0.fp32.zeros") for k in keys]
    N1 = [S(pp[k], "m0r1.int8.zeros") - S(pp[k], "m0r1.fp32.zeros") for k in keys]
    N2 = [S(pp[k], "m0r2.int8.zeros") - S(pp[k], "m0r2.fp32.zeros") for k in keys]
    out["N"], out["N1"], out["N2"] = ci(N), ci(N1), ci(N2)
    out["D21"] = ci([b - a for a, b in zip(N1, N2)])
    out["N_minus_N1"] = ci([a - b for a, b in zip(N, N1)])
    out["N1_minus_halfN"] = [a - b / 2 for a, b in zip(N1, N)]
    for f in ("fp32", "int8"):
        out[f"r2_over_r1_{f}"] = ci([S(pp[k], f"m0r2.{f}.zeros") - S(pp[k], f"m0r1.{f}.zeros") for k in keys])
        out[f"r1_over_m0_{f}"] = ci([S(pp[k], f"m0r1.{f}.zeros") - S(pp[k], f"m0.{f}.zeros") for k in keys])
    out["arms"] = {it: {"S": ci([S(pp[k], it) for k in keys]), "D": ci([pp[k][it]["D"] for k in keys]),
                        "rate": ci([pp[k][it]["rate"] for k in keys]), "cpo": [pp[k][it].get("cpo") for k in keys]}
                   for it in sorted(pp[keys[0]]) if it.startswith(("m0", "fp32", "int8", "anchor"))}
    return out


def overlap(a_lo, a_hi, b_lo, b_hi):
    return not (a_hi < b_lo or b_hi < a_lo)


def score(red, P, e129=None):
    st = per_pass_stats(red)
    n = len(st["passes"])
    mins = P["min_kept_passes"]
    rules = {}
    if n < mins:
        for r in ("W1", "W2", "Y1", "V1", "T1"):
            rules[r] = {"verdict": f"NOT-SCORED (fewer than {mins} kept passes: {n})"}
    else:
        d = st["D21"]
        cons = {}
        for k, r in P["readings"].items():
            cons[k] = "CONSISTENT" if overlap(d["lo"], d["hi"], r["lo"], r["hi"]) else "EXCLUDED"
        c = sorted(k for k, v in cons.items() if v == "CONSISTENT")
        lab = {"W": "WALK", "T": "A-PATH", "C": "PER-CYCLE"}
        v = "NONE" if not c else (lab[c[0]] if len(c) == 1 else "INCONCLUSIVE (consistent: " + ", ".join(c) + ")")
        rules["W1"] = {"D21": d, "readings": {k: {"range": [P["readings"][k]["lo"], P["readings"][k]["hi"]], "verdict": cons[k]} for k in cons}, "verdict": v}
        rules["W2"] = {"D21_lo": d["lo"], "verdict": "RISES" if d["lo"] > 0 else "NOT-RISES"}
        N = st["N"]
        rules["Y1"] = {"N": N, "line_w": 0.84, "verdict": "PASS" if N["lo"] >= 0.84 else ("FAIL" if N["hi"] < 0.84 else "INCONCLUSIVE")}
        N1 = st["N1"]
        half = N["mean"] / 2
        rules["V1"] = {"N1": N1, "line_w": half, "verdict": "PER-ROW" if N1["hi"] < half else ("PER-CYCLE" if N1["lo"] >= half else "INCONCLUSIVE")}
        ref = P["e129_reference"]
        rules["T1"] = {"N": {"e148": N["mean"], "e129": ref["N"]["mean"], "verdict": "PASS" if abs(N["mean"] - ref["N"]["mean"]) <= 0.5 else "FAIL"},
                       "N1": {"e148": N1["mean"], "e129": ref["N1"]["mean"], "verdict": "PASS" if abs(N1["mean"] - ref["N1"]["mean"]) <= 0.5 else "FAIL"}}
    # V1p: pooled with E129's three passes (registered with E129's values known)
    pool = []
    if e129 is not None:
        pe = e129["per_pass"]
        pool = [S(pe[k], "m0r1.int8.zeros") - S(pe[k], "m0r1.fp32.zeros") - (S(pe[k], "m0.int8.zeros") - S(pe[k], "m0.fp32.zeros")) / 2 for k in sorted(pe)]
    pool_all = pool + (st["N1_minus_halfN"] if n >= mins else [])
    if e129 is None:
        rules["V1p"] = {"verdict": "NOT-SCORED (no E129 reduction given)"}
    elif len(pool_all) < 6:
        rules["V1p"] = {"n": len(pool_all), "verdict": f"NOT-SCORED (fewer than 6 passes in all: {len(pool_all)})"}
    else:
        c = ci(pool_all)
        rules["V1p"] = {"N1_minus_halfN": c, "n_e129": len(pool), "n_e148": len(pool_all) - len(pool),
                        "verdict": "PER-ROW" if c["hi"] < 0 else ("PER-CYCLE" if c["lo"] >= 0 else "INCONCLUSIVE")}
    # R6: the cycles
    cpo = red.get("cycles_per_op", {})
    r6 = {}
    for k, want in P["rules"]["R6"]["predicted"].items():
        arm, f = k.split(".")
        have = cpo.get(f"{arm}:{f}")
        r6[k] = {"predicted": want, "measured": have,
                 "verdict": "NOT-MEASURED" if have is None else ("PASS" if abs(have - want) <= 2.0 else "FAIL")}
    rules["R6"] = r6
    # reported: the two-term solve per pass (pw fJ a new-address TenC read, pt pJ a 64-bit A read), and N2's out-of-sample predictions
    rep = {}
    a = P["two_term_design"]
    det = a["a11"] * a["a22"] - a["a12"] * a["a21"]
    if n >= 2 and det != 0:
        pw, pt = [], []
        for x, y in zip(st["N_minus_N1"]["per_pass"], st["D21"]["per_pass"]):
            pw.append((x * a["a22"] - a["a12"] * y) / det * 1e15)
            pt.append((a["a11"] * y - a["a21"] * x) / det * 1e12)
        rep["two_term"] = {"pw_fJ_per_newaddr_read": ci(pw), "pt_pJ_per_64bit_A_read": ci(pt)}
    if n >= 1:
        n1m, n2m = st["N1"]["mean"], st["N2"]["mean"]
        rep["N2_out_of_sample"] = {k: {"predicted_N2": n1m + r["point"], "measured_N2": n2m, "error_w": n2m - (n1m + r["point"])}
                                   for k, r in P["readings"].items()}
        rep["N2_out_of_sample"]["bench_card_order"] = {"predicted_N2_range": [P["bench_constants"]["card_order"][kn]["N2"] for kn in ("M4 floats", "M2 int8")],
                                                       "measured_N2": n2m}
    return {"n_passes": n, "passes": st["passes"], "stats": st, "rules": rules, "reported": rep}


def pick(prim, rel, P):
    need = P["min_kept_passes"]
    if len(prim["passes"]) >= need or rel is None:
        return prim, "primary"
    if len(rel["passes"]) > len(prim["passes"]):
        return rel, "relaxed (scored under the set-aside rule)"
    return prim, "primary"


def fmt(c, k=3):
    if c is None or c.get("mean") is None:
        return "-"
    return f"{c['mean']:+.{k}f}" + ("" if c.get("half") is None else f" ± {c['half']:.{k}f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed")
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--e129")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    prim = json.load(open(a.primary))
    rel = json.load(open(a.relaxed)) if a.relaxed else None
    e129 = json.load(open(a.e129)) if a.e129 else None
    red, which = pick(prim, rel, P)
    out = score(red, P, e129)
    out.update({"experiment": "E148", "which_reduction_scores": which, "primary_kept": len(prim["passes"]),
                "relaxed_kept": None if rel is None else len(rel["passes"]), "set_aside_primary": prim.get("passes_set_aside"),
                "set_aside_relaxed": None if rel is None else rel.get("passes_set_aside"), "leak": red.get("leak")})
    json.dump(out, open(a.out, "w"), indent=1)
    st, R = out["stats"], out["rules"]
    L = [f"# E148 scored ({which}; {out['n_passes']} passes {out['passes']})", "",
         f"N {fmt(st['N'])} W; N1 {fmt(st['N1'])}; N2 {fmt(st['N2'])}; D21 = N2 - N1 {fmt(st['D21'])}; N - N1 {fmt(st['N_minus_N1'])}", ""]
    for k, v in R.items():
        if k == "R6":
            L.append("R6: " + "; ".join(f"{a2} {x['measured']} vs {x['predicted']} {x['verdict']}" for a2, x in v.items()))
        else:
            if k == "T1" and "N" in v:
                L.append(f"T1: N {v['N']['verdict']}, N1 {v['N1']['verdict']}")
                continue
            L.append(f"{k}: {v.get('verdict')}" + (f" (readings: {json.dumps({q: x['verdict'] for q, x in v['readings'].items()})})" if k == "W1" and "readings" in v else ""))
    if "two_term" in out["reported"]:
        tt = out["reported"]["two_term"]
        L.append(f"reported, two-term solve: pw {fmt(tt['pw_fJ_per_newaddr_read'], 1)} fJ a new-address TenC read; pt {fmt(tt['pt_pJ_per_64bit_A_read'], 2)} pJ a 64-bit A read")
    open(a.md, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
