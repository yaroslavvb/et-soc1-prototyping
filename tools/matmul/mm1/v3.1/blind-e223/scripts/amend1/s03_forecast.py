#!/usr/bin/env python3
"""amend-e223 (Q239a) step 3: THE AMENDMENT'S NOMINAL FORECASTS (DECLARED-blind-e223-amendment-1, section h): every E223 case of the
declaration's list (decl-e223 work/step1/runs-listed.json, ed4595b1...: 695 cases, all rgm136 gemmL) forecast at the declaration's nominal
conditions (its section h: aifoundry1 card 1 600 MHz / 0.517 V / 60 C; aifoundry1 card 0 and aifoundry2 card 0 800 MHz / the model's own
volts / 55 C) by each amended model's frozen code unchanged, called as its land README says:
  'MM1-v3.2 + mesh' (Q238 mask-mesh, FROZEN.txt 487188c7...): mesh_term.Model(out/params-mesh.json, out/features-mesh.json).time_many
     (README section 6; MASK_MESH_REPO = this lane's lab copy): T; cycles an op = T x f; the counter's mean = cycles / MM1-v3.2's rho;
     seconds = ops x T; W over idle = MM1-v3.2's A + B / T (t forecast at this T);
  'MM1-v3.2 + AF4 + mesh' (by construction, no refit): scripts/compose_af4.py composed(specs, mesh) unchanged;
  'MM1-v3.2 + mask-ceiling' (Q238 mask-ceiling, a REPORTED reference, never a model candidate; posted FROZEN.txt 1649ba5b...):
     python3 -I -B mask_ceiling.py --points <points.json> --out <factors.json> (README section 7): MM1-v3.2's own row with T_op_us,
     cycles_per_op_wall and seconds_per_gemm times the factor, the counter's mean MM1-v3.2's, W over idle A_W + B_W_us / T_op_us.
MM1-v3.2's rows are made by mm1_v32.Model(out/mm1_v32_params.json).predict_many at the declaration's specs and CHECKED equal to the
declaration's frozen MM1-v3.2 column (forecasts-nominal-e223.json) at every case; each term's own base checked equal to MM1-v3.2's.
Run: /usr/bin/python3 -I -B s03_forecast.py <lane dir> [--test <scratch out dir>]   (--test: a code test before the amendment; not kept)"""
import collections
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
TEST = len(sys.argv) > 3 and sys.argv[2] == '--test'
OUT = os.path.dirname(L)
DECL = os.path.join(OUT, 'decl-e223')
LAB = os.path.join(L, 'work', 'lab')
MM1 = os.path.join(LAB, 'tools', 'matmul', 'mm1')
MESHD = os.path.join(MM1, 'v3.4-cands', 'mesh')
CEILD = os.path.join(MM1, 'v3.4-cands', 'mask-ceiling')
OUTD = os.path.abspath(sys.argv[3]) if TEST else os.path.join(L, 'work', 'step3')
os.makedirs(OUTD, exist_ok=True)
TZ = dict(os.environ, TZ='America/Los_Angeles')
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0},
       'aifoundry2 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}
