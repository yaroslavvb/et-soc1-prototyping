#!/usr/bin/env python3
"""decl-e221 (Q235) step 2: THE NOMINAL FORECASTS (the declaration's section h, the second footing, frozen now and scored beside the
measured-conditions footing): every E221 case (all 733 in MM1's domain: rgm136 gemmL) forecast by every declared model at the registered
nominal conditions, before any E221 datum exists. decl-e219's s02b_nominal.py in form, with MM1-v3.2 (landed 4e386f75) and the three
MM1-v3.3 candidates REPORTED (Q234's frozen makers, their functions unchanged).
THE NOMINAL CONDITIONS (declared): aifoundry1 card 1 f 600.0 MHz, V 0.517 V, die at start 60.0 C (the kit's a1c1 start-gate ceiling);
aifoundry1 card 0 and aifoundry2 card 0 (the governed cards) f 800.0 MHz (the kit's main band '800'), V None (each model's own volts at f),
die at start 55.0 C (the kit's a1c0 and a2c0 start-gate ceilings).
MODELS: MM1-v3.2 (predict_many), MM1-v3.1 (predict_many), MM1-v3 (predict), MM1-v2 (unread_v2_e212.call: random, zeros and ones, E221's
only kinds), 'v3.1+contention' (F1: T x clip(1 + a Phi_fresh, 0.3, 3), a = -0.08316593007433395, Phi_fresh by the term's eval_layout.phi_of
over the walk features of step 2w; energy MM1-v3.1's affine at its own op time), 'v3.1+both' (F1's time; the gemmLnc term's dW = 0: no
gemmLnc arm), verify-lay's controls (#1.29.1.1, v02_fits.py's forms and all-data constants: N1+N2, G1, G1+N1, the layout-blind F1 over
E221's configurations of the same (n shires, arm)); REPORTED: 'MM1-v3.2 + posimb' (layout2's h01_freeze.py composition at its all-data
a_hop, a_lag: the elasticity e by Engine31 at v3.2's constants with the memory constants x 1.01, G1core and LAGcore from f02_private's
features; 1 at the full mask), 'MM1-v3.2 + L3S' (l3-edge's term_l3s.ModelL3S at its all-data lam, the set model's records from step 2f;
MM1-v3.2 off the full mask). NOT APPLICABLE (no gemmLnc arm in E221): 'v3.1 + gemmLnc term' and 'MM1-v3.2 + gemmLnc term AF4' (each 0
off gemmLnc: equal to their bases on every E221 case).
SECONDS: a pass = the host's ops a minion a pass (64 MB NB KB) x the op time; the models' own seconds_per_gemm must equal it.
CHECKS before any output: F1 re-makes its 94 frozen E215 rows; the controls re-make v02_e215_controls.csv's columns; posimb re-makes every
in-scope row's g_wall and wall cycles of its frozen E220 forecast; L3S re-makes every row's wall cycles of its frozen E220 forecast.
Run: /usr/bin/python3 -I -B s02b_nominal.py <lane dir> [--test <scratch out dir>]   (--test: a code test before the declaration; nothing kept)"""
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
TEST = len(sys.argv) > 3 and sys.argv[2] == '--test'
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
LNC = os.path.join(MM1, 'v3.2-terms', 'gemmlnc')
CANDS = os.path.join(L, 'work', 'cands')
S1 = os.path.join(L, 'work', 'step1')
OUTD = os.path.abspath(sys.argv[3]) if TEST else os.path.join(L, 'work', 'step2')
os.makedirs(OUTD, exist_ok=True)
FULL = 0xFFFFFFFF
A_FRESH_POSTED = -0.08316593007433395


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


if not TEST:
    DECL = json.load(open(os.path.join(L, 'DECLARED-blind-e221.json')))
    for k, v in DECL['inputs_sha256'].items():
        if k.startswith('work/'):
            assert sha(os.path.join(L, k)) == v, k
POSTED = {os.path.join(LAY, 'forecast-e215-v31-layout.csv'): '50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754',
          os.path.join(LAY, 'forecast-e215-v31-layout.json'): 'f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259',
          os.path.join(LAY, 'freeze_layout.py'): 'ca04faa37bb4f22cb8b8b293fcefbdc99b153a2e0f15b46857ace034f926b58c',
          os.path.join(LAY, 'eval_layout.py'): 'f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1',
          os.path.join(LAY, 'features_layout.py'): 'b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3',
          os.path.join(LAY, 'out', 'features_layout.json'): '1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183',
          os.path.join(LNC, 'term-gemmlnc.json'): '2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4',
          os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'): '4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8',
          os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'): 'c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d',
          # the candidates' frozen files (W/out/orch/q234-frozen-posts.txt and each maker's FROZEN.txt)
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
          os.path.join(CANDS, 'lnc-form', 'FROZEN.txt'): '5373973ff4ce03175df72801163241cc7015003b8c0fd52e2f0b5cfaf999bfab'}
