#!/usr/bin/env python3
"""lnc-form step 3: freeze 'MM1-v3.2 + gemmLnc term AF4' (the form chosen by DECLARED-lnc-form.md's rule in s02_fit.py) for every E220 point on
both arms (OUT/reg-e220/POINTS-e220.json, FINAL 05:24:17 PST; tokens, cards and clocks only: no E220 datum exists or is opened), with every
other declared form's W and J beside (REPORTED). Desk; numpy; single-threaded inside the round's CPU slots.

The call (E220's, as POINTS.txt states it): card = the arm's card, arm = token, fmt, kind = random, mask, f = the arm's clock (A 600.0 MHz;
B 799.0 MHz with 700.0 and 600.0 MHz columns), kernel = rgm136; V, G, t0_c, minions, ops not given (MM1-v3.2's defaults: the card's volts at
f, the governed base at f, a 50 C die). F3 is removed and the form's term added at MM1-v3.2's own op time; both scale as 1 / t_op, so the
affine form for W over idle at a measured op time t is W(t) = A + B' / t with B' = B - F3 t_op + dW t_op."""
import csv
import hashlib
import json
import os
import sys
import time

import numpy as np

L = os.environ['LNC_FORM_DIR']
REPO = os.path.join(L, 'work', 'repo')
V32 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2')
REG = os.environ['E220_REG_DIR']
sys.path.insert(0, V32)
import mm1_v32  # noqa: E402

sys.path.insert(0, os.path.join(L, 'scripts'))
FIT = json.load(open(os.path.join(L, 'work', 's02_fit.json')))
CHOICE = FIT['choice']['form']
assert CHOICE == 'AF4' and FIT['choice']['status'] == 'KEPT', FIT['choice']

PARAMS = os.path.join(V32, 'out', 'mm1_v32_params.json')
P = json.load(open(PARAMS))
M = mm1_v32.Model(P)
C1V, C2V = P['energy']['F3']['c1_pJ'], P['energy']['F3']['c2_pJ']

