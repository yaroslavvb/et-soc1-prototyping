#!/usr/bin/env python3
"""E136 (Q137): the frozen predictions for a large GEMM's power, clock, rate and die under aifoundry2's own governor, the admission table and the
rules. No E136 data exists when this runs. Writes predictions-e136.json; prints predictions-e136.txt. Standard library only.

    python3 tools/claims-v3/e136/make_predictions_e136.py > tools/claims-v3/e136/predictions-e136.txt

THE GEMMS (rgm136's SP_GEMM_LARGE, the vendor's pattern scaled up; tools/claims-v3/e136/rgm136/README.md):
  g4k  gemmL4x8x8: 4,096 x 4,096 x 4,096 elements in fp32 (K 8,192 in fp16, 16,384 in int8); A, B, C 64 MB each, 192 MB with C: it streams to DRAM.
  g2k  gemmL2x2x2: 2,048 x 1,024 x 1,024 in fp32; A 8, B 4, C 8 MB, 20 MB with C: it stays in the 32 MB L3 from its second pass.

INPUTS, every one committed before E136:
  * the desk model (tools/claims-v3/e136/desk/reuse_e136.json): per shire-op, the lines that miss the L2 (192 of 192 in g4k, 176 in g2k) and, for g4k,
    the share of A's and B's missing lines the L3 still holds (B 0.500: a column panel's second row tile; A 0.658 at a 32 MB L3, 0 at 24 MB).
  * E119 (docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm.<arm>.<type>.fit): aifoundry2's T(f) = C/f + M of c1 (no line missing),
    c8s (128 missing lines an op, served by the L3: E107 R4) and c16 (128, each a block's first touch: fresh), per format, this binary's kernel loop.
  * E107 (docs/reports/data/2026-11-01-e107-gemm-placement/): T at 600 MHz on aifoundry3 (scored.json T) and S over idle (e107.json items.<arm>.<t>.<kind>.S)
    of c1, c8s, c16 for zeros, random and sparse50, and the resident kernel's zeros S (items.<t>.zeros).
  * E95 (docs/reports/data/2026-11-01-e95-real-tensors-energy/scored.json tiles.<t>.r2_<name>.D over tiles.<t>.<random>.D): the real kind's tiles,
    E101's registered real set (tools/claims-v3/kinds/e101_common.py REAL_SET: GPT-2, BERT and ViT tiles of Q132(r)'s real2), each tile's D over the
    same format's random D, averaged over the four.
  * E101's relation and E83's dither, through E119's own module (tools/claims-v3/e119/make_predictions_e119.py: B(f), s(f), c_zeros, the transfer
    1.01865, the burst cap 66.15 +- 2.75 W and sustained 49.75 +- 1.95 W).
  * E126 (docs/reports/data/2026-11-02-e126-gemm-arms/results.json cells): the five random fp32 sustained runs the governor held (c4s, c8s, c16r8, c16r4,
    c16r2), for the second footing of the sustained clock only (below).
  * The heat path: aifoundry2's steady coefficient 0.67 C per board W (E111 A3, E133: 0.65-0.70), and E119's and E126's own burst and sustained cells
    (die start, die max or window mean, board W) for the two shape constants below.

THE SPEED MODEL. A line that misses the L2 costs what it costs in the arm that serves it the same way:
  T(f) = T_c1(f) + n_L3 / 128 x (T_c8s(f) - T_c1(f)) + n_fresh / 128 x (T_c16(f) - T_c1(f)),
  with n_L3 + n_fresh the missing lines an op. g2k: n_L3 176, n_fresh 0. g4k P1 (A held by a 32 MB L3): n_L3 = 64 x 0.658 + 64 = 106.1, n_fresh 85.9;
  g4k P2 (A fresh every time): n_L3 64, n_fresh 128. P1 is the point frozen; P2 is the other end; R1 places the measurement between them.
  The kind does not change T (E119 R4, E126 R7).

THE POWER MODEL. Energy per op interpolated the same way, from E107's pinned card (aifoundry3, 600 MHz, the same kernel loop):
  E(kind) = E_c1 + n_L3 / 128 (E_c8s - E_c1) + n_fresh / 128 (E_c16 - E_c1), E_arm = S_arm x T_arm, and S = E / T(600, aifoundry3's T by the same law).
  real = zeros + r_real x (random - zeros), r_real E95's mean over the four tiles of E101's real set (fp32 0.995, fp16 0.983, int8 0.792).
  Then E119's rule: c(600) = c_zeros + (S - S_resident_zeros) / 1.01865; board power at f = B(f) + c s(f) (600 T(600)) / (f T(f)), with T aifoundry2's.

THE CLOCK. Footing G1 (registered primary): E119's dither at E101's caps (burst 66.15 W, sustained 49.75 W). Footing G2 (registered second): the sustained
  cap refitted so that the same dither gives E126's five held random fp32 clocks from E119's laws for those arms (least squares; c4s takes c8s's law);
  for a held cell G2 predicts E126's mean held board power. Both are scored; R4 says which predicts better.

THE DIE. Burst (6 s): die_max = die_start + k_b x (P_burst - 21.5 W), k_b fitted through the origin over E119's and E126's bursts. Sustained (the last
  40 s of about 76 s): die = (1 - w) die_start + w (44.0 + 0.67 (P_sus - 21.5)), capped at 65.5 C (the trip holds the die; E133: it trips at a reading
  of 66), w fitted over E119's and E126's sustained runs whose die stayed under 64 C. die_start is the run's own measured start (a frozen law of a
  measured input).

THE ADMISSION ESTIMATE (the registered rule, run_e105.py's code with `fixed_p800_w` entries): p800 = B(800) + s(800) x c(600). A cell runs only if
  p800 <= 88 W; after any run whose board reading reached 93 W, no cell with an estimate at or above that run's goes on; the session's stops are E126's
  (80 C on one sample, 93 W on three), inside E101's registered 97 W.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "docs/reports/data")
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import make_predictions_e119 as M119  # noqa: E402  (E119's module: the relation, the dither, its laws for E107's arms)

TYPES = ("fp32", "fp16", "int8")
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
KINDS = ("zeros", "top", "sparse50", "real")
MACS, MINIONS = M119.MACS, M119.MINIONS
GEMMS = {"g4k": "gemmL4x8x8", "g2k": "gemmL2x2x2"}
P_IDLE, DIE_IDLE, C_STEADY, TRIP = 21.5, 44.0, 0.67, 65.5
LIMIT_W, LOCK_W = 88.0, 93.0

DESK = json.load(open(os.path.join(HERE, "desk", "reuse_e136.json")))
R119 = json.load(open(os.path.join(DATA, "2026-11-01-e119-gemm-speed/results.json")))
R126 = json.load(open(os.path.join(DATA, "2026-11-02-e126-gemm-arms/results.json")))
S107 = json.load(open(os.path.join(DATA, "2026-11-01-e107-gemm-placement/scored.json")))
E107 = json.load(open(os.path.join(DATA, "2026-11-01-e107-gemm-placement/e107.json")))["items"]
E95 = json.load(open(os.path.join(DATA, "2026-11-01-e95-real-tensors-energy/scored.json")))["tiles"]
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e101_common as EC  # noqa: E402  (E101's registered real set)
B, SF, CZ, XFER = M119.B, M119.SF, M119.CZ, M119.XFER
WB, SB, WS, SS = M119.WB, M119.SB, M119.WS, M119.SS


def lines(g, model="P1"):
    """(n_L3, n_fresh) missing lines per shire-op"""
    d = DESK["gemms"][g]
    miss = d["L2"]["steady_missing_lines_per_op"]
    if g == "g2k":
        return miss, 0.0
    a = d["L3"]["32MB"]["A_in_L3"] if model == "P1" else 0.0
    b = d["L3"]["32MB"]["B_in_L3"]
    nA, nB = 64.0, 128.0                       # A's 4 tiles and B's 8 tiles an op, 16 lines each; every one misses the L2 (desk model 1)
    assert abs(miss - (nA + nB)) < 1e-6
    return nA * a + nB * b, nA * (1 - a) + nB * (1 - b)


def T_end(arm, t, f):
    fit = R119["per_arm"][f"{arm}.{t}"]["fit"]
    return fit["C"] / f + fit["M"]


def T_a2(g, t, f, model="P1"):
    nl, nf = lines(g, model)
    c1, c8, c16 = T_end("c1", t, f), T_end("c8s", t, f), T_end("c16", t, f)
    return c1 + nl / 128.0 * (c8 - c1) + nf / 128.0 * (c16 - c1)


def T_a3_600(g, t, model="P1"):
    nl, nf = lines(g, model)
    c1, c8, c16 = (S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16"))
    return c1 + nl / 128.0 * (c8 - c1) + nf / 128.0 * (c16 - c1)


def r_real(t):
    ref = E95[f"{t}.{TOP[t]}"]["D"]["mean"]
    v = [E95[f"{t}.r2_{n}"]["D"]["mean"] / ref for n in EC.REAL_SET[t]]
    return sum(v) / len(v)


def S_arm(arm, t, kind):
    k = TOP[t] if kind == "top" else kind
    if kind == "real":
        z, r = E107[f"{arm}.{t}.zeros"]["S"]["mean"], E107[f"{arm}.{t}.{TOP[t]}"]["S"]["mean"]
        return z + r_real(t) * (r - z)
    return E107[f"{arm}.{t}.{k}"]["S"]["mean"]


def S_gemm(g, t, kind, model="P1"):
    nl, nf = lines(g, model)
    E = {a: S_arm(a, t, kind) * S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16")}
    e = E["c1"] + nl / 128.0 * (E["c8s"] - E["c1"]) + nf / 128.0 * (E["c16"] - E["c1"])
    return e / T_a3_600(g, t, model)


def c600(g, t, kind, model="P1"):
    return CZ[t] + (S_gemm(g, t, kind, model) - E107[f"{t}.zeros"]["S"]["mean"]) / XFER


def levels(g, t, kind, model="P1"):
    c = c600(g, t, kind, model)
    t6 = T_a2(g, t, 600, model)
    return {f: B[f] + c * SF[f] * (600.0 * t6) / (f * T_a2(g, t, f, model)) for f in (600, 700, 800)}


def p_at(P, f):
    """board power at a mean clock f between the levels (the dither's own interpolation)"""
    if f >= 800:
        return P[800]
    if f >= 700:
        return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
    if f >= 600:
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0
    return P[600]


def rate(t, T_us):
    return 2.0 * MACS[t] * MINIONS / (T_us * 1e-6) / 1e12


def fit_g2():
    """G2: the sustained cap that makes E119's dither give E126's five held random fp32 clocks (golden-section on squared error), and their mean board W"""
    held = {"c4s": "c8s", "c8s": "c8s", "c16r8": "c16r8", "c16r4": "c16r4", "c16r2": "c16r2"}
    obs = []
    for arm, law in held.items():
        c = R126["cells"][f"{arm}-fp32-randn"]
        P = M119.power_levels(law, "fp32", "randn")
        obs.append((P, c["sus_mhz"], c["sus_w"]))

    def err(W):
        return sum((M119.dither(P, W, SS)[0] - f) ** 2 for P, f, _ in obs)
    lo, hi = 40.0, 80.0
    for _ in range(80):
        a, b = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
        if err(a) < err(b):
            hi = b
        else:
            lo = a
    W = (lo + hi) / 2
    rms = math.sqrt(err(W) / len(obs))
    return W, rms, sum(o[2] for o in obs) / len(obs), [(round(M119.dither(P, W, SS)[0], 1), f) for P, f, _ in obs]


def fit_heat():
    """k_b through the origin over the bursts; w over the sustained runs whose die stayed under 64 C (E119 and E126 cells, one value per run)"""
    xb = yb = 0.0
    nb = 0
    num = den = 0.0
    ns = 0
    for R in (R119, R126):
        for lab, c in R["cells"].items():
            for dmax, dst, w in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or [], [c.get("burst_w")] * len(c.get("burst_die_max") or [])):
                if None in (dmax, dst, w):
                    continue
                xb += (w - P_IDLE) ** 2
                yb += (w - P_IDLE) * (dmax - dst)
                nb += 1
            if c.get("sus_die") is not None and c["sus_die"] < 64 and c.get("sus_die_start"):
                dst = sum(c["sus_die_start"]) / len(c["sus_die_start"])
                target = DIE_IDLE + C_STEADY * (c["sus_w"] - P_IDLE)
                # die = dst + w (target - dst)  ->  least squares for w
                num += (target - dst) * (c["sus_die"] - dst)
                den += (target - dst) ** 2
                ns += 1
    return yb / xb, nb, num / den, ns


