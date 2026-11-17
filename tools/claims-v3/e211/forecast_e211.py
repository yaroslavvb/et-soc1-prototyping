#!/usr/bin/env python3
"""E211 (Q204): THE FROZEN FORECASTS of the second kernel, made before any E211 datum by committed code from committed inputs only. Desk.

    python3 -I -B tools/claims-v3/e211/forecast_e211.py            writes forecast-e211.json, forecast-e211.csv and forecast-e211.txt here
    python3 -I -B tools/claims-v3/e211/forecast_e211.py --check    re-makes all three in memory and compares them byte for byte (exit 0 = PASS)

THE INPUTS (every one pinned by sha256 below and recorded in the output; the run stops on any difference):
  MM1-v1 as landed (tools/matmul/mm1/v1 at 25d2e74e): mm1_core.py, mm1_v1.py, kinds_v1.py, out/mm1_v1_params.json (the freeze line's files);
  E211's desk map (desk/map-e211.json, made by desk/map_e211.py) and its points (points-e211.json);
  E206's registered route for F1 and F2 (tools/claims-v3/e206/forecast_e206.py, which imports E190's route and ledger v3), every one of its 33
    files checked first against MM1-v1's route record (out/f1f2_route.json);
  E101's committed one-block measurements of cooperation (docs/reports/data/2026-11-01-e101-real-matmul/e101.json: gemm1 and gemmnc1, fp32
    random, aifoundry3 at 600 MHz) for family C's rule.
THE CARD: aifoundry3 card 0 at its pinned 600 MHz, 0.522 V (MM1-v1's blind-day footing), the full chip (1,024 minions).
THE FORECASTS, per point (every number a forecast of code; desk):
  MM1   MM1-v1 as landed, its frozen equations and constants unchanged, with the op classes of the point's walk from the desk map in place of its
        closed form (the map's Q0 and Q1, and MM1-v1's frozen stride rule 'r1' carried literally: B's second-use retention x zeta, and piF0 on
        B's first-use fresh stream, where NB is a power of two >= 4 and the footprint passes 32 MB - in BOTH walks, since the term is tied to NB
        and to B's halves, which keep their meaning in rgm211's walk). Cycles an op (the wall: the slowest minion; the counter's mean), seconds a
        GEMM, W over idle (MM1-v1's affine W = A + B / t_op), J over idle, J with the card at rest by MM1-v1's rest law (REPORTED), transistor
        switches (counted, estimated; never scorable), the timing simulation's two columns.
  MM1-S THE SHARING-AWARE RULE (critic-kernel2 fix 1): MM1 with A's fresh lines a shire-op priced twice (an A tile is read by 4 shires, a B tile
        by 8, and MM1-v1's per-shire-line fresh price was fitted where fresh lines were mostly B's: per DRAM line, an A line a shire-op costs two B
        lines); time, awake terms and every other line as MM1's.
  MM1cf MM1-v1 as frozen (its closed-form map) at the twins (gemmL points): REPORTED beside, never scored.
  F1    E190's route as E206 registered it, run unchanged, with the point's walk's strict lines from the desk map (E136's convention, 32/28/24 MB).
  F2    ledger v3's tensor terms through E206's route (F1's seconds; the walk's strict lines as bytes).
  NC    THE CHIP-LINES NULL (critic-kernel2 fix 1): F1's route with every fresh-line count, the point's and the anchor's, replaced by its chip
        level equivalent n_fresh_chip = n_fresh + the A fresh lines a shire-op (each fresh A line counted twice: the chip's DRAM lines a step
        over four), so the cycles follow the chip's DRAM traffic; time only.
  N0    THE NO-WALK NULL: rgm211 = rgm136 at every shape (its ratio 1; its absolute values MM1's at the twin).
  family C (gemmLnc): C0 (MM1-v1 literally: no term for the load mode, so gemmLnc = its twin), C1 THE REGISTERED RULE (E101's one-block
        measurements carried: the wall x the rate ratio, the counter's mean x the counter ratio - so the wall over the mean moves by their ratio,
        the cooperation term's rho rule - and E101's extra J over idle a minion-op added to MM1's B), C2 mm-kernel2's draft rule (REPORTED: time
        unchanged, +832 L2 lines a shire-op at b2 + d2 phi).
  ratios per W pair (rgm211 / rgm136): the wall cycles an op by MM1, F1, NC, N0 and the four stride readings (literal; no stride term; zeta on
        both halves; the stride on rgm136's walk only); the counter's mean by MM1; J over idle a GEMM by MM1, MM1-S, F1, F2.
MM1-v2: not in this file unless landed when it was made (see "mm1_v2" in the output).
SPDX-License-Identifier: Apache-2.0
"""
import copy
import csv
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V1 = "tools/matmul/mm1/v1"
E101 = "docs/reports/data/2026-11-01-e101-real-matmul/e101.json"
PINS = {
    f"{V1}/mm1_core.py": "3e6ff68dfe4f7eb7e2af5873a8b6df52823cc5daa95066d8292d827ada0d84aa",
    f"{V1}/mm1_v1.py": "6bed4a5b2b441b4464a4c320cb0b5ecb09f42aa1403ff8fb25e705cf5a680a52",
    f"{V1}/kinds_v1.py": "29728e43ce3a17ad8cdfbe8a60ba12f4a5a9aa73fb603b71b62b9b4e7d742e6a",
    f"{V1}/out/mm1_v1_params.json": "4e97654ea01e293bc61fab0fa73e8c25128af574a602e7384a14683d3b208408",
    f"{V1}/out/f1f2_route.json": "033ffbadaf46acc985047e52dea142a4393d990c0d2d2de988e149853c8c203f",
    "tools/claims-v3/e206/forecast_e206.py": "d46e2bc6711da556cde4fdc9e3a35103b3d7fe41b818819e40bd80877f1754ed",
    E101: "8d344fc858cfc4b7dcd84cdd290ee33765408bc3fc33fd28f7797a8f4ff3b135",
}
OWN = {"map": "tools/claims-v3/e211/desk/map-e211.json", "points": "tools/claims-v3/e211/points-e211.json"}
OUT_JSON = os.path.join(HERE, "forecast-e211.json")
OUT_CSV = os.path.join(HERE, "forecast-e211.csv")
OUT_TXT = os.path.join(HERE, "forecast-e211.txt")
CARD, F_MHZ, V, MASK, N = "aifoundry3 card 0", 600.0, 0.522, "0xffffffff", 1024
REST_HIGH_W, PLAN_K, PLAN_PLUS_W = 26.0, 1.10, 1.0      # MM1-v1's blind-day planning peak: 26.0 W high-side rest + 1.10 x W over idle + 1 W
LOW_W = 3.0
ANCHOR_SHAPE = {"fp32": "4x8x8", "fp16": "4x8x8", "int8": "4x8x4"}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_pins():
    for rel, want in PINS.items():
        got = sha_rel(rel)
        if got != want:
            sys.exit(f"forecast_e211: REFUSED, {rel} is {got}, pinned {want}")
    route = json.load(open(os.path.join(REPO, V1, "out", "f1f2_route.json")))["route"]
    bad = [r["path"] for r in route if sha_rel(r["path"]) != r["sha256"]]
    if bad:
        sys.exit(f"forecast_e211: REFUSED, F1/F2's route differs from MM1-v1's record at {bad}")
    return len(route)


