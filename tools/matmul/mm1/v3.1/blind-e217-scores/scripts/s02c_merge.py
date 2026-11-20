#!/usr/bin/env python3
"""blind-e217 (Q228) step 2c: THE MEASURED-CONDITIONS FORECASTS in one table, before any E217 measurement is read (decl-e217's order:
the conditions read -> these forecasts hashed -> the scorer hashed -> the read). Every declared model, per listed run:
MM1-v3.1, MM1-v3, MM1-v2 (fc-v31/v3/v2.json, each frozen predictor unchanged at the run's measured clock, minion volts and die at start),
and the composed forms on MM1-v3.1's forecast at the same conditions (the declaration's 'The models'): 'v3.1+contention' (F1: time x the
case's frozen factor clip(1 + a Phi_fresh, 0.3, 3); energy MM1-v3.1's affine A + B / t at its own op time), 'v3.1+both' (the composition of
reg-e216: F1's time; W at a time t = A + (B + dW t_op,v3.1) / t with the gemmLnc term's dW = 0 on every E217 case) and verify-lay's four
controls (time x 1 + sum a_i x_i; energy MM1-v3.1's affine at their own op time). The factors are fc-lay.json's (equal to decl-e217's frozen
nominal factors, 2430 of 2430). 'v3.1+gemmLnc' is NOT APPLICABLE (no gemmLnc arm). Group S: the null kinds (MM1-v3.1, MM1-v3) and the
zero-row gates' REPORTED columns. Twins per model (the declaration, section c): (card, kernel, arm, format, mask, the mean of the case's
runs' measured clocks to 25 MHz) in the model's training time configurations, + the energy kind for energy (twin-keys.json 3418b7d8); the
composed forms carry MM1-v3.1's flags. Writes forecasts-blind-e217.json (every field) and forecasts-blind-e217.csv (one row a run).
Desk; stdlib. Run: /usr/bin/python3 -I -B s02c_merge.py <lane dir>
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


assert sha(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')) == '25154e5dedd47519a145c693273e3ac3f3cbcabc4e82581a30ebaef34d0d4bc1'
assert sha(os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json')) == '3418b7d8de1f0e07e765de8deb2486d44392788f83c7bb9159ff8230fb96893c'
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
TK = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'twin-keys.json')))
COND = json.load(open(os.path.join(S2, 'conditions-e217.json')))
FC = {m: json.load(open(os.path.join(S2, f'fc-{m}.json'))) for m in ('v31', 'v3', 'v2')}
LAYF = json.load(open(os.path.join(S2, 'fc-lay.json')))
NC = json.load(open(os.path.join(S2, 'nominal-check.json')))
assert NC['VERDICT'].startswith('SAME PROCEDURE'), NC['VERDICT']
BASE = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2'}
COMP = {'v31c': ('v3.1+contention', 'v3.1+contention'), 'v31b': ('v3.1+both', 'v3.1+contention'), 'cn12': ('ctrl N1+N2', 'ctrl N1+N2'),
        'cg1': ('ctrl G1', 'ctrl G1'), 'cg1n1': ('ctrl G1+N1', 'ctrl G1+N1'), 'cf1b': ('ctrl F1-layout-blind', 'ctrl F1-layout-blind')}
MODELS = list(BASE) + list(COMP)
MNAME = {**BASE, **{k: v[0] for k, v in COMP.items()}}
TWIN_OF = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', **{k: 'MM1-v3.1' for k in COMP}}
tset = {n: {tuple(k) for k in TK[n]['time_keys']} for n in ('MM1-v3.1', 'MM1-v3', 'MM1-v2')}
eset = {n: {tuple(k) for k in TK[n]['energy_keys']} for n in ('MM1-v3.1', 'MM1-v3', 'MM1-v2')}
LNC_DW = 0.0   # the gemmLnc term's dW on every E217 case (no gemmLnc arm)


def composed(base, g, extra, dW=None):
    o = {'T_op_us': base['T_op_us'] * g, 'cyc_wall': base['cyc_wall'] * g, 'cyc_mean': base['cyc_mean'] * g, 'sec_gemm': base['sec_gemm'] * g,
         'factor': g}
    o.update(extra)
    if base['energy'] != 'FORECAST':
        o['energy'] = base['energy']
        return o
    WB = base['W_B'] if dW is None else base['W_B'] + dW * base['T_op_us']
    o.update({'energy': 'FORECAST', 'W_A': base['W_A'], 'W_B': WB, 'W_fc': base['W_A'] + WB / o['T_op_us']})
    return o


R = RL['runs']
bycase = collections.defaultdict(list)
for r in R:
    bycase[r['case']].append(r)
cases = {}
for c, rs in sorted(bycase.items()):
    r0 = rs[0]
    fs = [COND['runs'][r['id']]['kclock_mhz'] for r in rs if COND['runs'][r['id']]['kclock_mhz'] is not None]
    f = sum(fs) / len(fs)
    f25 = int(round(f / 25.0) * 25)
    kt = (r0['card'], 'rgm136', r0['arm'], r0['fmt'], r0['mask'].lower(), f25)
    ke = kt + (r0['kind_energy'],)
    cases[c] = {'card': r0['card'], 'arm': r0['arm'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'kind_energy': r0['kind_energy'], 'mask': r0['mask'],
                'n_runs': len(rs), 'runs': [r['id'] for r in rs], 'f_mean_mhz': f, 'f25': f25, 'group_kind': r0['group_kind'],
                'group_mask': r0['group_mask'], 'group_shape': r0['group_shape'], 'n_shires': r0['n_shires'],
                'twin_time': {m: kt in tset[TWIN_OF[m]] for m in MODELS}, 'twin_energy': {m: ke in eset[TWIN_OF[m]] for m in MODELS},
                'arm_labels': sorted({r['arm_label'] for r in rs}), 'sessions': sorted({r['session'] for r in rs}),
                'factors': {k: LAYF['cases'][c][v[1]]['factor'] for k, v in COMP.items()},
                'phi_fresh': LAYF['cases'][c]['v3.1+contention']['phi_fresh']}
runs = {}
for r in R:
    c = COND['runs'][r['id']]
    o = {'id': r['id'], 'session': r['session'], 'card': r['card'], 'run': r['run'], 'i': r['i'], 'role': r['role'], 'arm_label': r['arm_label'],
         'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'], 'case': r['case'],
         'group_kind': r['group_kind'], 'group_mask': r['group_mask'], 'group_shape': r['group_shape'],
         'ops_minion_gemm': 64 * r['MB'] * r['NB'] * r['KB'], 'f_mhz': c['kclock_mhz'], 'minion_mV': c['minion_mV'], 'die_start_c': c['die_start_c']}
    for m in BASE:
        o[m] = FC[m]['rows'][r['id']]
    base = o['v31']
    for k, (nm, src) in COMP.items():
        g = LAYF['cases'][r['case']][src]['factor']
        o[k] = composed(base, g, {'note': nm}, dW=(LNC_DW if k == 'v31b' else None))
    runs[r['id']] = o
now = time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())
J = {'what': ("blind-e217 step 2: the frozen forecasts of every declared model for E217's 599 listed runs at their MEASURED conditions "
              "(the primary view's clock, minion volts (card 1 the 0.517 V footing), die at start), made before any E217 measurement is read; "
              "W over idle at a measured op time t = W_A + W_B / t"),
     'made_pst': now, 'python': sys.version.split()[0],
     'declaration_sha256': {'DECLARED-blind-e217.md': sha(os.path.join(DEC, 'DECLARED-blind-e217.md')),
                            'DECLARED-blind-e217.json': sha(os.path.join(DEC, 'DECLARED-blind-e217.json')),
                            'FROZEN.txt': sha(os.path.join(DEC, 'FROZEN.txt')), 'COUNTS-FROZEN.txt': sha(os.path.join(DEC, 'COUNTS-FROZEN.txt'))},
     'inputs_sha256': {'work/step2/conditions-e217.json': sha(os.path.join(S2, 'conditions-e217.json')),
                       **{f'work/step2/fc-{m}.json': sha(os.path.join(S2, f'fc-{m}.json')) for m in ('v31', 'v3', 'v2', 'lay')},
                       'work/step2/nominal-check.json': sha(os.path.join(S2, 'nominal-check.json'))},
     'models': MNAME, 'twin_flags_of': TWIN_OF, 'lnc_dW': LNC_DW,
     'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E217 (it equals MM1-v3.1 on every case); not scored',
     'procedure_check': NC['VERDICT'],
     'model_records': {m: {k: v for k, v in F.items() if k != 'rows'} for m, F in FC.items()},
     'twins_summary': {m: {'time_twin_cases': sum(1 for c in cases.values() if c['twin_time'][m]),
                           'energy_twin_cases': sum(1 for c in cases.values() if c['twin_energy'][m]), 'cases': len(cases)} for m in ('v31', 'v3', 'v2')},
     'cases': cases, 'runs': runs}
JP = os.path.join(L, 'forecasts-blind-e217.json')
json.dump(J, open(JP, 'w'), indent=1, sort_keys=True)
cols = ['id', 'session', 'card', 'run', 'role', 'arm_label', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'group_kind', 'group_mask', 'group_shape',
        'ops_minion_gemm', 'f_mhz', 'minion_mV', 'die_start_c']
NCOL = len(cols)
for m in MODELS:
    cols += [f'{m}_T_op_us', f'{m}_cyc_wall', f'{m}_cyc_mean', f'{m}_sec_gemm', f'{m}_W_A', f'{m}_W_B', f'{m}_W_fc', f'{m}_energy']
for m in ('v31', 'v3'):
    for k in ('zeros', 'ones', 'random'):
        cols += [f'{m}_null_{k}_W_A', f'{m}_null_{k}_W_B']
    cols += [f'{m}_gate_literal_W_A', f'{m}_gate_literal_W_B', f'{m}_gate_count_W_A', f'{m}_gate_count_W_B']
cols += ['twin_time_v31', 'twin_time_v3', 'twin_time_v2', 'twin_energy_v31', 'twin_energy_v3', 'twin_energy_v2', 'factor_contention']
CP = os.path.join(L, 'forecasts-blind-e217.csv')
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    for rid, o in runs.items():
        row = [o[k] for k in cols[:NCOL]]
        for m in MODELS:
            x = o[m]
            row += [repr(x['T_op_us']), repr(x['cyc_wall']), repr(x['cyc_mean']), repr(x['sec_gemm']), repr(x['W_A']) if 'W_A' in x else '',
                    repr(x['W_B']) if 'W_B' in x else '', repr(x['W_fc']) if 'W_fc' in x else '', x['energy'][:12]]
        for m in ('v31', 'v3'):
            x = o[m]
            for k in ('zeros', 'ones', 'random'):
                n = x.get(f'null_{k}')
                row += [repr(n['W_A']) if n else '', repr(n['W_B']) if n else '']
            for t in ('gate_literal_REPORTED', 'gate_count_REPORTED'):
                g = x.get(t)
                row += [repr(g['W_A']) if g else '', repr(g['W_B']) if g else '']
        c = cases[o['case']]
        row += [int(c['twin_time']['v31']), int(c['twin_time']['v3']), int(c['twin_time']['v2']), int(c['twin_energy']['v31']),
                int(c['twin_energy']['v3']), int(c['twin_energy']['v2']), repr(c['factors']['v31c'])]
        w.writerow(row)
print(json.dumps(J['twins_summary']))
print('cases', len(cases), 'by group_kind', dict(collections.Counter(c['group_kind'] for c in cases.values())),
      'by group_mask', dict(collections.Counter(c['group_mask'] for c in cases.values())), 'f25', dict(collections.Counter((c['card'], c['f25']) for c in cases.values())))
for n in ('forecasts-blind-e217.csv', 'forecasts-blind-e217.json'):
    print(sha(os.path.join(L, n)), n)
