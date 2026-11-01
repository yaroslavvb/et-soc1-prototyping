#!/usr/bin/env python3
"""E86 (Q130): write predictions-e86.json, the freeze - every number copied from its committed source, never retyped.

    python3 tools/claims-v3/kinds/make_predictions_e86.py [--out tools/claims-v3/kinds/predictions-e86.json]

Sources, each checked by sha256 before anything is copied (it refuses on any difference):
  Q130(n)'s frozen points   tools/claims-v3/kinds/real/predictions-real.json  bab33bee... (7d5b99af)
  Q130(n)'s Amendment 1     tools/claims-v3/kinds/real/amendment-1.json       f32e8a90... (99620cc2)
  the real tiles            tools/claims-v3/kinds/real/real.json              eb36f4cd... (7d5b99af)
  E78's reduction           docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json  b7463b6c... (410c56f6)
  E78's freeze              tools/claims-v3/kinds/predictions-e78.json        83d504bb... (cfd94285): E78-R2's bounds
It also records the sha256 of E78's code that E86 runs unchanged or ports, and of E86's own files.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
SRC = {
    "predictions_real": (f"{K}/real/predictions-real.json",
                         "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941", "7d5b99af"),
    "amendment_1": (f"{K}/real/amendment-1.json",
                    "f32e8a9087a9cf3bf60f29ff623c1a375537b43696df0dca24972ba220bc0d9e", "99620cc2"),
    "real_json": (f"{K}/real/real.json", "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0", "7d5b99af"),
    "e78_reduction": ("docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json",
                      "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5", "410c56f6"),
    "predictions_e78": (f"{K}/predictions-e78.json",
                        "83d504bbde46917dd11e87af2dc1e06b4e3f4144a624fe9f2ef21ec4cda248fe", "cfd94285"),
}
REUSED = ["tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json"]
REUSED_WANT = {   # E78's freeze values (E78's logs/box-harness.sha256, E82.md's table)
    "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
    f"{K}/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
    f"{K}/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
    f"{K}/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
    f"{K}/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
PORTED = {f"{K}/block_e78.sh": "e6b39c2c4cfcd3eab7298d026e0d24b2fc84bbd688e218c111646d7298abfb3d",
          f"{K}/queue_e78.sh": "0232c08c2ec204091c30c5c6a77991fddea7412cbe7a0928b5a427c62cc35a56",
          f"{K}/run_e78.sh": "b3e9480e7579760724f4f4493b50198ad09a37656bb4e21c00e69ab9afcb51fe",
          f"{K}/collect_e78.sh": "5d7da297e5204a08df83e716550c4f31a1f135ef04bf02b91207370d46c2000f"}
E86_FILES = [f"{K}/{f}" for f in ("e86_common.py", "run_e86.py", "block_e86.sh", "queue_e86.sh", "run_e86.sh",
                                  "reduce_e86.py", "score_e86.py", "collect_e86.sh", "selftest_e86.py")]
TYPES = ("fp32", "fp16", "int8")
MATRICES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
COMPARE = {"fp32": "fp32.nn_like", "fp16": "fp16.nn_like", "int8": "int8.gauss_q"}
TIE_BAND_W = {"fp32": 0.50, "fp16": 0.50, "int8": 0.25}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions-e86.json"))
    a = ap.parse_args()
    for key, (rel, want, _) in SRC.items():
        have = sha(rel)
        if have != want:
            raise SystemExit(f"{key}: {rel} sha256 {have} != {want}")
    for rel, want in {**REUSED_WANT, **PORTED}.items():
        have = sha(rel)
        if have != want:
            raise SystemExit(f"{rel} sha256 {have} != E78's freeze {want}")
    pr = json.load(open(os.path.join(ROOT, SRC["predictions_real"][0])))
    am = json.load(open(os.path.join(ROOT, SRC["amendment_1"][0])))
    rj = json.load(open(os.path.join(ROOT, SRC["real_json"][0])))
    e78 = json.load(open(os.path.join(ROOT, SRC["e78_reduction"][0])))
    p78 = json.load(open(os.path.join(ROOT, SRC["predictions_e78"][0])))
    tiles = {}
    for ty in TYPES:
        cmp_d = e78["items"][COMPARE[ty]]["D"]["mean"]
        for m in MATRICES:
            key = f"{ty}/{m}"
            p, q, t = pr["tiles"][key], am["tiles"][key], rj["tiles"][ty][m]
            assert p["tile_sha256"] == t["sha256"], key
            pa, qa, lw = p["a_aifoundry3_600mhz"], q["a_aifoundry3_600mhz"], q["like_with_like"]
            ref_d = lw["ref_measured_w"]
            tiles[f"{ty}.real_{m}"] = {
                "type": ty, "matrix": m, "what": t["what"], "file": f"{K}/real/{t['file']}",
                "sha256": t["sha256"], "sha256_a": t["sha256_a"], "sha256_b": t["sha256_b"],
                "gated_lane_frac": t["stats"]["gated_lane_frac"], "bus_bits_per_op": t["stats"]["bus_bits_per_op"],
                "D_frozen_w": pa["D_w"], "D_frozen_pi95_w": pa["D_pi95_w"],
                "D_scoring_interval_w": qa["scoring_interval_w"], "scoring_halfwidth_w": qa["scoring_halfwidth_w"],
                "ref": REF[ty], "ref_e78_D_w": ref_d,
                "ratio_scoring_interval": [round(qa["scoring_interval_w"][0] / ref_d, 5),
                                           round(qa["scoring_interval_w"][1] / ref_d, 5)],
                "ratio_frozen_interval": [round(pa["D_pi95_w"][0] / ref_d, 5), round(pa["D_pi95_w"][1] / ref_d, 5)],
                "ratio_predicted_anchored": lw["ratio_to_ref_measured"],
                "compare": COMPARE[ty], "compare_e78_D_w": round(cmp_d, 4),
                "order_vs_ref_predicted": "below",
                "order_vs_compare_predicted": "below" if pa["D_w"] < cmp_d else "above",
                "provisional": ty == "int8",
            }
    e78ref = {}
    for nm in list(REF.values()) + list(COMPARE.values()) + ["anchor_pi"]:
        it = e78["items"][nm]
        ty = it["type"]
        e78ref[nm] = {"D_w": round(it["D"]["mean"], 4), "ci95_w": round(it["D"]["ci95"], 4), "n": it["D"]["n"],
                      "band_w": TIE_BAND_W[ty], "S_w": round(it["S"]["mean"], 4)}
    reg = {
        "experiment": "E86",
        "title": "the real tensors' energy: Q130(n)'s nine real GPT-2 tiles beside E78's anchors and comparison kinds, "
                 "aifoundry3 card 0, 600 MHz",
        "request": "Q130 evening round (workflow q130-evening, lane a3-e86-real-energy), Sat 31 Oct 2026",
        "date": "2026-10-31",
        "registration": f"{K}/E86.md",
        "card": {"host": "aifoundry3", "card": 0, "clock_mhz": 600, "minion_mv_approx": 522,
                 "config_gate": {"tdp_w": 0, "temp_threshold_c": 65}, "writes": "nothing (no governor, TDP, "
                 "threshold or clock set; no reset; no --reset-ms)"},
        "inputs_frozen": {k: {"path": v[0], "sha256": v[1], "commit": v[2]} for k, v in SRC.items()},
        "harness": {
            "reused_unchanged_sha256": {r: sha(r) for r in REUSED},
            "ported_from_sha256": PORTED,
            "e86_files_sha256": {r: sha(r) for r in E86_FILES},
            "binary": "build/sparsity/host/sparsity_host in the aifoundry3 tree E67/E70/E78/E79 ran from (~/aifoundry)",
            "data_dir": "docs/reports/data/2026-10-31-e86-real-tensors-energy/",
            "raw_data_on_box": "build/claims-v3/aifoundry3/kinds/p86<nn>/ and kinds-smoke/p8601/",
        },
        "plan": {
            "passes_planned": [8610, 8611, 8612, 8613, 8614, 8615], "passes_min": 4, "smoke": 8601,
            "runs_per_pass": 32,
            "pass": "the tie (anchor_pi), three segments of E78's six anchors and four of the twelve E86 items, the tie; "
                    "the twelve shuffled by Random('E86|aifoundry3|<pass>') and dealt round-robin (e86_common.pass_order)",
            "anchors_three_per_pass": ["fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"],
            "once_per_pass": sorted(tiles) + sorted(COMPARE.values()),
            "run": "sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff "
                   "--per-shire 32 --seconds 4; E78's launch reading (heat to 59 C, launch at 58 C after 2.0 s quiet)",
        },
        "card_budget": {"max_card_min": 40, "queue_budget_min": 36, "first_pass_estimate_s": 390,
                        "deadline_local": "22:25", "no_new_session_after": "21:45 PDT", "runs_end_by": "22:30 PDT"},
        "analysis": {
            "reduction": "reduce_e78.py unchanged (via reduce_e86.py): D = p80 - Zhat_type(t0), the type's own zeros "
                         "interpolated in time; one value per (pass, item); the pass the unit of replication",
            "leak_primary": "auto (E78's registered estimator, on E86's own runs)",
            "leak_arms": [0.1994, 0.3803, 0.0],
            "leak_arms_why": "0.1994 W/C is E78's primary slope value, at which Q130(n) states its D (amendment-1.json "
                             "D_scope); 0.3803 (E71) and 0 are E78's registered arms",
            "min_kept_passes": 4, "min_passes_per_quantity": 3,
        },
        "tiles": tiles,
        "e78_reference": e78ref,
        "rules": {
            "E86-R1": {"name": "Amendment 1's intervals",
                       "what": "each real tile's D (mean over kept passes) inside its scoring interval "
                               "(tiles.<name>.D_scoring_interval_w)",
                       "pass_if": "at least 7 of the 9 inside; fewer: FAIL",
                       "min_resolved": 8,
                       "beside": "the count inside the frozen intervals (D_frozen_pi95_w); the count whose own 95% "
                                 "interval overlaps the scoring interval; every arm"},
            "E86-R2": {"name": "accuracy per format",
                       "what": "rms over a format's three tiles of (D - D_frozen_w)",
                       "bound_w": p78["rules"]["E78-R2"]["bound_w"],
                       "pass_if": "rms <= bound in each format separately (E78-R2's bounds, copied)",
                       "beside": "mean error per format; the nested-LOO rms Amendment 1 expects",
                       "nested_loo_rms_w": {ty: am["nested_loo"][ty]["nested_loo_rms_w"] for ty in TYPES}},
            "E86-R3": {"name": "real against random, the predicted direction",
                       "what": "per pass, per format, rho = mean over the three real tiles of D(real)/D(ref) (ref = "
                               "randn fp32/fp16, full int8, the pass's mean of its three runs); over passes the mean and "
                               "its 95% interval t(0.975, n-1) x SE",
                       "threshold": {"fp32": 1.0, "fp16": 1.0, "int8": 0.9},
                       "verdict": "per format PASS if the upper bound < threshold, FAIL if the lower bound > threshold, "
                                  "else INCONCLUSIVE; the rule passes only if all three formats pass",
                       "beside": "per tile the paired difference D(real) - D(ref), three-way at 95%"},
            "E86-R4": {"name": "real against nn_like / gauss_q, the predicted order",
                       "what": "per tile, paired per pass: D(real) - D(compare) (compare = nn_like fp32/fp16, gauss_q "
                               "int8); predicted side from Q130(n)'s frozen point against E78's measured compare "
                               "(tiles.<name>.order_vs_compare_predicted)",
                       "verdict": "per tile PASS if the 95% interval lies on the predicted side of 0, FAIL if on the "
                                  "other, else INCONCLUSIVE; per format PASS if its three tiles pass, FAIL if any "
                                  "fails; the rule passes only if all three formats pass"},
            "E86-R5": {"name": "the session tie",
                       "what": "D of each e78_reference cell (fp32/fp16 randn, int8 full, fp32/fp16 nn_like, int8 "
                               "gauss_q, anchor_pi) within band_w of E78's",
                       "pass_if": "all seven inside their bands",
                       "meaning": "a failure means the session moved, not that a model did; S1 is then the reading"},
            "E86-S1": {"name": "like with like",
                       "what": "per tile, the per-pass ratio D(real)/D(ref), averaged over passes, inside "
                               "tiles.<name>.ratio_scoring_interval (the scoring interval over E78's D(ref))",
                       "pass_if": "at least 7 of the 9 inside", "min_resolved": 8,
                       "beside": "the frozen ratio interval; the anchored D = ratio x E78's D(ref)"},
            "E86-C": {"name": "checks, reported, never a verdict",
                      "what": "E78-R5's: idle consistency median |S - S0 - D| <= 0.15 W; rail lag re-fit median in "
                              "[0.80, 1.15] s; duty in [0.990, 1.000]; carry-over |beta| <= 0.01 W/W or < 3 SE; the "
                              "dumped tiles equal their registered sha256 (a run gate)"},
        },
        "not_scored_if": "fewer than 4 kept passes: every rule NOT SCORED; a quantity with fewer than 3 kept passes "
                         "is unresolved and never counts as inside or PASS",
    }
    json.dump(reg, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}: {len(tiles)} tiles, sha256 {hashlib.sha256(open(a.out, 'rb').read()).hexdigest()}")


if __name__ == "__main__":
    main()
