#!/usr/bin/env python3
"""fix-unread-e212sw (Q218), ADDENDUM 1, step A3: THE READ AND THE SCORE of E209's three real points (POST HOC, UNREAD), exactly as the addendum
declares (work/addendum/addendum-declared-e209.json, sha256 5f9e7f21...) with the forecasts of step A2 (forecasts-e209-posthoc.json, 18438c3f...).

Reads E209's committed data file at GitHub main 3e8991d0 (git show from the lab clone; checked against its data folder's SHA256SUMS and against
MM1-v3's vendored copy), reduces each listed run by data_v3.mms_runs's own rule (the energy condition widened to the listed runs; cross-checked
against data_v3.e209_runs on time, clock and die), evaluates the frozen forms at each run's measured conditions, cross-checks MM1-v3's form against
its predictor called there (the same added rows and phi), and scores Q1 per run and per point (Q3, Q4 REPORTED; Q2 NOT SCORED: no zeros point).
Then REPORTS, post hoc, group A's Q1 pass-rule conditions (P1, P2) with e35 and e36 added to the 42 declared Q1 cases (taken at full precision from
the unchanged scorer's re-run, work/rerun-full.json), and group B with e34 added. Finally compares with verify-unread-e212sw's own post hoc numbers.
Desk; no device; single-threaded (in slot.sh). Run: /usr/bin/python3 -I -B a03_score_e209.py
"""
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
WL = os.path.join(ME, 'work', 'lab')
V3 = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3')
CNT = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
LANDU = os.path.join(W, 'out', 'unread-e212sw', 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
LAB = '<LAB>'
OUTD = os.path.join(ME, 'work', 'addendum')
DATAD = os.path.join(OUTD, 'data')
os.makedirs(DATAD, exist_ok=True)
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
LOW = 3.0
COMMIT = open(os.path.join(ME, 'work', 'main-commit.txt')).read().strip()
assert COMMIT == '3e8991d0da7a054797a1a8503c38b6e02796960e'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())


AD_P = os.path.join(OUTD, 'addendum-declared-e209.json')
AF_P = os.path.join(OUTD, 'forecasts-e209-posthoc.json')
assert sha(AD_P) == '5f9e7f219104afa78f8d2ba89bfe1c5ca4af0e2295ac1c9be858d9321c3531bb', 'addendum declaration changed'
assert sha(AF_P) == '18438c3f82d0c0859542403135b371fb9736613fdb262bae0d53951eb7139b65', 'addendum forecasts changed'
AD = json.load(open(AD_P))
AF = json.load(open(AF_P))
start = ts()
print('A3 start', start)

# ---------------------------------------------------------------- the read: E209's committed data file
rel = 'docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/data-e209.json'
b = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{rel}'], check=True, capture_output=True, env=ENV).stdout
dp = os.path.join(DATAD, 'data-e209.json')
open(dp, 'wb').write(b)
listed = []
for sf in ('SHA256SUMS', 'SHA256SUMS-note15', 'SHA256SUMS-note16'):   # the data folder's checksum files (the data file is listed in note 16's)
    sums = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/{sf}'],
                          check=True, capture_output=True, env=ENV).stdout.decode()
    listed += [(sf, ln.split()[0]) for ln in sums.splitlines() if ln.split() and ln.split()[-1] == 'data-e209.json']
src = {'path': rel, 'sha256': sha(dp), 'data_folder_SHA256SUMS': listed, 'equal_to_SHA256SUMS': bool(listed) and all(h == sha(dp) for _, h in listed),
       'mm1_v3_vendored_equal': sha(dp) == sha(os.path.join(V3, 'inputs', 'e209', 'data-e209.json'))}
print('source', json.dumps(src))
assert src['equal_to_SHA256SUMS'] and src['mm1_v3_vendored_equal']
DD = json.load(open(dp))

sys.path.insert(0, V3)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import mm1_core_v3 as C  # noqa: E402
import mm1_v3  # noqa: E402

WANT = {p['point']: p for p in AD['points']}


