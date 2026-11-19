#!/usr/bin/env python3
"""counts-e214 (Q225) step 9b: the merge check (desk; no energy is computed). This lane's two tables merged into MM1-v3.1's merged tables
exactly as energy_v31.py merges tools/matmul/mm1/v3.1/counts/ (its own loop and asserts: no key already committed), then MM1-v3.1's own
counts31() asked at every (format, kind, KB) an E214 arm runs (scope-e214.json): every NEEDS-COUNT kind must now return (S, v), and every
other kind the same (S, v) as before the merge. Reads energy_v31 as landed (8bde0182's copy); changes nothing on disk but its own output.
    /usr/bin/python3 -I -B s09b_mergecheck.py <lane dir>
"""
import json
import os
import sys

L = sys.argv[1]
LAB = os.path.join(L, 'work', 'lab')
V31 = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.1')
sys.path.insert(0, V31)
import energy_v31 as EN31  # noqa: E402

sc = json.load(open(os.path.join(L, 'counts', 'scope-e214.json')))
before = {}
for k in sc['kinds']:
    for kb in k['KB']:
        c = EN31.counts31(k['fmt'], k['kind'], kb)
        before[(k['fmt'], k['kind'], kb)] = None if c is None else (float(c[0]), float(c[1]))
C32 = json.load(open(os.path.join(L, 'counts', 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(L, 'counts', 'counts-fp16-int8-launch.json')))['rows']
for sh in ('S1', 'S2'):                      # energy_v31's own merge loop, on this lane's rows
    for k, r in C32[sh].items():
        assert k not in EN31.E210C31[sh], ('fp32 count row already committed', sh, k)
        EN31.E210C31[sh][k] = r
for k, r in C16.items():
    assert k not in EN31.SWT31, ('fp16/int8 count row already committed', k)
    EN31.SWT31[k] = r
out = {'what': ("counts31() of MM1-v3.1 as landed, before and after this lane's rows are merged the way energy_v31 merges its counts/ "
                "(desk; S signal fin edges an op, v valid share; no energy computed)"), 'points': [], 'problems': []}
for k in sc['kinds']:
    for kb in k['KB']:
        c = EN31.counts31(k['fmt'], k['kind'], kb)
        after = None if c is None else (float(c[0]), float(c[1]))
        b = before[(k['fmt'], k['kind'], kb)]
        rec = {'fmt': k['fmt'], 'kind': k['kind'], 'KB': kb, 'verdict_scope': k['verdict'], 'before': b, 'after': after}
        if k['verdict'] == 'NEEDS COUNT' and after is None:
            out['problems'].append(f"{k['fmt']} {k['kind']} KB {kb}: still no count")
        if k['verdict'] != 'NEEDS COUNT' and after != b:
            out['problems'].append(f"{k['fmt']} {k['kind']} KB {kb}: a committed kind's count changed")
        out['points'].append(rec)
n_new = sum(1 for p in out['points'] if p['verdict_scope'] == 'NEEDS COUNT' and p['after'] is not None)
out['summary'] = (f"{n_new} (format, kind, KB) cells of E214's NEEDS-COUNT kinds now return a count; "
                  f"{sum(1 for p in out['points'] if p['verdict_scope'] != 'NEEDS COUNT')} committed-kind cells unchanged; problems {len(out['problems'])}")
json.dump(out, open(os.path.join(L, 'counts', 'merge-check.json'), 'w'), indent=1, sort_keys=True)
print(out['summary'])
for p in out['points']:
    if p['verdict_scope'] == 'NEEDS COUNT':
        print(f"  {p['fmt']:5s} {p['kind']:22s} KB {p['KB']:2d}: S {p['after'][0]:.6g} v {p['after'][1]:.4f}" if p['after'] else f"  {p['fmt']} {p['kind']} KB {p['KB']}: NONE")
sys.exit(1 if out['problems'] else 0)
