#!/usr/bin/env python3
"""Predict the power and heating of a custom TensorFMA32 workload on the ET-SoC-1 card from its operands alone.

    predict_heat.py --model model.json --tiles my.bin [--active 1024] [--start 80] [--cap 90] [--seconds 600]
    predict_heat.py --model model.json --toggles toggles.json --pattern randn ...

Steps: (1) replay the 16x16 A and B tiles through the multiply-add RTL (rtl-sim/fma_toggle) and count the four
kinds of flip per op; (2) turn flip rates into switching watts with the fitted energies; (3) add leakage at the
die temperature and run the fitted thermal network forward from an idle die at --start degrees.
Prints the flip counts, the switching power, the board power at the start temperature, the temperature after
10 s, 1 min and 10 min, the time to --cap, and the duty cycle that would hold the die at the start temperature.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FMA = os.path.join(HERE, "..", "..", "rtl-sim", "fma_toggle")
F_OP = 600e6 / 546.0
CLASSES = ["ffclk", "mult", "rest", "bus"]
MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")


def flips_from_tiles(path):
    sys.path.insert(0, FMA)
    import toggles as tg
    pts = [tg.run("custom", path, n0, 4, 1) for n0 in (1000, 400000)]
    out = {}
    for k in ("ff_clocked", "bus", "lane_valid", "nets"):
        out[k] = sum(p[k] for p in pts) / len(pts)
    mult = sum(sum(v for b, v in p["by_block"].items() if any(s in b for s in MULT_BLOCKS)) for p in pts) / len(pts)
    return {"ffclk": out["ff_clocked"], "mult": mult, "rest": out["nets"] - mult, "bus": out["bus"], "valid": out["lane_valid"]}


def flips_from_toggles(tog, pattern):
    m = tog[pattern]["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(s in k for s in MULT_BLOCKS))
    return {"ffclk": m["ff_clocked"], "mult": mult, "rest": m["nets"] - mult, "bus": m["bus"], "valid": m["lane_valid"]}


def predict(model, flips, active=1024, start=80.0, cap=90.0, seconds=600.0):
    pw, taus, R, T_amb = model["power"], model["taus"], model["R"], model["T_amb"]
    e = pw["e_fJ"]
    rate = {c: flips[c] * F_OP * active / 1e15 for c in CLASSES}                  # 1e15 events per second, chip-wide
    parts = {c: e[c] * rate[c] for c in CLASSES}                                  # watts
    p_dyn = sum(parts.values()) + pw["p_sm_full_chip"] * active / 1024.0
    leak = lambda T: pw["A_leak_at_80"] * math.exp((min(T, 110.0) - 80.0) / pw["T_L"])
    p_idle = pw["P_fix"] + leak(start)
    # an idle die at `start`: fast stages settled at idle power, the rest of the rise held by the slow stages
    x = [Rk * p_idle if tau <= 25 else 0.0 for Rk, tau in zip(R, taus)]
    slow_R = sum(Rk for Rk, tau in zip(R, taus) if tau > 25) or 1.0
    rest = start - T_amb - sum(x)
    x = [xk if tau <= 25 else rest * Rk / slow_R for xk, Rk, tau in zip(x, R, taus)]
    dt = 0.1
    al = [1.0 - math.exp(-dt / tau) for tau in taus]
    T, t_cap, at = start, None, {}
    for n in range(int(seconds / dt)):
        p = pw["P_fix"] + leak(T) + p_dyn
        x = [xk + a * (Rk * p - xk) for xk, a, Rk in zip(x, al, R)]
        T = T_amb + sum(x)
        tnow = (n + 1) * dt
        for mark in (10, 60, 600):
            if abs(tnow - mark) < dt / 2:
                at[mark] = T
        if t_cap is None and T >= cap:
            t_cap = tnow
            break
    # duty cycle that holds the start temperature: average switching power equal to what an idle die at `start` sheds
    hold = max(0.0, (start - T_amb) / sum(R) - p_idle)
    return {"rate_1e15_per_s": rate, "watts_by_class": parts, "p_switching": p_dyn, "p_board_at_start": p_idle + p_dyn, "p_idle_at_start": p_idle,
            "T_at": at, "t_cap": t_cap, "sustainable_switching_w": hold, "duty_to_hold_start": min(1.0, hold / p_dyn) if p_dyn > 0 else 1.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tiles")
    ap.add_argument("--toggles")
    ap.add_argument("--pattern")
    ap.add_argument("--active", type=int, default=1024)
    ap.add_argument("--start", type=float, default=80.0)
    ap.add_argument("--cap", type=float, default=90.0)
    ap.add_argument("--seconds", type=float, default=600.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    model = json.load(open(a.model))
    if "T_amb" not in model:
        model["T_amb"] = model["sessions"][0]["T_amb"]
    flips = flips_from_tiles(a.tiles) if a.tiles else flips_from_toggles(json.load(open(a.toggles)), a.pattern)
    r = predict(model, flips, a.active, a.start, a.cap, a.seconds)
    if a.json:
        print(json.dumps({"flips_per_op": flips, **r}))
        return
    print(f"flips per op and minion: {flips['valid']:.0f} of 4,096 multiply-adds valid; {flips['ffclk']/1e6:.2f} M register bits clocked; "
          f"{flips['mult']/1e6:.1f} M tree toggles; {flips['rest']/1e6:.2f} M other toggles; {flips['bus']/1e3:.0f} k operand-word toggles")
    names = {"ffclk": "register clocking", "mult": "multiplier tree", "rest": "rest of the unit", "bus": "operand words"}
    print("switching power: " + ", ".join(f"{names[k]} {v:.1f} W" for k, v in r["watts_by_class"].items())
          + f", state machines {model['power']['p_sm_full_chip'] * a.active / 1024:.1f} W; total {r['p_switching']:.1f} W on {a.active} minions")
    print(f"board power at {a.start:.0f} C: {r['p_board_at_start']:.1f} W (idle {r['p_idle_at_start']:.1f} W)")
    print("die temperature from an idle die at %.0f C: " % a.start + ", ".join(f"{k} s: {v:.1f} C" for k, v in r["T_at"].items())
          + (f"; reaches {a.cap:.0f} C after {r['t_cap']:.0f} s" if r["t_cap"] else f"; stays under {a.cap:.0f} C for {a.seconds:.0f} s"))
    print(f"to hold {a.start:.0f} C indefinitely the card can shed {r['sustainable_switching_w']:.1f} W of switching: run this workload {100*r['duty_to_hold_start']:.0f}% of the time")


if __name__ == "__main__":
    main()
