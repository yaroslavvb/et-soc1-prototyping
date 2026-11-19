#!/usr/bin/env python3
"""lay-contention s08: the freeze. 'MM1-v3.1 + contention' (form F1, kept by work/DECLARED-layout.md's rule and addendum 1's placebo
check) for every E215 point and reference: MM1-v3.1's own wall op time at its frozen all-data constants (re-made with time_v31.Engine31
and checked against the frozen forecast files) times (1 + a x Phi_fresh), a fitted on every training point of MM1-v3.1's all-data
record (two-stage, as scored). Phi_fresh = 0 at the full mask, so every full-chip point keeps MM1-v3.1's forecast exactly.
REPORTED beside (never the frozen form): F5 (Phi_fresh + Phi_fan) and G1 (Phi_hopmean), the same way.
Reads only committed files: E215's registered points (tools/claims-v3/e215/points-e215.csv), MM1-v3.1's frozen forecasts
(tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv, tools/claims-v3/e215/forecast-e215b-v31.csv, forecast-e215-refs.csv). No E215 datum.
Desk; /usr/bin/python3 3.12.3 -I -B; single-threaded. Output work/forecast-e215-v31-layout.csv / .json."""
import csv
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)
import eval_layout as S  # noqa: E402

FV, E = S.FV, S.E
LAB = S.LAB


