#!/usr/bin/env python3
"""E200 registration desk check (reg-e200, Q192): the governor's climb on aifoundry2 card 0, re-read by this lane from E190 arm A's
committed records (Fri 13 Nov 2026), in the forms THE CLOCK RULE and C2 use (E200.md sections 3 and 4). A desk reading of another
experiment's measured records; nothing here is an E200 datum. Standard library only.

    python3 -I -B tools/claims-v3/e200/desk/climb_e200.py [TOP] > tools/claims-v3/e200/desk/climb-e200.txt

Reads docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2/: telemetry.jsonl.gz (the sampler's t_ms and mhz.minion),
runs/*/run.json (each process's launch window: its first launch's start and its last launch's end) and runs/*/proc-*.out (each
launch's SPARSITY line: t_start_ms, t_end_ms and the launch's own clock count, ghz). For every process, with lo its first launch's
start and hi its last launch's end:
  A the climb as E194's registration read it: the first 800 MHz sample after lo (E194's desk/climb-e190.txt);
  B the last sample off 800 MHz before that first 800 MHz sample (the climb's tail, 700 MHz samples included);
  C THE CLOCK RULE's sample clause: any sample off 800 MHz in [lo + 1.5 s, hi] (such a process would be set aside);
  D the first launch at 790 MHz or more by its own count (ghz >= 0.79): its start after lo (a launch-based climb);
  E the gap between a process's launch window and the previous one's in a run of back-to-back processes.
"""
import gzip
import hashlib
import json
import os
import statistics
import sys

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
D = os.path.join(TOP, 'docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2')


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    i = int(k)
    return xs[i] if i + 1 >= len(xs) else xs[i] + (xs[i + 1] - xs[i]) * (k - i)


print('E200 desk check: the governor\'s climb on aifoundry2 card 0, re-read from E190 arm A\'s committed records (a desk read of '
      'measured records; nothing here is an E200 datum)')
print('interpreter: %s %s' % (sys.executable, sys.version.split()[0]))
tp = os.path.join(D, 'telemetry.jsonl.gz')
print('  %s  %s' % (hashlib.sha256(open(tp, 'rb').read()).hexdigest(), os.path.relpath(tp, TOP)))
tel = []
with gzip.open(tp, 'rt') as f:
    for ln in f:
        try:
            s = json.loads(ln)
        except ValueError:
            continue
        if isinstance(s, dict) and 't_ms' in s:
            tel.append((s['t_ms'], (s.get('mhz') or {}).get('minion')))
tel.sort(key=lambda x: x[0])
print('  telemetry samples: %d' % len(tel))
rows = []
for run in sorted(os.listdir(os.path.join(D, 'runs'))):
    rj = os.path.join(D, 'runs', run, 'run.json')
    r = json.load(open(rj))
    prev_end = None
    for p in r.get('procs', []):
        lw = p.get('launch_window_ms')
        if not lw:
            continue
        lo, hi = lw
        inside = [x for x in tel if lo <= x[0] <= hi]
        f800 = next((t for t, f in inside if f == 800), None)
        tail = max((t for t, f in inside if f is not None and f != 800 and (f800 is None or t < f800)), default=None)
        late = [(t, f) for t, f in inside if t >= lo + 1500 and f is not None and abs(f - 800) > 1]
        launches = []
        po = os.path.join(D, 'runs', run, p['name'] + '.out')
        for ln in open(po):
            if ln.startswith('SPARSITY '):
                try:
                    j = json.loads(ln[len('SPARSITY '):])
                except ValueError:
                    continue
                if j.get('test') != 'check' and j.get('ghz'):
                    launches.append(j)
        launches.sort(key=lambda j: j['t_start_ms'])
        first_fast = next((j['t_start_ms'] for j in launches if j['ghz'] >= 0.79), None)
        rows.append({'run': run, 'proc': p['name'], 'kind': r.get('kind'),
                     'A': None if f800 is None else (f800 - lo) / 1000.0,
                     'B': None if tail is None else (tail - lo) / 1000.0,
                     'C': len(late), 'C_values': sorted({f for _, f in late}),
                     'C_first': (late[0][0] - lo) / 1000.0 if late else None,
                     'D': None if first_fast is None else (first_fast - lo) / 1000.0,
                     'E': None if prev_end is None else (lo - prev_end) / 1000.0, 'launches': len(launches)})
        prev_end = hi


def summ(name, xs):
    xs = [x for x in xs if x is not None]
    print('  %s: n %d; min %.3f, median %.3f, mean %.3f, p95 %.3f, max %.3f s' % (
        name, len(xs), min(xs), statistics.median(xs), statistics.mean(xs), q(xs, 0.95), max(xs)))


print()
print('per process (run, proc: A first 800 MHz sample after lo, B the climb\'s last sample off 800 MHz, C samples off 800 MHz from '
      'lo + 1.5 s to hi, D first launch at >= 790 MHz by its own count, E the gap after the previous process\'s launches; seconds):')
for x in rows:
    print('  %-20s %-7s A %6s  B %6s  C %2d %-11s D %6s  E %6s' % (
        x['run'], x['proc'], '-' if x['A'] is None else '%.3f' % x['A'], '-' if x['B'] is None else '%.3f' % x['B'], x['C'],
        x['C_values'] or '', '-' if x['D'] is None else '%.3f' % x['D'], '-' if x['E'] is None else '%.3f' % x['E']))
print()
summ('A, the first 800 MHz sample (E194\'s climb)', [x['A'] for x in rows])
summ('B, the climb\'s last off-800 sample', [x['B'] for x in rows])
summ('D, the first launch at >= 790 MHz by its own count', [x['D'] for x in rows])
summ('E, the gap between back-to-back processes\' launch windows', [x['E'] for x in rows])
started = sum(1 for x in rows if x['B'] is not None)
print('  processes whose launch window began off 800 MHz (a sample at 600 or 700 MHz before the first 800 MHz sample): %d of %d' % (
    started, len(rows)))
setaside = [x for x in rows if x['C']]
print('  C, processes with a sample off 800 MHz from lo + 1.5 s to hi (THE CLOCK RULE would set them aside): %d of %d (bursts %d of %d, '
      'sustained %d of %d)' % (len(setaside), len(rows), sum(1 for x in setaside if x['kind'] == 'burst'),
                               sum(1 for x in rows if x['kind'] == 'burst'), sum(1 for x in setaside if x['kind'] != 'burst'),
                               sum(1 for x in rows if x['kind'] != 'burst')))
for x in setaside:
    print('    %s %s: %d samples, values %s, the first at %.3f s after lo' % (x['run'], x['proc'], x['C'], x['C_values'], x['C_first']))
print()
print('CLIMB-E200 DONE')
