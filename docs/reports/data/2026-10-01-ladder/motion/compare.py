"""compare.py TAGA TAGB ... : the motion runs side by side: late camera frames, the worst frame, the largest velocity kink
per run, and each flow's camera time (the sum of its moves' frames)"""
import re, sys, os, glob
D = os.path.dirname(os.path.abspath(__file__))
def summ(tag):
    out = {}
    for ln in open(os.path.join(D, tag + '-summ.txt')):
        m = re.match(r'(\S+)\s+zoom frames: n=(\d+) median=([\d.]+) p95=([\d.]+) max=([\d.]+) late\(>25ms\)=(\d+) \(([\d.]+)%\)', ln)
        if m:
            k = os.path.basename(m[1]).split('-', 1)[1][:-5] if '-' in os.path.basename(m[1]) else m[1]
            out[k.replace(tag + '-', '')] = dict(n=int(m[2]), p95=float(m[4]), mx=float(m[5]), late=int(m[6]), pct=float(m[7]))
    return out
def kinks(tag):
    out, cur = {}, None
    p = os.path.join(D, tag + '-kink.txt')
    if not os.path.exists(p): return out
    for ln in open(p):
        if ln.startswith('## '): cur = ln[3:].strip(); out[cur] = []; continue
        m = re.search(r'frames\s+(\d+).*\(\s*([\d.]+)% of peak\)', ln)
        if m and cur: out[cur].append((int(m[1]), float(m[2])))
    return out
tags = sys.argv[1:]
S = {t: summ(t) for t in tags}; K = {t: kinks(t) for t in tags}
keys = sorted(set(k for t in tags for k in S[t]), key=lambda k: ['A', 'H', 'K', 'tour', 'up', 'dive', 'wrap'].index(k) if k in ['A', 'H', 'K', 'tour', 'up', 'dive', 'wrap'] else 99)
print(f"{'run':6s} " + ' | '.join(f"{t:>38s}" for t in tags))
for k in keys:
    row = []
    for t in tags:
        s = S[t].get(k)
        if not s: row.append(f"{'-':>38s}"); continue
        kk = K[t].get(k, [])
        km = max((x[1] for x in kk), default=0); fr = sum(x[0] for x in kk)
        row.append(f"frames {s['n']:5d} late {s['late']:3d} ({s['pct']:4.1f}%) max {s['mx']:6.1f}" + (f" kink {km:4.1f}% cam {fr}" if kk else ''))
    print(f"{k:6s} " + ' | '.join(row))
