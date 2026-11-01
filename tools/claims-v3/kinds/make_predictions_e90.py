#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E90 (Q130): write predictions-e90.json, E90's freeze, from committed sources only. Every number below is read
from the file it names (never retyped): E78's reduction (the reference cells), the sign-bit items of E65 (fp32 B),
E67 (fp32 A) and E79 (fp16 A and B, from its README's price tables), e90/e90.json (each tile's designed sign flips),
and Q130(n)'s predictor (real/make_real.py's fit_predictor / features / predict_D on E78's 51 kinds, unchanged).

    /usr/bin/python3 tools/claims-v3/kinds/make_predictions_e90.py      # writes predictions-e90.json

The sign-bit price model (the "bits" prediction). A sign kind's step over its reference is the price of the sign
bits it flips: for each side, the measured step of the item that flips that side's sign bit at every designed read
(E65 bit_31: B, 4,096 flips per fp32 op; E67 abit_31: A, 2,048; E79 b16_15: fp16 B jg, 8,192; E79 a16_15: fp16 A,
4,096; E79 README "How a price is counted") times the tile's own designed sign flips over that item's:
    P_bits = dW_B(item) * flips_B(tile) / flips_B(item) + dW_A(item) * flips_A(tile) / flips_A(item)
with flips counted by make_e90.sign_flips_per_op, the rule E65/E67/E79 used (an element read whose sign bit differs
from the previous read in the same lane, summed over the lanes, the broadcast A word once per column slot, wrapped
op to op).
"""
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "real"))

E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E86_JSON = "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json"
E65_HL = "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"
E67_HL = "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"
E67_HL_CLEAN = "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl-clean.json"
E79_README = "docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/README.md"
E90_JSON = "tools/claims-v3/kinds/e90/e90.json"
REUSED = ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json")
E90_BOX_FILES = ("tools/claims-v3/kinds/e90_common.py", "tools/claims-v3/kinds/run_e90.py",
                 "tools/claims-v3/kinds/reduce_e90.py", "tools/claims-v3/kinds/block_e90.sh",
                 "tools/claims-v3/kinds/queue_e90.sh", "tools/claims-v3/kinds/run_e90.sh",
                 "tools/claims-v3/kinds/make_e90.py")
# designed flips per op of the full-alternation items (E79 README, "How a price is counted"; E65 and E67 the same)
ITEM_FLIPS = {"fp32": {"B": 4096, "A": 2048}, "fp16": {"B": 8192, "A": 4096}}
FACTOR = 2.0            # R1/R2: PASS if the step's 95% upper bound <= FACTOR x P_bits, FAIL if its lower bound > it
STATIC_BAND = 0.30      # R3: E78-R3f's band for a static set bit (predictions-e78.json)
REP_BAND = 0.50         # R4: E86-R5's session-tie band for fp32/fp16 cells


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def e79_sign_row(text, heading):
    """The bit-15 (sign) row of the E79 README price table under `heading`: dW mean, its +-, fJ."""
    i = text.index(heading)
    seg = text[i:i + 4000]
    m = re.search(r"\|\s*15\s*\|\s*sign\s*\|\s*([0-9.]+)\s*±\s*([0-9.]+)\s*\|\s*\*\*(-?[0-9]+)\*\*\s*\|\s*\[(-?[0-9]+),\s*(-?[0-9]+)\]", seg)
    return {"dW": float(m.group(1)), "dW_pm95": float(m.group(2)), "fJ": int(m.group(3)),
            "fJ_ci95": [int(m.group(4)), int(m.group(5))], "table": heading}


def main():
    e78 = json.load(open(os.path.join(ROOT, E78_JSON)))
    e90 = json.load(open(os.path.join(ROOT, E90_JSON)))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items()}
    Dci = {n: v["D"]["ci95"] for n, v in e78["items"].items()}
    it65 = json.load(open(os.path.join(ROOT, E65_HL)))["cards"]["aifoundry3"]["items"]["bit_31"]
    it67 = json.load(open(os.path.join(ROOT, E67_HL)))["cards"]["aifoundry3"]["items"]["abit_31"]
    it67c = json.load(open(os.path.join(ROOT, E67_HL_CLEAN)))["cards"]["aifoundry3"]["items"]["abit_31"]
    txt79 = open(os.path.join(ROOT, E79_README)).read()
    b16 = e79_sign_row(txt79, "### fp16, B side (A = 1.0), jg layout")
    a16 = e79_sign_row(txt79, "### fp16, A side (B = 1.0)")
    price = {
        "fp32": {"B": {"dW": it65["d_p80"], "se": it65["d_p80_se"], "n": it65["d_n"],
                       "source": f"{E65_HL} cards.aifoundry3.items.bit_31.d_p80"},
                 "A": {"dW": it67["d_p80"], "se": it67["d_p80_se"], "n": it67["d_n"],
                       "source": f"{E67_HL} cards.aifoundry3.items.abit_31.d_p80 (E67's registered passes)"},
                 "A_clean_arm": {"dW": it67c["d_p80"], "se": it67c["d_p80_se"], "n": it67c["d_n"],
                                 "source": f"{E67_HL_CLEAN} cards.aifoundry3.items.abit_31.d_p80 (E67 A15, post hoc)"}},
        "fp16": {"B": {"dW": b16["dW"], "pm95": b16["dW_pm95"], "fJ": b16["fJ"], "fJ_ci95": b16["fJ_ci95"],
                       "source": f"{E79_README} table '{b16['table']}' row 15 (a bound: its interval spans 0)"},
                 "A": {"dW": a16["dW"], "pm95": a16["dW_pm95"], "fJ": a16["fJ"], "fJ_ci95": a16["fJ_ci95"],
                       "source": f"{E79_README} table '{a16['table']}' row 15"}},
    }

    def p_bits(t, fa, fb, a_key="A"):
        pb = price[t]["B"]["dW"] * fb / ITEM_FLIPS[t]["B"]
        pa = price[t][a_key]["dW"] * fa / ITEM_FLIPS[t]["A"]
        return pa + pb, pa, pb

    refs = e90["e78_references"]
    tiles = e90["tiles"]
    # Q130(n)'s predictor, unchanged, fitted on E78's 51 kinds and their committed tiles
    import make_real as mr  # noqa: E402
    P, rows = mr.fit_predictor(e78, ROOT)

    def qpred(t, raw):
        r = mr.predict_D(P, t, mr.features(raw, t), rows[t])
        return {"point_w": r["point_w"], "pi95_w": r["pi95_w"], "model": r["model"],
                "features_outside_e78_range": r["features_outside_e78_range"]}

    def raw_of(rel):
        return open(os.path.join(ROOT, rel), "rb").read()

    out_tiles = {}
    # --- the sign group: steps, each against a reference that runs in every pass
    steps = {}
    for t in ("fp32", "fp16"):
        s = tiles[f"{t}.signs"]["stats"]
        tot, pa, pb = p_bits(t, s["sign_flips_per_op_a"], s["sign_flips_per_op_b"])
        steps[f"{t}.signs-{t}.ones"] = {"rule": "E90-R1", "hi": f"{t}.signs", "lo": f"{t}.ones",
                                        "P_bits_w": round(tot, 4), "P_bits_a_w": round(pa, 4), "P_bits_b_w": round(pb, 4),
                                        "e78_lo_D_w": round(D[f"{t}.ones"], 4)}
        r = refs[f"{t}.randn"]
        tot, pa, pb = p_bits(t, r["sign_flips_per_op_a"], r["sign_flips_per_op_b"])
        steps[f"{t}.randn-{t}.abs_randn"] = {"rule": "E90-R2", "hi": f"{t}.randn", "lo": f"{t}.abs_randn",
                                             "P_bits_w": round(tot, 4), "P_bits_a_w": round(pa, 4),
                                             "P_bits_b_w": round(pb, 4), "e78_hi_D_w": round(D[f"{t}.randn"], 4)}
        steps[f"{t}.negabs_randn-{t}.abs_randn"] = {"rule": "E90-R3", "hi": f"{t}.negabs_randn",
                                                    "lo": f"{t}.abs_randn", "P_bits_w": 0.0, "band_w": STATIC_BAND}
    s = tiles["fp32.pm_pi"]["stats"]
    tot, pa, pb = p_bits("fp32", s["sign_flips_per_op_a"], s["sign_flips_per_op_b"])
    off = D["fp32.pi"] - D["anchor_pi"]       # E78: the file's pi against the host's built-in pi, same word
    steps["fp32.pm_pi-anchor_pi"] = {"rule": "E90-R1", "hi": "fp32.pm_pi", "lo": "anchor_pi",
                                     "P_bits_w": round(tot + off, 4), "P_bits_sign_only_w": round(tot, 4),
                                     "P_bits_a_w": round(pa, 4), "P_bits_b_w": round(pb, 4),
                                     "file_vs_builtin_pi_offset_w": round(off, 4),
                                     "offset_source": f"{E78_JSON} items.fp32.pi.D - items.anchor_pi.D",
                                     "e78_lo_D_w": round(D["anchor_pi"], 4)}
    # the clean-arm A price, reported beside (not a verdict)
    for k, v in steps.items():
        if v["rule"] in ("E90-R1", "E90-R2") and k.startswith("fp32"):
            hi = v["hi"]
            st = (tiles[hi]["stats"] if hi in tiles else refs[hi])
            tot_c, _, _ = p_bits("fp32", st["sign_flips_per_op_a"], st["sign_flips_per_op_b"], a_key="A_clean_arm")
            v["P_bits_w_E67_clean_arm"] = round(tot_c + (v.get("file_vs_builtin_pi_offset_w") or 0.0), 4)
        if v["rule"] in ("E90-R1", "E90-R2"):
            v["threshold_w"] = round(FACTOR * v["P_bits_w"], 4)
    for name, e in tiles.items():
        t = e["type"]
        rec = {"type": t, "group": e["group"], "sha256": e["sha256"], "stats": e["stats"],
               "q130n_predictor": qpred(t, raw_of("tools/claims-v3/kinds/e90/" + e["file"]))}
        if e["group"] == "redraw":
            c = e["rule_of"]
            rec["committed"] = c
            rec["D_pred_w"] = round(D[c], 4)            # the task's prediction: E78's measured value of the rule
            rec["D_pred_source"] = f"{E78_JSON} items.{c}.D.mean"
            rec["e78_committed_D_ci95_w"] = round(Dci[c], 4)
            craw = raw_of(f"tools/claims-v3/kinds/tiles/{t}/{c.split('.', 1)[1]}.bin")
            qc = qpred(t, craw)
            rec["q130n_committed_point_w"] = qc["point_w"]
            rec["q130n_delta_vs_committed_w"] = round(rec["q130n_predictor"]["point_w"] - qc["point_w"], 4)
        out_tiles[name] = rec
    # bits-model D points for the sign tiles (reported; the verdicts are on the paired steps)
    out_tiles["fp32.signs"]["D_pred_w"] = round(D["fp32.ones"] + steps["fp32.signs-fp32.ones"]["P_bits_w"], 4)
    out_tiles["fp16.signs"]["D_pred_w"] = round(D["fp16.ones"] + steps["fp16.signs-fp16.ones"]["P_bits_w"], 4)
    out_tiles["fp32.pm_pi"]["D_pred_w"] = round(D["anchor_pi"] + steps["fp32.pm_pi-anchor_pi"]["P_bits_w"], 4)
    for t in ("fp32", "fp16"):
        v = round(D[f"{t}.randn"] - steps[f"{t}.randn-{t}.abs_randn"]["P_bits_w"], 4)
        out_tiles[f"{t}.abs_randn"]["D_pred_w"] = v
        out_tiles[f"{t}.negabs_randn"]["D_pred_w"] = v
    out_tiles["int8.signs"]["D_pred_w"] = None
    out_tiles["int8.signs"]["note"] = ("no bits prediction: a +-1 sign change in int8 flips bits 1-7, and E79 has no "
                                       "int8 B-side price list that alternates (E79 A4); reported, scored only by "
                                       "E90-S2 (the predictor's interval)")
    for n in ("fp32.signs", "fp16.signs", "fp32.pm_pi", "fp32.abs_randn", "fp32.negabs_randn", "fp16.abs_randn",
              "fp16.negabs_randn"):
        out_tiles[n]["D_pred_source"] = "the E78 reference's D plus (or minus) P_bits of steps"

    reg = {
        "experiment": "E90", "title": "sign patterns and tile-to-tile spread (aifoundry3 card 0, 600 MHz)",
        "request": "Q130 evening round, critic items 6 and 13", "date": "2026-10-31",
        "registration": "tools/claims-v3/kinds/E90.md", "card": "aifoundry3 card 0",
        "inputs_frozen": {
            "e78_reduction": {"path": E78_JSON, "sha256": sha(E78_JSON)},
            "e86_reduction": {"path": E86_JSON, "sha256": sha(E86_JSON)},
            "e65_hl": {"path": E65_HL, "sha256": sha(E65_HL)},
            "e67_hl": {"path": E67_HL, "sha256": sha(E67_HL)},
            "e67_hl_clean": {"path": E67_HL_CLEAN, "sha256": sha(E67_HL_CLEAN)},
            "e79_readme": {"path": E79_README, "sha256": sha(E79_README)},
            "make_real": {"path": "tools/claims-v3/kinds/real/make_real.py",
                          "sha256": sha("tools/claims-v3/kinds/real/make_real.py")},
            "e90_json": {"path": E90_JSON, "sha256": sha(E90_JSON)},
        },
        "harness": {
            "reused_unchanged_sha256": {r: sha(r) for r in REUSED},
            "e90_files_sha256": {r: sha(r) for r in E90_BOX_FILES},
            "e90_json_sha256": sha(E90_JSON),
        },
        "plan": {"passes": [9010, 9011, 9012], "smoke": 9001, "runs_per_pass": 42,
                 "items_per_pass": "the tie twice, E78's six anchors three times, E90's 17 tiles and 5 E78 kinds once"},
        "card_budget": {"card_minutes_max": 30, "queue_budget_min": 26, "queue_deadline": "22:25",
                        "no_session_after": "21:45 PDT", "every_run_ends_by": "22:30 PDT"},
        "sign_bit_prices": price,
        "item_flips": ITEM_FLIPS,
        "steps": steps,
        "tiles": out_tiles,
        "e78_reference": {n: {"D_w": round(D[n], 4), "ci95_w": round(Dci[n], 4)} for n in
                          ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones", "fp16.ones", "anchor_pi",
                           "fp32.sparse50", "fp16.nn_like", "fp16.uniform01", "int8.ones", "int8.neg_ones",
                           "int8.highbit", "fp32.pi", "fp32.neg_ones", "fp16.neg_ones")},
        "rules": {
            "E90-R1": {"what": "random signs at a fixed magnitude cost what their sign-bit flips cost",
                       "steps": ["fp32.signs-fp32.ones", "fp16.signs-fp16.ones", "fp32.pm_pi-anchor_pi"],
                       "per_step": "paired per pass; PASS if the 95% upper bound <= FACTOR x P_bits, FAIL if the 95% "
                                   "lower bound > FACTOR x P_bits, else INCONCLUSIVE", "factor": FACTOR,
                       "rule": "PASS if all three steps pass; FAIL if any fails; else INCONCLUSIVE"},
            "E90-R2": {"what": "random signs on random magnitudes cost what their sign-bit flips cost",
                       "steps": ["fp32.randn-fp32.abs_randn", "fp16.randn-fp16.abs_randn"],
                       "per_step": "as E90-R1", "factor": FACTOR, "rule": "PASS if both pass; FAIL if either fails"},
            "E90-R3": {"what": "a static set sign bit costs nothing",
                       "steps": ["fp32.negabs_randn-fp32.abs_randn", "fp16.negabs_randn-fp16.abs_randn"],
                       "per_step": f"paired per pass; PASS if the 95% interval lies inside +-{STATIC_BAND} W, FAIL if it "
                                   "lies entirely outside, else INCONCLUSIVE", "band_w": STATIC_BAND,
                       "rule": "PASS if both pass; FAIL if either fails"},
            "E90-R4": {"what": "E78's committed tile represents its rule (the prediction: E78's measured value)",
                       "kinds": ["fp32.sparse50", "fp16.nn_like", "fp16.uniform01"],
                       "per_kind": f"mean over the three fresh draws of D(draw) - D(committed tile), paired per pass; "
                                   f"PASS if its 95% interval lies inside +-{REP_BAND} W, FAIL if it lies entirely "
                                   "outside, else INCONCLUSIVE", "band_w": REP_BAND,
                       "rule": "PASS if all three kinds pass; FAIL if any fails"},
            "E90-R5": {"what": "Q130(n)'s predictor tracks the draws (its delta against the committed tile)",
                       "per_draw": "measured paired D(draw) - D(committed) against q130n_delta_vs_committed_w",
                       "rule": "PASS if rms over the nine draws <= 0.50 W and no draw whose predicted |delta| >= 0.30 W "
                               "is resolved (95%) on the other side of zero; FAIL if rms > 1.00 W or any such draw "
                               "is; else INCONCLUSIVE"},
            "E90-S1": {"what": "the session tie (reported, not a model test)",
                       "cells": {"fp32.randn": 0.5, "fp16.randn": 0.5, "fp32.ones": 0.5, "fp16.ones": 0.5,
                                 "anchor_pi": 0.5, "fp32.sparse50": 0.5, "fp16.nn_like": 0.5,
                                 "fp16.uniform01": 0.5, "int8.full": 0.25},
                       "rule": "each cell's D within its band of E78's; a failure means the session moved"},
            "E90-S2": {"what": "Q130(n)'s predictor's 95% interval holds every E90 tile",
                       "rule": "count of the 17 E90 tiles whose D lies inside q130n_predictor.pi95_w; PASS if >= 14"},
        },
        "not_scored_if": "fewer than 3 kept passes in the primary reduction: then every rule is scored on the "
                         "registered dips-removed arm (E86's posthoc_dips method), labelled as that arm; fewer than "
                         "3 there too: NOT SCORED. A quantity with fewer than 3 kept passes is unresolved.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e90.json"), "w"), indent=1)
    for k, v in steps.items():
        print(f"{k:36s} P_bits {v['P_bits_w']:+.3f} W  threshold {v.get('threshold_w', v.get('band_w'))}"
              + (f"  clean-arm {v['P_bits_w_E67_clean_arm']:+.3f}" if "P_bits_w_E67_clean_arm" in v else ""))
    for n, v in out_tiles.items():
        q = v["q130n_predictor"]
        print(f"{n:22s} D_pred {v.get('D_pred_w')}  Q130(n) {q['point_w']} {q['pi95_w']}"
              + (f"  dq {v['q130n_delta_vs_committed_w']:+.3f}" if "q130n_delta_vs_committed_w" in v else "")
              + (f" outside {q['features_outside_e78_range']}" if q["features_outside_e78_range"] else ""))
    print("sha256 predictions-e90.json", hashlib.sha256(open(os.path.join(HERE, "predictions-e90.json"), "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
