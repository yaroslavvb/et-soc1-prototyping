import numpy as np
from load import SETS, load, indicator_response
T,B,M=load(SETS[('v2','aifoundry3')])
t=T['t']
def held_times(ts, ys):
    # time at which each held value first appeared
    out=ts.copy()
    for i in range(1,len(ts)):
        if ys[i]==ys[i-1]: out[i]=out[i-1]
    return out
for b in [x for x in B if x['cfg'] in ('wu/p0.5/hop3','wu/p0/hop1')][:2]:
    nxt=[a for a,_,_ in M if a>b['hi']]
    w=(t>=b['lo']-3)&(t<=min(b['hi']+3.8,nxt[0]-0.05))
    ts,ys=t[w],T['noc'][w]
    pf=[(a,e) for a,e,k in M if e<b['lo'] and e>b['lo']-12]
    for mode in ('raw','held'):
        for tau,de in ((1.04,0.375),(1.04,0.2),(1.04,0.3)):
            tt = ts if mode=='raw' else held_times(ts,ys)
            X=np.vstack([np.ones_like(tt), indicator_response(tt,b['launches'],tau,de), indicator_response(tt,pf,tau,de)]).T
            c,*_=np.linalg.lstsq(X,ys,rcond=None)
            r=ys-X@c
            print(b['cfg'],b['pass'],mode,tau,de,'step',round(c[1],3),'base',round(c[0],3),'fill',round(c[2],3),'rms mW',round(np.sqrt((r**2).mean())*1000,1))
    tt=held_times(ts,ys)
    X=np.vstack([np.ones_like(tt), indicator_response(tt,b['launches'],1.04,0.2), indicator_response(tt,pf,1.04,0.2)]).T
    c,*_=np.linalg.lstsq(X,ys,rcond=None)
    for a,bb,cc,dd in zip(ts-b['lo'],tt-b['lo'],ys,X@c):
        if -0.5<a<5: print(f'{a:6.2f} {bb:6.2f} {cc:7.3f} {dd:7.3f} {cc-dd:+.3f}')
