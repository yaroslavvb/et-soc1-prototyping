"""compare-p2.py TAG... : part 2's motion runs side by side (TAG-summ.txt, TAG-kink.txt in this folder): per run, the
camera frames, the late ones (over 25 ms), the worst frame, the largest velocity kink (% of the move's peak) and the
camera's frames by the kink script (the sum of its moves' frames)"""
import os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
def summ(tag):
    out = {}
    p = os.path.join(D, tag + '-summ.txt')
    if not os.path.exists(p): return out
    for ln in open(p):
        m = re.match(r'(\S+)\s+zoom frames: n=(\d+) median=([\d.]+) p95=([\d.]+) max=([\d.]+) late\(>25ms\)=(\d+) \(([\d.]+)%\)', ln)
        if m:
            k = os.path.basename(m[1])[:-5].rsplit('-', 1)[1]   # (the run's name: the file's last part)
            out[k] = dict(n=int(m[2]), mx=float(m[5]), late=int(m[6]), pct=float(m[7]))
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
order = ['load', 'tabs', 'out', 'in', 'A', 'H', 'K', 'tour']
keys = sorted(set(k for t in tags for k in S[t]), key=lambda k: order.index(k) if k in order else 99)
print(f"{'run':5s} " + ' | '.join(f"{t:>44s}" for t in tags))
for k in keys:
    row = []
    for t in tags:
        s = S[t].get(k)
        if not s: row.append(f"{'-':>44s}"); continue
        kk = K[t].get(k, [])
        km = max((x[1] for x in kk), default=0); fr = sum(x[0] for x in kk)
        row.append(f"{s['n']:5d} fr, late {s['late']:3d} ({s['pct']:4.1f}%) max {s['mx']:5.1f}" + (f" kink {km:4.1f}%" if kk else ''))
    print(f"{k:5s} " + ' | '.join(row))
