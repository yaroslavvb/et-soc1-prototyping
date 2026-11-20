#!/usr/bin/env python3
"""blind-e217 (Q228) step 2b: THE FORECASTS of one frozen model at each listed run's MEASURED conditions (decl-e217's declaration, section
'The forecast procedure', footing_1_measured), before any E217 measurement is read. The only E217 inputs are work/step2/conditions-e217.json
(the primary view's kclock_mhz, rails.minion.mV and the run's die_start_c) and decl-e217's work/step1/runs-listed.json (the registered arms).
THE CONDITIONS (declared): f = the primary view's kclock_mhz; V: card 1 the models' footing 0.517 V, card 0 the primary view's
rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f) (inside the predictor);
t0_c = the run's die_start_c (the predictor's own 50 C when absent). MM1-v2 through MM1-v3's unread_v2_e212.call (card 1 V None = the 0.517 V
footing, card 0 the measured volts; energy for random, zeros and ones only; no die term).
THE PREDICTORS ARE CALLED UNCHANGED; added in memory, as data only (the declaration, section e; decl-e217's s04c_nominal_counts.py form):
MM1-v3.1: counts-e217's rows in energy_v31's E210C31 / SWT31; MM1-v3: 3e8991d0's and counts-e217's rows in energy_v3's E210C / SWT (no key
colliding: asserted); phi of the 21 new kinds (the declaration's table) in each model's memo; THE DECLARED GATE for the four zero-row tiles
(gt125, gt25, gt875, h_gt25: (g_op, g_lane, g8) = (the all-zero A-row share, 0, 0)) by wrapping gate_shares; sparse50f/h/i priced as the
committed sparse50 kind (runs-listed's kind_energy). REPORTED beside, for the four zero-row tiles: the frozen literal gate (0, 0, 0) and the
count-implied gate (decl-e217's s04c 'count gate'). For group S runs also the null kinds' (zeros, ones, random) A and B at the same conditions
(MM1-v3.1 and MM1-v3): the null N of the switch test.
Mode lay: the layout factors (configuration-only; no model call): F1 (#1.29.1) T x clip(1 + a Phi_fresh, 0.3, 3), a = -0.08316593007433395,
Phi_fresh by the term's eval_layout.phi_of over the term's frozen walk cache + decl-e217's walk-feats-e217.json; verify-lay's controls by
v02_fits.py's forms and all-data constants (1 + sum a_i x_i, unclipped; the layout-blind F1 averaged over E217's listed configurations of the
same (n, arm)); each factor asserted EQUAL to the factor frozen in decl-e217's nominal forecasts (forecasts-nominal-e217.json).
Mode --nominal (a self-check, never scored): the same code at the declared nominal conditions, to be compared with the frozen nominal forecasts.
One model per process (energy_v31 imports energy_v3: one model's in-memory tables never reach the other's). Desk; numpy single-threaded.
Run: /usr/bin/python3 -I -B s02b_forecast.py <lane dir> <v31|v3|v2|lay> [--nominal]
"""
import collections
import hashlib
import json
import math
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
NOMINAL = '--nominal' in sys.argv[3:]
assert MODE in ('v31', 'v3', 'v2', 'lay'), MODE
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
DEC = os.path.join(L, 'work', 'decl')
OUTD = os.path.join(L, 'work', 'step2')
FULL = 0xFFFFFFFF


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


