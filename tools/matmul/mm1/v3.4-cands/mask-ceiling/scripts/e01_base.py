#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) e01: MM1-v3.2's base op time at every point of work/points_all.json, at its all-data constants and at each of
its stored folds' constants (tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json), by time_v31.Engine31 unchanged (layout2's e01_base.py
form), plus each point's elasticity of the op time to the mesh-served memory costs (c3, m3, cF, mF scaled together by 1.01:
e = ln(T(1.01) / T) / ln(1.01)), a CONTEXT feature of the reference. Checks the all-data base against the stored pred_all and every fold's
held-out base against its stored pred_test, and E221's all-data base error against blind-e221's per-case v32_e_wall (REPORTED: blind-e221
priced each run at its own measured clock and averaged the runs' errors; this lane prices a case at its mean clock).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded. Output: work/base.npz, work/base_meta.json.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

import numpy as np

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import time_v31 as TV  # noqa: E402

MEMK = ('c3', 'm3', 'cF', 'mF')
USED_FOLDS = ('LOCO aifoundry3 card 0', 'LOCO aifoundry1 card 1', 'LOCO aifoundry2 card 0', 'LOCO aifoundry1 card 0')


def scaled(th, s):
    t = dict(th)
    for k in MEMK:
        t[k] = th[k] * s
    return t


def main():
    t0 = time.time()
    d = json.load(open(os.path.join(LANE, 'work/points_all.json')))
    P = d['points']
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    form = rec['form']
    en = TV.Engine31([{'arm': p['arm'], 'kernel': p['kernel'], 'fmt': p['fmt'], 'mask': p['mask'], 'f': float(p['f'])} for p in P])
    print('engine built', round(time.time() - t0, 1), 's', flush=True)
    n_old = d['counts']['v32_fit']
    out = {}
    meta = {'form_name': rec['form_name'], 'n': len(P), 'n_old': n_old, 'folds': {}, 'checks': {}, 'interpreter': sys.version.split()[0],
            'numpy': np.__version__}
    th = rec['theta_all']
    b = en.predict(th, form)
    bu = en.predict(scaled(th, 1.01), form)
    out['base_all'] = b
    out['e_all'] = np.log(bu / b) / np.log(1.01)
    chk = float(np.max(np.abs(b[:n_old] / np.array(rec['pred_all']) - 1)))
    meta['checks']['all_vs_stored_pred_all_maxrel'] = chk
    print('all-data: max rel diff vs stored pred_all %.3e' % chk, flush=True)
    folds = [k for k in rec['folds'] if k.startswith('LOEO ') or k in USED_FOLDS]
    for name in folds:
        fr = rec['folds'][name]
        thf = fr['theta']
        bf = en.predict(thf, form)
        buf = en.predict(scaled(thf, 1.01), form)
        te = np.array(fr['test_idx'])
        c = float(np.max(np.abs(bf[te] / np.array(fr['pred_test']) - 1)))
        out['base|' + name] = bf
        out['e|' + name] = np.log(buf / bf) / np.log(1.01)
        out['test|' + name] = te
        meta['folds'][name] = {'n_test_old': int(len(te)), 'check_maxrel': c}
        print('  %-24s n_test %4d check %.2e (%.0f s)' % (name, len(te), c, time.time() - t0), flush=True)
    T = np.array([p['T'] for p in P])
    out['T_meas'] = T
    # E221 against blind-e221's per-case errors (REPORTED)
    idx = [i for i, p in enumerate(P) if p['exp'] == 'E221']
    mine = b[idx] / T[idx] - 1
    theirs = np.array([P[i]['e221_v32_e_wall'] for i in idx])
    dd = mine - theirs
    meta['checks']['E221_vs_blind_e221_v32_e_wall'] = {'n': len(idx), 'max_abs_diff': float(np.max(np.abs(dd))), 'rms_diff': float(np.sqrt(np.mean(dd ** 2))),
                                                       'how': 'this lane: MM1-v3.2 all-data base at the case mean clock / measured - 1; blind-e221: the mean of its runs errors'}
    print('E221 vs blind-e221 v32_e_wall: max |diff| %.3e, rms %.3e (n %d)' % (np.max(np.abs(dd)), np.sqrt(np.mean(dd ** 2)), len(idx)))
    np.savez(os.path.join(LANE, 'work/base.npz'), **out)
    json.dump(meta, open(os.path.join(LANE, 'work/base_meta.json'), 'w'), indent=1)
    print('done', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