N_ROUTE = check_pins()
sys.path.insert(0, os.path.join(REPO, V1))
import mm1_core as C  # noqa: E402
import mm1_v1 as M1  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e206"))
import forecast_e206 as F  # noqa: E402
FE = F.FE

PARAMS = json.load(open(os.path.join(REPO, V1, "out", "mm1_v1_params.json")))
MAP = json.load(open(os.path.join(REPO, OWN["map"])))
PTS = json.load(open(os.path.join(REPO, OWN["points"])))
E101J = json.load(open(os.path.join(REPO, E101)))["items"]


def r(x, n=6):
    if x is None:
        return None
    return float(f"{float(x):.{n}g}")


# ------------------------------------------------------------------ MM1-v1 through the desk map
class MapShape:
    """a gemmL point's map skeleton for MM1-v1's Model: the desk map's op classes in place of the closed form (full chip). variant: 'r1' (MM1-v1's
    frozen rule), 'none' (no stride term), 'both' (zeta on both halves' B)."""

    def __init__(self, sh, walk, variant="r1"):
        MB, NB, KB = (int(x) for x in sh.split("x"))
        self.arm = f"map:{walk}:{sh}:{variant}"
        self.mi = C.mask_info(MASK)
        self.blocks = (MB, NB, KB)
        self.kernel = "gemmL"
        self.masked_map = False
        self.F = self.F_full = C.footprint(MB, NB, KB)
        self.p2 = C.is_pow2(NB) and NB >= 4
        self.ops = 64 * MB * NB * KB
        lg = MAP["shapes"][sh][walk]["mm1v1_logistic"]
        assert lg["r1_rule_applies"] == (self.p2 and self.F > 32.0)
        self.q = {k: [list(map(float, row)) for row in lg[k]] for k in ("Q0", "Q1", "Q0z", "Q1z")}
        self.variant = variant
        self.applies = lg["r1_rule_applies"]

    def Qhalves(self, x50, s, zeta=1.0, rule="v1"):
        th = PARAMS["time"]["theta"]
        assert rule == "r1" and (x50, s, zeta) == (th["x50"], th["s"], th["zeta"]), "the map was made with MM1-v1's frozen retention"
        import numpy as np
        q = {k: np.array(v) for k, v in self.q.items()}
        if self.variant == "none" or not self.applies:
            return q["Q0"], q["Q1"]
        if self.variant == "both":
            return q["Q0z"], q["Q1z"]
        return q["Q0"], q["Q1z"]


