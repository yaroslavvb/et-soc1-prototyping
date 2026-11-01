#!/usr/bin/env python3
"""E95 (Q132): write predictions-e95.json, the lane's freeze, from committed sources only. Every number is read from the
file it names, never retyped. E95 makes NO new prediction of its own: each tile's predictions and the claims C1-C12 are
Q132(r)'s, frozen in real2/predictions-real2.json (sha256 0957e0c2...), which this file only cites by sha256. What this
file adds is the lane's plan, the harness's sha256 and the reference cells of the reported session tie.

    /usr/local/bin/python3.12 tools/claims-v3/kinds/make_predictions_e95.py      # writes predictions-e95.json
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e78_common as ec  # noqa: E402
import e95_common as e95  # noqa: E402

E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E86_JSON = "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json"
E86_SCORED = "docs/reports/data/2026-10-31-e86-real-tensors-energy/scored.json"
K = "tools/claims-v3/kinds"
REUSED = ("tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json")
BOX_FILES = (f"{K}/e95_common.py", f"{K}/run_e95.py", f"{K}/reduce_e95.py", f"{K}/block_e95.sh", f"{K}/queue_e95.sh", f"{K}/run_e95.sh")
# E78's cells a reader wants beside these tiles (reported, never a verdict)
E78_BESIDE = ("fp32.randn", "fp16.randn", "int8.full", "fp32.zeros", "fp16.zeros", "int8.zeros", "anchor_pi", "fp32.bf16trunc",
              "fp32.fp16grid", "fp32.nn_like", "fp16.nn_like", "int8.gauss_q", "fp32.sparse50", "fp16.sparse50", "int8.sparse50",
              "fp32.a_randn_b_zeros", "fp32.a_zeros_b_randn", "fp16.a_randn_b_zeros", "fp16.a_zeros_b_randn")
TIE_BAND = {"fp32.randn": 0.50, "fp16.randn": 0.50, "anchor_pi": 0.50, "int8.full": 0.25}     # E86-R5's bands, the same cells
E86_TIE_BAND = {"fp16.real_l6_mlp_down": 0.50, "fp16.real_l6_attn_qk": 0.50, "int8.real_l6_mlp_down": 0.50}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    e78 = json.load(open(os.path.join(ROOT, E78_JSON)))
    e86 = json.load(open(os.path.join(ROOT, E86_SCORED)))
    frozen = json.load(open(e95.FROZEN_JSON))
    pe86 = json.load(open(os.path.join(HERE, "predictions-e86.json")))
    if frozen.get("real2_json_sha256") != e95.REAL2_JSON_SHA256:
        raise SystemExit("real2.json's sha256 in predictions-real2.json differs from e95_common's")
    D78 = {n: v["D"] for n, v in e78["items"].items()}
    tie = {n: {"D_w": round(D78[n]["mean"], 4), "ci95_w": round(D78[n]["ci95"], 4), "ref": "E78", "band_w": b,
               "source": f"{E78_JSON} items.{n}.D.mean"} for n, b in TIE_BAND.items()}
    for n, b in E86_TIE_BAND.items():
        tie[n] = {"D_w": round(e86["tiles"][n]["D"]["mean"], 4), "ci95_w": round(e86["tiles"][n]["D"]["ci95"], 4), "ref": "E86", "band_w": b,
                  "source": f"{E86_SCORED} tiles.{n}.D.mean"}
    tier1 = [k for k, v in frozen["tiles"].items() if v["tier"] == 1]
    tier2 = [k for k, v in frozen["tiles"].items() if v["tier"] == 2]
    if sorted(tier1) != sorted(frozen["e95_suggested"]["tier1"]) or sorted(tier2) != sorted(frozen["e95_suggested"]["tier2"]):
        raise SystemExit("the frozen tiers differ from e95_suggested")
    reg = {
        "experiment": "E95", "title": "more real tensors' energy, and exact zeros letting the gate act (aifoundry3 card 0, 600 MHz)",
        "request": "Q132, item 3 of the kinds page's section 11", "date": "2026-11-01",
        "registration": f"{K}/E95.md", "card": "aifoundry3 card 0",
        "predictions_and_claims": f"{K}/real2/predictions-real2.json: tiles.*, gate_law, known_misses and claims.E95 (C1-C12), unchanged; E95 adds no prediction",
        "inputs_frozen": {
            "predictions_real2": {"path": f"{K}/real2/predictions-real2.json", "sha256": sha(f"{K}/real2/predictions-real2.json")},
            "real2_json": {"path": f"{K}/real2/real2.json", "sha256": sha(f"{K}/real2/real2.json")},
            "real_json": {"path": f"{K}/real/real.json", "sha256": sha(f"{K}/real/real.json")},
            "predictions_e86": {"path": f"{K}/predictions-e86.json", "sha256": sha(f"{K}/predictions-e86.json")},
            "e78_reduction": {"path": E78_JSON, "sha256": sha(E78_JSON)},
            "e86_reduction": {"path": E86_JSON, "sha256": sha(E86_JSON)},
            "e86_scored": {"path": E86_SCORED, "sha256": sha(E86_SCORED)},
        },
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in REUSED},
                    "e95_files_sha256": {r: sha(r) for r in BOX_FILES},
                    "real2_json_sha256": sha(f"{K}/real2/real2.json")},
        "plan": {"passes": [9510, 9511, 9512, 9513], "smoke": 9501, "runs_per_pass": 53, "min_kept_passes": 3,
                 "items_per_pass": "the tie twice, E78's six anchors three times, the 25 tier-1 and 5 tier-2 real2 tiles and E86's three once",
                 "smoke_items": list(e95.SMOKE_ITEMS)},
        "card_budget": {"card_minutes_max": 45, "queue_budget_min": 41, "queue_deadline": "2026-11-01 06:45 PST", "every_run_ends_by": "07:15 PST"},
        "items": {"tier1_new": tier1, "tier2_new": tier2, "e86_partners": list(e95.E86_NAMES),
                  "e86_partner_frozen_points_w": {n: pe86["tiles"][n]["D_frozen_w"] for n in e95.E86_NAMES}},
        "anchors": list(ec.ANCHORS), "tie": ec.TIE,
        "leakage": {"primary": "auto", "arms": [0.1994, 0.3803, 0]},
        "session_tie": tie,
        "e78_beside": {n: {"D_w": round(D78[n]["mean"], 4), "ci95_w": round(D78[n]["ci95"], 4)} for n in E78_BESIDE if n in D78},
        "not_scored_if": "fewer than 3 kept passes: every frozen claim reads NOT SCORED (claims.conventions). The registered dips-removed "
                         "arm (posthoc_dips_e95.py, E86's method) is then the reading reported, labelled as that arm; it is always "
                         "reported beside, and it moves no verdict of the primary",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e95.json"), "w"), indent=1)
    print("sha256 predictions-e95.json", hashlib.sha256(open(os.path.join(HERE, "predictions-e95.json"), "rb").read()).hexdigest())
    print("missing E78 cells:", [n for n in E78_BESIDE if n not in D78])
    for r, v in reg["harness"]["e95_files_sha256"].items():
        print(v[:12], r)


if __name__ == "__main__":
    main()
