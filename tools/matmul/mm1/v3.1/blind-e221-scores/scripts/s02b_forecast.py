#!/usr/bin/env python3
"""blind-e221 (Q235) step 2b: THE FORECASTS of every declared model at each listed run's MEASURED conditions (decl-e221's declaration,
'The forecast procedure', footing_1_measured), before any E221 measurement is read. decl-e221's s02b_nominal.py (b4303018, a FROZEN.txt
supporting file) in form and in code: the same models, the same imports and call order, the same composed forms, the same four maker checks,
one run a spec in place of one case a spec. The only E221 inputs are work/step2/conditions-e221.json (the primary view's kclock_mhz,
rails.minion.mV and the run's die_start_c) and decl-e221's inputs/step1/runs-listed.json (the registered arms and schedules).
THE CONDITIONS (declared): f = the primary view's kclock_mhz; V: card 1 the models' footing 0.517 V, the governed cards (aifoundry1 card 0,
aifoundry2 card 0) the primary view's rails.minion.mV / 1000 (else None: the model's own volts at f); the governed base by the model's own
G_of_f(card, f) (inside each predictor); t0_c = the run's die_start_c (the predictor's own 50 C when absent). MM1-v2 through MM1-v3's
unread_v2_e212.call (V_mv the measured volts; the call drops card 1's; energy for random, zeros and ones, E221's only kinds; no die term).
MODELS (decl-e221's twelve columns): MM1-v3.2 (predict_many; THE PASS RULE'S MODEL), MM1-v3.1 (predict_many), MM1-v3 (predict), MM1-v2,
'v3.1+contention' (F1: T x clip(1 + a Phi_fresh, 0.3, 3), a = -0.08316593007433395, Phi_fresh by the term's eval_layout.phi_of over the walk
features of decl-e221's step 2w; energy MM1-v3.1's affine at its own op time), 'v3.1+both' (F1's time; dW = 0: no gemmLnc arm), verify-lay's
four controls (v02_fits.py's forms and all-data constants; the layout-blind F1 over E221's listed configurations of the same (n shires,
arm)); REPORTED: 'MM1-v3.2 + posimb' (layout2's h01_freeze.py composition at its all-data a_hop, a_lag: the elasticity e by Engine31 at
v3.2's constants with the memory constants x 1.01 AT THE RUN'S CONDITIONS, G1core and LAGcore from f02_private's features of decl-e221's step
2f; 1 at the full mask) and 'MM1-v3.2 + L3S' (l3-edge's term_l3s.ModelL3S at its all-data lam, the set model's records of step 2f; MM1-v3.2
off the full mask). NOT APPLICABLE (no gemmLnc arm): 'v3.1 + gemmLnc' and 'MM1-v3.2 + AF4'.
ONE DEPARTURE IN HOW THE POSIMB MAKER IS LOADED (not in what it computes): layout2's as-run h01_freeze.py and f02_private.py hard-code their
lane folder, whose lab clone (out/layout2/work/lab) the orchestrator's 16:07 cleanup removed, so they no longer import. This script loads the
LANDED copies (tools/matmul/mm1/v3.3-cands/posimb/scripts: the as-run files but for the LANE/REG path lines, SCRUB.json; checked by step 0b)
with LAYOUT2_LANE set to this lane's stand-in folder (the landed f02_private.py, and this lane's archive of main as work/lab, whose
v01_map.py and nocbench/analyze.py are unchanged on main since before layout2's run). CHECK 3 below (every in-scope g_wall and wall cycles of
posimb's 306 frozen E220 rows re-made) is the proof that the composition is the frozen one.
SECONDS: a pass = the host's ops a minion a pass (64 MB NB KB) x the op time; the models' own seconds_per_gemm must equal it.
CHECKS before any output (decl-e221's four, their figures asserted equal to decl-e221's own record to the last digit): F1 re-makes its 94
frozen E215 rows; the controls re-make v02_e215_controls.csv's columns; posimb re-makes its 306 frozen E220 rows; L3S re-makes its 306.
Mode --nominal (a self-check, never scored): the same code at decl-e221's declared NOMINAL conditions (card 1 600 MHz, 0.517 V, 60 C; the
governed cards 800 MHz, the model's own volts, 55 C), every run of a case at the same conditions, compared by s02d with the frozen forecasts.
Desk; numpy single-threaded. Run: /usr/bin/python3 -I -B s02b_forecast.py <lane dir> [--nominal]
"""
import collections
import csv
import hashlib
import importlib.util
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
CANDS = os.path.join(L, 'work', 'cands')
DEC = os.path.join(L, 'work', 'decl')
S1 = os.path.join(DEC, 'inputs', 'step1')
S2I = os.path.join(DEC, 'inputs', 'step2')
OUTD = os.path.join(L, 'work', 'step2')
FULL = 0xFFFFFFFF
A_FRESH_POSTED = -0.08316593007433395
H01_LANDED = os.path.join(MM1, 'v3.3-cands', 'posimb', 'scripts', 'h01_freeze.py')
STANDIN_LANE = os.path.join(L, 'work', 'layout2-lane')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# the files decl-e221's s02b_nominal.py pinned (its POSTED table), on this lane's copies; and the declaration's own inputs used here
PINS = {os.path.join(LAY, 'forecast-e215-v31-layout.csv'): '50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754',
        os.path.join(LAY, 'forecast-e215-v31-layout.json'): 'f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259',
        os.path.join(LAY, 'freeze_layout.py'): 'ca04faa37bb4f22cb8b8b293fcefbdc99b153a2e0f15b46857ace034f926b58c',
        os.path.join(LAY, 'eval_layout.py'): 'f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1',
        os.path.join(LAY, 'features_layout.py'): 'b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3',
        os.path.join(LAY, 'out', 'features_layout.json'): '1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183',
        os.path.join(LNC, 'term-gemmlnc.json'): '2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'): '4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8',
        os.path.join(L, 'work', 'verify-lay', 'v02_fits.json'): '1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312',
        os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'): 'c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d',
        os.path.join(CANDS, 'layout2', 'FROZEN.txt'): '81d04c97af0ecf69e16d2a7a17141e0ca0bdf7ce57ebfd9cc42a3440516dd85f',
        os.path.join(CANDS, 'layout2', 'land', 'tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.csv'): '1de81ec510573d184c960234f83f0ed51881a5b17b7e8ce75aa3702925e86182',
        os.path.join(CANDS, 'layout2', 'land', 'tools/matmul/mm1/v3.3-cands/posimb/DECLARED-posimb.md'): 'a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9',
        os.path.join(CANDS, 'layout2', 'work', 'fit_results.json'): '816d1d51548b68062ffebf26f2c29b815a9069066c9d1f2cd71cb8fb222d3071',
        os.path.join(CANDS, 'layout2', 'work', 'private_shared.json'): 'aa5c9cf309bc71ab6cbf6d24b75d6a38aaf321477a62dacc7fc04fdb9c459e17',
        os.path.join(CANDS, 'l3-edge', 'FROZEN.txt'): 'e8216cbb2a222a1c48a4b929fd4f07d10d80f4b20f97813b700bbdc6cff401e0',
        os.path.join(CANDS, 'l3-edge', 'land', 'tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.csv'): 'ff46a16ec6c83eb3464090db1c9295d9b75338309785f0f965d3d99039f42a2e',
        os.path.join(CANDS, 'l3-edge', 'land', 'tools/matmul/mm1/v3.3-cands/l3s/DECLARED-l3s.md'): '1e6e1c52d790bc35dcb03415f22564c5592d620026420c3ad0df3ff58ebc8b26',
        os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json'): '4fe923507f7fef4d9925e8d5746727a0024b0ea42465dc0d463553e9936d750b',
        os.path.join(CANDS, 'l3-edge', 'work', 'feature', 'l3s_cache.json'): '6171c473e57534be7ca6828f08d989887b770d1197d98044068fa9efaac0668c',
        os.path.join(CANDS, 'lnc-form', 'FROZEN.txt'): '5373973ff4ce03175df72801163241cc7015003b8c0fd52e2f0b5cfaf999bfab',
        os.path.join(CANDS, 'l3-edge', 'scripts', 'term_l3s.py'): '99918f0abaa3d404d2b5372758506607415f2f0369d14b4616d98317c7ed6b86',
        os.path.join(CANDS, 'l3-edge', 'scripts', 'costs.py'): '66bb02024b2867af0ae0439d2981fdd609f4dc0a6bdd1bcc30ed3afd84a20b19',
        os.path.join(CANDS, 'l3-edge', 'scripts', 'l3s_feature.py'): '8a7b506a09baae1602dd208b4e2b11d34b656605e53e785e363c6d74ebb513f0',
        H01_LANDED: '06c9b77b787bc00e6fe2a836f533a951f687c34de43bc5d3ee104c01c921984f',
        os.path.join(STANDIN_LANE, 'scripts', 'f02_private.py'): '183a354a2f691e63b792d61098cf241dbff394761d258f5bdff3efb3096602c7',
        os.path.join(DEC, 'DECLARED-blind-e221.json'): 'b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4',
        os.path.join(DEC, 'FROZEN.txt'): '2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b',
        os.path.join(S1, 'runs-listed.json'): '3a686510a43c453ac85588d5e649c7fe2e8554c3a98357e79047784e5165fe98',
        os.path.join(S2I, 'walk-feats-e221.json'): 'b316da119b61c2ec2ab275e9528d843ae6bfad146e29edc36f0ddac6949be7b8',
        os.path.join(S2I, 'cand-feats-e221.json'): '848db0174a64edd81265ff2bfc8261585b93861b9b9437a27d02e95980e599b2',
        os.path.join(S2I, 'fc-nominal.json'): 'a80943cb770dc7f5681671fdeadecea4c571270a0a6674ae1a6911ab8895756c'}
