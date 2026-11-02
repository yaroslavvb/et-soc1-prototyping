#!/usr/bin/env python3
"""E132: the frozen predictions, bands and decision constants, written before any E132 pass (predictions.json).

    python3 tools/claims-v3/e132/make_predictions_e132.py <lab repo root> > tools/claims-v3/e132/predictions.txt
        (writes tools/claims-v3/e132/predictions.json)

Every number comes from a committed file of E110 or E99, named beside it:
  * the session ties (R1): E110's headline contrasts on byte-identical images and commands (e110.json headline.contrasts.board);
  * the channel rung (R2): E110's prices per toggled bit with each path's line-to-line edge counted (e110.json
    verdicts.prices_pJ_per_toggled_bit.W_cyclic: 64 bits; verdicts.R4_half_line.c256.pJ_per_bit_if_line_edges_count: 256 bits) and
    its pin-toggle price (V16 / 496 / line rate), applied to the counts ab_4 adds over ab_3 on one channel (make_e132.py --check:
    128 bits a line on a 256-bit path, 32 on a 64-bit path, 8 pin toggles);
  * the encoded part on the DDR die rail (R3, R6): E110's die-rail readings (e110.json headline.over_zeros.ddr_mv) and its post-hoc
    ordering (README reading 4, labelled post hoc there), which puts raw and encoded 64-bit toggles on one count;
  * the encoded part on the board (R4): E110's encoded wide-path residuals by its registration's formula (ew-readme-formula.json, D1);
  * the rails' steps (R5): E99's per-rail period ladder (tools/claims-v3/e110/desk/e99_ladder_ways.txt "steps:", post hoc, labelled
    there), mapped rung by rung: L4-L2 -> R_1, L8-L4 -> R_2, L16-L8 -> R_3, L32-L16 -> R_4, L8192-L32 -> R_wide. E99's rungs also
    raised every finer path's count, which is why they could not separate interleaves; this freezes what its steps say, to be scored.
"""
import json
import os
import re
import sys

ROOT = sys.argv[1]
E110 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e110-memory-width")
d = json.load(open(os.path.join(E110, "e110.json")))
ew = json.load(open(os.path.join(E110, "ew-readme-formula.json")))
LR = d["headline"]["lines_per_s"]["dram"]
B = d["headline"]["contrasts"]["board"]
OZ = d["headline"]["over_zeros"]

# ---- R1: the session's tie to E110
ties = {"S64": B["S64"]["mean"], "S128": B["S128"]["mean"], "V16": B["V16"]["mean"], "V64": B["V64"]["mean"],
        "V128": B["V128"]["mean"], "U4z": OZ["board"]["dm_u4"]["mean"]}

# ---- R2: the channel rung, priced by E110's line-edge prices
pin_pJ = B["V16"]["mean"] / 496 / LR * 1e12
p64_cyc = d["verdicts"]["prices_pJ_per_toggled_bit"]["W_cyclic"]["64"]
p256_cyc = d["verdicts"]["R4_half_line"]["c256"]["pJ_per_bit_if_line_edges_count"]
p256_within = d["verdicts"]["R4_half_line"]["c256"]["pJ_per_bit"]
edges_W = (128 * p256_cyc + 32 * p64_cyc + 8 * pin_pJ) * LR / 1e12
no_edges_W = 8 * pin_pJ * LR / 1e12


# ---- R4: E110's encoded residuals by the registration's formula (D1), primary arm (the e110.json entry)
EWF = {k: ew["e110.json"][k]["readme_formula"]["mean"] for k in ("E64", "E128", "E256")}

# ---- R5: E99's per-rail period steps
STEPS = {}
for line in open(os.path.join(ROOT, "tools/claims-v3/e110/desk/e99_ladder_ways.txt")):
    if line.split() and line.split()[0] in ("board", "noc", "sram", "minion", "off"):
        cur = line.split()[0]
    if line.strip().startswith("steps:"):
        STEPS[cur] = {m.group(1): (float(m.group(2)), float(m.group(3)))
                      for m in re.finditer(r"(L\d+-L\d+) ([+-][0-9.]+)±([0-9.]+)", line)}
MAP = {"L4-L2": "R_1", "L8-L4": "R_2", "L16-L8": "R_3", "L32-L16": "R_4", "L8192-L32": "R_wide"}
RAIL_T = {"board": 0.10, "noc": 0.03, "sram": 0.03, "minion": 0.03, "off": 0.10}


