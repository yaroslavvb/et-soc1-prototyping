#!/usr/bin/env python3
"""E155 scorer (Q139): score E155's reduction with predictions-e155.json's frozen rules. Written before any E155 data.

    python3 tools/claims-v3/e155/score_e155.py --primary e155.json [--relaxed e155-relaxed.json] --pred tools/claims-v3/e155/predictions-e155.json \
        --out scored.json --md results.md

Every statistic is computed per kept pass, paired inside the pass, then its mean and 95% t interval over passes (the pass is the unit of replication):
  N1  = S(m0r1.int8.zeros) - S(m0r1.fp32.zeros)          (E129's and E148's)
  N3  = S(m0r3.int8.zeros) - S(m0r3.fp32.zeros)          (NEW: three A rows)
  D31 = N3 - N1                                          (rule F1 against the frozen readings Wn, Wt, C, T)
  e(f) = [D(m0r3k8.f) - D(m0r3.f)] / [rate(m0r3k8.f) - rate(m0r3.f)], de3 = e(int8) - e(fp32), de3c = de3 - b_mid   (rule F3)
S is over the run's idle bracket and D over the format's zeros (E78's reduction). The set-aside rule (predictions-e155.json > set_aside_rule) picks the
reduction that carries the verdicts. Reported with no verdict: D31 less the shared per-op term measured in this session (E_op from fp32's m0r1 against
m0r3), each count's one-term price fitted on it, the raw de3 and each e, Q31k = S(m0r3k8.int8) - S(m0r1.int8), N3's out-of-sample predictions, every
arm. Standard library only.
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


def per_pass_stats(red, P):
    pp = red["per_pass"]
    keys = sorted(pp, key=int)
    out = {"passes": [int(k) for k in keys]}
    if not keys:
        return out
    N1 = [S(pp[k], "m0r1.int8.zeros") - S(pp[k], "m0r1.fp32.zeros") for k in keys]
    N3 = [S(pp[k], "m0r3.int8.zeros") - S(pp[k], "m0r3.fp32.zeros") for k in keys]
    N3k8 = [S(pp[k], "m0r3k8.int8.zeros") - S(pp[k], "m0r3k8.fp32.zeros") for k in keys]
    D31 = [b - a for a, b in zip(N1, N3)]
    out["N1"], out["N3"], out["N3k8"], out["D31"] = ci(N1), ci(N3), ci(N3k8), ci(D31)
    e = {}
    for f in ("fp32", "int8"):
        e[f] = [(pp[k][f"m0r3k8.{f}.zeros"]["D"] - pp[k][f"m0r3.{f}.zeros"]["D"]) /
                (pp[k][f"m0r3k8.{f}.zeros"]["rate"] - pp[k][f"m0r3.{f}.zeros"]["rate"]) * 1e12 for k in keys]
        out[f"e3_{f}_pJ"] = ci(e[f])
    de3 = [a - b for a, b in zip(e["int8"], e["fp32"])]
    out["de3_raw_pJ"] = ci(de3)
    bm = P["f3_allowance"]["mid_pJ"]
    out["de3c_pJ"] = ci([x - bm for x in de3])
    # reported: the shared per-op term measured in this session (fp32's per-op energy at K = 16 from m0r1 against m0r3)
    eop = [(S(pp[k], "m0r1.fp32.zeros") - S(pp[k], "m0r3.fp32.zeros")) / (pp[k]["m0r1.fp32.zeros"]["rate"] - pp[k]["m0r3.fp32.zeros"]["rate"]) for k in keys]
    dr3 = [pp[k]["m0r3.int8.zeros"]["rate"] - pp[k]["m0r3.fp32.zeros"]["rate"] for k in keys]
    out["E_op_session_pJ"] = ci([x * 1e12 for x in eop])
    out["shared_session_w"] = ci([a * b for a, b in zip(eop, dr3)])
    out["D31_less_session_shared"] = ci([d - a * b for d, a, b in zip(D31, eop, dr3)])
    out["D31_less_frozen_shared"] = ci([d - P["shared_per_op_term"]["point"] for d in D31])
    out["Q31k"] = ci([S(pp[k], "m0r3k8.int8.zeros") - S(pp[k], "m0r1.int8.zeros") for k in keys])
    for f in ("fp32", "int8"):
        out[f"r3_over_r1_{f}"] = ci([S(pp[k], f"m0r3.{f}.zeros") - S(pp[k], f"m0r1.{f}.zeros") for k in keys])
        out[f"r3k8_over_r3_{f}"] = ci([S(pp[k], f"m0r3k8.{f}.zeros") - S(pp[k], f"m0r3.{f}.zeros") for k in keys])
    out["arms"] = {it: {"S": ci([S(pp[k], it) for k in keys]), "D": ci([pp[k][it]["D"] for k in keys]),
                        "rate": ci([pp[k][it]["rate"] for k in keys]), "cpo": [pp[k][it].get("cpo") for k in keys]}
                   for it in sorted(pp[keys[0]]) if it.startswith(("m0", "fp32", "int8", "anchor"))}
    return out


def overlap(a_lo, a_hi, b_lo, b_hi):
    return not (a_hi < b_lo or b_hi < a_lo)


def score(red, P):
    st = per_pass_stats(red, P)
    n = len(st["passes"])
    mins = P["min_kept_passes"]
    rules = {}
    if n < mins:
        for r in ("F1", "F3", "T1"):
            rules[r] = {"verdict": f"NOT-SCORED (fewer than {mins} kept passes: {n})"}
    else:
        d = st["D31"]
        cons = {k: ("CONSISTENT" if overlap(d["lo"], d["hi"], r["lo"], r["hi"]) else "EXCLUDED") for k, r in P["readings"].items()}
        c = sorted(k for k, v in cons.items() if v == "CONSISTENT")
        walk = cons["Wn"] == "CONSISTENT" or cons["Wt"] == "CONSISTENT"
        if walk and cons["C"] == "EXCLUDED":
            f1a = "WALK"
        elif cons["C"] == "CONSISTENT" and not walk:
            f1a = "PER-CYCLE"
        elif not walk and cons["C"] == "EXCLUDED":
            f1a = "NEITHER"
        else:
            f1a = "INCONCLUSIVE (walk and per cycle both consistent)"
        if cons["Wt"] == "CONSISTENT" and cons["Wn"] == "EXCLUDED":
            f1b = "TOGGLES"
        elif cons["Wn"] == "CONSISTENT" and cons["Wt"] == "EXCLUDED":
            f1b = "NEW-ADDRESS"
        elif cons["Wn"] == "EXCLUDED" and cons["Wt"] == "EXCLUDED":
            f1b = "NEITHER"
        else:
            f1b = "INCONCLUSIVE (both counts consistent)"
        rules["F1"] = {"D31": d, "readings": {k: {"band": [P["readings"][k]["lo"], P["readings"][k]["hi"]], "point": P["readings"][k]["point"],
                                                  "verdict": cons[k]} for k in cons},
                       "F1a_walk_against_per_cycle": f1a, "F1b_toggles_against_new_address": f1b, "consistent_set": c,
                       "verdict": f"F1a {f1a}; F1b {f1b}; consistent: {', '.join(c) if c else 'none'}"}
        x = st["de3c_pJ"]
        bh = P["f3_allowance"]["half_pJ"]
        H = math.sqrt(x["half"] ** 2 + bh ** 2)
        lo, hi = x["mean"] - H, x["mean"] + H
        v3 = "BOUNDED" if (lo > -30.0 and hi < 30.0) else ("EXCEEDS" if (lo > 30.0 or hi < -30.0) else "INCONCLUSIVE")
        rules["F3"] = {"de3c_pJ": x, "H_pJ": H, "interval_pJ": [lo, hi], "allowance_mid_pJ": P["f3_allowance"]["mid_pJ"], "allowance_half_pJ": bh,
                       "line_pJ": 30.0, "raw_de3_pJ": st["de3_raw_pJ"], "verdict": v3}
        ref = P["e148_reference"]["N1"]["mean"]
        rules["T1"] = {"N1": {"e155": st["N1"]["mean"], "e148": ref, "verdict": "PASS" if abs(st["N1"]["mean"] - ref) <= 0.5 else "FAIL"},
                       "verdict": "PASS" if abs(st["N1"]["mean"] - ref) <= 0.5 else "FAIL"}
    cpo = red.get("cycles_per_op", {})
    r6 = {}
    for k, want in P["rules"]["R6"]["predicted"].items():
        arm, f = k.split(".")
        have = cpo.get(f"{arm}:{f}")
        r6[k] = {"predicted": want, "measured": have,
                 "verdict": "NOT-MEASURED" if have is None else ("PASS" if abs(have - want) <= 2.0 else "FAIL")}
    rules["R6"] = r6
    rep = {}
    if n >= mins:
        n1m, n3m = st["N1"]["mean"], st["N3"]["mean"]
        e148n1 = P["e148_reference"]["N1"]["mean"]
        rep["N3_out_of_sample"] = {}
        for k, r in list(P["readings"].items()) + [(k, r) for k, r in P["readings_reported"].items()]:
            rep["N3_out_of_sample"][k] = {"predicted_N3_from_frozen": e148n1 + r["point"], "error_w_from_frozen": n3m - (e148n1 + r["point"]),
                                          "predicted_N3_session_N1": n1m + r["point"], "error_w_session_N1": n3m - (n1m + r["point"]),
                                          "D31_error_w": st["D31"]["mean"] - r["point"]}
        Q = P["bench_per_s_card_order"]["m0r3"]
        y = st["D31_less_session_shared"]
        if y.get("mean") is not None:
            rep["one_term_prices_on_D31_less_session_shared"] = {
                "fJ_per_newaddr_read": {k: (v / Q["newaddr"] * 1e15 if isinstance(v, (int, float)) and k in ("mean", "half", "lo", "hi") else v)
                                        for k, v in y.items() if k != "per_pass"},
                "fJ_per_addr_bit_toggle": {k: (v / Q["tog"] * 1e15 if isinstance(v, (int, float)) and k in ("mean", "half", "lo", "hi") else v)
                                           for k, v in y.items() if k != "per_pass"},
                "e148_one_term_fJ": {"newaddr": P["e148_reference"]["N_minus_N1"]["mean"] / P["bench_per_s_card_order"]["m0"]["newaddr"] * 1e15,
                                     "toggle": P["e148_reference"]["N_minus_N1"]["mean"] / P["bench_per_s_card_order"]["m0"]["tog"] * 1e15}}
        qk = P["q31k_reported"]
        rep["Q31k"] = {"measured": st["Q31k"], "walk_Wn": qk["walk_Wn"], "walk_Wt": qk["walk_Wt"], "C_and_T_walk_part": 0.0,
                       "note": qk["what"]}
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
    a = ap.parse_args()
    P = json.load(open(a.pred))
    prim = json.load(open(a.primary))
    rel = json.load(open(a.relaxed)) if a.relaxed else None
    red, which = pick(prim, rel, P)
    out = score(red, P)
    out.update({"experiment": "E155", "which_reduction_scores": which, "primary_kept": len(prim["passes"]),
                "relaxed_kept": None if rel is None else len(rel["passes"]), "set_aside_primary": prim.get("passes_set_aside"),
                "set_aside_relaxed": None if rel is None else rel.get("passes_set_aside"), "leak": red.get("leak")})
    json.dump(out, open(a.out, "w"), indent=1)
    st, R = out["stats"], out["rules"]
    L = [f"# E155 scored ({which}; {out['n_passes']} passes {out['passes']})", ""]
    if out["n_passes"]:
        L += [f"N1 {fmt(st['N1'])} W; N3 {fmt(st['N3'])}; D31 = N3 - N1 {fmt(st['D31'])}; N3k8 {fmt(st['N3k8'])}; Q31k {fmt(st['Q31k'])}",
              f"e3 fp32 {fmt(st['e3_fp32_pJ'], 1)} pJ, int8 {fmt(st['e3_int8_pJ'], 1)} pJ; de3 raw {fmt(st['de3_raw_pJ'], 1)}, corrected {fmt(st['de3c_pJ'], 1)} pJ", ""]
    for k, v in R.items():
        if k == "R6":
            L.append("R6: " + "; ".join(f"{a2} {x['measured']} vs {x['predicted']} {x['verdict']}" for a2, x in v.items()))
        elif k == "F1" and "readings" in v:
            L.append(f"F1: {v['verdict']} (bands: {json.dumps({q: [round(x['band'][0], 3), round(x['band'][1], 3), x['verdict']] for q, x in v['readings'].items()})})")
        elif k == "F3" and "interval_pJ" in v:
            L.append(f"F3: {v['verdict']} (de3c {v['de3c_pJ']['mean']:+.1f} pJ, interval [{v['interval_pJ'][0]:+.1f}, {v['interval_pJ'][1]:+.1f}] against +-30)")
        else:
            L.append(f"{k}: {v.get('verdict')}")
    open(a.md, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
