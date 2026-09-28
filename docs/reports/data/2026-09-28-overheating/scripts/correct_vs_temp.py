#!/usr/bin/env python3
"""Did anything compute wrong, fail or report a hardware error when the die was hot?

Joins every launch record under docs/reports/data (any JSON line with t_start_ms and t_end_ms) to the same card's
telemetry (every JSON line with temp_c and t_ms), and reports, per card and die-temperature bin (the hottest 34-sensor
MEAN seen from 0.3 s before the launch to 0.3 s after it), how many launches: ran, had their results checked, had a
wrong result, reported a hardware tensor error, or did not complete (ok false).

Correctness fields by workload (read from the host sources):
  mmbench   check == "exact": every tile compared exactly; bad_minions, launch_errors      (launchers/mmbench)
  sparsity  result in {both, math, prm-literal}: C tiles compared exactly; "wrong" = mismatch; "unchecked" = randn fp32;
            gemv/other tests: "wrong" = count of wrong outputs; tensor_errors = harts whose tensor_error CSR != 0
            (workloads/sparsity/host/main.cpp:511-550, 615, 767-792)
  relay     wrong_elements (workloads/onchip)
  nocbench  checked > 0: ring values compared (workloads/nocbench/host/main.cpp:774-795)
  enercat   verify.checked / verify.mismatches (gathers and scatters); otherwise ok = completed with every hart's
            record (workloads/enercat/host: no arithmetic check)
The overheating experiments' own directory (2026-09-28-overheating) is left out: its launches are checked by
tools/claims-v3/oh/reduce.py (reductions/oh2.json), and its outputs are tarred, so this scan would see only their
unchecked launch lines. Writes docs/reports/data/2026-09-28-overheating/analysis/correct_vs_temp.json.
Usage: python3 correct_vs_temp.py [docs/reports/data] > out.txt
"""
import bisect, collections, gzip, json, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'correct_vs_temp.json')
EXCLUDE = '2026-09-28-overheating'


def card_of(p):
    b = os.path.basename(p)
    if b.startswith('guard.jsonl') or 'card0' in b:
        return 'aifoundry1-c0'
    for c in ('aifoundry1-c1', 'aifoundry1-c0', 'aifoundry2', 'aifoundry3'):
        if c in p:
            return c
    if '/a1c1' in p:
        return 'aifoundry1-c1'
    return None


def lines_of(p):
    op = gzip.open if p.endswith('.gz') else open
    try:
        with op(p, 'rt', errors='replace') as fh:
            for line in fh:
                yield line
    except (OSError, EOFError):
        return


TEL = collections.defaultdict(list)   # card -> [(t_ms, mean, high, windowed)]
RECS = []                             # (card, path, record)
for d, _, fs in os.walk(ROOT):
    if EXCLUDE in d:
        continue
    for f in fs:
        if not re.search(r'\.(jsonl|json|out|log|txt)(\.gz)?$', f):
            continue
        p = os.path.join(d, f)
        c = card_of(p)
        if c is None:
            continue
        for line in lines_of(p):
            i = line.find('{')
            if i < 0:
                continue
            if '"temp_c"' in line and '"t_ms"' in line:
                try:
                    s = json.loads(line[i:])
                except ValueError:
                    continue
                ms = (s.get('temp_c') or {}).get('minshire')
                if isinstance(ms, list) and ms and s.get('t_ms'):
                    hi = ms[2] if len(ms) == 3 else None
                    TEL[c].append((s['t_ms'], ms[0], hi, (s.get('since_reset_ms') or -1) >= 0))
            elif '"t_start_ms"' in line and '"t_end_ms"' in line:
                try:
                    r = json.loads(line[i:])
                except ValueError:
                    continue
                if isinstance(r, dict) and r.get('t_start_ms') and r.get('t_end_ms'):
                    RECS.append((c, p, r))

for c in TEL:
    TEL[c].sort()
KEYS = {c: [x[0] for x in TEL[c]] for c in TEL}


def hottest(c, t0, t1, pad=300):
    if c not in KEYS:
        return None, None
    k = KEYS[c]
    a, b = bisect.bisect_left(k, t0 - pad), bisect.bisect_right(k, t1 + pad)
    xs = TEL[c][a:b]
    if not xs:
        return None, None
    return max(x[1] for x in xs), max((x[2] for x in xs if x[2] is not None and x[3]), default=None)


