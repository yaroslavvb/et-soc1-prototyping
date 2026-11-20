#!/usr/bin/env python3
"""decl-e217 probe (code test only, never a forecast of record): call each frozen model once on a few E217 configurations at the nominal
footing, to learn the call forms (a new kind without its count; card 0's volts at 800 MHz; the walk's cost on the largest subset shape).
Nothing here is kept as a forecast. Run: /usr/bin/python3 -I -B p01_probe.py <lane dir>"""
import json
import os
import sys
import time
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
M2, n2 = U2.v2_model()
R = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
cases = R['cases']
pick = []
for want in ('gemmL1x1x1', 'gemmL10x12x11', 'gemmL4x8x8'):
    for c in cases:
        if c['arm'] == want and c not in pick:
            pick.append(c)
            break
for c in cases:
    if c['group_kind'] == 'S' and c['fmt'] == 'fp32':
        pick.append(c)
        break
for c in cases:
    if c['group_kind'] == 'S' and c['fmt'] == 'int8':
        pick.append(c)
        break
for c in cases:
    if c['group_kind'] == 'C':
        pick.append(c)
        break
for c in cases:
    if c['group_mask'] == 'MG' and c['card'] == 'aifoundry1 card 0':
        pick.append(c)
        break
NOM = {'aifoundry1 card 1': (600.0, 0.517, 60.0), 'aifoundry1 card 0': (800.0, None, 55.0)}
for c in pick:
    f, V, t0 = NOM[c['card']]
    spec = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind_energy'], 'mask': c['mask'], 'f': f, 'kernel': 'rgm136',
            'V': V, 't0_c': t0}
    print('---', c['case'])
    for nm, fn in (('v31', lambda s: M31.predict_many([s])[0]),
                   ('v3', lambda s: M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c'])),
                   ('v2', lambda s: U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'], 'f': s['f'],
                                                 'V_mv': None}))):
        try:
            p = fn(spec)
            print(nm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items() if k in ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'W_over_idle', 'V', 's_V', 'die_start_c', 'G_W', 'energy', 'minions', 'loop')},
                  'W_affine' in p, sorted(p.keys())[:40] if nm == 'v31' else '')
        except Exception as e:  # noqa: BLE001
            print(nm, 'EXCEPTION', type(e).__name__, str(e)[:300])
            traceback.print_exc(limit=2)
# the walk's cost
sys.path.insert(0, os.path.join(MM1, 'v3.2-terms', 'layout'))
import features_layout as FL  # noqa: E402
sub = sorted([c for c in cases if c['mask'] != '0xffffffff'], key=lambda c: -(c['MB'] * c['NB'] * c['KB']))
for c in sub[:2] + [x for x in sub if x['arm'] == 'gemmL1x1x1'][:1]:
    t0 = time.time()
    m = int(c['mask'], 16)
    f1 = FL.walk_feats('rgm136.gemmL', (c['MB'], c['NB'], c['KB']), m)
    print('walk', c['arm'], c['mask'], round(time.time() - t0, 2), 's', {k: v for k, v in f1.items() if k in ('n', 'fresh_lines_step', 'lines_req_step')})
print('subset configurations (arm, mask):', len({(c['arm'], c['mask']) for c in sub}), 'shapes', len({c['arm'] for c in sub}))
