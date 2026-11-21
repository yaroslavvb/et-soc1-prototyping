#!/usr/bin/env python3
"""mask-mesh x02 (EXPLORATION, post hoc, disclosed in DECLARED): the mechanism's raw numbers (mesh_l3, no fitted constant) at E221's
single-shire placements of six shapes and at each shape's full chip: per mask the SA and FA miss shares of A and B at the laggard and the
chip; printed beside the shire's place. MM1-v3.2's residuals are NOT read here (x01 printed them before). Run: bash run.sh x02_single_look.py <lane dir>"""
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, 'scripts'))
import mesh_l3 as M  # noqa: E402

shapes = ['gemmL2x6x10', 'gemmL1x12x8', 'gemmL3x4x6', 'gemmL1x16x6', 'gemmL4x1x10', 'gemmL2x1x16', 'gemmL2x4x24', 'gemmL4x6x2', 'gemmL1x3x4']
singles = {'gemmL2x6x10': list(range(32))}
out = {}
for arm in shapes:
    ss = singles.get(arm, [10, 14, 17])
    full = M.features(arm, '0xffffffff')
    rows = []
    for s in ss:
        f = M.features(arm, '0x%x' % (1 << s))
        ps = f['per_shire'][str(s)]
        rows.append((s, M.MARTY[s], ((s >> 2) & 3) == (s & 3), ps['xA_SA'], ps['xB_SA'], ps['xA_FA'], ps['xB_FA'], M.HBAR[s]))
    fl = full['per_shire'][str(full['laggard'])]
    print('== %s full chip: laggard %d xA_SA %.4f xB_SA %.4f xA_FA %.4f xB_FA %.4f chip A_SA %.4f B_SA %.4f A_FA %.4f B_FA %.4f' % (
        arm, full['laggard'], fl['xA_SA'], fl['xB_SA'], fl['xA_FA'], fl['xB_FA'], full['chip']['A_SA'], full['chip']['B_SA'],
        full['chip']['A_FA'], full['chip']['B_FA']))
    for r in rows:
        print('   shire %2d at %s collide %d | SA A %.4f B %.4f | FA A %.4f B %.4f | hbar %.3f' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
    out[arm] = {'full': full, 'singles': rows}
json.dump(out, open(os.path.join(L, 'work', 'x02_single_look.json'), 'w'), indent=0, default=str)