def model(piF0=None):
    P = copy.deepcopy(PARAMS)
    if piF0 is not None:
        P["time"]["theta"]["piF0"] = piF0
    return M1.Model(P)


M_FROZEN = model()
M_NOPI = model(0.0)


def mm1_on_map(sh, walk, fmt, variant="r1", m=None):
    m = m or (M_NOPI if variant == "none" else M_FROZEN)
    shp = MapShape(sh, walk, variant)
    m._shapes[(shp.arm, MASK)] = shp
    return m.predict(CARD, shp.arm, fmt, "random", MASK, F_MHZ, V)


def sharing_aware(pred, sh, walk):
    """MM1-S: A's fresh lines a shire-op priced twice; returns (B_S in W us, W_S, J_S)"""
    E = PARAMS["energy"]["theta"]
    lg = MAP["shapes"][sh][walk]["mm1v1_logistic"]["frozen_rule_r1"]
    nFA = lg["A_lines_L2_L3_F_per_shire_op"][2]
    s = (V / 0.517) ** 2
    add = N * s * 1e-12 * nFA / 32.0 * (E["bF"] + E["dF"] * pred["phi"]) * 1e6
    A = pred["W_affine"]["A_W"]
    B = pred["W_affine"]["B_W_us"] + add
    t_us = pred["T_op_us"]
    W = A + B / t_us
    return {"A_W": A, "B_W_us": B, "W_over_idle": W, "J_over_idle_per_gemm": W * pred["seconds_per_gemm"], "A_fresh_lines_per_shire_op": nFA,
            "B_added_W_us": add}


# ------------------------------------------------------------------ F1, F2 and the chip-lines null through E206's route
def reuse_table(walk, chip=False):
    t = {"shapes": {}, "law_arms": F.REUSE["law_arms"]}
    for sh, w in MAP["shapes"].items():
        lines = {}
        for cap, v in w[walk]["strict_lines"].items():
            nf = v["n_fresh_chip"] if chip else v["n_fresh"]
            lines[cap] = {"l2_missing": v["l2_missing"], "n_L3": v["n_L3"], "n_fresh": nf}
        t["shapes"][f"gemmL{sh}@{MASK}"] = {"lines": lines}
    return t


REUSE = {"mn": reuse_table("mn"), "nm": reuse_table("nm")}


def f_point(p, sh, fmt):
    MB, NB, KB = (int(x) for x in sh.split("x"))
    return {"id": p, "name": f"gemmL{sh}.{fmt}.random", "shape": {"kind": "gemmL", "blocks": [MB, NB, KB]}, "format": fmt, "kind": "random",
            "arm": f"gemmL{sh}", "shire_mask": MASK, "shires": 32, "minions": N, "ops_per_minion_per_gemm": 64 * MB * NB * KB}


