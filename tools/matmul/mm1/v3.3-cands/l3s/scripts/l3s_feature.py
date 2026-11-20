#!/usr/bin/env python3
"""Lane l3-edge (Q234): the L3S term's feature, the A tiles' L3 share in the 4-way set-associative L3 of the public shire-cache
specification, by row half, at the FULL MASK, for a gemmL-family shape (MB, NB, KB) and walk ('mn' rgm136 gemmL / gemmLnc and rgm211
gemmL; 'nm' rgm211 gemmLn). No fitted constant. Standard library only; /usr/bin/python3 3.12.3.

The stream (MM1-v3.1's walk, walk_v31.chip_steps at the full mask, re-generated with integer tile ids; l3sim.py is the general form and
this file's fast path is checked against it by --check): per op step (mb, nb, r, kb, k) the 32 distinct A tiles a_off(mb, kb, row, k),
row = 8 s1 + 2 d + r (s1 < 8, d < 4), and the 32 distinct B tiles b_off(kb, nb, col, k), col = 8 s0 + p (s0 < 4, p < 8), A first; after
each row half every minion's C tile c_off(mb, nb, 2 q + r, c) (q, c < 32) is stored (write-allocate). Pools: C at 0, A at |C| = MB NB
2 MiB, B at |C| + |A| (rgm136's host allocation order, one arm a device process; a common base only permutes the sets). The L3: 8192
tile-sets (a 1 KiB tile's 16 lines fall in 16 consecutive line-sets PA[22:6]; 2^17 sets of 4 ways x 64 B = 32 MiB, period 8 MiB), 4 ways,
true LRU. Two passes; the second recorded. At the full mask every A tile serves 32 minions and every B tile 32: the shares are counts.

    python3 -I -B l3s_feature.py --points <points_all.json> [--extra MBxNBxKB:walk ...] --cache <json>   (adds missing shapes)
    python3 -I -B l3s_feature.py --check                                                              (fast path = l3sim.simulate)
"""
import argparse
import json
import os
import re
import sys
import time

SETS, WAYS = 8192, 4


def domain_key(p):
    """(MB, NB, KB, walk) when the point is in the L3S term's domain, else None: the gemmL-family loops at the full mask, any KB"""
    m = re.fullmatch(r'(gemmLnc|gemmLn|gemmL)(\d+)x(\d+)x(\d+)', p['arm'])
    if not m or p['mask'].lower() != '0xffffffff':
        return None
    MB, NB, KB = (int(x) for x in m.groups()[1:])
    walk = 'nm' if (m.group(1) == 'gemmLn' and p.get('kernel') == 'rgm211') else 'mn'
    return (MB, NB, KB, walk)


def a_shares(MB, NB, KB, walk):
    sets = [[] for _ in range(SETS)]
    A0 = MB * NB * 2048
    B0 = A0 + MB * KB * 2048
    order = [(mb, nb) for mb in range(MB) for nb in range(NB)] if walk == 'mn' else [(mb, nb) for nb in range(NB) for mb in range(MB)]
    joff = [64 * j for j in range(32)]
    boff = [32 * j for j in range(32)]
    coff = [64 * q + c for q in range(32) for c in range(32)]
    hA = [0, 0]
    nA = [0, 0]
    hB = [0, 0]
    nB = [0, 0]
    for p in range(2):
        rec = p == 1
        for mb, nb in order:
            cb = (mb * NB + nb) * 2048
            for r in (0, 1):
                ha = hb = na = nb_ = 0
                for kb in range(KB):
                    abase = A0 + (mb * KB + kb) * 2048 + 32 * r
                    bbase = B0 + (kb * NB + nb) * 1024
                    for k in range(32):
                        a0 = abase + k
                        for o in joff:
                            t = a0 + o
                            s = sets[t & 8191]
                            if t in s:
                                if s[-1] != t:
                                    s.remove(t)
                                    s.append(t)
                                ha += 1
                            else:
                                s.append(t)
                                if len(s) > WAYS:
                                    del s[0]
                        b0 = bbase + k
                        for o in boff:
                            t = b0 + o
                            s = sets[t & 8191]
                            if t in s:
                                if s[-1] != t:
                                    s.remove(t)
                                    s.append(t)
                                hb += 1
                            else:
                                s.append(t)
                                if len(s) > WAYS:
                                    del s[0]
                        na += 32
                        nb_ += 32
                c0 = cb + 32 * r
                for o in coff:
                    t = c0 + o
                    s = sets[t & 8191]
                    if t in s:
                        if s[-1] != t:
                            s.remove(t)
                            s.append(t)
                    else:
                        s.append(t)
                        if len(s) > WAYS:
                            del s[0]
                if rec:
                    hA[r] += ha
                    nA[r] += na
                    hB[r] += hb
                    nB[r] += nb_
    return {'hA': [hA[0] / nA[0], hA[1] / nA[1]], 'hB': [hB[0] / nB[0], hB[1] / nB[1]], 'nA': nA, 'nB': nB}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--points')
    ap.add_argument('--extra', nargs='*', default=[])
    ap.add_argument('--cache')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.check:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import l3sim as S
        worst = 0.0
        for (MB, NB, KB, walk) in [(2, 1, 7, 'mn'), (1, 2, 9, 'mn'), (2, 2, 7, 'mn'), (2, 3, 5, 'nm'), (3, 2, 4, 'mn'), (1, 1, 16, 'mn')]:
            f = a_shares(MB, NB, KB, walk)
            g = S.simulate(MB, NB, KB, 0xFFFFFFFF, walk)
            for r in (0, 1):
                worst = max(worst, abs(f['hA'][r] - g['hA_sa'][r] / g['wA'][r]), abs(f['hB'][r] - g['hB_sa'][r] / g['wB'][r]))
            print('check', MB, NB, KB, walk, f['hA'], [g['hA_sa'][r] / g['wA'][r] for r in (0, 1)])
        print('CHECK worst |difference|', worst, 'PASS' if worst < 1e-12 else 'FAIL')
        return
    cache = json.load(open(a.cache)) if a.cache and os.path.exists(a.cache) else {}
    keys = set()
    if a.points:
        for p in json.load(open(a.points)):
            k = domain_key(p)
            if k:
                keys.add(k)
    for e in a.extra:
        s, _, w = e.partition(':')
        keys.add(tuple(int(x) for x in s.split('x')) + (w or 'mn',))
    todo = sorted((k for k in keys if '%dx%dx%d:%s' % k not in cache), key=lambda k: k[0] * k[1] * k[2])
    print('shapes', len(keys), 'to do', len(todo), flush=True)
    t0 = time.time()
    for i, k in enumerate(todo):
        t1 = time.time()
        cache['%dx%dx%d:%s' % k] = a_shares(*k)
        if (i % 20 == 0) or time.time() - t1 > 5:
            print(i, k, round(time.time() - t1, 1), 's; total', round(time.time() - t0, 1), flush=True)
            json.dump(cache, open(a.cache + '.tmp', 'w'))
            os.replace(a.cache + '.tmp', a.cache)
    json.dump(cache, open(a.cache + '.tmp', 'w'), sort_keys=True)
    os.replace(a.cache + '.tmp', a.cache)
    print('done', len(cache), 'shapes in cache;', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
