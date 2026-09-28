#!/usr/bin/env python3
"""Idle board power against die temperature, per card, from the version-3 cooling cycles (E44:
docs/reports/data/2026-09-25-claims-v3/raw/<card>/idle/p1..p3): heat to 88 C, then 900 s idle at 600 MHz.

Idle samples: more than 5 s after the heater's last launch, minion clock 600 MHz. Per whole degree of the 34-sensor mean,
the median board power. Then:
  - the slope dP/dT (W per C) from a straight line over each 10 C band;
  - P(T) = P_fix + A * exp(T / T_L) fitted on a grid of T_L (least squares, P_fix and A free and >= 0), reporting the
    best T_L, the doubling temperature of the exponential part (T_L ln 2) and the rms. The split between P_fix and
    the exponential is weakly determined by idle data alone (docs/findings/11-thermal-model.md), so the T_L range
    whose rms is within 10% of the best is reported too.
Writes docs/reports/data/2026-09-28-overheating/analysis/idle_vs_temp.json.
Usage: python3 idle_vs_temp.py [docs/reports/data]
"""
import collections, glob, gzip, json, math, os, statistics as st, sys
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'idle_vs_temp.json')
BASE = os.path.join(ROOT, '2026-09-25-claims-v3/raw')
J = {}
GRID = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 60, 80, 120]

for card in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1'):
    bins = collections.defaultdict(list)
    for pd in sorted(glob.glob(os.path.join(BASE, card, 'idle', 'p*'))):
        L = [json.loads(l) for l in open(os.path.join(pd, 'launches.jsonl')) if l.strip()]
        if not L:
            continue
        t_last = max(x['t_end_ms'] for x in L)
        with gzip.open(os.path.join(pd, 'telemetry.jsonl.gz'), 'rt') as fh:
            for line in fh:
                s = json.loads(line)
                if s['t_ms'] < t_last + 5000 or (s.get('mhz') or {}).get('minion') != 600:
                    continue
                bins[s['temp_c']['minshire'][0]].append(s['board_w'])
    T = np.array(sorted(t for t in bins if len(bins[t]) >= 20), dtype=float)
    P = np.array([st.median(bins[int(t)]) for t in T])
    N = np.array([len(bins[int(t)]) for t in T])
    print('%s: idle %d samples, %d whole-degree bins %d-%d C; board %.2f W at %d C, %.2f W at %d C' %
          (card, int(N.sum()), len(T), T.min(), T.max(), P[0], T[0], P[-1], T[-1]))
    for lo in range(int(T.min()) // 10 * 10, int(T.max()) + 1, 10):
        m = (T >= lo) & (T < lo + 10)
        if m.sum() >= 4:
            b = np.polyfit(T[m], P[m], 1)[0]
            print('   slope %d-%d C: %.3f W/C' % (lo, lo + 10, b))
    fits = []
    for TL in GRID:
        X = np.column_stack([np.ones_like(T), np.exp((T - 80.0) / TL)])
        c, *_ = np.linalg.lstsq(X * np.sqrt(N)[:, None], P * np.sqrt(N), rcond=None)
        if c[0] < 0 or c[1] < 0:
            continue
        rms = math.sqrt(float(np.sum(N * (X @ c - P) ** 2) / N.sum()))
        fits.append((rms, TL, c[0], c[1]))
    fits.sort()
    rms, TL, a, b = fits[0]
    ok = sorted(f[1] for f in fits if f[0] <= 1.10 * rms)
    print('   best fit: P = %.2f + %.2f exp((T-80)/%d)  rms %.3f W; exponential part doubles every %.1f C '
          '(T_L within 10%% of best rms: %d-%d C -> doubling %.0f-%.0f C); at 80 C the exponential part is %.1f W, slope %.2f W/C' %
          (a, b, TL, rms, TL * math.log(2), ok[0], ok[-1], ok[0] * math.log(2), ok[-1] * math.log(2), b, b / TL))
    # total idle power: temperature rise that doubles it, from the fit, starting at the lowest bin
    Pfit = lambda t: a + b * math.exp((t - 80.0) / TL)
    t0 = T.min()
    t = t0
    while Pfit(t) < 2 * Pfit(t0) and t < 200:
        t += 0.5
    print('   total idle board power doubles from %d C (%.1f W) by %.1f C (extrapolated past %d C if above it)' %
          (t0, Pfit(t0), t, T.max()))
    for tq in (100, 116):
        print('   extrapolated idle board power at %d C: %.1f W' % (tq, Pfit(tq)))
    J[card] = {'samples': int(N.sum()), 'bins': [{'T': int(t), 'n': int(n), 'board_w': float(p)} for t, n, p in zip(T, N, P)],
               'fit': {'P_fix': round(float(a), 3), 'A': round(float(b), 3), 'T_L': TL, 'rms': round(rms, 4),
                       'doubling_C': round(TL * math.log(2), 1)},
               'T_L_within_10pct': [ok[0], ok[-1]], 'doubling_range_C': [round(ok[0] * math.log(2), 1), round(ok[-1] * math.log(2), 1)],
               'extrapolated_w': {str(tq): round(Pfit(tq), 1) for tq in (100, 116, 120)},
               'total_doubles_from': [int(t0), round(Pfit(t0), 1), t]}
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
