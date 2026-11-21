#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) f01: THE MASK FEATURES of the nonparametric reference at every subset configuration (arm, mask) of rgm136's
cooperative gemmL loop among the points (work/points_all.json), by this lane's own code from the documented geometry, plus the DRAM
private/shared shares by layout2's committed walk code. No residual is read here.

Geometry (named; known = read from a committed source, assumed = this lane's modelling choice):
  - known: shire s's row group is s >> 2 (8 groups; A tiles are shared by a row group's shires) and its column group s & 3 (4 groups; B tiles
    shared by a column group's), from rgm136's kernel as verify-lay's v01_map.groups encodes it;
  - known: the mesh positions MARTY (workloads/nocbench/analyze.py: marty1885's map, 6 x 6, four empty cells);
  - known: the L3 law 110 + 12 x hops to the home, homes = PA[10:6] (all 32 shires), the lab's notes; the memory shires 0-3 one step off the
    north edge at x = 1-4 and 4-7 off the south edge in that map (docs/et-soc1-notes.md), placed at (1 + m % 4, -1) and (1 + m % 4, 6) as
    layout2's x01_hops.py places them;
  - known (derived here from the kernel's addresses, verify-lay's my_steps): every A and B tile of one op step has the same PA[10] (the parity of
    k), so a step's requests fall on one half of the 32 homes, each home of that half receiving one line of every tile: the per-home load of
    a step is exactly 12 n requested lines and 4 R + 8 C distinct lines (no home imbalance within a step for this kernel);
  - assumed: dimension-order (X then Y) routing on the MARTY mesh for the link loads, data flowing home -> shire, each active shire's traffic
    spread evenly over the 32 homes.
Features (M, the mask features; the placebo permutes them within each shape):
  n; R; C; rmax, cmax (the largest active row and column group); rimb = rmax / (n / R), cimb = cmax / (n / C);
  G1 = (110 + 12 hbar_act) / (110 + 12 hbar_full) - 1 (hbar = mean hop to the 32 homes); hlag = (Lmax_act - Lmean_act) / Lmean_full;
  spread = mean pairwise hop among the active shires (0 at one shire); bbox = the active shires' bounding box cells / 36;
  memd = mean over active shires of the mean hop to the 8 memory shires; link = the largest directed link load of the active set (the
  assumed routing, each active shire at the same rate) over the full chip's; dist_rel = (4 R + 8 C) / 64 (distinct lines per receiving home a step, over the full chip's);
  Fp, Fs = layout2's private and shared DRAM-served request shares at a 32 MB strict LRU (f02_private.private_shared, committed, imported
  unchanged; seeded from its committed out/private_shared.json where the configuration is there); LAG = hlag x Fp / (Fp + Fs) (0 when no fresh).
  (The shape context MB, NB, ln KB, the format and the clock are added by r_common.feature_rows; no elasticity feature is used: MM1-v3.2's
  elasticity of its op time to its memory costs reads 0.967-1.000 at every in-scope point, so it carries no information here.)
Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded, in a slot. Output: work/features.json, logs/f01.log.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import importlib.util
import itertools
import json
import os
import re
import sys
import time

import numpy as np

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
POSIMB = os.path.join(LAB, 'tools/matmul/mm1/v3.3-cands/posimb')
os.environ['LAYOUT2_LANE'] = LANE          # f02_private.py's LAB = LANE/work/lab = this lane's scratch clone
os.environ.setdefault('ET_LAB', LAB)
spec = importlib.util.spec_from_file_location('f02_private_committed', os.path.join(POSIMB, 'scripts/f02_private.py'))
F02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F02)
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULLM = 0xFFFFFFFF
MARTY = F02.MARTY
MEM = {m: (1 + (m % 4), -1 if m < 4 else 6) for m in range(8)}
FEATS_M = ('n', 'R', 'C', 'rmax', 'cmax', 'rimb', 'cimb', 'G1', 'hlag', 'spread', 'bbox', 'memd', 'link', 'dist_rel', 'Fp', 'Fs', 'LAG')


