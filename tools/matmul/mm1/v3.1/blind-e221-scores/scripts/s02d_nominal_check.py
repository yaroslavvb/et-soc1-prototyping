#!/usr/bin/env python3
"""blind-e221 (Q235) step 2d: THE PROCEDURE CHECK. This lane's forecast code (s02b_forecast.py --nominal: one run a spec, at decl-e221's
declared NOMINAL conditions) against decl-e221's frozen nominal forecasts, field by field and bit for bit: work/decl/inputs/step2/fc-nominal.json
(a80943cb, a FROZEN.txt supporting file) and forecasts-nominal-e221.json (f7875611, frozen and posted). Every run of a case must give its
case's frozen forecast for every one of the 12 model columns; key sets compared too. Desk; stdlib.
Run: /usr/bin/python3 -I -B s02d_nominal_check.py <lane dir>      Writes work/step2/nominal-check.json.
"""
import collections
import hashlib
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
DEC = os.path.join(L, 'work', 'decl')
S2 = os.path.join(L, 'work', 'step2')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


PINS = {os.path.join(DEC, 'inputs', 'step2', 'fc-nominal.json'): 'a80943cb770dc7f5681671fdeadecea4c571270a0a6674ae1a6911ab8895756c',
        os.path.join(DEC, 'forecasts-nominal-e221.json'): 'f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '3a686510a43c453ac85588d5e649c7fe2e8554c3a98357e79047784e5165fe98'}
for p, h in PINS.items():
    assert sha(p) == h, p
FCN = json.load(open(os.path.join(DEC, 'inputs', 'step2', 'fc-nominal.json')))['cases']
FNJ = json.load(open(os.path.join(DEC, 'forecasts-nominal-e221.json')))['cases']
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
MINE = json.load(open(os.path.join(S2, 'fc-nominalcheck.json')))
assert MINE['nominal_selfcheck'] is True
rows = MINE['rows']
MODELS = MINE['models']
case_of = {r['id']: r['case'] for r in RL['runs']}
out = {'what': "blind-e221 step 2d: this lane's code at the declared nominal conditions against decl-e221's frozen nominal forecasts",
       'fc_nominalcheck_sha256': sha(os.path.join(S2, 'fc-nominalcheck.json')), 'against': {}}
for nm, FROZ in (('work/decl/inputs/step2/fc-nominal.json (a80943cb)', FCN), ('forecasts-nominal-e221.json (f7875611)', FNJ)):
    n_fields = n_diff = n_keydiff = 0
    diffs = []
    per_model = collections.Counter()
    seen_cases = set()
    for rid, o in rows.items():
        cid = case_of[rid]
        seen_cases.add(cid)
        fz = FROZ[cid]
        for mo in MODELS:
            a, b = o[mo], fz[mo]
            if set(a) != set(b):
                n_keydiff += 1
                if len(diffs) < 20:
                    diffs.append({'run': rid, 'model': mo, 'keys_only_mine': sorted(set(a) - set(b)), 'keys_only_frozen': sorted(set(b) - set(a))})
            for k in set(a) & set(b):
                n_fields += 1
                if a[k] != b[k]:
                    n_diff += 1
                    per_model[mo] += 1
                    if len(diffs) < 20:
                        diffs.append({'run': rid, 'model': mo, 'field': k, 'mine': a[k], 'frozen': b[k]})
    out['against'][nm] = {'runs': len(rows), 'cases_covered': len(seen_cases), 'frozen_cases': len(FROZ), 'fields_compared': n_fields,
                          'fields_differ': n_diff, 'model_dicts_with_other_keys': n_keydiff, 'differ_by_model': dict(per_model), 'first_diffs': diffs}
ok = all(v['fields_differ'] == 0 and v['model_dicts_with_other_keys'] == 0 and v['cases_covered'] == v['frozen_cases'] for v in out['against'].values())
out['VERDICT'] = ('SAME PROCEDURE: every field of every run equals its case\'s frozen nominal forecast, bit for bit' if ok else
                  'DIFFERENT: see first_diffs')
json.dump(out, open(os.path.join(S2, 'nominal-check.json'), 'w'), indent=1, sort_keys=True)
for k, v in out['against'].items():
    print(k, json.dumps({kk: vv for kk, vv in v.items() if kk != 'first_diffs'}))
    for d in v['first_diffs'][:5]:
        print('   ', json.dumps(d)[:300])
print(out['VERDICT'])
print(sha(os.path.join(S2, 'nominal-check.json')), 'work/step2/nominal-check.json')
sys.exit(0 if ok else 1)
