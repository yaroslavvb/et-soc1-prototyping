#!/usr/bin/env python3
"""fix-unread-e212sw (Q218), ADDENDUM 1, step A2: THE FORECASTS of E209's three real points (POST HOC), before this lane opens any E209 measurement.

The unread lane's step-2 machinery, unchanged (its scripts/s02_forecast.py, sha256 c8166622... as run: the functions decompose, check and W_formula
are copied here verbatim, with the same table rows and phi values added the same way): MM1-v3's landed predictor (b1493082's folder from this
lane's git archive of GitHub main 3e8991d0, SHA256SUMS 170/170) and its frozen parameters (out/mm1_v3_params.json, 1fdc0749...), no refit, no
constant changed; the frozen counts (c74c2d49...) as table rows; phi for every declared kind by rule e (declared-unread.json, 5eb2c93d...).
A first check re-makes the frozen forecast of four entries of forecasts-unread.json (8938bbeb...) and asserts bit-equality, so the machinery is
the frozen one. Then each E209 point gets K0, K1, K2, T600, T800 (V3), N and N2 (the means over the counted kinds), V3phi1, its count and phi.
The form, exact in the run's measured conditions (evaluated in step A3):
    W(t, f, V, T0) = [K0 + g G(f) + (1e6/t)(sV K1 + (1 + xi (sV - 1)) K2)] x (1 + 0.0048 (T0 - 50)),  sV = (V / 0.517 V)^2
Desk; no device; no E209 data file opened (no data loader imported). Run: /usr/bin/python3 -I -B a02_forecast_e209.py
"""
import csv
import hashlib
import json
import os
import sys
import time

import numpy as np

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
WL = os.path.join(ME, 'work', 'lab')
V3 = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3')
CNT = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
LANDU = os.path.join(W, 'out', 'unread-e212sw', 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
OUTD = os.path.join(ME, 'work', 'addendum')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())


AD_P = os.path.join(OUTD, 'addendum-declared-e209.json')
assert sha(AD_P) == '5f9e7f219104afa78f8d2ba89bfe1c5ca4af0e2295ac1c9be858d9321c3531bb', 'addendum declaration changed'
DECL_P = os.path.join(LANDU, 'declared-unread.json')
FC_P = os.path.join(LANDU, 'forecasts-unread.json')
assert sha(DECL_P) == '5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc'
assert sha(FC_P) == '8938bbebd1a6db028d55602773e7c2bce7286f6e378f2bcede948f82deb79f01'
assert sha(os.path.join(CNT, 'SHA256SUMS')) == 'c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f'
PP = os.path.join(V3, 'out', 'mm1_v3_params.json')
assert sha(PP) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
AD = json.load(open(AD_P))
DECL = json.load(open(DECL_P))
FC = json.load(open(FC_P))

sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import mm1_core_v3 as C  # noqa: E402
import mm1_v3  # noqa: E402

C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
PHI = DECL['e_phi']['values']
# ---------------------------------------------------------------- the rows and phi, added exactly as s02_forecast.py adds them
for S in ('S1', 'S2'):
    for kind, row in C32[S].items():
        assert kind not in EN.E210C[S], (S, kind)
        EN.E210C[S][kind] = row
for key, row in C16.items():
    assert key not in EN.SWT, key
    EN.SWT[key] = row
for k, v in PHI.items():
    fmt, kind = k.split('|', 1)
    if kind.startswith('pattern:sparse50'):
        continue
    for kb1 in (True, False):
        key = (fmt, kind, kb1)
        assert EN._PHI.get(key) is None, key
        EN._PHI[key] = float(v)
params = json.load(open(PP))
M3 = mm1_v3.Model(params)
g3 = params['energy']['theta']['g']
xi = params['energy']['theta']['xi']
assert (g3, xi) == (FC['g'], FC['xi'])


