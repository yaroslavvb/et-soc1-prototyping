#!/usr/bin/env python3
"""decl-e217 (Q228) step 2c: write the frozen nominal forecasts, forecasts-nominal-e217.csv (one row a case and model) and
forecasts-nominal-e217.json (meta + every field of work/step2/fc-nominal.json), at the lane root. Reads only this lane's step-2 output and
the declaration (its sha256 recorded in the meta). Desk. Run: /usr/bin/python3 -I -B s02c_write.py <lane dir>"""
import csv
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


FC = json.load(open(os.path.join(L, 'work', 'step2', 'fc-nominal.json')))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
CASE = {c['case']: c for c in RL['cases']}
MODELS = ['MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1', 'ctrl F1-layout-blind']
made = subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()
meta = {'what': "decl-e217: E217's NOMINAL forecasts by every declared model, frozen before any E217 datum (the declaration's section h)",
        'written_pst': made, 'declaration_md_sha256': sha(os.path.join(L, 'DECLARED-blind-e217.md')),
        'declaration_json_sha256': sha(os.path.join(L, 'DECLARED-blind-e217.json')),
        'fc_nominal_sha256': sha(os.path.join(L, 'work', 'step2', 'fc-nominal.json')),
        'runs_listed_sha256': sha(os.path.join(L, 'work', 'step1', 'runs-listed.json')),
        'walk_feats_sha256': sha(os.path.join(L, 'work', 'step2', 'walk-feats-e217.json')),
        'nominal_conditions': FC['nominal'], 'models': MODELS, 'controls_constants': FC['controls_constants'], 'a_fresh': FC['a_fresh'],
        'checks': FC['checks'], 'factor_ranges_subset_only': FC['factor_ranges_subset_only'], 'energy_status': FC['energy_status'],
        'python': FC['python'], 'numpy': FC['numpy'], 'sha256sum_c': FC['sha256sum_c'], 'n_cases': FC['n_cases'],
        'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E217 (it equals MM1-v3.1 on every case)',
        'group_S_energy': 'NOT FORECAST at this freeze (no count): made after counts-e217 into forecasts-nominal-e217-counts.csv/.json',
        'units': {'T_op_us': 'microseconds an op (a minion)', 'cycles': 'cycles an op', 'seconds_per_gemm': 's', 'W': 'W over idle',
                  'W_B_us': 'W x us (W over idle at a measured op time t is W_A + W_B_us / t)', 'J_over_idle_per_gemm': 'J'}}
out = {'meta': meta, 'cases': FC['cases'], 'layout_blind_groups': FC['layout_blind_groups']}
JP = os.path.join(L, 'forecasts-nominal-e217.json')
json.dump(out, open(JP, 'w'), indent=1, sort_keys=True)
CP = os.path.join(L, 'forecasts-nominal-e217.csv')
cols = ['case', 'card', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'n_shires', 'group_shape', 'group_mask', 'group_kind', 'n_runs', 'model',
        'f_mhz', 'V', 'die_start_c', 'T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'energy', 'W_A', 'W_B_us',
        'W_over_idle_own_t', 'J_over_idle_per_gemm', 'rest_law_W', 'factor', 'phi_fresh']


def g(x, k, f='%.9g'):
    v = x.get(k)
    return '' if v is None else (f % v if isinstance(v, float) else str(v))


n = 0
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for case, o in FC['cases'].items():
        c = CASE[case]
        for m in MODELS:
            x = o[m]
            en = 'FORECAST' if x['energy'] == 'FORECAST' else x['energy']
            jg = (x['W_fc'] * x['sec_gemm']) if x['energy'] == 'FORECAST' else None
            w.writerow([case, c['card'], c['arm'], c['fmt'], c['kind'], c['kind_energy'], c['mask'], c['n_shires'], c['group_shape'],
                        c['group_mask'], c['group_kind'], len(c['runs']), m, g(x, 'f_mhz'), g(x, 'V'), g(x, 'die_start_c'), g(x, 'T_op_us'),
                        g(x, 'cyc_wall'), g(x, 'cyc_mean'), g(x, 'sec_gemm'), en, g(x, 'W_A'), g(x, 'W_B'), g(x, 'W_fc'),
                        '' if jg is None else '%.9g' % jg, g(x, 'rest_law_W'), g(x, 'factor'), g(x, 'phi_fresh')])
            n += 1
print('rows', n, 'cases', len(FC['cases']), 'models', len(MODELS))
print(sha(CP), 'forecasts-nominal-e217.csv')
print(sha(JP), 'forecasts-nominal-e217.json')