PINS = {os.path.join(DEC, 'DECLARED-blind-e217.json'): '633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7',
        os.path.join(DEC, 'DECLARED-blind-e217.md'): '099806dc1a5cb6c53ed7ea0645d5e2b3ae55e0d7734872a467019222da324405',
        os.path.join(DEC, 'forecasts-nominal-e217.json'): '611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c',
        os.path.join(DEC, 'counts-e217', 'counts-fp32-gemm-states.json'): '0169d260348ae8b0ae8a540f1c702ff2e931577215d5d60ba887447cc13893c2',
        os.path.join(DEC, 'counts-e217', 'counts-fp16-int8-launch.json'): '6509e20d4fe21c942fdb89d7feaa0479e3b7efac847a0561405dfae9cd65f1f0',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '25154e5dedd47519a145c693273e3ac3f3cbcabc4e82581a30ebaef34d0d4bc1',
        os.path.join(DEC, 'inputs', 'step2', 'walk-feats-e217.json'): '6c65696dfe40bbdc69097ea5f4b05b980ee09d270f69dfdae029b102fac2bba0',
        os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'): 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3',
        os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'): '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db',
        os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json'): '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5',
        os.path.join(MM1, 'v3.1', 'counts', 'SHA256SUMS'): 'c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f',
        os.path.join(MM1, 'v3.2-terms', 'layout', 'forecast-e215-v31-layout.json'): 'f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259',
        os.path.join(MM1, 'v3.2-terms', 'layout', 'eval_layout.py'): 'f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1',
        os.path.join(MM1, 'v3.2-terms', 'layout', 'features_layout.py'): 'b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3',
        os.path.join(MM1, 'v3.2-terms', 'layout', 'out', 'features_layout.json'): '1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.json'): '1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'): '4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8'}
for p, h in PINS.items():
    assert sha(p) == h, p
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e217.json')))
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e217.json')))
NOM = FCN['meta']['nominal_conditions']
PHI = DECL['e_switch']['phi']
GATE = DECL['e_switch']['gate_values']
NEWK = set(RL['counts']['new_kinds'])
NULLK = ('zeros', 'ones', 'random')
R = RL['runs']
rec = {'model': MODE, 'nominal_selfcheck': NOMINAL, 'python': sys.version.split()[0], 'pins_checked': len(PINS)}
if not NOMINAL:
    COND = json.load(open(os.path.join(OUTD, 'conditions-e217.json')))['runs']
    rec['conditions_sha256'] = sha(os.path.join(OUTD, 'conditions-e217.json'))
else:
    COND = None


def cond(r):
    """the run's conditions: (f, V for v3/v3.1, V_mv for MM1-v2, t0_c)"""
    if NOMINAL:
        n = NOM[r['card']]
        return n['f'], n['V'], None, n['t0_c']
    c = COND[r['id']]
    f = float(c['kclock_mhz'])
    if r['card'] == 'aifoundry1 card 1':
        V = 0.517
    else:
        V = (float(c['minion_mV']) / 1000.0) if c.get('minion_mV') else None
    return f, V, c.get('minion_mV'), c.get('die_start_c')


def spec(r, kind):
    f, V, _, t0 = cond(r)
    return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': kind, 'mask': r['mask'], 'f': f, 'kernel': 'rgm136', 'V': V, 't0_c': t0}


