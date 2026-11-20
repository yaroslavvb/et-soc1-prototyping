#!/usr/bin/env python3
"""lnc-form step 7: the README's tables from the frozen and recorded files (no new number is fitted here)."""
import csv, json, os
import numpy as np
L = os.environ['LNC_FORM_DIR']
LAND = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'gemmlnc-af4')
O = json.load(open(os.path.join(L, 'work', 's02_fit.json')))
D = json.load(open(os.path.join(L, 'work', 's01_points.json')))['points']
out = []
def P(s=''): out.append(s)
P('### Table 2. Every declared form: constants (all data), in sample, held out, the pooled guard, the placebo, the keep rule')
P()
P('| form | c1, c2 (pJ a line) | in sample rms (bias) | **LOEO** rms (bias) | LOCO rms (bias) | LOPO rms (bias) | pooled MM1 LOEO no twins | placebo wins / 100 | kept |')
P('|---|---|---|---|---|---|---|---|---|')
keep = O['keep_rule']
for f in ['F3r', 'F1r', 'F2r', 'F4r', 'STEPr', 'AF1', 'AF2', 'AF3', 'AF4']:
    r = O['forms'][f]; pl = O['placebo'][f]
    k = keep.get(f, {}).get('kept')
    P('| %s | %s | %.2f%% (%+.2f) | **%.2f%% (%+.2f)** | %.2f%% (%+.2f) | %.2f%% (%+.2f) | %.3f%% | %s | %s |' % (
        ('**AF4**' if f == 'AF4' else f), ', '.join('%.1f' % x for x in r['constants_all_data_pJ']), *r['in_sample'], *r['LOEO'], *r['LOCO'],
        *r['LOPO'], O['pooled_guard']['forms'][f][0], (pl['wins_of_100'] if isinstance(pl, dict) else 'n/a'),
        ('comparator' if f == 'F3r' else ('**KEPT**' if k else 'no'))))
P()
P('MM1-v3.2 as landed (F3 at c1 247.7, c2 448.6 pJ): pooled %.3f%% (n %d; its own record %.3f%%, n %d, plus the 22 E216 and E218 gemmLnc points at its frozen forecasts).' % (
    O['pooled_guard']['MM1-v3.2'][0], O['pooled_guard']['MM1-v3.2'][1], *O['pooled_guard']['check_MM1-v3.2_record_no_twins_ge3W']))
P()
P('### Table 3. Held out by fold: rms (bias) over each fold\'s gemmLnc points, W over idle given the measured op time')
P()
P('| fold | n | MM1-v3.2 as landed | F3r (F3 refitted) | AF1 | AF2 | AF3 | **AF4** |')
P('|---|---|---|---|---|---|---|---|')
v32rec = {}
import csv as _c
rows = list(_c.DictReader(open(os.path.join(L, 'work', 'repo', 'tools', 'matmul', 'mm1', 'v3.2', 'out', 'points_energy_v32.csv'))))
for r in rows:
    if r['gemmLnc'] == '1':
        v32rec[r['id']] = float(r['v32_LOEO_W_given_t']) / float(r['meas_W_over_idle']) - 1
v32 = {p['id']: (v32rec[p['id']] if p['id'] in v32rec else p['v32_W_given_t'] / p['w'] - 1) for p in D}
def rb(ids):
    e = np.array([v32[i] for i in ids]); return 100*np.sqrt(np.mean(e*e)), 100*np.mean(e)
for g in ['E211', 'E213', 'E215', 'E216', 'E218']:
    ids = [p['id'] for p in D if p['exp'] == g]
    cells = ['%.2f (%+.2f)' % tuple(O['forms'][f]['LOEO_by_fold'][g][:2]) for f in ['F3r', 'AF1', 'AF2', 'AF3', 'AF4']]
    P('| LOEO %s | %d | %.2f (%+.2f) | %s | **%s** |' % (g, len(ids), *rb(ids), ' | '.join(cells[:-1]), cells[-1]))
for g in ['E212', 'E214', 'E217', 'E219']:
    P('| LOEO %s | 0 | no gemmLnc point: the term is 0 at every point of the fold, so the fold equals MM1-v3.2 there | | | | | |' % g)