for p, h in PINS.items():
    assert sha(p) == h, p
FCN = json.load(open(os.path.join(S2I, 'fc-nominal.json')))     # decl-e221's frozen nominal record (a FROZEN.txt supporting file)
rec = {'what': 'blind-e221 step 2b: forecasts at the ' + ('declared NOMINAL conditions (self-check)' if NOMINAL else "runs' MEASURED conditions"),
       'nominal_selfcheck': NOMINAL, 'python': sys.version.split()[0], 'numpy': np.__version__, 'sha256sum_c': {}, 'pins_checked': len(PINS)}
MODEL_DIRS = [('MM1-v3.2', 'v3.2'), ('MM1-v3.1', 'v3.1'), ('MM1-v3', 'v3'), ('MM1-v2', 'v2')]
for nm, d in MODEL_DIRS:
    rc, nok = sumscheck(os.path.join(MM1, d))
    assert rc == 0, nm
    rec['sha256sum_c'][nm] = nok
assert rec['sha256sum_c'] == FCN['sha256sum_c'], (rec['sha256sum_c'], FCN['sha256sum_c'])
assert sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')) == 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3'
assert sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json')) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
assert sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')) == '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'
P32P = os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json')
rec['mm1_v32_params_sha256'] = sha(P32P)
assert rec['mm1_v32_params_sha256'] == FCN['mm1_v32_params_sha256']

