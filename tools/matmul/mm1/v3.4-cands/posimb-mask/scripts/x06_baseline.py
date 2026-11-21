#!/usr/bin/env python3
"""mask-posimb (Q238) x06: MM1-v3.2's own baseline before the declaration (no candidate constant fitted): its all-data base op time against the
measured at E221's 363 MASK cases that blind-e221 scored as no-twin for MM1-v3.2 (the 12.41%), compared case by case with blind-e221's
committed v32_e_wall; and the A1 shares among those cases. Desk; numpy; single-threaded."""
import json
import os

import numpy as np

LANE = os.environ['MASKPOS_LANE']
D = json.load(open(os.path.join(LANE, 'work/points_all.json')))
P = D['points']
Z = np.load(os.path.join(LANE, 'work/base.npz'))
Tm = Z['T_meas']
b = Z['base_all']
sel = [j for j, p in enumerate(P) if p['exp'] == 'E221' and p['cls221'] == 'MASK' and not p['twin_v32_e221']]
e_mine = np.array([b[j] / Tm[j] - 1 for j in sel])
e_comm = np.array([P[j]['v32_e_wall_committed'] for j in sel])
print('n', len(sel), 'rms mine %.4f%%, committed %.4f%%, max |diff| %.3e' % (100 * np.sqrt(np.mean(e_mine ** 2)), 100 * np.sqrt(np.mean(e_comm ** 2)), np.max(np.abs(e_mine - e_comm))))


def A1(m):
    m = int(m, 16)
    return int(not any(((s >> 2) & 3) == (s & 3) for s in range(32) if (m >> s) & 1))


a = np.array([A1(P[j]['mask']) for j in sel])
print('A1 = 1 among them: %d of %d; rms by A1: 1 -> %.2f%%, 0 -> %.2f%%' % (a.sum(), len(a), 100 * np.sqrt(np.mean(e_mine[a == 1] ** 2)), 100 * np.sqrt(np.mean(e_mine[a == 0] ** 2))))
json.dump({'n': len(sel), 'rms_mine_pct': float(100 * np.sqrt(np.mean(e_mine ** 2))), 'rms_committed_pct': float(100 * np.sqrt(np.mean(e_comm ** 2))),
           'max_abs_diff': float(np.max(np.abs(e_mine - e_comm)))}, open(os.path.join(LANE, 'work/x06_baseline.json'), 'w'), indent=1)
