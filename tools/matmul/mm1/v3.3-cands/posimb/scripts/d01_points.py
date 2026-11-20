#!/usr/bin/env python3
"""layout2 (Q234) d01: every committed matmul time point through E219 in MM1-v3.2's point form.

  1. MM1-v3.2's own 2508 time points (data_v32.time_points(), E105-E215), checked against its fit record's ids;
  2. E216 (aifoundry2 card 0, 46 points): the frozen scorer's measured route c per point (scored-e216.json, data a8ce142d, scores 5478fce9);
  3. E217 (aifoundry1, seven sessions, 486 cases): blind-e217's case table (f522d6ef), every case with a measured wall;
  4. E218 (aifoundry3 card 0, 52 points): the frozen scorer's measured record per point (scores-e218-A.json, 0f046200);
  5. E219 (aifoundry1, 139 in-domain cases): blind-e219's case table (544d5cfd).
Op time T (us) = measured wall cycles an op / the measured clock (MHz); the clock is the point's own measured clock.
Desk; /usr/bin/python3 3.12.3 -I -B; reads committed files of the lane's scratch clone only. Output: work/points_all.json.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import os
import sys

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import data_v32 as DV32  # noqa: E402
import time_v31 as TV  # noqa: E402

E = TV.E


def kernel_of(arm, kernel_hint='rgm136'):
    pre, b = E.arm_parts(arm)
    if pre is None:
        return 'run_gemm'
    if pre == 'gemmLn':
        return 'rgm211'
    return kernel_hint


def main():
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    P = DV32.time_points()
    ids = [p['id'] for p in P]
    assert ids == rec['ids'], 'v3.2 point set differs from its fit record'
    out = []
    for p in P:
        q = {k: p[k] for k in ('id', 'exp', 'arm', 'kernel', 'fmt', 'mask', 'card', 'f', 'T') if k in p}
        q['kind'] = p.get('kind')
        q['src'] = 'v32-fit'
        out.append(q)
    n_old = len(out)
    # ---- E216
    d6 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))
    reg6 = {r['id']: r for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e216/points-e216.csv')))}
    n6 = 0
    for pid, rec6 in sorted(d6['points'].items()):
        m = rec6.get('measured_route_c') or {}
        if not m.get('wall') or not m.get('col'):
            continue
        r = reg6[pid]
        f = float(m['col'])
        kern = r['loop'].split()[0]
        out.append({'id': 'E216|a2c0|' + pid, 'exp': 'E216', 'arm': r['arm'], 'kernel': kernel_of(r['arm'], kern), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': r['mask'], 'card': 'aifoundry2 card 0', 'f': f, 'T': float(m['wall']) / f,
                    'cw': float(m['wall']), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': r['family'], 'pair': r.get('pair', ''),
                    'src': 'E216 scored-e216.json measured_route_c'})
        n6 += 1
    # ---- E218
    d8 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))
    reg8 = {r['id']: r for r in csv.DictReader(open(os.path.join(V32, 'out/e218/points-e218.csv')))}
    n8 = 0
    for pid, m in sorted(d8['measured'].items()):
        if not m.get('cw'):
            continue
        r = reg8[pid]
        f = float(r.get('f_mhz') or 600.0)
        kern = r['loop'].split()[0]
        out.append({'id': 'E218|a3c0|' + pid, 'exp': 'E218', 'arm': r['arm'], 'kernel': kernel_of(r['arm'], kern), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': r['mask'], 'card': 'aifoundry3 card 0', 'f': f, 'T': float(m['cw']) / f,
                    'cw': float(m['cw']), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': r['family'], 'pair': r.get('pair', ''),
                    'src': 'E218 scores-e218-A.json measured'})
        n8 += 1
    # ---- E217
    n7 = 0
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e217-scores/cases/scores-blind-e217-cases.csv'))):
        if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
            continue
        f = float(r['f_mean_mhz'])
        cw = float(r['meas_cyc_wall'])
        ck = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1'}[r['card']]
        out.append({'id': 'E217|%s|%s' % (ck, r['case']), 'exp': 'E217', 'arm': r['arm'], 'kernel': kernel_of(r['arm']), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': r['mask'], 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': r.get('n_time'),
                    'group_kind': r.get('group_kind'), 'group_shape': r.get('group_shape'), 'src': 'blind-e217 cases'})
        n7 += 1
    # ---- E219 (in-domain cases)
    n9 = 0
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e219-scores/cases/scores-blind-e219-cases.csv'))):
        if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
            continue
        f = float(r['f_mean_mhz'])
        cw = float(r['meas_cyc_wall'])
        ck = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1'}[r['card']]
        arm = r['token']
        out.append({'id': 'E219|%s|%s' % (ck, r['case']), 'exp': 'E219', 'arm': arm, 'kernel': kernel_of(arm, r.get('kernel') or 'rgm136'), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': r['mask'], 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': r.get('n_time'),
                    'class': r.get('class'), 'src': 'blind-e219 cases'})
        n9 += 1
    ids = [p['id'] for p in out]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    json.dump({'points': out, 'counts': {'v32_fit': n_old, 'E216': n6, 'E217': n7, 'E218': n8, 'E219': n9}},
              open(os.path.join(LANE, 'work/points_all.json'), 'w'), indent=0)
    print('points', len(out), {'v32_fit': n_old, 'E216': n6, 'E217': n7, 'E218': n8, 'E219': n9})


if __name__ == '__main__':
    main()
