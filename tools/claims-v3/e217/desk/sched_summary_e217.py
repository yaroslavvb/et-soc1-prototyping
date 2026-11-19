"""E217 (reg-e217, Q228): a summary of 1119-mmsweep4's arm table and seven session schedules, read from a COPY of the model session's
src/ (E214's sched_summary_e214.py, itself E212's and E208's, with this sweep's names; its families, its plan tiles and the claims' way of counting arms).

    /usr/bin/python3 -I -B sched_summary_e217.py <src dir> [--full]

Reads only: arms.json and sched/*.json. Prints the arm table's counts; per session: runs by role and form, the distinct arm
labels (the claims count these: the arms, the anchor and the numbered null runs), the blocks in order, the planned minutes, rule
and cap, the planning line, the smoke, the arms whose data is a plan tile (the operand-pattern arms); with --full, every run in
order (i, block, role, form, arm, mask; two spaces after the run number and the block). The schedules' est_peak_w and est_s are
the proposal's planning estimates (make_schedule2.py's documented law over the lab's public measurements), not a forecast; this
summary prints only the highest planned peak and the planned minutes.
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
LAB_KINDS = ('rnd', 'zeros', 'ones')
print('arms.json: kit %s, seed %s, %d arms with the anchor, %d plan tiles, sessions %s' % (
    arms['kit'], arms['seed'], len(A), len(arms['tiles']), json.dumps(arms['sessions'], sort_keys=True)))
fam = collections.Counter(f for a in A.values() for f in a['families'])
print('  families (an arm is in one or more): ' + ', '.join('%s %d' % kv for kv in sorted(fam.items())))
print('  types: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['type'] for a in A.values()).items())))
print('  kinds: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['kind'] for a in A.values()).items())))
print('  masks: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['shires'] for a in A.values()).items())))
print('  forms: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['form'] for a in A.values()).items())))
print('  priorities: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['priority'] for a in A.values()).items())))
print('  M %d-%d, N %d-%d, K %d-%d; footprint %d-%d MB' % (
    min(a['M'] for a in A.values()), max(a['M'] for a in A.values()), min(a['N'] for a in A.values()),
    max(a['N'] for a in A.values()), min(a['K'] for a in A.values()), max(a['K'] for a in A.values()),
    min(a['footprint_mb'] for a in A.values()), max(a['footprint_mb'] for a in A.values())))
op = sorted(i for i, a in A.items() if a['kind'] not in LAB_KINDS)
print('  arms whose data is a plan tile (operand-pattern arms): %d' % len(op))
union = set()
tot_runs = tot_min = 0
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
    opx = sorted({r['arm'] for r in runs if r['role'] in ('arm', 'time') and A[r['arm']]['kind'] not in LAB_KINDS})
    print()
    print('%s: card %s session %s seed %s kit %s' % (fn, s['card'], s['session'], s['seed'], s['kit']))
    print('  runs %d (%s); forms %s; distinct arms %d with the anchor (not in arms.json: %d); distinct arm labels %d (arms, '
          'anchor, nulls); device processes planned %d (+3 smoke)' % (
              len(runs), ', '.join('%s %d' % kv for kv in sorted(roles.items())), dict(sorted(forms.items())), len(arms_here),
              len(missing), len(labels), devproc))
    print('  blocks in order: %s' % ' '.join(blocks))
    print('  process %s' % json.dumps(s['process'], sort_keys=True))
    print('  forms %s' % json.dumps(s['forms'], sort_keys=True))
    print('  timing %s; planned %.1f card-minutes; planning line %s W; cap_est_w %s' % (
        json.dumps(s['timing'], sort_keys=True), s['planned_min'], s['line_w'], s['cap_est_w']))
    print('  highest planned peak in the schedule %.1f W (smoke %s)' % (
        max(r['est_peak_w'] for r in runs), ', '.join('%s %s' % (x['arm'], x['shires']) for x in s['smoke'])))
    tr = [r['arm'] for r in runs if r['role'] == 'time']
    if tr:
        print('  role time (energy not read; run for its time and clock): %s' % ', '.join(tr))
    print('  operand-pattern arms (data a plan tile): %d%s' % (len(opx), (': ' + ', '.join(opx)) if opx else ''))
    if full:
        for r in runs:
            print('    %3d  %-6s  %-6s %-5s %-28s %s' % (r['i'], r['block'], r['role'], r['form'], r['arm'], r.get('shires', '-')))
print()
print('runs in all sessions: %d; planned card-minutes in all: %.1f' % (tot_runs, tot_min))
print('arms scheduled in at least one session: %d of %d; never scheduled: %s' % (
    len(union & set(A)), len(A), ', '.join(sorted(set(A) - union)) or 'none'))
