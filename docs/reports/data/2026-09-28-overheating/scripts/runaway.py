#!/usr/bin/env python3
"""Where does leakage make an idle aifoundry2 heat itself without limit? (derived, extrapolated past the data)

Steady state of the lumped model (docs/reports/data/2026-09-21-horace-aifoundry2/model.json):
  T = T_amb + R_total * P_idle(T),   P_idle(T) = P_fix + A_leak_at_80 * exp((T - 80) / T_L)
f(T) = T_amb + R*P(T) - T. f > 0: the die warms; f < 0: it cools. A zero with f' < 0 is a stable rest temperature,
one with f' > 0 the runaway threshold: above it an idle card at this clock and voltage heats until something else acts.
f' = R * dP/dT - 1 = loop gain - 1. T_amb: the model's session intercepts (22.8 C main session, 28.0 C afternoon).
The fit spans idle readings of 62-88 C; above 88 C this is an extrapolation.
Writes docs/reports/data/2026-09-28-overheating/analysis/runaway.json.
Usage: python3 runaway.py [docs/reports/data]
"""
import json, math, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'runaway.json')
m = json.load(open(os.path.join(ROOT, '2026-09-21-horace-aifoundry2/model.json')))
pw, R = m['power'], m['R_total']
P = lambda T: pw['P_fix'] + pw['A_leak_at_80'] * math.exp((T - 80.0) / pw['T_L'])
dP = lambda T: pw['A_leak_at_80'] / pw['T_L'] * math.exp((T - 80.0) / pw['T_L'])
print('model: P_fix %.2f W, A_leak_at_80 %.2f W, T_L %.0f C, R_total %.3f C/W, loop_gain_at_80 (file) %s' %
      (pw['P_fix'], pw['A_leak_at_80'], pw['T_L'], R, m.get('loop_gain_at_80')))
T1 = 80 + pw['T_L'] * math.log(1 / (R * dP(80)))
print('loop gain R*dP/dT = 1 at %.1f C' % T1)
J = {'model': {'P_fix': pw['P_fix'], 'A_leak_at_80': pw['A_leak_at_80'], 'T_L': pw['T_L'], 'R_total': R,
                'loop_gain_at_80': m.get('loop_gain_at_80')}, 'gain_one_at_c': round(T1, 1), 'equilibria': {}}
T_ambs = sorted({round(v, 1) for v in [22.8, 28.0]})
for Ta in T_ambs:
    f = lambda T: Ta + R * P(T) - T
    zeros, prev = [], None
    T = 20.0
    while T <= 160:
        v = f(T)
        if prev is not None and (prev < 0) != (v < 0):
            lo, hi = T - 0.1, T
            for _ in range(60):
                mid = (lo + hi) / 2
                if (f(lo) < 0) == (f(mid) < 0):
                    lo = mid
                else:
                    hi = mid
            z = (lo + hi) / 2
            zeros.append((round(z, 1), 'stable rest' if R * dP(z) < 1 else 'runaway threshold', round(P(z), 1)))
        prev = v
        T += 0.1
    print('T_amb %.1f C: equilibria %s; the largest cooling margin f = %.1f C at %.0f C' %
          (Ta, zeros, min(f(t) for t in range(40, 140)), min(range(40, 140), key=f)))
    J['equilibria'][str(Ta)] = [{'T': z[0], 'kind': z[1], 'P_w': z[2]} for z in zeros]
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
