#!/usr/bin/env python3
"""lnc-energy step 3 (desk, POST HOC): the gemmLnc term, fitted on the residuals of MM1-v3.1's frozen predictor (in-sample W over idle given the
measured op time, MM1-v3.1's own records points_energy_v31.csv) at the 9 committed gemmLnc energy points (E211 c01c, c02c; E213 arm A a075,
a079, a082, a086, a087; arm B k37, k40). Every candidate form has at most two constants; each is linear in them:

    dW = D * sL * rate * 1e-12 * (c1 * x1 + c2 * x2)        (watts; c in pJ a line; rate = minions / t_op; D, sL MM1-v3.1's die and
                                                             line-voltage factors, exactly as it applies them to its line energies)
  x per minion-op, from the kernels' sources and the walk (s03_walk.json) and MM1-v3.1's own line map (s01_points.json):
    dup     = 26: the duplicate line reads a minion-op the non-cooperative branch adds (a shire-op: 32 + 32 tile reads of 16 lines against the
              cooperative 4 + 8, 1,024 - 192 = 832 lines; 448 of A, 384 of B); 0 for every cooperative loop
    beyond  = 14 qA_b + 12 qB_b: the duplicates of the lines MM1-v3.1's map serves beyond the L2 (qA_b, qB_b the A and B shares at L3 or
              fresh: 1 - Q's L2 marginal), i.e. the duplicates that must cross the NoC if the L2 does not merge them
    first   = beyond / NB: the same on the A panel's first C block of its row of blocks (one in NB)
  forms:
    F1  c1 dup                       one constant: an energy a duplicate L2 read
    F2  c1 dup + c2 beyond           two: the L2 read, and a NoC re-fetch of every duplicate of a line from beyond the L2
    F3  c1 dup + c2 first            two: the L2 read, and the NoC re-fetch on the A panel's first use (1 in NB C blocks)
    F4  c1 beyond                    one: the NoC re-fetch only
Folds: in sample; leave one point out (LOPO); leave one run out (LORO: one run's W from the committed sessions, s02_rails_runs.json, the
point's mean re-made from its other runs); leave one experiment out (E211 / E213); leave one card out (aifoundry1 card 1 / aifoundry3).
Declared selection (written before the fits ran; post hoc as all of this is): the form with the lowest LOPO rms of W over idle in %, a
two-constant form only if it beats the best one-constant form by at least 1 point; LOEO and LORO reported beside. The term is identically 0
on every cooperative loop (dup = beyond = first = 0): shown by the twins' table. /usr/bin/python3 3.12.3, numpy."""
import json
import os
import sys

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
WK = os.environ.get('LNC_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
sys.path.insert(0, V31)
import data_v31  # noqa: E402

P = json.load(open(os.path.join(V31, 'out/mm1_v31_params.json')))
TH = P['energy']['theta']
LAM = 0.0048          # energy_v3.LAM (MM1-v3's die factor slope), as MM1-v3.1 imports it
XI = TH['xi']

pts = json.load(open(os.path.join(WK, 's01_points.json')))
walk = {r['shape']: r for r in json.load(open(os.path.join(WK, 's03_walk.json')))['rows']}
runs = json.load(open(os.path.join(WK, 's02_rails_runs.json')))
EP = {e['id']: e for e in data_v31.energy_points()}

EXPKEY = {'E211': 'E211', 'E213|a3': 'E213A', 'E213|c1': 'E213B'}


def shape_of(arm):
    import re
    m = re.search(r'(\d+)x(\d+)x(\d+)$', arm)
    return tuple(int(x) for x in m.groups())


def feats(x):
    MB, NB, KB = shape_of(x['arm'])
    qA, qB = x['qA_L2_L3_F'], x['qB_L2_L3_F']
    lnc = x['arm'].startswith('gemmLnc')
    dup = 26.0 if lnc else 0.0
    beyond = (14.0 * (1.0 - qA[0]) + 12.0 * (1.0 - qB[0])) if lnc else 0.0
    return {'dup': dup, 'beyond': beyond, 'first': beyond / NB, 'MB': MB, 'NB': NB, 'KB': KB}


FORMS = {'F1': ('dup', None), 'F2': ('dup', 'beyond'), 'F3': ('dup', 'first'), 'F4': ('beyond', None)}

L = []
for x in pts:
    e = EP[x['id']]
    T0 = e['die_start'] if e.get('die_start') is not None else 50.0
    D = 1.0 + LAM * (T0 - 50.0)
    sL = 1.0 + XI * (e['s'] - 1.0)
    rate = e['minions'] / (e['T'] * 1e-6)
    f = feats(x)
    key = EXPKEY['E211' if x['exp'] == 'E211' else x['id'][:7]]
    rid = x['id'].split('|')[-1]
    rr = [r for r in runs if r['exp'] == key and r['id'] == rid]
    L.append(dict(x, **f, D=D, sL=sL, rate_fit=rate, T_us=e['T'], die_start=T0, s=e['s'], w_point=e['w'], key=key, rid=rid,
                  run_w=[r['board_over_idle'] for r in rr], run_names=[r['run'] for r in rr]))

LNC = [p for p in L if p['role'] == 'gemmLnc']
TW = [p for p in L if p['role'] == 'twin']


def z(p, name):
    return 0.0 if name is None else p['D'] * p['sL'] * p['rate_fit'] * 1e-12 * p[name]


def fit(train, form, wts=None):
    a, b = FORMS[form]
    Z = np.array([[z(p, a)] + ([z(p, b)] if b else []) for p in train])
    y = np.array([p['w_meas'] - p['W_v31_csv_in'] for p in train])
    c, *_ = np.linalg.lstsq(Z, y, rcond=None)
    return c


def pred(p, form, c):
    a, b = FORMS[form]
    return p['W_v31_csv_in'] + c[0] * z(p, a) + (c[1] * z(p, b) if b else 0.0)


def rms(v):
    v = np.asarray(v, float)
    return float(np.sqrt(np.mean(v * v))) if len(v) else float('nan')


out = {'n_points': len(LNC), 'points': [], 'forms': {}, 'twins': []}
base = [(p['W_v31_csv_in'] - p['w_meas']) / p['w_meas'] * 100 for p in LNC]
out['v31_alone'] = {'rms_pct': rms(base), 'mean_pct': float(np.mean(base)), 'rms_W': rms([p['W_v31_csv_in'] - p['w_meas'] for p in LNC])}

for form in FORMS:
    c = fit(LNC, form)
    ins = [(pred(p, form, c) - p['w_meas']) / p['w_meas'] * 100 for p in LNC]
    # LOPO
    lopo = []
    for i, p in enumerate(LNC):
        cc = fit([q for j, q in enumerate(LNC) if j != i], form)
        lopo.append((pred(p, form, cc) - p['w_meas']) / p['w_meas'] * 100)
    # LORO: one run out; its point's mean re-made from its other runs (if any)
    loro = []
    for i, p in enumerate(LNC):
        for k, wr in enumerate(p['run_w']):
            tr = []
            for j, q in enumerate(LNC):
                if j != i:
                    tr.append(q)
                elif len(p['run_w']) > 1:
                    others = [w for kk, w in enumerate(p['run_w']) if kk != k]
                    tr.append(dict(q, w_meas=float(np.mean(others))))
            cc = fit(tr, form)
            loro.append((pred(p, form, cc) - wr) / wr * 100)
    # LOEO and LOCO
    folds = {'LOEO E211 out': lambda p: p['exp'] == 'E211', 'LOEO E213 out': lambda p: p['exp'] == 'E213',
             'LOEO-arm E213 arm A out': lambda p: p['exp'] == 'E213' and p['card'] == 'aifoundry3 card 0',
             'LOCO aifoundry1 card 1 out (= LOEO-arm E213 arm B out)': lambda p: p['card'] == 'aifoundry1 card 1',
             'LOCO aifoundry3 card 0 out': lambda p: p['card'] == 'aifoundry3 card 0'}
    fo = {}
    loeo_all = []
    for fname, test in folds.items():
        tr = [p for p in LNC if not test(p)]
        te = [p for p in LNC if test(p)]
        if len(tr) < len([v for v in FORMS[form] if v]):
            fo[fname] = 'NOT IDENTIFIED (fewer training points than constants)'
            continue
        cc = fit(tr, form)
        ee = [(pred(p, form, cc) - p['w_meas']) / p['w_meas'] * 100 for p in te]
        fo[fname] = {'constants_pJ_per_line': [float(v) for v in cc], 'test': [p['id'] for p in te], 'err_pct': [round(v, 3) for v in ee],
                     'rms_pct': rms(ee)}
        if fname in ('LOEO E211 out', 'LOEO E213 out'):
            loeo_all += ee
        # identification: a two-constant fit is identified only if its training set holds an L2-resident point (first = 0 with dup > 0)
        # and a point with first > 0; otherwise the two columns are near-collinear
        if FORMS[form][1] is not None:
            fo[fname]['identified'] = bool(any(q['first'] == 0 and q['dup'] > 0 for q in tr) and any(q['first'] > 0 for q in tr)) \
                if FORMS[form][1] == 'first' else bool(any(q['beyond'] == 0 and q['dup'] > 0 for q in tr) and any(q['beyond'] > 0 for q in tr))
    out['forms'][form] = {'x': FORMS[form], 'constants_pJ_per_line': [float(v) for v in c], 'in_sample_rms_pct': rms(ins),
                          'in_sample_err_pct': [round(v, 3) for v in ins], 'LOPO_rms_pct': rms(lopo), 'LOPO_err_pct': [round(v, 3) for v in lopo],
                          'LORO_rms_pct': rms(loro), 'LORO_n_runs': len(loro), 'LOEO_pooled_rms_pct': rms(loeo_all), 'folds': fo}

# declared selection
one = [f for f in FORMS if FORMS[f][1] is None]
two = [f for f in FORMS if FORMS[f][1] is not None]
best1 = min(one, key=lambda f: out['forms'][f]['LOPO_rms_pct'])
best2 = min(two, key=lambda f: out['forms'][f]['LOPO_rms_pct'])
chosen = best2 if out['forms'][best2]['LOPO_rms_pct'] <= out['forms'][best1]['LOPO_rms_pct'] - 1.0 else best1
out['selection'] = {'rule': 'lowest LOPO rms % of W over idle; a two-constant form only if >= 1 point better than the best one-constant form',
                    'best_one_constant': best1, 'best_two_constant': best2, 'chosen': chosen}

for p in LNC:
    out['points'].append({k: p[k] for k in ('id', 'exp', 'arm', 'fmt', 'card', 'w_meas', 'W_v31_csv_in', 'cyc_meas', 'dup', 'beyond', 'first', 'NB',
                                             'D', 'sL', 'rate_fit', 'run_w', 'run_names')})
for p in TW:
    out['twins'].append({'id': p['id'], 'arm': p['arm'], 'fmt': p['fmt'], 'card': p['card'], 'w_meas': p['w_meas'], 'W_v31_csv_in': p['W_v31_csv_in'],
                         'ratio_meas_over_v31': p['w_meas'] / p['W_v31_csv_in'], 'term_W': 0.0,
                         'why_zero': 'cooperative loop: dup = beyond = first = 0 (one read a coop group)'})

json.dump(out, open(os.path.join(WK, 's04_fit.json'), 'w'), indent=1)
print('v3.1 alone on the 9 gemmLnc points: rms %.2f%%, mean %.2f%%, rms %.2f W' % (out['v31_alone']['rms_pct'], out['v31_alone']['mean_pct'],
                                                                                 out['v31_alone']['rms_W']))
for f, r in out['forms'].items():
    print('%s x=%s c=%s pJ/line | in %.2f%% | LOPO %.2f%% | LORO %.2f%% (n %d) | LOEO pooled %.2f%%' % (
        f, r['x'], ['%.1f' % v for v in r['constants_pJ_per_line']], r['in_sample_rms_pct'], r['LOPO_rms_pct'], r['LORO_rms_pct'], r['LORO_n_runs'],
        r['LOEO_pooled_rms_pct']))
    print('    in-sample err %%: %s' % r['in_sample_err_pct'])
    print('    LOPO err %%:      %s' % r['LOPO_err_pct'])
    for fn, fv in r['folds'].items():
        print('    %-28s %s' % (fn, fv if isinstance(fv, str) else 'c=%s rms %.2f%% err %s' % (['%.1f' % v for v in fv['constants_pJ_per_line']],
                                                                                              fv['rms_pct'], fv['err_pct'])))
print('selection:', out['selection'])
print('points:', [(p['id'], p['NB'], round(p['beyond'], 2), round(p['first'], 2)) for p in LNC])
print('twins (term 0):', [(t['id'], round(t['ratio_meas_over_v31'], 3)) for t in out['twins']])