# ---------------------------------------------------------------- verbatim from s02_forecast.py (as run, c8166622...)
def decompose(card, arm, fmt, kind, mask):
    """(K0, K1, K2, T600, T800, the predictor's record at sV = 1) for MM1-v3, or None when its energy is NOT FORECAST"""
    a = M3.predict(card, arm, fmt, kind, mask, 600.0, kernel='rgm136', V=0.517, t0_c=50.0, G=0.0)
    if 'W_affine' not in a:
        return None, a
    b = M3.predict(card, arm, fmt, kind, mask, 600.0, kernel='rgm136', V=1.034, t0_c=50.0, G=0.0)
    A1, B1 = a['W_affine']['A_W'], a['W_affine']['B_W_us']
    A4, B4 = b['W_affine']['A_W'], b['W_affine']['B_W_us']
    assert abs(A1 - A4) <= 1e-12 * max(1.0, abs(A1)), (A1, A4)
    s4 = (1.034 / 0.517) ** 2
    q = 1.0 + xi * (s4 - 1.0)
    K1 = (B4 - q * B1) / (1e6 * (s4 - q))
    K2 = B1 / 1e6 - K1
    c = M3.predict(card, arm, fmt, kind, mask, 800.0, kernel='rgm136', V=0.517, t0_c=50.0, G=0.0)
    return {'K0': A1, 'K1': K1, 'K2': K2, 'T600_us': a['T_op_us'], 'T800_us': c['T_op_us']}, a


def W_formula(k, card, t, f, V, T0, g=g3):
    sV = (V / 0.517) ** 2
    return (k['K0'] + g * C.G_of_f(card, f) + (1e6 / t) * (sV * k['K1'] + (1.0 + xi * (sV - 1.0)) * k['K2'])) * (1.0 + 0.0048 * (T0 - 50.0))


def check(k, card, arm, fmt, kind, mask):
    """the formula against the predictor at a test condition, and the class split (terms_v3) at sV 1"""
    f, V, T0, t = 812.5, 0.604, 57.0, 1.37
    p = M3.predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=V, t0_c=T0)
    Wp = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / t
    Wf = W_formula(k, card, t, f, V, T0)
    return abs(Wp / Wf - 1.0)


# ---------------------------------------------------------------- 1. the machinery equals the frozen one: four frozen entries re-made bit for bit
FCR = {r['id']: r for r in FC['rows']}
same = []
for fid in ('E212|a2c0-S2|003-4x8x8-fp32-fld_sign', 'E212|a1c1-S2|064-1x1x1-int8-i8_pm1', 'E212|a1c1-S2|069-1x1x1-fp16-den16_4', 'E206A|p114'):
    fr = FCR[fid]
    k, _ = decompose(fr['card'], fr['arm'], fr['fmt'], fr['priced_as'], fr['mask'])
    eq = all(k[x] == fr['V3'][x] for x in ('K0', 'K1', 'K2', 'T600_us', 'T800_us'))
    same.append({'id': fid, 'bit_equal_V3': eq})
    assert eq, fid
print('machinery check: 4 frozen entries re-made bit for bit:', json.dumps(same))

# ---------------------------------------------------------------- 2. the E209 points
rows = []
for p in AD['points']:
    card, arm, fmt, kind, mask = p['card'], p['arm'], p['fmt'], p['priced_as'], p['mask']
    k3, rec = decompose(card, arm, fmt, kind, mask)
    assert k3 is not None, (p['id'], rec.get('energy'))
    ks = {kk: decompose(card, arm, fmt, kk, mask)[0] for kk in ('zeros', 'ones', 'random')}
    old = {kb: EN._PHI[(fmt, kind, kb)] for kb in (True, False)}
    for kb in (True, False):
        EN._PHI[(fmt, kind, kb)] = 1.0
    kp, _ = decompose(card, arm, fmt, kind, mask)
    for kb in (True, False):
        EN._PHI[(fmt, kind, kb)] = old[kb]
    sw = rec.get('switches') or {}
    rows.append({'id': p['id'], 'point': p['point'], 'group': p['group'], 'card': card, 'arm': arm, 'fmt': fmt, 'kind': p['kind'], 'priced_as': kind,
                 'mask': mask, 'KB': p['KB'], 'minions': rec['minions'], 'V3': k3, 'V3_check_rel': check(k3, card, arm, fmt, kind, mask),
                 'count': list(EN.counts(fmt, kind, p['KB'])), 'phi': EN.phi_of(fmt, kind, p['KB']),
                 'N': {'K0': k3['K0'], 'K1': float(np.mean([ks[x]['K1'] for x in ks])), 'K2': float(np.mean([ks[x]['K2'] for x in ks]))},
                 'N2': {'K0': k3['K0'], 'K1': float(np.mean([ks[x]['K1'] for x in ('ones', 'random')])),
                        'K2': float(np.mean([ks[x]['K2'] for x in ('ones', 'random')]))},
                 'V3phi1': kp, 'counted_kinds_K': ks,
                 'switches_label': {'counts_source': sw.get('counts_source'), 'counts_footing': sw.get('counts_footing')},
                 'V1': 'not computed: V1 is compared only at the pinned cards\' footings (no V1 test point on a governed card)'})
    assert rows[-1]['V3_check_rel'] < 1e-9
