#!/usr/bin/env python3
"""mask-posimb (Q238) x02: a look (post hoc, in sample, disclosed in the declaration) at MM1-v3.2's and the frozen posimb's COMMITTED blind
wall errors on E221's MASK cases (blind-e221's case table, columns v32_e_wall and v32p_e_wall; no fit, no feature of this lane): by shire
count, by shape, by card, by kind, single-shire by shire. Desk; stdlib only."""
import collections
import csv
import math
import os
import re

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
D = os.path.join(LAB, 'tools/matmul/mm1/v3.1/blind-e221-scores/cases')
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
C = [c for c in csv.DictReader(open(os.path.join(D, 'scores-blind-e221-cases.csv'))) if c['class'] == 'MASK' and c['twin_time_v32'] == '0']


def rb(v):
    v = [x for x in v if x is not None]
    return (100 * math.sqrt(sum(x * x for x in v) / len(v)), 100 * sum(v) / len(v), len(v)) if v else (float('nan'),) * 3


def f(x):
    return None if x in ('', 'None') else float(x)


def show(name, key):
    g = collections.defaultdict(list)
    for c in C:
        g[key(c)].append(c)
    print('==', name)
    for k in sorted(g, key=lambda z: str(z)):
        a = rb([f(c['v32_e_wall']) for c in g[k]])
        b = rb([f(c['v32p_e_wall']) for c in g[k]])
        print('  %-38s v32 %6.2f (%+6.2f) n %3d | posimb-frozen %6.2f (%+6.2f)' % (str(k)[:38], a[0], a[1], a[2], b[0], b[1]))


print('MASK no-twin', len(C), 'v32', rb([f(c['v32_e_wall']) for c in C]), 'posimb frozen', rb([f(c['v32p_e_wall']) for c in C]))
print('in posimb scope', collections.Counter(c['posimb_in_scope'] for c in C))
show('shire count', lambda c: int(c['n_shires']) if int(c['n_shires']) < 4 else ('4-7' if int(c['n_shires']) < 8 else ('8-15' if int(c['n_shires']) < 16 else ('16-31' if int(c['n_shires']) < 32 else '32'))))
show('arm', lambda c: c['arm'])
show('card', lambda c: c['card'])
show('fmt kind', lambda c: (c['fmt'], c['kind']))
show('arm x count', lambda c: (c['arm'], int(c['n_shires'])))
show('subfamily', lambda c: c['subfamily'])
print('== single-shire cases: arm, mask, card, v32 err')
for c in sorted([c for c in C if c['n_shires'] == '1'], key=lambda c: (c['arm'], c['mask'], c['card']))[:200]:
    print('  %-12s %-11s %-18s %-6s %-6s v32 %+6.1f%% posimbF %+6.1f%%' % (c['arm'], c['mask'], c['card'], c['fmt'], c['kind'], 100 * f(c['v32_e_wall']), 100 * f(c['v32p_e_wall'])))
