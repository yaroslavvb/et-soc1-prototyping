import json, collections, numpy as np
B=json.load(open('../indep/bursts.json'))
good=[b for b in B if not b['bad']]
C=collections.defaultdict(list)
for b in good: C[(b['set'],b['card'],b['cfg'])].append(b['pJB_noc'])
C={k:np.mean(v) for k,v in C.items()}
def slope(set_,card,pre,ds):
    x=[];y=[]
    for d in ds:
        k=(set_,card,pre.format(d=d))
        if k in C: x.append(d); y.append(C[k])
    return np.polyfit(x,y,1)[0]
for card in ['aifoundry2','aifoundry3']:
    Ps=[0,0.1,0.25,0.5,0.75,0.9,1]
    s=np.array([slope('v1',card,'wbern/p%s/hop{d}'%P,[1,2,3,4,6]) for P in Ps])
    for model in ['t,P','t,P,par']:
        X=[[1,2*P*(1-P),P]+([1.0 if 0<P<1 else 0.0] if 'par' in model else []) for P in Ps]
        X=np.array(X); c,_,_,_=np.linalg.lstsq(X,s,rcond=None); r=s-X@c
        print(card,model,' '.join(f'{v*125:.1f}' for v in c),'fJ/bit/hop; rms %.4f'%np.sqrt(np.mean(r**2)),'resid',' '.join(f'{v:+.3f}' for v in r))
    # also: does P-dependence look linear+quadratic? fit s0 + c1 P + c2 P^2 (equivalent) and a cubic
    X=np.array([[1,P,P*P,P**3] for P in Ps]); c,_,_,_=np.linalg.lstsq(X,s,rcond=None); r=s-X@c
    print(card,'cubic coef P^3 %.3f pJ/B/hop, rms %.4f'%(c[3],np.sqrt(np.mean(r**2))))
