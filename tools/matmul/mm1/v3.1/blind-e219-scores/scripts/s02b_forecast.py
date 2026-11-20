#!/usr/bin/env python3
"""blind-e219 (Q232) step 2b: THE FORECASTS of every declared model at each listed IN-DOMAIN run's MEASURED conditions (decl-e219's
declaration, 'The forecast procedure', footing_1_measured), before any E219 measurement is read. decl-e219's s02b_nominal.py in form and
in code (the same models, the same imports and call order, the same composed forms and checks), one run a spec in place of one case a spec.
The only E219 inputs are work/step2/conditions-e219.json (the primary view's kclock_mhz, rails.minion.mV and the run's die_start_c) and
decl-e219's inputs/step1/runs-listed.json (the registered arms and schedules).
THE CONDITIONS (declared): f = the primary view's kclock_mhz; V: card 1 the models' footing 0.517 V, card 0 the primary view's
rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f) (inside the predictor);
t0_c = the run's die_start_c (the predictor's own 50 C when absent). MM1-v2 through MM1-v3's unread_v2_e212.call (card 1 V None = the 0.517 V
footing (the call drops card 1's mV), card 0 the measured volts; energy for random, zeros and ones, E219's only kinds; no die term).
MODELS: MM1-v3.1 (predict_many), MM1-v3 (predict), MM1-v2 (unread_v2_e212.call), 'v3.1+contention' (F1: T x clip(1 + a Phi_fresh, 0.3, 3),
a = -0.08316593007433395 from the frozen forecast's meta, Phi_fresh by the term's eval_layout.phi_of: 0 at the full mask and off the walk's
loops; energy MM1-v3.1's affine at its own op time), 'v3.1+both' (reg-e216's composition, dW = 0 off gemmLnc) and verify-lay's controls
(#1.29.1.1: N1+N2, G1, G1+N1 and the layout-blind F1, 1 + sum a_i x_i unclipped; time MM1-v3.1's x the factor; energy MM1-v3.1's affine at
its own op time). The layout factors are configuration-only: asserted EQUAL to the factors frozen in decl-e219's nominal forecasts.
'v3.1 + gemmLnc term' is NOT APPLICABLE: E219 runs no gemmLnc arm. OUT-OF-DOMAIN runs: NOT FORECAST (no model is called on them).
SECONDS: a pass = the host's ops a minion a pass (the kit's grammar: 64 MB NB KB for gemmL, 64 B R for gemmc) x the op time; the models'
own seconds_per_gemm (gemmL only) is kept beside and must equal it.
CHECKS before any output (decl-e219's): the two terms' makers re-make their frozen E215 forecasts.
Mode --nominal (a self-check, never scored): the same code at decl-e219's declared NOMINAL conditions (card 1 600 MHz, 0.517 V, 60 C; card 0
800 MHz, the model's own volts, 55 C), every run of a case at the same conditions, to be compared with the frozen nominal forecasts.
Desk; numpy single-threaded. Run: /usr/bin/python3 -I -B s02b_forecast.py <lane dir> [--nominal]
"""
import collections
import csv
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
NOMINAL = '--nominal' in sys.argv[2:]
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
LNC = os.path.join(MM1, 'v3.2-terms', 'gemmlnc')
DEC = os.path.join(L, 'work', 'decl')
OUTD = os.path.join(L, 'work', 'step2')
FULL = 0xFFFFFFFF
A_FRESH_POSTED = -0.08316593007433395


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


PINS = {os.path.join(DEC, 'DECLARED-blind-e219.json'): '670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479',
        os.path.join(DEC, 'DECLARED-blind-e219.md'): 'd629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495',
        os.path.join(DEC, 'FROZEN.txt'): '73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e',
        os.path.join(DEC, 'forecasts-nominal-e219.json'): 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '0bd052dcbc277c9937c82b1c7dce04124e41deb1b57e21e4699271c8aa2d3376',
        os.path.join(DEC, 'inputs', 'step2', 'walk-feats-e219.json'): '9c13958d026c8a6f9e5fabfc34c580377dab9efa24ae8095b1dc47eb5e09020d',
        os.path.join(LAY, 'forecast-e215-v31-layout.csv'): '50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754',
        os.path.join(LAY, 'forecast-e215-v31-layout.json'): 'f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259',
        os.path.join(LAY, 'freeze_layout.py'): 'ca04faa37bb4f22cb8b8b293fcefbdc99b153a2e0f15b46857ace034f926b58c',
        os.path.join(LAY, 'eval_layout.py'): 'f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1',
        os.path.join(LAY, 'features_layout.py'): 'b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3',
        os.path.join(LAY, 'out', 'features_layout.json'): '1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183',
        os.path.join(LNC, 'term-gemmlnc.json'): '2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'): '4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.json'): '1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312',
        os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'): 'c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d',
        os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'): 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3',
        os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'): '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db',
        os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json'): '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'}
