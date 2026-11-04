#!/usr/bin/env python3
"""E161 (Q139): the reducer's self-test, before any data. It writes synthetic E161 sessions in the collected layout (G1Q/ and G2Q/ with
tel/REST-00-rest-r1.jsonl.gz, tel/HOLD-00-<label>-r1.jsonl.gz and launches.jsonl.gz) made by Q139(e)'s frozen composition itself
(predict_q139e.a2_closed from a REST at T_rest, P_ref), runs reduce_e161.score on them and checks what the rules must read:

  1. the frozen model's own trajectory (die and board on the closed chain, the clock it simulates): E PASS on both holds with plateau
     errors near 0, both clock rules PASS, arm A PASS (the chain on its own board trace), M7 beside;
  2. the same with the die read as the firmware does (whole degrees, floor): every E and A verdict still PASS;
  3. G1Q's die 4.0 C high in the hold: E INCONCLUSIVE (over 3.149, under 6.297); 7.0 C high: E FAIL;
  4. G2Q's clock held at 800 MHz over the last 300 s: E FAIL (the other regime);
  5. G2Q's clock 50 MHz under the trip clock: the clock rule INCONCLUSIVE; 80 MHz under: FAIL.
Writes into a temporary directory only. Run: /usr/bin/python3 tools/claims-v3/e161/reduce_e161.py --self-test
"""
import gzip
import json
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e161 as R  # noqa: E402

PQ = R.PQ
LABEL = {"G1Q": "b6-int8.b_line_zero_ff", "G2Q": "b6-fp32.real_smol_softmax_v_causal"}
PROC_S = {"G1Q": 8.41, "G2Q": 8.58}
NPROC = {"G1Q": 93, "G2Q": 91}


def write_step(root, st, T_rest=46.0, P_ref=21.93, quant=False, die_shift=0.0, mhz_override=None, t_epoch=1.8e9):
    item = R.HOLDS[st]
    c = PQ.c_of(item)
    d = os.path.join(root, st)
    os.makedirs(os.path.join(d, "tel"), exist_ok=True)
    dur = NPROC[st] * PROC_S[st]
    g, T, P, F = PQ.a2_closed(c, T_rest, P_ref, dur)
    rest_t = t_epoch + np.arange(0, 120.0, 0.1)
    hold_t0 = t_epoch + 121.0
    ht = hold_t0 + np.arange(0, dur + 6.0, 0.1)
    Ti = np.interp(ht - hold_t0, g, T) + die_shift
    Pi = np.interp(ht - hold_t0, g, P)
    Fi = np.interp(ht - hold_t0, g, F)
    if mhz_override is not None:
        Fi = mhz_override(ht - hold_t0, Fi)

    def rd(x):
        return float(math.floor(x)) if quant else float(x)

    with gzip.open(os.path.join(d, "tel", "REST-00-rest-r1.jsonl.gz"), "wt") as f:
        for t in rest_t:
            f.write(json.dumps({"t_ms": int(t * 1000), "board_w": P_ref, "temp_c": {"minshire": [rd(T_rest + (0.5 if quant else 0.0)), 0, 70.0]},
                                "mhz": {"minion": 600.0}}) + "\n")
    with gzip.open(os.path.join(d, "tel", f"HOLD-00-{LABEL[st]}-r1.jsonl.gz"), "wt") as f:
        for t, Tv, Pv, Fv in zip(ht, Ti, Pi, Fi):
            f.write(json.dumps({"t_ms": int(t * 1000), "board_w": float(Pv), "temp_c": {"minshire": [rd(Tv + (0.5 if quant else 0.0)), 0, 70.0]},
                                "mhz": {"minion": float(Fv)}}) + "\n")
    with gzip.open(os.path.join(d, "launches.jsonl.gz"), "wt") as f:
        for i in range(NPROC[st]):
            a = hold_t0 + i * PROC_S[st]
            f.write(json.dumps({"run": f"HOLD-00-{LABEL[st]}-r1", "role": "work", "proc": i, "rc": 0, "t_start_ms": int(a * 1000),
                                "t_end_ms": int((a + PROC_S[st] - 0.01) * 1000)}) + "\n")
    return {"c": c, "T_rest": T_rest, "P_ref": P_ref}


