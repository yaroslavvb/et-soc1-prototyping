"""took_ms during waxis/y/hop3 bursts on both cards (v1), and the median elsewhere. Files only."""
import json, numpy as np
for host in ('aifoundry2','aifoundry3'):
    d=f'/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-24-wire-{host}/'
    tel=[json.loads(l) for l in open(d+'telemetry.jsonl')]; runs=[json.loads(l) for l in open(d+'runs.jsonl')]
    t=np.array([s['t_ms'] for s in tel])/1000; took=np.array([s.get('took_ms',0) for s in tel])
    g={}
    for r in runs: g.setdefault((r['cfg'],r['pass']),[]).append(r)
    allbusy=np.zeros(len(t),bool); ys=[]
    for (cfg,p),rs in g.items():
        lo=min(r['t_start_ms'] for r in rs)/1000; hi=max(r['t_end_ms'] for r in rs)/1000
        m=(t>=lo)&(t<=hi); allbusy|=m
        if cfg.startswith('waxis/y/hop3'): ys.append((cfg,p,int(m.sum()),float(np.median(took[m])) if m.sum() else None,float(took[m].max()) if m.sum() else None))
    print(host,'median took_ms in all bursts',np.median(took[allbusy]))
    for y in sorted(ys): print('  ',y)
