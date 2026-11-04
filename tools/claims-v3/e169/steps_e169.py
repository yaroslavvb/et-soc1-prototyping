#!/usr/bin/env python3
"""E169 (Q141(s)): the numbers behind REGISTRATION-A2.md's step rule, from committed files only. Desk only: no card, no device.
Writes step-rule-e169.json (the rule's constants, the frozen hypotheses' steps and their zones, E158's repeatability); prints
steps-e169.txt. Standard library only.

    nice -n 10 python3 -B tools/claims-v3/e169/steps_e169.py > tools/claims-v3/e169/steps-e169.txt

WHAT IT COMPUTES
  1. The step each frozen model predicts from E169's non-power-of-two shape to its power-of-two partner, T800(P) / T800(N) - 1 for
     P1/N1, P2/N2 and P3/N3, from predictions-e169.json as frozen in e39d06da (its sha256 is checked first), in fp32 (the primary)
     and in fp16 and int8 (printed if run); the registered sensitivity arms ALIGNED and A_STRICT beside them. It compares the fp32
     steps with the post hoc desk check of Q140's final critic (Q140(f), its e169_steps.json: SM 1.3706 / 1.0794 / 1.3097, ISO
     1.0 / 1.0576 / 1.0, STRICT 1.0 / 0.9897 / 1.0, quoted below as constants).
  2. E158's repeatability, the floor of the rule's interval: per cell (shape and format) with three passes, the sample sd of
     ln T800 over the passes (E158 results.json t800_by_pass), pooled over the 28 cells (2 degrees of freedom each); the step's
     floor sigma0 = sqrt(2) x that pooled sd (the log of a ratio of two cells); and the session-to-session repeat E158 measured
     against E146 (results.json rules.R0.replicate, 8 cells).
  3. The card's own steps where no power-of-two stride is involved: adjacent rungs on E158's plateau (K2 NB 9-13, K4 NB 6-7, K6 NB
     5-6, every far line at 39-59 MB), the card's null for "no step".
  4. The card's committed collapse steps, Q140(q)'s C3 (corrections.txt): each collapse over the nearest rung of its own ladder
     that is not one, measured (E146 and E158 results.json per_shape) and as SM, ISO and STRICT froze them (stride-sm.json
     predictions, e39d06da), with the rule's interval from E158's three passes where the two shapes are E158's.
  5. E158's measured T800 and steps for E169's four tie shapes (K4n7, K4n8, K6n5, K6n4).
  6. Copied, not changed: B7's constants as 49575094 registered them, and the reported power check's constants (beta and the
     fallback zeros offsets from g4.json, T_ref from m9_a2.json, the frozen P0(800) per shape from predictions-e169.json).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
Q140Q = os.path.join(LAB, "docs/reports/data/2026-11-04-q140q-gemm-g4-stride")
E158 = os.path.join(LAB, "docs/reports/data/2026-11-03-e158-l3-retention/results.json")
E146 = os.path.join(LAB, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")
FROZEN = {"predictions-e169.json": "38ee500fa1e66107ef5c544688263b1e988fb5a675bdee05f9876df1432cf19f",
          "stride_sm.py": "4b8b028dc09365b3a587a0808d7f13ccf22332962a9db139ff8d38f1cab8c65c",
          "stride-sm.json": "ef41a520029aa4b04c9ffb2377963b2c8c7ffcca70a3744f6c8c6317874225e3"}
PAIRS = (("P1", "N1"), ("P2", "N2"), ("P3", "N3"))
DECISIVE = ("P1/N1", "P3/N3")
REPORTED = ("P2/N2",)
MODELS = ("SM", "ISO", "STRICT")
ARMS = ("ALIGNED", "A_STRICT")
TYPES = ("fp32", "fp16", "int8")
BAND = 0.030          # the zone around each model's step: +-3.0 points of T800(P)/T800(N) - 1 (B7's own 3%)
N_MIN = 3             # passes with both shapes of a pair needed for a reading
N_MIN_LAUNCHES = 5    # launches at or above 790 MHz a burst needs for its pass to count (E119's clock_x min_hi)
CI = 0.95
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179}
CRITIC = {"P1/N1": {"SM": 1.3706, "ISO": 1.0, "STRICT": 1.0}, "P2/N2": {"SM": 1.0794, "ISO": 1.0576, "STRICT": 0.9897},
          "P3/N3": {"SM": 1.3097, "ISO": 1.0, "STRICT": 1.0}}
PLATEAU = (("K2n10", "K2n9"), ("K2n11", "K2n10"), ("K2n12", "K2n11"), ("K2n13", "K2n12"), ("K4n7", "K4n6"), ("K6n6", "K6n5"))
C3 = (("E146", "D4", "D2"), ("E146", "D8", "D2"), ("E158", "D4", "D2"), ("E158", "K4n8", "K4n7"), ("E158", "K6n4", "K6n3"), ("E158", "K6n4", "K6n5"))
TIES = ("K4n7", "K4n8", "K6n5", "K6n4")
TIE_STEPS = (("K4n8", "K4n7"), ("K6n4", "K6n5"))


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r(x, n=5):
    return None if x is None else round(x, n)


def interval(logs, sigma0):
    """the rule's step and 95% interval from per-pass log ratios: mean, the larger of their sd and sigma0, t at n - 1 degrees of freedom"""
    n = len(logs)
    m = sum(logs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in logs) / (n - 1)) if n > 1 else None
    s = max(sd or 0.0, sigma0)
    h = T975[n - 1] * s / math.sqrt(n) if n > 1 else None
    return {"n": n, "step": math.exp(m) - 1, "lo": None if h is None else math.exp(m - h) - 1, "hi": None if h is None else math.exp(m + h) - 1,
            "sd_log": sd, "sd_used": s, "floor_used": sd is None or sd < sigma0}


