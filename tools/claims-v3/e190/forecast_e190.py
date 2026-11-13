#!/usr/bin/env python3
"""E190 (Q169): the frozen forecasts for ONE 8,192 x 8,192 x 8,192 GEMM in fp32, fp16 and int8 (random data, E136's kind) on two ET-SoC-1 cards:
its seconds, its board watts, its joules over idle and with the card at rest, and the die. Written before any E190 datum. Standard library only.

    python3 -I -B tools/claims-v3/e190/forecast_e190.py            writes forecast-e190.json and prints forecast-e190.txt (redirect stdout)
    python3 -I -B tools/claims-v3/e190/forecast_e190.py --check    recomputes everything and compares it with the committed JSON (exit 0 = PASS)

LABEL. Informed by E136's measured results (and E146's replicate of them): NOT blind to E136. Blind to every 8,192^3 datum (none exists) and to
card 1's GEMM behaviour (no GEMM of this harness has run on aifoundry1's card 1).

THE GEMM (rgm136 unchanged; desk/reuse_e190.py): fp32 gemmL8x16x16, fp16 gemmL8x16x8, int8 gemmL8x16x4: M = N = K = 8,192 in every format, so
131,072 / 65,536 / 32,768 tensor ops per minion (16 x 16 tiles, K 16 / 32 / 64 per op), 1,024 minions, 2 x 8,192^3 = 1.0995e12 operations.

ARM A, aifoundry2 card 0 under its own governor (nothing set), 800 MHz bursts. ARM B, aifoundry1 card 1 as found (600 MHz in every sample since Sep).

1. SECONDS. t = ops per minion x T(f), T the time per op. T is anchored on a measured large GEMM of the same block shape and scaled by E136's line-cost
   law re-footed on E126's c16s (E136 posthoc.txt section 1, -1.5% on g4k fp32): T(f) = c1(f) + n_L3/128 (c8s(f) - c1(f)) + n_fresh/128 (c16s(f) - c1(f)),
   E119's and E126's aifoundry2 fits, lines a shire-op from desk/reuse_e190.json at a 32 MB L3 (strict LRU, E136's model unchanged; the model that
   matched the measured power-of-two-stride shapes D4 and D8 within 2.2%, Q140(q) stride-sm.txt S2). Anchors: fp32 and fp16 on E136's g4k
   (gemmL4x8x8, measured T600 and T800, its P1 lines 106.1 / 85.9); int8 on E146's D4 (gemmL4x8x4, KB 4 as E190's int8; lines 120 / 72).
   T = T_anchor x law(E190 lines) / law(anchor lines). Two-sided band by rule: from min(1, every alternative ratio) x 0.97 to max(1, every
   alternative ratio) x 1.03, the alternatives being the c16s and c16 footings at a 32, 28 and 24 MB L3 (ratio 1 = the extra fresh lines cost nothing).
2. WATTS, arm A. The board over idle W = P_work - P_rest(T0). Anchored on the anchor's measured bursts (E136 and E146: burst_w less the ledger v2's
   idle law at each run's starting die), moved to E190's shape and clock by E136's frozen power law (make_predictions_e136.py: energy per op
   interpolated by line class from E107's pinned card, E119's relation B(f), s(f)) with its switching coefficient re-read from the anchor's
   measured burst: c_E190 = c_meas x c_law(E190 lines) / c_law(anchor lines); P(f) = B(f) + c s(f) 600 T(600) / (f T(f)); W(f) = W_meas + P_E190(f)
   - P_anchor,meas. Sustained: the burst level at the governor's clock (E119's dither at G2's refitted cap, E136's better footing) plus the anchor's
   measured sustained heating, scaled by W. Band: W at the T band's two ends and both footings, widened by 2 W (sessions, start die).
3. WATTS, arm B. The same switching at the same clock: W_B = kappa x W_A(600), kappa = 1.0094, card 1 over aifoundry2 in E37's DRAM-streamed fp32
   matmul at 600 MHz (8.865 / 8.783 W over the pre-launch idle; aifoundry3 8.355). Band: W_A(600)'s band x [0.95, 1.05] (E37's three-card spread).
   The ledger v2 as frozen (tools/ledger/ledger_v2.py, card aifoundry1-c1, 600 MHz, its own rows) prices the same GEMM as a REPORTED arm.
4. THE CARD AT REST: the ledger v2's idle law per card (frozen-v2.json idle_laws, the registered footing law) at the forecast starting die: arm A
   50 C (band 46-55), arm B 58 C (band 56-62); +-0.5 W (its rest band).
5. JOULES per GEMM: over idle J = W t; with the card at rest J = (P_rest + W) t. Bands: the products of the bands' ends.
6. THE DIE: arm A E136's frozen laws (burst die_max = die_start + k_burst (P - 21.5); sustained window = min(65.5, (1 - w) die_start + w (44 + 0.67
   (P_sus - 21.5)))); arm B burst die_start + k_rise W (M10's 4.5 s law for card 1, 0.12 C a W [0.09, 0.20]), sustained REPORTED only.
7. given(): the given-seconds formulas the scorer evaluates at the measured seconds, rest and clock (section "given" in the JSON).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e136"))
import make_predictions_e136 as M136  # noqa: E402  (E136's frozen laws; imports E119's module: B(f), s(f), the dither)
sys.path.insert(0, os.path.join(ROOT, "tools", "ledger"))
import ledger_v2 as LV  # noqa: E402  (the load ledger v2 as frozen, 06d60fa2)

FMTS = ("fp32", "fp16", "int8")
SHAPE = {"fp32": (8, 16, 16), "fp16": (8, 16, 8), "int8": (8, 16, 4)}
KIND = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
VALUES = {"fp32": "gemmL8x16x16:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
          "fp16": "gemmL8x16x8:randn:tools/claims-v3/kinds/tiles/fp16/randn.bin",
          "int8": "gemmL8x16x4:randn:tools/claims-v3/kinds/tiles/int8/full.bin"}
OPS = {t: SHAPE[t][0] * SHAPE[t][1] * 2 * SHAPE[t][2] * 32 for t in FMTS}
MINIONS = 1024
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
FLOP = 2 * 8192 ** 3
T0_A, T0_A_BAND = 50.0, (46.0, 55.0)
T0_B, T0_B_BAND = 58.0, (56.0, 62.0)
K_LEAK_RUN = 0.47          # W per C of start die inside a run (E159 0.44-0.50; E169's D12 term 0.47)
KAPPA_E37 = 8.86504 / 8.78283
KAPPA_BAND = (0.95, 1.05)
W_WIDEN = 2.0
PEAK_MARGIN_W = 4.0
LINE_A, LINE_B = 82.0, 70.0
STOP_A = {"board_w": 85.0, "board_samples": 3, "die_c": 80.0}
STOP_B = {"board_w": 75.0, "board_samples": 3, "die_c": 80.0}
F_LEDGER = os.path.join(DATA, "2026-11-12-q166-ledger-v2", "frozen-v2.json")

INPUTS = {
    "e136_results": "docs/reports/data/2026-11-02-e136-large-gemm/results.json",
    "e136_predictions": "tools/claims-v3/e136/predictions-e136.json",
    "e136_law_code": "tools/claims-v3/e136/make_predictions_e136.py",
    "e136_reuse_model": "tools/claims-v3/e136/desk/reuse_e136.py",
    "e119_module": "tools/claims-v3/e119/make_predictions_e119.py",
    "e119_fits": "docs/reports/data/2026-11-01-e119-gemm-speed/results.json",
    "e126_fits": "docs/reports/data/2026-11-02-e126-gemm-arms/results.json",
    "e146_results": "docs/reports/data/2026-11-02-e146-gemm-stores/results.json",
    "e146_desk": "tools/claims-v3/e146/desk/reuse_e146.json",
    "e190_desk": "tools/claims-v3/e190/desk/reuse_e190.json",
    "ledger_code": "tools/ledger/ledger_v2.py",
    "ledger_frozen": "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json",
    "ledger_scores_e37": "docs/reports/data/2026-11-12-q166-ledger-v2/scores-v2.json",
}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


R136 = load(INPUTS["e136_results"])
P136 = load(INPUTS["e136_predictions"])
R146 = load(INPUTS["e146_results"])
D146 = load(INPUTS["e146_desk"])
D190 = load(INPUTS["e190_desk"])
F119 = M136.R119["per_arm"]
F126 = M136.R126["per_arm"]
FL = LV.load_frozen(F_LEDGER)


def r(x, n=4):
    return None if x is None else round(x, n)


# ------------------------------------------------------------------ 1. the speed law
def T_fit(F, arm, f):
    v = F[arm]["fit"]
    return v["C"] / f + v["M"]


def law_T(nl, nf, t, f, footing):
    c1, c8 = T_fit(F119, f"c1.{t}", f), T_fit(F119, f"c8s.{t}", f)
    cf = T_fit(F126, f"c16s.{t}", f) if footing == "c16s" else T_fit(F119, f"c16.{t}", f)
    return c1 + nl / 128.0 * (c8 - c1) + nf / 128.0 * (cf - c1)


def anchor(t):
    """(name, (n_L3, n_fresh), T600, T800, measured bursts [(burst_w, mean die start, session)], sustained (sus_w, die start) or None)"""
    if t in ("fp32", "fp16"):
        g = R136["per_gemm"][f"g4k.{t}"]
        k = f"g4k-{t}-randn"
        c = R136["cells"][k]
        d8 = R146["cells"][f"D8-{t}-randn"]
        bursts = [(c["burst_w"], sum(c["burst_die_start"]) / len(c["burst_die_start"]), "E136"),
                  (d8["burst_w"], sum(d8["burst_die_start"]) / len(d8["burst_die_start"]), "E146 D8")]
        sus = (c["sus_w"], sum(c["sus_die_start"]) / len(c["sus_die_start"]), c["sus_mhz"], c["sus_die"])
        nl, nf = P136["lines"]["g4k"]["P1"]
        return {"name": "g4k (gemmL4x8x8; E136, its replicate E146 D8)", "lines": (nl, nf), "T600": g["T600"], "T800": g["T800"], "bursts": bursts, "sus": sus,
                "lines_source": "tools/claims-v3/e136/predictions-e136.json lines.g4k.P1", "T_source": f"{INPUTS['e136_results']} per_gemm.g4k.{t}"}
    g = R146["per_shape"]["D4.int8"]
    d4 = R146["cells"]["D4-int8-full"]
    l4 = D146["shapes"]["D4"]["lines"]["32MB"]
    c = R136["cells"]["g4k-int8-full"]
    bursts = [(d4["burst_w"], sum(d4["burst_die_start"]) / len(d4["burst_die_start"]), "E146 D4")]
    sus = (c["sus_w"], sum(c["sus_die_start"]) / len(c["sus_die_start"]), c["sus_mhz"], c["sus_die"])
    return {"name": "D4 (gemmL4x8x4; E146), KB 4 as E190's int8; sustained heating from E136's g4k int8", "lines": (l4["n_L3"], l4["n_F"]),
            "T600": g["T600"], "T800": g["T800"], "bursts": bursts, "sus": sus, "sus_from": "g4k-int8-full",
            "lines_source": "tools/claims-v3/e146/desk/reuse_e146.json shapes.D4.lines.32MB", "T_source": f"{INPUTS['e146_results']} per_shape.D4.int8"}


def e190_lines(t, cap="32MB"):
    v = D190["shapes"][t]["lines_per_shire_op"][cap]
    return v["n_L3"], v["n_fresh"]


def speed(t):
    a = anchor(t)
    out = {"anchor": a["name"], "anchor_lines": list(a["lines"]), "e190_lines_32MB": list(e190_lines(t))}
    for f in (600, 800):
        Ta = a["T600"] if f == 600 else a["T800"]
        ratios = {}
        for footing in ("c16s", "c16"):
            for cap in ("32MB", "28MB", "24MB"):
                nl, nf = e190_lines(t, cap)
                ratios[f"{footing}@{cap}"] = law_T(nl, nf, t, f, footing) / law_T(a["lines"][0], a["lines"][1], t, f, footing)
        pt = Ta * ratios["c16s@32MB"]
        lo = Ta * min(1.0, min(ratios.values())) * 0.97
        hi = Ta * max(1.0, max(ratios.values())) * 1.03
        out[f"T{f}_us"] = {"point": pt, "band": [lo, hi], "anchor_measured": Ta, "ratios": ratios}
        out[f"t{f}_s"] = {"point": OPS[t] * pt * 1e-6, "band": [OPS[t] * lo * 1e-6, OPS[t] * hi * 1e-6]}
    out["X"] = out["T600_us"]["point"] / out["T800_us"]["point"]
    out["rate_800_tflops"] = FLOP / out["t800_s"]["point"] / 1e12
    out["rate_600_tflops"] = FLOP / out["t600_s"]["point"] / 1e12
    return out


# ------------------------------------------------------------------ 2. E136's power law, parametrized by the lines (its formulas, unchanged)
def T_a3_600(nl, nf, t):
    c1, c8, c16 = (M136.S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16"))
    return c1 + nl / 128.0 * (c8 - c1) + nf / 128.0 * (c16 - c1)


def c600_law(nl, nf, t, kind="top"):
    E = {a: M136.S_arm(a, t, kind) * M136.S107["T"][f"{a}.{t}"] for a in ("c1", "c8s", "c16")}
    e = E["c1"] + nl / 128.0 * (E["c8s"] - E["c1"]) + nf / 128.0 * (E["c16"] - E["c1"])
    S = e / T_a3_600(nl, nf, t)
    return M136.CZ[t] + (S - M136.E107[f"{t}.zeros"]["S"]["mean"]) / M136.XFER


def law_tie():
    """the parametrized law at g4k P1 reproduces E136's frozen c600 and P(f) for the random cells (to 1e-6)"""
    worst = 0.0
    for t in FMTS:
        nl, nf = P136["lines"]["g4k"]["P1"]
        c = c600_law(nl, nf, t)
        fz = P136["cells"][f"g4k-{t}-{M136.TOP[t]}"]
        worst = max(worst, abs(round(c, 3) - fz["c600_w"]))
        t6 = M136.T_a2("g4k", t, 600)
        for f in (600, 700, 800):
            p = M136.B[f] + c * M136.SF[f] * (600.0 * t6) / (f * M136.T_a2("g4k", t, f))
            worst = max(worst, abs(round(p, 2) - fz["P_w"][str(f)]))
    return worst


