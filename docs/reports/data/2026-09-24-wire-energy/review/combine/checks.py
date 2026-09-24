"""Cross-checks on wire.json (pipeline output) for the combined verdict. Reads files only."""
import json, numpy as np
B='/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-24-wire-energy/'
W=json.load(open(B+'wire.json')); R=json.load(open(B+'report.json')); C=W['configs']
L=R['inputs']['hop_mm']['value']
def m(cfg,key,card=None):
    c=C.get(cfg)
    if not c or key not in c: return None
    return c[key]['mean'] if card is None else c[key]['per_card'][card]['mean']
cards=['aifoundry2','aifoundry3']
print('== d=1 totals: all-ones vs random vs zeros (wu) ==')
for key in ('noc_pj_per_byte','pj_per_byte'):
    for d in (0,1,2,3,4,6):
        p1,p5,p0=m(f'wu/p1/hop{d}',key),m(f'wu/p0.5/hop{d}',key),m(f'wu/p0/hop{d}',key)
        print(f'{key:16s} d={d} P1 {p1:.3f} P.5 {p5:.3f} P0 {p0:.3f}  P1/P.5 {p1/p5:.3f}')
print('== d=1 wu vs wsep ==')
for key in ('noc_pj_per_byte','pj_per_byte'):
    for card in cards+[None]:
        r_u,r_s=m('wu/p0.5/hop1',key,card),m('wsep/p0.5/hop1',key,card)
        z_u,z_s=m('wu/p0/hop1',key,card),m('wsep/p0/hop1',key,card)
        print(f'{key:16s} {card}: random wu {r_u:.3f} wsep {r_s:.3f} ({100*(r_u/r_s-1):+.1f}%)  zeros wu {z_u:.3f} wsep {z_s:.3f} ({100*(z_u/z_s-1):+.1f}%)  data wu {r_u-z_u:.3f} wsep {r_s-z_s:.3f} ({100*((r_u-z_u)/(r_s-z_s)-1):+.1f}%)')
print('== participants / GB/s wsep vs wu ==')
for d in (1,2,3,4,5,6):
    for s in ('wu','wsep'):
        c=C.get(f'{s}/p0.5/hop{d}')
        if c: print(f'{s} d={d} participants {c["participants"]} readers(shires) {c["participants"]/32:.0f} GB/s {c["gb_s"]:.0f} per-shire {c["gb_s"]/(c["participants"]/32):.1f}')
print('== axes d=1-2 and d=1-3, random minus zeros slope, fJ/bit/hop ==')
def slope(xs,ys):
    return np.polyfit(xs,ys,1)[0]
for key in ('noc_pj_per_byte','pj_per_byte'):
    for ax in ('x','y'):
        for card in cards:
            for ds in ((1,2),(1,2,3)):
                xs=[d for d in ds if C.get(f'waxis/{ax}/hop{d}/p0.5') and C[f'waxis/{ax}/hop{d}/p0.5'][key]['per_card'].get(card)]
                if len(xs)<2: print(key,ax,card,ds,'n/a'); continue
                if len(xs)<len(ds): print(key,ax,card,ds,'missing', set(ds)-set(xs)); continue
                ys=[m(f'waxis/{ax}/hop{d}/p0.5',key,card)-m(f'waxis/{ax}/hop{d}/p0',key,card) for d in xs]
                zs=[m(f'waxis/{ax}/hop{d}/p0',key,card) for d in xs]
                print(f'{key:16s} {ax} {card} d={ds}: data {125*slope(xs,ys):.1f}  zeros {125*slope(xs,zs):.1f}  random {125*slope(xs,[a+b for a,b in zip(ys,zs)]):.1f}')
