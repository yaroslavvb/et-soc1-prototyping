#!/usr/bin/env python3
"""E206 (Q198): the frozen forecasts for the matmul sweep - every point's clock cycles an op and a GEMM, seconds a GEMM, board watts over idle, the
card at rest, and joules a GEMM over idle and with the card at rest, on each arm (A: aifoundry3 card 0 at 600 MHz; B: aifoundry1 card 1 at 600 MHz),
by today's two models, each with a two-sided band. Written before any E206 datum. Standard library only.

    python3 -I -B tools/claims-v3/e206/forecast_e206.py            writes forecast-e206.json and prints forecast-e206.txt (redirect stdout)
    python3 -I -B tools/claims-v3/e206/forecast_e206.py --check    recomputes everything and compares it with the committed JSON (exit 0 = PASS)

LABEL. Not blind to the lab's earlier GEMM data (E136, E146, E107, E37 through the ledger, E190 itself): every input below is committed and pinned.
Blind to every E206 datum (none exists) and to every one of the 95 points never run on any card.

F1, E190'S ROUTE (tools/claims-v3/e190/forecast_e190.py imported unchanged: its anchors, its line-cost law, E136's power law, the ledger v2's idle law):
 1. LINES a shire-op: desk/reuse-e206.json (E136's model unchanged; a new subset function; tied first to E136's g2k and g4k and E190's three shapes).
 2. SECONDS. A gemmL point: T600 = T600(anchor) x law(point's lines) / law(anchor's lines), law = E119's and E126's aifoundry2 fits at 600 MHz on
    the c16s footing (E190's T(f)); anchors E136's g4k (fp32, fp16) and E146's D4 (int8), as E190. A law arm (gemmc1, gemmc8s, gemmc16s): the law's
    own value at the arm's lines (c1, c8s, c16s). One T for both cards (E37: a DRAM-streamed matmul's cycles an op agreed within 0.9% on three
    cards; E190's arm B form). Cycles an op = T600 x 600; cycles a GEMM = ops a minion x T600 x 600; seconds a GEMM = ops a minion x T600.
    BAND (E190's rule): from min(1, every alternative ratio) x 0.97 to max(1, every alternative ratio) x 1.03 of the anchor's T, the alternatives the
    c16s and c16 footings at a 32, 28 and 24 MB L3 (1 = the anchor's own measured time: E190 kept "the extra lines cost nothing" open). A law arm's
    band: its own value x [min(1, c16 / c16s footing) x 0.97, max(1, c16 / c16s) x 1.03]. F1 has no contention term (a subset's line costs are the
    full chip's; its lines are its own footprint's).
 3. WATTS over idle at 600 MHz on aifoundry2: E190's watts_A at 600 MHz - the anchor's measured bursts less the ledger v2's idle law at each run's
    start die, moved to the point's lines by E136's frozen power law with its switching coefficient re-read from the anchor's burst; the data kind by
    E136's kind law (random 'top'; zeros and sparse50 from E107's S; real = zeros + r (random - zeros), E95's r for E101's set). Band: W at the point's
    lines, at the anchor's lines ("no change") and at the 28 and 24 MB lines, +-2 W (a law arm: its own value +-2 W). THE CARD: x kappa, E37's
    DRAM-streamed matmul over aifoundry2 (aifoundry3 8.35519 / 8.78283; card 1 8.86504 / 8.78283), band x [0.95, 1.05] (E190's form). A SUBSET: x shires / 32.
 4. THE CARD AT REST: the ledger's idle law per card (frozen-v2.json, unchanged in ledger v3) at the forecast die of ledger v3's rule 5, 50 C (band
    46-56 C), +-0.5 W.
 5. JOULES a GEMM: over idle W t; with the card at rest (P_rest + W) t; bands the products of the bands' ends.
 6. THE DIE (REPORTED, not scored): arm A E136's burst law carried to aifoundry3, die = 50 + 0.1445 (P_work - 21.5); arm B M10's rise, die = 50 + 0.12 W.
F2, LEDGER V3'S TENSOR TERMS (tools/ledger/ledger_v3.py, landed 50795847, frozen-v3.json sha256 4b43f510...): each GEMM as a ledger load in E190's
 ledger-arm form - tensor ops (minions x ops a minion) by format and kind on the card's own rows (aifoundry3: a3; card 1: c1, a kind priced on a3
 only carried unchanged by ledger v3's carried()); bytes l3_load = n_L3 x 64 / 32 B and dram_load = n_fresh x 64 / 32 B an op a minion (F1's lines),
 rho = tau = 0.5 for random and real data, 0 for zeros - priced by predict_v2load() with every rule on (rule 5's 50 C die and its 1.5 ms a launch; rule
 7 is zero on these pinned cards), the load being one launch of the host's own size (GEMMs a launch = max(1, floor(c x 0.5 / (c t))), c = max(1,
 floor(64,000 / ops a pass)): rgm136's repeatFor()), divided by its GEMMs. J over idle = the ledger's J over idle with its heat (E190's ledger arm);
 J with the card at rest = its j_total. The ledger has no tensor seconds rule: F2's seconds are F1's. sparse50 has no row in the ledger: NOT PRICED.
P0, THE DESIGN'S PLANNING LAW (desk/design-planning-e206.json; REPORTED beside, never scored for a verdict): cycles an op and W over idle by E136's
 line-cost form on aifoundry3's own E105/E107 arms (card 1 x 1.061).
given(): the given-seconds formulas the scorer evaluates (F1: W t and (P_rest + W) t at the measured seconds and rest; F2: the same ledger load at the
 measured seconds and starting die, J with the card at rest = the measured rest x t + the ledger's J over idle with heat).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e190"))
import forecast_e190 as FE  # noqa: E402  (E190's route, unchanged: anchors, the law, E136's power law, the ledger v2's idle law)
sys.path.insert(0, os.path.join(REPO, "tools", "ledger"))
import ledger_v3 as LV3  # noqa: E402  (the load ledger v3 as landed, 50795847)

M136 = FE.M136
FMTS = ("fp32", "fp16", "int8")
ARMS = ("A", "B")
F_MHZ = 600.0
CAPS = ("32MB", "28MB", "24MB")
FOOTINGS = ("c16s", "c16")
CARD = {"A": "aifoundry3", "B": "aifoundry1-c1"}
CARD_TEXT = {"A": "aifoundry3 card 0, 600 MHz pinned (nothing set)", "B": "aifoundry1 card 1, 600 MHz as found (nothing set)"}
E37 = {"aifoundry1-c1": 8.86504, "aifoundry2": 8.78283, "aifoundry3": 8.35519}      # W over the pre-launch idle, E37 (scores-v2.json rows E37)
KAPPA = {"A": E37["aifoundry3"] / E37["aifoundry2"], "B": E37["aifoundry1-c1"] / E37["aifoundry2"]}
KAPPA_BAND = (0.95, 1.05)
T0, T0_BAND = 50.0, (46.0, 56.0)
REST_BAND_W = 0.5
W_WIDEN = 2.0
T_BAND = (0.97, 1.03)
PEAK_MARGIN_W = 4.0
LINE_W = {"A": 65.0, "B": 65.0}
STOP = {"A": {"board_w_above": 70.0, "samples_in_a_row": 3, "die_c_at_or_above": 70.0},
        "B": {"board_w_above": 72.0, "samples_in_a_row": 3, "die_c_at_or_above": 80.0}}
KIND_E136 = {"random": "top", "zeros": "zeros", "sparse50": "sparse50", "real": "real"}
LEDGER_KIND = {("fp32", "random"): "fp32.randn", ("fp16", "random"): "fp16.randn", ("int8", "random"): "int8.full",
               ("fp32", "zeros"): "fp32.zeros", ("fp16", "zeros"): "fp16.zeros", ("int8", "zeros"): "int8.zeros"}
RHO_TAU = {"random": (0.5, 0.5), "zeros": (0.0, 0.0), "real": (0.5, 0.5)}
TENSOR_FLOOR = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}   # cycles an op, A and B resident (E101's resident loop on aifoundry3; E109 R6's rule)
INPUTS = dict(FE.INPUTS)
INPUTS.update({
    "e190_route_code": "tools/claims-v3/e190/forecast_e190.py",
    "e190_forecast": "tools/claims-v3/e190/forecast-e190.json",
    "e107_scored": "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json",
    "e107_items": "docs/reports/data/2026-11-01-e107-gemm-placement/e107.json",
    "e95_scored": "docs/reports/data/2026-11-01-e95-real-tensors-energy/scored.json",
    "e101_real_set": "tools/claims-v3/kinds/e101_common.py",
    "ledger_v3_code": "tools/ledger/ledger_v3.py",
    "ledger_v3_frozen": "tools/ledger/frozen-v3.json",
    "ledger_estimate": "workloads/ledger/ledger_estimate.py",
    "energy_catalogue": "docs/reports/data/2026-09-23-energy-manual/catalogue.json",
    "e206_points": "tools/claims-v3/e206/points-e206.json",
    "e206_reuse": "tools/claims-v3/e206/desk/reuse-e206.json",
    "e206_design_planning": "tools/claims-v3/e206/desk/design-planning-e206.json",
})


def sha(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(REPO, rel)))


PTS = load(INPUTS["e206_points"])
REUSE = load(INPUTS["e206_reuse"])
DES = load(INPUTS["e206_design_planning"])
F3 = LV3.load_frozen()
HEAT136 = load(INPUTS["e136_predictions"])["heat"]
K_RISE = FE.FL["constants"]["k_rise_c_per_w"]["value"]


def lines(p, cap="32MB"):
    if p["shape"]["kind"] == "law arm":
        a = REUSE["law_arms"][p["arm"]]
        return a["n_L3"], a["n_fresh"]
    MB, NB, KB = p["shape"]["blocks"]
    v = REUSE["shapes"][f"gemmL{MB}x{NB}x{KB}@{p['shire_mask']}"]["lines"][cap]
    return v["n_L3"], v["n_fresh"]


# ------------------------------------------------------------------ F1: seconds and cycles
def speed(p):
    t = p["format"]
    ops = p["ops_per_minion_per_gemm"]
    if p["shape"]["kind"] == "law arm":
        nl, nf = lines(p)
        T6 = FE.law_T(nl, nf, t, F_MHZ, "c16s")
        ratios = {"c16 footing": FE.law_T(nl, nf, t, F_MHZ, "c16") / T6}
        lo, hi = T6 * min(1.0, min(ratios.values())) * T_BAND[0], T6 * max(1.0, max(ratios.values())) * T_BAND[1]
        route = f"the law's own value at the arm's lines ({nl:.0f}, {nf:.0f}): E119's and E126's aifoundry2 fits at 600 MHz"
        anchor = None
    else:
        a = FE.anchor(t)
        ratios = {f"{ft}@{cap}": FE.law_T(*lines(p, cap), t, F_MHZ, ft) / FE.law_T(a["lines"][0], a["lines"][1], t, F_MHZ, ft)
                  for ft in FOOTINGS for cap in CAPS}
        T6 = a["T600"] * ratios["c16s@32MB"]
        lo = a["T600"] * min(1.0, min(ratios.values())) * T_BAND[0]
        hi = a["T600"] * max(1.0, max(ratios.values())) * T_BAND[1]
        route = f"T600(anchor) x law(point) / law(anchor); anchor {a['name']}, lines {list(a['lines'])}, T600 {a['T600']:.4f} us"
        anchor = {"name": a["name"], "lines": list(a["lines"]), "T600_us": a["T600"]}
    cyc = lambda x: x * F_MHZ  # noqa: E731
    return {"route": route, "anchor": anchor, "ratios": ratios,
            "T600_us": {"point": T6, "band": [lo, hi]},
            "cycles_per_op": {"point": cyc(T6), "band": [cyc(lo), cyc(hi)]},
            "cycles_gemm": {"point": ops * cyc(T6), "band": [ops * cyc(lo), ops * cyc(hi)]},
            "t_gemm_s": {"point": ops * T6 * 1e-6, "band": [ops * lo * 1e-6, ops * hi * 1e-6]}}


# ------------------------------------------------------------------ F1: watts over idle at 600 MHz on aifoundry2 (E190's watts_A at 600 MHz)
def watts600(p):
    t = p["format"]
    kind = KIND_E136[p["kind"]]
    a = FE.anchor(t)
    Pm = sum(b[0] for b in a["bursts"]) / len(a["bursts"])
    Wm = sum(b[0] - FE.idle("aifoundry2", b[1]) for b in a["bursts"]) / len(a["bursts"])
    rm = 600.0 * a["T600"] / (800.0 * a["T800"])
    c_meas = (Pm - M136.B[800]) / (M136.SF[800] * rm)
    c_law_a = FE.c600_law(a["lines"][0], a["lines"][1], t)

    def W_at(nl, nf):
        cE = c_meas * FE.c600_law(nl, nf, t, kind) / c_law_a
        # P_levels(cE, T600, T800)[600] = B(600) + cE s(600) (600 T600) / (600 T600): the time cancels at 600 MHz
        return Wm + (M136.B[600] + cE * M136.SF[600]) - Pm, cE
    W, cE = W_at(*lines(p))
    alts = {"point": W}
    if p["shape"]["kind"] != "law arm":
        alts["no change (the anchor's lines)"] = W_at(*a["lines"])[0]
        for cap in ("28MB", "24MB"):
            alts[f"lines at {cap}"] = W_at(*lines(p, cap))[0]
    band = [min(alts.values()) - W_WIDEN, max(alts.values()) + W_WIDEN]
    return {"point": W, "band": band, "alternatives": alts, "c600_point": cE, "anchor_burst_mean_w": Pm, "anchor_w_over_idle_mean": Wm,
            "c_meas": c_meas, "c_law_anchor": c_law_a, "kind_law": kind}


def gemms_a_launch(p, t_gemm):
    """rgm136's repeatFor(): a calibration launch of c = max(1, 64,000 // ops a pass) passes, then launches of max(1, floor(c x 0.5 / wall)) passes"""
    c = max(1, 64000 // p["ops_per_minion_per_gemm"])
    return max(1, int(c * 0.5 / max(c * t_gemm, 1e-4)))


# ------------------------------------------------------------------ F2: ledger v3's tensor terms
def ledger_load(p, arm, t_gemm, g, die_c=None):
    t, kind = p["format"], p["kind"]
    n_ops = p["minions"] * p["ops_per_minion_per_gemm"] * g
    nl, nf = lines(p)
    if kind == "real":
        tiles = PTS["real_tiles"][t]
        tensor = [{"format": t, "kind": f"{t}.real2:{x}", "ops": n_ops / len(tiles)} for x in tiles]
    else:
        tensor = [{"format": t, "kind": LEDGER_KIND[(t, kind)], "ops": n_ops}]
    rho, tau = RHO_TAU[kind]
    ld = {"card": CARD[arm], "f_mhz": F_MHZ, "seconds": t_gemm * g, "work_units": g, "work_unit": "GEMM", "tensor": tensor,
          "bytes": [{"path": "l3_load", "bytes": nl * 64.0 / 32.0 * n_ops, "rho": rho, "tau": tau, "what": "lines a shire-op from the L3, x 64 B / 32 minions"},
                    {"path": "dram_load", "bytes": nf * 64.0 / 32.0 * n_ops, "rho": rho, "tau": tau, "what": "fresh lines a shire-op, x 64 B / 32 minions"}]}
    ld["die_start_c"] = T0 if die_c is None else die_c
    return ld


def f2_price(p, arm, t_gemm, die_c=None):
    if p["kind"] == "sparse50":
        return {"priced": False, "why": "the ledger (v2's kinds, unchanged in v3) has no sparse50 tensor row: NOT PRICED"}
    g = gemms_a_launch(p, t_gemm)
    o = LV3.predict_v2load(ledger_load(p, arm, t_gemm, g, die_c), F3, rules=None, die_c=die_c)
    pr = o["v2_prediction"]
    tens = sum(v["j"] for k, v in pr["terms"].items() if k.startswith("tensor:")) / g
    l3 = sum(v["j"] for k, v in pr["terms"].items() if k.startswith("bytes:l3_load")) / g
    dr = sum(v["j"] for k, v in pr["terms"].items() if k.startswith("bytes:dram_load")) / g
    jo = pr["j_over_idle_with_heat"] / g
    jo_b = [pr["w_over_idle_with_heat_band"][0] * pr["seconds"] / g, pr["w_over_idle_with_heat_band"][1] * pr["seconds"] / g]
    return {"priced": True, "gemms_a_launch": g, "die_start_c": o["die_start_c"], "rules": o["rules"],
            "J_over": {"point": jo, "band": jo_b}, "J_rest": {"point": o["j_total"] / g, "band": [o["j_total_band"][0] / g, o["j_total_band"][1] / g]},
            "W_over": {"point": jo / t_gemm, "band": [jo_b[0] / t_gemm, jo_b[1] / t_gemm]},
            "parts_j": {"tensor": tens, "l3_load": l3, "dram_load": dr, "heat": pr["heat"]["j"] / g, "rest": (o["j_total"] - pr["j_over_idle_with_heat"]) / g},
            "wall_s_a_gemm": o["wall_s"] / g}


# ------------------------------------------------------------------ the arms
def rest(arm):
    card = CARD[arm]
    pr = FE.idle(card, T0)
    lo = min(FE.idle(card, x) for x in T0_BAND) - REST_BAND_W
    hi = max(FE.idle(card, x) for x in T0_BAND) + REST_BAND_W
    return {"point": pr, "band": [lo, hi]}


def arm_cell(p, arm, sp, w6, pr):
    k = KAPPA[arm]
    frac = p["shires"] / 32.0
    W = k * w6["point"] * frac
    Wb = [w6["band"][0] * KAPPA_BAND[0] * frac, w6["band"][1] * KAPPA_BAND[1] * frac]
    t, tb = sp["t_gemm_s"]["point"], sp["t_gemm_s"]["band"]
    Pw = {"point": pr["point"] + W, "band": [pr["band"][0] + Wb[0], pr["band"][1] + Wb[1]]}
    die = T0 + (HEAT136["k_burst_c_per_w"] * (Pw["point"] - HEAT136["P_idle_w"]) if arm == "A" else K_RISE * W)
    f1 = {"W_over": {"point": W, "band": Wb}, "P_rest_w": pr, "P_work_w": Pw,
          "J_over": {"point": W * t, "band": [Wb[0] * tb[0], Wb[1] * tb[1]]},
          "J_rest": {"point": (pr["point"] + W) * t, "band": [(pr["band"][0] + Wb[0]) * tb[0], (pr["band"][1] + Wb[1]) * tb[1]]},
          "die_c_reported": die, "peak_point_w": Pw["point"] + PEAK_MARGIN_W, "peak_band_top_w": Pw["band"][1] + PEAK_MARGIN_W,
          "kappa": k, "shire_share": frac}
    f2 = f2_price(p, arm, t)
    dp = DES["points"][p["id"]]
    p0 = {"label": "REPORTED: the design's planning law (aifoundry3's own arms; card 1 x 1.061), never scored for a verdict",
          "cycles_per_op": dp["planning_cycles_per_op"], "W_over": dp["arms"][arm]["w_over_idle"],
          "J_over": dp["arms"][arm]["w_over_idle"] * p["ops_per_minion_per_gemm"] * dp["planning_cycles_per_op"] / (F_MHZ * 1e6)}
    return {"card": CARD_TEXT[arm], "F1": f1, "F2": f2, "P0": p0}


def build():
    fc = {"experiment": "E206", "request": "Q198",
          "what": "frozen before any E206 datum: F1 (E190's route widened to every shape and both cards) and F2 (ledger v3's tensor terms), each with "
                  "two-sided bands; P0 (the design's planning law) REPORTED beside",
          "label": "not blind to the lab's committed GEMM data (E136, E146, E107, E37, E190: every input pinned); blind to every E206 datum",
          "inputs": INPUTS, "inputs_sha256": {k: sha(v) for k, v in INPUTS.items()}, "law_tie_worst_e136": FE.law_tie(),
          "constants": {"f_mhz": F_MHZ, "kappa_e37": KAPPA, "kappa_band": KAPPA_BAND, "e37_w_over_idle": E37, "t0_c": T0, "t0_band_c": T0_BAND,
                        "rest_band_w": REST_BAND_W, "w_widen_w": W_WIDEN, "t_band": T_BAND, "peak_margin_w": PEAK_MARGIN_W, "line_w": LINE_W,
                        "stop": STOP, "k_burst_c_per_w_e136": HEAT136["k_burst_c_per_w"], "k_rise_c_per_w_m10": K_RISE,
                        "tensor_floor_cycles_per_op": TENSOR_FLOOR, "rho_tau": RHO_TAU, "ledger_kind": {f"{a}.{b}": v for (a, b), v in LEDGER_KIND.items()},
                        "ledger_rules": sorted(LV3.ALL), "frozen_v3_sha256": LV3.sha256_file(LV3.FROZEN_V3)},
          "anchors": {t: {"name": FE.anchor(t)["name"], "lines": list(FE.anchor(t)["lines"]), "T600_us": FE.anchor(t)["T600"],
                          "T800_us": FE.anchor(t)["T800"], "bursts": FE.anchor(t)["bursts"]} for t in FMTS},
          "rest": {a: rest(a) for a in ARMS}, "points": {}, "peaks": {}}
    for p in PTS["points"]:
        sp = speed(p)
        w6 = watts600(p)
        rec = {"name": p["name"], "family": p["family"], "format": p["format"], "kind": p["kind"], "arm": p["arm"], "shire_mask": p["shire_mask"],
               "shires": p["shires"], "minions": p["minions"], "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"], "on_arm": p["on_arm"],
               "lines": {cap: list(lines(p, cap)) for cap in CAPS}, "F1_speed": sp, "F1_W600_aifoundry2": w6,
               "reported_columns": {"sim_steps_per_minion_per_gemm": DES["points"][p["id"]]["sim_steps_per_minion_per_gemm"],
                                    "tensor_floor_cycles_gemm": TENSOR_FLOOR[p["format"]] * p["ops_per_minion_per_gemm"]},
               "arms": {}}
        for arm in ARMS:
            if p["on_arm"][arm]:
                rec["arms"][arm] = arm_cell(p, arm, sp, w6, fc["rest"][arm])
        fc["points"][p["id"]] = rec
    for arm in ARMS:
        cells = [(pid, r["arms"][arm]["F1"]) for pid, r in fc["points"].items() if arm in r["arms"]]
        top_pt = max(cells, key=lambda x: x[1]["peak_point_w"])
        top_bd = max(cells, key=lambda x: x[1]["peak_band_top_w"])
        over_pt = [pid for pid, c in cells if c["peak_point_w"] > LINE_W[arm]]
        over_bd = [pid for pid, c in cells if c["peak_band_top_w"] > LINE_W[arm]]
        fc["peaks"][arm] = {"line_w": LINE_W[arm], "stop": STOP[arm], "highest_point_peak": {"id": top_pt[0], "w": top_pt[1]["peak_point_w"]},
                            "highest_band_top_peak": {"id": top_bd[0], "w": top_bd[1]["peak_band_top_w"]},
                            "points_over_line_at_point": over_pt, "points_over_line_at_band_top": over_bd,
                            "under_line_at_point": not over_pt,
                            "how": "P_work = the card at rest + W over idle, + 4 W for the 10 Hz peak above a window's mean (E190's margin); the point's, "
                                   "and its band's top (the rest band's top + W's band top)"}
    return fc


