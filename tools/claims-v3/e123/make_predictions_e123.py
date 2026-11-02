#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E123 (Q134): freeze E123's numbers into predictions-e123.json, before the claim and the first launch. Every number is
read or computed from a committed file named here (each recorded with its sha256), never retyped.

    python3 tools/claims-v3/e123/make_predictions_e123.py      # writes tools/claims-v3/e123/predictions-e123.json

Registration: tools/claims-v3/e123/E123.md.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KDIR = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, HERE)

SRC = {
    "kinds_json": "tools/claims-v3/kinds/kinds.json",
    "e123_json": "tools/claims-v3/e123/e123.json",
    "e78_reduction": "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json",
    "e94_predictions": "tools/claims-v3/kinds/predictions-e94.json",
    "e94_scored": "docs/reports/data/2026-11-01-e94-tile-spread/scored.json",
}
REUSED = ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json")
CARD_FILES = ("tools/claims-v3/e123/e123_common.py", "tools/claims-v3/e123/run_e123.py",
              "tools/claims-v3/e123/block_e123.sh", "tools/claims-v3/e123/queue_e123.sh",
              "tools/claims-v3/e123/run_e123.sh", "tools/claims-v3/e123/e123.json", "tools/claims-v3/e123/make_e123.py",
              "tools/claims-v3/e123/reduce_e123.py")
DESK_FILES = ("tools/claims-v3/e123/score_e123.py", "tools/claims-v3/e123/selftest_e123.py",
              "tools/claims-v3/e123/collect_e123.sh", "tools/claims-v3/e123/make_predictions_e123.py",
              "tools/claims-v3/kinds/score_e94.py")
RANDOM_ANCHOR = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
BAND = {"fp32": 0.50, "fp16": 0.50, "int8": 0.25}
CLASSES = {
    "G": "float kinds gating 25-75% of lanes (E94 measured a between-draw SD of 0.5-0.7 W on three such rows)",
    "LF": "the other float dagger rows (E94's desk table predicted 0.32 W or less)",
    "LI": "the int8 dagger rows E94 did not run (E94's desk table predicted 0.26 W or less)",
}
# one tile's between-pass SD assumed ONLY by the single-pass fallback (above E94's measured 0.04-0.11 W on card 1)
SIGMA_FALLBACK = {"fp32": 0.15, "fp16": 0.15, "int8": 0.12}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}


def t975(df):
    d = max(1, int(math.floor(df)))
    return T975.get(d, 2.0 if d > 20 else T975[1])


