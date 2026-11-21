#!/usr/bin/env python3
"""decl-e221 (Q235) step 2c: write the frozen nominal forecasts, forecasts-nominal-e221.csv (one row a case and model; E221 has no
out-of-domain case) and forecasts-nominal-e221.json (meta + every field of work/step2/fc-nominal.json), at the lane root. Reads only
this lane's step-2 output and the declaration (its sha256 recorded in the meta). Desk. decl-e219's s02c_write.py in form.
Run: /usr/bin/python3 -I -B s02c_write.py <lane dir>"""
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
MODELS = FC['models']
made = subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()
meta = {'what': "decl-e221: E221's NOMINAL forecasts by every declared model, frozen before any E221 datum (the declaration's section h)",
        'written_pst': made, 'declaration_md_sha256': sha(os.path.join(L, 'DECLARED-blind-e221.md')),
        'declaration_json_sha256': sha(os.path.join(L, 'DECLARED-blind-e221.json')),
        'fc_nominal_sha256': sha(os.path.join(L, 'work', 'step2', 'fc-nominal.json')),
        'runs_listed_sha256': sha(os.path.join(L, 'work', 'step1', 'runs-listed.json')),
        'walk_feats_sha256': sha(os.path.join(L, 'work', 'step2', 'walk-feats-e221.json')),
        'cand_feats_sha256': sha(os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')),
        'models_reported': FC['models_reported'], 'candidates': FC['candidates'], 'l3s_ratio_range_full_mask': FC['l3s_ratio_range_full_mask'],
        'nominal_conditions': FC['nominal'], 'models': MODELS, 'controls_constants': FC['controls_constants'], 'a_fresh': FC['a_fresh'],
        'checks': FC['checks'], 'factor_ranges_subset_only': FC['factor_ranges_subset_only'], 'energy_status': FC['energy_status'],
        'python': FC['python'], 'numpy': FC['numpy'], 'sha256sum_c': FC['sha256sum_c'], 'n_cases': FC['n_cases'],
        'n_in_domain': FC['n_cases'], 'n_out_of_domain': 0,
        'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E221 (it equals MM1-v3.1 on every case)',
        'MM1-v3.2+AF4': 'NOT APPLICABLE: no gemmLnc arm in E221 (it equals MM1-v3.2 on every case)',
        'out_of_domain': 'none: every E221 case is rgm136 gemmL, in every declared model\'s domain (the declaration, section 0)',
        'units': {'T_op_us': 'microseconds an op (a minion)', 'cycles': 'cycles an op', 'seconds_per_pass': 's (ops a minion a pass x T_op)',
                  'W': 'W over idle', 'W_B_us': 'W x us (W over idle at a measured op time t is W_A + W_B_us / t)',
                  'J_over_idle_per_pass': 'J (W over idle at the model\'s own op time x its seconds a pass)'}}
out = {'meta': meta, 'cases': FC['cases'], 'layout_blind_groups': FC['layout_blind_groups']}
JP = os.path.join(L, 'forecasts-nominal-e221.json')
json.dump(out, open(JP, 'w'), indent=1, sort_keys=True)
CP = os.path.join(L, 'forecasts-nominal-e221.csv')
cols = ['case', 'card', 'token', 'fmt', 'kind', 'mask', 'n_shires', 'domain', 'class', 'subfamily', 'group_mask', 'ops_per_minion_pass', 'n_runs', 'model', 'reported',
        'f_mhz', 'V', 'die_start_c', 'T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_pass', 'energy', 'W_A', 'W_B_us',
        'W_over_idle_own_t', 'J_over_idle_per_pass', 'rest_law_W', 'factor', 'phi_fresh']


def g(x, k, f='%.9g'):
    v = x.get(k)
    return '' if v is None else (f % v if isinstance(v, float) else str(v))


n = 0
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for case, o in FC['cases'].items():
        c = CASE[case]
        base = [case, c['card'], c['token'], c['fmt'], c['kind'], c['mask'], c['n_shires'], 'IN', c['class'], c['subfamily'] or '', c['group_mask'],
                c['ops_per_minion_pass'], len(c['runs'])]
        if 'OUT_OF_DOMAIN' in o:
            tail = ['ALL', '', '', '', 'NOT FORECAST (OUT OF DOMAIN)', '', '', '', 'NOT FORECAST (OUT OF DOMAIN)', '', '', '', '', '', '', '']
            assert len(base) + len(tail) == len(cols)
            w.writerow(base + tail)
            n += 1
            continue
        for m in MODELS:
            x = o[m]
            en = 'FORECAST' if x['energy'] == 'FORECAST' else x['energy']
            w.writerow(base + [m, ('REPORTED' if m in FC['models_reported'] else ''), g(x, 'f_mhz'), g(x, 'V'), g(x, 'die_start_c'), g(x, 'T_op_us'), g(x, 'cyc_wall'), g(x, 'cyc_mean'),
                               g(x, 'sec_pass'), en, g(x, 'W_A'), g(x, 'W_B'), g(x, 'W_fc'), g(x, 'J_over_idle_pass'), g(x, 'rest_law_W'),
                               g(x, 'factor'), g(x, 'phi_fresh')])
            n += 1
print('rows', n, 'cases', len(FC['cases']), 'models', len(MODELS))
print(sha(CP), 'forecasts-nominal-e221.csv')
print(sha(JP), 'forecasts-nominal-e221.json')