# ---------------------------------------------------------------- mode lay: the layout factors (configuration-only)
if MODE == 'lay':
    import numpy as np  # noqa: E402
    LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
    sys.path.insert(0, LAY)
    import eval_layout as EL  # noqa: E402
    meta = json.load(open(os.path.join(LAY, 'forecast-e215-v31-layout.json')))['meta']
    A_FRESH = float(meta['a_fresh'])
    assert A_FRESH == -0.08316593007433395, A_FRESH
    VL = json.load(open(os.path.join(L, 'work', 'verify-lay', 'v02_fits.json')))
    CTRL = {'N1+N2': (['N1', 'N2'], VL['forms']['N1+N2']['a_all']), 'G1': (['G1'], VL['forms']['G1']['a_all']),
            'G1+N1': (['G1', 'N1'], VL['forms']['G1+N1']['a_all']), 'F1-layout-blind': (['fresh32_bar_narm'], VL['forms']['fresh32_bar_narm']['a_all'])}
    for nm, (cs, a) in CTRL.items():
        assert FCN['meta']['controls_constants'][nm]['a_all'] == a, nm
    WALK = json.load(open(os.path.join(DEC, 'inputs', 'step2', 'walk-feats-e217.json')))
    FEATS = dict(EL.FEATS)
    for k, v in WALK['computed'].items():
        assert k not in FEATS, k
        FEATS[k] = v
    EL.FEATS.update(WALK['computed'])

    def key_of(arm, m):
        MB, NB, KB = (int(x) for x in EL.SHAPE.match(arm).groups())
        return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)

    def feat_row(arm, m, fresh_bar=None):
        if m == FULL:
            return {c: 0.0 for c in ('fresh32', 'G1', 'N1', 'N2', 'N3', 'fresh32_bar_narm')}
        f, g = FEATS[key_of(arm, m)], FEATS[key_of(arm, FULL)]
        n = f['n']
        fresh = f['fresh_lines_step'] / f['lines_req_step'] - g['fresh_lines_step'] / g['lines_req_step']
        return {'fresh32': fresh, 'G1': (110 + 12 * f['mesh_hop_mean']) / (110 + 12 * g['mesh_hop_mean']) - 1, 'N1': 1 - n / 32.0,
                'N2': (1 - n / 32.0) ** 2, 'N3': 32.0 / n - 1, 'fresh32_bar_narm': fresh if fresh_bar is None else fresh_bar}
    CASES = RL['cases']
    confs = sorted({(c['arm'], c['mask']) for c in CASES if c['mask'] != '0xffffffff'})
    grp = collections.defaultdict(list)
    for arm, mk in confs:
        m = int(mk, 16)
        grp[(bin(m).count('1'), arm)].append(feat_row(arm, m)['fresh32'])
    BAR = {k: float(np.mean(v)) for k, v in grp.items()}
    out = {}
    neq = 0
    for c in CASES:
        m = int(c['mask'], 16)
        ph, key = EL.phi_of('rgm136 gemmL', c['arm'], c['mask'])
        g = float(np.clip(1.0 + A_FRESH * ph[0], 0.3, 3.0))
        fb = BAR[(bin(m).count('1'), c['arm'])] if m != FULL else None
        fr = feat_row(c['arm'], m, fb)
        o = {'v3.1+contention': {'factor': g, 'phi_fresh': float(ph[0]), 'walk_key': key}}
        for nm, (cs, a) in CTRL.items():
            o['ctrl ' + nm] = {'factor': 1.0 + sum(ai * fr[cc] for ai, cc in zip(a, cs)), 'features': {cc: fr[cc] for cc in cs}}
        frz = FCN['cases'][c['case']]
        for nm, x in o.items():
            if x['factor'] != frz[nm]['factor']:
                neq += 1
        assert frz['v3.1+contention']['phi_fresh'] == o['v3.1+contention']['phi_fresh'], c['case']
        out[c['case']] = o
    assert neq == 0, neq
    rec.update({'a_fresh': A_FRESH, 'controls_constants': {nm: {'features': cs, 'a_all': a} for nm, (cs, a) in CTRL.items()},
                'factors_equal_to_frozen_nominal': f'{5 * len(out)} of {5 * len(out)}', 'cases': out,
                'factor_ranges_subset_only': {nm: [min(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff')),
                                                   max(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff'))]
                                              for nm in next(iter(out.values()))}})
    fn = os.path.join(OUTD, 'fc-lay.json')
    json.dump(rec, open(fn, 'w'), indent=1, sort_keys=True)
    print('lay: cases', len(out), 'factors equal to the frozen nominal', rec['factors_equal_to_frozen_nominal'])
    print('factor ranges (subset masks)', json.dumps(rec['factor_ranges_subset_only']))
    print(sha(fn), os.path.relpath(fn, L))
    sys.exit(0)

# ---------------------------------------------------------------- the three predictors
C32n = json.load(open(os.path.join(DEC, 'counts-e217', 'counts-fp32-gemm-states.json')))['shapes']
C16n = json.load(open(os.path.join(DEC, 'counts-e217', 'counts-fp16-int8-launch.json')))['rows']
added = []


def gate_wrap(EN):
    orig = EN.gate_shares

    def g(fmt, kind, v):
        k = f'{fmt}|{kind}'
        if k in GATE:
            return float(GATE[k]['g_op']), 0.0, 0.0
        return orig(fmt, kind, v)
    return orig, g


def gate_wrap_count(EN, orig):
    def g(fmt, kind, v):
        k = f'{fmt}|{kind}'
        if k in GATE:
            r = float(GATE[k]['g_op'])
            return r, max(0.0, (1.0 - float(v)) - r), 0.0
        return orig(fmt, kind, v)
    return g


if MODE == 'v31':
    V31 = os.path.join(MM1, 'v3.1')
    rc, nok = sumscheck(V31)
    assert rc == 0
    rec['sha256sum_c'] = nok
    sys.path.insert(0, V31)
    import energy_v31 as EV  # noqa: E402
    import mm1_v31  # noqa: E402
    EN = EV.EN
    for sh in ('S1', 'S2'):
        for k, r in C32n[sh].items():
            assert k not in EV.E210C31[sh], (sh, k)
            EV.E210C31[sh][k] = r
            added.append(f'E210C31[{sh}][{k}]')
    for k, r in C16n.items():
        assert k not in EV.SWT31, k
        EV.SWT31[k] = r
        added.append(f'SWT31[{k}]')
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            assert (fmt, kind, kb1) not in EV._PHI31
            EV._PHI31[(fmt, kind, kb1)] = (float(v['phi']), "kinds_v3.phi over E217's registered tile file (decl-e217's declaration)")
    M = mm1_v31.Model(json.load(open(os.path.join(V31, 'out', 'mm1_v31_params.json'))))

    def run_many(specs):
        return M.predict_many(specs)
elif MODE == 'v3':
    V3 = os.path.join(MM1, 'v3')
    rc, nok = sumscheck(V3)
    assert rc == 0
    rec['sha256sum_c'] = nok
    sys.path.insert(0, V3)
    import energy_v3 as EN  # noqa: E402
    import mm1_v3  # noqa: E402
    V31C = os.path.join(MM1, 'v3.1', 'counts')
    C32o = json.load(open(os.path.join(V31C, 'counts-fp32-gemm-states.json')))['shapes']
    C16o = json.load(open(os.path.join(V31C, 'counts-fp16-int8-launch.json')))['rows']
    for tag, (A32, A16) in (('3e8991d0', (C32o, C16o)), ('counts-e217', (C32n, C16n))):
        for sh in ('S1', 'S2'):
            for k, r in A32[sh].items():
                assert k not in EN.E210C[sh], (sh, k)
                EN.E210C[sh][k] = r
                added.append(f'{tag} E210C[{sh}][{k}]')
        for k, r in A16.items():
            assert k not in EN.SWT, k
            EN.SWT[k] = r
            added.append(f'{tag} SWT[{k}]')
    for key, v in PHI.items():
        fmt, kind = key.split('|', 1)
        for kb1 in (True, False):
            assert EN._PHI.get((fmt, kind, kb1)) is None
            EN._PHI[(fmt, kind, kb1)] = float(v['phi'])
    M = mm1_v3.Model(json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json'))))

    def run_many(specs):
        return [M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']) for s in specs]
else:
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import unread_v2_e212 as U2  # noqa: E402
    M2, nsum = U2.v2_model()
    rec['sha256sum_c'] = nsum
    EN = None

    def run_many(specs):
        out = []
        for s in specs:
            r = s['_run']
            f, _, Vmv, _ = cond(r)
            out.append(U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': f, 'V_mv': Vmv}))
        return out
rec['rows_added_in_memory'] = added


def pack(p, energy_ok=True):
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean'], 'f_mhz': p.get('f_mhz'),
         'minions': p.get('minions'), 'ops_per_minion_per_gemm': p.get('ops_per_minion_per_gemm'), 'model_sec_gemm': p.get('seconds_per_gemm')}
    if energy_ok and isinstance(p.get('W_affine'), dict):
        o.update({'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'], 'energy': 'FORECAST',
                  'V': p.get('V'), 's_V': p.get('s_V'), 'G_W': p.get('G_W'), 'die_start_c_used': p.get('die_start_c')})
    else:
        o['energy'] = p.get('energy') if isinstance(p.get('energy'), str) else 'NOT FORECAST'
    return o


def specs_for(rs, kind_of):
    out = []
    for r in rs:
        s = spec(r, kind_of(r))
        s['_run'] = r
        out.append(s)
    return out


def strip(s):
    return {k: v for k, v in s.items() if k != '_run'}


rows = {}
if EN is not None:
    orig, wrapped = gate_wrap(EN)
    EN.gate_shares = wrapped
main_specs = specs_for(R, lambda r: r['kind_energy'])
P = run_many([strip(s) for s in main_specs] if MODE != 'v2' else main_specs)
for r, s, p in zip(R, main_specs, P):
    ok = not (MODE == 'v2' and r['kind_energy'] not in NULLK)
    o = pack(p, ok)
    if MODE == 'v2' and not ok:
        o['energy'] = "NOT FORECAST: MM1-v2 prices random, zeros and ones only (unread_v2_e212.call's form)"
    ops = 64 * r['MB'] * r['NB'] * r['KB']
    o['sec_gemm'] = ops * p['T_op_us'] * 1e-6
    f, V, Vmv, t0 = cond(r)
    o['inputs'] = {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'mask': r['mask'], 'f': f,
                   'V': (V if MODE != 'v2' else None), 'V_mv': (Vmv if MODE == 'v2' else None), 't0_c': (t0 if MODE != 'v2' else None)}
    rows[r['id']] = o
if MODE in ('v31', 'v3'):
    sS = [r for r in R if r['kind'] in NEWK]
    for k in NULLK:
        Pk = run_many([strip(s) for s in specs_for(sS, lambda r, k=k: k)])
        for r, p in zip(sS, Pk):
            rows[r['id']][f'null_{k}'] = {'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'], 'T_op_us': p['T_op_us']}
    zr = [r for r in R if f"{r['fmt']}|{r['kind']}" in GATE]
    EN.gate_shares = orig
    for r, p in zip(zr, run_many([strip(s) for s in specs_for(zr, lambda r: r['kind_energy'])])):
        rows[r['id']]['gate_literal_REPORTED'] = {'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle']}
    EN.gate_shares = gate_wrap_count(EN, orig)
    for r, p in zip(zr, run_many([strip(s) for s in specs_for(zr, lambda r: r['kind_energy'])])):
        rows[r['id']]['gate_count_REPORTED'] = {'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle']}
    EN.gate_shares = wrapped
    rec['zero_row_gate_effect'] = {r['id']: {'W_fc_declared_gate': rows[r['id']]['W_fc'], 'W_fc_literal': rows[r['id']]['gate_literal_REPORTED']['W_fc'],
                                             'W_fc_count_gate': rows[r['id']]['gate_count_REPORTED']['W_fc']} for r in zr}
rec['n_runs'] = len(rows)
rec['n_energy_forecast'] = sum(1 for v in rows.values() if v['energy'] == 'FORECAST')
rec['not_forecast_energy'] = {k: v['energy'] for k, v in rows.items() if v['energy'] != 'FORECAST'}
rec['rows'] = rows
bad = [k for k, v in rows.items() if not all(isinstance(v[x], float) and math.isfinite(v[x]) for x in ('T_op_us', 'cyc_wall', 'cyc_mean'))]
assert not bad, bad[:5]
badsec = [k for k, v in rows.items() if v['model_sec_gemm'] is not None and abs(v['model_sec_gemm'] / v['sec_gemm'] - 1) > 1e-12]
rec['sec_gemm_equals_model_seconds_per_gemm'] = not badsec
fn = os.path.join(OUTD, f"fc-{MODE}{'-nominalcheck' if NOMINAL else ''}.json")
json.dump(rec, open(fn, 'w'), indent=1, sort_keys=True)
print(MODE, 'nominal self-check' if NOMINAL else 'measured conditions', 'runs', rec['n_runs'], 'energy forecast', rec['n_energy_forecast'],
      'not forecast', len(rec['not_forecast_energy']), 'sha256sum -c OK', rec.get('sha256sum_c'), 'rows added', len(added),
      'sec_gemm = model seconds', rec['sec_gemm_equals_model_seconds_per_gemm'])
if 'zero_row_gate_effect' in rec:
    print('zero-row gate (W_fc declared / literal / count), first 4:', json.dumps(dict(list(rec['zero_row_gate_effect'].items())[:4])))
print(sha(fn), os.path.relpath(fn, L))
