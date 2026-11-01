import gzip,json,os
import numpy as np
D=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../docs/reports/data/2026-10-31-e89-heat-low-power/aifoundry3/e89/")
G,H,C=57400,249400,4096
out={}
for p in ("p8910","p8911"):
    tel=[json.loads(l) for l in gzip.open(D+p+"/telemetry.jsonl.gz","rt") if l.startswith("{")]
    t=np.array([r["t_ms"]/1000 for r in tel]);T=np.array([np.mean([(G+H*x/C-H/2)/1000 for x in r["pvt"]["c"]]) for r in tel]);P=np.array([r["board_w"] for r in tel])
    marks=[json.loads(l) for l in open(D+p+"/marks.jsonl")]
    runs=[json.loads(l) for l in open(D+p+"/runs.jsonl")]
    for mk in [m for m in marks if m["kind"]=="block"]:
        b=mk["block"]
        hk=sorted([h for h in marks if h["kind"]=="half" and h["block"]==b and h["role"]=="K"],key=lambda h:h["half"])
        for cy,h in enumerate(hk):
            q=sorted([r for r in runs if r["block"]==b and r["half"]==h["half"]],key=lambda r:r["t_start_ms"])
            s0=q[0]["t_start_ms"]/1000
            # the previous launch's last record end
            prev=[r for r in runs if r["block"]==b and r["t_end_ms"]/1000<s0]
            gap=s0-max(r["t_end_ms"] for r in prev)/1000 if prev else None
            post=(t>=s0+1)&(t<s0+3)
            a=(t>=s0-5)&(t<s0-.2);c1=np.polyfit(t[a]-(s0+2),T[a],1)
            g=(t>=s0-8)&(t<s0-2);c2=np.polyfit(t[g]-(s0+2),T[g],1)
            qq=(t>=s0-20)&(t<s0-.2);c3=np.polyfit(t[qq]-(s0+2),T[qq],2)
            out.setdefault(b,{}).setdefault(cy,[]).append((T[post].mean()-c1[1],T[post].mean()-c2[1],T[post].mean()-c3[2],gap))
for b,v in out.items():
    print(f"{b:9s}", " | ".join(f"c{cy}: line5 {np.mean([x[0] for x in vv]):.3f} gapfree {np.mean([x[1] for x in vv]):.3f} quad {np.mean([x[2] for x in vv]):.3f} gap {np.mean([x[3] for x in vv if x[3] is not None]) if any(x[3] is not None for x in vv) else float('nan'):.2f}s" for cy,vv in v.items()))