# the features, exactly as s02_fit.py's feats() (DECLARED section 2), imported from that file's text to keep one definition
src = open(os.path.join(L, 'scripts', 's02_fit.py')).read()
start = src.index('def feats(')
end = src.index('FORMS = {')
ns = {'np': np, 'C': mm1_v32.C, 'X1': float(P['time']['theta']['x1'])}
sys.path.insert(0, os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3'))
import mm1_core_v3 as CORE  # noqa: E402
ns['C'] = CORE
exec(src[start:end], ns)
feats = ns['feats']
FORMS = {'F3r': ['dup', 'first'], 'F1r': ['dup'], 'F2r': ['dup', 'beyond'], 'F4r': ['beyond'], 'STEPr': ['dup', 'stepNB3'],
         'AF1': ['dup', 'R1'], 'AF2': ['dup', 'R2'], 'AF3': ['dup', 'R3'], 'AF4': ['dup', 'R4']}
CONST = {f: FIT['forms'][f]['constants_all_data_pJ'] for f in FORMS}

J = json.load(open(os.path.join(REG, 'POINTS-e220.json')))
POINTS_TXT_SHA = hashlib.sha256(open(os.path.join(REG, 'POINTS.txt'), 'rb').read()).hexdigest()
POINTS_CSV_SHA = hashlib.sha256(open(os.path.join(REG, 'POINTS-e220.csv'), 'rb').read()).hexdigest()
POINTS_JSON_SHA = hashlib.sha256(open(os.path.join(REG, 'POINTS-e220.json'), 'rb').read()).hexdigest()
assert POINTS_CSV_SHA == '64a7c99a90a2d899db44dc0c3790dfd840cd02b49c9d12f24396f4691125afc4', POINTS_CSV_SHA
assert POINTS_JSON_SHA == '2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28', POINTS_JSON_SHA

CLOCKS = {'A': [600.0], 'B': [799.0, 700.0, 600.0]}
EPS_G = float(J['eps_G'])                       # E220's drop-line form: MM1-v3.2's held-out gemmLnc W error (POINT-RULE-e220.md)
STOP = {'A': J['arms']['A']['drop_line_W'] + 3.0, 'B': J['arms']['B']['drop_line_W'] + 3.0}   # the board stops (drop line + 3 W)
specs, meta = [], []
for arm in ('A', 'B'):
    for p in J['points'][arm]:
        for f in CLOCKS[arm]:
            specs.append({'card': p['card'], 'arm': p['token'], 'fmt': p['format'], 'kind': 'random', 'mask': p['shire_mask'], 'f': f,
                          'kernel': 'rgm136'})
            meta.append((arm, p, f))
t0 = time.time()
pr = M.predict_many(specs)
rows = []
for (arm, p, f), o in zip(meta, pr):
    lnc = p['token'].startswith('gemmLnc')
    A_, B_ = o['W_affine']['A_W'], o['W_affine']['B_W_us']
    t = o['T_op_us']
    Wv = A_ + B_ / t
    f3 = o['F3_W_at_own_t']
    rl = o.get('rest_law') or {}
    sec = o['seconds_per_gemm']
    r = {'arm': arm, 'card': p['card'], 'f_mhz': f, 'id': p['id'], 'family': p['family'], 'subfamily': p['subfamily'], 'token': p['token'],
         'format': p['format'], 'kind': 'random', 'shire_mask': p['shire_mask'], 'loop': p['loop'], 'ops_per_minion_per_gemm': p['ops_per_minion_per_gemm'],
         'cycles_per_op_wall': o['cycles_per_op_wall'], 'cycles_per_op_mean': o['cycles_per_op_mean'], 'T_op_us': t, 'seconds_per_gemm': sec,
         'MM1-v3.2_W_over_idle': Wv, 'MM1-v3.2_F3_W': f3, 'rest_law_W': rl.get('P_rest_W'), 'rest_T0_c': rl.get('T0_c'),
         'PP32_registered': p.get('PP32_W')}
    if lnc:
        assert abs(o['F3_dup'] - 26.0) < 1e-12
        S_own = f3 / (C1V * 26.0 + C2V * o['F3_first'])
        Q = 0.5 * (np.array(o['Q0']) + np.array(o['Q1']))
        ft = feats(tuple(int(x) for x in p['shape']), p['format'], Q.sum(axis=1).tolist(), Q.sum(axis=0).tolist(), p['shire_mask'])
        r['features'] = {k: ft[k] for k in ('dup', 'beyond', 'first', 'qA_b', 'qBF', 'phi', 'm', 'a_f', 'a3', 'Lres', 'R1', 'R2', 'R3', 'R4',
                                            'stepNB3', 'footprint_MB')}
        r['S_W_per_pJ_minion_op'] = S_own
        r['forms_W_REPORTED'] = {}
        for fm, cols in FORMS.items():
            E = float(np.dot(CONST[fm], [ft[c] for c in cols]))
            r['forms_W_REPORTED'][fm] = {'E_pJ_per_minion_op': E, 'term_W': S_own * E, 'W_over_idle': Wv - f3 + S_own * E,
                                         'J_over_idle_per_gemm': (Wv - f3 + S_own * E) * sec}
        E4 = r['forms_W_REPORTED']['AF4']['E_pJ_per_minion_op']
        dW = S_own * E4
    else:
        assert f3 == 0.0, (p['id'], f3)
        S_own, dW, E4 = None, 0.0, 0.0
    Wn = Wv - f3 + dW
    Bn = B_ - f3 * t + dW * t
    r.update({'term_AF4_E_pJ_per_minion_op': E4, 'term_AF4_W': dW, 'W_over_idle': Wn, 'A_W': A_, 'B_W_us': Bn,
              'J_over_idle_per_gemm_t_forecast': Wn * sec,
              'J_at_rest_per_gemm_t_forecast': ((rl['P_rest_W'] + Wn) * sec) if rl else None,
              'PP_with_term_W': ((rl['P_rest_W'] + Wn + 2.0) if rl else None),
              'PP_with_term_E220_form_W': ((rl['P_rest_W'] + Wn * ((1.0 + 2.0 * EPS_G) if lnc else 1.0) + 2.0) if rl else None),
              'board_stop_W': STOP[arm],
              'PP32_check': ((rl['P_rest_W'] + Wv * ((1.0 + 2.0 * EPS_G) if lnc else 1.0) + 2.0 - p['PP32_W'])
                             if (rl and p.get('PP32_W') is not None and f == p['f_mhz']) else None)})
    rows.append(r)

stamp = time.strftime('%Y-%m-%d %H:%M:%S %Z')
OUTD = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'gemmlnc-af4')
os.makedirs(OUTD, exist_ok=True)
term = {'name': 'gemmLnc term AF4', 'model': "MM1-v3.2 + gemmLnc term AF4 (replaces F3)",
        'equation': 'dW = D x sL x (n / t_op) x 1e-12 x (c1 x dup + c2 x R4) [W over idle]; R4 = Lres x beyond + (1 - Lres) x a3 x (14 qA_b + 12 qBF)',
        'features': {'dup': '26 at rgm136 gemmLnc, 0 at every cooperative loop',
                     'beyond': '14 (1 - qA_L2) + 12 (1 - qB_L2), the map Q = (Q0 + Q1) / 2 of MM1-v3.2 at its all-data constants',
                     'qA_b': '1 - qA_L2', 'qBF': "B's fresh share of Q",
                     'phi': '1 if MB = 1 else (NB - 1) / NB', 'm': '1 if 2 KB sa + KB sb > x1 (37.334 MB, MM1-v3.2 time theta x1) else 0',
                     'a3': '1 if NB = 1 or m = 1; else (1 - phi) if NB = 2; else 0',
                     'Lres': "1 if MM1's footprint(MB, NB, KB, mask) <= x1 else 0",
                     'D, sL, n, t_op': "F3's: D = 1 + 0.0048 (die - 50 C), sL = 1 + xi (s_V - 1) at MM1-v3.2's xi, n minions, t_op the op time"},
        'constants_pJ_per_line': {'c1': CONST['AF4'][0], 'c2': CONST['AF4'][1]}, 'bounds_pJ': [0.0, 10000.0],
        'fit': 'relative least squares of W over idle given the measured op time on the 36 committed gemmLnc points E211-E218 (bvls)',
        'held_out': {k: FIT['forms']['AF4'][k] for k in ('in_sample', 'LOEO', 'LOCO', 'LOPO', 'LOEO_by_fold', 'LOCO_by_fold')},
        'comparator_F3r': {k: FIT['forms']['F3r'][k] for k in ('constants_all_data_pJ', 'in_sample', 'LOEO', 'LOCO', 'LOPO')},
        'keep_rule': FIT['keep_rule']['AF4'], 'placebo': FIT['placebo']['AF4'], 'pooled_guard': FIT['pooled_guard']['forms']['AF4'],
        'pooled_guard_MM1-v3.2': FIT['pooled_guard']['MM1-v3.2'], 'declaration': 'DECLARED-lnc-form.md sha256 7e1c01e4eaf758263d35778ba8c5ffb35ba21362ede5d3f9f85b2272cae0b414 (hashed 2026-11-20 05:30:58 PST)',
        'base': 'MM1-v3.2 frozen (tools/matmul/mm1/v3.2/out/mm1_v32_params.json, sha256 %s), F3 removed, no other constant changed' % hashlib.sha256(open(PARAMS, 'rb').read()).hexdigest(),
        'labels': 'every constant post hoc; the form post hoc in design (DECLARED section 0); E220 forecasts blind once their sha256 is posted or pushed before E220 first card command'}
