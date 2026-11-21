#!/usr/bin/env python3
"""mask-mesh x01 (EXPLORATION, post hoc, disclosed in DECLARED): MM1-v3.2's blind wall errors on E221's MASK class, by placement family
and mask, from the committed case table (tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-cases.csv at LAB HEAD).
Prints per family: the shape, and per mask the shire count, row groups R (s >> 2) and column groups C (s & 3), the measured wall / counter
mean, and MM1-v3.2's wall error per card. No feature of a candidate form is computed here. stdlib only.
Run: bash run.sh x01_e221_look.py <out.json>"""
import collections
import csv
import json
import math
import sys

LAB = '<LAB>'
CSV = LAB + '/tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-cases.csv'
rows = list(csv.DictReader(open(CSV)))
out = {'source': CSV, 'n_rows': len(rows), 'families': {}}
fam = collections.defaultdict(list)
for r in rows:
    if r['class'] != 'MASK':
        continue
    fam[r['subfamily'] or '-'].append(r)
CK = {'aifoundry1 card 1': 'a1c1', 'aifoundry1 card 0': 'a1c0', 'aifoundry2 card 0': 'a2c0'}
for f in sorted(fam):
    rs = fam[f]
    shapes = collections.Counter((r['arm'], r['fmt'], r['kind']) for r in rs)
    print('=== family %s: %d cases; shapes %s' % (f, len(rs), dict(shapes)))
    bym = collections.defaultdict(dict)
    for r in rs:
        m = int(r['mask'], 16)
        sh = [s for s in range(32) if (m >> s) & 1]
        key = (r['arm'], r['fmt'], r['kind'], r['mask'])
        e = float(r['v32_e_wall']) if r['v32_e_wall'] not in ('', None) else float('nan')
        wm = (float(r['meas_cyc_wall']) / float(r['meas_cyc_mean'])) if r['meas_cyc_mean'] not in ('', None) and r['meas_cyc_wall'] else float('nan')
        bym[key][CK[r['card']]] = (e, wm, r['twin_time_v32'])
        bym[key]['geo'] = (len(sh), len({s >> 2 for s in sh}), len({s & 3 for s in sh}))
    lst = []
    for key, d in sorted(bym.items(), key=lambda kv: (kv[1]['geo'][0], kv[0][3])):
        es = ['%s %+6.1f%% w/m %.3f%s' % (c, 100 * d[c][0], d[c][1], ' T' if d[c][2] in ('1', 'True', 'true') else '') for c in ('a1c1', 'a1c0', 'a2c0') if c in d]
        n, R, C = d['geo']
        print('  %-14s %-5s %-6s %-11s n%2d R%d C%d | %s' % (key[0], key[1], key[2], key[3], n, R, C, ' | '.join(es)))
        lst.append({'arm': key[0], 'fmt': key[1], 'kind': key[2], 'mask': key[3], 'n': n, 'R': R, 'C': C,
                    'by_card': {c: {'e_wall': d[c][0], 'wall_over_mean': d[c][1], 'twin': d[c][2]} for c in ('a1c1', 'a1c0', 'a2c0') if c in d}})
    out['families'][f] = lst
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x)
