#!/usr/bin/env python3
"""decl-e217 (Q228) step 2: THE NOMINAL FORECASTS (the declaration's section h, the second footing, frozen now and scored beside the
measured-conditions footing): every E217 case forecast by every declared model at the registered nominal conditions, before any E217 datum
exists. Inputs: work/step1/runs-listed.json (the registered arms and schedules), the frozen models (work copies of GitHub main 8bde0182,
their SHA256SUMS checked here), the two frozen terms' land dirs (their posted sha256 checked), verify-lay's fits record (the controls'
constants), and the walk features (the term's frozen cache + work/step2/walk-feats-e217.json, made by the term's own code from the arms).
THE NOMINAL CONDITIONS (declared): aifoundry1 card 1 f 600.0 MHz, V 0.517 V (the models' card-1 footing), die at start 60.0 C (the kit's
start-gate ceiling, mms_common.CARDS['a1c1']['gate']['ceiling_c']); aifoundry1 card 0 f 800.0 MHz (its planned clock: the kit's main band
'800', the governed card's counted launches), V None (each model's own volts at f: 0.604 V), die at start 55.0 C (the a1c0 gate ceiling).
MODELS: MM1-v3.1 (predict_many), MM1-v3 (predict), MM1-v2 (unread_v2_e212.call, energy for random, zeros and ones only),
'v3.1+contention' (F1: T x clip(1 + a Phi_fresh, 0.3, 3), a = -0.08316593007433395 from the frozen forecast's meta; energy MM1-v3.1's affine
at its own op time), 'v3.1+both' (the composition declared in reg-e216: F1's time, B + dW t_op with the gemmLnc term's dW = 0 off gemmLnc:
equal to 'v3.1+contention' on every E217 case, computed by the composition all the same), and verify-lay's controls (#1.29.1.1) by
v02_fits.py's forms with its all-data constants (work/verify-lay/v02_fits.json): N1+N2, G1, G1+N1 and the layout-blind F1 (fresh32_bar_narm:
Phi_fresh averaged over E217's listed configurations of the same (n shires, arm), both cards, as v02_fits.py averages over the fit's points of
the same (n, arm)); a control's factor is 1 + sum a_i x_i (v02's E215 control columns: unclipped; 0 off the subset masks), its time the
MM1-v3.1 time x the factor, its energy MM1-v3.1's affine at its own op time. 'v3.1 + gemmLnc term' is NOT APPLICABLE: E217 runs no gemmLnc
arm (0 of 332 arms), so it equals MM1-v3.1 on every case.
ENERGY OF THE 21 NEW KINDS: NOT FORECAST at this freeze by any model (no committed count: MM1-v3.1 and MM1-v3 print NOT FORECAST; MM1-v2
prices random, zeros and ones only); their switch-route energy is made after counts-e217 (step 4) as the declaration's section e says. For
group S the null kinds' W (zeros, ones, random at the same conditions, MM1-v3.1 and MM1-v3) are frozen here: the null N of the switch test.
CHECKS before any output: the two terms' makers re-make their frozen E215 forecasts (F1: all 94 rows' factor and cycles; the controls: every
E215 subset row's N3, N1+N2, G1 and G1+N1 columns of v02_e215_controls.csv).
Run: /usr/bin/python3 -I -B s02b_nominal.py <lane dir>"""
import collections
import copy
import csv
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
LNC = os.path.join(MM1, 'v3.2-terms', 'gemmlnc')
S1 = os.path.join(L, 'work', 'step1')
OUTD = os.path.join(L, 'work', 'step2')
FULL = 0xFFFFFFFF
A_FRESH_POSTED = -0.08316593007433395


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


DECL = json.load(open(os.path.join(L, 'DECLARED-blind-e217.json')))
INP = DECL['inputs_sha256']
for k, v in INP.items():
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
          os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'): 'c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d'}
