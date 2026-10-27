#!/usr/bin/env python3
"""Q129 fix pass: E64-T1's sustained numbers as a (gamma, trip) SURFACE, not a single pairing.

The first Q129 draft published model E64-T1 at one trip (66.0 C) and quoted its headline closure at one
voltage exponent (gamma 3), while its own text called gamma unidentified and promised 65.5 C "as a
sensitivity" that was never run. Q129's verifier ran the 65.5 C variant and found it material: the
nine-cell rms, which gamma closes the fp32 all-ones cell, and the size of the fp16 miss all move. This
file prints the surface over both declared parameters from the two committed figures files, so every
claim in the README is read off a table rather than off one corner of it.

  python3 trip_surface.py <figures-t1.json> <figures-t1-trip655.json> --out trip-surface.json

Both inputs are outputs of tools/claims-v3/hpl/surface_hpl_t.py on E64's committed results.json, the
second with --trip 65.5. Nothing is fitted here.
"""
import argparse
import json

CELLS = ("fp32-ones-1024", "fp16-ones-1024", "int8-randn-1024", "fp16-zeros-1024", "fp16-randn-1024")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figures", nargs="+", help="figures-t1 json files, one per trip")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    F = {}
    for p in a.figures:
        d = json.load(open(p))
        F[d["t_trip_c"]] = d
    trips = sorted(F)
    gammas = sorted(F[trips[0]]["variants"], key=float)

    out = {"trips_c": trips, "gammas": [float(g) for g in gammas],
           "note": ("gamma (the leakage law's voltage exponent) and the thermal trip are BOTH declared, "
                    "not fitted. Every sustained number below is out of sample: the cell's whole "
                    "workload label is dropped from B_f, the die line, tau_th and the governor, and its "
                    "switching term is solved against the held-out B_f from its own cool-die bursts."),
           "sustained_oos_rms_mhz": {}, "sustained_informative_oos_rms_mhz": {},
           "registered_cap_rms_mhz": {}, "registered_cap_informative_rms_mhz": {},
           "burst_oos_rms_mhz": {}, "cells": {}}
    for t in trips:
        for g in gammas:
            V = F[t]["variants"][g]
            k = "trip%.1f_g%s" % (t, g)
            out["sustained_oos_rms_mhz"][k] = V["sustained_oos_rms_mhz"]
            out["sustained_informative_oos_rms_mhz"][k] = V["sustained_informative_oos_rms_mhz"]
            out["registered_cap_rms_mhz"][k] = V["sustained_registered_rms_mhz"]
            out["registered_cap_informative_rms_mhz"][k] = V["sustained_informative_registered_rms_mhz"]
            out["burst_oos_rms_mhz"][k] = V["burst_oos_rms_mhz"]
            for x in V["sustained"]:
                if x["label"] not in CELLS:
                    continue
                e = out["cells"].setdefault(x["label"], {"meas_mhz": x["meas_mhz"],
                                                         "registered_cap_mhz": x["registered_cap_mhz"],
                                                         "t1_oos_mhz": {}, "miss_mhz": {}})
                e["t1_oos_mhz"][k] = x["t1_oos_mhz"]
                e["miss_mhz"][k] = (round(x["t1_oos_mhz"] - x["meas_mhz"], 1)
                                    if x["t1_oos_mhz"] is not None else None)
    for lab, e in out["cells"].items():
        m = [v for v in e["miss_mhz"].values() if v is not None]
        e["miss_range_mhz"] = [min(m), max(m)]
        e["closes_somewhere"] = min(abs(x) for x in m) <= 5.0
        e["registered_miss_mhz"] = (round(e["registered_cap_mhz"] - e["meas_mhz"], 1)
                                    if e["registered_cap_mhz"] is not None else None)
    r = [v for v in out["sustained_oos_rms_mhz"].values() if v is not None]
    ri = [v for v in out["sustained_informative_oos_rms_mhz"].values() if v is not None]
    reg = max(v for v in out["registered_cap_rms_mhz"].values())
    regi = max(v for v in out["registered_cap_informative_rms_mhz"].values())
    out["summary"] = {
        "sustained_oos_rms_range_mhz": [min(r), max(r)],
        "registered_cap_rms_mhz": reg,
        "improvement_factor_range": [round(reg / max(r), 1), round(reg / min(r), 1)],
        "informative_oos_rms_range_mhz": [min(ri), max(ri)],
        "informative_registered_cap_rms_mhz": regi,
        "informative_improvement_factor_range": [round(regi / max(ri), 1), round(regi / min(ri), 1)]}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)

    cols = ["trip%.1f_g%s" % (t, g) for t in trips for g in gammas]
    print("E64-T1 over its two DECLARED parameters: the voltage exponent gamma and the thermal trip.")
    print("Every number is out of sample. 'informative' excludes the sustained cells where the")
    print("registered cap and T1 both already sit on the measurement (pure clamps, exact zeros).")
    print("")
    hdr = "%-34s" % "" + "".join("%12s" % c.replace("trip", "") for c in cols)
    print(hdr)
    for key, lab in (("sustained_oos_rms_mhz", "sustained rms, 9 cells"),
                     ("sustained_informative_oos_rms_mhz", "sustained rms, 5 informative"),
                     ("burst_oos_rms_mhz", "burst rms, leave-one-label-out")):
        print("%-34s" % lab + "".join("%12s" % out[key][c] for c in cols))
    print("%-34s" % "E64 registered cap, 9 cells" + "".join("%12s" % out["registered_cap_rms_mhz"][c]
                                                            for c in cols))
    print("%-34s" % "E64 registered cap, 5 informative"
          + "".join("%12s" % out["registered_cap_informative_rms_mhz"][c] for c in cols))
    print("")
    print("%-18s %7s %9s %s" % ("cell", "meas", "E64 cap", "T1 out of sample, MHz (miss)"))
    for lab, e in out["cells"].items():
        print("%-18s %7.1f %9s  %s" % (lab, e["meas_mhz"], e["registered_cap_mhz"],
                                       "  ".join("%s %.1f(%+.1f)" % (c.replace("trip", ""),
                                                                     e["t1_oos_mhz"][c], e["miss_mhz"][c])
                                                 for c in cols)))
    print("")
    s = out["summary"]
    print("sustained rms over the 9 cells: E64's cap %s MHz -> T1 %s-%s, a factor of %s-%s"
          % (s["registered_cap_rms_mhz"], s["sustained_oos_rms_range_mhz"][0],
             s["sustained_oos_rms_range_mhz"][1], s["improvement_factor_range"][0],
             s["improvement_factor_range"][1]))
    print("over the 5 that discriminate:   E64's cap %s MHz -> T1 %s-%s, a factor of %s-%s"
          % (s["informative_registered_cap_rms_mhz"], s["informative_oos_rms_range_mhz"][0],
             s["informative_oos_rms_range_mhz"][1], s["informative_improvement_factor_range"][0],
             s["informative_improvement_factor_range"][1]))
    return 0


if __name__ == "__main__":
    main()
