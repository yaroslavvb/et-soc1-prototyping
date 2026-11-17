#!/usr/bin/env python3
"""MM1-v2: the README's tables from the outputs (out/). Desk; reads files only (and the vendored E208 checks for the measured peaks).

    /usr/bin/python3 -I -B summary_v2.py --out <dir>      reads <dir>/*.json, *.csv; writes <dir>/summary_v2.json and <dir>/summary_v2.md
fix-mm1v2 (Tue 17 Nov 2026) added: the fold fits' record (the pin rule's pins, the starts' training costs and held-out errors, local
minima), the frozen all-data fit beside its converged refit and what that refit would move in E209's forecasts, the governor's base rate and
misses, the clock routes on E209's points, E208's measured peaks on aifoundry2's card, and the held-out cases that recur in another
experiment.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import copy
import csv
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_e208 as D8  # noqa: E402
import e209_v2 as E9M  # noqa: E402
import mm1_core_v2 as C  # noqa: E402
import mm1_v2 as M2  # noqa: E402

CARDS = ['aifoundry3 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry1 card 0']


def fold_report(ff):
    """per fold: the pins, the lowest training cost, how many starts reached it (within 1e-5), the held-out spread among those, and every
    distinct training cost (to 1e-4) with its held-out rms: a spread at the best cost would mean a direction still flat"""
    out = collections.OrderedDict()
    for k, v in ff.items():
        best = min(s['train_cost'] for s in v['starts'])
        near = [s for s in v['starts'] if s['train_cost'] <= best + 1e-5]
        hs = [s['heldout_rms_pct'] for s in near]
        dist = collections.OrderedDict()
        for s in sorted(v['starts'], key=lambda s: s['train_cost']):
            dist.setdefault('%.4f' % s['train_cost'], set()).add(s['heldout_rms_pct'])
        out[k] = {'pins': v['pins'], 'best_cost': best, 'starts_at_best': len(near), 'starts': len(v['starts']),
                  'heldout_spread_at_best_pct': round(max(hs) - min(hs), 2), 'distinct_costs': {c: sorted(h) for c, h in dist.items()}}
    return out


def e208_peaks():
    """E208's measured peaks on aifoundry2 card 0, from the vendored checks' C5 lines (board_max_w, die_max_c, latch_first_max_c)"""
    out = {}
    for s in ('a2c0-S1', 'a2c0-S2'):
        txt = open(os.path.join(HERE, 'inputs', 'e208', f'{s}__checks-e208-{s}.txt')).read()
        m = re.search(r'C5_stops PASS:.*?board_max_w ([0-9.]+);.*?die_max_c ([0-9.]+); latch_first_max_c \((\d+), (\d+)\)', txt)
        out[s] = {'board_max_w': float(m.group(1)), 'die_max_c': float(m.group(2)), 'latch_first_max_c': [int(m.group(3)), int(m.group(4))]}
    return out


def st(e):
    e = np.asarray([x for x in e if x is not None], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2)}


def fmt(s):
    return f"{s['rms_pct']} ({s['bias_pct']:+}) n={s['n']}" if s else '-'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    O = os.path.abspath(a.out)
    U = json.load(open(os.path.join(O, 'unread_e208.json')))
    H = json.load(open(os.path.join(O, 'holdout_v2.json')))
    G = json.load(open(os.path.join(O, 'governor_v2.json')))
    RL = json.load(open(os.path.join(O, 'rest_v2.json')))
    P = json.load(open(os.path.join(O, 'mm1_v2_params.json')))
    E9 = json.load(open(os.path.join(O, 'mm1_v2_e209.json')))
    S = {'unread': {}, 'heldout': {}, 'e209': {}}
    QT = ['cycles an op, wall', "cycles an op, the counter's mean", 'seconds a GEMM', 'W = J over idle given t (>= 3 W)',
          'J over idle, seconds forecast (>= 3 W)', 'J at rest given t', 'J at rest, seconds forecast']
    L = ['# MM1-v2: the tables (desk; error = forecast / measured - 1, rms % (bias %) and n)', '']
    L += ['## 1. MM1-v1 and MM1-v0 on E208, UNREAD (unchanged; every committed run with a time figure)', '',
          '| model | card | ' + ' | '.join(QT) + ' | W under 3 W (W rms) |', '|---' * (len(QT) + 3) + '|']
    for m in ('v1', 'v0'):
        for g in ['all', 'aifoundry2 card 0', 'aifoundry1 card 1', 'aifoundry1 card 0']:
            b = U[f'stats {m} per run'][g]
            S['unread'][f'{m} | {g}'] = {q: b.get(q) for q in QT}
            u = b.get('W over idle under 3 W (watts)')
            L.append(f'| MM1-{m} | {g} | ' + ' | '.join(fmt(b.get(q)) if b.get(q) else 'NOT FORECAST' for q in QT) + f" | {u['rms_W'] if u else '-'} |")
    L += ['', 'aifoundry1 card 0, borrowed footing (aifoundry2\'s card terms; not a forecast of either model): ' +
          '; '.join(f"{m}: W|t {fmt(v.get('W = J over idle given t (>= 3 W)'))}" for m, v in
                    U['aifoundry1 card 0, borrowed footing (aifoundry2 card terms; NOT a forecast of either model)'].items()), '']
    # held out
    L += ['## 2. Held out, the same points and folds for v2 and for MM1-v1\'s form refitted (cold starts; every constant refitted per fold)', '']
    T2, T1 = H['time v2'], H['time v1form']
    rows = [('cycles (wall), in sample', 'in_sample', 'all'), ('cycles, LOEO all', 'loeo', 'all'), ('cycles, LOEO the 888 pre-E208 points', 'loeo', 'pre-E208 (888)'),
            ('cycles, LOEO E208 (its fold)', 'loeo', 'E208'), ('cycles, LOEO E206 (its fold)', 'loeo', 'E206'), ('cycles, LOEO subsets', 'loeo', 'subsets'),
            ('cycles, LOCO all', 'loco', 'all')]
    L += ['| quantity | v2 | v1 form refitted | v2 without F2 | v2 with one chi |', '|---|---|---|---|---|']
    for lab, tag, g in rows:
        L.append(f'| {lab} | {fmt(T2[tag].get(g))} | {fmt(T1[tag].get(g))} | {fmt(H["time v2_noF2"][tag].get(g))} | {fmt(H["time v2_onechi"][tag].get(g))} |')
        S['heldout'][lab] = {'v2': T2[tag].get(g), 'v1form': T1[tag].get(g), 'v2_noF2': H['time v2_noF2'][tag].get(g), 'v2_onechi': H['time v2_onechi'][tag].get(g)}
    for c in CARDS:
        lab = f'cycles, LOCO {c}'
        L.append(f'| {lab} | {fmt(T2["loco_by_card"].get(c))} | {fmt(T1["loco_by_card"].get(c))} | {fmt(H["time v2_noF2"]["loco_by_card"].get(c))} | {fmt(H["time v2_onechi"]["loco_by_card"].get(c))} |')
        S['heldout'][lab] = {'v2': T2['loco_by_card'].get(c), 'v1form': T1['loco_by_card'].get(c)}
    by2 = '; '.join('%s %s' % (k, v['rms_pct']) for k, v in T2['loeo_by_exp'].items())
    by1 = '; '.join('%s %s' % (k, v['rms_pct']) for k, v in T1['loeo_by_exp'].items())
    L.append('| cycles, LOEO by experiment | ' + by2 + ' | ' + by1 + ' | | |')
    L.append('')
    E2 = H['energy v2']['stats']
    E1 = H['energy v1form']['stats']
    EC = H['energy v2 on v1form points']
    L += ['| energy (same points: those v1\'s form prices) | v2 | v1 form refitted |', '|---|---|---|']
    for tag in ('in', 'LOEO', 'LOCO'):
        for q in ('W = J over idle given t (>= 3 W)', 'J over idle t forecast (>= 3 W)', 'J at rest given t', 'J at rest t forecast'):
            for g in ('all', 'E208 aifoundry2 card 0', 'E208 aifoundry1 card 1', 'E208 aifoundry1 card 0', 'aifoundry3 card 0'):
                k = f'{tag} | {q} | {g}'
                if k in EC or k in E1:
                    L.append(f'| {tag}, {q}, {g} | {fmt(EC.get(k))} | {fmt(E1.get(k))} |')
                    S['heldout'][k] = {'v2_same_points': EC.get(k), 'v1form': E1.get(k), 'v2_all_points': E2.get(k)}
    L.append(f"| ones (v2 only; v1's form has no ones price), LOCO W given t | {fmt(E2.get('LOCO | W = J over idle given t (>= 3 W) | ones'))} | NOT FORECAST |")
    L.append('')
    # counter's mean (held out, E208): wall prediction / rho
    R8 = D8.runs()
    pt = {r['id']: r for r in csv.DictReader(open(os.path.join(O, 'points_time_v2.csv')))}
    Mx = M2.Model(P)
    cm = {'v2_in': [], 'v2_loeo': [], 'v2_loco': []}
    T8 = {}
    for r in R8:
        T8.setdefault(f"E208|{ {'a2c0': 'a2', 'a1c1': 'c1', 'a1c0': 'c0'}[r['card_key']] }|{r['case']}", []).append(r)
    for pid, rs in T8.items():
        if pid not in pt:
            continue
        p = pt[pid]
        o = Mx.predict(rs[0]['card'], rs[0]['arm'], rs[0]['fmt'], rs[0]['kind'], rs[0]['mask'], float(p['f_mhz']), ops=rs[0]['ops'], minions=rs[0]['minions'])
        rho = o['rho_wall_over_mean']
        meas = float(np.mean([r['cyc_mean'] for r in rs]))
        for k, col in (('v2_in', 'v2_in'), ('v2_loeo', 'v2_loeo'), ('v2_loco', 'v2_loco')):
            cm[k].append(float(p[col]) / rho / meas - 1)
    S['heldout']["counter's mean, E208 (one point a card and case)"] = {k: st(v) for k, v in cm.items()}
    L.append("Counter's mean on E208 (v2's wall / its rho): " + '; '.join(f'{k} {fmt(st(v))}' for k, v in cm.items()))
    L.append('')
    # the fold fits (fix-mm1v2): the pin rule, every start converged, local minima; the all-data fit frozen beside its converged refit
    rule = H.get('fold_fit_rule', {})
    L += ['### The fold fits (fix-mm1v2): the pin rule, every start converged, the lowest training cost kept', '',
          f"- pin rule (constant: the experiment that alone identifies it; pinned at 0 in a fold without it): {rule.get('pin_rule')}; "
          f"{len(rule.get('starts', []))} cold starts a fold"]
    S['fold_fits'] = {}
    for form in ('v2', 'v1form', 'v2_noF2', 'v2_onechi'):
        fr = fold_report(H['time ' + form]['fold_fits'])
        S['fold_fits'][form] = fr
        pinned = '; '.join(f"{k} {v['pins']}" for k, v in fr.items() if v['pins']) or 'none'
        spread = max(v['heldout_spread_at_best_pct'] for v in fr.values())
        minima = '; '.join(f"{k}: " + ', '.join(f"cost {c} -> {'/'.join(str(x) for x in h)}%" for c, h in v['distinct_costs'].items())
                           for k, v in fr.items() if len(v['distinct_costs']) > 1) or 'none'
        ac = H['time ' + form]['all_data_converged']
        L.append(f"- {form}: pinned folds {pinned}; largest held-out spread among the starts at the best cost {spread} pt; folds whose starts end at "
                 f"different training costs (cost -> held-out rms): {minima}; all-data fit frozen cost {ac['frozen_train_cost']} (in sample "
                 f"{ac['in_sample_rms_pct_frozen']}%) against converged {min(s['train_cost'] for s in ac['converged']['starts'])} "
                 f"({ac['in_sample_rms_pct_converged']}%)")
        S['fold_fits'][form + ' all-data'] = {k: v for k, v in ac.items() if k != 'theta_converged'}
    prof = H['time v2'].get('profiles') or {}
    S['fold_fits']['v2 profiles (the pinned constant held at each value, the rest refitted)'] = prof
    for k, rows in prof.items():
        cn = k.split(' | ')[1]
        c = [r['train_cost'] for r in rows]
        h = [r['heldout_rms_pct'] for r in rows]
        hs = [r['heldout_subsets_rms_pct'] for r in rows if r['heldout_subsets_rms_pct'] is not None]
        L.append(f"- v2 profile {k}: {cn} over {[r[cn] for r in rows]}: training cost {min(c)}-{max(c)}; held out {min(h)}-{max(h)}%"
                 + (f", its subsets {min(hs)}-{max(hs)}%" if hs else ''))
    # what the converged all-data refit would move in E209's forecasts at 799 MHz (a record; the frozen fit stays)
    Pc = copy.deepcopy(P)
    Pc['time']['theta'] = dict(H['time v2']['all_data_converged']['theta_converged'])
    Mc = M2.Model(Pc)
    dcyc, dw = [], []
    for r in csv.DictReader(open(os.path.join(O, 'e209_points.csv'))):
        es, ps = E9M.specs(r['fmt'], r['kind'])
        a0 = Mx.predict(E9M.CARD, r['arm'], r['fmt'], r['kind'], r['mask'], E9M.F_TOP, ops=int(r['ops']), minions=int(r['minions']), e_res_spec=es, phi_spec=ps)
        a1 = Mc.predict(E9M.CARD, r['arm'], r['fmt'], r['kind'], r['mask'], E9M.F_TOP, ops=int(r['ops']), minions=int(r['minions']), e_res_spec=es, phi_spec=ps)
        dcyc.append(a1['cycles_per_op_wall'] / a0['cycles_per_op_wall'] - 1)
        if 'W_over_idle' in a0:
            dw.append(a1['W_over_idle'] / a0['W_over_idle'] - 1)
    S['e209_if_all_data_converged'] = {'cycles': {'n': len(dcyc), 'rms_pct': round(float(np.sqrt(np.mean(np.square(dcyc)))) * 100, 4),
                                                  'max_abs_pct': round(float(np.max(np.abs(dcyc))) * 100, 4)},
                                       'W_over_idle': {'n': len(dw), 'rms_pct': round(float(np.sqrt(np.mean(np.square(dw)))) * 100, 4),
                                                       'max_abs_pct': round(float(np.max(np.abs(dw))) * 100, 4)}}
    L.append(f"- E209's v2 forecasts at 799 MHz if the all-data fit were the converged refit (a record; the frozen fit stays): cycles "
             f"{S['e209_if_all_data_converged']['cycles']['rms_pct']}% rms (max {S['e209_if_all_data_converged']['cycles']['max_abs_pct']}%), W over idle "
             f"{S['e209_if_all_data_converged']['W_over_idle']['rms_pct']}% rms (max {S['e209_if_all_data_converged']['W_over_idle']['max_abs_pct']}%) on "
             f"{len(dcyc)} / {len(dw)} points")
    # held-out cases that recur in another experiment (LOEO does not hold their case out; LOCO does)
    case_exps = collections.defaultdict(set)
    for r in pt.values():
        case_exps[(r['card'], r['arm'], r['fmt'], r['kind'], r['mask'])].add(r['exp'])
    tw = collections.OrderedDict()
    for ex in ('E206', 'E208'):
        hit = sorted({k for k, v in case_exps.items() if ex in v and len(v) > 1})
        tw[ex] = {'n_cases': len(hit), 'cases': ['%s %s %s %s %s in %s' % (k[0], k[1], k[2], k[3], k[4], '/'.join(sorted(case_exps[k] - {ex}))) for k in hit]}
    S['heldout']['LOEO cases also in another experiment'] = tw
    L.append('- LOEO cases that recur in another experiment (that experiment trains in the fold): ' +
             '; '.join(f"{ex} {v['n_cases']}" for ex, v in tw.items()) + ' (one point a card and case; LOCO holds every case of its card out)')
    L.append('')
    # governor and rest
    L += ['## 3. The governor clock model (post hoc, E208 aifoundry2 runs only) and the rest law', '',
          f"- loop on measured powers: t_climb {G['constants']['t_climb']:.3f} s, tau {G['constants']['tau']:.3f} s (E64: 1.3 s), P_th {G['constants']['P_th']:.2f} W (TDP 65 W), "
          f"k_die {G['constants']['k_die']:.4f} C/W; capped {G['fit']['capped_agree']}; burst mean clock rms {G['fit']['f_burst_mean_rms_mhz']} MHz (bias {G['fit']['f_burst_mean_bias_mhz']})",
          f"- the chain (v2's own powers into the loop; the clock-forecast route): P_th {G['chain']['P_th_chain_W']:.1f} W; capped {G['chain']['capped_agree']}; burst mean clock rms "
          f"{G['chain']['f_burst_mean_rms_mhz']} MHz (bias {G['chain']['f_burst_mean_bias_mhz']})"]
    for c, v in RL.items():
        L.append(f"- rest law {c}: {v['source'][:90]}; T0 forecast {v['T0_forecast_c']:.1f} C; on E208's rests {v.get('on_E208_rests')}")
    # the base rate (fix-mm1v2): how often 'never capped' would agree, and the runs the model misses
    gr = G['rows']
    n_cap = sum(1 for r in gr if r['capped_meas'])
    miss = [r for r in gr if r['capped_meas'] != r['capped_sim']]
    cr = {r['id']: r for r in G['chain']['rows']}
    miss_c = [r for r in gr if r['capped_meas'] != cr[r['id']]['capped_chain']]
    base = {'n_runs': len(gr), 'measured_capped': n_cap, 'never_capped_agrees': len(gr) - n_cap,
            'model_on_measured_powers_agrees': len(gr) - len(miss), 'chain_agrees': len(gr) - len(miss_c),
            'misses_on_measured_powers': [{'id': r['id'], 'capped_meas': r['capped_meas'], 'frac_800_meas': r['frac_meas'], 'P800_meas_W': r['P800_meas'],
                                           'die_max_meas_c': r['die_max_meas']} for r in miss],
            'misses_in_the_chain': [{'id': r['id'], 'capped_meas': r['capped_meas'], 'P800_chain_W': cr[r['id']]['P800_chain'], 'P800_meas_W': r['P800_meas']}
                                    for r in miss_c],
            'out_of_sample': 'NOT RUN (E190 arm A, E194 and E200 ran on this card under its governor; none was read)',
            'telemetry': "the vendored telemetry files (inputs/e208/a2c0-S*__telemetry.jsonl.gz) are read by no script here"}
    S['governor_base_rate'] = base
    L.append(f"- base rate: {n_cap} of {len(gr)} runs measured capped, so 'never capped' agrees on {len(gr) - n_cap}; the loop agrees on "
             f"{base['model_on_measured_powers_agrees']} on measured powers and {base['chain_agrees']} in the chain; misses on measured powers: "
             + ('; '.join(f"{m['id']} (capped {m['capped_meas']}, 800 MHz share {m['frac_800_meas']}, launch power {m['P800_meas_W']} W, die max "
                          f"{m['die_max_meas_c']} C)" for m in base['misses_on_measured_powers']) or 'none')
             + '; in the chain: ' + ('; '.join(f"{m['id']} (capped {m['capped_meas']}, v2's power {m['P800_chain_W']} W against {m['P800_meas_W']} W)"
                                               for m in base['misses_in_the_chain']) or 'none')
             + f"; out of sample: {base['out_of_sample']}; {base['telemetry']}")
    S['governor'] = {'constants': G['constants'], 'fit': G['fit'], 'chain': {k: v for k, v in G['chain'].items() if k != 'rows'}}
    S['rest'] = RL
    L.append('')
    # E209
    v1 = {r['id']: r for r in csv.DictReader(open(os.path.join(O, 'mm1_v1_e209.csv')))}
    v2 = {r['id']: r for r in csv.DictReader(open(os.path.join(O, 'mm1_v2_e209.csv')))}
    ff = {r['id']: r for r in csv.DictReader(open(os.path.join(O, 'f1f2_e209.csv')))}
    gaps = {'cycles v1/v2': [], 'cycles F1@800/v2': [], 'W v1/v2': [], 'W F1@800/v2': [], 'W F2@800/v2': []}
    for k, r in v2.items():
        c2 = float(r['cyc_wall@799'])
        gaps['cycles v1/v2'].append(math.log(float(v1[k]['cyc_wall@799']) / c2))
        gaps['cycles F1@800/v2'].append(math.log(float(ff[k]['F1_cycles_per_op@800']) / c2))
        if r['W_over@799']:
            w2 = float(r['W_over@799'])
            if v1[k]['W_over@799']:
                gaps['W v1/v2'].append(math.log(float(v1[k]['W_over@799']) / w2))
            if ff[k].get('F1_W_over@800'):
                gaps['W F1@800/v2'].append(math.log(float(ff[k]['F1_W_over@800']) / w2))
            if ff[k].get('F2_W_over@800'):
                gaps['W F2@800/v2'].append(math.log(float(ff[k]['F2_W_over@800']) / w2))
    S['e209'] = {'n_points': E9['n_points'], 'n_runs': E9['n_runs_planned'], 'planning_card_minutes': E9['planning_card_minutes'],
                 'predicted_gap_rms_log_pct': {k: (round(float(np.sqrt(np.mean(np.square(v)))) * 100, 1), len(v)) for k, v in gaps.items()},
                 'capped_forecast': [k for k, r in v2.items() if r['clock_fc_capped'] == 'True'],
                 'max_pred_board_top_W': max(float(r['pred_board_top_W']) for r in v2.values() if r['pred_board_top_W']),
                 'max_pred_die_burst_c': max(p['point']['pred_die_peak_burst_c'] for p in E9['rows'] if p['point']['pred_die_peak_burst_c']),
                 'max_pred_die_3proc_c': max(p['point']['pred_die_peak_3proc_c'] for p in E9['rows'] if p['point']['pred_die_peak_3proc_c'])}
    # the two clock routes on E209's points (fix-mm1v2): where the forecast win-view clock is the tabulated 799.0 MHz column
    win = collections.Counter(r['clock_fc_win_mhz'] for r in v2.values())
    S['e209']['clock_routes'] = {'forecast_win_clock_mhz_counts': dict(win), 'capped_forecast': S['e209']['capped_forecast'],
                                 'how': ("with the clock forecast, a point whose forecast win-view clock is 799.0 MHz takes the 799.0 MHz column's cycles, "
                                         "seconds and W, which is what 'given the measured clock' gives a run measured at 799.0 MHz; the routes part only "
                                         "where a run's measured clock differs, in the capped flag and in the burst-mean columns")}
    pk = e208_peaks()
    S['e209']['e208_measured_peaks_aifoundry2'] = pk
    L += ['## 4. E209 (planning and the predicted gaps between the models; not a score)', '',
          f"- {E9['n_points']} points (distinct cases), {E9['n_runs_planned']} runs planned; card-minutes: {E9['planning_card_minutes']}",
          f"- predicted rms |ln| gaps on the same points: {S['e209']['predicted_gap_rms_log_pct']}",
          f"- forecast capped: {S['e209']['capped_forecast']}; highest forecast board at the top point {S['e209']['max_pred_board_top_W']:.1f} W; "
          f"die at most {S['e209']['max_pred_die_burst_c']:.1f} C (6 s burst), {S['e209']['max_pred_die_3proc_c']:.1f} C (three processes, desk); stops 85 W x3 / 80 C",
          f"- the clock routes: forecast win-view clock {dict(win)} (MHz: points); so with the clock forecast every point's cycles, seconds and W are "
          f"the 799.0 MHz column, as given a measured 799.0 MHz; the routes part only in the capped flag ({S['e209']['capped_forecast']}) and the burst means",
          "- E208 measured on this card (the planning bound; vendored checks, C5): " +
          '; '.join(f"{s} board max {v['board_max_w']} W, die max {v['die_max_c']:.0f} C, hottest-sensor latch {v['latch_first_max_c']} C" for s, v in pk.items())]
    json.dump(S, open(os.path.join(O, 'summary_v2.json'), 'w'), indent=1, default=float)
    open(os.path.join(O, 'summary_v2.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
