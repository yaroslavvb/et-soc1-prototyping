#!/usr/bin/env python3
"""unread-e212sw (Q218) step 2: THE FORECASTS, before any read of the test runs' power, energy or seconds.

MM1-v3's landed predictor (mm1_v3.Model, work copy of GitHub main 8e91dda6 = b1493082's folder, SHA256SUMS 170/170) with its frozen parameters
(out/mm1_v3_params.json, sha256 1fdc0749...), UNCHANGED: no refit, no constant, no line of its code changed. Added, as data only:
  - the frozen switch counts (work/counts = fix-v31counts' land dir, SHA256SUMS c74c2d49..., checked here first) as rows of the very tables
    energy_v3.counts() and mm1_v3.counts_full() read: fp32 kinds at GEMM states into energy_v3.E210C['S1'|'S2'], fp16 and int8 kinds into
    energy_v3.SWT (MM1-v1's switch-table row form); no existing row is touched (asserted);
  - phi for the new kinds by the declared rule (declared-unread.json e_phi, values from tile bytes) into energy_v3._PHI, the memo phi_of()
    reads first, for both KB classes;
  - group C (E212's gen-sparse50 arms) priced as the committed kind 'sparse50' (the declaration).
Every model's W over idle for a run is written in a form exact in the run's measured conditions, so the read in step 3 only evaluates it:
    W(t, f, V, T0) = [ K0 + g G(f) + (1e6 / t) ( sV K1 + (1 + xi (sV - 1)) K2 ) ] x (1 + 0.0048 (T0 - 50))      (MM1-v3, V3, N, N2, V3phi1)
    t the op time in us, f the clock (MHz), sV = (V / 0.517 V)^2, G(f) = mm1_core_v3.G_of_f(card, f), T0 the die at start (C)
    MM1-v1 (V1): W = A0 + g1 G(f) + sV B1 / t (no die term), A0, B1 from its predictor at G = 0
K0, K1, K2 come from the predictor's own W_affine (A, B) at sV = 1 and sV = 4 (V = 0.517 and 1.034 V), G = 0, die 50 C; checked against
energy_v3.terms_v3 (the class split) and against the predictor at a test condition (f 812.5 MHz, V 0.604 V, T0 57 C, t 1.37 us).
N = the mean over zeros, ones and random of the run's format of MM1-v3's own K1, K2 (W is linear in them); N2 over ones and random.
The forecast op time (for the REPORTED J with seconds forecast) is the predictor's T at 600 and 800 MHz here; step 3 calls the same frozen
predictor at the run's measured clock.
Desk; no device; no measurement file opened (this script imports no data loader). Run: /usr/bin/python3 -I -B s02_forecast.py <lane dir>
"""
import csv
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
V3 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3')
V1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v1')
CNT = os.path.join(L, 'work', 'counts')
LANDCNT = '<W>/out/fix-v31counts/land/tools/matmul/mm1/v3.1/counts'
OUTD = os.path.join(L, 'work', 'step2')
os.makedirs(OUTD, exist_ok=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S PST', time.localtime())


# ---------------------------------------------------------------- the counts, checked first (both copies)
chk = {}
for tag, d in (('land dir', LANDCNT), ('work copy', CNT)):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    lines = [x for x in r.stdout.splitlines() if x.strip()]
    chk[tag] = {'rc': r.returncode, 'ok': sum(1 for x in lines if x.endswith(': OK')), 'not_ok': sum(1 for x in lines if not x.endswith(': OK')),
                'SHA256SUMS_sha256': sha(os.path.join(d, 'SHA256SUMS')), 'time': ts()}
    print('sha256sum -c SHA256SUMS', tag, json.dumps(chk[tag]))
    assert r.returncode == 0 and chk[tag]['not_ok'] == 0
    assert chk[tag]['SHA256SUMS_sha256'] == 'c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f'
PP = os.path.join(V3, 'out', 'mm1_v3_params.json')
assert sha(PP) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=V3, capture_output=True, text=True)
assert r.returncode == 0, 'MM1-v3 SHA256SUMS'
v3sums = sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))

sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import mm1_core_v3 as C  # noqa: E402
import mm1_v3  # noqa: E402

DECL = json.load(open(os.path.join(L, 'declared-unread.json')))
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
PHI = DECL['e_phi']['values']

# ---------------------------------------------------------------- add the rows (data only), asserting nothing existing is touched
added = []
for S in ('S1', 'S2'):
    for kind, row in C32[S].items():
        assert kind not in EN.E210C[S], (S, kind)
        EN.E210C[S][kind] = row
        added.append(f'E210C[{S}][{kind}]')
for key, row in C16.items():
    assert key not in EN.SWT, key
    EN.SWT[key] = row
    added.append(f'SWT[{key}]')
phi_added = []
for k, v in PHI.items():
    fmt, kind = k.split('|', 1)
    if kind.startswith('pattern:sparse50'):
        continue     # group C is priced as 'sparse50' (MM1-v3's own phi_of)
    for kb1 in (True, False):
        key = (fmt, kind, kb1)
        assert EN._PHI.get(key) is None, key
        EN._PHI[key] = float(v)
        phi_added.append(f'{fmt}|{kind}|KB==1:{kb1}')

params = json.load(open(PP))
M3 = mm1_v3.Model(params)
g3 = params['energy']['theta']['g']
xi = params['energy']['theta']['xi']
sys.path.insert(1, V1)
import blind_day_v1 as BD1  # noqa: E402
import kinds_v1 as K1  # noqa: E402
import mm1_v1  # noqa: E402

P1 = json.load(open(os.path.join(V1, 'out', 'mm1_v1_params.json')))
M1 = mm1_v1.Model(P1)
V_FOOT = {'aifoundry1 card 1': 0.517, 'aifoundry3 card 0': 0.522}


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


def v1_spec(x):
    """MM1-v1's own kind specs where its kind term applies: (e_res_spec, phi_spec) or None"""
    if x['exp'] == 'E207':
        es, ps, _ = BD1.kind_specs({'fmt': x['fmt'], 'kind': x['kind'], 'arm': x['arm']})
        return es, ps
    if x['exp'] == 'E206' and x['kind'] == 'real':
        return K1.e206_kind(x['fmt'], 'real')
    return None


def v1_decompose(card, arm, fmt, kind, mask, spec):
    V = V_FOOT.get(card)
    if card not in mm1_v1.CARD_KEY:
        return None, 'NOT FORECAST: MM1-v1 has no constants for this card'
    if V is None:
        return None, 'not computed: V1 is compared only at the pinned cards\' footings (no V1 test point on a governed card)'
    if spec is None and kind not in ('random', 'zeros'):
        return None, 'NOT FORECAST: no e_res source in MM1-v1 for this kind (no ledger row or frozen per-tile prediction)'
    es, ps = spec if spec else (None, None)
    o = M1.predict(card, arm, fmt, kind, mask, 600.0, V=0.517, G=0.0, e_res_spec=es, phi_spec=ps)
    if 'W_affine' not in o:
        return None, o.get('energy', 'NOT FORECAST')
    return {'A0': o['W_affine']['A_W'], 'B1': o['W_affine']['B_W_us'], 'e_res_source': o.get('e_res_source'), 'phi': o.get('phi'),
            'g1': P1['energy']['theta']['g'], 'T600_us': o['T_op_us']}, None


