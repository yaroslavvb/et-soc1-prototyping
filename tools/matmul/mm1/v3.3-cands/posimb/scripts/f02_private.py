#!/usr/bin/env python3
"""layout2 (Q234) f02: per subset configuration of rgm136's gemmL loop, the walk's DRAM-served (fresh) requests split by whether their
tile is asked by one active shire only (private) or by two or more (shared), at the strict-LRU L3 capacity of 32 MB (1 KiB tiles), pass 2,
by verify-lay's committed v01_map.my_steps generator (the same walk the layout features use) and v01_map.lru_fresh's LRU logic, here with
each tile's sharers carried along; plus the active shires' L3-latency figures on the MARTY mesh (110 + 12 hops law, the 32 homes).
  Fp = private fresh requests / all requests;  Fs = shared fresh requests (a shared tile counts once per asking shire) / all requests;
  L(s) = 110 + 12 hbar(s), hbar(s) = shire s's mean hop to the 32 homes; Lmean_act, Lmax_act over the active shires; Lmean_full = 154.95.
Desk; /usr/bin/python3 3.12.3 -I -B, single-threaded. Usage: f02_private.py <points_json> <out_json> (configs taken from the points).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
C215 = os.path.join(LAB, 'tools/matmul/mm1/v3.2-terms/layout/controls-e215')
os.environ.setdefault('ET_LAB', LAB)
spec = importlib.util.spec_from_file_location('v01_map_committed', os.path.join(C215, 'v01_map.py'))
V01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V01)
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF
CAP_TILES = 32 * 1024
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}


def hp(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HBAR = {s: float(np.mean([hp(MARTY[s], MARTY[h]) for h in range(32)])) for s in range(32)}
LAT = {s: 110.0 + 12.0 * HBAR[s] for s in range(32)}
LMEAN_FULL = float(np.mean([LAT[s] for s in range(32)]))


def mesh_lat(mask):
    sh = [s for s in range(32) if (mask >> s) & 1]
    L = np.array([LAT[s] for s in sh])
    return {'Lmean_act': float(L.mean()), 'Lmax_act': float(L.max()), 'Lmean_full': LMEAN_FULL, 'n': len(sh)}


def private_shared(MB, NB, KB, mask):
    seq = list(V01.my_steps(MB, NB, KB, mask))
    od = collections.OrderedDict()
    nsteps = 0
    priv = shared = req = 0
    for p in range(2):
        rec = p == 1
        for st in seq:
            if st[0] == 'store':
                for a in st[1]:
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > CAP_TILES:
                            od.popitem(last=False)
                continue
            if rec:
                nsteps += 1
            for lst in (st[1], st[2]):
                for a, sharers in lst:
                    k = len(sharers)
                    if rec:
                        req += k
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > CAP_TILES:
                            od.popitem(last=False)
                        if rec:
                            if k == 1:
                                priv += 1
                            else:
                                shared += k
    return {'Fp': priv / req, 'Fs': shared / req, 'req_tiles': req, 'steps': nsteps}


def main():
    pts_fn, out_fn = sys.argv[1], sys.argv[2]
    P = json.load(open(pts_fn))
    P = P['points'] if isinstance(P, dict) else P
    need = set()
    for p in P:
        m = int(p['mask'], 16)
        if m != FULL and p.get('kernel', 'rgm136') == 'rgm136' and SHAPE.match(p['arm']):
            need.add((p['arm'], m))
    out = json.load(open(out_fn)) if os.path.exists(out_fn) else {}
    t0 = time.time()
    todo = sorted(k for k in need if '%s|0x%x' % k not in out)
    print('configurations', len(need), 'to make', len(todo), flush=True)
    for i, (arm, m) in enumerate(todo):
        MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
        r = private_shared(MB, NB, KB, m)
        r.update(mesh_lat(m))
        out['%s|0x%x' % (arm, m)] = r
        if (i + 1) % 25 == 0:
            print('  %d/%d (%.0f s)' % (i + 1, len(todo), time.time() - t0), flush=True)
            json.dump(out, open(out_fn + '.tmp', 'w'), indent=0, sort_keys=True)
            os.replace(out_fn + '.tmp', out_fn)
    json.dump(out, open(out_fn + '.tmp', 'w'), indent=0, sort_keys=True)
    os.replace(out_fn + '.tmp', out_fn)
    print('done', len(out), round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