# the imports and their order exactly as decl-e221's s02b_nominal.py
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import mm1_v31  # noqa: E402
M31 = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
sys.path.insert(0, os.path.join(MM1, 'v3.2'))
import mm1_v32  # noqa: E402
P32 = json.load(open(P32P))
M32 = mm1_v32.Model(P32)
import time_v31 as TV  # noqa: E402   (v3.1's, the one mm1_v32 loaded)
sys.path.insert(0, os.path.join(MM1, 'v3'))
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402
M3 = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
M2, n2 = U2.v2_model()
sys.path.insert(0, LAY)
import eval_layout as EL  # noqa: E402
import features_layout as FL  # noqa: E402,F401   (imported for its frozen functions' identity)
# the candidates' makers: posimb by its LANDED scripts with LAYOUT2_LANE = this lane's stand-in (the departure above); L3S by the copies
# decl-e221 ran (l3-edge's as-run scripts; mm1_v32 and time_v31 are already the modules above)
os.environ['LAYOUT2_LANE'] = STANDIN_LANE
H01 = load('h01_freeze', H01_LANDED)
assert H01.mm1_v32 is mm1_v32 and H01.TV is TV, 'posimb maker bound to another MM1-v3.2 module'
assert os.path.realpath(H01.LANE) == os.path.realpath(STANDIN_LANE) and os.path.realpath(H01.F02.LAB) == os.path.realpath(os.path.join(L, 'work', 'lab'))
rec['posimb_maker_load'] = {'h01_freeze': os.path.relpath(H01_LANDED, L), 'h01_sha256': sha(H01_LANDED), 'LAYOUT2_LANE': os.path.relpath(STANDIN_LANE, L),
                            'f02_private': os.path.relpath(H01.F02.__file__, L), 'f02_sha256': sha(H01.F02.__file__),
                            'v01_map': os.path.relpath(H01.F02.V01.__file__, L), 'v01_sha256': sha(H01.F02.V01.__file__),
                            'ET_LAB': os.path.relpath(os.environ.get('ET_LAB', ''), L)}
