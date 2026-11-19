#!/usr/bin/env python3
"""lnc-energy step 4: 'MM1-v3.1 + gemmLnc term' forecasts for every E215 gemmLnc point (arm A a024, a026, a031, a032 on aifoundry3 card 0;
arm B b013 on aifoundry1 card 1), from MM1-v3.1's frozen predictor (2c971828, its registered call: mm1_v31.Model(out/mm1_v31_params.json)
.predict_many([{card, arm, fmt, kind, mask, f: 600.0, kernel}])) plus the term chosen by s04_fit.py's declared rule; the two gemmLnc smoke
processes (s03 arm A, s14 arm B, gemmLnc2x2x2 fp32) beside as safety rows (REPORTED: a smoke is not a scored point). Reads E215's registration
(points-e215.csv: the points' tokens) and MM1-v3.1's own frozen E215 forecasts (to check the predictor reproduces them); NEVER an E215 datum.
Also the held-out check of the term on E213's two gemmLnc smokes (committed, never fitted; their rest estimated, REPORTED).
Outputs (new files): forecasts-gemmlnc-e215.csv, forecasts-gemmlnc-e215.json, term-gemmlnc.json. /usr/bin/python3 3.12.3, numpy."""
import csv
import datetime
import hashlib
import json
import os
import sys

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
WK = os.environ.get('LNC_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
OUTD = os.environ.get('LNC_OUT') or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, V31)
import mm1_v31  # noqa: E402

P = json.load(open(os.path.join(V31, 'out/mm1_v31_params.json')))
M = mm1_v31.Model(P)
XI = P['energy']['theta']['xi']
LAM = 0.0048
FIT = json.load(open(os.path.join(WK, 's04_fit.json')))
CHOSEN = FIT['selection']['chosen']
FORMS = {'F1': ('dup', None), 'F2': ('dup', 'beyond'), 'F3': ('dup', 'first'), 'F4': ('beyond', None)}
STOP = {'A': 70.0, 'B': 72.0}
CARD = {'A': 'aifoundry3 card 0', 'B': 'aifoundry1 card 1'}


def shape(arm):
    import re
    return tuple(int(x) for x in re.search(r'(\d+)x(\d+)x(\d+)$', arm).groups())


def feats(arm, Q):
    MB, NB, KB = shape(arm)
    qA, qB = Q.sum(axis=1), Q.sum(axis=0)
    lnc = arm.startswith('gemmLnc')
    dup = 26.0 if lnc else 0.0
    beyond = (14.0 * (1.0 - qA[0]) + 12.0 * (1.0 - qB[0])) if lnc else 0.0
    return {'dup': dup, 'beyond': beyond, 'first': beyond / NB, 'NB': NB, 'qA': qA.tolist(), 'qB': qB.tolist()}


def term_W(form, c, f, rate, D, sL):
    a, b = FORMS[form]
    E = c[0] * f[a] + (c[1] * f[b] if b else 0.0)
    return D * sL * rate * 1e-12 * E, E


# ---- the points (tokens from E215's registration; no datum)
pts = [r for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv'))) if r['loop'] == 'rgm136 gemmLnc']
assert sorted(r['id'] for r in pts) == ['a024', 'a026', 'a031', 'a032', 'b013'], [r['id'] for r in pts]
rows = [{'id': r['id'], 'arm': r['arm'], 'role': 'point (registered)', 'token': r['arm_token'], 'fmt': r['format'], 'kind': r['kind'],
         'mask': r['shire_mask'], 'card': CARD[r['arm']], 'ops': int(r['ops_per_minion_per_gemm']), 'pass1_position': r['pass1_position']}
        for r in pts]
rows += [{'id': 's03', 'arm': 'A', 'role': 'smoke (REPORTED, safety)', 'token': 'gemmLnc2x2x2', 'fmt': 'fp32', 'kind': 'random',
          'mask': '0xffffffff', 'card': CARD['A'], 'ops': 512, 'pass1_position': 'smoke before the gemmLnc block'},
         {'id': 's14', 'arm': 'B', 'role': 'smoke (REPORTED, safety)', 'token': 'gemmLnc2x2x2', 'fmt': 'fp32', 'kind': 'random',
          'mask': '0xffffffff', 'card': CARD['B'], 'ops': 512, 'pass1_position': 'smoke before the gemmLnc block'}]

specs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'f': 600.0, 'kernel': 'rgm136'} for r in rows]
pr = M.predict_many(specs)

