#!/usr/bin/env python3
"""lnc-form step 2: the declared fit, folds, pooled guard and placebo of every form in DECLARED-lnc-form.md (hashed 05:30:58 PST before this
script ran). Desk; numpy + scipy; single-threaded inside the round's CPU slots. Reads work/s01_points.json (sha256 in DECLARED.sha256),
MM1-v3.2's frozen params, its points_energy_v32.csv and holdout_v32.json (the git-archive copy of LAB's tools/ at main 0f046200)."""
import csv
import hashlib
import json
import os
import sys

import numpy as np
from scipy.optimize import lsq_linear

L = os.environ['LNC_FORM_DIR']
REPO = os.path.join(L, 'work', 'repo')
V32 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2')
sys.path.insert(0, os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3'))
import mm1_core_v3 as C  # noqa: E402

DECL = os.path.join(L, 'work', 'declared', 'DECLARED.sha256')
for line in open(DECL):
    if line.startswith('#') or not line.strip():
        continue
    h, fn = line.split()
    p = os.path.normpath(os.path.join(L, 'work', 'declared', fn))
    assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == h, ('declared file changed', fn)

P = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
X1 = float(P['time']['theta']['x1'])
D = json.load(open(os.path.join(L, 'work', 's01_points.json')))
PTS = D['points']
N = len(PTS)
assert N == 36, N


# ------------------------------------------------------------------ features (DECLARED section 2)
def feats(arm_shape, fmt, qA, qB, mask='0xffffffff'):
    MB, NB, KB = arm_shape
    mi = C.mask_info(mask)
    sa, sb = mi['sa'], mi['sb']
    qA_b = 1.0 - qA[0]
    qB_b = 1.0 - qB[0]
    qBF = qB[2]
    beyond = 14.0 * qA_b + 12.0 * qB_b
    first = beyond / NB
    phi = 1.0 if MB == 1 else (NB - 1.0) / NB
    m = 1.0 if (2.0 * KB * sa + KB * sb) > X1 else 0.0
    a_f = (1.0 - phi) + phi * m
    Lres = 1.0 if C.footprint(MB, NB, KB, mi) <= X1 else 0.0
    if NB == 1 or m == 1.0:
        a3 = 1.0
    elif NB == 2:
        a3 = 1.0 - phi
    else:
        a3 = 0.0
    R1 = a_f * (14.0 * qA_b + 12.0 * qBF)
    R3 = a3 * (14.0 * qA_b + 12.0 * qBF)
    R2 = Lres * beyond + (1.0 - Lres) * R1
    R4 = Lres * beyond + (1.0 - Lres) * R3
    return {'dup': 26.0, 'beyond': beyond, 'first': first, 'qA_b': qA_b, 'qBF': qBF, 'phi': phi, 'm': m, 'a_f': a_f, 'a3': a3, 'Lres': Lres,
            'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4, 'stepNB3': beyond * (1.0 if NB <= 3 else 0.0), 'MB': MB, 'NB': NB, 'KB': KB,
            'footprint_MB': C.footprint(MB, NB, KB, mi)}


FORMS = {  # name: list of feature columns (c1 on the first, c2 on the second)
    'F3r': ['dup', 'first'], 'F1r': ['dup'], 'F2r': ['dup', 'beyond'], 'F4r': ['beyond'], 'STEPr': ['dup', 'stepNB3'],
    'AF1': ['dup', 'R1'], 'AF2': ['dup', 'R2'], 'AF3': ['dup', 'R3'], 'AF4': ['dup', 'R4']}
NEW_ORDER = ['AF4', 'AF3', 'AF2', 'AF1', 'STEPr', 'F2r', 'F4r', 'F1r']   # the declared tie order (section 6)

F = [feats((p['MB'], p['NB'], p['KB']), p['fmt'], p['qA_L2_L3_F'], p['qB_L2_L3_F'], p['mask']) for p in PTS]
W = np.array([p['w'] for p in PTS])
BASE = np.array([p['base_W'] for p in PTS])
S = np.array([p['S'] for p in PTS])
EXP = np.array([p['exp'] for p in PTS])
CARD = np.array([p['card'] for p in PTS])
IDS = [p['id'] for p in PTS]


def colmat(form, feat_rows=None):
    fr = feat_rows if feat_rows is not None else F
    return np.array([[r[c] for c in FORMS[form]] for r in fr])


def fit(form, idx, Xf=None):
    Xf = colmat(form) if Xf is None else Xf
    A = (S[idx, None] * Xf[idx]) / W[idx, None]
    y = 1.0 - BASE[idx] / W[idx]
    r = lsq_linear(A, y, bounds=(0.0, 10000.0), method='bvls', tol=1e-12)
    return r.x


def predict(form, c, idx, Xf=None):
    Xf = colmat(form) if Xf is None else Xf
    return BASE[idx] + S[idx] * (Xf[idx] @ c)


def rms_bias(pred, meas):
    e = pred / meas - 1.0
    return [float(100 * np.sqrt(np.mean(e * e))), float(100 * np.mean(e))]


def heldout(form, groups, Xf=None):
    """refit without each group; predictions at the held-out points"""
    pred = np.full(N, np.nan)
    consts = {}
    for g in sorted(set(groups)):
        te = np.where(groups == g)[0]
        tr = np.where(groups != g)[0]
        c = fit(form, tr, Xf)
        consts[str(g)] = c.tolist()
        pred[te] = predict(form, c, te, Xf)
    return pred, consts


OUT = {'declared_sha256_file': DECL, 'x1_MB': X1, 'forms': {}}
LOPO_G = np.arange(N)
for form in FORMS:
    allc = fit(form, np.arange(N))
    pin = predict(form, allc, np.arange(N))
    pe, ce = heldout(form, EXP)
    pc, cc = heldout(form, CARD)
    pp, _ = heldout(form, LOPO_G)
    rec = {'features': FORMS[form], 'constants_all_data_pJ': allc.tolist(),
           'in_sample': rms_bias(pin, W), 'LOEO': rms_bias(pe, W), 'LOCO': rms_bias(pc, W), 'LOPO': rms_bias(pp, W),
           'LOEO_consts': ce, 'LOCO_consts': cc,
           'LOEO_by_fold': {g: rms_bias(pe[EXP == g], W[EXP == g]) + [int((EXP == g).sum())] for g in sorted(set(EXP))},
           'LOCO_by_fold': {g: rms_bias(pc[CARD == g], W[CARD == g]) + [int((CARD == g).sum())] for g in sorted(set(CARD))},
           'per_point': [{'id': IDS[i], 'meas_W': float(W[i]), 'in_sample_err_pct': float(100 * (pin[i] / W[i] - 1)),
                          'LOEO_err_pct': float(100 * (pe[i] / W[i] - 1)), 'LOCO_err_pct': float(100 * (pc[i] / W[i] - 1)),
                          'term_W_all_data': float(pin[i] - BASE[i]), 'feature_c2': (float(colmat(form)[i, -1]))} for i in range(N)]}
    OUT['forms'][form] = rec

# ------------------------------------------------------------------ MM1-v3.2 as frozen at the 36 points (REPORTED beside)
v32 = np.array([p['v32_W_given_t'] for p in PTS])
OUT['MM1-v3.2_frozen_at_points'] = {'all_data_or_blind': rms_bias(v32, W),
                                    'by_exp': {g: rms_bias(v32[EXP == g], W[EXP == g]) + [int((EXP == g).sum())] for g in sorted(set(EXP))}}

# ------------------------------------------------------------------ the pooled guard (section 6 rule 2)
rows = list(csv.DictReader(open(os.path.join(V32, 'out', 'points_energy_v32.csv'))))
H = json.load(open(os.path.join(V32, 'out', 'holdout_v32.json')))['energy']['by_fold']


def ok3(r):
    return float(r['meas_W_over_idle']) >= 3.0 and r['twin_LOEO'] == '0'


base_err = []
lnc_rows = {}
for r in rows:
    if not ok3(r):
        continue
    if r['gemmLnc'] == '1':
        lnc_rows[r['id']] = r
        continue
    base_err.append(float(r['v32_LOEO_W_given_t']) / float(r['meas_W_over_idle']) - 1.0)
base_err = np.array(base_err)
idx_in = [i for i, p in enumerate(PTS) if p['id'] in lnc_rows]
assert len(idx_in) == 14, len(idx_in)
v32_rec_all = np.array([float(r['v32_LOEO_W_given_t']) / float(r['meas_W_over_idle']) - 1.0 for r in rows if ok3(r)])
check_v32_record = (float(100 * np.sqrt(np.mean(v32_rec_all ** 2))), len(v32_rec_all))
fold_base = {}
for i in idx_in:
    p = PTS[i]
    r = lnc_rows[p['id']]
    c3 = H['LOEO ' + p['exp']]['F3']
    f3_fold = S[i] * (c3['c1'] * 26.0 + c3['c2'] * F[i]['first'])
    fold_base[i] = float(r['v32_LOEO_W_given_t']) - f3_fold
idx_new = [i for i, p in enumerate(PTS) if p['exp'] in ('E216', 'E218')]


def pooled(errs_lnc):
    e = np.concatenate([base_err, np.array(errs_lnc)])
    return float(100 * np.sqrt(np.mean(e * e))), len(e)


v32_lnc = [float(lnc_rows[PTS[i]['id']]['v32_LOEO_W_given_t']) / W[i] - 1.0 for i in idx_in] + [v32[i] / W[i] - 1.0 for i in idx_new]
OUT['pooled_guard'] = {'check_MM1-v3.2_record_no_twins_ge3W': check_v32_record, 'MM1-v3.2': pooled(v32_lnc), 'forms': {}}
for form in FORMS:
    pe, ce = heldout(form, EXP)
    errs = []
    for i in idx_in:
        c = np.array(ce[PTS[i]['exp']])
        errs.append((fold_base[i] + S[i] * (colmat(form)[i] @ c)) / W[i] - 1.0)
    for i in idx_new:
        errs.append(pe[i] / W[i] - 1.0)
    OUT['pooled_guard']['forms'][form] = pooled(errs)

# ------------------------------------------------------------------ the placebo (section 6 rule 3)
OUT['placebo'] = {}
for form in FORMS:
    Xf = colmat(form)
    col = Xf.shape[1] - 1
    if np.ptp(Xf[:, col]) == 0.0:
        OUT['placebo'][form] = 'NOT APPLICABLE: no non-constant feature'
        continue
    real = OUT['forms'][form]['LOEO'][0]
    wins, vals = 0, []
    for j in range(100):
        rng = np.random.default_rng(20261120 + j)
        Xp = Xf.copy()
        Xp[:, col] = Xf[rng.permutation(N), col]
        pe, _ = heldout(form, EXP, Xp)
        v = rms_bias(pe, W)[0]
        vals.append(v)
        wins += int(real < v)
    OUT['placebo'][form] = {'real_LOEO': real, 'wins_of_100': wins, 'placebo_LOEO_median': float(np.median(vals)),
                            'placebo_LOEO_min': float(np.min(vals))}

# ------------------------------------------------------------------ the keep rule and the choice (section 6)
F3L = OUT['forms']['F3r']['LOEO'][0]
P32 = OUT['pooled_guard']['MM1-v3.2'][0]
keep = {}
for form in NEW_ORDER:
    pl = OUT['placebo'][form]
    r1 = OUT['forms'][form]['LOEO'][0] <= F3L - 1.0
    r2 = OUT['pooled_guard']['forms'][form][0] <= P32 + 0.05
    r3 = isinstance(pl, dict) and pl['wins_of_100'] >= 95
    keep[form] = {'margin_1pt': r1, 'pooled_guard': r2, 'placebo_95': r3, 'kept': bool(r1 and r2 and r3),
                  'LOEO': OUT['forms'][form]['LOEO'][0], 'F3r_LOEO': F3L, 'pooled': OUT['pooled_guard']['forms'][form][0], 'pooled_v32': P32}
kept = [f for f in NEW_ORDER if keep[f]['kept']]


def choose(cands):
    best = min(OUT['forms'][f]['LOEO'][0] for f in cands)
    near = [f for f in cands if OUT['forms'][f]['LOEO'][0] <= best + 0.25]
    ncon = min(len(FORMS[f]) for f in near)
    near = [f for f in near if len(FORMS[f]) == ncon]
    return sorted(near, key=NEW_ORDER.index)[0]


if kept:
    OUT['choice'] = {'form': choose(kept), 'status': 'KEPT', 'kept': kept}
else:
    OUT['choice'] = {'form': choose(NEW_ORDER), 'status': 'REJECTED CANDIDATE (none kept)', 'kept': []}
OUT['keep_rule'] = keep
OUT['features_per_point'] = [{'id': IDS[i], **F[i]} for i in range(N)]
OUT['twins_REPORTED'] = [{'id': p['twin']['id'], 'of': p['id'], 'meas_W': p['twin']['w'], 'v32_W_given_t': p['twin']['v32_W_given_t'],
                          'err_pct': 100 * (p['twin']['v32_W_given_t'] / p['twin']['w'] - 1)} for p in PTS if p.get('twin')]
tw = np.array([t['err_pct'] for t in OUT['twins_REPORTED']])
OUT['twins_summary'] = {'n': len(tw), 'rms_pct': float(np.sqrt(np.mean(tw ** 2))), 'bias_pct': float(np.mean(tw))}
json.dump(OUT, open(os.path.join(L, 'work', 's02_fit.json'), 'w'), indent=1)

print('x1', X1, 'pooled check (v3.2 record, no twins, >=3W):', check_v32_record)
print('%-6s %-18s %-14s %-14s %-14s %-14s %-12s %-10s' % ('form', 'c (pJ)', 'in-sample', 'LOEO', 'LOCO', 'LOPO', 'pooled', 'placebo'))
for form in FORMS:
    r = OUT['forms'][form]
    pl = OUT['placebo'][form]
    print('%-6s %-18s %5.2f (%+5.2f) %5.2f (%+5.2f) %5.2f (%+5.2f) %5.2f (%+5.2f) %6.3f %s' % (
        form, ','.join('%.1f' % x for x in r['constants_all_data_pJ']), *r['in_sample'], *r['LOEO'], *r['LOCO'], *r['LOPO'],
        OUT['pooled_guard']['forms'][form][0], (pl['wins_of_100'] if isinstance(pl, dict) else 'n/a')))
print('MM1-v3.2 pooled', OUT['pooled_guard']['MM1-v3.2'], ' MM1-v3.2 frozen at the 36:', OUT['MM1-v3.2_frozen_at_points']['all_data_or_blind'])
for form in FORMS:
    print(form, 'LOEO by fold', {g: '%.2f(%+.2f) n%d' % tuple(v) for g, v in OUT['forms'][form]['LOEO_by_fold'].items()})
    print(form, 'LOCO by fold', {g[-6:]: '%.2f(%+.2f) n%d' % tuple(v) for g, v in OUT['forms'][form]['LOCO_by_fold'].items()})
print('keep', json.dumps(keep, indent=0))
print('CHOICE', OUT['choice'])
print('twins', OUT['twins_summary'])
