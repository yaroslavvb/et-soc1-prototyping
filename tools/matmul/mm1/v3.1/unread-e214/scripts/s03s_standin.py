#!/usr/bin/env python3
"""unread-e214 (Q225) step 3s: a STAND-IN day for testing the scorer before the real read. Built from the frozen forecasts and the
conditions only (no E214 measurement): every listed run gets a primary view whose cycles and op time are MM1-v3.1's forecast x exp(N(0, 0.04))
and whose W over idle is MM1-v3.1's W given that op time x exp(N(0, 0.05)), the rest 30 W; three runs capped (energy not read). The scorer is run
on it with --standin; its verdicts are code checks only, never a result. Run: /usr/bin/python3 -I -B s03s_standin.py <lane dir> <out dir>
"""
import json
import math
import os
import random
import sys

L = os.path.abspath(sys.argv[1])
OUTD = os.path.abspath(sys.argv[2])
os.makedirs(OUTD, exist_ok=True)
FCJ = json.load(open(os.path.join(L, 'forecasts-unread-e214.json')))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
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
        g = math.exp(rnd.gauss(0, 0.04))
        cw = v31['cyc_wall'] * g
        T = cw / f
        ops = F['ops_minion_gemm']
        Wg = v31['W_A'] + v31['W_B'] / T
        w = Wg * math.exp(rnd.gauss(0, 0.05))
        cap = (r['card'] == 'aifoundry1 card 0' and len(capped) < 3 and rnd.random() < 0.05)
        if cap:
            capped.add(r['id'])
        view = {'n_launch': 3, 'T_op_us': T, 'cyc_op_max': cw, 'cyc_op_mean': v31['cyc_mean'] * g, 'kclock_mhz': f, 't_pass_s': T * ops * 1e-6,
                'dP_w': w, 'p_mean_w': w + 30.0, 'rails': {'minion': {'mV': F['minion_mV']}}}
        runs.append({'run': r['run'], 'i': r['i'], 'ran': True, 'role': r['role'], 'arm': r['arm_label'], 'values': r['values'], 'type': r['fmt'],
                     'shires': r['mask'], 'minions': r['minions'], 'die_start_c': F['die_start_c'], 'capped': cap, 'views': {pv: view}})
    D = {'card': RL['sessions'][s]['card_key'], 'session': RL['sessions'][s]['sid'], 'primary_view': pv, 'runs': runs, 'STANDIN': True}
    json.dump(D, open(os.path.join(OUTD, f'data-e214-{s}.json'), 'w'))
print('stand-in sessions', len(by), 'runs', sum(len(v) for v in by.values()), 'capped', sorted(capped))
