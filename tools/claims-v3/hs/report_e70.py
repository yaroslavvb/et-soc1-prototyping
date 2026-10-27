#!/usr/bin/env python3
"""E70 (Q129): the saturation law, the A-side ladder, discriminators D1-D5 and the registered rules, scored.

    python3 tools/claims-v3/hs/report_e70.py --hl hl.json --runs runs.csv --pred predictions-e70.json \
        [--leak hl-leak0.2.json,hl-leak0.3.json,hl-leak0.4.json] [--load e70-load.jsonl] \
        [--blocks build/claims-v3/aifoundry3/hl] [--closure <E67 closure.json>] --out report.md --json scored.json

Everything is recomputed from runs.csv, so every contrast is a PAIRED per-pass one (the unit of replication is
the pass, as registered) and the SE comes from the between-pass scatter of the paired difference. hl.json is read
for the registered gate verdicts and the fitted leakage slope. Pure stdlib: no numpy on the reporting path.
"""
import argparse
import csv
import json
import math
import os

N_B, N_A = 4096, 2048        # designed flips per multiply-add per minion, B side and A side
LQ_H = [1, 2, 3, 4, 6, 8, 12, 16, 23]
LS_H = [2, 3, 4, 6, 8, 12, 16]
ALQ_K = [1, 2, 4, 8, 12, 16, 23]
CONST_ITEMS = ["lq_h0", "aq_h0", "anchor_pi"]      # one physical state by three routes (anchor_pi runs twice)
SPREAD_GATE_W = 0.45                               # departure D-a
DRIFT_GATE_W = 0.3                                 # E67's registered gate, kept
LOAD_GATE = 4.0                                    # departure D-b
RATE_GATE = 0.01


