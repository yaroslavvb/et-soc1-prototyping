#!/usr/bin/env python3
"""decl-e223 (Q239) step 2: THE NOMINAL FORECASTS (the declaration's section h, the second footing, frozen now and scored beside the
measured-conditions footing): every E223 case (all 695 in MM1's domain: rgm136 gemmL) forecast by every declared model at the registered
nominal conditions, before any E223 datum exists. decl-e221's s02b_nominal.py in form; the candidates and their compositions by E224's
frozen callers (tools/claims-v3/e224/desk/models_e224.py, registration 7de83360 / kit 0fb6eb95, unchanged: posimb_rows, af4_rows,
ModelL3S, compose, compose_sub) and Q238's frozen 'MM1-v3.2 + posimb-mask' (tools/matmul/mm1/v3.4-cands/posimb-mask/posimb_mask.py,
FROZEN.txt 0cd8e9da..., unchanged).
THE NOMINAL CONDITIONS (declared): aifoundry1 card 1 f 600.0 MHz, V 0.517 V, die at start 60.0 C (the kit's a1c1 start-gate ceiling);
aifoundry1 card 0 and aifoundry2 card 0 (the governed cards) f 800.0 MHz (the kit's main band '800'), V None (each model's own volts at f),
die at start 55.0 C (the kit's a1c0 and a2c0 start-gate ceilings). E223's kit is E221's (mms_common.py: the same bands and gates).
MODELS (columns): MM1-v3.2 (predict_many; THE REGISTERED BASELINE, the pass rule's model), MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's SEL, by
models_e224.af4_rows unchanged: AF4 acts only at gemmLnc tokens, so on every E223 case it equals MM1-v3.2, checked to 1e-12 here), MM1-v3.1
(predict_many), MM1-v3 (predict), MM1-v2 (unread_v2_e212.call: random, zeros and ones, E223's only kinds); REPORTED: 'MM1-v3.2 + posimb'
(models_e224.posimb_rows: h01_freeze's per-row form), 'MM1-v3.2 + L3S' (ModelL3S), the compositions by E222's and E224's construction
(compose_sub: 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S'; compose: 'MM1-v3.2 + all three'), and Q238's
'MM1-v3.2 + posimb-mask' with 'MM1-v3.2 + AF4 + posimb-mask' (posimb_mask.Model.predict_many_with_af4).
SECONDS: a pass = the host's ops a minion a pass (64 MB NB KB) x the op time; each model's own seconds_per_gemm must equal it.
CHECKS before any output: (A) E224's frozen forecasts (forecast-e224.csv, every row of the lab's kinds at both arms and every clock) re-made
by E224's own Models.forecast at this lane's work copy; (B) Q238's posimb-mask re-makes its frozen forecasts-compose-e222-e224.csv rows of
the lab's kinds; (C) every column's W over idle equals its affine A + B / t at its own op time; MM1-v3.3 equals MM1-v3.2 on every case;
each composition's internal checks (E224's: compose_sub at all three = compose; each single term = its own candidate).
Run: /usr/bin/python3 -I -B s02b_nominal.py <lane dir> [--test <scratch out dir>]   (--test: a code test before the declaration; nothing kept)
The function forecast_cases(cases, cond) is the declared forecast procedure's caller (blind-e223 calls it at each run's measured
conditions: cond[case-or-run key] = {'f', 'V', 't0_c'})."""
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

L = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
TEST = len(sys.argv) > 3 and sys.argv[2] == '--test'
LW = os.path.join(L, 'work', 'lab')
MM1 = os.path.join(LW, 'tools', 'matmul', 'mm1')
E224D = os.path.join(LW, 'tools', 'claims-v3', 'e224')
PMD = os.path.join(MM1, 'v3.4-cands', 'posimb-mask')
S1 = os.path.join(L, 'work', 'step1')
OUTD = os.path.abspath(sys.argv[3]) if TEST else os.path.join(L, 'work', 'step2')
os.makedirs(OUTD, exist_ok=True)
FULL = 0xFFFFFFFF
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0},
       'aifoundry2 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}
BASE_MODELS = ['MM1-v3.2', 'MM1-v3.3', 'MM1-v3.1', 'MM1-v3', 'MM1-v2']
REPORTED = ['MM1-v3.2 + posimb', 'MM1-v3.2 + L3S', 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S',
            'MM1-v3.2 + all three', 'MM1-v3.2 + posimb-mask', 'MM1-v3.2 + AF4 + posimb-mask']
