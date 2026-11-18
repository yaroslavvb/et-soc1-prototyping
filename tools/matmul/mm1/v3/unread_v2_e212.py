#!/usr/bin/env python3
"""MM1-v3's step 1, before any fit (the spec's section 9 item 1): MM1-v2 as frozen (tools/matmul/mm1/v2 at 3ca4b717, its four freeze-table
files pinned by sha256 here and its own SHA256SUMS checked) scored UNREAD on every E212 session committed when MM1-v3's fit started, per run
and per case, in the lab's form; the table is written and hashed before any v3 fit runs. Desk; numpy.

    /usr/bin/python3 -I -B unread_v2_e212.py --out <dir>      writes unread_v2_e212_runs.csv, unread_v2_e212_cases.csv, unread_v2_e212.json

LABEL: UNREAD. MM1-v2's predictor and constants were frozen (pushed 01:44:48 PST Tue 17 Nov 2026) before E212's first datum (05:30 PST), but
no forecast for E212's points was frozen then: these are made now by the frozen code, the call's arguments chosen now. Not a blind test.
HOW MM1-v2 IS CALLED (as tools/matmul/mm1/v2/score_unread.py called MM1-v1 on E208): the run's primary view (win on the governed cards,
band600 on card 1) at its measured kernel clock; card 1 at V = 0.517 V (v2's footing), G = 0; the governed cards at the view's measured minion
volts when present, G by v2's M7 relation at the clock. Time for every kind (time is kind-blind in MM1-v2); energy for random, zeros and
ones only (E212's switch-pattern arms are not read for energy: their counts are not yet made). W given t = A + B / t_meas (v2's affine form),
scored at 3 W and above (watts below). A case = (card, shape, format, kind, mask): the mean of its runs, as v3's points.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, '..', 'v2'))
PINS = {'mm1_v2.py': '5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08',
        'mm1_core_v2.py': 'f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08',
        'kinds_v2.py': '14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d',
        'out/mm1_v2_params.json': '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def v2_model():
    for rel, h in PINS.items():
        if sha(os.path.join(V2, rel)) != h:
            sys.exit(f'MM1-v2 pin mismatch: {rel}')
    bad = 0
    n = 0
    for ln in open(os.path.join(V2, 'SHA256SUMS')):
        h, rel = ln.split()
        n += 1
        bad += sha(os.path.join(V2, rel)) != h
    if bad:
        sys.exit(f'MM1-v2 SHA256SUMS: {bad} of {n} differ')
    sys.path.insert(0, V2)
    import mm1_v2  # noqa: E402
    sys.path.pop(0)
    return mm1_v2.Model(json.load(open(os.path.join(V2, 'out', 'mm1_v2_params.json')))), n


def st(es):
    es = [e for e in es if e is not None]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_pct': round(100 * math.sqrt(sum(e * e for e in es) / n), 2), 'bias_pct': round(100 * sum(es) / n, 2)}


def sta(es):
    es = [e for e in es if e is not None]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_W': round(math.sqrt(sum(e * e for e in es) / n), 3), 'bias_W': round(sum(es) / n, 3)}


def call(M, r):
    card = r['card']
    V = None
    if card != 'aifoundry1 card 1' and r.get('V_mv'):
        V = r['V_mv'] / 1000.0
    kind = r['kind'] if r['kind'] in ('random', 'zeros', 'ones') else 'random'
    return M.predict(card, r['arm'], r['fmt'], kind, r['mask'], r['f'], V=V)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('--out must not be this folder')
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, HERE)
    import data_v3 as D  # noqa: E402
    M, nsum = v2_model()
    R = D.e212_runs()
    rows = []
    for r in R:
        pr = call(M, r)
        row = {'id': r['id'], 'session': r['session'], 'card': r['card'], 'run': r['run'], 'arm_label': r['arm_label'], 'role': r['role'],
               'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'f_mhz': round(r['f'], 3),
               'meas_cyc_wall': round(r['cyc_wall'], 4), 'meas_cyc_mean': round(r['cyc_mean'], 4), 'meas_T_op_us': r['T'],
               'v2_cyc_wall': round(pr['cycles_per_op_wall'], 4), 'v2_cyc_mean': round(pr['cycles_per_op_mean'], 4)}
        row['e_wall'] = pr['cycles_per_op_wall'] / r['cyc_wall'] - 1
        row['e_mean'] = pr['cycles_per_op_mean'] / r['cyc_mean'] - 1
        if 'w' in r and 'W_affine' in pr:
            Wg = pr['W_affine']['A_W'] + pr['W_affine']['B_W_us'] / r['T']
            row.update({'meas_w': r['w'], 'meas_rest_w': r['p_rest'], 'v2_w_given_t': Wg, 'v2_w_forecast_t': pr['W_over_idle']})
            row['e_w_given_t'] = Wg / r['w'] - 1 if r['w'] >= 3.0 else None
            row['dW_low_w'] = Wg - r['w'] if r['w'] < 3.0 else None
            tf = pr['T_op_us']
            row['e_jo_forecast_t'] = (pr['W_over_idle'] * tf) / (r['w'] * r['T']) - 1 if r['w'] >= 3.0 else None
            row['e_jr_given_t'] = (r['p_rest'] + Wg) / (r['p_rest'] + r['w']) - 1
            row['e_jr_forecast_t'] = (r['p_rest'] + pr['W_over_idle']) * tf / ((r['p_rest'] + r['w']) * r['T']) - 1
        rows.append(row)
    # per case: v2 on the case's mean (the mean measured over its runs; v2 called at the mean clock and volts)
    T, E = D.cases(R, 'E212')
    Em = {e['id']: e for e in E}
    crow = []
    for c in T:
        rr = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'f': c['f']}
        e = Em.get(c['id'])
        if e and c['card'] != 'aifoundry1 card 1':
            rr['V_mv'] = e['V'] * 1000.0
        pr = call(M, rr)
        row = {'id': c['id'], 'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'n_runs': c['n_runs'],
               'f_mhz': round(c['f'], 3), 'meas_cyc_wall': round(c['cw'], 4), 'v2_cyc_wall': round(pr['cycles_per_op_wall'], 4),
               'e_wall': pr['cycles_per_op_wall'] / c['cw'] - 1, 'e_mean': pr['cycles_per_op_mean'] / c['cyc_mean'] - 1}
        if e and 'W_affine' in pr:
            Wg = pr['W_affine']['A_W'] + pr['W_affine']['B_W_us'] / e['T']
            row.update({'meas_w': e['w'], 'v2_w_given_t': Wg, 'e_w_given_t': (Wg / e['w'] - 1) if e['w'] >= 3.0 else None,
                        'dW_low_w': (Wg - e['w']) if e['w'] < 3.0 else None})
        crow.append(row)
    flds = ['id', 'session', 'card', 'run', 'arm_label', 'role', 'arm', 'fmt', 'kind', 'mask', 'f_mhz', 'meas_cyc_wall', 'meas_cyc_mean',
            'meas_T_op_us', 'v2_cyc_wall', 'v2_cyc_mean', 'e_wall', 'e_mean', 'meas_w', 'meas_rest_w', 'v2_w_given_t', 'v2_w_forecast_t',
            'e_w_given_t', 'dW_low_w', 'e_jo_forecast_t', 'e_jr_given_t', 'e_jr_forecast_t']
    with open(os.path.join(out, 'unread_v2_e212_runs.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=flds, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    cf = ['id', 'card', 'arm', 'fmt', 'kind', 'mask', 'n_runs', 'f_mhz', 'meas_cyc_wall', 'v2_cyc_wall', 'e_wall', 'e_mean', 'meas_w',
          'v2_w_given_t', 'e_w_given_t', 'dW_low_w']
    with open(os.path.join(out, 'unread_v2_e212_cases.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cf, lineterminator='\n')
        w.writeheader()
        for r in crow:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    S = {'label': 'UNREAD: MM1-v2 frozen (3ca4b717) on E212, arguments chosen now', 'interpreter': sys.version.split()[0],
         'v2_sha256sums_checked': nsum, 'sessions': sorted({r['session'] for r in rows}), 'n_runs': len(rows), 'n_cases': len(crow),
         'per_run': {}, 'per_case': {}}
    for lab, fn in (('all', lambda r: True), ('aifoundry1 card 1', lambda r: r['card'] == 'aifoundry1 card 1'),
                    ('aifoundry1 card 0', lambda r: r['card'] == 'aifoundry1 card 0'), ('aifoundry2 card 0', lambda r: r['card'] == 'aifoundry2 card 0')):
        rs = [r for r in rows if fn(r)]
        cs = [r for r in crow if fn(r)]
        S['per_run'][lab] = {'wall': st([r['e_wall'] for r in rs]), 'counter_mean': st([r['e_mean'] for r in rs]),
                             'W_given_t_ge3W': st([r.get('e_w_given_t') for r in rs]), 'W_under_3W_watts': sta([r.get('dW_low_w') for r in rs]),
                             'J_over_idle_t_forecast_ge3W': st([r.get('e_jo_forecast_t') for r in rs]),
                             'J_at_rest_given_t': st([r.get('e_jr_given_t') for r in rs]), 'J_at_rest_t_forecast': st([r.get('e_jr_forecast_t') for r in rs])}
        S['per_case'][lab] = {'wall': st([r['e_wall'] for r in cs]), 'counter_mean': st([r['e_mean'] for r in cs]),
                              'W_given_t_ge3W': st([r.get('e_w_given_t') for r in cs]), 'W_under_3W_watts': sta([r.get('dW_low_w') for r in cs])}
    json.dump(S, open(os.path.join(out, 'unread_v2_e212.json'), 'w'), indent=1, sort_keys=True)
    for fn in ('unread_v2_e212_runs.csv', 'unread_v2_e212_cases.csv', 'unread_v2_e212.json'):
        print(sha(os.path.join(out, fn)), fn)
    print(json.dumps(S['per_run']['all']), json.dumps(S['per_case']['all']))


if __name__ == '__main__':
    main()
