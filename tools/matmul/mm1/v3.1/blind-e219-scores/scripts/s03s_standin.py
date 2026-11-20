#!/usr/bin/env python3
"""blind-e219 (Q232) step 3s: STAND-IN days for testing the scorer before the real read, built from the frozen measured-conditions
forecasts and the conditions only (no E219 measurement). Every listed in-domain run gets a primary view whose cycles and op time are
MM1-v3.1's forecast x g and whose W over idle is MM1-v3.1's W at that op time x h, the rest 30 W; every out-of-domain run a made-up view
(1,000 cycles an op x g, 10 W); every block, stream and TenB run its grammar fields (arm_token, arm_family, ops_pass, ops_pass_ok); the null
runs' placeholders (role null, no view), which every selection must skip; and a stand-in queue (ran, rc, check per run; t_first_ms 10 s
after the session's T0). Modes: 'noise' (g = exp(N(0, 0.04)), h = exp(N(0, 0.05)); three card-0 runs capped: energy not read; one
in-domain run with rc 1 and one with check 'mismatch': both left out by the queue condition; one run 'approx': kept) and 'exact'
(g = h = 1, nothing capped, every check exact: MM1-v3.1's errors are 0, so part A must PASS). The scorer is run on each with --standin;
its verdicts are code checks only, never a result. blind-e217's s03s_standin.py in form.
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
FCJ = json.load(open(os.path.join(L, 'forecasts-blind-e219.json')))
COND = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e219.json')))
RL = json.load(open(os.path.join(L, 'work', 'decl', 'inputs', 'step1', 'runs-listed.json')))
rnd = random.Random(20261120)
by = {}
for r in RL['runs']:
    by.setdefault(r['session'], []).append(r)
capped, qbad, qapprox = set(), {}, set()
for s, rs in sorted(by.items()):
    pv = RL['sessions'][s]['primary_view']
    runs, queue = [], []
    for r in rs:
        F = FCJ['runs'][r['id']]
        f = F['f_mhz']
        g = 1.0 if MODE == 'exact' else math.exp(rnd.gauss(0, 0.04))
        ops = F['ops_per_minion_pass']
        if r['domain'] == 'IN':
            v31 = F['v31']
            cw, cm = v31['cyc_wall'] * g, v31['cyc_mean'] * g
            T = cw / f
            Wg = v31['W_A'] + v31['W_B'] / T
            w = Wg * (1.0 if MODE == 'exact' else math.exp(rnd.gauss(0, 0.05)))
        else:
            cw = cm = 1000.0 * g
            T = cw / f
            w = 10.0
        cap = (MODE == 'noise' and r['card'] == 'aifoundry1 card 0' and len(capped) < 3 and rnd.random() < 0.05)
        if cap:
            capped.add(r['id'])
        view = {'n_launch': 3, 'T_op_us': T, 'cyc_op_max': cw, 'cyc_op_mean': cm, 'kclock_mhz': f, 't_pass_s': T * ops * 1e-6,
                'dP_w': w, 'p_mean_w': w + 30.0, 'rails': {'minion': {'mV': F['minion_mV']}}}
        x = {'run': r['run'], 'i': r['i'], 'ran': True, 'role': r['role'], 'arm': r['arm_label'], 'values': r['values'], 'type': r['fmt'],
             'shires': r['mask'], 'minions': r['minions'], 'die_start_c': F['die_start_c'], 'capped': cap, 'primary_view': pv, 'views': {pv: view}}
        if not str(r['values']).startswith('gemmL'):
            x.update({'arm_token': r['token'], 'arm_family': (r['shape'] or {}).get('family'), 'ops_pass': ops, 'ops_pass_ok': True})
        runs.append(x)
        q = {'i': r['i'], 'run': r['run'], 'arm': r['arm_label'], 'role': r['role'], 'ran': True, 'rc': 0, 'rcs': [0], 'check': 'exact', 'checks': ['exact']}
        if MODE == 'noise' and r['domain'] == 'IN' and len(qbad) < 2 and rnd.random() < 0.03:
            if not qbad:
                q.update({'rc': 1, 'rcs': [1]})
                qbad[r['id']] = 'rc 1'
            else:
                q.update({'check': 'mismatch', 'checks': ['mismatch']})
                qbad[r['id']] = 'check mismatch'
        elif MODE == 'noise' and not qapprox and r['domain'] == 'IN' and rnd.random() < 0.05:
            q.update({'check': 'approx', 'checks': ['approx']})
            qapprox.add(r['id'])
        queue.append(q)
    for j in range(2):
        runs.append({'run': f'9{j:02d}-null', 'i': 900 + j, 'ran': True, 'role': 'null', 'arm': None, 'values': None, 'type': None, 'shires': None,
                     'minions': None, 'die_start_c': None, 'capped': False, 'views': {}})
    D = {'card': RL['sessions'][s]['card_key'], 'session': COND['sessions'][s]['session'], 'primary_view': pv, 'runs': runs, 'STANDIN': True}
    json.dump(D, open(os.path.join(OUTD, f'data-e219-{s}.json'), 'w'))
    Q = {'t0': COND['sessions'][s]['session_id_epoch'], 'STANDIN': True, 'queue': queue,
         't_first_ms': (COND['sessions'][s]['session_id_epoch'] + 10) * 1000}
    json.dump(Q, open(os.path.join(OUTD, f'queue-{s}.json'), 'w'))
print('stand-in', MODE, 'sessions', len(by), 'runs', sum(len(v) for v in by.values()), 'capped', sorted(capped), 'queue left out', qbad,
      'approx kept', sorted(qapprox))
