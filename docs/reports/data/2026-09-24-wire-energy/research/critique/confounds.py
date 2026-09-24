#!/usr/bin/env python3
"""Leakage-correction share of the wire slope; temperature gap; a per-time vs per-hop regression on the NoC rail;
and the per-pass scatter of the random-zeros difference, from catalogue.json bursts."""
import json, numpy as np, collections
C = json.load(open('/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-23-energy-manual/catalogue.json'))
LINKS_XY = {1: 32, 2: 57, 3: 79, 4: 90, 5: 97, 6: 105, 8: 80}   # links used (XY), from linkload.py (link_hops/mean)
lk = json.load(open('linkload.json'))
for d in LINKS_XY: LINKS_XY[d] = lk[f'any/d{d}']['XY']['links_used']
def fit(X, y):
    c, *_ = np.linalg.lstsq(X, y, rcond=None); r = y - X @ c
    return c, float(np.sqrt(np.mean(r**2)))
DS = (1, 2, 3, 4, 5, 6, 8)
for host, card in C['cards'].items():
    s = card['summary']
    print(f"\n=== {host}")
    lc, raw, T = {}, {}, {}
    for o in ('zeros', 'random'):
        for d in DS:
            v = s[f'wire/hop{d}/{o}']; bw = v['bytes_per_s']['mean']
            lc[(o, d)] = v['leak_correction_w']['mean'] / bw * 1e12
            raw[(o, d)] = (v['over_idle_w']['mean'] + v['leak_correction_w']['mean']) / bw * 1e12
            T[(o, d)] = v['die_c_busy']['mean']
    print(" d: leak-corr pJ/B zeros random diff | Tbusy zeros random")
    for d in DS:
        print(f" {d}: {lc[('zeros',d)]:.2f} {lc[('random',d)]:.2f} {lc[('random',d)]-lc[('zeros',d)]:.2f} | {T[('zeros',d)]:.1f} {T[('random',d)]:.1f}")
    x = np.array(DS, float); X = np.vstack([np.ones_like(x), x]).T
    for o in ('zeros', 'random'):
        c, r = fit(X, np.array([raw[(o, d)] for d in DS]))
        print(f"  no leakage correction, {o}: slope {c[1]:.3f} pJ/B/hop")
    c, r = fit(X, np.array([raw[('random', d)] - raw[('zeros', d)] for d in DS]))
    print(f"  no leakage correction, diff: slope {c[1]:.3f}")
    c, r = fit(X, np.array([lc[('random', d)] - lc[('zeros', d)] for d in DS]))
    print(f"  leakage correction alone, diff: slope {c[1]:.3f} (it is SUBTRACTED)")
    # NoC rail power model: P = e_hop*BW*d + e_end*BW + p_link*links_used  (W, bytes/s)
    for o in ('zeros', 'random'):
        P = np.array([s[f'wire/hop{d}/{o}']['rails_over_w']['noc_w']['mean'] for d in DS])
        BW = np.array([s[f'wire/hop{d}/{o}']['bytes_per_s']['mean'] for d in DS])
        L = np.array([LINKS_XY[d] for d in DS], float)
        c2, r2 = fit(np.vstack([BW * x, BW]).T, P)
        c3, r3 = fit(np.vstack([BW * x, BW, L]).T, P)
        print(f"  NoC rail {o}: 2-term e_hop={c2[0]*1e12:.3f} pJ/B/hop e_end={c2[1]*1e12:.2f} pJ/B rms {r2:.3f} W |"
              f" 3-term e_hop={c3[0]*1e12:.3f} e_end={c3[1]*1e12:.2f} p_link={c3[2]*1e3:.1f} mW/link rms {r3:.3f} W")
    # per-pass scatter of random-zeros per-byte at each d
    B = card and C['bursts'][host]
    by = collections.defaultdict(list)
    for b in B:
        if b['cfg'].startswith('wire/'): by[b['cfg']].append(b['pj_per_byte'])
    print("  per-pass pJ/B:", {k: [round(v, 2) for v in vs] for k, vs in sorted(by.items())})