def cls(mean, half, t):
    lo, hi = mean - half, mean + half
    if mean >= t and lo > 0:
        return "present"
    if mean <= -t and hi < 0:
        return "negative"
    if lo >= -t and hi <= t:
        return "absent"
    return "unresolved"


r5 = {rail: {MAP[k]: {"E99_step": k, "E99_W": v[0], "E99_half_W": v[1], "class": cls(v[0], v[1], RAIL_T[rail])}
             for k, v in STEPS[rail].items()} for rail in STEPS}

pred = {
    "exp": "E132",
    "line_rate_dram_E110": LR,
    "sources": {"e110": "docs/reports/data/2026-11-01-e110-memory-width/e110.json",
                "e110_formula": "docs/reports/data/2026-11-01-e110-memory-width/ew-readme-formula.json",
                "e99_steps": "tools/claims-v3/e110/desk/e99_ladder_ways.txt"},
    "prediction": {
        "ties_W": ties,
        "R2": {"reading": "EDGES", "edges_W": edges_W, "no_edges_W": no_edges_W,
               "prices_pJ": {"pin": pin_pJ, "p64_line_edges": p64_cyc, "p256_line_edges": p256_cyc, "p256_within_line": p256_within},
               "counts_per_line": {"p256": 128, "p64": 32, "pins": 8},
               "where": "off every metered rail (E99: L32-L16 off +0.162 W, NoC -0.004, SRAM +0.011)"},
        "R3": {"reading": "ENCODED", "classes": {"eh_64z": "moves", "el_64z": "still", "RE64": "moves", "wl_64z": "moves"},
               "E110_ddr_mV_over_zeros": {k: OZ["ddr_mv"][k]["mean"] for k in ("wl_64", "vl_64", "wl_128", "vl_128", "dm_u4", "dm_l08")},
               "reported": {"RE128": "moves", "vl_64z": "moves"}},
        "R4": {"reading": "PAYS", "E56_W": EWF.get("E64"), "E448_W": EWF.get("E64"), "E192_W": EWF.get("E128")},
        "R5": r5,
        "R6": {"classes": {"RH64": "still", "RH128": "still"}, "high_pin_pJ_E99": 1.47,
               "Hp_W": 192 * 1.47 * LR / 1e12},
    },
    "decision": {
        "tie_within_W": 0.30,
        "board_present_W": 0.10, "board_absent_half_W": 0.10,
        "rail_threshold_W": RAIL_T,
        "ddr_moves_mV": 0.30, "ddr_still_half_mV": 0.30,
        "rails_on_none_half_W": 0.10,
        "warmup_pass": 13210, "min_headline_passes": 3,
        "budget_card_min": 40, "deadline_after_session_start_min": 36,
    },
}
json.dump(pred, open(os.path.join(ROOT, "tools/claims-v3/e132/predictions.json"), "w"), indent=1, sort_keys=True)
print("E132 frozen predictions (from committed E110 and E99 files)")
print("line rate %.5e lines/s (E110)" % LR)
print("R1 ties, W:", json.dumps({k: round(v, 4) for k, v in ties.items()}))
print("R2: pin %.3f pJ, 64-bit with line edges %.3f pJ, 256-bit with line edges %.3f pJ (within-line %.3f)" % (pin_pJ, p64_cyc, p256_cyc, p256_within))
print("R2: EDGES predicts R_4 = +%.3f W; NO-EDGES predicts +%.3f W (the pins alone)" % (edges_W, no_edges_W))
print("R3: E110's die rail over zeros, mV:", json.dumps({k: round(v, 3) for k, v in pred["prediction"]["R3"]["E110_ddr_mV_over_zeros"].items()}))
print("R4: E56 and E448 predicted %s W (E110's E64, the registration's formula), E192 %s W (E128)" % (EWF.get("E64"), EWF.get("E128")))
print("R6: 192 high pins at E99's 1.47 pJ = %.3f W" % pred["prediction"]["R6"]["Hp_W"])
for rail, rr in r5.items():
    print("R5 %-6s" % rail, " ".join("%s %s(%+.3f±%.3f)" % (k, v["class"], v["E99_W"], v["E99_half_W"]) for k, v in sorted(rr.items())))
