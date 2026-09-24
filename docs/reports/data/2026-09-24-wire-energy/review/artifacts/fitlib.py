import json, numpy as np, collections
FRZ = 244/512
def load(path="bursts.json"):
    return [b for b in json.load(open(path)) if b['ok']]
def line(pts):
    x=np.array([p[0] for p in pts],float); y=np.array([p[1] for p in pts],float)
    A=np.vstack([x,np.ones_like(x)]).T; c,*_=np.linalg.lstsq(A,y,rcond=None); return c[0],c[1]
def slopes(B, card, pre, key, hops, suffix=None):
    """per-pass slope of key vs hop for configs starting with pre"""
    by=collections.defaultdict(list)
    for b in B:
        if b['card']==card and b['cfg'].startswith(pre) and (suffix is None or b['cfg'].endswith(suffix)) and b['hop'] in hops:
            by[b['pass_']].append((b['hop'], b[key]))
    return {p: line(v)[0] for p,v in by.items() if len({h for h,_ in v})>=3}
def model(B, card, key, st="v2"):
    if st=="v2":
        defs=[(f"wu/p{q}/",2*float(q)*(1-float(q)),float(q),(1,2,3,4,6)) for q in ("0","0.25","0.5","0.75","1")]+[("wfrz/",0.0,FRZ,(1,3,6))]
    else:
        defs=[(f"wbern/p{q}/",2*float(q)*(1-float(q)),float(q),(1,2,3,4,6)) for q in ("0","0.1","0.25","0.5","0.75","0.9","1")]
    per=collections.defaultdict(list)
    for pre,tq,pq,hp in defs:
        for p,s in slopes(B,card,pre,key,hp).items(): per[p].append((tq,pq,s))
    res=[]
    for p,pts in per.items():
        A=np.array([[q[0],q[1],1] for q in pts]); y=np.array([q[2] for q in pts])
        c,*_=np.linalg.lstsq(A,y,rcond=None); res.append(c)
    c=np.mean(res,axis=0)
    return {"a_fJ":c[0]*125,"b_fJ":c[1]*125,"s0_pJBh":c[2]}
def sep(B, card, key, fam, hops):
    s5=slopes(B,card,f"{fam}/p0.5/",key,hops); s0=slopes(B,card,f"{fam}/p0/",key,hops)
    d=[(s5[k]-s0[k])*125 for k in s5 if k in s0]
    return np.mean(d), np.mean(list(s0.values()))*125
