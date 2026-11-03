#!/usr/bin/env python3
"""E141 (Q138): write predictions-e141.json, the freeze, before the claim of aifoundry3 card 0 and the first launch (E141: a port of
tools/claims-v3/e141/make_predictions_e141.py with aifoundry3's predictions, reference rows, heat pools, stops and binaries). Standard library only.

E141 adds no prediction. Every model number is copied from Q138(x)'s committed aifoundry3 predictions
(tools/claims-v3/kinds/blind5/predictions-blind5-aifoundry3.json, dac39d97, made by Q138(m)'s predict_blind5.py at 3a210f2b with nothing
refitted), every reference error from Q138(m)'s committed nested scores (docs/reports/data/2026-11-02-q138m-model/loko-m7.json ›
families.<family>.row_errors, the aifoundry3 rows, card `a3`) and M7's heat pools (m7.json › heat). Each source's sha256 is checked against the value
written here and recorded. The plan, the stops, the rules and the harness hashes (every file the box runs, the pool, the binaries) are
written here too.

    python3 tools/claims-v3/e141/make_predictions_e141.py            # writes predictions-e141.json beside it
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q = "docs/reports/data/2026-11-02-q138m-model"
P5 = "tools/claims-v3/kinds/blind5"
SOURCES = {   # the frozen inputs and the sha256 each must have (Q138(x)'s result and Q138(m)'s commit)
    f"{P5}/predictions-blind5-aifoundry3.json": "396d336015664c46f6d181440059023d980df57e07f6e47206b3700283ab9bf1",
    f"{P5}/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    f"{P5}/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
    f"{Q}/m7.json": "bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2",
    f"{Q}/loko-m7.json": "c30320b7a8f290e6f5640db4897b68a5876c63627c90315accec578661fd9322",
}
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
             "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp"]
E141_FILES = ["e141_common.py", "run_e141.py", "block_e141.sh", "queue_e141.sh", "session_e141.sh", "check_e141.py",
              "preflight_e141.sh", "smoke_gate_e141.py", "reduce_e141.py"]
BOX_BINARIES = {   # read on aifoundry3 (~/aifoundry) at 21:13 PST, Mon 2 Nov 2026: the binaries E140 (its setup) and E147 ran on this card today
    "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
}
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
    pred = json.load(open(os.path.join(ROOT, P5, "predictions-blind5-aifoundry3.json")))
    m7 = json.load(open(os.path.join(ROOT, Q, "m7.json")))
    loko = json.load(open(os.path.join(ROOT, Q, "loko-m7.json")))
    spec = {t["name"]: t for t in json.load(open(os.path.join(ROOT, P5, "blind5.json")))["tiles"]}
    tiles = {}
    for name, t in sorted(pred["tiles"].items()):
        s = spec[name]
        row = {"type": t["type"], "priority": int(t["priority"]), "pool_anchor": bool(s.get("anchor")), "case": t["case"],
               "sha256": t["sha256"], "sha256_matches_manifest": t["sha256_matches_manifest"]}
        for m in ("M7", "M6", "M5"):
            x = t[m]
            row[m] = {"D_w": x["D_w"], "D_95": x["D_95"], "S_w": x["S_w"], "dT_win_c": x["dT_win_c"], "dT_win_95": x["dT_win_95"],
                      "D600_a3_footing_w": x["D600_a3_footing_w"]}
        tiles[name] = row
    assert len(tiles) == 36 and all(tiles[n]["sha256_matches_manifest"] for n in tiles)
    # power reference: M7's nested leave-one-kind-out errors of every aifoundry3 power row (card a3) of each format (both cards: an arm)
    ref, ref_both, ref_m6, ref_m5 = {}, {}, {}, {}
    for fam in ("float", "int8"):
        for r in loko["families"][fam]["row_errors"]:
            ty = r["type"]
            ref_both.setdefault(ty, []).append(r["M7_nested_err_w"])
            if r["card"] == "a3":
                ref.setdefault(ty, []).append(r["M7_nested_err_w"])
                ref_m6.setdefault(ty, []).append(r["M6_frozen_err_w"])
                ref_m5.setdefault(ty, []).append(r["M5_frozen_err_w"])
    pools = m7["heat"]["interval_pool_by_format_card_c"]
    heat_rms = {f: pools[f"{f}|aifoundry3"]["rms_c"] for f in FORMATS}
    rng = random.Random("E141|heat-reference")
    heat_ref = {f: [rng.gauss(0.0, heat_rms[f]) for _ in range(2000)] for f in FORMATS}
    p1 = {f: sorted(n for n, r in tiles.items() if r["type"] == f and r["priority"] == 1) for f in FORMATS}
    scored = sorted(n for n, r in tiles.items() if not r["pool_anchor"])
    harness = {
        "card_code_unchanged_sha256": {rel: sha(rel) for rel in CARD_CODE},
        "e141_card_files_sha256": {f"tools/claims-v3/e141/{f}": sha(f"tools/claims-v3/e141/{f}") for f in E141_FILES},
        "pool_sha256": dict({f"{P5}/blind5.json": SOURCES[f"{P5}/blind5.json"], f"{P5}/SHA256SUMS": SOURCES[f"{P5}/SHA256SUMS"],
                             f"{P5}/predictions-blind5-aifoundry3.json": SOURCES[f"{P5}/predictions-blind5-aifoundry3.json"]},
                            **{os.path.relpath(p, ROOT): hashlib.sha256(open(p, "rb").read()).hexdigest()
                               for p in sorted(glob.glob(os.path.join(ROOT, P5, "tiles", "*", "*.bin")))}),
        "box_binaries_sha256": BOX_BINARIES,
    }
    assert len([k for k in harness["pool_sha256"] if k.endswith(".bin")]) == 36
    reg = {
        "experiment": "E141",
        "date": "2026-11-02",
        "request": "Q138 (the owner, Mon 2 Nov 2026, ~18:40 PST: settle the power model's open questions; goal: predict power and heat "
                   "as accurately as possible); kinds page section 11 item 6 (#11-what-is-still-open)",
        "card": "aifoundry3 card 0 (no V3_DEVICE), 600 MHz as its boot-time TDP of 0 latches it, TDP 0 W and threshold 65 C as read, never set",
        "frozen_inputs": {"sha256": SOURCES, "commits": {"pool_and_predictions": "dac39d97eca93e41bff28bdf3dbc4fa2550d11f2",
                                                          "m7": "3a210f2bef4356d97c7b55c4ba40e2620a11dc3a"},
                          "band_rule_note": "Q138(m) README section 3: k 3.179 floats / 2.483 int8 times sqrt(pool^2 + s^2 x'Cx); heat "
                                            "k_h 1.95 x pool_h; the band_rule string in the predictions file is run 1's wording"},
        "plan": {
            "passes": [14110, 14111, 14112, 14113, 14114], "smoke": 14101, "stoptest": 14102,
            "smoke_items": ["anchor_pi", "fp32.zeros", "fp32.randn", "fp32.wideexp48_dense", "fp32.anchor_zeros",
                            "fp16.pair_cancel_asign", "fp16.zeros", "int8.b_line_flipflop_nogate", "int8.zeros"],
            "runs_per_pass": 56, "burn_in_runs": 2, "min_kept_passes_scored": 2, "min_tile_passes": 2,
            "order": "Random('E141|aifoundry3|<pass>'): the 36 tiles dealt into three segments of 12, each with E78's six anchors, "
                     "reshuffled; the tie first and last (E140's order with 36 tiles)",
            "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz",
            "budget_s_from_session_start": 3000, "reserve_s": 60, "card_minutes_max": 50, "first_pass_estimate_s": 620, "gap_s": 10,
            "deadline": "2026-11-02 23:40 PST (no session starts after 23:00 PST; every run ends by 23:50 PST)",
            "stops": {"board_w": 65.0, "die_shire0_c": 70.0, "run_e78_max_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "how": "E140's values on this card (board 65 W, die 70 C); the newest line of the running sampler's file "
                             "(telemetry.jsonl.raw), read by the main path before every launch and every 0.1 s while it waits (E145's "
                             "guard) and by the in-run watcher every 0.1 s for the whole pass (E141's); the die stop reads "
                             "temp_c.minshire[0] (aifoundry3's minshire[2] is a constant 87 C latch)"},
            "reduction": {"primary": "reduce_e141.py (E78's reduce_e78.py unchanged: leakage auto, dips kept, E78's run and pass "
                                     "gates and its aifoundry3 config gate: E140's primary on this card)",
                          "arms": ["dips removed (E82 A2; reported, never the verdict)", "leak 0.1994", "leak 0.3803", "leak 0",
                                   "pass gates opened"]},
            "bootstrap": {"draws": 20000, "seed": 14100},
        },
        "harness": harness,
        "model": {"name": "M7 (Q138(m), 3a210f2b), scored; M6 and M5 frozen beside it",
                  "units": "D: W over the type's own zeros at 600 MHz on aifoundry3 card 0 (M7's own footing, no card scale); dT: C "
                           "over the run's launch reading over the kinds run (4.5 s)",
                  "heat_coef_a3": {"S": m7["heat"]["coef"]["S|aifoundry3"], "ST": m7["heat"]["coef"]["ST|aifoundry3"]},
                  "heat_pool_a3_rms_c": heat_rms,
                  "power_pool_a3_rms_w": {f: loko["families"]["float" if f != "int8" else "int8"]["band_calibration"]["pools"]
                                          [f"{f}|a3"]["rms_w"] for f in FORMATS}},
        "tiles": tiles,
        "reference_errors": {"power_a3": ref, "power_both_cards": ref_both, "power_a3_M6_frozen": ref_m6,
                             "power_a3_M5_frozen": ref_m5, "heat_normal_a3": heat_ref,
                             "n": {f: len(ref[f]) for f in ref}},
        "sets": {"priority1_by_format": p1, "coverage_tiles": scored},
        "rules": {
            "E141-P1": "power fp32: rms(D - M7) over the 9 priority-1 fp32 tiles (at least 5) against the 2.5-97.5% range of the rms of "
                       "as many draws with replacement from M7's nested errors of every aifoundry3 fp32 row (card a3): PASS at or below the 97.5% point, "
                       "FAIL above; below the 2.5% point is reported as better than the nested score says",
            "E141-P2": "power fp16: as P1, the 8 priority-1 fp16 tiles (at least 5), aifoundry3 fp16 rows",
            "E141-P3": "power int8: as P1, the 7 priority-1 int8 tiles (at least 4), aifoundry3 int8 rows",
            "E141-B1": "bias, floats: mean(D - M7) over the 17 priority-1 float tiles against the 2.5-97.5% range of the mean of as many "
                       "draws (same format mix) from the same nested errors: PASS inside, FAIL outside (named HIGH when M7 predicts too much, "
                       "LOW when too little)",
            "E141-B2": "bias, int8: as B1, the 7 priority-1 int8 tiles",
            "E141-C1": f"coverage, power: tiles inside M7's frozen 95% band among the 30 non-anchor tiles; PASS if at least the 2.5% point "
                       f"of Binomial(n, 0.95) ({binom_low(30)} of 30), FAIL if fewer; NOT SCORED under 10 tiles",
            "E141-M1": "M7 against M6: d = rms(M7 errors) - rms(M6 errors) over the 24 priority-1 tiles, 95% interval by a bootstrap over "
                       "tiles: BETTER if the upper bound < 0, WORSE if the lower bound > 0, else NOT RESOLVED",
            "E141-M2": "M7 against M5: as M1",
            "E141-H1": "heat fp32: rms(dT_win - M7) over the 9 priority-1 fp32 tiles (at least 5) against the 2.5-97.5% range of the rms of "
                       "as many draws from a deterministic normal sample of 2,000 points with M7's nested aifoundry3 heat rms for fp32 "
                       f"(m7.json heat.interval_pool_by_format_card_c, {heat_rms['fp32']:.3f} C): PASS at or below the 97.5% point, FAIL above",
            "E141-H2": f"heat fp16: as H1 ({heat_rms['fp16']:.3f} C)",
            "E141-H3": f"heat int8: as H1, 7 tiles, at least 4 ({heat_rms['int8']:.3f} C)",
            "E141-H4": f"coverage, heat: as C1, M7's frozen dT band ({binom_low(30)} of 30)",
            "min_passes": "fewer than 2 kept passes on the primary: every rule NOT SCORED; a tile with fewer than 2 kept passes is left out",
        },
        "reported_not_verdicts": [
            "every rule on the dips-removed arm (E82 A2's definition; reported, never the verdict)",
            "M6's and M5's rms, bias and coverage beside M7's on every set", "every rule at every reduction arm (leakage 0.1994, 0.3803, 0; "
            "dips removed; pass gates opened)", "the per-format bias of each model",
            "the priority-2 tests and the pool's six anchors (footing: the pool's zeros tiles against E78's built-in zeros, the pool's "
            "random tiles against M7)",
            "heat at the measured run length: M7's H2 with its ST term at each tile's median T_run (dT + ST x S_M7 x (T_run - 4.5), ST "
            "-0.0490 C/W/s on aifoundry3)",
            "the reference on both cards' rows (an arm of P1-P3)", "the session tie and E78's anchors against E140's on this card",
            "errors by case", "the die rise per board W against M7's 0.1186 C/W on aifoundry3",
            "E141's reduction is handed to E141 for its card-term rules X1/X2 (E141's registration)"],
        "expected": "P1-P3 PASS; B1 PASS or FAIL HIGH (M7 still over-predicted pool 4's floats by 0.22 W out of kind, Q138(m) section 1); "
                    "B2 PASS; C1 PASS (rule B's wider bands); M1 and M2 NOT RESOLVED (the models differ by at most 0.6 W on this pool); "
                    "H1-H4 PASS. Likeliest misses named now: the wide-exponent gate tiles (fp32.wideexp48_bgate_alt, "
                    "fp32.wideexp48_bgate_kblk, fp16.wideexp_bgate_alt; M6's and M7's steady-gate over-prediction), the fp16 pairs that "
                    "cancel (fp16.pair_cancel_asign, fp16.pair_nearcancel), int8's whole-line flip-flops (int8.b_line_flipflop_nogate, "
                    "int8.b_line_zero_one), and on heat the small int8 rises the die's whole-degree readings floor.",
        "binomial_low_2p5": {"30": binom_low(30), "36": binom_low(36), "24": binom_low(24)},
    }
    out = os.path.join(HERE, "predictions-e141.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    print(f"wrote {out}: {len(tiles)} tiles; reference rows aifoundry3 {reg['reference_errors']['n']}; heat pools {heat_rms}; "
          f"binomial low end 30 -> {binom_low(30)}")


if __name__ == "__main__":
    main()
