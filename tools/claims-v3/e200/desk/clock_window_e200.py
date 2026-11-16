#!/usr/bin/env python3
"""E200 registration desk check (reg-e200, Q192): why E200's window is 320,000,000 cycles, and THE CLOCK RULE's numbers, from
committed code and records only (desk check of code and desk arithmetic; nothing measured here).

    python3 -I -B tools/claims-v3/e200/desk/clock_window_e200.py [TOP] > tools/claims-v3/e200/desk/clock-window-e200.txt

TOP: the top of a tree holding E197's registration and E192's, E194's and E190's committed files (default: the current folder).
Reads, each pinned by sha256 below and refused if different: E197's reducer (its reading() and LAG_MS, run as registered on
synthetic sample grids), E197's host source (the launch budget), E197's lab runner (its window and process bounds), E197.md
(its card-time sentence), E192's committed launch records and host stderr on aifoundry3 (a launch's own count and the device's
opening time for this host family), E194's committed read of E190 arm A's climbs on aifoundry2 (desk/climb-e190.txt).
Standard library only.
"""
import hashlib
import importlib.util
import json
import os
import re
import statistics
import sys

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
P = {
    'reducer': ('tools/claims-v3/e197/proposal/src/reduce_regfile.py', 'f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87'),
    'host': ('tools/claims-v3/e197/proposal/src/host/main.cpp', None),
    'runner': ('tools/claims-v3/e197/lab/run_trains.py', '91c46f4e8a28a2505af1f9e0bb029d1935da59e26915a80bfadd19abd638c40d'),
    'e192runs': ('docs/reports/data/2026-11-14-e192-intbits-aifoundry3/run/runs.jsonl', None),
    'e192stderr': ('docs/reports/data/2026-11-14-e192-intbits-aifoundry3/run/stderr.txt', None),
    'climbs': ('tools/claims-v3/e194/desk/climb-e190.txt', None),
}


def path(k):
    return os.path.join(TOP, P[k][0])


def sha(k):
    return hashlib.sha256(open(path(k), 'rb').read()).hexdigest()


print('E200 desk check: the window and THE CLOCK RULE, from committed code and records (desk check of code; desk arithmetic)')
print('interpreter: %s %s' % (sys.executable, sys.version.split()[0]))
for k, (p, want) in P.items():
    got = sha(k)
    if want and got != want:
        sys.exit('REFUSED: %s is %s, not %s' % (p, got, want))
    print('  %s  %s%s' % (got, p, '' if not want else '  (pinned)'))

# ------------------------------------------------------------------ 1. the reading at 0.30 s and 0.40 s launches
spec = importlib.util.spec_from_file_location('reduce_e200_w', os.path.join(TOP, 'tools/claims-v3/e200/reduce_e200.py'))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
R, _ = M.load_e197(path('reducer'))
print()
print('1. E197\'s launch reading (its reading(), LAG_MS %d ms: the board samples in [start + %d ms, end], at least 2) on a 10 Hz '
      'sample grid, every phase of the grid against the launch start (0-99 ms, 1 ms steps)' % (R.LAG_MS, R.LAG_MS))
rows = {}
for label, dur_ms in (('240,000,000 cycles at 600 MHz (E197 on aifoundry3)', 400.3), ('240,000,000 cycles at 800 MHz (E197\'s window on aifoundry2)', 300.3),
                      ('320,000,000 cycles at 800 MHz (E200\'s window W1)', 400.3), ('320,000,000 cycles at 600 MHz (inside a climb)', 533.6)):
    ok = 0
    for ph in range(100):
        S = {'ts': [float(t) for t in range(ph - 1000, 3000, 100)], 'ws': None}
        S['ws'] = [1.0] * len(S['ts'])
        t0 = 1000.0
        r = R.reading(S, t0, t0 + dur_ms)
        ok += 1 if r is not None else 0
    p = ok / 100.0
    q = p ** 4
    proc = 1 - (1 - q) ** 3
    unit = proc ** 2
    rows[label] = p
    print('  %-62s %5.1f ms: a reading in %3d of 100 phases; a quad complete %.4f; a process with a value %.4f; a unit %.5f; '
          'T1\'s expected units of 67 pairs %.2f' % (label, dur_ms, ok, q, proc, unit, 67 * unit))
print('  The launch spans: E192\'s committed launches (240,000,000 cycles at 600 MHz on aifoundry3) read wall_s 0.4003 s: the same '
      'cycles take 0.3003 s at 800 MHz, 320,000,000 take 0.4003 s.')