def f1f2(pid, sh, walk, fmt):
    F.REUSE = REUSE[walk]
    pt = f_point(pid, sh, fmt)
    sp = F.speed(pt)
    w6 = F.watts600(pt)
    rest = F.rest("A")
    k = F.KAPPA["A"]
    W = k * w6["point"]
    Wb = [w6["band"][0] * F.KAPPA_BAND[0], w6["band"][1] * F.KAPPA_BAND[1]]
    t, tb = sp["t_gemm_s"]["point"], sp["t_gemm_s"]["band"]
    f2 = F.f2_price(pt, "A", t)
    out = {"F1_cycles_per_op": sp["cycles_per_op"]["point"], "F1_cycles_per_op_band": sp["cycles_per_op"]["band"], "F1_seconds_per_gemm": t,
           "F1_seconds_band": tb, "F1_W_over_idle": W, "F1_W_band": Wb, "F1_J_over_idle_per_gemm": W * t, "F1_J_over_band": [Wb[0] * tb[0], Wb[1] * tb[1]],
           "F1_P_rest_W": rest["point"], "F1_J_at_rest_per_gemm": (rest["point"] + W) * t, "F1_peak_point_W": rest["point"] + W + F.PEAK_MARGIN_W,
           "F1_lines_32MB": list(F.lines(pt))}
    if f2["priced"]:
        out.update({"F2_J_over_idle_per_gemm": f2["J_over"]["point"], "F2_J_over_band": f2["J_over"]["band"], "F2_W_over_idle": f2["W_over"]["point"],
                    "F2_J_at_rest_per_gemm": f2["J_rest"]["point"], "F2_gemms_a_launch": f2["gemms_a_launch"]})
    else:
        out["F2"] = f2["why"]
    # the chip-lines null: F1's law at the chip-level fresh lines, the point's and the anchor's
    a = FE.anchor(fmt)
    an = MAP["anchors"][ANCHOR_SHAPE[fmt]]["mn"]["strict_lines"]["32MB"]
    nfa_chip = a["lines"][1] + (an["n_fresh_chip"] - an["n_fresh"])
    v = MAP["shapes"][sh][walk]["strict_lines"]["32MB"]
    T6 = a["T600"] * FE.law_T(v["n_L3"], v["n_fresh_chip"], fmt, F_MHZ, "c16s") / FE.law_T(a["lines"][0], nfa_chip, fmt, F_MHZ, "c16s")
    out.update({"NC_cycles_per_op": T6 * F_MHZ, "NC_seconds_per_gemm": pt["ops_per_minion_per_gemm"] * T6 * 1e-6,
                "NC_lines_32MB": [v["n_L3"], v["n_fresh_chip"]], "NC_anchor_lines": [a["lines"][0], nfa_chip]})
    return out


# ------------------------------------------------------------------ family C: E101's cooperation, carried
def e101_rule():
    g, n = E101J["gemm1.fp32.randn"], E101J["gemmnc1.fp32.randn"]
    cyc = json.load(open(os.path.join(REPO, E101)))["cycles_per_op"]
    r_wall = g["rate"]["mean"] / n["rate"]["mean"]
    r_mean = cyc["gemmnc1:fp32"] / cyc["gemm1:fp32"]
    dE = (n["pj_op_S"]["mean"] - g["pj_op_S"]["mean"]) * 1e-12
    return {"source": E101 + " items gemm1.fp32.randn, gemmnc1.fp32.randn (rate, pj_op_S) and cycles_per_op (gemm1:fp32, gemmnc1:fp32); "
                      "aifoundry3 card 0, 600 MHz; measured, one block, not in MM1-v1's fit",
            "rate_coop": g["rate"]["mean"], "rate_nc": n["rate"]["mean"], "r_wall": r_wall,
            "cycles_mean_coop": cyc["gemm1:fp32"], "cycles_mean_nc": cyc["gemmnc1:fp32"], "r_mean": r_mean, "rho_factor": r_wall / r_mean,
            "pj_op_S_coop": g["pj_op_S"]["mean"], "pj_op_S_nc": n["pj_op_S"]["mean"], "dE_J_per_minion_op": dE,
            "W_over_idle_coop": g["S"]["mean"], "W_over_idle_nc": n["S"]["mean"]}


E101R = e101_rule()


def family_c(twin):
    """C1 and C2 from the twin's MM1 forecast (on rgm136's walk)"""
    E = PARAMS["energy"]["theta"]
    s = (V / 0.517) ** 2
    A, B = twin["W_affine"]["A_W"], twin["W_affine"]["B_W_us"]
    t_us, tg = twin["T_op_us"], twin["seconds_per_gemm"]
    c1t = t_us * E101R["r_wall"]
    B1 = B + N * E101R["dE_J_per_minion_op"] * 1e6
    W1 = A + B1 / c1t
    tg1 = tg * E101R["r_wall"]
    B2 = B + N * s * 1e-12 * 832.0 / 32.0 * (E["b2"] + E["d2"] * twin["phi"]) * 1e6
    W2 = A + B2 / t_us
    rl = twin.get("rest_law", {}).get("P_rest_W")
    return {"C1": {"cycles_per_op_wall": twin["cycles_per_op_wall"] * E101R["r_wall"], "cycles_per_op_mean": twin["cycles_per_op_mean"] * E101R["r_mean"],
                   "rho_wall_over_mean": twin["rho_wall_over_mean"] * E101R["rho_factor"], "seconds_per_gemm": tg1, "T_op_us": c1t,
                   "W_affine": {"A_W": A, "B_W_us": B1}, "W_over_idle": W1, "J_over_idle_per_gemm": W1 * tg1,
                   "J_at_rest_per_gemm_REPORTED": (rl + W1) * tg1 if rl is not None else None},
            "C0": {"cycles_per_op_wall": twin["cycles_per_op_wall"], "cycles_per_op_mean": twin["cycles_per_op_mean"], "seconds_per_gemm": tg,
                   "W_affine": {"A_W": A, "B_W_us": B}, "W_over_idle": twin["W_over_idle"], "J_over_idle_per_gemm": twin["J_over_idle_per_gemm"]},
            "C2_REPORTED": {"cycles_per_op_wall": twin["cycles_per_op_wall"], "seconds_per_gemm": tg, "W_affine": {"A_W": A, "B_W_us": B2},
                            "W_over_idle": W2, "J_over_idle_per_gemm": W2 * tg}}


