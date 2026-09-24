import json, collections, numpy as np
B=json.load(open('../indep/bursts.json'))
good=[b for b in B if not b['bad']]
def cell(key):
    d=collections.defaultdict(list)
    for b in good:
        d[(b['set'],b['card'],b['cfg'])].append(b[key])
    return {k:np.mean(v) for k,v in d.items()}
for key in ['pJB_noc']:
    C=cell(key)
    print('=====',key,'v1 wbern')
    for card in ['aifoundry2','aifoundry3']:
        for d in [0,1,2,3,4,6]:
            X=[];y=[]
            for P in [0,0.1,0.25,0.5,0.75,0.9,1]:
                k=('v1',card,f'wbern/p{P}/hop{d}')
                if k in C: X.append([1,2*P*(1-P),P]); y.append(C[k])
            X=np.array(X);y=np.array(y)
            c,_,_,_=np.linalg.lstsq(X,y,rcond=None); r=y-X@c
            print(f' {card} d={d} c0={c[0]:.3f} A={c[1]*125:.1f} B={c[2]*125:.1f} rms={np.sqrt(np.mean(r**2)):.4f}', ' resid', ' '.join(f'{v:+.3f}' for v in r))
    # walt at d relative to wbern model at same d: alt N<=128 has t=0,P=.5 -> predicted c0+B*0.5 ; N=256 t=1 -> c0 + A + 0.5B
    print('walt vs v1 per-d model')
    for card in ['aifoundry2','aifoundry3']:
        for d in [0,1,3,6]:
            X=[];y=[]
            for P in [0,0.1,0.25,0.5,0.75,0.9,1]:
                k=('v1',card,f'wbern/p{P}/hop{d}')
                X.append([1,2*P*(1-P),P]); y.append(C[k])
            c,_,_,_=np.linalg.lstsq(np.array(X),np.array(y),rcond=None)
            p0=c[0]+0.5*c[2]; p1=c[0]+c[1]+0.5*c[2]
            lo=np.mean([C[('v1',card,f'walt/n{n}/hop{d}')] for n in [16,32,64,128]]); hi=C[('v1',card,f'walt/n256/hop{d}')]
            print(f' {card} d={d} pred t=0 {p0:.3f} meas {lo:.3f} | pred t=1 {p1:.3f} meas {hi:.3f} | frac of full flip {(hi-lo)/c[1]:.2f}')
