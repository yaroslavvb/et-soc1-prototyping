#!/usr/bin/env python3
"""unread-e214 (Q225) step 1c: every E214 energy cell (format, energy kind, KB class) through each frozen model's own count and phi readers
after the declared table rows are added in memory (verify-counts-e214's fix: merge counts-e214's two tables by the model's own loop, no key
colliding), and the facts behind the sp_ar4 gate declaration. Desk; no device; no E214 measurement opened (runs-listed.json only).
  v31: MM1-v3.1 (energy_v31): counts-e214's rows added to E210C31 / SWT31; phi for the 20 new kinds pre-set in phi31's memo (_PHI31) from
       step 1b's values (kinds_v3.phi over E214's tile files); sparse50f / h / i priced as 'sparse50'.
  v3:  MM1-v3 (energy_v3): v31-counts' rows (3e8991d0, tools/matmul/mm1/v3.1/counts) and counts-e214's rows added to E210C / SWT; phi for the
       new kinds pre-set in phi_of's memo (_PHI); sparse50 as above.
Run: /usr/bin/python3 -I -B s01c_cells.py <lane dir> <v31|v3>
"""
import json
import os
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
MODEL = sys.argv[2]
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
CNT = os.path.join(L, 'work', 'counts-e214')
OUTD = os.path.join(L, 'work', 'step1')
R = json.load(open(os.path.join(OUTD, 'runs-listed.json')))['runs']
PHI = json.load(open(os.path.join(OUTD, 'models-step1.json')))['phi_new_kinds']
C32n = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16n = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
added = []
if MODEL == 'v31':
    sys.path.insert(0, os.path.join(MM1, 'v3.1'))
    import energy_v31 as EV  # noqa: E402
    EN = EV.EN
    T32, T16 = EV.E210C31, EV.SWT31
    for sh in ('S1', 'S2'):
        for k, r in C32n[sh].items():
            assert k not in T32[sh], (sh, k)
            T32[sh][k] = r
            added.append(f'E210C31[{sh}][{k}]')
    for k, r in C16n.items():
        assert k not in T16, k
        T16[k] = r
        added.append(f'SWT31[{k}]')
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            assert (fmt, kind, kb1) not in EV._PHI31
            EV._PHI31[(fmt, kind, kb1)] = (float(v['phi']), "kinds_v3.phi over E214's registered tile file (unread-e214's declaration)")

    def count(fmt, kind, KB):
        return EV.counts31(fmt, kind, KB)

    def phi(fmt, kind, KB):
        return EV.phi31(fmt, kind, KB)

    def usable(e):
        return bool(EV.Features31([e]).usable3[0])
else:
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import energy_v3 as EN  # noqa: E402
    V31C = os.path.join(MM1, 'v3.1', 'counts')
    C32o = json.load(open(os.path.join(V31C, 'counts-fp32-gemm-states.json')))['shapes']
    C16o = json.load(open(os.path.join(V31C, 'counts-fp16-int8-launch.json')))['rows']
    for tag, (A32, A16) in (('v31-counts 3e8991d0', (C32o, C16o)), ('counts-e214', (C32n, C16n))):
        for sh in ('S1', 'S2'):
            for k, r in A32[sh].items():
                assert k not in EN.E210C[sh], (sh, k)
                EN.E210C[sh][k] = r
                added.append(f'{tag}: E210C[{sh}][{k}]')
        for k, r in A16.items():
            assert k not in EN.SWT, k
            EN.SWT[k] = r
            added.append(f'{tag}: SWT[{k}]')
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            assert EN._PHI.get((fmt, kind, kb1)) is None
            EN._PHI[(fmt, kind, kb1)] = float(v['phi'])

    def count(fmt, kind, KB):
        return EN.counts(fmt, kind, KB)

    def phi(fmt, kind, KB):
        return EN.phi_of(fmt, kind, KB), 'energy_v3.phi_of (memo pre-set for the new kinds)'

    def usable(e):
        return bool(EN.Features([e]).usable3[0])

cells = {}
for r in R:
    KB = r['KB']
    key = f"{r['fmt']}|{r['kind_energy']}|{'S1' if KB == 1 else 'S2'}"
    if key in cells:
        cells[key]['runs'] += 1
        continue
    c = count(r['fmt'], r['kind_energy'], KB)
    p, rule = phi(r['fmt'], r['kind_energy'], KB)
    e = {'card': r['card'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'arm': r['arm'], 'kernel': 'rgm136', 'minions': r['minions'],
         'mask': r['mask'], 'f': 600.0, 'T': 1.0, 'w': 0.0, 'idle_w': None, 'G': 0.0, 'die_start': 50.0, 's': 1.0}
    cells[key] = {'count_S_per_op': (None if c is None else float(c[0])), 'valid_share_v': (None if c is None else float(c[1])),
                  'phi': (None if p is None else float(p)), 'phi_rule': rule, 'usable3': usable(e), 'runs': 1,
                  'gate_shares_frozen': list(EN.gate_shares(r['fmt'], r['kind_energy'], c[1])) if c is not None else None}
# the sp_ar4 facts: the count's valid share at S1 / S2 and A's all-zero rows (tile bytes: A = the first 1,024 bytes, 16 x 16 fp32)
E214T = os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e214', 'proposal', 'src', 'tiles', 'fp32', 'sp_ar4.bin')
b = open(E214T, 'rb').read()
A = np.frombuffer(b[:1024], dtype='<f4').reshape(16, 16)
B = np.frombuffer(b[1024:], dtype='<f4').reshape(16, 16)
sp = {'valid_share_S1': C32n['S1']['pattern:sp_ar4'].get('valid_slots'), 'valid_share_S2': C32n['S2']['pattern:sp_ar4'].get('valid_slots'),
      'A_all_zero_rows': [int(i) for i in range(16) if not A[i].any()], 'A_all_zero_cols': [int(j) for j in range(16) if not A[:, j].any()],
      'B_all_zero_rows': [int(i) for i in range(16) if not B[i].any()], 'A_zero_share': float((A == 0).mean()), 'B_zero_share': float((B == 0).mean()),
      'arow50_count_S1_valid': EN.E210C['S1'].get('arow50', {}).get('valid_slots'), 'arow50_count_S2_valid': EN.E210C['S2'].get('arow50', {}).get('valid_slots'),
      'gate_shares_frozen_sp_ar4': list(EN.gate_shares('fp32', 'pattern:sp_ar4', 0.5)), 'gate_shares_arow50': list(EN.gate_shares('fp32', 'arow50', 0.5))}
out = {'model': MODEL, 'python': sys.version.split()[0], 'rows_added': added, 'cells': cells, 'sp_ar4': sp,
       'cells_without_energy': sorted(k for k, v in cells.items() if not v['usable3'])}
json.dump(out, open(os.path.join(OUTD, f'cells-{MODEL}.json'), 'w'), indent=1, sort_keys=True)
print(MODEL, 'rows added', len(added), '; cells', len(cells), '; usable', sum(v['usable3'] for v in cells.values()),
      '; without energy', out['cells_without_energy'])
print(json.dumps(sp))
