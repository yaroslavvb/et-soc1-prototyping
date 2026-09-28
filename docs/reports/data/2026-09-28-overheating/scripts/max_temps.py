#!/usr/bin/env python3
"""Highest die readings ever recorded per card, over every telemetry JSON-lines file under docs/reports/data.
Card from the path: guard.jsonl* and *card0.json are aifoundry1 card 0; aifoundry1-c1 card 1; aifoundry2; aifoundry3.
Fields: temp_c.minshire = [mean of 34 sensors, min peak-hold, max peak-hold]; temp_c.ioshire [cur, lo, hi];
sp.minion_c = [cma, min, max] of the mean since the SP's last stats reset.
Writes docs/reports/data/2026-09-28-overheating/analysis/max_temps.json beside its printed text (run from the repository root).
Usage: python3 max_temps.py [docs/reports/data]"""
import gzip, json, os, re, sys, collections
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'max_temps.json')
def card_of(p):
    if p.endswith('guard.jsonl.gz') or 'card0' in os.path.basename(p): return 'aifoundry1-c0'
    for c in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
        if c in p: return c
    if 'a1c1' in p: return 'aifoundry1-c1'
    if 'aifoundry1' in p: return 'aifoundry1-?'
    return None
best = collections.defaultdict(lambda: {k: (-1, None) for k in ('mean', 'high', 'io_hi', 'io_cur', 'sp_max', 'board_w')})
nfiles = collections.Counter(); nsamp = collections.Counter()
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if not re.search(r'\.(jsonl|json)(\.gz)?$', f): continue
        p = os.path.join(d, f); c = card_of(p)
        if c is None: continue
        op = gzip.open if f.endswith('.gz') else open
        try:
            fh = op(p, 'rt')
            lines = fh if f.endswith('l') or f.endswith('l.gz') else [fh.read()]
            got = 0
            for line in lines:
                line = line.strip()
                if not line.startswith('{') or '"temp_c"' not in line: continue
                try: s = json.loads(line)
                except Exception: continue
                t = s.get('temp_c') or {}
                ms = t.get('minshire'); io = t.get('ioshire'); sp = (s.get('sp') or {}).get('minion_c')
                b = best[c]; got += 1
                def upd(k, v):
                    if v is not None and isinstance(v, (int, float)) and v < 200 and v > b[k][0]: b[k] = (v, p)
                L = lambda x: x if isinstance(x, list) else [x]
                ms, io, sp = (L(ms) if ms is not None else None), (L(io) if io is not None else None), (L(sp) if sp is not None else None)
                if ms: upd('mean', ms[0])
                if ms and len(ms) == 3: upd('high', ms[2])
                if io: upd('io_cur', io[0])
                if io and len(io) == 3: upd('io_hi', io[2])
                if sp and len(sp) == 3 and sp[2] != 65535: upd('sp_max', sp[2])
                upd('board_w', s.get('board_w'))
            if got: nfiles[c] += 1; nsamp[c] += got
        except (OSError, EOFError, UnicodeDecodeError):
            continue
for c in sorted(best):
    print(c, 'files', nfiles[c], 'samples', nsamp[c])
    for k, (v, p) in best[c].items():
        print('   %-8s %6s  %s' % (k, v, p))
J = {c: {'files': nfiles[c], 'samples': nsamp[c], **{k: {'value': v, 'file': p} for k, (v, p) in best[c].items()}}
     for c in sorted(best)}
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
