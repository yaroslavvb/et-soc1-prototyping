#!/usr/bin/env python3
"""mask-mesh h01: hash DECLARED-mesh.md, the procedure's code and its inputs BEFORE the fit (DECLARED.sha256.json and DECLARED.sha256);
m03_fit.py refuses to run if any of them changed. Run: python3 -I -B h01_hash_declaration.py <lane dir>"""
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])


def sha(rel):
    return hashlib.sha256(open(os.path.join(L, rel), 'rb').read()).hexdigest()


code = ['scripts/' + f for f in sorted(os.listdir(os.path.join(L, 'scripts'))) if f.endswith(('.py', '.sh')) and f != 'h01_hash_declaration.py']
inputs = ['work/points-mesh.json', 'work/features-mesh.json', 'work/e224b/data-e224b.json', 'work/lab-SNAPSHOT.txt']
rec = {'what': 'mask-mesh: the declaration, its code and its inputs, hashed before any fit of the form', 'hashed_at': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
       'python': sys.version.split()[0], 'DECLARED-mesh.md': sha('DECLARED-mesh.md'), 'code': {c: sha(c) for c in code},
       'inputs': {i: sha(i) for i in inputs}}
json.dump(rec, open(os.path.join(L, 'DECLARED.sha256.json'), 'w'), indent=1)
with open(os.path.join(L, 'DECLARED.sha256'), 'w') as f:
    f.write(f"{rec['DECLARED-mesh.md']}  DECLARED-mesh.md\n")
    for k, v in list(rec['code'].items()) + list(rec['inputs'].items()):
        f.write(f'{v}  {k}\n')
print(json.dumps({'hashed_at': rec['hashed_at'], 'DECLARED-mesh.md': rec['DECLARED-mesh.md'], 'n_code': len(code)}, indent=1))
