#!/usr/bin/env python3
"""Lane l3-edge (Q234), exploration (desk, post hoc reading of committed code only; no datum of E220).
For a few rgm136 gemmL shapes at the full mask: the walk's exact chip-level LRU stack distances (v3.1 walk, 1 KiB tiles, the active
shires in lock step, C stores allocating) of every A and B tile request of the second pass, against MM1-v3's closed-form group distances.
Prints quantiles and the share of requests per distance band, per operand.
"""
import json
import os
import sys

LAB = os.environ.get('ET_LAB') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk'))
sys.path.insert(0, os.path.join(LAB, 'tools/matmul/mm1/v3'))
import walk_v31 as W  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

shapes = [tuple(int(x) for x in s.split('x')) for s in sys.argv[1:]] or [(2, 1, 7), (2, 1, 6), (3, 1, 7), (1, 1, 7), (2, 1, 8)]
out = {}
for MB, NB, KB in shapes:
    recA, recB = W.l3_distances('rgm136.gemmL', MB, NB, KB, 0xFFFFFFFF)
    dA = sorted(d / 1024.0 for st in recA for d, _ in st)
    dB = sorted(d / 1024.0 for st in recB for d, _ in st)

    def q(v, p):
        return v[min(len(v) - 1, int(p * len(v)))]

    def band(v, lo, hi):
        return sum(1 for x in v if lo <= x < hi) / len(v)
    gs = C.groups_masked(MB, NB, KB)
    cf = {name: {'count': cnt, 'l2': l2, 'd_min': min(ds), 'd_max': max(ds), 'd_mean': sum(ds) / len(ds)} for name, cnt, l2, ds in gs}
    rec = {'footprint_MB': C.footprint(MB, NB, KB), 'walk_footprint': W.footprint_tiles('rgm136.gemmL', MB, NB, KB, 0xFFFFFFFF),
           'A': {'n': len(dA), 'q05': q(dA, .05), 'q25': q(dA, .25), 'q50': q(dA, .5), 'q75': q(dA, .75), 'q95': q(dA, .95),
                 'min': dA[0], 'max': dA[-1], 'lt32': band(dA, 0, 32), '32_36': band(dA, 32, 36), '36_40': band(dA, 36, 40),
                 '40_48': band(dA, 40, 48), 'ge48': band(dA, 48, 1e18)},
           'B': {'n': len(dB), 'q05': q(dB, .05), 'q25': q(dB, .25), 'q50': q(dB, .5), 'q75': q(dB, .75), 'q95': q(dB, .95),
                 'min': dB[0], 'max': dB[-1], 'lt32': band(dB, 0, 32), '32_36': band(dB, 32, 36), '36_40': band(dB, 36, 40),
                 '40_48': band(dB, 40, 48), 'ge48': band(dB, 48, 1e18)},
           'closed_form': cf}
    out['%dx%dx%d' % (MB, NB, KB)] = rec
    print('gemmL%dx%dx%d F %.1f MB' % (MB, NB, KB, rec['footprint_MB']))
    for op in ('A', 'B'):
        r = rec[op]
        print('  %s n %6d  q05 %.2f q50 %.2f q95 %.2f [min %.2f max %.2f] <32 %.3f 32-36 %.3f 36-40 %.3f 40-48 %.3f >=48 %.3f' % (
            op, r['n'], r['q05'], r['q50'], r['q95'], r['min'], r['max'], r['lt32'], r['32_36'], r['36_40'], r['40_48'], r['ge48']))
    for name, v in cf.items():
        print('  cf %-6s count %5.1f l2 %5.1f d %.2f..%.2f' % (name, v['count'], v['l2'], v['d_min'], v['d_max']))
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'out', 'explore'), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'out', 'explore', 'walk_explore.json'), 'w'), indent=1)
