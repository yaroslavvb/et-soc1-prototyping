#!/usr/bin/env python3
"""E178 (Q146, the kit): write kit-e178.json, the machine form of E178.md section 7's run plan for the kit (the passes and plans, the
budget, the stops, the smoke, the sessions that must carry a C log, the scorer's call) and the A and B halves' sha256 of the 34 new tiles.
A port of tools/claims-v3/e171/make_plan_e171.py: plan-e178.json (the registered order) stays the registration's file; this file holds
what the kit reads beside it. It refuses if the registration's files differ from their hash lists, if a tile's whole sha256 differs from
kinds-e178.json's, if a tile's halves do not join to it, or if the smoke list differs from E178.md section 7's. Standard library only.

    python3 -B tools/claims-v3/e178/make_kit_e178.py            # writes kit-e178.json
    python3 -B tools/claims-v3/e178/make_kit_e178.py --check    # rebuilds it in memory and compares byte for byte: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "kit-e178.json")
# E178.md section 7, quoted: "the tie; fp32.zeros; fp32.randn; fp16.zeros; int8.zeros; int8.full; fp32.e178_uf (its C must read +0
# throughout); int8.e178_v85 and int8.e178_v127 (the int32 accumulator wraps within a launch); fp16.e178_v5"
SMOKE_TEXT = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp16.zeros", "int8.zeros", "int8.full", "fp32.e178_uf", "int8.e178_v85",
              "int8.e178_v127", "fp16.e178_v5")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build():
    sys.path.insert(0, HERE)
    # e178_common needs kit-e178.json only for load_items; check_frozen and the constants do not
    import e178_common as e  # noqa: E402
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    if tuple(e.SMOKE_ITEMS) != SMOKE_TEXT:
        raise SystemExit(f"refusing: e178_common.SMOKE_ITEMS {list(e.SMOKE_ITEMS)} is not E178.md section 7's {list(SMOKE_TEXT)}")
    tiles = {}
    for k in e.KINDS_LIST:
        if k["tile"] != "new":
            continue
        rel = f"tools/claims-v3/e178/tiles/{k['type']}/{k['name']}.bin"
        b = open(os.path.join(TOP, rel), "rb").read()
        if len(b) != 2048:
            raise SystemExit(f"refusing: {rel} is {len(b)} bytes, not 2048")
        if sha(b) != k["sha256"]:
            raise SystemExit(f"refusing: {rel}'s sha256 is not kinds-e178.json's")
        tiles[k["key"]] = {"file": rel, "sha256": sha(b), "sha256_a": sha(b[:1024]), "sha256_b": sha(b[1024:])}
    if len(tiles) != 34:
        raise SystemExit(f"refusing: {len(tiles)} new tiles, not 34")
    for p in (17810, 17811, 17812, 17813):
        err = e.check_order("aifoundry3", p)
        if err:
            raise SystemExit(f"refusing: pass {p}: {err}")
    kit = {
        "_what": "E178 (Q146): the kit's machine form of E178.md section 7 (make_kit_e178.py); the order itself is plan-e178.json",
        "experiment": "E178", "card": "aifoundry3",
        "registration": {"E178.md": "48171930 (20:51:01 PST, 5 Nov 2026)", "E178.md.dated-note-A1.md": "f421c67a (22:12:30 PST)",
                         "dated_note_M1": "E178.md.dated-note-M1.md, the mordast forecast's sha256 (section 8): committed before any E178 "
                                          "datum, or that forecast is not scored; the kit does not need it to run"},
        "frozen_inputs": dict(e.FROZEN, **e.LISTS),
        "tiles": tiles,
        "plan": {
            "passes": {"kinds": [17810, 17819], "planned": e.planned("aifoundry3"), "smoke": 17801, "stoptest": 17802},
            "plans": {"FULL": {"seq": [17810, 17811, 17812, 17813], "budget_s": 3600,
                               "note": "the fourth only if the budget rule admits it; a fifth is never planned"},
                      "TWO": {"seq": [17810, 17811], "budget_s": 1920}},
            "reserve_s": 60, "gap_s": 10, "first_estimate_s": {"kinds": 800},
            "runs_per_pass": 76, "launches_per_pass_with_burnins": 78,
            "stops": {"kinds": {"board_w": 65.0, "die_shire0_c": 70.0}, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "max_c": 70},
            "protocol": {"target_c": 58, "preheat_c": 59, "quiet_s": 2.0, "burnin": 2, "fma_s": 4,
                         "smoke": {"fma_s": 2, "preheat_c": 0, "quiet_s": 0.2, "burnin": 0}},
            "smoke": list(e.SMOKE_ITEMS),
            "min_kept_passes_scored": 2,
            "c_log_sessions": {"rule": "e178-smoke/p17801, and every e178/p178NN (17810-17819, never .attempt-*) whose runs.jsonl holds a "
                                       "launch record, whatever its block status; e178-stoptest/p17802 must hold no launch record and no "
                                       "C record (E171's rule, E178.md section 7)",
                               "checker": "tools/claims-v3/e178/ccsessions_e178.py (ccsessions_p8.py's check, unchanged, on E178's layout)"},
            "expected_card_minutes": {"FULL": [51, 54], "TWO": 27, "cap_FULL": 60, "cap_TWO": 32},
            "post": {"FULL": "using aifoundry3 for 1.5 h, until ~HH:MM PST", "TWO": "using aifoundry3 for 1 h, until ~HH:MM PST"},
            "time_gates": "E178_LATEST_START and E178_DEADLINE required, set at his go",
        },
        "scorer": {"code": "tools/claims-v3/e178/score_e178.py",
                   "call": "score --card aifoundry3 --reduction <out>/e178.json --runs-csv <out>/runs.csv --raw <raw copy> "
                           "--ccheck <out>/ccheck/ccheck-all.json [--arm name=<reduction json> ...] --json scored.json --md results.md",
                   "primary_reduction": "reduce_e178.py --leak 0.20563713796102187 --no-refit --drop-dips (E171's registered footing, "
                                        "E178.md section 5)",
                   "arms": {"session_own": "leakage auto, dips kept", "auto_dips_removed": "--drop-dips",
                            "kfrozen_dips_kept": "--leak K --no-refit", "leak0.1994": "--leak 0.1994 --no-refit --drop-dips",
                            "leak0.3803": "--leak 0.3803 --no-refit --drop-dips", "leak0": "--leak 0 --no-refit --drop-dips",
                            "gates_off": "--leak K --no-refit --drop-dips --gates-off"}},
        "card1_fallback": "aifoundry1 card 1 (E178.md section 7's fallback, A1-7's footing) is NOT kitted here: its box kit is E172's form "
                          "(tools/claims-v3/e172/) and needs its own port and readiness check; the scorer reads card 1's frozen P and F",
    }
    return json.dumps(kit, indent=1) + "\n"


def main():
    s = build()
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e178/kit-e178.json: {len(json.loads(s)['tiles'])} new tiles' halves, plans FULL and TWO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
