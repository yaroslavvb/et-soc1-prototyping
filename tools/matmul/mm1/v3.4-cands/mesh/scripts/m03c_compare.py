#!/usr/bin/env python3
"""mask-mesh m03c: the re-run (m03b, the unchanged m03_fit.py) against the first run: every log line equal but for its times (the start and
end stamps and the seconds in parentheses), and the first run's partial holdout-mesh.json a prefix of the re-run's bytes up to where it
stopped. Run: python3 -I -B m03c_compare.py <lane dir>"""
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
a = open(os.path.join(L, 'work', 'fit-run1', 'm03.log')).read().splitlines()
b = open(os.path.join(L, 'work', 'fit', 'm03.log')).read().splitlines()


def norm(s):
    s = re.sub(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [A-Z]+', '<time>', s)
    s = re.sub(r'\(\d+(\.\d+)? s\)', '(<s>)', s)
    s = re.sub(r'\(\d+ s\)', '(<s>)', s)
    return s


na = [norm(x) for x in a]
nb = [norm(x) for x in b if not x.startswith('m03 done')]
same = na == nb[:len(na)]
diff = [(i, x, y) for i, (x, y) in enumerate(zip(na, nb)) if x != y]
pa = open(os.path.join(L, 'work', 'fit-run1', 'holdout-mesh.json'), 'rb').read()
pb = open(os.path.join(L, 'work', 'fit', 'holdout-mesh.json'), 'rb').read()
fa = open(os.path.join(L, 'work', 'fit-run1', 'fit-mesh.json'), 'rb').read()
fb = open(os.path.join(L, 'work', 'fit', 'fit-mesh.json'), 'rb').read()
fit_same = re.sub(rb'"(started|ended)": "[^"]*"', b'', fa) == re.sub(rb'"(started|ended)": "[^"]*"', b'', fb)
print(f'log lines: run 1 {len(na)}, re-run {len(nb)} (but its "m03 done"); equal but for times over run 1\'s lines: {same}; differing lines {len(diff)}')
for d in diff[:5]:
    print('  DIFF', d)
print(f'fit-mesh.json equal but for its start/end stamps: {fit_same}')
print(f"run 1's partial holdout-mesh.json ({len(pa)} bytes) a prefix of the re-run's ({len(pb)} bytes): {pb.startswith(pa)}")
sys.exit(0 if (same and fit_same and pb.startswith(pa)) else 1)
