#!/usr/bin/env python3
"""fit.py: the runaway's model. Leakage: P(T) = a + b*exp(c*T), fitted to all records. Heat balance on the first 45
minutes: C dT/dt = P - (T - Ta)/R (C, R, Ta by least squares). Prints the fits and where heating and cooling meet."""
import json, os, numpy as np
rs = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.jsonl"))]
rs = [r for r in rs if r["cards"][0].get("die") is not None]
t = np.array([r["t"] for r in rs]) / 1000.0; t -= t[0]
T = np.array([r["cards"][0]["die"] for r in rs], float); P = np.array([r["cards"][0]["w"] for r in rs], float)
best = None
for c in np.linspace(0.01, 0.12, 111):
    X = np.c_[np.ones_like(T), np.exp(c * T)]; k, *_ = np.linalg.lstsq(X, P, rcond=None); e = ((X @ k - P) ** 2).sum()
    if best is None or e < best[0]: best = (e, c, k)
e, c, (a, b) = best
print(f"P(T) = {a:.1f} + {b:.3f} exp({c:.3f} T) W; rms {np.sqrt(e / len(T)):.2f} W; excess doubles every {np.log(2) / c:.0f} C")
w = 12; dT = np.full_like(T, np.nan); dT[w:-w] = (T[2 * w:] - T[:-2 * w]) / (t[2 * w:] - t[:-2 * w])
ok = ~np.isnan(dT) & (t < 45 * 60)
k, *_ = np.linalg.lstsq(np.c_[P[ok], T[ok], np.ones(ok.sum())], dT[ok], rcond=None)
C = 1 / k[0]; R = -1 / (k[1] * C); Ta = k[2] * R * C
print(f"heat balance: C {C:.0f} J/C, R {R:.2f} C/W, air {Ta:.1f} C, time constant {R * C / 60:.1f} min")
Ts = np.linspace(40, 140, 10001); net = a + b * np.exp(c * Ts) - (Ts - Ta) / R
print(f"closest approach of heating and cooling: {net.min():.2f} W at {Ts[net.argmin()]:.0f} C ({'no' if net.min() > 0 else 'a'} stable point)")
for ta in (48, 45, 40, 31):
    n = a + b * np.exp(c * Ts) - (Ts - ta) / R; s = np.where(np.diff(np.sign(n)) < 0)[0]
    print(f"  with air at {ta} C it would settle at {Ts[s[0]]:.0f} C" if len(s) else f"  air {ta} C: no stable point")