# ---- check: the predictor reproduces MM1-v3.1's frozen E215 forecasts
frA = {r['token'].split('|')[1]: r for r in csv.DictReader(open(os.path.join(V31, 'out/e215/mm1_v31_e215.csv')))}
frB = json.load(open(os.path.join(LAB, 'tools/claims-v3/e215/forecast-e215b-v31.json')))['points']
checks = []
for r, p in zip(rows, pr):
    if r['role'].startswith('point'):
        if r['arm'] == 'A':
            fr = frA[r['token']]
            d = {'W': abs(p['W_over_idle'] - float(fr['v31_W_over_idle'])), 'cyc': abs(p['cycles_per_op_wall'] - float(fr['v31_cycles_wall'])),
                 'A': abs(p['W_affine']['A_W'] - float(fr['v31_W_A'])), 'B': abs(p['W_affine']['B_W_us'] - float(fr['v31_W_B_us']))}
            tol = {'W': 1e-4, 'cyc': 1e-3, 'A': 1e-5, 'B': 1e-5}
        else:
            fr = frB[r['id']]
            d = {'W': abs(p['W_over_idle'] - fr['W_over_idle']), 'cyc': abs(p['cycles_per_op_wall'] - fr['cycles_per_op_wall']),
                 'A': abs(p['W_affine']['A_W'] - fr['W_affine']['A_W']), 'B': abs(p['W_affine']['B_W_us'] - fr['W_affine']['B_W_us'])}
            tol = {'W': 1e-9, 'cyc': 1e-9, 'A': 1e-9, 'B': 1e-9}
        ok = bool(all(float(d[k]) <= tol[k] for k in d))
        d = {k: float(v) for k, v in d.items()}
        checks.append({'id': r['id'], 'max_abs_diff': d, 'tolerance': tol, 'reproduces_frozen': ok})
        assert ok, (r['id'], d)

out_rows = []
for r, p in zip(rows, pr):
    t = p['T_op_us']
    Q = 0.5 * (np.array(p['Q0']) + np.array(p['Q1']))
    f = feats(r['token'], Q)
    D = 1.0 + LAM * (p['die_start_c'] - 50.0)
    sL = 1.0 + XI * (p['s_V'] - 1.0)
    rate = p['minions'] / (t * 1e-6)
    sec = p['seconds_per_gemm']
    Pr = p['rest_law']['P_rest_W']
    W31 = p['W_over_idle']
    A, B = p['W_affine']['A_W'], p['W_affine']['B_W_us']
    o = dict(r, v31_cycles_wall=p['cycles_per_op_wall'], v31_cycles_mean=p['cycles_per_op_mean'], v31_t_op_us=t, v31_seconds_per_gemm=sec,
             v31_W_over_idle=W31, v31_A_W=A, v31_B_W_us=B, v31_J_over_idle=p['J_over_idle_per_gemm'], rest_law_W=Pr,
             rest_law_T0_c=p['rest_law']['T0_c'], v31_J_at_rest=(Pr + W31) * sec, v31_peak_planning_W=W31 + Pr + 2.0,
             dup=f['dup'], beyond=f['beyond'], first=f['first'], NB=f['NB'], qA_L2_L3_F=f['qA'], qB_L2_L3_F=f['qB'], D=D, sL=sL, s_V=p['s_V'])
    for form in FORMS:
        c = FIT['forms'][form]['constants_pJ_per_line']
        dW, E = term_W(form, c, f, rate, D, sL)
        W = W31 + dW
        tag = 'chosen' if form == CHOSEN else form
        o[f'{form}_term_W'] = dW
        o[f'{form}_term_pJ_per_minion_op'] = E
        o[f'{form}_W_over_idle'] = W
        o[f'{form}_B_W_us'] = B + dW * t
        o[f'{form}_J_over_idle'] = W * sec
        o[f'{form}_J_at_rest'] = (Pr + W) * sec
        o[f'{form}_peak_planning_W'] = W + Pr + 2.0
    o['term_form'] = CHOSEN
    for k in ('term_W', 'W_over_idle', 'B_W_us', 'J_over_idle', 'J_at_rest', 'peak_planning_W'):
        o['lnc_' + k] = o[f'{CHOSEN}_{k}']
    o['lnc_A_W'] = A
    o['stop_W'] = STOP[r['arm']]
    o['margin_W'] = STOP[r['arm']] - o['lnc_peak_planning_W']
    o['within_3W_of_stop'] = bool(o['margin_W'] < 3.0)
    o['max_over_forms_peak_planning_W'] = max(o[f'{fm}_peak_planning_W'] for fm in FORMS)
    o['within_3W_of_stop_any_form'] = bool((STOP[r['arm']] - o['max_over_forms_peak_planning_W']) < 3.0)
    out_rows.append(o)