def entry(kind_role, x, card, arm, fmt, kind, priced, mask, group):
    pre, b = E.arm_parts(arm)
    KB = b[2]
    k3, rec = decompose(card, arm, fmt, priced, mask)
    row = {'id': x['id'], 'role': kind_role, 'group': group, 'card': card, 'arm': arm, 'fmt': fmt, 'kind': kind, 'priced_as': priced, 'mask': mask,
           'KB': KB, 'minions': rec['minions'], 'ops_per_minion_per_gemm': rec['ops_per_minion_per_gemm']}
    if k3 is None:
        row['V3'] = rec.get('energy')
        return row
    row['V3'] = k3
    row['V3_check_rel'] = check(k3, card, arm, fmt, priced, mask)
    row['count'] = EN.counts(fmt, priced, KB)
    row['phi'] = EN.phi_of(fmt, priced, KB)
    if kind_role == 'test':
        ks = {}
        for kk in ('zeros', 'ones', 'random'):
            ks[kk], _ = decompose(card, arm, fmt, kk, mask)
        row['N'] = {'K0': k3['K0'], 'K1': float(np.mean([ks[k]['K1'] for k in ks])), 'K2': float(np.mean([ks[k]['K2'] for k in ks]))}
        row['N2'] = {'K0': k3['K0'], 'K1': float(np.mean([ks[k]['K1'] for k in ('ones', 'random')])),
                     'K2': float(np.mean([ks[k]['K2'] for k in ('ones', 'random')]))}
        row['counted_kinds_K'] = ks
        # V3 with phi = 1 for the new kind (rule e's weight): same predictor, the memo set to 1 for this kind only
        if priced not in ('sparse50',):
            old = {kb: EN._PHI[(fmt, priced, kb)] for kb in (True, False)}
            for kb in (True, False):
                EN._PHI[(fmt, priced, kb)] = 1.0
            kp, _ = decompose(card, arm, fmt, priced, mask)
            for kb in (True, False):
                EN._PHI[(fmt, priced, kb)] = old[kb]
            row['V3phi1'] = kp
        sw = rec.get('switches') or {}
        row['switches_label'] = {'counts_source': sw.get('counts_source'), 'counts_footing': sw.get('counts_footing')}
        if 'counted_signal_fin_edges' in sw:
            row['counted_signal_fin_edges_lo_per_gemm'] = sw['counted_signal_fin_edges']['lo_zero_delay']
    v1, why = v1_decompose(card, arm, fmt, priced, mask, x.get('_v1spec'))
    row['V1'] = v1 if v1 else why
    return row


rows = []
A = DECL['a_runs']
for grp, key in (('A', 'group_A_pass_rule_pool'), ('C', 'group_C_reported_sparse50')):
    for r in A[key]['e212_runs']:
        rows.append(entry('test', r, r['card'], r['arm'], r['fmt'], r['kind'], r['priced_as'], r['mask'], grp))
        for kk, ids in r['refs'].items():
            for rid in ids:
                rr = {'id': f"E212|{r['session']}|{rid}"}
                if any(q['id'] == rr['id'] for q in rows):
                    continue
                rows.append(entry('ref', rr, r['card'], r['arm'], r['fmt'], kk, kk, r['mask'], 'ref'))
for grp, key, sub in (('A', 'group_A_pass_rule_pool', 'e206_e207_points'), ('B', 'group_B_reported_phi_only', 'e206_points')):
    for x in A[key][sub]:
        x = dict(x)
        x['_v1spec'] = v1_spec(x)
        rows.append(entry('test', x, x['card'], x['arm'], x['fmt'], x['kind'], x['priced_as'], x['mask'], grp))
        pref = x['id'].split('|')[0]
        for kk, ids in x['refs'].items():
            for pid in ids:
                rr = {'id': f'{pref}|{pid}'}
                if any(q['id'] == rr['id'] for q in rows):
                    continue
                rows.append(entry('ref', rr, x['card'], x['arm'], x['fmt'], kk, kk, x['mask'], 'ref'))
# ---------------------------------------------------------------- summary and files
nf = [r['id'] for r in rows if not isinstance(r['V3'], dict)]
maxchk = max(r.get('V3_check_rel', 0.0) for r in rows)
assert not nf, ('NOT FORECAST', nf)
assert maxchk < 1e-9, maxchk
out = {'what': 'unread-e212sw step 2: the forecasts (MM1-v3 unchanged + the frozen counts as table rows + the declared phi), made before any read',
       'made_pst': ts(), 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
       'formula_V3_N_N2_V3phi1': ('W(t, f, V, T0) = [K0 + g G(f) + (1e6/t)(sV K1 + (1 + xi (sV - 1)) K2)] x (1 + 0.0048 (T0 - 50)); '
                                  't us an op, f MHz, sV = (V/0.517)^2, G(f) = mm1_core_v3.G_of_f(card, f), T0 C'),
       'formula_V1': 'W = A0 + g1 G(f) + sV B1 / t (MM1-v1, no die term); applies only where V1 is a dict',
       'g': g3, 'xi': xi, 'counts_check': chk, 'mm1_v3_sha256sums_ok': v3sums, 'params_sha256': sha(PP),
       'rows_added': added, 'phi_added': phi_added, 'declaration_sha256': sha(os.path.join(L, 'declared-unread.json')),
       'max_rel_formula_vs_predictor_at_test_condition': maxchk, 'n_rows': len(rows),
       'n_test': sum(1 for r in rows if r['role'] == 'test'), 'n_ref': sum(1 for r in rows if r['role'] == 'ref'),
       'rows': rows}
