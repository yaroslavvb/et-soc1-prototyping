#!/usr/bin/env python3
"""E92 scorer (Q132): every registered rule of tools/claims-v3/kinds/E92.md, thresholds and frozen numbers read from
predictions-e92.json, on reduce_e92.py's output (E78's reduction, unchanged, with E92's items). Standard library only.
It changes no rule.

    python3 tools/claims-v3/kinds/score_e92.py --e92 e92.json [--e92-arm leak0.1994=e92-leak0.1994.json ...]
        --json scored.json --md results.md [--label <arm name>]

It refuses to score if a frozen input differs from the sha256 predictions-e92.json records. The unit of replication
is the pass; fewer than 3 kept passes make every rule NOT SCORED in this input (E92.md: the dips-removed arm is then
the registered reading). Every contrast is paired per pass. A verdict that moves between leakage arms (NOT SCORED
aside) is marked slope-sensitive. CONFIRMED / REFUTED / INCONCLUSIVE per contrast; a rule's combined verdict is
REFUTED if any contrast is, CONFIRMED if all are, else INCONCLUSIVE.
"""
import argparse
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MIN_PASSES = 3
LO_FRACTION, HI_FACTOR, LO_REFUTE, HI_REFUTE = 0.5, 2.0, 0.25, 4.0


def mean_ci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "values": []}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "values": v}
    se = statistics.stdev(v) / math.sqrt(len(v))
    return {"mean": m, "se": se, "n": len(v), "ci95": se * T95.get(len(v) - 1, 1.96), "values": [round(x, 4) for x in v]}


def bounds(mc):
    return mc["mean"] - mc["ci95"], mc["mean"] + mc["ci95"]


def scored(mc):
    return mc["n"] >= MIN_PASSES and mc["ci95"] is not None


def v_threshold(mc, thr):
    if not scored(mc):
        return "NOT SCORED"
    lo, hi = bounds(mc)
    return "CONFIRMED" if hi <= thr else ("REFUTED" if lo > thr else "INCONCLUSIVE")


def v_factor(mc, pred):
    if not scored(mc):
        return "NOT SCORED"
    lo, hi = bounds(mc)
    if lo >= LO_FRACTION * pred and hi <= HI_FACTOR * pred:
        return "CONFIRMED"
    if hi < LO_REFUTE * pred or lo > HI_REFUTE * pred:
        return "REFUTED"
    return "INCONCLUSIVE"


def v_band(mc, band):
    if not scored(mc):
        return "NOT SCORED"
    lo, hi = bounds(mc)
    if -band <= lo and hi <= band:
        return "CONFIRMED"
    if lo > band or hi < -band:
        return "REFUTED"
    return "INCONCLUSIVE"


def v_direction(mc, pred):
    if not scored(mc):
        return "NOT SCORED"
    lo, hi = bounds(mc)
    return "CONFIRMED" if lo >= LO_FRACTION * pred else ("REFUTED" if hi < 0 else "INCONCLUSIVE")


def combine(vs):
    vs = list(vs)
    if any(v == "REFUTED" for v in vs):
        return "REFUTED"
    if any(v == "NOT SCORED" for v in vs):
        return "NOT SCORED"
    return "CONFIRMED" if all(v == "CONFIRMED" for v in vs) else "INCONCLUSIVE"


def per_pass(res, passes, name, key="D"):
    out = {}
    for p in passes:
        e = res["per_pass"].get(str(p), {}).get(name)
        if e is not None and e.get(key) is not None:
            out[p] = e[key]
    return out


def diff(res, passes, hi, lo, key="D"):
    a, b = per_pass(res, passes, hi, key), per_pass(res, passes, lo, key)
    return {p: a[p] - b[p] for p in passes if p in a and p in b}


def combo(terms):
    """A per-pass linear combination [(coefficient, {pass: value}), ...]; a constant goes in as (c, None)."""
    keys = None
    for c, d in terms:
        if d is not None:
            keys = set(d) if keys is None else keys & set(d)
    out = {}
    for p in sorted(keys or []):
        v = 0.0
        for c, d in terms:
            v += c if d is None else c * d[p]
        out[p] = v
    return out