MODELS = BASE_MODELS + REPORTED
PM_FROZEN_SHA = '0cd8e9da11e1b0f0bedba342e40adf2a18e9ff112f87e5436d712f32fe5eafdc'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sumscheck(d, f='SHA256SUMS'):
    r = subprocess.run(['sha256sum', '-c', f], cwd=d, capture_output=True, text=True)
    return r.returncode, sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


if not TEST:
    DECL = json.load(open(os.path.join(L, 'DECLARED-blind-e223.json')))
    for k, v in DECL['inputs_sha256'].items():
        if k.startswith('work/'):
            assert sha(os.path.join(L, k)) == v, k
rec = {'what': 'decl-e223 step 2: nominal forecasts', 'python': sys.version.split()[0], 'numpy': np.__version__, 'sha256sum_c': {},
       'test_run': TEST, 'lab_commit': open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()}
for nm, d in (('MM1-v3.2', 'v3.2'), ('MM1-v3.1', 'v3.1'), ('MM1-v3', 'v3'), ('MM1-v2', 'v2'), ('posimb', 'v3.3-cands/posimb'),
              ('gemmlnc-af4', 'v3.3-cands/gemmlnc-af4'), ('l3s', 'v3.3-cands/l3s'), ('posimb-mask', 'v3.4-cands/posimb-mask')):
    rc, nok = sumscheck(os.path.join(MM1, d))
    assert rc == 0, nm
    rec['sha256sum_c'][nm] = nok
for d, s in (('tools/claims-v3/e224', 'SHA256SUMS-e224-registration'), ('tools/claims-v3/e224', 'SHA256SUMS-e224-kit')):
    r = subprocess.run(['sha256sum', '-c', os.path.join(d, s)], cwd=LW, capture_output=True, text=True)
    assert r.returncode == 0, s
    rec['sha256sum_c'][s] = sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))
