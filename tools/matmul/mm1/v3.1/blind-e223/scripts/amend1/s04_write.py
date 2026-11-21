#!/usr/bin/env python3
"""amend-e223 (Q239a) step 4: write the amendment's frozen nominal forecasts, forecasts-nominal-e223-amend1.csv (one row a case and model,
decl-e223's forecasts-nominal-e223.csv columns) and forecasts-nominal-e223-amend1.json (meta + every field of work/step3/fc-amend1.json), at
the lane root. Reads only this lane's step-3 output, the declaration's case list and the amendment (its sha256 in the meta). decl-e223's
s02c_write.py in form. Run: /usr/bin/python3 -I -B s04_write.py <lane dir>"""
import csv
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
OUT = os.path.dirname(L)
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


FC = json.load(open(os.path.join(L, 'work', 'step3', 'fc-amend1.json')))
RLP = os.path.join(OUT, 'decl-e223', 'work', 'step1', 'runs-listed.json')
assert sha(RLP) == 'ed4595b10697daa0d1923d3fcaca2a04b295e6ccdd0dc2e87e5f77448330004d'
RL = json.load(open(RLP))
CASE = {c['case']: c for c in RL['cases']}
assert FC['n_cases'] == len(CASE) == 695 and not FC['test_run']
MODELS = FC['models']
assert FC['amendment_sha256'] == {f: sha(os.path.join(L, f)) for f in ('DECLARED-blind-e223-amendment-1.md', 'DECLARED-blind-e223-amendment-1.json')}
made = subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()
meta = {'what': "amend-e223: E223's NOMINAL forecasts by the three columns DECLARED-blind-e223-amendment-1 adds (REPORTED), frozen before any "
                "E223 datum (the amendment's section h; the declaration's nominal conditions)",
        'written_pst': made, 'amendment_md_sha256': FC['amendment_sha256']['DECLARED-blind-e223-amendment-1.md'],
        'amendment_json_sha256': FC['amendment_sha256']['DECLARED-blind-e223-amendment-1.json'],
        'declaration_FROZEN_txt': '5551c2d7b7b6b5bc40526997a2d8bcbfe62fc8b1468da514781fa59d7543b850',
        'fc_amend1_sha256': sha(os.path.join(L, 'work', 'step3', 'fc-amend1.json')), 'runs_listed_sha256': sha(RLP),
        'models': MODELS, 'models_reported': MODELS, 'reference_not_candidate': ['MM1-v3.2 + mask-ceiling'], 'candidates': FC['candidates'],
        'nominal_conditions': FC['nominal'], 'checks': FC['checks'], 'scope': FC['scope'], 'factor_ranges': FC['factor_ranges'],
        'frozen_files_checked': FC['frozen_files_checked'], 'sha256sum_c': FC['sha256sum_c'], 'python': FC['python'], 'numpy': FC['numpy'],
        'n_cases': FC['n_cases'], 'n_in_domain': FC['n_cases'], 'n_out_of_domain': 0, 'made_started_pst': FC['started_pst'],
        'made_ended_pst': FC['ended_pst'],
        'MM1-v3.2': "the declaration's frozen column (forecasts-nominal-e223.json), re-made by mm1_v32.Model.predict_many at the declaration's "
                    "specs and checked equal at every case (worst relative difference 0.0); not repeated here",
        'units': {'T_op_us': 'microseconds an op (a minion)', 'cycles': 'cycles an op', 'seconds_per_pass': 's (ops a minion a pass x T_op)',
                  'W': 'W over idle', 'W_B_us': 'W x us (W over idle at a measured op time t is W_A + W_B_us / t)',
                  'J_over_idle_per_pass': "J (W over idle at the model's own op time x its seconds a pass)"}}
out = {'meta': meta, 'cases': FC['cases'], 'made_keys': FC['made_keys']}
JP = os.path.join(L, 'forecasts-nominal-e223-amend1.json')
CP = os.path.join(L, 'forecasts-nominal-e223-amend1.csv')
assert not os.path.exists(JP) and not os.path.exists(CP), 'the forecasts exist already: never rewritten'
json.dump(out, open(JP, 'w'), indent=1, sort_keys=True)
cols = ['case', 'card', 'token', 'arm_label', 'fmt', 'kind', 'mask', 'n_shires', 'domain', 'class', 'ho_sets', 'maske221', 'gateset',
        'group_mask', 'ops_per_minion_pass', 'n_runs', 'model', 'reported', 'f_mhz', 'V', 'die_start_c', 'T_op_us', 'cycles_per_op_wall',
        'cycles_per_op_mean', 'seconds_per_pass', 'energy', 'W_A', 'W_B_us', 'W_over_idle_own_t', 'J_over_idle_per_pass', 'rest_law_W',
        'factor_vs_MM1-v3.2', 'term_in_scope']


def g(x, k, f='%.9g'):
    v = x.get(k)
    return '' if v is None else (f % v if isinstance(v, float) else str(v))


def scope(x):
    for k in ('in_scope_mesh', 'in_scope_ceiling'):
        if k in x:
            return str(bool(x[k]))
    return ''


n = 0
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for case, o in FC['cases'].items():
        c = CASE[case]
        base = [case, c['card'], c['token'], c['arm_label'], c['fmt'], c['kind'], c['mask'], c['n_shires'], 'IN', c['class'], '+'.join(c['ho_sets']),
                c['maske221'], c['gateset'], c['group_mask'], c['ops_per_minion_pass'], len(c['runs'])]
        for m in MODELS:
            x = o[m]
            w.writerow(base + [m, ('REPORTED (reference)' if m == 'MM1-v3.2 + mask-ceiling' else 'REPORTED'), g(x, 'f_mhz'), g(x, 'V'),
                               g(x, 'die_start_c'), g(x, 'T_op_us'), g(x, 'cyc_wall'), g(x, 'cyc_mean'), g(x, 'sec_pass'), x['energy'], g(x, 'W_A'),
                               g(x, 'W_B'), g(x, 'W_fc'), g(x, 'J_over_idle_pass'), g(x, 'rest_law_W'), g(x, 'factor'), scope(x)])
            n += 1
os.chmod(JP, 0o444)
os.chmod(CP, 0o444)
print('rows', n, 'cases', len(FC['cases']), 'models', len(MODELS))
print(sha(CP), 'forecasts-nominal-e223-amend1.csv')
print(sha(JP), 'forecasts-nominal-e223-amend1.json')
print('written', made)
