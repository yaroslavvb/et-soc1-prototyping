import json, collections, numpy as np
exec(open('contention.py').read().split('B=json.load')[0])
bw={}
for s,f in [('v1','2026-09-24-wire-aifoundry3'),('v2','2026-09-24-wire2-aifoundry3')]:
    agg=collections.defaultdict(list)
    for l in open(D+f+'/runs.jsonl'):
        r=json.loads(l); agg[r['cfg']].append((r['bytes_per_s'],r['participants']//32))
    for k,v in agg.items(): bw[(s,k)]=(np.mean([x[0] for x in v])/1e9, v[0][1])
def loads(m):
    pairs=[tuple(int(x.split('/')[0]) for x in p.split('>')) for p in m.split(',')] if '>' in m else [tuple(map(int,p.split(':'))) for p in m.split(',')]
    cnt=collections.Counter(); L={}
    for r,t in pairs:
        if r==t: continue
        L[(r,t)]=links(t,r); cnt.update(L[(r,t)])
    w=[cnt[l] for v in L.values() for l in v]
    return np.mean(w), max(cnt.values())
for s,cfg in [('v2','wsep/p0.5/hop4'),('v2','wu/p0.5/hop4'),('v1','waxis/x/hop4/p0.5'),('v1','waxis/y/hop4/p0.5'),('v2','wsep/p0.5/hop2'),('v2','wu/p0.5/hop2'),('v1','waxis/x/hop2/p0.5'),('v1','waxis/y/hop2/p0.5'),('v2','wu/p0.5/hop3'),('v1','waxis/x/hop3/p0.5'),('v2','wu/p0.5/hop6')]:
    m=tm[(s,'aifoundry3',cfg)]; ml,mx=loads(m); g,n=bw[(s,cfg)]
    print(f'{cfg:22s} readers {n:2d} per-reader {g/n:5.1f} GB/s  flow-weighted flows/link {ml:.2f} max {mx}  -> mean link traffic {ml*g/n:5.1f} GB/s')
