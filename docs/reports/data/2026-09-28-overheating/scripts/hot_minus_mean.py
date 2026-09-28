#!/usr/bin/env python3
"""How much hotter is the hottest of the 34 minion-shire sensors than their mean, and does it depend on where the work sits?

Data: the heat-placement blocks (E52: docs/reports/data/2026-09-28-heat-placement/raw/<card>/hp/p*/), whose sampler
resets the service processor's statistics every 1 s (ettelem --reset-ms 1000), so in each 1 s window
temp_c.minshire[2] is the highest reading of any one sensor in that window and minshire[0] the mean. Per window:
  dhot = max over the window of minshire[2] - max over the window of minshire[0]   (whole degrees, both truncated)
Windows are split by what ran: 'load' = inside a measured launch (kind chain or single) and at least 2 s after its start;
'idle' = no launch of any kind within 3 s. Placement = the run's name (tools/claims-v3/hp/placements.json).
Also: the DV2 night (E51, aifoundry2): one statistics reset at S+1, then the peak-hold runs over the whole T-run, so
max(minshire[2]) - max(minshire[0]) over the run = the hottest sensor's peak above the mean's peak.
Writes docs/reports/data/2026-09-28-overheating/analysis/hot_minus_mean.json.
Usage: python3 hot_minus_mean.py [docs/reports/data]
"""
import collections, glob, gzip, json, os, statistics as st, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'hot_minus_mean.json')
HP = os.path.join(ROOT, '2026-09-28-heat-placement/raw')


def jl(p):
    op = gzip.open if p.endswith('.gz') else open
    with op(p, 'rt') as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('{'):
                try:
                    yield json.loads(line)
                except ValueError:
                    pass


def windows(samples, reset_ms=1000):
    out, cur = [], []
    for s in samples:
        cur.append(s)
        sr = s.get('since_reset_ms')
        if sr is not None and sr >= reset_ms:
            out.append(cur)
            cur = []
    res = []
    for w in out:
        # the first sample after a reset can carry the SP's cleared statistics; use samples >= 150 ms into the window
        ws = [s for s in w if (s.get('since_reset_ms') or 0) >= 150 and (s.get('temp_c') or {}).get('minshire')]
        if len(ws) < 3:
            continue
        ms = [s['temp_c']['minshire'] for s in ws]
        io = [s['temp_c'].get('ioshire', [None])[0] for s in ws]
        res.append({'t0': ws[0]['t_ms'], 't1': ws[-1]['t_ms'], 'mean': max(m[0] for m in ms), 'high': max(m[2] for m in ms),
                    'low': min(m[1] for m in ms), 'io': max(x for x in io if x is not None),
                    'board': st.mean(s.get('board_w') or 0 for s in ws)})
    return res


