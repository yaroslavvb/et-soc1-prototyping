#!/usr/bin/env python3
"""MM1-v1: THE TIE, run before any fit. The masked closed-form map (mm1_core.groups_masked) at strict L3 caps of 32, 28 and 24 MB against E206's
registered LRU lines (inputs/reuse-e206.json: E136's l3_model and E206's l3_model_masked), on every E206 gemmL shape and mask; and the masked
map at the full mask against design B's groups() (equal number for number). Desk; numpy.

    /usr/bin/python3 -I -B tie_masked_map.py --out <dir>       writes tie_masked_map.json
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mm1_core as C  # noqa: E402

RU = json.load(open(os.path.join(HERE, 'inputs', 'reuse-e206.json')))


def strict_lines(arm, mask, cap):
    sh = C.Shape(arm, mask, masked_map=True)
    A = np.zeros(3); B = np.zeros(3)
    for name, cnt, l2, ds in sh.groups:
        rr = float(np.mean((ds < cap).astype(float)))
        v = np.array([l2, (cnt - l2) * rr, (cnt - l2) * (1 - rr)])
        if name.startswith('A'):
            A += v
        else:
            B += v
    return A, B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    # 1. the masked map at the full mask equals design B's groups() (w = 1) number for number, on every shape below and E206's
    shapes = set()
    for k, v in RU['shapes'].items():
        MB, NB, KB = v['blocks']
        shapes.add((MB, NB, KB))
    for s in [(1, 3, 2), (2, 3, 2), (3, 2, 2), (1, 4, 3), (1, 9, 3), (2, 3, 5), (3, 3, 4), (5, 2, 3), (3, 5, 5), (6, 6, 6), (1, 3, 24), (3, 6, 4), (1, 2, 2)]:
        shapes.add(s)
    worst_eq = 0.0
    for MB, NB, KB in sorted(shapes):
        a = C.LM.groups(MB, NB, KB, 1.0)
        b = C.groups_masked(MB, NB, KB, 1.0, 1.0, 1.0)
        assert [g[0] for g in a] == [g[0] for g in b]
        for ga, gb in zip(a, b):
            assert ga[1] == gb[1] and ga[2] == gb[2] and len(ga[3]) == len(gb[3])
            worst_eq = max(worst_eq, max(abs(x - y) for x, y in zip(ga[3], gb[3])))
    print(f'1. masked map at the full mask vs design B groups(): {len(shapes)} shapes, worst |distance diff| {worst_eq:.3e} MB '
          f'({"EQUAL" if worst_eq < 1e-9 else "DIFFER"})')
    # 2. against E206's LRU lines at strict caps (convention: n_fresh = min(miss, 64 (1 - A_in) + 128 (1 - B_in)), n_L3 = miss - n_fresh)
    rows = []
    for k, v in sorted(RU['shapes'].items()):
        MB, NB, KB = v['blocks']
        arm = 'gemmL%dx%dx%d' % (MB, NB, KB)
        mask = v['shire_mask']
        for cap in (32, 28, 24):
            A, B = strict_lines(arm, mask, cap)
            mine_L3, mine_F = A[1] + B[1], A[2] + B[2]
            ref = v['lines']['%dMB' % cap]
            rows.append({'shape': k, 'shires': v['shires'], 'cap_MB': cap, 'lru_n_L3': ref['n_L3'], 'lru_n_fresh': ref['n_fresh'],
                         'map_n_L3': round(mine_L3, 3), 'map_n_fresh': round(mine_F, 3), 'd_L3': round(mine_L3 - ref['n_L3'], 3),
                         'd_fresh': round(mine_F - ref['n_fresh'], 3), 'subset': v['shires'] < 32})
    sub = [r for r in rows if r['subset']]
    full = [r for r in rows if not r['subset']]
    for lab, rr in (('subset points (the tie)', sub), ('full-chip shapes (design B closed form vs LRU, for reference)', full)):
        w = max(max(abs(r['d_L3']), abs(r['d_fresh'])) for r in rr)
        n4 = sum(1 for r in rr if abs(r['d_L3']) <= 4 and abs(r['d_fresh']) <= 4)
        print(f'2. {lab}: {len(rr)} shape-cap rows; worst |line diff| {w:.3f} of 192; within 4 lines {n4} of {len(rr)}')
    for r in sub:
        print('   %-28s %2d shires cap %d: LRU (L3 %7.3f, F %7.3f)  map (L3 %7.3f, F %7.3f)  diff (%+.3f, %+.3f)' % (
            r['shape'], r['shires'], r['cap_MB'], r['lru_n_L3'], r['lru_n_fresh'], r['map_n_L3'], r['map_n_fresh'], r['d_L3'], r['d_fresh']))
    bad = [r for r in full if max(abs(r['d_L3']), abs(r['d_fresh'])) > 4]
    for r in bad:
        print('   full-chip over 4 lines: %-24s cap %d LRU (%.2f, %.2f) map (%.2f, %.2f)' % (r['shape'], r['cap_MB'], r['lru_n_L3'], r['lru_n_fresh'],
                                                                                         r['map_n_L3'], r['map_n_fresh']))
    tie_ok = worst_eq < 1e-9 and all(abs(r['d_L3']) <= 4 and abs(r['d_fresh']) <= 4 for r in sub)
    print('TIE', 'PASS' if tie_ok else 'FAIL', '(the masked map equals groups() at the full mask; every subset point within 4 lines of 192 of E206\'s LRU lines at every cap)')
    json.dump({'what': "MM1-v1's masked closed-form map against E206's registered LRU lines (reuse-e206.json) at strict caps, before any fit",
               'python': sys.version.split()[0], 'full_mask_equals_groups': worst_eq < 1e-9, 'worst_full_mask_diff_MB': worst_eq,
               'rows': rows, 'tie_rule': 'every subset row within 4 lines (of 192) in n_L3 and n_fresh, at 32, 28 and 24 MB', 'tie_ok': tie_ok},
              open(os.path.join(args.out, 'tie_masked_map.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