MESH = 'MM1-v3.2 + mesh'
AF4MESH = 'MM1-v3.2 + AF4 + mesh'
CEIL = 'MM1-v3.2 + mask-ceiling'
MODELS = [MESH, AF4MESH, CEIL]
SHA = {'runs-listed': 'ed4595b10697daa0d1923d3fcaca2a04b295e6ccdd0dc2e87e5f77448330004d',
       'decl_json_fc': 'aeb174a7ea93a73b0baeac3d404fe57013694118dfb39e2963fe1fc388aa424f',
       'mesh_term.py': 'c8ee1ea9f044d1919712b081a32331f3f5080e043b35042432943124cb2366ac',
       'mesh_l3.py': 'fb591e1ed6a048b954bc4c007365cb765368f2eab26cbae79bd733a35d0274b1',
       'compose_af4.py': '04c28b969714d2b4a0e734f7a343383fc72708bb7ba7cedb5e9310723c7f2a47',
       'params-mesh.json': 'b4e3ff8e3fd07e1e76761e82a9d48428b0ad17f31d7c83d4c69ef433cb11293f',
       'features-mesh.json': '76ffbf216950818b9be9779967e45345c601160f1774d588f574add75582dff1',
       'mask_ceiling.py': '3674c568c34891f7b8ceedccf36fa5e6a4ba9d5c18669504e5aaef2f9af806f1',
       'params-mask-ceiling.json': 'f991b63787a4b3990328a8d1f232413f3b91ae0005df011d8a3a9c03c2fbe1d8',
       'r_common.py': '4a43e05482775f1599c2e05b39ba20d04c9d1b7eb3c0c4fa11d1b3adbb1771ce',
       'rf_core.py': '5f92ba5af3d2f3fde39e5d2e9bba493ace193611ee983a62a7315fbb72523c97',
       'f01_features.py': 'fd9e8df17b3e8b42d842090e68f78621117f706bdd60cf751160dcebd7ae3e18',
       'mm1_v32_params.json': 'c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab',
       'mm1_v32.py': 'e9a1ced7aa2fe50c66f9a1c389cb6c0064979be1d5f149a299f7a82e54ba2d5f'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def pst():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


rec = {'what': 'amend-e223 step 3: the amendment nominal forecasts', 'python': sys.version.split()[0], 'numpy': np.__version__,
       'test_run': TEST, 'started_pst': pst()}
# ------------------------------------------------------------------------------------------------ the frozen files, again, before any call
PATHS = {'runs-listed': os.path.join(DECL, 'work', 'step1', 'runs-listed.json'), 'decl_json_fc': os.path.join(DECL, 'forecasts-nominal-e223.json'),
         'mesh_term.py': os.path.join(MESHD, 'scripts', 'mesh_term.py'), 'mesh_l3.py': os.path.join(MESHD, 'scripts', 'mesh_l3.py'),
         'compose_af4.py': os.path.join(MESHD, 'scripts', 'compose_af4.py'), 'params-mesh.json': os.path.join(MESHD, 'out', 'params-mesh.json'),
         'features-mesh.json': os.path.join(MESHD, 'out', 'features-mesh.json'), 'mask_ceiling.py': os.path.join(CEILD, 'mask_ceiling.py'),
         'params-mask-ceiling.json': os.path.join(CEILD, 'params-mask-ceiling.json'), 'r_common.py': os.path.join(CEILD, 'scripts', 'r_common.py'),
         'rf_core.py': os.path.join(CEILD, 'scripts', 'rf_core.py'), 'f01_features.py': os.path.join(CEILD, 'scripts', 'f01_features.py'),
         'mm1_v32_params.json': os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json'), 'mm1_v32.py': os.path.join(MM1, 'v3.2', 'mm1_v32.py')}
for k, p in PATHS.items():
    assert sha(p) == SHA[k], (k, sha(p))
rec['frozen_files_checked'] = {k: SHA[k] for k in PATHS}
for d in (MESHD, CEILD, os.path.join(MM1, 'v3.2'), os.path.join(MM1, 'v3.1'), os.path.join(MM1, 'v3.3-cands', 'gemmlnc-af4')):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True)
    assert r.returncode == 0, d
    rec.setdefault('sha256sum_c', {})[os.path.relpath(d, MM1)] = sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))
if not TEST:
    for f in ('DECLARED-blind-e223-amendment-1.md', 'DECLARED-blind-e223-amendment-1.json'):
        rec.setdefault('amendment_sha256', {})[f] = sha(os.path.join(L, f))

# ------------------------------------------------------------------------------------------------ the models, as their READMEs call them
os.environ['MASK_MESH_REPO'] = LAB
os.environ['MASK_MESH_LANE'] = MESHD
sys.path.insert(0, os.path.join(MM1, 'v3.2'))
import mm1_v32  # noqa: E402
sys.path.insert(0, os.path.join(MESHD, 'scripts'))
import mesh_term as MT  # noqa: E402
import mesh_l3 as ML  # noqa: E402
assert os.path.normpath(MT.REPO) == os.path.normpath(LAB), MT.REPO
assert sys.modules['mm1_v32'].__file__ == os.path.join(MM1, 'v3.2', 'mm1_v32.py')
_argv = sys.argv
sys.argv = [os.path.join(MESHD, 'scripts', 'compose_af4.py'), MESHD]       # compose_af4 reads its lane folder from argv[1] at import
spec = importlib.util.spec_from_file_location('compose_af4', os.path.join(MESHD, 'scripts', 'compose_af4.py'))
CA = importlib.util.module_from_spec(spec)
sys.modules['compose_af4'] = CA
spec.loader.exec_module(CA)
sys.argv = _argv
assert CA.MT is MT and CA.mm1_v32 is mm1_v32
V32P = json.load(open(PATHS['mm1_v32_params.json']))
M32 = mm1_v32.Model(V32P)
MP = json.load(open(PATHS['params-mesh.json']))
MM = MT.Model(MP, PATHS['features-mesh.json'])
NCACHE0 = len(MM.F)
rec['candidates'] = {MESH: {'constants': MP['constants'], 'variant': MM.variant, 'maker': 'mesh_term.Model.time_many (mask-mesh README section 6)'},
                     AF4MESH: {'maker': 'compose_af4.composed(specs, mesh) (mask-mesh README section 6), no refit'},
                     CEIL: {'maker': 'mask_ceiling.py --points --out (mask-ceiling README section 7)', 'label': 'reference, REPORTED; never a model candidate'}}


