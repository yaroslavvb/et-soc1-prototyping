#!/usr/bin/env python3
"""E109 self-test: synthetic reducer outputs through score_e109.py, one per reading, from predictions-e109.json's frozen numbers plus pass noise
(sd 0.04 W a cell). Under H_ops the scorer must name PER-OP, under H_reads PER-TIME, and under H_bench LANES-OPPOSE; R7 and R8 must PASS (every reading
says 0); R6 must PASS at the predicted cycles. Run before the claim; it writes selftest.txt. Standard library only.
SPDX-License-Identifier: Apache-2.0"""
import json, os, random, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e109.json")))
ARMS = P["arms"]
def nm(k):
    a, f, kind = k.split(".", 2)
    return f"{f}.{kind}" if a == "base" else k
def synth(h, seed):
    rng = random.Random(seed)
    passes = ["10910", "10911", "10912", "10913"]
    per, items = {}, {}
    S0 = {"fp32": 1.95, "int8": 1.95 + (P["predicted_quantities"][h]["gap"]["G_w"] if h != "H_bench" else 0.6)}
    for p in passes:
        e = {}
        for k, r in ARMS.items():
            f = k.split(".")[1]
            D = P["predicted_D_w"][k][h] + (0 if k.startswith("base.") and k.endswith(".zeros") else rng.gauss(0, 0.04))
            if k == "base.fp32.a_nz_b_randn":
                D = 12.0 + rng.gauss(0, 0.04)
            if k == "m0.fp32.a_nz_b_randn":
                D = P["predicted_D_w"]["m0.fp32.zeros"][h] + 0.8 + rng.gauss(0, 0.04)
            if k == "m0.fp32.a_zeros_b_randn":
                D = P["predicted_D_w"]["m0.fp32.zeros"][h] + 0.8 + rng.gauss(0, 0.04)
            if k == "base.fp32.a_zeros_b_randn":
                D = 0.8 + rng.gauss(0, 0.04)
            e[nm(k)] = {"D": D, "S": S0[f] + D + rng.gauss(0, 0.03), "rate": r["rate_pred"] * (1 + rng.gauss(0, 0.0005)), "cpo": r["card_cycles_pred"]}
        e["anchor_pi"] = {"D": 8.3 + rng.gauss(0, 0.05), "S": 10.3, "rate": 1.12e9, "cpo": 546.0}
        per[p] = e
    for n in per[passes[0]]:
        items[n] = {"D": {"mean": sum(per[p][n]["D"] for p in passes) / 4}, "cycles_per_op": per[passes[0]][n]["cpo"]}
    for n, v in (("fp32.randn", 24.7), ("fp16.randn", 22.2), ("int8.full", 7.05)):
        items[n] = {"D": {"mean": v}, "cycles_per_op": 546.0}
    return {"passes": [int(p) for p in passes], "per_pass": per, "items": items}
L = []
ok = True
want = {"H_ops": ("PER-OP", "FAIL", "PASS"), "H_reads": ("PER-TIME", "PASS", "FAIL"), "H_bench": (None, None, None)}
for h in ("H_ops", "H_reads", "H_bench"):
    with tempfile.TemporaryDirectory() as d:
        src, out = os.path.join(d, "e.json"), os.path.join(d, "s.json")
        json.dump(synth(h, 7), open(src, "w"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "score_e109.py"), src, "--out", out], capture_output=True, text=True)
        if r.returncode:
            L.append(f"{h}: scorer failed: {r.stderr[-400:]}"); ok = False; continue
        s = json.load(open(out))
    R = s["rules"]
    line = (f"{h}: R0 {R['R0_answer']['verdict']}, R1 {R['R1_ops']['verdict']}, R2 {R['R2_lanes']['verdict']}, R3 {R['R3_per_time']['verdict']}, "
            f"R4 {R['R4_b_reads']['verdict']}/{R['R4_b_reads']['h_reads']}, R5 {R['R5_additive']['fp32']['verdict']}/{R['R5_additive']['int8']['verdict']}, "
            f"R6 {sorted(set(v['verdict'] for v in R['R6_cycles'].values()))}, R7 {R['R7_sign_unseen']['verdict']}, R8 {R['R8_gated_transport']['verdict']}; "
            f"G_op {s['gap']['G_op']['mean']:+.3f}, G_lane {s['gap']['G_lane']['mean']:+.3f}, G_rest {s['gap']['G_rest']['mean']:+.3f}")
    L.append(line)
    w = want[h]
    if w[0] and R["R0_answer"]["verdict"] != w[0]: ok = False; L.append(f"  FAIL: R0 should be {w[0]}")
    if w[1] and R["R3_per_time"]["verdict"] != w[1]: ok = False; L.append(f"  FAIL: R3 should be {w[1]}")
    if w[2] and R["R1_ops"]["verdict"] != w[2]: ok = False; L.append(f"  FAIL: R1 should be {w[2]}")
    if h == "H_bench" and R["R2_lanes"]["verdict"] != "LANES-OPPOSE": ok = False; L.append("  FAIL: R2 should be LANES-OPPOSE")
    if R["R7_sign_unseen"]["verdict"] != "PASS" or R["R8_gated_transport"]["verdict"] != "PASS": ok = False; L.append("  FAIL: R7/R8 should PASS")
    if set(v["verdict"] for v in R["R6_cycles"].values()) != {"PASS"}: ok = False; L.append("  FAIL: R6 should PASS")
L.append("SELFTEST " + ("PASS" if ok else "FAIL"))
open(os.path.join(HERE, "selftest.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
sys.exit(0 if ok else 1)