for p, h in POSTED.items():
    assert sha(p) == h, p
rec = {'what': 'decl-e217 step 2: nominal forecasts', 'python': sys.version.split()[0], 'numpy': np.__version__, 'sha256sum_c': {}}
for nm, d in (('MM1-v3.1', os.path.join(MM1, 'v3.1')), ('MM1-v3', os.path.join(MM1, 'v3')), ('MM1-v2', os.path.join(MM1, 'v2'))):
    rc, nok = sumscheck(d)
    assert rc == 0, nm
    rec['sha256sum_c'][nm] = nok
assert sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')) == 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3'
assert sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json')) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
assert sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')) == '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'

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
import features_layout as FL  # noqa: E402   (imported for its frozen functions' identity; the walk ran in step 2w)

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
WALK = json.load(open(os.path.join(OUTD, 'walk-feats-e217.json')))
FEATS = dict(EL.FEATS)
for k, v in WALK['computed'].items():
    assert k not in FEATS, k
    FEATS[k] = v
EL.FEATS.update(WALK['computed'])   # the term's phi_of reads its module cache: the new keys added, the frozen ones untouched


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
assert all(v < 0.12 for v in worst.values()), worst          # 4 dp v31 in the CSV: |a x| v31 rounding stays far below 0.12 cycles
rec['checks'] = chk
print('checks', json.dumps(chk), flush=True)

# ---------------------------------------------------------------- the nominal conditions and the cases
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}
rec['nominal'] = NOM
RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
CASES = RL['cases']
# the layout-blind F1's feature: Phi_fresh averaged over E217's configurations of the same (n, arm) (both cards; a configuration once)
confs = sorted({(c['arm'], c['mask']) for c in CASES if c['mask'] != '0xffffffff'})
grp = collections.defaultdict(list)
for arm, mk in confs:
    m = int(mk, 16)
    grp[(bin(m).count('1'), arm)].append(feat_row(arm, m)['fresh32'])
BAR = {k: float(np.mean(v)) for k, v in grp.items()}
rec['layout_blind_groups'] = {f'{k[1]}|n{k[0]}': {'configs': len(grp[k]), 'mean_phi_fresh': BAR[k]} for k in sorted(grp)}
NULLK = ('zeros', 'ones', 'random')


def fields(p, note=''):
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean'],
         'sec_gemm': p.get('seconds_per_gemm'), 'ops_per_minion_per_gemm': p.get('ops_per_minion_per_gemm'), 'f_mhz': p.get('f_mhz'),
         'minions': p.get('minions'), 'note': note}
    if isinstance(p.get('W_affine'), dict):
        o.update({'energy': 'FORECAST', 'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'],
                  'V': p.get('V'), 's_V': p.get('s_V'), 'G_W': p.get('G_W'), 'die_start_c': p.get('die_start_c')})
        rl = p.get('rest_law')
        if isinstance(rl, dict):
            o['rest_law_W'] = rl.get('P_rest_W')
            o['rest_law_T0_c'] = rl.get('T0_c')
    else:
        o['energy'] = p.get('energy') if isinstance(p.get('energy'), str) else 'NOT FORECAST'
    return o


def composed(base, g, extra):
    """a time factor g on MM1-v3.1's forecast; energy MM1-v3.1's affine at the composed op time (A + B / t); B unchanged (dW = 0 here)"""
    o = {'T_op_us': base['T_op_us'] * g, 'cyc_wall': base['cyc_wall'] * g, 'cyc_mean': base['cyc_mean'] * g,
         'sec_gemm': base['sec_gemm'] * g, 'ops_per_minion_per_gemm': base['ops_per_minion_per_gemm'], 'f_mhz': base['f_mhz'],
         'minions': base['minions'], 'factor': g}
    o.update(extra)
    if base['energy'] != 'FORECAST':
        o['energy'] = base['energy']
        return o
    W = base['W_A'] + base['W_B'] / o['T_op_us']
    o.update({'energy': 'FORECAST', 'W_A': base['W_A'], 'W_B': base['W_B'], 'W_fc': W, 'V': base['V'], 's_V': base['s_V'],
              'G_W': base['G_W'], 'die_start_c': base['die_start_c']})
    if 'rest_law_W' in base:
        o['rest_law_W'], o['rest_law_T0_c'] = base['rest_law_W'], base.get('rest_law_T0_c')
    return o