for p, h in PINS.items():
    assert sha(p) == h, p
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e219.json')))
assert 'MM1-v3.2' not in DECL['models']           # MM1-v3.2 was NOT_ON_MAIN at the declaration: not a declared model
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e219.json')))
NOM = FCN['meta']['nominal_conditions']
rec = {'what': 'blind-e219 step 2b: forecasts at the ' + ('declared NOMINAL conditions (self-check)' if NOMINAL else "runs' MEASURED conditions"),
       'nominal_selfcheck': NOMINAL, 'python': sys.version.split()[0], 'numpy': np.__version__, 'sha256sum_c': {}, 'pins_checked': len(PINS)}
for nm, d in (('MM1-v3.1', 'v3.1'), ('MM1-v3', 'v3'), ('MM1-v2', 'v2')):
    rc, nok = sumscheck(os.path.join(MM1, d))
    assert rc == 0, nm
    rec['sha256sum_c'][nm] = nok

# the imports and their order exactly as decl-e219's s02b_nominal.py
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import mm1_v31  # noqa: E402
P31 = json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')))
M31 = mm1_v31.Model(P31)
sys.path.insert(0, os.path.join(MM1, 'v3'))
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402
M3 = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
M2, n2 = U2.v2_model()
sys.path.insert(0, LAY)
import eval_layout as EL  # noqa: E402
import features_layout as FL  # noqa: E402,F401   (imported for its frozen functions' identity, as decl-e219 did)

meta = json.load(open(os.path.join(LAY, 'forecast-e215-v31-layout.json')))['meta']
A_FRESH = float(meta['a_fresh'])
assert A_FRESH == A_FRESH_POSTED, A_FRESH
VL = json.load(open(os.path.join(L, 'work', 'verify-lay', 'v02_fits.json')))
CTRL = {'N1+N2': (['N1', 'N2'], VL['forms']['N1+N2']['a_all']), 'G1': (['G1'], VL['forms']['G1']['a_all']),
        'G1+N1': (['G1', 'N1'], VL['forms']['G1+N1']['a_all']), 'F1-layout-blind': (['fresh32_bar_narm'], VL['forms']['fresh32_bar_narm']['a_all'])}
CTRL_N3 = (['N3'], VL['forms']['N3']['a_all'])
for nm, (cs, a) in CTRL.items():
    if nm in VL['e215_control_columns']['forms']:
        assert VL['e215_control_columns']['forms'][nm]['a_all'] == a, nm
    assert FCN['meta']['controls_constants'][nm]['a_all'] == a, nm
rec['controls_constants'] = {nm: {'features': cs, 'a_all': a} for nm, (cs, a) in CTRL.items()}
rec['a_fresh'] = A_FRESH
WALK = json.load(open(os.path.join(DEC, 'inputs', 'step2', 'walk-feats-e219.json')))
FEATS = dict(EL.FEATS)
for k, v in WALK['computed'].items():
    assert k not in FEATS, k
    FEATS[k] = v
EL.FEATS.update(WALK['computed'])   # nothing new here (all three configurations are in the frozen cache)


def key_of(arm, m):
    MB, NB, KB = (int(x) for x in EL.SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)


