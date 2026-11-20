#!/usr/bin/env python3
"""blind-e219 (Q232) step 3p: POST HOC readings (REPORTED, deciding nothing; read after the score) from the scorer's outputs
(scores-blind-e219.json and its cases and out-of-domain CSVs): (1) where part A's misses are (class, shape, sign; MM1-v2 beside); (2) the R
ladder: MM1-v3.1's wall and E1 error against R per card, format and kind, the slope of the wall error in 1/R; (3) the out-of-domain stream
and TenB arms' measured cycles an op beside MM1's two TenB floors (529 cycles fp32 / fp16, 270 int8: E101's, in no predictor's map for these
arms); (4) MM1-v3 against MM1-v3.1 by class (the rms, D1 NOT DECIDED). Desk; stdlib. Run: /usr/bin/python3 -I -B s03p_posthoc.py <lane dir>
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

L = os.path.abspath(sys.argv[1])
S3 = os.path.join(L, 'work', 'step3')
SC = json.load(open(os.path.join(S3, 'scores-blind-e219.json')))
CS = {r['case']: r for r in csv.DictReader(open(os.path.join(S3, 'scores-blind-e219-cases.csv')))}
OD = list(csv.DictReader(open(os.path.join(S3, 'scores-blind-e219-out-of-domain.csv'))))
P = SC['primary_footing']
RQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}
f = lambda x: float(x) if x not in ('', None) else None  # noqa: E731
out = {'what': 'blind-e219 post hoc readings (REPORTED, deciding nothing)', 'misses': [], 'ladder_slope': {}, 'tenb_floor': [], 'v3_vs_v31_by_class': {}}
for card, rr in P['part_A']['v31'].items():
    for rule, x in rr.items():
        for c in x['misses']:
            r = CS[c]
            q = RQ[rule]
            out['misses'].append({'card': card, 'rule': rule, 'band': x['band'], 'case': c, 'class': r['class'], 'v31_e': f(r[f'v31_e_{q}']),
                                  'v3_e': f(r[f'v3_e_{q}']), 'v2_e': f(r[f'v2_e_{q}']), 'meas_cyc_wall': f(r['meas_cyc_wall']), 'meas_w': f(r['meas_w'])})
out['miss_classes'] = dict(sorted({m['class']: sum(1 for z in out['misses'] if z['class'] == m['class']) for m in out['misses']}.items()))
out['time_misses_all_GAP'] = all(m['class'] == 'GAP' for m in out['misses'] if m['rule'] in ('T1', 'T2', 'T3'))
out['time_misses_v2_closer'] = sum(1 for m in out['misses'] if m['rule'] == 'T1' and abs(m['v2_e']) < abs(m['v31_e']))
out['time_misses_T1'] = sum(1 for m in out['misses'] if m['rule'] == 'T1')
for k, rows in P and SC['R_ladder_REPORTED']['rows'].items():
    xs = [1.0 / r['R'] for r in rows if r['v31_e_wall'] is not None]
    ys = [r['v31_e_wall'] for r in rows if r['v31_e_wall'] is not None]
    if len(xs) >= 3:
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        a = my - b * mx
        res = [y - (a + b * x) for x, y in zip(xs, ys)]
        out['ladder_slope'][k] = {'n': len(xs), 'e_wall_at_R_inf_pct': round(100 * a, 3), 'slope_per_1_over_R_pct': round(100 * b, 3),
                                  'rms_resid_pct': round(100 * math.sqrt(sum(e * e for e in res) / len(res)), 3),
                                  'e_wall_pct_by_R': {r['R']: round(100 * r['v31_e_wall'], 2) for r in rows if r['v31_e_wall'] is not None},
                                  'e_E1_pct_by_R': {r['R']: (round(100 * r['v31_e_E1'], 2) if r['v31_e_E1'] is not None else None) for r in rows}}
FLOOR = {'fp32': 529.0, 'fp16': 529.0, 'int8': 270.0}
for r in OD:
    if r['class'] in ('OUT-tenb', 'OUT-mm') and r['meas_cyc_wall']:
        out['tenb_floor'].append({'case': r['case'], 'class': r['class'], 'fmt': r['fmt'], 'meas_cyc_wall': f(r['meas_cyc_wall']),
                                  'meas_cyc_mean': f(r['meas_cyc_mean']), 'floor': FLOOR[r['fmt']],
                                  'meas_over_floor_minus_1_pct': round(100 * (f(r['meas_cyc_wall']) / FLOOR[r['fmt']] - 1), 4)})
for k in ('CTRL', 'GAP', 'ANCHOR', 'CTAB', 'C16R'):
    out['v3_vs_v31_by_class'][k] = {mo: {q: (P['splits'][mo][f'{k}|pooled'][q]['no_twin'] if q != 'E1' else P['splits'][mo][f'{k}|pooled'][q]['no_twin']['relative'])
                                         for q in ('wall', 'E1', 'E3')} for mo in ('v31', 'v3', 'v2')}
json.dump(out, open(os.path.join(S3, 'posthoc-e219.json'), 'w'), indent=1, sort_keys=True)
print('misses by class', out['miss_classes'], '| time misses all GAP:', out['time_misses_all_GAP'], '| T1 misses where MM1-v2 is closer:',
      out['time_misses_v2_closer'], 'of', out['time_misses_T1'])
for k, v in out['ladder_slope'].items():
    print('ladder', k, 'e_wall(R->inf)', v['e_wall_at_R_inf_pct'], '% slope/(1/R)', v['slope_per_1_over_R_pct'], '% resid', v['rms_resid_pct'], '%')
for t in out['tenb_floor']:
    print('floor', t['case'].replace('aifoundry1 ', ''), t['meas_cyc_wall'], 'floor', t['floor'], f"{t['meas_over_floor_minus_1_pct']:+.4f}%")
