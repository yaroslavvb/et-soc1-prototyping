#!/usr/bin/env python3
"""E147 (Q138), a design input read post hoc from E134's committed runs (no E147 data): does a zero read that follows a
large step read high? Each interior zero read's deviation from the line through its two neighbouring reads of the same zero
(board p_raw, E134's primary table) against the step of the item before it, less the mean step before its neighbours.
The slope is the board's carry-over per W of the preceding step, the noise that grows with E147's larger steps.

    python3 tools/claims-v3/e147/carry_e134.py [<data dir holding runs.csv and scored.json>]
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
R = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs/reports/data/2026-11-02-e134-bit-prices-more")) + "/"
runs=[r for r in csv.DictReader(open(R+'runs.csv'))]
sc=json.load(open(R+'scored.json'))['primary']['prices']
by={}
for r in runs:
    if r.get('fail') not in ('0','0.0',''): continue
    by.setdefault(int(float(r['pass'])),[]).append(r)
xs=[];ys=[]
for p,rr in sorted(by.items()):
    rr.sort(key=lambda r: float(r['t0_ms']))
    zeros=[i for i,r in enumerate(rr) if r['item'] in ('fp32.hq','fp32.aq','fp32.a67q') and r.get('segment') not in ('-1',)]
    for a,b,c in zip(zeros, zeros[1:], zeros[2:]):
        ra,rb,rc=rr[a],rr[b],rr[c]
        if not (ra['item']==rb['item']==rc['item']): continue
        ta,tb,tc=[float(x['t0_ms']) for x in (ra,rb,rc)]
        va,vb,vc=[float(x['p_raw']) for x in (ra,rb,rc)]
        dev=vb-(va+(vc-va)*(tb-ta)/(tc-ta))
        prev=rr[b-1]['item'][5:]
        step=sc.get(prev,{}).get('W',{}).get('mean')
        if step is None: continue
        # the steps of the items before the neighbour zeros too (they raise the line)
        pa=sc.get(rr[a-1]['item'][5:],{}).get('W',{}).get('mean') or 0
        pc=sc.get(rr[c-1]['item'][5:],{}).get('W',{}).get('mean') or 0
        xs.append(step-(pa+pc)/2); ys.append(dev)
n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
b=sxy/sxx; res=[y-my-b*(x-mx) for x,y in zip(xs,ys)]
se=(sum(e*e for e in res)/(n-2)/sxx)**0.5
print(f"E134 zero reads: n={n}; deviation from neighbours' line vs (preceding step - neighbours' preceding steps): slope {b:+.4f} +- {se:.4f} W per W; rms dev {(sum(y*y for y in ys)/n)**0.5:.3f} W; max |dev| {max(abs(y) for y in ys):.3f}")
big=[(x,y) for x,y in zip(xs,ys) if x>1.5]
print('after a step > 1.5 W above the neighbours\':', [(round(x,2),round(y,3)) for x,y in big])
