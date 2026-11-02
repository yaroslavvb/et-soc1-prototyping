#!/usr/bin/env python3
"""E137 (Q137): write predictions-e137.json, the freeze. Every M4 number is copied from E128's frozen predictions-e128.json (never refitted);
E128's own two passes, per pass, are copied from its committed scored.json/e128.json as the reference E137 replicates; the hashes are of the files
as they are at this commit. Standard library only.

    python3 tools/claims-v3/e137/make_predictions_e137.py          # writes tools/claims-v3/e137/predictions-e137.json

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P128 = os.path.join(ROOT, "tools/claims-v3/e128/predictions-e128.json")
D128 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e128-fp16-signs")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


TILES = ["fp16.b_B_w", "fp16.b_B_wm", "fp16.b_B_z", "fp16.b_B_zm", "fp16.c_abs", "fp16.ones", "fp16.signs", "fp16.z_s"]
QUANT = ["fp16.step", "fp16.held_z", "fp16.rest_vs_z", "fp16.Bz_het", "fp16.Bz_walk", "fp16.Bz_rest", "fp16.Bm_het", "fp16.Bm_walk",
         "fp16.Bm_rest", "fp16.held_alt", "fp16.walk_alt", "fp16.share_z", "fp16.share_het_z", "fp16.share_het_m", "fp16.share_walk_m",
         "fp16.rest_ratio_m", "fp16.design_m"]
CARD_FILES = ["tools/claims-v3/e137/e137_common.py", "tools/claims-v3/e137/run_e137.py", "tools/claims-v3/e137/block_e137.sh",
              "tools/claims-v3/e137/queue_e137.sh", "tools/claims-v3/e137/session_e137.sh", "tools/claims-v3/e137/preflight_e137.sh",
              "tools/claims-v3/e137/smoke_gate_e137.py"]
REUSED = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/e128/e128.json",
          "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
          "workloads/sparsity/host/main.cpp"]


def main():
    p = json.load(open(P128))
    e128 = json.load(open(os.path.join(D128, "e128.json")))
    sc = json.load(open(os.path.join(D128, "scored.json")))
    tiles = {t: p["tiles"][t] for t in TILES}
    quant = {q: p["quantities"][q] for q in QUANT}
    # E128's per-pass D (primary) for E137's tiles, copied: the reference E137 replicates and the pooled arm's E128 half
    ref = {ps: {t: e128["per_pass"][ps][t]["D"] for t in TILES if t in e128["per_pass"][ps]} for ps in sorted(e128["per_pass"])}
    out = {
        "experiment": "E137",
        "title": "fp16's sign rest on E128's matched design, at four or more kept passes (aifoundry1 card 1, 600 MHz)",
        "request": "Q137 (the owner's words, Mon 2 Nov 2026 ~15:20 PST: 'The overall goal is to be able to predict the power requirement and heat "
                   "generation of various kinds of numeric computations as accurately as possible'); the kinds page's section 11, item 5",
        "date": "2026-11-02",
        "registration": "tools/claims-v3/e137/E137.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "harness": {
            "reused_unchanged_sha256": {r: sha(r) for r in REUSED[:5]},
            "card_code_unchanged_sha256": {r: sha(r) for r in REUSED},
            "e137_card_files_sha256": {r: sha(r) for r in CARD_FILES},
            "box_binaries_sha256": dict((k, v) for k, v in p["harness"]["binaries_sha256"].items()
                                        if k in ("build/sparsity/host/sparsity_host", "build/ettelem/ettelem")),
            "e128_json_sha256": p["harness"]["e128_json_sha256"],
            "predictions_e128_sha256": sha("tools/claims-v3/e128/predictions-e128.json"),
        },
        "plan": {"passes": list(range(13710, 13717)), "smoke": 13701, "readback": None,
                 "runs_per_pass": 28,
                 "items_per_pass": "the tie twice, E78's six anchors three times, E128's seven fp16 sign tiles and E78's fp16.ones once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's), E78's gates (S1 of the set-aside rule)",
                 "min_kept_passes_scored": 4},
        "card_budget": {"card_minutes_at_most": 60, "counted": "the session's first device access (its start config read) to its last (its end config read)",
                        "queue_budget_s": 3420, "reserve_s": 60, "first_pass_estimate_s": 700, "queue_deadline": "2026-11-02 21:30 PST",
                        "no_session_start_after": "2026-11-02 21:00 PST", "every_run_ends_by": "2026-11-02 21:45 PST"},
        "stops": {"board_w": 68.0, "die_hottest_shire_c": 72.0, "run_e78_max_c": 72.0, "run_e78_pmic_stop_c": 82.0,
                  "what": "run_e137.py (E131's guard, copied): a telemetry line with board_w >= 68 W or any minion-shire reading >= 72 C writes the "
                          "pass's STOP and ends it (run_e78's EXIT_HOT); run_e78.py's own --max-c 72 on the first shire reading (and its PMIC field "
                          ">= 82 C, a die reading on this runner); either stop fails the block and ends the queue",
                  "margin_basis": "E128's two passes of the same tiles on this card: board at most 59.79 W, the shires' mean at most 61 C, no shire "
                                  "above 65 C (docs/reports/data/2026-11-02-e128-fp16-signs/desk/telemetry-max-e128.txt); E137 drops E128's fp32 "
                                  "tiles but keeps fp32.randn, the hottest kind, as an anchor; the PMIC's alarm is 75 W"},
        "set_aside_rule": {
            "min_kept_passes": 4,
            "written": "Mon 2 Nov 2026, in this registration, before the claim and before any E137 data",
            "relaxed_reduction_gates": {"zero_mid_departure_w": 99.0, "zero_range_w": 99.0, "random_range_w": 99.0, "tie_drift_w": 99.0},
            "steps": [
                "S1, the primary: E78's pass gates unchanged (each type's zeros line departs <= 0.25 W from its straight line and spans <= 0.60 W; each "
                "random anchor spans <= 1.0 W; the pi tie drifts <= 0.60 W; at most 2 failed runs; card 1's config read). It carries every verdict if "
                "it keeps >= 4 passes",
                "S2, only if S1 keeps < 4: a pass set aside ONLY by the pi tie's drift is restored whole (pi enters no rule but the reported session tie)",
                "S3, only if S1 and S2 keep < 4: a pass set aside only by the fp32 or int8 anchor gates (their zeros line's departure or span, their "
                "random anchor's span; the tie as in S2) is restored for fp16's items: every rule reads fp16 D, which is over fp16's own zeros line. "
                "A pass set aside by fp16's own anchors (fp16.zeros' departure or span, fp16.randn's span) is never restored",
                "Never restored in any step: a pass with more than 2 failed runs, a pass whose config read is not card 1's 65/65, a pass whose block "
                "did not end ok, an .attempt-* directory",
                "Per rule: a quantity is formed only in the kept passes in which every tile it reads has a kept run (a run skipped by E78's launch "
                "rule, as E128's 12811 fp16.signs, leaves that pass out of that quantity only); a rule is scored only if its quantity has >= 4 "
                "such passes, else NOT SCORED with its n",
                "Where restored values come from: reduce_e137.py --relax-anchors at the same frozen slope (with a fixed slope each pass's "
                "reduction does not depend on the others', so its per-pass values equal the primary's for every pass both keep)",
                "No pass is added after any reduction is read, and no pass is chosen after the fact. Every reading is reported and every verdict "
                "names the reading that carries it"]},
        "model": p["model"],
        "matched_alternations": {"fp16": p["matched_alternations"]["fp16"]},
        "tiles": tiles,
        "quantities": quant,
        "e128_reference": {
            "source": "docs/reports/data/2026-11-02-e128-fp16-signs/e128.json per_pass.<pass>.<tile>.D and scored.json primary.quantities",
            "per_pass_D": ref,
            "quantities": {q: sc["primary"]["quantities"].get(q) for q in QUANT},
        },
        "session_tie": p["session_tie"],
        "rules": {
            "E137-R1": {"kind": "power", "form": "bands", "legs": ["fp16.share_het_m"], "lo": 0.35, "hi": 0.65,
                        "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "E128-R8 again: fp16, matched: (b_B_zm - z_s) / (b_B_wm - z_s), the share of B's rest the accumulators differing carry"},
            "E137-R2": {"kind": "power", "form": "band_then_sign", "legs": ["fp16.share_walk_m"], "band": 0.1,
                        "names": {"inside": "ALMOST NONE", "above": "SOME", "below": "NEGATIVE"},
                        "what": "E128-R9 again: fp16, matched: (b_B_wm - b_B_zm) / (b_B_wm - z_s), the share that goes with the sums changing"},
            "E137-R3": {"kind": "power", "form": "bands", "legs": ["fp16.share_het_z"], "lo": 0.35, "hi": 0.65,
                        "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "E128-R7 again: fp16, E108's design ported: (b_B_z - z_s) / (b_B_w - z_s)"},
            "E137-R4": {"kind": "power", "form": "sign_then_band", "legs": ["fp16.design_m"], "band": 0.1,
                        "names": {"above": "MATCHED HIGHER", "below": "MATCHED LOWER", "inside": "ALIKE"},
                        "what": "fp16: the matched share less E108's design's share, per pass"},
            "E137-R5": {"kind": "power", "form": "step_band", "what": "the fp16 step on this card: signs - ones against E108's",
                        "e108_w": p["rules"]["E128-R2"]["e108_w"]["fp16"], "band_w": 1.0},
            "E137-R6": {"kind": "power", "form": "rms", "what": "the bench's model M4 on E137's eight items: rms(D - M4)", "pass_w": 0.6, "fail_w": 1.0},
            "E137-R7": {"kind": "power", "form": "m4_contrasts",
                        "legs": ["fp16.step", "fp16.Bz_het", "fp16.Bz_walk", "fp16.Bz_rest", "fp16.Bm_het", "fp16.Bm_walk", "fp16.Bm_rest"],
                        "what": "the sign term out of sample: each of M4's seven frozen fp16 sign contrasts against the measured one; PASS if every "
                                "measured mean lies inside M4's frozen 95% half-width (quantities.<q>.half95) and rms(measured - M4) <= 0.30 W; FAIL "
                                "if two or more lie outside or the rms exceeds 0.60 W; else INCONCLUSIVE",
                        "inside_all_rms_w": 0.30, "fail_rms_w": 0.60, "fail_outside_n": 2},
            "E137-R8": {"kind": "power", "form": "e128_replicate", "legs": ["fp16.share_het_m", "fp16.share_walk_m", "fp16.share_het_z"],
                        "what": "E137 against E128's two passes on the same card and tiles (E122's cross-session form): d = Q137 - Q128, "
                                "h = sqrt(h137^2 + h128^2); PASS if |d| + h <= 0.15, FAIL if |d| - h > 0.15, else INCONCLUSIVE, per share",
                        "w": 0.15},
            "E137-S1": {"kind": "power", "form": "session_tie", "what": "the session tie against E82, dips removed (E128-S1's bands)"},
        },
        "expect": {"E137-R1": "MOST", "E137-R2": "ALMOST NONE or INCONCLUSIVE", "E137-R3": "MOST", "E137-R4": "ALIKE or INCONCLUSIVE",
                   "E137-R5": "PASS", "E137-R6": "PASS", "E137-R7": "PASS or INCONCLUSIVE", "E137-R8": "PASS or INCONCLUSIVE", "E137-S1": "PASS"},
        "not_scored_if": "a rule's quantity has fewer than 4 kept passes after the set-aside rule: that rule NOT SCORED, with its n",
    }
    json.dump(out, open(os.path.join(HERE, "predictions-e137.json"), "w"), indent=1, sort_keys=False)
    print("wrote predictions-e137.json:", len(tiles), "tiles,", len(quant), "quantities,", len(out["rules"]), "rules")


if __name__ == "__main__":
    main()
