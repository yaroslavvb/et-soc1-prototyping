#!/usr/bin/env python3
"""E121 (Q134): write predictions-e121.json, the frozen numbers of E93's zero-gate tests replicated on a second card
(aifoundry3 card 0, 600 MHz). Every number is read from a committed file named below (each checked by sha256), copied or
computed, never retyped. Registration: E121.md beside this file.

    python3 tools/claims-v3/e121/make_predictions_e121.py            # writes predictions-e121.json
    python3 tools/claims-v3/e121/make_predictions_e121.py --check    # recomputes and compares, writes nothing

What it freezes:
  * the 24 gate rules of E93 (predictions-e93.json > rules), contrasts and lines unchanged; where E93 subtracted a fixed
    E82 number of card 1, E121 subtracts E78's number for the same cell on aifoundry3 (e78.json > items > <cell> > D);
  * the session tie: E78's cells on aifoundry3 with E93's bands (E93 tied to E82's cells on card 1 the same way);
  * the cross-card rules X-<rule>: E93's measured contrast (scored.json > primary > rules > <id> > contrast) times E82's
    per-type card scale (E82 scored.json > cross_card > primary > x3 > per_type_median, aifoundry3 over card 1), with a
    tolerance w of 0.75 W (fp32, fp16) or 0.50 W (int8);
  * E93's verdicts, the int8 pairing reading it named, its tiles' D (reported beside, never a band here);
  * the power of the X rules by simulation (normal per-pass contrasts at E93's own per-pass sd, 20,000 sessions).
Standard library only.
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "predictions-e121.json")

SOURCES = {
    "e93_predictions": ("tools/claims-v3/kinds/predictions-e93.json", "d470f6a9",
                        "020bb188f011147292525e6a6decb2c491ffb54e1c200069a0c27ccb6c0f8387"),
    "e93_scored": ("docs/reports/data/2026-11-01-e93-zero-gate-silicon/scored.json", "9105d764",
                   "20b19340d9e0cff24461697de99908e2cd5e53563a4b56442a4c896e044da437"),
    "e93_reduction": ("docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json", "9105d764",
                      "04ec3a93b6a382985a50c217bfa3cd6b082b6d183315c7b2e177e90573461c1a"),
    "e78_reduction": ("docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json", "410c56f6",
                      "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5"),
    "e82_scored": ("docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json", "0a041356",
                   "498d5c70f01778248c7800d7d1d7e07b033db35f29b897d40f5a21787bef0b53"),
    "e95_nodips": ("docs/reports/data/2026-11-01-e95-real-tensors-energy/dips-arm/e95-nodips.json", "ab23b1aa",
                   "4e5c1048dfb300d8902c39cc1a86b1789283d749855468a47c87fc5159137603"),
}
# the card code E121 runs unchanged (E78's and E93's freezes), and the desk code it reuses unchanged
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json",
             "tools/claims-v3/kinds/e93_common.py", "tools/claims-v3/kinds/run_e93.py",
             "tools/claims-v3/kinds/block_e93.sh", "tools/claims-v3/kinds/predictions-e93.json",
             "tools/claims-v3/kinds/e93/e93.json"]
DESK_CODE = ["tools/claims-v3/kinds/reduce_e93.py", "tools/claims-v3/kinds/score_e93.py",
             "tools/claims-v3/kinds/make_e93.py"]
E121_FILES = ["tools/claims-v3/e121/run_e121.sh", "tools/claims-v3/e121/queue_e121.sh",
              "tools/claims-v3/e121/score_e121.py", "tools/claims-v3/e121/collect_e121.sh",
              "tools/claims-v3/e121/selftest_e121.py", "tools/claims-v3/e121/make_predictions_e121.py"]

TYPE_OF_RULE = {"R6a": "int8", "R6b": "int8", "R6c": "int8", "R7": "int8", "R8": "fp32", "R5-fp32": "fp32"}
W_X = {"fp32": 0.75, "fp16": 0.75, "int8": 0.50}
GATE_RULES = ["R1-fp32-both", "R1-fp32-a", "R1-fp32-b", "R1-fp16-both", "R1-fp16-a", "R1-fp16-b", "R2-fp32", "R2-fp16",
              "R3-fp32-one", "R3-fp32-both", "R3-fp32-a", "R3-fp32-b", "R3-fp16-both", "R3-fp16-a",
              "R4-fp32-both", "R4-fp32-a", "R4-fp16-both", "R4-fp16-a", "R6a", "R6b", "R6c", "R7"]
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(key):
    rel, commit, want = SOURCES[key]
    have = sha(rel)
    if have != want:
        raise SystemExit(f"{rel}: sha256 {have} != the one this freeze was written from ({want})")
    return json.load(open(os.path.join(ROOT, rel)))


def rule_type(rid, a):
    return TYPE_OF_RULE.get(rid) or a.split(".")[0]


def sim_x(e93_mean, e93_h, s, sd, w, delta, n, rng, N=20000):
    """P(PASS, FAIL, INCONCLUSIVE) of one X rule: E121's per-pass contrasts ~ Normal(s*e93_mean + delta, sd), n passes."""
    p = f = 0
    tq = T95[n - 1]
    for _ in range(N):
        v = [rng.gauss(s * e93_mean + delta, sd) for _ in range(n)]
        m = sum(v) / n
        sdv = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
        h = math.sqrt((tq * sdv / math.sqrt(n)) ** 2 + (s * e93_h) ** 2)
        d = m - s * e93_mean
        if abs(d) + h <= w:
            p += 1
        elif abs(d) - h > w:
            f += 1
    return round(p / N, 3), round(f / N, 3), round(1 - (p + f) / N, 3)