def zone_reading(lo, hi, steps):
    """REGISTRATION-A2.md S3: inside a model's zone, outside every zone, or across an edge"""
    inside = [m for m, s in steps.items() if lo >= s - BAND and hi <= s + BAND]
    if inside:
        return "SUPPORTS " + ", ".join(inside)
    if all(hi < s - BAND or lo > s + BAND for s in steps.values()):
        return "NONE OF THE THREE"
    return "UNRESOLVED"


def main():
    bad = [f for f, h in FROZEN.items() if sha256(os.path.join(Q140Q, f)) != h]
    if bad:
        raise SystemExit(f"refused: {bad} differ from their bytes at e39d06da")
    P = json.load(open(os.path.join(Q140Q, "predictions-e169.json")))
    SMJ = json.load(open(os.path.join(Q140Q, "stride-sm.json")))
    R158 = json.load(open(E158))
    R146 = json.load(open(E146))
    S = P["shapes"]
    out = {"what": "E169's step rule (REGISTRATION-A2.md, Q141(s)): its constants, the frozen hypotheses' steps and zones, and E158's repeatability, every number from committed files",
           "date": "2026-11-04", "amends": {"registration": "49575094", "freeze": "e39d06da", "amendment_A1": "1bfaa4e4"},
           "frozen_sha256": FROZEN,
           "rule": {"quantity": "s = T800(P) / T800(N) - 1, fp32 zeros, per pass j on that pass's two bursts (E158's per-pass T800: launches at or above 790 MHz), "
                                "then over the passes holding both: the mean of ln(T800_j(P) / T800_j(N)), its 95% interval with t at n - 1 degrees of freedom and the larger of the passes' sd and sigma0, back-transformed",
                    "band_points": round(100 * BAND, 1), "ci": CI, "n_min_passes": N_MIN, "n_min_launches_800": N_MIN_LAUNCHES, "t975": T975,
                    "decisive_pairs": list(DECISIVE), "reported_pairs": list(REPORTED),
                    "pass_counts": "a pass counts for a pair only if both of its bursts ran in that pass with at least n_min_launches_800 launches at or above 790 MHz each",
                    "pair_reading": "SUPPORTS <models whose zone holds the whole interval>; NONE OF THE THREE if the interval lies outside every zone; UNRESOLVED if it crosses a zone's edge; NO READING below n_min passes",
                    "presence": "on a decisive pair (ISO and STRICT both predict 0.0): PRESENT if the interval's low end is above +3.0 points, ABSENT if the interval lies inside [-3.0, +3.0], else UNRESOLVED",
                    "size": "on a decisive pair: SM if the interval lies inside SM's zone, NOT SM if it lies wholly outside it, else UNRESOLVED",
                    "verdict": {"INDEX STEP AS SM": "both decisive pairs PRESENT and SM",
                                "NO STEP": "both decisive pairs ABSENT",
                                "A STRIDE STEP SM DOES NOT SIZE": "both PRESENT, at least one NOT SM",
                                "A STRIDE STEP, ITS SIZE UNRESOLVED": "both PRESENT, none NOT SM, at least one size UNRESOLVED",
                                "MIXED": "one decisive pair PRESENT and the other ABSENT",
                                "UNRESOLVED": "any other combination (a presence UNRESOLVED)",
                                "NO VERDICT": "a decisive pair below n_min passes"},
                    "r0_label": "if any check of C is neither exact nor approx (or a run has none), R0 FAILS and every reading and verdict is printed labelled 'R0 FAIL' (E158's R0); nothing is dropped",
                    "reported_beside": "per pair: the share of SM's step, s / s_SM, over the same interval; the ratio of the pass-pooled T800s; each pass's step; fp16 and int8 steps against their own frozen steps if those formats ran (no verdict)"},
           "b7_as_registered": {"source": "REGISTRATION.md B7 (49575094), predictions-e169.json rules", "point_rel": 0.03, "point": "SM's frozen T800 within 3% on every one of the six shapes (fp32; fp16 and int8 printed if run)",
                                "resolved_min_sm_iso_rel": 0.03, "resolved": "on each of P1-P3: |T_SM - T_ISO| / T_ISO >= 3% and the measured T800 closer to SM than to ISO"},
           "power_reported": {"what": "reported, no verdict: each fp32 shape's first-second board at 800 MHz (E126's collect, burst_p800_w_runs) against E136's law P0(800) as frozen (predictions-e169.json peak.P0_800_fp32_zeros_w); "
                                      "against P0 + beta x delta_fp32 (Q140(l)'s zeros level, the T_Z G4 keeps); and against Q140(q) check (i)'s form P0 + beta x delta + k_D (T_start - T_ref) at k_D 0.47 (T_D, which G4 rejected for holds)",
                              "constants_from": "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/g4.json constants (beta, delta_fallback_w) and g4_model.T_REF 54.3818 C (m9_a2.json)", "k_D": 0.47}}
    # 1. the hypotheses' steps
    hyp, critic_diff = {}, 0.0
    for p, n in PAIRS:
        key = f"{p}/{n}"
        hyp[key] = {"P": S[p]["arm"], "N": S[n]["arm"], "decisive": key in DECISIVE}
        for t in TYPES:
            st = {m: S[p][t][m]["T800"] / S[n][t][m]["T800"] - 1 for m in MODELS + ARMS}
            hyp[key][t] = {"steps": {m: r(v) for m, v in st.items()},
                           "zones": {m: [r(st[m] - BAND), r(st[m] + BAND)] for m in MODELS},
                           "T800": {m: {"P": S[p][t][m]["T800"], "N": S[n][t][m]["T800"]} for m in MODELS}}
            if t == "fp32":
                for m in MODELS:
                    critic_diff = max(critic_diff, abs(round(1 + st[m], 4) - CRITIC[key][m]))
        f = hyp[key]["fp32"]["steps"]
        hyp[key]["fp32"]["SM_minus_nearest_other_points"] = r(100 * min(abs(f["SM"] - f["ISO"]), abs(f["SM"] - f["STRICT"])), 2)
    out["hypotheses"] = hyp
    out["critic_check"] = {"critic_e169_steps": CRITIC, "max_abs_diff_ratio_4dp": round(critic_diff, 6), "agree": critic_diff < 1e-9}
    # 2. E158's repeatability
    tbp = R158["t800_by_pass"]
    by = {}
    for k, v in tbp.items():
        ps, cell = k.split("|")
        by.setdefault(cell, {})[int(ps)] = v
    var, cells = [], {}
    for cell, d in sorted(by.items()):
        if len(d) < 3:
            continue
        lg = [math.log(d[j]) for j in sorted(d)]
        m = sum(lg) / len(lg)
        v = sum((x - m) ** 2 for x in lg) / (len(lg) - 1)
        var.append(v)
        cells[cell] = r(math.sqrt(v), 6)
    pooled = math.sqrt(sum(var) / len(var))
    sigma0 = math.sqrt(2.0) * pooled
    rep = R158["rules"]["R0"]["replicate"]
    out["e158_repeatability"] = {"cells": len(var), "df": 2 * len(var), "pooled_sd_ln_T800": r(pooled, 6), "worst_cell_sd_ln_T800": r(max(cells.values()), 6),
                                 "sigma0_ln_step": r(sigma0, 6), "per_cell_sd_ln_T800": cells,
                                 "expected_half_width_points_at_floor": {str(n): r(100 * T975[n - 1] * sigma0 / math.sqrt(n), 3) for n in (3, 4, 5)},
                                 "session_repeat_vs_e146": {"cells": len(rep), "rel_min": min(v["rel"] for v in rep.values()), "rel_max": max(v["rel"] for v in rep.values())}}
    out["rule"]["sigma0_ln_step"] = r(sigma0, 6)
    # 3. plateau neighbours
    ps158 = R158["per_shape"]
    plat = {}
    for a, b in PLATEAU:
        plat[f"{a}/{b}"] = r(ps158[f"{a}.fp32"]["T800"] / ps158[f"{b}.fp32"]["T800"] - 1)
    out["plateau_neighbour_steps_fp32"] = {"steps": plat, "min": min(plat.values()), "max": max(plat.values())}
    # 4. the committed collapses (Q140(q) C3) with the rule's machinery
    pred = SMJ["predictions"]
    c3 = {}
    for sess, a, b in C3:
        R = R158 if sess == "E158" else R146
        meas = R["per_shape"][f"{a}.fp32"]["T800"] / R["per_shape"][f"{b}.fp32"]["T800"] - 1
        st = {m: pred[f"{a}.fp32"][m]["T800"] / pred[f"{b}.fp32"][m]["T800"] - 1 for m in MODELS}
        rec = {"measured_pooled": r(meas), "models": {m: r(v) for m, v in st.items()}, "share_of_SM_step_pooled": r(meas / st["SM"], 3)}
        if sess == "E158":
            logs = [math.log(by[f"{a}.fp32"][j] / by[f"{b}.fp32"][j]) for j in (1, 2, 3)]
            iv = interval(logs, sigma0)
            rec["rule_interval_3_passes"] = {k: (r(v) if isinstance(v, float) else v) for k, v in iv.items()}
            rec["reading_post_hoc"] = zone_reading(iv["lo"], iv["hi"], st)
            rec["share_of_SM_step"] = r(iv["step"] / st["SM"], 3)
        c3[f"{sess}:{a}/{b}"] = rec
    out["committed_collapses_C3_post_hoc"] = c3
    # 5. the ties
    out["ties_e158"] = {"T800": {s: r(ps158[f"{s}.fp32"]["T800"]) for s in TIES},
                        "steps": {f"{a}/{b}": r(ps158[f"{a}.fp32"]["T800"] / ps158[f"{b}.fp32"]["T800"] - 1) for a, b in TIE_STEPS},
                        "t800_rel_bar": 0.02, "step_bar_points": 2.0}
    # the reported power check's constants, copied from the frozen files that hold them
    m9 = json.load(open(os.path.join(LAB, "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json")))
    g4 = json.load(open(os.path.join(Q140Q, "g4.json")))["constants"]
    assert abs(g4["beta"] - m9["params"]["beta"]) < 1e-12 and g4["delta_fallback_w"] == m9["fallback_delta_w"]
    out["power_reported"].update({"beta": g4["beta"], "delta_fallback_w": g4["delta_fallback_w"], "T_ref_c": m9["params"]["T_ref_c"],
                                  "P0_800_fp32_zeros_w": {s: S[s]["peak"]["P0_800_fp32_zeros_w"] for s in S}})
    json.dump(out, open(os.path.join(HERE, "step-rule-e169.json"), "w"), indent=1)

    print("E169's step rule: the numbers, from committed files (predictions-e169.json, stride_sm.py and stride-sm.json checked against e39d06da: OK)")
    print(f"\n1. The frozen models' steps, T800(P) / T800(N) - 1 (fp32 primary; zones +-{100 * BAND:.1f} points):")
    for key, h in hyp.items():
        f = h["fp32"]["steps"]
        print(f"  {key} ({h['P']} over {h['N']}{', decisive' if h['decisive'] else ', reported'}): SM {100 * f['SM']:+.2f}%  ISO {100 * f['ISO']:+.2f}%  STRICT {100 * f['STRICT']:+.2f}%"
              f"   (arms: ALIGNED {100 * f['ALIGNED']:+.2f}%, A_STRICT {100 * f['A_STRICT']:+.2f}%; SM to the nearest other {h['fp32']['SM_minus_nearest_other_points']:.2f} points)")
        for t in ("fp16", "int8"):
            g = h[t]["steps"]
            print(f"      {t} (printed if run): SM {100 * g['SM']:+.2f}%  ISO {100 * g['ISO']:+.2f}%  STRICT {100 * g['STRICT']:+.2f}%")
    print(f"  against Q140(f)'s e169_steps.json (ratios to 4 decimals): worst |diff| {critic_diff:.6f}: {'AGREE' if critic_diff < 1e-9 else 'DIFFER'}")
    e = out["e158_repeatability"]
    print(f"\n2. E158's repeatability: the sd of ln T800 over three passes, pooled over {e['cells']} cells ({e['df']} df): {100 * e['pooled_sd_ln_T800']:.4f}% "
          f"(worst cell {100 * e['worst_cell_sd_ln_T800']:.4f}%); the step's floor sigma0 = sqrt(2) x that = {100 * sigma0:.4f}%")
    print(f"  the 95% half-width at the floor: {e['expected_half_width_points_at_floor']} points (n = 3, 4, 5 passes); "
          f"E158 against E146 (another session, {e['session_repeat_vs_e146']['cells']} cells): {100 * e['session_repeat_vs_e146']['rel_min']:+.2f}% to {100 * e['session_repeat_vs_e146']['rel_max']:+.2f}%")
    print(f"\n3. The card's plateau neighbours (no power-of-two stride; far lines at 39-59 MB), fp32: " + ", ".join(f"{k} {100 * v:+.2f}%" for k, v in plat.items()))
    print("\n4. The committed collapses (Q140(q) C3), the step over the nearest rung that is not one, fp32; the rule's machinery on E158's three passes (post hoc for E158):")
    for k, v in c3.items():
        m = v["models"]
        line = (f"  {k:18s} measured {100 * v['measured_pooled']:+6.2f}%  SM {100 * m['SM']:+6.2f}%  ISO {100 * m['ISO']:+6.2f}%  STRICT {100 * m['STRICT']:+6.2f}%"
                f"  (share of SM's step {v['share_of_SM_step_pooled']:.2f})")
        if "rule_interval_3_passes" in v:
            iv = v["rule_interval_3_passes"]
            line += f"  | rule: {100 * iv['step']:+.2f}% [{100 * iv['lo']:+.2f}, {100 * iv['hi']:+.2f}]{' (floor)' if iv['floor_used'] else ''} -> {v['reading_post_hoc']}; {v['share_of_SM_step']:.2f} of SM's step"
        print(line)
    t = out["ties_e158"]
    print(f"\n5. E158's tie shapes, fp32 T800: {t['T800']}; steps: " + ", ".join(f"{k} {100 * v:+.2f}%" for k, v in t["steps"].items()))
    print("\nwrote step-rule-e169.json")


if __name__ == "__main__":
    main()
