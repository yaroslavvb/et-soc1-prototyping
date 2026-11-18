#!/usr/bin/env python3
"""v31-counts (Q217) step 1: list every (experiment, card, format, kind) among MM1-v3's own energy points (and E212's pattern runs, which
data_v3.py keeps out of energy) that MM1-v3's switch route cannot price for want of a count (energy_v3.counts() is None) or of a phi
(energy_v3.phi_of() is None). Reads MM1-v3 as landed (b1493082, at GitHub main 6efdb002), extracted read-only by git archive into this
lane's work folder; changes nothing there. Desk; no device. Run: python3 -I -B s01_enum_unpriced.py <v3 dir> <out json>
"""
import collections
import json
import os
import sys

V3 = os.path.abspath(sys.argv[1])
OUT = sys.argv[2]
sys.path.insert(0, V3)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402

EP = D.energy_points()
rows = collections.OrderedDict()
for e in EP:
    pre, b = E.arm_parts(e['arm'])
    KB = b[2] if b else 1
    c = EN.counts(e['fmt'], e['kind'], KB)
    p = EN.phi_of(e['fmt'], e['kind'], KB)
    if c is None or p is None:
        key = (e['exp'], e['card'], e['fmt'], e['kind'], 'S1' if KB == 1 else 'S2')
        r = rows.setdefault(key, {'exp': e['exp'], 'card': e['card'], 'fmt': e['fmt'], 'kind': e['kind'], 'KB_class': key[4],
                                  'count': c is not None, 'phi': p is not None, 'n_points': 0, 'values': set(), 'arms': set()})
        r['n_points'] += 1
        if e.get('values'):
            r['values'].add(str(e['values']).split(':', 1)[-1])
        r['arms'].add(e['arm'])
# E212's pattern runs: data_v3 reads them for time only (kind 'pattern:<name>'); list them with their KB classes
pat = collections.OrderedDict()
for r in D.e212_runs():
    if str(r['kind']).startswith('pattern:'):
        pre, b = E.arm_parts(r['arm'])
        KB = b[2] if b else 1
        key = (r['card'], r['fmt'], r['kind'], 'S1' if KB == 1 else 'S2')
        q = pat.setdefault(key, {'card': r['card'], 'fmt': r['fmt'], 'kind': r['kind'], 'KB_class': key[3], 'n_runs': 0, 'arms': set(),
                                 'sessions': set()})
        q['n_runs'] += 1
        q['arms'].add(r['arm'])
        q['sessions'].add(r['session'])


def jl(d):
    out = []
    for v in d.values():
        v = dict(v)
        for k in list(v):
            if isinstance(v[k], set):
                v[k] = sorted(v[k])
        out.append(v)
    return out


res = {'what': 'MM1-v3 energy points (and E212 pattern runs) the switch route cannot price: no count or no phi (desk, from v3 as landed)',
       'v3_dir': 'tools/matmul/mm1/v3 at GitHub main 6efdb002 (MM1-v3 landed b1493082)', 'python': sys.version.split()[0],
       'n_energy_points': len(EP), 'unpriced_energy_points': jl(rows), 'e212_pattern_runs_time_only': jl(pat)}
json.dump(res, open(OUT, 'w'), indent=1)
print('energy points', len(EP), '; unpriced groups', len(rows), '; unpriced points', sum(r['n_points'] for r in rows.values()))
for r in jl(rows):
    print(f"  {r['exp']:6s} {r['card']:18s} {r['fmt']:5s} {r['kind']:28s} {r['KB_class']} count={r['count']!s:5s} phi={r['phi']!s:5s} n={r['n_points']:3d} "
          f"values={r['values'][:4]}")
print('E212 pattern runs (time only in v3):', sum(q['n_runs'] for q in pat.values()))
for q in jl(pat):
    print(f"  {q['card']:18s} {q['fmt']:5s} {q['kind']:24s} {q['KB_class']} runs={q['n_runs']} arms={q['arms']} sessions={q['sessions']}")
