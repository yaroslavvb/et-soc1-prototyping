#!/usr/bin/env python3
"""decl-e219 (Q232) recheck of step 2 (after the freeze; changes nothing frozen): each base model's nominal forecasts re-made in a process of
its own (only that model imported) and compared field by field with the frozen forecasts-nominal-e219.json; the composed forms (the
contention term, 'both', the four controls) re-derived from the frozen MM1-v3.1 fields and factors; every out-of-domain case re-checked to
raise in every base model (no form). decl-e217's s02r_recheck.py in form. Run per model, then 'compare':
  /usr/bin/python3 -I -B s02r_recheck.py <lane dir> <v31|v3|v2|compare>"""
import hashlib
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
OUTD = os.path.join(L, 'work', 'recheck')
os.makedirs(OUTD, exist_ok=True)
FJ = os.path.join(L, 'forecasts-nominal-e219.json')
assert hashlib.sha256(open(FJ, 'rb').read()).hexdigest() == 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899'
F = json.load(open(FJ))
NOM = F['meta']['nominal_conditions']
ALL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))['cases']
CASES = [c for c in ALL if c['domain'] == 'IN']
OUTC = [c for c in ALL if c['domain'] == 'OUT']


def spec(c, kind, arm=None):
    n = NOM[c['card']]
    return {'card': c['card'], 'arm': arm or c['arm'], 'fmt': c['fmt'], 'kind': kind, 'mask': c['mask'], 'f': n['f'], 'kernel': 'rgm136',
            'V': n['V'], 't0_c': n['t0_c']}


def pick(p, ops):
    o = {'T_op_us': p['T_op_us'], 'cyc_wall': p['cycles_per_op_wall'], 'cyc_mean': p['cycles_per_op_mean'], 'sec_pass': ops * p['T_op_us'] * 1e-6}
    if isinstance(p.get('W_affine'), dict):
        o.update({'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle']})
    return o


def raises(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        return type(e).__name__
    return None


if MODE == 'v31':
    sys.path.insert(0, os.path.join(MM1, 'v3.1'))
    import mm1_v31  # noqa: E402
    M = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
    P = M.predict_many([spec(c, c['kind_energy']) for c in CASES])
    out = {'in': {c['case']: pick(p, c['ops_per_minion_pass']) for c, p in zip(CASES, P)},
           'out': {c['case']: raises(lambda c=c: M.predict_many([spec(c, c['kind_energy'], arm=c['token'])])) for c in OUTC}}
    json.dump(out, open(os.path.join(OUTD, 'v31.json'), 'w'))
elif MODE == 'v3':
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import mm1_v3  # noqa: E402
    M = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
    out = {'in': {}, 'out': {}}
    for c in CASES:
        s = spec(c, c['kind_energy'])
        out['in'][c['case']] = pick(M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']),
                                    c['ops_per_minion_pass'])
    for c in OUTC:
        s = spec(c, c['kind_energy'], arm=c['token'])
        out['out'][c['case']] = raises(lambda s=s: M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136',
                                                             V=s['V'], t0_c=s['t0_c']))
    json.dump(out, open(os.path.join(OUTD, 'v3.json'), 'w'))
elif MODE == 'v2':
    sys.path.insert(0, os.path.join(MM1, 'v3'))
    import unread_v2_e212 as U2  # noqa: E402
    M2, _ = U2.v2_model()
    out = {'in': {}, 'out': {}}
    for c in CASES:
        s = spec(c, c['kind_energy'])
        out['in'][c['case']] = pick(U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'],
                                                 'f': s['f'], 'V_mv': None}), c['ops_per_minion_pass'])
    for c in OUTC:
        s = spec(c, c['kind_energy'], arm=c['token'])
        out['out'][c['case']] = raises(lambda s=s: U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'],
                                                                'mask': s['mask'], 'f': s['f'], 'V_mv': None}))
    json.dump(out, open(os.path.join(OUTD, 'v2.json'), 'w'))
else:
    diff = {}
    out_raise = {}
    n = 0
    for mdl, fn in (('MM1-v3.1', 'v31.json'), ('MM1-v3', 'v3.json'), ('MM1-v2', 'v2.json')):
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
        out_raise[mdl] = {'cases': len(R['out']), 'raised': sum(1 for v in R['out'].values() if v), 'kinds': sorted({v for v in R['out'].values() if v})}
    # the composed forms from the frozen MM1-v3.1 fields: time x factor; W = A + B / (T x factor)
    dc = 0
    for case, o in F['cases'].items():
        if 'OUT_OF_DOMAIN' in o:
            continue
        b = o['MM1-v3.1']
        for m in ('v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1', 'ctrl F1-layout-blind'):
            x = o[m]
            n += 1
            if x['T_op_us'] != b['T_op_us'] * x['factor'] or x['cyc_wall'] != b['cyc_wall'] * x['factor']:
                dc += 1
            if b['energy'] == 'FORECAST' and x['W_fc'] != b['W_A'] + b['W_B'] / x['T_op_us']:
                dc += 1
    res = {'fields_compared': n, 'differences_by_model': diff, 'composed_differences': dc, 'out_of_domain_raise': out_raise,
           'pass': all(v == 0 for v in diff.values()) and dc == 0 and all(v['raised'] == v['cases'] for v in out_raise.values())}
    json.dump(res, open(os.path.join(OUTD, 'recheck.json'), 'w'), indent=1)
    print(json.dumps(res))