def spec(c, kind):
    n = NOM[c['card']]
    return {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': kind, 'mask': c['mask'], 'f': n['f'], 'kernel': 'rgm136',
            'V': n['V'], 't0_c': n['t0_c']}


specs = [spec(c, c['kind_energy']) for c in CASES]
P31 = M31.predict_many(specs)
out = collections.OrderedDict()
for c, s, p in zip(CASES, specs, P31):
    o = collections.OrderedDict()
    o['MM1-v3.1'] = fields(p)
    o['MM1-v3'] = fields(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']))
    p2 = U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'], 'V_mv': None})
    o['MM1-v2'] = fields(p2)
    if s['kind'] not in NULLK:
        for k in [k for k in o['MM1-v2'] if k.startswith('W_') or k in ('V', 's_V', 'G_W', 'die_start_c', 'rest_law_W', 'rest_law_T0_c')]:
            o['MM1-v2'].pop(k)
        o['MM1-v2']['energy'] = "NOT FORECAST: MM1-v2 prices random, zeros and ones only (unread_v2_e212.call's form)"
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
    if c['group_kind'] == 'S':
        nulls = {}
        for mdl, fn in (('MM1-v3.1', lambda sp: M31.predict_many([sp])[0]),
                        ('MM1-v3', lambda sp: M3.predict(sp['card'], sp['arm'], sp['fmt'], sp['kind'], sp['mask'], sp['f'], kernel='rgm136', V=sp['V'], t0_c=sp['t0_c']))):
            for k in NULLK:
                q = fn(spec(c, k))
                nulls[f'{mdl}|{k}'] = {'W_A': q['W_affine']['A_W'], 'W_B': q['W_affine']['B_W_us'], 'W_fc': q['W_over_idle'], 'T_op_us': q['T_op_us']}
        o['null_kinds'] = nulls
    out[c['case']] = o
# sanity: every time field finite; the time is kind-blind (MM1-v3.1's T for a kind equals the same configuration's at zeros)
bad = [k for k, v in out.items() for mdl, x in v.items() if mdl != 'null_kinds' and not all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean'))]
assert not bad, bad[:5]
fac = {nm: [v[nm]['factor'] for v in out.values()] for nm in ['v3.1+contention'] + ['ctrl ' + n for n in CTRL]}
rec['factor_ranges'] = {nm: [min(x), max(x)] for nm, x in fac.items()}
rec['factor_ranges_subset_only'] = {nm: [min(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff')),
                                         max(v[nm]['factor'] for k, v in out.items() if not k.endswith('|0xffffffff'))] for nm in fac}
rec['n_cases'] = len(out)
rec['energy_status'] = {mdl: dict(collections.Counter(('FORECAST' if v[mdl]['energy'] == 'FORECAST' else 'NOT FORECAST') for v in out.values()))
                        for mdl in ('MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention')}
rec['cases'] = out
json.dump(rec, open(os.path.join(OUTD, 'fc-nominal.json'), 'w'), indent=1, sort_keys=True)
print('cases', len(out), 'energy', json.dumps(rec['energy_status']))
print('factor ranges (subset masks)', json.dumps(rec['factor_ranges_subset_only']))
print('layout-blind groups', len(BAR), 'of which single-configuration', sum(1 for v in grp.values() if len(v) == 1))
print(sha(os.path.join(OUTD, 'fc-nominal.json')), 'work/step2/fc-nominal.json')