# ------------------------------------------------------------------ given(): what the scorer evaluates at measured values
def given_f1(fc, arm, pid, t_meas, p_rest_meas):
    W = fc["points"][pid]["arms"][arm]["F1"]["W_over"]["point"]
    return {"W_over": W, "j_over": W * t_meas, "j_rest": (p_rest_meas + W) * t_meas}


def given_f2(arm, pid, t_meas, T0_meas, p_rest_meas):
    p = next(x for x in PTS["points"] if x["id"] == pid)
    o = f2_price(p, arm, t_meas, die_c=T0_meas)
    if not o["priced"]:
        return None
    return {"j_over": o["J_over"]["point"], "j_rest": p_rest_meas * t_meas + o["J_over"]["point"], "ledger_j_total": o["J_rest"]["point"]}


def text(fc):
    L = ["E206 frozen forecasts (no E206 datum exists): F1 = E190's route widened; F2 = ledger v3's tensor terms (seconds F1's); P0 REPORTED.",
         f"E136's power law parametrized, at g4k P1 against predictions-e136.json: worst |diff| {fc['law_tie_worst_e136']:.4f}",
         f"the card at rest (the ledger's idle law at {T0:.0f} C, band {T0_BAND[0]:.0f}-{T0_BAND[1]:.0f} C, +-0.5 W): "
         + "; ".join(f"arm {a} {fc['rest'][a]['point']:.2f} W [{fc['rest'][a]['band'][0]:.2f}, {fc['rest'][a]['band'][1]:.2f}]" for a in ARMS),
         f"kappa (E37): A {KAPPA['A']:.5f}, B {KAPPA['B']:.5f}; band x [0.95, 1.05]",
         "", "per point: id name | F1 cycles an op [band] | F1 seconds a GEMM [band] | per arm: F1 W over idle; F1 J over idle [band]; F1 J with the card "
             "at rest [band]; F2 J over idle [band]; F2 J with the card at rest; peak (point, band top)"]

    def pb(x, n=3, s=1.0):
        return f"{x['point'] * s:.{n}g} [{x['band'][0] * s:.{n}g}, {x['band'][1] * s:.{n}g}]"
    for pid, r in fc["points"].items():
        sp = r["F1_speed"]
        L.append(f"{pid} {r['name']:34s} cyc/op {pb(sp['cycles_per_op'], 5)} | t {pb(sp['t_gemm_s'], 4)} s | lines32 ({r['lines']['32MB'][0]:.1f}, "
                 f"{r['lines']['32MB'][1]:.1f})")
        for arm, c in r["arms"].items():
            f1, f2 = c["F1"], c["F2"]
            s2 = (f"F2 J_over {pb(f2['J_over'], 4)}; J_rest {f2['J_rest']['point']:.4g}" if f2["priced"] else "F2 NOT PRICED")
            L.append(f"    {arm}: F1 W {f1['W_over']['point']:.2f} [{f1['W_over']['band'][0]:.2f}, {f1['W_over']['band'][1]:.2f}]; J_over {pb(f1['J_over'], 4)}; "
                     f"J_rest {pb(f1['J_rest'], 4)}; {s2}; peak {f1['peak_point_w']:.1f} / {f1['peak_band_top_w']:.1f} W")
    L += ["", "predicted peaks (P_work + 4 W) against each arm's line"]
    for arm, p in fc["peaks"].items():
        L.append(f"  arm {arm}: highest at the point {p['highest_point_peak']['w']:.1f} W ({p['highest_point_peak']['id']}), at the band's top "
                 f"{p['highest_band_top_peak']['w']:.1f} W ({p['highest_band_top_peak']['id']}); line {p['line_w']:.0f} W; over the line at the point: "
                 f"{p['points_over_line_at_point'] or 'none'}; at the band's top: {len(p['points_over_line_at_band_top'])} points")
    return "\n".join(L) + "\n"


