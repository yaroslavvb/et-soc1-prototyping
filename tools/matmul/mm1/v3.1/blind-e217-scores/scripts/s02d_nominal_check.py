#!/usr/bin/env python3
"""blind-e217 (Q228) step 2d: THE PROCEDURE CHECK, before any E217 measurement is read. This lane's forecast code (s02b_forecast.py), run
at decl-e217's declared NOMINAL conditions (--nominal), must re-make decl-e217's frozen nominal forecasts: every run of a case against the
case's frozen forecast (forecasts-nominal-e217.json; group S's energy and the zero-row gates' REPORTED columns against
forecasts-nominal-e217-counts.json; group S's null kinds against forecasts-nominal-e217.json's null_kinds). Fields: T_op_us, cycles (wall,
counter mean), seconds a GEMM, W_A, W_B, W over idle at the model's own op time; energy status. Prints the worst relative difference per
model and field and the count of fields not bit-equal. Desk; stdlib. Run: /usr/bin/python3 -I -B s02d_nominal_check.py <lane dir>
"""
import collections
import hashlib
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
DEC = os.path.join(L, 'work', 'decl')
S2 = os.path.join(L, 'work', 'step2')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(os.path.join(DEC, 'forecasts-nominal-e217.json')) == '611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c'
assert sha(os.path.join(DEC, 'forecasts-nominal-e217-counts.json')) == '590c0be2ebb30bd07fd89b6d22bd182eb5415134807ca8afde06d67952065353'
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e217.json')))['cases']
FCC = json.load(open(os.path.join(DEC, 'forecasts-nominal-e217-counts.json')))['cases']
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2'}
TF = (('T_op_us', 'T_op_us'), ('cyc_wall', 'cyc_wall'), ('cyc_mean', 'cyc_mean'), ('sec_gemm', 'sec_gemm'))
EF = (('W_A', 'W_A'), ('W_B', 'W_B'), ('W_fc', 'W_fc'))
res = {}
for m, nm in MN.items():
    X = json.load(open(os.path.join(S2, f'fc-{m}-nominalcheck.json')))['rows']
    worst = collections.defaultdict(float)
    neq = collections.Counter()
    nfield = collections.Counter()
    status = collections.Counter()
    for r in RL['runs']:
        mine = X[r['id']]
        fz = FCN[r['case']][nm]
        for a, b in TF:
            nfield[a] += 1
            if mine[a] != fz[b]:
                neq[a] += 1
                worst[a] = max(worst[a], abs(mine[a] / fz[b] - 1))
        fe = fz if r['group_kind'] != 'S' else (FCC[r['case']][nm] if nm in FCC[r['case']] else fz)
        st_mine = mine['energy'] == 'FORECAST'
        st_fz = fe.get('energy') == 'FORECAST'
        status['equal' if st_mine == st_fz else 'DIFFERENT'] += 1
        if st_mine and st_fz:
            for a, b in EF:
                nfield[a] += 1
                if mine[a] != fe[b]:
                    neq[a] += 1
                    worst[a] = max(worst[a], abs(mine[a] / fe[b] - 1))
        if r['group_kind'] == 'S' and m in ('v31', 'v3'):
            for k in ('zeros', 'ones', 'random'):
                a0 = mine[f'null_{k}']
                b0 = FCN[r['case']]['null_kinds'][f'{nm}|{k}']
                for f in ('W_A', 'W_B', 'W_fc', 'T_op_us'):
                    nfield['null_' + f] += 1
                    if a0[f] != b0[f]:
                        neq['null_' + f] += 1
                        worst['null_' + f] = max(worst['null_' + f], abs(a0[f] / b0[f] - 1))
            for tag, key in (('gate_literal_REPORTED', f'{nm} literal gate (REPORTED)'), ('gate_count_REPORTED', f'{nm} count gate (REPORTED)')):
                if tag in mine:
                    b0 = FCC[r['case']][key]
                    for f in ('W_A', 'W_B', 'W_fc'):
                        nfield[tag + '_' + f] += 1
                        if mine[tag][f] != b0[f]:
                            neq[tag + '_' + f] += 1
                            worst[tag + '_' + f] = max(worst[tag + '_' + f], abs(mine[tag][f] / b0[f] - 1))
    res[nm] = {'fields_compared': dict(nfield), 'fields_not_bit_equal': dict(neq), 'worst_rel_diff': dict(worst),
               'energy_status': dict(status), 'all_bit_equal': sum(neq.values()) == 0 and status.get('DIFFERENT', 0) == 0}
res['VERDICT'] = 'SAME PROCEDURE: every field bit-equal' if all(res[n]['all_bit_equal'] for n in MN.values()) else 'DIFFERS: see the fields'
json.dump(res, open(os.path.join(S2, 'nominal-check.json'), 'w'), indent=1, sort_keys=True)
for n in MN.values():
    print(n, 'fields', sum(res[n]['fields_compared'].values()), 'not bit-equal', sum(res[n]['fields_not_bit_equal'].values()),
          'worst', json.dumps(res[n]['worst_rel_diff']), 'energy status', res[n]['energy_status'])
print(res['VERDICT'])
print(sha(os.path.join(S2, 'nominal-check.json')), 'work/step2/nominal-check.json')
