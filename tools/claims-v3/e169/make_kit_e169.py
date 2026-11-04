#!/usr/bin/env python3
"""E169 (Q141(s)): the kit's run parameters, from frozen inputs only. None of them is a scored prediction. Writes kit-e169.json;
prints kit-e169.txt. Standard library only; desk only (no card, no device).

    nice -n 10 python3 -B tools/claims-v3/e169/make_kit_e169.py > tools/claims-v3/e169/kit-e169.txt

WHAT IT WRITES (REGISTRATION-A2.md D3, D7, D8):
  cells       every label a session runs (the six E169 shapes in fp32, fp16 and int8; E158's four tie rungs in fp32), its values
              string (the shape as rgm136's argument, the format's zero tile) and its admission entry for E105's rule:
                * E169's shapes, fp32: the frozen predicted peak, predictions-e169.json peak.predicted_peak_w (E146's P0(800) for fp32
                  zeros on the desk's 32 MB split + 8.51 W, G3's margin), unchanged;
                * E169's shapes, fp16 and int8: the same rule through the same code (E146's desk split reuse_e146.split(.., 32) and
                  make_predictions_e146.levels0, as peaks_e169.py runs them through g4_model.add_shape146), which must reproduce the
                  six frozen fp32 peaks to 0.01 W first, else this script stops;
                * the ties: E158's frozen admission entry (predictions-e158.json admission), unchanged;
              and c600 (E146's c600 for the cell; the toy card's power in the dry run, and E105's c_ref_w).
  smoke       the smoke's four cells (P1 fp32, N2 fp16, P3 int8, N3 fp32) and their cycles per op at 800 MHz for the queue's 50-250%
              check: STRICT's frozen T800 x 800 (predictions-e169.json), as E158 used STRICT-C's.
  relation    E101's relation as E158 used it (predictions-e158.json relation: B at 600/700/800 MHz, s800), which E126's collect()
              and the protocol read.
  rules       R2_clock_buys, E119's clock_x rule as E158 registered it (predictions-e158.json rules.R2_clock_buys), unchanged.
  stops       the session's stops and limits (D7): abs_stop_c 76 C, board_cap_w 60 W on 3 samples, limit_p800_w 82 W, peak_lock_w 60 W.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146"))
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146/desk"))
import make_predictions_e146 as M146  # noqa: E402  (E146's module as frozen: E136's power law, E119's relation)
import reuse_e146 as RD  # noqa: E402  (E146's desk: split())

PRED169 = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/predictions-e169.json"
PRED158 = "tools/claims-v3/e158/predictions-e158.json"
FROZEN = {PRED169: "38ee500fa1e66107ef5c544688263b1e988fb5a675bdee05f9876df1432cf19f"}
TILES = "tools/claims-v3/kinds/tiles"
TYPES = ("fp32", "fp16", "int8")
E169 = ("N1", "P1", "N2", "P2", "N3", "P3")
TIES = ("K4n7", "K4n8", "K6n5", "K6n4")
SMOKE = (("P1", "fp32"), ("N2", "fp16"), ("P3", "int8"), ("N3", "fp32"))
MARGIN_W = 8.51
STOPS = {"abs_stop_c": 76, "board_cap_w": 60, "cap_consecutive": 3}
LIMIT_W, LOCK_W = 82.0, 60.0


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def values(arm, t):
    return f"{arm}:tiles:{TILES}/{t}/zeros.bin"


def main():
    for rel, h in FROZEN.items():
        if sha256(os.path.join(LAB, rel)) != h:
            raise SystemExit(f"refused: {rel} differs from its bytes at e39d06da")
    P = json.load(open(os.path.join(LAB, PRED169)))
    Q = json.load(open(os.path.join(LAB, PRED158)))
    S = P["shapes"]
    cells, adm, worst = {}, {"rest": {"fixed_p800_w": 30.0}}, 0.0
    for s in E169:
        MB, NB, KB = S[s]["blocks"]
        label = f"e169_{s}"
        M146.DESK["shapes"][label] = {"lines": {"32MB": RD.split(("large", MB, NB, KB), 32)}, "store_every_ops": KB * 32}
        for t in TYPES:
            lev = M146.levels0(label, t, "zeros")
            c6 = M146.c600(label, t, "zeros")
            peak = round(lev[800] + MARGIN_W, 2)
            if t == "fp32":
                frozen = S[s]["peak"]["predicted_peak_w"]
                worst = max(worst, abs(peak - frozen), abs(round(lev[800], 2) - S[s]["peak"]["P0_800_fp32_zeros_w"]))
                est, src = frozen, "predictions-e169.json peak.predicted_peak_w (frozen, e39d06da)"
            else:
                est, src = peak, "E146's P0(800) for zeros on the desk's 32 MB split + 8.51 W, the frozen fp32 rule's code (this kit)"
            lab = f"{s}-{t}-zeros"
            cells[lab] = {"shape": s, "arm": S[s]["arm"], "type": t, "values": values(S[s]["arm"], t), "P0_w": {str(f): round(v, 3) for f, v in lev.items()},
                          "c600_w": round(c6, 3), "fixed_p800_w": est, "estimate_source": src}
            adm[lab] = {"c_ref_w": round(c6, 3), "fixed_p800_w": est}
    if worst > 0.0051:
        raise SystemExit(f"refused: the fp32 peaks recomputed here differ from the frozen ones by {worst:.3f} W")
    for s in TIES:
        lab = f"{s}-fp32-zeros"
        e = Q["admission"][lab]
        arm = Q["laws"][f"{s}.fp32"]["arm"]
        cells[lab] = {"shape": s, "arm": arm, "type": "fp32", "values": values(arm, "fp32"), "c600_w": e["c_ref_w"], "fixed_p800_w": e["fixed_p800_w"],
                      "estimate_source": "predictions-e158.json admission (frozen, 2cfc4525)"}
        adm[lab] = dict(e)
    smoke = {f"{s}-{t}-zeros": round(S[s][t]["STRICT"]["T800"] * 800.0, 1) for s, t in SMOKE}
    top = max(v["fixed_p800_w"] for v in cells.values())
    rel = Q["relation"]
    out = {"what": "E169's kit parameters (REGISTRATION-A2.md D3, D7, D8): admission entries, the smoke's cycles, the relation and the clock rule; from frozen inputs only, no scored prediction",
           "date": "2026-11-04", "frozen_inputs_sha256": {PRED169: FROZEN[PRED169], PRED158: sha256(os.path.join(LAB, PRED158))},
           "fp32_peaks_reproduced_worst_w": round(worst, 4), "cells": cells, "admission": adm, "smoke_cells": [f"{s}-{t}-zeros" for s, t in SMOKE],
           "smoke_cycles": smoke, "relation": rel, "rules": {"R2_clock_buys": Q["rules"]["R2_clock_buys"]}, "safety": dict(STOPS),
           "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "highest_estimate_w": top}
    json.dump(out, open(os.path.join(HERE, "kit-e169.json"), "w"), indent=1)
    print("E169 kit parameters, from frozen inputs only (predictions-e169.json checked against e39d06da: OK)")
    print(f"the six frozen fp32 peaks recomputed through E146's desk split and levels0: worst |diff| {worst:.4f} W (must be under 0.0051)")
    for lab, c in cells.items():
        print(f"  {lab:15s} {c['values']:52s} estimate {c['fixed_p800_w']:6.2f} W  c600 {c['c600_w']:6.3f} W  ({c['estimate_source'].split(' (')[0]})")
    print(f"highest estimate {top} W (limit {LIMIT_W} W, lock {LOCK_W} W); stops {STOPS}")
    print(f"smoke cells and their cycles per op at 800 MHz (STRICT's frozen T800 x 800): {smoke}")
    print("wrote kit-e169.json")


if __name__ == "__main__":
    main()