def item_mean(res, name, key="D"):
    it = res["items"].get(name) or {}
    v = it.get(key)
    return v.get("mean") if isinstance(v, dict) else v


def score(res, reg):
    passes = res.get("passes", [])
    enough = len(passes) >= MIN_PASSES
    C = reg["contrasts"]
    M = reg["models"]
    T = reg["tiles"]
    out = {"passes": passes, "enough_passes": enough, "contrasts": {}, "statistics": {}, "factorial": {}, "budget": {},
           "ladder": {}, "rules": {}, "tiles": {}}
    d = {}
    for k, c in C.items():
        d[k] = diff(res, passes, c["hi"], c["lo"])
        mc = mean_ci(list(d[k].values()))
        ms = mean_ci(list(diff(res, passes, c["hi"], c["lo"], "S").values()))
        rule = c.get("rule")
        v = None
        if rule == "E92-R1":
            v = v_threshold(mc, c["threshold_w"])
        elif rule in ("E92-R2", "E92-R8"):
            v = v_factor(mc, c["pred_w"])
        elif rule in ("E92-R3", "E92-R9"):
            v = v_band(mc, c["band_w"])
        elif rule == "E92-R10":
            v = v_direction(mc, c["pred_w"])
        e88 = c["e88"]
        out["contrasts"][k] = {"rule": rule, "what": c["what"], "hi": c["hi"], "lo": c["lo"], "D_w": mc, "S_w": ms, "verdict": v,
                               "bits_w": c["bits_w"], "alt_w": c["alt_w"], "e88_mu_w": e88["mu"], "e88_band_w": [e88["lo"], e88["hi"]],
                               "e88_inside": bool(mc["mean"] is not None and e88["lo"] <= mc["mean"] <= e88["hi"]),
                               "e88_flops_w": c["e88_flops_w"], "pred_w": c.get("pred_w"), "threshold_w": c.get("threshold_w"),
                               "band_w": c.get("band_w"), "e90_linear_w": c.get("e90_linear_w"), "dN_alt": c["dN_alt"], "dflops": c["dflops"]}
    R = out["rules"]
    for rule in ("E92-R1", "E92-R2", "E92-R3", "E92-R8", "E92-R9", "E92-R10"):
        names = reg["rules"][rule]["contrasts"]
        vs = {n: out["contrasts"][n]["verdict"] for n in names}
        R[rule] = {"verdict": "NOT SCORED" if not enough else combine(vs.values()), "contrasts": vs}

    def h(ty, a, b):
        return d[f"{ty}.{a}-{b}"]

    def stat(name, rule, terms, band):
        mc = mean_ci(list(combo(terms).values()))
        v = v_band(mc, band)
        out["statistics"][name] = {"rule": rule, "value_w": mc, "band_w": band, "verdict": v}
        return v

    NA = lambda n: T[n]["sign"]["N_alt1"] + T[n]["sign"]["N_alt2"]    # noqa: E731
    lb = M["linear_band_w"]
    # R4: the A-side twin
    ratio = NA("fp32.i_sub") / NA("fp32.h_sub")
    v4 = stat("i_sub-i_add minus ratio x (h_sub-h_add)", "E92-R4",
              [(1.0, h("fp32", "i_sub", "i_add")), (-ratio, h("fp32", "h_sub", "h_add"))], lb["fp32"])
    R["E92-R4"] = {"verdict": "NOT SCORED" if not enough else v4, "ratio": ratio}
    # R5: the ladder
    vs5 = {}
    for m in (2, 4, 6):
        vs5[f"h_sub{m}"] = stat(f"h_sub{m}-c_abs minus {m}/8 x (h_sub-c_abs)", "E92-R5",
                                [(1.0, h("fp32", f"h_sub{m}", "c_abs")), (-m / 8.0, h("fp32", "h_sub", "c_abs"))], lb["fp32"])
    R["E92-R5"] = {"verdict": "NOT SCORED" if not enough else combine(vs5.values()), "rungs": vs5}
    # R6: random signs against structured signs, beyond their bits
    vs6 = {}
    for ty in ("fp32", "fp16"):
        r = NA(f"{ty}.s_abs") / NA(f"{ty}.h_sub")
        b_s, b_h = C[f"{ty}.s_abs-c_abs"]["bits_w"], C[f"{ty}.h_sub-c_abs"]["bits_w"] if f"{ty}.h_sub-c_abs" in C else None
        vs6[ty] = stat(f"{ty}: (s_abs-c_abs-bits) minus {r:.4f} x (h_sub-c_abs-bits)", "E92-R6",
                       [(1.0, h(ty, "s_abs", "c_abs")), (-b_s, None), (-r, h(ty, "h_sub", "c_abs")), (r * b_h, None)], lb[ty])
    R["E92-R6"] = {"verdict": "NOT SCORED" if not enough else combine(vs6.values()), "formats": vs6}
    # R7: magnitudes, absorbed
    v7 = stat("(r_h_sub-r_h_add) minus (h_sub-h_add)", "E92-R7",
              [(1.0, h("fp32", "r_h_sub", "r_h_add")), (-1.0, h("fp32", "h_sub", "h_add"))], lb["fp32"])
    R["E92-R7"] = {"verdict": "NOT SCORED" if not enough else v7}
    # ---- the factorial (reported): a sign path alpha (B and product signs), a sum-sign path beta (C read and result signs),
    # the add/subtract switch gamma, a steady subtract delta; c_abs is the origin
    #   h_add = alpha + beta; c_alt = beta + gamma + delta/2; h_sub = alpha + gamma + delta/2; h_allsub = alpha + beta + delta
    for ty in ("fp32", "fp16"):
        dl = h(ty, "h_allsub", "h_add")
        terms_g = [(0.5, h(ty, "c_alt", "c_abs")), (0.5, h(ty, "h_sub", "h_add")), (-0.5, dl)]
        g = combo(terms_g)
        beta = combo([(1.0, h(ty, "c_alt", "c_abs")), (-1.0, g), (-0.5, dl)])
        alpha = combo([(1.0, diff(res, passes, f"{ty}.h_add", f"{ty}.c_abs")), (-1.0, beta)])
        rate = item_mean(res, f"{ty}.h_sub", "rate")
        mg = mean_ci(list(g.values()))
        n_lane_alt = T[f"{ty}.h_sub"]["sign"]["N_alt1"]
        out["factorial"][ty] = {"gamma_w": mg, "alpha_w": mean_ci(list(alpha.values())), "beta_w": mean_ci(list(beta.values())),
                                "delta_w": mean_ci(list(dl.values())), "rate_ops_per_s": rate,
                                "gamma_fj_per_lane_alternation": (1e15 * mg["mean"] / (n_lane_alt * rate)) if (rate and mg["mean"] is not None) else None,
                                "n_lane_alternations_per_op": n_lane_alt}
        # ---- where the signs' cost goes (reported)
        tot = h(ty, "signs", "ones")
        froz = h(ty, "s_abs", "c_abs")
        bits_s = C[f"{ty}.signs-ones"]["bits_w"]
        r_alt = (T[f"{ty}.signs"]["sign"]["N_alt1"] + T[f"{ty}.signs"]["sign"]["N_alt2"]) / NA(f"{ty}.h_sub")
        r_alt_s = NA(f"{ty}.s_abs") / NA(f"{ty}.h_sub")
        out["budget"][ty] = {"signs_minus_ones_w": mean_ci(list(tot.values())), "frozen_s_abs_minus_c_abs_w": mean_ci(list(froz.values())),
                             "moving_sum_part_w": mean_ci(list(combo([(1.0, tot), (-1.0, froz)]).values())),
                             "frozen_share": mean_ci([froz[p] / tot[p] for p in froz if p in tot and tot[p]]),
                             "bits_w": bits_s, "bits_s_abs_w": C[f"{ty}.s_abs-c_abs"]["bits_w"],
                             "alternation_at_signs_rate_w": mean_ci([g[p] * r_alt for p in g]),
                             "alternation_at_s_abs_rate_w": mean_ci([g[p] * r_alt_s for p in g]),
                             "frozen_left_after_bits_and_alternation_w": mean_ci(list(combo([(1.0, froz), (-C[f"{ty}.s_abs-c_abs"]["bits_w"], None), (-r_alt_s, g)]).values())),
                             "alt_ratio_signs": r_alt, "alt_ratio_s_abs": r_alt_s}
    # ---- the ladder as a slope (reported)
    x = {2: h("fp32", "h_sub2", "c_abs"), 4: h("fp32", "h_sub4", "c_abs"), 6: h("fp32", "h_sub6", "c_abs"), 8: h("fp32", "h_sub", "c_abs")}
    slopes = {}
    for p in passes:
        pts = [(m, x[m][p]) for m in x if p in x[m]]
        if len(pts) == 4:
            mb = statistics.fmean(a for a, _ in pts)
            yb = statistics.fmean(b for _, b in pts)
            slopes[p] = {"slope": sum((a - mb) * (b - yb) for a, b in pts) / sum((a - mb) ** 2 for a, _ in pts),
                         "icpt": yb - mb * sum((a - mb) * (b - yb) for a, b in pts) / sum((a - mb) ** 2 for a, _ in pts)}
    rate = item_mean(res, "fp32.h_sub", "rate")
    ms = mean_ci([v["slope"] for v in slopes.values()])
    out["ladder"] = {"slope_w_per_lane": ms, "intercept_w": mean_ci([v["icpt"] for v in slopes.values()]),
                     "means_w": {str(m): mean_ci(list(x[m].values())) for m in x},
                     "fj_per_alternation": (1e15 * ms["mean"] / (480 * rate)) if (rate and ms["mean"] is not None) else None}
    # ---- S1, S2, S3
    s1 = {}
    for c, b in reg["rules"]["E92-S1"]["cells"].items():
        m = item_mean(res, c)
        e7, e9 = reg["e78_reference"][c]["D_w"], reg["e90_reference"][c]["D_w"]
        s1[c] = {"D_w": m, "e78_D_w": e7, "e90_D_w": e9, "diff_e78_w": None if m is None else m - e7, "diff_e90_w": None if m is None else m - e9,
                 "band_w": b, "inside": bool(m is not None and abs(m - e7) <= b and abs(m - e9) <= b)}
    for c, b in reg["rules"]["E92-S1"]["cells_e90_only"].items():
        m = item_mean(res, c)
        e9 = reg["e90_reference"][c]["D_w"]
        s1[c] = {"D_w": m, "e90_D_w": e9, "diff_e90_w": None if m is None else m - e9, "band_w": b, "inside": bool(m is not None and abs(m - e9) <= b)}
    R["E92-S1"] = {"verdict": "NOT SCORED" if not enough else ("PASS" if all(x_["inside"] for x_ in s1.values()) else "FAIL"), "cells": s1}
    inside, rows = 0, {}
    for name, t in T.items():
        m = item_mean(res, name)
        lo, hi = t["q130n_predictor"]["pi95_w"]
        ok = m is not None and lo <= m <= hi
        inside += int(ok)
        rows[name] = {"D_w": m, "q130n_point_w": t["q130n_predictor"]["point_w"], "pi95_w": [lo, hi], "inside": ok, "D_pred_w": t["D_pred_w"]}
    errs = [out["contrasts"][k]["D_w"]["mean"] - C[k]["e88_flops_w"] for k in C if C[k].get("rule") and out["contrasts"][k]["D_w"]["mean"] is not None]
    errs88 = [out["contrasts"][k]["D_w"]["mean"] - C[k]["e88"]["mu"] for k in C if C[k].get("rule") and out["contrasts"][k]["D_w"]["mean"] is not None]
    R["E92-S2"] = {"q130n_inside": inside, "q130n_of": len(rows), "tiles": rows,
                   "e88_flops_rms_w": math.sqrt(statistics.fmean(e * e for e in errs)) if errs else None,
                   "e88_rms_w": math.sqrt(statistics.fmean(e * e for e in errs88)) if errs88 else None,
                   "e88_inside": sum(1 for k in C if C[k].get("rule") and out["contrasts"][k]["e88_inside"]),
                   "e88_of": sum(1 for k in C if C[k].get("rule"))}
    scale = M["card_scale"]["fp32"]
    sab = out["contrasts"]["fp32.s_abs-c_abs"]["D_w"]["mean"]
    f32 = item_mean(res, "fp32.c_abs")
    e88r = reg["e88_reference"]
    R["E92-S3"] = {"s_abs_minus_c_abs_w": sab, "e88_scaled_w": scale * e88r["M32s_w"], "inside_s_abs": bool(sab is not None and abs(sab - scale * e88r["M32s_w"]) <= 0.75),
                   "c_abs_w": f32, "e88_F32_scaled_w": scale * e88r["F32_w"], "inside_c_abs": bool(f32 is not None and abs(f32 - scale * e88r["F32_w"]) <= 1.0)}
    for name in list(T) + ["fp32.ones", "fp16.ones", "fp32.randn", "fp16.randn", "int8.full", "anchor_pi", "fp32.zeros", "fp16.zeros", "int8.zeros"]:
        it = res["items"].get(name)
        if it is None:
            continue
        out["tiles"][name] = {k: it.get(k) for k in ("D", "S", "D32", "Drail", "dT_win", "pj_op_S", "pj_op_D", "pj_mac_S", "pj_mac_D", "rate", "duty", "gated_lane_frac", "bus_bits_per_op")}
        out["tiles"][name]["D_pred_w"] = (T.get(name) or {}).get("D_pred_w")
    return out