def feat_row(arm, m, fresh_bar=None):
    """v02_fits.py's feat_row (its E215 control columns) on the term's walk features: zeros at the full mask"""
    if m == FULL:
        return {c: 0.0 for c in ('fresh32', 'G1', 'N1', 'N2', 'N3', 'fresh32_bar_narm')}
    f, g = FEATS[key_of(arm, m)], FEATS[key_of(arm, FULL)]
    n = f['n']
    fresh = f['fresh_lines_step'] / f['lines_req_step'] - g['fresh_lines_step'] / g['lines_req_step']
    return {'fresh32': fresh, 'G1': (110 + 12 * f['mesh_hop_mean']) / (110 + 12 * g['mesh_hop_mean']) - 1, 'N1': 1 - n / 32.0,
            'N2': (1 - n / 32.0) ** 2, 'N3': 32.0 / n - 1, 'fresh32_bar_narm': fresh if fresh_bar is None else fresh_bar}


# ---------------------------------------------------------------- CHECK 1: F1 re-makes its frozen E215 forecasts (decl-e219's check)
chk = {'F1_e215': {'rows': 0, 'subset_rows': 0, 'worst_abs_factor_diff': 0.0, 'worst_rel_cycles_diff': 0.0},
       'controls_e215': {'rows': 0, 'worst_abs_diff_cycles': {}}}
for r in csv.DictReader(open(os.path.join(LAY, 'forecast-e215-v31-layout.csv'))):
    chk['F1_e215']['rows'] += 1
    m = int(r['mask'], 16)
    ph, key = EL.phi_of(r['loop'], r['arm'], r['mask'])
    g = float(np.clip(1.0 + A_FRESH * ph[0], 0.3, 3.0))
    if m != FULL:
        chk['F1_e215']['subset_rows'] += 1
    chk['F1_e215']['worst_abs_factor_diff'] = max(chk['F1_e215']['worst_abs_factor_diff'], abs(g - float(r['layout_factor'])))
    v31c = float(r['v31_cycles_per_op_wall']) * g
    chk['F1_e215']['worst_rel_cycles_diff'] = max(chk['F1_e215']['worst_rel_cycles_diff'], abs(v31c / float(r['v31c_cycles_per_op_wall']) - 1))
