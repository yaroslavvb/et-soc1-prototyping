#!/usr/bin/env python3
"""Q140(q): the 82 W rule for E169's six shapes (REGISTRATION.md A8's rule applied to part B's designs): fp32 zeros bursts, so the
predicted peak is E146's P0(800) for fp32 zeros on the desk's 32 MB split (make_predictions_e146.levels0, unchanged) + 8.51 W (G3's
frozen margin). Adds a "peak" record to predictions-e169.json, before any E169 claim.

    /usr/bin/python3 -B peaks_e169.py
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g4_model as G4  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e169.json")))
M146, _ = G4._m146()
for s, c in P["shapes"].items():
    MB, NB, KB = c["blocks"]
    G4.add_shape146(s, MB, NB, KB)
    lev = M146.levels0(s, "fp32", "zeros")
    c["peak"] = {"P0_800_fp32_zeros_w": round(lev[800], 2), "predicted_peak_w": round(lev[800] + 8.51, 2), "under_82_w": lev[800] + 8.51 <= 82.0}
P["peak_rule"] = "predicted peak = E146's P0(800) for fp32 zeros on the desk's 32 MB split + 8.51 W (G3's frozen margin) <= 82 W; E158's 98 zeros bursts peaked at 36.1 W board"
json.dump(P, open(os.path.join(HERE, "predictions-e169.json"), "w"), indent=1)
for s, c in P["shapes"].items():
    print(s, c["arm"], c["peak"])
