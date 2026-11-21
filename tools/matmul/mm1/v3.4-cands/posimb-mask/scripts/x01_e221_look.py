#!/usr/bin/env python3
"""mask-posimb (Q238) x01: a look at blind-e221's committed case and run tables (5eb23fd4): the classes against shape and mask, the sessions
of each case, the twin flags, and MM1-v3.2's MASK no-twin wall rms from the committed per-case errors (the 12.41% on 363 to reproduce).
Desk; stdlib only; reads the lane's clone. No fit, no feature."""
import collections
import csv
import math
import os
import re

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
D = os.path.join(LAB, 'tools/matmul/mm1/v3.1/blind-e221-scores/cases')
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
C = list(csv.DictReader(open(os.path.join(D, 'scores-blind-e221-cases.csv'))))
R = list(csv.DictReader(open(os.path.join(D, 'scores-blind-e221-runs.csv'))))
print('cases', len(C), 'runs', len(R))
print('classes', collections.Counter(c['class'] for c in C))
tab = collections.Counter()
for c in C:
    MB, NB, KB = (int(x) for x in SH.match(c['arm']).groups())
    sub = c['mask'] != '0xffffffff'
    k = (c['class'], 'SUB' if sub else 'FULL', 'MB=NB=KB=1' if (MB, NB, KB) == (1, 1, 1) else ('MB=NB=1' if MB == NB == 1 else 'other'), c['fmt'])
    tab[k] += 1
for k, v in sorted(tab.items()):
    print('  ', k, v)
# MASK full-chip cases: does each have a MASK subset case of the same card, arm, fmt, kind?
subkeys = {(c['card'], c['arm'], c['fmt'], c['kind']) for c in C if c['class'] == 'MASK' and c['mask'] != '0xffffffff'}
fullm = [c for c in C if c['class'] == 'MASK' and c['mask'] == '0xffffffff']
print('MASK full cases', len(fullm), 'with a MASK subset twin (card, arm, fmt, kind):', sum((c['card'], c['arm'], c['fmt'], c['kind']) in subkeys for c in fullm))
other_full_with_sub = [c for c in C if c['class'] != 'MASK' and c['mask'] == '0xffffffff' and (c['card'], c['arm'], c['fmt'], c['kind']) in subkeys]
print('non-MASK full cases with a MASK subset key:', len(other_full_with_sub), [(c['class'], c['arm'], c['fmt'], c['kind']) for c in other_full_with_sub][:10])
# sessions per case
runs_by_case = collections.defaultdict(list)
for r in R:
    k = '|'.join((r['card'], r['arm'], r['fmt'], r['kind'], r['mask']))
    runs_by_case[k].append(r)
ns = collections.Counter()
multi = []
for c in C:
    k = '|'.join((c['card'], c['arm'], c['fmt'], c['kind'], c['mask']))
    ss = sorted({r['session'] for r in runs_by_case.get(k, [])})
    ns[len(ss)] += 1
    if len(ss) > 1:
        multi.append((c['class'], k, ss))
print('sessions per case', dict(ns), 'multi-session cases', len(multi), multi[:8])
print('case key match', sum(1 for c in C if '|'.join((c['card'], c['arm'], c['fmt'], c['kind'], c['mask'])) in runs_by_case), 'of', len(C))
print('case column', C[0]['case'])
print('time_ok values', collections.Counter(r['time_ok'] for r in R), 'roles', collections.Counter(r['role'] for r in R))
# MM1-v3.2 MASK no-twin wall rms from the committed errors
e = [float(c['v32_e_wall']) for c in C if c['class'] == 'MASK' and c['twin_time_v32'] in ('0', 'False', '') and c['v32_e_wall'] not in ('', 'None')]
print('MASK no-twin wall n', len(e), 'rms %.4f%%' % (100 * math.sqrt(sum(x * x for x in e) / len(e))) if e else '', 'twin values', collections.Counter(c['twin_time_v32'] for c in C))
print('sample errors', [c['v32_e_wall'] for c in C[:5]])
# subset masks used, counts
print('distinct subset masks', len({c['mask'] for c in C if c['mask'] != '0xffffffff'}), 'MASK subset masks', len({c['mask'] for c in C if c['class'] == 'MASK' and c['mask'] != '0xffffffff'}))
print('subfamilies', collections.Counter(c['subfamily'] for c in C if c['class'] == 'MASK'))
print('MASK arms', collections.Counter(c['arm'] for c in C if c['class'] == 'MASK').most_common(40))
