#!/usr/bin/env python3
"""mask-mesh (Q238, track M) m03: THE DECLARED PROCEDURE (DECLARED-mesh.md): the fit of 'MM1-v3.2 + mesh' on every committed matmul time point
through E224, the held-out folds, the keep rule, the placebo, and the REPORTED controls. Run only after DECLARED-mesh.md and the code are
hashed (DECLARED.sha256). Desk; numpy + scipy; single-threaded inside the round's CPU slots.
Run: bash run.sh m03_fit.py <lane dir> [--placebo-draws 100]  ->  work/fit/ (fit-mesh.json, holdout-mesh.json, placebo-mesh.json, ...)"""
import collections
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
NDRAW = int(sys.argv[sys.argv.index('--placebo-draws') + 1]) if '--placebo-draws' in sys.argv else 100
os.environ['MASK_MESH_LANE'] = L
sys.path.insert(0, os.path.join(L, 'scripts'))
import mesh_term as MT  # noqa: E402

OUTD = os.path.join(L, 'work', 'fit')
os.makedirs(OUTD, exist_ok=True)
T_START = time.strftime('%Y-%m-%d %H:%M:%S %Z')
DECL = os.path.join(L, 'DECLARED-mesh.md')
DECL_SHA = hashlib.sha256(open(DECL, 'rb').read()).hexdigest()
REC = json.load(open(os.path.join(L, 'DECLARED.sha256.json')))
assert REC['DECLARED-mesh.md'] == DECL_SHA, 'DECLARED-mesh.md changed since it was hashed'
for rel, h in REC['code'].items():
    assert hashlib.sha256(open(os.path.join(L, rel), 'rb').read()).hexdigest() == h, f'{rel} changed since the declaration was hashed'

PT = json.load(open(os.path.join(L, 'work', 'points-mesh.json')))
P = PT['points']
FC = json.load(open(os.path.join(L, 'work', 'features-mesh.json')))['configs']
V32 = MT.V32
V32P = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
FITS = json.load(open(os.path.join(V32, 'out', 'fits', 'time_T5r+G0+n32.json')))
FORM = V32P['time']['form']
TH_ALL = V32P['time']['theta']
N = len(P)
Tm = np.array([p['T'] for p in P], float)
lay = np.array([p['layout_point'] for p in P])
MASK = np.array([bool(p['MASK']) for p in P])
twx = np.array([bool(p['twin_x']) for p in P])
exp_ = np.array([p['exp'] for p in P])
card = np.array([p['card'] for p in P])
maskh = np.array([MT.mask_hex(p['mask']) for p in P])
LEAD = np.array([p['exp'] == 'E221' and bool(p['MASK']) and not p.get('twin_v32') for p in P])     # the lead's 363 cases
assert int(LEAD.sum()) == 363, int(LEAD.sum())
IL = np.where(lay)[0]
PL = [P[i] for i in IL]
log = open(os.path.join(OUTD, 'm03.log'), 'a')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    log.write(s + '\n')
    log.flush()


say(f'm03 start {T_START}; N {N} points, {len(IL)} in the term\'s scope; DECLARED sha256 {DECL_SHA}')

# ------------------------------------------------------------------ the bases: MM1-v3.2's op time at each fold's constants
eng_all = MT.TV.Engine31([{k: p[k] for k in ('arm', 'kernel', 'fmt', 'mask', 'f')} for p in P])
eng_lay = MT.TV.Engine31([{k: p[k] for k in ('arm', 'kernel', 'fmt', 'mask', 'f')} for p in PL])
THETAS = {'all-data': TH_ALL}
for name, fd in FITS['folds'].items():
    if name.startswith('LOEO ') or name.startswith('LOCO '):
        THETAS[name] = fd['theta']
T0 = {}
BL = {}
for name, th in THETAS.items():
    T0[name] = eng_all.predict(th, FORM)
    BL[name] = MT.Base(PL, th, FORM, eng31=eng_lay)
    assert np.array_equal(BL[name].T0, T0[name][IL]), name
