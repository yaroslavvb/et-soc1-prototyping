#!/usr/bin/env python3
"""MM1 residuals, step 2: the pooled residuals' systematic misses, with bootstrap intervals, and each model's rms with and without them.
Desk; POST HOC (every group below was named after the data existed; nothing here was registered before any datum).

    /usr/bin/python3 -I -B analyze_residuals.py --rows <dir>/residual-rows.json --out <dir> [--date 2026-11-17]
        writes <dir>/residuals-<date>.csv (one row a (set, point)), <dir>/residuals-<date>.json (every table) and <dir>/residuals-<date>.md.

Own code, the standard library only; reads build_residuals.py's rows (and through them nothing but committed files).
METHOD
  - Pools: e = forecast / measured - 1; J over idle in % only at 3 W over idle and above (the lab scorers' rule); J at rest, every point.
    (a) each set as the lab scored it; (b) each MODEL pooled over its out-of-sample sets (MM1-v0: E206 arm A, arm B, E208; MM1-v1: arm B,
    E207, E208; MM1-v2: E207 and its LOEO folds); (c) THE FRONTIER: each measured experiment once, seen by the newest model that did not fit
    it (E206 arm A: MM1-v2's LOEO fold; arm B: MM1-v1 BLIND; E207: MM1-v2 BLIND; E208: MM1-v2's LOEO fold; the older experiments E105-E190:
    MM1-v2's LOEO folds). LOCO (a card left out) is reported apart: it measures card transfer, not a missing term.
  - Groups: every value of seven dimensions (data kind, shire-mask class, K-block class, format, the lines' place, card, clock class) and
    the NAMED MISSES (NAMED below), each a physical hypothesis: time misses for cycles and seconds, energy misses for joules.
  - A group: n points, n clusters (a cluster = one case (shape, format, mask) on one card: repeats and kinds of one case share it), the
    mean error (size and sign), its rms, a cluster bootstrap of the mean (2,000 resamples of the group's clusters, seed 20261117 + the
    group's index: the 95% percentile interval and the share of resamples with the estimate's sign), and its share of the pool's mean
    square error (n x mean^2 / sum e^2). Under 3 clusters: TOO FEW (no interval).
  - Verdict (on the frontier, by measured experiment): SYSTEMATIC = the interval excludes zero with one sign in two or more experiments and
    the other sign in none; ONE EXPERIMENT; MIXED SIGN; NOT BORNE OUT. FIXED SINCE MM1-v0 = significant for MM1-v0, borne out nowhere on
    the frontier.
  - Joint: least squares of e on an intercept and the named misses holding 2 or more clusters in the pool (time misses for time; energy
    misses for J given t and J at rest given t; both for J with seconds forecast). Reported: the rms; with the named misses' fitted
    offsets removed (the overall bias kept); with the overall bias removed too; both again with each cluster left out of its own fit
    (leave-one-cluster-out: the honest figure); the rms of the points outside every named miss. Share explained = 1 - after^2 / before^2.
  - The floor: E208's session-repeat table (a2c0-S1r against a2c0-S1, 5d99fe17): rms of repeat / first - 1 over the single-run arms;
    J at rest's repeat from the two sessions' runs (S1r's runs matched to S1's by arm).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

TIME_Q = ('cyc_wall', 'cyc_mean', 't')
EN_Q = ('jo_g', 'jo_f', 'jr_g', 'jr_f')
QUANT = TIME_Q + EN_Q
DIMS = ('kind', 'mask_class', 'KB_class', 'fmt', 'place', 'card', 'clock_class')
SEED = 20261117
NBOOT = 2000
MODEL_SETS = {'MM1-v0': ('v0-E206A', 'v0-E206B', 'v0-E208'), 'MM1-v1': ('v1-E206B', 'v1-E207', 'v1-E208'), 'MM1-v2': ('v2-E207', 'v2-LOEO')}
OLDER = 'older (E105-E190)'
FRONTIER_EXPS = ('E206A', 'E206B', 'E207', 'E208', OLDER)


def _knee(r):
    return str(r.get('place', '')).startswith('the knee')


def _inside(r):
    return str(r.get('place', '')).startswith('inside')


def _past(r):
    return str(r.get('place', '')).startswith('past')


def _mn(r):
    return (r['MB'] or 0) * (r['NB'] or 0)


NAMED = [  # (name, kind, predicate, definition); the physical readings and candidate terms are in the README
    ('T1a int8 1x1x1 at about 800 MHz', 'time', lambda r: r['fmt'] == 'int8' and r['arm'] == 'gemmL1x1x1' and r['clock_class'] == 'about 800 MHz',
     'int8 gemmL1x1x1 with a measured kernel clock of 790 MHz or more'),
    ('T1b int8 at one K block, MB x NB >= 2', 'time', lambda r: r['fmt'] == 'int8' and r['KB'] == 1 and _mn(r) >= 2, 'int8, KB = 1, MB x NB >= 2'),
    ('T1c fp32 or fp16 at one K block, MB x NB >= 2', 'time', lambda r: r['fmt'] != 'int8' and r['KB'] == 1 and _mn(r) >= 2,
     'fp32 or fp16, KB = 1, MB x NB >= 2'),
    ('T2 the knee, narrow N (NB 1)', 'time', lambda r: r['NB'] == 1 and _knee(r), 'NB = 1, footprint A+B+C in 33-70 MB'),
    ('T3 the knee, NB >= 2', 'time', lambda r: (r['NB'] or 0) >= 2 and _knee(r), 'NB >= 2, footprint in 33-70 MB'),
    ('T4 int8 inside the L3, KB >= 2', 'time', lambda r: r['fmt'] == 'int8' and _inside(r) and (r['KB'] or 0) >= 2, 'int8, footprint <= 32 MB, KB >= 2'),
    ('T5 subsets inside the L3', 'time', lambda r: (r['shires'] or 32) < 32 and _inside(r), 'under 32 shires, footprint <= 32 MB'),
    ('T6 subsets past the L3 or at the knee', 'time', lambda r: (r['shires'] or 32) < 32 and (_past(r) or _knee(r)), 'under 32 shires, footprint > 32 MB'),
    ('T7a power-of-two NB, MB 1, KB 4-8', 'time', lambda r: r['MB'] == 1 and r['NB'] in (8, 16) and 4 <= (r['KB'] or 0) <= 8, 'MB = 1, NB in {8, 16}, KB 4-8'),
    ('T7b power-of-two NB, MB 1, KB >= 12', 'time', lambda r: r['MB'] == 1 and r['NB'] in (8, 16) and (r['KB'] or 0) >= 12, 'MB = 1, NB in {8, 16}, KB >= 12'),
    ('T8 run_gemm shared arms', 'time', lambda r: r['arm'] in ('gemmc4s', 'gemmc8s', 'gemmc16s'), "run_gemm's gemmc4s, gemmc8s, gemmc16s"),
    ('T9 the governed clock (about 800 MHz), other shapes', 'time',
     lambda r: r['clock_class'] == 'about 800 MHz' and not (r['fmt'] == 'int8' and r['arm'] == 'gemmL1x1x1'),
     'measured kernel clock 790 MHz or more (aifoundry2 card 0, aifoundry1 card 0), int8 1x1x1 apart'),
    ('E1 zero data on aifoundry1 card 1', 'energy', lambda r: r['kind'] == 'zeros' and r['card'] == 'aifoundry1 card 1', 'all-zero operands, aifoundry1 card 1'),
    ('E2 zero data on aifoundry3 card 0', 'energy', lambda r: r['kind'] == 'zeros' and r['card'] == 'aifoundry3 card 0', 'all-zero operands, aifoundry3 card 0'),
    ('E3 zero data on the governed cards', 'energy', lambda r: r['kind'] == 'zeros' and r['card'] in ('aifoundry2 card 0', 'aifoundry1 card 0'),
     'all-zero operands, aifoundry2 card 0 or aifoundry1 card 0'),
    ('E4 deep K (KB >= 16), data not zero', 'energy', lambda r: (r['KB'] or 0) >= 16 and r['kind'] != 'zeros', 'KB >= 16, any kind but zeros'),
    ('E5 inside the L3, full chip, KB >= 2', 'energy', lambda r: _inside(r) and r['shires'] == 32 and (r['KB'] or 0) >= 2, 'footprint <= 32 MB, 32 shires, KB >= 2'),
    ('E6 one K block, MB x NB >= 2', 'energy', lambda r: r['KB'] == 1 and _mn(r) >= 2, 'KB = 1, MB x NB >= 2'),
    ('E7 narrow masks (8 shires or fewer)', 'energy', lambda r: (r['shires'] or 32) <= 8, 'mask of 8 shires or fewer'),
    ('E8 the knee', 'energy', _knee, 'footprint in 33-70 MB'),
    ('E9 ones data', 'energy', lambda r: r['kind'] == 'ones', 'a repeated tile of 1.0 (MM1-v0 and MM1-v1 forecast no energy for it)'),
]


def exp_point(r):
    e = r.get('exp_point')
    if e:
        return {'E206': 'E206A', 'E208': 'E208'}.get(e, OLDER)
    return {'E206 arm A': 'E206A', 'E206 arm B': 'E206B', 'E207': 'E207', 'E208': 'E208'}[r['exp']]


def pool(rows, q):
    out = []
    for r in rows:
        e = r['e'].get(q)
        if e is None:
            continue
        if q in ('jo_g', 'jo_f') and r['low_w']:
            continue
        out.append(r)
    return out


def stats(es):
    n = len(es)
    if n == 0:
        return None
    return {'n': n, 'rms_pct': 100 * math.sqrt(sum(e * e for e in es) / n), 'bias_pct': 100 * sum(es) / n}


def boot_mean(clusters, seed):
    rng = random.Random(seed)
    k = len(clusters)
    sums = [sum(c) for c in clusters]
    cnts = [len(c) for c in clusters]
    ms = []
    for _ in range(NBOOT):
        s = n = 0
        for _ in range(k):
            j = rng.randrange(k)
            s += sums[j]
            n += cnts[j]
        ms.append(s / n)
    ms.sort()
    return ms[int(0.025 * NBOOT)], ms[int(0.975 * NBOOT) - 1], ms


def group_stats(prow, q, pred, total_sq, seed):
    g = [r for r in prow if pred(r)]
    if not g:
        return None
    es = [r['e'][q] for r in g]
    cl = defaultdict(list)
    for r in g:
        cl[r['cluster']].append(r['e'][q])
    mean = sum(es) / len(es)
    rec = {'n': len(es), 'n_clusters': len(cl), 'bias_pct': 100 * mean, 'rms_pct': 100 * math.sqrt(sum(e * e for e in es) / len(es)),
           'share_of_mse': (len(es) * mean * mean / total_sq) if total_sq > 0 else None}
    if len(cl) >= 3:
        lo, hi, ms = boot_mean(list(cl.values()), seed)
        same = sum(1 for m in ms if (m > 0) == (mean > 0)) / len(ms)
        rec.update({'ci95_pct': [100 * lo, 100 * hi], 'p_same_sign': same, 'excludes_zero': (lo > 0) or (hi < 0)})
    else:
        rec.update({'ci95_pct': None, 'p_same_sign': None, 'excludes_zero': None, 'note': 'TOO FEW clusters'})
    return rec


def solve(A, b):
    k = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(k):
        p = max(range(c, k), key=lambda i: abs(M[i][c]))
        if abs(M[p][c]) < 1e-15:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [x / piv for x in M[c]]
        for i in range(k):
            if i != c and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return [M[i][k] for i in range(k)]


def joint(prow, q, terms, ridge=1e-6):
    names = [t[0] for t in terms]
    X = [[1.0] + [1.0 if t[1](r) else 0.0 for t in terms] for r in prow]
    y = [r['e'][q] for r in prow]
    k = len(names) + 1
    XtX = [[0.0] * k for _ in range(k)]
    Xty = [0.0] * k
    for xi, yi in zip(X, y):
        for a_ in range(k):
            if xi[a_]:
                Xty[a_] += yi
                for b_ in range(k):
                    if xi[b_]:
                        XtX[a_][b_] += 1.0

    def fit(A, b):
        A2 = [row[:] for row in A]
        for j in range(1, k):
            A2[j][j] += ridge
        return solve(A2, b)
    beta = fit(XtX, Xty)
    if beta is None:
        return None
    n = len(y)
    res_all = [yi - sum(bj * xj for bj, xj in zip(beta, xi)) for xi, yi in zip(X, y)]
    res_named = [yi - sum(bj * xj for bj, xj in zip(beta[1:], xi[1:])) for xi, yi in zip(X, y)]
    cl = defaultdict(list)
    for i, r in enumerate(prow):
        cl[r['cluster']].append(i)
    res_cv_named = [0.0] * n
    res_cv_all = [0.0] * n
    for c, idx in cl.items():
        A = [row[:] for row in XtX]
        b = Xty[:]
        for i in idx:
            xi = X[i]
            for a_ in range(k):
                if xi[a_]:
                    b[a_] -= y[i]
                    for b_ in range(k):
                        if xi[b_]:
                            A[a_][b_] -= 1.0
        bc = fit(A, b) or [0.0] * k
        for i in idx:
            xi = X[i]
            res_cv_all[i] = y[i] - sum(bj * xj for bj, xj in zip(bc, xi))
            res_cv_named[i] = y[i] - sum(bj * xj for bj, xj in zip(bc[1:], xi[1:]))

    def rms(v):
        return 100 * math.sqrt(sum(x * x for x in v) / len(v))
    outside = [yi for xi, yi in zip(X, y) if not any(xi[1:])]
    r0 = rms(y)
    rec = {'terms': names, 'coef_pct': {'intercept (overall bias)': 100 * beta[0], **{nm: 100 * bj for nm, bj in zip(names, beta[1:])}},
           'n': n, 'n_clusters': len(cl), 'rms_pct': r0, 'bias_pct': 100 * sum(y) / n,
           'rms_named_removed_pct': rms(res_named), 'rms_named_and_bias_removed_pct': rms(res_all),
           'rms_named_removed_cv_pct': rms(res_cv_named), 'rms_named_and_bias_removed_cv_pct': rms(res_cv_all),
           'n_outside_named': len(outside), 'rms_outside_named_pct': rms(outside) if outside else None}
    for k2 in ('rms_named_removed_pct', 'rms_named_and_bias_removed_pct', 'rms_named_removed_cv_pct', 'rms_named_and_bias_removed_cv_pct'):
        rec['share_explained_' + k2[4:-4]] = 1 - (rec[k2] / r0) ** 2 if r0 > 0 else None
    return rec


def terms_for(p, q):
    want = ('time',) if q in TIME_Q else (('energy', 'time') if q in ('jo_f', 'jr_f') else ('energy',))
    out = []
    for nm, kind, pred, _ in NAMED:
        if kind not in want:
            continue
        cl = {r['cluster'] for r in p if pred(r)}
        if len(cl) >= 2 and sum(1 for r in p if not pred(r)) >= 3:
            out.append((nm, pred))
    return out


def fmt_num(x, p=6):
    if x is None:
        return ''
    if isinstance(x, bool):
        return 'True' if x else 'False'
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        return '' if x != x else f'{x:.{p}g}'
    return str(x)


def rnd(o):
    if isinstance(o, float):
        return float(f'{o:.6g}')
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rnd(v) for v in o]
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--date', default='2026-11-17')
    a = ap.parse_args()
    R = json.load(open(a.rows))
    rows = R['rows']
    sets = list(R['sets'])
    print(f'analyze_residuals: interpreter {sys.executable} {sys.version.split()[0]}; {len(rows)} rows, {len(sets)} sets')
    for r in rows:
        r['misses'] = [nm for nm, kind, pred, _ in NAMED if pred(r)]
        r['exp_measured'] = exp_point(r)
    out = {'what': 'MM1 residuals: every residual of the lab matmul models on data they did not fit, their systematic misses and the floor',
           'label': 'POST HOC (desk arithmetic of committed forecasts and measured records; no group here was registered before any datum)',
           'date': a.date, 'python': sys.version.split()[0], 'interpreter': sys.executable, 'sets': R['sets'], 'pins': R['pins'],
           'conventions': {'error': 'forecast / measured - 1', 'J over idle pools': 'points at 3 W over idle and above (the lab scorers\' rule)',
                           'given seconds': 'W_g = A + (W_f - A) t_f / t_meas (the model\'s own affine form); E208 UNREAD rows: the scorer\'s given-t column',
                           'cluster': 'one case (shape, format, mask) on one card', 'bootstrap': f'{NBOOT} cluster resamples, seed {SEED} + group index',
                           'held out sets': 'MM1-v2 refitted without the point\'s experiment (LOEO) or card (LOCO); J in units of the measured seconds',
                           'model pools': MODEL_SETS, 'frontier': 'E206A: v2-LOEO; E206B: v1-E206B; E207: v2-E207; E208: v2-LOEO; ' + OLDER + ': v2-LOEO'},
           'named_misses_definitions': {nm: d for nm, _, _, d in NAMED}}
    gi = [0]

    def nextseed():
        gi[0] += 1
        return SEED + gi[0]
    # (a) each set
    summ = {}
    for s in sets:
        rs = [r for r in rows if r['set'] == s]
        summ[s] = {}
        for q in QUANT:
            p = pool(rs, q)
            st = stats([r['e'][q] for r in p])
            if st is None:
                continue
            allp = [r['e'][q] for r in rs if r['e'].get(q) is not None]
            st.update({'n_all_points': len(allp), 'rms_all_points_pct': 100 * math.sqrt(sum(e * e for e in allp) / len(allp)),
                       'bias_all_points_pct': 100 * sum(allp) / len(allp), 'n_clusters': len({r['cluster'] for r in p})})
            summ[s][q] = st
    out['summary'] = summ
    pc = {}
    for s in ('v1-E207', 'v2-E207'):
        by = defaultdict(list)
        for r in rows:
            if r['set'] == s:
                by[r['case']].append(r)
        pc[s] = {}
        for q in TIME_Q:
            es = []
            for c, g in by.items():
                ms = [r['meas'][q] for r in g if r['meas'].get(q) is not None]
                fs = [r['fc'][q] for r in g if r['fc'].get(q) is not None]
                if ms and fs:
                    es.append((sum(fs) / len(fs)) / (sum(ms) / len(ms)) - 1)
            pc[s][q] = stats(es)
    out['e207_per_case'] = pc
    PUB = [('v0-E206A', 'cyc_wall', 9.0, -2.5, 'mm1v0-e206'), ('v0-E206A', 'cyc_mean', 9.5, None, 'mm1v0-e206'),
           ('v0-E206A', 't', 9.0, None, 'mm1v0-e206'), ('v0-E206A', 'jr_g', 2.6, None, 'mm1v0-e206'), ('v0-E206A', 'jr_f', 7.6, None, 'mm1v0-e206'),
           ('v0-E206A', 'jo_g', 9.8, -6.1, 'mm1v0-e206, all 109 points (W under 3 W included)'), ('v0-E206A', 'jo_f', 10.4, None, 'mm1v0-e206, all 109 points'),
           ('v1-E206B', 'cyc_mean', 4.7, -1.6, 'verify-e206bd'), ('v1-E206B', 't', 4.6, None, 'verify-e206bd'),
           ('v1-E206B', 'jo_g', 14.3, 6.8, 'verify-e206bd, n 105 (W under 3 W included)'), ('v1-E206B', 'jr_g', 2.1, None, 'verify-e206bd'),
           ('v0-E206B', 'cyc_mean', 9.8, None, 'verify-e206bd'), ('v0-E206B', 't', 9.2, None, 'verify-e206bd'),
           ('v0-E206B', 'jo_g', 15.5, None, 'verify-e206bd, n 105'), ('v0-E206B', 'jr_g', 2.4, None, 'verify-e206bd'),
           ('v1-E207', 'jo_g', 5.42, -2.11, 'score-v2-e207 (030ffa42), n 50'), ('v1-E207', 'jo_f', 5.80, -2.43, '030ffa42'),
           ('v1-E207', 'jr_g', 2.13, -0.73, '030ffa42'), ('v1-E207', 'jr_f', 5.34, -2.79, '030ffa42'),
           ('v2-E207', 'jo_g', 4.82, -0.71, '030ffa42, n 46'), ('v2-E207', 'jo_f', 5.15, -0.87, '030ffa42'), ('v2-E207', 'jr_g', 1.92, -0.25, '030ffa42'),
           ('v2-E207', 'jr_f', 4.60, -1.13, '030ffa42'), ('v1-E208', 'cyc_wall', 7.59, None, 'unread_e208 (3ca4b717)'),
           ('v1-E208', 'jo_g', 9.57, None, 'unread_e208 (W over idle given t)'), ('v0-E208', 'cyc_wall', 9.39, None, 'unread_e208'),
           ('v0-E208', 'jo_g', 11.39, None, 'unread_e208'), ('v2-LOEO', 'cyc_wall', 5.41, None, 'fix-mm1v2 pin rule (3ca4b717)')]
    PUBCASE = [('v1-E207', 'cyc_wall', 5.62, -2.52), ('v1-E207', 'cyc_mean', 5.93, -2.37), ('v1-E207', 't', 5.66, -2.62),
               ('v2-E207', 'cyc_wall', 4.80, -1.02), ('v2-E207', 'cyc_mean', 5.01, -0.86), ('v2-E207', 't', 4.81, -1.12)]
    xc = []
    for s, q, rms_p, bias_p, src in PUB:
        st = summ.get(s, {}).get(q)
        if st is None:
            continue
        use_all = 'all 109' in src or 'n 105' in src
        mr = st['rms_all_points_pct'] if use_all else st['rms_pct']
        mb = st['bias_all_points_pct'] if use_all else st['bias_pct']
        xc.append({'set': s, 'q': q, 'published_rms_pct': rms_p, 'published_bias_pct': bias_p, 'mine_rms_pct': round(mr, 3), 'mine_bias_pct': round(mb, 3),
                   'n_mine': st['n_all_points'] if use_all else st['n'], 'source': src,
                   'agrees_to_rounding': abs(mr - rms_p) <= 0.051 + 0.005 * rms_p and (bias_p is None or abs(mb - bias_p) <= 0.06)})
    for s, q, rms_p, bias_p in PUBCASE:
        st = pc[s][q]
        xc.append({'set': s, 'q': q + ' (per case)', 'published_rms_pct': rms_p, 'published_bias_pct': bias_p, 'mine_rms_pct': round(st['rms_pct'], 3),
                   'mine_bias_pct': round(st['bias_pct'], 3), 'n_mine': st['n'], 'source': 'score-v2-e207 (030ffa42), 47 cases',
                   'agrees_to_rounding': abs(st['rms_pct'] - rms_p) <= 0.006 and abs(st['bias_pct'] - bias_p) <= 0.006})
    out['crosscheck_published'] = xc
    nag = sum(1 for x in xc if x['agrees_to_rounding'])
    print(f'cross-check against published figures: {nag} of {len(xc)} agree to rounding')
    # pools: per set, per model, frontier (and frontier by experiment)
    POOLS = {}
    for s in sets:
        POOLS['set ' + s] = [r for r in rows if r['set'] == s]
    for m, ss in MODEL_SETS.items():
        POOLS['model ' + m] = [r for r in rows if r['set'] in ss]
    fr = [r for r in rows if r['set'] == 'v1-E206B' or r['set'] == 'v2-E207' or r['set'] == 'v2-LOEO']
    POOLS['frontier'] = fr
    for ex in FRONTIER_EXPS:
        POOLS['frontier ' + ex] = [r for r in fr if r['exp_measured'] == ex]
    out['pool_sizes'] = {k: len(v) for k, v in POOLS.items()}
    named = {nm: {'kind': kind, 'definition': d, 'pools': {}} for nm, kind, _, d in NAMED}
    marg = {}
    jt = {}
    for pk, prs in POOLS.items():
        for q in QUANT:
            p = pool(prs, q)
            if len(p) < 3:
                continue
            tot = sum(r['e'][q] ** 2 for r in p)
            for nm, kind, pred, _ in NAMED:
                if (kind == 'time') != (q in TIME_Q):
                    continue
                g = group_stats(p, q, pred, tot, nextseed())
                if g:
                    named[nm]['pools'].setdefault(pk, {})[q] = g
            if (pk.startswith('set ') or pk == 'frontier') and q in ('cyc_wall', 'jo_g', 'jr_g'):
                mg = marg.setdefault(pk, {}).setdefault(q, {})
                for d in DIMS:
                    vals = sorted({str(r.get(d)) for r in p})
                    if len(vals) < 2:
                        continue
                    for v in vals:
                        g = group_stats(p, q, lambda r, d=d, v=v: str(r.get(d)) == v, tot, nextseed())
                        if g:
                            mg[f'{d} = {v}'] = g
            if not pk.startswith('frontier ') and len(p) >= 5:
                j = joint(p, q, terms_for(p, q))
                if j:
                    jt.setdefault(pk, {})[q] = j
    # verdicts on the frontier, per measured experiment, on each miss's primary quantity
    MATERIAL = {'time': 2.0, 'energy': 3.0}  # % : about 5x the cycles floor (0.38%) and 2.5x the joules floor (1.2%)
    for nm, kind, _, _ in NAMED:
        q0 = 'cyc_wall' if kind == 'time' else 'jo_g'
        pos, neg, cells = [], [], {}
        for ex in FRONTIER_EXPS:
            c = named[nm]['pools'].get('frontier ' + ex, {}).get(q0)
            cells[ex] = c
            if c and c.get('excludes_zero'):
                (pos if c['bias_pct'] > 0 else neg).append(ex)
        v0sig = []
        for s in MODEL_SETS['MM1-v0']:
            c = named[nm]['pools'].get('set ' + s, {}).get(q0)
            if c and c.get('excludes_zero'):
                v0sig.append(s)
        pooled = named[nm]['pools'].get('frontier', {}).get(q0)
        signs = [c['bias_pct'] > 0 for c in cells.values() if c]
        material = bool(pooled) and abs(pooled['bias_pct']) >= MATERIAL[kind]
        spread = math.sqrt(max(0.0, pooled['rms_pct'] ** 2 - pooled['bias_pct'] ** 2)) if pooled else None
        if pos and neg:
            v = 'MIXED SIGN'
        elif material and ((len(pos) >= 2 and not neg) or (len(neg) >= 2 and not pos)
                           or (pooled.get('excludes_zero') and len(signs) >= 3 and (all(signs) or not any(signs)))):
            v = 'SYSTEMATIC'
        elif material and (pos or neg):
            v = 'ONE EXPERIMENT'
        elif material and pooled['n'] >= 3 and spread is not None and spread <= 1.0 and pooled.get('ci95_pct') is None:
            v = 'CONSISTENT, TOO FEW CLUSTERS'
        elif pos or neg or (pooled and pooled.get('excludes_zero')):
            v = 'SMALL'
        elif v0sig:
            v = 'FIXED SINCE MM1-v0'
        else:
            v = 'NOT BORNE OUT'
        named[nm].update({'primary_quantity': q0, 'frontier_significant': {'positive': pos, 'negative': neg}, 'mm1_v0_significant_in': v0sig,
                          'material_threshold_pct': MATERIAL[kind], 'frontier_spread_pct': spread, 'verdict': v})
    # two continuous checks: the die at the run's start (J over idle given t, data not zero), and per-experiment offsets
    die = {}
    for s in sets:
        p = [r for r in pool([r for r in rows if r['set'] == s], 'jo_g') if r['kind'] != 'zeros' and r['meas'].get('die_start') is not None]
        if len(p) < 10:
            continue
        cl = defaultdict(list)
        for r in p:
            cl[r['cluster']].append((r['meas']['die_start'], r['e']['jo_g']))

        def slope(pts):
            n = len(pts)
            mx = sum(x for x, _ in pts) / n
            my = sum(y for _, y in pts) / n
            sxx = sum((x - mx) ** 2 for x, _ in pts)
            sxy = sum((x - mx) * (y - my) for x, y in pts)
            syy = sum((y - my) ** 2 for _, y in pts)
            return (sxy / sxx if sxx > 0 else None), (sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None), sxx
        allp = [xy for v in cl.values() for xy in v]
        b, rr, sxx = slope(allp)
        rec = {'n': len(allp), 'n_clusters': len(cl), 'die_range_c': [min(x for x, _ in allp), max(x for x, _ in allp)],
               'slope_pct_per_c': 100 * b if b is not None else None, 'r': rr, 'share_of_variance': rr * rr if rr is not None else None}
        if b is not None and len(cl) >= 3:
            rng = random.Random(nextseed())
            ks = list(cl.values())
            bs = []
            for _ in range(NBOOT):
                pts = [xy for _ in range(len(ks)) for xy in ks[rng.randrange(len(ks))]]
                bb, _, s2 = slope(pts)
                if bb is not None:
                    bs.append(bb)
            bs.sort()
            rec['ci95_pct_per_c'] = [100 * bs[int(0.025 * len(bs))], 100 * bs[int(0.975 * len(bs)) - 1]]
        die[s] = rec
    out['die_check'] = {'what': "J over idle given t (data not zero) against the die at the run's start: slope of e in % per C; the lab's die "
                                "correction is +0.48% of power per C (E208's reduction), so a model without a die term reads about -0.5% per C",
                        'sets': die}
    offs = {}
    for pk in ('set v2-LOEO', 'frontier'):
        offs[pk] = {}
        for q in ('cyc_wall', 'jo_g'):
            p = pool(POOLS[pk], q)
            by = defaultdict(list)
            for r in p:
                by[r.get('exp_point') or r['exp']].append(r['e'][q])
            tot = sum(e * e for v in by.values() for e in v)
            means = [sum(v) / len(v) for v in by.values()]
            offs[pk][q] = {'per_experiment_bias_pct': {k: [100 * sum(v) / len(v), len(v)] for k, v in sorted(by.items())},
                           'share_of_mse_in_experiment_means': sum(len(v) * (sum(v) / len(v)) ** 2 for v in by.values()) / tot if tot else None,
                           'rms_of_experiment_means_unweighted_pct': 100 * math.sqrt(sum(m * m for m in means) / len(means)) if means else None,
                           'n_experiments': len(means)}
    out['experiment_offsets'] = {'what': 'the share of the pool\'s mean square error held by each measured experiment\'s mean error (in sample; '
                                         'a session or campaign term no size or operation can forecast)', 'pools': offs}
    out['named_misses'] = named
    out['marginal_groups'] = marg
    out['joint'] = jt
    # the floor and each set's error against it
    fl = R.get('floor') or {}
    FQ = {'cyc_wall': 'cyc_op_max', 'cyc_mean': 'cyc_op_mean', 't': 'T_op_us', 'jo_g': 'J_op', 'jo_f': 'J_op'}
    vs = {}
    for pk in [k for k in POOLS if k.startswith('set ') or k.startswith('model ') or k == 'frontier']:
        vs[pk] = {}
        for q, fk in FQ.items():
            p = pool(POOLS[pk], q)
            st = stats([r['e'][q] for r in p])
            if st and fk in fl:
                f = 100 * fl[fk]['rms']
                vs[pk][q] = {'rms_pct': st['rms_pct'], 'floor_pct': f, 'ratio': st['rms_pct'] / f,
                             'beyond_floor_pct': math.sqrt(max(0.0, st['rms_pct'] ** 2 - f ** 2)), 'floor_share_of_mse': (f / st['rms_pct']) ** 2}
    side = R.get('s1r_side_check', [])
    jr_rep, cw_rep, w_rep = [], [], []
    for x in side:
        m, m1 = x['meas'], x.get('meas_S1') or {}
        if m.get('jr') and m1.get('jr'):
            jr_rep.append(m['jr'] / m1['jr'] - 1)
        if m.get('cyc_wall') and m1.get('cyc_wall'):
            cw_rep.append(m['cyc_wall'] / m1['cyc_wall'] - 1)
        if m.get('w') and m1.get('w'):
            w_rep.append(m['w'] / m1['w'] - 1)

    def rmsf(v):
        return (100 * math.sqrt(sum(e * e for e in v) / len(v))) if v else None
    out['floor'] = fl
    out['floor_j_at_rest'] = {'label': 'post hoc desk arithmetic: S1r run / S1 run of the same arm and role - 1, every matched run with energy',
                              'rms_pct': rmsf(jr_rep), 'n': len(jr_rep), 'cyc_wall_rms_pct_same_runs': rmsf(cw_rep), 'n_cyc': len(cw_rep),
                              'w_over_idle_rms_pct_same_runs': rmsf(w_rep), 'n_w': len(w_rep)}
    out['model_error_vs_floor'] = vs
    s1r = {'label': "post hoc; S1r has no forecast of its own: its runs against S1's UNREAD forecast of the same arm ('matched'), never pooled",
           'n_runs_matched': len(side)}
    for pre in ('v1_', 'v0_'):
        a1 = [x[pre + 'e_cyc_wall'] for x in side if x.get(pre + 'e_cyc_wall') is not None]
        b1 = [x[pre + 'e_cyc_wall_S1'] for x in side if x.get(pre + 'e_cyc_wall_S1') is not None]
        a2 = [x[pre + 'e_w_given_S1r'] for x in side if x.get(pre + 'e_w_given_S1r') is not None]
        b2 = [x[pre + 'e_w_given_S1'] for x in side if x.get(pre + 'e_w_given_S1') is not None]
        s1r[pre + 'matched'] = {'cyc_wall_rms_pct_S1r': rmsf(a1), 'cyc_wall_rms_pct_S1': rmsf(b1), 'n_cyc': len(a1),
                                'w_given_rms_pct_S1r': rmsf(a2), 'w_given_rms_pct_S1': rmsf(b2), 'n_w': len(a2)}
    out['s1r_side_check'] = s1r
    # outputs
    os.makedirs(a.out, exist_ok=True)
    cols = ['set', 'model', 'label', 'exp', 'exp_measured', 'card', 'f_mhz', 'clock_class', 'pid', 'arm', 'MB', 'NB', 'KB', 'fmt', 'kind', 'kind_raw', 'mask',
            'shires', 'mask_class', 'footprint_MB', 'place', 'KB_class', 'NB_pow2', 'law_arm', 'case', 'cluster', 'low_w']
    mcols = ['cyc_wall', 'cyc_mean', 't', 'w', 'p_rest', 'jo', 'jr']
    fcols = ['cyc_wall', 'cyc_mean', 't', 'w_f', 'w_g', 'jo_g', 'jo_f', 'jr_g', 'jr_f']
    fn_csv = os.path.join(a.out, f'residuals-{a.date}.csv')
    with open(fn_csv, 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(cols + ['meas_' + c for c in mcols] + ['fc_' + c for c in fcols] + ['e_' + q for q in QUANT] + ['named_misses'])
        for r in rows:
            w.writerow([fmt_num(r.get(c)) for c in cols] + [fmt_num(r['meas'].get(c), 8) for c in mcols] + [fmt_num(r['fc'].get(c), 8) for c in fcols]
                       + [fmt_num(r['e'].get(q), 6) for q in QUANT] + [';'.join(m.split(' ')[0] for m in r['misses'])])
    fn_js = os.path.join(a.out, f'residuals-{a.date}.json')
    with open(fn_js, 'w') as fh:
        json.dump(rnd(out), fh, indent=1)
        fh.write('\n')
    print(f'wrote {os.path.basename(fn_csv)} ({len(rows)} rows) and {os.path.basename(fn_js)}')
    # md tables
    L = [f'# MM1 residuals {a.date}: tables (POST HOC)', '',
         "Made by `analyze_residuals.py` from `build_residuals.py`'s rows. e = forecast / measured - 1, in %. J over idle: points at 3 W over idle "
         'and above. Cells: rms (bias) and n, or bias (n points / n clusters) with * when the 95% cluster-bootstrap interval excludes zero.', '']
    L += ['## 1. Each set as forecast', '', '| set | model | label | ' + ' | '.join(QUANT) + ' |', '|---|---|---|' + '---|' * len(QUANT)]
    for s in sets:
        m, lab, ex = R['sets'][s]
        cells = [(f"{summ[s][q]['rms_pct']:.2f} ({summ[s][q]['bias_pct']:+.2f}) n{summ[s][q]['n']}" if q in summ[s] else '-') for q in QUANT]
        L.append(f'| {s} | {m} | {lab} on {ex} | ' + ' | '.join(cells) + ' |')
    L += ['', '## 2. The named misses on the frontier (each measured experiment once, newest model that did not fit it)', '',
          '| miss | primary | ' + ' | '.join(FRONTIER_EXPS) + ' | frontier pooled | MM1-v0 sets | verdict |', '|---|---|' + '---|' * len(FRONTIER_EXPS) + '---|---|---|']

    def cell(c):
        if not c:
            return '-'
        return f"{c['bias_pct']:+.1f}{'*' if c.get('excludes_zero') else ''} ({c['n']}/{c['n_clusters']})"
    for nm, kind, _, _ in NAMED:
        q0 = named[nm]['primary_quantity']
        cs = [cell(named[nm]['pools'].get('frontier ' + ex, {}).get(q0)) for ex in FRONTIER_EXPS]
        v0c = '; '.join(f"{s[3:]} {cell(named[nm]['pools'].get('set ' + s, {}).get(q0))}" for s in MODEL_SETS['MM1-v0'])
        L.append(f"| {nm} | {q0} | " + ' | '.join(cs) + f" | {cell(named[nm]['pools'].get('frontier', {}).get(q0))} | {v0c} | {named[nm]['verdict']} |")
    L += ['', '## 3. With and without the named misses (joint least squares; cv = each cluster left out of its own fit)', '',
          '| pool | quantity | rms (bias) | named removed | cv | named and bias removed | cv | share explained, named, cv | outside every miss: rms (n) |',
          '|---|---|---|---|---|---|---|---|---|']
    for pk in [k for k in jt]:
        for q in QUANT:
            j = jt[pk].get(q)
            if not j:
                continue
            L.append(f"| {pk} | {q} | {j['rms_pct']:.2f} ({j['bias_pct']:+.2f}) | {j['rms_named_removed_pct']:.2f} | {j['rms_named_removed_cv_pct']:.2f} | "
                     f"{j['rms_named_and_bias_removed_pct']:.2f} | {j['rms_named_and_bias_removed_cv_pct']:.2f} | "
                     f"{100 * j['share_explained_named_removed_cv']:.0f}% | "
                     f"{(format(j['rms_outside_named_pct'], '.2f') if j['rms_outside_named_pct'] is not None else '-')} ({j['n_outside_named']}) |")
    L += ['', '## 4. The floor (E208 session repeat, a2c0-S1r against a2c0-S1)', '']
    for k, v in fl.items():
        if isinstance(v, dict):
            L.append(f"- {k}: repeat rms {100 * v['rms']:.3f}% over {v['n']} single-run arms (median {100 * v['median']:+.3f}%)")
    fj = out['floor_j_at_rest']
    if fj['rms_pct'] is not None:
        L.append(f"- J with the card at rest (desk, matched runs): repeat rms {fj['rms_pct']:.3f}% over {fj['n']} runs")
    L += ['', '| pool | cycles wall: rms / floor | J over idle given t: rms / floor | J over idle: beyond the floor |', '|---|---|---|---|']
    for pk, d in vs.items():
        c1 = d.get('cyc_wall')
        c2 = d.get('jo_g')
        L.append(f"| {pk} | {(format(c1['rms_pct'], '.2f') + ' / ' + format(c1['floor_pct'], '.2f') + ' (' + format(c1['ratio'], '.0f') + 'x)') if c1 else '-'} | "
                 f"{(format(c2['rms_pct'], '.2f') + ' / ' + format(c2['floor_pct'], '.2f') + ' (' + format(c2['ratio'], '.1f') + 'x)') if c2 else '-'} | "
                 f"{format(c2['beyond_floor_pct'], '.2f') if c2 else '-'} |")
    L += ['', '## 5. Two continuous checks', '', "The die at the run's start against J over idle given t (data not zero):", '',
          '| set | n (clusters) | die range C | slope % per C [95%] | share of variance |', '|---|---|---|---|---|']
    for s, d in die.items():
        ci = d.get('ci95_pct_per_c')
        L.append(f"| {s} | {d['n']} ({d['n_clusters']}) | {d['die_range_c'][0]:.0f}-{d['die_range_c'][1]:.0f} | {d['slope_pct_per_c']:+.2f} "
                 f"[{(format(ci[0], '+.2f') + ', ' + format(ci[1], '+.2f')) if ci else '-'}] | {100 * (d['share_of_variance'] or 0):.0f}% |")
    L += ['', "Each measured experiment's mean error (in sample):", '']
    for pk, d in offs.items():
        for q, x in d.items():
            L.append(f"- {pk}, {q}: share of the mean square error in the experiments' means {100 * x['share_of_mse_in_experiment_means']:.0f}%; "
                     f"rms of the {x['n_experiments']} means (unweighted) {x['rms_of_experiment_means_unweighted_pct']:.1f}%; "
                     + ', '.join(f"{k} {v[0]:+.1f} (n {v[1]})" for k, v in x['per_experiment_bias_pct'].items()))
    with open(os.path.join(a.out, f'residuals-{a.date}.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    return 0 if nag == len(xc) else 3


if __name__ == '__main__':
    sys.exit(main())
