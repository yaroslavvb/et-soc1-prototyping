#!/usr/bin/env python3
"""Write tools/claims-v3/kinds/predictions-e82.json, E82's machine-readable freeze (Q130). E78's rule thresholds,
Q130(c) scoring and Q130(b) scoring are COPIED from predictions-e78.json, never retyped, so E82 scores exactly
E78's rules; E82's own parts (the card, the passes, the leakage arm, the replication targets on card 1, the
cross-card rules) are set here, each with its source.

    python3 tools/claims-v3/kinds/make_predictions_e82.py        # standard library only
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E78 = json.load(open(os.path.join(HERE, "predictions-e78.json")))
PC = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-q130-kinds-model/predictions.json")))
TYPES = ("fp32", "fp16", "int8")
ZERO = {t: f"{t}.zeros" for t in TYPES}
BAND = [0.88, 0.99]
K_CARD1 = 0.545       # e82_desk_checks.txt [1]


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


pred = {k.replace("/", "."): v["switching_w_600mhz_a3"] for k, v in PC["predictions"].items()}
eligible = sorted(n for n, v in pred.items() if v >= 5.0)
x1_sets = {t: sorted(n for n in pred if n.startswith(t + ".") and n != ZERO[t]) for t in TYPES}
reused = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/block_e78.sh", "tools/claims-v3/kinds/queue_e78.sh",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/score_e78.py",
          "tools/claims-v3/kinds/kinds.json"]

plan = copy.deepcopy(E78["plan"])
plan.update({
    "order": "e78_common.pass_order unchanged, with card 'aifoundry1-c1': random.Random('E78|aifoundry1-c1|<pass>') "
             "shuffles the 45 non-anchor kinds, deals them round-robin into three segments, adds the six anchors to "
             "each segment and shuffles each segment again. The 'E78' in the seed string is the unchanged code's; the "
             "card name makes the order card 1's own. No pass is 7810, so fp32.a_randn_b_zeros is never moved to the "
             "front (Q130(c)'s R9 asked that of E78's first pass only)",
    "passes_planned": [8210, 8211, 8212, 8213, 8214, 8215], "min_passes": 4, "smoke_pass": 8201,
    "first_pass_first_ten": "e82_desk_checks.txt [8]",
})
plan["launch"] = dict(plan["launch"], note="E78's launch reading unchanged (heat to 59 C, launch at 58 C, 2.0 s quiet); "
                      "card 1 idles at 52 C (the lab monitor's history, 13:21 PDT, read without opening the card), so "
                      "every run is heated to the band as on aifoundry3 (idle 55-57 C)")

analysis = copy.deepcopy(E78["analysis"])
analysis["leak"] = {
    "primary": "auto (the median within-run slope of runs heating >= 1 C, as E70/E78/E79), unchanged",
    "arms": [K_CARD1, 0.3803, 0.0],
    "arm_source": f"{K_CARD1}: card 1's own idle slope over the launch band 58-62 C, from E44's idle bins (28 Sep), "
                  "by the estimator that gives 0.3800 on aifoundry3's bins against E71's measured 0.3803 "
                  "(e82_desk_checks.txt [1]); 0.3803: E78's own arm (E71, aifoundry3), for a like-for-like reading "
                  "with E78; 0: no correction",
    "verdicts": "every rule is scored at the primary; the arms' verdicts are reported beside; a verdict that moves "
                "between arms is reported as slope-sensitive",
}
analysis["rail_model"] = dict(analysis["rail_model"], e82_note="E78's frozen rail model is kept (tau 0.95 s, d 0.2 s, "
                              "c 0.81, arms 0.80 / 1.10 s). Card 1's minion rail lags 1.08 s (E58, 14-card-behaviour.md), "
                              "next to the 1.10 arm; the rail is reported, never scored")
analysis["pass_gates"] = dict(analysis["pass_gates"], config="ettelem config reads a TDP other than 65 or a threshold "
                              "other than 65 at either end (card 1's registered values): reported separately, not pooled "
                              "(E78's gate with card 1's values; reduce_e82.py)")
analysis["reduction_code"] = {
    "file": "tools/claims-v3/kinds/reduce_e78.py", "sha256": sha("tools/claims-v3/kinds/reduce_e78.py"),
    "wrapper": "tools/claims-v3/kinds/reduce_e82.py: runs reduce_e78.main() unchanged after one substitution in the "
               "config gate (card 1's 65 / 65 accepted where aifoundry3's 0 / 65 is); it refuses to run if "
               "reduce_e78.py, e78_common.py or kinds.json differs from the sha256 below",
}

rules = copy.deepcopy(E78["rules"])
rules["E78-R4"]["defense"] = ("E82: card 1's own September anchors (E38, built-in values, 4 runs, launches near 80 C); "
                              "E67's and E79's aifoundry3 targets do not apply to another card. The tie test is E78's")
rules["E78-R4"]["e82_targets_source"] = "replication_targets below, from e82_desk_checks.txt [3]"
for k in rules:
    rules[k]["e82"] = "E78's rule, its threshold copied from predictions-e78.json, scored on card 1 by score_e78.py's code"

q130c = copy.deepcopy(E78["q130c_scoring"])
q130c["C-R9"]["e82_note"] = ("no E82 pass runs fp32.a_randn_b_zeros first; the arm is selected on the mean, and "
                             "score_e78's pass_7810_first field reads null for E82")

reg = {
    "experiment": "E82",
    "title": "the kinds-of-numbers energy matrix (E78's design) replicated on aifoundry1 card 1",
    "request": "Q130 (AI Foundry, the Horace project), second workflow q130-more-cards",
    "date": "2026-10-31",
    "registration": "tools/claims-v3/kinds/E82.md (this file's prose). Frozen with the commit that adds them, before the "
                    "Discord claim of card 1, the first launch, and before E82's lane opened any E78 data. Any change "
                    "after it is a dated amendment in E82.md, written before the data it touches",
    "replicates": {"experiment": "E78", "registration": "cfd94285 (tools/claims-v3/kinds/E78.md, predictions-e78.json)",
                   "amendment": "A1 09c6e29b (plumbing only)",
                   "predictions_e78_sha256": sha("tools/claims-v3/kinds/predictions-e78.json"),
                   "e78_md_sha256_at_freeze": sha("tools/claims-v3/kinds/E78.md")},
    "card": {
        "host": "aifoundry1", "device": 1, "card_id": "aifoundry1-c1", "select": "V3_DEVICE=1 (lib.sh exports ET_DEVICES=1)",
        "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600, "minion_mv_expected": 499,
        "firmware_as_last_read": "release 1.2.0 (BL2 0.18.0 / PMIC 1.3.0 / minion 0.22.0), docs/findings/14-card-behaviour.md",
        "clock_policy": "600 MHz in every sample since 25 Sep; its governor never raises the clock",
        "tdp_w": 65, "temp_threshold_c": 65,
        "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65},
                        "source": "every card-1 config_start.json of the 25-26 Sep campaign (e82_desk_checks.txt [4])",
                        "rule": "a pass whose start or end read differs is reported separately and not pooled, as E78's"},
        "knobs_written": "none: no governor move, no TDP/threshold/clock set, no reset, no PMIC or flash path (card 1's "
                         "BL2 0.18.0 writes NoC voltage sets to flash; nothing in E82 sets anything); the only management "
                         "reads are `ettelem config` at both ends of every pass, inside the card lock, under timeout 10",
    },
    "inputs_frozen": copy.deepcopy(E78["inputs_frozen"]),
    "harness": {
        "dir": "tools/claims-v3/kinds/",
        "files_new": ["E82.md", "predictions-e82.json", "make_predictions_e82.py", "reduce_e82.py", "score_e82.py",
                      "collect_e82.sh", "run_e82.sh", "selftest_e82.py", "selftest_e82.txt", "e82_desk_checks.py",
                      "e82_desk_checks.txt"],
        "reused_unchanged_sha256": {r: sha(r) for r in reused},
        "lib_sh_sha256": sha("tools/claims-v3/lib.sh"),
        "tree_on_box": "aifoundry1 ~/nekko (an rsynced copy, no git); tools/claims-v3/kinds/ copied in from this commit",
        "binary": "build/sparsity/host/sparsity_host in ~/nekko (aifoundry1's own build); its workloads/sparsity sources "
                  "are compared with aifoundry3's before the claim (E82.md, 'How to run it')",
        "data_dir": "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/",
        "raw_data_on_box": "build/claims-v3/aifoundry1-c1/kinds/p82<nn>/",
    },
    "plan": plan,
    "card_budget": dict(copy.deepcopy(E78["card_budget"]), deadline_local="19:15 PDT (card runs must end by ~19:30 PDT)",
                        e82_note="the budget rule of queue_e78.sh unchanged (85 card-minutes for full passes, 88 for a "
                                 "tier-1 fallback, 19:15 PDT); card 1 starts 6 C below the launch band, so a pass may "
                                 "take longer than aifoundry3's ~10.7 min and the rule may stop at 4 or 5 passes"),
    "analysis": analysis,
    "rules": rules,
    "q130c_scoring": q130c,
    "q130b_scoring": copy.deepcopy(E78["q130b_scoring"]),
    "replication_targets": {
        "fp32.ones": {"target_w": 8.996, "tol_w": 1.0,
                      "source": "E38 abla.json ABL-T8 per_card.aifoundry1-c1.vs_aifoundry2_values.subtests[0]: fp32 ones - "
                                "zeros 8.996 W (se 0.151), built-in values (= kinds.json's fp32.ones bit for bit), launches "
                                "near 80 C; tolerance: September's launch-temperature offset on card 1 (0.05-0.73 W, note C2) "
                                "plus E78's 0.60 W"},
        "fp32.randn": {"target_w": 26.662, "tol_w": 1.5,
                       "source": "E38 abla.json ABL-T8 ...subtests[1]: fp32 randn - zeros 26.662 W (se 0.159), the host's "
                                 "kernel-generated randn; E82 runs kinds.json's one fixed tile (1.8% under its rule's mean "
                                 "operand bits, about -0.5 W) and C2's offsets apply: hence 1.5 W"},
    },
    "reported_beside_r4": {
        "fp16.randn pJ/MAC over idle": {"e38_card1": 2.700, "interval": [2.486, 2.914]},
        "int8.full pJ/MAC over idle": {"e38_card1": 0.309, "interval": [0.261, 0.357]},
        "source": "E38 abla.json ABL-T5 per_card.aifoundry1-c1.reported.vs_aifoundry2_values (built-in randn, a different "
                  "protocol: reported against E82's pj_mac_S, never scored)",
    },
    "secondary": {"r2_scaled": {"factor": round(1 / 0.935, 6),
                                "why": "the midpoint of the registered card band (aifoundry3 = 0.935 x card 1): E78-R2 again "
                                       "with Q130(c)'s aifoundry3 predictions divided by 0.935, reported only"}},
    "cross_card": {
        "against": "E78's committed reduction of aifoundry3 (docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json "
                   "and its leakage arms), read only after this freeze is pushed",
        "quantity": "D, each kind's switching power over its own type's zeros (mean over kept passes), on each card",
        "band": BAND,
        "band_source": "e82_desk_checks.txt [2]: aifoundry3 / card 1 in September read 0.887 (registered values), 0.955 "
                       "and 0.965 (at the launch temperatures, note C2), per pattern 0.897-0.915; [0.88, 0.99] covers them",
        "min_passes_each": 4,
        "X1": {"name": "rank", "what": "Spearman rho of D(card 1) against D(aifoundry3) within each type, over every kind but "
                                       "the type's zeros (D of zeros is 0 by construction)",
               "sets": x1_sets, "threshold": 0.9, "min_resolved_frac": 0.75,
               "pass_if": "rho >= 0.90 in each type; X1 passes only if all three do",
               "power": "e82_desk_checks.txt [7]: 1.00 in every case simulated, including doubled noise and a 5% per-kind "
                        "deviation from one scale: a necessary check, not a sharp one"},
        "eligible_kinds": eligible,
        "eligible_rule": "frozen Q130(c) switching_w_600mhz_a3 >= 5.0 W (32 kinds: 14 fp32, 12 fp16, 6 int8), so that "
                         "each ratio is a ratio of watts, not of noise",
        "X2": {"name": "one scale, kind by kind",
               "X2a": "the ratio of means D(aifoundry3)/D(card 1) lies inside the band, for >= 80% of the resolved eligible "
                      "kinds (the orchestrator's form)",
               "X2b": "the ratio's 95% interval (delta method from the two cards' t intervals) overlaps the band, for >= 80% "
                      "of the resolved eligible kinds",
               "min_frac": 0.8, "min_resolved_frac": 0.75,
               "non_positive": "a kind with D <= 0 on either card counts as outside the band in both",
               "power": "e82_desk_checks.txt [7]: X2a passes with probability 0.97-1.00 only if the common scale sits "
                        "mid-band (0.935-0.96) and the noise is E67's; 0.01-0.05 at the band's edges (0.887, 0.985), 0.16 "
                        "with doubled noise, 0.75 with a 2% per-kind deviation. X2b passes whenever the scale is inside "
                        "[0.887, 1.00] and fails at 1.05 (and at 0.85 with 6 passes): it is the noise-aware reading. Both "
                        "are reported; neither stands in for the other"},
        "X3": {"name": "the card scale", "what": "the median over the resolved eligible kinds of D(aifoundry3)/D(card 1)",
               "pass_if": "inside the band [0.88, 0.99]",
               "power": "e82_desk_checks.txt [7]: 0.86-1.00 for a true scale in [0.887, 0.985]; 0.00-0.01 at 0.85, 1.00 and 1.05"},
        "arms": {"own idle slopes (card 1 0.545, aifoundry3 0.3803)": ["leak0.545", "e78-leak0.3803.json"],
                 "same slope 0.3803 on both": ["leak0.3803", "e78-leak0.3803.json"],
                 "no correction on both": ["leak0", "e78-leak0.json"]},
        "reported": ["each type's zero-data level S(zeros) on both cards", "the idle level", "the minion voltage",
                     "the auto leakage slopes", "per-type X2/X3 statistics", "E78's rule verdicts on both cards"],
    },
    "joins": copy.deepcopy(E78["joins"]),
}
json.dump(reg, open(os.path.join(HERE, "predictions-e82.json"), "w"), indent=1)
print(f"wrote predictions-e82.json: {len(eligible)} eligible kinds, X1 sets "
      f"{ {t: len(v) for t, v in x1_sets.items()} }, reused files {len(reused)}")
