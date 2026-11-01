import sys, json, math, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from obs import all_obs
O=all_obs(('e94',))
isfloat=lambda r:r['type'] in('fp32','fp16')
F=[r for r in O if isfloat(r)]
MODELS={
 "M2 nets,clk":lambda d:[d['nets'],d['clk']],
 "bus":lambda d:[d['nets']-d['bus'],d['bus'],d['clk']],
 "mult,add":lambda d:[d['mult'],d['add'],d['nets']-d['mult']-d['add'],d['clk']],
 "core,bus,rest":lambda d:[d['mult']+d['add'],d['bus'],d['nets']-d['mult']-d['add']-d['bus'],d['clk']],
 "mult,add,bus":lambda d:[d['mult'],d['add'],d['bus'],d['nets']-d['mult']-d['add']-d['bus'],d['clk']],
 "core,bus,exp+ctl,clk":lambda d:[d['mult']+d['add'],d['bus'],d['exp']+d['ctl']+d['seq'],d['op']+d['res']+d['oth'],d['clk']],
 "core,bus,op,clk":lambda d:[d['mult']+d['add'],d['bus'],d['op'],d['nets']-d['mult']-d['add']-d['bus']-d['op'],d['clk']],
}
def X(rows,f): return np.array([[v*r['rate'] for v in f(r['d'])] for r in rows],float)
def fit(rows,f,w=None):
    A=X(rows,f); y=np.array([r['D'] for r in rows])
    if w is not None:
        A=A*w[:,None]; y=y*w
    sc=np.abs(A).max(axis=0); sc[sc==0]=1
    return np.linalg.lstsq(A/sc,y,rcond=None)[0]/sc
def rms(y,p): return float(np.sqrt(np.mean((np.array(y)-np.array(p))**2)))
FAMS=['E78','E86','E90','E92','E65b','E65pi','E67a','E67api','E67ix','E70lq','E70ls','E70alq','E60lb','E60ord','E79a16','E79b16','E79b16p','E79b16m','E79b32','E79b32p','E79a8','E79b8']
AF3=[r for r in F if r['card']=='a3']
C1=[r for r in F if r['card']=='c1']
def weights(rows):
    # every family counts as much as sqrt(n), so that the ladders do not swamp the kinds
    from collections import Counter
    c=Counter(r['exp'] for r in rows)
    return np.array([1/math.sqrt(c[r['exp']]) for r in rows])
print('leave one experiment out, fit on the rest of aifoundry3 floats (family-weighted), predict the left-out family; card 1 sets with E82 scale from fit on all aifoundry3')
hdr=[f for f in FAMS if any(r['exp']==f for r in AF3)]
print(f"{'model':24s} {'pooled':>7s} | "+" ".join(f"{s[:7]:>7s}" for s in hdr)+' |    E82s    E88     E94 | coef(all a3, family weighted)')
for n,f in MODELS.items():
    errs=[];row=[]
    for s in hdr:
        tr=[r for r in AF3 if r['exp']!=s]; te=[r for r in AF3 if r['exp']==s]
        b=fit(tr,f,weights(tr))
        p=X(te,f)@b
        row.append(rms([r['D'] for r in te],p)); errs+=list(np.array([r['D'] for r in te])-p)
    b=fit(AF3,f,weights(AF3))
    e82=[r for r in C1 if r['exp']=='E82']
    s82=float(np.linalg.lstsq((X(e82,f)@b)[:,None],np.array([r['D'] for r in e82]),rcond=None)[0][0])
    c1r=[rms([r['D'] for r in C1 if r['exp']==e],(X([r for r in C1 if r['exp']==e],f)@b)*s82) for e in('E82','E88','E94')]
    print(f"{n:24s} {float(np.sqrt(np.mean(np.square(errs)))):7.3f} | "+" ".join(f"{v:7.3f}" for v in row)+' | '+" ".join(f"{v:7.3f}" for v in c1r)+f" | s82 {s82:.3f} "+str([round(float(x)*1e15,2) for x in b]))
print()
print('fit on E78 only; same families out of sample')
for n,f in MODELS.items():
    E78=[r for r in AF3 if r['exp']=='E78']
    b=fit(E78,f)
    row=[rms([r['D'] for r in AF3 if r['exp']==s],X([r for r in AF3 if r['exp']==s],f)@b) for s in hdr]
    e82=[r for r in C1 if r['exp']=='E82']
    s82=float(np.linalg.lstsq((X(e82,f)@b)[:,None],np.array([r['D'] for r in e82]),rcond=None)[0][0])
    c1r=[rms([r['D'] for r in C1 if r['exp']==e],(X([r for r in C1 if r['exp']==e],f)@b)*s82) for e in('E82','E88','E94')]
    errs=np.concatenate([np.array([r['D'] for r in AF3 if r['exp']==s])-X([r for r in AF3 if r['exp']==s],f)@b for s in hdr if s!='E78'])
    print(f"{n:24s} {float(np.sqrt(np.mean(errs**2))):7.3f} | "+" ".join(f"{v:7.3f}" for v in row)+' | '+" ".join(f"{v:7.3f}" for v in c1r)+f" | s82 {s82:.3f} "+str([round(float(x)*1e15,2) for x in b]))
print()
# gated residuals under the bus model on E78
f=MODELS['bus']; E78=[r for r in AF3 if r['exp']=='E78']; b=fit(E78,f); p=X(E78,f)@b
print('E78 residual under bus (D-fit):',{r['key']:round(r['D']-q,2) for r,q in zip(E78,p) if abs(r['D']-q)>.2})
f=MODELS['M2 nets,clk']; b=fit(E78,f); p=X(E78,f)@b
print('E78 residual under M2 (D-fit):',{r['key']:round(r['D']-q,2) for r,q in zip(E78,p) if abs(r['D']-q)>.3})
# int8
I=[r for r in O if r['type']=='int8']
IM={"nets,clk":lambda d:[d['nets'],d['clk']],"nets-bus,bus,clk":lambda d:[d['nets']-d['bus'],d['bus'],d['clk']],"unit,rest,clk":lambda d:[d['unit'],d['nets']-d['unit'],d['clk']],"nets,clk,tog":lambda d:[d['nets'],d['clk'],d['tog']],"unit,bus,rest,clk":lambda d:[d['unit'],d['bus'],d['nets']-d['unit']-d['bus'],d['clk']]}
E78i=[r for r in I if r['exp']=='E78']
print('int8', sorted({r['exp'] for r in I}), len(I))
for n,f in IM.items():
    b=fit(E78i,f); p=X(E78i,f)@b
    loo=[float(X([E78i[i]],f)[0]@fit(E78i[:i]+E78i[i+1:],f)) for i in range(len(E78i))]
    out={}
    for e in sorted({r['exp'] for r in I}-{'E78'}):
        R=[r for r in I if r['exp']==e]
        out[e]=round(rms([r['D'] for r in R],X(R,f)@b),3)
    print(f"  {n:20s} fit {rms([r['D'] for r in E78i],p):.3f} loo {rms([r['D'] for r in E78i],loo):.3f} coef {[round(float(x)*1e15,2) for x in b]} {out}")
