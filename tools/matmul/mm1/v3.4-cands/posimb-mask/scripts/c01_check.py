#!/usr/bin/env python3
"""mask-posimb (Q238) c01: a self-check of g01's deciding numbers BY SEPARATE CODE (not imported from g01): the MASK class, A1, posimb's two
features, the LOSO, LOMO and LOEO held-out predictions and the all-data constants re-derived from points_all.json, base.npz and
private_shared.json with a different solver (the normal equations), compared with work/fit_results.json; then the frozen predictor module
(land/.../posimb_mask.py, staged into the lane's own clone at its repository path) called on all 4311 points: its op times against
T_v32 x the factor at the all-data constants, and its features made fresh by the walk at 40 configurations against the cache.
Desk; numpy; single-threaded. Output: work/check_c01.json."""
import json
import os
import random
import shutil
import sys

import numpy as np

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask')
STAGE = os.path.join(LAB, 'tools/matmul/mm1/v3.4-cands/posimb-mask')
F = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
Z = np.load(os.path.join(LANE, 'work/base.npz'))
PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
rung_ids = set(json.load(open(os.path.join(LAB, 'tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json')))['store_rung_ids'])
N = len(P)
Tm = np.array([p['T'] for p in P])
out = {}


def isgl(arm):
    if not arm.startswith('gemmL') or arm.startswith('gemmLn'):
        return None
    try:
        return tuple(int(x) for x in arm[5:].split('x'))
    except ValueError:
        return None


