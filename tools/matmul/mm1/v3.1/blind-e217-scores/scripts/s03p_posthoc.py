#!/usr/bin/env python3
"""blind-e217 (Q228) step 3p: POST HOC readings of the scored E217 cases (REPORTED; decided after the read; nothing here decides or changes
any declared verdict): where MM1-v3.1's part A misses fall (1x1x1 or not, full chip or subset, format) per card and rule; how many E4 misses
are also T1 misses (the time error carried into joules with t forecast); the 25 largest no-twin wall-cycle misses with MM1-v3 and MM1-v2
beside; the arms by MM1-v3.1's wall rms. Inputs: work/step3/scores-blind-e217.json and -cases.csv (the scorer's outputs).
Desk; stdlib. Run: /usr/bin/python3 -I -B s03p_posthoc.py <lane dir>
"""
import collections
import csv
import hashlib
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
S3 = os.path.join(L, 'work', 'step3')
SC = json.load(open(os.path.join(S3, 'scores-blind-e217.json')))
P = SC['primary_footing']
R = list(csv.DictReader(open(os.path.join(S3, 'scores-blind-e217-cases.csv'))))
out = {'label': 'POST HOC (REPORTED; read after the scores; decides nothing)', 'misses_by_place': {}, 'E4_misses_also_T1': {}}
for cd, rules in P['part_A']['v31'].items():
    for rule in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4'):
        cnt = collections.Counter()
        for m in rules[rule]['misses']:
            _, arm, fmt, kind, mask = m.split('|')
            cnt[f"{'1x1x1' if arm == 'gemmL1x1x1' else 'other shapes'}|{'full chip' if mask == '0xffffffff' else 'subset mask'}|{fmt}"] += 1
        out['misses_by_place'][f'{cd}|{rule}'] = {'misses': len(rules[rule]['misses']), 'of': rules[rule]['n'], 'by': dict(sorted(cnt.items()))}
    t1 = set(rules['T1']['misses'])
    e4 = rules['E4']['misses']
    out['E4_misses_also_T1'][cd] = {'E4_misses': len(e4), 'also_T1_misses': sum(1 for m in e4 if m in t1)}
nt = [r for r in R if r['twin_time_v31'] == '0' and r['v31_e_wall'] != '']
nt.sort(key=lambda r: -abs(float(r['v31_e_wall'])))
out['largest_wall_misses_no_twin'] = [{'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'runs': int(r['n_runs']),
                                       'meas_cyc_wall': float(r['meas_cyc_wall']), 'v31_e_wall': float(r['v31_e_wall']), 'v3_e_wall': float(r['v3_e_wall']),
                                       'v2_e_wall': float(r['v2_e_wall'])} for r in nt[:25]]
by = collections.defaultdict(list)
for r in nt:
    by[r['arm']].append(float(r['v31_e_wall']))
out['arms_by_v31_wall_rms_no_twin'] = [{'arm': a, 'cases': len(v), 'rms_pct': round(100 * math.sqrt(sum(x * x for x in v) / len(v)), 2),
                                        'bias_pct': round(100 * sum(v) / len(v), 2)} for a, v in sorted(by.items(), key=lambda kv: -math.sqrt(sum(x * x for x in kv[1]) / len(kv[1])))]
sign = collections.Counter(('over' if float(r['v31_e_wall']) > 0 else 'under') for r in nt if abs(float(r['v31_e_wall'])) > 0.10)
out['no_twin_wall_misses_over_10pct_by_sign'] = dict(sign)
x1 = [float(r['v31_e_wall']) for r in nt if r['arm'] == 'gemmL1x1x1']
ox = [float(r['v31_e_wall']) for r in nt if r['arm'] != 'gemmL1x1x1']
out['wall_rms_no_twin_1x1x1_vs_other'] = {'1x1x1': {'cases': len(x1), 'rms_pct': round(100 * math.sqrt(sum(x * x for x in x1) / len(x1)), 3)},
                                          'other shapes': {'cases': len(ox), 'rms_pct': round(100 * math.sqrt(sum(x * x for x in ox) / len(ox)), 3)}}
fn = os.path.join(S3, 'posthoc-e217.json')
json.dump(out, open(fn, 'w'), indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in out.items() if k not in ('largest_wall_misses_no_twin', 'arms_by_v31_wall_rms_no_twin')}, indent=1))
print(hashlib.sha256(open(fn, 'rb').read()).hexdigest(), os.path.relpath(fn, L))
