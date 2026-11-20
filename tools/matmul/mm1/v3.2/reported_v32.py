#!/usr/bin/env python3
"""MM1-v3.2: section 8's REPORTED readings (never deciding a rule), from run_v32's records and the frozen E215 forecast files. Desk.

    /usr/bin/python3 -I -B reported_v32.py --out <run_v32's out dir>
  - the layout rule's full record (every candidate, condition, interval, placebo) is in out/layout/layout-rule-v32.json (step 2);
  - F3: c1 and c2 in every fold with their pins (decisions step 3); the frozen 'v3.1 + gemmLnc term' E215 forecasts
    (tools/matmul/mm1/v3.2-terms/gemmlnc/forecasts-gemmlnc-e215.csv) against E215's measured gemmLnc points beside MM1-v3.2's E215 fold;
  - E215 by family (P, C, R registered; L, S post hoc): MM1-v3.1's and MM1-v3's frozen blind forecasts (arm A: ../v3.1/out/e215/
    mm1_v31_e215.csv; arm B: tools/claims-v3/e215/forecast-e215b-v31.csv, -v3.csv), 'v3.1 + contention' (forecast-e215-v31-layout.csv),
    verify-lay's controls (controls-e215/v02_e215_controls.csv) and MM1-v3.2's E215 fold, per point, at the measured points (E215's
    scorer's MEASURED readings: the wall cycles an op = the kept runs' mean cycles_gemm / ops; W over idle = the mean p_work - p_rest; W given t
    = A + B / t_op at t_op = the measured wall cycles / 600 MHz);
  - the anchor route's LOCO and the ledger (v3-ledger refitted) LOEO / LOKO.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_v32 as RV  # noqa: E402

F, DV, EV = RV.F, RV.DV, RV.EV
REPO = RV.REPO
FORM, EFORM = RV.FORM, RV.EFORM


def stat(e):
    return F.stat(e)


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def e215_measured():
    """per E215 point (pid): the scorer's MEASURED readings over the kept runs (data_v32's reading of the runs)"""
    out = {}
    for arm in DV.e215_available():
        R, _ = DV.e215_runs(arm)
        by = collections.defaultdict(list)
        for r in R:
            by[r['pid']].append(r)
        for pid, rs in by.items():
            cw = float(np.mean([r['cw'] for r in rs]))
            out[(arm, pid)] = {'arm': arm, 'pid': pid, 'family': rs[0]['family'], 'reading': rs[0]['reading'], 'role': rs[0]['role'],
                               'case': rs[0]['case'], 'loop': rs[0]['loop'], 'token': rs[0]['arm'], 'fmt': rs[0]['fmt'], 'kind': rs[0]['kind'],
                               'mask': rs[0]['mask'], 'cw': cw, 't_op_us': cw / 600.0, 'W': float(np.mean([r['p_work'] - r['p_rest'] for r in rs])),
                               't_gemm': float(np.mean([r['t_gemm'] for r in rs])), 'n_runs': len(rs)}
    return out


def frozen_e215():
    """the frozen blind forecasts of E215's points by model: {(arm, pid): {model: {'cw', 'A', 'B'}}}"""
    reg = {(r['arm'], r['id']): r for r in DV.e215_registry()}
    key = {(r['arm'], f"{r['loop']}|{r['arm_token']}|{r['format']}|{r['kind']}|{r['shire_mask']}"): r['id'] for r in reg.values()}
    out = collections.defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(REPO, 'tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv'))):
        pid = key.get(('A', r['token']))
        if pid is None:
            continue
        out[('A', pid)]['MM1-v3.1'] = {'cw': fl(r['v31_cycles_wall']), 'A': fl(r['v31_W_A']), 'B': fl(r['v31_W_B_us'])}
        out[('A', pid)]['MM1-v3'] = {'cw': fl(r['v3_cycles_wall']), 'W_own_t': fl(r['v3_W_over_idle'])}
    for fn, m in (('forecast-e215b-v31.csv', 'MM1-v3.1'), ('forecast-e215b-v3.csv', 'MM1-v3')):
        p = os.path.join(REPO, 'tools/claims-v3/e215', fn)
        for r in csv.DictReader(open(p)):
            out[('B', r['id'])][m] = {'cw': fl(r['cycles_per_op_wall']), 'A': fl(r.get('A_W')), 'B': fl(r.get('B_W_us'))}
    for r in csv.DictReader(open(os.path.join(REPO, 'tools/matmul/mm1/v3.2-terms/gemmlnc/forecasts-gemmlnc-e215.csv'))):
        if r['role'].startswith('point'):
            out[(r['arm'], r['id'])]['v3.1 + gemmLnc term'] = {'cw': fl(r['v31_cycles_wall']), 'A': fl(r['lnc_A_W']), 'B': fl(r['lnc_B_W_us'])}
    for r in csv.DictReader(open(os.path.join(REPO, 'tools/matmul/mm1/v3.2-terms/layout/forecast-e215-v31-layout.csv'))):
        out[(r['e215_arm'], r['id'])]['v3.1 + contention'] = {'cw': fl(r['v31c_cycles_per_op_wall'])}
    for r in csv.DictReader(open(os.path.join(REPO, 'tools/matmul/mm1/v3.2-terms/layout/controls-e215/v02_e215_controls.csv'))):
        arm = 'A' if r['id'].startswith('a') else 'B'
        for fm in ('N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24'):
            out[(arm, r['id'])][f'verify-lay {fm}'] = {'cw': fl(r[f'REPORTED_{fm}_cycles_per_op_wall'])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    dec = json.load(open(os.path.join(out, 'decisions_v32.json')))
    rep = {'what': "DECLARED-v32.md section 8's REPORTED readings (never deciding a rule)"}
    rep['F3_by_fold'] = dec['steps']['step3']['F3_by_fold']
    rep['layout_rule_record'] = 'out/layout/layout-rule-v32.json (every candidate, condition, bootstrap interval, placebo; step 2 summary in decisions)'
    rep['layout_joint_refit'] = ('NOT RUN: section 3\'s rule chose none' if dec['steps']['step2']['enters'] == 'none'
                                 else 'NOT RUN (the slots were kept for the declared fits; section 8 allows NOT RUN)')
    acc = dec['steps']['step4']['acceptance']
    rep['anchor_route_LOCO'] = {'v32': acc['2']['anchor_route_REPORTED'], 'v3_refitted': acc['2']['v3_refitted_routes']['anchor']['pooled_no_anchor_points'],
                                'kc_by_card_v32': {c: v.get('kc_anchor') for c, v in acc['2']['v32_routes']['anchor']['folds'].items()}}
    lp = os.path.join(out, 'fits', 'v3refit', f'energy_{FORM}.json')
    ER = json.load(open(lp))
    if 'ledger' in ER['forms']:
        g = []
        X = None
        rep['ledger_folds_REPORTED'] = {fn: len(fd['test_idx']) for fn, fd in ER['forms']['ledger']['folds'].items()}
    # E215 by family
    M = e215_measured()
    if M:
        FZ = frozen_e215()
        TR = json.load(open(os.path.join(out, 'fits', f'time_{FORM}.json')))
        E32 = json.load(open(os.path.join(out, 'fits', 'v32', f'energy_{FORM}.json')))
        ids_t = TR['ids']
        fdT = TR['folds'].get('LOEO E215')
        fdE = E32['forms'][EFORM]['folds'].get('LOEO E215')
        tpred = {ids_t[i]: fdT['pred_test'][k] for k, i in enumerate(fdT['test_idx'])} if fdT else {}
        ids_e = E32['ids']
        epred = {ids_e[i]: fdE['W_given_t'][k] for k, i in enumerate(fdE['test_idx'])} if fdE else {}
        rows = []
        for (arm, pid), m in sorted(M.items()):
            ck = 'a3' if arm == 'A' else 'c1'
            row = dict(m)
            row['v32_E215_fold_cw'] = (tpred.get(f"E215|{ck}|{m['case']}") or float('nan')) * 600.0
            eid = [k for k in epred if k.startswith(f'E215|{ck}|') and pid in k.split('|')[2].split('+')]
            row['v32_E215_fold_W_given_t'] = epred[eid[0]] if len(eid) == 1 else None
            for mdl, fz in FZ.get((arm, pid), {}).items():
                row[mdl + '|cw'] = fz.get('cw')
                if fz.get('A') is not None and fz.get('B') is not None:
                    row[mdl + '|W_given_t'] = fz['A'] + fz['B'] / m['t_op_us']
            rows.append(row)
        models = ['MM1-v3.1', 'MM1-v3', 'v3.1 + gemmLnc term', 'v3.1 + contention'] + [f'verify-lay {x}' for x in ('N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24')]
        fam = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows:
            if r['role'] != 'point':
                continue
            for f_ in (r['family'], 'registered' if r['reading'] == 'literal' else 'posthoc', 'all'):
                if r['family'] != 'S':
                    fam[f_]['v32 cw'].append(r['v32_E215_fold_cw'] / r['cw'] - 1)
                    for mdl in models:
                        if r.get(mdl + '|cw') is not None:
                            fam[f_][mdl + ' cw'].append(r[mdl + '|cw'] / r['cw'] - 1)
                if r['W'] >= 3.0:
                    if r.get('v32_E215_fold_W_given_t') is not None:
                        fam[f_]['v32 W given t'].append(r['v32_E215_fold_W_given_t'] / r['W'] - 1)
                    for mdl in ('MM1-v3.1', 'MM1-v3', 'v3.1 + gemmLnc term'):
                        if r.get(mdl + '|W_given_t') is not None:
                            fam[f_][mdl + ' W given t'].append(r[mdl + '|W_given_t'] / r['W'] - 1)
        rep['E215_by_family_per_point'] = {f_: {k: stat(v) for k, v in d.items()} for f_, d in sorted(fam.items())}
        rep['E215_note'] = ("per POINT (E215's scorer scores time per case; here every point once, family S's points (time = their reference's "
                            "case) left out of the time rows); MM1-v3.2 is its E215 fold (E215 held out of its fit: HELD OUT, not blind); the "
                            "frozen forecasts are BLIND (frozen before any E215 datum); MM1-v3's arm A W is at its own seconds, not given t")
        lnc = [r for r in rows if r['loop'] == 'rgm136 gemmLnc']
        rep['gemmLnc_points'] = [{k: r.get(k) for k in ('arm', 'pid', 'token', 'W', 'cw', 'v32_E215_fold_W_given_t', 'v3.1 + gemmLnc term|W_given_t',
                                                        'MM1-v3.1|W_given_t')} for r in lnc]
        json.dump(rows, open(os.path.join(out, 'reported-e215-points.json'), 'w'), indent=0, default=float)
    else:
        rep['E215_by_family_per_point'] = 'NOT RUN (no E215 data in this run)'
    json.dump(rep, open(os.path.join(out, 'reported_v32.json'), 'w'), indent=1, sort_keys=True, default=float)
    print('reported written', {k: (v if isinstance(v, str) else type(v).__name__) for k, v in rep.items()})


if __name__ == '__main__':
    main()
