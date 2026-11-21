#!/usr/bin/env python3
"""mask-posimb (Q238) g02 (REPORTED, never deciding; DECLARED-posimb-mask.md section 7): the counter's mean cycles an op at E221's 363 headline
MASK cases: MM1-v3.2's mean (mm1_v32 predict_many at each case's clock) against the measured mean (blind-e221's case table meas_cyc_mean), and
the term's g_m = clip(1 + a_hop e G1core + a_al e A1, 0.3, 3.0) at each LOSO fold's constants (held out) and at the all-data constants (in
sample), through the frozen module staged in the lane's clone. Desk; numpy; single-threaded. Output: work/g02_mean.json."""
import csv
import json
import os
import sys

import numpy as np

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
STAGE = os.path.join(LAB, 'tools/matmul/mm1/v3.4-cands/posimb-mask')
sys.path.insert(0, STAGE)
import posimb_mask as PM  # noqa: E402

F = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
cases = {}
for c in csv.DictReader(open(os.path.join(LAB, 'tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-cases.csv'))):
    cases[c['case']] = c
head = [p for p in P if p['exp'] == 'E221' and p['cls221'] == 'MASK' and not p['twin_v32_e221']]
M = PM.Model()
specs = [{'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'], 'mask': p['mask'], 'f': float(p['f']), 'kernel': 'rgm136'} for p in head]
rows = M.predict_many(specs)
meas = np.array([float(cases[p['id'].split('|', 2)[2]]['meas_cyc_mean']) if cases[p['id'].split('|', 2)[2]]['meas_cyc_mean'] not in ('', 'None') else np.nan
                 for p in head])
v32m = np.array([r['MM1-v3.2']['cycles_per_op_mean'] for r in rows])
ins = np.array([r[PM.LABEL]['cycles_per_op_mean'] for r in rows])
phi = np.array([[r['term']['Phi_hop'], r['term']['Phi_lag'], r['term']['Phi_al']] for r in rows])
held = np.zeros(len(head))
cnt = np.zeros(len(head))
for k, a in F['constants_by_fold']['cand'].items():
    if not k.startswith('LOSO '):
        continue
    s = k.split(' ', 1)[1]
    for i, p in enumerate(head):
        if s in p['sessions']:
            gm = np.clip(1.0 + a[0] * phi[i, 0] + a[2] * phi[i, 2], 0.3, 3.0) if rows[i]['in_scope'] else 1.0
            held[i] += v32m[i] * gm
            cnt[i] += 1
held /= cnt
ok = ~np.isnan(meas)


def r(x):
    e = x[ok] / meas[ok] - 1
    return [float(100 * np.sqrt(np.mean(e ** 2))), float(100 * np.mean(e)), int(ok.sum())]


out = {'what': "the counter's mean at E221's 363 headline MASK cases (REPORTED)", 'MM1-v3.2': r(v32m), 'posimb-mask LOSO held out': r(held),
       'posimb-mask all-data in sample': r(ins)}
json.dump(out, open(os.path.join(LANE, 'work/g02_mean.json'), 'w'), indent=1)
print(json.dumps(out))
