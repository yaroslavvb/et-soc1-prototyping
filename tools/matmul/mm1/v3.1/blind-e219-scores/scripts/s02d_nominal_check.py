#!/usr/bin/env python3
"""blind-e219 (Q232) step 2d: THE PROCEDURE CHECK, before any E219 measurement is read. This lane's forecast code (s02b_forecast.py), run
at decl-e219's declared NOMINAL conditions (--nominal), must re-make decl-e219's frozen nominal forecasts (forecasts-nominal-e219.json,
d605db13): every in-domain run of a case against the case's frozen forecast, for all nine declared models, EVERY field the frozen record
holds (times, cycles, seconds a pass, W_A, W_B, W over idle at the model's own op time, J a pass, V, s_V, G_W, die, rest law, factors,
features, notes, kernels); and every out-of-domain run NOT FORECAST as its frozen case is. Prints the count of fields not bit-equal and the
worst relative difference. Desk; stdlib. blind-e217's s02d_nominal_check.py in form.
Run: /usr/bin/python3 -I -B s02d_nominal_check.py <lane dir>
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


assert sha(os.path.join(DEC, 'forecasts-nominal-e219.json')) == 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899'
assert sha(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')) == '0bd052dcbc277c9937c82b1c7dce04124e41deb1b57e21e4699271c8aa2d3376'
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e219.json')))
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
X = json.load(open(os.path.join(S2, 'fc-nominalcheck.json')))
MODELS = FCN['meta']['models']
assert X['models'] == MODELS
nfield = collections.Counter()
neq = collections.Counter()
worst = collections.defaultdict(float)
keydiff = collections.Counter()
ood = collections.Counter()
for r in RL['runs']:
    fz = FCN['cases'][r['case']]
    mine = X['rows'][r['id']]
    if r['domain'] != 'IN':
        ood['frozen OUT' if 'OUT_OF_DOMAIN' in fz else 'frozen NOT OUT'] += 1
        ood['mine OUT' if 'OUT_OF_DOMAIN' in mine else 'mine NOT OUT'] += 1
        continue
    for m in MODELS:
        a, b = mine[m], fz[m]
        if set(a) != set(b):
            keydiff[m] += 1
        for k in b:
            nfield[m] += 1
            if a.get(k) != b[k]:
                neq[f'{m}|{k}'] += 1
                if isinstance(b[k], float) and isinstance(a.get(k), float) and b[k] != 0:
                    worst[f'{m}|{k}'] = max(worst[f'{m}|{k}'], abs(a[k] / b[k] - 1))
res = {'fields_compared': dict(nfield), 'fields_not_bit_equal': dict(neq), 'worst_rel_diff': dict(worst), 'key_set_differs_runs': dict(keydiff),
       'out_of_domain': dict(ood), 'in_domain_runs': sum(1 for r in RL['runs'] if r['domain'] == 'IN'),
       'out_of_domain_runs': sum(1 for r in RL['runs'] if r['domain'] != 'IN'),
       'fc_nominalcheck_sha256': sha(os.path.join(S2, 'fc-nominalcheck.json'))}
ok = (sum(neq.values()) == 0 and sum(keydiff.values()) == 0 and ood.get('frozen NOT OUT', 0) == 0 and ood.get('mine NOT OUT', 0) == 0)
res['VERDICT'] = 'SAME PROCEDURE: every field bit-equal' if ok else 'DIFFERS: see the fields'
json.dump(res, open(os.path.join(S2, 'nominal-check.json'), 'w'), indent=1, sort_keys=True)
print('fields compared', sum(nfield.values()), json.dumps(dict(nfield)))
print('not bit-equal', sum(neq.values()), json.dumps(dict(neq))[:800], 'worst', json.dumps(dict(worst))[:400])
print('key sets differ (runs)', dict(keydiff), 'out of domain', dict(ood))
print(res['VERDICT'])
print(sha(os.path.join(S2, 'nominal-check.json')), 'work/step2/nominal-check.json')
