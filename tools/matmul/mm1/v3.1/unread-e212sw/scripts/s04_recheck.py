#!/usr/bin/env python3
"""unread-e212sw (Q218) step 4: an independent re-computation of the verdict's four numbers from the cases CSV alone (no import of the
scorer): rms of V3 and N on Q1 and Q2 over group A, the sign tests with the declared tie bands, and the verdict. Also re-derives one E212
run's Q1 error by hand from the committed data file and the frozen K's (the first group A run in the runs CSV). Desk.
Run: /usr/bin/python3 -I -B s04_recheck.py <lane dir>
"""
import csv
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
C = [r for r in csv.DictReader(open(os.path.join(L, 'work', 'step3', 'scores-unread-cases.csv'))) if r['group'] == 'A']


def num(x):
    return None if x in ('', None) else float(x)


def rms(v):
    return 100 * math.sqrt(sum(x * x for x in v) / len(v))


out = {}
for q in ('e1', 'e2'):
    pairs = [(num(r[f'{q}_V3']), num(r[f'{q}_N'])) for r in C if num(r[f'{q}_V3']) is not None and num(r[f'{q}_N']) is not None]
    k = n = 0
    for a, b in pairs:
        d = abs(b) - abs(a)
        if abs(d) < 0.01:
            continue
        n += 1
        k += d > 0
    lo = min(k, n - k)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(lo + 1)) / 2 ** n)
    out[q] = {'n': len(pairs), 'rms_V3': round(rms([a for a, _ in pairs]), 3), 'rms_N': round(rms([b for _, b in pairs]), 3), 'V3_closer': k,
              'non_tied': n, 'p': p}
P = [out['e1']['rms_V3'] < out['e1']['rms_N'], out['e1']['p'] < 0.05 and out['e1']['V3_closer'] * 2 > out['e1']['non_tied'],
     out['e2']['rms_V3'] < out['e2']['rms_N'], out['e2']['p'] < 0.05 and out['e2']['V3_closer'] * 2 > out['e2']['non_tied']]
out['verdict'] = 'PASS' if all(P) else 'FAIL'
# one run by hand
R = [r for r in csv.DictReader(open(os.path.join(L, 'work', 'step3', 'scores-unread-runs.csv'))) if r['group'] == 'A' and r['source'] == 'E212']
r0 = R[0]
F = {x['id']: x for x in json.load(open(os.path.join(L, 'forecasts-unread.json')))['rows']}
k = F[r0['id']]['V3']
sess, run = r0['id'].split('|')[1:]
Dd = json.load(open(os.path.join(L, 'work', 'step3', 'data', f'data-e212-{sess}.json')))
rr = [x for x in Dd['runs'] if x.get('run') == run][0]
v = rr['views'][Dd['primary_view']]
t, f, w = float(v['T_op_us']), float(v['kclock_mhz']), float(v['dP_w'])
T0 = rr.get('die_start_c') if rr.get('die_start_c') is not None else 50.0
V = 0.517     # card 1's footing
W = (k['K0'] + 0.0 + (1e6 / t) * (k['K1'] + k['K2'])) * (1 + 0.0048 * (T0 - 50.0))
out['by_hand'] = {'id': r0['id'], 't_us': t, 'f': f, 'die': T0, 'W_meas': w, 'W_V3_by_hand': W, 'e1_by_hand': W / w - 1, 'e1_scorer': float(r0['e1_V3'])}
print(json.dumps(out, indent=1))
assert abs(out['by_hand']['e1_by_hand'] - out['by_hand']['e1_scorer']) < 1e-5