def main():
    t0 = time.time()
    rec = json.load(open(os.path.join(S.V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    assert [p['id'] for p in P] == rec['ids']
    form, _ = FV.parse_form_name(rec['form_name'])
    en = FV.TV.Engine31(P)
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = FV.rung_mask(P)
    th = rec['theta_all']
    base = en.predict(th, form)
    assert float(np.max(np.abs(base / np.array(rec['pred_all']) - 1))) == 0.0
    Phi4 = np.zeros((N, 4))
    hm = np.zeros(N)
    for j, p in enumerate(P):
        lp = E.loop_of(p['arm'], p['kernel']) if S.SHAPE.match(p['arm']) else None
        Phi4[j], k = S.phi_of(lp, p['arm'], p['mask'])
        if k:
            f, g = S.FEATS[k], S.FEATS[k.rsplit('|', 1)[0] + '|0xffffffff']
            hm[j] = (110.0 + 12.0 * f['mesh_hop_mean']) / (110.0 + 12.0 * g['mesh_hop_mean']) - 1.0
    tr = np.arange(N)[~rung]
    r = base / Tm

    def fitc(X):
        a, *_ = np.linalg.lstsq(r[tr, None] * X[tr], 1.0 - r[tr], rcond=None)
        return a
    aF1 = fitc(Phi4[:, [0]])
    aF5 = fitc(Phi4[:, [0, 3]])
    aG1 = fitc(hm[:, None])
    s04 = json.load(open(os.path.join(WORK, 'eval_layout.json')))
    assert abs(aF1[0] - s04['forms']['F1']['all_data_constants']['fresh']) < 1e-12
    pin = os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv')
    pts = list(csv.DictReader(open(pin)))
    fa = {r_['token']: r_ for r_ in csv.DictReader(open(os.path.join(S.V31, 'out/e215/mm1_v31_e215.csv')))}
    fb = {r_['id']: r_ for r_ in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/forecast-e215b-v31.csv')))}
    fr = {r_['id']: r_ for r_ in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/forecast-e215-refs.csv')))
          if r_['model'] == 'MM1-v3.1'}
    specs = []
    for q in pts:
        specs.append({'arm': q['arm_token'], 'kernel': q['elf'], 'fmt': q['format'], 'mask': q['shire_mask'], 'f': 600.0,
                      'kind': q['kind'], 'id': q['id'], 'exp': 'E215'})
    en2 = FV.TV.Engine31(specs)
    T31 = en2.predict(th, form)
    rows = []
    worst = 0.0
    for q, sp, t in zip(pts, specs, T31):
        lp = q['loop']
        assert E.loop_of(sp['arm'], sp['kernel']) == lp, (q['id'], lp)
        ph, key = S.phi_of(lp, sp['arm'], sp['mask'])
        hmv = 0.0
        if key:
            f, g = S.FEATS[key], S.FEATS[key.rsplit('|', 1)[0] + '|0xffffffff']
            hmv = (110.0 + 12.0 * f['mesh_hop_mean']) / (110.0 + 12.0 * g['mesh_hop_mean']) - 1.0
        tok = '|'.join([lp, sp['arm'], sp['fmt'], sp['kind'], sp['mask']])
        if q['id'] in fr:
            frozen = float(fr[q['id']]['cycles_per_op_wall'])
            src = 'tools/claims-v3/e215/forecast-e215-refs.csv'
        elif q['arm'] == 'B':
            frozen = float(fb[q['id']]['cycles_per_op_wall'])
            src = 'tools/claims-v3/e215/forecast-e215b-v31.csv'
        else:
            frozen = float(fa[tok]['v31_cycles_wall'])
            src = 'tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv'
        cyc = t * 600.0
        worst = max(worst, abs(cyc / frozen - 1))
        g1 = float(np.clip(1.0 + aF1[0] * ph[0], 0.3, 3.0))
        g5 = float(np.clip(1.0 + aF5[0] * ph[0] + aF5[1] * ph[3], 0.3, 3.0))
        gg = float(np.clip(1.0 + aG1[0] * hmv, 0.3, 3.0))
        ops = float(q['ops_per_minion_per_gemm'])
        rows.append({'id': q['id'], 'e215_arm': q['arm'], 'family': q['family'], 'reading': q['reading'], 'role': q['role'],
                     'card': 'aifoundry3 card 0' if q['arm'] == 'A' else 'aifoundry1 card 1', 'f_mhz': 600.0, 'loop': lp,
                     'kernel': sp['kernel'], 'arm': sp['arm'], 'fmt': sp['fmt'], 'kind': sp['kind'], 'mask': sp['mask'],
                     'n_shires': bin(int(sp['mask'], 16)).count('1'), 'phi_fresh': round(float(ph[0]), 9),
                     'layout_factor': round(g1, 9), 'v31_cycles_per_op_wall': round(cyc, 4), 'v31_frozen_cycles_per_op_wall': frozen,
                     'v31_frozen_source': src, 'v31c_cycles_per_op_wall': round(cyc * g1, 4), 'v31c_T_op_us': round(t * g1, 8),
                     'v31c_seconds_per_gemm': '%.9e' % (t * g1 * 1e-6 * ops), 'v31_seconds_per_gemm': '%.9e' % (t * 1e-6 * ops),
                     'ops_per_minion_per_gemm': int(ops), 'REPORTED_F5_cycles_per_op_wall': round(cyc * g5, 4),
                     'REPORTED_G1_cycles_per_op_wall': round(cyc * gg, 4)})
    full = [x for x in rows if int(x['mask'], 16) == S.FULL]
    subs = [x for x in rows if int(x['mask'], 16) != S.FULL]
    assert all(x['layout_factor'] == 1.0 and x['v31c_cycles_per_op_wall'] == x['v31_cycles_per_op_wall'] for x in full)
    fn = os.path.join(HERE, 'forecast-e215-v31-layout.csv')
    with open(fn, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    meta = {'model': "MM1-v3.1 + contention (form F1: T = T_v31 x (1 + a Phi_fresh))", 'a_fresh': float(aF1[0]),
            'REPORTED_F5': {'a_fresh': float(aF5[0]), 'a_fan': float(aF5[1])}, 'REPORTED_G1': {'a_hopmean': float(aG1[0])},
            'base': 'MM1-v3.1 (tools/matmul/mm1/v3.1, landed 2c971828) all-data constants out/fits/time_T5r+G0+n32.json theta_all',
            'base_check_worst_rel_vs_frozen_files': worst, 'n_rows': len(rows), 'n_full_mask_rows': len(full), 'n_subset_rows': len(subs),
            'full_mask_factor': 'exactly 1 at every full-mask row (Phi_fresh = 0 by construction): checked',
            'subset_factor_range': [min(x['layout_factor'] for x in subs), max(x['layout_factor'] for x in subs)],
            'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__), 'secs': round(time.time() - t0, 1)}
    json.dump({'meta': meta, 'rows': rows}, open(os.path.join(HERE, 'forecast-e215-v31-layout.json'), 'w'), indent=1)
    print(json.dumps(meta, indent=1))
    for x in subs:
        print(f"{x['id']} {x['family']} {x['arm']:12s} {x['mask']:>11s} n{x['n_shires']:2d} phi {x['phi_fresh']:+.4f} factor {x['layout_factor']:.5f} "
              f"v31 {x['v31_cycles_per_op_wall']:9.3f} (frozen {x['v31_frozen_cycles_per_op_wall']}) -> {x['v31c_cycles_per_op_wall']:9.3f}  "
              f"F5 {x['REPORTED_F5_cycles_per_op_wall']:9.3f} G1 {x['REPORTED_G1_cycles_per_op_wall']:9.3f}")


if __name__ == '__main__':
    main()
