#!/usr/bin/env python3
"""E153 (Q139): write predictions-e153.json, the freeze, before the claim of aifoundry3 card 0 and the first launch. A port of
tools/claims-v3/e141/make_predictions_e141.py with pool 6, M8 and the K1 re-run. Standard library only.

E153 adds no prediction. Every model number is copied from Q139(x)'s committed aifoundry3 predictions
(tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json, d98d2e34, made by Q139(m)'s predict_blind6.py at 122da8b6 with nothing
refitted); every power reference error from M8's nested leave-one-kind-out errors of the aifoundry3 rows, recomputed with Q139(m)'s own
fit_m8.run_family on the committed rows (ref_errors_e153.py -> ref-errors-m8.json, which reproduces nested-m8.json's pools exactly); the
heat reference from M7's heat pools, which M8 carries (m8.json > heat); the card scales from card-scale-blind6.json; the K1 comparison
values from E141's committed reduction (its own session footing) and from Q139(u)'s re-reduction of E141 on the one footing. Each
source's sha256 is checked against the value written here and recorded. The plan, the stops, the rules and the harness hashes (every
file the box runs, the pools, the binaries) are written here too, and planned-intervals.txt (the rules' intervals before any data).

    python3 tools/claims-v3/e153/make_predictions_e153.py            # writes predictions-e153.json and planned-intervals.txt beside it
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
P6 = "tools/claims-v3/kinds/blind6"
P5 = "tools/claims-v3/kinds/blind5"
QM = "docs/reports/data/2026-11-03-q139m-model"
QU = "docs/reports/data/2026-11-03-q139u-footing"
E141D = "docs/reports/data/2026-11-02-e141-blind5-aifoundry3"
SOURCES = {   # the frozen inputs and the sha256 each must have (Q139(x)'s d98d2e34, Q139(m)'s 122da8b6, Q139(u), E141, Q139(k))
    f"{P6}/predictions-blind6-aifoundry3.json": "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    f"{P6}/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    f"{P6}/MANIFEST": "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0",
    f"{P6}/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
    f"{P6}/card-scale-blind6.json": "6b04079139e05d168517779fbc97c6c9a720c69226585ee6c5e67d6857ff9312",
    f"{P6}/counts-blind6.json": "6f321736d1a5edd5e0965c83c1e3154d91807fe0b841ac622f8b3866da847190",
    f"{QM}/m8.json": "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
    f"{QM}/nested-m8.json": "f284b5407a98641ec33a57410be925a4c64199e0033b6c94ef893702de0f4905",
    f"{QM}/rows-m8.json": "6e3383ef10e2f8a3102755695c4ba95fe6367bd8ff17498a00382420349681d9",
    f"{QM}/fit_m8.py": "3764bc4c345412ae71d66f18f114d0fe395d8db90988d699988513a590b6bad7",
    f"{QU}/footing.json": "f589efaad1fc9b19390658f16a5ffd4ca71e23cde59fbcf2f5cc88c267a73a97",
    f"{QU}/reduced/e141-footing.json": "74b36e6854008de72ec6bb0b25cd039d8bb021924002b90eb22e70a674fe22dc",
    f"{E141D}/e141.json": "31b5d31912026069280aa6920f9669f4d6a45b8bd338472dd44c62484ad776d8",
    f"{P5}/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    f"{P5}/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
}
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
             "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp",
             "tools/claims-v3/ccheck/sparsity_ccheck.sh", "tools/claims-v3/ccheck/patch_host_ccheck.py",
             "tools/claims-v3/ccheck/build_host_ccheck.sh", "tools/claims-v3/ccheck/ccheck.py", "tools/claims-v3/ccheck/pick6.py"]
E153_FILES = ["e153_common.py", "run_e153.py", "block_e153.sh", "queue_e153.sh", "session_e153.sh", "check_e153.py",
              "preflight_e153.sh", "smoke_gate_e153.py", "reduce_e153.py"]
REF_ERRORS = "tools/claims-v3/e153/ref-errors-m8.json"
BOX_BINARIES = {   # read on aifoundry3 (~/aifoundry) at 06:40 PST, Tue 3 Nov 2026 (look.sh / build.sh in the lane's scratch, logs/)
    "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",   # E141's: the heater
    "build/sparsity/kernel/sparsity.elf": "d521e43248d00b4da455ada7020741f39b8940e52bbbce05380beccedcd17d19",  # every launch's kernel
    "build/ccheck/b/host/sparsity_host": "99ed75fbcad323b4a640377710d1f9c5428224401e988400177e9c0749e911a4",   # the C-logging host
    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
}
K1_TILES = ("fp32.b_exp_busy_a_const", "fp32.real_pythia_ln1_q", "fp16.sparse24_aligned", "fp16.exp_only", "int8.gray_a",
            "int8.b_line_zero_one")
FORMATS = ("fp32", "fp16", "int8")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def binom_low(n, p=0.95, alpha=0.025):
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def main():
    for rel, want in SOURCES.items():
        have = sha(rel)
        if have != want:
            raise SystemExit(f"{rel}: sha256 {have} != the committed {want}")
    J = lambda rel: json.load(open(os.path.join(ROOT, rel)))  # noqa: E731
    pred = J(f"{P6}/predictions-blind6-aifoundry3.json")
    m8 = J(f"{QM}/m8.json")
    spec = {t["name"]: t for t in J(f"{P6}/blind6.json")["tiles"]}
    cs = J(f"{P6}/card-scale-blind6.json")
    refj = J(REF_ERRORS)
    if refj["sha256"].get(f"{QM}/nested-m8.json") != SOURCES[f"{QM}/nested-m8.json"] or \
            refj["sha256"].get(f"{QM}/rows-m8.json") != SOURCES[f"{QM}/rows-m8.json"]:
        raise SystemExit("ref-errors-m8.json was not made from the committed nested-m8.json / rows-m8.json")
    tiles = {}
    for name, t in sorted(pred["tiles"].items()):
        s = spec[name]
        row = {"type": t["type"], "priority": int(t["priority"]), "pool_anchor": bool(s.get("anchor")), "case": t["case"],
               "real": t["case"].startswith("R"), "hold_candidate": bool(s.get("hold_candidate")),
               "sha256": t["sha256"], "sha256_matches_manifest": t["sha256_matches_manifest"]}
        for m in ("M8", "M7", "M6"):
            x = t[m]
            row[m] = {"D_w": x["D_w"], "D_95": x["D_95"], "S_w": x["S_w"], "dT_win_c": x["dT_win_c"], "dT_win_95": x["dT_win_95"],
                      "D600_a3_footing_w": x["D600_a3_footing_w"]}
        tiles[name] = row
    assert len(tiles) == 50 and all(tiles[n]["sha256_matches_manifest"] for n in tiles)
    assert sum(1 for r in tiles.values() if r["real"]) == 12
    # power reference: M8's nested errors of every aifoundry3 row of each format (both cards: an arm)
    ref, ref_both = {}, {}
    for fam in ("float", "int8"):
        for r in refj["families"][fam]["row_errors"]:
            if r["err_w"] != r["err_w"]:      # nan
                continue
            ref_both.setdefault(r["type"], []).append(r["err_w"])
            if r["card"] == "a3":
                ref.setdefault(r["type"], []).append(r["err_w"])
    pools = m8["heat"]["interval_pool_by_format_card_c"]
    heat_rms = {f: pools[f"{f}|aifoundry3"]["rms_c"] for f in FORMATS}
    rng = random.Random("E153|heat-reference")
    heat_ref = {f: [rng.gauss(0.0, heat_rms[f]) for _ in range(2000)] for f in FORMATS}
    new = sorted(n for n, r in tiles.items() if not r["pool_anchor"])
    p1 = {f: sorted(n for n in new if tiles[n]["type"] == f and tiles[n]["priority"] == 1) for f in FORMATS}
    cov = sorted(n for n in new if tiles[n]["priority"] == 1)
    real = sorted(n for n in new if tiles[n]["real"])
    p2 = sorted(n for n in new if tiles[n]["priority"] == 2)
    anchors = sorted(n for n, r in tiles.items() if r["pool_anchor"])
    assert len(cov) == 30 and len(new) == 44 and len(anchors) == 6 and len(p2) == 14
    e141 = J(f"{E141D}/e141.json")["items"]
    e141f = J(f"{QU}/reduced/e141-footing.json")["items"]
    k1 = {t: {"type": t.split(".")[0], "E141_session": {k: e141[t]["D"][k] for k in ("mean", "se", "n", "ci95")},
              "E141_footing": {k: e141f[t]["D"][k] for k in ("mean", "se", "n", "ci95")}} for t in K1_TILES}
    scale = {"M8_applied": {c: {f: cs["cards"][c][f]["scale_applied_by_model"]["M8"] for f in ("floats", "int8")} for c in cs["cards"]},
             "cheap_read_a3": {f: {k: v["pred_scale"] for k, v in cs["cards"]["aifoundry3"][f]["cheap_read_predicted_scale"].items()}
                               for f in ("floats", "int8")},
             "cheap_read_c1": {f: {k: v["pred_scale"] for k, v in cs["cards"]["aifoundry1c1"][f]["cheap_read_predicted_scale"].items()}
                               for f in ("floats", "int8")},
             "cheap_read_a2": {f: {k: v["pred_scale"] for k, v in cs["cards"]["aifoundry2"][f]["cheap_read_predicted_scale"].items()}
                               for f in ("floats", "int8")},
             "what_pool6_measures": cs["what_pool6_measures"]}
    harness = {
        "card_code_unchanged_sha256": {rel: sha(rel) for rel in CARD_CODE},
        "e153_card_files_sha256": {f"tools/claims-v3/e153/{f}": sha(f"tools/claims-v3/e153/{f}") for f in E153_FILES},
        "pool_sha256": dict({rel: SOURCES[rel] for rel in (f"{P6}/blind6.json", f"{P6}/MANIFEST", f"{P6}/SHA256SUMS",
                                                            f"{P6}/predictions-blind6-aifoundry3.json", f"{P5}/blind5.json",
                                                            f"{P5}/SHA256SUMS")},
                            **{os.path.relpath(p, ROOT): hashlib.sha256(open(p, "rb").read()).hexdigest()
                               for p in sorted(glob.glob(os.path.join(ROOT, P6, "tiles", "*", "*.bin")))},
                            **{f"{P5}/tiles/{t.split('.')[0]}/{t}.bin": sha(f"{P5}/tiles/{t.split('.')[0]}/{t}.bin") for t in K1_TILES}),
        "box_binaries_sha256": BOX_BINARIES,
    }
    assert len([k for k in harness["pool_sha256"] if k.endswith(".bin")]) == 56
    mins = {"fp32": 6, "fp16": 4, "int8": 6, "floats": 8, "real": 8}
    reg = {
        "experiment": "E153",
        "date": "2026-11-03",
        "request": "Q139 (the owner's words of Mon 2 Nov 2026, ~18:40 PST, carried: settle the power model's open questions; goal: predict "
                   "the power and heat of numeric computations as accurately as possible); Q138's final critic ranks 2, 5 and 14 (with 8's "
                   "real-tile sub-rule); kinds page section 11 item 6 (#11-what-is-still-open)",
        "card": "aifoundry3 card 0 (no V3_DEVICE), 600 MHz as its boot-time TDP of 0 latches it, TDP 0 W and threshold 65 C as read, never set",
        "frozen_inputs": {"sha256": SOURCES, "ref_errors_sha256": sha(REF_ERRORS),
                          "commits": {"pool_and_predictions": "d98d2e34e1de004bb49a8e728c19b8f7b5f5bb70 (Q139(x), 05:39:23 PST)",
                                      "m8": "122da8b6 (Q139(m), 04:57:59 PST; registration f640fb7a)",
                                      "footing": "f47669d1 (Q139(u); rule d4c36bfe)", "ccheck": "60b91395, corrected 4946a992 (Q139(k))",
                                      "pool_corrections": "e9d20985 (Q139(b)'s fix pass: no frozen file changed)"},
                          "band_rule": pred["band_rule_M8"]},
        "plan": {
            "passes": [15310, 15311, 15312, 15313], "smoke": 15301, "stoptest": 15302,
            "smoke_items": ["anchor_pi", "fp32.zeros", "fp32.randn", "fp32.real_qwen_softmax_v", "fp32.anchor6_zeros",
                            "fp16.real_smol_softmax_v", "fp16.zeros", "int8.a_zeros_b_lineflip", "int8.zeros", "fp32.b_exp_busy_a_const"],
            "runs_per_pass": 76, "burn_in_runs": 2, "min_kept_passes_scored": 2, "min_tile_passes": 2, "min_tiles": mins,
            "order": "Random('E153|aifoundry3|<pass>'): the 56 tiles (pool 6's 50, the 6 K1 tiles) dealt into three segments of 19, 19 and "
                     "18, each with E78's six anchors, reshuffled; the tie first and last (E141's order with 56 tiles)",
            "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz; every measured launch "
                        "through tools/claims-v3/ccheck/sparsity_ccheck.sh (the C-logging host, the power passes' kernel, --c-log "
                        "--c-poison); the heater on E78's host",
            "budget_s_from_session_start": 3300, "reserve_s": 60, "card_minutes_max": 55, "first_pass_estimate_s": 880, "gap_s": 10,
            "deadline": "2026-11-03 21:50 PST for a pass's projected end (no card session starts after 21:00 PST, session_e153.sh refuses one; every run ends by 22:00 PST)",
            "stops": {"board_w": 65.0, "die_shire0_c": 70.0, "run_e78_max_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "how": "E141's values and code on this card (board 65 W, die 70 C); the newest line of the running sampler's file "
                             "(telemetry.jsonl.raw), read by the main path before every launch and every 0.1 s while it waits and by "
                             "the in-run watcher every 0.1 s for the whole pass; the die stop reads temp_c.minshire[0]"},
            "reduction": {"primary": "Q139(u)'s one footing: reduce_e153.py (E78's reduce_e78.py unchanged) --leak 0.20563713796102187 "
                                     "--no-refit --drop-dips (k frozen for aifoundry3 in footing.json; E82 A2's dip rule once); E78's run "
                                     "and pass gates and its aifoundry3 config gate",
                          "beside": "E141's session-own footing: reduce_e153.py with leakage auto (fitted on this session), dips kept "
                                    "(E141's registered primary), scored with every rule and reported beside the primary",
                          "arms": ["leak auto, dips removed", "k frozen, dips kept", "leak 0.1994, dips removed",
                                   "leak 0.3803, dips removed", "leak 0, dips removed", "pass gates opened (footing)"]},
            "k1": {"tiles": list(K1_TILES), "flat_tolerance_w": 0.05,
                   "source": "tools/claims-v3/ccheck/pick6.py (Q139(k)): per format the two pool-5 tiles measured most tightly on both cards"},
            "bootstrap": {"draws": 20000, "seed": 15300},
        },
        "harness": harness,
        "model": {"name": "M8 (Q139(m), 122da8b6), scored; M7 and M6 frozen beside it",
                  "units": "D: W over the type's own zeros at 600 MHz on aifoundry3 card 0 (M8's own footing, scale 1); dT: C over the "
                           "run's launch reading over the kinds run (4.5 s), M7's heat law carried by M8",
                  "heat_coef_a3": {"S": m8["heat"]["coef"]["S|aifoundry3"], "ST": m8["heat"]["coef"]["ST|aifoundry3"]},
                  "heat_pool_a3_rms_c": heat_rms,
                  "power_pool_a3_rms_w": {f: refj["families"]["int8" if f == "int8" else "float"]["pool_check"][f"{f}|a3"]["rms_w"]
                                          for f in FORMATS},
                  "footing_k_w_per_c": pred["footing"]["k_w_per_c"]["a3"]},
        "tiles": tiles,
        "k1": k1,
        "card_scale": scale,
        "reference_errors": {"power_a3": ref, "power_both_cards": ref_both, "heat_normal_a3": heat_ref,
                             "n": {f: len(ref[f]) for f in ref}},
        "sets": {"priority1_by_format": p1, "coverage_tiles": cov, "new_kinds": new, "real_tiles": real, "p2_tests": p2,
                 "anchors": anchors, "hold_candidates": sorted(n for n, r in tiles.items() if r["hold_candidate"])},
        "rules": {
            "E153-KC": "the C check: every measured launch of a pool-6 tile in a kept pass has a C record (same t_start_ms and t_end_ms) "
                       "that tools/claims-v3/ccheck/ccheck.py check judges PASS (bit-exact against the RTL's arithmetic; ROUNDING, "
                       "UNMODELLED and FAIL count as not checked, Q139(k)'s verdict table); PASS if every pool-6 tile's launches do. A tile "
                       "with any launch not PASS leaves the scored set of every rule below (named); the rules are also given over all tiles",
            "E153-K1": "the critic's rank-14 sub-rule on the 6 pool-5 tiles: K1-C every launch PASS (the critic's 'exact or within the "
                       "format's rounding' is also read, as PASS or ROUNDING, and reported) AND K1-D |D_E153 - D_E141| <= 0.05 W on each "
                       "tile, on the same footing on both sides (primary: Q139(u)'s one footing, E141 as Q139(u) re-reduced it; beside: "
                       "E141's own session footing against this session's own); K1' = K1-C AND K1-W, Welch's same-card 95% interval "
                       "(Q139(k)'s rule, pick6.welch) on each tile, registered beside it",
            "E153-P1": "power fp32: rms(D - M8) over the 12 priority-1 fp32 kinds (at least 6) against the 2.5-97.5% range of the rms of "
                       "as many draws with replacement from M8's nested errors of every aifoundry3 fp32 row (ref-errors-m8.json, card a3): "
                       "PASS at or below the 97.5% point, FAIL above; below the 2.5% point is reported as better than the nested score says",
            "E153-P2": "power fp16: as P1, the 6 priority-1 fp16 kinds (at least 4), aifoundry3 fp16 rows",
            "E153-P3": "power int8: as P1, the 12 priority-1 int8 kinds (at least 6), aifoundry3 int8 rows",
            "E153-B1": "bias, floats (the critic's B1): mean(D - M8) over the 18 priority-1 float kinds (at least 8) against the 2.5-97.5% "
                       "range of the mean of as many draws (same format mix) from the same nested errors: PASS inside, FAIL outside "
                       "(HIGH when M8 predicts too much, LOW when too little)",
            "E153-B2": "bias, int8 (the critic's B2): as B1, the 12 priority-1 int8 kinds (at least 6)",
            "E153-C1": f"coverage, power (the critic's): kinds inside M8's frozen 95% band among the 30 priority-1 kinds; PASS if at least "
                       f"the 2.5% point of Binomial(n, 0.95) ({binom_low(30)} of 30), FAIL if fewer; NOT SCORED under 10",
            "E153-M1": "M8 against M6 (the critic's): d = rms(M8 errors) - rms(M6 errors) over the 30 priority-1 kinds, 95% interval by a "
                       "paired bootstrap over tiles (E141's compare_rule): BETTER (the rule's PASS) if the upper bound < 0, WORSE if the "
                       "lower bound > 0, else NOT RESOLVED",
            "E153-M2": "M8 against M7: as M1",
            "E153-H1": "heat fp32: rms(dT_win - M8's dT) over the priority-1 fp32 kinds (at least 6) against the 2.5-97.5% range of the rms "
                       "of as many draws from a deterministic normal sample of 2,000 points with M7's nested aifoundry3 heat rms for fp32 "
                       f"(m8.json heat, carried from M7: {heat_rms['fp32']:.3f} C): PASS at or below the 97.5% point, FAIL above",
            "E153-H2": f"heat fp16: as H1 ({heat_rms['fp16']:.3f} C; at least 4)",
            "E153-H3": f"heat int8: as H1 ({heat_rms['int8']:.3f} C; at least 6)",
            "E153-H4": f"coverage, heat: as C1, M8's frozen dT band ({binom_low(30)} of 30)",
            "E153-R1": "the real-tile sub-rule (critic rank 8, over all 12 real tiles, pool 6's CORRECTIONS C9), rms within the pool's own: "
                       "rms(D - M8) over the 12 real tiles (at least 8) at or below the 97.5% point of the rms of as many draws (same "
                       "format mix) from the errors of the pool's own non-real new kinds (all priorities): PASS, else FAIL",
            "E153-R2": "the real-tile sub-rule, no tile outside its band: every measured real tile inside M8's frozen 95% band",
            "E153-CS0": "the card scale on aifoundry3 (rank 5): the measured scale, median over pool-6 tiles of D / M8's D (floats with "
                        "D >= 5 W, int8 with D >= 1 W, measured and predicted; anchors included), within 1% of M8's applied 1.0: PASS, "
                        "else FAIL; per format family; the cheap-read predictor's leave-one-card-out values for aifoundry3 are reported "
                        "beside (V600^2 physical 1.0220 floats)",
            "E153-CS1": "the card scale of card 1 (rank 5, joint with E157): median over the same pool-6 tiles of D_card1 / D_E153 "
                        "(floats D >= 5 W, int8 D >= 1 W on both) within 1% of M8's 0.9616 (floats and int8): PASS, else FAIL; the "
                        "cheap-read predictions (V600^2 physical 0.9102 floats, 0.9011 int8, and each other read and form) within 1% of "
                        "the measured scale, reported per read; scored by score_e153.py --e157 where E157's registered-primary reduction "
                        "exists, else NOT SCORED here",
            "E153-CS2": "the card scale of aifoundry2 (joint with E160): (c_w - c_zeros) / D600 on bursts pinned at 795-800 MHz, D600 this "
                        "session's measured D; E160's to score (E153 provides D600); not scored here",
            "min_passes": "fewer than 2 kept passes on the primary: every rule NOT SCORED; a tile with fewer than 2 kept passes is left out",
        },
        "reported_not_verdicts": [
            "every rule on E141's session-own footing (leak auto, dips kept) beside the primary, and at every arm",
            "M7's and M6's rms, bias and coverage beside M8's on every set, per format and by case (E, R, Z, S, C, B, L, W)",
            "the 14 priority-2 tests, all 44 new kinds together (rms, coverage, paired M8 - M6), and the pool's six anchors",
            "every rule over all tiles when the C check removes any",
            "K1's tiles on both footings, the flat 0.05 W and Welch's interval, each tile's C verdicts",
            "int8.a_zeros_b_lineflip, which M8 puts below its zeros (-0.339 W [-1.73, +1.05]; M7 +0.049, M6 +0.505): the bsat term's test",
            "heat at the measured run length (M7's ST term, -0.0490 C/W/s on aifoundry3)", "the die rise per board W against 0.1186 C/W",
            "the reference on both cards' rows (an arm of P1-P3)", "E78's anchors and the tie against E141's on this card",
            "the C log's DMA: K1's D against E141's is the test of whether the extra 2 MiB a launch moves the watts"],
        "expected": "KC and K1-C PASS (E104's 110 silicon reads PASS through the same reference; the kernel is unchanged); K1-D FAIL on "
                    "at least one tile (the flat 0.05 W is narrower than a same-card repeat's noise, Q139(k) finding 2) and K1-W PASS; "
                    "P1-P3 PASS; B1 and B2 PASS (one footing for training and test); C1 PASS; M1 NOT RESOLVED (M8 and M6 differ by "
                    "little on most tiles; M8's nested gain over M6 as frozen was -0.007 W [-0.066, +0.049] on pool 5's rows) and M2 "
                    "NOT RESOLVED; H1-H3 PASS and H4 PASS; R1 PASS and R2 FAIL or PASS (12 bands at 95% all inside has probability "
                    "0.54); CS0 PASS for floats (aifoundry3 is M8's reference card) and int8 PASS or FAIL (int8's scale rests on D of "
                    "1-7 W); CS1 FAIL for the cheap read (V600^2 missed card 1 by 5% in training) and PASS or FAIL for M8's 0.9616. "
                    "Likeliest misses named now: the exponent-heavy kinds (case E; E147 found the card pays 0.82-0.84 of the models' "
                    "watts on exponent flips and M8 kept no exponent term), int8.a_zeros_b_lineflip (M8's bsat discount alone "
                    "-0.90 W), int8's whole-line kinds (case L) and the W8A8 real tiles (E141's steady misses), and fp16's two-term "
                    "tiles (fp16.real_smol_softmax_v, fp16.real_qwen_dequant_v: pool 6's CORRECTIONS C1).",
        "binomial_low_2p5": {"30": binom_low(30), "44": binom_low(44), "12": binom_low(12)},
    }
    out = os.path.join(HERE, "predictions-e153.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    # the rules' intervals before any data (the registered draws)
    import score_e153 as S  # noqa: E402
    bs = reg["plan"]["bootstrap"]
    L = ["E153 planned intervals (make_predictions_e153.py; the registered draws and seeds; nothing measured)", ""]
    for rid, f in (("E153-P1", "fp32"), ("E153-P2", "fp16"), ("E153-P3", "int8")):
        iv = S.draw_interval(ref, {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
        L.append(f"{rid}: rms over {len(p1[f])} {f} kinds, nested reference {len(ref[f])} rows: {iv['lo95']:.3f}-{iv['hi95']:.3f} W "
                 f"(median {iv['median']:.3f})")
    for rid, mix in (("E153-B1", {"fp32": len(p1["fp32"]), "fp16": len(p1["fp16"])}), ("E153-B2", {"int8": len(p1["int8"])})):
        iv = S.draw_interval(ref, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
        L.append(f"{rid}: mean over {sum(mix.values())} kinds: {iv['lo95']:+.3f} to {iv['hi95']:+.3f} W (median {iv['median']:+.3f})")
    for rid, f in (("E153-H1", "fp32"), ("E153-H2", "fp16"), ("E153-H3", "int8")):
        iv = S.draw_interval(heat_ref, {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
        L.append(f"{rid}: heat rms over {len(p1[f])} {f} kinds: {iv['lo95']:.3f}-{iv['hi95']:.3f} C")
    L.append(f"E153-C1 / E153-H4: at least {binom_low(30)} of 30 inside; E153-R2: all 12 inside (probability 0.95^12 = "
             f"{0.95 ** 12:.2f} if the bands are exact)")
    hw = {f: sorted((r["M8"]["D_95"][1] - r["M8"]["D_95"][0]) / 2 for n, r in tiles.items() if n in cov and r["type"] == f)
          for f in FORMATS}
    L.append("M8's frozen 95% power half-widths on the priority-1 kinds: " +
             "; ".join(f"{f} {hw[f][0]:.3f}-{hw[f][-1]:.3f} W" for f in FORMATS))
    d86 = sorted(abs(tiles[n]["M8"]["D_w"] - tiles[n]["M6"]["D_w"]) for n in cov)
    L.append(f"|M8 - M6| on the 30 priority-1 kinds: median {d86[len(d86) // 2]:.3f} W, max {d86[-1]:.3f} W (M1 can only resolve where "
             f"the two models' predictions differ)")
    open(os.path.join(HERE, "planned-intervals.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"wrote {out}: {len(tiles)} tiles + {len(k1)} K1; reference rows aifoundry3 {reg['reference_errors']['n']}; heat pools {heat_rms}")


if __name__ == "__main__":
    main()
