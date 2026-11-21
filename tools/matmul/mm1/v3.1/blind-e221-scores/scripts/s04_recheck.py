#!/usr/bin/env python3
"""blind-e221 (Q235) step 4: AN INDEPENDENT RECHECK of the scorer's deciding figures by a second code path. Inputs: the frozen forecast CSV
(forecasts-blind-e221.csv, one row a run and model; not the JSON the scorer used), a fresh `git show` of the nine committed data files and
queues (not the scorer's copies), the declaration's twin keys and bands. Its own selection (time: ran, role not null, values gemmL, shires,
the primary view's T_op_us, cyc_op_max, n_launch >= 1, the queue's ran / rc 0 / check exact or approx; energy: + dP_w, p_mean_w, not capped,
role not 'time'), its own twin flags (the case's mean data clock to 25 MHz), its own case means and rule arithmetic. Compares with the
scorer's scores-blind-e221.json: all 21 part A cells of MM1-v3.2 and of MM1-v3.1 (verdict, pass, n), the pooled no-twin rms and bias of
MM1-v3.2, v3.1, v3, v2 on T1 wall, E1 (relative and watts) and E3, and the pooled D0 (H1, H4), D2 (H1) and D3 contention (H1) tallies.
Desk; stdlib. Run: /usr/bin/python3 -I -B s04_recheck.py <lane dir>      Writes work/step4/recheck-e221.json.
"""
import collections
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='<GITHUB_SSH_PREFIX>')
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
OUT = os.path.join(L, 'work', 'step4')
os.makedirs(OUT, exist_ok=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(os.path.join(L, 'forecasts-blind-e221.csv')) == '962252bd28c9a6184580a38fd2dad87f4790fab62097cd651d5b602f814bf844'
SC = json.load(open(os.path.join(L, 'work', 'step3', 'scores-blind-e221.json')))
DEC = json.load(open(os.path.join(L, 'work', 'decl', 'DECLARED-blind-e221.json')))
TK = json.load(open(os.path.join(L, 'work', 'decl', 'inputs', 'step1', 'twin-keys.json')))
BANDS = DEC['declaration']['pass_rule']['bands']
TIES = {'aifoundry1 card 1': (0.005, 0.005, 0.01, 0.1), 'aifoundry1 card 0': (0.005, 0.005, 0.01, 0.15), 'aifoundry2 card 0': (0.005, 0.005, 0.02, 0.4)}
CARDK = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a2c0': 'aifoundry2 card 0'}
WANT = {'MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention'}
# --- the forecasts from the CSV
fc = collections.defaultdict(dict)
meta = {}
for r in csv.DictReader(open(os.path.join(L, 'forecasts-blind-e221.csv'))):
    if r['model'] not in WANT:
        continue
    fc[r['id']][r['model']] = {'cw': float(r['cycles_per_op_wall']), 'cm': float(r['cycles_per_op_mean']), 'T': float(r['T_op_us']),
                               'sp': float(r['seconds_per_pass']), 'A': float(r['W_A']), 'B': float(r['W_B_us']), 'Wf': float(r['W_over_idle_own_t'])}
    meta[r['id']] = {'session': r['session'], 'run': r['run'], 'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
                     'kind_energy': r['kind_energy'], 'mask': r['mask'], 'group': r['group_mask']}
# --- the data, fresh
names = subprocess.run(['git', '-C', LAB, 'ls-tree', '--name-only', COMMIT, 'docs/reports/data/'], check=True, capture_output=True, text=True, env=ENV).stdout.split()
fold = {re.fullmatch(r'docs/reports/data/2026-11-20-e221-mmsweep6-(a[12]c[01]-S\d)', n).group(1): n for n in names
        if re.fullmatch(r'docs/reports/data/2026-11-20-e221-mmsweep6-(a[12]c[01]-S\d)', n)}
meas = {}
for s, fo in sorted(fold.items()):
    dj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{fo}/data-e221-{s}.json'], check=True, capture_output=True, env=ENV).stdout)
    qj = json.loads(subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{fo}/session/queue.json'], check=True, capture_output=True, env=ENV).stdout)
    qq = {q['run']: q for q in qj['queue']}
    pv = dj['primary_view']
    for x in dj['runs']:
        rid = f'E221|{s}|{x["run"]}'
        if rid not in meta:
            continue
        v = x['views'][pv]
        q = qq[x['run']]
        qok = q['ran'] and q['rc'] == 0 and all(c == 0 for c in q['rcs']) and q['check'] in ('exact', 'approx') and all(c in ('exact', 'approx') for c in q['checks'])
        tok = (x['ran'] and x['role'] not in (None, 'null') and x['arm'] and x['shires'] and re.match(r'gemmL\d+x\d+x\d+:', x['values'])
               and v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1 and qok)
        if not tok:
            continue
        m = {'T': v['T_op_us'], 'cw': v['cyc_op_max'], 'cm': v['cyc_op_mean'], 'tp': v['t_pass_s'], 'f': v['kclock_mhz']}
        if v.get('dP_w') is not None and v.get('p_mean_w') and not x.get('capped') and x['role'] != 'time':
            m['w'] = v['dP_w']
            m['rest'] = v['p_mean_w'] - v['dP_w']
        meas[rid] = m
# --- per case
cases = collections.defaultdict(list)
for rid, mt in meta.items():
    cases[(mt['card'], mt['arm'], mt['fmt'], mt['kind'], mt['mask'])].append(rid)
tk = {n: {tuple(k) for k in TK[n]['time_keys']} for n in ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2')}
ek = {n: {tuple(k) for k in TK[n]['energy_keys']} for n in ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2')}
CK = []
for key, rids in cases.items():
    card, arm, fmt, kind, mask = key
    ke = meta[rids[0]]['kind_energy']
    tr = [r for r in rids if r in meas]
    er = [r for r in tr if 'w' in meas[r]]
    fs = [meas[r]['f'] for r in rids if r in meas]
    f25 = int(round(sum(fs) / len(fs) / 25.0) * 25)
    c = {'key': key, 'card': card, 'group': meta[rids[0]]['group'], 'nt': len(tr), 'ne': len(er)}
    for mo in WANT:
        base = 'MM1-v3.1' if mo == 'v3.1+contention' else mo
        c[f'tw_{mo}'] = (card, 'rgm136', arm, fmt, mask, f25) in tk[base]
        c[f'ew_{mo}'] = (card, 'rgm136', arm, fmt, mask, f25, ke) in ek[base]
        if tr:
            c[f'wall_{mo}'] = sum(fc[r][mo]['cw'] / meas[r]['cw'] - 1 for r in tr) / len(tr)
            c[f'mean_{mo}'] = sum(fc[r][mo]['cm'] / meas[r]['cm'] - 1 for r in tr) / len(tr)
            c[f'sec_{mo}'] = sum(fc[r][mo]['sp'] / meas[r]['tp'] - 1 for r in tr) / len(tr)
        if er:
            g = [fc[r][mo]['A'] + fc[r][mo]['B'] / meas[r]['T'] for r in er]
            c[f'E1_{mo}'] = sum(gi / meas[r]['w'] - 1 for gi, r in zip(g, er)) / len(er)
            c[f'd1_{mo}'] = sum(gi - meas[r]['w'] for gi, r in zip(g, er)) / len(er)
            c[f'E2_{mo}'] = sum(fc[r][mo]['Wf'] * fc[r][mo]['T'] / (meas[r]['w'] * meas[r]['T']) - 1 for r in er) / len(er)
            c[f'd2_{mo}'] = sum(fc[r][mo]['Wf'] - meas[r]['w'] for r in er) / len(er)
            c[f'E3_{mo}'] = sum((meas[r]['rest'] + gi) / (meas[r]['rest'] + meas[r]['w']) - 1 for gi, r in zip(g, er)) / len(er)
            c[f'E4_{mo}'] = sum((meas[r]['rest'] + fc[r][mo]['Wf']) * fc[r][mo]['T'] / ((meas[r]['rest'] + meas[r]['w']) * meas[r]['T']) - 1 for r in er) / len(er)
            if mo == 'MM1-v3.2':
                c['g32'] = sum(g) / len(g)
                c['wm'] = sum(meas[r]['w'] for r in er) / len(er)
    if er:
        c['watts'] = c['g32'] < 3.0 or c['wm'] < 3.0
    CK.append(c)
# --- part A, independently
RQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}
mine = {}
for mo in ('MM1-v3.2', 'MM1-v3.1'):
    for card in BANDS:
        for rule, q in RQ.items():
            tw = 'tw' if q in ('wall', 'mean', 'sec') else 'ew'
            ok = n = 0
            for c in CK:
                if c['card'] != card or c[f'{tw}_{mo}']:
                    continue
                if q in ('wall', 'mean', 'sec'):
                    if not c['nt']:
                        continue
                    good = abs(c[f'{q}_{mo}']) <= BANDS[card][rule]
                else:
                    if not c['ne']:
                        continue
                    if q in ('E1', 'E2') and c['watts']:
                        good = abs(c[f'd{q[1]}_{mo}']) <= BANDS[card]['watts_W']
                    else:
                        good = abs(c[f'{q}_{mo}']) <= BANDS[card][rule]
                n += 1
                ok += good
            v = 'NO DATA' if n == 0 else ('TOO FEW' if n < 10 else ('PASS' if 10 * ok >= 9 * n else 'FAIL'))
            mine[f'{mo}|{card}|{rule}'] = (v, ok, n)
SMN = {'MM1-v3.2': 'v32', 'MM1-v3.1': 'v31', 'MM1-v3': 'v3', 'MM1-v2': 'v2', 'v3.1+contention': 'v31c'}
cmp_ = {'partA_cells': 0, 'partA_equal': 0, 'partA_diffs': []}
for k, (v, ok, n) in mine.items():
    mo, card, rule = k.split('|')
    s = SC['primary_footing']['part_A'][SMN[mo]][card][rule]
    cmp_['partA_cells'] += 1
    if (s['verdict'], s['pass'], s['n']) == (v, ok, n):
        cmp_['partA_equal'] += 1
    else:
        cmp_['partA_diffs'].append({'cell': k, 'mine': [v, ok, n], 'scorer': [s['verdict'], s['pass'], s['n']]})


def rmsb(v):
    return (math.sqrt(sum(x * x for x in v) / len(v)) * 100, sum(v) / len(v) * 100, len(v)) if v else None


cmp_['rms_cells'] = cmp_['rms_equal'] = 0
cmp_['rms_diffs'] = []
for mo in ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2'):
    for q in ('wall', 'E1', 'E3'):
        tw = 'tw' if q == 'wall' else 'ew'
        if q == 'wall':
            vals = [c[f'wall_{mo}'] for c in CK if c['nt'] and not c[f'{tw}_{mo}']]
        elif q == 'E1':
            vals = [c[f'E1_{mo}'] for c in CK if c['ne'] and not c['watts'] and not c[f'{tw}_{mo}']]
            wv = [c[f'd1_{mo}'] for c in CK if c['ne'] and c['watts'] and not c[f'{tw}_{mo}']]
        else:
            vals = [c[f'E3_{mo}'] for c in CK if c['ne'] and not c[f'{tw}_{mo}']]
        r = rmsb(vals)
        sc = SC['primary_footing']['tables_per_case'][SMN[mo]][q]['pooled']['no_twin']
        if q == 'E1':
            scw = sc['watts']
            sc = sc['relative']
            rw = (math.sqrt(sum(x * x for x in wv) / len(wv)), sum(wv) / len(wv), len(wv))
            cmp_['rms_cells'] += 1
            if abs(rw[0] - scw['rms_W']) < 1e-9 and abs(rw[1] - scw['bias_W']) < 1e-9 and rw[2] == scw['n']:
                cmp_['rms_equal'] += 1
            else:
                cmp_['rms_diffs'].append({'cell': f'{mo} E1 watts', 'mine': rw, 'scorer': scw})
        cmp_['rms_cells'] += 1
        if abs(r[0] - sc['rms_pct']) < 1e-9 and abs(r[1] - sc['bias_pct']) < 1e-9 and r[2] == sc['n']:
            cmp_['rms_equal'] += 1
        else:
            cmp_['rms_diffs'].append({'cell': f'{mo} {q}', 'mine': r, 'scorer': sc})


def tally(a, b, q, sel):
    p = n = t = 0
    for c in CK:
        if not sel(c):
            continue
        tie = TIES[c['card']]
        if q in ('wall', 'mean', 'sec'):
            if not c['nt']:
                continue
            d = abs(math.log(1 + c[f'{q}_{b}'])) - abs(math.log(1 + c[f'{q}_{a}']))
            tt = tie[1] if q == 'sec' else tie[0]
        else:
            if not c['ne']:
                continue
            if c['watts']:
                d = abs(c[f'd{q[1]}_{b}']) - abs(c[f'd{q[1]}_{a}'])
                tt = tie[3]
            else:
                d = abs(math.log(1 + c[f'{q}_{b}'])) - abs(math.log(1 + c[f'{q}_{a}']))
                tt = tie[2]
        if d > tt:
            p += 1
        elif d < -tt:
            n += 1
        else:
            t += 1
    return [p, n, t]


cmp_['tallies'] = {}
for nm, a, b, q, sel, skey, rule in (('D0 H1', 'MM1-v3.2', 'MM1-v3.1', 'wall', lambda c: True, 'D0 MM1-v3.2 vs MM1-v3.1', 'H1'),
                                     ('D0 H4', 'MM1-v3.2', 'MM1-v3.1', 'E1', lambda c: True, 'D0 MM1-v3.2 vs MM1-v3.1', 'H4'),
                                     ('D2 H1', 'MM1-v3.1', 'MM1-v2', 'wall', lambda c: True, 'D2 MM1-v3.1 vs MM1-v2', 'H1'),
                                     ('D3 contention H1', 'v3.1+contention', 'MM1-v3.1', 'wall', lambda c: c['group'] != 'FULL', None, 'H1')):
    mine_t = tally(a, b, q, sel)
    if skey:
        z = SC['primary_footing']['comparisons'][skey][rule]['pooled']
    else:
        z = SC['primary_footing']['comparisons']['D3 layout']['D3 v3.1+contention vs MM1-v3.1 (the subset masks)'][rule]['pooled']
    cmp_['tallies'][nm] = {'mine': mine_t, 'scorer': [z['closer_A'], z['closer_B'], z['ties']], 'equal': mine_t == [z['closer_A'], z['closer_B'], z['ties']]}
cmp_['runs_time_mine'] = len(meas)
cmp_['runs_energy_mine'] = sum(1 for m in meas.values() if 'w' in m)
cmp_['ALL_EQUAL'] = (cmp_['partA_equal'] == cmp_['partA_cells'] and cmp_['rms_equal'] == cmp_['rms_cells'] and all(x['equal'] for x in cmp_['tallies'].values()))
json.dump(cmp_, open(os.path.join(OUT, 'recheck-e221.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in cmp_.items() if k not in ('partA_diffs', 'rms_diffs')}))
print('partA diffs', cmp_['partA_diffs'][:5])
print('rms diffs', cmp_['rms_diffs'][:5])
print(sha(os.path.join(OUT, 'recheck-e221.json')), 'work/step4/recheck-e221.json')
sys.exit(0 if cmp_['ALL_EQUAL'] else 1)