def idle(card, T):
    return LV.idle_w(FL, card, T)[0]


def P_levels(c, T600, T800):
    T = {600: T600, 800: T800, 700: None}
    # T(700) by the T = C/f + M form through the two ends
    C = (T600 - T800) / (1 / 600.0 - 1 / 800.0)
    M = T800 - C / 800.0
    T[700] = C / 700.0 + M
    return {f: M136.B[f] + c * M136.SF[f] * (600.0 * T600) / (f * T[f]) for f in (600, 700, 800)}


def watts_A(t, sp):
    a = anchor(t)
    Pm = sum(b[0] for b in a["bursts"]) / len(a["bursts"])
    Wm = sum(b[0] - idle("aifoundry2", b[1]) for b in a["bursts"]) / len(a["bursts"])
    rm = 600.0 * a["T600"] / (800.0 * a["T800"])
    c_meas = (Pm - M136.B[800]) / (M136.SF[800] * rm)
    c_law_a = c600_law(a["lines"][0], a["lines"][1], t)

    def at(T600, T800, footing_lines=None):
        nl, nf = footing_lines or e190_lines(t)
        cE = c_meas * c600_law(nl, nf, t) / c_law_a
        L = P_levels(cE, T600, T800)
        return {f: Wm + L[f] - Pm for f in L}, cE, L
    W, cE, L = at(sp["T600_us"]["point"], sp["T800_us"]["point"])
    alts = [at(sp["T600_us"]["band"][i], sp["T800_us"]["band"][i])[0] for i in (0, 1)]
    alts.append(at(sp["T600_us"]["anchor_measured"], sp["T800_us"]["anchor_measured"], a["lines"])[0])   # no change from the anchor
    for cap in ("28MB", "24MB"):
        alts.append(at(sp["T600_us"]["point"], sp["T800_us"]["point"], e190_lines(t, cap))[0])
    band = {f: [min([W[f]] + [x[f] for x in alts]) - W_WIDEN, max([W[f]] + [x[f] for x in alts]) + W_WIDEN] for f in W}
    # sustained: the anchor's measured heating (sus over idle less burst over idle), scaled by W; the clock by the dither at G2's cap
    sus_w, sus_die_start, sus_mhz_meas, sus_die_meas = a["sus"]
    Wsus_anchor = sus_w - idle("aifoundry2", sus_die_start)
    c = R136["cells"][a.get("sus_from") or f"g4k-{t}-randn"]          # the sustained run's own session: its burst over idle
    Wb_ref = c["burst_w"] - idle("aifoundry2", sum(c["burst_die_start"]) / len(c["burst_die_start"]))
    H = (Wsus_anchor - Wb_ref) * W[800] / Wb_ref
    p_rest = idle("aifoundry2", T0_A)
    sus_levels = {f: p_rest + W[f] + H for f in W}
    W2 = P136["governor"]["G2"]["sustained_W_star_w"]
    f_sus, share800 = M136.M119.dither(sus_levels, W2, M136.SS)
    f_burst, _ = M136.M119.dither({f: p_rest + W[f] for f in W}, M136.WB, M136.SB)
    Wsus = M136.p_at({f: W[f] + H for f in W}, f_sus)
    heat = P136["heat"]
    P_burst = p_rest + W[800]
    P_sus = p_rest + Wsus
    die_b = T0_A + heat["k_burst_c_per_w"] * (P_burst - heat["P_idle_w"])
    die_s = min(heat["trip_c"], (1 - heat["w_sus"]) * (T0_A + 2.0) + heat["w_sus"] * (heat["die_idle_c"] + heat["c_steady_c_per_w"] * (P_sus - heat["P_idle_w"])))
    return {"anchor_bursts": [{"burst_w": b[0], "die_start_c": b[1], "session": b[2], "rest_by_law_w": idle("aifoundry2", b[1])} for b in a["bursts"]],
            "W_meas_anchor": Wm, "P_meas_anchor": Pm, "c_meas": c_meas, "c_law_anchor": c_law_a, "c_e190": cE, "levels_P": L,
            "W_over": {str(f): W[f] for f in W}, "W_over_band": {str(f): band[f] for f in band},
            "sus": {"heating_w": H, "anchor_sus_w": sus_w, "anchor_sus_mhz": sus_mhz_meas, "anchor_sus_die_c": sus_die_meas, "W2_cap_w": W2,
                    "f_mhz": f_sus, "share_800": share800, "W_over": Wsus, "W_over_band": [Wsus - (W[800] - band[800][0]), Wsus + (band[800][1] - W[800])],
                    "levels_board_w": {str(f): sus_levels[f] for f in sus_levels}},
            "burst_mhz": f_burst, "p_rest_w": p_rest, "p_rest_band_w": [idle("aifoundry2", T0_A_BAND[0]) - 0.5, idle("aifoundry2", T0_A_BAND[1]) + 0.5],
            "P_burst_w": P_burst, "P_sus_w": P_sus, "die_burst_max_c": die_b, "die_sus_window_c": die_s,
            "die_law": {"k_burst_c_per_w": heat["k_burst_c_per_w"], "w_sus": heat["w_sus"], "P_idle_w": heat["P_idle_w"], "trip_c": heat["trip_c"],
                        "die_start_burst_c": T0_A, "die_start_sus_c": T0_A + 2.0}}


