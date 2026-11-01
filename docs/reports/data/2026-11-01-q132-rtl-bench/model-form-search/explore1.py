import sys, json, math, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from obs import all_obs
O=all_obs(('e94',))
print(len(O))
MODELS={
 "M2 nets,clk":lambda d:[d['nets'],d['clk']],
 "M2u unit,clk":lambda d:[d['unit'],d['clk']],
 "bus":lambda d:[d['nets']-d['bus'],d['bus'],d['clk']],
 "bus+op":lambda d:[d['nets']-d['bus']-d['op'],d['bus']+d['op'],d['clk']],
 "scp":lambda d:[d['nets'],d['clk'],d['scp']],
 "tog":lambda d:[d['nets'],d['clk'],d['tog']],
 "mult":lambda d:[d['mult'],d['nets']-d['mult'],d['clk']],
 "mult,add":lambda d:[d['mult'],d['add'],d['nets']-d['mult']-d['add'],d['clk']],
 "mult,bus":lambda d:[d['mult'],d['bus'],d['nets']-d['mult']-d['bus'],d['clk']],
 "mult,add,bus":lambda d:[d['mult'],d['add'],d['bus'],d['nets']-d['mult']-d['add']-d['bus'],d['clk']],
 "clkt,clkr":lambda d:[d['nets'],d['clkt'],d['clkr']],
}
def X(rows,f): return np.array([[v*r['rate'] for v in f(r['d'])] for r in rows],float)
def fit(rows,f):
    A=X(rows,f); y=np.array([r['D'] for r in rows]); sc=np.abs(A).max(axis=0); sc[sc==0]=1
    b=np.linalg.lstsq(A/sc,y,rcond=None)[0]/sc
    return b
def rms(y,p): return float(np.sqrt(np.mean((np.array(y)-np.array(p))**2)))
isfloat=lambda r:r['type'] in('fp32','fp16')
E78=[r for r in O if r['exp']=='E78' and isfloat(r)]
E82=[r for r in O if r['exp']=='E82' and isfloat(r)]
sets=['E86','E90','E92','E65b','E65pi','E67a','E67api','E67ix','E70lq','E70ls','E70alq','E60lb','E60ord','E79a16','E79b16','E79b32','E79b32p','E79b16p','E79b16m','E79a8']
c1sets=['E88','E94']
print(f"{'model':16s} {'coef fJ':36s} fit  loo | "+" ".join(f"{s[:7]:>7s}" for s in sets+c1sets))
for n,f in MODELS.items():
    b=fit(E78,f)
    p=X(E78,f)@b; y=[r['D'] for r in E78]
    loo=[float(X([E78[i]],f)[0]@fit(E78[:i]+E78[i+1:],f)) for i in range(len(E78))]
    s82=float(np.linalg.lstsq((X(E82,f)@b)[:,None],np.array([r['D'] for r in E82]),rcond=None)[0][0])
    row=[]
    for s in sets:
        R=[r for r in O if (r['exp']==s) and isfloat(r)]
        row.append(rms([r['D'] for r in R],X(R,f)@b) if R else float('nan'))
    for s in c1sets:
        R=[r for r in O if (r['exp']==s) and isfloat(r)]
        row.append(rms([r['D'] for r in R],(X(R,f)@b)*s82) if R else float('nan'))
    print(f"{n:16s} {str([round(x*1e15,2) for x in b]):36s} {rms(y,p):.3f} {rms(y,loo):.3f} | "+" ".join(f"{v:7.3f}" for v in row), 's82',round(s82,3))
print([ (s,sum(1 for r in O if r['exp']==s and isfloat(r))) for s in sets+c1sets])
# frozen predictions vs E94
P=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','e94-e95-bench-prediction.json')))['models']['vpu_map']['e94_card1']
e=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','2026-11-01-e94-tile-spread','e94.json')))['items']
res={}
for k,v in P.items():
    d=e[k]['D']['mean']
    res.setdefault(v['type'],[]).append((k,d,v['D_w'],v['lo95'],v['hi95']))
for t,v in res.items():
    print(t,'n',len(v),'rms',round(rms([x[1] for x in v],[x[2] for x in v]),3),'bias',round(float(np.mean([x[2]-x[1] for x in v])),3),'covered',sum(1 for x in v if x[3]<=x[1]<=x[4]))
    if 1:
        for x in sorted(v,key=lambda z:z[1]-z[2])[:4]+sorted(v,key=lambda z:z[1]-z[2])[-3:]:
            print('   ',x[0],'meas',round(x[1],2),'pred',round(x[2],2))
