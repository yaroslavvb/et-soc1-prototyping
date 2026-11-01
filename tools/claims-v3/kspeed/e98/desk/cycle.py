#!/usr/bin/env python3
# E98, desk, before the freeze. Usage: cycle.py <dir holding aifoundry1/ aifoundry2/ aifoundry3/ history jsonl>
# The idle card's 20 min cycle: its period, its phase on the wall clock, which boxes carry it. Desk copy of the boxes' own 5 s history.
import json, glob, statistics as st, math, time, os, sys
B=sys.argv[1]
def load(box,n=0):
    rows=[]
    for p in sorted(glob.glob(f"{B}/{box}/*.jsonl")):
        for l in open(p):
            try: r=json.loads(l)
            except: continue
            cs={c["n"]:c for c in (r.get("cards") or [])}
            c=cs.get(n,{})
            T=r.get("temps") or {}
            rows.append((r["t"]/1000.0,c.get("w"),c.get("die"),bool(c.get("held")),T.get("nic"),T.get("nvme"),T.get("cpu"),r.get("cpu"),r.get("load")))
    rows.sort()
    return rows
for box,n,bar in (("aifoundry2",0,26),("aifoundry3",0,27),("aifoundry1",1,34),("aifoundry1",0,22)):
    rows=load(box,n)
    # goertzel-like: for period P minutes, the amplitude of W after removing a 2 h running mean over idle stretches, in stretches of 6 h
    t0=rows[0][0]
    m={}
    for t,w,d,h,nic,nv,tc,cpu,lo in rows:
        if w is None or h or w>bar: continue
        i=int((t-t0)//60); m.setdefault(i,[]).append(w)
    mw={i:st.mean(v) for i,v in m.items() if len(v)>=6}
    keys=sorted(mw)
    detr={}
    for i in keys:
        v=[mw[j] for j in range(i-60,i+60) if j in mw]
        if len(v)>=100: detr[i]=mw[i]-st.mean(v)
    best=[]
    for P in (5,6,7.5,8,9,10,12,15,18,19,19.5,20,20.5,21,22,24,25,30,40,60):
        c=sum(v*math.cos(2*math.pi*i/P) for i,v in detr.items()); s=sum(v*math.sin(2*math.pi*i/P) for i,v in detr.items())
        best.append((round(2*math.sqrt(c*c+s*s)/max(1,len(detr)),4),P))
    print(box,"card",n,"n",len(detr),"amplitude W by period (top 6):",sorted(best,reverse=True)[:6])
    # fold on the wall clock: minute of the hour mod 20, W anomaly, the last 3 days vs the first 3 days
    for name,lo_,hi_ in (("first half",0,0.5),("second half",0.5,1.0)):
        kk=sorted(detr)
        a=kk[int(len(kk)*lo_)]; b=kk[min(len(kk)-1,int(len(kk)*hi_))]
        f={}
        for i,v in detr.items():
            if a<=i<=b:
                mm=int(((t0+i*60)//60)%20)
                f.setdefault(mm,[]).append(v)
        print("  ",name,"wall minute mod 20:"," ".join(f"{mm}:{st.mean(f[mm])*1000:+.0f}" for mm in sorted(f)))
# a2 host: CPU % and package temp folded the same way
rows=load("aifoundry2",0)
f={};g={};h2={}
for t,w,d,h,nic,nv,tc,cpu,lo in rows:
    mm=int((t//60)%20)
    if cpu is not None: f.setdefault(mm,[]).append(cpu)
    if lo is not None: g.setdefault(mm,[]).append(lo)
    if nic is not None: h2.setdefault(mm,[]).append(nic)
print("a2 host cpu% by wall minute mod 20:"," ".join(f"{m}:{st.mean(v):.1f}" for m,v in sorted(f.items())))
print("a2 load by wall minute mod 20:"," ".join(f"{m}:{st.mean(v):.2f}" for m,v in sorted(g.items())))
print("a2 nic by wall minute mod 20:"," ".join(f"{m}:{st.mean(v):.2f}" for m,v in sorted(h2.items())))
