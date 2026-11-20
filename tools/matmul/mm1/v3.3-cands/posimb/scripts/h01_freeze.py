#!/usr/bin/env python3
"""layout2 (Q234) h01: FREEZE 'MM1-v3.2 + posimb' forecasts for every E220 point on both arms (OUT/reg-e220/POINTS.txt, FINAL 05:24:17
PST, sha256 058984a0...; its points-e220.csv sha256 64a7c99a...), as DECLARED-posimb.md section 7 (sha256 a7cd74a0..., 05:35:31 PST)
says: MM1-v3.2's predictor (mm1_v32.Model at out/mm1_v32_params.json, unchanged) per point exactly as POINTS.txt's MM1 call line gives it
(card = the arm's card, arm = token, fmt, kind = random, mask, f = the clock, kernel = rgm136), times the term's factors at its all-data
constants (work/fit_results.json, g01_fit.py); features by f02_private.py's code; the elasticity e by e01_base.py's method at MM1-v3.2's
all-data constants. Arm A at 600.0 MHz; arm B at 799.0 MHz (registered route c) and, as the registration also freezes, 700.0 and 600.0 MHz.
No E220 datum is opened. Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded.
Output (new files): <land>/forecasts-e220-posimb.csv, .json, .txt.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.3-cands/posimb')
REG = os.environ.get('E220_REG_DIR', os.path.join(LANE, '..', 'reg-e220'))
POINTS_TXT_SHA = '058984a04b90cd8585cb41cc6618430306d7bf1c7e230159e7719b9e9e1e9bdc'
POINTS_CSV_SHA = '64a7c99a90a2d899db44dc0c3790dfd840cd02b49c9d12f24396f4691125afc4'
DECL_SHA = 'a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9'
CARD = {'A': 'aifoundry1 card 1', 'B': 'aifoundry2 card 0'}
CLOCKS = {'A': [600.0], 'B': [799.0, 700.0, 600.0]}
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF
MEMK = ('c3', 'm3', 'cF', 'mF')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import mm1_v32  # noqa: E402
import time_v31 as TV  # noqa: E402

spec_f02 = importlib.util.spec_from_file_location('f02_private', os.path.join(LANE, 'scripts/f02_private.py'))
F02 = importlib.util.module_from_spec(spec_f02)
spec_f02.loader.exec_module(F02)
E = TV.E
COLS = ('cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
        'J_at_rest_per_gemm')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def fields(p):
    o = {'cycles_per_op_wall': p['cycles_per_op_wall'], 'cycles_per_op_mean': p.get('cycles_per_op_mean'), 'T_op_us': p['T_op_us'],
         'seconds_per_gemm': p.get('seconds_per_gemm')}
    if 'W_over_idle' in p:
        o.update({'W_over_idle': p['W_over_idle'], 'A_W': p['W_affine']['A_W'], 'B_W_us': p['W_affine']['B_W_us'],
                  'J_over_idle_per_gemm': p.get('J_over_idle_per_gemm')})
        rl = p.get('rest_law')
        o['J_at_rest_per_gemm'] = rl['J_at_rest_per_gemm_REPORTED'] if rl else None
        o['_P_rest'] = rl['P_rest_W'] if rl else None
    return o


def compose(b, gw, gm):
    o = {'cycles_per_op_wall': b['cycles_per_op_wall'] * gw, 'cycles_per_op_mean': (b['cycles_per_op_mean'] * gm if b['cycles_per_op_mean'] is not None else None),
         'T_op_us': b['T_op_us'] * gw, 'seconds_per_gemm': (b['seconds_per_gemm'] * gw if b['seconds_per_gemm'] is not None else None)}
    if 'A_W' in b:
        A, B = b['A_W'], b['B_W_us']
        W = A + B / o['T_op_us']
        o.update({'W_over_idle': W, 'A_W': A, 'B_W_us': B, 'J_over_idle_per_gemm': W * o['seconds_per_gemm']})
        o['J_at_rest_per_gemm'] = (b['_P_rest'] + W) * o['seconds_per_gemm'] if b.get('_P_rest') is not None else None
    return o


def main():
    t0 = time.time()
    assert sha(os.path.join(REG, 'POINTS.txt')) == POINTS_TXT_SHA, 'POINTS.txt differs'
    assert sha(os.path.join(REG, 'POINTS-e220.csv')) == POINTS_CSV_SHA, 'points csv differs'
    assert sha(os.path.join(LAND, 'DECLARED-posimb.md')) == DECL_SHA, 'declaration differs'
    fit = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
    assert fit['declaration_sha256'] == DECL_SHA
    a_hop, a_lag = fit['constants_all_data']['posimb']
    kept = bool(fit['keep_rule']['KEPT'])
    label = 'MM1-v3.2 + posimb' if kept else 'MM1-v3.2 + posimb (rejected candidate)'
    params = json.load(open(os.path.join(V32, 'out/mm1_v32_params.json')))
    M = mm1_v32.Model(params)
    th = params['time']['theta']
    form = params['time']['form']
    ths = dict(th)
    for k in MEMK:
        ths[k] = th[k] * 1.01
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
    rows_in = list(csv.DictReader(open(os.path.join(REG, 'POINTS-e220.csv'))))
    out_rows = []
    made = 0
    for arm in ('A', 'B'):
        R = [r for r in rows_in if r['arm'] == arm]
        for f in CLOCKS[arm]:
            specs = [{'card': CARD[arm], 'arm': r['token'], 'fmt': r['format'], 'kind': 'random', 'mask': r['shire_mask'], 'f': f, 'kernel': 'rgm136'}
                     for r in R]
            base = M.predict_many(specs)
            pts = []
            for s in specs:
                pre, b = E.arm_parts(s['arm'])
                kernel = 'rgm211' if pre == 'gemmLn' else ('run_gemm' if pre is None else 'rgm136')
                pts.append({'arm': s['arm'], 'kernel': kernel, 'fmt': s['fmt'], 'mask': s['mask'], 'f': f})
            en = TV.Engine31(pts)
            T0 = en.predict(th, form)
            T1 = en.predict(ths, form)
            e = np.log(T1 / T0) / np.log(1.01)
            for j, (r, s, bp) in enumerate(zip(R, specs, base)):
                assert abs(T0[j] / bp['T_op_us'] - 1) < 1e-12, 'engine and predictor differ'
                m = int(s['mask'], 16)
                in_scope = m != FULL and pts[j]['kernel'] == 'rgm136' and bool(SHAPE.match(s['arm']))
                G1c = LAGc = 0.0
                feat = None
                if in_scope:
                    key = '%s|0x%x' % (s['arm'], m)
                    if key not in PS:
                        MB, NB, KB = (int(x) for x in SHAPE.match(s['arm']).groups())
                        rr = F02.private_shared(MB, NB, KB, m)
                        rr.update(F02.mesh_lat(m))
                        PS[key] = rr
                        made += 1
                    feat = PS[key]
                    G1c = feat['Lmean_act'] / feat['Lmean_full'] - 1.0
                    F = feat['Fp'] + feat['Fs']
                    LAGc = ((feat['Lmax_act'] - feat['Lmean_act']) / feat['Lmean_full']) * (feat['Fp'] / F if F > 0 else 0.0)
                ph_hop, ph_lag = float(e[j] * G1c), float(e[j] * LAGc)
                gw = float(np.clip(1.0 + a_hop * ph_hop + a_lag * ph_lag, 0.3, 3.0)) if in_scope else 1.0
                gm = float(np.clip(1.0 + a_hop * ph_hop, 0.3, 3.0)) if in_scope else 1.0
                bf = fields(bp)
                cf = compose(bf, gw, gm)
                row = {'arm': arm, 'card': CARD[arm], 'f_mhz': f, 'id': r['id'], 'family': r['family'], 'subfamily': r['subfamily'], 'pair': r['pair'],
                       'token': r['token'], 'format': r['format'], 'kind': 'random', 'shire_mask': r['shire_mask'], 'in_scope': int(in_scope),
                       'e': float(e[j]), 'G1core': G1c, 'LAGcore': LAGc, 'Phi_hop': ph_hop, 'Phi_lag': ph_lag, 'g_wall': gw, 'g_mean': gm,
                       'Fp': (feat or {}).get('Fp'), 'Fs': (feat or {}).get('Fs'), 'Lmean_act': (feat or {}).get('Lmean_act'),
                       'Lmax_act': (feat or {}).get('Lmax_act')}
                for c in COLS:
                    row[label + '|' + c] = cf.get(c)
                for c in COLS:
                    row['MM1-v3.2|' + c] = bf.get(c)
                if 'W_over_idle' not in bp:
                    row['energy_note'] = bp.get('energy', 'NOT FORECAST')
                out_rows.append(row)
    odir = sys.argv[1] if len(sys.argv) > 1 else LAND
    os.makedirs(odir, exist_ok=True)
    fn_csv = os.path.join(odir, 'forecasts-e220-posimb.csv')
    fn_json = os.path.join(odir, 'forecasts-e220-posimb.json')
    fn_txt = os.path.join(odir, 'forecasts-e220-posimb.txt')
    for fn in (fn_csv, fn_json, fn_txt):
        assert not os.path.exists(fn), 'refusing to overwrite ' + fn
    keys = list(out_rows[0].keys())
    for r in out_rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(fn_csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator='\n')
        w.writeheader()
        for r in out_rows:
            w.writerow({k: ('' if r.get(k) is None else (repr(r[k]) if isinstance(r[k], float) else r[k])) for k in keys})
    meta = {'label': label, 'kept_by_declared_rule': kept, 'declaration_sha256': DECL_SHA, 'points_txt_sha256': POINTS_TXT_SHA,
            'points_csv_sha256': POINTS_CSV_SHA, 'constants_all_data': {'a_hop': a_hop, 'a_lag': a_lag},
            'fit_results_sha256': sha(os.path.join(LANE, 'work/fit_results.json')), 'mm1_v32_params_sha256': sha(os.path.join(V32, 'out/mm1_v32_params.json')),
            'features_made_here': made, 'n_rows': len(out_rows), 'n_in_scope_rows': sum(r['in_scope'] for r in out_rows),
            'interpreter': sys.version.split()[0], 'numpy': np.__version__, 'how': 'h01_freeze.py; DECLARED-posimb.md section 7',
            'rows': out_rows}
    json.dump(meta, open(fn_json, 'w'), indent=1)
    with open(fn_txt, 'w') as fh:
        fh.write('# %s forecasts for E220 (both arms), frozen by layout2 (Q234). Constants a_hop %.6f a_lag %.6f (all data through E219).\n'
                 % (label, a_hop, a_lag))
        fh.write('# arm f_mhz id token mask g_wall wall_cycles(term) wall_cycles(v3.2) mean_cycles(term) seconds(term) W(term,t fc) J_over(term) J_rest(term)\n')
        for r in out_rows:
            if r['in_scope']:
                fh.write('%s %.1f %s %s %s %.6f %.3f %.3f %s %.6g %s %s %s\n' % (
                    r['arm'], r['f_mhz'], r['id'], r['token'], r['shire_mask'], r['g_wall'], r[label + '|cycles_per_op_wall'], r['MM1-v3.2|cycles_per_op_wall'],
                    ('%.3f' % r[label + '|cycles_per_op_mean']) if r[label + '|cycles_per_op_mean'] is not None else '-', r[label + '|seconds_per_gemm'],
                    ('%.4f' % r[label + '|W_over_idle']) if r.get(label + '|W_over_idle') is not None else '-',
                    ('%.6g' % r[label + '|J_over_idle_per_gemm']) if r.get(label + '|J_over_idle_per_gemm') is not None else '-',
                    ('%.6g' % r[label + '|J_at_rest_per_gemm']) if r.get(label + '|J_at_rest_per_gemm') is not None else '-'))
        fh.write('# every other row (full chip, or outside rgm136 gemmL) equals MM1-v3.2 to the last bit (g_wall = g_mean = 1): see the CSV.\n')
    print(label, 'rows', len(out_rows), 'in scope', meta['n_in_scope_rows'], 'features made', made, 'secs', round(time.time() - t0, 1))
    for fn in (fn_csv, fn_json, fn_txt):
        print(sha(fn), fn)


if __name__ == '__main__':
    main()
