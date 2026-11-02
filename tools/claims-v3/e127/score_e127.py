#!/usr/bin/env python3
"""E127's rules, on a reduction written by reduce_e127.py. Standard library only.

    python3 tools/claims-v3/e127/score_e127.py --e127 <e127.json> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and every prediction comes from predictions-e127.json (frozen before E127's claim): M5's and M4's frozen
predictions for each tile (the three E115 tiles copied from Q133(b)'s predictions-blind3.json, the ten new ones computed by
make_predictions_e127.py with predict_blind3.py's own functions on the bench's counts), each contrast's frozen point and 95%
interval (the two tiles' half-widths in quadrature, Q133(b)'s contrasts_blind3.py rule) and E115's measured values. Fewer
than plan.min_kept_passes_scored kept passes: every rule NOT SCORED. A tile with fewer than plan.min_tile_passes is left out.

A contrast C = D(plus) - D(minus), paired inside each kept pass, mean over passes, 95% interval t(n-1) x sd / sqrt(n).
Its excess e(C) = C - M5(C), M5's frozen point: the part of the contrast the model does not price (same interval as C).

  E127-R1  the replicate: B1 = g_blanes_alt - g_blanes_steady (fp32, E115's registered contrast, +2.00 W against M5's
           +0.78 [+0.23, +1.34]). PASS if B1's interval lies above M5's upper bound; FAIL if B1's mean is at or below it;
           else INCONCLUSIVE.
  E127-R2  the primary: does the miss stay with the data held still? (fp32) Q1 = q_alt - q_steady at quiet data, its
           excess e(Q1) against L = half of e(B1) in this session. GATE if e(Q1)'s low end >= L; DATA if its high end
           <= L; OPPOSITE if its high end < -L; else INCONCLUSIVE. NOT SCORED unless R1 PASS.
  E127-R3  the same in fp16: F2 = q_alt - q_steady (fp16) against half of e(F1), F1 = g_blanes_alt - g_blanes_steady
           (fp16). NOT SCORED unless e(F1)'s low end > 0.
  E127-R4  per-lane flipping or all lanes off together? (fp32, random data) B3 = g_blanes_chk - g_blanes_steady against
           half of e(B1): PER-LANE if e(B3)'s low end >= it; ALL-OFF if its high end <= it; else INCONCLUSIVE. NOT SCORED
           unless R1 PASS. R4q, the same at quiet data, Q2 = q_chk - q_steady against half of e(Q1): scored only if R2 GATE.
  E127-R5  the time scale (fp32, quiet): Q4 = q_blk - q_steady against half of e(Q1): SHORT (a lane off for 32 cycles
           at a time already prices like a steady one) if e(Q4)'s high end <= it; LONG if its low end >= it; else
           INCONCLUSIVE. Scored only if R2 GATE.
  E127-R6  lane position (fp32, quiet): Q5 = q_steady_hi - q_steady: PASS if |Q5| + its half-width <= 0.30 W; FAIL if
           |Q5| - its half-width > 0.30 W; else INCONCLUSIVE.
  E127-S1  the session tie against E115 on this card (its dips-removed reading): fp32.randn, fp16.randn, anchor_pi
           (+-0.50 W), int8.full (+-0.25 W). A failure means the session moved, never a verdict on the model.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e127.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def t975(df):
    if df in T975:
        return T975[df]
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def mean_ci(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"mean": None, "n": 0, "ci95": None}
    m = sum(v) / len(v)
    if len(v) < 2:
        return {"mean": m, "n": 1, "ci95": None}
    return {"mean": m, "n": len(v), "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v)), "sd": statistics.stdev(v)}


def ratio_delta(num, den):
    """num/den with a delta-method 95% interval from the two per-pass series (paired: the covariance is used)."""
    n = min(len(num), len(den))
    if n < 2:
        return None
    a, b = num[:n], den[:n]
    ma, mb = sum(a) / n, sum(b) / n
    if mb == 0:
        return None
    va, vb = statistics.variance(a) / n, statistics.variance(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (n - 1) / n
    r = ma / mb
    var = (va - 2 * r * cov + r * r * vb) / (mb * mb)
    h = t975(n - 1) * math.sqrt(max(var, 0.0))
    return {"ratio": r, "lo95": r - h, "hi95": r + h, "n": n}


def score(res, reg, footing="a3"):
    plan, tiles, cons_reg = reg["plan"], reg["tiles"], reg["contrasts"]
    passes = res.get("passes", [])
    out = {"footing": footing, "passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer_arm": (res.get("reducer") or {}).get("arm"), "rules": {}, "table": {}, "contrasts": {}}
    rule_ids = list(reg["rules"])
    if len(passes) < plan["min_kept_passes_scored"]:
        for r in rule_ids:
            out["rules"][r] = {"verdict": "NOT SCORED", "why": f"{len(passes)} kept passes, fewer than {plan['min_kept_passes_scored']}"}
        out["tally"] = {"NOT SCORED": len(rule_ids)}
        return out
    items, per = res["items"], res.get("per_pass", {})
    anchor_meas = {a: ((items.get(a) or {}).get("D") or {}).get("mean") for a in reg["anchors_predicted_a3_w"]}
    scale = {}
    for a, pr in reg["anchors_predicted_a3_w"].items():
        for w in ("M5", "M4"):
            scale[(a, w)] = (anchor_meas[a] / pr[w]) if (footing == "anchor" and anchor_meas[a]) else 1.0
    left_out = []
    for k, t in tiles.items():
        d = (items.get(k) or {}).get("D")
        if not d or d.get("mean") is None or (d.get("n") or 0) < plan["min_tile_passes"]:
            left_out.append(k)
            continue
        s5, s4 = scale[(t["anchor"], "M5")], scale[(t["anchor"], "M4")]
        m5, h5 = t["M5"]["D_w"] * s5, t["M5"]["half95"]
        m4, h4 = t["M4"]["D_w"] * s4, t["M4"]["half95"]
        out["table"][k] = {"type": t["type"], "family": t["family"], "D": d["mean"], "ci95": d.get("ci95"), "n": d.get("n"),
                           "M5": m5, "lo95": m5 - h5, "hi95": m5 + h5, "err_M5": d["mean"] - m5,
                           "inside_M5": m5 - h5 <= d["mean"] <= m5 + h5, "M4": m4, "err_M4": d["mean"] - m4,
                           "inside_M4": m4 - h4 <= d["mean"] <= m4 + h4}
    out["left_out"] = left_out
    C = out["contrasts"]
    for name, c in cons_reg.items():
        plus, minus = c["plus"], c["minus"]
        if plus in left_out or minus in left_out:
            C[name] = {"verdict": "LEFT OUT"}
            continue
        vals = []
        for p in passes:
            a_, b_ = (per.get(str(p)) or {}).get(plus), (per.get(str(p)) or {}).get(minus)
            if a_ and b_ and a_.get("D") is not None and b_.get("D") is not None:
                vals.append(a_["D"] - b_["D"])
        m = mean_ci(vals)
        if m["n"] < plan["min_tile_passes"]:
            C[name] = {"verdict": "LEFT OUT", "n": m["n"]}
            continue
        s5 = scale[(c["anchor"], "M5")]
        s4 = scale[(c["anchor"], "M4")]
        P, h = c["M5"]["D_w"] * s5, c["M5"]["half95"]
        where = "INSIDE" if P - h <= m["mean"] <= P + h else ("BELOW" if m["mean"] < P - h else "ABOVE")
        C[name] = {"plus": plus, "minus": minus, "measured_w": m["mean"], "ci95_w": m["ci95"], "n_passes": m["n"],
                   "per_pass_w": vals, "M5_w": P, "lo95": P - h, "hi95": P + h, "M4_w": c["M4"]["D_w"] * s4,
                   "excess_w": m["mean"] - P, "excess_lo95": m["mean"] - P - m["ci95"], "excess_hi95": m["mean"] - P + m["ci95"],
                   "excess_per_pass_w": [v - P for v in vals], "verdict": where, "isolates": c.get("isolates")}
    R = out["rules"]

    def ok(name):
        return name in C and C[name].get("verdict") in ("INSIDE", "BELOW", "ABOVE")

    # R1, the replicate
    b1 = reg["rules"]["E127-R1"]["contrast"]
    if ok(b1):
        c = C[b1]
        lo = c["measured_w"] - c["ci95_w"]
        v = "PASS" if lo > c["hi95"] else ("FAIL" if c["measured_w"] <= c["hi95"] else "INCONCLUSIVE")
        R["E127-R1"] = {"verdict": v, "measured_w": c["measured_w"], "ci95_w": c["ci95_w"], "M5_hi95": c["hi95"],
                        "E115_w": reg["rules"]["E127-R1"]["E115_measured_w"],
                        "minus_E115_w": c["measured_w"] - reg["rules"]["E127-R1"]["E115_measured_w"], "excess_w": c["excess_w"]}
    else:
        R["E127-R1"] = {"verdict": "UNRESOLVED", "why": f"{b1} left out"}

    def against(test, ref, rid, labels, needs, frac=0.5):
        """A test contrast's excess against frac x the reference contrast's excess (this session): labels = (at or above,
        at or below, opposite)."""
        if not needs[0]:
            return {"verdict": "NOT SCORED", "why": needs[1], **({"reported": C[test]} if ok(test) else {})}
        if not ok(test) or not ok(ref):
            return {"verdict": "UNRESOLVED", "why": f"{test} or {ref} left out"}
        t, r = C[test], C[ref]
        L = frac * r["excess_w"]
        lo, hi = t["excess_lo95"], t["excess_hi95"]
        if lo >= L:
            v = labels[0]
        elif labels[2] and hi < -L:
            v = labels[2]
        elif hi <= L:
            v = labels[1]
        else:
            v = "INCONCLUSIVE"
        rr = ratio_delta(t["excess_per_pass_w"], r["excess_per_pass_w"])
        return {"verdict": v, "line_w": L, "excess_w": t["excess_w"], "excess_lo95": lo, "excess_hi95": hi,
                "reference_excess_w": r["excess_w"], "ratio": rr, "test": test, "reference": ref}

    rules = reg["rules"]
    r1 = R["E127-R1"]["verdict"] == "PASS"
    R["E127-R2"] = against(rules["E127-R2"]["test"], b1, "E127-R2", ("GATE", "DATA", "OPPOSITE"),
                           (r1, "R1 did not PASS: no replicated miss to locate"))
    f1 = rules["E127-R3"]["reference"]
    f1_ok = ok(f1) and C[f1]["excess_lo95"] > 0
    R["E127-R3"] = against(rules["E127-R3"]["test"], f1, "E127-R3", ("GATE", "DATA", "OPPOSITE"),
                           (f1_ok, "fp16's random pair shows no excess over M5 (its low end <= 0)"))
    R["E127-R4"] = against(rules["E127-R4"]["test"], b1, "E127-R4", ("PER-LANE", "ALL-OFF", None),
                           (r1, "R1 did not PASS"))
    gate = R["E127-R2"]["verdict"] == "GATE"
    q1 = rules["E127-R2"]["test"]
    R["E127-R4q"] = against(rules["E127-R4q"]["test"], q1, "E127-R4q", ("PER-LANE", "ALL-OFF", None),
                            (gate, "R2 is not GATE: no quiet-data miss to locate"))
    R["E127-R5"] = against(rules["E127-R5"]["test"], q1, "E127-R5", ("LONG", "SHORT", None),
                           (gate, "R2 is not GATE: no quiet-data miss to time"))
    q5 = rules["E127-R6"]["contrast"]
    if ok(q5):
        c = C[q5]
        w = rules["E127-R6"]["tolerance_w"]
        v = "PASS" if abs(c["measured_w"]) + c["ci95_w"] <= w else ("FAIL" if abs(c["measured_w"]) - c["ci95_w"] > w else "INCONCLUSIVE")
        R["E127-R6"] = {"verdict": v, "measured_w": c["measured_w"], "ci95_w": c["ci95_w"], "tolerance_w": w}
    else:
        R["E127-R6"] = {"verdict": "UNRESOLVED"}
    cells, good_all = {}, True
    for cell, v in reg["session_tie"]["cells"].items():
        d = ((items.get(cell) or {}).get("D") or {}).get("mean")
        good = d is not None and abs(d - v["ref_w"]) <= v["band_w"]
        good_all &= good
        cells[cell] = {"D": d, "ref_w": v["ref_w"], "band_w": v["band_w"], "inside": good}
    R["E127-S1"] = {"verdict": "PASS" if good_all else "FAIL", "cells": cells}
    ins = [r["inside_M5"] for r in out["table"].values()]
    out["reported"] = {"coverage_M5": {"inside": sum(ins), "n": len(ins)},
                       "coverage_M4": {"inside": sum(r["inside_M4"] for r in out["table"].values()), "n": len(ins)}}
    tally = {}
    for r in R.values():
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    out["tally"] = tally
    return out


def md(sc, reg, path):
    P = sc["primary"]
    L = [f"# E127: the float B-lane gate held steady against switching it, at equal operand activity: results\n",
         f"Written by `tools/claims-v3/e127/score_e127.py` from `{sc['input']}` (footing a3, the registered reading). "
         f"Kept passes: {P['passes']}; set aside: {[x.get('pass') for x in (P.get('set_aside') or [])]}; "
         f"reducer arm: {P.get('reducer_arm')}.\n"]
    L.append("\n## Rules\n\n| rule | verdict | what |\n|---|---|---|\n")
    for rid, r in P["rules"].items():
        what = []
        for q in ("measured_w", "ci95_w", "excess_w", "excess_lo95", "excess_hi95", "line_w", "reference_excess_w"):
            if isinstance(r.get(q), (int, float)):
                what.append(f"{q} {r[q]:+.3f}")
        if isinstance(r.get("ratio"), dict):
            what.append(f"ratio {r['ratio']['ratio']:.2f} [{r['ratio']['lo95']:.2f}, {r['ratio']['hi95']:.2f}]")
        if r.get("why"):
            what.append(r["why"])
        L.append(f"| {rid} | **{r['verdict']}** | {'; '.join(what)} |\n")
    L.append("\n## Contrasts (W; measured is the mean over kept passes of D(plus) - D(minus) inside each pass, 95% t)\n\n"
             "| contrast | measured | M5 [95%] | excess over M5 | M4 | verdict |\n|---|---:|---:|---:|---:|---|\n")
    for n, c in P["contrasts"].items():
        if c.get("verdict") not in ("INSIDE", "BELOW", "ABOVE"):
            L.append(f"| `{n}` | - | - | - | - | {c.get('verdict')} |\n")
            continue
        L.append(f"| `{n}` | {c['measured_w']:+.3f} +- {c['ci95_w']:.3f} | {c['M5_w']:+.3f} [{c['lo95']:+.3f}, {c['hi95']:+.3f}] | "
                 f"{c['excess_w']:+.3f} [{c['excess_lo95']:+.3f}, {c['excess_hi95']:+.3f}] | {c['M4_w']:+.3f} | {c['verdict']} |\n")
    L.append("\n## Tiles (D over the type's zeros, W, 95% over kept passes)\n\n| tile | family | D | M5 [95%] | D - M5 | inside | M4 | D - M4 |\n"
             "|---|---|---:|---:|---:|---|---:|---:|\n")
    for n, r in sorted(P["table"].items()):
        ci = f" +- {r['ci95']:.3f}" if r.get("ci95") is not None else ""
        L.append(f"| `{n}` | {r['family']} | {r['D']:.3f}{ci} | {r['M5']:.3f} [{r['lo95']:.3f}, {r['hi95']:.3f}] | {r['err_M5']:+.3f} | "
                 f"{'yes' if r['inside_M5'] else 'no'} | {r['M4']:.3f} | {r['err_M4']:+.3f} |\n")
    L.append("\n## Beside the primary\n\n| reading | " + " | ".join(P["rules"]) + " |\n|---|" + "---|" * len(P["rules"]) + "\n")
    for nm, s in [("anchor footing", sc.get("anchor_footing"))] + list((sc.get("arms") or {}).items()):
        if s:
            L.append(f"| {nm} | " + " | ".join(s["rules"].get(r, {}).get("verdict", "-") for r in P["rules"]) + " |\n")
    open(path, "w").write("".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e127", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    res = json.load(open(a.e127))
    sc = {"input": os.path.basename(a.e127), "primary": score(res, reg, "a3"), "anchor_footing": score(res, reg, "anchor"),
          "arms": {}}
    for arm in a.arm:
        name, path = arm.split("=", 1)
        sc["arms"][name] = score(json.load(open(path)), reg, "a3")
    for rid in sc["primary"]["rules"]:
        v0 = sc["primary"]["rules"][rid]["verdict"]
        sc["primary"]["rules"][rid]["footing_sensitive"] = sc["anchor_footing"]["rules"].get(rid, {}).get("verdict") != v0
        sc["primary"]["rules"][rid]["arm_sensitive"] = sorted(n for n, s in sc["arms"].items() if s["rules"].get(rid, {}).get("verdict") != v0)
    if a.json:
        json.dump(sc, open(a.json, "w"), indent=1)
    if a.md:
        md(sc, reg, a.md)
    print(json.dumps({rid: r["verdict"] for rid, r in sc["primary"]["rules"].items()}))


if __name__ == "__main__":
    main()
