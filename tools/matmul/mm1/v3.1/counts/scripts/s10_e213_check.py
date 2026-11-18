#!/usr/bin/env python3
"""v31-counts (Q217) step 10: which of E213's registered points did MM1-v3 leave NOT FORECAST in energy for want of a count? (desk)

Reads only E213's registration (tools/claims-v3/e213/points-e213.csv and forecast-e213b-v3.json at GitHub main 6efdb002) and MM1-v3 as landed
(tools/matmul/mm1/v3: out/mm1_v3_e213.json, energy_v3.counts() and phi_of() unchanged). Opens no E213 data file. For every point:
  (1) does MM1-v3's switch route price its (format, kind, KB class)? counts() and phi_of() both non-None, as energy_v3.Features requires;
  (2) does MM1-v3's frozen forecast carry its W over idle and J over idle? (arm A: out/mm1_v3_e213.json by id; arm B: forecast-e213b-v3.json)
    /usr/bin/python3 -I -B s10_e213_check.py <v3 dir> <e213 registration dir> <out json>
"""
import collections
import csv
import json
import os
import sys

V3, REG, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402

pts = list(csv.DictReader(open(os.path.join(REG, 'points-e213.csv'))))
FA = json.load(open(os.path.join(V3, 'out', 'mm1_v3_e213.json')))['points']
FB = json.load(open(os.path.join(REG, 'forecast-e213b-v3.json')))['points']
rows, nf, tally = [], [], collections.Counter()
for p in pts:
    pre, b = E.arm_parts(p['arm_token'])
    KB = b[2] if b else 1
    c = EN.counts(p['format'], p['kind'], KB)
    ph = EN.phi_of(p['format'], p['kind'], KB)
    f = (FA if p['arm'] == 'A' else FB).get(p['id'])
    w = f.get('W_over_idle') if f else None
    j = f.get('J_over_idle_per_gemm') if f else None
    priced = c is not None and ph is not None
    ok = priced and w is not None and j is not None
    tally[(p['arm'], p['format'], p['kind'], 'priced' if ok else 'NOT FORECAST')] += 1
    r = {'id': p['id'], 'arm': p['arm'], 'role': p['role'], 'family': p['family'], 'arm_token': p['arm_token'], 'loop': p['loop'],
         'format': p['format'], 'kind': p['kind'], 'values_gen': p['values'].split(':')[1], 'KB_class': 'S1' if KB == 1 else 'S2',
         'count_found': c is not None, 'phi_found': ph is not None, 'frozen_forecast_found': f is not None,
         'frozen_W_over_idle': w, 'frozen_J_over_idle_per_gemm': j, 'energy_forecast': 'yes' if ok else 'NOT FORECAST'}
    rows.append(r)
    if not ok:
        nf.append(r)
res = {'what': ("E213's registered points against MM1-v3's switch-route coverage and frozen energy forecasts (desk; E213's registration only, "
                'no E213 datum)'),
       'sources': {'points': 'tools/claims-v3/e213/points-e213.csv (GitHub main 6efdb002)',
                   'arm_A_forecasts': 'tools/matmul/mm1/v3/out/mm1_v3_e213.json (sha256 932c5a18..., MM1-v3 landed b1493082)',
                   'arm_B_forecasts': 'tools/claims-v3/e213/forecast-e213b-v3.json (registered 291c8201)'},
       'python': sys.version.split()[0], 'n_points': len(rows), 'n_energy_forecast': len(rows) - len(nf),
       'not_forecast_for_want_of_a_count': nf,
       'tally': [{'arm': k[0], 'format': k[1], 'kind': k[2], 'status': k[3], 'n': v} for k, v in sorted(tally.items())],
       'values_gens': sorted(set(r['values_gen'] for r in rows)), 'points': rows}
json.dump(res, open(OUT, 'w'), indent=1)
print(f"E213 points {len(rows)}; energy forecast by MM1-v3 {len(rows) - len(nf)}; NOT FORECAST for want of a count {len(nf)}")
for t in res['tally']:
    print(f"  arm {t['arm']} {t['format']:5s} {t['kind']:9s} {t['status']:13s} {t['n']}")
print('value generators:', res['values_gens'])