# ------------------------------------------------------------------ 3. the ledger v2's price of the same GEMM on card 1 (REPORTED arm)
def ledger_load(t, card, f, T0, seconds):
    n_ops = MINIONS * OPS[t]
    nl, nf = e190_lines(t)
    rho, tau = 0.5, 0.5
    return {"card": card, "f_mhz": f, "die_start_c": T0, "seconds": seconds, "work_units": 1, "work_unit": "GEMM",
            "tensor": [{"format": t, "kind": KIND[t], "ops": n_ops}],
            "bytes": [{"path": "l3_load", "bytes": nl * 64.0 / 32.0 * n_ops, "rho": rho, "tau": tau, "what": "lines a shire-op from the L3, x 64 B / 32 minions"},
                      {"path": "dram_load", "bytes": nf * 64.0 / 32.0 * n_ops, "rho": rho, "tau": tau, "what": "fresh lines a shire-op, x 64 B / 32 minions"}]}


def ledger_price(t, card, f, T0, seconds):
    o = LV.predict(ledger_load(t, card, f, T0, seconds), FL)
    return {"j_over_idle": o["j_over_idle"], "j_over_idle_band": o["j_over_idle_band"], "j_heat": o["heat"]["j"], "die_rise_c": o["heat"]["die_rise_c"],
            "j_over_idle_with_heat": o["j_over_idle_with_heat"], "w_over_idle_with_heat": o["w_over_idle_with_heat"],
            "w_over_idle_with_heat_band": o["w_over_idle_with_heat_band"], "p_rest_w": o["rest"]["w"], "j_total": o["j_total"], "j_total_band": o["j_total_band"]}


