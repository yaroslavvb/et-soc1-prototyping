#!/usr/bin/env python3
"""POST HOC, a reading and not a result (Q142's records, Wed 4 Nov 2026): are the frozen heat chain's misses on held plateaus a
gain (growing with the rise, through zero) or a session level (flat in the rise)? No registered rule tests one against the other.

Reads only `docs/reports/data/2026-11-04-q142m-m10/heldout-m10.json` > heat_d_chain_gain.holds (lab 6829c9ba, listed in that
directory's SHA256SUMS): per hold, the measured plateau rise R (deg C) and the error e = measured - Q138(t)'s chain given the
measured watts (deg C), with M10's own `fitted` flag. Writes nothing; prints:
  1. the large rises (fitted, R >= 10.0 deg C, the selection fit_m10.py uses for term d), each with e and e/R;
  2. per session, every fitted hold, and where a session has 3 or more fitted holds three least-squares readings of e against R:
     a level and a gain together (e = a + g R), a level alone (e = a0) and a gain alone through zero (e = g0 R), each with its
     residual rms. Two holds give the two one-parameter readings only.
Standard library only. Usage: python3 -I posthoc_heat_level_gain.py [path to heldout-m10.json]"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "2026-11-04-q142m-m10", "heldout-m10.json")
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
holds = json.load(open(path, encoding="utf-8"))["heat_d_chain_gain"]["holds"]
fit = [h for h in holds if h.get("fitted") and h.get("R_C") is not None and h.get("e_C") is not None]


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


print("POST HOC (Q142's records): the frozen chain's misses given the watts, from heldout-m10.json > heat_d_chain_gain.holds")
print(f"{len(holds)} holds listed, {len(fit)} fitted (M10's own flag)\n")
print("1. The large rises (fitted, R >= 10.0 C), e = measured - chain given the watts:")
big = sorted((h for h in fit if h["R_C"] >= 10.0), key=lambda h: (h["session"], h["hold"]))
for h in big:
    print(f"   {h['session']:6s} {h['card_kind']:10s} {h['hold']:11s} R {h['R_C']:6.2f} C  e {h['e_C']:+.3f} C  e/R {100 * h['e_C'] / h['R_C']:+.2f}%")
rel = [100 * h["e_C"] / h["R_C"] for h in big]
low = [h for h in big if h["e_C"] / h["R_C"] >= 0.01]
print(f"   {len(big)} large rises; {len(low)} read 1% or more low (e/R {min(100 * h['e_C'] / h['R_C'] for h in low):.2f}-"
      f"{max(100 * h['e_C'] / h['R_C'] for h in low):.2f}%); the rest: "
      + ", ".join(f"{h['session']} {h['hold']} {100 * h['e_C'] / h['R_C']:+.2f}%" for h in big if h not in low))
print(f"   rms of e over the {len(big)}: {rms([h['e_C'] for h in big]):.4f} C\n")

print("2. Per session: e against R (a level, a gain, or both)")
by = {}
for h in fit:
    by.setdefault((h["session"], h["card_kind"]), []).append(h)
for (s, c), v in sorted(by.items()):
    v.sort(key=lambda h: h["R_C"])
    R = [h["R_C"] for h in v]
    E = [h["e_C"] for h in v]
    print(f"   {s} ({c}): " + ", ".join(f"{h['hold']} R {h['R_C']:.2f} e {h['e_C']:+.3f}" for h in v))
    if len(v) >= 2:
        a0 = sum(E) / len(E)
        r_level = rms([e - a0 for e in E])
        g0 = sum(e * r for e, r in zip(E, R)) / sum(r * r for r in R)
        r_gain = rms([e - g0 * r for e, r in zip(E, R)])
        line = f"      a level alone: a0 {a0:+.3f} C, residual rms {r_level:.3f} C; a gain alone: g0 {100 * g0:+.2f}% of R, residual rms {r_gain:.3f} C"
        if len(v) >= 3:
            n = len(v); mr = sum(R) / n; me = sum(E) / n
            sxx = sum((r - mr) ** 2 for r in R)
            g = sum((r - mr) * (e - me) for r, e in zip(R, E)) / sxx
            a = me - g * mr
            r_both = rms([e - (a + g * r) for r, e in zip(R, E)])
            line += f"; both: a {a:+.3f} C and g {100 * g:+.2f}% of R, residual rms {r_both:.3f} C"
        print(line)
print("\nRead: within one session a pure gain makes e grow with R through zero, and a session level makes e flat in R. With two")
print("to five holds a session, these are readings, not tests; a registered test needs two or more rise levels in each session.")
