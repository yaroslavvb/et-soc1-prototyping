"""E219 (reg-e219, Q232) desk: aifoundry1's committed record of board power, run by run, for the two cards E219 uses (E219.md section 5;
post hoc, it adds no rule). E217's card_record_e217.py, widened:
  PART 1, the committed rgm136 sessions on aifoundry1 card 1 and card 0 (session/runs/*/run.json with session/telemetry.jsonl.gz):
    E208's, E212's, E214's and E217's sweep sessions by name, E206 arm B and E213 arm B, E215 arm B (committed Thu 19 Nov 2026) and
    E190 arm B (its folder holds runs/ and telemetry.jsonl.gz without a session/ level); each device process's window
    [t0_ms, t1_ms] read against the telemetry's board_w samples: the highest sample, and the highest value held on 3 samples in a
    row (the stop rule's form), with the run's planned estimate where its schedule gave one; the host's arm token from --values;
  PART 2, the stream and TenB loops on card 1 in the lab's September record (docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1):
    E37's mmbench bursts (mmb/p1-p4/e1/<workload>: the shared 16-pair stream loop, the loop rgm136's mm<N> runs, a different binary),
    their results.json power summary and the telemetry over each burst's launches; and E39's sparsity_host runs with B streamed
    through TenB and with B in the L1 (ablb/p1-p3: the mode rgm136's tenb arm runs), the telemetry over each run's launches; each
    with the die at its start (E37's MINSHIRE reading before; E39's strict-start temperature).
Reads committed lab files only (Python's own modules); writes its standard output and, if a second argument is given, a JSON of
every row.
    /usr/bin/python3 -I -B card_record_e219.py <lab tree> [<out json>]
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
    m = re.match(r'\d{4}-\d\d-\d\d-(e208|e212|e214|e217)-mmsweep\d?-(a1c[01])-(S\d+r?)$', d)
    if m:
        SESS.append((os.path.join(d, 'session'), m.group(1).upper(), {'a1c1': 'card 1', 'a1c0': 'card 0'}[m.group(2)], m.group(3)))
for d, exp in (('2026-11-17-e206-matmul-sweep-aifoundry1-c1', 'E206'), ('2026-11-18-e213-blind-matmul-aifoundry1-c1', 'E213'),
               ('2026-11-19-e215-blind-matmul-aifoundry1-c1', 'E215')):
    if os.path.isdir(os.path.join(ddir, d)):
        SESS.append((os.path.join(d, 'session'), exp, 'card 1', 'arm B'))
if os.path.isdir(os.path.join(ddir, '2026-11-13-e190-large-gemm', 'aifoundry1-c1')):
    SESS.append((os.path.join('2026-11-13-e190-large-gemm', 'aifoundry1-c1'), 'E190', 'card 1', 'arm B'))


def tele(p):
    out = []
    with gzip.open(p, 'rt') as fh:
        for ln in fh:
            try:
                x = json.loads(ln)
            except ValueError:
                continue
            if isinstance(x, dict) and x.get('board_w') is not None and x.get('t_ms') is not None:
                out.append((x['t_ms'], x['board_w']))
    out.sort()
    return out


def window(T, ts, t0, t1):
    i0, i1 = bisect.bisect_left(ts, t0), bisect.bisect_right(ts, t1)
    w = [T[i][1] for i in range(i0, i1)]
    if not w:
        return None, None, 0
    s3 = max(min(w[i:i + 3]) for i in range(len(w) - 2)) if len(w) >= 3 else None
    return max(w), s3, len(w)


def argval(argv, k):
    return argv[argv.index(k) + 1] if k in argv else None


rows, sess_max = [], []
for sd_rel, exp, card, sname in SESS:
    sd = os.path.join(ddir, sd_rel)
    tp = os.path.join(sd, 'telemetry.jsonl.gz')
    rd = os.path.join(sd, 'runs')
    if not (os.path.exists(tp) and os.path.isdir(rd)):
        print('skip (no telemetry or runs):', sd_rel)
        continue
    T = tele(tp)
    ts = [t[0] for t in T]
    bmax = max(t[1] for t in T) if T else None
    sess_max.append((exp, card, sname, sd_rel, bmax, len(T)))
    for rn in sorted(os.listdir(rd)):
        rj = os.path.join(rd, rn, 'run.json')
        if not os.path.exists(rj):
            continue
        R = json.load(open(rj))
        est = (R.get('sched') or {}).get('est_peak_w')
        for pr in R.get('procs', []):
            if pr.get('t0_ms') is None or pr.get('t1_ms') is None:
                continue
            mx, s3, n = window(T, ts, pr['t0_ms'], pr['t1_ms'])
            if mx is None:
                continue
            argv = pr.get('argv') or []
            v = argval(argv, '--values') or ''
            rows.append({'part': 1, 'exp': exp, 'card': card, 'session': sname, 'run': rn, 'values': v,
                         'token': v.split(':')[0], 'type': argval(argv, '--type'), 'mask': argval(argv, '--shires'),
                         'est_peak_w': est, 'max_w': mx, 'held3_w': s3, 'n': n, 'rc': pr.get('rc')})

# PART 2: the September record of the stream and TenB loops on card 1
loops = []
V3 = os.path.join(ddir, '2026-09-25-claims-v3', 'raw', 'aifoundry1-c1')
for p in sorted(os.listdir(os.path.join(V3, 'mmb'))) if os.path.isdir(os.path.join(V3, 'mmb')) else []:
    e1 = os.path.join(V3, 'mmb', p, 'e1')
    for wl in sorted(os.listdir(e1)) if os.path.isdir(e1) else []:
        d = os.path.join(e1, wl)
        try:
            res = json.load(open(os.path.join(d, 'results.json')))
        except (OSError, ValueError):
            continue
        r0 = (res.get('results') or [{}])[0]
        runs = [json.loads(x) for x in open(os.path.join(d, 'runs.jsonl')) if x.strip()]
        T = tele(os.path.join(d, 'telemetry.jsonl.gz'))
        ts = [t[0] for t in T]
        t0, t1 = min(r['t_start_ms'] for r in runs), max(r['t_end_ms'] for r in runs)
        mx, s3, n = window(T, ts, t0, t1)
        tb = [x for x in (res.get('info') or {}).get('temp_before', []) if 'MINSHIRE Current' in x]
        loops.append({'part': 2, 'exp': 'E37', 'card': 'card 1', 'pass': p, 'what': 'mmbench %s (shared %s-pair pool%s)' % (
            wl, r0.get('ntiles'), ', private' if r0.get('private_pools') else ''), 'mode': r0.get('mode'),
            'idle_before_w': r0.get('idle_before_w'), 'mean_w': r0.get('mean_w'), 'max_w': mx, 'held3_w': s3, 'n': n,
            'summary_max_w': r0.get('max_w'), 'die_start': tb[0].split(':')[-1].strip() if tb else None})
ab = os.path.join(V3, 'ablb')
for p in sorted(os.listdir(ab)) if os.path.isdir(ab) else []:
    d = os.path.join(ab, p)
    try:
        runs = [json.loads(x) for x in open(os.path.join(d, 'runs.jsonl')) if x.strip()]
        starts = [json.loads(x) for x in open(os.path.join(d, 'starts.jsonl')) if x.strip()]
        T = tele(os.path.join(d, 'telemetry.jsonl.gz'))
    except (OSError, ValueError):
        continue
    ts = [t[0] for t in T]
    st = {(s.get('block'), s.get('config')): s for s in starts}
    by = {}
    for r in runs:
        if r.get('block', -1) < 0 or r.get('launch', 0) < 0:
            continue
        by.setdefault((r['block'], r['config']), []).append(r)
    for (blk, cfg), rr in sorted(by.items()):
        if not any(k in cfg for k in ('tenb', '_l1')):
            continue
        t0, t1 = min(r['t_start_ms'] for r in rr), max(r['t_end_ms'] for r in rr)
        mx, s3, n = window(T, ts, t0, t1)
        s = st.get((blk, cfg), {})
        loops.append({'part': 2, 'exp': 'E39', 'card': 'card 1', 'pass': p, 'what': '%s (block %s; B %s)' % (
            cfg, blk, 'streamed through TenB' if rr[0].get('b_stream') else 'in the L1'), 'mode': rr[0].get('type'),
            'cycles_per_op': rr[0].get('cycles_per_op'), 'max_w': mx, 'held3_w': s3, 'n': n,
            'die_start': s.get('start_temp')})

print('# aifoundry1 committed record: part 1, %d rgm136 device processes in %d sessions; part 2, %d September loop bursts on card 1'
      % (len(rows), len(sess_max), len(loops)))
for exp, card, sname, d, bmax, n in sess_max:
    print('session %-5s %-6s %-6s board max %6.2f W over %d samples  (%s)' % (exp, card, sname, bmax, n, d))
BLOCK = re.compile(r'^(gemm(?:c|h|v|nc)?\d|mmp?\d|tenb$)')
for card in ('card 1', 'card 0'):
    rr = sorted([r for r in rows if r['card'] == card], key=lambda r: -(r['held3_w'] or 0))
    print('\n== %s: the 30 highest held-on-3-samples board powers (W), every committed process read' % card)
    for r in rr[:30]:
        print('  %-5s %-6s %-26s %-6s %-11s held3 %6.2f max %6.2f est %s  %s' % (r['exp'], r['session'], r['run'][:26], r['type'],
                                                                             r['mask'], r['held3_w'] or -1, r['max_w'], r['est_peak_w'], r['values']))
    print('\n== %s: every block, stream or TenB process (the host\'s gemm<B>, gemmc<B>, gemmh<B>, mm<N>, tenb arms)' % card)
    for r in sorted([r for r in rr if BLOCK.match(r['token'] or '')], key=lambda r: (r['type'], r['token'], r['exp'], r['run'])):
        print('  %-5s %-6s %-26s %-5s held3 %6.2f max %6.2f  %s' % (r['exp'], r['session'], r['run'][:26], r['type'], r['held3_w'] or -1,
                                                                 r['max_w'], r['values']))
    print('\n== %s: every gemmL1x1x1 fp32 or fp16 process on all 32 shires (the resident op on random data and the kinds)' % card)
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
print('\n== card 1, part 2: the stream (E37, mmbench) and TenB (E39) loops in September, by burst (board W; die at the start)')
for x in sorted(loops, key=lambda x: (x['exp'], x['what'], x['pass'])):
    extra = ('idle before %.2f, results mean %.2f, results max %.2f' % (x['idle_before_w'], x['mean_w'], x['summary_max_w'])
             if x['exp'] == 'E37' else 'cycles an op %s' % x.get('cycles_per_op'))
    print('  %-3s %-3s %-58s %-5s held3 %6.2f max %6.2f n %4d die at start %s C; %s' % (
        x['exp'], x['pass'], x['what'][:58], x['mode'], x['held3_w'] or -1, x['max_w'] or -1, x['n'], x['die_start'], extra))
if outp:
    json.dump({'sessions': sess_max, 'rows': rows, 'loops': loops}, open(outp, 'w'), indent=0)
