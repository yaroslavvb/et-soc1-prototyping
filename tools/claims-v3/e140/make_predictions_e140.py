#!/usr/bin/env python3
"""E140's freeze (Q137): writes predictions-e140.json - the harness hashes E140 refuses to run without, the plan, and (from
Q137(m)'s committed model files, every number read from them and each file hash-checked) M6's frozen predictions for blind
pool 4, power and die rise, with the rules and the reference errors behind them.

    python3 tools/claims-v3/e140/make_predictions_e140.py              # the registration (needs Q137(m)'s committed files)
    python3 tools/claims-v3/e140/make_predictions_e140.py --card-only  # harness and plan only: for a no-device setup test

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e140_common as e140  # noqa: E402
import m6_inputs  # noqa: E402  (reads Q137(m)'s committed files; the one place their layout is known)

REUSED = {   # E78's card code and reduction, byte for byte as E78 froze them (the same values E115's freeze checks)
    "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
    "tools/claims-v3/kinds/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
    "tools/claims-v3/kinds/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
    "tools/claims-v3/kinds/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
    "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
BINARIES = {   # the two binaries E115/E130 classified on this card (sparsity_host 26 Sep, ettelem 25 Sep)
    "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
}
CODE = ["e140_common.py", "run_e140.py", "block_e140.sh", "queue_e140.sh", "run_e140.sh", "reduce_e140.py", "score_e140.py",
        "collect_e140.sh", "make_predictions_e140.py", "m6_inputs.py", "selftest_e140.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card-only", action="store_true")
    a = ap.parse_args()
    for rel, want in REUSED.items():
        if sha(os.path.join(ROOT, rel)) != want:
            raise SystemExit(f"{rel} differs from E78's freeze")
    if e140.check_frozen():
        raise SystemExit(e140.check_frozen())
    pool = {f"{e140.POOL_REL}/{t['file']}": t["sha256"]["whole"] for t in e140._spec()["tiles"]}
    pool |= {rel: want for rel, want in e140.FROZEN.items()}
    plan = {
        "passes": [14010, 14011, 14012, 14013], "smoke": 14001, "smoke_items": list(e140.SMOKE_ITEMS), "runs_per_pass": 45,
        "burn_in_runs": 2, "min_kept_passes_scored": 2, "min_tile_passes": 2,
        "order": "Random('E140|aifoundry3|<pass>'): the 25 tiles dealt into three segments of 9, 8, 8, each with E78's six "
                 "anchors, reshuffled; the tie first and last (E115's order, unchanged)",
        "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz",
        "budget_s_from_session_start": 2040, "card_minutes_max": 35, "first_pass_estimate_s": 480, "gap_s": 15,
        "deadline": "2026-11-02 21:40 PST (no session starts after 21:00 PST; every run ends by 21:45 PST)",
        "die_stop_c": 70.0, "board_power_stop_w": 65.0, "bootstrap": {"draws": 100000, "seed": 14000},
        "data": "build/claims-v3/aifoundry3/kinds/p140<nn>/ on aifoundry3; results docs/reports/data/2026-11-02-e140-blind4/",
    }
    out = {
        "experiment": "E140", "date": "2026-11-02",
        "request": "Q137 (prediction is the goal): the blind test of Q137(m)'s frozen model M6 on blind pool 4; the kinds page's "
                   "section 11, item 6 ('a power model across kinds')",
        "card": "aifoundry3 card 0, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 C as read, never set",
        "plan": plan,
        "harness": {"reused_unchanged_sha256": REUSED, "binaries_sha256": BINARIES, "frozen_pool_sha256": pool,
                    "e140_files_sha256": {}},
    }
    if not a.card_only:
        m6 = m6_inputs.load(ROOT)          # every number from Q137(m)'s committed files, each hash recorded
        names = set(e140.E140_NAMES)
        miss = names - set(m6["tiles"])
        if miss:
            raise SystemExit(f"M6 has no prediction for {sorted(miss)}")
        out["frozen_inputs"] = m6["files"]
        out["model"] = m6["model"]
        out["tiles"] = {n: m6["tiles"][n] | {"type": n.split(".")[0], "priority": e140.PRIORITY[n], "case": e140.OPEN_CASE[n]}
                        for n in sorted(names)}
        out["reference_errors"] = m6["reference_errors"]
        out["anchors_predicted"] = m6.get("anchors_predicted")
        out["rules"] = m6_inputs.rules(out)
        out["expected"] = m6_inputs.expected(out)
    # the code's hashes last (this file's own hash included as it stands at the freeze)
    out["harness"]["e140_files_sha256"] = {f"tools/claims-v3/e140/{f}": sha(os.path.join(HERE, f)) for f in CODE
                                           if os.path.exists(os.path.join(HERE, f))}
    json.dump(out, open(os.path.join(HERE, "predictions-e140.json"), "w"), indent=1)
    open(os.path.join(HERE, "predictions-e140.json"), "a").write("\n")
    print("wrote predictions-e140.json", "(card side only)" if a.card_only else f"({len(out.get('tiles', {}))} tiles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
