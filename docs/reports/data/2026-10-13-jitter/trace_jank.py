#!/usr/bin/env python3
"""trace_jank.py <trace.json> <jit.json> [--min 25] [--top 12]: for the late frames of a jit_probe run (frame gap over
--min ms while the camera moves), what the renderer's main thread did: trace events by name (time inside the gap) and,
from the V8 sampling profiler, the JS functions on the stack (self time, and the top-level function they ran under)."""
import json, sys, collections, bisect
args = sys.argv[1:]
MIN = float(args[args.index('--min') + 1]) if '--min' in args else 25.0
TOP = int(args[args.index('--top') + 1]) if '--top' in args else 12
T = json.load(open(args[0])); T = T['traceEvents'] if isinstance(T, dict) else T
J = json.load(open(args[1]))
names = {}
for e in T:
    if e.get('ph') == 'M' and e.get('name') == 'thread_name': names[(e['pid'], e['tid'])] = e['args']['name']
main = {k for k, v in names.items() if v == 'CrRendererMain'}
X = [e for e in T if e.get('ph') == 'X' and 'dur' in e and (e['pid'], e['tid']) in main]
fires = sorted(e['ts'] for e in X if e['name'] in ('FireAnimationFrame',))
# V8 samples: Profile (startTime) + ProfileChunk (nodes, samples, timeDeltas), per profile id
prof = {}; nodes = {}; samples = []
for e in T:
    if e.get('name') == 'Profile' and (e['pid'], e['tid']) in main:
        prof[e['id']] = e['args']['data'].get('startTime', e['ts'])
for e in sorted((e for e in T if e.get('name') == 'ProfileChunk'), key=lambda e: e['ts']):
    pid = e.get('id'); d = e['args']['data']; cp = d.get('cpuProfile', {})
    for n in cp.get('nodes', []): nodes[(pid, n['id'])] = n
    if pid not in prof: continue
    t = prof[pid]
    for sid, dt in zip(cp.get('samples', []), d.get('timeDeltas', [])):
        t += dt; samples.append((t, pid, sid))
    prof[pid] = t
samples.sort()
sts = [s[0] for s in samples]
def stack(pid, nid):
    out = []
    while (pid, nid) in nodes:
        n = nodes[(pid, nid)]; cf = n.get('callFrame', {})
        out.append(f"{cf.get('functionName') or '(anon)'}:{cf.get('lineNumber', -1) + 1}")
        nid = n.get('parent')
        if nid is None: break
    return out   # leaf first
# frames from the probe: [rafT, perfNow, tag, layers]; align perfNow (ms) to trace ts (us) by the fires
rows = [f for r in J['runs'] for f in r['frames']]
moving = set()
for i in range(1, len(rows)):
    if rows[i][3] != rows[i - 1][3]: moving.add(i)
ALL = '--all' in args; TAG = args[args.index('--tag') + 1] if '--tag' in args else ''
late = [(i, rows[i][0] - rows[i - 1][0]) for i in range(1, len(rows)) if (ALL or i in moving) and TAG in rows[i][2] and rows[i][0] - rows[i - 1][0] > MIN]
if not fires: raise SystemExit('no FireAnimationFrame in the trace')
# offset: try candidate offsets from the first fires and keep the one that puts most rAF times near a fire
cands = [fires[k] - rows[0][1] * 1000 for k in range(min(40, len(fires)))]
def score(off):
    s = 0
    for f in rows[::7]:
        t = f[1] * 1000 + off; j = bisect.bisect_left(fires, t)
        near = min([abs(fires[j] - t)] if j < len(fires) else [1e9] + [abs(fires[j - 1] - t)] if j else [1e9])
        s += near < 3000
    return s
off = max(cands, key=score)
print(f'late frames (> {MIN} ms) while moving: {len(late)} of {len(moving)}; offset score {score(off)} of {len(rows[::7])}')
evn = collections.Counter(); selff = collections.Counter(); tops = collections.Counter(); gaps = 0.0
for i, dt in late:
    t1 = rows[i][1] * 1000 + off; t0 = t1 - dt * 1000; gaps += dt
    for e in X:
        s, d = e['ts'], e['dur']
        a, b = max(s, t0), min(s + d, t1)
        if b > a and d < 5e6: evn[e['name']] += (b - a) / 1000
    j0, j1 = bisect.bisect_left(sts, t0), bisect.bisect_right(sts, t1)
    for t, pid, sid in samples[j0:j1]:
        st = stack(pid, sid)
        if not st: continue
        selff[st[0]] += 1
        user = [s for s in st if not s.startswith(('(program)', '(idle)', '(root)', '(garbage', '(anon):0'))]
        if user: tops[user[-1] if len(user) > 1 else user[0]] += 1
print(f'time in late frames: {gaps:.0f} ms')
print('\n== trace events in the late frames (ms, overlapping time, nested events counted in each)')
for k, v in evn.most_common(TOP): print(f'  {v:8.1f}  {k}')
print('\n== V8 samples in the late frames: self (leaf) functions')
for k, v in selff.most_common(TOP): print(f'  {v:6d}  {k}')
print('\n== ... and the outermost user function they ran under')
for k, v in tops.most_common(TOP): print(f'  {v:6d}  {k}')
