#!/usr/bin/env python3
"""Q141(t) step 3, post hoc (not registered): is e(27) a fair error for the 27-point launch average? And what does the arm's one
tile with an 81-point twin read at 81 points?

    python3 -B posthoc_e_check.py        # reads recount-rule.json beside this file and ../arm-s7.json; writes posthoc-e-check.json/.txt

1. For each calibration tile counted at 81 points, the 27-point mean minus the 81-point mean, d, against its expected spread under
   the rule's own error model. The 27 points are nested in the 81, so var(d) = e(27)^2 - e(81)^2; z = d / sqrt(e(27)^2 - e(81)^2).
   If e(27) is a fair 1-s.e. error, z has rms about 1.
2. Pool 7's fp32.b_onebit_b20_pi is byte for byte fp32.cal_pi_b20 (Q140(x)'s note A1-2). Its three-point minus 81-point
   difference at M9's prices is the arm's k at N = 81, beside the frozen arm's k at 27. On this tile the frozen code's k equals the
   rule's stage-price difference (the arm's check; the score_s7arm self-test's T3), and on card 1 it scales by M9's
   card1_scale_by_format. The arm stays as frozen: this is a reading, not an amendment.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "recount-rule.json")))
arm = json.load(open(os.path.join(HERE, "..", "arm-s7.json")))
out = {"_note": "Q141(t) step 3, post hoc: e(27) against the 27-to-81 move; the arm's b20_pi at 81 points through its byte twin",
       "tiles": {}}
L = ["Q141(t) step 3, post hoc: the 27-point mean minus the 81-point mean against sqrt(e(27)^2 - e(81)^2)", "",
     f"{'tile':20s} {'d (W)':>7s} {'e(27)':>6s} {'e(81)':>6s} {'z':>6s}"]
zs = []
for n, t in r["tiles"].items():
    b = t["by_N"]
    if "81" not in b:
        continue
    e27, e81 = b["27"]["e_w"], b["81"]["e_w"]
    d = b["27"]["mean_w"] - b["81"]["mean_w"]
    z = d / math.sqrt(e27 ** 2 - e81 ** 2)
    zs.append(z)
    out["tiles"][n] = {"d_w": d, "e27_w": e27, "e81_w": e81, "z": z}
    L.append(f"{n:20s} {d:+7.3f} {e27:6.3f} {e81:6.3f} {z:+6.2f}")
out["z_rms"] = math.sqrt(sum(z * z for z in zs) / len(zs))
out["n"] = len(zs)
out["abs_z_over_2"] = sum(abs(z) > 2 for z in zs)
L += ["", f"rms z {out['z_rms']:.2f} over {len(zs)} tiles; |z| > 2 on {out['abs_z_over_2']}"]
pb = r["tiles"]["fp32.cal_pi_b20"]["by_N"]
s1 = arm["cards"]["aifoundry1c1"]["fp32.b_onebit_b20_pi"]["card_scale"]
out["arm_b20_pi_at_81"] = {}
for card, s in (("aifoundry3", 1.0), ("aifoundry1c1", s1)):
    a = arm["cards"][card]["fp32.b_onebit_b20_pi"]
    rec = {"k27_frozen_w": a["k_w"], "u27_w": a["u_w"], "k81_w": round(s * pb["81"]["three_point_minus_N_w"], 4),
           "u81_w": round(s * pb["81"]["e_w"], 4), "P27_frozen_w": a["P27_w"],
           "P81_w": round(a["P3_w"] - s * pb["81"]["three_point_minus_N_w"], 4)}
    out["arm_b20_pi_at_81"][card] = rec
    L.append(f"{card}: the arm's fp32.b_onebit_b20_pi (twin fp32.cal_pi_b20): k {rec['k27_frozen_w']:+.3f} +- {rec['u27_w']:.3f} W at 27 "
             f"(frozen) -> {rec['k81_w']:+.3f} +- {rec['u81_w']:.3f} W at 81; D {rec['P27_frozen_w']:.3f} -> {rec['P81_w']:.3f} W")
json.dump(out, open(os.path.join(HERE, "posthoc-e-check.json"), "w"), indent=1, sort_keys=True)
open(os.path.join(HERE, "posthoc-e-check.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
