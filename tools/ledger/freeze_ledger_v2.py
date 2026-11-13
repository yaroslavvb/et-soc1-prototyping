#!/usr/bin/env python3
"""Freeze the load ledger v2's form and every constant, from committed files only (Q166, step 1).

Writes docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json. It reads no measurement of the three held-out
loads (E39, E37, E59) and no measurement of the four loads set beside them (E101, E136, E86, E95) except where a
constant is named below as coming from one of them (E101's set-bit weight and streaming price: E101 is then scored
IN SAMPLE for those terms; M10's term a reads each session's own random anchors, so E86's and E95's kernel terms are
held out by kind, not by session).

    python3 -I -B tools/ledger/freeze_ledger_v2.py [--out PATH]

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import json
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
OUT_DIR = os.path.join(DATA, "2026-11-12-q166-ledger-v2")

P_M10 = "docs/reports/data/2026-11-04-q142m-m10"
P_E78 = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
P_E82 = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"
P_LAW = "docs/reports/data/2026-11-05-q145a-footing-law/law.json"
P_E66 = "docs/reports/data/2026-10-27-e66-idle-long/e66-split.json"
P_CAT = "docs/reports/data/2026-09-23-energy-manual/catalogue.json"
P_CYC = "workloads/sparseparity/tools/cycle_model.py"
P_D21 = "docs/reports/data/2026-09-21-horace-aifoundry2/model.json"

CARD_OF = {"a2": "aifoundry2", "a3": "aifoundry3", "c1": "aifoundry1-c1"}


def rd(rel):
    return json.load(open(os.path.join(REPO, rel)))


def git(*a):
    try:
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def const(value, source, label, unit, band=None, note=None):
    d = {"value": value, "unit": unit, "source": source, "label": label}
    if band is not None:
        d["band"] = list(band)
    if note:
        d["note"] = note
    return d


# ------------------------------------------------------------------ M10's kernel term
def m10_heldout():
    """{(kind, card): [held-out predictions over that kind's rows on that card]} and M10's bands.
    Held out = leave one kind out (rows-m10.json err_w[variant] = D - held-out prediction; the frozen variant is
    B+a+b for the floats and B for int8, m10.json families.*.variant)."""
    m = rd(P_M10 + "/m10.json")
    rows = rd(P_M10 + "/rows-m10.json")
    var = {"float": m["families"]["float"]["variant"], "int8": m["families"]["int8"]["variant"]}
    out = {}
    for r in rows:
        fam = "int8" if r["type"] == "int8" else "float"
        pred = r["D"] - r["err_w"][var[fam]]
        out.setdefault((r["kind"], r["card"]), []).append({"exp": r["exp"], "D_measured": r["D"], "pred": pred})
    bands = {}
    for fam in ("float", "int8"):
        f = m["families"][fam]
        for fc, v in f["interval_pool_by_format_card"].items():
            bands[fc] = {"rms_w": v["rms_w"], "band_k": f["band_k"], "half_w": f["band_k"] * v["rms_w"], "n": v["n"]}
    return out, bands, var


def kind_entry(H, bands, kinds, card, fmt, how):
    """One v2 kind on one card from M10's held-out predictions for one or more M10 kinds (a composite takes the mean
    of the kinds' means and widens its band to their spread)."""
    means = []
    used = []
    for k in kinds:
        xs = H.get((k, card))
        if not xs:
            continue
        mu = statistics.fmean(x["pred"] for x in xs)
        means.append(mu)
        used.append({"m10_kind": k, "rows": [x["exp"] for x in xs], "heldout_pred_w": mu})
    if not means:
        return None
    mu = statistics.fmean(means)
    hb = bands[f"{fmt}|{card}"]["half_w"]
    return {"D_w": mu, "D_band_w": [min(means) - hb, max(means) + hb], "m10_kinds": used,
            "how": how, "band_how": f"spread of the kinds' held-out means, widened by M10's band k x rms ({hb:.3f} W, "
                                    f"m10.json families.*.interval_pool_by_format_card['{fmt}|{card}'])"}


def build_kinds(H, bands):
    K = {}
    small = ["fp32.s:signs", "fp32.pow2", "fp32.smallint"]
    how_small = ("small-integer fp32 operands, the class of E39's host default (random non-zero integers in [-3, 3]) "
                 "and E37's mmbench fill ({-2, -1, 1, 2}); M10 has no row of either fill, so v2 takes the mean of M10's "
                 "held-out predictions for its three nearest kinds (+-1 signs, powers of two, integers -8..7), "
                 "their spread as part of the band (a hand choice, stated)")
    K["fp32.small_int"] = {}
    for c in ("a3", "c1"):
        e = kind_entry(H, bands, small, c, "fp32", how_small)
        K["fp32.small_int"][c] = e
    K["int8.pm1"] = {"a3": kind_entry(H, bands, ["int8.s:signs"], "a3", "int8",
                                      "random +-1 bytes (0x01, 0xFF): sparse parity's operands; M10's held-out "
                                      "prediction for E90's int8 signs tile")}
    K["fp32.randn"] = {c: kind_entry(H, bands, ["fp32.randn"], c, "fp32", "random normal fp32") for c in ("a3", "c1")}
    K["fp16.randn"] = {c: kind_entry(H, bands, ["fp16.randn"], c, "fp16", "random normal fp16") for c in ("a3", "c1")}
    K["int8.full"] = {c: kind_entry(H, bands, ["int8.full"], c, "int8", "random int8 over the full range")
                      for c in ("a3", "c1")}
    K["fp32.zeros"] = {c: {"D_w": 0.0, "D_band_w": [0.0, 0.0], "how": "zeros: D is over the type's own zeros"}
                       for c in ("a2", "a3", "c1")}
    K["fp16.zeros"] = {c: {"D_w": 0.0, "D_band_w": [0.0, 0.0], "how": "zeros"} for c in ("a2", "a3", "c1")}
    K["int8.zeros"] = {c: {"D_w": 0.0, "D_band_w": [0.0, 0.0], "how": "zeros"} for c in ("a2", "a3", "c1")}
    # aifoundry2: M10 has no aifoundry2 family, so its aifoundry3 D is carried by E38's card scale (a3 = 0.963 a2)
    for k in ("fp32.small_int", "fp32.randn", "fp16.randn", "int8.full"):
        e3 = K[k]["a3"]
        K[k]["a2"] = {"D_w": e3["D_w"] / 0.963, "D_band_w": [e3["D_band_w"][0] / 0.969, e3["D_band_w"][1] / 0.958],
                      "how": e3["how"] + "; aifoundry2 = aifoundry3 / 0.963 (E38's card scale, band 0.958-0.969)",
                      "m10_kinds": e3.get("m10_kinds")}
    # E86's and E95's own kinds on aifoundry3, each from its own M10 rows (held out by kind)
    for (kind, card), xs in sorted(H.items()):
        if card != "a3" or not any(x["exp"] in ("E86", "E95") for x in xs):
            continue
        if kind in K:
            continue
        fmt = kind.split(".")[0]
        K[kind] = {"a3": kind_entry(H, bands, [kind], "a3", fmt, "the kind's own M10 rows, held out by kind")}
    return K


# ------------------------------------------------------------------ the zeros anchors
def zeros_anchors():
    Z = {}
    for fmt in ("fp32", "fp16", "int8"):
        Z[fmt] = {}
        for ck, p, exp in (("a3", P_E78, "E78"), ("c1", P_E82, "E82")):
            it = rd(p)["items"][f"{fmt}.zeros"]
            S, ci, rate = it["S"]["mean"], it["S"]["ci95"], it["rate"]["mean"]
            Z[fmt][ck] = {"Z_w": S, "Z_band_w": [S - ci, S + ci], "rate_ops_per_s": rate,
                          "source": f"{p} items.{fmt}.zeros.S (mean, ci95), .rate ({exp}, 600 MHz, six passes)"}
    # aifoundry2, fp32 only (E37 and E39 run fp32 there): the 21 Sep session's zeros board power over its idle
    # (docs/findings/10-data-dependent-power.md: zeros 38.29 W, idle before each launch 36.29 W; four runs).
    zeros_w, idle_w = 38.29, 36.29
    Z["fp32"]["a2"] = {"Z_w": zeros_w - idle_w, "Z_band_w": [zeros_w - idle_w - 0.30, zeros_w - idle_w + 0.30],
                       "rate_ops_per_s": 1024 * 600e6 / 546.0,
                       "source": "docs/findings/10-data-dependent-power.md (21 Sep, aifoundry2: zeros 38.29 W board, "
                                 "idle 36.29 W before each launch; the same two numbers tools/ettelem/"
                                 "score_load_predictions.py MEAS14 and IDLE21 carry); band +-0.30 W, a hand choice "
                                 "wider than the runs' own 0.03 W spread (that file, line 27), for a session days "
                                 "before E39's and E37's",
                       "label": "reported (an earlier campaign; not E39's or E37's record)"}
    for fmt in ("fp16", "int8"):
        z3 = Z[fmt]["a3"]
        Z[fmt]["a2"] = {"Z_w": z3["Z_w"], "Z_band_w": list(z3["Z_band_w"]),
                        "rate_ops_per_s": 1024 * 600e6 / (546.0 if fmt == "fp16" else 318.0),
                        "source": "a PLACEHOLDER (aifoundry3's E78 anchor): used only where it cancels, E136's random "
                                  "minus zeros", "label": "placeholder"}
    return Z


# ------------------------------------------------------------------ instruction classes
VEC_INT = ["fadd.pi", "fsub.pi", "fmul.pi", "fmulh.pi", "fmulhu.pi", "fand.pi", "for.pi", "fxor.pi", "fnot.pi",
           "fsll.pi", "fsrl.pi", "fsra.pi", "fmin.pi", "fmax.pi", "fminu.pi", "fmaxu.pi", "feq.pi", "flt.pi",
           "fltu.pi", "fle.pi", "faddi.pi", "fandi.pi", "fslli.pi", "fsrli.pi", "fsrai.pi", "fpackrepb.pi",
           "fpackreph.pi"]


def instr_classes():
    comb = rd(P_CAT)["combined"]
    out = {}
    per = {}
    for ck, card in CARD_OF.items():
        xs = [comb[f"{n}/random/h2"]["per_card"][card]["mean"] for n in VEC_INT if f"{n}/random/h2" in comb]
        per[ck] = statistics.median(xs)
    zs = [comb[f"{n}/zeros/h2"]["mean"] for n in VEC_INT if f"{n}/zeros/h2" in comb]
    rs = [comb[f"{n}/random/h2"]["mean"] for n in VEC_INT if f"{n}/random/h2" in comb]
    out["vec_int"] = {"random_pj": per, "band_pj": [statistics.median(zs), max(rs)],
                      "n_instructions": len(rs),
                      "source": f"{P_CAT} combined.<op>/random/h2 per_card means, median over the vector-integer class "
                                "of docs/energy-manual/03a-every-instruction.md (27 instructions); band from the "
                                "class's zeros median to its dearest random row (fmul.pi)",
                      "label": "measured (three passes on each of three cards, 26 Sep); class median a hand choice"}
    return out


# ------------------------------------------------------------------ memory, mesh
def mem_paths():
    """§4.1 of the energy manual (tensor loads and stores, zeros and random, per card for random), §4.2's L3, and
    E101's post hoc path cost for tiles streamed from the L2 (the streaming price)."""
    m = {
        "scp_load": {"zeros_pj": 2.12, "random_pj": {"a2": 4.16, "a3": 4.14, "c1": 4.98}, "rel_band": [0.875, 1.135],
                     "source": "docs/energy-manual/04-bytes-memory.md §4.1, 'Tensor load from the shire's own "
                               "scratchpad' (zeros 2.12 [1.85-2.46], random 4.43 [4.06-5.03]; per card random)"},
        "scp_store": {"zeros_pj": 4.65, "random_pj": {"a2": 8.03, "a3": 7.87, "c1": 9.84}, "rel_band": [0.914, 1.164],
                      "source": "docs/energy-manual/04-bytes-memory.md §4.1, 'Tensor store into the shire's own "
                                "scratchpad' (zeros 4.65 [4.25-5.25], random 8.58 [7.84-9.99])"},
        "dram_load": {"zeros_pj": 94.6, "random_pj": {"a2": 134.8, "a3": 127.3, "c1": 135.8}, "rel_band": [0.89, 1.10],
                      "source": "docs/energy-manual/04-bytes-memory.md §4.1, 'Tensor load from DRAM' (zeros 94.6 "
                                "[86.2-105.7], random 132.6 [117.9-145.4]); 76 GB/s"},
        "dram_store": {"zeros_pj": 94.4, "random_pj": {"a2": 136.4, "a3": 132.4, "c1": 156.9}, "rel_band": [0.88, 1.11],
                       "source": "docs/energy-manual/04-bytes-memory.md §4.1, 'Tensor store to DRAM'"},
        "l3_load": {"zeros_pj": 13.5, "random_pj": {"a2": 12.3, "a3": 13.5, "c1": 18.4}, "rel_band": [0.48, 1.39],
                    "source": "docs/energy-manual/04-bytes-memory.md §4.2, L3 (contents not set: no zeros/random split, "
                              "so both columns carry the level's own figure; a2's zeros entry is a3's); bar [7.1-20.5]",
                    "note": "unsplit"},
        "l2_stream": {"zeros_pj": 2.15e3 / 2048.0, "random_pj": {"a2": 7.70e3 / 2048.0 * 4.16 / 4.14,
                                                                "a3": 7.70e3 / 2048.0,
                                                                "c1": 7.70e3 / 2048.0 * 4.98 / 4.14},
                      "rel_band": [0.90, 1.10],
                      "source": "docs/reports/data/2026-11-01-e101-real-matmul/README.md, the POST HOC path cost in the "
                                "benchmark (mm16) arm: zeros 2.07/2.18/2.19 and random 7.93/7.65/7.53 nJ per 2 KB op "
                                "(fp32/fp16/int8; posthoc-path.json); means 2.15 and 7.70 nJ; a3 only, carried to the "
                                "other cards by §4.1's scratchpad-load ratio",
                      "label": "post hoc (E101): E101 is IN SAMPLE wherever this price is used"},
    }
    for k, v in m.items():
        v.setdefault("label", "measured (the version-3 check, three passes on each of three cards, 26 Sep)")
    return m


def mesh_hop():
    return {"zeros_pj": 0.65, "random_pj": 1.8, "rel_band": [0.92, 1.06],
            "source": "docs/energy-manual/README.md, row 4.3 (from 04a-fine-grain.md): one mesh hop costs 1.7-1.9 "
                      "pJ/B on random data and 0.6-0.7 on zeros, fitted over 1-8 hops", "label": "measured"}


# ------------------------------------------------------------------ the card at rest
def idle_laws():
    law = rd(P_LAW)["law"]
    e66 = rd(P_E66)["verdicts"]
    out = {}
    q = {"aifoundry2": law["aifoundry2_idle"], "aifoundry3": law["aifoundry3"], "aifoundry1-c1": law["aifoundry1c1"]}
    exps = {
        "aifoundry2": {"B": e66["L2b"]["mean"], "A80": e66["L2a"]["mean"], "T_L": e66["L1"]["mean"],
                       "source": P_E66 + " verdicts.L2b/L2a/L1 means (E66: 18 cycles, 47-88 C)"},
        "aifoundry3": {"B": 12.3, "A80": 25.0, "T_L": 36.0,
                       "source": "docs/energy-manual/01-at-rest.md, 'Confidence': aifoundry3 12.3 W + 25.0 W e^((T-80)/36)"},
        "aifoundry1-c1": {"B": 14.1, "A80": 34.8, "T_L": 36.0,
                          "source": "docs/energy-manual/01-at-rest.md, 'Confidence': aifoundry1 card 1 14.1 W + 34.8 W "
                                    "e^((T-80)/36)"},
    }
    for card in ("aifoundry2", "aifoundry3", "aifoundry1-c1"):
        a, b, c = q[card]["quad_w"]
        out[card] = {"quad": {"a": a, "b": b, "c": c}, "quad_band_c": q[card]["T_degrees"],
                     "quad_rms_w": q[card]["rms_w"],
                     "quad_source": P_LAW + f" law.{ {'aifoundry2': 'aifoundry2_idle', 'aifoundry3': 'aifoundry3', 'aifoundry1-c1': 'aifoundry1c1'}[card] }.quad_w (the footing law, FL1-FL6, registered c14e5f35)",
                     "exp": exps[card], "rest_band_w": 0.5,
                     "rest_band_how": "a hand choice: a card's idle moves a few tenths of a watt from day to day "
                                      "about any committed law (01-at-rest.md: aifoundry3 +1.01 W, card 1 +10.1 W above "
                                      "aifoundry2's law; the footing law's fit rms 0.02-0.03 W)"}
    return out


def cycle_constants():
    """The sparse-parity kernel's fitted cycle constants, parsed (not imported: the module needs numpy)."""
    src = open(os.path.join(REPO, P_CYC)).read()
    tree = ast.parse(src)
    fitted = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "FITTED" for t in node.targets):
            call = node.value
            fitted = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
    return {"FITTED": fitted, "source": P_CYC + " FITTED (fitted to 29 Sep's card records: 33 runs of the same kernel, "
                                                "M1-M3; rms 1.8% of a minion's cycles; held out +5.0% / +7.5%)",
            "variant_b": "variant b = --variant m1 --cost fit --gen inc (E59's energy runs): M1's epilogue whole "
                         "(E_OUT per output tile), incremental generation as variant_constants() states it: G_TILE/2 "
                         "and G_SLICE + G_K/8 per slice"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "frozen-v2.json"))
    a = ap.parse_args()
    H, bands, var = m10_heldout()
    F = {
        "model": "load ledger v2 (Q166, calc-a): the joined load model revived by its retirement note's recipe",
        "frozen_pst": time.strftime("%a %d %b %Y %H:%M:%S %Z"),
        "repo_head_at_freeze": git("rev-parse", "HEAD"),
        "form": ("J_total = P_idle(card, T0) t + k_leak(card, T0) dT t + J_over_idle; J_over_idle = sum_ops (Z_f + D_kind)/R_f "
                 "v2 + sum_class cycles r_issue e_class v2 + awake_cycles e_awake v2 + sum_paths bytes (z + (r - z) phi) "
                 "+ mesh bytes hops p_hop; phi = w_set rho/0.5 + (1 - w_set) tau/0.5; dT = k_rise P_over_idle; "
                 "v2 = (V/V600)^2. See tools/ledger/ledger_v2.py."),
        "constants": {
            "w_set": const(0.70, "docs/reports/data/2026-11-01-e101-real-matmul/README.md R5 and R5b (the benchmark arm): "
                                 "a constant costs the path +2.09 / +1.74 / +2.43 W over zeros against random's +6.78 / "
                                 "+6.33 / +11.66 W (fp32 / fp16 / int8); the constants carry 7/32, 4/16 and 1/8 set bits "
                                 "and change none, so w_set = (ratio) / (rho / 0.5) = 0.703 / 0.550 / 0.834",
                           "post hoc (E101's measurements; E101 is IN SAMPLE for this term)", "share", band=[0.55, 0.83],
                           note="the mean of the three formats; band their range"),
            "issue_rate": const(0.37, "docs/energy-manual/03a-every-instruction.md, 'issue per hart per cycle' of the "
                                      "vector-integer class with both harts issuing (0.361-0.374)",
                                "measured (rate); its use for an epilogue or a generator's busy cycles is a hand choice",
                                "instructions per hart-cycle", band=[0.25, 0.60],
                                note="band a hand choice: a lone hart may issue faster, a store-bound one slower"),
            "awake_pj_per_hart_cycle": const(1.19 / (1024 * 600e6) * 1e12,
                                             "docs/energy-manual/02-awake.md and 07-composition.md §7.3: 1,024 minions "
                                             "stalled on one contended atomic draw 1.19 W [1.01-1.41] over idle (E23); "
                                             "per hart-cycle at 600 MHz",
                                             "measured (the stalled-minion figure); its use for a waiting hart a hand "
                                             "choice", "pJ per hart-cycle",
                                             band=[1.01 / (1024 * 600e6) * 1e12, 1.92 / (1024 * 600e6) * 1e12],
                                             note="band from the stalled figure's low end to the one-hart addi loop's "
                                                  "1.92 W (02-awake.md, aifoundry2)"),
            "k_rise_c_per_w": const(0.12, P_M10 + "/m10.json heat_4p5s.coef S|aifoundry3 0.1198, S|aifoundry1-c1 0.1194 "
                                          "C per W over idle (M10's 4.5 s window law)",
                                    "registered law (M10), carried to aifoundry2 by hand", "C per W",
                                    band=[0.09, 0.20],
                                    note="band a hand choice: the scored runs last 5-7 s, longer than the 4.5 s window"),
            "dram_bandwidth_gb_s": const(76.0, "docs/energy-manual/04-bytes-memory.md §4.1, tensor load from DRAM, 76 GB/s",
                                         "measured", "GB/s", band=[70.0, 82.0],
                                         note="band a hand choice; used only to forecast a DRAM-bound load's seconds"),
            "card_scale_a3_over_a2": const(0.963, "docs/findings/05-claims.md (E38): aifoundry3 switches 0.958-0.969 of "
                                                  "aifoundry2 at a matched die temperature; tools/ettelem/load_model.py "
                                                  "CARDS['aifoundry3']['scale']",
                                           "measured (E38)", "ratio", band=[0.958, 0.969],
                                           note="M10 has no aifoundry2 family; v2 carries M10's aifoundry3 D to "
                                                "aifoundry2 by this ratio"),
        },
        "awake_rule": ("a hart's time is priced once. The catalogue's per-byte and per-op prices were measured with "
                       "their issuing harts awake for the whole transfer (e_i = (P - P_idle) / rate), so a hart's "
                       "cycles blocked on its own tensor op or its own loads and stores are inside those prices up to "
                       "the probe's own time per byte; its instruction-bound cycles (an epilogue, a tile's set-up, a "
                       "generator's work beyond its stores) are priced as issue; only the rest of a running hart's "
                       "time, waiting on another hart or the host, is priced as awake"),
        "probe_rates_b_per_minion_cycle": {
            "scp_load": 2458e9 / (1024 * 600e6), "scp_store": 1230e9 / (1024 * 600e6),
            "dram_load": 76e9 / (1024 * 600e6), "dram_store": 76e9 / (1024 * 600e6),
            "source": "docs/energy-manual/04-bytes-memory.md §4.1, the GB/s column (2,458 / 1,230 / 76 / 76 over the "
                      "chip), per minion-cycle at 600 MHz: the time the catalogue's own probe took per byte"},
        "leak_slope_band_rel": [0.8, 1.25],
        "leak_slope_band_how": "a hand choice: the committed estimators of one card's slope spread about this much "
                               "(aifoundry3 at 58 C: 0.30-0.38 W/C, the footing-law README's table)",
        "zeros_anchor": zeros_anchors(),
        "kinds": build_kinds(H, bands),
        "m10_variant": var,
        "m10_bands": bands,
        "instr_classes": instr_classes(),
        "mem_paths": mem_paths(),
        "mesh_hop": mesh_hop(),
        "idle_laws": idle_laws(),
        "volts": {"aifoundry2": {"600": 0.5174, "800": 0.6174109375},
                  "aifoundry3": {"600": 0.521775}, "aifoundry1-c1": {"600": 0.499},
                  "source": "aifoundry2: tools/claims-v3/hpl/surface_hpl.py:31 (E64), as tools/ettelem/load_model.py "
                            "CARDS carries it; aifoundry3: E60 hl.json v_mean via load_model.CARDS; card 1: the energy "
                            "manual's catalogue median reading, 0.499 V (README) - used at 600 MHz only, where v2 = 1, "
                            "so E39's own busy_mv (v1's held-out leak) is not read"},
        "cycle_model": cycle_constants(),
        "held_out_leaks": {
            "v1's three, gone": "hop_pj_per_byte 1.753 (E43): no scored load reads a mesh term; CARDS c1 volts 0.4979 "
                                "(E39's own record): v2 reads card 1's kernel term from M10's card-1 rows and its volts "
                                "only at 600 MHz, where they cancel; E59_CYCLES_IDEAL 280.35 (E37's record): v2 prices "
                                "a tensor op per op, so no duty is needed",
            "v2's own, named": [
                "E39's and E37's die temperatures and E37's cycles per op are read from their own records as OPERATING "
                "POINTS (inputs), as v1 read them; no price comes from them",
                "E59's op, tile and row-tile counts, the planner's U and the host's model_s are read from E59's own "
                "plan.json (desk numbers the host wrote before each launch); its measured seconds feed only the "
                "'given its measured seconds' score",
                "the sparse-parity cycle constants were fitted on the same kernel's earlier runs of the same day (M1-M3), "
                "not on E59's energy runs",
                "E101 is in sample for w_set and the l2_stream price; E86's and E95's kernel terms come from M10 "
                "held out by kind but with each session's own random anchors (M10's term a)",
            ],
        },
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(F, f, indent=1, sort_keys=False)
        f.write("\n")
    print("wrote", os.path.relpath(a.out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