# ------------------------------------------------------------------ the record of one point
def mm1_record(pred):
    sw = pred.get("switches", {})
    return {"cycles_per_op_wall": pred["cycles_per_op_wall"], "cycles_per_op_mean": pred["cycles_per_op_mean"], "rho_wall_over_mean": pred["rho_wall_over_mean"],
            "T_op_us": pred["T_op_us"], "seconds_per_gemm": pred["seconds_per_gemm"], "cycles_per_gemm_wall": pred["cycles_per_gemm_wall"],
            "W_affine": {"A_W": pred["W_affine"]["A_W"], "B_W_us": pred["W_affine"]["B_W_us"]}, "W_over_idle": pred["W_over_idle"],
            "J_over_idle_per_gemm": pred["J_over_idle_per_gemm"], "phi": pred["phi"], "e_res_nJ": pred["e_res_nJ"],
            "rest_law_P_W": pred["rest_law"]["P_rest_W"], "J_at_rest_rest_law_REPORTED": pred["rest_law"]["J_at_rest_per_gemm_REPORTED"],
            "lines_L2_L3_F": pred["lines_L2_L3_F"], "footprint_MB": pred["footprint_MB"],
            "sim_steps_per_minion_per_gemm": pred["sim_steps_per_minion_per_gemm"], "floor_cycles_measured_tenb": pred["floor_cycles_measured_tenb"],
            "bench_resident_cycles_simulated": pred["bench_resident_cycles_simulated"],
            "switches": {"counted_fin_edges": sw.get("counted_fin_edges"), "estimated_fin_edges": sw.get("estimated_fin_edges"),
                         "fresh_lines_J_apart": sw.get("fresh_lines_J_apart"), "scope": sw.get("scope")},
            "J_over_idle_by_class": pred.get("J_over_idle_by_class"),
            "planning_peak_W": REST_HIGH_W + PLAN_K * pred["W_over_idle"] + PLAN_PLUS_W}


