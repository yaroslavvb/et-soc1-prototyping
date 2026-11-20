#!/usr/bin/env python3
"""blind-e219 (Q232) step 4: an INDEPENDENT CODE PATH for the deciding numbers, after the score (a check, deciding nothing). It reads the
frozen forecasts from forecasts-blind-e219.csv (the CSV, not the JSON the scorer read), the measurements by a fresh `git show` of the five
committed data-e219-<s>.json and session queues (into memory only), the bands, ties and run list from decl-e219's declaration and run list;
selects the runs by the declared conditions with its own code; and re-makes: part A per card (T1, T2, T3, E1, E2, E3, E4: passes / cases
over MM1-v3.1's no-twin in-domain cases, the verdict), the no-twin pooled rms of MM1-v3.1, MM1-v3 and MM1-v2 (wall, E1 relative, E3), and the
D1 / D2 sign-test tallies on H1 and H4 (pooled), then compares each with the scorer's scores-blind-e219.json. Desk; stdlib.
Run: /usr/bin/python3 -I -B s04_recheck.py <lane dir>
"""
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections import defaultdict

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='<GITHUB_SSH_PREFIX>')
DEC = os.path.join(L, 'work', 'decl')
assert hashlib.sha256(open(os.path.join(L, 'forecasts-blind-e219.csv'), 'rb').read()).hexdigest() == \
    '6ebeb3951b6bd023b2771717bb9b63b00eae7ea4d8e5dfed162cbe384a104e5b'
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e219.json')))
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
SC = json.load(open(os.path.join(L, 'work', 'step3', 'scores-blind-e219.json')))
BANDS = DECL['f_pass_rule']['bands']
TIES = DECL['d_comparisons']['ties']
FC = {r['id']: r for r in csv.DictReader(open(os.path.join(L, 'forecasts-blind-e219.csv')))}
FOLDER = {s: f'docs/reports/data/2026-11-19-e219-mmsweep5-{s}' for s in RL['sessions']}
meas = {}
for s, fo in FOLDER.items():
    Dj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{fo}/data-e219-{s}.json'], check=True, capture_output=True, env=ENV).stdout)
    Qj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{fo}/session/queue.json'], check=True, capture_output=True, env=ENV).stdout)
    qmap = {q['run']: q for q in Qj['queue'] if 'run' in q}
    pv = Dj['primary_view']
    for x in Dj['runs']:
        rid = f"E219|{s}|{x['run']}"
        if rid not in FC:
            continue
        v = x.get('views', {}).get(pv, {})
        q = qmap.get(x['run'], {})
        ok = (x.get('ran') is True and x.get('role') in ('arm', 'anchor') and bool(x.get('shires')) and bool(v.get('T_op_us'))
              and bool(v.get('cyc_op_max')) and (v.get('n_launch') or 0) >= 1 and q.get('ran') is True and set(q.get('rcs') or [None]) == {0}
              and set(q.get('checks') or [None]) <= {'exact', 'approx'} and q.get('rc') == 0 and q.get('check') in ('exact', 'approx')
              and (str(x.get('values', '')).startswith('gemmL') or x.get('ops_pass_ok') is True)
              and str(x.get('values', '')).split(':')[0] == FC[rid]['token'])
        e = ok and v.get('dP_w') is not None and bool(v.get('p_mean_w')) and not x.get('capped') and x.get('role') != 'time'
        meas[rid] = {'ok': ok, 'e': e, 'T': v.get('T_op_us'), 'cw': v.get('cyc_op_max'), 'cm': v.get('cyc_op_mean'), 'tp': v.get('t_pass_s'),
                     'w': v.get('dP_w'), 'pm': v.get('p_mean_w')}
by_case = defaultdict(list)
for rid, r in FC.items():
    if r['domain'] == 'IN':
        by_case[r['case'] if 'case' in r else None].append(rid)
# the CSV has no case column: rebuild it from the run list
case_of = {r['id']: r['case'] for r in RL['runs']}
by_case = defaultdict(list)
for rid, r in FC.items():
    if r['domain'] == 'IN':
        by_case[case_of[rid]].append(rid)


def g(r, k):
    return float(r[k])


def case_err(rids, m):
    """per case: the mean of its runs' errors for wall, mean, sec, E1 (rel), dE1 (W), E2, dE2, E3, E4, and the watts flag"""
    out = defaultdict(list)
    wg31, ws = [], []
    for rid in rids:
        M = meas[rid]
        if not M['ok']:
            continue
        r = FC[rid]
        out['wall'].append(g(r, f'{m}_cyc_wall') / M['cw'] - 1)
        out['mean'].append(g(r, f'{m}_cyc_mean') / M['cm'] - 1)
        out['sec'].append(g(r, f'{m}_sec_pass') / M['tp'] - 1)
        if M['e']:
            A, B, Wf, Tf = g(r, f'{m}_W_A'), g(r, f'{m}_W_B'), g(r, f'{m}_W_fc'), g(r, f'{m}_T_op_us')
            Wg = A + B / M['T']
            rest = M['pm'] - M['w']
            out['E1'].append(Wg / M['w'] - 1)
            out['dE1'].append(Wg - M['w'])
            out['E2'].append(Wf * Tf / (M['w'] * M['T']) - 1)
            out['dE2'].append(Wf - M['w'])
            out['E3'].append((rest + Wg) / (rest + M['w']) - 1)
            out['E4'].append((rest + Wf) * Tf / ((rest + M['w']) * M['T']) - 1)
            wg31.append(g(r, 'v31_W_A') + g(r, 'v31_W_B') / M['T'])
            ws.append(M['w'])
    res = {k: sum(v) / len(v) for k, v in out.items() if v}
    if ws:
        res['watts'] = (sum(wg31) / len(wg31) < 3.0) or (sum(ws) / len(ws) < 3.0)
    return res