for r in rows:
    r.pop('_v1spec', None)
json.dump(out, open(os.path.join(L, 'forecasts-unread.json'), 'w'), indent=1, sort_keys=True, default=float)
cols = ['id', 'role', 'group', 'card', 'arm', 'fmt', 'kind', 'priced_as', 'mask', 'KB', 'minions', 'S_signal_lo_per_op', 'valid_share', 'phi',
        'V3_K0_W', 'V3_K1_Wus', 'V3_K2_Wus', 'V3_T600_us', 'V3_T800_us', 'N_K1_Wus', 'N_K2_Wus', 'N2_K1_Wus', 'N2_K2_Wus', 'V3phi1_K2_Wus',
        'V1_A0_W', 'V1_B1_Wus', 'W_V3_at_T600_footing_50C', 'W_N_at_T600_footing_50C']
with open(os.path.join(L, 'forecasts-unread.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    wr.writeheader()
    for r in rows:
        k = r['V3']
        Vf = V_FOOT.get(r['card'], float(C.volts(r['card'], 600.0)))
        d = {c: r.get(c) for c in ('id', 'role', 'group', 'card', 'arm', 'fmt', 'kind', 'priced_as', 'mask', 'KB', 'minions')}
        d.update({'S_signal_lo_per_op': (r['count'][0] if r.get('count') else None), 'valid_share': (r['count'][1] if r.get('count') else None),
                  'phi': r.get('phi'), 'V3_K0_W': k['K0'], 'V3_K1_Wus': k['K1'], 'V3_K2_Wus': k['K2'], 'V3_T600_us': k['T600_us'],
                  'V3_T800_us': k['T800_us'],
                  'W_V3_at_T600_footing_50C': W_formula(k, r['card'], k['T600_us'], 600.0, Vf, 50.0)})
        if 'N' in r:
            d.update({'N_K1_Wus': r['N']['K1'], 'N_K2_Wus': r['N']['K2'], 'N2_K1_Wus': r['N2']['K1'], 'N2_K2_Wus': r['N2']['K2'],
                      'W_N_at_T600_footing_50C': W_formula(r['N'], r['card'], k['T600_us'], 600.0, Vf, 50.0)})
        if isinstance(r.get('V3phi1'), dict):
            d['V3phi1_K2_Wus'] = r['V3phi1']['K2']
        if isinstance(r.get('V1'), dict):
            d.update({'V1_A0_W': r['V1']['A0'], 'V1_B1_Wus': r['V1']['B1']})
        wr.writerow({c: (round(v, 9) if isinstance(v, float) else v) for c, v in d.items()})
print('rows', len(rows), 'test', out['n_test'], 'ref', out['n_ref'], '; max |formula/predictor - 1| at the test condition', maxchk)
print('V1 applies on:', [r['id'] for r in rows if r['role'] == 'test' and isinstance(r.get('V1'), dict)])
for r in rows:
    if r['role'] == 'test':
        k = r['V3']
        print(f"{r['group']} {r['id']:44s} {r['fmt']} {r['priced_as']:34s} S {r['count'][0]:12.1f} phi {r['phi']:.3f} K0 {k['K0']:7.3f} "
              f"K1 {k['K1']:9.4f} K2 {k['K2']:8.4f} | N K1 {r['N']['K1']:9.4f} K2 {r['N']['K2']:8.4f}")