def fields_raw(p, ops_pass, note=''):
    """decl-e223's s02b_nominal.fields_raw, verbatim: a base predictor's raw output -> the declared record"""
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


def rec_term(b, T, cyc_wall, cyc_mean, sec_model, A, B, extra):
    """the declared record (decl-e223's fields_z form) for a term on MM1-v3.2's row b at the same conditions"""
    o = {'T_op_us': float(T), 'cyc_wall': float(cyc_wall), 'cyc_mean': float(cyc_mean), 'ops_per_minion_pass': b['ops_per_minion_pass'],
         'sec_pass': b['ops_per_minion_pass'] * float(T) * 1e-6, 'sec_gemm_model': sec_model, 'f_mhz': b.get('f_mhz'), 'minions': b.get('minions')}
    if o['sec_gemm_model'] is not None:
        assert abs(o['sec_gemm_model'] / o['sec_pass'] - 1) < 1e-12, (o['sec_gemm_model'], o['sec_pass'])
    o.update({'energy': 'FORECAST', 'W_A': float(A), 'W_B': float(B), 'W_fc': float(A + B / T), 'V': b.get('V'), 's_V': b.get('s_V'),
              'G_W': b.get('G_W'), 'die_start_c': b.get('die_start_c')})
    o['J_over_idle_pass'] = o['W_fc'] * o['sec_pass']
    if b.get('rest_law_W') is not None:
        o['rest_law_W'] = b['rest_law_W']
    o['factor'] = o['T_op_us'] / b['T_op_us']
    o.update(extra)
    return o


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-300)


RL = json.load(open(PATHS['runs-listed']))
CASES_ALL = [dict(c, key=c['case']) for c in RL['cases']]
DFC = json.load(open(PATHS['decl_json_fc']))['cases']
FC0 = json.load(open(PATHS['features-mesh.json']))['configs']


