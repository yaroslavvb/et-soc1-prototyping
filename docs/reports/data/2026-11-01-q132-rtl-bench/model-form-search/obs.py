"""All tiles already read, with the bench's features: one list of observations for model exploration."""
import json, math, os, sys
import numpy as np
D=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))+'/'
Q=D+'2026-11-01-q132-rtl-bench/'
sys.path.insert(0,Q)
from analyze import ladder
CPO={"fp32":546,"fp16":546,"int8":318}
def load(p): return json.load(open(p))
def feat(m):
    s=m["vpu"]["by_stage"]
    return {"mult":s["multiplier"],"add":s["adder_norm"],"res":s["result"]+s["c_regfile"],"op":s["operand"],"bus":s["lane_operand_bus"],"exp":s["exponent"],"ctl":s["control"],"seq":s["vpu_sequencer"],"oth":s["other"],
            "clk":m["ff"]["all"]["clocked"],"tog":m["ff"]["all"]["toggles"],"scp":m["scp_reads"],"nets":m["vpu"]["nets_map"],"nets2":m["vpu"]["nets_hier2"],"unit":m["unit"]["nets_map"],"valid":m["valid_slots"],"clkt":m["ff"]["txfma"]["clocked"]+m["ff"]["tima"]["clocked"],"clkr":m["ff"]["rest"]["clocked"]}
def rate_of(t): return 600e6/CPO[t]*1024*0.9963
Z=load(Q+'counts-v2.json')['rows']
def row(exp,card,key,t,Dv,m,base=None,se=None,fam=None):
    z=base if base is not None else Z[t+'.zeros']['mean']
    fm,fz=feat(m),feat(z)
    return {"exp":exp,"card":card,"key":key,"type":t,"D":Dv,"se":se,"rate":rate_of(t),"d":{k:fm[k]-fz[k] for k in fm},"abs":fm,"fam":fam or exp}
def kinds_rows(exp,card,meas,counts,skip_zero=True):
    out=[]
    for k,v in counts.items():
        t,name=v["type"],v["kind"]
        it=meas.get(k) or meas.get(f"{t}.real_{name}")
        if not it or not isinstance(it.get("D"),dict) or name=="zeros": continue
        r=row(exp,card,k,t,it["D"]["mean"],v["mean"],se=it["D"].get("se"))
        r["rate"]=it["rate"]["mean"] if isinstance(it.get("rate"),dict) else r["rate"]
        out.append(r)
    return out
def all_obs(include=('e94',)):
    obs=[]
    obs+=kinds_rows('E78','a3',load(D+'2026-10-31-e78-kinds-energy-matrix/e78.json')['items'],Z)
    obs+=kinds_rows('E82','c1',load(D+'2026-10-31-e82-kinds-aifoundry1/e82.json')['items'],Z)
    obs+=kinds_rows('E86','a3',load(D+'2026-10-31-e86-real-tensors-energy/e86.json')['items'],load(Q+'counts-e86.json')['rows'])
    obs+=kinds_rows('E90','a3',load(D+'2026-10-31-e90-signs-spread/e90.json')['items'],load(Q+'counts-e90.json')['rows'])
    obs+=kinds_rows('E88','c1',load(D+'2026-10-31-e88-result-path/e88.json')['items'],load(Q+'counts-e88.json')['rows'])
    obs+=kinds_rows('E92','a3',load(D+'2026-11-01-e92-sign-split/e92.json')['items'],load(Q+'counts-e92.json')['rows'])
    if 'e94' in include:
        c=load(Q+'counts-e94e95.json')['rows']
        obs+=kinds_rows('E94','c1',load(D+'2026-11-01-e94-tile-spread/e94.json')['items'],{k:v for k,v in c.items() if not v['kind'].startswith(('r2_','real_'))})
    if 'e95' in include:
        c=load(Q+'counts-e94e95.json')['rows']
        import glob
        f=glob.glob(D+'2026-11-01-e95*/e95.json')[0]
        obs+=kinds_rows('E95','a3',load(f)['items'],{k:v for k,v in c.items() if v['kind'].startswith(('r2_','real_'))})
    hl=load(Q+'counts-hl.json')['rows']
    e65f=D+'2026-10-26-e65-bit-prices-hart-ladder/hl.json'; e67f=D+'2026-10-27-e67-a-side-bit-prices/hl-clean.json'; e70f=D+'2026-10-27-e70-saturation-ladder/hl.json'; e60f=D+'2026-10-20-bitflip-ladder/hl.json'
    sets=[("E65b",e65f,lambda it:"lq_h0",[f"bit_{j}" for j in range(32)]),("E65pi",e65f,lambda it:"lb_h0",[f"bpi_{j}" for j in (0,8,11,16,22)]),
          ("E67a",e67f,lambda it:"aq_e64" if it=="abit_30" else "aq_h0",[f"abit_{j}" for j in range(32)]),("E67api",e67f,lambda it:"ap_h0",[f"abp_{j}" for j in (0,8,11,16,22)]),
          ("E67ix",e67f,lambda it:"ix_z",[f"ix_{i}_{j}" for i in (0,8,16,22) for j in (0,8,16,22)]+[f"ix_a{i}" for i in (0,8,16,22)]+[f"ix_b{j}" for j in (0,8,16,22)]),
          ("E70lq",e70f,lambda it:"lq_h0",[f"lq_h{h}" for h in (1,2,3,4,6,8,12,16,23)]),("E70ls",e70f,lambda it:"lq_h0",[f"ls_h{h}" for h in (2,3,4,6,8,12,16)]),
          ("E70alq",e70f,lambda it:"aq_h0",[f"alq_h{h}" for h in (1,2,4,8,12,16,23)]),("E60lb",e60f,lambda it:"lb_h0",[f"lb_h{h}" for h in (1,2,4,8,12,16,23)]),
          ("E60ord",e60f,lambda it:"lq_h0",[f"ord_{o}_{p}" for o in ("gray","binary","shuffled","maxflip") for p in (0,19)])]
    for nm,f,base,items in sets:
        bs=sorted({base(i) for i in items})
        tbl={}
        for b_ in bs:
            tbl.update(ladder(f,b_,[i for i in items if base(i)==b_]))
        for it,v in tbl.items():
            kk="fp32."+it
            if kk not in hl: continue
            obs.append(row(nm,'a3',kk,'fp32',v["D"],hl[kk]["mean"],base=hl["fp32."+base(it)]["mean"],se=v.get("se"),fam=nm))
    hp=load(Q+'counts-hlp.json')['rows']; pr=load(D+'2026-10-31-e79-fp16-int8-bit-prices/hlp.json')['cards']['aifoundry3']['items']
    for name,x in pr.items():
        if not x.get('zero') or x.get('d_p80') is None: continue
        t=x['type']; kk,zk=f"{t}.{name}",f"{t}.{x['zero']}"
        if kk not in hp or zk not in hp: continue
        obs.append(row('E79'+x['family'],'a3',kk,t,float(x['d_p80']),hp[kk]['mean'],base=hp[zk]['mean'],fam='E79'+x['family']))
    return obs