say('bases made:', len(THETAS), 'constant sets; the re-made engine equals Engine31.predict at zero term in every one (max rel diff 0)')
# check against MM1-v3.2's own records (its 2508 points)
v32rows = {r['id']: r for r in csv.DictReader(open(os.path.join(V32, 'out', 'points_time_v32.csv')))}
chk = []
for i, p in enumerate(P):
    r = v32rows.get(p['id'])
    if r is not None:
        chk.append(abs(T0['all-data'][i] / float(r['v32_all_data_T_us']) - 1.0))
say(f'MM1-v3.2 all-data op time re-made at its {len(chk)} own points: max rel diff {max(chk):.3e}')


def base_name_loeo(e):
    return f'LOEO {e}' if f'LOEO {e}' in THETAS else 'all-data'


# ------------------------------------------------------------------ features
X = {v: MT.feature_matrix(PL, FC, v) for v in ('laggard', 'chip', 'fa', 'mean_hop')}
STARTS = ((1.0, 1.0), (0.0, 0.0))


def fit_idx(bname, Xv, idx_local, fixed=None):
    """fit on the scope points idx_local (indices into PL); fixed: {'a_set': v} or {'a_hop': v} for the REPORTED one-part controls"""
    b = BL[bname]
    bounds = dict(MT.BOUNDS)
    if fixed:
        for k, v in fixed.items():
            bounds[k] = (v - 1e-12, v + 1e-12)
        st = tuple(tuple(fixed.get(k, s[j]) for j, k in enumerate(('a_set', 'a_hop'))) for s in STARTS)
    else:
        st = STARTS
    a, c, ends = MT.fit(b, Xv, Tm[IL], idx_local, starts=st, bounds=bounds)
    return a, c, ends


def predict_lay(bname, Xv, a):
    return BL[bname].Tx(Xv, a)


LPOS = {int(i): j for j, i in enumerate(IL)}


def run_folds(Xv, kinds=('LOMO', 'LOSO', 'LOEO', 'LOCO'), fixed=None, record=True):
    """held-out op times for every point under each fold kind (points out of the term's scope: the fold base's MM1-v3.2 op time)"""
    out, consts = {}, {}
    if 'LOMO' in kinds:
        Tp = T0['all-data'].copy()
        masks = sorted({maskh[i] for i in IL if exp_[i] in ('E221', 'E217', 'E224')})
        cs = {}
        for m in masks:
            te = [j for j, i in enumerate(IL) if maskh[i] == m]
            tr = [j for j, i in enumerate(IL) if maskh[i] != m]
            a, _, _ = fit_idx('all-data', Xv, np.array(tr), fixed)
            Tl = predict_lay('all-data', Xv, a)
            for j in te:
                Tp[IL[j]] = Tl[j]
            cs[m] = a
        out['LOMO'] = Tp
        consts['LOMO'] = cs
        out['LOMO_masks'] = masks
    if 'LOSO' in kinds:
        Tp = T0['all-data'].copy()
        ss = sorted({s for p in P if p['exp'] == 'E221' for s in p['sessions']})
        cs = {}
        for s in ss:
            hit = [i for i, p in enumerate(P) if p['exp'] == 'E221' and s in p['sessions']]
            hs = set(hit)
            tr = [j for j, i in enumerate(IL) if int(i) not in hs]
            a, _, _ = fit_idx('all-data', Xv, np.array(tr), fixed)
            Tl = predict_lay('all-data', Xv, a)
            for i in hit:
                if P[i]['session'] == s and lay[i]:
                    Tp[i] = Tl[LPOS[i]]
            cs[s] = a
        out['LOSO'] = Tp
        consts['LOSO'] = cs
    if 'LOEO' in kinds:
        Tp = np.zeros(N)
        cs = {}
        for e in sorted(set(exp_)):
            bn = base_name_loeo(e)
            te = np.where(exp_ == e)[0]
            Tp[te] = T0[bn][te]
            tr = [j for j, i in enumerate(IL) if exp_[i] != e]
            tl = [j for j, i in enumerate(IL) if exp_[i] == e]
            if tl:
                a, _, _ = fit_idx(bn, Xv, np.array(tr), fixed)
                Tl = predict_lay(bn, Xv, a)
                for j in tl:
                    Tp[IL[j]] = Tl[j]
                cs[e] = a
        out['LOEO'] = Tp
        consts['LOEO'] = cs
    if 'LOCO' in kinds:
        Tp = np.zeros(N)
        cs = {}
        for c in sorted(set(card)):
            bn = f'LOCO {c}'
            te = np.where(card == c)[0]
            Tp[te] = T0[bn][te]
            tr = [j for j, i in enumerate(IL) if card[i] != c]
            tl = [j for j, i in enumerate(IL) if card[i] == c]
            a, _, _ = fit_idx(bn, Xv, np.array(tr), fixed)
            Tl = predict_lay(bn, Xv, a)
            for j in tl:
                Tp[IL[j]] = Tl[j]
            cs[c] = a
        out['LOCO'] = Tp
        consts['LOCO'] = cs
    return out, consts


