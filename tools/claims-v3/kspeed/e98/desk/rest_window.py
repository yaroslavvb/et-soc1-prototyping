#!/usr/bin/env python3
# E98, desk, before the freeze. Usage: rest_window.py <dir of aifoundry2 history jsonl>
# Which rest window predicts the idle card's next 20 min best? Nine days of aifoundry2's own 5 s history (desk copy). Idle rows only.
import json, glob, os, statistics as st, math, sys
D=sys.argv[1]
rows=[]
for p in sorted(glob.glob(D+"/*.jsonl")):
    for l in open(p):
        try: r=json.loads(l)
        except: continue
        c=(r.get("cards") or [{}])[0]
        rows.append((r["t"]//1000, c.get("w"), c.get("die"), bool(c.get("held")), (r.get("temps") or {}).get("nic"), (r.get("temps") or {}).get("nvme"), r.get("load"), r.get("cpu")))
rows.sort()
t0=rows[0][0]; N=(rows[-1][0]-t0)//60+1
# 1-minute bins
W=[[] for _ in range(N)]; DIE=[[] for _ in range(N)]; NIC=[[] for _ in range(N)]; BUSY=[False]*N
for t,w,d,h,nic,nv,lo,cpu in rows:
    i=(t-t0)//60
    if h or (w is not None and w>26) or (d is not None and d>55): BUSY[i]=True
    if w is not None and not h: W[i].append(w); DIE[i].append(d)
    if nic is not None: NIC[i].append(nic)
mW=[st.mean(x) if len(x)>=6 else None for x in W]
mD=[st.mean(x) if len(x)>=6 else None for x in DIE]
mN=[st.mean(x) if len(x)>=6 else None for x in NIC]
def win(a,i,j):
    v=a[i:j]
    if any(x is None for x in v): return None
    return sum(v)/len(v)
ok=[False]*N
for i in range(N): ok[i]= (mW[i] is not None and not BUSY[i])
# candidates
res={}
pts=[]
for i in range(60,N-25,7):
    if not all(ok[i-45:i+20]): continue
    tgt=win(mW,i,i+20)
    tgtd=win(mD,i,i+20)
    pts.append((win(mW,i-1,i),win(mW,i-5,i),win(mW,i-15,i),win(mW,i-30,i),win(mN,i-15,i),win(mD,i-1,i),win(mD,i-15,i),tgt,tgtd,win(mW,i-45,i)))
print("points",len(pts))
names=["W 1min","W 5min","W 15min","W 30min","NIC 15min","die 1min","die 15min"]
def fit(x,y):
    mx,my=st.mean(x),st.mean(y); sxx=sum((a-mx)**2 for a in x); b=sum((a-mx)*(c-my) for a,c in zip(x,y))/sxx; a0=my-b*mx
    return b, math.sqrt(sum((c-a0-b*a)**2 for a,c in zip(x,y))/len(x)), sum((a-mx)*(c-my) for a,c in zip(x,y))/math.sqrt(sxx*sum((c-my)**2 for c in y))
for k,nm in enumerate(names):
    x=[p[k] for p in pts]; y=[p[7] for p in pts]; b,rms,r=fit(x,y)
    print(f"{nm:10s} predicts next 20 min mean W: slope {b:.3f} rms {rms:.4f} W r {r:.4f}")
# short-term scatter of the 1-min, 5-min, 15-min means about a 2-hour running mean
import itertools
def scatter(wn):
    d=[]
    for i in range(120,N-60,3):
        if not all(ok[i-60:i+60]): continue
        c=win(mW,i-60,i+60); a=win(mW,i,i+wn)
        if c is not None and a is not None: d.append(a-c)
    return st.pstdev(d) if d else None,len(d)
for wn in (1,5,15,30): print("scatter about 2 h mean, window",wn,"min:",scatter(wn))
# autocorrelation of 1-min W after removing a 2-hour running mean
sig=[]
for i in range(60,N-60):
    if all(ok[i-60:i+60]):
        sig.append((i,mW[i]-win(mW,i-60,i+60)))
s=dict(sig)
for lag in (1,2,3,5,7,10,12,15,20,30,45):
    a=[(s[i],s[i+lag]) for i in s if i+lag in s]
    if a:
        mx=st.mean(x for x,_ in a); my=st.mean(y for _,y in a)
        c=sum((x-mx)*(y-my) for x,y in a)/len(a)/(st.pstdev([x for x,_ in a])*st.pstdev([y for _,y in a]))
        print("lag",lag,"min autocorr",round(c,3),"n",len(a))
