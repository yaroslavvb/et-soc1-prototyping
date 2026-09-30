"""trace_an.py TRACE RUN: what the main thread and the raster threads did in each late frame of the camera moves."""
import json, sys, collections
tr = json.load(open(sys.argv[1]))['traceEvents']
run = json.load(open(sys.argv[2]))
# the renderer's main thread: the thread named CrRendererMain
names = {}
for e in tr:
    if e.get('ph') == 'M' and e.get('name') == 'thread_name': names[(e['pid'], e['tid'])] = e['args']['name']
main = [k for k, v in names.items() if v == 'CrRendererMain']
print('threads:', collections.Counter(names.values()).most_common(12))
# map rAF 'now' (ms, performance time origin) to trace ts (us): use the FireAnimationFrame / 'FunctionCall' of rAF
# simpler: Blink's 'BeginMainThreadFrame' / 'Animation Frame Fired' events on main; align by the recorder's frame count
log = run['log']
X = [e for e in tr if e.get('ph') == 'X' and 'dur' in e]
mainX = [e for e in X if (e['pid'], e['tid']) in main]
fires = sorted(e['ts'] for e in mainX if e['name'] == 'FireAnimationFrame')
print('FireAnimationFrame events:', len(fires), 'log rows:', len(log))
# per late frame (dt > 60 ms in the log), find the trace window between the two fires closest in time
t_first = log[0][0]; f_first = fires[0]
def at(ts0, ts1, evs):
    agg = collections.Counter()
    for e in evs:
        s, d = e['ts'], e['dur']
        a, b = max(s, ts0), min(s + d, ts1)
        if b > a: agg[e['name']] += (b - a) / 1000
    return agg
# align: rAF now -> ts via the offset that best matches the fire times
import bisect
off = f_first - t_first * 1000
late = [(i, log[i][0] - log[i - 1][0]) for i in range(1, len(log)) if log[i][0] - log[i - 1][0] > 45]
raster = [e for e in X if names.get((e['pid'], e['tid']), '').startswith(('CompositorTileWorker', 'VizCompositorThread', 'Compositor', 'CrGpuMain', 'ThreadPoolForeground'))]
for i, dt in late[:40]:
    t0 = log[i - 1][0] * 1000 + off; t1 = log[i][0] * 1000 + off
    # snap to the nearest fires
    j0 = bisect.bisect_left(fires, t0 - 8000); 
    m = at(t0, t1, mainX); r = at(t0, t1, raster)
    top = [(k, round(v, 1)) for k, v in m.most_common(8) if v > 2]
    rt = [(k, round(v, 1)) for k, v in r.most_common(5) if v > 2]
    print(f"frame {i} t={log[i][0]:.0f} dt={dt:.0f} step={log[i][1][:22]} zoom={log[i][4]} main: {top}\n      raster/gpu: {rt}")