def main():
    W2, rms2, held_w2, g2_check = fit_g2()
    k_b, n_b, w_s, n_s = fit_heat()
    laws, cells, adm, gaps = {}, {}, {}, {}
    for g in GEMMS:
        for t in TYPES:
            rec = {}
            for model in ("P1", "P2") if g == "g4k" else ("P1",):
                t6, t8 = T_a2(g, t, 600, model), T_a2(g, t, 800, model)
                nl, nf = lines(g, model)
                rec[model] = {"n_L3": round(nl, 2), "n_fresh": round(nf, 2), "T600_us": round(t6, 4), "T800_us": round(t8, 4), "X": round(t6 / t8, 4),
                              "rate_600": round(rate(t, t6), 3), "rate_800": round(rate(t, t8), 3), "T600_a3_us": round(T_a3_600(g, t, model), 4)}
            laws[f"{g}.{t}"] = rec
    for g in GEMMS:
        for t in TYPES:
            for kind in KINDS:
                kn = TOP[t] if kind == "top" else kind
                lab = f"{g}-{t}-{kn}"
                P = levels(g, t, kind)
                est = B[800] + SF[800] * c600(g, t, kind)
                fb, _ = M119.dither(P, WB, SB)
                fs1, _ = M119.dither(P, WS, SS)
                fs2, _ = M119.dither(P, W2, SS)
                pb = p_at(P, fb)
                ps1 = p_at(P, fs1)
                ps2 = held_w2 if fs2 < 795 else p_at(P, fs2)
                T = lambda f: T_a2(g, t, f)  # noqa: E731
                cells[lab] = {"S600_w": round(S_gemm(g, t, kind), 2), "c600_w": round(c600(g, t, kind), 3), "P_w": {str(f): round(v, 2) for f, v in P.items()},
                              "p800_estimate_w": round(est, 1), "admitted": est <= LIMIT_W,
                              "burst_mhz": round(fb, 1), "burst_w": round(pb, 2), "burst_rate": round(rate(t, T(fb)), 3),
                              "sus_mhz_G1": round(fs1, 1), "sus_w_G1": round(ps1, 2), "sus_rate_G1": round(rate(t, T(fs1)), 3),
                              "sus_mhz_G2": round(fs2, 1), "sus_w_G2": round(ps2, 2), "sus_rate_G2": round(rate(t, T(fs2)), 3),
                              "die_burst_rise_c": round(k_b * (pb - P_IDLE), 2),
                              "die_sus_target_G1_c": round(DIE_IDLE + C_STEADY * (ps1 - P_IDLE), 2), "die_sus_target_G2_c": round(DIE_IDLE + C_STEADY * (ps2 - P_IDLE), 2)}
                if g == "g4k":
                    P2 = levels(g, t, kind, "P2")
                    cells[lab]["P2_P_w"] = {str(f): round(v, 2) for f, v in P2.items()}
                adm[lab] = {"c_ref_w": round(c600(g, t, kind), 3), "fixed_p800_w": round(est, 1)}
            z = cells[f"{g}-{t}-zeros"]
            for kind in KINDS[1:]:
                kn = TOP[t] if kind == "top" else kind
                r = cells[f"{g}-{t}-{kn}"]
                gaps[f"{g}-{t}-{kn}"] = {"burst_rate": round(z["burst_rate"] / r["burst_rate"], 4), "burst_clock": round(z["burst_mhz"] / r["burst_mhz"], 4),
                                         "sus_rate_G1": round(z["sus_rate_G1"] / r["sus_rate_G1"], 4), "sus_rate_G2": round(z["sus_rate_G2"] / r["sus_rate_G2"], 4)}
    adm["rest"] = {"fixed_p800_w": 30.0}
    heat = {"P_idle_w": P_IDLE, "die_idle_c": DIE_IDLE, "c_steady_c_per_w": C_STEADY, "trip_c": TRIP, "k_burst_c_per_w": round(k_b, 4), "n_burst": n_b,
            "w_sus": round(w_s, 4), "n_sus": n_s,
            "burst_law": "die_max = die_start + k_burst (P_burst - P_idle)", "sus_law": "die_window = min(trip, (1 - w) die_start + w (die_idle + c_steady (P_sus - P_idle)))"}
    gov = {"G1": {"burst": [WB, SB], "sustained": [WS, SS]}, "G2": {"sustained_W_star_w": round(W2, 3), "sigma_w": SS, "fit_rms_mhz": round(rms2, 2),
                                                                     "held_board_w": round(held_w2, 2), "fit_check": g2_check}}
    rules = {
        "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "safety": {"die_c": 80, "board_w": 93, "board_samples": 3},
        "R2_clock_buys": {"text": "the X measurement, E119's clock_x unchanged (used by reduce_e136.py): T600 the mean T of launches whose kernel clock is in [590, 610] MHz, T800 of those at or above 790 MHz, every kind pooled; at least 2 launches at 600 and 5 at 800, else from the fit T = C/f + M over 590-810 MHz.",
                          "lo_mhz": [590, 610], "hi_mhz": 790, "min_lo": 2, "min_hi": 5},
        "R0_ties": {"text": "every check of C (the host's reference over the whole K) exact or approx, in the smoke and in every run; the smoke's cycles per op within 50-250% of P1's at 800 MHz. A FAIL labels every other verdict."},
        "R1_g4k_place": {"text": "g4k, the large GEMM that streams to DRAM: T at 800 MHz (wall / ops per minion, launches at or above 790 MHz on the kernel's own clock, every kind pooled) against P1 (A held by the L3) and P2 (A fresh). h = (T800 - T800(P2)) / (T800(P1) - T800(P2)). A HELD: h >= 0.75; A FRESH: h <= 0.25; BETWEEN otherwise; OUTSIDE if h < -0.5 or h > 1.5 (the line-cost law fails). Per format; fp32 primary. And the point: PASS if T800 within 5% of P1's.",
                         "held_min": 0.75, "fresh_max": 0.25, "outside": [-0.5, 1.5], "point_rel": 0.05, "primary": "fp32"},
        "R2_g2k_l3": {"text": "g2k, the large GEMM the L3 holds: T at 800 MHz within 5% of the law with its 176 missing lines an op served by the L3; X = T600 / T800 within 0.03 of the law's (E119's clock_x on this session's launches).", "point_rel": 0.05, "x_band": 0.03},
        "R3_burst_power": {"text": "every admitted cell's measured burst board power at 800 MHz (reduce_kspeed's p800_w, the first second's) within 4 W of the frozen P(800) (P1 for g4k); and at or below the admission estimate + 1 W (E119's R6). Per cell PASS / FAIL; the rms error printed.", "band_w": 4.0, "slack_w": 1.0},
        "R4_sus_clock": {"text": "each sustained cell's mean clock over its last 40 s within 30 MHz of the frozen clock, footing G1 (the registered primary) and footing G2 scored the same way; the rms error of each footing over the sustained cells, and of the sustained board W (G1, G2). The footing with the lower clock rms predicts better.", "band_mhz": 30.0},
        "R5_gap": {"text": "the zeros-against-kind speed gap (zeros' rate / the kind's rate) per format and kind with both runs: burst within 0.03 of the frozen gap; sustained within 0.05 of G1's (G2's printed beside it).", "burst_band": 0.03, "sus_band": 0.05},
        "R6_die": {"text": "the die law: a burst's die_max (the minion shires' mean, the sampler's reading) within 3 C of die_start + k_burst (P_burst - P_idle) with the run's measured die_start and the frozen P_burst; a sustained run's window mean within 3 C of min(65.5, (1 - w) die_start + w (44.0 + 0.67 (P_sus,G1 - 21.5))), and the same with G2's P_sus. rms printed.", "band_c": 3.0},
        "R7_kind": {"text": "at a given clock the kind does not change the count in a large GEMM either: every cell's T at or above 790 MHz within 1% of its zeros' (same GEMM and format).", "rel": 0.01},
        "R8_rate": {"text": "the headline: each cell's measured sustained rate (TFLOPS or TOPS) within 7% of the frozen G1 rate, and burst rate within 5%; the error per cell and the rms printed (the prediction error the README leads with).", "sus_rel": 0.07, "burst_rel": 0.05},
    }
    out = {"experiment": "E136", "request": "Q137", "date": "2026-11-02", "what": "frozen before the claim and the first launch of E136; nothing of E136 exists",
           "gemms": GEMMS, "kinds": KINDS, "top": TOP, "macs": MACS, "minions": MINIONS, "desk": "tools/claims-v3/e136/desk/reuse_e136.json",
           "lines": {g: {m: lines(g, m) for m in (("P1", "P2") if g == "g4k" else ("P1",))} for g in GEMMS}, "r_real": {t: round(r_real(t), 4) for t in TYPES},
           "laws": laws, "cells": cells, "gaps": gaps, "admission": adm, "heat": heat, "governor": gov, "rules": rules,
           "relation": {"B": B, "s800": SF[800], "s_f": SF, "burst": [WB, SB], "sustained": [WS, SS], "c_zeros_w": CZ, "xfer": XFER},
           "inputs": {"e119_fits": "docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm.<arm>.<type>.fit (c1, c8s, c16)",
                      "e107": "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json T, e107.json items.<arm>.<t>.<kind>.S",
                      "e95": "docs/reports/data/2026-11-01-e95-real-tensors-energy/scored.json tiles.<t>.r2_<name>.D / tiles.<t>.<random>.D over kinds/e101_common.py REAL_SET",
                      "e126": "docs/reports/data/2026-11-02-e126-gemm-arms/results.json cells (G2 and the heat constants)",
                      "relation": "tools/claims-v3/kinds/predictions-e101.json clock.relation via tools/claims-v3/e119/make_predictions_e119.py",
                      "heat": "E111 A3 / E133 A: 0.67 C per board W"}}
    json.dump(out, open(os.path.join(HERE, "predictions-e136.json"), "w"), indent=1)
    print("E136 frozen predictions (no E136 data exists). aifoundry2 under its own governor; T from E119's aifoundry2 fits by the line-cost law; S from E107's pinned card.")
    print(f"lines per shire-op: {out['lines']}; r_real {out['r_real']}")
    print(f"heat: k_burst {k_b:.4f} C/W over {n_b} bursts; w {w_s:.4f} over {n_s} sustained runs; G2 sustained cap {W2:.2f} W (fit rms {rms2:.1f} MHz; {g2_check}), held board {held_w2:.2f} W")
    print(f"{'gemm.format':10s} {'model':5s} {'nL3':>6s} {'nfr':>6s} {'T600':>7s} {'T800':>7s} {'X':>6s} {'rate600':>8s} {'rate800':>8s}")
    for k, rec in laws.items():
        for m, v in rec.items():
            print(f"{k:10s} {m:5s} {v['n_L3']:6.1f} {v['n_fresh']:6.1f} {v['T600_us']:7.4f} {v['T800_us']:7.4f} {v['X']:6.3f} {v['rate_600']:8.3f} {v['rate_800']:8.3f}")
    print(f"{'cell':22s} {'S600':>6s} {'P800':>6s} {'est':>6s} {'adm':>3s} {'burst':>6s} {'bW':>6s} {'brate':>7s} {'sus1':>6s} {'sW1':>6s} {'srate1':>7s} {'sus2':>6s} {'sW2':>6s} {'srate2':>7s} {'dB':>5s}")
    for k, v in cells.items():
        print(f"{k:22s} {v['S600_w']:6.2f} {v['P_w']['800']:6.1f} {v['p800_estimate_w']:6.1f} {str(v['admitted'])[0]:>3s} {v['burst_mhz']:6.1f} {v['burst_w']:6.1f} {v['burst_rate']:7.3f} "
              f"{v['sus_mhz_G1']:6.1f} {v['sus_w_G1']:6.1f} {v['sus_rate_G1']:7.3f} {v['sus_mhz_G2']:6.1f} {v['sus_w_G2']:6.1f} {v['sus_rate_G2']:7.3f} {v['die_burst_rise_c']:5.1f}")
    print("zeros / kind, frozen: burst rate; sustained rate G1, G2")
    for k, v in gaps.items():
        print(f"  {k:22s} x{v['burst_rate']:.3f}   x{v['sus_rate_G1']:.3f}  x{v['sus_rate_G2']:.3f}")


if __name__ == "__main__":
    main()
