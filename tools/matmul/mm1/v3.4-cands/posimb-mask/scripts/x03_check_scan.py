#!/usr/bin/env python3
"""mask-posimb (Q238) x03: scan every committed matmul data JSON E206-E224 (docs/reports/data/*e2[0-2][0-9]*/data*.json, E208's and E215's
reducer forms) for runs whose check of C is missing or not exact/approx. Desk; stdlib only. Output: work/check_scan.json (+ printed)."""
import glob
import json
import os

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
out = {}
fs = sorted(glob.glob(os.path.join(LAB, 'docs/reports/data/*-e2[0-2][0-9]-*/data*.json')))
fs.append(os.path.join(LANE, 'work/e224b/data-e224b.json'))
for f in fs:
    rel = os.path.relpath(f, LAB) if f.startswith(LAB) else 'lane:' + os.path.relpath(f, LANE)
    try:
        d = json.load(open(f))
    except Exception as ex:  # noqa: BLE001
        out[rel] = {'error': str(ex)}
        continue
    bad, n = [], 0
    if isinstance(d.get('runs'), list):   # E208's reducer form
        for r in d['runs']:
            if r.get('role') not in ('arm', 'anchor', 'tie') or not r.get('ran', True):
                continue
            n += 1
            c = r.get('checks') or []
            if not c or any(x not in ('exact', 'approx') for x in c):
                bad.append({'arm': r.get('arm'), 'i': r.get('i'), 'role': r.get('role'), 'checks': c})
    if isinstance(d.get('arms'), dict):    # E215's reducer form
        for tag, A in d['arms'].items():
            if not isinstance(A, dict):
                continue
            for pid, P in (A.get('points') or {}).items():
                for r in P.get('runs', []):
                    n += 1
                    c = r.get('checks') or []
                    if not c or any(x not in ('exact', 'approx') for x in c):
                        bad.append({'tag': tag, 'pid': pid, 'n': r.get('n'), 'checks': c, 'has_cycles': r.get('cycles_gemm') is not None})
    out[rel] = {'runs_seen': n, 'bad': bad}
json.dump(out, open(os.path.join(LANE, 'work/check_scan.json'), 'w'), indent=1)
for k, v in out.items():
    print('%-90s runs %4s bad %s' % (k[-90:], v.get('runs_seen'), v.get('bad') if v.get('bad') else 0))
