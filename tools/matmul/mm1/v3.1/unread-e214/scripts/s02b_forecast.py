#!/usr/bin/env python3
"""unread-e214 (Q225) step 2b: THE FORECASTS of one frozen model at each listed run's measured conditions (the declaration, section b),
before any E214 measurement is read: the only E214 inputs are work/step2/conditions-e214.json (clock, minion volts, die at start) and
work/step1/runs-listed.json (the registered arms). The frozen predictor is called UNCHANGED; added in memory, as data only (the declaration,
section e): the count rows (MM1-v3.1: counts-e214's; MM1-v3: 3e8991d0's and counts-e214's), phi for the 20 new kinds (memo), the sparse50
alias, and the sp_ar4 gate as arow50's (the frozen literal (0, 0, 0) forecast beside, REPORTED).
Per run: T_op_us, cycles an op (wall, counter mean), seconds a GEMM, and where the model prices the kind W_affine (A, B: W over idle at a
measured op time t is A + B / t) and W over idle at the model's own op time; for group S runs also the null kinds' (zeros, ones, random)
A and B at the same conditions (MM1-v3.1 and MM1-v3). Desk; numpy single-threaded.
Run: /usr/bin/python3 -I -B s02b_forecast.py <lane dir> <v31|v3|v2>
"""
import hashlib
import json
import math
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
MODEL = sys.argv[2]
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
CNT = os.path.join(L, 'work', 'counts-e214')
S1 = os.path.join(L, 'work', 'step1')
OUTD = os.path.join(L, 'work', 'step2')
DECL = json.load(open(os.path.join(L, 'DECLARED-unread-e214.json')))
RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
COND = json.load(open(os.path.join(OUTD, 'conditions-e214.json')))['runs']
PHI = json.load(open(os.path.join(S1, 'models-step1.json')))['phi_new_kinds']
C32n = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16n = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
NEWK = sorted({r['kind'] for r in RL['runs'] if r['kind'].startswith('pattern:') and not r['kind'].startswith('pattern:sparse50')})
NULLK = ('zeros', 'ones', 'random')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


# the inputs as declared (sha256 against the declaration's table)
INP = DECL['inputs_sha256']
assert sha(os.path.join(CNT, 'SHA256SUMS')) == INP['counts-e214 SHA256SUMS (land dir and work copy, 49/49 OK; verify-counts-e214 HOLDS)']
assert sumscheck(CNT)[0] == 0
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json'):
    assert sha(os.path.join(S1, n)) == INP[f'work/step1/{n}'], n
rec = {'model': MODEL, 'python': sys.version.split()[0], 'conditions_sha256': sha(os.path.join(OUTD, 'conditions-e214.json'))}


def volts(r, c):
    if r['card'] == 'aifoundry1 card 1':
        return 0.517
    return (c['minion_mV'] / 1000.0) if c.get('minion_mV') else None


def gate_wrap(EN):
    orig = EN.gate_shares

    def g(fmt, kind, v):
        if fmt == 'fp32' and kind == 'pattern:sp_ar4':
            return orig(fmt, 'arow50', v)
        return orig(fmt, kind, v)
    return orig, g


rows = {}
if MODEL == 'v31':
    V31 = os.path.join(MM1, 'v3.1')
    assert sha(os.path.join(V31, 'out', 'mm1_v31_params.json')) == INP['MM1-v3.1 out/mm1_v31_params.json']
    rc, nok = sumscheck(V31)
    assert rc == 0
    rec['sha256sum_c'] = nok
    sys.path.insert(0, V31)
    import energy_v31 as EV  # noqa: E402
    import mm1_v31  # noqa: E402
    EN = EV.EN
    for sh in ('S1', 'S2'):
        for k, r in C32n[sh].items():
            assert k not in EV.E210C31[sh]
            EV.E210C31[sh][k] = r
    for k, r in C16n.items():
        assert k not in EV.SWT31
        EV.SWT31[k] = r
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            EV._PHI31[(fmt, kind, kb1)] = (float(v['phi']), "kinds_v3.phi over E214's registered tile file (unread-e214's declaration)")
    orig, wrapped = gate_wrap(EN)
    M = mm1_v31.Model(json.load(open(os.path.join(V31, 'out', 'mm1_v31_params.json'))))

    def spec(r, c, kind):
        return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': kind, 'mask': r['mask'], 'f': float(c['kclock_mhz']),
                'kernel': 'rgm136', 'V': volts(r, c), 't0_c': c['die_start_c']}

    def run_many(specs):
        return M.predict_many(specs)
