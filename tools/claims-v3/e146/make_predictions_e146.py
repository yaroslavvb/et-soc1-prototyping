#!/usr/bin/env python3
"""E146 (Q138): the frozen predictions for a ladder of C-store cadences and one fresh GEMM shape under aifoundry2's own governor: time per op (three
models), board power (two), the burst clock, the die, the admission table and the rules. No E146 data exists when this runs. Writes
predictions-e146.json; prints predictions-e146.txt. Standard library only.

    python3 tools/claims-v3/e146/make_predictions_e146.py > tools/claims-v3/e146/predictions-e146.txt

THE SHAPES (rgm136's gemmL<MB>x<NB>x<KB>, E136's binary unchanged; a minion stores each C tile after KB x 32 ops; the desk split of every line by operand
and place is tools/claims-v3/e146/desk/reuse_e146.json, its 32 MB column):
  L1 2x2x1, L2 2x2x2 (= E136's g2k), L4 1x2x4, L8 1x1x8: held by the L3 (14, 20, 20, 26 MB with C), a store every 32, 64, 128, 256 ops.
  D1 4x8x1, D2 4x8x2, D4 4x8x4, D8 4x8x8 (= E136's g4k): C's 64 MB streams to DRAM (80, 96, 128, 192 MB), a store every 32, 64, 128, 256 ops.
  F6 3x4x6: the fresh shape nobody has run (3,072 x 2,048 x 3,072 in fp32, 84 MB with C), a store every 192 ops.

INPUTS, E119 AND E136 ONLY for every term this run tests (the brief: "a store term fitted on E119 and E136 only"):
  * E119 (docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm.<arm>.<type>.fit): T(f) = C/f + M of c1, c8s and c16 on aifoundry2, each storing
    a C tile every 32 ops.
  * E136 (docs/reports/data/2026-11-02-e136-large-gemm/results.json): per_gemm.<g>.<t>.fit (T(f) of g2k and g4k, every kind pooled) and T800; cells.<cell>
    .burst_p800_w_runs (the first second's board power at 800 MHz in a burst) for zeros and random.
  * E136's frozen power law, governor and heat law as frozen (tools/claims-v3/e136/predictions-e136.json and make_predictions_e136.py: E107's pinned S and
    T, E119's relation B(f), s(f), c_zeros and the transfer, the dither and its caps, G2's sustained cap, k_burst 0.1445 C/W, w_sus 0.6207), unchanged.

TIME PER OP. With n_L3, n_F the lines an op that miss the shire's L2 and come from the L3 or fresh (A_ and B_ the same by operand), n_miss their sum, N the
ops between C stores, and E119's arms' T at f (T1 = c1, T8 = c8s, T16 = c16):
  M0, E136's frozen law (the baseline, "before"): T0 = T1 + n_L3/128 (T8 - T1) + n_F/128 (T16 - T1).
  MS, THE STORE TERM (registered primary): T_S = T0 + (n_miss/128) sigma(f) (1/N - 1/32). A store's cost shows only where lines miss (c1 hides it: its 528
    FMA cycles leave no room), and every E119 arm stores every 32 ops, so the law prices 1/32 of a store into every op. sigma per format, least squares
    at 600 and at 800 MHz over E136's g2k (N 64) and g4k (N 256), then sigma(f) = Cs/f + Ms through the two.
  MAB, THE OPERAND SPLIT (registered alternative, no store term): a missing line costs by operand and place, pA, pB (L3) and qA, qB (fresh), solved
    exactly at 600 and 800 MHz from c8s (A 64, B 64 from the L3), g2k (A 64, B 112 from the L3), c16 (A 64, B 64 fresh) and g4k (A 42.11 / 21.89, B 64 / 64,
    L3 / fresh); T_AB = T1 + A_L3 pA + B_L3 pB + A_F qA + B_F qB, and C/f + M through the two clocks.
  The kind does not change T (E119 R4, E126 R7, E136 R7).

POWER. E136's law as frozen for each shape's lines (E107's pinned energies interpolated by line class, E119's relation): c600, then P0(f) = B(f) + c s(f)
  (600 T0(600)) / (f T0(f)) ("before"). THE STORE'S ENERGY (registered primary, "after"): the law's energy per op e0(f) = (P0(f) - B(f)) T0(f) gains
  eps (1/N - 1/32) (scaled with f as the law's own energy, s(f) 800 / (s(800) f)), eps per format and kind fitted at 800 MHz by least squares over E136's
  two GEMMs from e_meas = (p800 - B(800)) T800; then P_S(f) = B(f) + e_S(f) / T_S(f). eps is the card's energy for one store step: every minion storing
  one 1 KB tile, 1 MB of C. A floor, frozen with it: e_S >= 0, so no shape is predicted under the base power B(f) (an extrapolation of the zeros' eps
  to a store every 256 ops would otherwise read below it). The burst clock: E119's dither at the burst cap 66.15 +- 2.75 W on P_S's levels.

THE DIE. E136's laws as frozen: a burst's die_max = die_start + 0.1445 (P_burst - 21.5); a sustained run's window mean = min(65.5, 0.379 die_start + 0.621
  (44.0 + 0.67 (P_sus - 21.5))), P_sus on footing G2 (E136's better footing: the sustained cap 60.827 W, a held cell at 62.06 W) and on G1.

THE ADMISSION ESTIMATE, E119's and E136's rule unchanged: p800 = B(800) + s(800) c600 (the law's c, which over-read every one of E136's 20 bursts). A cell
  runs only if its estimate is at or below 88 W; after any run whose board reading reached 93 W, no cell with an estimate at or above that run's goes on.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "docs/reports/data")
sys.path.insert(0, os.path.join(HERE, "..", "e136"))
import make_predictions_e136 as M136  # noqa: E402  (E136's module as frozen: E119's relation and dither, E107's S and T, the heat constants)

M119 = M136.M119
TYPES, TOP = M136.TYPES, M136.TOP
KINDS = ("zeros", "top")
MACS, MINIONS = M136.MACS, M136.MINIONS
B, SF, CZ, XFER = M136.B, M136.SF, M136.CZ, M136.XFER
WB, SB, WS, SS = M136.WB, M136.SB, M136.WS, M136.SS
P_IDLE, DIE_IDLE, C_STEADY, TRIP = M136.P_IDLE, M136.DIE_IDLE, M136.C_STEADY, M136.TRIP
LIMIT_W, LOCK_W = 88.0, 93.0
DESK = json.load(open(os.path.join(HERE, "desk", "reuse_e146.json")))
R136 = json.load(open(os.path.join(DATA, "2026-11-02-e136-large-gemm/results.json")))
P136 = json.load(open(os.path.join(HERE, "..", "e136", "predictions-e136.json")))
SHAPES = list(DESK["shapes"])
LADDER_L, LADDER_D, FRESH = ("L1", "L2", "L4", "L8"), ("D1", "D2", "D4", "D8"), "F6"
E136_AS = {"g2k": "L2", "g4k": "D8"}        # E136's two GEMMs are these two shapes (the same arm, the same binary)
CLOCKS = (600, 800)


def ln(s, cap="32MB"):
    d = DESK["shapes"][s]["lines"][cap]
    return d


def N(s):
    return DESK["shapes"][s]["store_every_ops"]


def T_end(arm, t, f):
    return M136.T_end(arm, t, f)


def T0(s, t, f, cap="32MB"):
    d = ln(s, cap)
    T1, T8, T16 = T_end("c1", t, f), T_end("c8s", t, f), T_end("c16", t, f)
    return T1 + d["n_L3"] / 128.0 * (T8 - T1) + d["n_F"] / 128.0 * (T16 - T1)


def T136(g, t, f):
    v = R136["per_gemm"][f"{g}.{t}"]["fit"]
    return v["C"] / f + v["M"]


def xs(s):
    return (ln(s)["n_miss"] / 128.0) * (1.0 / N(s) - 1.0 / 32.0)


def fit_sigma(t):
    """sigma(f) at 600 and 800 MHz by least squares through the origin over E136's two GEMMs; then Cs, Ms of sigma(f) = Cs/f + Ms"""
    sig = {}
    for f in CLOCKS:
        num = den = 0.0
        for g, s in E136_AS.items():
            x, y = xs(s), T136(g, t, f) - T0(s, t, f)
            num += x * y
            den += x * x
        sig[f] = num / den
    Cs = (sig[600] - sig[800]) / (1 / 600.0 - 1 / 800.0)
    Ms = sig[800] - Cs / 800.0
    return {"sigma600_us": sig[600], "sigma800_us": sig[800], "Cs_cycles": Cs, "Ms_us": Ms}


