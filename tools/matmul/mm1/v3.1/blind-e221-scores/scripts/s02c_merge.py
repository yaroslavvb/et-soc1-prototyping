#!/usr/bin/env python3
"""blind-e221 (Q235) step 2c: THE MEASURED-CONDITIONS FORECASTS in one table, before any E221 measurement is read (decl-e221's order:
the conditions read -> these forecasts hashed -> the scorer hashed -> the read). Every declared model, per listed run: MM1-v3.2, MM1-v3.1,
MM1-v3, MM1-v2, 'v3.1+contention', 'v3.1+both', verify-lay's four controls, and REPORTED 'MM1-v3.2+posimb' and 'MM1-v3.2+L3S'
(fc-measured.json: each frozen predictor unchanged at the run's measured clock, minion volts and die at start; the composed forms on their
base model's forecast at the same conditions). 'v3.1+gemmLnc' and 'MM1-v3.2+AF4' are NOT APPLICABLE (no gemmLnc arm).
Twins per model (the declaration, section c): (card, kernel rgm136, arm, format, mask, the mean of the case's runs' measured clocks to 25 MHz)
in the model's training time configurations, + the energy kind for energy (twin-keys.json 3bfd3883); the composed forms carry their base's
flags (the terms and controls MM1-v3.1's, the candidates MM1-v3.2's). Checked first: at the nominal clocks the same code gives decl-e221's
twin preview (MM1-v3.2 35/31, v3.1 17/15, v3 17/15, v2 8/8). Writes forecasts-blind-e221.json (every field) and forecasts-blind-e221.csv
(one row a run and model) at the lane top folder. Desk; stdlib. blind-e219's s02c_merge.py in form.
Run: /usr/bin/python3 -I -B s02c_merge.py <lane dir>
"""
import collections
import csv
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
DEC = os.path.join(L, 'work', 'decl')
S2 = os.path.join(L, 'work', 'step2')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


PINS = {os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '3a686510a43c453ac85588d5e649c7fe2e8554c3a98357e79047784e5165fe98',
        os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json'): '3bfd3883739214e80d485a06e72a58fde72b5abef44992345ae6c0cf98656807',
        os.path.join(DEC, 'inputs', 'step1', 'models-step1.json'): 'b2dc3a2ffa7934b8679212f960e256193f7576903f3bd2767836b5bc01387cfe',
        os.path.join(DEC, 'DECLARED-blind-e221.json'): 'b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4',
        os.path.join(DEC, 'DECLARED-blind-e221.md'): '9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b',
        os.path.join(DEC, 'FROZEN.txt'): '2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b',
        os.path.join(DEC, 'forecasts-nominal-e221.json'): 'f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831',
        os.path.join(DEC, 'forecasts-nominal-e221.csv'): 'e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a'}
for p, h in PINS.items():
    assert sha(p) == h, p
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
TK = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json')))
MS1 = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'models-step1.json')))
COND = json.load(open(os.path.join(S2, 'conditions-e221.json')))
FC = json.load(open(os.path.join(S2, 'fc-measured.json')))
NC = json.load(open(os.path.join(S2, 'nominal-check.json')))
assert NC['VERDICT'].startswith('SAME PROCEDURE'), NC['VERDICT']
assert FC['nominal_selfcheck'] is False
MN = {'v32': 'MM1-v3.2', 'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'v3.1+contention', 'v31b': 'v3.1+both',
      'cn12': 'ctrl N1+N2', 'cg1': 'ctrl G1', 'cg1n1': 'ctrl G1+N1', 'cf1b': 'ctrl F1-layout-blind', 'v32p': 'MM1-v3.2+posimb', 'v32l': 'MM1-v3.2+L3S'}
MODELS = list(MN)
assert [MN[m] for m in MODELS] == FC['models']
TWIN_OF = {'v32': 'MM1-v3.2', 'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'MM1-v3.1', 'v31b': 'MM1-v3.1', 'cn12': 'MM1-v3.1',
           'cg1': 'MM1-v3.1', 'cg1n1': 'MM1-v3.1', 'cf1b': 'MM1-v3.1', 'v32p': 'MM1-v3.2', 'v32l': 'MM1-v3.2'}
BASE4 = ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2')
tset = {n: {tuple(k) for k in TK[n]['time_keys']} for n in BASE4}
eset = {n: {tuple(k) for k in TK[n]['energy_keys']} for n in BASE4}


