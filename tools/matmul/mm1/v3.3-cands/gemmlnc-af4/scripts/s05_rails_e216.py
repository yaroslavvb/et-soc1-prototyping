#!/usr/bin/env python3
"""lnc-form step 5 (REPORTED, post hoc; decides nothing): E216's committed rail split (E208's reducer, view 'win', route-c runs) for each
gemmLnc point minus its cooperative twin, per minion-op at each kernel's own op rate, beside the frozen form AF4's R4."""
import json, os
import numpy as np
L = os.environ['LNC_FORM_DIR']
LAB = os.environ['LAB_DIR']
d = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/data-e216.json')))
fit = json.load(open(os.path.join(L, 'work', 's02_fit.json')))
R4 = {r['id']: r['R4'] for r in fit['features_per_point']}
def rails(pid):
    out = []
    for r in d['runs']:
        if r.get('arm') != pid or r.get('role') != 'arm' or r.get('capped'):
            continue
        v = r['views']['win']
        if v.get('dP_w') is None or not (790 <= v['kclock_mhz'] <= 810):
            continue
        out.append({k: v['rails'][k]['dW'] for k in ('minion', 'noc', 'sram')} | {'board': v['dP_w'], 'T': v['T_op_us']})
    return {k: float(np.mean([o[k] for o in out])) for k in out[0]}
rows = []
print('%-5s %-15s %5s | %7s %7s %7s %7s | %7s %7s (nJ a minion-op, at each kernel own rate: dW x T_op / 1e3 ... per minion)' % ('pt', 'token', 'R4', 'board', 'minion', 'noc', 'sram', 'noc_nJ', 'sram_nJ'))
for i in range(1, 11):
    pid = 'g%02d' % i
    a, b = rails(pid), rails(pid + 't')
    # energy a minion-op = W x T_op(us) x 1e-6 / 1024 minions -> nJ: x 1e9
    e = {k: (a[k] * a['T'] - b[k] * b['T']) * 1e-6 / 1024 * 1e9 for k in ('board', 'minion', 'noc', 'sram')}
    rid = 'E216|a2c0|' + pid
    rows.append({'point': pid, 'R4': R4[rid], 'dW': {k: a[k] - b[k] for k in ('board', 'minion', 'noc', 'sram')}, 'dE_nJ_per_minion_op': e})
    print('%-5s %-15s %5.1f | %+7.2f %+7.2f %+7.2f %+7.2f | %+7.2f %+7.2f' % (pid, '', R4[rid], a['board'] - b['board'], a['minion'] - b['minion'],
          a['noc'] - b['noc'], a['sram'] - b['sram'], e['noc'], e['sram']))
json.dump(rows, open(os.path.join(L, 'work', 's05_rails_e216.json'), 'w'), indent=1)
