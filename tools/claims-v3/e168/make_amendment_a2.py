#!/usr/bin/env python3
"""E168 (Q141(o)): the machine-readable half of amendment A2 to Q140(q)'s registration (REGISTRATION-A2-cold-int8-zeros.md beside
this file). Desk only: no card, no device command, and no model is run. Standard library only.

    /usr/bin/python3 -B tools/claims-v3/e168/make_amendment_a2.py > tools/claims-v3/e168/amendment-a2.txt   (writes predictions-e168-a2.json)

It COPIES, and computes no new prediction. From Q140(q)'s frozen predictions-e168.json (e39d06da; sha256 430f4afa..., the file
frozen-sha256-e168.json pins), it takes the g4 block and the S2 int8 zeros cell, and writes them under two labels:

  S2-int8-zeros-warm55   the frozen cell, every field unchanged (hold 7 of the frozen order);
  S2-int8-zeros-cold     A2's added hold, the 10th, after the nine: the same values string, P0 levels, predicted peak and
                         both_nominal_starts, with its G4 and G3 numbers taken from the frozen cell's both_nominal_starts.cold
                         (the chain at rest at 46.0 C), as Q140(q)'s amendment A1 item 5 says ("the nominal cold prediction is
                         already frozen in that table").

score_e168.score(<session dir>, ppath=<predictions-e168-a2.json>) then scores both holds with the frozen code from each hold's own
measured start (the registered primary for every E168 hold), and only those two (score_e168.build scores the labels its predictions
file names). The start dependence's nominal numbers below are differences of frozen numbers. Nothing here changes a frozen file.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G4D_REL = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride"
PRED_REL = f"{G4D_REL}/predictions-e168.json"
PRED_SHA256 = "430f4afa266a30c35f3e4da44ebef9fbf1d1186c00ceb5e2e8ae312c8c168583"   # frozen-sha256-e168.json (e39d06da), re-checked by 1bfaa4e4's sidecar
WARM, COLD = "S2-int8-zeros-warm55", "S2-int8-zeros-cold"
OUT = os.path.join(HERE, "predictions-e168-a2.json")


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    p = os.path.join(LAB, PRED_REL)
    got = sha256(p)
    if got != PRED_SHA256:
        print(f"refused: {PRED_REL} sha256 {got}, frozen {PRED_SHA256}")
        return 2
    P = json.load(open(p))
    w = P["cells"][WARM]
    nom = w["both_nominal_starts"]
    # the frozen cell's own G4 / G3 numbers are its warm55 nominal: the copy below relies on that, so check it
    assert w["G4"] == nom["warm55"]["G4"] and w["G3_as_frozen"] == nom["warm55"]["G3_as_frozen"], "the frozen warm cell is not its warm55 nominal"
    cold = {k: copy.deepcopy(v) for k, v in w.items() if k not in ("G4", "G3_as_frozen", "E136_law", "start")}
    cold["start"] = "cold"
    cold["G4"] = copy.deepcopy(nom["cold"]["G4"])
    cold["G3_as_frozen"] = copy.deepcopy(nom["cold"]["G3_as_frozen"])
    cold["copied_from"] = (f"{PRED_REL} cells.{WARM}: values, P0_w, predicted_peak_w, runs_as_designed, int8_full_P0_w and both_nominal_starts "
                           f"unchanged; G4 and G3_as_frozen = its both_nominal_starts.cold (the chain at rest at 46.0 C). E136_law is not copied: the "
                           f"frozen file computes it at the warm start only, and score_e168.score computes E136's law from each hold's measured start")
    order = list(P["design"]["order"]) + [COLD]

    def d(a, b):
        return round(a - b, 3)
    g4c, g4w = nom["cold"]["G4"], nom["warm55"]["G4"]
    g3c, g3w = nom["cold"]["G3_as_frozen"], nom["warm55"]["G3_as_frozen"]
    sd = {
        "what": ("A2's reported test of G4's start dependence: the measured window board of S2-int8-zeros-cold minus that of S2-int8-zeros-warm55 "
                 "(the same session, the same shape, format and values string), against G4's difference computed the same way"),
        "nominal_frozen": {
            "G4": {"w": d(g4c["w"], g4w["w"]), "die": d(g4c["die"], g4w["die"]), "die_start": d(g4c["die_start"], g4w["die_start"]),
                   "cold": g4c, "warm55": g4w},
            "G3_as_frozen": {"w": d(g3c["w"], g3w["w"]), "die": d(g3c["die"], g3w["die"]), "cold": g3c, "warm55": g3w},
            "note": "differences of predictions-e168.json's frozen both_nominal_starts numbers; no model is run here",
        },
        "E159_context": {
            "measured_spread_w": 0.057, "G4_spread_w": 0.442, "G3_as_frozen_spread_w": 0.097, "starts_c": [57.4, 52.46, 51.58],
            "source": f"{G4D_REL}/checks-g4.json ii_E159_zeros_spread (README check (ii)): E159's three fp32 zeros holds, three shapes",
        },
        "measured": "dW_meas = meas.w(S2-int8-zeros-cold) - meas.w(S2-int8-zeros-warm55), each score_e168.build's window mean (the in-kernel samples of the last 40 s)",
        "predicted": ("dW_G4 = pred.G4.w(cold) - pred.G4.w(warm55), each score_e168.score's G4 from that hold's own measured start (the primary path); "
                      "dW_G3 the same with G3 as frozen; dW_E136 the same with E136's law; the frozen nominal differences beside"),
        "reading": {
            "rule": ("with h = dW_G4 / 2 (half G4's mechanical difference): 'G4's start dependence SUPPORTED' if dW_meas >= +h; 'NO START DEPENDENCE "
                     "(E159's reading)' if -h < dW_meas < +h; 'OPPOSITE SIGN: the window board falls with the start, the direction of a leakage law in "
                     "the absolute die' if dW_meas <= -h. If dW_G4 <= 0.2 W the test has no power and is labelled so, with no reading"),
            "reported_beside": ["dW_meas - dW_G4", "dW_meas - dW_G3", "the window die difference, measured against G4's", "both holds' measured starts"],
            "counted_in_A7": False,
        },
    }
    out = {
        "what": "Q141(o): amendment A2 to Q140(q)'s registration for E168 - a cold int8 zeros hold at S2; every number copied from the frozen predictions-e168.json, none computed",
        "date": "2026-11-04",
        "amends": {"registration": "49575094", "predictions_and_scorer": "e39d06da", "A1_and_sidecar": "1bfaa4e4"},
        "source": {"path": PRED_REL, "sha256": got},
        "g4": copy.deepcopy(P["g4"]), "g4_sha256": P["g4_sha256"],
        "rules": {"per_hold_reported": dict(P["rules"]["per_hold"]), "counted_in_A7": False,
                  "A7": "unchanged: the nine frozen holds alone, scored by score_e168.score with predictions-e168.json as frozen"},
        "design": {"added_hold": COLD, "position": "the 10th and last, after the nine of the frozen order", "order_with_A2": order,
                   "hold": dict(P["design"]["hold"], starts={"cold": "the card at rest: the die mean read 46 C or less, waiting at most 360 s"}),
                   "budget": "about 8 card-minutes more (a rest from about 60 C to 46 C, about 3-4.5 min by Q138(t)'s frozen chain and at most 6, then the 141 s planned hold)",
                   "power_rule": f"predicted peak {w['predicted_peak_w']} W (the frozen cell's, P0(800) + 8.51 W) <= 82 W: runs as designed"},
        "start_dependence": sd,
        "cells": {WARM: copy.deepcopy(w), COLD: cold},
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"E168 amendment A2 (Q141(o)): copied from {PRED_REL} (sha256 {got}, as frozen)")
    print(f"  {COLD}: values {cold['values']}; P0 600/700/800 {cold['P0_w']}; predicted peak {cold['predicted_peak_w']} W")
    print(f"    G4 (frozen nominal cold, from 46.0 C): {json.dumps(g4c)}")
    print(f"    G3 as frozen (nominal cold):          {json.dumps(g3c)}")
    print(f"  {WARM} (hold 7, unchanged): G4 {json.dumps(g4w)}")
    print(f"  start dependence, frozen nominal: G4 cold - warm {sd['nominal_frozen']['G4']['w']:+.3f} W, window die {sd['nominal_frozen']['G4']['die']:+.3f} C; "
          f"G3 as frozen {sd['nominal_frozen']['G3_as_frozen']['w']:+.3f} W")
    print(f"  E159's three zeros holds: measured spread {sd['E159_context']['measured_spread_w']} W, G4 {sd['E159_context']['G4_spread_w']} W")
    print(f"  order with A2: {order}")
    print(f"wrote {os.path.relpath(OUT, LAB)} sha256 {sha256(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
