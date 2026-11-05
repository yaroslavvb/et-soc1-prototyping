#!/usr/bin/env python3
"""E172 (Q142(k6)): write plan-e172.json, the machine form of E172.md's session plan (the passes and plans, the budget, the stops, the smoke,
the sessions that must carry a C log, the scorer's call), from E172.md's text and the frozen pool-8 files. It refuses if the smoke list it
derives by E172.md's rule differs from e172_common.SMOKE_ITEMS, or if a frozen file differs. Standard library only.

    python3 -B tools/claims-v3/e172/make_plan_e172.py
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e172_common as e  # noqa: E402

CARD = "aifoundry1c1"


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
        raise SystemExit(f"refusing: the smoke by E172.md's rule {smoke} is not e172_common.SMOKE_ITEMS {list(e.SMOKE_ITEMS)}")
    plan = {
        "_what": "E172 (Q142(k6)): the machine form of E172.md's session plan; written by make_plan_e172.py after the registration (4441083f)",
        "experiment": "E172", "card": CARD, "registration": "tools/claims-v3/e172/E172.md", "registration_sha256": sha("tools/claims-v3/e172/E172.md"),
        "registration_commit": "4441083f",
        "frozen_inputs": {rel: h for rel, h in e.FROZEN.items()},
        "frozen_in": {"pool_and_predictions": "4576fb90", "converter_rule": "ebf68c52", "freeze_note": "dfe226f1", "pool8_registration": "3e97f583",
                      "A1": "8a8fa34c", "A2": "68a7c322", "predictor": "9d81d254", "predictor_a2": "97765c0a", "design": "153b720f"},
        "plan": {
            "passes": {"kinds": [17210, 17219], "smoke": 17201, "stoptest": 17202},
            "plans": {"FULL": {"seq": [17210, 17211, 17212, 17213, 17214], "budget_s": 3900,
                               "note": "four planned as the budget allows; a fifth does not fit (E164's form)"}},
            "reserve_s": 60, "gap_s": 10, "first_estimate_s": {"kinds": 800},
            "runs_per_pass": {"kinds": 84, "drop_p2": 75}, "launches_per_pass_with_burnins": {"kinds": 86, "drop_p2": 77},
            "drop_p2_switch": "E172_DROP_P2=1, set before the session and never after a pass has run", "drop_p2": list(e.P2_KINDS),
            "stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "max_c": 72},
            "smoke": list(e.SMOKE_ITEMS), "smoke_rule": why,
            "min_kept_passes_scored": 2, "min_tile_passes": 2,
            "c_log_sessions": {"rule": "e172-smoke/p17201, and every e172/p172NN (17210-17219, never .attempt-*) whose runs.jsonl holds a launch "
                                       "record, whatever its block status; e172-stoptest/p17202 must hold no launch record and no C record",
                               "checker": "tools/claims-v3/p8-600/ccsessions_p8.py --run E172"},
            "expected_card_minutes": {"FULL_four_passes": [51, 53], "cap": 65},
            "time_gates": "E172_DEADLINE required (the round's time gate less 10 minutes), set by box/launch_e172.sh; never two of our "
                          "sessions on aifoundry1: card 0's E174 starts only after E172 has ended",
        },
        "scorer": {"code": "tools/claims-v3/p8-600/score_p8_600.py", "commit": "a518aa11",
                   "call": "score --run E172 --reduction <data>/e172.json --raw <raw copy> --ccheck <out>/ccheck/ccheck-session.json [--arm ...]",
                   "primary_reduction": "reduce_e172.py --leak 0.3134106532552718 --no-refit (dips removed once, E164's reducer)",
                   "arms": {"session_own_slope": "--leak auto --no-refit", "dips_kept": "--keep-dips --leak K --no-refit",
                            "leak0.2955": "--leak 0.2955 --no-refit", "leak0.3320": "--leak 0.3320 --no-refit",
                            "relaxed": "--relax-anchors --leak K --no-refit"}},
    }
    json.dump(plan, open(os.path.join(HERE, "plan-e172.json"), "w"), indent=1)
    print(f"wrote tools/claims-v3/e172/plan-e172.json: smoke {len(smoke)} items ({why['hottest'][0]} the hottest, {why['hottest'][1]:.2f} W)")


if __name__ == "__main__":
    main()
