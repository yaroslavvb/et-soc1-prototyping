#!/usr/bin/env python3
"""decl-e219 probe p01 (a code test, nothing kept): which E219 arm tokens each frozen MM1 accepts, by calling each predictor unchanged on
one spec per token class (aifoundry1 card 1, 600 MHz, fp32 zeros, full chip). Desk; no device; no E219 datum (none exists).
Run: /usr/bin/python3 -I -B p01_probe.py <lane dir>"""
import json
import os
import sys
import traceback

L = os.path.abspath(sys.argv[1])
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import mm1_v31  # noqa: E402
M31 = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
sys.path.insert(0, os.path.join(MM1, 'v3'))
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402
M3 = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
M2, _ = U2.v2_model()
TOK = ['gemmL1x1x1', 'gemmL4x3x3', 'gemmc1', 'gemmc4s', 'gemmc8s', 'gemmc8', 'gemmc16', 'gemmc16s', 'gemmc16r4', 'gemmc16r32',
       'gemmc16r4s', 'gemmc2', 'gemmc2r8', 'gemmc2s', 'gemmc1r8', 'gemmc8r8', 'gemmc32r8', 'gemmh1', 'gemmh16r8', 'gemm1', 'gemm16r8',
       'mm16', 'mm128', 'tenb']
res = {}
for tok in TOK:
    row = {}
    for nm, fn in (('MM1-v3.1', lambda a, c: M31.predict_many([{'card': c, 'arm': a, 'fmt': 'fp32', 'kind': 'zeros', 'mask': '0xffffffff',
                                                                   'f': 600.0 if c.endswith('1') else 800.0, 'kernel': 'rgm136', 'V': None,
                                                                   't0_c': 50.0}])[0]),
                   ('MM1-v3', lambda a, c: M3.predict(c, a, 'fp32', 'zeros', '0xffffffff', 600.0 if c.endswith('1') else 800.0, kernel='rgm136',
                                                       V=None, t0_c=50.0)),
                   ('MM1-v2', lambda a, c: U2.call(M2, {'card': c, 'arm': a, 'fmt': 'fp32', 'kind': 'zeros', 'mask': '0xffffffff',
                                                        'f': 600.0 if c.endswith('1') else 800.0, 'V_mv': None}))):
        for card in ('aifoundry1 card 1', 'aifoundry1 card 0'):
            try:
                p = fn(tok, card)
                row[f'{nm}|{card[-6:]}'] = {'cyc_wall': round(p['cycles_per_op_wall'], 2), 'cyc_mean': round(p['cycles_per_op_mean'], 2),
                                            'W': (round(p['W_over_idle'], 3) if isinstance(p.get('W_over_idle'), float) else p.get('energy')),
                                            'kernel': p.get('kernel'), 'loop': p.get('loop'), 'ops': p.get('ops_per_minion_per_gemm')}
            except Exception as e:  # noqa: BLE001
                row[f'{nm}|{card[-6:]}'] = 'ERROR ' + type(e).__name__ + ': ' + str(e)[:80]
    res[tok] = row
for k, v in res.items():
    print(k)
    for m, x in v.items():
        print('   ', m, json.dumps(x))