def classify(r):
    """-> (kind, checked, wrong, tensor_err, not_ok)"""
    ok = r.get('ok')
    not_ok = ok is False
    te = (r.get('tensor_errors') or 0) > 0
    if r.get('check') is not None:                       # mmbench
        chk = r.get('check') in ('exact', 'approx')       # approx: iters past the exact limit, compared within tolerance
        wrong = (r.get('bad_minions') or 0) > 0 or (r.get('launch_errors') or 0) > 0
        if r.get('private_pools') and r.get('mode') in ('fp32', 'fp16'):
            return 'mmbench-private-by-design', False, False, te, False   # fails its check by design (03-experiments E37)
        return 'mmbench', chk, wrong, te, not_ok
    if 'result' in r and r.get('test') == 'fma':         # sparsity fma
        chk = r['result'] in ('both', 'math', 'prm-literal', 'wrong')
        return 'sparsity-fma', chk, r['result'] == 'wrong', te, not_ok
    if 'wrong' in r:                                     # sparsity gemv etc.
        return 'sparsity-' + str(r.get('test')), True, (r.get('wrong') or 0) > 0, te, not_ok
    if 'wrong_elements' in r:
        return 'relay', True, (r.get('wrong_elements') or 0) > 0, te, not_ok
    if 'checked' in r and r.get('test') is not None and 'gbps_kernel' in r:
        return 'nocbench', (r.get('checked') or 0) > 0, (r.get('checked') or 0) > 0 and not_ok, te, not_ok
    v = r.get('verify')
    if isinstance(v, dict):
        return 'enercat-gs', (v.get('checked') or 0) > 0, (v.get('mismatches') or 0) > 0 or v.get('ok') is False, te, not_ok
    if 'ops_per_cycle_per_hart' in r:
        return 'enercat', False, False, te, not_ok
    if 'tensor_errors' in r:
        return 'sparsity-other', False, False, te, not_ok
    return 'other', False, False, te, not_ok


BINS = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 100), (100, 130)]
tab = collections.defaultdict(lambda: collections.Counter())
bad_list, seen = [], set()
top = collections.defaultdict(lambda: (-1, None))
for c, p, r in RECS:
    key = (c, r['t_start_ms'], r['t_end_ms'], r.get('cycles_max'), r.get('launch'))
    if key in seen:                     # the same launch filed twice (a copy of a directory)
        continue
    seen.add(key)
    kind, chk, wrong, te, not_ok = classify(r)
    if kind == 'other':
        continue
    T, H = hottest(c, r['t_start_ms'], r['t_end_ms'])
    if T is None:
        tb = 'no-tel'
    else:
        tb = next('%d-%d' % b for b in BINS if b[0] <= T < b[1])
    t = tab[(c, tb)]
    t['launches'] += 1
    t['checked'] += chk
    t['wrong'] += wrong
    t['tensor_err'] += te
    t['not_ok'] += not_ok
    t['kind:' + kind] += 1
    if chk:
        t['chk:' + kind] += 1
    if chk and T is not None and T > top[c][0]:
        top[c] = (T, (kind, p, r.get('t_start_ms'), H))
    if wrong or te or not_ok:
        bad_list.append((c, T, H, kind, p, {k: r.get(k) for k in ('cfg', 'label', 'test', 'result', 'wrong', 'wrong_elements',
                                                             'bad_minions', 'launch_errors', 'tensor_errors', 'ok',
                                                             't_start_ms', 'ghz', 'implied_ghz') if k in r}))

print('telemetry samples per card:', {c: len(v) for c, v in TEL.items()})
print('launch records (deduplicated):', len(seen))
print()
print('%-14s %-8s %8s %8s %6s %6s %6s' % ('card', 'mean C', 'launches', 'checked', 'wrong', 'tens.e', 'not_ok'))
for (c, tb) in sorted(tab, key=lambda x: (x[0], x[1] if x[1] != 'no-tel' else 'zzz')):
    t = tab[(c, tb)]
    print('%-14s %-8s %8d %8d %6d %6d %6d' % (c, tb, t['launches'], t['checked'], t['wrong'], t['tensor_err'], t['not_ok']))
print()
print('checked launches by kind, 80 C and above:')
for (c, tb), t in sorted(tab.items()):
    if tb in ('80-90', '90-100', '100-130'):
        print(' ', c, tb, {k[4:]: v for k, v in t.items() if k.startswith('chk:')}, 'all kinds:', {k[5:]: v for k, v in t.items() if k.startswith('kind:')})
print()
print('hottest CHECKED launch per card (mean C, kind, file, t_start_ms, windowed hottest sensor):')
for c, (T, info) in sorted(top.items()):
    print(' ', c, T, info)
print()
print('every launch with a wrong result, a tensor error or ok false (%d):' % len(bad_list))
for b in sorted(bad_list, key=lambda x: (x[0], x[1] or 0)):
    print(' ', b)

J = {'excluded': EXCLUDE, 'telemetry_samples': {c: len(v) for c, v in TEL.items()}, 'launch_records': len(seen),
     'bins': [{'card': c, 'bin': tb, **{k: tab[(c, tb)][k] for k in ('launches', 'checked', 'wrong', 'tensor_err', 'not_ok')},
               'checked_by_kind': {k[4:]: v for k, v in tab[(c, tb)].items() if k.startswith('chk:')}}
              for (c, tb) in sorted(tab)],
     'hottest_checked': {c: {'mean_c': T, 'kind': info[0], 'file': info[1], 't_start_ms': info[2]} for c, (T, info) in top.items()},
     'bad': [{'card': b[0], 'mean_c': b[1], 'kind': b[3], 'file': b[4], **b[5]} for b in sorted(bad_list, key=lambda x: (x[0], x[1] or 0))]}
json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