# ------------------------------------------------------------------ given(): what the scorer evaluates at measured values
def W_at(fc, arm, t, block, f_mhz=None):
    """the frozen W over idle of a cell at the measured mean clock (arm A: E136's p_at between the frozen levels; arm B: its 600 MHz point)"""
    c = fc["cells"][f"{arm}.{t}.{block}"]
    if arm == "B" or "W_levels" not in c:
        return c["W_over"]["point"]
    lv = {int(k): v for k, v in c["W_levels"].items()}
    f = c["mhz"]["point"] if f_mhz is None else f_mhz
    return M136.p_at(lv, f)


def given(fc, arm, t, block, t_meas, p_rest_meas, f_mhz=None):
    """J a GEMM given the measured seconds (and the measured rest, and the measured clock on arm A): over idle = W t; with the card at rest = (P_rest + W) t"""
    W = W_at(fc, arm, t, block, f_mhz)
    return {"W_over": W, "j_over": W * t_meas, "j_rest": (p_rest_meas + W) * t_meas}


def given_ledger(t, t_meas, T0_meas, p_rest_meas, card="aifoundry1-c1", f=600):
    o = ledger_price(t, card, f, T0_meas, t_meas)
    return {"j_over": o["j_over_idle_with_heat"], "j_rest": p_rest_meas * t_meas + o["j_over_idle_with_heat"]}


