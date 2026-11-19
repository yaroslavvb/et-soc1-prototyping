#!/usr/bin/env python3
"""lnc-energy: the README's tables, from the work files only (s01_points.json, s02_rails_points.json, s03_walk.json, s04_fit.json) and the frozen
forecasts JSON. Prints Markdown. Standard library; /usr/bin/python3 3.12.3."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WK = os.environ.get('LNC_WORK') or os.path.join(HERE, 'work')
FR = os.environ.get('LNC_OUT') or HERE
pts = json.load(open(os.path.join(WK, 's01_points.json')))
rails = json.load(open(os.path.join(WK, 's02_rails_points.json')))
walk = {r['shape']: r for r in json.load(open(os.path.join(WK, 's03_walk.json')))['rows']}
fit = json.load(open(os.path.join(WK, 's04_fit.json')))
fz = json.load(open(os.path.join(FR, 'forecasts-gemmlnc-e215.json')))

P = {p['id']: p for p in pts}
PAIRS = [('E211|c01c', 'E211|w01m', 'E211', 'c01c', 'w01m'), ('E211|c02c', 'E211|w06m', 'E211', 'c02c', 'w06m'),
         ('E213|a3|a087', 'E213|a3|a088', 'E213A', 'a087', 'a088'), ('E213|a3|a086', 'E213|a3|a083', 'E213A', 'a086', 'a083'),
         ('E213|a3|a079', 'E213|a3|a076', 'E213A', 'a079', 'a076'), ('E213|a3|a075', 'E213|a3|a006', 'E213A', 'a075', 'a006'),
         ('E213|a3|a082', 'E213|a3|a030', 'E213A', 'a082', 'a030'), ('E213|c1|k40', 'E213|c1|k41', 'E213B', 'k40', 'k41'),
         ('E213|c1|k37', 'E213|c1|k06', 'E213B', 'k37', 'k06')]
print('### Table 1. The 9 committed gemmLnc points and their rgm136 gemmL twins (measured; MM1-v3.1 in sample, given the measured op time)\n')
print('| point | shape, format, card | measured W over idle: gemmLnc / twin | MM1-v3.1: gemmLnc / twin | measured / MM1-v3.1: gemmLnc / twin | '
      'wall cycles an op: gemmLnc / twin | excess over MM1-v3.1, nJ a minion-op |')
print('|---|---|---|---|---|---|---|')
for a, b, e, ia, ib in PAIRS:
    x, y = P[a], P[b]
    exc = (x['w_meas'] - x['W_v31_csv_in']) / x['rate_minion_ops_per_s'] * 1e9
    print('| %s (%s) | %s %s, %s | %.2f / %.2f | %.2f / %.2f | %.3f / %.3f | %.1f / %.1f | %.2f |' % (
        ia, ib, x['arm'], x['fmt'], x['card'], x['w_meas'], y['w_meas'], x['W_v31_csv_in'], y['W_v31_csv_in'], x['w_meas'] / x['W_v31_csv_in'],
        y['w_meas'] / y['W_v31_csv_in'], x['cyc_meas'], y['cyc_meas'], exc))
print('\n### Table 2. Where the excess goes: W over idle by rail, gemmLnc minus its twin (measured, post hoc; medians in the reducers\' windows)\n')
print('| point | shape | board | minion rail | SRAM rail | NoC rail | NoC rail, nJ a minion-op | SRAM rail, nJ a minion-op |')
print('|---|---|---|---|---|---|---|---|')
for q in rails['pairs']:
    a = [p for p in PAIRS if p[2] == q['exp'] and p[3] == q['lnc']][0]
    x = P[a[0]]
    r = x['rate_minion_ops_per_s']
    d = q['delta']
    # the twin's rail per op is taken at the twin's own rate; the excess per op = gemmLnc's rail / its rate - the twin's rail / the twin's rate
    y = P[a[1]]
    nn = q['lnc_rails']['noc'] / r - q['twin_rails']['noc'] / y['rate_minion_ops_per_s']
    ss = q['lnc_rails']['sram'] / r - q['twin_rails']['sram'] / y['rate_minion_ops_per_s']
    print('| %s | %s | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f |' % (q['lnc'], x['arm'][7:], d['board'], d['minion'], d['sram'], d['noc'],
                                                                     nn * 1e9, ss * 1e9))
print('\n### Table 3. The walk (desk, exact streams; full mask): what the branch changes a shire-op\n')
print('| shape | what | footprint MB | reads a shire-op, gemmL / gemmLnc (lines) | duplicates (lines) | desk L2 hits, gemmL / gemmLnc (lines) | '
      'duplicates hitting the desk L2 | chip L3 strict 32 MB, A / B in-L3 share (both kernels) |')
print('|---|---|---|---|---|---|---|---|')
for shp, r in walk.items():
    d = r['derived_per_shire_op']
    l, n = r['l2_desk_shire0_gemmL'], r['l2_desk_shire0_gemmLnc']
    print('| %s | %s | %.0f | 192 / 1,024 | 832 (A 448, B 384) | %.0f / %.0f | %.3f | %.3f / %.3f |' % (
        shp, r['what'], r['footprint']['MB'], l['A_L2_lines_per_op'] + l['B_L2_lines_per_op'], n['A_L2_lines_per_op'] + n['B_L2_lines_per_op'],
        d['duplicates_that_hit_L2_desk_share'], r['l3_strict_32MB']['A_in_L3_share_distinct'], r['l3_strict_32MB']['B_in_L3_share_distinct']))
print('\n### Table 4. The candidate terms (post hoc; W over idle errors in %%, on the 9 points; MM1-v3.1 alone: rms %.2f%%, mean %.2f%%)\n' % (
    fit['v31_alone']['rms_pct'], fit['v31_alone']['mean_pct']))
print('| form | x | constants, pJ a line | in sample | LOPO | LORO (12 runs) | LOEO E211 out | LOEO E213 out | E213 arm A out | card 1 out | aifoundry3 out |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for f, r in fit['forms'].items():
    fo = r['folds']

    def g(k):
        v = fo[k]
        if isinstance(v, str):
            return v
        s = '%.2f' % v['rms_pct']
        if v.get('identified') is False:
            s += ' (NOT IDENTIFIED)'
        return s
    print('| %s | %s | %s | %.2f | %.2f | %.2f | %s | %s | %s | %s | %s |' % (
        f, ' + '.join(x for x in r['x'] if x), ', '.join('%.1f' % c for c in r['constants_pJ_per_line']), r['in_sample_rms_pct'], r['LOPO_rms_pct'],
        r['LORO_rms_pct'], g('LOEO E211 out'), g('LOEO E213 out'), g('LOEO-arm E213 arm A out'), g('LOCO aifoundry1 card 1 out (= LOEO-arm E213 arm B out)'),
        g('LOCO aifoundry3 card 0 out')))
print('\nper-point errors, chosen form %s, in sample: %s; LOPO: %s' % (fit['selection']['chosen'], fit['forms'][fit['selection']['chosen']]['in_sample_err_pct'],
                                                                  fit['forms'][fit['selection']['chosen']]['LOPO_err_pct']))
print('\n### Table 5. The frozen forecasts (MM1-v3.1 + gemmLnc term, form %s)\n' % fz['term']['form'])
print('| id | arm, card | shape | NB | MM1-v3.1 W over idle | term W | **W over idle** | A, B (W, W us) for given() | J over idle a GEMM | J at rest a GEMM '
      '(rest law, T0) | planning peak W | stop | margin W | within 3 W |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for o in fz['rows']:
    print('| %s%s | %s, %s | %s | %d | %.3f | %.3f | **%.3f** | %.4f, %.4f | %.5f | %.5f (%.2f W, %.1f C) | %.2f | %.0f W x3 | %.2f | %s |' % (
        o['id'], '' if o['role'].startswith('point') else ' (smoke)', o['arm'], o['card'], o['token'], o['NB'], o['v31_W_over_idle'], o['lnc_term_W'],
        o['lnc_W_over_idle'], o['lnc_A_W'], o['lnc_B_W_us'], o['lnc_J_over_idle'], o['lnc_J_at_rest'], o['rest_law_W'], o['rest_law_T0_c'],
        o['lnc_peak_planning_W'], o['stop_W'], o['margin_W'], 'YES' if o['within_3W_of_stop'] else 'no'))
print('\nother forms beside (REPORTED): ' + '; '.join('%s: F1 %.2f, F2 %.2f, F4 %.2f W (max-form peak %.2f W%s)' % (
    o['id'], o['F1_W_over_idle'], o['F2_W_over_idle'], o['F4_W_over_idle'], o['max_over_forms_peak_planning_W'],
    ', within 3 W' if o['within_3W_of_stop_any_form'] else '') for o in fz['rows']))
print('\nheld-out smokes (REPORTED): ' + '; '.join('%s: est %.2f W, v3.1 %.1f%%, F3 %.1f%%, analog E215 planning peak %.2f W (margin %.2f W)' % (
    s['id'], s['W_over_idle_est'], s['v31_err_pct'], s['F3_err_pct'], s['analog_E215_peak_planning_W'], s['analog_margin_planning_W'])
    for s in fz['heldout_smokes_e213_REPORTED']))