SIG = {t: fit_sigma(t) for t in TYPES}


def sigma(t, f):
    return SIG[t]["Cs_cycles"] / f + SIG[t]["Ms_us"]


def TS(s, t, f, cap="32MB"):
    return T0(s, t, f, cap) + sigma(t, f) * xs(s) if cap == "32MB" else T0(s, t, f, cap) + sigma(t, f) * (ln(s, cap)["n_miss"] / 128.0) * (1.0 / N(s) - 1.0 / 32.0)


def solve2(a11, a12, b1, a21, a22, b2):
    det = a11 * a22 - a12 * a21
    return (b1 * a22 - a12 * b2) / det, (a11 * b2 - b1 * a21) / det


def fit_ab(t):
    """per-line prices by operand and place at 600 and 800 MHz, solved exactly from c8s, g2k (L3) and c16, g4k (fresh)"""
    arms = DESK["arms"]
    out = {}
    for f in CLOCKS:
        T1, T8, T16 = T_end("c1", t, f), T_end("c8s", t, f), T_end("c16", t, f)
        L2, D8 = ln("L2"), ln("D8")
        pA, pB = solve2(arms["c8s"]["A_miss"], arms["c8s"]["B_miss"], T8 - T1, L2["A_L3"], L2["B_L3"], T136("g2k", t, f) - T1)
        rest = T136("g4k", t, f) - T1 - D8["A_L3"] * pA - D8["B_L3"] * pB
        qA, qB = solve2(arms["c16"]["A_miss"], arms["c16"]["B_miss"], T16 - T1, D8["A_F"], D8["B_F"], rest)
        out[f] = {"pA_L3": pA, "pB_L3": pB, "qA_F": qA, "qB_F": qB}
    return out


