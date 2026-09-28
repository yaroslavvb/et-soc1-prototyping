#!/usr/bin/env python3
"""aifoundry2's kernel-log error events (DV2 incident/kernel-events.out) against the card's die mean and clock
in any committed telemetry within 30 s of the event.
Writes docs/reports/data/2026-09-28-overheating/analysis/events_vs_temp.json.
Usage: python3 events_vs_temp.py [docs/reports/data]"""
import bisect, datetime, gzip, json, os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'events_vs_temp.json')
tel = []
for d, _, fs in os.walk(ROOT):
    if 'aifoundry2' not in d:
        continue
    for f in fs:
        if not re.search(r'\.jsonl(\.gz)?$', f):
            continue
        op = gzip.open if f.endswith('.gz') else open
        try:
            for line in op(os.path.join(d, f), 'rt', errors='replace'):
                if '"temp_c"' in line and '"t_ms"' in line:
                    try:
                        s = json.loads(line[line.find('{'):])
                        tel.append((s['t_ms'], s['temp_c']['minshire'][0], (s.get('mhz') or {}).get('minion'), s.get('board_w')))
                    except (ValueError, KeyError, IndexError, TypeError):
                        pass
        except (OSError, EOFError):
            pass
tel.sort()
K = [x[0] for x in tel]
J = []
ev = os.path.join(ROOT, '2026-09-28-dvfs2-aifoundry2/incident/kernel-events.out')
for line in open(ev):
    m = re.match(r'(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+) PDT .*?\]\s+(.*)', line)
    if not m:
        continue
    t = datetime.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    ms = int(t.timestamp() * 1000)
    a, b = bisect.bisect_left(K, ms - 30000), bisect.bisect_right(K, ms + 30000)
    near = tel[a:b]
    if near:
        x = min(near, key=lambda s: abs(s[0] - ms))
        print('%s  %-70s  mean %s C, %s MHz, %s W (sample %+.1f s)' % (m.group(1)[:19], m.group(2)[:70], x[1], x[2], x[3], (x[0] - ms) / 1000))
        J.append({'time': m.group(1)[:19], 'event': m.group(2)[:120], 'mean_c': x[1], 'mhz': x[2], 'board_w': x[3], 'dt_s': round((x[0] - ms) / 1000, 1)})
    else:
        print('%s  %-70s  no telemetry within 30 s' % (m.group(1)[:19], m.group(2)[:70]))
        J.append({'time': m.group(1)[:19], 'event': m.group(2)[:120], 'mean_c': None})
json.dump(J, open(OUT, 'w'), indent=1)
