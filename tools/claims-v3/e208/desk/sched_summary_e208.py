"""E208 (reg-e208, Q200): a summary of 1116-mmsweep's arm table and six session schedules, read from a COPY of the model session's src/.

    /usr/bin/python3 -I -B sched_summary_e208.py <src dir> [--full]

Reads only: arms.json and sched/*.json. Prints per session: runs by role and form, the distinct arms, the blocks in order, the
planned minutes, rule and cap, the planning line, the smoke; with --full, every run in order (i, block, role, form, arm, mask; two spaces after the run number and the block).
The schedules' est_peak_w and est_s are the proposal's planning estimates (make_schedule.py's documented law over the lab's
public measurements), not a forecast; this summary prints only the highest planned peak and the planned minutes.
"""
import collections
import json
import os
import sys

src = sys.argv[1]
full = '--full' in sys.argv
arms = json.load(open(os.path.join(src, 'arms.json')))
A = {a['id']: a for a in arms['arms']}
print('arms.json: kit %s, %d arms' % (arms['kit'], len(A)))
fam = collections.Counter(f for a in A.values() for f in a['families'])
print('  families (an arm may be in two): ' + ', '.join('%s %d' % (k, fam[k]) for k in ('K', 'N', 'M', 'SQ', 'D', 'S')))
print('  types: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['type'] for a in A.values()).items())))
print('  kinds: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['kind'] for a in A.values()).items())))
print('  masks: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a['shires'] for a in A.values()).items())))
print('  M %d-%d, N %d-%d, K %d-%d' % (min(a['M'] for a in A.values()), max(a['M'] for a in A.values()),
                                     min(a['N'] for a in A.values()), max(a['N'] for a in A.values()),
                                     min(a['K'] for a in A.values()), max(a['K'] for a in A.values())))
print('  small (sus3 form): %d arms' % sum(1 for a in A.values() if a['small']))
union = set()
for fn in sorted(os.listdir(os.path.join(src, 'sched'))):
    s = json.load(open(os.path.join(src, 'sched', fn)))
    runs = s['runs']
    roles = collections.Counter(r['role'] for r in runs)
    forms = collections.Counter(r['form'] for r in runs)
    arms_here = sorted({r['arm'] for r in runs if r['role'] != 'null'})
    union |= set(arms_here)
    missing = [x for x in arms_here if x not in A]
    blocks = []
    for r in runs:
        if r['block'] not in blocks:
            blocks.append(r['block'])
    devproc = sum(s['forms'][r['form']]['nproc'] for r in runs)
    print()
    print('%s: card %s session %s seed %s kit %s' % (fn, s['card'], s['session'], s['seed'], s['kit']))
    print('  runs %d (%s); forms %s; distinct arms %d (not in arms.json: %d); device processes planned %d' % (
        len(runs), ', '.join('%s %d' % kv for kv in sorted(roles.items())), dict(sorted(forms.items())), len(arms_here),
        len(missing), devproc))
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
    if full:
        for r in runs:
            print('    %3d  %-4s  %-6s %-5s %-22s %s' % (r['i'], r['block'], r['role'], r['form'], r['arm'], r.get('shires', '-')))
print()
print('arms scheduled in at least one session: %d of %d; never scheduled: %s' % (
    len(union & set(A)), len(A), ', '.join(sorted(set(A) - union)) or 'none'))
