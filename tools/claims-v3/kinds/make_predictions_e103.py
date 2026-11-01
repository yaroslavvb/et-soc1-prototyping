#!/usr/bin/env python3
"""E103 (Q132): freeze the registration: predictions-e103.json, from e103/selection.json and the files' hashes. Standard library only.

    python3 tools/claims-v3/kinds/make_predictions_e103.py

The thresholds are here and in E103.md, set before any E103 data. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
D = "docs/reports/data"


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    sel = json.load(open(os.path.join(HERE, "e103", "selection.json")))
    e94 = json.load(open(os.path.join(HERE, "predictions-e94.json")))
    reused = e94["harness"]["reused_unchanged_sha256"]
    bad = [r for r, w in reused.items() if sha(r) != w]
    assert not bad, bad
    nod = json.load(open(os.path.join(ROOT, D, "2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")))["items"]
    tiles = {}
    for k, r in sel["chosen"].items():
        tiles[k] = {"type": r["type"], "kind": r["name"], "group": sel["group"][k],
                    "pred": {"M": r["M"], "lo95": r["lo95"], "hi95": r["hi95"], "half95": r["half95"], "launch_points_w": r["launch_points_w"], "terms_w": r["terms_w"],
                             "M2": r["M2"], "Mall": r["Mall"], "q130n": r["q130n"], "flop": r["flop"], "gate_law": r["gate_law"], "gate": r["gate_closes"], "disagreement_w": r["dis"],
                             "q130n_outside_e78_range": r["q130n_outside_e78_range"]},
                    "bus_bits_per_op": r["bus_bits_per_op"], "check_mismatch_words": r["check_mismatch_words"]}
    files = [f"{K}/e103_common.py", f"{K}/run_e103.py", f"{K}/block_e103.sh", f"{K}/queue_e103.sh", f"{K}/run_e103.sh", f"{K}/reduce_e103.py", f"{K}/score_e103.py", f"{K}/collect_e103.sh"]
    reg = {
        "experiment": "E103",
        "title": "a blind test built to break the bench's power model, on aifoundry1 card 1 at 600 MHz",
        "request": "Q132, item 6 of the kinds page's section 11: a power model that predicts every kind",
        "date": "2026-11-01",
        "registration": f"{K}/E103.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {
            "bench_counts_of_e78": {"path": f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json", "sha256": sha(f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json")},
            "e78_reduction": {"path": f"{D}/2026-10-31-e78-kinds-energy-matrix/e78.json", "sha256": sha(f"{D}/2026-10-31-e78-kinds-energy-matrix/e78.json")},
            "e82_nodips": {"path": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json", "sha256": sha(f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")},
            "selection": {"path": f"{K}/e103/selection.json", "sha256": sha(f"{K}/e103/selection.json")},
            "pool_predictions": {"path": f"{K}/e103/pool-predictions.json", "sha256": sha(f"{K}/e103/pool-predictions.json")},
        },
        "harness": {"reused_unchanged_sha256": reused, "e103_json_sha256": sha(f"{K}/e103/e103.json"), "e103_files_sha256": {f: sha(f) for f in files}},
        "plan": {"passes": [10310, 10311, 10312], "smoke": 10301, "runs_per_pass": 2 + 18 + len(tiles), "items_per_pass": f"the tie twice, E78's six anchors three times, E103's {len(tiles)} tiles once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2, "min_tile_passes": 2},
        "card_budget": {"card_minutes_about": 25, "queue_budget_s": 1620, "first_pass_estimate_s": 500, "queue_deadline": "2026-11-01 07:00 PST", "every_run_ends_by": "07:15 PST"},
        "models": sel["models"],
        "e82_per_type_scale_for_q130n_and_flop": sel["e82_per_type_scale_for_q130n_and_flop"],
        "tiles": tiles,
        "session_tie": {"reference": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json items.<cell>.D.mean (dips removed, as E103's primary)",
                        "cells": {c: {"ref_w": round(nod[c]["D"]["mean"], 4), "band_w": b} for c, b in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "rules": {
            "E103-R1": {"what": "the model's accuracy on the float tiles: rms(D - M4) over every fp32 and fp16 tile", "pass_w": 0.60, "fail_w": 1.00},
            "E103-R2": {"what": "the model beats the named null on the float tiles: rms(Q130(n)) - rms(M4), 95% over tiles", "null": "Q130(n)'s predictor (real/make_real.py, fitted on E78's 51 kinds, unchanged) divided by E82's per-type card scale"},
            "E103-R3": {"what": "the model beats E92's flop-price refit on the float tiles", "null": "posthoc-fit.json's 'four prices + flops' per type, divided by E82's per-type card scale. It saw E92; the bench's M4 did not"},
            "E103-R4": {"what": "int8's own terms on the int8 tiles: rms(D - I3)", "pass_w": 0.40, "fail_w": 0.80},
            "E103-R5": {"what": "I3 beats Q130(n) on the int8 tiles", "null": "the same"},
            "E103-R6": {"what": "the bus price earns its term: rms(M2) - rms(M4) on the float tiles"},
            "E103-R7": {"what": "the frozen 95% intervals: the share of all tiles whose D lies inside", "pass_at_least": 0.80, "fail_below": 0.50},
            "E103-R8": {"what": "the A side's named weak spot: mean (D - T)/(M4 - T) over the float h_a_ and o_a_ tiles, T M4's frozen clock term, 95% over tiles", "persists_below": 0.95, "gone_inside": [0.95, 1.05]},
            "E103-R9": {"what": "gated kinds' named weak spot: mean D - M4 over float tiles with the gate closing at least 10% of slots, 95% over tiles", "gate_closes_at_least": 0.10, "band_w": 0.30},
            "E103-S1": {"what": "the session tie against E82, dips removed: every cell inside its band"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out of every rule and named.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e103.json"), "w"), indent=1)
    print("tiles", len(tiles), "runs per pass", reg["plan"]["runs_per_pass"])


if __name__ == "__main__":
    main()