# (1) class, A1, features, separately
sc = np.zeros(N, bool)
X3 = np.zeros((N, 3))
cls = np.zeros(N, bool)
subkeys = set()
for j, p in enumerate(P):
    s = isgl(p['arm'])
    m = int(p['mask'], 16)
    if s is not None and p['kernel'] == 'rgm136' and m != 0xFFFFFFFF:
        sc[j] = True
        r = PS['%s|0x%x' % (p['arm'], m)]
        act = [i for i in range(32) if m >> i & 1]
        a1 = 0.0 if any((i // 4) % 4 == i % 4 for i in act) else 1.0
        tot = r['Fp'] + r['Fs']
        X3[j] = [r['Lmean_act'] / r['Lmean_full'] - 1.0, (r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full'] * (r['Fp'] / tot if tot else 0.0), a1]
        if s != (1, 1, 1):
            cls[j] = True
            for k in str(p.get('kind')).split('+'):
                subkeys.add((p['exp'], p['card'], p['arm'], p['fmt'], k))
for j, p in enumerate(P):
    if not cls[j] and isgl(p['arm']) is not None and p['kernel'] == 'rgm136' and int(p['mask'], 16) == 0xFFFFFFFF:
        cls[j] = any((p['exp'], p['card'], p['arm'], p['fmt'], k) in subkeys for k in str(p.get('kind')).split('+'))
out['n_MASK'] = int(cls.sum())
out['n_MASK_g01'] = F['n_MASK']
rung = np.array([p['id'] in rung_ids for p in P])


def fitne(rho, Phi, tr):
    X = rho[tr, None] * Phi[tr]
    y = 1.0 - rho[tr]
    return np.linalg.solve(X.T @ X, X.T @ y)


def pred(b, Phi, a):
    return b * np.clip(1.0 + Phi @ a, 0.3, 3.0)


ball, eall = Z['base_all'], Z['e_all']
Phi_all = (eall[:, None] * X3) * sc[:, None]
head = np.array([p['exp'] == 'E221' and p['cls221'] == 'MASK' and not p['twin_v32_e221'] for p in P])
# LOSO
acc = np.zeros(N)
cnt = np.zeros(N)
for s in sorted({x for p in P if p['exp'] == 'E221' for x in p['sessions']}):
    te = np.array([p['exp'] == 'E221' and s in p['sessions'] for p in P])
    a = fitne(ball / Tm, Phi_all, ~te & ~rung)
    acc[te] += pred(ball, Phi_all, a)[te]
    cnt[te] += 1
m1 = float(100 * np.sqrt(np.mean((acc[head] / cnt[head] / Tm[head] - 1) ** 2)))
# LOMO
lomo = np.full(N, np.nan)
masks = sorted({p['mask'].lower() for j, p in enumerate(P) if sc[j] and p['exp'] in ('E221', 'E217', 'E224')})
for m in masks:
    te = sc & np.array([p['mask'].lower() == m for p in P])
    a = fitne(ball / Tm, Phi_all, ~te & ~rung)
    lomo[te] = pred(ball, Phi_all, a)[te]
x = np.where(np.isnan(lomo), ball, lomo)
m1l = float(100 * np.sqrt(np.mean((x[head] / Tm[head] - 1) ** 2)))
# LOEO (M4, M2)
twinkey = {}
for p in P:
    twinkey.setdefault((p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower()), set()).add(p['exp'])
twin = np.array([len(twinkey[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())] - {p['exp']}) > 0 for p in P])
loeo = np.zeros(N)
loeo_v = np.zeros(N)
for xexp in sorted({p['exp'] for p in P}):
    te = np.array([p['exp'] == xexp for p in P])
    nm = 'base|LOEO ' + xexp
    b = Z[nm] if nm in Z.files else ball
    e = Z['e|LOEO ' + xexp] if nm in Z.files else eall
    Phi = (e[:, None] * X3) * sc[:, None]
    a = fitne(b / Tm, Phi, ~te & ~rung)
    loeo[te] = pred(b, Phi, a)[te]
    loeo_v[te] = b[te]
expa = np.array([p['exp'] for p in P])
s4 = cls & (expa != 'E221') & ~twin
s2 = ~cls & ~twin
m4 = float(100 * np.sqrt(np.mean((loeo[s4] / Tm[s4] - 1) ** 2)))
m4v = float(100 * np.sqrt(np.mean((loeo_v[s4] / Tm[s4] - 1) ** 2)))
m2 = float(100 * np.sqrt(np.mean((loeo[s2] / Tm[s2] - 1) ** 2)))
m2v = float(100 * np.sqrt(np.mean((loeo_v[s2] / Tm[s2] - 1) ** 2)))
a_all = fitne(ball / Tm, Phi_all, ~rung)
out['separate_code'] = {'M1': m1, 'M1L': m1l, 'M4': m4, 'M4_v32': m4v, 'M2': m2, 'M2_v32': m2v, 'a_all': a_all.tolist()}
out['g01'] = {'M1': F['M1_LOSO_head_rms_pct']['cand'], 'M1L': F['M1L_LOMO_head_rms_pct']['cand'], 'M4': F['M4_LOEO_MASK_not_E221_no_twin_rms_pct']['cand'],
              'M4_v32': F['M4_LOEO_MASK_not_E221_no_twin_rms_pct']['v32'], 'M2': F['M2_LOEO_nonMASK_no_twin_rms_pct']['cand'],
              'M2_v32': F['M2_LOEO_nonMASK_no_twin_rms_pct']['v32'], 'a_all': F['constants_all_data']['cand']}
out['max_abs_diff'] = max(abs(out['separate_code'][k] - out['g01'][k]) for k in ('M1', 'M1L', 'M4', 'M4_v32', 'M2', 'M2_v32'))
out['max_abs_diff_constants'] = float(np.max(np.abs(np.array(out['separate_code']['a_all']) - np.array(out['g01']['a_all']))))
print('(1) separate code vs g01:', json.dumps(out['separate_code']), '\n    g01:', json.dumps(out['g01']))
print('    max |diff| metrics %.3g, constants %.3g; MASK %d vs %d' % (out['max_abs_diff'], out['max_abs_diff_constants'], out['n_MASK'], out['n_MASK_g01']))
# (2) the frozen module, staged at its repository path in the lane's clone
if os.path.isdir(STAGE):
    shutil.rmtree(STAGE)
shutil.copytree(LAND, STAGE)
sys.path.insert(0, STAGE)
import posimb_mask as PM  # noqa: E402
M = PM.Model()
specs = [{'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': 'random', 'mask': p['mask'], 'f': float(p['f']),
          'kernel': p['kernel']} for p in P]
rows = M.predict_many(specs)
Tmod = np.array([r[PM.LABEL]['T_op_us'] for r in rows])
Tref = pred(ball, Phi_all, np.array(F['constants_all_data']['cand']))
rel = np.abs(Tmod / Tref - 1)
out['module_vs_reference_max_rel'] = float(rel.max())
out['module_scope_equal'] = bool(np.array_equal(np.array([r['in_scope'] for r in rows]), sc))
out['module_v32_vs_base_all_max_rel'] = float(np.max(np.abs(np.array([r['MM1-v3.2']['T_op_us'] for r in rows]) / ball - 1)))
keys = sorted(PS)
random.seed(20261121)
sample = random.sample(keys, 40)
mx = 0.0
for k in sample:
    arm, m = k.split('|')
    MB, NB, KB = (int(x) for x in arm[5:].split('x'))
    r = PM.private_shared(MB, NB, KB, int(m, 16))
    r.update(PM.mesh_lat(int(m, 16)))
    for q in ('Fp', 'Fs', 'Lmean_act', 'Lmax_act', 'Lmean_full'):
        mx = max(mx, abs(r[q] - PS[k][q]))
out['features_fresh_vs_cache_max_abs'] = mx
print('(2) module: op time vs reference max rel %.3g; scope equal %s; its MM1-v3.2 vs base max rel %.3g; fresh features (40) max abs %.3g' % (
    out['module_vs_reference_max_rel'], out['module_scope_equal'], out['module_v32_vs_base_all_max_rel'], mx))
json.dump(out, open(os.path.join(LANE, 'work/check_c01.json'), 'w'), indent=1)
