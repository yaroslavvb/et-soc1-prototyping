#!/usr/bin/env python3
"""lnc-form step 6 (REPORTED, post hoc; decides nothing): lnc-energy's committed rail reducer (tools/matmul/mm1/v3.2-terms/gemmlnc/s02_rails.py,
its reading unchanged: work = the 10 Hz samples inside a counted launch, rest = the 5 s before the run's first process, medians) applied to
E218's committed session (b445b0f5) with E218's own host_records and counted (tools/claims-v3/e218/e218_common.py): each gemmLnc point minus
its cooperative twin, by rail. /usr/bin/python3 3.12.3, standard library."""
import gzip
import importlib.util
import json
import os
import statistics
import sys

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
OUT = os.environ.get('LNC_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
SESS = {
    'E218': (os.path.join(LAB, 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/session'), 'tools/claims-v3/e218/e218_common.py',
             'aifoundry3 card 0'),
}
RAILS = ('board', 'minion', 'sram', 'noc')


def load_mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LAB, rel))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.join(LAB, rel)))
    spec.loader.exec_module(m)
    return m


def load_tel(sd):
    out = []
    with gzip.open(os.path.join(sd, 'telemetry.jsonl.gz'), 'rt') as f:
        for ln in f:
            if not ln.startswith('{'):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            sp = s.get('sp') or {}

            def g(k):
                v = sp.get(k)
                return float(v[0]) if isinstance(v, list) and v and v[0] is not None else None
            out.append((s.get('t_ms'), s.get('board_w'), g('minion_w'), g('sram_w'), g('noc_w'),
                        ((s.get('temp_c') or {}).get('minshire') or [None])[0]))
    return sorted([x for x in out if x[0] is not None])


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


rows = []
for exp, (sd, common, card) in SESS.items():
    C = load_mod(common, 'common_' + exp)
    tel = load_tel(sd)
    for rd in sorted(os.listdir(os.path.join(sd, 'runs'))):
        d = os.path.join(sd, 'runs', rd)
        pj = os.path.join(d, 'run.json')
        if not os.path.exists(pj):
            continue
        rec = json.load(open(pj))
        procs = rec.get('procs') or []
        if not procs:
            continue
        launches = []
        for p in procs:
            po = os.path.join(d, p['name'] + '.out')
            txt = open(po, errors='replace').read() if os.path.exists(po) else ''
            fma, _, _ = C.host_records(txt, p.get('argv'))
            launches += fma
        cnt = [L for L in launches if C.counted(L)]
        if not cnt:
            continue
        t_first = procs[0]['t0_ms']
        rest = [x for x in tel if t_first - 5000 <= x[0] < t_first]
        work = [x for x in tel if any(L['t_start_ms'] <= x[0] <= L['t_end_ms'] for L in cnt)]
        r = {'exp': exp, 'card': card, 'run': rd, 'id': rec.get('id'), 'name': rec.get('name'), 'block': rec.get('block'),
             'family': procs[0].get('family'), 'n_work': len(work), 'n_rest': len(rest),
             'die_start_c': med([x[5] for x in rest])}
        for j, k in enumerate(RAILS):
            w, rr = med([x[1 + j] for x in work]), med([x[1 + j] for x in rest])
            r[k + '_work'] = w
            r[k + '_rest'] = rr
            r[k + '_over_idle'] = (w - rr) if (w is not None and rr is not None) else None
        rows.append(r)

json.dump(rows, open(os.path.join(OUT, 's06_rails_e218_runs.json'), 'w'), indent=1)
print('runs with a counted launch:', len(rows), {e: sum(1 for r in rows if r['exp'] == e) for e in SESS})

# per (exp, id): the mean over its runs
pts = {}
for r in rows:
    pts.setdefault((r['exp'], r['id']), []).append(r)
P = {}
for k, rs in pts.items():
    P[k] = {'name': rs[0]['name'], 'family': rs[0]['family'], 'n_runs': len(rs)}
    for rail in RAILS:
        v = [x[rail + '_over_idle'] for x in rs if x[rail + '_over_idle'] is not None]
        P[k][rail] = sum(v) / len(v) if v else None
    for rail in RAILS:
        v = [x[rail + '_rest'] for x in rs if x[rail + '_rest'] is not None]
        P[k][rail + '_rest'] = sum(v) / len(v) if v else None

PAIRS = [('E218', 'g%02d' % i, 'g%02dt' % i) for i in range(1, 13) if i != 7]
print('\nW over idle by rail (W), gemmLnc vs its rgm136 gemmL twin (mean over runs; medians inside each run window):')
print('%-6s %-5s %-16s %3s | %7s %7s %7s %7s | %-5s %3s | %7s %7s %7s %7s | %7s %7s %7s %7s' % (
    'exp', 'id', 'name', 'n', 'board', 'minion', 'sram', 'noc', 'twin', 'n', 'board', 'minion', 'sram', 'noc', 'dboard', 'dminion', 'dsram',
    'dnoc'))
out_pairs = []
for exp, a, b in PAIRS:
    x, y = P.get((exp, a)), P.get((exp, b))
    if not x or not y:
        print('MISSING', exp, a, b, bool(x), bool(y))
        continue
    d = {rail: (x[rail] - y[rail]) for rail in RAILS}
    out_pairs.append({'exp': exp, 'lnc': a, 'twin': b, 'lnc_rails': x, 'twin_rails': y, 'delta': d})
    print('%-6s %-5s %-16s %3d | %7.2f %7.2f %7.2f %7.2f | %-5s %3d | %7.2f %7.2f %7.2f %7.2f | %7.2f %7.2f %7.2f %7.2f' % (
        exp, a, x['name'][:16], x['n_runs'], x['board'], x['minion'], x['sram'], x['noc'], b, y['n_runs'], y['board'], y['minion'], y['sram'],
        y['noc'], d['board'], d['minion'], d['sram'], d['noc']))
json.dump({'points': {f'{k[0]}|{k[1]}': v for k, v in P.items()}, 'pairs': out_pairs}, open(os.path.join(OUT, 's06_rails_e218_points.json'), 'w'),
          indent=1)
print('\nshares of the excess by rail (dX / dboard):')
for q in out_pairs:
    d = q['delta']
    print('%-6s %-5s minion %.2f  sram %.2f  noc %.2f  (sum of rails %.2f of board)' % (
        q['exp'], q['lnc'], d['minion'] / d['board'], d['sram'] / d['board'], d['noc'] / d['board'],
        (d['minion'] + d['sram'] + d['noc']) / d['board']))
