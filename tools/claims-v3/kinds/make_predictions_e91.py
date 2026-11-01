#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E91 (Q130): write predictions-e91.json, the freeze - every number copied from its committed source, never retyped.

    python3 tools/claims-v3/kinds/make_predictions_e91.py [--out tools/claims-v3/kinds/predictions-e91.json]

E91 is E86 (the real GPT-2 tiles' energy beside E78's anchors) replicated on aifoundry1 card 1 in E82's frame.
Sources, each checked by sha256 before anything is copied (it refuses on any difference):
  Q130(n)'s frozen points    tools/claims-v3/kinds/real/predictions-real.json  bab33bee... (7d5b99af)
  Q130(n)'s Amendment 1      tools/claims-v3/kinds/real/amendment-1.json       f32e8a90... (99620cc2): the E91 column,
                             tiles.<key>.e91_aifoundry1_card1_600mhz (the amended interval / E82's per-type scale)
  the real tiles             tools/claims-v3/kinds/real/real.json              eb36f4cd... (7d5b99af)
  E82's reduction (card 1)   docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json and scored.json: the
                             card-1 reference cells (the session tie) and E82's measured card scale
  E82's freeze               tools/claims-v3/kinds/predictions-e82.json: the cross-card rules X1-X3, copied
  E86's reduction (a3)       docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json and its leakage arms: the
                             other card of the cross-card rules (committed a3c0b60d, before this freeze)
  E86's freeze               tools/claims-v3/kinds/predictions-e86.json: E86's rules, copied
  E78's freeze               tools/claims-v3/kinds/predictions-e78.json: E78-R2's bounds
It also records the sha256 of the code E91 runs unchanged (E78's and E86's) and of E91's own files, and simulates
the cross-card rules' power from E86's committed per-pass scatter (seeded; it reads no E91 data, none exist).
"""
import argparse
import hashlib
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
E82D = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1"
E86D = "docs/reports/data/2026-10-31-e86-real-tensors-energy"
SRC = {
    "predictions_real": (f"{K}/real/predictions-real.json",
                         "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941", "7d5b99af"),
    "amendment_1": (f"{K}/real/amendment-1.json",
                    "f32e8a9087a9cf3bf60f29ff623c1a375537b43696df0dca24972ba220bc0d9e", "99620cc2"),
    "real_json": (f"{K}/real/real.json", "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0", "7d5b99af"),
    "e82_reduction": (f"{E82D}/e82.json", "4794f5ac4ccfde95f45535aa855fa06c8d85b7d7716c9b63bd508ded1ade8601", None),
    "e82_scored": (f"{E82D}/scored.json", None, None),
    "e82_nodips": (f"{E82D}/posthoc/e82-nodips.json", None, None),
    "predictions_e82": (f"{K}/predictions-e82.json", None, None),
    "e86_reduction": (f"{E86D}/e86.json", "e5cc743acdc6bd47ec0b32603ed433ef09daf3f9d08c3163d66c1854eaedca40", "a3c0b60d"),
    "e86_leak0.1994": (f"{E86D}/e86-leak0.1994.json", None, "a3c0b60d"),
    "e86_leak0.3803": (f"{E86D}/e86-leak0.3803.json", None, "a3c0b60d"),
    "e86_leak0": (f"{E86D}/e86-leak0.json", None, "a3c0b60d"),
    "e86_nodips": (f"{E86D}/posthoc/e86-nodips.json", None, "a3c0b60d"),
    "e86_scored": (f"{E86D}/scored.json", None, "a3c0b60d"),
    "predictions_e86": (f"{K}/predictions-e86.json",
                        "e1f173c17de85209288290ef6e45bcee34ee21ae6f3f8696bab5ecd78e64677b", "190c1ac4"),
    "predictions_e78": (f"{K}/predictions-e78.json",
                        "83d504bbde46917dd11e87af2dc1e06b4e3f4144a624fe9f2ef21ec4cda248fe", "cfd94285"),
}
# run on the card unchanged: E78's (as E86 ran them) and E86's card-side files, at E86's freeze values
REUSED = ["tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json",
          f"{K}/e86_common.py", f"{K}/run_e86.py", f"{K}/block_e86.sh", f"{K}/queue_e86.sh"]
# scorers whose functions E91 calls unchanged (score_e86.score, score_e82.cross, score_e78.spearman)
REUSED_DESK = [f"{K}/score_e86.py", f"{K}/score_e82.py", f"{K}/score_e78.py"]
E91_FILES = [f"{K}/{f}" for f in ("run_e91.sh", "reduce_e91.py", "score_e91.py", "collect_e91.sh", "selftest_e91.py")]
TYPES = ("fp32", "fp16", "int8")
MATRICES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
COMPARE = {"fp32": "fp32.nn_like", "fp16": "fp16.nn_like", "int8": "int8.gauss_q"}
TIE_BAND_W = {"fp32": 0.50, "fp16": 0.50, "int8": 0.25}
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
X4_HALFWIDTH = 0.030


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def power(e86, names_by_type, eligible, real_names, scale, band, x4_band, n_pass=5, dev=0.0, draws=4000, seed=91):
    """The cross-card rules' verdict rates if card 1 reads E86's committed means / scale (times a per-kind factor
    N(1, dev)), with E86's per-pass scatter, n_pass kept passes on card 1, and E86's fixed means on aifoundry3."""
    rng = np.random.default_rng(seed)
    pp = e86["per_pass"]
    allnames = sorted(set(sum(names_by_type.values(), [])) | set(eligible))
    mu = {n: e86["items"][n]["D"]["mean"] for n in allnames}
    ci = {n: e86["items"][n]["D"]["ci95"] for n in allnames}
    sd = {n: float(np.std([pp[p][n]["D"] for p in pp if n in pp[p]], ddof=1)) for n in allnames}
    t = T95[n_pass - 1]
    hit = {"X1": 0, "X2a": 0, "X2b": 0, "X3": 0, "X4": 0, **{f"X1_{ty}": 0 for ty in names_by_type}}
    for _ in range(draws):
        fac = {n: 1.0 + (rng.normal(0, dev) if dev else 0.0) for n in allnames}
        m1, c1 = {}, {}
        for n in allnames:
            x = rng.normal(mu[n] / scale * fac[n], sd[n], n_pass)
            m1[n] = x.mean()
            c1[n] = x.std(ddof=1) / np.sqrt(n_pass) * t
        ok1 = True
        for ty, names in names_by_type.items():
            rho = spearman([m1[n] for n in names], [mu[n] for n in names])
            if rho >= 0.9:
                hit[f"X1_{ty}"] += 1
            else:
                ok1 = False
        hit["X1"] += ok1
        r = {n: mu[n] / m1[n] for n in eligible}
        hw = {n: r[n] * np.sqrt((ci[n] / mu[n]) ** 2 + (c1[n] / m1[n]) ** 2) for n in eligible}
        fa = np.mean([band[0] <= r[n] <= band[1] for n in eligible])
        fb = np.mean([(r[n] - hw[n]) <= band[1] and (r[n] + hw[n]) >= band[0] for n in eligible])
        hit["X2a"] += fa >= 0.8
        hit["X2b"] += fb >= 0.8
        hit["X3"] += band[0] <= np.median([r[n] for n in eligible]) <= band[1]
        hit["X4"] += x4_band[0] <= np.median([r[n] for n in real_names]) <= x4_band[1]
    return {k: round(v / draws, 3) for k, v in hit.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions-e91.json"))
    a = ap.parse_args()
    frozen = {}
    for key, (rel, want, commit) in SRC.items():
        have = sha(rel)
        if want and have != want:
            raise SystemExit(f"{key}: {rel} sha256 {have} != {want}")
        if not commit:   # the last commit that touched the file (score_e91.py reads it from there if it moves)
            commit = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--", rel], capture_output=True,
                                    text=True).stdout.strip() or None
        frozen[key] = {"path": rel, "sha256": have, **({"commit": commit} if commit else {})}
    p86 = json.load(open(os.path.join(ROOT, SRC["predictions_e86"][0])))
    for rel in REUSED[:5]:
        if sha(rel) != p86["harness"]["reused_unchanged_sha256"][rel]:
            raise SystemExit(f"{rel} differs from E86's freeze")
    for rel in REUSED[5:]:
        if sha(rel) != p86["harness"]["e86_files_sha256"][rel]:
            raise SystemExit(f"{rel} differs from E86's freeze")
    pr = json.load(open(os.path.join(ROOT, SRC["predictions_real"][0])))
    am = json.load(open(os.path.join(ROOT, SRC["amendment_1"][0])))
    rj = json.load(open(os.path.join(ROOT, SRC["real_json"][0])))
    e82 = json.load(open(os.path.join(ROOT, SRC["e82_reduction"][0])))
    s82 = json.load(open(os.path.join(ROOT, SRC["e82_scored"][0])))
    p82 = json.load(open(os.path.join(ROOT, SRC["predictions_e82"][0])))
    e86 = json.load(open(os.path.join(ROOT, SRC["e86_reduction"][0])))
    p78 = json.load(open(os.path.join(ROOT, SRC["predictions_e78"][0])))
    x3 = s82["cross_card"]["primary"]["x3"]
    tiles = {}
    for ty in TYPES:
        ref_d = e82["items"][REF[ty]]["D"]["mean"]
        cmp_d = e82["items"][COMPARE[ty]]["D"]["mean"]
        for m in MATRICES:
            key = f"{ty}/{m}"
            p, q, t = pr["tiles"][key], am["tiles"][key], rj["tiles"][ty][m]
            assert p["tile_sha256"] == t["sha256"], key
            e9, lw, t86 = q["e91_aifoundry1_card1_600mhz"], q["like_with_like"], p86["tiles"][f"{ty}.real_{m}"]
            lo, hi = e9["scoring_interval_w"]
            flo, fhi = e9["frozen_pi95_w"]
            tiles[f"{ty}.real_{m}"] = {
                "type": ty, "matrix": m, "what": t["what"], "file": f"{K}/real/{t['file']}",
                "sha256": t["sha256"], "sha256_a": t["sha256_a"], "sha256_b": t["sha256_b"],
                "gated_lane_frac": t["stats"]["gated_lane_frac"], "bus_bits_per_op": t["stats"]["bus_bits_per_op"],
                "D_frozen_w": e9["D_w"], "D_frozen_pi95_w": [flo, fhi], "D_scoring_interval_w": [lo, hi],
                "card_scale_e82": e9["card_scale_e82"], "interval_excludes": e9["excludes"],
                "a3_D_frozen_w": t86["D_frozen_w"], "a3_D_scoring_interval_w": t86["D_scoring_interval_w"],
                "ref": REF[ty], "ref_D_w": round(ref_d, 4), "ref_source": f"{E82D}/e82.json items.{REF[ty]}.D.mean",
                "ratio_scoring_interval": [round(lo / ref_d, 5), round(hi / ref_d, 5)],
                "ratio_frozen_interval": [round(flo / ref_d, 5), round(fhi / ref_d, 5)],
                "ratio_predicted_anchored": lw["ratio_to_ref_measured"],
                "compare": COMPARE[ty], "compare_D_w": round(cmp_d, 4),
                "compare_source": f"{E82D}/e82.json items.{COMPARE[ty]}.D.mean",
                "order_vs_ref_predicted": "below",
                "order_vs_compare_predicted": "below" if e9["D_w"] < cmp_d else "above",
                "provisional": ty == "int8",
            }
    e82ref = {}
    for nm in list(REF.values()) + list(COMPARE.values()) + ["anchor_pi"]:
        it = e82["items"][nm]
        ty = it["type"]
        e82ref[nm] = {"D_w": round(it["D"]["mean"], 4), "ci95_w": round(it["D"]["ci95"], 4), "n": it["D"]["n"],
                      "band_w": TIE_BAND_W[ty], "S_w": round(it["S"]["mean"], 4)}
    # ---- the cross-card rules, E82's, on E91's kinds
    sets = {ty: sorted([f"{ty}.real_{m}" for m in MATRICES] + [REF[ty], COMPARE[ty]]) for ty in TYPES}
    eligible = sorted(sum(sets.values(), []))
    real_names = sorted(tiles)
    xc = p82["cross_card"]
    band = xc["band"]
    x4_band = [round(x3["median_ratio"] - X4_HALFWIDTH, 4), round(x3["median_ratio"] + X4_HALFWIDTH, 4)]
    pw = {
        "model": "card 1 reads E86's committed D / scale (x a per-kind factor N(1, dev)), with E86's per-pass scatter "
                 "per item, 5 kept passes on card 1 (4 in the second row); aifoundry3 = E86's committed means and "
                 "intervals, fixed; 4000 draws, seed 91. Rates of PASS",
        "scale_e82_median_dev0_n5": power(e86, sets, eligible, real_names, x3["median_ratio"], band, x4_band),
        "scale_e82_median_dev0_n4": power(e86, sets, eligible, real_names, x3["median_ratio"], band, x4_band, n_pass=4),
        "scale_e82_median_dev0.012_n5": power(e86, sets, eligible, real_names, x3["median_ratio"], band, x4_band,
                                              dev=0.012),
        "scale_0.96_dev0_n5": power(e86, sets, eligible, real_names, 0.96, band, x4_band),
        "scale_1.00_dev0_n5": power(e86, sets, eligible, real_names, 1.00, band, x4_band),
        "scale_1.07_dev0_n5": power(e86, sets, eligible, real_names, 1.07, band, x4_band),
    }
    cross = {
        "against": f"E86's committed reduction of aifoundry3 card 0 ({E86D}/e86.json, a3c0b60d, 4 kept passes) and its "
                   "leakage arms; E86's post-hoc dips-removed view (posthoc/e86-nodips.json) only in a reported pair",
        "quantity": "D, each kind's switching power over its own type's zeros (mean over kept passes), on each card",
        "orientation": "every ratio is D(aifoundry3, E86) / D(card 1, E91), as E82's D(aifoundry3) / D(card 1)",
        "band": band, "band_source": "predictions-e82.json cross_card.band, copied: " + xc["band_source"],
        "min_passes_each": xc["min_passes_each"],
        "X1": {**{k: v for k, v in xc["X1"].items() if k not in ("sets", "power")}, "sets": sets,
               "copied_from": "predictions-e82.json cross_card.X1 (threshold, min_resolved_frac, pass_if)",
               "power": "this freeze's power block: five kinds a type, four of them (the three real tiles and random "
                        "data) within 1.7% (fp32) and 2.9% (fp16) of each other on E86, so their order is within the "
                        "noise; X1 can fail on noise in fp32 and fp16"},
        "eligible_kinds": eligible,
        "eligible_rule": "every non-zero E91 kind: the nine real tiles (frozen points 5.18-24.46 W) and the six E78 "
                         "kinds in E82's own eligible list (each type's random kind and its comparison kind); E82's "
                         "rule was a frozen prediction >= 5.0 W, and all fifteen meet it",
        "X2": {k: v for k, v in xc["X2"].items() if k != "power"},
        "X3": {k: v for k, v in xc["X3"].items() if k != "power"},
        "X4": {"name": "the real tiles share the card scale E82 measured",
               "what": "the median over the nine real tiles of D(aifoundry3, E86) / D(card 1, E91)",
               "band": x4_band,
               "band_source": f"E82's measured median ratio over its 32 eligible kinds, {x3['median_ratio']:.4f} "
                              f"({E82D}/scored.json cross_card.primary.x3.median_ratio), +- {X4_HALFWIDTH}: 2.5x the "
                              "1.2% sd of E82's per-kind ratios (its README result 1); E82's IQR "
                              f"{x3['iqr'][0]:.4f}-{x3['iqr'][1]:.4f}",
               "pass_if": "inside the band; else FAIL; NOT SCORED with fewer than 7 of the 9 resolved on both cards",
               "min_resolved": 7},
        "expectation": "E82 measured the card scale at 1.031 (X2a, X2b and X3 FAIL against September's band). If the "
                       "real tiles share it, X2a, X2b and X3 fail again here, and X4 passes; the rules are kept as E82 "
                       "registered them so that both experiments are scored alike",
        "arms": {"own idle slopes (card 1 0.545, aifoundry3 0.3803)": ["leak0.545", "e86-leak0.3803.json"],
                 "0.3803 on both": ["leak0.3803", "e86-leak0.3803.json"],
                 "0.1994 on both (Q130(n)'s D scope)": ["leak0.1994", "e86-leak0.1994.json"],
                 "no correction on both": ["leak0", "e86-leak0.json"]},
        "reported_pairs": {"both dips removed (E91 primary, E86 post hoc)": ["primary", "posthoc/e86-nodips.json"],
                           "E91 dips kept, E86 registered": ["dips_kept", "e86.json"]},
        "power": pw,
    }
    rules86 = p86["rules"]
    reg = {
        "experiment": "E91",
        "title": "the real tensors' energy replicated: E86's nine real GPT-2 tiles beside E78's anchors and comparison "
                 "kinds, on aifoundry1 card 1 (600 MHz) in E82's frame",
        "request": "Q130 evening round (workflow q130-evening, lane a1c1-e91-real-replicate), Sat 31 Oct 2026",
        "date": "2026-10-31",
        "registration": f"{K}/E91.md",
        "replicates": {"E86": f"{K}/E86.md (registration 190c1ac4, data a3c0b60d)",
                       "frame": f"{K}/E82.md (card 1, config gate 65/65, leakage arm 0.545) and "
                                "tools/claims-v3/rpath/E88.md (card 1's meter dips removed as the primary reduction)"},
        "card": {"host": "aifoundry1", "card": 1, "V3_DEVICE": 1, "card_name": "aifoundry1-c1",
                 "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600, "minion_mv_approx": 499,
                 "firmware": "release 1.4.0, BL2 0.22.0 (E82 A1, read 13:45 PDT)",
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65},
                                 "note": "E82's substitution: a read equal to card 1's 65/65 is handed to E78's gate "
                                         "as the (0, 65) it accepts; any other read sets the pass apart"},
                 "writes": "nothing (no governor, TDP, threshold or clock set; no reset; no --reset-ms)"},
        "inputs_frozen": frozen,
        "harness": {
            "reused_unchanged_sha256": {r: sha(r) for r in REUSED},
            "reused_desk_sha256": {r: sha(r) for r in REUSED_DESK},
            "e91_files_sha256": {r: sha(r) for r in E91_FILES if os.path.exists(os.path.join(ROOT, r))},
            "binary": "build/sparsity/host/sparsity_host in aifoundry1's ~/nekko (built 28 Sep 20:56; E82 and E88 ran it)",
            "data_dir": "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1/",
            "raw_data_on_box": "~/nekko/build/claims-v3/aifoundry1-c1/kinds/p91<nn>/ and kinds-smoke/p9101/",
        },
        "plan": {
            "passes_planned": [9110, 9111, 9112, 9113, 9114, 9115], "passes_min": 4, "smoke": 9101,
            "runs_per_pass": 32,
            "pass": "E86's: the tie (anchor_pi), three segments of E78's six anchors and four of the twelve E86 items, "
                    "the tie; the twelve shuffled by Random('E86|aifoundry1-c1|<pass>') and dealt round-robin "
                    "(e86_common.pass_order, unchanged, with this card's name)",
            "anchors_three_per_pass": p86["plan"]["anchors_three_per_pass"],
            "once_per_pass": p86["plan"]["once_per_pass"],
            "smoke_items": "e86_common.SMOKE_ITEMS (seven 2 s runs, no preheat)",
            "run": p86["plan"]["run"],
        },
        "card_budget": {"max_card_min": 35, "counted": "from the claim post to its release edit",
                        "queue_budget_min": 30, "first_pass_estimate_s": 390, "deadline_local": "22:25",
                        "no_new_session_after": "21:45 PDT", "runs_end_by": "22:30 PDT",
                        "how": "queue_e86.sh unchanged, with E86_BUDGET_MIN=30 E86_DEADLINE=22:25 E86_FIRST_S=390"},
        "analysis": {
            "reduction": "reduce_e78.py unchanged (via reduce_e91.py) with E86's items installed, E82's config-gate "
                         "substitution, and card 1's board-meter launch-gap dips removed from the telemetry first "
                         "(E82 A2's definition: board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W; E88's registered "
                         "primary on this card): D = p80 - Zhat_type(t0); one value per (pass, item); the pass the "
                         "unit of replication",
            "dips_why": "on card 1 the dips set aside 2 of 7 E82 passes and 3 of 6 E88 passes (dips kept); E91 has "
                        "about five passes, so the registered E78 reduction with dips kept could leave fewer than "
                        "four. E86 (aifoundry3) set one of five aside for the same reason",
            "leak_primary": "auto (E78's registered estimator, on E91's own runs)",
            "arms": {"dips_kept": "the same reduction on the raw telemetry (E82's frame unchanged)",
                     "leak": [0.1994, 0.545, 0.3803, 0.0]},
            "arms_why": "0.1994 W/C: Q130(n)'s D scope (E86's arm); 0.545: card 1's idle slope (E82's arm); 0.3803 "
                        "(E71) and 0: E78's arms. Arms are reported; a verdict that moves is marked arm-sensitive",
            "min_kept_passes": 4, "min_passes_per_quantity": 3,
        },
        "tiles": tiles,
        "e82_reference": e82ref,
        "e82_reference_source": f"{E82D}/e82.json (E82's registered reduction of card 1, 5 kept passes, dips kept); "
                                "its post-hoc dips-removed view is reported beside",
        "rules": {
            "E91-R1": {**rules86["E86-R1"], "what": "each real tile's D (mean over kept passes) inside Amendment 1's "
                       "E91 scoring interval (tiles.<name>.D_scoring_interval_w = "
                       "amendment-1.json tiles.<key>.e91_aifoundry1_card1_600mhz.scoring_interval_w)",
                       "beside": "the count inside the frozen E91 intervals; the count whose own 95% interval overlaps; "
                                 "the count inside aifoundry3's (unscaled) intervals; every arm"},
            "E91-R2": {**rules86["E86-R2"], "what": "rms over a format's three tiles of (D - D_frozen_w), D_frozen_w "
                       "the E91 point (Q130(n)'s frozen point / E82's per-type scale)",
                       "bound_w": p78["rules"]["E78-R2"]["bound_w"]},
            "E91-R3": rules86["E86-R3"],
            "E91-R4": {**rules86["E86-R4"], "what": "per tile, paired per pass: D(real) - D(compare); predicted side "
                       "from the E91 point against E82's measured compare on card 1 "
                       "(tiles.<name>.order_vs_compare_predicted)"},
            "E91-R5": {"name": "the session tie on card 1",
                       "what": "D of each e82_reference cell (fp32/fp16 randn, int8 full, fp32/fp16 nn_like, int8 "
                               "gauss_q, anchor_pi) within band_w of E82's (card 1, the same protocol, 6-7 h earlier)",
                       "pass_if": "all seven inside their bands (E86-R5's bands, copied)",
                       "meaning": "a failure means the session moved, not that a model did; S1 is then the reading"},
            "E91-S1": {**rules86["E86-S1"], "what": "per tile, the per-pass ratio D(real)/D(ref), averaged over "
                       "passes, inside tiles.<name>.ratio_scoring_interval (the E91 scoring interval over E82's "
                       "D(ref) on card 1)"},
            "E91-X1": "cross_card.X1 (E82's, copied)", "E91-X2a": "cross_card.X2.X2a (E82's, copied)",
            "E91-X2b": "cross_card.X2.X2b (E82's, copied)", "E91-X3": "cross_card.X3 (E82's, copied)",
            "E91-X4": "cross_card.X4 (E91's: E82's measured scale)",
            "E91-C": rules86["E86-C"],
        },
        "cross_card": cross,
        "reported_never_a_verdict": [
            "per tile, D(real)/D(ref) on card 1 against E86's on aifoundry3: the difference and its 95% interval "
            "(two independent experiments, intervals added in quadrature)",
            "every rule at the dips-kept arm and the four leakage arms",
            "the dip samples removed per pass, and where they fell",
            "S, pJ per op / MAC / flop, the heat column dT, D32, the rail, for every tile and comparison kind",
            "the session tie against E82's post-hoc dips-removed cells",
        ],
        "not_scored_if": "fewer than 4 kept passes: every rule NOT SCORED; a quantity with fewer than 3 kept passes "
                         "is unresolved and never counts as inside or PASS",
    }
    json.dump(reg, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}: {len(tiles)} tiles, sha256 {hashlib.sha256(open(a.out, 'rb').read()).hexdigest()}")
    print(json.dumps(pw, indent=1))


if __name__ == "__main__":
    main()