def f25(f):
    return int(round(float(f) / 25.0) * 25)


# the check: at the nominal clocks (card 1 600, the governed cards 800) this twin code gives decl-e221's preview (models-step1.json)
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800, 'aifoundry2 card 0': 800}
prev_check = {}
for n in BASE4:
    nt = ne = 0
    for c in RL['cases']:
        kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'].lower(), NOMF[c['card']])
        nt += kt in tset[n]
        ne += (kt + (c['kind_energy'],)) in eset[n]
    pv = MS1['twin_preview_nominal'][n]
    prev_check[n] = {'time': nt, 'energy': ne, 'frozen_preview_time': pv['time_twin_cases_at_nominal_clock'],
                     'frozen_preview_energy': pv['energy_twin_cases_at_nominal_clock']}
    assert nt == pv['time_twin_cases_at_nominal_clock'] and ne == pv['energy_twin_cases_at_nominal_clock'], prev_check[n]

R = RL['runs']
cases = {}
for c in RL['cases']:
    rs = [x for x in R if x['case'] == c['case']]
    assert [x['id'] for x in rs] == c['runs'], c['case']
    fs = [COND['runs'][x['id']]['kclock_mhz'] for x in rs if COND['runs'][x['id']]['kclock_mhz'] is not None]
    f = sum(fs) / len(fs) if fs else None
    o = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'], 'mask': c['mask'],
         'class': c['class'], 'subfamily': c.get('subfamily'), 'group_mask': c['group_mask'], 'kernel': c['kernel'], 'n_shires': c['n_shires'],
         'MB': c['MB'], 'NB': c['NB'], 'KB': c['KB'], 'ops_per_minion_pass': c['ops_per_minion_pass'], 'families': c['families'],
         'n_runs': len(rs), 'runs': c['runs'], 'f_mean_mhz': f, 'f25': (f25(f) if f is not None else None),
         'arm_labels': sorted({x['arm_label'] for x in rs}), 'sessions': sorted({x['session'] for x in rs})}
    kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'].lower(), o['f25'])
    ke = kt + (c['kind_energy'],)
    o['twin_time'] = {m: kt in tset[TWIN_OF[m]] for m in MODELS}
    o['twin_energy'] = {m: ke in eset[TWIN_OF[m]] for m in MODELS}
    r0 = FC['rows'][rs[0]['id']]
    o['factors'] = {m: r0[MN[m]]['factor'] for m in ('v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b')}
    o['phi_fresh'] = r0['v3.1+contention']['phi_fresh']
    o['posimb_in_scope'] = r0['MM1-v3.2+posimb']['in_scope']
    o['l3s_in_domain'] = r0['MM1-v3.2+L3S']['in_domain_l3s']
    for x in rs:
        for m in ('v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
            assert FC['rows'][x['id']][MN[m]]['factor'] == o['factors'][m], (x['id'], m)
        assert FC['rows'][x['id']]['MM1-v3.2+posimb']['in_scope'] == o['posimb_in_scope']
        assert FC['rows'][x['id']]['MM1-v3.2+L3S']['in_domain_l3s'] == o['l3s_in_domain']
    cases[c['case']] = o
runs = {}
for r in R:
    cnd = COND['runs'][r['id']]
    o = {'id': r['id'], 'session': r['session'], 'card': r['card'], 'run': r['run'], 'i': r['i'], 'role': r['role'], 'arm_label': r['arm_label'],
         'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'], 'case': r['case'],
         'class': r['class'], 'subfamily': r.get('subfamily'), 'group_mask': r['group_mask'], 'kernel': r['kernel'],
         'ops_per_minion_pass': r['ops_per_minion_pass'], 'f_mhz': cnd['kclock_mhz'], 'minion_mV': cnd['minion_mV'], 'die_start_c': cnd['die_start_c']}
    fr = FC['rows'][r['id']]
    for m in MODELS:
        o[m] = fr[MN[m]]
    o['inputs'] = fr['_inputs']
    assert fr['_inputs']['f'] == float(cnd['kclock_mhz'])
    runs[r['id']] = o
