#!/usr/bin/env python3
"""E168 (Q141(o)): a planning aid for the rests, from the frozen code only. Desk only; no card. It writes nothing but its stdout.

    /usr/bin/python3 -B tools/claims-v3/e168/rest_chain_e168.py > tools/claims-v3/e168/logs/rest-chain.txt

Q138(t)'s frozen aifoundry2 chain (g3_model, as G4 uses it) run through each hold as predict_e168.py's nominal starts build it
(cold: the chain at rest at 46.0 C; warm55: after the same shape's fp32 random cold hold, idle until the die reads 55 C), then
idle (the chain's excess decaying at the rest board power), to give:
  * the time from each hold's end until the die is within 2, 1 and 0.5 C of the rest: how long a rest to about 46 C takes, the
    basis of the 360 s cold-gate bound and of the card-minutes;
  * the time from each cold hold's end to 55 C: the warm55 gate's wait.
SELF-CHECK: the window means it computes for every hold must equal predictions-e168.json's frozen G4 nominal numbers (both starts)
to 0.01, or it says FAIL: the replication is then not predict_e168.py's model. No number here is a prediction that is scored.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G4D = os.path.join(LAB, "docs/reports/data/2026-11-04-q140q-gemm-g4-stride")
sys.path.insert(0, G4D)
import g4_model as G4  # noqa: E402  (frozen in e39d06da; imports g3_model as frozen in 91def7c4)

G = G4.G
P = json.load(open(os.path.join(G4D, "predictions-e168.json")))
C4 = P["g4"]["constants"]
ARM = {"k": C4["k_W_per_C"], "trip": C4["trip_C"], "T_ref": C4["T_ref_C"], "zeros": C4["zeros_level"], "dip": (C4["dip"]["d_G"], C4["dip"]["P_G_w"])}
T_COLD, T_WARM, N_PROC, SECONDS = 46.0, 55.0, 12, 8.0


def lev(cell):
    return {int(f): v for f, v in P["cells"][cell]["P0_w"].items()}


def hold(levels, t, x0, T0):
    """predict_e168.run_model's simulate4 call, returning the window means and the chain state at the hold's end"""
    g, on, wins = G.run_schedule(N_PROC, SECONDS)
    shift = G4.BETA * G4.DELTA_FALLBACK[t] if ARM["zeros"] else 0.0
    T, Pw, F = G4.simulate4(levels, on, x0, T_COLD, T0, ARM["trip"], ARM["k"], T_ref=ARM["T_ref"], shift=shift, dip=ARM["dip"])
    w = G.window_means(g, on, T, Pw, F, wins[-1][1])
    return w, G.chain_open(Pw, x0=x0)[-1], float(T[-1])


def decay_until(x, thr_c):
    n = 0
    while float(G.R @ x) > thr_c and n < 200000:
        x = G.A * x
        n += 1
    return round(n * G.DT, 1), x


def main():
    print("E168 rests from Q138(t)'s frozen aifoundry2 chain (planning aid; nothing here is scored). tau_s", [float(v) for v in G.TAU], "R C/W",
          [float(v) for v in G.R], "dt", G.DT)
    bad = []
    rows = []
    for cell, c in P["cells"].items():
        prev = lev(f"{c['shape']}-fp32-randn-cold")
        for start in ("cold", "warm55"):
            x0 = np.zeros(len(G.TAU))
            if start == "warm55":
                _, xp, _ = hold(prev, "fp32", np.zeros(len(G.TAU)), T_COLD)
                while T_COLD + float(G.R @ xp) > T_WARM:
                    xp = G.A * xp
                x0 = xp
            T0 = T_COLD + float(G.R @ x0)
            w, xe, Te = hold(lev(cell), c["type"], x0, T0)
            ref = c["both_nominal_starts"][start]["G4"]
            diff = max(abs(w["mhz"] - ref["mhz"]), abs(w["w"] - ref["w"]), abs(w["die"] - ref["die"]))
            if diff > 0.01:
                bad.append((cell, start, round(diff, 4)))
            t2, _ = decay_until(xe.copy(), 2.0)
            t1, _ = decay_until(xe.copy(), 1.0)
            t05, _ = decay_until(xe.copy(), 0.5)
            t55, _ = decay_until(xe.copy(), T_WARM - T_COLD)
            rows.append((cell, start, w, Te, t2, t1, t05, t55, diff))
    print(f"{'hold':36s} {'start':7s} | {'window MHz':>10s} {'W':>7s} {'die':>6s} | {'die at end':>10s} | {'to rest+2':>9s} {'+1':>6s} {'+0.5 C':>7s} | {'to 55 C':>7s} | self-check")
    for cell, start, w, Te, t2, t1, t05, t55, diff in rows:
        print(f"{cell:36s} {start:7s} | {w['mhz']:10.2f} {w['w']:7.3f} {w['die']:6.2f} | {Te:10.2f} | {t2:8.1f}s {t1:5.1f}s {t05:6.1f}s | {t55:6.1f}s | "
              f"{'ok' if diff <= 0.01 else 'FAIL'} ({diff:.4f})")
    print()
    print("SELF-CHECK:", "PASS (every window mean equals predictions-e168.json's frozen G4 nominal, both starts, to 0.01)" if not bad else f"FAIL {bad}")
    print("Reading: after a warm fp32 random hold the chain is within 1 C of the rest in about 3.5 min and 0.5 C in about 4.5 min; after the int8 holds sooner;")
    print("a cold hold's end reaches 55 C in about half a minute, most of it inside the 25 s of queries after every run. E161's measured rest (G1Q, 13 min):")
    print("50 C about 2 min after the hold and its 47 C floor from about 4.5 min on. So the cold gate's bound is 360 s and a rest is planned at 4 min.")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
