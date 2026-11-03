#!/usr/bin/env python3
"""E152 (Q139): the freeze - every number E152's rules use, written to predictions-e152.json before the claim of
aifoundry3 and before any card has run one of E152's nine ladder tiles. Standard library only.

    python3 tools/claims-v3/e152/make_predictions_e152.py     # writes predictions-e152.json and predictions-e152.md

What it reads, each checked by sha256 and named in the output:
  * E127's registered reading, docs/reports/data/2026-11-02-e127-b-gate/scored.json (committed 9b6311c7, unchanged since):
    the per-pass Q2 = q_chk - q_steady and Q5 = q_steady_hi - q_steady over its five kept passes. THE PRICE PER FLIP frozen
    here is E127's whole contrast per gate flip at equal live count and equal operand bus, net of half its lane-position
    contrast (E127's correction C2: q_chk has half its live lane-cycles on lanes 0-3, q_steady none; E152's ladder tiles all
    have half): p* = mean over passes of (Q2 - Q5 / 2) / (4,096 flips x the op rate), with t(4)'s 95% interval. The op rate
    is fit_m5's (600 MHz / 546 cycles x 1,024 minions x 0.9963 duty), the rate E127's post hoc price used. The unnetted
    price (Q2 alone) is carried as an arm.
  * e152-tiles.json (make_e152.py): the designed flips an op of every tile.
  * M8 (docs/reports/data/2026-11-03-q139m-model/m8.json, frozen 122da8b6) and M7 (2026-11-02-q138m-model/m7.json): their
    float per-flip constant gtr, and their frozen predictions of E127's two bridge tiles, written by predict_blind6.py (the
    committed predictor, nothing refitted) on E127's bench counts (tools/claims-v3/e127/counts-e127.json) - the output is
    m8-bridge/predictions-aifoundry3.json beside this file. M8's whole price per flip at E127's pair = its predicted Q2 over
    4,096 flips x the op rate. E152's nine new tiles have no bench counts (the RTL bench was not run for them), so the models'
    ladder predictions are given two ways, both labelled: "gtr only" (the gate term alone, gtr x the flips) and "linear
    bench" (the models' whole price per flip at E127's pair x the flips, which assumes the bench's toggle terms scale with
    the flips). Neither is a verdict.
  * E127's session tie (its S1 cells, dips removed) for E152-S1, and its Q2 for E152-S2.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = "tools/claims-v3/e152"
E127_SCORED = "docs/reports/data/2026-11-02-e127-b-gate/scored.json"
M8 = "docs/reports/data/2026-11-03-q139m-model/m8.json"
M7 = "docs/reports/data/2026-11-02-q138m-model/m7.json"
PRED6 = "docs/reports/data/2026-11-03-q139m-model/predict_blind6.py"
COUNTS127 = "tools/claims-v3/e127/counts-e127.json"
BRIDGE_PRED = f"{REL}/m8-bridge/predictions-aifoundry3.json"
RATE = 600e6 / 546 * 1024 * 0.9963          # ops a second, chip-wide (fit_m5.RATE["fp32"]; E127's posthoc_e127.py)
T4 = 2.776                                   # t(4), 97.5%
LADDER8 = ["fp32.gd0", "fp32.gd1a", "fp32.gd1b", "fp32.gd2a", "fp32.gd2b", "fp32.gd4a", "fp32.gd4b", "fp32.gd8"]


def fsha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    sc = json.load(open(os.path.join(ROOT, E127_SCORED)))["primary"]
    C = sc["contrasts"]

    def c(k):
        return next(v for n, v in C.items() if n.startswith(k + ":"))

    q2, q5 = c("Q2"), c("Q5")
    assert sc["passes"] == [12710, 12711, 12712, 12713, 12714], sc["passes"]
    net = [a - 0.5 * b for a, b in zip(q2["per_pass_w"], q5["per_pass_w"])]

    def price(series):
        m = sum(series) / len(series)
        h = T4 * statistics.stdev(series) / math.sqrt(len(series))
        f = 4096 * RATE * 1e-15
        return {"p_fJ": m / f, "lo95": (m - h) / f, "hi95": (m + h) / f, "contrast_w": m, "contrast_ci95_w": h,
                "per_pass_w": series}

    p_net, p_raw = price(net), price(q2["per_pass_w"])
    spec = json.load(open(os.path.join(HERE, "e152-tiles.json")))
    tiles = {n: {"family": v["family"], "kind": v["kind"], "lanes_switching": v["lanes_switching"],
                 "flips_per_op": v["stats"]["gate_flips_per_op"], "flips_above_gd0": v["stats"]["flips_above_gd0"],
                 "boundaries_with_a_flip": v["stats"]["boundaries_with_a_flip"], "file": v["file"], "sha256": v["sha256"]}
             for n, v in spec["tiles"].items()}
    groups = {"0": ["fp32.gd0"], "1": ["fp32.gd1a", "fp32.gd1b"], "2": ["fp32.gd2a", "fp32.gd2b"],
              "4": ["fp32.gd4a", "fp32.gd4b"], "8": ["fp32.gd8"]}
    doses = {}
    for n, g in groups.items():
        f = {tiles[k]["flips_above_gd0"] for k in g}
        assert len(f) == 1 and f.pop() == 510 * int(n), (n, g)
        doses[n] = {"n": int(n), "flips_above_gd0": 510 * int(n), "tiles": g}
    # the models: gtr, and their frozen predictions of E127's two bridge tiles (predict_blind6.py on counts-e127.json)
    m8, m7 = json.load(open(os.path.join(ROOT, M8))), json.load(open(os.path.join(ROOT, M7)))

    def coef(m, term):
        fl = m["families"]["float"]
        cf = fl["coef_fJ"]
        return cf[term] if isinstance(cf, dict) else dict(zip(fl["terms"], cf))[term]

    gtr8, gtr7 = coef(m8, "gtr"), coef(m7, "gtr")
    gtr8_se = m8["families"]["float"]["coef_jackknife_se_fJ"]["gtr"]
    bp = json.load(open(os.path.join(ROOT, BRIDGE_PRED)))
    rows = {r["name"]: r for r in bp["tiles"]} if isinstance(bp.get("tiles"), list) else bp["tiles"]

    def model_d(name, model):
        r = rows[name]
        v = r[model] if model in r else r["models"][model]
        return v["D_w"] if isinstance(v, dict) and "D_w" in v else (v["D"] if isinstance(v, dict) else v)

    mq = {mdl: {t: model_d(t, mdl) for t in ("fp32.q_steady", "fp32.q_chk")} for mdl in ("M8", "M7", "M6")}
    whole = {mdl: (v["fp32.q_chk"] - v["fp32.q_steady"]) / (4096 * RATE) * 1e15 for mdl, v in mq.items()}
    models = {"M8_whole_at_E127_pair": whole["M8"], "M7_whole_at_E127_pair": whole["M7"], "M6_whole_at_E127_pair": whole["M6"],
              "M8_gtr": gtr8, "M8_gtr_jackknife_se": gtr8_se, "M7_gtr": gtr7}
    f8 = 4080 * RATE * 1e-15
    C8s = p_net["p_fJ"] * f8
    pred = {"C8_star_w": C8s, "C_pred_w": {}, "what": "C(n) = D(dose n) - D(gd0), W; E127_price = p* x 510 n x the op rate"}
    for n in ("1", "2", "4", "8"):
        fl = 510 * int(n) * RATE * 1e-15
        pred["C_pred_w"][n] = {"E127_price": p_net["p_fJ"] * fl, "E127_price_lo95": p_net["lo95"] * fl,
                               "E127_price_hi95": p_net["hi95"] * fl, "E127_price_unnetted": p_raw["p_fJ"] * fl,
                               "M8_gtr_only": gtr8 * fl, "M8_linear_bench": whole["M8"] * fl,
                               "M7_gtr_only": gtr7 * fl, "M7_linear_bench": whole["M7"] * fl}
    pred["gd0_minus_q_steady_w"] = 0.5 * q5["measured_w"] + p_net["p_fJ"] * 16 * RATE * 1e-15
    pred["gd0_minus_q_steady_what"] = ("E127's lane position taken as additive per live lane-cycle (half of Q5, gd0 has half "
                                       "its live lane-cycles on lanes 0-3, q_steady none) plus gd0's 16 flips an op at p*")
    pred["gd8_minus_q_chk_w"] = 0.0
    pred["bridge"] = {"E127_measured_D_w": {t: sc["table"][t]["D"] for t in ("fp32.q_steady", "fp32.q_chk")},
                      "E127_Q2_w": q2["measured_w"], "models_D_w": mq,
                      "models_Q2_w": {mdl: v["fp32.q_chk"] - v["fp32.q_steady"] for mdl, v in mq.items()}}
    # the precision before the data (README "Precision"): E127's quiet contrasts' per-pass sd, as independent tile noise
    sds = [statistics.stdev(c(k)["per_pass_w"]) for k in ("Q1", "Q2", "Q3", "Q4", "Q5")]
    sig = (sum(sds) / len(sds)) / math.sqrt(2)
    plan_h = {}
    for npass, t in ((4, 3.182), (5, 2.776), (6, 2.571)):
        hh = {}
        for n, k in ((1, 2), (2, 2), (4, 2)):
            var = 1 / k + (1 - n / 8) ** 2 + (n / 8) ** 2
            hh[f"delta_{n}_w"] = t * sig * math.sqrt(var) / math.sqrt(npass)
        xs = [tiles[k]["flips_per_op"] for k in LADDER8]
        mx = sum(xs) / len(xs)
        sxx = sum((x - mx) ** 2 for x in xs)
        hh["price_fJ"] = t * sig / math.sqrt(sxx) / math.sqrt(npass) / RATE * 1e15
        plan_h[str(npass)] = hh
    reused = {r: fsha(r) for r in ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py",
                                   "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py",
                                   "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh")}
    want = {"tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
            "tools/claims-v3/kinds/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
            "tools/claims-v3/kinds/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
            "tools/claims-v3/kinds/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
            "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
            "tools/claims-v3/e128/ettelem_guard.sh": "c2c4ab7602c2e4d2b3ed3454faa4f60b745d5985bb7f71713229979079dbd2fc"}
    assert reused == want, "the reused E78 card code is not the code E127 registered and ran (or E128's guard changed)"
    files = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(HERE, "*"))
                   if os.path.isfile(p) and not p.endswith(("predictions-e152.json", "predictions-e152.md", "README.md"))
                   and "__pycache__" not in p)
    reg = {
        "experiment": "E152 (Q139)", "date": "2026-11-03",
        "answers": spec["answers"],
        "written_by": f"{REL}/make_predictions_e152.py",
        "plan": {"card": "aifoundry3 card 0", "clock": "600 MHz as read (TDP 0 latched at boot), never set",
                 "rate_ops_per_s": RATE, "first_pass": 15210, "passes_planned": 6, "smoke_pass": 15201,
                 "stoptest_passes": {"board": 15202, "die": 15203}, "runs_per_pass": 31, "launches_per_pass": 33,
                 "min_kept_passes_scored": 3, "min_tile_passes": 3, "min_c8_frac": 0.25,
                 "board_power_stop_w": 65.0, "die_stop_c": 70.0, "card_minutes_max": 40, "budget_s_from_session_start": 2160,
                 "first_pass_estimate_s": 360, "gap_s": 15,
                 "deadline": "2026-11-03 11:20 PST (every run ends by 11:30 PST; no session starts after 10:30 PST)",
                 "primary_reduction": "reduce_e78.py unchanged via reduce_e152.py --drop-dips (E82 A2), leakage auto",
                 "arms": ["dips kept", "leakage 0.1994 (dips removed)", "leakage 0.3803 (dips removed)",
                          "leakage 0 (dips removed)", "gates off (dips removed)"],
                 "fewer_than_min_kept": "every rule NOT SCORED on the primary; the gates-off arm is then the reading reported, labelled"},
        "price": {**p_net, "what": "E127's (Q2 - Q5/2) per pass over 4,096 flips x the op rate, fJ a gate flip, whole (not "
                                   "beyond any model); 95% t(4) over E127's five kept passes",
                  "unnetted": p_raw, "source": E127_SCORED, "source_sha256": fsha(E127_SCORED)},
        "tiles": tiles, "doses": doses, "dose_groups": groups, "predictions": pred, "models_per_flip_fJ": models,
        "rules": {
            "E152-R1": {"what": "linear within 10%: every |delta(n)| + h <= 0.10 x C8* -> LINEAR; some |delta(n)| - h > it -> "
                                "NONLINEAR; else INCONCLUSIVE; NOT SCORED unless C(8)'s low end >= 0.25 x C8*",
                        "tolerance_frac": 0.10, "tau_w": 0.10 * C8s, "doses": [1, 2, 4]},
            "E152-R2": {"what": "E127's price carries: the ladder's least-squares price per flip inside [0.9, 1.1] x p* -> "
                                "CARRIES; wholly outside -> MISSES; else INCONCLUSIVE", "band_frac": 0.10, "tiles": LADDER8},
            "E152-S1": {"what": "the session tie against E127 (its dips-removed reading)"},
            "E152-S2": {"what": "the bridge: q_chk - q_steady against E127's Q2", "E127_w": q2["measured_w"], "band_w": 0.25},
        },
        "session_tie": {"cells": {k: {"ref_w": v["D"], "band_w": v["band_w"]} for k, v in sc["rules"]["E127-S1"]["cells"].items()},
                        "source": "E127's S1 cells, dips removed"},
        "precision_before_data": {"sigma_tile_w": sig, "from": "E127's Q1-Q5 per-pass sd / sqrt(2), as independent tile noise",
                                  "half_widths_by_passes": plan_h},
        "expectations_frozen": {
            "E152-R1": "LINEAR: a lane's gate flip spends its price in that lane's own clock-gate enable and clock branch, so "
                       "the price adds over lanes and the ladder is straight; a share spent whenever ANY lane flips (a shared "
                       "enable or valid path) would bend it concave, and I do not expect one",
            "E152-R2": "CARRIES, with INCONCLUSIVE likely if the session's level moves (the slope's planned half-width is about "
                       "6% of the price at six passes, so a session offset of more than about 4% reads INCONCLUSIVE)",
            "E152-S1": "PASS", "E152-S2": "PASS",
            "reported": "the mirrored pairs within 0.1 W; gd1h equal to gd1a/gd1b within 0.1 W; gd0 - q_steady about +0.07 W "
                        "(lane position, additive); gd8 - q_chk about 0"},
        "harness": {
            "reused_unchanged_sha256": reused,
            "e152_tiles_sha256": {v["file"]: v["sha256"] for v in tiles.values()},
            "e152_files_sha256": {f: fsha(f) for f in files},
            "binaries_sha256": {"build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
                                "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0"},
            "frozen_inputs_sha256": {r: fsha(r) for r in (E127_SCORED, M8, M7, PRED6, COUNTS127, BRIDGE_PRED,
                                                           "tools/claims-v3/e127/tiles/fp32/q_steady.bin",
                                                           "tools/claims-v3/e127/tiles/fp32/q_chk.bin")},
        },
    }
    jp = os.path.join(HERE, "predictions-e152.json")
    json.dump(reg, open(jp, "w"), indent=1, sort_keys=True)
    L = ["# E152's frozen numbers (written by make_predictions_e152.py)\n\n",
         f"E127's price per gate flip (whole, net of half its lane-position contrast): **{p_net['p_fJ']:.1f} fJ "
         f"[{p_net['lo95']:.1f}, {p_net['hi95']:.1f}]**; unnetted {p_raw['p_fJ']:.1f} [{p_raw['lo95']:.1f}, {p_raw['hi95']:.1f}]. "
         f"Op rate {RATE:.6e} /s. C8* = {C8s:.4f} W; tau = {0.10 * C8s:.4f} W.\n\n",
         "| dose n | flips above gd0 | C predicted, E127's price [95%] | M8 linear bench | M8 gtr only | M7 linear bench |\n|---|---:|---:|---:|---:|---:|\n"]
    for n in ("1", "2", "4", "8"):
        v = pred["C_pred_w"][n]
        L.append(f"| {n} | {510 * int(n)} | {v['E127_price']:+.4f} [{v['E127_price_lo95']:+.4f}, {v['E127_price_hi95']:+.4f}] | "
                 f"{v['M8_linear_bench']:+.4f} | {v['M8_gtr_only']:+.4f} | {v['M7_linear_bench']:+.4f} |\n")
    L.append(f"\nModels per flip (fJ): M8 whole at E127's pair {whole['M8']:.1f}, M8 gtr {gtr8:.1f} (jackknife se {gtr8_se:.1f}), "
             f"M7 whole {whole['M7']:.1f}, M7 gtr {gtr7:.1f}, M6 whole {whole['M6']:.1f}.\n\n"
             f"Bridge: E127 measured q_steady {pred['bridge']['E127_measured_D_w']['fp32.q_steady']:.3f}, q_chk "
             f"{pred['bridge']['E127_measured_D_w']['fp32.q_chk']:.3f} W (Q2 {q2['measured_w']:+.3f}); M8 "
             f"{mq['M8']['fp32.q_steady']:.3f} / {mq['M8']['fp32.q_chk']:.3f} W.\n\n"
             f"gd0 - q_steady predicted {pred['gd0_minus_q_steady_w']:+.4f} W; gd8 - q_chk 0.\n\n")
    L.append(f"Planned 95% half-widths (sigma_tile {sig:.4f} W): " +
             "; ".join(f"{k} passes: " + ", ".join(f"{q} {v:.3f}" for q, v in hh.items()) for k, hh in plan_h.items()) + "\n")
    open(os.path.join(HERE, "predictions-e152.md"), "w").write("".join(L))
    print(json.dumps({"price_fJ": round(p_net["p_fJ"], 2), "C8_star_w": round(C8s, 4), "tau_w": round(0.1 * C8s, 4),
                      "M8_whole": round(whole["M8"], 1), "M7_whole": round(whole["M7"], 1), "sigma": round(sig, 4),
                      "planned": {k: {q: round(v, 3) for q, v in hh.items()} for k, hh in plan_h.items()},
                      "sha256": hashlib.sha256(open(jp, "rb").read()).hexdigest()}))


if __name__ == "__main__":
    main()