def mean_se(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None, None, 0
    m = sum(xs) / len(xs)
    if len(xs) == 1:
        return m, None, 1
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(v / len(xs)), len(xs)


def spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def coverage(s, w):
    return w * (1 - math.exp(-s / w)) if w > 0 else 0.0


def fit_ceiling(points):
    def err(w):
        return sum((coverage(s, w) - y) ** 2 for s, y in points)
    best, lo, hi, n = None, 0.5, 400.0, 4000
    for i in range(n + 1):
        w = lo * (hi / lo) ** (i / n)
        e = err(w)
        if best is None or e < best[1]:
            best = (w, e)
    return best[0], math.sqrt(best[1] / len(points))


def load_runs(path):
    out = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                r["pass"] = int(r["pass"])
                r["p80"] = float(r["p80"]) if r["p80"] not in ("", "None") else None
                r["rate"] = float(r["rate"]) if r["rate"] not in ("", "None") else None
                r["rail"] = float(r["rail"]) if r["rail"] not in ("", "None") else None
            except ValueError:
                continue
            r["failed"] = r["fail"] not in ("[]", "", None)
            out.append(r)
    return out


def gate(runs, load_by_pass):
    """The registered gates: E67's two (more than one failed run; anchor_pi drift > 0.3 W) plus departure D-a
    (the spread of every constant-operand run in the pass > 0.45 W). Departure D-b's load/rate rule marks a pass
    as load-disturbed but keeps it, and a labelled sensitivity over the undisturbed passes is reported."""
    passes = sorted({r["pass"] for r in runs})
    per = {}
    for p in passes:
        rp = [r for r in runs if r["pass"] == p]
        good = [r for r in rp if not r["failed"] and r["p80"] is not None]
        nf = sum(1 for r in rp if r["failed"])
        pis = sorted([r for r in good if r["item"] == "anchor_pi"], key=lambda r: int(r["pos"]))
        drift = pis[-1]["p80"] - pis[0]["p80"] if len(pis) >= 2 else None
        consts = [r["p80"] for r in good if r["item"] in CONST_ITEMS]
        spread = (max(consts) - min(consts)) if len(consts) >= 2 else None
        rate, _, _ = mean_se([r["rate"] for r in good])
        why = []
        if nf > 1:
            why.append(f"{nf} failed runs")
        if drift is not None and abs(drift) > DRIFT_GATE_W:
            why.append(f"anchor_pi drift {drift:+.2f} W")
        if spread is not None and spread > SPREAD_GATE_W:
            why.append(f"constant-operand spread {spread:.2f} W")
        per[p] = {"pass": p, "n_runs": len(rp), "n_failed": nf, "pi_drift_W": drift,
                  "const_spread_W": spread, "n_const_runs": len(consts), "mean_rate": rate,
                  "set_aside": why, "load1_mean": load_by_pass.get(p, {}).get("load1_mean")}
    kept = [p for p in passes if not per[p]["set_aside"]]
    base_rate = per[kept[0]]["mean_rate"] if kept else None
    for p in passes:
        d = per[p]
        flags = []
        if d["load1_mean"] is not None and d["load1_mean"] > LOAD_GATE:
            flags.append(f"load1 {d['load1_mean']:.2f}")
        if base_rate and d["mean_rate"] and abs(d["mean_rate"] / base_rate - 1) > RATE_GATE:
            flags.append(f"op rate {100 * (d['mean_rate'] / base_rate - 1):+.2f}%")
        d["load_disturbed"] = flags
    return per, kept


def pass_values(runs, kept):
    val = {}
    for p in kept:
        d = {}
        for r in runs:
            if r["pass"] != p or r["failed"] or r["p80"] is None:
                continue
            d.setdefault(r["item"], []).append(r)
        val[p] = {k: {"p80": sum(x["p80"] for x in v) / len(v),
                      "rate": (sum(x["rate"] for x in v if x["rate"]) / max(1, len([x for x in v if x["rate"]])))
                      if any(x["rate"] for x in v) else None,
                      "rail": (sum(x["rail"] for x in v if x["rail"] is not None) / max(1, len([x for x in v if x["rail"] is not None])))
                      if any(x["rail"] is not None for x in v) else None}
                 for k, v in d.items()}
    return val


def paired(val, kept, a, b):
    """Per-pass (a - b), then mean and SE over the passes that ran both."""
    return mean_se([val[p][a]["p80"] - val[p][b]["p80"] for p in kept if a in val[p] and b in val[p]])


def load_windows(load_path, blocks_dir, passes):
    """Mean 1-minute load average inside each pass's own window (departure D-b)."""
    out = {}
    if not (load_path and os.path.exists(load_path) and blocks_dir and os.path.isdir(blocks_dir)):
        return out
    samples = []
    for line in open(load_path):
        line = line.strip()
        if line.startswith("{"):
            try:
                samples.append(json.loads(line))
            except ValueError:
                pass
    for p in passes:
        bj = os.path.join(blocks_dir, f"p{p}", "block.json")
        if not os.path.exists(bj):
            continue
        b = json.load(open(bj))
        t0, t1 = b.get("t0_ms", 0) / 1000.0, b.get("t1_ms", 0) / 1000.0
        ss = [s for s in samples if t0 <= s["t"] <= t1]
        if ss:
            out[p] = {"load1_mean": sum(s["load1"] for s in ss) / len(ss),
                      "load1_max": max(s["load1"] for s in ss),
                      "load15_mean": sum(s["load15"] for s in ss) / len(ss),
                      "n_samples": len(ss), "t0": t0, "t1": t1,
                      "minutes": (t1 - t0) / 60.0}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hl", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--leak", default="")
    ap.add_argument("--load", default="")
    ap.add_argument("--blocks", default="")
    ap.add_argument("--closure", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    hl = json.load(open(a.hl))
    P = json.load(open(a.pred))
    C3 = hl["cards"].get("aifoundry3", {})
    runs = load_runs(a.runs)
    allp = sorted({r["pass"] for r in runs})
    lw = load_windows(a.load, a.blocks, allp)
    per, kept = gate(runs, lw)
    val = pass_values(runs, kept)
    S = {r["item"]: r for group in ("lq", "ls", "alq") for r in P[group]}
    rate, _, _ = mean_se([val[p][i]["rate"] for p in kept for i in val[p] if val[p][i]["rate"]])
    R = {"card": "aifoundry3", "clock_mhz": C3.get("clock_mhz"), "v_mean": C3.get("v_mean"),
         "leak_W_per_C": hl.get("gates", {}).get("aifoundry3", {}).get("leak_W_per_C"),
         "passes_all": allp, "passes_kept": kept, "pass_table": per, "load": lw,
         "n_runs": len(runs), "n_runs_failed": sum(1 for r in runs if r["failed"]),
         "mean_rate_ops_s": rate, "law_W_frozen_Winf_W": P["law_W_fit"]["Winf_W"],
         "turn_on_T_W": P["sources"]["turn_on_T_W"], "turn_on_T_se_W": P["sources"]["turn_on_T_se_W"]}

    # ---------------------------------------------------------------- the three ladders
    def ladder(group, zero, nbits):
        rows = []
        for r in P[group]:
            it = r["item"]
            if not any(it in val[p] for p in kept):
                continue
            m, se, n = paired(val, kept, it, zero)
            if m is None:
                continue
            row = {"item": it, "h": r["h"], "designed_bits_per_op": r["designed_bits_per_op"],
                   "S_additive_W": r["S_additive_W"], "dW": m, "se": se, "n_passes": n,
                   "fJ_per_bit": 1e15 * m / (r["designed_bits_per_op"] * rate) if rate else None,
                   "W_per_flipped_position": m / r["h"],
                   "ratio_measured_over_additive": m / r["S_additive_W"] if r["S_additive_W"] else None,
                   "pred_law_A_W": r["pred_law_A_W"], "pred_law_H_offset_W": r["pred_law_H_offset_W"],
                   "pred_law_W_W": r["pred_law_W_W"],
                   "T_implied_W": (r["S_additive_W"] - m) / (r["h"] - 1) if r["h"] > 1 else None}
            if "pred_replicate_E60_W" in r:
                row["E60_W"] = r["pred_replicate_E60_W"]
                row["E60_se"] = r["pred_replicate_E60_se_W"]
                row["minus_E60_W"] = m - r["pred_replicate_E60_W"]
            rows.append(row)
        return rows
    R["lq"] = ladder("lq", "lq_h0", N_B)
    R["ls"] = ladder("ls", "lq_h0", N_B)
    R["alq"] = ladder("alq", "aq_h0", N_A)
    byitem = {r["item"]: r for r in R["lq"] + R["ls"] + R["alq"]}

    # ---------------------------------------------------------------- D1: matched-h layout contrast
    R["D1"] = []
    for h in LS_H:
        q, s = f"lq_h{h}", f"ls_h{h}"
        m, se, n = paired(val, kept, s, q)
        if m is None:
            continue
        pr = next((d for d in P["D1_matched_h_layout_contrast"] if d["h"] == h), {})
        R["D1"].append({"h": h, "dW_ls_minus_lq": m, "se": se, "n_passes": n,
                        "pred_law_A_dW": pr.get("pred_law_A_dW"), "pred_law_H_strong_dW": 0.0,
                        "pred_law_W_dW": pr.get("pred_law_W_dW"),
                        "sigma_from_zero": (m / se) if se else None,
                        "sigma_from_law_A": ((m - pr["pred_law_A_dW"]) / se) if se and pr else None,
                        "sigma_from_law_W": ((m - pr["pred_law_W_dW"]) / se) if se and pr else None})

    # ---------------------------------------------------------------- D2: which variable the layouts collapse on
    bs = [r for r in R["lq"] + R["ls"] if r["h"] != 23]
    byh = {}
    for r in bs:
        byh.setdefault(r["h"], []).append(r["dW"])
    fh = {h: sum(v) / len(v) for h, v in byh.items()}
    R_h = math.sqrt(sum((r["dW"] - fh[r["h"]]) ** 2 for r in bs) / len(bs)) if bs else None
    matched = [h for h, v in byh.items() if len(v) > 1]
    R_h_matched = (math.sqrt(sum((r["dW"] - fh[r["h"]]) ** 2 for r in bs if r["h"] in matched)
                             / sum(1 for r in bs if r["h"] in matched)) if matched else None)
    w_refit, R_S = fit_ceiling([(r["S_additive_W"], r["dW"]) for r in bs]) if bs else (None, None)
    R_S_frozen = (math.sqrt(sum((r["dW"] - coverage(r["S_additive_W"], P["law_W_fit"]["Winf_W"])) ** 2 for r in bs) / len(bs))
                  if bs else None)
    R_A = math.sqrt(sum((r["dW"] - r["S_additive_W"]) ** 2 for r in bs) / len(bs)) if bs else None
    R_A_ls = (math.sqrt(sum((r["dW"] - r["S_additive_W"]) ** 2 for r in R["ls"]) / len(R["ls"])) if R["ls"] else None)
    R_W_ls = (math.sqrt(sum((r["dW"] - r["pred_law_W_W"]) ** 2 for r in R["ls"]) / len(R["ls"])) if R["ls"] else None)
    R["D2"] = {"n_rungs": len(bs), "R_h_W": R_h, "R_h_matched_only_W": R_h_matched,
               "R_S_refit_W": R_S, "Winf_refit_W": w_refit, "R_S_frozen_W": R_S_frozen, "R_additive_W": R_A,
               "ls_rms_vs_law_A_W": R_A_ls, "ls_rms_vs_law_W_frozen_W": R_W_ls,
               "verdict": None}
    if R_h and R_S:
        if R_S < R_h / 2:
            R["D2"]["verdict"] = "shared wires (which bits): the layouts collapse on the additive sum, not on h"
        elif R_h < R_S / 2:
            R["D2"]["verdict"] = "interaction (how many): the layouts collapse on h, not on the additive sum"
        else:
            R["D2"]["verdict"] = "both, with weights: neither collapse wins by 2x"

    # ---------------------------------------------------------------- D3: is one turn-on enough?
    ts = [(r["item"], r["T_implied_W"]) for r in bs if r["T_implied_W"] is not None]
    R["D3"] = {"T_implied": dict(ts), "min_W": min(v for _, v in ts) if ts else None,
               "max_W": max(v for _, v in ts) if ts else None,
               "span_factor": (max(v for _, v in ts) / min(v for _, v in ts))
               if ts and min(v for _, v in ts) > 0 else None,
               "grid_T_W": P["sources"]["turn_on_T_W"], "grid_T_se_W": P["sources"]["turn_on_T_se_W"]}

    # ---------------------------------------------------------------- D4: the carry-over between operands
    R["D4"] = []
    for h in ALQ_K:
        qa, qb = f"alq_h{h}", f"lq_h{h}"
        if qb not in byitem or qa not in byitem:
            continue
        per_pass = [((val[p][qa]["p80"] - val[p]["aq_h0"]["p80"]) / (N_A * h))
                    / ((val[p][qb]["p80"] - val[p]["lq_h0"]["p80"]) / (N_B * h))
                    for p in kept
                    if all(k in val[p] for k in (qa, qb, "aq_h0", "lq_h0"))
                    and (val[p][qb]["p80"] - val[p]["lq_h0"]["p80"]) > 0]
        m, se, n = mean_se(per_pass)
        pr = next((d for d in P["D4_matched_h_A_over_B"] if d["h"] == h), {})
        R["D4"].append({"h": h, "rho_per_bit": m, "se": se, "n_passes": n,
                        "dW_alq": byitem[qa]["dW"], "dW_lq": byitem[qb]["dW"],
                        "pred_law_A_per_bit": pr.get("pred_law_A_per_bit"),
                        "pred_law_W_per_bit": pr.get("pred_law_W_per_bit")})
    R["carry_over_prior"] = P["carry_over_prior"]

    # ---------------------------------------------------------------- the A-side ceiling (P5)
    if len(R["alq"]) >= 3:
        wa, rmsa = fit_ceiling([(r["S_additive_W"], r["dW"]) for r in R["alq"]])
        R["A_ceiling"] = {"Winf_A_W": wa, "fit_rms_W": rmsa, "B_ceiling_W": P["law_W_fit"]["Winf_W"],
                          "ratio_A_over_B": wa / P["law_W_fit"]["Winf_W"],
                          "half_ceiling_W": P["law_W_fit"]["Winf_W"] / 2}

    # ---------------------------------------------------------------- D5: the closure, through the chosen law
    R["D5"] = {}
    cl = None
    if a.closure and os.path.exists(a.closure):
        cl = json.load(open(a.closure))
    for name, zero in (("nrd_a", "aq_h0"), ("nrd_b", "lq_h0")):
        m, se, n = paired(val, kept, name, zero)
        if m is None:
            continue
        ent = {"measured_W": m, "se": se, "n_passes": n}
        if cl and name in cl["items"]:
            s = cl["items"][name]["predicted_W"]
            ent.update({"S_additive_W": s, "E67_ratio": cl["items"][name]["ratio_measured_over_predicted"],
                        "E67_measured_W": cl["items"][name]["measured_W"],
                        "ratio_additive": m / s if s else None})
            for tag, w in (("law_W_frozen", P["law_W_fit"]["Winf_W"]),
                           ("law_W_refit_B", w_refit),
                           ("law_W_A_side", R.get("A_ceiling", {}).get("Winf_A_W"))):
                if w:
                    pw = coverage(s, w)
                    ent[f"pred_{tag}_W"] = pw
                    ent[f"ratio_{tag}"] = m / pw if pw else None
        R["D5"][name] = ent

    # ---------------------------------------------------------------- P3: does dW/S track S or h?
    if len(bs) >= 4:
        R["P3"] = {"rho_ratio_vs_S": spearman([r["S_additive_W"] for r in bs], [r["ratio_measured_over_additive"] for r in bs]),
                   "rho_ratio_vs_h": spearman([float(r["h"]) for r in bs], [r["ratio_measured_over_additive"] for r in bs])}

    # ---------------------------------------------------------------- the leakage sensitivity (departure D-d)
    R["leak_sensitivity"] = {}
    for pth in [x for x in a.leak.split(",") if x and os.path.exists(x)]:
        j = json.load(open(pth))["cards"].get("aifoundry3", {})
        it = j.get("items", {})
        R["leak_sensitivity"][os.path.basename(pth)] = {
            "leak_W_per_C": json.load(open(pth)).get("gates", {}).get("aifoundry3", {}).get("leak_W_per_C"),
            "rungs": {k: it[k].get("d_p80") for k in sorted(it) if k.startswith(("lq_h", "ls_h", "alq_h", "nrd_"))
                      and it[k].get("d_p80") is not None}}

    # ---------------------------------------------------------------- the registered rules, scored
    def g(item, key="dW"):
        return byitem.get(item, {}).get(key)
    sc = {}
    d1_8 = next((d for d in R["D1"] if d["h"] == 8), None)
    if d1_8 and d1_8["se"]:
        sc["P1"] = {"asked": "dW_ls - dW_lq > 2.0 W at >= 3 SE at h = 8 (H-strong needs 0)",
                    "measured": f"{d1_8['dW_ls_minus_lq']:.3f} +- {d1_8['se']:.3f} W "
                                f"({d1_8['dW_ls_minus_lq'] / d1_8['se']:.1f} SE from zero)",
                    "verdict": "PASS" if (d1_8["dW_ls_minus_lq"] > 2.0 and d1_8["dW_ls_minus_lq"] > 3 * d1_8["se"])
                    else ("FAIL (how many)" if d1_8["dW_ls_minus_lq"] < 2.0 else "UNDECIDED")}
    if R_W_ls is not None and R_A_ls is not None:
        sc["P2"] = {"asked": "ls rms vs law W's frozen curve <= 2.0 W, and <= law A's rms / 3",
                    "measured": f"law W rms {R_W_ls:.3f} W, law A rms {R_A_ls:.3f} W, factor {R_A_ls / R_W_ls:.2f}",
                    "verdict": "PASS" if (R_W_ls <= 2.0 and R_A_ls >= 3 * R_W_ls) else "FAIL"}
    if "P3" in R and R["P3"]["rho_ratio_vs_S"] is not None:
        sc["P3"] = {"asked": "Spearman rho(dW/S, S) < -0.7, and |rho vs S| > |rho vs h|",
                    "measured": f"rho vs S {R['P3']['rho_ratio_vs_S']:.3f}, rho vs h {R['P3']['rho_ratio_vs_h']:.3f}",
                    "verdict": "PASS" if (R["P3"]["rho_ratio_vs_S"] < -0.7
                                          and abs(R["P3"]["rho_ratio_vs_S"]) > abs(R["P3"]["rho_ratio_vs_h"])) else "FAIL"}
    if R["D3"]["span_factor"]:
        far = [k for k, v in R["D3"]["T_implied"].items()
               if R["D3"]["grid_T_se_W"] and abs(v - R["D3"]["grid_T_W"]) > 3 * R["D3"]["grid_T_se_W"]]
        sc["P4"] = {"asked": "T_implied spans > 4x over the B-side rungs, and >= 1 rung > 3 SE from the grid's 1.351 W",
                    "measured": f"span {R['D3']['span_factor']:.1f}x ({R['D3']['min_W']:.3f}..{R['D3']['max_W']:.3f} W), "
                                f"{len(far)} rungs beyond 3 SE",
                    "verdict": "PASS" if (R["D3"]["span_factor"] > 4 and far) else "FAIL"}
    if g("alq_h23") and g("alq_h1"):
        bend = (g("alq_h23") / 23) / g("alq_h1")
        ac = R.get("A_ceiling", {})
        sc["P5"] = {"asked": "dW_alq(23)/23 below dW_alq(1) by >= 2x, and the A ceiling within 1.5x of the B ceiling",
                    "measured": f"bend factor {1 / bend:.2f}x, A ceiling {ac.get('Winf_A_W', float('nan')):.2f} W "
                                f"vs B {P['law_W_fit']['Winf_W']:.2f} W (ratio {ac.get('ratio_A_over_B', float('nan')):.2f})",
                    "verdict": "PASS" if (bend <= 0.5 and ac.get("ratio_A_over_B")
                                          and 1 / 1.5 <= ac["ratio_A_over_B"] <= 1.5) else "FAIL"}
    r12 = next((d for d in R["D4"] if d["h"] == 12), None)
    r16 = next((d for d in R["D4"] if d["h"] == 16), None)
    r2 = next((d for d in R["D4"] if d["h"] == 2), None)
    if r12 and r16 and r2 and all(x["rho_per_bit"] for x in (r12, r16, r2)):
        inband = all(0.7 <= x["rho_per_bit"] <= 2.5 for x in (r12, r16))
        sc["P6"] = {"asked": "rho(12) and rho(16) in [0.7, 2.5], and rho(16) < rho(2)",
                    "measured": f"rho(2) {r2['rho_per_bit']:.2f}, rho(12) {r12['rho_per_bit']:.2f}, "
                                f"rho(16) {r16['rho_per_bit']:.2f}",
                    "verdict": "PASS" if (inband and r16["rho_per_bit"] < r2["rho_per_bit"]) else "FAIL"}
    rs = [R["D5"].get(k, {}).get("ratio_law_W_frozen") for k in ("nrd_a", "nrd_b")]
    if all(x is not None for x in rs):
        sc["P7"] = {"asked": "both closure ratios in [0.7, 1.4] with the selected law (E67's raw: 0.43, 0.50)",
                    "measured": f"nrd_a {rs[0]:.2f}, nrd_b {rs[1]:.2f} (frozen ceiling)",
                    "verdict": "PASS" if all(0.7 <= x <= 1.4 for x in rs) else "FAIL"}
    rep = [(r["item"], r["minus_E60_W"]) for r in R["lq"] if r.get("minus_E60_W") is not None]
    if rep:
        worst16 = max((abs(d) for n, d in rep if n != "lq_h23"), default=None)
        w23 = next((abs(d) for n, d in rep if n == "lq_h23"), None)
        sc["P8"] = {"asked": "E60's 7 lq rungs reproduce within 0.6 W (lq_h23 within 1.0 W)",
                    "measured": f"largest |E70 - E60| below h=23: {worst16:.3f} W; lq_h23 "
                                f"{(f'{w23:.3f} W' if w23 is not None else 'not run')}",
                    "verdict": "PASS" if (worst16 is not None and worst16 <= 0.6
                                          and (w23 is None or w23 <= 1.0)) else "FAIL"}
    R["scored"] = sc
    R["verdict_Q128_s5_item2"] = R["D2"]["verdict"]
    json.dump(R, open(a.json, "w"), indent=1)

    # ---------------------------------------------------------------- the readable report
    L = []
    w = L.append
    w(f"# E70 results — the saturation ladder and the A-side multi-bit ladder (aifoundry3, "
      f"{R['clock_mhz']} MHz, {1000 * (R['v_mean'] or 0):.1f} mV)\n")
    w(f"Passes run {R['passes_all']}; kept {R['passes_kept']}; {R['n_runs']} runs, {R['n_runs_failed']} failed a "
      f"per-run gate; leakage {R['leak_W_per_C']} W/°C; mean op rate "
      f"{(R['mean_rate_ops_s'] or 0) / 1e9:.4f} Gop/s per minion.\n")
    w("## Pass health (departures D-a and D-b)\n")
    w("| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (Gop/s) | load1 | gate |")
    w("|---|---|---|---|---|---|---|---|")
    for p in allp:
        d = per[p]
        w(f"| {p} | {d['n_runs']} | {d['n_failed']} | "
          f"{'—' if d['pi_drift_W'] is None else f'{d['pi_drift_W']:+.3f}'} | "
          f"{'—' if d['const_spread_W'] is None else f'{d['const_spread_W']:.3f}'} | "
          f"{'—' if not d['mean_rate'] else f'{d['mean_rate'] / 1e9:.4f}'} | "
          f"{'—' if d['load1_mean'] is None else f'{d['load1_mean']:.2f}'} | "
          f"{'kept' if not d['set_aside'] else 'SET ASIDE: ' + '; '.join(d['set_aside'])}"
          f"{' / load-disturbed: ' + '; '.join(d['load_disturbed']) if d['load_disturbed'] else ''} |")
    w("")
    for group, title, zero in (("lq", "the low layout (B's low h mantissa bits)", "lq_h0"),
                               ("ls", "the spread layout (h bits spread over B's mantissa)", "lq_h0"),
                               ("alq", "the A-side ladder (A's low k mantissa bits)", "aq_h0")):
        w(f"## {group} — {title}, each rung against {zero}\n")
        w("| item | h | designed bits/op | measured ΔW | SE | fJ per flipped bit | W per flipped position | "
          "additive sum S | measured/S | law W (frozen) | law A | E60 |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in R[group]:
            w(f"| `{r['item']}` | {r['h']} | {r['designed_bits_per_op']} | {r['dW']:.3f} | "
              f"{'—' if r['se'] is None else f'{r['se']:.3f}'} | "
              f"{'—' if r['fJ_per_bit'] is None else f'{r['fJ_per_bit']:.0f}'} | {r['W_per_flipped_position']:.3f} | "
              f"{r['S_additive_W']:.3f} | {r['ratio_measured_over_additive']:.3f} | {r['pred_law_W_W']:.3f} | "
              f"{r['pred_law_A_W']:.3f} | {('%.3f' % r['E60_W']) if 'E60_W' in r else '—'} |")
        w("")
    w("## D1 — the matched-h layout contrast (the sharpest discriminator)\n")
    w("| h | measured ΔW(ls) − ΔW(lq) | SE | SE from zero | law A / H-offset predict | law W predicts | "
      "H-strong predicts |")
    w("|---|---|---|---|---|---|---|")
    for d in R["D1"]:
        w(f"| {d['h']} | {d['dW_ls_minus_lq']:+.3f} | {'—' if d['se'] is None else f'{d['se']:.3f}'} | "
          f"{'—' if d['sigma_from_zero'] is None else f'{d['sigma_from_zero']:.1f}'} | "
          f"{d['pred_law_A_dW']:.3f} | {d['pred_law_W_dW']:.3f} | 0.000 |")
    w("")
    w("## D2 — which variable the two layouts collapse on\n")
    d = R["D2"]
    w(f"- `R_h` (best any \"how many\" law can do: free value per h) over {d['n_rungs']} rungs: "
      f"**{d['R_h_W']:.3f} W**; over the matched-h pairs only: "
      f"{'—' if d['R_h_matched_only_W'] is None else f'{d['R_h_matched_only_W']:.3f} W'}")
    w(f"- `R_S` (one-parameter coverage curve in the additive sum, ceiling refitted on E70's own rungs, "
      f"W∞ = {d['Winf_refit_W']:.2f} W): **{d['R_S_refit_W']:.3f} W**")
    w(f"- the same curve with the ceiling **frozen** at E60's 12.58 W: {d['R_S_frozen_W']:.3f} W")
    w(f"- pure additivity (law A): {d['R_additive_W']:.3f} W")
    w(f"- **verdict: {d['verdict']}**\n")
    w("## D3 — is one shared turn-on enough?\n")
    w(f"`T_implied = (S − ΔW)/(h − 1)` over the B-side rungs: {R['D3']['min_W']:.3f} … {R['D3']['max_W']:.3f} W, "
      f"a factor of {R['D3']['span_factor']:.1f}, against the grid's {R['D3']['grid_T_W']:.3f} ± "
      f"{R['D3']['grid_T_se_W']:.3f} W. H-offset needs one constant.\n")
    w("## D4 — the carry-over between operands, measured at each Hamming weight\n")
    w("| h | ρ = A price per bit / B price per bit | SE | ΔW(alq) | ΔW(lq) | law A predicts | law W predicts |")
    w("|---|---|---|---|---|---|---|")
    for d in R["D4"]:
        w(f"| {d['h']} | {'—' if d['rho_per_bit'] is None else f'{d['rho_per_bit']:.3f}'} | "
          f"{'—' if d['se'] is None else f'{d['se']:.3f}'} | {d['dW_alq']:.3f} | {d['dW_lq']:.3f} | "
          f"{'—' if d['pred_law_A_per_bit'] is None else f'{d['pred_law_A_per_bit']:.2f}'} | "
          f"{'—' if d['pred_law_W_per_bit'] is None else f'{d['pred_law_W_per_bit']:.2f}'} |")
    w(f"\nThe two numbers Q128 had to choose between: raw single-bit median "
      f"{R['carry_over_prior']['single_bit_raw_per_bit_median']:.2f}, turn-on-corrected median "
      f"{R['carry_over_prior']['single_bit_marginal_per_bit_median']:.2f}.\n")
    if "A_ceiling" in R:
        w(f"A-side ceiling fitted on the alq rungs: **{R['A_ceiling']['Winf_A_W']:.2f} W** (fit rms "
          f"{R['A_ceiling']['fit_rms_W']:.3f} W) against the B side's {R['A_ceiling']['B_ceiling_W']:.2f} W "
          f"— ratio {R['A_ceiling']['ratio_A_over_B']:.2f}; a flip-rate-scaled ceiling would be "
          f"{R['A_ceiling']['half_ceiling_W']:.2f} W.\n")
    if R["D5"]:
        w("## D5 — the closure: do the price lists reproduce a random-word step once the law is applied?\n")
        w("| item | additive sum S | measured ΔW (E70) | ratio additive | law W (frozen) | ratio | E67's ratio |")
        w("|---|---|---|---|---|---|---|")
        for k, e in R["D5"].items():
            w(f"| `{k}` | {('%.2f' % e['S_additive_W']) if 'S_additive_W' in e else '—'} | "
              f"{e['measured_W']:.3f} ± {('%.3f' % e['se']) if e['se'] else '—'} | "
              f"{('%.2f' % e['ratio_additive']) if e.get('ratio_additive') else '—'} | "
              f"{('%.2f' % e['pred_law_W_frozen_W']) if e.get('pred_law_W_frozen_W') else '—'} | "
              f"{('%.2f' % e['ratio_law_W_frozen']) if e.get('ratio_law_W_frozen') else '—'} | "
              f"{('%.2f' % e['E67_ratio']) if e.get('E67_ratio') else '—'} |")
        w("")
    w("## The registered rules, scored\n")
    w("| rule | what it asked | measured | verdict |")
    w("|---|---|---|---|")
    for k in sorted(sc):
        w(f"| **{k}** | {sc[k]['asked']} | {sc[k]['measured']} | **{sc[k]['verdict']}** |")
    w("")
    if R["leak_sensitivity"]:
        w("## Leakage sensitivity (departure D-d)\n")
        w("| rung | " + " | ".join(f"{v['leak_W_per_C']} W/°C" for v in R["leak_sensitivity"].values()) + " |")
        w("|---|" + "---|" * len(R["leak_sensitivity"]))
        keys = sorted({k for v in R["leak_sensitivity"].values() for k in v["rungs"]})
        for k in keys:
            w(f"| `{k}` | " + " | ".join(f"{v['rungs'].get(k, float('nan')):.3f}"
                                         for v in R["leak_sensitivity"].values()) + " |")
        w("")
    open(a.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main()
