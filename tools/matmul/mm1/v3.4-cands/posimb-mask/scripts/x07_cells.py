#!/usr/bin/env python3
"""mask-posimb (Q238) x07: before the declaration: MM1-v3.2's elasticity e and residual at the in-scope 1x1x1 cells (subset masks) against the
other in-scope points; A1's share there. No fit. Desk; numpy; single-threaded."""
import json, os, re
import numpy as np
LANE = os.environ['MASKPOS_LANE']
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
D = json.load(open(os.path.join(LANE, 'work/points_all.json'))); P = D['points']
Z = np.load(os.path.join(LANE, 'work/base.npz')); Tm = Z['T_meas']; b = Z['base_all']; e = Z['e_all']
def A1(m):
    m = int(m, 16)
    return int(not any(((s >> 2) & 3) == (s & 3) for s in range(32) if (m >> s) & 1))
cell = []; other = []
for j, p in enumerate(P):
    m = SH.match(p['arm'])
    if p['kernel'] == 'rgm136' and m and int(p['mask'], 16) != 0xFFFFFFFF:
        (cell if tuple(int(x) for x in m.groups()) == (1, 1, 1) else other).append(j)
for nm, jj in (('1x1x1 cells', cell), ('other in-scope', other)):
    jj = np.array(jj); r = np.log(Tm[jj] / b[jj]); a = np.array([A1(P[j]['mask']) for j in jj])
    print('%-15s n %4d  e min/median/max %.3f %.3f %.3f  resid rms %.2f%%  A1=1 n %d mean resid %+.2f%%  A1=0 mean %+.2f%%' % (
        nm, len(jj), e[jj].min(), np.median(e[jj]), e[jj].max(), 100 * np.sqrt(np.mean(r ** 2)), a.sum(),
        100 * r[a == 1].mean() if a.sum() else np.nan, 100 * r[a == 0].mean()))