# Q238's posimb-mask: every file its FROZEN.txt lists, at the posted FROZEN.txt
assert sha(os.path.join(L, 'work', 'mask-posimb-FROZEN.txt')) == PM_FROZEN_SHA
r = subprocess.run(['sha256sum', '-c', os.path.join(L, 'work', 'mask-posimb-frozen-lines.txt')], cwd=PMD, capture_output=True, text=True)
assert r.returncode == 0
rec['sha256sum_c']['posimb-mask FROZEN.txt lines'] = sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))
assert sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')) == 'd01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3'
assert sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json')) == '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db'
assert sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')) == '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5'
assert sha(os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json')) == 'c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab'
assert sha(os.path.join(E224D, 'desk', 'models_e224.py')) == rec.setdefault('models_e224_sha256', sha(os.path.join(E224D, 'desk', 'models_e224.py')))

sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import mm1_v31  # noqa: E402
sys.path.insert(0, os.path.join(MM1, 'v3.2'))
import mm1_v32  # noqa: E402
sys.path.insert(0, os.path.join(MM1, 'v3'))
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402
sys.path.insert(0, os.path.join(E224D, 'desk'))
import models_e224 as MZ  # noqa: E402
assert os.path.normpath(MZ.REPO) == os.path.normpath(LW), MZ.REPO
MZM = MZ.Models(cands=True, e217=False)       # check_pins() inside: every pinned file of E224's callers at this work copy
assert MZM.mm1_v32 is mm1_v32, 'E224 callers bound to another MM1-v3.2 module'
M32 = MZM.M32
M31 = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
M3 = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
M2, n2 = U2.v2_model()
sys.path.insert(0, PMD)
import posimb_mask as PMK  # noqa: E402
assert os.path.normpath(PMK.REPO) == os.path.normpath(LW), PMK.REPO
PMM = PMK.Model()
rec['candidates'] = {'MM1-v3.2 + posimb': {'a_hop': MZM.a_hop, 'a_lag': MZM.a_lag, 'maker': 'models_e224.posimb_rows (h01_freeze per-row form)'},
                     'MM1-v3.2 + AF4': {'constants_pJ': MZM.CONST_AF4, 'maker': 'models_e224.af4_rows (s03_freeze per-row form)'},
                     'MM1-v3.2 + L3S': {'lam': MZM.lam, 'maker': 'models_e224: term_l3s.ModelL3S'},
                     'MM1-v3.2 + posimb-mask': {'constants': PMM.par['constants'], 'maker': 'posimb_mask.Model (Q238, FROZEN.txt 0cd8e9da)'}}


def fields_raw(p, ops_pass, note=''):
    """decl-e221's fields(): a base predictor's raw output -> the declared record"""
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


def fields_z(x, ops_pass, base, extra=None):
    """an E224-form record (T_op_us, cycles_per_op_wall, ..., A_W, B_W_us, W_over_idle) -> the declared record; conditions from the base"""
    o = {'T_op_us': x['T_op_us'], 'cyc_wall': x['cycles_per_op_wall'], 'cyc_mean': x['cycles_per_op_mean'], 'ops_per_minion_pass': ops_pass,
         'sec_pass': ops_pass * x['T_op_us'] * 1e-6, 'sec_gemm_model': x.get('seconds_per_gemm'), 'f_mhz': base.get('f_mhz'),
         'minions': base.get('minions')}
    if o['sec_gemm_model'] is not None:
        assert abs(o['sec_gemm_model'] / o['sec_pass'] - 1) < 1e-12, (o['sec_gemm_model'], o['sec_pass'])
    if x.get('W_over_idle') is not None and x.get('A_W') is not None:
        o.update({'energy': 'FORECAST', 'W_A': x['A_W'], 'W_B': x['B_W_us'], 'W_fc': x['W_over_idle'], 'V': base.get('V'),
                  's_V': base.get('s_V'), 'G_W': base.get('G_W'), 'die_start_c': base.get('die_start_c')})
        o['J_over_idle_pass'] = o['W_fc'] * o['sec_pass']
        if x.get('rest_law_W') is not None:
            o['rest_law_W'] = x['rest_law_W']
    else:
        o['energy'] = 'NOT FORECAST'
    o['factor'] = o['T_op_us'] / base['T_op_us']
    if extra:
        o.update(extra)
    return o


def forecast_cases(cases, cond):
    """THE DECLARED CALLERS: cases = [{'key', 'card', 'arm', 'fmt', 'kind_energy', 'mask', 'ops_per_minion_pass'}], cond[key] = {'f', 'V', 't0_c'}
    -> {key: {model: record}}; every frozen predictor unchanged; the candidates on MM1-v3.2's forecast at the same conditions."""
    specs = [{'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind_energy'], 'mask': c['mask'], 'f': float(cond[c['key']]['f']),
              'kernel': 'rgm136', 'V': cond[c['key']]['V'], 't0_c': cond[c['key']]['t0_c']} for c in cases]
    for s in specs:
        assert s['kind'] in ('zeros', 'ones', 'random'), s
    r32 = M32.predict_many(specs)
    r31 = M31.predict_many(specs)
    pr = MZM.posimb_rows(specs, r32)
    ar = MZM.af4_rows(specs, r32)
    made_l3s = MZM.l3s_ensure(specs)
    lr = MZM.ML3S.predict_many(specs)
    dom, fsa = MZM.TL.features([{'arm': s['arm'], 'kernel': 'rgm136', 'mask': s['mask'], 'fmt': s['fmt'], 'f': s['f']} for s in specs],
                               MZM.l3s_cache)
    pmr = PMM.predict_many_with_af4(specs)
    out = collections.OrderedDict()
    for j, (c, s) in enumerate(zip(cases, specs)):
        ops = c['ops_per_minion_pass']
        o = collections.OrderedDict()
        b = fields_raw(r32[j], ops)
        o['MM1-v3.2'] = b
        # E224's record set for the compositions, by its own methods
        z = {'MM1-v3.2': MZ.fields(r32[j])}
        MZM._posimb_out(z, pr[j])
        MZM._af4_out(z, z['MM1-v3.2'], ar[j])
        MZM._l3s_out(z, lr[j], dom[j], fsa[j])
        p = {'id': c['key'], 'arm': s['arm'], 'mask': s['mask']}
        z[MZ.COMBO] = MZ.compose(p, z, MZM)
        for terms in (('posimb', 'AF4'), ('posimb', 'L3S'), ('AF4', 'L3S')):
            z[MZ.COMPOS[terms]] = MZ.compose_sub(p, z, MZM, terms)
        chk = MZ.compose_sub(p, z, MZM, MZ.TERMS)
        assert MZ._close(chk, z[MZ.COMBO], 0.0) and chk['acting'] == z[MZ.COMBO]['acting'], ('compose_sub all three', c['key'])
        for t, n in (('posimb', MZ.POSIMB), ('AF4', MZ.AF4), ('L3S', MZ.L3S)):
            one = MZ.compose_sub(p, z, MZM, (t,))
            assert MZ._close(one, z[n] if one['acting'] else z['MM1-v3.2']), ('single term', t, c['key'])
        # MM1-v3.3 = MM1-v3.2 + AF4 (E222's SEL): AF4 is 0 off gemmLnc
        assert not z[MZ.AF4]['in_scope'] and MZ._close(z[MZ.AF4], z['MM1-v3.2']), ('AF4 acts at a gemmL case', c['key'])
        o['MM1-v3.3'] = fields_z(z[MZ.AF4], ops, b, {'in_scope_AF4': False, 'note': "MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's SEL); AF4 0 off gemmLnc"})
        o['MM1-v3.1'] = fields_raw(r31[j], ops)
        o['MM1-v3'] = fields_raw(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'],
                                            t0_c=s['t0_c']), ops)
        p2 = U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'], 'V_mv': None})
        o['MM1-v2'] = fields_raw(p2, ops)
        o['MM1-v3.2 + posimb'] = fields_z(z[MZ.POSIMB], ops, b, {'in_scope_posimb': bool(z[MZ.POSIMB]['in_scope']),
                                                                 'g_wall': z[MZ.POSIMB]['term']['g_wall'], 'g_mean': z[MZ.POSIMB]['term']['g_mean']})
        o['MM1-v3.2 + L3S'] = fields_z(z[MZ.L3S], ops, b, {'in_domain_l3s': bool(z[MZ.L3S]['in_scope'])})
        for nm in ('MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S', 'MM1-v3.2 + all three'):
            o[nm] = fields_z(z[nm], ops, b, {'acting': list(z[nm]['acting']), 'how': z[nm]['how']})
        pm = pmr[j]
        for k in ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'W_over_idle', 'A_W', 'B_W_us'):
            a_, b_ = pm['MM1-v3.2'][k], z['MM1-v3.2'][k] if k in z['MM1-v3.2'] else None
            assert b_ is not None and abs(a_ - b_) <= 1e-12 * max(abs(a_), abs(b_)), ('posimb-mask base differs', k, c['key'])
        o['MM1-v3.2 + posimb-mask'] = fields_z(pm[PMK.LABEL], ops, b, {'in_scope_posimb_mask': bool(pm['in_scope']),
                                                                       'g_wall': pm['term']['g_wall'], 'g_mean': pm['term']['g_mean'],
                                                                       'A1': pm['term'].get('A1')})
        o['MM1-v3.2 + AF4 + posimb-mask'] = fields_z(pm[PMK.LABEL_AF4], ops, b, {'how': pm[PMK.LABEL_AF4]['how']})
        for nm, x in o.items():
            assert all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass')), (nm, c['key'])
            if x['energy'] == 'FORECAST':
                assert abs((x['W_A'] + x['W_B'] / x['T_op_us']) / x['W_fc'] - 1) < 1e-9, ('affine', nm, c['key'])
        out[c['key']] = o
    return out, {'l3s_records_made': made_l3s, 'posimb_features_made': sorted(MZM.PS_made), 'posimb_mask_features_made': sorted(PMM.PS_made)}


