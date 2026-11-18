#!/usr/bin/env python3
"""fix-v31counts (Q217) step 2a: the spec count_e210.py reads for the re-count of fp32 real:blind4 at S2 (desk; writes JSON only).
E207's two-file blind4 pool in inventory.py's order (file 0 = fp32.real_pythia_embed_qkv, file 1 = fp32.real_qwen_q_down), the files from
this lane's git archive of GitHub main 6efdb002 (sha256 checked against v31-counts' tile inventory).
    /usr/bin/python3 -I -B s02a_spec.py <lane dir>
"""
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory as I  # noqa: E402

k = [x for x in I.KINDS if x['key'] == 'fp32.e207.real_blind4'][0]
inv = json.load(open(os.path.join(L, 'work', 'tiles-inventory.json')))
files = []
for p in k['files']:
    a = os.path.join(L, 'work', 'lab', p)
    h = hashlib.sha256(open(a, 'rb').read()).hexdigest()
    assert h == inv[p]['sha256'], (p, h)
    files.append(a)
json.dump({k['key']: {'files': files}}, open(os.path.join(L, 'work', 'spec-recount-b4.json'), 'w'), indent=1)
print(f"spec: {k['key']}: " + ', '.join(f'file {i} {os.path.basename(f)}' for i, f in enumerate(files)))
