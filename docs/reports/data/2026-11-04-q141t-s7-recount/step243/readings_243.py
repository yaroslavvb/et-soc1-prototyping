#!/usr/bin/env python3
"""Q141(t2), ../REGISTRATION-step243.md section 5: the step's reported readings, registered with it before any 243-point count.
None is a verdict, and none changes a frozen prediction, price, card term, band or rule.

    /usr/bin/python3 -B readings_243.py      # reads recount-rule.json beside this file and ../arm-s7.json;
                                             # writes readings-243.json / .txt

G1  the 81-to-243 move: d = mean(81) - mean(243) on each tile counted at 243. The 81 points are nested in the 243, so under the
    rule's own error model var(d) = e(81)^2 - e(243)^2 and z = d / sqrt(e(81)^2 - e(243)^2) (undefined where e(243) >= e(81)).
    If e(81) is a fair 1-s.e. error, z has rms about 1. The same reading at 27 -> 81 was step81's post hoc check.
G2  the 1/sqrt(N) law: e(81)/e(243) per tile against sqrt(3) = 1.73; its range and median.
G3  the three-point count's error on bit-20 and bit-21 tiles: 3pt - 243 per tile, at M9's frozen prices.
G4  the arm's one tile with a calibration twin: pool 7's fp32.b_onebit_b20_pi is byte for byte fp32.cal_pi_b20 (Q140(x)'s note
    A1-2). Its counting part at 243 points, k243 = s x (3pt - 243) +- s x e(243), beside the arm's frozen k at 27 points and
    step81's reading at 81 (s = 1 on aifoundry3, M9's card1_scale_by_format on card 1, as arm-s7.json carries it). The arm stays
    as frozen, at 27 points: this is a reading for E163 and E164, not an amendment.
G5  pool 6's twin: recount_rule.py main()'s own post hoc lines (posthoc_pool6_twins) at the largest N counted, copied.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "recount-rule.json")))
arm = json.load(open(os.path.join(HERE, "..", "arm-s7.json")))
out = {"_note": "Q141(t2): the 243-point step's registered readings (REGISTRATION-step243.md section 5); reported only",
       "G1_move_81_to_243": {}, "G2_ratio": {}, "G3_three_point_error_w": {}}
L = ["Q141(t2): the 243-point step's readings (REGISTRATION-step243.md section 5), reported only", "",
     "G1-G3 per tile counted at 243 points (W of D at M9's frozen prices)", "",
     f"{'tile':20s} {'d=m81-m243':>10s} {'e(81)':>6s} {'e(243)':>6s} {'z':>6s} {'e81/e243':>8s} {'3pt-243':>8s}"]
zs, rats = [], []
for n, t in r["tiles"].items():
    b = t["by_N"]
    if "243" not in b:
        continue
    e81, e243 = b["81"]["e_w"], b["243"]["e_w"]
    d = b["81"]["mean_w"] - b["243"]["mean_w"]
    z = d / math.sqrt(e81 ** 2 - e243 ** 2) if e81 > e243 else None
    rat = e81 / e243
    if z is not None:
        zs.append(z)
    rats.append(rat)
    out["G1_move_81_to_243"][n] = {"d_w": d, "e81_w": e81, "e243_w": e243, "z": z}
    out["G2_ratio"][n] = rat
    out["G3_three_point_error_w"][n] = b["243"]["three_point_minus_N_w"]
    zt = f"{z:+6.2f}" if z is not None else f"{'-':>6s}"
    L.append(f"{n:20s} {d:+10.3f} {e81:6.3f} {e243:6.3f} {zt} {rat:8.2f} {b['243']['three_point_minus_N_w']:+8.3f}")
if zs:
    out["G1_z_rms"] = math.sqrt(sum(z * z for z in zs) / len(zs))
    out["G1_n"] = len(zs)
    out["G1_abs_z_over_2"] = sum(abs(z) > 2 for z in zs)
    L += ["", f"G1: z rms {out['G1_z_rms']:.2f} over {len(zs)} tiles; |z| > 2 on {out['G1_abs_z_over_2']}"]
if rats:
    out["G2_range"] = [min(rats), max(rats)]
    out["G2_median"] = statistics.median(rats)
    L.append(f"G2: e(81)/e(243) {min(rats):.2f}-{max(rats):.2f}, median {out['G2_median']:.2f} (the 1/sqrt(N) law: {math.sqrt(3):.2f})")
g3 = list(out["G3_three_point_error_w"].values())
if g3:
    L.append(f"G3: the three-point count's error at 243 points runs {min(g3):+.3f} to {max(g3):+.3f} W over these tiles")
pb = r["tiles"]["fp32.cal_pi_b20"]["by_N"]
out["G4_arm_b20_pi"] = {}
if "243" in pb:
    s1 = arm["cards"]["aifoundry1c1"]["fp32.b_onebit_b20_pi"]["card_scale"]
    for card, s in (("aifoundry3", 1.0), ("aifoundry1c1", s1)):
        a = arm["cards"][card]["fp32.b_onebit_b20_pi"]
        rec = {"k27_frozen_w": a["k_w"], "u27_w": a["u_w"], "k81_w": round(s * pb["81"]["three_point_minus_N_w"], 4),
               "u81_w": round(s * pb["81"]["e_w"], 4), "k243_w": round(s * pb["243"]["three_point_minus_N_w"], 4),
               "u243_w": round(s * pb["243"]["e_w"], 4), "P3_frozen_w": a["P3_w"], "P27_frozen_w": a["P27_w"],
               "P243_w": round(a["P3_w"] - s * pb["243"]["three_point_minus_N_w"], 4), "card_scale": s}
        out["G4_arm_b20_pi"][card] = rec
        L.append(f"G4 {card}: the arm's fp32.b_onebit_b20_pi (twin fp32.cal_pi_b20): k {rec['k27_frozen_w']:+.3f} +- {rec['u27_w']:.3f} W "
                 f"at 27 (frozen), {rec['k81_w']:+.3f} +- {rec['u81_w']:.3f} at 81, {rec['k243_w']:+.3f} +- {rec['u243_w']:.3f} at 243; "
                 f"D {rec['P3_frozen_w']:.3f} (M9 frozen) -> {rec['P243_w']:.3f} W")
out["G5_pool6_twins"] = r.get("posthoc_pool6_twins")
for k, v in (out["G5_pool6_twins"] or {}).items():
    L.append(f"G5 {k} (N = {v['N']}): correction {v['correction_w']:+.3f} +- {v['e_w']:.3f} W; M9 nested "
             f"{v['M9_nested|a3']['err_w']:+.3f} -> {v['M9_nested|a3']['err_with_N_point_average_w']:+.3f} W (aifoundry3), "
             f"{v['M9_nested|c1']['err_w']:+.3f} -> {v['M9_nested|c1']['err_with_N_point_average_w']:+.3f} W (card 1)")
json.dump(out, open(os.path.join(HERE, "readings-243.json"), "w"), indent=1, sort_keys=True)
open(os.path.join(HERE, "readings-243.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
