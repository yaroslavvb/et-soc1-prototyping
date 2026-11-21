#!/usr/bin/env python3
"""decl-e223 (Q239) recheck, after the freeze (nothing frozen changes): the nominal forecasts re-made by s02b_nominal.py in a process of its
own (--test into work/recheck/) compared field by field with the frozen work/step2/fc-nominal.json (every case, every model, every numeric
field equal to the last bit). Run: /usr/bin/python3 -I -B s02r_compare.py <lane dir>"""
import hashlib
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
A = json.load(open(os.path.join(L, 'work', 'step2', 'fc-nominal.json')))
B = json.load(open(os.path.join(L, 'work', 'recheck', 'fc-nominal.json')))
n = diff = 0
bad = []
for case, o in A['cases'].items():
    for m, x in o.items():
        y = B['cases'][case][m]
        for k, v in x.items():
            n += 1
            if y.get(k) != v:
                diff += 1
                if len(bad) < 5:
                    bad.append((case, m, k, v, y.get(k)))
out = {'what': 'decl-e223 recheck: the nominal forecasts re-made in a process of their own', 'fields_compared': n, 'differing': diff,
       'examples': bad, 'cases': len(A['cases']), 'models': A['models'], 'checks_equal': A['checks'] == B['checks'],
       'frozen_sha256': hashlib.sha256(open(os.path.join(L, 'work', 'step2', 'fc-nominal.json'), 'rb').read()).hexdigest()}
json.dump(out, open(os.path.join(L, 'work', 'recheck', 'recheck.json'), 'w'), indent=1)
print(json.dumps(out))
