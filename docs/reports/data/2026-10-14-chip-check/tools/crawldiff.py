#!/usr/bin/env python3
"""crawldiff.py BEFORE_DIR AFTER_DIR OUT.md : what a reader sees that changed between two crawls of the chip diagram
(crawl.mjs output): every scale's own panel and every part's panel, every flow stage's caption and panel, every tour
slide, the static sections and the facts table. One section per changed text, as a unified word-level diff."""
import json, sys, difflib, re, os

A, B, OUT = sys.argv[1:4]

def load(d, f):
    p = os.path.join(d, f)
    return json.load(open(p)) if os.path.exists(p) else None

def texts(d):
    t = {}
    st = load(d, 'static.json') or {}
    for k in ('summary', 'honest'):
        t[f'static/{k}'] = st.get(k) or ''
    t['static/bodytext'] = st.get('bodytext') or ''
    for row in st.get('facts', [])[1:]:
        if row and row[0]: t[f'fact/{row[0]}'] = ' | '.join(row[1:])
    for i, row in enumerate(st.get('asks', [])[1:]): t[f'ask/{i}'] = ' | '.join(row)
    for i, row in enumerate(st.get('electrons', [])[1:]): t[f'electrons/{i}'] = ' | '.join(row)
    for s in load(d, 'scales.json') or []:
        sid = s.get('id') or s.get('path')
        t[f'scale/{sid}/here'] = s.get('here') or ''
        seen = {}
        for p in s.get('parts', []):
            k = p.get('key') or p.get('label')
            seen[k] = seen.get(k, 0) + 1
            kk = k if seen[k] == 1 else f'{k}#{seen[k]}'
            t[f'scale/{sid}/part/{kk}'] = (p.get('label') or '') + '\n' + (p.get('panel') or '')
    for fl in load(d, 'flows.json') or []:
        for st_ in fl['stages']:
            c = st_['cap']
            t[f"flow/{fl['flow']}/{st_['i']}"] = f"{c.get('k','')}\n{c.get('cap','')}\n{c.get('sub','')}\n{' / '.join(c.get('stages', []))}\n--panel--\n{st_.get('panel') or ''}"
    for tr in load(d, 'tour.json') or []:
        c = tr['cap']
        t[f"tour/{tr['i']}"] = f"{c.get('k','')}\n{c.get('cap','')}\n{c.get('sub','')}\n--panel--\n{tr.get('panel') or ''}"
    return t

ta, tb = texts(A), texts(B)
keys = sorted(set(ta) | set(tb))
tok = lambda s: re.findall(r'\S+|\n', s)
n = 0
with open(OUT, 'w') as fh:
    for k in keys:
        a, b = ta.get(k), tb.get(k)
        if a == b: continue
        n += 1
        fh.write(f'## {k}\n')
        if a is None: fh.write('(new)\n```\n' + b[:3000] + '\n```\n\n'); continue
        if b is None: fh.write('(gone)\n```\n' + a[:3000] + '\n```\n\n'); continue
        sm = difflib.SequenceMatcher(None, tok(a), tok(b), autojunk=False)
        ta_, tb_ = tok(a), tok(b)
        out = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                seg = ta_[i1:i2]
                out.append(' '.join(seg) if len(seg) <= 24 else ' '.join(seg[:10]) + ' … ' + ' '.join(seg[-10:]))
            else:
                if i2 > i1: out.append('[-' + ' '.join(ta_[i1:i2]) + '-]')
                if j2 > j1: out.append('{+' + ' '.join(tb_[j1:j2]) + '+}')
        fh.write(' '.join(out).replace(' \n ', '\n') + '\n\n')
print(f'{n} changed texts of {len(keys)} -> {OUT}')
