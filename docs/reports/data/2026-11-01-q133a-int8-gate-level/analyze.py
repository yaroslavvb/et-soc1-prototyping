#!/usr/bin/env python3
"""Q133(a): int8's multiply-add counted at gate level, set beside the RTL count, the card, and the float units.

    python3 analyze.py            (from this directory; reads runs/, Q132(b)'s, E78's, E79's and E102's committed files)

Writes analysis.json and tables.md. Every count is nets_hier (settle_count.cpp's `hier`: one count per net, merging a name
only with the same waveform in an ancestor scope), per TensorFMA op on one minion unless it says per MAC (16,384 an int8 op).
The RTL reference is Q132(b)'s committed counts, after the control run here reproduced them (section `control`).

SPDX-License-Identifier: Apache-2.0
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.dirname(HERE)
Q132 = os.path.join(DD, "2026-11-01-q132-rtl-bench")
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MID = 471698                        # the middle of run_kinds.py's three int8 launch points
ARMS = ["booth_tree", "plain", "booth", "booth_swap"]
KINDS = ["full", "gauss_q", "sorted", "pos", "smallint", "sparse50", "ternary", "highbit", "wsparse50", "neg_ones", "ones",
         "sparse90", "wsparse90", "a_full_b_zeros", "a_zeros_b_full", "zeros"]
STAGES = ["operand", "multiplier", "adder_norm", "result", "control"]


def load(p):
    return json.load(open(p))


def maybe(p):
    return load(p) if os.path.exists(p) else None


def at(row, n0):
    for p in row["points"]:
        if p["n0"] == n0:
            return p
    return None


def mean_pts(row):
    return row["mean"]


def u(m):
    return m["unit"]["nets_hier"]


def v(m):
    return m["vpu"]["nets_hier"]


def stats(y, p):
    y, p = np.array(y, float), np.array(p, float)
    r = float(np.corrcoef(y, p)[0, 1]) if len(y) > 2 and np.std(p) > 0 else None
    return {"n": int(len(y)), "rms_w": float(np.sqrt(((y - p) ** 2).mean())), "bias_w": float((p - y).mean()),
            "worst_w": float(np.abs(y - p).max()), "pearson_r": r}


def spearman(x, y):
    def rank(a):
        a = np.array(a, float)
        o = a.argsort()
        r = np.empty(len(a))
        r[o] = np.arange(len(a))
        return r
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def fit(rows, cols):
    X = np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)
    y = np.array([r["D"] for r in rows], float)
    sc = np.where(X.max(axis=0) > 0, X.max(axis=0), 1.0)
    b, *_ = np.linalg.lstsq(X / sc, y, rcond=None)
    return b / sc


def fit_report(rows, cols):
    b = fit(rows, cols)
    X = np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)
    res = stats([r["D"] for r in rows], X @ b)
    res["coef_fJ"] = {c: float(x) * 1e15 for c, x in zip(cols, b)}
    loo = []
    for i in range(len(rows)):
        bi = fit(rows[:i] + rows[i + 1:], cols)
        loo.append(float(np.array([rows[i][c] * rows[i]["rate"] for c in cols]) @ bi))
    res["loo"] = stats([r["D"] for r in rows], loo)
    res["resid_w"] = {r["kind"]: float(r["D"] - q) for r, q in zip(rows, X @ b)}
    return res


def apply(rows, cols, coef_fJ):
    b = np.array([coef_fJ[c] for c in cols]) * 1e-15
    X = np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)
    res = stats([r["D"] for r in rows], X @ b)
    res["pred_w"] = {r["kind"]: {"D": r["D"], "pred": float(q)} for r, q in zip(rows, X @ b)}
    return res


def main():
    out = {"_what": "Q133(a): tima_top (int8) at gate level in Q132(b)'s whole-vpu_top bench; counts are nets_hier per TensorFMA op "
                    "on one minion unless marked per MAC", "_rtl_reference": "Q132(b) counts-v2.json, counts-e102.json, counts-hlp.json"}
    runs = {a: {"kinds": maybe(os.path.join(HERE, "runs", a, "counts_kinds.json")),
                "bits": maybe(os.path.join(HERE, "runs", a, "counts_bits.json"))} for a in ARMS + ["rtl"]}
    v2 = load(os.path.join(Q132, "counts-v2.json"))["rows"]
    e102c = load(os.path.join(DD, "2026-11-01-e102-balanced-bit-prices", "bench", "counts-e102.json"))["rows"]
    hlp = load(os.path.join(Q132, "counts-hlp.json"))["rows"]
    e78 = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix", "e78.json"))["items"]
    q132a = load(os.path.join(Q132, "analysis.json"))
    e79 = load(os.path.join(DD, "2026-10-31-e79-fp16-int8-bit-prices", "hlp.json"))["cards"]["aifoundry3"]["items"]
    e102s = load(os.path.join(DD, "2026-11-01-e102-balanced-bit-prices", "scored.json"))["primary"]["prices"]

    def rtl_row(name):
        """Q132(b)'s committed RTL row for a tile, by this lane's name."""
        if name.startswith("e102_"):
            return e102c.get("int8." + name[5:])
        if name.startswith("e79_"):
            return hlp.get("int8." + name[4:])
        return v2.get("int8." + name)

    # ---- 1. the control: this machine's build of Q132(b)'s bench against its committed counts, point for point --------
    ctl = {"points": [], "max_abs_diff": {}}
    for part in ("kinds", "bits"):
        c = runs["rtl"][part]
        if not c:
            continue
        for key, row in c["rows"].items():
            name = key.split(".", 1)[1]
            ref = rtl_row(name)
            for p in row["points"]:
                q = at(ref, p["n0"]) if ref else None
                if q is None:
                    continue
                d = {"tile": name, "n0": p["n0"], "unit_nets_hier": u(p) - u(q), "vpu_nets_hier": v(p) - v(q),
                     "ff_clocked": p["ff"]["all"]["clocked"] - q["ff"]["all"]["clocked"],
                     "ff_toggles": p["ff"]["all"]["toggles"] - q["ff"]["all"]["toggles"],
                     "valid_slots": p["valid_slots"] - q["valid_slots"], "check_mismatch_here": p["check_mismatch"]}
                ctl["points"].append(d)
    for k in ("unit_nets_hier", "vpu_nets_hier", "ff_clocked", "ff_toggles", "valid_slots", "check_mismatch_here"):
        ctl["max_abs_diff"][k] = max((abs(d[k]) for d in ctl["points"]), default=None)
    out["control"] = ctl

    # ---- 2. the netlists ---------------------------------------------------------------------------------------------
    syn = {}
    for a in ARMS:
        sj = maybe(os.path.join(HERE, "netlists", f"stages_{a}.json"))
        st = os.path.join(HERE, "netlists", f"stat_{a}.txt")
        if not sj:
            continue
        area = None
        if os.path.exists(st):
            for line in open(st):
                if "Chip area for module" in line:
                    area = float(line.split(":")[-1])
        syn[a] = {"cells": sj["cells"], "flops": sj["flops"], "nets": sj["nets"], "nets_by_stage": sj["nets_by_stage"],
                  "flop_groups": sj["flop_groups"], "area_um2": area}
    out["netlists"] = syn

    # ---- 3. per kind ---------------------------------------------------------------------------------------------------
    kinds = {}
    for k in KINDS:
        ref = v2.get("int8." + k)
        if not ref:
            continue
        r = {"rtl": {"unit_per_mac": u(ref["mean"]) / MACS["int8"], "unit_per_mac_mid": u(at(ref, MID)) / MACS["int8"],
                     "vpu_per_mac": v(ref["mean"]) / MACS["int8"], "by_stage_per_mac": {s: ref["mean"]["unit"]["by_stage_hier1"].get(s, 0) / MACS["int8"] for s in STAGES},
                     "ff_clocked": ref["mean"]["ff"]["all"]["clocked"], "ff_clocked_tima": ref["mean"]["ff"]["tima"]["clocked"]}}
        for a in ARMS:
            c = runs[a]["kinds"]
            row = c["rows"].get("int8." + k) if c else None
            if not row:
                continue
            m = row["mean"]
            pm = at(row, MID)
            r[a] = {"points": len(row["points"]), "unit_per_mac": u(m) / MACS["int8"],
                    "unit_per_mac_mid": u(pm) / MACS["int8"] if pm else None,
                    "vpu_per_mac": v(m) / MACS["int8"], "vpu_per_mac_mid": v(pm) / MACS["int8"] if pm else None,
                    "by_stage_per_mac": {s: m["unit"]["by_stage_hier1"].get(s, 0) / MACS["int8"] for s in STAGES},
                    "check_mismatch_max": max(p["check_mismatch"] for p in row["points"]),
                    "valid_slots": m["valid_slots"], "gate_over_rtl": u(m) / u(ref["mean"]) if u(ref["mean"]) else None,
                    "gate_over_rtl_mid": (u(pm) / u(at(ref, MID))) if pm and u(at(ref, MID)) else None}
        kinds[k] = r
    out["kinds"] = kinds

    # does the count order the kinds as the card does: Spearman between E78's D and the unit count, over the seven dense kinds and all 15
    dense = ["full", "gauss_q", "sorted", "pos", "smallint", "ternary", "highbit"]
    rk = {}
    for a in ["rtl"] + ARMS:
        key = "unit_per_mac" if a in ("rtl", "booth_tree") else "unit_per_mac_mid"
        res = {}
        for nm, ks in (("dense_7", dense), ("all_15", [k for k in KINDS if k != "zeros"])):
            if all(a in kinds.get(k, {}) for k in ks):
                res[nm] = spearman([e78["int8." + k]["D"]["mean"] for k in ks], [kinds[k][a][key] for k in ks])
        rk[a] = res
    out["rank_vs_card"] = rk

    # zeros-subtracted, per MAC (D is over the type's zeros)
    for k, r in kinds.items():
        z = kinds.get("zeros")
        for a in ["rtl"] + ARMS:
            if a in r and z and a in z:
                key = "unit_per_mac" if a in ("rtl", "booth_tree") else "unit_per_mac_mid"
                if r[a].get(key) is not None and z[a].get(key) is not None:
                    r[a]["unit_per_mac_over_zeros"] = r[a][key] - z[a][key]

    # ---- 4. beside E78's watts: int8 alone, and the floats' constants carried across ------------------------------------
    model = {}
    for a in ["rtl"] + ARMS:
        rows = []
        for k in KINDS:
            item = e78.get("int8." + k)
            ref = v2.get("int8." + k)
            zr = v2.get("int8.zeros")
            if not item or not ref or k == "zeros":      # the zero row is 0 = 0 by construction; Q132(b) fits n = 15 without it
                continue
            if a == "rtl":
                g, gz = ref["mean"], zr["mean"]
            else:
                c = runs[a]["kinds"]
                if not c or "int8." + k not in c["rows"] or "int8.zeros" not in c["rows"]:
                    rows = None
                    break
                gr, gzr = c["rows"]["int8." + k], c["rows"]["int8.zeros"]
                if len(gr["points"]) == 3:
                    g, gz = gr["mean"], gzr["mean"]
                else:                                  # one point: set it beside the RTL's same point
                    g, gz = at(gr, MID), at(gzr, MID)
            # the clocked bits are the RTL's (the gate-level unit has no accounting macros; same registers, same stimulus)
            bus = g["vpu"]["by_stage_hier1"]["lane_operand_bus"] - gz["vpu"]["by_stage_hier1"]["lane_operand_bus"]
            rows.append({"kind": k, "D": item["D"]["mean"], "rate": item["rate"]["mean"],
                         "dnets_vpu": v(g) - v(gz), "dclk": ref["mean"]["ff"]["all"]["clocked"] - zr["mean"]["ff"]["all"]["clocked"],
                         "dbus": bus, "dnonbus": v(g) - v(gz) - bus})
        if not rows:
            continue
        cols = ["dnets_vpu", "dclk"]
        m = {"int8_alone": fit_report(rows, cols),
             "float_constants_applied": apply(rows, cols, q132a["fit_e78"]["fp32+fp16"]["vpu_hier"]["coef_fJ"]),
             "nets_only_int8_alone": fit_report(rows, ["dnets_vpu"]),
             "i3_int8_alone": fit_report(rows, ["dnonbus", "dbus", "dclk"])}
        model[a] = m
    out["model"] = {"form_i3": "Q132(b)'s I3 in nets_hier: k x delta(VPU nets other than the lane operand bus) + k_bus x delta(lane operand bus nets) + a x delta clocked bits",
                    "form": "D = rate x (k x delta nets_hier over the whole VPU + a x delta clocked register bits), deltas over int8.zeros; "
                            "E78's measured D and rate (aifoundry3, 600 MHz); the floats' constants are Q132(b)'s fp32+fp16 vpu_hier fit",
                    "float_constants_fJ": q132a["fit_e78"]["fp32+fp16"]["vpu_hier"]["coef_fJ"],
                    "q132b_int8_vpu_hier": {"rms_w": q132a["fit_e78"]["int8"]["vpu_hier"]["rms_w"], "loo_rms_w": q132a["fit_e78"]["int8"]["vpu_hier"]["loo"]["rms_w"],
                                            "coef_fJ": q132a["fit_e78"]["int8"]["vpu_hier"]["coef_fJ"]},
                    "q132b_float_to_int8_vpu_hier": q132a["across_formats"]["vpu_hier"]["float_to_int8"],
                    "arms": model}

    # ---- 5. single bits ------------------------------------------------------------------------------------------------
    card_b_rail = [e102s[f"int8.bk_{b}@I"]["rail"]["fJ"]["mean"] for b in range(8)]
    card_b_board = [e102s[f"int8.bk_{b}@I"]["board"]["fJ"]["mean"] for b in range(8)]
    card_a_board = [e79[f"a8_{b}"]["e_fJ"] for b in range(8)]
    card_a_rail = [e79[f"a8_{b}"]["e_rail_fJ"] for b in range(8)]
    flips = {"a": 8192, "b": 1024}
    masks = {"bk_0f": 4, "bk_f0": 4, "bk_15": 3, "bk_2a": 3, "bk_ff": 8}

    def per_flip(rowsrc, zero, item, nflip, n0=MID):
        # on these regular streams nets_hier can fold a fan-out of same-waveform nets into one ancestor-scope name (Q132(b) section 4),
        # so each flip is counted both ways; nets_map (the merge learned once on random data) is the one quoted for single bits
        r1, r0 = rowsrc(item), rowsrc(zero)
        if not r1 or not r0:
            return None
        p1, p0 = at(r1, n0), at(r0, n0)
        if not p1 or not p0:
            return None
        res = {"unit": (u(p1) - u(p0)) / nflip, "vpu": (v(p1) - v(p0)) / nflip,
               "unit_map": (p1["unit"]["nets_map"] - p0["unit"]["nets_map"]) / nflip, "vpu_map": (p1["vpu"]["nets_map"] - p0["vpu"]["nets_map"]) / nflip,
               "by_stage_map": {s: (p1["unit"]["by_stage"].get(s, 0) - p0["unit"]["by_stage"].get(s, 0)) / nflip for s in STAGES},
               "check_mismatch": max(p1["check_mismatch"], p0["check_mismatch"])}
        return res

    def shape_of(bu, rail, board, M, key):
        sh = {"odd_over_even_unit": float(np.mean([bu[1], bu[3], bu[5]]) / np.mean([bu[0], bu[2], bu[4]])),
              "msb_over_rest_unit": float(bu[7] / np.mean(bu[:7])), "bit7_over_bit6": float(bu[7] / bu[6]) if bu[6] else None,
              "spearman_unit_vs_rail": spearman(bu, rail), "spearman_unit_vs_board": spearman(bu, board),
              "mean_unit_per_flip": float(np.mean(bu))}
        if M.get("bk_2a") and M.get("bk_15") and M["bk_15"][key]:
            sh["mask_2a_over_15_unit"] = M["bk_2a"][key] / M["bk_15"][key]
        if M.get("bk_ff") and np.mean(bu):
            sh["ff_over_singles_unit"] = M["bk_ff"][key] / float(np.mean(bu))
        if M.get("bk_f0") and M.get("bk_0f"):
            sh["f0_minus_0f_per_op"] = (M["bk_f0"][key] - M["bk_0f"][key]) * 4 * 1024
        return sh

    bits = {"flips_per_op": {"a_list": 8192, "b_list": 1024, "masks": "bits x 1024"},
            "card": {"b_rail_fJ_e102": card_b_rail, "b_board_fJ_e102": card_b_board, "a_board_fJ_e79": card_a_board, "a_rail_fJ_e79": card_a_rail},
            "arms": {}}
    srcs = {"rtl": lambda n: rtl_row(n)}
    for a in ARMS:
        c = runs[a]["bits"]
        if c:
            srcs[a] = (lambda c: (lambda n: c["rows"].get("int8." + n)))(c)
    for a, src in srcs.items():
        A = [per_flip(src, "e79_a8q", f"e79_a8_{b}", flips["a"]) for b in range(8)]
        Bl = [per_flip(src, "e102_hq", f"e102_bk_{b}", flips["b"]) for b in range(8)]
        M = {mk: per_flip(src, "e102_hq", "e102_" + mk, nb * 1024) for mk, nb in masks.items()}
        res = {"a_list": A, "b_list": Bl, "masks": M}
        if all(x is not None for x in Bl):
            res["b_shape_map"] = shape_of([x["unit_map"] for x in Bl], card_b_rail, card_b_board, M, "unit_map")
            bu = [x["unit"] for x in Bl]
            bv = [x["vpu"] for x in Bl]
            res["b_shape"] = {"odd_over_even_unit": float(np.mean([bu[1], bu[3], bu[5]]) / np.mean([bu[0], bu[2], bu[4]])),
                              "odd_over_even_vpu": float(np.mean([bv[1], bv[3], bv[5]]) / np.mean([bv[0], bv[2], bv[4]])),
                              "msb_over_rest_unit": float(bu[7] / np.mean(bu[:7])),
                              "spearman_unit_vs_rail": spearman(bu, card_b_rail), "spearman_vpu_vs_rail": spearman(bv, card_b_rail),
                              "spearman_unit_vs_board": spearman(bu, card_b_board),
                              "mean_unit_per_flip": float(np.mean(bu)), "mean_vpu_per_flip": float(np.mean(bv))}
            if M.get("bk_2a") and M.get("bk_15"):
                res["b_shape"]["mask_2a_over_15_unit"] = M["bk_2a"]["unit"] / M["bk_15"]["unit"] if M["bk_15"]["unit"] else None
            if M.get("bk_ff"):
                res["b_shape"]["ff_over_singles_unit"] = M["bk_ff"]["unit"] / float(np.mean(bu)) if np.mean(bu) else None
        if all(x is not None for x in A):
            am = [x["unit_map"] for x in A]
            res["a_shape_map"] = {"odd_over_even_unit": float(np.mean([am[1], am[3], am[5]]) / np.mean([am[0], am[2], am[4]])),
                                  "msb_over_rest_unit": float(am[7] / np.mean(am[:7])), "spearman_unit_vs_board": spearman(am, card_a_board),
                                  "mean_unit_per_flip": float(np.mean(am)), "mean_magnitude_bits": float(np.mean(am[:7]))}
            au = [x["unit"] for x in A]
            av = [x["vpu"] for x in A]
            res["a_shape"] = {"odd_over_even_unit": float(np.mean([au[1], au[3], au[5]]) / np.mean([au[0], au[2], au[4]])),
                              "msb_over_rest_unit": float(au[7] / np.mean(au[:7])), "msb_over_rest_vpu": float(av[7] / np.mean(av[:7])),
                              "spearman_unit_vs_board": spearman(au, card_a_board), "spearman_vpu_vs_board": spearman(av, card_a_board),
                              "mean_unit_per_flip": float(np.mean(au)), "mean_vpu_per_flip": float(np.mean(av))}
        bits["arms"][a] = res
    cb, ca = card_b_rail, card_a_board
    bits["card_shape"] = {"b_odd_over_even_rail": float(np.mean([cb[1], cb[3], cb[5]]) / np.mean([cb[0], cb[2], cb[4]])),
                          "b_msb_over_rest_rail": float(cb[7] / np.mean(cb[:7])),
                          "a_odd_over_even_board": float(np.mean([ca[1], ca[3], ca[5]]) / np.mean([ca[0], ca[2], ca[4]])),
                          "a_msb_over_rest_board": float(ca[7] / np.mean(ca[:7]))}
    out["bits"] = bits
    out["k_rtl_map_fJ"] = q132a["fit_e78"]["fp32+fp16"]["vpu_map"]["coef_fJ"]["dnetsm_vpu"]   # Q132(b)'s constant for RTL nets_map counts

    # ---- 6. the float unit at gate level, from the same flow, in the same bench (the middle launch point) ---------------
    fg = maybe(os.path.join(HERE, "runs", "f_txfma_flat", "counts_kinds.json"))
    FMID = {"fp32": 274725, "fp16": 274725}
    if fg:
        fl = {}
        for key, row in fg["rows"].items():
            t, k = key.split(".", 1)
            ref = v2.get(key)
            p, q = at(row, FMID[t]), (at(ref, FMID[t]) if ref else None)
            if not p or not q:
                continue
            fl[key] = {"gate_unit_per_mac": u(p) / MACS[t], "rtl_unit_per_mac": u(q) / MACS[t], "gate_over_rtl": u(p) / u(q) if u(q) else None,
                       "gate_vpu_per_mac": v(p) / MACS[t], "rtl_vpu_per_mac": v(q) / MACS[t], "check_mismatch": p["check_mismatch"],
                       "valid_slots": p["valid_slots"]}
        out["float_gate"] = {"netlist": maybe(os.path.join(HERE, "netlists", "stages_txfma_flat.json")), "point_n0": FMID, "kinds": fl}
        # the cross-format test with every format at gate level: floats' constants fitted on gate-level float counts, applied to
        # int8's gate-level counts (booth_tree at the middle point), against Q132(b)'s same test on RTL counts (bias -1.53 W)
        frows = []
        for key, r in fl.items():
            t, k = key.split(".", 1)
            if k == "zeros":
                continue
            item, z = e78.get(key), fg["rows"].get(f"{t}.zeros")
            ref, zr = v2.get(key), v2.get(f"{t}.zeros")
            if not item or not z or not ref:
                continue
            p, pz = at(fg["rows"][key], FMID[t]), at(z, FMID[t])
            frows.append({"kind": key, "D": item["D"]["mean"], "rate": item["rate"]["mean"], "dnets_vpu": v(p) - v(pz),
                          "dclk": at(ref, FMID[t])["ff"]["all"]["clocked"] - at(zr, FMID[t])["ff"]["all"]["clocked"]})
        rrows = []                                      # the same float kinds at the same point, RTL counts, for a like-for-like
        for fr in frows:
            t = fr["kind"].split(".")[0]
            ref, zr = v2[fr["kind"]], v2[f"{t}.zeros"]
            rrows.append(dict(fr, dnets_vpu=v(at(ref, FMID[t])) - v(at(zr, FMID[t]))))
        irows = {}
        for a in ["booth_tree", "plain", "booth_swap", "booth"]:
            c = runs[a]["kinds"]
            if not c:
                continue
            rows = []
            for k in KINDS:
                item, ref, zr = e78.get("int8." + k), v2.get("int8." + k), v2.get("int8.zeros")
                g, gz = c["rows"].get("int8." + k), c["rows"].get("int8.zeros")
                if not item or not g or not gz or k == "zeros":
                    continue
                pg, pz = at(g, MID), at(gz, MID)
                rows.append({"kind": "int8." + k, "D": item["D"]["mean"], "rate": item["rate"]["mean"], "dnets_vpu": v(pg) - v(pz),
                             "dclk": at(ref, MID)["ff"]["all"]["clocked"] - at(zr, MID)["ff"]["all"]["clocked"]})
            irows[a] = rows
        rtl_i = []
        for k in KINDS:
            item, ref, zr = e78.get("int8." + k), v2.get("int8." + k), v2.get("int8.zeros")
            if item and ref and k != "zeros":
                rtl_i.append({"kind": "int8." + k, "D": item["D"]["mean"], "rate": item["rate"]["mean"],
                              "dnets_vpu": v(at(ref, MID)) - v(at(zr, MID)), "dclk": at(ref, MID)["ff"]["all"]["clocked"] - at(zr, MID)["ff"]["all"]["clocked"]})
        cols = ["dnets_vpu", "dclk"]
        xt = {"n_float_kinds": len(frows), "float_kinds": [r["kind"] for r in frows]}
        if len(frows) >= 3:
            fgfit = fit_report(frows, cols)
            frfit = fit_report(rrows, cols)
            xt["floats_gate_fit"] = fgfit
            xt["floats_rtl_fit_same_kinds"] = frfit
            xt["to_int8"] = {a: apply(rows, cols, fgfit["coef_fJ"]) for a, rows in irows.items()}
            xt["rtl_to_int8_same_kinds"] = apply(rtl_i, cols, frfit["coef_fJ"])
        out["float_gate"]["cross_format"] = xt
    # float single bits at gate level: E102's all-in B lists (E65's construction for fp32), per flipped bit, beside E102's own
    # RTL bench counts at the same point and E102's card prices (board and rail fJ, its primary arm)
    fb = maybe(os.path.join(HERE, "runs", "f_txfma_flat", "counts_bits.json"))
    if fb:
        e102s_all = e102s
        fl_bits = {}
        for t, bitsl, nflip in (("fp32", [0, 11, 16, 22], 4096), ("fp16", [0, 9], 8192)):
            z, zr = fb["rows"].get(f"{t}.e102_hq"), e102c.get(f"{t}.hq")
            if not z or not zr:
                continue
            pz, qz = at(z, FMID[t]), at(zr, FMID[t])
            for b in bitsl:
                r, rr = fb["rows"].get(f"{t}.e102_bj_{b}"), e102c.get(f"{t}.bj_{b}")
                if not r or not rr:
                    continue
                p1, q1 = at(r, FMID[t]), at(rr, FMID[t])
                card = next((e102s_all[k] for k in e102s_all if k.startswith(f"{t}.bj_{b}@")), None)
                mu = lambda m: m["unit"]["nets_map"]
                mv = lambda m: m["vpu"]["nets_map"]
                fl_bits[f"{t}.bj_{b}"] = {"gate_unit_per_flip": (u(p1) - u(pz)) / nflip, "rtl_unit_per_flip": (u(q1) - u(qz)) / nflip,
                                          "gate_vpu_per_flip": (v(p1) - v(pz)) / nflip, "rtl_vpu_per_flip": (v(q1) - v(qz)) / nflip,
                                          "gate_unit_map_per_flip": (mu(p1) - mu(pz)) / nflip, "rtl_unit_map_per_flip": (mu(q1) - mu(qz)) / nflip,
                                          "gate_vpu_map_per_flip": (mv(p1) - mv(pz)) / nflip, "rtl_vpu_map_per_flip": (mv(q1) - mv(qz)) / nflip,
                                          "flips_per_op": nflip, "check_mismatch": max(p1["check_mismatch"], pz["check_mismatch"]),
                                          "card_board_fJ": card["board"] if card and not isinstance(card["board"], dict) else (card["board"]["fJ"]["mean"] if card else None),
                                          "card_rail_fJ": card["rail"] if card and not isinstance(card["rail"], dict) else (card["rail"]["fJ"]["mean"] if card else None)}
        out["float_gate"]["bits"] = fl_bits
    # E102's 'the bench undercounts a single flip': each int8 single bit priced at one k per net toggle (a flip moves no clocked bit),
    # the floats' own gate-level k beside the RTL floats' k on RTL counts, against the card's fJ per flip
    xt = out.get("float_gate", {}).get("cross_format", {})
    if "floats_gate_fit" in xt:
        # the counts priced are nets_map: at gate level map and hier agree on random data (float randn 0.2% apart), so the gate floats' hier
        # fit prices them; at RTL the map reads well above hier, so RTL map counts take Q132(b)'s own vpu_map constant
        kg = xt["floats_gate_fit"]["coef_fJ"]["dnets_vpu"]
        kr = q132a["fit_e78"]["fp32+fp16"]["vpu_map"]["coef_fJ"]["dnetsm_vpu"]
        priced = {"k_gate_fJ": kg, "k_rtl_map_fJ": kr, "arms": {}}
        for a, res in out["bits"]["arms"].items():
            k_use = kr if a == "rtl" else kg
            row = {}
            for side, key, card_r, card_b in (("b", "b_list", card_b_rail, card_b_board), ("a", "a_list", card_a_rail, card_a_board)):
                lst = res.get(key)
                if not lst or any(x is None for x in lst):
                    continue
                pf = [x["vpu_map"] * k_use for x in lst]
                row[side] = {"fJ_per_flip": pf, "card_rail_fJ": card_r, "card_board_fJ": card_b,
                             "mean_over_card_rail": float(np.mean(pf) / np.mean(card_r)),
                             "mean_over_card_board_bits1to7": float(np.mean(pf[1:]) / np.mean(card_b[1:])) if side == "b" else float(np.mean(pf) / np.mean(card_b)),
                             "rms_vs_rail_fJ": float(np.sqrt(np.mean((np.array(pf) - np.array(card_r)) ** 2)))}
            priced["arms"][a] = row
        out["bits"]["priced_at_one_k"] = priced
    json.dump(out, open(os.path.join(HERE, "analysis.json"), "w"), indent=1)
    write_tables(out)


def fmt(x, nd=1):
    if x is None:
        return ""
    return f"{x:,.{nd}f}"


def write_tables(o):
    L = ["# Q133(a) tables", "", "Generated by `analyze.py` from `analysis.json`. nets_hier throughout; per TensorFMA op on one minion unless per MAC.", ""]
    c = o["control"]
    L += ["## The control", "", f"{len(c['points'])} tile-points of Q132(b)'s bench rebuilt here, against its committed counts; largest difference:", ""]
    L += ["| " + " | ".join(c["max_abs_diff"]) + " |", "|" + "---:|" * len(c["max_abs_diff"]),
          "| " + " | ".join(str(x) for x in c["max_abs_diff"].values()) + " |", ""]
    L += ["## The netlists (one tima_top; 16 per VPU)", "", "| arm | cells | flip-flops | area (um2) | nets | operand | multiplier | adder_norm | result | control |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for a, s in o["netlists"].items():
        n = s["nets_by_stage"]
        L.append(f"| {a} | {s['cells']:,} | {s['flops']} | {fmt(s['area_um2'])} | {s['nets']:,} | " + " | ".join(f"{n.get(x, 0):,}" for x in STAGES) + " |")
    L += ["", "## Per kind, merged-net toggles per MAC in the unit", "",
          "RTL: Q132(b), mean of three launch points. booth_tree: mean of three points. plain, booth, booth_swap: the middle point; their RTL column is the RTL's middle point.", "",
          "| kind | RTL | booth_tree | ×RTL | plain | booth | booth_swap | RTL (mid) | check |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, r in o["kinds"].items():
        bt = r.get("booth_tree", {})
        chk = max([r[a]["check_mismatch_max"] for a in ARMS if a in r] or [0])
        L.append(f"| {k} | {fmt(r['rtl']['unit_per_mac'])} | {fmt(bt.get('unit_per_mac'))} | {fmt(bt.get('gate_over_rtl'), 2)} | "
                 f"{fmt(r.get('plain', {}).get('unit_per_mac_mid'))} | {fmt(r.get('booth', {}).get('unit_per_mac_mid'))} | "
                 f"{fmt(r.get('booth_swap', {}).get('unit_per_mac_mid'))} | {fmt(r['rtl']['unit_per_mac_mid'])} | {chk:.0f} |")
    L += ["", "## booth_tree by stage, per MAC (three points)", "", "| kind | " + " | ".join(STAGES) + " | RTL " + " | RTL ".join(STAGES) + " |",
          "|---|" + "---:|" * (2 * len(STAGES))]
    for k, r in o["kinds"].items():
        if "booth_tree" in r:
            L.append(f"| {k} | " + " | ".join(fmt(r["booth_tree"]["by_stage_per_mac"][s]) for s in STAGES) + " | "
                     + " | ".join(fmt(r["rtl"]["by_stage_per_mac"][s]) for s in STAGES) + " |")
    L += ["", "## Beside E78's watts (int8, 15 kinds)", "", "| counts | int8 alone: rms (W) | LOO rms | k (fJ) | a (fJ) | floats' constants: rms (W) | bias (W) | r |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for a, m in o["model"]["arms"].items():
        f, x = m["int8_alone"], m["float_constants_applied"]
        L.append(f"| {a} | {f['rms_w']:.3f} | {f['loo']['rms_w']:.3f} | {f['coef_fJ']['dnets_vpu']:.3f} | {f['coef_fJ']['dclk']:.3f} | "
                 f"{x['rms_w']:.3f} | {x['bias_w']:+.3f} | {x['pearson_r']:.4f} |")
    L += ["", "## Single bits: merged-net toggles in the unit per flipped bit (middle point)", ""]
    b = o["bits"]
    L += ["| list, arm | bit 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | odd ÷ even | MSB ÷ rest | Spearman vs card |", "|---|" + "---:|" * 11]
    for side, key, card, cname in (("B", "b_list", b["card"]["b_rail_fJ_e102"], "rail"), ("A", "a_list", b["card"]["a_board_fJ_e79"], "board")):
        L.append(f"| **{side}, the card ({cname} fJ)** | " + " | ".join(fmt(x, 0) for x in card) + " | " +
                 (f"{b['card_shape']['b_odd_over_even_rail']:.2f} | {b['card_shape']['b_msb_over_rest_rail']:.2f} |  |" if side == "B" else
                  f"{b['card_shape']['a_odd_over_even_board']:.2f} | {b['card_shape']['a_msb_over_rest_board']:.2f} |  |"))
        for a, res in b["arms"].items():
            lst = res.get(key)
            if not lst or any(x is None for x in lst):
                continue
            sh = res.get("b_shape" if side == "B" else "a_shape", {})
            sp = sh.get("spearman_unit_vs_rail" if side == "B" else "spearman_unit_vs_board")
            L.append(f"| {side}, {a} | " + " | ".join(fmt(x["unit"], 2) for x in lst) + f" | {sh.get('odd_over_even_unit', 0):.2f} | "
                     f"{sh.get('msb_over_rest_unit', 0):.2f} | {sp:.2f} |")
    # single bits in nets_map, the merge quoted for these regular streams
    L += ["", "## Single bits in `nets_map` (the merge learned on random data; quoted for single bits)", "",
          "| list, arm | bit 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | odd ÷ even | MSB ÷ rest | Spearman vs card |", "|---|" + "---:|" * 11]
    for side, key, shk, sp in (("B", "b_list", "b_shape_map", "spearman_unit_vs_rail"), ("A", "a_list", "a_shape_map", "spearman_unit_vs_board")):
        for a, res in b["arms"].items():
            lst = res.get(key)
            if not lst or any(x is None for x in lst) or shk not in res:
                continue
            sh = res[shk]
            L.append(f"| {side}, {a} | " + " | ".join(fmt(x["unit_map"], 1) for x in lst) + f" | {sh['odd_over_even_unit']:.2f} | {sh['msb_over_rest_unit']:.2f} | {sh[sp]:.2f} |")
    L += ["", "B-list masks in `nets_map`, per flipped bit (bk_2a: bits 1, 3, 5; bk_15: bits 0, 2, 4; bk_ff all eight):", ""]
    for a, res in b["arms"].items():
        sh = res.get("b_shape_map", {})
        if "mask_2a_over_15_unit" in sh:
            L.append(f"- {a}: 2a ÷ 15 = {sh['mask_2a_over_15_unit']:.2f} (card, rail: 1.97 [1.69, 2.33]); ff ÷ mean of singles = {sh.get('ff_over_singles_unit', 0):.3f} (card 0.63 [0.53, 0.77]); bit 7 ÷ bit 6 = {sh['bit7_over_bit6']:.2f} (card 1.9)")
    fg = o.get("float_gate")
    if fg:
        L += ["", "## The float unit at gate level (middle launch point, 274,725 ops)", "", "| kind | gates per MAC | RTL per MAC | gates ÷ RTL | check |", "|---|---:|---:|---:|---:|"]
        for k2, r in sorted(fg["kinds"].items()):
            L.append(f"| {k2} | {fmt(r['gate_unit_per_mac'])} | {fmt(r['rtl_unit_per_mac'])} | {fmt(r['gate_over_rtl'], 2)} | {r['check_mismatch']:.0f} |")
        x = fg.get("cross_format", {})
        if "floats_gate_fit" in x:
            L += ["", "## One price across formats", "", "| fit | n | k (fJ) | a (fJ) | rms (W) | LOO rms (W) |", "|---|---:|---:|---:|---:|---:|"]
            for nm, f in (("floats, gates", x["floats_gate_fit"]), ("floats, RTL, same kinds", x["floats_rtl_fit_same_kinds"])):
                L.append(f"| {nm} | {f['n']} | {f['coef_fJ']['dnets_vpu']:.3f} | {f['coef_fJ']['dclk']:.3f} | {f['rms_w']:.3f} | {f['loo']['rms_w']:.3f} |")
            L += ["", "| floats' constants put on int8 | rms (W) | bias (W) | r |", "|---|---:|---:|---:|"]
            t = x["rtl_to_int8_same_kinds"]
            L.append(f"| RTL both sides | {t['rms_w']:.3f} | {t['bias_w']:+.3f} | {t['pearson_r']:.4f} |")
            for a, t in x["to_int8"].items():
                L.append(f"| gates both sides, int8 {a} | {t['rms_w']:.3f} | {t['bias_w']:+.3f} | {t['pearson_r']:.4f} |")
        if fg.get("bits"):
            kgf = fg["cross_format"]["floats_gate_fit"]["coef_fJ"]["dnets_vpu"] if "floats_gate_fit" in fg.get("cross_format", {}) else None
            krf = o["k_rtl_map_fJ"]   # RTL map counts take Q132(b)'s vpu_map constant
            L += ["", "## Float single bits at gate level (E102's all-in B lists, middle point), in `nets_map`", "",
                  "nets_hier on these regular streams folds unit nets into same-waveform names in the VPU's scopes (its whole-VPU count per flip falls below the unit's), so nets_map is quoted. Priced at one k per net toggle (a flip moves no clocked bit): gates at the gate-level floats' fit, RTL at Q132(b)'s vpu_map constant, 1.871 fJ.", "",
                  "| tile | flips/op | gates, unit | RTL, unit | gates ÷ RTL | gates, VPU | RTL, VPU | gates, VPU × k (fJ) | RTL, VPU × k (fJ) | card board fJ | card rail fJ |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
            for k2, r in fg["bits"].items():
                gu, ru = r["gate_unit_map_per_flip"], r["rtl_unit_map_per_flip"]
                L.append(f"| {k2} | {r['flips_per_op']} | {fmt(gu)} | {fmt(ru)} | {fmt(gu / ru if ru else None, 2)} | {fmt(r['gate_vpu_map_per_flip'])} | {fmt(r['rtl_vpu_map_per_flip'])} | "
                         f"{fmt(r['gate_vpu_map_per_flip'] * kgf if kgf else None, 0)} | {fmt(r['rtl_vpu_map_per_flip'] * krf if krf else None, 0)} | {fmt(r['card_board_fJ'], 0)} | {fmt(r['card_rail_fJ'], 0)} |")
    open(os.path.join(HERE, "tables.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