def fmt(mc, nd=3):
    if not mc or mc.get("mean") is None:
        return "n/a"
    if mc.get("ci95") is None:
        return f"{mc['mean']:.{nd}f}"
    return f"{mc['mean']:.{nd}f} ± {mc['ci95']:.{nd}f}"


def write_md(sc, arms, path, label):
    L = [f"# E92 scored ({label})", "", f"Kept passes: {sc['passes']} ({'enough' if sc['enough_passes'] else 'FEWER THAN 3: NOT SCORED'}).", "",
         "## Rules", "", "| rule | verdict | " + " | ".join(arms) + " | slope-sensitive |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in sc["rules"].items():
        if "verdict" not in v:
            continue
        av = [arms[a]["rules"].get(r, {}).get("verdict", "n/a") for a in arms]
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(av) + f" | {v.get('slope_sensitive', False)} |")
    L += ["", "## Contrasts (paired per pass, board W over the type's zeros)", "",
          "| contrast | rule | measured D | measured S | bits | alt | e88 [band] | e88+flops | pred / thr / band | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, c in sc["contrasts"].items():
        p = c["pred_w"] if c["pred_w"] is not None else (c["threshold_w"] if c["threshold_w"] is not None else (f"±{c['band_w']}" if c["band_w"] else ""))
        L.append(f"| `{k}` | {c['rule'] or ''} | {fmt(c['D_w'])} | {fmt(c['S_w'])} | {c['bits_w']:.3f} | {c['alt_w']:.3f} | {c['e88_mu_w']:.3f} "
                 f"[{c['e88_band_w'][0]:.2f}, {c['e88_band_w'][1]:.2f}] | {c['e88_flops_w']:.3f} | {p} | {c['verdict'] or ''} |")
    L += ["", "## Paired statistics", "", "| statistic | rule | value (W) | band | verdict |", "|---|---|---|---|---|"]
    for k, s in sc["statistics"].items():
        L.append(f"| {k} | {s['rule']} | {fmt(s['value_w'])} | ±{s['band_w']} | {s['verdict']} |")
    L += ["", "## The factorial (reported)", "", "| format | gamma: the add/subtract switch (W) | fJ per lane alternation | alpha: B and product signs (W) | beta: C and result signs (W) | delta: a steady subtract (W) |", "|---|---|---|---|---|---|"]
    for ty, f in sc["factorial"].items():
        fj = f"{f['gamma_fj_per_lane_alternation']:.0f}" if f["gamma_fj_per_lane_alternation"] is not None else "n/a"
        L.append(f"| {ty} | {fmt(f['gamma_w'])} | {fj} | {fmt(f['alpha_w'])} | {fmt(f['beta_w'])} | {fmt(f['delta_w'])} |")
    L += ["", "## Where the signs' cost goes (reported)", "", "| format | signs − ones (W) | frozen s_abs − c_abs (W) | moving-sum part (W) | frozen share | bits of signs (W) | alternation at signs' rate (W) | frozen left after bits and alternation (W) |", "|---|---|---|---|---|---|---|---|"]
    for ty, b in sc["budget"].items():
        L.append(f"| {ty} | {fmt(b['signs_minus_ones_w'])} | {fmt(b['frozen_s_abs_minus_c_abs_w'])} | {fmt(b['moving_sum_part_w'])} | {fmt(b['frozen_share'])} | {b['bits_w']:.3f} | {fmt(b['alternation_at_signs_rate_w'])} | {fmt(b['frozen_left_after_bits_and_alternation_w'])} |")
    la = sc["ladder"]
    L += ["", "## The ladder (reported)", "", f"Slope {fmt(la['slope_w_per_lane'])} W per lane, intercept {fmt(la['intercept_w'])} W, "
          + (f"{la['fj_per_alternation']:.0f} fJ per alternation." if la["fj_per_alternation"] is not None else "")]
    L += ["", "## Every tile", "", "| item | D (W) | S (W) | pJ/MAC (S) | dT (C) | D_pred | Q130(n) [95%] |", "|---|---|---|---|---|---|---|"]
    q = sc["rules"]["E92-S2"]["tiles"]
    for n, t in sc["tiles"].items():
        pj = t.get("pj_mac_S")
        pjs = fmt(pj, 4) if isinstance(pj, dict) else "n/a"
        dt = t.get("dT_win")
        dts = fmt(dt, 2) if isinstance(dt, dict) else "n/a"
        pr = t.get("D_pred_w")
        qq = q.get(n)
        qs = f"{qq['q130n_point_w']:.2f} [{qq['pi95_w'][0]:.2f}, {qq['pi95_w'][1]:.2f}]" if qq else ""
        L.append(f"| `{n}` | {fmt(t.get('D'))} | {fmt(t.get('S'))} | {pjs} | {dts} | {pr if pr is not None else ''} | {qs} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e92", required=True)
    ap.add_argument("--e92-arm", action="append", default=[])
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--label", default="primary: leakage slope auto")
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e92.json")))
    bad = []
    for key, f in reg["inputs_frozen"].items():
        have = hashlib.sha256(open(os.path.join(ROOT, f["path"]), "rb").read()).hexdigest()
        if have != f["sha256"]:
            bad.append(f"{f['path']}: {have} != {f['sha256']}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    sc = score(json.load(open(a.e92)), reg)
    arms = {}
    for arm in a.e92_arm:
        name, path = arm.split("=", 1)
        arms[name] = score(json.load(open(path)), reg)
    for r, v in sc["rules"].items():
        if "verdict" not in v:
            continue
        vs = {v["verdict"]} | {arms[x]["rules"][r]["verdict"] for x in arms}
        vs.discard("NOT SCORED")
        v["slope_sensitive"] = len(vs) > 1
        v["arms"] = {x: arms[x]["rules"][r]["verdict"] for x in arms}
    sc["arms_contrasts"] = {x: {k: {"D_w": s["D_w"], "verdict": s["verdict"]} for k, s in arms[x]["contrasts"].items()} for x in arms}
    sc["arms_factorial"] = {x: arms[x]["factorial"] for x in arms}
    sc["label"] = a.label
    json.dump(sc, open(a.json, "w"), indent=1)
    write_md(sc, arms, a.md, a.label)
    print(json.dumps({r: v.get("verdict") for r, v in sc["rules"].items()}))


if __name__ == "__main__":
    main()