# ------------------------------------------------------------------ 2. the host's launch budget and the timeout
src = open(path('host')).read()
fits = 'secondsSince(tOpen_) + double(o_.window) / 0.5e9 + 1.0 <= o_.budget'
assert fits in src, 'launchFits() not as read'
m = re.search(r'double seconds = 4\.0, budget = ([0-9.]+);', src)
budget = float(m.group(1))
mw = re.search(r'window = (\d+);', src)
win_default = int(mw.group(1))
lim = re.search(r'o\.window > (\d+)ull', src)
dev = [float(x) for x in re.findall(r'device ready in ([0-9.]+) s', open(path('e192stderr')).read())]
print()
print('2. The host\'s launch budget (E197\'s host/main.cpp launchFits(): "%s"; --budget %.1f s by default, at most 9; --window default %d, '
      'at most %s)' % (fits, budget, win_default, lim.group(1)))
print('   the device\'s opening on this host family (E192\'s committed stderr, %d processes): "device ready in" median %.2f s, max %.2f s' % (
    len(dev), statistics.median(dev), max(dev)))
for label, win, f_before, climb in (('E197 at 600 MHz (240M)', 240e6, 600e6, None), ('E197\'s window at 800 MHz (240M)', 240e6, 800e6, None),
                                    ('E200 at 800 MHz from the start (320M)', 320e6, 800e6, None),
                                    ('E200 with a climb of 1.5 s (320M)', 320e6, 600e6, 1.5),
                                    ('E200 at 600 MHz throughout (320M)', 320e6, 600e6, 99.0)):
    for d in (statistics.median(dev), max(dev)):
        t = d
        starts = []
        c_abs = d + climb if climb is not None else None
        for n in range(13):
            starts.append(t)
            if c_abs is None or c_abs <= t:
                t += win / (800e6 if (c_abs is not None or f_before == 800e6) else 600e6) if c_abs is not None else win / f_before
            elif c_abs >= t + win / 600e6:
                t += win / 600e6
            else:
                done = 600e6 * (c_abs - t)
                t = c_abs + (win - done) / 800e6
        need = starts[12] + win / 0.5e9 + 1.0
        print('   %-40s device ready %.2f s: launch 12 starts at %.3f s; launchFits needs %.3f <= %.1f: %s (margin %+.3f s); the process '
              'ends near %.2f s, under timeout 10' % (label, d, starts[12], need, budget, 'fits' if need <= budget else 'REFUSED',
                                                     budget - need, t + 0.05))

# ------------------------------------------------------------------ 3. the runner's bounds
run = open(path('runner')).read()
n240 = run.count('"--window", "240000000"')
proc_s = float(re.search(r'^PROC_S = ([0-9.]+)', run, re.M).group(1))
proc_max = float(re.search(r'^PROC_MAX_S = ([0-9.]+)', run, re.M).group(1))
print()
print('3. E197\'s lab runner: "--window", "240000000" on %d lines (the anchors\' and the trains\' host calls; W1 changes both and '
      'nothing else); PROC_S %.1f s (a train process, for the deadline); PROC_MAX_S %.1f s (timeout 10 plus 1 s)' % (n240, proc_s, proc_max))

# ------------------------------------------------------------------ 4. the launch's own count (E192) and the climb (E190 arm A)
runs = [json.loads(ln) for ln in open(path('e192runs')) if ln.strip()]
own = sorted(r['cycles_max'] / r['wall_s'] / 1e6 for r in runs if r.get('cycles_max') and r.get('wall_s'))
ratio = [x / 600.0 for x in own]
print()
print('4. A launch\'s own count, cycles_max / wall_s, on E192\'s %d committed launches (the same host family, 240,000,000 cycles at '
      '600 MHz on aifoundry3): min %.3f, median %.3f, max %.3f MHz, i.e. %.5f-%.5f of the clock; at 800 MHz that is %.1f-%.1f MHz, '
      'inside THE CLOCK RULE\'s 780-810 MHz; a launch at 700 MHz would read about %.0f MHz and one at 600 MHz about %.0f, outside' % (
          len(own), own[0], statistics.median(own), own[-1], ratio[0], ratio[-1], 800 * ratio[0], 800 * ratio[-1],
          700 * statistics.median(ratio), 600 * statistics.median(ratio)))
climbs = []
for ln in open(path('climbs')):
    mm = re.match(r'\s*(\S+)\s+proc-(\d+)\s+([0-9.]+)\s+(\d+)\s', ln)
    if mm:
        climbs.append((mm.group(1), int(mm.group(2)), float(mm.group(3)), int(mm.group(4))))
cs = sorted(c[2] for c in climbs)
print('   E190 arm A on aifoundry2 (E194\'s committed read of its telemetry): %d processes; the climb from the launch window\'s start to '
      'the first 800 MHz sample: min %.3f, median %.3f, mean %.3f, max %.3f s; above 1.0 s %d, above 1.5 s %d' % (
          len(cs), cs[0], statistics.median(cs), statistics.mean(cs), cs[-1], sum(1 for c in cs if c > 1.0), sum(1 for c in cs if c > 1.5)))
