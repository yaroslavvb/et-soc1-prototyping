#!/usr/bin/env python3
"""E113 (Q133): the A side's two layouts at fixed Hamming weight, scored as registered (README.md, this directory).

    python3 tools/claims-v3/e113/score_e113.py --runs runs.csv --pred predictions-e113.json [--hl hl.json] \
        [--arm NAME=runs-leak0.2.csv ...] [--all-passes] --out report.md --json scored.json

runs.csv is hl/reduce_hl.py's per-run table (its gates already applied per run: clock, voltage, launch, records, cycles
per op). This script applies the registered PASS gates (E67's two and E70's departure D-a), forms one value per (pass,
item), and computes every contrast as a PAIRED per-pass difference: the unit of replication is the pass and every SE
is the between-pass scatter of that difference. Pure stdlib.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os

N_A, N_B = 2048, 4096
ALQ_K = [1, 2, 3, 4, 6, 8, 12, 16, 23]
ALS_K = [2, 3, 4, 6, 8, 12, 16]
FIT_A = [f"alq_h{k}" for k in ALQ_K if k != 23] + [f"als_h{k}" for k in ALS_K]    # 15 rungs; alq_h23 out of the fits
CONST_ITEMS = ["lq_h0", "aq_h0", "anchor_pi"]       # one physical state by three routes (anchor_pi runs twice)
DRIFT_GATE_W, SPREAD_GATE_W = 0.3, 0.45             # E67's registered gate; E70's departure D-a
MIN_PASSES = 3
ZERO = {"alq": "aq_h0", "als": "aq_h0", "nrd_a": "aq_h0", "nrd_b": "lq_h0", "lq": "lq_h0", "ls": "lq_h0"}


def zero_of(item):
    if item.startswith("alq_") or item.startswith("als_") or item == "nrd_a":
        return "aq_h0"
    if item.startswith("lq_") or item.startswith("ls_") or item == "nrd_b":
        return "lq_h0"
    return None


def mean_se(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None, None, 0
    m = sum(xs) / len(xs)
    if len(xs) == 1:
        return m, None, 1
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(v / len(xs)), len(xs)


T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def ci95(m, se, n):
    if m is None or se is None or n < 2:
        return None
    t = T975.get(n - 1, 1.96)
    return [m - t * se, m + t * se]


def cov(s, w):
    return w * (1 - math.exp(-s / w)) if w > 0 else 0.0


def fit_w(points):
    """Least-squares W of dW = W (1 - exp(-S/W)): log scan then golden refine (E70's fit_ceiling, finer)."""
    def err(w):
        return sum((cov(s, w) - y) ** 2 for s, y in points)
    best, lo, hi, n = None, 0.3, 400.0, 4000
    for i in range(n + 1):
        w = lo * (hi / lo) ** (i / n)
        e = err(w)
        if best is None or e < best[1]:
            best = (w, e)
    a, b = best[0] / 1.003, best[0] * 1.003
    g = (math.sqrt(5) - 1) / 2
    for _ in range(60):
        c_, d_ = b - g * (b - a), a + g * (b - a)
        if err(c_) < err(d_):
            b = d_
        else:
            a = c_
    w = 0.5 * (a + b)
    return w, math.sqrt(err(w) / len(points))


def fit_scale(points):
    """Least squares through the origin, y = c x."""
    sxx = sum(x * x for x, _ in points)
    c = sum(x * y for x, y in points) / sxx if sxx else 0.0
    return c, math.sqrt(sum((y - c * x) ** 2 for x, y in points) / len(points))


def rms(res):
    res = [r for r in res if r is not None]
    return math.sqrt(sum(r * r for r in res) / len(res)) if res else None


def load_runs(path):
    out = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                r["pass"] = int(r["pass"])
                r["pos"] = int(r["pos"])
                r["p80"] = float(r["p80"]) if r["p80"] not in ("", "None") else None
                r["rate"] = float(r["rate"]) if r.get("rate") not in ("", "None", None) else None
                r["rail"] = float(r["rail"]) if r.get("rail") not in ("", "None", None) else None
            except ValueError:
                continue
            r["failed"] = r["fail"] not in ("[]", "", None)
            out.append(r)
    return out


def gate(runs, use_gates=True):
    passes = sorted({r["pass"] for r in runs})
    per = {}
    for p in passes:
        rp = [r for r in runs if r["pass"] == p]
        good = [r for r in rp if not r["failed"] and r["p80"] is not None]
        nf = sum(1 for r in rp if r["failed"])
        pis = sorted([r for r in good if r["item"] == "anchor_pi"], key=lambda r: r["pos"])
        drift = pis[-1]["p80"] - pis[0]["p80"] if len(pis) >= 2 else None
        consts = [r["p80"] for r in good if r["item"] in CONST_ITEMS]
        spread = (max(consts) - min(consts)) if len(consts) >= 2 else None
        why = []
        if nf > 1:
            why.append(f"{nf} failed runs")
        if drift is not None and abs(drift) > DRIFT_GATE_W:
            why.append(f"anchor_pi drift {drift:+.3f} W")
        if use_gates and spread is not None and spread > SPREAD_GATE_W:
            why.append(f"constant-operand spread {spread:.3f} W")
        per[p] = {"pass": p, "n_runs": len(rp), "n_failed": nf, "pi_drift_W": drift, "const_spread_W": spread,
                  "n_const_runs": len(consts), "mean_rate": mean_se([r["rate"] for r in good])[0], "set_aside": why}
    kept = [p for p in passes if not per[p]["set_aside"]]
    return per, kept


def pass_values(runs, kept):
    val = {}
    for p in kept:
        d = {}
        for r in runs:
            if r["pass"] == p and not r["failed"] and r["p80"] is not None:
                d.setdefault(r["item"], []).append(r)
        val[p] = {k: {"p80": sum(x["p80"] for x in v) / len(v),
                      "rate": mean_se([x["rate"] for x in v])[0]} for k, v in d.items()}
    return val


def dw(val, p, item):
    z = zero_of(item)
    if z is None or item not in val[p] or z not in val[p]:
        return None
    return val[p][item]["p80"] - val[p][z]["p80"]


def score(runs, pred, use_gates=True, all_passes=False):
    per, kept = gate(runs, use_gates=use_gates)
    if all_passes:
        kept = [p for p in per if per[p]["n_failed"] <= 1]
    val = pass_values(runs, kept)
    R = {"passes_all": sorted(per), "passes_kept": kept, "pass_table": per,
         "n_runs": len(runs), "n_runs_failed": sum(1 for r in runs if r["failed"])}
    R["scored_ok"] = len(kept) >= MIN_PASSES
    rung_pred = {r["item"]: r for r in pred["rungs"]}
    C = pred["constants"]
    items = {}
    names = sorted({r["item"] for r in runs if zero_of(r["item"])})
    for it in names:
        m, se, n = mean_se([dw(val, p, it) for p in kept])
        rate = mean_se([val[p][it]["rate"] for p in kept if it in val[p]])[0]
        ent = {"item": it, "dW": m, "se": se, "n_passes": n, "ci95": ci95(m, se, n), "zero": zero_of(it)}
        rp = rung_pred.get(it)
        if rp:
            k = rp["k"]
            ent.update({"k": k, "layout": rp["layout"], "bits": rp["bits"], "S_A_W": rp["S_A_W"],
                        "B_same_mask_E70_W": rp["B_same_mask_E70_W"],
                        "pred_A_W": rp["pred_A_W"], "pred_WA_W": rp["pred_WA_W"], "pred_M_W": rp["pred_M_W"],
                        "E70_measured_W": rp.get("E70_measured_W"), "E70_se_W": rp.get("E70_se_W")})
            if m is not None and rate:
                ent["fJ_per_designed_bit"] = 1e15 * m / (N_A * k * rate)
        items[it] = ent
    R["items"] = items

    # ---- D1_A: the matched-k layout contrast, paired per pass
    d1 = []
    for k in ALS_K:
        a, b = f"als_h{k}", f"alq_h{k}"
        diffs = [val[p][a]["p80"] - val[p][b]["p80"] for p in kept if a in val[p] and b in val[p]]
        m, se, n = mean_se(diffs)
        pr = [d for d in pred["D1_A_layout_contrast"] if d["k"] == k][0]
        d1.append({"k": k, "dW_spread_minus_low": m, "se": se, "n_passes": n, "ci95": ci95(m, se, n),
                   "sigma_from_zero": (m / se) if (m is not None and se) else None,
                   "pred_H": 0.0, "pred_WA": pr["pred_WA"], "pred_M": pr["pred_M"], "pred_A": pr["pred_A"],
                   "B_side_D1_E70_W": pr["B_side_D1_E70_W"]})
    R["D1_A"] = d1

    # ---- D2_A: what collapses the two A layouts (15 rungs; alq_h23 out of sample)
    pts = [(items[n]["S_A_W"], items[n]["dW"], items[n]["B_same_mask_E70_W"], items[n]["k"], n)
           for n in FIT_A if n in items and items[n]["dW"] is not None]
    D2 = {"fit_set": FIT_A, "n_rungs": len(pts)}
    if len(pts) >= 5:
        byk = {}
        for s, y, b, k, n in pts:
            byk.setdefault(k, []).append(y)
        res_k = [y - sum(byk[k]) / len(byk[k]) for s, y, b, k, n in pts]
        res_k_m = [y - sum(byk[k]) / len(byk[k]) for s, y, b, k, n in pts if len(byk[k]) > 1]
        D2["R_k_W"] = rms(res_k)
        D2["R_k_matched_only_W"] = rms(res_k_m)
        wa, r_sa = fit_w([(s, y) for s, y, b, k, n in pts])
        D2["WA_refit_W"], D2["R_SA_refit_W"] = wa, r_sa
        D2["R_SA_frozen_W"] = rms([y - cov(s, C["WA_W"]) for s, y, b, k, n in pts])
        D2["R_A_additive_W"] = rms([y - s for s, y, b, k, n in pts])
        c, r_m = fit_scale([(b, y) for s, y, b, k, n in pts])
        D2["c_refit"], D2["R_M_refit_W"] = c, r_m
        D2["R_M_frozen_W"] = rms([y - C["mirror_c"] * b for s, y, b, k, n in pts])
        # out of sample for both frozen laws: the 7 spread rungs (c and WA were fitted on E70's low layout only)
        spr = [(s, y, b) for s, y, b, k, n in pts if n.startswith("als_")]
        D2["R_M_frozen_spread_W"] = rms([y - C["mirror_c"] * b for s, y, b in spr])
        D2["R_SA_frozen_spread_W"] = rms([y - cov(s, C["WA_W"]) for s, y, b in spr])
        D2["R_A_additive_spread_W"] = rms([y - s for s, y, b in spr])
        D2["n_spread"] = len(spr)
        D2["residuals"] = [{"item": n, "k": k, "dW": y, "res_SA_refit": y - cov(s, wa), "res_M_refit": y - c * b,
                            "res_M_frozen": y - C["mirror_c"] * b, "res_k": y - sum(byk[k]) / len(byk[k])}
                           for s, y, b, k, n in pts]
        # per-pass refits, so each fitted constant carries a between-pass SE
        wa_pp, c_pp = [], []
        for p in kept:
            pp = [(items[n]["S_A_W"], dw(val, p, n), items[n]["B_same_mask_E70_W"]) for n in FIT_A
                  if n in items and dw(val, p, n) is not None]
            if len(pp) >= 5:
                wa_pp.append(fit_w([(s, y) for s, y, b in pp])[0])
                c_pp.append(fit_scale([(b, y) for s, y, b in pp])[0])
        D2["WA_per_pass"], D2["c_per_pass"] = wa_pp, c_pp
        D2["WA_per_pass_mean_se"] = mean_se(wa_pp)[:2]
        D2["c_per_pass_mean_se"] = mean_se(c_pp)[:2]
        top = items.get("alq_h23")
        if top and top["dW"] is not None:
            D2["out_of_sample_alq_h23"] = {
                "dW": top["dW"], "se": top["se"],
                "res_SA_refit": top["dW"] - cov(top["S_A_W"], wa),
                "res_SA_refit_sigma": (top["dW"] - cov(top["S_A_W"], wa)) / top["se"] if top["se"] else None,
                "res_M_refit": top["dW"] - c * top["B_same_mask_E70_W"],
                "res_M_refit_sigma": (top["dW"] - c * top["B_same_mask_E70_W"]) / top["se"] if top["se"] else None,
                "res_M_frozen": top["dW"] - C["mirror_c"] * top["B_same_mask_E70_W"],
                "above_WA_refit_by_W": top["dW"] - wa,
                "above_WA_refit_sigma": (top["dW"] - wa) / top["se"] if top["se"] else None}
    R["D2_A"] = D2

    # ---- rho(8): the per-bit A/B ratio at k = 8 in both layouts, from E113's own passes (B ties lq_h8, ls_h8)
    def rho(a, b):
        rs = []
        for p in kept:
            x, y = dw(val, p, a), dw(val, p, b)
            if x is not None and y:
                rs.append(2 * x / y)
        m, se, n = mean_se(rs)
        ma, mb = items.get(a, {}).get("dW"), items.get(b, {}).get("dW")
        return {"rho": m, "se": se, "n_passes": n, "ratio_of_means": (2 * ma / mb) if (ma is not None and mb) else None,
                "per_pass": rs}
    rl, rs_ = rho("alq_h8", "lq_h8"), rho("als_h8", "ls_h8")
    dd = []
    for p in kept:
        x1, y1, x2, y2 = dw(val, p, "alq_h8"), dw(val, p, "lq_h8"), dw(val, p, "als_h8"), dw(val, p, "ls_h8")
        if None not in (x1, y1, x2, y2) and y1 and y2:
            dd.append(2 * x2 / y2 - 2 * x1 / y1)
    m, se, n = mean_se(dd)
    R["rho8"] = {"low": rl, "spread": rs_, "spread_minus_low": {"d": m, "se": se, "n_passes": n, "ci95": ci95(m, se, n)},
                 "pred": pred["rho8"]}

    # ---- B tie and replicate
    b1 = mean_se([val[p]["ls_h8"]["p80"] - val[p]["lq_h8"]["p80"] for p in kept if "ls_h8" in val[p] and "lq_h8" in val[p]])
    rep = {}
    for k in (1, 2, 4, 8, 12, 16, 23):
        it = f"alq_h{k}"
        e = pred["E70_replicate"].get(it)
        if it in items and items[it]["dW"] is not None and e:
            rep[it] = {"E113": items[it]["dW"], "E113_se": items[it]["se"], "E70": e["W"], "E70_se": e["se"],
                       "diff": items[it]["dW"] - e["W"], "band": 1.0 if k == 23 else 0.6}
    R["replicate"] = {"alq": rep, "D1_B_h8": {"E113": b1[0], "E113_se": b1[1], "n_passes": b1[2],
                                             "E70": pred["E70_B_ties"]["D1_B_h8"]["W"],
                                             "diff": (b1[0] - pred["E70_B_ties"]["D1_B_h8"]["W"]) if b1[0] is not None else None}}
    # ---- the random-word check: nrd_a against c * nrd_b, in the same passes
    rr = []
    for p in kept:
        x, y = dw(val, p, "nrd_a"), dw(val, p, "nrd_b")
        if x is not None and y:
            rr.append(x / y)
    m, se, n = mean_se(rr)
    R["nrd"] = {"ratio_nrd_a_over_nrd_b": m, "se": se, "n_passes": n, "pred_M_c": C["mirror_c"],
                "nrd_a": items.get("nrd_a", {}).get("dW"), "nrd_b": items.get("nrd_b", {}).get("dW")}
    if D2.get("WA_refit_W") and items.get("nrd_a", {}).get("dW") is not None:
        s_nrd = pred["nrd_a_E70"]["S_additive_W"]
        R["nrd"]["pred_SA_refit_W"] = cov(s_nrd, D2["WA_refit_W"])
        R["nrd"]["ratio_measured_over_SA_refit"] = items["nrd_a"]["dW"] / cov(s_nrd, D2["WA_refit_W"])
    R["rules"] = rules(R) if R["scored_ok"] else {"note": f"NOT SCORED: {len(kept)} passes kept, the rules need {MIN_PASSES}"}
    return R


def rules(R):
    out = {}
    d8 = [d for d in R["D1_A"] if d["k"] == 8][0]
    m, se = d8["dW_spread_minus_low"], d8["se"]
    ci = d8["ci95"]
    if m is not None and se and m > 1.0 and m / se >= 3:
        v = "PASS"
    elif m is not None and ci and m < 0.5 and ci[1] < 1.0:
        v = "FAIL (how many)"
    else:
        v = "INCONCLUSIVE"
    out["P1"] = {"asked": "dW(als_h8) - dW(alq_h8) > 1.0 W at >= 3 SE (H needs 0; WA 1.19, M 2.48, A 3.96 W)",
                 "measured": m, "se": se, "verdict": v}
    D2 = R["D2_A"]
    r = D2.get("R_SA_refit_W")
    out["P2"] = {"asked": "one saturating curve in A's own additive sum S_A, W refitted on the 15 A rungs: ACCEPTED if rms "
                          "<= 0.40 W, REJECTED if > 0.60 W (E70: 1.063 W on the low layout alone)",
                 "measured": r, "WA_refit_W": D2.get("WA_refit_W"),
                 "verdict": None if r is None else ("ACCEPTED" if r <= 0.40 else ("REJECTED" if r > 0.60 else "INCONCLUSIVE"))}
    r0 = D2.get("R_M_frozen_spread_W")
    out["P3"] = {"asked": "the mirror law with c frozen at 0.643 (fitted on E70's low layout; no free parameter): rms over the 7 "
                          "spread rungs <= 0.50 W PASS, > 0.80 W FAIL (WA frozen and law A beside it, reported)",
                 "measured": r0, "R_SA_frozen_spread_W": D2.get("R_SA_frozen_spread_W"),
                 "R_A_additive_spread_W": D2.get("R_A_additive_spread_W"), "R_M_frozen_all15_W": D2.get("R_M_frozen_W"),
                 "c_refit": D2.get("c_refit"),
                 "verdict": None if r0 is None else ("PASS" if r0 <= 0.50 else ("FAIL" if r0 > 0.80 else "INCONCLUSIVE"))}
    rk, rsa, rm = D2.get("R_k_W"), D2.get("R_SA_refit_W"), D2.get("R_M_refit_W")
    best1 = min(x for x in (rsa, rm) if x is not None) if (rsa is not None or rm is not None) else None
    if out["P1"]["verdict"] == "PASS" and best1 is not None and rk is not None and best1 < rk / 2:
        form = "which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k"
    elif out["P1"]["verdict"].startswith("FAIL") and rk is not None and best1 is not None and rk < best1 / 2:
        form = "how many: the two A layouts collapse on k"
    else:
        form = "both or neither: no collapse wins by 2x"
    if rsa is not None and rm is not None:
        if rsa / rm >= 1.5:
            which = "the mirror law (the same mask's B rung, scaled) collapses the A side better than a curve in S_A"
        elif rm / rsa >= 1.5:
            which = "a curve in S_A collapses the A side better than the mirror law"
        else:
            which = "the mirror law and a curve in S_A are not separated (ratio under 1.5)"
    else:
        which = None
    out["P4"] = {"asked": "the verdict on the A side's form, read off D1_A(8) and D2_A together (README)",
                 "R_k_W": rk, "R_SA_refit_W": rsa, "R_M_refit_W": rm, "verdict": form, "one_parameter_laws": which}
    rl, rsp, dd = R["rho8"]["low"], R["rho8"]["spread"], R["rho8"]["spread_minus_low"]
    ok_band = all(x["rho"] is not None and 0.7 <= x["rho"] <= 2.5 for x in (rl, rsp))
    if ok_band and dd["d"] is not None and abs(dd["d"]) <= 0.30:
        v5 = "PASS"
    elif dd["d"] is not None and dd["se"] and abs(dd["d"]) > 0.30 and abs(dd["d"]) / dd["se"] >= 3:
        v5 = "FAIL (the A/B weight depends on the layout)"
    elif not ok_band:
        v5 = "FAIL (outside [0.7, 2.5])"
    else:
        v5 = "INCONCLUSIVE"
    out["P5"] = {"asked": "rho(8) per designed bit, A over B, in both layouts inside [0.7, 2.5] and |spread - low| <= 0.30 "
                          "(M: 1.29 both; WA spread 1.40; A spread 2.74; H spread 0.55)",
                 "rho_low": rl["rho"], "rho_spread": rsp["rho"], "spread_minus_low": dd["d"], "se": dd["se"], "verdict": v5}
    rep = R["replicate"]
    fails = [k for k, v in rep["alq"].items() if abs(v["diff"]) > v["band"]]
    b = rep["D1_B_h8"]
    b_ok = b["diff"] is not None and abs(b["diff"]) <= 0.6
    out["P6"] = {"asked": "E70's seven alq rungs within 0.6 W (alq_h23 within 1.0 W) and ls_h8 - lq_h8 within 0.6 W of 3.860 W",
                 "alq_outside": fails, "D1_B_h8": b["E113"], "D1_B_h8_diff": b["diff"],
                 "verdict": "PASS" if (not fails and b_ok and len(rep["alq"]) == 7) else "FAIL"}
    n = R["nrd"]
    v7 = None
    if n["ratio_nrd_a_over_nrd_b"] is not None:
        v7 = "PASS" if 0.55 <= n["ratio_nrd_a_over_nrd_b"] <= 0.75 else "FAIL"
    out["P7"] = {"asked": "the random-word check: dW(nrd_a) / dW(nrd_b) in the same passes inside [0.55, 0.75] (M: c = 0.643; "
                          "E70's own pair read 0.668, seen before this registration)",
                 "measured": n["ratio_nrd_a_over_nrd_b"], "se": n["se"], "verdict": v7}
    return out


def fmt(x, nd=3):
    return "—" if x is None else f"{x:.{nd}f}"


def write_report(R, arms, path):
    L = []
    w = L.append
    w("# E113 — the A side's two layouts at fixed Hamming weight (scored)\n")
    w(f"Passes run {R['passes_all']}, kept {R['passes_kept']} (E67's two gates and E70's D-a). Runs {R['n_runs']}, "
      f"failed a per-run gate {R['n_runs_failed']}.\n")
    w("## Pass health\n")
    w("| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (Gop/s) | set aside |")
    w("|---|---|---|---|---|---|---|")
    for p, d in sorted(R["pass_table"].items()):
        w(f"| {p} | {d['n_runs']} | {d['n_failed']} | {fmt(d['pi_drift_W'])} | {fmt(d['const_spread_W'])} | "
          f"{fmt(d['mean_rate'] / 1e9 if d['mean_rate'] else None, 4)} | {', '.join(d['set_aside']) or '—'} |")
    w("\n## The rungs (W over the zero, paired per pass; mean ± SE over the kept passes)\n")
    w("| item | k | layout | bits | dW (W) | ± SE | fJ / designed bit | S_A | law A | law WA (6.37) | law M (c 0.643) | E70 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n, e in sorted(R["items"].items(), key=lambda kv: (kv[1].get("layout") or "z", kv[1].get("k") or 0, kv[0])):
        w(f"| `{n}` | {e.get('k', '—')} | {e.get('layout', '—')} | {str(e.get('bits', '—')).replace(' ', '')} | "
          f"{fmt(e['dW'])} | {fmt(e['se'])} | {fmt(e.get('fJ_per_designed_bit'), 0)} | {fmt(e.get('S_A_W'))} | "
          f"{fmt(e.get('pred_A_W'))} | {fmt(e.get('pred_WA_W'))} | {fmt(e.get('pred_M_W'))} | {fmt(e.get('E70_measured_W'))} |")
    w("\n## D1_A: spread minus low at the same k (paired per pass)\n")
    w("| k | measured (W) | ± SE | 95% | σ from 0 | H | WA | M | A | B side, E70 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for d in R["D1_A"]:
        ci = d["ci95"]
        w(f"| {d['k']} | {fmt(d['dW_spread_minus_low'])} | {fmt(d['se'])} | "
          f"{'—' if not ci else f'[{ci[0]:.3f}, {ci[1]:.3f}]'} | {fmt(d['sigma_from_zero'], 1)} | 0 | {fmt(d['pred_WA'])} | "
          f"{fmt(d['pred_M'])} | {fmt(d['pred_A'])} | {fmt(d['B_side_D1_E70_W'])} |")
    D2 = R["D2_A"]
    w("\n## D2_A: what collapses the two A layouts (15 rungs; `alq_h23` out of sample)\n")
    w("| law | free parameters | rms (W) |")
    w("|---|---|---|")
    w(f"| a free value per k (the best any 'how many' law can do) | one per k | {fmt(D2.get('R_k_W'))} "
      f"(matched k only {fmt(D2.get('R_k_matched_only_W'))}) |")
    w(f"| one saturating curve in A's own sum S_A, W refitted ({fmt(D2.get('WA_refit_W'), 2)} W) | 1 | {fmt(D2.get('R_SA_refit_W'))} |")
    w(f"| the same curve, W frozen at E70's 6.37 W | 0 | {fmt(D2.get('R_SA_frozen_W'))} |")
    w(f"| the mirror: c × the same mask's B rung (E70), c refitted ({fmt(D2.get('c_refit'), 4)}) | 1 | {fmt(D2.get('R_M_refit_W'))} |")
    w(f"| the mirror, c frozen at 0.643 | 0 | {fmt(D2.get('R_M_frozen_W'))} |")
    w(f"| additive (S_A) | 0 | {fmt(D2.get('R_A_additive_W'))} |")
    w(f"\nOut of sample for the frozen laws, the {D2.get('n_spread')} spread rungs alone: mirror (c 0.643) "
      f"{fmt(D2.get('R_M_frozen_spread_W'))} W, WA (6.37 W) {fmt(D2.get('R_SA_frozen_spread_W'))} W, additive "
      f"{fmt(D2.get('R_A_additive_spread_W'))} W.")
    if D2.get("WA_per_pass_mean_se"):
        m, se = D2["WA_per_pass_mean_se"]
        mc, sc = D2["c_per_pass_mean_se"]
        w(f"\nPer-pass refits: W {fmt(m, 3)} ± {fmt(se, 3)} W; c {fmt(mc, 4)} ± {fmt(sc, 4)}.")
    o = D2.get("out_of_sample_alq_h23")
    if o:
        w(f"\nOut of sample, `alq_h23` ({fmt(o['dW'])} ± {fmt(o['se'])} W): the refitted S_A curve misses it by "
          f"{fmt(o['res_SA_refit'])} W ({fmt(o['res_SA_refit_sigma'], 1)} SE) and it sits {fmt(o['above_WA_refit_by_W'])} W "
          f"({fmt(o['above_WA_refit_sigma'], 1)} SE) above the refitted W; the refitted mirror misses it by "
          f"{fmt(o['res_M_refit'])} W ({fmt(o['res_M_refit_sigma'], 1)} SE), the frozen mirror by {fmt(o['res_M_frozen'])} W.")
    rh = R["rho8"]
    w("\n## rho(8): per designed bit, A over B, at the same mask (E113's own B ties)\n")
    w(f"- low: {fmt(rh['low']['rho'])} ± {fmt(rh['low']['se'])} (ratio of means {fmt(rh['low']['ratio_of_means'])})")
    w(f"- spread: {fmt(rh['spread']['rho'])} ± {fmt(rh['spread']['se'])} (ratio of means {fmt(rh['spread']['ratio_of_means'])})")
    w(f"- spread − low: {fmt(rh['spread_minus_low']['d'])} ± {fmt(rh['spread_minus_low']['se'])}")
    rp = R["replicate"]
    w("\n## Replicate of E70 and the B tie\n")
    w("| item | E113 | ± SE | E70 | difference | band |")
    w("|---|---|---|---|---|---|")
    for k, v in rp["alq"].items():
        w(f"| `{k}` | {fmt(v['E113'])} | {fmt(v['E113_se'])} | {fmt(v['E70'])} | {v['diff']:+.3f} | {v['band']} |")
    b = rp["D1_B_h8"]
    w(f"| `ls_h8` − `lq_h8` | {fmt(b['E113'])} | {fmt(b['E113_se'])} | {fmt(b['E70'])} | "
      f"{'—' if b['diff'] is None else f'{b['diff']:+.3f}'} | 0.6 |")
    n = R["nrd"]
    w(f"\nRandom words: `nrd_a` {fmt(n['nrd_a'])} W, `nrd_b` {fmt(n['nrd_b'])} W, ratio {fmt(n['ratio_nrd_a_over_nrd_b'])} ± "
      f"{fmt(n['se'])} (mirror c 0.643); the refitted S_A curve predicts `nrd_a` {fmt(n.get('pred_SA_refit_W'))} W "
      f"(measured/predicted {fmt(n.get('ratio_measured_over_SA_refit'))}).")
    w("\n## The registered rules\n")
    if "note" in R["rules"]:
        w(R["rules"]["note"])
    else:
        w("| rule | asked | measured | verdict |")
        w("|---|---|---|---|")
        for k, v in R["rules"].items():
            meas = {kk: vv for kk, vv in v.items() if kk not in ("asked", "verdict")}
            ms = "; ".join(f"{kk} {fmt(vv) if isinstance(vv, float) else vv}" for kk, vv in meas.items())
            w(f"| {k} | {v['asked']} | {ms} | **{v['verdict']}** |")
    if arms:
        w("\n## Arms (reported, never verdicts)\n")
        w("| arm | passes kept | D1_A(8) | R_k | R_SA refit (W) | R_M frozen | R_M refit | c refit | rho8 low / spread | verdicts P1-P7 |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for name, A in arms.items():
            d8 = [d for d in A["D1_A"] if d["k"] == 8][0]
            D = A["D2_A"]
            vs = " ".join(f"{k}:{v['verdict']}" for k, v in A["rules"].items()) if "note" not in A["rules"] else A["rules"]["note"]
            w(f"| {name} | {A['passes_kept']} | {fmt(d8['dW_spread_minus_low'])} ± {fmt(d8['se'])} | {fmt(D.get('R_k_W'))} | "
              f"{fmt(D.get('R_SA_refit_W'))} | {fmt(D.get('R_M_frozen_W'))} | {fmt(D.get('R_M_refit_W'))} | "
              f"{fmt(D.get('c_refit'), 4)} | {fmt(A['rho8']['low']['rho'])} / {fmt(A['rho8']['spread']['rho'])} | {vs} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--hl")
    ap.add_argument("--arm", action="append", default=[], help="NAME=runs.csv, a labelled sensitivity")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    runs = load_runs(a.runs)
    R = score(runs, pred)
    if a.hl and os.path.exists(a.hl):
        hl = json.load(open(a.hl))
        g = list(hl.get("gates", {}).values())
        if g:
            R["leak_W_per_C"], R["clock_mhz"] = g[0].get("leak_W_per_C"), g[0].get("clock_mhz")
    arms = {"all passes (E67's gates, no D-a)": score(runs, pred, all_passes=True)}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        arms[name] = score(load_runs(path), pred)
    R["arms"] = {k: {"passes_kept": v["passes_kept"], "rules": v["rules"], "D1_A": v["D1_A"], "D2_A": v["D2_A"],
                     "rho8": v["rho8"], "items": {n: {"dW": e["dW"], "se": e["se"]} for n, e in v["items"].items()}}
                 for k, v in arms.items()}
    write_report(R, arms, a.out)
    json.dump(R, open(a.json, "w"), indent=1, default=str)
    print(open(a.out).read())


if __name__ == "__main__":
    main()
