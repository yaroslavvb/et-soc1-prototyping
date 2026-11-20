#!/usr/bin/env python3
"""Lane l3-edge (Q234): every committed matmul TIME point through E219, as one list, read-only from the lab clone at GitHub main.
  - E105-E215: MM1-v3.2's own point table (tools/matmul/mm1/v3.2/out/points_time_v32.csv: its 2508 points, its LOEO and LOCO
    predictions, its twin flag), byte for byte as landed in 4e386f75;
  - E216: tools/claims-v3/e216/points-e216.csv (the registered points) with the frozen scorer's measured route
    (docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json > points > <id> > measured_route_c: wall cycles an op,
    T_op us, the clock column 'col' in MHz);
  - E217: the lab's blind score of E217 (tools/matmul/mm1/v3.1/blind-e217-scores/): forecasts-blind-e217.csv (the run's arm, format,
    kind, mask, clock, volts, die) joined by id to cases/scores-blind-e217-runs.csv (meas_T_op_us, meas_f; rows with time_ok = 1);
  - E218: MM1-v3.2's E218 points (tools/matmul/mm1/v3.2/out/e218/points-e218.csv) with the frozen scorer's measured table
    (docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json > measured: cw wall cycles an op at 600 MHz);
  - E219: the lab's blind score of E219 (tools/matmul/mm1/v3.1/blind-e219-scores/), in-domain runs only (domain IN), joined as E217.
Writes OUT/l3-edge/work/data/points_all.json. Desk, standard library only.
"""
import csv
import json
import os
import re
import sys

LAB = os.environ.get('ET_LAB') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, '..', 'out', 'data')
os.makedirs(OUTD, exist_ok=True)
pts = []


def kernel_of(arm, kernel):
    m = re.match(r'(gemmLnc|gemmLn|gemmL)\d', arm)
    if not m:
        return 'run_gemm'
    if m.group(1) == 'gemmLn':
        return 'rgm211'
    return kernel or 'rgm136'


# ---------------------------------------------------------------- E105-E215: MM1-v3.2's table
for r in csv.DictReader(open(os.path.join(LAB, 'tools/matmul/mm1/v3.2/out/points_time_v32.csv'))):
    pts.append({'id': r['id'], 'exp': r['exp'], 'card': r['card'], 'kernel': r['kernel'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
                'mask': r['mask'].lower(), 'f': float(r['f_mhz_mean']), 'meas_T_us': float(r['meas_T_us']),
                'store_rung': int(r['store_rung'] or 0), 'src': 'v32-table',
                'v32_table': {'all': float(r['v32_all_data_T_us']), 'LOEO': float(r['v32_LOEO_T_us']), 'LOCO': float(r['v32_LOCO_T_us']),
                              'twin_LOEO': int(r['twin_LOEO'])}})
n_v32 = len(pts)
# ---------------------------------------------------------------- E216
sc = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))['points']
n216 = 0
for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e216/points-e216.csv'))):
    m = (sc.get(r['id']) or {}).get('measured_route_c') or {}
    if not m.get('T_op'):
        continue
    pts.append({'id': 'E216|a2|' + r['id'], 'exp': 'E216', 'card': 'aifoundry2 card 0', 'kernel': kernel_of(r['arm'], r['kernel']),
                'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'].lower(), 'f': float(m['col']),
                'meas_T_us': float(m['T_op']), 'store_rung': 0, 'src': 'e216', 'family': r['family'],
                'energy': {'W': m.get('W'), 'J_over': m.get('J_over'), 'J_rest': m.get('J_rest'), 'p_rest': m.get('p_rest'), 't': m.get('t')}})
    n216 += 1


# ---------------------------------------------------------------- E217, E219
def blind(exp, d, only_in):
    fc = {r['id']: r for r in csv.DictReader(open(os.path.join(d, 'forecasts-blind-%s.csv' % exp.lower())))}
    n = 0
    for r in csv.DictReader(open(os.path.join(d, 'cases', 'scores-blind-%s-runs.csv' % exp.lower()))):
        if r.get('time_ok') != '1':
            continue
        f = fc.get(r['id'])
        if f is None:
            continue
        if only_in and f.get('domain') != 'IN':
            continue
        arm = f['arm']
        if not re.match(r'(gemmLnc|gemmLn|gemmL)\d+x\d+x\d+$', arm) and not arm.startswith('gemmc'):
            continue
        pts.append({'id': r['id'], 'exp': exp, 'card': r['card'], 'kernel': kernel_of(arm, f.get('kernel') or 'rgm136'), 'arm': arm,
                    'fmt': f['fmt'], 'kind': f['kind'], 'mask': f['mask'].lower(), 'f': float(r['meas_f']),
                    'meas_T_us': float(r['meas_T_op_us']), 'store_rung': 0, 'src': exp.lower(), 'session': r['session'],
                    'energy': {'W': float(r['meas_w']) if r.get('meas_w') not in (None, '', 'nan') else None,
                               'energy_ok': r.get('energy_ok'), 'mV': f.get('minion_mV'), 'die_start_c': f.get('die_start_c'),
                               'rest': r.get('meas_rest')}})
        n += 1
    return n


n217 = blind('E217', os.path.join(LAB, 'tools/matmul/mm1/v3.1/blind-e217-scores'), False)
n219 = blind('E219', os.path.join(LAB, 'tools/matmul/mm1/v3.1/blind-e219-scores'), True)
# ---------------------------------------------------------------- E218
meas = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))['measured']
n218 = 0
for r in csv.DictReader(open(os.path.join(LAB, 'tools/matmul/mm1/v3.2/out/e218/points-e218.csv'))):
    m = meas.get(r['id'])
    if not m or not m.get('cw'):
        continue
    f = float(r['f_mhz'])
    pts.append({'id': 'E218|a3|' + r['id'], 'exp': 'E218', 'card': r['card'], 'kernel': kernel_of(r['arm'], r['kernel']), 'arm': r['arm'],
                'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'].lower(), 'f': f, 'meas_T_us': float(m['cw']) / f, 'store_rung': 0,
                'src': 'e218', 'family': r['family'], 'energy': {'W': m.get('W'), 'J': m.get('J'), 'Jrest': m.get('Jrest'), 'die': m.get('die'),
                                                                 'prest': m.get('prest'), 't': m.get('t')}})
    n218 += 1
json.dump(pts, open(os.path.join(OUTD, 'points_all.json'), 'w'), indent=0)
print(json.dumps({'v32_table': n_v32, 'E216': n216, 'E217': n217, 'E218': n218, 'E219': n219, 'total': len(pts)}))