def rms(T, sel):
    e = T[sel] / Tm[sel] - 1.0
    return float(100.0 * math.sqrt(np.mean(e * e))) if len(e) else None, float(100.0 * np.mean(e)) if len(e) else None, int(len(e))


# MM1-v3.2's own held-out op times (the comparators): all-data for E216-E224 (never in its fit), its stored fold constants otherwise
BASE = {'LOMO': T0['all-data'], 'LOSO': T0['all-data']}
BASE['LOEO'] = np.array([T0[base_name_loeo(exp_[i])][i] for i in range(N)])
BASE['LOCO'] = np.array([T0[f'LOCO {card[i]}'][i] for i in range(N)])

# ------------------------------------------------------------------ 1. the all-data fit (the frozen constants)
t1 = time.time()
a_all, c_all, ends_all = fit_idx('all-data', X['laggard'], np.arange(len(IL)))
say(f'all-data fit: a_set {a_all[0]:.6f} a_hop {a_all[1]:.6f} cost {c_all:.6f} ({time.time() - t1:.1f} s); ends {ends_all}')
T_ins = T0['all-data'].copy()
T_ins[IL] = predict_lay('all-data', X['laggard'], a_all)

# ------------------------------------------------------------------ 2. the held-out folds
t1 = time.time()
HO, CS = run_folds(X['laggard'])
say(f'folds done ({time.time() - t1:.1f} s)')

SEL = {'lead E221 MASK no-twin (363)': LEAD,
       'MASK all points, no twin': MASK & ~twx,
       'MASK all points': MASK,
       'MASK subset points, no twin': MASK & lay & ~twx,
       'non-MASK, no twin': ~MASK & ~twx,
       'non-MASK subset points (scope), no twin': ~MASK & lay & ~twx}
loeo_late = np.isin(exp_, ['E215', 'E216', 'E217', 'E218', 'E219', 'E220', 'E221', 'E222', 'E224'])
lomo_cover = np.isin(maskh, HO['LOMO_masks'])
table = {}
for fk in ('LOMO', 'LOSO', 'LOEO', 'LOCO'):
    for sname, s in SEL.items():
        ss = s.copy()
        if fk == 'LOMO' and sname not in ('lead E221 MASK no-twin (363)',):
            ss = ss & (lomo_cover | ~lay)
        table[f'{fk} | {sname}'] = {'MM1-v3.2': rms(BASE[fk], ss), 'MM1-v3.2 + mesh': rms(HO[fk], ss)}
