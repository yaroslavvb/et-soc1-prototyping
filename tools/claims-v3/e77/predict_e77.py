#!/usr/bin/env python3
"""E77's frozen predictions and decision rules, from E77-PLAN.md and the rail ledger's measured 600 MHz law.

    python3 tools/claims-v3/e77/predict_e77.py > tools/claims-v3/e77/predictions.json

Nothing here is fitted to E77's data; it is written and committed before the claim and the first launch.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LEDGER = os.path.join(ROOT, "docs/reports/data/2026-10-27-q129-rail-ledger")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    led = json.load(open(os.path.join(LEDGER, "rail-ledger.json")))
    law = led["hart_law_600mhz"]["per_card"]["aifoundry2"]["minion"]
    off, slope = law["offset_w"], law["mw_per_hart"] / 1000.0
    f_ratio, v_a, v_b = 800 / 600, 0.516, 0.618
    k = f_ratio * (v_b / v_a) ** 2                      # the f*V^2 transfer per hart, 1.913
    arm_a = [1024, 768, 544, 288]
    arm_b = [544, 416, 288, 160]
    pa = [off + slope * h for h in arm_a]
    pb = [k * (off + slope * h) for h in arm_b]
    coef = led["published_fit_coef"]["aifoundry2"]
    pred = {
        "experiment": "E77",
        "frozen": "before the claim and the first launch (the commit that adds this file)",
        "sources": {"E77-PLAN.md": sha(os.path.join(LEDGER, "E77-PLAN.md")),
                    "rail-ledger.json": sha(os.path.join(LEDGER, "rail-ledger.json")),
                    "law": "rail-ledger.json hart_law_600mhz.per_card.aifoundry2.minion",
                    "law_offset_w": off, "law_mw_per_hart": law["mw_per_hart"]},
        "transfer": {"f_ratio": f_ratio, "v_a_nominal": v_a, "v_b_nominal": v_b, "per_hart_ratio": round(k, 4)},
        "rungs": [{"rung": i + 1, "arm_a_harts": arm_a[i], "arm_a_minion_w": round(pa[i], 2),
                   "arm_b_harts": arm_b[i], "arm_b_minion_w": round(pb[i], 2),
                   "mismatch_pct": round(100 * (pb[i] - pa[i]) / pa[i], 1)} for i in range(4)],
        "plan_table_check": "these reproduce E77-PLAN.md's table: 22.40/16.69/11.69/5.98 and 22.36/16.90/11.44/5.98 W",
        "P1_ratio": {"what": "minion-rail watts over idle, arm B / arm A at the SAME hart count (544 and 288)",
                     "predicted": round(k, 3), "tolerance_pct": 5.0,
                     "rule": "PASS if both hart counts read within 5% of 1.913 (the tolerance is this registration's: "
                             "the plan names the ratio, not a band; 5% is its matching tolerance). Also reported "
                             "against (800/600)*(V_B/V_A)^2 from the measured sp.minion_mv. A FAIL is reported "
                             "before anything else: the matching itself is then wrong"},
        "P2_matching": {"what": "measured minion-rail watts over idle in each rung pair (A rung g against B rung g)",
                        "tolerance_pct": 5.0,
                        "rule": "a pair differing by more than 5% is reported as mismatched and the 43.4% check is "
                                "reported against the achieved mismatch; if more than one pair misses, the f*V^2 "
                                "transfer is reported as refuted on this card, and since the ladder cannot be re-cut "
                                "inside this session the verdict below is reported as provisional, pending a "
                                "re-cut ladder"},
        "P3_conduction_excess": {"what": "at matched rail watts, arm A's conduction loss exceeds arm B's by "
                                         "(V_B/V_A)^2 - 1 of the conduction part, from the per-rung MEASURED voltages",
                                 "nominal": round((v_b / v_a) ** 2 - 1, 4)},
        "V_fit": {"model": "offrail = a_m*dminion + a_s*dSRAM + a_n*dNoC + R_eff*[((m0 + dminion)/V)^2 - (m0/V0)^2], "
                           "no intercept, all as deltas over each launch's own pre-launch idle, on the central "
                           "(drift_split) footing; m0 = the idle bracket's minion-rail watts, V0 its sp.minion_mv and V "
                           "the window's, in volts. The conduction term is the change in the regulator's I^2 from the "
                           "TOTAL minion current: a regulator loses R I^2 in its whole current, and E77-PLAN.md's "
                           "literal R_eff*(dminion/V)^2 leaves out the idle current's cross term 2*I0*dI, which is "
                           "larger than dI^2 at these loads (m0 about 15-16 W, so I0 about 30 A, against a load step "
                           "of at most about 43 A) and differs between the arms through 1/V^2 (registered before any "
                           "data as README departure 10; the literal form is reported beside it as a secondary)",
                  "unit": "per pass: the rung means of arm A pass k and arm B pass k (8 points), least squares; "
                          "the unit of replication is the pass (CONTEXT section 4)",
                  "PASS": "R_eff's two-sided 99% interval over passes (mean +- t(0.995, n-1) * SD/sqrt(n)) excludes "
                          "0, AND the pooled fit over every rung mean has an rms at least 30% below the same fit "
                          "without the R_eff term",
                  "FAIL": "R_eff's 99% interval contains 0: the whole 0.875 pJ row is then off-rail logic in step "
                          "with the rails, the conduction loss bounded above by the interval's upper edge. A FAIL "
                          "is a result",
                  "neither": "the interval excludes 0 but the rms improves by less than 30%: reported as 'R_eff "
                             "resolved, not a material term', neither PASS nor FAIL",
                  "report": "R_eff in milliohm; the conduction loss it implies at a 21 W minion rail at arm A's "
                            "measured voltage, R_eff*(21/V_A)^2; that loss as a share of the published minion "
                            "coefficient's 0.188*21 W; and that share of the 0.875 pJ row in pJ (the pJ this moves "
                            "out of 'delivery loss plus logic in step' into a named regulator conduction loss)",
                  "secondary_plan_literal_square": "E77-PLAN.md's R_eff*(dminion/V)^2 with the same rules; no verdict",
                  "secondary_fixed_small_rails": {"a_s": coef["sram"], "a_n": coef["noc"],
                                                  "what": "the same fit with the SRAM and NoC coefficients held at "
                                                          "the published aifoundry2 values; secondary, does not "
                                                          "carry the verdict"},
                  "sensitivities": ["uncorrected footing", "board_only footing", "the rails deconvolved "
                                    "(tools/ettelem/deconv.py) instead of the settling ratio", "launches flagged "
                                    "below_floor left out", "launch-level pooled fit"]},
        "no_outcome_predicted": "E77-PLAN.md freezes the structure of the test, not the size or sign of R_eff, and "
                                "this registration adds none",
        "row_quoted": {"row_pJ": 0.875, "coef_minion": coef["minion"],
                       "source": "docs/reports/data/2026-10-27-q129-rail-ledger/README.md Results table"},
    }
    json.dump(pred, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
