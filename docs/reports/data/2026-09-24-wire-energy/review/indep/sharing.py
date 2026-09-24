#!/usr/bin/env python3
"""Fraction of payload link-hops on a directed link used by >1 flow (XY routing, target->reader), per v2 config."""
import json, collections
DATA = '/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data'
# logical mesh positions of shires (geometry input, as listed in run_wire.py MESH)
MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0), 8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1),
        10: (4, 1), 19: (5, 1), 3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2), 12: (1, 3), 21: (2, 3),
        22: (3, 3), 26: (4, 3), 20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4), 28: (1, 5), 5: (2, 5), 6: (3, 5),
        7: (4, 5), 31: (5, 5)}
def route(a, b, xfirst=True):
    (x, y), (x1, y1) = MESH[a], MESH[b]; out = []
    order = ('x', 'y') if xfirst else ('y', 'x')
    for ax in order:
        if ax == 'x':
            while x != x1:
                nx = x + (1 if x1 > x else -1); out.append(((x, y), (nx, y))); x = nx
        else:
            while y != y1:
                ny = y + (1 if y1 > y else -1); out.append(((x, y), (x, ny))); y = ny
    return out
for vs, d in [('v2', '2026-09-24-wire2-aifoundry2'), ('v1', '2026-09-24-wire-aifoundry2')]:
    seen = {}
    for l in open(f'{DATA}/{d}/runs.jsonl'):
        r = json.loads(l)
        if r['cfg'] in seen: continue
        seen[r['cfg']] = r
    for cfg, r in sorted(seen.items()):
        if not (cfg.startswith('wu/p0/') or cfg.startswith('wsep/p0/') or cfg.startswith('wbern/p0/')): continue
        tm = r['target_map']
        if tm:
            pairs = [(int(x.split('>')[0]), int(x.split('>')[1].split('/')[0])) for x in tm.split(',')]
        else:
            continue
        for xfirst in (True, False):
            use = collections.Counter(); tot = 0; hops = []
            for rd, tg in pairs:
                L = route(tg, rd, xfirst); hops.append(len(L))
                for l in L: use[l] += 1
            tot = sum(use.values()); shared = sum(v for v in use.values() if v > 1)
            print(vs, cfg, 'xfirst' if xfirst else 'yfirst', 'flows', len(pairs), 'mean hops %.2f' % (sum(hops)/len(hops)),
                  'shared link-hops %.0f%%' % (100 * shared / tot if tot else 0), 'readers/target max', max(collections.Counter(t for _, t in pairs).values()))
