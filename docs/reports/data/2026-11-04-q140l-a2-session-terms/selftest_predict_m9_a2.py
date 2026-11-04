#!/usr/bin/env python3
"""Q140(l): the frozen prediction code reproduces the fit's own in-sample predictions of M9's aifoundry2 part.

    python3 selftest_predict_m9_a2.py > selftest-predict-m9a2.txt

For every one of the 134 scored cells in rows-m9a2.json: predict_m9_a2.burst() with the cell's session's own zeros-anchor
reads and the cell's own die starts must give fit_m9_a2.py's final in-sample clock and board to 1e-6. Then the fallback
path (no anchors) must use m9_a2.json's fallback offsets, and a session with one format's anchor missing must fill it from
the others, as registered.
"""
import sys

sys.dont_write_bytecode = True
import json  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predict_m9_a2 as A2  # noqa: E402

R = json.load(open(os.path.join(HERE, "rows-m9a2.json")))
anch = {h: {t: [{"burst_w": r["w"], "burst_mhz": r["mhz"], "die_start": r["T"]} for r in rr] for t, rr in a.items()} for h, a in R["anchors"].items()}
worst_f = worst_w = 0.0
for row in R["rows"]:
    p = A2.burst(row["D"], row["type"], anch[row["session"]], [r["T"] for r in row["runs"]])
    worst_f = max(worst_f, abs(p["burst_mhz"] - row["final_in_sample"][0]))
    worst_w = max(worst_w, abs(p["burst_board_w"] - row["final_in_sample"][1]))
# burst() rounds to 0.01 MHz and 0.001 W, so compare with the unrounded internals too
worst_fu = worst_wu = 0.0
for row in R["rows"]:
    delta, _ = A2.session_delta(anch[row["session"]])
    f, P = A2._cell(A2.CZ[row["type"]] + A2.G * row["D"], row["type"], delta, [r["T"] for r in row["runs"]])
    worst_fu = max(worst_fu, abs(f - row["final_in_sample"][0]))
    worst_wu = max(worst_wu, abs(P - row["final_in_sample"][1]))
ok = worst_fu < 1e-6 and worst_wu < 1e-6
d0, s0 = A2.session_delta(None)
ok_fb = d0 == A2.M9["fallback_delta_w"] and s0.startswith("fallback")
d1, s1 = A2.session_delta(anch["E80"])          # E80 has no fp32 anchor: filled from fp16 and int8
ok_fill = abs(d1["fp32"] - (d1["fp16"] + d1["int8"]) / 2.0) < 1e-12 and "filled" in s1
d2, _ = A2.session_delta(anch["E160"])          # E160's fp16 anchor ran its first burst at 752 MHz: left out
fp16_runs = [r for r in anch["E160"]["fp16"] if r["burst_mhz"] >= 795]
ok_752 = len(fp16_runs) == 2 and len(anch["E160"]["fp16"]) == 3
print(f"cells: {len(R['rows'])}; worst |burst() - fit| (rounded output) {worst_f:.4f} MHz, {worst_w:.5f} W; unrounded {worst_fu:.2e} MHz, {worst_wu:.2e} W: {'OK' if ok else 'FAIL'}")
print(f"fallback path (no anchors): delta {d0} source '{s0}': {'OK' if ok_fb else 'FAIL'}")
print(f"E80's missing fp32 anchor filled from fp16 and int8: {d1['fp32']:.4f} = mean({d1['fp16']:.4f}, {d1['int8']:.4f}): {'OK' if ok_fill else 'FAIL'}")
print(f"E160's fp16 anchor: {len(fp16_runs)} of {len(anch['E160']['fp16'])} bursts at 795 MHz or more count: {'OK' if ok_752 else 'FAIL'}")
print(f"m9_a2.json sha256 {A2.M9_SHA256}")
print("SELFTEST", "PASS" if (ok and ok_fb and ok_fill and ok_752) else "FAIL")
sys.exit(0 if (ok and ok_fb and ok_fill and ok_752) else 1)
