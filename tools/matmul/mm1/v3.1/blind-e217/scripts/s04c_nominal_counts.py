#!/usr/bin/env python3
"""decl-e217 (Q228) step 4c: group S's NOMINAL energy forecasts with counts-e217 (the declaration's sections e and h), made after the counts
and before any E217 measurement is read: the frozen predictors unchanged, called at the same nominal conditions as step 2 (s02b_nominal.py),
with, added in memory as data only (unread-e214's form): counts-e217's rows (cnt/counts/counts-fp32-gemm-states.json and
counts-fp16-int8-launch.json) in MM1-v3.1's E210C31 / SWT31 and, with 3e8991d0's rows, in MM1-v3's E210C / SWT (no key colliding: asserted);
phi for the 21 new kinds (the declaration's table: kinds_v3.phi over each tile file) in each model's memo; THE DECLARED GATE for the four
zero-row tiles (gt125, gt25, gt875, h_gt25: (g_op, g_lane, g8) = (the all-zero A-row share, 0, 0)) by wrapping gate_shares; the frozen
literal (0, 0, 0) for those four REPORTED beside, and (REPORTED, added after the counts showed it, before any E217 datum) the gate the
count implies: g_op the all-zero A-row share, g_lane the rest of the count's gated share, (1 - v) - g_op (v the count's valid share, which
the frozen code passes to gate_shares). Every other case is unchanged from step 2 (checked: re-made bit for bit for 8 of them).
Models with energy here: MM1-v3.1, MM1-v3, 'v3.1+contention', 'v3.1+both' and the four controls (MM1-v3.1's affine at their own op times);
MM1-v2 prices no new kind (NOT FORECAST). Each model runs in its own process (unread-e214's form: MM1-v3.1's energy_v31 imports
energy_v3 itself, so one model's in-memory tables must never reach the other's): modes v31, v3, then merge.
Run: /usr/bin/python3 -I -B s04c_nominal_counts.py <lane dir> <v31|v3|merge>"""
import collections
import csv
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
assert MODE in ('v31', 'v3', 'merge'), MODE
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
CNT = os.path.join(L, 'cnt', 'counts')
OUTD = os.path.join(L, 'work', 'step4')
os.makedirs(OUTD, exist_ok=True)
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(os.path.join(L, 'DECLARED-blind-e217.json')) == '633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7'
assert sha(os.path.join(L, 'forecasts-nominal-e217.json')) == '611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c'
DECL = json.load(open(os.path.join(L, 'DECLARED-blind-e217.json')))
FCN = json.load(open(os.path.join(L, 'forecasts-nominal-e217.json')))
PHI = DECL['e_switch']['phi']
GATE = DECL['e_switch']['gate_values']
NOM = FCN['meta']['nominal_conditions']
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
CASES = RL['cases']
CASE = {c['case']: c for c in CASES}
SC = [c for c in CASES if c['group_kind'] == 'S']
CTL = [c for c in CASES if c['group_kind'] == 'K'][:8]
CNTF = ('counts-fp32-gemm-states.json', 'counts-fp16-int8-launch.json', 'SHA256SUMS')


def spec(c, kind):
    n = NOM[c['card']]
    return {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': kind, 'mask': c['mask'], 'f': n['f'], 'kernel': 'rgm136',
            'V': n['V'], 't0_c': n['t0_c']}


def gate_wrap(EN):
    orig = EN.gate_shares

    def g(fmt, kind, v):
        k = f'{fmt}|{kind}'
        if k in GATE:
            return float(GATE[k]['g_op']), 0.0, 0.0
        return orig(fmt, kind, v)
    return orig, g


def gate_wrap_count(EN):
    orig = EN.gate_shares

    def g(fmt, kind, v):
        k = f'{fmt}|{kind}'
        if k in GATE:
            r = float(GATE[k]['g_op'])
            return r, max(0.0, (1.0 - float(v)) - r), 0.0
        return orig(fmt, kind, v)
    return g


def efields(p):
    if not isinstance(p.get('W_affine'), dict):
        return {'energy': p.get('energy', 'NOT FORECAST')}
    o = {'energy': 'FORECAST', 'W_A': p['W_affine']['A_W'], 'W_B': p['W_affine']['B_W_us'], 'W_fc': p['W_over_idle'], 'T_op_us': p['T_op_us'],
         'sec_gemm': p['seconds_per_gemm'], 'switches': p.get('switches'), 'phi': p.get('phi'), 'phi_rule': p.get('phi_rule')}
    rl = p.get('rest_law')
    if isinstance(rl, dict):
        o['rest_law_W'] = rl.get('P_rest_W')
    return o


