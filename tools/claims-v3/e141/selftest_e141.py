#!/usr/bin/env python3
"""E141 self-test (Q138), on the Intel, before the claim: nothing here is a measurement. Standard library only.

  A. the planned intervals: every rms and bias rule's 2.5-97.5% range for the registered tile mix, at the registered draws
     (planned-intervals.txt);
  B. the scorer on simulated sessions (60 a world, three passes, 0.05 W / 0.05 C pass noise; bootstrap draws cut to 2,000 for speed):
     the measured value of each tile is M7's frozen prediction plus an error drawn from M7's own aifoundry3 reference errors (power) or a
     normal error of M7's aifoundry3 heat rms (heat), times 1 (as good as the nested score), 2 and 3; a fourth world adds a -0.3 W bias (M7
     too high) to the floats at 1x;
  C. the scorer on a session with one kept pass (every rule NOT SCORED) and with a missing tile (it is left out and named).

    python3 tools/claims-v3/e141/selftest_e141.py > tools/claims-v3/e141/selftest.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e141 as S  # noqa: E402

reg = json.load(open(os.path.join(HERE, "predictions-e141.json")))


def fake(reg, scale, bias_floats, seed, passes=(14110, 14111, 14112), drop=()):
    rng = random.Random(seed)
    refP = reg["reference_errors"]["power_a3"]
    hr = reg["model"]["heat_pool_a3_rms_c"]
    pp = {str(p): {} for p in passes}
    for t, P in reg["tiles"].items():
        if t in drop:
            continue
        f = P["type"]
        eP = scale * refP[f][rng.randrange(len(refP[f]))] + (bias_floats if f != "int8" else 0.0)
        eH = scale * rng.gauss(0, hr[f])
        for p in passes:
            pp[str(p)][t] = {"D": P["M7"]["D_w"] + eP + rng.gauss(0, 0.05),
                             "dT_win": P["M7"]["dT_win_c"] + eH + rng.gauss(0, 0.05),
                             "S": P["M7"]["S_w"] + eP}
        for a in ("fp32.randn", "fp16.randn", "int8.full"):
            for p in passes:
                pp[str(p)][a] = {"D": 20.0}
    return {"passes": list(passes), "passes_set_aside": [], "leak": {"mode": "auto"}, "per_pass": pp}


def main():
    r2 = copy.deepcopy(reg)
    print("E141 self-test (nothing here is a measurement)")
    print("\nA. planned intervals (registered draws):")
    p1 = reg["sets"]["priority1_by_format"]
    bs = reg["plan"]["bootstrap"]
    lines = []
    for rid, f in (("E141-P1", "fp32"), ("E141-P2", "fp16"), ("E141-P3", "int8")):
        iv = S.draw_interval(reg["reference_errors"]["power_a3"], {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
        lines.append(f"{rid} power {f} rms over {len(p1[f])}: [{iv['lo95']:.3f}, {iv['hi95']:.3f}] W (median {iv['median']:.3f})")
    for rid, mix in (("E141-B1", {"fp32": len(p1["fp32"]), "fp16": len(p1["fp16"])}), ("E141-B2", {"int8": len(p1["int8"])})):
        iv = S.draw_interval(reg["reference_errors"]["power_a3"], mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
        lines.append(f"{rid} bias {mix}: [{iv['lo95']:+.3f}, {iv['hi95']:+.3f}] W")
    for rid, f in (("E141-H1", "fp32"), ("E141-H2", "fp16"), ("E141-H3", "int8")):
        iv = S.draw_interval(reg["reference_errors"]["heat_normal_a3"], {f: len(p1[f])}, bs["draws"], bs["seed"] + sum(map(ord, rid)),
                             "rms")
        lines.append(f"{rid} heat {f} rms over {len(p1[f])}: [{iv['lo95']:.3f}, {iv['hi95']:.3f}] C")
    lines.append(f"E141-C1 / E141-H4: at least {S.binom_low(30)} of 30 inside")
    print("\n".join("  " + x for x in lines))
    open(os.path.join(HERE, "planned-intervals.txt"), "w").write("\n".join(lines) + "\n")
    r2["plan"]["bootstrap"]["draws"] = 2000
    print("\nB. simulated sessions, 60 a world (bootstrap draws 2,000): count of each verdict")
    for name, scale, bias in (("as good as the nested score", 1.0, 0.0), ("twice as bad", 2.0, 0.0), ("three times as bad", 3.0, 0.0),
                              ("floats biased -0.3 W (M7 too high), 1x", 1.0, -0.3)):
        tally = {}
        for i in range(60):
            s = S.score(fake(r2, scale, bias, f"{name}|{i}"), r2)
            for rid, v in S.verdicts(s).items():
                tally.setdefault(rid, {}).setdefault(v, 0)
                tally[rid][v] += 1
        print(f"  {name}:")
        for rid in sorted(tally):
            print(f"    {rid}: " + ", ".join(f"{v} {n}" for v, n in sorted(tally[rid].items())))
    print("\nC. edge cases:")
    s = S.score(fake(r2, 1.0, 0.0, "one", passes=(14110,)), r2)
    print("  one kept pass:", s.get("NOT SCORED"))
    s = S.score(fake(r2, 1.0, 0.0, "drop", drop=("fp32.sorted_k",)), r2)
    print("  fp32.sorted_k missing: short tiles", s["short_tiles"], "; P1 tiles", len(s["rules"]["E141-P1"]["tiles"]))
    print("\nSELFTEST DONE")


if __name__ == "__main__":
    main()