AB = {t: fit_ab(t) for t in TYPES}


def TAB(s, t, f, cap="32MB"):
    d = ln(s, cap)
    vals = {}
    for g in CLOCKS:
        p = AB[t][g]
        vals[g] = T_end("c1", t, g) + d["A_L3"] * p["pA_L3"] + d["B_L3"] * p["pB_L3"] + d["A_F"] * p["qA_F"] + d["B_F"] * p["qB_F"]
    C = (vals[600] - vals[800]) / (1 / 600.0 - 1 / 800.0)
    M = vals[800] - C / 800.0
    return C / f + M


MODELS = {"M0": T0, "MS": TS, "MAB": TAB}


# ------------------------------------------------------------------------------------------------ power: E136's law for explicit lines
def T_a3_600(s, t):
    d = ln(s)
    c1, c8, c16 = (M136.S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16"))
    return c1 + d["n_L3"] / 128.0 * (c8 - c1) + d["n_F"] / 128.0 * (c16 - c1)


def S_shape(s, t, kind):
    d = ln(s)
    E = {a: M136.S_arm(a, t, kind) * M136.S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16")}
    e = E["c1"] + d["n_L3"] / 128.0 * (E["c8s"] - E["c1"]) + d["n_F"] / 128.0 * (E["c16"] - E["c1"])
    return e / T_a3_600(s, t)


def c600(s, t, kind):
    return CZ[t] + (S_shape(s, t, kind) - M136.E107[f"{t}.zeros"]["S"]["mean"]) / XFER


def levels0(s, t, kind):
    c, t6 = c600(s, t, kind), T0(s, t, 600)
    return {f: B[f] + c * SF[f] * (600.0 * t6) / (f * T0(s, t, f)) for f in (600, 700, 800)}


def e0(s, t, kind, f):
    return (levels0(s, t, kind)[f] - B[f]) * T0(s, t, f)


def fscale(f):
    return SF[f] * 800.0 / (SF[800] * f)


def fit_eps(t, kind):
    """eps at 800 MHz by least squares through the origin over E136's two GEMMs: e_meas - e0 = eps (1/N - 1/32)"""
    kn = TOP[t] if kind == "top" else kind
    num = den = 0.0
    pts = []
    for g, s in E136_AS.items():
        runs = [x for x in R136["cells"][f"{g}-{t}-{kn}"]["burst_p800_w_runs"] if x is not None]
        p8 = sum(runs) / len(runs)
        em = (p8 - B[800]) * R136["per_gemm"][f"{g}.{t}"]["T800"]
        x = 1.0 / N(s) - 1.0 / 32.0
        y = em - e0(s, t, kind, 800)
        num += x * y
        den += x * x
        pts.append({"gemm": g, "p800_w": round(p8, 2), "e_meas": round(em, 3), "e0": round(e0(s, t, kind, 800), 3), "x": x})
    eps = num / den
    for p in pts:
        p["resid"] = round(p["e_meas"] - p["e0"] - eps * p["x"], 3)
    return eps, pts


EPS = {(t, k): fit_eps(t, k) for t in TYPES for k in KINDS}


def levelsS(s, t, kind):
    eps = EPS[(t, kind)][0]
    out = {}
    for f in (600, 700, 800):
        Tf = TS(s, t, f)
        e = e0(s, t, kind, f) + eps * (1.0 / N(s) - 1.0 / 32.0) * fscale(f)
        out[f] = B[f] + max(0.0, e) / Tf          # the floor: a GEMM draws at least the card's base power at its clock, B(f)
    return out


def rate(t, T_us):
    return 2.0 * MACS[t] * MINIONS / (T_us * 1e-6) / 1e12


def main():
    k_b, w_s = P136["heat"]["k_burst_c_per_w"], P136["heat"]["w_sus"]
    W2, held_w2 = P136["governor"]["G2"]["sustained_W_star_w"], P136["governor"]["G2"]["held_board_w"]
    laws, cells, adm, pairs, fitted = {}, {}, {}, {}, {}
    for t in TYPES:
        fitted[t] = {"sigma": {k: round(v, 5) for k, v in SIG[t].items()},
                     "ab": {str(f): {k: round(v, 6) for k, v in AB[t][f].items()} for f in CLOCKS},
                     "eps": {k: {"eps_uJ_per_store_step": round(EPS[(t, k)][0], 2), "points": EPS[(t, k)][1]} for k in KINDS},
                     "e136_check": {g: {m: round(MODELS[m](s, t, 800), 4) for m in MODELS} | {"measured_T800_fit": round(T136(g, t, 800), 4)} for g, s in E136_AS.items()}}
    for s in SHAPES:
        for t in TYPES:
            rec = {"arm": DESK["shapes"][s]["arm"], "store_every_ops": N(s), "lines": ln(s), "lines_24MB": ln(s, "24MB")}
            for m, fn in MODELS.items():
                t6, t8 = fn(s, t, 600), fn(s, t, 800)
                rec[m] = {"T600_us": round(t6, 4), "T800_us": round(t8, 4), "X": round(t6 / t8, 4), "C_cycles": round((t6 - t8) / (1 / 600.0 - 1 / 800.0), 1),
                          "M_us": round(t8 - (t6 - t8) / (1 / 600.0 - 1 / 800.0) / 800.0, 4), "cyc800": round(t8 * 800, 1), "rate_800": round(rate(t, t8), 3)}
                rec[m + "_24MB"] = {"T800_us": round(fn(s, t, 800, "24MB"), 4)}
            laws[f"{s}.{t}"] = rec
            for kind in KINDS:
                kn = TOP[t] if kind == "top" else kind
                lab = f"{s}-{t}-{kn}"
                P0 = levels0(s, t, kind)
                PS = levelsS(s, t, kind)
                est = B[800] + SF[800] * c600(s, t, kind)
                fb0, _ = M119.dither(P0, WB, SB)
                fbS, _ = M119.dither(PS, WB, SB)
                pbS = M136.p_at(PS, fbS)
                pb0 = M136.p_at(P0, fb0)
                c = {"c600_w": round(c600(s, t, kind), 3), "P0_w": {str(f): round(v, 2) for f, v in P0.items()}, "PS_w": {str(f): round(v, 2) for f, v in PS.items()},
                     "p800_estimate_w": round(est, 1), "admitted": est <= LIMIT_W,
                     "e0_800": round(e0(s, t, kind, 800), 3), "eS_800": round((PS[800] - B[800]) * TS(s, t, 800), 3),
                     "burst_mhz_S": round(fbS, 1), "burst_w_S": round(pbS, 2), "burst_mhz_0": round(fb0, 1), "burst_w_0": round(pb0, 2),
                     "die_burst_rise_S_c": round(k_b * (pbS - P_IDLE), 2), "die_burst_rise_0_c": round(k_b * (pb0 - P_IDLE), 2),
                     "burst_rate_S": round(rate(t, TS(s, t, fbS)), 3)}
                if s == FRESH:
                    for g, (W, sig) in (("G1", (WS, SS)), ("G2", (W2, SS))):
                        fs, _ = M119.dither(PS, W, sig)
                        ps = (held_w2 if fs < 795 else M136.p_at(PS, fs)) if g == "G2" else M136.p_at(PS, fs)
                        c[f"sus_mhz_{g}"] = round(fs, 1)
                        c[f"sus_w_{g}"] = round(ps, 2)
                        c[f"die_sus_target_{g}_c"] = round(DIE_IDLE + C_STEADY * (ps - P_IDLE), 2)
                        c[f"sus_rate_{g}"] = round(rate(t, TS(s, t, fs)), 3)
                cells[lab] = c
                adm[lab] = {"c_ref_w": round(c600(s, t, kind), 3), "fixed_p800_w": round(est, 1)}
    adm["rest"] = {"fixed_p800_w": 30.0}
    # the registered contrasts: two shapes with the same lines a op and different store cadences, and the ladders' rungs
    for (a, b) in (("L4", "L8"), ("L2", "L4"), ("L1", "L2"), ("D4", "D8"), ("D2", "D4"), ("D1", "D2")):
        for t in TYPES:
            pairs[f"{a}/{b}.{t}"] = {m: round(MODELS[m](b, t, 800) / MODELS[m](a, t, 800), 4) for m in MODELS}
    heat = dict(P136["heat"])
    gov = {"G1": {"burst": [WB, SB], "sustained": [WS, SS]}, "G2": {"sustained_W_star_w": W2, "sigma_w": SS, "held_board_w": held_w2}}
    rules = {
        "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W,
        "safety": {"abs_stop_c": 80, "board_cap_w": 93, "cap_consecutive": 3},
        "R2_clock_buys": {"text": "E119's clock_x unchanged (used by reduce_e146.py): T600 the mean T of launches whose kernel clock is in [590, 610] MHz, T800 of those at or above 790 MHz, every kind pooled; at least 2 launches at 600 and 5 at 800, else from the fit T = C/f + M over 590-810 MHz.",
                          "lo_mhz": [590, 610], "hi_mhz": 790, "min_lo": 2, "min_hi": 5},
        "R0_ties": {"text": "every check of C (the host's reference over the whole K) exact or approx, in the smoke and in every run; the smoke's cycles per op at the launch's own clock within 50-250% of MS's at 800 MHz; L2 and D8 (E136's g2k and g4k, the same arm and binary) T800 within 2% of E136's measured T800, per format (a second session on the same card). A FAIL of the checks labels every other verdict.", "replicate_rel": 0.02},
        "R1_store_pair": {"text": "THE STORE TERM, primary. L4 (a store every 128 ops) and L8 (every 256) have the same lines an op by the desk model (A 64, B 128, all from the L3); rho = T800(L8) / T800(L4). On the axis from MAB's rho (no store term) to MS's: h = (rho - rho_MAB) / (rho_MS - rho_MAB). THE STORE TERM if h >= 0.75; NO STORE TERM if h <= 0.25; BETWEEN otherwise; NEITHER if h < -0.5 or h > 1.5. Per format; fp32 primary. If L8's T800 is above MS's 24 MB bound (its A no longer held by the L3), R1 is UNRESOLVED and the pair L2/L4 (MS against MAB the same way) is read in its place.",
                          "store_min": 0.75, "none_max": 0.25, "outside": [-0.5, 1.5], "primary": "fp32", "fallback": "L2/L4"},
        "R2_ladder": {"text": "every ladder cell's T800 (L1-L8, D1-D8; launches at or above 790 MHz, every kind pooled) within 5% of MS's; the rms relative error of each model (M0, MS, MAB) over the 24 cells; the model with the lowest rms predicts the ladder best. And each cell's X within 0.03 of MS's.", "point_rel": 0.05, "x_band": 0.03},
        "R3_burst_power": {"text": "every admitted ladder cell's burst board power at 800 MHz (p800_w, the first second's median) within 4 W of PS(800); the rms of PS and of P0 (E136's law with M0's time) over the cells; at or below the admission estimate + 1 W.", "band_w": 4.0, "slack_w": 1.0},
        "R4_store_energy": {"text": "the store's energy, measured: on the pair L4/L8 (the same lines), eps_meas = (e(L8) - e(L4)) / (1/256 - 1/128) with e = (p800 - B(800)) T800 per kind and format; within a factor of two of the fitted eps (the same sign, 0.5-2x), per format and kind; a cell whose PS(800) sits on the floor B(800) for either shape is not scored (the model says only the floor there). And on D4/D8 (lines nearly the same) printed, not scored.", "factor": 2.0},
        "R5_fresh": {"text": "THE FRESH SHAPE F6 (gemmL3x4x6, never run), predicted first: T800 within 5% of MS's (per format; M0 and MAB printed); X within 0.03; burst p800 within 4 W of PS(800) (zeros and random, every format); burst die_max within 3 C of die_start + 0.1445 (P_burst,S - 21.5); the two sustained runs (fp32 randn, int8 full): clock within 30 MHz of G2's, board W within 4 W of G2's, the window die within 3 C of E136's sustained law on G2's power.", "point_rel": 0.05, "x_band": 0.03, "band_w": 4.0, "band_c": 3.0, "band_mhz": 30.0},
        "R6_die": {"text": "every burst's die_max within 3 C of die_start + 0.1445 (P_burst - 21.5) with PS's burst power at PS's burst clock; rms printed (and with P0's).", "band_c": 3.0},
        "R7_kind": {"text": "every cell's T at or above 790 MHz within 1% of its zeros' (same shape and format).", "rel": 0.01},
        "R8_passes": {"text": "the unit of replication is the pass: each cell's T800 and p800 per pass; the pair ratios of R1 per pass; a verdict that holds in one pass and not the other is reported as such (no interval between sessions: one session).", "scored": False},
    }
    out = {"experiment": "E146", "request": "Q138", "date": "2026-11-02", "what": "frozen before the claim and the first launch of E146; nothing of E146 exists",
           "shapes": {s: DESK["shapes"][s]["arm"] for s in SHAPES}, "ladders": {"L": LADDER_L, "D": LADDER_D}, "fresh": FRESH, "kinds": KINDS, "top": TOP,
           "macs": MACS, "minions": MINIONS, "desk": "tools/claims-v3/e146/desk/reuse_e146.json", "e136_as": E136_AS,
           "fitted": fitted, "laws": laws, "cells": cells, "pairs": pairs, "admission": adm, "heat": heat, "governor": gov, "rules": rules,
           "relation": {"B": B, "s800": SF[800], "s_f": SF, "burst": [WB, SB], "sustained": [WS, SS], "c_zeros_w": CZ, "xfer": XFER},
           "inputs": {"e119_fits": "docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm.<arm>.<type>.fit (c1, c8s, c16)",
                      "e136": "docs/reports/data/2026-11-02-e136-large-gemm/results.json per_gemm.<g>.<t>.fit, .T800; cells.<g>-<t>-<kind>.burst_p800_w_runs (zeros, top)",
                      "e136_frozen": "tools/claims-v3/e136/predictions-e136.json heat, governor; tools/claims-v3/e136/make_predictions_e136.py (the power law, E107's S and T, E95's real ratios, E119's relation)"}}
    json.dump(out, open(os.path.join(HERE, "predictions-e146.json"), "w"), indent=1)
    print("E146 frozen predictions (no E146 data exists). aifoundry2 under its own governor; time per op by M0 (E136's law), MS (the store term) and MAB (the operand split);")
    print("power by P0 (E136's law) and PS (the store's energy); every new term fitted on E119's arms and E136's two GEMMs only.")
    for t in TYPES:
        sg = SIG[t]
        print(f"{t}: sigma(600) {sg['sigma600_us']:.3f} us, sigma(800) {sg['sigma800_us']:.3f} us a store (Cs {sg['Cs_cycles']:.0f} cycles, Ms {sg['Ms_us']:.3f} us); "
              f"AB at 800: pA {AB[t][800]['pA_L3']*1e3:.2f} pB {AB[t][800]['pB_L3']*1e3:.2f} qA {AB[t][800]['qA_F']*1e3:.2f} qB {AB[t][800]['qB_F']*1e3:.2f} ns a line; "
              f"eps zeros {EPS[(t, 'zeros')][0]:.0f}, {TOP[t]} {EPS[(t, 'top')][0]:.0f} uJ a store step")
        for g, v in fitted[t]["e136_check"].items():
            print(f"    E136 {g}: measured (fit) T800 {v['measured_T800_fit']:.4f}; M0 {v['M0']:.4f}, MS {v['MS']:.4f}, MAB {v['MAB']:.4f}")
    print(f"{'shape.fmt':9s} {'N':>4s} {'miss':>6s} {'nL3':>6s} {'nF':>6s}  {'M0 T800':>8s} {'MS T800':>8s} {'MAB T800':>8s}  {'MS X':>6s} {'MAB X':>6s}  {'MS 24MB':>8s}")
    for k, v in laws.items():
        d = v["lines"]
        print(f"{k:9s} {v['store_every_ops']:4d} {d['n_miss']:6.1f} {d['n_L3']:6.1f} {d['n_F']:6.1f}  {v['M0']['T800_us']:8.4f} {v['MS']['T800_us']:8.4f} {v['MAB']['T800_us']:8.4f}  "
              f"{v['MS']['X']:6.3f} {v['MAB']['X']:6.3f}  {v['MS_24MB']['T800_us']:8.4f}")
    print(f"{'cell':18s} {'est':>5s} {'adm':>3s} {'P0 800':>7s} {'PS 800':>7s} {'burstS':>7s} {'bW_S':>6s} {'dieRise':>7s}  fresh sustained (G2: MHz, W, die target)")
    for k, v in cells.items():
        extra = f"  G2 {v['sus_mhz_G2']:.0f} MHz {v['sus_w_G2']:.1f} W {v['die_sus_target_G2_c']:.1f} C; G1 {v['sus_mhz_G1']:.0f} MHz {v['sus_w_G1']:.1f} W" if "sus_mhz_G2" in v else ""
        print(f"{k:18s} {v['p800_estimate_w']:5.1f} {str(v['admitted'])[0]:>3s} {v['P0_w']['800']:7.2f} {v['PS_w']['800']:7.2f} {v['burst_mhz_S']:7.1f} {v['burst_w_S']:6.2f} {v['die_burst_rise_S_c']:7.2f}{extra}")
    print("pairs, T800(b) / T800(a) by model:")
    for k, v in pairs.items():
        print(f"  {k:12s} M0 {v['M0']:.4f}  MS {v['MS']:.4f}  MAB {v['MAB']:.4f}")


if __name__ == "__main__":
    main()