def e209_records():
    """data_v3.mms_runs's selection for the listed points, the energy condition widened to them (kind 'real')"""
    ck = DD['card']
    card = D.CARDS[ck]
    pv = DD['primary_view']
    out = []
    for r in DD['runs']:
        if r.get('arm') not in WANT:
            continue
        rec = {'run': r['run'], 'point': r['arm'], 'card': card, 'role': r.get('role'), 'capped': bool(r.get('capped')), 'view': pv,
               'die_start_c': r.get('die_start_c'), 'why': None}
        if not r.get('ran') or r.get('role') in (None, 'null'):
            rec['why'] = 'did not run, or no role'
            out.append(rec)
            continue
        mask = r.get('shires')
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', r.get('values') or '')
        assert m and mask, r['run']
        MB, NB, KB = (int(x) for x in m.groups())
        rec.update({'arm': f'gemmL{MB}x{NB}x{KB}', 'fmt': r.get('type'), 'mask': mask, 'values': r.get('values')})
        v = (r.get('views') or {}).get(pv) or {}
        if not (v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1):
            rec['why'] = 'no time figure in the primary view'
            out.append(rec)
            continue
        rec.update({'f': float(v['kclock_mhz']), 'T': float(v['T_op_us']), 'cyc_wall': float(v['cyc_op_max'])})
        energy_ok = (v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time')
        if energy_ok:
            mv = ((v.get('rails') or {}).get('minion') or {}).get('mV')
            rec.update({'w': float(v['dP_w']), 'p_mean': float(v['p_mean_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']),
                        'V_mv': (float(mv) if mv is not None else None)})
        else:
            rec['why'] = ('capped' if r.get('capped') else ('role time' if r['role'] == 'time' else 'no dP_w / p_mean_w in the primary view'))
        out.append(rec)
    return out


REC = e209_records()
# cross-check against MM1-v3's own loader on time, clock and die (it reads these points for time only)
mine = {r['run']: r for r in REC}
loader = {'compared': 0, 'max_abs_diff': 0.0, 'runs_in_mm1_v3_time_records': 0}
for q in D.e209_runs():
    if q['run'] not in mine:
        continue
    loader['runs_in_mm1_v3_time_records'] += 1
    assert 'w' not in q, 'MM1-v3 read energy for a real point?'
    m = mine[q['run']]
    for fld in ('T', 'f'):
        loader['compared'] += 1
        loader['max_abs_diff'] = max(loader['max_abs_diff'], abs(q[fld] - m[fld]))
    assert q['die_start_c'] == m['die_start_c'] and q['arm'] == m['arm'] and q['mask'] == m['mask']
assert loader['max_abs_diff'] == 0.0, loader
print('loader check against data_v3.e209_runs:', json.dumps(loader))
for pt, p in WANT.items():
    got = [r for r in REC if r['point'] == pt]
    assert len(got) == len(p['runs_registered']), (pt, len(got))
    for r in got:
        assert r['values'] == p['runs_registered'][0]['values'] and r['arm'] == p['arm'] and r['fmt'] == p['fmt'] and r['mask'] == p['mask']

# ---------------------------------------------------------------- the predictor with the same rows and phi (for the cross-check and Q4)
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
for S in ('S1', 'S2'):
    for kind, row in C32[S].items():
        assert kind not in EN.E210C[S]
        EN.E210C[S][kind] = row
for key, row in C16.items():
    assert key not in EN.SWT
    EN.SWT[key] = row
DECL = json.load(open(os.path.join(LANDU, 'declared-unread.json')))
for k, v in DECL['e_phi']['values'].items():
    fmt, kind = k.split('|', 1)
    if kind.startswith('pattern:sparse50'):
        continue
    for kb1 in (True, False):
        EN._PHI[(fmt, kind, kb1)] = float(v)
params = json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json')))
M3 = mm1_v3.Model(params)
g3, xi = AF['g'], AF['xi']
FCR = {r['id']: r for r in AF['rows']}


def W_form(k, card, t, f, V, T0):
    sV = (V / 0.517) ** 2
    return (k['K0'] + g3 * C.G_of_f(card, f) + (1e6 / t) * (sV * k['K1'] + (1.0 + xi * (sV - 1.0)) * k['K2'])) * (1.0 + 0.0048 * (T0 - 50.0))


xcheck = {'n': 0, 'max_rel': 0.0}
rows = []
for r in REC:
    p = WANT[r['point']]
    fid = p['id']
    row = {'id': f"{fid}|{r['run']}", 'point': r['point'], 'group': p['group'], 'run': r['run'], 'card': r['card'], 'arm': p['arm'], 'fmt': p['fmt'],
           'kind': 'real', 'mask': p['mask'], 'role': r['role']}
    if 'w' not in r:
        row['not_scored'] = r['why']
        rows.append(row)
        continue
    V = r['V_mv'] / 1000.0 if r.get('V_mv') else float(C.volts(r['card'], r['f']))
    T0 = r['die_start_c'] if r.get('die_start_c') is not None else 50.0
    cond = {'f': r['f'], 'V': V, 'T0': T0, 't': r['T']}
    fr = FCR[fid]
    fc = {m: W_form(fr[m], r['card'], cond['t'], cond['f'], cond['V'], cond['T0']) for m in ('V3', 'N', 'N2', 'V3phi1')}
    pr = M3.predict(r['card'], p['arm'], p['fmt'], 'real', p['mask'], cond['f'], kernel='rgm136', V=cond['V'], t0_c=cond['T0'])
    Wp = pr['W_affine']['A_W'] + pr['W_affine']['B_W_us'] / cond['t']
    rel_ = abs(Wp / fc['V3'] - 1.0)
    xcheck['n'] += 1
    xcheck['max_rel'] = max(xcheck['max_rel'], rel_)
    t_fc = pr['T_op_us']
    w_tfc = pr['W_affine']['A_W'] + pr['W_affine']['B_W_us'] / t_fc
    Wm = r['w']
    row.update({'f_mhz': cond['f'], 'V': cond['V'], 'die_c': cond['T0'], 't_meas_us': cond['t'], 't_fc_us': t_fc, 'W_meas': Wm, 'P_rest': r['p_rest']})
    for m in ('V3', 'N', 'N2', 'V3phi1'):
        row[f'W_{m}'] = fc[m]
        row[f'e1_{m}'] = (fc[m] / Wm - 1.0) if Wm >= LOW else None
    row['e3_V3'] = (r['p_rest'] + fc['V3']) / (r['p_rest'] + Wm) - 1.0
    row['e4_V3'] = (w_tfc * t_fc) / (Wm * cond['t']) - 1.0 if Wm >= LOW else None
    row['share_why'] = 'NOT SCORED: no zeros point at this configuration in E209'
    rows.append(row)
assert xcheck['max_rel'] < 1e-9, xcheck
print('V3 frozen form = the predictor at each measured condition:', json.dumps(xcheck))

# ---------------------------------------------------------------- per point (case = the point: the mean of its runs' errors)
cases = []
for pt in ('e34', 'e35', 'e36'):
    rs = [x for x in rows if x['point'] == pt and not x.get('not_scored')]
    c = {'case': f'E209|{pt}', 'group': WANT[pt]['group'], 'fmt': WANT[pt]['fmt'], 'arm': WANT[pt]['arm'], 'n_runs': len(rs),
         'W_meas': float(np.mean([x['W_meas'] for x in rs])) if rs else None}
    for k in ('e1_V3', 'e1_N', 'e1_N2', 'e1_V3phi1', 'e3_V3', 'e4_V3'):
        v = [x[k] for x in rs if x.get(k) is not None]
        c[k] = float(np.mean(v)) if v else None
    cases.append(c)


def st(es):
    es = [e for e in es if e is not None]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_pct': 100 * math.sqrt(sum(e * e for e in es) / n), 'mean_pct': 100 * sum(es) / n}


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    lo = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, lo + 1)) / 2 ** n)