def case(name, builders):
    with tempfile.TemporaryDirectory(prefix="e161-selftest-") as td:
        for st, kw in builders.items():
            write_step(td, st, **kw)
        return R._json(R.score(td))


def main():
    checks = []

    def want(label, got, exp):
        ok = got == exp if not callable(exp) else exp(got)
        checks.append((label, got, ok))

    r = case("model", {"G1Q": {}, "G2Q": {}})
    g1, g2 = r["holds"]["G1Q"], r["holds"]["G2Q"]
    want("1 G1Q E verdict", g1["E_end_to_end"]["verdict"], "PASS")
    want("1 G1Q E plateau err ~0", g1["E_end_to_end"]["plateau_err_C"], lambda x: abs(x) < 0.15)
    want("1 G1Q E clock", g1["E_end_to_end"]["clock_verdict"], "PASS")
    want("1 G1Q regime predicted", g1["E_end_to_end"]["regime_predicted"], "800 MHz")
    want("1 G1Q A verdict", g1["A_given_watts"]["verdict"], "PASS")
    want("1 G2Q E verdict", g2["E_end_to_end"]["verdict"], "PASS")
    want("1 G2Q regime measured", g2["E_end_to_end"]["regime_measured"], "trip")
    want("1 G2Q E clock", g2["E_end_to_end"]["clock_verdict"], "PASS")
    want("1 G2Q A verdict", g2["A_given_watts"]["verdict"], "PASS")
    want("1 G2Q trip clock at 46.0 C, 21.93 W ~ 681.6", g2["E_end_to_end"]["clock_predicted_MHz"], lambda x: abs(x - 681.6) < 0.5)
    want("1 frozen-R check = predicted", g2["A1_C2_trip_clock_with_G1Q_R"]["frozen_R_clock_MHz_check"],
         lambda x: abs(x - g2["E_end_to_end"]["clock_predicted_MHz"]) < 0.05)
    want("1 session figure exists", r["session"]["rms_plateau_err_from_the_bits_C"], lambda x: x is not None and x < 0.3)
    r = case("quantized", {"G1Q": {"quant": True}, "G2Q": {"quant": True}})
    for st in ("G1Q", "G2Q"):
        want(f"2 {st} E verdict (whole degrees)", r["holds"][st]["E_end_to_end"]["verdict"], "PASS")
        want(f"2 {st} A verdict (whole degrees)", r["holds"][st]["A_given_watts"]["verdict"], "PASS")
    r = case("hot4", {"G1Q": {"die_shift": 4.0}})
    want("3 G1Q +4 C: E INCONCLUSIVE", r["holds"]["G1Q"]["E_end_to_end"]["verdict"], "INCONCLUSIVE")
    want("3 G2Q not run", r["verdicts"].get("G2Q"), "NOT RUN: NOT SCORED")
    r = case("hot7", {"G1Q": {"die_shift": 7.0}})
    want("3 G1Q +7 C: E FAIL", r["holds"]["G1Q"]["E_end_to_end"]["verdict"], "FAIL")
    r = case("800", {"G2Q": {"mhz_override": lambda t, F: np.where(t >= t[-1] - 310.0, 800.0, F)}})
    want("4 G2Q at 800 MHz: E FAIL (the other regime)", r["holds"]["G2Q"]["E_end_to_end"]["verdict"], "FAIL")
    f0 = 681.6
    r = case("slow50", {"G2Q": {"mhz_override": lambda t, F: np.where(t >= t[-1] - 310.0, f0 - 50.0, F)}})
    want("5 G2Q clock -50 MHz: INCONCLUSIVE", r["holds"]["G2Q"]["E_end_to_end"]["clock_verdict"], "INCONCLUSIVE")
    r = case("slow80", {"G2Q": {"mhz_override": lambda t, F: np.where(t >= t[-1] - 310.0, f0 - 80.0, F)}})
    want("5 G2Q clock -80 MHz: FAIL", r["holds"]["G2Q"]["E_end_to_end"]["clock_verdict"], "FAIL")
    bad = 0
    for label, got, ok in checks:
        print(("ok   " if ok else "FAIL ") + label + f": {got}")
        bad += not ok
    print(f"selftest_e161: {len(checks) - bad} of {len(checks)} as expected")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
