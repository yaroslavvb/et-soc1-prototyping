#!/usr/bin/env python3
"""blind-e217 (Q228) step 3s: STAND-IN days for testing the scorer before the real read, built from the frozen measured-conditions
forecasts and the conditions only (no E217 measurement). Every listed run gets a primary view whose cycles and op time are MM1-v3.1's
forecast x g and whose W over idle is MM1-v3.1's W at that op time x h, the rest 30 W, plus the null runs' placeholders (role null, no view),
which every selection must skip. Modes: 'noise' (g = exp(N(0, 0.04)), h = exp(N(0, 0.05)), three card-0 runs capped: energy not read) and
'exact' (g = h = 1, nothing capped: MM1-v3.1's errors are 0, so part A must PASS, MM1-v3.1 must be closer than MM1-v3 and the null N).
The scorer is run on each with --standin; its verdicts are code checks only, never a result.
Run: /usr/bin/python3 -I -B s03s_standin.py <lane dir> <out dir> <noise|exact>
"""
import json
import math
import os
import random
import sys

L = os.path.abspath(sys.argv[1])
OUTD = os.path.abspath(sys.argv[2])
MODE = sys.argv[3]
assert MODE in ('noise', 'exact')
os.makedirs(OUTD, exist_ok=True)
FCJ = json.load(open(os.path.join(L, 'forecasts-blind-e217.json')))
COND = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e217.json')))
RL = json.load(open(os.path.join(L, 'work', 'decl', 'inputs', 'step1', 'runs-listed.json')))
rnd = random.Random(20261119)
by = {}
for r in RL['runs']:
    by.setdefault(r['session'], []).append(r)
capped = set()
for s, rs in sorted(by.items()):
    pv = RL['sessions'][s]['primary_view']
    runs = []
    for r in rs:
        F = FCJ['runs'][r['id']]
        v31 = F['v31']
        f = F['f_mhz']
        g = 1.0 if MODE == 'exact' else math.exp(rnd.gauss(0, 0.04))
        cw = v31['cyc_wall'] * g
        T = cw / f
        ops = F['ops_minion_gemm']
        Wg = v31['W_A'] + v31['W_B'] / T
        w = Wg * (1.0 if MODE == 'exact' else math.exp(rnd.gauss(0, 0.05)))
        cap = (MODE == 'noise' and r['card'] == 'aifoundry1 card 0' and len(capped) < 3 and rnd.random() < 0.05)
        if cap:
            capped.add(r['id'])
        view = {'n_launch': 3, 'T_op_us': T, 'cyc_op_max': cw, 'cyc_op_mean': v31['cyc_mean'] * g, 'kclock_mhz': f, 't_pass_s': T * ops * 1e-6,
                'dP_w': w, 'p_mean_w': w + 30.0, 'rails': {'minion': {'mV': F['minion_mV']}}}
        runs.append({'run': r['run'], 'i': r['i'], 'ran': True, 'role': r['role'], 'arm': r['arm_label'], 'values': r['values'], 'type': r['fmt'],
                     'shires': r['mask'], 'minions': r['minions'], 'die_start_c': F['die_start_c'], 'capped': cap, 'views': {pv: view}})
    for j in range(2):
        runs.append({'run': f'9{j:02d}-null', 'i': 900 + j, 'ran': True, 'role': 'null', 'arm': None, 'values': None, 'type': None, 'shires': None,
                     'minions': None, 'die_start_c': None, 'capped': False, 'views': {}})
    D = {'card': RL['sessions'][s]['card_key'], 'session': COND['sessions'][s]['session'], 'primary_view': pv, 'runs': runs, 'STANDIN': True}
    json.dump(D, open(os.path.join(OUTD, f'data-e217-{s}.json'), 'w'))
print('stand-in', MODE, 'sessions', len(by), 'runs', sum(len(v) for v in by.values()), 'capped', sorted(capped))
