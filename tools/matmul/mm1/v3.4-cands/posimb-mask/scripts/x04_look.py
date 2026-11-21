#!/usr/bin/env python3
"""mask-posimb (Q238) x04: a look BEFORE the declaration (post hoc, in sample; disclosed in DECLARED): (1) the lane's MASK-class rule against
blind-e221's committed classes on E221's 733 cases; (2) posimb's frozen features made here against layout2's committed private_shared.json on
their common configurations; (3) MM1-v3.2's residuals ln(T_meas / T_v32) at the MASK points of every experiment (its all-data base for
E216-E224; its stored LOEO base for its own experiments), by shire count, by single shire (row group s>>2, column group s&3), and by the
mask's row groups R, column groups C and spread; NO constant of any candidate form is fitted here. Desk; numpy; single-threaded.
Output: work/x04_look.json + printed tables."""
import collections
import json
import os
import re

import numpy as np

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 'ffffffff'

D = json.load(open(os.path.join(LANE, 'work/points_all.json')))
P = D['points']
N = len(P)
Z = np.load(os.path.join(LANE, 'work/base.npz'))
PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
PS0 = json.load(open(os.path.join(LAB, 'tools/matmul/mm1/v3.3-cands/posimb/out/private_shared.json')))
Tm = Z['T_meas']
V32_EXPS = sorted({p['exp'] for p in P[:D['counts']['v32_fit']]})


def mint(m):
    return int(m, 16)


def shape(p):
    m = SH.match(p['arm'])
    return tuple(int(x) for x in m.groups()) if m else None


def is_gemmL136(p):
    return p['kernel'] == 'rgm136' and SH.match(p['arm']) is not None


# (1) the MASK class rule
def mask_class(P):
    sub = [False] * len(P)
    keys = set()
    for j, p in enumerate(P):
        if is_gemmL136(p) and mint(p['mask']) != 0xFFFFFFFF and shape(p) != (1, 1, 1):
            sub[j] = True
            for k in (p.get('kind') or '').split('+'):
                keys.add((p['exp'], p['card'], p['arm'], p['fmt'], k))
    cls = []
    for j, p in enumerate(P):
        if sub[j]:
            cls.append('MASK-sub')
        elif is_gemmL136(p) and mint(p['mask']) == 0xFFFFFFFF and any((p['exp'], p['card'], p['arm'], p['fmt'], k) in keys for k in (p.get('kind') or '').split('+')):
            cls.append('MASK-full')
        else:
            cls.append('')
    return cls


cls = mask_class(P)
agree = collections.Counter()
for j, p in enumerate(P):
    if p['exp'] == 'E221':
        agree[(p['cls221'] == 'MASK', cls[j] != '')] += 1
print('(1) E221 class agreement (committed MASK, rule MASK):', dict(agree))
print('    MASK points by experiment:', dict(collections.Counter(p['exp'] for j, p in enumerate(P) if cls[j])))
# (2) features vs posimb's committed
common = sorted(set(PS) & set(PS0))
mx = 0.0
for k in common:
    for f in ('Fp', 'Fs', 'Lmean_act', 'Lmax_act'):
        mx = max(mx, abs(PS[k][f] - PS0[k][f]))
print('(2) features: %d made, %d in layout2\'s committed file, max abs difference %.3g' % (len(PS), len(common), mx))
# (3) residuals
expa = np.array([p['exp'] for p in P])
base = Z['base_all'].copy()
e = Z['e_all'].copy()
for x in V32_EXPS:
    nm = 'base|LOEO ' + x
    if nm in Z.files:
        s = expa == x
        base[s] = Z[nm][s]
        e[s] = Z['e|LOEO ' + x][s]
res = np.log(Tm / base)
M = np.array([c != '' for c in cls])
Msub = np.array([c == 'MASK-sub' for c in cls])


def rb(v):
    v = np.asarray(v)
    return (100 * np.sqrt(np.mean(v ** 2)), 100 * np.mean(v), len(v)) if len(v) else (np.nan, np.nan, 0)


