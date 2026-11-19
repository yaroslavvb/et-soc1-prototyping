#!/usr/bin/env python3
"""unread-e214 (Q225) step 2c: the frozen forecasts in one table, with each case's twin flags per model (the declaration, section c), before
any E214 measurement is read: forecasts-unread-e214.json (every field) and forecasts-unread-e214.csv (one row a run). Inputs: step 1's files,
work/step2/conditions-e214.json and the three models' fc-<model>.json. Desk. Run: /usr/bin/python3 -I -B s02c_merge.py <lane dir>
"""
import collections
import csv
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
S1 = os.path.join(L, 'work', 'step1')
S2 = os.path.join(L, 'work', 'step2')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
TK = json.load(open(os.path.join(S1, 'twin-keys.json')))
COND = json.load(open(os.path.join(S2, 'conditions-e214.json')))
FC = {m: json.load(open(os.path.join(S2, f'fc-{m}.json'))) for m in ('v31', 'v3', 'v2')}
MNAME = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2'}
NEWK = sorted({r['kind'] for r in RL['runs'] if r['kind'].startswith('pattern:') and not r['kind'].startswith('pattern:sparse50')})
tset = {m: {tuple(k) for k in TK[MNAME[m]]['time_keys']} for m in FC}
eset = {m: {tuple(k) for k in TK[MNAME[m]]['energy_keys']} for m in FC}
R = RL['runs']
bycase = collections.defaultdict(list)
for r in R:
    bycase[r['case']].append(r)
cases = {}
for c, rs in sorted(bycase.items()):
    r0 = rs[0]
    f = sum(COND['runs'][r['id']]['kclock_mhz'] for r in rs) / len(rs)
    f25 = int(round(f / 25.0) * 25)
    kt = (r0['card'], 'rgm136', r0['arm'], r0['fmt'], r0['mask'].lower(), f25)
    ke = kt + (r0['kind_energy'],)
    cases[c] = {'card': r0['card'], 'arm': r0['arm'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'kind_energy': r0['kind_energy'], 'mask': r0['mask'],
                'n_runs': len(rs), 'runs': [r['id'] for r in rs], 'f_mean_mhz': f, 'f25': f25,
                'group': 'S' if r0['kind'] in NEWK else ('C' if r0['kind'].startswith('pattern:sparse50') else 'M'),
                'twin_time': {m: kt in tset[m] for m in FC}, 'twin_energy': {m: ke in eset[m] for m in FC},
                'arm_labels': sorted({r['arm_label'] for r in rs}), 'sessions': sorted({r['session'] for r in rs})}
runs = {}
for r in R:
    c = COND['runs'][r['id']]
    o = {'id': r['id'], 'session': r['session'], 'card': r['card'], 'run': r['run'], 'role': r['role'], 'arm_label': r['arm_label'], 'arm': r['arm'],
         'fmt': r['fmt'], 'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'], 'case': r['case'], 'group': cases[r['case']]['group'],
         'ops_minion_gemm': 64 * r['MB'] * r['NB'] * r['KB'], 'f_mhz': c['kclock_mhz'], 'minion_mV': c['minion_mV'], 'die_start_c': c['die_start_c']}
    for m, F in FC.items():
        o[m] = F['rows'][r['id']]
    runs[r['id']] = o
now = time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())
J = {'what': ('unread-e214 step 2: the frozen forecasts of MM1-v3.1, MM1-v3 and MM1-v2 for E214\'s 593 runs at their measured conditions '
              '(clock, minion volts, die at start), before any E214 measurement is read; W over idle at a measured op time t = W_A + W_B / t'),
     'made_pst': now, 'declaration_sha256': {'DECLARED-unread-e214.md': sha(os.path.join(L, 'DECLARED-unread-e214.md')),
                                             'DECLARED-unread-e214.json': sha(os.path.join(L, 'DECLARED-unread-e214.json'))},
     'inputs_sha256': {'work/step2/conditions-e214.json': sha(os.path.join(S2, 'conditions-e214.json')),
                       **{f'work/step2/fc-{m}.json': sha(os.path.join(S2, f'fc-{m}.json')) for m in FC}},
     'models': {m: {k: v for k, v in F.items() if k != 'rows'} for m, F in FC.items()},
     'twins_summary': {m: {'time_twin_cases': sum(1 for c in cases.values() if c['twin_time'][m]),
                           'energy_twin_cases': sum(1 for c in cases.values() if c['twin_energy'][m]), 'cases': len(cases)} for m in FC},
     'cases': cases, 'runs': runs}
json.dump(J, open(os.path.join(L, 'forecasts-unread-e214.json'), 'w'), indent=1, sort_keys=True)
cols = ['id', 'session', 'card', 'run', 'role', 'arm_label', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'group', 'ops_minion_gemm', 'f_mhz',
        'minion_mV', 'die_start_c']
for m in ('v31', 'v3', 'v2'):
    cols += [f'{m}_T_op_us', f'{m}_cyc_wall', f'{m}_cyc_mean', f'{m}_sec_gemm', f'{m}_W_A', f'{m}_W_B', f'{m}_W_fc', f'{m}_energy']
for m in ('v31', 'v3'):
    for k in ('zeros', 'ones', 'random'):
        cols += [f'{m}_null_{k}_W_A', f'{m}_null_{k}_W_B']
    cols += [f'{m}_gate_none_W_A', f'{m}_gate_none_W_B']
cols += ['twin_time_v31', 'twin_time_v3', 'twin_time_v2', 'twin_energy_v31', 'twin_energy_v3', 'twin_energy_v2']
with open(os.path.join(L, 'forecasts-unread-e214.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    for rid, o in runs.items():
        row = [o[k] for k in cols[:16]]
        for m in ('v31', 'v3', 'v2'):
            x = o[m]
            row += [repr(x['T_op_us']), repr(x['cyc_wall']), repr(x['cyc_mean']), repr(x['sec_gemm']), repr(x.get('W_A', '')) if 'W_A' in x else '',
                    repr(x['W_B']) if 'W_B' in x else '', repr(x['W_fc']) if 'W_fc' in x else '', x['energy'][:12]]
        for m in ('v31', 'v3'):
            x = o[m]
            for k in ('zeros', 'ones', 'random'):
                n = x.get(f'null_{k}')
                row += [repr(n['W_A']) if n else '', repr(n['W_B']) if n else '']
            g = x.get('gate_none_REPORTED')
            row += [repr(g['W_A']) if g else '', repr(g['W_B']) if g else '']
        c = cases[o['case']]
        row += [int(c['twin_time']['v31']), int(c['twin_time']['v3']), int(c['twin_time']['v2']), int(c['twin_energy']['v31']),
                int(c['twin_energy']['v3']), int(c['twin_energy']['v2'])]
        w.writerow(row)
print(json.dumps(J['twins_summary']))
print('groups (cases)', dict(collections.Counter(c['group'] for c in cases.values())), 'by card', dict(collections.Counter(c['card'] for c in cases.values())))
for n in ('forecasts-unread-e214.csv', 'forecasts-unread-e214.json'):
    print(sha(os.path.join(L, n)), n)