if MODE in ('v31', 'v3'):
    C32n = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
    C16n = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
    added = []
    if MODE == 'v31':
        sys.path.insert(0, os.path.join(MM1, 'v3.1'))
        import energy_v31 as EV  # noqa: E402
        import mm1_v31  # noqa: E402
        for sh in ('S1', 'S2'):
            for k, r in C32n[sh].items():
                assert k not in EV.E210C31[sh], (sh, k)
                EV.E210C31[sh][k] = r
                added.append(f'E210C31[{sh}][{k}]')
        for k, r in C16n.items():
            assert k not in EV.SWT31, k
            EV.SWT31[k] = r
            added.append(f'SWT31[{k}]')
        for key, v in PHI.items():
            fmt, kind = key.split('|', 1)
            for kb1 in (True, False):
                assert (fmt, kind, kb1) not in EV._PHI31
                EV._PHI31[(fmt, kind, kb1)] = (float(v['phi']), "kinds_v3.phi over E217's registered tile file (decl-e217's declaration)")
        M = mm1_v31.Model(json.load(open(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))))
        EN = EV.EN

        def run(specs):
            return M.predict_many(specs)
        name = 'MM1-v3.1'
    else:
        sys.path.insert(0, os.path.join(MM1, 'v3'))
        import energy_v3 as EN  # noqa: E402
        import mm1_v3  # noqa: E402
        V31C = os.path.join(MM1, 'v3.1', 'counts')
        C32o = json.load(open(os.path.join(V31C, 'counts-fp32-gemm-states.json')))['shapes']
        C16o = json.load(open(os.path.join(V31C, 'counts-fp16-int8-launch.json')))['rows']
        for tag, (A32, A16) in (('3e8991d0', (C32o, C16o)), ('counts-e217', (C32n, C16n))):
            for sh in ('S1', 'S2'):
                for k, r in A32[sh].items():
                    assert k not in EN.E210C[sh], (sh, k)
                    EN.E210C[sh][k] = r
                    added.append(f'{tag} E210C[{sh}][{k}]')
            for k, r in A16.items():
                assert k not in EN.SWT, k
                EN.SWT[k] = r
                added.append(f'{tag} SWT[{k}]')
        for key, v in PHI.items():
            fmt, kind = key.split('|', 1)
            for kb1 in (True, False):
                assert EN._PHI.get((fmt, kind, kb1)) is None
                EN._PHI[(fmt, kind, kb1)] = float(v['phi'])
        M = mm1_v3.Model(json.load(open(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))))

        def run(specs):
            return [M.predict(s['card'], s['arm'], s['fmt'], s['kind'], s['mask'], s['f'], kernel='rgm136', V=s['V'], t0_c=s['t0_c']) for s in specs]
        name = 'MM1-v3'
    orig, wrapped = gate_wrap(EN)
    EN.gate_shares = wrapped
    # check: the lab's kinds unchanged from step 2, bit for bit
    chk = []
    for c, p in zip(CTL, run([spec(c, c['kind_energy']) for c in CTL])):
        old = FCN['cases'][c['case']][name]
        chk.append({'case': c['case'], 'W_equal': p['W_over_idle'] == old['W_fc'], 'T_equal': p['T_op_us'] == old['T_op_us']})
    assert all(x['W_equal'] and x['T_equal'] for x in chk), chk
    res = {'model': name, 'python': sys.version.split()[0], 'rows_added': added, 'check_unchanged_K': chk, 'declared': {}, 'literal': {}}
    for c, p in zip(SC, run([spec(c, c['kind_energy']) for c in SC])):
        e = efields(p)
        assert p['T_op_us'] == FCN['cases'][c['case']][name]['T_op_us']
        res['declared'][c['case']] = e
    EN.gate_shares = orig
    zr = [c for c in SC if f"{c['fmt']}|{c['kind']}" in GATE]
    for c, p in zip(zr, run([spec(c, c['kind_energy']) for c in zr])):
        res['literal'][c['case']] = efields(p)
    EN.gate_shares = gate_wrap_count(EN)
    res['countgate'] = {}
    for c, p in zip(zr, run([spec(c, c['kind_energy']) for c in zr])):
        res['countgate'][c['case']] = efields(p)
    EN.gate_shares = wrapped
    res['counts_sha256'] = {n: sha(os.path.join(CNT, n)) for n in CNTF if os.path.exists(os.path.join(CNT, n))}
    json.dump(res, open(os.path.join(OUTD, f'fc-counts-{MODE}.json'), 'w'), indent=1, sort_keys=True)
    print(name, 'rows added', len(added), 'group S', len(res['declared']), 'energy', dict(collections.Counter(v['energy'] == 'FORECAST' for v in res['declared'].values())),
          'literal (REPORTED)', len(res['literal']))
    print(sha(os.path.join(OUTD, f'fc-counts-{MODE}.json')), f'work/step4/fc-counts-{MODE}.json')
    sys.exit(0)

