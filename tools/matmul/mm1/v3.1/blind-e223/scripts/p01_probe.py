#!/usr/bin/env python3
"""decl-e223 probe p01 (MM1's domain, a code test; no forecast value is printed or kept): every E223 case (work/step1/runs-listed.json)
put to each frozen base predictor unchanged (MM1-v3.2 predict_many, MM1-v3.1 predict_many, MM1-v3 predict, MM1-v2 unread_v2_e212.call)
at the declared nominal footing (card 1 600 MHz 0.517 V die 60 C; the governed cards 800 MHz, the model's volts, die 55 C), and
MM1-v0 / MM1-v1 put the same arm token and mask where their predictors take one; records per case and model only: a form (finite time
fields, energy FORECAST or the model's own not-forecast word) or the exception's type and text. Desk; no device; no E223 datum (none
exists). Output: work/step1/domain-probe.json (counts and per-case status only). Run: /usr/bin/python3 -I -B p01_probe.py <lane dir>"""
import collections
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import mm1_v31  # noqa: E402
M31 = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
sys.path.insert(0, os.path.join(MM1, 'v3.2'))
import mm1_v32  # noqa: E402
M32 = mm1_v32.Model(json.load(open(os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json'))))
sys.path.insert(0, os.path.join(MM1, 'v3'))
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402
M3 = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))
M2, _ = U2.v2_model()
NOM = {'aifoundry1 card 1': {'f': 600.0, 'V': 0.517, 't0_c': 60.0}, 'aifoundry1 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0},
       'aifoundry2 card 0': {'f': 800.0, 'V': None, 't0_c': 55.0}}


def status(p):
    ok = all(isinstance(p.get(k), float) and math.isfinite(p[k]) for k in ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean'))
    en = 'FORECAST' if isinstance(p.get('W_affine'), dict) and math.isfinite(p.get('W_over_idle', float('nan'))) else str(p.get('energy', 'NOT FORECAST'))
    return {'time': 'FORM' if ok else 'NONFINITE', 'energy': en}


res = {}
cnt = collections.Counter()
specs = []
for c in RL['cases']:
    n = NOM[c['card']]
    specs.append({'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind_energy'], 'mask': c['mask'], 'f': n['f'],
                  'kernel': 'rgm136', 'V': n['V'], 't0_c': n['t0_c']})
for nm, fn in (('MM1-v3.2', lambda ss: M32.predict_many(ss)), ('MM1-v3.1', lambda ss: M31.predict_many(ss))):
    try:
        P = fn(specs)
        for c, p in zip(RL['cases'], P):
            res.setdefault(c['case'], {})[nm] = status(p)
    except Exception as e:  # noqa: BLE001  (then case by case)
        for c, s in zip(RL['cases'], specs):
            try:
                res.setdefault(c['case'], {})[nm] = status(fn([s])[0])
            except Exception as e2:  # noqa: BLE001
                res.setdefault(c['case'], {})[nm] = {'time': 'ERROR ' + type(e2).__name__ + ': ' + str(e2)[:100], 'energy': '-'}
for c, s in zip(RL['cases'], specs):
    try:
        res[c['case']]['MM1-v3'] = status(M3.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'],
                                                    t0_c=s['t0_c']))
    except Exception as e:  # noqa: BLE001
        res[c['case']]['MM1-v3'] = {'time': 'ERROR ' + type(e).__name__ + ': ' + str(e)[:100], 'energy': '-'}
    try:
        res[c['case']]['MM1-v2'] = status(U2.call(M2, {'card': s['card'], 'arm': s['arm'], 'fmt': s['fmt'], 'kind': s['kind'], 'mask': s['mask'],
                                                       'f': s['f'], 'V_mv': None}))
    except Exception as e:  # noqa: BLE001
        res[c['case']]['MM1-v2'] = {'time': 'ERROR ' + type(e).__name__ + ': ' + str(e)[:100], 'energy': '-'}
for c in RL['cases']:
    for nm, st in res[c['case']].items():
        cnt[f"{nm}|{c['class']}|{c['card']}|time={st['time'][:40]}|energy={st['energy'][:40]}"] += 1
out = {'what': 'decl-e223 p01: MM1 domain probe at the nominal footing (status only, no values)', 'python': sys.version.split()[0],
       'counts': dict(sorted(cnt.items())), 'cases': res}
json.dump(out, open(os.path.join(L, 'work', 'step1', 'domain-probe.json'), 'w'), indent=0, sort_keys=True)
for k, v in sorted(cnt.items()):
    print(v, k)