def hp(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HBAR = {s: float(np.mean([hp(MARTY[s], MARTY[h]) for h in range(32)])) for s in range(32)}
LAT = {s: 110.0 + 12.0 * HBAR[s] for s in range(32)}
LMEAN_FULL = float(np.mean([LAT[s] for s in range(32)]))
MEMD = {s: float(np.mean([hp(MARTY[s], MEM[m]) for m in range(8)])) for s in range(32)}


def xy_path(a, b):
    """directed links of the X-then-Y route from cell a to cell b"""
    (x, y), (x1, y1) = a, b
    out = []
    while x != x1:
        nx = x + (1 if x1 > x else -1)
        out.append(((x, y), (nx, y)))
        x = nx
    while y != y1:
        ny = y + (1 if y1 > y else -1)
        out.append(((x, y), (x, ny)))
        y = ny
    return out


PATHS = {(h, s): xy_path(MARTY[h], MARTY[s]) for h in range(32) for s in range(32)}


def link_load(act):
    load = collections.Counter()
    for s in act:
        for h in range(32):
            for lk in PATHS[(h, s)]:
                load[lk] += 1.0 / 32
    return max(load.values()) if load else 0.0


LINK_FULL = link_load(list(range(32)))


def mask_feats(m):
    act = [s for s in range(32) if (m >> s) & 1]
    n = len(act)
    rows = collections.Counter(s >> 2 for s in act)
    cols = collections.Counter(s & 3 for s in act)
    R, C = len(rows), len(cols)
    rmax, cmax = max(rows.values()), max(cols.values())
    hb = np.mean([HBAR[s] for s in act])
    L = np.array([LAT[s] for s in act])
    xs = [MARTY[s][0] for s in act]
    ys = [MARTY[s][1] for s in act]
    pairs = [hp(MARTY[a], MARTY[b]) for a, b in itertools.combinations(act, 2)]
    return {'n': n, 'R': R, 'C': C, 'rmax': rmax, 'cmax': cmax, 'rimb': rmax / (n / R), 'cimb': cmax / (n / C),
            'G1': (110 + 12 * hb) / LMEAN_FULL - 1, 'hlag': float((L.max() - L.mean()) / LMEAN_FULL),
            'spread': float(np.mean(pairs)) if pairs else 0.0, 'bbox': (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1) / 36.0,
            'memd': float(np.mean([MEMD[s] for s in act])), 'link': link_load(act) / LINK_FULL, 'dist_rel': (4 * R + 8 * C) / 64.0}


def main():
    t0 = time.time()
    log = []
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    need = sorted({(p['arm'], int(p['mask'], 16)) for p in P
                   if p['kernel'] == 'rgm136' and SHAPE.match(p['arm']) and int(p['mask'], 16) != FULLM})
    seed = json.load(open(os.path.join(POSIMB, 'out/private_shared.json')))
    log.append('subset configurations of rgm136 gemmL: %d; in layout2\'s committed private_shared.json: %d' %
               (len(need), sum(1 for a, m in need if '%s|0x%x' % (a, m) in seed)))
    # check the seed: re-make 5 seeded configurations (the smallest walks) with the committed code, exact equality required
    seeded = sorted([(a, m) for a, m in need if '%s|0x%x' % (a, m) in seed],
                    key=lambda am: np.prod([int(x) for x in SHAPE.match(am[0]).groups()]))[:5]
    for a, m in seeded:
        MB, NB, KB = (int(x) for x in SHAPE.match(a).groups())
        r = F02.private_shared(MB, NB, KB, m)
        s = seed['%s|0x%x' % (a, m)]
        assert r['Fp'] == s['Fp'] and r['Fs'] == s['Fs'], (a, m, r, s)
    log.append('seed check: %d configurations re-made equal (Fp, Fs exactly)' % len(seeded))
    out = {}
    made = 0
    for i, (a, m) in enumerate(need):
        k = '%s|0x%x' % (a, m)
        if k in seed:
            ps = {'Fp': seed[k]['Fp'], 'Fs': seed[k]['Fs'], 'src': 'layout2 private_shared.json (committed)'}
        else:
            MB, NB, KB = (int(x) for x in SHAPE.match(a).groups())
            r = F02.private_shared(MB, NB, KB, m)
            ps = {'Fp': r['Fp'], 'Fs': r['Fs'], 'src': 'made here by f02_private.private_shared'}
            made += 1
        f = mask_feats(m)
        f.update({'Fp': ps['Fp'], 'Fs': ps['Fs']})
        f['LAG'] = f['hlag'] * ps['Fp'] / (ps['Fp'] + ps['Fs']) if (ps['Fp'] + ps['Fs']) > 0 else 0.0
        f['src_Fp_Fs'] = ps['src']
        out[k] = f
        if (i + 1) % 50 == 0:
            print('  %d/%d made %d (%.0f s)' % (i + 1, len(need), made, time.time() - t0), flush=True)
    log.append('made here %d; full-chip link load %.4f (per-shire units), Lmean_full %.6f' % (made, LINK_FULL, LMEAN_FULL))
    # forms only: feature ranges (no residual)
    for c in FEATS_M:
        v = np.array([out[k][c] for k in out], float)
        log.append('  %-8s min %.4g median %.4g max %.4g' % (c, v.min(), np.median(v), v.max()))
    json.dump({'features': out, 'feats_M': FEATS_M, 'MEM': {str(k): v for k, v in MEM.items()}, 'link_full': LINK_FULL,
               'lmean_full': LMEAN_FULL}, open(os.path.join(LANE, 'work/features.json'), 'w'), indent=0, sort_keys=True)
    log.append('done %.0f s' % (time.time() - t0))
    open(os.path.join(LANE, 'logs/f01.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    main()