sys.path.insert(0, os.path.join(CANDS, 'l3-edge', 'scripts'))
TL = load('term_l3s', os.path.join(CANDS, 'l3-edge', 'scripts', 'term_l3s.py'))
assert TL.M is mm1_v32, 'L3S maker bound to another MM1-v3.2 module'
FITP = json.load(open(os.path.join(CANDS, 'layout2', 'work', 'fit_results.json')))
assert FITP['declaration_sha256'] == 'a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9' and bool(FITP['keep_rule']['KEPT'])
A_HOP, A_LAG = FITP['constants_all_data']['posimb']
FITL = json.load(open(os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json')))
LAM = float(FITL['lam_all'])
assert bool(FITL['kept'])
CF = json.load(open(os.path.join(S2I, 'cand-feats-e221.json')))
PS = json.load(open(os.path.join(CANDS, 'layout2', 'work', 'private_shared.json')))
for k, v in CF['posimb']['computed'].items():
    assert k not in PS, k
    PS[k] = v
L3CACHE = json.load(open(os.path.join(CANDS, 'l3-edge', 'work', 'feature', 'l3s_cache.json')))
for k, v in CF['l3s']['computed'].items():
    assert k not in L3CACHE, k
    L3CACHE[k] = v
ML3 = TL.ModelL3S(P32, LAM, L3CACHE)
rec['candidates'] = {'MM1-v3.2+posimb': {'a_hop': A_HOP, 'a_lag': A_LAG, 'fit_results_sha256': sha(os.path.join(CANDS, 'layout2', 'work', 'fit_results.json')),
                                         'maker': 'layout2 h01_freeze.py (fields, compose) and f02_private.py (landed copies)', 'kept': True},
                     'MM1-v3.2+L3S': {'lam': LAM, 'fit_l3s_sha256': sha(os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json')),
                                      'maker': 'l3-edge term_l3s.ModelL3S', 'kept': True},
                     'MM1-v3.2+AF4': 'NOT APPLICABLE: no gemmLnc arm in E221 (the term is 0 off gemmLnc)'}
assert rec['candidates']['MM1-v3.2+posimb']['a_hop'] == FCN['candidates']['MM1-v3.2+posimb']['a_hop']
assert rec['candidates']['MM1-v3.2+posimb']['a_lag'] == FCN['candidates']['MM1-v3.2+posimb']['a_lag']
assert rec['candidates']['MM1-v3.2+L3S']['lam'] == FCN['candidates']['MM1-v3.2+L3S']['lam']

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
    assert FCN['controls_constants'][nm]['a_all'] == a, nm
rec['controls_constants'] = {nm: {'features': cs, 'a_all': a} for nm, (cs, a) in CTRL.items()}
rec['a_fresh'] = A_FRESH
WALK = json.load(open(os.path.join(S2I, 'walk-feats-e221.json')))
FEATS = dict(EL.FEATS)
for k, v in WALK['computed'].items():
    assert k not in FEATS, k
    FEATS[k] = v
EL.FEATS.update(WALK['computed'])


def key_of(arm, m):
    MB, NB, KB = (int(x) for x in EL.SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)


def feat_row(arm, m, fresh_bar=None):
    """v02_fits.py's feat_row (its E215 control columns) on the term's walk features: zeros at the full mask (decl-e221's, unchanged)"""
    if m == FULL:
        return {c: 0.0 for c in ('fresh32', 'G1', 'N1', 'N2', 'N3', 'fresh32_bar_narm')}
    f, g = FEATS[key_of(arm, m)], FEATS[key_of(arm, FULL)]
    n = f['n']
    fresh = f['fresh_lines_step'] / f['lines_req_step'] - g['fresh_lines_step'] / g['lines_req_step']
    return {'fresh32': fresh, 'G1': (110 + 12 * f['mesh_hop_mean']) / (110 + 12 * g['mesh_hop_mean']) - 1, 'N1': 1 - n / 32.0,
            'N2': (1 - n / 32.0) ** 2, 'N3': 32.0 / n - 1, 'fresh32_bar_narm': fresh if fresh_bar is None else fresh_bar}


def posimb_factors(specs, kinds_ok=True):
    """layout2 h01_freeze.main's per-point composition, line for line (decl-e221's, unchanged): (g_wall, g_mean, e, G1core, LAGcore, in_scope)"""
    th = P32['time']['theta']
    form = P32['time']['form']
    ths = dict(th)
    for k in H01.MEMK:
        ths[k] = th[k] * 1.01
    pts = []
    for s in specs:
        pre, b = H01.E.arm_parts(s['arm'])
        kernel = 'rgm211' if pre == 'gemmLn' else ('run_gemm' if pre is None else 'rgm136')
        pts.append({'arm': s['arm'], 'kernel': kernel, 'fmt': s['fmt'], 'mask': s['mask'], 'f': s['f']})
    en = TV.Engine31(pts)
    T0 = en.predict(th, form)
    T1 = en.predict(ths, form)
    e = np.log(T1 / T0) / np.log(1.01)
    res = []
    for j, s in enumerate(specs):
        m = int(s['mask'], 16)
        in_scope = m != FULL and pts[j]['kernel'] == 'rgm136' and bool(H01.SHAPE.match(s['arm']))
        G1c = LAGc = 0.0
        if in_scope:
            pkey = '%s|0x%x' % (s['arm'], m)
            if pkey not in PS:      # h01_freeze.main's own branch: a configuration not in the cache is made by f02_private (E220's check rows)
                MB, NB, KB = (int(x) for x in H01.SHAPE.match(s['arm']).groups())
                rr = H01.F02.private_shared(MB, NB, KB, m)
                rr.update(H01.F02.mesh_lat(m))
                PS[pkey] = rr
                MADE.append(pkey)
            feat = PS[pkey]
            G1c = feat['Lmean_act'] / feat['Lmean_full'] - 1.0
            F = feat['Fp'] + feat['Fs']
            LAGc = ((feat['Lmax_act'] - feat['Lmean_act']) / feat['Lmean_full']) * (feat['Fp'] / F if F > 0 else 0.0)
        ph_hop, ph_lag = float(e[j] * G1c), float(e[j] * LAGc)
        gw = float(np.clip(1.0 + A_HOP * ph_hop + A_LAG * ph_lag, 0.3, 3.0)) if in_scope else 1.0
        gm = float(np.clip(1.0 + A_HOP * ph_hop, 0.3, 3.0)) if in_scope else 1.0
        res.append({'g_wall': gw, 'g_mean': gm, 'e': float(e[j]), 'G1core': G1c, 'LAGcore': LAGc, 'in_scope': in_scope, 'T0': float(T0[j])})
    return res


# ---------------------------------------------------------------- CHECK 1: F1 re-makes its frozen E215 forecasts
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
# ---------------------------------------------------------------- CHECK 3: posimb re-makes its frozen E220 rows (g_wall and wall cycles)
MADE = []
NPS0 = len(PS)
PROWS = list(csv.DictReader(open(os.path.join(CANDS, 'layout2', 'land', 'tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.csv'))))
pspecs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': r['kind'], 'mask': r['shire_mask'], 'f': float(r['f_mhz']),
           'kernel': 'rgm136'} for r in PROWS]
pf = posimb_factors(pspecs)
pb = M32.predict_many(pspecs)
wg = wc = 0.0
for r, x, b in zip(PROWS, pf, pb):
    wg = max(wg, abs(x['g_wall'] - float(r['g_wall'])))
    wc = max(wc, abs(b['cycles_per_op_wall'] * x['g_wall'] / float(r['MM1-v3.2 + posimb|cycles_per_op_wall']) - 1))
chk['posimb_e220'] = {'rows': len(PROWS), 'in_scope_rows': sum(1 for x in pf if x['in_scope']), 'worst_abs_g_wall_diff': wg,
                      'worst_rel_wall_cycles_diff': wc, 'e220_features_made_for_the_check': len(MADE)}
assert wg < 1e-9 and wc < 1e-9, chk['posimb_e220']
for k in MADE:                # E220's check features out again: E221's forecasts use the frozen cache and step 2f's features only
    del PS[k]
assert len(PS) == NPS0
MADE = []
# ---------------------------------------------------------------- CHECK 4: L3S re-makes its frozen E220 rows (wall cycles)
LROWS = [r for r in csv.DictReader(open(os.path.join(CANDS, 'l3-edge', 'land', 'tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.csv')))
         if r['model'].startswith('MM1-v3.2 + L3S')]
lspecs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': 'random', 'mask': r['mask'], 'f': float(r['f_mhz']),
           'kernel': 'rgm136'} for r in LROWS]