def main():
    import e123_common as e123  # noqa: E402  (no numpy needed there)
    kinds = load(SRC["kinds_json"])
    spec = load(SRC["e123_json"])
    e78 = load(SRC["e78_reduction"])
    p94 = load(SRC["e94_predictions"])
    s94 = load(SRC["e94_scored"])
    it78 = e78["items"]
    beta = {t: it78[a]["D"]["mean"] for t, a in RANDOM_ANCHOR.items()}

    rules = {}
    for rule, r in spec["rules"].items():
        t, kind = rule.split(".", 1)
        base = kinds["kinds"][t][kind]
        rep = base["replicates"]["gated_lane_frac"]
        dt = p94["desk_table"][rule]
        draws = sorted(n for n, v in spec["tiles"].items() if v["rule_of"] == rule)
        g_c = base["stats"]["gated_lane_frac"]
        D_c = it78[rule]["D"]["mean"]
        rules[rule] = {
            "type": t, "kind": kind, "class": r["class"], "committed": rule, "draws": draws,
            "fresh": [n for n in draws if spec["tiles"][n]["group"] == "draw"],
            "bridge": [n for n in draws if spec["tiles"][n]["group"] == "bridge"],
            "band_w": BAND[t],
            "committed_gate_share": g_c,
            "rule_gate_share": {"n": rep["n"], "mean": rep["mean"], "sd": rep["sd"], "se_of_mean": rep["sd"] / math.sqrt(rep["n"]),
                                "p2.5": rep["p2.5"], "p97.5": rep["p97.5"]},
            "cv_slope_w_per_unit": beta[t],
            "cv_slope_source": f"E78's D of {RANDOM_ANCHOR[t]} on aifoundry3 ({SRC['e78_reduction']} items.{RANDOM_ANCHOR[t]}.D.mean)",
            "gate_law_slope_w_per_unit": D_c / (1.0 - g_c),
            "e78_a3": {"D_w": D_c, "D_se_w": it78[rule]["D"]["se"], "S_w": it78[rule]["S"]["mean"],
                       "S_se_w": it78[rule]["S"]["se"], "n_passes": it78[rule]["D"]["n"]},
            "desk_table_e94": {"gate_law_sd_w": dt.get("gate_law_sd_a3_w"), "q130n_sd_w": dt.get("q130n_sd_a3_w"),
                               "gate_law_offset_w": dt.get("gate_law_committed_minus_mean_a3_w"),
                               "q130n_offset_w": dt.get("q130n_committed_minus_mean_a3_w"),
                               "measured_by_e94": dt.get("measured_by_e94")},
        }
    tiles = {}
    for n, v in spec["tiles"].items():
        r = rules[v["rule_of"]]
        g = v["stats"]["gated_lane_frac"]
        tiles[n] = {"rule_of": v["rule_of"], "class": r["class"], "group": v["group"], "gated_lane_frac": g,
                    "bus_bits_per_op": v["stats"]["bus_bits_per_op"],
                    "inside_rule_band": v.get("inside_rule_band"),
                    "gate_law_delta_w": r["e78_a3"]["D_w"] * ((1.0 - g) / (1.0 - r["committed_gate_share"]) - 1.0),
                    "cv_shift_w": r["cv_slope_w_per_unit"] * (g - r["rule_gate_share"]["mean"])}

    # the bridge: E94's card-1 means of fp32.nn_like and its six draws (E94's registered two-way fit)
    rn = s94["primary"]["rules_of_number"]["fp32.nn_like"]
    c1 = rn["per_tile"]["fp32.nn_like"]["mean_w"]
    scale = p94["card_scale"]["per_type"]["fp32"]
    bridge = {"rule": "fp32.nn_like", "card_scale_fp32": scale, "card_scale_source": p94["card_scale"]["source"],
              "card1_committed_D_w": c1,
              "card1_offsets_w": {n: rn["per_tile"][n]["mean_w"] - c1 for n in rules["fp32.nn_like"]["bridge"]},
              "card1_source": f"{SRC['e94_scored']} primary.rules_of_number.fp32.nn_like.per_tile"}

    tie = {"reference": f"{SRC['e78_reduction']} items.<cell>.D.mean (E78's primary on this card, leakage auto = 0.1994 W/C)",
           "cells": {}}
    for c in list(rules) + ["fp32.randn", "fp16.randn", "int8.full", "anchor_pi"]:
        t = it78[c]["type"] if "type" in it78[c] else c.split(".")[0]
        tie["cells"][c] = {"ref_w": it78[c]["D"]["mean"], "band_w": 0.25 if t == "int8" else 0.50}

    # what the rules can say: a simple simulation of R2 (primary, CV) for every rule, with E123's actual draws' gate shares
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(b"E123-sim").digest()[:8], "little"))
    sims = 4000
    sig = {"fp32": 0.10, "fp16": 0.10, "int8": 0.10}   # one tile's between-pass SD (E94: 0.04-0.11 W)
    tres = {"G": 0.08, "LF": 0.08, "LI": 0.05}          # what the gate share leaves of a draw (E94 R7: 0.10 W with noise)
    n_pass = 2
    power = {}
    for world, slope_of in (("frozen slope true", lambda r: r["cv_slope_w_per_unit"]),
                            ("gate-law slope true", lambda r: r["gate_law_slope_w_per_unit"])):
        counts = {rule: {"CORRECTION": 0, "NO CORRECTION": 0, "UNRESOLVED": 0} for rule in rules}
        for _ in range(sims):
            by_class = {}
            sim = {}
            for rule, r in rules.items():
                t = r["type"]
                gbar = r["rule_gate_share"]["mean"]
                b_true = slope_of(r)
                delta = r["desk_table_e94"]["gate_law_offset_w"] or 0.0
                ys = []
                for n in r["draws"]:
                    g = tiles[n]["gated_lane_frac"]
                    y = -b_true * (g - gbar) + rng.normal(0, tres[r["class"]]) + rng.normal(0, sig[t] / math.sqrt(n_pass))
                    ys.append(y + r["cv_slope_w_per_unit"] * (g - gbar))
                yc = delta + rng.normal(0, sig[t] / math.sqrt(n_pass))
                sim[rule] = (ys, yc)
                k = len(ys)
                m = sum(ys) / k
                by_class.setdefault(r["class"], []).append((k - 1, sum((y - m) ** 2 for y in ys)))
            pooled = {c: (sum(s for _, s in v) / sum(d for d, _ in v), sum(d for d, _ in v)) for c, v in by_class.items()}
            for rule, r in rules.items():
                ys, yc = sim[rule]
                k = len(ys)
                s2, df = pooled[r["class"]]
                N2 = sig[r["type"]] ** 2 / n_pass
                var = s2 / k + N2 + (r["cv_slope_w_per_unit"] * r["rule_gate_share"]["se_of_mean"]) ** 2
                off = yc - sum(ys) / k
                hw = t975(df) * math.sqrt(var)
                b = r["band_w"]
                v = ("NO CORRECTION" if abs(off) + hw <= b else
                     ("CORRECTION" if (abs(off) - hw > 0 and abs(off) >= b) else "UNRESOLVED"))
                counts[rule][v] += 1
        power[world] = {rule: {k: round(v / sims, 3) for k, v in c.items()} for rule, c in counts.items()}

    reg = {
        "experiment": "E123",
        "title": "E94's tile-spread rows it left: the dagger rows no card re-drew, and fp32 ReLU x small weights, on aifoundry3",
        "request": "Q134 (Sun 1 Nov 2026, ~19:05 PST): confirmations while the cards are free; E123 optional",
        "date": "2026-11-01",
        "registration": "tools/claims-v3/e123/E123.md",
        "card": {"host": "aifoundry3", "card": 0, "lock": "/run/lock/etsoc-shire0.lock", "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 0, "temp_threshold_c": 65}, "read_only": True},
                 "writes": "none: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no PMIC command"},
        "inputs_frozen": {k: {"path": v, "sha256": sha(v)} for k, v in SRC.items()},
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in REUSED},
                    "e123_json_sha256": sha(SRC["e123_json"]),
                    "e123_card_files_sha256": {r: sha(r) for r in CARD_FILES},
                    "desk_files_sha256": {r: sha(r) for r in DESK_FILES}},
        "plan": {"passes_planned": [12310, 12311], "smoke_pass": 12301, "items_per_pass": 54, "runs_per_pass": 74,
                 "segments": 3, "smoke_items": list(e123.SMOKE_ITEMS), "leak_primary_w_per_c": 0.1994,
                 "leak_primary_source": "E78's own fit on this card (e78.json leak.k_w_per_c 0.19940), as E121's primary",
                 "dips": "removed (E82 A2's definition), as E93, E94 and E121; dips kept is an arm",
                 "arms": ["dips_kept", "gates_off", "auto", "leak0.2414", "leak0.3803", "leak0.545", "leak0"]},
        "card_budget": {"claim_to_release_max_min": 35, "queue_budget_s_from_claim": 2100, "reserve_s": 240,
                        "first_pass_estimate_s": 760, "deadline_pass_end": "2026-11-01 23:15 PST",
                        "claim_text_hours": 1, "no_start_after": "2026-11-01 22:30 PST"},
        "classes": CLASSES,
        "rules_of_number": rules,
        "tiles": tiles,
        "bridge": bridge,
        "session_tie": tie,
        "single_pass_fallback": {"sigma_w": SIGMA_FALLBACK, "df_res": 60,
                                 "what": "with exactly one kept pass, N^2 = sigma^2 (one tile's between-pass variance, "
                                         "assumed) and every verdict is labelled 'single pass'"},
        "thresholds": {
            "R2_band_w": BAND,
            "R3": "the gate law's expected SD (desk_table_e94.gate_law_sd_w) inside tau's 95% interval: PASS; outside: FAIL",
            "R4_LF_x_w": 0.50, "R4_LI_x_w": 0.25,
            "R5": "the slope left after the frozen CV slope, class G, 95% interval contains 0: PASS; excludes 0: FAIL",
            "R6": {"pass_rms_w": 0.30, "fail_rms_w": 0.60},
            "R7": {"pass_rms_w": 0.50, "fail_rms_w": 1.00},
            "R8": {"pass_rms_w": 0.30, "fail_rms_w": 0.60},
        },
        "power": {"sims": sims, "n_passes": n_pass, "sigma_w": sig, "tau_residual_w": tres,
                  "committed_offset": "desk_table_e94.gate_law_offset_w", "R2_primary": power},
        "not_scored_if": "no pass kept (one kept pass scores with the single-pass fallback)",
    }
    out = os.path.join(HERE, "predictions-e123.json")
    json.dump(reg, open(out, "w"), indent=1)
    print(f"wrote {out}")
    for rule, r in rules.items():
        d = r["desk_table_e94"]
        print(f"{rule:16s} {r['class']:2s} k={len(r['draws'])} gc {r['committed_gate_share']:.3f} gbar {r['rule_gate_share']['mean']:.3f}"
              f" D78 {r['e78_a3']['D_w']:6.3f} beta {r['cv_slope_w_per_unit']:5.2f} law {r['gate_law_slope_w_per_unit']:6.2f}"
              f" offGL {d['gate_law_offset_w']:+.2f} sdGL {d['gate_law_sd_w']:.2f}  P(R2) {power['frozen slope true'][rule]}")
    print("bridge offsets card 1:", {k: round(v, 3) for k, v in bridge["card1_offsets_w"].items()})


if __name__ == "__main__":
    main()
