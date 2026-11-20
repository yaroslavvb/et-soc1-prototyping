"""E221 (reg-e221, Q235): a summary of 1120-mmsweep6's arm table and nine session schedules, read from a COPY of the model session's
src/ (E219's sched_summary_e219.py, itself E217's, E214's, E212's and E208's, with this sweep's names; this sweep's arms are gemmL
arms only, on the lab's kinds, and it has no plan tiles; the block-arm lines print only if such arms exist).

    /usr/bin/python3 -I -B sched_summary_e221.py <src dir> [--full]

Reads only: arms.json and sched/*.json. Prints the arm table's counts (by host family, type, kind, mask, form, priority, tag; the
gemmL arms' M, N, K); per session: runs by role and form, the distinct arm labels (the claims count these: the arms, the anchor and
the numbered null runs), the blocks in order, the planned minutes, rule and cap, the planning line, the smoke; with --full, every
run in order (i, block, role, form, arm, mask, the planning estimate; two spaces after the run number and the block). The
schedules' est_peak_w and est_s are the proposal's planning estimates (make_schedule2.py's documented laws over the lab's public
measurements), not a forecast.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import os
import sys

src = sys.argv[1]
full = '--full' in sys.argv
arms = json.load(open(os.path.join(src, 'arms.json')))
A = {a['id']: a for a in arms['arms']}


def fam_of(a):
    return a.get('family', 'gemmL')


print('arms.json: kit %s, seed %s, %d arms with the anchor, %d plan tiles, sessions %s' % (
    arms['kit'], arms['seed'], len(A), len(arms['tiles']), json.dumps(arms['sessions'], sort_keys=True)))
print('  host families: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(fam_of(a) for a in A.values()).items())))
fam = collections.Counter(f for a in A.values() for f in a['families'])
print('  tags (an arm carries one or more): ' + ', '.join('%s %d' % kv for kv in sorted(fam.items())))
for k in ('type', 'kind', 'shires', 'form', 'priority'):
    print('  %s: ' % k + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a[k] for a in A.values()).items())))
for f in ('gemmL', 'gemmc', 'gemmh', 'gemm', 'mm', 'tenb'):
    xs = [a for a in A.values() if fam_of(a) == f]
    if not xs:
        continue
    by = collections.Counter((a['type'], a['kind']) for a in xs)
    line = '  %-5s %3d arms; type/kind %s' % (f, len(xs), ', '.join('%s/%s %d' % (t, k, n) for (t, k), n in sorted(by.items())))
    if f == 'gemmL':
        line += '; M %d-%d, N %d-%d, K %d-%d; footprint %g-%g MB; masks %s' % (
            min(a['M'] for a in xs), max(a['M'] for a in xs), min(a['N'] for a in xs), max(a['N'] for a in xs),
            min(a['K'] for a in xs), max(a['K'] for a in xs), min(a['footprint_mb'] for a in xs),
            max(a['footprint_mb'] for a in xs), ', '.join('%s %d' % kv for kv in sorted(collections.Counter(
                a['shires'] for a in xs).items())))
    elif f in ('gemmc', 'gemmh', 'gemm'):
        line += '; blocks %s; repeats %s; shared C %d; ops a minion a pass %d-%d; footprint %g-%g MB' % (
            ','.join(str(b) for b in sorted({a['nblocks'] for a in xs})), ','.join(str(r) for r in sorted({a['repeats'] for a in xs})),
            sum(1 for a in xs if a.get('c_shared')), min(a['ops_per_minion_pass'] for a in xs),
            max(a['ops_per_minion_pass'] for a in xs), min(a['footprint_mb'] for a in xs), max(a['footprint_mb'] for a in xs))
    elif f == 'mm':
        line += '; pools %s pairs; ops a minion a pass %d-%d' % (','.join(str(n) for n in sorted({a['ntiles'] for a in xs})),
                                                                 min(a['ops_per_minion_pass'] for a in xs),
                                                                 max(a['ops_per_minion_pass'] for a in xs))
    print(line)
    print('        tokens: ' + ' '.join(sorted({a.get('arm') or a['values'].split(':')[0] for a in xs},
                                               key=lambda s: (len(s), s))))
union = set()
tot_runs = tot_min = tot_proc = 0
for fn in sorted(os.listdir(os.path.join(src, 'sched'))):
    s = json.load(open(os.path.join(src, 'sched', fn)))
    runs = s['runs']
    roles = collections.Counter(r['role'] for r in runs)
    forms = collections.Counter(r['form'] for r in runs)
    arms_here = sorted({r['arm'] for r in runs if r['role'] != 'null'})
    labels = {r['arm'] for r in runs}
    union |= set(arms_here)
    missing = [x for x in arms_here if x not in A]
    blocks = []
    for r in runs:
        if r['block'] not in blocks:
            blocks.append(r['block'])
    devproc = sum(s['forms'][r['form']]['nproc'] for r in runs)
    tot_runs += len(runs)
    tot_min += s['planned_min']
    tot_proc += devproc
    fams = collections.Counter(fam_of(A[r['arm']]) for r in runs if r['role'] in ('arm', 'time'))
    print()
    print('%s: card %s session %s seed %s kit %s' % (fn, s['card'], s['session'], s['seed'], s['kit']))
    print('  runs %d (%s); forms %s; distinct arms %d with the anchor (not in arms.json: %d); distinct arm labels %d (arms, '
          'anchor, nulls); device processes planned %d (+3 smoke)' % (
              len(runs), ', '.join('%s %d' % kv for kv in sorted(roles.items())), dict(sorted(forms.items())), len(arms_here),
              len(missing), len(labels), devproc))
    print('  arm runs by host family: ' + ', '.join('%s %d' % kv for kv in sorted(fams.items())))
    print('  blocks in order: %s' % ' '.join(blocks))
    print('  process %s' % json.dumps(s['process'], sort_keys=True))
    print('  forms %s' % json.dumps(s['forms'], sort_keys=True))
    print('  timing %s; planned %.1f card-minutes; planning line %s W; cap_est_w %s' % (
        json.dumps(s['timing'], sort_keys=True), s['planned_min'], s['line_w'], s['cap_est_w']))
    print('  highest planned peak in the schedule %.1f W (smoke %s)' % (
        max(r['est_peak_w'] for r in runs), ', '.join('%s %s %.1f W' % (x['arm'], x['shires'], x['est_peak_w']) for x in s['smoke'])))
    tr = [r['arm'] for r in runs if r['role'] == 'time']
    if tr:
        print('  role time (energy not read; run for its time and clock): %s' % ', '.join(tr))
    if full:
        for r in runs:
            print('    %3d  %-6s  %-6s %-5s %-28s %-10s %5.1f W' % (r['i'], r['block'], r['role'], r['form'], r['arm'],
                                                                  r.get('shires', '-'), r['est_peak_w']))
print()
print('runs in all sessions: %d; device processes planned in all: %d (+3 smoke a session); planned card-minutes in all: %.1f' % (
    tot_runs, tot_proc, tot_min))
print('arms scheduled in at least one session: %d of %d; never scheduled: %s' % (
    len(union & set(A)), len(A), ', '.join(sorted(set(A) - union)) or 'none'))