def canon(x):
    return json.loads(json.dumps(x), parse_float=lambda s: round(float(s), 9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    fc = build()
    path = os.path.join(HERE, "forecast-e206.json")
    if a.check:
        old = json.load(open(path))
        same = canon(old) == canon(fc)
        tie = fc["law_tie_worst_e136"] <= 0.011
        under = all(p["under_line_at_point"] for p in fc["peaks"].values())
        gw = 0.0
        for pid, r in old["points"].items():
            for arm, c in r["arms"].items():
                g = given_f1(old, arm, pid, r["F1_speed"]["t_gemm_s"]["point"], c["F1"]["P_rest_w"]["point"])
                gw = max(gw, abs(g["j_over"] - c["F1"]["J_over"]["point"]), abs(g["j_rest"] - c["F1"]["J_rest"]["point"]))
        g2 = 0.0
        for pid, r in old["points"].items():
            for arm, c in r["arms"].items():
                if c["F2"]["priced"]:
                    g = given_f2(arm, pid, r["F1_speed"]["t_gemm_s"]["point"], T0, c["F1"]["P_rest_w"]["point"])
                    g2 = max(g2, abs(g["j_over"] - c["F2"]["J_over"]["point"]) / c["F2"]["J_over"]["point"])
        gok = gw <= 1e-9 and g2 <= 1e-12
        print(f"forecast_e206 --check: recomputed == committed: {same}; law tie {fc['law_tie_worst_e136']:.4f} (<= 0.011: {tie}); every point's peak "
              f"under its arm's line at the point: {under}; given() at the points reproduces the frozen J (F1 worst {gw:.1e} J, F2 worst {g2:.1e} relative): {gok}")
        print("PASS" if (same and tie and under and gok) else "FAIL")
        sys.exit(0 if (same and tie and under and gok) else 1)
    json.dump(fc, open(path, "w"), indent=1)
    sys.stdout.write(text(fc))


if __name__ == "__main__":
    main()
