#!/usr/bin/env python3
"""At a fixed 600 MHz clock, does the work per cycle change with die temperature?

(1) The heater launches (sparsity_host, TensorFMA fp32 random data, launch >= 0): cycles per op and the implied clock
    (cycles_max / wall), binned by the card's 34-sensor mean during the launch.
(2) The version-3 catalogue on aifoundry2 (enercat, fixed 240 M-cycle launches): ops per cycle per hart of each
    configuration in the hot passes (hold 88 C: p3, p6, p9, p11) against the warm passes (p1, p4, p7, p10), all at 600 MHz.
    Memory configurations (dram, scp, wire) would show a refresh or a DRAM-timing change; arithmetic ones a pipeline one.
The overheating experiments' directory is left out (reductions/oh2.json has their cycles per operation).
Writes docs/reports/data/2026-09-28-overheating/analysis/timing_vs_temp.json.
Usage: python3 timing_vs_temp.py [docs/reports/data]
"""
import bisect, collections, gzip, json, os, re, statistics as st, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'timing_vs_temp.json')
EXCLUDE = '2026-09-28-overheating'


def card_of(p):
    for c in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
        if c in p:
            return c
    return None


def lines_of(p):
    op = gzip.open if p.endswith('.gz') else open
    try:
        with op(p, 'rt', errors='replace') as fh:
            yield from fh
    except (OSError, EOFError):
        return


TEL = collections.defaultdict(list)
HEAT = []
for d, _, fs in os.walk(ROOT):
    if EXCLUDE in d:
        continue
    for f in fs:
        if not re.search(r'\.(jsonl|out)(\.gz)?$', f):
            continue
        p = os.path.join(d, f)
        c = card_of(p)
        if c is None or os.path.basename(p).startswith('guard'):
            continue
        for line in lines_of(p):
            if '"temp_c"' in line and '"t_ms"' in line:
                try:
                    s = json.loads(line[line.find('{'):])
                except ValueError:
                    continue
                ms = (s.get('temp_c') or {}).get('minshire')
                mhz = (s.get('mhz') or {}).get('minion')
                if isinstance(ms, list) and ms:
                    TEL[c].append((s['t_ms'], ms[0], mhz))
            elif line.startswith('SPARSITY {') and '"test":"fma"' in line:
                try:
                    r = json.loads(line[9:])
                except ValueError:
                    continue
                if (r.get('launch', -1) >= 0 and r.get('type') == 'fp32' and r.get('values') == 'randn'
                        and r.get('pattern') == 'none' and r.get('iters', 0) >= 100000):
                    HEAT.append((c, r))
for c in TEL:
    TEL[c].sort()
KEYS = {c: [x[0] for x in TEL[c]] for c in TEL}


def during(c, t0, t1, pad=300):
    k = KEYS.get(c, [])
    a, b = bisect.bisect_left(k, t0 - pad), bisect.bisect_right(k, t1 + pad)
    return TEL[c][a:b]


print('(1) heater launches: TensorFMA fp32 random, cycles per op and implied GHz by die mean (all samples at 600 MHz)')
BINS = [(40, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
agg = collections.defaultdict(list)
seen = set()
for c, r in HEAT:
    key = (c, r['t_start_ms'], r['cycles_max'])
    if key in seen:
        continue
    seen.add(key)
    xs = during(c, r['t_start_ms'], r['t_end_ms'])
    if not xs or any(x[2] not in (600, None) for x in xs):
        continue                                   # only launches whose every sample read 600 MHz
    T = max(x[1] for x in xs)
    b = next((b for b in BINS if b[0] <= T < b[1]), None)
    if b is None:
        continue
    agg[(c, b)].append((r['cycles_per_op'], r['ghz'], r['minions']))
print('%-14s %-7s %6s %12s %12s %12s %10s' % ('card', 'die C', 'n', 'cyc/op med', 'cyc/op min', 'cyc/op max', 'GHz med'))
for (c, b) in sorted(agg):
    v = agg[(c, b)]
    cpo = [x[0] for x in v]
    print('%-14s %-7s %6d %12.3f %12.3f %12.3f %10.4f' % (c, '%d-%d' % b, len(v), st.median(cpo), min(cpo), max(cpo),
                                                     st.median(x[1] for x in v)))

print()
print('(2) aifoundry2 catalogue: bytes per cycle (memory configs) or ops per cycle per hart, hot passes (hold 88 C) against warm passes, same configuration')
base = os.path.join(ROOT, '2026-09-25-claims-v3/raw/aifoundry2/cat')
per = collections.defaultdict(lambda: collections.defaultdict(list))
temps = collections.defaultdict(list)
for pdir in sorted(os.listdir(base)):
    pj = json.load(open(os.path.join(base, pdir, 'pass.json')))
    cond = pj.get('cond')
    if cond not in ('H', 'W'):
        continue
    ch = json.load(open(os.path.join(base, pdir, 'check.json')))
    temps[cond].append((pdir, ch['die_c_busy_mean']))
    for line in lines_of(os.path.join(base, pdir, 'runs.jsonl.gz')):
        r = json.loads(line)
        if r.get('ok') and r.get('cycles_max'):
            # bytes per cycle (whole chip) for memory configurations, ops per cycle per hart otherwise
            m = r['bytes'] / r['cycles_max'] if r.get('bytes') else r['ops'] / r['cycles_max'] / r['participants']
            per[r['cfg']][cond].append(m)
print('passes:', dict(temps))
rows = []
for cfg in sorted(per):
    h, w = per[cfg]['H'], per[cfg]['W']
    if len(h) >= 4 and len(w) >= 4:
        mh, mw = st.median(h), st.median(w)
        sdw = st.pstdev(w) / mw if mw else 0
        rows.append((cfg, len(w), len(h), mw, mh, (mh / mw - 1) * 100 if mw else 0, sdw * 100))
print('%-26s %4s %4s %10s %10s %8s %9s' % ('config', 'nW', 'nH', 'warm med', 'hot med', 'hot/warm', 'warm sd%'))
for r in rows:
    print('%-26s %4d %4d %10.4f %10.4f %+7.2f%% %8.2f%%' % r)
d = [r[5] for r in rows]
print('median hot/warm change over %d configurations: %+.2f%%; range %+.2f%% .. %+.2f%%' % (len(d), st.median(d), min(d), max(d)))
mem = [r for r in rows if any(k in r[0] for k in ('dram', 'scp', 'wire', 'tload', 'tstore', 'st_stream'))]
print('memory configurations:', [(r[0], round(r[5], 2)) for r in mem])

J = {'heater': [{'card': c, 'bin': '%d-%d' % b, 'n': len(agg[(c, b)]),
                 'cycles_per_op_median': st.median(x[0] for x in agg[(c, b)]),
                 'cycles_per_op_min': min(x[0] for x in agg[(c, b)]), 'cycles_per_op_max': max(x[0] for x in agg[(c, b)]),
                 'ghz_median': st.median(x[1] for x in agg[(c, b)])} for (c, b) in sorted(agg)],
     'catalogue': {'passes': dict(temps), 'n_configs': len(rows), 'median_pct': st.median(d), 'min_pct': min(d), 'max_pct': max(d),
                   'warm_sd_max_pct': max(r[6] for r in rows),
                   'rows': [{'cfg': r[0], 'n_warm': r[1], 'n_hot': r[2], 'warm': r[3], 'hot': r[4], 'change_pct': r[5], 'warm_sd_pct': r[6]} for r in rows]}}
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
