#!/usr/bin/env python3
"""blind-e219 (Q232) step 2c: THE MEASURED-CONDITIONS FORECASTS in one table, before any E219 measurement is read (decl-e219's order:
the conditions read -> these forecasts hashed -> the scorer hashed -> the read). Every declared model, per listed run: MM1-v3.1, MM1-v3,
MM1-v2, 'v3.1+contention', 'v3.1+both' and verify-lay's four controls (fc-measured.json: each frozen predictor unchanged at the run's
measured clock, minion volts and die at start; the composed forms on MM1-v3.1's forecast at the same conditions, factors equal to
decl-e219's frozen ones). 'v3.1+gemmLnc' is NOT APPLICABLE (no gemmLnc arm). OUT-OF-DOMAIN runs: NOT FORECAST.
Twins per model (the declaration, section c): (card, kernel (run_gemm for a c-arm, rgm136 for gemmL), arm, format, mask, the mean of the
case's runs' measured clocks to 25 MHz) in the model's training time configurations, + the energy kind for energy (twin-keys.json
3418b7d8); the composed forms carry MM1-v3.1's flags. Checked first: at the nominal clocks the same code gives decl-e219's twin preview.
Writes forecasts-blind-e219.json (every field) and forecasts-blind-e219.csv (one row a run) in the lane folder.
Desk; stdlib. blind-e217's s02c_merge.py in form. Run: /usr/bin/python3 -I -B s02c_merge.py <lane dir>
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


PINS = {os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '0bd052dcbc277c9937c82b1c7dce04124e41deb1b57e21e4699271c8aa2d3376',
        os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json'): '3418b7d8de1f0e07e765de8deb2486d44392788f83c7bb9159ff8230fb96893c',
        os.path.join(DEC, 'inputs', 'step1', 'models-step1.json'): 'f2d6ee260e3b52c43fef4d5fcdb3f777def6928f0512dad27091aebb2ef70c5c',
        os.path.join(DEC, 'DECLARED-blind-e219.json'): '670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479',
        os.path.join(DEC, 'DECLARED-blind-e219.md'): 'd629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495',
        os.path.join(DEC, 'FROZEN.txt'): '73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e',
        os.path.join(DEC, 'forecasts-nominal-e219.json'): 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899'}
for p, h in PINS.items():
    assert sha(p) == h, p
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
TK = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json')))
MS1 = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'models-step1.json')))
COND = json.load(open(os.path.join(S2, 'conditions-e219.json')))
FC = json.load(open(os.path.join(S2, 'fc-measured.json')))
NC = json.load(open(os.path.join(S2, 'nominal-check.json')))
assert NC['VERDICT'].startswith('SAME PROCEDURE'), NC['VERDICT']
assert FC['nominal_selfcheck'] is False
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'v3.1+contention', 'v31b': 'v3.1+both', 'cn12': 'ctrl N1+N2', 'cg1': 'ctrl G1',
      'cg1n1': 'ctrl G1+N1', 'cf1b': 'ctrl F1-layout-blind'}
MODELS = list(MN)
assert [MN[m] for m in MODELS] == FC['models']
TWIN_OF = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', **{k: 'MM1-v3.1' for k in MODELS[3:]}}
tset = {n: {tuple(k) for k in TK[n]['time_keys']} for n in ('MM1-v3.1', 'MM1-v3', 'MM1-v2')}
eset = {n: {tuple(k) for k in TK[n]['energy_keys']} for n in ('MM1-v3.1', 'MM1-v3', 'MM1-v2')}


def f25(f):
    return int(round(float(f) / 25.0) * 25)


# the check: at the nominal clocks (card 1 600, card 0 800) this twin code gives decl-e219's preview (models-step1.json)
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800}
prev_check = {}
for n in ('MM1-v3.1', 'MM1-v3', 'MM1-v2'):
    nt = ne = 0
    for c in RL['cases']:
        if c['domain'] != 'IN':
            continue
        kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'], NOMF[c['card']])
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
    o = {'card': c['card'], 'arm': c['arm'], 'token': c['token'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'],
         'mask': c['mask'], 'domain': c['domain'], 'class': c['class'], 'group_mask': c['group_mask'], 'kernel': c['kernel'],
         'n_shires': c['n_shires'], 'ops_per_minion_pass': c['ops_per_minion_pass'], 'shape': c['shape'], 'families': c['families'],
         'n_runs': len(rs), 'runs': c['runs'], 'f_mean_mhz': f, 'f25': (f25(f) if f is not None else None),
         'arm_labels': sorted({x['arm_label'] for x in rs}), 'sessions': sorted({x['session'] for x in rs})}
    if c['domain'] == 'IN':
        kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'].lower(), o['f25'])
        ke = kt + (c['kind_energy'],)
        o['twin_time'] = {m: kt in tset[TWIN_OF[m]] for m in MODELS}
        o['twin_energy'] = {m: ke in eset[TWIN_OF[m]] for m in MODELS}
        r0 = FC['rows'][rs[0]['id']]
        o['factors'] = {m: r0[MN[m]]['factor'] for m in MODELS[3:]}
        o['phi_fresh'] = r0['v3.1+contention']['phi_fresh']
        for x in rs:
            for m in MODELS[3:]:
                assert FC['rows'][x['id']][MN[m]]['factor'] == o['factors'][m], (x['id'], m)
    cases[c['case']] = o
runs = {}
for r in R:
    cnd = COND['runs'][r['id']]
    o = {'id': r['id'], 'session': r['session'], 'card': r['card'], 'run': r['run'], 'i': r['i'], 'role': r['role'], 'arm_label': r['arm_label'],
         'arm': r['arm'], 'token': r['token'], 'fmt': r['fmt'], 'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'],
         'case': r['case'], 'class': r['class'], 'domain': r['domain'], 'group_mask': r['group_mask'], 'kernel': r['kernel'],
         'ops_per_minion_pass': r['ops_per_minion_pass'], 'f_mhz': cnd['kclock_mhz'], 'minion_mV': cnd['minion_mV'],
         'die_start_c': cnd['die_start_c']}
    fr = FC['rows'][r['id']]
    if r['domain'] == 'IN':
        for m in MODELS:
            o[m] = fr[MN[m]]
        o['inputs'] = fr['_inputs']
        assert fr['_inputs']['f'] == float(cnd['kclock_mhz'])
    else:
        o['OUT_OF_DOMAIN'] = fr['OUT_OF_DOMAIN']
    runs[r['id']] = o
now = time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())
IN = [c for c in cases.values() if c['domain'] == 'IN']
J = {'what': ("blind-e219 step 2: the frozen forecasts of every declared model for E219's 203 listed IN-DOMAIN runs (139 cases) at their "
              "MEASURED conditions (the primary view's clock, minion volts (card 1 the 0.517 V footing), die at start), made before any E219 "
              "measurement is read; W over idle at a measured op time t = W_A + W_B / t; the 189 OUT-OF-DOMAIN runs (175 cases) NOT FORECAST"),
     'made_pst': now, 'python': sys.version.split()[0],
     'declaration_sha256': {'DECLARED-blind-e219.md': sha(os.path.join(DEC, 'DECLARED-blind-e219.md')),
                            'DECLARED-blind-e219.json': sha(os.path.join(DEC, 'DECLARED-blind-e219.json')),
                            'FROZEN.txt': sha(os.path.join(DEC, 'FROZEN.txt')),
                            'forecasts-nominal-e219.json': sha(os.path.join(DEC, 'forecasts-nominal-e219.json'))},
     'inputs_sha256': {'work/step2/conditions-e219.json': sha(os.path.join(S2, 'conditions-e219.json')),
                       'work/step2/fc-measured.json': sha(os.path.join(S2, 'fc-measured.json')),
                       'work/step2/fc-nominalcheck.json': sha(os.path.join(S2, 'fc-nominalcheck.json')),
                       'work/step2/nominal-check.json': sha(os.path.join(S2, 'nominal-check.json'))},
     'models': MN, 'twin_flags_of': TWIN_OF, 'lnc_dW': 0.0,
     'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E219 (it equals MM1-v3.1 on every case); not scored',
     'MM1-v3.2': 'NOT DECLARED (NOT_ON_MAIN at the declaration, 18:36:38 PST; first on main 4e386f75, 19:50:04 PST): not forecast, not scored',
     'procedure_check': NC['VERDICT'], 'twin_preview_check_at_nominal_clocks': prev_check,
     'model_record': {k: v for k, v in FC.items() if k != 'rows'},
     'twins_summary': {m: {'time_twin_cases': sum(1 for c in IN if c['twin_time'][m]), 'energy_twin_cases': sum(1 for c in IN if c['twin_energy'][m]),
                           'in_domain_cases': len(IN)} for m in ('v31', 'v3', 'v2')},
     'cases': cases, 'runs': runs}
JP = os.path.join(L, 'forecasts-blind-e219.json')
json.dump(J, open(JP, 'w'), indent=1, sort_keys=True)
cols = ['id', 'session', 'card', 'run', 'role', 'arm_label', 'arm', 'token', 'fmt', 'kind', 'kind_energy', 'mask', 'class', 'domain', 'kernel',
        'ops_per_minion_pass', 'f_mhz', 'minion_mV', 'die_start_c']
NCOL = len(cols)
for m in MODELS:
    cols += [f'{m}_T_op_us', f'{m}_cyc_wall', f'{m}_cyc_mean', f'{m}_sec_pass', f'{m}_W_A', f'{m}_W_B', f'{m}_W_fc', f'{m}_energy']
cols += ['twin_time_v31', 'twin_time_v3', 'twin_time_v2', 'twin_energy_v31', 'twin_energy_v3', 'twin_energy_v2', 'factor_contention']
CP = os.path.join(L, 'forecasts-blind-e219.csv')
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    for rid, o in runs.items():
        row = [o[k] for k in cols[:NCOL]]
        c = cases[o['case']]
        if o['domain'] == 'IN':
            for m in MODELS:
                x = o[m]
                row += [repr(x['T_op_us']), repr(x['cyc_wall']), repr(x['cyc_mean']), repr(x['sec_pass']), repr(x['W_A']) if 'W_A' in x else '',
                        repr(x['W_B']) if 'W_B' in x else '', repr(x['W_fc']) if 'W_fc' in x else '', x['energy'][:12]]
            row += [int(c['twin_time']['v31']), int(c['twin_time']['v3']), int(c['twin_time']['v2']), int(c['twin_energy']['v31']),
                    int(c['twin_energy']['v3']), int(c['twin_energy']['v2']), repr(c['factors']['v31c'])]
        else:
            for m in MODELS:
                row += ['', '', '', '', '', '', '', 'NOT FORECAST (OUT OF DOMAIN)']
            row += ['', '', '', '', '', '', '']
        w.writerow(row)
print('twin preview check at the nominal clocks', json.dumps(prev_check))
print('twins at the measured clocks', json.dumps(J['twins_summary']))
print('cases', len(cases), 'in domain', len(IN), 'by class', dict(collections.Counter(c['class'] for c in cases.values())),
      'f25', dict(collections.Counter((c['card'], c['f25']) for c in cases.values())))
for n in ('forecasts-blind-e219.csv', 'forecasts-blind-e219.json'):
    print(sha(os.path.join(L, n)), n)