def build():
    pts = {p["id"]: p for p in PTS["points"] + PTS["smoke"]}
    out = {"experiment": "E211", "request": "Q204",
           "what": "E211's frozen forecasts, before any E211 datum: MM1-v1 as landed through the desk map (MM1), the sharing-aware rule (MM1-S), "
                   "MM1-v1's closed form at the twins (REPORTED), F1, F2, the chip-lines null (NC), the no-walk null (N0), family C's rules (C0, C1, "
                   "C2 REPORTED), the ratios per pair and the four stride readings",
           "card": {"card": CARD, "f_MHz": F_MHZ, "V": V, "minions": N, "mask": MASK},
           "interpreter": "/usr/bin/python3 %s" % sys.version.split()[0],
           "inputs_sha256": dict(PINS, **{OWN["map"]: sha_rel(OWN["map"]), OWN["points"]: sha_rel(OWN["points"])}),
           "f1f2_route_files_checked": N_ROUTE, "e101_rule": E101R,
           "mm1_v2": "NOT IN THIS FILE: MM1-v2 had not landed when it was made (see E211.md section 0)",
           "points": {}, "pairs": {}, "family_C": {}}
    mm = {}
    for pid, p in pts.items():
        sh, fmt, walk = p["shape"], p["format"], p["walk"]
        pred = mm1_on_map(sh, walk, fmt)
        rec = {"arm": p["arm"], "arm_family": p["arm_family"], "family": p["family"], "shape": sh, "format": fmt, "walk": walk, "coop": p["coop"],
               "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"], "scored_in_watts": False}
        rec["MM1"] = mm1_record(pred)
        rec["MM1"]["scope"] = ("MM1-v1 as landed (25d2e74e), its frozen equations and constants, on the desk map of the point's walk "
                               "(desk/map-e211.json); the stride rule r1 carried literally")
        rec["MM1_S"] = sharing_aware(pred, sh, walk)
        rec["F"] = f1f2(pid, sh, walk, fmt)
        if p["arm_family"] == "gemmL":
            cf = M_FROZEN.predict(CARD, p["arm"], fmt, "random", MASK, F_MHZ, V)
            rec["MM1cf_REPORTED"] = {"cycles_per_op_wall": cf["cycles_per_op_wall"], "cycles_per_op_mean": cf["cycles_per_op_mean"],
                                     "seconds_per_gemm": cf["seconds_per_gemm"], "W_over_idle": cf["W_over_idle"],
                                     "J_over_idle_per_gemm": cf["J_over_idle_per_gemm"], "lines_L2_L3_F": cf["lines_L2_L3_F"],
                                     "map_over_closed_form_cycles_minus_1": pred["cycles_per_op_wall"] / cf["cycles_per_op_wall"] - 1.0}
        rec["scored_in_watts"] = bool(pred["W_over_idle"] < LOW_W)
        mm[pid] = pred
        out["points"][pid] = rec
    # family C
    for pid, p in pts.items():
        if p["arm_family"] != "gemmLnc":
            continue
        twin_id = p["twin_of"] if p["twin_of"] else None
        twin = mm[pid]          # the gemmLnc point's own MM1 forecast IS its twin's: rgm136's walk on the same shape
        fc = family_c(twin)
        out["points"][pid]["C"] = fc
        out["family_C"][p["pair"] or pid] = {"point": pid, "twin": twin_id, "ratio_C1_wall": E101R["r_wall"], "ratio_C1_mean": E101R["r_mean"],
                                             "ratio_C1_J_over_idle": fc["C1"]["J_over_idle_per_gemm"] / twin["J_over_idle_per_gemm"],
                                             "ratio_C0": 1.0,
                                             "ratio_C2_J_over_idle_REPORTED": fc["C2_REPORTED"]["J_over_idle_per_gemm"] / twin["J_over_idle_per_gemm"]}
    # the pairs: ratios rgm211 / rgm136
    for p in PTS["points"]:
        if p["arm_family"] != "gemmLn":
            continue
        pair = p["pair"]
        m_id, n_id = pair + "m", pair + "n"
        mrec, nrec = out["points"][m_id], out["points"][n_id]
        sh, fmt = p["shape"], p["format"]
        rd = {}
        for var in ("r1", "none", "both"):
            a = mm1_on_map(sh, "mn", fmt, var)["cycles_per_op_wall"]
            b = mm1_on_map(sh, "nm", fmt, var)["cycles_per_op_wall"]
            rd[var] = b / a
        rd["rgm136_only"] = mm1_on_map(sh, "nm", fmt, "none")["cycles_per_op_wall"] / mm1_on_map(sh, "mn", fmt, "r1")["cycles_per_op_wall"]
        out["pairs"][pair] = {
            "family": p["family"], "shape": sh, "format": fmt, "twin": m_id, "second": n_id,
            "ratio_wall": {"MM1": nrec["MM1"]["cycles_per_op_wall"] / mrec["MM1"]["cycles_per_op_wall"],
                           "F1": nrec["F"]["F1_cycles_per_op"] / mrec["F"]["F1_cycles_per_op"],
                           "NC": nrec["F"]["NC_cycles_per_op"] / mrec["F"]["NC_cycles_per_op"], "N0": 1.0},
            "ratio_mean": {"MM1": nrec["MM1"]["cycles_per_op_mean"] / mrec["MM1"]["cycles_per_op_mean"]},
            "ratio_J_over_idle": {"MM1": nrec["MM1"]["J_over_idle_per_gemm"] / mrec["MM1"]["J_over_idle_per_gemm"],
                                  "MM1_S": nrec["MM1_S"]["J_over_idle_per_gemm"] / mrec["MM1_S"]["J_over_idle_per_gemm"],
                                  "F1": nrec["F"]["F1_J_over_idle_per_gemm"] / mrec["F"]["F1_J_over_idle_per_gemm"],
                                  "F2": (nrec["F"]["F2_J_over_idle_per_gemm"] / mrec["F"]["F2_J_over_idle_per_gemm"]
                                         if "F2_J_over_idle_per_gemm" in nrec["F"] and "F2_J_over_idle_per_gemm" in mrec["F"] else None)},
            "stride_readings_ratio_wall": {"literal_r1 (MM1)": rd["r1"], "no_stride_term": rd["none"], "zeta_both_halves": rd["both"],
                                           "stride_on_rgm136_only": rd["rgm136_only"]},
            "chip_DRAM_lines_per_step": {w: MAP["shapes"][sh][w]["mm1v1_logistic"]["frozen_rule_r1"]["chip_distinct_lines_per_step"]["DRAM_lines"]
                                         for w in ("mn", "nm")},
            "fresh_lines_per_shire_op": {w: MAP["shapes"][sh][w]["mm1v1_logistic"]["frozen_rule_r1"]["lines_L2_L3_F_per_shire_op"][2] for w in ("mn", "nm")}}
    # peaks (planning, not forecasts of the peak)
    def peak(ids):
        best = None
        for i in ids:
            rec = out["points"][i]
            w = rec["MM1"]["planning_peak_W"]
            if rec.get("C"):
                w = max(w, REST_HIGH_W + PLAN_K * rec["C"]["C1"]["W_over_idle"] + PLAN_PLUS_W,
                        REST_HIGH_W + PLAN_K * rec["C"]["C2_REPORTED"]["W_over_idle"] + PLAN_PLUS_W)
            f1 = rec["F"]["F1_peak_point_W"]
            if best is None or w > best["planning_W"]:
                best = {"id": i, "planning_W": w}
            best["F1_peak_max_W"] = max(best.get("F1_peak_max_W", 0.0), f1)
        return best
    out["peaks"] = {"smoke": peak([p["id"] for p in PTS["smoke"]]),
                    "families_X_and_W": peak([p["id"] for p in PTS["points"] if p["family"] in ("W", "X")]),
                    "family_C": peak([p["id"] for p in PTS["points"] if p["family"] == "C"]),
                    "how": "MM1-v1's blind-day planning form: 26.0 W high-side rest + 1.10 x W over idle + 1 W (family C at the larger of C1 and C2); "
                           "F1's: its rest + its W over idle + 4 W"}
    return out