if __name__ == '__main__':
    # ---------------------------------------------------------------- CHECK A: E224's frozen forecasts re-made by E224's own Models.forecast
    FR = list(csv.DictReader(open(os.path.join(E224D, 'forecast-e224.csv'))))
    want = collections.defaultdict(dict)
    for r in FR:
        if r['kind'] not in ('zeros', 'ones', 'random') or not r['token'].startswith('gemmL'):
            continue
        want[(r['arm'], float(r['clock_mhz']))][(r['id'], r['forecaster'])] = r
    chkA = {'rows': 0, 'worst_rel': 0.0, 'fields': ['cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'W_over_idle', 'A_W', 'B_W_us']}
    for (arm, f), rows in sorted(want.items()):
        card = MZ.ARMS[arm]['card']
        ids = sorted({k[0] for k in rows})
        pts = [{'id': i, 'arm': rows[[k for k in rows if k[0] == i][0]]['token'], 'fmt': rows[[k for k in rows if k[0] == i][0]]['format'],
                'kind': rows[[k for k in rows if k[0] == i][0]]['kind'], 'mask': rows[[k for k in rows if k[0] == i][0]]['mask']} for i in ids]
        got = MZM.forecast(pts, f=f, card=card)
        for (i, fc), r in rows.items():
            x = got[i].get(fc)
            if x is None:
                continue
            chkA['rows'] += 1
            for k in chkA['fields']:
                if r.get(k) in ('', None) or x.get(k) is None:
                    continue
                chkA['worst_rel'] = max(chkA['worst_rel'], abs(float(x[k]) / float(r[k]) - 1))
    assert chkA['rows'] > 1000 and chkA['worst_rel'] < 1e-9, chkA
    # ---------------------------------------------------------------- CHECK B: posimb-mask re-makes its frozen E222/E224 rows
    PR = [r for r in csv.DictReader(open(os.path.join(PMD, 'forecasts-compose-e222-e224.csv'))) if r['kind'] in ('zeros', 'ones', 'random')]
    pspecs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': r['kind'], 'mask': r['mask'], 'f': float(r['f_mhz']),
               'kernel': 'rgm136'} for r in PR]
    pg = PMM.predict_many_with_af4(pspecs)
    wb = 0.0
    for r, x in zip(PR, pg):
        for lab in (PMK.LABEL, PMK.LABEL_AF4):
            for k in ('cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'W_over_idle'):
                v = r.get(f'{lab}|{k}')
                if v in ('', None) or x[lab].get(k) is None:
                    continue
                wb = max(wb, abs(x[lab][k] / float(v) - 1))
    chkB = {'rows': len(PR), 'worst_rel': wb, 'posimb_mask_features_made_for_the_check': len(PMM.PS_made)}
    assert len(PR) > 100 and wb < 1e-9, chkB
    for k in list(PMM.PS_made):          # the check's features out again: E223's use the frozen cache and the walk only
        del PMM.PS[k]
    PMM.PS_made.clear()
    NPS = len(MZM.PS_made)
    for k in list(MZM.PS_made):
        del MZM.PS[k]
    MZM.PS_made.clear()
    rec['checks'] = {'A_e224_forecasts_remade': chkA, 'B_posimb_mask_remade': chkB, 'A_posimb_features_made_and_dropped': NPS}
    print('checks', json.dumps(rec['checks']), flush=True)
    # ---------------------------------------------------------------- the nominal conditions and the cases
    rec['nominal'] = NOM
    RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
    CASES = [dict(c, key=c['case']) for c in RL['cases']]
    out, made = forecast_cases(CASES, {c['key']: NOM[c['card']] for c in CASES})
    rec['made'] = {k: len(v) for k, v in made.items()}
    rec['made_keys'] = made
    rec['models'] = MODELS
    rec['models_reported'] = REPORTED
    rec['n_cases'] = len(out)
    rec['energy_status'] = {m: dict(collections.Counter(('FORECAST' if v[m]['energy'] == 'FORECAST' else 'NOT FORECAST') for v in out.values()))
                            for m in MODELS}
    rec['scope'] = {'posimb (subset masks of rgm136 gemmL)': sum(1 for v in out.values() if v['MM1-v3.2 + posimb']['in_scope_posimb']),
                    'L3S (full mask, gemmL)': sum(1 for v in out.values() if v['MM1-v3.2 + L3S']['in_domain_l3s']),
                    'AF4 (gemmLnc)': 0,
                    'posimb-mask (subset masks of rgm136 gemmL)': sum(1 for v in out.values() if v['MM1-v3.2 + posimb-mask']['in_scope_posimb_mask'])}
    fr = {}
    for m in ('MM1-v3.2 + posimb', 'MM1-v3.2 + L3S', 'MM1-v3.2 + all three', 'MM1-v3.2 + posimb-mask'):
        xs = [v[m]['factor'] for v in out.values()]
        fr[m] = [min(xs), max(xs)]
    rec['factor_ranges'] = fr
    rec['equal_to_MM1-v3.2_everywhere'] = {m: all(abs(v[m]['cyc_wall'] / v['MM1-v3.2']['cyc_wall'] - 1) < 1e-12 and
                                                  (v[m]['energy'] != 'FORECAST' or abs(v[m]['W_fc'] / v['MM1-v3.2']['W_fc'] - 1) < 1e-12)
                                                  for v in out.values()) for m in MODELS}
    rec['cases'] = out
    OUTF = os.path.join(OUTD, 'fc-nominal.json')
    json.dump(rec, open(OUTF, 'w'), indent=1, sort_keys=True)
    print('cases', len(out), 'models', MODELS)
    print('energy', json.dumps(rec['energy_status']))
    print('scope', json.dumps(rec['scope']), 'made', json.dumps(rec['made']))
    print('equal to MM1-v3.2 on every case', json.dumps(rec['equal_to_MM1-v3.2_everywhere']))
    print('factor ranges', json.dumps(fr))
    if not TEST:
        print(sha(OUTF), 'work/step2/fc-nominal.json')
    else:
        print('TEST RUN: output in', OUTF, '(not kept)')
