#!/usr/bin/env python3
"""blind-e221 (Q235) step 3s: a STAND-IN DAY for the scorer's code test (decl-e221's section f: the scorer 'code-tested on a stand-in day
built from the frozen forecasts alone'). Built ONLY from this lane's frozen measured-conditions forecasts (forecasts-blind-e221.json) and the
step 2a conditions (clock, die, minion mV): no E221 measurement exists in it. Per session a data-e221-<s>.json in the reducer's form (top card,
session, primary_view; per run the identity fields, capped, the primary view's kclock_mhz, T_op_us, cyc_op_max, cyc_op_mean, t_pass_s, n_launch,
dP_w, p_mean_w, rails.minion.mV; one null run added per session) and a queue-<s>.json (t_first_ms; per run ran, rc, rcs, check, checks).
  exact: 'measured' = MM1-v3.2's forecast at the run (its errors are 0 by construction; dP_w = its W at its own op time, rest 30 W);
  noise: the same with seeded log-normal noise (cycles 4%, counter mean 3% more, W over idle 6%), 9 runs capped (energy not read), 4 runs
         with a queue rc 1 and 3 with check 'mismatch' (no time read), 2 runs with p_mean_w 0, a W over idle under 3 W on some ones runs.
Desk; stdlib. Run: /usr/bin/python3 -I -B s03s_standin.py <lane dir> <exact|noise>     Writes work/standin/<name>/.
"""
import hashlib
import json
import math
import os
import random
import sys

L = os.path.abspath(sys.argv[1])
NAME = sys.argv[2]
assert NAME in ('exact', 'noise')
OUT = os.path.join(L, 'work', 'standin', NAME)
os.makedirs(OUT, exist_ok=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(os.path.join(L, 'forecasts-blind-e221.json')) == '10dac66160a871ac39453ebf4d7ac42d29c824beca59b2d079bcbbf9878dbebe'
FC = json.load(open(os.path.join(L, 'forecasts-blind-e221.json')))
COND = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e221.json')))
RL = json.load(open(os.path.join(L, 'work', 'decl', 'inputs', 'step1', 'runs-listed.json')))
rng = random.Random(20261120 if NAME == 'noise' else 0)
by_s = {}
for r in RL['runs']:
    by_s.setdefault(r['session'], []).append(r)
allids = [r['id'] for r in RL['runs']]
capped = set(rng.sample(allids, 9)) if NAME == 'noise' else set()
rcbad = set(rng.sample(sorted(set(allids) - capped), 4)) if NAME == 'noise' else set()
chkbad = set(rng.sample(sorted(set(allids) - capped - rcbad), 3)) if NAME == 'noise' else set()
pm0 = set(rng.sample(sorted(set(allids) - capped - rcbad - chkbad), 2)) if NAME == 'noise' else set()
summary = {'name': NAME, 'capped': sorted(capped), 'queue_rc_1': sorted(rcbad), 'check_mismatch': sorted(chkbad), 'p_mean_0': sorted(pm0)}
for s, rs in sorted(by_s.items()):
    sd = COND['sessions'][s]
    pv = sd['primary_view']
    runs, queue = [], []
    for r in rs:
        c = COND['runs'][r['id']]
        F = FC['runs'][r['id']]['v32']
        f = float(c['kclock_mhz'])
        if NAME == 'exact':
            cw, cm = F['cyc_wall'], F['cyc_mean']
            T = F['T_op_us']
            tp = F['sec_pass']
            w = F['W_fc']
        else:
            cw = F['cyc_wall'] * math.exp(rng.gauss(0.0, 0.04))
            cm = cw * (F['cyc_mean'] / F['cyc_wall']) * math.exp(rng.gauss(0.0, 0.03))
            T = cw / f
            tp = r['ops_per_minion_pass'] * T * 1e-6
            w = (F['W_A'] + F['W_B'] / T) * math.exp(rng.gauss(0.0, 0.06))
            if r['kind'] == 'ones' and rng.random() < 0.3:
                w = 2.4
        view = {'kclock_mhz': f, 'T_op_us': T, 'cyc_op_max': cw, 'cyc_op_mean': cm, 't_pass_s': tp, 'n_launch': 10, 'dP_w': w,
                'p_mean_w': (0 if r['id'] in pm0 else 30.0 + w), 'rails': {'minion': {'mV': c['minion_mV']}}}
        runs.append({'run': r['run'], 'i': r['i'], 'ran': True, 'role': r['role'], 'arm': r['arm_label'], 'values': r['values'], 'type': r['fmt'],
                     'shires': r['mask'], 'minions': c['minions'], 'die_start_c': c['die_start_c'], 'capped': r['id'] in capped,
                     'views': {pv: view}})
        rc = 1 if r['id'] in rcbad else 0
        chk = 'mismatch' if r['id'] in chkbad else 'exact'
        queue.append({'run': r['run'], 'i': r['i'], 'ran': True, 'role': r['role'], 'arm': r['arm_label'], 'rc': rc, 'rcs': [rc], 'check': chk, 'checks': [chk]})
    runs.append({'run': '999-null', 'i': 999, 'ran': True, 'role': 'null', 'arm': 'null', 'values': 'null', 'type': None, 'shires': None,
                 'minions': None, 'die_start_c': None, 'views': {}})
    queue.append({'run': '999-null', 'i': 999, 'ran': True, 'role': 'null', 'arm': 'null', 'rc': None, 'rcs': [None], 'check': None, 'checks': [None]})
    dj = {'card': sd['card'], 'session': sd['session'], 'primary_view': pv, 'runs': runs, 'standin': f'blind-e221 stand-in {NAME}: NOT E221 DATA'}
    json.dump(dj, open(os.path.join(OUT, f'data-e221-{s}.json'), 'w'), indent=0)
    json.dump({'t_first_ms': (sd['session_id_epoch'] + 60) * 1000, 'queue': queue, 'standin': True}, open(os.path.join(OUT, f'queue-{s}.json'), 'w'), indent=0)
json.dump(summary, open(os.path.join(OUT, 'standin-summary.json'), 'w'), indent=1)
print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in summary.items()}))
print('stand-in', NAME, 'written to', os.path.relpath(OUT, L), 'sessions', len(by_s))