# ---------------------------------------------------------------- merge: the two models + the composed forms, the files
R31 = json.load(open(os.path.join(OUTD, 'fc-counts-v31.json')))
R3 = json.load(open(os.path.join(OUTD, 'fc-counts-v3.json')))
C32n = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16n = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
out = collections.OrderedDict()
for c in SC:
    base = FCN['cases'][c['case']]
    o = collections.OrderedDict()
    e31 = R31['declared'][c['case']]
    o['MM1-v3.1'] = e31
    o['MM1-v3'] = R3['declared'][c['case']]
    for m in ('v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1', 'ctrl F1-layout-blind'):
        b = base[m]
        if e31['energy'] == 'FORECAST':
            W = e31['W_A'] + e31['W_B'] / b['T_op_us']
            o[m] = {'energy': 'FORECAST', 'W_A': e31['W_A'], 'W_B': e31['W_B'], 'W_fc': W, 'T_op_us': b['T_op_us'], 'sec_gemm': b['sec_gemm'],
                    'factor': b['factor']}
        else:
            o[m] = {'energy': e31['energy']}
    o['MM1-v2'] = {'energy': base['MM1-v2']['energy']}
    if c['case'] in R31['literal']:
        o['MM1-v3.1 literal gate (REPORTED)'] = R31['literal'][c['case']]
        o['MM1-v3 literal gate (REPORTED)'] = R3['literal'][c['case']]
        o['MM1-v3.1 count gate (REPORTED)'] = R31['countgate'][c['case']]
        o['MM1-v3 count gate (REPORTED)'] = R3['countgate'][c['case']]
    o['gate'] = GATE.get(f"{c['fmt']}|{c['kind']}", {'g_op': None, 'note': "the frozen code's own gate_shares (no zero-row tile)"})
    out[c['case']] = o
vs = {}
for key in GATE:
    fmt, kind = key.split('|', 1)
    rows = ({sh: C32n[sh].get(kind, {}).get('valid_slots') for sh in ('S1', 'S2')} if fmt == 'fp32'
            else {'launch': (C16n.get(f'{fmt}.{kind}') or {}).get('valid_share_v')})
    vs[key] = {'declared_g_op': GATE[key]['g_op'], 'count_valid_share': rows}
rec = {'what': "decl-e217 step 4c: group S's nominal energy forecasts with counts-e217 (the declaration's sections e and h)",
       'made_pst': subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip(),
       'python': sys.version.split()[0], 'numpy': np.__version__, 'nominal_conditions': NOM,
       'declaration_json_sha256': sha(os.path.join(L, 'DECLARED-blind-e217.json')),
       'forecasts_nominal_json_sha256': sha(os.path.join(L, 'forecasts-nominal-e217.json')),
       'counts_sha256': R31['counts_sha256'], 'fc_counts_v31_sha256': sha(os.path.join(OUTD, 'fc-counts-v31.json')),
       'fc_counts_v3_sha256': sha(os.path.join(OUTD, 'fc-counts-v3.json')), 'rows_added': {'MM1-v3.1': R31['rows_added'], 'MM1-v3': R3['rows_added']},
       'check_unchanged_K': {'MM1-v3.1': R31['check_unchanged_K'], 'MM1-v3': R3['check_unchanged_K']},
       'gate_vs_count_valid_share_REPORTED': vs, 'n_cases': len(out),
       'energy_status': dict(collections.Counter(('FORECAST' if v['MM1-v3.1']['energy'] == 'FORECAST' else 'NOT FORECAST') for v in out.values())),
       'cases': out}
JP = os.path.join(L, 'forecasts-nominal-e217-counts.json')
json.dump(rec, open(JP, 'w'), indent=1, sort_keys=True)
CP = os.path.join(L, 'forecasts-nominal-e217-counts.csv')
MODELS = ['MM1-v3.1', 'MM1-v3', 'v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1', 'ctrl F1-layout-blind',
          'MM1-v3.1 literal gate (REPORTED)', 'MM1-v3 literal gate (REPORTED)', 'MM1-v3.1 count gate (REPORTED)', 'MM1-v3 count gate (REPORTED)']
with open(CP, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['case', 'card', 'arm', 'fmt', 'kind', 'mask', 'model', 'energy', 'W_A', 'W_B_us', 'T_op_us', 'W_over_idle_own_t', 'J_over_idle_per_gemm',
                'declared_gate_g_op'])
    for k, o in out.items():
        c = CASE[k]
        for m in MODELS:
            if m not in o:
                continue
            x = o[m]
            f = (lambda n: '' if x.get(n) is None else '%.9g' % x[n])
            jg = '' if x.get('energy') != 'FORECAST' else '%.9g' % (x['W_fc'] * x['sec_gemm'])
            w.writerow([k, c['card'], c['arm'], c['fmt'], c['kind'], c['mask'], m, x.get('energy'), f('W_A'), f('W_B'), f('T_op_us'), f('W_fc'), jg,
                        '' if o['gate'].get('g_op') is None else '%.4f' % o['gate']['g_op']])
print('group S cases', len(out), 'energy', rec['energy_status'])
print('gate vs count valid share (REPORTED)', json.dumps(vs))
print(sha(CP), 'forecasts-nominal-e217-counts.csv')
print(sha(JP), 'forecasts-nominal-e217-counts.json')
