#!/usr/bin/env python3
"""E163 (Q141): write predictions-e163.json, the machine-readable freeze of E163.md (the registration), and planned-intervals.txt.
A port of tools/claims-v3/e153/make_predictions_e153.py with pool 7, M9 primary (M8, M7 and M6 beside), rank 1's rules, rank 14's
re-runs and rank 4's reference half. Standard library only.

E163 adds no prediction. Every model number is copied from Q140(x)'s committed aifoundry3 predictions
(tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry3.json, 75802201, made by Q140(m)'s predict_blind7.py at 1f244140 with
nothing refitted); every power reference error from M9's nested leave-one-kind-out errors of the aifoundry3 rows (ref_errors_e163.py ->
ref-errors-m9.json, which reproduces m9.json's pools exactly, and row by row fit_m9.run_family); the heat reference from M7's heat
pools, which M9 carries (m9.json > heat); the re-run tiles and their earlier values from rerun_ref_e163.py (rerun-ref.json). Each
source's sha256 is checked against the value written here and recorded. The harness hashes (every file the box runs) are not here:
they are harness-e163.json, written by make_harness_e163.py after the kit (E163.md, "The order of the freeze").

    python3 -B tools/claims-v3/e163/make_predictions_e163.py      # writes predictions-e163.json and planned-intervals.txt beside it
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e163 as S  # noqa: E402

P7 = "tools/claims-v3/kinds/blind7"
QM = "docs/reports/data/2026-11-04-q140m-m9"
QU = "docs/reports/data/2026-11-03-q139u-footing"
SOURCES = {   # the frozen inputs and the sha256 each must have (Q140(x)'s 75802201 / 3c9bb2ba, Q140(m)'s 1f244140, Q139(u))
    f"{P7}/predictions-blind7-aifoundry3.json": "303dc5b94b35dbd772a9d405934406b4f3fa23551efeba63d85e064839b3d750",
    f"{P7}/blind7.json": "24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552",
    f"{P7}/MANIFEST": "92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a",
    f"{P7}/SHA256SUMS": "df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239",
    f"{P7}/counts-blind7.json": "0749922588daf81f684d5e7804d337cf38d6b3c8519a99903b535118492caa57",
    f"{P7}/rank4_rule.json": "4b9ccaf006fff9bc92041bf470fe8520e7443f790c02dd1ba3e1ee62293f2507",
    f"{P7}/score_rank4.py": "2aba0a82898c96521f35fa402a376cb303588791775da2c7d4b8004bb8998897",
    f"{P7}/RANK4-RULE.md": "852b7db73b933e93d7316bc8f80ddd1e894efce93b4e35fa7becc8c5b9c4747b",
    f"{P7}/README-predictions.md": "1e388c5990b6e1b9a480c7b8cac385d40ea877db7bca550cbbe29a91a5b5013a",
    f"{QM}/m9.json": "322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835",
    f"{QM}/predict_blind7.py": "32b5cdac865945e88e4616a30de78ce93eaf97381fe38f3d62aab5cbf158c2d1",
    f"{QM}/nested-m9.json": "f6057e3b9f055d538182485756fbe7cde27f96f8af7617085314d68ebada44a0",
    f"{QM}/rows-m9.json": "96ec405065257a543f7385711ad1841eb37316cc0148c362f35727534d05d41e",
    f"{QM}/fit_m9.py": "0b3f1074c4a84865dd2f6e6e4e018a56ce28e016b22b6fbfd66b74a1520752f5",
    f"{QM}/M9-REGISTRATION.md": "5d8546cbfe1df58ce39d526e8067c1e595177d144e338a585a675211c7058605",
    f"{QM}/recount-rule/recount-rule.txt": "d99c48b1bc3b838f97abdb2b20b548b99a95ceef630b37a79dd8528c8dc15e98",
    f"{QU}/footing.json": "f589efaad1fc9b19390658f16a5ffd4ca71e23cde59fbcf2f5cc88c267a73a97",
}
REF_ERRORS = "tools/claims-v3/e163/ref-errors-m9.json"
RERUN_REF = "tools/claims-v3/e163/rerun-ref.json"
FORMATS = ("fp32", "fp16", "int8")
MODELS = ("M9", "M8", "M7", "M6")
E78_ANCHORS = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full")
SMOKE = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.uniform_pm1", "fp32.anchor7_zeros", "fp16.real_qwen_l3_softmax_v_h1",
         "fp16.zeros", "int8.bheld_ff", "int8.zeros", "fp32.gd0", "fp16.pair_cancel_asign", "int8.b1_1")
P2_DROP_ORDER = ("fp32.real_s360_l1_qk", "fp32.b_onebit_b20_third_a1p5", "int8.real_smol_l3_w8a8_down", "int8.bheld_55_asmall")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    for rel, want in SOURCES.items():
        have = sha(rel)
        if have != want:
            raise SystemExit(f"{rel}: sha256 {have} != the committed {want}")
    J = lambda rel: json.load(open(os.path.join(ROOT, rel)))  # noqa: E731
    pred = J(f"{P7}/predictions-blind7-aifoundry3.json")
    m9 = J(f"{QM}/m9.json")
    man = J(f"{P7}/blind7.json")
    spec7 = {t["name"]: t for t in man["tiles"]}
    sub = man["subsets"]
    refj = J(REF_ERRORS)
    for f in ("rows-m9.json", "nested-m9.json", "m9.json", "fit_m9.py"):
        if refj["sha256"].get(f"{QM}/{f}") != SOURCES[f"{QM}/{f}"]:
            raise SystemExit(f"ref-errors-m9.json was not made from the committed {f}")
    rr = J(RERUN_REF)
    tiles = {}
    for name, t in sorted(pred["tiles"].items()):
        s = spec7[name]
        row = {"type": t["type"], "priority": int(t["priority"]), "pool_anchor": bool(s.get("anchor")), "case": t["case"],
               "real": bool(s.get("real")), "aim": s.get("aim"), "sha256": t["sha256"], "sha256_matches_manifest": t["sha256_matches_manifest"],
               "file": f"{P7}/{s['file']}", "sha256_a": s["sha256"]["a"], "sha256_b": s["sha256"]["b"]}
        assert t["sha256"] == s["sha256"]["whole"]
        for m in MODELS:
            x = t[m]
            row[m] = {"D_w": x["D_w"], "D_95": x["D_95"], "S_w": x["S_w"], "dT_win_c": x["dT_win_c"], "dT_win_95": x["dT_win_95"],
                      "D600_a3_footing_w": x["D600_a3_footing_w"]}
            if m == "M9":
                row[m]["form"] = x.get("form")
        tiles[name] = row
    assert len(tiles) == 61 and all(tiles[n]["sha256_matches_manifest"] for n in tiles)
    new = sorted(n for n, r in tiles.items() if not r["pool_anchor"])
    p1 = {f: sorted(n for n in new if tiles[n]["type"] == f and tiles[n]["priority"] == 1) for f in FORMATS}
    cov = sorted(n for n in new if tiles[n]["priority"] == 1)
    p2 = sorted(n for n in new if tiles[n]["priority"] == 2)
    anchors = sorted(n for n, r in tiles.items() if r["pool_anchor"])
    real_all = sorted(n for n in new if tiles[n]["real"])
    real_p1 = sorted(sub["real"])
    assert len(new) == 52 and len(cov) == 48 and len(p2) == 4 and len(anchors) == 9 and len(real_all) == 12 and len(real_p1) == 10
    assert sorted(p2) == sorted(sub["priority2_tests"]) == sorted(P2_DROP_ORDER)
    assert all(tiles[n]["priority"] == 1 and tiles[n]["real"] for n in real_p1)
    classes = {c: sorted(sub["aimed"][c]) for c in ("S", "E", "L", "H")}
    classes["U"] = sorted(sub["unaimed_synthetic"])
    classes["R"] = real_p1
    assert sorted(x for v in classes.values() for x in v) == cov
    assert {c: len(v) for c, v in classes.items()} == {"S": 7, "E": 6, "L": 7, "H": 6, "U": 12, "R": 10}
    # power reference: M9's nested errors of every aifoundry3 row of each format (both cards: an arm)
    ref, ref_both = {}, {}
    for fam in ("float", "int8"):
        for r in refj["families"][fam]["row_errors"]:
            if r["err_w"] != r["err_w"]:      # nan
                continue
            ref_both.setdefault(r["type"], []).append(r["err_w"])
            if r["card"] == "a3":
                ref.setdefault(r["type"], []).append(r["err_w"])
    assert {f: len(ref[f]) for f in FORMATS} == {"fp32": 241, "fp16": 124, "int8": 90}
    pools = m9["heat"]["interval_pool_by_format_card_c"]
    heat_rms = {f: pools[f"{f}|aifoundry3"]["rms_c"] for f in FORMATS}
    rng = random.Random("E163|heat-reference")
    heat_ref = {f: [rng.gauss(0.0, heat_rms[f]) for _ in range(2000)] for f in FORMATS}
    reruns = {}
    for src in ("pool5", "e152"):
        for t, x in rr[src]["tiles"].items():
            reruns[t] = {"source": x["source"], "type": x["type"], "file": x["file"], "sha256": x["sha256"], "sha256_a": x["sha256_a"],
                         "sha256_b": x["sha256_b"], "footing": x["footing"], "session": x["session"]}
    assert len(reruns) == 16
    mins = {"fp32": 9, "fp16": 5, "int8": 11, "floats": 13, "real": 7}
    bs = {"draws": 20000, "seed": 16300}
    chain = rr["e151"]["chain_sha256"]
    e151_ref = {t: {k: x[k] for k in ("mean", "se", "n")} | {"per_block": x["per_block"], "rail_fJ_mean": x["rail_fJ_mean"]}
                for t, x in rr["e151"]["tiles"].items()}
    spec = {"prefix": "E163", "primary": "M9", "models": list(MODELS),
            "compare": [["E163-M1", "M6"], ["E163-M2", "M8"], ["E163-M3", "M7"]],
            "p_rules": [["E163-P1", "fp32"], ["E163-P2", "fp16"], ["E163-P3", "int8"]],
            "b_rules": [["E163-B1", ["fp32", "fp16"], "floats"], ["E163-B2", ["int8"], "int8"]],
            "h_rules": [["E163-H1", "fp32"], ["E163-H2", "fp16"], ["E163-H3", "int8"]],
            "coverage_rules": {"power": "E163-C1", "heat": "E163-H4"},
            "real_rules": {"R1": "E163-R1", "R2": "E163-R2", "scored": real_p1, "exclude_from_pool": real_all, "beside_all": real_all},
            "sets": {"priority1_by_format": p1, "coverage_tiles": cov, "new_kinds": new, "p2_tests": p2, "anchors": anchors,
                     "unaimed": sorted(sub["unaimed_synthetic"]), "unaimed_beside": sorted(sub["unaimed_with_float_real"])},
            "mins": mins, "min_kept_passes_scored": 2, "min_tile_passes": 2, "bootstrap": bs,
            "reruns": {"id": "E163-K14", "prime": "E163-K14prime", "flat_w": 0.05,
                       "tiles": {t: {k: x[k] for k in ("source", "footing", "session")} for t, x in sorted(reruns.items())}},
            "kc": "E163-KC", "cs0": "reported", "cs1": None, "cs_prefix": "E163-CS0",
            "u_rule": {"id": "E163-U1", "set": "unaimed", "beside_set": "unaimed_beside", "other": "M6", "min_tiles": 8},
            "rank1": {"id": "E163-RANK1", "needs": {"E163-M1": "BETTER", "E163-U1": "PASS", "E163-B1": "PASS", "E163-B2": "PASS",
                                                     "E163-C1": "PASS"}},
            "byte_twin": {"tile": "fp32.b_onebit_b20_pi", "twin": "fp32.cal_pi_b20 (docs/reports/data/2026-11-04-q140m-m9/bench-check/tiles/)",
                          "expected_error_w": 0.311, "expected_error_se_w": 0.198,
                          "source": "README-predictions.md A1-2; recount-rule/recount-rule.txt, fp32.cal_pi_b20 at 27 points: 3pt-N -0.311, e(27) 0.198"},
            "e151_block": {"id": "E163-KE", "prime": "E163-KEprime", "tiles": sorted(e151_ref), "reported": sorted(rr["e151"]["reported"]),
                           "flat_w": 0.05, "min_blocks": 2, "block_passes": [16350, 16359], "chain_sha256": chain, "ref": e151_ref,
                           "ref_blocks": rr["e151"]["blocks_kept"]},
            "below_zeros_tile": None, "p2_compare_id": "E163-M1-all", "classes": classes}
    binom48 = S.binom_low(48)
    assert binom48 == 42
    reg = {
        "experiment": "E163",
        "date": "2026-11-04",
        "registration": "tools/claims-v3/e163/E163.md (committed first and alone in 64dff136, 09:33:22 PST, before any other E163 file "
                        "and before any E163 data)",
        "request": "Q141(a) (the card half's desk preparation; the owner's mandate of Mon 2 Nov 2026, ~18:40 PST, carried; goal: predict the "
                   "power and heat of numeric computations as accurately as possible); Q140's final critic card_half[0], desk_next 1 and 7; "
                   "ranks 1, 4 (reference half), 9 (real tiles) and 14 (re-runs); kinds page section 11 item 6 (#11-what-is-still-open)",
        "card": "aifoundry3 card 0 (no V3_DEVICE, lock etsoc-shire0), 600 MHz as its boot-time TDP of 0 latches it, TDP 0 W and threshold 65 C as read, never set",
        "frozen_inputs": {"sha256": SOURCES, "ref_errors_sha256": sha(REF_ERRORS), "rerun_ref_sha256": sha(RERUN_REF),
                          "commits": {"pool7": "75802201 (Q140(x), 03:27:39 PST); dated notes 3c9bb2ba (04:18:24 PST)",
                                      "m9": "1f244140 (Q140(m), 01:12:04 PST); registration 8dfafae3 (00:45:51 PST); corrections through e95c3f89 (no frozen file changed)",
                                      "rank4": "rank4_rule.json, score_rank4.py, selftest-rank4.txt in 75802201",
                                      "footing": "Q139(u): rule d4c36bfe, slopes f47669d1", "ccheck": "Q139(k): 60b91395, corrected 4946a992",
                                      "parent": "E153: registration 359c96b2, A1 e6ca949d, data 8e18eb67, corrections 42e79d23 and e0f5a18a (its data README, C1-C7)"},
                          "band_rule": pred["band_rule_M9"]},
        "plan": {
            "plans": {"FULL": {"sequence": [16310, 16311, 16312, 16350, 16351, 16352, 16313], "budget_s": 4200,
                               "what": "three kinds passes, the E151 block (three B blocks), a fourth pass only if the budget rule admits it"},
                      "TWO": {"sequence": [16310, 16311], "budget_s": 2280,
                              "what": "the registered subset for a short window: two kinds passes as designed; the E151 block dropped by name"},
                      "SHORT": {"sequence": [16320, 16321], "budget_s": 1800,
                                "what": "two 77-run passes: the four priority-2 tests dropped first, then the 16 re-runs; the E151 block dropped by name"}},
            "default_plan": "FULL", "reserve_s": 60, "gap_s": 10, "card_minutes_cap": {"FULL": 70, "TWO": 38, "SHORT": 30},
            "first_estimate_s": {"kinds97": 1000, "kinds77": 820, "e151": 190},
            "kinds_passes": [16310, 16311, 16312, 16313], "short_passes": [16320, 16321], "e151_blocks": [16350, 16351, 16352],
            "smoke": 16301, "stoptest": 16302, "smoke_items": list(SMOKE),
            "runs_per_pass": {"kinds": 97, "short": 77, "e151_block": 34}, "burn_in_runs": 2,
            "short_drop": {"priority2_tests_first": list(P2_DROP_ORDER), "then_reruns": sorted(reruns)},
            "min_kept_passes_scored": 2, "min_tile_passes": 2, "min_tiles": mins, "min_kept_e151_blocks": 2,
            "order": "Random('E163|aifoundry3|<pass>'): the 77 tiles (pool 7's 61, the 16 re-runs; 57 in a SHORT pass) dealt round-robin "
                     "into three segments (26, 26, 25; 19, 19, 19 in SHORT), each with E78's six anchors, reshuffled; the tie first and last. "
                     "E151 blocks: E151's B design (e151_common.pass_order's B branch) with Random('E163|aifoundry3|<block>')",
            "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz, two anchor_pi burn-ins a "
                        "pass; every measured launch through tools/claims-v3/ccheck/sparsity_ccheck.sh (the C-logging host, the power passes' "
                        "kernel, --c-log --c-poison); the heater on E78's host",
            "e151_protocol": "E151's trains: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0, 4 s runs, every launch through the C wrapper; "
                             "E151's B design: 4 settling hb1, hb1 between every pair of b1_0..b1_5 (twice each), b1_6, b1_7, the units "
                             "[hb2 b2_7 hb2] and [hb1d b1d_7 hb1d]: 34 runs",
            "stops": {"kinds": {"board_w": 65.0, "die_shire0_c": 70.0, "run_e78_max_c": 70.0},
                      "e151": {"board_w": 45.0, "die_shire0_c": 68.0, "run_e78_max_c": 70.0},
                      "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "stoptest_age_max_s": 2.0,
                      "how": "E153's (E141's) code: the newest line of the running sampler's file (telemetry.jsonl.raw), read by the main path "
                             "before every launch and every 0.1 s while it waits and by the in-run watcher every 0.1 s for the whole pass; the "
                             "die stop reads temp_c.minshire[0]"},
            "time_gates": "E163_LATEST_START (no session starts after it) and E163_DEADLINE (a pass's or block's projected end must be "
                          "before it): both required, set at his go from the round's time gates; session_e163.sh refuses without them",
            "reduction": {"primary": "Q139(u)'s one footing: reduce_e163.py (E78's reduce_e78.py unchanged) --leak 0.20563713796102187 "
                                     "--no-refit --drop-dips; E78's run and pass gates and its aifoundry3 config gate",
                          "beside": "the session-own footing: leakage auto (fitted on this session), dips kept, scored with every rule, "
                                    "reported beside the primary",
                          "arms": ["leak auto, dips removed", "k frozen, dips kept", "leak 0.1994, dips removed", "leak 0.3803, dips removed",
                                   "leak 0, dips removed", "pass gates opened (footing)"],
                          "e151": "reduce_e163.py --e151 --drop-dips --rail-filter (E151's registered primary: E82 A2's dips and E151's "
                                  "rail glitches removed, leakage auto, E78's configuration gate), then E151's Book (rail_raw, E130's train "
                                  "gate at 0.25 W) divided by c_rb 0.81"},
            "bootstrap": bs,
        },
        "model": {"name": "M9 (Q140(m), 1f244140), scored; M8, M7 and M6 frozen beside it",
                  "units": "D: W over the type's own zeros at 600 MHz on aifoundry3 card 0 (M9's own footing, scale 1); dT: C over the "
                           "run's launch reading over the kinds run (4.5 s), M7's heat law carried by M9",
                  "heat_coef_a3": {"S": m9["heat"]["coef"]["S|aifoundry3"], "ST": m9["heat"]["coef"]["ST|aifoundry3"]},
                  "heat_pool_a3_rms_c": heat_rms,
                  "power_pool_a3_rms_w": {f: refj["families"]["int8" if f == "int8" else "float"]["pool_check"][f"{f}|a3"]["rms_w"]
                                          for f in FORMATS},
                  "band_k": {"floats": m9["families"]["float"]["band_k"], "int8": m9["families"]["int8"]["band_k"]},
                  "footing_k_w_per_c": pred["footing"]["k_w_per_c"]["a3"]},
        "tiles": tiles,
        "reruns": reruns,
        "reference_errors": {"power_a3": ref, "power_both_cards": ref_both, "heat_normal_a3": heat_ref,
                             "n": {f: len(ref[f]) for f in ref}},
        "sets": spec["sets"] | {"classes": classes, "real_priority1": real_p1, "real_all": real_all},
        "spec": spec,
        "rank4": {"rule": f"{P7}/rank4_rule.json", "scorer": f"{P7}/score_rank4.py",
                  "anchors_floats": ["fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp16.anchor7_randn_a", "fp16.anchor7_randn_b"],
                  "anchors_int8": ["int8.anchor7_full_a", "int8.anchor7_full_b"],
                  "how": "scored after E164 by score_rank4.py --a3 <E163 scored.json> --c1 <E164 scored.json> --pair E163/E164; E163 "
                         "supplies the reference half (its primary power_rows: measured, n_passes, sd, per_pass) and runs all nine anchors "
                         "in every pass"},
        "arm27": {"registered_by": "Q141(t)", "dir": "docs/reports/data/2026-11-04-q141t-s7-recount/",
                  "what": "M9's frozen prices on 27-point recounts of pool 7's S tiles (and the priority-2 b20-on-1/3 tile): a reported arm, "
                          "passed to score_e163.py --arm27 as {tile: D_w} if Q141(t)'s registration is committed before E163's claim"},
        "binomial_low_2p5": {"48": binom48, "12": S.binom_low(12), "10": S.binom_low(10)},
    }
    out = os.path.join(HERE, "predictions-e163.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    # the rules' intervals before any data (the registered draws and seeds)
    L = ["E163 planned intervals (make_predictions_e163.py; the registered draws and seeds; nothing measured)", ""]
    for rid, f in spec["p_rules"]:
        iv = S.draw_interval(ref, {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
        L.append(f"{rid}: rms over {len(p1[f])} {f} kinds, M9's nested reference {len(ref[f])} aifoundry3 rows: "
                 f"{iv['lo95']:.3f}-{iv['hi95']:.3f} W (median {iv['median']:.3f})")
    for rid, fam, _ in spec["b_rules"]:
        mix = {f: len(p1[f]) for f in fam}
        iv = S.draw_interval(ref, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
        L.append(f"{rid}: mean over {sum(mix.values())} kinds: {iv['lo95']:+.3f} to {iv['hi95']:+.3f} W (median {iv['median']:+.3f})")
    for rid, f in spec["h_rules"]:
        iv = S.draw_interval(heat_ref, {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
        L.append(f"{rid}: heat rms over {len(p1[f])} {f} kinds: {iv['lo95']:.3f}-{iv['hi95']:.3f} C")
    L.append(f"E163-C1 / E163-H4: at least {binom48} of 48 inside; E163-R2: all 10 priority-1 real tiles inside (probability "
             f"0.95^10 = {0.95 ** 10:.2f} if the bands are exact)")
    hw = {f: sorted((r["M9"]["D_95"][1] - r["M9"]["D_95"][0]) / 2 for n, r in tiles.items() if n in cov and r["type"] == f)
          for f in FORMATS}
    L.append("M9's frozen 95% power half-widths on the priority-1 kinds: " +
             "; ".join(f"{f} {hw[f][0]:.3f}-{hw[f][-1]:.3f} W" for f in FORMATS))
    for other in ("M6", "M8", "M7"):
        d = sorted(abs(tiles[n]["M9"]["D_w"] - tiles[n][other]["D_w"]) for n in cov)
        md = statistics_median(d)
        L.append(f"|M9 - {other}| on the 48 priority-1 kinds: median {md:.3f} W, max {d[-1]:.3f} W")
    du = sorted(abs(tiles[n]["M9"]["D_w"] - tiles[n]["M6"]["D_w"]) for n in spec["sets"]["unaimed"])
    L.append(f"|M9 - M6| on the 12 unaimed U tiles: median {statistics_median(du):.3f} W, max {du[-1]:.3f} W (U1 can only resolve where "
             f"they differ)")
    open(os.path.join(HERE, "planned-intervals.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"wrote {os.path.relpath(out, ROOT)}: {len(tiles)} tiles + {len(reruns)} re-runs; reference rows aifoundry3 "
          f"{reg['reference_errors']['n']}; heat pools {heat_rms}")


def statistics_median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


if __name__ == "__main__":
    main()