now = time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())
J = {'what': ("blind-e221 step 2: the frozen forecasts of every declared model for E221's 811 listed runs (733 cases, all IN DOMAIN) at their "
              "MEASURED conditions (the primary view's clock, minion volts (card 1 the 0.517 V footing), die at start), made before any E221 "
              "measurement is read; W over idle at a measured op time t = W_A + W_B / t"),
     'made_pst': now, 'python': sys.version.split()[0],
     'declaration_sha256': {'DECLARED-blind-e221.md': sha(os.path.join(DEC, 'DECLARED-blind-e221.md')),
                            'DECLARED-blind-e221.json': sha(os.path.join(DEC, 'DECLARED-blind-e221.json')),
                            'FROZEN.txt': sha(os.path.join(DEC, 'FROZEN.txt')),
                            'forecasts-nominal-e221.json': sha(os.path.join(DEC, 'forecasts-nominal-e221.json')),
                            'forecasts-nominal-e221.csv': sha(os.path.join(DEC, 'forecasts-nominal-e221.csv'))},
     'inputs_sha256': {'work/step2/conditions-e221.json': sha(os.path.join(S2, 'conditions-e221.json')),
                       'work/step2/fc-measured.json': sha(os.path.join(S2, 'fc-measured.json')),
                       'work/step2/fc-nominalcheck.json': sha(os.path.join(S2, 'fc-nominalcheck.json')),
                       'work/step2/nominal-check.json': sha(os.path.join(S2, 'nominal-check.json'))},
     'models': MN, 'models_reported': ['v32p', 'v32l'], 'twin_flags_of': TWIN_OF, 'lnc_dW': 0.0,
     'not_applicable': {'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E221 (it equals MM1-v3.1 on every case); not scored',
                        'MM1-v3.2+AF4': 'NOT APPLICABLE: no gemmLnc arm in E221 (it equals MM1-v3.2 on every case); not scored'},
     'procedure_check': NC['VERDICT'], 'twin_preview_check_at_nominal_clocks': prev_check,
     'model_record': {k: v for k, v in FC.items() if k != 'rows'},
     'twins_summary': {m: {'time_twin_cases': sum(1 for c in cases.values() if c['twin_time'][m]),
                           'energy_twin_cases': sum(1 for c in cases.values() if c['twin_energy'][m]), 'cases': len(cases)} for m in ('v32', 'v31', 'v3', 'v2')},
     'f25_by_card': {f'{k[0]}|{k[1]}': v for k, v in sorted(collections.Counter((c['card'], c['f25']) for c in cases.values()).items())},
     'cases': cases, 'runs': runs}
JP = os.path.join(L, 'forecasts-blind-e221.json')
json.dump(J, open(JP, 'w'), indent=1, sort_keys=True)
cols = ['id', 'session', 'card', 'run', 'role', 'arm_label', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'class', 'subfamily', 'group_mask', 'kernel',
        'ops_per_minion_pass', 'f_mhz', 'minion_mV', 'die_start_c', 'model', 'reported', 'T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean',
        'seconds_per_pass', 'energy', 'W_A', 'W_B_us', 'W_over_idle_own_t', 'J_over_idle_per_pass', 'factor', 'twin_time', 'twin_energy']
CP = os.path.join(L, 'forecasts-blind-e221.csv')
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    for rid, o in runs.items():
        c = cases[o['case']]
        head = [o[k] if o[k] is not None else '' for k in cols[:19]]
        for m in MODELS:
            x = o[m]
            w.writerow(head + [MN[m], 'REPORTED' if m in ('v32p', 'v32l') else '', repr(x['T_op_us']), repr(x['cyc_wall']), repr(x['cyc_mean']),
                               repr(x['sec_pass']), x['energy'], repr(x['W_A']) if 'W_A' in x else '', repr(x['W_B']) if 'W_B' in x else '',
                               repr(x['W_fc']) if 'W_fc' in x else '', repr(x['J_over_idle_pass']) if 'J_over_idle_pass' in x else '',
                               repr(x['factor']) if 'factor' in x else '', int(c['twin_time'][m]), int(c['twin_energy'][m])])
print('twin preview check at the nominal clocks', json.dumps(prev_check))
print('twins at the measured clocks', json.dumps(J['twins_summary']))
print('f25 by card', json.dumps(J['f25_by_card']))
print('cases', len(cases), 'by class', dict(collections.Counter(c['class'] for c in cases.values())), 'runs', len(runs))
for n in ('forecasts-blind-e221.csv', 'forecasts-blind-e221.json'):
    print(sha(os.path.join(L, n)), n)
