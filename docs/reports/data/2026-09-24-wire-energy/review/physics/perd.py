import json, collections, numpy as np
B=json.load(open('../indep/bursts.json'))
good=[b for b in B if not b['bad']]
def cell(key):
    d=collections.defaultdict(list)
    for b in good:
        d[(b['set'],b['card'],b['cfg'])].append(b[key])
    return {k:np.mean(v) for k,v in d.items()}
for key in ['pJB_noc','pJB_boardleak']:
    C=cell(key)
    print('=====',key)
    # per-d decomposition in wu
    for card in ['aifoundry2','aifoundry3']:
        print(card)
        for d in [0,1,2,3,4,6]:
            X=[];y=[]
            for P in [0,0.25,0.5,0.75,1]:
                k=('v2',card,f'wu/p{P}/hop{d}')
                if k in C: X.append([1,2*P*(1-P),P]); y.append(C[k])
            k=('v2',card,f'wfrz/hop{d}')
            if k in C: X.append([1,0,244/512]); y.append(C[k])
            X=np.array(X);y=np.array(y)
            c,res,_,_=np.linalg.lstsq(X,y,rcond=None)
            r=y-X@c
            print(f' d={d} c0={c[0]:.3f} A={c[1]*125:.1f} B={c[2]*125:.1f} fJ/bit (total, not per hop) B/A={c[2]/c[1] if c[1] else 0:.2f} rms={np.sqrt(np.mean(r**2)):.4f} n={len(y)}')
        # incremental per hop between successive d
    # walt
    print('walt: e(n256)-mean(e n16..n128) per d, pJ/B')
    for card in ['aifoundry2','aifoundry3']:
        for d in [0,1,3,6]:
            base=np.mean([C[('v1',card,f'walt/n{n}/hop{d}')] for n in [16,32,64,128]])
            vals=[C[('v1',card,f'walt/n{n}/hop{d}')] for n in [16,32,64,128,256]]
            print(f' {card} d={d} ', ' '.join(f'{v:.3f}' for v in vals), f' excess={vals[-1]-base:.3f}')
