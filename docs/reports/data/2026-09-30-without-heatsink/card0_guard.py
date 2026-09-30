#!/usr/bin/env python3
"""Card 0 (aifoundry1, firmware 1.4.1) at 300 MHz: idle board and rail power against the die mean,
from the read-only guard samples that E52/E53 recorded (docs/reports/data/*/raw/aifoundry1-c1/**/guard.jsonl.gz)."""
import gzip, json, glob, os, collections
import numpy as np
R = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))   # docs/reports/data
files = sorted(glob.glob(R + '/**/guard.jsonl.gz', recursive=True))
rows = []
for f in files:
    with gzip.open(f, 'rt') as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            try:
                if d['mhz']['minion'] != 300:
                    continue
                rows.append((d['temp_c']['minshire'][0], d['board_w'], d['sp']['minion_w'][0], d['sp']['sram_w'][0],
                             d['sp']['noc_w'][0], d['temp_c']['ioshire'][0], d['die_mv']['minion'], d['t_ms']))
            except Exception:
                pass
a = np.array(rows, dtype=float)
print(f'{len(files)} guard files, {len(a)} samples at 300 MHz')
T, B, M, S, N = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
print(f'die mean {T.min():.0f}-{T.max():.0f} C; board {B.min():.2f}-{B.max():.2f} W (median {np.median(B):.2f}); '
      f'minion {np.median(M):.2f} W, SRAM {np.median(S):.2f} W, NoC {np.median(N):.2f} W; rails sum {np.median(M+S+N):.2f} W; '
      f'unmetered {np.median(B-(M+S+N)):.2f} W; minion die mV {np.median(a[:,6]):.0f}')
by = collections.defaultdict(list)
for t, b, m, s, n in zip(T, B, M, S, N):
    by[int(t)].append((b, m + s + n, m, s, n))
print('per whole-degree bin: T  n  board  rails  minion  sram  noc')
xs, yb, yr = [], [], []
for t in sorted(by):
    v = np.array(by[t])
    print(f'  {t}  {len(v):5d}  {v[:,0].mean():.2f}  {v[:,1].mean():.2f}  {v[:,2].mean():.3f}  {v[:,3].mean():.3f}  {v[:,4].mean():.3f}')
    if len(v) >= 30:
        xs.append(t); yb.append(v[:, 0].mean()); yr.append(v[:, 1].mean())
if len(xs) >= 2:
    pb = np.polyfit(xs, yb, 1); pr = np.polyfit(xs, yr, 1)
    print(f'bin-mean slope (bins with >=30 samples, {xs[0]}-{xs[-1]} C): board {pb[0]:.3f} W/C, metered rails {pr[0]:.3f} W/C')
