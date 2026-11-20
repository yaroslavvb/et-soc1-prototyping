#!/usr/bin/env python3
"""blind-e217 (Q228) step 4: a RECHECK of the verdict's numbers, independent of the scorer's code path: from the frozen forecasts CSV
(forecasts-blind-e217.csv) and the committed data files re-read here (GitHub main, `git show`; not the scorer's copies), with its own
selection code: MM1-v3.1's per-case wall error, T1, T3 and E4 per card over the no-twin cases at the declared bands, the wall rms, the switch
test's Q1 rms against N with its closer counts, D1's H1 (MM1-v3.1 vs MM1-v3, wall) counts at the declared ties, and one run by hand; then
each figure compared with the scorer's scores-blind-e217.json. Desk; stdlib. Run: /usr/bin/python3 -I -B s04_recheck.py <lane dir>
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
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='<GITHUB_SSH_PREFIX>')
DECL = json.load(open(os.path.join(L, 'work', 'decl', 'DECLARED-blind-e217.json')))
BANDS = DECL['f_pass_rule']['bands']
TIES = DECL['d_comparisons']['ties']
F = list(csv.DictReader(open(os.path.join(L, 'forecasts-blind-e217.csv'))))
COND = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e217.json')))
SC = json.load(open(os.path.join(L, 'work', 'step3', 'scores-blind-e217.json')))['primary_footing']
M = {}
for s, d in COND['sessions'].items():
    Dj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f"{COMMIT}:{d['file']}"], check=True, capture_output=True, env=ENV).stdout)
    pv = Dj['primary_view']
    for r in Dj['runs']:
        M[f'E217|{s}|{r["run"]}'] = (((r.get('views') or {}).get(pv) or {}), r)
cw = collections.defaultdict(list)
cs3 = collections.defaultdict(list)
cw3 = collections.defaultdict(list)
ce4 = collections.defaultdict(list)
cq1 = collections.defaultdict(list)
twt, twe, card = {}, {}, {}
for f in F:
    v, r = M[f['id']]
    c = (f['card'], f['arm'], f['fmt'], f['kind'], f['mask'])
    card[c] = f['card']
    twt[c] = f['twin_time_v31'] == '1'
    twe[c] = f['twin_energy_v31'] == '1'
    cw[c].append(float(f['v31_cyc_wall']) / v['cyc_op_max'] - 1)
    cw3[c].append(float(f['v3_cyc_wall']) / v['cyc_op_max'] - 1)
    cs3[c].append(float(f['v31_sec_gemm']) / v['t_pass_s'] - 1)
    if v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped'):
        w, T = v['dP_w'], v['T_op_us']
        rest = v['p_mean_w'] - w
        Wf, Tf = float(f['v31_W_fc']), float(f['v31_T_op_us'])
        ce4[c].append((rest + Wf) * Tf / ((rest + w) * T) - 1)
        if f['group_kind'] == 'S':
            Wg = float(f['v31_W_A']) + float(f['v31_W_B']) / T
            N = sum(float(f[f'v31_null_{k}_W_A']) + float(f[f'v31_null_{k}_W_B']) / T for k in ('zeros', 'ones', 'random')) / 3.0
            cq1[c].append((Wg / w - 1, N / w - 1, w))


def mn(v):
    return sum(v) / len(v)


out = {'cards': {}}
for cd in ('aifoundry1 card 1', 'aifoundry1 card 0'):
    es = [mn(v) for c, v in cw.items() if card[c] == cd and not twt[c]]
    e3 = [mn(v) for c, v in cs3.items() if card[c] == cd and not twt[c]]
    e4 = [mn(v) for c, v in ce4.items() if card[c] == cd and not twe[c]]
    mine = {'T1': f"{sum(abs(x) <= BANDS[cd]['T1'] for x in es)}/{len(es)}", 'T3': f"{sum(abs(x) <= BANDS[cd]['T3'] for x in e3)}/{len(e3)}",
            'E4': f"{sum(abs(x) <= BANDS[cd]['E4'] for x in e4)}/{len(e4)}", 'wall_rms_no_twin_pct': round(100 * math.sqrt(sum(x * x for x in es) / len(es)), 3)}
    sc = {r: f"{SC['part_A']['v31'][cd][r]['pass']}/{SC['part_A']['v31'][cd][r]['n']}" for r in ('T1', 'T3', 'E4')}
    sc['wall_rms_no_twin_pct'] = SC['tables_per_case']['v31']['wall'][cd]['no_twin']['rms_pct']
    out['cards'][cd] = {'recheck': mine, 'scorer': sc, 'equal': mine == sc}
q1 = [(mn([a for a, _, _ in v]), mn([b for _, b, _ in v])) for c, v in cq1.items() if mn([w for _, _, w in v]) >= 3.0]
mine = {'cases': len(q1), 'v31_rms_pct': round(100 * math.sqrt(sum(a * a for a, _ in q1) / len(q1)), 3),
        'N_rms_pct': round(100 * math.sqrt(sum(b * b for _, b in q1) / len(q1)), 3),
        'closer_v31': sum(1 for a, b in q1 if abs(b) - abs(a) >= 0.01), 'closer_N': sum(1 for a, b in q1 if abs(b) - abs(a) <= -0.01)}
S1 = SC['part_S']['v31']['Q1']
sc = {'cases': S1['cases'], 'v31_rms_pct': S1['model']['rms_pct'], 'N_rms_pct': S1['N']['rms_pct'], 'closer_v31': S1['closer_model'], 'closer_N': S1['closer_N']}
out['Q1'] = {'recheck': mine, 'scorer': sc, 'equal': mine == sc}
npos = nneg = nt = 0
for c in cw:
    t = TIES[card[c]]['cycles_ln']
    d = abs(math.log(1 + mn(cw3[c]))) - abs(math.log(1 + mn(cw[c])))
    if d > t:
        npos += 1
    elif d < -t:
        nneg += 1
    else:
        nt += 1
H = SC['comparisons']['D1 MM1-v3.1 vs MM1-v3']['H1']['pooled']
out['D1_H1_pooled'] = {'recheck': [npos, nneg, nt], 'scorer': [H['closer_A'], H['closer_B'], H['ties']], 'equal': [npos, nneg, nt] == [H['closer_A'], H['closer_B'], H['ties']]}
rid = 'E217|a1c1-S1|001-4x8x8-int8-rnd'
f = [x for x in F if x['id'] == rid][0]
v, r = M[rid]
Wg = float(f['v31_W_A']) + float(f['v31_W_B']) / v['T_op_us']
out['one_run_by_hand'] = {'id': rid, 'e_wall': float(f['v31_cyc_wall']) / v['cyc_op_max'] - 1, 'W_given_t': Wg, 'meas_dP_w': v['dP_w'],
                          'e_E1': Wg / v['dP_w'] - 1, 'clock_equal_to_conditions': v['kclock_mhz'] == float(f['f_mhz'])}
out['ALL_EQUAL'] = all(x['equal'] for x in out['cards'].values()) and out['Q1']['equal'] and out['D1_H1_pooled']['equal']
json.dump(out, open(os.path.join(L, 'work', 'step3', 'recheck.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out, indent=1))
