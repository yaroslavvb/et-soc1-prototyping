#!/usr/bin/env python3
"""mask-posimb (Q238) x05: a second look BEFORE the declaration (post hoc, in sample; disclosed): at the subset MASK points, MM1-v3.2's
held-out-base residual against (a) two readings of 'alignment' of the kernel's row group (s>>2) and column group (s&3): A1 = no active shire
with (s>>2)&3 == s&3; A2 = no pair (R, C) of an active row group and an active column group with R&3 == C; and (b) the balance of the walk's
DRAM-served A and B tile requests (verify-lay's committed v01_map.my_steps and lru_fresh, strict LRU at 32 MB, pass 2): Bal = 2 min(FA, FB) /
(FA + FB). NO constant of any candidate form is fitted. Desk; numpy; single-threaded. Output: work/x05_feat.json (per configuration) + tables."""
import collections
import importlib.util
import json
import os
import re
import time

import numpy as np

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
C215 = os.path.join(LAB, 'tools/matmul/mm1/v3.2-terms/layout/controls-e215')
os.environ.setdefault('ET_LAB', LAB)
spec = importlib.util.spec_from_file_location('v01_map_committed', os.path.join(C215, 'v01_map.py'))
V01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V01)
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
D = json.load(open(os.path.join(LANE, 'work/points_all.json')))
P = D['points']
N = len(P)
Z = np.load(os.path.join(LANE, 'work/base.npz'))
Tm = Z['T_meas']
V32_EXPS = sorted({p['exp'] for p in P[:D['counts']['v32_fit']]})
expa = np.array([p['exp'] for p in P])
base = Z['base_all'].copy()
for x in V32_EXPS:
    nm = 'base|LOEO ' + x
    if nm in Z.files:
        s = expa == x
        base[s] = Z[nm][s]
res = np.log(Tm / base)


def mint(m):
    return int(m, 16)


def A1(m):
    act = [s for s in range(32) if (m >> s) & 1]
    return int(not any(((s >> 2) & 3) == (s & 3) for s in act))


def A2(m):
    act = [s for s in range(32) if (m >> s) & 1]
    Rs = {s >> 2 for s in act}
    Cs = {s & 3 for s in act}
    return int(not any((R & 3) == C for R in Rs for C in Cs))


cache_fn = os.path.join(LANE, 'work/x05_feat.json')
cache = json.load(open(cache_fn)) if os.path.exists(cache_fn) else {}
sub = []
for j, p in enumerate(P):
    m = SH.match(p['arm'])
    if p['kernel'] == 'rgm136' and m and mint(p['mask']) != 0xFFFFFFFF and tuple(int(x) for x in m.groups()) != (1, 1, 1):
        sub.append(j)
t0 = time.time()
for j in sub:
    p = P[j]
    k = '%s|%s' % (p['arm'], p['mask'])
    if k in cache:
        continue
    MB, NB, KB = (int(x) for x in SH.match(p['arm']).groups())
    mm = mint(p['mask'])
    seq = list(V01.my_steps(MB, NB, KB, mm))
    nsteps = MB * NB * 2 * KB * V01.KT
    fr = V01.lru_fresh(seq, 32 * 1024, nsteps)
    FA = sum(len(a) for a, b in fr)
    FB = sum(len(b) for a, b in fr)
    cache[k] = {'A1': A1(mm), 'A2': A2(mm), 'FA': FA, 'FB': FB, 'n': bin(mm).count('1')}
json.dump(cache, open(cache_fn, 'w'), indent=0, sort_keys=True)
print('configurations', len({('%s|%s' % (P[j]['arm'], P[j]['mask'])) for j in sub}), 'made in %.0f s' % (time.time() - t0))


def rb(v):
    v = np.asarray(v)
    return (100 * np.sqrt(np.mean(v ** 2)), 100 * np.mean(v), len(v)) if len(v) else (np.nan, np.nan, 0)


sub = np.array(sub)
f = {k: np.array([cache['%s|%s' % (P[j]['arm'], P[j]['mask'])][k] for j in sub]) for k in ('A1', 'A2', 'FA', 'FB', 'n')}
bal = np.where(f['FA'] + f['FB'] > 0, 2 * np.minimum(f['FA'], f['FB']) / np.maximum(f['FA'] + f['FB'], 1), 0.0)
r = res[sub]
print('subset MASK points', len(sub), 'residual rms %.2f bias %+.2f' % rb(r)[:2])
for nm in ('A1', 'A2'):
    for v in (0, 1):
        s = f[nm] == v
        print('  %s=%d: rms %6.2f bias %+6.2f n %4d' % ((nm, v) + rb(r[s])))
s = (f['A1'] == 1) & (f['A2'] == 0)
print('  A1=1 but A2=0 (no diagonal shire, a cross pair aligned): rms %6.2f bias %+6.2f n %4d' % rb(r[s]))
print('  by Bal bins, A2=1 vs A2=0 (single and multi shire):')
for lo, hi in ((0, .05), (.05, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
    sb = (bal >= lo) & (bal < hi)
    a = r[sb & (f['A2'] == 1)]
    b = r[sb & (f['A2'] == 0)]
    print('    Bal %.2f-%.2f: A2=1 mean %+6.2f%% n %3d | A2=0 mean %+6.2f%% n %3d' % (lo, hi, 100 * a.mean() if len(a) else np.nan, len(a), 100 * b.mean() if len(b) else np.nan, len(b)))
print('  per arm (A2=1 vs A2=0 mean residual %, and Bal):')
arms = collections.defaultdict(list)
for i, j in enumerate(sub):
    arms[P[j]['arm']].append(i)
for a in sorted(arms):
    ii = np.array(arms[a])
    x1 = r[ii][f['A2'][ii] == 1]
    x0 = r[ii][f['A2'][ii] == 0]
    print('    %-14s A2=1 %+6.2f%% (n %3d)  A2=0 %+6.2f%% (n %3d)  Bal %.2f-%.2f' % (a, 100 * x1.mean() if len(x1) else np.nan, len(x1),
          100 * x0.mean() if len(x0) else np.nan, len(x0), bal[ii].min(), bal[ii].max()))
x = (f['A2'] * bal)
c = np.corrcoef(x, r)[0, 1]
c1 = np.corrcoef(f['A2'], r)[0, 1]
c2 = np.corrcoef(f['A1'], r)[0, 1]
c3 = np.corrcoef(f['A1'] * bal, r)[0, 1]
print('  correlation with the residual: A2 %.3f, A1 %.3f, A2*Bal %.3f, A1*Bal %.3f' % (c1, c2, c, c3))
