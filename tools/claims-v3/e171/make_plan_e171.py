#!/usr/bin/env python3
"""E171 (Q142(k6)): write plan-e171.json, the machine form of E171.md's session plan (the passes and plans, the budget, the stops, the smoke,
the sessions that must carry a C log, the scorer's call), from E171.md's text and the frozen pool-8 files. It refuses if the smoke list it
derives by E171.md's rule differs from e171_common.SMOKE_ITEMS, or if a frozen file differs. Standard library only.

    python3 -B tools/claims-v3/e171/make_plan_e171.py
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e171_common as e  # noqa: E402

CARD = "aifoundry3"


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def smoke_by_rule(pred):
    T, S = pred["tiles"], pred["sets"]
    D = {n: r["M10"]["D_stated_w"] for n, r in T.items()}
    D9 = {n: r["M9"]["D_stated_w"] for n, r in T.items()}
    hot = max((n for n in T if not T[n]["anchor_role"]), key=lambda n: (D[n], n))
    part = {t: max((n for n in S["N1"] if T[n]["type"] == t), key=lambda n: (abs(D[n] - D9[n]), n)) for t in ("fp16", "int8")}
    return ["anchor_pi", "fp32.zeros", "fp32.randn", hot, "fp32.anchor7_zeros", part["fp16"], "fp16.zeros", part["int8"], "int8.zeros",
            "fp32.anchor8_check_randn_319f73"], {"hottest": [hot, D[hot]], "fp16": [part["fp16"], D[part["fp16"]] - D9[part["fp16"]]],
                                                "int8": [part["int8"], D[part["int8"]] - D9[part["int8"]]]}


def main():
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    pred = json.load(open(e.PRED_JSON))
    smoke, why = smoke_by_rule(pred)
    if tuple(smoke) != tuple(e.SMOKE_ITEMS):
        raise SystemExit(f"refusing: the smoke by E171.md's rule {smoke} is not e171_common.SMOKE_ITEMS {list(e.SMOKE_ITEMS)}")
    plan = {
        "_what": "E171 (Q142(k6)): the machine form of E171.md's session plan; written by make_plan_e171.py after the registration (4441083f)",
        "experiment": "E171", "card": CARD, "registration": "tools/claims-v3/e171/E171.md", "registration_sha256": sha("tools/claims-v3/e171/E171.md"),
        "registration_commit": "4441083f",
        "frozen_inputs": {rel: h for rel, h in e.FROZEN.items()},
        "frozen_in": {"pool_and_predictions": "4576fb90", "converter_rule": "ebf68c52", "freeze_note": "dfe226f1", "pool8_registration": "3e97f583",
                      "A1": "8a8fa34c", "A2": "68a7c322", "predictor": "9d81d254", "predictor_a2": "97765c0a", "design": "153b720f"},
        "plan": {
            "passes": {"kinds": [17110, 17119], "short": [17120, 17129], "smoke": 17101, "stoptest": 17102},
            "plans": {"FULL": {"seq": [17110, 17111, 17112, 17113], "budget_s": 4200, "note": "17113 only if the budget rule admits it"},
                      "TWO": {"seq": [17110, 17111], "budget_s": 2280}, "SHORT": {"seq": [17120, 17121], "budget_s": 1800}},
            "reserve_s": 60, "gap_s": 10, "first_estimate_s": {"kinds": 900, "short": 820},
            "runs_per_pass": {"kinds": 84, "short": 75}, "launches_per_pass_with_burnins": {"kinds": 86, "short": 77},
            "short_drops": list(e.P2_KINDS),
            "stops": {"kinds": {"board_w": 65.0, "die_shire0_c": 70.0}, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "max_c": 70},
            "smoke": list(e.SMOKE_ITEMS), "smoke_rule": why,
            "min_kept_passes_scored": 2, "min_tile_passes": 2,
            "c_log_sessions": {"rule": "e171-smoke/p17101, and every e171/p171NN (17110-17129, never .attempt-*) whose runs.jsonl holds a launch "
                                       "record, whatever its block status; e171-stoptest/p17102 must hold no launch record and no C record",
                               "checker": "tools/claims-v3/p8-600/ccsessions_p8.py --run E171"},
            "expected_card_minutes": {"FULL_four_passes": [60, 62], "FULL_three_passes": [45, 46], "TWO": 31, "SHORT": 28, "cap": 70},
            "time_gates": "E171_LATEST_START and E171_DEADLINE required, set at his go",
        },
        "scorer": {"code": "tools/claims-v3/p8-600/score_p8_600.py", "commit": "a518aa11",
                   "call": "score --run E171 --reduction <data>/e171.json --raw <raw copy> --ccheck <out>/ccheck/ccheck-all.json [--arm ...]",
                   "primary_reduction": "reduce_e171.py --leak 0.20563713796102187 --no-refit --drop-dips",
                   "arms": {"session_own": "leakage auto, dips kept", "auto_dips_removed": "--drop-dips", "kfrozen_dips_kept": "--leak K --no-refit",
                            "leak0.1994": "--leak 0.1994 --no-refit --drop-dips", "leak0.3803": "--leak 0.3803 --no-refit --drop-dips",
                            "leak0": "--leak 0 --no-refit --drop-dips", "gates_off": "--leak K --no-refit --drop-dips --gates-off"}},
    }
    json.dump(plan, open(os.path.join(HERE, "plan-e171.json"), "w"), indent=1)
    print(f"wrote tools/claims-v3/e171/plan-e171.json: smoke {len(smoke)} items ({why['hottest'][0]} the hottest, {why['hottest'][1]:.2f} W)")


if __name__ == "__main__":
    main()