lp = ML3.predict_many(lspecs)
wl = max(abs(p['cycles_per_op_wall'] / float(r['cycles_per_op_wall']) - 1) for r, p in zip(LROWS, lp))
chk['l3s_e220'] = {'rows': len(LROWS), 'worst_rel_wall_cycles_diff': wl}
assert wl < 1e-9, chk['l3s_e220']
assert chk == FCN['checks'], (chk, FCN['checks'])     # the same check figures as decl-e221's, to the last digit
rec['checks'] = chk
rec['checks_equal_to_decl_e221'] = True
print('checks (equal to decl-e221 fc-nominal.json checks)', json.dumps(chk), flush=True)

# ---------------------------------------------------------------- the runs, their conditions and the configuration-only factors
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0},
       'aifoundry2 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}
assert NOM == FCN['nominal'], FCN['nominal']
RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
CASES = RL['cases']
confs = sorted({(c['arm'], c['mask']) for c in CASES if c['mask'] != '0xffffffff'})
grp = collections.defaultdict(list)
for arm, mk in confs:
    m = int(mk, 16)
    grp[(bin(m).count('1'), arm)].append(feat_row(arm, m)['fresh32'])
BAR = {k: float(np.mean(v)) for k, v in grp.items()}
assert {f'{k[1]}|n{k[0]}': {'configs': len(grp[k]), 'mean_phi_fresh': BAR[k]} for k in sorted(grp)} == FCN['layout_blind_groups']
COND = None
if not NOMINAL:
    COND = json.load(open(os.path.join(OUTD, 'conditions-e221.json')))['runs']
    rec['conditions_sha256'] = sha(os.path.join(OUTD, 'conditions-e221.json'))