# ------------------------------------------------------------------ build
def build():
    fc = {"experiment": "E190", "request": "Q169", "what": "frozen before any E190 datum; informed by E136's measured results (not blind to E136); blind to every "
          "8,192^3 datum and to card 1's GEMM behaviour", "gemm": {t: {"values": VALUES[t], "ops_per_minion": OPS[t], "minions": MINIONS, "macs_per_op": MACS_PER_OP[t],
                                                                        "operations": FLOP, "K_per_op": MACS_PER_OP[t] // 256} for t in FMTS},
          "inputs_sha256": {k: sha(v) for k, v in INPUTS.items()}, "inputs": INPUTS, "law_tie_worst": law_tie(),
          "constants": {"T0_A_c": T0_A, "T0_A_band_c": T0_A_BAND, "T0_B_c": T0_B, "T0_B_band_c": T0_B_BAND, "k_leak_run_w_per_c": K_LEAK_RUN,
                        "kappa_e37": KAPPA_E37, "kappa_band": KAPPA_BAND, "w_widen_w": W_WIDEN, "peak_margin_w": PEAK_MARGIN_W,
                        "line_A_w": LINE_A, "line_B_w": LINE_B, "stop_A": STOP_A, "stop_B": STOP_B,
                        "kappa_source": "docs/reports/data/2026-11-12-q166-ledger-v2/scores-v2.json rows E37 'W over the pre-launch idle' measured: "
                                        "aifoundry1-c1 8.86504, aifoundry2 8.78283, aifoundry3 8.35519 (mmb.json MMB-c fp32-tensor-DRAM)"},
          "die_law_e136": dict({k: P136["heat"][k] for k in ("k_burst_c_per_w", "P_idle_w", "w_sus", "die_idle_c", "c_steady_c_per_w", "trip_c")},
                               source="tools/claims-v3/e136/predictions-e136.json heat (E136's frozen die laws; held out on E146, 0.98 C rms)"),
          "speed": {}, "cells": {}, "ledger_arm": {}, "peaks": {}}
    for t in FMTS:
        sp = speed(t)
        fc["speed"][t] = sp
        wa = watts_A(t, sp)
        # ---- arm A cells: burst at the burst clock (800), sustained at the dither's clock
        for block in ("burst", "sus"):
            if block == "burst":
                W, Wb = wa["W_over"]["800"], wa["W_over_band"]["800"]
                f = wa["burst_mhz"]
                levels = {k: v for k, v in wa["W_over"].items()}
                die = wa["die_burst_max_c"]
                P = wa["P_burst_w"]
            else:
                W, Wb = wa["sus"]["W_over"], wa["sus"]["W_over_band"]
                f = wa["sus"]["f_mhz"]
                levels = {k: v + wa["sus"]["heating_w"] for k, v in wa["W_over"].items()}
                die = wa["die_sus_window_c"]
                P = wa["P_sus_w"]
            # seconds at the cell's clock: T(f) by T = C/f + M through the two frozen ends
            T6, T8 = sp["T600_us"]["point"], sp["T800_us"]["point"]
            C = (T6 - T8) / (1 / 600.0 - 1 / 800.0)
            Tf = C / f + (T8 - C / 800.0)
            tp = OPS[t] * Tf * 1e-6
            tb = [sp["t800_s"]["band"][0], sp["t800_s"]["band"][1] * (Tf / T8)]
            pr, prb = wa["p_rest_w"], wa["p_rest_band_w"]
            fc["cells"][f"A.{t}.{block}"] = {
                "card": "aifoundry2 card 0, its own governor", "mhz": {"point": f, "band": [790.0 if block == "burst" else max(600.0, f - 30.0), 800.0]},
                "t_gemm_s": {"point": tp, "band": tb}, "W_over": {"point": W, "band": Wb}, "W_levels": levels, "P_rest_w": {"point": pr, "band": prb},
                "P_work_w": {"point": pr + W, "band": [prb[0] + Wb[0], prb[1] + Wb[1]]},
                "J_over": {"point": W * tp, "band": [Wb[0] * tb[0], Wb[1] * tb[1]]},
                "J_rest": {"point": (pr + W) * tp, "band": [(prb[0] + Wb[0]) * tb[0], (prb[1] + Wb[1]) * tb[1]]},
                "die_c": {"point": die, "band": [die - 3.0, die + 3.0], "what": "burst: die max (the shires' mean) from a 50 C start; sus: the last 40 s's mean from 52 C"},
                "rate_tflops": FLOP / tp / 1e12}
        fc["cells"][f"A.{t}.burst"]["power_law"] = {k: wa[k] for k in ("anchor_bursts", "W_meas_anchor", "P_meas_anchor", "c_meas", "c_law_anchor", "c_e190", "levels_P")}
        fc["cells"][f"A.{t}.sus"]["governor"] = wa["sus"]
        # ---- arm B: card 1 at 600 MHz, the same switching at the same clock x kappa, its own idle
        WA6, WA6b = wa["W_over"]["600"], wa["W_over_band"]["600"]
        WB, WBb = KAPPA_E37 * WA6, [WA6b[0] * KAPPA_BAND[0], WA6b[1] * KAPPA_BAND[1]]
        pr, prb = idle("aifoundry1-c1", T0_B), [idle("aifoundry1-c1", T0_B_BAND[0]) - 0.5, idle("aifoundry1-c1", T0_B_BAND[1]) + 0.5]
        tp, tb = sp["t600_s"]["point"], sp["t600_s"]["band"]
        kr = FL["constants"]["k_rise_c_per_w"]
        die_b = T0_B + kr["value"] * WB
        leak = LV.leak_slope(FL, "aifoundry1-c1", T0_B)
        heat = P136["heat"]
        dT_sus = heat["w_sus"] * heat["c_steady_c_per_w"] * WB
        for block in ("burst", "sus"):
            Hs = 0.0 if block == "burst" else leak * dT_sus
            W, Wb = WB + Hs, [WBb[0] + 0.5 * Hs, WBb[1] + 1.5 * Hs]
            fc["cells"][f"B.{t}.{block}"] = {
                "card": "aifoundry1 card 1 as found", "mhz": {"point": 600.0, "band": [590.0, 610.0]},
                "t_gemm_s": {"point": tp, "band": tb}, "W_over": {"point": W, "band": Wb}, "P_rest_w": {"point": pr, "band": prb},
                "P_work_w": {"point": pr + W, "band": [prb[0] + Wb[0], prb[1] + Wb[1]]},
                "J_over": {"point": W * tp, "band": [Wb[0] * tb[0], Wb[1] * tb[1]]},
                "J_rest": {"point": (pr + W) * tp, "band": [(prb[0] + Wb[0]) * tb[0], (prb[1] + Wb[1]) * tb[1]]},
                "die_c": {"point": die_b if block == "burst" else T0_B + 2.0 + dT_sus,
                          "band": [T0_B + kr["band"][0] * WBb[0], T0_B_BAND[1] + kr["band"][1] * WBb[1]] if block == "burst"
                          else [T0_B + 2.0 + 0.5 * dT_sus, T0_B_BAND[1] + 2.0 + 1.6 * dT_sus],
                          "what": "burst: die max from a 58 C start (M10's 4.5 s law for card 1); sus: REPORTED only, aifoundry2's steady 0.67 C a W and E136's w carried by hand"},
                "rate_tflops": FLOP / tp / 1e12, "kappa": KAPPA_E37, "W_A600": WA6}
        fc["ledger_arm"][t] = ledger_price(t, "aifoundry1-c1", 600, T0_B, tp)
        fc["ledger_arm"][t]["label"] = "REPORTED arm: the ledger v2 as frozen, card aifoundry1-c1, 600 MHz, die 58 C, the frozen seconds; bytes by E136's convention (lines a shire-op x 64 B / 32)"
    # ---- predicted peaks against each arm's line
    for arm, line in (("A", LINE_A), ("B", LINE_B)):
        worst = max(fc["cells"][f"{arm}.{t}.{b}"]["P_work_w"]["band"][1] for t in FMTS for b in ("burst", "sus"))
        pt = max(fc["cells"][f"{arm}.{t}.{b}"]["P_work_w"]["point"] for t in FMTS for b in ("burst", "sus"))
        fc["peaks"][arm] = {"point_w": pt + PEAK_MARGIN_W, "band_top_w": worst + PEAK_MARGIN_W, "line_w": line, "under_line": worst + PEAK_MARGIN_W <= line,
                            "how": "the highest P_work (point, and its band's top) over the arm's cells, + 4 W for the 10 Hz peak above a window's mean "
                                   "(E136: +1.8 W burst, +2.8 W sustained on g4k random)"}
    return fc


def text(fc):
    L = ["E190 frozen forecasts (no E190 datum exists). Informed by E136's measured results; blind to every 8,192^3 datum and to card 1's GEMM behaviour.",
         f"law tie (E136's power law, parametrized, at g4k P1 against predictions-e136.json): worst |diff| {fc['law_tie_worst']:.4f}",
         "", "seconds a GEMM: T an op (us), point [band]; t a GEMM (s); X = T600 / T800"]
    for t in FMTS:
        s = fc["speed"][t]
        L.append(f"  {t}: anchor {s['anchor']}; lines a shire-op {s['anchor_lines']} -> {s['e190_lines_32MB']} (L3, fresh)")
        for f in (800, 600):
            T, tt = s[f"T{f}_us"], s[f"t{f}_s"]
            L.append(f"    {f} MHz: T {T['point']:.4f} [{T['band'][0]:.4f}, {T['band'][1]:.4f}] (anchor measured {T['anchor_measured']:.4f}); "
                     f"t {tt['point']:.4f} s [{tt['band'][0]:.4f}, {tt['band'][1]:.4f}]")
        L.append(f"    X {s['X']:.4f}; {s['rate_800_tflops']:.2f} TFLOPS-equivalent at 800, {s['rate_600_tflops']:.2f} at 600")
    L += ["", "cells: arm.format.block: clock MHz; t s; W over idle; P at rest; J over idle; J with the card at rest; die C  (point [band])"]
    for k, c in fc["cells"].items():
        def pb(x, n=2):
            return f"{x['point']:.{n}f} [{x['band'][0]:.{n}f}, {x['band'][1]:.{n}f}]"
        L.append(f"  {k:14s} {c['mhz']['point']:6.1f} MHz; t {pb(c['t_gemm_s'], 4)}; W {pb(c['W_over'])}; rest {pb(c['P_rest_w'])}; "
                 f"J_over {pb(c['J_over'], 3)}; J_rest {pb(c['J_rest'], 3)}; die {pb(c['die_c'], 1)}")
    L += ["", "the ledger v2 arm (REPORTED), card 1 at 600 MHz, 58 C, the frozen seconds: J over idle with heat [band of J over idle]; J total"]
    for t in FMTS:
        g = fc["ledger_arm"][t]
        L.append(f"  {t}: {g['j_over_idle_with_heat']:.3f} J [{g['j_over_idle_band'][0]:.3f}, {g['j_over_idle_band'][1]:.3f}] (W {g['w_over_idle_with_heat']:.2f}); "
                 f"total {g['j_total']:.3f} J [{g['j_total_band'][0]:.3f}, {g['j_total_band'][1]:.3f}]")
    L += ["", "predicted peaks against each arm's line"]
    for arm, p in fc["peaks"].items():
        L.append(f"  arm {arm}: {p['point_w']:.1f} W at the point, {p['band_top_w']:.1f} W at the bands' top, line {p['line_w']:.0f} W: "
                 f"{'UNDER' if p['under_line'] else 'OVER - the plan is refused'}")
    return "\n".join(L) + "\n"


def canon(x):
    return json.loads(json.dumps(x), parse_float=lambda s: round(float(s), 9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    fc = build()
    path = os.path.join(HERE, "forecast-e190.json")
    if a.check:
        old = json.load(open(path))
        same = canon(old) == canon(fc)
        tie = fc["law_tie_worst"] <= 0.011
        under = all(p["under_line"] for p in fc["peaks"].values())
        gw = 0.0                     # given() at each cell's own frozen point reproduces its frozen joules
        for k, c in old["cells"].items():
            arm, t, b = k.split(".")
            g = given(old, arm, t, b, c["t_gemm_s"]["point"], c["P_rest_w"]["point"], c["mhz"]["point"])
            gw = max(gw, abs(g["j_over"] - c["J_over"]["point"]), abs(g["j_rest"] - c["J_rest"]["point"]))
        gok = gw <= 1e-9
        print(f"forecast_e190 --check: recomputed == committed: {same}; law tie {fc['law_tie_worst']:.4f} (<= 0.011: {tie}); peaks under the lines: {under}; "
              f"given() at the points reproduces the frozen J (worst {gw:.1e} J): {gok}")
        print("PASS" if (same and tie and under and gok) else "FAIL")
        sys.exit(0 if (same and tie and under and gok) else 1)
    json.dump(fc, open(path, "w"), indent=1)
    sys.stdout.write(text(fc))


if __name__ == "__main__":
    main()
