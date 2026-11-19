#!/usr/bin/env python3
"""unread-e214 (Q225) step 3p: a POST HOC reading of where MM1-v3.1's time misses sit (REPORTED, after the scores; never a verdict).
From work/step3/scores-unread-e214-cases.csv and the registered arms (families, K): MM1-v3.1's no-twin wall error by E214 family tag, mask
class, depth past the first sweep's largest K, format, and the misses of T1 (|e| over the card's band). Desk.
Run: /usr/bin/python3 -I -B s03p_posthoc.py <lane dir>
"""
import collections
import csv
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
DECL = json.load(open(os.path.join(L, 'DECLARED-unread-e214.json')))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
A = {a['id']: a for a in json.load(open(os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e214', 'proposal', 'src', 'arms.json')))['arms']}
C = list(csv.DictReader(open(os.path.join(L, 'work', 'step3', 'scores-unread-e214-cases.csv'))))
BANDS = DECL['f_pass_rule']['bands']
labels = collections.defaultdict(set)
for r in RL['runs']:
    labels[r['case']].add(r['arm_label'])
KMAX1 = {'fp32': 16384, 'fp16': 8192, 'int8': 32768}     # the first sweep's largest K (E214.md section 3)
KPER = {'fp32': 512, 'fp16': 1024, 'int8': 2048}


def st(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {'n': len(v), 'rms_pct': round(100 * math.sqrt(sum(x * x for x in v) / len(v)), 2), 'bias_pct': round(100 * sum(v) / len(v), 2)}


rows = []
for c in C:
    if c['twin_time_v31'] == '1' or not c['v31_e_wall']:
        continue
    arm = sorted(labels[c['case']])[0]
    fam = A[arm].get('families', [])
    MB, NB, KB = (int(x) for x in c['arm'][5:].split('x'))
    K = KB * KPER[c['fmt']]
    rows.append({'case': c['case'], 'card': c['card'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'arm_label': arm, 'families': fam,
                 'e31': float(c['v31_e_wall']), 'e3': float(c['v3_e_wall']), 'e2': float(c['v2_e_wall']), 'MB': MB, 'NB': NB, 'KB': KB,
                 'deepK': K > KMAX1[c['fmt']], 'full': c['mask'].lower() == '0xffffffff',
                 'miss': abs(float(c['v31_e_wall'])) > BANDS[c['card']]['T1']})
out = {'label': 'POST HOC (REPORTED): read after the scores; nothing here decides a rule', 'no_twin_time_cases': len(rows)}
grp = collections.defaultdict(list)
for r in rows:
    top = 'blind' if 'blind' in r['families'] else ('mech' if 'mech' in r['families'] else ('tl' if 'tl' in r['families'] else 'other'))
    grp[('top family', top)].append(r)
    for f in r['families']:
        grp[('tag', f)].append(r)
    grp[('mask', 'full chip' if r['full'] else 'subset mask')].append(r)
    grp[('depth', 'past the first sweep\'s largest K' if r['deepK'] else 'within it')].append(r)
    grp[('format', r['fmt'])].append(r)
    grp[('kind', r['kind'] if r['kind'] in ('random', 'zeros', 'ones') else ('sparse50 pools' if r['kind'].startswith('pattern:sparse50') else 'new tiles'))].append(r)
    grp[('card x kind', r['card'] + ' ' + (r['kind'] if r['kind'] in ('random', 'zeros', 'ones') else 'pattern'))].append(r)
    grp[('card', r['card'])].append(r)
    grp[('KB', 'KB 1' if r['KB'] == 1 else ('KB 2-4' if r['KB'] <= 4 else ('KB 5-16' if r['KB'] <= 16 else 'KB > 16')))].append(r)
    grp[('NB', 'NB 1' if r['NB'] == 1 else ('NB 2-4' if r['NB'] <= 4 else 'NB > 4'))].append(r)
tab = {}
for k, rs in sorted(grp.items()):
    tab[f'{k[0]}: {k[1]}'] = {'v31': st([r['e31'] for r in rs]), 'v3': st([r['e3'] for r in rs]), 'v2': st([r['e2'] for r in rs]),
                              'T1_misses_v31': sum(r['miss'] for r in rs)}
out['groups'] = tab
out['T1_misses_v31'] = sorted(({'case': r['case'], 'arm': r['arm_label'], 'e_v31_pct': round(100 * r['e31'], 2), 'e_v3_pct': round(100 * r['e3'], 2),
                                'e_v2_pct': round(100 * r['e2'], 2), 'families': r['families']} for r in rows if r['miss']), key=lambda x: -abs(x['e_v31_pct']))
json.dump(out, open(os.path.join(L, 'work', 'step3', 'posthoc-time-misses.json'), 'w'), indent=1, sort_keys=True)
print('no-twin time cases', len(rows), 'T1 misses', len(out['T1_misses_v31']))
for k, v in tab.items():
    if k.startswith('tag:') and (v['v31'] or {}).get('n', 0) < 8:
        continue
    print(f"{k:55s} v31 {v['v31']} v3 {v['v3']} v2 {v['v2']} misses {v['T1_misses_v31']}")
for m in out['T1_misses_v31'][:40]:
    print(m['arm'], m['e_v31_pct'], m['e_v3_pct'], m['e_v2_pct'], ','.join(f for f in m['families'] if f not in ('newshape',)))
