import json, collections, numpy as np
exec(open('share_ab.py').read().split('tm={}')[0])  # MESH, links
D='/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/'
tm={}; readers_per_target={}
for s,f in [('v1','2026-09-24-wire-aifoundry2'),('v2','2026-09-24-wire2-aifoundry2'),('v1','2026-09-24-wire-aifoundry3'),('v2','2026-09-24-wire2-aifoundry3')]:
    for l in open(D+f+'/runs.jsonl'):
        r=json.loads(l)
        tm[(s,r['host'],r['cfg'])]=r['target_map']
def share(m):
    pairs=[tuple(int(x.split('/')[0]) for x in p.split('>')) for p in m.split(',')] if '>' in m else [tuple(map(int,p.split(':'))) for p in m.split(',')]
    cnt=collections.Counter(); L={}
    for r,t in pairs:
        if r==t: continue
        L[(r,t)]=links(t,r); cnt.update(L[(r,t)])
    tot=sum(len(v) for v in L.values()); sh=sum(1 for v in L.values() for l in v if cnt[l]>1)
    tc=collections.Counter(t for r,t in L)
    turns=sum(1 for (r,t) in L if MESH[r][0]!=MESH[t][0] and MESH[r][1]!=MESH[t][1])
    return len(L), sh/max(tot,1), sh/max(len(L),1), max(tc.values()), turns/len(L)
B=json.load(open('../indep/bursts.json'))
good=[b for b in B if not b['bad']]
C=collections.defaultdict(list)
for b in good: C[(b['set'],b['card'],b['cfg'])].append((b['pJB_noc'],b['pJB_boardleak']))
C={k:np.mean(v,axis=0) for k,v in C.items()}
rows=[('v2','wsep/p0.5/hop{d}','wsep/p0/hop{d}',[1,2,3,4,5]),('v2','wu/p0.5/hop{d}','wu/p0/hop{d}',[1,2,3,4,6]),
      ('v1','waxis/x/hop{d}/p0.5','waxis/x/hop{d}/p0',[1,2,3,4]),('v1','waxis/y/hop{d}/p0.5','waxis/y/hop{d}/p0',[1,2,3,4]),('v1','wbern/p0.5/hop{d}','wbern/p0/hop{d}',[1,2,3,4,6])]
for s,a,z,ds in rows:
    print(a.split('/')[0], a.split('/')[1] if 'waxis' in a else '')
    for d in ds:
        vals=[]
        for card in ['aifoundry2','aifoundry3']:
            ka=(s,card,a.format(d=d)); kz=(s,card,z.format(d=d))
            if ka in C and kz in C: vals.append((C[ka][0]-C[kz][0], C[kz][0], C[ka][1]-C[kz][1]))
        m=tm.get((s,'aifoundry3',a.format(d=d))) or tm.get((s,'aifoundry2',a.format(d=d)))
        n,fr,per,mx,tu=share(m)
        v=np.mean(vals,axis=0) if vals else [np.nan]*3
        print(f'  d={d} flows={n} shared={fr:.2f} sh/flow={per:.2f} max readers/target={mx} turned={tu:.2f} | NoC data {v[0]:.3f} zeros {v[1]:.3f} board data {v[2]:.3f} pJ/B (n cards {len(vals)})')