for p, h in POSTED.items():
    assert sha(p) == h, p
rec = {'what': 'decl-e221 step 2: nominal forecasts', 'python': sys.version.split()[0], 'numpy': np.__version__, 'sha256sum_c': {},
       'test_run': TEST}
MODEL_DIRS = [('MM1-v3.2', 'v3.2'), ('MM1-v3.1', 'v3.1'), ('MM1-v3', 'v3'), ('MM1-v2', 'v2')]
for nm, d in MODEL_DIRS:
    rc, nok = sumscheck(os.path.join(MM1, d))
    assert rc == 0, nm
    rec['sha256sum_c'][nm] = nok
assert sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')) == 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3'
assert sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json')) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
assert sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')) == '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'
P32P = os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json')
rec['mm1_v32_params_sha256'] = sha(P32P)

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
# the candidates' makers (this lane's read-only copies of their scripts; mm1_v32 and time_v31 are already the modules above)
H01 = load('h01_freeze', os.path.join(CANDS, 'layout2', 'scripts', 'h01_freeze.py'))
assert H01.mm1_v32 is mm1_v32 and H01.TV is TV, 'posimb maker bound to another MM1-v3.2 module'
sys.path.insert(0, os.path.join(CANDS, 'l3-edge', 'scripts'))
TL = load('term_l3s', os.path.join(CANDS, 'l3-edge', 'scripts', 'term_l3s.py'))
assert TL.M is mm1_v32, 'L3S maker bound to another MM1-v3.2 module'
FITP = json.load(open(os.path.join(CANDS, 'layout2', 'work', 'fit_results.json')))
assert FITP['declaration_sha256'] == 'a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9' and bool(FITP['keep_rule']['KEPT'])
A_HOP, A_LAG = FITP['constants_all_data']['posimb']
FITL = json.load(open(os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json')))
LAM = float(FITL['lam_all'])
assert bool(FITL['kept'])
CF = json.load(open(os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')))
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
                                         'maker': 'layout2 h01_freeze.py (fields, compose) and f02_private.py', 'kept': True},
                     'MM1-v3.2+L3S': {'lam': LAM, 'fit_l3s_sha256': sha(os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json')),
                                      'maker': 'l3-edge term_l3s.ModelL3S', 'kept': True},
                     'MM1-v3.2+AF4': 'NOT APPLICABLE: no gemmLnc arm in E221 (the term is 0 off gemmLnc)'}

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
rec['controls_constants'] = {nm: {'features': cs, 'a_all': a} for nm, (cs, a) in CTRL.items()}
rec['a_fresh'] = A_FRESH
WALK = json.load(open(os.path.join(L, 'work', 'step2', 'walk-feats-e221.json')))
FEATS = dict(EL.FEATS)
for k, v in WALK['computed'].items():
    assert k not in FEATS, k
    FEATS[k] = v
EL.FEATS.update(WALK['computed'])


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


def posimb_factors(specs, kinds_ok=True):
    """layout2 h01_freeze.main's per-point composition, line for line: (g_wall, g_mean, e, G1core, LAGcore, in_scope, feature)"""
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
        feat = None
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
rec['checks'] = chk
print('checks', json.dumps(chk), flush=True)

# ---------------------------------------------------------------- the nominal conditions and the cases
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0},
       'aifoundry2 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}
rec['nominal'] = NOM
RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
CASES = RL['cases']
confs = sorted({(c['arm'], c['mask']) for c in CASES if c['mask'] != '0xffffffff'})
grp = collections.defaultdict(list)
for arm, mk in confs:
    m = int(mk, 16)
    grp[(bin(m).count('1'), arm)].append(feat_row(arm, m)['fresh32'])
BAR = {k: float(np.mean(v)) for k, v in grp.items()}
rec['layout_blind_groups'] = {f'{k[1]}|n{k[0]}': {'configs': len(grp[k]), 'mean_phi_fresh': BAR[k]} for k in sorted(grp)}


def fields(p, ops_pass, note=''):
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
    """a time factor g on a base forecast (g_mean on the counter's mean when given); energy the base's affine at the composed op time"""
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


def spec(c, kind):
    n = NOM[c['card']]
    return {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': kind, 'mask': c['mask'], 'f': n['f'], 'kernel': 'rgm136',
            'V': n['V'], 't0_c': n['t0_c']}


specs = [spec(c, c['kind_energy']) for c in CASES]
P31 = M31.predict_many(specs)
P32L = M32.predict_many(specs)
PL3 = ML3.predict_many(specs)
PIMB = posimb_factors(specs)
dom_l3, _ = TL.features([{'arm': s['arm'], 'kernel': 'rgm136', 'mask': s['mask'], 'fmt': s['fmt'], 'f': s['f']} for s in specs], L3CACHE)
out = collections.OrderedDict()
for j, (c, s, p, p32, pl3, pim) in enumerate(zip(CASES, specs, P31, P32L, PL3, PIMB)):
    o = collections.OrderedDict()
    ops = c['ops_per_minion_pass']
    o['MM1-v3.2'] = fields(p32, ops)
    o['MM1-v3.1'] = fields(p, ops)
    o['MM1-v3'] = fields(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']), ops)
    p2 = U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'], 'V_mv': None})
    o['MM1-v2'] = fields(p2, ops)
    assert s['kind'] in ('zeros', 'ones', 'random'), s
    m = int(c['mask'], 16)
    ph, key = EL.phi_of('rgm136 gemmL', c['arm'], c['mask'])
    g = float(np.clip(1.0 + A_FRESH * ph[0], 0.3, 3.0))
    o['v3.1+contention'] = composed(o['MM1-v3.1'], g, {'phi_fresh': float(ph[0]), 'walk_key': key, 'note': 'F1 (#1.29.1)'})
    o['v3.1+both'] = composed(o['MM1-v3.1'], g, {'phi_fresh': float(ph[0]), 'walk_key': key, 'lnc_dW': 0.0,
                                                 'note': 'F1 x the gemmLnc term (dW = 0: no gemmLnc arm)'})
    fb = BAR[(bin(m).count('1'), c['arm'])] if m != FULL else None
    fr = feat_row(c['arm'], m, fb)
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
        assert o['MM1-v3.2+L3S']['cyc_wall'] == o['MM1-v3.2']['cyc_wall'], c['case']
    if not pim['in_scope']:
        assert o['MM1-v3.2+posimb']['cyc_wall'] == o['MM1-v3.2']['cyc_wall'], c['case']
    out[c['case']] = o
bad = [k for k, v in out.items() for mdl, x in v.items()
       if not all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass'))]
assert not bad, bad[:5]
MODELS = ['MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention', 'v3.1+both'] + ['ctrl ' + n for n in CTRL] + \
    ['MM1-v3.2+posimb', 'MM1-v3.2+L3S']
rec['models'] = MODELS
rec['models_reported'] = ['MM1-v3.2+posimb', 'MM1-v3.2+L3S']
fac = {nm: [v[nm]['factor'] for v in out.values()] for nm in ['v3.1+contention', 'MM1-v3.2+posimb'] + ['ctrl ' + n for n in CTRL]}
rec['factor_ranges'] = {nm: [min(x), max(x)] for nm, x in fac.items()}
rec['factor_ranges_subset_only'] = {nm: [min(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff')),
                                         max(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff'))] for nm in fac}
l3r = [v['MM1-v3.2+L3S']['cyc_wall'] / v['MM1-v3.2']['cyc_wall'] for v in out.values() if v['MM1-v3.2+L3S']['in_domain_l3s']]
rec['l3s_ratio_range_full_mask'] = [min(l3r), max(l3r), len(l3r)]
rec['n_cases'] = len(out)
rec['energy_status'] = {mdl: dict(collections.Counter(('FORECAST' if v[mdl]['energy'] == 'FORECAST' else 'NOT FORECAST')
                                                      for v in out.values())) for mdl in MODELS}
rec['cases'] = out
OUTF = os.path.join(OUTD, 'fc-nominal.json')
json.dump(rec, open(OUTF, 'w'), indent=1, sort_keys=True)
print('cases', len(out), 'models', MODELS)
print('energy', json.dumps(rec['energy_status']))
print('factor ranges (subset masks)', json.dumps(rec['factor_ranges_subset_only']))
print('L3S / v3.2 wall ratio at the full mask (min, max, n)', json.dumps(rec['l3s_ratio_range_full_mask']))
if not TEST:
    print(sha(OUTF), 'work/step2/fc-nominal.json')
else:
    print('TEST RUN: output in', OUTF, '(not kept)')
