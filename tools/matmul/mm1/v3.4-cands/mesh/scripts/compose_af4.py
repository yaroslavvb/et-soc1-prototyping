#!/usr/bin/env python3
"""mask-mesh: 'MM1-v3.2 + AF4 + mesh' BY CONSTRUCTION (no refit). MM1-v3.3 as E222's registered selection rule chose it is 'MM1-v3.2 + AF4'
(tools/matmul/mm1/v3.3-cands/gemmlnc-af4/: W over idle at rgm136 gemmLnc points, F3 replaced; no op time changed; 0 at every cooperative loop).
This term changes the op time of cooperative rgm136 gemmL subset points only (mesh_term). No point is in both, so the composition is:
  - a gemmLnc point: AF4's forecast exactly (its frozen equation and constants, its own feature code exec'd from its landed s02_fit.py as its
    s03_freeze.py does), op time MM1-v3.2's (this term is out of scope: factor 1, asserted);
  - a cooperative gemmL subset point: this term's op time (wall, mean = wall / MM1-v3.2's rho, seconds), W over idle at a measured t = MM1-v3.2's
    A + B / t (AF4's dW = 0 there, asserted), with t forecast at this term's t;
  - every other point: MM1-v3.2's.
CHECKS (run): (1) at every gemmLnc row of AF4's frozen E220 forecasts (forecasts-e220-af4.csv) the composition re-makes AF4's W over idle,
A_W and B_W_us; (2) at every cooperative row there, AF4's frozen W equals MM1-v3.2's and the composed op time equals this term's (its factor
printed); (3) at the full-chip rows all three are MM1-v3.2's. Run: bash run.sh compose_af4.py <lane dir>  ->  work/compose-af4-check.json"""
import csv
import json
import os
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
os.environ['MASK_MESH_LANE'] = L
sys.path.insert(0, os.path.join(L, 'scripts'))
import mesh_term as MT  # noqa: E402
import mm1_v32  # noqa: E402  (from the snapshot, through mesh_term's paths)
import mm1_core_v3 as CORE  # noqa: E402

AF = os.path.join(MT.REPO, 'tools', 'matmul', 'mm1', 'v3.3-cands', 'gemmlnc-af4')
TERM = json.load(open(os.path.join(AF, 'term-gemmlnc-af4.json')))
C1, C2 = TERM['constants_pJ_per_line']['c1'], TERM['constants_pJ_per_line']['c2']
V32P = json.load(open(os.path.join(MT.V32, 'out', 'mm1_v32_params.json')))
C1V, C2V = V32P['energy']['F3']['c1_pJ'], V32P['energy']['F3']['c2_pJ']
src = open(os.path.join(AF, 'scripts', 's02_fit.py')).read()
ns = {'np': np, 'C': CORE, 'X1': float(V32P['time']['theta']['x1'])}
exec(src[src.index('def feats('):src.index('FORMS = {')], ns)
feats = ns['feats']


def composed(specs, mesh):
    """per spec (card, arm, fmt, kind, mask, f, kernel): the composed forecast"""
    M = mm1_v32.Model(V32P)
    pr = M.predict_many(specs)
    pts = [{'arm': s['arm'], 'kernel': s.get('kernel', 'rgm136'), 'fmt': s['fmt'], 'mask': s['mask'], 'f': float(s['f'])} for s in specs]
    Tm, fac, X = mesh.time_many(pts)
    out = []
    for s, o, t_mesh, fa in zip(specs, pr, Tm, fac):
        lnc = s['arm'].startswith('gemmLnc')
        A_, B_ = o['W_affine']['A_W'], o['W_affine']['B_W_us']
        t32 = o['T_op_us']
        f3 = o['F3_W_at_own_t']
        if lnc:
            assert fa == 1.0, ('the mesh term must be out of scope at a gemmLnc point', s)
            S_own = f3 / (C1V * 26.0 + C2V * o['F3_first'])
            Q = 0.5 * (np.array(o['Q0']) + np.array(o['Q1']))
            MB, NB, KB = (int(x) for x in s['arm'][len('gemmLnc'):].split('x'))
            ft = feats((MB, NB, KB), s['fmt'], Q.sum(axis=1).tolist(), Q.sum(axis=0).tolist(), s['mask'])
            dW = S_own * (C1 * ft['dup'] + C2 * ft['R4'])
        else:
            assert f3 == 0.0, s
            dW = 0.0
        Bn = B_ - f3 * t32 + dW * t32
        T = t_mesh                                         # the composed op time: this term's (= MM1-v3.2's off its scope)
        rho = o['rho_wall_over_mean']
        sec = (o['ops_per_minion_per_gemm'] * T * 1e-6) if o.get('ops_per_minion_per_gemm') else None
        out.append({'spec': s, 'T_op_us': float(T), 'cycles_per_op_wall': float(T * s['f']), 'cycles_per_op_mean': float(T * s['f'] / rho),
                    'seconds_per_gemm': sec, 'A_W': A_, 'B_W_us': Bn, 'W_over_idle_at_t_forecast': A_ + Bn / T,
                    'W_over_idle_AF4_at_v32_t': A_ + Bn / t32, 'mesh_factor': float(fa), 'AF4_dW_at_v32_t': dW, 'MM1-v3.2_T_op_us': t32})
    return out