def cond(r):
    """the run's conditions: (f, V for MM1-v3.2/v3.1/v3, V_mv for MM1-v2, t0_c)"""
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
    """decl-e221's fields(), unchanged"""
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


def composed(base, g, extra, g_mean=None):
    """decl-e221's composed(), unchanged: a time factor g on a base forecast (g_mean on the counter's mean when given); energy the base's
    affine at the composed op time"""
    gm = g if g_mean is None else g_mean
    o = {'T_op_us': base['T_op_us'] * g, 'cyc_wall': base['cyc_wall'] * g, 'cyc_mean': base['cyc_mean'] * gm,
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


RUNS = RL['runs']


def spec(r):
    f, V, _, t0 = cond(r)
    return {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'mask': r['mask'], 'f': f, 'kernel': 'rgm136',
            'V': V, 't0_c': t0}


specs = [spec(r) for r in RUNS]
P31 = M31.predict_many(specs)
P32L = M32.predict_many(specs)
PL3 = ML3.predict_many(specs)
PIMB = posimb_factors(specs)
assert not MADE, ('a configuration not in the frozen caches', MADE[:5])
dom_l3, _ = TL.features([{'arm': s['arm'], 'kernel': 'rgm136', 'mask': s['mask'], 'fmt': s['fmt'], 'f': s['f']} for s in specs], L3CACHE)
rows = collections.OrderedDict()
fac_eq = collections.Counter()
for j, (r, s, p, p32, pl3, pim) in enumerate(zip(RUNS, specs, P31, P32L, PL3, PIMB)):
    o = collections.OrderedDict()
    ops = r['ops_per_minion_pass']
    f, V, Vmv, t0 = cond(r)
    o['MM1-v3.2'] = fields(p32, ops)
    o['MM1-v3.1'] = fields(p, ops)
    o['MM1-v3'] = fields(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']), ops)
    p2 = U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'], 'V_mv': Vmv})
    o['MM1-v2'] = fields(p2, ops)
    assert s['kind'] in ('zeros', 'ones', 'random'), s
    m = int(r['mask'], 16)
    ph, key = EL.phi_of('rgm136 gemmL', r['arm'], r['mask'])
    g = float(np.clip(1.0 + A_FRESH * ph[0], 0.3, 3.0))
    o['v3.1+contention'] = composed(o['MM1-v3.1'], g, {'phi_fresh': float(ph[0]), 'walk_key': key, 'note': 'F1 (#1.29.1)'})
    o['v3.1+both'] = composed(o['MM1-v3.1'], g, {'phi_fresh': float(ph[0]), 'walk_key': key, 'lnc_dW': 0.0,
                                                 'note': 'F1 x the gemmLnc term (dW = 0: no gemmLnc arm)'})
    fb = BAR[(bin(m).count('1'), r['arm'])] if m != FULL else None
    fr = feat_row(r['arm'], m, fb)
    for nm, (cs, a) in CTRL.items():
        gc = 1.0 + sum(ai * fr[cc] for ai, cc in zip(a, cs))
        o['ctrl ' + nm] = composed(o['MM1-v3.1'], gc, {'features': {cc: fr[cc] for cc in cs}, 'note': "verify-lay's control (#1.29.1.1)"})
    assert abs(pim['T0'] / p32['T_op_us'] - 1) < 1e-12, 'engine and predictor differ'
    o['MM1-v3.2+posimb'] = composed(o['MM1-v3.2'], pim['g_wall'], {'g_mean': pim['g_mean'], 'e': pim['e'], 'G1core': pim['G1core'],
                                                                  'LAGcore': pim['LAGcore'], 'in_scope': pim['in_scope'],
                                                                  'note': "REPORTED: layout2's posimb (h01_freeze's composition)"},
                                    g_mean=pim['g_mean'])
    o['MM1-v3.2+L3S'] = fields(pl3, ops, note="REPORTED: l3-edge's L3S (term_l3s.ModelL3S)")
    o['MM1-v3.2+L3S']['in_domain_l3s'] = bool(dom_l3[j])
    if not dom_l3[j]:
        assert o['MM1-v3.2+L3S']['cyc_wall'] == o['MM1-v3.2']['cyc_wall'], r['id']
    if not pim['in_scope']:
        assert o['MM1-v3.2+posimb']['cyc_wall'] == o['MM1-v3.2']['cyc_wall'], r['id']
    # the configuration-only factors equal decl-e221's frozen ones for the run's case (the walk and the controls' features)
    frz = FCN['cases'][r['case']]
    for nm in ['v3.1+contention', 'v3.1+both'] + ['ctrl ' + n for n in CTRL]:
        fac_eq['equal' if o[nm]['factor'] == frz[nm]['factor'] else 'DIFFERENT'] += 1
        assert o[nm]['factor'] == frz[nm]['factor'], (r['id'], nm)
        if 'features' in o[nm]:
            assert o[nm]['features'] == frz[nm]['features'], (r['id'], nm)
    assert o['v3.1+contention']['phi_fresh'] == frz['v3.1+contention']['phi_fresh'], r['id']
    assert o['MM1-v3.2+posimb']['in_scope'] == frz['MM1-v3.2+posimb']['in_scope'] and o['MM1-v3.2+L3S']['in_domain_l3s'] == frz['MM1-v3.2+L3S']['in_domain_l3s']
    assert o['MM1-v3.2+posimb']['G1core'] == frz['MM1-v3.2+posimb']['G1core'] and o['MM1-v3.2+posimb']['LAGcore'] == frz['MM1-v3.2+posimb']['LAGcore']
    o['_inputs'] = {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind_energy'], 'mask': r['mask'], 'f': f, 'V_models': V,
                    'V_mv_v2': Vmv, 't0_c': t0, 'kernel_arg': 'rgm136', 'ops_per_minion_pass': ops}
    rows[r['id']] = o
bad = [k for k, v in rows.items() for mdl, x in v.items() if mdl != '_inputs'
       and not all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass'))]
assert not bad, bad[:5]
MODELS = ['MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention', 'v3.1+both'] + ['ctrl ' + n for n in CTRL] + \
    ['MM1-v3.2+posimb', 'MM1-v3.2+L3S']
assert MODELS == FCN['models'], (MODELS, FCN['models'])
rec['models'] = MODELS
rec['models_reported'] = ['MM1-v3.2+posimb', 'MM1-v3.2+L3S']
rec['configuration_factors_equal_to_frozen_nominal'] = dict(fac_eq)
rec['n_runs'] = len(rows)
rec['energy_status'] = {mdl: dict(collections.Counter(('FORECAST' if v[mdl]['energy'] == 'FORECAST' else 'NOT FORECAST')
                                                      for v in rows.values())) for mdl in MODELS}
rec['posimb_features_made_here'] = len(MADE)
rec['rows'] = rows
fn = os.path.join(OUTD, 'fc-nominalcheck.json' if NOMINAL else 'fc-measured.json')
json.dump(rec, open(fn, 'w'), indent=1, sort_keys=True)
print('nominal self-check' if NOMINAL else 'measured conditions', 'runs', len(rows))
print('energy', json.dumps(rec['energy_status']))
print('configuration factors equal to the frozen nominal ones', json.dumps(rec['configuration_factors_equal_to_frozen_nominal']))
print('posimb maker load', json.dumps(rec['posimb_maker_load']))
print(sha(fn), os.path.relpath(fn, L))
