#!/usr/bin/env python3
"""E120's frozen predictions and decision rules, from E77's committed data (its post hoc per-hart lines, operating-point
step and offset fit) and E77's registered rules where they carry over.

    python3 tools/claims-v3/e120/predict_e120.py > tools/claims-v3/e120/predictions.json

Nothing here is fitted to E120's data; it is written and committed before the claim and the first launch.
"""
import hashlib
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
E77 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e77-rail-one-temperature")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ph = json.load(open(os.path.join(E77, "posthoc.json")))
    A, B = ph["A"], ph["B"]
    arm_a = [992, 736, 512, 256]
    arm_b = [416, 288, 160, 32]
    pa = [A["intercept_w"] + A["mW_per_hart"] / 1000 * h for h in arm_a]
    pb = [B["intercept_w"] + B["mW_per_hart"] / 1000 * h for h in arm_b]
    fo = ph["fit_offset"]
    pred = {
        "experiment": "E120",
        "frozen": "before the claim and the first launch (the commit that adds this file)",
        "sources": {"E77 posthoc.json": sha(os.path.join(E77, "posthoc.json")),
                    "E77 results.json": sha(os.path.join(E77, "results.json")),
                    "E77 corrections-check.txt": sha(os.path.join(E77, "corrections-check.txt")),
                    "lines": "posthoc.json A, B: each arm's minion-rail delta over its pre-launch idle against harts "
                             "(arm A 600 MHz, arm B 800 MHz; both idles at 600 MHz)",
                    "arm_a_line": {"intercept_w": A["intercept_w"], "mw_per_hart": A["mW_per_hart"]},
                    "arm_b_line": {"intercept_w": B["intercept_w"], "mw_per_hart": B["mW_per_hart"]}},
        "rungs": [{"rung": i + 1, "arm_a_harts": arm_a[i], "arm_a_minion_w": round(pa[i], 2),
                   "arm_b_harts": arm_b[i], "arm_b_minion_w": round(pb[i], 2),
                   "mismatch_pct": round(100 * (pb[i] - pa[i]) / pa[i], 1)} for i in range(4)],
        "design_note": "arm B's harts re-cut so that 3.752 + 0.04049*N matches arm A's -0.343 + 0.02105*N on the "
                       "minion rail's watts over the common 600 MHz idle, i.e. on the total minion-rail power in the "
                       "window, which sets the regulator's current at each arm's voltage",
        "V_verdict": {
            "model": "offrail = a_m*dminion + c_B*[arm B] + R_eff*[((m0 + dminion)/V)^2 - (m0/V0)^2], no other "
                     "intercept, deltas over each launch's own pre-launch idle, drift_split footing (E77's reading "
                     "unchanged). c_B is the off-rail part of the 800 MHz operating point's step that a_m does not "
                     "carry: E77 measured that step post hoc (4.09 W minion, 1.73 W SRAM) and this registers its fit",
            "unit": "per pass k: the rung means of arm A pass k and arm B pass k (8 points, 3 coefficients); the unit "
                    "of replication is the pass; 99% interval = mean +- t(0.995, n-1) * SD/sqrt(n) over passes",
            "PASS": "R_eff's 99% interval excludes 0 AND the pooled fit over every rung mean has an rms at least 30% "
                    "below the same fit without R_eff (E77's rule, unchanged)",
            "NEITHER": "the interval excludes 0 but the rms improves by less than 30%: 'R_eff resolved, not a "
                       "material term'",
            "FAIL": "the interval contains 0. A FAIL is a result: the bound B below is then what the run says",
            "expected_from_E77_posthoc_not_a_rule": {"per_pass_R_mohm": [fo["per_pass"][k]["R_mohm"] for k in
                                                                       ("1", "2", "3")],
                                                     "ci99_mohm": fo["R_ci99_mohm"],
                                                     "note": "E77's three passes in this form (post hoc); no size "
                                                             "or sign of R_eff is frozen as a prediction"}},
        "B_bound": {
            "what": "the conduction loss a 21 W minion-rail step adds, in the registered model's total-current form, "
                    "at the 99% interval's upper edge: R_hi*[((m0_A + 21)/V_A)^2 - (m0_A/V_A)^2], m0_A = arm A's "
                    "measured idle minion rail (mean of its kept launches), V_A its mean window voltage; as pJ of the "
                    "0.875 pJ row, pJ = W x 0.875 / (0.188 x 21). The literal R_hi*(21/V_A)^2 is reported beside it "
                    "(E77 F2: the literal form is not the registered model's)",
            "rule": "BOUNDED BELOW THE ROW if the total-current upper edge is under 0.875 pJ; else NOT BOUNDED"},
        "C1_e77_posthoc_bound": {
            "what": "E77's post hoc offset fit, the same form, on fresh data",
            "rule": "PASS if E120's 99% upper edge is at or under E77's post hoc 0.496 mOhm (0.30 pJ total-current at "
                    "E77's m0); FAIL otherwise",
            "e77": fo["R_ci99_mohm"]},
        "T1_per_hart_transfer": {
            "what": "per pass, each arm's least-squares line of rung-mean minion delta against harts; the slope ratio "
                    "B/A divided by (800/600)*(V_B/V_A)^2 from that pass's mean window voltages",
            "rule": "PASS if the 99% interval over passes contains 1 AND the mean is within 5% of 1",
            "e77_posthoc": {"ratio": ph["per_hart_ratio_B_over_A"], "fV2": ph["fV2_measured"],
                            "ci99": [1.81, 2.04]}},
        "S1_step_minion": {"what": "arm B's line intercept minus arm A's, per pass (the 800 MHz operating point on the "
                                   "minion rail with no work)",
                           "rule": "PASS if the mean over passes lies in E77's post hoc 99% interval [3.44, 4.75] W"},
        "S2_step_sram": {"what": "arm B's mean SRAM delta minus arm A's, per pass",
                         "rule": "PASS if the mean over passes lies in E77's post hoc 99% interval [1.69, 1.78] W"},
        "P2_matching": {"what": "measured minion-rail watts over idle in each rung pair, pooled over passes",
                        "tolerance_pct": 5.0,
                        "rule": "PASS if all four pairs are within 5%. The offset fit compares the arms' lines and "
                                "needs their ranges to overlap, not exact pairs, so a miss does not make the verdict "
                                "provisional; it is reported"},
        "G_one_temperature": {"what": "the arms' mean launch readings (the die mean in the last idle sample)",
                              "rule": "PASS if they differ by at most 1 C (E77: 1.2 C, named)"},
        "RING_return": {"what": "the return burst after the restore",
                        "rule": "PASS if the clock reaches 800 MHz in the burst AND the ring dumped after it holds at "
                                "least one throttle-up entry newer than the dump before it, by service-processor "
                                "timestamp"},
        "K_kernel": {"what": "host kernel 'SP Runtime Error' events between the gate reads and the closing read",
                     "expected": 0,
                     "rule": "reported; E77's 22 were all its own raw-4 residency reads (F1), and E120 reads raw 1-3 "
                             "only, so any event is named and looked for in the rings"},
        "secondaries_no_verdict": ["floor-referenced: arm B's deltas over its own 32-hart floor rung at 800 MHz, arm "
                                   "A's over its idle, no offset", "offset with the published SRAM and NoC "
                                   "coefficients held (0.034, 0.291)", "offset with SRAM and NoC free",
                                   "E77's registered form (no offset; SRAM and NoC free)", "the uncorrected and "
                                   "board_only footings", "launches flagged below_floor left out"],
        "row_quoted": {"row_pJ": 0.875, "coef_minion": 0.18789339920416637,
                       "source": "docs/reports/data/2026-10-27-q129-rail-ledger/README.md Results table"},
    }
    print(json.dumps(pred, indent=1))


if __name__ == "__main__":
    main()