if __name__ == '__main__':
    params = json.load(open(os.path.join(L, 'work', 'fit', 'params-mesh.json')))
    mesh = MT.Model(params, os.path.join(L, 'work', 'features-mesh.json'))
    rows = list(csv.DictReader(open(os.path.join(AF, 'forecasts-e220-af4.csv'))))
    specs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': r['kind'], 'mask': r['shire_mask'], 'f': float(r['f_mhz']),
              'kernel': r['loop'].split()[0]} for r in rows]
    res = composed(specs, mesh)
    chk = {'lnc': [], 'coop_subset': [], 'full': []}
    for r, o in zip(rows, res):
        lnc = r['token'].startswith('gemmLnc')
        sub = r['shire_mask'].lower() != '0xffffffff'
        if lnc:
            chk['lnc'].append(max(abs(o['W_over_idle_AF4_at_v32_t'] / float(r['W_over_idle']) - 1.0), abs(o['A_W'] / float(r['A_W']) - 1.0),
                                  abs(o['B_W_us'] / float(r['B_W_us']) - 1.0), abs(o['MM1-v3.2_T_op_us'] / float(r['T_op_us']) - 1.0), abs(o['mesh_factor'] - 1.0)))
        elif sub:
            chk['coop_subset'].append({'id': r['id'], 'arm': r['arm'], 'token': r['token'], 'mask': r['shire_mask'], 'f': r['f_mhz'],
                                       'AF4_W_equals_v32': abs(float(r['W_over_idle']) / float(r['MM1-v3.2_W_over_idle']) - 1.0) < 1e-12,
                                       'mesh_factor': o['mesh_factor'], 'composed_T_over_v32_T': o['T_op_us'] / float(r['T_op_us'])})
        else:
            chk['full'].append(max(abs(o['T_op_us'] / float(r['T_op_us']) - 1.0), abs(o['W_over_idle_at_t_forecast'] / float(r['W_over_idle']) - 1.0)))
    rep = {'what': "'MM1-v3.2 + AF4 + mesh' by construction against AF4's frozen E220 forecasts (no refit)", 'af4_term_sha256':
           __import__('hashlib').sha256(open(os.path.join(AF, 'term-gemmlnc-af4.json'), 'rb').read()).hexdigest(),
           'gemmLnc_rows': len(chk['lnc']), 'gemmLnc_max_rel_diff_vs_AF4_frozen': max(chk['lnc']) if chk['lnc'] else None,
           'cooperative_subset_rows': chk['coop_subset'], 'full_chip_rows': len(chk['full']),
           'full_chip_max_rel_diff_vs_AF4_frozen': max(chk['full']) if chk['full'] else None,
           'all_af4_equal_v32_at_cooperative_subset_rows': all(x['AF4_W_equals_v32'] for x in chk['coop_subset'])}
    json.dump(rep, open(os.path.join(L, 'work', 'compose-af4-check.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'cooperative_subset_rows'}, indent=1))
    print('cooperative subset rows: %d, mesh factor range %.4f-%.4f' % (len(chk['coop_subset']), min(x['mesh_factor'] for x in chk['coop_subset']),
                                                                         max(x['mesh_factor'] for x in chk['coop_subset'])))