def head(pairs, tie=0.01):
    k = n = ties = 0
    for x, y in pairs:
        d = abs(y) - abs(x)
        if abs(d) < tie:
            ties += 1
            continue
        n += 1
        k += d > 0
    sa, sb = st([x for x, _ in pairs]), st([y for _, y in pairs])
    return {'n_cases': len(pairs), 'V3': sa, 'other': sb, 'rms_lower (P1)': sa['rms_pct'] < sb['rms_pct'], 'V3_closer': k, 'other_closer': n - k,
            'ties': ties, 'non_tied': n, 'p_two_sided': binom_two_sided(k, n), 'sign_holds (P2)': n >= 6 and binom_two_sided(k, n) < 0.05 and k > n - k}


RF = json.load(open(os.path.join(ME, 'work', 'rerun-full.json')))
A42 = RF['group_A_cases_full']
B3 = RF['group_B_cases_full']
assert len(A42) == 42 and len(B3) == 3
newA = [c for c in cases if c['group'] == 'A']
newB = [c for c in cases if c['group'] == 'B']
pooled = {
    'group_A_declared_42_Q1_vs_N': head([(c['e1_V3'], c['e1_N']) for c in A42]),
    'group_A_with_e35_e36_Q1_vs_N': head([(c['e1_V3'], c['e1_N']) for c in A42] + [(c['e1_V3'], c['e1_N']) for c in newA]),
    'group_A_with_e35_e36_Q1_vs_N2': head([(c['e1_V3'], c['e1_N2']) for c in A42] + [(c['e1_V3'], c['e1_N2']) for c in newA]),
    'group_B_with_e34_Q1': {'V3': st([c['e1_V3'] for c in B3] + [c['e1_V3'] for c in newB]), 'N': st([c['e1_N'] for c in B3] + [c['e1_N'] for c in newB])},
    'E209_alone_Q1': {'V3': st([c['e1_V3'] for c in cases]), 'N': st([c['e1_N'] for c in cases]), 'N2': st([c['e1_N2'] for c in cases])},
    'Q2': 'unchanged: 29 declared cases (no E209 point has a zeros reference); P3 and P4 as declared',
}
pa = pooled['group_A_with_e35_e36_Q1_vs_N']
pooled['reading'] = ('REPORTED, post hoc: with e35 and e36 in group A, P1 ' + ('holds' if pa['rms_lower (P1)'] else 'fails') + ' and P2 ' +
                     ('holds' if pa['sign_holds (P2)'] else 'fails') + '; with P3 and P4 unchanged, the pass rule would read ' +
                     ('PASS' if pa['rms_lower (P1)'] and pa['sign_holds (P2)'] else 'not PASS') + '. The verdict of record is the declared one.')