assert chk['F1_e215']['worst_abs_factor_diff'] < 1e-8 and chk['F1_e215']['worst_rel_cycles_diff'] < 1e-6, chk['F1_e215']
# ---------------------------------------------------------------- CHECK 2: the controls re-make v02_e215_controls.csv (N3, N1+N2, G1, G1+N1)
worst = collections.defaultdict(float)
for r in csv.DictReader(open(os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'))):
    m = int(r['mask'], 16)
    fr = feat_row(r['arm'], m)
    v31 = float(r['v31_cycles_per_op_wall'])
    chk['controls_e215']['rows'] += 1
    for nm, (cs, a) in list(CTRL.items())[:3] + [('N3', CTRL_N3)]:
        mine = v31 * (1.0 + sum(ai * fr[c] for ai, c in zip(a, cs)))
        worst[nm] = max(worst[nm], abs(mine - float(r['REPORTED_%s_cycles_per_op_wall' % nm])))
chk['controls_e215']['worst_abs_diff_cycles'] = dict(worst)
assert all(v < 0.12 for v in worst.values()), worst
assert chk == FCN['meta']['checks'], (chk, FCN['meta']['checks'])     # the same check figures as decl-e219's, to the last digit
rec['checks'] = chk
print('checks (equal to decl-e219 meta.checks)', json.dumps(chk), flush=True)

# ---------------------------------------------------------------- the runs, their conditions and the layout factors (configuration-only)
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
CASES = RL['cases']
INC = [c for c in CASES if c['domain'] == 'IN']
GEMML = ('CTRL', 'GAP', 'ANCHOR')
confs = sorted({(c['arm'], c['mask']) for c in INC if c['class'] in GEMML and c['mask'] != '0xffffffff'})
grp = collections.defaultdict(list)
for arm, mk in confs:
    m = int(mk, 16)
    grp[(bin(m).count('1'), arm)].append(feat_row(arm, m)['fresh32'])
BAR = {k: float(np.mean(v)) for k, v in grp.items()}
LAYF = {}
for c in INC:
    m = int(c['mask'], 16)
    loop = 'rgm136 gemmL' if c['class'] in GEMML else 'run_gemm'
    ph, key = EL.phi_of(loop, c['arm'], c['mask'])
    g = float(np.clip(1.0 + A_FRESH * ph[0], 0.3, 3.0))
    if c['class'] in GEMML:
        fb = BAR[(bin(m).count('1'), c['arm'])] if m != FULL else None
        fr = feat_row(c['arm'], m, fb)
    else:
        fr = feat_row(None, FULL)
    o = {'v3.1+contention': {'factor': g, 'phi_fresh': float(ph[0]), 'walk_key': key}}
    for nm, (cs, a) in CTRL.items():
        o['ctrl ' + nm] = {'factor': 1.0 + sum(ai * fr[cc] for ai, cc in zip(a, cs)), 'features': {cc: fr[cc] for cc in cs}}
    frz = FCN['cases'][c['case']]
    for nm, x in o.items():
        assert x['factor'] == frz[nm]['factor'], (c['case'], nm)
        if 'features' in x:
            assert x['features'] == frz[nm]['features'], (c['case'], nm)
    assert frz['v3.1+contention']['phi_fresh'] == o['v3.1+contention']['phi_fresh'], c['case']
    assert frz['v3.1+both']['factor'] == g, c['case']
    LAYF[c['case']] = o
rec['layout_factors_equal_to_frozen_nominal'] = f'{5 * len(LAYF)} of {5 * len(LAYF)} (+ v3.1+both {len(LAYF)} of {len(LAYF)})'
COND = None
if not NOMINAL:
    COND = json.load(open(os.path.join(OUTD, 'conditions-e219.json')))['runs']
    rec['conditions_sha256'] = sha(os.path.join(OUTD, 'conditions-e219.json'))


def cond(r):
    """the run's conditions: (f, V for MM1-v3/v3.1, V_mv for MM1-v2, t0_c)"""
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


def fields(p, ops_pass, note=''):
    """decl-e219's fields(), unchanged"""
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean'],
         'ops_per_minion_pass': ops_pass, 'sec_pass': ops_pass * p['T_op_us'] * 1e-6,
         'sec_gemm_model': p.get('seconds_per_gemm'), 'f_mhz': p.get('f_mhz'), 'minions': p.get('minions'), 'note': note,
         'kernel_model': p.get('kernel'), 'loop_model': p.get('loop')}
    if o['sec_gemm_model'] is not None:
        assert abs(o['sec_gemm_model'] / o['sec_pass'] - 1) < 1e-12, (o['sec_gemm_model'], o['sec_pass'])
    if isinstance(p.get('W_affine'), dict):
        o.update({'energy': 'FORECAST', 'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'],
                  'V': p.get('V'), 's_V': p.get('s_V'), 'G_W': p.get('G_W'), 'die_start_c': p.get('die_start_c')})
        o['J_over_idle_pass'] = o['W_fc'] * o['sec_pass']
        rl = p.get('rest_law')
        if isinstance(rl, dict):
            o['rest_law_W'] = rl.get('P_rest_W')
            o['rest_law_T0_c'] = rl.get('T0_c')
    else:
        o['energy'] = p.get('energy') if isinstance(p.get('energy'), str) else 'NOT FORECAST'
    return o


def composed(base, g, extra):
    """decl-e219's composed(), unchanged: a time factor g on MM1-v3.1's forecast; energy MM1-v3.1's affine at the composed op time"""
    o = {'T_op_us': base['T_op_us'] * g, 'cyc_wall': base['cyc_wall'] * g, 'cyc_mean': base['cyc_mean'] * g,
         'ops_per_minion_pass': base['ops_per_minion_pass'], 'sec_pass': base['sec_pass'] * g, 'f_mhz': base['f_mhz'],
         'minions': base['minions'], 'factor': g}
    o.update(extra)
    if base['energy'] != 'FORECAST':
        o['energy'] = base['energy']
        return o
    W = base['W_A'] + base['W_B'] / o['T_op_us']
    o.update({'energy': 'FORECAST', 'W_A': base['W_A'], 'W_B': base['W_B'], 'W_fc': W, 'V': base['V'], 's_V': base['s_V'],
              'G_W': base['G_W'], 'die_start_c': base['die_start_c'], 'J_over_idle_pass': W * o['sec_pass']})
    if 'rest_law_W' in base:
        o['rest_law_W'], o['rest_law_T0_c'] = base['rest_law_W'], base.get('rest_law_T0_c')
    return o


