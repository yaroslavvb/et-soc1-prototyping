#!/usr/bin/env python3
"""E157 (Q139): write predictions-e157.json, the freeze, before the claim of aifoundry1 card 1 and the first launch. Standard library only.

E157 adds no prediction. Every model number is copied from Q139(x)'s committed card-1 predictions
(tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry1c1.json, d98d2e34, made by Q139(m)'s predict_blind6.py at 122da8b6 with nothing
refitted); the card scale predicted from cheap reads from Q139(x)'s card-scale-blind6.json; the power reference errors are M8's nested
leave-one-kind-out errors of every card-1 row (M8's per-row nested errors are not committed, so ref_errors_e157.py recomputes them with
Q139(m)'s own fit_m8.run_family, unchanged, into ref-errors-m8.json, and every pool's rms and n equal nested-m8.json's to 1e-9 W: E142's
form, which took M7's card-1 rows from loko-m7.json); the heat reference is a deterministic normal sample with M8's carried card-1 heat rms
(m8.json > heat, M7's law carried; E142's form); K1's reference values from E142's committed reductions of pool 5 on this card (e142.json,
its own footing, and Q139(u)'s re-reduction e142-footing.json). Each source's sha256 is checked against the value written here and
recorded. The plan, the stops, the rules, the precision of each rule before the data and the harness hashes (every file the box runs, the
pools, the binaries) are written here too.

    python3 tools/claims-v3/e157/make_predictions_e157.py            # writes predictions-e157.json beside it
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
P6 = "tools/claims-v3/kinds/blind6"
P5 = "tools/claims-v3/kinds/blind5"
QM = "docs/reports/data/2026-11-03-q139m-model"
QU = "docs/reports/data/2026-11-03-q139u-footing"
E142D = "docs/reports/data/2026-11-02-e142-blind5-card1"
SOURCES = {   # the frozen inputs and the sha256 each must have (Q139(x)'s result, Q139(m)'s and Q139(u)'s commits, E142's data)
    f"{P6}/predictions-blind6-aifoundry1c1.json": "267565abe1b06466ea44ed123755c16ad6d091fb20f26fd710853526912c3276",
    f"{P6}/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    f"{P6}/MANIFEST": "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0",
    f"{P6}/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
    f"{P6}/card-scale-blind6.json": "6b04079139e05d168517779fbc97c6c9a720c69226585ee6c5e67d6857ff9312",
    f"{P5}/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    f"{P5}/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
    f"{QM}/m8.json": "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
    f"{QM}/nested-m8.json": "f284b5407a98641ec33a57410be925a4c64199e0033b6c94ef893702de0f4905",
    f"{QU}/footing.json": "f589efaad1fc9b19390658f16a5ffd4ca71e23cde59fbcf2f5cc88c267a73a97",
    f"{QU}/reduced/e142-footing.json": "d117d83bb67cbabe19cdad07b165f790b738977ffc328f3f73a9d78137e294fc",
    f"{E142D}/e142.json": "f997632825d50d3e03a2b4c0a4322ba1cb0314cc16cc8f02516486e630adb5aa",
    "tools/claims-v3/ccheck/pick6.py": "b4b92dc14001609f4d4a9528ec7f3eafc23f9a7ae59d6962c240b119d1a327e6",
    "tools/claims-v3/ccheck/ccheck.py": "2f806fe6080baeea33558ddd49fded16f2ebcb8c02f494217dfd32cc033c0a22",
    "tools/claims-v3/e157/ref-errors-m8.json": "ba713adc00ee8d3967f1330a5351e0676c00de378ce6a1f694f16cc2a90c7d9d",
}
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
             "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp",
             "tools/claims-v3/ccheck/sparsity_ccheck.sh", "tools/claims-v3/ccheck/patch_host_ccheck.py",
             "tools/claims-v3/ccheck/build_host_ccheck.sh", "tools/claims-v3/ccheck/ccheck.py", "tools/claims-v3/ccheck/pick6.py",
             "rtl-sim/fma_toggle_v2/accum.c"]
E157_FILES = ["e157_common.py", "run_e157.py", "block_e157.sh", "queue_e157.sh", "session_e157.sh", "check_e157.py",
              "preflight_e157.sh", "smoke_gate_e157.py", "reduce_e157.py"]
BOX_BINARIES = {   # read on aifoundry1 at 06:37 PST, Tue 3 Nov 2026 (no device opened): the binaries E142 and E156 ran on this card, the
                   # kernel the power passes load, and Q139(k)'s patched host, built there at 06:37 by build_host_ccheck.sh
    "build/sparsity/host/sparsity_host": "e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe",
    "build/ettelem/ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",
    "build/sparsity/kernel/sparsity.elf": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    "build/ccheck/b/host/sparsity_host": "4f0956ceabb107337c2996636ad712946aa135ecf33f72fb833bae72c8c5e585",
}
PATCHED_MAIN_SHA256 = "5bd029ca1bc0a3f63573015d400b9e7b2d8c2e84de12a722f58bc84057edf79f"   # build/ccheck/src/host/main.cpp on the box
FORMATS = ("fp32", "fp16", "int8")
K1 = ("fp32.b_exp_busy_a_const", "fp32.real_pythia_ln1_q", "fp16.sparse24_aligned", "fp16.exp_only", "int8.gray_a",
      "int8.b_line_zero_one")
M8_CARD_TERM = 0.9615998850616304       # m8.json: C0_M5_E78E82_family, floats and int8 (card-scale-blind6.json scale_applied_by_model)


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def binom_low(n, p=0.95, alpha=0.025):
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def interval(ref, mix, draws, seed, stat):
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        xs = []
        for t, k in sorted(mix.items()):
            e = ref[t]
            xs += [e[rng.randrange(len(e))] for _ in range(k)]
        vals.append(math.sqrt(sum(x * x for x in xs) / len(xs)) if stat == "rms" else sum(xs) / len(xs))
    vals.sort()
    return [round(vals[int(0.025 * draws)], 4), round(vals[int(0.5 * draws)], 4), round(vals[int(0.975 * draws) - 1], 4)]


def welch_half(se, n):
    """The half-width a same-card repeat with the old session's se and passes would get (pick6.py's repeat_band_W)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("pick6", os.path.join(ROOT, "tools/claims-v3/ccheck/pick6.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.welch(0.0, se, n, 0.0, se, n)["half_width_W"]


def main():
    for rel, want in SOURCES.items():
        have = sha(rel)
        if have != want:
            raise SystemExit(f"{rel}: sha256 {have} != the committed {want}")
    pred = json.load(open(os.path.join(ROOT, P6, "predictions-blind6-aifoundry1c1.json")))
    spec = {t["name"]: t for t in json.load(open(os.path.join(ROOT, P6, "blind6.json")))["tiles"]}
    spec5 = {t["name"]: t for t in json.load(open(os.path.join(ROOT, P5, "blind5.json")))["tiles"]}
    m8 = json.load(open(os.path.join(ROOT, QM, "m8.json")))
    nested = json.load(open(os.path.join(ROOT, QM, "nested-m8.json")))
    cs = json.load(open(os.path.join(ROOT, P6, "card-scale-blind6.json")))
    e142 = json.load(open(os.path.join(ROOT, E142D, "e142.json")))
    e142u = json.load(open(os.path.join(ROOT, QU, "reduced", "e142-footing.json")))
    footing = json.load(open(os.path.join(ROOT, QU, "footing.json")))
    tiles = {}
    for name, t in sorted(pred["tiles"].items()):
        s = spec[name]
        row = {"type": t["type"], "priority": int(t["priority"]), "pool_anchor": bool(s.get("anchor")), "case": t["case"],
               "hold_candidate": bool(s.get("hold_candidate")), "sha256": t["sha256"],
               "sha256_matches_manifest": t["sha256_matches_manifest"]}
        for m in ("M8", "M7", "M6"):
            x = t[m]
            row[m] = {"D_w": x["D_w"], "D_95": x["D_95"], "S_w": x["S_w"], "dT_win_c": x["dT_win_c"], "dT_win_95": x["dT_win_95"],
                      "D600_a3_footing_w": x["D600_a3_footing_w"]}
        tiles[name] = row
    assert len(tiles) == 50 and all(tiles[n]["sha256_matches_manifest"] for n in tiles)
    assert all(tiles[n]["sha256"] == spec[n]["sha256"]["whole"] for n in tiles)
    k1 = {}
    for n in K1:
        k1[n] = {"type": spec5[n]["type"], "case": spec5[n]["case"], "sha256": spec5[n]["sha256"]["whole"],
                 "E142_registered_footing": {q: e142["items"][n][q] for q in ("D", "S", "dT_win")},
                 "E142_q139u_footing": {q: e142u["items"][n][q] for q in ("D", "S", "dT_win")},
                 "repeat_band_W_E142_footing": welch_half(e142["items"][n]["D"]["se"], e142["items"][n]["D"]["n"]),
                 "repeat_band_W_q139u_footing": welch_half(e142u["items"][n]["D"]["se"], e142u["items"][n]["D"]["n"])}
    # power reference: M8's nested card-1 rms per format (nested-m8.json > families.*.band.pools, the band's own pools)
    pools = {**nested["families"]["float"]["band"]["pools"], **nested["families"]["int8"]["band"]["pools"]}
    p_rms = {f: pools[f"{f}|c1"]["rms_w"] for f in FORMATS}
    p_n = {f: pools[f"{f}|c1"]["n"] for f in FORMATS}
    hp = m8["heat"]["interval_pool_by_format_card_c"]
    h_rms = {f: hp[f"{f}|aifoundry1-c1"]["rms_c"] for f in FORMATS}
    rer = json.load(open(os.path.join(HERE, "ref-errors-m8.json")))
    p_ref = {f: rer["card1_by_format"][f] for f in FORMATS}
    p_ref_both = {f: rer["both_cards_by_format"][f] for f in FORMATS}
    assert all(len(p_ref[f]) == p_n[f] for f in FORMATS)
    assert all(abs(math.sqrt(sum(x * x for x in p_ref[f]) / len(p_ref[f])) - p_rms[f]) < 1e-9 for f in FORMATS)
    rng = random.Random("E157|heat-reference")
    h_ref = {f: [rng.gauss(0.0, h_rms[f]) for _ in range(2000)] for f in FORMATS}
    p1 = {f: sorted(n for n, r in tiles.items() if r["type"] == f and r["priority"] == 1) for f in FORMATS}
    p1_all = sorted(n for f in FORMATS for n in p1[f])
    nonanchor = sorted(n for n, r in tiles.items() if not r["pool_anchor"])
    real = sorted(n for n in nonanchor if ".real_" in n)
    assert len(real) == 12 and sum(tiles[n]["priority"] == 1 for n in real) == 9
    min_tiles = {"fp32": 6, "fp16": 4, "int8": 6, "floats": 8, "real": 8}      # E153's minimums
    bs = {"draws": 20000, "seed": 15700}
    precision = {}
    for rid, f in (("E157-P1", "fp32"), ("E157-P2", "fp16"), ("E157-P3", "int8")):
        precision[rid] = {"tiles": len(p1[f]), "rms_interval_W": interval(p_ref, {f: len(p1[f])}, 4000, 1, "rms")}
    precision["E157-B1"] = {"tiles": len(p1["fp32"]) + len(p1["fp16"]),
                            "mean_interval_W": interval(p_ref, {"fp32": len(p1["fp32"]), "fp16": len(p1["fp16"])}, 4000, 2, "mean")}
    precision["E157-B2"] = {"tiles": len(p1["int8"]), "mean_interval_W": interval(p_ref, {"int8": len(p1["int8"])}, 4000, 3, "mean")}
    for rid, f in (("E157-H1", "fp32"), ("E157-H2", "fp16"), ("E157-H3", "int8")):
        precision[rid] = {"tiles": len(p1[f]), "rms_interval_C": interval(h_ref, {f: len(p1[f])}, 4000, 4, "rms")}
    precision["E157-C1"] = {"tiles": len(p1_all), "binomial_low_2p5": binom_low(len(p1_all))}
    precision["E157-H4"] = {"tiles": len(p1_all), "binomial_low_2p5": binom_low(len(p1_all))}
    precision["E157-K1D"] = {"repeat_band_W_E142_footing": {n: k1[n]["repeat_band_W_E142_footing"] for n in K1},
                             "repeat_band_W_q139u_footing": {n: k1[n]["repeat_band_W_q139u_footing"] for n in K1},
                             "note": "the Welch half-width a same-card repeat with E142's own se and passes would get; every one is "
                                     "wider than 0.05 W, so K1-D (the critic's flat 0.05 W) can fail by noise alone (Q139(k) finding 2), "
                                     "which is why K1-W is registered beside it"}
    c1s = cs["cards"]["aifoundry1c1"]
    reg_form = "zeros_level_fp32_w|physical"
    card_scale = {
        "registered_form": reg_form,
        "why_this_form": "the critic's rank 5 asks for each card's scale 'predicted from its own zeros and idle reads only'; of those two "
                         "reads the zeros level is the one whose leave-one-card-out error on card 1 was smallest in training (physical: "
                         "+1.1% floats, -0.1% int8; idle power physical +32.6% / +31.0%), chosen from m8.json's training table before any "
                         "pool-6 data exists; every other read and form, V600^2 (M8's physical candidate) among them, is reported beside",
        "floats": {"forms": c1s["floats"]["cheap_read_predicted_scale"], "reads_this_card": c1s["floats"]["reads_this_card"],
                   "train_measured_scale": c1s["floats"]["train_measured_scale"]},
        "int8": {"forms": c1s["int8"]["cheap_read_predicted_scale"], "reads_this_card": c1s["int8"]["reads_this_card"],
                 "train_measured_scale": c1s["int8"]["train_measured_scale"]},
        "formula": cs["formula"],
        "zeros_reread": {"frozen_read_card1_w": c1s["floats"]["reads_this_card"]["zeros_level_fp32_w"], "beta": 1.0,
                         "formula": "s' = s_frozen x (read' / read_frozen)^beta: the registered form with card 1's zeros level re-read "
                                    "in this session (pool 6's own fp32 zeros tile, fp32.anchor6_zeros, its S on the primary footing; "
                                    "the other two cards' frozen reads unchanged); reported, never a verdict"},
    }
    harness = {
        "card_code_unchanged_sha256": {rel: sha(rel) for rel in CARD_CODE},
        "e157_card_files_sha256": {f"tools/claims-v3/e157/{f}": sha(f"tools/claims-v3/e157/{f}") for f in E157_FILES},
        "pool_sha256": dict({f"{P6}/blind6.json": SOURCES[f"{P6}/blind6.json"], f"{P6}/MANIFEST": SOURCES[f"{P6}/MANIFEST"],
                             f"{P6}/SHA256SUMS": SOURCES[f"{P6}/SHA256SUMS"],
                             f"{P6}/predictions-blind6-aifoundry1c1.json": SOURCES[f"{P6}/predictions-blind6-aifoundry1c1.json"],
                             f"{P5}/blind5.json": SOURCES[f"{P5}/blind5.json"], f"{P5}/SHA256SUMS": SOURCES[f"{P5}/SHA256SUMS"]},
                            **{os.path.relpath(p, ROOT): hashlib.sha256(open(p, "rb").read()).hexdigest()
                               for p in sorted(glob.glob(os.path.join(ROOT, P6, "tiles", "*", "*.bin")))},
                            **{f"{P5}/{spec5[n]['file']}": sha(f"{P5}/{spec5[n]['file']}") for n in K1}),
        "box_binaries_sha256": BOX_BINARIES,
        "patched_main_cpp_sha256": PATCHED_MAIN_SHA256,
    }
    assert len([k for k in harness["pool_sha256"] if k.endswith(".bin")]) == 56
    reg = {
        "experiment": "E157",
        "date": "2026-11-03",
        "request": "Q139, resumed (the owner's mandate of Mon 2 Nov 2026, ~18:40 PST: settle the power model's open questions; goal: "
                   "predict power and heat as accurately as possible; his 'approved both aifoundry and mordast, continue' of Tue 3 Nov "
                   "~15:47 PST); kinds page section 11 item 6 (#11-what-is-still-open); Q138 final critic ranks 2, 5 and 14",
        "card": "aifoundry1 card 1 (aifoundry1-c1, V3_DEVICE=1), 600 MHz, TDP 65 W and threshold 65 C as read, never set",
        "frozen_inputs": {"sha256": SOURCES,
                          "commits": {"pool6_and_predictions": "d98d2e34e1de004bb49a8e728c19b8f7b5f5bb70 (Q139(x))",
                                      "m8": "122da8b6 (Q139(m); registration f640fb7a)",
                                      "ccheck": "60b91395, corrected 4946a992 (Q139(k))",
                                      "footing": "d4c36bfe (rule), Q139(u) data; corrections ca7dee2a",
                                      "pool5": "dac39d97 (Q138(x)); E142 registration and data on lab main"},
                          "band_rule_M8": pred["band_rule_M8"]},
        "plan": {
            "passes": [15710, 15711, 15712, 15713, 15714], "smoke": 15701, "stoptest": 15702,
            "smoke_items": ["anchor_pi", "fp32.zeros", "fp32.randn", "fp32.real_qwen_softmax_v", "fp32.anchor6_zeros",
                            "fp32.real_pythia_ln1_q", "fp16.real_smol_qk", "fp16.zeros", "int8.b_line_zero_ff", "int8.zeros"],
            "runs_per_pass": 76, "burn_in_runs": 2, "min_kept_passes_scored": 2, "min_tile_passes": 2, "min_tiles": min_tiles,
            "order": "Random('E157|aifoundry1-c1|<pass>'): pool 6's 50 tiles shuffled and dealt 13 / 19 / 18 into three segments, K1's "
                     "six pool-5 tiles join segment 0 (first in every pass), each segment with E78's six anchors, reshuffled; the tie "
                     "first and last",
            "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz",
            "c_check": "every measured launch through tools/claims-v3/ccheck/sparsity_ccheck.sh: the patched host "
                       "build/ccheck/b/host/sparsity_host --c-log <pass>/c-log.jsonl --c-poison, kernel build/sparsity/kernel/sparsity.elf "
                       "(the power passes'); the heater unchanged; checked at the desk with ccheck.py check, never on the box",
            "budget_s_from_session_start": 3300, "reserve_s": 60, "card_minutes_max": 55, "first_pass_estimate_s": 780, "gap_s": 10,
            "deadline": "2026-11-03 21:50 PST for a pass's projected end (section 23 of the round's brief: no card session starts after "
                        "21:00 PST; every run ends by 22:00 PST)",
            "stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "run_e78_max_c": 72.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "how": "the newest line of the running sampler's file, read by the main path before every launch and every 0.1 s "
                             "while it waits (E145's guard) and by the in-run watcher every 0.1 s for the whole pass (E142)"},
            "reduction": {"primary": f"reduce_e157.py --leak {footing['slopes']['c1']['k_w_per_c']!r} --no-refit (Q139(u)'s footing: card "
                                     "1's frozen slope, E82 A2's dips removed once; E78's gates; card 1's config gate)",
                          "k_w_per_c": footing["slopes"]["c1"]["k_w_per_c"],
                          "beside": "E142's own footing: reduce_e157.py --leak 0.2414 (E82's frozen slope, dips removed: the footing "
                                    "E142's session was reduced on, the frame of e142.json), every rule scored and reported beside the "
                                    "primary; K1 read on it against e142.json",
                          "arms": ["leak auto (the session's own fitted slope)", "dips kept at the primary slope",
                                   "leak 0.2955 and 0.3320 (Q139(u)'s slope interval)", "anchor gates relaxed"]},
            "bootstrap": bs,
        },
        "harness": harness,
        "model": {"name": "M8 (Q139(m), 122da8b6), scored; M7 and M6 frozen beside it",
                  "units": "D: W over the type's own zeros at 600 MHz on card 1 on Q139(u)'s footing (M8's card term 0.9616 floats and "
                           "int8); dT: C, the die reading over the window less the launch reading, over the kinds run (4.5 s)",
                  "card_term_applied": {"M8": M8_CARD_TERM, "M7_floats": 0.9711174157693975, "M7_int8": 0.9735},
                  "heat_coef_card1": {"S": m8["heat"]["coef"]["S|aifoundry1-c1"], "ST": m8["heat"]["coef"]["ST|aifoundry1-c1"]},
                  "heat_pool_card1_rms_c": h_rms,
                  "power_pool_card1_rms_w": p_rms, "power_pool_card1_n": p_n,
                  "card_scale_predicted_from_cheap_reads": card_scale},
        "tiles": tiles,
        "k1": k1,
        "reference_errors": {"power_card1": p_ref, "power_both_cards": p_ref_both, "heat_normal_card1": h_ref,
                             "n": {f: len(p_ref[f]) for f in FORMATS},
                             "note": "power: M8's nested leave-one-kind-out errors of every card-1 row (ref-errors-m8.json, fit_m8.run_family "
                                     "unchanged; pools equal nested-m8.json's to 1e-9 W); heat: a deterministic normal sample (2,000 points, "
                                     "Random('E157|heat-reference')) with M8's carried card-1 heat rms per format"},
        "sets": {"priority1_by_format": p1, "priority1_all": p1_all, "nonanchor": nonanchor, "real": real,
                 "nonreal_nonanchor": sorted(set(nonanchor) - set(real)), "k1": list(K1)},
        "precision_before_data": precision,
        "rules": {
            "E157-PC": "the C check (E153-KC's rule on this card): every measured launch of a pool-6 tile in a kept pass has a C record "
                       "(same t_start_ms and t_end_ms) that tools/claims-v3/ccheck/ccheck.py check judges PASS (bit-exact against the RTL's "
                       "arithmetic, int8 mod 2^32; ROUNDING, UNMODELLED, FAIL and an unrecorded launch count as not checked, Q139(k)'s "
                       "verdict table); PASS if every pool-6 tile's launches do, else FAIL naming them. A tile with any launch not PASS "
                       "leaves the scored set of every rule below (named); every rule is also given over all tiles, beside",
            "E157-P1": "power fp32: rms(D - M8) over the 12 priority-1 fp32 tiles (at least 6) against the 2.5-97.5% range of the rms of as "
                       "many draws with replacement from M8's nested errors of every card-1 fp32 row (ref-errors-m8.json, card c1): PASS "
                       "at or below the 97.5% point, FAIL above; below the 2.5% point is reported as better than the nested score says",
            "E157-P2": "power fp16: as P1, the 6 priority-1 fp16 tiles (at least 4), card-1 fp16 rows",
            "E157-P3": "power int8: as P1, the 12 priority-1 int8 tiles (at least 6), card-1 int8 rows",
            "E157-B1": "bias, floats (the critic's B1): mean(D - M8) over the 18 priority-1 float tiles (at least 8) against the 2.5-97.5% "
                       "range of the mean of as many draws (the same format mix) from the same nested errors: PASS inside, FAIL HIGH below "
                       "it (M8 predicts too much), FAIL LOW above it",
            "E157-B2": "bias, int8 (the critic's B2): as B1, the 12 priority-1 int8 tiles (at least 6)",
            "E157-C1": f"coverage, power (the critic's): tiles inside M8's frozen 95% band among the 30 priority-1 tiles; PASS if at least "
                       f"the 2.5% point of Binomial(n, 0.95) ({binom_low(30)} of 30), FAIL if fewer; NOT SCORED under 10",
            "E157-M1": "M8 against M6 (the critic's): d = rms(M8 errors) - rms(M6 errors) over the priority-1 tiles, 95% interval by a "
                       "paired bootstrap over tiles (5,000 draws): BETTER (the critic's 'resolved below zero') if the upper bound < 0, "
                       "WORSE if the lower bound > 0, else NOT RESOLVED; this is card 1's half of the critic's 'on both 600 MHz cards' "
                       "(E153 has aifoundry3's)",
            "E157-M2": "M8 against M7: as M1",
            "E157-H1": "heat fp32: rms(dT_win - M8's dT) over the priority-1 fp32 tiles (at least 6) against the 2.5-97.5% range of the rms "
                       "of as many draws from a deterministic normal sample of 2,000 points with M8's carried card-1 heat rms for fp32 "
                       "(m8.json heat.interval_pool_by_format_card_c): PASS at or below the 97.5% point, FAIL above",
            "E157-H2": "heat fp16: as H1 (at least 4)",
            "E157-H3": "heat int8: as H1 (at least 6)",
            "E157-H4": f"coverage, heat: as C1, M8's frozen dT band ({binom_low(30)} of 30)",
            "E157-R1": "the real-tile sub-rule (critic rank 8, over all 12 real tiles, pool 6's CORRECTIONS C9; E153-R1's form): rms(D - M8) "
                       "over the 12 real tiles (at least 8) at or below the 97.5% point of the rms of as many draws (same format mix) from "
                       "the errors of the pool's own non-real non-anchor tiles (all priorities): PASS, else FAIL",
            "E157-R2": "the real-tile sub-rule, no tile outside its band: every measured real tile inside M8's frozen 95% band: PASS, else "
                       "FAIL naming them",
            "E157-X1": "E142's card term X1 on pool 6 (scored only if E153's committed primary reduction of pool 6 on aifoundry3 exists when "
                       "this lane reduces, else NOT SCORED and handed on with the code): the median over non-anchor float tiles with D >= "
                       "5 W on both cards, in both cards' scored sets, of D(card 1) / D(aifoundry3), on each card's registered primary "
                       "(Q139(u)'s footing on both), 95% interval by a bootstrap over tiles (5,000 draws): PASS if the interval holds M8's "
                       "applied card term 0.9616, FAIL if not; M7's 0.9711 against the same interval and E153-CS1's reading (the median "
                       "within 1% of 0.9616) reported",
            "E157-X2": "the card term, int8: as X1 with tiles with D >= 1 W on both cards, against M8's 0.9616 (M7's 0.9735 reported)",
            "E157-S1": "card 1's scale predicted from its cheap reads (critic rank 5), floats: the registered form, the zeros level with the "
                       "physical exponent and the frozen reads (card-scale-blind6.json: 0.9707), against X1's measured median ratio: PASS "
                       "if |predicted / measured - 1| <= 1%, FAIL if not; NOT SCORED when X1 is; every other read and form (V600^2 0.9102 "
                       "among them) reported with its own 1% reading, and the zeros level re-read in this session reported",
            "E157-S2": "the card scale, int8: as S1 against X2's measured ratio (the zeros level, physical: 0.9610)",
            "E157-K1C": "K1, C (rank 14): every launch of K1's six pool-5 tiles in the session (the smoke's included) has its C record "
                        "(t_start_ms and t_end_ms equal) and is PASS by Q139(k)'s ccheck.py check (bit-exact, int8 mod 2^32): PASS if all, "
                        "FAIL if any is ROUNDING, UNMODELLED, FAIL or unrecorded (Q139(k): only PASS counts as checked); the critic's "
                        "literal 'every C exact or within the format's rounding' (PASS or ROUNDING) is reported beside",
            "E157-K1D": "K1, D (the critic's literal rule): |D_E157 - D_E142| <= 0.05 W on each of the six tiles, on Q139(u)'s footing on "
                        "both sides (this session's primary reduction against E142 as Q139(u) re-reduced it, e142-footing.json): PASS if all "
                        "six, else FAIL naming the tiles; fewer than 2 passes for a tile: NOT SCORED",
            "E157-K1W": "K1, D (Q139(k)'s same-card rule, registered beside K1D): per tile |D_E157 - D_E142| <= t_0.975(nu) sqrt(se_new^2 + "
                        "se_old^2) (Welch; pick6.py's welch()), the same frame as K1D: PASS if all six inside, else FAIL naming them",
            "E157-K1": "K1 = K1C AND K1D (the critic's rank-14 sub-rule as written); K1' = K1C AND K1W; both also read on E142's own "
                       "footing (the reduction at 0.2414 against e142.json), reported",
            "E157-PCa": "E78's six anchors and the tie (the frame D is measured over): every launch PASS and recorded, else FAIL naming them",
            "min_passes": "fewer than 2 kept passes on the primary: every rule but the C rules NOT SCORED; a tile with fewer than 2 kept passes "
                          "is left out and named",
        },
        "reported_not_verdicts": [
            "M7's and M6's rms, bias and coverage beside M8's on every set; every model on all 44 non-anchor tiles",
            "every rule on E142's own footing (0.2414 W/C, dips removed) and at every arm (the session's own slope, dips kept, k 0.2955 and "
            "0.3320, anchor gates relaxed) and over all tiles with the C check's exclusions put back",
            "K1 on E142's own footing against e142.json (0.05 W and Welch)",
            "the priority-2 tests, the pool's six anchors (its zeros tiles against E78's built-in zeros, its random tiles against M8), "
            "the four hold candidates, errors by case",
            "the below-zeros tile int8.a_zeros_b_lineflip against M8's -0.326 W (M7 +0.048, M6 +0.492): M8's bsat term's most direct test",
            "heat at the measured run length: H2's ST term at each tile's median T_run (dT + ST x S x (T_run - 4.5))",
            "the die rise per board W against M8's (M7's) 0.1151 C/W on card 1",
            "the C check's per-tile verdict counts in every pass and the smoke, its first-read notes (ccheck.py domain), the launch gaps "
            "with the C log",
            "card 1's cheap reads in this session (its fp32 zeros tile's S, the idle level) and the card scale they give",
            "E78's anchors and the tie against E142's on this card"],
        "expected": "P1-P3 PASS (M8's nested card-1 rms: fp32 0.198, fp16 0.170, int8 0.238 W); B1 PASS; B2 PASS or FAIL; C1 PASS; M1 and "
                    "M2 NOT RESOLVED (M8 and M6 differ by under 0.2 W on most tiles, at most 0.73 W); H1-H4 PASS; R1 PASS, R2 PASS or "
                    "FAIL on one tile; PC PASS unless a first-read tile shows the reference's limit; K1C PASS (E104 read this "
                    "arithmetic on this card); K1D FAIL by noise on at least one tile, K1W PASS; PCa PASS; X1 PASS or FAIL (pool 5's "
                    "ratio was 0.982 against M7's 0.9711), S1 and S2 FAIL by about 1% (the zeros level missed card 1's floats by +1.1% "
                    "in training), handed on if E153's reduction is not committed when this lane reduces. Likeliest misses named now: "
                    "int8.a_zeros_b_lineflip and int8.b_line_55_aa (M8's bsat discount), the whole-line int8 flip-flops "
                    "(int8.b_line_zero_ff, int8.a_word_zero_one), the zeros' transport tiles (fp32.negzero_a_b_complement, M6 0.73 W "
                    "above M8).",
        "binomial_low_2p5": {"30": binom_low(30), "44": binom_low(44), "50": binom_low(50)},
    }
    out = os.path.join(HERE, "predictions-e157.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    print(f"wrote {out}: {len(tiles)} pool-6 tiles, {len(k1)} K1 tiles; power reference rms {p_rms}; heat {h_rms}; "
          f"binomial low end 30 -> {binom_low(30)}, 44 -> {binom_low(44)}")
    print(json.dumps(precision, indent=1))


if __name__ == "__main__":
    main()
