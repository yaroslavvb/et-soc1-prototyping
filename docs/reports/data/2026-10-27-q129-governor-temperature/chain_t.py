#!/usr/bin/env python3
"""Q129 — what E64-T1's temperature term does to the chain closure's burst prediction and sustained clamp.

Re-runs section 6 of docs/reports/data/2026-10-27-chain-closure/chain.py with ONE change: the board power
at a clock carries E66's leakage term at the die temperature the cell is actually at, instead of being
held at the 58 C the referral used. chain.py itself is untouched; its committed chain.json supplies every
input, so nothing here is refitted.

  python3 chain_t.py <chain.json> <figures-t1.json> --out <chain-t1.json>
"""
import argparse
import json
import math

A80, T_L, V_IDLE = 20.41, 29.8, 0.519        # E66's measured idle split on this card
T_REF = 58.0
P_CAP = 65.0                                  # the TDP the card reads back (chain.py)
GAMMAS = (0.0, 2.0, 3.0)
TRIPS = (65.5, 66.0)                          # E64's registered sustained reading, and its R3 trip
LAUNCH = (50.0, 56.0, 58.0)                   # E64's own LAD launch readings, and the referral's 58 C


def lam(T, v, g):
    return A80 * math.exp((T - 80.0) / T_L) * (v / V_IDLE) ** g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chain")
    ap.add_argument("t1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C = json.load(open(a.chain))["chain"]
    Bf = {int(k): v for k, v in C["B_f_W"].items()}
    TH = C["die_line"]
    v600, v800 = C["v600"], C["v800_mean"]
    # chain.py's own dynamic terms at 600 MHz, recovered from its committed predicted board powers
    dyn = {k: C["predicted_board_W"]["600"][k] - Bf[600] for k in ("zeros", "ones", "randn")}

    def vlin(f):
        return v600 + (v800 - v600) * (f - 600) / 200.0

    def B_at(f):
        k = sorted(Bf)
        if f <= k[0]:
            return Bf[k[0]]
        for x, y in zip(k, k[1:]):
            if f <= y:
                return Bf[x] + (Bf[y] - Bf[x]) * (f - x) / (y - x)
        return Bf[k[-1]]

    def P_of(f, d600, T=T_REF, g=0.0):
        base = B_at(f) + d600 * (f / 600.0) * ((vlin(f) / v600) ** 2)
        return base + lam(T, vlin(f), g) - lam(T_REF, vlin(f), g)

    def settle(d600, cap, T=T_REF, g=0.0):
        lo, hi = 600.0, 800.0
        if P_of(hi, d600, T, g) <= cap:
            return hi
        if P_of(lo, d600, T, g) >= cap:
            return lo
        for _ in range(90):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if P_of(m, d600, T, g) <= cap else (lo, m)
        return lo

    out = {"inputs": {"B_f_W": Bf, "die_line": TH, "v600": v600, "v800_mean": v800, "dyn600_W": dyn,
                      "power_cap_W": P_CAP, "leak_law": {"A80_W": A80, "T_L_C": T_L, "V_idle_V": V_IDLE},
                      "registered": {"burst_ratio": C["predicted_ratio"]["from_measured_anchors"]["burst"],
                                     "burst_measured_comparators": C["burst_measured_comparators"],
                                     "sustained_clamp_window_W": C["sustained_is_a_clamp"]["clamp_window_W"],
                                     "sustained_window_width_W": C["sustained_is_a_clamp"]["window_width_W"],
                                     "sustained_cap_W": C["sustained_cap_W"]}},
           "burst": {}, "sustained": {}}

    # ── BURST: the die sits at its launch reading over a 6.5 s run, so the only change is the
    #    referral's own offset between that reading and the 58 C the powers were referred to.
    for g in GAMMAS:
        for T0 in LAUNCH:
            fz = settle(dyn["zeros"], P_CAP, T0, g)
            fr = settle(dyn["randn"], P_CAP, T0, g)
            fo = settle(dyn["ones"], P_CAP, T0, g)
            out["burst"]["g%.1f_T%.0f" % (g, T0)] = {
                "gamma": g, "die_c": T0, "zeros_mhz": round(fz, 1), "ones_mhz": round(fo, 1),
                "randn_mhz": round(fr, 1), "ratio": fz / fr,
                "leak_offset_at_800_W": round(lam(T0, vlin(800), g) - lam(T_REF, vlin(800), g), 3)}

    # ── SUSTAINED: the cap is a DIE READING, not a board power. At equilibrium the die sits at the
    #    trip, so the clock is the one whose power AT THE TRIP TEMPERATURE equals (trip - a) / R.
    for g in GAMMAS:
        for trip in TRIPS:
            capW = (trip - TH["a_c"]) / TH["k_c_per_w"]
            fz = settle(dyn["zeros"], capW, trip, g)
            fr = settle(dyn["randn"], capW, trip, g)
            fo = settle(dyn["ones"], capW, trip, g)
            lo = P_of(800, dyn["zeros"], trip, g)
            hi = P_of(600, dyn["randn"], trip, g)
            out["sustained"]["g%.1f_trip%.1f" % (g, trip)] = {
                "gamma": g, "trip_c": trip, "cap_W_at_trip": round(capW, 3),
                "zeros_mhz": round(fz, 1), "ones_mhz": round(fo, 1), "randn_mhz": round(fr, 1),
                "ratio": fz / fr,
                "clamp_window_W": [round(lo, 3), round(hi, 3)], "window_width_W": round(hi - lo, 3),
                "cap_inside_window": bool(lo <= capW <= hi)}

    json.dump(out, open(a.out, "w"), indent=1)
    reg = out["inputs"]["registered"]
    print("chain closure, registered: burst ratio %.4f against measured %.3f-%.3f; sustained clamp window "
          "%.2f-%.2f W (width %.2f), cap %.1f W"
          % (reg["burst_ratio"], min(reg["burst_measured_comparators"].values()),
             max(reg["burst_measured_comparators"].values()), reg["sustained_clamp_window_W"][0],
             reg["sustained_clamp_window_W"][1], reg["sustained_window_width_W"], reg["sustained_cap_W"]))
    print("")
    print("BURST (65 W TDP; the die is at its launch reading for 6.5 s)")
    print("  %-7s %-7s %9s %9s %9s %8s  %s" % ("gamma", "die C", "zeros", "ones", "random", "ratio",
                                                "leak offset at 800 MHz"))
    for k, v in out["burst"].items():
        print("  %-7.1f %-7.0f %9.1f %9.1f %9.1f %8.4f  %+.3f W"
              % (v["gamma"], v["die_c"], v["zeros_mhz"], v["ones_mhz"], v["randn_mhz"], v["ratio"],
                 v["leak_offset_at_800_W"]))
    print("")
    print("SUSTAINED (the cap is a die reading; the power curve is evaluated AT that reading)")
    print("  %-7s %-7s %9s %9s %9s %9s %8s %-22s %s"
          % ("gamma", "trip C", "cap W", "zeros", "ones", "random", "ratio", "clamp window W", "width"))
    for k, v in out["sustained"].items():
        print("  %-7.1f %-7.1f %9.2f %9.1f %9.1f %9.1f %8.4f %-22s %.2f"
              % (v["gamma"], v["trip_c"], v["cap_W_at_trip"], v["zeros_mhz"], v["ones_mhz"],
                 v["randn_mhz"], v["ratio"], "%.2f-%.2f" % tuple(v["clamp_window_W"]),
                 v["window_width_W"]))
    print("")
    print("  E64 measured sustained, fp32, 1,024 harts: zeros 800 MHz, ones 738, random 600")
    return 0


if __name__ == "__main__":
    main()