elif MODEL == 'v3':
    V3 = os.path.join(MM1, 'v3')
    assert sha(os.path.join(V3, 'out', 'mm1_v3_params.json')) == INP['MM1-v3 out/mm1_v3_params.json']
    rc, nok = sumscheck(V3)
    assert rc == 0
    rec['sha256sum_c'] = nok
    sys.path.insert(0, V3)
    import energy_v3 as EN  # noqa: E402
    import mm1_v3  # noqa: E402
    V31C = os.path.join(MM1, 'v3.1', 'counts')
    C32o = json.load(open(os.path.join(V31C, 'counts-fp32-gemm-states.json')))['shapes']
    C16o = json.load(open(os.path.join(V31C, 'counts-fp16-int8-launch.json')))['rows']
    for A32, A16 in ((C32o, C16o), (C32n, C16n)):
        for sh in ('S1', 'S2'):
            for k, r in A32[sh].items():
                assert k not in EN.E210C[sh]
                EN.E210C[sh][k] = r
        for k, r in A16.items():
            assert k not in EN.SWT
            EN.SWT[k] = r
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            EN._PHI[(fmt, kind, kb1)] = float(v['phi'])
    orig, wrapped = gate_wrap(EN)
    M = mm1_v3.Model(json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json'))))

    def spec(r, c, kind):
        return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': kind, 'mask': r['mask'], 'f': float(c['kclock_mhz']),
                'kernel': 'rgm136', 'V': volts(r, c), 't0_c': c['die_start_c']}

    def run_many(specs):
        return [M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']) for s in specs]
else:
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import unread_v2_e212 as U2  # noqa: E402
    M2, nsum = U2.v2_model()
    rec['sha256sum_c'] = nsum
    assert sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')) == INP['MM1-v2 out/mm1_v2_params.json']
    orig = wrapped = None

    def spec(r, c, kind):
        return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': kind, 'mask': r['mask'], 'f': float(c['kclock_mhz']),
                'V_mv': c['minion_mV']}

    def run_many(specs):
        return [U2.call(M2, s) for s in specs]


def pack(p, energy_ok=True):
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean']}
    if energy_ok and isinstance(p.get('W_affine'), dict):
        o.update({'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'], 'energy': 'FORECAST'})
    else:
        o['energy'] = p.get('energy') if isinstance(p.get('energy'), str) else 'NOT FORECAST'
    return o


R = RL['runs']
if wrapped is not None:
    EN.gate_shares = wrapped
main_specs = [spec(r, COND[r['id']], r['kind_energy']) for r in R]
P = run_many(main_specs)
for r, s, p in zip(R, main_specs, P):
    ok = True
    if MODEL == 'v2' and r['kind_energy'] not in NULLK:
        ok = False
    o = pack(p, ok)
    if MODEL == 'v2' and not ok:
        o['energy'] = "NOT FORECAST: MM1-v2 prices random, zeros and ones only (unread_v2_e212.call's form)"
    ops = 64 * r['MB'] * r['NB'] * r['KB']
    o['sec_gemm'] = ops * p['T_op_us'] * 1e-6
    o['inputs'] = {k: s.get(k) for k in ('card', 'arm', 'fmt', 'kind', 'mask', 'f', 'V', 't0_c', 'V_mv') if k in s}
    rows[r['id']] = o
# the null kinds for group S (MM1-v3.1 and MM1-v3), and the sp_ar4 gate as the frozen literal (REPORTED)
if MODEL in ('v31', 'v3'):
    sS = [r for r in R if r['kind'] in NEWK]
    for k in NULLK:
        Pk = run_many([spec(r, COND[r['id']], k) for r in sS])
        for r, p in zip(sS, Pk):
            rows[r['id']][f'null_{k}'] = {'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'], 'T_op_us': p['T_op_us']}
    EN.gate_shares = orig
    sp = [r for r in R if r['kind'] == 'pattern:sp_ar4']
    Pn = run_many([spec(r, COND[r['id']], r['kind_energy']) for r in sp])
    for r, p in zip(sp, Pn):
        rows[r['id']]['gate_none_REPORTED'] = {'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle']}
    EN.gate_shares = wrapped
    # the gate check: the declared gate changes only the sp_ar4 runs (their W differs from the literal's), time unchanged
    rec['sp_ar4_gate_effect'] = {r['id']: {'W_fc_arow50_gate': rows[r['id']]['W_fc'], 'W_fc_literal_no_gate': rows[r['id']]['gate_none_REPORTED']['W_fc']} for r in sp}
rec['n_runs'] = len(rows)
rec['n_energy_forecast'] = sum(1 for v in rows.values() if v['energy'] == 'FORECAST')
rec['not_forecast_energy'] = {k: v['energy'] for k, v in rows.items() if v['energy'] != 'FORECAST'}
rec['rows'] = rows
bad = [k for k, v in rows.items() if not all(isinstance(v[x], float) and math.isfinite(v[x]) for x in ('T_op_us', 'cyc_wall', 'cyc_mean'))]
assert not bad, bad[:5]
json.dump(rec, open(os.path.join(OUTD, f'fc-{MODEL}.json'), 'w'), indent=1, sort_keys=True)
print(MODEL, 'runs', rec['n_runs'], 'energy forecast', rec['n_energy_forecast'], 'not forecast', len(rec['not_forecast_energy']),
      'sha256sum -c OK', rec.get('sha256sum_c'))
if 'sp_ar4_gate_effect' in rec:
    print('sp_ar4', json.dumps(rec['sp_ar4_gate_effect']))
print(sha(os.path.join(OUTD, f'fc-{MODEL}.json')), f'work/step2/fc-{MODEL}.json')
