"""E223 (reg-e223, Q239) desk: the committed record of board power, run by run, for the three cards E223 uses (E223.md section 5;
post hoc, it adds no rule): aifoundry1 card 1, aifoundry1 card 0 and aifoundry2 card 0. E221's card_record_e221.py (itself E219's
and E217's), with E221's nine sweep sessions and the lab's E220 and E224 card days on these cards added:
  the committed rgm136 sessions (session/runs/*/run.json with session/telemetry.jsonl.gz, or runs/ and telemetry.jsonl.gz without a
  session/ level): E208's, E212's, E214's, E217's, E219's and E221's sweep sessions by name (a1c1, a1c0, a2c0); E206 arm B, E213 arm
  B, E215 arm B, E220 arm A and E224 arm A (aifoundry1 card 1); E190 arm B (aifoundry1 card 1) and E190's aifoundry2 arm; E209,
  E216, E220 arm B and E224 arm B (aifoundry2 card 0's blind days); each device process's window [t0_ms, t1_ms] read against
  the telemetry's board_w samples: the highest sample, and the highest value held on 3 samples in a row (the stop rule's form), with the run's planned estimate where its schedule gave one;
  the host's arm token, format, data kind (by the tile's file name: randn or full under the randn generator = rnd; zeros; ones;
  any other tile 'other:<name>') and mask from --values, --type and --shires.
  With E223's src/ as a second argument it also prints, per card, E223's highest planned runs against the committed processes of the
  same configuration (token, format, data, mask) on that card, and of the same token, format and data at any mask; and the highest
  committed held-on-3 board power of fp32 and fp16 random gemmL processes on all 32 shires by footprint band (MB, from the token);
  and (E223's addition) E223's planned runs by regime (type, data, whole chip or subset mask, footprint band) against the committed
  processes of the same regime on that card, with their measured max minus planned estimate where their schedule gave one.
Reads committed lab files only (Python's own modules); writes its standard output and, if a third argument is given, a JSON of every
row.
    /usr/bin/python3 -I -B card_record_e223.py <lab tree> [<E223 src dir> [<out json>]]
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import json
import os
import re
import sys

lab = sys.argv[1]
src = sys.argv[2] if len(sys.argv) > 2 else None
outp = sys.argv[3] if len(sys.argv) > 3 else None
ddir = os.path.join(lab, 'docs', 'reports', 'data')
CARDN = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a2c0': 'aifoundry2 card 0'}
SESS = []
for d in sorted(os.listdir(ddir)):
    m = re.match(r'\d{4}-\d\d-\d\d-(e208|e212|e214|e217|e219|e221)-mmsweep\d?-(a1c[01]|a2c0)-(S\d+r?)$', d)
    if m:
        SESS.append((os.path.join(d, 'session'), m.group(1).upper(), CARDN[m.group(2)], m.group(3)))
for d, exp, card, sname in (('2026-11-17-e206-matmul-sweep-aifoundry1-c1', 'E206', 'a1c1', 'arm B'),
                            ('2026-11-18-e213-blind-matmul-aifoundry1-c1', 'E213', 'a1c1', 'arm B'),
                            ('2026-11-19-e215-blind-matmul-aifoundry1-c1', 'E215', 'a1c1', 'arm B'),
                            ('2026-11-20-e220-blind-matmul-aifoundry1-c1', 'E220', 'a1c1', 'arm A'),
                            ('2026-11-21-e224-blind-matmul-aifoundry1-c1', 'E224', 'a1c1', 'arm A'),
                            ('2026-11-17-e209-blind-matmul-aifoundry2', 'E209', 'a2c0', 'day'),
                            ('2026-11-19-e216-blind-matmul-aifoundry2', 'E216', 'a2c0', 'day'),
                            ('2026-11-20-e220-blind-matmul-aifoundry2', 'E220', 'a2c0', 'arm B'),
                            ('2026-11-21-e224-blind-matmul-aifoundry2', 'E224', 'a2c0', 'arm B')):
    if os.path.isdir(os.path.join(ddir, d)):
        SESS.append((os.path.join(d, 'session'), exp, CARDN[card], sname))
for sub, card, sname in (('aifoundry1-c1', 'a1c1', 'arm B'), ('aifoundry2', 'a2c0', 'arm A')):
    if os.path.isdir(os.path.join(ddir, '2026-11-13-e190-large-gemm', sub)):
        SESS.append((os.path.join('2026-11-13-e190-large-gemm', sub), 'E190', CARDN[card], sname))


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


def kind_of(values):
    parts = (values or '').split(':')
    gen = parts[1] if len(parts) > 1 else ''
    base = os.path.basename(parts[2]) if len(parts) > 2 else ''
    if gen == 'randn' and base in ('randn.bin', 'full.bin'):
        return 'rnd'
    if gen == 'tiles' and base in ('zeros.bin', 'ones.bin'):
        return base[:-4]
    return 'other:%s:%s' % (gen, base)


def foot_mb(tok, fmt):
    m = re.fullmatch(r'gemmL(\d+)x(\d+)x(\d+)', tok or '')
    if not m:
        return None
    mb, nb, kb = (int(x) for x in m.groups())
    return (mb * kb * 64 * 32 * 1024 + kb * nb * 32 * 32 * 1024 + mb * nb * 64 * 32 * 1024) / 1048576.0


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
            tok = v.split(':')[0]
            fmt = argval(argv, '--type')
            rows.append({'exp': exp, 'card': card, 'session': sname, 'run': rn, 'values': v, 'token': tok, 'type': fmt,
                         'kind': kind_of(v), 'mask': argval(argv, '--shires'), 'footprint_mb': foot_mb(tok, fmt),
                         'est_peak_w': est, 'max_w': mx, 'held3_w': s3, 'n': n, 'rc': pr.get('rc')})

print('# the committed record of board power on aifoundry1 card 1, aifoundry1 card 0 and aifoundry2 card 0: %d rgm136 device '
      'processes in %d sessions' % (len(rows), len(sess_max)))
for exp, card, sname, d, bmax, n in sess_max:
    print('session %-5s %-18s %-6s board max %6.2f W over %d samples  (%s)' % (exp, card, sname, bmax, n, d))
for card in CARDN.values():
    rr = sorted([r for r in rows if r['card'] == card], key=lambda r: -(r['held3_w'] or 0))
    print('\n== %s: %d committed processes; the 30 highest held-on-3-samples board powers (W)' % (card, len(rr)))
    for r in rr[:30]:
        print('  %-5s %-6s %-26s %-6s %-11s held3 %6.2f max %6.2f est %s  %s' % (r['exp'], r['session'], r['run'][:26], r['type'],
                                                                             r['mask'], r['held3_w'] or -1, r['max_w'], r['est_peak_w'], r['values']))
    print('\n== %s: every gemmL1x1x1 fp32 or fp16 process on all 32 shires (the resident op on random data and the kinds)' % card)
    for r in sorted([r for r in rr if (r['values'] or '').startswith('gemmL1x1x1:') and r['type'] in ('fp32', 'fp16')
                     and r['mask'] == '0xffffffff'], key=lambda r: (r['type'], r['values'], r['exp'])):
        print('  %-5s %-6s %-26s %-5s held3 %6.2f max %6.2f est %s  %s' % (r['exp'], r['session'], r['run'][:26], r['type'],
                                                                      r['held3_w'] or -1, r['max_w'], r['est_peak_w'], r['values']))
    ests = [(r['max_w'] - r['est_peak_w'], r) for r in rr if r['est_peak_w']]
    if ests:
        ests.sort(key=lambda x: -x[0])
        print('\n== %s: measured max minus planned estimate over %d processes with an estimate: largest %+.2f W, %d over +0 W; '
              'the 15 largest' % (card, len(ests), ests[0][0], sum(1 for d, _ in ests if d > 0)))
        for dlt, r in ests[:15]:
            print('  %+6.2f  %-5s %-6s %-26s %-11s max %6.2f est %5.1f  %s' % (dlt, r['exp'], r['session'], r['run'][:26], r['mask'],
                                                                        r['max_w'], r['est_peak_w'], r['values']))
    print('\n== %s: fp32 and fp16 random gemmL processes on all 32 shires, the highest held-on-3 board power by footprint band' % card)
    for lo, hi in ((0, 8), (8, 40), (40, 80), (80, 200), (200, 700)):
        for fmt in ('fp32', 'fp16'):
            xs = [r for r in rr if r['type'] == fmt and r['kind'] == 'rnd' and r['mask'] == '0xffffffff' and r['footprint_mb'] is not None
                  and lo < r['footprint_mb'] <= hi and r['held3_w'] is not None]
            if xs:
                top = max(xs, key=lambda r: r['held3_w'])
                print('  %-4s %3d-%3d MB: %4d processes, held3 at most %6.2f W (%s %s %s), max sample at most %6.2f W' % (
                    fmt, lo, hi, len(xs), top['held3_w'], top['exp'], top['session'], top['values'].split(':')[0],
                    max(r['max_w'] for r in xs)))

if src:
    A = {a['id']: a for a in json.load(open(os.path.join(src, 'arms.json')))['arms']}
    plan = {}
    for fn in sorted(os.listdir(os.path.join(src, 'sched'))):
        s = json.load(open(os.path.join(src, 'sched', fn)))
        for r in s['runs'] + [dict(x, smoke=True) for x in s['smoke']]:
            if r.get('role') == 'null':
                continue
            key = (s['card'], r['arm'])
            plan[key] = max(plan.get(key, 0), r['est_peak_w'])
    print('\n# E223: the highest planned runs per card (src/sched/*.json est_peak_w, smoke included) against the committed record on '
          'that card (same configuration = token, format, data, mask; then the same token, format and data at any mask)')
    for ck, card in CARDN.items():
        rr = [r for r in rows if r['card'] == card]
        items = sorted([(w, arm) for (c, arm), w in plan.items() if c == ck], key=lambda x: -x[0])
        print('\n== %s: E223 runs planned at or above %.1f W (the 20 highest planned)' % (card, items[min(19, len(items) - 1)][0]))
        for w, arm in items[:20]:
            a = A.get(arm)
            if a is None:
                m = re.fullmatch(r'(\d+)x(\d+)x(\d+)-(fp32|fp16|int8)-(rnd|zeros|ones)(?:-s(\d+)|-m([0-9a-f]+))?', arm)
                tok = 'gemmL%sx%sx%s' % m.group(1, 2, 3)
                fmt, kind = m.group(4), m.group(5)
                mask = '0xffffffff' if not (m.group(6) or m.group(7)) else ('0x%x' % ((1 << int(m.group(6))) - 1) if m.group(6) else '0x' + m.group(7))
            else:
                tok, fmt, kind, mask = a['values'].split(':')[0], a['type'], a['kind'], a['shires']
            same = [r for r in rr if r['token'] == tok and r['type'] == fmt and r['kind'] == kind and r['mask'] == mask and r['held3_w']]
            anym = [r for r in rr if r['token'] == tok and r['type'] == fmt and r['kind'] == kind and r['held3_w']]
            f = ('same config: %d, held3 %.2f-%.2f W, max sample %.2f W' % (len(same), min(r['held3_w'] for r in same),
                                                                           max(r['held3_w'] for r in same), max(r['max_w'] for r in same))
                 if same else 'same config: none')
            g = ('; any mask: %d, held3 at most %.2f W' % (len(anym), max(r['held3_w'] for r in anym)) if anym else '; any mask: none')
            print('  planned %5.1f W  %-30s %s%s' % (w, arm, f, g))
    # E223's own addition: E223's planned runs by regime (format, data, whole chip or a subset mask, footprint band) against the
    # committed record in the same regime on that card, and the measured-minus-planned spread of the committed processes there
    BANDS = ((0, 8), (8, 20), (20, 40), (40, 80), (80, 200), (200, 700))

    def band(mb):
        for lo, hi in BANDS:
            if lo < mb <= hi:
                return '%d-%d MB' % (lo, hi)
        return 'other'
    print('\n# E223: its planned runs by regime (type, data, whole chip or subset, footprint band) against the committed record in the '
          'same regime on that card: held3 / max sample at most, and measured max minus planned over the regime\'s processes with an estimate')
    for ck, card in CARDN.items():
        rr = [r for r in rows if r['card'] == card and r['footprint_mb'] is not None and r['kind'] in ('rnd', 'zeros', 'ones')]
        reg = {}
        for (c, arm), w in plan.items():
            if c != ck:
                continue
            a = A.get(arm)
            if a is None:
                continue
            key = (a['type'], a['kind'], 'whole' if a['shires'] == '0xffffffff' else 'subset', band(a['footprint_mb']))
            reg.setdefault(key, []).append((w, arm, a['footprint_mb']))
        print('\n== %s: %d regimes' % (card, len(reg)))
        for key in sorted(reg, key=lambda k: -max(w for w, _, _ in reg[k])):
            xs = reg[key]
            fmt, kind, whole, bnd = key
            lo, hi = [int(v) for v in bnd.split(' ')[0].split('-')]
            ys = [r for r in rr if r['type'] == fmt and r['kind'] == kind and ((r['mask'] == '0xffffffff') == (whole == 'whole'))
                  and lo < r['footprint_mb'] <= hi and r['held3_w'] is not None]
            de = [r['max_w'] - r['est_peak_w'] for r in ys if r['est_peak_w']]
            rec = ('record %d processes, held3 at most %.2f W, max sample at most %.2f W%s' % (
                len(ys), max(r['held3_w'] for r in ys), max(r['max_w'] for r in ys),
                ('; measured minus planned %+.2f to %+.2f W over %d' % (min(de), max(de), len(de))) if de else '; no estimate')
                if ys else 'record: none')
            print('  %-4s %-5s %-6s %-11s E223 %3d run(s) of %3d arm(s), planned %.1f-%.1f W, %g-%g MB; %s' % (
                fmt, kind, whole, bnd, len(xs), len({x[1] for x in xs}), min(w for w, _, _ in xs), max(w for w, _, _ in xs),
                min(x[2] for x in xs), max(x[2] for x in xs), rec))
if outp:
    json.dump({'sessions': sess_max, 'rows': rows}, open(outp, 'w'), indent=0)