def flat(out):
    rows = []
    for pid, rec in out["points"].items():
        m = rec["MM1"]
        row = {"id": pid, "arm": rec["arm"], "family": rec["family"], "format": rec["format"], "walk": rec["walk"], "coop": rec["coop"],
               "ops_per_minion_per_gemm": rec["ops_per_minion_per_gemm"],
               "MM1_cycles_per_op_wall": r(m["cycles_per_op_wall"], 8), "MM1_cycles_per_op_mean": r(m["cycles_per_op_mean"], 8),
               "MM1_seconds_per_gemm": r(m["seconds_per_gemm"], 8), "MM1_W_over_idle": r(m["W_over_idle"], 8),
               "MM1_A_W": r(m["W_affine"]["A_W"], 10), "MM1_B_W_us": r(m["W_affine"]["B_W_us"], 10), "MM1_J_over_idle_per_gemm": r(m["J_over_idle_per_gemm"], 8),
               "MM1_rest_law_P_W": r(m["rest_law_P_W"], 8), "MM1_J_at_rest_rest_law_REPORTED": r(m["J_at_rest_rest_law_REPORTED"], 8),
               "MM1S_B_W_us": r(rec["MM1_S"]["B_W_us"], 10), "MM1S_J_over_idle_per_gemm": r(rec["MM1_S"]["J_over_idle_per_gemm"], 8),
               "F1_cycles_per_op": r(rec["F"]["F1_cycles_per_op"], 8), "F1_seconds_per_gemm": r(rec["F"]["F1_seconds_per_gemm"], 8),
               "F1_W_over_idle": r(rec["F"]["F1_W_over_idle"], 8), "F1_J_over_idle_per_gemm": r(rec["F"]["F1_J_over_idle_per_gemm"], 8),
               "F2_J_over_idle_per_gemm": r(rec["F"].get("F2_J_over_idle_per_gemm"), 8), "NC_cycles_per_op": r(rec["F"]["NC_cycles_per_op"], 8),
               "scored_in_watts": rec["scored_in_watts"]}
        if rec.get("C"):
            c1 = rec["C"]["C1"]
            row.update({"C1_cycles_per_op_wall": r(c1["cycles_per_op_wall"], 8), "C1_cycles_per_op_mean": r(c1["cycles_per_op_mean"], 8),
                        "C1_seconds_per_gemm": r(c1["seconds_per_gemm"], 8), "C1_B_W_us": r(c1["W_affine"]["B_W_us"], 10),
                        "C1_J_over_idle_per_gemm": r(c1["J_over_idle_per_gemm"], 8)})
        rows.append(row)
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=keys, lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