# ---------------------------------------------------------------- against verify-unread-e212sw's own post hoc numbers
VP = os.path.join(W, 'out', 'verify-unread-e212sw', 'work', 'score', 'e209-real-posthoc.json')
vp = json.load(open(VP))
cmpv = {'verifier_file_sha256': sha(VP), 'per_point': {}}
for c in cases:
    pt = c['case'].split('|')[1]
    vc = vp['cases'][pt]
    cmpv['per_point'][pt] = {'e1_V3_mine': c['e1_V3'], 'e1_V3_verifier': vc['e1_V3'], 'e1_N_mine': c['e1_N'], 'e1_N_verifier': vc['e1_N'],
                             'abs_diff_V3': abs(c['e1_V3'] - vc['e1_V3']), 'abs_diff_N': abs(c['e1_N'] - vc['e1_N'])}
vg = vp['group_A_with_e35_e36_Q1']
cmpv['group_A_with_e35_e36'] = {'mine': {'V3_rms': pa['V3']['rms_pct'], 'N_rms': pa['other']['rms_pct'], 'closer': pa['V3_closer'],
                                         'non_tied': pa['non_tied'], 'ties': pa['ties'], 'p': pa['p_two_sided']},
                                'verifier': {k: vg[k] for k in ('V3_rms', 'N_rms', 'V3_closer', 'non_tied', 'ties', 'p')}}
cmpv['max_abs_diff'] = max(max(v['abs_diff_V3'], v['abs_diff_N']) for v in cmpv['per_point'].values())
print('against the verifier:', json.dumps(cmpv, indent=1))

res = {'label': AD['label'], 'what': 'fix-unread-e212sw ADDENDUM 1 step A3: the read and score of E209\'s three real points (POST HOC, UNREAD)',
       'start_pst': start, 'end_pst': ts(), 'interpreter': sys.version.split()[0], 'numpy': np.__version__, 'lab_commit': COMMIT,
       'addendum_declaration_sha256': sha(AD_P), 'addendum_forecasts_sha256': sha(AF_P), 'source': src, 'loader_check': loader,
       'v3_form_vs_predictor': xcheck, 'cases': cases, 'pooled_REPORTED_post_hoc': pooled, 'against_verifier': cmpv,
       'not_scored': {x['id']: x['not_scored'] for x in rows if x.get('not_scored')}}
pj = os.path.join(OUTD, 'scores-e209-posthoc.json')
json.dump(res, open(pj, 'w'), indent=1, sort_keys=True)
rf = ['id', 'point', 'group', 'run', 'card', 'arm', 'fmt', 'kind', 'mask', 'role', 'not_scored', 'f_mhz', 'V', 'die_c', 't_meas_us', 't_fc_us', 'W_meas',
      'P_rest', 'W_V3', 'W_N', 'W_N2', 'W_V3phi1', 'e1_V3', 'e1_N', 'e1_N2', 'e1_V3phi1', 'e3_V3', 'e4_V3', 'share_why']
pc = os.path.join(OUTD, 'scores-e209-posthoc-runs.csv')
with open(pc, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=rf, lineterminator='\n', extrasaction='ignore')
    w.writeheader()
    for x in rows:
        w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in x.items()})
print('A3 written', res['end_pst'])
print(sha(pj), 'scores-e209-posthoc.json')
print(sha(pc), 'scores-e209-posthoc-runs.csv')
for c in cases:
    print(c['case'], c['group'], c['fmt'], 'runs', c['n_runs'], 'W_meas %.3f' % c['W_meas'], 'Q1 V3 %+.4f N %+.4f N2 %+.4f V3phi1 %+.4f' %
          (100 * c['e1_V3'], 100 * c['e1_N'], 100 * c['e1_N2'], 100 * c['e1_V3phi1']), 'Q3 %+.4f Q4 %+.4f' % (100 * c['e3_V3'], 100 * c['e4_V3']))
for k, v in pooled.items():
    print(k, json.dumps(v))
