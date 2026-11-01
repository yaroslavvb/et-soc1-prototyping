#!/usr/bin/env python3
"""E89 (Q130): write predictions-e89.json, the frozen numbers of the registration (E89.md). Run once, before the claim:

    python3 tools/claims-v3/e89/make_predictions_e89.py > tools/claims-v3/e89/predictions-e89.json

Inputs, all committed: E78's switching powers (docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json
items.<type.kind>.D and .S, six passes, aifoundry3 card 0 at 600 MHz) and the lab's heat model, the Foster chain of
docs/findings/11-thermal-model.md (tau 1.5 / 4 / 60 / 150 / 400 / 2,500 s, R 0.106 / 0.050 / 0.234 / 0.136 / 0.860 /
0.081 C/W) with E78's leakage slope (0.1994 W/C) as feedback. The model predicts the die's response at the lock-in
frequency (1/60 Hz) per W of the board's fundamental; the prediction that matters is r = 1: every kind heats the die
by the same degrees per watt (E78's extrapolation S x 0.118 C/W assumes exactly that).
"""
import hashlib
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
E78 = os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")
TAU = [1.5, 4.0, 60.0, 150.0, 400.0, 2500.0]
R = [0.106, 0.050, 0.234, 0.136, 0.860, 0.081]
KLEAK = 0.1994
HALF_S, CYCLES, LEAD_S, LAUNCH_S, OVERHEAD_S = 30.0, 2, 20.0, 6.8, 0.75
BLOCKS = {"i8full": ("int8.full", "int8.zeros"), "i8gauss": ("int8.gauss_q", "int8.zeros"),
          "i8small": ("int8.smallint", "int8.zeros"), "i8sp50": ("int8.sparse50", "int8.zeros"),
          "i8neg1": ("int8.neg_ones", "int8.zeros"), "i8zero": ("int8.zeros", "idle"),
          "f32ones": ("fp32.ones", "fp32.zeros"), "f32randn": ("fp32.randn", "fp32.zeros")}


def H(f):
    w = 2 * math.pi * f
    h = sum(r / complex(1, w * t) for r, t in zip(R, TAU))
    return h / (1 - KLEAK * h)          # leakage feedback: P_leak = k T


def main():
    e78 = json.load(open(E78))["items"]
    f = 1 / (2 * HALF_S)
    h = H(f)
    h0 = H(1e-9)
    # the compute share of a half (launches of <= 6.8 s each with ~0.75 s start-up), as the runner schedules them
    duty = (4 * LAUNCH_S if HALF_S >= 4 * (LAUNCH_S + OVERHEAD_S) - 0.01 else (HALF_S - 4 * OVERHEAD_S)) / HALF_S
    blocks = {}
    for b, (k, z) in BLOCKS.items():
        key = "S" if z == "idle" else "D"
        w = e78[k][key]["mean"]
        pf = (2 / math.pi) * w * duty
        blocks[b] = {"kind": k, "ref": z, "e78_quantity": key, "e78_w": round(w, 4),
                     "e78_ci95": round(e78[k][key]["ci95"], 4),
                     "e78_dT_win_2s": round(e78[k]["dT_win"]["mean"], 3),
                     "e78_extrapolation_C": round(0.118 * e78[k]["S"]["mean"], 3),
                     "pred_board_fund_W": round(pf, 3), "pred_T_fund_C": round(abs(h) * pf, 3),
                     "pred_r": 1.0}
    lib = hashlib.sha256(open(os.path.join(ROOT, "tools/claims-v3/lib.sh"), "rb").read()).hexdigest()
    out = {
        "experiment": "E89", "card": "aifoundry3 card 0 (600 MHz, pinned by its boot-time TDP 0; never set)",
        "registration": "tools/claims-v3/e89/E89.md",
        "harness": {"lib_sh_sha256": lib, "data_dir": "docs/reports/data/2026-10-31-e89-heat-low-power/",
                    "passes": [8910, 8911], "smoke": 8901, "card_budget_min": 45,
                    "half_s": HALF_S, "cycles": CYCLES, "lead_s": LEAD_S, "launch_s": LAUNCH_S, "idle_s": 15.0,
                    "gate_c": 62.0, "gate_max_s": 60.0, "max_c": 78.0, "sampler": "tools/claims-v3/e89/pvt_sample.py",
                    "order": "the seven low-power blocks shuffled with Random('E89|aifoundry3|<pass>'), then f32randn"},
        "model": {"source": "docs/findings/11-thermal-model.md (Foster chain) + E78 leak 0.1994 W/C",
                  "f_lockin_hz": f, "H_lockin_C_per_W": round(abs(h), 4),
                  "H_lockin_phase_deg": round(math.degrees(math.atan2(h.imag, h.real)), 1),
                  "H_dc_C_per_W": round(abs(h0), 3), "duty": round(duty, 4),
                  "e78_resolved_2s_C_per_W": 0.118},
        "blocks": blocks,
        "rules": {
            "E89-R0": {"what": "the per-sensor reading works: command 74 group 0 answers 34 sensors, and the floor of "
                               "their mean is the firmware's own minshire_avg",
                       "min_share_with_34": 0.99, "min_share_eq": 0.95, "pred": "PASS"},
            "E89-R1": {"what": "every block's temperature fundamental (34-sensor mean, on the reference lag) is "
                               "detected: 95% lower bound over laps > 0", "pred": "PASS for all 8"},
            "E89-R2": {"what": "heat follows switching power: r = H_K / H_ref inside the band at 95% (laps, delta "
                               "method, t(0.975, min(n) - 1))", "band": [0.80, 1.25], "pred": "PASS for all 7"},
            "E89-R3": {"what": "the reference's H at 1/60 Hz against the heat model's",
                       "band": [round(0.75 * abs(h), 3), round(1.40 * abs(h), 3)], "pred": "PASS"},
            "E89-R4": {"what": "E78's 2 s window, now on the fine reading: (step2/W)_K over (step2/W)_ref inside the "
                               "band at 95% (over the K halves' up-steps)", "band": [0.70, 1.43], "pred": "PASS for all 7"},
        },
    }
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