table['LOEO (E215-E224 folds) | lead E221 MASK no-twin (363)'] = {'MM1-v3.2': rms(BASE['LOEO'], LEAD & loeo_late), 'MM1-v3.2 + mesh': rms(HO['LOEO'], LEAD & loeo_late)}
table['LOEO (E215-E224 folds) | MASK all points, no twin'] = {'MM1-v3.2': rms(BASE['LOEO'], MASK & ~twx & loeo_late),
                                                             'MM1-v3.2 + mesh': rms(HO['LOEO'], MASK & ~twx & loeo_late)}
table['in sample | lead E221 MASK no-twin (363)'] = {'MM1-v3.2': rms(T0['all-data'], LEAD), 'MM1-v3.2 + mesh': rms(T_ins, LEAD)}
for k, v in table.items():
    say(f'{k}: MM1-v3.2 {v["MM1-v3.2"]} | + mesh {v["MM1-v3.2 + mesh"]}')

# ------------------------------------------------------------------ 3. the keep rule (declared)
v32_K1 = rms(BASE['LOMO'], LEAD)[0]
t_K1 = rms(HO['LOMO'], LEAD)[0]
K1 = t_K1 <= v32_K1 - 1.0
K2 = {fk: (rms(HO[fk], LEAD & (loeo_late if fk == 'LOEO' else np.ones(N, bool)))[0] < rms(BASE[fk], LEAD & (loeo_late if fk == 'LOEO' else np.ones(N, bool)))[0])
      for fk in ('LOSO', 'LOEO', 'LOCO')}
g_b = rms(BASE['LOEO'], ~MASK & ~twx)[0]
g_t = rms(HO['LOEO'], ~MASK & ~twx)[0]
K3 = g_t <= g_b + 0.05
say(f'K1 LOMO lead: MM1-v3.2 {v32_K1:.3f}% -> {t_K1:.3f}% (needs <= {v32_K1 - 1.0:.3f}): {K1}; K2 {K2}; K3 guard {g_b:.4f} -> {g_t:.4f} (<= +0.05): {K3}')

# ------------------------------------------------------------------ 4. the placebo (declared): the mask features permuted within each shape
arm_l = [PL[j]['arm'] for j in range(len(PL))]
cfgs = collections.defaultdict(list)
for j, p in enumerate(PL):
    cfgs[p['arm']].append(MT.mask_hex(p['mask']))
arm_masks = {a: sorted(set(v)) for a, v in cfgs.items()}
fvec = {(PL[j]['arm'], MT.mask_hex(PL[j]['mask'])): X['laggard'][j] for j in range(len(PL))}
pl_scores, beaten = [], 0
t1 = time.time()
for d in range(NDRAW):
    rng = np.random.default_rng(20261121 + d)
    mp = {}
    for a in sorted(arm_masks):
        ms = arm_masks[a]
        perm = rng.permutation(len(ms))
        for k, m in enumerate(ms):
            mp[(a, m)] = ms[perm[k]]
    Xp = np.array([fvec[(PL[j]['arm'], mp[(PL[j]['arm'], MT.mask_hex(PL[j]['mask']))])] for j in range(len(PL))])
    hp, _ = run_folds(Xp, kinds=('LOMO',))
    s = rms(hp['LOMO'], LEAD)[0]
    pl_scores.append(s)
    beaten += (t_K1 < s)
    if (d + 1) % 10 == 0:
        say(f'placebo {d + 1}/{NDRAW}: beaten {beaten}; last {s:.3f}% ({time.time() - t1:.0f} s)')
K4 = beaten >= 95 if NDRAW == 100 else None
KEPT = bool(K1 and all(K2.values()) and K3 and K4)
say(f'K4 placebo beaten {beaten}/{NDRAW}: {K4}; VERDICT {"KEPT" if KEPT else "NOT KEPT (rejected candidate)"}')

