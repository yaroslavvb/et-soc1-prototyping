"""E217 (reg-e217, Q228) desk: aifoundry1's committed record of board power under rgm136 (and E213 arm B's), run by run, for the two
cards E217 uses (E217.md section 5; post hoc, it adds no rule): for every committed session folder on aifoundry1 card 1 and card 0 with
session/runs/*/run.json and session/telemetry.jsonl.gz (E208's, E212's and E214's sessions by name, E206 arm B and E213 arm B), each
device process's window [t0_ms, t1_ms] read against the telemetry's board_w samples: the highest sample, and the highest value held on
3 samples in a row (the stop rule's form), with the run's planned estimate where its schedule gave one. Reads committed lab files only
(Python's own modules); writes its standard output and, if a second argument is given, a JSON of every process row.
    /usr/bin/python3 -I -B card_record_e217.py <lab tree> [<out json>]
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import json
import os
import re
import sys

lab = sys.argv[1]
outp = sys.argv[2] if len(sys.argv) > 2 else None
ddir = os.path.join(lab, 'docs', 'reports', 'data')
SESS = []
for d in sorted(os.listdir(ddir)):
    m = re.match(r'\d{4}-\d\d-\d\d-(e208|e212|e214)-mmsweep\d?-(a1c[01])-(S\d+r?)$', d)
    if m:
        SESS.append((d, m.group(1).upper(), {'a1c1': 'card 1', 'a1c0': 'card 0'}[m.group(2)], m.group(3)))
for d, exp in (('2026-11-17-e206-matmul-sweep-aifoundry1-c1', 'E206'), ('2026-11-18-e213-blind-matmul-aifoundry1-c1', 'E213')):
    if os.path.isdir(os.path.join(ddir, d)):
        SESS.append((d, exp, 'card 1', 'arm B'))


def tele(p):
    out = []
    with gzip.open(p, 'rt') as fh:
        for ln in fh:
            try:
                x = json.loads(ln)
            except ValueError:
                continue
            if 'board_w' in x and 't_ms' in x:
                out.append((x['t_ms'], x['board_w']))
    out.sort()
    return out


def argval(argv, k):
    return argv[argv.index(k) + 1] if k in argv else None


rows, sess_max = [], []
for d, exp, card, sname in SESS:
    sd = os.path.join(ddir, d, 'session')
    tp = os.path.join(sd, 'telemetry.jsonl.gz')
    rd = os.path.join(sd, 'runs')
    if not (os.path.exists(tp) and os.path.isdir(rd)):
        print('skip (no telemetry or runs):', d)
        continue
    T = tele(tp)
    ts = [t[0] for t in T]
    bmax = max(t[1] for t in T) if T else None
    sess_max.append((exp, card, sname, d, bmax, len(T)))
    for rn in sorted(os.listdir(rd)):
        rj = os.path.join(rd, rn, 'run.json')
        if not os.path.exists(rj):
            continue
        R = json.load(open(rj))
        est = (R.get('sched') or {}).get('est_peak_w')
        for pr in R.get('procs', []):
            if pr.get('t0_ms') is None or pr.get('t1_ms') is None:
                continue
            i0, i1 = bisect.bisect_left(ts, pr['t0_ms']), bisect.bisect_right(ts, pr['t1_ms'])
            w = [T[i][1] for i in range(i0, i1)]
            if not w:
                continue
            s3 = max(min(w[i:i + 3]) for i in range(len(w) - 2)) if len(w) >= 3 else None
            argv = pr.get('argv') or []
            rows.append({'exp': exp, 'card': card, 'session': sname, 'run': rn, 'values': argval(argv, '--values'),
                         'type': argval(argv, '--type'), 'mask': argval(argv, '--shires'), 'est_peak_w': est,
                         'max_w': max(w), 'held3_w': s3, 'n': len(w), 'rc': pr.get('rc')})
print('# aifoundry1 committed rgm136 record: %d device processes in %d sessions' % (len(rows), len(sess_max)))
for exp, card, sname, d, bmax, n in sess_max:
    print('session %-5s %-6s %-6s board max %6.2f W over %d samples  (%s)' % (exp, card, sname, bmax, n, d))
for card in ('card 1', 'card 0'):
    rr = sorted([r for r in rows if r['card'] == card], key=lambda r: -(r['held3_w'] or 0))
    print('\n== %s: the 30 highest held-on-3-samples board powers (W), every committed process' % card)
    for r in rr[:30]:
        print('  %-5s %-6s %-26s %-6s %-11s held3 %6.2f max %6.2f est %s  %s' % (r['exp'], r['session'], r['run'][:26], r['type'],
                                                                             r['mask'], r['held3_w'] or -1, r['max_w'], r['est_peak_w'], r['values']))
    print('\n== %s: every gemmL1x1x1 fp32 or fp16 process on all 32 shires (the post\'s 1x1x1 cells, full chip)' % card)
    for r in sorted([r for r in rr if (r['values'] or '').startswith('gemmL1x1x1:') and r['type'] in ('fp32', 'fp16')
                     and r['mask'] == '0xffffffff'], key=lambda r: (r['type'], r['values'], r['exp'])):
        print('  %-5s %-6s %-26s %-5s held3 %6.2f max %6.2f est %s  %s' % (r['exp'], r['session'], r['run'][:26], r['type'],
                                                                      r['held3_w'] or -1, r['max_w'], r['est_peak_w'], r['values']))
    ests = [(r['max_w'] - r['est_peak_w'], r) for r in rr if r['est_peak_w']]
    if ests:
        ests.sort(key=lambda x: -x[0])
        print('\n== %s: measured max minus planned estimate, the 15 largest (W) over %d processes with an estimate' % (card, len(ests)))
        for dlt, r in ests[:15]:
            print('  %+6.2f  %-5s %-6s %-26s %-11s max %6.2f est %5.1f  %s' % (dlt, r['exp'], r['session'], r['run'][:26], r['mask'],
                                                                        r['max_w'], r['est_peak_w'], r['values']))
if outp:
    json.dump({'sessions': sess_max, 'rows': rows}, open(outp, 'w'), indent=0)
