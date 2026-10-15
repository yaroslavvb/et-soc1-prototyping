#!/usr/bin/env python3
"""compare.py BEFORE.json AFTER.json : the texts past a frame or the visible area, and the pairs of texts whose ink
meets, on every scale, before and after this round's fixes (measure.mjs output). Prints what went away, what stays
and anything new."""
import json, sys

def load(p):
    d = json.load(open(p))
    out = {}
    for r in d['res']:
        if r.get('err'):
            out[r['id']] = None
            continue
        over = {}
        for o in r.get('over', []):
            what = [k for k in ('fr', 'fl', 'fb', 'vr', 'vl', 'vb', 'vt') if o.get(k, 0) > 0.5]
            over[o['s']] = (what, max(o.get(k, 0) for k in what) if what else 0)
        pairs = {}
        for p in r.get('pairs', []):
            pairs[tuple(sorted((p['a'], p['b'])))] = (p['ox'], p['oy'])
        out[r['id']] = {'over': over, 'pairs': pairs, 'atOk': r.get('atOk'), 'n': r.get('n')}
    return d['W'], d['H'], out

W, H, A = load(sys.argv[1])
_, _, B = load(sys.argv[2])
print(f'== {W}x{H}: {len(A)} scales before, {len(B)} after')
gone_o = new_o = kept_o = gone_p = new_p = kept_p = 0
for sid in sorted(set(A) | set(B)):
    a, b = A.get(sid), B.get(sid)
    if a is None or b is None:
        print(f'  {sid}: missing or error (before {a is not None}, after {b is not None})')
        continue
    if not b['atOk']:
        print(f'  {sid}: NOT AT its path after')
    for s in sorted(set(a['over']) | set(b['over'])):
        ia, ib = s in a['over'], s in b['over']
        if ia and not ib:
            gone_o += 1; print(f'  {sid}: fixed  over {a["over"][s]} {s[:70]!r}')
        elif ib and not ia:
            new_o += 1; print(f'  {sid}: NEW    over {b["over"][s]} {s[:70]!r}')
        else:
            kept_o += 1; print(f'  {sid}: stays  over {a["over"][s]} -> {b["over"][s]} {s[:70]!r}')
    for p in sorted(set(a['pairs']) | set(b['pairs'])):
        ia, ib = p in a['pairs'], p in b['pairs']
        if ia and not ib:
            gone_p += 1; print(f'  {sid}: fixed  pair {a["pairs"][p]} {p[0][:40]!r} x {p[1][:40]!r}')
        elif ib and not ia:
            new_p += 1; print(f'  {sid}: NEW    pair {b["pairs"][p]} {p[0][:40]!r} x {p[1][:40]!r}')
        else:
            kept_p += 1; print(f'  {sid}: stays  pair {a["pairs"][p]} -> {b["pairs"][p]} {p[0][:40]!r} x {p[1][:40]!r}')
print(f'== over: {gone_o} fixed, {kept_o} stay, {new_o} new; pairs: {gone_p} fixed, {kept_p} stay, {new_p} new')
