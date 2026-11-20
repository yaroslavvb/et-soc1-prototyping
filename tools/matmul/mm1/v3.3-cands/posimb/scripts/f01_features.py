#!/usr/bin/env python3
"""layout2 (Q234) f01: verify-lay's committed v01_map records (layout_v32.FeatureStore: the committed v01_map.json first, then MM1-v3.2's
cache out/layout/features-v32.json read-only as a seed, else made by v01_map's functions) for every subset configuration of rgm136's gemmL
loop among the points through E219, and each shape's full-chip record. Caches into the lane's own work/features_cache.json (never into the
clone's files). Desk; /usr/bin/python3 3.12.3 -I -B, single-threaded. Output: work/features_cache.json, work/features_points.json.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import sys
import time

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
sys.path.insert(0, V32)
import layout_v32 as LY  # noqa: E402

CAPS = (24, 32, 48)


def main():
    t0 = time.time()
    cache = os.path.join(LANE, 'work/features_cache.json')
    if not os.path.exists(cache):
        shutil.copyfile(os.path.join(V32, 'out/layout/features-v32.json'), cache)
    st = LY.FeatureStore(cache)
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    need = []
    for p in P:
        if LY.is_layout_point(p):
            need.append((p['arm'], LY.mask_int(p['mask'])))
    need = sorted(set(need))
    print('subset configurations', len(need), flush=True)
    rows = {}
    for i, (arm, m) in enumerate(need):
        r, src = LY.feat_row(arm, m, st, caps=CAPS, check=False)
        f, _ = st.get(tuple(int(x) for x in LY.SHAPE.match(arm).groups()), m, caps=CAPS, check=False)
        rows['%s|0x%x' % (arm, m)] = {'feat': r, 'src': src, 'n': f['n'], 'R': f['R'], 'C': f['C'], 'hop_mean': f['hop_mean'],
                                      'hop_max': f['hop_max'], 'fresh': f['fresh_lines_step'], 'req': f['req_lines_step'],
                                      'distinct': f['distinct_lines_step']}
        if (i + 1) % 20 == 0:
            print('  %d/%d made %d (%.0f s)' % (i + 1, len(need), st.made, time.time() - t0), flush=True)
            st.save()
    st.save()
    json.dump(rows, open(os.path.join(LANE, 'work/features_points.json'), 'w'), indent=0, sort_keys=True)
    print('done: %d configurations, made %d, %.0f s' % (len(rows), st.made, time.time() - t0))


if __name__ == '__main__':
    main()