ids = [p['id'] for p in D]
cells = ['%.2f (%+.2f)' % tuple(O['forms'][f]['LOEO'][:2]) for f in ['F3r', 'AF1', 'AF2', 'AF3', 'AF4']]
P('| **LOEO, all 36** | 36 | %.2f (%+.2f) | %s | **%s** |' % (*rb(ids), ' | '.join(cells[:-1]), cells[-1]))
for g in ['aifoundry3 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0']:
    ids = [p['id'] for p in D if p['card'] == g]
    cells = ['%.2f (%+.2f)' % tuple(O['forms'][f]['LOCO_by_fold'][g][:2]) for f in ['F3r', 'AF1', 'AF2', 'AF3', 'AF4']]
    P('| LOCO %s | %d | %.2f (%+.2f) | %s | **%s** |' % (g, len(ids), *rb(ids), ' | '.join(cells[:-1]), cells[-1]))
P()
P('MM1-v3.2 as landed: its own LOEO fold forecasts at the 14 points in its fit (E211, E213, E215), and its frozen forecasts at the measured op time at E216\'s and E218\'s 22 points (outside its fit).')
P()
P('### Table 4. Every gemmLnc point: the features, the measured W over idle, and the held-out errors (forecast / measured - 1, %)')
P()
P('| point | token | card | NB | R4 | first | measured W | MM1-v3.2 as landed | F3r LOEO | **AF4 LOEO** | AF4 LOCO | AF4 in sample |')
P('|---|---|---|---|---|---|---|---|---|---|---|---|')
fe = {r['id']: r for r in O['features_per_point']}
A = {r['id']: r for r in O['forms']['AF4']['per_point']}
F3 = {r['id']: r for r in O['forms']['F3r']['per_point']}
for p in D:
    i = p['id']
    P('| %s | %s | %s | %d | %.1f | %.2f | %.2f | %+.1f | %+.1f | **%+.1f** | %+.1f | %+.1f |' % (i, p['arm'], p['card'], p['NB'], fe[i]['R4'], fe[i]['first'],
      p['w'], 100*v32[i], F3[i]['LOEO_err_pct'], A[i]['LOEO_err_pct'], A[i]['LOCO_err_pct'], A[i]['in_sample_err_pct']))
P()
P('The cooperative twins (term 0 for every form; MM1-v3.2 at the measured op time): n %d, rms %.2f%%, bias %+.2f%%.' % (
    O['twins_summary']['n'], O['twins_summary']['rms_pct'], O['twins_summary']['bias_pct']))
P()
# E220 summary
fr = list(csv.DictReader(open(os.path.join(LAND, 'forecasts-e220-af4.csv'))))
P('### Table 6. The frozen E220 forecasts at its gemmLnc points (arm A at 600 MHz, arm B at 799 MHz; every cooperative point equals MM1-v3.2)')
P()
P('| arm | id | token | R4 regime | MM1-v3.2 W over idle | F3 in it | AF4 term | **MM1-v3.2 + AF4 W over idle** | J over idle a GEMM, t forecast | J at rest a GEMM | planning peak, plain / E220 form | stop |')
P('|---|---|---|---|---|---|---|---|---|---|---|---|')
J = json.load(open(os.path.join(LAND, 'forecasts-e220-af4.json')))
feat = {(r['arm'], r['id'], r['f_mhz']): r.get('features') for r in J['rows']}
for r in fr:
    if not r['token'].startswith('gemmLnc'): continue
    if not ((r['arm'] == 'A' and r['f_mhz'] == '600') or (r['arm'] == 'B' and r['f_mhz'] == '799')): continue
    ft = feat[(r['arm'], r['id'], float(r['f_mhz']))]
    reg = 'L3-resident' if ft['Lres'] else ('none (R4 0)' if ft['R4'] == 0 else ('A fresh into the row' if ft['m'] == 0 else 'near reuse misses the L3'))
    P('| %s | %s | %s | %s, R4 %.1f | %.2f | %.2f | %.2f | **%.2f** | %.4g | %.4g | %.1f / %.1f | %s |' % (r['arm'], r['id'], r['token'], reg, ft['R4'],
      float(r['MM1-v3.2_W_over_idle']), float(r['MM1-v3.2_F3_W']), float(r['term_AF4_W']), float(r['W_over_idle']),
      float(r['J_over_idle_per_gemm_t_forecast']), float(r['J_at_rest_per_gemm_t_forecast']), float(r['PP_with_term_W']),
      float(r['PP_with_term_E220_form_W']), r['board_stop_W']))
open(os.path.join(L, 'work', 's07_tables.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
