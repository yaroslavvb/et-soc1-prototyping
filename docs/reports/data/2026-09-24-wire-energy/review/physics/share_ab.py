import json, collections, numpy as np, sys
sys.path.insert(0,'/home/yaroslavvb/claude/et-soc1-prototyping/workloads/enercat')
MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0), 8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1),
        10: (4, 1), 19: (5, 1), 3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2), 12: (1, 3), 21: (2, 3),
        22: (3, 3), 26: (4, 3), 20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4), 28: (1, 5), 5: (2, 5), 6: (3, 5),
        7: (4, 5), 31: (5, 5)}
def links(t,r):
    (x,y),(x1,y1)=MESH[t],MESH[r]; out=[]
    while x!=x1:
        nx=x+(1 if x1>x else -1); out.append(((x,y),(nx,y))); x=nx
    while y!=y1:
        ny=y+(1 if y1>y else -1); out.append(((x,y),(x,ny))); y=ny
    return out
tm={}
for l in open('/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-24-wire2-aifoundry2/runs.jsonl'):
    r=json.loads(l)
    if r['cfg'].startswith('wu/p0.5/') and r['target_map']: tm[r['hop_distance']]=r['target_map']
S={}
for d,m in sorted(tm.items()):
    pairs=[tuple(int(x.split('/')[0]) for x in p.split('>')) for p in m.split(',')]  # reader>target
    cnt=collections.Counter()
    L={}
    for r,t in pairs:
        if r==t: continue
        L[(r,t)]=links(t,r); cnt.update(L[(r,t)])
    tot=sum(len(v) for v in L.values()); sh=sum(1 for v in L.values() for l in v if cnt[l]>1)
    load=np.mean([cnt[l] for v in L.values() for l in v])
    S[d]=sh/len(L)
    print(f'd={d} flows={len(L)} shared frac={sh/tot:.2f} shared link-hops/flow={sh/len(L):.2f} mean flows per used link-hop={load:.2f}')
B=json.load(open('../indep/bursts.json'))
good=[b for b in B if not b['bad']]
C=collections.defaultdict(list)
for b in good: C[(b['set'],b['card'],b['cfg'])].append(b['pJB_noc'])
C={k:np.mean(v) for k,v in C.items()}
for card in ['aifoundry2','aifoundry3']:
    A=[];Bv=[];ds=[1,2,3,4,6]
    for d in ds:
        X=[];y=[]
        for P in [0,0.25,0.5,0.75,1]:
            X.append([1,2*P*(1-P),P]); y.append(C[('v2',card,f'wu/p{P}/hop{d}')])
        k=('v2',card,f'wfrz/hop{d}')
        if k in C: X.append([1,0,244/512]); y.append(C[k])
        c,_,_,_=np.linalg.lstsq(np.array(X),np.array(y),rcond=None); A.append(c[1]*125); Bv.append(c[2]*125)
    M=np.array([[1,d,S[d]] for d in ds])
    ca,_,_,_=np.linalg.lstsq(M,np.array(A),rcond=None); cb,_,_,_=np.linalg.lstsq(M,np.array(Bv),rcond=None)
    print(card,'A = %.0f + %.0f*d + %.0f*S   B = %.0f + %.0f*d + %.0f*S  (fJ/bit; S = shared link-hops per flow)'%(*ca,*cb))