json.dump(term, open(os.path.join(OUTD, 'term-gemmlnc-af4.json'), 'w'), indent=1)
cols = ['arm', 'card', 'f_mhz', 'id', 'family', 'subfamily', 'token', 'format', 'kind', 'shire_mask', 'loop', 'ops_per_minion_per_gemm',
        'cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us',
        'J_over_idle_per_gemm_t_forecast', 'rest_law_W', 'rest_T0_c', 'J_at_rest_per_gemm_t_forecast', 'term_AF4_E_pJ_per_minion_op',
        'term_AF4_W', 'MM1-v3.2_W_over_idle', 'MM1-v3.2_F3_W', 'PP_with_term_W', 'PP_with_term_E220_form_W', 'board_stop_W', 'PP32_registered']
with open(os.path.join(OUTD, 'forecasts-e220-af4.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for r in rows:
        w.writerow([('%.10g' % r[c]) if isinstance(r[c], float) else ('' if r[c] is None else r[c]) for c in cols])
json.dump({'what': "E220's forecasts by 'MM1-v3.2 + gemmLnc term AF4' (the form kept by DECLARED-lnc-form.md's rule), every point of both "
                   "arms; every other declared form's W and J at the gemmLnc points beside (REPORTED); cooperative points equal MM1-v3.2",
           'how_given_t': "W over idle at a measured op time t (us, the slowest minion: T_op = t_gemm x 1e6 / ops) = A_W + B_W_us / t; J over idle "
                          "given t = that W x the measured seconds a GEMM; J at rest = (the measured or law rest + W) x seconds",
           'call': specs[0] | {'note': 'per point: card, token, format, kind random, mask, f, kernel rgm136; V, G, t0_c, minions, ops not given'},
           'points_files_sha256': {'POINTS.txt': POINTS_TXT_SHA, 'POINTS-e220.csv': POINTS_CSV_SHA, 'POINTS-e220.json': POINTS_JSON_SHA},
           'params_sha256': hashlib.sha256(open(PARAMS, 'rb').read()).hexdigest(), 'term': 'term-gemmlnc-af4.json', 'constants': CONST,
           'made': stamp, 'rows': rows}, open(os.path.join(OUTD, 'forecasts-e220-af4.json'), 'w'), indent=1)
chk = [r['PP32_check'] for r in rows if r['PP32_check'] is not None]
print('rows', len(rows), 'made', stamp, 'secs', round(time.time() - t0, 1), 'PP32 check max |diff|', max(abs(x) for x in chk), 'n', len(chk))
print('drop lines / stops', {a: J['arms'][a]['drop_line_W'] for a in 'AB'}, STOP, 'eps_G', EPS_G)
print('%-2s %-6s %-6s %-15s %7s %7s %7s %7s %7s %7s %7s %6s %6s' % ('ar', 'f', 'id', 'token', 'W_v32', 'F3', 'AF4', 'W_new', 'PPnew', 'PPnewE', 'PP32', 'R4', 'F3r_W'))
for r in rows:
    if r['token'].startswith('gemmLnc'):
        print('%-2s %6.0f %-6s %-15s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %6.1f %6.2f' % (
            r['arm'], r['f_mhz'], r['id'], r['token'], r['MM1-v3.2_W_over_idle'], r['MM1-v3.2_F3_W'], r['term_AF4_W'], r['W_over_idle'],
            r['PP_with_term_W'], r['PP_with_term_E220_form_W'], r['PP32_registered'] or float('nan'), r['features']['R4'],
            r['forms_W_REPORTED']['F3r']['W_over_idle']))
coop = [r for r in rows if not r['token'].startswith('gemmLnc')]
print('cooperative rows', len(coop), 'term 0 at all:', all(r['term_AF4_W'] == 0.0 and r['W_over_idle'] == r['MM1-v3.2_W_over_idle'] for r in coop))
print('highest PP with term (plain / E220 form) by arm at the registered clock:',
      {a: (max(r['PP_with_term_W'] for r in rows if r['arm'] == a and r['f_mhz'] == CLOCKS[a][0]),
           max(r['PP_with_term_E220_form_W'] for r in rows if r['arm'] == a and r['f_mhz'] == CLOCKS[a][0])) for a in 'AB'})