out = {'what': 'fix-unread-e212sw ADDENDUM 1 step A2: forecasts of E209\'s three real points (POST HOC), made before this lane opened any E209 measurement',
       'made_pst': ts(), 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
       'addendum_declaration_sha256': sha(AD_P), 'declaration_sha256': sha(DECL_P), 'frozen_forecasts_sha256': sha(FC_P),
       'params_sha256': sha(PP), 'counts_SHA256SUMS_sha256': sha(os.path.join(CNT, 'SHA256SUMS')), 'g': g3, 'xi': xi,
       'formula_V3_N_N2_V3phi1': FC['formula_V3_N_N2_V3phi1'], 'machinery_check': same, 'rows': rows}
pj = os.path.join(OUTD, 'forecasts-e209-posthoc.json')
json.dump(out, open(pj, 'w'), indent=1, sort_keys=True, default=float)
pc = os.path.join(OUTD, 'forecasts-e209-posthoc.csv')
cols = ['id', 'group', 'card', 'arm', 'fmt', 'kind', 'mask', 'KB', 'minions', 'S_signal_lo_per_op', 'valid_share', 'phi', 'V3_K0_W', 'V3_K1_Wus',
        'V3_K2_Wus', 'V3_T600_us', 'V3_T800_us', 'N_K1_Wus', 'N_K2_Wus', 'N2_K1_Wus', 'N2_K2_Wus', 'V3phi1_K2_Wus']
with open(pc, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    for r in rows:
        k = r['V3']
        d = {c: r.get(c) for c in ('id', 'group', 'card', 'arm', 'fmt', 'kind', 'mask', 'KB', 'minions', 'phi')}
        d.update({'S_signal_lo_per_op': r['count'][0], 'valid_share': r['count'][1], 'V3_K0_W': k['K0'], 'V3_K1_Wus': k['K1'], 'V3_K2_Wus': k['K2'],
                  'V3_T600_us': k['T600_us'], 'V3_T800_us': k['T800_us'], 'N_K1_Wus': r['N']['K1'], 'N_K2_Wus': r['N']['K2'],
                  'N2_K1_Wus': r['N2']['K1'], 'N2_K2_Wus': r['N2']['K2'], 'V3phi1_K2_Wus': r['V3phi1']['K2']})
        w.writerow({c: (round(v, 9) if isinstance(v, float) else v) for c, v in d.items()})
print('A2 written', out['made_pst'])
print(sha(pj), 'forecasts-e209-posthoc.json')
print(sha(pc), 'forecasts-e209-posthoc.csv')
for r in rows:
    k = r['V3']
    print(f"{r['group']} {r['id']} {r['fmt']} {r['arm']} S {r['count'][0]:.1f} phi {r['phi']:.4f} K0 {k['K0']:.4f} K1 {k['K1']:.5f} K2 {k['K2']:.5f} "
          f"T600 {k['T600_us']:.4f} T800 {k['T800_us']:.4f} | N K1 {r['N']['K1']:.5f} K2 {r['N']['K2']:.5f} | check {r['V3_check_rel']:.1e}")
