#!/usr/bin/env python3
"""fix-v31counts (Q217) step 5: the rebuilt tables against v31-counts' published ones (desk; reads files, writes work/tables-diff.json + .txt).
Allowed changes, and nothing else:
  counts-fp32-gemm-states.json: shapes.S2['real:blind4'] (its numbers, n_points, counts_source); a 'note' and 'tiles_measured' on real:blind4
      S1 and S2 and on e37 S1 and S2; the top-level 'what' and 'driver' texts and a new 'fix' entry;
  counts-v31.csv: the same rows in the same order, every old column equal except real:blind4 S2's counts; a new 'note' column;
  counts-v31-tiles.csv: the same rows, every old column equal; two new columns (counts_footing = MM1-v3's COUNT_FOOTING[fmt], and the
      bench sources manifest sha256);
  counts-fp16-int8-launch.json, crosscheck-launch-fp32.json and .txt: byte for byte equal.
    /usr/bin/python3 -I -B s05_diff.py <lane dir>
"""
import csv
import json
import os
import sys

L = sys.argv[1]
OLD = os.path.join(L, 'work', 'old')
VL = os.path.join(L, '..', 'v31-counts', 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
NEW = os.path.join(L, 'counts')
problems, lines = [], []
B4, E37 = 'real:blind4', 'e37'

for f, base in (('counts-fp16-int8-launch.json', OLD), ('crosscheck-launch-fp32.json', VL), ('crosscheck-launch-fp32.txt', VL)):
    same = open(os.path.join(base, f), 'rb').read() == open(os.path.join(NEW, f), 'rb').read()
    lines.append(f"{f}: {'BYTE-EQUAL' if same else 'DIFFERS'} to v31-counts'")
    if not same:
        problems.append(f'{f} differs')

o32 = json.load(open(os.path.join(OLD, 'counts-fp32-gemm-states.json')))
n32 = json.load(open(os.path.join(NEW, 'counts-fp32-gemm-states.json')))
top_changed = sorted(k for k in set(o32) | set(n32) if k != 'shapes' and o32.get(k) != n32.get(k))
lines.append(f'fp32 JSON top-level keys changed or added: {top_changed}')
if set(top_changed) - {'what', 'driver', 'fix'}:
    problems.append(f'fp32 JSON top-level: unexpected change {set(top_changed) - {"what", "driver", "fix"}}')
nchg = 0
for s in ('S1', 'S2'):
    if set(o32['shapes'][s]) != set(n32['shapes'][s]):
        problems.append(f'fp32 {s}: kinds differ')
    for kind in o32['shapes'][s]:
        a, b = o32['shapes'][s][kind], n32['shapes'][s][kind]
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if not diff:
            continue
        nchg += 1
        allowed = set()
        if kind in (B4, E37):
            allowed |= {'note', 'tiles_measured'}
        if kind == B4 and s == 'S2':
            allowed |= {k for k in a if isinstance(a[k], (int, float, list)) and k not in ('tiles', 'tiles_sha256')} | {'counts_source'}
        bad = set(diff) - allowed
        lines.append(f'fp32 {s} {kind}: changed {diff}' + (f'  UNEXPECTED {sorted(bad)}' if bad else ''))
        if bad:
            problems.append(f'fp32 {s} {kind}: unexpected change {sorted(bad)}')
lines.append(f'fp32 JSON rows with any change: {nchg} (expected 4: real:blind4 S1/S2 and e37 S1/S2)')
r_old, r_new = o32['shapes']['S2'][B4], n32['shapes']['S2'][B4]
lines.append(f"real:blind4 S2: fin edges lo {r_old['fin_edges_lo']:,.1f} -> {r_new['fin_edges_lo']:,.1f} ({r_old['fin_edges_lo'] / r_new['fin_edges_lo'] - 1:+.2%} "
             f"published over fixed); S {r_old['S_signal_lo_per_op']:,.0f} -> {r_new['S_signal_lo_per_op']:,.0f} ({r_old['S_signal_lo_per_op'] / r_new['S_signal_lo_per_op'] - 1:+.2%}); "
             f"n {r_old['n_points']} -> {r_new['n_points']}; tiles measured {r_new.get('tiles_measured')}")


def rd(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


oc, nc = rd(os.path.join(OLD, 'counts-v31.csv')), rd(os.path.join(NEW, 'counts-v31.csv'))
if len(oc) != len(nc):
    problems.append('counts-v31.csv: row count differs')
cchg = 0
for a, b in zip(oc, nc):
    if (a['key'], a['footing_class']) != (b['key'], b['footing_class']):
        problems.append(f"counts-v31.csv: row order differs at {a['key']}")
        continue
    diff = [k for k in a if a[k] != b.get(k)]
    is_b4s2 = a['key'] == 'fp32.e207.real_blind4' and a['footing_class'].startswith('S2')
    if diff:
        cchg += 1
        if not is_b4s2:
            problems.append(f"counts-v31.csv {a['key']} {a['footing_class']}: unexpected change {diff}")
        lines.append(f"counts-v31.csv {a['key']} {a['footing_class'][:2]}: changed {diff}")
    if b.get('note') and a['key'] not in ('fp32.e207.real_blind4', 'fp32.e207.e37'):
        problems.append(f"counts-v31.csv {a['key']}: a note where none was expected")
nn = sum(1 for b in nc if b.get('note'))
lines.append(f"counts-v31.csv: {len(nc)} rows, {cchg} with an old column changed (expected 1), new column 'note' on {nn} rows (expected 4); "
             f"columns {len(oc[0])} -> {len(nc[0])}")
if cchg != 1 or nn != 4 or list(nc[0].keys()) != list(oc[0].keys()) + ['note']:
    problems.append('counts-v31.csv: the change set is not the expected one')

ot, nt = rd(os.path.join(OLD, 'counts-v31-tiles.csv')), rd(os.path.join(NEW, 'counts-v31-tiles.csv'))
FOOT = {r['fmt']: r['counts_footing'] for r in nc}
bench = {r['bench_sources_manifest_sha256'] for r in nc}
tchg = 0
for a, b in zip(ot, nt):
    if any(a[k] != b.get(k) for k in a):
        tchg += 1
    if b.get('counts_footing') != FOOT[b['fmt']] or {b.get('bench_sources_manifest_sha256')} != bench:
        problems.append(f"counts-v31-tiles.csv {b['tile']}: new columns wrong")
lines.append(f"counts-v31-tiles.csv: {len(nt)} rows (was {len(ot)}), {tchg} with an old column changed (expected 0); new columns "
             f"{[k for k in nt[0] if k not in ot[0]]}; footing = the kind rows' counts_footing for its format on {len(nt)} of {len(nt)}; "
             f"manifest {sorted(bench)[0][:16]}... on every row")
if len(nt) != len(ot) or tchg or list(nt[0].keys()) != list(ot[0].keys()) + ['counts_footing', 'bench_sources_manifest_sha256']:
    problems.append('counts-v31-tiles.csv: the change set is not the expected one')
lines.append(f"VERDICT {'AS EXPECTED' if not problems else 'PROBLEMS: ' + '; '.join(problems)}")
json.dump({'lines': lines, 'problems': problems}, open(os.path.join(L, 'work', 'tables-diff.json'), 'w'), indent=1)
open(os.path.join(L, 'work', 'tables-diff.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(1 if problems else 0)
