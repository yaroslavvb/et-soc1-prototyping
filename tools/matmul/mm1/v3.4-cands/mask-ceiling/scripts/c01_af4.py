#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) c01: THE COMPOSITION WITH AF4, BY CONSTRUCTION (DECLARED-mask-ceiling.md section 6), with no refit.
MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's registered selection rule). AF4 acts on gemmLnc tokens' ENERGY only; the reference acts on the OP TIME of
rgm136 gemmL tokens at shire subsets with MB x NB >= 2 only (r_common.in_scope). This script shows, from committed frozen rows and this lane's
points:
  C1 no point is in both scopes: every point of work/points_all.json and every registered point of E220, E222 and E224 (token grammar:
     'gemmLnc...' never matches r_common's ^gemmL<MB>x<NB>x<KB>$);
  C2 AF4 changes no op time: at every row of E222's and E224's frozen forecasts (forecast-e222.json, forecast-e224.json, landed with their
     registrations) 'MM1-v3.2 + AF4' carries MM1-v3.2's T_op_us, wall and mean cycles an op and seconds a GEMM exactly;
  C3 AF4 changes nothing outside gemmLnc: at every non-gemmLnc row the two rows are equal in every number;
  C4 MM1-v3.2's energy law at a time t is what the composition uses: W_over_idle = A_W + B_W_us / T_op_us, J over idle = W x seconds,
     J at rest = (rest_law_W + W) x seconds (checked on MM1-v3.2's own rows);
then builds 'MM1-v3.2 + AF4 + mask-ceiling' at those registered points: AF4's row at a gemmLnc token; at an in-scope point MM1-v3.2's row
with the op time (wall cycles, T_op_us, seconds) times exp(clip(the all-data forest, -0.5, 0.5)) and the energy by C4's law at the new time
(the counter's mean cycles MM1-v3.2's own: not forecast by the reference); MM1-v3.2's row elsewhere. The composed rows are REPORTED (a
demonstration of the construction: E222's and E224's data are in the reference's training set, so nothing here is blind).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded, in a slot. Output: work/composed-af4-REPORTED.json, logs/c01.log.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

import numpy as np

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
sys.path.insert(0, os.path.join(LANE, 'scripts'))
import r_common as RC  # noqa: E402
import rf_core as RF  # noqa: E402
import f01_features as F1  # noqa: E402

V32, AF4 = 'MM1-v3.2', 'MM1-v3.2 + AF4'
TIME_KEYS = ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm')
E_KEYS = ('W_over_idle', 'J_over_idle_per_gemm', 'J_at_rest_per_gemm')


def feats_for(arm, mask, FJ):
    k = '%s|%s' % (arm, mask)
    if k in FJ:
        return FJ[k]
    MB, NB, KB = RC.shape(arm)
    m = int(mask, 16)
    f = F1.mask_feats(m)
    r = F1.F02.private_shared(MB, NB, KB, m)
    f.update({'Fp': r['Fp'], 'Fs': r['Fs']})
    f['LAG'] = f['hlag'] * r['Fp'] / (r['Fp'] + r['Fs']) if (r['Fp'] + r['Fs']) > 0 else 0.0
    FJ[k] = f
    return f


def xrow(arm, fmt, mask, f, FJ):
    MB, NB, KB = RC.shape(arm)
    ft = feats_for(arm, mask, FJ)
    return [float(ft[c]) for c in RC.FEATS_M] + [float(MB), float(NB), math.log(KB), float(RC.FMT[fmt]), float(f)]


def main():
    log = []
    prm = json.load(open(os.path.join(LANE, 'work/params-mask-ceiling.json')))
    assert prm['features'] == list(RC.FEATS)
    forest = RF.Forest.from_json(prm['forest'])
    FJ = json.load(open(os.path.join(LANE, 'work/features.json')))['features']
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    both = [p['id'] for p in P if RC.in_scope(p) and p['arm'].startswith('gemmLnc')]
    nlnc = sum(1 for p in P if p['arm'].startswith('gemmLnc'))
    log.append('C1 data points: %d, in the reference scope %d, gemmLnc %d, in both %d' % (len(P), sum(1 for p in P if RC.in_scope(p)), nlnc, len(both)))
    c1_ok = not both
    reg = []
    for exp, fn, arms in (('E220', 'tools/claims-v3/e220/points-e220.json', ('A', 'B')), ('E222', 'tools/claims-v3/e222/points-e222.json', None),
                          ('E224', 'tools/claims-v3/e224/points-e224.json', ('A', 'B'))):
        d = json.load(open(os.path.join(LAB, fn)))['points']
        L = [p for a in arms for p in d[a]] if arms else d
        for p in L:
            q = {'arm': p['arm'], 'kernel': 'rgm136', 'mask': '0x%x' % int(p['shire_mask'], 16), 'fmt': p['format']}
            reg.append((exp, p['id'], RC.in_scope(q), p['arm'].startswith('gemmLnc')))
    nb = sum(1 for r in reg if r[2] and r[3])
    log.append('C1 registered points E220/E222/E224: %d, in the reference scope %d, gemmLnc %d, in both %d' %
               (len(reg), sum(1 for r in reg if r[2]), sum(1 for r in reg if r[3]), nb))
    c1_ok = c1_ok and nb == 0
    # the frozen rows
    rowsets = []
    d22 = json.load(open(os.path.join(LAB, 'tools/claims-v3/e222/forecast-e222.json')))
    for pid, v in sorted(d22['points'].items()):
        rowsets.append(('E222', 'A', pid, 600.0, v['token'], v['fmt'], v['mask'], v['models']))
    d24 = json.load(open(os.path.join(LAB, 'tools/claims-v3/e224/forecast-e224.json')))
    for a in ('A', 'B'):
        for pid, v in sorted(d24['arms'][a]['points'].items()):
            for col, models in sorted(v['clocks'].items()):
                rowsets.append(('E224', a, pid, float(col), v['token'], v['format'], v['mask'], models))
    c2 = c3 = c4 = 0
    c2_bad, c3_bad, c4_bad = [], [], []
    comp = []
    for exp, a, pid, col, tok, fmt, mask, models in rowsets:
        b, af = models[V32], models[AF4]
        lnc = tok.startswith('gemmLnc')
        if any(b[k] != af[k] for k in TIME_KEYS):
            c2_bad.append((exp, a, pid, col))
        c2 += 1
        if not lnc:
            c3 += 1
            if any(b[k] != af[k] for k in TIME_KEYS + E_KEYS + ('A_W', 'B_W_us', 'rest_law_W')):
                c3_bad.append((exp, a, pid, col))
        c4 += 1
        W = b['A_W'] + b['B_W_us'] / b['T_op_us']
        if not (abs(W / b['W_over_idle'] - 1) < 1e-9 and abs(b['W_over_idle'] * b['seconds_per_gemm'] / b['J_over_idle_per_gemm'] - 1) < 1e-9
                and abs((b['rest_law_W'] + b['W_over_idle']) * b['seconds_per_gemm'] / b['J_at_rest_per_gemm'] - 1) < 1e-9):
            c4_bad.append((exp, a, pid, col))
        q = {'arm': tok, 'kernel': 'rgm136', 'mask': '0x%x' % int(mask, 16), 'fmt': fmt}
        insc = RC.in_scope(q)
        if lnc:
            out, how, fac = dict(af), 'AF4 (the reference is 1 at a gemmLnc token)', 1.0
        elif insc:
            yh = float(np.clip(forest.predict(np.array([xrow(tok, fmt, q['mask'], col, FJ)]))[0], -0.5, 0.5))
            fac = math.exp(yh)
            out = dict(b)
            for k in ('T_op_us', 'cycles_per_op_wall', 'seconds_per_gemm'):
                out[k] = b[k] * fac
            out['W_over_idle'] = b['A_W'] + b['B_W_us'] / out['T_op_us']
            out['J_over_idle_per_gemm'] = out['W_over_idle'] * out['seconds_per_gemm']
            out['J_at_rest_per_gemm'] = (b['rest_law_W'] + out['W_over_idle']) * out['seconds_per_gemm']
            how = 'the reference (AF4 equals MM1-v3.2 here: C3)'
        else:
            out, how, fac = dict(b), 'MM1-v3.2 (neither term acts)', 1.0
        comp.append({'exp': exp, 'arm_tag': a, 'id': pid, 'clock_MHz': col, 'token': tok, 'format': fmt, 'mask': mask, 'acting': how,
                     'factor_mask_ceiling': fac, 'MM1-v3.2 + AF4 + mask-ceiling': {k: out[k] for k in TIME_KEYS + E_KEYS if k in out},
                     'MM1-v3.2': {k: b[k] for k in TIME_KEYS + E_KEYS}, 'MM1-v3.2 + AF4': {k: af[k] for k in TIME_KEYS + E_KEYS}})
    log.append('C2 AF4 changes no op time: %d rows, differing %d %s' % (c2, len(c2_bad), c2_bad[:5]))
    log.append('C3 AF4 equals MM1-v3.2 in every number off gemmLnc: %d rows, differing %d %s' % (c3, len(c3_bad), c3_bad[:5]))
    log.append('C4 MM1-v3.2 energy law at t: %d rows, failing %d %s' % (c4, len(c4_bad), c4_bad[:5]))
    nin = sum(1 for c in comp if c['acting'].startswith('the reference'))
    nlnc = sum(1 for c in comp if c['acting'].startswith('AF4'))
    log.append('composed rows %d: the reference acts at %d (factor range %.4f-%.4f), AF4 at %d, neither at %d' %
               (len(comp), nin, min([c['factor_mask_ceiling'] for c in comp if c['acting'].startswith('the reference')] or [1]),
                max([c['factor_mask_ceiling'] for c in comp if c['acting'].startswith('the reference')] or [1]), nlnc, len(comp) - nin - nlnc))
    ok = c1_ok and not c2_bad and not c3_bad and not c4_bad
    log.append('COMPOSITION BY CONSTRUCTION: %s' % ('SHOWN (C1-C4 hold)' if ok else 'NOT SHOWN'))
    json.dump({'what': "'MM1-v3.2 + AF4 + mask-ceiling' at E222's and E224's registered points, by construction (no refit); REPORTED, not blind",
               'checks': log, 'ok': ok, 'rows': comp}, open(os.path.join(LANE, 'work/composed-af4-REPORTED.json'), 'w'), indent=0)
    open(os.path.join(LANE, 'logs/c01.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