RUNS = [r for r in RL['runs'] if r['domain'] == 'IN']
OUTR = [r for r in RL['runs'] if r['domain'] != 'IN']


def spec(r):
    f, V, _, t0 = cond(r)
    return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'mask': r['mask'], 'f': f, 'kernel': 'rgm136',
            'V': V, 't0_c': t0}


specs = [spec(r) for r in RUNS]
P31s = M31.predict_many(specs)
rows = collections.OrderedDict()
for r, s, p in zip(RUNS, specs, P31s):
    o = collections.OrderedDict()
    ops = r['ops_per_minion_pass']
    f, V, Vmv, t0 = cond(r)
    o['MM1-v3.1'] = fields(p, ops)
    o['MM1-v3'] = fields(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']), ops)
    p2 = U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'], 'V_mv': Vmv})
    o['MM1-v2'] = fields(p2, ops)
    assert s['kind'] in ('zeros', 'ones', 'random'), s
    lf = LAYF[r['case']]
    g = lf['v3.1+contention']['factor']
    o['v3.1+contention'] = composed(o['MM1-v3.1'], g, {'phi_fresh': lf['v3.1+contention']['phi_fresh'], 'walk_key': lf['v3.1+contention']['walk_key'],
                                                       'note': 'F1 (#1.29.1)'})
    o['v3.1+both'] = composed(o['MM1-v3.1'], g, {'phi_fresh': lf['v3.1+contention']['phi_fresh'], 'walk_key': lf['v3.1+contention']['walk_key'],
                                                 'lnc_dW': 0.0, 'note': 'F1 x the gemmLnc term (dW = 0: no gemmLnc arm)'})
    for nm in CTRL:
        o['ctrl ' + nm] = composed(o['MM1-v3.1'], lf['ctrl ' + nm]['factor'], {'features': lf['ctrl ' + nm]['features'],
                                                                              'note': "verify-lay's control (#1.29.1.1)"})
    o['_inputs'] = {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'mask': r['mask'], 'f': f, 'V_v3_v31': V,
                    'V_mv_v2': Vmv, 't0_c_v3_v31': t0, 'kernel_arg': 'rgm136', 'ops_per_minion_pass': ops}
    rows[r['id']] = o
for r in OUTR:
    rows[r['id']] = {'OUT_OF_DOMAIN': {'domain': 'OUT', 'class': r['class'], 'token': r['token'], 'energy': 'NOT FORECAST', 'time': 'NOT FORECAST',
                                       'note': 'OUT OF DOMAIN: no frozen MM1 has a form for this arm token (the models raise KeyError on it)'}}
bad = [k for k, v in rows.items() for mdl, x in v.items() if mdl not in ('OUT_OF_DOMAIN', '_inputs')
       and not all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass'))]
assert not bad, bad[:5]
MODELS = ['MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention', 'v3.1+both'] + ['ctrl ' + n for n in CTRL]
assert MODELS == FCN['meta']['models'], (MODELS, FCN['meta']['models'])
rec['models'] = MODELS
rec['n_runs'] = len(rows)
rec['n_in_domain_runs'] = len(RUNS)
rec['n_out_of_domain_runs'] = len(OUTR)
rec['energy_status'] = {mdl: dict(collections.Counter(('FORECAST' if v[mdl]['energy'] == 'FORECAST' else 'NOT FORECAST')
                                                      for v in rows.values() if mdl in v)) for mdl in MODELS}
rec['kernels_model'] = dict(collections.Counter(f"{r['class']}:{rows[r['id']]['MM1-v3.1']['kernel_model']}" for r in RUNS))
rec['rows'] = rows
fn = os.path.join(OUTD, 'fc-nominalcheck.json' if NOMINAL else 'fc-measured.json')
json.dump(rec, open(fn, 'w'), indent=1, sort_keys=True)
print('nominal self-check' if NOMINAL else 'measured conditions', 'runs', len(rows), 'in domain', len(RUNS), 'out of domain', len(OUTR))
print('energy', json.dumps(rec['energy_status']))
print('kernel the model ran', json.dumps(rec['kernels_model']))
print('layout factors', rec['layout_factors_equal_to_frozen_nominal'])
print(sha(fn), os.path.relpath(fn, L))