def forecast_amend1(cases, cond, outd, check_decl=False):
    """THE AMENDMENT'S CALLERS: cases = [{'key', 'card', 'arm', 'fmt', 'kind_energy', 'mask', 'ops_per_minion_pass'}], cond[key] = {'f', 'V',
    't0_c'} -> ({key: {model: record}}, checks); each frozen code unchanged; each term on MM1-v3.2's forecast at the same conditions.
    check_decl: MM1-v3.2's rows checked equal to the declaration's frozen nominal column (the nominal footing only)."""
    worst = collections.defaultdict(float)
    specs = [{'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind_energy'], 'mask': c['mask'], 'f': float(cond[c['key']]['f']),
              'kernel': 'rgm136', 'V': cond[c['key']]['V'], 't0_c': cond[c['key']]['t0_c']} for c in cases]
    for s in specs:
        assert s['kind'] in ('zeros', 'ones', 'random') and s['arm'].startswith('gemmL') and not s['arm'].startswith('gemmLnc'), s
    r32 = M32.predict_many(specs)
    pts = [{'arm': s['arm'], 'kernel': 'rgm136', 'fmt': s['fmt'], 'mask': s['mask'], 'f': s['f']} for s in specs]
    t0 = time.time()
    Tm, fac, X = MM.time_many(pts)
    tm_s = round(time.time() - t0, 2)
    made_mesh = sorted(set(MM.F) - set(FC0))
    # check: the frozen walk re-makes cached configurations' features (up to 5 E223 configurations already in the frozen cache)
    cached = sorted({f"{p['arm']}|{MT.mask_hex(p['mask'])}" for p in pts if MT.is_layout_point(p)} & set(FC0))[:5]
    remade = {'configs': cached, 'fields_compared': 0, 'differ': []}
    for k in cached:
        arm, m = k.split('|')
        MB, NB, KB = ML.shape(arm)
        sim, nreq = ML.simulate(MB, NB, KB, m)
        x = ML.features(arm, m, sim)
        for f, v in x.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(FC0[k].get(f), (int, float)):
                remade['fields_compared'] += 1
                if not close(float(v), float(FC0[k][f]), 1e-12):
                    remade['differ'].append((k, f, v, FC0[k][f]))
    assert remade['fields_compared'] > 0 and not remade['differ'], remade
    comp = CA.composed(specs, MM)
    # the ceiling, by its own command line
    ptsj = os.path.join(outd, 'points-ceiling.json')
    facj = os.path.join(outd, 'factors-ceiling.json')
    json.dump(pts, open(ptsj, 'w'), indent=1)
    env = dict(os.environ, TMPDIR=os.path.join(L, 'work', 'tmp'))
    os.makedirs(env['TMPDIR'], exist_ok=True)
    r = subprocess.run(['/usr/bin/python3', '-I', '-B', PATHS['mask_ceiling.py'], '--selftest'], capture_output=True, text=True, env=env)
    selftest = {'rc': r.returncode, 'stdout': r.stdout.strip()[-400:]}
    assert r.returncode == 0, r.stdout + r.stderr
    t0 = time.time()
    r = subprocess.run(['/usr/bin/python3', '-I', '-B', PATHS['mask_ceiling.py'], '--points', ptsj, '--out', facj], capture_output=True, text=True,
                       env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    cl_s = round(time.time() - t0, 2)
    CF = json.load(open(facj))
    assert len(CF) == len(pts)
    out = collections.OrderedDict()
    for j, (c, s) in enumerate(zip(cases, specs)):
        ops = c['ops_per_minion_pass']
        b = fields_raw(r32[j], ops)
        if check_decl:
            d = DFC[c['key']]['MM1-v3.2']
            for k in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass', 'W_A', 'W_B', 'W_fc', 'rest_law_W'):
                assert close(b[k], d[k]), ('MM1-v3.2 differs from the frozen declaration column', k, c['key'], b[k], d[k])
                worst['MM1-v3.2 vs declaration'] = max(worst['MM1-v3.2 vs declaration'], abs(b[k] / d[k] - 1))
        o = collections.OrderedDict()
        # 'MM1-v3.2 + mesh'
        T = float(Tm[j])
        T0 = T / float(fac[j])
        assert close(T0, b['T_op_us']), ('mesh base differs from MM1-v3.2', c['key'], T0, b['T_op_us'])
        worst['mesh base vs MM1-v3.2'] = max(worst['mesh base vs MM1-v3.2'], abs(T0 / b['T_op_us'] - 1))
        rho = r32[j]['rho_wall_over_mean']
        assert close(b['cyc_wall'] / b['cyc_mean'], rho, 1e-9), ('rho', c['key'])
        insc = bool(MT.is_layout_point(pts[j]))
        if not insc:
            assert float(fac[j]) == 1.0, ('mesh acts off its scope', c['key'])
        o[MESH] = rec_term(b, T, T * s['f'], T * s['f'] / rho, None, b['W_A'], b['W_B'],
                           {'in_scope_mesh': insc, 'features': [float(v) for v in X[j]]})
        # 'MM1-v3.2 + AF4 + mesh' (compose_af4.composed)
        q = comp[j]
        assert close(q['MM1-v3.2_T_op_us'], b['T_op_us']) and q['AF4_dW_at_v32_t'] == 0.0 and close(q['A_W'], b['W_A']) and close(q['B_W_us'], b['W_B'])
        o[AF4MESH] = rec_term(b, q['T_op_us'], q['cycles_per_op_wall'], q['cycles_per_op_mean'], q['seconds_per_gemm'], q['A_W'], q['B_W_us'],
                              {'in_scope_mesh': insc, 'AF4_dW_at_v32_t': q['AF4_dW_at_v32_t'], 'how': 'compose_af4.composed: AF4 0 off gemmLnc'})
        assert close(o[AF4MESH]['W_fc'], q['W_over_idle_at_t_forecast'], 1e-12)
        for k in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass', 'W_fc'):
            assert close(o[AF4MESH][k], o[MESH][k]), ('AF4 + mesh differs from mesh at a gemmL case', k, c['key'])
            worst['AF4 + mesh vs mesh'] = max(worst['AF4 + mesh vs mesh'], abs(o[AF4MESH][k] / o[MESH][k] - 1))
        # 'MM1-v3.2 + mask-ceiling' (reference): MM1-v3.2's row, T, wall cycles and seconds times the factor; the counter's mean MM1-v3.2's
        cf = CF[j]
        assert cf['arm'] == s['arm'] and int(str(cf['mask']), 16) == int(str(s['mask']), 16) and float(cf['f']) == s['f'], ('ceiling row order', j)
        g = float(cf['factor'])
        if not cf['in_scope']:
            assert g == 1.0
        sg = r32[j].get('seconds_per_gemm')
        o[CEIL] = rec_term(b, b['T_op_us'] * g, b['cyc_wall'] * g, b['cyc_mean'], (sg * g) if sg is not None else None, b['W_A'], b['W_B'],
                           {'in_scope_ceiling': bool(cf['in_scope']), 'ln_factor': float(cf['ln_factor']),
                            'cyc_mean_note': "MM1-v3.2's own counter mean (the reference forecasts no counter mean: its README)"})
        for nm, x in o.items():
            assert all(isinstance(x[f], float) and math.isfinite(x[f]) for f in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass', 'W_fc')), (nm, c['key'])
            assert abs((x['W_A'] + x['W_B'] / x['T_op_us']) / x['W_fc'] - 1) < 1e-9, ('affine', nm, c['key'])
        out[c['key']] = o

    checks = {'worst_relative': dict(worst), 'mesh_features_remade_from_the_frozen_walk': {'configs': remade['configs'],
              'fields_compared': remade['fields_compared'], 'differ': len(remade['differ'])}, 'mesh_cache_frozen_configs': len(FC0),
              'mesh_configs_made_by_the_frozen_walk': len(made_mesh), 'mesh_configs_made': made_mesh, 'ceiling_selftest': selftest,
              'mesh_time_many_s': tm_s, 'ceiling_run_s': cl_s, 'factors_ceiling_sha256': sha(facj)}
    return out, checks


if __name__ == '__main__':
    CASES = CASES_ALL[::23] if TEST else CASES_ALL
    out, chk = forecast_amend1(CASES, {c['key']: NOM[c['card']] for c in CASES}, OUTD, check_decl=True)
    rec['mesh_time_many_s'] = chk['mesh_time_many_s']
    rec['ceiling_run_s'] = chk['ceiling_run_s']
    rec['ceiling_selftest'] = chk['ceiling_selftest']
    rec['nominal'] = NOM
    rec['models'] = MODELS
    rec['n_cases'] = len(out)
    rec['checks'] = {k: v for k, v in chk.items() if k != 'mesh_configs_made'}
    rec['made_keys'] = {'mesh_configs_made': chk['mesh_configs_made']}
    rec['scope'] = {'mesh (subset masks of rgm136 gemmL)': sum(1 for v in out.values() if v[MESH]['in_scope_mesh']),
                    'mask-ceiling (rgm136 gemmL, MB x NB >= 2, subset)': sum(1 for v in out.values() if v[CEIL]['in_scope_ceiling'])}
    fr = {}
    for m in MODELS:
        xs = [v[m]['factor'] for v in out.values()]
        fr[m] = [min(xs), max(xs)]
    rec['factor_ranges'] = fr
    rec['ended_pst'] = pst()
    rec['cases'] = out
    OUTF = os.path.join(OUTD, 'fc-amend1.json')
    json.dump(rec, open(OUTF, 'w'), indent=1, sort_keys=True)
    print('checks', json.dumps(rec['checks']))
    print('scope', json.dumps(rec['scope']), 'cases', len(out), 'mesh time_many s', rec['mesh_time_many_s'], 'ceiling s', rec['ceiling_run_s'])
    print('ceiling selftest', rec['ceiling_selftest'])
    print('factor ranges', json.dumps(fr))
    print('sha256sum -c', json.dumps(rec['sha256sum_c']))
    if not TEST:
        print(sha(OUTF), 'work/step3/fc-amend1.json')
    else:
        print('TEST RUN: output in', OUTD, '(not kept)')