print('(3) MM1-v3.2 held-out-base residual ln(meas/v32) at MASK points: rms %.2f%% bias %+.2f%% n %d; subset only %.2f%% %+.2f%% n %d' % (rb(res[M]) + rb(res[Msub])))
nsh = np.array([bin(mint(p['mask'])).count('1') for p in P])
print('  by experiment (subset MASK):')
for x in sorted(set(expa[Msub]), key=lambda z: int(z[1:])):
    s = Msub & (expa == x)
    print('    %-5s rms %6.2f bias %+6.2f n %4d' % ((x,) + rb(res[s])))
print('  by shire count (subset MASK):')
for lo, hi in ((1, 1), (2, 2), (3, 3), (4, 7), (8, 15), (16, 23), (24, 31)):
    s = Msub & (nsh >= lo) & (nsh <= hi)
    print('    n %2d-%2d rms %6.2f bias %+6.2f n %4d' % ((lo, hi) + rb(res[s])))
# single shire: by shire, row group, column group, diagonal
single = Msub & (nsh == 1)
by_s = collections.defaultdict(list)
for j in np.where(single)[0]:
    s = mint(P[j]['mask']).bit_length() - 1
    by_s[s].append(j)
print('  single shire, by shire index s (row group s>>2, column group s&3): mean residual %, n, mean e')
rows = []
for s in sorted(by_s):
    jj = np.array(by_s[s])
    r = res[jj]
    rows.append((s, s >> 2, s & 3, ((s >> 2) & 3) == (s & 3), float(100 * r.mean()), len(jj), float(e[jj].mean())))
    print('    s %2d R %d C %d diag %-5s mean %+6.2f n %3d e %.2f  exps %s' % (rows[-1] + (sorted({P[j]['exp'] for j in jj}),)))
# single-shire residual vs (diag) and vs e
for lab, sel in (('diag', [((mint(P[j]['mask']).bit_length() - 1) >> 2) % 4 == ((mint(P[j]['mask']).bit_length() - 1) & 3) for j in np.where(single)[0]]),):
    sel = np.array(sel)
    jj = np.where(single)[0]
    print('  single shire: diagonal (R mod 4 == C) mean %+.2f%% n %d | off-diagonal mean %+.2f%% n %d' % (100 * res[jj[sel]].mean(), sel.sum(), 100 * res[jj[~sel]].mean(), (~sel).sum()))
    for elo, ehi in ((0, .2), (.2, .5), (.5, .8), (.8, 2)):
        es = (e[jj] >= elo) & (e[jj] < ehi)
        a = res[jj[sel & es]]
        b = res[jj[~sel & es]]
        print('    e %.1f-%.1f: diag %+6.2f%% (n %3d)  off %+6.2f%% (n %3d)' % (elo, ehi, 100 * a.mean() if len(a) else np.nan, len(a), 100 * b.mean() if len(b) else np.nan, len(b)))
# multi-shire: fraction of active shires on the diagonal, R, C
print('  multi-shire subset MASK points: residual by fraction of active shires on the diagonal (bins), and by (R, C)')
fd = np.zeros(N)
Rg = np.zeros(N, int)
Cg = np.zeros(N, int)
for j, p in enumerate(P):
    m = mint(p['mask'])
    act = [s for s in range(32) if (m >> s) & 1]
    fd[j] = np.mean([((s >> 2) & 3) == (s & 3) for s in act]) if act else 0
    Rg[j] = len({s >> 2 for s in act})
    Cg[j] = len({s & 3 for s in act})
multi = Msub & (nsh > 1)
for lo, hi in ((0, 0.001), (0.001, 0.26), (0.26, 0.51), (0.51, 0.99), (0.99, 1.01)):
    s = multi & (fd >= lo) & (fd < hi)
    print('    diag fraction %.2f-%.2f rms %6.2f bias %+6.2f n %4d' % ((lo, hi) + rb(res[s])))
rc = collections.defaultdict(list)
for j in np.where(Msub)[0]:
    rc[(Rg[j], Cg[j])].append(j)
for k in sorted(rc):
    jj = np.array(rc[k])
    print('    R %d C %d rms %6.2f bias %+6.2f n %4d  e %.2f' % (k + rb(res[jj]) + (float(e[jj].mean()),)))
json.dump({'agree_e221': {str(k): v for k, v in agree.items()}, 'single_shire_rows': rows, 'features_max_abs_diff_vs_layout2': mx,
           'n_features': len(PS), 'n_common': len(common)}, open(os.path.join(LANE, 'work/x04_look.json'), 'w'), indent=1)
