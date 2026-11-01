#!/usr/bin/env python3
"""E98, a dated note (Q132(o), Sun 1 Nov 2026), POST HOC, read-only, standard library only: does E97's second plateau move sit in
P6's 20 min rest window? Reads this directory's history/aifoundry2-2026-11-01.jsonl.gz (the box's own 5 s rows) and results.json.
No verdict moves. Output: p6-rest-note.txt."""
import gzip, json, os, statistics as st, datetime as dt
H = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in gzip.open(os.path.join(H, 'history/aifoundry2-2026-11-01.jsonl.gz'), 'rt')]
res = json.load(open(os.path.join(H, 'results.json')))
P = {p['probe']: p for p in res['probes']}
D0 = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc).timestamp()


def ms(pst):  # PST = UTC - 8, after 02:00 PDT that night
    h, m = map(int, pst.split(':'))
    return int((D0 + (h + 8) * 3600 + m * 60) * 1000)


def win(a, b):
    A, B = ms(a), ms(b)
    return [r for r in rows if A <= r['t'] < B]


def m(rs, k):
    vals = [(r['cards'][0].get(k) if k in ('die', 'w') else r['temps'].get(k)) for r in rs]
    vals = [v for v in vals if v is not None]
    return st.mean(vals) if vals else float('nan')


e6 = P['P6']['rest20']['window_end_ms']
print('P6 rest20 window end, ms', e6, 'PST', dt.datetime.fromtimestamp(e6 / 1000 - 8 * 3600, dt.timezone.utc).strftime('%H:%M:%S'),
      '; the window is the 20 min before it; rows', P['P6']['rest20']['rows'], '; registered w', P['P6']['rest20']['w'], 'die', P['P6']['rest20']['die'])
a, b = win('05:39', '05:41'), win('05:44', '05:46')
print('E97 second move windows, aifoundry2 idle:')
print('  05:39-05:41 reading %.3f C, board %.3f W, NIC %.3f C, rows %d, held %d' % (m(a, 'die'), m(a, 'w'), m(a, 'nic'), len(a), sum(r['cards'][0]['held'] for r in a)))
print('  05:44-05:46 reading %.3f C, board %.3f W, NIC %.3f C, rows %d, held %d' % (m(b, 'die'), m(b, 'w'), m(b, 'nic'), len(b), sum(r['cards'][0]['held'] for r in b)))
print('  move: reading %+.3f C, board %+.3f W, NIC %+.3f C' % (m(b, 'die') - m(a, 'die'), m(b, 'w') - m(a, 'w'), m(b, 'nic') - m(a, 'nic')))
for t0, t1 in [('05:35', '05:41'), ('05:41', '05:44'), ('05:44', '05:48'), ('05:48', '05:50'), ('05:50', '05:55')]:
    r = win(t0, t1)
    print('  %s-%s reading %.3f C, board %.3f W, NIC %.3f C, CPU %.1f%%, rows %d' % (t0, t1, m(r, 'die'), m(r, 'w'), m(r, 'nic'), st.mean(x['cpu'] for x in r), len(r)))
full = win('05:35', '05:55')
out = [r for r in full if not (ms('05:42') <= r['t'] < ms('05:49'))]
wf, wo = m(full, 'w'), m(out, 'w')
print('P6 rest W, 20 min %.4f; leaving out 05:42-05:49 %.4f; difference %+.4f W; rows %d' % (wf, wo, wo - wf, len(out)))
# the registered W-to-die factor, from results.json
for k in ('P1', 'P3', 'P6', 'P7'):
    print(k, 'rest_w', P[k]['rest_w'], 'rest_die_w_derived', P[k]['rest_die_w_derived'])
slope = (P['P1']['rest_die_w_derived'] - P['P7']['rest_die_w_derived']) / (P['P1']['rest_w'] - P['P7']['rest_w'])
print('W to rest-die scale implied by results.json: %.3f C per W' % slope)
dx = (wo - wf) * slope
print('so P6 moves %+.3f C of rest die; the contrast P1 minus the mean of P3, P6, P7 goes from %.3f to %.3f C' % (
    dx, P['P1']['rest_die_w_derived'] - st.mean(P[k]['rest_die_w_derived'] for k in ('P3', 'P6', 'P7')),
    P['P1']['rest_die_w_derived'] - st.mean([P['P3']['rest_die_w_derived'], P['P6']['rest_die_w_derived'] + dx, P['P7']['rest_die_w_derived']])))
# R1's and R2's points, as a sensitivity only
r1 = res['R1']; r2 = res['R2']
print('R1 keys', list(r1.keys())[:12]); print('R2 keys', list(r2.keys())[:12])
def ols(x, y):
    xb, yb = st.mean(x), st.mean(y)
    return sum((a - xb) * (b - yb) for a, b in zip(x, y)) / sum((a - xb) ** 2 for a in x)
pp = r1.get('per_probe')
print('R1 per_probe sample', json.dumps(pp)[:400] if pp else None)
for name, rr in (('R1', r1), ('R2', r2)):
    ks = ['P1', 'P3', 'P6', 'P7']
    y = [rr['per_probe'][k] if not isinstance(rr['per_probe'][k], dict) else rr['per_probe'][k].get('die', rr['per_probe'][k].get('y')) for k in ks]
    x0 = [P[k]['rest_die_w_derived'] for k in ks]
    x1 = [P[k]['rest_die_w_derived'] + (dx if k == 'P6' else 0) for k in ks]
    print(name, 'y', y, 'slope as registered %.3f; with P6 moved %.3f (a sensitivity, not a verdict)' % (ols(x0, y), ols(x1, y)), 'registered fit', json.dumps(rr['fit'])[:160])