CASE = {c['case']: c for c in RL['cases'] if c['domain'] == 'IN'}
ERR = {m: {c: case_err(rids, m) for c, rids in by_case.items()} for m in ('v31', 'v3', 'v2')}


def twin(c, kind, m):
    return FC[by_case[c][0]][f'twin_{kind}_{m}'] == '1'


mine = {'partA': {}, 'rms': {}, 'D': {}}
RQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}
for card in ('aifoundry1 card 1', 'aifoundry1 card 0'):
    for rule, q in RQ.items():
        npass = n = 0
        for c, x in ERR['v31'].items():
            if CASE[c]['card'] != card or q not in x:
                continue
            if twin(c, 'time' if q in ('wall', 'mean', 'sec') else 'energy', 'v31'):
                continue
            n += 1
            if q in ('E1', 'E2') and x['watts']:
                npass += abs(x['d' + q]) <= BANDS[card]['watts_W']
            else:
                npass += abs(x[q]) <= BANDS[card][rule]
        v = 'NO DATA' if n == 0 else ('TOO FEW' if n < 10 else ('PASS' if npass >= 0.9 * n else 'FAIL'))
        mine['partA'][f'{card} {rule}'] = [v, npass, n]
for m in ('v31', 'v3', 'v2'):
    for q in ('wall', 'E1', 'E3'):
        vals = [x[q] for c, x in ERR[m].items() if q in x and not twin(c, 'time' if q == 'wall' else 'energy', m)
                and not (q == 'E1' and x['watts'])]
        mine['rms'][f'{m} {q}'] = [len(vals), round(100 * math.sqrt(sum(e * e for e in vals) / len(vals)), 3)]
for nm, (a, b) in (('D1', ('v31', 'v3')), ('D2', ('v31', 'v2'))):
    for h, q in (('H1', 'wall'), ('H4', 'E1')):
        k = kk = t = 0
        for c in ERR[a]:
            xa, xb = ERR[a][c], ERR[b][c]
            if q not in xa or q not in xb:
                continue
            tie = TIES[CASE[c]['card']]
            if q == 'E1' and xa['watts']:
                d, tt = abs(xb['dE1']) - abs(xa['dE1']), tie['watts_W']
            else:
                d = abs(math.log(1 + xb[q])) - abs(math.log(1 + xa[q]))
                tt = tie['cycles_ln'] if q == 'wall' else tie['joules_ln']
            if d > tt:
                k += 1
            elif d < -tt:
                kk += 1
            else:
                t += 1
        mine['D'][f'{nm} {h} pooled'] = [k, kk, t]
P = SC['primary_footing']
theirs = {'partA': {f'{card} {rule}': [x['verdict'], x['pass'], x['n']] for card, rr in P['part_A']['v31'].items() for rule, x in rr.items()},
          'rms': {}, 'D': {}}
for m in ('v31', 'v3', 'v2'):
    for q in ('wall', 'E1', 'E3'):
        cell = P['tables_per_case'][m][q]['pooled']['no_twin']
        cell = cell['relative'] if q == 'E1' else cell
        theirs['rms'][f'{m} {q}'] = [cell['n'], cell['rms_pct']]
for nm, key in (('D1', 'D1 MM1-v3.1 vs MM1-v3'), ('D2', 'D2 MM1-v3.1 vs MM1-v2')):
    for h in ('H1', 'H4'):
        z = P['comparisons'][key][h]['pooled']
        theirs['D'][f'{nm} {h} pooled'] = [z['closer_A'], z['closer_B'], z['ties']]
diff = {sec: {k: (mine[sec][k], theirs[sec].get(k)) for k in mine[sec] if mine[sec][k] != theirs[sec].get(k)} for sec in mine}
res = {'what': 'blind-e219 step 4: an independent code path for the deciding numbers', 'mine': mine, 'scorer': theirs, 'differences': diff,
       'ALL_EQUAL': all(not v for v in diff.values()),
       'runs_selected_time': sum(1 for rid, M in meas.items() if M['ok'] and FC[rid]['domain'] == 'IN'),
       'runs_selected_energy': sum(1 for rid, M in meas.items() if M['e'] and FC[rid]['domain'] == 'IN')}
os.makedirs(os.path.join(L, 'work', 'step4'), exist_ok=True)
json.dump(res, open(os.path.join(L, 'work', 'step4', 'recheck-e219.json'), 'w'), indent=1, sort_keys=True)
print('part A', json.dumps(mine['partA']))
print('rms', json.dumps(mine['rms']))
print('D', json.dumps(mine['D']))
print('in-domain runs selected: time', res['runs_selected_time'], 'energy', res['runs_selected_energy'])
print('ALL EQUAL to the scorer' if res['ALL_EQUAL'] else 'DIFFERENCES: ' + json.dumps(diff))