# ---- held-out check on E213's two committed gemmLnc smokes (never fitted): W over idle = the smoke's work median minus the session's opening
#      rest moved to the smoke's start die by the card's frozen rest law (the reducer's p_rest there is the previous process's tail)
sm = []
d13 = {'A': json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json')))['arms']['A'],
       'B': json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json')))['arms']['B']}
for arm, sid, first in (('A', 's03', 's01'), ('B', 's14', 's11')):
    S = {r['point']: r for r in d13[arm]['smoke']['runs']}
    s, f0 = S[sid], S[first]
    rl = P['rest_law'][CARD[arm]]

    def law(T):
        return rl['a'] * T * T + rl['b'] * T + rl['c']
    rest = f0['p_rest_w'] + law(s['die_start_c']) - law(f0['die_start_c'])
    w = s['p_work_w'] - rest
    cyc = s['cycles_gemm'] / 512.0
    p = M.predict(CARD[arm], 'gemmLnc2x2x2', 'fp32', 'random', '0xffffffff', 600.0, kernel='rgm136', t0_c=s['die_start_c'])
    t = cyc / 600.0
    W31 = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / t
    Q = 0.5 * (np.array(p['Q0']) + np.array(p['Q1']))
    f = feats('gemmLnc2x2x2', Q)
    D = 1.0 + LAM * (s['die_start_c'] - 50.0)
    sL = 1.0 + XI * (p['s_V'] - 1.0)
    rate = 1024 / (t * 1e-6)
    row = {'id': f'E213 {arm} {sid}', 'card': CARD[arm], 'p_work_W': s['p_work_w'], 'rest_est_W': rest, 'W_over_idle_est': w,
           'cyc_wall_meas': cyc, 'v31_W_given_t': W31, 'v31_err_pct': (W31 - w) / w * 100}
    for form in FORMS:
        dW, _ = term_W(form, FIT['forms'][form]['constants_pJ_per_line'], f, rate, D, sL)
        row[f'{form}_W_given_t'] = W31 + dW
        row[f'{form}_err_pct'] = (W31 + dW - w) / w * 100
    # the measured analog for the same smoke in E215 (it runs again, now right before the gemmLnc block): the E213 smoke's measured W over
    # idle (estimated as above) on the frozen rest law at the card's T0 forecast, + 2 W (the registration's planning-peak form), and the
    # E213 session's own peak excess over its mean board (s14: 66.1 W peak against its 65.15 W median; a075: 64.22 against 62.93)
    Pr = law(rl['T0_forecast_c'])
    row['analog_E215_board_mean_rest_law_W'] = w + Pr
    row['analog_E215_peak_planning_W'] = w + Pr + 2.0
    row['analog_E215_board_mean_measured_rest_W'] = w + rest
    row['stop_W'] = STOP[arm]
    row['analog_margin_planning_W'] = STOP[arm] - (w + Pr + 2.0)
    row['analog_within_3W_planning'] = bool(STOP[arm] - (w + Pr + 2.0) < 3.0)
    sm.append(row)

now = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
cols = ['id', 'arm', 'role', 'token', 'card', 'fmt', 'kind', 'mask', 'ops', 'NB', 'v31_cycles_wall', 'v31_t_op_us', 'v31_seconds_per_gemm',
        'v31_W_over_idle', 'v31_A_W', 'v31_B_W_us', 'dup', 'first', 'term_form', 'lnc_term_W', 'lnc_W_over_idle', 'lnc_A_W', 'lnc_B_W_us',
        'lnc_J_over_idle', 'rest_law_W', 'rest_law_T0_c', 'lnc_J_at_rest', 'lnc_peak_planning_W', 'stop_W', 'margin_W', 'within_3W_of_stop',
        'F1_W_over_idle', 'F2_W_over_idle', 'F3_W_over_idle', 'F4_W_over_idle', 'max_over_forms_peak_planning_W', 'within_3W_of_stop_any_form']
with open(os.path.join(OUTD, 'forecasts-gemmlnc-e215.csv'), 'w', newline='') as fh:
    wr = csv.writer(fh, lineterminator='\n')
    wr.writerow(cols)
    for o in out_rows:
        wr.writerow([('%.9g' % o[c]) if isinstance(o[c], float) else o[c] for c in cols])
term = {'name': 'MM1-v3.1 + gemmLnc term', 'form': CHOSEN, 'x': FORMS[CHOSEN],
        'constants_pJ_per_line': FIT['forms'][CHOSEN]['constants_pJ_per_line'],
        'equation': 'dW = D * sL * (minions / t_op) * 1e-12 * (c1 * dup + c2 * first); dup = 26 duplicate line reads a minion-op (gemmLnc; 0 for '
                    'every cooperative loop); first = (14 qA_b + 12 qB_b) / NB, the duplicates of beyond-L2 lines on the A panel\'s first C block; '
                    'qA_b, qB_b = 1 - the L2 marginals of MM1-v3.1\'s Q; D = 1 + 0.0048 (die - 50), sL = 1 + xi (s_V - 1), MM1-v3.1\'s; the scorer\'s '
                    'given(): W = A + (B + dW t_op) / t_op, i.e. the term adds dW t_op to B',
        'fit': {k: FIT['forms'][CHOSEN][k] for k in ('in_sample_rms_pct', 'LOPO_rms_pct', 'LORO_rms_pct', 'folds')},
        'v31_alone_on_the_9': FIT['v31_alone'], 'selection': FIT['selection'], 'labels': 'post hoc (fitted after the 9 points existed); desk'}
json.dump(term, open(os.path.join(OUTD, 'term-gemmlnc.json'), 'w'), indent=1)
json.dump({'what': 'MM1-v3.1 + gemmLnc term forecasts for E215\'s gemmLnc points, before any E215 datum', 'made': now,
           'interpreter': '/usr/bin/python3 ' + sys.version.split()[0], 'numpy': np.__version__,
           'v31_params_sha256': hashlib.sha256(open(os.path.join(V31, 'out/mm1_v31_params.json'), 'rb').read()).hexdigest(),
           'reproduces_v31_frozen': checks, 'term': term, 'rows': out_rows, 'heldout_smokes_e213_REPORTED': sm},
          open(os.path.join(OUTD, 'forecasts-gemmlnc-e215.json'), 'w'), indent=1)

print('made', now, 'form', CHOSEN, FIT['forms'][CHOSEN]['constants_pJ_per_line'])
print('frozen-predictor reproduction:', [(c['id'], c['reproduces_frozen']) for c in checks])
print('%-5s %-4s %-14s %-18s %3s %8s %8s %7s %8s %8s %8s %7s %7s %6s %5s' % ('id', 'arm', 'token', 'card', 'NB', 'v31cyc', 'v31 W', 'term W', 'lnc W',
                                                                         'J idle', 'J rest', 'peak', 'stop', 'margin', 'flag'))
for o in out_rows:
    print('%-5s %-4s %-14s %-18s %3d %8.1f %8.3f %7.3f %8.3f %8.5f %8.5f %7.2f %7.1f %6.2f %5s | F1 %.2f F2 %.2f F3 %.2f F4 %.2f W; max-form peak %.2f %s' % (
        o['id'], o['arm'], o['token'], o['card'], o['NB'], o['v31_cycles_wall'], o['v31_W_over_idle'], o['lnc_term_W'], o['lnc_W_over_idle'],
        o['lnc_J_over_idle'], o['lnc_J_at_rest'], o['lnc_peak_planning_W'], o['stop_W'], o['margin_W'], o['within_3W_of_stop'],
        o['F1_W_over_idle'], o['F2_W_over_idle'], o['F3_W_over_idle'], o['F4_W_over_idle'], o['max_over_forms_peak_planning_W'],
        o['within_3W_of_stop_any_form']))
print('held-out E213 smokes (REPORTED):')
for s in sm:
    print('  %s: W over idle est %.2f (work %.2f - rest %.2f); v3.1 %.2f (%.1f%%); F1 %.1f%% F2 %.1f%% F3 %.1f%% F4 %.1f%% | E215 analog: '
          'board mean %.2f W on the rest law, planning peak %.2f W (stop %.0f, margin %.2f, within 3 W %s); on the E213 measured rest %.2f W' % (
        s['id'], s['W_over_idle_est'], s['p_work_W'], s['rest_est_W'], s['v31_W_given_t'], s['v31_err_pct'], s['F1_err_pct'], s['F2_err_pct'],
        s['F3_err_pct'], s['F4_err_pct'], s['analog_E215_board_mean_rest_law_W'], s['analog_E215_peak_planning_W'], s['stop_W'],
        s['analog_margin_planning_W'], s['analog_within_3W_planning'], s['analog_E215_board_mean_measured_rest_W']))