# ------------------------------------------------------------------ 5. REPORTED controls (never deciding)
rep = {}
for name, Xv, fixed in (('chip shares (hop of the active mean)', X['chip'], None), ('fully associative LRU (FA)', X['fa'], None),
                        ('the form with the hop of the active mean', X['mean_hop'], None),
                        ('sets only (a_hop = 0)', X['laggard'], {'a_hop': 0.0}), ('hop only (a_set = 0)', X['laggard'], {'a_set': 0.0})):
    a, c, _ = fit_idx('all-data', Xv, np.arange(len(IL)), fixed)
    hl, _ = run_folds(Xv, kinds=('LOMO',), fixed=fixed)
    rep[name] = {'all_data_constants': a, 'LOMO lead E221 MASK no-twin rms': rms(hl['LOMO'], LEAD),
                 'LOMO MASK all no-twin (LOMO masks)': rms(hl['LOMO'], MASK & ~twx & (lomo_cover | ~lay))}
    say(f'REPORTED {name}: a {a}; LOMO lead {rep[name]["LOMO lead E221 MASK no-twin rms"]}')

# posimb beside (REPORTED): E221's committed case table carries MM1-v3.2 + posimb's frozen, blind wall error per case (v32p_e_wall); the
# mesh term's are held out (LOMO, post hoc). Per placement family and shire-count bucket: rms of each, and the cases each brings closer to
# the measured wall than MM1-v3.2 by more than 1 point
CASE = {r['case']: r for r in csv.DictReader(open(os.path.join(MT.V31, 'blind-e221-scores', 'cases', 'scores-blind-e221-cases.csv')))}
cmp_rows = collections.defaultdict(lambda: {'n': 0, 'v32': [], 'posimb': [], 'mesh': [], 'posimb_closer': 0, 'mesh_closer': 0, 'both_closer': 0})


def bucket(n):
    return '1' if n == 1 else ('2-3' if n <= 3 else ('4-7' if n <= 7 else ('8-15' if n <= 15 else ('16-31' if n <= 31 else '32'))))


for i, p in enumerate(P):
    if not LEAD[i] or not lay[i]:
        continue
    c = CASE[p['id'].split('|', 2)[2]]
    ev = T0['all-data'][i] / Tm[i] - 1.0
    em = HO['LOMO'][i] / Tm[i] - 1.0
    ep = float(c['v32p_e_wall']) if c['v32p_e_wall'] not in ('', None) else None
    for key in (f"family {p.get('subfamily')}", f'shires {bucket(p["n_shires"])}', 'all subset cases of the lead'):
        d = cmp_rows[key]
        d['n'] += 1
        d['v32'].append(ev)
        d['mesh'].append(em)
        if ep is not None:
            d['posimb'].append(ep)
            pc = abs(ep) < abs(ev) - 0.01
            mc = abs(em) < abs(ev) - 0.01
            d['posimb_closer'] += pc
            d['mesh_closer'] += mc
            d['both_closer'] += pc and mc


def r_(v):
    return float(100 * math.sqrt(np.mean(np.square(v)))) if v else None


posimb_cmp = {k: {'n': d['n'], 'rms_MM1-v3.2': r_(d['v32']), 'rms_posimb_blind': r_(d['posimb']), 'rms_mesh_LOMO': r_(d['mesh']),
                  'posimb_closer_by_1pt': d['posimb_closer'], 'mesh_closer_by_1pt': d['mesh_closer'], 'both': d['both_closer']}
              for k, d in sorted(cmp_rows.items())}
for k, v in posimb_cmp.items():
    say(f'posimb beside | {k}: n {v["n"]} rms v3.2 {v["rms_MM1-v3.2"]:.2f} posimb {v["rms_posimb_blind"]} mesh {v["rms_mesh_LOMO"]:.2f}; '
        f'closer by 1 pt: posimb {v["posimb_closer_by_1pt"]}, mesh {v["mesh_closer_by_1pt"]}, both {v["both"]}')
rep['posimb_beside_on_the_lead'] = posimb_cmp