def text(out):
    L = ["E211 frozen forecasts (no E211 datum exists): aifoundry3 card 0, 600 MHz, 0.522 V, the full chip. Desk; every number a forecast of code.",
         "per point: id arm format | MM1 cycles an op wall / mean | seconds a GEMM | W over idle | J over idle | J at rest (rest law, REPORTED) | "
         "MM1-S J over idle | F1 cycles, seconds, W, J | F2 J | NC cycles"]
    for pid, rec in out["points"].items():
        m, f = rec["MM1"], rec["F"]
        f2 = f.get("F2_J_over_idle_per_gemm")
        L.append(f"{pid:5s} {rec['arm']:16s} {rec['format']:4s} | {m['cycles_per_op_wall']:8.2f} / {m['cycles_per_op_mean']:8.2f} | {m['seconds_per_gemm']:.5g} s | "
                 f"{m['W_over_idle']:6.2f} W | {m['J_over_idle_per_gemm']:.5g} J | {m['J_at_rest_rest_law_REPORTED']:.5g} J | S {rec['MM1_S']['J_over_idle_per_gemm']:.5g} J | "
                 f"F1 {f['F1_cycles_per_op']:8.2f} {f['F1_seconds_per_gemm']:.5g} s {f['F1_W_over_idle']:6.2f} W {f['F1_J_over_idle_per_gemm']:.5g} J | "
                 f"F2 {('%.5g J' % f2) if f2 is not None else 'not priced'} | NC {f['NC_cycles_per_op']:8.2f}")
        if rec.get("C"):
            c1 = rec["C"]["C1"]
            L.append(f"      family C: C1 wall {c1['cycles_per_op_wall']:.2f} mean {c1['cycles_per_op_mean']:.2f} t {c1['seconds_per_gemm']:.5g} s "
                     f"W {c1['W_over_idle']:.2f} J {c1['J_over_idle_per_gemm']:.5g}; C0 = the twin; C2 (REPORTED) J {rec['C']['C2_REPORTED']['J_over_idle_per_gemm']:.5g}")
    L += ["", "pairs, rgm211 / rgm136: wall cycles MM1 F1 NC N0 | counter mean MM1 | J over idle MM1 MM1-S F1 F2 | stride readings (literal, none, both, "
              "rgm136 only) | chip DRAM lines a step mn -> nm | fresh lines a shire-op mn -> nm"]
    for pair, x in out["pairs"].items():
        rw, rj, sr = x["ratio_wall"], x["ratio_J_over_idle"], x["stride_readings_ratio_wall"]
        f2 = rj["F2"]
        L.append(f"{pair} {x['shape']} {x['format']}: {rw['MM1']:.4f} {rw['F1']:.4f} {rw['NC']:.4f} {rw['N0']:.1f} | {x['ratio_mean']['MM1']:.4f} | "
                 f"{rj['MM1']:.4f} {rj['MM1_S']:.4f} {rj['F1']:.4f} {('%.4f' % f2) if f2 else '-'} | "
                 + " ".join(f"{v:.4f}" for v in sr.values())
                 + f" | {x['chip_DRAM_lines_per_step']['mn']:.1f} -> {x['chip_DRAM_lines_per_step']['nm']:.1f} | "
                 f"{x['fresh_lines_per_shire_op']['mn']:.1f} -> {x['fresh_lines_per_shire_op']['nm']:.1f}")
    L += ["", "family C (gemmLnc / its twin): C1 wall %.4f, mean %.4f (E101, measured, one block); C0 1" % (E101R["r_wall"], E101R["r_mean"])]
    for k, x in out["family_C"].items():
        L.append(f"  {k} ({x['point']} / {x['twin']}): C1 J over idle ratio {x['ratio_C1_J_over_idle']:.4f}; C2 (REPORTED) {x['ratio_C2_J_over_idle_REPORTED']:.4f}")
    pk = out["peaks"]
    L += ["", "planning peaks (MM1-v1's form) and F1's: " + "; ".join(f"{k} {v['planning_W']:.1f} W at {v['id']} (F1 at most {v['F1_peak_max_W']:.1f} W)"
                                                              for k, v in pk.items() if isinstance(v, dict))]
    return "\n".join(L) + "\n"


def main():
    out = build()
    js = json.dumps(out, indent=1, sort_keys=True, default=float) + "\n"
    cs = flat(out)
    tx = text(out)
    if sys.argv[1:] == ["--check"]:
        res = [(n, s == open(p).read()) for n, s, p in (("json", js, OUT_JSON), ("csv", cs, OUT_CSV), ("txt", tx, OUT_TXT))]
        print("forecast_e211 --check: " + ", ".join(f"{n} {'SAME' if ok else 'DIFFERS'}" for n, ok in res))
        return 0 if all(ok for _, ok in res) else 1
    open(OUT_JSON, "w").write(js)
    open(OUT_CSV, "w").write(cs)
    open(OUT_TXT, "w").write(tx)
    sys.stdout.write(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
