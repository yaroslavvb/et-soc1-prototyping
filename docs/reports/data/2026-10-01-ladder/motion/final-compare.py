# mcompare.py CPU : the final check's motion runs at a CPU slowdown, bb0eb78 against head, rep by rep:
# summ.py's frames in motion and late frames (over 25 ms), and moves.py's kink (mean/max over the moves) and longest move
import re, sys, glob, os
D = '/home/yaroslavvb/claude/work/ladder/final/motion'
cpu = sys.argv[1]
RUNS = ['A', 'H', 'K', 'up', 'dive', 'loop', 'load', 'tabs', 'out', 'in']
def summ(tag):
    out = {}
    p = f'{D}/{tag}-summ.txt'
    if not os.path.exists(p): return out
    for line in open(p):
        m = re.search(r'-r\d+-(\w+)\.json\s+zoom frames: n=(\d+) .*?max=([\d.]+) late\(>25ms\)=(\d+) \(([\d.]+)%\)', line)
        if m: out[m.group(1)] = (int(m.group(2)), float(m.group(3)), int(m.group(4)), float(m.group(5)))
    return out
def moves(tag):
    out, cur = {}, None
    p = f'{D}/{tag}-moves.txt'
    if not os.path.exists(p): return out
    for line in open(p):
        if line.startswith('## '): cur = line[3:].strip(); out[cur] = []; continue
        m = re.match(r'\s*\d+ n=\s*(\d+)\s+(\d+) ms late (\d+) max\s+([\d.]+)\s+peak\s+([\d.]+)\s+kink\s+(\d+)%\s+first\s+(\d+)%', line)
        if m and cur: out[cur].append(tuple(float(x) for x in m.groups()))
    return out
tags = sorted({os.path.basename(p)[:-len('-summ.txt')] for p in glob.glob(f'{D}/*-c{cpu}-r*-summ.txt')})
S = {t: summ(t) for t in tags}; M = {t: moves(t) for t in tags}
print(f'CPU x{cpu}; runs: {", ".join(tags)}')
print('run   ' + ''.join(f'{t:>34}' for t in tags))
for r in RUNS:
    row = f'{r:6}'
    for t in tags:
        s = S[t].get(r); mv = M[t].get(r, [])
        if not s: row += f'{"-":>34}'; continue
        n, mx, late, pct = s
        kink = max((x[5] for x in mv), default=0); kmean = sum(x[5] for x in mv) / len(mv) if mv else 0
        lng = max((x[1] for x in mv), default=0)
        row += f'{f"{late}/{n} {pct:.1f}% mx{mx:.0f} k{kmean:.0f}/{kink:.0f} L{lng:.0f}":>34}'
    print(row)
print('(late/n: frames over 25 ms of the frames in motion; mx: the longest frame, ms; k mean/max: moves.py kink %; L: the longest move, ms)')