by = collections.defaultdict(list)          # (card, placement, state) -> [dhot]
by_mean = collections.defaultdict(list)     # (card, state, mean bin) -> [dhot]
worst = []
for bd in sorted(glob.glob(os.path.join(HP, '*/hp/p*'))):
    card = bd.split('/raw/')[1].split('/')[0]
    if not os.path.exists(os.path.join(bd, 'runs.jsonl')) or 'guard-stop' in bd:
        continue
    if not os.path.exists(os.path.join(bd, 'launches.jsonl')):
        continue          # early scouting blocks (R1b p1601-p1603) logged no launch times: load and idle cannot be told apart
    runs = list(jl(os.path.join(bd, 'runs.jsonl')))
    L = list(jl(os.path.join(bd, 'launches.jsonl'))) if os.path.exists(os.path.join(bd, 'launches.jsonl')) else []
    for r in runs:
        tf = os.path.join(bd, 'tel-%s.jsonl.gz' % r['idx'])
        if not os.path.exists(tf):
            continue
        tel = sorted(jl(tf), key=lambda s: s.get('t_ms', 0))
        mine = [x for x in L if str(x.get('run')) == str(r['idx'])]
        meas = [(x['t_start_ms'], x['t_end_ms']) for x in mine if x.get('kind') in ('chain', 'single')]
        anyl = [(x['t_start_ms'], x['t_end_ms']) for x in mine]
        for w in windows(tel):
            if any(a + 2000 <= w['t0'] and w['t1'] <= b for a, b in meas):
                state = 'load'
            elif not any(a - 3000 <= w['t1'] and w['t0'] <= b + 3000 for a, b in anyl):
                state = 'idle'
            else:
                continue
            d = w['high'] - w['mean']
            by[(card, r['name'], state)].append(d)
            mb = '%d-%d' % (w['mean'] // 5 * 5, w['mean'] // 5 * 5 + 5)
            by_mean[(card, state, mb)].append(d)
            worst.append((d, card, r['name'], state, w['mean'], w['high'], w['io'], round(w['board'], 1), bd.split('/')[-1]))


def summ(v):
    c = collections.Counter(v)
    return 'n %5d  median %+d  mean %+.2f  max %+d  dist %s' % (len(v), st.median(v), st.mean(v), max(v),
                                                             dict(sorted(c.items())))


print('E52 heat placement: hottest sensor minus mean, per 1 s window (whole degrees)')
for k in sorted(by):
    if len(by[k]) >= 5:
        print('  %-14s %-10s %-5s %s' % (k[0], k[1], k[2], summ(by[k])))
print()
print('by card, state and mean temperature:')
for k in sorted(by_mean):
    if len(by_mean[k]) >= 5:
        print('  %-14s %-5s %-6s %s' % (k[0], k[1], k[2], summ(by_mean[k])))
print()
print('largest dhot windows:')
for x in sorted(worst, reverse=True)[:12]:
    print('  dhot %+d  %s %s %s mean %d high %d io %d board %.1f W  %s' % x)

# placement meta: how many shires each placement loads, from placements.json
pl = json.load(open(os.path.join(os.path.dirname(ROOT.rstrip('/')), '..', 'tools/claims-v3/hp/placements.json'))) \
    if os.path.exists(os.path.join(os.path.dirname(ROOT.rstrip('/')), '..', 'tools/claims-v3/hp/placements.json')) else None

print()
print('E51 DV2 (aifoundry2): peak-hold since the one reset at S+1, over each T-run')
dv = os.path.join(ROOT, '2026-09-28-dvfs2-aifoundry2/raw')
rows = []
for rf in sorted(glob.glob(os.path.join(dv, '**/runs.jsonl'), recursive=True)):
    d = os.path.dirname(rf)
    for r in jl(rf):
        tf = os.path.join(d, 'tel-%s.jsonl.gz' % r.get('idx'))
        if not os.path.exists(tf) or not r.get('placement', r.get('name')):
            continue
        tel = [s for s in jl(tf) if (s.get('temp_c') or {}).get('minshire')]
        # samples after the reset (since_reset_ms small and growing) through the run
        post = []
        started = False
        for s in sorted(tel, key=lambda s: s['t_ms']):
            sr = s.get('since_reset_ms')
            if sr is not None and 0 <= sr < 400:
                started = True
                post = []
            if started:
                post.append(s)
        post = [s for s in post if (s.get('since_reset_ms') or 0) >= 150]
        if len(post) < 5:
            continue
        mmean = max(s['temp_c']['minshire'][0] for s in post)
        mhigh = max(s['temp_c']['minshire'][2] for s in post)
        rows.append((r.get('placement', r.get('name')), mmean, mhigh, mhigh - mmean, os.path.relpath(d, dv)))
for x in rows:
    print('  %-10s mean-peak %d  hottest-peak %d  dhot %+d  %s' % x)
if rows:
    c = collections.defaultdict(list)
    for x in rows:
        c[x[0]].append(x[3])
    print('  by placement:', {k: (len(v), st.median(v), max(v)) for k, v in c.items()})


def sj(v):
    c = collections.Counter(v)
    return {'n': len(v), 'median': st.median(v), 'mean': round(st.mean(v), 3), 'max': max(v), 'dist': {str(k): c[k] for k in sorted(c)}}


J = {'e52_by_placement': [{'card': k[0], 'placement': k[1], 'state': k[2], **sj(v)} for k, v in sorted(by.items()) if len(v) >= 5],
     'e52_by_mean': [{'card': k[0], 'state': k[1], 'bin': k[2], **sj(v)} for k, v in sorted(by_mean.items()) if len(v) >= 5],
     'e52_largest': [dict(zip(('dhot', 'card', 'placement', 'state', 'mean', 'high', 'io', 'board_w', 'block'), x))
                     for x in sorted(worst, reverse=True)[:12]],
     'e51_runs': [dict(zip(('placement', 'mean_peak', 'hottest_peak', 'dhot', 'dir'), x)) for x in rows]}
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
