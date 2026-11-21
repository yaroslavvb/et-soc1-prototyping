#!/usr/bin/env python3
"""mask-posimb (Q238) x08: before the declaration's hash: A1's share among the in-scope multi-tile subset points by experiment (a count; no
fit, no residual). Desk; stdlib."""
import collections, json, os, re
LANE = os.environ['MASKPOS_LANE']
SH = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
def A1(m):
    m = int(m, 16)
    return int(not any(((s >> 2) & 3) == (s & 3) for s in range(32) if (m >> s) & 1))
c = collections.defaultdict(lambda: [0, 0])
for p in P:
    m = SH.match(p['arm'])
    if p['kernel'] == 'rgm136' and m and int(p['mask'], 16) != 0xFFFFFFFF and tuple(int(x) for x in m.groups()) != (1, 1, 1):
        c[p['exp']][A1(p['mask'])] += 1
for x in sorted(c, key=lambda z: int(z[1:])):
    print('%-5s A1=0 %4d  A1=1 %4d' % (x, c[x][0], c[x][1]))
