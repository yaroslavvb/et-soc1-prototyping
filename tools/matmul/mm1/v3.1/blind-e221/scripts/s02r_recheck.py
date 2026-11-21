#!/usr/bin/env python3
"""decl-e221 (Q235) recheck of step 2 (after the freeze; changes nothing frozen): each base model's nominal forecasts re-made in a process of
its own (only that model imported; MM1-v3.2+L3S with MM1-v3.2 and its maker's module only) and compared field by field with the frozen
forecasts-nominal-e221.json; the composed forms (the contention term, 'both', the four controls on MM1-v3.1; posimb on MM1-v3.2) re-derived
from the frozen base fields and factors. decl-e219's s02r_recheck.py in form (E221 has no out-of-domain case). Run per model, then 'compare':
  /usr/bin/python3 -I -B s02r_recheck.py <lane dir> <v32|v31|v3|v2|l3s|compare>"""
import hashlib
import importlib.util
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
CANDS = os.path.join(L, 'work', 'cands')
OUTD = os.path.join(L, 'work', 'recheck')
os.makedirs(OUTD, exist_ok=True)
FJ = os.path.join(L, 'forecasts-nominal-e221.json')
assert hashlib.sha256(open(FJ, 'rb').read()).hexdigest() == 'f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831'
F = json.load(open(FJ))
NOM = F['meta']['nominal_conditions']
CASES = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))['cases']


def spec(c, kind):
    n = NOM[c['card']]
    return {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': kind, 'mask': c['mask'], 'f': n['f'], 'kernel': 'rgm136',
            'V': n['V'], 't0_c': n['t0_c']}


def pick(p, ops):
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean'], 'sec_pass': ops * p['T_op_us'] * 1e-6}
    if isinstance(p.get('W_affine'), dict):
        o.update({'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle']})
    return o


if MODE in ('v32', 'l3s'):
    sys.path.insert(0, os.path.join(MM1, 'v3.2'))
    import mm1_v32  # noqa: E402
    P32 = json.load(open(os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json')))
    if MODE == 'v32':
        M = mm1_v32.Model(P32)
    else:
        sys.path.insert(0, os.path.join(CANDS, 'l3-edge', 'scripts'))
        spec_ = importlib.util.spec_from_file_location('term_l3s', os.path.join(CANDS, 'l3-edge', 'scripts', 'term_l3s.py'))
        TL = importlib.util.module_from_spec(spec_)
        sys.modules['term_l3s'] = TL
        spec_.loader.exec_module(TL)
        cache = json.load(open(os.path.join(CANDS, 'l3-edge', 'work', 'feature', 'l3s_cache.json')))
        cache.update(json.load(open(os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')))['l3s']['computed'])
        lam = float(json.load(open(os.path.join(CANDS, 'l3-edge', 'work', 'fit', 'fit-l3s.json')))['lam_all'])
        M = TL.ModelL3S(P32, lam, cache)
    P = M.predict_many([spec(c, c['kind_energy']) for c in CASES])
    json.dump({'in': {c['case']: pick(p, c['ops_per_minion_pass']) for c, p in zip(CASES, P)}}, open(os.path.join(OUTD, MODE + '.json'), 'w'))
elif MODE == 'v31':
    sys.path.insert(0, os.path.join(MM1, 'v3.1'))
    import mm1_v31  # noqa: E402
    M = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
    P = M.predict_many([spec(c, c['kind_energy']) for c in CASES])
    json.dump({'in': {c['case']: pick(p, c['ops_per_minion_pass']) for c, p in zip(CASES, P)}}, open(os.path.join(OUTD, 'v31.json'), 'w'))
elif MODE == 'v3':
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import mm1_v3  # noqa: E402
    M = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
    out = {'in': {}}
    for c in CASES:
        s = spec(c, c['kind_energy'])
        out['in'][c['case']] = pick(M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']),
                                    c['ops_per_minion_pass'])
    json.dump(out, open(os.path.join(OUTD, 'v3.json'), 'w'))
elif MODE == 'v2':
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import unread_v2_e212 as U2  # noqa: E402
    M2, _ = U2.v2_model()
    out = {'in': {}}
    for c in CASES:
        s = spec(c, c['kind_energy'])
        out['in'][c['case']] = pick(U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'],
                                                 'f': s['f'], 'V_mv': None}), c['ops_per_minion_pass'])
    json.dump(out, open(os.path.join(OUTD, 'v2.json'), 'w'))
else:
    diff = {}
    n = 0
    for mdl, fn in (('MM1-v3.2', 'v32.json'), ('MM1-v3.1', 'v31.json'), ('MM1-v3', 'v3.json'), ('MM1-v2', 'v2.json'), ('MM1-v3.2+L3S', 'l3s.json')):
        R = json.load(open(os.path.join(OUTD, fn)))
        d = 0
        for case, o in R['in'].items():
            fz = F['cases'][case][mdl]
            for k, v in o.items():
                n += 1
                if fz.get(k) != v:
                    d += 1
            if ('W_fc' in fz) != ('W_fc' in o):
                d += 1
        diff[mdl] = d
    dc = 0
    for case, o in F['cases'].items():
        for basem, ms in (('MM1-v3.1', ('v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1', 'ctrl F1-layout-blind')),
                          ('MM1-v3.2', ('MM1-v3.2+posimb',))):
            b = o[basem]
            for m in ms:
                x = o[m]
                n += 1
                gm = x.get('g_mean', x['factor'])
                if x['T_op_us'] != b['T_op_us'] * x['factor'] or x['cyc_wall'] != b['cyc_wall'] * x['factor'] or x['cyc_mean'] != b['cyc_mean'] * gm:
                    dc += 1
                if b['energy'] == 'FORECAST' and x['W_fc'] != b['W_A'] + b['W_B'] / x['T_op_us']:
                    dc += 1
    res = {'fields_compared': n, 'differences_by_model': diff, 'composed_differences': dc,
           'pass': all(v == 0 for v in diff.values()) and dc == 0}
    json.dump(res, open(os.path.join(OUTD, 'recheck.json'), 'w'), indent=1)
    print(json.dumps(res))
    print(hashlib.sha256(open(os.path.join(OUTD, 'recheck.json'), 'rb').read()).hexdigest(), 'work/recheck/recheck.json')
