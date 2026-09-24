import json,collections,numpy as np
MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0), 8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1),
        10: (4, 1), 19: (5, 1), 3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2), 12: (1, 3), 21: (2, 3),
        22: (3, 3), 26: (4, 3), 20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4), 28: (1, 5), 5: (2, 5), 6: (3, 5),
        7: (4, 5), 31: (5, 5)}
def links(t, r, yfirst=False):
    (x, y), (x1, y1) = MESH[t], MESH[r]; out = []
    def mx():
        nonlocal x
        while x != x1:
            nx = x + (1 if x1 > x else -1); out.append(((x, y), (nx, y))); x = nx
    def my():
        nonlocal y
        while y != y1:
            ny = y + (1 if y1 > y else -1); out.append(((x, y), (x, ny))); y = ny
    (my(), mx()) if yfirst else (mx(), my())
    return out
res=collections.defaultdict(list)
for v in ('2026-09-24-wire2-aifoundry2','2026-09-24-wire2-aifoundry3','2026-09-24-wire-aifoundry2'):
    seen=set()
    for l in open(f'/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/{v}/runs.jsonl'):
        r=json.loads(l)
        if not r['cfg'].startswith(('wu/p0.5','wsep/p0.5','wbern/p0.5')) or (r['cfg'],r['pass']) in seen: continue
        seen.add((r['cfg'],r['pass']))
        if not r.get('target_map'): continue
        pairs=[tuple(map(int,x.split('/')[0].split('>'))) for x in r['target_map'].split(',') if '>' in x]
        for yf in (False,True):
            use=collections.Counter(); per=[]
            for rd,tg in pairs:
                L=links(tg,rd,yf); per.append(L); use.update(L)
            tot=sum(len(L) for L in per); sh=sum(1 for L in per for l in L if use[l]>1)
            res[(v[-10:],r['cfg'],'yx' if yf else 'xy')].append((sh/tot if tot else 0, len(pairs), np.mean([len(L) for L in per])))
for k,v in sorted(res.items()):
    print(k, 'shared frac', [round(x[0],2) for x in v], 'flows',v[0][1],'mean hops',round(v[0][2],2))