print('pipeline axes', {k:(round(v['mean'],1), {c:round(v['per_card'][c]['mean'],1) for c in v.get('per_card',{})}) for k,v in W['axes'].items() if 'random_bit' in k})
print('== alt:N slopes per d-step (NoC and board), shortfall fraction ==')
M1n=W['model']['v1']['noc_rail']; M1b=W['model']['v1']['board']
for key,M in (('noc_pj_per_byte',M1n),('pj_per_byte',M1b)):
    a=M['toggle_fj_per_bit_transition_hop']['mean']*8/1000
    for d in (1,3,6):
        small=np.mean([m(f'walt/n{n}/hop{d}',key) for n in (16,32,64,128)]); big=m(f'walt/n256/hop{d}',key)
        print(f'{key:16s} d={d}: small {small:.3f} n256 {big:.3f} excess {big-small:.3f}')
    sm=[np.mean([m(f'walt/n{n}/hop{d}',key) for n in (16,32,64,128)]) for d in (1,3,6)]
    bg=[m(f'walt/n256/hop{d}',key) for d in (1,3,6)]
    ex_slope=slope([1,3,6],[b-s for b,s in zip(bg,sm)])
    print(f'   excess slope {ex_slope:.3f} pJ/B/hop = {ex_slope/a:.2f} of a (a={a:.3f} pJ/B/hop per unit transition)')
    P=W['patterns']
    print('   pattern slopes', {n:round(P[f'alt:{n}'][key.replace("noc_pj_per_byte","noc_pj_per_byte")]['slope']['mean'],3) if key in P[f'alt:{n}'] else None for n in (16,32,64,128,256)})
print('== exit cost in hops: (intercept over d=1..6 - d0)/slope ==')
for key in ('noc_pj_per_byte','pj_per_byte'):
    for pre,ds in (('wu/p0.5/hop',(1,2,3,4,6)),('wu/p0/hop',(1,2,3,4,6)),('wu/p1/hop',(1,2,3,4,6)),('wsep/p0.5/hop',(1,2,3,4,5)),('wsep/p0/hop',(1,2,3,4,5))):
        xs=[d for d in ds if C.get(pre+str(d))]; ys=[m(pre+str(d),key) for d in xs]
        s,i=np.polyfit(xs,ys,1); e0=m(pre.replace('wsep','wu')+'0',key)
        print(f'{key:16s} {pre:14s} slope {s:.3f} int {i:.3f} d0 {e0:.3f} exit {(i-e0)/s:+.2f} hops')
    # data part
    for a_,b_,ds in (('wu/p0.5/hop','wu/p0/hop',(1,2,3,4,6)),('wsep/p0.5/hop','wsep/p0/hop',(1,2,3,4,5))):
        ys=[m(a_+str(d),key)-m(b_+str(d),key) for d in ds]; s,i=np.polyfit(ds,ys,1)
        e0=m('wu/p0.5/hop0',key)-m('wu/p0/hop0',key)
        print(f'{key:16s} data {a_[:4]}: slope {s:.3f} int {i:.3f} d0 {e0:.3f} exit {(i-e0)/s:+.2f} hops')
print('== linearity: d=4 above line through 1,2,3,6 ==')
for key in ('noc_pj_per_byte','pj_per_byte'):
    for p in ('0','0.5','1'):
        xs=[1,2,3,6]; ys=[m(f'wu/p{p}/hop{d}',key) for d in xs]; s,i=np.polyfit(xs,ys,1)
        print(f'{key:16s} wu P={p}: d4 {m(f"wu/p{p}/hop4",key):.3f} line {i+4*s:.3f} {100*(m(f"wu/p{p}/hop4",key)/(i+4*s)-1):+.1f}%')
    for p in ('0','0.5'):
        xs=[1,2,3,5]; ys=[m(f'wsep/p{p}/hop{d}',key) for d in xs]; s,i=np.polyfit(xs,ys,1)
        print(f'{key:16s} wsep P={p}: d4 {m(f"wsep/p{p}/hop4",key):.3f} line {i+4*s:.3f} {100*(m(f"wsep/p{p}/hop4",key)/(i+4*s)-1):+.1f}%')