def build():
    p93 = load("e93_predictions")
    s93 = load("e93_scored")
    r93 = load("e93_reduction")
    e78 = load("e78_reduction")
    e82 = load("e82_scored")
    e95 = load("e95_nodips")
    scale = e82["cross_card"]["primary"]["x3"]["per_type_median"]
    prim = s93["primary"]

    rules = []
    for r in p93["rules"]:
        r2 = dict(r)
        if r.get("fixed"):
            cell = r["fixed"]["e82"]
            d = e78["items"][cell]["D"]
            r2["fixed"] = {"e78": cell, "value_w": round(d["mean"], 4), "ci95_w": round(d["ci95"], 4),
                           "source": SOURCES["e78_reduction"][0] + f" > items > {cell} > D (aifoundry3, 31 Oct, E78's primary)",
                           "e93_used": {"e82": cell, "value_w": r["fixed"]["value_w"]}}
            if r["id"] == "R2-fp16":
                r2["what"] = "the same in fp16, against E78's constant on this card"
        rules.append(r2)

    tie = {}
    for cell, e in p93["e82_reference"].items():
        d = e78["items"][cell]["D"]
        tie[cell] = {"D_w": round(d["mean"], 4), "ci95_w": round(d["ci95"], 4), "band_w": e["band_w"],
                     "e93_band_from": "predictions-e93.json > e82_reference"}
    e95_beside = {n: {"D_w": round(e95["items"][n]["D"]["mean"], 4), "ci95_w": round(e95["items"][n]["D"]["ci95"], 4)}
                  for n in ("anchor_pi", "fp32.randn", "fp16.randn", "int8.full")}

    xr = []
    rng = random.Random("E121|power")
    for r in p93["rules"]:
        rid = r["id"]
        c = prim["rules"][rid]["contrast"]
        ty = rule_type(rid, r["a"])
        s = scale[ty]
        pp = c["per_pass"]
        m = sum(pp) / len(pp)
        sd = math.sqrt(sum((x - m) ** 2 for x in pp) / (len(pp) - 1))
        w = W_X[ty]
        power = {}
        for n in (3, 4, 5):
            for delta in (0.0, 0.5, 1.0, 1.5):
                power[f"n{n}_delta{delta}"] = sim_x(c["mean"], c["ci95"], s, s * sd, w, delta, n, rng, N=4000)
        xr.append({"id": f"X-{rid}", "of": rid, "type": ty, "scale": s,
                   "e93": {"mean": round(c["mean"], 4), "ci95": round(c["ci95"], 4), "n": c["n"],
                           "per_pass_sd": round(sd, 4), "verdict": prim["rules"][rid]["verdict"]},
                   "predicted_w": round(s * c["mean"], 4), "w": w, "test": "within",
                   "power_pass_fail_inconclusive": power})

    # aggregate power at true delta 0 for every rule (independent rules: an approximation)
    agg = {}
    for n in (3, 4, 5):
        k = f"n{n}_delta0.0"
        P = [x["power_pass_fail_inconclusive"][k] for x in xr]
        rng2 = random.Random(f"E121|agg|{n}")
        ok = bad = 0
        N = 20000
        for _ in range(N):
            npass = nfail = 0
            for (pp_, pf_, pi_) in P:
                u = rng2.random()
                if u < pp_:
                    npass += 1
                elif u < pp_ + pf_:
                    nfail += 1
            if nfail == 0 and npass >= 12:
                ok += 1
            elif nfail >= 3:
                bad += 1
        agg[f"n{n}"] = {"P_aggregate_PASS": round(ok / N, 3), "P_aggregate_FAIL": round(bad / N, 3)}

    tiles = {}
    for n, v in prim["tiles"].items():
        ty = n.split(".")[0]
        tiles[n] = {"e93_D_w": round(v["D"]["mean"], 4), "e93_ci95_w": round(v["D"]["ci95"], 4),
                    "scaled_w": round(scale[ty] * v["D"]["mean"], 4), "e93_band_verdict": v["verdict"]}
    for n in ("fp32.sparse50", "fp32.a_zeros_b_randn", "anchor_pi", "fp32.randn", "fp32.zeros", "fp16.randn",
              "fp16.zeros", "int8.a_zeros_b_full", "int8.full", "int8.zeros"):
        d = r93["items"][n]["D"]
        ty = "fp32" if n == "anchor_pi" else n.split(".")[0]
        tiles.setdefault(n, {"e93_D_w": round(d["mean"], 4), "e93_ci95_w": round(d["ci95"] or 0.0, 4),
                             "scaled_w": round(scale[ty] * d["mean"], 4), "e93_band_verdict": None})

    reg = {
        "experiment": "E121",
        "registration": "tools/claims-v3/e121/E121.md",
        "registered": "2026-11-01",
        "answers": "the kinds page's section 11 (https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "
                   "the closed list's 'The zero gate on silicon' (old item 4): closed at power resolution on one card",
        "card": {"name": "aifoundry3", "device": 0, "clock_mhz": 600, "mv_expected": round(e78["v_mean"] * 1000, 1),
                 "config_expected": {"tdp_w": 0, "temp_threshold_c": 65},
                 "lock": "/run/lock/etsoc-shire0.lock", "V3_DEVICE": None},
        "inputs_frozen": {k: {"path": v[0], "commit": v[1], "sha256": v[2]} for k, v in SOURCES.items()},
        "harness": {
            "card_code_unchanged_sha256": {r: sha(r) for r in CARD_CODE},
            "desk_code_unchanged_sha256": {r: sha(r) for r in DESK_CODE},
            "e121_files_sha256": {r: sha(r) for r in E121_FILES if os.path.exists(os.path.join(ROOT, r))
                                  and not r.endswith("make_predictions_e121.py")},
            "order": "e93_common.pass_order unchanged: Random('E93|aifoundry3|<pass>'), the tie, three segments of "
                     "E78's six anchors and seven, seven and six of E93's twenty items, the tie; two burn-ins",
        },
        "passes": {"smoke": 12101, "dry": 12100, "planned": [12110, 12111, 12112, 12113, 12114],
                   "min_kept_passes": 3, "min_cell_passes": 3, "runs_per_pass": 40},
        "primary": {"leak_w_per_c": 0.1994, "dips": "removed (E82 A2's definition)",
                    "reduction": "tools/claims-v3/kinds/reduce_e93.py unchanged: reduce_e78.py with E93's items; on "
                                 "aifoundry3 its card-1 config substitution never fires (the card reads 0/65, which "
                                 "E78's gate accepts as it stands); --leak 0.1994, E78's own fit on this card",
                    "arms": {"dips_kept": ["--keep-dips", "--leak", "0.1994", "--no-refit"],
                             "auto": ["--leak", "auto", "--no-refit"],
                             "leak0.2414": ["--leak", "0.2414", "--no-refit"],
                             "leak0.3803": ["--leak", "0.3803", "--no-refit"],
                             "leak0.545": ["--leak", "0.545", "--no-refit"],
                             "leak0": ["--leak", "0", "--no-refit"]}},
        "rules": rules,
        "gate_rules": GATE_RULES,
        "gate_summary": "PASS if every one of the 22 gate rules PASSes; FAIL if any FAILs; else INCONCLUSIVE "
                        "(UNRESOLVED or NOT SCORED rules make it INCONCLUSIVE / NOT SCORED)",
        "e93_verdicts": {rid: v["verdict"] for rid, v in prim["rules"].items()},
        "e93_pairing_reading": prim["pairing_reading"],
        "e78_reference": tie,
        "e95_beside": {"source": SOURCES["e95_nodips"][0] + " (aifoundry3, 1 Nov 00:49-01:22 PDT, dips removed, "
                                 "leakage auto 0.299): reported beside the tie, never a verdict", "cells": e95_beside},
        "card_scale": {"per_type": scale, "source": SOURCES["e82_scored"][0] + " > cross_card > primary > x3 > "
                                                     "per_type_median (D on aifoundry3 over D on card 1, 32 kinds >= 5 W)",
                       "median": e82["cross_card"]["primary"]["x3"]["median_ratio"],
                       "iqr": e82["cross_card"]["primary"]["x3"]["iqr"]},
        "cross_card": {"rules": xr, "w_w": W_X,
                       "verdict": "per rule: d = C121 - s*C93, h = sqrt(h121^2 + (s*h93)^2); PASS if |d| + h <= w, FAIL "
                                  "if |d| - h > w, else INCONCLUSIVE; UNRESOLVED if C121 has fewer than 3 passes",
                       "aggregate": "PASS if no X rule FAILs and at least 12 of 24 PASS; FAIL if 3 or more FAIL; else "
                                    "INCONCLUSIVE",
                       "aggregate_power_true_delta0": agg},
        "tiles_e93": tiles,
        "prices_e93_card1": {"F_w": p93["prices"]["F_w"], "note": "E88's clocked lane on card 1, echoed by "
                                                                   "score_e93.reported only; not a prediction here"},
        "budget": {"card_minutes": 35, "anchor": "the claim edit's time (E121_T0)", "queue_budget_s": 2100,
                   "reserve_s": 120, "first_pass_estimate_s": 450, "gap_s": 15,
                   "deadline": "2026-11-01 23:15 PST", "claim_hold": "for 1 h"},
    }
    return reg


def main():
    reg = build()
    txt = json.dumps(reg, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        old = open(OUT).read()
        a, b = json.loads(old), json.loads(txt)
        for k in ("harness",):
            a.pop(k, None), b.pop(k, None)
        print("predictions-e121.json reproduces (harness hashes aside):", a == b)
        sys.exit(0 if a == b else 1)
    open(OUT, "w").write(txt)
    print("wrote", OUT, hashlib.sha256(txt.encode()).hexdigest())
    for x in reg["cross_card"]["rules"]:
        pw = x["power_pass_fail_inconclusive"]
        print(f"{x['id']:16s} e93 {x['e93']['mean']:+8.3f} ± {x['e93']['ci95']:.3f} sd {x['e93']['per_pass_sd']:.3f} "
              f"pred {x['predicted_w']:+8.3f} w {x['w']}  n4 d0 {pw['n4_delta0.0']}  n4 d1 {pw['n4_delta1.0']}")
    print("aggregate:", reg["cross_card"]["aggregate_power_true_delta0"])


if __name__ == "__main__":
    main()