# per-point records for the lead (E221) and every MASK point
rows = []
for i, p in enumerate(P):
    if not (p['MASK'] or p['layout_point']):
        continue
    j = LPOS.get(i)
    xv = X['laggard'][j].tolist() if j is not None else [0, 0, 0, 0]
    rows.append({'id': p['id'], 'exp': p['exp'], 'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p.get('kind'), 'mask': maskh[i],
                 'n_shires': p['n_shires'], 'MASK': bool(p['MASK']), 'layout_point': bool(p['layout_point']), 'twin_x': bool(p['twin_x']),
                 'twin_v32': p.get('twin_v32'), 'lead': bool(LEAD[i]), 'subfamily': p.get('subfamily'), 'session': p.get('session'),
                 'T_meas_us': Tm[i], 'f_mhz': p['f'], 'v32_all': float(T0['all-data'][i]), 'mesh_in_sample': float(T_ins[i]),
                 **{f'v32_{k}': float(BASE[k][i]) for k in ('LOEO', 'LOCO')}, **{f'mesh_{k}': float(HO[k][i]) for k in ('LOMO', 'LOSO', 'LOEO', 'LOCO')},
                 'dA': xv[0], 'dB': xv[1], 'g3': xv[2], 'gF': xv[3]})
fitrec = {'what': "mask-mesh: 'MM1-v3.2 + mesh' fitted by its declaration (DECLARED-mesh.md)", 'declared_sha256': DECL_SHA,
          'started': T_START, 'ended': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'python': sys.version.split()[0], 'numpy': np.__version__,
          'base': 'MM1-v3.2 (tools/matmul/mm1/v3.2, model 4e386f75) at its all-data constants, unchanged', 'form': FORM,
          'n_points': N, 'n_scope': int(len(IL)), 'constants': {'a_set': a_all[0], 'a_hop': a_all[1]}, 'cost': c_all, 'ends': ends_all,
          'bounds': MT.BOUNDS, 'starts': STARTS, 'variant': 'laggard'}
hold = {'table': table, 'keep_rule': {'K1': {'MM1-v3.2': v32_K1, 'mesh': t_K1, 'margin_points': 1.0, 'pass': bool(K1)},
                                      'K2': {k: bool(v) for k, v in K2.items()}, 'K3': {'MM1-v3.2': g_b, 'mesh': g_t, 'allowed_points': 0.05, 'pass': bool(K3)},
                                      'K4': {'beaten': beaten, 'draws': NDRAW, 'pass': K4}, 'verdict': 'KEPT' if KEPT else 'NOT KEPT (rejected candidate)'},
        'fold_constants': {k: v for k, v in CS.items()}, 'lomo_masks': HO['LOMO_masks'],
        'placebo': {'scores_pct': pl_scores, 'seed_base': 20261121, 'how': 'within each arm, the subset masks\' feature vectors (dA, dB, g3, gF) permuted by numpy.random.default_rng(20261121 + draw).permutation over the arm\'s sorted masks; LOMO refitted; the lead\'s rms'},
        'reported_controls': rep}
json.dump(fitrec, open(os.path.join(OUTD, 'fit-mesh.json'), 'w'), indent=1)
json.dump(hold, open(os.path.join(OUTD, 'holdout-mesh.json'), 'w'), indent=1)
json.dump({'rows': rows}, open(os.path.join(OUTD, 'points-scored-mesh.json'), 'w'), indent=0)
json.dump({'model': 'MM1-v3.2 + mesh', 'variant': 'laggard', 'constants': {'a_set': a_all[0], 'a_hop': a_all[1]}, 'base_params': 'tools/matmul/mm1/v3.2/out/mm1_v32_params.json',
           'base_params_sha256': hashlib.sha256(open(os.path.join(V32, 'out', 'mm1_v32_params.json'), 'rb').read()).hexdigest(),
           'verdict': 'KEPT' if KEPT else 'NOT KEPT (rejected candidate)'}, open(os.path.join(OUTD, 'params-mesh.json'), 'w'), indent=1)
say('m03 done', time.strftime('%Y-%m-%d %H:%M:%S %Z'))