sus = [c for c in climbs if '-sus-' in c[0]]
bur = [c for c in climbs if '-burst-' in c[0]]
print('   samples off 800 MHz after the climb: bursts %d of %d processes; sustained runs (twelve 6 s processes back to back) %d of %d '
      '(E194\'s read: 8 of them at a shire mean of 66 C, the governor\'s thermal test)' % (
          sum(1 for c in bur if c[3]), len(bur), sum(1 for c in sus if c[3]), len(sus)))
ext = [0.25 * c for c in cs]
print('   the climb\'s cost in a train process under W1 (the cycles run at 600 MHz before it take 4/3 as long): 0.25 x c: mean %.3f s, '
      'max %.3f s a process' % (statistics.mean(ext), max(ext)))


def launch_starts(c, win=320e6):
    t, s = 0.0, []
    for n in range(13):
        s.append(t)
        if c <= t:
            t += win / 800e6
        elif c >= t + win / 600e6:
            t += win / 600e6
        else:
            t = c + (win - 600e6 * (c - t)) / 800e6
    return s, t


for c in (0.0, statistics.median(cs), cs[-1], 1.5):
    s, end = launch_starts(c)
    print('   a climb at %.3f s: launches 0-4 start at %s s, launch 5 at %.3f s, the last ends at %.3f s; nothing is read before 2.0 s, '
          'so quads 2 and 3 (launches 5-12) are read and quad 1 never' % (c, ', '.join('%.3f' % x for x in s[:5]), s[5], end))
assert all(launch_starts(c)[0][4] < 2.0 <= launch_starts(c)[0][5] for c in [i / 1000.0 for i in range(0, 1501)])
print('   checked for every climb from 0 to 1.500 s in 1 ms steps: launch 4 starts before 2.0 s and launch 5 at or after it')
clean = sum(1 for c in cs if c <= 0.4 + 0.25 * c)
print('   (E190\'s climbs short enough that quad 1 would hold no 600 MHz sample, about c <= 0.533 s: %d of %d; E200 does not read quad 1 '
      'in any process, so the board meter\'s pass after the step never reaches a read launch)' % (clean, len(cs)))

# ------------------------------------------------------------------ 5. card time and the cap (E197's arithmetic, with the climb)
e197 = open(os.path.join(TOP, 'tools/claims-v3/e197/E197.md')).read()
sent = '400 processes x 5.7 s + 24 bursts x 8.2 s +\n  80 s of block idles + 90 s of gaps + about 35 s of smoke + the session\'s 18 s of sampler margins is 2,700 s'
assert sent in e197, 'E197.md 10\'s sentence not as read'
mean_x, max_x = statistics.mean(ext), max(ext)
print()
print('5. Card time (E197.md 10: "400 processes x 5.7 s + 24 bursts x 8.2 s + 80 s of block idles + 90 s of gaps + about 35 s of smoke '
      '+ the session\'s 18 s of sampler margins is 2,700 s"), with W1 the launches last as E197\'s; the climb adds its cost to each '
      'device process (the anchors\' bursts are bounded in time and change little)')
for label, n_proc, base_s, cap in (('sitting 1, full plan', 400, 2700.0, 3000), ('sitting 1, short plan', 302, 35.7 * 60, 2400),
                                   ('sitting 2 (ext)', 266, 27.3 * 60, 2100)):
    print('   %-22s E197 %.1f min; E200 at the mean climb %.1f min, at the longest %.1f min; cap %d min' % (
        label, base_s / 60, (base_s + n_proc * mean_x) / 60, (base_s + n_proc * max_x) / 60, cap // 60))
# T15, the full plan's last train: does it start? (the runner: no train starts unless processes x 6.2 s + 30 s fit before its
# deadline; E197's kit puts the deadline at the first card command + the cap - 120 s, and step 9 about 90 s after step 7)
dl = 3000 - 120 - 90
t15 = 2700.0 - 18 * 5.7 - 3 * 8.2 - 10 - 8
for label, x in (('E197 (5.7 s a process)', 0.0), ('E200 at the mean climb', mean_x), ('E200 at the longest climb', max_x)):
    st = t15 + 382 * x
    need = st + 18 * proc_s + 30
    print('   T15 (block D\'s last train, 18 processes), %s: starts about %.0f s after the sampler; the runner needs %.0f s <= its '
          'deadline about %d s (the cap - 120 s - 90 s from step 7): %s (%+.0f s)' % (label, st, need, dl, 'starts' if need <= dl else
                                                                                    'NOT STARTED', dl - need))
print()
print('CLOCK-WINDOW DONE')
