#!/usr/bin/env python3
"""unread-e214 (Q225) step 4: a recheck of the verdict's numbers, independent of the scorer's code path: from the forecasts CSV (frozen) and
the committed data files re-read here (GitHub main 8bde0182, `git show`; not the scorer's copies), MM1-v3.1's per-case wall error, T1 and E4
per card over the no-twin cases at the declared bands, the switch test's Q1 rms against N, and one run by hand. Desk; stdlib.
Run: /usr/bin/python3 -I -B s04_recheck.py <lane dir>
"""
import collections
import csv
import json
import math
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
DECL = json.load(open(os.path.join(L, 'DECLARED-unread-e214.json')))
BANDS = DECL['f_pass_rule']['bands']
F = list(csv.DictReader(open(os.path.join(L, 'forecasts-unread-e214.csv'))))
folders = {s: d['folder'] for s, d in json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))['sessions'].items()}
M = {}
for s, fo in folders.items():
    Dj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{fo}/data-e214-{s}.json'], check=True, capture_output=True, env=ENV).stdout)
    pv = Dj['primary_view']
    for r in Dj['runs']:
        v = (r.get('views') or {}).get(pv) or {}
        M[f'E214|{s}|{r["run"]}'] = (v, r)
case_e = collections.defaultdict(list)
case_e4 = collections.defaultdict(list)
case_q1 = collections.defaultdict(list)
twin_t, twin_e, card_of = {}, {}, {}
for f in F:
    v, r = M[f['id']]
    c = (f['card'], f['arm'], f['fmt'], f['kind'], f['mask'])
    card_of[c] = f['card']
    twin_t[c] = f['twin_time_v31'] == '1'
    twin_e[c] = f['twin_energy_v31'] == '1'
    case_e[c].append(float(f['v31_cyc_wall']) / v['cyc_op_max'] - 1)
    if v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped'):
        w, T = v['dP_w'], v['T_op_us']
        rest = v['p_mean_w'] - w
        Wf, Tf = float(f['v31_W_fc']), float(f['v31_T_op_us'])
        case_e4[c].append((rest + Wf) * Tf / ((rest + w) * T) - 1)
        if f['group'] == 'S':
            Wg = float(f['v31_W_A']) + float(f['v31_W_B']) / T
            N = sum(float(f[f'v31_null_{k}_W_A']) + float(f[f'v31_null_{k}_W_B']) / T for k in ('zeros', 'ones', 'random')) / 3.0
            case_q1[c].append((Wg / w - 1, N / w - 1, w))
out = {}
for card in ('aifoundry1 card 1', 'aifoundry1 card 0'):
    es = [sum(v) / len(v) for c, v in case_e.items() if card_of[c] == card and not twin_t[c]]
    e4 = [sum(v) / len(v) for c, v in case_e4.items() if card_of[c] == card and not twin_e[c]]
    out[card] = {'T1': f"{sum(abs(x) <= BANDS[card]['T1'] for x in es)}/{len(es)}", 'E4': f"{sum(abs(x) <= BANDS[card]['E4'] for x in e4)}/{len(e4)}",
                 'wall_rms_no_twin_pct': round(100 * math.sqrt(sum(x * x for x in es) / len(es)), 3)}
q1 = [(sum(a for a, _, _ in v) / len(v), sum(b for _, b, _ in v) / len(v)) for c, v in case_q1.items() if sum(w for _, _, w in v) / len(v) >= 3.0]
out['Q1'] = {'cases': len(q1), 'v31_rms_pct': round(100 * math.sqrt(sum(a * a for a, _ in q1) / len(q1)), 3),
             'N_rms_pct': round(100 * math.sqrt(sum(b * b for _, b in q1) / len(q1)), 3),
             'closer_v31': sum(1 for a, b in q1 if abs(b) - abs(a) >= 0.01), 'closer_N': sum(1 for a, b in q1 if abs(b) - abs(a) <= -0.01)}
# one run by hand
rid = 'E214|a1c1-S2|034-1x1x1-fp32-sp_ar4'
f = [x for x in F if x['id'] == rid][0]
v, r = M[rid]
Wg = float(f['v31_W_A']) + float(f['v31_W_B']) / v['T_op_us']
out['one_run_by_hand'] = {'id': rid, 'e_wall': float(f['v31_cyc_wall']) / v['cyc_op_max'] - 1, 'W_given_t': Wg, 'meas_dP_w': v['dP_w'],
                          'e_E1': Wg / v['dP_w'] - 1, 'clock_equal_to_conditions': v['kclock_mhz'] == float(f['f_mhz'])}
json.dump(out, open(os.path.join(L, 'work', 'step3', 'recheck.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out, indent=1))
